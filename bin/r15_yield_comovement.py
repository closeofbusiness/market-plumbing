#!/usr/bin/env python3
"""R15: how much of the weekly movement in the US, German, UK and Japanese 10-year government yields is common to all four.

  python3 bin/r15_yield_comovement.py selftest                       # synthetic fixtures, 23 guards and their mutants; no network
  python3 bin/r15_yield_comovement.py fetch [--archive] [--cache DIR]  # the ONLY mode that uses the network
  python3 bin/r15_yield_comovement.py calibrate [--cache DIR]        # offline; pre-2018 history only: placebo layouts and their spread
  python3 bin/r15_yield_comovement.py build [--cache DIR] [--out DIR] # offline and byte-identical on re-run
  python3 bin/r15_yield_comovement.py mde                            # synthetic; the false-SHIFT and power tables, and the fallback k_infl

Specification: _research/2026-10-18-Yield-Comovement-Four-Country-Spec.md (section 12, the amendments, overrides the sections above it).

The statistic is the first-eigenvalue share of the 4x4 correlation matrix of non-overlapping weekly changes in the four 10-year yields
(0.25 for four unrelated series, 1.0 for four moving in lockstep). One pre-registered question: did that share differ between the
2018-19 window and the 2024-latest window? Everything else is description.

Raw files never enter the repository. They live in a cache outside it (default ~/r15_yield_cache/; a path inside the repo is refused) and
the weekly panel built from them lives in <cache>/derived/. Only derived statistics are committed, under data/r15_yield_comovement/, and
every output file has an exact column allowlist. The sources are the US Treasury, the Deutsche Bundesbank, the Bank of England, the
Ministry of Finance Japan and the European Central Bank. CC BY 4.0 covers only this project's computation.

fetch is polite: one request at a time, at least 3 seconds apart, at most 50 per run, a neutral User-Agent with no address, GET only,
redirects not followed, five hosts only. Any status other than 200, a redirect, or a body that fails its content test writes
~/r15_yield_cache/STOP and ends the run; no fetch happens while STOP exists, nothing retries, and only a person deletes it. A socket fault
ends the run without latching.
"""
import argparse
import bisect
import contextlib
import csv
import datetime as dt
import hashlib
import io
import math
import os
import re
import shutil
import socket
import ssl
import sys
import tempfile
import time
import zipfile
import http.client
import urllib.error
import urllib.request
from urllib.parse import urlsplit

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "data", "r15_yield_comovement")
SPEC_PATH = os.path.join(ROOT, "_research", "2026-10-18-Yield-Comovement-Four-Country-Spec.md")
DEFAULT_CACHE = os.path.expanduser("~/r15_yield_cache")
STOP_PATH = os.path.join(os.path.expanduser("~/r15_yield_cache"), "STOP")  # fixed whatever --cache says (R5)

UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
HOSTS = ("home.treasury.gov", "api.statistiken.bundesbank.de", "www.mof.go.jp", "www.bankofengland.co.uk", "data-api.ecb.europa.eu")
PACE_S = 3.0
MAX_REQUESTS = 50
TIMEOUT_S = 120
ARCHIVE_TIMEOUT_S = 600
MAX_BODY = 120 * 1024 * 1024

# ----------------------------------------------------------------------------------------------------------------------
# pre-registered constants: the single source. selftest renders them and compares the sha256 with the anchor in the spec (G15)
# ----------------------------------------------------------------------------------------------------------------------
CONST_ANCHOR = "8ecbe5c0af92f9f7e43b2a407490900f5c9d4d17fe1173c9b12dd618c81fe097"
CONST = dict(
    windows=(("w2018_19", "2018-01-05", "2019-12-27"), ("w2020_21", "2020-01-03", "2021-12-31"), ("w2022_23", "2022-01-07", "2023-12-29"),
             ("w2024_latest", "2024-01-05", "latest"), ("w2024_25", "2024-01-05", "2025-12-26"), ("w2026_ytd", "2026-01-02", "latest"),
             ("full", "2018-01-05", "latest")),
    primary_set="nom4", primary_from="w2018_19", primary_to="w2024_latest",
    block_len=8, block_checks=(4, 12), boot_draws=2000, seed=20261018,
    z95=1.96, z90=1.645, shift_floor=0.10, equivalence_margin=0.15,
    span_from="1997-08-15", span_to="2017-12-29", pre=104, gap=209, step=13, min_layouts=20,
    grid_lo=1.0, grid_hi=4.0, grid_step=0.25, k_author=3.0, target_false_shift=0.05,
    rho_txt=("0.3", "0.5"), phi_txt=("0", "0.90", "0.97"), sdlog_txt=("0.3", "0.6"),
    d1_stale_bdays=5, d2_max_drop=0.05, d3_min_sd_bp=1.0, d5_floor=(("w2018_19", 90), ("w2024_latest", 125)),
    robust_delta=0.05, robust_sets=("nom4_ecb", "nom4_jgb_lead1"),
)
W_NAMES = [w[0] for w in CONST["windows"]]
SEED = CONST["seed"]
Z95, Z90 = CONST["z95"], CONST["z90"]
SHIFT_FLOOR, EQ_MARGIN = CONST["shift_floor"], CONST["equivalence_margin"]
D5_FLOOR = dict(CONST["d5_floor"])


def render_constants(c=None):
    """The constants block, exactly as the spec prints it between its two marker lines (each line ends with a newline)."""
    c = dict(CONST if c is None else c)
    if _mut("const_alter"):
        c["z95"] = 1.95
    lines = [
        "windows=" + "|".join("%s:%s:%s" % w for w in c["windows"]),
        "primary=%s:%s->%s:lambda1_share:two_sided" % (c["primary_set"], c["primary_from"], c["primary_to"]),
        "gap_rule=previous_print_iso_week_immediately_preceding(mondays_7_days_apart)",
        "week_included_if=friday<=asof",
        "block_len=%d;block_checks=%s;boot_draws=%d;seed=%d" % (c["block_len"], ",".join(str(x) for x in c["block_checks"]), c["boot_draws"], c["seed"]),
        "z95=%s;z90=%s;shift_floor=%.2f;equivalence_margin=%.2f;overlap=INCONCLUSIVE" % (c["z95"], c["z90"], c["shift_floor"], c["equivalence_margin"]),
        "placebo=span:%s..%s;layout:%d+%d+n_C;step_weeks:%d;spread:rms_about_zero;min_layouts:%d"
        % (c["span_from"], c["span_to"], c["pre"], c["gap"], c["step"], c["min_layouts"]),
        "boot_sd_used=max(boot_sd,placebo_sd)",
        "fallback_k_infl_grid=%.1f..%.1f:%.2f;fallback_k_infl_author=%.1f;fallback_target_false_shift=%.2f"
        % (c["grid_lo"], c["grid_hi"], c["grid_step"], c["k_author"], c["target_false_shift"]),
        "fallback_scenarios=rho:%s;phi:%s;sdlog:%s;shocks:t5" % (",".join(c["rho_txt"]), ",".join(c["phi_txt"]), ",".join(c["sdlog_txt"])),
        "d1_stale_bdays=%d;d2_max_drop=%.2f;d3_min_sd_bp=%.1f;d5_min_weeks=%s"
        % (c["d1_stale_bdays"], c["d2_max_drop"], c["d3_min_sd_bp"], ",".join("%s:%d" % x for x in c["d5_floor"])),
        "robustness_flag_delta=%.2f;robustness_sets=%s" % (c["robust_delta"], ",".join(c["robust_sets"])),
        "jgb_lead1=first_jgb_print_after_friday_within_4_bdays;last_week_requires_lead_print<=asof",
    ]
    return "".join(x + "\n" for x in lines)


def constants_sha(text=None):
    return hashlib.sha256((render_constants() if text is None else text).encode("utf-8")).hexdigest()


def spec_constants_block(path=SPEC_PATH):
    """The text strictly between the two marker lines of the landed spec, or None when the spec is not on disk."""
    if not os.path.exists(path):
        return None
    t = open(path, encoding="utf-8").read()
    a = t.find("R15-CONSTANTS-BEGIN\n")
    b = t.find("R15-CONSTANTS-END")
    if a < 0 or b < 0:
        return None
    return t[a + len("R15-CONSTANTS-BEGIN\n"):b]


# ----------------------------------------------------------------------------------------------------------------------
# series, sets, outputs
# ----------------------------------------------------------------------------------------------------------------------
NOM4 = ["us_nom", "bund_nom", "gilt_nom", "jgb_nom"]
SETS = {
    "nom4": list(NOM4),
    "nom3_ex_jgb": ["us_nom", "bund_nom", "gilt_nom"],
    "nom4_ecb": ["us_nom", "ea_aaa", "gilt_nom", "jgb_nom"],
    "nom4_usreal": ["us_nom", "bund_nom", "gilt_nom", "jgb_nom", "us_real"],
    "nom4_jgb_lead1": ["us_nom", "bund_nom", "gilt_nom", "jgb_lead1"],
}
SET_ORDER = ["nom4", "nom3_ex_jgb", "nom4_ecb", "nom4_usreal", "nom4_jgb_lead1"]
DAILY_SERIES = ["us_nom", "us_real", "bund_nom", "gilt_nom", "jgb_nom", "ea_aaa"]
ISSUER = {"us_nom": "US Treasury", "us_real": "US Treasury", "bund_nom": "Deutsche Bundesbank", "gilt_nom": "Bank of England",
          "jgb_nom": "Ministry of Finance Japan", "ea_aaa": "European Central Bank"}
SEAM_OF = {"gilt_nom": "boe_archive|boe_latest", "jgb_nom": "mof_all|mof_current"}

ALLOW = {
    "windows.csv": ["window", "series_set", "k", "asof", "first_week", "last_week", "weeks_calendar", "weeks_used", "dropped_gap",
                    "dropped_missing", "lambda1", "lambda1_share", "rho_mean", "rho_min", "rho_max", "share_ci95_lo", "share_ci95_hi",
                    "block_len", "boot_draws", "status"],
    "pairs.csv": ["window", "series_set", "pair", "n", "rho", "ci95_lo", "ci95_hi"],
    "shift_test.csv": ["comparison", "role", "statistic", "series_set", "window_from", "window_to", "value_from", "value_to", "delta",
                       "boot_sd", "placebo_sd", "placebo_layouts", "boot_sd_used", "calibration", "inflation_k", "ci95_lo", "ci95_hi",
                       "ci90_lo", "ci90_hi", "block_len", "boot_draws", "verdict", "downgrade_reasons"],
    "series_stats.csv": ["window", "series", "n_changes", "sd_bp", "dropped_gap", "missing_weeks"],
    "freshness.csv": ["source", "series", "last_obs", "asof", "lag_bdays", "max_lag_bdays", "status", "seam", "seam_status"],
    "checks.csv": ["check_id", "description", "pin_date", "expected", "observed", "status"],
    "fetch_log.csv": ["utc", "host", "path", "status", "bytes", "sha256", "note"],
}
DATE_COLS = {"windows.csv": {"first_week", "last_week", "asof"}, "freshness.csv": {"last_obs", "asof"}, "checks.csv": {"pin_date"},
             "fetch_log.csv": {"utc"}}
MAX_ROWS = 80


def max_rows():
    """The leak-guard row limit. selftest G16 asserts the literal 80, not this function (mutant max_rows_800)."""
    return 800 if _mut("max_rows_800") else MAX_ROWS


def allowlist(name):
    """The exact column allowlist of one output (mutant allow_extra adds a level column). G16 and G17 compare it with literal copies."""
    return ALLOW[name] + ["us_nom_level"] if _mut("allow_extra") else ALLOW[name]
ISSUER_NOTES = ("US Treasury (home.treasury.gov, daily par yield curve and par real yield curve)",
                "Deutsche Bundesbank (api.statistiken.bundesbank.de, BBSIS)",
                "Bank of England (www.bankofengland.co.uk, nominal spot curve)",
                "Ministry of Finance Japan (www.mof.go.jp, JGB interest rate)",
                "European Central Bank (data-api.ecb.europa.eu, YC euro-area AAA)")
HOST_OF_ISSUER = {"US Treasury": "home.treasury.gov", "Deutsche Bundesbank": "api.statistiken.bundesbank.de",
                  "Bank of England": "www.bankofengland.co.uk", "Ministry of Finance Japan": "www.mof.go.jp",
                  "European Central Bank": "data-api.ecb.europa.eu"}


class HardFail(Exception):
    """A rule of the build that must stop the run (header off its allowlist, a set that is singular, a missing cache file)."""


class Refused(Exception):
    """A request, path or setting this script will not honour."""


class Latched(Exception):
    """STOP was written or exists: the run ends, nothing retries."""


class MaxRequests(Refused):
    """The per-run request cap was reached."""


class SocketFault(Exception):
    """Timeout, reset or TLS error: the run ends without latching."""


class ParseError(Exception):
    """A source file did not have the layout the spec records."""


# ----------------------------------------------------------------------------------------------------------------------
# mutants (selftest only): production code carries small named hooks; a mutant is a hook switched on
# ----------------------------------------------------------------------------------------------------------------------
MUT = set()


def _mut(name):
    return name in MUT


@contextlib.contextmanager
def mutated(*names):
    MUT.update(names)
    try:
        yield
    finally:
        MUT.difference_update(names)


# ----------------------------------------------------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------------------------------------------------
def tilde(p):
    home = os.path.expanduser("~")
    return str(p).replace(home, "~") if home and home != "~" else str(p)


def fmt(x, nd=3):
    if x is None:
        return ""
    if isinstance(x, (float, np.floating)):
        if not math.isfinite(float(x)):
            return ""
        s = "%.*f" % (nd, float(x))
        return ("%.*f" % (nd, 0.0)) if float(s) == 0.0 else s
    return str(x)


def iso(d):
    return d.isoformat() if d is not None else ""


def monday_of(d):
    return d - dt.timedelta(days=d.weekday())


def friday_of(d):
    return monday_of(d) + dt.timedelta(days=4)


def bdays_after(d, upto):
    """Weekdays in (d, upto]; Monday to Friday, no holiday calendar."""
    if upto <= d:
        return 0
    return int(np.busday_count(np.datetime64(d + dt.timedelta(days=1)), np.datetime64(upto + dt.timedelta(days=1))))


def next_weekday(d):
    n = d + dt.timedelta(days=1)
    while n.weekday() >= 5:
        n += dt.timedelta(days=1)
    return n


def fridays(lo, hi):
    out, f = [], lo
    while f <= hi:
        out.append(f)
        f += dt.timedelta(days=7)
    return out


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def utcnow():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


MISSING = {"", ".", "-", "n/a", "na", "nan", "null", "none"}


def to_float(s, decimal="."):
    """A numeric cell, or None for any missing marker. A missing marker is never 0 (G12)."""
    if s is None:
        s = ""
    if isinstance(s, (int, float)) and not isinstance(s, bool):
        v = float(s)
        return v if math.isfinite(v) else None
    t = str(s).strip()
    key = t.lower()
    if key in MISSING:
        if key == "." and _mut("miss0_dot"):
            return 0.0
        if key == "-" and _mut("miss0_dash"):
            return 0.0
        if key == "n/a" and _mut("miss0_na"):
            return 0.0
        if key == "" and _mut("miss0_blank"):
            return 0.0
        return None
    if decimal == ",":
        t = t.replace(",", ".")
    try:
        v = float(t)
    except ValueError:
        return None
    return v if math.isfinite(v) else None


# ----------------------------------------------------------------------------------------------------------------------
# parsers (select by NAME, never by position; every missing marker is missing)
# ----------------------------------------------------------------------------------------------------------------------
DATE_MDY = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
DATE_YMD_SLASH = re.compile(r"^(\d{4})/(\d{1,2})/(\d{1,2})$")
DATE_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_treasury(text, kind="nom"):
    """Daily Treasury CSV (par yield curve or par real yield curve) -> {date: 10-year value}. The header differs by year."""
    target = "10 Yr" if kind == "nom" else "10 YR"
    rows = csv.reader(io.StringIO(text.lstrip("﻿")))
    header = next(rows, None)
    if not header:
        raise ParseError("empty Treasury file")
    names = [h.strip() for h in header]
    if _mut("treasury_positional"):
        idx = 12
    else:
        hits = [i for i, n in enumerate(names) if n == target]
        if len(hits) != 1:
            raise ParseError("Treasury header: expected exactly one column named %r, found %d" % (target, len(hits)))
        idx = hits[0]
    out = {}
    for r in rows:
        if not r:
            continue
        m = DATE_MDY.match(r[0].strip())
        if not m:
            continue
        d = dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        v = to_float(r[idx]) if idx < len(r) else None
        if v is not None:
            out[d] = v
    return out


def parse_bundesbank(text):
    """Bundesbank BBSIS CSV, German (';' and decimal comma) or English (',' and decimal point) -> {date: value}. '.' is missing."""
    head = text[:6000]
    if "Stand vom" in head:
        sep, dec = ";", ","
    elif "last update" in head.lower():
        sep, dec = ",", "."
    else:
        raise ParseError("Bundesbank header holds neither 'Stand vom' nor 'last update'")
    if _mut("bbk_split_comma"):
        sep = ","
    out = {}
    for line in text.splitlines():
        cells = next(csv.reader([line], delimiter=sep), [])
        if len(cells) < 1 or not DATE_ISO.match(cells[0].strip()):
            continue
        v = to_float(cells[1], dec) if len(cells) > 1 else None
        if v is not None:
            out[dt.date.fromisoformat(cells[0].strip())] = v
    return out


def parse_mof(text):
    """MoF JGB interest-rate CSV -> ({date: 10Y value}, {row dates}). Title, blank and footer lines are skipped; '-' or blank is missing."""
    idx = None
    prints, rowdates = {}, set()
    for r in csv.reader(io.StringIO(text.lstrip("﻿"))):
        if idx is None:
            cells = [c.strip() for c in r]
            if cells and cells[0] == "Date" and "10Y" in cells:
                idx = cells.index("10Y")
            continue
        if not r:
            continue
        m = DATE_YMD_SLASH.match(r[0].strip())
        if not m:
            continue
        d = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        rowdates.add(d)
        v = to_float(r[idx]) if idx < len(r) else None
        if v is not None:
            prints[d] = v
    if idx is None:
        raise ParseError("MoF file has no 'Date,...,10Y' header line")
    return prints, rowdates


def parse_ecb(text):
    rows = csv.DictReader(io.StringIO(text.lstrip("﻿")))
    if not rows.fieldnames or "OBS_VALUE" not in rows.fieldnames or "TIME_PERIOD" not in rows.fieldnames:
        raise ParseError("ECB header lacks TIME_PERIOD or OBS_VALUE")
    out = {}
    for r in rows:
        t = (r.get("TIME_PERIOD") or "").strip()
        if not DATE_ISO.match(t):
            continue
        v = to_float(r.get("OBS_VALUE"))
        if v is not None:
            out[dt.date.fromisoformat(t)] = v
    return out


BOE_SPOT_SHEETS = ("4. spot curve", "4. nominal spot curve")


def boe_pick_sheet(names):
    """The spot-curve sheet: '4. spot curve' (2005 onward) or '4. nominal spot curve' (before). Never a sheet with 'fwd' in its name."""
    norm = [(n, n.strip().lower()) for n in names]
    if _mut("boe_fwd"):
        c = [n for n, k in norm if k == "2. fwd curve"]
    elif _mut("boe_only_spot"):
        c = [n for n, k in norm if k == "4. spot curve"]
    else:
        c = [n for n, k in norm if k in BOE_SPOT_SHEETS and "fwd" not in k]
    if len(c) != 1:
        raise ParseError("BoE workbook: expected exactly one spot-curve sheet, found %r among %r" % (c, list(names)))
    return c[0]


