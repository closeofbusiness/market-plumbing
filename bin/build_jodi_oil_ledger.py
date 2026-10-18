#!/usr/bin/env python3
"""JODI world oil ledger: country-reported crude oil production and closing stocks from the JODI-Oil World Database, reconciled with EIA's
Short-Term Energy Outlook, and one pre-registered test (is any of EIA's "other inventory draws and balance" line visible in the crude
stocks that non-OECD countries actually report?). Python 3 standard library plus xlrd (the EIA .xls files, as requirements.txt says).

  python3 bin/build_jodi_oil_ledger.py fetch [--years 2024,2025 | --all] [--cache DIR] [--out DIR] [--sleep 5.05] [--max-requests 20]
  python3 bin/build_jodi_oil_ledger.py check-vintage [--cache DIR] [--out DIR]       # HEAD each annual file; report which differ from the cache
  python3 bin/build_jodi_oil_ledger.py build [--panel-only] [--panel-sha HEX] [--cache DIR] [--out DIR]    # offline; byte-identical on re-run
  python3 bin/build_jodi_oil_ledger.py selftest [--no-mutants]                       # synthetic rows only; no network

Specification: _research/2026-10-18-JODI-World-Oil-Ledger-Spec.md (its Amendments A1-A13 and its section "Builder decisions" are part of it).

WHAT TOUCHES THE NETWORK. Only `fetch` and `check-vintage`. Hosts: www.jodidata.org (the data-downloads page and the annual primary CSVs) and
www.eia.gov (four Petroleum Supply Monthly .xls files and the STEO bulk zip; US government, public domain). GET (fetch) or HEAD
(check-vintage) only; one request at a time; at least 5.05 s between request starts, persisted across invocations in ~/jodi_oil/.last_request
(beside the STOP latch); at most 20 requests per run; the CLAUDE.md non-SEC User-Agent (no address, no name); redirects are NOT followed (a 3xx
latches). Any status other than 200, or a body that fails its check, writes ~/jodi_oil/STOP and ends the run. While STOP exists every fetch
refuses; only a person deletes it. A socket fault ends the invocation without latching. No retry, ever. Every request is one row of
data/jodi_oil/fetch_log.csv.

WHERE THE JODI FILES LIVE. ~/jodi_oil/ (override --cache; a path whose realpath is inside this repository is refused), as
jodi_primary_<YYYY>_<sha12>.csv so that every vintage is kept. JODI's terms say "All such rights are reserved", so no JODI file, and no table
from which a reader could rebuild JODI's country-by-month table, is committed: .gitignore has jodi_primary_*.csv, primaryyear*.csv and
secondaryyear*.csv; bin/check.sh M12 looks for the rest. What is published is derived statistics: sums over FIXED panels, coverage ratios and
counts for the changing set of reporters, and a short fixed list of checkpoints.

THE GUARDS. Every guard is behind on("<name>"). `selftest` runs the synthetic suite, then re-runs the relevant part of it once per guard with
that guard switched off (in this process only; there is no command-line or environment switch) and FAILS if a guard's removal goes
unnoticed. For a guard that is a check, "off" means the check is skipped; for a guard that is a behaviour, "off" means the bug the spec names.
"""
import argparse
import bisect
import calendar
import collections
import contextlib
import csv
import datetime as dt
import hashlib
import http.client
import io
import json
import math
import os
import random
import re
import sys
import tempfile
import time
import zipfile
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(ROOT, "data", "jodi_oil")
CACHE_DEFAULT = "~/jodi_oil"
STOP_PATH = os.path.expanduser("~/jodi_oil/STOP")      # fixed, whatever --cache says
STEO_XLSX = os.path.join(ROOT, "data", "crude", "raw", "eia_STEO_m.xlsx")     # the crude ledger's copy of the same STEO release: cross-check and last-historical month

UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
HEADERS = {"User-Agent": UA, "Accept-Encoding": "identity"}

JODI_HOST = "www.jodidata.org"
EIA_HOST = "www.eia.gov"
PAGE_PATH = "/oil/database/data-downloads.aspx"
PRIMARY_DIR = "/_resources/files/downloads/oil-data/annual-csv/primary/"
JODI_FILE_RX = re.compile(r"/_resources/files/downloads/oil-data/annual-csv/primary/((?:primaryyear)?(20[0-9]{2})\.csv)")
PAGE_LINK_RX = re.compile(r"annual-csv/primary/((?:primaryyear)?(20[0-9]{2})\.csv)")
EIA_XLS_IDS = ("MCRSTUS1", "MCESTUS1", "MCSSTUS1", "MCRFPUS2")
EIA_XLS_RX = re.compile(r"/dnav/pet/hist_xls/(MCRSTUS1|MCESTUS1|MCSSTUS1|MCRFPUS2)m\.xls")
STEO_PATH = "/opendata/bulk/STEO.zip"
MANIFEST_PATH = "/opendata/bulk/manifest.txt"       # EIA bulk manifest: gives the STEO file's last_updated, which dates the release
JODI_HEADER = "REF_AREA,TIME_PERIOD,ENERGY_PRODUCT,FLOW_BREAKDOWN,UNIT_MEASURE,OBS_VALUE,ASSESSMENT_CODE"
XLS_MAGIC = b"\xd0\xcf\x11\xe0"
ZIP_MAGIC = b"PK\x03\x04"
MIN_SLEEP = 5.05                       # seconds between request starts: the 5 s of the house rule plus a margin for clock granularity
MAX_REQUESTS = 20
TIMEOUT = 120
BODY_CAP = 60 * 1024 * 1024
FIRST_YEAR = 2015                      # the window starts 2015-01 (spec 3.5)
W0 = "2015-01"
EVENT_RANGE = ("2020-03", "2020-12")   # the episode removed in the descriptive rows and in the SUPPORTS condition
SEED = 20261020
BOOT_B = 10000
BOOT_L = 12
REGISTER_LM = dt.datetime(2026, 10, 21, 0, 0, tzinfo=dt.timezone.utc)
REGISTER_MAX = "2026-08"
REGISTER_YEAR = 2026
MIN_PANEL = 5
MIN_LEVEL_MB = 100.0
MIN_MONTHS = 100
MAX_CHECKPOINTS = 30
SPR_THRESHOLD_KBBL = 2000.0

OECD = ("AU AT BE CA CL CO CR CZ DK EE FI FR DE GR HU IS IE IL IT JP KR LV LT LU MX NL NZ NO PL PT SK SI ES SE CH TR GB US").split()

SRC_JODI = ("# source: International Energy Forum (IEF). Joint Organizations Data Initiative (JODI) Database. JODI Oil and Gas World Databases: "
            "www.jodidata.org, Accessed %s. Derived statistics only; JODI reserves all rights; no JODI file is redistributed.")
_RELEASE = [dt.date(2026, 10, 6)]          # the STEO release date; read from raw/eia_steo_release.txt (EIA's manifest) when that file exists
RELEASE_FILE = "eia_steo_release.txt"


def src_eia():
    d = _RELEASE[0]
    return ("# source: U.S. Energy Information Administration (%s %d): STEO bulk file (release of %d %s %d); Petroleum Supply Monthly series "
            "MCRSTUS1, MCESTUS1, MCSSTUS1, MCRFPUS2." % (calendar.month_abbr[d.month], d.year, d.day, calendar.month_abbr[d.month], d.year))


def read_release(out_dir):
    """Set the STEO release date from EIA's manifest entry saved by `fetch` (raw/eia_steo_release.txt); keep the default if there is none."""
    pth = os.path.join(out_dir, "raw", RELEASE_FILE)
    if os.path.exists(pth):
        m = re.search(r"last_updated: ([0-9]{4}-[0-9]{2}-[0-9]{2})", open(pth, encoding="utf-8").read())
        if m:
            _RELEASE[0] = dt.date.fromisoformat(m.group(1))
    return _RELEASE[0]


def manifest_problem(body):
    if body is None:
        return "body larger than the cap"
    t = body.decode("utf-8", "replace")
    if "STEO" not in t or "last_updated" not in t:
        return "200 but the manifest has no STEO entry with last_updated"
    return None


def manifest_steo_updated(body):
    """The last_updated string of the STEO entry in EIA's bulk manifest (JSON; read as text so a change of layout cannot hide it)."""
    t = body.decode("utf-8", "replace")
    m = re.search(r'"STEO"\s*:\s*\{[^{}]*?"last_updated"\s*:\s*"([^"]+)"', t, re.S) or re.search(r'"last_updated"\s*:\s*"([^"]+)"[^{}]*?"STEO"', t, re.S)
    if m is None:
        raise DataError("manifest: no last_updated for STEO")
    return m.group(1)


# ------------------------------------------------------------------------------------------------------------------------
# guards: every guard is behind on("<name>"); only the selftest ever switches one off, in this process
# ------------------------------------------------------------------------------------------------------------------------
_OFF = set()
_BLIND = [False]               # True while a DRY_RUN build is in progress: no correlation of any kind may be computed


def on(name):
    return name not in _OFF


@contextlib.contextmanager
def mutant(name):
    """Switch guard `name` off for the block. Re-entrant."""
    added = name not in _OFF
    _OFF.add(name)
    try:
        yield
    finally:
        if added:
            _OFF.discard(name)


class Refused(Exception):
    """A request, path or setting this script will not honour (host list, cache inside the repo, spacing, cap)."""


class MaxRequests(Refused):
    """--max-requests reached: an orderly end of the invocation, not a refusal by a server."""


class Latched(Exception):
    """A technical refusal: ~/jodi_oil/STOP was written (or already existed); the run ends."""


class SocketFault(Exception):
    """Timeout, reset or TLS error: the invocation ends without latching."""


class DataError(Exception):
    """A hard check on the data failed. The build stops and repairs nothing."""


class Blind(Exception):
    """A correlation was asked for during a DRY_RUN."""


# ------------------------------------------------------------------------------------------------------------------------
# small helpers
# ------------------------------------------------------------------------------------------------------------------------
def tilde(p):
    home = os.path.expanduser("~")
    return str(p).replace(home, "~") if home and home != "~" else str(p)


def f(v, nd):
    """Fixed-decimal text, '' for None, no negative zero, no scientific notation (byte-stable outputs)."""
    if v is None:
        return ""
    s = format(round(v, nd), ".%df" % nd)
    return s[1:] if s.startswith("-") and float(s) == 0 else s


