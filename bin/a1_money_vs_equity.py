#!/usr/bin/env python3
"""
A1 — money creation vs household equity net purchases.

Goal (from the task brief): test, roughly, whether newly created bank money has any
relationship to the household equity buying that the Z.1 accounts cannot otherwise
attribute (the "household residual").

Inputs (all already on disk, not re-downloaded):
  data/a1_money_creation/Bank_credit_all_commercial_banks.csv   (H.8, B1001NCBA, weekly, $mn, ASSET line)
  data/a1_money_creation/Deposits_all_commercial_banks.csv      (H.8, B1058NCBA, weekly, $mn)
  data/a1_money_creation/SOMA_US_Treasury_held_outright.csv     (H.4.1, weekly, $mn)
  data/a1_money_creation/SOMA_MBS_held_outright.csv             (H.4.1, weekly, $mn)
  data/z1_equity_netbuyers/netbuyers_quarterly_2026Q2.csv       (Z.1, quarterly, $bn, FLOW already)

Method:
  1. Weekly levels -> quarter-end levels (last weekly obs on or before the calendar quarter end).
  2. Quarter-end levels -> quarterly CHANGES (flows), converted $mn -> $bn (divide by 1000).
  3. Household equity net purchases: taken directly from the Z.1 file's flow_bn column for
     sector="Households and nonprofit organizations", role="holder" -- already a quarterly flow
     in $bn, no differencing needed, no re-derivation of the residual identity.
  4. Merge on quarter, compute Pearson correlation + OLS slope/intercept/R^2 for each money
     variable against household equity net purchases, for the full sample and for pre/post-2020
     (and a bonus pre-2020-vs-post-2021 cut that drops 2020-21 to see if the relationship survives).
  5. Scale comparison: cumulative deposit growth vs cumulative household equity net purchases
     over matching windows -- an upper bound, not a causal test.

Outputs -> data/a1_analysis/:
  a1_quarterly_series.csv          the merged quarterly panel, every column unit-labelled
  a1_correlations_slopes.csv       correlation/slope/R^2 per (variable x sample period)
  a1_scale_comparison.csv          cumulative-flow scale comparison

No new data is downloaded. No causal claim is made anywhere in this script's output.
"""
import csv
import math
import statistics
from datetime import date, datetime
from pathlib import Path

BASE = Path("/Users/martinschroeder/Dropbox/31 - Claude Cowork/Work/2026.08 - Third Derivative Research")
MONEY_DIR = BASE / "data" / "a1_money_creation"
EQUITY_FILE = BASE / "data" / "z1_equity_netbuyers" / "netbuyers_quarterly_2026Q2.csv"
OUT_DIR = BASE / "data" / "a1_analysis"

H8_H41_URL_NOTE = "as pulled into the local CSV; original releases: https://www.federalreserve.gov/releases/h8/ (H.8) and https://www.federalreserve.gov/releases/h41/ (H.4.1)"
Z1_URL_NOTE = "https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip (Z.1 Financial Accounts, series FU153064105.Q, sector='Households and nonprofit organizations', role=holder), via local file data/z1_equity_netbuyers/netbuyers_quarterly_2026Q2.csv"

QUARTER_END_MONTH_DAY = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}


def quarter_end_date(qlabel: str) -> date:
    """'2015:Q1' -> date(2015,3,31)"""
    y, q = qlabel.split(":Q")
    y = int(y)
    q = int(q)
    m, d = QUARTER_END_MONTH_DAY[q]
    return date(y, m, d)


