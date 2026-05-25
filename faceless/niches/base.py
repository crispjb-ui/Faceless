from __future__ import annotations

from pydantic import BaseModel, Field


class DiscoveryConfig(BaseModel):
    """What "trending in this niche" means."""

    seed_queries: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    # YouTube videoCategoryId values to bias toward (24=Entertainment, 27=Education...).
    category_ids: list[str] = Field(default_factory=list)
    # Minimum views-per-hour velocity for a candidate to be considered.
    min_velocity: float = 500.0
    # Max age (hours) of a video to still count as "trending".
    max_age_hours: int = 96
    max_candidates: int = 50


class ScriptConfig(BaseModel):
    """How scripts are written for this niche."""

    persona_system_prompt: str
    tone: str
    # Target durations in seconds for each format.
    short_target_seconds: int = 45
    longform_target_seconds: int = 420
    # Call-to-action funnel text appended/spoken at the end.
    cta: str = ""


class VoiceConfig(BaseModel):
    provider: str = "elevenlabs"
    voice_id: str | None = None
    # Provider-specific style/stability knobs.
    style: dict = Field(default_factory=dict)


class VisualConfig(BaseModel):
    # Style prompt prefix applied to every image/motion generation.
    style_prompt: str
    # Remotion template id that gives the channel its consistent look.
    template_id: str = "default"
    # Library / playlist id for royalty-free music selection.
    music_library: str = "default"
    # Use AI motion (Runway/Luma/...) vs. cheaper Ken Burns over stills.
    use_ai_motion: bool = False


class ComplianceConfig(BaseModel):
    # Niche-specific terms that hard-block a script (e.g. copyrighted IP).
    banned_terms: list[str] = Field(default_factory=list)
    # Extra free-text rules handed to the LLM compliance check.
    extra_rules: list[str] = Field(default_factory=list)
    # Reject if cosine/semantic similarity to source exceeds this (0-1).
    max_source_similarity: float = 0.7


class PublishConfig(BaseModel):
    made_for_kids: bool = False
    # YouTube "altered or synthetic content" disclosure.
    synthetic_content_disclosure: bool = True
    default_tags: list[str] = Field(default_factory=list)
    # Target channel id (per niche → its own channel).
    channel_id: str | None = None
    # Platforms to fan the rendered vertical video out to.
    distribute_to: list[str] = Field(
        default_factory=lambda: ["youtube_shorts", "tiktok", "instagram_reels"]
    )


class Niche(BaseModel):
    """A complete niche definition. The whole pipeline reads this; adding a niche
    requires no pipeline code, only a new `Niche(...)` + a Remotion template."""

    id: str
    name: str
    discovery: DiscoveryConfig
    script: ScriptConfig
    voice: VoiceConfig
    visual: VisualConfig
    compliance: ComplianceConfig
    publish: PublishConfig
