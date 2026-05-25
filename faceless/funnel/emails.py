from __future__ import annotations

import os

from faceless.config import get_settings
from faceless.niches.base import Niche


def _sequence(niche: Niche, count: int, store_url: str, *, dry_run: bool) -> list[dict]:
    """Welcome emails: [{subject, body}] driving toward the product."""
    if dry_run:
        cta = store_url or "[your store link]"
        return [
            {"subject": "Your Discipline Cheat Sheet is inside",
             "body": "Here's the cheat sheet you asked for. Read it once now, then keep "
                     "it where you'll see it tomorrow morning.\n\nReply and tell me the "
                     "one habit you're fixing first."},
            {"subject": "Motivation is a liar",
             "body": "Waiting to feel ready is why most people stall. Discipline is just "
                     "a decision you pre-make. Tonight, decide your first 30 minutes."},
            {"subject": "The 10-minute rule",
             "body": "Can't start? Set a timer for 10 minutes with permission to quit "
                     "after. You almost never will. Starting is the whole game."},
            {"subject": "What gets tracked gets done",
             "body": "Track the streak, not the outcome. A simple journal beats a perfect "
                     f"plan.\n\nIf you want mine: {cta}"},
            {"subject": "Want the full system?",
             "body": "The cheat sheet is the spark. The journal is the system — one prompt "
                     f"and one action a day until it's automatic.\n\nGrab it: {cta}"},
        ][:count]
    from faceless.llm import complete_json

    system = (
        "You write a warm, punchy welcome email sequence for a self-improvement email list. "
        f"Return JSON: {{emails:[{{subject, body}}]}} with EXACTLY {count} emails. Email 1 "
        "delivers the free cheat sheet; the middle emails give real value; the last 1-2 "
        f"softly pitch the journal at this link: {store_url or '[store link]'}. Plain text "
        "bodies, no fluff.\n\nChannel persona:\n" + niche.script.persona_system_prompt
    )
    data = complete_json(system, "Write the welcome sequence.", max_tokens=2500)
    return data["emails"][:count]


def generate_welcome_sequence(
    niche: Niche, out_dir: str, *, count: int = 5, dry_run: bool = False
) -> list[str]:
    """Write the welcome emails as markdown files (paste into Stan.store/ESP).

    Returns the list of file paths written.
    """
    os.makedirs(out_dir, exist_ok=True)
    store_url = get_settings().store_url or ""
    emails = _sequence(niche, count, store_url, dry_run=dry_run)
    paths = []
    for i, email in enumerate(emails, start=1):
        path = os.path.join(out_dir, f"email_{i:02d}.md")
        with open(path, "w") as f:
            f.write(f"# Subject: {email['subject']}\n\n{email['body']}\n")
        paths.append(path)
    return paths
