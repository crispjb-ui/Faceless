from __future__ import annotations

import os

from faceless.niches.base import Niche


def select_music(niche: Niche, out_path: str, *, dry_run: bool = False) -> str:
    """Pick a royalty-free / licensed background track for the video.

    IMPORTANT: only use commercially-cleared music (Epidemic Sound, YouTube Audio
    Library, or Suno with commercial terms) so the same render is safe on YouTube,
    TikTok, and Reels. niche.visual.music_library selects the pool.
    """
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    if dry_run:
        open(out_path, "wb").close()  # placeholder
        return out_path
    # pragma: no cover - requires a configured music source
    raise NotImplementedError(
        "Wire select_music() to a licensed/royalty-free source (see MUSIC_API_KEY)."
    )
