from __future__ import annotations

from faceless.niches.base import (
    ComplianceConfig,
    DiscoveryConfig,
    Niche,
    PublishConfig,
    ScriptConfig,
    VisualConfig,
    VoiceConfig,
)

SELF_IMPROVEMENT = Niche(
    id="self_improvement",
    name="Self-Improvement / Motivation",
    discovery=DiscoveryConfig(
        seed_queries=[
            "discipline motivation",
            "stoicism daily",
            "how to stop procrastinating",
            "self improvement habits",
            "mindset shift",
            "focus deep work",
        ],
        keywords=["discipline", "stoic", "habits", "mindset", "motivation", "productivity"],
        category_ids=["22", "27"],  # People&Blogs, Education
        min_velocity=800.0,
        max_age_hours=96,
        max_candidates=50,
    ),
    script=ScriptConfig(
        persona_system_prompt=(
            "You are a scriptwriter for a faceless self-improvement channel. You write "
            "punchy, sincere, non-cringe motivational scripts grounded in stoicism, "
            "discipline, and practical psychology. Every script must be ORIGINAL: you may "
            "reuse the topic/hook/format of a trending video but never its wording, and "
            "never reproduce copyrighted passages or long quotes. Speak in second person, "
            "concrete and specific, no empty platitudes."
        ),
        tone="grounded, intense, sincere",
        short_target_seconds=60,  # >=60s to qualify for TikTok Creativity Program
        longform_target_seconds=480,
        cta="Grab the free Discipline Cheat Sheet — link in bio.",
    ),
    voice=VoiceConfig(
        provider="elevenlabs",
        voice_id=None,  # set ELEVENLABS_VOICE_ID; a deep, calm narrator = brand identity
        style={"stability": 0.5, "similarity_boost": 0.75},
    ),
    visual=VisualConfig(
        style_prompt=(
            "cinematic, moody, high-contrast, film grain, atmospheric lighting, "
            "lone figure / nature / cityscape, no readable text, no recognizable faces"
        ),
        template_id="self_improvement_v1",
        music_library="cinematic_ambient",
        use_ai_motion=False,
    ),
    compliance=ComplianceConfig(
        banned_terms=[
            # copyrighted/branded names that crop up in this niche
            "marvel",
            "disney",
            "joe rogan",
            "andrew tate",
        ],
        extra_rules=[
            "No medical, clinical, or mental-health treatment claims; keep it motivational.",
            "No copyrighted song lyrics or long verbatim quotes from living authors.",
            "Attribute quotes only if verifiably correct; otherwise paraphrase as a general idea.",
            "Must be meaningfully transformative vs. the source video, not a re-narration of it.",
        ],
        max_source_similarity=0.65,
    ),
    publish=PublishConfig(
        made_for_kids=False,
        synthetic_content_disclosure=True,
        default_tags=["motivation", "discipline", "stoicism", "selfimprovement", "mindset"],
        channel_id=None,
        distribute_to=["youtube_shorts", "tiktok", "instagram_reels", "facebook_reels"],
    ),
)
