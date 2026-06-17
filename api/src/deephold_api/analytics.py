"""Analytics: compute financial statistics from observations."""

from __future__ import annotations

import numpy as np
import pandas as pd

from deephold_api.schemas import SeriesStats


def compute_stats(dates: list, values: list) -> SeriesStats:
    """Compute CAGR, volatility, Sharpe, max drawdown from a time series."""
    if not dates or not values:
        return SeriesStats(count=0)

    s = pd.Series(values, index=pd.to_datetime(dates), dtype=float).dropna()
    if len(s) < 2:
        return SeriesStats(
            count=len(s),
            latest=float(s.iloc[-1]) if len(s) else None,
            first=float(s.iloc[0]) if len(s) else None,
            min=float(s.min()) if len(s) else None,
            max=float(s.max()) if len(s) else None,
            mean=float(s.mean()) if len(s) else None,
        )

    returns = s.pct_change().dropna()

    # CAGR
    years = (s.index[-1] - s.index[0]).days / 365.25
    if years > 0 and s.iloc[0] > 0 and s.iloc[-1] > 0:
        cagr = float((s.iloc[-1] / s.iloc[0]) ** (1.0 / years) - 1.0)
    else:
        cagr = None

    # Annualized volatility
    vol = float(returns.std() * np.sqrt(252)) if len(returns) > 1 else None

    # Sharpe ratio (risk-free = 0)
    sharpe: float | None = None
    if vol and vol > 0:
        annual_return = float(returns.mean() * 252)
        sharpe = annual_return / vol

    # Max drawdown
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_dd = float(drawdown.min())

    return SeriesStats(
        cagr=cagr,
        volatility=vol,
        sharpe=sharpe,
        max_drawdown=max_dd,
        latest=float(s.iloc[-1]),
        first=float(s.iloc[0]),
        min=float(s.min()),
        max=float(s.max()),
        mean=float(s.mean()),
        count=len(s),
    )


def compute_correlation_matrix(
    all_values: list[list[float | None]],
) -> list[list[float | None]]:
    """Compute pairwise correlation from aligned observations.

    Each inner list is one series. NaN/None values are filled forward.
    """
    df = pd.DataFrame(all_values).T.ffill()
    if df.empty or df.shape[1] < 2:
        return [[None] * len(all_values)] * len(all_values)

    corr = df.corr()
    return corr.values.tolist()
