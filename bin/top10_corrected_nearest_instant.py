#!/usr/bin/env python3
"""
top10_corrected.py

Corrected-value-measure companion to top10.py, per supervisor direction
(2026-09-12): the original method applies ONE CY{Y}Q2I frame to the whole
universe, which structurally excludes any company whose fiscal Q2 does not
end in calendar Q2 -- confirmed in the single-frame run to exclude Apple and
Microsoft (and Costco/P&G/Visa/Oracle/Nike) from every single year's float
universe, even though several of them are routinely among the largest S&P
500 companies by value throughout 2015-2025.

METHOD (as specified by the supervisor): for each target year Y, fetch five
candidate dei:EntityPublicFloat instant frames --
    CY{Y-1}Q3I, CY{Y-1}Q4I, CY{Y}Q1I, CY{Y}Q2I, CY{Y}Q3I
-- spanning a full 12 months (quarter-end markers from ~Sep 30 Y-1 to ~Sep 30
Y). For each mapped company individually, use the ONE instant (across
whichever of these 5 frames contains that CIK) whose actual reported 'end'
date is closest in calendar days to 30 June of year Y. Record the lag (days
between the chosen instant and 30 June Y) and which of the 5 frames it came
from.

Everything else is unchanged from top10.py, reused directly (imported, not
reimplemented) so the compliance-sensitive code path is identical:
  - USER_AGENT_SEC (declared contact) sent to sec.gov hosts only; the
    no-email UA to every other host -- this script makes sec.gov calls only.
  - 1.0s minimum gap between sec.gov requests (enforced globally in top10.py).
  - Stops hard, no retry, on 403/429 from a sec.gov host.
  - Successful responses cached to disk; safe to split across separate
    foreground invocations.
  - Same $5T FLOAT_SANITY_MAX_USD bound, applied to whichever value is
    selected per company; values above it are excluded (treated as missing)
    and logged, same policy as the original run's float_outliers_excluded.csv
    (written here to a separate file so the two runs' logs don't conflate).
  - Same ticker->CIK mapping, same S&P 500 mid-year membership resolution,
    same NetIncomeLoss annual earnings frames (no new fetch needed), same
    "top 10 by float, same 10 CIKs used for both shares" construction.

Only the float VALUE (and hence which 10 CIKs rank top-10) changes.

USAGE (foreground, one stage at a time, same discipline as top10.py):
    python3 top10_corrected.py fetch-floats-multi --years 2015
    python3 top10_corrected.py fetch-floats-multi --years 2017
    ... (one year at a time recommended)
    python3 top10_corrected.py analyze-corrected   [--years ...]

Outputs (next to this script):
    top10_by_year_corrected.csv
    float_outliers_excluded_corrected.csv
"""

import argparse
import csv
import statistics
from datetime import date
from pathlib import Path

import top10 as base

HERE = Path(__file__).resolve().parent
CACHE_DIR = HERE / "cache"
OUT_DIR = HERE

# (year offset relative to target year Y, period) -> fixed column label.
CANDIDATE_OFFSETS = [(-1, "Q3I"), (-1, "Q4I"), (0, "Q1I"), (0, "Q2I"), (0, "Q3I")]
COL_LABELS = ["prevQ3", "prevQ4", "thisQ1", "thisQ2", "thisQ3"]


def candidates_for_year(y: int):
    return [(y + off, period) for off, period in CANDIDATE_OFFSETS]


def fetch_floats_multi(cache_dir: Path, years, force: bool = False):
    """Ensure all 5 candidate instant frames are cached for each year. Frames
    already cached from the original run (e.g. CY{Y}Q2I) are reused, not
    re-fetched."""
    for y in years:
        print(f"--- {y}: ensuring 5 candidate instant frames are cached ---")
        for (fy, period) in candidates_for_year(y):
            name = base.float_frame_cache_name(fy, period)
            was_cached = base.cache_path(cache_dir, name).exists() and not force
            data = base.fetch_json_cached(base.float_frame_url(fy, period), cache_dir, name, force=force)
            tag = "cache hit, no network call" if was_cached else "fetched from sec.gov"
            print(f"  CY{fy}{period}: {len(data.get('data', []))} filer records total ({tag})")


def _parse_date(s: str) -> date:
    y, m, d = (int(x) for x in s.split("-"))
    return date(y, m, d)