def sha256_of(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_ua(ua=UA):
    if on("ua_no_address"):
        if "@" in ua:
            raise Refused("User-Agent contains an address")
        for var in ("SEC_UA", "CLAUDE_CODE_USER_EMAIL"):
            v = os.environ.get(var, "").strip()
            if v and (v in ua or ua in v):
                raise Refused("User-Agent contains a configured contact value (not printed)")


assert_ua()


def check_url(host, path, method="GET"):
    """Only the allowlisted JODI and EIA paths (R3). Returns (host, path)."""
    host = (host or "").lower()
    if on("host_allowlist"):
        if method not in ("GET", "HEAD"):
            raise Refused("only GET or HEAD")
        if "?" in path or "#" in path:
            raise Refused("no query or fragment")
        ok = ((host == JODI_HOST and (path == PAGE_PATH or JODI_FILE_RX.fullmatch(path)))
              or (host == EIA_HOST and (EIA_XLS_RX.fullmatch(path) or path in (STEO_PATH, MANIFEST_PATH))))
        if not ok:
            raise Refused("host or path outside the allowlist (www.jodidata.org downloads page and annual primary CSVs; www.eia.gov PSM .xls files and STEO.zip)")
    return host, path


def check_cache(cache):
    real = os.path.realpath(os.path.expanduser(cache))
    root = os.path.realpath(ROOT)
    if on("cache_outside_repo") and (real == root or real.startswith(root + os.sep)):
        raise Refused("the cache must be outside the repository (JODI files are never committed)")
    return real


def month_add(m, k):
    y, mo = int(m[:4]), int(m[5:7])
    t = y * 12 + (mo - 1) + k
    return "%04d-%02d" % (t // 12, t % 12 + 1)


def month_range(a, b):
    out, m = [], a
    while m <= b:
        out.append(m)
        m = month_add(m, 1)
    return out


def days_in(m):
    return calendar.monthrange(int(m[:4]), int(m[5:7]))[1]


def http_date(s):
    """An HTTP Last-Modified header to an aware UTC datetime, or None."""
    from email.utils import parsedate_to_datetime
    try:
        d = parsedate_to_datetime(s)
    except (TypeError, ValueError, IndexError):
        return None
    if d is None:
        return None
    return d.astimezone(dt.timezone.utc) if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def iso_z(d):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ") if d else ""


# ------------------------------------------------------------------------------------------------------------------------
# table output: every CSV begins with the three R2 lines, then the header; headers are on an exact allowlist
# ------------------------------------------------------------------------------------------------------------------------
LOG_COLS = ["requested_at_utc", "host", "path", "method", "http_status", "outcome", "bytes", "sha256", "last_modified"]
FILE_STATS_COLS = ["file", "url", "retrieved_utc", "last_modified", "bytes", "sha256", "rows", "n_areas", "first_period", "max_period", "n_dash",
                   "n_x", "n_dotdot", "n_code1", "n_code2", "n_code3", "n_code4", "header_ok"]
PANEL_AGG_COLS = ["month", "panel", "flow", "unit", "value", "n_members", "n_code1", "n_code3", "data_status", "suppression"]
COVERAGE_COLS = ["month", "group", "flow", "n_reporters", "n_code1", "n_code3", "n_code2_excluded", "n_zero_reported", "n_ktons_only",
                 "n_not_reported", "n_areas_in_file", "data_status"]
PANELS_COLS = ["panel", "ref_area", "oecd_member", "months_usable", "months_in_window"]
RECON_COLS = ["month", "data_status", "steo_basis", "steo_world_crude_mbd", "jodi_panel_producers_crude_mbd", "coverage_reporters",
              "coverage_reporters_allcodes", "coverage_panel", "steo_other_draws_balance_mb", "jodi_panel_nonoecd_draw_mb",
              "steo_residual_minus_panel_mb", "n_panel_nonoecd", "seam_flag", "steo_oecd_commercial_change_mb",
              "jodi_panel_oecd_crude_exspr_change_mb"]
PRIMARY_COLS = ["role", "label", "run_status", "window_first", "window_last", "n_months", "n_seam_excluded", "n_panel", "panel_sha256",
                "panel_mean_level_mb", "largest_member", "largest_member_var_share", "demeaned", "pearson_r", "ci95_lo", "ci95_hi",
                "spearman_rho", "band_1p96_sqrt_n", "verdict"]
IDENT_COLS = ["check", "scope", "code_set", "n", "n_pass", "pass_rate", "n_exact", "note"]
CHECKPOINT_COLS = ["id", "ref_area", "month", "flow", "unit", "jodi_value", "jodi_code", "comparator", "comparator_value", "difference", "status"]
CHECKS_COLS = ["id", "check", "expected", "observed", "status"]
ALLOW = {"fetch_log.csv": LOG_COLS, "file_stats.csv": FILE_STATS_COLS, "panel_aggregates.csv": PANEL_AGG_COLS, "coverage_counts.csv": COVERAGE_COLS,
         "panels.csv": PANELS_COLS, "steo_reconciliation.csv": RECON_COLS, "primary_test.csv": PRIMARY_COLS, "identity_checks.csv": IDENT_COLS,
         "checkpoints.csv": CHECKPOINT_COLS, "checks.csv": CHECKS_COLS}
BANNED_HDR = re.compile(r"(^|_)(price|prices|usd|brent|wti|p_value|pvalue|p_val|t_stat|tstat|beta)(_|$)")
COUNTRY_HDR = re.compile(r"(^|_)(ref_area|country|area)(_|$)")
TIME_HDR = re.compile(r"(^|_)(month|period|time_period|date)(_|$)")
PANEL_NAMES = ("panel_producers", "panel_nonoecd_stocks", "panel_oecd_stocks_exspr")
REPORTER_GROUPS = ("reporters_all", "reporters_oecd", "reporters_nonoecd")
SUPPRESS_OK = ("", "suppressed_diff_lt3", "withheld_dry_run")


def access_date_text(d):
    return "%d %s %d" % (d.day, calendar.month_name[d.month], d.year)


def ack_lines(access, vintage):
    """The three lines every output begins with (R2)."""
    return [SRC_JODI % access, src_eia(), vintage]


def render_table(header, rows, lines):
    out = io.StringIO()
    for ln in lines:
        out.write(ln + "\n")
    w = csv.writer(out, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return out.getvalue()


def check_header_allowed(name, header):
    """The header must equal the file's allowlist exactly, carry no price/statistic name (R5) and, outside checkpoints.csv, no country
    column together with a time column (R6)."""
    if on("column_allowlist"):
        if name not in ALLOW:
            raise DataError("no column allowlist for output file %s" % name)
        if list(header) != ALLOW[name]:
            extra = [h for h in header if h not in ALLOW[name]]
            raise DataError("%s: header differs from its allowlist (not allowed: %s; missing: %s)"
                            % (name, ", ".join(extra) or "-", ", ".join(h for h in ALLOW[name] if h not in header) or "-"))
    if on("no_price"):
        bad = [h for h in header if BANNED_HDR.search(h.lower())]
        if bad:
            raise DataError("%s: header carries a price or regression-statistic name: %s" % (name, ", ".join(bad)))
    if on("no_country_table") and name != "checkpoints.csv":
        low = [h.lower() for h in header]
        if any(COUNTRY_HDR.search(h) for h in low) and any(TIME_HDR.search(h) for h in low) and name != "panels.csv":
            raise DataError("%s: a country column beside a time column would let a reader rebuild JODI's country-by-month table" % name)


def verify_text(name, text, ack=None):
    """The written text itself is checked, not the rows it came from: the three R2 lines, the allowlist, the disclosure rules.
    Returns (header, body rows)."""
    lines = text.split("\n")
    if on("acknowledgement"):
        if not (lines[0].startswith("# source: International Energy Forum (IEF). Joint Organizations Data Initiative (JODI) Database.")
                and lines[1].startswith("# source: U.S. Energy Information Administration") and lines[2].startswith("# vintage:")):
            raise DataError("%s: the first three lines are not the required JODI, EIA and vintage lines" % name)
        if ack is not None and lines[:3] != list(ack):
            raise DataError("%s: the three acknowledgement lines differ from this build's" % name)
    rd = list(csv.reader(io.StringIO("\n".join(l for l in lines if not l.startswith("#")), newline="")))
    header, body = rd[0], rd[1:]
    check_header_allowed(name, header)
    if name == "panel_aggregates.csv" and on("disclosure"):
        j, js = header.index("panel"), header.index("suppression")
        for n, r in enumerate(body, start=1):
            if r[j] not in PANEL_NAMES:
                raise DataError("%s row %d: panel %r is not a fixed panel (no reporter group and no world total may carry a value)" % (name, n, r[j]))
            if r[js] not in SUPPRESS_OK:
                raise DataError("%s row %d: unknown suppression value %r" % (name, n, r[js]))
    if name == "coverage_counts.csv" and on("disclosure"):
        j = header.index("group")
        for n, r in enumerate(body, start=1):
            if r[j] not in REPORTER_GROUPS:
                raise DataError("%s row %d: group %r is not a reporter group" % (name, n, r[j]))
    if name == "checkpoints.csv" and on("no_country_table") and len(body) > MAX_CHECKPOINTS:
        raise DataError("checkpoints.csv: %d rows; at most %d (a longer list would be a country table)" % (len(body), MAX_CHECKPOINTS))
    if os.path.expanduser("~") in text and os.path.expanduser("~") != "~":
        raise DataError("%s: an absolute home path would be published" % name)
    return header, body


def read_table(path, header=None):
    """Data rows of a table written by render_table (comment lines skipped); [] if the file is absent."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh.read().splitlines(True) if not ln.startswith("#")]
    rd = list(csv.reader(io.StringIO("".join(lines))))
    if not rd:
        return []
    if header is not None and list(rd[0]) != list(header):
        raise DataError("unexpected header in " + tilde(path))
    return rd[1:]


def write_text(path, text):
    """Write in place (the checkout may sit on a share where an atomic rename fails) via a temp file in the same folder when possible."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    try:
        os.replace(tmp, path)
    except OSError:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        os.remove(tmp)


# ------------------------------------------------------------------------------------------------------------------------
# the fetch log and the vintage text derived from it
# ------------------------------------------------------------------------------------------------------------------------
def log_path(out_dir):
    return os.path.join(out_dir, "fetch_log.csv")


def log_year(path):
    m = JODI_FILE_RX.fullmatch(path)
    return int(m.group(2)) if m else None


def log_vintage(rows):
    """Access date and the `# vintage:` text from the fetch log alone (R2): the newest GET of a JODI annual file per year, with its
    Last-Modified date and sha256 prefix. The maximum period and preliminary months are not in the log; file_stats.csv has them."""
    newest, access = {}, None
    for r in rows:
        if r[1] == JODI_HOST and r[3] == "GET" and r[4] == "200" and r[5] in ("saved", "unchanged"):
            access = max(access or r[0], r[0])
            y = log_year(r[2])
            if y is not None and (y not in newest or r[0] >= newest[y][0]):
                newest[y] = r
    if access is None:
        for r in rows:
            if r[1] == JODI_HOST:
                access = max(access or r[0], r[0])
    try:
        d = dt.datetime.strptime((access or "")[:10], "%Y-%m-%d")
    except ValueError:
        d = dt.datetime.now(dt.timezone.utc)
    parts = []
    for y in sorted(newest):
        lm = http_date(newest[y][8])
        parts.append("%d:%s:%s" % (y, lm.strftime("%Y-%m-%d") if lm else "no-last-modified", newest[y][7][:12]))
    text = "# vintage: JODI files %s; max TIME_PERIOD and preliminary months: see file_stats.csv." % (" ".join(parts) if parts else "none yet")
    return access_date_text(d), text


def render_log(rows, out_dir=None):
    if out_dir:
        read_release(out_dir)
    access, vint = log_vintage(rows)
    return render_table(LOG_COLS, rows, ack_lines(access, vint))


# ------------------------------------------------------------------------------------------------------------------------
# fetching: the only network code. One request at a time, paced, GET or HEAD only, STOP latch  [R3]
# ------------------------------------------------------------------------------------------------------------------------
def real_opener(method, host, target, headers, timeout, cap):
    """GET or HEAD https://host/target. Returns (status, body, headers); body is None when it exceeds `cap`. No redirect is followed (a 3xx
    comes back as a status and latches), no cookies. Socket-level faults raise SocketFault."""
    conn = http.client.HTTPSConnection(host, timeout=timeout)
    try:
        conn.request(method, target, headers=dict(headers))
        resp = conn.getresponse()
        status = resp.status
        hdrs = {k.lower(): v for k, v in resp.getheaders()}
        if status != 200 or method == "HEAD":
            return status, b"", hdrs
        chunks, total = [], 0
        while True:
            b = resp.read(1 << 16)
            if not b:
                break
            total += len(b)
            if total > cap:
                return status, None, hdrs
            chunks.append(b)
        return status, b"".join(chunks), hdrs
    except (OSError, http.client.HTTPException) as e:
        raise SocketFault(type(e).__name__)
    finally:
        conn.close()


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def jodi_csv_problem(body, path):
    """None when `body` is a JODI annual primary CSV: the exact header line, a /primary/ URL, and at least one CRUDEOIL row."""
    if body is None:
        return "body larger than the cap"
    if on("crude_primary_only") and "/annual-csv/primary/" not in path:
        return "the URL is not under /annual-csv/primary/ (the secondary files share this header)"
    text = body.decode("utf-8", "replace")
    first = text.split("\n", 1)[0].rstrip("\r")
    if first.lstrip("﻿") != JODI_HEADER or first != JODI_HEADER:
        return "200 but the first line is not the JODI header"
    if on("crude_primary_only") and ",CRUDEOIL," not in text:
        return "200 but the file has no CRUDEOIL rows"
    return None


def eia_xls_problem(body):
    if body is None:
        return "body larger than the cap"
    if on("xls_magic") and not body.startswith(XLS_MAGIC):
        return "200 but the body is not an XLS file"
    return None


def steo_zip_problem(body):
    if body is None:
        return "body larger than the cap"
    if on("xls_magic") and not body.startswith(ZIP_MAGIC):
        return "200 but the body is not a zip file"
    try:
        with zipfile.ZipFile(io.BytesIO(body)) as z:
            if "STEO.txt" not in z.namelist():
                return "200 but the zip has no STEO.txt member"
    except zipfile.BadZipFile:
        return "200 but the zip does not open"
    return None


def page_problem(body):
    if body is None:
        return "body larger than the cap"
    if "annual-csv/primary/" not in body.decode("utf-8", "replace"):
        return "200 but the downloads page has no annual-csv/primary/ link"
    return None


class Fetcher:
    """All requests go through here. Injectable opener, clock, sleeper and STOP path make it testable without a network."""

    def __init__(self, cache, out_dir, sleep=MIN_SLEEP, max_requests=MAX_REQUESTS, opener=real_opener, wall=time.time, mono=time.monotonic,
                 sleeper=time.sleep, stop_path=STOP_PATH, now_utc=None, pid_alive=None, eia_loader=None, steo_loader=None):
        if on("min_sleep") and sleep < MIN_SLEEP:
            raise Refused("--sleep must be at least %.2f seconds" % MIN_SLEEP)
        if on("max_requests") and (max_requests > MAX_REQUESTS or max_requests < 1):
            raise Refused("--max-requests must be between 1 and %d" % MAX_REQUESTS)
        self.cache = check_cache(cache)
        self.out_dir = out_dir
        self.sleep, self.max_requests = float(sleep), max_requests
        self.opener, self.wall, self.mono, self.sleeper = opener, wall, mono, sleeper
        self.stop_path = stop_path
        self.now_utc = now_utc or (lambda: dt.datetime.now(dt.timezone.utc))
        self.pid_alive = pid_alive or _pid_alive
        self.eia_loader = eia_loader or load_eia_xls_check
        self.steo_loader = steo_loader or steo_extract_rows
        self.requests = 0
        self._last_mono = None
        self.pace_dir = os.path.dirname(stop_path)
        self._lock = os.path.join(self.pace_dir, ".fetch.lock")
        self._last_file = os.path.join(self.pace_dir, ".last_request")
        self.log_path = log_path(out_dir)
        self._locked = False
        self.links = {}                        # year -> file name, from the downloads page of this run

    # -- lifecycle ------------------------------------------------------------------------------------------------
    def __enter__(self):
        if on("stop_blocks_fetch") and os.path.exists(self.stop_path):
            with open(self.stop_path, encoding="utf-8") as fh:
                why = fh.read().strip().replace("\n", " ")[:200]
            raise Latched("STOP exists at %s (%s); a human must inspect and delete it" % (tilde(self.stop_path), why))
        os.makedirs(self.cache, exist_ok=True)
        os.makedirs(self.pace_dir, exist_ok=True)
        self._acquire()
        return self

    def __exit__(self, *exc):
        self._release()
        return False

    def _acquire(self):
        for _ in range(2):
            try:
                fd = os.open(self._lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                try:
                    with open(self._lock, encoding="utf-8") as fh:
                        pid_s, t_s = (fh.read().split() + ["0", "0"])[:2]
                    pid, t0 = int(pid_s), float(t_s)
                except (ValueError, OSError):
                    pid, t0 = 0, 0.0
                if pid > 0 and self.pid_alive(pid) and self.wall() - t0 < 6 * 3600:
                    raise Refused("another fetcher holds %s (pid %d)" % (tilde(self._lock), pid))
                os.remove(self._lock)          # stale: dead pid or older than six hours
                continue
            with os.fdopen(fd, "w") as fh:
                fh.write("%d %.0f\n" % (os.getpid(), self.wall()))
            self._locked = True
            return
        raise Refused("could not take the fetch lock")

    def _release(self):
        if self._locked:
            try:
                os.remove(self._lock)
            except OSError:
                pass
            self._locked = False

    # -- one request ----------------------------------------------------------------------------------------------
    def _pace(self):
        wait = 0.0
        try:
            with open(self._last_file, encoding="utf-8") as fh:
                last = float(fh.read().strip())
            wait = max(wait, min(self.sleep, self.sleep - (self.wall() - last)))
        except (OSError, ValueError):
            pass
        if self._last_mono is not None:
            wait = max(wait, self.sleep - (self.mono() - self._last_mono))
        if wait > 0 and on("pacing"):
            self.sleeper(wait)

    def _request(self, method, host, path):
        """Returns (status, body, headers, started_wall). Raises SocketFault (after logging it; latching only if the guard is off)."""
        check_url(host, path, method)
        if on("max_requests") and self.requests >= self.max_requests:
            raise MaxRequests("--max-requests reached (%d)" % self.max_requests)
        self._pace()
        started = self.wall()
        self._last_mono = self.mono()
        with open(self._last_file, "w", encoding="utf-8") as fh:
            fh.write("%r\n" % started)               # repr: the float exactly
        self.requests += 1
        try:
            status, body, hdrs = self.opener(method, host, path, HEADERS, TIMEOUT, BODY_CAP)
        except SocketFault as e:
            self._log(started, host, path, method, "", "socket_fault:" + str(e), "", "", "")
            if not on("socket_no_latch"):
                self._latch("socket fault (%s) for %s" % (e, path))
            raise
        return status, body, hdrs, started

    def _stamp(self, ts):
        return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % int((ts % 1) * 1000)

    def _log(self, ts, host, path, method, status, outcome, nbytes, sha, lm):
        rows = read_table(self.log_path, LOG_COLS)
        rows.append([self._stamp(ts), host, path, method, str(status), outcome, str(nbytes), sha, lm])
        text = render_log(rows, self.out_dir)
        verify_text("fetch_log.csv", text)
        write_text(self.log_path, text)

    def _latch(self, reason):
        os.makedirs(os.path.dirname(self.stop_path), exist_ok=True)
        with open(self.stop_path, "w", encoding="utf-8") as fh:
            fh.write("%s UTC  %s\n" % (self.now_utc().strftime("%Y-%m-%dT%H:%M:%S"), reason))
        raise Latched(reason)

    def _done_today(self, host, path, method="GET"):
        today = self.now_utc().strftime("%Y-%m-%d")
        return any(r[1] == host and r[2] == path and r[3] == method and r[5] in ("saved", "unchanged") and r[0][:10] == today
                   for r in read_table(self.log_path, LOG_COLS))

    def _refuse_response(self, started, host, path, method, status, hdrs, bad_body_reason):
        """Common handling: non-200 or a bad body latches (unless that guard is switched off in the selftest)."""
        lm = hdrs.get("last-modified", "") if hdrs else ""
        if status != 200:
            self._log(started, host, path, method, status, "STOP:http_%d" % status, "", "", lm)
            if on("latch_non200"):
                self._latch("HTTP %d for %s" % (status, path))
            return True
        if bad_body_reason:
            self._log(started, host, path, method, status, "STOP:bad_body", "", "", lm)
            if on("latch_bad_body"):
                self._latch("%s (%s)" % (bad_body_reason, path))
            return True
        return False

    # -- the downloads page ---------------------------------------------------------------------------------------
    def fetch_page(self):
        status, body, hdrs, started = self._request("GET", JODI_HOST, PAGE_PATH)
        prob = page_problem(body) if status == 200 else None
        if self._refuse_response(started, JODI_HOST, PAGE_PATH, "GET", status, hdrs, prob):
            return "refused_unlatched"
        text = body.decode("utf-8", "replace")
        self.links = {int(m.group(2)): m.group(1) for m in PAGE_LINK_RX.finditer(text)}
        self._log(started, JODI_HOST, PAGE_PATH, "GET", status, "saved", len(body), sha256_of(body), hdrs.get("last-modified", ""))
        return "saved (%d annual links)" % len(self.links)

    # -- JODI annual files ----------------------------------------------------------------------------------------
    def cached_for_year(self, year):
        return sorted(n for n in (os.listdir(self.cache) if os.path.isdir(self.cache) else [])
                      if re.fullmatch(r"jodi_primary_%d_[0-9a-f]{12}\.csv" % year, n))

    def fetch_year(self, year, explicit=False):
        """Returns an outcome word. A past-year file already cached is not requested again unless the year was named; the current-year
        file (the page links it as primaryyear<YYYY>.csv) is requested unless it was fetched today."""
        name = self.links.get(year)
        if name is None:
            raise Refused("year %d is not linked on the downloads page" % year)
        path = PRIMARY_DIR + name
        have = self.cached_for_year(year)
        if have and not explicit and not name.startswith("primaryyear"):
            return "cached"
        if have and self._done_today(JODI_HOST, path):
            return "cached_today"
        status, body, hdrs, started = self._request("GET", JODI_HOST, path)
        prob = jodi_csv_problem(body, path) if status == 200 else None
        if self._refuse_response(started, JODI_HOST, path, "GET", status, hdrs, prob):
            return "refused_unlatched"
        sha = sha256_of(body)
        target = os.path.join(self.cache, "jodi_primary_%d_%s.csv" % (year, sha[:12]))
        outcome = "unchanged" if os.path.exists(target) else "saved"
        if outcome == "saved":
            with open(target + ".part", "wb") as fh:
                fh.write(body)
            os.replace(target + ".part", target)
        self._log(started, JODI_HOST, path, "GET", status, outcome, len(body), sha, hdrs.get("last-modified", ""))
        return outcome

    def check_year(self, year):
        """HEAD one annual file; compare Last-Modified and Content-Length with the newest logged GET. Returns (status word, detail)."""
        name = self.links.get(year)
        if name is None:
            raise Refused("year %d is not linked on the downloads page" % year)
        path = PRIMARY_DIR + name
        status, body, hdrs, started = self._request("HEAD", JODI_HOST, path)
        if self._refuse_response(started, JODI_HOST, path, "HEAD", status, hdrs, None):
            return "refused_unlatched", ""
        lm, cl = hdrs.get("last-modified", ""), hdrs.get("content-length", "")
        self._log(started, JODI_HOST, path, "HEAD", status, "head", cl, "", lm)
        gets = [r for r in read_table(self.log_path, LOG_COLS) if r[1] == JODI_HOST and r[2] == path and r[3] == "GET" and r[5] in ("saved", "unchanged")]
        if not gets:
            return "not_cached", "no GET of this file in the log (Last-Modified %s)" % lm
        last = max(gets, key=lambda r: r[0])
        same = last[8] == lm and (not cl or last[6] == cl)
        return ("same" if same else "DIFFERS"), "Last-Modified %s (cached %s), bytes %s (cached %s)" % (lm, last[8], cl, last[6])

    # -- EIA ------------------------------------------------------------------------------------------------------
    def fetch_eia_xls(self, sid):
        path = "/dnav/pet/hist_xls/%sm.xls" % sid
        raw_dir = os.path.join(self.out_dir, "raw")
        target = os.path.join(raw_dir, "eia_%sm.xls" % sid)
        if os.path.exists(target) and self._done_today(EIA_HOST, path):
            return "cached_today"
        status, body, hdrs, started = self._request("GET", EIA_HOST, path)
        prob, part = None, target + ".part"
        if status == 200:
            prob = eia_xls_problem(body)
            if prob is None:
                os.makedirs(raw_dir, exist_ok=True)
                with open(part, "wb") as fh:
                    fh.write(body)
                if on("eia_validate"):                       # the build's own reader must be able to load it, before it replaces anything
                    try:
                        self.eia_loader(part, sid)
                    except DataError as e:
                        prob = "200 but the XLS does not load (%s)" % e
                        os.remove(part)
        if self._refuse_response(started, EIA_HOST, path, "GET", status, hdrs, prob):
            return "refused_unlatched"
        os.replace(part, target)
        self._log(started, EIA_HOST, path, "GET", status, "saved", len(body), sha256_of(body), hdrs.get("last-modified", ""))
        return "saved"

    def fetch_steo(self):
        raw_dir = os.path.join(self.out_dir, "raw")
        ext = os.path.join(raw_dir, "eia_steo_extract.csv")
        if os.path.exists(ext) and self._done_today(EIA_HOST, STEO_PATH):
            return "cached_today"
        status, body, hdrs, started = self._request("GET", EIA_HOST, STEO_PATH)
        prob, rows = None, None
        if status == 200:
            prob = steo_zip_problem(body)
            if prob is None:
                try:
                    rows = self.steo_loader(body)
                except DataError as e:
                    prob = "200 but the STEO zip does not parse (%s)" % e
        if self._refuse_response(started, EIA_HOST, STEO_PATH, "GET", status, hdrs, prob):
            return "refused_unlatched"
        sha = sha256_of(body)
        with open(os.path.join(self.cache, "eia_STEO_%s.zip" % sha[:12]), "wb") as fh:
            fh.write(body)
        self._log(started, EIA_HOST, STEO_PATH, "GET", status, "saved", len(body), sha, hdrs.get("last-modified", ""))
        write_steo_extract(ext, rows, ack_lines(*log_vintage(read_table(self.log_path, LOG_COLS))))
        return "saved"


    def fetch_manifest(self):
        """EIA's bulk manifest, once: it dates the STEO release. The STEO entry's last_updated is saved to raw/eia_steo_release.txt."""
        raw_dir = os.path.join(self.out_dir, "raw")
        target = os.path.join(raw_dir, RELEASE_FILE)
        if os.path.exists(target) and self._done_today(EIA_HOST, MANIFEST_PATH):
            return "cached_today"
        status, body, hdrs, started = self._request("GET", EIA_HOST, MANIFEST_PATH)
        prob, upd = None, None
        if status == 200:
            prob = manifest_problem(body)
            if prob is None:
                try:
                    upd = manifest_steo_updated(body)
                except DataError as e:
                    prob = "200 but %s" % e
        if self._refuse_response(started, EIA_HOST, MANIFEST_PATH, "GET", status, hdrs, prob):
            return "refused_unlatched"
        sha = sha256_of(body)
        with open(os.path.join(self.cache, "eia_manifest_%s.txt" % sha[:12]), "wb") as fh:
            fh.write(body)
        os.makedirs(raw_dir, exist_ok=True)
        write_text(target, "EIA bulk manifest (https://%s%s), STEO entry. STEO last_updated: %s\n" % (EIA_HOST, MANIFEST_PATH, upd))
        self._log(started, EIA_HOST, MANIFEST_PATH, "GET", status, "saved", len(body), sha, hdrs.get("last-modified", ""))
        return "saved (STEO last_updated %s)" % upd


def parse_years(spec, cur):
    out = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"(20[0-9]{2})(?:-(20[0-9]{2}))?", part)
        if not m:
            raise Refused("--years: %r is not a year or a range like 2015-2017" % part)
        a = int(m.group(1))
        b = int(m.group(2) or a)
        if b < a:
            raise Refused("--years: %r runs backwards" % part)
        out.update(range(a, b + 1))
    return sorted(out)


# ------------------------------------------------------------------------------------------------------------------------
# EIA: Petroleum Supply Monthly .xls files and the STEO bulk zip (US government, public domain; committed as an extract)
# ------------------------------------------------------------------------------------------------------------------------
PSM_UNITS = {"MCRSTUS1": "thousand barrels", "MCESTUS1": "thousand barrels", "MCSSTUS1": "thousand barrels", "MCRFPUS2": "thousand barrels per day"}
STEO_SERIES = ("COPR_WORLD", "PAPR_WORLD", "T3_STCHANGE_NOECD", "T3_STCHANGE_WORLD", "T3_STCHANGE_US", "T3_STCHANGE_OOECD", "PASC_OECD_T3",
               "PASC_US", "COPR_SA", "COPR_NI", "COPR_KU")
STEO_FIRST, STEO_LAST = "2014-12", "2027-12"
STEO_COLS = ["series_id", "name", "units", "month", "value"]
# STEO uses FIPS country codes, JODI ISO 3166-1 alpha-2: NG is Nigeria in ISO and Niger in FIPS (G16).
FIPS_FOR_ISO = {"SA": "SA", "NG": "NI", "KW": "KU"}


def load_psm(path, sid):
    """One EIA dnav hist_xls workbook: sheet 'Data 1', row 2 Sourcekey, row 3 title with the unit, then (Excel date, value).
    Returns {YYYY-MM: float}. Raises DataError when the layout or the unit is not the expected one."""
    import xlrd
    try:
        b = xlrd.open_workbook(path)
        sh = b.sheet_by_name("Data 1")
    except Exception as e:
        raise DataError("%s: cannot open as an EIA workbook with a 'Data 1' sheet (%s)" % (os.path.basename(path), type(e).__name__))
    if sh.cell_value(1, 0) != "Sourcekey" or sh.cell_value(1, 1) != sid:
        raise DataError("%s: Sourcekey is %r, not %s" % (os.path.basename(path), sh.cell_value(1, 1), sid))
    title = str(sh.cell_value(2, 1))
    m = re.search(r"\(([^()]*)\)\s*$", title.strip())
    if not m or m.group(1).strip().lower() != PSM_UNITS[sid]:
        raise DataError("%s: header unit %r is not %r" % (os.path.basename(path), m.group(1) if m else None, PSM_UNITS[sid]))
    out = {}
    for r in range(3, sh.nrows):
        v = sh.cell_value(r, 1)
        if v != "":
            d = xlrd.xldate_as_datetime(sh.cell_value(r, 0), b.datemode)
            out["%04d-%02d" % (d.year, d.month)] = float(v)
    if not out:
        raise DataError("%s: no data rows" % os.path.basename(path))
    return out


def load_eia_xls_check(path, sid):
    return load_psm(path, sid)


def _steo_month(p):
    p = str(p)
    if re.fullmatch(r"[0-9]{6}", p):
        return p[:4] + "-" + p[4:]
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}", p):
        return p
    return None


def steo_extract_rows(zbytes):
    """Rows (series_id, name, units, month, value) of the used STEO series from the bulk zip's STEO.txt (one JSON series per line)."""
    out, seen = [], set()
    try:
        with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
            text = z.read("STEO.txt").decode("utf-8")
    except (KeyError, zipfile.BadZipFile) as e:
        raise DataError("STEO zip: cannot read STEO.txt (%s)" % type(e).__name__)
    want = {"STEO.%s.M" % s: s for s in STEO_SERIES}
    for line in text.splitlines():
        if not line.startswith("{") or '"series_id"' not in line:
            continue
        j = json.loads(line)
        sid = j.get("series_id")
        if sid not in want:
            continue
        if sid in seen:
            raise DataError("STEO zip: series %s appears twice" % sid)
        seen.add(sid)
        for p, v in j.get("data") or []:
            m = _steo_month(p)
            if m is None or not (STEO_FIRST <= m <= STEO_LAST):
                continue
            out.append((sid, j.get("name", ""), j.get("units", ""), m, None if v in (None, "", "NA", "-") else float(v)))
    if len(seen) != len(want):
        raise DataError("STEO zip: series missing: %s" % ", ".join(sorted(set(want) - seen)))
    out.sort(key=lambda r: (r[0], r[3]))
    return out


def write_steo_extract(path, rows, lines):
    """The committed extract: the three acknowledgement lines, then series_id, name, units, month, value."""
    text = render_table(STEO_COLS, [[sid, name, units, m, "" if v is None else repr(float(v))] for sid, name, units, m, v in rows], lines)
    write_text(path, text)


def read_steo_extract(path):
    """{series short name: {YYYY-MM: float}} and {series short name: (name, units)}."""
    data, meta = collections.defaultdict(dict), {}
    for r in read_table(path, STEO_COLS):
        short = r[0].split(".")[1]
        meta[short] = (r[1], r[2])
        if r[4] != "":
            data[short][r[3]] = float(r[4])
    return dict(data), meta


def steo_xlsx_facts():
    """From the crude ledger's copy of the same STEO release (data/crude/raw/eia_STEO_m.xlsx): the last historical month, and the monthly
    values of the series this build uses, for the cross-check. The bulk file has no historical flag. Returns (last_hist 'YYYY-MM',
    {short name: {YYYY-MM: float}}) or None when the workbook or openpyxl is not available."""
    if not os.path.exists(STEO_XLSX):
        return None
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import build_crude_ledger as bcl
        info, ym, hist, t3, t2 = bcl.parse_steo(STEO_XLSX)
    except Exception:
        return None
    finally:
        try:
            sys.path.remove(os.path.dirname(os.path.abspath(__file__)))
        except ValueError:
            pass
    last = "%04d-%02d" % (info["last_hist"] // 100, info["last_hist"] % 100)
    vals = {}
    for short in STEO_SERIES:
        k = short.lower()
        if k in t3:
            vals[short] = {"%04d-%02d" % (m // 100, m % 100): v for m, v in zip(ym, t3[k][1]) if v is not None}
    return last, vals


# ------------------------------------------------------------------------------------------------------------------------
# reading a JODI annual file (spec 3.1). Cells are keyed (area, month, flow, unit); only ENERGY_PRODUCT=CRUDEOIL is kept.
# ------------------------------------------------------------------------------------------------------------------------
PRODUCT = "CRUDEOIL"
FLOWS = ("INDPROD", "TOTIMPSB", "TOTEXPSB", "CLOSTLV", "STOCKCH")
RATE_FLOWS = ("INDPROD", "TOTIMPSB", "TOTEXPSB")        # read in KBD, thousand barrels per day
UNITS = ("KBD", "KBBL", "KL", "KTONS", "CONVBBL")
MARKERS = ("-", "x", "..")
VALID_CODES = (1, 2, 3, 4)
USABLE_CODES = (1, 3)
KL_PER_KBBL = 0.158987
NUM_RX = re.compile(r"-?[0-9]+(\.[0-9]+)?")


class FileData:
    pass


def unit_for(flow):
    """The one unit a flow is read in (G4): KBD for the rate flows, KBBL for stock levels and changes."""
    if not on("single_unit"):
        return "KL"                     # mutant: a different unit's number for the same series
    return "KBD" if flow in RATE_FLOWS else "KBBL"


def unit_relations(allc, check=True):
    """The five units are one number re-expressed (spec 2.1). Over every crude cell of the file where both numbers exist:
    KBD = KBBL / days in the month (hard check, 0.01 KBD); KL = KBBL x 0.158987; CONVBBL = 1000 x KBBL / KTONS (within 1).
    Also counts the cells that are numeric in KTONS only. Returns a dict of counts and worst gaps."""
    st = {"n_kbd": 0, "n_kbd_exact": 0, "worst_kbd": 0.0, "n_kl": 0, "n_kl_off": 0, "worst_kl_rel": 0.0, "n_conv": 0, "n_conv_off": 0, "n_ktons_only": 0}
    for (a, m, fl, u), (v, c, mk) in allc.items():
        if u == "KBD" and v is not None:
            kb = allc.get((a, m, fl, "KBBL"))
            if kb is not None and kb[0] is not None:
                st["n_kbd"] += 1
                gap = abs(v - kb[0] / days_in(m))
                st["worst_kbd"] = max(st["worst_kbd"], gap)
                st["n_kbd_exact"] += gap <= 1e-4
                if check and gap > 0.01:
                    raise DataError("unit check: KBD %.4f x %d days differs from KBBL %.4f by more than 0.01 KBD (%s %s %s)" % (v, days_in(m), kb[0], a, m, fl))
        elif u == "KL" and v is not None:
            kb = allc.get((a, m, fl, "KBBL"))
            if kb is not None and kb[0] is not None:
                st["n_kl"] += 1
                gap = abs(v - kb[0] * KL_PER_KBBL)
                st["worst_kl_rel"] = max(st["worst_kl_rel"], gap / max(abs(v), 1.0))
                st["n_kl_off"] += gap > 1.5 + 1e-4 * abs(v)
        elif u == "CONVBBL" and v is not None:
            kb, kt = allc.get((a, m, fl, "KBBL")), allc.get((a, m, fl, "KTONS"))
            if kb is not None and kt is not None and kb[0] is not None and kt[0] not in (None, 0.0):
                st["n_conv"] += 1
                st["n_conv_off"] += abs(v - 1000.0 * kb[0] / kt[0]) > 1.0
        elif u == "KTONS" and v is not None:
            kb = allc.get((a, m, fl, "KBBL"))
            if kb is not None and kb[0] is None:
                st["n_ktons_only"] += 1
    return st


def parse_file(raw, year, name="", url=""):
    """Parse one annual file held in memory. Hard failures: wrong header, a period outside the file's year, a duplicate crude cell, a
    numeric cell whose assessment code is not 1-4, a value that is neither a number nor a marker."""
    text = raw.decode("utf-8")
    fd = FileData()
    fd.year, fd.name, fd.url, fd.sha, fd.bytes = year, name, url, sha256_of(raw), len(raw)
    rd = csv.reader(io.StringIO(text, newline=""))
    head = next(rd, None)
    fd.header_ok = head is not None and ",".join(head) == JODI_HEADER
    if not fd.header_ok:
        raise DataError("%s: the first line is not the JODI header" % (name or year))
    allc, areas, periods_num, periods_all = {}, set(), set(), set()
    n_rows = n_dash = n_x = n_dd = 0
    codes = collections.Counter()
    crude_rows = 0
    prods = (PRODUCT,) if on("crude_primary_only") else (PRODUCT, "TOTCRUDE")
    for r in rd:
        if not r:
            continue
        area, per, prod, flow, unit, val, code = r
        n_rows += 1
        areas.add(area)
        periods_all.add(per)
        if val == "-":
            n_dash += 1
        elif val == "x":
            n_x += 1
        elif val == "..":
            n_dd += 1
        else:
            if not NUM_RX.fullmatch(val):
                raise DataError("%s: value %r (%s %s %s %s) is neither a number nor a marker" % (name, val, area, per, flow, unit))
            if not re.fullmatch(r"[0-9]", code) or int(code) not in VALID_CODES:
                if on("assessment_codes"):
                    raise DataError("%s: assessment code %r on a numeric cell (%s %s %s %s); only 1-4 exist" % (name, code, area, per, flow, unit))
            codes[code] += 1
            periods_num.add(per)
        if prod in prods:
            if not re.fullmatch(r"[0-9]{4}-[0-9]{2}", per) or int(per[:4]) != year:
                raise DataError("%s: period %r is outside the file's year %d" % (name, per, year))
            if unit not in UNITS:
                raise DataError("%s: unknown unit %r" % (name, unit))
            key = (area, per, flow, unit)
            if key in allc and on("crude_primary_only"):
                raise DataError("%s: duplicate crude cell %s" % (name, key))
            try:
                c = int(code)
            except ValueError:
                c = None
            allc[key] = (float(val) if val not in MARKERS else None, c, val if val in MARKERS else "")
            crude_rows += 1
    if crude_rows == 0:
        raise DataError("%s: no CRUDEOIL rows" % (name or year))
    fd.unit_stats = unit_relations(allc, on("unit_kbd_check"))
    fd.cells = {k: v for k, v in allc.items() if k[2] in FLOWS}
    fd.areas = areas
    fd.rows, fd.n_dash, fd.n_x, fd.n_dd = n_rows, n_dash, n_x, n_dd
    fd.codes = {k: codes.get(k, 0) for k in "1234"}
    fd.codes_other = sum(v for k, v in codes.items() if k not in "1234")
    fd.first_period, fd.max_period = min(periods_all), (max(periods_num) if periods_num else "")
    fd.months = sorted({k[1] for k in fd.cells})
    return fd


class World:
    """The selected annual files read as one monthly panel of areas. `cell(area, month, flow)` is (value, code, status) in KBD/KBBL."""

    def __init__(self, files):
        self.files = dict(files)
        self.months = sorted({m for fd in self.files.values() for m in fd.months})
        self.file_of = {m: fd for fd in self.files.values() for m in fd.months}
        self.areas = sorted({a for fd in self.files.values() for a in fd.areas})
        self._zero = None

    def raw(self, area, month, flow, unit):
        fd = self.file_of.get(month)
        if fd is None:
            return None
        return fd.cells.get((area, month, flow, unit))

    def cell(self, area, month, flow):
        """(value, code, status). status: ok | code2_excluded | not_reported | not_applicable | ktons_only. Absent areas are not_reported."""
        fd = self.file_of.get(month)
        miss = (None, None, "not_reported")
        if fd is None:
            return miss if on("missing_stays_missing") else (0.0, 3, "ok")
        if area not in fd.areas:
            return miss if on("missing_stays_missing") else (0.0, 3, "ok")
        u = fd.cells.get((area, month, flow, unit_for(flow)))
        if u is None:
            return miss if on("missing_stays_missing") else (0.0, 3, "ok")
        val, code, marker = u
        if val is None:
            if not on("missing_stays_missing"):
                return (0.0, 3, "ok")
            if marker == "x":
                return (None, code, "not_applicable")
            kt = fd.cells.get((area, month, flow, "KTONS"))
            if marker == "-" and kt is not None and kt[0] is not None:
                return (None, code, "ktons_only")
            return (None, code, "not_reported")
        if code in (2, 4) and on("assessment_codes"):
            return (val, code, "code2_excluded")
        return (val, code, "ok")

    def zero_areas(self, month):
        """Areas whose numeric closing stock is exactly 0 in every month it is numeric within the annual file holding `month`, and numeric at
        least once there (zero_reported; the 2026 file has 8 of them)."""
        fd = self.file_of.get(month)
        if fd is None:
            return frozenset()
        if self._zero is None:
            self._zero = {}
        if fd.year not in self._zero:
            z = set()
            for a in sorted(fd.areas):
                vals = []
                for m in fd.months:
                    v, c, s = self.cell(a, m, "CLOSTLV")
                    if v is not None and s in ("ok", "code2_excluded"):
                        vals.append(v)
                if vals and all(v == 0.0 for v in vals):
                    z.add(a)
            self._zero[fd.year] = frozenset(z)
        return self._zero[fd.year]


def usable(c, flow, zero=frozenset(), area=None):
    """A usable cell: numeric, status ok, assessment code 1 or 3, and (stocks) not from an all-zero area."""
    v, code, st = c
    if v is None or st != "ok" or code not in (USABLE_CODES if on("assessment_codes") else (1, 2, 3)):
        return False
    if flow == "CLOSTLV" and on("zero_reported") and area in zero:
        return False
    return True


def classify(c, flow, area, zero):
    """One word per (area, month, flow): code1 | code3 | code2_excluded | zero_reported | ktons_only | not_reported."""
    v, code, st = c
    if v is not None and flow == "CLOSTLV" and on("zero_reported") and area in zero:
        return "zero_reported"
    if st == "code2_excluded":
        return "code2_excluded"
    if st == "ok":
        return "code1" if code == 1 else ("code3" if code == 3 else ("code2_excluded" if on("assessment_codes") else "code3"))
    if st == "ktons_only":
        return "ktons_only"
    return "not_reported"


def file_stats_row(fd, log_rows):
    """One row of file_stats.csv: the file's vintage from the fetch log and its own contents."""
    path = log_path_of(fd)
    gets = [r for r in log_rows if r[1] == JODI_HOST and r[2] == path and r[3] == "GET" and r[5] in ("saved", "unchanged") and r[7] == fd.sha]
    last = max(gets, key=lambda r: r[0]) if gets else None
    lm = http_date(last[8]) if last and last[8] else None
    return {"file": fd.name, "url": "https://" + JODI_HOST + path,
            "retrieved_utc": last[0][:19] + "Z" if last else "",
            "last_modified": iso_z(lm) if on("vintage_recorded") else "",
            "bytes": fd.bytes, "sha256": fd.sha, "rows": fd.rows, "n_areas": len(fd.areas), "first_period": fd.first_period,
            "max_period": fd.max_period if on("vintage_recorded") else "",
            "n_dash": fd.n_dash, "n_x": fd.n_x, "n_dotdot": fd.n_dd, "n_code1": fd.codes["1"], "n_code2": fd.codes["2"],
            "n_code3": fd.codes["3"], "n_code4": fd.codes["4"], "header_ok": "yes" if fd.header_ok else "no"}


def log_path_of(fd):
    return fd.url if fd.url.startswith("/") else PRIMARY_DIR + fd.name


# ------------------------------------------------------------------------------------------------------------------------
# the cache: which file is read for each year, and the refusal of a file the log does not know (R4)
# ------------------------------------------------------------------------------------------------------------------------
def select_cache(cache, log_rows, years=None):
    """{year: (cache path, file name, sha)}: for each year the newest logged GET whose sha256 matches a cached file. A cached file with
    no log row of the same sha256 is a hard failure (G6)."""
    cache = os.path.realpath(os.path.expanduser(cache))
    names = sorted(n for n in os.listdir(cache) if re.fullmatch(r"jodi_primary_[0-9]{4}_[0-9a-f]{12}\.csv", n)) if os.path.isdir(cache) else []
    shas = {}
    for r in log_rows:
        if r[1] == JODI_HOST and r[3] == "GET" and r[4] == "200" and r[5] in ("saved", "unchanged") and log_year(r[2]) is not None:
            shas.setdefault(r[7], []).append(r)
    out = {}
    for n in names:
        y = int(n[13:17])
        sha = sha256_file(os.path.join(cache, n))
        if not n.endswith("_%s.csv" % sha[:12]):
            raise DataError("%s: the file name does not carry its own sha256 prefix (the file was edited or renamed)" % n)
        rows = [r for r in shas.get(sha, []) if log_year(r[2]) == y]
        if not rows:
            if on("vintage_recorded"):
                raise DataError("%s: no row of fetch_log.csv records this sha256; the build refuses a file with no log row" % n)
            continue
        newest = max(rows, key=lambda r: r[0])
        if y not in out or newest[0] >= out[y][3]:
            out[y] = (os.path.join(cache, n), os.path.basename(newest[2]), sha, newest[0])
    if years is not None:
        out = {y: v for y, v in out.items() if y in years}
    return {y: v[:3] for y, v in out.items()}


# ------------------------------------------------------------------------------------------------------------------------
# parameters (the fixture overrides them; the real build uses the defaults, which are the spec's numbers)
# ------------------------------------------------------------------------------------------------------------------------
class Params:
    def __init__(self, **kw):
        self.w0 = W0
        self.oecd = frozenset(OECD)
        self.us = "US"
        self.min_panel, self.min_level, self.min_months = MIN_PANEL, MIN_LEVEL_MB, MIN_MONTHS
        self.boot_b, self.boot_l, self.seed = BOOT_B, BOOT_L, SEED
        self.reg_year, self.reg_lm, self.reg_max = REGISTER_YEAR, REGISTER_LM, REGISTER_MAX
        self.event = EVENT_RANGE
        self.recent_year = 2026
        self.start_late = "2018-01"
        self.steo_pins = True
        self.ident_start = "2025-01"
        self.spr_start = "2025-01"
        self.ck_year_end = "2025-12"
        self.ck_mid = "2025-06"
        self.ck_stockch = ("2026-04", "2026-05", "2026-06")
        self.__dict__.update(kw)


def split_sum(parts):
    return math.fsum(parts)


def mean(xs):
    return math.fsum(xs) / len(xs)


# ------------------------------------------------------------------------------------------------------------------------
# reporter groups: counts and in-memory sums only (R6, A10)
# ------------------------------------------------------------------------------------------------------------------------
def coverage_tables(world, months, p, nonoecd=None):
    """Counts per month, group and flow (INDPROD, CLOSTLV) for the three reporter groups, and the INDPROD sums that feed the coverage
    ratios. The partition identity oecd + nonoecd = all is asserted per month and flow (G30). Returns (rows, sums); `sums` stays in memory."""
    rows, sums = [], {}
    for m in months:
        fd = world.file_of[m]
        zero = world.zero_areas(m)
        in_file = sorted(fd.areas)
        nonoecd_set = set(nonoecd) if nonoecd is not None else {a for a in in_file if a not in p.oecd}
        preds = (("reporters_all", lambda a: True), ("reporters_oecd", lambda a: a in p.oecd), ("reporters_nonoecd", lambda a: a in nonoecd_set))
        for flow in ("INDPROD", "CLOSTLV"):
            cnt = {g: collections.Counter() for g, _ in preds}
            sm = {g: {"comp": 0.0, "allc": 0.0} for g, _ in preds}
            for a in in_file:
                c = world.cell(a, m, flow)
                k = classify(c, flow, a, zero)
                for g, pr in preds:
                    if pr(a):
                        cnt[g][k] += 1
                        cnt[g]["areas"] += 1
                        if flow == "INDPROD" and c[0] is not None and c[2] in ("ok", "code2_excluded"):
                            sm[g]["allc"] += c[0]
                            if k in ("code1", "code3"):
                                sm[g]["comp"] += c[0]
            if on("partition"):
                keys = set().union(*[set(cnt[g]) for g in cnt])
                for k in keys:
                    if cnt["reporters_oecd"][k] + cnt["reporters_nonoecd"][k] != cnt["reporters_all"][k]:
                        raise DataError("partition: reporters_oecd + reporters_nonoecd != reporters_all for %s, %s, %s" % (m, flow, k))
                for k in ("comp", "allc"):
                    if abs(sm["reporters_oecd"][k] + sm["reporters_nonoecd"][k] - sm["reporters_all"][k]) > 1e-6:
                        raise DataError("partition: in-memory sums differ for %s, %s" % (m, k))
            for g, _ in preds:
                c = cnt[g]
                n_rep = c["code1"] + c["code3"]
                rows.append({"month": m, "group": g, "flow": flow, "n_reporters": n_rep, "n_code1": c["code1"], "n_code3": c["code3"],
                             "n_code2_excluded": c["code2_excluded"], "n_zero_reported": c["zero_reported"], "n_ktons_only": c["ktons_only"],
                             "n_not_reported": c["not_reported"], "n_areas_in_file": c["areas"], "data_status": None})
                if (c["code1"] + c["code3"] + c["code2_excluded"] + c["zero_reported"] + c["ktons_only"] + c["not_reported"]) != c["areas"]:
                    raise DataError("coverage counts for %s %s %s do not add up to the areas in the file" % (m, g, flow))
            if flow == "INDPROD":
                a_ = sm["reporters_all"]
                sums[m] = {"comp_kbd": a_["comp"], "allc_kbd": a_["allc"],
                           "n_comp": cnt["reporters_all"]["code1"] + cnt["reporters_all"]["code3"],
                           "n_allc": cnt["reporters_all"]["code1"] + cnt["reporters_all"]["code3"] + cnt["reporters_all"]["code2_excluded"]}
    return rows, sums


# ------------------------------------------------------------------------------------------------------------------------
# fixed panels (spec 3.2)
# ------------------------------------------------------------------------------------------------------------------------
def member_level(world, a, m, flow, spr, p, exspr=False):
    """(value, code) of one area's cell in KBD/KBBL, or (None, None) when it is not usable. For the US in the ex-SPR panel the Strategic
    Petroleum Reserve (EIA MCSSTUS1, thousand barrels) is taken off the JODI figure, which includes it (G17)."""
    c = world.cell(a, m, flow)
    if not usable(c, flow, world.zero_areas(m), a):
        return None, None
    v = c[0]
    if exspr and a == p.us and on("spr_removed"):
        s = spr.get(m)
        if s is None:
            return None, None
        v = v - s
    return v, c[1]


def usable_months(world, a, flow, W, spr, p, exspr):
    n = 0
    for m in W:
        v, _ = member_level(world, a, m, flow, spr, p, exspr)
        if v is not None and (flow == "INDPROD" or v > 0):
            n += 1
    return n


def make_panels(world, W, spr, p):
    """The three panels, by rule, for window W. Returns {name: {"flow", "members", "months_usable"}}; members are usable in every month of W."""
    out = {}
    areas = world.areas
    spec = (("panel_producers", "INDPROD", lambda a: True, False),
            ("panel_nonoecd_stocks", "CLOSTLV", lambda a: a not in p.oecd, False),
            ("panel_oecd_stocks_exspr", "CLOSTLV", lambda a: a in p.oecd, True))
    for name, flow, pred, exspr in spec:
        mu = {}
        for a in areas:
            if pred(a):
                n = usable_months(world, a, flow, W, spr, p, exspr)
                if n:
                    mu[a] = n
        members = sorted(a for a, n in mu.items() if n == len(W))
        out[name] = {"flow": flow, "members": members, "months_usable": mu, "exspr": exspr}
    return out


def panel_rows(panels, p, W):
    """panels.csv: members only, so months_usable equals months_in_window by construction. No values."""
    rows = []
    for name in PANEL_NAMES:
        for a in panels[name]["members"]:
            rows.append([name, a, "yes" if a in p.oecd else "no", panels[name]["months_usable"][a], len(W)])
    return rows


def nested_suppression(defs, min_diff=3):
    """Names of panels to blank: for two panels of the same flow where one's members are a proper subset of the other's and the larger has
    1 or 2 more, the larger is blanked (differencing two published sums would reveal a single country). defs: {name: (flow, members)}."""
    blank = set()
    if not on("disclosure"):
        return blank
    for a, (fa, ma) in defs.items():
        for b, (fb, mb_) in defs.items():
            if a != b and fa == fb and set(ma) < set(mb_) and 0 < len(set(mb_) - set(ma)) < min_diff:
                blank.add(b)
    return blank


def publishable(panels):
    """Panels with at least 3 members; a smaller panel is a country (R6)."""
    if not on("disclosure"):
        return list(PANEL_NAMES)
    return [n for n in PANEL_NAMES if len(panels[n]["members"]) >= 3]


def panel_level(world, pn, m, spr, p):
    """Sum over the members for month m: (value, n_present, n_code1, n_code3); value is None unless every member is present."""
    tot, n, n1, n3 = [], 0, 0, 0
    for a in pn["members"]:
        v, code = member_level(world, a, m, pn["flow"], spr, p, pn["exspr"])
        if v is not None:
            tot.append(v)
            n += 1
            n1 += code == 1
            n3 += code == 3
    scale = 1000.0 if on("mb_scale") else 1e6
    return (math.fsum(tot) / scale if n == len(pn["members"]) and n else None), n, n1, n3


def member_change(world, a, m, spr, p, exspr):
    """One member's stock change in mb for month m (positive = build), and a seam flag. Within a file: the level difference. At a file
    boundary (January): JODI's own STOCKCH from the new file when it is usable; else seam_unresolved (A6, G28)."""
    pm = month_add(m, -1)
    fd, pfd = world.file_of.get(m), world.file_of.get(pm)
    if pfd is None or fd is None:
        return None, ""
    if pfd is fd or not on("seam_stockch"):
        v1, _ = member_level(world, a, m, "CLOSTLV", spr, p, exspr)
        v0, _ = member_level(world, a, pm, "CLOSTLV", spr, p, exspr)
        if v1 is None or v0 is None:
            return None, ""
        return (v1 - v0) / 1000.0, ""
    c = world.cell(a, m, "STOCKCH")
    if not usable(c, "STOCKCH"):
        return None, "seam_unresolved"
    adj = 0.0
    if exspr and a == p.us and on("spr_removed"):
        s1, s0 = spr.get(m), spr.get(pm)
        if s1 is None or s0 is None:
            return None, "seam_unresolved"
        adj = s1 - s0
    return (c[0] - adj) / 1000.0, "seam_resolved"


def panel_change(world, pn, m, spr, p):
    """(change in mb, flag, per-member changes) for the stock panel; None when any member lacks a value (seam_unresolved or a gap)."""
    ch, flags = {}, set()
    for a in pn["members"]:
        v, fl = member_change(world, a, m, spr, p, pn["exspr"])
        flags.add(fl)
        if v is None:
            if "seam_unresolved" in flags:
                return None, "seam_unresolved", {}
            return None, "", {}
        ch[a] = v
    if not ch:
        return None, "", {}
    flag = "seam_resolved" if "seam_resolved" in flags else ""
    return math.fsum(ch.values()), flag, ch


def aggregate_rows(world, panels, months, E, spr, p, blind=False):
    """panel_aggregates.csv rows (fixed panels only) and the in-memory series the reconciliation and the test use."""
    pub = publishable(panels)
    blank = nested_suppression({n: (panels[n]["flow"], panels[n]["members"]) for n in pub})
    rows, series = [], {n: {} for n in PANEL_NAMES}
    for m in months:
        status = "final" if m <= E else "preliminary"
        for n in PANEL_NAMES:
            pn = panels[n]
            if not pn["members"]:
                continue
            val, k, n1, n3 = panel_level(world, pn, m, spr, p)
            ent = {"level": val, "n": k, "n1": n1, "n3": n3}
            if pn["flow"] == "CLOSTLV":
                chg, flag, per = panel_change(world, pn, m, spr, p)
                ent.update({"change": chg, "flag": flag, "per": per})
            series[n][m] = ent
            if n not in pub:
                continue
            sup = "suppressed_diff_lt3" if n in blank else ""
            hide_d = blind and n == "panel_nonoecd_stocks" and on("dry_run_no_d")      # in a DRY_RUN the non-OECD panel's monthly level and change are withheld: they give D
            if hide_d:
                sup = sup or "withheld_dry_run"
            unit = "mb_per_day" if pn["flow"] == "INDPROD" else "mb"
            rows.append({"month": m, "panel": n, "flow": pn["flow"], "unit": unit, "value": None if (sup or hide_d) else val, "n_members": k, "n_code1": n1,
                         "n_code3": n3, "data_status": status, "suppression": sup})
            if pn["flow"] == "CLOSTLV":
                rows.append({"month": m, "panel": n, "flow": "DCLOSTLV", "unit": "mb", "value": None if (sup or hide_d) else ent["change"], "n_members": k,
                             "n_code1": n1, "n_code3": n3, "data_status": status, "suppression": sup})
    return rows, series


# ------------------------------------------------------------------------------------------------------------------------
# reconciliation against STEO (spec 3.3)
# ------------------------------------------------------------------------------------------------------------------------
def steo_basis(steo, last_hist, m):
    if "COPR_WORLD" not in steo or m not in steo["COPR_WORLD"]:
        return ""
    return "historical" if m <= last_hist else "forecast"


def residual_r(steo, last_hist, m):
    """STEO's 'other inventory draws and balance' line in mb for month m (positive = draw); None for a forecast month."""
    s = steo.get("T3_STCHANGE_NOECD" if on("oecd_commercial_only") else "T3_STCHANGE_WORLD", {})
    if m in s and m <= last_hist:
        return s[m] * days_in(m)
    return None


def recon_rows(months, E, series, sums, steo, last_hist, panels, blind=False):
    rows, dd = [], {}
    npn = len(panels["panel_nonoecd_stocks"]["members"])
    for m in months:
        basis = steo_basis(steo, last_hist, m)
        world_mbd = steo["COPR_WORLD"][m] if basis else None
        use = world_mbd if basis == "historical" else None
        pp = series["panel_producers"].get(m, {})
        ppv = pp.get("level")
        sm = sums.get(m)
        nn = series["panel_nonoecd_stocks"].get(m, {})
        oo = series["panel_oecd_stocks_exspr"].get(m, {})
        chg = nn.get("change")
        d = None if chg is None else (-chg if on("sign") else chg)
        if not on("changes_not_levels") and nn.get("level") is not None:
            d = -nn["level"]                  # mutant: the level of the panel's closing stocks instead of its change
        r = residual_r(steo, last_hist, m)
        dd[m] = {"D": d, "R": r, "flag": nn.get("flag", "")}
        hide_d = blind and on("dry_run_no_d")          # in a DRY_RUN D (and anything minus D) is not written
        oech = None
        if basis == "historical" and "PASC_OECD_T3" in steo and m in steo["PASC_OECD_T3"] and month_add(m, -1) in steo["PASC_OECD_T3"]:
            oech = steo["PASC_OECD_T3"][m] - steo["PASC_OECD_T3"][month_add(m, -1)]
        den = use
        if not on("steo_crude_line") and "PAPR_WORLD" in steo and m in steo["PAPR_WORLD"]:
            den = steo["PAPR_WORLD"][m] if basis == "historical" else None
        cov = (lambda x: None if x is None or not den else round(x / den, 2))
        rows.append({"month": m, "data_status": "final" if m <= E else "preliminary", "steo_basis": basis,
                     "steo_world_crude_mbd": world_mbd, "jodi_panel_producers_crude_mbd": ppv,
                     "coverage_reporters": cov(sm["comp_kbd"] / 1000.0) if sm else None,
                     "coverage_reporters_allcodes": cov(sm["allc_kbd"] / 1000.0) if sm else None,
                     "coverage_panel": cov(ppv),
                     "steo_other_draws_balance_mb": r, "jodi_panel_nonoecd_draw_mb": None if hide_d else dd[m]["D"],
                     "steo_residual_minus_panel_mb": (None if hide_d or r is None or dd[m]["D"] is None else r - dd[m]["D"]),
                     "n_panel_nonoecd": nn.get("n"), "seam_flag": nn.get("flag", ""), "steo_oecd_commercial_change_mb": oech,
                     "jodi_panel_oecd_crude_exspr_change_mb": oo.get("change")})
    return rows, dd


def d_leak_tokens(series, dd):
    """Every 3-decimal text form of the non-OECD panel's monthly level, change and draw (either sign), at least 1 mb in size: what a DRY_RUN
    must not write, because D can be differenced out of any of them."""
    toks = set()
    for m, e in series["panel_nonoecd_stocks"].items():
        for v in (e.get("level"), e.get("change"), dd.get(m, {}).get("D")):
            if v is not None:
                toks.add(f(v, 3))
                toks.add(f(-v, 3))
    return {t for t in toks if abs(float(t)) >= 1.0}


# cells that hold a different series from D and may therefore coincide with a D-derived value to three decimals by chance: the scan skips them
OTHER_SERIES = {"steo_reconciliation.csv": {"steo_world_crude_mbd", "jodi_panel_producers_crude_mbd", "steo_other_draws_balance_mb",
                                           "steo_oecd_commercial_change_mb", "jodi_panel_oecd_crude_exspr_change_mb"}}
NUM3 = re.compile(r"(?<![0-9.])-?[0-9]+[.][0-9]{3}(?![0-9.])")


def d_leak_hits(texts, toks):
    """Scan every written text for a D-derived monthly value. CSV cells are scanned except those that hold another series (the OECD and
    producer panels' values, STEO's own columns); anything else (report.txt, an unknown table) is scanned line by line."""
    hits = []
    for name, text in sorted(texts.items()):
        lines = [l for l in text.split("\n") if not l.startswith("#")]
        if name.endswith(".csv") and lines:
            rd = list(csv.reader(io.StringIO("\n".join(lines), newline="")))
            hdr = rd[0]
            for row in rd[1:]:
                rowd = dict(zip(hdr, row))
                for col, cell in rowd.items():
                    if name == "panel_aggregates.csv" and col == "value" and rowd.get("panel") != "panel_nonoecd_stocks":
                        continue
                    if col in OTHER_SERIES.get(name, ()):
                        continue
                    if cell in toks:
                        hits.append((name, cell))
        else:
            for ln in lines:
                hits += [(name, t) for t in NUM3.findall(ln) if t in toks]
    return hits


# ------------------------------------------------------------------------------------------------------------------------
# statistics. Every correlation goes through pearson()/spearman()/bootstrap_ci(), which refuse to run during a DRY_RUN (G25).
# ------------------------------------------------------------------------------------------------------------------------
def _no_corr_in_dry_run():
    if _BLIND[0] and on("dry_run_blind"):
        raise Blind("a correlation was requested during a DRY_RUN build; the primary statistic is not computed on the pre-registration vintage")


def pearson(x, y):
    _no_corr_in_dry_run()
    n = len(x)
    if n < 3 or n != len(y):
        raise DataError("pearson: need two series of equal length of at least 3 (got %d and %d)" % (n, len(y)))
    mx, my = math.fsum(x) / n, math.fsum(y) / n
    sxx = math.fsum((a - mx) ** 2 for a in x)
    syy = math.fsum((b - my) ** 2 for b in y)
    sxy = math.fsum((a - mx) * (b - my) for a, b in zip(x, y))
    if sxx <= 0.0 or syy <= 0.0:
        raise DataError("pearson: a series has zero variance")
    r = sxy / math.sqrt(sxx * syy)
    if not on("pearson_exact"):
        r = r * (n - 1) / n                  # mutant: a population covariance over sample variances
    return r


def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    out, i = [0.0] * len(v), 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return out


def spearman(x, y):
    _no_corr_in_dry_run()
    return pearson(ranks(x), ranks(y))


def demean_by_calendar_month(months, vals):
    """Subtract from each value the mean of the values in the same calendar month (all Januaries, all Februaries, ...) within this sample."""
    groups = collections.defaultdict(list)
    for m, v in zip(months, vals):
        groups[m[5:7]].append(v)
    mu = {k: math.fsum(v) / len(v) for k, v in groups.items()}
    return [v - mu[m[5:7]] for m, v in zip(months, vals)]


def bootstrap_ci(x, y, B=BOOT_B, L=BOOT_L, seed=SEED):
    """Moving-block bootstrap of the n index positions in time order (A9): k = ceil(n / L) blocks per resample, each start
    rng.randrange(n - L + 1), blocks concatenated and truncated to n; one random.Random(seed) created once; B resamples drawn in sequence;
    a resample with zero variance is a hard failure (pearson raises). Sorted ascending: lower = index round(0.025 B), upper = B - 1 - that
    (250 and 9,749 at B = 10,000). Returns (lower, upper)."""
    _no_corr_in_dry_run()
    n = len(x)
    if n < L + 1:
        raise DataError("bootstrap: n = %d is shorter than a block of %d" % (n, L))
    rng = random.Random(seed) if on("seed") else random.Random()
    k = -(-n // L)
    rs = []
    for _ in range(B):
        idx = []
        for _ in range(k):
            if on("boot_start"):
                s = rng.randrange(n - L + 1)
                idx.extend(range(s, s + L))
            else:
                s = rng.randrange(n)
                idx.extend((s + j) % n for j in range(L))
        if on("boot_trunc"):
            idx = idx[:n]
        rs.append(pearson([x[i] for i in idx], [y[i] for i in idx]))
    rs.sort()
    lo = int(round(0.025 * B))
    if not on("boot_pct"):
        lo += 1
    return rs[lo], rs[B - 1 - lo + (0 if on("boot_pct") else 1)]


def verdict_for(r, ci_lo, ci_hi, r_excl, run_ok=True):
    """Spec section 4. r_excl is the demeaned r with 2020-03..2020-12 and the most recent year removed (None counts as failing)."""
    if not run_ok or r is None:
        return "INCONCLUSIVE"
    episode_ok = (r_excl is not None and r_excl >= 0.10) if on("episode_condition") else True
    if r >= 0.25 and ci_lo > 0:
        return "SUPPORTS" if episode_ok else "SUPPORTS (episode-driven)"
    if r < 0.10 and ci_hi < 0.25:
        return "AGAINST"
    return "INCONCLUSIVE"


def concentration(per_member, months, D):
    """share_i = Cov(d_i, D) / Var(D) over the test months, d_i member i's draw (the negative of its change). Sums to 1. Returns
    (largest member, its share, all shares)."""
    n = len(months)
    dm = math.fsum(D) / n
    var = math.fsum((d - dm) ** 2 for d in D)
    if var <= 0:
        return None, None, {}
    shares = {}
    for a in sorted(per_member):
        di = [-per_member[a][m] for m in months]
        mi = math.fsum(di) / n
        shares[a] = math.fsum((u - mi) * (v - dm) for u, v in zip(di, D)) / var
    top = max(sorted(shares), key=lambda a: shares[a])
    return top, shares[top], shares


def month_filter(months, event=None, recent_year=None, start=None):
    keep = []
    for m in months:
        if event and event[0] <= m <= event[1]:
            continue
        if recent_year and int(m[:4]) == recent_year:
            continue
        if start and m < start:
            continue
        keep.append(m)
    return keep


def live_run(status):
    """True when statistics may be computed: a REGISTERED build (the guard dry_run_blind is what keeps a DRY_RUN blind)."""
    return status == "REGISTERED" or not on("dry_run_blind")


def corr_row(role, label, status, months, D, R, n_panel, sha, demeaned, extra=None):
    """One descriptive row of primary_test.csv: Pearson r only, on the demeaned or raw series; blank when the run is a DRY_RUN."""
    row = {"role": role, "label": label, "run_status": status, "window_first": months[0] if months else "", "window_last": months[-1] if months else "",
           "n_months": len(months), "n_seam_excluded": None, "n_panel": n_panel, "panel_sha256": sha, "panel_mean_level_mb": None,
           "largest_member": "", "largest_member_var_share": None, "demeaned": "yes" if demeaned else "no", "pearson_r": None, "ci95_lo": None,
           "ci95_hi": None, "spearman_rho": None, "band_1p96_sqrt_n": None, "verdict": "descriptive" if on("one_primary") else "SUPPORTS"}
    if live_run(status) and len(months) >= 3:
        x, y = (demean_by_calendar_month(months, D), demean_by_calendar_month(months, R)) if demeaned else (D, R)
        try:
            row["pearson_r"] = pearson(x, y)
        except DataError:
            row["pearson_r"] = None
    if extra:
        row.update(extra)
    return row


def primary_block(dd, panels, series, W, E, p, sha, status, world):
    """The pre-registered test and its descriptive companions (spec 3.4). Returns (rows, info). In a DRY_RUN nothing is correlated: the
    row carries the counts, the panel facts and the concentration (which does not involve STEO), and blank statistic cells."""
    nn = panels["panel_nonoecd_stocks"]
    members = nn["members"]
    W1 = [m for m in W if m > W[0]]
    seam_ex = [m for m in W1 if dd.get(m, {}).get("flag") == "seam_unresolved"]
    tm = [m for m in W1 if dd.get(m, {}).get("D") is not None and dd.get(m, {}).get("R") is not None]
    info = {"n": len(tm), "n_seam_excluded": len(seam_ex), "months": tm}
    levels = [series["panel_nonoecd_stocks"][m]["level"] for m in W if series["panel_nonoecd_stocks"].get(m, {}).get("level") is not None]
    mean_level = mean(levels) if levels else None
    info["mean_level"] = mean_level
    reasons = []
    if len(members) < p.min_panel:
        reasons.append("panel_too_thin")
    if mean_level is None or mean_level < p.min_level:
        reasons.append("panel_too_thin") if "panel_too_thin" not in reasons else None
    if len(tm) < p.min_months:
        reasons.append("too_few_months")
    info["run_reasons"] = reasons
    run_ok = not reasons
    info["run_ok"] = run_ok
    D = [dd[m]["D"] for m in tm]
    R = [dd[m]["R"] for m in tm]
    if not on("non_overlapping"):             # mutant: overlapping three-month sums
        D = [math.fsum(D[max(0, i - 2):i + 1]) for i in range(len(D))]
        R = [math.fsum(R[max(0, i - 2):i + 1]) for i in range(len(R))]
    per = {a: {m: series["panel_nonoecd_stocks"][m]["per"][a] for m in tm if a in series["panel_nonoecd_stocks"][m]["per"]} for a in members}
    top, share, shares = (concentration(per, tm, D) if len(tm) >= 3 and all(len(per[a]) == len(tm) for a in members) else (None, None, {}))
    info.update({"largest": top, "share": share, "shares": shares})
    band = (1.96 / math.sqrt(len(tm))) if len(tm) else None
    prim = {"role": "primary", "label": "non-OECD panel draw vs STEO other inventory draws and balance", "run_status": status,
            "window_first": tm[0] if tm else "", "window_last": tm[-1] if tm else "", "n_months": len(tm), "n_seam_excluded": len(seam_ex),
            "n_panel": len(members), "panel_sha256": sha, "panel_mean_level_mb": mean_level, "largest_member": top or "",
            "largest_member_var_share": share, "demeaned": "yes", "pearson_r": None, "ci95_lo": None, "ci95_hi": None, "spearman_rho": None,
            "band_1p96_sqrt_n": band, "verdict": ""}
    rows = [prim]
    info["stats"] = None
    if live_run(status):
        if not run_ok:
            prim["verdict"] = "INCONCLUSIVE"
        else:
            if on("demeaned"):
                xs, ys = demean_by_calendar_month(tm, D), demean_by_calendar_month(tm, R)
                prim["demeaned"] = "yes"
            else:
                xs, ys = D, R
                prim["demeaned"] = "no"
            r = pearson(xs, ys)
            lo, hi = bootstrap_ci(xs, ys, p.boot_b, p.boot_l, p.seed)
            rho = spearman(xs, ys)
            prim.update({"pearson_r": r, "ci95_lo": lo, "ci95_hi": hi, "spearman_rho": rho})
            info["stats"] = {"r": r, "lo": lo, "hi": hi, "rho": rho}
    if not on("one_primary"):
        rows.append(dict(prim))              # mutant: a second primary row
    # descriptive companions (no CI, no verdict)
    nd = len(members)
    sub = {}
    sub["raw"] = ("raw (not demeaned)", tm, False)
    sub["excl_event"] = ("excluding %s..%s" % p.event, month_filter(tm, event=p.event), True)
    sub["excl_recent"] = ("excluding %d" % p.recent_year, month_filter(tm, recent_year=p.recent_year), True)
    sub["excl_both"] = ("excluding %s..%s and %d" % (p.event[0], p.event[1], p.recent_year), month_filter(tm, event=p.event, recent_year=p.recent_year), True)
    sub["start_late"] = ("starting %s" % p.start_late, month_filter(tm, start=p.start_late), True)
    dmap = dict(zip(tm, zip(D, R)))
    for key, (label, ms, dem) in sub.items():
        if ms:
            row = corr_row("descriptive", label, status, ms, [dmap[m][0] for m in ms], [dmap[m][1] for m in ms], nd, sha, dem)
        else:
            row = corr_row("descriptive", label, status, [], [], [], nd, sha, dem)
        rows.append(row)
        if key == "excl_both":
            info["r_excl_both"] = row["pearson_r"]
    # panel restricted to members whose closing stock is code 1 in every month of W
    code1 = [a for a in members if all(world.cell(a, m, "CLOSTLV")[1] == 1 for m in W)]
    if code1 and all(len(per[a]) == len(tm) for a in code1):
        D1 = [-math.fsum(per[a][m] for a in code1) for m in tm]
        rows.append(corr_row("descriptive", "panel restricted to code-1 cells (%d of %d members)" % (len(code1), nd), status, tm, D1, R, len(code1), sha, True))
    else:
        rows.append(corr_row("descriptive", "panel restricted to code-1 cells (0 of %d members)" % nd, status, [], [], [], 0, sha, True))
    if info.get("stats") is not None:
        st = info["stats"]
        prim["verdict"] = verdict_for(st["r"], st["lo"], st["hi"], info.get("r_excl_both"), run_ok)
    return rows, info


def oecd_shared_row(dd_oecd, steo, last_hist, W, p, sha, status):
    """Pearson r of monthly changes: OECD ex-SPR panel against STEO's OECD commercial inventory (a shared source, so not independent)."""
    ms, x, y = [], [], []
    for m in W:
        if m == W[0]:
            continue
        a = dd_oecd.get(m)
        pm = month_add(m, -1)
        s = steo.get("PASC_OECD_T3", {})
        if a is not None and m in s and pm in s and m <= last_hist:
            ms.append(m)
            x.append(a)
            y.append(s[m] - s[pm])
    return corr_row("descriptive", "OECD ex-SPR panel vs STEO OECD commercial change (shared source: IEA data feed both)", status, ms, x, y, None, sha, False)


# ------------------------------------------------------------------------------------------------------------------------
# identity checks, SPR finding, checkpoints
# ------------------------------------------------------------------------------------------------------------------------
def trim(v):
    """A JODI or EIA number as text: up to four decimals, trailing zeros dropped."""
    if v is None:
        return ""
    s = format(round(v, 4), ".4f").rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def ident_pass(stockch, d):
    return abs(stockch - d) <= max(0.01 * abs(d), 100.0)


def identity_stats(world, scope, codeset):
    """JODI's stock identity |STOCKCH - dCLOSTLV| <= max(1% of |dCLOSTLV|, 100 KBBL) over country-months with all three cells numeric
    (month t and t-1 both in `scope`). Returns (n, n_pass, n_exact)."""
    sc = set(scope)
    n = ok = ex = 0
    for m in scope:
        pm = month_add(m, -1)
        if pm not in sc:
            continue
        for a in world.areas:
            c1, c0, s = world.cell(a, m, "CLOSTLV"), world.cell(a, pm, "CLOSTLV"), world.cell(a, m, "STOCKCH")
            if c1[0] is None or c0[0] is None or s[0] is None:
                continue
            cs = (c1[1], c0[1], s[1])
            if codeset == "1_3" and not all(c in (1, 3) for c in cs):
                continue
            if codeset == "all_three_code1" and not all(c == 1 for c in cs):
                continue
            d = c1[0] - c0[0]
            n += 1
            ok += ident_pass(s[0], d)
            ex += abs(s[0] - d) <= 0.5
    return n, ok, ex


def seam_stats(world, year, codeset):
    """January of `year` against December of the year before: CLOSTLV(Jan, new file) - CLOSTLV(Dec, old file) against STOCKCH(Jan, new file)."""
    jan, dec = "%04d-01" % year, "%04d-12" % (year - 1)
    if jan not in world.file_of or dec not in world.file_of:
        return None
    n = ok = 0
    mism = []
    for a in world.areas:
        c1, c0, s = world.cell(a, jan, "CLOSTLV"), world.cell(a, dec, "CLOSTLV"), world.cell(a, jan, "STOCKCH")
        if c1[0] is None or c0[0] is None or s[0] is None:
            continue
        cs = (c1[1], c0[1], s[1])
        if codeset == "1_3" and not all(c in (1, 3) for c in cs):
            continue
        if codeset == "all_three_code1" and not all(c == 1 for c in cs):
            continue
        n += 1
        d = c1[0] - c0[0]
        if ident_pass(s[0], d):
            ok += 1
        else:
            mism.append(a)
    return n, ok, mism


def identity_rows(world, p, maxp):
    rows = []
    first_year = int(p.w0[:4])
    scopes = [(str(first_year), month_range("%04d-01" % first_year, "%04d-12" % first_year)),
              ("%s..%s" % (p.ident_start, maxp), month_range(p.ident_start, maxp))]
    note = {"all": "identity |STOCKCH - dCLOSTLV| <= max(1% of |dCLOSTLV|, 100 KBBL), KBBL; any assessment code 1-3",
            "1_3": "as all, restricted to cells whose three codes are 1 or 3 (the comparable set)",
            "all_three_code1": "STOCKCH, CLOSTLV(t) and CLOSTLV(t-1) all code 1: code-1 cells pass by construction (JODI's assessment includes this identity), so the rate is a data descriptor, not evidence"}
    for label, sc in scopes:
        for cs in ("all", "1_3", "all_three_code1"):
            n, ok, ex = identity_stats(world, sc, cs)
            rows.append({"check": "stock_identity", "scope": label, "code_set": cs, "n": n, "n_pass": ok, "pass_rate": (ok / n if n else None),
                         "n_exact": ex, "note": note[cs]})
    seam_total = {cs: [0, 0] for cs in ("all", "1_3", "all_three_code1")}
    mism_all = []
    if on("seam"):
        for y in sorted({int(m[:4]) for m in world.months if m[5:7] == "01"}):
            for cs in ("all", "1_3", "all_three_code1"):
                st = seam_stats(world, y, cs)
                if st is None:
                    continue
                n, ok, mism = st
                seam_total[cs][0] += n
                seam_total[cs][1] += ok
                if cs == "all":
                    mism_all.append((y, mism))
                    rows.append({"check": "seam", "scope": "%d-12/%d-01" % (y - 1, y), "code_set": cs, "n": n, "n_pass": ok,
                                 "pass_rate": (ok / n if n else None), "n_exact": None,
                                 "note": "CLOSTLV(Jan, new file) - CLOSTLV(Dec, old file) against STOCKCH(Jan, new file); December comes from an older file vintage"})
        for cs in ("all", "1_3", "all_three_code1"):
            n, ok = seam_total[cs]
            rows.append({"check": "seam", "scope": "all year boundaries", "code_set": cs, "n": n, "n_pass": ok, "pass_rate": (ok / n if n else None),
                         "n_exact": None, "note": "sum of the boundary rows" if cs == "all" else "restricted by code as above"})
    for y in sorted(world.files):
        us = world.files[y].unit_stats
        rows.append({"check": "unit_kbd_kbbl", "scope": str(y), "code_set": "all", "n": us["n_kbd"], "n_pass": us["n_kbd"],
                     "pass_rate": 1.0 if us["n_kbd"] else None, "n_exact": us["n_kbd_exact"],
                     "note": "KBD = KBBL / days in month on every crude cell of the file where both are numeric (all flows); worst gap %.5f KBD; exact = within 0.0001" % us["worst_kbd"]})
    return rows, mism_all


def median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def spr_analysis(world, psm, p, maxp, E):
    """Does JODI's US crude stock include the SPR? JODI US STOCKCH against the change in EIA's total (MCRSTUS1) and in total less SPR."""
    r, s = psm["MCRSTUS1"], psm["MCSSTUS1"]
    a_tot, a_ex, big, rows = [], [], [], []
    for m in month_range(p.spr_start, E):
        pm = month_add(m, -1)
        c = world.cell(p.us, m, "STOCKCH")
        if c[0] is None or any(x not in r or x not in s for x in (m, pm)):
            continue
        dtot = r[m] - r[pm]
        dex = (r[m] - s[m]) - (r[pm] - s[pm])
        a_tot.append(abs(c[0] - dtot))
        a_ex.append(abs(c[0] - dex))
        if abs(c[0] - dtot) > SPR_THRESHOLD_KBBL:
            big.append((m, c[0], dtot))
    included = bool(a_tot) and median(a_tot) < 0.1 * median(a_ex)
    offs = []
    for m in (p.w0, p.spr_start, "2025-12", maxp):
        c = world.cell(p.us, m, "CLOSTLV")
        if c[0] is not None and m in r:
            offs.append((m, r[m] - c[0]))
    return {"included": included, "med_tot": median(a_tot) if a_tot else None, "med_ex": median(a_ex) if a_ex else None, "n": len(a_tot),
            "big": big, "offsets": offs}


def checkpoint_rows(world, steo, psm, p, E, maxp):
    rows = []

    def cellrow(area, m, flow):
        c = world.cell(area, m, flow)
        if c[0] is not None:
            return trim(c[0]), ("" if c[1] is None else str(c[1])), "ok" if c[2] == "ok" else c[2]
        return "", "", c[2]

    def add(area, m, flow, comp, compv, note=None):
        unit = "KBD" if flow in RATE_FLOWS else "KBBL"
        jv, jc, st = cellrow(area, m, flow)
        diff = None
        if jv != "" and compv is not None:
            diff = compv - float(jv)
        rows.append({"id": "CK%02d" % (len(rows) + 1), "ref_area": area, "month": m, "flow": flow, "unit": unit, "jodi_value": jv, "jodi_code": jc,
                     "comparator": comp, "comparator_value": trim(compv) if compv is not None else "", "difference": trim(diff) if diff is not None else "",
                     "status": st if not note else (st + ";" + note if st != "ok" else note)})

    r, s, fp = psm["MCRSTUS1"], psm["MCSSTUS1"], psm["MCRFPUS2"]
    for m in (p.w0, p.ck_year_end, E, maxp):
        add(p.us, m, "CLOSTLV", "EIA MCRSTUS1 (kb, incl. SPR); difference = offset", r.get(m))
    for m in p.ck_stockch:
        pm = month_add(m, -1)
        if m in r and pm in r:
            add(p.us, m, "STOCKCH", "EIA change in MCRSTUS1 (kb)", r[m] - r[pm])
            add(p.us, m, "STOCKCH", "EIA change in MCRSTUS1 less MCSSTUS1 (kb)", (r[m] - s[m]) - (r[pm] - s[pm]) if m in s and pm in s else None)
        else:
            add(p.us, m, "STOCKCH", "EIA change in MCRSTUS1 (kb)", None)
            add(p.us, m, "STOCKCH", "EIA change in MCRSTUS1 less MCSSTUS1 (kb)", None)
    for m in (p.ck_year_end, maxp):
        add(p.us, m, "INDPROD", "EIA MCRFPUS2 (kb/d)", fp.get(m))

    def copr(iso, m):
        short = "COPR_" + (FIPS_FOR_ISO.get(iso, iso) if on("fips_map") else iso)
        v = steo.get(short, {}).get(m)
        return None if v is None else v * 1000.0
    for m in (p.w0, p.ck_mid, maxp):
        add("SA", m, "INDPROD", "STEO COPR_SA (kb/d)", copr("SA", m))
    add("NG", maxp, "INDPROD", "STEO COPR_NI (kb/d; STEO uses FIPS: NI is Nigeria)", copr("NG", maxp))
    add("KW", maxp, "INDPROD", "STEO COPR_KU (kb/d; FIPS KU is Kuwait)", copr("KW", maxp))
    add("SA", p.w0, "CLOSTLV", "", None)
    add("SA", maxp, "CLOSTLV", "", None)
    add("JP", maxp, "CLOSTLV", "", None)
    add("CN", maxp, "CLOSTLV", "", None)
    last = ""
    for m in world.months:
        for fl in FLOWS:
            if world.cell("RU", m, fl)[0] is not None:
                last = m
    rows.append({"id": "CK%02d" % (len(rows) + 1), "ref_area": "RU", "month": last, "flow": "any", "unit": "", "jodi_value": "", "jodi_code": "",
                 "comparator": "", "comparator_value": "", "difference": "", "status": "last_numeric_month" if last else "no_numeric_cell"})
    if on("no_country_table") and len(rows) > MAX_CHECKPOINTS:
        raise DataError("checkpoints: %d rows, at most %d" % (len(rows), MAX_CHECKPOINTS))
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# registration (A1): decided from the file, never from the clock
# ------------------------------------------------------------------------------------------------------------------------
def registration(fs_rows, p):
    """('REGISTERED' | 'DRY_RUN', reason). REGISTERED iff the year-`reg_year` file's Last-Modified is on or after reg_lm and its max period is
    on or after reg_max."""
    row = next((r for r in fs_rows if r["file"].endswith("%d.csv" % p.reg_year)), None)
    if not on("registration_from_file"):
        now = p.__dict__.get("now") or dt.datetime.now(dt.timezone.utc)
        return ("REGISTERED" if now >= p.reg_lm else "DRY_RUN"), "mutant: read from the clock"
    if row is None:
        return "DRY_RUN", "no %d file in the cache" % p.reg_year
    lm = None
    if row["last_modified"]:
        try:
            lm = dt.datetime.strptime(row["last_modified"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
        except ValueError:
            lm = None
    if lm is None or not row["max_period"]:
        return "DRY_RUN", "the %d file's Last-Modified or max period is not recorded" % p.reg_year
    if lm < p.reg_lm:
        return "DRY_RUN", "%s was last modified %s, before %s" % (row["file"], row["last_modified"], iso_z(p.reg_lm))
    if row["max_period"] < p.reg_max:
        return "DRY_RUN", "%s ends %s, before %s" % (row["file"], row["max_period"], p.reg_max)
    return "REGISTERED", "%s last modified %s, max period %s" % (row["file"], row["last_modified"], row["max_period"])


def vintage_text(fs_rows, maxp, E):
    parts = []
    for r in fs_rows:
        y = r["file"][-8:-4]
        parts.append("%s:%s:%s" % (y, (r["last_modified"] or "no-last-modified")[:10], r["sha256"][:12]))
    prelim = month_range(month_add(E, 1), maxp)
    return "# vintage: JODI files %s; max TIME_PERIOD %s; preliminary months %s." % (" ".join(parts), maxp, ", ".join(prelim) if prelim else "none")


# ------------------------------------------------------------------------------------------------------------------------
# row formatting
# ------------------------------------------------------------------------------------------------------------------------
TWO_DEC = {"coverage_reporters", "coverage_reporters_allcodes", "coverage_panel"}
INT_COLS = {"n_members", "n_code1", "n_code3", "n_reporters", "n_code2_excluded", "n_zero_reported", "n_ktons_only", "n_not_reported", "n_areas_in_file",
            "n_panel_nonoecd", "n", "n_pass", "n_exact", "n_months", "n_seam_excluded", "n_panel", "months_usable", "months_in_window", "bytes", "rows",
            "n_areas", "n_dash", "n_x", "n_dotdot", "n_code2", "n_code4"}


def fmt_cell(col, v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return f(v, 2 if col in TWO_DEC else 3)
    return str(v)


def table_text(name, header, rows, ack):
    body = []
    for r in rows:
        if isinstance(r, dict):
            body.append([fmt_cell(c, r.get(c)) for c in header])
        else:
            body.append([fmt_cell(c, v) for c, v in zip(header, r)])
    text = render_table(header, body, ack)
    verify_text(name, text, ack)
    return text


# ------------------------------------------------------------------------------------------------------------------------
# inputs, and the whole computation
# ------------------------------------------------------------------------------------------------------------------------
class Inputs:
    pass


PIN_SHA = {2026: "909a73300584b877b122659d549033f1eebab9f93d1131157e47ba0d142ca5e2",
           2025: "5726e6e7319bbb72cf051b2bbdb3ea436ae32a3e0370cea60e04f9472e54870b",
           2015: "08d761f322d81a10c431321515683ebb9bdd4254dd6273c2c8218cb65e6cab4f"}


class Ctx:
    pass


def compute(inp, p, panel_sha=None, panel_only=False, say=print):
    """Everything the build writes, as text, plus the terminal-only block. Writes nothing."""
    ck = []

    def add(cid, name, expected, observed, ok, kind="pin"):
        """kind: 'G' a data-integrity check (a FAIL stops the build), 'pin' a vintage pin (WARN on a changed vintage), 'must' a pin that has
        to hold on any vintage, 'info'."""
        if kind == "info":
            status = "INFO"
        elif kind == "warn":
            status = "PASS" if ok else "WARN"
        elif ok:
            status = "PASS"
        elif kind == "pin" and not pinned:
            status = "WARN"
        else:
            status = "FAIL"
        ck.append((cid, name, expected, observed, status))
    files = inp.files
    world = World(files)
    log_rows = inp.log_rows
    fs_rows = [file_stats_row(files[y], log_rows) for y in sorted(files)]
    for r in fs_rows:
        if not r["last_modified"] or not r["max_period"]:
            raise DataError("file_stats: the vintage of %s is not recorded (Last-Modified or max period is empty)" % r["file"])
    pinned = all(y in files and files[y].sha == s for y, s in PIN_SHA.items()) if p.steo_pins else False
    maxp = max(fd.max_period for fd in files.values())
    E = month_add(maxp, -2) if on("preliminary_lag") else maxp
    months = month_range(p.w0, maxp)
    W = month_range(p.w0, E)
    status, reason = registration(fs_rows, p)
    access, _ = log_vintage(log_rows)
    vint = vintage_text(fs_rows, maxp, E)
    ack = ack_lines(access, vint)
    spr = inp.psm["MCSSTUS1"]
    panels = make_panels(world, W, spr, p)
    prow = panel_rows(panels, p, W)
    ptext = table_text("panels.csv", PANELS_COLS, prow, ack)
    psha = sha256_of(ptext.encode("utf-8"))
    ctx = Ctx()
    ctx.status, ctx.reason, ctx.E, ctx.maxp, ctx.W, ctx.panel_sha, ctx.ack = status, reason, E, maxp, W, psha, ack
    ctx.texts = {"panels.csv": ptext}
    ctx.terminal = []
    ctx.panels, ctx.checks, ctx.fs_rows = panels, ck, fs_rows
    if panel_only:
        return ctx
    if on("panel_frozen"):
        if panel_sha is not None and panel_sha != psha:
            raise Refused("the panel changed: panels.csv now hashes to %s, not the %s passed with --panel-sha; the primary is not computed" % (psha, panel_sha))
        if status == "REGISTERED" and panel_sha is None:
            raise Refused("a REGISTERED build needs --panel-sha <hex> (the sha256 recorded in CALENDAR.tsv from `build --panel-only`)")
    _BLIND[0] = status != "REGISTERED"
    try:
        _compute_rest(ctx, inp, p, world, fs_rows, panels, months, W, E, maxp, status, reason, ack, psha, pinned, add, say)
    finally:
        _BLIND[0] = False
    return ctx


def _compute_rest(ctx, inp, p, world, fs_rows, panels, months, W, E, maxp, status, reason, ack, psha, pinned, add, say):
    ck, files = ctx.checks, inp.files
    spr = inp.psm["MCSSTUS1"]
    steo, last_hist = inp.steo, inp.last_hist
    # ---- G checks that the parse and the groups already enforced -------------------------------------------------------------------
    add("G01", "every file has the exact JODI header and one row per crude key", "all %d files" % len(files), "%d files read" % len(files), True, "G")
    add("G02", "unit relation KBD = KBBL / days in the month on every crude cell where both are numeric (hard; 0.01 KBD)", "worst gap <= 0.01 KBD",
        "worst gap %.5f KBD over %d cells" % (max(fd.unit_stats["worst_kbd"] for fd in files.values()), sum(fd.unit_stats["n_kbd"] for fd in files.values())),
        all(fd.unit_stats["worst_kbd"] <= 0.01 for fd in files.values()), "G")
    add("G02b", "other unit relations: KL = KBBL x 0.158987 (within the rounding of KL), CONVBBL = 1000 x KBBL / KTONS (within 1); counted, not enforced", "few exceptions",
        "KL off %d of %d cells; CONVBBL off %d of %d; %d cells numeric in KTONS only (never used)" % (
            sum(fd.unit_stats["n_kl_off"] for fd in files.values()), sum(fd.unit_stats["n_kl"] for fd in files.values()),
            sum(fd.unit_stats["n_conv_off"] for fd in files.values()), sum(fd.unit_stats["n_conv"] for fd in files.values()),
            sum(fd.unit_stats["n_ktons_only"] for fd in files.values())), True, "info")
    code4 = sum(fd.codes["4"] for fd in files.values())
    add("G03", "assessment codes on numeric cells", "only 1-4; 2 and 4 excluded and counted", "code 1 %d, code 2 %d, code 3 %d, code 4 %d" % tuple(
        sum(fd.codes[k] for fd in files.values()) for k in "1234"), all(fd.codes_other == 0 for fd in files.values()), "G")
    add("G04", "every cached file has a fetch-log row with the same sha256; Last-Modified and max period recorded", "%d files" % len(files),
        "%d rows in file_stats.csv" % len(fs_rows), len(fs_rows) == len(files), "G")
    rows_cov, sums = coverage_tables(world, months, p)
    for r in rows_cov:
        r["data_status"] = "final" if r["month"] <= E else "preliminary"
    add("G05", "partition: reporters_oecd + reporters_nonoecd = reporters_all (counts and in-memory sums), every month and flow", "holds",
        "holds in %d months x 2 flows" % len(months), True, "G")
    add("G06", "window and preliminary lag", "E = max period - 2 months", "max %s, E %s, window %s..%s (%d months)" % (maxp, E, W[0], W[-1], len(W)), E == month_add(maxp, -2), "G")
    pub = publishable(panels)
    add("G07", "disclosure: panels published only with at least 3 members; reporter groups only as counts and ratios", "3 or more members",
        "; ".join("%s %d%s" % (n, len(panels[n]["members"]), "" if n in pub else " (not published)") for n in PANEL_NAMES), True, "G")
    blind = status != "REGISTERED"
    agg_rows, series = aggregate_rows(world, panels, months, E, spr, p, blind)
    rec_rows, dd = recon_rows(months, E, series, sums, steo, last_hist, panels, blind)
    dd_oecd = {m: series["panel_oecd_stocks_exspr"].get(m, {}).get("change") for m in months}
    ident_rows, seam_mism = identity_rows(world, p, maxp)
    ckpt = checkpoint_rows(world, steo, inp.psm, p, E, maxp)
    spr_res = spr_analysis(world, inp.psm, p, maxp, E)
    sha = psha
    prim_rows, pinfo = primary_block(dd, panels, series, W, E, p, sha, status, world)
    oecd_row = oecd_shared_row(dd_oecd, steo, last_hist, W, p, sha, status)
    prim_rows.append(oecd_row)
    n_primary = sum(1 for r in prim_rows if r["role"] == "primary")
    add("G08", "exactly one primary row; ci95 and a verdict only on it", "1 primary row", "%d primary row(s)" % n_primary,
        n_primary == 1 and all(r["verdict"] == "descriptive" and r["ci95_lo"] is None and r["ci95_hi"] is None for r in prim_rows if r["role"] != "primary"), "G")
    seam_n = sum(len(m) for _, m in seam_mism)
    add("G09", "seam check: December (older file) to January (new file) against STOCKCH", "no country-boundary off beyond max(1%, 100 KBBL) (older files are older vintages)",
        "%d country-boundaries off" % seam_n, seam_n == 0, "warn")
    # ---- success criteria -----------------------------------------------------------------------------------------------------------
    if p.steo_pins:
        _pins(ctx, inp, p, world, add, files, fs_rows, E, maxp, spr_res, ident_rows, ckpt, steo, last_hist, status, sums)
    add("C10", "primary row", "one primary row; DRY_RUN has blank statistic cells" if status == "DRY_RUN" else "one primary row with n >= %d, the CI and a verdict" % p.min_months,
        "%s, n = %d, statistic cells %s" % (status, pinfo["n"], "blank" if prim_rows[0]["pearson_r"] is None else "filled"),
        (prim_rows[0]["pearson_r"] is None) if status == "DRY_RUN" else (prim_rows[0]["pearson_r"] is not None or not pinfo["run_ok"]), "must")
    # ---- outputs ---------------------------------------------------------------------------------------------------------------------
    T = ctx.texts
    T["file_stats.csv"] = table_text("file_stats.csv", FILE_STATS_COLS, fs_rows, ack)
    T["panel_aggregates.csv"] = table_text("panel_aggregates.csv", PANEL_AGG_COLS, agg_rows, ack)
    T["coverage_counts.csv"] = table_text("coverage_counts.csv", COVERAGE_COLS, rows_cov, ack)
    T["steo_reconciliation.csv"] = table_text("steo_reconciliation.csv", RECON_COLS, rec_rows, ack)
    T["primary_test.csv"] = table_text("primary_test.csv", PRIMARY_COLS, prim_rows, ack)
    T["identity_checks.csv"] = table_text("identity_checks.csv", IDENT_COLS, ident_rows, ack)
    T["checkpoints.csv"] = table_text("checkpoints.csv", CHECKPOINT_COLS, ckpt, ack)
    head = SRC_JODI.split("%s")[0]
    n_out = len(T) + 2                      # report.txt and checks.csv are written from the same three lines
    first_ok = all(t.startswith(head) for t in T.values()) and ack[0].startswith(head)
    add("C11a", "every output's first line names JODI", "all %d outputs" % n_out, "%d of %d" % (n_out if first_ok else 0, n_out), first_ok, "G")
    if p.steo_pins:
        stray = []
        for root_, dirs_, names_ in os.walk(ROOT):
            dirs_[:] = [d for d in dirs_ if d != ".git"]
            stray += [os.path.join(root_, n) for n in names_ if re.fullmatch(r"jodi_primary_.*\.csv|primaryyear.*\.csv|secondaryyear.*\.csv", n)]
        add("C11b", "no JODI annual file anywhere under the repository", "none", ", ".join(os.path.relpath(s, ROOT) for s in stray) or "none", not stray, "G")
    od = getattr(inp, "out_dir", None)
    if od and p.steo_pins:
        stale = []
        for fn in ("README.md", "SOURCES_JODI.md"):
            pth = os.path.join(od, fn)
            txt = open(pth, encoding="utf-8").read() if os.path.exists(pth) else ""
            plain = [l[len("# source: "):].strip() for l in ack[:2]]
            if not all(x in txt.replace("\n", " ") for x in plain):
                stale.append(fn)
        add("C11c", "README.md and SOURCES_JODI.md carry this build's JODI and EIA acknowledgement lines (access date included)", "both do", "stale or missing: " + ", ".join(stale) if stale else "both do", not stale, "warn")
    ctx.rec_rows, ctx.agg_rows, ctx.prim_rows, ctx.ident_rows, ctx.ckpt, ctx.pinfo = rec_rows, agg_rows, prim_rows, ident_rows, ckpt, pinfo
    ctx.spr_res, ctx.cov_rows, ctx.sums, ctx.series, ctx.dd = spr_res, rows_cov, sums, series, dd
    ctx.seam_mism = seam_mism
    # terminal-only coverage block (C3): reporter sums are never written
    t = ctx.terminal
    t.append("TERMINAL ONLY (reporter barrel sums are never written to a file; R6):")
    for m in (p.w0, p.ck_mid, maxp):
        if m in sums:
            s_ = sums[m]
            den = steo.get("COPR_WORLD", {}).get(m)
            t.append("  %s: all codes %d reporters, %.2f mb/d, %s of STEO world crude; codes 1 and 3 only %d reporters, %.2f mb/d, %s"
                     % (m, s_["n_allc"], s_["allc_kbd"] / 1000.0, ("%.3f" % (s_["allc_kbd"] / 1000.0 / den)) if den else "n/a", s_["n_comp"],
                        s_["comp_kbd"] / 1000.0, ("%.3f" % (s_["comp_kbd"] / 1000.0 / den)) if den else "n/a"))
    ym = [m for m in months if m[:4] == p.ck_year_end[:4]]
    if ym and all(m in sums for m in ym):
        mean_all = mean([sums[m]["allc_kbd"] / 1000.0 for m in ym])
        sm = [steo["COPR_WORLD"][m] for m in ym if m in steo.get("COPR_WORLD", {})]
        t.append("  %s mean of monthly all-code sums %.2f mb/d%s" % (p.ck_year_end[:4], mean_all, (", %.3f of STEO's mean %.2f" % (mean_all / mean(sm), mean(sm))) if len(sm) == len(ym) else ""))
    dtoks = d_leak_tokens(series, dd)
    hits = d_leak_hits(T, dtoks) if blind else []
    add("G10", "DRY_RUN blindness: no monthly value of the non-OECD panel's level, change or draw (D) in any written table", "none" if blind else "n/a (REGISTERED: filled)",
        ("%d D-derived values written (first in %s; the values are not repeated here)" % (len(hits), hits[0][0])) if hits else ("none among %d candidate values" % len(dtoks) if blind else "n/a"), not hits, "G")
    ctx.report = build_report(ctx, inp, p, status, reason, E, maxp)
    T["report.txt"] = "\n".join(ack) + "\n" + "\n".join(ctx.report) + "\n"
    rh = d_leak_hits({"report.txt": T["report.txt"]}, dtoks) if blind else []
    if rh:
        raise DataError("G10: report.txt carries a D-derived monthly value in a DRY_RUN")
    T["checks.csv"] = table_text("checks.csv", CHECKS_COLS, [list(c) for c in ck], ack)
    hard = [c for c in ck if c[4] == "FAIL" and c[0].startswith("G")]
    if hard:
        raise DataError("G-check failed: " + "; ".join("%s %s (observed: %s)" % (c[0], c[1], c[3]) for c in hard))


def _pins(ctx, inp, p, world, add, files, fs_rows, E, maxp, spr_res, ident_rows, ckpt, steo, last_hist, status, sums):
    f26, f25, f15 = files.get(2026), files.get(2025), files.get(2015)
    r26 = next(r for r in fs_rows if r["file"].endswith("2026.csv")) if f26 else None
    # C1
    ok = bool(f26 and f26.rows == 134400 and len(f26.areas) == 96 and f26.max_period == "2026-07" and f26.sha == PIN_SHA[2026])
    add("C1a", "primaryyear2026.csv: rows, areas, max period, sha256", "134,400 rows; 96 areas; max 2026-07; 909a7330...", "%s rows; %s areas; max %s; %s..." % (
        f26.rows if f26 else "-", len(f26.areas) if f26 else "-", f26.max_period if f26 else "-", f26.sha[:8] if f26 else "-"), ok)
    ok = bool(f25 and f25.rows == 283200 and len(f25.areas) == 118 and f25.sha == PIN_SHA[2025])
    add("C1b", "2025.csv: rows, areas, sha256", "283,200 rows; 118 areas; 5726e6e7...", "%s rows; %s areas; %s..." % (f25.rows if f25 else "-", len(f25.areas) if f25 else "-", f25.sha[:8] if f25 else "-"), ok)
    r15 = next((r for r in fs_rows if r["file"] == "2015.csv"), None)
    ok = bool(f15 and f15.rows == 283200 and len(f15.areas) == 118 and r15 and r15["last_modified"].startswith("2025-10-21"))
    add("C1c", "2015.csv: rows, areas, Last-Modified", "283,200 rows; 118 areas; 2025-10-21", "%s rows; %s areas; %s" % (f15.rows if f15 else "-", len(f15.areas) if f15 else "-", r15["last_modified"][:10] if r15 else "-"), ok)
    add("C1d", "no code 4 in the 2015, 2025 and 2026 files", "0", str(sum(files[y].codes["4"] for y in (2015, 2025, 2026) if y in files)),
        all(files[y].codes["4"] == 0 for y in (2015, 2025, 2026) if y in files))
    want_e = "2026-05" if maxp == "2026-07" else ("2026-06" if maxp == "2026-08" else E)
    add("C1e", "E = max period - 2", want_e, E, E == want_e)
    # C2
    us_conv = world.raw("US", "2026-07", "INDPROD", "CONVBBL")
    add("C2a", "KBD = KBBL / days on every crude cell where both are numeric (2026 file)", "2,137 cells, worst gap <= 0.00005 KBD",
        "%d cells, worst gap %.5f KBD" % (f26.unit_stats["n_kbd"], f26.unit_stats["worst_kbd"]) if f26 else "-", bool(f26 and f26.unit_stats["n_kbd"] == 2137 and f26.unit_stats["worst_kbd"] <= 5e-5))
    add("C2b", "CONVBBL for US INDPROD 2026-07", "7400", trim(us_conv[0]) if us_conv else "-", bool(us_conv and us_conv[0] == 7400.0))
    # C3 (the sums themselves are printed to the terminal only; this row records whether they match the pins)
    cw_ = steo["COPR_WORLD"]
    def cov3(m):
        s_ = sums.get(m)
        return None if s_ is None else (s_["n_allc"], round(s_["allc_kbd"] / 1000.0, 2), round(s_["allc_kbd"] / 1000.0 / cw_[m], 3), s_["n_comp"], round(s_["comp_kbd"] / 1000.0, 2), round(s_["comp_kbd"] / 1000.0 / cw_[m], 3))
    y25 = [m for m in month_range("2025-01", "2025-12") if m in sums]
    m25 = (round(mean([sums[m]["allc_kbd"] / 1000.0 for m in y25]), 2), round(mean([sums[m]["allc_kbd"] / 1000.0 for m in y25]) / mean([cw_[m] for m in y25]), 3)) if len(y25) == 12 else None
    s26 = sums.get("2026-07")
    okc3 = (cov3("2015-01") == (95, 73.96, 0.974, 85, 61.34, 0.808) and m25 == (46.79, 0.592)
            and s26 is not None and s26["n_allc"] == 47 and round(s26["allc_kbd"] / 1000.0, 2) == 40.49)
    add("C3", "coverage against STEO world crude: 2015-01 all codes 95 reporters / ratio 0.974, codes 1 and 3 85 / 0.808; 2025 mean ratio 0.592; 2026-07 47 reporters",
        "all match the pins (reporter sums are printed to the terminal only)", "all match (values in the terminal block)" if okc3 else "DO NOT MATCH: see the terminal block", okc3)
    # C4
    idm = {(r["check"], r["scope"], r["code_set"]): r for r in ident_rows}
    scope_b = "%s..%s" % (p.ident_start, maxp)
    for tag, key, want in (("C4a", ("stock_identity", scope_b, "all"), (974, 901, 712)), ("C4b", ("stock_identity", scope_b, "all_three_code1"), (702, 702, None)),
                           ("C4c", ("stock_identity", "2015", "all"), (961, 894, None)), ("C4d", ("stock_identity", "2015", "all_three_code1"), (441, 441, None))):
        r = idm.get(key)
        obs = (r["n"], r["n_pass"], r["n_exact"]) if r else None
        ok = bool(r and obs[0] == want[0] and obs[1] == want[1] and (want[2] is None or obs[2] == want[2]))
        add(tag, "stock identity %s, %s, %s: n, pass%s" % (key[1], key[2], "KBBL", ", exact" if want[2] is not None else ""), "/".join(str(x) for x in want if x is not None),
            "/".join(str(x) for x in obs if x is not None) if obs else "-", ok)
    # C5
    c = world.cell("US", "2026-07", "CLOSTLV")
    r_, s_ = inp.psm["MCRSTUS1"], inp.psm["MCSSTUS1"]
    add("C5a", "US CLOSTLV 2026-07 (JODI, KBBL); MCRSTUS1; MCSSTUS1", "568,729; 713,343; 304,810", "%s; %s; %s" % (trim(c[0]), trim(r_.get("2026-07")), trim(s_.get("2026-07"))),
        bool(c[0] == 568729.0 and r_.get("2026-07") == 713343.0 and s_.get("2026-07") == 304810.0))
    pins5 = (("2026-05", -64114, -64113, -24970), ("2026-04", -23547, -23552, -3251), ("2026-06", -54279, -54277, -21082))
    for m, sc, d_tot, d_ex in pins5:
        pm = month_add(m, -1)
        st = world.cell("US", m, "STOCKCH")[0]
        dt_ = r_[m] - r_[pm]
        de_ = (r_[m] - s_[m]) - (r_[pm] - s_[pm])
        add("C5-" + m, "US STOCKCH %s vs change in MCRSTUS1 and in MCRSTUS1 less SPR" % m, "%d vs %d and %d" % (sc, d_tot, d_ex),
            "%s vs %s and %s" % (trim(st), trim(dt_), trim(de_)), bool(st == sc and dt_ == d_tot and de_ == d_ex))
    add("C5v", "spr_included = yes: median |STOCKCH - dMCRSTUS1| < 0.1 x median |STOCKCH - d(MCRSTUS1 - MCSSTUS1)| over %s..E" % p.spr_start, "yes",
        "%s (medians %s and %s KBBL, n = %d)" % ("yes" if spr_res["included"] else "no", trim(spr_res["med_tot"]), trim(spr_res["med_ex"]), spr_res["n"]), spr_res["included"], "must")
    big = {m: (a, b) for m, a, b in spr_res["big"]}
    add("C5w", "months with |STOCKCH - dMCRSTUS1| > 2,000 KBBL (2025-03 must be among them: JODI -5,654 vs EIA +3,549)", "2025-03 listed",
        ", ".join("%s (%s vs %s)" % (m, trim(a), trim(b)) for m, (a, b) in sorted(big.items())) or "none", "2025-03" in big and big["2025-03"][0] == -5654.0 and big["2025-03"][1] == 3549.0)
    offs = dict(spr_res["offsets"])
    add("C5x", "level offset MCRSTUS1 - JODI US CLOSTLV (kb), unexplained (OPEN-2)", "99,121 (2015-01); 135,979 (2025-01); 144,612 (2025-12); 144,614 (2026-07)",
        "; ".join("%s: %s" % (m, trim(v)) for m, v in sorted(offs.items())), [offs.get(m) for m in ("2015-01", "2025-01", "2025-12", "2026-07")] == [99121.0, 135979.0, 144612.0, 144614.0])
    ex_ = inp.psm["MCESTUS1"]
    gaps = [abs(r_[m] - s_[m] - ex_[m]) for m in r_ if m in s_ and m in ex_]
    add("C5y", "EIA total less SPR equals EIA's own commercial-excluding-SPR series (MCRSTUS1 - MCSSTUS1 = MCESTUS1)", "equal to within 1 kb", "worst gap %s kb over %d months" % (trim(max(gaps)) if gaps else "n/a", len(gaps)),
        bool(gaps) and max(gaps) <= 1.0, "info")
    # C6
    bymark = {(r["ref_area"], r["month"], r["flow"], r["comparator"][:12]): r for r in ckpt}
    us_ip = next((r for r in ckpt if r["ref_area"] == "US" and r["flow"] == "INDPROD" and r["month"] == maxp), None)
    sa_ip = next((r for r in ckpt if r["ref_area"] == "SA" and r["flow"] == "INDPROD" and r["month"] == maxp), None)
    ng_ip = next((r for r in ckpt if r["ref_area"] == "NG"), None)
    kw_ip = next((r for r in ckpt if r["ref_area"] == "KW"), None)
    got = [(r["jodi_value"], r["comparator_value"]) if r else ("-", "-") for r in (us_ip, sa_ip, ng_ip, kw_ip)]
    add("C6", "checkpoints at max month: US INDPROD vs MCRFPUS2; SA vs COPR_SA; NG vs COPR_NI; KW vs COPR_KU (kb/d; difference printed, no pass/fail)",
        "13817.3871 vs 13948; 8135.0968 vs 7830; 1505 vs 1420; 1971 vs 1770", "; ".join("%s vs %s" % g for g in got),
        got[0][0] == "13817.3871" and got[1][0] == "8135.0968" and got[2][0] == "1505" and got[3][0] == "1971")
    # C7
    cn26 = all(world.cell("CN", m, "CLOSTLV")[0] is None for m in month_range("2026-01", maxp))
    ru = any(world.cell("RU", m, fl)[0] is not None for m in month_range("2025-01", maxp) for fl in FLOWS)
    iq = any(world.cell(a, m, fl)[0] is not None for a in ("IQ", "IR", "AE") for m in month_range("2025-01", maxp) for fl in FLOWS)
    add("C7", "CN CLOSTLV not numeric in every 2026 month; no numeric RU crude cell and none for IQ, IR, AE in 2025-2026", "all hold",
        "CN %s; RU %s; IQ/IR/AE %s" % ("not numeric" if cn26 else "NUMERIC", "none" if not ru else "NUMERIC", "none" if not iq else "NUMERIC"), cn26 and not ru and not iq, "must")
    # C8, C9
    cw = steo["COPR_WORLD"]

    def ymean(y):
        v = [cw["%d-%02d" % (y, k)] for k in range(1, 13) if "%d-%02d" % (y, k) in cw]
        return mean(v) if len(v) == 12 else None
    m15, m25, m26 = ymean(2015), ymean(2025), ymean(2026)
    add("C8a", "STEO COPR_WORLD annual means 2015; 2025; 2026 (2026 incl. forecast months, printed only)", "76.86; 78.99; 75.44",
        "%s; %s; %s" % tuple("n/a" if x is None else "%.2f" % x for x in (m15, m25, m26)),
        m15 is not None and round(m15, 2) == 76.86 and round(m25, 2) == 78.99 and round(m26, 2) == 75.44)
    add("C8b", "PASC_OECD_T3 2025-12; T3_STCHANGE_NOECD 2025-12", "2,831.603; -1.714", "%s; %s" % (f(steo["PASC_OECD_T3"].get("2025-12"), 3), f(steo["T3_STCHANGE_NOECD"].get("2025-12"), 3)),
        round(steo["PASC_OECD_T3"].get("2025-12", 0), 3) == 2831.603 and round(steo["T3_STCHANGE_NOECD"].get("2025-12", 0), 3) == -1.714)
    xf = inp.steo_xlsx
    if xf is None:
        add("C8c", "STEO bulk values equal the crude ledger's eia_STEO_m.xlsx within 0.001 (2022-01 to 2027-12)", "equal", "workbook or openpyxl not available: not checked", False, "info")
    else:
        _, xv = xf
        worst, n = 0.0, 0
        for short, d in xv.items():
            for m, v in d.items():
                b = steo.get(short, {}).get(m)
                if b is not None:
                    n += 1
                    worst = max(worst, abs(b - v))
        add("C8c", "STEO bulk values equal the crude ledger's eia_STEO_m.xlsx within 0.001 (2022-01 to 2027-12)", "worst gap <= 0.001", "%d values, worst gap %.6f" % (n, worst), n > 0 and worst <= 0.001)
    sw = steo["T3_STCHANGE_WORLD"]
    nn = steo["T3_STCHANGE_NOECD"]
    s9 = sum(sw["2026-%02d" % k] * days_in("2026-%02d" % k) for k in range(1, 10))
    h1 = sum(sw["2026-%02d" % k] * days_in("2026-%02d" % k) for k in range(1, 7))
    r9 = sum(nn["2026-%02d" % k] * days_in("2026-%02d" % k) for k in range(1, 10))
    r7 = sum(nn["2026-%02d" % k] * days_in("2026-%02d" % k) for k in range(1, 8))
    add("C9", "sum of STEO withdrawals 2026-01..09 (world) and H1; residual line 2026-01..09 and 2026-01..07 (mb; printed for context, unmatched)",
        "424.4; 252.3; 145.94 +/- 0.05; 42.6", "%.1f; %.1f; %.2f; %.1f" % (s9, h1, r9, r7),
        round(s9, 1) == 424.4 and round(h1, 1) == 252.3 and abs(r9 - 145.94) <= 0.05 and round(r7, 1) == 42.6)


# ------------------------------------------------------------------------------------------------------------------------
# the report (written to report.txt; it holds no reporter barrel sum, which R6 keeps to the terminal)
# ------------------------------------------------------------------------------------------------------------------------
def verdict_sentence(verdict, info, prim, p):
    st, n = info.get("stats"), prim["n_months"]
    who = "a fixed panel of %d countries, mean %s mb, of which %s carries %s%% of the change variance" % (
        prim["n_panel"], f(prim["panel_mean_level_mb"], 1), prim["largest_member"] or "n/a", f(100 * prim["largest_member_var_share"], 0) if prim["largest_member_var_share"] is not None else "n/a")
    if verdict == "SUPPORTS":
        return ("Reported non-OECD crude stock changes (%s) move with EIA's 'other inventory draws and balance' line, r = %s, n = %d." % (who, f(st["r"], 3), n))
    if verdict == "SUPPORTS (episode-driven)":
        return ("Reported non-OECD crude stock changes (%s) co-moved with EIA's 'other inventory draws and balance' line during %s..%s and %d, not outside them; "
                "r = %s, n = %d." % (who, p.event[0], p.event[1], p.recent_year, f(st["r"], 3), n))
    if verdict == "AGAINST":
        return ("EIA's residual line is not visible in reported non-OECD crude stocks (%s): r = %s, 95%% CI [%s, %s], n = %d. This does not mean the residual is wrong."
                % (who, f(st["r"], 3), f(st["lo"], 3), f(st["hi"], 3), n))
    return "INCONCLUSIVE: r = %s, 95%% CI [%s, %s], n = %d; neither the SUPPORTS nor the AGAINST condition holds." % (
        f(st["r"], 3) if st else "n/a", f(st["lo"], 3) if st else "n/a", f(st["hi"], 3) if st else "n/a", n)


def build_report(ctx, inp, p, status, reason, E, maxp):
    L = []
    P = L.append
    P("JODI WORLD OIL LEDGER: country-reported crude production and closing stocks, reconciled with EIA's STEO")
    P("")
    P("RUN STATUS: %s" % status)
    P("  %s" % reason)
    P("")
    P("1. FILES AND VINTAGE")
    P("  %-4s %-20s %-21s %-8s %8s %5s  %s" % ("year", "file", "last modified (UTC)", "max", "rows", "areas", "sha256 (12)"))
    for r in ctx.fs_rows:
        P("  %-4s %-20s %-21s %-8s %8d %5d  %s" % (r["file"][-8:-4], r["file"], r["last_modified"], r["max_period"], r["rows"], r["n_areas"], r["sha256"][:12]))
    P("  Window W = %s to %s (%d months). Months after E = %s (%s) are preliminary: published, flagged, never in a statistic." % (
        ctx.W[0], E, len(ctx.W), E, ", ".join(month_range(month_add(E, 1), maxp)) or "none"))
    P("")
    P("2. FIXED PANELS (frozen for this vintage; panels.csv sha256 %s)" % ctx.panel_sha)
    for n in PANEL_NAMES:
        pn = ctx.panels[n]
        lv = [ctx.series[n][m]["level"] for m in ctx.W if m in ctx.series[n] and ctx.series[n][m]["level"] is not None]
        unit = "mb/d" if pn["flow"] == "INDPROD" else "mb"
        P("  %-26s %3d members%s; mean over W %s %s" % (n, len(pn["members"]), "" if len(pn["members"]) >= 3 else " (fewer than 3: not published)",
                                                     f(mean(lv), 1) if lv else "n/a", unit))
    P("  The US member of panel_oecd_stocks_exspr is JODI's US figure less EIA's SPR (JODI's US crude stocks include the SPR; see 5).")
    P("")
    P("3. COVERAGE OF STEO WORLD CRUDE PRODUCTION (ratios at 0.01; reporters change over time, so these are not a consistent series of one set of countries)")
    P("  %-8s %10s %10s %10s %12s %14s" % ("month", "reporters", "(+code 2)", "ratio", "ratio+code2", "panel ratio"))
    rec = {r["month"]: r for r in ctx.rec_rows}
    cov = {(r["month"], r["group"], r["flow"]): r for r in ctx.cov_rows}
    for m in sorted({p.w0, p.ck_mid, ctx.W[-1], maxp}):
        if m in rec:
            c = cov[(m, "reporters_all", "INDPROD")]
            P("  %-8s %10d %10d %10s %12s %14s" % (m, c["n_reporters"], c["n_reporters"] + c["n_code2_excluded"], f(rec[m]["coverage_reporters"], 2) or "n/a",
                                                    f(rec[m]["coverage_reporters_allcodes"], 2) or "n/a", f(rec[m]["coverage_panel"], 2) or "n/a"))
    P("  The fall in the ratio is countries that stopped reporting (counts above), not lower output.")
    P("")
    P("4. OECD STOCKS AGAINST STEO (shared source: IEA data feed both, so agreement is not independent evidence)")
    orow = [r for r in ctx.prim_rows if r["label"].startswith("OECD")][0]
    P("  months %d; Pearson r of monthly changes: %s" % (orow["n_months"], f(orow["pearson_r"], 3) if orow["pearson_r"] is not None else "not computed (DRY_RUN)"))
    P("")
    P("5. DOES JODI'S US CRUDE STOCK INCLUDE THE SPR?")
    sr = ctx.spr_res
    P("  spr_included = %s: median |STOCKCH - change in EIA total| %s KBBL against %s KBBL for the change excluding the SPR, over %s..E (n = %d)." % (
        "yes" if sr["included"] else "no", trim(sr["med_tot"]), trim(sr["med_ex"]), p.spr_start, sr["n"]))
    P("  Months where |STOCKCH - change in MCRSTUS1| exceeds %d KBBL: %s" % (SPR_THRESHOLD_KBBL, ", ".join("%s (JODI %s, EIA %s)" % (m, trim(a), trim(b)) for m, a, b in sr["big"]) or "none"))
    P("  Level offset, EIA total less JODI (kb): %s. Unexplained (OPEN-2)." % "; ".join("%s %s" % (m, trim(v)) for m, v in sr["offsets"]))
    P("")
    P("6. STOCK IDENTITY AND SEAMS")
    for r in ctx.ident_rows:
        if r["check"] == "stock_identity" and r["code_set"] != "1_3":
            P("  stock identity, %s, %s: %d of %d pass (%s); exact %s" % (r["scope"], r["code_set"], r["n_pass"], r["n"], f(r["pass_rate"], 3), r["n_exact"]))
    allr = [r for r in ctx.ident_rows if r["check"] == "seam" and r["scope"] == "all year boundaries" and r["code_set"] == "all"]
    if allr:
        P("  seams (December of an older file to January of the new one), all boundaries: %d of %d pass; older files are older vintages." % (allr[0]["n_pass"], allr[0]["n"]))
    P("")
    P("7. THE PRE-REGISTERED TEST (spec sections 3.4 and 4)")
    prim = ctx.prim_rows[0]
    info = ctx.pinfo
    P("  D = the panel's draw (minus the change in closing stocks), R = STEO's 'other inventory draws and balance' line, months %s..%s." % (ctx.W[1] if len(ctx.W) > 1 else "", E))
    P("  test months n = %d (seam months excluded: %d); panel %d countries, mean level %s mb; run conditions %s." % (
        prim["n_months"], prim["n_seam_excluded"], prim["n_panel"], f(prim["panel_mean_level_mb"], 1) if prim["panel_mean_level_mb"] is not None else "n/a",
        "met" if info["run_ok"] else "NOT met (" + ", ".join(info["run_reasons"]) + ")"))
    if prim["largest_member"]:
        P("  largest member of the panel's change variance: %s, share %s (shares sum to 1)." % (prim["largest_member"], f(prim["largest_member_var_share"], 3)))
    if status == "DRY_RUN":
        P("  DRY_RUN: the 2026 file is not the registered vintage. NO correlation of any kind between D and R was computed; the primary row's")
        P("  statistic cells (pearson_r, ci95_lo, ci95_hi, spearman_rho, verdict) and every descriptive correlation are blank. The first REGISTERED build's verdict is the result.")
    else:
        v = prim["verdict"]
        P("  VERDICT: %s" % v)
        if info["stats"]:
            P("  Pearson r (demeaned by calendar month) %s, 95%% moving-block bootstrap CI [%s, %s], Spearman rho %s, house band 1.96/sqrt(n) = %s." % (
                f(info["stats"]["r"], 3), f(info["stats"]["lo"], 3), f(info["stats"]["hi"], 3), f(info["stats"]["rho"], 3), f(prim["band_1p96_sqrt_n"], 3)))
            P("  " + verdict_sentence(v, info, prim, p))
        for r in ctx.prim_rows:
            if r["role"] == "descriptive":
                P("  descriptive: %-72s n = %3d  r = %s" % (r["label"][:72], r["n_months"], f(r["pearson_r"], 3) if r["pearson_r"] is not None else "n/a"))
    P("")
    P("8. CONTEXT, UNMATCHED")
    sw = inp.steo.get("T3_STCHANGE_WORLD", {})
    ms = [m for m in month_range("%d-01" % int(maxp[:4]), "%d-09" % int(maxp[:4])) if m in sw]
    if len(ms) == 9 and ms[-1] <= inp.last_hist:
        P("  STEO's world withdrawal %s..%s: %s mb, of which the residual line %s mb (a balancing item; no JODI quantity is set against the world figure)." % (
            ms[0], ms[-1], f(sum(sw[m] * days_in(m) for m in ms), 1), f(sum(inp.steo["T3_STCHANGE_NOECD"][m] * days_in(m) for m in ms), 1)))
    P("")
    P("9. CHECKS: %s" % ", ".join("%d %s" % (sum(1 for c in ctx.checks if c[4] == s), s) for s in ("PASS", "WARN", "FAIL", "INFO")))
    for c in ctx.checks:
        if c[4] in ("WARN", "FAIL"):
            P("  %s %s %s: expected %s; observed %s" % (c[4], c[0], c[1], c[2], c[3]))
    P("")
    P("WHAT THIS BUILD CANNOT SAY: a world stock level or change (China, Russia and most of the Gulf do not report stocks); anything about product stocks;")
    P("anything about prices (none enters); anything in real time (every series is a revised vintage). Not allowed under any verdict: 'world stocks',")
    P("'China's stocks', 'the residual is measured', any price or causal wording.")
    return L


# ------------------------------------------------------------------------------------------------------------------------
# reading the inputs from disk, and writing the outputs
# ------------------------------------------------------------------------------------------------------------------------
def load_inputs(cache, out_dir, say=print):
    inp = Inputs()
    inp.out_dir = out_dir
    inp.log_rows = read_table(log_path(out_dir), LOG_COLS)
    if not inp.log_rows:
        raise DataError("no fetch_log.csv in %s: run `fetch` first" % tilde(out_dir))
    sel = select_cache(cache, inp.log_rows)
    if not sel:
        raise DataError("no JODI file in the cache %s: run `fetch` first" % tilde(cache))
    inp.files = {}
    for y, (path, name, sha) in sorted(sel.items()):
        with open(path, "rb") as fh:
            inp.files[y] = parse_file(fh.read(), y, name, PRIMARY_DIR + name)
    read_release(out_dir)
    raw = os.path.join(out_dir, "raw")
    inp.psm = {}
    for sid in EIA_XLS_IDS:
        pth = os.path.join(raw, "eia_%sm.xls" % sid)
        if not os.path.exists(pth):
            raise DataError("missing %s: run `fetch` first" % tilde(pth))
        inp.psm[sid] = load_psm(pth, sid)
    inp.steo, inp.steo_meta = read_steo_extract(os.path.join(raw, "eia_steo_extract.csv"))
    inp.steo_xlsx = steo_xlsx_facts()
    if inp.steo_xlsx:
        inp.last_hist = inp.steo_xlsx[0]
    else:
        inp.last_hist = max(inp.steo["COPR_SA"])         # STEO's country series end at its last historical month (checked on 18 Oct 2026)
        say("WARN: eia_STEO_m.xlsx or openpyxl not available; STEO's last historical month taken from the end of COPR_SA: %s" % inp.last_hist)
    return inp


def pull_log_text(out_dir, log_rows):
    raw = os.path.join(out_dir, "raw")
    rows = [["path", "source_url", "fetched_utc", "sha256", "size_bytes"]]
    names = [("eia_%sm.xls" % s, "https://%s/dnav/pet/hist_xls/%sm.xls" % (EIA_HOST, s), "/dnav/pet/hist_xls/%sm.xls" % s) for s in EIA_XLS_IDS]
    names.append(("eia_steo_extract.csv", "https://%s%s" % (EIA_HOST, STEO_PATH), STEO_PATH))
    names.append((RELEASE_FILE, "https://%s%s" % (EIA_HOST, MANIFEST_PATH), MANIFEST_PATH))
    for fname, url, path in names:
        pth = os.path.join(raw, fname)
        got = [r for r in log_rows if r[1] == EIA_HOST and r[2] == path and r[5] == "saved"]
        when = max(got, key=lambda r: r[0])[0][:19] + "Z" if got else ""
        with open(pth, "rb") as fh:
            b = fh.read()
        rows.append(["data/jodi_oil/raw/" + fname, url, when, sha256_of(b), str(len(b))])
    return "\n".join("\t".join(r) for r in rows) + "\n"


def write_outputs(ctx, out_dir, inp):
    for name, text in sorted(ctx.texts.items()):
        write_text(os.path.join(out_dir, name), text)
    # the STEO extract carries the same three lines as every other output
    steo_rows = read_table(os.path.join(out_dir, "raw", "eia_steo_extract.csv"), STEO_COLS)
    text = render_table(STEO_COLS, steo_rows, ctx.ack)
    write_text(os.path.join(out_dir, "raw", "eia_steo_extract.csv"), text)
    write_text(os.path.join(out_dir, "raw", "pull_log.tsv"), pull_log_text(out_dir, inp.log_rows))


def build(cache, out_dir, panel_only=False, panel_sha=None, say=print, write=True, p=None):
    p = p or Params()
    inp = load_inputs(cache, out_dir, say)
    ctx = compute(inp, p, panel_sha=panel_sha, panel_only=panel_only, say=say)
    if panel_only:
        if write:
            write_text(os.path.join(out_dir, "panels.csv"), ctx.texts["panels.csv"])
        say("panels.csv sha256 %s" % ctx.panel_sha)
        return ctx
    say(ctx.texts["report.txt"].rstrip("\n"))
    say("")
    say("\n".join(ctx.terminal))
    if write:
        write_outputs(ctx, out_dir, inp)
        say("")
        say("wrote %s in %s" % (", ".join(sorted(list(ctx.texts) + ["raw/pull_log.tsv"])), tilde(out_dir)))
    say("panels.csv sha256 %s" % ctx.panel_sha)
    return ctx


# ------------------------------------------------------------------------------------------------------------------------
# selftest: synthetic rows (2030-2031), no JODI content, no network
# ------------------------------------------------------------------------------------------------------------------------
class Checks:
    def __init__(self):
        self.items = []

    def ok(self, name, cond, detail=""):
        self.items.append((name, bool(cond), "" if cond else detail))

    def eq(self, name, got, want):
        self.ok(name, got == want, "got %r, want %r" % (got, want))

    def near(self, name, got, want, tol=1e-9):
        self.ok(name, got is not None and want is not None and abs(got - want) <= tol, "got %r, want %r" % (got, want))

    def value(self, name, fn, want):
        """fn() must return `want`; an exception is recorded as a failure instead of ending the suite."""
        try:
            got = fn()
        except Exception as e:
            self.ok(name, False, "raised %s: %s" % (type(e).__name__, e))
        else:
            self.eq(name, got, want)

    def raises(self, name, exc, fn, contains=None):
        try:
            fn()
        except exc as e:
            self.ok(name, contains is None or contains in str(e), "raised %s without %r: %s" % (type(e).__name__, contains, e))
        except Exception as e:
            self.ok(name, False, "raised %s: %s" % (type(e).__name__, e))
        else:
            self.ok(name, False, "did not raise")

    def failed(self):
        return [(n, d) for n, c, d in self.items if not c]


FX_OECD = ("US", "DE", "GB", "JP")
FX_NON = ("SA", "NG", "KW", "AE", "QA", "OM", "AZ", "BR")
FX_M = month_range("2030-01", "2031-06")
FX_BASE_KBD = {"US": 13000, "DE": 40, "GB": 800, "JP": 5, "SA": 9500, "NG": 1500, "KW": 2500, "AE": 3000, "QA": 600, "OM": 1000, "AZ": 700, "BR": 3000}
FX_BASE_STOCK = {"US": 250000, "DE": 20000, "GB": 15000, "JP": 120000, "SA": 150000, "NG": 12000, "KW": 0, "AE": 30000, "QA": 8000, "OM": 20000,
                 "AZ": 6000, "BR": 5000}
FX_CODE = {"NG": 3, "QA": 3}
FX_SPR0 = 280000
FX_REVISION = {"NG": 400, "GB": 250}        # December 2030 as written in the 2030 file is stale by this many KBBL (the 2031 file revised it)


def fx_lcg(seed):
    x = [seed]

    def nxt(lo, hi):
        x[0] = (1103515245 * x[0] + 12345) % (2 ** 31)
        return lo + (x[0] >> 8) % (hi - lo + 1)
    return nxt


def fx_model(gb_gap=False, seam_missing=False):
    """The truth: for every area, production (KBBL per month), the closing stock as written (KBBL) and JODI's STOCKCH as written, plus the
    SPR path. These arrays are what the CSV text is made from; the tests recompute every published number from them with plain arithmetic."""
    nxt = fx_lcg(20301)
    mdl, spr = {}, {}
    k = 0
    for m in FX_M:
        spr[m] = FX_SPR0 + 300 * k
        k += 1
    spr_prev = FX_SPR0 - 300
    for a in FX_OECD + FX_NON:
        prod, lvl, chg = {}, {}, {}
        cur = FX_BASE_STOCK[a]
        for m in FX_M:
            prod[m] = round(FX_BASE_KBD[a] * days_in(m) * (1 + nxt(-20, 20) / 1000.0))
            s = 0 if a == "KW" else nxt(-max(500, FX_BASE_STOCK[a] // 30), max(500, FX_BASE_STOCK[a] // 30))
            cur += s
            if a == "US":
                lvl[m] = cur + spr[m]
                chg[m] = s + spr[m] - (spr[month_add(m, -1)] if m != FX_M[0] else spr_prev)
            else:
                lvl[m], chg[m] = cur, s
        mdl[a] = {"prod": prod, "lvl": lvl, "chg": chg}
    for a, rev in FX_REVISION.items():
        d = mdl[a]
        d["lvl"]["2030-12"] += rev                     # the stale December of the 2030 file
        d["chg"]["2030-12"] += rev                     # ... and its own STOCKCH, consistent inside that file
    mdl["spr"] = spr
    mdl["gb_gap"], mdl["seam_missing"] = gb_gap, seam_missing
    return mdl


def fx_status(a, m, flow, mdl):
    """'num' | 'dash' for a cell of the synthetic world; the special cases the spec's fixture needs."""
    if flow == "CLOSTLV" or flow == "STOCKCH":
        if a == "AZ" and m in ("2030-07",) + (("2030-08",) if flow == "STOCKCH" else ()):
            return "dash"
        if a == "JP" and m == "2030-03":
            return "dash"
        if a == "AE" and m == "2031-06":
            return "dash"
        if a == "GB" and mdl["gb_gap"] and m == "2030-05":
            return "dash"
        if flow == "STOCKCH" and mdl["seam_missing"] and a == "QA" and m == "2031-01":
            return "dash"
    if flow == "INDPROD" and a == "OM" and m == "2030-09":
        return "ktons"
    return "num"


def fx_code(a, m, flow):
    if flow == "INDPROD" and a == "DE" and m == "2030-03":
        return 2
    if flow == "INDPROD" and a == "SA" and m < "2030-04":
        return 3
    return FX_CODE.get(a, 1)


def fx_csv(year, mdl, drop_areas=(), extra_rows=(), code5=False, lm_header=True, no_crude=False):
    """One annual file in JODI's layout for the synthetic world. TOTCRUDE and NGL rows carry decoy numbers."""
    out = [JODI_HEADER]
    months = [m for m in FX_M if int(m[:4]) == year]
    for a in FX_OECD + FX_NON:
        if a in drop_areas:
            continue
        for m in months:
            dm = days_in(m)
            for flow in FLOWS:
                st = fx_status(a, m, flow, mdl)
                src = {"INDPROD": mdl[a]["prod"][m], "TOTIMPSB": mdl[a]["prod"][m] // 10, "TOTEXPSB": mdl[a]["prod"][m] // 3,
                       "CLOSTLV": mdl[a]["lvl"][m], "STOCKCH": mdl[a]["chg"][m]}[flow]
                code = fx_code(a, m, flow)
                for prod in (PRODUCT, "TOTCRUDE", "NGL"):
                    if no_crude and prod == PRODUCT:
                        continue
                    kb = src if prod == PRODUCT else src * 10 + 7
                    for u in UNITS:
                        if st == "num" or (st == "ktons" and u == "KTONS"):
                            kt = round(kb / 7.4)
                            if u == "KBBL":
                                v = "%.4f" % kb
                            elif u == "KBD":
                                v = ("%.4f" % (kb / dm)) if flow in RATE_FLOWS else "x"
                            elif u == "KL":
                                v = "%.4f" % (kb * KL_PER_KBBL)
                            elif u == "KTONS":
                                v = "%.4f" % kt
                            else:
                                v = ("%.4f" % (1000.0 * kb / kt)) if kt else ".."
                            if st == "ktons" and u != "KTONS":
                                v = "-" if u != "CONVBBL" else ".."
                            c = code if (v not in ("-", "x", "..")) else 3
                        else:
                            v = "x" if (u == "KBD" and flow not in RATE_FLOWS) else ("-" if u != "CONVBBL" else "..")
                            c = 3
                        if code5 and a == "US" and m == months[0] and flow == "INDPROD" and u == "KBBL" and prod == PRODUCT:
                            c = 5
                        out.append("%s,%s,%s,%s,%s,%s,%d" % (a, m, prod, flow, u, v, c))
    out.extend(extra_rows)
    return ("\n".join(out) + "\n").encode("utf-8")


FX_LM = {2030: "Mon, 05 Oct 2026 10:00:00 GMT", 2031: "Tue, 22 Sep 2026 07:18:47 GMT"}


def fx_steo(mdl, scale=1.0, unrelated=False):
    """Synthetic STEO series, 2029-12 to 2031-12. R (the 'other draws and balance' line) is built from the world's own draw plus a fixed
    deterministic wobble, so the relation is strong but not exact. T3_STCHANGE_WORLD and PAPR_WORLD are decoys with other magnitudes."""
    nxt = fx_lcg(777)
    months = month_range("2029-12", "2031-12")
    d = collections.defaultdict(dict)
    nonoecd = ("SA", "NG", "AE", "QA", "OM")
    for m in months:
        d["COPR_WORLD"][m] = 100.0 + 0.1 * months.index(m)
        d["PAPR_WORLD"][m] = d["COPR_WORLD"][m] + 6.0
        draw = None
        if m in FX_M and m != FX_M[0]:
            if m[5:7] == "01" and m != FX_M[0]:
                draw = -sum(mdl[a]["chg"][m] for a in nonoecd) / 1000.0
            else:
                draw = -sum(mdl[a]["lvl"][m] - mdl[a]["lvl"][month_add(m, -1)] for a in nonoecd) / 1000.0
        wob = nxt(-300, 300) / 100.0
        if unrelated:
            r_mb = nxt(-4000, 4000) / 100.0
        else:
            r_mb = (draw if draw is not None else 0.0) * scale + wob * 4
        d["T3_STCHANGE_NOECD"][m] = r_mb / days_in(m)
        d["T3_STCHANGE_WORLD"][m] = -3.0 * r_mb / days_in(m) + 0.5
        d["T3_STCHANGE_US"][m] = 0.01
        d["T3_STCHANGE_OOECD"][m] = 0.02
        d["PASC_OECD_T3"][m] = 2900.0 + 3.0 * months.index(m) + nxt(-200, 200) / 10.0
        d["PASC_US"][m] = 800.0
    for m in months:
        d["COPR_SA"][m] = 9.5
        d["COPR_NI"][m] = 1.3
        d["COPR_NG"][m] = 0.07                    # Niger (FIPS NG): a decoy for G16
        d["COPR_KU"][m] = 2.4
    return {k: dict(v) for k, v in d.items()}


def fx_psm(mdl):
    spr = {m: float(mdl["spr"][m]) for m in FX_M}
    spr[month_add(FX_M[0], -1)] = float(FX_SPR0 - 300)
    tot = {m: float(mdl["US"]["lvl"][m] + 100000) for m in FX_M}
    # December 2029 for the first change
    tot[month_add(FX_M[0], -1)] = tot[FX_M[0]] - mdl["US"]["chg"][FX_M[0]]
    return {"MCSSTUS1": spr, "MCRSTUS1": tot, "MCESTUS1": {m: tot[m] - spr[m] for m in tot},
            "MCRFPUS2": {m: float(mdl["US"]["prod"][m]) / days_in(m) + 120.0 for m in FX_M}}


def fx_log(files, lm):
    rows = []
    t0 = dt.datetime(2026, 10, 18, 9, 0, 0, tzinfo=dt.timezone.utc)
    for i, (y, (name, body)) in enumerate(sorted(files.items())):
        rows.append([(t0 + dt.timedelta(seconds=6 * i)).strftime("%Y-%m-%dT%H:%M:%S.000Z"), JODI_HOST, PRIMARY_DIR + name, "GET", "200", "saved",
                     str(len(body)), sha256_of(body), lm[y]])
    return rows


def fx_inputs(mdl=None, lm=None, drop_2031=("BR",), steo_kw=None, last_hist="2031-06", opts=None, code5=False):
    mdl = mdl or fx_model()
    bodies = {2030: ("2030.csv", fx_csv(2030, mdl)), 2031: ("primaryyear2031.csv", fx_csv(2031, mdl, drop_areas=drop_2031))}
    inp = Inputs()
    inp.files = {y: parse_file(b, y, n, PRIMARY_DIR + n) for y, (n, b) in bodies.items()}
    lmx = dict(FX_LM)
    if lm:
        lmx[2031] = lm
    inp.log_rows = fx_log(bodies, lmx)
    inp.steo = fx_steo(mdl, **(steo_kw or {}))
    inp.steo_meta = {}
    inp.last_hist = last_hist
    inp.psm = fx_psm(mdl)
    inp.steo_xlsx = None
    inp.out_dir = None
    inp.mdl = mdl
    return inp


def fx_params(**kw):
    base = dict(w0="2030-01", oecd=frozenset(FX_OECD), min_months=12, boot_b=200, reg_year=2031, reg_max="2031-05", event=("2030-04", "2030-05"),
                recent_year=2031, start_late="2030-03", steo_pins=False, ident_start="2030-01", spr_start="2030-02", ck_year_end="2030-12",
                ck_mid="2030-06", ck_stockch=("2030-10", "2030-11", "2030-12"))
    base.update(kw)
    return Params(**base)


# ------------------------------------------------------------------------------------------------------------------------
# reference calculations for the tests: plain arithmetic on the fixture's own arrays, written apart from the build's code paths
# ------------------------------------------------------------------------------------------------------------------------
FX_NONOECD_PANEL = ("AE", "NG", "OM", "QA", "SA")
FX_OECD_PANEL = ("DE", "GB", "US")
FX_PRODUCER_PANEL = ("AE", "AZ", "GB", "JP", "KW", "NG", "QA", "SA", "US")
FX_W = month_range("2030-01", "2031-04")


def ref_change(mdl, a, m, exspr=False):
    """The member's change in KBBL as the written files give it: January from STOCKCH in the new file, otherwise level differences."""
    if m[5:7] == "01":
        return mdl[a]["chg"][m] - ((mdl["spr"][m] - mdl["spr"][month_add(m, -1)]) if exspr and a == "US" else 0)
    pm = month_add(m, -1)
    lv = lambda mm: mdl[a]["lvl"][mm] - (mdl["spr"][mm] if exspr and a == "US" else 0)
    return lv(m) - lv(pm)


def ref_D(mdl, m, members=FX_NONOECD_PANEL):
    return -sum(ref_change(mdl, a, m) for a in members) / 1000.0


def ref_pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / (sxx * syy) ** 0.5


def fx_pair(n, seed=4242):
    """Two series of length n with a loose positive relation, for the bootstrap pins (independent numpy run, B = 10,000)."""
    nxt = fx_lcg(seed)
    x = [nxt(-1000, 1000) / 100.0 for _ in range(n)]
    y = [0.5 * a + nxt(-1000, 1000) / 100.0 for a in x]
    return x, y


def fx_known_r():
    x = [1, -1, 1, -1, 1, -1, 1, -1]
    z = [1, 1, -1, -1, 1, 1, -1, -1]
    return [float(v) for v in x], [0.6 * a + 0.8 * b for a, b in zip(x, z)]


def mk_inputs(**kw):
    return fx_inputs(**kw)


def run(inp, p, **kw):
    return compute(inp, p, **kw)


def rows_of(text, header=None):
    lines = [l for l in text.split("\n") if not l.startswith("#")]
    return list(csv.DictReader(io.StringIO("\n".join(lines), newline="")))


def agg(ctx, month, panel, flow):
    return next((r for r in ctx.agg_rows if r["month"] == month and r["panel"] == panel and r["flow"] == flow), None)


# ------------------------------------------------------------------------------------------------------------------------
# suite: pure functions and refusals
# ------------------------------------------------------------------------------------------------------------------------
def suite_pure(ck):
    at = chr(64)
    ck.eq("the User-Agent is the CLAUDE.md string and carries no address", (UA.startswith("Mozilla"), at in UA, UA.count("Derivative")), (True, False, 1))
    ck.raises("a User-Agent with an address is refused", Refused, lambda: assert_ua(UA.replace("research", "research x" + at + "y.org")))
    # helpers
    ck.eq("month_add / month_range", (month_add("2030-12", 1), month_add("2031-01", -1), month_range("2030-11", "2031-02")), ("2031-01", "2030-12", ["2030-11", "2030-12", "2031-01", "2031-02"]))
    ck.eq("days_in handles a leap year", (days_in("2032-02"), days_in("2031-02")), (29, 28))
    ck.eq("f() has no negative zero and no scientific notation", (f(-0.0004, 3), f(1234.5, 1), f(None, 3), f(1e-9, 3)), ("0.000", "1234.5", "", "0.000"))
    ck.eq("trim() keeps four decimals and drops trailing zeros", (trim(568729.0), trim(13817.3871), trim(-0.00001), trim(None)), ("568729", "13817.3871", "0", ""))
    ck.eq("http_date reads Last-Modified", iso_z(http_date("Tue, 22 Sep 2026 07:18:47 GMT")), "2026-09-22T07:18:47Z")
    ck.eq("parse_years reads ranges and lists", parse_years("2024,2026-2027", 2026), [2024, 2026, 2027])
    ck.raises("parse_years refuses a malformed year", Refused, lambda: parse_years("26", 2026))
    ck.eq("ranks give ties their mean rank", ranks([3.0, 1.0, 3.0, 2.0]), [3.5, 1.0, 3.5, 2.0])
    # G24: URL allowlist
    ok_urls = [(JODI_HOST, PAGE_PATH), (JODI_HOST, PRIMARY_DIR + "2015.csv"), (JODI_HOST, PRIMARY_DIR + "primaryyear2026.csv"), (EIA_HOST, "/dnav/pet/hist_xls/MCRSTUS1m.xls"), (EIA_HOST, STEO_PATH), (EIA_HOST, MANIFEST_PATH)]
    ck.ok("the allowlisted hosts and paths pass", all(check_url(h, pth) == (h, pth) for h, pth in ok_urls))
    bad = [("evil.example", PAGE_PATH, "GET"), (JODI_HOST, PAGE_PATH + "?a=1", "GET"), (JODI_HOST, PRIMARY_DIR.replace("/primary/", "/secondary/") + "2026.csv", "GET"),
           (EIA_HOST, "/dnav/pet/hist_xls/RBRTEd.xls", "GET"), (JODI_HOST, PAGE_PATH, "POST"), ("www.sec.gov", "/cgi-bin/browse-edgar", "GET")]
    for h, pth, mth in bad:
        ck.raises("refused: %s %s %s" % (mth, h, pth[-34:]), Refused, lambda h=h, pth=pth, mth=mth: check_url(h, pth, mth))
    ck.raises("a cache inside the repository is refused", Refused, lambda: check_cache(os.path.join(ROOT, "data", "cache")))
    ck.ok("a cache outside the repository is accepted", check_cache(tempfile.gettempdir()) != "")
    # body checks (G3)
    good = fx_csv(2030, fx_model())
    ck.eq("a JODI annual file with the exact header and CRUDEOIL rows passes the body check", jodi_csv_problem(good, PRIMARY_DIR + "2030.csv"), None)
    ck.ok("a secondary-file URL is a problem even if the header matches", jodi_csv_problem(good, "/_resources/files/downloads/oil-data/annual-csv/secondary/2030.csv") is not None)
    ck.ok("a file with the header but no CRUDEOIL rows is a problem", jodi_csv_problem(fx_csv(2030, fx_model(), no_crude=True), PRIMARY_DIR + "2030.csv") is not None)
    ck.ok("an HTML body is a problem", jodi_csv_problem(b"<html>blocked</html>", PRIMARY_DIR + "2030.csv") is not None)
    ck.raises("parse_file refuses a file with no CRUDEOIL rows", DataError, lambda: parse_file(fx_csv(2030, fx_model(), no_crude=True), 2030, "2030.csv"))
    # G5: assessment codes
    ck.raises("a numeric cell with assessment code 5 is a hard failure", DataError, lambda: parse_file(fx_csv(2030, fx_model(), code5=True), 2030, "2030.csv"), "code")
    # G4: unit relation
    def bent():
        rows = fx_csv(2030, fx_model()).decode().split("\n")
        i = next(k for k, r in enumerate(rows) if r.startswith("US,2030-01,CRUDEOIL,INDPROD,KBD,"))
        parts = rows[i].split(",")
        parts[5] = "%.4f" % (float(parts[5]) + 0.5)
        rows[i] = ",".join(parts)
        return "\n".join(rows).encode()
    ck.raises("KBD x days differing from KBBL by 0.5 is a hard failure", DataError, lambda: parse_file(bent(), 2030, "2030.csv"), "KBD")
    # output text guards
    ack = ack_lines("18 October 2026", "# vintage: JODI files 2030:2026-10-05:f18f4819cf36; max TIME_PERIOD 2031-06; preliminary months none.")
    hdr = ["month", "panel", "flow", "unit", "value", "n_members", "n_code1", "n_code3", "data_status", "suppression"]
    row = ["2030-01", "panel_producers", "INDPROD", "mb_per_day", "1.000", "3", "3", "0", "final", ""]
    ck.value("a well-formed table passes verify_text", lambda: len(verify_text("panel_aggregates.csv", render_table(hdr, [row], ack), ack)[1]), 1)
    ck.raises("an output without the JODI line is refused", DataError, lambda: verify_text("panel_aggregates.csv", render_table(hdr, [row], ack[1:] + ["# x"]), ack))
    ck.raises("a table with an extra column (ref_area) is refused", DataError, lambda: verify_text("panel_aggregates.csv", render_table(hdr + ["ref_area"], [row + ["US"]], ack), ack))
    ck.raises("a table with an extra column that is harmless in itself (n_extra) is refused by the allowlist", DataError, lambda: verify_text("panel_aggregates.csv", render_table(hdr + ["n_extra"], [row + ["1"]], ack), ack), "allowlist")
    ck.raises("a table whose columns are in another order is refused", DataError, lambda: verify_text("panel_aggregates.csv", render_table(hdr[1:] + hdr[:1], [row[1:] + row[:1]], ack), ack), "allowlist")
    saved = dict(ALLOW)
    try:
        ALLOW["t_country.csv"] = ["ref_area", "month", "value"]
        ck.raises("a country column beside a month column is refused outside checkpoints.csv", DataError, lambda: check_header_allowed("t_country.csv", ["ref_area", "month", "value"]), "country")
        for bad_col in ("price_usd", "brent", "p_value", "t_stat", "beta", "wti"):
            ALLOW["t_price.csv"] = ["month", bad_col]
            ck.raises("a header '%s' is refused (no price, no regression statistic)" % bad_col, DataError, lambda: check_header_allowed("t_price.csv", ["month", bad_col]))
    finally:
        ALLOW.clear()
        ALLOW.update(saved)
    cp = [["CK%02d" % i, "US", "2030-01", "CLOSTLV", "KBBL", "1", "1", "", "", "", "ok"] for i in range(MAX_CHECKPOINTS + 1)]
    ck.raises("more than 30 checkpoint rows are refused", DataError, lambda: verify_text("checkpoints.csv", render_table(CHECKPOINT_COLS, cp, ack), ack))
    ck.raises("a panel_aggregates row for reporters_all is refused (no world or reporter total)", DataError,
              lambda: verify_text("panel_aggregates.csv", render_table(hdr, [["2030-01", "reporters_all", "CLOSTLV", "mb", "9.000", "9", "9", "0", "final", ""]], ack), ack))
    ck.raises("a panel_aggregates row for world_stocks is refused", DataError,
              lambda: verify_text("panel_aggregates.csv", render_table(hdr, [["2030-01", "world_stocks", "CLOSTLV", "mb", "9.000", "9", "9", "0", "final", ""]], ack), ack))
    ck.raises("a coverage_counts row for a non-reporter group is refused", DataError,
              lambda: verify_text("coverage_counts.csv", render_table(COVERAGE_COLS, [["2030-01", "world", "CLOSTLV", "1", "1", "0", "0", "0", "0", "0", "1", "final"]], ack), ack))
    # disclosure (G15)
    d = {"A": ("CLOSTLV", [1, 2, 3, 4, 5]), "B": ("CLOSTLV", [1, 2, 3, 4, 5, 6]), "C": ("CLOSTLV", [1, 2, 3, 4, 5, 6, 7, 8]), "D": ("INDPROD", [1, 2, 3, 4, 5, 6])}
    ck.eq("nested panels differing by 1 or 2 areas: the larger is blanked (B over A, C over B and C over A at 3 is not blanked)", nested_suppression(d), {"B", "C"})
    ck.eq("nested panels differing by 3 are left alone", nested_suppression({"A": ("CLOSTLV", [1, 2, 3, 4]), "B": ("CLOSTLV", [1, 2, 3, 4, 5, 6, 7])}), set())
    pp = {n: {"members": m} for n, m in zip(PANEL_NAMES, ([1, 2, 3], [1, 2], [1, 2, 3, 4]))}
    ck.eq("a panel with two members is not published", publishable(pp), ["panel_producers", "panel_oecd_stocks_exspr"])
    # statistics (G22, G26, G29)
    x, y = fx_known_r()
    ck.near("Pearson r on a series with r = 0.6 exactly", pearson(x, y), 0.6, 0.01)
    ck.near("Spearman rho of a monotone pair is 1", spearman([1.0, 2.0, 3.0, 5.0], [2.0, 4.0, 6.0, 9.0]), 1.0, 1e-12)
    ck.eq("calendar-month demeaning removes each calendar month's mean", [round(v, 9) for v in demean_by_calendar_month(["2030-01", "2031-01", "2030-02", "2031-02"], [1.0, 3.0, 10.0, 20.0])], [-1.0, 1.0, -5.0, 5.0])
    ck.eq("verdict: SUPPORTS", verdict_for(0.4, 0.1, 0.6, 0.3), "SUPPORTS")
    ck.eq("verdict: SUPPORTS needs the episode condition, else episode-driven", verdict_for(0.4, 0.1, 0.6, 0.05), "SUPPORTS (episode-driven)")
    ck.eq("verdict: a missing episode r is not a pass", verdict_for(0.4, 0.1, 0.6, None), "SUPPORTS (episode-driven)")
    ck.eq("verdict: AGAINST", verdict_for(0.02, -0.2, 0.2, 0.0), "AGAINST")
    ck.eq("verdict: INCONCLUSIVE between", verdict_for(0.2, -0.1, 0.5, 0.2), "INCONCLUSIVE")
    ck.eq("verdict: the CI lower bound must be above zero", verdict_for(0.3, -0.01, 0.6, 0.3), "INCONCLUSIVE")
    ck.eq("verdict: run conditions failing is INCONCLUSIVE", verdict_for(0.9, 0.5, 0.95, 0.9, run_ok=False), "INCONCLUSIVE")
    pr_ = {"n_months": 120, "n_panel": 9, "panel_mean_level_mb": 260.0, "largest_member": "SA", "largest_member_var_share": 0.57}
    in_ = {"stats": {"r": 0.31, "lo": 0.12, "hi": 0.48}}
    pp_ = Params()
    s1 = verdict_sentence("SUPPORTS", in_, pr_, pp_)
    ck.ok("SUPPORTS wording: 'move with' the line, the panel, the mean level, the largest member's share, r and n",
          "move with EIA's 'other inventory draws and balance' line" in s1 and "a fixed panel of 9 countries, mean 260.0 mb, of which SA carries 57% of the change variance" in s1 and "r = 0.310" in s1 and "n = 120" in s1, s1)
    s2 = verdict_sentence("SUPPORTS (episode-driven)", in_, pr_, pp_)
    ck.ok("episode-driven wording never says 'move with the line' and names the episodes", "move with" not in s2 and "co-moved" in s2 and "2020-03..2020-12 and 2026, not outside them" in s2, s2)
    s3 = verdict_sentence("AGAINST", {"stats": {"r": 0.02, "lo": -0.2, "hi": 0.2}}, pr_, pp_)
    ck.ok("AGAINST wording says the line is not visible and that the residual is not thereby wrong", "not visible in reported non-OECD crude stocks" in s3 and "does not mean the residual is wrong" in s3, s3)
    ck.ok("no verdict sentence uses 'world stocks', 'China' or price or causal wording", not any(w in (s1 + s2 + s3).lower() for w in ("world stock", "china", "price", "cause", "because")))
    bx, by = fx_pair(55)
    # blindness (G25)
    _BLIND[0] = True
    try:
        ck.raises("pearson refuses to run during a DRY_RUN", Blind, lambda: pearson([1.0, 2.0, 3.0], [1.0, 3.0, 2.0]))
        ck.raises("spearman refuses to run during a DRY_RUN", Blind, lambda: spearman([1.0, 2.0, 3.0], [1.0, 3.0, 2.0]))
        ck.raises("the bootstrap refuses to run during a DRY_RUN", Blind, lambda: bootstrap_ci(bx, by, 10, 12, 1))
    finally:
        _BLIND[0] = False
    # STEO extract from a synthetic bulk zip
    def zip_with(series_ids, extra=""):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            lines = []
            for sid in series_ids:
                lines.append(json.dumps({"series_id": sid, "name": "n " + sid, "units": "u", "data": [["202612", 1.5], ["202001", None], ["201401", 9.0]]}))
            z.writestr("STEO.txt", "\n".join(lines) + "\n" + extra)
        return buf.getvalue()
    full = zip_with(["STEO.%s.M" % s for s in STEO_SERIES])
    rows = steo_extract_rows(full)
    ck.eq("the STEO extract keeps the used series within the month range", (len(rows), rows[0][3], rows[-1][3]), (len(STEO_SERIES) * 2, "2020-01", "2026-12"))
    ck.raises("a STEO zip missing a used series is refused", DataError, lambda: steo_extract_rows(zip_with(["STEO.COPR_WORLD.M"])))
    ck.eq("steo_zip_problem accepts a zip with STEO.txt", steo_zip_problem(full), None)
    ck.ok("steo_zip_problem refuses HTML", steo_zip_problem(b"<html>") is not None)


BOOT_PIN = (0.28168, 0.65635, 0.55099)           # independent numpy run on fx_pair(55): r, then the 95% CI for B = 10,000, L = 12, seed 20261020

# ------------------------------------------------------------------------------------------------------------------------
# suite: parsing the synthetic world
# ------------------------------------------------------------------------------------------------------------------------
def suite_parse(ck):
    inp = mk_inputs()
    w = World(inp.files)
    mdl = inp.mdl
    ck.eq("TOTCRUDE and NGL rows are not read as crude (US INDPROD 2030-01 is the crude figure)", w.cell("US", "2030-01", "INDPROD")[0], round(mdl["US"]["prod"]["2030-01"] / 31, 4))
    ck.eq("INDPROD is read in KBD", w.raw("US", "2030-01", "INDPROD", "KBD")[0], w.cell("US", "2030-01", "INDPROD")[0])
    ck.eq("CLOSTLV is read in KBBL, not KL", w.cell("US", "2030-02", "CLOSTLV")[0], float(mdl["US"]["lvl"]["2030-02"]))
    ck.eq("an absent area is not_reported, not zero", w.cell("BR", "2031-02", "CLOSTLV"), (None, None, "not_reported"))
    ck.eq("a dash is not_reported, not zero", w.cell("AZ", "2030-07", "CLOSTLV")[::2], (None, "not_reported"))
    ck.eq("'x' (KBD of a stock) is a marker, not zero", w.raw("US", "2030-01", "CLOSTLV", "KBD")[2], "x")
    ck.eq("a cell numeric only in KTONS is ktons_only and has no value", w.cell("OM", "2030-09", "INDPROD")[::2], (None, "ktons_only"))
    ck.eq("assessment code 2 is code2_excluded and keeps its value", w.cell("DE", "2030-03", "INDPROD")[1:], (2, "code2_excluded"))
    ck.eq("zero_reported areas in the 2030 file", sorted(w.zero_areas("2030-05")), ["KW"])
    ck.eq("a zero-reported area is not usable as a stock reporter", usable(w.cell("KW", "2030-05", "CLOSTLV"), "CLOSTLV", w.zero_areas("2030-05"), "KW"), False)
    ck.eq("...but a zero production is a value for INDPROD", usable(w.cell("KW", "2030-05", "INDPROD"), "INDPROD", w.zero_areas("2030-05"), "KW"), True)
    ck.eq("code 2 is not usable", usable(w.cell("DE", "2030-03", "INDPROD"), "INDPROD"), False)
    fs = {r["file"]: r for r in (file_stats_row(fd, inp.log_rows) for fd in inp.files.values())}
    ck.eq("file_stats carries Last-Modified and the max period of every file", (fs["2030.csv"]["last_modified"], fs["2030.csv"]["max_period"], fs["primaryyear2031.csv"]["max_period"]),
          ("2026-10-05T10:00:00Z", "2030-12", "2031-06"))
    ck.eq("file_stats counts the markers", (fs["2030.csv"]["n_x"] > 0, fs["2030.csv"]["n_dash"] > 0, fs["2030.csv"]["n_code4"]), (True, True, 0))
    # coverage counts
    p = fx_params()
    rows, sums = coverage_tables(w, ["2030-03", "2031-02"], p)
    by = {(r["month"], r["group"], r["flow"]): r for r in rows}
    allareas = FX_OECD + FX_NON
    codes = collections.Counter()
    for a in allareas:
        st, c = fx_status(a, "2030-03", "INDPROD", mdl), fx_code(a, "2030-03", "INDPROD")
        codes["code%d" % c if c != 2 else "code2_excluded"] += 1
    r = by[("2030-03", "reporters_all", "INDPROD")]
    ck.eq("coverage counts, 2030-03 INDPROD, all reporters: code1, code3, code2 excluded", (r["n_code1"], r["n_code3"], r["n_code2_excluded"]),
          (codes["code1"], codes["code3"], codes["code2_excluded"]))
    ck.eq("...and the counts add up to the areas in the file", r["n_reporters"] + r["n_code2_excluded"] + r["n_zero_reported"] + r["n_ktons_only"] + r["n_not_reported"], r["n_areas_in_file"])
    r = by[("2030-03", "reporters_all", "CLOSTLV")]
    ck.eq("a zero-reported stock area is counted as zero_reported, not as a reporter", (r["n_zero_reported"], r["n_reporters"]), (1, 12 - 1 - 1))
    r = by[("2031-02", "reporters_all", "INDPROD")]
    ck.eq("n_areas_in_file follows the file of the month (BR is absent from the 2031 file)", r["n_areas_in_file"], 11)
    ck.eq("oecd + nonoecd = all in every count", all(by[(m, "reporters_oecd", fl)][k] + by[(m, "reporters_nonoecd", fl)][k] == by[(m, "reporters_all", fl)][k]
                                                  for m in ("2030-03", "2031-02") for fl in ("INDPROD", "CLOSTLV") for k in ("n_reporters", "n_code1", "n_code3", "n_code2_excluded", "n_areas_in_file")), True)
    ck.eq("in-memory INDPROD sums: all-code sum exceeds the comparable sum by DE's code-2 cell in 2030-03",
          round((sums["2030-03"]["allc_kbd"] - sums["2030-03"]["comp_kbd"]) * 31, 3), round(float(mdl["DE"]["prod"]["2030-03"]), 3))
    ck.raises("a partition that does not add up is refused (a non-OECD set that drops an area)", DataError,
              lambda: coverage_tables(w, ["2030-03"], p, nonoecd=[a for a in FX_NON if a != "SA"]), "partition")
    # DRY_RUN blindness at the row level (a DRY_RUN must not write D)
    spr_ = inp.psm["MCSSTUS1"]
    pans = make_panels(w, month_range("2030-01", "2031-04"), spr_, p)
    arows, ser = aggregate_rows(w, pans, FX_M, "2031-04", spr_, p, blind=True)
    rrows, _dd = recon_rows(FX_M, "2031-04", ser, {}, inp.steo, "2031-06", pans, blind=True)
    ck.eq("blind rows: the non-OECD panel's level and change values are all blank", {r["value"] for r in arows if r["panel"] == "panel_nonoecd_stocks"}, {None})
    ck.eq("blind rows: the draw and residual-minus-draw columns are blank, STEO's line stays",
          ({r["jodi_panel_nonoecd_draw_mb"] for r in rrows}, {r["steo_residual_minus_panel_mb"] for r in rrows}, rrows[3]["steo_other_draws_balance_mb"] is not None), ({None}, {None}, True))
    arows2, ser2 = aggregate_rows(w, pans, FX_M, "2031-04", spr_, p, blind=False)
    ck.ok("unblind rows carry the values", any(r["value"] is not None for r in arows2 if r["panel"] == "panel_nonoecd_stocks"))
    # identities
    idr, mism = identity_rows(w, p, "2031-06")
    idm = {(r["check"], r["scope"], r["code_set"]): r for r in idr}
    want_n = sum(1 for a in allareas for m in month_range("2030-02", "2030-12") if fx_status(a, m, "CLOSTLV", mdl) == "num"
                 and fx_status(a, month_add(m, -1), "CLOSTLV", mdl) == "num" and fx_status(a, m, "STOCKCH", mdl) == "num")
    r = idm[("stock_identity", "2030", "all")]
    ck.eq("stock identity, 2030, all: n and pass (every written change equals the level difference)", (r["n"], r["n_pass"], r["n_exact"]), (want_n, want_n, want_n))
    ck.eq("seam rows: the revised Decembers (NG, GB) are the two mismatches", [m for y, m in mism if y == 2031], [["GB", "NG"]])
    sm = idm[("seam", "2030-12/2031-01", "all")]
    ck.eq("seam row 2030-12/2031-01: 11 country-boundaries (BR is absent from the 2031 file), 9 pass", (sm["n"], sm["n_pass"]), (11, 9))
    ck.eq("unit_kbd_kbbl row per file", sorted(r["scope"] for r in idr if r["check"] == "unit_kbd_kbbl"), ["2030", "2031"])
    # the cache: a file with no log row is refused (G6)
    with tempfile.TemporaryDirectory() as tmp:
        body = fx_csv(2030, mdl)
        name = "jodi_primary_2030_%s.csv" % sha256_of(body)[:12]
        open(os.path.join(tmp, name), "wb").write(body)
        ck.raises("a cached file with no fetch-log row of the same sha256 is refused", DataError, lambda: select_cache(tmp, []), "log")
        row = [["2026-10-18T09:00:00.000Z", JODI_HOST, PRIMARY_DIR + "2030.csv", "GET", "200", "saved", str(len(body)), sha256_of(body), FX_LM[2030]]]
        ck.eq("...and accepted when the log has the row", {y: v[1:] for y, v in select_cache(tmp, row).items()}, {2030: ("2030.csv", sha256_of(body))})
        os.rename(os.path.join(tmp, name), os.path.join(tmp, "jodi_primary_2030_000000000000.csv"))
        ck.raises("a file whose name does not carry its own sha256 is refused", DataError, lambda: select_cache(tmp, row), "sha256")


# ------------------------------------------------------------------------------------------------------------------------
# suite: builds on the synthetic world (DRY_RUN and REGISTERED)
# ------------------------------------------------------------------------------------------------------------------------
UTC = dt.timezone.utc


def suite_build_dry(ck):
    inp = mk_inputs()
    mdl = inp.mdl
    p = fx_params()
    ctx = run(inp, p)
    inpR = mk_inputs(lm="Thu, 22 Oct 2026 12:00:00 GMT")        # the same world as a registered build: here D and the panel levels are written
    ctxR = compute(inpR, p, panel_sha=compute(inpR, p, panel_only=True).panel_sha)
    rec = {r["month"]: r for r in ctxR.rec_rows}
    ck.eq("a Last-Modified before 21 Oct 2026 makes the build a DRY_RUN", ctx.status, "DRY_RUN")
    ck.eq("E is the max period less two months; the last two months are preliminary", (ctx.E, ctx.maxp, [m for m in rec if rec[m]["data_status"] == "preliminary"]),
          ("2031-04", "2031-06", ["2031-05", "2031-06"]))
    ck.eq("panel members follow the rule (non-OECD stocks, OECD stocks, producers)", [ctx.panels[n]["members"] for n in PANEL_NAMES],
          [list(FX_PRODUCER_PANEL), list(FX_NONOECD_PANEL), list(FX_OECD_PANEL)])
    # panel levels against plain arithmetic
    for m in ("2030-01", "2030-06", "2031-04"):
        dm = days_in(m)
        r1 = agg(ctxR, m, "panel_nonoecd_stocks", "CLOSTLV")
        ck.near("non-OECD stock panel level %s (mb, from KBBL)" % m, r1["value"], sum(mdl[a]["lvl"][m] for a in FX_NONOECD_PANEL) / 1000.0, 1e-9)
        r2 = agg(ctxR, m, "panel_oecd_stocks_exspr", "CLOSTLV")
        ck.near("OECD stock panel level %s: the US figure is less the SPR" % m, r2["value"], (sum(mdl[a]["lvl"][m] for a in FX_OECD_PANEL) - mdl["spr"][m]) / 1000.0, 1e-9)
        r3 = agg(ctxR, m, "panel_producers", "INDPROD")
        ck.near("producer panel %s (mb/d, from KBD)" % m, r3["value"], sum(mdl[a]["prod"][m] / dm for a in FX_PRODUCER_PANEL) / 1000.0, 1e-5)
    ck.eq("the code counts of a panel row add up to its members", [(r["n_code1"] + r["n_code3"], r["n_members"]) for r in ctxR.agg_rows if r["panel"] == "panel_nonoecd_stocks" and r["month"] == "2030-01" and r["flow"] == "CLOSTLV"],
          [(5, 5)])
    ck.eq("a preliminary month with a missing member has no panel sum (AE has no stock in 2031-06) and n_members shows it",
          (agg(ctxR, "2031-06", "panel_nonoecd_stocks", "CLOSTLV")["value"], agg(ctxR, "2031-06", "panel_nonoecd_stocks", "CLOSTLV")["n_members"]), (None, 4))
    # draw, sign and seam
    for m in month_range("2030-02", "2031-04"):
        ck.near("D (draw) %s: minus the change in closing stocks; January from STOCKCH" % m, rec[m]["jodi_panel_nonoecd_draw_mb"], ref_D(mdl, m), 1e-9)
    ck.eq("the first month has no change", rec["2030-01"]["jodi_panel_nonoecd_draw_mb"], None)
    ck.eq("the January seam is flagged resolved", (rec["2031-01"]["seam_flag"], rec["2030-06"]["seam_flag"]), ("seam_resolved", ""))
    ck.near("the OECD ex-SPR panel change 2030-08 is the level difference less the SPR change", rec["2030-08"]["jodi_panel_oecd_crude_exspr_change_mb"],
            sum(ref_change(mdl, a, "2030-08", True) for a in FX_OECD_PANEL) / 1000.0, 1e-9)
    ck.near("...and for January 2031 from STOCKCH less the SPR change", rec["2031-01"]["jodi_panel_oecd_crude_exspr_change_mb"],
            sum(ref_change(mdl, a, "2031-01", True) for a in FX_OECD_PANEL) / 1000.0, 1e-9)
    # STEO side
    ck.near("R is STEO's non-OECD line times days (not the world line)", rec["2030-03"]["steo_other_draws_balance_mb"], inp.steo["T3_STCHANGE_NOECD"]["2030-03"] * 31, 1e-9)
    ck.near("residual minus panel = R - D", rec["2030-03"]["steo_residual_minus_panel_mb"], rec["2030-03"]["steo_other_draws_balance_mb"] - ref_D(mdl, "2030-03"), 1e-9)
    prod_all = sum(mdl[a]["prod"]["2030-01"] / 31 for a in FX_OECD + FX_NON) / 1000.0
    ck.eq("coverage_reporters is against STEO's crude line (COPR_WORLD), rounded to 0.01", rec["2030-01"]["coverage_reporters"], round(prod_all / inp.steo["COPR_WORLD"]["2030-01"], 2))
    ck.near("STEO OECD commercial change", rec["2030-02"]["steo_oecd_commercial_change_mb"], inp.steo["PASC_OECD_T3"]["2030-02"] - inp.steo["PASC_OECD_T3"]["2030-01"], 1e-9)
    # dry run is blind
    pr = ctx.prim_rows
    ck.eq("DRY_RUN: the primary row's statistic cells are blank", [pr[0][k] for k in ("pearson_r", "ci95_lo", "ci95_hi", "spearman_rho", "verdict")], [None, None, None, None, ""])
    ck.eq("DRY_RUN: no descriptive correlation is filled", [r["pearson_r"] for r in pr[1:]], [None] * (len(pr) - 1))
    nn_rows = [r for r in ctx.agg_rows if r["panel"] == "panel_nonoecd_stocks"]
    ck.eq("DRY_RUN: the non-OECD panel's monthly level and change are withheld (blank, marked withheld_dry_run); the counts stay",
          ({r["value"] for r in nn_rows}, {r["suppression"] for r in nn_rows}, agg(ctx, "2030-01", "panel_nonoecd_stocks", "CLOSTLV")["n_members"]), ({None}, {"withheld_dry_run"}, 5))
    ck.ok("DRY_RUN: the other panels are still written (OECD, producers)", all(agg(ctx, "2030-03", n, fl)["value"] is not None for n, fl in (("panel_oecd_stocks_exspr", "CLOSTLV"), ("panel_producers", "INDPROD"))))
    ck.eq("DRY_RUN: D and residual-minus-D are blank in every month; STEO's own line R stays", ({r["jodi_panel_nonoecd_draw_mb"] for r in ctx.rec_rows}, {r["steo_residual_minus_panel_mb"] for r in ctx.rec_rows},
          rec["2030-03"]["steo_other_draws_balance_mb"] == {r["month"]: r for r in ctx.rec_rows}["2030-03"]["steo_other_draws_balance_mb"]), ({None}, {None}, True))
    toks = {f(v, 3) for m in month_range("2030-01", "2031-06") for v in (sum(mdl[a]["lvl"][m] for a in FX_NONOECD_PANEL) / 1000.0, ref_D(mdl, m) if m > "2030-01" else 0.0)}
    toks |= {f(-float(t), 3) for t in toks}
    toks = {t for t in toks if abs(float(t)) >= 1.0}
    ck.eq("DRY_RUN: scan of every written file finds no monthly level, change or draw of the non-OECD panel (%d candidate values)" % len(toks), d_leak_hits(ctx.texts, toks), [])
    ck.ok("...and the same scan does find them in the registered build (the scan can see them)", len(d_leak_hits(ctxR.texts, toks)) > 20)
    ck.eq("the scan finds a leaked value in a crafted table", d_leak_hits({"x.csv": "# c\nm,v\n2030-01,%s\n" % sorted(toks)[0]}, toks), [("x.csv", sorted(toks)[0])])
    ck.eq("DRY_RUN: the counts and the concentration are still given", (pr[0]["n_months"], pr[0]["n_panel"], pr[0]["largest_member"]), (15, 5, "SA"))
    csv_rows = rows_of(ctx.texts["primary_test.csv"])
    ck.eq("DRY_RUN: the written primary row has empty r, CI, rho and verdict cells", [csv_rows[0][k] for k in ("pearson_r", "ci95_lo", "ci95_hi", "spearman_rho", "verdict")], [""] * 5)
    ck.eq("exactly one primary row; every other row says descriptive and has no CI", ([r["role"] for r in pr].count("primary"), {r["verdict"] for r in pr[1:]}, {r["ci95_lo"] for r in pr[1:]}),
          (1, {"descriptive"}, {None}))
    ck.ok("the report says DRY_RUN and prints no correlation", "DRY_RUN" in ctx.texts["report.txt"] and "VERDICT" not in ctx.texts["report.txt"])
    pc = compute(inp, fx_params(now=dt.datetime(2026, 10, 25, tzinfo=UTC)))
    ck.eq("registration is read from the file, not the clock: a later clock does not register an old file", pc.status, "DRY_RUN")
    try:
        pc = compute(mk_inputs(lm="Thu, 22 Oct 2026 12:00:00 GMT"), fx_params(reg_max="2031-07"))
        ck.eq("a file modified after 21 Oct but ending before the registered month is still a DRY_RUN", pc.status, "DRY_RUN")
    except Exception as e:
        ck.ok("a file modified after 21 Oct but ending early is still a DRY_RUN", False, "%s: %s" % (type(e).__name__, e))
    # outputs: acknowledgement lines, allowlists, no reporter sums
    ack = ctx.ack
    ck.eq("every output begins with the three acknowledgement lines", all(t.split("\n")[:3] == list(ack) for t in ctx.texts.values()), True)
    ck.ok("the first line names JODI and the second names EIA", ack[0].startswith("# source: International Energy Forum (IEF). Joint Organizations Data Initiative (JODI) Database.")
          and "Accessed 18 October 2026" in ack[0] and ack[1].startswith("# source: U.S. Energy Information Administration (Oct 2026)"))
    ck.ok("the vintage line lists each file with its Last-Modified date and sha prefix, the max period and the preliminary months",
          "2030:2026-10-05:%s" % inp.files[2030].sha[:12] in ack[2] and "max TIME_PERIOD 2031-06" in ack[2] and "preliminary months 2031-05, 2031-06" in ack[2])
    sums = ctx.sums["2030-01"]
    needles = ["%.2f" % (sums["allc_kbd"] / 1000.0), "%.3f" % (sums["allc_kbd"] / 1000.0), "%.0f" % sums["allc_kbd"]]
    ck.ok("no reporter barrel sum is written to any output (the terminal block carries it)", not any(n in t for t in ctx.texts.values() for n in needles[:2]))
    ck.ok("the terminal block carries the reporter sum", any(needles[0] in ln for ln in ctx.terminal))
    # checkpoints
    cps = ctx.ckpt
    ck.ok("at most 30 checkpoint rows", len(cps) <= MAX_CHECKPOINTS, str(len(cps)))
    ng = next(r for r in cps if r["ref_area"] == "NG")
    ck.eq("Nigeria is compared with STEO's COPR_NI, not Niger's COPR_NG", ng["comparator_value"], "1300")
    ck.eq("Saudi Arabia and Kuwait comparators", [r["comparator_value"] for r in cps if r["ref_area"] in ("SA", "KW") and r["flow"] == "INDPROD"], ["9500", "9500", "9500", "2400"])
    ck.eq("the first US checkpoint is the level offset against MCRSTUS1", next(r for r in cps if r["ref_area"] == "US")["difference"], "100000")
    # coverage and zero-reported
    cc = {(r["month"], r["group"], r["flow"]): r for r in ctx.cov_rows}
    ck.eq("the zero-reported stock area (KW) is counted, not as a reporter", cc[("2030-06", "reporters_all", "CLOSTLV")]["n_zero_reported"], 1)
    # disclosure: a two-member OECD panel is not published
    ctx2 = compute(mk_inputs(mdl=fx_model(gb_gap=True)), p)
    ck.eq("with GB's stock missing one month the OECD panel has 2 members", ctx2.panels["panel_oecd_stocks_exspr"]["members"], ["DE", "US"])
    ck.eq("...and a panel of two is not published", [r for r in ctx2.agg_rows if r["panel"] == "panel_oecd_stocks_exspr"], [])
    ck.ok("...while the other panels are", any(r["panel"] == "panel_nonoecd_stocks" for r in ctx2.agg_rows))
    # frozen panel
    psha = ctx.panel_sha
    ck.raises("a different --panel-sha stops the build before the primary", Refused, lambda: compute(inp, p, panel_sha="0" * 64), "panel changed")
    ck.value("the matching --panel-sha is accepted", lambda: compute(inp, p, panel_sha=psha).status, "DRY_RUN")
    ck.eq("--panel-only returns only panels.csv", sorted(compute(inp, p, panel_only=True).texts), ["panels.csv"])
    ck.eq("panels.csv lists members with months_usable = months_in_window", {tuple(r[3:]) for r in panel_rows(ctx.panels, p, ctx.W)}, {(16, 16)})
    # forecast month
    ctx3 = compute(mk_inputs(last_hist="2031-05"), p)
    r6 = {r["month"]: r for r in ctx3.rec_rows}["2031-06"]
    ck.eq("a month after STEO's last historical month is flagged forecast and carries no ratio and no R", (r6["steo_basis"], r6["coverage_reporters"], r6["steo_other_draws_balance_mb"]), ("forecast", None, None))
    # SPR finding
    ck.eq("spr_included is yes when JODI's US STOCKCH tracks the EIA total", ctx.spr_res["included"], True)
    # decoy-free: world and PAPR are not used
    ck.ok("no output has a price, p-value or world-total column", all(not BANNED_HDR.search(h) for h in ALLOW_FLAT()))


def ALLOW_FLAT():
    return [h.lower() for cols in ALLOW.values() for h in cols]


def suite_build_reg(ck):
    inp = mk_inputs(lm="Thu, 22 Oct 2026 12:00:00 GMT")
    mdl = inp.mdl
    p = fx_params()
    psha = compute(inp, p, panel_only=True).panel_sha
    ck.raises("a REGISTERED build without --panel-sha is refused", Refused, lambda: compute(inp, p), "--panel-sha")
    ck.raises("a REGISTERED build with a different panel hash is refused", Refused, lambda: compute(inp, p, panel_sha="1" * 64), "panel changed")
    ctx = compute(inp, p, panel_sha=psha)
    pr = ctx.prim_rows
    prim = pr[0]
    ck.eq("a file modified on or after 21 Oct 2026 with data to the registered month makes the build REGISTERED", ctx.status, "REGISTERED")
    ck.eq("the primary sample: months, window, panel", (prim["n_months"], prim["window_first"], prim["window_last"], prim["n_panel"]), (15, "2030-02", "2031-04", 5))
    ck.near("primary Pearson r on the calendar-month-demeaned series (independent numpy run)", prim["pearson_r"], 0.68016, 5e-5)
    ck.near("bootstrap CI lower bound", prim["ci95_lo"], 0.56523, 5e-5)
    ck.near("bootstrap CI upper bound", prim["ci95_hi"], 0.79072, 5e-5)
    ck.near("Spearman rho on the demeaned series", prim["spearman_rho"], 0.42727, 5e-5)
    ck.near("house band 1.96/sqrt(n)", prim["band_1p96_sqrt_n"], 1.96 / 15 ** 0.5, 1e-12)
    ck.eq("the largest member of the change variance is SA", prim["largest_member"], "SA")
    ck.near("...with its share Cov(d_i, D)/Var(D)", prim["largest_member_var_share"], 0.88722, 5e-5)
    ck.near("the panel's mean level over W", prim["panel_mean_level_mb"], sum(sum(mdl[a]["lvl"][m] for a in FX_NONOECD_PANEL) / 1000.0 for m in FX_W) / len(FX_W), 1e-9)
    ck.eq("the verdict follows section 4 (r high, CI above zero, the episode-free r undefined: episode-driven)", prim["verdict"], "SUPPORTS (episode-driven)")
    ck.eq("exactly one primary row; the others say descriptive and carry no CI", ([r["role"] for r in pr].count("primary"), {r["verdict"] for r in pr[1:]}, {r["ci95_lo"] for r in pr[1:]}), (1, {"descriptive"}, {None}))
    d = {r["label"]: r for r in pr[1:]}
    ck.near("descriptive: raw (not demeaned) r", d["raw (not demeaned)"]["pearson_r"], 0.25943, 5e-5)
    ck.near("descriptive: excluding the event months", d["excluding 2030-04..2030-05"]["pearson_r"], 0.22931, 5e-5)
    ck.eq("descriptive: excluding 2031 leaves single calendar months (zero variance after demeaning): blank", (d["excluding 2031"]["n_months"], d["excluding 2031"]["pearson_r"]), (11, None))
    ck.eq("descriptive: excluding both", (d["excluding 2030-04..2030-05 and 2031"]["n_months"], d["excluding 2030-04..2030-05 and 2031"]["pearson_r"]), (9, None))
    ck.near("descriptive: starting 2030-03", d["starting 2030-03"]["pearson_r"], 0.76651, 5e-5)
    ck.near("descriptive: panel restricted to code-1 cells (SA, AE, OM)", d["panel restricted to code-1 cells (3 of 5 members)"]["pearson_r"], 0.70322, 5e-5)
    ck.near("descriptive: OECD ex-SPR panel against STEO's OECD commercial change (shared source)", d["OECD ex-SPR panel vs STEO OECD commercial change (shared source: IEA data feed both)"]["pearson_r"], -0.30918, 5e-5)
    csv_rows = rows_of(ctx.texts["primary_test.csv"])
    ck.eq("the written primary row has 3-decimal statistics", [csv_rows[0][k] for k in ("pearson_r", "ci95_lo", "ci95_hi", "spearman_rho")], ["0.680", "0.565", "0.791", "0.427"])
    rep = ctx.texts["report.txt"]
    ck.ok("the report prints the verdict sentence with n, N, the mean level and the largest member's share", "co-moved" in rep and "n = 15" in rep and "SA carries 89%" in rep and "not outside them" in rep)
    # the January seam with one member's STOCKCH missing: the month is excluded and counted
    inp2 = mk_inputs(mdl=fx_model(seam_missing=True), lm="Thu, 22 Oct 2026 12:00:00 GMT")
    psha2 = compute(inp2, p, panel_only=True).panel_sha
    c2 = compute(inp2, p, panel_sha=psha2)
    rr = {r["month"]: r for r in c2.rec_rows}["2031-01"]
    ck.eq("a January whose STOCKCH is missing for a member is seam_unresolved, blank, excluded and counted",
          (rr["seam_flag"], rr["jodi_panel_nonoecd_draw_mb"], c2.prim_rows[0]["n_months"], c2.prim_rows[0]["n_seam_excluded"]), ("seam_unresolved", None, 14, 1))
    # run conditions
    c3 = compute(inp, fx_params(min_months=40), panel_sha=psha)
    ck.eq("too few months: the run does not happen and the verdict is INCONCLUSIVE", (c3.prim_rows[0]["verdict"], c3.prim_rows[0]["pearson_r"], c3.pinfo["run_reasons"]), ("INCONCLUSIVE", None, ["too_few_months"]))
    c4 = compute(inp, fx_params(min_panel=6), panel_sha=psha)
    ck.eq("a panel under the minimum size: INCONCLUSIVE (panel_too_thin)", (c4.prim_rows[0]["verdict"], c4.pinfo["run_reasons"]), ("INCONCLUSIVE", ["panel_too_thin"]))
    # a different STEO relation changes the statistic (the code path is live)
    c5 = compute(mk_inputs(lm="Thu, 22 Oct 2026 12:00:00 GMT", steo_kw={"unrelated": True}), p, panel_sha=psha)
    ck.ok("an unrelated R gives a different r", c5.prim_rows[0]["pearson_r"] is not None and abs(c5.prim_rows[0]["pearson_r"] - prim["pearson_r"]) > 0.05)


# ------------------------------------------------------------------------------------------------------------------------
# suite: fetching without a network
# ------------------------------------------------------------------------------------------------------------------------
class FakeClock:
    def __init__(self, t0):
        self.t = t0
        self.slept = []

    def time(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


FX_NOW = dt.datetime(2026, 10, 18, 9, 0, 0, tzinfo=UTC)
SPACING_OK = MIN_SLEEP - 1e-6


def fx_page():
    return (b"<html><body><a href='/_resources/files/downloads/oil-data/annual-csv/primary/2030.csv'>2030</a>"
            b"<a href='/_resources/files/downloads/oil-data/annual-csv/primary/primaryyear2031.csv'>2031</a>"
            b"<a href='/_resources/files/downloads/oil-data/annual-csv/secondary/2030.csv'>sec</a></body></html>")


def fx_zip():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("STEO.txt", "\n".join(json.dumps({"series_id": "STEO.%s.M" % s, "name": s, "units": "u", "data": [["203001", 1.0]]}) for s in STEO_SERIES) + "\n")
    return buf.getvalue()


def suite_fetch(ck):
    mdl = fx_model()
    csvs = {PRIMARY_DIR + "2030.csv": fx_csv(2030, mdl), PRIMARY_DIR + "primaryyear2031.csv": fx_csv(2031, mdl)}
    good_xls = XLS_MAGIC + b"\xa1\xb1\x1a\xe1" + b"x" * 64
    good_zip = fx_zip()
    good_manifest = json.dumps({"STEO": {"last_updated": "2026-10-06T16:02:16-04:00", "accessURL": "x"}, "AEO": {"last_updated": "2025-01-01T00:00:00-04:00"}}).encode()
    lm = "Tue, 22 Sep 2026 07:18:47 GMT"

    def ok_script(method, host, path):
        if path == PAGE_PATH:
            return 200, fx_page(), {}
        if path in csvs:
            b = csvs[path]
            return 200, (b if method == "GET" else b""), {"last-modified": lm, "content-length": str(len(b))}
        if path == STEO_PATH:
            return 200, good_zip, {"last-modified": lm}
        if path == MANIFEST_PATH:
            return 200, good_manifest, {"last-modified": lm}
        return 200, good_xls, {}

    def rig(tmp, script=ok_script, max_requests=MAX_REQUESTS, sleep=MIN_SLEEP, clock=None, cache="cache", eia_loader=None, steo_loader=None):
        clock = clock or FakeClock(FX_NOW.timestamp())
        calls = []

        def opener(method, host, target, headers, timeout, cap):
            calls.append((method, host, target, dict(headers), clock.time()))
            res = script(method, host, target) if callable(script) else script
            if isinstance(res, Exception):
                raise res
            return res
        fe = Fetcher(os.path.join(tmp, cache), os.path.join(tmp, "out"), sleep=sleep, max_requests=max_requests, opener=opener, wall=clock.time, mono=clock.time,
                     sleeper=clock.sleep, stop_path=os.path.join(tmp, "STOP"), now_utc=lambda: dt.datetime.fromtimestamp(clock.time(), UTC), pid_alive=lambda p_: False,
                     eia_loader=eia_loader or (lambda path, sid: {}), steo_loader=steo_loader or (lambda b: []))
        return fe, calls, clock

    def case(label, script, action, expect_stop, expect_exc=None, **kw):
        with tempfile.TemporaryDirectory() as tmp:
            fe, calls, clock = rig(tmp, script, **kw)
            exc = None
            try:
                with fe:
                    action(fe)
            except Exception as e:
                exc = e
            stop = os.path.exists(os.path.join(tmp, "STOP"))
            ck.eq("%s: STOP latch %s" % (label, "written" if expect_stop else "not written"), stop, expect_stop)
            if expect_exc is not None:
                ck.ok("%s: raises %s" % (label, expect_exc.__name__), isinstance(exc, expect_exc), "got %r" % (exc,))
            else:
                ck.ok("%s: no exception" % label, exc is None, "got %r" % (exc,))
            ck.ok("%s: lock removed in finally" % label, not os.path.exists(os.path.join(tmp, ".fetch.lock")))
            return calls

    # a good run: paced, logged, cached with the sha in the name
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = rig(tmp)
        with fe:
            outs = [fe.fetch_page(), fe.fetch_year(2030), fe.fetch_year(2031)] + [fe.fetch_eia_xls(s) for s in EIA_XLS_IDS] + [fe.fetch_steo(), fe.fetch_manifest()]
        ck.eq("a good run saves everything", [o.split(" ")[0] for o in outs], ["saved"] * 9)
        starts = [c[4] for c in calls]
        ck.ok("consecutive request starts are at least 5.05 s apart", len(starts) == 9 and all(b - a >= SPACING_OK for a, b in zip(starts, starts[1:])), str(starts))
        ck.ok("headers are exactly User-Agent and Accept-Encoding, the canonical agent", all(sorted(c[3]) == ["Accept-Encoding", "User-Agent"] and c[3]["User-Agent"] == UA for c in calls))
        ck.eq("requests went to www.jodidata.org and www.eia.gov only, GET only", ({c[1] for c in calls}, {c[0] for c in calls}), ({JODI_HOST, EIA_HOST}, {"GET"}))
        ck.eq("request targets are the allowlisted paths", [c[2] for c in calls], [PAGE_PATH, PRIMARY_DIR + "2030.csv", PRIMARY_DIR + "primaryyear2031.csv"] + ["/dnav/pet/hist_xls/%sm.xls" % s for s in EIA_XLS_IDS] + [STEO_PATH, MANIFEST_PATH])
        log = read_table(os.path.join(tmp, "out", "fetch_log.csv"), LOG_COLS)
        ck.eq("the log has one row per request with method, status, bytes, sha256 and Last-Modified", [(r[3], r[4], r[5]) for r in log], [("GET", "200", "saved")] * 9)
        b30 = csvs[PRIMARY_DIR + "2030.csv"]
        ck.eq("...the JODI row carries the bytes, sha256 and the Last-Modified header", log[1][6:], [str(len(b30)), sha256_of(b30), lm])
        ck.ok("the JODI file is cached as jodi_primary_<year>_<sha12>.csv", os.path.exists(os.path.join(tmp, "cache", "jodi_primary_2030_%s.csv" % sha256_of(b30)[:12])))
        ck.ok("the EIA workbook landed under <out>/raw/, no .part is left", os.path.exists(os.path.join(tmp, "out", "raw", "eia_MCRSTUS1m.xls")) and not any(n.endswith(".part") for n in os.listdir(os.path.join(tmp, "out", "raw"))))
        ck.ok("the STEO zip stays in the cache and the extract goes to <out>/raw/", any(n.startswith("eia_STEO_") for n in os.listdir(os.path.join(tmp, "cache"))) and os.path.exists(os.path.join(tmp, "out", "raw", "eia_steo_extract.csv")))
        ck.eq("the manifest's STEO entry dates the release in raw/eia_steo_release.txt", read_release(os.path.join(tmp, "out")), dt.date(2026, 10, 6))
        ck.ok("the manifest body is cached", any(n.startswith("eia_manifest_") for n in os.listdir(os.path.join(tmp, "cache"))))
        ck.eq("the fetch log begins with the three acknowledgement lines", open(os.path.join(tmp, "out", "fetch_log.csv"), encoding="utf-8").read().split("\n")[0][:60], SRC_JODI[:60])
        # a later run the same day: nothing is requested again; a past-year file is cached
        fe2, calls2, _ = rig(tmp, clock=clock)
        with fe2:
            fe2.fetch_page()
            ck.eq("a past-year file already cached is not requested again", (fe2.fetch_year(2030), len(calls2)), ("cached", 1))
            ck.eq("the current-year file fetched today is not requested again", (fe2.fetch_year(2031), len(calls2)), ("cached_today", 1))
            ck.eq("a named year is requested even if cached, unless fetched today", fe2.fetch_year(2030, explicit=True), "cached_today")
            ck.eq("the EIA files fetched today are not requested again", (fe2.fetch_eia_xls("MCRSTUS1"), fe2.fetch_steo(), fe2.fetch_manifest(), len(calls2)), ("cached_today", "cached_today", "cached_today", 1))
        ck.ok("the 5.05 s spacing persists across invocations", calls2[0][4] - starts[-1] >= SPACING_OK, "%s %s" % (calls2[0][4], starts[-1]))
        # a new vintage a day later is kept beside the old one
        later = FakeClock(clock.time() + 86400)
        new_body = csvs[PRIMARY_DIR + "primaryyear2031.csv"] + b"extra,row\n"
        csvs[PRIMARY_DIR + "primaryyear2031.csv"] = new_body
        fe3, calls3, _ = rig(tmp, clock=later)
        with fe3:
            fe3.fetch_page()
            r = fe3.fetch_year(2031)
        csvs[PRIMARY_DIR + "primaryyear2031.csv"] = fx_csv(2031, mdl)
        ck.eq("a changed current-year file is saved as a new vintage beside the old one", (r, len(fe3.cached_for_year(2031))), ("saved", 2))
        # check-vintage
        fe4, calls4, _ = rig(tmp, clock=FakeClock(later.time() + 100))
        with fe4:
            fe4.fetch_page()
            word1, _d = fe4.check_year(2030)
            word2, _d2 = fe4.check_year(2031)
        ck.eq("check-vintage uses HEAD only and reports same / DIFFERS", ([c[0] for c in calls4], word1, word2), (["GET", "HEAD", "HEAD"], "same", "DIFFERS"))
    # refusals latch
    for status in (301, 302, 401, 403, 404, 407, 429, 451, 500, 503):
        case("JODI HTTP %d" % status, (lambda s: lambda m, h, t: (s, b"", {}))(status), lambda fe: (fe.fetch_page(), fe.fetch_year(2030)), True, Latched)
    case("EIA HTTP 403", lambda m, h, t: (403, b"", {}), lambda fe: fe.fetch_eia_xls("MCRSTUS1"), True, Latched)
    case("STEO HTTP 404", lambda m, h, t: (404, b"", {}), lambda fe: fe.fetch_steo(), True, Latched)
    case("manifest 200 without a STEO entry", lambda m, h, t: (200, b'{"AEO": {"last_updated": "x"}}', {}), lambda fe: fe.fetch_manifest(), True, Latched)
    case("manifest HTTP 301", lambda m, h, t: (301, b"", {}), lambda fe: fe.fetch_manifest(), True, Latched)
    case("downloads page 200 without the primary links", lambda m, h, t: (200, b"<html>no links</html>", {}), lambda fe: fe.fetch_page(), True, Latched)

    def page_then(body):
        return lambda m, h, t: (200, fx_page(), {}) if t == PAGE_PATH else (200, body, {})
    case("JODI 200 with an HTML body", page_then(b"<html>blocked</html>"), lambda fe: (fe.fetch_page(), fe.fetch_year(2030)), True, Latched)
    case("JODI 200 with a CSV that has the wrong first line", page_then(b"a,b,c\n1,2,3\n"), lambda fe: (fe.fetch_page(), fe.fetch_year(2030)), True, Latched)
    case("JODI 200 with the header but no CRUDEOIL rows", page_then(fx_csv(2030, mdl, no_crude=True)), lambda fe: (fe.fetch_page(), fe.fetch_year(2030)), True, Latched)
    case("JODI 200 with a body over the cap", page_then(None), lambda fe: (fe.fetch_page(), fe.fetch_year(2030)), True, Latched)
    case("EIA 200 with a body that is not an XLS", lambda m, h, t: (200, b"<html>login</html>", {}), lambda fe: fe.fetch_eia_xls("MCSSTUS1"), True, Latched)
    case("STEO 200 with a zip that has no STEO.txt", lambda m, h, t: (200, ZIP_MAGIC + b"junk", {}), lambda fe: fe.fetch_steo(), True, Latched)
    case("a socket fault ends the invocation", lambda m, h, t: SocketFault("timeout"), lambda fe: (fe.fetch_page(), fe.fetch_page()), False, SocketFault)
    calls = case("a good page fetch", ok_script, lambda fe: fe.fetch_page(), False)
    ck.eq("...sends exactly one request", len(calls), 1)

    def bad_loader(path, sid):
        raise DataError("not a workbook")
    with tempfile.TemporaryDirectory() as tmp:
        raw_dir = os.path.join(tmp, "out", "raw")
        os.makedirs(raw_dir)
        open(os.path.join(raw_dir, "eia_MCRSTUS1m.xls"), "wb").write(b"previous good file")
        fe, calls, clock = rig(tmp, eia_loader=bad_loader)
        raised = None
        try:
            with fe:
                fe.fetch_eia_xls("MCRSTUS1")
        except Latched as e:
            raised = e
        ck.ok("EIA 200 with the XLS magic bytes but no loadable workbook: STOP written", raised is not None and os.path.exists(os.path.join(tmp, "STOP")), "got %r" % (raised,))
        ck.ok("...the file already saved is untouched and no .part is left", open(os.path.join(raw_dir, "eia_MCRSTUS1m.xls"), "rb").read() == b"previous good file"
              and not os.path.exists(os.path.join(raw_dir, "eia_MCRSTUS1m.xls.part")))
    # the socket fault is logged; the cap; refusals at construction
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = rig(tmp, lambda m, h, t: SocketFault("reset"))
        try:
            with fe:
                fe.fetch_page()
        except SocketFault:
            pass
        ck.eq("a socket fault is logged", [r[5] for r in read_table(os.path.join(tmp, "out", "fetch_log.csv"), LOG_COLS)], ["socket_fault:reset"])
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = rig(tmp, max_requests=20)
        raised = None
        with fe:
            for _ in range(20):
                fe._request("HEAD", JODI_HOST, PAGE_PATH)
            try:
                fe._request("HEAD", JODI_HOST, PAGE_PATH)
            except MaxRequests as e:
                raised = e
        ck.ok("the 21st request in one run is refused", raised is not None and len(calls) == 20, "%d calls" % len(calls))
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = rig(tmp)
        with fe:
            ck.raises("a host outside the allowlist is refused before any request", Refused, lambda: fe._request("GET", "www.sec.gov", "/cgi-bin/browse-edgar"))
            ck.raises("POST is not a verb this script has", Refused, lambda: fe._request("POST", JODI_HOST, PAGE_PATH))
        ck.eq("...and sent nothing", len(calls), 0)
    # STOP latch refuses later runs; the lock stops a second fetcher
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = rig(tmp, lambda m, h, t: (403, b"", {}))
        try:
            with fe:
                fe.fetch_page()
        except Latched:
            pass
        f2, calls2, _ = rig(tmp)
        ck.raises("a later fetch refuses to run while STOP exists", Latched, lambda: f2.__enter__())
        ck.eq("...and sends no request", len(calls2), 0)
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = rig(tmp)
        fe.pid_alive = lambda p_: True
        with fe:
            f2, _, _ = rig(tmp)
            f2.pid_alive = lambda p_: True
            ck.raises("a live lock stops a second fetcher", Refused, lambda: f2.__enter__())
        f3, _, _ = rig(tmp)
        with f3:
            ck.ok("the lock is free again after the first fetcher leaves", True)
    ck.raises("--sleep below 5.05 is refused", Refused, lambda: Fetcher(os.path.join(tempfile.gettempdir(), "x_never_used"), "/tmp/y", sleep=5.0))
    ck.value("--sleep 5.05 is accepted", lambda: Fetcher(os.path.join(tempfile.gettempdir(), "x_never_used"), "/tmp/y", sleep=5.05).sleep, 5.05)
    ck.raises("--max-requests above 20 is refused", Refused, lambda: Fetcher(os.path.join(tempfile.gettempdir(), "x_never_used"), "/tmp/y", max_requests=21))
    ck.raises("a cache inside the repository is refused by the fetcher", Refused, lambda: Fetcher(os.path.join(ROOT, "data", "cache"), "/tmp/y"))
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = rig(tmp, sleep=MIN_SLEEP)
        with fe:
            fe._request("HEAD", JODI_HOST, PAGE_PATH)
        fe2, calls2, _ = rig(tmp, clock=clock, cache="other_cache")
        with fe2:
            fe2._request("HEAD", JODI_HOST, PAGE_PATH)
        ck.ok("two runs with different --cache values are paced against each other", calls2[0][4] - calls[0][4] >= SPACING_OK)
        ck.ok("the pacing record and the lock sit beside STOP, not in the cache", os.path.exists(os.path.join(tmp, ".last_request")) and not os.path.exists(os.path.join(tmp, "cache", ".last_request")))
    # the real opener: no redirect followed, HEAD has no body, a body over the cap is None, a socket error is a SocketFault
    class FakeResp:
        def __init__(self, status, body):
            self.status, self._b = status, body

        def getheaders(self):
            return [("Last-Modified", lm), ("Content-Length", str(len(self._b)))]

        def read(self, n=-1):
            out, self._b = self._b[:n], self._b[n:]
            return out

    class FakeConn:
        seen = []
        status, body, boom = 200, b"abc", False

        def __init__(self, host, timeout=None):
            pass

        def request(self, method, target, headers=None):
            FakeConn.seen.append((method, target, dict(headers or {})))
            if FakeConn.boom:
                raise OSError("reset")

        def getresponse(self):
            return FakeResp(FakeConn.status, FakeConn.body)

        def close(self):
            pass
    real = http.client.HTTPSConnection
    http.client.HTTPSConnection = FakeConn
    try:
        FakeConn.status, FakeConn.body, FakeConn.boom = 200, b"abc", False
        ck.eq("real_opener GET returns the body and lower-cased headers", (real_opener("GET", JODI_HOST, PAGE_PATH, HEADERS, 5, 100)[:2], real_opener("GET", JODI_HOST, PAGE_PATH, HEADERS, 5, 100)[2]["last-modified"]), ((200, b"abc"), lm))
        ck.eq("real_opener HEAD returns no body", real_opener("HEAD", JODI_HOST, PAGE_PATH, HEADERS, 5, 100)[:2], (200, b""))
        ck.eq("real_opener returns None for a body over the cap", real_opener("GET", JODI_HOST, PAGE_PATH, HEADERS, 5, 2)[1], None)
        FakeConn.status = 301
        ck.eq("real_opener does not follow a redirect: the 301 comes back as a status", real_opener("GET", JODI_HOST, PAGE_PATH, HEADERS, 5, 100)[:2], (301, b""))
        FakeConn.boom = True
        ck.raises("real_opener turns a socket error into SocketFault", SocketFault, lambda: real_opener("GET", JODI_HOST, PAGE_PATH, HEADERS, 5, 100))
        ck.eq("...and only GET or HEAD were ever sent", {s[0] for s in FakeConn.seen}, {"GET", "HEAD"})
    finally:
        http.client.HTTPSConnection = real

    # the command line: fetch --all, fetch (default), fetch --years, check-vintage; each request count
    def cli(argv, today=dt.date(2031, 6, 1)):
        with tempfile.TemporaryDirectory() as tmp:
            clock = FakeClock(FX_NOW.timestamp())
            seen = []

            def opener(method, host, target, headers, timeout, cap):
                seen.append((method, target))
                return ok_script(method, host, target)
            kw = dict(opener=opener, wall=clock.time, mono=clock.time, sleeper=clock.sleep, stop_path=os.path.join(tmp, "STOP"),
                      now_utc=lambda: dt.datetime.fromtimestamp(clock.time(), UTC), pid_alive=lambda p_: False, eia_loader=lambda path, sid: {}, steo_loader=lambda b: [])
            sink = io.StringIO()
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                rc = main(argv + ["--cache", os.path.join(tmp, "cache"), "--out", os.path.join(tmp, "out")], _fetcher_kw=kw, _today=today)
            return rc, seen
    rc, seen = cli(["fetch", "--all"])
    ck.eq("fetch --all asks for the page, every linked year up to the current one, the four EIA workbooks, the STEO zip and the manifest", (rc, len(seen)), (0, 9))
    rc, seen = cli(["fetch"])
    ck.eq("fetch with no option asks for the current and previous year (2 files) plus the page and the EIA files", (rc, len(seen)), (0, 9))
    rc, seen = cli(["fetch", "--years", "2030"])
    ck.eq("fetch --years 2030 asks for that file", (rc, [t for m, t in seen if t.endswith("2030.csv")]), (0, [PRIMARY_DIR + "2030.csv"]))
    rc, seen = cli(["fetch", "--years", "2099"])
    ck.eq("fetch --years naming a year the page does not link is refused (exit 5)", rc, 5)
    rc, seen = cli(["check-vintage"])
    ck.eq("check-vintage sends the page (GET) and a HEAD per linked year, nothing else", (rc, [m for m, t in seen]), (0, ["GET", "HEAD", "HEAD"]))
    ck.eq("fetch --max-requests 22 is refused (exit 5), with no request", cli(["fetch", "--max-requests", "22"]), (5, []))


def suite_boot(ck):
    bx, by = fx_pair(55)
    lo, hi = bootstrap_ci(bx, by, 10000, 12, SEED)
    ck.near("bootstrap CI lower bound is pinned (n = 55, L = 12, B = 10,000, seed 20261020)", lo, BOOT_PIN[0], 5e-5)
    ck.near("bootstrap CI upper bound is pinned", hi, BOOT_PIN[1], 5e-5)
    ck.near("Pearson r of the bootstrap fixture is pinned", pearson(bx, by), BOOT_PIN[2], 5e-5)
    ck.raises("a bootstrap series shorter than one block is refused", DataError, lambda: bootstrap_ci([1.0, 2.0, 3.0], [2.0, 1.0, 3.0], 10, 12, 1))
    x, y = fx_known_r()
    ck.near("Pearson r on a series with r = 0.6 exactly", pearson(x, y), 0.6, 0.01)


SUITES = {"pure": suite_pure, "boot": suite_boot, "parse": suite_parse, "build_dry": suite_build_dry, "build_reg": suite_build_reg, "fetch": suite_fetch}
# the guard -> the suites that must notice when it is removed (any one failing detects it)
GUARDS = [
    ("ua_no_address", ("pure",)), ("host_allowlist", ("pure", "fetch")), ("cache_outside_repo", ("pure",)), ("column_allowlist", ("pure",)),
    ("no_country_table", ("pure",)), ("no_price", ("pure",)), ("acknowledgement", ("pure",)), ("disclosure", ("pure", "build_dry")),
    ("pearson_exact", ("boot",)), ("seed", ("boot",)), ("boot_start", ("boot",)), ("boot_trunc", ("boot",)), ("boot_pct", ("boot",)),
    ("episode_condition", ("pure",)), ("unit_kbd_check", ("pure",)), ("assessment_codes", ("pure", "parse")), ("crude_primary_only", ("pure", "parse")),
    ("missing_stays_missing", ("parse",)), ("single_unit", ("parse",)), ("zero_reported", ("build_dry",)), ("partition", ("parse",)), ("seam", ("parse",)),
    ("vintage_recorded", ("parse",)), ("mb_scale", ("build_dry",)), ("spr_removed", ("build_dry",)), ("sign", ("build_dry",)),
    ("seam_stockch", ("build_dry",)), ("oecd_commercial_only", ("build_dry",)), ("steo_crude_line", ("build_dry",)), ("preliminary_lag", ("build_dry",)),
    ("dry_run_blind", ("pure", "build_dry")), ("dry_run_no_d", ("parse", "build_dry")), ("registration_from_file", ("build_dry",)), ("panel_frozen", ("build_dry", "build_reg")), ("demeaned", ("build_reg",)),
    ("one_primary", ("build_dry", "build_reg")), ("fips_map", ("build_dry",)), ("changes_not_levels", ("build_dry",)), ("non_overlapping", ("build_reg",)),
    ("min_sleep", ("fetch",)), ("max_requests", ("fetch",)), ("stop_blocks_fetch", ("fetch",)), ("latch_non200", ("fetch",)), ("latch_bad_body", ("fetch",)),
    ("socket_no_latch", ("fetch",)), ("pacing", ("fetch",)), ("xls_magic", ("fetch",)), ("eia_validate", ("fetch",)),
]
# the spec's guard names (section 6) and the switches that carry them
SPEC_GUARDS = (
    ("G1 missing_stays_missing", ("missing_stays_missing",)), ("G2 no_world_stock_total", ("disclosure",)), ("G3 crude_primary_only", ("crude_primary_only",)),
    ("G4 single_unit", ("single_unit", "unit_kbd_check", "mb_scale")), ("G5 assessment_codes", ("assessment_codes",)), ("G6 vintage_recorded", ("vintage_recorded",)),
    ("G7 preliminary_lag", ("preliminary_lag",)), ("G8 steo_crude_line", ("steo_crude_line",)), ("G9 oecd_commercial_only", ("oecd_commercial_only",)),
    ("G10 no_price", ("no_price",)), ("G11 changes_not_levels", ("changes_not_levels",)), ("G12 non_overlapping", ("non_overlapping",)), ("G13 one_primary", ("one_primary",)),
    ("G14 sign", ("sign",)), ("G15 disclosure", ("disclosure",)), ("G16 fips_map", ("fips_map",)), ("G17 spr_removed", ("spr_removed",)),
    ("G18 zero_reported", ("zero_reported",)), ("G19 seam", ("seam",)), ("G20 acknowledgement", ("acknowledgement",)), ("G21 column_allowlist", ("column_allowlist",)),
    ("G22 bootstrap", ("seed", "pearson_exact")), ("G23 no_country_table", ("no_country_table",)),
    ("G24 fetch_rules", ("latch_non200", "latch_bad_body", "socket_no_latch", "pacing", "min_sleep", "max_requests", "host_allowlist", "cache_outside_repo", "stop_blocks_fetch", "xls_magic", "eia_validate", "ua_no_address")),
    ("G25 dry_run_blind", ("dry_run_blind", "registration_from_file", "dry_run_no_d")), ("G26 demeaned", ("demeaned", "episode_condition")), ("G27 panel_frozen", ("panel_frozen",)),
    ("G28 seam_stockch", ("seam_stockch",)), ("G29 bootstrap_spec", ("boot_start", "boot_trunc", "boot_pct")), ("G30 partition", ("partition", "disclosure")),
)


def run_suite(name):
    ck = Checks()
    saved = list(_OFF)
    try:
        SUITES[name](ck)
    except Exception as e:          # a suite that crashes under a removed guard has noticed it
        ck.ok("suite %s ran to completion" % name, False, "%s: %s" % (type(e).__name__, e))
    finally:
        _BLIND[0] = False
    return ck


def selftest(mutants=True):
    t0 = time.time()
    results = [(n, run_suite(n)) for n in ("pure", "boot", "parse", "build_dry", "build_reg", "fetch")]
    bad_total = 0
    for title, ck in results:
        print("== %s: %d checks" % (title, len(ck.items)))
        for name, cond, detail in ck.items:
            print("  %s  %s%s" % ("PASS" if cond else "FAIL", name, "" if cond else "   <- " + detail))
            bad_total += 0 if cond else 1
    mres = {}
    if mutants:
        print("== guards (each is switched off in turn; at least one check in its suites must fail)")
        for g, suites in GUARDS:
            first = None
            for s in suites:
                with mutant(g):
                    ck = run_suite(s)
                bad = ck.failed()
                if bad:
                    first = (s, bad[0], len(bad))
                    break
            mres[g] = first is not None
            print("  %s  %s  (%s)%s" % ("DETECTED    " if first else "NOT DETECTED", g, "/".join(suites),
                                         "   %s: %d failing, first: %s <- %s" % (first[0], first[2], first[1][0], first[1][1][:110]) if first else ""))
            bad_total += 0 if first else 1
        print("== the spec's guards G1-G30 (each is covered when every one of its switches is detected)")
        for label, sw in SPEC_GUARDS:
            ok = all(mres.get(s) for s in sw)
            print("  %s  %s  [%s]" % ("COVERED    " if ok else "NOT COVERED", label, ", ".join(sw)))
            bad_total += 0 if ok else 1
    n_checks = sum(len(ck.items) for _, ck in results)
    print("selftest: %d checks, %d guards switched off one at a time (%d spec guards), %d failure(s), %.1f s" % (n_checks, len(mres), len(SPEC_GUARDS) if mutants else 0, bad_total, time.time() - t0))
    return 0 if bad_total == 0 else 1


# ------------------------------------------------------------------------------------------------------------------------
# command line
# ------------------------------------------------------------------------------------------------------------------------
def main(argv=None, _fetcher_kw=None, _today=None):
    """_fetcher_kw and _today are for the selftest only (an injected opener, clock and STOP path; a fixed date)."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch", help="download the JODI annual primary CSVs into the cache and the EIA files (the network command)")
    pf.add_argument("--years", help="years and ranges, e.g. 2024,2025 or 2015-2026; named years are requested even if cached (default: current and previous year)")
    pf.add_argument("--all", action="store_true", help="every year from %d to the current one (past years already cached are not requested again)" % FIRST_YEAR)
    pf.add_argument("--cache", default=os.environ.get("JODI_OIL_CACHE") or CACHE_DEFAULT)
    pf.add_argument("--out", default=OUT_DEFAULT, help="where fetch_log.csv and raw/ are kept")
    pf.add_argument("--sleep", type=float, default=MIN_SLEEP, help="seconds between request starts (at least %.2f)" % MIN_SLEEP)
    pf.add_argument("--max-requests", type=int, default=MAX_REQUESTS)
    pc = sub.add_parser("check-vintage", help="HEAD each annual file and report which differ from the newest cached one")
    pc.add_argument("--cache", default=os.environ.get("JODI_OIL_CACHE") or CACHE_DEFAULT)
    pc.add_argument("--out", default=OUT_DEFAULT)
    pc.add_argument("--sleep", type=float, default=MIN_SLEEP)
    pc.add_argument("--max-requests", type=int, default=MAX_REQUESTS)
    pb = sub.add_parser("build", help="offline: validate the cache and write every output")
    pb.add_argument("--panel-only", action="store_true", help="write panels.csv, print its sha256, and stop (the supervisor records it before the primary is computed)")
    pb.add_argument("--panel-sha", help="the recorded panels.csv sha256; the build refuses to go on if the panels now hash differently")
    pb.add_argument("--cache", default=os.environ.get("JODI_OIL_CACHE") or CACHE_DEFAULT)
    pb.add_argument("--out", default=OUT_DEFAULT)
    ps = sub.add_parser("selftest", help="synthetic rows, guards switched off one at a time; no network")
    ps.add_argument("--no-mutants", action="store_true", help="run the suite once, without switching guards off")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest(mutants=not a.no_mutants)
    try:
        if a.cmd == "build":
            check_cache(a.cache)
            build(a.cache, a.out, panel_only=a.panel_only, panel_sha=a.panel_sha)
            return 0
        today = _today or dt.datetime.now(dt.timezone.utc).date()
        if a.cmd == "check-vintage":
            with Fetcher(a.cache, a.out, sleep=a.sleep, max_requests=a.max_requests, **(_fetcher_kw or {})) as fe:
                print("downloads page: %s" % fe.fetch_page())
                for y in sorted(fe.links):
                    if y < FIRST_YEAR or y > today.year:
                        continue
                    word, detail = fe.check_year(y)
                    print("JODI %d (%s): %s  %s" % (y, fe.links[y], word, detail))
                print("requests sent: %d" % fe.requests)
            return 0
        with Fetcher(a.cache, a.out, sleep=a.sleep, max_requests=a.max_requests, **(_fetcher_kw or {})) as fe:
            print("downloads page: %s" % fe.fetch_page())
            cur = today.year
            if a.all:
                years = [y for y in range(FIRST_YEAR, cur + 1) if y in fe.links]
            elif a.years:
                years = parse_years(a.years, cur)
            else:
                years = [y for y in (cur - 1, cur) if y in fe.links]
            for y in years:
                print("JODI %d: %s" % (y, fe.fetch_year(y, explicit=bool(a.years))))
            for sid in EIA_XLS_IDS:
                print("EIA %s: %s" % (sid, fe.fetch_eia_xls(sid)))
            print("EIA STEO.zip: %s" % fe.fetch_steo())
            print("EIA bulk manifest: %s" % fe.fetch_manifest())
            print("requests sent: %d" % fe.requests)
        return 0
    except Latched as e:
        print("STOP: %s" % e, file=sys.stderr)
        return 3
    except SocketFault as e:
        print("socket fault (%s): the invocation ends; nothing was latched and nothing is retried" % e, file=sys.stderr)
        return 4
    except MaxRequests as e:
        print("stopped: %s" % e)
        return 0
    except Refused as e:
        print("refused: %s" % e, file=sys.stderr)
        return 5
    except DataError as e:
        print("STOP (data): %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
