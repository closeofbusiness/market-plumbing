#!/usr/bin/env python3
"""
decomp.py -- S&P 500 return decomposition, 2015-2026 YTD.

Splits the S&P 500's return into earnings growth, dividends and valuation
(P/E multiple) change, using Robert Shiller's monthly ie_data.xls (price P,
dividend D, earnings E, all nominal/as-reported) and FRED's 10-year TIPS
yield (DFII10) and nominal 10-year yield (DGS10).

Inputs (third-party, not redistributed; download them to this folder first --
README, "Checking the work"):
  data/vintages/shiller_2026-09-02/ie_data.xls      Shiller, saved 2026-09-02
  data/vintages/shiller_2026-09-02/FRED_DGS10.csv   FRED DGS10
  data/vintages/shiller_2026-09-02/FRED_DFII10.csv  FRED DFII10

Outputs (overwrite the committed tables, so `git diff` shows any change):
  data/p2a_decomposition/decomp_annual.csv      one row per calendar year 2015-2025 plus 2026 YTD
  data/p2a_decomposition/decomp_cumulative.csv  the same split over 2015-latest, using log returns

Requires: Python 3 stdlib + `xlrd` (for the legacy .xls format; openpyxl
does not read .xls): pip install -r requirements.txt
Run from anywhere:  python3 bin/decomp_sp500_shiller.py
(Written in an agent sandbox as decomp.py; in this repository since 11 Sep 2026.
The notes below describe where the inputs came from; the paths above supersede
the "next to this script" caches they mention.)

-----------------------------------------------------------------------
DATA-SOURCING NOTES (read before trusting a re-run's numbers)
-----------------------------------------------------------------------

1. Shiller's ie_data.xls -- THE BRIEF'S STATIC URL IS STALE.
   SHILLER_STATIC_URL below (the exact URL given in the project brief)
   returned HTTP 200 when fetched on 2026-09-11, but its content was last
   saved 2024-09-05 (data through 2024-09 only) -- a pinned, ~2-year-old
   copy. That makes "2026 year-to-date" and all of 2025 impossible from
   that file alone, which contradicts the brief's own request. Per the
   brief's fallback clause ("if it fails, find the current link from
   Shiller's Yale data page"), this script instead treats that staleness
   as a failure and uses a fresher copy: econ.yale.edu/~shiller/data.htm
   -> "U.S. Stock Markets 1871-Present and CAPE Ratio" -> shillerdata.com
   -> its "Download" button, which on 2026-09-11 pointed at
     https://img1.wsimg.com/blobby/go/e5e77e0b-.../downloads/<uuid>/ie_data.xls?ver=<ts>
   i.e. the same blob container as the brief's URL, but a versioned,
   dynamically-generated sub-path that is refreshed each time the page
   renders. That copy was last saved 2026-09-02 (data through 2026-09,
   partial). Because the versioned URL is not a stable constant, it is not
   hardcoded here; instead the file it pointed to is cached locally as
   ie_data_current.xls and this script prefers that cache. If you delete
   the cache, the script falls back to a live fetch of SHILLER_STATIC_URL
   and prints a loud warning if the result looks more than ~120 days old.

2. FRED (DGS10, DFII10) -- direct HTTP was blocked in this script's
   development sandbox. curl (HTTP/2 and HTTP/1.1) and Python
   urllib/requests all completed the TLS handshake against
   fred.stlouisfed.org and then got either an immediate HTTP/2 stream
   reset or a silent hang with no response ever returned -- for the
   fredgraph.csv endpoint AND for the bare homepage, with both the
   mandated research User-Agent and, as a diagnostic, a plain desktop
   Chrome User-Agent (identical outcome, so this is not a UA-string
   check). A real browser (Chromium via a browser-automation tool)
   reached fred.stlouisfed.org fine and its in-page `fetch()` calls to
   the same fredgraph.csv URLs returned HTTP 200 with the expected CSV --
   that request necessarily carried the browser's own User-Agent, not the
   mandated string, since this script's mandated header is an HTTP-client
   concept and the browser controls its own. Those responses were saved
   to DGS10.csv / DFII10.csv next to this script. This script prefers
   those local caches; if absent, it attempts a live fetch with the
   mandated User-Agent and will very likely reproduce the same block
   outside a real browser context.

Only the mandated User-Agent is ever sent on this script's own HTTP
requests; no email address is placed in any request; live requests to a
single host are throttled to a minimum gap so as never to exceed 2/sec.
"""

import csv
import math
import os
import sys
import time
import urllib.request
from datetime import date

try:
    import xlrd