def nearest_instant(cik: int, frames_by_label: dict, target_date: date):
    """Across the 5 candidate frames, return (lag_days, val, end_str, label)
    for whichever has an entry for this CIK with 'end' date closest to
    target_date. None if the CIK appears in none of the 5."""
    best = None
    for label, cik_map in frames_by_label.items():
        entry = cik_map.get(cik)
        if entry is None or not entry.get("end"):
            continue
        end_d = _parse_date(entry["end"])
        lag = abs((end_d - target_date).days)
        if best is None or lag < best[0]:
            best = (lag, float(entry["val"]), entry["end"], label)
    return best


def analyze_year_corrected(cache_dir: Path, year: int, ticker_to_cik: dict, cik_to_title: dict,
                            sp500_rows, outlier_rows: list):
    mem = base.year_membership_ciks(year, ticker_to_cik, sp500_rows)
    cik_set = mem["cik_set"]
    n_unique_companies = mem["n_unique_companies_mapped"]
    target_date = date(year, 6, 30)

    frames_by_label = {}
    for (fy, period), label in zip(candidates_for_year(year), COL_LABELS):
        name = base.float_frame_cache_name(fy, period)
        frames_by_label[label] = base.frame_to_cik_map(base.load_json_cache_only(cache_dir, name))

    raw_selected = {}
    end_dates = {}
    lags = []
    source_counts = {lbl: 0 for lbl in COL_LABELS}
    for c in cik_set:
        r = nearest_instant(c, frames_by_label, target_date)
        if r is None:
            continue
        lag, val, end_str, label = r
        raw_selected[c] = val
        end_dates[c] = end_str
        lags.append(lag)
        source_counts[label] += 1

    float_outliers = {c: v for c, v in raw_selected.items() if v > base.FLOAT_SANITY_MAX_USD}
    float_vals = {c: v for c, v in raw_selected.items() if v <= base.FLOAT_SANITY_MAX_USD}
    for c, v in float_outliers.items():
        print(f"  EXCLUDED (data error, corrected method) {year}: CIK {c} {cik_to_title.get(c, '?')} "
              f"val={v:,.0f} USD (end={end_dates.get(c)}) -- exceeds sanity bound "
              f"{base.FLOAT_SANITY_MAX_USD:,.0f}.")
        outlier_rows.append({
            "year": year, "cik": c, "name": cik_to_title.get(c, "?"),
            "end_date": end_dates.get(c), "reported_float_usd": v,
            "sanity_bound_usd": base.FLOAT_SANITY_MAX_USD,
            "note": "excluded: exceeds sanity bound (corrected/nearest-instant method)",
        })

    n_with_float = len(float_vals)
    total_float = sum(float_vals.values())
    top10 = sorted(float_vals.items(), key=lambda kv: kv[1], reverse=True)[:10]
    if len(top10) < 10:
        print(f"  WARNING {year}: only {len(top10)} companies have (corrected) float data (< 10).")
    top10_ciks = [c for c, _ in top10]
    top10_float_sum = sum(v for _, v in top10)
    weight_share = (top10_float_sum / total_float) if total_float else None

    # ---- earnings: unchanged frames/values from the original run; only which
    # CIKs count as "top 10" can change, since that ranking is float-driven ----
    earn_map = base.frame_to_cik_map(base.load_json_cache_only(cache_dir, base.earnings_frame_cache_name(year)))
    earn_vals = {c: float(earn_map[c]["val"]) for c in cik_set if c in earn_map}
    n_with_earnings = len(earn_vals)
    total_earnings_all = sum(earn_vals.values())
    top10_earnings_all = sum(earn_vals.get(c, 0.0) for c in top10_ciks)
    earnings_share_all = (top10_earnings_all / total_earnings_all) if total_earnings_all else None
    total_earnings_pos = sum(v for v in earn_vals.values() if v > 0)
    top10_earnings_pos = sum(v for c in top10_ciks if (v := earn_vals.get(c, 0.0)) > 0)
    earnings_share_pos = (top10_earnings_pos / total_earnings_pos) if total_earnings_pos else None

    top10_names = "; ".join(f"{cik_to_title.get(c, '?')} (CIK {c})" for c in top10_ciks)

    apple_cik = ticker_to_cik.get("AAPL")
    msft_cik = ticker_to_cik.get("MSFT")

    def status(cik):
        if cik is None:
            return "TICKER_UNMAPPED"
        if cik in top10_ciks:
            return "in_universe_AND_top10"
        if cik in float_vals:
            return "in_universe_not_top10"
        if cik in float_outliers:
            return "in_universe_but_excluded_as_outlier"
        return "NOT_in_universe"

    apple_status = status(apple_cik)
    msft_status = status(msft_cik)
    apple_val = float_vals.get(apple_cik)
    msft_val = float_vals.get(msft_cik)
    print(f"  AAPL (CIK {apple_cik}): {apple_status}"
          + (f", val={apple_val:,.0f}, end={end_dates.get(apple_cik)}" if apple_val else ""))
    print(f"  MSFT (CIK {msft_cik}): {msft_status}"
          + (f", val={msft_val:,.0f}, end={end_dates.get(msft_cik)}" if msft_val else ""))

    return {
        "year": year,
        "target_date": target_date.isoformat(),
        "n_unique_companies_mapped": n_unique_companies,
        "n_with_float_corrected": n_with_float,
        "pct_float_coverage_of_mapped_corrected": (
            round(n_with_float / n_unique_companies, 4) if n_unique_companies else None
        ),
        "median_lag_days": round(statistics.median(lags), 1) if lags else None,
        "max_lag_days": max(lags) if lags else None,
        "n_from_prevQ3": source_counts["prevQ3"],
        "n_from_prevQ4": source_counts["prevQ4"],
        "n_from_thisQ1": source_counts["thisQ1"],
        "n_from_thisQ2": source_counts["thisQ2"],
        "n_from_thisQ3": source_counts["thisQ3"],
        "n_with_earnings": n_with_earnings,
        "pct_earnings_coverage_of_mapped": (
            round(n_with_earnings / n_unique_companies, 4) if n_unique_companies else None
        ),
        "top10_names_corrected": top10_names,
        "total_float_usd_corrected": total_float,
        "top10_float_usd_corrected": top10_float_sum,
        "weight_share_corrected": weight_share,
        "total_earnings_all_usd": total_earnings_all,
        "top10_earnings_all_usd": top10_earnings_all,
        "earnings_share_all_corrected": earnings_share_all,
        "total_earnings_positive_usd": total_earnings_pos,
        "top10_earnings_positive_usd": top10_earnings_pos,
        "earnings_share_positive_only_corrected": earnings_share_pos,
        "apple_status": apple_status,
        "msft_status": msft_status,
    }


