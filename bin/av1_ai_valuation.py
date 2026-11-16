#!/usr/bin/env python3
"""AV1: are share prices ahead of AI earnings? Registered statement AV1-P1 (version 2 of the spec).
Python 3 standard library plus xlrd (and openpyxl via the imported CV1-P6 BTOS code).

  python3 bin/av1_ai_valuation.py selftest                 # synthetic data only; no network
  python3 bin/av1_ai_valuation.py fetch                    # NYU Stern Damodaran .xls files (10 GETs, 3 s apart)
  python3 bin/av1_ai_valuation.py build [--out DIR]        # offline; writes registered.csv FIRST, then computes every statistic

Specification: _research/2026-11-16-AV1-AI-Valuation-Spec.md ("Version 2" governs; its sha256 is pinned in SPEC_SHA256 below and the build refuses to score if the file differs).
Outputs: data/av1_ai_valuation/ (registered.csv, scores.csv, detail.csv, vintages.csv, README.md). Raw downloads: data/vintages/av1/ (gitignored, never committed).
The BTOS sector AI-use means (2024-25, 46 cycles) come from bin/aj1_ai_jobs.py (load_btos_inputs, imported, not copied).

WHAT TOUCHES THE NETWORK. Only `fetch`. pages.stern.nyu.edu/~adamodar/pc/archives/ and datasets/ only (plain HTTPS GET, no key, no contact details); User-Agent is the neutral string fixed in cv1_confidence_velocity.py.
Any HTTP != 200 or body without OLE2 magic bytes (D0 CF 11 E0) writes data/vintages/av1/STOP.txt and exits non-zero.
"""
import argparse
import csv
import math
import os
import random
import re
import statistics
import sys
import tempfile
import time
import urllib.error
import urllib.request

import xlrd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv1_confidence_velocity as cv1                          # noqa: E402
import aj1_ai_jobs as aj1                                      # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_FILE = "_research/2026-11-16-AV1-AI-Valuation-Spec.md"
SPEC_SHA256 = "c8b3f868d1ad9525aad9307934d29f480c5315e36f0cf8ec9f500559d4d526da"
OUT_REL = "data/av1_ai_valuation"
CACHE_REL = "data/vintages/av1"

Refused = cv1.Refused
Stop = cv1.Stop
sha256_of = cv1.sha256_of
now_utc = cv1.now_utc
write_text = cv1.write_text
write_bytes = cv1.write_bytes
csv_line = cv1.csv_line
spearman = cv1.spearman
UA = cv1.UA
Checks = cv1.Checks
mc_se_at = aj1.mc_se_at
load_btos_inputs = aj1.load_btos_inputs

GAP_SECONDS = 3.0
TIMEOUT = 120
OLE2_MAGIC = b"\xd0\xcf\x11\xe0"

PERM_SEED = 20261116
N_PERM = 100000
ALPHA = 0.05

ARCHIVES_BASE = "https://pages.stern.nyu.edu/~adamodar/pc/archives/"
DATASETS_BASE = "https://pages.stern.nyu.edu/~adamodar/pc/datasets/"

# (key, local_rel, url, expected_ym)
FILES = (
    ("pedata16", "raw/pedata16.xls", ARCHIVES_BASE + "pedata16.xls", (2017, 1)),
    ("pedata19", "raw/pedata19.xls", ARCHIVES_BASE + "pedata19.xls", (2020, 1)),
    ("pedata21", "raw/pedata21.xls", ARCHIVES_BASE + "pedata21.xls", (2022, 1)),
    ("pedata22", "raw/pedata22.xls", ARCHIVES_BASE + "pedata22.xls", (2023, 1)),
    ("pedata23", "raw/pedata23.xls", ARCHIVES_BASE + "pedata23.xls", (2024, 1)),
    ("pedata_current", "raw/pedata_current.xls", DATASETS_BASE + "pedata.xls", (2026, 1)),
    ("DollarUS21", "raw/DollarUS21.xls", ARCHIVES_BASE + "DollarUS21.xls", (2022, 1)),
    ("DollarUS22", "raw/DollarUS22.xls", ARCHIVES_BASE + "DollarUS22.xls", (2023, 1)),
    ("DollarUS23", "raw/DollarUS23.xls", ARCHIVES_BASE + "DollarUS23.xls", (2024, 1)),
    ("DollarUS_current", "raw/DollarUS_current.xls", DATASETS_BASE + "DollarUS.xls", (2026, 1)),
)
EXPECTED_YM = {k: ym for k, _rel, _url, ym in FILES}

AI_COMPLEX = (
    "Semiconductor",
    "Semiconductor Equip",
    "Software (System & Application)",
    "Software (Internet)",
    "Computer Services",
    "Computers/Peripherals",
    "Telecom. Equipment",
)
AI_BUILDOUT = (
    "Power",
    "Utility (General)",
    "Electrical Equipment",
    "Engineering/Construction",
)
EXCLUDED_INDUSTRIES = frozenset((
    "Total Market",
    "Total Market (without financials)",
    "Diversified",
))

COL_INDUSTRY = "Industry"
INDUSTRY_HEADERS = ("Industry Name", "Industry")  # real files say "Industry Name" (supervisor fix, 16 Nov)
COL_NUM_FIRMS = "Number of firms"
COL_MKT_CAP = "Market Cap"
COL_NET_INCOME = "Net Income"
COL_PE_ALL = "Aggregate Mkt Cap/ Net Income (all firms)"
COL_PE_MM = "Aggregate Mkt Cap/ Trailing Net Income (only money making firms)"

# Fixed Damodaran industry -> 2-digit NAICS sector table for BTOS Spearman (reported only)
NAICS_BY_SECTOR = {
    "23": ("Engineering/Construction", "Homebuilding"),
    "31": (
        "Aerospace/Defense", "Apparel", "Auto & Truck", "Auto Parts", "Beverage (Alcoholic)",
        "Beverage (Soft)", "Building Materials", "Chemical (Basic)", "Chemical (Diversified)",
        "Chemical (Specialty)", "Computers/Peripherals", "Construction Supplies",
        "Drugs (Biotechnology)", "Drugs (Pharmaceutical)", "Electrical Equipment",
        "Electronics (Consumer & Office)", "Electronics (General)", "Food Processing",
        "Furn/Home Furnishings", "Healthcare Products", "Household Products", "Machinery",
        "Packaging & Container", "Paper/Forest Products", "Rubber& Tires", "Semiconductor",
        "Semiconductor Equip", "Shipbuilding & Marine", "Shoe", "Steel",
        "Telecom. Equipment", "Tobacco",
    ),
    "42": ("Food Wholesalers", "Retail (Distributors)"),
    "44": (
        "Retail (Automotive)", "Retail (Building Supply)", "Retail (General)",
        "Retail (Grocery and Food)", "Retail (Special Lines)",
    ),
    "48": ("Air Transport", "Transportation", "Transportation (Railroads)", "Trucking"),
    "51": (
        "Broadcasting", "Cable TV", "Publishing & Newspapers", "Software (Entertainment)",
        "Software (Internet)", "Software (System & Application)", "Telecom (Wireless)",
        "Telecom. Services",
    ),
    "52": (
        "Bank (Money Center)", "Banks (Regional)", "Brokerage & Investment Banking",
        "Financial Svcs. (Non-bank & Insurance)", "Insurance (General)", "Insurance (Life)",
        "Insurance (Prop/Cas.)", "Investments & Asset Management", "Reinsurance",
    ),
    "53": (
        "R.E.I.T.", "Real Estate (Development)", "Real Estate (General/Diversified)",
        "Real Estate (Operations & Services)", "Retail (REITs)",
    ),
    "54": ("Advertising", "Computer Services"),
    "56": ("Environmental & Waste Services",),
    "61": ("Education",),
    "62": ("Hospitals/Healthcare Facilities",),
    "72": ("Hotel/Gaming", "Restaurant/Dining"),
}
INDUSTRY_TO_NAICS = {ind: sec for sec, inds in NAICS_BY_SECTOR.items() for ind in inds}

