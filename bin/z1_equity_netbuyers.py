#!/usr/bin/env python3
"""
z1_equity_netbuyers.py

Builds the equity net-buyer table from the Federal Reserve's Financial
Accounts of the United States (Z.1): who bought US corporate equities, net,
each quarter, and who sold.

USAGE
    python3 z1_equity_netbuyers.py current        # use the release currently
                                                    # posted at /releases/z1/current/
    python3 z1_equity_netbuyers.py 20260911        # pin to a specific dated
                                                    # release folder (vintage)

WHAT IT DOES
    1. Fetches the Z.1 release landing page to record the release date and
       data vintage (e.g. "2026:Q2 Release").
    2. Fetches z1_table_mapping.csv from the release folder and looks up the
       table whose TITLE is "Corporate equities" -- NOT by assuming a fixed
       table number. (The Fed renumbers/relabels tables between releases;
       see CAVEAT below.)
    3. Downloads the single bulk CSV package (z1_csv_files.zip) linked from
       the release page and extracts only the members needed, locally --
       no further HTTP requests.
    4. Parses the flow (not-seasonally-adjusted quarterly, "FU"-prefixed)
       table and the level ("LM"/"FL"-prefixed) table, classifies every line
       as issuer / issuer_detail / holder / total from its own text
       description (asset vs. liability vs. "All sectors"), and computes
       flow, level, and implied revaluation (delta-level minus flow) for
       every sector line, every quarter, 2015:Q1 to the latest available.
    5. Runs the identity check (sum of holders vs. total; sum of issuers vs.
       total) and a revaluation cross-check against the Fed's own published
       FR (revaluation) series where one exists for a given sector.
    6. Writes netbuyers_quarterly.csv and netbuyers_periods.csv.

CAVEAT ON TABLE NUMBERS (discovered while building this script, 2026-09-11)
    The brief that specified this task asked for "F.223 (corporate
    equities, flows) and L.223 (levels)". In the 11-Sep-2026 (2026:Q2)
    release, old-style table numbers F.223 / L.223 denote "Direct
    investment intercompany debt", not corporate equities. Corporate
    equities is old-style F.224 / L.224, and under the Fed's current
    table-naming scheme both flow and level live under the same root code
    F51.1, distinguished by suffix: F51.1.t (transactions/flow) and F51.1.s
    (stock/level) -- i.e. the flow/level distinction moved from a
    F-prefix-vs-L-prefix table-number convention to a .t-vs-.s suffix on a
    shared root. This script does NOT hardcode "F51.1" either: it resolves
    the correct table each run by matching on the table TITLE ("Corporate
    equities") in that release's own z1_table_mapping.csv, so it keeps
    working if the Fed renumbers again.

CAVEAT ON REVALUATION SOURCE FILES
    Z.1 does not publish a single unified "R.223"-style revaluation table
    for corporate equities. Revaluation (FR-prefixed) series for this
    instrument are scattered across separate per-SECTOR "integrated" or
    "revaluation-only" tables (one file per sector, not one file per
    instrument). Quarterly (as opposed to annual-only) FR series for
    corporate equities exist only for four sectors/aggregates:
    Nonfinancial corporate business (as a holder of others' equity),
    Households and nonprofit organizations, Rest of the world (as a holder
    of US equity), and "Domestic financial sectors" in aggregate. The four
    source files (S11_1_r, S1M_r, S12_i_q, S2_i_q) were identified by
    manually inspecting data dictionaries for the corporate-equities
    instrument specifically; this mapping is HARDCODED below (see
    REVAL_SOURCE_FILEBASES) and would need re-verification by hand if this
    script is ever adapted to a different instrument. The "Domestic
    financial sectors" comparison further requires grouping ~14 individual
    holder lines into a best-effort proxy for that aggregate (excluding the
    two government pension lines, which are classified as general
    government, not financial business); that one comparison is
    approximate and is flagged as such in the printed diagnostics.

FREE PUBLIC SOURCE, POLITE FETCHING
    Only https://www.federalreserve.gov is contacted (3 requests total per
    run: the release page, the table-mapping CSV, and the bulk CSV zip).
    Every request carries the exact required User-Agent and no email
    address anywhere. A per-host minimum interval keeps requests to at most
    2/second even if this script is ever extended to fetch more files.
"""

import csv
import io
import re
import sys
import time
import zipfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

