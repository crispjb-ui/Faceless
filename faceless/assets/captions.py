from __future__ import annotations

import os
from dataclasses import dataclass

from faceless.scripting.generate import Shot

# Short caption chunks (a few words at a time) are the high-retention short-form
# style — far better than dumping a whole sentence on screen.
_MAX_WORDS = 4
_MAX_SECONDS = 1.4


@dataclass
class CaptionSegment:
    start: float  # seconds
    end: float
    text: str


def build_captions(
    shots: list[Shot], voice_path: str, *, dry_run: bool = False
) -> list[CaptionSegment]:
    """Build word-synced caption chunks.

    Prefers faster-whisper word timestamps over the real voiceover (true sync);
    falls back to evenly distributing each shot's words across its duration when
    Whisper is unavailable or in dry-run.
    """
    if not dry_run:
        whisper_segments = _whisper_segments(voice_path)
        if whisper_segments:
            return whisper_segments
    return _shot_segments(shots)


def _shot_segments(shots: list[Shot]) -> list[CaptionSegment]:
    segments: list[CaptionSegment] = []
    t = 0.0
    for shot in shots:
        words = shot.narration.split()
        if not words:
            t += shot.seconds
            continue
        chunks = [words[i : i + _MAX_WORDS] for i in range(0, len(words), _MAX_WORDS)]
        per = shot.seconds / len(chunks)
        for j, chunk in enumerate(chunks):
            start = t + j * per
            segments.append(CaptionSegment(start, start + per, " ".join(chunk)))
        t += shot.seconds
    return segments


def _whisper_segments(voice_path: str) -> list[CaptionSegment]:
    try:
        from faster_whisper import WhisperModel
    except Exception:
        return []
    try:
        model = WhisperModel("base", device="cpu", compute_type="int8")
        whisper_out, _info = model.transcribe(voice_path, word_timestamps=True)
        words = [w for seg in whisper_out for w in (seg.words or [])]
        if not words:
            return []

        segments: list[CaptionSegment] = []
        current: list[str] = []
        start: float | None = None
        for w in words:
            if start is None:
                start = w.start
            current.append(w.word.strip())
            if len(current) >= _MAX_WORDS or (w.end - start) >= _MAX_SECONDS:
                segments.append(CaptionSegment(start, w.end, " ".join(current)))
                current, start = [], None
        if current and start is not None:
            segments.append(CaptionSegment(start, words[-1].end, " ".join(current)))
        return segments
    except Exception:
        return []


def write_srt(segments: list[CaptionSegment], out_path: str) -> str:
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    blocks = [
        f"{i}\n{_ts(s.start)} --> {_ts(s.end)}\n{s.text}\n"
        for i, s in enumerate(segments, start=1)
    ]
    with open(out_path, "w") as f:
        f.write("\n".join(blocks))
    return out_path


def generate_captions(
    shots: list[Shot], voice_path: str, out_path: str, *, dry_run: bool = False
) -> str:
    """Convenience: build caption segments and write them as SRT. Returns the path."""
    write_srt(build_captions(shots, voice_path, dry_run=dry_run), out_path)
    return out_path


def _ts(seconds: float) -> str:
    ms = int(round((seconds - int(seconds)) * 1000))
    s = int(seconds) % 60
    m = (int(seconds) // 60) % 60
    h = int(seconds) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
