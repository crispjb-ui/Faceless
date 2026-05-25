from __future__ import annotations

import os

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

INK = HexColor("#1a1a1a")
ACCENT = HexColor("#c0392b")
MUTED = HexColor("#6b6b6b")


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title", parent=base["Title"], textColor=INK, fontSize=30, leading=34,
            spaceAfter=6, alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"], textColor=MUTED, fontSize=13, leading=18,
            spaceAfter=20, alignment=TA_CENTER,
        ),
        "heading": ParagraphStyle(
            "heading", parent=base["Heading2"], textColor=ACCENT, fontSize=15, leading=19,
            spaceBefore=14, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], textColor=INK, fontSize=11.5, leading=17,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"], textColor=INK, fontSize=11.5, leading=17,
            leftIndent=14, spaceAfter=4,
        ),
        "footer": ParagraphStyle(
            "footer", parent=base["Normal"], textColor=MUTED, fontSize=10, leading=14,
            alignment=TA_CENTER, spaceBefore=24,
        ),
    }


def ensure_parent(path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
