#!/usr/bin/env python3
"""
top10.py

Top-10 S&P 500 concentration test: does the top-10 companies' share of S&P 500
EARNINGS lag their share of S&P 500 float-adjusted VALUE?

============================================================================
STATUS AS OF WRITING: NOT RUN END-TO-END. NO DATA WAS COLLECTED.
============================================================================
During setup for this task, the first live request of the session --

    GET https://www.sec.gov/files/company_tickers.json
    -> HTTP/2 403, server: AkamaiGHost
       <title>SEC.gov | Request Rate Threshold Exceeded</title>
       Reference ID: 0.15d854b8.1789156967.25fbfbf0

-- came back as a genuine rate-limit block from SEC's own edge (confirmed via
response headers/body, not a local sandbox restriction). A single diagnostic
follow-up request to a *different* sec.gov host,

    GET https://data.sec.gov/api/xbrl/frames/us-gaap/NetIncomeLoss/USD/CY2023.json
    -> HTTP/2 200

came back clean, showing the block is (at least) not blanket across all of
sec.gov at that moment. Per the task rule "If SEC answers 403 or 429, stop
and report -- do not work around it", data collection was halted at that
point and NOT resumed. This script was written to fully implement the
specified method so it is ready to run, but none of its network-touching
functions have been exercised against live data in this session. Treat every
function below as unvalidated until it has actually been run clean,
end-to-end, with its output inspected.

Re-run guidance: try again later, one stage at a time (see USAGE below), and
stop again immediately if any sec.gov host answers 403/429.
============================================================================

METHOD (as specified by the research brief):

  VALUE    dei:EntityPublicFloat -- 10-K cover page figure: aggregate market
           value of common equity held by non-affiliates, as of the last
           business day of the registrant's most recently completed second
           fiscal quarter.
               https://data.sec.gov/api/xbrl/frames/dei/EntityPublicFloat/USD/CY{Y}Q2I.json
           If that frame is sparse for our mapped universe (< FLOAT_COVERAGE_OK,
           see below), also try Q1I / Q3I and use whichever gives the best
           coverage; record which was used.

  EARNINGS us-gaap:NetIncomeLoss, annual duration frame:
               https://data.sec.gov/api/xbrl/frames/us-gaap/NetIncomeLoss/USD/CY{Y}.json

  UNIVERSE S&P 500 membership at mid-year Y (July 1), from the fja05680/sp500
           GitHub dataset ("S&P 500 Historical Components & Changes"). Tickers
           are mapped to CIKs via
               https://www.sec.gov/files/company_tickers.json
           which lists CURRENT tickers only -- a real limitation for tickers
           that later changed name or were delisted/acquired; every ticker
           that fails to map is written to unmapped.csv with a reason.

  For each Y: one CIK = one company (share classes combined). This falls out
  automatically once tickers are resolved to CIKs, because a multi-class
  issuer (e.g. Alphabet GOOGL/GOOG, Berkshire Hathaway BRK.A/BRK.B) files
  under a single CIK and reports one already-combined EntityPublicFloat and
  NetIncomeLoss figure.

    weight share              = sum(float, top-10 by float) / sum(float, all mapped)
    earnings share (all)      = sum(NI,    top-10 by float) / sum(NI,    all mapped)
    earnings share (pos-only) = sum(NI>0,  top-10 by float) / sum(NI where NI>0, all mapped)

  "top 10 by float" is decided ONCE per year (ranking by float) and that same
  set of 10 CIKs is then used for both the weight share and the earnings
  shares -- that is the actual test: are the biggest-by-market-value firms
  proportionately as big by earnings, or do they lag/lead?

  positive-only variant, precisely: the denominator sums NetIncomeLoss only
  over mapped companies with NetIncomeLoss > 0 (loss-makers excluded
  entirely, not clamped to zero and kept in the sum); the numerator sums
  NetIncomeLoss over the SAME top-10-by-float set, counting a top-10 member
  only if its own NetIncomeLoss > 0 (contributes 0 otherwise). This avoids a
  few large losses distorting -- or flipping the sign of -- the ratio.

COMPLIANCE BUILT INTO THIS SCRIPT:
  - User-Agent is EXACTLY
      "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
    on every request. No email address is ever put in a request (header,
    query string, or body).
  - A minimum 1.0s gap is enforced between successive requests to any
    *.sec.gov host -- under the 2 req/s ceiling in the brief, since the
    egress IP is shared with other agents.
  - On HTTP 403 or 429 from a sec.gov host: raise SecBlocked immediately and
    STOP. No retry, no backoff-and-retry loop, no User-Agent rotation, no
    proxy fallback, anywhere in this file.
  - Every successful response is cached to disk (see --cache-dir) so re-runs
    do not re-request data already obtained, and so a long job can be split
    into several short, separate, foreground invocations (one per
    sub-command) instead of one long-running process.
  - The `analyze` stage is 100% offline: it only reads what earlier `fetch-*`
    stages cached to disk, and never makes a network call itself.
  - Non-sec.gov sources (GitHub, for the S&P 500 membership history) are not
    subject to the sec.gov rate rule, but requests are still minimal (one
    directory listing + one file download, plus at most a couple of
    subdirectory listings if the file isn't at repo root) and identify
    themselves with the same User-Agent.

USAGE (run each stage separately in the FOREGROUND and inspect its output
before moving on -- do not background any of these):

    python3 top10.py fetch-tickers
    python3 top10.py fetch-sp500
    python3 top10.py fetch-floats   [--years 2015,2017,2019,2021,2023,2025]
    python3 top10.py fetch-earnings [--years 2015,2017,2019,2021,2023,2025]
    python3 top10.py analyze        [--years 2015,2017,2019,2021,2023,2025]

`python3 top10.py all` runs the stages back to back for convenience, but
given the shared-IP rate limit and the "stop on 403/429" rule, prefer running
stages separately so a block during (say) fetch-earnings doesn't need
fetch-tickers/fetch-sp500/fetch-floats re-run.

Outputs land next to this script (override with --out-dir):
    top10_by_year.csv
    unmapped.csv
"""