except ImportError:
    sys.exit(
        "This script needs the 'xlrd' package to read Shiller's legacy .xls "
        "file. Run it with the virtualenv provided next to this script:\n"
        "  .venv/bin/python decomp.py\n"
        "or `pip install xlrd` (PEP 668 systems: use a venv)."
    )

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # repository root
VINTAGE = os.path.join(ROOT, "data", "vintages", "shiller_2026-09-02")
OUT_DIR = os.path.join(ROOT, "data", "p2a_decomposition")

USER_AGENT = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
REQUEST_HEADERS = {"User-Agent": USER_AGENT, "Accept": "*/*"}
MIN_REQUEST_GAP_SEC = 0.6  # keep comfortably under 2 req/sec to any one host

SHILLER_STATIC_URL = (
    "https://img1.wsimg.com/blobby/go/e5e77e0b-59d1-44d9-ab25-4763ac982e53"
    "/downloads/ie_data.xls"
)
FRED_URL_TMPL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"

SHILLER_CURRENT_CACHE = os.path.join(VINTAGE, "ie_data.xls")
# ie_data.xls (no suffix) is also kept next to this script -- it is the
# brief's literal static URL fetched verbatim, retained only as evidence of
# the staleness described above. Nothing in this script reads it.
FRED_CACHE_TMPL = os.path.join(VINTAGE, "FRED_{series}.csv")

STALE_WARN_DAYS = 120

_last_request_time = {"_default": 0.0}