def load_weekly(path: Path):
    """Return list of (date, value) sorted ascending, plus the unit and source_url seen."""
    rows = []
    unit = None
    src = None
    with open(path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            d = datetime.strptime(row["date"], "%Y-%m-%d").date()
            v = float(row["value"])
            rows.append((d, v))
            unit = row.get("unit", unit)
            src = row.get("source_url", src)
    rows.sort(key=lambda t: t[0])
    return rows, unit, src


def quarter_end_level(weekly_rows, qend: date):
    """Last observation on or before qend. None if qend is before the series starts."""
    best = None
    for d, v in weekly_rows:
        if d <= qend:
            best = (d, v)
        else:
            break
    return best  # (obs_date, value) or None


def pearson_and_ols(xs, ys):
    """Return (r, slope, intercept, r2, n) for paired (x,y), dropping any pair with a NaN."""
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None and not (isinstance(x, float) and math.isnan(x)) and not (isinstance(y, float) and math.isnan(y))]
    n = len(pairs)
    if n < 3:
        return None, None, None, None, n
    xs_ = [p[0] for p in pairs]
    ys_ = [p[1] for p in pairs]
    mx = sum(xs_) / n
    my = sum(ys_) / n
    sxx = sum((x - mx) ** 2 for x in xs_)
    syy = sum((y - my) ** 2 for y in ys_)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs_, ys_))
    if sxx == 0 or syy == 0:
        return None, None, None, None, n
    r = sxy / math.sqrt(sxx * syy)
    slope = sxy / sxx
    intercept = my - slope * mx
    r2 = r * r
    return r, slope, intercept, r2, n


