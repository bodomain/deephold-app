"""Compare and correlation endpoints."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from deephold_api.deps import get_db
from deephold_api.schemas import (
    CompareRequest,
    CompareResponse,
    CompareSeries,
    CorrelationRequest,
    CorrelationResponse,
)

router = APIRouter(prefix="/api", tags=["compare"])


def _parse(sid: str) -> tuple[str, str]:
    return sid.split(":", 1)


def _fetch_series_df(sid: str, db: Session, start: date | None, end: date | None) -> pd.Series:
    """Fetch a series as a pandas Series indexed by date."""
    kind, ident = _parse(sid)
    params: dict = {}
    dfilt = ""
    if start:
        dfilt += " AND date >= :start"
        params["start"] = start
    if end:
        dfilt += " AND date <= :end"
        params["end"] = end

    if kind == "price":
        params["sym"] = ident
        rows = db.execute(
            text(f"""
            SELECT p.date, p.close AS value FROM prices_daily p
            JOIN instrument_identifiers ii ON p.instrument_id = ii.instrument_id
            WHERE ii.scheme = 'YAHOO' AND ii.value = :sym{dfilt}
            ORDER BY p.date
        """),
            params,
        ).fetchall()
    elif kind == "bond":
        params["sym"] = ident
        rows = db.execute(
            text(f"""
            SELECT b.date, b.yield AS value FROM bond_yields b
            JOIN instrument_identifiers ii ON b.instrument_id = ii.instrument_id
            WHERE ii.scheme = 'YAHOO' AND ii.value = :sym{dfilt}
            ORDER BY b.date
        """),
            params,
        ).fetchall()
    elif kind == "fx":
        ccf, cct = ident.split("/", 1)
        params.update(cf=ccf, ct=cct)
        rows = db.execute(
            text(f"""
            SELECT date, rate AS value FROM fx_rates_daily
            WHERE ccy_from = :cf AND ccy_to = :ct{dfilt} ORDER BY date
        """),
            params,
        ).fetchall()
    elif kind == "macro":
        params["sid"] = ident
        rows = db.execute(
            text(f"""
            SELECT date, value FROM macro_observations
            WHERE series_id = :sid{dfilt} ORDER BY date
        """),
            params,
        ).fetchall()
    else:
        raise HTTPException(400, f"Unknown series type: {kind}")

    if not rows:
        return pd.Series(dtype=float)

    return pd.Series(
        [float(r.value) if r.value is not None else np.nan for r in rows],
        index=pd.to_datetime([r.date for r in rows]),
        dtype=float,
    )


def _get_name(sid: str, db: Session) -> str:
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
        return row.name if row else sid
    elif kind == "fx":
        return ident
    elif kind == "macro":
        row = db.execute(
            text("SELECT name FROM macro_series WHERE series_id = :sid"), {"sid": ident}
        ).fetchone()
        return row.name if row else sid
    return sid


@router.post("/compare", response_model=CompareResponse)
def compare_series(req: CompareRequest, db: Session = Depends(get_db)) -> CompareResponse:
    """Compare multiple series, optionally normalized to base 100."""
    if len(req.ids) < 2:
        raise HTTPException(400, "Need at least 2 series to compare")
    if len(req.ids) > 10:
        raise HTTPException(400, "Maximum 10 series per comparison")

    all_series: dict[str, pd.Series] = {}
    for sid in req.ids:
        all_series[sid] = _fetch_series_df(sid, db, req.start, req.end)

    # Align on common dates (outer join, forward-fill for normalize mode)
    df = pd.DataFrame(all_series)

    if req.normalize:
        df = df.ffill()
        for col in df.columns:
            first_valid = df[col].first_valid_index()
            if first_valid is not None and df[col].loc[first_valid] != 0:
                df[col] = df[col] / df[col].loc[first_valid] * 100.0

    dates = [d.date() for d in df.index]
    series_list: list[CompareSeries] = []
    for sid in req.ids:
        name = _get_name(sid, db)
        values = [float(v) if pd.notna(v) else None for v in df[sid].tolist()]
        series_list.append(CompareSeries(id=sid, name=name, dates=dates, values=values))

    return CompareResponse(series=series_list, dates=dates)


@router.post("/correlation", response_model=CorrelationResponse)
def correlation_matrix(
    req: CorrelationRequest, db: Session = Depends(get_db)
) -> CorrelationResponse:
    """Compute pairwise correlation matrix for selected series."""
    if len(req.ids) < 2:
        raise HTTPException(400, "Need at least 2 series for correlation")
    if len(req.ids) > 15:
        raise HTTPException(400, "Maximum 15 series per correlation")

    all_series: dict[str, pd.Series] = {}
    for sid in req.ids:
        all_series[sid] = _fetch_series_df(sid, db, req.start, req.end)

    # Inner join — only dates where ALL series have values
    df = pd.DataFrame(all_series).dropna()

    if df.empty or df.shape[1] < 2:
        raise HTTPException(400, "No overlapping data between series")

    corr = df.corr()

    labels = [_get_name(sid, db) for sid in req.ids]
    matrix = corr.values.tolist()

    return CorrelationResponse(matrix=matrix, labels=labels)
