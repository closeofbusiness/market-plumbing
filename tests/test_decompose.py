"""Deterministic unit tests for the return decomposition (no network)."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from marketplumbing import decompose_total_return, summarize_decomposition


def _dates(n: int) -> pd.DatetimeIndex:
    return pd.date_range("2024-01-01", periods=n, freq="D")


def test_price_only_return_matches_simple_return():
    prices = pd.Series([100.0, 110.0, 99.0], index=_dates(3))
    decomp = decompose_total_return(prices)

    assert list(decomp["price_return"].round(6)) == [0.1, -0.1]
    # No income supplied -> income channel is exactly zero.
    assert (decomp["income_return"] == 0.0).all()
    assert list(decomp["total_return"].round(6)) == [0.1, -0.1]


def test_income_adds_to_total_return():
    prices = pd.Series([100.0, 100.0], index=_dates(2))
    income = pd.Series([0.0, 2.0], index=_dates(2))  # $2 coupon over the period
    decomp = decompose_total_return(prices, income=income)

    row = decomp.iloc[0]
    assert row["price_return"] == pytest.approx(0.0)
    assert row["income_return"] == pytest.approx(0.02)
    assert row["total_return"] == pytest.approx(0.02)


def test_channels_sum_to_cumulative_total():
    prices = pd.Series([100.0, 105.0, 103.0, 108.0], index=_dates(4))
    income = pd.Series([0.0, 1.0, 0.0, 1.0], index=_dates(4))
    decomp = decompose_total_return(prices, income=income)

    last = decomp.iloc[-1]
    reconstructed = last["cum_price_return"] + last["cum_income_return"]
    assert reconstructed == pytest.approx(last["cum_total_return"], rel=1e-9)


def test_cumulative_total_matches_compounded_return():
    prices = pd.Series([50.0, 55.0, 60.5], index=_dates(3))  # +10% each step
    decomp = decompose_total_return(prices)
    expected = 1.1 * 1.1 - 1.0
    assert decomp.iloc[-1]["cum_total_return"] == pytest.approx(expected)


def test_summary_shares_are_consistent():
    prices = pd.Series([100.0, 110.0, 121.0], index=_dates(3))
    decomp = decompose_total_return(prices)
    summary = summarize_decomposition(decomp)

    assert summary["price_share"] == pytest.approx(1.0)
    assert summary["income_share"] == pytest.approx(0.0)
    assert math.isclose(
        summary["price_contribution"] + summary["income_contribution"],
        summary["total_return"],
        rel_tol=1e-9,
    )


def test_requires_two_prices():
    with pytest.raises(ValueError):
        decompose_total_return(pd.Series([100.0], index=_dates(1)))


def test_rejects_non_positive_prices():
    with pytest.raises(ValueError):
        decompose_total_return(pd.Series([100.0, 0.0], index=_dates(2)))