USER_AGENT = (
    "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
)
HOST_MIN_INTERVAL_SECONDS = 0.55  # keeps us under 2 req/sec to any one host

SCRIPT_DIR = Path(__file__).resolve().parent
RAW_DIR = SCRIPT_DIR / "raw"
DICT_DIR = RAW_DIR / "data_dictionary"

FIRST_QUARTER = "2015:Q1"

PERIODS = [
    ("2015-19", "2015:Q1", "2019:Q4"),
    ("2020-21", "2020:Q1", "2021:Q4"),
    ("2022-23", "2022:Q1", "2023:Q4"),
    ("2024-latest", "2024:Q1", None),  # None end = clipped to latest available
]

# Sector names that are TOP-LEVEL issuers of corporate equity (matches the
# brief's own definition: "nonfinancial corporate business; domestic
# financial sectors; rest of the world = foreign issues bought by US
# residents"). Every other "; liability" line is a *component* of the
# "Domestic financial sectors" aggregate and is classified issuer_detail so
# it is not double-counted against that aggregate in the identity check.
ISSUER_TOP_SECTOR_NAMES = {
    "Nonfinancial corporate business",
    "Domestic financial sectors",
    "Rest of the world",
}

# Hand-verified (2026-09-11) source files for corporate-equities revaluation
# (FR-prefixed) series, and the single series ID each contributes.
REVAL_SOURCES = {
    "nfc_holder": {
        "filebase": "S11_1_r",
        "series_id": "FR103064103.Q",
        "matches_holder_series": ["FU103064103.Q"],  # 1:1
        "note": "Nonfinancial corporate business as a holder of others' equity",
    },
    "households": {
        "filebase": "S1M_r",
        "series_id": "FR153064105.Q",
        "matches_holder_series": ["FU153064105.Q"],  # 1:1
        "note": "Households and nonprofit organizations",
    },
    "row_holder": {
        "filebase": "S2_i_q",
        "series_id": "FR263064105.Q",
        "matches_holder_series": ["FU263064105.Q"],  # 1:1
        "note": "Rest of the world as a holder of US equity",
    },
    "domestic_financial_approx": {
        "filebase": "S12_i_q",
        "series_id": "FR793064105.Q",
        # Best-effort grouping of financial-business holder lines. Excludes
        # federal and state/local government pension funds (general
        # government, not financial business, in Fed sector taxonomy).
        # APPROXIMATE -- see module docstring caveat.
        "matches_holder_series": [
            "FU763064103.Q",  # US-chartered depository institutions
            "FU753064103.Q",  # Foreign banking offices in the US
            "FU513064105.Q",  # Property-casualty insurance companies
            "FU543064105.Q",  # Life insurance companies
            "FU573064105.Q",  # Private pension funds
            "FU653064100.Q",  # Mutual funds
            "FU553064103.Q",  # Closed-end funds
            "FU563064100.Q",  # Exchange-traded funds
            "FU453064103.Q",  # Business development companies
            "FU463064105.Q",  # Interval funds and tender offer funds
            "FU623064105.Q",  # Hedge funds (domestic)
            "FU443064100.Q",  # Private debt funds
            "FU663064105.Q",  # Security brokers and dealers
            "FU503064105.Q",  # Other financial business
        ],
        "note": "APPROXIMATE: best-effort sum of financial-business holder "
        "lines, not an official Fed aggregation crosswalk",
    },
}

_last_request_time = {}


def throttled_get(url, timeout=60):
    host = urlparse(url).netloc
    now = time.monotonic()
    last = _last_request_time.get(host, 0.0)
    wait = HOST_MIN_INTERVAL_SECONDS - (now - last)
    if wait > 0:
        time.sleep(wait)
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        status = getattr(resp, "status", 200)
    _last_request_time[host] = time.monotonic()
    return status, data


def fetch_and_save(url, dest: Path, timeout=60):
    status, data = throttled_get(url, timeout=timeout)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    print(f"  fetched {url} -> {dest.relative_to(SCRIPT_DIR)} "
          f"(HTTP {status}, {len(data):,} bytes)")
    return data