REG_HEADER = (
    "statement_id", "version", "superseded", "scored", "statement", "statistic",
    "support_if", "against_if", "treatment_window", "placebo_window", "prereg_sha256",
)
SCORES_HEADER = ("statement_id", "label", "primary_statistic", "primary_value", "unit", "statistics", "denominators", "caveats")
DETAIL_HEADER = ("statement_id", "item", "value", "unit")
VINTAGES_HEADER = ("source", "key", "url", "fetched_utc", "status", "bytes", "sha256", "note")
LABELS = ("SUPPORT", "AGAINST", "INCONCLUSIVE")
COMMITTED = ("README.md", "registered.csv", "scores.csv", "detail.csv", "vintages.csv")
IDS = ("AV1-P1",)

MONTH_MAP = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12,
}


def cache_dir(root=None):
    return os.path.join(root or ROOT, *CACHE_REL.split("/"))


def out_dir(root=None):
    return os.path.join(root or ROOT, *OUT_REL.split("/"))


def norm_ws(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def stop_with(cache, reason):
    write_text(os.path.join(cache, "STOP.txt"), reason + "\n")
    raise Stop(reason)


def read_manifest(cache):
    p = os.path.join(cache, "manifest.csv")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


# ------------------------------------------------------------------------------------------------------------------------
# fetch (plain HTTPS GET, no key, no contact details)
# ------------------------------------------------------------------------------------------------------------------------
class HttpFetcher(object):
    """Plain HTTPS GET fetcher. `opener` is injectable for the selftest."""

    def __init__(self, opener=None):
        self.opener = opener or urllib.request.build_opener()

    def get(self, url, headers):
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with self.opener.open(req, timeout=TIMEOUT) as resp:
                return resp.status, resp.read(), dict(resp.headers)
        except urllib.error.HTTPError as e:
            return e.code, e.read() if hasattr(e, "read") else b"", dict(e.headers or {})


def cmd_fetch(root=None, fetcher=None, sleep=time.sleep):
    cache = cache_dir(root)
    os.makedirs(cache, exist_ok=True)
    stop_path = os.path.join(cache, "STOP.txt")
    if os.path.exists(stop_path):
        raise Stop("STOP.txt present in %s; review and delete manually before retrying" % CACHE_REL)
    for _key, rel, _url, _ym in FILES:
        if os.path.exists(os.path.join(cache, *rel.split("/"))):
            raise Refused("raw file %s already exists in %s (no refetch)" % (rel, CACHE_REL))
    f = fetcher or HttpFetcher()
    headers = {"User-Agent": UA}
    mp = os.path.join(cache, "manifest.csv")
    for idx, (key, rel, url, _ym) in enumerate(FILES):
        if idx > 0:
            sleep(GAP_SECONDS)
        status, body, _hdrs = f.get(url, headers)
        if status != 200:
            stop_with(cache, "%s: HTTP status %s (expected 200)" % (key, status))
        if not isinstance(body, (bytes, bytearray)) or body[:4] != OLE2_MAGIC:
            stop_with(cache, "%s: response body is not an OLE2 .xls file (magic bytes mismatch)" % key)
        write_bytes(os.path.join(cache, *rel.split("/")), bytes(body))
        new = not os.path.exists(mp)
        with open(mp, "a", encoding="utf-8", newline="") as fh:
            if new:
                fh.write("key,url,fetched_utc,status,bytes,sha256\n")
            fh.write(csv_line([key, url, now_utc(), status, len(body), sha256_of(body)]))
        print("%s: fetched %d bytes, sha256 %s" % (key, len(body), sha256_of(body)))
    return 0


# ------------------------------------------------------------------------------------------------------------------------
# xls reading, date & definition checks
# ------------------------------------------------------------------------------------------------------------------------
def _parse_date_text(text):
    s = norm_ws(text)
    if not s:
        return None
    # Match Month [Day,] Year or Day Month Year
    m = re.search(r"\b([A-Za-z]+)\s+(?:\d{1,2}\s*,?\s*)?((?:19|20)\d{2})\b", s)
    if m and m.group(1).lower() in MONTH_MAP:
        return int(m.group(2)), MONTH_MAP[m.group(1).lower()]
    m = re.search(r"\b\d{1,2}\s+([A-Za-z]+)\s*,?\s*((?:19|20)\d{2})\b", s)
    if m and m.group(1).lower() in MONTH_MAP:
        return int(m.group(2)), MONTH_MAP[m.group(1).lower()]
    m = re.search(r"\b((?:19|20)\d{2})[-/](\d{1,2})(?:[-/]\d{1,2})?\b", s)
    if m:
        yr, mo = int(m.group(1)), int(m.group(2))
        if 1 <= mo <= 12:
            return yr, mo
    m = re.search(r"\b(\d{1,2})/(\d{1,2})/((?:19|20)\d{2})\b", s)
    if m:
        mo, yr = int(m.group(1)), int(m.group(3))
        if 1 <= mo <= 12:
            return yr, mo
    return None


def _extract_date_updated(sheet, datemode):
    """Find 'Date updated' cell in `sheet` and return (year, month) or None."""
    for r in range(min(sheet.nrows, 25)):
        for c in range(sheet.ncols):
            cell = sheet.cell(r, c)
            if cell.ctype != xlrd.XL_CELL_TEXT:
                continue
            txt = norm_ws(cell.value)
            if "date updated" not in txt.lower():
                continue
            # Same cell may contain the date after a colon
            after = re.sub(r"^.*?date\s+updated\s*:?\s*", "", txt, flags=re.I)
            if after and after != txt:
                ym = _parse_date_text(after)
                if ym is not None:
                    return ym
            # Otherwise look rightwards in the same row
            for c2 in range(c + 1, sheet.ncols):
                c2_cell = sheet.cell(r, c2)
                if c2_cell.ctype == xlrd.XL_CELL_EMPTY:
                    continue
                if c2_cell.ctype == xlrd.XL_CELL_DATE:
                    yr, mo, _d, _h, _m, _s = xlrd.xldate_as_tuple(c2_cell.value, datemode)
                    return yr, mo
                if c2_cell.ctype == xlrd.XL_CELL_TEXT:
                    ym = _parse_date_text(c2_cell.value)
                    if ym is not None:
                        return ym
    return None


def _parse_num(val):
    if isinstance(val, bool):
        return None
    if isinstance(val, (int, float)):
        f = float(val)
        return f if math.isfinite(f) else None
    if isinstance(val, str):
        s = norm_ws(val).replace(",", "")
        if not s:
            return None
        try:
            f = float(s)
            return f if math.isfinite(f) else None
        except ValueError:
            return None
    return None


def _extract_var_faq_defs(wb):
    """Return {'Market Cap': text, 'Net Income': text} from 'Variables & FAQ' sheet."""
    if "Variables & FAQ" not in wb.sheet_names():
        return {}
    sh = wb.sheet_by_name("Variables & FAQ")
    defs = {}
    targets = {"market cap": "Market Cap", "net income": "Net Income"}
    for r in range(sh.nrows):
        cells = [norm_ws(sh.cell_value(r, c)) for c in range(sh.ncols)]
        non_empty = [x for x in cells if x]
        if len(non_empty) < 2:
            continue
        head = non_empty[0].rstrip(":").strip().lower()
        if head in targets and targets[head] not in defs:
            defs[targets[head]] = " ".join(non_empty[1:])
    return defs


def read_xls_file(path):
    """Read one Damodaran .xls file via xlrd.
    Returns dict: {date_ym, headers, rows_by_industry, faq_defs}.
    """
    wb = xlrd.open_workbook(path)
    names = wb.sheet_names()
    if "Industry Averages" in names:
        sh = wb.sheet_by_name("Industry Averages")
    elif len(names) == 1:
        sh = wb.sheet_by_index(0)
    else:
        raise Refused("%s: neither 'Industry Averages' nor single-sheet workbook (%s)" % (os.path.basename(path), names))

    date_ym = _extract_date_updated(sh, wb.datemode)
    header_row = None
    for r in range(sh.nrows):
        for c in range(sh.ncols):
            if norm_ws(sh.cell_value(r, c)) in INDUSTRY_HEADERS:
                header_row = r
                break
        if header_row is not None:
            break
    if header_row is None:
        raise Refused("%s: header row with 'Industry' cell not found" % os.path.basename(path))

    col_map = {}
    for c in range(sh.ncols):
        h = norm_ws(sh.cell_value(header_row, c))
        # dollar files carry units in the header (supervisor fix, 16 Nov)
        if h.startswith("Market Cap ("):
            h = COL_MKT_CAP
        elif h.startswith("Net Income (") or h.startswith("Net Income("):
            h = COL_NET_INCOME
        elif h == "Aggregate Mkt Cap/ Net Income":  # pedata16 header, no suffix
            h = COL_PE_ALL
        elif h == "Aggregate Mkt Cap/ Trailing Net Income":
            h = COL_PE_MM
        if h and h not in col_map:
            col_map[h] = c
    ind_key = next(h for h in INDUSTRY_HEADERS if h in col_map)
    ind_col = col_map[ind_key]

    rows = {}
    for r in range(header_row + 1, sh.nrows):
        ind = norm_ws(sh.cell_value(r, ind_col))
        if not ind:
            continue
        rec = {}
        for h, c in col_map.items():
            if h in INDUSTRY_HEADERS:
                continue
            rec[h] = _parse_num(sh.cell_value(r, c))
        rows[ind] = rec

    return {
        "date_ym": date_ym,
        "headers": list(col_map.keys()),
        "rows": rows,
        "faq_defs": _extract_var_faq_defs(wb),
    }


def load_cached_damodaran(root=None, reader=None):
    """Load and validate all 10 cached Damodaran files. Calls stop_with on date or definition mismatch."""
    cache = cache_dir(root)
    stop_path = os.path.join(cache, "STOP.txt")
    if os.path.exists(stop_path):
        raise Refused("STOP.txt present in %s; resolve before building" % CACHE_REL)
    read_fn = reader or read_xls_file
    data = {}
    for key, rel, _url, expected_ym in FILES:
        p = os.path.join(cache, *rel.split("/"))
        if not os.path.exists(p):
            raise Refused("missing cached file %s (run fetch)" % rel)
        parsed = read_fn(p)
        if parsed["date_ym"] != expected_ym:
            stop_with(cache, "%s: Date updated is %r, expected %r" % (key, parsed["date_ym"], expected_ym))
        data[key] = parsed

    # Ruling 6: check Market Cap and Net Income definition text between DollarUS22 and DollarUS_current
    d22 = data["DollarUS22"].get("faq_defs") or {}
    dcur = data["DollarUS_current"].get("faq_defs") or {}
    for term in (COL_MKT_CAP, COL_NET_INCOME):
        if term not in d22 or term not in dcur:
            stop_with(cache, "Variables & FAQ definition for %r missing in DollarUS22 or DollarUS_current" % term)
        if d22[term] != dcur[term]:
            stop_with(cache, "Variables & FAQ definition for %r differs between DollarUS22 and DollarUS_current" % term)

    return data


# ------------------------------------------------------------------------------------------------------------------------
# statistics: pooled measure, permutation test, version-2 label rule, reported items
# ------------------------------------------------------------------------------------------------------------------------
def _select_dollar_pair(f0, f1, group_set):
    """Select industries present with numeric Market Cap and Net Income in both dollar files."""
    all_names = sorted(set(f0["rows"].keys()) | set(f1["rows"].keys()))
    kept = []
    dropped = []
    for ind in all_names:
        if ind in EXCLUDED_INDUSTRIES:
            dropped.append((ind, "excluded (%s)" % ind))
            continue
        r0 = f0["rows"].get(ind)
        r1 = f1["rows"].get(ind)
        if r0 is None or r1 is None:
            dropped.append((ind, "missing at %s" % ("t0" if r0 is None else "t1")))
            continue
        mc0, ni0 = r0.get(COL_MKT_CAP), r0.get(COL_NET_INCOME)
        mc1, ni1 = r1.get(COL_MKT_CAP), r1.get(COL_NET_INCOME)
        if mc0 is None or ni0 is None or mc1 is None or ni1 is None:
            dropped.append((ind, "missing or non-numeric Market Cap / Net Income"))
            continue
        kept.append((ind, mc0, ni0, mc1, ni1))
    group_kept = [x for x in kept if x[0] in group_set]
    other_kept = [x for x in kept if x[0] not in group_set]
    return kept, group_kept, other_kept, dropped


def _pool_stats(items):
    """Compute sums, M(P,t), delta_M, and price/earnings legs for a list of (ind, mc0, ni0, mc1, ni1)."""
    mc0_sum = sum(x[1] for x in items)
    ni0_sum = sum(x[2] for x in items)
    mc1_sum = sum(x[3] for x in items)
    ni1_sum = sum(x[4] for x in items)
    valid = mc0_sum > 0 and ni0_sum > 0 and mc1_sum > 0 and ni1_sum > 0
    if not valid:
        return {
            "valid": False,
            "mc0_sum": mc0_sum, "ni0_sum": ni0_sum,
            "mc1_sum": mc1_sum, "ni1_sum": ni1_sum,
            "M0": None, "M1": None, "delta_M": None,
            "price_leg": math.log(mc1_sum / mc0_sum) if (mc0_sum > 0 and mc1_sum > 0) else None,
            "earnings_leg": math.log(ni1_sum / ni0_sum) if (ni0_sum > 0 and ni1_sum > 0) else None,
            "n": len(items),
            "members": [x[0] for x in items],
        }
    m0 = math.log(mc0_sum / ni0_sum)
    m1 = math.log(mc1_sum / ni1_sum)
    return {
        "valid": True,
        "mc0_sum": mc0_sum, "ni0_sum": ni0_sum,
        "mc1_sum": mc1_sum, "ni1_sum": ni1_sum,
        "M0": m0, "M1": m1, "delta_M": m1 - m0,
        "price_leg": math.log(mc1_sum) - math.log(mc0_sum),
        "earnings_leg": math.log(ni1_sum) - math.log(ni0_sum),
        "n": len(items),
        "members": [x[0] for x in items],
    }


def _perm_pooled(kept, k_size, g_obs, seed=PERM_SEED, nperm=N_PERM):
    """Permutation test reassigning the AI label to `k_size` of `kept` industries."""
    n = len(kept)
    mc0 = [x[1] for x in kept]
    ni0 = [x[2] for x in kept]
    mc1 = [x[3] for x in kept]
    ni1 = [x[4] for x in kept]
    tot_mc0, tot_ni0, tot_mc1, tot_ni1 = sum(mc0), sum(ni0), sum(mc1), sum(ni1)

    rng = random.Random(seed)
    idx_range = range(n)
    ge = le = undef = 0
    for _ in range(nperm):
        draw = rng.sample(idx_range, k_size)
        a_mc0 = a_ni0 = a_mc1 = a_ni1 = 0.0
        for j in draw:
            a_mc0 += mc0[j]
            a_ni0 += ni0[j]
            a_mc1 += mc1[j]
            a_ni1 += ni1[j]
        o_mc0 = tot_mc0 - a_mc0
        o_ni0 = tot_ni0 - a_ni0
        o_mc1 = tot_mc1 - a_mc1
        o_ni1 = tot_ni1 - a_ni1
        if not (a_mc0 > 0 and a_ni0 > 0 and a_mc1 > 0 and a_ni1 > 0 and o_mc0 > 0 and o_ni0 > 0 and o_mc1 > 0 and o_ni1 > 0):
            undef += 1
            continue
        dm_a = math.log(a_mc1 / a_ni1) - math.log(a_mc0 / a_ni0)
        dm_o = math.log(o_mc1 / o_ni1) - math.log(o_mc0 / o_ni0)
        g_p = dm_a - dm_o
        diff = round(g_p - g_obs, 9)
        if diff >= 0:
            ge += 1
        if diff <= 0:
            le += 1
    return {
        "p_pos": (1.0 + ge) / (nperm + 1.0),
        "p_neg": (1.0 + le) / (nperm + 1.0),
        "undefined_draws": undef,
        "nperm": nperm,
        "seed": seed,
    }


def _check_tail(dm_ai, g, p, tail, alpha=ALPHA, nperm=N_PERM):
    se = mc_se_at(alpha, nperm)
    p_ok = round(p, 9) <= alpha and abs(p - alpha) > 2.0 * se
    if tail == "pos":
        return round(dm_ai, 9) > 0 and round(g, 9) > 0 and p_ok
    return round(dm_ai, 9) < 0 and round(g, 9) < 0 and p_ok


def run_av1_p1(f0, f1, seed=PERM_SEED, nperm=N_PERM):
    """Compute AV1-P1 (version 2) pooled statistic, permutation p, leave-one-outs, and label."""
    kept, ai_kept, other_kept, dropped = _select_dollar_pair(f0, f1, set(AI_COMPLEX))
    ai_pool = _pool_stats(ai_kept)
    other_pool = _pool_stats(other_kept)
    k = len(ai_kept)

    if not (ai_pool["valid"] and other_pool["valid"]):
        return {
            "kept": kept, "dropped": dropped,
            "ai_pool": ai_pool, "other_pool": other_pool,
            "K": k, "G": None, "p_pos": None, "p_neg": None,
            "undefined_draws": None, "loo": [],
            "label": "INCONCLUSIVE",
            "nonpositive_pool": True,
            "nperm": nperm, "seed": seed,
        }

    g_obs = ai_pool["delta_M"] - other_pool["delta_M"]
    perm = _perm_pooled(kept, k, g_obs, seed=seed, nperm=nperm)

    loo = []
    if k >= 2:
        for item in ai_kept:
            ind_left_out = item[0]
            kept_loo = [x for x in kept if x[0] != ind_left_out]
            ai_loo_items = [x for x in ai_kept if x[0] != ind_left_out]
            ai_loo = _pool_stats(ai_loo_items)
            if not ai_loo["valid"]:
                loo.append({
                    "without": ind_left_out, "valid": False,
                    "delta_M_ai": None, "G": None, "p_pos": None, "p_neg": None,
                    "pos_ok": False, "neg_ok": False,
                })
                continue
            g_loo = ai_loo["delta_M"] - other_pool["delta_M"]
            p_loo = _perm_pooled(kept_loo, k - 1, g_loo, seed=seed, nperm=nperm)
            loo.append({
                "without": ind_left_out, "valid": True,
                "delta_M_ai": ai_loo["delta_M"], "G": g_loo,
                "p_pos": p_loo["p_pos"], "p_neg": p_loo["p_neg"],
                "pos_ok": _check_tail(ai_loo["delta_M"], g_loo, p_loo["p_pos"], "pos", ALPHA, nperm),
                "neg_ok": _check_tail(ai_loo["delta_M"], g_loo, p_loo["p_neg"], "neg", ALPHA, nperm),
            })

    if k < len(AI_COMPLEX):
        label = "INCONCLUSIVE"
    elif _check_tail(ai_pool["delta_M"], g_obs, perm["p_pos"], "pos", ALPHA, nperm) and loo and all(x["pos_ok"] for x in loo):
        label = "SUPPORT"
    elif _check_tail(ai_pool["delta_M"], g_obs, perm["p_neg"], "neg", ALPHA, nperm) and loo and all(x["neg_ok"] for x in loo):
        label = "AGAINST"
    else:
        label = "INCONCLUSIVE"

    return {
        "kept": kept, "dropped": dropped,
        "ai_pool": ai_pool, "other_pool": other_pool,
        "K": k, "G": g_obs,
        "p_pos": perm["p_pos"], "p_neg": perm["p_neg"],
        "undefined_draws": perm["undefined_draws"],
        "loo": loo,
        "label": label,
        "nonpositive_pool": False,
        "nperm": nperm, "seed": seed,
    }


def _pe_delta_m(files, col_name, group_set):
    """Compute equal-weighted mean and median of ln(PE_end) - ln(PE_start) across `files` = (f0, f1) or (f16, f19, f22, fcur)."""
    all_names = sorted(set().union(*(f["rows"].keys() for f in files)))
    kept_vals = {}
    dropped = []
    for ind in all_names:
        if ind in EXCLUDED_INDUSTRIES:
            dropped.append((ind, "excluded (%s)" % ind))
            continue
        vals = []
        reason = None
        for idx, f in enumerate(files):
            r = f["rows"].get(ind)
            if r is None:
                reason = "missing at file %d" % idx
                break
            v = r.get(col_name)
            if v is None or v <= 0:
                reason = "non-positive or non-numeric %s at file %d" % (col_name, idx)
                break
            vals.append(math.log(v))
        if reason is not None:
            dropped.append((ind, reason))
            continue
        if len(files) == 2:
            kept_vals[ind] = vals[1] - vals[0]
        elif len(files) == 4:
            kept_vals[ind] = (vals[3] - vals[2]) - (vals[1] - vals[0])
        else:
            raise ValueError("expected 2 or 4 files")

    ai_vals = [kept_vals[i] for i in sorted(kept_vals) if i in group_set]
    other_vals = [kept_vals[i] for i in sorted(kept_vals) if i not in group_set]
    ai_members = [i for i in sorted(kept_vals) if i in group_set]
    other_members = [i for i in sorted(kept_vals) if i not in group_set]

    return {
        "kept_map": kept_vals,
        "dropped": dropped,
        "ai_members": ai_members,
        "other_members": other_members,
        "ai_mean": statistics.mean(ai_vals) if ai_vals else None,
        "other_mean": statistics.mean(other_vals) if other_vals else None,
        "diff_mean": (statistics.mean(ai_vals) - statistics.mean(other_vals)) if (ai_vals and other_vals) else None,
        "ai_median": statistics.median(ai_vals) if ai_vals else None,
        "other_median": statistics.median(other_vals) if other_vals else None,
        "diff_median": (statistics.median(ai_vals) - statistics.median(other_vals)) if (ai_vals and other_vals) else None,
    }


def _reported_pooled(f0, f1, group_set):
    kept, grp_kept, oth_kept, dropped = _select_dollar_pair(f0, f1, group_set)
    grp = _pool_stats(grp_kept)
    oth = _pool_stats(oth_kept)
    g = (grp["delta_M"] - oth["delta_M"]) if (grp["valid"] and oth["valid"]) else None
    return {"group": grp, "other": oth, "G": g, "kept": kept, "dropped": dropped}


def _btos_spearman(pe_post, sec_2425, ncycles=46):
    """Reported-only Spearman of BTOS 2024-25 sector AI mean vs PE delta_m_post (Jan 2023 -> Jan 2026)."""
    kept_map = pe_post["kept_map"]
    all_inds = sorted(set(kept_map.keys()) | set(INDUSTRY_TO_NAICS.keys()))
    members, xs, ys, pairs = [], [], [], []
    dropped = []
    for ind in sorted(kept_map.keys()):
        sec = INDUSTRY_TO_NAICS.get(ind)
        if sec is None:
            dropped.append((ind, "not in fixed Damodaran->NAICS table"))
            continue
        b = sec_2425.get(sec)
        if b is None or len(b.get("used", [])) < ncycles:
            dropped.append((ind, "BTOS sector %s lacks %d-cycle mean" % (sec, ncycles)))
            continue
        members.append(ind)
        xs.append(b["mean"])
        ys.append(kept_map[ind])
        pairs.append((ind, sec, b["mean"], kept_map[ind]))
    rho = spearman(xs, ys) if len(members) >= 3 else None
    return {
        "rho": rho,
        "n": len(members),
        "members": members,
        "pairs": pairs,
        "dropped": dropped,
    }


def compute(damodaran, btos, seed=PERM_SEED, nperm=N_PERM):
    """Pure computation of all AV1 version-2 primary and reported statistics. No files, no network."""
    p1 = run_av1_p1(damodaran["DollarUS22"], damodaran["DollarUS_current"], seed=seed, nperm=nperm)
    v1_p1 = _pe_delta_m((damodaran["pedata22"], damodaran["pedata_current"]), COL_PE_ALL, set(AI_COMPLEX))
    v1_p2 = _pe_delta_m(
        (damodaran["pedata16"], damodaran["pedata19"], damodaran["pedata22"], damodaran["pedata_current"]),
        COL_PE_ALL,
        set(AI_COMPLEX),
    )
    mm = _pe_delta_m((damodaran["pedata22"], damodaran["pedata_current"]), COL_PE_MM, set(AI_COMPLEX))
    base_2022 = _reported_pooled(damodaran["DollarUS21"], damodaran["DollarUS_current"], set(AI_COMPLEX))
    win_2024 = _reported_pooled(damodaran["DollarUS23"], damodaran["DollarUS_current"], set(AI_COMPLEX))
    buildout = _reported_pooled(damodaran["DollarUS22"], damodaran["DollarUS_current"], set(AI_BUILDOUT))

    firm_counts = {}
    for ind in AI_COMPLEX:
        r23 = damodaran["DollarUS22"]["rows"].get(ind, {})
        r26 = damodaran["DollarUS_current"]["rows"].get(ind, {})
        firm_counts[ind] = {
            "n23": r23.get(COL_NUM_FIRMS),
            "n26": r26.get(COL_NUM_FIRMS),
        }

    btos_sp = _btos_spearman(v1_p1, btos["sec_2425"])

    return {
        "P1": p1,
        "v1_P1": v1_p1,
        "v1_P2": v1_p2,
        "mm": mm,
        "base_2022": base_2022,
        "win_2024": win_2024,
        "buildout": buildout,
        "firm_counts": firm_counts,
        "btos_spearman": btos_sp,
        "nperm": nperm,
        "seed": seed,
    }


# ------------------------------------------------------------------------------------------------------------------------
# spec pinning & registered.csv
# ------------------------------------------------------------------------------------------------------------------------
def spec_text(root=None):
    return open(os.path.join(root or ROOT, *SPEC_FILE.split("/")), "rb").read()


def check_spec_hash(root=None, pinned=None):
    got = sha256_of(spec_text(root))
    if got != (pinned or SPEC_SHA256):
        raise Refused("the spec file hashes to %s, not the pinned %s: the build refuses to score" % (got, pinned or SPEC_SHA256))
    return got


def parse_spec_v2(text):
    """Parse the version-2 Statement table (after '**Statement (version 2).**')."""
    marker = text.find("**Statement (version 2).**")
    if marker < 0:
        raise Refused("the spec has no 'Statement (version 2)' section")
    rows = {}
    for line in text[marker:].splitlines():
        m = re.match(r"^\|\s*(AV1-P[0-9][^|]*)\|(.*)\|\s*$", line)
        if not m:
            continue
        cells = [c.strip().replace("**", "") for c in m.group(2).split("|")]
        if len(cells) != 4:
            raise Refused("version 2 table row %s does not have four cells" % m.group(1).strip())
        rows[m.group(1).strip()] = tuple(cells)
    if sorted(rows) != list(IDS):
        raise Refused("the version 2 table does not hold %s: %s" % (list(IDS), sorted(rows)))
    return rows


def write_registered(out, root=None, pinned=None):
    sha = check_spec_hash(root, pinned)
    rows = parse_spec_v2(spec_text(root).decode("utf-8"))
    body = []
    for i in IDS:
        st, stat, sup, ag = rows[i]
        body.append([i, "2", "no", "yes", st, stat, sup, ag, "January 2023 to January 2026", "none", sha])
    text = (
        "# source: %s (version 2 statement table), sha256 %s; written before any statistic is computed\n" % (SPEC_FILE, sha)
        + csv_line(REG_HEADER)
        + "".join(csv_line(r) for r in body)
    )
    path = os.path.join(out, "registered.csv")
    write_text(path, text)
    return path, sha


# ------------------------------------------------------------------------------------------------------------------------
# output rows
# ------------------------------------------------------------------------------------------------------------------------
def f4(x):
    return "n/a" if x is None else "%.4f" % x


def f6(x):
    return "n/a" if x is None else "%.6f" % x


def pstr(p):
    return "n/a" if p is None else "%.5f" % p


def make_rows(R):
    p1 = R["P1"]
    se = mc_se_at(ALPHA, R["nperm"])
    ai_p = p1["ai_pool"]
    oth_p = p1["other_pool"]

    loo_gs = [x["G"] for x in p1["loo"] if x["G"] is not None]
    loo_min_g = min(loo_gs) if loo_gs else None
    loo_max_g = max(loo_gs) if loo_gs else None

    caveat = (
        "SUPPORT says prices of the AI complex rose faster than its earnings, relative to other industries, and does not show the market is wrong "
        "(a higher multiple can be a correct forecast of earnings still to come, or a lower discount rate). AGAINST says the AI complex's earnings "
        "kept pace with or outran its prices over the window. Neither speaks to the level of the multiple, only to its change. Aggregate net income "
        "is GAAP and includes one-off items; AV1 tests seven named industries, not 'AI firms'."
    )
    stats_str = (
        "delta_M_ai=%s; delta_M_other=%s; perm_p_pos=%s; perm_p_neg=%s; loo_min_G=%s; loo_max_G=%s; "
        "permutations=%d; seed=%d; mc_se_at_0.05=%.6f"
    ) % (
        f4(ai_p["delta_M"]), f4(oth_p["delta_M"]), pstr(p1["p_pos"]), pstr(p1["p_neg"]),
        f4(loo_min_g), f4(loo_max_g), R["nperm"], R["seed"], se,
    )
    den_str = "K=%d; n_ai=%d; n_other=%d; members_ai=%s; DollarUS22->DollarUS_current (Jan 2023->Jan 2026); permutations=%d; seed=%d" % (
        p1["K"], ai_p["n"], oth_p["n"], ",".join(ai_p["members"]), R["nperm"], R["seed"]
    )
    scores = [["AV1-P1", p1["label"], "G_delta_M_ai_minus_other", f6(p1["G"]), "log points", stats_str, den_str, caveat]]

    detail = []
    d = detail.append
    d(["AV1-SEC", "date_check", "all 10 files matched expected year-month", "text"])
    d(["AV1-SEC", "faq_definition_check", "Market Cap and Net Income definitions match between DollarUS22 and DollarUS_current", "text"])
    d(["AV1-SEC", "ai_complex_kept_K", str(p1["K"]), "industries"])
    d(["AV1-SEC", "comparison_kept_n", str(oth_p["n"]), "industries"])
    d(["AV1-SEC", "dropped_count", str(len(p1["dropped"])), "industries"])
    d(["AV1-SEC", "dropped_list", "; ".join("%s (%s)" % (i, r) for i, r in p1["dropped"]), "text"])

    # AV1-P1 primary details
    within_pos = p1["p_pos"] is not None and abs(p1["p_pos"] - ALPHA) <= 2.0 * se
    within_neg = p1["p_neg"] is not None and abs(p1["p_neg"] - ALPHA) <= 2.0 * se
    for item, val, unit in (
        ("G", f6(p1["G"]), "log points"),
        ("delta_M_ai", f6(ai_p["delta_M"]), "log points"),
        ("delta_M_other", f6(oth_p["delta_M"]), "log points"),
        ("perm_p_pos", pstr(p1["p_pos"]), "probability"),
        ("perm_p_neg", pstr(p1["p_neg"]), "probability"),
        ("loo_min_G", f6(loo_min_g), "log points"),
        ("loo_max_G", f6(loo_max_g), "log points"),
        ("loo_all_pos_rule", str(bool(p1["loo"]) and all(x["pos_ok"] for x in p1["loo"])), "boolean"),
        ("loo_all_neg_rule", str(bool(p1["loo"]) and all(x["neg_ok"] for x in p1["loo"])), "boolean"),
        ("K", str(p1["K"]), "industries"),
        ("n_ai", str(ai_p["n"]), "industries"),
        ("n_other", str(oth_p["n"]), "industries"),
        ("members_ai", ",".join(ai_p["members"]), "list"),
        ("members_other", ",".join(oth_p["members"]), "list"),
        ("permutations", str(R["nperm"]), "count"),
        ("seed", str(R["seed"]), "integer"),
        ("mc_se_at_0.05", "%.6f" % se, "probability"),
        ("within_2_mc_se_of_0.05", "pos=%s;neg=%s" % (within_pos, within_neg), "boolean"),
        ("nonpositive_pool", str(p1["nonpositive_pool"]), "boolean"),
    ):
        d(["AV1-P1", item, val, unit])
    for x in p1["loo"]:
        slug = re.sub(r"[^A-Za-z0-9]+", "_", x["without"]).strip("_")
        d(["AV1-P1", "loo_without_%s_G" % slug, f6(x["G"]), "log points"])
        d(["AV1-P1", "loo_without_%s_delta_M_ai" % slug, f6(x["delta_M_ai"]), "log points"])
        d(["AV1-P1", "loo_without_%s_p_pos" % slug, pstr(x["p_pos"]), "probability"])
        d(["AV1-P1", "loo_without_%s_p_neg" % slug, pstr(x["p_neg"]), "probability"])

    # Reported: price and earnings legs for both pools
    for tag, pool in (("ai", ai_p), ("other", oth_p)):
        d(["AV1-R-LEGS", "%s_price_leg_dln_mkt_cap" % tag, f6(pool["price_leg"]), "log points"])
        d(["AV1-R-LEGS", "%s_earnings_leg_dln_net_income" % tag, f6(pool["earnings_leg"]), "log points"])
        d(["AV1-R-LEGS", "%s_delta_M" % tag, f6(pool["delta_M"]), "log points"])
        d(["AV1-R-LEGS", "%s_n" % tag, str(pool["n"]), "industries"])
        d(["AV1-R-LEGS", "%s_members" % tag, ",".join(pool["members"]), "list"])

    # Reported: PE-file equal-weighted items (v1 P1, v1 P2, money-making-firms)
    for sid, obj in (("AV1-R-V1-P1", R["v1_P1"]), ("AV1-R-V1-P2", R["v1_P2"]), ("AV1-R-MM", R["mm"])):
        d([sid, "ai_mean", f6(obj["ai_mean"]), "log points"])
        d([sid, "other_mean", f6(obj["other_mean"]), "log points"])
        d([sid, "diff_mean", f6(obj["diff_mean"]), "log points"])
        d([sid, "ai_median", f6(obj["ai_median"]), "log points"])
        d([sid, "other_median", f6(obj["other_median"]), "log points"])
        d([sid, "diff_median", f6(obj["diff_median"]), "log points"])
        d([sid, "n_ai", str(len(obj["ai_members"])), "industries"])
        d([sid, "members_ai", ",".join(obj["ai_members"]), "list"])
        d([sid, "n_other", str(len(obj["other_members"])), "industries"])
        d([sid, "members_other", ",".join(obj["other_members"]), "list"])
        d([sid, "dropped_count", str(len(obj["dropped"])), "industries"])
        d([sid, "dropped_list", "; ".join("%s (%s)" % (i, r) for i, r in obj["dropped"]), "text"])

    # Reported: alternative pooled windows & AI build-out group
    for sid, obj in (("AV1-R-2022", R["base_2022"]), ("AV1-R-2024", R["win_2024"]), ("AV1-R-BUILDOUT", R["buildout"])):
        grp, oth = obj["group"], obj["other"]
        d([sid, "G", f6(obj["G"]), "log points"])
        d([sid, "group_delta_M", f6(grp["delta_M"]), "log points"])
        d([sid, "group_price_leg", f6(grp["price_leg"]), "log points"])
        d([sid, "group_earnings_leg", f6(grp["earnings_leg"]), "log points"])
        d([sid, "other_delta_M", f6(oth["delta_M"]), "log points"])
        d([sid, "other_price_leg", f6(oth["price_leg"]), "log points"])
        d([sid, "other_earnings_leg", f6(oth["earnings_leg"]), "log points"])
        d([sid, "n_group", str(grp["n"]), "industries"])
        d([sid, "members_group", ",".join(grp["members"]), "list"])
        d([sid, "n_other", str(oth["n"]), "industries"])
        d([sid, "members_other", ",".join(oth["members"]), "list"])
        d([sid, "dropped_count", str(len(obj["dropped"])), "industries"])
        d([sid, "dropped_list", "; ".join("%s (%s)" % (i, r) for i, r in obj["dropped"]), "text"])

    # Reported: firm counts of AI-complex industries at both labelled dates
    d(["AV1-R-FIRM-COUNTS", "n", str(len(AI_COMPLEX)), "industries"])
    d(["AV1-R-FIRM-COUNTS", "members", ",".join(AI_COMPLEX), "list"])
    for ind in AI_COMPLEX:
        fc = R["firm_counts"][ind]
        slug = re.sub(r"[^A-Za-z0-9]+", "_", ind).strip("_")
        d(["AV1-R-FIRM-COUNTS", "%s_2023" % slug, "n/a" if fc["n23"] is None else str(int(round(fc["n23"]))), "firms"])
        d(["AV1-R-FIRM-COUNTS", "%s_2026" % slug, "n/a" if fc["n26"] is None else str(int(round(fc["n26"]))), "firms"])

    # Reported: BTOS-sector Spearman
    bs = R["btos_spearman"]
    d(["AV1-R-BTOS-SPEARMAN", "spearman_rho", f6(bs["rho"]), "rank correlation"])
    d(["AV1-R-BTOS-SPEARMAN", "n", str(bs["n"]), "industries"])
    d(["AV1-R-BTOS-SPEARMAN", "members", ",".join(bs["members"]), "list"])
    d(["AV1-R-BTOS-SPEARMAN", "dropped_count", str(len(bs["dropped"])), "industries"])
    d(["AV1-R-BTOS-SPEARMAN", "dropped_list", "; ".join("%s (%s)" % (i, r) for i, r in bs["dropped"]), "text"])
    for ind, sec, ai_mean, dm in bs["pairs"]:
        slug = re.sub(r"[^A-Za-z0-9]+", "_", ind).strip("_")
        d(["AV1-R-BTOS-SPEARMAN", "map_%s" % slug, "naics=%s;btos_ai=%.4f;delta_m_post=%.6f" % (sec, ai_mean, dm), "mapping"])

    return scores, detail


def vintage_rows(cache):
    rows = []
    last = {}
    for r in read_manifest(cache):
        last[r["key"]] = r
    for key, _rel, url, _ym in FILES:
        r = last.get(key)
        if r is None:
            raise Refused("manifest has no row for %s: run fetch" % key)
        rows.append(["nyu-stern-damodaran", key, url, r["fetched_utc"], r["status"], r["bytes"], r["sha256"], "Damodaran US industry .xls"])
    bp = os.path.join(cv1.cache_dir(), *cv1.BTOS_REL.split("/"))
    rows.append([
        "census-btos", "btos-ai-core-questions", cv1.BTOS_URL, "2026-11-15", "hand download",
        os.path.getsize(bp) if os.path.exists(bp) else 0, cv1.BTOS_SHA256,
        "AI Core Questions (Original), hash-pinned in bin/cv1_confidence_velocity.py; read through aj1_ai_jobs.load_btos_inputs",
    ])
    return rows


def no_leak(name, text):
    for bad in ("@", "/Users/", "/private/", "~/"):
        if bad in text:
            raise Refused("%s would contain %r" % (name, bad))


def table_text(source_line, header, rows):
    return "# source: %s\n" % source_line + csv_line(header) + "".join(csv_line(r) for r in rows)


# ------------------------------------------------------------------------------------------------------------------------
# README
# ------------------------------------------------------------------------------------------------------------------------
def readme_text(R, sha):
    p1 = R["P1"]
    ai_p, oth_p = p1["ai_pool"], p1["other_pool"]
    loo_gs = [x["G"] for x in p1["loo"] if x["G"] is not None]
    L = []
    a = L.append
    a("# AV1: are share prices ahead of AI earnings? (build of 16 Nov 2026)")
    a("")
    a("## What was asked")
    a("")
    a("Did the AI complex's pooled price-to-earnings multiple rise from January 2023 to January 2026, and by more than the rest of the "
      "US market's? Registered blind before any multiple, market value or earnings figure by industry was read "
      "(`%s`, version 2, sha256 `%s`)." % (SPEC_FILE, sha))
    a("")
    a("## Result table")
    a("")
    a("| statement | label | K (AI) | n (other) | G (log pts) | delta_M AI | delta_M other | p (positive) | p (negative) | LOO G range |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    a("| AV1-P1 (pooled multiple change Jan 2023 -> Jan 2026) | %s | %d | %d | %s | %s | %s | %s | %s | %s to %s |" % (
        p1["label"], p1["K"], oth_p["n"], f4(p1["G"]), f4(ai_p["delta_M"]), f4(oth_p["delta_M"]),
        pstr(p1["p_pos"]), pstr(p1["p_neg"]),
        f4(min(loo_gs)) if loo_gs else "n/a", f4(max(loo_gs)) if loo_gs else "n/a",
    ))
    a("")
    a("Rule (version 2): SUPPORT if K >= 7, delta_M(AI pool) > 0, G > 0, one-sided permutation p <= 0.05 (outside two Monte Carlo standard errors of 0.05), "
      "and every leave-one-out with K - 1 meets the same three conditions; AGAINST if K >= 7, delta_M(AI pool) < 0, G < 0, one-sided permutation p <= 0.05 "
      "(outside two Monte Carlo standard errors of 0.05), and every leave-one-out meets the same three conditions; otherwise INCONCLUSIVE. "
      "%d permutations reassigning the AI label to K kept industries, seed %d, p = (1 + k) / (%d + 1)." % (
          R["nperm"], R["seed"], R["nperm"]
      ))
    a("")
    a("## Asymmetry, universe, and definitions")
    a("")
    a("- **Asymmetry (version 2).** SUPPORT says prices of the AI complex rose faster than its earnings, relative to other industries: "
      "the pattern T6 predicts. It does not show the market is wrong; a higher multiple can be a correct forecast of earnings still to come, "
      "or a lower discount rate for those firms. AGAINST says the AI complex's earnings kept pace with or outran its prices over the window: "
      "the gains were being delivered, not only priced. Neither speaks to the level of the multiple, only to its change.")
    a("- **Seven named industries, not \"AI firms\" (ruling 3).** AV1 tests seven named industries (%s), not \"AI firms\": "
      "industry buckets hold non-AI business and the AI firms are not all in them. A frozen firm list needs firm-level values and is AV2." % ", ".join(AI_COMPLEX))
    a("- **Universe (ruling 10).** Damodaran's frame: firms classified by country of incorporation (the US), all listed firms with a market price, no size cut-off.")
    a("- **Earnings definition (ruling 6).** Aggregate net income of all firms in the group (GAAP, including one-off items); "
      "Damodaran's documentation says trailing data run through the third quarter of the prior year.")
    a("")
    a("## Reported, not labelled")
    a("")
    a("- **Price and earnings legs (Jan 2023 -> Jan 2026):** AI pool dln(Mkt Cap) = %s, dln(Net Income) = %s; "
      "comparison pool dln(Mkt Cap) = %s, dln(Net Income) = %s." % (
          f4(ai_p["price_leg"]), f4(ai_p["earnings_leg"]), f4(oth_p["price_leg"]), f4(oth_p["earnings_leg"])
      ))
    a("- **Version 1 P1 (PE files, equal-weighted):** diff mean = %s, diff median = %s (n_ai=%d, n_other=%d)." % (
        f4(R["v1_P1"]["diff_mean"]), f4(R["v1_P1"]["diff_median"]), len(R["v1_P1"]["ai_members"]), len(R["v1_P1"]["other_members"])
    ))
    a("- **Version 1 P2 (PE files, delta_m_post - delta_m_pre):** diff mean = %s, diff median = %s (n_ai=%d, n_other=%d)." % (
        f4(R["v1_P2"]["diff_mean"]), f4(R["v1_P2"]["diff_median"]), len(R["v1_P2"]["ai_members"]), len(R["v1_P2"]["other_members"])
    ))
    a("- **January 2022 baseline (DollarUS21 -> current):** G = %s; **January 2024 -> January 2026:** G = %s." % (
        f4(R["base_2022"]["G"]), f4(R["win_2024"]["G"])
    ))
    a("- **Money-making-firms multiple (PE files):** diff mean = %s, diff median = %s." % (
        f4(R["mm"]["diff_mean"]), f4(R["mm"]["diff_median"])
    ))
    a("- **AI build-out group (Power; Utility (General); Electrical Equipment; Engineering/Construction):** G = %s (n_group=%d, n_other=%d)." % (
        f4(R["buildout"]["G"]), R["buildout"]["group"]["n"], R["buildout"]["other"]["n"]
    ))
    a("- **BTOS-sector Spearman (2024-25 46-cycle sector AI vs PE delta_m_post):** rho = %s (n=%d)." % (
        f4(R["btos_spearman"]["rho"]), R["btos_spearman"]["n"]
    ))
    a("")
    a("## Files")
    a("")
    a("`registered.csv` (written before any statistic), `scores.csv`, `detail.csv`, `vintages.csv`, `README.md`. Raw `.xls` files stay in `%s` (gitignored)." % CACHE_REL)
    a("")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------------------------------