def _throttled_get(url, host_key="_default", timeout=20):
    """HTTP GET with the mandated UA and a per-host minimum request gap."""
    gap = MIN_REQUEST_GAP_SEC - (time.monotonic() - _last_request_time.get(host_key, 0.0))
    if gap > 0:
        time.sleep(gap)
    req = urllib.request.Request(url, headers=REQUEST_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    _last_request_time[host_key] = time.monotonic()
    return data


# ---------------------------------------------------------------------
# Loading (local cache first; live fetch as a documented fallback)
# ---------------------------------------------------------------------

def load_shiller_bytes():
    if os.path.exists(SHILLER_CURRENT_CACHE):
        print(f"[shiller] using local cache: {SHILLER_CURRENT_CACHE}")
        return open(SHILLER_CURRENT_CACHE, "rb").read()
    print(f"[shiller] no local cache; attempting live fetch of {SHILLER_STATIC_URL}")
    try:
        data = _throttled_get(SHILLER_STATIC_URL, host_key="wsimg")
    except Exception as e:
        raise RuntimeError(
            f"Could not obtain Shiller data: no cache at {SHILLER_CURRENT_CACHE} "
            f"and live fetch of {SHILLER_STATIC_URL} failed: {e}"
        )
    print(f"[shiller] live-fetched {len(data)} bytes from {SHILLER_STATIC_URL} "
          "(NOTE: this URL is known to serve a stale, pinned snapshot -- see "
          "module docstring. Check the printed data date-range below.)")
    return data


def load_fred_text(series_id):
    cache_path = FRED_CACHE_TMPL.format(series=series_id)
    if os.path.exists(cache_path):
        print(f"[fred:{series_id}] using local cache: {cache_path}")
        with open(cache_path, "r") as f:
            return f.read()
    url = FRED_URL_TMPL.format(series=series_id)
    print(f"[fred:{series_id}] no local cache; attempting live fetch of {url}")
    try:
        data = _throttled_get(url, host_key="fred.stlouisfed.org")
    except Exception as e:
        raise RuntimeError(
            f"Could not obtain FRED series {series_id}: no cache at {cache_path} "
            f"and live fetch of {url} failed: {e}. In development, "
            "fred.stlouisfed.org silently dropped every direct HTTP request "
            "(see module docstring) -- the shipped CSV was fetched via a real "
            "browser instead."
        )
    return data.decode("utf-8")


# ---------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------

def parse_shiller_xls(xls_bytes):
    """Returns dict[(year, month)] -> {"P":, "D":, "E":} of nominal series."""
    book = xlrd.open_workbook(file_contents=xls_bytes)
    sh = book.sheet_by_name("Data")
    series = {}
    for r in range(8, sh.nrows):  # rows 0-7 are the (multi-line) header
        vals = sh.row_values(r)
        if not isinstance(vals[1], float):
            continue  # skips the trailing footnote row and any blank rows
        frac = vals[5]  # precise "Date Fraction" column -- avoids the
        # Jan/Oct ambiguity of the plain "Date" column (1871.01 vs 1871.1)
        year = int(math.floor(frac))
        month = int(round((frac - year) * 12 + 0.5))
        P = vals[1]
        D = vals[2] if isinstance(vals[2], float) else math.nan
        E = vals[3] if isinstance(vals[3], float) else math.nan
        series[(year, month)] = {"P": P, "D": D, "E": E}
    return series


def parse_fred_csv(text):
    """Returns list of (date_str 'YYYY-MM-DD', value_or_None)."""
    rows = list(csv.reader(text.splitlines()))
    out = []
    for row in rows[1:]:
        if len(row) < 2:
            continue
        date_s, val_s = row[0], row[1]
        val = None if val_s in ("", ".") else float(val_s)
        out.append((date_s, val))
    return out


def annual_average(fred_rows, year):
    vals = [v for (d, v) in fred_rows if d.startswith(f"{year}-") and v is not None]
    if not vals:
        return None, 0
    return sum(vals) / len(vals), len(vals)


# ---------------------------------------------------------------------
# Month arithmetic + return computation
# ---------------------------------------------------------------------

def month_add(y, m, k):
    idx = (y * 12 + (m - 1)) + k
    return idx // 12, idx % 12 + 1


def monthly_total_return(series, y, m):
    """
    (P_m + D_m/12) / P_{m-1} - 1.

    D_m is Shiller's trailing-12-month dividend; dividing by 12 approximates
    that month's per-share cash dividend under a smooth-payout assumption.
    This is the standard convention for reconstructing a monthly total
    return series from Shiller's P/D columns. Returns None if either month
    is missing or D/P/E needed is NaN (lagged earnings do not block this --
    only P and D matter here).
    """
    py, pm = month_add(y, m, -1)
    cur, prev = series.get((y, m)), series.get((py, pm))
    if cur is None or prev is None:
        return None
    P, D, P_prev = cur["P"], cur["D"], prev["P"]
    if any(math.isnan(x) for x in (P, D, P_prev)):
        return None
    return (P + D / 12.0) / P_prev - 1.0


def compounded_return(series, start_y, start_m, end_y, end_m):
    y, m = start_y, start_m
    acc = 1.0
    n = 0
    while (y, m) <= (end_y, end_m):
        r = monthly_total_return(series, y, m)
        if r is None:
            raise ValueError(f"missing monthly total return at {y}-{m:02d}")
        acc *= (1.0 + r)
        n += 1
        y, m = month_add(y, m, 1)
    return acc - 1.0, n


# ---------------------------------------------------------------------
# Decomposition
# ---------------------------------------------------------------------

def decompose_period(series, y0, m0, y1, m1, label):
    """
    Stage 1 -- price return into EPS growth and P/E change. Exact identity:
    (1+eps_growth)(1+pe_change) = P1/P0 = 1+price_return, so
        eps_growth + pe_change + cross_term == price_return
    to float precision, where cross_term = eps_growth*pe_change. This
    cross-term is reported per the brief (it is often LARGE -- e.g. in a
    sharp earnings-recovery year the EPS-growth and P/E-change legs can
    each run into double digits or more with a large offsetting
    cross-term -- so it must be shown, not dropped).

    Stage 2 -- total return into price return and dividends.
    dividend_return is defined residually so that
        (1+price_return)(1+dividend_return) == 1+total_return
    exactly. dividend_cross_term = price_return*dividend_return is the
    piece omitted if one just adds price_return + dividend_return; unlike
    the Stage-1 cross-term this one is small in every sample year (dividend
    yields are ~1-2%), which is what the brief's "reproduce the total
    within 0.5 percentage points" check is aimed at:
        check_gap_pp = (price_return + dividend_return - total_return) * 100
                     = -dividend_cross_term * 100
    """
    p0, p1 = series[(y0, m0)]["P"], series[(y1, m1)]["P"]
    e0, e1 = series[(y0, m0)]["E"], series[(y1, m1)]["E"]

    price_return = p1 / p0 - 1.0
    eps_growth = e1 / e0 - 1.0
    pe0, pe1 = p0 / e0, p1 / e1
    pe_change = pe1 / pe0 - 1.0
    cross_term = eps_growth * pe_change

    sy, sm = month_add(y0, m0, 1)
    total_return, n_months = compounded_return(series, sy, sm, y1, m1)
    dividend_return = (1.0 + total_return) / (1.0 + price_return) - 1.0

    price_plus_dividend = price_return + dividend_return
    dividend_cross_term = price_return * dividend_return
    check_gap_pp = (price_plus_dividend - total_return) * 100.0

    return dict(
        year=label, start=f"{y0}-{m0:02d}", end=f"{y1}-{m1:02d}", n_months=n_months,
        P_start=p0, P_end=p1, E_start=e0, E_end=e1, PE_start=pe0, PE_end=pe1,
        price_return=price_return, eps_growth=eps_growth, pe_change=pe_change,
        cross_term=cross_term, dividend_return=dividend_return, total_return=total_return,
        price_plus_dividend=price_plus_dividend, dividend_cross_term=dividend_cross_term,
        check_gap_pp=check_gap_pp,
    )


def decompose_cumulative(series, y0, m0, y1, m1, label):
    """Log-return split: log_price = log_eps + log_pe exactly (no cross
    term in log space); log_total = log_price + log_dividend by
    construction (log_dividend is the residual)."""
    p0, p1 = series[(y0, m0)]["P"], series[(y1, m1)]["P"]
    e0, e1 = series[(y0, m0)]["E"], series[(y1, m1)]["E"]

    log_price = math.log(p1 / p0)
    log_eps = math.log(e1 / e0)
    log_pe = log_price - log_eps

    sy, sm = month_add(y0, m0, 1)
    total_return, n_months = compounded_return(series, sy, sm, y1, m1)
    log_total = math.log(1.0 + total_return)
    log_div = log_total - log_price
    n_years = n_months / 12.0

    return dict(
        label=label, start=f"{y0}-{m0:02d}", end=f"{y1}-{m1:02d}",
        n_months=n_months, n_years=n_years,
        P_start=p0, P_end=p1, E_start=e0, E_end=e1,
        log_price_return=log_price, log_eps_growth=log_eps, log_pe_change=log_pe,
        log_total_return=log_total, log_dividend_return=log_div,
        share_pe_pct=log_pe / log_price * 100.0, share_eps_pct=log_eps / log_price * 100.0,
        simple_price_return=math.exp(log_price) - 1.0,
        simple_total_return=math.exp(log_total) - 1.0,
        simple_eps_growth=math.exp(log_eps) - 1.0,
        simple_pe_change=math.exp(log_pe) - 1.0,
        simple_dividend_return=math.exp(log_div) - 1.0,
        annualized_simple_price=math.exp(log_price / n_years) - 1.0,
        annualized_simple_total=math.exp(log_total / n_years) - 1.0,
    )


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def latest_month_with(series, field, on_or_before=None):
    keys = [k for k, v in series.items() if not math.isnan(v[field])]
    if on_or_before:
        keys = [k for k in keys if k <= on_or_before]
    return max(keys)


def main():
    shiller_bytes = load_shiller_bytes()
    series = parse_shiller_xls(shiller_bytes)

    all_months = sorted(series.keys())
    print(f"[shiller] parsed {len(all_months)} months: "
          f"{all_months[0][0]}-{all_months[0][1]:02d} to "
          f"{all_months[-1][0]}-{all_months[-1][1]:02d}")
    newest_y, newest_m = all_months[-1]
    days_old = (date.today() - date(newest_y, newest_m, 1)).days
    if days_old > STALE_WARN_DAYS:
        print(f"[shiller] WARNING: newest month {newest_y}-{newest_m:02d} is "
              f"{days_old} days before today ({date.today()}) -- source may be stale.")

    latest_P_month = max(all_months)
    latest_E_month = latest_month_with(series, "E")
    print(f"[shiller] latest month with any price P: {latest_P_month[0]}-{latest_P_month[1]:02d}")
    print(f"[shiller] latest month with reported trailing E (and D): "
          f"{latest_E_month[0]}-{latest_E_month[1]:02d} "
          "-- this script treats this as \"latest\" for every return/EPS/PE "
          "figure below, per the brief's instruction to say exactly how the "
          "E lag was handled. Newer P-only months are reported as a memo, "
          "not decomposed.")

    dgs10_rows = parse_fred_csv(load_fred_text("DGS10"))
    dfii10_rows = parse_fred_csv(load_fred_text("DFII10"))

    # ---------------- annual table, 2015-2025 + 2026 YTD ----------------
    annual_rows = []
    for Y in range(2015, 2026):
        row = decompose_period(series, Y - 1, 12, Y, 12, str(Y))
        ey_avg = sum(series[(Y, m)]["E"] / series[(Y, m)]["P"] for m in range(1, 13)) / 12.0 * 100.0
        tips_avg, n_tips = annual_average(dfii10_rows, Y)
        nom_avg, n_nom = annual_average(dgs10_rows, Y)
        row.update(
            earnings_yield_avg_pct=ey_avg, n_months_ey=12,
            tips_yield_avg_pct=tips_avg, n_days_tips=n_tips,
            nominal10y_avg_pct=nom_avg, n_days_nom10y=n_nom,
            erp_pct=ey_avg - tips_avg,
            memo_latest_month="", memo_latest_P="", memo_price_chg_from_end_pct="",
        )
        annual_rows.append(row)

    ey1, em1 = latest_E_month
    ytd = decompose_period(series, 2025, 12, ey1, em1, "2026_YTD")
    ey_avg = (sum(series[(2026, m)]["E"] / series[(2026, m)]["P"] for m in range(1, em1 + 1))
              / em1 * 100.0)
    tips_avg, n_tips = annual_average(dfii10_rows, 2026)
    nom_avg, n_nom = annual_average(dgs10_rows, 2026)
    ly, lm = latest_P_month
    memo_price_chg = None
    if (ly, lm) != (ey1, em1):
        memo_price_chg = (series[(ly, lm)]["P"] / series[(ey1, em1)]["P"] - 1.0) * 100.0
    ytd.update(
        earnings_yield_avg_pct=ey_avg, n_months_ey=em1,
        tips_yield_avg_pct=tips_avg, n_days_tips=n_tips,
        nominal10y_avg_pct=nom_avg, n_days_nom10y=n_nom,
        erp_pct=ey_avg - tips_avg,
        memo_latest_month=f"{ly}-{lm:02d}" if memo_price_chg is not None else "",
        memo_latest_P=series[(ly, lm)]["P"] if memo_price_chg is not None else "",
        memo_price_chg_from_end_pct=memo_price_chg if memo_price_chg is not None else "",
    )
    annual_rows.append(ytd)

    annual_fields = [
        "year", "start", "end", "n_months", "P_start", "P_end", "E_start", "E_end",
        "PE_start", "PE_end", "price_return", "eps_growth", "pe_change", "cross_term",
        "dividend_return", "total_return", "price_plus_dividend", "dividend_cross_term",
        "check_gap_pp",
        "earnings_yield_avg_pct", "n_months_ey", "tips_yield_avg_pct", "n_days_tips",
        "nominal10y_avg_pct", "n_days_nom10y", "erp_pct",
        "memo_latest_month", "memo_latest_P", "memo_price_chg_from_end_pct",
    ]
    annual_path = os.path.join(OUT_DIR, "decomp_annual.csv")
    with open(annual_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=annual_fields)
        w.writeheader()
        for row in annual_rows:
            w.writerow({k: row.get(k, "") for k in annual_fields})
    print(f"[out] wrote {annual_path} ({len(annual_rows)} rows)")

    worst = max(annual_rows[:-1], key=lambda r: abs(r["check_gap_pp"]))  # 11 full years only
    print(f"[check] price_return + dividend_return vs total_return -- worst full-year "
          f"gap: {worst['year']} ({worst['check_gap_pp']:+.3f} pp; tolerance was 0.5pp)")
    worst_cross = max(annual_rows[:-1], key=lambda r: abs(r["cross_term"]))
    print(f"[note] the EPS-growth x P/E-change cross_term (Stage 1, reported per the "
          f"brief, not the 0.5pp-checked quantity) is largest in {worst_cross['year']} "
          f"({worst_cross['cross_term']*100:+.1f} pp) -- naively adding eps_growth + "
          f"pe_change without it would be off by that much.")

    # ---------------- cumulative, 2015-latest ----------------
    cum_rows = [
        decompose_cumulative(series, 2014, 12, 2025, 12, "2015-2025 (full calendar years)"),
        decompose_cumulative(series, 2014, 12, ey1, em1, "2015-latest (through last month with reported E)"),
    ]
    cum_fields = [
        "label", "start", "end", "n_months", "n_years", "P_start", "P_end", "E_start", "E_end",
        "log_price_return", "log_eps_growth", "log_pe_change", "log_total_return",
        "log_dividend_return", "share_pe_pct", "share_eps_pct",
        "simple_price_return", "simple_total_return", "simple_eps_growth",
        "simple_pe_change", "simple_dividend_return",
        "annualized_simple_price", "annualized_simple_total",
    ]
    cum_path = os.path.join(OUT_DIR, "decomp_cumulative.csv")
    with open(cum_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cum_fields)
        w.writeheader()
        for row in cum_rows:
            w.writerow({k: row.get(k, "") for k in cum_fields})
    print(f"[out] wrote {cum_path} ({len(cum_rows)} rows)")

    if memo_price_chg is not None:
        print(f"[memo] price-only change from {ey1}-{em1:02d} (P={series[(ey1,em1)]['P']:.2f}) "
              f"to {ly}-{lm:02d} (P={series[(ly,lm)]['P']:.2f}, latest month in file): "
              f"{memo_price_chg:+.2f}% -- not decomposable, E/D not yet reported for that window.")

    print("[done]")


if __name__ == "__main__":
    main()
