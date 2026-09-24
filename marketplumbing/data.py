"""Thin free-data access layer.

Only free, public sources are used. Yahoo Finance (via ``yfinance``) covers
equities, ETFs, FX, rate proxies, and commodities; FRED (via
``pandas_datareader``) covers macro and rates series. Both are best-effort and
require network access — keep them out of unit tests and use them from demos
and research scripts instead.
"""

from __future__ import annotations

import pandas as pd

__all__ = ["fetch_prices", "fetch_dividends", "fetch_fred_series"]


def fetch_prices(
    ticker: str,
    start: str,
    end: str | None = None,
    *,
    field: str = "Close",
) -> pd.Series:
    """Fetch a single price series from Yahoo Finance.

    Parameters
    ----------
    ticker:
        Yahoo symbol, e.g. ``"SPY"``, ``"^TNX"`` (10y yield x10), ``"CL=F"``.
    start, end:
        ISO date strings. ``end`` defaults to today when omitted.
    field:
        Which OHLCV column to return. Defaults to ``"Close"``.

    Returns
    -------
    pandas.Series
        The requested field indexed by date, named ``ticker``.
    """
    import yfinance as yf

    frame = yf.download(
        ticker, start=start, end=end, progress=False, auto_adjust=False
    )
    if frame is None or frame.empty:
        raise RuntimeError(f"no data returned for {ticker!r} in [{start}, {end}]")

    # yfinance returns a column MultiIndex (field, ticker) for single tickers.
    if isinstance(frame.columns, pd.MultiIndex):
        series = frame[field].iloc[:, 0]
    else:
        series = frame[field]

    series = series.dropna()
    series.name = ticker
    return series


def fetch_dividends(ticker: str, start: str, end: str | None = None) -> pd.Series:
    """Fetch per-share cash dividends (the income/carry channel) from Yahoo.

    Returns a date-indexed series of dividend amounts on their ex-dates,
    clipped to ``[start, end]``. May be empty for non-dividend payers.
    """
    import yfinance as yf

    dividends = yf.Ticker(ticker).dividends
    if dividends is None or dividends.empty:
        return pd.Series(dtype="float64", name=f"{ticker}_dividends")

    # yfinance returns a tz-aware index; normalize to naive dates for alignment.
    dividends = dividends.copy()
    dividends.index = dividends.index.tz_localize(None).normalize()
    mask = dividends.index >= pd.Timestamp(start)
    if end is not None:
        mask &= dividends.index <= pd.Timestamp(end)
    dividends = dividends[mask]
    dividends.name = f"{ticker}_dividends"
    return dividends


def fetch_fred_series(series_id: str, start: str, end: str | None = None) -> pd.Series:
    """Fetch a single series from FRED (Federal Reserve Economic Data)."""
    from pandas_datareader import data as pdr

    frame = pdr.DataReader(series_id, "fred", start, end)
    series = frame[series_id].dropna()
    series.name = series_id
    return series