# build
# ------------------------------------------------------------------------------------------------------------------------
def run_build(root=None, out=None, reader=None, btos_loader=None):
    root = root or ROOT
    out = out or out_dir(root)
    cache = cache_dir(root)
    reg_path, sha = write_registered(out, root)
    reg_sha = sha256_of(open(reg_path, "rb").read())
    print("registered.csv written (spec sha256 %s; file sha256 %s)" % (sha, reg_sha), flush=True)
    damodaran = load_cached_damodaran(root, reader=reader)
    btos = (btos_loader or load_btos_inputs)(root)
    R = compute(damodaran, btos)
    scores, detail = make_rows(R)
    vint = vintage_rows(cache)
    src = "bin/av1_ai_valuation.py build; scores computed after registered.csv (sha256 %s) was written; spec %s sha256 %s; permutations %d seed %d" % (
        reg_sha, SPEC_FILE, sha, R["nperm"], R["seed"]
    )
    files = {
        "scores.csv": table_text(src, SCORES_HEADER, scores),
        "detail.csv": table_text(src, DETAIL_HEADER, detail),
        "vintages.csv": table_text("fetch manifest of the raw cache (%s); raw files are not committed" % CACHE_REL, VINTAGES_HEADER, vint),
        "README.md": readme_text(R, sha),
    }
    for name, text in files.items():
        no_leak(name, text)
    for name, text in files.items():
        write_text(os.path.join(out, name), text)
    for r in scores:
        print("%s  %s  %s=%s %s" % (r[0], r[1], r[2], r[3], r[4]))
    return R, scores