def parse_boe_workbook(fileobj):
    """One BoE GLC nominal workbook -> ({date: 10-year spot}, {row dates}). The 10-year column is the one whose maturity header equals 10."""
    import openpyxl
    wb = openpyxl.load_workbook(fileobj, read_only=True, data_only=True)
    try:
        ws = wb[boe_pick_sheet(wb.sheetnames)]
        idx = None
        prints, rowdates = {}, set()
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if idx is None:
                if i >= 12:
                    break
                if row and isinstance(row[0], str) and row[0].strip().lower() == "years:":
                    hits = []
                    for j, c in enumerate(row):
                        if j == 0 or c is None or isinstance(c, bool):
                            continue
                        try:
                            if float(c) == 10.0:
                                hits.append(j)
                        except (TypeError, ValueError):
                            pass
                    if len(hits) != 1:
                        raise ParseError("BoE maturity header: expected exactly one column equal to 10, found %d" % len(hits))
                    idx = 20 if _mut("boe_idx20") else hits[0]
                continue
            if not row or not isinstance(row[0], (dt.datetime, dt.date)):
                continue
            d = row[0].date() if isinstance(row[0], dt.datetime) else row[0]
            rowdates.add(d)
            v = to_float(row[idx]) if idx < len(row) else None
            if v is not None:
                prints[d] = v
        if idx is None:
            raise ParseError("BoE workbook has no 'years:' maturity header row")
        return prints, rowdates
    finally:
        wb.close()


def parse_boe_zip(body):
    """A BoE zip (archive or latest month) -> ({date: 10-year spot}, {row dates}) over its 'GLC Nominal daily data*.xlsx' members."""
    prints, rowdates = {}, set()
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        members = sorted(n for n in z.namelist() if os.path.basename(n).startswith("GLC Nominal daily data") and n.lower().endswith(".xlsx"))
        if not members:
            raise ParseError("BoE zip holds no 'GLC Nominal daily data' workbook")
        for n in members:  # the file names sort by their first year, so a later member overrides an earlier one on a shared date
            p, r = parse_boe_workbook(io.BytesIO(z.read(n)))
            prints.update(p)
            rowdates |= r
    return prints, rowdates


# ----------------------------------------------------------------------------------------------------------------------
# fetch plan, content tests, fence
# ----------------------------------------------------------------------------------------------------------------------
TREASURY_URL = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/%d/all"
                "?type=%s&field_tdr_date_value=%d&page&_format=csv")
BBK_URL = "https://api.statistiken.bundesbank.de/rest/data/BBSIS/D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A?format=csv"
BBK_KEY = "D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A"
MOF_ALL_URL = "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv"
MOF_CUR_URL = "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/jgbcme.csv"
BOE_ARCHIVE_URL = "https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/glcnominalddata.zip"
BOE_LATEST_URL = "https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/latest-yield-curve-data.zip"
ECB_URL = ("https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y"
           "?format=csvdata&detail=dataonly&startPeriod=2017-12-01")


def us_years(kind, cur_year):
    """The Treasury years the plan covers: nominal 1997..current (the placebo needs them), real 2017..current."""
    if kind == "nom":
        return list(range(2022, cur_year + 1)) if _mut("g4years") else list(range(1997, cur_year + 1))
    return list(range(2017, cur_year + 1))


def fetch_plan(cur_year, archive):
    """[(kind, filename, url)] in fetch order. Full fetch = 30 + 10 + 6 = 46 requests; the default refresh is 7."""
    plan = [("bund", "bund_nom.csv", BBK_URL), ("mof_all", "jgb_all.csv", MOF_ALL_URL), ("mof_cur", "jgb_current.csv", MOF_CUR_URL),
            ("boe_latest", "boe_latest.zip", BOE_LATEST_URL), ("ecb", "ecb_ea_aaa.csv", ECB_URL),
            ("us_nom", "us_nom_%d.csv" % cur_year, TREASURY_URL % (cur_year, "daily_treasury_yield_curve", cur_year)),
            ("us_real", "us_real_%d.csv" % cur_year, TREASURY_URL % (cur_year, "daily_treasury_real_yield_curve", cur_year))]
    if archive:
        for y in reversed(us_years("nom", cur_year)):
            if y != cur_year:
                plan.append(("us_nom", "us_nom_%d.csv" % y, TREASURY_URL % (y, "daily_treasury_yield_curve", y)))
        for y in reversed(us_years("real", cur_year)):
            if y != cur_year:
                plan.append(("us_real", "us_real_%d.csv" % y, TREASURY_URL % (y, "daily_treasury_real_yield_curve", y)))
        plan.append(("boe_archive", "boe_archive.zip", BOE_ARCHIVE_URL))
    return plan


def content_ok(kind, body):
    """R5 content tests, run on a body before it replaces a cached file. Returns (ok, reason)."""
    if _mut("no_content_test"):
        return True, ""
    if kind in ("boe_archive", "boe_latest"):
        if body[:4] != b"PK\x03\x04":
            return False, "no zip magic"
        try:
            with zipfile.ZipFile(io.BytesIO(body)) as z:
                if not any(os.path.basename(n).startswith("GLC Nominal daily data") for n in z.namelist()):
                    return False, "no 'GLC Nominal daily data' member"
        except zipfile.BadZipFile:
            return False, "bad zip"
        return True, ""
    text = body.decode("utf-8-sig", errors="replace")
    lines = text.splitlines()
    first = lines[0] if lines else ""
    if kind == "us_nom":
        return (first.startswith("Date,") and '"10 Yr"' in first), "header lacks Date, / 10 Yr"
    if kind == "us_real":
        return (first.startswith("Date,") and '"10 YR"' in first), "header lacks Date, / 10 YR"
    if kind == "bund":
        head = "\n".join(lines[:15])
        return (BBK_KEY in head and ("Stand vom" in head or "last update" in head.lower())), "header lacks the series key or the update line"
    if kind in ("mof_all", "mof_cur"):
        ok = any(l.startswith("Date,1Y,") and "10Y" in l for l in lines[:12])
        return ok, "no 'Date,1Y,...10Y' line"
    if kind == "ecb":
        return ("OBS_VALUE" in first), "header lacks OBS_VALUE"
    return False, "unknown kind"


def assert_ua(ua=UA):
    if _mut("ua_at"):
        return
    if "@" in ua:
        raise Refused("the User-Agent string holds an address")
    for var in ("SEC_UA", "CLAUDE_CODE_USER_EMAIL"):
        v = os.environ.get(var, "").strip()
        if v and (v in ua or ua in v):
            raise Refused("the User-Agent string holds a configured contact value (not printed)")


assert_ua()


def check_url(url):
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    if _mut("no_host_check"):
        return host, p.path + ("?" + p.query if p.query else "")
    if p.scheme != "https":
        raise Refused("only https is allowed")
    if host == "sec.gov" or host.endswith(".sec.gov"):
        raise Refused("sec.gov hosts are never fetched by this script")
    if host not in HOSTS:
        raise Refused("host %s is outside the allowlist" % host)
    return host, p.path + ("?" + p.query if p.query else "")