def stage_analyze_corrected(cache_dir: Path, out_dir: Path, years):
    ticker_to_cik, cik_to_title = base.load_ticker_map(cache_dir)
    sp500_rows = base.load_sp500_history(cache_dir)
    outlier_rows = []
    results = []
    for y in years:
        print(f"Analyzing (corrected method) {y} ...")
        results.append(analyze_year_corrected(cache_dir, y, ticker_to_cik, cik_to_title, sp500_rows, outlier_rows))

    out_dir.mkdir(parents=True, exist_ok=True)

    out_csv = out_dir / "top10_by_year_corrected.csv"
    fieldnames = list(results[0].keys()) if results else []
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in results:
            w.writerow(r)
    print(f"Wrote {out_csv}")

    outliers_csv = out_dir / "float_outliers_excluded_corrected.csv"
    with outliers_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "year", "cik", "name", "end_date", "reported_float_usd", "sanity_bound_usd", "note",
        ])
        w.writeheader()
        for r in outlier_rows:
            w.writerow(r)
    print(f"Wrote {outliers_csv} ({len(outlier_rows)} float values excluded as data errors)")

    for r in results:
        print(r)


def parse_years(s: str):
    return [int(x) for x in s.split(",") if x.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["fetch-floats-multi", "analyze-corrected"])
    ap.add_argument("--years", default=",".join(str(y) for y in base.YEARS_DEFAULT))
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    years = parse_years(args.years)

    try:
        if args.stage == "fetch-floats-multi":
            fetch_floats_multi(CACHE_DIR, years, force=args.force)
        else:
            stage_analyze_corrected(CACHE_DIR, OUT_DIR, years)
    except base.SecBlocked as e:
        import sys
        print(f"\nSTOPPED (SEC rate/access block): {e}\n", file=sys.stderr)
        sys.exit(2)
    except base.FetchError as e:
        import sys
        print(f"\nSTOPPED (fetch error): {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
