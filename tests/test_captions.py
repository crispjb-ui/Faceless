from __future__ import annotations

from faceless.assets import build_captions, write_srt
from faceless.scripting.generate import Shot


def _shots():
    return [
        Shot("Discipline is not a feeling it is a decision", "x", 4.0),
        Shot("You make it again and again", "y", 3.0),
    ]


def test_build_captions_chunks_into_short_synced_segments():
    segments = build_captions(_shots(), "voice.mp3", dry_run=True)
    # More segments than shots => sentences are split into short chunks.
    assert len(segments) > 2
    # Chunks are at most a few words.
    assert all(len(s.text.split()) <= 4 for s in segments)
    # Timeline is monotonic and within the total duration (~7s).
    assert segments == sorted(segments, key=lambda s: s.start)
    assert segments[-1].end <= 7.01


def test_write_srt_outputs_numbered_blocks(tmp_path):
    segments = build_captions(_shots(), "voice.mp3", dry_run=True)
    out = tmp_path / "c.srt"
    write_srt(segments, str(out))
    content = out.read_text()
    assert "1\n00:00:00,000 -->" in content
    assert "-->" in content
