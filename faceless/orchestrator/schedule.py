from __future__ import annotations

from dataclasses import dataclass, field

from faceless.analytics import collect_metrics
from faceless.orchestrator.pipeline import produce_batch, publish_approved


@dataclass
class DailyResult:
    published: int = 0
    produced: int = 0
    awaiting_review: int = 0
    metrics: int = 0
    errors: list[str] = field(default_factory=list)


def daily_flow(
    niche_id: str,
    *,
    produce_limit: int = 7,
    publish_limit: int = 10,
    spread_minutes: int = 0,
    dry_run: bool = False,
) -> DailyResult:
    """One daily cycle of the factory.

    Order: publish jobs approved since the last run → produce a fresh batch for
    review → refresh analytics. Stages are isolated so one failure does not abort
    the others; failures are collected in `errors`. The human approval gate sits
    between runs: today's produced batch is published on the next run after you
    approve it (or sooner via `faceless publish`).
    """
    result = DailyResult()

    try:
        result.published = publish_approved(
            niche_id, limit=publish_limit, spread_minutes=spread_minutes, dry_run=dry_run
        )
    except Exception as exc:  # noqa: BLE001 - daily job must keep going
        result.errors.append(f"publish: {exc}")

    try:
        summary = produce_batch(niche_id, limit=produce_limit, dry_run=dry_run)
        result.produced = summary.produced
        result.awaiting_review = summary.awaiting_review
    except Exception as exc:  # noqa: BLE001
        result.errors.append(f"produce: {exc}")

    try:
        result.metrics = collect_metrics(dry_run=dry_run)
    except Exception as exc:  # noqa: BLE001
        result.errors.append(f"analytics: {exc}")

    return result
