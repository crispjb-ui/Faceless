from __future__ import annotations

import json
import os
from dataclasses import dataclass

from faceless.assets import generate_captions, generate_images, select_music, synthesize_voiceover
from faceless.compliance import check_compliance
from faceless.config import get_settings
from faceless.db import Candidate, Idea, JobStatus, Script, VideoJob, get_session, init_db
from faceless.discovery import discover_candidates
from faceless.ideation import generate_idea
from faceless.ideation.analyze import IdeaResult
from faceless.niches import get_niche
from faceless.publish import upload_to_youtube
from faceless.render import assemble_video, make_thumbnail
from faceless.scripting import generate_script
from faceless.scripting.generate import Shot


@dataclass
class BatchSummary:
    discovered: int
    produced: int
    blocked: int
    awaiting_review: int


def produce_batch(
    niche_id: str, *, limit: int = 5, fmt: str = "short", dry_run: bool = False
) -> BatchSummary:
    """Run discovery → ideation → script → compliance → assets → render.

    Leaves each produced job in `awaiting_review` for the human approval gate.
    Publishing happens separately in publish_approved().
    """
    init_db()
    niche = get_niche(niche_id)
    settings = get_settings()
    videos = discover_candidates(niche, dry_run=dry_run)

    produced = blocked = awaiting = 0
    for video in videos[:limit]:
        with get_session() as s:
            cand = Candidate(
                niche=niche.id,
                video_id=video.video_id,
                title=video.title,
                description=video.description,
                channel_title=video.channel_title,
                published_at=video.published_at,
                view_count=video.view_count,
                velocity=video.velocity,
                score=video.score,
            )
            s.add(cand)
            s.flush()
            candidate_id = cand.id

        idea = generate_idea(video, niche, dry_run=dry_run)
        script = generate_script(idea, niche, fmt=fmt, dry_run=dry_run)
        verdict = check_compliance(script, niche, dry_run=dry_run)

        with get_session() as s:
            idea_row = Idea(
                niche=niche.id,
                candidate_id=candidate_id,
                angle=idea.angle,
                rationale=idea.rationale,
                predicted_score=idea.predicted_score,
            )
            s.add(idea_row)
            s.flush()
            job = VideoJob(niche=niche.id, idea_id=idea_row.id, format=fmt)
            job.script = Script(
                title=script.title,
                body=script.body,
                shot_list_json=json.dumps([s_.__dict__ for s_ in script.shots]),
                description=script.description,
                tags_json=json.dumps(script.tags),
            )
            job.compliance_notes = "; ".join(verdict.issues)
            if verdict.blocked:
                job.status = JobStatus.compliance_blocked
                s.add(job)
                blocked += 1
                continue
            job.status = (
                JobStatus.compliance_flagged
                if verdict.decision == "flag"
                else JobStatus.scripted
            )
            s.add(job)
            s.flush()
            job_id = job.id

        _build_assets_and_render(job_id, script, niche, settings, dry_run=dry_run)
        produced += 1
        awaiting += 1

    return BatchSummary(
        discovered=len(videos), produced=produced, blocked=blocked, awaiting_review=awaiting
    )


def _build_assets_and_render(
    job_id: int, script, niche, settings, *, dry_run: bool
) -> None:
    job_dir = os.path.join(settings.output_dir, niche.id, f"job_{job_id}")
    voice_path = os.path.join(job_dir, "voice.mp3")
    music_path = os.path.join(job_dir, "music.mp3")
    captions_path = os.path.join(job_dir, "captions.srt")
    video_path = os.path.join(job_dir, "video.mp4")
    thumb_path = os.path.join(job_dir, "thumb.jpg")

    synthesize_voiceover(script.body, niche, voice_path, dry_run=dry_run)
    image_paths = generate_images(script.shots, os.path.join(job_dir, "img"), dry_run=dry_run)
    select_music(niche, music_path, dry_run=dry_run)
    generate_captions(script.shots, voice_path, captions_path, dry_run=dry_run)
    assemble_video(
        image_paths, script.shots, voice_path, music_path, captions_path, video_path,
        dry_run=dry_run,
    )
    if image_paths:
        make_thumbnail(image_paths[0], thumb_path, dry_run=dry_run)

    with get_session() as s:
        job = s.get(VideoJob, job_id)
        job.voice_path = voice_path
        job.video_path = video_path
        job.thumbnail_path = thumb_path
        job.status = JobStatus.awaiting_review


def publish_approved(niche_id: str, *, limit: int = 10, dry_run: bool = False) -> int:
    """Upload jobs a human marked `approved` to YouTube (+ distribution)."""
    from faceless.db import Upload
    from faceless.distribution import distribute

    init_db()
    niche = get_niche(niche_id)
    published = 0
    with get_session() as s:
        jobs = (
            s.query(VideoJob)
            .filter(VideoJob.niche == niche_id, VideoJob.status == JobStatus.approved)
            .limit(limit)
            .all()
        )
        job_ids = [j.id for j in jobs]

    for job_id in job_ids:
        with get_session() as s:
            job = s.get(VideoJob, job_id)
            script = job.script
            title, description = script.title, script.description
            tags = json.loads(script.tags_json)
            video_path = job.video_path

        result = upload_to_youtube(video_path, title, description, tags, niche, dry_run=dry_run)
        posts = distribute(video_path, title, description, niche, dry_run=dry_run)

        with get_session() as s:
            job = s.get(VideoJob, job_id)
            job.status = JobStatus.published
            s.add(Upload(job_id=job_id, platform="youtube_shorts",
                         platform_video_id=result.video_id, url=result.url))
            for p in posts:
                s.add(Upload(job_id=job_id, platform=p.platform,
                             platform_video_id=p.platform_video_id, url=p.url))
        published += 1
    return published


# Keep linters happy about intentionally-imported helper types.
_ = (IdeaResult, Shot)
