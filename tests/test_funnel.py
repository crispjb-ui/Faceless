from __future__ import annotations

from faceless.funnel import (
    generate_journal,
    generate_landing_page,
    generate_lead_magnet,
    generate_welcome_sequence,
)
from faceless.niches import get_niche


def _pdf_ok(path) -> bool:
    return path.exists() and path.read_bytes()[:5] == b"%PDF-"


def test_lead_magnet_pdf(tmp_path):
    out = tmp_path / "lm.pdf"
    generate_lead_magnet(get_niche("self_improvement"), str(out), dry_run=True)
    assert _pdf_ok(out)


def test_journal_pdf(tmp_path):
    out = tmp_path / "journal.pdf"
    generate_journal(get_niche("self_improvement"), str(out), days=7, dry_run=True)
    assert _pdf_ok(out)


def test_welcome_emails(tmp_path):
    paths = generate_welcome_sequence(get_niche("self_improvement"), str(tmp_path), dry_run=True)
    assert len(paths) == 5
    assert "Subject:" in (tmp_path / "email_01.md").read_text()


def test_landing_page(tmp_path):
    out = tmp_path / "index.html"
    generate_landing_page(str(out))
    body = out.read_text()
    assert "<form" in body and "email" in body
