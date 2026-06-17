"""FastAPI dependencies (DB session, auth, etc.)."""

from __future__ import annotations

from collections.abc import Iterator

from deephold_db.db.session import get_sessionmaker
from sqlalchemy.orm import Session


def get_db() -> Iterator[Session]:
    """Yield a SQLAlchemy session for a single request."""
    session = get_sessionmaker()()
    try:
        yield session
    finally:
        session.close()
