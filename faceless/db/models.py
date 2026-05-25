from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class JobStatus(str, enum.Enum):
    discovered = "discovered"
    ideated = "ideated"
    scripted = "scripted"
    compliance_blocked = "compliance_blocked"
    compliance_flagged = "compliance_flagged"
    assets_ready = "assets_ready"
    rendered = "rendered"
    awaiting_review = "awaiting_review"
    approved = "approved"
    rejected = "rejected"
    published = "published"
    failed = "failed"


class Candidate(Base):
    """A trending source video discovered for a niche."""

    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    niche: Mapped[str] = mapped_column(String(64), index=True)
    video_id: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, default="")
    channel_title: Mapped[str] = mapped_column(String(255), default="")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    velocity: Mapped[float] = mapped_column(Float, default=0.0)  # views/hour
    score: Mapped[float] = mapped_column(Float, default=0.0)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    ideas: Mapped[list[Idea]] = relationship(back_populates="candidate")


class Idea(Base):
    """A differentiated, original content idea derived from a candidate."""

    __tablename__ = "ideas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    niche: Mapped[str] = mapped_column(String(64), index=True)
    candidate_id: Mapped[int | None] = mapped_column(ForeignKey("candidates.id"))
    angle: Mapped[str] = mapped_column(Text)  # the differentiated hook/angle
    rationale: Mapped[str] = mapped_column(Text, default="")
    predicted_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    candidate: Mapped[Candidate | None] = relationship(back_populates="ideas")
    job: Mapped[VideoJob | None] = relationship(back_populates="idea", uselist=False)


class Script(Base):
    __tablename__ = "scripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("video_jobs.id"))
    title: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)  # narration text
    shot_list_json: Mapped[str] = mapped_column(Text, default="[]")
    description: Mapped[str] = mapped_column(Text, default="")
    tags_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    job: Mapped[VideoJob] = relationship(back_populates="script")


class VideoJob(Base):
    """One video moving through the pipeline."""

    __tablename__ = "video_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    niche: Mapped[str] = mapped_column(String(64), index=True)
    idea_id: Mapped[int] = mapped_column(ForeignKey("ideas.id"))
    format: Mapped[str] = mapped_column(String(16), default="short")  # short | longform
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.ideated)
    compliance_notes: Mapped[str] = mapped_column(Text, default="")
    voice_path: Mapped[str | None] = mapped_column(Text)
    video_path: Mapped[str | None] = mapped_column(Text)
    thumbnail_path: Mapped[str | None] = mapped_column(Text)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

    idea: Mapped[Idea] = relationship(back_populates="job")
    script: Mapped[Script | None] = relationship(
        back_populates="job", uselist=False, cascade="all, delete-orphan"
    )
    uploads: Mapped[list[Upload]] = relationship(back_populates="job")


class Upload(Base):
    """A published instance of a job on a specific platform."""

    __tablename__ = "uploads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("video_jobs.id"))
    platform: Mapped[str] = mapped_column(String(32))  # youtube_shorts | tiktok | ...
    platform_video_id: Mapped[str | None] = mapped_column(String(64))
    url: Mapped[str | None] = mapped_column(Text)
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    job: Mapped[VideoJob] = relationship(back_populates="uploads")
    metrics: Mapped[list[Metric]] = relationship(back_populates="upload")


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id"))
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    avg_view_pct: Mapped[float] = mapped_column(Float, default=0.0)
    revenue: Mapped[float] = mapped_column(Float, default=0.0)

    upload: Mapped[Upload] = relationship(back_populates="metrics")
