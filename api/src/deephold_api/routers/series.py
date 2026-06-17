"""Series browser, detail, observations, candles, stats, export."""

from __future__ import annotations

import csv
import io
import time
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from deephold_api.analytics import compute_stats
from deephold_api.deps import get_db
from deephold_api.schemas import (
    Candle,
    Observation,
    SeriesDetail,
    SeriesStats,
    SeriesSummary,
)

router = APIRouter(prefix="/api/series", tags=["series"])

# In-memory cache for the series list (TTL in seconds)
_CACHE_TTL = 300
_cache: tuple[float, list[SeriesSummary]] = (0.0, [])


def _parse_series_id(series_id: str) -> tuple[str, str]:
    """Split 'price:AAPL' → ('price', 'AAPL')."""
    parts = series_id.split(":", 1)
    if len(parts) != 2:
        raise HTTPException(400, f"Invalid series ID: {series_id}")
    return parts[0], parts[1]


def _load_all_series(db: Session) -> list[SeriesSummary]:
    """Load all series from the materialized view (fast)."""
    rows = db.execute(
        text("""
        SELECT series_type, identifier, name, asset_class, currency, source,
               obs_count, first_date, last_date, latest_value
        FROM mv_series_stats
        ORDER BY series_type, name
    """)
    ).fetchall()

    results: list[SeriesSummary] = []
    for r in rows:
        results.append(
            SeriesSummary(
                id=f"{r.series_type}:{r.identifier}",
                type=r.series_type,
                identifier=r.identifier,
                name=r.name,
                asset_class=r.asset_class,
                source=r.source,
                currency=r.currency,
                count=r.obs_count,
                first_date=r.first_date,
                last_date=r.last_date,
                latest_value=float(r.latest_value) if r.latest_value is not None else None,
            )
        )
    return results


def _get_all_series(db: Session) -> list[SeriesSummary]:
    """Get all series with in-memory caching (5 min TTL)."""
    global _cache
    now = time.time()
    if _cache[0] and (now - _cache[0]) < _CACHE_TTL:
        return _cache[1]
    series = _load_all_series(db)
    _cache = (now, series)
    return series


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