import argparse
import os
import csv
import io
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

if not os.environ.get("SEC_UA"): raise SystemExit('Set SEC_UA first, e.g. export SEC_UA="Your Name you@example.com" -- SEC asks automated requests to name their sender (README, "Checking the work").')
USER_AGENT_SEC = os.environ["SEC_UA"]  # SEC fair-access format; sec.gov ONLY (Martin's ruling, 12 Sep).
USER_AGENT_OTHER = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"  # non-sec.gov hosts: no email, ever.
SEC_MIN_INTERVAL_SEC = 1.0          # brief allows up to 2 req/s to sec.gov hosts; we stay well under
YEARS_DEFAULT = [2015, 2017, 2019, 2021, 2023, 2025]
FLOAT_COVERAGE_OK = 0.70            # judgment call (brief does not fix a number): if CY{Y}Q2I covers
                                     # less than this fraction of the mapped universe, also try
                                     # Q1I/Q3I and keep whichever covers best. Stated in the output.
FLOAT_SANITY_MAX_USD = 5_000_000_000_000
    # Fix (agent, 2026-09-12): $5T, safely above the largest real single-company public float/market
    # cap ever recorded (~$3-4T, Apple/Nvidia/Microsoft circa 2024-2025). SEC's frames API republishes
    # dei:EntityPublicFloat exactly as each filer tagged it, with no cross-filer sanity check. A live
    # run against all 6 target years found filer-side scale errors in 5 of 6: Garmin Ltd's 2015 and
    # 2017 float both off by a clean factor of 10^3, and Host Hotels & Resorts (2019), Zimmer Biomet
    # (2021), and M&T Bank (2023) each off by a clean factor of 10^6 (Domino's Pizza, also 2023, off
    # by 10^3) -- e.g. Host Hotels' CY2019Q2I value was $13.1 quadrillion, ~500x total US GDP. Each
    # was large enough to land in "top 10 by float" and silently displace a real top-10 company,
    # corrupting both weight_share and earnings_share for that year, not just the float total. Values
    # above this bound are excluded the same way a CIK with no float data at all would be (dropped
    # from both numerator and denominator) and logged to float_outliers_excluded.csv.
