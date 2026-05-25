from __future__ import annotations

import json
import os
import shutil
import subprocess

from faceless.assets.captions import CaptionSegment
from faceless.scripting.generate import Shot

FPS = 30
_HERE = os.path.dirname(__file__)
REMOTION_DIR = os.path.join(_HERE, "remotion")


def render_with_remotion(
    image_paths: list[str],
    shots: list[Shot],
    voice_path: str,
    music_path: str | None,
    caption_segments: list[CaptionSegment],
    out_path: str,
    *,
    dry_run: bool = False,
) -> str:
    """Render the branded vertical video with the Remotion template.

    Requires Node + `npm install` inside faceless/render/remotion/. Assets are
    staged into the project's public/ dir and passed as props; the composition
    length is computed from shot durations via calculateMetadata.
    """
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    if dry_run:
        open(out_path, "wb").close()
        return out_path

    if shutil.which("npx") is None:
        raise RuntimeError(
            "npx/node not found. Install Node and run 'npm install' in "
            "faceless/render/remotion."
        )
    if not os.path.isdir(os.path.join(REMOTION_DIR, "node_modules")):
        raise RuntimeError("Run 'npm install' in faceless/render/remotion first.")

    job_id = os.path.basename(os.path.dirname(os.path.abspath(out_path))) or "job"
    public = os.path.join(REMOTION_DIR, "public", "jobs", job_id)
    os.makedirs(public, exist_ok=True)

    shot_props = []
    for i, (img, shot) in enumerate(zip(image_paths, shots)):
        shutil.copy(img, os.path.join(public, f"shot_{i:03d}.png"))
        shot_props.append(
            {
                "img": f"jobs/{job_id}/shot_{i:03d}.png",
                "durationInFrames": max(1, round(shot.seconds * FPS)),
            }
        )

    captions = [
        {
            "text": seg.text,
            "from": max(0, round(seg.start * FPS)),
            "durationInFrames": max(1, round((seg.end - seg.start) * FPS)),
        }
        for seg in caption_segments
    ]

    shutil.copy(voice_path, os.path.join(public, "voice.mp3"))
    music_rel = None
    if music_path and os.path.exists(music_path) and os.path.getsize(music_path) > 0:
        shutil.copy(music_path, os.path.join(public, "music.mp3"))
        music_rel = f"jobs/{job_id}/music.mp3"

    props = {
        "fps": FPS,
        "shots": shot_props,
        "captions": captions,
        "voice": f"jobs/{job_id}/voice.mp3",
        "music": music_rel,
    }
    props_file = os.path.join(public, "props.json")
    with open(props_file, "w") as f:
        json.dump(props, f)

    subprocess.run(
        [
            "npx", "remotion", "render", "src/index.ts", "MotivationVideo",
            os.path.abspath(out_path), f"--props={os.path.abspath(props_file)}",
        ],
        cwd=REMOTION_DIR,
        check=True,
    )
    return out_path