# ------------------------------------------------------------------------------------------------------------------------
# selftest: synthetic data only, no network
# ------------------------------------------------------------------------------------------------------------------------
class _FakeHttpFetcher(object):
    def __init__(self, handler):
        self.handler = handler
        self.calls = []

    def get(self, url, headers):
        self.calls.append((url, headers))
        return self.handler(len(self.calls) - 1, url, headers)


def _synth_btos():
    sec_vals = {
        "23": 2.4, "31": 14.0, "42": 3.9, "44": 4.2, "48": 2.1, "51": 20.9, "52": 9.6,
        "53": 9.4, "54": 16.2, "56": 6.1, "61": 12.2, "62": 7.0, "72": 1.9,
    }
    return {"sec_2425": {s: {"mean": v, "used": ["x"] * 46} for s, v in sec_vals.items()}}


def _synth_damodaran(ai_mult_jump=2.0):
    """Build synthetic parsed Damodaran tables for all 10 files (clearly synthetic numbers)."""
    industries = list(AI_COMPLEX) + list(AI_BUILDOUT) + [
        "Advertising", "Aerospace/Defense", "Air Transport", "Apparel", "Auto & Truck",
        "Bank (Money Center)", "Beverage (Soft)", "Broadcasting", "Chemical (Basic)",
        "Education", "Environmental & Waste Services", "Food Processing", "Homebuilding",
        "Hospitals/Healthcare Facilities", "Hotel/Gaming", "Machinery", "R.E.I.T.",
        "Restaurant/Dining", "Retail (General)", "Steel", "Trucking",
        "Total Market", "Total Market (without financials)", "Diversified",
    ]
    faq = {
        COL_MKT_CAP: "Aggregated market capitalization across all firms in the industry.",
        COL_NET_INCOME: "Aggregated value of net income across all companies in the group.",
    }
    out = {}
    for key, _rel, _url, ym in FILES:
        rows = {}
        is_post = key in ("pedata_current", "DollarUS_current")
        is_24 = key in ("pedata23", "DollarUS23")
        for idx, ind in enumerate(industries):
            base_mc = 1000.0 + 50.0 * idx
            base_ni = 100.0 + 5.0 * idx
            if is_post and ind in AI_COMPLEX:
                mc = base_mc * ai_mult_jump
                ni = base_ni
            elif is_24 and ind in AI_COMPLEX:
                mc = base_mc * (1.0 + 0.5 * (ai_mult_jump - 1.0))
                ni = base_ni
            else:
                mc = base_mc * (1.1 if is_post else 1.0)
                ni = base_ni * (1.1 if is_post else 1.0)
            pe = mc / ni
            rows[ind] = {
                COL_NUM_FIRMS: 20.0 + idx,
                COL_MKT_CAP: mc,
                COL_NET_INCOME: ni,
                COL_PE_ALL: pe,
                COL_PE_MM: pe * 0.9,
            }
        out[key] = {"date_ym": ym, "headers": [COL_INDUSTRY, COL_NUM_FIRMS, COL_MKT_CAP, COL_NET_INCOME, COL_PE_ALL, COL_PE_MM], "rows": rows, "faq_defs": dict(faq)}
    return out


