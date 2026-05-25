from __future__ import annotations

from dataclasses import dataclass, field

from faceless.ideation.analyze import IdeaResult
from faceless.llm import complete_json
from faceless.niches.base import Niche


@dataclass
class Shot:
    narration: str
    visual_prompt: str
    seconds: float


@dataclass
class ScriptResult:
    title: str
    body: str
    shots: list[Shot]
    description: str
    tags: list[str] = field(default_factory=list)


def generate_script(
    idea: IdeaResult, niche: Niche, *, fmt: str = "short", dry_run: bool = False
) -> ScriptResult:
    target = (
        niche.script.short_target_seconds
        if fmt == "short"
        else niche.script.longform_target_seconds
    )

    if dry_run:
        return ScriptResult(
            title=idea.angle[:80],
            body="Discipline is not a feeling. It is a decision you make again and again...",
            shots=[
                Shot("Discipline is not a feeling.", f"{niche.visual.style_prompt}, dawn", 3.0),
                Shot("It is a decision you repeat.", f"{niche.visual.style_prompt}, climber", 3.0),
            ],
            description="An original take on discipline.\n\n" + niche.script.cta,
            tags=list(niche.publish.default_tags),
        )

    system = (
        niche.script.persona_system_prompt
        + "\n\nReturn JSON with keys: title (str), body (str, the full narration), "
        "shots (list of {narration, visual_prompt, seconds}), description (str), "
        "tags (list of str). The shots' seconds should sum to roughly the target "
        f"duration ({target}s). Visual prompts must begin with this style: "
        f"'{niche.visual.style_prompt}'. End the narration with this CTA: "
        f"'{niche.script.cta}'."
    )
    user = (
        f"Idea angle: {idea.angle}\n"
        f"Rationale: {idea.rationale}\n"
        f"Format: {fmt}, target ~{target} seconds.\n"
        "Write the script now."
    )
    data = complete_json(system, user, max_tokens=2500)
    shots = [
        Shot(
            narration=str(s.get("narration", "")),
            visual_prompt=str(s.get("visual_prompt", "")),
            seconds=float(s.get("seconds", 3.0)),
        )
        for s in data.get("shots", [])
    ]
    return ScriptResult(
        title=str(data["title"]),
        body=str(data["body"]),
        shots=shots,
        description=str(data.get("description", "")),
        tags=[str(t) for t in data.get("tags", niche.publish.default_tags)],
    )
