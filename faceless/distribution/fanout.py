from __future__ import annotations

from dataclasses import dataclass

from faceless.niches.base import Niche


@dataclass
class PostResult:
    platform: str
    platform_video_id: str | None
    url: str | None


def distribute(
    video_path: str,
    title: str,
    description: str,
    niche: Niche,
    *,
    dry_run: bool = False,
) -> list[PostResult]:
    """Fan the same rendered vertical video out to TikTok / Reels / etc.

    The same render goes everywhere because we produce originals (no watermark).
    Wire to a multi-platform posting API/SaaS (upload-post / Blotato / Postiz /
    Metricool / Buffer) using DISTRIBUTION_API_KEY. TikTok's own Content Posting
    API requires app approval. Platforms come from niche.publish.distribute_to
    (excluding youtube_shorts, which is handled by the YouTube upload step).
    """
    targets = [p for p in niche.publish.distribute_to if p != "youtube_shorts"]
    if dry_run:
        return [PostResult(platform=p, platform_video_id=f"DRYRUN_{p}", url=None) for p in targets]
    # pragma: no cover - requires a configured posting provider
    raise NotImplementedError(
        "Wire distribute() to a multi-platform posting provider (see DISTRIBUTION_API_KEY)."
    )