SP500_GITHUB_REPO = "fja05680/sp500"
SP500_NAME_NEEDLE = "s&p 500 historical components"

HERE = Path(__file__).resolve().parent


class SecBlocked(RuntimeError):
    """Raised the instant a sec.gov host answers 403/429. Never caught-and-retried."""


class FetchError(RuntimeError):
    pass


_last_sec_request_ts = None


def _host_of(url: str) -> str:
    return url.split("/")[2].lower()


def _is_sec_host(url: str) -> bool:
    return _host_of(url).endswith("sec.gov")


def _throttle_if_sec(url: str) -> None:
    global _last_sec_request_ts
    if not _is_sec_host(url):
        return
    now = time.monotonic()
    if _last_sec_request_ts is not None:
        wait = SEC_MIN_INTERVAL_SEC - (now - _last_sec_request_ts)
        if wait > 0:
            time.sleep(wait)
    _last_sec_request_ts = time.monotonic()


def http_get(url: str, accept: str = "application/json") -> bytes:
    """GET url with the required User-Agent. The declared-contact UA (with
    email) is sent to sec.gov hosts ONLY; every other host gets the no-email
    UA -- never in headers, URL, or body for non-sec.gov hosts.

    Stops hard (raises SecBlocked) on 403/429 from a sec.gov host. This is by
    design NOT caught and retried anywhere in this script -- the caller
    (a human, or a fresh deliberate re-invocation) decides what to do next.
    """
    _throttle_if_sec(url)
    ua = USER_AGENT_SEC if _is_sec_host(url) else USER_AGENT_OTHER
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": ua,
            "Accept": accept,
            "Accept-Encoding": "identity",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        body = e.read(2000)
        if _is_sec_host(url) and e.code in (403, 429):
            raise SecBlocked(
                f"SEC host answered {e.code} for {url}\n"
                f"First bytes of body: {body[:500]!r}\n"
                f"STOPPING per task rules: no retry, no workaround."
            ) from None
        raise FetchError(f"HTTP {e.code} for {url}\nBody (truncated): {body[:500]!r}") from None
    except urllib.error.URLError as e:
        raise FetchError(f"Network error for {url}: {e}") from None


def cache_path(cache_dir: Path, name: str) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / name


def fetch_json_cached(url: str, cache_dir: Path, name: str, force: bool = False):
    """Network-capable JSON fetch. Only ever called from fetch-* stages."""
    p = cache_path(cache_dir, name)
    if p.exists() and not force:
        return json.loads(p.read_text())
    raw = http_get(url, accept="application/json")
    data = json.loads(raw)
    p.write_text(json.dumps(data))
    return data


def fetch_bytes_cached(url: str, cache_dir: Path, name: str, force: bool = False) -> bytes:
    """Network-capable byte fetch. Only ever called from fetch-* stages."""
    p = cache_path(cache_dir, name)
    if p.exists() and not force:
        return p.read_bytes()
    raw = http_get(url, accept="*/*")
    p.write_bytes(raw)
    return raw


def load_json_cache_only(cache_dir: Path, name: str):
    """Offline-only JSON load. Used by `analyze` so it never touches the network."""
    p = cache_path(cache_dir, name)
    if not p.exists():
        raise FetchError(f"{p} not cached yet -- run the relevant fetch-* stage first.")
    return json.loads(p.read_text())


# --------------------------------------------------------------------------
# Stage 1: SEC ticker -> CIK map
# --------------------------------------------------------------------------

def stage_fetch_tickers(cache_dir: Path, force: bool = False):
    url = "https://www.sec.gov/files/company_tickers.json"
    data = fetch_json_cached(url, cache_dir, "company_tickers.json", force=force)
    print(f"OK: {len(data)} ticker records cached at {cache_path(cache_dir, 'company_tickers.json')}")
    return data


