from __future__ import annotations

import os

from faceless.scripting.generate import Shot


def generate_captions(
    shots: list[Shot], voice_path: str, out_path: str, *, dry_run: bool = False
) -> str:
    """Produce a timed caption file (SRT/ASS) aligned to the voiceover.

    Approach: derive segment text from the shot narration and align timing with
    Whisper word timestamps over `voice_path`. Burned-in animated captions
    significantly lift short-form retention.
    """
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    if dry_run:
        # Minimal but valid SRT built from shot text + declared durations.
        lines, t = [], 0.0
        for i, shot in enumerate(shots, start=1):
            start, end = t, t + shot.seconds
            lines.append(f"{i}\n{_ts(start)} --> {_ts(end)}\n{shot.narration}\n")
            t = end
        with open(out_path, "w") as f:
            f.write("\n".join(lines))
        return out_path
    # pragma: no cover - requires whisper alignment
    raise NotImplementedError("Wire generate_captions() to Whisper word-timestamp alignment.")


def _ts(seconds: float) -> str:
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds) % 60
    m = (int(seconds) // 60) % 60
    h = int(seconds) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