def check_cache(cache):
    real = os.path.realpath(os.path.expanduser(cache))
    root = os.path.realpath(ROOT)
    if _mut("cache_in_repo"):
        return real
    if real == root or real.startswith(root + os.sep):
        raise Refused("the cache must be outside the repository (raw yield files are never committed)")
    return real


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def real_opener(url, ua, timeout):
    """GET, no redirect following. Returns (status, headers, body); a socket-level fault raises SocketFault."""
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*"}, method="GET")
    op = urllib.request.build_opener(_NoRedirect)
    try:
        with op.open(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read(MAX_BODY + 1)
    except urllib.error.HTTPError as e:
        try:
            body = e.read(1024 * 1024)
        except Exception:
            body = b""
        return e.code, dict(e.headers), body
    except (urllib.error.URLError, socket.timeout, ConnectionError, ssl.SSLError, http.client.HTTPException, OSError) as e:
        raise SocketFault("%s: %s" % (type(e).__name__, e))


class Fetcher:
    """Sequential, paced, capped. The STOP latch is a file; every request leaves a row in <cache>/fetch_log.csv."""

    def __init__(self, cache, opener=None, sleep=time.sleep, clock=time.monotonic, now=utcnow, stop_path=None, pace=PACE_S,
                 max_requests=MAX_REQUESTS, ua=UA):
        assert_ua(ua)
        self.cache = check_cache(cache)
        self.opener = opener or real_opener
        self.sleep, self.clock, self.now = sleep, clock, now
        self.stop_path = stop_path or STOP_PATH
        self.pace = pace
        self.max_requests = max_requests
        self.ua = ua
        self.n = 0
        self.last_end = None
        self.log_path = os.path.join(self.cache, "fetch_log.csv")
        os.makedirs(self.cache, exist_ok=True)

    def _log(self, host, path, status, nbytes, sha, note):
        new = not os.path.exists(self.log_path)
        with open(self.log_path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            if new:
                w.writerow(ALLOW["fetch_log.csv"])
            w.writerow([self.now().strftime("%Y-%m-%dT%H:%M:%SZ"), host, path, status, nbytes, sha, note])

    def _latch(self, why):
        os.makedirs(os.path.dirname(self.stop_path), exist_ok=True)
        with open(self.stop_path, "w", encoding="utf-8") as f:
            f.write("%s %s\n" % (self.now().strftime("%Y-%m-%dT%H:%M:%SZ"), why))

    def get(self, kind, filename, url):
        if os.path.exists(self.stop_path) and not _mut("ignore_stop"):
            raise Latched("STOP exists at %s; only a person deletes it" % tilde(self.stop_path))
        if self.n >= self.max_requests and not _mut("no_cap"):
            raise MaxRequests("request cap of %d reached" % self.max_requests)
        host, path = check_url(url)
        if self.last_end is not None and not _mut("no_pacing"):
            wait = self.pace - (self.clock() - self.last_end)
            if wait > 0:
                self.sleep(wait)
        self.n += 1
        timeout = ARCHIVE_TIMEOUT_S if kind == "boe_archive" else TIMEOUT_S
        try:
            status, headers, body = self.opener(url, self.ua, timeout)
        except SocketFault as e:
            self.last_end = self.clock()
            self._log(host, path, "fault", 0, "", "socket fault: %s" % str(e)[:120])
            if _mut("latch_on_fault"):
                self._latch("socket fault")
            raise
        self.last_end = self.clock()
        lm = (headers or {}).get("Last-Modified", "")
        if status != 200:
            self._log(host, path, status, len(body or b""), "", "refused: status %s" % status)
            if not (_mut("no_latch_redirect") and 300 <= int(status) < 400) and not _mut("no_latch_status"):
                self._latch("status %s from %s" % (status, host))
            raise Latched("status %s from %s; STOP written" % (status, host))
        if len(body) > MAX_BODY:
            self._log(host, path, status, len(body), "", "refused: body larger than the cap")
            self._latch("oversize body from %s" % host)
            raise Latched("oversize body from %s; STOP written" % host)
        ok, why = content_ok(kind, body)
        if not ok:
            self._log(host, path, status, len(body), sha256_bytes(body), "refused: content test failed (%s)" % why)
            if not _mut("no_latch_content"):
                self._latch("content test failed for %s: %s" % (host, why))
            raise Latched("content test failed for %s (%s); STOP written" % (host, why))
        sha = sha256_bytes(body)
        self._log(host, path, 200, len(body), sha, ("Last-Modified: %s" % lm) if lm else "")
        return self.store(filename, body, sha), len(body)

    def store(self, filename, body, sha):
        """Write the body; keep a previous different vintage as <name>.<sha8>.prev (2.4)."""
        dest = os.path.join(self.cache, filename)
        if os.path.exists(dest):
            old = open(dest, "rb").read()
            osha = sha256_bytes(old)
            if osha != sha:
                prev = "%s.%s.prev" % (dest, osha[:8])
                if not os.path.exists(prev):
                    os.replace(dest, prev)
        tmp = dest + ".tmp"
        with open(tmp, "wb") as f:
            f.write(body)
        os.replace(tmp, dest)
        return dest


# ----------------------------------------------------------------------------------------------------------------------
# weekly engine (3.1): non-overlapping changes between the last valid prints of consecutive ISO weeks
# ----------------------------------------------------------------------------------------------------------------------
def wk(d):
    """The key of the ISO week holding d. Normally the week's Monday; the mutants key it by integers (G22)."""
    if _mut("isoint"):
        y, w, _ = d.isocalendar()
        return (y, w)
    if _mut("calyear"):
        return (d.year, d.isocalendar()[1])
    return monday_of(d)


def prev_wk(k):
    if isinstance(k, tuple):
        y, w = k
        return (y, w - 1) if w > 1 else None
    return k - dt.timedelta(days=7)


def friday_ok(f, asof):
    """A week is included only if its Friday is on or before the as-of date (A2)."""
    return True if _mut("nofriday_asof") else f <= asof


def weekly_last(prints, asof):
    """{week key: (monday, date, value)}: the last valid print dated inside each included ISO week."""
    out = {}
    for d in sorted(prints):
        if d > asof:
            break
        if not friday_ok(friday_of(d), asof):
            continue
        out[wk(d)] = (monday_of(d), d, prints[d])
    return out


def change_records(prints, asof):
    """[(key, monday, end_date, start_date, bp)]. A change is kept only if the earlier print sits in the immediately preceding ISO week
    (the two Mondays exactly 7 days apart). Each change spans (start, end] and the spans of consecutive changes do not overlap."""
    if _mut("rolling5"):
        ds = sorted(d for d in prints if d <= asof)
        recs = []
        for d in ds:
            s = d
            for _ in range(5):
                s -= dt.timedelta(days=1)
                while s.weekday() >= 5:
                    s -= dt.timedelta(days=1)
            if s in prints:
                recs.append((d, monday_of(d), d, s, (prints[d] - prints[s]) * 100.0))
        return recs
    w = weekly_last(prints, asof)
    order = sorted(w, key=lambda k: w[k][1])
    recs = []
    if _mut("oldgap"):  # the superseded rule: drop a change when more than 5 business days separate the prints
        for a, b in zip(order, order[1:]):
            if bdays_after(w[a][1], w[b][1]) <= 5:
                recs.append((b, w[b][0], w[b][1], w[a][1], (w[b][2] - w[a][2]) * 100.0))
        return recs
    for k in order:
        pk = prev_wk(k)
        if pk is not None and pk in w:
            recs.append((k, w[k][0], w[k][1], w[pk][1], (w[k][2] - w[pk][2]) * 100.0))
    return recs


def series_tables(prints, asof):
    w = weekly_last(prints, asof)
    chg = {r[0]: r[4] for r in change_records(prints, asof)}
    return {"w": w, "chg": chg}


def lead_series(prints, asof):
    """nom4_jgb_lead1 (3.3): for the week ending Friday F the JGB value is the first JGB print dated after F, within 4 business days of F,
    and dated on or before the as-of date. Changes are taken between consecutive weeks' lead values."""
    if not prints:
        return {"w": {}, "chg": {}}
    dates = sorted(prints)
    w = {}
    for f in fridays(friday_of(dates[0]), friday_of(asof)):
        if not friday_ok(f, asof):
            continue
        i = bisect.bisect_right(dates, f)
        if i >= len(dates):
            continue
        d = dates[i]
        if bdays_after(f, d) > 4:
            continue
        if d > asof and not _mut("nolead_asof"):
            continue
        w[wk(f)] = (monday_of(f), d, prints[d])
    chg = {}
    for k, v in w.items():
        pk = prev_wk(k)
        if pk is not None and pk in w:
            chg[k] = (v[2] - w[pk][2]) * 100.0
    return {"w": w, "chg": chg}


class Panel:
    def __init__(self, daily, asof):
        self.asof = asof
        self.s = {n: series_tables(p, asof) for n, p in daily.items()}
        if "jgb_nom" in daily:
            self.s["jgb_lead1"] = lead_series(daily["jgb_nom"], asof)


def eval_set(panel, names, fris):
    """Listwise deletion (3.1): a week enters a set only if every series in it has a valid change that week."""
    X, used, gapw, missw = [], [], [], []
    for f in fris:
        k = wk(f)
        if _mut("levels"):
            vals = [panel.s[n]["w"][k][2] if (n in panel.s and k in panel.s[n]["w"]) else None for n in names]
            if all(v is not None for v in vals):
                X.append(vals)
                used.append(f)
            continue
        miss = gap = False
        row = []
        for n in names:
            s = panel.s.get(n)
            if s is None or k not in s["w"]:
                miss = True
                row.append(None)
            elif k not in s["chg"]:
                gap = True
                row.append(None)
            else:
                row.append(s["chg"][k])
        if _mut("pairwise") and sum(v is not None for v in row) >= 2:
            X.append([0.0 if v is None else v for v in row])
            used.append(f)
            continue
        if miss:
            missw.append(f)
        elif gap:
            gapw.append(f)
        else:
            X.append(row)
            used.append(f)
    return dict(X=np.array(X, float).reshape(len(X), len(names)), used=used, n_cal=len(fris), gap_weeks=gapw, miss_weeks=missw,
                names=list(names))


def series_window(panel, name, fris):
    """One series on its own: n_changes, sd_bp, weeks with a print but no change (gap), weeks without a print."""
    s = panel.s.get(name)
    vals, gap, miss = [], 0, 0
    for f in fris:
        k = wk(f)
        if s is None or k not in s["w"]:
            miss += 1
        elif k not in s["chg"]:
            gap += 1
        else:
            vals.append(s["chg"][k])
    sd = float(np.std(vals, ddof=1)) if len(vals) > 2 else None
    return dict(n=len(vals), sd=sd, gap=gap, miss=miss)


def latest_common_friday(panel, names, asof):
    common = None
    for n in names:
        keys = set(panel.s[n]["w"]) if n in panel.s else set()
        common = keys if common is None else common & keys
    if not common:
        return None
    f = max(panel.s[names[0]]["w"][k][0] for k in common) + dt.timedelta(days=4)
    return f


def resolve_windows(asof, latest_fri):
    """{window: [Fridays]}: every end is capped at the latest common week; weeks_calendar counts Fridays <= min(end, as-of)."""
    out = {}
    for name, a, b in CONST["windows"]:
        f0 = dt.date.fromisoformat(a)
        f1 = latest_fri if b == "latest" else min(dt.date.fromisoformat(b), latest_fri)
        hi = f1 if _mut("nofriday_asof") else min(f1, asof)
        out[name] = fridays(f0, hi)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# statistic, bootstrap, placebo, decision rule
# ----------------------------------------------------------------------------------------------------------------------
def corr_matrix(X):
    return np.corrcoef(X, rowvar=False)


def identity_errors(R):
    k = R.shape[0]
    return abs(float(np.trace(R)) - k), abs(float(np.linalg.eigvalsh(R).sum()) - k)


def share_from_R(R):
    """lambda1 / k of a correlation matrix. The denominator is k, the trace (3.4); the identities and the singularity guard are asserted."""
    k = R.shape[0]
    ev = np.linalg.eigvalsh(R)
    if not ev[0] > 1e-6:
        raise HardFail("singular correlation matrix (smallest eigenvalue %.3g): a series is a linear combination of others" % ev[0])
    t, s = identity_errors(R)
    if t > 1e-8 or s > 1e-8:
        raise HardFail("trace or eigenvalue-sum identity broken (%.3g, %.3g)" % (t, s))
    return float(ev[-1]) / (2.0 if _mut("half") else float(k))


def lambda1_share(X):
    if _mut("cov"):
        C = np.cov(X, rowvar=False)
        return float(np.linalg.eigvalsh(C)[-1] / np.trace(C))
    return share_from_R(corr_matrix(X))


JGB_NAMES = ("jgb_nom", "jgb_lead1")
OTHER_CTRY = ("us_nom", "bund_nom", "gilt_nom", "ea_aaa")


def _jgb_cols(names):
    j = [i for i, n in enumerate(names) if n in JGB_NAMES][0]
    return j, [i for i, n in enumerate(names) if i != j and n in OTHER_CTRY]


def stat_X(stat, X, names):
    if stat == "lambda1_share":
        return lambda1_share(X)
    if stat == "jgb_mean_rho":
        j, o = _jgb_cols(names)
        return float(np.mean(corr_matrix(X)[j, o]))
    raise ValueError(stat)


def stat_Rb(stat, Rb, names):
    if stat == "lambda1_share":
        return np.linalg.eigvalsh(Rb)[:, -1] / Rb.shape[1]
    if stat == "jgb_mean_rho":
        j, o = _jgb_cols(names)
        return Rb[:, j, :][:, o].mean(axis=1)
    raise ValueError(stat)


def corr_batch(Xb):
    xc = Xb - Xb.mean(axis=1, keepdims=True)
    cov = np.einsum("bni,bnj->bij", xc, xc)
    d = np.sqrt(np.einsum("bii->bi", cov))
    with np.errstate(divide="ignore", invalid="ignore"):
        return cov / (d[:, :, None] * d[:, None, :])


def block_indices(n, b, B, rng):
    """B resamples of n row indices: ceil(n/b) block starts uniform on 0..n-b, b consecutive rows from each, truncated to n (3.5)."""
    if _mut("iid"):
        return rng.integers(0, n, size=(B, n))
    nb = -(-n // b)
    starts = rng.integers(0, n - b + 1, size=(B, nb))
    return (starts[:, :, None] + np.arange(b)[None, None, :]).reshape(B, nb * b)[:, :n]


def boot_R(X, b, B, rng):
    idx = block_indices(X.shape[0], b, B, rng)
    R = corr_batch(X[idx])
    if not np.isfinite(R).all():
        raise HardFail("degenerate bootstrap draw (a constant column)")
    return R


def base_verdict(delta, used):
    """4.1 for one (delta, boot_sd_used): returns (category, reason)."""
    lo95, hi95 = delta - Z95 * used, delta + Z95 * used
    lo90, hi90 = delta - Z90 * used, delta + Z90 * used
    shift = (lo95 > 0 or hi95 < 0) and abs(delta) >= SHIFT_FLOOR
    elo, ehi = (lo95, hi95) if _mut("ci95_equiv") else (lo90, hi90)
    equiv = elo >= -EQ_MARGIN and ehi <= EQ_MARGIN
    if shift and equiv:
        if _mut("no_overlap_branch"):
            return "SHIFT", ""
        return "INCONCLUSIVE", "overlap"
    if shift:
        return "SHIFT", ""
    if equiv:
        return "NO SHIFT AS LARGE AS 0.15", ""
    return "INCONCLUSIVE", ""


def final_verdict(cats, flags):
    """cats = {8: (category, reason), 4: ..., 12: ...}; flags = {'d1': bool, 'd2': .., 'd3': .., 'd5': ..}. Returns (verdict, reasons).
    d4 (a block length of 4 or 12 gives a different category from 8) is computed here; mde and build use this one function."""
    cat, why = cats[CONST["block_len"]]
    d4 = any(cats[b][0] != cat for b in CONST["block_checks"])
    reasons = [why] if why else []
    f = dict(flags)
    f["d4"] = d4
    reasons += [k for k in ("d1", "d2", "d3", "d4", "d5") if f.get(k)]
    verdict = "INCONCLUSIVE" if any(f.get(k) for k in ("d1", "d2", "d3", "d4", "d5")) else cat
    return verdict, reasons


def boot_sd_used(boot_sd, placebo_sd, n_layouts, k_infl):
    """Primary path: max(boot_sd, placebo_sd). Fallback below the minimum number of placebo layouts: k_infl x boot_sd. -> (used, calibration, k)."""
    if n_layouts >= CONST["min_layouts"]:
        if _mut("no_placebo_floor"):
            return boot_sd, "placebo_floor", 1.0
        return max(boot_sd, placebo_sd), "placebo_floor", 1.0
    return k_infl * boot_sd, "fallback_k", k_infl


def d2_exceeded(dropped, n_cal):
    return dropped > CONST["d2_max_drop"] * n_cal


PLACEBO_F0 = dt.date.fromisoformat(CONST["span_from"])
PLACEBO_N = (dt.date.fromisoformat(CONST["span_to"]) - PLACEBO_F0).days // 7 + 1  # 1,064 weeks


def placebo_layouts(panel, names, stat, nA, gap, nC):
    """Historical placebo (3.5): the same difference on windows laid out like the pair (nA weeks, a gap, nC weeks), pre-2018 history only,
    starts stepped by 13 weeks. A layout that fails d2 (or has fewer than 20 usable weeks) is excluded and listed."""
    deltas, excluded = [], []
    total = nA + gap + nC
    for s in range(0, PLACEBO_N - total + 1, CONST["step"]):
        fa = [PLACEBO_F0 + dt.timedelta(days=7 * (s + i)) for i in range(nA)]
        fc = [PLACEBO_F0 + dt.timedelta(days=7 * (s + nA + gap + i)) for i in range(nC)]
        ea, ec = eval_set(panel, names, fa), eval_set(panel, names, fc)
        drop_a = len(ea["gap_weeks"]) + len(ea["miss_weeks"])
        drop_c = len(ec["gap_weeks"]) + len(ec["miss_weeks"])
        if d2_exceeded(drop_a, nA) or d2_exceeded(drop_c, nC) or len(ea["used"]) < 20 or len(ec["used"]) < 20:
            excluded.append((s, fa[0], drop_a, drop_c))
            continue
        deltas.append(stat_X(stat, ec["X"], names) - stat_X(stat, ea["X"], names))
    starts = len(range(0, PLACEBO_N - total + 1, CONST["step"])) if PLACEBO_N >= total else 0
    return dict(deltas=deltas, excluded=excluded, starts=starts)


def rms(xs):
    """Root mean square about ZERO (3.5): the placebo spread counts the historical regime differences as noise. Mutant: SD about the mean."""
    if not xs:
        return None
    if _mut("sd_about_mean"):
        m = sum(xs) / len(xs)
        return float(math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs)))
    return float(math.sqrt(sum(x * x for x in xs) / len(xs)))


# ----------------------------------------------------------------------------------------------------------------------
# seams (2.4) and freshness
# ----------------------------------------------------------------------------------------------------------------------
def compute_seam(series, name, old_prints, old_rows, new_prints, new_rows):
    """Where an archive file meets the current-period file. overlap_agree / overlap_disagree when they share dates; otherwise no_overlap with
    a continuity check: continuous, seam_gap (weekdays missing) or seam_jump (the one-day change across the seam is outside the 99.9th
    percentile of absolute daily changes over the preceding 500 prints)."""
    first_new = min(new_rows) if new_rows else min(new_prints)
    last_old = max(old_rows) if old_rows else max(old_prints)
    shared = sorted(set(old_prints) & set(new_prints))
    out = dict(series=series, name=name, date=first_new, last_old=last_old, n_shared=len(shared), status="", continuity="", detail="")
    if shared:
        bad = [d for d in shared if abs(old_prints[d] - new_prints[d]) > 0.0005 + 1e-12]
        out["status"] = "overlap_disagree" if bad else "overlap_agree"
        out["detail"] = "%d shared dates, %d differ by more than 0.0005pp" % (len(shared), len(bad))
        return out
    out["status"] = "overlap_agree" if _mut("seam_pass") else "no_overlap"
    if _mut("nocontinuity"):
        out["continuity"] = "continuous"
        return out
    if next_weekday(last_old) != first_new:
        out["continuity"] = "seam_gap"
        out["detail"] = "%d weekday(s) missing between the files" % max(0, bdays_after(last_old, first_new) - 1)
        return out
    od = sorted(old_prints)[-501:]
    diffs = np.abs(np.diff([old_prints[d] for d in od]))
    jump = abs(new_prints[min(new_prints)] - old_prints[od[-1]])
    if len(diffs) >= 50 and jump > float(np.percentile(diffs, 99.9)):
        out["continuity"] = "seam_jump"
        out["detail"] = "one-day change across the seam is outside the 99.9th percentile of the preceding %d daily changes" % len(diffs)
    else:
        out["continuity"] = "continuous"
        out["detail"] = "the newer file starts on the next weekday"
    return out


def seam_label(s):
    return ("no_overlap+" + s["continuity"]) if s["status"] == "no_overlap" else s["status"]


def seam_check_status(s):
    if s["status"] == "overlap_agree":
        return "PASS"
    if s["status"] == "overlap_disagree" or s["continuity"] == "seam_gap" or s["continuity"] == "seam_jump":
        return "FAIL" if s["status"] == "overlap_disagree" else "WARN"
    return "INFO"


def seam_bad(s):
    return s["status"] == "overlap_disagree" or s["continuity"] == "seam_gap"


def freshness_rows(daily, asof, seams):
    rows = []
    for s in DAILY_SERIES:
        if s not in daily or not daily[s]:
            continue
        last = max(daily[s])
        lag = bdays_after(last, asof)
        stale = lag > CONST["d1_stale_bdays"] and not _mut("nostale")
        sm = [x for x in seams if x["series"] == s]
        rows.append(dict(source=ISSUER[s], series=s, last_obs=last, asof=asof, lag_bdays=lag, max_lag_bdays=CONST["d1_stale_bdays"],
                         status="stale" if stale else "fresh", seam=SEAM_OF.get(s, "") if sm else "", seam_status=seam_label(sm[0]) if sm else ""))
    return rows


# ----------------------------------------------------------------------------------------------------------------------
# the analysis: windows, pairs, the shift test and its descriptive companions
# ----------------------------------------------------------------------------------------------------------------------
def sets_effective():
    s = {k: list(v) for k, v in SETS.items()}
    if _mut("us_bei_in_set"):
        s["nom4_usreal"].append("us_bei")
    return s


def validate_set(names):
    """G8: no breakeven series exists in this build, and a set never holds a series that is a linear combination of others."""
    for n in names:
        if n.endswith("_bei") or "breakeven" in n:
            raise HardFail("breakeven series %s may not enter a set beside nominal and real columns" % n)
    if len(set(names)) != len(names):
        raise HardFail("duplicate series in a set")


DESCRIPTIVE_COMPARISONS = (("w2018_19", "w2022_23"), ("w2022_23", "w2024_latest"), ("w2024_25", "w2026_ytd"))
STAT_SERIES = NOM4 + ["us_real", "ea_aaa"]


class Analysis:
    def __init__(self, daily, asof, seams, B=None, k_infl=None, panel=None):
        self.daily, self.asof, self.seams = daily, asof, list(seams)
        for names in sets_effective().values():
            validate_set(names)
        self.B = B or CONST["boot_draws"]
        self.k_infl = k_infl or CONST["k_author"]
        self.panel = panel or Panel(daily, asof)
        self.fresh = freshness_rows(daily, asof, self.seams)
        self.stale = any(r["status"] == "stale" for r in self.fresh if r["series"] in NOM4)
        self.latest = latest_common_friday(self.panel, NOM4, asof)
        if self.latest is None:
            raise HardFail("no week in which all four primary series have a print")
        self.wins = resolve_windows(asof, self.latest)
        self._ev, self._plac, self._sw = {}, {}, {}

    # -- evaluation caches
    def ev(self, sname, win):
        k = (sname, win)
        if k not in self._ev:
            self._ev[k] = eval_set(self.panel, SETS[sname], self.wins[win])
        return self._ev[k]

    def sw(self, name, win):
        k = (name, win)
        if k not in self._sw:
            self._sw[k] = series_window(self.panel, name, self.wins[win])
        return self._sw[k]

    def ends_latest(self, win):
        return dict((w[0], w[2]) for w in CONST["windows"])[win] == "latest"

    def seam_fail(self, win):
        fr = self.wins[win]
        if not fr:
            return False
        lo, hi = fr[0] - dt.timedelta(days=6), fr[-1]
        return any(seam_bad(s) and lo <= s["date"] <= hi for s in self.seams)

    def geom(self, wf, wt):
        fa, fb = self.wins[wf], self.wins[wt]
        return len(fa), (fb[0] - fa[-1]).days // 7 - 1, len(fb)

    def placebo(self, sname, stat, geom):
        k = (sname, stat, geom)
        if k not in self._plac:
            self._plac[k] = placebo_layouts(self.panel, SETS[sname], stat, *geom)
        return self._plac[k]

    # -- window status (descriptive rows) and the d1-d5 flags (primary)
    def window_status(self, win, sname, ev):
        names = SETS[sname]
        if self.stale and self.ends_latest(win):
            return "stale_end"
        if self.seam_fail(win):
            return "seam_fail"
        floor = D5_FLOOR.get(win)
        n = len(ev["used"])
        if n < 20 or d2_exceeded(len(ev["gap_weeks"]) + len(ev["miss_weeks"]), ev["n_cal"]) or (floor is not None and n < floor):
            return "low_n"
        for nm in names:
            sd = self.sw(nm, win)["sd"]
            if sd is None or sd < CONST["d3_min_sd_bp"]:
                return "low_sd"
        return "ok"

    def flags(self):
        wf, wt = CONST["primary_from"], CONST["primary_to"]
        evs = [self.ev(CONST["primary_set"], wf), self.ev(CONST["primary_set"], wt)]
        d2 = any(d2_exceeded(len(e["gap_weeks"]) + len(e["miss_weeks"]), e["n_cal"]) for e in evs)
        d3 = any(self.sw(nm, w)["sd"] is None or self.sw(nm, w)["sd"] < CONST["d3_min_sd_bp"] for w in (wf, wt) for nm in NOM4)
        d5 = self.seam_fail(wf) or self.seam_fail(wt) or len(evs[0]["used"]) < D5_FLOOR[wf] or len(evs[1]["used"]) < D5_FLOOR[wt]
        return dict(d1=self.stale, d2=d2, d3=d3, d5=d5)

    # -- tables
    def window_tables(self):
        wrows, prows, srows = [], [], []
        b = CONST["block_len"]
        for win in W_NAMES:
            fr = self.wins[win]
            for sname in SET_ORDER:
                names = SETS[sname]
                ev = self.ev(sname, win)
                n = len(ev["used"])
                row = dict(window=win, series_set=sname, k=len(names), asof=self.asof, first_week=ev["used"][0] if n else None,
                           last_week=ev["used"][-1] if n else None, weeks_calendar=len(fr), weeks_used=n, dropped_gap=len(ev["gap_weeks"]),
                           dropped_missing=len(ev["miss_weeks"]), lambda1=None, lambda1_share=None, rho_mean=None, rho_min=None,
                           rho_max=None, share_ci95_lo=None, share_ci95_hi=None, block_len=b, boot_draws=self.B,
                           status=self.window_status(win, sname, ev))
                if n >= 20:
                    R = corr_matrix(ev["X"])
                    share = share_from_R(R)
                    k = len(names)
                    off = R[np.triu_indices(k, 1)]
                    rng = np.random.default_rng(SEED)
                    Rb = boot_R(ev["X"], b, self.B, rng)
                    sd = float(np.std(stat_Rb("lambda1_share", Rb, names), ddof=1))
                    row.update(lambda1=share * k, lambda1_share=share, rho_mean=float(off.mean()), rho_min=float(off.min()),
                               rho_max=float(off.max()), share_ci95_lo=share - Z95 * sd, share_ci95_hi=share + Z95 * sd)
                    if sname in ("nom4", "nom4_usreal"):
                        for i in range(k):
                            for j in range(i + 1, k):
                                if sname == "nom4_usreal" and "us_real" not in (names[i], names[j]):
                                    continue
                                psd = float(np.std(Rb[:, i, j], ddof=1))
                                prows.append(dict(window=win, series_set=sname, pair="%s-%s" % (names[i], names[j]), n=n, rho=float(R[i, j]),
                                                  ci95_lo=max(-1.0, float(R[i, j]) - Z95 * psd), ci95_hi=min(1.0, float(R[i, j]) + Z95 * psd)))
                wrows.append(row)
            for nm in STAT_SERIES:
                sw = self.sw(nm, win)
                srows.append(dict(window=win, series=nm, n_changes=sw["n"], sd_bp=sw["sd"], dropped_gap=sw["gap"], missing_weeks=sw["miss"]))
        return wrows, prows, srows

    def shift_row(self, role, stat, sname, wf, wt, b):
        names = SETS[sname]
        ea, eb = self.ev(sname, wf), self.ev(sname, wt)
        if len(ea["used"]) < 20 or len(eb["used"]) < 20:
            return None
        va, vb = stat_X(stat, ea["X"], names), stat_X(stat, eb["X"], names)
        delta = vb - va
        rng = np.random.default_rng(SEED)
        Ra, Rb = boot_R(ea["X"], b, self.B, rng), boot_R(eb["X"], b, self.B, rng)
        bsd = float(np.std(stat_Rb(stat, Rb, names) - stat_Rb(stat, Ra, names), ddof=1))
        pl = self.placebo(sname, stat, self.geom(wf, wt))
        psd = rms(pl["deltas"])
        nl = len(pl["deltas"])
        used, cal, kinf = boot_sd_used(bsd, psd if psd is not None else 0.0, nl, self.k_infl)
        return dict(comparison="%s->%s" % (wf, wt), role=role, statistic=stat, series_set=sname, window_from=wf, window_to=wt, value_from=va,
                    value_to=vb, delta=delta, boot_sd=bsd, placebo_sd=psd, placebo_layouts=nl, boot_sd_used=used, calibration=cal,
                    inflation_k=kinf, ci95_lo=delta - Z95 * used, ci95_hi=delta + Z95 * used, ci90_lo=delta - Z90 * used,
                    ci90_hi=delta + Z90 * used, block_len=b, boot_draws=self.B, verdict="descriptive", downgrade_reasons="")

    def shift_tables(self):
        wf, wt, ps = CONST["primary_from"], CONST["primary_to"], CONST["primary_set"]
        b0 = CONST["block_len"]
        rows = []
        prim = {b: self.shift_row("primary" if b == b0 else "block_check", "lambda1_share", ps, wf, wt, b) for b in (b0,) + tuple(CONST["block_checks"])}
        if any(r is None for r in prim.values()):
            raise HardFail("a primary window has fewer than 20 usable weeks")
        cats = {b: base_verdict(r["delta"], r["boot_sd_used"]) for b, r in prim.items()}
        flags = self.flags()
        verdict, reasons = final_verdict(cats, flags)
        prim[b0]["verdict"] = verdict
        prim[b0]["downgrade_reasons"] = ";".join(reasons) if reasons else "none"
        for b in CONST["block_checks"]:
            prim[b]["verdict"] = cats[b][0]
            prim[b]["downgrade_reasons"] = cats[b][1] or "none"
        rows += [prim[b0]] + [prim[b] for b in CONST["block_checks"]]
        for stat, sname, role in (("lambda1_share", "nom3_ex_jgb", "interpretation"), ("jgb_mean_rho", "nom4", "interpretation"),
                                  ("lambda1_share", "nom4_ecb", "robustness"), ("lambda1_share", "nom4_jgb_lead1", "robustness")):
            r = self.shift_row(role, stat, sname, wf, wt, b0)
            if r is not None:
                rows.append(r)
        for a, c in DESCRIPTIVE_COMPARISONS:
            r = self.shift_row("descriptive", "lambda1_share", "nom4", a, c, b0)
            if r is not None:
                rows.append(r)
        r = self.shift_row("descriptive", "lambda1_share", "nom4_usreal", wf, wt, b0)
        if r is not None:
            rows.append(r)
        if _mut("second_primary"):
            rows[-1]["role"] = "primary"
        return rows, flags, cats

    def run(self):
        wrows, prows, srows = self.window_tables()
        shift, flags, cats = self.shift_tables()
        return dict(windows=wrows, pairs=prows, series=srows, shift=shift, fresh=self.fresh, flags=flags, cats=cats, asof=self.asof,
                    latest=self.latest, wins=self.wins, analysis=self)


# ----------------------------------------------------------------------------------------------------------------------
# outputs: exact allowlists, leak guard, source line
# ----------------------------------------------------------------------------------------------------------------------
# The fallback multiplier the second `mde` run (1,000 replications, 18 Oct 2026) gave: the smallest grid value holding every in-grid scenario at or
# below 0.05 (3.0 left 0.052 in rho 0.5, phi 0.97, sdlog 0.6). Larger than the spec author's 3.0, so it is the one used (spec 3.5). Fixed before any real-data build.
K_INFL_FROM_MDE = 3.25
SD4_COLS = {"boot_sd", "placebo_sd", "boot_sd_used"}
SD1_COLS = {"sd_bp"}
INT_COLS = {"k", "weeks_calendar", "weeks_used", "dropped_gap", "dropped_missing", "block_len", "boot_draws", "n", "n_changes", "missing_weeks",
            "placebo_layouts", "lag_bdays", "max_lag_bdays"}


def fmt_cell(col, v):
    if v is None:
        return ""
    if isinstance(v, (dt.date, dt.datetime)):
        return v.isoformat()
    if col in INT_COLS:
        return str(int(v))
    if col in SD4_COLS:
        return fmt(v, 4)
    if col in SD1_COLS:
        return fmt(v, 1)
    if col == "inflation_k":
        return fmt(v, 2)
    if isinstance(v, (float, np.floating)):
        return fmt(v, 3)
    return str(v)


def shape_rows(name, raw):
    cols = allowlist(name)
    out = []
    for r in raw:
        d = {c: fmt_cell(c, r.get(c)) for c in cols}
        if _mut("extra_col") and name == "windows.csv":
            d["us_nom_level"] = "0"
        out.append(d)
    return out


def write_csv(path, name, rows, source_line):
    """Every output starts with the # source: line, then a header that must equal the allowlist exactly (R2)."""
    allow = allowlist(name)
    fields = list(rows[0].keys()) if rows else list(allow)
    if fields != allow:
        raise HardFail("%s: header %r differs from its allowlist %r" % (name, fields, allow))
    if len(rows) > max_rows():
        raise HardFail("%s: %d data rows exceeds the leak-guard limit of %d" % (name, len(rows), max_rows()))
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write(source_line.rstrip("\n") + "\n")
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def read_csv_file(path):
    """(source line or None, header, rows) of one committed CSV."""
    src, lines = None, []
    for line in open(path, encoding="utf-8").read().splitlines():
        if line.startswith("#"):
            src = src or line
        elif line.strip():
            lines.append(line)
    if not lines:
        return src, [], []
    rows = list(csv.reader(lines))
    return src, rows[0], rows[1:]


DATE_CELL = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}Z)?$")


