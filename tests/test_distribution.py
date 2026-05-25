from __future__ import annotations

from faceless.distribution import distribute
from faceless.distribution.fanout import _FROM_AYRSHARE, _TO_AYRSHARE, _targets
from faceless.niches import get_niche


def test_targets_exclude_youtube():
    niche = get_niche("self_improvement")
    targets = _targets(niche)
    assert "youtube_shorts" not in targets
    assert "tiktok" in targets


def test_platform_mapping_round_trips():
    for internal, ayr in _TO_AYRSHARE.items():
        assert _FROM_AYRSHARE[ayr] == internal


def test_distribute_dry_run():
    niche = get_niche("self_improvement")
    results = distribute("/tmp/x.mp4", "title", "desc", niche, dry_run=True)
    platforms = {r.platform for r in results}
    assert "tiktok" in platforms
    assert all(r.platform_video_id and r.platform_video_id.startswith("DRYRUN_") for r in results)
