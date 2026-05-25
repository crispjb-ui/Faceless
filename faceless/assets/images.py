from __future__ import annotations

import os

from faceless.scripting.generate import Shot


def generate_images(
    shots: list[Shot], out_dir: str, *, dry_run: bool = False
) -> list[str]:
    """Generate one background image per shot. Returns paths in shot order.

    Wire this to your chosen provider (Flux via fal/Replicate, Google Imagen,
    etc.) using IMAGE_API_KEY. Each shot.visual_prompt already carries the
    niche's style prefix. Consider seed-locking for visual consistency.
    """
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for i, _shot in enumerate(shots):
        path = os.path.join(out_dir, f"shot_{i:03d}.png")
        if dry_run:
            open(path, "wb").close()  # placeholder
            paths.append(path)
        else:  # pragma: no cover - requires a configured image provider
            raise NotImplementedError(
                "Wire generate_images() to your image provider (see IMAGE_API_KEY)."
            )
    return paths