def approx_p_value(r, n):
    """Rough two-sided significance gut-check only -- NOT an exact Student-t p-value (no
    scipy on this machine). Uses the standard r-to-t transform, t = r*sqrt(n-2)/sqrt(1-r^2),
    then a NORMAL approximation to the t-distribution's tail (stdlib statistics.NormalDist).
    At n=19-45 (df=17-43) this understates the true t-tail slightly, so treat the result as
    indicative only -- consistent with this task's 'rough understanding' standard, not a
    formal significance test."""
    if r is None or n is None or n < 4:
        return None
    if abs(r) >= 1:
        return 0.0
    t = r * math.sqrt(n - 2) / math.sqrt(1 - r * r)
    p = 2 * (1 - statistics.NormalDist().cdf(abs(t)))
    return p


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- 1. Load weekly money series --------------------------------------------------
    bank_credit_w, bc_unit, bc_src = load_weekly(MONEY_DIR / "Bank_credit_all_commercial_banks.csv")
    deposits_w, dep_unit, dep_src = load_weekly(MONEY_DIR / "Deposits_all_commercial_banks.csv")
    soma_ust_w, ust_unit, ust_src = load_weekly(MONEY_DIR / "SOMA_US_Treasury_held_outright.csv")
    soma_mbs_w, mbs_unit, mbs_src = load_weekly(MONEY_DIR / "SOMA_MBS_held_outright.csv")

    assert bc_unit == "Millions of Dollars"
    assert dep_unit == "Millions of Dollars"
    assert ust_unit == "Millions of Dollars"
    assert mbs_unit == "Millions of Dollars"

    # ---- 2. Load quarterly household equity net purchases (already a FLOW, in $bn) ----
    equity_rows = []
    with open(EQUITY_FILE, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if row["sector"] == "Households and nonprofit organizations" and row["role"] == "holder":
                equity_rows.append(row)
    equity_rows.sort(key=lambda row: row["quarter"])
    quarters = [row["quarter"] for row in equity_rows]
    hh_equity_flow_bn = {row["quarter"]: float(row["flow_bn"]) for row in equity_rows}
    hh_equity_level_bn = {row["quarter"]: float(row["level_bn"]) for row in equity_rows}
    hh_series_code = equity_rows[0]["series_code"] if equity_rows else None

    print(f"Household equity holder-flow rows loaded: {len(equity_rows)}; quarters {quarters[0]} to {quarters[-1]}; series_code={hh_series_code}")

    # ---- 3. Weekly -> quarter-end levels, for every quarter in the equity file --------
    qend_dates = {q: quarter_end_date(q) for q in quarters}

    bc_level_mn = {}
    dep_level_mn = {}
    ust_level_mn = {}
    mbs_level_mn = {}
    bc_obsdate = {}
    dep_obsdate = {}
    ust_obsdate = {}
    mbs_obsdate = {}

    for q in quarters:
        qend = qend_dates[q]
        bc = quarter_end_level(bank_credit_w, qend)
        dp = quarter_end_level(deposits_w, qend)
        us = quarter_end_level(soma_ust_w, qend)
        mb = quarter_end_level(soma_mbs_w, qend)
        bc_level_mn[q], bc_obsdate[q] = (bc[1], bc[0]) if bc else (None, None)
        dep_level_mn[q], dep_obsdate[q] = (dp[1], dp[0]) if dp else (None, None)
        ust_level_mn[q], ust_obsdate[q] = (us[1], us[0]) if us else (None, None)
        mbs_level_mn[q], mbs_obsdate[q] = (mb[1], mb[0]) if mb else (None, None)

    # ---- 4. Quarter-end levels -> quarterly CHANGES (flows), $mn -> $bn ---------------
    def qchange_bn(level_mn_dict, q, q_prev):
        if q_prev is None:
            return None
        v1 = level_mn_dict.get(q_prev)
        v2 = level_mn_dict.get(q)
        if v1 is None or v2 is None:
            return None
        return (v2 - v1) / 1000.0  # $mn -> $bn

    prev_q = {quarters[i]: (quarters[i - 1] if i > 0 else None) for i in range(len(quarters))}

    bc_change_bn = {q: qchange_bn(bc_level_mn, q, prev_q[q]) for q in quarters}
    dep_change_bn = {q: qchange_bn(dep_level_mn, q, prev_q[q]) for q in quarters}
    ust_change_bn = {q: qchange_bn(ust_level_mn, q, prev_q[q]) for q in quarters}
    mbs_change_bn = {q: qchange_bn(mbs_level_mn, q, prev_q[q]) for q in quarters}
    soma_total_change_bn = {
        q: (ust_change_bn[q] + mbs_change_bn[q]) if (ust_change_bn[q] is not None and mbs_change_bn[q] is not None) else None
        for q in quarters
    }

    # ---- 5. Write the merged quarterly panel ------------------------------------------
    panel_path = OUT_DIR / "a1_quarterly_series.csv"
    with open(panel_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "quarter", "quarter_end_calendar_date",
            "deposits_obs_date", "deposits_level_usd_mn", "deposits_qchange_usd_bn",
            "bank_credit_obs_date", "bank_credit_level_usd_mn", "bank_credit_qchange_usd_bn",
            "soma_ust_obs_date", "soma_ust_level_usd_mn", "soma_ust_qchange_usd_bn",
            "soma_mbs_obs_date", "soma_mbs_level_usd_mn", "soma_mbs_qchange_usd_bn",
            "soma_total_qchange_usd_bn",
            "household_equity_netbuy_usd_bn_FLOW", "household_equity_level_usd_bn_STOCK",
            "period_bucket",
            "source_note",
        ])
        for q in quarters:
            y = int(q.split(":Q")[0])
            if y < 2020:
                bucket = "pre-2020 (2015:Q1-2019:Q4)"
            elif y in (2020, 2021):
                bucket = "2020-2021 (pandemic)"
            else:
                bucket = "post-2021 (2022:Q1-2026:Q2)"
            w.writerow([
                q, qend_dates[q].isoformat(),
                dep_obsdate[q].isoformat() if dep_obsdate[q] else "",
                dep_level_mn[q], dep_change_bn[q],
                bc_obsdate[q].isoformat() if bc_obsdate[q] else "",
                bc_level_mn[q], bc_change_bn[q],
                ust_obsdate[q].isoformat() if ust_obsdate[q] else "",
                ust_level_mn[q], ust_change_bn[q],
                mbs_obsdate[q].isoformat() if mbs_obsdate[q] else "",
                mbs_level_mn[q], mbs_change_bn[q],
                soma_total_change_bn[q],
                hh_equity_flow_bn[q], hh_equity_level_bn[q],
                bucket,
                "money series: quarter-end level = last H.8/H.4.1 weekly obs on/before calendar quarter end, "
                "$mn source converted to $bn (divide 1000), then quarter-on-quarter differenced to a FLOW; "
                "household equity column is FU153064105.Q flow_bn taken as-is from Z.1 (already a quarterly FLOW, $bn), source: " + Z1_URL_NOTE,
            ])
    print(f"Wrote {panel_path}")

    # ---- 6. Correlations + slopes, by sample period -----------------------------------
    def rows_for_period(q_list):
        x = {
            "deposits_qchange_usd_bn": [dep_change_bn[q] for q in q_list],
            "bank_credit_qchange_usd_bn": [bc_change_bn[q] for q in q_list],
            "soma_ust_qchange_usd_bn": [ust_change_bn[q] for q in q_list],
            "soma_mbs_qchange_usd_bn": [mbs_change_bn[q] for q in q_list],
            "soma_total_qchange_usd_bn": [soma_total_change_bn[q] for q in q_list],
        }
        y = [hh_equity_flow_bn[q] for q in q_list]
        return x, y

    periods = {
        "full_sample_2015Q2-2026Q2": [q for q in quarters if dep_change_bn[q] is not None],
        "pre_2020_2015Q2-2019Q4": [q for q in quarters if dep_change_bn[q] is not None and int(q.split(":Q")[0]) < 2020],
        "2020on_2020Q1-2026Q2": [q for q in quarters if dep_change_bn[q] is not None and int(q.split(":Q")[0]) >= 2020],
        "excl_2020_2021_pre+post": [q for q in quarters if dep_change_bn[q] is not None and int(q.split(":Q")[0]) not in (2020, 2021)],
        "pandemic_only_2020Q1-2021Q4": [q for q in quarters if dep_change_bn[q] is not None and int(q.split(":Q")[0]) in (2020, 2021)],
    }

    corr_path = OUT_DIR / "a1_correlations_slopes.csv"
    with open(corr_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "money_variable", "sample_period", "n_quarters", "quarter_range",
            "pearson_r", "r_squared", "slope_hh_equity_bn_per_bn_of_x", "intercept_bn",
            "approx_p_value_normal_approx", "units", "interpretation", "notes",
        ])
        for period_name, qlist in periods.items():
            if not qlist:
                continue
            qrange = f"{qlist[0]}..{qlist[-1]}"
            x_dict, y = rows_for_period(qlist)
            for varname, xs in x_dict.items():
                r, slope, intercept, r2, n = pearson_and_ols(xs, y)
                if r is None:
                    w.writerow([varname, period_name, n, qrange, "", "", "", "", "", "$bn quarterly flow vs $bn quarterly flow", "insufficient variation or n<3", ""])
                    continue
                p = approx_p_value(r, n)
                interp = f"{slope*100:.1f} cents of household equity net-buying per $1 of {varname.replace('_qchange_usd_bn','').replace('_',' ')} quarterly change" if slope is not None else ""
                w.writerow([
                    varname, period_name, n, qrange,
                    round(r, 4), round(r2, 4), round(slope, 4), round(intercept, 2),
                    round(p, 4) if p is not None else "",
                    "$bn quarterly flow (X) vs $bn quarterly flow (Y=household equity net purchases)",
                    interp,
                    "association only -- see brief's direction-problem caveat; not a causal estimate. "
                    "p-value is a NORMAL-approximation gut-check (no scipy on this machine), not an exact Student-t test -- indicative only.",
                ])
    print(f"Wrote {corr_path}")

    # ---- 7. Scale comparison: cumulative deposit growth vs cumulative HH equity buying
    def cumulative_window(q_list_all, q_start, q_end):
        idx = [i for i, q in enumerate(q_list_all) if q_start <= q <= q_end]
        return [q_list_all[i] for i in idx]

    def level_growth(level_dict, q_base, q_last):
        """Stock delta from the level at the END of q_base to the level at the END of q_last.
        q_base must be the quarter BEFORE the first flow-quarter being summed, so that this
        delta spans exactly the same real-time window as the sum of quarterly flows does."""
        v0 = level_dict.get(q_base)
        v1 = level_dict.get(q_last)
        if v0 is None or v1 is None:
            return None
        return (v1 - v0) / 1000.0  # $mn -> $bn

    # Each window is defined by its FLOW quarters [q_start, q_end] (inclusive) -- the same
    # quarters summed on the household-equity side. The matching STOCK delta must therefore
    # run from the level at the end of the quarter BEFORE q_start (q_base) to the level at
    # the end of q_end -- NOT from the level at q_start itself, which would drop q_start's
    # own quarter of change and understate growth by one quarter. full_2015Q2-2026Q2 starts
    # one quarter later than the equity data (2015:Q1) allows, because computing 2015:Q1's own
    # deposit change would require a 2014:Q4 level we do not have on disk.
    windows = [
        ("full_2015Q2-2026Q2", "2015:Q2", "2026:Q2"),
        ("since_2020_2020Q1-2026Q2", "2020:Q1", "2026:Q2"),
        ("HR_window_2024Q1-2026Q2", "2024:Q1", "2026:Q2"),
    ]

    scale_path = OUT_DIR / "a1_scale_comparison.csv"
    with open(scale_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "window", "quarter_base_(level_start,_excl)", "quarter_start_(flow,_incl)", "quarter_end", "n_quarters_summed",
            "deposit_growth_usd_bn_STOCK_delta", "bank_credit_growth_usd_bn_STOCK_delta",
            "soma_ust_growth_usd_bn_STOCK_delta", "soma_mbs_growth_usd_bn_STOCK_delta",
            "cumulative_household_equity_netbuy_usd_bn_FLOW_sum",
            "ratio_deposit_growth_to_hh_equity_buying",
            "pct_of_deposit_growth_that_would_fund_all_hh_equity_buying",
            "notes",
        ])
        for wname, qs, qe in windows:
            qlist = cumulative_window(quarters, qs, qe)
            if not qlist:
                continue
            q_base = prev_q[qs]
            dep_growth = level_growth(dep_level_mn, q_base, qe)
            bc_growth = level_growth(bc_level_mn, q_base, qe)
            ust_growth = level_growth(ust_level_mn, q_base, qe)
            mbs_growth = level_growth(mbs_level_mn, q_base, qe)
            hh_sum = sum(hh_equity_flow_bn[q] for q in qlist)
            ratio = (dep_growth / hh_sum) if (dep_growth is not None and hh_sum) else None
            pct = (hh_sum / dep_growth * 100) if (dep_growth not in (None, 0) and hh_sum is not None) else None
            w.writerow([
                wname, q_base, qs, qe, len(qlist),
                round(dep_growth, 1) if dep_growth is not None else "",
                round(bc_growth, 1) if bc_growth is not None else "",
                round(ust_growth, 1) if ust_growth is not None else "",
                round(mbs_growth, 1) if mbs_growth is not None else "",
                round(hh_sum, 1),
                round(ratio, 2) if ratio is not None else "",
                round(pct, 1) if pct is not None else "",
                "STOCK deltas = quarter-end level(quarter_end) minus quarter-end level(quarter_base), $mn->$bn, "
                "so the delta spans exactly the quarter_start..quarter_end flow window; "
                "household figure = sum of quarterly FLOWs over quarter_start..quarter_end (matches Z.1 FU153064105.Q, "
                "e.g. HR window reproduces the +3,069.4bn figure in 2026-09-14-HR-The-Household-Residual.md exactly); "
                "this is a scale/upper-bound comparison only, proves nothing about direction -- see brief.",
            ])
    print(f"Wrote {scale_path}")

    print("\nDONE. All three CSVs written to", OUT_DIR)


if __name__ == "__main__":
    main()
