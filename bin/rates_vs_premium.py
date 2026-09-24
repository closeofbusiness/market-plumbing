#!/usr/bin/env python3
"""
rates_vs_premium.py

Decompose the S&P 500 trailing earnings yield (E/P) into a 10-year real-yield
component and an implied equity-risk-premium (residual) component, and
attribute the CHANGE in that yield -- annually and across two windows
(2015-2019 and 2024-2026) -- to real yields vs. the premium.

Reads ONLY these three source files (read-only project folder, absolute paths):
  - .../data/vintages/shiller_2026-09-02/ie_data.xls      (Shiller: P, D, E, CAPE)
  - .../data/vintages/shiller_2026-09-02/FRED_DGS10.csv   (10y nominal Treasury, daily)
  - .../data/vintages/shiller_2026-09-02/FRED_DFII10.csv  (10y TIPS real yield, daily)

Also fetches (HTTP GET, declared non-commercial-research User-Agent, no API key)
two free public workbooks from Damodaran's NYU Stern page for an independent
forward-looking ERP cross-check, then deletes the raw downloads once parsed.

Writes ONLY into this scratch directory (absolute paths):
  - monthly_series.csv
  - decomposition_annual.csv
  - decomposition_windows.csv
  - damodaran_compare.csv

Method notes (read before trusting a number):

1. E/P is a TRAILING-earnings proxy (Shiller's reported trailing 12m E), not a
   forward-looking earnings yield. The "implied premium" here is therefore
   trailing E/P minus the 10-year TIPS real yield -- a backward-looking,
   accounting-based residual, not a model-based forward ERP. Section 4 (the
   Damodaran cross-check) is the forward-looking counterpoint.

2. The real yield is FRED DFII10 (market-priced 10y TIPS yield), monthly mean
   of available trading days. This is a REAL yield already (no inflation
   adjustment applied by us) -- DGS10 (nominal) is carried in monthly_series.csv
   only for context (and to report breakeven inflation = DGS10 - DFII10).

3. Because P/E = 1 / (E/P) is a NONLINEAR (reciprocal) function of the yield,
   splitting a change in P/E into a "rate part" and a "premium part" cannot be
   done by simple subtraction without leaving a cross term. We use the exact,
   symmetric two-path (Shapley) allocation for a two-factor function, which
   allocates 100% of the interaction term and sums EXACTLY to the true total
   change (no residual left over, no arbitrary order-of-operations bias):

       f(r, p) = 100 / (r + p)                    [P/E as a function of real yield r and premium p, both in %]
       path A: rate moves first (premium held at start), then premium moves (rate held at end)
       path B: premium moves first (rate held at start), then rate moves (premium held at end)
       rate_effect    = mean(path A's rate step,    path B's rate step)
       premium_effect = mean(path A's premium step, path B's premium step)
       rate_effect + premium_effect == f(r1,p1) - f(r0,p0)   EXACTLY

   In E/P space (percentage points of earnings yield) the split is trivial and
   exact because E/P = r + p by construction: delta(E/P) = delta(r) + delta(p).
"""

import math
import os
import urllib.request

import pandas as pd
import xlrd

# ---------------------------------------------------------------------------
# Absolute paths. Inputs are READ-ONLY. Outputs go only to this scratch dir.
# ---------------------------------------------------------------------------
PROJECT_DIR = "/Users/martinschroeder/Dropbox/31 - Claude Cowork/Work/2026.08 - Third Derivative Research"
SHILLER_XLS = os.path.join(PROJECT_DIR, "data/vintages/shiller_2026-09-02/ie_data.xls")
FRED_DGS10 = os.path.join(PROJECT_DIR, "data/vintages/shiller_2026-09-02/FRED_DGS10.csv")
FRED_DFII10 = os.path.join(PROJECT_DIR, "data/vintages/shiller_2026-09-02/FRED_DFII10.csv")

