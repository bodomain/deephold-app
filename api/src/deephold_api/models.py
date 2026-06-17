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


_MV_SERIES_STATS_SQL = """
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_series_stats AS
SELECT
  'price' AS series_type, ii.value AS identifier, i.name, i.asset_class,
  i.currency, v.code AS source, COUNT(p.date) AS obs_count,
  MIN(p.date) AS first_date, MAX(p.date) AS last_date,
  (SELECT p2.close FROM prices_daily p2 WHERE p2.instrument_id = i.instrument_id ORDER BY p2.date DESC LIMIT 1) AS latest_value
FROM instruments i
JOIN instrument_identifiers ii ON i.instrument_id = ii.instrument_id
JOIN prices_daily p ON i.instrument_id = p.instrument_id
LEFT JOIN vendors v ON p.vendor_id = v.vendor_id
WHERE ii.scheme = 'YAHOO'
GROUP BY ii.value, i.name, i.asset_class, i.currency, v.code, i.instrument_id
UNION ALL
SELECT
  'bond' AS series_type, ii.value AS identifier, i.name, 'bond_gov' AS asset_class,
  '%' AS currency, 'fred' AS source, COUNT(b.date) AS obs_count,
  MIN(b.date) AS first_date, MAX(b.date) AS last_date,
  (SELECT b2.yield FROM bond_yields b2 WHERE b2.instrument_id = i.instrument_id ORDER BY b2.date DESC LIMIT 1) AS latest_value
FROM instruments i
JOIN instrument_identifiers ii ON i.instrument_id = ii.instrument_id
JOIN bond_yields b ON i.instrument_id = b.instrument_id
WHERE ii.scheme = 'YAHOO'
GROUP BY ii.value, i.name, i.instrument_id
UNION ALL
SELECT
  'fx' AS series_type, f.ccy_from || '/' || f.ccy_to AS identifier,
  f.ccy_from || '/' || f.ccy_to AS name, 'fx' AS asset_class, f.ccy_to AS currency,
  'mixed' AS source, COUNT(*) AS obs_count, MIN(f.date) AS first_date, MAX(f.date) AS last_date,
  (SELECT f2.rate FROM fx_rates_daily f2 WHERE f2.ccy_from = f.ccy_from AND f2.ccy_to = f.ccy_to ORDER BY f2.date DESC LIMIT 1) AS latest_value
FROM fx_rates_daily f GROUP BY f.ccy_from, f.ccy_to
UNION ALL
SELECT
  'macro' AS series_type, ms.series_id AS identifier, ms.name, 'macro' AS asset_class,
  ms.unit AS currency, ms.source, COUNT(mo.date) AS obs_count,
  MIN(mo.date) AS first_date, MAX(mo.date) AS last_date,
  (SELECT mo2.value FROM macro_observations mo2 WHERE mo2.series_id = ms.series_id ORDER BY mo2.date DESC LIMIT 1) AS latest_value
FROM macro_series ms JOIN macro_observations mo ON ms.series_id = mo.series_id
GROUP BY ms.series_id, ms.name, ms.source, ms.unit
"""


def init_app_schema(engine=None) -> None:
    """Create the 'app' schema, tables, and mv_series_stats view."""
    from deephold_api.config import get_settings

    if engine is None:
        engine = create_engine(get_settings().database_url)
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS app"))
        conn.commit()
    AppBase.metadata.create_all(engine)
    with engine.connect() as conn:
        conn.execute(text(_MV_SERIES_STATS_SQL))
        conn.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_series_stats_id "
            "ON mv_series_stats (series_type, identifier)"
        ))
        conn.commit()