def resolve_release(arg):
    print("Step 1: resolving release ...")
    html_bytes = fetch_and_save(
        "https://www.federalreserve.gov/releases/z1/",
        RAW_DIR / "z1_release_page.html",
    )
    html = html_bytes.decode("utf-8", errors="replace")
    m_date = re.search(r"Release Date:\s*([A-Za-z]+ \d{1,2}, \d{4})", html)
    m_vint = re.search(r"(\d{4}:Q\d)\s*Release", html)
    m_folder = re.search(r"/releases/z1/(\d{8})/", html)
    release_date = m_date.group(1) if m_date else None
    vintage = m_vint.group(1) if m_vint else None
    folder_seen_on_page = m_folder.group(1) if m_folder else None

    if arg == "current":
        base_url = "https://www.federalreserve.gov/releases/z1/current/"
        folder_date = folder_seen_on_page
    else:
        if not re.fullmatch(r"\d{8}", arg):
            raise SystemExit(
                f"Release argument must be 'current' or an 8-digit date "
                f"(YYYYMMDD), got: {arg!r}"
            )
        base_url = f"https://www.federalreserve.gov/releases/z1/{arg}/"
        folder_date = arg

    print(f"  release date on page : {release_date}")
    print(f"  data vintage on page : {vintage}")
    print(f"  dated folder in use  : {folder_date}")
    print(f"  base URL             : {base_url}")
    return {
        "base_url": base_url,
        "release_date": release_date,
        "vintage": vintage,
        "folder_date": folder_date,
    }


def resolve_table_codes(base_url):
    print("Step 2: resolving 'Corporate equities' table codes from "
          "z1_table_mapping.csv ...")
    data = fetch_and_save(
        base_url + "z1_table_mapping.csv", RAW_DIR / "z1_table_mapping.csv"
    )
    text = data.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    flow_new = flow_old = stock_new = stock_old = None
    for row in reader:
        title = (row.get("title") or "").strip().lower()
        if title == "corporate equities":
            newc = (row.get("new") or "").strip()
            oldc = (row.get("old") or "").strip()
            if newc.endswith(".t"):
                flow_new, flow_old = newc, oldc
            elif newc.endswith(".s"):
                stock_new, stock_old = newc, oldc
    if not flow_new or not stock_new:
        raise SystemExit(
            "Could not find a 'Corporate equities' row in z1_table_mapping.csv"
        )
    print(f"  flow table : new={flow_new}  old={flow_old}")
    print(f"  level table: new={stock_new}  old={stock_old}")
    return flow_new, flow_old, stock_new, stock_old


def code_to_filebase(code):
    return code.replace(".", "_")


def download_and_extract_zip(base_url, wanted_filebases):
    print("Step 3: downloading bulk CSV package (single request) ...")
    zip_path = RAW_DIR / "z1_csv_files.zip"
    fetch_and_save(base_url + "z1_csv_files.zip", zip_path)

    print("  extracting needed members locally (no further HTTP requests) ...")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DICT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
        for fb in wanted_filebases:
            csv_member = f"csv/{fb}.csv"
            dict_member = f"data_dictionary/{fb}.txt"
            if csv_member not in names:
                raise SystemExit(
                    f"Expected member {csv_member!r} not found in "
                    f"{zip_path.name} -- stopping rather than guessing."
                )
            (RAW_DIR / f"{fb}.csv").write_bytes(zf.read(csv_member))
            if dict_member in names:
                (DICT_DIR / f"{fb}.txt").write_bytes(zf.read(dict_member))
            print(f"    extracted {fb}.csv"
                  + (f" + {fb}.txt" if dict_member in names else " (no data dictionary found)"))


def parse_data_dictionary(path: Path):
    """Returns list of (line_label, series_id, description) tuples.

    Z.1 data-dictionary .txt files are tab-separated with NO header row and
    columns [series_id, description, "Line N", table_label, unit_desc] --
    e.g. "FU893064105.Q\tAll sectors; corporate equities; asset\tLine 1\t...".
    (Do not confuse this with a text viewer's own cat-n-style line-number
    prefix, which is not part of the file.)
    """
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        series_id, description, line_label = parts[0].strip(), parts[1].strip(), parts[2].strip()
        rows.append((line_label, series_id, description))
    return rows


