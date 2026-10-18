#!/usr/bin/env python3
"""Full-sample COT horizons for NYMEX WTI and ICE Brent: is a weekly change in managed money's futures-only net position, as published, associated
with the NEXT week's price return, timed from after the report is public? Python 3 standard library plus xlrd.

  python3 bin/cot_horizons.py fetch      # the only network command: at most 8 requests, every URL named below, 2 s apart
  python3 bin/cot_horizons.py build [--unfreeze C-NNN]   # offline; byte-identical on re-run; never writes frozen_on
  python3 bin/cot_horizons.py freeze     # writes frozen_on once, only if checks.csv has no FAIL and the independent re-derivation is PASS
  python3 bin/cot_horizons.py selftest   # synthetic, no network, 24 named guards each shown to fail on its mutant

Specification: _research/2026-10-18-COT-Full-Sample-Horizons-Spec.md (its amendments and the OPEN-6 ruling override sections 0-10;
its final "Builder decisions" section records what the spec left open).

WHAT TOUCHES THE NETWORK. Only `fetch`. Hosts: publicreporting.cftc.gov, www.cftc.gov, www.eia.gov, www.gov.uk. Eight URLs, listed in URLS below,
sequential, at least 2 s apart, GET only, redirects NOT followed, retry only on 429/503 (Retry-After honoured), at most 8 requests per run
including retries, the CLAUDE.md non-SEC User-Agent (no address, no name). Any other status, or a body that is not the expected file, ends the
run. This script makes NO request to ICE, never opens a COTHist* file and never touches ~/ice_cot or its STOP latch (THE_ASK.md E-025): Brent
positions come only from the committed data/ice_brent/brent_ledger.csv.

WHAT IS PUBLISHED (data/cot_horizons/): primary.csv, descriptive.csv, plot26.csv, weekly_panel.csv, release_dates.csv, roll_calendar.csv, checks.csv,
fetch_log.csv, raw/ (CFTC rows and pages, gov.uk bank holidays), README.md, SOURCES.md. Local only (data/vintages/cot_horizons/, gitignored):
the two EIA NYMEX futures workbooks and weekly_panel_futures.csv. No raw futures print and no weekly futures return is ever committed (G24).

WHAT IT CANNOT SAY. It tests a post-release association on stated samples. It cannot say that funds moved prices, or did not.
"""
import argparse
import bisect
import contextlib
import csv
import datetime as dt
import hashlib
import http.client
import importlib.util
import io
import json
import math
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from urllib.parse import quote, urlsplit

sys.dont_write_bytecode = True

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(ROOT, "data", "cot_horizons")
VINT_DEFAULT = os.path.join(ROOT, "data", "vintages", "cot_horizons")
WTI_DIR = os.path.join(ROOT, "data", "cftc_cot")
BRENT_DIR = os.path.join(ROOT, "data", "ice_brent")

UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"       # CLAUDE.md, non-SEC hosts. No address, no name.
HEADERS = {"User-Agent": UA, "Accept-Encoding": "identity"}
MAX_REQUESTS = 8
MIN_GAP = 2.0                      # seconds between request starts
TIMEOUT = 120
BODY_CAP = 30 * 1024 * 1024
MAX_RETRY_AFTER = 120

CFTC_CODE = "067651"
SELECT = ("report_date_as_yyyy_mm_dd,cftc_contract_market_code,market_and_exchange_names,open_interest_all,"
          "m_money_positions_long_all,m_money_positions_short_all")
API_FIELDS = SELECT.split(",")


def _api_path(dsid):
    return ("/resource/%s.json?$select=%s&$where=%s&$order=report_date_as_yyyy_mm_dd&$limit=5000"
            % (dsid, quote(SELECT, safe=",_"), quote("cftc_contract_market_code='%s'" % CFTC_CODE, safe="_")))


# key, host, path (with query), saved file (relative to OUT/raw, or "~" = local vintage dir), kind of body expected
URLS = (
    ("cftc_fo", "publicreporting.cftc.gov", _api_path("72hh-3qpy"), "cftc_disagg_futonly_72hh-3qpy_067651.json", "json_rows"),
    ("cftc_co", "publicreporting.cftc.gov", _api_path("kh3c-gbw2"), "cftc_disagg_combined_kh3c-gbw2_067651.json", "json_rows"),
    ("cftc_schedule", "www.cftc.gov", "/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm", "cftc_release_schedule.html", "html"),
    ("cftc_special", "www.cftc.gov", "/MarketReports/CommitmentsofTraders/HistoricalSpecialAnnouncements/index.htm",
     "cftc_special_announcements.html", "html"),
    ("cftc_pr7864", "www.cftc.gov", "/PressRoom/PressReleases/7864-19", "cftc_press_release_7864-19.html", "html"),
    ("eia_rclc1", "www.eia.gov", "/dnav/pet/hist_xls/RCLC1d.xls", "~/eia_RCLC1d.xls", "xls"),
    ("eia_rclc2", "www.eia.gov", "/dnav/pet/hist_xls/RCLC2d.xls", "~/eia_RCLC2d.xls", "xls"),
    ("govuk_bh", "www.gov.uk", "/bank-holidays.json", "gov_uk_bank_holidays.json", "json_bh"),
)
ALLOWED_HOSTS = frozenset(h for _, h, _, _, _ in URLS)
ALLOWED_URLS = frozenset((h, p) for _, h, p, _, _ in URLS)
XLS_MAGIC = b"\xd0\xcf\x11\xe0"

# ----------------------------------------------------------------------------------------------------------------------
# E-025 isolation: an audit hook records every file the process opens (and directories it lists) that could be an ICE file or the ICE cache
# ----------------------------------------------------------------------------------------------------------------------
_ICE_RX = re.compile(r"(?i)cothist|[/\\]ice_cot([/\\]|$)|^~?[/\\]?ice_cot")
ICE_TOUCHED = []


def _audit(event, args):
    if event in ("open", "os.listdir", "os.scandir", "os.remove", "os.rename", "os.mkdir", "os.chmod", "os.truncate") and args:
        p = args[0]
        if isinstance(p, bytes):
            p = os.fsdecode(p)
        if isinstance(p, str) and _ICE_RX.search(p):
            ICE_TOUCHED.append((event, p))


sys.addaudithook(_audit)

# ----------------------------------------------------------------------------------------------------------------------
# mutants: the selftest switches one named defect on, in this process only. There is no command-line or environment switch.
# ----------------------------------------------------------------------------------------------------------------------
MUT = set()


def mut(name):
    return name in MUT


@contextlib.contextmanager
def mutated(name):
    added = name not in MUT
    MUT.add(name)
    try:
        yield
    finally:
        if added:
            MUT.discard(name)


class Refused(Exception):
    """A request, path or setting this script will not honour."""


class Stop(Exception):
    """A server refused, or a body is not the expected file: the run ends and nothing is routed around."""


class DataError(Exception):
    """A hard check failed."""


# ----------------------------------------------------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------------------------------------------------
def f(v, nd):
    """Fixed-decimal text, '' for None, no negative zero (byte-stable outputs)."""
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


def D(s):
    return dt.date.fromisoformat(s)


def iso(d):
    return d.isoformat()


def week_key(d):
    c = d.isocalendar()
    return (c[0], c[1])


def phi_p(z):
    """Two-sided p of a standard normal z."""
    return math.erfc(abs(z) / math.sqrt(2.0))


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx <= 0 or syy <= 0:
        return float("nan")
    return sxy / math.sqrt(sxx * syy)


def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2.0 + 1
        i = j + 1
    return r


def spearman(x, y):
    return pearson(ranks(x), ranks(y))


def easter(y):
    """Western Easter Sunday (anonymous Gregorian algorithm)."""
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    g = (8 * b + 13) // 25
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mo = (h + l - 7 * m + 114) // 31
    da = (h + l - 7 * m + 114) % 31 + 1
    return dt.date(y, mo, da)


def nth_weekday(y, mo, wd, n):
    """The n-th (1-based) weekday wd (Mon=0) of the month; n=-1 is the last."""
    if n > 0:
        d = dt.date(y, mo, 1)
        d += dt.timedelta(days=(wd - d.weekday()) % 7 + 7 * (n - 1))
        return d
    d = dt.date(y + (mo == 12), mo % 12 + 1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - wd) % 7)


# ----------------------------------------------------------------------------------------------------------------------
# tables: exact column allowlists, source lines, banned columns, verification of the written text
# ----------------------------------------------------------------------------------------------------------------------
PRIMARY_COLS = ["market", "book", "price_basis", "window", "first_report", "last_report", "n", "n_excl_backcast", "n_excl_shutdown",
                "n_excl_release", "n_excl_price", "n_excl_flag", "pearson", "spearman", "s_iid", "s_placebo", "s_used", "z", "p_two_sided",
                "holm_rank", "holm_alpha", "holm_reject", "spearman_band", "sign_check_spot", "verdict", "frozen_on"]
DESCRIPTIVE_COLS = ["market", "book", "price_basis", "window", "horizon_weeks", "form", "sample", "first_report", "last_report", "n", "n_blocks",
                    "pearson", "spearman", "bar", "note"]
PLOT26_COLS = ["market", "book", "price_basis", "block", "x_first_report", "x_last_report", "dn_contracts", "y_start", "y_end", "y_return_pct",
               "band"]
PANEL_COLS = ["market", "report_date", "release_used", "release_rule", "dn_fo", "dn_co", "post_start", "post_end", "ret_post_spot_pct",
              "ret_meas_spot_pct", "price_flag", "excluded_reason"]
RELEASE_COLS = ["market", "report_date", "nominal_release", "release_used", "rule", "source"]
ROLL_COLS = ["delivery_month", "expiry_date", "rule_case", "differs_from_union_calendar"]
CHECKS_COLS = ["check_id", "name", "expected", "observed", "status"]
LOG_COLS = ["utc", "host", "path", "status", "bytes", "sha256"]
ALLOW = {"primary.csv": PRIMARY_COLS, "descriptive.csv": DESCRIPTIVE_COLS, "plot26.csv": PLOT26_COLS, "weekly_panel.csv": PANEL_COLS,
         "release_dates.csv": RELEASE_COLS, "roll_calendar.csv": ROLL_COLS, "checks.csv": CHECKS_COLS, "fetch_log.csv": LOG_COLS}
BANNED_HDR = re.compile(r"nw_|newey|boot|p05|p95|pct_oi|(^|_)(long|short|gross|spread|spreading|open_interest)(_|$)|(^|_)oi(_|$)")
FUT_HDR = re.compile(r"fut")                      # G24: no committed header may contain 'fut'
ICE_SOURCE = ("ICE Futures Europe, Commitments of Traders historical files (ice.com/publicdocs/futures), derived statistics only; "
              "non-commercial research (THE_ASK.md E-025)")
BRENT_FILES = frozenset(["primary.csv", "descriptive.csv", "plot26.csv", "weekly_panel.csv", "release_dates.csv", "checks.csv"])


def check_header(name, header):
    allow = ALLOW.get(name)
    if allow is None:
        raise DataError("%s is not a table this script writes" % name)
    if list(header) != allow:
        raise DataError("%s: header differs from the exact column allowlist" % name)
    for c in header:
        if BANNED_HDR.search(c):
            raise DataError("%s: banned column %r" % (name, c))
        if FUT_HDR.search(c):
            raise DataError("%s: column %r contains 'fut' (G24)" % (name, c))


def render(name, header, rows, source):
    check_header(name, header)
    buf = io.StringIO()
    buf.write("# source: " + source + "\n")
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        if len(r) != len(header):
            raise DataError("%s: a row has %d cells, header has %d" % (name, len(r), len(header)))
        w.writerow(r)
    return buf.getvalue()


