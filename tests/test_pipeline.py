from __future__ import annotations

import os

from faceless.db import JobStatus, VideoJob, get_session
from faceless.niches import get_niche, list_niches
from faceless.orchestrator import produce_batch


def test_self_improvement_registered():
    assert "self_improvement" in list_niches()
    niche = get_niche("self_improvement")
    assert niche.publish.made_for_kids is False
    assert "tiktok" in niche.publish.distribute_to


def test_dry_run_batch_produces_reviewable_jobs():
    summary = produce_batch("self_improvement", limit=2, dry_run=True)
    assert summary.discovered >= 2
    assert summary.produced == 2

    with get_session() as s:
        jobs = s.query(VideoJob).all()
        assert len(jobs) == 2
        for job in jobs:
            assert job.status == JobStatus.awaiting_review
            assert job.video_path and os.path.exists(job.video_path)
            assert job.script is not None
