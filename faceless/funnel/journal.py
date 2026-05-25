from __future__ import annotations

from faceless.config import get_settings
from faceless.funnel.pdf import MUTED, ensure_parent, styles
from faceless.niches.base import Niche


def _content(niche: Niche, days: int, *, dry_run: bool) -> dict:
    """Journal copy: {title, subtitle, intro, prompts:[str]} (len(prompts)==days)."""
    if dry_run:
        seeds = [
            "What is the one hard thing you'll do today before anything else?",
            "Where did you rely on motivation yesterday instead of a system?",
            "What will you say no to today to protect your focus?",
            "Name the smallest first step on the task you're avoiding.",
            "What did discipline cost you today — and was it worth it?",
        ]
        return {
            "title": f"The {days}-Day Discipline Journal",
            "subtitle": "Build the habit of doing it anyway",
            "intro": (
                "Motivation is unreliable. Systems are not. For the next "
                f"{days} days, answer one prompt each morning and take one small "
                "action. Consistency compounds — show up."
            ),
            "prompts": [seeds[i % len(seeds)] for i in range(days)],
        }
    from faceless.llm import complete_json

    system = (
        "You design a guided journal for a self-improvement audience. Return JSON: "
        "{title, subtitle, intro, prompts:[str]} where prompts has EXACTLY "
        f"{days} distinct, specific daily reflection/action prompts (second person, "
        "concrete, no repetition).\n\nChannel persona:\n" + niche.script.persona_system_prompt
    )
    return complete_json(
        system, f"Create a {days}-day discipline journal.", max_tokens=3000
    )


def generate_journal(
    niche: Niche, out_path: str, *, days: int = 30, dry_run: bool = False
) -> str:
    """Render a KDP/Gumroad-ready journal interior PDF (6x9). Returns the path."""
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
    )

    ensure_parent(out_path)
    content = _content(niche, days, dry_run=dry_run)
    s = styles()
    brand = get_settings().brand_name

    flow = [
        Spacer(1, 2 * inch),
        Paragraph(content["title"], s["title"]),
        Paragraph(content.get("subtitle", ""), s["subtitle"]),
        Spacer(1, 2 * inch),
        Paragraph(brand, s["footer"]),
        PageBreak(),
        Paragraph("Start here", s["heading"]),
        Paragraph(content["intro"], s["body"]),
        PageBreak(),
    ]

    for i, prompt in enumerate(content["prompts"], start=1):
        flow.append(Paragraph(f"Day {i}", s["heading"]))
        flow.append(Paragraph(prompt, s["body"]))
        flow.append(Spacer(1, 0.2 * inch))
        for _ in range(12):  # writing lines
            flow.append(Spacer(1, 0.28 * inch))
            flow.append(HRFlowable(width="100%", thickness=0.4, color=MUTED))
        flow.append(PageBreak())

    SimpleDocTemplate(
        out_path, pagesize=(6 * inch, 9 * inch), title=content["title"]
    ).build(flow)
    return out_path