OUT_DIR = "/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave2/p2c"
OUT_MONTHLY = os.path.join(OUT_DIR, "monthly_series.csv")
OUT_ANNUAL = os.path.join(OUT_DIR, "decomposition_annual.csv")
OUT_WINDOWS = os.path.join(OUT_DIR, "decomposition_windows.csv")
OUT_DAMODARAN = os.path.join(OUT_DIR, "damodaran_compare.csv")

HTTP_UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"

SERIES_START = "2003-01"  # first month FRED DFII10 (10y TIPS) is available
SERIES_END = "2026-09"    # latest month present in the Shiller vintage

# The two focus windows, as point-in-time endpoint MONTHS (not annual averages).
# Chosen to match the prior step's own window definitions so the two pieces of
# work are comparable: decomp_annual.csv's 2015 row starts 2014-12; its 2019
# row ends 2019-12; its 2024 row starts 2023-12; and decomp_cumulative.csv's
# "2015-latest (through last month with reported E)" row ends 2026-06 (June
# 2026 is the last month with a non-blank Shiller trailing-E figure).
WINDOWS = {
    "2015-2019": ("2014-12", "2019-12"),
    "2024-2026": ("2023-12", "2026-06"),
}
# The "2015-2019 average" baseline used in the step-3 counterfactuals is the
# calendar-year span Jan2015-Dec2019 (60 months) -- deliberately NOT the same
# as WINDOWS["2015-2019"] above (which starts Dec-2014, for a clean Dec-to-Dec
# endpoint difference); see BASELINE_START/BASELINE_END below.
BASELINE_START = "2015-01"
BASELINE_END = "2019-12"


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
def load_shiller(path):
    """Parse Shiller's ie_data.xls 'Data' sheet into a monthly DataFrame.

    Column layout (0-indexed), confirmed by inspection of the header rows and
    by cross-checking known boundary months against data/p2a_decomposition/
    decomp_annual.csv (2014-12, 2019-12, 2023-12, 2026-06 P and E match to
    full float precision):
        0 Date (YYYY.MM, e.g. 2019.1 = Oct 2019 -- NOT Jan; parsed via rounding)
        1 P (S&P Comp price)      2 D (dividend)      3 E (trailing 12m earnings)
        12 CAPE (P/E10, cyclically adjusted P/E; 'NA' for the earliest history)
    """
    wb = xlrd.open_workbook(path)
    sh = wb.sheet_by_name("Data")
    rows = []
    for r in range(8, sh.nrows):  # data starts at row 8 (0-indexed); header rows 0-7
        vals = sh.row_values(r)
        date_raw = vals[0]
        if not isinstance(date_raw, float):
            continue  # trailing footnote row (non-numeric first cell)
        year = int(math.floor(date_raw + 1e-9))
        month = int(round((date_raw - year) * 100))
        if month < 1 or month > 12:
            continue
        def numify(x):
            return float(x) if isinstance(x, (int, float)) else float("nan")
        rows.append({
            "year": year, "month": month,
            "P": numify(vals[1]), "D": numify(vals[2]), "E": numify(vals[3]),
            "CPI": numify(vals[4]),
            "CAPE": numify(vals[12]),
        })
    df = pd.DataFrame(rows)
    df["ym"] = pd.PeriodIndex.from_fields(year=df["year"], month=df["month"], freq="M")
    df = df.set_index("ym").sort_index()
    return df[["P", "D", "E", "CPI", "CAPE"]]


def load_fred_monthly(path, col):
    """Load a FRED daily CSV (observation_date, <col>) and return the monthly mean."""
    df = pd.read_csv(path)
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df["val"] = pd.to_numeric(df[col], errors="coerce")
    df["ym"] = df["observation_date"].dt.to_period("M")
    monthly = df.dropna(subset=["val"]).groupby("ym")["val"].mean()
    monthly.name = col
    counts = df.dropna(subset=["val"]).groupby("ym")["val"].size()
    counts.name = col + "_n_days"
    return monthly, counts


