from __future__ import annotations

import os
from contextlib import contextmanager
from functools import lru_cache
from typing import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from faceless.config import get_settings
from faceless.db.models import Base


@lru_cache
def get_engine() -> Engine:
    url = make_url(get_settings().database_url)
    # Ensure the parent dir exists for file-based sqlite (relative or absolute).
    if url.get_backend_name() == "sqlite" and url.database and url.database != ":memory:":
        parent = os.path.dirname(url.database)
        if parent:
            os.makedirs(parent, exist_ok=True)
    return create_engine(url, future=True)


@lru_cache
def _sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False, future=True)


def init_db() -> None:
    """Create all tables. Idempotent; safe to call on every startup."""
    Base.metadata.create_all(get_engine())


@contextmanager
def get_session() -> Iterator[Session]:
    session = _sessionmaker()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