def leak_guard(dirpath):
    """Problems in an output directory (G16): a CSV with more than 80 data rows, a header off its allowlist, an unknown CSV (a weekly panel),
    or a column holding dates that is not one of the named date columns. A free-text cell that merely mentions a date is not a date column."""
    problems = []
    for fn in sorted(os.listdir(dirpath)):
        if not fn.endswith(".csv"):
            continue
        _, header, rows = read_csv_file(os.path.join(dirpath, fn))
        if fn not in ALLOW:
            problems.append("%s: not an allowed output file" % fn)
            continue
        if header != allowlist(fn):
            problems.append("%s: header is not its allowlist" % fn)
        if len(rows) > max_rows():
            problems.append("%s: %d data rows (limit %d)" % (fn, len(rows), max_rows()))
        for j, col in enumerate(header):
            cells = [r[j] for r in rows if j < len(r) and r[j].strip()]
            if cells and sum(1 for c in cells if DATE_CELL.match(c.strip())) * 2 >= len(cells) and col not in DATE_COLS.get(fn, set()):
                problems.append("%s: column %s holds dates and is not on the date allowlist" % (fn, col))
    return problems


def read_log(cache):
    p = os.path.join(cache, "fetch_log.csv")
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def asof_from_log(rows):
    ok = [r["utc"][:10] for r in rows if r["status"] == "200"]
    return dt.date.fromisoformat(max(ok)) if ok else None


def source_line(rows):
    parts = []
    for note in ISSUER_NOTES:
        issuer = note.split(" (")[0]
        host = HOST_OF_ISSUER[issuer]
        dates = [r["utc"][:10] for r in rows if r["host"] == host and r["status"] == "200"]
        parts.append("%s, retrieved %s" % (note, max(dates) if dates else "not fetched"))
    return "# source: " + "; ".join(parts) + ". Derived statistics only; CC BY 4.0 covers only this computation. Source: Deutsche Bundesbank."


def committed_fetch_rows(rows):
    last = {}
    for r in rows:
        last[(r["host"], r["path"])] = r
    out = sorted(last.values(), key=lambda r: (r["utc"], r["path"]))
    return [{c: r[c] for c in ALLOW["fetch_log.csv"]} for r in out]


def write_panel(path, analysis):
    """The weekly panel (changes in bp, blanks missing) -> the cache. It is never written under the repository."""
    cols = ["us_nom", "us_real", "bund_nom", "gilt_nom", "jgb_nom", "ea_aaa", "jgb_lead1"]
    f0 = PLACEBO_F0
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["week_ending"] + cols)
        for fr in fridays(f0, analysis.latest):
            k = wk(fr)
            w.writerow([fr.isoformat()] + [fmt(analysis.panel.s[c]["chg"][k], 4) if (c in analysis.panel.s and k in analysis.panel.s[c]["chg"]) else "" for c in cols])


def emit(res, outdir, meta):
    """Write every committed output of one analysis. meta: source_line, checks (list of dicts), fetch_rows (list of dicts), readme (text)."""
    os.makedirs(outdir, exist_ok=True)
    src = meta["source_line"]
    fresh = [dict(r) for r in res["fresh"]]
    write_csv(os.path.join(outdir, "windows.csv"), "windows.csv", shape_rows("windows.csv", res["windows"]), src)
    write_csv(os.path.join(outdir, "pairs.csv"), "pairs.csv", shape_rows("pairs.csv", res["pairs"]), src)
    write_csv(os.path.join(outdir, "shift_test.csv"), "shift_test.csv", shape_rows("shift_test.csv", res["shift"]), src)
    write_csv(os.path.join(outdir, "series_stats.csv"), "series_stats.csv", shape_rows("series_stats.csv", res["series"]), src)
    write_csv(os.path.join(outdir, "freshness.csv"), "freshness.csv", shape_rows("freshness.csv", fresh), src)
    write_csv(os.path.join(outdir, "checks.csv"), "checks.csv", shape_rows("checks.csv", meta["checks"]), src)
    write_csv(os.path.join(outdir, "fetch_log.csv"), "fetch_log.csv", shape_rows("fetch_log.csv", meta["fetch_rows"]), src)
    if meta.get("readme") is not None:
        with open(os.path.join(outdir, "README.md"), "w", encoding="utf-8") as f:
            f.write(meta["readme"])
    if _mut("panel_in_data"):
        write_panel(os.path.join(outdir, "weekly_panel.csv"), res["analysis"])


def publish_outputs(res, outdir, meta):
    """Write every output into a staging directory beside outdir, run the leak guard there, and only then move the files into outdir.
    A refusal leaves outdir untouched and removes the staged files, so an offending file is never left in the output folder."""
    if _mut("leave_leak"):
        emit(res, outdir, meta)
        problems = leak_guard(outdir)
        if problems:
            raise HardFail("leak guard: " + "; ".join(problems))
        return
    parent = os.path.dirname(os.path.abspath(outdir))
    os.makedirs(parent, exist_ok=True)
    stage = tempfile.mkdtemp(prefix=".r15_stage_", dir=parent)
    try:
        emit(res, stage, meta)
        problems = leak_guard(stage)
        if problems:
            raise HardFail("leak guard: " + "; ".join(problems))
        os.makedirs(outdir, exist_ok=True)
        for fn in sorted(os.listdir(stage)):
            os.replace(os.path.join(stage, fn), os.path.join(outdir, fn))
    finally:
        shutil.rmtree(stage, ignore_errors=True)


# ----------------------------------------------------------------------------------------------------------------------
# README (generated by build so every number in it is the build's own)
# ----------------------------------------------------------------------------------------------------------------------
def _shift_clear(r):
    return (r["ci95_lo"] > 0 or r["ci95_hi"] < 0) and abs(r["delta"]) >= SHIFT_FLOOR


def _inside(r):
    return r["ci90_lo"] >= -EQ_MARGIN and r["ci90_hi"] <= EQ_MARGIN


def interpretation(res):
    """4.3, pre-written: returns the sentence the README may print, or None."""
    rows = {(r["series_set"], r["statistic"], r["role"]): r for r in res["shift"]}
    prim = rows[(CONST["primary_set"], "lambda1_share", "primary")]
    n3 = rows.get(("nom3_ex_jgb", "lambda1_share", "interpretation"))
    if n3 is None or prim["verdict"] != "SHIFT":
        return None
    if _inside(n3):
        return "The change in the four-country share is carried by the JGB leg; the US, Bund and gilt share did not move by as much as 0.15."
    if _shift_clear(n3) and (n3["delta"] > 0) == (prim["delta"] > 0):
        return "The change is not only Japan's."
    return None


def robustness_notes(res):
    prim = [r for r in res["shift"] if r["role"] == "primary"][0]
    notes = []
    for r in res["shift"]:
        if r["role"] == "robustness" and abs(r["delta"] - prim["delta"]) >= CONST["robust_delta"] - 1e-12:
            notes.append("%s moves the change to %s (primary %s): a difference of 0.05 or more." % (r["series_set"], fmt(r["delta"]), fmt(prim["delta"])))
    return notes


def _missing_series(an, f):
    """Which nom4 series lack a print (or a change) in the week ending f, for the README's account of dropped weeks."""
    k = wk(f)
    return [n for n in NOM4 if n not in an.panel.s or k not in an.panel.s[n]["w"]]


def make_readme(res, meta):
    shift = res["shift"]
    an = res["analysis"]
    prim = [r for r in shift if r["role"] == "primary"][0]
    one = lambda role, stat, sset: [r for r in shift if r["role"] == role and r["statistic"] == stat and r["series_set"] == sset]
    n3 = one("interpretation", "lambda1_share", "nom3_ex_jgb")
    jr = one("interpretation", "jgb_mean_rho", "nom4")
    wmap = {(w["window"], w["series_set"]): w for w in res["windows"]}
    wf, wt = CONST["primary_from"], CONST["primary_to"]
    a, b = wmap[(wf, "nom4")], wmap[(wt, "nom4")]
    mde = 2.8 * prim["boot_sd_used"]
    pl = an.placebo(CONST["primary_set"], "lambda1_share", an.geom(wf, wt))
    pd_ = pl["deltas"]
    L = []
    L.append("# Do the four big 10-year yields move together more than they did in 2018-19?")
    L.append("")
    L.append("This folder measures how much of the week-to-week movement in the 10-year government bond yields of the United States, Germany "
             "(the German federal government bond, the Bund), the United Kingdom (the gilt) and Japan (the Japanese government bond, JGB) is shared by "
             "all four, and tests one question registered in advance: was that shared part different in 2024 to date from what it was in 2018-19? "
             "Only derived statistics are published here. No yield level and no weekly change is.")
    L.append("")
    L.append("## Result (as of %s)" % res["asof"].isoformat())
    L.append("")
    cal = ("the historical placebo floor (%d pre-2018 window layouts; placebo spread %s, bootstrap spread %s, used %s)"
           % (prim["placebo_layouts"], fmt(prim["placebo_sd"], 4), fmt(prim["boot_sd"], 4), fmt(prim["boot_sd_used"], 4))
           if prim["calibration"] == "placebo_floor" else
           "the pre-registered fallback (fewer than 20 usable pre-2018 layouts, so the bootstrap spread %s is multiplied by %s to give %s)"
           % (fmt(prim["boot_sd"], 4), fmt(prim["inflation_k"], 2), fmt(prim["boot_sd_used"], 4)))
    L.append("**Verdict: %s.** Share of the correlation matrix's trace taken by the common component of the four weekly changes: %s in 2018-19 "
             "(%s of %s weeks used) and %s in 2024 to %s (%s of %s weeks used). Change %s; 95%% interval [%s, %s]; 90%% interval [%s, %s]. Calibration: %s. "
             "Downgrade reasons: %s. Grade: MEASURED for the shares, and a pre-registered test result for the shift."
             % (prim["verdict"], fmt(a["lambda1_share"]), a["weeks_used"], a["weeks_calendar"], fmt(b["lambda1_share"]),
                b["last_week"].isoformat() if b["last_week"] else "", b["weeks_used"], b["weeks_calendar"], fmt(prim["delta"]), fmt(prim["ci95_lo"]),
                fmt(prim["ci95_hi"]), fmt(prim["ci90_lo"]), fmt(prim["ci90_hi"]), cal,
                ("none fired; neither the SHIFT condition nor the equivalence condition holds" if (prim["downgrade_reasons"] == "none" and prim["verdict"] == "INCONCLUSIVE")
                 else prim["downgrade_reasons"])))
    L.append("")
    L.append("The rule, written before any 2018-or-later statistic was computed: SHIFT if the 95% interval excludes zero and the change is at least 0.10; "
             "NO SHIFT AS LARGE AS 0.15 if the 90% interval lies inside plus or minus 0.15; otherwise INCONCLUSIVE (also when both hold, or when a "
             "stale series, heavy week loss, a near-flat series, a different answer at another block length, or a bad file seam undermines it).")
    if prim["calibration"] == "placebo_floor" and prim["boot_sd_used"] < 0.091:
        L.append("")
        L.append("The equivalence verdict (NO SHIFT AS LARGE AS 0.15) was reachable: it needs the used spread below 0.091, and it was %s." % fmt(prim["boot_sd_used"], 4))
    if prim["calibration"] == "placebo_floor" and prim["boot_sd_used"] >= 0.091:
        L.append("")
        L.append("With a used spread of %s, the equivalence verdict (NO SHIFT AS LARGE AS 0.15) was out of reach: it needs the used spread below 0.091. "
                 "The only possible verdicts were SHIFT and INCONCLUSIVE." % fmt(prim["boot_sd_used"], 4))
    L.append("")
    L.append("## Terms")
    L.append("")
    L.append("- **Trace.** The sum of the diagonal of the correlation matrix. With one 1.0 per series it equals the number of series (4 here), so the "
             "share is the largest eigenvalue divided by 4.")
    L.append("- **Bootstrap spread.** The standard deviation of the change in the share when blocks of 8 consecutive weeks are resampled within each "
             "window, 2,000 times. It measures sampling noise inside these two windows only.")
    L.append("- **Layouts and placebo spread.** A layout is a pair of pre-2018 windows placed like the real pair: 104 weeks, a gap of 209 weeks, then %d "
             "weeks. Starts are stepped by 13 weeks through 1997-2017, giving %d layouts. The placebo spread is the root mean square, about zero, of the "
             "change in the share across those layouts: how far apart two windows this far apart typically differed before 2018. The layouts overlap "
             "heavily%s, so the placebo spread is itself imprecise."
             % (len(an.wins[wt]), prim["placebo_layouts"], " (at 47 layouts only 2 are mutually disjoint)" if prim["placebo_layouts"] == 47 else ""))
    L.append("- **Used spread.** The larger of the bootstrap spread and the placebo spread. Intervals are the change plus or minus 1.96 (95%) or 1.645 (90%) "
             "times it.")
    L.append("- **TIPS.** US Treasury Inflation-Protected Securities; the 10-year TIPS real yield enters only one descriptive set.")
    L.append("")
    L.append("## How to read the number")
    L.append("")
    L.append("- **Scale.** The share is 0.25 for four unrelated series and 1.0 for four moving in lockstep.")
    L.append("- **Noise floor.** In a finite sample, unrelated series still show some correlation, so their share sits about 0.31 at 104 weeks and "
             "0.30 at 146 weeks, not 0.25 (synthetic: means over 4,000 draws of four independent t(5) series, spread 0.019 and 0.016).")
    L.append("- **Denominators.** The share is the largest eigenvalue of the correlation matrix divided by its trace, which is the number of series: "
             "4 for the main set, 3 without Japan, 5 with the TIPS yield. Correlations, not covariances, so a series' scale does not matter. "
             "A two-series figure (for example 0.88) has denominator 2 and cannot be compared with these.")
    miss = [(f, _missing_series(an, f)) for f in an.ev(CONST["primary_set"], wf)["miss_weeks"]]
    gaps = list(an.ev(CONST["primary_set"], wf)["gap_weeks"])
    if a["weeks_used"] < a["weeks_calendar"]:
        why = ""
        if miss and all(s == ["jgb_nom"] for _, s in miss) and all(f.month in (4, 5) for f, _ in miss):
            why = (" The JGB has no print in the week ending %s (Japan's Golden Week holidays), so that week is lost, and the change into the next "
                   "week (ending %s) is dropped because its earlier print is not in the immediately preceding week."
                   % (miss[0][0].isoformat(), gaps[0].isoformat() if gaps else "the following Friday"))
        L.append("- **Weeks used.** %d of %d calendar weeks in 2018-19: every week needs a valid change in all four series (listwise).%s"
                 % (a["weeks_used"], a["weeks_calendar"], why))
    L.append("- **The verdict compares two realised regimes.** It asks whether 2024 to date differs from 2018-19 by more than windows this far apart "
             "differed in the history before 2018. It does not estimate a permanent parameter. A SHIFT says these two periods differed, not that the world "
             "changed for good.")
    if pd_:
        pos = sum(1 for x in pd_ if x > 0)
        L.append("- **The placebo changes are mostly positive, but the spread is measured about zero.** Across the %d layouts the change in the share has "
                 "minimum %s, median %s and maximum %s, and %d of %d are above zero. The placebo spread (%s) is the root mean square about zero, not the "
                 "standard deviation about their mean (which would be %s, smaller), so history's own regime differences (1998, 2008, 2013, the 2016 cap on JGB "
                 "yields) count as noise and the bar for a SHIFT is higher. Because the layouts overlap, it could be dominated by one episode (spec OPEN-4)."
                 % (len(pd_), fmt(min(pd_)), fmt(float(np.median(pd_))), fmt(max(pd_)), pos, len(pd_), fmt(prim["placebo_sd"], 4),
                    fmt(float(np.std(pd_)), 4)))
    L.append("")
    L.append("### This test cannot detect small changes")
    L.append("")
    L.append("At the spread used here (%s) the smallest change the test would catch 80%% of the time is about 2.8 x %s = %s. A true change smaller than "
             "that will usually come back INCONCLUSIVE, which does not mean nothing changed. A change in Japan's link to the other three is below it "
             "too (see the Japan note below)." % (fmt(prim["boot_sd_used"], 4), fmt(prim["boot_sd_used"], 4), fmt(mde)))
    L.append("")
    L.append("## Descriptive results (intervals, no verdict)")
    L.append("")
    L.append("| window | series set | weeks used / calendar | share | 95% interval | mean pairwise correlation | status |")
    L.append("|---|---|---|---|---|---|---|")
    for w in res["windows"]:
        if w["series_set"] == "nom4":
            L.append("| %s | nom4 | %d / %d | %s | [%s, %s] | %s | %s |" % (w["window"], w["weeks_used"], w["weeks_calendar"], fmt(w["lambda1_share"]),
                                                                       fmt(w["share_ci95_lo"]), fmt(w["share_ci95_hi"]), fmt(w["rho_mean"]), w["status"]))
    L.append("")
    if n3:
        r = n3[0]
        L.append("- Without Japan (US, Bund, gilt; k = 3): %s in 2018-19, %s in 2024 to date; change %s, 95%% interval [%s, %s], 90%% interval [%s, %s]."
                 % (fmt(r["value_from"]), fmt(r["value_to"]), fmt(r["delta"]), fmt(r["ci95_lo"]), fmt(r["ci95_hi"]), fmt(r["ci90_lo"]), fmt(r["ci90_hi"])))
    if jr:
        r = jr[0]
        width = r["ci95_hi"] - r["ci95_lo"]
        L.append("- **Japan note.** The mean correlation of the JGB with the US, Bund and gilt was already %s in 2018-19 and was %s in 2024 to date: a change of %s, "
                 "with a 95%% interval of [%s, %s] (calibration: %s; placebo spread %s). That interval is %s wide and is too wide to say anything: "
                 "this build cannot tell a fall in Japan's link to the others from no change, nor a rise. The smallest change in that correlation it could "
                 "catch is about 2.8 x %s = %s. What the build can see is limited to the four-country share, which mostly reflects the US-Bund-gilt block "
                 "(without Japan the share is %s and %s); a change in Japan's correlation moves it by well under the smallest detectable change above."
                 % (fmt(r["value_from"]), fmt(r["value_to"]), fmt(r["delta"]), fmt(r["ci95_lo"]), fmt(r["ci95_hi"]), r["calibration"],
                    fmt(r["placebo_sd"], 4), fmt(width), fmt(r["boot_sd_used"], 4), fmt(2.8 * r["boot_sd_used"]),
                    fmt(n3[0]["value_from"]) if n3 else "n/a", fmt(n3[0]["value_to"]) if n3 else "n/a"))
    sent = interpretation(res)
    if sent:
        L.append("- " + sent)
    for note in robustness_notes(res):
        L.append("- Robustness flag: " + note)
    L.append("- Other comparisons (2018-19 to 2022-23, 2022-23 to 2024-latest, 2024-25 to 2026 year to date, and the same pair with the TIPS yield "
             "added) are in `shift_test.csv`, role `descriptive`.")
    L.append("- The Bank of Japan capped the 10-year yield in part of the baseline window. No code depends on its dates.")
    L.append("- **Timing caveat.** The Japanese yield is the 3pm Tokyo close, which is about a trading day earlier than the other three. The descriptive "
             "set `nom4_jgb_lead1` moves it to the next Tokyo close; it and the euro-area-AAA variant `nom4_ecb` are robustness checks only.")
    L.append("")
    L.append("## What this cannot say")
    L.append("")
    L.append("- Which country drives the others. Correlation has no direction, and no lead-lag is estimated.")
    L.append("- That a \"global term premium\" or any flow caused a move. Nothing here is regressed on a flow or position.")
    L.append("- How much of a cumulative level move (for example the US rise since end-2023) is \"global\". A share of weekly-change variation does not split a level change.")
    L.append("- Anything from covariance or variance shares. They are not computed, because the four series are different objects: a par yield, "
             "a Svensson zero-coupon yield, a continuously compounded spot yield and a constant-maturity yield.")
    L.append("- Small changes (see above).")
    L.append("")
    L.append("## Files")
    L.append("")
    L.append("`windows.csv`, `pairs.csv`, `shift_test.csv`, `series_stats.csv`, `freshness.csv`, `checks.csv` (the pins, identities, seams and the checkpoint "
             "re-derivation), `fetch_log.csv`, `SOURCES.md`. Every CSV starts with a `# source:` line and has an exact column allowlist. "
             "`python3 bin/r15_yield_comovement.py selftest` needs no network; `fetch --archive` then `build` regenerates everything from the five issuers. "
             "The raw files live outside the repository (`~/r15_yield_cache/`) and are never committed.")
    L.append("")
    return "\n".join(L)