# ---------------------------------------------------------------------------
# Exact two-path (Shapley) decomposition of a change in P/E = 100/(r+p)
# ---------------------------------------------------------------------------
def shapley_pe_decompose(r0, p0, r1, p1):
    f = lambda r, p: 100.0 / (r + p)
    f00, f10, f01, f11 = f(r0, p0), f(r1, p0), f(r0, p1), f(r1, p1)
    dR_pathA = f10 - f00          # rate moves first, premium at start
    dP_pathA = f11 - f10          # then premium moves, rate at end
    dP_pathB = f01 - f00          # premium moves first, rate at start
    dR_pathB = f11 - f01          # then rate moves, premium at end
    rate_effect = (dR_pathA + dR_pathB) / 2.0
    premium_effect = (dP_pathA + dP_pathB) / 2.0
    total = f11 - f00
    resid = total - (rate_effect + premium_effect)
    assert abs(resid) < 1e-8, f"Shapley split failed to reconcile: resid={resid}"
    return {
        "PE_start": f00, "PE_end": f11,
        "pe_effect_rate": rate_effect, "pe_effect_premium": premium_effect,
        "pe_total_change": total,
    }


def build_row(label, start_ym, end_ym, r, p, ep, measure):
    r0, r1 = r[start_ym], r[end_ym]
    p0, p1 = p[start_ym], p[end_ym]
    ep0, ep1 = ep[start_ym], ep[end_ym]
    if any(pd.isna(x) for x in (r0, r1, p0, p1, ep0, ep1)):
        return None
    dec = shapley_pe_decompose(r0, p0, r1, p1)
    pe_start = dec["PE_start"]
    row = {
        "label": label, "measure": measure,
        "start": str(start_ym), "end": str(end_ym),
        "real_yield_start_pct": r0, "real_yield_end_pct": r1, "real_yield_change_pp": r1 - r0,
        "premium_start_pct": p0, "premium_end_pct": p1, "premium_change_pp": p1 - p0,
        "EP_start_pct": ep0, "EP_end_pct": ep1, "EP_change_pp": ep1 - ep0,
        "EP_change_check_pp": (r1 - r0) + (p1 - p0),  # must equal EP_change_pp exactly
        "PE_start": pe_start, "PE_end": dec["PE_end"], "PE_change": dec["pe_total_change"],
        "pe_effect_rate_pts": dec["pe_effect_rate"],
        "pe_effect_premium_pts": dec["pe_effect_premium"],
        "pct_of_start_value_from_rate": 100.0 * dec["pe_effect_rate"] / pe_start,
        "pct_of_start_value_from_premium": 100.0 * dec["pe_effect_premium"] / pe_start,
    }
    return row


