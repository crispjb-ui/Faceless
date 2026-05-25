from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from faceless.config import get_settings

app = typer.Typer(help="Faceless video automation factory", no_args_is_help=True)
console = Console()


@app.command()
def niches() -> None:
    """List registered niches."""
    from faceless.niches import list_niches

    for n in list_niches():
        console.print(f"- {n}")


@app.command("init-db")
def init_db_cmd() -> None:
    """Create database tables."""
    from faceless.db import init_db

    init_db()
    console.print("[green]Database initialized.[/green]")


@app.command()
def discover(
    niche: str = typer.Option(None, help="Niche id (defaults to FACELESS_NICHE)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Use offline fixtures"),
) -> None:
    """Find trending source videos for a niche and print them."""
    from faceless.discovery import discover_candidates
    from faceless.niches import get_niche

    niche_id = niche or get_settings().niche
    videos = discover_candidates(get_niche(niche_id), dry_run=dry_run)
    table = Table(title=f"Candidates: {niche_id}")
    table.add_column("velocity/hr", justify="right")
    table.add_column("views", justify="right")
    table.add_column("title")
    for v in videos:
        table.add_row(f"{v.velocity:,.0f}", f"{v.view_count:,}", v.title)
    console.print(table)


@app.command()
def run(
    niche: str = typer.Option(None, help="Niche id (defaults to FACELESS_NICHE)"),
    limit: int = typer.Option(5, help="How many videos to produce"),
    fmt: str = typer.Option("short", help="short | longform"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Run offline end-to-end"),
) -> None:
    """Produce a batch (discovery → render); leaves jobs awaiting review."""
    from faceless.orchestrator import produce_batch

    niche_id = niche or get_settings().niche
    summary = produce_batch(niche_id, limit=limit, fmt=fmt, dry_run=dry_run)
    console.print(summary)


@app.command()
def review(niche: str = typer.Option(None)) -> None:
    """List jobs awaiting human review."""
    from faceless.db import JobStatus, VideoJob, get_session, init_db

    init_db()
    niche_id = niche or get_settings().niche
    with get_session() as s:
        jobs = (
            s.query(VideoJob)
            .filter(VideoJob.niche == niche_id, VideoJob.status == JobStatus.awaiting_review)
            .all()
        )
        table = Table(title=f"Awaiting review: {niche_id}")
        table.add_column("job")
        table.add_column("title")
        table.add_column("video")
        for j in jobs:
            table.add_row(str(j.id), j.script.title if j.script else "?", j.video_path or "-")
    console.print(table)


@app.command()
def approve(job_id: int) -> None:
    """Mark a job approved for publishing."""
    _set_status(job_id, "approved")


@app.command()
def reject(job_id: int) -> None:
    """Mark a job rejected."""
    _set_status(job_id, "rejected")


@app.command()
def publish(
    niche: str = typer.Option(None),
    limit: int = typer.Option(10),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Upload approved jobs to YouTube and distribute."""
    from faceless.orchestrator import publish_approved

    niche_id = niche or get_settings().niche
    n = publish_approved(niche_id, limit=limit, dry_run=dry_run)
    console.print(f"[green]Published {n} job(s).[/green]")


def _set_status(job_id: int, status: str) -> None:
    from faceless.db import JobStatus, VideoJob, get_session, init_db

    init_db()
    with get_session() as s:
        job = s.get(VideoJob, job_id)
        if not job:
            console.print(f"[red]No job {job_id}[/red]")
            raise typer.Exit(1)
        job.status = JobStatus(status)
    console.print(f"Job {job_id} -> {status}")


if __name__ == "__main__":
    app()