def read_table(path):
    """(header, rows as dicts, source line) of a table this script wrote or a committed sister table (first line '# source:' optional)."""
    with open(path, newline="", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    src = ""
    while lines and lines[0].startswith("#"):
        src = lines.pop(0)
    rd = list(csv.reader(lines))
    hdr = rd[0]
    return hdr, [dict(zip(hdr, r)) for r in rd[1:]], src


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".part"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


def write_bytes(path, b):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".part"
    with open(tmp, "wb") as fh:
        fh.write(b)
    os.replace(tmp, path)


def tilde(p):
    home = os.path.expanduser("~")
    return str(p).replace(home, "~") if home and home != "~" else str(p)


# ----------------------------------------------------------------------------------------------------------------------
# FETCH: the only network code
# ----------------------------------------------------------------------------------------------------------------------
def assert_ua(ua=UA):
    if "@" in ua:
        raise Refused("User-Agent contains an address")
    for var in ("SEC_UA", "CLAUDE_CODE_USER_EMAIL"):
        v = os.environ.get(var, "").strip()
        if v and (v in ua or ua in v):
            raise Refused("User-Agent contains a configured contact value (not printed)")


assert_ua()


def check_target(host, path):
    """Only the eight named URLs (G18)."""
    if mut("fetch_unlisted_ok"):
        return
    if host not in ALLOWED_HOSTS or (host, path) not in ALLOWED_URLS:
        raise Refused("host or path outside the eight named URLs: %s%s" % (host, path.split("?")[0]))


def real_opener(host, target, headers, timeout, cap):
    """GET https://host/target. Returns (status, headers, body). A redirect is NOT followed: a 3xx comes back as a status."""
    conn = http.client.HTTPSConnection(host, timeout=timeout)
    try:
        conn.request("GET", target, headers=dict(headers))
        resp = conn.getresponse()
        hd = {k.lower(): v for k, v in resp.getheaders()}
        if resp.status != 200:
            return resp.status, hd, b""
        chunks, total = [], 0
        while True:
            b = resp.read(1 << 16)
            if not b:
                break
            total += len(b)
            if total > cap:
                return resp.status, hd, None
            chunks.append(b)
        return resp.status, hd, b"".join(chunks)
    except (OSError, http.client.HTTPException) as e:
        raise Stop("socket fault (%s): the run ends, nothing is retried" % type(e).__name__)
    finally:
        conn.close()


def validate_body(kind, body):
    """The body must be the expected file; raises Stop otherwise (nothing is saved)."""
    if body is None or not body:
        raise Stop("empty or oversized body")
    if kind == "json_rows":
        try:
            rows = json.loads(body.decode("utf-8"))
        except Exception:
            raise Stop("CFTC API body is not JSON")
        if not isinstance(rows, list) or not rows or not all(isinstance(r, dict) and set(API_FIELDS) <= set(r) for r in rows):
            raise Stop("CFTC API rows do not carry the six requested fields")
        if any(r["cftc_contract_market_code"] != CFTC_CODE for r in rows):
            raise Stop("CFTC API returned a row for another contract code")
        if len(rows) >= 5000:
            raise Stop("CFTC API page limit reached (5000 rows): paging would be needed")
    elif kind == "html":
        t = body.decode("utf-8", "replace")
        if "Commitments of Traders" not in t and "COT" not in t:
            raise Stop("a cftc.gov page that does not mention the Commitments of Traders")
    elif kind == "xls":
        if not body.startswith(XLS_MAGIC):
            raise Stop("EIA body is not an .xls workbook")
        read_eia_bytes(body)
    elif kind == "json_bh":
        try:
            j = json.loads(body.decode("utf-8"))
        except Exception:
            raise Stop("bank-holidays body is not JSON")
        if "england-and-wales" not in j or "events" not in j["england-and-wales"]:
            raise Stop("bank-holidays JSON has no england-and-wales events")
    else:
        raise Stop("unknown body kind")


class Fetcher:
    """All requests go through here. Injectable opener, clock and sleeper make it testable without a network (G18)."""

    def __init__(self, out_dir, vint_dir, opener=real_opener, mono=time.monotonic, sleeper=time.sleep, utc=None, max_requests=MAX_REQUESTS,
                 urls=URLS, ua_headers=None, validator=None):
        if max_requests > MAX_REQUESTS and not mut("fetch_ninth"):
            raise Refused("at most %d requests per run, retries included" % MAX_REQUESTS)
        self.out, self.vint, self.opener = out_dir, vint_dir, opener
        self.mono, self.sleeper = mono, sleeper
        self.utc = utc or (lambda: dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        self.max_requests, self.urls = max_requests, urls
        self.validator = validator or validate_body
        self.headers = dict(ua_headers or HEADERS)
        assert_ua(self.headers["User-Agent"])
        if self.headers["User-Agent"] != UA:
            raise Refused("User-Agent is not the CLAUDE.md non-SEC string")
        self.requests, self.last_start, self.times = 0, None, []
        self.log_path = os.path.join(out_dir, "fetch_log.csv")
        self.log = self._read_log()

    def _read_log(self):
        if not os.path.exists(self.log_path):
            return []
        return read_table(self.log_path)[1]

    def _append_log(self, row):
        self.log.append(dict(zip(LOG_COLS, row)))
        src = ("request log for CFTC, EIA and gov.uk files fetched by bin/cot_horizons.py (CFTC public domain; EIA US government; "
               "gov.uk Open Government Licence); each row carries its own UTC time; no ICE request is made")
        write_text(self.log_path, render("fetch_log.csv", LOG_COLS, [[r[c] for c in LOG_COLS] for r in self.log], src))

    def saved_path(self, saved):
        return os.path.join(self.vint, saved[2:]) if saved.startswith("~/") else os.path.join(self.out, "raw", saved)

    def already(self, host, path, saved):
        p = self.saved_path(saved)
        if not os.path.exists(p):
            return False
        sha = sha256_file(p)
        return any(r["host"] == host and r["path"] == path and r["status"] == "200" and r["sha256"] == sha for r in self.log)

    def _pace(self):
        if self.last_start is not None:
            wait = MIN_GAP - (self.mono() - self.last_start)
            if wait > 0 and not mut("fetch_no_pacing"):
                self.sleeper(wait)

    def get(self, key, host, path, saved, kind):
        if self.already(host, path, saved):
            return "skipped (saved file matches a fetch_log.csv row)"
        while True:
            if self.requests >= self.max_requests:
                return "NOT FETCHED: request cap of %d reached (retries count); run fetch again to resume" % self.max_requests
            check_target(host, path)
            self._pace()
            self.last_start = self.mono()
            self.times.append(self.last_start)
            self.requests += 1
            status, hd, body = self.opener(host, path, self.headers, TIMEOUT, BODY_CAP)
            sha = sha256_of(body) if body else ""
            self._append_log([self.utc(), host, path, str(status), str(len(body) if body else 0), sha])
            if status == 200:
                self.validator(kind, body)
                write_bytes(self.saved_path(saved), body)
                return "fetched %d bytes" % len(body)
            if 300 <= status < 400 and not mut("fetch_follow_redirect"):
                raise Stop("%s%s answered HTTP %d (a redirect): not followed, the run ends" % (host, path.split("?")[0], status))
            if 300 <= status < 400:
                loc = hd.get("location", "")
                u = urlsplit(loc)
                host, path = u.hostname or host, (u.path or "/") + ("?" + u.query if u.query else "")
                continue
            if status in (429, 503):
                try:
                    ra = int(hd.get("retry-after", "0") or 0)
                except ValueError:
                    ra = 0
                if ra > MAX_RETRY_AFTER:
                    raise Stop("%s asked for a pause of %d s (over %d): the run ends" % (host, ra, MAX_RETRY_AFTER))
                self.sleeper(max(ra, MIN_GAP))
                continue
            raise Stop("%s%s answered HTTP %d: the run ends and nothing is routed around" % (host, path.split("?")[0], status))


def fetch_cmd(out_dir, vint_dir, opener=real_opener, **kw):
    os.makedirs(os.path.join(vint_dir), exist_ok=True)
    fe = Fetcher(out_dir, vint_dir, opener=opener, **kw)
    for key, host, path, saved, kind in fe.urls:
        print("%-14s %s" % (key, fe.get(key, host, path, saved, kind)))
    print("requests sent: %d (cap %d, retries included)" % (fe.requests, fe.max_requests))
    return fe


# ----------------------------------------------------------------------------------------------------------------------
# EIA workbooks (US government, public domain): Data 1 sheet, row 0 title, row 1 sourcekey, row 2 header, then Date / value
# ----------------------------------------------------------------------------------------------------------------------
def read_eia_bytes(body):
    """{date: value} plus (sourcekey, title). Every failure to read is a Stop/DataError: a file that does not open or lacks the layout is not the file."""
    import xlrd
    try:
        b = xlrd.open_workbook(file_contents=body)
        s = b.sheet_by_name("Data 1")
        title, key = str(s.cell_value(0, 1)), str(s.cell_value(1, 1))
        if s.cell_value(2, 0) != "Date" or "Dollars per Barrel" not in title:
            raise DataError("EIA workbook layout changed")
        ser = {}
        for i in range(3, s.nrows):
            dv, v = s.row_values(i)[:2]
            if not isinstance(v, float):
                continue
            d = xlrd.xldate_as_datetime(dv, b.datemode).date()
            if d in ser:
                raise DataError("EIA workbook: duplicate date %s" % d)
            ser[d] = v
    except (DataError, Stop):
        raise
    except Exception as e:
        raise DataError("EIA workbook cannot be read (%s)" % type(e).__name__)
    return ser, key, title


def read_eia(path):
    with open(path, "rb") as fh:
        body = fh.read()
    return read_eia_bytes(body)


# ----------------------------------------------------------------------------------------------------------------------
# CALENDARS
# ----------------------------------------------------------------------------------------------------------------------
def us_federal_holidays(y):
    """Observed US federal holidays of year y (5 U.S.C. 6103; a Saturday holiday is observed on the Friday, a Sunday holiday on the Monday;
    Juneteenth from 2021). Inauguration Day is a holiday for DC-area employees only and is not included."""
    def obs(d):
        return d - dt.timedelta(days=1) if d.weekday() == 5 else d + dt.timedelta(days=1) if d.weekday() == 6 else d
    s = {obs(dt.date(y, 1, 1)), nth_weekday(y, 1, 0, 3), nth_weekday(y, 2, 0, 3), nth_weekday(y, 5, 0, -1), obs(dt.date(y, 7, 4)),
         nth_weekday(y, 9, 0, 1), nth_weekday(y, 10, 0, 2), obs(dt.date(y, 11, 11)), nth_weekday(y, 11, 3, 4), obs(dt.date(y, 12, 25))}
    if y >= 2021:
        s.add(obs(dt.date(y, 6, 19)))
    return s


def us_federal_holidays_span(y0, y1):
    s = set()
    for y in range(y0 - 1, y1 + 2):
        s |= us_federal_holidays(y)
    return s


def nymex_rule_holidays(y):
    """The standard CME Group energy holidays of year y, by rule: New Year's Day (not observed on a Saturday), MLK, Presidents', Good Friday,
    Memorial, Juneteenth (from 2022), Independence Day, Labor, Thanksgiving, Christmas. Used to GENERATE and to CHECK NYMEX_HOLIDAYS; the set
    that is used is the literal below."""
    def obs(d):
        return d - dt.timedelta(days=1) if d.weekday() == 5 else d + dt.timedelta(days=1) if d.weekday() == 6 else d
    s = set()
    ny = dt.date(y, 1, 1)
    if ny.weekday() != 5:
        s.add(ny if ny.weekday() < 5 else ny + dt.timedelta(days=1))
    s |= {nth_weekday(y, 1, 0, 3), nth_weekday(y, 2, 0, 3), easter(y) - dt.timedelta(days=2), nth_weekday(y, 5, 0, -1), obs(dt.date(y, 7, 4)),
          nth_weekday(y, 9, 0, 1), nth_weekday(y, 11, 3, 4), obs(dt.date(y, 12, 25))}
    if y >= 2022:
        s.add(obs(dt.date(y, 6, 19)))
    return s


# Hard-coded NYMEX non-trading days, 2005-2026 (the days on which prints are ignored everywhere). Generated by nymex_rule_holidays and then
# checked against the EIA files: every entry that falls inside the data is evidenced by absence from BOTH files or by a carried-forward print
# (evidence=eia_carry_forward). No CME Group holiday notice could be read by a script (CME refuses scripts) or was read in a browser in this
# build, so an entry evidenced only by absence is a WARN in checks.csv (spec 3.4).
NYMEX_HOLIDAYS = frozenset(D(x) for x in (
    "2005-01-17 2005-02-21 2005-03-25 2005-05-30 2005-07-04 2005-09-05 2005-11-24 2005-12-26 "
    "2006-01-02 2006-01-16 2006-02-20 2006-04-14 2006-05-29 2006-07-04 2006-09-04 2006-11-23 2006-12-25 "
    "2007-01-01 2007-01-15 2007-02-19 2007-04-06 2007-05-28 2007-07-04 2007-09-03 2007-11-22 2007-12-25 "
    "2008-01-01 2008-01-21 2008-02-18 2008-03-21 2008-05-26 2008-07-04 2008-09-01 2008-11-27 2008-12-25 "
    "2009-01-01 2009-01-19 2009-02-16 2009-04-10 2009-05-25 2009-07-03 2009-09-07 2009-11-26 2009-12-25 "
    "2010-01-01 2010-01-18 2010-02-15 2010-04-02 2010-05-31 2010-07-05 2010-09-06 2010-11-25 2010-12-24 "
    "2011-01-17 2011-02-21 2011-04-22 2011-05-30 2011-07-04 2011-09-05 2011-11-24 2011-12-26 "
    "2012-01-02 2012-01-16 2012-02-20 2012-04-06 2012-05-28 2012-07-04 2012-09-03 2012-11-22 2012-12-25 "
    "2013-01-01 2013-01-21 2013-02-18 2013-03-29 2013-05-27 2013-07-04 2013-09-02 2013-11-28 2013-12-25 "
    "2014-01-01 2014-01-20 2014-02-17 2014-04-18 2014-05-26 2014-07-04 2014-09-01 2014-11-27 2014-12-25 "
    "2015-01-01 2015-01-19 2015-02-16 2015-04-03 2015-05-25 2015-07-03 2015-09-07 2015-11-26 2015-12-25 "
    "2016-01-01 2016-01-18 2016-02-15 2016-03-25 2016-05-30 2016-07-04 2016-09-05 2016-11-24 2016-12-26 "
    "2017-01-02 2017-01-16 2017-02-20 2017-04-14 2017-05-29 2017-07-04 2017-09-04 2017-11-23 2017-12-25 "
    "2018-01-01 2018-01-15 2018-02-19 2018-03-30 2018-05-28 2018-07-04 2018-09-03 2018-11-22 2018-12-25 "
    "2019-01-01 2019-01-21 2019-02-18 2019-04-19 2019-05-27 2019-07-04 2019-09-02 2019-11-28 2019-12-25 "
    "2020-01-01 2020-01-20 2020-02-17 2020-04-10 2020-05-25 2020-07-03 2020-09-07 2020-11-26 2020-12-25 "
    "2021-01-01 2021-01-18 2021-02-15 2021-04-02 2021-05-31 2021-07-05 2021-09-06 2021-11-25 2021-12-24 "
    "2022-01-17 2022-02-21 2022-04-15 2022-05-30 2022-06-20 2022-07-04 2022-09-05 2022-11-24 2022-12-26 "
    "2023-01-02 2023-01-16 2023-02-20 2023-04-07 2023-05-29 2023-06-19 2023-07-04 2023-09-04 2023-11-23 2023-12-25 "
    "2024-01-01 2024-01-15 2024-02-19 2024-03-29 2024-05-27 2024-06-19 2024-07-04 2024-09-02 2024-11-28 2024-12-25 "
    "2025-01-01 2025-01-20 2025-02-17 2025-04-18 2025-05-26 2025-06-19 2025-07-04 2025-09-01 2025-11-27 2025-12-25 "
    "2026-01-01 2026-01-19 2026-02-16 2026-04-03 2026-05-25 2026-06-19 2026-07-03 2026-09-07 2026-11-26 2026-12-25").split())


def step_bd(d, n, is_bd, direction=-1):
    """The n-th business day strictly before (direction -1) or after (+1) d."""
    k = 0
    while k < n:
        d += dt.timedelta(days=direction)
        if is_bd(d):
            k += 1
    return d


def expiry_date(dy, dm, is_bd):
    """Last trading day of the CL contract with delivery month (dy, dm), by the EIA text (TblDefs/pet_pri_fut_tbldef2): the third business day
    prior to the 25th calendar day of the month preceding the delivery month; if the 25th is a non-business day, the third business day prior to
    the business day preceding the 25th. Returns (date, rule_case)."""
    y, m = (dy, dm - 1) if dm > 1 else (dy - 1, 12)
    d25 = dt.date(y, m, 25)
    if is_bd(d25):
        return step_bd(d25, 3, is_bd), "25th_business_day"
    case = "25th_saturday" if d25.weekday() == 5 else "25th_sunday" if d25.weekday() == 6 else "25th_holiday"
    if mut("expiry_ignore_non_business"):
        return step_bd(d25, 3, is_bd), case
    anchor = step_bd(d25, 1, is_bd)
    return step_bd(anchor, 3, is_bd), case


def months_between(y0, m0, y1, m1):
    y, m = y0, m0
    while (y, m) <= (y1, m1):
        yield y, m
        y, m = (y, m + 1) if m < 12 else (y + 1, 1)


# ----------------------------------------------------------------------------------------------------------------------
# INPUTS: CFTC rows, the committed Brent ledger, EIA workbooks
# ----------------------------------------------------------------------------------------------------------------------
CFTC_FILES = {"fo": "cftc_disagg_futonly_72hh-3qpy_067651.json", "co": "cftc_disagg_combined_kh3c-gbw2_067651.json"}


def parse_cftc_rows(rows):
    """{date: (mm_long, mm_short, open_interest)} from API rows. Selected by contract code only, never by name; a duplicate date is an error."""
    out = {}
    for r in rows:
        if r["cftc_contract_market_code"] != CFTC_CODE:
            raise DataError("a row for another contract code: %r" % r["cftc_contract_market_code"])
        d = D(r["report_date_as_yyyy_mm_dd"][:10])
        if d in out:
            raise DataError("duplicate CFTC report date %s" % d)
        out[d] = (int(r["m_money_positions_long_all"]), int(r["m_money_positions_short_all"]), int(r["open_interest_all"]))
    return dict(sorted(out.items()))


def load_cftc(raw_dir):
    out = {}
    for book, fn in CFTC_FILES.items():
        with open(os.path.join(raw_dir, fn), "rb") as fh:
            out[book] = parse_cftc_rows(json.loads(fh.read().decode("utf-8")))
    if list(out["fo"]) != list(out["co"]):
        raise DataError("the futures-only and combined books do not carry the same report dates")
    return out


def load_brent_ledger(path):
    """Report dates and managed-money nets from the committed derived ledger only (E-025). Nothing else is read for Brent positions."""
    hdr, rows, _ = read_table(path)
    pf = "co" if mut("brent_read_co") else "fo"          # mutant of G21: the futures-only columns read from the combined ones
    need = ["report_date", "fo_mm_net", "fo_mm_net_chg", "co_mm_net", "co_mm_net_chg", "price_flag"]
    for c in need:
        if c not in hdr:
            raise DataError("brent_ledger.csv lacks column %s" % c)
    out = []
    for r in rows:
        out.append({"date": D(r["report_date"]), "fo_net": int(r[pf + "_mm_net"]), "co_net": int(r["co_mm_net"]),
                    "fo_chg": int(r["fo_mm_net_chg"]) if r["fo_mm_net_chg"] != "" else None,
                    "co_chg": int(r["co_mm_net_chg"]) if r["co_mm_net_chg"] != "" else None, "price_flag": r["price_flag"]})
    return out


def sister_suspect_ranges():
    """KNOWN_SUSPECT_PRINTS from bin/pull_ice_brent_cot.py, read by importing the module (it makes no request on import and opens no file)."""
    p = os.path.join(ROOT, "bin", "pull_ice_brent_cot.py")
    spec = importlib.util.spec_from_file_location("pull_ice_brent_cot_const", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return tuple(m.KNOWN_SUSPECT_PRINTS)


def in_ranges(d, ranges):
    return any(a <= d <= b for a, b in ranges)


# ----------------------------------------------------------------------------------------------------------------------
# RELEASE DATES
# ----------------------------------------------------------------------------------------------------------------------
BACKCAST_LAST_PUBLIC_GAP = D("2009-08-25")      # the last report whose position was first published on 2009-10-20 (spec 2.1)
FIRST_PUBLIC_REPORT = D("2009-09-01")           # the first disaggregated report, published on 4 Sep 2009
BACKCAST_LAST = D("2009-09-01")                 # OPEN-6 ruling: a pair whose delta uses a non-public level is backcast: report dates up to 2009-09-01
SHUTDOWN_BLOCKS = ((D("2013-09-24"), D("2013-11-12")), (D("2018-12-18"), D("2019-02-26")))
LAG_MAX_DAYS = 7
# Federal closure days that are not in 5 U.S.C. 6103 but are announced on the CFTC special-announcements page. Each is used by the holiday rule,
# so a release in its window moves to the next business day after the Friday (ambiguity takes the later release).
CLOSURE_DAYS = {D("2018-12-05"): "National Day of Mourning for President G. H. W. Bush (announcement of December 4, 2018)",
                D("2020-12-24"): "additional federal holiday (announcement of December 28, 2020)",
                D("2025-01-09"): "National Day of Mourning for President Carter (announcement of January 7, 2025)"}
PAGE_SPECIAL = "https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalSpecialAnnouncements/index.htm"
PAGE_SCHEDULE = "https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm"
# (report date, release date, announcement text that must be found on the saved special-announcements page, source label)
STATED_OVERRIDES = (
    (D("2014-07-01"), D("2014-07-04"), "inadvertently published on Friday, July 4, 2014", "special announcement of July 7, 2014 (early publication)"),
    (D("2014-12-23"), D("2014-12-30"), "next publication date for the Commitment of Traders will be Tuesday, December 30, 2014",
     "special announcement of December 19, 2014 (federal closures on 25-26 Dec 2014)"),
    (D("2025-01-07"), D("2025-01-13"), "will be released on Monday, January 13, 2025", "special announcement of January 7, 2025 (Carter)"),
)


def text_of_html(html_bytes):
    import html as _h
    t = html_bytes.decode("utf-8", "replace")
    t = re.sub(r"(?s)<(script|style).*?</\1>", "", t)
    t = re.sub(r"<(br|/p|/tr|/li|/h\d|/div|/table)[^>]*>", "\n", t)
    t = re.sub(r"</t[dh]>", " | ", t)
    t = _h.unescape(re.sub(r"<[^>]+>", "", t))
    return re.sub(r"[ \t\xa0]+", " ", t)


MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def parse_long_date(s):
    m = re.match(r"\s*([A-Z][a-z]+)\s+0?(\d{1,2}),\s*(\d{4})", s)
    if not m or m.group(1) not in MONTHS:
        raise DataError("cannot parse a date from %r" % s[:40])
    return dt.date(int(m.group(3)), MONTHS.index(m.group(1)) + 1, int(m.group(2)))


def parse_dec9_table(text, which="dec9"):
    """{report date: new publish date} from the table of the 9 Dec 2025 notice (authoritative) or, as a mutant, the 18 Nov 2025 notice."""
    start = text.find("December 9, 2025:" if which == "dec9" else "November 18, 2025:")
    end = text.find("November 18, 2025:" if which == "dec9" else "January 07, 2025:", start)
    if start < 0 or end < 0:
        raise DataError("the 2025 shutdown notice was not found on the special-announcements page")
    out = {}
    for m in re.finditer(r"(\d\d/\d\d/\d{4})\s*\|\s*(\d\d/\d\d/\d{4})\s*\|\s*(\d\d/\d\d/\d{4})", text[start:end]):
        rd = dt.datetime.strptime(m.group(1), "%m/%d/%Y").date()
        out[rd] = dt.datetime.strptime(m.group(3), "%m/%d/%Y").date()
    if len(out) < 10:
        raise DataError("the 2025 shutdown table has %d rows" % len(out))
    return out


def parse_ion_2023(text):
    """{report date: release date} for the ION delays: 'Today, staff is issuing the ... report that was originally scheduled to be published on <Friday>'
    under a notice dated <release>. The report date is the Tuesday three days before the originally scheduled Friday."""
    out = {}
    for m in re.finditer(r"((?:February|March) \d{1,2}, 2023): The cyber-related incident[^\n]*?Today, staff is issuing the Commitments of Traders report that was "
                         r"originally scheduled to be published on ((?:February|March) \d{1,2}, 2023)", text):
        rel, sched = parse_long_date(m.group(1)), parse_long_date(m.group(2))
        out[sched - dt.timedelta(days=3)] = rel
    if len(out) != 7:
        raise DataError("expected 7 ION 2023 re-issue notices, found %d" % len(out))
    return out


def build_overrides(special_html, which="dec9"):
    """{report date: (release date, source label)} from the saved special-announcements page. A stated override whose announcement text is not on the
    page is a DataError."""
    text = text_of_html(special_html)
    flat = re.sub(r"\s+", " ", text)
    ov = {}
    for rd, rel in parse_dec9_table(text, which).items():
        ov[rd] = (rel, "cftc.gov special announcements, 9 Dec 2025 table (authoritative)" if which == "dec9" else "cftc.gov special announcements, 18 Nov 2025 table")
    for rd, rel in parse_ion_2023(text).items():
        ov[rd] = (rel, "cftc.gov special announcements, ION re-issue notice of %s" % rel.strftime("%d %b %Y"))
    for rd, rel, phrase, label in STATED_OVERRIDES:
        if phrase not in flat:
            raise DataError("override %s: announcement text not found on the saved page: %r" % (rd, phrase))
        ov[rd] = (rel, "cftc.gov " + label)
    return ov


def friday_of(d):
    return d + dt.timedelta(days=4 - d.weekday())


def next_business_day_after(d, hol):
    d += dt.timedelta(days=1)
    while d.weekday() >= 5 or d in hol:
        d += dt.timedelta(days=1)
    return d


def cftc_release(rd, hol, overrides=None, ignore_holidays=False):
    """(nominal release, release used, rule). Nominal: the Friday of the report's week. Holiday rule: a US federal holiday (or listed closure) on a
    weekday strictly after the report date and on or before that Friday moves the release to the next business day after the Friday."""
    fri = friday_of(rd)
    rel, rule = fri, "friday_nominal"
    if not (ignore_holidays or mut("release_ignore_holidays")):
        d = rd + dt.timedelta(days=1)
        while d <= fri:
            if d.weekday() < 5 and d in hol:
                rel, rule = next_business_day_after(fri, hol), "federal_holiday_next_business_day"
                break
            d += dt.timedelta(days=1)
    if overrides and rd in overrides:
        rel, src = overrides[rd]
        return fri, rel, "override"
    return fri, rel, rule


def parse_schedule_2026(sched_html):
    """[(report date, release date)] for the 52 releases of the saved 2026 schedule page. The report date is the Tuesday three days before the
    release Friday; a release marked * is delayed, so its Friday is the Friday before it."""
    text = text_of_html(sched_html)
    i = text.find("2026 Release Schedule")
    j = text.find("*Delayed release date", i)
    if i < 0 or j < 0:
        raise DataError("2026 schedule not found on the saved page")
    out = []
    for m in re.finditer(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s*\|((?:\s*\d\d\*?\s*\|)+)", text[i:j]):
        mo = MONTHS.index(m.group(1)) + 1
        for dd, star in re.findall(r"(\d\d)(\*?)", m.group(2)):
            rel = dt.date(2026, mo, int(dd))
            fri = rel
            if star:
                fri = rel - dt.timedelta(days=1)
                while fri.weekday() != 4:
                    fri -= dt.timedelta(days=1)
            out.append((fri - dt.timedelta(days=3), rel))
    return out


# ----------------------------------------------------------------------------------------------------------------------
# ENGLISH BANK HOLIDAYS (ICE release timing): gov.uk JSON for the years it covers, computed (Easter, fixed days, substitutes) elsewhere
# ----------------------------------------------------------------------------------------------------------------------
UK_ONE_OFFS = (
    # (date, kind, text): 'add' = an extra day; 'move' = the usual bank holiday is moved to this date from `from`
    (D("2011-04-29"), "add", None, "Royal wedding (Proclamation, 2011)"),
    (D("2012-06-04"), "move", D("2012-05-28"), "Spring bank holiday moved for the Diamond Jubilee (Proclamation, 2012)"),
    (D("2012-06-05"), "add", None, "Diamond Jubilee extra day (Proclamation, 2012)"),
    (D("2020-05-08"), "move", D("2020-05-04"), "Early May bank holiday moved for the 75th anniversary of VE Day (2020)"),
    (D("2022-06-02"), "move", D("2022-05-30"), "Spring bank holiday moved for the Platinum Jubilee (Proclamation, 2022)"),
    (D("2022-06-03"), "add", None, "Platinum Jubilee extra day (Proclamation, 2022)"),
    (D("2022-09-19"), "add", None, "State funeral of Queen Elizabeth II (Proclamation, 2022)"),
    (D("2023-05-08"), "add", None, "Coronation of King Charles III (Proclamation, 2023)"),
)


def uk_computed(y):
    """English bank holidays of year y from the date algorithm, plus the proclaimed one-offs."""
    s = set()
    ny = dt.date(y, 1, 1)
    s.add(ny if ny.weekday() < 5 else ny + dt.timedelta(days=(7 - ny.weekday())))
    e = easter(y)
    s.add(e - dt.timedelta(days=2))
    s.add(e + dt.timedelta(days=1))
    s.add(nth_weekday(y, 5, 0, 1))
    s.add(nth_weekday(y, 5, 0, -1))
    s.add(nth_weekday(y, 8, 0, -1))
    xmas, box = dt.date(y, 12, 25), dt.date(y, 12, 26)
    s.add(xmas if xmas.weekday() < 5 else dt.date(y, 12, 27))
    s.add(box if box.weekday() < 5 else dt.date(y, 12, 28))
    for d, kind, frm, _ in UK_ONE_OFFS:
        if d.year == y:
            if kind == "move":
                s.discard(frm)
            s.add(d)
    return s


def uk_json_dates(bh_json):
    return sorted(D(e["date"]) for e in bh_json["england-and-wales"]["events"])


def uk_holidays(bh_json, y0=2010, y1=2028):
    """(set of English bank holidays y0..y1, years cross-checked, list of mismatch strings). The file's dates are used for the years it covers; a
    mismatch with the computed set for such a year is reported (and the caller fails)."""
    fj = uk_json_dates(bh_json)
    years = sorted(set(d.year for d in fj))
    comp = {y: uk_computed(y) for y in range(y0, y1 + 1)}
    bad = []
    for y in years:
        got = set(d for d in fj if d.year == y)
        if got != comp[y]:
            bad.append("%d: file-only %s; computed-only %s" % (y, sorted(iso(d) for d in got - comp[y]), sorted(iso(d) for d in comp[y] - got)))
    out = set()
    for y in range(y0, y1 + 1):
        out |= set(d for d in fj if d.year == y) if y in years else comp[y]
    return out, years, bad


def ice_release(rd, bh):
    """(nominal, release used, rule) for an ICE report: the Friday of the report's week at 18:30 London; if that Friday is an English bank holiday,
    the next London business day. Ambiguity takes the later date (uk_holiday_assumed)."""
    fri = friday_of(rd)
    if fri in bh and not mut("ice_good_friday_monday"):
        d = fri + dt.timedelta(days=1)
        while d.weekday() >= 5 or d in bh:
            d += dt.timedelta(days=1)
        return fri, d, "uk_holiday_assumed"
    if fri in bh:                                  # mutant: move to the Monday whatever it is
        return fri, fri + dt.timedelta(days=3), "uk_holiday_assumed"
    return fri, fri, "friday_nominal"


# ----------------------------------------------------------------------------------------------------------------------
# PRICE BASES AND WINDOWS
# ----------------------------------------------------------------------------------------------------------------------
MAX_MOVE_DAYS = 3
SPOT_WTI = "EIA_Cushing_spot_not_NYMEX_settle"
SPOT_BRENT = "EIA_Europe_Brent_spot_FOB_proxy_not_futures"
FUT_WTI = "nymex_futures_roll"
FLAG_NAME = "eia_spot_gap_unverified"


def next_ref_day(d, ref, limit=20):
    d += dt.timedelta(days=1)
    for _ in range(limit):
        if ref(d):
            return d
        d += dt.timedelta(days=1)
    raise DataError("no reference trading day within %d days after %s" % (limit, d))


class SpotBasis:
    """A single daily price series with a reference calendar. Prints dated on `ignore` days are ignored everywhere."""
    kind = "spot"

    def __init__(self, name, series, ref, ignore=frozenset()):
        self.name, self.ref = name, ref
        self.s = {d: v for d, v in series.items() if d not in ignore}
        self.last = max(self.s)

    def nominal_after(self, r):
        return next_ref_day(r, self.ref)

    def pick(self, a0):
        for k in range(MAX_MOVE_DAYS + 1):
            d = a0 + dt.timedelta(days=k)
            if d in self.s:
                return d
        return None

    def window(self, a0, b0):
        a, b = self.pick(a0), self.pick(b0)
        if a is None or b is None:
            return {"ret": None, "a": a, "b": b, "reason": "missing_print", "contract": ""}
        pa, pb = self.s[a], self.s[b]
        if pa <= 0 or pb <= 0:
            return {"ret": None, "a": a, "b": b, "reason": "non_positive_print", "contract": ""}
        return {"ret": pb / pa - 1, "a": a, "b": b, "reason": "", "contract": ""}


class FuturesBasis:
    """RCLC1/RCLC2 with the roll rule of spec 3.4: start at RCLC2(a); end at RCLC1(b) if an expiry e satisfies a <= e < b, otherwise at RCLC2(b).
    A date is usable only if BOTH series print on it (so the end of window k and the start of window k+1 are one date)."""
    kind = "fut"

    def __init__(self, r1, r2, hol, expiries, ref):
        self.hol = hol
        self.r1 = {d: v for d, v in r1.items() if d not in hol}
        self.r2 = {d: v for d, v in r2.items() if d not in hol}
        self.exp = sorted(expiries)
        self.ref = ref
        self.name = FUT_WTI
        self.last = min(max(self.r1), max(self.r2))

    def nominal_after(self, r):
        return next_ref_day(r, self.ref)

    def pick(self, a0):
        for k in range(MAX_MOVE_DAYS + 1):
            d = a0 + dt.timedelta(days=k)
            if d in self.r1 and d in self.r2:
                return d
        return None

    def expiry_between(self, a, b):
        i = bisect.bisect_left(self.exp, a)
        es = []
        while i < len(self.exp) and self.exp[i] < b:
            es.append(self.exp[i])
            i += 1
        if len(es) > 1:
            raise DataError("more than one expiry in the window %s to %s: %s" % (a, b, es))
        return es[0] if es else None

    def window(self, a0, b0):
        a, b = self.pick(a0), self.pick(b0)
        if a is None or b is None:
            return {"ret": None, "a": a, "b": b, "reason": "missing_print", "contract": ""}
        e = self.expiry_between(a0, b0) if mut("expiry_uses_nominal") else self.expiry_between(a, b)
        if mut("naive_front"):
            pa, pb, c = self.r1[a], self.r1[b], "RCLC1>RCLC1"
        elif e is not None:
            pa, pb, c = self.r2[a], self.r1[b], "RCLC2>RCLC1(roll)"
        else:
            pa, pb, c = self.r2[a], self.r2[b], "RCLC2>RCLC2"
        if pa <= 0 or pb <= 0:
            return {"ret": None, "a": a, "b": b, "reason": "non_positive_print", "contract": c}
        return {"ret": pb / pa - 1, "a": a, "b": b, "reason": "", "contract": c}


def fut_expiries(is_bd, y0, m0, y1, m1):
    return [(ym, expiry_date(ym[0], ym[1], is_bd)) for ym in months_between(y0, m0, y1, m1)]


# ----------------------------------------------------------------------------------------------------------------------
# MARKETS: reports, levels, releases, report-level exclusions
# ----------------------------------------------------------------------------------------------------------------------
class Cfg:
    """The dates and tables that make the build real; the selftest passes a synthetic one (2030-2031)."""

    def __init__(self, **kw):
        self.backcast_last = BACKCAST_LAST
        self.backcast_label_last = BACKCAST_LAST_PUBLIC_GAP
        self.shutdown_blocks = SHUTDOWN_BLOCKS
        self.lag_max = LAG_MAX_DAYS
        self.realtime_level_first = FIRST_PUBLIC_REPORT      # the first report whose LEVEL was public in real time
        self.wti_first = D("2009-09-08")                     # WTI primary first report (OPEN-6 ruling)
        self.wti_pool_first = D("2006-06-20")
        self.wti_last_fut = None                             # derived: last report whose futures window is complete
        self.brent_first = D("2011-01-11")
        self.flag_ranges = ()
        self.__dict__.update(kw)


class Mkt:
    def __init__(self, name, dates, nets, rel, rule, src):
        self.name, self.dates, self.N, self.rel, self.rule, self.src = name, dates, nets, rel, rule, src
        self.M = len(dates)
        self.idx = {d: i for i, d in enumerate(dates)}
        self.excl = [""] * self.M
        self.cause = [""] * self.M

    def dn(self, book, k, h=1):
        if k - h < 0:
            return None
        if mut("x_level"):
            return self.N[book][k]
        return self.N[book][k] - self.N[book][k - h]


def mark_exclusions(m, cfg):
    for k, d in enumerate(m.dates):
        if d <= cfg.backcast_last and m.name == "WTI":
            m.excl[k], m.cause[k] = "backcast_not_public", "backcast"
        elif any(a <= d <= b for a, b in cfg.shutdown_blocks) and m.name == "WTI":
            m.excl[k], m.cause[k] = "unverified_shutdown_release", "shutdown"
        elif (m.rel[k] - d).days > cfg.lag_max:
            m.excl[k], m.cause[k] = "release_lag_gt_7d", "release"
    for k in range(m.M - 1):
        if m.excl[k] == "" and m.excl[k + 1] in ("unverified_shutdown_release", "release_lag_gt_7d"):
            m.excl[k], m.cause[k] = "next_report_excluded", m.cause[k + 1]


def window_dates(m, basis, kind, k):
    """Nominal (a0, b0) of the window of report k, or None if the window needs a report that does not exist."""
    D_ = m.dates
    if kind == "post_release":
        if k + 1 >= m.M:
            return None
        if mut("start_at_report_tuesday"):
            return D_[k], basis.nominal_after(m.rel[k + 1])
        if mut("start_at_release_day"):
            return m.rel[k], basis.nominal_after(m.rel[k + 1])
        return basis.nominal_after(m.rel[k]), basis.nominal_after(m.rel[k + 1])
    if kind == "post_measurement":
        return (D_[k], D_[k + 1]) if k + 1 < m.M else None
    if kind == "same_week":
        return (D_[k - 1], D_[k]) if k >= 1 else None
    if kind == "prev_week":
        return (D_[k - 2], D_[k - 1]) if k >= 2 else None
    if kind == "post_next_report":
        return (D_[k + 1], D_[k + 2]) if k + 2 < m.M else None
    raise DataError("unknown window kind %s" % kind)


def compute_windows(m, basis, kind, fallback=None):
    out = []
    for k in range(m.M):
        wd = window_dates(m, basis, kind, k)
        if wd is None:
            out.append(None)
            continue
        if basis.kind == "fut" and wd[1] > basis.last:
            if fallback is not None and mut("fut_substitute_spot"):
                out.append(fallback.window(*wd))
                continue
            out.append({"ret": None, "a": None, "b": None, "reason": "beyond_data_end", "contract": ""})
            continue
        if basis.kind == "spot" and wd[1] > basis.last + dt.timedelta(days=MAX_MOVE_DAYS):
            out.append({"ret": None, "a": None, "b": None, "reason": "beyond_data_end", "contract": ""})
            continue
        out.append(basis.window(*wd))
    return out


def last_complete(m, W):
    """Index of the last report whose window is complete (both prints found)."""
    ks = [k for k in range(m.M) if W[k] is not None and W[k]["reason"] != "beyond_data_end"]
    return max(ks) if ks else None


# ----------------------------------------------------------------------------------------------------------------------
# SAMPLES AND STATISTICS
# ----------------------------------------------------------------------------------------------------------------------
BOOKS = ("fo", "co")
Z95 = 1.96
SEED = 20261018
PLACEBO_DRAWS = 2000


def select(m, W, first, last, admit_backcast=False, flag_ranges=(), include_flagged=False, pred=None):
    """Included report indexes of one sample, and the counts of what was left out of its frame. `pred(k, w)` returning False leaves a pair out
    silently into counts['other'] (used by the descriptive subsamples). Report-level exclusions come first, then price, then flag."""
    ks, c = [], {"frame": 0, "backcast": 0, "shutdown": 0, "release": 0, "price": 0, "flag": 0, "other": 0}
    for k in range(m.M):
        d = m.dates[k]
        if d < first or d > last:
            continue
        c["frame"] += 1
        if k == 0:
            c["other"] += 1
            continue
        if m.excl[k] and not (m.cause[k] == "backcast" and admit_backcast):
            c[m.cause[k]] += 1
            continue
        w = W[k]
        if w is None or w["reason"] == "beyond_data_end":
            c["other"] += 1
            continue
        if w["ret"] is None:
            c["price"] += 1
            continue
        if flag_ranges and not include_flagged and not mut("ignore_flag") and (in_ranges(w["a"], flag_ranges) or in_ranges(w["b"], flag_ranges)):
            c["flag"] += 1
            continue
        if pred is not None and not pred(k, w):
            c["other"] += 1
            continue
        ks.append(k)
    return ks, c


def xs_ys(m, W, ks, book, h=1):
    sh = 1 if mut("pair_next") else -1 if mut("pair_prev") else 0
    if sh:
        kk = [k for k in ks if 0 <= k + sh < m.M and W[k + sh] is not None and W[k + sh]["ret"] is not None]
        return [m.dn(book, k, h) for k in kk], [W[k + sh]["ret"] for k in kk]
    return [m.dn(book, k, h) for k in ks], [W[k]["ret"] for k in ks]


def placebo_scale(x, y, draws=PLACEBO_DRAWS, seed=SEED):
    """C-092: effective n demonstrated, not declared. `draws` random-sign placebos: R_k is multiplied by +1 or -1 (bit 1 = +1) from
    random.Random(seed).getrandbits(1), one bit per week in report order, draw after draw, X held fixed. Returns the population SD of the draws'
    Pearson r. Validity: X fixed, and R unpredictable and sign-symmetric given its magnitude."""
    n = len(x)
    mx = sum(x) / n
    xc = [a - mx for a in x]
    sxx = sum(a * a for a in xc)
    syy0 = sum(b * b for b in y)
    w = [a * b for a, b in zip(xc, y)]
    rng = random.Random(seed + 1 if mut("placebo_seed") else seed)
    gb = rng.getrandbits
    rs = []
    for _ in range(draws):
        sg = [1 if gb(1) else -1 for _ in range(n)]
        sy = sum(si * b for si, b in zip(sg, y))
        sxy = sum(si * wi for si, wi in zip(sg, w))
        syy = syy0 - sy * sy / n
        rs.append(sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else 0.0)
    mu = sum(rs) / len(rs)
    return math.sqrt(sum((r - mu) ** 2 for r in rs) / len(rs))


def sign_vector(n=20, seed=SEED):
    rng = random.Random(seed)
    return [1 if rng.getrandbits(1) else -1 for _ in range(n)]


PINNED_SIGNS = [1, 1, -1, -1, 1, -1, 1, -1, 1, 1, 1, 1, -1, 1, -1, 1, -1, 1, -1, -1]      # G16: first 20 signs of random.Random(20261018).getrandbits(1)


def primary_stats(x, y, draws=PLACEBO_DRAWS):
    n = len(x)
    r, rho = pearson(x, y), spearman(x, y)
    s_iid = 1.0 / math.sqrt(n)
    s_pl = placebo_scale(x, y, draws)
    s_used = s_iid if mut("scale_iid_only") else max(s_iid, s_pl)
    z = r / s_used
    return {"n": n, "pearson": r, "spearman": rho, "s_iid": s_iid, "s_placebo": s_pl, "s_used": s_used, "z": z, "p": phi_p(z)}


HOLM_ALPHAS = (0.025, 0.05)


def holm(ps):
    """Holm over a family of two. ps: {market: p}. Order by p (ties by market name); reject the smaller if p <= 0.025, and only then the other if
    p <= 0.05. Returns {market: (rank, alpha, reject)}."""
    order = sorted(ps, key=lambda k: (ps[k], k))
    out, still = {}, True
    for i, mk in enumerate(order):
        if mut("holm_bonferroni"):
            alpha, rej = 0.025, ps[mk] <= 0.025
        else:
            alpha = HOLM_ALPHAS[i]
            rej = ps[mk] <= alpha and (still or mut("holm_no_stop"))
            still = still and rej
        out[mk] = (i + 1, alpha, rej)
    return out


def verdict_text(market, st, hz_reject, sign_check):
    """Section 5, in order; AGAINST takes precedence."""
    r, rho, n, z, s = st["pearson"], st["spearman"], st["n"], st["z"], st["s_used"]
    if abs(z) < Z95:
        return "AGAINST (no lead larger than %s detected, 95%%)" % f(abs(r) + Z95 * s, 3)
    band = Z95 / math.sqrt(n)
    if hz_reject and (rho > 0) == (r > 0) and abs(rho) >= band:
        if market == "WTI" and sign_check == "disagree":
            return "INCONCLUSIVE (Holm rejects and Spearman agrees; WTI futures and spot disagree in sign)"
        return "SUPPORTS (spot proxy)" if market == "BRENT" else "SUPPORTS"
    why = []
    if not hz_reject:
        why.append("|z| >= 1.96 without Holm rejection")
    else:
        why.append("Holm rejected but Spearman has the other sign or is below its band")
    return "INCONCLUSIVE (%s)" % "; ".join(why)


def blocks_a(m, W, ks, book, h, lvl0):
    """Form (a) one_week_left: X = N_k - N_{k-h}, Y = R_k, for every included k with k-h at or after the first admissible level."""
    kk = [k for k in ks if k - h >= lvl0]
    return [m.dn(book, k, h) for k in kk], [W[k]["ret"] for k in kk]


def blocks_b(m, W, ks, book, h, lvl0):
    """Form (b) nonoverlap_blocks: blocks of h consecutive reports stepping by h. X_j = the h-week change ending at the block's first report;
    Y_j compounds the h post-release returns. A block holding an excluded week is dropped. Returns (xs, ys, first-report indexes)."""
    kset = set(ks)
    if not ks:
        return [], [], []
    s0 = min(k for k in ks if k - h >= lvl0) if any(k - h >= lvl0 for k in ks) else None
    xs, ys, st = [], [], []
    if s0 is None:
        return xs, ys, st
    step = 1 if mut("blocks_overlap") else h
    last = max(ks)
    s_ = s0
    while s_ + h - 1 <= last:
        blk = range(s_, s_ + h)
        if all(k in kset for k in blk) and s_ - h >= lvl0:
            g = 1.0
            for k in blk:
                g *= 1.0 + W[k]["ret"]
            xs.append(m.dn(book, s_, h))
            ys.append(g - 1.0)
            st.append(s_)
        s_ += step
    return xs, ys, st


def bar_for(n_blocks):
    return Z95 / math.sqrt(n_blocks) if n_blocks > 0 else None


# ----------------------------------------------------------------------------------------------------------------------
# THE COMPUTATION: one pass from inputs to every table
# ----------------------------------------------------------------------------------------------------------------------
WINDOW_KINDS = ("post_release", "post_measurement", "same_week", "prev_week", "post_next_report")
EX2020 = (D("2020-03-01"), D("2020-06-30"))


class Inputs:
    """Everything the computation reads, so that the selftest can hand it a synthetic world."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


def pct(v):
    return None if v is None else v * 100.0


def make_wti_market(inp, cfg):
    dates = list(inp.cftc["fo"])
    nets = {b: [inp.cftc[b][d][0] - inp.cftc[b][d][1] for d in dates] for b in BOOKS}
    rel, rule, src = [], [], []
    for d in dates:
        nom, r, ru = cftc_release(d, inp.hol_cftc, inp.overrides)
        if ru == "override":
            sr = inp.overrides[d][1]
        else:
            sr = "cftc.gov release schedule rule (Friday 3:30 p.m. ET; a federal holiday moves it to the next business day after the Friday)"
        if cfg.backcast_label_last is not None and d <= cfg.backcast_label_last:
            ru, sr = "backcast_not_public", "backcast: positions up to 2009-08-25 were first published on 2009-10-20 (spec 2.1)"
        rel.append(r)
        rule.append(ru)
        src.append(sr)
    m = Mkt("WTI", dates, nets, rel, rule, src)
    m.nominal = [friday_of(d) for d in dates]
    mark_exclusions(m, cfg)
    return m


def make_brent_market(inp, cfg):
    led = inp.brent
    dates = [r["date"] for r in led]
    nets = {"fo": [r["fo_net"] for r in led], "co": [r["co_net"] for r in led]}
    rel, rule, src = [], [], []
    for d in dates:
        nom, r, ru = ice_release(d, inp.bh)
        rel.append(r)
        rule.append(ru)
        src.append("ICE CoT_Notes: Friday 18:30 London" + ("; English bank holiday (gov.uk, computed Easter and proclaimed days) moves it" if ru != "friday_nominal" else ""))
    m = Mkt("BRENT", dates, nets, rel, rule, src)
    m.nominal = [friday_of(d) for d in dates]
    mark_exclusions(m, cfg)
    return m


class Res:
    pass


def compute_all(inp, cfg, say=print, draws=PLACEBO_DRAWS):
    R = Res()
    R.inp, R.cfg = inp, cfg
    R.wti, R.brent = make_wti_market(inp, cfg), make_brent_market(inp, cfg)
    H = inp.nymex_hol
    U = set(inp.r1) | set(inp.r2)
    lastU = max(U)
    R.U, R.lastU = U, lastU
    is_bd_A = lambda d: d in U and d not in H
    ref_wti = lambda d: is_bd_A(d) if d <= lastU else (d.weekday() < 5 and d not in H)
    # The calendar must reach past the last window: beyond the last EIA print the trading days are weekdays minus the holiday set. (Post-registration
    # fix, 18 Oct: the span used to stop at the March 2024 delivery month and missed the 2024-03-20 expiry.)
    span = tuple(inp.exp_span)
    if mut("exp_truncated"):
        y1, m1 = span[2], span[3] - 2
        span = span[:2] + ((y1, m1) if m1 >= 1 else (y1 - 1, m1 + 12))
    R.exp_list = fut_expiries(ref_wti, *span)
    R.bd_A = ref_wti
    R.bd_union = lambda d: (d in U) if d <= lastU else d.weekday() < 5
    R.fut = FuturesBasis(inp.r1, inp.r2, H, [e for _, (e, _c) in R.exp_list], ref_wti)
    R.spot_w = SpotBasis(SPOT_WTI, inp.rwtc, ref_wti, ignore=H)
    ref_b = lambda d: d.weekday() < 5 and d not in inp.bh
    R.spot_b = SpotBasis(SPOT_BRENT, inp.rbrte, ref_b)
    R.WF = {k: compute_windows(R.wti, R.fut, k, fallback=R.spot_w) for k in WINDOW_KINDS}
    R.WS = {k: compute_windows(R.wti, R.spot_w, k) for k in WINDOW_KINDS}
    R.WB = {k: compute_windows(R.brent, R.spot_b, k) for k in WINDOW_KINDS}
    wti, brent = R.wti, R.brent
    lvl_rt = wti.idx[cfg.realtime_level_first]
    R.lvl_rt = lvl_rt
    k_lf = last_complete(wti, R.WF["post_release"])
    k_ls = last_complete(wti, R.WS["post_release"])
    k_lb = last_complete(brent, R.WB["post_release"])
    R.last_fut, R.last_spot_w, R.last_brent = wti.dates[k_lf], wti.dates[k_ls], brent.dates[k_lb]
    flags = tuple(cfg.flag_ranges)
    R.flags = flags

    # --- samples (counts first: the bars are printed before any correlation is computed)
    S = {}
    S["wti_fut_primary"] = select(wti, R.WF["post_release"], cfg.wti_pool_first if mut("primary_admit_backcast") else cfg.wti_first, R.last_fut,
                                  admit_backcast=mut("primary_admit_backcast"))
    S["wti_fut_pooled"] = select(wti, R.WF["post_release"], cfg.wti_pool_first, R.last_fut, admit_backcast=True)
    S["wti_fut_backcast"] = select(wti, R.WF["post_release"], cfg.wti_pool_first, cfg.backcast_last, admit_backcast=True)
    S["wti_spot_primary"] = select(wti, R.WS["post_release"], cfg.wti_first, R.last_fut)
    S["wti_spot_ext"] = select(wti, R.WS["post_release"], wti.dates[wti.idx[R.last_fut] + 1], R.last_spot_w)
    S["wti_spot_all"] = select(wti, R.WS["post_release"], cfg.wti_first, R.last_spot_w)
    S["brent_primary"] = select(brent, R.WB["post_release"], cfg.brent_first, R.last_brent, flag_ranges=flags)
    R.S = S
    nF, nB = len(S["wti_fut_primary"][0]), len(S["brent_primary"][0])
    R.bar_lines = []
    say("-- the section 4 bars, printed before any correlation is computed --")
    for lab, n in (("WTI primary h=1", nF), ("Brent primary h=1", nB)):
        for tag, num in (("5%% bar 1.96/sqrt(n)", Z95), ("Holm first bar 2.2414/sqrt(n)", 2.2414), ("80%% power |r| (2.8/sqrt(n))", 2.8016)):
            line = "  %-20s n=%d  %-30s %s" % (lab, n, tag % () if "%%" in tag else tag, f(num / math.sqrt(n), 3))
            R.bar_lines.append(line)
            say(line)
    for h in (4, 13, 26):
        for lab, n in (("WTI", nF), ("Brent", nB)):
            say("  %-20s T=%d  h=%-2d blocks<=%d  bar 1.96/sqrt(blocks) <= %s" % (lab, n, h, n // h, f(Z95 / math.sqrt(max(n // h, 1)), 3)))

    # --- the two pre-registered correlations, once
    x, y = xs_ys(wti, R.WF["post_release"], S["wti_fut_primary"][0], "fo")
    xb, yb = xs_ys(brent, R.WB["post_release"], S["brent_primary"][0], "fo")
    R.stW, R.stB = primary_stats(x, y, draws), primary_stats(xb, yb, draws)
    hz = holm({"WTI": R.stW["p"], "BRENT": R.stB["p"]})
    R.holm = hz
    xs_, ys_ = xs_ys(wti, R.WS["post_release"], S["wti_spot_primary"][0], "fo")
    R.spot_r = pearson(xs_, ys_)
    R.sign_check = "agree" if (R.spot_r > 0) == (R.stW["pearson"] > 0) else "disagree"
    R.verdW = verdict_text("WTI", R.stW, hz["WTI"][2], R.sign_check)
    R.verdB = verdict_text("BRENT", R.stB, hz["BRENT"][2], "")
    return R


def load_inputs(out_dir=OUT_DEFAULT, vint_dir=VINT_DEFAULT, root=ROOT):
    raw = os.path.join(out_dir, "raw")
    for fn in (os.path.join(vint_dir, "eia_RCLC1d.xls"), os.path.join(vint_dir, "eia_RCLC2d.xls")):
        if not os.path.exists(fn):
            raise DataError("%s is missing: run `python3 bin/cot_horizons.py fetch` first" % tilde(fn))
    r1, k1, _ = read_eia(os.path.join(vint_dir, "eia_RCLC1d.xls"))
    r2, k2, _ = read_eia(os.path.join(vint_dir, "eia_RCLC2d.xls"))
    if (k1, k2) != ("RCLC1", "RCLC2") and not (k1.startswith("Data 1") or "RCLC" in k1):
        raise DataError("unexpected EIA futures workbook keys")
    rwtc = read_eia(os.path.join(root, "data", "cftc_cot", "raw", "eia_RWTCd.xls"))[0]
    rbrte = read_eia(os.path.join(root, "data", "ice_brent", "raw", "eia_RBRTEd.xls"))[0]
    special = open(os.path.join(raw, "cftc_special_announcements.html"), "rb").read()
    sched = open(os.path.join(raw, "cftc_release_schedule.html"), "rb").read()
    bhj = json.load(open(os.path.join(raw, "gov_uk_bank_holidays.json"), encoding="utf-8"))
    bh, bh_years, bh_bad = uk_holidays(bhj)
    return Inputs(cftc=load_cftc(raw), brent=load_brent_ledger(os.path.join(root, "data", "ice_brent", "brent_ledger.csv")), r1=r1, r2=r2,
                  rwtc=rwtc, rbrte=rbrte, special=special, sched=sched, bhj=bhj, bh=bh, bh_years=bh_years, bh_bad=bh_bad,
                  hol_cftc=us_federal_holidays_span(2004, 2028) | set(CLOSURE_DAYS), overrides=build_overrides(special),
                  nymex_hol=NYMEX_HOLIDAYS, exp_span=(2006, 1, 2024, 5), root=root, out_dir=out_dir, vint_dir=vint_dir)


def real_cfg():
    return Cfg(flag_ranges=sister_suspect_ranges())


# ----------------------------------------------------------------------------------------------------------------------
# TABLE ROWS
# ----------------------------------------------------------------------------------------------------------------------
def fin(v, nd):
    return "" if v is None or (isinstance(v, float) and not math.isfinite(v)) else f(v, nd)


def drow(market, book, basis, window, h, form, sample, xs, ys, first, last, nblocks, note="", bar_n=None):
    n = len(xs)
    r = rho = None
    if n >= 3 and len(set(xs)) > 1 and len(set(ys)) > 1:
        r, rho = pearson(xs, ys), spearman(xs, ys)
    bar = bar_for(nblocks if bar_n is None else bar_n)
    exceeds = "yes" if (r is not None and bar is not None and abs(r) > round(bar, 3)) else "no"
    note = ("role=descriptive (no verdict); exceeds_own_bar=%s; %s" % (exceeds, note)).strip()
    return [market, book, basis, window, str(h), form, sample, iso(first) if first else "", iso(last) if last else "", str(n), str(nblocks),
            fin(r, 3), fin(rho, 3), fin(bar, 3), note]


def sample_rows(rows, market, m, Wset, basis_name, books, sample, first, last, lvl0, windows=("post_release",), horizons=(1, 4, 13),
                admit_backcast=False, flag_ranges=(), include_flagged=False, pred=None, skip=(), note0=""):
    for wk in windows:
        ks, c = select(m, Wset[wk], first, last, admit_backcast=admit_backcast, flag_ranges=flag_ranges, include_flagged=include_flagged, pred=pred)
        if not ks:
            continue
        note = ("%s frame=%d; left out: backcast %d, shutdown %d, release %d, price %d, flag %d, other %d" %
                (note0, c["frame"], c["backcast"], c["shutdown"], c["release"], c["price"], c["flag"], c["other"])).strip()
        for book in books:
            for h in horizons:
                if h == 1:
                    if (wk, book, sample, 1) in skip:
                        continue
                    xs, ys = xs_ys(m, Wset[wk], ks, book)
                    rows.append(drow(market, book, basis_name, wk, 1, "weekly", sample, xs, ys, m.dates[ks[0]], m.dates[ks[-1]], len(xs), note))
                elif wk == "post_release":
                    xa, ya = blocks_a(m, Wset[wk], ks, book, h, lvl0)
                    kk = [k for k in ks if k - h >= lvl0]
                    rows.append(drow(market, book, basis_name, wk, h, "one_week_left", sample, xa, ya, m.dates[kk[0]] if kk else None,
                                     m.dates[kk[-1]] if kk else None, len(xa) // h, note, bar_n=len(ks) if mut("bar_from_T") else None))
                    xb, yb, st = blocks_b(m, Wset[wk], ks, book, h, lvl0)
                    rows.append(drow(market, book, basis_name, wk, h, "nonoverlap_blocks", sample, xb, yb, m.dates[st[0]] if st else None,
                                     m.dates[st[-1] + h - 1] if st else None, len(xb), note, bar_n=c["frame"] if mut("bar_from_T") else None))


def descriptive_rows(R):
    wti, brent, cfg = R.wti, R.brent, R.cfg
    rows = []
    lvl = R.lvl_rt
    ex20 = lambda k, w: not (EX2020[0] <= w["a"] <= EX2020[1])
    skip_primary = {("post_release", "fo", "primary", 1)}
    # WTI, futures basis
    sample_rows(rows, "WTI", wti, R.WF, FUT_WTI, BOOKS, "primary", cfg.wti_first, R.last_fut, lvl, windows=WINDOW_KINDS, skip=skip_primary)
    sample_rows(rows, "WTI", wti, R.WF, FUT_WTI, BOOKS, "pooled_2006_2024", cfg.wti_pool_first, R.last_fut, 0, horizons=(1,), admit_backcast=True,
                note0="n_before_exclusions=%d;" % R.S["wti_fut_pooled"][1]["frame"])
    sample_rows(rows, "WTI", wti, R.WF, FUT_WTI, BOOKS, "backcast_2006_2009", cfg.wti_pool_first, cfg.backcast_last, 0, horizons=(1,), admit_backcast=True)
    sample_rows(rows, "WTI", wti, R.WF, FUT_WTI, BOOKS, "excl_mar_jun_2020", cfg.wti_first, R.last_fut, lvl, horizons=(1,), pred=ex20)
    # WTI, spot basis
    sample_rows(rows, "WTI", wti, R.WS, SPOT_WTI, BOOKS, "spot_primary_window", cfg.wti_first, R.last_fut, lvl, windows=WINDOW_KINDS)
    sample_rows(rows, "WTI", wti, R.WS, SPOT_WTI, BOOKS, "spot_extension", wti.dates[wti.idx[R.last_fut] + 1], R.last_spot_w, lvl, horizons=(1,))
    sample_rows(rows, "WTI", wti, R.WS, SPOT_WTI, BOOKS, "spot_all_realtime", cfg.wti_first, R.last_spot_w, lvl, horizons=(1,))
    sample_rows(rows, "WTI", wti, R.WS, SPOT_WTI, BOOKS, "excl_mar_jun_2020", cfg.wti_first, R.last_fut, lvl, horizons=(1,), pred=ex20)
    # Brent, spot proxy
    flags = R.flags
    sample_rows(rows, "BRENT", brent, R.WB, SPOT_BRENT, BOOKS, "primary", cfg.brent_first, R.last_brent, 0, windows=WINDOW_KINDS, flag_ranges=flags,
                skip=skip_primary)
    sample_rows(rows, "BRENT", brent, R.WB, SPOT_BRENT, BOOKS, "incl_flagged_windows", cfg.brent_first, R.last_brent, 0, horizons=(1,),
                flag_ranges=flags, include_flagged=True)
    uk = lambda k, w: brent.rule[k] != "uk_holiday_assumed" and (k + 1 >= brent.M or brent.rule[k + 1] != "uk_holiday_assumed")
    sample_rows(rows, "BRENT", brent, R.WB, SPOT_BRENT, BOOKS, "excl_uk_holiday_weeks", cfg.brent_first, R.last_brent, 0, horizons=(1,),
                flag_ranges=flags, pred=uk)
    sample_rows(rows, "BRENT", brent, R.WB, SPOT_BRENT, BOOKS, "excl_mar_jun_2020", cfg.brent_first, R.last_brent, 0, horizons=(1,), flag_ranges=flags, pred=ex20)
    return rows


def plot26_rows(R):
    rows = []
    h = 26
    for market, m, W, basis, last, first, lvl, flags in (
            ("WTI", R.wti, R.WS, SPOT_WTI, R.last_fut, R.cfg.wti_first, R.lvl_rt, ()),
            ("WTI", R.wti, R.WF, FUT_WTI, R.last_fut, R.cfg.wti_first, R.lvl_rt, ()),
            ("BRENT", R.brent, R.WB, SPOT_BRENT, R.last_brent, R.cfg.brent_first, 0, R.flags)):
        ks, _c = select(m, W["post_release"], first, last, flag_ranges=flags)
        xs, ys, st = blocks_b(m, W["post_release"], ks, "fo", h, lvl)
        band = bar_for(len(xs))
        sp = {"WTI": R.spot_w, "BRENT": R.spot_b}[market]
        for j, s0 in enumerate(st):
            ys0 = ye = ""
            yr = ""
            if basis != FUT_WTI:
                ys0, ye, yr = f(sp.s[W["post_release"][s0]["a"]], 2), f(sp.s[W["post_release"][s0 + h - 1]["b"]], 2), f(pct(ys[j]), 3)
            rows.append([market, "fo", basis, str(j + 1), iso(m.dates[s0]), iso(m.dates[s0 + h - 1]), str(xs[j]), ys0, ye, yr, f(band, 3)])
    return rows


def panel_rows(R):
    rows = []
    for market, m, WP, WM, flags in (("WTI", R.wti, R.WS["post_release"], R.WS["post_measurement"], ()),
                                    ("BRENT", R.brent, R.WB["post_release"], R.WB["post_measurement"], R.flags)):
        for k, d in enumerate(m.dates):
            w, wm = WP[k], WM[k]
            reason = m.excl[k]
            flagged = False
            if w is not None and w["a"] is not None and flags and (in_ranges(w["a"], flags) or in_ranges(w["b"], flags)):
                flagged = True
            if not reason:
                if k == 0:
                    reason = "no_prior_report"
                elif w is None:
                    reason = "no_next_report"
                elif w["reason"]:
                    reason = w["reason"]
                elif flagged:
                    reason = "flagged_print"
            rows.append([market, iso(d), iso(m.rel[k]), m.rule[k], str(m.dn("fo", k)) if k else "", str(m.dn("co", k)) if k else "",
                         iso(w["a"]) if w and w["a"] else "", iso(w["b"]) if w and w["b"] else "",
                         fin(pct(w["ret"]), 4) if w and w["ret"] is not None else "", fin(pct(wm["ret"]), 4) if wm and wm["ret"] is not None else "",
                         FLAG_NAME if flagged else "", reason])
    return rows


def release_rows(R):
    rows = []
    for market, m in (("WTI", R.wti), ("BRENT", R.brent)):
        for k, d in enumerate(m.dates):
            rows.append([market, iso(d), iso(m.nominal[k]), iso(m.rel[k]), m.rule[k], m.src[k]])
    return rows


def roll_rows(R):
    U = R.U
    union_exp = {ym: expiry_date(ym[0], ym[1], R.bd_union) for ym, _ in R.exp_list}
    rows = []
    for ym, (e, case) in R.exp_list:
        rows.append(["%04d-%02d" % ym, iso(e), case, "yes" if union_exp[ym][0] != e else "no"])
    return rows


def futures_local_rows(R):
    rows = []
    wti = R.wti
    for k, d in enumerate(wti.dates):
        w = R.WF["post_release"][k]
        def r_(kind):
            x = R.WF[kind][k]
            return fin(pct(x["ret"]), 4) if x is not None and x["ret"] is not None else ""
        rows.append([iso(d), iso(w["a"]) if w and w["a"] else "", iso(w["b"]) if w and w["b"] else "", w["contract"] if w else "",
                     r_("post_release"), r_("post_measurement"), r_("same_week"), r_("prev_week")])
    return rows


def primary_rows(R, frozen=None):
    frozen = frozen or {}
    rows = []
    for market, st, ks_c, basis, first_, m, sc, flags in (("WTI", R.stW, R.S["wti_fut_primary"], FUT_WTI, R.cfg.wti_first, R.wti, R.sign_check, ()),
                                                         ("BRENT", R.stB, R.S["brent_primary"], SPOT_BRENT, R.cfg.brent_first, R.brent, "", R.flags)):
        ks, c = ks_c
        hz = R.holm[market]
        pool_back = R.S["wti_fut_pooled"][1]["frame"] - R.S["wti_fut_primary"][1]["frame"] if market == "WTI" else 0
        verdict = R.verdW if market == "WTI" else R.verdB
        rows.append([market, "fo", basis, "post_release", iso(m.dates[ks[0]]), iso(m.dates[ks[-1]]), str(st["n"]), str(pool_back), str(c["shutdown"]),
                     str(c["release"]), str(c["price"]), str(c["flag"]), f(st["pearson"], 3), f(st["spearman"], 3), f(st["s_iid"], 4),
                     f(st["s_placebo"], 4), f(st["s_used"], 4), f(st["z"], 3), f(st["p"], 4), str(hz[0]), f(hz[1], 3), "yes" if hz[2] else "no",
                     f(Z95 / math.sqrt(st["n"]), 3), sc, verdict,
                     frozen.get(market, "") if not mut("build_writes_frozen") else "2030-01-01"])
    return rows


# ----------------------------------------------------------------------------------------------------------------------
# GUARD FUNCTIONS: each returns a list of problems (empty = holds). The same function runs on the real data in `build` and on the synthetic
# world in `selftest`, where its mutant must make it return a problem.
# ----------------------------------------------------------------------------------------------------------------------
def g1_changes(m, ref):
    """G1: dn_book[k] equals the published first difference of the net, in contracts. ref = {book: {date: change}} from the committed ledgers."""
    bad = []
    for b in BOOKS:
        for k in range(1, m.M):
            d = m.dates[k]
            if d in ref[b] and m.dn(b, k) != ref[b][d]:
                bad.append("%s %s %s: dn=%s, ledger change=%s" % (m.name, b, d, m.dn(b, k), ref[b][d]))
                break
    return bad


def g2_post_release_start(m, W):
    """G2 (a code test): every post_start is strictly after the release date used, as dates."""
    bad = []
    for k in range(m.M):
        w = W[k]
        if w is None or w["a"] is None or m.excl[k]:
            continue
        if not w["a"] > m.rel[k]:
            bad.append("%s %s: post_start %s is not after release %s" % (m.name, m.dates[k], w["a"], m.rel[k]))
            break
    return bad


def g3_no_overlap(m, W, ks, blocks=None):
    """G3: post_end of report k equals post_start of the next report's window, for consecutive included reports; blocks are disjoint."""
    bad = []
    kset = set(ks)
    for k in ks:
        if k + 1 in kset and W[k]["b"] != W[k + 1]["a"]:
            bad.append("%s %s: post_end %s != next post_start %s" % (m.name, m.dates[k], W[k]["b"], W[k + 1]["a"]))
            break
    if blocks:
        st, h = blocks
        for i in range(len(st) - 1):
            if st[i] + h > st[i + 1]:
                bad.append("%s: blocks starting %s and %s overlap (h=%d)" % (m.name, m.dates[st[i]], m.dates[st[i + 1]], h))
                break
    return bad


def g4_honest_bar(rows):
    """G4: bar == 1.96/sqrt(n_blocks) with n_blocks <= floor(T/h); T is the number of reports in the frame (carried in the `note` as frame=)."""
    bad = []
    for r in rows:
        h, n, nb, bar = int(r[4]), int(r[9]), int(r[10]), r[13]
        if bar == "":
            continue
        if abs(float(bar) - round(Z95 / math.sqrt(nb), 3)) > 1e-9:
            bad.append("%s %s h=%d %s: bar %s != 1.96/sqrt(%d)" % (r[0], r[6], h, r[5], bar, nb))
            break
        mt = re.search(r"frame=(\d+)", r[14])
        if mt and nb > int(mt.group(1)) // h:
            bad.append("%s %s h=%d %s: n_blocks %d > floor(T/h)" % (r[0], r[6], h, r[5], nb))
            break
    return bad


def g5_estimators(files):
    """G5: every table's header is exactly its allowlist and holds no banned column. files: {name: header}."""
    bad = []
    for name, hdr in files.items():
        try:
            check_header(name, hdr)
        except DataError as e:
            bad.append(str(e))
    return bad


def g8_ice_timing(m, W, bh):
    """G8: no Brent window starts on a print dated on the release day; a release on a bank-holiday Friday is the next London business day."""
    bad = g2_post_release_start(m, W)
    for k, d in enumerate(m.dates):
        fri = friday_of(d)
        if fri in bh:
            want = fri + dt.timedelta(days=1)
            while want.weekday() >= 5 or want in bh:
                want += dt.timedelta(days=1)
            if m.rel[k] != want:
                bad.append("%s: bank-holiday Friday %s released %s, expected %s" % (d, fri, m.rel[k], want))
                break
    return bad


def g9_roll(basis, m, W, ks, truth=None):
    """G9: at most one expiry per window (raised by the basis), prices > 0, and on a synthetic world the same contract at both ends."""
    bad = []
    for k in ks:
        w = W[k]
        if w is None or w["ret"] is None:
            continue
        e = basis.expiry_between(w["a"], w["b"])
        if not basis.exp or basis.exp[-1] < w["b"]:
            bad.append("%s: the roll calendar ends %s, before the window end %s" % (m.dates[k], basis.exp[-1] if basis.exp else None, w["b"]))
            break
        if truth is not None:
            tr = truth(w["a"], w["b"])
            if abs(tr - w["ret"]) > 1e-9:
                bad.append("%s: return %.6f is not the same-contract return %.6f" % (m.dates[k], w["ret"], tr))
                break
    return bad


def g11_futures_end(m, W, last_print, last_report=None):
    bad = []
    for k in range(m.M):
        w = W[k]
        if w and w["b"] is not None and w["b"] > last_print:
            bad.append("%s: futures window ends %s after the last print %s" % (m.dates[k], w["b"], last_print))
            break
    if last_report is not None:
        ks = [k for k in range(m.M) if W[k] is not None and W[k]["reason"] != "beyond_data_end"]
        if m.dates[max(ks)] != last_report:
            bad.append("last futures report is %s, expected %s" % (m.dates[max(ks)], last_report))
    return bad


def g12_real_time(m, S_primary, cfg, pooled_n, backcast_n, first_expected):
    """G12: the primary starts at first_expected, rows up to cfg.backcast_last are backcast and absent from the primary; pooled and backcast samples exist."""
    bad = []
    ks, c = S_primary
    if m.dates[ks[0]] != first_expected:
        bad.append("primary first_report is %s, expected %s" % (m.dates[ks[0]], first_expected))
    if any(m.dates[k] <= cfg.backcast_last for k in ks):
        bad.append("a backcast report is inside the primary")
    for k, d in enumerate(m.dates):
        if d <= cfg.backcast_last and m.excl[k] != "backcast_not_public":
            bad.append("%s is not marked backcast_not_public" % d)
            break
    if pooled_n is not None and pooled_n <= 0:
        bad.append("no pooled sample")
    if backcast_n is not None and backcast_n <= 0:
        bad.append("no backcast sample")
    return bad


def g13_flags(m, W, S_primary, flags, first, last):
    """G13: no included window touches a flagged print, and every flagged complete window in the frame is counted in n_excl_flag."""
    bad = []
    ks, c = S_primary
    for k in ks:
        w = W[k]
        if in_ranges(w["a"], flags) or in_ranges(w["b"], flags):
            bad.append("%s: an included window touches a flagged print" % m.dates[k])
            break
    n_touch = 0
    for k in range(1, m.M):
        w = W[k]
        if m.dates[k] < first or m.dates[k] > last or w is None or w["ret"] is None or m.excl[k]:
            continue
        if in_ranges(w["a"], flags) or in_ranges(w["b"], flags):
            n_touch += 1
    if c["flag"] != n_touch:
        bad.append("n_excl_flag=%d but %d windows in the frame touch a flagged print" % (c["flag"], n_touch))
    return bad


def g14_holm(fn):
    """G14: order and alphas; (0.03, 0.04) rejects neither; (0.02, 0.04) rejects both; (0.02, 0.06) rejects only the first."""
    bad = []
    r = fn({"WTI": 0.03, "BRENT": 0.04})
    if r["WTI"] != (1, 0.025, False) or r["BRENT"] != (2, 0.05, False):
        bad.append("(0.03, 0.04) -> %r" % (r,))
    r = fn({"WTI": 0.04, "BRENT": 0.02})
    if r["BRENT"] != (1, 0.025, True) or r["WTI"] != (2, 0.05, True):
        bad.append("(0.04, 0.02) -> %r" % (r,))
    r = fn({"WTI": 0.02, "BRENT": 0.06})
    if r["WTI"][2] is not True or r["BRENT"][2] is not False:
        bad.append("(0.02, 0.06) -> %r" % (r,))
    r = fn({"WTI": 0.04, "BRENT": 0.04})
    if r["WTI"][2] or r["BRENT"][2]:
        bad.append("(0.04, 0.04): the second test must not run when the first fails")
    return bad


def g16_placebo(stats_fn, x, y):
    """G16: s_used == max(1/sqrt(n), s_placebo); the RNG is exactly random.Random(20261018).getrandbits(1) (pinned first 20 signs)."""
    bad = []
    if sign_vector(20) != PINNED_SIGNS:
        bad.append("the first 20 placebo signs differ from the pinned vector")
    st = stats_fn(x, y)
    want = max(1.0 / math.sqrt(st["n"]), st["s_placebo"])
    if abs(st["s_used"] - want) > 1e-12:
        bad.append("s_used %.6f != max(1/sqrt(n), s_placebo) %.6f" % (st["s_used"], want))
    return bad


def g21_brent_net(ledger):
    """G21: fo_mm_net_chg equals the first difference of fo_mm_net on every row (the first row has no change)."""
    for i in range(1, len(ledger)):
        if ledger[i]["fo_chg"] != ledger[i]["fo_net"] - ledger[i - 1]["fo_net"]:
            return ["%s: fo_mm_net_chg %s != first difference %s" % (ledger[i]["date"], ledger[i]["fo_chg"], ledger[i]["fo_net"] - ledger[i - 1]["fo_net"])]
    return []


def g22_one_per_week(dates, accepted_non_tuesdays):
    bad = []
    seen = {}
    for d in dates:
        wk = week_key(d)
        if wk in seen:
            bad.append("two reports in ISO week %d-W%02d: %s and %s" % (wk[0], wk[1], seen[wk], d))
            break
        seen[wk] = d
    odd = [d for d in dates if d.weekday() != 1 and d not in accepted_non_tuesdays]
    if odd:
        bad.append("non-Tuesday report dates that are not accepted: %s" % ", ".join(iso(d) for d in odd[:5]))
    return bad


EXPECTED_TOP = frozenset(ALLOW) | {"README.md", "SOURCES.md", "raw"}
EXPECTED_RAW = frozenset(CFTC_FILES.values()) | {"cftc_release_schedule.html", "cftc_special_announcements.html", "cftc_press_release_7864-19.html",
                                                  "gov_uk_bank_holidays.json"}


def unexpected_files(out_dir):
    """Any file under the output directory that is not one of the published ones, and any csv anywhere under it with a header cell containing 'fut'
    (a copied local futures panel, say). Returns problem strings."""
    bad = []
    if not os.path.isdir(out_dir):
        return bad
    for dp, dn, fn in os.walk(out_dir):
        rel = os.path.relpath(dp, out_dir)
        for d in dn:
            if rel == "." and d != "raw":
                bad.append("unexpected directory %s" % d)
            elif rel != ".":
                bad.append("unexpected directory %s/%s" % (rel, d))
        for f_ in fn:
            ok = (f_ in EXPECTED_TOP) if rel == "." else (rel == "raw" and f_ in EXPECTED_RAW)
            if not ok:
                bad.append("unexpected file %s" % (f_ if rel == "." else rel + "/" + f_))
            if f_.endswith(".csv"):
                try:
                    with open(os.path.join(dp, f_), encoding="utf-8", errors="replace") as fh:
                        lines = [l for l in fh.read().splitlines() if not l.startswith("#")][:1]
                    if lines and any(FUT_HDR.search(c) for c in next(csv.reader(lines))):
                        bad.append("%s has a header cell containing 'fut'" % (f_ if rel == "." else rel + "/" + f_))
                except OSError:
                    pass
    return sorted(set(bad))


def g24_leak(headers, panel_rows=None, plot_rows=None, plot_basis_col=2, files_text=None, raw_prints=()):
    """G24: no committed header contains 'fut'; y_start/y_end are blank on futures bases; no raw print appears in any committed text."""
    bad = []
    for name, hdr in headers.items():
        for c in hdr:
            if FUT_HDR.search(c):
                bad.append("%s: header %r contains 'fut'" % (name, c))
    if plot_rows:
        for r in plot_rows:
            if r[plot_basis_col] == FUT_WTI and (r[7] or r[8] or r[9]):
                bad.append("plot26.csv: y fields filled on a futures basis")
                break
    for name, text in (files_text or {}).items():
        for pr in raw_prints:
            if re.search(r"(?<![\d.])" + re.escape(pr) + r"(?![\d])", text):
                bad.append("%s carries a raw print" % name)
                break
    return bad


def g23_pairing(m, W, ks, book="fo"):
    """G23 helper: the Pearson r of dn_k against the window of report k."""
    xs, ys = xs_ys(m, W, ks, book)
    return pearson(xs, ys)


# ----------------------------------------------------------------------------------------------------------------------
# CHECKPOINTS OF THE REAL DATA (spec 8.3)
# ----------------------------------------------------------------------------------------------------------------------
PINS_WTI = ((D("2026-09-08"), "fo", 111731), (D("2026-10-06"), "fo", 53598), (D("2026-10-06"), "co", 104491))
PINS_BRENT = ((D("2026-03-31"), "fo", 382072), (D("2026-03-31"), "co", 429853))
NON_TUESDAYS_PRE = frozenset(D(x) for x in ("2006-07-03", "2007-01-03", "2007-12-24", "2007-12-31", "2008-12-22", "2009-11-09"))
NON_TUESDAYS_POST = frozenset(D(x) for x in ("2012-12-24", "2012-12-31", "2017-07-03", "2018-12-24", "2018-12-31", "2020-12-21", "2023-07-03", "2025-11-10"))
NON_TUESDAYS_BRENT = frozenset(D(x) for x in ("2012-12-24", "2012-12-31", "2018-12-24", "2018-12-31"))      # the Mondays of the committed ledger
SPEC_SANITY = {0: (128, 218), -1: (96, 216), 1: (98, 218)}


def calendar_sanity(r1, r2, expiries, cal):
    """For each shift in {0, -1, +1} trading days: on the (shifted) expiry day E, |RCLC1(E+1) - RCLC2(E)| < |RCLC1(E+1) - RCLC1(E)|, E+1 being the
    next calendar date that has an RCLC1 print. Returns {shift: (holds, testable)}."""
    out = {}
    for sh in (0, -1, 1):
        tot = ok = 0
        for e in expiries:
            i = bisect.bisect_left(cal, e)
            if i >= len(cal) or cal[i] != e:
                continue
            i2 = i + sh
            if i2 < 0 or i2 >= len(cal):
                continue
            d = cal[i2]
            j = i2 + 1
            while j < len(cal) and cal[j] not in r1:
                j += 1
            if j >= len(cal) or d not in r1 or d not in r2:
                continue
            d1 = cal[j]
            tot += 1
            if abs(r1[d1] - r2[d]) < abs(r1[d1] - r1[d]):
                ok += 1
        out[sh] = (ok, tot)
    return out


def price_bridge(r1, r2, rwtc, U, exp_union, last_friday=D("2024-03-29")):
    """The spec's price-only bridge, on the plain union-of-prints calendar with no move-forward: grid of the first trading day strictly after each
    Friday from 2006-06-16 in 7-day steps to last_friday; a consecutive pair is dropped if RCLC2 at the start, the section 3.4 end price or RWTC at
    either end is missing or not positive. Returns the counts and the correlation of the two returns (prices only, no position)."""
    fr = D("2006-06-16")
    grid = []
    while fr <= last_friday:
        d = fr + dt.timedelta(days=1)
        while d not in U:
            d += dt.timedelta(days=1)
        grid.append(d)
        fr += dt.timedelta(days=7)
    ex = sorted(exp_union)
    rf, rs, starts = [], [], []
    miss = nonpos = futdrop = 0
    for a, b in zip(grid, grid[1:]):
        e = None
        i = bisect.bisect_left(ex, a)
        if i < len(ex) and ex[i] < b:
            e = ex[i]
        pa = r2.get(a)
        pb = (r1 if e is not None else r2).get(b)
        sa, sb = rwtc.get(a), rwtc.get(b)
        if pa is None or pb is None or pa <= 0 or pb <= 0:
            futdrop += 1
            continue
        if sa is None or sb is None:
            miss += 1
            continue
        if sa <= 0 or sb <= 0:
            nonpos += 1
            continue
        rf.append(pb / pa - 1)
        rs.append(sb / sa - 1)
        starts.append(a)
    out = {"grid": len(grid), "pairs": len(rf), "miss": miss, "nonpos": nonpos, "futdrop": futdrop, "r": pearson(rf, rs),
           "sd_f": math.sqrt(sum((v - sum(rf) / len(rf)) ** 2 for v in rf) / len(rf)),
           "sd_s": math.sqrt(sum((v - sum(rs) / len(rs)) ** 2 for v in rs) / len(rs))}
    keep = [i for i, a in enumerate(starts) if not (EX2020[0] <= a <= EX2020[1])]
    out["r_ex2020"], out["n_ex2020"] = pearson([rf[i] for i in keep], [rs[i] for i in keep]), len(keep)
    return out


def legacy_leadlag(dates, N, P, split=D("2024-01-01")):
    """The legacy lead-lag method of bin/pull_cftc_cot.py and bin/pull_ice_brent_cot.py: the percent change of the Tuesday print over the week,
    correlated with the same, next and previous week's change in net. Returns {tag: (n, pearson, spearman)}."""
    t0 = max(1, next(i for i, d in enumerate(dates) if d >= split))
    ts = list(range(t0, len(dates)))
    dn = {t: N[t] - N[t - 1] for t in ts}
    ret = {t: ((P[t] - P[t - 1]) / P[t] if mut("legacy_base") else P[t] / P[t - 1] - 1) for t in range(1, len(dates))}
    out = {}
    for tag, shift in (("same", 0), ("next", 1), ("prev", -1)):
        tt = [t for t in ts if 1 <= t + shift < len(dates)]
        x = [dn[t] for t in tt]
        y = [ret[t + shift] for t in tt]
        out[tag] = (len(tt), pearson(x, y), pearson(ranks(x), ranks(y)))
    return out


def git_show(commit, path):
    r = subprocess.run(["git", "show", "%s:%s" % (commit, path)], cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8")


def parse_leadlag_text(text):
    lines = [l for l in text.splitlines() if l and not l.startswith("#")]
    rd = list(csv.reader(lines))
    return [dict(zip(rd[0], r)) for r in rd[1:]]


LEGACY_COMMIT = "768a26f"


def carry_forward_dates(r1, r2):
    u = sorted(set(r1) | set(r2))
    out = []
    for prev, d in zip(u, u[1:]):
        if d in r1 and d in r2 and prev in r1 and prev in r2 and r1[d] == r1[prev] and r2[d] == r2[prev]:
            out.append(d)
    return out


def legacy_rows(inp):
    """Recompute the legacy lead-lag rows from the committed ledgers (futures-only and combined) for WTI and Brent."""
    w_hdr, w_rows, _ = read_table(os.path.join(inp.root, "data", "cftc_cot", "wti_ledger.csv"))
    wd = [D(r["report_date"]) for r in w_rows]
    wp = [float(r["price_usd_per_bbl"]) for r in w_rows]
    b_hdr, b_rows, _ = read_table(os.path.join(inp.root, "data", "ice_brent", "brent_ledger.csv"))
    bd = [D(r["report_date"]) for r in b_rows]
    bp = [float(r["price_usd_per_bbl"]) for r in b_rows]
    out = {}
    for kind, col in (("fo", "fo_mm_net"), ("combined", "co_mm_net")):
        out[("wti", kind)] = legacy_leadlag(wd, [int(r[col]) for r in w_rows], wp)
        out[("brent", kind)] = legacy_leadlag(bd, [int(r[col]) for r in b_rows], bp)
    return out, w_rows


def legacy_expected(commit):
    """{(contract, report_type): {tag: (n, pearson, spearman)}} from `git show commit:<path>` for the two lead-lag files, or None."""
    res = {}
    for path in ("data/cftc_cot/leadlag.csv", "data/ice_brent/brent_leadlag.csv"):
        t = git_show(commit, path)
        if t is None:
            return None
        for r in parse_leadlag_text(t):
            res[(r["contract"], r["report_type"])] = {tag: (int(r["n_" + tag]), r["pearson_%s_pct" % tag], r["spearman_%s_pct" % tag]) for tag in ("same", "next", "prev")}
    return res


def legacy_match(got, want):
    bad = []
    for key, tags in want.items():
        for tag, (n, p_, sp) in tags.items():
            g = got[key][tag]
            if g[0] != n or f(g[1], 3) != p_ or f(g[2], 3) != sp:
                bad.append("%s %s %s: got n=%d r=%s rho=%s; file n=%d r=%s rho=%s" % (key[0], key[1], tag, g[0], f(g[1], 3), f(g[2], 3), n, p_, sp))
    return bad


class CheckList:
    def __init__(self):
        self.rows = []

    def add(self, cid, name, expected, observed, status):
        self.rows.append([cid, name, str(expected), str(observed), status])

    def fails(self):
        return [r for r in self.rows if r[4] == "FAIL"]


def real_checks(R, say=print):
    """Spec 8.3 checkpoints on the real data. Statuses: PASS, FAIL (hard), WARN, INFO. Raw futures prints go to stdout only."""
    inp, cfg, ck = R.inp, R.cfg, CheckList()
    wti, brent = R.wti, R.brent
    # --- positions
    for d, book, want in PINS_WTI:
        got = wti.N[book][wti.idx[d]]
        ck.add("P%d" % (len(ck.rows) + 1), "WTI managed-money net %s, %s" % (d, "futures only" if book == "fo" else "combined"), "{:,}".format(want), "{:,}".format(got),
               "PASS" if got == want else "FAIL")
    for d, book, want in PINS_BRENT:
        got = brent.N[book][brent.idx[d]]
        ck.add("P%d" % (len(ck.rows) + 1), "Brent managed-money net %s, %s (committed ledger)" % (d, "futures only" if book == "fo" else "combined"), "{:,}".format(want),
               "{:,}".format(got), "PASS" if got == want else "FAIL")
    n_rows = {b: len(inp.cftc[b]) for b in BOOKS}
    ds = list(inp.cftc["fo"])
    ck.add("D01", "CFTC report dates per book (067651)", ">= 1,062, first 2006-06-13", "fo %d, co %d, %s to %s" % (n_rows["fo"], n_rows["co"], ds[0], ds[-1]),
           "PASS" if n_rows["fo"] >= 1062 and n_rows["fo"] == n_rows["co"] and ds[0] == D("2006-06-13") else "FAIL")
    pre = [d for d in ds if d < D("2010-01-01")]
    ck.add("D02", "pre-2010 WTI report dates", 186, len(pre), "PASS" if len(pre) == 186 else "FAIL")
    nt_pre = frozenset(d for d in pre if d.weekday() != 1)
    nt_post = frozenset(d for d in ds if d >= D("2010-01-01") and d.weekday() != 1)
    ck.add("D03", "non-Tuesday dates before 2010", ", ".join(sorted(iso(d) for d in NON_TUESDAYS_PRE)), ", ".join(sorted(iso(d) for d in nt_pre)),
           "PASS" if nt_pre == NON_TUESDAYS_PRE else "FAIL")
    ck.add("D04", "non-Tuesday dates from 2010", ", ".join(sorted(iso(d) for d in NON_TUESDAYS_POST)), ", ".join(sorted(iso(d) for d in nt_post)),
           "PASS" if nt_post == NON_TUESDAYS_POST else "FAIL")
    bd_ = [r["date"] for r in inp.brent]
    ck.add("D05", "Brent ledger report dates (committed ledger)", "824 at commit 768a26f; more if refreshed", "%d, %s to %s" % (len(bd_), bd_[0], bd_[-1]),
           "PASS" if len(bd_) >= 824 and bd_[0] == D("2011-01-04") else "FAIL")
    # --- prices
    r1, r2 = inp.r1, inp.r2
    ck.add("F01", "RCLC1 and RCLC2 last date", "2024-04-05 both", "%s and %s" % (max(r1), max(r2)), "PASS" if max(r1) == max(r2) == D("2024-04-05") else "FAIL")
    say("RCLC1 last print %s = %s ; RCLC2 last print %s = %s (stdout only)" % (max(r1), f(r1[max(r1)], 2), max(r2), f(r2[max(r2)], 2)))
    s0 = D("2006-06-13")
    h1 = sorted(d for d in r1 if d >= s0 and d not in r2)
    h2 = sorted(d for d in r2 if d >= s0 and d not in r1)
    ck.add("F02", "dates with RCLC1 but no RCLC2, counted from 2006-06-13", 4, "%d: %s" % (len(h1), ", ".join(iso(d) for d in h1)), "PASS" if len(h1) == 4 else "FAIL")
    ck.add("F03", "dates with RCLC2 but no RCLC1, counted from 2006-06-13", 14, "%d: %s" % (len(h2), ", ".join(iso(d) for d in h2)), "PASS" if len(h2) == 14 else "FAIL")
    cf = [d for d in carry_forward_dates(r1, r2) if d >= s0]
    ck.add("F04", "carry-forward prints (both files repeat the previous print), 2006-2024", "spec author 13; second reviewer 9; a different count is not a failure",
           "%d: %s" % (len(cf), ", ".join(iso(d) for d in cf)), "INFO")
    # NYMEX holiday evidence
    H = inp.nymex_hol
    cfs = set(cf)
    ev = {"eia_carry_forward": [], "absent_both_files": [], "print_present_not_carry_forward": [], "outside_data": []}
    for d in sorted(H):
        if d < min(r1) or d > max(U := R.U):
            ev["outside_data"].append(d)
        elif d in cfs:
            ev["eia_carry_forward"].append(d)
        elif d not in r1 and d not in r2:
            ev["absent_both_files"].append(d)
        else:
            ev["print_present_not_carry_forward"].append(d)
    gen = set()
    for y in range(2005, 2027):
        gen |= nymex_rule_holidays(y)
    ck.add("F05", "NYMEX_HOLIDAYS equals the standard-rule holidays 2005-2026 (the set was generated that way)", "equal", "equal" if gen == set(H) else "differs",
           "PASS" if gen == set(H) else "FAIL")
    ck.add("F06", "NYMEX_HOLIDAYS entries evidenced by an EIA carried-forward print (evidence=eia_carry_forward)", "11 holidays in 2018-19", len(ev["eia_carry_forward"]),
           "INFO")
    ck.add("F07", "NYMEX_HOLIDAYS entries with neither a CME notice nor a carry-forward print (absent from both EIA files only; no CME notice was read)",
           "0 for a PASS", "%d entries, 2005-2024" % len(ev["absent_both_files"]), "WARN" if ev["absent_both_files"] else "PASS")
    ck.add("F08", "NYMEX_HOLIDAYS entries on which the files carry a distinct print (that print is ignored)", 0, len(ev["print_present_not_carry_forward"]),
           "PASS" if not ev["print_present_not_carry_forward"] else "WARN")
    # --- roll calendar
    exps = [x for x in R.exp_list if x[0] <= (2024, 3)]            # the spec's 219 (January 2006 to March 2024 delivery months)
    n_more = len(R.exp_list) - len(exps)
    n_exp = len(exps)
    e_apr20 = [e for ym, (e, c) in exps if e == D("2020-04-21")]
    ck.add("R01", "roll calendar expiries, Jan 2006 to Mar 2024, including 2020-04-21 (CLK20)", "219 including 2020-04-21", "%d%s; %d further delivery months (April and May 2024, last expiry %s) cover the final windows" % (n_exp, " including 2020-04-21" if e_apr20 else "", n_more, R.exp_list[-1][1][0]),
           "PASS" if n_exp == 219 and e_apr20 else "FAIL")
    U_ = R.U
    union_exp = {ym: expiry_date(ym[0], ym[1], R.bd_union)[0] for ym, _ in R.exp_list}
    diffs = [(ym, e) for ym, (e, c) in exps if union_exp[ym] != e]
    ck.add("R02", "months where the holiday-set calendar and the plain union-of-prints calendar give different expiries", "at least Nov 2018 and Dec 2018",
           "; ".join("%04d-%02d %s vs union %s" % (ym[0], ym[1], e, union_exp[ym]) for ym, e in diffs), "INFO")
    cal_union = sorted(U_)
    cal_set = sorted(d for d in U_ if d not in H)
    for lab, cal, ex in (("plain union-of-prints calendar", cal_union, [union_exp[ym] for ym, _ in exps]), ("holiday-set calendar", cal_set, [e for _, (e, c) in exps])):
        san = calendar_sanity(r1, r2, ex, cal)
        obs = "; ".join("shift %+d: %d of %d" % (sh, *san[sh]) for sh in (0, -1, 1))
        exp_ = "; ".join("shift %+d: %d of %d" % (sh, *SPEC_SANITY[sh]) for sh in (0, -1, 1)) if cal is cal_union else "shift 0 must beat both shifts"
        if cal is cal_union:
            ok_ = all(san[sh] == SPEC_SANITY[sh] for sh in SPEC_SANITY)
        else:
            ok_ = san[0][0] > san[-1][0] and san[0][0] > san[1][0]
        ck.add("R03", "calendar sanity, %s (E+1 is the next date with an RCLC1 print)" % lab, exp_, obs, "PASS" if ok_ else "WARN")
    # --- price-only bridge
    br = price_bridge(r1, r2, inp.rwtc, R.U, [union_exp[ym] for ym, _ in R.exp_list])
    ck.add("B01", "price-only bridge on the plain union-of-prints calendar (no move-forward)",
           "929 grid dates, 888 pairs (38 missing + 2 non-positive spot), r 0.893, SD 0.0513 futures and 0.0682 spot; excl. Mar-Jun 2020 r 0.955 n 872",
           "%d grid dates, %d pairs (%d missing + %d non-positive spot, %d futures-missing), r %s, SD %s futures and %s spot; excl. Mar-Jun 2020 r %s n %d" %
           (br["grid"], br["pairs"], br["miss"], br["nonpos"], br["futdrop"], f(br["r"], 3), f(br["sd_f"], 4), f(br["sd_s"], 4), f(br["r_ex2020"], 3), br["n_ex2020"]), "INFO")
    both = [k for k in range(wti.M) if R.WF["post_release"][k] and R.WF["post_release"][k]["ret"] is not None and R.WS["post_release"][k] and R.WS["post_release"][k]["ret"] is not None
            and not wti.excl[k] and cfg.wti_first <= wti.dates[k] <= R.last_fut]
    fx = [R.WF["post_release"][k]["ret"] for k in both]
    sx = [R.WS["post_release"][k]["ret"] for k in both]
    ck.add("B02", "builder's own bridge: post-release futures return vs spot return, primary window, pairs usable on both bases", "INFO", "n %d, r %s" % (len(both), f(pearson(fx, sx), 3)), "INFO")
    # --- n pins
    S = R.S
    fr = S["wti_fut_primary"][1]
    ck.add("N01", "WTI primary pairs before exclusions (first report 2009-09-08 after the OPEN-6 ruling)", "759 (spec: 760 before the ruling)", fr["frame"], "PASS" if fr["frame"] == 759 else "FAIL")
    ck.add("N02", "WTI primary pairs after the two shutdown blocks and their preceding reports", "738 (spec: 739 before the ruling)", fr["frame"] - fr["shutdown"],
           "PASS" if fr["frame"] - fr["shutdown"] == 738 else "FAIL")
    lag_dates = [d for k, d in enumerate(wti.dates) if wti.cause[k] == "release" and cfg.wti_first <= d <= R.last_fut]
    ck.add("N03", "WTI primary n after the release-lag rule (reports named)", "listed", "n %d; left out: %s" % (len(S["wti_fut_primary"][0]), ", ".join("%s (%s)" % (iso(d), wti.excl[wti.idx[d]]) for d in lag_dates)), "INFO")
    ck.add("N04", "Brent primary n on the committed EIA file", "819 at commit 768a26f", len(S["brent_primary"][0]), "PASS" if len(S["brent_primary"][0]) == 819 else "WARN")
    ck.add("N05", "descriptive pooled WTI pairs (2006-06-20 to 2024-03-19), before exclusions", 927, S["wti_fut_pooled"][1]["frame"], "PASS" if S["wti_fut_pooled"][1]["frame"] == 927 else "FAIL")
    ck.add("N06", "backcast WTI pairs (2006-06-20 to 2009-09-01 after the OPEN-6 ruling)", "168 (spec: 167 to 2009-08-25, plus 2009-09-01)", S["wti_fut_backcast"][1]["frame"],
           "PASS" if S["wti_fut_backcast"][1]["frame"] == 168 else "FAIL")
    ck.add("N07", "WTI spot extension pairs (2024-03-26 to the last complete window)", "132 to 2026-09-29", "%d to %s" % (S["wti_spot_ext"][1]["frame"], R.last_spot_w),
           "PASS" if S["wti_spot_ext"][1]["frame"] == 132 and R.last_spot_w == D("2026-09-29") else "WARN")
    ck.add("N08", "last WTI futures report", "2024-03-19", R.last_fut, "PASS" if R.last_fut == D("2024-03-19") else "FAIL")
    ck.add("N09", "last Brent report with a complete window; last unflagged", "complete 2026-09-29, unflagged 2026-09-15", "%s, %s" % (R.last_brent, brent.dates[S["brent_primary"][0][-1]]),
           "PASS" if brent.dates[S["brent_primary"][0][-1]] == D("2026-09-15") else "WARN")
    for lab, n in (("WTI", len(S["wti_fut_primary"][0])), ("Brent", len(S["brent_primary"][0]))):
        ck.add("N10", "%s primary bars: 5%% 1.96/sqrt(n), Holm first 2.2414/sqrt(n), 80%% power 2.8016/sqrt(n)" % lab, "printed before any correlation",
               "n %d: %s, %s, %s" % (n, f(Z95 / math.sqrt(n), 3), f(2.2414 / math.sqrt(n), 3), f(2.8016 / math.sqrt(n), 3)), "INFO")
    return ck


def wti_ledger_changes(inp):
    hdr, rows, _ = read_table(os.path.join(inp.root, "data", "cftc_cot", "wti_ledger.csv"))
    ref = {"fo": {}, "co": {}}
    nets = {"fo": {}, "co": {}}
    for r in rows:
        d = D(r["report_date"])
        nets["fo"][d], nets["co"][d] = int(r["fo_mm_net"]), int(r["co_mm_net"])
        if r["fo_mm_net_chg"] != "":
            ref["fo"][d] = int(r["fo_mm_net_chg"])
        if r["co_mm_net_chg"] != "":
            ref["co"][d] = int(r["co_mm_net_chg"])
    return ref, nets


def brent_ledger_changes(ledger):
    return {"fo": {r["date"]: r["fo_chg"] for r in ledger if r["fo_chg"] is not None}, "co": {r["date"]: r["co_chg"] for r in ledger if r["co_chg"] is not None}}


def raw_prints_of(r1, r2):
    """The raw futures prints that must never appear in a committed file: first, last and lowest RCLC1 print since 2006-06-13 and the last RCLC2 print."""
    s0 = D("2006-06-13")
    d1 = sorted(d for d in r1 if d >= s0)
    return sorted(set([f(r1[d1[0]], 2), f(r1[d1[-1]], 2), f(min(r1[d] for d in d1), 2), f(r2[max(r2)], 2)]))


def g6_problems(sched_html, hol, ignore_holidays=False):
    """G6: the CFTC release rule reproduces every release date of the saved 2026 schedule. Returns (schedule pairs, mismatch strings)."""
    sched = parse_schedule_2026(sched_html)
    bad = []
    for rd, rel in sched:
        got = cftc_release(rd, hol, None, ignore_holidays=ignore_holidays)[1]
        if got != rel:
            bad.append("%s got %s want %s" % (rd, got, rel))
    return sched, bad


def g7_problems(m, ov, cfg):
    """G7: the stated overrides and the shutdown blocks, on a WTI market whose dates include them."""
    p7 = []
    if ov.get(D("2025-09-30"), (None,))[0] != D("2025-11-19"):
        p7.append("2025-09-30 is not released 2025-11-19")
    if ov.get(D("2025-11-10"), (None,))[0] != D("2025-12-10"):
        p7.append("2025-11-10 is not released 2025-12-10 (the 9 Dec 2025 table)")
    if D("2025-09-30") in m.idx:
        k_ = m.idx[D("2025-09-30")]
        if m.excl[k_] != "release_lag_gt_7d" or m.excl[k_ - 1] != "next_report_excluded":
            p7.append("2025-09-30 and the report before it are not excluded")
    if D("2014-12-23") in m.idx and m.rel[m.idx[D("2014-12-23")]] != D("2014-12-30"):
        p7.append("2014-12-23 is not released 2014-12-30")
    for a_, b_ in cfg.shutdown_blocks:
        inb = [k for k, d in enumerate(m.dates) if a_ <= d <= b_]
        if not inb or any(m.excl[k] != "unverified_shutdown_release" for k in inb) or m.excl[inb[0] - 1] != "next_report_excluded":
            p7.append("block %s to %s is not excluded as unverified_shutdown_release with its preceding report" % (a_, b_))
    return p7


def g19_seam(cftc_nets, ledger_nets):
    """G19: every committed-ledger net (2010-01-05 on) equals the 2006 pull's net for the same date, both books. Returns (problems, values compared)."""
    bad, n = [], 0
    for b in BOOKS:
        for d, v in ledger_nets[b].items():
            n += 1
            if cftc_nets[b].get(d) != v:
                bad.append("%s %s: pull %s, ledger %s" % (b, d, cftc_nets[b].get(d), v))
    return bad, n


def real_checks_more(R, ck, say=print):
    inp, cfg = R.inp, R.cfg
    wti, brent = R.wti, R.brent
    # G6: the CFTC release rule reproduces every date of the saved 2026 schedule
    sched, bad = g6_problems(inp.sched, inp.hol_cftc)
    delayed = sum(1 for rd, rel in sched if rel != friday_of(rd))
    ck.add("G06", "CFTC release rule reproduces the saved 2026 schedule (cftc.gov ReleaseSchedule), report-date to release", "52 dates, 6 delayed",
           "%d dates, %d delayed, %d mismatches%s" % (len(sched), delayed, len(bad), "" if not bad else ": " + ", ".join(bad[:3])),
           "PASS" if len(sched) == 52 and delayed == 6 and not bad else "FAIL")
    # G7: overrides
    p7 = g7_problems(wti, inp.overrides, cfg)
    blk_n = [sum(1 for d in wti.dates if a_ <= d <= b_) for a_, b_ in cfg.shutdown_blocks]
    ck.add("G07", "release overrides read from the saved special-announcements page; shutdown blocks excluded", "2025-09-30 -> 2025-11-19, excluded with the report before; 2025-11-10 -> 2025-12-10; 2014-12-23 -> 2014-12-30; blocks of 8 and 11 reports",
           "blocks of %s reports; %d overrides read; %s" % (" and ".join(map(str, blk_n)), len(inp.overrides), "; ".join(p7) or "all hold"), "PASS" if not p7 and blk_n == [8, 11] else "FAIL")
    lag_known = sorted(d for k, d in enumerate(wti.dates) if wti.cause[k] == "release" and wti.excl[k] == "release_lag_gt_7d")
    ck.add("G07b", "reports released more than 7 days after the report date (excluded)", "ION 2023 and the 2025 shutdown weeks", "%d: %s" % (len(lag_known), ", ".join(iso(d) for d in lag_known)), "INFO")
    # G8, G2, G3, G9, G11, G12, G13
    p8 = g8_ice_timing(brent, R.WB["post_release"], inp.bh)
    ck.add("G08", "ICE timing: no Brent window starts on a print dated on the release day; bank-holiday Friday releases move to the next London business day", "holds", "; ".join(p8) or "holds", "PASS" if not p8 else "FAIL")
    p2 = g2_post_release_start(wti, R.WF["post_release"]) + g2_post_release_start(wti, R.WS["post_release"]) + g2_post_release_start(brent, R.WB["post_release"])
    ck.add("G02", "every post_start is strictly after the release date used (WTI futures, WTI spot, Brent)", "holds", "; ".join(p2) or "holds", "PASS" if not p2 else "FAIL")
    p3 = []
    for m_, W_, key in ((wti, R.WF, "wti_fut_primary"), (wti, R.WS, "wti_spot_primary"), (brent, R.WB, "brent_primary")):
        p3 += g3_no_overlap(m_, W_["post_release"], R.S[key][0])
    ck.add("G03", "no overlap: post_end of report k equals post_start of the next included report", "holds", "; ".join(p3) or "holds", "PASS" if not p3 else "FAIL")
    p9 = g9_roll(R.fut, wti, R.WF["post_release"], list(range(wti.M)))
    ck.add("G09", "roll consistency: at most one expiry per window on every window; prices positive", "holds", "; ".join(p9) or "holds", "PASS" if not p9 else "FAIL")
    p11 = g11_futures_end(wti, R.WF["post_release"], R.fut.last, R.last_fut)
    ck.add("G11", "no WTI futures window ends after the last print; last report", "2024-03-19", "; ".join(p11) or str(R.last_fut), "PASS" if not p11 and R.last_fut == D("2024-03-19") else "FAIL")
    p12 = g12_real_time(wti, R.S["wti_fut_primary"], cfg, len(R.S["wti_fut_pooled"][0]), len(R.S["wti_fut_backcast"][0]), cfg.wti_first)
    ck.add("G12", "WTI primary starts at 2009-09-08; reports up to 2009-09-01 are backcast and outside it; pooled and backcast samples exist", "holds", "; ".join(p12) or "holds",
           "PASS" if not p12 else "FAIL")
    p13 = g13_flags(brent, R.WB["post_release"], R.S["brent_primary"], R.flags, cfg.brent_first, R.last_brent)
    ck.add("G13", "flag exclusion: windows touching a print in KNOWN_SUSPECT_PRINTS are excluded and counted", "holds; ranges %s" % "; ".join("%s to %s" % x for x in R.flags),
           "; ".join(p13) or "holds, n_excl_flag=%d" % R.S["brent_primary"][1]["flag"], "PASS" if not p13 else "FAIL")
    # G1: changes, not levels (against the committed ledgers' own changes)
    ref_w, nets_w = wti_ledger_changes(inp)
    p1 = g1_changes(wti, ref_w) + g1_changes(brent, brent_ledger_changes(inp.brent))
    ck.add("G01", "regressor is the published first difference of the net in contracts (WTI vs wti_ledger.csv, Brent vs brent_ledger.csv)", "holds", "; ".join(p1) or "holds", "PASS" if not p1 else "FAIL")
    # G19 seam
    nets_api = {b: {d: wti.N[b][i] for i, d in enumerate(wti.dates)} for b in BOOKS}
    seam, nn = g19_seam(nets_api, nets_w)
    ck.add("G19", "seam: for 2010-01-05 on, the 2006 pull's managed-money nets equal wti_ledger.csv exactly", "all equal", "%d values compared; %s" % (nn, "%d differ" % len(seam) if seam else "all equal"),
           "PASS" if not seam and nn > 1000 else "FAIL")
    # G20 legacy reproduction
    got, _ = legacy_rows(inp)
    want_now = legacy_expected(LEGACY_COMMIT)
    key = ("wti", "fo")
    pins20 = (("wti", "fo", "same", 146, "0.376"), ("wti", "fo", "next", 145, "-0.084"), ("brent", "fo", "same", 146, "0.580"), ("brent", "fo", "next", 145, "-0.008"))
    p20 = ["%s %s %s: got n=%d r=%s, want n=%d r=%s" % (c, t, tag, got[(c, t)][tag][0], f(got[(c, t)][tag][1], 3), n, r_) for c, t, tag, n, r_ in pins20
           if got[(c, t)][tag][0] != n or f(got[(c, t)][tag][1], 3) != r_]
    ck.add("G20a", "legacy reproduction: WTI futures-only same-week 0.376 (n=146), next-week -0.084 (145); Brent 0.580 (146), -0.008 (145)", "reproduced", "; ".join(p20) or "reproduced",
           "PASS" if not p20 else "FAIL")
    if want_now is None:
        ck.add("G20b", "legacy reproduction against `git show %s:<path>` for leadlag.csv and brent_leadlag.csv, all 12 rows x 3 shifts" % LEGACY_COMMIT, "matches", "git object not readable", "FAIL")
    else:
        pm = legacy_match(got, want_now)
        ck.add("G20b", "legacy reproduction against `git show %s:<path>` for leadlag.csv and brent_leadlag.csv, 4 rows x 3 shifts x (n, Pearson, Spearman)" % LEGACY_COMMIT, "matches",
               "; ".join(pm[:3]) or "matches", "PASS" if not pm else "FAIL")
    cur = {}
    for path in ("data/cftc_cot/leadlag.csv", "data/ice_brent/brent_leadlag.csv"):
        for r in parse_leadlag_text(open(os.path.join(inp.root, path), encoding="utf-8").read()):
            cur[(r["contract"], r["report_type"])] = {tag: (int(r["n_" + tag]), r["pearson_%s_pct" % tag], r["spearman_%s_pct" % tag]) for tag in ("same", "next", "prev")}
    pw = legacy_match(got, cur)
    ck.add("G20c", "legacy reproduction against the working copy of the two lead-lag files (a mismatch is a WARN: the sister outputs moved on)", "matches", "; ".join(pw[:3]) or "matches",
           "PASS" if not pw else "WARN")
    # G21, G22
    p21 = g21_brent_net(inp.brent)
    ck.add("G21", "Brent fo_mm_net_chg equals the first difference of fo_mm_net on every row", "holds", "; ".join(p21) or "holds", "PASS" if not p21 else "FAIL")
    p22 = g22_one_per_week(wti.dates, NON_TUESDAYS_PRE | NON_TUESDAYS_POST) + g22_one_per_week(brent.dates, NON_TUESDAYS_BRENT)
    ck.add("G22", "one report per ISO week per market; accepted non-Tuesdays", "WTI: the 14 listed; Brent: %s" % ", ".join(sorted(iso(d) for d in NON_TUESDAYS_BRENT)), "; ".join(p22) or "holds",
           "PASS" if not p22 else "FAIL")
    # UK holiday cross-check, E-025 isolation
    ck.add("G10b", "English bank holidays: computed set equals the gov.uk file for every year it covers", "no mismatch", "%s; years %d-%d" % ("; ".join(inp.bh_bad) or "no mismatch", min(inp.bh_years), max(inp.bh_years)),
           "PASS" if not inp.bh_bad else "FAIL")
    iso_bad = [p_ for _e, p_ in ICE_TOUCHED]
    ck.add("G17", "E-025 isolation: no COTHist* path opened, no ice.com host allowed, ~/ice_cot untouched (audit hook over this process)", "none", "%d paths%s" % (len(iso_bad), ": " + ", ".join(iso_bad[:3]) if iso_bad else "")
           + ("; ice host in the allowlist" if any("ice.com" in h for h in ALLOWED_HOSTS) else ""),
           "PASS" if not iso_bad and not any("ice.com" in h for h in ALLOWED_HOSTS) else "FAIL")
    # materiality of the one deviation from the spec text (see Builder decisions): the correct business-day calendar for expiries
    bdB = lambda d: d.weekday() < 5 and d not in inp.nymex_hol
    expB = [e for _, (e, _c) in fut_expiries(bdB, *inp.exp_span)]
    futB = FuturesBasis(inp.r1, inp.r2, inp.nymex_hol, expB, R.fut.ref)
    WB_ = compute_windows(wti, futB, "post_release")
    ch = [(k, abs(WB_[k]["ret"] - R.WF["post_release"][k]["ret"])) for k in range(wti.M)
          if WB_[k] and R.WF["post_release"][k] and WB_[k]["ret"] is not None and R.WF["post_release"][k]["ret"] is not None
          and abs(WB_[k]["ret"] - R.WF["post_release"][k]["ret"]) > 1e-12]
    exA = {ym: e for ym, (e, _c) in R.exp_list}
    dB = [(ym, exA[ym], e) for ym, (e, _c) in fut_expiries(bdB, *inp.exp_span) if ym in exA and exA[ym] != e]
    ck.add("X01", "spec calendar (plain union of prints minus NYMEX_HOLIDAYS) vs weekdays minus NYMEX_HOLIDAYS: months with a different expiry; windows whose futures return changes",
           "INFO (the registered build uses the spec calendar)",
           "%d months (%s); %d windows change, largest absolute change in return %s" % (len(dB), ", ".join("%04d-%02d %s vs %s" % (ym[0], ym[1], a_, b_) for ym, a_, b_ in dB),
                                                                                  len(ch), f(max([c for _, c in ch] or [0.0]), 4)), "INFO")
    ck.add("X02", "post-registration fix, 18 Oct, after independent verification: the roll calendar stopped at the March 2024 delivery month and missed the 2024-03-20 expiry",
           "pre-fix values kept for the record",
           "before the fix the report of 2024-03-12 was priced RCLC2 to RCLC2 (-0.949%) instead of RCLC2 to RCLC1 (-0.256%); WTI primary r -0.01066 (-0.011), z -0.288, p 0.7731, s_used 0.0370, verdict unchanged",
           "INFO")
    return ck


# ----------------------------------------------------------------------------------------------------------------------
# BUILD, FREEZE
# ----------------------------------------------------------------------------------------------------------------------
V01_NAME = "independent re-derivation of the WTI primary n and r to 3 decimals from the raw CFTC rows and the RCLC files, spec section 3 alone (section 8.6)"


def eia_provenance(inp):
    """{label: (retrieval date, sha256)} of the four EIA workbooks read, from the logs that recorded their fetch."""
    out = {}
    fl = read_table(os.path.join(inp.out_dir, "fetch_log.csv"))[1] if os.path.exists(os.path.join(inp.out_dir, "fetch_log.csv")) else []
    for lab, fn in (("RCLC1d", "eia_RCLC1d.xls"), ("RCLC2d", "eia_RCLC2d.xls")):
        sha = sha256_file(os.path.join(inp.vint_dir, fn))
        row = next((r for r in fl if r["path"].endswith(lab + ".xls") and r["sha256"] == sha), None)
        out[lab] = (row["utc"][:10] if row else "unknown", sha)
    sha = sha256_file(os.path.join(inp.root, "data", "cftc_cot", "raw", "eia_RWTCd.xls"))
    man = read_manifest_dates(os.path.join(inp.root, "data", "cftc_cot", "raw", "MANIFEST.tsv"))
    out["RWTCd"] = (man.get("eia_RWTCd.xls", "unknown"), sha)
    sha = sha256_file(os.path.join(inp.root, "data", "ice_brent", "raw", "eia_RBRTEd.xls"))
    bl = read_table(os.path.join(inp.root, "data", "ice_brent", "fetch_log.csv"))[1]
    row = next((r for r in bl if r["path"].endswith("RBRTEd.xls") and r["sha256"] == sha), None)
    out["RBRTEd"] = (row["requested_at_utc"][:10] if row else "unknown", sha)
    return out


def read_manifest_dates(path):
    out = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            out[os.path.basename(r["path"])] = r["fetched_utc"][:10]
    return out


def source_for(inp, name):
    prov = eia_provenance(inp)
    fl = read_table(os.path.join(inp.out_dir, "fetch_log.csv"))[1]
    cf_date = next((r["utc"][:10] for r in fl if r["host"] == "publicreporting.cftc.gov"), "unknown")
    s = ("CFTC Disaggregated Commitments of Traders, NYMEX WTI code 067651 (publicreporting.cftc.gov and cftc.gov, public domain), retrieved %s; "
         "EIA spot and NYMEX price workbooks (eia.gov, US government, public domain), retrieved and sha256: " % cf_date)
    s += "; ".join("%s %s %s" % (k, v[0], v[1]) for k, v in sorted(prov.items()))
    s += "; gov.uk bank holidays (Open Government Licence)"
    if name in BRENT_FILES:
        s += "; " + ICE_SOURCE
    return s


def frozen_state(path):
    if not os.path.exists(path):
        return {}, {}
    hdr, rows, _ = read_table(path)
    if hdr != PRIMARY_COLS:
        raise DataError("primary.csv has an unexpected header")
    return {r["market"]: r["frozen_on"] for r in rows if r["frozen_on"]}, {r["market"]: r for r in rows}


def correction_exists(cnum, root=ROOT):
    path = os.path.join(root, "CORRECTIONS.md")
    if not re.fullmatch(r"C-\d{3,4}", cnum or ""):
        return False
    if not os.path.exists(path):
        return False
    return re.search(r"^## %s\b" % re.escape(cnum), open(path, encoding="utf-8").read(), re.M) is not None


def frozen_guard(new_rows, frozen, old_rows, unfreeze, root, ck=None):
    """Which frozen_on values to keep. A changed frozen row is refused unless `unfreeze` is a C-number that has an entry in CORRECTIONS.md."""
    keep = {}
    for r in new_rows:
        mk = r[0]
        if mk not in frozen:
            continue
        old = old_rows[mk]
        changed = [c for c, v in zip(PRIMARY_COLS, r) if c != "frozen_on" and old[c] != v]
        if changed and mut("frozen_overwrite"):
            continue
        if changed and not unfreeze:
            raise Refused("the frozen row for %s would change (%s); a changed frozen row needs `build --unfreeze C-NNN` and a CORRECTIONS entry" % (mk, ", ".join(changed[:4])))
        if changed:
            if not correction_exists(unfreeze, root):
                raise Refused("%s is not a CORRECTIONS.md entry; unfreezing needs one" % unfreeze)
            if ck is not None:
                ck.add("U01", "unfrozen row %s under %s" % (mk, unfreeze), "re-freeze after review", "changed: %s" % ", ".join(changed[:6]), "INFO")
        else:
            keep[mk] = frozen[mk]
    return keep


def write_all(R, ck, out_dir, vint_dir, unfreeze=None, say=print):
    inp = R.inp
    frozen, old_rows = frozen_state(os.path.join(out_dir, "primary.csv"))
    keep = frozen_guard(primary_rows(R), frozen, old_rows, unfreeze, inp.root, ck)
    rows = primary_rows(R, keep)
    old_checks = os.path.join(out_dir, "checks.csv")
    v01_expected = "WTI primary n=%d r=%s; Brent primary n=%d r=%s" % (R.stW["n"], f(R.stW["pearson"], 3), R.stB["n"], f(R.stB["pearson"], 3))
    v01 = [V01_NAME, v01_expected, "not yet run", "PENDING"]
    if os.path.exists(old_checks):
        for r in read_table(old_checks)[1]:
            if r["check_id"] == "V01" and r["expected"] == v01_expected and r["status"] == "PASS":
                v01 = [r["name"], r["expected"], r["observed"], r["status"]]
    ck.rows.append(["V01"] + v01)
    tables = {"primary.csv": (PRIMARY_COLS, rows), "descriptive.csv": (DESCRIPTIVE_COLS, descriptive_rows(R)), "plot26.csv": (PLOT26_COLS, plot26_rows(R)),
              "weekly_panel.csv": (PANEL_COLS, panel_rows(R)), "release_dates.csv": (RELEASE_COLS, release_rows(R)), "roll_calendar.csv": (ROLL_COLS, roll_rows(R))}
    for name, (hdr, rs) in tables.items():
        write_text(os.path.join(out_dir, name), render(name, hdr, rs, source_for(inp, name)))
    # G24 and G5 on what was just written
    headers, texts = {}, {}
    for name in tables:
        txt = open(os.path.join(out_dir, name), encoding="utf-8").read()
        texts[name] = txt
        headers[name] = next(csv.reader([l for l in txt.splitlines() if not l.startswith("#")][:1]))
    for extra in ("README.md", "SOURCES.md"):
        if os.path.exists(os.path.join(out_dir, extra)):
            texts[extra] = open(os.path.join(out_dir, extra), encoding="utf-8").read()
    p5 = g5_estimators(headers)
    ck.add("G05", "banned estimators: every header is its exact allowlist; no nw_, newey, boot, p05, p95, pct_oi or ICE gross column", "holds", "; ".join(p5) or "holds", "PASS" if not p5 else "FAIL")
    p24 = g24_leak(headers, plot_rows=tables["plot26.csv"][1], files_text=texts, raw_prints=raw_prints_of(inp.r1, inp.r2)) + unexpected_files(out_dir)
    ck.add("G24", "futures leak: no committed header contains 'fut'; y fields blank on futures bases; none of 4 raw futures prints in any committed table or note", "holds",
           "; ".join(p24) or "holds", "PASS" if not p24 else "FAIL")
    cl = os.path.join(vint_dir, "weekly_panel_futures.csv")
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["report_date", "post_start", "post_end", "contract_rule", "ret_post_fut_pct", "ret_meas_fut_pct", "ret_same_fut_pct", "ret_prev_fut_pct"])
    w.writerows(futures_local_rows(R))
    write_text(cl, buf.getvalue())
    write_text(os.path.join(out_dir, "checks.csv"), render("checks.csv", CHECKS_COLS, ck.rows, source_for(inp, "checks.csv")))
    return rows


def build_cmd(unfreeze=None, say=print, out_dir=OUT_DEFAULT, vint_dir=VINT_DEFAULT, root=ROOT, draws=PLACEBO_DRAWS):
    stray = unexpected_files(out_dir)
    if stray:
        raise Refused("unexpected content under %s, which may hold only the published files (G24): %s" % (tilde(out_dir), "; ".join(stray[:6])))
    inp = load_inputs(out_dir, vint_dir, root)
    cfg = real_cfg()
    R = compute_all(inp, cfg, say, draws)
    say("")
    say("-- checks (statuses are written to checks.csv) --")
    ck = real_checks(R, say)
    real_checks_more(R, ck, say)
    rows = write_all(R, ck, out_dir, vint_dir, unfreeze, say)
    for r in ck.rows:
        say("  %-5s %-5s %s -> %s" % (r[0], r[4], r[1][:110], r[3][:230]))
    say("")
    say("-- the two pre-registered correlations (futures-only managed-money change against the next week's post-release return) --")
    for mk, st, ks_c, m in (("WTI", R.stW, R.S["wti_fut_primary"], R.wti), ("BRENT", R.stB, R.S["brent_primary"], R.brent)):
        say("  %-5s n=%d (%s to %s)  Pearson r=%s  Spearman=%s  s_iid=%s  s_placebo=%s  s_used=%s  z=%s  p=%s  Holm rank %d alpha %s reject=%s" %
            (mk, st["n"], m.dates[ks_c[0][0]], m.dates[ks_c[0][-1]], f(st["pearson"], 3), f(st["spearman"], 3), f(st["s_iid"], 4), f(st["s_placebo"], 4), f(st["s_used"], 4),
             f(st["z"], 3), f(st["p"], 4), R.holm[mk][0], f(R.holm[mk][1], 3), R.holm[mk][2]))
    say("  WTI spot over the same window: r=%s -> sign_check_spot=%s" % (f(R.spot_r, 3), R.sign_check))
    say("  WTI verdict:   %s" % R.verdW)
    say("  Brent verdict: %s" % R.verdB)
    fails = ck.fails()
    say("")
    say("wrote 7 tables to %s and weekly_panel_futures.csv to %s" % (tilde(out_dir), tilde(vint_dir)))
    say("checks: %d PASS, %d FAIL, %d WARN, %d INFO, %d PENDING" % tuple(sum(1 for r in ck.rows if r[4] == s_) for s_ in ("PASS", "FAIL", "WARN", "INFO", "PENDING")))
    return 1 if fails else 0


def freeze_cmd(say=print, out_dir=OUT_DEFAULT, today=None):
    cpath, ppath = os.path.join(out_dir, "checks.csv"), os.path.join(out_dir, "primary.csv")
    if not os.path.exists(cpath) or not os.path.exists(ppath):
        raise Refused("run `build` first")
    checks = read_table(cpath)[1]
    fails = [r["check_id"] for r in checks if r["status"] == "FAIL"]
    v01 = [r for r in checks if r["check_id"] == "V01"]
    if fails and not mut("freeze_ignore_fail"):
        raise Refused("checks.csv has FAIL rows: %s" % ", ".join(fails))
    if (not v01 or v01[0]["status"] != "PASS") and not mut("freeze_ignore_v01"):
        raise Refused("the section 8.6 independent re-derivation (check V01) is not recorded as PASS")
    hdr, rows, src = read_table(ppath)
    if all(r["frozen_on"] for r in rows):
        raise Refused("primary.csv is already frozen; unfreezing needs a CORRECTIONS entry and `build --unfreeze C-NNN`")
    d = (today or dt.datetime.now(dt.timezone.utc).date()).isoformat()
    for r in rows:
        if not r["frozen_on"]:
            r["frozen_on"] = d
    write_text(ppath, render("primary.csv", PRIMARY_COLS, [[r[c] for c in PRIMARY_COLS] for r in rows], src[len("# source: "):]))
    say("frozen_on %s written into primary.csv for %s" % (d, ", ".join(r["market"] for r in rows)))
    return 0


def fetch_report(out_dir=OUT_DEFAULT, vint_dir=VINT_DEFAULT, say=print):
    """What the fetched files hold (spec 8.2): the CFTC counts and range per book, and the RCLC last dates. The last values print to stdout only."""
    try:
        for book, fn in CFTC_FILES.items():
            rows = parse_cftc_rows(json.load(open(os.path.join(out_dir, "raw", fn), encoding="utf-8")))
            ds = list(rows)
            say("CFTC %s: %d report dates, %s to %s" % ("futures only" if book == "fo" else "combined", len(ds), ds[0], ds[-1]))
        for lab, fn in (("RCLC1", "eia_RCLC1d.xls"), ("RCLC2", "eia_RCLC2d.xls")):
            ser, _k, _t = read_eia(os.path.join(vint_dir, fn))
            d = max(ser)
            say("%s: %d prints, last date %s, last value %s (stdout only)" % (lab, len(ser), d, f(ser[d], 2)))
    except (OSError, DataError, ValueError) as e:
        say("fetch report skipped: %s" % e)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch", help="the only network command: at most 8 requests, every URL named")
    pb = sub.add_parser("build", help="offline: write every table except frozen_on")
    pb.add_argument("--unfreeze", metavar="C-NNN", help="allow a frozen row to change; needs a CORRECTIONS.md entry")
    sub.add_parser("freeze", help="write frozen_on into primary.csv once, if checks.csv has no FAIL and V01 is PASS")
    sub.add_parser("selftest", help="synthetic, no network: 24 guards, each shown to fail on its mutant")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "fetch":
            fe = fetch_cmd(OUT_DEFAULT, VINT_DEFAULT)
            fetch_report()
            return 0
        if a.cmd == "build":
            return build_cmd(a.unfreeze)
        if a.cmd == "freeze":
            return freeze_cmd()
        if a.cmd == "selftest":
            return selftest()
    except Stop as e:
        print("STOP: %s" % e, file=sys.stderr)
        return 3
    except Refused as e:
        print("refused: %s" % e, file=sys.stderr)
        return 5
    except DataError as e:
        print("STOP (data): %s" % e, file=sys.stderr)
        return 2
    return 0


# ======================================================================================================================
# SELFTEST: synthetic worlds (2030-2031), 24 named guards, each shown to fail on its mutant. No network. Mutants are applied in this process
# only (mutated(...)); the named guard must report a problem on the mutant and none on the clean run.
# ======================================================================================================================
def quiet(*_a, **_k):
    return None


class World:
    pass


def synth_world(n_weeks=92, start=D("2030-01-08"), seed=5, holidays_on=True, carry=True):
    """A synthetic world: weekly Tuesday reports from 2030-01-08, daily prices with a rule-based NYMEX and English holiday calendar, a two-contract
    futures curve with real expiry dates, spot series, a Brent ledger and CFTC rows. The futures end before the spot series does."""
    rng = random.Random(seed)
    W = World()
    dates = [start + dt.timedelta(days=7 * i) for i in range(n_weeks)]
    W.dates = dates
    y0, y1 = start.year - 1, dates[-1].year + 1
    nyh, ukh = set(), set()
    if holidays_on:
        for y in range(y0, y1 + 1):
            nyh |= nymex_rule_holidays(y)
            ukh |= uk_computed(y)
    d0, d1 = start - dt.timedelta(days=120), dates[-1] + dt.timedelta(days=45)
    days = [d0 + dt.timedelta(days=i) for i in range((d1 - d0).days + 1)]
    tdays = [d for d in days if d.weekday() < 5 and d not in nyh]
    base, b = {}, 70.0
    for d in tdays:
        b *= 1 + rng.gauss(0, 0.012)
        base[d] = b
    is_bd = lambda d: d.weekday() < 5 and d not in nyh
    months = list(months_between(d0.year, d0.month, d1.year + 1, 3))
    exp = [expiry_date(y, m, is_bd)[0] for y, m in months]
    eps = [rng.gauss(0, 0.8) for _ in months]

    def front(t):
        return next(i for i, e in enumerate(exp) if e >= t)

    def F(c, t):
        return base[t] + 0.15 * (c - front(t)) + eps[c]

    fut_end = dates[-1] - dt.timedelta(days=75)
    W.fut_end = max(d for d in tdays if d <= fut_end)
    W.r1 = {t: F(front(t), t) for t in tdays if t <= W.fut_end}
    W.r2 = {t: F(front(t) + 1, t) for t in tdays if t <= W.fut_end}
    W.carry_day = None
    if carry:
        for y in (start.year, start.year + 1):
            c = D("%d-12-25" % y)
            if c in nyh and c.weekday() < 5 and c <= W.fut_end:
                prev = max(t for t in W.r1 if t < c)
                W.r1[c], W.r2[c] = W.r1[prev], W.r2[prev]
                W.carry_day = c
                break
    W.front, W.F, W.exp, W.months, W.nyh, W.ukh, W.base, W.tdays = front, F, exp, months, nyh, ukh, base, tdays
    W.rwtc = {t: base[t] * (1 + rng.gauss(0, 0.002)) for t in tdays}
    for t in rng.sample(sorted(W.rwtc), 4):
        del W.rwtc[t]
    bdays = [d for d in days if d.weekday() < 5 and d not in ukh and d <= dates[-1] + dt.timedelta(days=14)]
    bb, W.rbrte = 75.0, {}
    for d in bdays:
        bb *= 1 + rng.gauss(0, 0.012)
        W.rbrte[d] = bb
    nets = {"fo": [], "co": []}
    lv = {"fo": 50000, "co": 70000}
    for _ in dates:
        for bk in BOOKS:
            lv[bk] += rng.randint(-9000, 9000)
            nets[bk].append(lv[bk])
    W.nets = nets
    W.cftc = {bk: {d: (150000 + max(nets[bk][i], 0), 150000 - min(nets[bk][i], 0), 900000) for i, d in enumerate(dates)} for bk in BOOKS}
    W.ledger = [{"date": d, "fo_net": nets["fo"][i], "co_net": nets["co"][i], "fo_chg": nets["fo"][i] - nets["fo"][i - 1] if i else None,
                 "co_chg": nets["co"][i] - nets["co"][i - 1] if i else None, "price_flag": ""} for i, d in enumerate(dates)]
    flag_lo = dates[-1] + dt.timedelta(days=3)
    usable = [ym for ym in months[1:] if D("%d-%02d-25" % (ym[0] - (ym[1] == 1), ym[1] - 1 or 12)) <= W.fut_end - dt.timedelta(days=5)]
    ue = months.index(usable[-1]) + 2
    exp_span = (months[1][0], months[1][1], months[ue][0], months[ue][1])
    W.cfg = Cfg(backcast_last=dates[9], backcast_label_last=dates[7], shutdown_blocks=((dates[30], dates[31]),), wti_first=dates[11], wti_pool_first=dates[1],
                realtime_level_first=dates[10], brent_first=dates[1], flag_ranges=((flag_lo, max(W.rbrte)),))
    W.inp = Inputs(cftc=W.cftc, brent=W.ledger, r1=W.r1, r2=W.r2, rwtc=W.rwtc, rbrte=W.rbrte, hol_cftc=us_federal_holidays_span(y0, y1), overrides={}, bh=ukh,
                   nymex_hol=nyh, exp_span=exp_span, root=ROOT, out_dir="", vint_dir="")
    return W


def synth_R(W, draws=10, mutant=None, cfg=None):
    if mutant:
        with mutated(mutant):
            return compute_all(W.inp, cfg or W.cfg, quiet, draws)
    return compute_all(W.inp, cfg or W.cfg, quiet, draws)


def planted_world(c_r=0.5, n=500, seed=3):
    """No holidays: report k's window is the Monday after its Friday release to the next such Monday, and R_k = c*dn_k + noise with a true r of c_r."""
    rng = random.Random(seed)
    start = D("2030-01-08")
    dates = [start + dt.timedelta(days=7 * i) for i in range(n)]
    N = [0]
    for _ in range(n - 1):
        N.append(N[-1] + rng.randint(-5000, 5000))
    dn = [None] + [N[i] - N[i - 1] for i in range(1, n)]
    sd = math.sqrt(sum(v * v for v in dn[1:]) / (n - 1))
    c = 0.01 / sd
    noise_sd = c * sd * math.sqrt(1 / (c_r ** 2) - 1)
    Rk = [c * (dn[k] or 0) + rng.gauss(0, noise_sd) for k in range(n)]
    P, a_k = 100.0, [dates[k] + dt.timedelta(days=6) for k in range(n)]
    px = {}
    for k in range(n):
        px[a_k[k]] = P
        P *= 1 + Rk[k]
    series, last = {}, None
    d = a_k[0]
    while d <= a_k[-1]:
        if d in px:
            last = px[d]
        if d.weekday() < 5:
            series[d] = last
        d += dt.timedelta(days=1)
    cftc = {bk: {dt_: (150000 + max(N[i], 0), 150000 - min(N[i], 0), 900000) for i, dt_ in enumerate(dates)} for bk in BOOKS}
    inp = Inputs(cftc=cftc, hol_cftc=set(), overrides={})
    cfg = Cfg(backcast_last=dates[0] - dt.timedelta(days=1), backcast_label_last=None, shutdown_blocks=(), wti_first=dates[1], wti_pool_first=dates[1])
    return dates, series, inp, cfg


def planted_r():
    dates, series, inp, cfg = planted_world()
    m = make_wti_market(inp, cfg)
    basis = SpotBasis("planted", series, lambda d: d.weekday() < 5)
    Wd = compute_windows(m, basis, "post_release")
    ks, _c = select(m, Wd, dates[1], dates[-2])
    xs, ys = xs_ys(m, Wd, ks, "fo")
    return pearson(xs, ys), len(xs)


def placebo_reference(x, y, draws, seed=SEED):
    """A plain implementation of the placebo (explicit signs, pearson per draw) to compare placebo_scale with."""
    rng = random.Random(seed)
    rs = []
    for _ in range(draws):
        sg = [1 if rng.getrandbits(1) else -1 for _ in range(len(y))]
        rs.append(pearson(x, [a * b for a, b in zip(sg, y)]))
    mu = sum(rs) / len(rs)
    return math.sqrt(sum((r - mu) ** 2 for r in rs) / len(rs))


def shared_vol_series(n=300, seed=9):
    rng = random.Random(seed)
    x, y = [], []
    for i in range(n):
        sg = 1.0 if (i // 10) % 2 == 0 else 6.0
        x.append(sg * rng.gauss(0, 1))
        y.append(sg * rng.gauss(0, 1) * 0.01)
    return x, y


class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def mono(self):
        return self.t

    def sleep(self, x):
        self.t += x


def g18_problems(calls):
    """G18 analysis of what a fake transport saw: exactly the CLAUDE.md string with no address in it, only the eight named URLs, no request after a redirect, at most 8
    requests including retries, at least 2 s between request starts."""
    bad = []
    prev_t, prev_status = None, None
    for i, c in enumerate(calls):
        if c["ua"] != UA or "@" in c["ua"]:
            bad.append("request %d: User-Agent is not the CLAUDE.md string" % (i + 1))
        if (c["host"], c["path"]) not in ALLOWED_URLS:
            bad.append("request %d went to an unlisted URL on %s" % (i + 1, c["host"]))
        if prev_status is not None and 300 <= prev_status < 400:
            bad.append("request %d was made after a redirect" % (i + 1))
        if prev_t is not None and c["t"] - prev_t < MIN_GAP - 1e-9:
            bad.append("request %d started %.2f s after the previous one" % (i + 1, c["t"] - prev_t))
        prev_t, prev_status = c["t"], c["status"]
    if len(calls) > MAX_REQUESTS:
        bad.append("%d requests (cap %d)" % (len(calls), MAX_REQUESTS))
    return bad


def g18_scenario(kind, mutants=()):
    """Run a Fetcher against a fake transport. kind: 'retry' (429 once, then 200s), 'redirect' (302 on the first URL), 'unlisted' (an ice.com URL in the list)."""
    clk = FakeClock()
    calls = []
    tmp = tempfile.mkdtemp(prefix="cot_g18_")
    try:
        def opener(host, target, headers, timeout, cap):
            first_seen = sum(1 for c in calls if (c["host"], c["path"]) == (host, target))
            status = 200
            hd = {}
            if kind == "retry" and len(calls) == 0:
                status, hd = 429, {"retry-after": "1"}
            if kind == "redirect" and len(calls) == 0:
                status, hd = 302, {"location": "https://www.gov.uk/bank-holidays.json"}
            calls.append({"t": clk.mono(), "host": host, "path": target, "ua": headers["User-Agent"], "status": status})
            return status, hd, (b"x" if status == 200 else b"")
        urls = URLS
        if kind == "unlisted":
            urls = (("ice", "www.ice.com", "/publicdocs/futures/COTHist2031.csv", "ice_probe.csv", "html"),) + URLS
        ctxs = [mutated(m_) for m_ in mutants]
        for cm in ctxs:
            cm.__enter__()
        try:
            fe = Fetcher(os.path.join(tmp, "out"), os.path.join(tmp, "v"), opener=opener, mono=clk.mono, sleeper=clk.sleep, urls=urls,
                         max_requests=9 if "fetch_ninth" in mutants else MAX_REQUESTS, validator=lambda k_, b_: None)
            raised = None
            try:
                for key, host, path, saved, kind_ in fe.urls:
                    fe.get(key, host, path, saved, kind_)
            except (Stop, Refused) as e:
                raised = e
        finally:
            for cm in reversed(ctxs):
                cm.__exit__(None, None, None)
        return calls, raised
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def tmp_dir(prefix):
    return tempfile.mkdtemp(prefix=prefix)


def g15_problems(mutants=()):
    """G15: build never writes frozen_on; freeze refuses on a FAIL or a missing section-8.6 PASS and writes the date once; a changed frozen row
    needs --unfreeze C-NNN naming a CORRECTIONS entry."""
    import shutil
    bad = []
    ctxs = [mutated(m_) for m_ in mutants]
    for cm in ctxs:
        cm.__enter__()
    tmp = tmp_dir("cot_g15_")
    try:
        W = synth_world(n_weeks=60)
        R = synth_R(W)
        if any(r[-1] for r in primary_rows(R)):
            bad.append("build wrote frozen_on")
        rows = primary_rows(R)
        hdr = PRIMARY_COLS

        def put(d, check_rows):
            os.makedirs(d, exist_ok=True)
            write_text(os.path.join(d, "primary.csv"), render("primary.csv", hdr, rows, "synthetic"))
            write_text(os.path.join(d, "checks.csv"), render("checks.csv", CHECKS_COLS, check_rows, "synthetic"))
        base_ok = [["P1", "pin", "1", "1", "PASS"]]
        # refuses on a missing V01 PASS
        d1 = os.path.join(tmp, "a")
        put(d1, base_ok + [["V01", "rederivation", "x", "not yet run", "PENDING"]])
        try:
            freeze_cmd(quiet, d1, today=D("2030-02-01"))
            bad.append("freeze ran without a section 8.6 PASS")
        except Refused:
            pass
        # refuses on a FAIL
        d2 = os.path.join(tmp, "b")
        put(d2, base_ok + [["X1", "broken", "1", "2", "FAIL"], ["V01", "rederivation", "x", "ok", "PASS"]])
        try:
            freeze_cmd(quiet, d2, today=D("2030-02-01"))
            bad.append("freeze ran with a FAIL in checks.csv")
        except Refused:
            pass
        # writes the date once
        d3 = os.path.join(tmp, "c")
        put(d3, base_ok + [["V01", "rederivation", "x", "ok", "PASS"]])
        try:
            freeze_cmd(quiet, d3, today=D("2030-02-01"))
        except Refused as e:
            bad.append("freeze refused a clean build: %s" % str(e)[:60])
        fr, old = frozen_state(os.path.join(d3, "primary.csv"))
        if sorted(fr) != ["BRENT", "WTI"] or set(fr.values()) != {"2030-02-01"}:
            bad.append("freeze did not write frozen_on for both markets")
        try:
            freeze_cmd(quiet, d3, today=D("2030-02-02"))
            bad.append("freeze ran twice")
        except Refused:
            pass
        # a changed frozen row needs --unfreeze naming a CORRECTIONS entry
        if not fr:
            fr, old = {r[0]: "2030-02-01" for r in rows}, {r[0]: dict(zip(PRIMARY_COLS, r)) for r in rows}
        changed = [list(r) for r in rows]
        changed[0][12] = "0.999"
        try:
            frozen_guard(changed, fr, old, None, tmp)
            bad.append("a changed frozen row was accepted without --unfreeze")
        except Refused:
            pass
        os.makedirs(tmp, exist_ok=True)
        write_text(os.path.join(tmp, "CORRECTIONS.md"), "## C-001 something\n")
        try:
            frozen_guard(changed, fr, old, "C-777", tmp)
            bad.append("--unfreeze accepted a C-number that is not in CORRECTIONS.md")
        except Refused:
            pass
        keep = frozen_guard(changed, fr, old, "C-001", tmp)
        if "WTI" in keep:
            bad.append("an unfrozen row kept its frozen_on")
        if "BRENT" not in keep:
            bad.append("an unchanged frozen row lost its frozen_on")
    finally:
        for cm in reversed(ctxs):
            cm.__exit__(None, None, None)
        shutil.rmtree(tmp, ignore_errors=True)
    return bad


def synth_ledger_text(W):
    lines = ["# source: synthetic", "report_date,fo_mm_net,fo_mm_net_chg,co_mm_net,co_mm_net_chg,price_flag"]
    for r in W.ledger:
        lines.append("%s,%d,%s,%d,%s," % (r["date"], r["fo_net"], "" if r["fo_chg"] is None else r["fo_chg"], r["co_net"], "" if r["co_chg"] is None else r["co_chg"]))
    return "\n".join(lines) + "\n"


def gs_ids():
    return [
        ("G01", "changes-not-levels"), ("G02", "post-release start"), ("G03", "no-overlap"), ("G04", "honest bar"), ("G05", "banned estimators"),
        ("G06", "CFTC release rule"), ("G07", "release overrides"), ("G08", "ICE timing"), ("G09", "roll consistency"), ("G10", "roll calendar"),
        ("G11", "futures end"), ("G12", "real-time start"), ("G13", "flag exclusion"), ("G14", "Holm"), ("G15", "freeze"), ("G16", "placebo"),
        ("G17", "E-025 isolation"), ("G18", "fetch hygiene"), ("G19", "seam"), ("G20", "legacy reproduction"), ("G21", "Brent net check"),
        ("G22", "one per ISO week"), ("G23", "week pairing"), ("G24", "futures leak")]


def run_guards(W, say=print):
    """Returns [(id, name, clean problems, [(mutant label, problems)])]."""
    out = []
    R = synth_R(W)
    wti, brent = R.wti, R.brent
    ref_w = {b: {d: W.nets[b][i] - W.nets[b][i - 1] for i, d in enumerate(W.dates) if i} for b in BOOKS}

    # G01
    clean = g1_changes(wti, ref_w) + g1_changes(brent, ref_w)
    with mutated("x_level"):
        mu = g1_changes(wti, ref_w)
    out.append(("G01", clean, [("feed the level of net", mu)]))

    # G02
    clean = g2_post_release_start(wti, R.WS["post_release"]) + g2_post_release_start(wti, R.WF["post_release"]) + g2_post_release_start(brent, R.WB["post_release"])
    mus = []
    for mn, lab in (("start_at_report_tuesday", "start at the report Tuesday"), ("start_at_release_day", "start at the release Friday")):
        Rm = synth_R(W, mutant=mn)
        mus.append((lab, g2_post_release_start(Rm.wti, Rm.WS["post_release"]) + g2_post_release_start(Rm.brent, Rm.WB["post_release"])))
    out.append(("G02", clean, mus))

    # G03
    ks = R.S["wti_spot_primary"][0]
    _x, _y, st = blocks_b(wti, R.WS["post_release"], ks, "fo", 4, R.lvl_rt)
    clean = g3_no_overlap(wti, R.WS["post_release"], ks, (st, 4))
    if len(ks) < 30 or len(st) < 5:
        clean.append("too few included weeks (%d) or blocks (%d) in the synthetic world" % (len(ks), len(st)))
    with mutated("blocks_overlap"):
        _x2, _y2, st2 = blocks_b(wti, R.WS["post_release"], ks, "fo", 4, R.lvl_rt)
    out.append(("G03", clean, [("an h-week return computed every week", g3_no_overlap(wti, R.WS["post_release"], ks, (st2, 4)))]))

    # G04
    rows = descriptive_rows(R)
    clean = g4_honest_bar(rows)
    with mutated("bar_from_T"):
        rows_m = descriptive_rows(R)
    out.append(("G04", clean, [("bar from 1.96/sqrt(T) at h=13", g4_honest_bar(rows_m))]))

    # G05
    allow_ok = {n: list(c) for n, c in ALLOW.items()}
    clean = g5_estimators(allow_ok)
    m1 = {n: list(c) for n, c in ALLOW.items()}
    m1["primary.csv"] = m1["primary.csv"] + ["nw_se"]
    m2 = {n: list(c) for n, c in ALLOW.items()}
    m2["descriptive.csv"] = m2["descriptive.csv"] + ["boot_p05"]
    out.append(("G05", clean, [("add nw_se", g5_estimators(m1)), ("add boot_p05", g5_estimators(m2))]))

    # G06 (reads the saved CFTC schedule page)
    sp = os.path.join(OUT_DEFAULT, "raw", "cftc_release_schedule.html")
    sched_html = open(sp, "rb").read()
    hol = us_federal_holidays_span(2004, 2028) | set(CLOSURE_DAYS)
    sch, bad = g6_problems(sched_html, hol)
    clean = bad + ([] if len(sch) == 52 and sum(1 for rd, rel in sch if rel != friday_of(rd)) == 6 else ["not 52 dates with 6 delayed"])
    with mutated("release_ignore_holidays"):
        _s, badm = g6_problems(sched_html, hol)
    out.append(("G06", clean, [("ignore holidays", badm)]))

    # G07 (reads the saved special-announcements page; a market whose dates include the overrides and both blocks)
    special = open(os.path.join(OUT_DEFAULT, "raw", "cftc_special_announcements.html"), "rb").read()
    dd = [D("2013-01-01") + dt.timedelta(days=7 * i) for i in range(0, 13 * 52 + 2)]
    dd = sorted(set(d for d in dd if d <= D("2025-12-30")) | {D("2014-12-23"), D("2025-09-30"), D("2025-11-10")})
    inp7 = Inputs(cftc={b: {d: (1, 0, 1) for d in dd} for b in BOOKS}, hol_cftc=us_federal_holidays_span(2012, 2026) | set(CLOSURE_DAYS))
    cfg7 = Cfg()

    def g7_with(overrides):
        inp7.overrides = overrides
        return g7_problems(make_wti_market(inp7, cfg7), overrides, cfg7)
    clean = g7_with(build_overrides(special))
    mus = [("drop the override table", g7_with({})), ("use the 18 Nov 2025 table", g7_with(build_overrides(special, which="nov18")))]
    out.append(("G07", clean, mus))

    # G08: a Brent report whose Friday is Good Friday
    gf_year = 2030
    gf = easter(gf_year) - dt.timedelta(days=2)
    rd = gf - dt.timedelta(days=3)
    clean = g8_ice_timing(brent, R.WB["post_release"], W.ukh)
    _n, rel_ok, _r = ice_release(rd, W.ukh)
    if rel_ok != easter(gf_year) + dt.timedelta(days=2):
        clean.append("Good Friday %s released %s, expected the Tuesday %s" % (gf, rel_ok, easter(gf_year) + dt.timedelta(days=2)))
    mus = []
    Rm = synth_R(W, mutant="start_at_release_day")
    mus.append(("start at Friday's print", g8_ice_timing(Rm.brent, Rm.WB["post_release"], W.ukh)))
    with mutated("ice_good_friday_monday"):
        Rm2 = synth_R(W)
        mus.append(("move Good Friday to Monday", g8_ice_timing(Rm2.brent, Rm2.WB["post_release"], W.ukh)))
    out.append(("G08", clean, mus))

    # G09: same contract at both ends on every window; a negative RCLC1 print on an expiry day does not enter a return
    def truth(a, b):
        c = W.front(a) + 1
        return W.F(c, b) / W.F(c, a) - 1
    ksw = [k for k in range(wti.M) if R.WF["post_release"][k] and R.WF["post_release"][k]["ret"] is not None]
    clean = g9_roll(R.fut, wti, R.WF["post_release"], ksw, truth)
    n_roll = sum(1 for k in ksw if R.fut.expiry_between(R.WF["post_release"][k]["a"], R.WF["post_release"][k]["b"]) is not None)
    if n_roll < 5 or len(ksw) < 50:
        clean.append("the synthetic world exercises only %d rolls in %d windows" % (n_roll, len(ksw)))
    micro = micro_negative_check()
    clean += micro
    Rm = synth_R(W, mutant="naive_front")
    mu = g9_roll(Rm.fut, Rm.wti, Rm.WF["post_release"], ksw, truth)
    with mutated("naive_front"):
        mu += micro_negative_check()
    Rt = synth_R(W, mutant="exp_truncated")
    mt = g9_roll(Rt.fut, Rt.wti, Rt.WF["post_release"], ksw, truth)
    out.append(("G09", clean, [("naive RCLC1 at both ends", mu), ("roll calendar truncated before the last window", mt)]))

    # G10: roll calendar rule cases; holiday-set prints ignored; a <= e < b on the dates actually used
    clean = g10_problems(W)
    if W.carry_day is None:
        clean.append("the synthetic world has no carried-forward holiday print")
    mus = []
    with mutated("expiry_ignore_non_business"):
        mus.append(("25th on a Saturday counted as a business day", g10_problems(W)))
    mus.append(("count a carry-forward holiday as a business day", g10_problems(W, holiday_is_bd=True)))
    with mutated("expiry_uses_nominal"):
        mus.append(("test the original grid dates", g10_problems(W)))
    out.append(("G10", clean, mus))

    # G11
    exp_last = max(d for k, d in enumerate(wti.dates) if k + 1 < wti.M and R.fut.nominal_after(wti.rel[k + 1]) <= R.fut.last)
    clean = g11_futures_end(wti, R.WF["post_release"], R.fut.last, exp_last)
    if not any(w_ and w_["reason"] == "beyond_data_end" for w_ in R.WF["post_release"]):
        clean.append("no window lies beyond the futures end in the synthetic world")
    Rm = synth_R(W, mutant="fut_substitute_spot")
    out.append(("G11", clean, [("substitute spot after the futures end", g11_futures_end(Rm.wti, Rm.WF["post_release"], Rm.fut.last, exp_last))]))

    # G12
    pooled, back = len(R.S["wti_fut_pooled"][0]), len(R.S["wti_fut_backcast"][0])
    clean = g12_real_time(wti, R.S["wti_fut_primary"], W.cfg, pooled, back, W.cfg.wti_first)
    Rm = synth_R(W, mutant="primary_admit_backcast")
    out.append(("G12", clean, [("START = the pooled start in the primary", g12_real_time(Rm.wti, Rm.S["wti_fut_primary"], W.cfg, pooled, back, W.cfg.wti_first))]))

    # G13
    clean = g13_flags(brent, R.WB["post_release"], R.S["brent_primary"], R.flags, W.cfg.brent_first, R.last_brent)
    clean += [] if R.S["brent_primary"][1]["flag"] > 0 else ["the synthetic world has no flagged window to test"]
    Rm = synth_R(W, mutant="ignore_flag")
    out.append(("G13", clean, [("ignore the flag", g13_flags(Rm.brent, Rm.WB["post_release"], Rm.S["brent_primary"], R.flags, W.cfg.brent_first, Rm.last_brent))]))

    # G14
    clean = g14_holm(holm)
    mus = []
    with mutated("holm_bonferroni"):
        mus.append(("Bonferroni on both", g14_holm(holm)))
    with mutated("holm_no_stop"):
        mus.append(("no stopping", g14_holm(holm)))
    out.append(("G14", clean, mus))

    # G15
    clean = g15_problems()
    mus = [("build writes frozen_on", g15_problems(("build_writes_frozen",))), ("freeze ignores a FAIL", g15_problems(("freeze_ignore_fail",))),
           ("freeze ignores a missing 8.6 PASS", g15_problems(("freeze_ignore_v01",))), ("overwrite a frozen row", g15_problems(("frozen_overwrite",)))]
    out.append(("G15", clean, mus))

    # G16
    xv, yv = shared_vol_series()
    clean = g16_placebo(lambda a, b: primary_stats(a, b, 300), xv, yv)
    st_ = primary_stats(xv, yv, 300)
    if not st_["s_placebo"] > st_["s_iid"]:
        clean.append("s_placebo %.4f is not above 1/sqrt(n) %.4f on a shared-volatility series" % (st_["s_placebo"], st_["s_iid"]))
    ref = placebo_reference(xv, yv, 300)
    if abs(placebo_scale(xv, yv, 300) - ref) > 1e-12:
        clean.append("placebo_scale differs from the plain reference implementation")
    mus = []
    with mutated("scale_iid_only"):
        mu = g16_placebo(lambda a, b: primary_stats(a, b, 300), xv, yv)
    mus.append(("s_used = 1/sqrt(n) always", mu))
    with mutated("placebo_seed"):
        d_ = abs(placebo_scale(xv, yv, 300) - ref) > 1e-12
    mus.append(("a different seed", ["placebo_scale differs from the reference"] if d_ else []))
    out.append(("G16", clean, mus))

    # G17
    n0 = len(ICE_TOUCHED)
    synth_R(W)
    clean = (["ICE path touched during a synthetic run"] if len(ICE_TOUCHED) > n0 else []) + (["ice.com is in the host allowlist"] if any("ice.com" in h for h in ALLOWED_HOSTS) else [])
    tmpd = tmp_dir("cot_g17_")
    try:
        fn = os.path.join(tmpd, "COTHist2031.csv")
        with open(fn, "w") as fh:
            fh.write("probe\n")
        with open(fn) as fh:
            fh.read()
        mu = ["a COTHist file was opened"] if len(ICE_TOUCHED) > n0 else []
    finally:
        import shutil
        shutil.rmtree(tmpd, ignore_errors=True)
    del ICE_TOUCHED[n0:]
    out.append(("G17", clean, [("read a COTHist file", mu)]))

    # G18
    calls, raised = g18_scenario("retry")
    clean = g18_problems(calls) + ([] if len(calls) == MAX_REQUESTS else ["the cap did not stop the run at %d requests (saw %d)" % (MAX_REQUESTS, len(calls))])
    calls_r, raised_r = g18_scenario("redirect")
    clean += g18_problems(calls_r) + ([] if isinstance(raised_r, Stop) and len(calls_r) == 1 else ["a redirect did not stop the run"])
    calls_u, raised_u = g18_scenario("unlisted")
    clean += ([] if isinstance(raised_u, Refused) else ["an unlisted URL was not refused"]) + g18_problems(calls_u)
    mus = []
    c_, _ = g18_scenario("redirect", ("fetch_follow_redirect",))
    mus.append(("follow a 302", g18_problems(c_)))
    c_, _ = g18_scenario("retry", ("fetch_ninth",))
    mus.append(("a 9th request", g18_problems(c_)))
    c_, _ = g18_scenario("unlisted", ("fetch_unlisted_ok",))
    mus.append(("an unlisted URL", g18_problems(c_)))
    c_, _ = g18_scenario("retry", ("fetch_no_pacing",))
    mus.append(("no pacing", g18_problems(c_)))
    out.append(("G18", clean, mus))

    # G19
    nets_api = {b: {d: W.nets[b][i] for i, d in enumerate(W.dates)} for b in BOOKS}
    led = {b: {d: W.nets[b][i] for i, d in enumerate(W.dates) if i >= 5} for b in BOOKS}
    clean, _n = g19_seam(nets_api, led)
    shifted = {b: {d: W.nets[b][i - 1] for i, d in enumerate(W.dates) if i} for b in BOOKS}
    mu, _n2 = g19_seam(shifted, led)
    out.append(("G19", clean, [("shift the rows one week", mu)]))

    # G20
    dts = W.dates
    Pser = [100 * (1 + 0.004 * ((i * 7) % 11 - 5) + 0.0001 * i) for i in range(len(dts))]
    Nser = W.nets["fo"]
    split = dts[len(dts) // 2]
    got = legacy_leadlag(dts, Nser, Pser, split)
    clean = legacy_reference_problems(dts, Nser, Pser, split, got)
    with mutated("legacy_base"):
        got_m = legacy_leadlag(dts, Nser, Pser, split)
    out.append(("G20", clean, [("change the percent-change base", legacy_reference_problems(dts, Nser, Pser, split, got_m))]))

    # G21
    tmpd = tmp_dir("cot_g21_")
    try:
        pth = os.path.join(tmpd, "brent_ledger.csv")
        write_text(pth, synth_ledger_text(W))
        clean = g21_brent_net(load_brent_ledger(pth))
        with mutated("brent_read_co"):
            mu = g21_brent_net(load_brent_ledger(pth))
    finally:
        import shutil
        shutil.rmtree(tmpd, ignore_errors=True)
    out.append(("G21", clean, [("read co_ for fo_", mu)]))

    # G22
    clean = g22_one_per_week(W.dates, frozenset())
    dup = sorted(W.dates + [W.dates[5] + dt.timedelta(days=1)])
    out.append(("G22", clean, [("a duplicated week", g22_one_per_week(dup, frozenset()))]))

    # G23
    r, n = planted_r()
    clean = [] if r >= 0.4 else ["planted r %.3f is below 0.4 (n=%d)" % (r, n)]
    mus = []
    for mn, lab in (("pair_next", "pair dn_k with window k+1"), ("pair_prev", "pair dn_k with window k-1")):
        with mutated(mn):
            r2_, _ = planted_r()
        mus.append((lab, [] if r2_ >= 0.4 else ["planted r fell to %.3f" % r2_]))
    out.append(("G23", clean, mus))

    # G24
    hdrs = {n_: list(c) for n_, c in ALLOW.items()}
    pr = plot26_rows(R)
    raw_p = raw_prints_of(W.r1, W.r2)
    txt = {"weekly_panel.csv": "market,report_date\nWTI,2030-01-08\n"}
    clean = g24_leak(hdrs, plot_rows=pr, files_text=txt, raw_prints=raw_p)
    if not any(r_[2] == FUT_WTI for r_ in pr):
        clean.append("no futures-basis plot row to test")
    m1 = {n_: list(c) for n_, c in ALLOW.items()}
    m1["weekly_panel.csv"] = m1["weekly_panel.csv"] + ["ret_post_fut_pct"]
    d24 = tmp_dir("cot_g24_")
    try:
        for n_ in EXPECTED_TOP - {"raw"}:
            write_text(os.path.join(d24, n_), "# source: x\nmarket\n" if n_.endswith(".csv") else "x\n")
        for n_ in EXPECTED_RAW:
            write_text(os.path.join(d24, "raw", n_), "{}")
        clean += unexpected_files(d24)
        write_text(os.path.join(d24, "weekly_panel_futures.csv"), "# source: x\nreport_date,ret_post_fut_pct\n2030-01-08,1.0\n")
        copied = unexpected_files(d24)
    finally:
        import shutil
        shutil.rmtree(d24, ignore_errors=True)
    out.append(("G24", clean, [("a copied weekly_panel_futures.csv in the output directory", copied), ("write ret_post_fut_pct into weekly_panel.csv", g24_leak(m1, plot_rows=pr, files_text=txt, raw_prints=raw_p)),
                               ("a raw print in a committed table", g24_leak(hdrs, plot_rows=pr, files_text={"checks.csv": "x," + raw_p[0] + ",y"}, raw_prints=raw_p)),
                               ("y fields filled on a futures basis", g24_leak(hdrs, plot_rows=[[r_[0], r_[1], FUT_WTI, "1", "a", "b", "1", "10.00", "11.00", "10.0", "0.4"] for r_ in pr[:1]], files_text=txt, raw_prints=raw_p))]))
    return out


def legacy_reference_problems(dates, N, P, split, got):
    """Compare legacy_leadlag with a straightforward re-derivation through statistics.correlation (exact floats)."""
    import statistics
    bad = []
    t0 = max(1, next(i for i, d in enumerate(dates) if d >= split))
    ts = list(range(t0, len(dates)))
    ret = {t: P[t] / P[t - 1] - 1 for t in range(1, len(dates))}
    for tag, sh in (("same", 0), ("next", 1), ("prev", -1)):
        tt = [t for t in ts if 1 <= t + sh < len(dates)]
        x = [N[t] - N[t - 1] for t in tt]
        y = [ret[t + sh] for t in tt]
        want = statistics.correlation(x, y)
        if got[tag][0] != len(tt) or abs(got[tag][1] - want) > 1e-12:
            bad.append("%s: legacy_leadlag r=%.9f n=%d, reference r=%.9f n=%d" % (tag, got[tag][1], got[tag][0], want, len(tt)))
    return bad


def micro_negative_check():
    """A negative RCLC1 print on an expiry day that ends a window must not enter the return: the end is RCLC2 and the return is positive-priced."""
    d1, d2, d3 = D("2030-03-04"), D("2030-03-05"), D("2030-03-06")
    r1 = {d1: 50.0, d2: -37.0, d3: 51.0}
    r2 = {d1: 51.0, d2: 52.0, d3: 53.0}
    fb = FuturesBasis(r1, r2, frozenset(), [d2], lambda d: d.weekday() < 5)
    w = fb.window(d1, d2)
    bad = []
    if w["ret"] is None or abs(w["ret"] - (52.0 / 51.0 - 1)) > 1e-12:
        bad.append("a window ending on the expiry day did not use RCLC2 (got %r)" % (w["ret"],))
    return bad


def g10_problems(W, holiday_is_bd=False):
    """G10: 2020-04-21 is an expiry; rule cases for a 25th on a weekday, Saturday and Sunday follow the EIA text; prints on holiday-set days are ignored
    (a carried-forward Christmas print must not move the next expiry); a <= e < b uses the dates actually used after the move-forward."""
    bad = []

    def bdy(y):
        h = nymex_rule_holidays(y) | nymex_rule_holidays(y - 1) | nymex_rule_holidays(y + 1)
        return lambda d: d.weekday() < 5 and d not in h
    e, case = expiry_date(2020, 5, bdy(2020))
    if e != D("2020-04-21") or case != "25th_saturday":
        bad.append("May 2020 expiry is %s (%s), expected 2020-04-21" % (e, case))
    e, case = expiry_date(2022, 10, bdy(2022))
    if e != D("2022-09-20") or case != "25th_sunday":
        bad.append("Oct 2022 expiry is %s (%s), expected 2022-09-20 (25th on a Sunday)" % (e, case))
    e, case = expiry_date(2015, 12, bdy(2015))
    if e != D("2015-11-20") or case != "25th_business_day":
        bad.append("Dec 2015 expiry is %s (%s), expected 2015-11-20 (25th on a weekday)" % (e, case))
    # a carried-forward Christmas print: the pipeline's calendar is (prints) minus (holiday set)
    if W.carry_day is not None:
        U = set(W.r1) | set(W.r2)
        H = W.nyh if not holiday_is_bd else frozenset()
        isb = lambda d: d in U and d not in H
        e2, _c = expiry_date(W.carry_day.year + 1, 1, isb)
        want = expiry_date(W.carry_day.year + 1, 1, lambda d: d.weekday() < 5 and d not in W.nyh)[0]
        if e2 != want:
            bad.append("the carried-forward %s print moved the January expiry to %s (expected %s)" % (W.carry_day, e2, want))
        fb = FuturesBasis(W.r1, W.r2, H if not holiday_is_bd else frozenset(), [], lambda d: d.weekday() < 5)
        if W.carry_day in fb.r1 and not holiday_is_bd:
            bad.append("a print on the holiday-set day %s was not ignored" % W.carry_day)
        if holiday_is_bd and W.carry_day in fb.r1:
            bad.append("a print on the holiday %s was counted as a business day" % W.carry_day)
    # the window test uses the moved-forward dates: Monday print missing, expiry on Monday
    mon, tue, wed = D("2030-06-03"), D("2030-06-04"), D("2030-06-05")
    r1 = {tue: 50.0, wed: 51.0, D("2030-06-10"): 52.0}
    r2 = {tue: 60.0, wed: 61.0, D("2030-06-10"): 62.0}
    fb = FuturesBasis(r1, r2, frozenset(), [mon], lambda d: d.weekday() < 5)
    w = fb.window(mon, D("2030-06-10"))
    if w["a"] != tue or w["ret"] is None or abs(w["ret"] - (62.0 / 60.0 - 1)) > 1e-12:
        bad.append("an expiry before the moved-forward start was treated as inside the window (got %r)" % (w["ret"],))
    return bad


def selftest():
    t0 = time.time()
    W = synth_world()
    try:
        res = run_guards(W)
    except FileNotFoundError as e:
        print("selftest FAIL: a saved page is missing (%s); G6 and G7 read the committed pages under data/cot_horizons/raw/" % e.filename)
        return 1
    names = dict(gs_ids())
    ok = True
    for gid, clean, mus in res:
        caught = bool(mus) and all(p for _lab, p in mus)
        if not clean and caught:
            print("%s %-22s caught   (clean run holds; %d mutant%s fail: %s)" % (gid, names[gid], len(mus), "" if len(mus) == 1 else "s", "; ".join(l for l, _p in mus)))
        else:
            ok = False
            if clean:
                print("%s %-22s CLEAN RUN FAILED: %s" % (gid, names[gid], "; ".join(clean)[:300]))
            for lab, p in mus:
                if not p:
                    print("%s %-22s NOT CAUGHT: the mutant %r passed the guard" % (gid, names[gid], lab))
    got = [g for g, _c, _m in res]
    if got != [g for g, _n in gs_ids()]:
        ok = False
        print("selftest FAIL: guards run %s, expected 24 in order" % got)
    dt_ = time.time() - t0
    print("%d guards, %.1f s" % (len(res), dt_))
    if dt_ > 10:
        ok = False
        print("selftest FAIL: took more than 10 s")
    print("selftest PASS" if ok else "selftest FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