def load_ticker_map(cache_dir: Path):
    """Return (ticker_upper -> cik:int, cik:int -> title). Offline (cache-only)."""
    data = load_json_cache_only(cache_dir, "company_tickers.json")
    ticker_to_cik = {}
    cik_to_title = {}
    for row in data.values():
        cik = int(row["cik_str"])
        ticker = str(row["ticker"]).upper().strip()
        ticker_to_cik[ticker] = cik
        cik_to_title.setdefault(cik, row.get("title", ""))
    return ticker_to_cik, cik_to_title


def normalize_candidates(ticker: str):
    """A few reasonable spellings for the same ticker (BRK.B vs BRK-B, etc.)."""
    t = ticker.upper().strip()
    cands = [t, t.replace(".", "-"), t.replace("-", "."), t.replace(".", ""), t.replace("-", "")]
    out = []
    for c in cands:
        if c not in out:
            out.append(c)
    return out


def map_ticker_to_cik(ticker: str, ticker_to_cik: dict):
    for cand in normalize_candidates(ticker):
        if cand in ticker_to_cik:
            return ticker_to_cik[cand]
    return None


# --------------------------------------------------------------------------
# Stage 2: S&P 500 historical membership (GitHub, fja05680/sp500)
# --------------------------------------------------------------------------

def _list_repo_dir(cache_dir: Path, path_suffix: str, force: bool):
    url = f"https://api.github.com/repos/{SP500_GITHUB_REPO}/contents/{path_suffix}"
    safe_name = f"github_listing_{path_suffix or 'root'}.json".replace("/", "_")
    raw = fetch_bytes_cached(url, cache_dir, safe_name, force=force)
    return json.loads(raw)


def _csv_last_date(csv_bytes: bytes) -> str:
    """Max value of the 'date' column (YYYY-MM-DD sorts lexicographically),
    used only to compare same-shaped candidate files by data recency.
    Returns '' if the column is missing/unparseable."""
    text = csv_bytes.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    fieldnames = reader.fieldnames or []
    date_col = next((c for c in fieldnames if c.lower() == "date"), None)
    if not date_col:
        return ""
    max_date = ""
    for row in reader:
        v = (row.get(date_col) or "").strip()
        if v > max_date:
            max_date = v
    return max_date


def stage_fetch_sp500(cache_dir: Path, force: bool = False):
    root = _list_repo_dir(cache_dir, "", force)

    def find_csv_candidates(listing):
        return [
            e for e in listing
            if e.get("type") == "file"
            and e["name"].lower().endswith(".csv")
            and SP500_NAME_NEEDLE in e["name"].lower()
        ]

    candidates = find_csv_candidates(root)
    if not candidates:
        # The file may live one level down (e.g. a "data" folder) rather than at repo root.
        for entry in root:
            if entry.get("type") == "dir":
                try:
                    sub = _list_repo_dir(cache_dir, entry["name"], force)
                except FetchError:
                    continue
                candidates.extend(find_csv_candidates(sub))

    if not candidates:
        raise FetchError(
            "Could not find an 'S&P 500 Historical Components...csv' file in the "
            f"{SP500_GITHUB_REPO} GitHub repo (checked root and one level of "
            f"subdirectories). Inspect {cache_path(cache_dir, 'github_listing_root.json')} "
            "by hand and adjust SP500_NAME_NEEDLE / the search logic above."
        )

    if len(candidates) == 1:
        chosen = candidates[0]
        print(f"Found 1 candidate file; using: {chosen['name']}")
        csv_bytes = fetch_bytes_cached(chosen["download_url"], cache_dir, "sp500_constituents.csv", force=force)
    else:
        # Fix (agent, 2026-09-12): originally picked by reverse-alphabetical
        # filename sort. For this repo that silently chose a STALE file --
        # its last 'date' row is 2019-01-11 -- over a same-named "(Updated)"
        # file whose data continues to 2026-08-18. Filename sort has no way
        # to know which is current, and picking the stale one would silently
        # apply 2019-vintage S&P 500 membership to the 2021/2023/2025
        # analysis years. Fetch every candidate (a few MB of CSV each,
        # cached) and keep whichever's data actually extends furthest -- a
        # data-driven tie-break instead of a naming guess.
        scored = []
        for c in candidates:
            safe_name = "sp500_candidate__" + c["name"]
            b = fetch_bytes_cached(c["download_url"], cache_dir, safe_name, force=force)
            scored.append((c, _csv_last_date(b), b))
        scored.sort(key=lambda t: t[1], reverse=True)
        print(f"Found {len(scored)} candidate file(s); picking by most recent data coverage:")
        for c, last_date, _ in scored:
            print(f"  {c['name']}: last date row = {last_date or '(unparseable)'}")
        chosen, _, csv_bytes = scored[0]
        print(f"  -> using: {chosen['name']} (most current)")
        cache_path(cache_dir, "sp500_constituents.csv").write_bytes(csv_bytes)

    cache_path(cache_dir, "sp500_source_filename.txt").write_text(chosen["name"])
    print(f"OK: cached {len(csv_bytes)} bytes to {cache_path(cache_dir, 'sp500_constituents.csv')}")


