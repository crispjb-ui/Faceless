from __future__ import annotations

import os
import random
import shutil

from faceless.config import get_settings
from faceless.niches.base import Niche

_AUDIO_EXTS = (".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac")


def select_music(
    niche: Niche, out_path: str, *, dry_run: bool = False, seed: int | None = None
) -> str:
    """Pick a background track from your pre-licensed local library.

    Populate MUSIC_LIBRARY_DIR/<niche.visual.music_library>/ with commercially
    cleared tracks (e.g. Epidemic Sound downloads — your subscription license
    covers your own channels, and a local pool keeps the same render safe on
    YouTube, TikTok, and Reels). Epidemic's track API is enterprise-gated, so a
    local library is the reliable automatable approach.
    """
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    if dry_run:
        open(out_path, "wb").close()  # placeholder
        return out_path

    settings = get_settings()
    library = os.path.join(settings.music_library_dir, niche.visual.music_library)
    tracks = (
        [
            os.path.join(library, f)
            for f in sorted(os.listdir(library))
            if f.lower().endswith(_AUDIO_EXTS)
        ]
        if os.path.isdir(library)
        else []
    )
    if not tracks:
        raise RuntimeError(
            f"No licensed tracks in '{library}'. Populate it with commercially "
            f"cleared music (e.g. Epidemic Sound downloads for '"
            f"{niche.visual.music_library}')."
        )
    chosen = random.Random(seed).choice(tracks)
    shutil.copy(chosen, out_path)
    return out_path
