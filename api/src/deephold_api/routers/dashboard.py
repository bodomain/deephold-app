"""Macro dashboard endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from deephold_api.deps import get_db
from deephold_api.schemas import DashboardItem, DashboardResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Fixed list of dashboard series
DASHBOARD_SERIES = [
    "price:^GSPC",
    "bond:DGS10",
    "bond:DGS2",
    "macro:FRED:FEDFUNDS",
    "macro:FRED:CPIAUCSL",
    "macro:FRED:UNRATE",
    "macro:FRED:VIXCLS",
    "fx:EUR/USD",
    "price:BZ=F",
]


def _parse(sid: str) -> tuple[str, str]:
    kind, ident = sid.split(":", 1)
    return kind, ident


def _fetch_last_n(
    db: Session, sid: str, n: int = 30
) -> tuple[list[float], float | None, object | None, float | None]:
    """Return (sparkline_values, latest_value, latest_date, change_pct)."""
    kind, ident = _parse(sid)
    params: dict = {"n": n}

    if kind == "price":
        params["sym"] = ident
        rows = db.execute(
            text("""
            SELECT p.date, p.close AS value FROM prices_daily p
            JOIN instrument_identifiers ii ON p.instrument_id = ii.instrument_id
            WHERE ii.scheme = 'YAHOO' AND ii.value = :sym
            ORDER BY p.date DESC LIMIT :n
        """),
            params,
        ).fetchall()
    elif kind == "bond":
        params["sym"] = ident
        rows = db.execute(
            text("""
            SELECT b.date, b.yield AS value FROM bond_yields b
            JOIN instrument_identifiers ii ON b.instrument_id = ii.instrument_id
            WHERE ii.scheme = 'YAHOO' AND ii.value = :sym
            ORDER BY b.date DESC LIMIT :n
        """),
            params,
        ).fetchall()
    elif kind == "fx":
        ccy_from, ccy_to = ident.split("/", 1)
        params.update(cf=ccy_from, ct=ccy_to)
        rows = db.execute(
            text("""
            SELECT date, rate AS value FROM fx_rates_daily
            WHERE ccy_from = :cf AND ccy_to = :ct
            ORDER BY date DESC LIMIT :n
        """),
            params,
        ).fetchall()
    elif kind == "macro":
        params["sid"] = ident
        rows = db.execute(
            text("""
            SELECT date, value FROM macro_observations
            WHERE series_id = :sid ORDER BY date DESC LIMIT :n
        """),
            params,
        ).fetchall()
    else:
        return [], None, None, None

    if not rows:
        return [], None, None, None

    values = [float(r.value) if r.value is not None else 0.0 for r in reversed(rows)]
    latest_val = float(rows[0].value) if rows[0].value is not None else None
    latest_dt = rows[0].date

    change_pct: float | None = None
    if len(rows) >= 2 and rows[1].value and rows[0].value:
        change_pct = ((float(rows[0].value) - float(rows[1].value)) / float(rows[1].value)) * 100.0

    return values, latest_val, latest_dt, change_pct


@router.get("/macro", response_model=DashboardResponse)
def get_macro_dashboard(db: Session = Depends(get_db)) -> DashboardResponse:
    """Get macro dashboard: latest values + sparklines for key series."""
    items: list[DashboardItem] = []

    for sid in DASHBOARD_SERIES:
        sparkline, latest_val, latest_dt, change_pct = _fetch_last_n(db, sid)

        # Get display name
        kind, ident = _parse(sid)
        if kind in ("price", "bond"):
            row = db.execute(
                text("""
                SELECT i.name FROM instruments i
                JOIN instrument_identifiers ii ON i.instrument_id = ii.instrument_id
                WHERE ii.scheme = 'YAHOO' AND ii.value = :sym
            """),
                {"sym": ident},
            ).fetchone()
            name = row.name if row else sid
        elif kind == "fx":
            name = ident
        elif kind == "macro":
            row = db.execute(
                text("SELECT name FROM macro_series WHERE series_id = :sid"), {"sid": ident}
            ).fetchone()
            name = row.name if row else sid
        else:
            name = sid

        items.append(
            DashboardItem(
                id=sid,
                name=name,
                latest_value=latest_val,
                latest_date=latest_dt,
                change_pct=change_pct,
                sparkline=sparkline,
            )
        )

    return DashboardResponse(items=items)