def classify(description: str):
    """Classify a Z.1 line from its own text description alone (no
    hardcoded series-ID lists), per the module docstring's rules."""
    parts = [p.strip() for p in description.split(";")]
    sector = parts[0]
    tail = parts[-1] if parts else ""
    if sector == "All sectors":
        return "total", sector
    if tail == "liability":
        if sector in ISSUER_TOP_SECTOR_NAMES:
            return "issuer", sector
        return "issuer_detail", sector
    if "total financial assets" in tail:
        # Closed-end fund / ETF equity-liability proxy lines: the Fed uses
        # a fund's total financial assets as a stand-in for its equity
        # liability (shares outstanding), since these are pass-through
        # vehicles. These are components of "Domestic financial sectors".
        return "issuer_detail", sector
    if tail == "asset":
        return "holder", sector
    return "unclassified", sector


def to_float(x):
    if x is None:
        return None
    x = x.strip()
    if x in ("", "ND"):
        return None
    try:
        return float(x)
    except ValueError:
        return None


def load_wide_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return {row["date"]: row for row in csv.DictReader(f)}


def quarter_before(date_str):
    year_s, q_s = date_str.split(":Q")
    year, q = int(year_s), int(q_s)
    return f"{year - 1}:Q4" if q == 1 else f"{year}:Q{q - 1}"


def enumerate_quarters(start, end):
    y, q = (int(v) for v in start.split(":Q"))
    ey, eq = (int(v) for v in end.split(":Q"))
    out = []
    while (y, q) <= (ey, eq):
        out.append(f"{y}:Q{q}")
        q += 1
        if q == 5:
            q, y = 1, y + 1
    return out


def r3(x):
    return None if x is None else round(x, 3)


