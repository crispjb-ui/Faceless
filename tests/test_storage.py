from __future__ import annotations

from faceless import storage
from faceless.distribution import distribute
from faceless.niches import get_niche


def test_storage_not_configured_by_default():
    # Tests run with no STORAGE_* env, so storage is inactive.
    assert storage.is_configured() is False


def test_storage_dry_run_builds_public_url():
    url = storage.upload_file("/tmp/whatever.mp4", "self_improvement/job_1/video.mp4", dry_run=True)
    assert url.endswith("/self_improvement/job_1/video.mp4")


def test_distribute_uses_supplied_media_url_in_dry_run():
    niche = get_niche("self_improvement")
    results = distribute(
        "/tmp/x.mp4", "t", "d", niche, media_url="https://media.example.com/x.mp4", dry_run=True
    )
    assert {r.platform for r in results} >= {"tiktok"}