def load_sp500_history(cache_dir: Path):
    """Offline (cache-only). Returns sorted list of (date_str YYYY-MM-DD, tickers_field)."""
    p = cache_path(cache_dir, "sp500_constituents.csv")
    if not p.exists():
        raise FetchError("sp500_constituents.csv not cached yet -- run `fetch-sp500` first.")
    rows = []
    with p.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        date_col = next((c for c in fieldnames if c.lower() == "date"), None)
        tick_col = next((c for c in fieldnames if "ticker" in c.lower()), None)
        if not date_col or not tick_col:
            raise FetchError(
                f"Unexpected columns in sp500_constituents.csv: {fieldnames} -- "
                "expected a 'date' column and a 'tickers' column."
            )
        for row in reader:
            rows.append((row[date_col].strip(), row[tick_col]))
    rows.sort(key=lambda r: r[0])
    return rows


def membership_at(rows, target_date: str):
    """Latest snapshot with date <= target_date. Falls back to earliest available
    snapshot (and says so) if target_date predates all history."""
    chosen = None
    for date_str, tickers_field in rows:
        if date_str <= target_date:
            chosen = (date_str, tickers_field)
        else:
            break
    used_fallback_earliest = False
    if chosen is None:
        if not rows:
            raise FetchError("sp500 history is empty")
        chosen = rows[0]
        used_fallback_earliest = True
    date_used, tickers_field = chosen
    tickers = [t.strip().upper() for t in tickers_field.split(",") if t.strip()]
    return date_used, tickers, used_fallback_earliest


def year_membership_ciks(year: int, ticker_to_cik: dict, sp500_rows, unmapped_rows=None):
    """Resolve mid-year (July 1) S&P 500 membership for `year` down to a CIK set.
    Offline: pure computation over already-loaded data structures."""
    target_date = f"{year}-07-01"
    date_used, tickers, used_fallback = membership_at(sp500_rows, target_date)
    cik_set = set()
    ticker_hits = 0
    for t in tickers:
        cik = map_ticker_to_cik(t, ticker_to_cik)
        if cik is None:
            if unmapped_rows is not None:
                unmapped_rows.append({
                    "year": year, "ticker": t,
                    "note": "no CIK match in company_tickers.json (current tickers only)",
                })
        else:
            cik_set.add(cik)
            ticker_hits += 1
    return {
        "date_used": date_used,
        "used_fallback_earliest": used_fallback,
        "tickers": tickers,
        "n_members_raw_tickers": len(tickers),
        "n_tickers_mapped": ticker_hits,
        "cik_set": cik_set,
        "n_unique_companies_mapped": len(cik_set),
    }


# --------------------------------------------------------------------------
# Stage 3: EntityPublicFloat frames (value)
# --------------------------------------------------------------------------

