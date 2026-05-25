from __future__ import annotations

import os

import pytest

from faceless.assets import select_music
from faceless.config import get_settings
from faceless.niches import get_niche


def test_select_music_from_local_library(tmp_path):
    niche = get_niche("self_improvement")
    library = os.path.join(get_settings().music_library_dir, niche.visual.music_library)
    os.makedirs(library, exist_ok=True)
    track = os.path.join(library, "calm_01.mp3")
    with open(track, "wb") as f:
        f.write(b"FAKEAUDIO")

    out = tmp_path / "music.mp3"
    result = select_music(niche, str(out), seed=0)
    assert result == str(out)
    assert out.read_bytes() == b"FAKEAUDIO"


def test_select_music_errors_when_library_empty(tmp_path):
    niche = get_niche("self_improvement")
    # Point at an empty/missing library so selection must fail loudly.
    empty = niche.model_copy(deep=True)
    empty.visual.music_library = "does_not_exist_pool"
    with pytest.raises(RuntimeError, match="No licensed tracks"):
        select_music(empty, str(tmp_path / "m.mp3"))
