from __future__ import annotations


def collect_metrics(*, dry_run: bool = False) -> int:
    """Pull per-video performance and store Metric rows.

    Use the YouTube Analytics API (views, averageViewPercentage, estimatedRevenue)
    for each Upload, plus platform APIs for TikTok/Reels. These metrics feed back
    into discovery scoring so the factory learns which hooks/formats win. Returns
    the number of metric rows written.
    """
    if dry_run:
        return 0
    # pragma: no cover - requires YouTube Analytics API + OAuth
    raise NotImplementedError(
        "Wire collect_metrics() to the YouTube Analytics API and platform metrics."
    )
