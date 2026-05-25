from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

from faceless.scripting.generate import Shot

# Vertical 9:16 for Shorts / TikTok / Reels.
WIDTH, HEIGHT = 1080, 1920


def assemble_video(
    image_paths: list[str],
    shots: list[Shot],
    voice_path: str,
    music_path: str | None,
    captions_path: str | None,
    out_path: str,
    *,
    dry_run: bool = False,
) -> str:
    """Compose stills + voiceover (+ music + captions) into a vertical MP4.

    This FFmpeg path produces a slideshow with per-shot durations and burned-in
    captions; it is the cheap default. For a branded, animated channel look,
    swap in the Remotion project under faceless/render/remotion/ (recommended).
    """
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    if dry_run:
        open(out_path, "wb").close()  # placeholder
        return out_path

    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found on PATH; install ffmpeg to render.")
    if len(image_paths) != len(shots):
        raise ValueError("image_paths and shots length mismatch")

    with tempfile.TemporaryDirectory() as tmp:
        # 1) Build a concat list of images, each held for its shot duration.
        concat_file = os.path.join(tmp, "concat.txt")
        with open(concat_file, "w") as f:
            for img, shot in zip(image_paths, shots):
                f.write(f"file '{os.path.abspath(img)}'\n")
                f.write(f"duration {shot.seconds}\n")
            f.write(f"file '{os.path.abspath(image_paths[-1])}'\n")  # last frame hold

        scale = (
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={WIDTH}:{HEIGHT},setsar=1"
        )
        vf = scale + (f",subtitles={_esc(captions_path)}" if captions_path else "")

        # 2) Mix narration with optional ducked background music.
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", concat_file,
            "-i", voice_path,
        ]
        if music_path:
            cmd += ["-i", music_path]
            cmd += [
                "-filter_complex",
                "[2:a]volume=0.18[m];[1:a][m]amix=inputs=2:duration=first[a]",
                "-map", "0:v", "-map", "[a]",
            ]
        else:
            cmd += ["-map", "0:v", "-map", "1:a"]
        cmd += [
            "-vf", vf,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
            "-c:a", "aac", "-b:a", "192k", "-shortest", out_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
    return out_path


def make_thumbnail(image_path: str, out_path: str, *, dry_run: bool = False) -> str:
    """Generate a thumbnail (hook image + template overlay)."""
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    if dry_run:
        open(out_path, "wb").close()
        return out_path
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found on PATH.")
    subprocess.run(
        ["ffmpeg", "-y", "-i", image_path, "-vf", "scale=1280:720", out_path],
        check=True,
        capture_output=True,
    )
    return out_path


def _esc(path: str) -> str:
    # Escape for ffmpeg subtitles filter.
    return path.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
