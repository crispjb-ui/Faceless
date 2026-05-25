from __future__ import annotations

from dataclasses import dataclass, field

from faceless.llm import complete_json
from faceless.niches.base import Niche
from faceless.scripting.generate import ScriptResult


@dataclass
class ComplianceVerdict:
    decision: str  # "pass" | "flag" | "block"
    issues: list[str] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return self.decision == "block"


def _rule_checks(script: ScriptResult, niche: Niche) -> list[str]:
    """Cheap deterministic checks that run before any LLM call."""
    issues: list[str] = []
    haystack = f"{script.title}\n{script.body}\n{script.description}".lower()
    for term in niche.compliance.banned_terms:
        if term.lower() in haystack:
            issues.append(f"banned term present: '{term}'")
    return issues


def check_compliance(
    script: ScriptResult, niche: Niche, *, dry_run: bool = False
) -> ComplianceVerdict:
    """Gate a script for IP, licensing, safety, and transformation.

    Hard rule violations block immediately. Otherwise an LLM reviews against the
    niche's extra_rules and returns pass/flag/block.
    """
    hard_issues = _rule_checks(script, niche)
    if hard_issues:
        return ComplianceVerdict(decision="block", issues=hard_issues)

    if dry_run:
        return ComplianceVerdict(decision="pass")

    rules = "\n".join(f"- {r}" for r in niche.compliance.extra_rules)
    system = (
        "You are a strict content-compliance reviewer for an automated video channel. "
        "Check the script against the rules. Respond JSON: {\"decision\": "
        "\"pass\"|\"flag\"|\"block\", \"issues\": [str]}. Use 'block' for clear "
        "copyright/IP, safety, or policy violations; 'flag' for things a human should "
        "double-check; 'pass' otherwise.\n\nRules:\n" + rules
    )
    user = f"Title: {script.title}\n\nNarration:\n{script.body}\n\nDescription:\n{script.description}"
    data = complete_json(system, user, heavy=True, max_tokens=600)
    return ComplianceVerdict(
        decision=str(data.get("decision", "flag")),
        issues=[str(i) for i in data.get("issues", [])],
    )