def selftest():
    ck = Checks()
    # 1. Spec hash & version-2 table parsing
    spec_bytes = spec_text()
    ck.eq("spec: file on disk hashes to pinned sha256", sha256_of(spec_bytes), SPEC_SHA256)
    rows = parse_spec_v2(spec_bytes.decode("utf-8"))
    ck.eq("spec: AV1-P1 parsed from version-2 table", sorted(rows), list(IDS))
    ck.raises("spec: tampered hash refused", Refused, lambda: check_spec_hash(pinned="0" * 64))
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "_research"))
        with open(os.path.join(td, *SPEC_FILE.split("/")), "wb") as fh:
            fh.write(spec_bytes + b"\ntamper\n")
        ck.raises("spec: tampered file stops write_registered", Refused, lambda: write_registered(os.path.join(td, "out"), root=td))
        ck.ok("spec: nothing written when refused", not os.path.exists(os.path.join(td, "out", "registered.csv")))

    # 2. Fetcher: 10 GETs, UA, 3s sleep, no refetch, STOP conditions
    with tempfile.TemporaryDirectory() as td:
        slept = []
        ff = _FakeHttpFetcher(lambda idx, url, hdrs: (200, OLE2_MAGIC + b"synthetic-xls-" + str(idx).encode(), {}))
        cmd_fetch(td, fetcher=ff, sleep=slept.append)
        ck.eq("fetch: 10 GETs made", len(ff.calls), 10)
        ck.eq("fetch: User-Agent is exact house string", ff.calls[0][1]["User-Agent"], UA)
        ck.eq("fetch: 3.0s sleep between GETs (9 gaps)", slept, [3.0] * 9)
        ck.ok("fetch: manifest.csv written", os.path.exists(os.path.join(cache_dir(td), "manifest.csv")))
        ck.ok("fetch: current files saved with _current names", os.path.exists(os.path.join(cache_dir(td), "raw", "pedata_current.xls")) and os.path.exists(os.path.join(cache_dir(td), "raw", "DollarUS_current.xls")))
        ck.raises("fetch: refuses to refetch if raw files already exist", Refused, lambda: cmd_fetch(td, fetcher=ff, sleep=slept.append))

    with tempfile.TemporaryDirectory() as td:
        ff = _FakeHttpFetcher(lambda idx, url, hdrs: (403, b"forbidden", {}))
        ck.raises("fetch STOP: HTTP 403 writes STOP.txt", Stop, lambda: cmd_fetch(td, fetcher=ff, sleep=lambda s: None))
        ck.ok("fetch STOP: STOP.txt created on HTTP 403", os.path.exists(os.path.join(cache_dir(td), "STOP.txt")))
        ck.raises("fetch STOP: existing STOP.txt blocks subsequent run", Stop, lambda: cmd_fetch(td, fetcher=ff, sleep=lambda s: None))

    with tempfile.TemporaryDirectory() as td:
        ff = _FakeHttpFetcher(lambda idx, url, hdrs: (200, b"<html>not an xls</html>", {}))
        ck.raises("fetch STOP: non-OLE2 body writes STOP.txt", Stop, lambda: cmd_fetch(td, fetcher=ff, sleep=lambda s: None))
        ck.ok("fetch STOP: STOP.txt created on bad magic bytes", os.path.exists(os.path.join(cache_dir(td), "STOP.txt")))

    # 3. Date updated & FAQ definition checks
    synth_d = _synth_damodaran(ai_mult_jump=2.0)
    with tempfile.TemporaryDirectory() as td:
        for _k, rel, _u, _ym in FILES:
            write_bytes(os.path.join(cache_dir(td), *rel.split("/")), OLE2_MAGIC + b"x")
        bad_date = _synth_damodaran()
        bad_date["pedata22"]["date_ym"] = (2022, 12)
        ck.raises(
            "build STOP: wrong Date updated stops and writes STOP.txt",
            Stop,
            lambda: load_cached_damodaran(td, reader=lambda p: bad_date[os.path.basename(p).replace(".xls", "")]),
        )
        ck.ok("build STOP: STOP.txt written on date mismatch", os.path.exists(os.path.join(cache_dir(td), "STOP.txt")))

    with tempfile.TemporaryDirectory() as td:
        for _k, rel, _u, _ym in FILES:
            write_bytes(os.path.join(cache_dir(td), *rel.split("/")), OLE2_MAGIC + b"x")
        bad_faq = _synth_damodaran()
        bad_faq["DollarUS_current"]["faq_defs"][COL_NET_INCOME] = "Different definition text."
        ck.raises(
            "build STOP: differing Net Income FAQ definition stops",
            Stop,
            lambda: load_cached_damodaran(td, reader=lambda p: bad_faq[os.path.basename(p).replace(".xls", "")]),
        )

    # 4. End-to-end compute: SUPPORT when AI multiple doubles, INCONCLUSIVE when K < 7 or non-positive NI
    btos = _synth_btos()
    R_sup = compute(synth_d, btos, seed=PERM_SEED, nperm=1000)
    ck.eq("compute: SUPPORT when AI multiple doubles (K=7, nperm=1000)", R_sup["P1"]["label"], "SUPPORT")
    ck.near("compute: delta_M_ai is ln(2)", R_sup["P1"]["ai_pool"]["delta_M"], math.log(2.0))
    ck.near("compute: delta_M_other is 0.0", R_sup["P1"]["other_pool"]["delta_M"], 0.0)
    ck.eq("compute: 3 excluded rows dropped", len(R_sup["P1"]["dropped"]), 3)
    ck.ok("compute: reported items populated", R_sup["v1_P1"]["diff_mean"] is not None and R_sup["btos_spearman"]["n"] > 0)

    # K < 7 -> INCONCLUSIVE
    synth_k6 = _synth_damodaran(ai_mult_jump=2.0)
    del synth_k6["DollarUS_current"]["rows"]["Computer Services"]
    R_k6 = compute(synth_k6, btos, seed=PERM_SEED, nperm=1000)
    ck.eq("compute: K=6 (< 7) forces INCONCLUSIVE", (R_k6["P1"]["K"], R_k6["P1"]["label"]), (6, "INCONCLUSIVE"))

    # Non-positive pool net income -> INCONCLUSIVE
    synth_neg = _synth_damodaran(ai_mult_jump=2.0)
    for ind in AI_COMPLEX:
        synth_neg["DollarUS_current"]["rows"][ind][COL_NET_INCOME] = -500.0
    R_neg = compute(synth_neg, btos, seed=PERM_SEED, nperm=1000)
    ck.eq("compute: non-positive AI pool net income -> INCONCLUSIVE", (R_neg["P1"]["nonpositive_pool"], R_neg["P1"]["label"]), (True, "INCONCLUSIVE"))

    # 5. Output files, no_leak, README required sentences
    scores, detail = make_rows(R_sup)
    ck.eq("outputs: 1 score row (AV1-P1)", len(scores), 1)
    ck.raises("no_leak: at sign refused", Refused, lambda: no_leak("x", "a@b"))
    ck.raises("no_leak: /Users/ refused", Refused, lambda: no_leak("x", "/Users/foo"))
    with tempfile.TemporaryDirectory() as td:
        out_td = os.path.join(td, "out")
        _reg_p, sha = write_registered(out_td)
        rd_txt = readme_text(R_sup, sha)
        for name, txt in (
            ("scores.csv", table_text("selftest", SCORES_HEADER, scores)),
            ("detail.csv", table_text("selftest", DETAIL_HEADER, detail)),
            ("README.md", rd_txt),
        ):
            no_leak(name, txt)
            write_text(os.path.join(out_td, name), txt)
        ck.ok("outputs: registered.csv, scores.csv, detail.csv, README.md written", all(os.path.exists(os.path.join(out_td, n)) for n in ("registered.csv", "scores.csv", "detail.csv", "README.md")))
        ck.ok("README: asymmetry, universe, earnings def, seven named industries", (
            "It does not show the market is wrong" in rd_txt
            and "country of incorporation (the US)" in rd_txt
            and "third quarter of the prior year" in rd_txt
            and "seven named industries" in rd_txt
        ))

    bad = [(n, d) for n, c, d in ck.items if not c]
    for n, c, d in ck.items:
        print(("ok   " if c else "FAIL ") + n + ("" if c else "  <- " + d))
    print("%d checks, %d failed" % (len(ck.items), len(bad)))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="AV1 AI valuation scorer (spec version 2)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sub.add_parser("fetch")
    bp = sub.add_parser("build")
    bp.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    try:
        if a.cmd == "fetch":
            return cmd_fetch()
        run_build(out=a.out)
    except Stop as e:
        print("STOP: %s" % e, file=sys.stderr)
        return 4
    except Refused as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