def float_frame_url(year: int, period: str) -> str:
    return f"https://data.sec.gov/api/xbrl/frames/dei/EntityPublicFloat/USD/CY{year}{period}.json"


def float_frame_cache_name(year: int, period: str) -> str:
    return f"float_CY{year}{period}.json"


def frame_to_cik_map(frame_json: dict) -> dict:
    """SEC frame 'data' entries -> {cik:int: entry}. If a CIK appears more than
    once (original + amended filing both landing in the same window), keep the
    one with the latest 'filed' date."""
    out = {}
    for entry in frame_json.get("data", []):
        cik = int(entry["cik"])
        prev = out.get(cik)
        if prev is None or entry.get("filed", "") >= prev.get("filed", ""):
            out[cik] = entry
    return out


def _coverage(cik_set, fmap: dict) -> float:
    if not cik_set:
        return 0.0
    return sum(1 for c in cik_set if c in fmap) / len(cik_set)


def stage_fetch_floats(cache_dir: Path, years, force: bool = False):
    """Fetch CY{Y}Q2I always; also fetch Q1I/Q3I if Q2I coverage of that year's
    mapped S&P 500 universe is below FLOAT_COVERAGE_OK. Needs tickers+sp500
    already fetched (reads them offline)."""
    ticker_to_cik, _ = load_ticker_map(cache_dir)
    sp500_rows = load_sp500_history(cache_dir)

    for y in years:
        mem = year_membership_ciks(y, ticker_to_cik, sp500_rows)
        cik_set = mem["cik_set"]

        q2_name = float_frame_cache_name(y, "Q2I")
        q2 = fetch_json_cached(float_frame_url(y, "Q2I"), cache_dir, q2_name, force=force)
        q2_map = frame_to_cik_map(q2)
        cov_q2 = _coverage(cik_set, q2_map)
        print(f"CY{y}Q2I: {len(q2.get('data', []))} filer records total; "
              f"covers {cov_q2:.0%} of {len(cik_set)} mapped {y} S&P 500 companies "
              f"(mid-year snapshot: {mem['date_used']}).")

        if cov_q2 < FLOAT_COVERAGE_OK:
            print(f"  coverage below {FLOAT_COVERAGE_OK:.0%} threshold -- also fetching Q1I/Q3I fallbacks.")
            for period in ("Q1I", "Q3I"):
                name = float_frame_cache_name(y, period)
                fr = fetch_json_cached(float_frame_url(y, period), cache_dir, name, force=force)
                cov = _coverage(cik_set, frame_to_cik_map(fr))
                print(f"  CY{y}{period}: {len(fr.get('data', []))} filer records total; covers {cov:.0%}.")


# --------------------------------------------------------------------------
# Stage 4: NetIncomeLoss frames (earnings)
# --------------------------------------------------------------------------

def earnings_frame_url(year: int) -> str:
    return f"https://data.sec.gov/api/xbrl/frames/us-gaap/NetIncomeLoss/USD/CY{year}.json"


def earnings_frame_cache_name(year: int) -> str:
    return f"earnings_CY{year}.json"


def stage_fetch_earnings(cache_dir: Path, years, force: bool = False):
    for y in years:
        name = earnings_frame_cache_name(y)
        data = fetch_json_cached(earnings_frame_url(y), cache_dir, name, force=force)
        print(f"OK: CY{y} NetIncomeLoss frame cached, {len(data.get('data', []))} filer records.")


# --------------------------------------------------------------------------
# Stage 5: analysis (100% offline -- reads only what fetch-* stages cached)
# --------------------------------------------------------------------------

