from __future__ import annotations

import os

from faceless.scripting.generate import Shot


def generate_captions(
    shots: list[Shot], voice_path: str, out_path: str, *, dry_run: bool = False
) -> str:
    """Write a timed SRT caption file aligned to the shot list.

    Because we author the shot durations, segment timing is derived directly from
    them — no transcription needed. (For word-level karaoke captions, refine these
    timings with faster-whisper over `voice_path`.) Burned-in animated captions
    significantly lift short-form retention.
    """
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    blocks, t = [], 0.0
    for i, shot in enumerate(shots, start=1):
        start, end = t, t + shot.seconds
        blocks.append(f"{i}\n{_ts(start)} --> {_ts(end)}\n{shot.narration}\n")
        t = end
    with open(out_path, "w") as f:
        f.write("\n".join(blocks))
    return out_path


def _ts(seconds: float) -> str:
    ms = int(round((seconds - int(seconds)) * 1000))
    s = int(seconds) % 60
    m = (int(seconds) // 60) % 60
    h = int(seconds) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