# ----------------------------------------------------------------------------------------------------------------------
# the cache: loading, vintages, checks
# ----------------------------------------------------------------------------------------------------------------------
SERIES_OF_KIND = {"us_nom": "us_nom", "us_real": "us_real", "bund": "bund_nom", "mof_all": "jgb_nom", "mof_cur": "jgb_nom",
                  "boe_archive": "gilt_nom", "boe_latest": "gilt_nom", "ecb": "ea_aaa"}
FIXED_FILES = {"bund_nom.csv": "bund", "jgb_all.csv": "mof_all", "jgb_current.csv": "mof_cur", "boe_archive.zip": "boe_archive",
               "boe_latest.zip": "boe_latest", "ecb_ea_aaa.csv": "ecb"}


def kind_of(fn):
    m = re.match(r"^(us_nom|us_real)_(\d{4})\.csv$", fn)
    if m:
        return m.group(1)
    return FIXED_FILES.get(fn)


def parse_file(kind, body):
    """-> (prints, row dates or None)."""
    if kind in ("boe_archive", "boe_latest"):
        return parse_boe_zip(body)
    text = body.decode("utf-8-sig", errors="replace")
    if kind == "us_nom":
        return parse_treasury(text, "nom"), None
    if kind == "us_real":
        return parse_treasury(text, "real"), None
    if kind == "bund":
        return parse_bundesbank(text), None
    if kind in ("mof_all", "mof_cur"):
        return parse_mof(text)
    if kind == "ecb":
        return parse_ecb(text), None
    raise ParseError("unknown kind %s" % kind)


def load_cache(cache, progress=None):
    """Parse the cached raw files. -> dict(daily, seams, kinds, vint). Raises HardFail when a file or a year is missing."""
    say = progress or (lambda s: None)
    cache = check_cache(cache)
    names = sorted(os.listdir(cache))
    for fn in FIXED_FILES:
        if fn not in names:
            raise HardFail("cache file %s is missing: run `fetch --archive` first" % fn)
    years = {"us_nom": [], "us_real": []}
    for fn in names:
        m = re.match(r"^(us_nom|us_real)_(\d{4})\.csv$", fn)
        if m:
            years[m.group(1)].append(int(m.group(2)))
    for kind, first in (("us_nom", 1997), ("us_real", 2017)):
        ys = sorted(years[kind])
        if not ys or ys[0] > first or ys != list(range(ys[0], ys[-1] + 1)) or ys[0] != first:
            raise HardFail("cache lacks Treasury %s years %d..current (has %r): run `fetch --archive`" % (kind, first, ys))
    parsed = {}
    for fn in names:
        k = kind_of(fn)
        if k is None:
            continue
        say("  parsing %s" % fn)
        parsed[fn] = (k,) + parse_file(k, open(os.path.join(cache, fn), "rb").read())
    daily = {s: {} for s in DAILY_SERIES}
    for fn in sorted(parsed):
        k, prints, _ = parsed[fn]
        if k in ("us_nom", "us_real", "bund", "ecb"):
            daily[SERIES_OF_KIND[k]].update(prints)
    seams = []
    m_all, m_cur = parsed["jgb_all.csv"], parsed["jgb_current.csv"]
    daily["jgb_nom"].update(m_all[1])
    daily["jgb_nom"].update(m_cur[1])
    seams.append(compute_seam("jgb_nom", "mof_all|mof_current", m_all[1], m_all[2], m_cur[1], m_cur[2]))
    b_arc, b_lat = parsed["boe_archive.zip"], parsed["boe_latest.zip"]
    daily["gilt_nom"].update(b_arc[1])
    daily["gilt_nom"].update(b_lat[1])
    seams.append(compute_seam("gilt_nom", "boe_archive|boe_latest", b_arc[1], b_arc[2], b_lat[1], b_lat[2]))
    return dict(daily=daily, seams=seams, parsed=parsed, cache=cache)


def vintage_compare(cache, parsed):
    """K20: per series, over dates shared by a cached file and its previous vintage, the count revised by more than 0.005pp and the largest
    revision in bp. -> {series: (n_shared, n_revised, max_bp)} or None when there is no previous vintage at all."""
    agg, any_prev = {}, False
    for fn, (k, prints, _) in sorted(parsed.items()):
        prevs = sorted((p for p in os.listdir(cache) if p.startswith(fn + ".") and p.endswith(".prev")),
                       key=lambda p: os.path.getmtime(os.path.join(cache, p)))
        if not prevs:
            continue
        any_prev = True
        old, _ = parse_file(k, open(os.path.join(cache, prevs[-1]), "rb").read())
        sh = set(old) & set(prints)
        a = agg.setdefault(SERIES_OF_KIND[k], [0, 0, 0.0])
        a[0] += len(sh)
        for d in sh:
            diff = abs(prints[d] - old[d])
            if diff > 0.005 + 1e-12:
                a[1] += 1
            a[2] = max(a[2], diff * 100.0)
    return {s: tuple(v) for s, v in agg.items()} if any_prev else None


PINS = {
    "us_nom": [("2023-12-29", 3.88), ("2026-01-02", 4.19), ("2026-07-31", 4.75), ("2026-09-18", 5.01), ("2026-10-16", 5.09)],
    "us_real": [("2023-12-29", 1.72), ("2026-09-18", 2.68), ("2026-10-16", 2.74)],
    "bund_nom": [("2018-01-02", 0.50), ("2023-12-29", 2.06), ("2026-01-02", 2.96), ("2026-07-31", 3.21), ("2026-10-16", 3.48)],
    "jgb_nom": [("2018-01-04", 0.052), ("2023-12-29", 0.647), ("2026-09-30", 3.057), ("2026-10-13", 3.019), ("2026-10-15", 2.948)],
    "gilt_nom": [("2018-01-02", 1.3498), ("2023-12-29", 3.5803), ("2026-07-31", 5.1040), ("2026-09-30", 5.4028), ("2026-10-15", 5.3435)],
    "ea_aaa": [("2018-01-02", 0.5376), ("2026-10-01", 3.5922)],
}
PIN_WARN_ONLY = ("bund_nom", "gilt_nom")  # may have been revised
G4_FRIDAYS = fridays(dt.date(2026, 1, 9), dt.date(2026, 7, 31))
G4_EXPECT = dict(n=30, sums=(56, 53, 25), corr=(0.76, 0.88, 0.72))


def chk(cid, desc, expected="", observed="", status="INFO", pin_date=""):
    return dict(check_id=cid, description=desc, pin_date=pin_date, expected=expected, observed=observed, status=status)


def pin_checks(daily):
    rows = []
    for s, pins in PINS.items():
        for d, exp in pins:
            v = daily.get(s, {}).get(dt.date.fromisoformat(d))
            if v is None:
                st, obs = ("WARN" if s in PIN_WARN_ONLY else "FAIL"), "no print on that date"
            elif abs(v - exp) <= 0.005 + 1e-9:
                st, obs = "PASS", "%.4f" % v
            else:
                st, obs = ("WARN" if s in PIN_WARN_ONLY else "FAIL"), "%.4f" % v + ("; may have revised" if s in PIN_WARN_ONLY else "")
            rows.append(chk("PIN_%s_%s" % (s, d), "%s %s verification checkpoint (pp, tolerance 0.005)" % (ISSUER[s], s), "%g" % exp, obs, st, d))
    return rows


def build_checks(res, ld, log_rows, cache):
    an = res["analysis"]
    daily = ld["daily"]
    rows = pin_checks(daily)
    # 3.4 identities and the singularity guard, on every correlation matrix the build used
    mt = me = 0.0
    mineig = 9.0
    for w in res["windows"]:
        if w["weeks_used"] >= 20:
            R = corr_matrix(an.ev(w["series_set"], w["window"])["X"])
            t, s = identity_errors(R)
            mt, me = max(mt, t), max(me, s)
            mineig = min(mineig, float(np.linalg.eigvalsh(R)[0]))
    rows.append(chk("I1_trace", "trace of every correlation matrix minus k, largest absolute value over all windows and sets", "< 1e-8", "%.2e" % mt, "PASS" if mt < 1e-8 else "FAIL"))
    rows.append(chk("I2_eigsum", "sum of eigenvalues minus k, largest absolute value", "< 1e-8", "%.2e" % me, "PASS" if me < 1e-8 else "FAIL"))
    rows.append(chk("I3_mineig", "smallest eigenvalue over all correlation matrices (singularity guard)", "> 1e-6", "%.4f" % mineig, "PASS" if mineig > 1e-6 else "FAIL"))
    # seams
    for s in res["analysis"].seams:
        rows.append(chk("S_%s" % s["name"].replace("|", "_"), "seam %s: %s" % (s["name"], s["detail"] or s["status"]), "overlap_agree or no_overlap+continuous",
                        seam_label(s), seam_check_status(s)))
    # K20 vintages
    v = vintage_compare(ld["cache"], ld["parsed"])
    if v is None:
        rows.append(chk("K20_vintage", "dates revised by more than 0.005pp against the previous cached vintage", "informational", "no previous vintage (first fetch)", "INFO"))
    else:
        rows.append(chk("K20_vintage", "dates revised by more than 0.005pp against the previous cached vintage; largest revision in bp", "informational",
                        "; ".join("%s: %d of %d dates, max %.1fbp" % (s, a[1], a[0], a[2]) for s, a in sorted(v.items())), "INFO"))
    # K30-K32: the g4 re-derivation
    names = ["us_nom", "us_real", "bund_nom"]
    ev = eval_set(an.panel, names, G4_FRIDAYS)
    n = len(ev["used"])
    X = ev["X"]
    sums = tuple(int(round(float(X[:, i].sum()))) for i in range(3)) if n else ()
    cr = corr_matrix(X) if n >= 3 else None
    obs_c = (round(float(cr[0, 2]), 2), round(float(cr[0, 1]), 2), round(float(cr[1, 2]), 2)) if cr is not None else ()
    rows.append(chk("K30_g4_count", "g4 re-derivation, weeks ending 2026-01-09..2026-07-31 under the 3.1 gap rule: weeks with a change in all three of us_nom, us_real, bund_nom",
                    "30", str(n), "PASS" if n == G4_EXPECT["n"] else "FAIL"))
    rows.append(chk("K31_g4_sums", "g4 re-derivation: sums of the weekly changes in bp (us_nom, us_real, bund_nom)", "+56 / +53 / +25",
                    " / ".join("%+d" % x for x in sums), "PASS" if sums == G4_EXPECT["sums"] else "FAIL"))
    rows.append(chk("K32_g4_corr", "g4 re-derivation: correlations us_nom-bund_nom / us_nom-us_real / us_real-bund_nom", "0.76 / 0.88 / 0.72",
                    " / ".join("%.2f" % x for x in obs_c), "PASS" if obs_c == G4_EXPECT["corr"] else "FAIL"))
    # week counts (8.5) and placebo layouts (8.6), expectations that hold at the spec's as-of date
    wmap = {(w["window"], w["series_set"]): w for w in res["windows"]}
    cal = tuple(wmap[(w, "nom4")]["weeks_calendar"] for w in ("w2018_19", "w2022_23", "w2024_latest"))
    dr = (wmap[("w2018_19", "nom4")]["dropped_gap"] + wmap[("w2018_19", "nom4")]["dropped_missing"],
          wmap[("w2024_latest", "nom4")]["dropped_gap"] + wmap[("w2024_latest", "nom4")]["dropped_missing"])
    at_spec = res["asof"] == dt.date(2026, 10, 18)
    st = ("PASS" if cal == (104, 104, 146) else "WARN") if at_spec else "INFO"
    rows.append(chk("K40_weeks_calendar", "weeks_calendar for w2018_19 / w2022_23 / w2024_latest (expectation holds at as-of 2026-10-18)", "104 / 104 / 146",
                    " / ".join(str(x) for x in cal), st))
    ev0, ev1 = an.ev("nom4", "w2018_19"), an.ev("nom4", "w2024_latest")
    lst = "; ".join("%s" % d.isoformat() for d in ev0["gap_weeks"] + ev0["miss_weeks"] + ev1["gap_weeks"] + ev1["miss_weeks"])
    st = ("PASS" if dr == (2, 0) else "WARN") if at_spec else "INFO"
    rows.append(chk("K41_dropped", "weeks dropped from nom4 in w2018_19 / w2024_latest (gap plus missing); weeks listed: %s" % (lst or "none"),
                    "2 / 0", "%d / %d" % dr, st))
    pl = an.placebo(CONST["primary_set"], "lambda1_share", an.geom(CONST["primary_from"], CONST["primary_to"]))
    nl = len(pl["deltas"])
    nC = len(an.wins[CONST["primary_to"]])
    st = ("PASS" if nl == 47 else "WARN") if nC == 146 else "INFO"
    rows.append(chk("K42_placebo_layouts", "placebo layouts used for the primary (of %d laid out, n_C = %d)" % (pl["starts"], nC), "47 at n_C = 146", str(nl), st))
    rows.append(chk("K43_placebo_excluded", "placebo layouts excluded by d2 (start week; weeks dropped in the 104-week and the n_C-week window)", "listed",
                    "; ".join("%s:%d/%d" % (e[1].isoformat(), e[2], e[3]) for e in pl["excluded"]) or "none", "INFO"))
    if pl["deltas"]:
        q = (min(pl["deltas"]), float(np.median(pl["deltas"])), max(pl["deltas"]))
        rows.append(chk("K44_placebo_quantiles", "OPEN-4: placebo change in the nom4 share, min / median / max, and the RMS about zero", "read before the primary change",
                        "%.3f / %.3f / %.3f ; rms %.4f" % (q + (rms(pl["deltas"]),)), "INFO"))
    # fetch bookkeeping
    stop = os.path.exists(STOP_PATH)
    rows.append(chk("K45_requests", "requests logged in the cache's fetch_log.csv (all runs)", "<= 46", str(len(log_rows)), "PASS" if len(log_rows) <= 46 else "WARN"))
    rows.append(chk("K46_stop", "STOP latch present", "absent", "present" if stop else "absent", "FAIL" if stop else "PASS"))
    rows.append(chk("K47_asof", "as-of date (UTC date of the newest successful row in fetch_log.csv)", "informational", res["asof"].isoformat(), "INFO"))
    # K50: the verdict recomputed from delta, boot_sd_used, the block checks and the downgrade flags
    prim = [r for r in res["shift"] if r["role"] == "primary"][0]
    cats = {r["block_len"]: base_verdict(r["delta"], r["boot_sd_used"]) for r in res["shift"] if r["role"] in ("primary", "block_check")}
    verdict, reasons = final_verdict(cats, res["flags"])
    rows.append(chk("K50_verdict_recompute", "primary verdict recomputed mechanically from delta, boot_sd_used, the b = 4 and 12 rows and d1-d5", prim["verdict"], verdict,
                    "PASS" if verdict == prim["verdict"] else "FAIL"))
    notes = robustness_notes(res)
    rows.append(chk("K51_robustness_flag", "robustness sets that move the primary change by 0.05 or more", "informational", "; ".join(notes) or "none", "INFO"))
    if len(rows) > max_rows():
        raise HardFail("checks.csv would have %d rows" % len(rows))
    return rows


