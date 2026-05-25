"""Optional Prefect entrypoint for the daily flow.

Requires the orchestration extra:  pip install -e ".[orchestration]"

Run as a long-lived scheduled deployment:
    python -m faceless.orchestrator.prefect_flow

Or trigger once from Python via faceless_daily(...).
"""
from __future__ import annotations

from prefect import flow, get_run_logger

from faceless.orchestrator.schedule import DailyResult, daily_flow


@flow(name="faceless-daily")
def faceless_daily(
    niche_id: str = "self_improvement",
    produce_limit: int = 7,
    publish_limit: int = 10,
    spread_minutes: int = 90,
    dry_run: bool = False,
) -> DailyResult:
    result = daily_flow(
        niche_id,
        produce_limit=produce_limit,
        publish_limit=publish_limit,
        spread_minutes=spread_minutes,
        dry_run=dry_run,
    )
    logger = get_run_logger()
    logger.info("Daily flow result: %s", result)
    if result.errors:
        logger.error("Daily flow errors: %s", result.errors)
    return result


if __name__ == "__main__":
    # Serve a scheduled deployment (default: 14:00 UTC daily).
    faceless_daily.serve(name="daily", cron="0 14 * * *")
