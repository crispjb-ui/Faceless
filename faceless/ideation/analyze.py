from __future__ import annotations

from dataclasses import dataclass

from faceless.discovery.youtube import DiscoveredVideo
from faceless.llm import complete_json
from faceless.niches.base import Niche

_SYSTEM = (
    "You analyze a trending video and propose ONE original, differentiated video idea "
    "for our channel. Extract the underlying concept (hook, theme, structure) and then "
    "reframe it into a NEW angle that does not copy the source's wording, characters, or "
    "footage. Respond as JSON: {{\"angle\": str, \"rationale\": str, \"predicted_score\": "
    "number 0-100}}.\n\nChannel persona:\n{persona}"
)


@dataclass
class IdeaResult:
    angle: str
    rationale: str
    predicted_score: float


def generate_idea(video: DiscoveredVideo, niche: Niche, *, dry_run: bool = False) -> IdeaResult:
    if dry_run:
        return IdeaResult(
            angle=f"Original take inspired by the theme of: {video.title}",
            rationale="Reframes the trending hook into a fresh, transformative angle.",
            predicted_score=72.0,
        )

    system = _SYSTEM.format(persona=niche.script.persona_system_prompt)
    user = (
        f"Trending video title: {video.title}\n"
        f"Description: {video.description[:1500]}\n"
        f"Channel: {video.channel_title}\n"
        f"Velocity (views/hr): {video.velocity:.0f}\n\n"
        "Propose one original, differentiated idea for our channel."
    )
    data = complete_json(system, user, max_tokens=800)
    return IdeaResult(
        angle=str(data["angle"]),
        rationale=str(data.get("rationale", "")),
        predicted_score=float(data.get("predicted_score", 0.0)),
    )