# ----------------------------------------------------------------------------------------------------------------------
# commands
# ----------------------------------------------------------------------------------------------------------------------
def cmd_fetch(cache, archive, missing_only=False):
    cache = check_cache(cache)
    if os.path.exists(STOP_PATH):
        print("STOP exists at %s: no fetch happens while it exists, and only a person deletes it." % tilde(STOP_PATH))
        return 2
    cur = utcnow().year
    plan = fetch_plan(cur, archive)
    f = Fetcher(cache)
    total = 0
    t0 = time.time()
    for i, (kind, fn, url) in enumerate(plan, 1):
        host, path = check_url(url)
        if missing_only and os.path.exists(os.path.join(cache, fn)):
            print("[%d/%d] %s already cached, skipped (--missing-only)" % (i, len(plan), fn))
            continue
        try:
            dest, nbytes = f.get(kind, fn, url)
        except Latched as e:
            print("[%d/%d] %s%s: %s" % (i, len(plan), host, path[:60], e))
            print("STOP: the run ends. Nothing retries. Tell the principal; only a person deletes %s." % tilde(STOP_PATH))
            return 3
        except SocketFault as e:
            print("[%d/%d] %s%s: socket fault (%s). The run ends without a latch; re-run later." % (i, len(plan), host, path[:60], e))
            return 4
        except MaxRequests as e:
            print(str(e))
            return 5
        total += nbytes
        print("[%d/%d] %s%s -> %s  %d bytes" % (i, len(plan), host, path[:70], fn, nbytes))
    print("fetch done: %d requests, %d bytes, %.0f s. Cache: %s" % (f.n, total, time.time() - t0, tilde(cache)))
    return 0


def cmd_calibrate(cache, k_infl):
    """Offline, pre-2018 history only: the placebo layouts for the primary geometry and their spread. No 2018-or-later statistic is computed;
    only which weeks have prints (existence) is read from later data, to size the n_C-week window."""
    cache = check_cache(cache)
    rows = read_log(cache)
    asof = asof_from_log(rows)
    if asof is None:
        raise HardFail("fetch_log.csv has no successful row: run fetch first")
    ld = load_cache(cache, progress=print)
    daily = ld["daily"]
    full = Panel(daily, asof)
    latest = latest_common_friday(full, NOM4, asof)
    wins = resolve_windows(asof, latest)
    wf, wt = CONST["primary_from"], CONST["primary_to"]
    nA, nC = len(wins[wf]), len(wins[wt])
    gap = (wins[wt][0] - wins[wf][-1]).days // 7 - 1
    cutoff = dt.date(2017, 12, 31)
    pre = Panel({n: {d: v for d, v in p.items() if d <= cutoff} for n, p in daily.items()}, cutoff)
    print("calibration on pre-2018 history: as-of %s; primary geometry %d + %d + %d weeks; span %s..%s (%d weeks); step %d"
          % (asof, nA, gap, nC, CONST["span_from"], CONST["span_to"], PLACEBO_N, CONST["step"]))
    out = {}
    for sname, stat in (("nom4", "lambda1_share"), ("nom3_ex_jgb", "lambda1_share"), ("nom4", "jgb_mean_rho"), ("nom4_jgb_lead1", "lambda1_share"),
                        ("nom4_ecb", "lambda1_share"), ("nom4_usreal", "lambda1_share")):
        pl = placebo_layouts(pre, SETS[sname], stat, nA, gap, nC)
        d = pl["deltas"]
        out[(sname, stat)] = pl
        path = "placebo_floor" if len(d) >= CONST["min_layouts"] else "FALLBACK k_infl=%.2f" % max(k_infl, CONST["k_author"])
        if d:
            print("  %-15s %-14s layouts %2d of %2d (excluded %d); placebo_sd(rms about 0) %.4f; delta min/median/max %.3f/%.3f/%.3f -> %s"
                  % (sname, stat, len(d), pl["starts"], len(pl["excluded"]), rms(d), min(d), float(np.median(d)), max(d), path))
        else:
            print("  %-15s %-14s layouts  0 of %2d (excluded %d) -> %s" % (sname, stat, pl["starts"], len(pl["excluded"]), path))
    pl = out[("nom4", "lambda1_share")]
    if pl["excluded"]:
        print("  nom4 layouts excluded by d2 (start week, weeks dropped in the 104-week / n_C-week window): "
              + "; ".join("%s:%d/%d" % (e[1], e[2], e[3]) for e in pl["excluded"]))
    return 0


def cmd_build(cache, out, B, k_infl):
    if constants_sha() != CONST_ANCHOR:
        raise HardFail("the constants block does not hash to the anchor in the spec: refusing to build")
    spec_block = spec_constants_block()
    if spec_block is not None and spec_block != render_constants():
        raise HardFail("the constants block differs from the landed spec's block: refusing to build")
    cache = check_cache(cache)
    rows = read_log(cache)
    asof = asof_from_log(rows)
    if asof is None:
        raise HardFail("fetch_log.csv has no successful row: run fetch first")
    if os.path.exists(STOP_PATH):
        print("note: STOP exists at %s (build is offline and goes on)" % tilde(STOP_PATH))
    t0 = time.time()
    ld = load_cache(cache, progress=print)
    an = Analysis(ld["daily"], asof, ld["seams"], B=B, k_infl=k_infl)
    res = an.run()
    checks = build_checks(res, ld, rows, cache)
    meta = dict(source_line=source_line(rows), checks=checks, fetch_rows=committed_fetch_rows(rows))
    meta["readme"] = make_readme(res, meta)
    os.makedirs(os.path.join(cache, "derived"), exist_ok=True)
    write_panel(os.path.join(cache, "derived", "weekly_panel.csv"), an)
    publish_outputs(res, out, meta)
    prim = [r for r in res["shift"] if r["role"] == "primary"][0]
    print("build done in %.0f s; as-of %s; outputs in %s" % (time.time() - t0, asof, os.path.relpath(out, ROOT) if out.startswith(ROOT) else out))
    print("PRIMARY: %s share %s -> %s, delta %s, boot_sd %s, placebo_sd %s (%d layouts), used %s [%s], verdict %s (%s)"
          % (prim["series_set"], fmt(prim["value_from"]), fmt(prim["value_to"]), fmt(prim["delta"]), fmt(prim["boot_sd"], 4), fmt(prim["placebo_sd"], 4),
             prim["placebo_layouts"], fmt(prim["boot_sd_used"], 4), prim["calibration"], prim["verdict"], prim["downgrade_reasons"]))
    bad = [c for c in checks if c["status"] in ("FAIL", "WARN")]
    for c in bad:
        print("  %s %s: expected %s, observed %s" % (c["status"], c["check_id"], c["expected"], c["observed"]))
    return 0


# ----------------------------------------------------------------------------------------------------------------------
# mde: the synthetic false-SHIFT and power tables (4.5) and the fallback k_infl (3.5). No market data.
# ----------------------------------------------------------------------------------------------------------------------
MDE_B = 300
MDE_REPS = 1000
MDE_POWER_REPS = 300
T5_SCALE = math.sqrt(5.0 / 3.0)


def k_grid():
    n = int(round((CONST["grid_hi"] - CONST["grid_lo"]) / CONST["grid_step"]))
    return [CONST["grid_lo"] + i * CONST["grid_step"] for i in range(n + 1)]


def sim_window(n, rho, phi, sdlog, rng):
    """x_i = sqrt(rho) sigma_t f_t + sqrt(1-rho) e_i; f, e unit-variance t(5); log sigma_t AR(1) with persistence phi and stationary SD sdlog."""
    f = rng.standard_t(5, n) / T5_SCALE
    e = rng.standard_t(5, (n, 4)) / T5_SCALE
    if phi == 0:
        sig = np.ones(n)
    else:
        z = rng.standard_normal(n)
        lv = np.empty(n)
        lv[0] = sdlog * z[0]
        c = sdlog * math.sqrt(1.0 - phi * phi)
        for t in range(1, n):
            lv[t] = phi * lv[t - 1] + c * z[t]
        sig = np.exp(lv)
    return math.sqrt(rho) * (sig * f)[:, None] + math.sqrt(1.0 - rho) * e


def sim_pair(rho_a, rho_c, phi, sdlog, rng, B, n_a=104, n_c=146):
    A = sim_window(n_a, rho_a, phi, sdlog, rng)
    C = sim_window(n_c, rho_c, phi, sdlog, rng)
    delta = lambda1_share(C) - lambda1_share(A)
    sds = {}
    for b in (CONST["block_len"],) + tuple(CONST["block_checks"]):
        Ra, Rc = boot_R(A, b, B, rng), boot_R(C, b, B, rng)
        sds[b] = float(np.std(np.linalg.eigvalsh(Rc)[:, -1] / 4.0 - np.linalg.eigvalsh(Ra)[:, -1] / 4.0, ddof=1))
    return delta, sds


def shift_rate(reps, k, flags=None):
    hit = 0
    for delta, sds in reps:
        cats = {b: base_verdict(delta, k * sd) for b, sd in sds.items()}
        verdict, _ = final_verdict(cats, flags or {})
        hit += verdict == "SHIFT"
    return hit / len(reps)


def cmd_mde(reps=MDE_REPS, B=MDE_B, power_reps=MDE_POWER_REPS):
    t0 = time.time()
    grid = k_grid()
    rho_l = [float(x) for x in CONST["rho_txt"]]
    phi_l = [float(x) for x in CONST["phi_txt"]]
    sd_l = [float(x) for x in CONST["sdlog_txt"]]
    scen = []
    for rho in rho_l:
        for phi in phi_l:
            for sd in ([sd_l[0]] if phi == 0 else sd_l):
                scen.append((rho, phi, sd, True))
    scen += [(rho, 0.99, 0.6, False) for rho in rho_l]  # outside the grid: reported, not used for k_infl
    print("mde: synthetic only. %d replications x %d bootstrap draws per scenario; n = 104 and 146 weeks; the 4.1 rule including d4 and the 0.10 floor" % (reps, B))
    print("False-SHIFT rate at the null (equal rho in both windows), fallback multiplier k on the bootstrap spread:")
    print("  %-34s" % "scenario" + "".join("%7.2f" % k for k in grid))
    table, med_sd = {}, {}
    for i, (rho, phi, sd, in_grid) in enumerate(scen):
        rng = np.random.default_rng(SEED + 1000 * (i + 1))
        r = [sim_pair(rho, rho, phi, sd, rng, B) for _ in range(reps)]
        rates = [shift_rate(r, k) for k in grid]
        table[(rho, phi, sd, in_grid)] = rates
        med_sd[(rho, phi, sd)] = float(np.median([x[1][CONST["block_len"]] for x in r]))
        lab = "rho %.1f phi %.2f sdlog %s%s" % (rho, phi, "-" if phi == 0 else "%.1f" % sd, "" if in_grid else " (outside grid)")
        print("  %-34s" % lab + "".join("%7.3f" % x for x in rates), flush=True)
    # fallback k_infl: smallest grid value holding the false-SHIFT rate at or below the target in every in-grid scenario
    k_need = None
    for gi, k in enumerate(grid):
        if all(rates[gi] <= CONST["target_false_shift"] + 1e-12 for key, rates in table.items() if key[3]):
            k_need = k
            break
    worst = {k: max(rates[gi] for key, rates in table.items() if key[3]) for gi, k in enumerate(grid)}
    print("Worst in-grid false-SHIFT rate by k: " + ", ".join("%.2f:%.3f" % (k, worst[k]) for k in grid if k in (1.0, 2.0, 2.5, 2.75, 3.0, 3.25, 3.5, 4.0)))
    k_use = max(CONST["k_author"], k_need) if k_need is not None else None
    if k_need is None:
        print("FALLBACK k_infl: no grid value up to %.2f holds the rate at %.2f" % (grid[-1], CONST["target_false_shift"]))
    else:
        print("FALLBACK k_infl: smallest grid value holding every in-grid scenario at or below %.2f is %.2f; the spec author's value is %.1f; the value used is %.2f"
              % (CONST["target_false_shift"], k_need, CONST["k_author"], k_use))
        rr = max(rates[grid.index(k_use)] for key, rates in table.items() if key[3])
        print("  at k = %.2f the worst in-grid false-SHIFT rate is %.3f (%s)" % (k_use, rr, "holds" if rr <= CONST["target_false_shift"] + 1e-12 else "DOES NOT HOLD"))
    print("Bootstrap spread (median, b = 8, n = 146 minus n = 104 difference): " + "; ".join("rho %.1f phi %.2f %s: %.3f" % (k[0], k[1], "-" if k[1] == 0 else "sd%.1f" % k[2], v)
                                                                                         for k, v in sorted(med_sd.items()) if k[0] == rho_l[0]))
    print("Power (SHIFT rate), %d replications; base rho 0.3, the later window's rho raised so the population share rises by the true change:" % power_reps)
    print("  %-8s %-14s %-14s %-14s %-14s" % ("true D", "k=1 phi=0", "k=1 phi=.97", "k=3 phi=0", "k=3 phi=.97"))
    pw = {}
    for j, d in enumerate((0.15, 0.25, 0.35)):
        row = []
        for phi, sd in ((0.0, 0.0), (0.97, 0.6)):
            rng = np.random.default_rng(SEED + 7000 + 100 * j + int(phi * 10))
            r = [sim_pair(0.3, 0.3 + 4.0 * d / 3.0, phi, sd, rng, B) for _ in range(power_reps)]
            row.append((shift_rate(r, 1.0), shift_rate(r, 3.0)))
        pw[d] = row
        print("  %-8.2f %-14.2f %-14.2f %-14.2f %-14.2f" % (d, row[0][0], row[1][0], row[0][1], row[1][1]), flush=True)
    print("MDE at 80%% power is about 2.8 x boot_sd_used: %.2f if the used spread is 0.06 (bootstrap alone, phi = 0), %.2f if 0.10; on the fallback path (k = %.2f) about %.2f or more."
          % (2.8 * 0.06, 2.8 * 0.10, k_use or float("nan"), 2.8 * (k_use or 3.0) * 0.06))
    # d1-d5 pass through the same verdict function: one scenario each sets the flag
    ok = True
    cats_shift = {8: ("SHIFT", ""), 4: ("SHIFT", ""), 12: ("SHIFT", "")}
    for flag in ("d1", "d2", "d3", "d5"):
        v, why = final_verdict(cats_shift, {flag: True})
        good = v == "INCONCLUSIVE" and flag in why
        ok &= good
        print("  downgrade %s: SHIFT -> %s (%s) %s" % (flag, v, ",".join(why), "ok" if good else "WRONG"))
    v, why = final_verdict({8: ("SHIFT", ""), 4: ("INCONCLUSIVE", ""), 12: ("SHIFT", "")}, {})
    good = v == "INCONCLUSIVE" and "d4" in why
    ok &= good
    print("  downgrade d4: SHIFT -> %s (%s) %s" % (v, ",".join(why), "ok" if good else "WRONG"))
    print("mde done in %.0f s" % (time.time() - t0))
    return 0 if ok and k_use is not None else 1


# ----------------------------------------------------------------------------------------------------------------------
# selftest: synthetic fixtures; each guard must PASS clean and FAIL when its mutant is applied
# ----------------------------------------------------------------------------------------------------------------------
D = dt.date


def weekdays(first, last):
    out, d = [], first
    while d <= last:
        if d.weekday() < 5:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def synth_daily(asof, seed=1, first=D(1997, 1, 1), rho=0.4, stale_bund_bdays=0):
    """Six synthetic daily series (random-walk levels; four share a common factor). No market data."""
    rng = np.random.default_rng(seed)
    days = weekdays(first, asof)
    n = len(days)
    f = rng.standard_normal(n)
    chg = {s: 0.04 * (math.sqrt(rho) * f + math.sqrt(1 - rho) * rng.standard_normal(n)) for s in NOM4}
    chg["us_real"] = chg["us_nom"] + 0.01 * rng.standard_normal(n)
    chg["ea_aaa"] = chg["bund_nom"] + 0.01 * rng.standard_normal(n)
    base = {"us_nom": 4.0, "bund_nom": 2.0, "gilt_nom": 3.0, "jgb_nom": 1.0, "ea_aaa": 2.0, "us_real": 1.5}
    out = {}
    for s, c in chg.items():
        lv = base[s] + np.cumsum(c)
        out[s] = {d: round(float(v), 4) for d, v in zip(days, lv)}
    if stale_bund_bdays:
        cut = days[-1 - stale_bund_bdays]
        out["bund_nom"] = {d: v for d, v in out["bund_nom"].items() if d <= cut}
    return out


class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def clock(self):
        return self.t

    def sleep(self, s):
        self.t += s


def fx_opener(responses, clk=None, log=None):
    it = iter(responses)

    def op(url, ua, timeout):
        if log is not None:
            log.append(clk.clock() if clk else 0.0)
        if clk:
            clk.t += 0.5
        r = next(it)
        if isinstance(r, Exception):
            raise r
        return r
    return op


_BASE = {}


def base_analysis():
    """One small analysis of synthetic data, shared by several guards."""
    if "res" not in _BASE:
        asof = D(2026, 10, 18)
        daily = synth_daily(D(2026, 10, 16), seed=11)
        seams = [compute_seam("gilt_nom", "boe_archive|boe_latest", {D(2026, 9, 29): 3.0, D(2026, 9, 30): 3.01}, {D(2026, 9, 29), D(2026, 9, 30)},
                              {D(2026, 10, 1): 3.0}, {D(2026, 10, 1)})]
        an = Analysis(daily, asof, seams, B=80)
        _BASE["an"], _BASE["res"], _BASE["daily"], _BASE["asof"] = an, an.run(), daily, asof
    return _BASE


def g01():
    asof = D(2019, 12, 31)
    pr = synth_daily(asof, seed=3, first=D(2018, 1, 1))["us_nom"]
    recs = change_records(pr, asof)
    assert len(recs) >= 100, "too few changes: %d" % len(recs)
    ends = [r[2] for r in recs]
    assert len(set(ends)) == len(ends), "a daily print ends two changes"
    for r in recs:
        _, mon, end, start, _ = r
        assert not any(d > end and monday_of(d) == mon for d in pr), "change ends on %s, which is not the last print of its week" % end
    for a, b in zip(recs, recs[1:]):
        assert b[3] >= a[2], "changes %s and %s share daily prints" % (a[2], b[2])


def g02():
    asof = D(2019, 12, 31)
    for seed in range(10):
        rng = np.random.default_rng(100 + seed)
        days = weekdays(D(2017, 12, 1), asof)
        daily = {s: {d: float(v) for d, v in zip(days, np.cumsum(rng.standard_normal(len(days))) * 0.04 + 3)} for s in NOM4}
        panel = Panel(daily, asof)
        ev = eval_set(panel, NOM4, fridays(D(2018, 1, 5), D(2019, 12, 27)))
        sh = lambda1_share(ev["X"])
        assert 0.20 <= sh <= 0.40, "four independent random walks gave a share of %.3f" % sh


def g03():
    R = np.full((4, 4), 0.40)
    np.fill_diagonal(R, 1.0)
    sh = share_from_R(R)
    assert abs(sh - 0.55) < 1e-9, "equicorrelation 0.40 gave %.12f" % sh
    t, s = identity_errors(R)
    assert t < 1e-8 and s < 1e-8, "trace or eigenvalue sum is not k"


def g04():
    rng = np.random.default_rng(4)
    X = rng.standard_normal((200, 4)) @ np.array([[1, .3, .2, .1], [0, 1, .3, .2], [0, 0, 1, .4], [0, 0, 0, 1.]])
    a = lambda1_share(X)
    Y = X.copy()
    Y[:, 2] *= 100.0
    b = lambda1_share(Y)
    assert abs(a - b) < 1e-9, "scaling one series by 100 moved the share from %.6f to %.6f" % (a, b)


