from __future__ import annotations

import os

from faceless.config import get_settings
from faceless.niches.base import Niche


def synthesize_voiceover(
    text: str, niche: Niche, out_path: str, *, dry_run: bool = False
) -> str:
    """Render narration to an audio file. Returns the path written.

    Provider: ElevenLabs (set ELEVENLABS_API_KEY and a niche voice_id or
    ELEVENLABS_VOICE_ID). The signature voice IS the channel's brand identity.
    """
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    if dry_run:
        with open(out_path, "wb") as f:
            f.write(b"")  # placeholder so downstream path checks succeed
        return out_path

    settings = get_settings()
    voice_id = niche.voice.voice_id or settings.elevenlabs_voice_id
    if not voice_id:
        raise RuntimeError(
            "No voice id. Set ELEVENLABS_VOICE_ID or niche.voice.voice_id."
        )

    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=settings.require("elevenlabs_api_key"))
    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        text=text,
        voice_settings=niche.voice.style or None,
    )
    with open(out_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    return out_path
