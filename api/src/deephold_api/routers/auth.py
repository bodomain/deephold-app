"""Auth router: login, logout, me."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from deephold_api.auth import (
    authenticate_user,
    create_access_token,
    decode_access_token,
    get_user_by_id,
)
from deephold_api.config import get_settings
from deephold_api.deps import get_db
from deephold_api.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: int
    email: str
    name: str | None
    is_admin: bool


class LoginResponse(BaseModel):
    token: str
    user: UserResponse


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, response: Response, db: Session = Depends(get_db)) -> LoginResponse:
    """Login with email + password, returns JWT token."""
    user = authenticate_user(db, req.email, req.password)
    if user is None:
        raise HTTPException(401, "Invalid email or password")

    token = create_access_token(user.user_id, user.email, user.is_admin)

    # Also set as httpOnly cookie
    settings = get_settings()
    response.set_cookie(
        key="deephold_token",
        value=token,
        httponly=True,
        secure=False,  # set True in production with HTTPS
        samesite="lax",
        max_age=settings.jwt_expire_minutes * 60,
    )

    return LoginResponse(
        token=token,
        user=UserResponse(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            is_admin=user.is_admin,
        ),
    )


@router.post("/logout")
def logout(response: Response) -> dict:
    """Logout by clearing the auth cookie."""
    response.delete_cookie("deephold_token")
    return {"status": "ok"}


@router.get("/me", response_model=UserResponse)
def me(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Get current authenticated user."""
    user = _require_user(credentials, db)
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        name=user.name,
        is_admin=user.is_admin,
    )


def _require_user(
    credentials: HTTPAuthorizationCredentials | None,
    db: Session,
) -> User:
    """Extract and validate the user from JWT. Raises 401 if not authenticated."""
    if credentials is None:
        raise HTTPException(401, "Not authenticated")
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(401, "Invalid or expired token")
    user_id = int(payload.get("sub", 0))
    user = get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise HTTPException(401, "User not found or inactive")
    return user
