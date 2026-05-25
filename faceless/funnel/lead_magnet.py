from __future__ import annotations

from faceless.config import get_settings
from faceless.funnel.pdf import ensure_parent, styles
from faceless.niches.base import Niche


def _content(niche: Niche, *, dry_run: bool) -> dict:
    """Lead-magnet copy: {title, subtitle, sections:[{heading, tips:[str]}]}."""
    if dry_run:
        return {
            "title": "The Discipline Cheat Sheet",
            "subtitle": "5 systems to stop relying on motivation",
            "sections": [
                {"heading": "1. Win the morning", "tips": [
                    "Decide tonight what the first 30 minutes look like.",
                    "No phone until one hard thing is done.",
                    "Make the default action the easy one.",
                ]},
                {"heading": "2. Beat procrastination", "tips": [
                    "Shrink the task until starting feels trivial.",
                    "Set a 10-minute timer; permission to stop after.",
                    "Track streaks, not outcomes.",
                ]},
                {"heading": "3. Protect your focus", "tips": [
                    "One screen, one task, notifications off.",
                    "Batch shallow work into a single window.",
                    "Treat deep work like an appointment you can't move.",
                ]},
                {"heading": "4. Build the identity", "tips": [
                    "Ask 'what would a disciplined person do?' then do that.",
                    "Cast small votes daily — they compound into who you are.",
                    "Never miss twice; one slip is noise, two is a pattern.",
                ]},
                {"heading": "5. Engineer the environment", "tips": [
                    "Put the good habit one step closer, the bad one step farther.",
                    "Prep tomorrow's friction tonight (clothes, tabs, tools).",
                    "Remove the choice and you remove the willpower tax.",
                ]},
            ],
        }
    from faceless.llm import complete_json

    system = (
        "You write a concise, genuinely useful one-page lead magnet (cheat sheet) for a "
        "self-improvement audience. Return JSON: {title, subtitle, sections:[{heading, "
        "tips:[str]}]}. Produce EXACTLY 5 sections with 3-5 punchy, specific, actionable "
        "tips each, and a subtitle whose number matches the 5 sections (e.g. '5 systems "
        "to ...'). No fluff, no platitudes.\n\nChannel persona:\n"
        + niche.script.persona_system_prompt
    )
    return complete_json(system, "Create the Discipline Cheat Sheet.", max_tokens=1600)


def generate_lead_magnet(niche: Niche, out_path: str, *, dry_run: bool = False) -> str:
    """Render the free opt-in lead magnet to a PDF. Returns the path."""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

    ensure_parent(out_path)
    content = _content(niche, dry_run=dry_run)
    s = styles()
    brand = get_settings().brand_name

    flow = [
        Paragraph(content["title"], s["title"]),
        Paragraph(content.get("subtitle", ""), s["subtitle"]),
    ]
    for section in content["sections"]:
        flow.append(Paragraph(section["heading"], s["heading"]))
        flow.append(
            ListFlowable(
                [ListItem(Paragraph(tip, s["bullet"]), leftIndent=12) for tip in section["tips"]],
                bulletType="bullet",
            )
        )
    flow.append(Spacer(1, 12))
    flow.append(Paragraph(f"{brand} — keep going.", s["footer"]))

    SimpleDocTemplate(out_path, pagesize=letter, title=content["title"]).build(flow)
    return out_path
