from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from faceless.config import get_settings


@lru_cache
def _client():
    from anthropic import Anthropic

    settings = get_settings()
    return Anthropic(api_key=settings.require("anthropic_api_key"))


def complete_json(
    system: str,
    user: str,
    *,
    heavy: bool = False,
    max_tokens: int = 2000,
) -> Any:
    """Call Claude and parse the response as JSON.

    The system prompt is sent with cache_control so the (large, static) niche
    persona is cached across the many calls in a daily batch.
    """
    settings = get_settings()
    model = settings.anthropic_model_heavy if heavy else settings.anthropic_model
    msg = _client().messages.create(
        model=model,
        max_tokens=max_tokens,
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(block.text for block in msg.content if block.type == "text").strip()
    return json.loads(_strip_code_fence(text))


def _strip_code_fence(text: str) -> str:
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()
