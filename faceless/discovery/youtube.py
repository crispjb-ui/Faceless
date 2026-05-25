from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from faceless.config import get_settings
from faceless.niches.base import Niche


@dataclass
class DiscoveredVideo:
    video_id: str
    title: str
    description: str
    channel_title: str
    published_at: datetime | None
    view_count: int
    velocity: float  # views per hour since publish
    score: float


def _velocity(view_count: int, published_at: datetime | None) -> float:
    if not published_at:
        return 0.0
    hours = max((datetime.now(timezone.utc) - published_at).total_seconds() / 3600.0, 1.0)
    return view_count / hours


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def discover_candidates(niche: Niche, *, dry_run: bool = False) -> list[DiscoveredVideo]:
    """Find trending source videos for a niche via the YouTube Data API.

    Uses search.list to find recent videos per seed query, then videos.list to
    fetch statistics, computes views/hour velocity, and ranks. `dry_run=True`
    returns deterministic fixtures so the pipeline can be exercised offline.
    """
    if dry_run:
        return _fixtures(niche)

    from googleapiclient.discovery import build

    settings = get_settings()
    youtube = build("youtube", "v3", developerKey=settings.require("youtube_api_key"))
    cfg = niche.discovery

    found: dict[str, dict] = {}
    for query in cfg.seed_queries:
        resp = (
            youtube.search()
            .list(
                q=query,
                part="snippet",
                type="video",
                order="viewCount",
                publishedAfter=_published_after(cfg.max_age_hours),
                maxResults=10,
            )
            .execute()
        )
        for item in resp.get("items", []):
            vid = item["id"]["videoId"]
            found[vid] = item["snippet"]

    candidates: list[DiscoveredVideo] = []
    for batch in _chunk(list(found), 50):
        stats = (
            youtube.videos()
            .list(part="statistics,snippet", id=",".join(batch))
            .execute()
        )
        for item in stats.get("items", []):
            snip = item["snippet"]
            views = int(item.get("statistics", {}).get("viewCount", 0))
            published = _parse_dt(snip.get("publishedAt"))
            velocity = _velocity(views, published)
            if velocity < cfg.min_velocity:
                continue
            candidates.append(
                DiscoveredVideo(
                    video_id=item["id"],
                    title=snip.get("title", ""),
                    description=snip.get("description", ""),
                    channel_title=snip.get("channelTitle", ""),
                    published_at=published,
                    view_count=views,
                    velocity=velocity,
                    score=velocity,  # ranking is refined later by analytics feedback
                )
            )

    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates[: cfg.max_candidates]


def _published_after(max_age_hours: int) -> str:
    from datetime import timedelta

    dt = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _chunk(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _fixtures(niche: Niche) -> list[DiscoveredVideo]:
    now = datetime.now(timezone.utc)
    samples = [
        ("dQw4w9_demo1", "The 5am Discipline That Changed My Life", 1_200_000),
        ("dQw4w9_demo2", "Stop Procrastinating in 60 Seconds (Stoic Method)", 880_000),
        ("dQw4w9_demo3", "Why Discipline Beats Motivation Every Time", 640_000),
    ]
    out = []
    for vid, title, views in samples:
        out.append(
            DiscoveredVideo(
                video_id=vid,
                title=title,
                description="(fixture description for offline dry-run)",
                channel_title="DemoChannel",
                published_at=now,
                view_count=views,
                velocity=float(views),
                score=float(views),
            )
        )
    return out
