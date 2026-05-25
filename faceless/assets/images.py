from __future__ import annotations

import os

import httpx

from faceless.config import get_settings
from faceless.scripting.generate import Shot

# Flux 1.1 Pro on fal.ai — best cinematic quality-per-dollar with a clean API.
FAL_MODEL = "fal-ai/flux-pro/v1.1"


def generate_images(
    shots: list[Shot], out_dir: str, *, dry_run: bool = False
) -> list[str]:
    """Generate one vertical (9:16) background image per shot via Flux on fal.ai.

    Each shot.visual_prompt already carries the niche's cinematic style prefix.
    Set IMAGE_API_KEY to your fal key. Returns image paths in shot order.
    """
    os.makedirs(out_dir, exist_ok=True)

    if dry_run:
        paths = []
        for i, _shot in enumerate(shots):
            path = os.path.join(out_dir, f"shot_{i:03d}.png")
            open(path, "wb").close()  # placeholder
            paths.append(path)
        return paths

    settings = get_settings()
    # fal_client reads the FAL_KEY env var.
    os.environ.setdefault("FAL_KEY", settings.require("image_api_key"))
    import fal_client

    paths = []
    for i, shot in enumerate(shots):
        result = fal_client.subscribe(
            FAL_MODEL,
            arguments={
                "prompt": shot.visual_prompt,
                "image_size": "portrait_16_9",  # vertical 9:16 for Shorts/TikTok/Reels
                "num_images": 1,
                "output_format": "png",
                "safety_tolerance": "2",
            },
        )
        url = result["images"][0]["url"]
        path = os.path.join(out_dir, f"shot_{i:03d}.png")
        _download(url, path)
        paths.append(path)
    return paths


def _download(url: str, path: str) -> None:
    with httpx.stream("GET", url, timeout=120.0, follow_redirects=True) as resp:
        resp.raise_for_status()
        with open(path, "wb") as f:
            for chunk in resp.iter_bytes():
                f.write(chunk)
