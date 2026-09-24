"""Decompose an asset's total return into price and income (carry) components.

The identity used is the standard holding-period return:

    total_return_t = price_return_t + income_return_t

where, for a price series ``P`` and per-period income ``I`` (coupons,
dividends, or accrued carry) paid over the period ending at ``t``:

    price_return_t  = P_t / P_{t-1} - 1
    income_return_t = I_t / P_{t-1}

Keeping the two channels separate is the first step of every market-plumbing
update: a move driven by carry is a very different story from a move driven by
a repricing of the asset itself.
"""

from __future__ import annotations

import pandas as pd

__all__ = ["decompose_total_return", "summarize_decomposition"]


def decompose_total_return(
    prices: pd.Series,
    income: pd.Series | None = None,
) -> pd.DataFrame:
    """Decompose per-period total return into price and income contributions.

    Parameters
    ----------
    prices:
        Price level series indexed by date (ascending). Must contain at least
        two observations.
    income:
        Optional per-period income paid over the period *ending* on each date
        (e.g. dividends or coupons), aligned to ``prices``. Missing values are
        treated as zero. When omitted, income return is zero everywhere.

    Returns
    -------
    pandas.DataFrame
        One row per period (the first observation is dropped because a return
        needs a prior price) with columns:
        ``price_return``, ``income_return``, ``total_return``,
        and their cumulative counterparts
        ``cum_price_return``, ``cum_income_return``, ``cum_total_return``.

    Raises
    ------
    ValueError
        If fewer than two prices are supplied or any price is non-positive.
    """
    prices = pd.Series(prices).astype("float64")
    if prices.shape[0] < 2:
        raise ValueError("need at least two prices to compute a return")
    if (prices <= 0).any():
        raise ValueError("prices must be strictly positive")

    if income is None:
        income = pd.Series(0.0, index=prices.index)
    else:
        income = pd.Series(income).reindex(prices.index).fillna(0.0).astype("float64")

    prev = prices.shift(1)
    price_return = prices / prev - 1.0
    income_return = income / prev
    total_return = price_return + income_return

    out = pd.DataFrame(
        {
            "price_return": price_return,
            "income_return": income_return,
            "total_return": total_return,
        }
    ).iloc[1:]

    # Cumulative price/income contributions are additive within the compounded
    # total so the two channels always sum back to the total wealth relative.
    out["cum_total_return"] = (1.0 + out["total_return"]).cumprod() - 1.0
    weight = (1.0 + out["total_return"]).cumprod().shift(1).fillna(1.0)
    out["cum_price_return"] = (out["price_return"] * weight).cumsum()
    out["cum_income_return"] = (out["income_return"] * weight).cumsum()
    return out


def summarize_decomposition(decomposition: pd.DataFrame) -> dict[str, float]:
    """Reduce a decomposition frame to headline totals.

    Returns a mapping with the cumulative total return and the share of that
    move attributable to price versus income over the whole window.
    """
    if decomposition.empty:
        raise ValueError("decomposition is empty")

    last = decomposition.iloc[-1]
    total = float(last["cum_total_return"])
    price = float(last["cum_price_return"])
    income = float(last["cum_income_return"])

    denom = abs(price) + abs(income)
    price_share = float(abs(price) / denom) if denom else 0.0
    return {
        "total_return": total,
        "price_contribution": price,
        "income_contribution": income,
        "price_share": price_share,
        "income_share": 1.0 - price_share if denom else 0.0,
    }