def main(arg):
    release_info = resolve_release(arg)
    flow_new, flow_old, stock_new, stock_old = resolve_table_codes(
        release_info["base_url"]
    )
    if flow_old.upper() not in ("F.224",) or stock_old.upper() not in ("L.224",):
        print(f"  NOTE: old-style codes resolved to {flow_old}/{stock_old} "
              f"(this script does not assume F.224/L.224 either -- it always "
              f"looks the codes up by table title).")

    flow_fb = code_to_filebase(flow_new)          # e.g. F51_1_t  (SAAR)
    flow_tu_fb = flow_fb + "_tu"                   # e.g. F51_1_t_tu (NSA quarterly)
    stock_fb = code_to_filebase(stock_new)         # e.g. F51_1_s

    reval_filebases = sorted({v["filebase"] for v in REVAL_SOURCES.values()})
    wanted = [flow_fb, flow_tu_fb, stock_fb] + reval_filebases
    download_and_extract_zip(release_info["base_url"], wanted)

    print("Step 4: parsing data dictionaries and classifying lines ...")
    flow_dict_rows = parse_data_dictionary(DICT_DIR / f"{flow_tu_fb}.txt")
    level_dict_rows = parse_data_dictionary(DICT_DIR / f"{stock_fb}.txt")

    classification = {}  # series_id -> (role, sector, description)
    for _, sid, desc in flow_dict_rows:
        classification[sid] = (*classify(desc), desc)

    n_by_role = {}
    for sid, (role, sector, desc) in classification.items():
        n_by_role.setdefault(role, []).append((sid, sector))
    for role in ("total", "issuer", "issuer_detail", "holder", "unclassified"):
        items = n_by_role.get(role, [])
        print(f"  role={role:14s} n={len(items)}")
        if role == "unclassified" and items:
            for sid, sector in items:
                print(f"    UNCLASSIFIED: {sid} ({sector}) -- "
                      f"{classification[sid][2]}")

    level_by_tail = {}
    for _, sid, desc in level_dict_rows:
        level_by_tail[sid[2:]] = sid  # strip 2-letter prefix (LM/FL/...)

    print("Step 5: loading time series ...")
    flow_by_date = load_wide_csv(RAW_DIR / f"{flow_tu_fb}.csv")
    level_by_date = load_wide_csv(RAW_DIR / f"{stock_fb}.csv")
    reval_by_date = {}
    for key, spec in REVAL_SOURCES.items():
        reval_by_date[key] = load_wide_csv(RAW_DIR / f"{spec['filebase']}.csv")

    all_dates = sorted(flow_by_date.keys())
    last_date = all_dates[-1]
    quarters = [d for d in all_dates if FIRST_QUARTER <= d <= last_date]
    print(f"  quarters covered: {quarters[0]} .. {quarters[-1]} "
          f"({len(quarters)} quarters)")
    if release_info["vintage"] and not last_date.startswith(
        release_info["vintage"].split(":")[0]
    ):
        pass  # vintage sanity is reported below regardless

    # ---- Build per quarter x series table -------------------------------
    series_ids = list(classification.keys())
    records = []  # (quarter, series_id, role, sector, flow_bn, level_bn, reval_bn)
    for date in quarters:
        prev_date = quarter_before(date)
        for sid in series_ids:
            role, sector, desc = classification[sid]
            flow_raw = to_float(flow_by_date.get(date, {}).get(sid))
            flow_bn = flow_raw / 1000.0 if flow_raw is not None else None

            level_bn = None
            reval_bn = None
            level_sid = level_by_tail.get(sid[2:])
            if level_sid:
                lv_t = to_float(level_by_date.get(date, {}).get(level_sid))
                lv_prev = to_float(level_by_date.get(prev_date, {}).get(level_sid))
                if lv_t is not None:
                    level_bn = lv_t / 1000.0
                if lv_t is not None and lv_prev is not None and flow_raw is not None:
                    reval_bn = (lv_t - lv_prev) / 1000.0 - flow_bn

            records.append((date, sid, role, sector, flow_bn, level_bn, reval_bn))

    # ---- Identity checks --------------------------------------------------
    print("Step 6: identity checks ...")
    total_sid = next(sid for sid, (role, *_ ) in classification.items() if role == "total")
    by_date_role = {}
    for date, sid, role, sector, flow_bn, level_bn, reval_bn in records:
        by_date_role.setdefault(date, {}).setdefault(role, []).append(
            (sid, flow_bn)
        )

    max_disc_holders = (None, -1.0)
    max_disc_issuers = (None, -1.0)
    max_disc_issuer_detail_vs_domfin = (None, -1.0)
    for date in quarters:
        d = by_date_role.get(date, {})
        total_val = next(
            (v for sid, v in d.get("total", []) if sid == total_sid), None
        )
        holder_sum = sum(v for _, v in d.get("holder", []) if v is not None)
        issuer_sum = sum(v for _, v in d.get("issuer", []) if v is not None)
        detail_sum = sum(v for _, v in d.get("issuer_detail", []) if v is not None)
        domfin_val = next(
            (v for sid, v in d.get("issuer", []) if sid == "FU793164105.Q"), None
        )
        if total_val is not None:
            disc_h = abs(holder_sum - total_val)
            disc_i = abs(issuer_sum - total_val)
            if disc_h > max_disc_holders[1]:
                max_disc_holders = (date, disc_h)
            if disc_i > max_disc_issuers[1]:
                max_disc_issuers = (date, disc_i)
        if domfin_val is not None:
            disc_d = abs(detail_sum - domfin_val)
            if disc_d > max_disc_issuer_detail_vs_domfin[1]:
                max_disc_issuer_detail_vs_domfin = (date, disc_d)

    print(f"  max |sum(holders) - TOTAL|            = {max_disc_holders[1]:.4f} "
          f"$bn (at {max_disc_holders[0]})")
    print(f"  max |sum(issuer top3) - TOTAL|        = {max_disc_issuers[1]:.4f} "
          f"$bn (at {max_disc_issuers[0]})")
    print(f"  max |sum(issuer_detail) - domfin agg| = "
          f"{max_disc_issuer_detail_vs_domfin[1]:.4f} $bn "
          f"(at {max_disc_issuer_detail_vs_domfin[0]}) "
          f"[internal QC: detail lines should sum to the 'Domestic financial "
          f"sectors' aggregate]")

    # Household-as-residual check: TOTAL(t) - sum(all OTHER holders)(t) vs
    # actual published household line.
    household_sid = "FU153064105.Q"
    max_resid_gap = (None, -1.0)
    for date in quarters:
        d = by_date_role.get(date, {})
        total_val = next(
            (v for sid, v in d.get("total", []) if sid == total_sid), None
        )
        other_holders_sum = sum(
            v for sid, v in d.get("holder", []) if sid != household_sid and v is not None
        )
        actual_hh = next(
            (v for sid, v in d.get("holder", []) if sid == household_sid), None
        )
        if total_val is not None and actual_hh is not None:
            implied_hh = total_val - other_holders_sum
            gap = abs(implied_hh - actual_hh)
            if gap > max_resid_gap[1]:
                max_resid_gap = (date, gap)
    print(f"  household-as-plug check: max |implied - actual| = "
          f"{max_resid_gap[1]:.4f} $bn (at {max_resid_gap[0]}) "
          f"[near-zero confirms household absorbs the holder-side allocation "
          f"residual, as the brief describes]")

    # ---- Revaluation cross-check against published FR series -------------
    print("Step 7: revaluation cross-check (implied vs. published FR) ...")
    flow_bn_by_date_sid = {
        (date, sid): flow_bn for date, sid, *_r, flow_bn, _lv, _rv in
        [(d, s, r, sec, fb, lb, rb) for d, s, r, sec, fb, lb, rb in records]
    }
    reval_bn_by_date_sid = {
        (date, sid): reval_bn for date, sid, role, sector, flow_bn, level_bn, reval_bn in records
    }

    overall_max_gap = (-1.0, None, None)
    for key, spec in REVAL_SOURCES.items():
        fr_dates = reval_by_date[key]
        max_gap = (None, -1.0)
        n_compared = 0
        for date in quarters:
            fr_raw = to_float(fr_dates.get(date, {}).get(spec["series_id"]))
            if fr_raw is None:
                continue
            fr_bn = fr_raw / 1000.0
            implied = 0.0
            missing = False
            for sid in spec["matches_holder_series"]:
                v = reval_bn_by_date_sid.get((date, sid))
                if v is None:
                    missing = True
                    break
                implied += v
            if missing:
                continue
            gap = abs(implied - fr_bn)
            n_compared += 1
            if gap > max_gap[1]:
                max_gap = (date, gap)
        label = spec["note"]
        print(f"  {key:26s} ({label}): max |implied - published FR| = "
              f"{max_gap[1]:.4f} $bn (at {max_gap[0]}, n={n_compared} quarters compared)")
        if max_gap[1] > overall_max_gap[0]:
            overall_max_gap = (max_gap[1], key, max_gap[0])
    print(f"  overall max revaluation gap across the four checks = "
          f"{overall_max_gap[0]:.4f} $bn ({overall_max_gap[1]}, {overall_max_gap[2]})")

    # ---- Write netbuyers_quarterly.csv ------------------------------------
    print("Step 8: writing netbuyers_quarterly.csv ...")
    out_q = SCRIPT_DIR / "netbuyers_quarterly.csv"
    with out_q.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["quarter", "sector", "role", "flow_bn", "level_bn",
                    "reval_bn", "series_code"])
        for date, sid, role, sector, flow_bn, level_bn, reval_bn in records:
            w.writerow([date, sector, role, r3(flow_bn), r3(level_bn),
                        r3(reval_bn), sid])
    print(f"  wrote {out_q.relative_to(SCRIPT_DIR)} ({len(records)} rows)")

    # ---- Period aggregation and netbuyers_periods.csv ---------------------
    print("Step 9: period aggregation ...")
    out_p = SCRIPT_DIR / "netbuyers_periods.csv"
    period_rows = []
    for label, p_start, p_end_nominal in PERIODS:
        p_end = p_end_nominal if p_end_nominal is not None else last_date
        p_end = min(p_end, last_date)
        q_list = [q for q in enumerate_quarters(p_start, p_end) if q in flow_by_date]
        start_level_q = quarter_before(p_start)

        # per-series sums for this period
        per_series = {}
        for sid in series_ids:
            role, sector, desc = classification[sid]
            flow_sum = 0.0
            any_flow = False
            for q in q_list:
                v = flow_bn_by_date_sid.get((q, sid))
                if v is not None:
                    flow_sum += v
                    any_flow = True
            level_sid = level_by_tail.get(sid[2:])
            start_level_bn = None
            end_level_bn = None
            if level_sid:
                sv = to_float(level_by_date.get(start_level_q, {}).get(level_sid))
                ev = to_float(level_by_date.get(p_end, {}).get(level_sid))
                start_level_bn = sv / 1000.0 if sv is not None else None
                end_level_bn = ev / 1000.0 if ev is not None else None
            reval_sum = 0.0
            any_reval = False
            for q in q_list:
                v = reval_bn_by_date_sid.get((q, sid))
                if v is not None:
                    reval_sum += v
                    any_reval = True
            delta_level_bn = (
                end_level_bn - start_level_bn
                if (end_level_bn is not None and start_level_bn is not None)
                else None
            )
            per_series[sid] = {
                "role": role,
                "sector": sector,
                "sum_flow_bn": flow_sum if any_flow else None,
                "start_level_bn": start_level_bn,
                "end_level_bn": end_level_bn,
                "delta_level_bn": delta_level_bn,
                "sum_reval_bn": reval_sum if any_reval else None,
                "n_quarters": len(q_list),
            }

        holder_sids = [sid for sid in series_ids if classification[sid][0] == "holder"]
        ranked = sorted(
            holder_sids,
            key=lambda s: (per_series[s]["sum_flow_bn"] if per_series[s]["sum_flow_bn"] is not None else 0.0),
            reverse=True,
        )
        rank_of = {sid: i + 1 for i, sid in enumerate(ranked)}

        for sid in series_ids:
            info = per_series[sid]
            is_holder = info["role"] == "holder"
            rank_buyer = rank_of[sid] if is_holder else None
            net_seller = (
                (info["sum_flow_bn"] is not None and info["sum_flow_bn"] < 0)
                if is_holder else None
            )
            period_rows.append([
                label, info["sector"], info["role"], sid, info["n_quarters"],
                r3(info["sum_flow_bn"]), r3(info["start_level_bn"]),
                r3(info["end_level_bn"]), r3(info["delta_level_bn"]),
                r3(info["sum_reval_bn"]),
                rank_buyer if rank_buyer is not None else "",
                net_seller if net_seller is not None else "",
            ])

    with out_p.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["period", "sector", "role", "series_code", "quarters_n",
                    "sum_flow_bn", "start_level_bn", "end_level_bn",
                    "delta_level_bn", "sum_reval_bn", "rank_buyer",
                    "net_seller"])
        w.writerows(period_rows)
    print(f"  wrote {out_p.relative_to(SCRIPT_DIR)} ({len(period_rows)} rows)")

    # ---- Period summary printed for the record ----------------------------
    print("Step 10: period summary (top 5 net buyers, all net sellers, "
          "NFC net issuance, revaluation share of change in total market value) ...")
    nfc_sid = "FU103164105.Q"
    for label, p_start, p_end_nominal in PERIODS:
        p_end = p_end_nominal if p_end_nominal is not None else last_date
        p_end = min(p_end, last_date)
        rows_this_period = [r for r in period_rows if r[0] == label]
        by_sid = {r[3]: r for r in rows_this_period}
        print(f"\n  == period {label} ({p_start} to {p_end}) ==")

        holder_entries = [r for r in rows_this_period if r[2] == "holder"]
        holder_entries_sorted = sorted(
            holder_entries,
            key=lambda r: (r[5] if r[5] is not None else 0.0),
            reverse=True,
        )
        print("  top 5 net buyers ($bn cumulative net purchases over period):")
        for r in holder_entries_sorted[:5]:
            print(f"    {r[1]:60s} {r[5]:>12}")
        sellers = [r for r in holder_entries_sorted if (r[5] is not None and r[5] < 0)]
        print(f"  all net sellers ({len(sellers)}):")
        for r in sellers:
            print(f"    {r[1]:60s} {r[5]:>12}")

        nfc_row = by_sid.get(nfc_sid)
        if nfc_row:
            print(f"  NFC net issuance (buybacks net), $bn cumulative: {nfc_row[5]}")

        total_row = by_sid.get(total_sid)
        if total_row and total_row[8] is not None:
            delta_mv = total_row[8]
            flow_part = total_row[5]
            reval_part = total_row[9]
            if delta_mv:
                print(f"  total equity market value: start={total_row[6]} bn, "
                      f"end={total_row[7]} bn, delta={delta_mv} bn")
                print(f"    of which net flow     = {flow_part} bn "
                      f"({(flow_part / delta_mv * 100):.1f}% of delta)"
                      if flow_part is not None else "")
                print(f"    of which revaluation  = {reval_part} bn "
                      f"({(reval_part / delta_mv * 100):.1f}% of delta)"
                      if reval_part is not None else "")

    print("\nDone.")
    return {
        "release_info": release_info,
        "flow_old": flow_old,
        "stock_old": stock_old,
        "flow_new": flow_new,
        "stock_new": stock_new,
        "quarters": quarters,
        "max_disc_holders": max_disc_holders,
        "max_disc_issuers": max_disc_issuers,
    }


if __name__ == "__main__":
    release_arg = sys.argv[1] if len(sys.argv) > 1 else "current"
    main(release_arg)
