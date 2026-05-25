from __future__ import annotations

from faceless.niches.base import Niche
from faceless.niches.self_improvement import SELF_IMPROVEMENT

_REGISTRY: dict[str, Niche] = {}


def register(niche: Niche) -> None:
    _REGISTRY[niche.id] = niche


def get_niche(niche_id: str) -> Niche:
    try:
        return _REGISTRY[niche_id]
    except KeyError:
        known = ", ".join(sorted(_REGISTRY)) or "(none)"
        raise KeyError(f"Unknown niche '{niche_id}'. Registered: {known}") from None


def list_niches() -> list[str]:
    return sorted(_REGISTRY)


# Built-in niches. Add new channels here (or via register() from a plugin).
register(SELF_IMPROVEMENT)