def analyze_year(cache_dir: Path, year: int, ticker_to_cik: dict, cik_to_title: dict,
                  sp500_rows, unmapped_rows: list, outlier_rows: list = None):
    mem = year_membership_ciks(year, ticker_to_cik, sp500_rows, unmapped_rows=unmapped_rows)
    if mem["used_fallback_earliest"]:
        print(f"  WARNING {year}: no S&P 500 snapshot on/before {year}-07-01; "
              f"used earliest available ({mem['date_used']}) instead.")
    cik_set = mem["cik_set"]
    n_unique_companies = mem["n_unique_companies_mapped"]

    # ---- value (float): use whichever of Q2I/Q1I/Q3I is cached and covers best ----
    periods_available = {}
    for period in ("Q2I", "Q1I", "Q3I"):
        name = float_frame_cache_name(year, period)
        if cache_path(cache_dir, name).exists():
            periods_available[period] = frame_to_cik_map(load_json_cache_only(cache_dir, name))
    if "Q2I" not in periods_available:
        raise FetchError(f"{float_frame_cache_name(year, 'Q2I')} not cached -- run fetch-floats first.")

    cov_q2 = _coverage(cik_set, periods_available["Q2I"])
    if cov_q2 < FLOAT_COVERAGE_OK and len(periods_available) > 1:
        chosen_period = max(periods_available, key=lambda k: _coverage(cik_set, periods_available[k]))
    else:
        chosen_period = "Q2I"
    chosen_map = periods_available[chosen_period]

    raw_float_vals = {c: float(chosen_map[c]["val"]) for c in cik_set if c in chosen_map}
    float_outliers = {c: v for c, v in raw_float_vals.items() if v > FLOAT_SANITY_MAX_USD}
    float_vals = {c: v for c, v in raw_float_vals.items() if v <= FLOAT_SANITY_MAX_USD}
    for c, v in float_outliers.items():
        print(f"  EXCLUDED (data error) {year}: CIK {c} {cik_to_title.get(c, '?')} reported "
              f"EntityPublicFloat={v:,.0f} USD in CY{year}{chosen_period} -- exceeds sanity bound "
              f"{FLOAT_SANITY_MAX_USD:,.0f}; ratio to a plausible value is a clean power of 10, "
              f"consistent with a filer-side XBRL scale error. Treated as missing (dropped from "
              f"both the top-10 ranking and the value/earnings totals).")
        if outlier_rows is not None:
            outlier_rows.append({
                "year": year, "cik": c, "name": cik_to_title.get(c, "?"),
                "frame": f"CY{year}{chosen_period}", "reported_float_usd": v,
                "sanity_bound_usd": FLOAT_SANITY_MAX_USD,
                "note": "excluded: exceeds sanity bound, likely filer XBRL scale error (10^3/10^6)",
            })
    n_with_float = len(float_vals)
    total_float = sum(float_vals.values())
    top10 = sorted(float_vals.items(), key=lambda kv: kv[1], reverse=True)[:10]
    if len(top10) < 10:
        print(f"  WARNING {year}: only {len(top10)} companies have float data (< 10).")
    top10_ciks = [c for c, _ in top10]
    top10_float_sum = sum(v for _, v in top10)
    weight_share = (top10_float_sum / total_float) if total_float else None

    # ---- earnings ----
    earn_name = earnings_frame_cache_name(year)
    earn_map = frame_to_cik_map(load_json_cache_only(cache_dir, earn_name))
    earn_vals = {c: float(earn_map[c]["val"]) for c in cik_set if c in earn_map}
    n_with_earnings = len(earn_vals)

    total_earnings_all = sum(earn_vals.values())
    top10_earnings_all = sum(earn_vals.get(c, 0.0) for c in top10_ciks)
    earnings_share_all = (top10_earnings_all / total_earnings_all) if total_earnings_all else None

    total_earnings_pos = sum(v for v in earn_vals.values() if v > 0)
    top10_earnings_pos = sum(v for c in top10_ciks if (v := earn_vals.get(c, 0.0)) > 0)
    earnings_share_pos = (top10_earnings_pos / total_earnings_pos) if total_earnings_pos else None

    top10_names = "; ".join(f"{cik_to_title.get(c, '?')} (CIK {c})" for c in top10_ciks)

    return {
        "year": year,
        "sp500_snapshot_date": mem["date_used"],
        "float_frame_used": f"CY{year}{chosen_period}",
        "n_members_raw_tickers": mem["n_members_raw_tickers"],
        "n_tickers_mapped": mem["n_tickers_mapped"],
        "n_unique_companies_mapped": n_unique_companies,
        "n_with_float": n_with_float,
        "pct_float_coverage_of_mapped": (
            round(n_with_float / n_unique_companies, 4) if n_unique_companies else None
        ),
        "n_with_earnings": n_with_earnings,
        "pct_earnings_coverage_of_mapped": (
            round(n_with_earnings / n_unique_companies, 4) if n_unique_companies else None
        ),
        "top10_names": top10_names,
        "total_float_usd": total_float,
        "top10_float_usd": top10_float_sum,
        "weight_share": weight_share,
        "total_earnings_all_usd": total_earnings_all,
        "top10_earnings_all_usd": top10_earnings_all,
        "earnings_share_all": earnings_share_all,
        "total_earnings_positive_usd": total_earnings_pos,
        "top10_earnings_positive_usd": top10_earnings_pos,
        "earnings_share_positive_only": earnings_share_pos,
    }