def fetch_url(url, local_path):
    req = urllib.request.Request(url, headers={"User-Agent": HTTP_UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
        status = resp.status
    print(f"  fetch attempt: {url} -> HTTP {status}, {len(data)} bytes")
    if status != 200 or len(data) < 1000:
        raise RuntimeError(f"HTTP {status}, {len(data)} bytes (too small)")
    with open(local_path, "wb") as fh:
        fh.write(data)
    return local_path


def fetch_damodaran_annual():
    """Damodaran's long-history ANNUAL implied ERP workbook (free, public, NYU Stern).

    'Implied ERP (FCFE)' is his headline forward-looking number: a 3-stage
    FCFE/dividend-discount model using current cash yield (dividends +
    buybacks) and analyst consensus growth estimates, solved for the discount
    rate that equates model value to the current index level, minus his own
    T.Bond (NOMINAL 10y Treasury) rate. That is a fundamentally different
    construct from our trailing E/P-minus-REAL-yield residual (see notes in
    parse step below) -- both get reported, not blended.
    """
    candidates = [
        "https://pages.stern.nyu.edu/~adamodar/pc/datasets/histimpl.xls",
        "https://www.stern.nyu.edu/~adamodar/pc/datasets/histimpl.xls",
    ]
    last_err = None
    for url in candidates:
        local_path = os.path.join(OUT_DIR, "_damodaran_annual.xls")
        try:
            fetch_url(url, local_path)
            return local_path, url, None
        except Exception as e:
            print(f"  fetch attempt: {url} -> FAILED: {e!r}")
            last_err = repr(e)
    return None, None, last_err


def fetch_damodaran_monthly():
    """Damodaran's MONTHLY-updated implied ERP workbook (free, public, NYU Stern).
    Used only to get a reading more current than the annual file's last full year.
    """
    candidates = [
        "https://pages.stern.nyu.edu/~adamodar/pc/implprem/ERPbymonth.xlsx",
    ]
    last_err = None
    for url in candidates:
        local_path = os.path.join(OUT_DIR, "_damodaran_monthly.xlsx")
        try:
            fetch_url(url, local_path)
            return local_path, url, None
        except Exception as e:
            print(f"  fetch attempt: {url} -> FAILED: {e!r}")
            last_err = repr(e)
    return None, None, last_err


def main():
    print("=" * 70)
    print("Loading Shiller monthly data:", SHILLER_XLS)
    shiller = load_shiller(SHILLER_XLS)
    print(f"  {len(shiller)} months, {shiller.index.min()} to {shiller.index.max()}")

    print("Loading FRED DFII10 (10y TIPS real yield):", FRED_DFII10)
    dfii10, dfii10_n = load_fred_monthly(FRED_DFII10, "DFII10")
    print(f"  {len(dfii10)} months, {dfii10.index.min()} to {dfii10.index.max()}")

    print("Loading FRED DGS10 (10y nominal Treasury):", FRED_DGS10)
    dgs10, dgs10_n = load_fred_monthly(FRED_DGS10, "DGS10")
    print(f"  {len(dgs10)} months, {dgs10.index.min()} to {dgs10.index.max()}")

    full_index = pd.period_range(SERIES_START, SERIES_END, freq="M")
    df = pd.DataFrame(index=full_index)
    df = df.join(shiller).join(dfii10).join(dgs10).join(dfii10_n).join(dgs10_n)
    df.index.name = "year_month"

    # --- Core yield series ---
    df["EP_trailing_pct"] = 100.0 * df["E"] / df["P"]
    df["PE_trailing"] = df["P"] / df["E"]
    df["CAPE_yield_pct"] = 100.0 / df["CAPE"]
    df["real_yield_pct"] = df["DFII10"]
    df["nominal_yield_pct"] = df["DGS10"]
    df["breakeven_inflation_pct"] = df["DGS10"] - df["DFII10"]
    df["premium_trailing_pct"] = df["EP_trailing_pct"] - df["real_yield_pct"]
    df["premium_cape_pct"] = df["CAPE_yield_pct"] - df["real_yield_pct"]

    monthly_out = df.reset_index()
    monthly_out["year_month"] = monthly_out["year_month"].astype(str)
    col_order = [
        "year_month", "P", "D", "E", "CAPE",
        "EP_trailing_pct", "PE_trailing", "CAPE_yield_pct",
        "real_yield_pct", "DFII10_n_days", "nominal_yield_pct", "DGS10_n_days",
        "breakeven_inflation_pct", "premium_trailing_pct", "premium_cape_pct",
    ]
    monthly_out[col_order].to_csv(OUT_MONTHLY, index=False)
    print(f"\nWrote {OUT_MONTHLY} ({len(monthly_out)} rows)")

    # Sanity cross-check against the prior step's own point-in-time figures
    print("\nCross-check against data/p2a_decomposition/decomp_annual.csv boundary months:")
    for ym in ["2014-12", "2019-12", "2023-12", "2026-06"]:
        p = pd.Period(ym, freq="M")
        print(f"  {ym}: P={df.loc[p,'P']:.4f} E={df.loc[p,'E']:.4f} "
              f"PE={df.loc[p,'PE_trailing']:.4f} EP%={df.loc[p,'EP_trailing_pct']:.4f} "
              f"real_yield%={df.loc[p,'real_yield_pct']:.4f} premium%={df.loc[p,'premium_trailing_pct']:.4f}")

    # -----------------------------------------------------------------
    # Annual decomposition (Dec->Dec, point-in-time; 2026 row is a stub
    # Dec2025->Jun2026 since June 2026 is the last month with reported E)
    # -----------------------------------------------------------------
    years = list(range(2004, 2026))
    annual_rows = []
    r_series = df["real_yield_pct"]
    p_trail = df["premium_trailing_pct"]
    ep_trail = df["EP_trailing_pct"]
    p_cape = df["premium_cape_pct"]
    ep_cape = df["CAPE_yield_pct"]

    for y in years:
        start_ym = pd.Period(f"{y-1}-12", freq="M")
        end_ym = pd.Period(f"{y}-12", freq="M")
        row = build_row(str(y), start_ym, end_ym, r_series, p_trail, ep_trail, "trailing_E")
        if row:
            annual_rows.append(row)
        row_cape = build_row(str(y), start_ym, end_ym, r_series, p_cape, ep_cape, "CAPE_E10")
        if row_cape:
            annual_rows.append(row_cape)
    # 2026 stub (Dec 2025 -> Jun 2026, last month with reported trailing E)
    start_ym, end_ym = pd.Period("2025-12", freq="M"), pd.Period("2026-06", freq="M")
    row = build_row("2026_YTD(Jan-Jun)", start_ym, end_ym, r_series, p_trail, ep_trail, "trailing_E")
    if row:
        annual_rows.append(row)
    row_cape = build_row("2026_YTD(Jan-Jun)", start_ym, end_ym, r_series, p_cape, ep_cape, "CAPE_E10")
    if row_cape:
        annual_rows.append(row_cape)

    annual_df = pd.DataFrame(annual_rows)
    annual_df.to_csv(OUT_ANNUAL, index=False)
    print(f"\nWrote {OUT_ANNUAL} ({len(annual_df)} rows)")

    # -----------------------------------------------------------------
    # Window decomposition (2015-2019, 2024-2026), trailing E and CAPE E10
    # -----------------------------------------------------------------
    window_rows = []
    for label, (s, e) in WINDOWS.items():
        s_ym, e_ym = pd.Period(s, freq="M"), pd.Period(e, freq="M")
        window_rows.append(build_row(label, s_ym, e_ym, r_series, p_trail, ep_trail, "trailing_E"))
        window_rows.append(build_row(label, s_ym, e_ym, r_series, p_cape, ep_cape, "CAPE_E10"))

    # Baseline averages over the 2015-2019 window (Jan2015-Dec2019, 60 months)
    base_s = pd.Period(BASELINE_START, freq="M")
    base_e = pd.Period(BASELINE_END, freq="M")
    base_mask = (df.index >= base_s) & (df.index <= base_e)
    avg_real_yield_1519 = df.loc[base_mask, "real_yield_pct"].mean()
    avg_premium_1519_trail = df.loc[base_mask, "premium_trailing_pct"].mean()
    avg_premium_1519_cape = df.loc[base_mask, "premium_cape_pct"].mean()
    print(f"\n2015-2019 monthly-average baseline (Jan2015-Dec2019, n={base_mask.sum()} months):")
    print(f"  avg real yield = {avg_real_yield_1519:.4f}%")
    print(f"  avg premium (trailing E) = {avg_premium_1519_trail:.4f}%")
    print(f"  avg premium (CAPE E10)   = {avg_premium_1519_cape:.4f}%")

    # Step 3 counterfactuals, evaluated at EACH window's end
    cf_rows = []
    for label, (s, e) in WINDOWS.items():
        e_ym = pd.Period(e, freq="M")
        for measure, prem_series, ep_series, avg_prem in [
            ("trailing_E", p_trail, ep_trail, avg_premium_1519_trail),
            ("CAPE_E10", p_cape, ep_cape, avg_premium_1519_cape),
        ]:
            r_actual = r_series[e_ym]
            prem_actual = prem_series[e_ym]
            ep_actual = ep_series[e_ym]
            pe_actual = 100.0 / ep_actual
            # (a) actual real yield, premium held at 2015-2019 average
            ep_cf_a = r_actual + avg_prem
            pe_cf_a = 100.0 / ep_cf_a
            # (b) actual premium, real yield held at 2015-2019 average
            ep_cf_b = avg_real_yield_1519 + prem_actual
            pe_cf_b = 100.0 / ep_cf_b
            cf_rows.append({
                "window": label, "measure": measure, "end_month": str(e_ym),
                "real_yield_actual_pct": r_actual, "premium_actual_pct": prem_actual,
                "EP_actual_pct": ep_actual, "PE_actual": pe_actual,
                "avg_real_yield_2015_2019_pct": avg_real_yield_1519,
                "avg_premium_2015_2019_pct": avg_prem,
                "cfA_desc": "actual real yield + 2015-2019 avg premium",
                "EP_cfA_pct": ep_cf_a, "PE_cfA": pe_cf_a,
                "gap_A_pe_pts": pe_actual - pe_cf_a,
                "gap_A_pct_of_actual_level": 100.0 * (pe_actual - pe_cf_a) / pe_actual,
                "cfB_desc": "2015-2019 avg real yield + actual premium",
                "EP_cfB_pct": ep_cf_b, "PE_cfB": pe_cf_b,
                "gap_B_pe_pts": pe_actual - pe_cf_b,
                "gap_B_pct_of_actual_level": 100.0 * (pe_actual - pe_cf_b) / pe_actual,
            })
    cf_df = pd.DataFrame(cf_rows)

    windows_df = pd.DataFrame([r for r in window_rows if r])
    # Merge the counterfactual block on as extra columns keyed by (label/measure)
    windows_df = windows_df.merge(
        cf_df, left_on=["label", "measure"], right_on=["window", "measure"], how="left"
    )
    windows_df.to_csv(OUT_WINDOWS, index=False)
    print(f"\nWrote {OUT_WINDOWS} ({len(windows_df)} rows)")
    print("\nWindow decomposition summary:")
    for _, row in windows_df.iterrows():
        print(f"  [{row['label']} | {row['measure']}] EP {row['EP_start_pct']:.3f}% -> {row['EP_end_pct']:.3f}% "
              f"(rate {row['real_yield_change_pp']:+.3f}pp, premium {row['premium_change_pp']:+.3f}pp); "
              f"PE {row['PE_start']:.2f} -> {row['PE_end']:.2f} "
              f"(rate effect {row['pe_effect_rate_pts']:+.2f}, premium effect {row['pe_effect_premium_pts']:+.2f}); "
              f"actual PE {row['PE_actual']:.2f} vs cfA(baseline premium) {row['PE_cfA']:.2f} "
              f"[{row['gap_A_pct_of_actual_level']:+.1f}% of level] vs cfB(baseline rate) {row['PE_cfB']:.2f} "
              f"[{row['gap_B_pct_of_actual_level']:+.1f}% of level]")

    # -----------------------------------------------------------------
    # Damodaran cross-check (independent, free, forward-looking implied ERP)
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print("Attempting Damodaran implied ERP fetch (free, public, NYU Stern)...")
    annual_path, annual_url, annual_err = fetch_damodaran_annual()
    monthly_path, monthly_url, monthly_err = fetch_damodaran_monthly()

    damo_records = []
    raw_files_to_clean = []

    if annual_path is None:
        print(f"  ANNUAL FILE COULD NOT BE FETCHED: {annual_err}")
        damo_records.append({"label": "FETCH_FAILED_ANNUAL", "detail": str(annual_err)})
    else:
        raw_files_to_clean.append(annual_path)
        try:
            axls = pd.ExcelFile(annual_path, engine="xlrd")
            adf = axls.parse("Historical Impl Premiums", header=None)
            header = adf.iloc[6]
            adata = adf.iloc[7:].copy()
            adata.columns = header
            adata["Year"] = pd.to_numeric(adata["Year"], errors="coerce")
            adata = adata.dropna(subset=["Year"]).set_index("Year")
            adata.index = adata.index.astype(int)
            print(f"  parsed annual file: {annual_path} ({annual_url}), years "
                  f"{adata.index.min()}-{adata.index.max()}")

            for y, our_ym in [(2015, "2015-12"), (2019, "2019-12"), (2023, "2023-12"), (2025, "2025-12")]:
                p = pd.Period(our_ym, freq="M")
                our_real = df.loc[p, "real_yield_pct"]
                our_ep = df.loc[p, "EP_trailing_pct"]
                our_prem = df.loc[p, "premium_trailing_pct"]
                our_breakeven = df.loc[p, "breakeven_inflation_pct"]
                arow = adata.loc[y]
                damo_erp = float(arow["Implied ERP (FCFE)"]) * 100.0
                damo_tbond = float(arow["T.Bond Rate"]) * 100.0
                damo_erp_realbasis = damo_erp + our_breakeven
                damo_records.append({
                    "label": f"{y} (Dec, annual)",
                    "our_month": our_ym, "damodaran_period": f"{y} (year-end)",
                    "our_real_yield_pct": our_real, "our_EP_trailing_pct": our_ep,
                    "our_trailing_premium_pct": our_prem,
                    "damodaran_tbond_nominal_pct": damo_tbond,
                    "damodaran_implied_erp_pct_nominal_basis": damo_erp,
                    "our_breakeven_inflation_pct": our_breakeven,
                    "damodaran_erp_pct_restated_on_real_rate_basis": damo_erp_realbasis,
                    "gap_raw_pp_ours_minus_damodaran_nominal_basis": our_prem - damo_erp,
                    "gap_pp_ours_minus_damodaran_realbasis": our_prem - damo_erp_realbasis,
                    "note": "raw gap compares different constructs (nominal forward DDM ERP vs real "
                            "trailing accounting residual); realbasis gap adds Damodaran's own T.Bond-DFII10 "
                            "breakeven back to his ERP so both are expressed over the same real risk-free rate",
                })
        except Exception as e:
            print(f"  FAILED TO PARSE ANNUAL FILE: {e!r}")
            damo_records.append({"label": "PARSE_FAILED_ANNUAL", "detail": repr(e)})

    if monthly_path is None:
        print(f"  MONTHLY FILE COULD NOT BE FETCHED: {monthly_err}")
        damo_records.append({"label": "FETCH_FAILED_MONTHLY", "detail": str(monthly_err)})
    else:
        raw_files_to_clean.append(monthly_path)
        try:
            mxls = pd.ExcelFile(monthly_path)
            mdf = mxls.parse("Historical ERP", header=None)
            mheader = mdf.iloc[0]
            mdata = mdf.iloc[1:].copy()
            mdata.columns = mheader
            mdata["Start of month"] = pd.to_datetime(mdata["Start of month"])
            mdata = mdata.dropna(subset=["Start of month"]).set_index("Start of month").sort_index()
            latest_date = mdata.index.max()
            latest = mdata.loc[latest_date]
            print(f"  parsed monthly file: {monthly_path} ({monthly_url}), "
                  f"latest row dated {latest_date.date()} (label convention: this date's row reflects "
                  f"pricing/cash-flow data as of approximately the END of the PRIOR month)")

            # Cross-check: the monthly file's "ERP (T12m)" one row after a given
            # December should equal that December's annual "Implied ERP (FCFE)"
            # (confirmed for Jan-2026 == 2025 annual figure, 0.0423 both ways).
            latest_erp = float(latest["ERP (T12m)"]) * 100.0
            latest_tbond = float(latest["T.Bond Rate"]) * 100.0

            # Pair against OUR latest computable month (2026-06, last month with
            # reported trailing E). Also build a flat-E approximation so the two
            # sides can be compared as of the SAME month as Damodaran's latest
            # (labelled clearly as an approximation, not a reported figure).
            our_latest_actual_ym = "2026-06"
            p_actual = pd.Period(our_latest_actual_ym, freq="M")
            our_real_actual = df.loc[p_actual, "real_yield_pct"]
            our_prem_actual = df.loc[p_actual, "premium_trailing_pct"]
            our_breakeven_actual = df.loc[p_actual, "breakeven_inflation_pct"]

            damo_month_str = str(latest_date.date())[:7]
            p_damo_month = pd.Period(damo_month_str, freq="M")
            e_flat = df.loc[p_actual, "E"]  # last reported trailing E, held flat
            p_at_damo_month = df.loc[p_damo_month, "P"] if p_damo_month in df.index else float("nan")
            real_at_damo_month = df.loc[p_damo_month, "real_yield_pct"] if p_damo_month in df.index else float("nan")
            breakeven_at_damo_month = df.loc[p_damo_month, "breakeven_inflation_pct"] if p_damo_month in df.index else float("nan")
            ep_flatE_approx = 100.0 * e_flat / p_at_damo_month if pd.notna(p_at_damo_month) else float("nan")
            prem_flatE_approx = ep_flatE_approx - real_at_damo_month if pd.notna(real_at_damo_month) else float("nan")
            damo_erp_realbasis_latest = latest_erp + breakeven_at_damo_month if pd.notna(breakeven_at_damo_month) else float("nan")

            damo_records.append({
                "label": "latest available (monthly)",
                "our_month": our_latest_actual_ym, "damodaran_period": f"{damo_month_str} (start-of-month; reflects ~prior month-end)",
                "our_real_yield_pct": our_real_actual, "our_EP_trailing_pct": df.loc[p_actual, "EP_trailing_pct"],
                "our_trailing_premium_pct": our_prem_actual,
                "damodaran_tbond_nominal_pct": latest_tbond,
                "damodaran_implied_erp_pct_nominal_basis": latest_erp,
                "our_breakeven_inflation_pct": our_breakeven_actual,
                "damodaran_erp_pct_restated_on_real_rate_basis": latest_erp + our_breakeven_actual,
                "gap_raw_pp_ours_minus_damodaran_nominal_basis": our_prem_actual - latest_erp,
                "gap_pp_ours_minus_damodaran_realbasis": our_prem_actual - (latest_erp + our_breakeven_actual),
                "note": f"MONTH MISMATCH: our figure is {our_latest_actual_ym} (last month with reported "
                        f"trailing E); Damodaran's latest is dated {damo_month_str}. Approx. same-month "
                        f"comparison using {our_latest_actual_ym}'s trailing E held flat and {damo_month_str}'s "
                        f"actual price/real yield: our_EP_flatE_approx={ep_flatE_approx:.4f}%, "
                        f"our_premium_flatE_approx={prem_flatE_approx:.4f}%, "
                        f"gap_flatE_approx_pp={prem_flatE_approx-latest_erp:.4f} (nominal-basis Damodaran), "
                        f"{prem_flatE_approx-damo_erp_realbasis_latest:.4f} (real-basis Damodaran)",
            })
        except Exception as e:
            print(f"  FAILED TO PARSE MONTHLY FILE: {e!r}")
            damo_records.append({"label": "PARSE_FAILED_MONTHLY", "detail": repr(e)})

    damo_df = pd.DataFrame(damo_records)
    damo_df.to_csv(OUT_DAMODARAN, index=False)
    print(f"\nWrote {OUT_DAMODARAN} ({len(damo_df)} rows)")
    print("\nDamodaran comparison summary:")
    for _, row in damo_df.iterrows():
        if "gap_raw_pp_ours_minus_damodaran_nominal_basis" in row and pd.notna(row.get("gap_raw_pp_ours_minus_damodaran_nominal_basis")):
            print(f"  [{row['label']}] our_premium={row['our_trailing_premium_pct']:.3f}% "
                  f"damodaran_ERP(nominal)={row['damodaran_implied_erp_pct_nominal_basis']:.3f}% "
                  f"damodaran_ERP(realbasis)={row['damodaran_erp_pct_restated_on_real_rate_basis']:.3f}% "
                  f"gap_raw={row['gap_raw_pp_ours_minus_damodaran_nominal_basis']:+.3f}pp "
                  f"gap_realbasis={row['gap_pp_ours_minus_damodaran_realbasis']:+.3f}pp")
        else:
            print(f"  [{row['label']}]: {row.get('detail')}")

    # Clean up temp raw downloads -- deliverables are the 5 named files only.
    for f in raw_files_to_clean:
        try:
            os.remove(f)
        except OSError:
            pass

    print("\nDone.")


if __name__ == "__main__":
    main()