def _g5_fixture():
    rng = np.random.default_rng(5)
    Z = rng.standard_normal((30, 3))
    Z -= Z.mean(axis=0)
    Q, _ = np.linalg.qr(Z)
    Y = Q * math.sqrt(29.0)
    Rt = np.array([[1, .88, .76], [.88, 1, .72], [.76, .72, 1]])  # order us_nom, us_real, bund_nom
    Y = Y @ np.linalg.cholesky(Rt).T
    X = Y * np.array([7.0, 7.0, 6.0]) + np.array([56.0, 53.0, 25.0]) / 30.0  # bp; sums exactly 56, 53, 25
    mondays = [D(2025, 12, 29) + dt.timedelta(days=7 * w) for w in range(31)]
    miss = {"us_nom": {D(2026, 6, 19), D(2026, 7, 3)}, "us_real": {D(2026, 6, 19), D(2026, 7, 3)}, "bund_nom": {D(2026, 4, 3), D(2026, 5, 1)}}
    daily = {}
    for c, s in enumerate(("us_nom", "us_real", "bund_nom")):
        lev = [4.0]
        for w in range(30):
            lev.append(lev[-1] + X[w, c] / 100.0)
        pr = {}
        for w, m in enumerate(mondays):
            start, end = (lev[w - 1], lev[w]) if w else (lev[0] - 0.05, lev[0])
            days = [m + dt.timedelta(days=i) for i in range(5) if (m + dt.timedelta(days=i)) not in miss[s]]
            for i, d in enumerate(days):
                pr[d] = end if i == len(days) - 1 else start + (end - start) * (i + 1) / 5.0
        daily[s] = pr
    return daily


def g05():
    daily = _g5_fixture()
    asof = D(2026, 8, 7)
    panel = Panel(daily, asof)
    ev = eval_set(panel, ["us_nom", "us_real", "bund_nom"], G4_FRIDAYS)
    assert len(ev["used"]) == 30, "the Good Friday / Juneteenth / 3 July fixture gave %d weeks, not 30" % len(ev["used"])
    kept = [("bund_nom", D(2026, 4, 10)), ("bund_nom", D(2026, 5, 8)), ("us_nom", D(2026, 6, 26)), ("us_nom", D(2026, 7, 10)), ("us_real", D(2026, 7, 10))]
    for s, f in kept:
        assert wk(f) in panel.s[s]["chg"], "the %s change into the week ending %s was dropped" % (s, f)
    sums = tuple(int(round(float(ev["X"][:, i].sum()))) for i in range(3))
    assert sums == (56, 53, 25), "sums %r" % (sums,)
    c = corr_matrix(ev["X"])
    assert (round(c[0, 2], 2), round(c[0, 1], 2), round(c[1, 2], 2)) == (0.76, 0.88, 0.72), "correlations %r" % (c,)
    d2 = {k: dict(v) for k, v in daily.items()}
    for d in list(d2["bund_nom"]):
        if D(2026, 3, 2) <= d <= D(2026, 3, 6):
            del d2["bund_nom"][d]
    ev2 = eval_set(Panel(d2, asof), ["us_nom", "us_real", "bund_nom"], G4_FRIDAYS)
    assert len(ev2["used"]) == 28, "a week with no print should drop itself and the next change (28 weeks), got %d" % len(ev2["used"])
    assert D(2026, 3, 6) in ev2["miss_weeks"] and D(2026, 3, 13) in ev2["gap_weeks"]


def g06():
    plan = fetch_plan(2026, True)
    nom = sorted(int(re.search(r"us_nom_(\d{4})", fn).group(1)) for k, fn, u in plan if k == "us_nom")
    real = sorted(int(re.search(r"us_real_(\d{4})", fn).group(1)) for k, fn, u in plan if k == "us_real")
    assert nom == list(range(1997, 2027)), "nominal years %r" % nom
    assert real == list(range(2017, 2027)), "real years %r" % real
    assert len(plan) == 46, "a full fetch is %d requests, not 46" % len(plan)
    assert len(fetch_plan(2026, False)) == 7, "the default refresh is not 7 requests"
    asof = D(2026, 10, 16)
    daily = synth_daily(asof, seed=6)
    daily["us_nom"] = {d: v for d, v in daily["us_nom"].items() if d.year in nom}
    panel = Panel(daily, asof)
    ev = eval_set(panel, NOM4, fridays(D(2020, 1, 3), D(2021, 12, 31)))
    assert len(ev["used"]) >= 100, "only %d weeks in 2020-21" % len(ev["used"])


def g07():
    asof = D(2026, 10, 18)
    daily = synth_daily(D(2026, 10, 16), seed=7, stale_bund_bdays=8)
    an = Analysis(daily, asof, [], B=60)
    fr = {r["series"]: r for r in an.fresh}
    assert fr["bund_nom"]["lag_bdays"] > 5 and fr["bund_nom"]["status"] == "stale", "bund_nom 8 business days behind is not stale"
    rows = {(w["window"], w["series_set"]): w for w in an.window_tables()[0]}
    assert rows[("w2024_latest", "nom4")]["status"] == "stale_end" and rows[("w2026_ytd", "nom4")]["status"] == "stale_end"
    shift, flags, _ = an.shift_tables()
    prim = [r for r in shift if r["role"] == "primary"][0]
    assert flags["d1"] and prim["verdict"] == "INCONCLUSIVE" and "d1" in prim["downgrade_reasons"], "stale series did not give INCONCLUSIVE (d1)"


def g08():
    for nm, names in sets_effective().items():
        validate_set(names)
    for bad in (["us_nom", "us_real", "us_bei"], ["us_nom", "us_nom"]):
        try:
            validate_set(bad)
        except HardFail:
            continue
        raise AssertionError("validate_set accepted %r" % bad)
    rng = np.random.default_rng(8)
    nom = rng.standard_normal(120)
    real = rng.standard_normal(120)
    X = np.column_stack([nom, real, nom - real])
    try:
        lambda1_share(X)
    except HardFail:
        return
    raise AssertionError("a nominal, a real and their difference was not refused as singular")


BBK_FIXTURE = ("Source: fixture\n;;\n;;\nBBSIS key;" + BBK_KEY + "\nUnit;Prozent\nNote;\nNote;\n;;\nStand vom 16.10.2026 12:13:05 Uhr;;\n"
               "2026-10-14;3,45;\n2026-10-15;3,47;\n2026-10-16;3,48;\n2026-10-17;.;Kein Wert vorhanden\n2026-10-18;.;Kein Wert vorhanden\n")


def g09():
    p = parse_bundesbank(BBK_FIXTURE)
    assert p.get(D(2026, 10, 16)) == 3.48, "decimal comma not parsed: %r" % p
    assert D(2026, 10, 17) not in p and D(2026, 10, 18) not in p, "'.' was read as a value"
    assert len(p) == 3
    en = "last update: 2026-10-16\nkey,value,flag\n2026-10-16,3.48,\n2026-10-17,.,\n"
    pe = parse_bundesbank(en)
    assert pe == {D(2026, 10, 16): 3.48}, "English format: %r" % pe
    assert to_float(".", ",") is None


def g11():
    hdr = {
        "1990": 'Date,"3 Mo","6 Mo","1 Yr","2 Yr","3 Yr","5 Yr","7 Yr","10 Yr","20 Yr","30 Yr"',
        "2023": 'Date,"1 Mo","2 Mo","3 Mo","4 Mo","6 Mo","1 Yr","2 Yr","3 Yr","5 Yr","7 Yr","10 Yr","20 Yr","30 Yr"',
        "2026": 'Date,"1 Mo","1.5 Month","2 Mo","3 Mo","4 Mo","6 Mo","1 Yr","2 Yr","3 Yr","5 Yr","7 Yr","10 Yr","20 Yr","30 Yr"',
    }
    for y, h in hdr.items():
        cols = h.split(",")
        row = ["01/03/2024"] + ["%.2f" % (1.0 + i) for i in range(len(cols) - 1)]
        i10 = [c.strip('"') for c in cols].index("10 Yr")
        row[i10] = "9.99"
        text = h + "\n" + ",".join(row) + "\n"
        got = parse_treasury(text, "nom")
        assert got == {D(2024, 1, 3): 9.99}, "%s-style header gave %r" % (y, got)
    real = 'Date,"5 YR","7 YR","10 YR","20 YR","30 YR"\n10/16/2026,2.50,2.60,2.74,2.80,2.90\n'
    assert parse_treasury(real, "real") == {D(2026, 10, 16): 2.74}


def g12():
    assert parse_treasury('Date,"10 Yr"\n01/02/2024,N/A\n01/03/2024,\n01/04/2024,4.0\n', "nom") == {D(2024, 1, 4): 4.0}
    assert parse_bundesbank(BBK_FIXTURE).get(D(2026, 10, 17)) is None
    mof = "Interest Rate (October 2026)\n(Unit : %)\nDate,1Y,2Y,10Y,30Y\n2026/10/13,0.5,0.9,3.019,3.5\n2026/10/14,0.5,0.9,-,3.5\n2026/10/15,0.5,0.9,,3.5\n"
    p, rows = parse_mof(mof)
    assert p == {D(2026, 10, 13): 3.019} and len(rows) == 3, "MoF markers: %r" % p
    for tok in (".", "-", "N/A", "", None, " "):
        assert to_float(tok) is None, "%r was read as a number" % (tok,)


def _boe_xlsx(sheets):
    import openpyxl
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for name, (mats, val10, fill) in sheets.items():
        ws = wb.create_sheet(name)
        ws.cell(1, 1, "Title")
        ws.cell(4, 1, "years:")
        for j, m in enumerate(mats):
            ws.cell(4, 2 + j, m)
        ws.cell(5, 1, "Refresh")
        r = 6
        for d, v in ((D(2024, 1, 2), val10), (D(2024, 1, 3), val10 + 0.1), (D(2024, 1, 4), None), (D(2024, 1, 5), val10 + 0.2)):
            ws.cell(r, 1, dt.datetime(d.year, d.month, d.day))
            for j, m in enumerate(mats):
                ws.cell(r, 2 + j, (v if (m == 10 and v is not None) else (fill if v is not None else None)))
            r += 1
    bio = io.BytesIO()
    wb.save(bio)
    bio.seek(0)
    return bio


def g10():
    mats_a = [0.5, 1, 2, 5, 10, 20, 40]  # the 10-year column is not at index 20
    a = _boe_xlsx({"info": ([1], 0.0, 0.0), "2. fwd curve": (mats_a, 9.99, 9.99), "4. spot curve": (mats_a, 3.58, 1.0)})
    p, rows = parse_boe_workbook(a)
    assert p == {D(2024, 1, 2): 3.58, D(2024, 1, 3): 3.68, D(2024, 1, 5): 3.78}, "'4. spot curve': %r" % p
    assert len(rows) == 4 and D(2024, 1, 4) not in p, "the holiday's empty cell must be missing"
    mats_b = [float(x) for x in range(1, 26)]  # 10 sits at index 10; 25 maturities
    b = _boe_xlsx({"4. nominal spot curve": (mats_b, 2.5, 1.0)})
    pb, _ = parse_boe_workbook(b)
    assert pb[D(2024, 1, 2)] == 2.5, "'4. nominal spot curve': %r" % pb
    c = _boe_xlsx({"4. spot curve": ([0.5, 10, 10.0], 1.0, 1.0)})
    try:
        parse_boe_workbook(c)
    except ParseError:
        return
    raise AssertionError("two columns equal to 10 were not refused")


def _seam_series(n=600):
    days = weekdays(D(2024, 1, 1), D(2026, 12, 31))[:n]
    rng = np.random.default_rng(13)
    lv = 3.0 + np.cumsum(0.04 * rng.standard_normal(n))
    return days, {d: float(round(v, 4)) for d, v in zip(days, lv)}


def g13():
    days, old = _seam_series()
    rows = set(days)
    last = days[-1]
    s = compute_seam("x", "a|b", old, rows, {last: old[last] + 0.001, next_weekday(last): 3.0}, {last, next_weekday(last)})
    assert s["status"] == "overlap_disagree" and seam_check_status(s) == "FAIL", "an overlap differing by 0.001pp is %s" % s["status"]
    s = compute_seam("x", "a|b", old, rows, {last: old[last] + 0.0004, next_weekday(last): 3.0}, {last, next_weekday(last)})
    assert s["status"] == "overlap_agree", "an overlap within 0.0005pp is %s" % s["status"]
    nxt = next_weekday(last)
    s = compute_seam("x", "a|b", old, rows, {nxt: old[last] + 0.01}, {nxt})
    assert s["status"] == "no_overlap" and s["continuity"] == "continuous" and seam_check_status(s) == "INFO", "next-weekday start: %r" % (s,)
    gap = next_weekday(nxt)
    s = compute_seam("x", "a|b", old, rows, {gap: old[last] + 0.01}, {gap})
    assert s["status"] == "no_overlap" and s["continuity"] == "seam_gap", "a missing weekday must be seam_gap, got %r" % (s,)
    s = compute_seam("x", "a|b", old, rows, {nxt: old[last] + 5.0}, {nxt})
    assert s["continuity"] == "seam_jump" and not seam_bad(s), "a jump is a warning only"
    # d5: a bad seam inside a primary window downgrades the primary; a jump does not
    asof = D(2026, 10, 18)
    daily = synth_daily(D(2026, 10, 16), seed=14)
    bad = dict(series="gilt_nom", name="boe_archive|boe_latest", date=D(2026, 10, 1), status="no_overlap", continuity="seam_gap", detail="", last_old=D(2026, 9, 29), n_shared=0)
    an = Analysis(daily, asof, [bad], B=60)
    assert an.flags()["d5"], "a seam_gap inside w2024_latest did not trigger d5"
    jump = dict(bad, continuity="seam_jump")
    assert not Analysis(daily, asof, [jump], B=60).flags()["d5"], "seam_jump alone must not trigger d5"
    dis = dict(bad, status="overlap_disagree", continuity="")
    assert Analysis(daily, asof, [dis], B=60).flags()["d5"], "overlap_disagree inside the window did not trigger d5"


def g14():
    rng = np.random.default_rng(14)
    for n, b in ((104, 8), (146, 8), (146, 4), (146, 12)):
        idx = block_indices(n, b, 40, np.random.default_rng(5))
        assert idx.shape == (40, n) and idx.min() >= 0 and idx.max() <= n - 1
        for row in idx:
            for s in range(0, n, b):
                run = row[s:s + b]
                assert np.all(np.diff(run) == 1), "resample is not made of runs of %d consecutive rows" % b
    a = block_indices(104, 8, 30, np.random.default_rng(SEED))
    c = block_indices(104, 8, 30, np.random.default_rng(SEED))
    assert np.array_equal(a, c), "the same seed gave different draws"


def g15():
    sha = constants_sha()
    assert sha == CONST_ANCHOR, "the rendered constants hash to %s, not the anchor" % sha
    blk = spec_constants_block()
    if blk is not None:
        assert hashlib.sha256(blk.encode("utf-8")).hexdigest() == CONST_ANCHOR, "the landed spec's block does not hash to the anchor"
        assert blk == render_constants(), "the rendered block differs from the landed spec's block"


def _meta_for(res, daily):
    return dict(source_line="# source: fixture", checks=pin_checks(daily)[:5], fetch_rows=[dict(utc="2026-10-18T10:00:00Z", host="h", path="/p", status="200", bytes="1", sha256="0", note="")])


LITERAL_ALLOW = {
    "windows.csv": ["window", "series_set", "k", "asof", "first_week", "last_week", "weeks_calendar", "weeks_used", "dropped_gap", "dropped_missing",
                    "lambda1", "lambda1_share", "rho_mean", "rho_min", "rho_max", "share_ci95_lo", "share_ci95_hi", "block_len", "boot_draws", "status"],
    "pairs.csv": ["window", "series_set", "pair", "n", "rho", "ci95_lo", "ci95_hi"],
    "shift_test.csv": ["comparison", "role", "statistic", "series_set", "window_from", "window_to", "value_from", "value_to", "delta", "boot_sd",
                       "placebo_sd", "placebo_layouts", "boot_sd_used", "calibration", "inflation_k", "ci95_lo", "ci95_hi", "ci90_lo", "ci90_hi",
                       "block_len", "boot_draws", "verdict", "downgrade_reasons"],
    "series_stats.csv": ["window", "series", "n_changes", "sd_bp", "dropped_gap", "missing_weeks"],
    "freshness.csv": ["source", "series", "last_obs", "asof", "lag_bdays", "max_lag_bdays", "status", "seam", "seam_status"],
    "checks.csv": ["check_id", "description", "pin_date", "expected", "observed", "status"],
    "fetch_log.csv": ["utc", "host", "path", "status", "bytes", "sha256", "note"],
}  # a second, literal copy of spec section 6 (bin/check.sh M12 holds a third); the guard compares the script's tables with it, never with themselves


def g16():
    assert max_rows() == 80, "the leak-guard row limit is %r, not the literal 80" % (max_rows(),)
    for fn, cols in LITERAL_ALLOW.items():
        assert allowlist(fn) == cols, "%s allowlist is %r, not the spec's" % (fn, allowlist(fn))
    b = base_analysis()
    res = b["res"]
    with tempfile.TemporaryDirectory() as td:
        meta = _meta_for(res, b["daily"])
        meta["readme"] = make_readme(res, meta)
        emit(res, td, meta)
        assert leak_guard(td) == [], "leak guard flags the production outputs: %r" % leak_guard(td)
        for fn in os.listdir(td):
            if fn.endswith(".csv"):
                assert len(read_csv_file(os.path.join(td, fn))[2]) <= 80, "%s has more than the literal 80 data rows" % fn
        # positive controls: a planted weekly panel, a planted date column, and a pairs.csv with 81 rows (one over the literal limit)
        with open(os.path.join(td, "weekly_panel.csv"), "w") as f:
            f.write("week_ending,us_nom\n" + "".join("2020-01-%02d,1.0\n" % (i % 28 + 1) for i in range(90)))
        assert leak_guard(td), "the leak guard missed a planted weekly panel"
        os.remove(os.path.join(td, "weekly_panel.csv"))
        p = os.path.join(td, "pairs.csv")
        src, hdr, rows = read_csv_file(p)
        with open(p, "w") as f:
            f.write(src + "\n" + ",".join(hdr) + "\n" + "".join(",".join(r[:2] + ["2020-01-03"] + r[3:]) + "\n" for r in rows[:5]))
        assert leak_guard(td), "the leak guard missed a date column in pairs.csv"
        with open(p, "w") as f:
            f.write(src + "\n" + ",".join(hdr) + "\n" + "".join("w,nom4,a-b,100,0.5,0.4,0.6\n" for _ in range(81)))
        assert leak_guard(td), "the leak guard missed a CSV with 81 data rows"
        try:
            write_csv(os.path.join(td, "x.csv"), "pairs.csv", shape_rows("pairs.csv", [dict(window="w", series_set="s", pair="p", n=1, rho=0.1, ci95_lo=0, ci95_hi=0)] * 81), "# source: x")
        except HardFail:
            return
        raise AssertionError("write_csv wrote 81 data rows")


