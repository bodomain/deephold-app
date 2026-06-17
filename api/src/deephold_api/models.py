"""SQLAlchemy models for the app schema (users, watchlists)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Text, create_engine, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class AppBase(DeclarativeBase):
    """Separate declarative base for the 'app' schema."""


class User(AppBase):
    __tablename__ = "users"
    __table_args__ = {"schema": "app"}

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str | None] = mapped_column(Text)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Watchlist(AppBase):
    __tablename__ = "watchlists"
    __table_args__ = {"schema": "app"}

    watchlist_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("app.users.user_id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    items: Mapped[list[WatchlistItem]] = relationship(
        back_populates="watchlist", cascade="all, delete-orphan"
    )


class WatchlistItem(AppBase):
    __tablename__ = "watchlist_items"
    __table_args__ = {"schema": "app"}

    watchlist_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("app.watchlists.watchlist_id", ondelete="CASCADE"), primary_key=True
    )
    series_id: Mapped[str] = mapped_column(Text, primary_key=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    watchlist: Mapped[Watchlist] = relationship(back_populates="items")


def init_app_schema(engine=None) -> None:
    """Create the 'app' schema and tables if they don't exist."""
    from deephold_api.config import get_settings

    if engine is None:
        engine = create_engine(get_settings().database_url)
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS app"))
        conn.commit()
    AppBase.metadata.create_all(engine)
