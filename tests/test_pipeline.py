from __future__ import annotations

import os

from faceless.db import JobStatus, VideoJob, get_session
from faceless.niches import get_niche, list_niches
from faceless.orchestrator import daily_flow, produce_batch


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


def test_daily_flow_dry_run_isolated_stages():
    result = daily_flow("self_improvement", produce_limit=2, dry_run=True)
    assert result.errors == []
    assert result.produced == 2
    assert result.awaiting_review == 2
    # Nothing approved yet on a fresh run, so nothing is published.
    assert result.published == 0