def g24():
    assert abs(rms([0.1, 0.1, 0.1, 0.1]) - 0.1) < 1e-12, "four equal placebo changes of 0.1 gave a spread of %r (the RMS about zero is 0.1)" % rms([0.1] * 4)
    d = [0.08, 0.02, -0.01, 0.05, 0.11]
    want = math.sqrt(sum(x * x for x in d) / len(d))
    assert abs(rms(d) - want) < 1e-12, "rms %r, not %r" % (rms(d), want)
    # end to end: the placebo_sd the shift test reports is the RMS of that layout's changes about zero
    b = base_analysis()
    an = Analysis(b["daily"], b["asof"], [], B=40)
    wf, wt = CONST["primary_from"], CONST["primary_to"]
    row = an.shift_row("primary", "lambda1_share", CONST["primary_set"], wf, wt, CONST["block_len"])
    deltas = placebo_layouts(an.panel, SETS[CONST["primary_set"]], "lambda1_share", *an.geom(wf, wt))["deltas"]
    want = math.sqrt(sum(x * x for x in deltas) / len(deltas))
    assert len(deltas) >= 20 and abs(row["placebo_sd"] - want) < 1e-12, "placebo_sd %r is not the RMS about zero %r" % (row["placebo_sd"], want)


def g25():
    b = base_analysis()
    res = b["res"]
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "data")
        meta = _meta_for(res, b["daily"])
        with mutated("panel_in_data"):
            try:
                publish_outputs(res, out, meta)
            except HardFail:
                pass
            else:
                raise AssertionError("outputs holding a weekly panel were published")
        left = os.listdir(out) if os.path.isdir(out) else []
        assert not left, "a refused build left %r in the output folder" % left
        assert not [f for f in os.listdir(td) if f.startswith(".r15_stage")], "a staging directory was left behind"
        publish_outputs(res, out, meta)
        assert leak_guard(out) == [] and "windows.csv" in os.listdir(out), "a clean build was not published"


def g17():
    b = base_analysis()
    res = b["res"]
    with tempfile.TemporaryDirectory() as td:
        meta = _meta_for(res, b["daily"])
        emit(res, td, meta)
        for fn, allow in ALLOW.items():
            _, hdr, _ = read_csv_file(os.path.join(td, fn))
            assert hdr == allow, "%s header %r" % (fn, hdr)
        bad = shape_rows("pairs.csv", res["pairs"][:2])
        bad[0]["us_nom_level"] = "1"
        try:
            write_csv(os.path.join(td, "x.csv"), "pairs.csv", bad, "# source: x")
        except HardFail:
            return
        raise AssertionError("a header outside the allowlist was written")


def g18():
    with tempfile.TemporaryDirectory() as td:
        cache, stop = os.path.join(td, "cache"), os.path.join(td, "STOP")
        good = b'Date,"10 Yr"\n01/02/2026,4.19\n'
        url = TREASURY_URL % (2026, "daily_treasury_yield_curve", 2026)
        now = lambda: dt.datetime(2026, 10, 18, 10, 0, 0, tzinfo=dt.timezone.utc)

        def mk(resp, **kw):
            clk = FakeClock()
            calls = []
            f = Fetcher(cache, opener=fx_opener(resp, clk, calls), sleep=clk.sleep, clock=clk.clock, now=now, stop_path=stop, **kw)
            return f, calls

        def reset():
            if os.path.exists(stop):
                os.remove(stop)
        # host allowlist, https only, no sec.gov
        for bad in ("https://example.com/x", "https://www.sec.gov/cgi-bin/x", "http://home.treasury.gov/x", "https://data.sec.gov/x"):
            try:
                check_url(bad)
            except Refused:
                continue
            raise AssertionError("%s was not refused" % bad)
        assert check_url(url)[0] == "home.treasury.gov"
        assert "@" not in UA and PACE_S >= 3.0 and MAX_REQUESTS <= 50
        bad_ua = "agent-x" + chr(64) + "host-y"
        try:
            Fetcher(cache, ua=bad_ua)
        except Refused:
            pass
        else:
            raise AssertionError("a User-Agent holding an address was accepted")
        # cache inside the repository is refused
        for bad in (os.path.join(ROOT, "data", "cachex"), ROOT):
            try:
                check_cache(bad)
            except Refused:
                continue
            raise AssertionError("a cache inside the repository was accepted")
        # a good fetch, then a status other than 200 latches and blocks later fetches
        reset()
        f, calls = mk([(200, {"Last-Modified": "x"}, good)])
        f.get("us_nom", "us_nom_2026.csv", url)
        assert os.path.exists(os.path.join(cache, "us_nom_2026.csv")) and not os.path.exists(stop)
        for label, resp in (("404", (404, {}, b"no")), ("302", (302, {"Location": "https://x"}, b""))):
            reset()
            f, calls = mk([resp])
            try:
                f.get("us_nom", "us_nom_2026.csv", url)
            except Latched:
                pass
            else:
                raise AssertionError("status %s did not raise" % label)
            assert os.path.exists(stop), "status %s did not write the STOP latch" % label
            f2, calls2 = mk([(200, {}, good)])
            try:
                f2.get("us_nom", "us_nom_2026.csv", url)
            except Latched:
                pass
            assert calls2 == [], "a fetch happened while STOP existed (after %s)" % label
        # a failed content test latches
        reset()
        f, _ = mk([(200, {}, b"<html>captcha</html>")])
        try:
            f.get("us_nom", "us_nom_2026.csv", url)
        except Latched:
            pass
        else:
            raise AssertionError("a body failing its content test was accepted")
        assert os.path.exists(stop), "a failed content test did not write STOP"
        # a socket fault ends the run without latching
        reset()
        f, _ = mk([SocketFault("timeout")])
        try:
            f.get("us_nom", "us_nom_2026.csv", url)
        except SocketFault:
            pass
        assert not os.path.exists(stop), "a socket fault wrote STOP"
        # pacing: at least 3 s between request starts
        reset()
        f, calls = mk([(200, {}, good)] * 3)
        for i in range(3):
            f.get("us_nom", "us_nom_2026.csv", url)
        gaps = [b - a for a, b in zip(calls, calls[1:])]
        assert len(gaps) == 2 and min(gaps) >= 3.0 - 1e-9, "requests were %r s apart" % gaps
        # cap
        reset()
        f, _ = mk([(200, {}, good)] * 3, max_requests=2)
        f.get("us_nom", "us_nom_2026.csv", url)
        f.get("us_nom", "us_nom_2026.csv", url)
        try:
            f.get("us_nom", "us_nom_2026.csv", url)
        except MaxRequests:
            pass
        else:
            raise AssertionError("the request cap was not enforced")
        assert len(fetch_plan(2026, True)) <= MAX_REQUESTS
        # an existing latch blocks the very first fetch
        with open(stop, "w") as fh:
            fh.write("x\n")
        f, calls = mk([(200, {}, good)])
        try:
            f.get("us_nom", "us_nom_2026.csv", url)
        except Latched:
            pass
        assert calls == [], "a fetch happened while STOP existed"


def g19():
    asof = D(2018, 12, 31)
    daily = synth_daily(asof, seed=19, first=D(2017, 12, 1))
    bund = {d: v for d, v in daily["bund_nom"].items() if not (D(2018, 3, 12) <= d <= D(2018, 3, 16))}
    daily["bund_nom"] = bund
    panel = Panel(daily, asof)
    fr = fridays(D(2018, 1, 5), D(2018, 12, 28))
    nom4 = eval_set(panel, NOM4, fr)
    no_bund = eval_set(panel, ["us_nom", "gilt_nom", "jgb_nom"], fr)
    w = D(2018, 3, 16)
    assert w not in nom4["used"], "a week with one series missing entered nom4"
    assert w in no_bund["used"], "the same week is missing from a set without that series"


def g20():
    b = base_analysis()
    shift, _, _ = b["an"].shift_tables()
    prim = [r for r in shift if r["role"] == "primary"]
    assert len(prim) == 1, "%d primary rows" % len(prim)
    for r in shift:
        if r["role"] in ("primary", "block_check"):
            assert r["verdict"] in ("SHIFT", "NO SHIFT AS LARGE AS 0.15", "INCONCLUSIVE")
        else:
            assert r["verdict"] == "descriptive", "%s row has verdict %s" % (r["role"], r["verdict"])
    assert sorted(r["block_len"] for r in shift if r["role"] == "block_check") == [4, 12]


def g21():
    cases = [(0.20, 0.03, "SHIFT", ""), (-0.25, 0.05, "SHIFT", ""), (0.08, 0.03, "NO SHIFT AS LARGE AS 0.15", ""),
             (0.11, 0.02, "INCONCLUSIVE", "overlap"), (0.0, 0.10, "INCONCLUSIVE", ""), (0.0, 0.09, "NO SHIFT AS LARGE AS 0.15", ""),
             (0.0, 0.092, "INCONCLUSIVE", ""), (0.10, 0.04, "SHIFT", ""), (0.099, 0.04, "INCONCLUSIVE", ""), (0.12, 0.05, "SHIFT", ""),
             (0.05, 0.05, "NO SHIFT AS LARGE AS 0.15", "")]
    for delta, sd, cat, why in cases:
        got = base_verdict(delta, sd)
        assert got == (cat, why), "delta %.3f sd %.3f -> %r, expected %r" % (delta, sd, got, (cat, why))
    assert boot_sd_used(0.03, 0.08, 47, 3.0) == (0.08, "placebo_floor", 1.0), "boot_sd_used must be max(boot, placebo)"
    assert boot_sd_used(0.09, 0.05, 47, 3.0) == (0.09, "placebo_floor", 1.0)
    assert boot_sd_used(0.03, 0.08, 20, 3.0)[1] == "placebo_floor"
    u, cal, k = boot_sd_used(0.03, 0.08, 19, 3.0)
    assert abs(u - 0.09) < 1e-12 and cal == "fallback_k" and k == 3.0, "below 20 layouts the fallback must apply"
    sh = {8: ("SHIFT", ""), 4: ("SHIFT", ""), 12: ("SHIFT", "")}
    assert final_verdict(sh, {}) == ("SHIFT", [])
    for d in ("d1", "d2", "d3", "d5"):
        v, why = final_verdict(sh, {d: True})
        assert v == "INCONCLUSIVE" and d in why, "%s did not downgrade" % d
    v, why = final_verdict({8: ("SHIFT", ""), 4: ("INCONCLUSIVE", ""), 12: ("SHIFT", "")}, {})
    assert v == "INCONCLUSIVE" and "d4" in why, "d4 did not downgrade"
    v, why = final_verdict({8: ("INCONCLUSIVE", "overlap"), 4: ("INCONCLUSIVE", "overlap"), 12: ("INCONCLUSIVE", "overlap")}, {})
    assert v == "INCONCLUSIVE" and why == ["overlap"]
    assert d2_exceeded(6, 104) and not d2_exceeded(5, 104) and d2_exceeded(8, 146) and not d2_exceeded(7, 146)


def g22():
    pr = {}
    for d in weekdays(D(2020, 12, 14), D(2021, 1, 15)):
        if d != D(2021, 1, 1):
            pr[d] = 1.0 + 0.01 * (d - D(2020, 12, 14)).days
    asof = D(2021, 3, 1)
    assert D(2020, 12, 28).isocalendar()[1] == 53 and D(2020, 12, 31).isocalendar()[:2] == (2020, 53)
    panel = Panel({"x": pr}, asof)
    fr = [D(2020, 12, 25), D(2021, 1, 1), D(2021, 1, 8)]
    ev = eval_set(panel, ["x"], fr)
    assert ev["used"] == fr, "the week-53 / year-turn weeks used %r" % ev["used"]
    w53 = panel.s["x"]["w"][wk(D(2021, 1, 1))]
    assert w53[1] == D(2020, 12, 31), "the ISO 2020-W53 week's last print is %s" % w53[1]
    lo, hi = D(2020, 1, 3), D(2021, 12, 31)
    assert lo <= D(2021, 1, 1) <= hi


def g23():
    asof = D(2026, 10, 15)
    daily = synth_daily(D(2026, 10, 16), seed=23)
    panel = Panel(daily, asof)
    latest = latest_common_friday(panel, NOM4, asof)
    wins = resolve_windows(asof, latest)
    assert latest == D(2026, 10, 9), "latest common week %s with as-of Thursday 10-15" % latest
    assert len(wins["w2024_latest"]) == 145, "weeks_calendar(w2024_latest) = %d, not 145" % len(wins["w2024_latest"])
    assert D(2026, 10, 16) not in wins["w2024_latest"]
    asof2 = D(2026, 10, 16)
    daily2 = synth_daily(D(2026, 10, 19), seed=23)
    for s in NOM4 + ["us_real", "ea_aaa"]:
        if s != "jgb_nom":
            daily2[s] = {d: v for d, v in daily2[s].items() if d <= asof2}
    panel2 = Panel(daily2, asof2)
    k = wk(D(2026, 10, 16))
    assert k in panel2.s["us_nom"]["w"], "the week ending 2026-10-16 is missing from nom4 with as-of Friday 10-16"
    assert k not in panel2.s["jgb_lead1"]["w"], "a JGB lead print dated after the as-of date stayed in nom4_jgb_lead1"
    assert wk(D(2026, 10, 9)) in panel2.s["jgb_lead1"]["w"]


GUARDS = [
    ("G1", "non-overlap: changes come from last-in-week prints, consecutive changes share no daily print", g01, ["rolling5"]),
    ("G2", "changes, not levels: independent random walks give a share in [0.20, 0.40]", g02, ["levels"]),
    ("G3", "denominator: equicorrelation 0.40 gives 0.55; trace and eigenvalue sum = k", g03, ["half"]),
    ("G4", "correlation, not covariance: scaling one series by 100 leaves the share unchanged", g04, ["cov"]),
    ("G5", "gap rule on the Good Friday / Juneteenth / 3 July fixture: 30 weeks, +56/+53/+25, 0.76/0.88/0.72", g05, ["oldgap"]),
    ("G6", "years: the plan covers US 1997..current and the panel has 2020 and 2021", g06, ["g4years"]),
    ("G7", "staleness: bund_nom 8 business days behind gives stale_end and INCONCLUSIVE (d1)", g07, ["nostale"]),
    ("G8", "no breakeven beside nominal and real; singular sets refused", g08, ["us_bei_in_set"]),
    ("G9", "decimal comma: '2026-10-16;3,48;' parses to 3.48; '.' is missing", g09, ["bbk_split_comma", "miss0_dot"]),
    ("G10", "BoE sheet and column: moved 10-year column, '2. fwd curve' decoy, '4. nominal spot curve' name", g10, ["boe_idx20", "boe_fwd", "boe_only_spot"]),
    ("G11", "Treasury by name: 1990-, 2023- and 2026-style headers all give '10 Yr'", g11, ["treasury_positional"]),
    ("G12", "missing markers '.', '-', 'N/A', blank, empty cell are missing, never 0", g12, ["miss0_dot", "miss0_dash", "miss0_na", "miss0_blank"]),
    ("G13", "seams: overlap_disagree / no_overlap+continuous / seam_gap (triggers d5) / seam_jump (warning)", g13, ["seam_pass", "nocontinuity"]),
    ("G14", "block bootstrap: runs of exactly b, same seed same draws", g14, ["iid"]),
    ("G15", "constants anchor: the rendered block hashes to the sha256 printed in the spec", g15, ["const_alter"]),
    ("G16", "leak guard: no output over the literal 80 rows, the literal allowlists, no unlisted date column", g16, ["panel_in_data", "max_rows_800", "allow_extra"]),
    ("G17", "allowlists: each output header equals its allowlist exactly", g17, ["extra_col"]),
    ("G18", "fetch fence: hosts, no address, latch rules, no latch on a socket fault, in-repo cache refused, pacing, cap",
     g18, ["no_host_check", "ua_at", "no_latch_status", "no_latch_redirect", "no_latch_content", "no_content_test", "latch_on_fault", "ignore_stop",
           "cache_in_repo", "no_pacing", "no_cap"]),
    ("G19", "listwise: a week with one series missing is absent from nom4 and present without that series", g19, ["pairwise"]),
    ("G20", "one primary row; descriptive rows read verdict=descriptive", g20, ["second_primary"]),
    ("G21", "decision rule: floor, overlap, equivalence on the 90% interval, placebo floor, fallback, d1-d5", g21, ["no_overlap_branch", "ci95_equiv", "no_placebo_floor"]),
    ("G22", "week 53 / year turn: 2020-W53 labelled 2021-01-01, both changes kept", g22, ["isoint", "calyear"]),
    ("G23", "partial week and lead1 end: as-of Thursday gives 145 weeks; a lead print after as-of leaves nom4_jgb_lead1 only", g23, ["nofriday_asof", "nolead_asof"]),
    ("G24", "placebo spread is the RMS about zero, not the SD about the mean", g24, ["sd_about_mean"]),
    ("G25", "a build refused by the leak guard leaves no file in the output folder", g25, ["leave_leak"]),
]


def selftest():
    t0 = time.time()
    n_pass = n_mut = n_caught = 0
    survivors = []
    print("selftest: %d guards on synthetic fixtures; each must pass clean and fail under every mutant" % len(GUARDS))
    for gid, name, fn, mutants in GUARDS:
        MUT.clear()
        t1 = time.time()
        try:
            fn()
            ok, why = True, ""
        except Exception as e:  # a guard failing on clean code is itself the finding
            ok, why = False, "%s: %s" % (type(e).__name__, e)
        n_pass += ok
        print("%-4s %s  %s%s" % (gid, "PASS" if ok else "FAIL", name, "" if ok else "\n       " + why))
        for m in mutants:
            n_mut += 1
            with mutated(m):
                try:
                    fn()
                    caught, how = False, ""
                except Exception as e:
                    caught, how = True, "%s: %s" % (type(e).__name__, str(e)[:90])
            n_caught += caught
            if not caught:
                survivors.append("%s/%s" % (gid, m))
            print("       mutant %-22s %s%s" % (m, "caught" if caught else "SURVIVED", ("  [" + how + "]") if caught else ""))
        MUT.clear()
    print("%d/%d guards PASS" % (n_pass, len(GUARDS)))
    print("%d/%d mutants caught%s" % (n_caught, n_mut, "" if not survivors else "; SURVIVORS: " + ", ".join(survivors)))
    print("selftest: %.1f s" % (time.time() - t0))
    return 0 if n_pass == len(GUARDS) and n_caught == n_mut else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch", help="the only mode that uses the network")
    f.add_argument("--archive", action="store_true", help="the full fetch: every Treasury year since 1997 and the 39 MB Bank of England archive (46 requests)")
    f.add_argument("--cache", default=DEFAULT_CACHE)
    f.add_argument("--missing-only", action="store_true", help="resume an interrupted full fetch: skip files already in the cache (no re-request)")
    c = sub.add_parser("calibrate", help="offline; pre-2018 history only")
    c.add_argument("--cache", default=DEFAULT_CACHE)
    c.add_argument("--k-infl", type=float, default=CONST["k_author"])
    b = sub.add_parser("build", help="offline and byte-identical on re-run")
    b.add_argument("--cache", default=DEFAULT_CACHE)
    b.add_argument("--out", default=OUT_DIR)
    b.add_argument("--k-infl", type=float, default=K_INFL_FROM_MDE, help="fallback multiplier; may not be below the pre-registered 3.0 (default: the mde value 3.25)")
    sub.add_parser("selftest", help="synthetic fixtures; no network")
    sub.add_parser("mde", help="synthetic false-SHIFT and power tables; the fallback k_infl")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "selftest":
            return selftest()
        if a.cmd == "mde":
            return cmd_mde()
        if a.cmd == "fetch":
            return cmd_fetch(a.cache, a.archive, a.missing_only)
        if a.cmd == "calibrate":
            return cmd_calibrate(a.cache, a.k_infl)
        if a.cmd == "build":
            if a.k_infl < CONST["k_author"]:
                raise HardFail("--k-infl may not be below the pre-registered %.1f" % CONST["k_author"])
            return cmd_build(a.cache, a.out, CONST["boot_draws"], a.k_infl)
    except (HardFail, Refused, ParseError) as e:
        print("refused: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
