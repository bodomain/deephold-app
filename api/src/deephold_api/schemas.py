"""Pydantic schemas for API request/response models."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class SeriesSummary(BaseModel):
    id: str
    type: str
    identifier: str
    name: str
    asset_class: str
    source: str | None = None
    currency: str | None = None
    unit: str | None = None
    frequency: str | None = None
    count: int = 0
    first_date: date | None = None
    last_date: date | None = None
    latest_value: float | None = None


class SeriesDetail(BaseModel):
    id: str
    type: str
    identifier: str
    name: str
    asset_class: str
    source: str | None = None
    currency: str | None = None
    unit: str | None = None
    frequency: str | None = None
    count: int = 0
    first_date: date | None = None
    last_date: date | None = None


class Observation(BaseModel):
    date: date
    value: float | None = None


class Candle(BaseModel):
    date: date
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: int | None = None


class SeriesStats(BaseModel):
    cagr: float | None = None
    volatility: float | None = None
    sharpe: float | None = None
    max_drawdown: float | None = None
    latest: float | None = None
    first: float | None = None
    min: float | None = None
    max: float | None = None
    mean: float | None = None
    count: int = 0


class CompareRequest(BaseModel):
    ids: list[str]
    normalize: bool = True
    start: date | None = None
    end: date | None = None


class CompareSeries(BaseModel):
    id: str
    name: str
    dates: list[date]
    values: list[float | None]


class CompareResponse(BaseModel):
    series: list[CompareSeries]
    dates: list[date]


class CorrelationRequest(BaseModel):
    ids: list[str]
    window: int | None = None
    start: date | None = None
    end: date | None = None


class CorrelationResponse(BaseModel):
    matrix: list[list[float | None]]
    labels: list[str]


class DashboardItem(BaseModel):
    id: str
    name: str
    latest_value: float | None = None
    latest_date: date | None = None
    change_pct: float | None = None
    sparkline: list[float] = []


class DashboardResponse(BaseModel):
    items: list[DashboardItem]
