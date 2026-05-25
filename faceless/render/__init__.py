from __future__ import annotations

from faceless.assets.captions import CaptionSegment
from faceless.config import get_settings
from faceless.render.assemble import assemble_video, make_thumbnail
from faceless.render.remotion_render import render_with_remotion
from faceless.scripting.generate import Shot

__all__ = ["render_video", "assemble_video", "make_thumbnail", "render_with_remotion"]


def render_video(
    image_paths: list[str],
    shots: list[Shot],
    voice_path: str,
    music_path: str | None,
    captions_path: str | None,
    out_path: str,
    *,
    caption_segments: list[CaptionSegment] | None = None,
    dry_run: bool = False,
) -> str:
    """Render via the configured backend (RENDER_BACKEND: ffmpeg | remotion).

    ffmpeg burns the SRT at `captions_path`; remotion renders word-synced caption
    chunks from `caption_segments`.
    """
    backend = get_settings().render_backend.lower()
    if backend == "remotion":
        return render_with_remotion(
            image_paths, shots, voice_path, music_path, caption_segments or [], out_path,
            dry_run=dry_run,
        )
    return assemble_video(
        image_paths, shots, voice_path, music_path, captions_path, out_path,
        dry_run=dry_run,
    )
