"""End-to-end demo: decompose a price move using only free data.

Pulls daily prices for an asset from Yahoo Finance, splits the move into price
and income (carry) channels, prints a summary, and writes a contribution chart.

Usage
-----
    python examples/decompose_demo.py                 # SPY, last ~6 months
    python examples/decompose_demo.py --ticker QQQ --start 2024-01-01
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

# Allow running as a plain script (`python examples/decompose_demo.py`) by
# putting the repo root on the path before importing the local package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib

matplotlib.use("Agg")  # headless-safe backend for Cloud Agents / CI
import matplotlib.pyplot as plt

from marketplumbing import decompose_total_return, summarize_decomposition
from marketplumbing.data import fetch_prices


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", default="SPY", help="Yahoo Finance symbol")
    default_start = (date.today() - timedelta(days=182)).isoformat()
    parser.add_argument("--start", default=default_start, help="ISO start date")
    parser.add_argument("--end", default=None, help="ISO end date (default: today)")
    parser.add_argument(
        "--out",
        default="output/decomposition.png",
        help="Path for the contribution chart",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print(f"Fetching {args.ticker} from Yahoo Finance ({args.start} -> {args.end or 'today'}) ...")
    prices = fetch_prices(args.ticker, start=args.start, end=args.end)
    print(f"  got {len(prices)} observations: {prices.index[0].date()} -> {prices.index[-1].date()}")

    decomp = decompose_total_return(prices)
    summary = summarize_decomposition(decomp)

    print("\nPrice-move decomposition")
    print("------------------------")
    print(f"  total return       : {summary['total_return']:+.2%}")
    print(f"  price contribution : {summary['price_contribution']:+.2%}")
    print(f"  income contribution: {summary['income_contribution']:+.2%}")
    print(f"  price share of |move|: {summary['price_share']:.1%}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(decomp.index, decomp["cum_total_return"], label="total", linewidth=2)
    ax.plot(decomp.index, decomp["cum_price_return"], label="price", linestyle="--")
    ax.plot(decomp.index, decomp["cum_income_return"], label="income", linestyle=":")
    ax.axhline(0.0, color="black", linewidth=0.6)
    ax.set_title(f"{args.ticker}: cumulative return decomposition")
    ax.set_ylabel("cumulative return")
    ax.legend()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    print(f"\nWrote chart -> {out_path}")


if __name__ == "__main__":
    main()
