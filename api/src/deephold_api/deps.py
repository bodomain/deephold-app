"""FastAPI dependencies (DB session, auth, etc.)."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from deephold_api.auth import decode_access_token, get_user_by_id
from deephold_api.db_session import get_sessionmaker
from deephold_api.models import User

_security = HTTPBearer(auto_error=False)


def get_db() -> Iterator[Session]:
    """Yield a SQLAlchemy session for a single request."""
    session = get_sessionmaker()()
    try:
        yield session
    finally:
        session.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security),
    db: Session = Depends(get_db),
) -> User:
    """Require authentication: returns the current User or raises 401."""
    if credentials is None:
        raise PermissionError("Not authenticated")
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise PermissionError("Invalid or expired token")
    user_id = int(payload.get("sub", 0))
    user = get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise PermissionError("User not found or inactive")
    return user
