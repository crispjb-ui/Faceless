from __future__ import annotations

import os
from dataclasses import dataclass

import httpx

from faceless.config import get_settings
from faceless.niches.base import Niche

AYRSHARE_BASE = "https://api.ayrshare.com/api"

# Map our internal platform ids to Ayrshare platform names.
_TO_AYRSHARE = {
    "tiktok": "tiktok",
    "instagram_reels": "instagram",
    "facebook_reels": "facebook",
}
_FROM_AYRSHARE = {v: k for k, v in _TO_AYRSHARE.items()}


@dataclass
class PostResult:
    platform: str
    platform_video_id: str | None
    url: str | None


def _targets(niche: Niche) -> list[str]:
    # youtube_shorts is handled by the dedicated YouTube upload step.
    return [p for p in niche.publish.distribute_to if p != "youtube_shorts"]


def distribute(
    video_path: str,
    title: str,
    description: str,
    niche: Niche,
    *,
    dry_run: bool = False,
) -> list[PostResult]:
    """Fan the rendered vertical video out to TikTok / Reels via Ayrshare.

    Ayrshare needs the media at a public URL, so we use its upload-URL flow:
    request a signed URL, PUT the file, then create the post with the returned
    access URL. Set DISTRIBUTION_API_KEY to your Ayrshare API key.
    """
    targets = _targets(niche)
    if dry_run:
        return [PostResult(platform=p, platform_video_id=f"DRYRUN_{p}", url=None) for p in targets]
    if not targets:
        return []

    settings = get_settings()
    headers = {"Authorization": f"Bearer {settings.require('distribution_api_key')}"}
    access_url = _upload_media(video_path, headers)

    body = {
        "post": f"{title}\n\n{description}".strip(),
        "platforms": [_TO_AYRSHARE[p] for p in targets],
        "mediaUrls": [access_url],
    }
    resp = httpx.post(f"{AYRSHARE_BASE}/post", json=body, headers=headers, timeout=120.0)
    resp.raise_for_status()
    data = resp.json()

    results: list[PostResult] = []
    for entry in data.get("postIds", []):
        platform = _FROM_AYRSHARE.get(entry.get("platform", ""), entry.get("platform", ""))
        results.append(
            PostResult(
                platform=platform,
                platform_video_id=entry.get("id"),
                url=entry.get("postUrl"),
            )
        )
    return results


def _upload_media(video_path: str, headers: dict[str, str]) -> str:
    """Get a signed upload URL from Ayrshare, PUT the file, return the access URL."""
    filename = os.path.basename(video_path)
    r = httpx.get(
        f"{AYRSHARE_BASE}/media/uploadUrl",
        params={"fileName": filename, "contentType": "video/mp4"},
        headers=headers,
        timeout=60.0,
    )
    r.raise_for_status()
    info = r.json()
    upload_url, access_url = info["uploadUrl"], info["accessUrl"]

    with open(video_path, "rb") as f:
        put = httpx.put(
            upload_url, content=f.read(), headers={"Content-Type": "video/mp4"}, timeout=300.0
        )
        put.raise_for_status()
    return access_url
