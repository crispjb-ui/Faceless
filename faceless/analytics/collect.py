from __future__ import annotations

from faceless.config import get_settings
from faceless.db import Metric, Upload, get_session, init_db


def collect_metrics(*, dry_run: bool = False) -> int:
    """Capture current performance for published uploads. Returns rows written.

    YouTube view/like counts come from the Data API (videos.list statistics) —
    no extra OAuth, reuses YOUTUBE_API_KEY. These feed back into discovery
    scoring. Revenue / averageViewPercentage require the YouTube Analytics API
    with an OAuth analytics scope (extend here); TikTok/IG metrics can be pulled
    via the Ayrshare analytics endpoint using the stored platform post ids.
    """
    if dry_run:
        return 0

    init_db()
    with get_session() as s:
        uploads = (
            s.query(Upload)
            .filter(Upload.platform == "youtube_shorts", Upload.platform_video_id.isnot(None))
            .all()
        )
        by_video = {u.platform_video_id: u.id for u in uploads}

    if not by_video:
        return 0

    stats = _youtube_stats(list(by_video))
    written = 0
    with get_session() as s:
        for video_id, upload_id in by_video.items():
            stat = stats.get(video_id)
            if not stat:
                continue
            s.add(
                Metric(
                    upload_id=upload_id,
                    views=int(stat.get("viewCount", 0)),
                    likes=int(stat.get("likeCount", 0)),
                )
            )
            written += 1
    return written


def _youtube_stats(video_ids: list[str]) -> dict[str, dict]:
    from googleapiclient.discovery import build

    youtube = build("youtube", "v3", developerKey=get_settings().require("youtube_api_key"))
    out: dict[str, dict] = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        resp = youtube.videos().list(part="statistics", id=",".join(batch)).execute()
        for item in resp.get("items", []):
            out[item["id"]] = item.get("statistics", {})
    return out