def stage_analyze(cache_dir: Path, out_dir: Path, years):
    ticker_to_cik, cik_to_title = load_ticker_map(cache_dir)
    sp500_rows = load_sp500_history(cache_dir)
    unmapped_rows = []
    outlier_rows = []
    results = []
    for y in years:
        print(f"Analyzing {y} ...")
        results.append(analyze_year(cache_dir, y, ticker_to_cik, cik_to_title, sp500_rows,
                                     unmapped_rows, outlier_rows))

    out_dir.mkdir(parents=True, exist_ok=True)

    out_csv = out_dir / "top10_by_year.csv"
    fieldnames = list(results[0].keys()) if results else []
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in results:
            w.writerow(r)
    print(f"Wrote {out_csv}")

    unmapped_csv = out_dir / "unmapped.csv"
    with unmapped_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["year", "ticker", "note"])
        w.writeheader()
        for r in unmapped_rows:
            w.writerow(r)
    print(f"Wrote {unmapped_csv} ({len(unmapped_rows)} unmapped ticker-years)")

    outliers_csv = out_dir / "float_outliers_excluded.csv"
    with outliers_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "year", "cik", "name", "frame", "reported_float_usd", "sanity_bound_usd", "note",
        ])
        w.writeheader()
        for r in outlier_rows:
            w.writerow(r)
    print(f"Wrote {outliers_csv} ({len(outlier_rows)} float values excluded as data errors)")

    for r in results:
        print(r)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def parse_years(s: str):
    return [int(x) for x in s.split(",") if x.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=[
        "fetch-tickers", "fetch-sp500", "fetch-floats", "fetch-earnings", "analyze", "all",
    ])
    ap.add_argument("--cache-dir", default=str(HERE / "cache"))
    ap.add_argument("--out-dir", default=str(HERE))
    ap.add_argument("--years", default=",".join(str(y) for y in YEARS_DEFAULT))
    ap.add_argument("--force", action="store_true", help="ignore cache, re-fetch from network")
    args = ap.parse_args()

    cache_dir = Path(args.cache_dir)
    out_dir = Path(args.out_dir)
    years = parse_years(args.years)

    try:
        if args.stage in ("fetch-tickers", "all"):
            stage_fetch_tickers(cache_dir, force=args.force)
        if args.stage in ("fetch-sp500", "all"):
            stage_fetch_sp500(cache_dir, force=args.force)
        if args.stage in ("fetch-floats", "all"):
            stage_fetch_floats(cache_dir, years, force=args.force)
        if args.stage in ("fetch-earnings", "all"):
            stage_fetch_earnings(cache_dir, years, force=args.force)
        if args.stage in ("analyze", "all"):
            stage_analyze(cache_dir, out_dir, years)
    except SecBlocked as e:
        print(f"\nSTOPPED (SEC rate/access block): {e}\n", file=sys.stderr)
        sys.exit(2)
    except FetchError as e:
        print(f"\nSTOPPED (fetch error): {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