@router.get("", response_model=list[SeriesSummary])
def list_series(
    type: str | None = Query(None, description="price, bond, fx, macro"),
    asset_class: str | None = None,
    source: str | None = None,
    q: str | None = Query(None, description="Search in name/identifier"),
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[SeriesSummary]:
    """List all available series with optional filters."""
    results = _get_all_series(db)

    # Filter
    if type:
        results = [r for r in results if r.type == type]
    if asset_class:
        results = [r for r in results if r.asset_class == asset_class]
    if source:
        results = [r for r in results if (r.source or "") == source]
    if q:
        ql = q.lower()
        results = [r for r in results if ql in (r.name or "").lower() or ql in r.identifier.lower()]

    return results[offset : offset + limit]


@router.post("/refresh-cache")
def refresh_cache(db: Session = Depends(get_db)) -> dict:
    """Force-refresh the in-memory series cache + materialized view."""
    global _cache
    db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_series_stats"))
    db.commit()
    _cache = (0.0, [])
    return {"status": "ok", "message": "Cache refreshed"}


# ---------------------------------------------------------------------------
# Detail
# ---------------------------------------------------------------------------


@router.get("/{series_id}", response_model=SeriesDetail)
def get_series(series_id: str, db: Session = Depends(get_db)) -> SeriesDetail:
    """Get metadata for a single series."""
    kind, ident = _parse_series_id(series_id)

    if kind == "price":
        row = db.execute(
            text("""
            SELECT ii.value, i.name, i.asset_class, i.currency,
                   'yahoo' AS source, COUNT(p.date) AS cnt,
                   MIN(p.date) AS first_date, MAX(p.date) AS last_date
            FROM instruments i
            JOIN instrument_identifiers ii ON i.instrument_id = ii.instrument_id
            JOIN prices_daily p ON i.instrument_id = p.instrument_id
            WHERE ii.scheme = 'YAHOO' AND ii.value = :sym
            GROUP BY ii.value, i.name, i.asset_class, i.currency
        """),
            {"sym": ident},
        ).fetchone()
    elif kind == "bond":
        row = db.execute(
            text("""
            SELECT ii.value, i.name, 'bond_gov' AS asset_class, '%' AS currency,
                   'fred' AS source, COUNT(b.date) AS cnt,
                   MIN(b.date) AS first_date, MAX(b.date) AS last_date
            FROM instruments i
            JOIN instrument_identifiers ii ON i.instrument_id = ii.instrument_id
            JOIN bond_yields b ON i.instrument_id = b.instrument_id
            WHERE ii.scheme = 'YAHOO' AND ii.value = :sym
            GROUP BY ii.value, i.name
        """),
            {"sym": ident},
        ).fetchone()
    elif kind == "fx":
        ccy_from, ccy_to = ident.split("/", 1)
        row = db.execute(
            text("""
            SELECT :id AS value, :id AS name, 'fx' AS asset_class, ccy_to AS currency,
                   'mixed' AS source, COUNT(*) AS cnt,
                   MIN(date) AS first_date, MAX(date) AS last_date
            FROM fx_rates_daily WHERE ccy_from = :cf AND ccy_to = :ct
        """),
            {"id": ident, "cf": ccy_from, "ct": ccy_to},
        ).fetchone()
    elif kind == "macro":
        row = db.execute(
            text("""
            SELECT ms.series_id AS value, ms.name, 'macro' AS asset_class,
                   ms.unit AS currency, ms.source, ms.frequency,
                   COUNT(mo.date) AS cnt,
                   MIN(mo.date) AS first_date, MAX(mo.date) AS last_date
            FROM macro_series ms
            JOIN macro_observations mo ON ms.series_id = mo.series_id
            WHERE ms.series_id = :sid
            GROUP BY ms.series_id, ms.name, ms.source, ms.unit, ms.frequency
        """),
            {"sid": ident},
        ).fetchone()
    else:
        raise HTTPException(400, f"Unknown series type: {kind}")

    if not row:
        raise HTTPException(404, f"Series not found: {series_id}")

    return SeriesDetail(
        id=series_id,
        type=kind,
        identifier=row.value,
        name=row.name,
        asset_class=row.asset_class,
        source=row.source,
        currency=row.currency,
        frequency=getattr(row, "frequency", None),
        count=row.cnt,
        first_date=row.first_date,
        last_date=row.last_date,
    )


# ---------------------------------------------------------------------------
# Observations
# ---------------------------------------------------------------------------


def _fetch_observations(
    kind: str, ident: str, db: Session, start: date | None = None, end: date | None = None
) -> list[Observation]:
    """Fetch observations for a series."""
    params: dict = {}
    date_filter = ""
    if start:
        date_filter += " AND date >= :start"
        params["start"] = start
    if end:
        date_filter += " AND date <= :end"
        params["end"] = end

    if kind == "price":
        params["sym"] = ident
        rows = db.execute(
            text(f"""
            SELECT p.date, p.close AS value
            FROM prices_daily p
            JOIN instrument_identifiers ii ON p.instrument_id = ii.instrument_id
            WHERE ii.scheme = 'YAHOO' AND ii.value = :sym{date_filter}
            ORDER BY p.date
        """),
            params,
        ).fetchall()
    elif kind == "bond":
        params["sym"] = ident
        rows = db.execute(
            text(f"""
            SELECT b.date, b.yield AS value
            FROM bond_yields b
            JOIN instrument_identifiers ii ON b.instrument_id = ii.instrument_id
            WHERE ii.scheme = 'YAHOO' AND ii.value = :sym{date_filter}
            ORDER BY b.date
        """),
            params,
        ).fetchall()
    elif kind == "fx":
        ccy_from, ccy_to = ident.split("/", 1)
        params.update(cf=ccy_from, ct=ccy_to)
        rows = db.execute(
            text(f"""
            SELECT date, rate AS value
            FROM fx_rates_daily
            WHERE ccy_from = :cf AND ccy_to = :ct{date_filter}
            ORDER BY date
        """),
            params,
        ).fetchall()
    elif kind == "macro":
        params["sid"] = ident
        rows = db.execute(
            text(f"""
            SELECT date, value
            FROM macro_observations
            WHERE series_id = :sid{date_filter}
            ORDER BY date
        """),
            params,
        ).fetchall()
    else:
        raise HTTPException(400, f"Unknown series type: {kind}")

    return [
        Observation(date=r.date, value=float(r.value) if r.value is not None else None)
        for r in rows
    ]


@router.get("/{series_id}/observations", response_model=list[Observation])
def get_observations(
    series_id: str,
    start: date | None = None,
    end: date | None = None,
    limit: int = Query(10000, le=100000),
    db: Session = Depends(get_db),
) -> list[Observation]:
    """Fetch observations (date, value) for a series."""
    kind, ident = _parse_series_id(series_id)
    obs = _fetch_observations(kind, ident, db, start, end)
    return obs[:limit]


# ---------------------------------------------------------------------------
# Candles (price series only)
# ---------------------------------------------------------------------------


@router.get("/{series_id}/candles", response_model=list[Candle])
def get_candles(
    series_id: str,
    start: date | None = None,
    end: date | None = None,
    limit: int = Query(10000, le=100000),
    db: Session = Depends(get_db),
) -> list[Candle]:
    """Fetch OHLCV candles for a price series."""
    kind, ident = _parse_series_id(series_id)
    if kind != "price":
        raise HTTPException(400, "Candles only available for price series")

    params: dict = {"sym": ident}
    date_filter = ""
    if start:
        date_filter += " AND p.date >= :start"
        params["start"] = start
    if end:
        date_filter += " AND p.date <= :end"
        params["end"] = end

    rows = db.execute(
        text(f"""
        SELECT p.date, p.open, p.high, p.low, p.close, p.volume
        FROM prices_daily p
        JOIN instrument_identifiers ii ON p.instrument_id = ii.instrument_id
        WHERE ii.scheme = 'YAHOO' AND ii.value = :sym{date_filter}
        ORDER BY p.date
    """),
        params,
    ).fetchall()

    candles = [
        Candle(
            date=r.date,
            open=float(r.open) if r.open is not None else None,
            high=float(r.high) if r.high is not None else None,
            low=float(r.low) if r.low is not None else None,
            close=float(r.close) if r.close is not None else None,
            volume=r.volume,
        )
        for r in rows
    ]
    return candles[:limit]


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


@router.get("/{series_id}/stats", response_model=SeriesStats)
def get_stats(series_id: str, db: Session = Depends(get_db)) -> SeriesStats:
    """Compute financial statistics for a series."""
    kind, ident = _parse_series_id(series_id)
    obs = _fetch_observations(kind, ident, db)
    dates = [o.date for o in obs]
    values = [o.value for o in obs]
    return compute_stats(dates, values)


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


@router.get("/{series_id}/export")
def export_series(
    series_id: str,
    format: str = "csv",
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Download series observations as CSV or JSON."""
    kind, ident = _parse_series_id(series_id)
    obs = _fetch_observations(kind, ident, db)

    if format == "json":
        import json

        data = [{"date": o.date.isoformat(), "value": o.value} for o in obs]
        return StreamingResponse(
            io.BytesIO(json.dumps(data, indent=2).encode()),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={series_id.replace(':', '_')}.json"
            },
        )

    # CSV
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["date", "value"])
    for o in obs:
        writer.writerow([o.date.isoformat(), o.value])
    return StreamingResponse(
        io.BytesIO(buf.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={series_id.replace(':', '_')}.csv"},
    )
