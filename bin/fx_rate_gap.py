#!/usr/bin/env python3
"""The yen and the euro against US-minus-foreign yield gaps: a weekly regression with ONE pre-registered test. Python 3 standard library only.

  python3 bin/fx_rate_gap.py fetch [--cache DIR] [--out DIR] [--sleep 2.05] [--max-requests 30]   # the only network command
  python3 bin/fx_rate_gap.py build [--cache DIR] [--out DIR]                                       # offline; byte-identical on re-run
  python3 bin/fx_rate_gap.py selftest [--no-mutants]                                               # synthetic data only; no network

Specification: _research/2026-10-18-FX-Rate-Gap-Weekly-Spec.md (with its Amendments and its "Builder decisions" section). The decision rule of
its section 4 was written before any FX series or coefficient was computed, and `build` applies it once, as written.

WHAT TOUCHES THE NETWORK. Only `fetch`. Hosts: home.treasury.gov, www.mof.go.jp, stats.bis.org, data-api.ecb.europa.eu and
api.statistiken.bundesbank.de (any other host, FRED included, is refused before a request is made, and each request must be one of the 19 exact
URLs of the request table). GET only; one request at a time; at least 2 s between request starts, remembered across invocations in
<cache>/.last_request; at most 30 requests per run; the CLAUDE.md non-SEC identification string (no address, no name); no redirect is followed.
Any HTTP status other than 200, or a body that fails its content test, writes <default cache>/STOP and ends the run. While STOP exists every
fetch refuses; only a person deletes it. A socket fault ends the invocation without latching. Nothing retries. Every request is one row of
data/fx_rate_gap/fetch_log.csv.

WHERE THE FILES LIVE. The cache (default data/vintages/fx_rate_gap/) holds every raw download and the weekly panel. It is gitignored. A --cache
path inside this repository is refused unless git reports it as ignored (and it may never sit in the committed output folder). No committed file
carries a per-week series from which a yield level can be rebuilt (spec R4, O-6).

GUARDS AND THE SELFTEST. Every guard of the spec's section 7 (G1-G21) has a test with synthetic data; `selftest` applies each mutant (a
deliberately broken variant, switched on in this process only) and requires the test to notice it. A mutant not caught is a failure.
"""
import argparse
import bisect
import contextlib
import csv
import datetime as dt
import hashlib
import http.client
import io
import math
import os
import re
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(ROOT, "data", "fx_rate_gap")
CACHE_DEFAULT = os.path.join(ROOT, "data", "vintages", "fx_rate_gap")
STOP_PATH = os.path.join(CACHE_DEFAULT, "STOP")            # fixed, whatever --cache says

# R2: the CLAUDE.md canonical string for every non-SEC host. No address, no name.
UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
HEADERS = {"User-Agent": UA, "Accept-Encoding": "identity", "Accept": "*/*"}
MIN_SLEEP = 2.05                 # R3 says at least 2 s between request starts; the 0.05 is a margin for clock granularity
MAX_REQUESTS = 30
TIMEOUT = 120
BODY_CAP = 64 * 1024 * 1024
Z95 = 1.959964

TSY_HOST, MOF_HOST, BIS_HOST, ECB_HOST, BBK_HOST = ("home.treasury.gov", "www.mof.go.jp", "stats.bis.org", "data-api.ecb.europa.eu",
                                                    "api.statistiken.bundesbank.de")
HOST_ALLOW = frozenset({TSY_HOST, MOF_HOST, BIS_HOST, ECB_HOST, BBK_HOST})
TSY_PATH = ("/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{Y}/all"
            "?type=daily_treasury_yield_curve&field_tdr_date_value={Y}&page&_format=csv")
FIRST_FETCH_YEAR, LAST_FETCH_YEAR = 2017, 2026
JGB_PATH = "/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv"
YC_PATH = ("/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.BETA0+BETA1+BETA2+BETA3+TAU1+TAU2+SR_2Y+SR_10Y+PY_2Y+PY_10Y"
           "?format=csvdata&startPeriod=2017-12-01")
BIS_PATH = "/api/v2/data/dataflow/BIS/WS_XRU/1.0/D.JP+XM.JPY+EUR.A?startPeriod=2017-12-01&format=csv"
EXR_PATH = "/service/data/EXR/D.JPY+USD.EUR.SP00.A?format=csvdata&startPeriod=2017-12-01"
FEIO_PATH = "/english/policy/international_policy/reference/feio/foreign_exchange_intervention_operations.csv"
MONTHLY = ("20260731e", "20260828e", "20260930e")
MONTHLY_PATH = "/english/policy/international_policy/reference/feio/monthly/%s.html"
BBK_PATH = ("/rest/data/BBSIS/D.I.ZST.ZI.EUR.S1311.B.A604.R02XX+R10XX.R.A.A._Z._Z.A?format=csv&lang=en&startPeriod=2017-12-01")

PARAM_KEYS = ("BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2")
YC_PREFIX = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM."

FIRST_WEEK, LAST_WEEK = dt.date(2017, 12, 29), dt.date(2026, 9, 18)
# name, first week_end, last week_end  (spec 3.5; P is the supervisor's ruling)
SAMPLES = (("FULL", dt.date(2018, 1, 5), dt.date(2026, 9, 18)), ("W1", dt.date(2018, 1, 5), dt.date(2021, 12, 31)),
           ("W2", dt.date(2022, 1, 7), dt.date(2023, 12, 29)), ("W3", dt.date(2024, 1, 5), dt.date(2026, 9, 18)),
           ("P", dt.date(2024, 3, 29), dt.date(2026, 9, 18)))
P_START = dt.date(2024, 3, 29)
EXPECTED_COUNTS = {      # the reviewer's counts (spec 3.5): weeks, intervention weeks, stale weeks, kept
    "FULL": (455, 13, 6, 436), "W1": (209, 0, 4, 205), "W2": (104, 3, 0, 101), "W3": (142, 10, 2, 130), "P": (130, 10, 2, 118)}
EXPECTED_P_IV = ("2024-05-03", "2024-07-12", "2024-07-19", "2026-05-01", "2026-05-08", "2026-07-31", "2026-08-07", "2026-08-14", "2026-08-21",
                 "2026-08-28")
EXPECTED_P_STALE = ("2025-01-03", "2025-01-10")
MARKER_WEEK = dt.date(2025, 4, 11)

# ------------------------------------------------------------------------------------------------------------------------
# mutants: deliberately broken variants, switched on only by the selftest, in this process
# ------------------------------------------------------------------------------------------------------------------------
_ACTIVE = set()


def M(name):
    return name in _ACTIVE


@contextlib.contextmanager
def mutant(name):
    added = name not in _ACTIVE
    _ACTIVE.add(name)
    try:
        yield
    finally:
        if added:
            _ACTIVE.discard(name)


class Refused(Exception):
    """A request, path or setting this script will not honour."""


class MaxRequests(Refused):
    """The request cap for this invocation was reached: an orderly end."""


class Latched(Exception):
    """A technical refusal: STOP was written (or already existed); the run ends."""


class SocketFault(Exception):
    """Timeout, reset or TLS error: the invocation ends without latching."""


class DataError(Exception):
    """A hard check on the data failed."""


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


def iso(d):
    return d.isoformat() if d is not None else ""


def assert_ua(ua=UA):
    if not M("ua_check_off"):
        if "@" in ua:
            raise Refused("the identification string contains an address")
        for var in ("SEC_UA", "CLAUDE_CODE_USER_EMAIL"):
            v = os.environ.get(var, "").strip()
            if v and (v in ua or ua in v):
                raise Refused("the identification string contains a configured contact value (not printed)")


assert_ua()


def request_table():
    """The 19 requests of the spec (section 2), in fetch order: key, host, target (path and query), cache file, kind, argument, immutable."""
    reqs = []
    for y in range(FIRST_FETCH_YEAR, LAST_FETCH_YEAR + 1):
        reqs.append(dict(key="tsy%d" % y, host=TSY_HOST, target=TSY_PATH.format(Y=y), file="tsy_%d.csv" % y, kind="tsy", arg=y,
                         immutable=y < LAST_FETCH_YEAR))
    reqs += [dict(key="jgb", host=MOF_HOST, target=JGB_PATH, file="mof_jgbcme_all.csv", kind="jgb", arg=None, immutable=False),
             dict(key="yc", host=ECB_HOST, target=YC_PATH, file="ecb_yc.csv", kind="yc", arg=None, immutable=False),
             dict(key="bis", host=BIS_HOST, target=BIS_PATH, file="bis_xru.csv", kind="bis", arg=None, immutable=False),
             dict(key="exr", host=ECB_HOST, target=EXR_PATH, file="ecb_exr.csv", kind="exr", arg=None, immutable=False),
             dict(key="feio", host=MOF_HOST, target=FEIO_PATH, file="mof_feio.csv", kind="feio", arg=None, immutable=False)]
    for m in MONTHLY:
        reqs.append(dict(key="monthly" + m, host=MOF_HOST, target=MONTHLY_PATH % m, file="mof_monthly_%s.html" % m, kind="monthly", arg=m,
                         immutable=True))
    reqs.append(dict(key="bbk", host=BBK_HOST, target=BBK_PATH, file="bbk_svensson.csv", kind="bbk", arg=None, immutable=False))
    return reqs


ALLOWED = frozenset((r["host"], r["target"]) for r in request_table())


def check_url(url):
    """Only the 19 exact requests of the table, over https, on the five allowed hosts. Returns (host, target)."""
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    target = p.path + ("?" + p.query if p.query else "")
    if M("allow_fred"):
        return host, target
    if p.scheme != "https" or p.username or p.password or p.port not in (None, 443) or p.fragment:
        raise Refused("only plain https URLs are allowed")
    if host not in HOST_ALLOW:
        raise Refused("host %s is not on the allowlist" % host)
    if (host, target) not in ALLOWED:
        raise Refused("that path is not one of the 19 requests of the spec")
    return host, target


def check_cache(cache, root=ROOT, out_dir=None):
    """The cache may be outside the repository, or inside it only where git ignores it (never in the committed output folder)."""
    real = os.path.realpath(os.path.expanduser(cache))
    rroot = os.path.realpath(root)
    if M("cache_check_off"):
        return real
    if real == rroot or real.startswith(rroot + os.sep):
        outd = os.path.realpath(out_dir or os.path.join(root, "data", "fx_rate_gap"))
        if real == outd or real.startswith(outd + os.sep):
            raise Refused("the cache may not sit in the committed output folder")
        probe = os.path.relpath(os.path.join(real, ".probe"), rroot)
        try:
            r = subprocess.run(["git", "-C", rroot, "check-ignore", "-q", "--", probe], capture_output=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            raise Refused("cannot ask git whether the cache path is ignored; use a cache outside the repository")
        if r.returncode != 0:
            raise Refused("the cache is inside the repository and git does not ignore it (raw downloads are never committed)")
    return real


# ------------------------------------------------------------------------------------------------------------------------
# parsers (every one also serves as the content test of its downloaded file)
# ------------------------------------------------------------------------------------------------------------------------
def decode_text(body):
    try:
        return body.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise DataError("not UTF-8 text")


DATE_US = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
DATE_JP = re.compile(r"(\d{4})/(\d{1,2})/(\d{1,2})")


def parse_treasury(text, year=None, min_rows=1):
    """Par yields by HEADER NAME ('2 Yr', '10 Yr'); the 2025-26 files carry an extra '1.5 Month' column, so positions differ. -> {date: (y2, y10)}"""
    rows = list(csv.reader(io.StringIO(text.lstrip("﻿"))))
    if not rows:
        raise DataError("empty Treasury file")
    hdr = [h.strip() for h in rows[0]]
    for need in ("Date", "2 Yr", "10 Yr"):
        if need not in hdr:
            raise DataError("Treasury header lacks %r" % need)
    if M("positional_treasury"):
        i2, i10 = 8, 12                                  # the 2026 layout, read by position
    else:
        i2, i10 = hdr.index("2 Yr"), hdr.index("10 Yr")
    out = {}
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        m = DATE_US.fullmatch(r[0].strip())
        if not m:
            raise DataError("Treasury date %r" % r[0])
        d = dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        if year is not None and d.year != year:
            raise DataError("Treasury row %s is outside %d" % (d, year))
        a, b = r[i2].strip(), r[i10].strip()
        if a in ("", "N/A") or b in ("", "N/A"):
            continue
        if d in out:
            raise DataError("Treasury duplicate date %s" % d)
        out[d] = (float(a), float(b))
    if len(out) < min_rows:
        raise DataError("Treasury file has %d usable rows (need %d)" % (len(out), min_rows))
    return out


def parse_mof_yields(text, min_rows=1):
    """MoF constant-maturity yields: header line 'Date,1Y,2Y,...', dates Y/M/D without padding, '-' = missing. -> {date: (y2, y10)} (None = missing)"""
    lines = text.lstrip("﻿").splitlines()
    hi = next((i for i, ln in enumerate(lines[:10]) if ln.split(",")[0].strip() == "Date"), None)
    if hi is None:
        raise DataError("MoF yield file: no 'Date' header line")
    hdr = [h.strip() for h in lines[hi].split(",")]
    if "2Y" not in hdr or "10Y" not in hdr:
        raise DataError("MoF yield file lacks 2Y or 10Y")
    i2, i10 = hdr.index("2Y"), hdr.index("10Y")
    out = {}

    def val(s):
        s = s.strip()
        if s == "-":
            return 0.0 if M("dash_as_zero") else None
        try:
            return float(s)
        except ValueError:
            raise DataError("MoF yield value %r" % s)
    for ln in lines[hi + 1:]:
        cells = ln.split(",")
        c0 = cells[0].strip()
        if not c0:
            continue
        m = DATE_JP.fullmatch(c0)
        if not m:
            if c0[0].isdigit():
                raise DataError("MoF yield date %r" % c0)
            continue                                       # a trailing note line
        d = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if d in out:
            raise DataError("MoF duplicate date %s" % d)
        out[d] = (val(cells[i2]), val(cells[i10]))
    if len(out) < min_rows:
        raise DataError("MoF yield file has %d rows (need %d)" % (len(out), min_rows))
    return out


def merge_mof(a, b):
    """Two MoF files that overlap (history and current month) must agree on every shared date."""
    out = dict(a)
    for d, v in b.items():
        if d in out and out[d] != v and not M("overlap_ignored"):
            raise DataError("MoF files disagree on %s: %r against %r" % (d, out[d], v))
        out.setdefault(d, v)
    return out


def parse_ecb_yc(text, min_dates=1):
    """ECB AAA Svensson parameters and published SR/PY yields. -> {date: {type: value}}"""
    rd = csv.reader(io.StringIO(text.lstrip("﻿")))
    hdr = next(rd, None)
    if not hdr:
        raise DataError("empty ECB yield-curve file")
    try:
        ik, it, id_, iv = hdr.index("KEY"), hdr.index("DATA_TYPE_FM"), hdr.index("TIME_PERIOD"), hdr.index("OBS_VALUE")
    except ValueError:
        raise DataError("ECB yield-curve header")
    out = {}
    for r in rd:
        if not r:
            continue
        if not r[ik].startswith(YC_PREFIX):
            raise DataError("ECB series key %r" % r[ik])
        if r[iv] == "":
            continue
        d = dt.date.fromisoformat(r[id_])
        slot = out.setdefault(d, {})
        if r[it] in slot:
            raise DataError("ECB duplicate %s %s" % (r[it], d))
        slot[r[it]] = float(r[iv])
    if len(out) < min_dates:
        raise DataError("ECB yield file has %d dates (need %d)" % (len(out), min_dates))
    return out


def parse_bis(text, min_each=1):
    """BIS daily USD rates. -> {'JP': {date: yen per USD}, 'XM': {date: euro per USD}}"""
    rd = csv.DictReader(io.StringIO(text.lstrip("﻿")))
    out = {"JP": {}, "XM": {}}
    want = {"JP": "JPY", "XM": "EUR"}
    for r in rd:
        area = r.get("REF_AREA")
        if area not in out or r.get("CURRENCY") != want[area]:
            raise DataError("BIS series %r/%r" % (area, r.get("CURRENCY")))
        if (r.get("OBS_VALUE") or "") == "":
            continue
        d = dt.date.fromisoformat(r["TIME_PERIOD"])
        if d in out[area]:
            raise DataError("BIS duplicate %s %s" % (area, d))
        out[area][d] = float(r["OBS_VALUE"])
    if min(len(out["JP"]), len(out["XM"])) < min_each:
        raise DataError("BIS file lacks rows (JP %d, XM %d)" % (len(out["JP"]), len(out["XM"])))
    return out


def parse_exr(text, min_each=1):
    """ECB euro reference rates. -> {'JPY': {date: JPY per EUR}, 'USD': {date: USD per EUR}}"""
    rd = csv.DictReader(io.StringIO(text.lstrip("﻿")))
    out = {"JPY": {}, "USD": {}}
    for r in rd:
        c = r.get("CURRENCY")
        if c not in out or r.get("CURRENCY_DENOM") != "EUR":
            raise DataError("ECB reference-rate series %r" % c)
        if (r.get("OBS_VALUE") or "") == "":
            continue
        d = dt.date.fromisoformat(r["TIME_PERIOD"])
        if d in out[c]:
            raise DataError("ECB reference-rate duplicate %s %s" % (c, d))
        out[c][d] = float(r["OBS_VALUE"])
    if min(len(out["JPY"]), len(out["USD"])) < min_each:
        raise DataError("ECB reference-rate file lacks rows")
    return out


MONTHS = {m: i + 1 for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"))}
QUARTER_RX = re.compile(r"(January|April|July|October)\s*-\s*(March|June|September|December)\s+(\d{4})")
QUARTER_END = {"March": (3, 31), "June": (6, 30), "September": (9, 30), "December": (12, 31)}


def parse_feio(raw, min_days=1):
    """MoF intervention operations CSV: CP932, amounts in 100 million yen with thousands commas. The year is written only on the first day row after a
    subtotal row or a gap and the month only when it changes, so BOTH are carried down. -> dict(days=[(date, amount)], quarters=[(end_date, subtotal,
    n_days, sum_of_days)], covered_through=date)"""
    text = raw.decode("utf-8" if M("utf8_decode") else "cp932")
    days, quarters, pending = [], [], []
    year = month = None
    for r in csv.reader(io.StringIO(text)):
        if len(r) < 7:
            continue
        c3, c4, c5, c6 = r[3].strip(), r[4].strip(), r[5].strip(), r[6].strip().replace(",", "")
        q = QUARTER_RX.fullmatch(c3)
        if q:
            end = dt.date(int(q.group(3)), *QUARTER_END[q.group(2)])
            amt = int(c6)
            quarters.append((end, amt, len(pending), sum(a for _, a in pending)))
            if M("subtotal_as_day"):
                days.append((dt.date(end.year, end.month, 1), amt))
            pending = []
            continue
        if not c5.isdigit():
            continue
        if c3.isdigit():
            year = int(c3)
        if c4:
            month = MONTHS[c4[:3].lower()]
        elif M("month_not_carried"):
            month = None
        if M("year_not_carried") and not c3.isdigit():
            continue
        if year is None or month is None:
            continue
        if not re.fullmatch(r"-?\d+", c6):
            raise DataError("intervention amount %r" % r[6])
        d = dt.date(year, month, int(c5))
        days.append((d, int(c6)))
        pending.append((d, int(c6)))
    if pending:
        raise DataError("day rows after the last subtotal row")
    if len(days) < min_days or not quarters:
        raise DataError("intervention file has %d day rows and %d subtotal rows" % (len(days), len(quarters)))
    recent = [d for d, _ in days if d >= dt.date(2018, 1, 1)]
    if len(set(recent)) != len(recent):
        raise DataError("intervention file repeats a date since 2018")      # before 2018 two currency pairs can share a day
    return dict(days=days, quarters=quarters, covered_through=max(q[0] for q in quarters))


MONTHLY_RX = re.compile(r"Total amount of foreign exchange intervention operations for the period from\s+([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})\s+through\s+"
                        r"([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})\s*<p[^>]*>&yen;\s*([\d,.]+)\s*(billion|trillion|million)?")


def parse_monthly(html):
    """MoF monthly page: 'from A through B  yen X [billion]'. -> (start, end, amount in 100 million yen, float)"""
    m = MONTHLY_RX.search(html)
    if not m:
        raise DataError("monthly intervention page: no total line")
    s = dt.date(int(m.group(3)), MONTHS[m.group(1)[:3].lower()], int(m.group(2)))
    e = dt.date(int(m.group(6)), MONTHS[m.group(4)[:3].lower()], int(m.group(5)))
    x = float(m.group(7).replace(",", ""))
    unit = m.group(8)
    yen_100m = {"billion": 10.0, "trillion": 10000.0, "million": 0.01, None: 1e-8}[unit] * x
    return s, e, yen_100m


def parse_bundesbank(text, min_rows=1):
    """Check-only: Bundesbank Svensson 10-year yield. -> {date: value}"""
    rows = list(csv.reader(io.StringIO(text.lstrip("﻿"))))
    hdr = next((r for r in rows if any("BBSIS" in c for c in r)), None)
    if hdr is None:
        raise DataError("Bundesbank header")
    j = next((i for i, c in enumerate(hdr) if "R10XX" in c and "FLAGS" not in c), None)
    if j is None:
        raise DataError("Bundesbank file lacks the 10-year column")
    out = {}
    for r in rows:
        if r and re.fullmatch(r"\d{4}-\d{2}-\d{2}", r[0]) and len(r) > j and r[j] not in (".", ""):
            out[dt.date.fromisoformat(r[0])] = float(r[j])
    if len(out) < min_rows:
        raise DataError("Bundesbank file has %d values (need %d)" % (len(out), min_rows))
    return out


def body_problem(kind, arg, body):
    """The content test of a downloaded body: None if it is the expected file, else the reason."""
    try:
        if kind == "tsy":
            parse_treasury(decode_text(body), year=arg, min_rows=100)
        elif kind == "jgb":
            parse_mof_yields(decode_text(body), min_rows=12000)
        elif kind == "yc":
            yc = parse_ecb_yc(decode_text(body), min_dates=2000)
            if sum(1 for p in yc.values() if all(k in p for k in PARAM_KEYS)) < 2000:
                raise DataError("too few dates with a full parameter set")
        elif kind == "bis":
            parse_bis(decode_text(body), min_each=2000)
        elif kind == "exr":
            parse_exr(decode_text(body), min_each=2000)
        elif kind == "feio":
            parse_feio(body, min_days=50)
        elif kind == "monthly":
            parse_monthly(decode_text(body))
        elif kind == "bbk":
            parse_bundesbank(decode_text(body), min_rows=2000)
        else:
            return "unknown file kind"
    except (DataError, ValueError, UnicodeDecodeError, KeyError) as e:
        return "%s: %s" % (type(e).__name__, e)
    return None


# ------------------------------------------------------------------------------------------------------------------------
# the fetch log and fetching: the only network code
# ------------------------------------------------------------------------------------------------------------------------
LOG_COLS = ["utc_time", "host", "path", "status", "bytes", "sha256"]
PUBLISHERS = (("U.S. Department of the Treasury (home.treasury.gov)", TSY_HOST), ("Ministry of Finance Japan (www.mof.go.jp)", MOF_HOST),
              ("European Central Bank (data-api.ecb.europa.eu)", ECB_HOST), ("Bank for International Settlements (stats.bis.org)", BIS_HOST),
              ("Deutsche Bundesbank (api.statistiken.bundesbank.de)", BBK_HOST))


def read_csv_rows(path):
    """(header, rows) of a csv with comment lines (# ...) skipped; ([], []) if absent."""
    if not os.path.exists(path):
        return [], []
    with open(path, encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh.read().splitlines(True) if not ln.startswith("#")]
    rd = list(csv.reader(io.StringIO("".join(lines))))
    return (rd[0], rd[1:]) if rd else ([], [])


def retrieval_dates(log_rows, hosts):
    ds = sorted({r[0][:10] for r in log_rows if r[1] in hosts and r[3] == "200" and r[4]})
    return ds


def source_line(log_rows, hosts, what):
    parts = []
    for name, host in PUBLISHERS:
        if host in hosts:
            ds = retrieval_dates(log_rows, {host})
            parts.append("%s retrieved %s" % (name, ", ".join(ds) if ds else "(no logged retrieval)"))
    return "# source: " + "; ".join(parts) + "; " + what


def real_opener(host, target, headers, timeout, cap):
    """GET https://host/target. Returns (status, body); body is None when it exceeds `cap`. No redirect is followed (a 3xx comes back as a status
    and latches), no cookies, the only verb is GET. Socket-level faults raise SocketFault."""
    conn = http.client.HTTPSConnection(host, timeout=timeout)
    try:
        conn.request("GET", target, headers=dict(headers))
        resp = conn.getresponse()
        status = resp.status
        if status != 200:
            return status, b""
        chunks, total = [], 0
        while True:
            b = resp.read(1 << 16)
            if not b:
                break
            total += len(b)
            if total > cap:
                return status, None
            chunks.append(b)
        return status, b"".join(chunks)
    except (OSError, http.client.HTTPException) as e:
        raise SocketFault(type(e).__name__)
    finally:
        conn.close()


class Fetcher:
    """All requests go through here. Injectable opener, clock, sleeper and STOP path make it testable without a network."""

    def __init__(self, cache, out_dir, sleep=MIN_SLEEP, max_requests=MAX_REQUESTS, opener=real_opener, wall=time.time, mono=time.monotonic,
                 sleeper=time.sleep, stop_path=STOP_PATH, now_utc=None, root=ROOT):
        if sleep < 2.0 and not M("no_pacing"):
            raise Refused("--sleep must be at least 2 seconds")
        if max_requests > MAX_REQUESTS or max_requests < 1:
            raise Refused("--max-requests must be between 1 and %d" % MAX_REQUESTS)
        self.out_dir = out_dir
        self.cache = check_cache(cache, root=root, out_dir=out_dir)
        self.sleep, self.max_requests = float(sleep), max_requests
        self.opener, self.wall, self.mono, self.sleeper = opener, wall, mono, sleeper
        self.stop_path = stop_path
        self.now_utc = now_utc or (lambda: dt.datetime.now(dt.timezone.utc))
        self.requests = 0
        self._last_mono = None
        self._last_file = os.path.join(self.cache, ".last_request")
        self.log_path = os.path.join(out_dir, "fetch_log.csv")

    def check_stop(self):
        if os.path.exists(self.stop_path) and not M("stop_ignored"):
            with open(self.stop_path, encoding="utf-8") as fh:
                why = fh.read().strip().replace("\n", " ")[:200]
            raise Latched("STOP exists at %s (%s); a person must inspect it and delete it" % (tilde(self.stop_path), why))

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
        if wait > 0 and not M("no_pacing"):
            self.sleeper(wait)

    def _stamp(self, ts):
        return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % int((ts % 1) * 1000)

    def _log(self, ts, host, target, status, nbytes, sha):
        _, rows = read_csv_rows(self.log_path)
        rows.append([self._stamp(ts), host, target, str(status), str(nbytes), sha])
        text = render_csv("fetch_log.csv", rows, source_line(rows, HOST_ALLOW, "request log of bin/fx_rate_gap.py fetch (one row per request)"))
        write_text(self.log_path, text)

    def _latch(self, reason):
        os.makedirs(os.path.dirname(self.stop_path), exist_ok=True)
        with open(self.stop_path, "w", encoding="utf-8") as fh:
            fh.write("%s UTC  %s\n" % (self.now_utc().strftime("%Y-%m-%dT%H:%M:%S"), reason))
        raise Latched(reason)

    def _get(self, host, target):
        check_url("https://" + host + target)
        if self.requests >= self.max_requests:
            raise MaxRequests("--max-requests reached (%d)" % self.max_requests)
        self._pace()
        started = self.wall()
        self._last_mono = self.mono()
        os.makedirs(self.cache, exist_ok=True)
        with open(self._last_file, "w", encoding="utf-8") as fh:
            fh.write("%r\n" % started)
        self.requests += 1
        try:
            status, body = self.opener(host, target, HEADERS, TIMEOUT, BODY_CAP)
        except SocketFault as e:
            self._log(started, host, target, "socket_fault", "", "")
            if M("latch_on_socket"):
                self._latch("socket fault (%s) for %s" % (e, target))
            raise
        return status, body, started

    def _done_today(self, host, target):
        today = self.now_utc().strftime("%Y-%m-%d")
        _, rows = read_csv_rows(self.log_path)
        return any(r[1] == host and r[2] == target and r[3] == "200" and r[4] and r[0][:10] == today for r in rows)

    def fetch_one(self, req):
        """Returns an outcome word; raises Latched / SocketFault / MaxRequests / Refused."""
        path = os.path.join(self.cache, req["file"])
        if os.path.exists(path) and (req["immutable"] or self._done_today(req["host"], req["target"])):
            return "cached"
        self.check_stop()
        status, body, started = self._get(req["host"], req["target"])
        if status != 200:
            self._log(started, req["host"], req["target"], status, "", "")
            if status // 100 == 3:
                if not M("no_latch_redirect"):
                    self._latch("HTTP %d (a redirect, not followed) for %s" % (status, req["target"][:80]))
            elif not M("no_latch_non200"):
                self._latch("HTTP %d for %s" % (status, req["target"][:80]))
            return "refused_unlatched"
        problem = "body larger than the cap" if body is None else body_problem(req["kind"], req["arg"], body)
        self._log(started, req["host"], req["target"], status, len(body or b""), sha256_of(body or b""))
        if problem:
            if not M("no_latch_bad_body"):
                self._latch("200 but not the expected file (%s) for %s" % (problem, req["target"][:80]))
            return "refused_unlatched"
        os.makedirs(self.cache, exist_ok=True)
        with open(path + ".part", "wb") as fh:
            fh.write(body)
        os.replace(path + ".part", path)
        return "saved"

    def run(self, reqs, say=print):
        saved = 0
        for req in reqs:
            out = self.fetch_one(req)
            saved += out == "saved"
            say("%-22s %s" % (req["file"], out))
        return saved


# ------------------------------------------------------------------------------------------------------------------------
# writing outputs: exact column allowlists, source lines, no causal wording (G11, G19)
# ------------------------------------------------------------------------------------------------------------------------
PANEL_COLS = ["week_end", "fx_date", "usdjpy", "eur_per_usd", "us_date", "us2", "us10", "us_date_sd", "us2_sd", "us10_sd", "jp_date", "jp2", "jp10",
              "ea_date", "ea2_sa", "ea10_sa", "gap_jp2", "gap_jp10", "slope_gap_jp", "gap_ea2", "gap_ea10", "slope_gap_ea", "dln_jpy", "dln_eur",
              "d_gap_jp2", "d_gap_jp10", "d_slope_gap_jp", "d_gap_ea2", "d_gap_ea10", "d_slope_gap_ea", "d_gap_jp2_sd", "d_slope_gap_jp_sd",
              "drop_reason"]
REG_COLS = ["role", "pair", "sample", "spec", "regressor", "variant", "n", "first_week", "last_week", "alpha", "beta", "se_hc3", "p_hc3", "se_nw4",
            "p_nw4", "beta_ci_lo", "beta_ci_hi", "r2", "vif", "hh_lag", "sum_dln", "sum_dx", "fitted_sum", "phi", "phi_ci_lo", "phi_ci_hi", "resid_sum"]
DEC_COLS = ["run_label", "n", "alpha", "n_alpha", "beta", "se_hc3", "p_hc3", "se_nw4", "p_nw4", "S", "S_all", "S_dropped", "X", "F", "phi", "phi_ci_lo",
            "phi_ci_hi", "se_placebo", "n_placebo", "halfwidth_phi", "gate", "class_primary", "class_nw4", "gate_nw4", "class_restored", "gate_restored",
            "class_sameday", "gate_sameday", "verdict_of_record", "labels"]
EVENT_COLS = ["week_end", "reason", "iv_days", "iv_amount_100m_yen", "dln_jpy", "d_gap_jp2", "fitted_term", "dln_minus_fitted"]
IVDAY_COLS = ["kind", "start", "end", "amount_100m_yen", "source_file", "release_note"]
PIN_COLS = ["source", "series", "pin_date", "value", "unit"]
CHECK_COLS = ["check_id", "description", "expected", "observed", "status"]
# The allowlists exactly as the spec prints them (section 5, the backticked column lists), typed separately from the constants above so that the
# selftest compares two independent copies, and a hash of them. G11 fails if ALLOW or the written headers drift from these.
SPEC_ALLOW = {
    "weekly_panel.csv": "week_end, fx_date, usdjpy, eur_per_usd, us_date, us2, us10, us_date_sd, us2_sd, us10_sd, jp_date, jp2, jp10, ea_date, ea2_sa, ea10_sa, gap_jp2, gap_jp10, slope_gap_jp, gap_ea2, gap_ea10, slope_gap_ea, dln_jpy, dln_eur, d_gap_jp2, d_gap_jp10, d_slope_gap_jp, d_gap_ea2, d_gap_ea10, d_slope_gap_ea, d_gap_jp2_sd, d_slope_gap_jp_sd, drop_reason",
    "regressions.csv": "role, pair, sample, spec, regressor, variant, n, first_week, last_week, alpha, beta, se_hc3, p_hc3, se_nw4, p_nw4, beta_ci_lo, beta_ci_hi, r2, vif, hh_lag, sum_dln, sum_dx, fitted_sum, phi, phi_ci_lo, phi_ci_hi, resid_sum",
    "decision.csv": "run_label, n, alpha, n_alpha, beta, se_hc3, p_hc3, se_nw4, p_nw4, S, S_all, S_dropped, X, F, phi, phi_ci_lo, phi_ci_hi, se_placebo, n_placebo, halfwidth_phi, gate, class_primary, class_nw4, gate_nw4, class_restored, gate_restored, class_sameday, gate_sameday, verdict_of_record, labels",
    "event_weeks.csv": "week_end, reason, iv_days, iv_amount_100m_yen, dln_jpy, d_gap_jp2, fitted_term, dln_minus_fitted",
    "intervention_days.csv": "kind, start, end, amount_100m_yen, source_file, release_note",
    "pins.csv": "source, series, pin_date, value, unit",
    "checks.csv": "check_id, description, expected, observed, status",
    "fetch_log.csv": "utc_time, host, path, status, bytes, sha256",
}
SPEC_ALLOW_SHA256 = "b4ecde725fdeffea704bbc80972443b79833f529df71a9b3c43aa0dfe9338f68"     # of \n.join(name:cols with no spaces) over the sorted names

ALLOW = {"weekly_panel.csv": PANEL_COLS, "regressions.csv": REG_COLS, "decision.csv": DEC_COLS, "event_weeks.csv": EVENT_COLS,
         "intervention_days.csv": IVDAY_COLS, "pins.csv": PIN_COLS, "checks.csv": CHECK_COLS, "fetch_log.csv": LOG_COLS}

CAUSAL_RX = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention)\b", re.I)


def causal_hits(text):
    return sorted({m.group(0).lower() for m in CAUSAL_RX.finditer(text)})


def allowlist(name):
    cols = list(ALLOW[name])
    if M("allow_drift") and name == "regressions.csv":
        cols[cols.index("phi")] = "share"
    return cols


def check_header(name, header):
    allow = allowlist(name)
    if M("extra_column"):
        ok = list(header[:len(allow)]) == allow
    elif M("renamed_column"):
        ok = len(header) == len(allow)
    else:
        ok = list(header) == allow
    if not ok:
        raise DataError("%s: header %r is not the exact column allowlist" % (name, list(header)))


def render_csv(name, rows, source, header=None, extra_comments=()):
    header = allowlist(name) if header is None else header
    check_header(name, header)
    out = io.StringIO()
    out.write(source + "\n")
    for c in extra_comments:
        out.write("# " + c + "\n")
    w = csv.writer(out, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        if len(r) != len(header):
            raise DataError("%s: a row has %d cells, the header %d" % (name, len(r), len(header)))
        w.writerow(r)
    text = out.getvalue()
    if not text.startswith("# source:"):
        raise DataError("%s: the first line is not a `# source:` line" % name)
    guard_text(name, text)
    return text


def guard_text(name, text):
    hits = causal_hits(text)
    if hits and not M("causal_guard_off"):
        raise DataError("%s: causal wording %s" % (name, hits))
    if os.path.expanduser("~") != "~" and os.path.expanduser("~") in text:
        raise DataError("%s: an absolute home path would be published" % name)


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


# ------------------------------------------------------------------------------------------------------------------------
# euro-area yields: Svensson curve, semiannual par yield recomputed from the parameters (spec 3.2)
# ------------------------------------------------------------------------------------------------------------------------
def svensson_z(T, b0, b1, b2, b3, t1, t2):
    """Continuously compounded zero yield in percent."""
    x1, x2 = T / t1, T / t2
    e1, e2 = math.exp(-x1), math.exp(-x2)
    f1, f2 = (1 - e1) / x1, (1 - e2) / x2
    return b0 + b1 * f1 + b2 * (f1 - e1) + b3 * (f2 - e2)


def disc(T, pr):
    return math.exp(-svensson_z(T, *pr) * T / 100.0)


def par_semiannual(T, pr):
    """Par yield of a semiannual-coupon bond on the continuous curve, percent: 200 (1 - d(T)) / sum_{i=1}^{2T} d(i/2)."""
    return 200.0 * (1 - disc(T, pr)) / sum(disc(i / 2.0, pr) for i in range(1, int(round(2 * T)) + 1))


def par_continuous(T, pr, steps=20000):
    """The ECB's continuous-coupon par yield: (1 - d(T)) / integral_0^T d(t) dt, midpoint rule, percent."""
    b0, b1, b2, b3, t1, t2 = pr
    h = T / steps
    s = 0.0
    for k in range(steps):
        t = (k + 0.5) * h
        e1, e2 = math.exp(-t / t1), math.exp(-t / t2)
        f1, f2 = (1 - e1) * t1 / t, (1 - e2) * t2 / t
        z = b0 + b1 * f1 + b2 * (f1 - e1) + b3 * (f2 - e2)
        s += math.exp(-z * t / 100.0)
    return 100.0 * (1 - disc(T, pr)) / (s * h)


def ea_semiannual(T, pr):
    """The euro-area gap leg, semiannual par yield (the G3 mutants put the continuous zero or the continuous-coupon par in its place)."""
    if M("ea_sa_as_sr"):
        return svensson_z(T, *pr)
    if M("ea_sa_as_py"):
        return par_continuous(T, pr)
    return par_semiannual(T, pr)


def params_of(p):
    return tuple(p[k] for k in PARAM_KEYS)


def usable_yc(yc):
    """Split the ECB dates into usable ones and quarantined ones. A date whose parameter set is incomplete, or whose parameters do not reproduce the
    ECB's own published SR_2Y and SR_10Y within 1e-6, cannot feed the euro leg (spec 3.2 asks for the check, not for what to do on a miss):
    it is left out like a missing day and named in checks.csv C05. -> (clean, incomplete [dates], quarantined {date: max |SR diff|})"""
    clean, incomplete, quar = {}, [], {}
    for d, p in yc.items():
        if not all(k in p for k in PARAM_KEYS):
            incomplete.append(d)
            continue
        if "SR_2Y" in p and "SR_10Y" in p and not M("no_quarantine"):
            pr = params_of(p)
            err = max(abs(svensson_z(T, *pr) - p["SR_%dY" % T]) for T in (2, 10))
            if err > 1e-6:
                quar[d] = err
                continue
        clean[d] = p
    return clean, sorted(incomplete), quar


def ea_selfcheck(p, midpoint=True):
    """Max absolute differences of the recomputed zero (vs SR_2Y, SR_10Y) and, optionally, continuous-coupon par (vs PY_2Y, PY_10Y)."""
    pr = params_of(p)
    sr = max(abs(svensson_z(T, *pr) - p["SR_%dY" % T]) for T in (2, 10))
    py = max(abs(par_continuous(T, pr) - p["PY_%dY" % T]) for T in (2, 10)) if midpoint else None
    return sr, py


# ------------------------------------------------------------------------------------------------------------------------
# least squares by hand: HC3 (primary), Newey-West lag 4 (check); matrix algebra for k <= 3
# ------------------------------------------------------------------------------------------------------------------------
def invert(A):
    n = len(A)
    M_ = [list(map(float, A[i])) + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M_[r][c]))
        if abs(M_[p][c]) < 1e-14:
            raise DataError("singular design matrix")
        M_[c], M_[p] = M_[p], M_[c]
        piv = M_[c][c]
        M_[c] = [v / piv for v in M_[c]]
        for r in range(n):
            if r != c and M_[r][c] != 0.0:
                fct = M_[r][c]
                M_[r] = [a - fct * b for a, b in zip(M_[r], M_[c])]
    return [row[n:] for row in M_]


def pnorm2(z):
    """Two-sided normal p-value."""
    return math.erfc(abs(z) / math.sqrt(2.0))


def ols(y, X, lag=4):
    """OLS of y on a constant and the columns of X (list of rows). Returns b (constant first), residuals, HC0/HC1/HC3 and Newey-West standard errors."""
    n = len(y)
    const = not M("no_constant")
    A = [([1.0] + list(r)) if const else list(r) for r in X]
    k = len(A[0])
    if n <= k:
        raise DataError("too few observations (%d) for %d coefficients" % (n, k))
    XtX = [[sum(a[i] * a[j] for a in A) for j in range(k)] for i in range(k)]
    inv = invert(XtX)
    Xty = [sum(a[i] * yy for a, yy in zip(A, y)) for i in range(k)]
    b = [sum(inv[i][j] * Xty[j] for j in range(k)) for i in range(k)]
    e = [yy - sum(a[i] * b[i] for i in range(k)) for a, yy in zip(A, y)]
    h = [sum(a[i] * inv[i][j] * a[j] for i in range(k) for j in range(k)) for a in A]
    if any(1 - hh < 1e-9 for hh in h):
        raise DataError("a leverage of 1 (HC3 undefined)")

    def sand(w):
        om = [[sum(w[t] * A[t][i] * A[t][j] for t in range(n)) for j in range(k)] for i in range(k)]
        V = [[sum(inv[i][p] * om[p][q] * inv[q][j] for p in range(k) for q in range(k)) for j in range(k)] for i in range(k)]
        return [math.sqrt(V[i][i]) for i in range(k)]
    se_hc0 = sand([ei * ei for ei in e])
    se_hc1 = sand([ei * ei * n / (n - k) for ei in e])
    se_hc3 = sand([ei * ei / (1 - hh) ** 2 for ei, hh in zip(e, h)])
    L = 0 if M("nw_lag0") else lag
    om = [[sum(e[t] * e[t] * A[t][i] * A[t][j] for t in range(n)) for j in range(k)] for i in range(k)]
    for l in range(1, L + 1):
        w = 1.0 - l / (L + 1.0)
        for t in range(l, n):
            for i in range(k):
                for j in range(k):
                    om[i][j] += w * e[t] * e[t - l] * (A[t][i] * A[t - l][j] + A[t - l][i] * A[t][j])
    V = [[sum(inv[i][p] * om[p][q] * inv[q][j] for p in range(k) for q in range(k)) for j in range(k)] for i in range(k)]
    se_nw = [math.sqrt(max(V[i][i], 0.0)) for i in range(k)]
    ybar = sum(y) / n
    sst = sum((yy - ybar) ** 2 for yy in y)
    ssr = sum(ei * ei for ei in e)
    se_primary = se_hc0 if M("hc0") else (se_hc1 if M("hc1") else se_hc3)
    return dict(b=b, e=e, n=n, k=k, const=const, se_hc0=se_hc0, se_hc1=se_hc1, se_hc3=se_primary, se_hc3_true=se_hc3, se_nw=se_nw,
                r2=(1 - ssr / sst) if sst > 0 else None)


def fit(rows, ycol, xcols):
    """One regression. The design is EXACTLY a constant and the gap-change column(s) (spec 3.3: no amount, dummy or flow). Returns a dict."""
    y = [r[ycol] for r in rows]
    X = [[r[c] for c in xcols] for r in rows]
    design = ["const"] + list(xcols)
    if M("amount_regressor"):
        X = [x + [sum(a for _, a in r.get("_iv_days", []))] for x, r in zip(X, rows)]
        design.append("iv_amount")
    res = ols(y, X)
    off = 1 if res["const"] else 0
    alpha = res["b"][0] if res["const"] else 0.0
    resid_sum = sum(res["e"])
    if abs(resid_sum) > 1e-8:
        raise DataError("residuals do not sum to zero (%.3g): the constant is missing" % resid_sum)
    n = res["n"]
    out = dict(n=n, alpha=alpha, design=design, y=y, resid_sum=resid_sum, r2=res["r2"], regs=[])
    for j, c in enumerate(xcols):
        beta = res["b"][off + j]
        dx = sum(r[c] for r in rows)
        fitted = beta * dx + (n * alpha if M("f_includes_alpha") else 0.0)
        out["regs"].append(dict(name=c, beta=beta, se_hc3=res["se_hc3"][off + j], se_nw=res["se_nw"][off + j], sum_dx=dx, fitted_sum=fitted,
                                p_hc3=pnorm2(beta / res["se_hc3"][off + j]), p_nw=pnorm2(beta / res["se_nw"][off + j])))
    out["res"] = res
    return out


def corr(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    sab = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    saa = sum((x - ma) ** 2 for x in a)
    sbb = sum((y - mb) ** 2 for y in b)
    return sab / math.sqrt(saa * sbb) if saa > 0 and sbb > 0 else None


def sd(v):
    m = sum(v) / len(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def placebo_betas(y, x):
    """Slope on every circular shift of x by k = 13 ... n-13 weeks (spec 4.2): n - 25 of them."""
    n = len(y)
    ybar = sum(y) / n
    out = []
    first = 0 if M("placebo_shift0") else 13
    for k in range(first, n - 12):
        xs = x[n - k:] + x[:n - k]
        xb = sum(xs) / n
        sxx = sum((v - xb) ** 2 for v in xs)
        out.append(sum((v - xb) * (yy - ybar) for v, yy in zip(xs, y)) / sxx)
    return out


# ------------------------------------------------------------------------------------------------------------------------
# alignment: weeks, dates, FX, gaps, changes, stale legs, intervention weeks (spec 3.1, 3.2, 3.4)
# ------------------------------------------------------------------------------------------------------------------------
def last_on_or_before(dates, d, strict=False):
    i = bisect.bisect_left(dates, d) if strict else bisect.bisect_right(dates, d)
    return dates[i - 1] if i > 0 else None


def pick_dates(we, ecb_ref, us_dates, jp_dates, ea_dates):
    """(fx_date, us_date, us_date_sd, jp_date, ea_date) for the week ending Friday `we`.
    fx_date is the last day of the week with an ECB reference rate. No rate leg is observed after the FX price: US and euro-area legs are strictly
    BEFORE fx_date, Japan's on or before it."""
    fx = last_on_or_before(ecb_ref, we)
    if fx is None or fx < we - dt.timedelta(days=4):
        raise DataError("no ECB reference rate in the week ending %s" % we)
    if M("no_fx_fallback"):
        fx = we
    us = last_on_or_before(us_dates, fx, strict=not M("same_day_us"))
    us_sd = last_on_or_before(us_dates, fx)
    jp = last_on_or_before(jp_dates, fx)
    ea = last_on_or_before(ea_dates, fx, strict=True)
    return fx, us, us_sd, jp, ea


def fx_pair(bis, exr, d):
    """(yen per USD, euro per USD, ECB-cross yen, ECB-cross euro) on d. Both pairs are FOREIGN CURRENCY PER US DOLLAR (spec 3.2)."""
    usd, jp_e = exr["USD"].get(d), exr["JPY"].get(d)
    if usd is None or jp_e is None:
        raise DataError("no ECB reference rate on %s" % d)
    cj, ce = jp_e / usd, 1.0 / usd
    bj, be = bis["JP"].get(d), bis["XM"].get(d)
    jpy = bj if bj is not None else cj
    eur = be if be is not None else ce
    if M("eur_usd_per_eur"):
        eur = 1.0 / eur
    return jpy, eur, cj, ce


def gapf(us, foreign):
    """US minus foreign, percentage points."""
    return (foreign - us) if M("gap_foreign_minus_us") else (us - foreign)


def span_ok(d_prev, d):
    return d_prev is not None and d is not None and 4 <= (d - d_prev).days <= 10


def make_weeks(tsy, jgb, yc, bis, exr, first=FIRST_WEEK, last=LAST_WEEK, selfcheck=None):
    """The weekly rows (levels only) from the parsed raw data. `selfcheck`, if given, collects the Svensson reproduction errors per ECB date."""
    ecb_ref = sorted(set(exr["JPY"]) & set(exr["USD"]))
    us_dates = sorted(tsy)
    jp_dates = sorted(d for d, (a, b) in jgb.items() if a is not None and b is not None)
    ea_dates = sorted(d for d, p in yc.items() if all(k in p for k in PARAM_KEYS))
    rows, seen = [], set()
    we = first
    while we <= last:
        key = we.isocalendar()[:2]
        if key in seen:
            raise DataError("duplicate ISO week %s for %s" % (key, we))
        seen.add(key)
        fx, us, us_sd, jp, ea = pick_dates(we, ecb_ref, us_dates, jp_dates, ea_dates)
        jpy, eur, cj, ce = fx_pair(bis, exr, fx)
        pr = params_of(yc[ea])
        if selfcheck is not None and ea not in selfcheck:
            selfcheck[ea] = ea_selfcheck(yc[ea])
        rows.append(dict(week_end=we, fx_date=fx, usdjpy=jpy, eur_per_usd=eur, us_date=us, us2=tsy[us][0], us10=tsy[us][1], us_date_sd=us_sd,
                         us2_sd=tsy[us_sd][0], us10_sd=tsy[us_sd][1], jp_date=jp, jp2=jgb[jp][0], jp10=jgb[jp][1], ea_date=ea,
                         ea2_sa=ea_semiannual(2, pr), ea10_sa=ea_semiannual(10, pr), _cross_jpy=cj, _cross_eur=ce,
                         _bis_missing=(fx not in bis["JP"] or fx not in bis["XM"])))
        we += dt.timedelta(days=7)
    return rows


def finish_panel(rows, days=(), blocks=()):
    """Gaps, weekly changes, stale legs and intervention weeks, in place. days: [(date, amount_100m_yen)]; blocks: [(start, end, amount_100m_yen)]."""
    for r in rows:
        for tag, a, b in (("jp", "jp2", "jp10"), ("ea", "ea2_sa", "ea10_sa")):
            g2, g10 = gapf(r["us2"], r[a]), gapf(r["us10"], r[b])
            r["gap_%s2" % tag], r["gap_%s10" % tag], r["slope_gap_%s" % tag] = g2, g10, g10 - g2
        g2s, g10s = gapf(r["us2_sd"], r["jp2"]), gapf(r["us10_sd"], r["jp10"])
        r["_gap_jp2_sd"], r["_slope_gap_jp_sd"] = g2s, g10s - g2s
    names = ("gap_jp2", "gap_jp10", "slope_gap_jp", "gap_ea2", "gap_ea10", "slope_gap_ea", "_gap_jp2_sd", "_slope_gap_jp_sd")
    dn = ("d_gap_jp2", "d_gap_jp10", "d_slope_gap_jp", "d_gap_ea2", "d_gap_ea10", "d_slope_gap_ea", "d_gap_jp2_sd", "d_slope_gap_jp_sd")
    for i, r in enumerate(rows):
        r["_stale_jp"] = r["_stale_ea"] = r["_stale_jp_sd"] = False
        r["_iv_days"], r["_iv_dated"], r["_iv_block"] = [], False, False
        if i == 0:
            r["dln_jpy"] = r["dln_eur"] = None
            for d in dn:
                r[d] = None
            continue
        p = rows[i - 1]
        r["dln_jpy"] = math.log(r["usdjpy"] / p["usdjpy"])
        r["dln_eur"] = math.log(r["eur_per_usd"] / p["eur_per_usd"])
        if M("shift_regressor"):                       # the regressor of week t-1 stands in for week t (a lag)
            for nm, d in zip(names, dn):
                r[d] = (p[nm] - rows[i - 2][nm]) if i >= 2 else 0.0
        else:
            for nm, d in zip(names, dn):
                r[d] = r[nm] - p[nm]
        if not M("no_stale_check"):
            r["_stale_jp"] = not (span_ok(p["us_date"], r["us_date"]) and span_ok(p["jp_date"], r["jp_date"]))
            r["_stale_ea"] = not (span_ok(p["us_date"], r["us_date"]) and span_ok(p["ea_date"], r["ea_date"]))
            r["_stale_jp_sd"] = not (span_ok(p["us_date_sd"], r["us_date_sd"]) and span_ok(p["jp_date"], r["jp_date"]))
        lo, hi = p["fx_date"], r["fx_date"]
        r["_iv_days"] = [(d, a) for d, a in days if ((lo < d if M("iv_exclusive_start") else lo <= d) and d <= hi)]
        r["_iv_dated"] = bool(r["_iv_days"])
        if not M("iv_block_ignored"):
            for s, e, a in blocks:
                if (a != 0 or M("iv_zero_block_dropped")) and not (e < lo or s > hi):
                    r["_iv_block"] = True
    for r in rows:
        r["drop_reason"] = "iv_dated" if r["_iv_dated"] else ("iv_block" if r["_iv_block"] else ("stale_leg" if r["_stale_jp"] else ""))
    return rows


def sample_bounds():
    return {nm: (dt.date(2024, 3, 22) if (nm == "P" and M("p_start_0322")) else lo, hi) for nm, lo, hi in SAMPLES}


def week_rows(rows, sample):
    """Every week with a change whose week_end lies in the sample."""
    lo, hi = sample_bounds()[sample]
    return [r for i, r in enumerate(rows) if i >= 1 and lo <= r["week_end"] <= hi]


def kept_rows(rows, sample, pair, variant="base"):
    """The weeks a regression uses. Yen: intervention weeks and stale weeks dropped ('restored' puts the intervention weeks back, 'sameday' uses the
    same-calendar-Friday stale rule). Euro: stale weeks only."""
    out = []
    for r in week_rows(rows, sample):
        if pair == "yen":
            if (r["_stale_jp_sd"] if variant == "sameday" else r["_stale_jp"]):
                continue
            if (r["_iv_dated"] or r["_iv_block"]) and variant != "restored" and not M("kept_keeps_iv"):
                continue
        elif r["_stale_ea"]:
            continue
        out.append(r)
    return out


# ------------------------------------------------------------------------------------------------------------------------
# the decision rule of section 4 (pure functions of numbers)
# ------------------------------------------------------------------------------------------------------------------------
CLS_HALF = "WEEKLY 2Y-GAP TERM ACCOUNTS FOR AT LEAST HALF"
CLS_OTHER = "WEEKLY 2Y-GAP TERM POINTS THE OTHER WAY"
CLS_LTQ = "WEEKLY 2Y-GAP TERM ACCOUNTS FOR LESS THAN A QUARTER"
CLS_UNC = "UNCLASSIFIED"
S_FLOOR, X_FLOOR, HALFWIDTH_MAX = 0.01, 0.5, 0.25


def phi_interval(beta, se, X, S):
    lo, hi = beta - Z95 * se, beta + Z95 * se
    a, b = lo * X / S, hi * X / S
    return (a, b) if M("unsorted_phi") else (min(a, b), max(a, b))


def classify(beta, se, X, S, S_all=None):
    """cls(beta, SE, X, S) of spec 4.3, with no power gate inside it. Returns a dict."""
    floor_s = abs(S) <= S_FLOOR and not M("no_s_floor")
    floor_x = abs(X) < X_FLOOR and not M("no_x_floor")
    if floor_s or floor_x:
        return dict(cls=CLS_UNC, phi=None, phi_lo=None, phi_hi=None, p=pnorm2(beta / se), why="|S| <= 0.01" if floor_s else "|X| < 0.5pp")
    denom = S_all if (M("phi_s_all") and S_all is not None) else S
    phi = beta * X / denom
    lo, hi = phi_interval(beta, se, X, denom)
    p = pnorm2(beta / se)
    if M("grok_abs_rule"):
        c = CLS_LTQ if abs(phi) < 0.25 else CLS_UNC
    elif beta > 0 and p < 0.05 and phi >= 0.5 and lo > 0.25:
        c = CLS_HALF
    elif hi < 0:
        c = CLS_OTHER
    elif 0 <= hi < 0.25:
        c = CLS_LTQ
    else:
        c = CLS_UNC
    return dict(cls=c, phi=phi, phi_lo=lo, phi_hi=hi, p=p, why="")


def halfwidth(se_gate, X, S):
    return None if abs(S) <= S_FLOOR else Z95 * se_gate * abs(X) / abs(S)


def gate_word(hw):
    return "PASS" if (hw is not None and hw <= HALFWIDTH_MAX) else "FAIL"


def decide(prim, variants):
    """prim: dict(beta, se_hc3, se_nw4, X, S, S_all, se_placebo). variants: {'restored': dict(beta, se_hc3, X, S, S_all, se_placebo), 'sameday': ...}.
    Returns the classes, the gates and the verdict of record (spec 4.3)."""
    out = {}
    se_gate = max(prim["se_placebo"], prim["se_hc3"])
    hw = halfwidth(se_gate, prim["X"], prim["S"])
    out["halfwidth"], out["gate"] = hw, gate_word(hw)
    cp = classify(prim["beta"], prim["se_hc3"], prim["X"], prim["S"], prim["S_all"])
    ca = classify(prim["beta"], prim["se_nw4"], prim["X"], prim["S"], prim["S_all"])
    hwa = halfwidth(max(prim["se_placebo"], prim["se_nw4"]), prim["X"], prim["S"])
    out.update(primary=cp, nw4=ca, gate_nw4=gate_word(hwa))
    for nm in ("restored", "sameday"):
        v = variants[nm]
        out[nm] = classify(v["beta"], v["se_hc3"], v["X"], v["S"], v["S_all"])
        out["gate_" + nm] = gate_word(halfwidth(max(v["se_placebo"], v["se_hc3"]), v["X"], v["S"]))
    labels = []
    if abs(prim["S"]) <= S_FLOOR and not M("no_s_floor"):
        verdict = "INCONCLUSIVE (|S| <= 0.01)"
    elif abs(prim["X"]) < X_FLOOR and not M("no_x_floor"):
        verdict = "INCONCLUSIVE (|X| < 0.5pp)"
    elif out["gate"] == "FAIL" and not M("gate_skipped"):
        verdict = "INCONCLUSIVE (underpowered)"
    else:
        flips = [t for t, nm in (("a", "nw4"), ("b", "restored"), ("c", "sameday")) if out[nm]["cls"] != cp["cls"]]
        if flips and not M("ignore_variant_flip"):
            verdict = "INCONCLUSIVE (fragile: %s)" % "/".join(flips)
        elif cp["cls"] == CLS_UNC:
            verdict = "INCONCLUSIVE"
        else:
            verdict = cp["cls"]
    out["verdict"] = verdict
    if prim["beta"] > 0 and cp["p"] < 0.05:
        labels.append("co-moves week to week")
    else:
        labels.append("no detectable weekly co-movement at MDE = 2.8*SE_gate = %s" % f(2.8 * se_gate, 6))
    if prim["beta"] < 0 and cp["p"] < 0.05:
        labels.append("wrong-signed co-movement")
    out["labels"] = labels
    return out


# ------------------------------------------------------------------------------------------------------------------------
# the analysis: regressions.csv, decision.csv, event_weeks.csv
# ------------------------------------------------------------------------------------------------------------------------
SPECS = {"yen": (("gap2", ["d_gap_jp2"]), ("slope", ["d_slope_gap_jp"]), ("gap10", ["d_gap_jp10"]), ("joint", ["d_gap_jp2", "d_gap_jp10"])),
         "euro": (("gap2", ["d_gap_ea2"]), ("slope", ["d_slope_gap_ea"]), ("gap10", ["d_gap_ea10"]), ("joint", ["d_gap_ea2", "d_gap_ea10"]))}
YCOL = {"yen": "dln_jpy", "euro": "dln_eur"}
SD_COL = {"d_gap_jp2": "d_gap_jp2_sd", "d_slope_gap_jp": "d_slope_gap_jp_sd"}


def reg_rows(role, pair, sample, spec, variant, kept, xcols):
    """The rows of regressions.csv for one regression (one per regressor)."""
    fr = fit(kept, YCOL[pair], xcols)
    S = sum(fr["y"])
    vif = None
    if len(xcols) == 2:
        r_ = corr([r[xcols[0]] for r in kept], [r[xcols[1]] for r in kept])
        vif = 1.0 / (1.0 - r_ * r_)
    out = []
    for rg in fr["regs"]:
        se = rg["se_nw"] if variant == "nw4" else rg["se_hc3"]
        phi = plo = phi_hi = None
        if abs(S) > S_FLOOR:
            phi = rg["fitted_sum"] / S
            plo, phi_hi = phi_interval(rg["beta"], se, rg["sum_dx"], S)
        out.append(dict(role=role, pair=pair, sample=sample, spec=spec, regressor=rg["name"], variant=variant, n=fr["n"],
                        first_week=kept[0]["week_end"], last_week=kept[-1]["week_end"], alpha=fr["alpha"], beta=rg["beta"], se_hc3=rg["se_hc3"],
                        p_hc3=rg["p_hc3"], se_nw4=rg["se_nw"], p_nw4=rg["p_nw"], beta_ci_lo=rg["beta"] - Z95 * se, beta_ci_hi=rg["beta"] + Z95 * se,
                        r2=fr["r2"], vif=vif, hh_lag=0, sum_dln=S, sum_dx=rg["sum_dx"], fitted_sum=rg["fitted_sum"], phi=phi, phi_ci_lo=plo,
                        phi_ci_hi=phi_hi, resid_sum=fr["resid_sum"]))
    return out


def reg_text_row(r):
    nd = 6
    return [r["role"], r["pair"], r["sample"], r["spec"], r["regressor"], r["variant"], str(r["n"]), iso(r["first_week"]), iso(r["last_week"]),
            f(r["alpha"], nd), f(r["beta"], nd), f(r["se_hc3"], nd), f(r["p_hc3"], nd), f(r["se_nw4"], nd), f(r["p_nw4"], nd), f(r["beta_ci_lo"], nd),
            f(r["beta_ci_hi"], nd), f(r["r2"], nd), f(r["vif"], 3), str(r["hh_lag"]), f(r["sum_dln"], nd), f(r["sum_dx"], nd), f(r["fitted_sum"], nd),
            f(r["phi"], nd), f(r["phi_ci_lo"], nd), f(r["phi_ci_hi"], nd), "%.2e" % r["resid_sum"] if abs(r["resid_sum"]) >= 1e-12 else "0"]


def variant_inputs(rows, variant):
    """The primary regression (yen, P, 2-year gap) in one of its four dress: base, nw4 (same fit), restored, sameday. Returns the numbers the rule needs."""
    kvar = variant if variant in ("restored", "sameday") else "base"
    kept = kept_rows(rows, "P", "yen", kvar)
    xcol = SD_COL["d_gap_jp2"] if variant == "sameday" else "d_gap_jp2"
    fr = fit(kept, "dln_jpy", [xcol])
    rg = fr["regs"][0]
    x = [r[xcol] for r in kept]
    plac = placebo_betas(fr["y"], x)
    S_all = sum(r["dln_jpy"] for r in week_rows(rows, "P"))
    S = sum(fr["y"])
    return dict(beta=rg["beta"], se_hc3=rg["se_hc3"], se_nw4=rg["se_nw"], p_hc3=rg["p_hc3"], p_nw4=rg["p_nw"], X=rg["sum_dx"], S=S, S_all=S_all,
                S_dropped=sum(r["dln_jpy"] for r in week_rows(rows, "P") if r not in kept), se_placebo=sd(plac), n_placebo=len(plac),
                n=fr["n"], alpha=fr["alpha"], kept=kept, fr=fr)


def sample_counts(rows):
    out = {}
    for nm, _, _ in SAMPLES:
        w = week_rows(rows, nm)
        iv = [r for r in w if r["drop_reason"] in ("iv_dated", "iv_block")]
        st = [r for r in w if r["drop_reason"] == "stale_leg"]
        out[nm] = dict(weeks=len(w), iv=len(iv), stale=len(st), kept=len(kept_rows(rows, nm, "yen")), iv_weeks=[iso(r["week_end"]) for r in iv],
                       stale_weeks=[iso(r["week_end"]) for r in st], euro_kept=len(kept_rows(rows, nm, "euro")))
    return out


def analyze(rows, run_label="synthetic"):
    """Everything computed from the finished panel rows. Returns a dict."""
    regs, fits = [], {}
    for pair in ("yen", "euro"):
        for sample, _, _ in SAMPLES:
            if M("drop_full") and sample == "FULL":
                continue
            kept = kept_rows(rows, sample, pair)
            for spec, xcols in SPECS[pair]:
                role = "DESCRIPTIVE"
                if pair == "yen" and sample == "P" and spec == ("slope" if M("primary_slope") else "gap2"):
                    role = "PRIMARY"
                elif pair == "yen" and sample == "P" and spec == ("gap2" if M("primary_slope") else "slope"):
                    role = "SEPARATE"
                elif M("two_primaries") and pair == "yen" and sample == "W3" and spec == "gap2":
                    role = "PRIMARY"
                regs += reg_rows(role, pair, sample, spec, "base", kept, xcols)
    for spec, xcols in (("gap2", ["d_gap_jp2"]), ("slope", ["d_slope_gap_jp"])):
        for variant in ("nw4", "restored", "sameday"):
            kept = kept_rows(rows, "P", "yen", variant if variant != "nw4" else "base")
            xc = [SD_COL[c] for c in xcols] if variant == "sameday" else xcols
            regs += reg_rows("CHECK", "yen", "P", spec, variant, kept, xc)
    nprim = sum(1 for r in regs if r["role"] == "PRIMARY")
    if nprim != 1:
        raise DataError("regressions.csv must hold exactly one PRIMARY row, not %d" % nprim)
    prim_row = next(r for r in regs if r["role"] == "PRIMARY")
    if not M("two_primaries") and not M("primary_slope") and not M("p_start_0322"):
        assert prim_row["pair"] == "yen" and prim_row["sample"] == "P" and prim_row["spec"] == "gap2"
    base = variant_inputs(rows, "base")
    var = {"restored": variant_inputs(rows, "restored"), "sameday": variant_inputs(rows, "sameday")}
    dc = decide(base, var)
    F = base["beta"] * base["X"]
    n_alpha = base["n"] * base["alpha"]
    if abs(base["S"] - (n_alpha + F)) > 1e-9:
        raise DataError("S = n*alpha + F fails (%.3g)" % (base["S"] - n_alpha - F))
    if abs(base["S_all"] - (base["S"] + base["S_dropped"])) > 1e-9:
        raise DataError("S_all = S + S_dropped fails")
    se_gate = max(base["se_placebo"], base["se_hc3"])
    cp = dc["primary"]
    dec = dict(run_label=run_label, n=base["n"], alpha=base["alpha"], n_alpha=n_alpha, beta=base["beta"], se_hc3=base["se_hc3"], p_hc3=base["p_hc3"],
               se_nw4=base["se_nw4"], p_nw4=base["p_nw4"], S=base["S"], S_all=base["S_all"], S_dropped=base["S_dropped"], X=base["X"], F=F,
               phi=cp["phi"], phi_ci_lo=cp["phi_lo"], phi_ci_hi=cp["phi_hi"], se_placebo=base["se_placebo"], n_placebo=base["n_placebo"],
               halfwidth_phi=dc["halfwidth"], gate=dc["gate"], class_primary=cp["cls"], class_nw4=dc["nw4"]["cls"], gate_nw4=dc["gate_nw4"],
               class_restored=dc["restored"]["cls"], gate_restored=dc["gate_restored"], class_sameday=dc["sameday"]["cls"],
               gate_sameday=dc["gate_sameday"], verdict_of_record=dc["verdict"], labels="; ".join(dc["labels"]), se_gate=se_gate)
    counts = sample_counts(rows)
    kdesc = sum(1 for r in regs if r["role"] == "DESCRIPTIVE")
    return dict(rows=rows, regs=regs, dec=dec, dc=dc, base=base, var=var, counts=counts, k_desc=kdesc, run_label=run_label)


def dec_text_row(d):
    nd = 6
    return [d["run_label"], str(d["n"]), f(d["alpha"], nd), f(d["n_alpha"], nd), f(d["beta"], nd), f(d["se_hc3"], nd), f(d["p_hc3"], nd),
            f(d["se_nw4"], nd), f(d["p_nw4"], nd), f(d["S"], nd), f(d["S_all"], nd), f(d["S_dropped"], nd), f(d["X"], nd), f(d["F"], nd), f(d["phi"], nd),
            f(d["phi_ci_lo"], nd), f(d["phi_ci_hi"], nd), f(d["se_placebo"], nd), str(d["n_placebo"]), f(d["halfwidth_phi"], nd), d["gate"],
            d["class_primary"], d["class_nw4"], d["gate_nw4"], d["class_restored"], d["gate_restored"], d["class_sameday"], d["gate_sameday"],
            d["verdict_of_record"], d["labels"]]


def event_rows(ctx):
    """Dropped yen weeks over the FULL sample (and the 2025-04-11 marker). fitted_term uses the primary's coefficient."""
    rows = ctx["rows"]
    beta = ctx["base"]["beta"]
    out = []
    for r in week_rows(rows, "FULL"):
        mark = r["week_end"] == MARKER_WEEK
        if not (r["drop_reason"] or mark):
            continue
        dated = r["_iv_days"]
        amt = sum(a for _, a in dated) if dated else None
        ft = beta * r["d_gap_jp2"]
        out.append([iso(r["week_end"]), "marker_2025_04_09" if (mark and not r["drop_reason"]) else r["drop_reason"], str(len(dated)),
                    f(amt, 0) if amt is not None else "", f(r["dln_jpy"], 6), f(r["d_gap_jp2"], 6), f(ft, 6), f(r["dln_jpy"] - ft, 6)])
    return out


# ------------------------------------------------------------------------------------------------------------------------
# reading the cache
# ------------------------------------------------------------------------------------------------------------------------
class Inputs:
    pass


def read_bytes(cache, name):
    p = os.path.join(cache, name)
    if not os.path.exists(p):
        raise DataError("%s is missing from the cache; run `fetch` first" % name)
    with open(p, "rb") as fh:
        return fh.read()


def load_inputs(cache):
    inp = Inputs()
    tsy = {}
    for y in range(FIRST_FETCH_YEAR, LAST_FETCH_YEAR + 1):
        part = parse_treasury(decode_text(read_bytes(cache, "tsy_%d.csv" % y)), year=y)
        if set(part) & set(tsy):
            raise DataError("Treasury years overlap")
        tsy.update(part)
    inp.tsy = tsy
    inp.jgb = parse_mof_yields(decode_text(read_bytes(cache, "mof_jgbcme_all.csv")))
    inp.yc = parse_ecb_yc(decode_text(read_bytes(cache, "ecb_yc.csv")))
    inp.bis = parse_bis(decode_text(read_bytes(cache, "bis_xru.csv")))
    inp.exr = parse_exr(decode_text(read_bytes(cache, "ecb_exr.csv")))
    inp.feio = parse_feio(read_bytes(cache, "mof_feio.csv"))
    inp.monthly = []
    for m in MONTHLY:
        s, e, a = parse_monthly(decode_text(read_bytes(cache, "mof_monthly_%s.html" % m)))
        inp.monthly.append(dict(name=m, start=s, end=e, amount=a, covered=e <= inp.feio["covered_through"]))
    inp.bbk = parse_bundesbank(decode_text(read_bytes(cache, "bbk_svensson.csv")))
    return inp


def iv_inputs(inp):
    """(dated days since the sample start, undated blocks that bind, run_label). A monthly window the quarterly CSV already covers is superseded by
    its dated days (spec 3.4); a window with a zero total binds nothing."""
    days = [(d, a) for d, a in inp.feio["days"] if d >= FIRST_WEEK - dt.timedelta(days=14)]
    blocks = [(m["start"], m["end"], m["amount"]) for m in inp.monthly if not m["covered"]]
    nz = sum(1 for b in blocks if b[2] != 0)
    label = "csv_through_%s_blocks_%d" % (inp.feio["covered_through"].isoformat(), nz)
    return sorted(days), blocks, label


# ------------------------------------------------------------------------------------------------------------------------
# checks (spec section 6)
# ------------------------------------------------------------------------------------------------------------------------
TSY_PINS = {dt.date(2023, 12, 29): (4.23, 3.88), dt.date(2024, 3, 21): (4.62, 4.27), dt.date(2024, 3, 22): (4.59, 4.22),
            dt.date(2026, 9, 17): (4.67, 4.94), dt.date(2026, 9, 18): (4.76, 5.01)}
MOF_PINS = {dt.date(2018, 1, 5): (-0.138, 0.057), dt.date(2023, 12, 29): (0.048, 0.647), dt.date(2024, 3, 22): (0.206, 0.762),
            dt.date(2026, 9, 18): (1.849, 2.981), dt.date(2026, 9, 24): (1.912, 3.073)}
BIS_PINS = (("JP", dt.date(2023, 12, 29), 141.475113), ("JP", dt.date(2026, 9, 18), 157.888307), ("XM", dt.date(2026, 9, 18), 0.8726))
ECB_PIN_DATE = dt.date(2026, 9, 18)
ECB_PINS = {"SR_2Y": 3.2152124072, "SR_10Y": 3.529753074, "PY_2Y": 3.2107329091, "PY_10Y": 3.5024674241}
EA_SA_PINS = {"ea2_sa": 3.237019, "ea10_sa": 3.533452}
ECB_PARAMS_PIN = {"BETA0": 1.608146049, "BETA1": 0.6677584932, "BETA2": 2.8889513654, "BETA3": 6.8503522231, "TAU1": 1.0445730922, "TAU2": 13.8644399107}
IV_ROW_PINS = {dt.date(2022, 9, 22): 28382, dt.date(2022, 10, 21): 56202, dt.date(2022, 10, 24): 7296, dt.date(2024, 4, 29): 59185,
               dt.date(2024, 5, 1): 38700, dt.date(2024, 7, 11): 31678, dt.date(2024, 7, 12): 23670, dt.date(2026, 4, 30): 62787,
               dt.date(2026, 5, 4): 7802, dt.date(2026, 5, 6): 46759}
IV_QUARTER_PINS = {dt.date(2022, 12, 31): (63498, 63499), dt.date(2024, 6, 30): (97885, 97885), dt.date(2024, 9, 30): (55348, 55348),
                   dt.date(2026, 6, 30): (117348, 117349)}
IV_MONTHLY_PINS = ((dt.date(2026, 6, 29), dt.date(2026, 7, 29), 0.0), (dt.date(2026, 7, 30), dt.date(2026, 8, 26), 153993.0),
                   (dt.date(2026, 8, 27), dt.date(2026, 9, 28), 0.0))
TRIPLES = {dt.date(2024, 3, 29): (dt.date(2024, 3, 28), dt.date(2024, 3, 27), dt.date(2024, 3, 28)),
           dt.date(2025, 1, 3): (dt.date(2025, 1, 3), dt.date(2025, 1, 2), dt.date(2024, 12, 30)),
           dt.date(2025, 12, 26): (dt.date(2025, 12, 24), dt.date(2025, 12, 23), dt.date(2025, 12, 24)),
           dt.date(2026, 1, 2): (dt.date(2026, 1, 2), dt.date(2025, 12, 31), dt.date(2025, 12, 30))}
PY_STRICT_FROM = dt.date(2024, 1, 1)     # measured 18 Oct 2026: PY reproduces from the parameters to 1e-10 from 2024, and misses by 1e-4 to 4e-3 before
C09_EXPECT = {"d_gap_jp2": -1.593, "d_slope_gap_jp": 0.044, "d_gap_jp10": -1.549, "d_gap_jp2_sd": -1.473}


def timing_corr(ust10, sr10, lo, hi):
    """C11: daily change of the Treasury 10y against the ECB AAA SR_10Y change. Each Treasury change on date u is paired with the ECB change dated u
    (same), dated the next ECB date after u (next: the euro market reacting to the US close) and dated the last ECB date before u (previous)."""
    ud = sorted(ust10)
    ed = sorted(sr10)
    uc = {d: ust10[d] - ust10[ud[i - 1]] for i, d in enumerate(ud) if i > 0}
    ec = {d: sr10[d] - sr10[ed[i - 1]] for i, d in enumerate(ed) if i > 0}
    pairs = {"same": [], "next": [], "prev": []}
    for u, c in uc.items():
        if not (lo <= u <= hi):
            continue
        if u in ec:
            pairs["same"].append((ec[u], c))
        j = bisect.bisect_right(ed, u)
        if j < len(ed) and ed[j] in ec:
            pairs["next"].append((ec[ed[j]], c))
        j = bisect.bisect_left(ed, u) - 1
        if j >= 1 and ed[j] in ec:
            pairs["prev"].append((ec[ed[j]], c))
    return {k: (corr([a for a, _ in v], [b for _, b in v]), len(v)) for k, v in pairs.items()}


def run_checks(inp, rows, ctx, selfcheck, incomplete, quar, affected):
    ck = []

    def add(cid, desc, exp, obs, status):
        ck.append([cid, desc, exp, obs, status])
    # C01 Treasury by header
    bad = []
    for d, (e2, e10) in TSY_PINS.items():
        o = inp.tsy.get(d)
        if o is None or abs(o[0] - e2) > 1e-9 or abs(o[1] - e10) > 1e-9:
            bad.append("%s 2 Yr/10 Yr expected %s/%s observed %s" % (d, e2, e10, "missing" if o is None else "%s/%s" % o))
    add("C01", "Treasury par yields read by header name (2023 and 2026 layouts differ)", "10 pinned values (5 dates x 2 Yr, 10 Yr)",
        "10 of 10 match" if not bad else "; ".join(bad) + " (source may have restated)", "PASS" if not bad else ("WARN" if all("missing" not in b for b in bad) else "FAIL"))
    # C02 MoF
    bad = []
    for d, (e2, e10) in MOF_PINS.items():
        o = inp.jgb.get(d)
        if o is None or o[0] is None or abs(o[0] - e2) > 1e-9 or abs(o[1] - e10) > 1e-9:
            bad.append("%s 2Y/10Y expected %s/%s observed %s" % (d, e2, e10, "missing" if o is None else "%s/%s" % o))
    add("C02", "MoF constant-maturity yields, 2Y and 10Y", "10 pinned values (5 dates x 2Y, 10Y)",
        "10 of 10 match" if not bad else "; ".join(bad) + " (source may have restated)", "PASS" if not bad else ("WARN" if all("missing" not in b for b in bad) else "FAIL"))
    # C03 BIS
    bad = []
    for area, d, e in BIS_PINS:
        o = inp.bis[area].get(d)
        if o is None or abs(o / e - 1) > 1e-5:
            bad.append("%s %s expected %s observed %s" % (area, d, e, o))
    add("C03", "BIS daily rates: yen per USD 2023-12-29 and 2026-09-18, euro per USD 2026-09-18", "3 pinned values (relative 1e-5)",
        "3 of 3 match" if not bad else "; ".join(bad) + " (source may have restated)", "PASS" if not bad else "WARN")
    # C04 BIS equals the ECB cross on every fx_date
    worst, n4, miss, off = 0.0, 0, [], []
    for r in rows:
        n4 += 1
        if r["_bis_missing"]:
            miss.append(iso(r["fx_date"]))
            continue
        for v, c in ((r["usdjpy"], r["_cross_jpy"]), (r["eur_per_usd"], r["_cross_eur"])):
            rel = abs(v / c - 1)
            worst = max(worst, rel)
            if rel > 1e-6:
                off.append(iso(r["fx_date"]))
    add("C04", "BIS daily rate equals the ECB reference cross (JPY/EUR over USD/EUR; 1 over USD/EUR) on every fx_date", "relative difference <= 1e-6",
        "%d fx_dates, largest relative difference %.2e%s%s" % (n4, worst, "; BIS missing on " + ", ".join(miss[:10]) if miss else "",
                                                               "; above 1e-6 on " + ", ".join(sorted(set(off))[:10]) if off else ""),
        "PASS" if not (miss or off) else "FAIL")
    # C05 ECB
    p = inp.yc[ECB_PIN_DATE]
    d_sr, d_py = ea_selfcheck(p)
    obs_sa = {"ea2_sa": ea_semiannual(2, params_of(p)), "ea10_sa": ea_semiannual(10, params_of(p))}
    bad = [k for k, v in ECB_PINS.items() if abs(p.get(k, 1e9) - v) > 1e-9]
    bad += ["param " + k for k, v in ECB_PARAMS_PIN.items() if abs(p.get(k, 1e9) - v) > 1e-9]
    pin_ok = d_sr <= 1e-6 and d_py <= 1e-4 and all(abs(obs_sa[k] - v) <= 1e-5 for k, v in EA_SA_PINS.items())
    sc_sr = max([v[0] for v in selfcheck.values()] or [0.0])
    late = [v[1] for d_, v in selfcheck.items() if v[1] is not None and d_ >= PY_STRICT_FROM]
    early = [v[1] for d_, v in selfcheck.items() if v[1] is not None and d_ < PY_STRICT_FROM]
    sc_py = max(late or [0.0])
    early_bad = sum(1 for v in early if v > 1e-4)
    used_ok = sc_sr <= 1e-6 and sc_py <= 1e-4
    qtxt = ""
    if quar or incomplete:
        qtxt = "; left out of the euro leg because the recomputation disagrees with the published SR or the set is incomplete: " + "; ".join(
            ["%s (parameters reproduce SR to %.2e only)" % (iso(d), e) for d, e in sorted(quar.items())] +
            ["%s (parameter set incomplete)" % iso(d) for d in incomplete]) + (
            "; weeks that moved to the previous ECB date: " + ", ".join(affected) if affected else "")
    qtxt += "; continuous-coupon par (PY) on the weekly dates before %s: max |diff| %.2e, %d of %d dates above 1e-4 (published PY and the continuous-coupon par recomputed from " \
            "the parameters agree to 1e-10 from 2024 and differ before; the zero yields SR agree on every date but one, and the semiannual par uses only the zero curve)" % (
                iso(PY_STRICT_FROM), max(early or [0.0]), early_bad, len(early)) if early else ""
    status = "PASS" if (pin_ok and used_ok and not bad and not quar and not incomplete and not early_bad) else (
        "WARN" if (pin_ok and used_ok and not bad and len(quar) + len(incomplete) <= 5) else "FAIL")
    add("C05", "ECB AAA Svensson parameters reproduce SR_2Y/SR_10Y (1e-6) and PY_2Y/PY_10Y (1e-4); semiannual par yields on 2026-09-18",
        "SR 1e-6, PY 1e-4, ea2_sa 3.237019, ea10_sa 3.533452 (1e-5); self-check on every ECB date and every weekly date. WARN accepted by the supervisor on 18 Oct: "
        "the euro gap uses the zero curve (SR), not the published par yields (PY)",
        "2026-09-18: max |SR diff| %.2e, max |PY diff| %.2e, ea2_sa %s, ea10_sa %s; %d ECB dates, %d usable; %d weekly dates used: max |SR diff| %.2e, "
        "max |PY diff| since %s %.2e%s%s" % (d_sr, d_py, f(obs_sa["ea2_sa"], 6), f(obs_sa["ea10_sa"], 6), len(inp.yc), len(inp.yc) - len(quar) - len(incomplete),
                                    len(selfcheck), sc_sr, iso(PY_STRICT_FROM), sc_py, qtxt, "; pin mismatch " + ", ".join(bad) if bad else ""), status)
    # C06 intervention CSV
    days = dict(inp.feio["days"])
    bad = ["%s expected %s observed %s" % (d, v, days.get(d)) for d, v in IV_ROW_PINS.items() if days.get(d) != v]
    q = {e: (s, ssum, n) for e, s, n, ssum in inp.feio["quarters"]}
    for e, (sum_exp, sub_exp) in IV_QUARTER_PINS.items():
        if e not in q:
            bad.append("quarter ending %s missing" % e)
            continue
        sub, ssum, n = q[e]
        if sub != sub_exp or ssum != sum_exp or abs(ssum - sub) > n:
            bad.append("quarter ending %s: days sum %s (expected %s), subtotal %s (expected %s), %d days" % (e, ssum, sum_exp, sub, sub_exp, n))
    for e, (sub, ssum, n) in q.items():
        if abs(ssum - sub) > max(n, 0):
            bad.append("quarter ending %s: days sum %s differs from subtotal %s by more than 1 per day" % (e, ssum, sub))
    quiet = [d for d in days if (dt.date(2018, 1, 1) <= d <= dt.date(2022, 8, 31)) or d.year in (2023, 2025)]
    if quiet:
        bad.append("day rows where none were expected: " + ", ".join(iso(d) for d in sorted(quiet)[:5]))
    add("C06", "MoF intervention CSV: ten day rows exact; each quarter's days sum to its subtotal within 1 per day; no day rows Jan 2018-Aug 2022, 2023, 2025",
        "10 day rows, 4 quarter sums, 0 stray rows", "%d day rows since 2018, %d subtotal rows; %s" % (sum(1 for d in days if d.year >= 2018), len(q),
                                                                                                     "all pins match" if not bad else "; ".join(bad)),
        "PASS" if not bad else "FAIL")
    # C07 monthly pages
    got = tuple((m["start"], m["end"], m["amount"]) for m in inp.monthly)
    add("C07", "MoF monthly pages: totals for the three 2026 windows", "0; 15,399.3 billion yen (153,993 x 100m, undated); 0",
        "; ".join("%s to %s: %s" % (iso(s), iso(e), f(a, 1)) for s, e, a in got), "PASS" if got == IV_MONTHLY_PINS else "FAIL")
    # C08 sample P
    cn = ctx["counts"]
    P = cn["P"]
    exp_p = EXPECTED_COUNTS["P"]
    ok8 = (P["weeks"], P["iv"], P["stale"], P["kept"]) == exp_p and tuple(P["iv_weeks"]) == EXPECTED_P_IV and tuple(P["stale_weeks"]) == EXPECTED_P_STALE
    add("C08", "Sample P: weekly changes, intervention weeks, stale weeks, kept", "130; 10 (%s); 2 (%s); 118" % (", ".join(EXPECTED_P_IV), ", ".join(EXPECTED_P_STALE)),
        "%d; %d (%s); %d (%s); %d" % (P["weeks"], P["iv"], ", ".join(P["iv_weeks"]), P["stale"], ", ".join(P["stale_weeks"]), P["kept"]), "PASS" if ok8 else "FAIL")
    parts = []
    allok = True
    for nm in ("FULL", "W1", "W2", "W3"):
        c, e = cn[nm], EXPECTED_COUNTS[nm]
        parts.append("%s %d/%d iv/%d stale/%d kept" % (nm, c["weeks"], c["iv"], c["stale"], c["kept"]))
        allok &= (c["weeks"], c["iv"], c["stale"], c["kept"]) == e
    add("C08b", "Other samples: weeks / intervention weeks / stale weeks / kept (reviewer's counts: FULL 455/13/6/436, W1 209/0/4/205, W2 104/3/0/101, W3 142/10/2/130)",
        "reviewer's counts", "; ".join(parts), "PASS" if allok else "WARN")
    # C09 telescoping identity (INFO)
    Pw = week_rows(rows, "P")
    sums = {k: sum(r[k] for r in Pw) for k in C09_EXPECT}
    add("C09", "Telescoping identity over all 130 P weeks (INFO: it cannot fail): sums of the weekly gap changes",
        "d_gap_jp2 -1.593; d_slope_gap_jp +0.044; d_gap_jp10 -1.549; d_gap_jp2_sd -1.473",
        "; ".join("%s %s" % (k, f(v, 9)) for k, v in sums.items()), "INFO")
    # C11 timing diagnostic
    ust10 = {d: v[1] for d, v in inp.tsy.items()}
    sr10 = {d: p_["SR_10Y"] for d, p_ in inp.yc.items() if "SR_10Y" in p_}
    full = timing_corr(ust10, sr10, dt.date(2017, 12, 1), dt.date(2026, 9, 30))
    rec = timing_corr(ust10, sr10, dt.date(2023, 12, 1), dt.date(2026, 9, 30))
    ordered = full["same"][0] > full["next"][0] > full["prev"][0]
    add("C11", "Timing diagnostic: daily change of the Treasury 10y against the ECB AAA SR_10Y change dated the same day / the next ECB date / the previous ECB date",
        "same > next > previous (Dec 2023-Sep 2026 reviewer: 0.549, 0.206, 0.029, n=692)",
        "2018-2026: %s (n=%d); Dec 2023-Sep 2026: %s (n=%d)" % (
            " / ".join(f(full[k][0], 3) for k in ("same", "next", "prev")), full["same"][1],
            " / ".join(f(rec[k][0], 3) for k in ("same", "next", "prev")), rec["same"][1]), "INFO" if ordered else "WARN")
    # C12 AAA set against the Bund (statistic and dates only)
    ds, bs, wk = [], [], []
    for i, r in enumerate(rows):
        s_ = inp.yc[r["ea_date"]].get("SR_10Y")
        b_ = inp.bbk.get(r["ea_date"])
        if i >= 1 and s_ is not None and b_ is not None:
            pr_ = rows[i - 1]
            s0, b0 = inp.yc[pr_["ea_date"]].get("SR_10Y"), inp.bbk.get(pr_["ea_date"])
            if s0 is not None and b0 is not None:
                ds.append(s_ - s0)
                bs.append(b_ - b0)
                if abs((s_ - s0) - (b_ - b0)) > 0.15:
                    wk.append(iso(r["week_end"]))
    add("C12", "AAA set: weekly change of the ECB SR_10Y against the Bundesbank 10y (statistic and dates only; no Bundesbank value is stored); weeks where the two differ by more than 15bp",
        "INFO", "weekly correlation %s over %d weeks; %d weeks above 15bp: %s" % (f(corr(ds, bs), 3), len(ds), len(wk), ", ".join(wk) if wk else "none"), "INFO")
    # C14 alignment triples
    byw = {r["week_end"]: r for r in rows}
    bad = []
    for we, (fx, us, jp) in TRIPLES.items():
        r = byw.get(we)
        got = (r["fx_date"], r["us_date"], r["jp_date"]) if r else None
        if got != (fx, us, jp):
            bad.append("%s expected %s observed %s" % (we, (fx, us, jp), got))
    add("C14", "Alignment triples (fx_date / us_date / jp_date) for the weeks ending 2024-03-29, 2025-01-03, 2025-12-26, 2026-01-02",
        "4 pinned triples", "4 of 4 match" if not bad else "; ".join(bad), "PASS" if not bad else "FAIL")
    return ck


def pins_rows(inp, rows):
    out = []
    for d in sorted(TSY_PINS):
        out.append(["U.S. Treasury", "2 Yr par yield", iso(d), f(inp.tsy[d][0], 2), "percent"])
    for d in sorted(MOF_PINS):
        out.append(["MoF Japan", "2Y constant-maturity yield", iso(d), f(inp.jgb[d][0], 3), "percent"])
    for area, d, _ in BIS_PINS:
        out.append(["BIS", "D.JP.JPY.A yen per USD" if area == "JP" else "D.XM.EUR.A euro per USD", iso(d), f(inp.bis[area][d], 6),
                    "yen per USD" if area == "JP" else "euro per USD"])
    p = inp.yc[ECB_PIN_DATE]
    for k in ("SR_2Y", "SR_10Y", "PY_2Y", "PY_10Y"):
        out.append(["ECB", k, iso(ECB_PIN_DATE), f(p[k], 6), "percent"])
    pr = params_of(p)
    out.append(["project_computation", "ea2_sa (semiannual par from ECB parameters)", iso(ECB_PIN_DATE), f(ea_semiannual(2, pr), 6), "percent"])
    out.append(["project_computation", "ea10_sa (semiannual par from ECB parameters)", iso(ECB_PIN_DATE), f(ea_semiannual(10, pr), 6), "percent"])
    return out


def ivday_rows(inp):
    out = []
    for d, a in sorted(inp.feio["days"]):
        if d >= dt.date(2018, 1, 1):
            out.append(["day", iso(d), iso(d), str(a), "foreign_exchange_intervention_operations.csv", "quarterly CSV; latest quarter in the file ends %s" %
                        iso(inp.feio["covered_through"])])
    for m in inp.monthly:
        note = ("zero total" if m["amount"] == 0 else "monthly page, no day split") + ("; superseded by the quarterly CSV" if m["covered"] else "")
        out.append(["block", iso(m["start"]), iso(m["end"]), f(m["amount"], 1), "monthly/%s.html" % m["name"], note])
    return out


def panel_rows_text(rows):
    out = []
    for r in rows:
        def g(k, nd):
            return f(r.get(k), nd)
        out.append([iso(r["week_end"]), iso(r["fx_date"]), g("usdjpy", 6), g("eur_per_usd", 6), iso(r["us_date"]), g("us2", 3), g("us10", 3),
                    iso(r["us_date_sd"]), g("us2_sd", 3), g("us10_sd", 3), iso(r["jp_date"]), g("jp2", 3), g("jp10", 3), iso(r["ea_date"]),
                    g("ea2_sa", 6), g("ea10_sa", 6), g("gap_jp2", 6), g("gap_jp10", 6), g("slope_gap_jp", 6), g("gap_ea2", 6), g("gap_ea10", 6),
                    g("slope_gap_ea", 6), g("dln_jpy", 10), g("dln_eur", 10), g("d_gap_jp2", 6), g("d_gap_jp10", 6), g("d_slope_gap_jp", 6),
                    g("d_gap_ea2", 6), g("d_gap_ea10", 6), g("d_slope_gap_ea", 6), g("d_gap_jp2_sd", 6), g("d_slope_gap_jp_sd", 6), r["drop_reason"]])
    return out


# ------------------------------------------------------------------------------------------------------------------------
# README.md and SOURCES.md (generated, so every number in them is the run's)
# ------------------------------------------------------------------------------------------------------------------------
def pf(p):
    return "<0.0001" if p < 1e-4 else f(p, 4)


def d_long(d):
    return "%d %s %d" % (d.day, d.strftime("%B"), d.year)


def example_week(ctx):
    """The worked example: the first kept week of sample P."""
    b = ctx["base"]
    r = b["kept"][0]
    i = ctx["rows"].index(r)
    prev = ctx["rows"][i - 1]
    fitted = b["beta"] * r["d_gap_jp2"]
    return dict(week=r["week_end"], fx_prev=prev["fx_date"], fx=r["fx_date"], dln=r["dln_jpy"], dx=r["d_gap_jp2"], fitted=fitted, beta=b["beta"])


def plain_words(ctx):
    """The verdict in plain words, and why the expected outcome did or did not happen. Built from the run's own numbers."""
    d = ctx["dec"]
    X, F, S, na = d["X"], d["F"], d["S"], d["n_alpha"]
    out = []
    if d["verdict_of_record"].startswith("INCONCLUSIVE"):
        out.append("The 'what to expect' paragraph above anticipated INCONCLUSIVE (underpowered), and the verdict of record is %s." % d["verdict_of_record"])
    else:
        out.append("The 'what to expect' paragraph above anticipated INCONCLUSIVE (underpowered); that did not happen, because the gate was passed: the half-width of "
                   "the phi interval is %s against the limit 0.25. The gate needs |S| above about 0.08 to 0.11 (the specification's ex-ante arithmetic), and S = %s "
                   "is above it." % (f(d["halfwidth_phi"], 3), f(S, 3)))
    out.append("In plain words: over the %d kept weeks the 2-year gap %s by %s percentage points, which on the weekly slope goes with a %s yen (%s%% in log terms), "
               "while the yen %s by %s%% (log terms). The yen's move over those weeks sits in the constant term (n x alpha = %s), not in the gap term. "
               "This describes co-movement; it does not show what moved the yen." % (
                   d["n"], "narrowed" if X < 0 else "widened", f(abs(X), 1), "stronger" if F < 0 else "weaker", f(100 * F, 1),
                   "weakened" if S > 0 else "strengthened", f(100 * abs(S), 1), f(na, 3)))
    return " ".join(out)


def render_readme(ctx, log_rows):
    d, b, cn = ctx["dec"], ctx["base"], ctx["counts"]
    P = cn["P"]
    ex = example_week(ctx)
    full = next(r for r in ctx["regs"] if r["pair"] == "yen" and r["sample"] == "FULL" and r["spec"] == "gap2" and r["variant"] == "base")
    slope = next(r for r in ctx["regs"] if r["role"] == "SEPARATE")
    diffs = []
    for nm, _, _ in SAMPLES:
        c, e = cn[nm], EXPECTED_COUNTS[nm]
        if (c["weeks"], c["iv"], c["stale"], c["kept"]) != e:
            diffs.append("%s: weeks %d (reviewer %d), intervention weeks %d (%d), stale weeks %d (%d), kept %d (%d)" %
                         (nm, c["weeks"], e[0], c["iv"], e[1], c["stale"], e[2], c["kept"], e[3]))
    pubs = "; ".join("%s retrieved %s" % (n, ", ".join(retrieval_dates(log_rows, {h})) or "(no logged retrieval)") for n, h in PUBLISHERS)
    L = []
    w = L.append
    w("# The yen and the euro against interest-rate gaps: one weekly test")
    w("")
    w("*Generated by `python3 bin/fx_rate_gap.py build`; do not edit by hand. Specification: `_research/2026-10-18-FX-Rate-Gap-Weekly-Spec.md`. "
      "Data: %s.*" % pubs)
    w("")
    w("## In five sentences")
    w("")
    w("1. We asked whether, after the Bank of Japan changed its policy framework on 19 March 2024, the yen's weekly moves against the US dollar went "
      "together with weekly changes in the gap between the US and Japanese 2-year government bond yields, and how much of the yen's total move over "
      "those weeks that gap-change term accounts for.")
    w("2. For each week we measured the change in the natural log of the yen price of a dollar and the change in the 2-year gap (US minus Japan, in "
      "percentage points), and drew the best straight line, with a constant, through those weekly pairs.")
    w("3. The weeks run from the one ending %s to the one ending %s: %d weekly changes, of which %d remain after dropping %d weeks that overlap a Japanese "
      "intervention and %d weeks in which a yield quote was stale." % (d_long(P_START), d_long(LAST_WEEK), P["weeks"], d["n"], P["iv"], P["stale"]))
    w("4. The one test is whether the slope of that line differs from zero (two-sided, 5%, HC3 standard errors), and a decision rule fixed before any "
      "exchange rate was read then asks what share of the yen's cumulative move over the kept weeks the fitted gap-change term accounts for.")
    w("5. It cannot show that rates, flows, positions or intervention made the yen move, it says nothing about the intervention weeks themselves, and "
      "a short sample can miss an effect that is there.")
    w("")
    w("## A worked example")
    w("")
    w("Take the first kept week, the one ending %s (the exchange rate is the BIS daily rate on %s, equal to the ECB reference cross; the change runs from "
      "the rate on %s). The log of yen per "
      "dollar changed by %s (about %s%%) and the 2-year gap changed by %s percentage points. The fitted slope for the whole sample is beta = %s, so the "
      "gap-change term for that week is beta x gap change = %s x %s = %s. The week adds %s to S, the sum of the yen's log changes over the kept weeks, "
      "and %s to F, the sum of the fitted gap-change terms. Over all %d kept weeks S = %s and F = %s, so phi = F / S is %s." %
      (d_long(ex["week"]), iso(ex["fx"]), iso(ex["fx_prev"]), f(ex["dln"], 6), f(100 * ex["dln"], 2), f(ex["dx"], 3), f(ex["beta"], 6), f(ex["beta"], 6),
       f(ex["dx"], 3), f(ex["fitted"], 6), f(ex["dln"], 6), f(ex["fitted"], 6), d["n"], f(d["S"], 4), f(d["F"], 4),
       f(d["phi"], 4) if d["phi"] is not None else "not defined (|S| <= 0.01)"))
    w("")
    w("## Four definitions")
    w("")
    w("- **Log change.** The natural log of this week's price divided by last week's; 0.01 is about 1%.")
    w("- **Gap.** The US yield minus the foreign yield, in percentage points; a wider gap and a stronger dollar both push the series up, so the slope is "
      "expected to be positive.")
    w("- **HC3.** Standard errors that let each week have its own variance and damp the weight of influential weeks.")
    w("- **Placebo.** The same regression with the gap series slid out of line in time (by 13 to n-13 weeks, wrapping round), to see how large the slope "
      "looks by chance.")
    w("")
    w("This build is one test plus description: the regression of section 3.6 of the specification on the 2-year gap, in sample P, is the only "
      "confirmatory test. Every other row (the 10-year gap, the joint regression, the other samples, every euro row) is description. "
      "`regressions.csv` prints k = %d descriptive rows in its second line; a reader who treats them as tests must use 0.05 / k." % ctx["k_desc"])
    w("")
    w("## Commands")
    w("")
    w("```")
    w("python3 bin/fx_rate_gap.py selftest   # synthetic data, no network: guards G1-G21 of the spec plus X1-X6 added by the builder; every mutant must be caught")
    w("python3 bin/fx_rate_gap.py fetch      # the only network command: 19 requests, 2 s apart; a refusal writes data/vintages/fx_rate_gap/STOP")
    w("python3 bin/fx_rate_gap.py build      # offline: writes the files in this folder; a second run is byte-identical")
    w("```")
    w("")
    w("The raw downloads and the weekly panel stay in `data/vintages/fx_rate_gap/`, which `.gitignore` keeps out of the repository, because the panel "
      "would let a reader rebuild yield levels. This folder holds only statistics, the decision, a few pinned values, the intervention list, the checks "
      "and the fetch log.")
    w("")
    w("## When each yield is observed (the time-zone rule)")
    w("")
    w("A week runs Monday to Friday; its exchange rate is the BIS daily rate on the last day of the week with an ECB reference rate (normally the Friday). "
      "No yield is observed after that rate: Japan's is the MoF yield on that day or the last earlier one (15:00 Tokyo, about 06:00 GMT), and the US "
      "and euro-area yields are the last observations strictly before it (normally Thursday's close). The same-Friday US yield, observed about seven "
      "hours after the exchange rate, is kept only as a fragility check (variant c). What remains: the exchange-rate change runs from fix to fix, while "
      "the US and euro legs run from Thursday close to Thursday close, so news in Friday's Asian and London hours enters this week's exchange rate but "
      "next week's yield change.")
    w("")
    w("## The denominator of phi and two identities")
    w("")
    w("S is the sum of the yen's log changes over the **kept** weeks only. The sum over all %d weeks of P, S_all = %s, is never the denominator; "
      "S_all = S + S_dropped (%s = %s + %s) holds by construction. Because the residuals of a regression with a constant sum to zero, S = n x alpha + F "
      "(%s = %s + %s): the intercept absorbs any level or carry channel, so a share phi near zero does not mean the gap's level is irrelevant." %
      (P["weeks"], f(d["S_all"], 6), f(d["S_all"], 6), f(d["S"], 6), f(d["S_dropped"], 6), f(d["S"], 6), f(d["n_alpha"], 6), f(d["F"], 6)))
    w("")
    w("## What to expect (written before the run)")
    w("")
    w("X, the sum of the 2-year gap changes over the kept weeks, is negative over P (the gap narrowed). With a positive slope, phi >= 0.50 therefore "
      "needs S < 0: the yen must have strengthened, in dollar terms, over the kept weeks. The power arithmetic makes INCONCLUSIVE (underpowered) the "
      "expected outcome; in that case the build's value is the descriptive table, not a verdict.")
    w("")
    w("## Why the 2-year gap (a forking path, disclosed)")
    w("")
    w("The choice of the 2-year gap rather than the slope gap was made after the specification's author had seen how the candidate regressors moved over "
      "P: the four end-point yields and the totals of the three candidate gaps (+0.044, -1.593 and -1.549 percentage points over all 130 weeks of P). No exchange rate "
      "was used. A primary regressor chosen with knowledge of the regressors' own path is one fork of the garden, even when the outcome is unseen. The "
      "slope-gap regression stays in every output as the SEPARATE row, and the full-sample row is printed beside the primary every time.")
    w("")
    w("## What this can and cannot say")
    w("")
    w("It can say whether, in non-intervention weeks from 29 March 2024 to 18 September 2026, the yen moved with the 2-year gap, at what rate, and "
      "whether the weekly 2-year-gap-change term accounts for at least half, or for less than a quarter, of the yen's cumulative log change over those "
      "weeks, or points the other way. That is association: the coefficient is MEASURED (observed on the stated data, and can be wrong), and the share, given the coefficient, is an IDENTITY (true by construction, so it carries no information beyond its inputs). It cannot "
      "say that rates, flows, positions or intervention moved anything; anything about the intervention weeks, which are dropped; or anything about "
      "real yields, policy rates or forecasting. It cannot say that rates do not matter if the power gate fails. The post-March-2024 sample was dated "
      "after the 2024-26 path had been tabulated, so the primary is not a blind test.")
    w("")
    w("A move in an intervention week is not attributed to the intervention by `event_weeks.csv`; its `fitted_term` column uses the sample-P coefficient "
      "for every listed week.")
    w("")
    w("## What the registered run printed")
    w("")
    w("Run label `%s`. Verdict of record: **%s**. n = %d; beta = %s (HC3 SE %s, p %s; Newey-West SE %s, p %s); S = %s, X = %s pp, F = %s; phi = %s%s; "
      "placebo SD %s over %d shifts; half-width of the phi interval %s (gate %s)." %
      (d["run_label"], d["verdict_of_record"], d["n"], f(d["beta"], 6), f(d["se_hc3"], 6), pf(d["p_hc3"]), f(d["se_nw4"], 6), pf(d["p_nw4"]),
       f(d["S"], 6), f(d["X"], 6), f(d["F"], 6), f(d["phi"], 4) if d["phi"] is not None else "not defined",
       " (interval %s to %s)" % (f(d["phi_ci_lo"], 4), f(d["phi_ci_hi"], 4)) if d["phi"] is not None else "", f(d["se_placebo"], 6), d["n_placebo"],
       f(d["halfwidth_phi"], 4) if d["halfwidth_phi"] is not None else "not defined", d["gate"]))
    w("")
    w(plain_words(ctx))
    w("")
    w("The same regression on the full sample (%d weeks): beta = %s (HC3 SE %s). The separate slope-gap row: beta = %s (p %s), phi = %s; the sum of "
      "the slope-gap changes over the %d kept weeks is %s pp (+0.044 pp is the sum over all 130 weeks of P), so phi_s is near zero by construction." %
      (full["n"], f(full["beta"], 6), f(full["se_hc3"], 6), f(slope["beta"], 6), pf(slope["p_hc3"]), f(slope["phi"], 4) if slope["phi"] is not None else "not defined",
       slope["n"], f(slope["sum_dx"], 3)))
    w("")
    if diffs:
        w("Counts that differ from the reviewer's (specification 3.5): " + "; ".join(diffs) + ".")
    else:
        w("Every count matches the reviewer's (specification 3.5): FULL 455 weeks (436 kept), W1 209 (205), W2 104 (101), W3 142 (130), P 130 (118).")
    w("")
    notes = ctx.get("ecb_notes")
    if notes:
        w("## Data notes (what the checks found in the sources)")
        w("")
        w("- **ECB dates left out of the euro leg.** %s Both lie outside the yen regressions, which use no ECB yield; the euro rows, which are description, use the "
          "previous ECB date for the week ending %s." % (
              "; ".join(["%s: the Svensson parameters reproduce the published 2- and 10-year zero yields only to %.1e (tolerance 1e-6)" % (iso(d), e)
                         for d, e in sorted(notes["quar"].items())] +
                        ["%s: the parameter set is incomplete in the file" % iso(d) for d in notes["incomplete"]]) + ".",
              ", ".join(notes["affected"]) or "no week"))
        if notes["py_early_total"]:
            w("- **The ECB's published continuous-coupon par yields before 2024.** Recomputed from the parameters they agree to 1e-10 from 1 January 2024 and "
              "differ before it (largest gap %.1e; %d of %d weekly dates above the spec's 1e-4). The zero yields agree on every date but the one named above, and "
              "the semiannual par yield used in the euro gap needs only the zero curve, so the euro gap does not depend on the published par yields." % (
                  notes["py_early_max"], notes["py_early_bad"], notes["py_early_total"]))
        w("")
    w("## Appendix: the decision rule (specification section 4, summarised)")
    w("")
    w("Written on 18 October 2026, before any exchange-rate series or coefficient was computed. Quantities, in sample P with the kept weeks: S is the sum of "
      "dln(yen per dollar); X is the sum of the 2-year gap changes; F = beta x X; phi = F / S (left blank if |S| <= 0.01). The phi interval is "
      "(beta -/+ 1.959964 SE) x X / S with the endpoints sorted. The standard errors: the power gate uses max(placebo SD, SE_HC3); the primary's "
      "intervals and verdict use SE_HC3; variant (a) uses SE_NW4 for its interval and max(placebo SD, SE_NW4) for its printed gate; variants (b) and (c) "
      "use their own SE_HC3 and their own placebo.")
    w("")
    w("Power gate (computed before beta is read): the placebo re-estimates beta on every circular shift of the kept gap series by 13 ... n-13 weeks "
      "(n - 25 shifts). If 1.959964 x SE_gate x |X| / |S| exceeds 0.25 the design is underpowered and the verdict is INCONCLUSIVE, whatever beta is.")
    w("")
    w("Classes, with no gate inside them: UNCLASSIFIED if |S| <= 0.01 or |X| < 0.5 pp; AT LEAST HALF if beta > 0, p < 0.05, phi >= 0.50 and the lower end "
      "of the phi interval > 0.25; POINTS THE OTHER WAY if the upper end < 0; LESS THAN A QUARTER if 0 <= the upper end < 0.25; otherwise UNCLASSIFIED. "
      "The verdict of record is INCONCLUSIVE if |S| <= 0.01, |X| < 0.5 pp or the primary's gate fails; otherwise each of three variants is classified "
      "by its own phi and interval without a gate, (a) Newey-West lag 4, (b) the intervention weeks restored (stale weeks stay out), (c) the "
      "same-calendar-Friday US leg, and the verdict is INCONCLUSIVE (fragile) if any variant's class differs from the primary's; otherwise it is the "
      "primary's class. The 0.25 and 0.50 marks, the 0.5 pp floor, lag 4 and the 13-week placebo floor are pre-commitments, not estimates. "
      "The euro rows have no verdict.")
    text = "\n".join(L) + "\n"
    if M("causal_text"):
        text += "\nThe yen moved because of intervention, and flows drove it.\n"
    guard_text("README.md", text)
    return text


def render_sources(log_rows):
    L = []
    w = L.append
    w("# Sources and column provenance")
    w("")
    w("Generated by `python3 bin/fx_rate_gap.py build`. Every web fact was fetched by `fetch` with the project's neutral identification string; "
      "`fetch_log.csv` lists each request with its time, status, size and sha256. Retrieval dates below are read from that log.")
    w("")
    rows = [
        ("U.S. Department of the Treasury (home.treasury.gov)", TSY_HOST,
         "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{Y}/all?type=daily_treasury_yield_curve"
         "&field_tdr_date_value={Y}&page&_format=csv, Y = 2017 to 2026 (10 files)",
         "A US government work; the catalogue's CC0 notice was not read.", "Source: U.S. Department of the Treasury, Daily Treasury Par Yield Curve Rates."),
        ("Ministry of Finance, Japan (www.mof.go.jp)", MOF_HOST,
         "https://www.mof.go.jp" + JGB_PATH + "; https://www.mof.go.jp" + FEIO_PATH + "; the monthly pages under "
         "https://www.mof.go.jp/english/policy/international_policy/reference/feio/monthly/ (20260731e, 20260828e, 20260930e)",
         "Public Data License 1.0, with numerical data outside copyright (as relayed in the specification). The Japan Securities Dealers Association's rights "
         "behind the yields were not read.", "Source: Ministry of Finance Japan, Interest Rate (JGB constant maturity) and Foreign Exchange Intervention Operations."),
        ("European Central Bank (data-api.ecb.europa.eu)", ECB_HOST,
         "https://data-api.ecb.europa.eu" + YC_PATH + "; https://data-api.ecb.europa.eu" + EXR_PATH,
         "Reuse with the source named, unmodified (as relayed in the specification). The semiannual par yield is a project computation from the ECB's "
         "parameters, not an ECB statistic. Data note: the euro gap uses the zero curve built from those parameters (it reproduces the published zero yields, "
         "SR, to 1e-10 on every date but one), not the ECB's published par yields (PY), which do not follow the parameters before 2024; `checks.csv` C05 "
         "prints WARN for this and the supervisor accepted it on that ground.", "Source: ECB statistics, euro area yield curves (AAA, Svensson) and euro foreign exchange reference rates."),
        ("Bank for International Settlements (stats.bis.org)", BIS_HOST, "https://stats.bis.org" + BIS_PATH,
         "Reuse with citation (data.bis.org/help/legal, as relayed in the specification).", "Source: Bank for International Settlements, daily exchange rates "
         "(WS_XRU), series D.JP.JPY.A and D.XM.EUR.A."),
        ("Deutsche Bundesbank (api.statistiken.bundesbank.de)", BBK_HOST, "https://api.statistiken.bundesbank.de" + BBK_PATH,
         "Terms page not read in this pass. Used only for one correlation and a list of dates in `checks.csv`; no Bundesbank value is committed.",
         "Source: Deutsche Bundesbank, time series BBSIS.D.I.ZST.ZI.EUR.S1311.B.A604.R02XX/R10XX."),
    ]
    for name, host, url, lic, cite in rows:
        ds = retrieval_dates(log_rows, {host})
        w("## " + name)
        w("")
        w("- URL: " + url)
        w("- Retrieved: " + (", ".join(ds) if ds else "(no logged retrieval)"))
        w("- Licence: " + lic)
        w("- Citation: " + cite)
        w("")
    w("## Which weekly-panel columns are source values and which are computed")
    w("")
    w("The weekly panel itself (`data/vintages/fx_rate_gap/weekly_panel.csv`) is not committed.")
    w("")
    w("| Column | Kind | Origin |")
    w("|---|---|---|")
    w("| `usdjpy`, `eur_per_usd` | source value | BIS WS_XRU daily rates on `fx_date` (checked against the ECB reference cross) |")
    w("| `us2`, `us10`, `us2_sd`, `us10_sd` | source value | Treasury par yields, 2 Yr and 10 Yr |")
    w("| `jp2`, `jp10` | source value | MoF constant-maturity yields, 2Y and 10Y |")
    w("| `ea2_sa`, `ea10_sa` | computed | semiannual par yield from the ECB AAA Svensson parameters of `ea_date` |")
    w("| `week_end`, `fx_date`, `us_date`, `us_date_sd`, `jp_date`, `ea_date` | computed | the alignment rule of specification 3.1 |")
    w("| `gap_*`, `slope_gap_*` | computed | US minus foreign, in percentage points; slope gap = 10-year gap minus 2-year gap |")
    w("| `dln_jpy`, `dln_eur`, `d_*` | computed | weekly log change and weekly change in the level |")
    w("| `drop_reason` | computed | intervention weeks from the MoF files; stale legs from the 4-10 day span rule |")
    text = "\n".join(L) + "\n"
    guard_text("SOURCES.md", text)
    return text


# ------------------------------------------------------------------------------------------------------------------------
# the build
# ------------------------------------------------------------------------------------------------------------------------
def read_decision_rows(out_dir):
    hdr, rows = read_csv_rows(os.path.join(out_dir, "decision.csv"))
    if hdr and hdr != DEC_COLS:
        raise DataError("decision.csv has an unexpected header")
    return rows


def render_all(ctx, checks, existing_dec, log_rows):
    """name -> text for every output (the weekly panel included)."""
    S = lambda hosts, what: source_line(log_rows, hosts, what)
    out = {}
    out["regressions.csv"] = render_csv("regressions.csv", [reg_text_row(r) for r in ctx["regs"]],
                                        S(HOST_ALLOW, "regression statistics computed by bin/fx_rate_gap.py from daily data of the above"),
                                        extra_comments=["descriptive_rows_k=%d (a reader who treats the DESCRIPTIVE rows as tests must use 0.05/k)" % ctx["k_desc"]])
    dec_rows = ([] if M("decision_overwrite") else [r for r in existing_dec if r[0] != ctx["dec"]["run_label"]]) + [dec_text_row(ctx["dec"])]
    out["decision.csv"] = render_csv("decision.csv", dec_rows, S(HOST_ALLOW, "the pre-registered decision of specification section 4, computed by bin/fx_rate_gap.py"))
    out["event_weeks.csv"] = render_csv("event_weeks.csv", event_rows(ctx), S({TSY_HOST, MOF_HOST, ECB_HOST, BIS_HOST},
                                        "dropped yen weeks, computed by bin/fx_rate_gap.py. A move in an intervention week is not attributed to the intervention by this table"))
    out["intervention_days.csv"] = render_csv("intervention_days.csv", ctx["ivday_rows"], S({MOF_HOST}, "Japan MoF foreign exchange intervention operations; amounts in 100 million yen"))
    out["pins.csv"] = render_csv("pins.csv", ctx["pins"], S({TSY_HOST, MOF_HOST, ECB_HOST, BIS_HOST}, "at most five pinned values per source; project_computation rows are computed by bin/fx_rate_gap.py"))
    out["checks.csv"] = render_csv("checks.csv", checks, S(HOST_ALLOW, "pinned checks of specification section 6"))
    out["README.md"] = render_readme(ctx, log_rows)
    out["SOURCES.md"] = render_sources(log_rows)
    out["weekly_panel.csv"] = render_csv("weekly_panel.csv", panel_rows_text(ctx["rows"]), S(HOST_ALLOW, "weekly panel computed by bin/fx_rate_gap.py (cache only, never committed)"))
    return out


def write_outputs(texts, cache, target):
    """The weekly panel goes to the cache and ONLY there (R4: it would let a reader rebuild yield levels); everything else goes to `target`."""
    for name, text in texts.items():
        if name == "weekly_panel.csv" and not M("panel_to_output"):
            write_text(os.path.join(cache, name), text)
        else:
            write_text(os.path.join(target, name), text)
    if os.path.exists(os.path.join(target, "weekly_panel.csv")):
        raise DataError("weekly_panel.csv found in the output folder %s: the panel belongs in the gitignored cache only" % tilde(target))


def build(cache, out_dir, say=print):
    cache = check_cache(cache, out_dir=out_dir)
    t0 = time.time()
    inp = load_inputs(cache)
    selfcheck = {}
    clean, incomplete, quar = usable_yc(inp.yc)
    rows = make_weeks(inp.tsy, inp.jgb, clean, inp.bis, inp.exr, selfcheck=selfcheck)
    full_dates = sorted(d for d, p in inp.yc.items() if all(k in p for k in PARAM_KEYS))
    affected = [iso(r["week_end"]) for r in rows
                if last_on_or_before(full_dates, r["fx_date"], strict=True) != r["ea_date"]]
    days, blocks, label = iv_inputs(inp)
    finish_panel(rows, days, blocks)
    ctx = analyze(rows, run_label=label)
    early_py = [v[1] for d_, v in selfcheck.items() if v[1] is not None and d_ < PY_STRICT_FROM]
    ctx["ecb_notes"] = dict(quar=quar, incomplete=incomplete, affected=affected, py_early_max=max(early_py or [0.0]),
                            py_early_bad=sum(1 for v in early_py if v > 1e-4), py_early_total=len(early_py))
    ctx["pins"] = pins_rows(inp, rows)
    ctx["ivday_rows"] = ivday_rows(inp)
    checks = run_checks(inp, rows, ctx, selfcheck, incomplete, quar, affected)
    base_out = out_dir
    _, log_rows = read_csv_rows(os.path.join(base_out, "fetch_log.csv"))
    existing = read_decision_rows(base_out)
    checks.sort(key=lambda c: c[0])
    t1 = render_all(ctx, checks, existing, log_rows)
    t2 = render_all(ctx, checks, existing, log_rows)
    same = all(t1[k] == t2[k] for k in t1)
    checks.append(["C13", "Fixed output: the outputs rendered twice in this run have identical sha256 (the on-disk comparison is the second `build`)",
                   "identical", "identical" if same else "DIFFERENT: " + ", ".join(k for k in t1 if t1[k] != t2[k]), "PASS" if same else "FAIL"])
    checks.sort(key=lambda c: c[0])
    texts = render_all(ctx, checks, existing, log_rows)
    failed = [c for c in checks if c[4] == "FAIL"]
    target = os.path.join(out_dir, "_FAILED") if failed else out_dir
    write_outputs(texts, cache, target)
    ctx.update(checks=checks, failed=failed, target=target, texts=texts, seconds=time.time() - t0, inp=inp, cache=cache)
    return ctx


def decision_lines(ctx):
    d, dc, b = ctx["dec"], ctx["dc"], ctx["base"]
    regs = ctx["regs"]
    full = next(r for r in regs if r["pair"] == "yen" and r["sample"] == "FULL" and r["spec"] == "gap2" and r["variant"] == "base")
    slope = next(r for r in regs if r["role"] == "SEPARATE")
    P = ctx["counts"]["P"]
    nz = lambda v, nd=6: f(v, nd) if v is not None else "n/a"
    L = []
    L.append("== decision (run_label %s) ==" % d["run_label"])
    L.append("PRIMARY: yen per USD, sample P, intervention and stale weeks dropped, dln_jpy = alpha + beta * d_gap_jp2 + e, H0: beta = 0 (two-sided 5%, HC3)")
    L.append("n = %d  (P has %d weekly changes: %d intervention weeks and %d stale-leg weeks dropped)" % (d["n"], P["weeks"], P["iv"], P["stale"]))
    L.append("alpha = %s   beta = %s   SE_HC3 = %s   p_HC3 = %s   SE_NW4 = %s   p_NW4 = %s" % (nz(d["alpha"]), nz(d["beta"]), nz(d["se_hc3"]), nz(d["p_hc3"]),
                                                                                              nz(d["se_nw4"]), nz(d["p_nw4"])))
    L.append("S = %s   S_all = %s   S_dropped = %s   X = %s   F = %s   n*alpha = %s   (S = n*alpha + F: %s)" % (
        nz(d["S"]), nz(d["S_all"]), nz(d["S_dropped"]), nz(d["X"]), nz(d["F"]), nz(d["n_alpha"]), nz(d["n_alpha"] + d["F"])))
    L.append("phi = %s   interval [%s, %s]" % (nz(d["phi"]), nz(d["phi_ci_lo"]), nz(d["phi_ci_hi"])))
    L.append("se_placebo = %s   n_placebo = %d (= n - 25)   SE_gate = %s   halfwidth_phi = %s   gate = %s" % (nz(d["se_placebo"]), d["n_placebo"], nz(d["se_gate"]),
                                                                                                  nz(d["halfwidth_phi"]), d["gate"]))
    L.append("class (primary)  = %s" % d["class_primary"])
    L.append("variant (a) NW4      : %s   [gate %s]" % (d["class_nw4"], d["gate_nw4"]))
    L.append("variant (b) restored : %s   [gate %s]  (n = %d)" % (d["class_restored"], d["gate_restored"], ctx["var"]["restored"]["n"]))
    L.append("variant (c) sameday  : %s   [gate %s]  (n = %d)" % (d["class_sameday"], d["gate_sameday"], ctx["var"]["sameday"]["n"]))
    L.append("VERDICT OF RECORD: %s" % d["verdict_of_record"])
    L.append("labels: %s" % d["labels"])
    L.append("SEPARATE (slope gap): beta = %s  p_HC3 = %s  phi = %s.  Sum of d_slope_gap over P is %s pp, so phi_s is near zero by construction." % (
        nz(slope["beta"]), nz(slope["p_hc3"]), nz(slope["phi"]), nz(slope["sum_dx"], 3)))
    L.append("FULL sample, yen 2y (descriptive): n = %d  beta = %s  SE_HC3 = %s  p_HC3 = %s  phi = %s" % (full["n"], nz(full["beta"]), nz(full["se_hc3"]),
                                                                                                          nz(full["p_hc3"]), nz(full["phi"])))
    L.append("S_all (all %d P weeks) = %s;  S_dropped = %s;  descriptive rows k = %d" % (P["weeks"], nz(d["S_all"]), nz(d["S_dropped"]), ctx["k_desc"]))
    if M("causal_text"):
        L.append("the yen moved because of intervention and flows drove it")
    return L


def report(ctx):
    L = ["%-4s %-5s %s" % (c[0], c[4], c[3]) for c in ctx["checks"]]
    L.append("")
    L += decision_lines(ctx)
    return L


# ------------------------------------------------------------------------------------------------------------------------
# selftest: synthetic data only; each guard G1-G21 has a test, and every mutant of it must make that test fail
# ------------------------------------------------------------------------------------------------------------------------
class Checks:
    def __init__(self):
        self.items = []

    def ok(self, name, cond, detail=""):
        self.items.append((name, bool(cond), "" if cond else detail))

    def eq(self, name, got, want):
        self.ok(name, got == want, "got %r, want %r" % (got, want))

    def close(self, name, got, want, tol):
        self.ok(name, got is not None and abs(got - want) <= tol, "got %r, want %r (tol %g)" % (got, want, tol))

    def raises(self, name, exc, fn):
        try:
            fn()
        except exc:
            self.ok(name, True)
        except Exception as e:
            self.ok(name, False, "raised %s: %s" % (type(e).__name__, e))
        else:
            self.ok(name, False, "did not raise")

    def failed(self):
        return [(n, d) for n, c, d in self.items if not c]


class Lcg:
    def __init__(self, seed):
        self.s = seed

    def u(self):
        self.s = (self.s * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        return ((self.s >> 11) / float(1 << 53)) * 2 - 1


def synth_rows(first=FIRST_WEEK, last=LAST_WEEK, seed=11):
    """Weekly level rows with regular dates (Friday fx_date, Thursday US/euro legs, Friday Japan leg); random-walk levels."""
    g = Lcg(seed)
    rows, we = [], first
    us2, us10, jp2, jp10, ea2, ea10, jpy, eur = 4.0, 4.3, 0.2, 0.8, 3.0, 3.3, 130.0, 0.9
    while we <= last:
        us2 += 0.08 * g.u()
        us10 += 0.07 * g.u()
        jp2 += 0.03 * g.u()
        jp10 += 0.03 * g.u()
        ea2 += 0.06 * g.u()
        ea10 += 0.05 * g.u()
        jpy *= math.exp(0.012 * g.u())
        eur *= math.exp(0.008 * g.u())
        thu = we - dt.timedelta(days=1)
        rows.append(dict(week_end=we, fx_date=we, usdjpy=jpy, eur_per_usd=eur, us_date=thu, us2=us2, us10=us10, us_date_sd=we,
                         us2_sd=us2 + 0.01 * g.u(), us10_sd=us10 + 0.01 * g.u(), jp_date=we, jp2=jp2, jp10=jp10, ea_date=thu, ea2_sa=ea2, ea10_sa=ea10,
                         _cross_jpy=jpy, _cross_eur=eur, _bis_missing=False))
        we += dt.timedelta(days=7)
    return rows


SYN_DAYS = [(dt.date(2024, 7, 11), 31678), (dt.date(2024, 7, 12), 23670)]
SYN_BLOCKS = [(dt.date(2026, 6, 29), dt.date(2026, 7, 29), 0.0), (dt.date(2026, 7, 30), dt.date(2026, 8, 26), 153993.0)]


def synth_ctx(seed=11):
    rows = finish_panel(synth_rows(seed=seed), SYN_DAYS, SYN_BLOCKS)
    ctx = analyze(rows, run_label="synthetic")
    ctx["pins"] = [["U.S. Treasury", "2 Yr par yield", "2024-03-22", "4.59", "percent"]]
    ctx["ivday_rows"] = [["day", "2024-07-11", "2024-07-11", "31678", "x", "y"]]
    return ctx


def fx_tsy_body(year, n=120, layout="2026"):
    hdr = ('Date,"1 Mo","2 Mo","3 Mo","4 Mo","6 Mo","1 Yr","2 Yr","3 Yr","5 Yr","7 Yr","10 Yr","20 Yr","30 Yr"' if layout == "2023" else
           'Date,"1 Mo","1.5 Month","2 Mo","3 Mo","4 Mo","6 Mo","1 Yr","2 Yr","3 Yr","5 Yr","7 Yr","10 Yr","20 Yr","30 Yr"')
    k = 14 if layout == "2023" else 15
    lines = [hdr]
    d = dt.date(year, 12, 31)
    for i in range(n):
        while d.weekday() >= 5:
            d -= dt.timedelta(days=1)
        lines.append(",".join(["%02d/%02d/%d" % (d.month, d.day, d.year)] + ["4.00"] * (k - 1)))
        d -= dt.timedelta(days=1)
    return ("\n".join(lines) + "\n").encode()


class FakeClock:
    def __init__(self, t=1_000_000.0):
        self.t = t

    def wall(self):
        return self.t

    def mono(self):
        return self.t

    def sleep(self, s):
        self.t += s


def fx_fetcher(tmp, opener, clock=None, **kw):
    clock = clock or FakeClock()
    return Fetcher(os.path.join(tmp, "cache"), os.path.join(tmp, "out"), opener=opener, wall=clock.wall, mono=clock.mono, sleeper=clock.sleep,
                   stop_path=os.path.join(tmp, "cache", "STOP"), now_utc=lambda: dt.datetime(2026, 10, 18, 12, 0, 0, tzinfo=dt.timezone.utc),
                   root=os.path.join(tmp, "norepo"), **kw), clock


FX_PARAMS = dict(BETA0=1.608146049, BETA1=0.6677584932, BETA2=2.8889513654, BETA3=6.8503522231, TAU1=1.0445730922, TAU2=13.8644399107)
G5_X = [0.10, -0.05, 0.20, 0.00, -0.15, 0.05, 0.12, -0.08, 0.03, -0.02]
G5_Y = [0.004, -0.006, 0.011, 0.001, -0.004, 0.000, 0.009, -0.007, 0.005, 0.002]


def weekdays(a, b, closed=()):
    out, d = [], a
    while d <= b:
        if d.weekday() < 5 and d not in closed:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def t_g1(ck):
    d = dt.date(2026, 9, 18)
    bis = {"JP": {d: 157.888307}, "XM": {d: 0.8726}}
    exr = {"JPY": {d: 180.94}, "USD": {d: 1.1460}}
    jpy, eur, cj, ce = fx_pair(bis, exr, d)
    ck.close("yen is yen per USD (greater than 100)", jpy, 157.888307, 1e-9)
    ck.ok("euro is euro per USD (below 1), not USD per euro", abs(eur - 0.8726) < 1e-9, "got %r" % eur)
    ck.close("ECB cross euro is 1/USD per EUR", ce, 1 / 1.1460, 1e-12)
    d0 = dt.date(2026, 9, 11)
    bis2 = {"JP": {d0: 150.0, d: 153.0}, "XM": {d0: 0.90, d: 0.92}}
    exr2 = {"JPY": {d0: 135.0, d: 138.0}, "USD": {d0: 1.5, d: 1.5}}
    r0, r1 = fx_pair(bis2, exr2, d0), fx_pair(bis2, exr2, d)
    ck.close("a stronger dollar raises the euro series: ln(0.92/0.90)", math.log(r1[1] / r0[1]), math.log(0.92 / 0.90), 1e-12)


def t_g2(ck):
    ck.close("gap = US minus foreign", gapf(4.0, 1.0), 3.0, 1e-12)
    ck.close("negative when foreign above US", gapf(1.0, 4.0), -3.0, 1e-12)


def t_g3(ck):
    pr = params_of(FX_PARAMS)
    ck.close("ea2_sa on the 2026-09-18 parameters", ea_semiannual(2, pr), 3.237019, 1e-5)
    ck.close("ea10_sa on the 2026-09-18 parameters", ea_semiannual(10, pr), 3.533452, 1e-5)
    ck.close("zero yield reproduces SR_2Y (1e-6)", svensson_z(2, *pr), 3.2152124072, 1e-6)
    ck.close("zero yield reproduces SR_10Y (1e-6)", svensson_z(10, *pr), 3.529753074, 1e-6)
    if not M("ea_sa_as_py"):
        ck.close("continuous-coupon par reproduces PY_2Y (1e-4)", par_continuous(2, pr), 3.2107329091, 1e-4)
        ck.close("continuous-coupon par reproduces PY_10Y (1e-4)", par_continuous(10, pr), 3.5024674241, 1e-4)


def t_g4(ck):
    rows = [dict(y=y, x=x) for x, y in zip(G5_X, G5_Y)]
    r = fit(rows, "y", ["x"])
    ck.close("residual sum is zero", r["resid_sum"], 0.0, 1e-8)
    ck.close("alpha (constant present)", r["alpha"], 0.0004644351, 1e-9)
    rg = r["regs"][0]
    ck.close("fitted_sum = beta * sum(x), intercept excluded", rg["fitted_sum"], rg["beta"] * sum(G5_X), 1e-12)
    ck.close("S = n*alpha + F", sum(G5_Y), 10 * r["alpha"] + rg["fitted_sum"], 1e-9)


def t_g5(ck):
    rows = [dict(y=y, x=x) for x, y in zip(G5_X, G5_Y)]
    r = fit(rows, "y", ["x"])
    rg = r["regs"][0]
    ck.close("beta", rg["beta"], 0.0517782427, 1e-9)
    ck.close("SE_HC3", rg["se_hc3"], 0.0119156725, 1e-9)
    ck.close("SE_NW4", rg["se_nw"], 0.0047685672, 1e-9)
    ck.close("HC0 (the mutant's value) computed correctly", r["res"]["se_hc0"][1], 0.0080437330, 1e-9)
    ck.close("HC1 (the mutant's value) computed correctly", r["res"]["se_hc1"][1], 0.0089931669, 1e-9)


def t_g6(ck):
    ecb_closed = {dt.date(2024, 3, 29), dt.date(2024, 4, 1), dt.date(2024, 5, 1), dt.date(2024, 12, 25), dt.date(2024, 12, 26), dt.date(2025, 1, 1),
                  dt.date(2025, 4, 18), dt.date(2025, 4, 21), dt.date(2025, 5, 1), dt.date(2025, 12, 25), dt.date(2025, 12, 26), dt.date(2026, 1, 1),
                  dt.date(2026, 4, 3), dt.date(2026, 4, 6), dt.date(2026, 5, 1)}
    us_closed = {dt.date(2024, 12, 25), dt.date(2025, 1, 1), dt.date(2025, 12, 25), dt.date(2026, 1, 1)}
    jp_closed = {dt.date(y, m, dd) for y in range(2023, 2027) for m, dd in ((12, 31), (1, 1), (1, 2), (1, 3))}
    a, b = dt.date(2023, 12, 1), dt.date(2026, 6, 30)
    ecb, us, jp = weekdays(a, b, ecb_closed), weekdays(a, b, us_closed), weekdays(a, b, jp_closed)
    ea = ecb
    for we, want in TRIPLES.items():
        fx, u, usd, j, e = pick_dates(we, ecb, us, jp, ea)
        ck.eq("triple for the week ending %s" % we, (fx, u, j), want)
    fx, u, usd, j, e = pick_dates(dt.date(2026, 5, 1), ecb, us, jp, ea)
    ck.eq("1 May 2026 (a Friday): fx_date moves back to Thursday 30 Apr", fx, dt.date(2026, 4, 30))
    ck.eq("1 May 2026: the US leg is strictly before fx_date", u, dt.date(2026, 4, 29))
    ck.eq("the same-calendar-Friday US leg is the check, on or before fx_date", usd, dt.date(2026, 4, 30))


def t_g7(ck):
    rows = synth_rows(dt.date(2024, 3, 22), dt.date(2025, 12, 26), seed=5)
    for i in range(1, len(rows)):
        dgap = (rows[i]["us2"] - rows[i]["jp2"]) - (rows[i - 1]["us2"] - rows[i - 1]["jp2"])
        rows[i]["usdjpy"] = rows[i - 1]["usdjpy"] * math.exp(0.03 * dgap)
    finish_panel(rows)
    kept = kept_rows(rows, "P", "yen")
    r = fit(kept, "dln_jpy", ["d_gap_jp2"])
    ck.close("fixture y_t = 0.03 * x_t gives beta = 0.03 exactly", r["regs"][0]["beta"], 0.03, 1e-9)
    ck.eq("n of the fixture", r["n"], len(kept))


def t_g8(ck):
    rows = finish_panel(synth_rows(dt.date(2024, 6, 28), dt.date(2026, 9, 18), seed=3), SYN_DAYS, SYN_BLOCKS)
    iv = {iso(r["week_end"]) for r in rows if r["drop_reason"]}
    ck.ok("Friday carry: ops on 11 and 12 Jul 2024 drop the weeks ending 12 Jul AND 19 Jul", {"2024-07-12", "2024-07-19"} <= iv, "got %s" % sorted(iv))
    blk = {"2026-07-31", "2026-08-07", "2026-08-14", "2026-08-21", "2026-08-28"}
    ck.ok("the 30 Jul-26 Aug block drops the five weeks that meet it", blk <= iv, "got %s" % sorted(iv))
    ck.ok("the zero-total window 29 Jun-29 Jul keeps its weeks", not ({"2026-07-03", "2026-07-10", "2026-07-17", "2026-07-24"} & iv), "got %s" % sorted(iv))
    ck.eq("nothing else is dropped", iv, {"2024-07-12", "2024-07-19"} | blk)
    r2 = finish_panel(synth_rows(dt.date(2022, 9, 9), dt.date(2022, 11, 4), seed=3), [(dt.date(2022, 10, 21), 56202)])
    ck.eq("a lone Friday op on 21 Oct 2022 drops 21 Oct and 28 Oct", {iso(r["week_end"]) for r in r2 if r["drop_reason"]}, {"2022-10-21", "2022-10-28"})


def t_g9(ck):
    ctx = synth_ctx()
    prim = [r for r in ctx["regs"] if r["role"] == "PRIMARY"]
    ck.eq("exactly one PRIMARY row", len(prim), 1)
    if prim:
        p = prim[0]
        ck.eq("PRIMARY is yen / P / gap2 / base / d_gap_jp2", (p["pair"], p["sample"], p["spec"], p["variant"], p["regressor"]), ("yen", "P", "gap2", "base", "d_gap_jp2"))
        ck.eq("PRIMARY starts with the week ending 2024-03-29", p["first_week"], dt.date(2024, 3, 29))
        ck.eq("PRIMARY standard error is the HC3 column (SE_HC3 is what the verdict uses)", ctx["dec"]["se_hc3"], p["se_hc3"])
    sep = [r for r in ctx["regs"] if r["role"] == "SEPARATE"]
    ck.eq("the SEPARATE row is the slope gap", [(r["spec"], r["regressor"]) for r in sep], [("slope", "d_slope_gap_jp")])


def t_g10(ck):
    rows = finish_panel(synth_rows(dt.date(2024, 6, 28), dt.date(2026, 9, 18), seed=3), SYN_DAYS, SYN_BLOCKS)
    kept = kept_rows(rows, "P", "yen", "restored")
    r = fit(kept, "dln_jpy", ["d_gap_jp2"])
    ck.eq("design matrix is exactly a constant and the gap change", r["design"], ["const", "d_gap_jp2"])
    ck.eq("one slope", len(r["regs"]), 1)


def t_g11(ck):
    for name, lit in SPEC_ALLOW.items():
        want = [c.strip() for c in lit.split(",")]
        ck.eq("%s: allowlist equals the spec's printed list" % name, allowlist(name), want)
        ck.eq("%s: the written header equals the spec's printed list" % name, render_csv(name, [], "# source: t").split("\n")[1], ",".join(want))
    blob = "\n".join("%s:%s" % (k, ",".join(allowlist(k))) for k in sorted(SPEC_ALLOW))
    ck.eq("sha256 of the allowlist block equals the pinned spec hash", hashlib.sha256(blob.encode()).hexdigest(), SPEC_ALLOW_SHA256)
    for name, allow in ALLOW.items():
        ck.eq("%s: its own header passes" % name, render_csv(name, [], "# source: t").split("\n")[1], ",".join(allow))
        ck.raises("%s: an extra column is a hard failure" % name, DataError, lambda: render_csv(name, [], "# source: t", header=list(allow) + ["extra"]))
        ren = list(allow)
        ren[-1] = ren[-1] + "_x"
        ck.raises("%s: a renamed column is a hard failure" % name, DataError, lambda: render_csv(name, [], "# source: t", header=ren))
    ck.raises("a file without a source line is refused", DataError, lambda: render_csv("pins.csv", [], "no source here"))


FEIO_FIX = """財務省,,,,,,,,
Ministry of Finance,,,,,,,,
,,,,,,,,
(単位:億円),,,,,,,,
(amount:100 million Yen),,,,,,,,
,,,,,,,,
年,月,日,Year,Month,Day,金額(amount),売買通貨,Currency pairs
,,,,,,,,
令和4年,9月,22日,2022,Sep,22,"28,382",米ドル売り・日本円買い,the US dollar (sold) the Japanese yen (bought)
令和4年7月～9月期計,,,July - September 2022,,,"28,382",,
令和4年,10月,21日,2022,Oct,21,"56,202",米ドル売り・日本円買い,the US dollar (sold) the Japanese yen (bought)
,,24日,,,24,"7,296",米ドル売り・日本円買い,the US dollar (sold) the Japanese yen (bought)
令和4年10月～12月期計,,,October - December 2022,,,"63,499",,
令和6年,4月,29日,2024,Apr,29,"59,185",米ドル売り・日本円買い,the US dollar (sold) the Japanese yen (bought)
,5月,1日,,May,1,"38,700",米ドル売り・日本円買い,the US dollar (sold) the Japanese yen (bought)
令和6年4月～6月期計,,,April - June 2024,,,"97,885",,
令和8年,4月,30日,2026,Apr,30,"62,787",米ドル売り・日本円買い,the US dollar (sold) the Japanese yen (bought)
,5月,4日,,May,4,"7,802",米ドル売り・日本円買い,the US dollar (sold) the Japanese yen (bought)
,5月,6日,,May,6,"46,759",米ドル売り・日本円買い,the US dollar (sold) the Japanese yen (bought)
令和8年4月～6月期計,,,April - June 2026,,,"117,349",,
,,,,,,,,
(注1) 日本円を対価としない外国為替平衡操作の場合,,,,,,,,
"""


def t_g12(ck):
    raw = FEIO_FIX.encode("cp932")
    got = parse_feio(raw)
    want = {dt.date(2022, 9, 22): 28382, dt.date(2022, 10, 21): 56202, dt.date(2022, 10, 24): 7296, dt.date(2024, 4, 29): 59185, dt.date(2024, 5, 1): 38700,
            dt.date(2026, 4, 30): 62787, dt.date(2026, 5, 4): 7802, dt.date(2026, 5, 6): 46759}
    ck.eq("day rows (year and month carried, subtotals skipped, commas removed)", dict(got["days"]), want)
    ck.eq("four quarter subtotals", len(got["quarters"]), 4)
    ck.eq("Q4 2022: days 63,498 against subtotal 63,499", [(q[1], q[3]) for q in got["quarters"] if q[0] == dt.date(2022, 12, 31)], [(63499, 63498)])
    ck.eq("covered through the end of Q2 2026", got["covered_through"], dt.date(2026, 6, 30))
    ck.close("monthly page in billions: 15,399.3 billion yen = 153,993 x 100m",
             parse_monthly("Total amount of foreign exchange intervention operations for the period from July 30, 2026 through August 26, 2026\n"
                           "<p align=\"right\">&yen;　" + "15,399.3 billion</p>")[2], 153993.0, 1e-9)
    ck.close("monthly page, zero", parse_monthly("Total amount of foreign exchange intervention operations for the period from June 29, 2026 through July 29, 2026\n"
                                                 "<p align=\"right\">&yen;　" + "0</p>")[2], 0.0, 1e-12)


MOF_FIX = ("Interest Rate,,,,,,,,,,,,,,,(Unit : %)\nDate,1Y,2Y,3Y,4Y,5Y,6Y,7Y,8Y,9Y,10Y,15Y,20Y,25Y,30Y,40Y\n"
           "1974/9/24,10.327,9.362,8.83,8.515,8.348,8.29,8.24,8.121,8.127,-,-,-,-,-,-\n"
           "2024/3/9,0.054,0.189,0.2,0.277,0.372,0.394,0.473,0.559,0.644,0.75,1.15,1.484,1.654,1.789,1.939\n")


def t_g13(ck):
    m = parse_mof_yields(MOF_FIX)
    ck.eq("'-' is missing, not zero", m[dt.date(1974, 9, 24)], (9.362, None))
    ck.eq("unpadded date 2024/3/9", m.get(dt.date(2024, 3, 9)), (0.189, 0.75))
    ck.eq("agreeing overlap is merged", len(merge_mof(m, {dt.date(2024, 3, 9): (0.189, 0.75)})), 2)
    ck.raises("disagreeing overlap is a hard failure", DataError, lambda: merge_mof(m, {dt.date(2024, 3, 9): (0.19, 0.75)}))


def t_g14(ck):
    r23 = ("12/29/2023,5.60,5.59,5.40,5.41,5.26,4.79,4.23,4.01,3.84,3.88,3.88,4.20,4.03\n")
    r26 = ("10/16/2026,4.12,4.14,4.17,4.26,4.32,4.34,4.46,4.74,4.82,4.89,4.98,5.09,5.47,5.43\n")
    h23 = 'Date,"1 Mo","2 Mo","3 Mo","4 Mo","6 Mo","1 Yr","2 Yr","3 Yr","5 Yr","7 Yr","10 Yr","20 Yr","30 Yr"\n'
    h26 = 'Date,"1 Mo","1.5 Month","2 Mo","3 Mo","4 Mo","6 Mo","1 Yr","2 Yr","3 Yr","5 Yr","7 Yr","10 Yr","20 Yr","30 Yr"\n'
    ck.eq("2023 layout read by header: 2 Yr 4.23, 10 Yr 3.88", parse_treasury(h23 + r23)[dt.date(2023, 12, 29)], (4.23, 3.88))
    ck.eq("2026 layout read by header: 2 Yr 4.74, 10 Yr 5.09", parse_treasury(h26 + r26)[dt.date(2026, 10, 16)], (4.74, 5.09))


def t_g15(ck):
    body = fx_tsy_body(2026)
    treq = request_table()[9]                          # the 2026 Treasury file (not immutable)
    assert treq["key"] == "tsy2026"

    def good(host, target, headers, timeout, cap):
        return 200, body

    def mk(opener, **kw):
        tmp = tempfile.mkdtemp(prefix="fxst_")
        return tmp, fx_fetcher(tmp, opener, **kw)
    # non-200 latches
    tmp, (fe, _) = mk(lambda *a: (403, b""))
    try:
        fe.fetch_one(treq)
        ck.ok("HTTP 403 latches", False, "no exception")
    except Latched:
        ck.ok("HTTP 403 latches", os.path.exists(os.path.join(tmp, "cache", "STOP")))
    ck.raises("while STOP exists the next fetch refuses", Latched, lambda: fe.fetch_one(request_table()[0]))
    tmp, (fe, _) = mk(lambda *a: (301, b""))
    try:
        fe.fetch_one(treq)
        ck.ok("a redirect latches (not followed)", False, "no exception")
    except Latched:
        ck.ok("a redirect latches (not followed)", os.path.exists(os.path.join(tmp, "cache", "STOP")))
    tmp, (fe, _) = mk(lambda *a: (200, b"<html>Access denied</html>"))
    try:
        fe.fetch_one(treq)
        ck.ok("a 200 that is not the file latches", False, "no exception")
    except Latched:
        ck.ok("a 200 that is not the file latches", os.path.exists(os.path.join(tmp, "cache", "STOP")))

    def sock(*a):
        raise SocketFault("timeout")
    tmp, (fe, _) = mk(sock)
    try:
        fe.fetch_one(treq)
        ck.ok("a socket fault ends the run", False, "no exception")
    except SocketFault:
        ck.ok("a socket fault ends the run", True)
        ck.ok("a socket fault does NOT latch", not os.path.exists(os.path.join(tmp, "cache", "STOP")))
    except Latched:
        ck.ok("a socket fault ends the run, without latching", False, "latched")
    ck.raises("FRED host is refused", Refused, lambda: check_url("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2"))
    ck.raises("a path outside the request table is refused", Refused, lambda: check_url("https://home.treasury.gov/other.csv"))
    ck.raises("plain http is refused", Refused, lambda: check_url("http://home.treasury.gov" + treq["target"]))
    at = chr(64)
    ck.raises("an address in the identification string is refused", Refused, lambda: assert_ua(UA + " x" + at + "y.org"))
    ck.ok("the identification string is the CLAUDE.md one and has no address", UA == "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
          and at not in UA)
    # pacing: five good requests, starts at least 2 s apart, using the real request table (five immutable-free kinds are not needed: same request, new day)
    starts, clock = [], FakeClock()

    def timed(host, target, headers, timeout, cap):
        starts.append(clock.t)
        clock.t += 0.2
        ck.ok("the request carries the neutral identification string", headers["User-Agent"] == UA)
        return 200, body
    tmp = tempfile.mkdtemp(prefix="fxst_")
    fe, _ = fx_fetcher(tmp, timed, clock=clock)
    for i in range(4):
        path = os.path.join(tmp, "cache", treq["file"])
        if os.path.exists(path):
            os.remove(path)
        fe.fetch_one(dict(treq))
    gaps = [b - a for a, b in zip(starts, starts[1:])]
    ck.ok("request starts are at least 2 s apart", len(gaps) == 3 and min(gaps) >= 2.0, "gaps %s" % gaps)
    # cap and cache layout
    ck.raises("--max-requests above 30 is refused", Refused, lambda: fx_fetcher(tempfile.mkdtemp(prefix="fxst_"), good, max_requests=31))
    fe, _ = fx_fetcher(tempfile.mkdtemp(prefix="fxst_"), good, max_requests=1)
    fe.fetch_one(request_table()[9])
    ck.raises("the cap stops a second request", MaxRequests, lambda: fe.fetch_one(request_table()[10]))
    ck.eq("a good body is saved and logged", [r[3] for r in read_csv_rows(fe.log_path)[1]][:1], ["200"])


def t_g16(ck):
    ctx = synth_ctx()
    for pair in ("yen", "euro"):
        for spec, xc in SPECS[pair]:
            n = sum(1 for r in ctx["regs"] if r["sample"] == "FULL" and r["pair"] == pair and r["spec"] == spec and r["variant"] == "base")
            ck.eq("FULL rows for %s %s" % (pair, spec), n, len(xc))


def t_g17(ck):
    lo, hi = phi_interval(0.6, 0.2, -1.0, 1.0)
    ck.ok("phi endpoints are sorted when X/S < 0", lo <= hi, "got %r, %r" % (lo, hi))
    lo, hi = phi_interval(0.6, 0.2, -1.0, -1.0)
    ck.ok("and when X/S > 0", lo <= hi)


def t_g18(ck):
    rows = synth_rows(dt.date(2019, 4, 19), dt.date(2019, 5, 17), seed=2)
    jp = [dt.date(2019, 4, 19), dt.date(2019, 4, 26), dt.date(2019, 4, 26), dt.date(2019, 5, 10), dt.date(2019, 5, 17)]
    for r, d in zip(rows, jp):
        r["jp_date"] = d
    finish_panel(rows)
    ck.eq("Golden Week 2019: stale flags by week", [r["_stale_jp"] for r in rows], [False, False, True, True, False])
    ck.eq("the euro pair is not dropped by a Japanese closure", [r["_stale_ea"] for r in rows], [False] * 5)


def t_g19(ck):
    for w in ("caused", "drove", "because of intervention", "leaned against", "the move was caused by flows"):
        ck.ok("scanner sees %r" % w, bool(causal_hits("so it " + w + " the yen")))
    ctx = synth_ctx()
    log = [["2026-10-18T10:00:00.000Z", TSY_HOST, "/x", "200", "1", "ab"]]
    ck.eq("README carries no causal wording", causal_hits(render_readme(ctx, log)), [])
    ck.eq("SOURCES carries none", causal_hits(render_sources(log)), [])
    ck.eq("the printout carries none", causal_hits("\n".join(decision_lines(ctx))), [])


def t_g20(ck):
    def prim(beta, se, X, S, S_all=None, se_p=1e-4, se_nw=None):
        return dict(beta=beta, se_hc3=se, se_nw4=se if se_nw is None else se_nw, X=X, S=S, S_all=S if S_all is None else S_all, se_placebo=se_p)

    def same(p):
        return {"restored": dict(p), "sameday": dict(p)}
    d = decide(prim(0.8, 0.1, -1.0, -1.0), same(prim(0.8, 0.1, -1.0, -1.0)))
    ck.eq("AT LEAST HALF reaches the verdict", d["verdict"], CLS_HALF)
    c = classify(0.6, 0.20408, -1.0, 1.0)
    ck.close("class function, case phi_hat = -0.6", c["phi"], -0.6, 1e-9)
    ck.ok("class function, case phi_hi = -0.2", abs(c["phi_hi"] + 0.2) < 1e-3, "got %r" % c["phi_hi"])
    ck.eq("phi_hi < 0 gives POINTS THE OTHER WAY, not Grok's |phi| < 0.25 rule", c["cls"], CLS_OTHER)
    p = prim(0.6, 1e-4, -1.0, 1.0)
    ck.eq("POINTS THE OTHER WAY reaches the verdict when the design is powered", decide(p, same(p))["verdict"], CLS_OTHER)
    p = prim(0.05, 0.02, -1.0, -1.0)
    ck.eq("LESS THAN A QUARTER", decide(p, same(p))["verdict"], CLS_LTQ)
    p = prim(0.3, 1e-4, -1.0, -1.0)
    ck.eq("UNCLASSIFIED gives plain INCONCLUSIVE", decide(p, same(p))["verdict"], "INCONCLUSIVE")
    p = prim(0.8, 0.1, -1.0, -1.0)
    v = same(p)
    v["restored"] = prim(0.05, 0.02, -1.0, -1.0)
    ck.eq("a variant whose class differs makes the verdict fragile", decide(p, v)["verdict"], "INCONCLUSIVE (fragile: b)")
    p = prim(0.8, 0.1, -1.0, -1.0, se_p=0.2)
    ck.eq("the power gate: half-width above 0.25 is underpowered", decide(p, same(p))["verdict"], "INCONCLUSIVE (underpowered)")
    p = prim(0.8, 1e-4, -1.0, -0.008)
    ck.eq("|S| = 0.008 is INCONCLUSIVE", decide(p, same(p))["verdict"], "INCONCLUSIVE (|S| <= 0.01)")
    p = prim(0.8, 1e-4, -0.4, -0.5)
    ck.eq("|X| = 0.4 is INCONCLUSIVE", decide(p, same(p))["verdict"], "INCONCLUSIVE (|X| < 0.5pp)")
    p = prim(0.8, 0.1, -1.0, -1.0, S_all=-3.0)
    ck.close("phi uses S, not S_all", decide(p, same(p))["primary"]["phi"], 0.8, 1e-9)


def t_g21(ck):
    g = Lcg(9)
    x = [g.u() for _ in range(118)]
    plac = placebo_betas(list(x), x)
    ck.eq("n_placebo = n - 25", len(plac), 118 - 25)
    ck.ok("shift 0 (beta = 1 for y = x) is not among the placebo shifts", max(plac) < 0.9, "max %r" % max(plac))


def t_x_cache(ck):
    tmp = tempfile.mkdtemp(prefix="fxst_")
    try:
        subprocess.run(["git", "init", "-q", tmp], check=True, capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        ck.ok("git available for the cache-path test", False, "git failed")
        return
    with open(os.path.join(tmp, ".gitignore"), "w") as fh:
        fh.write("ign/\n")
    out = os.path.join(tmp, "out")
    ck.eq("a cache git ignores is accepted", check_cache(os.path.join(tmp, "ign"), root=tmp, out_dir=out), os.path.realpath(os.path.join(tmp, "ign")))
    ck.raises("a cache inside the repo that git does not ignore is refused", Refused, lambda: check_cache(os.path.join(tmp, "notign"), root=tmp, out_dir=out))
    ck.raises("a cache in the committed output folder is refused", Refused, lambda: check_cache(os.path.join(out, "x"), root=tmp, out_dir=out))
    ck.eq("a cache outside the repo is accepted", check_cache(tempfile.mkdtemp(prefix="fxst_"), root=tmp, out_dir=out) is not None, True)


def t_x_quarantine(ck):
    good = dict(FX_PARAMS)
    pr = params_of(good)
    good.update(SR_2Y=svensson_z(2, *pr), SR_10Y=svensson_z(10, *pr))
    bad = dict(good)
    bad["SR_2Y"] += 0.01
    short = {k: v for k, v in good.items() if k != "BETA3"}
    clean, incomplete, quar = usable_yc({dt.date(2022, 6, 22): good, dt.date(2022, 6, 23): bad, dt.date(2021, 12, 14): short})
    ck.eq("a date whose parameters do not reproduce the published SR is quarantined", sorted(quar), [dt.date(2022, 6, 23)])
    ck.eq("an incomplete parameter set is set aside", incomplete, [dt.date(2021, 12, 14)])
    ck.eq("the good date stays", sorted(clean), [dt.date(2022, 6, 22)])


def t_x_iv_runs(ck):
    ctx = synth_ctx()
    ctx["dec"] = dict(ctx["dec"], run_label="csv_through_2026-06-30_blocks_1")
    first = render_all(ctx, [], [], [])["decision.csv"]
    old_rows = read_csv_rows_from_text(first)
    ctx["dec"] = dict(ctx["dec"], run_label="csv_through_2026-09-30_blocks_0", beta=0.5)
    second = render_all(ctx, [], old_rows, [])["decision.csv"]
    labels = [r[0] for r in read_csv_rows_from_text(second)]
    ck.eq("the earlier run is kept beside the new one", labels, ["csv_through_2026-06-30_blocks_1", "csv_through_2026-09-30_blocks_0"])
    third = render_all(ctx, [], read_csv_rows_from_text(second), [])["decision.csv"]
    ck.eq("the same run twice leaves the file unchanged", third, second)
    covered = [dict(name="a", start=dt.date(2026, 7, 30), end=dt.date(2026, 8, 26), amount=153993.0, covered=True)]
    inp = Inputs()
    inp.feio = dict(days=[(dt.date(2026, 8, 3), 100)], covered_through=dt.date(2026, 9, 30))
    inp.monthly = covered
    days, blocks, label = iv_inputs(inp)
    ck.eq("a window the quarterly CSV covers is replaced by its dated days", (len(days), blocks, label), (1, [], "csv_through_2026-09-30_blocks_0"))


def read_csv_rows_from_text(text):
    rows = list(csv.reader(io.StringIO("".join(ln for ln in text.splitlines(True) if not ln.startswith("#")))))
    return rows[1:]


def t_x_panel(ck):
    ctx = synth_ctx()
    texts = render_all(ctx, [], [], [])
    cache, out = tempfile.mkdtemp(prefix="fxst_"), tempfile.mkdtemp(prefix="fxst_")
    try:
        write_outputs(texts, cache, out)
    except DataError as e:
        ck.ok("write_outputs completed", False, str(e))
    ck.ok("the weekly panel is in the cache", os.path.exists(os.path.join(cache, "weekly_panel.csv")))
    ck.ok("the weekly panel is NOT in the output folder", not os.path.exists(os.path.join(out, "weekly_panel.csv")))
    ck.eq("the output folder holds the eight committed files and nothing else", sorted(os.listdir(out)),
          sorted(["README.md", "SOURCES.md", "checks.csv", "decision.csv", "event_weeks.csv", "intervention_days.csv", "pins.csv", "regressions.csv"]))


def t_x_kept(ck):
    rows = finish_panel(synth_rows(), SYN_DAYS, SYN_BLOCKS)
    ck.eq("sample P has 130 weekly changes", len(week_rows(rows, "P")), 130)
    ck.eq("primary keeps 130 - 7 intervention weeks = 123", len(kept_rows(rows, "P", "yen")), 123)
    ck.eq("variant (b) restores them: 130", len(kept_rows(rows, "P", "yen", "restored")), 130)
    ck.eq("the euro pair drops no intervention week: 130", len(kept_rows(rows, "P", "euro")), 130)
    ck.eq("sameday variant keeps 123", len(kept_rows(rows, "P", "yen", "sameday")), 123)
    ck.eq("sample_counts agrees (kept, iv)", (sample_counts(rows)["P"]["kept"], sample_counts(rows)["P"]["iv"]), (123, 7))


def t_x_stop(ck):
    tmp = tempfile.mkdtemp(prefix="fxst_")
    fe, _ = fx_fetcher(tmp, lambda *a: (200, fx_tsy_body(2026)))
    os.makedirs(os.path.join(tmp, "cache"), exist_ok=True)
    with open(os.path.join(tmp, "cache", "STOP"), "w") as fh:
        fh.write("test\n")
    ck.raises("an existing STOP file blocks every fetch", Latched, lambda: fe.fetch_one(request_table()[9]))


GUARDS = [
    ("G1", "sign convention: both pairs foreign currency per USD", ["eur_usd_per_eur"], t_g1),
    ("G2", "gap direction: US minus foreign", ["gap_foreign_minus_us"], t_g2),
    ("G3", "compounding: semiannual euro par from the parameters", ["ea_sa_as_sr", "ea_sa_as_py"], t_g3),
    ("G4", "intercept and contribution: constant present, F excludes alpha", ["no_constant", "f_includes_alpha"], t_g4),
    ("G5", "estimator: HC3 primary, NW lag 4 check", ["hc0", "hc1", "nw_lag0"], t_g5),
    ("G6", "no look-ahead: US/euro legs strictly before fx_date; TARGET-holiday fallback", ["same_day_us", "no_fx_fallback"], t_g6),
    ("G7", "no leads or lags: d_x at t uses rows t and t-1", ["shift_regressor"], t_g7),
    ("G8", "intervention drop: dated, Friday carry, blocks", ["iv_exclusive_start", "iv_block_ignored", "iv_zero_block_dropped"], t_g8),
    ("G9", "single primary: yen, 2y gap, P, HC3", ["two_primaries", "primary_slope", "p_start_0322"], t_g9),
    ("G10", "no amount regressor", ["amount_regressor"], t_g10),
    ("G11", "exact column allowlists, anchored to the spec's printed lists and their sha256", ["extra_column", "renamed_column", "allow_drift"], t_g11),
    ("G12", "MoF intervention parse: CP932, year and month carried, subtotals skipped", ["year_not_carried", "month_not_carried", "subtotal_as_day", "utf8_decode"], t_g12),
    ("G13", "MoF yield parse: '-' missing, unpadded dates, overlap rule", ["dash_as_zero", "overlap_ignored"], t_g13),
    ("G14", "Treasury read by header name", ["positional_treasury"], t_g14),
    ("G15", "fetch safety: latches, redirects, socket fault, FRED, identification string, pacing",
     ["no_latch_non200", "no_latch_redirect", "no_latch_bad_body", "latch_on_socket", "allow_fred", "ua_check_off", "no_pacing"], t_g15),
    ("G16", "FULL sample beside every split", ["drop_full"], t_g16),
    ("G17", "phi interval sorted", ["unsorted_phi"], t_g17),
    ("G18", "stale legs: span 4-10 days", ["no_stale_check"], t_g18),
    ("G19", "no causal text", ["causal_text"], t_g19),
    ("G20", "decision function of section 4", ["grok_abs_rule", "gate_skipped", "ignore_variant_flip", "no_s_floor", "no_x_floor", "phi_s_all"], t_g20),
    ("G21", "placebo set: shifts 13 ... n-13 only", ["placebo_shift0"], t_g21),
    ("X1", "cache path: outside the repo, or git-ignored inside it", ["cache_check_off"], t_x_cache),
    ("X2", "an existing STOP file blocks fetching", ["stop_ignored"], t_x_stop),
    ("X3", "an ECB date whose parameters do not reproduce its own SR is quarantined, named in C05", ["no_quarantine"], t_x_quarantine),
    ("X5", "build writes weekly_panel.csv to the cache only, never to the output folder", ["panel_to_output"], t_x_panel),
    ("X6", "kept_rows drops intervention weeks (primary 123, variant b 130 on the fixture)", ["kept_keeps_iv"], t_x_kept),
    ("X4", "decision.csv keeps every run_label; a quarterly CSV that covers a block replaces it", ["decision_overwrite"], t_x_iv_runs),
]


def run_test(fn):
    ck = Checks()
    try:
        fn(ck)
    except Exception as e:                      # a test that crashes under a mutant has noticed it
        ck.ok("test ran to completion", False, "%s: %s" % (type(e).__name__, e))
    return ck


def selftest(mutants=True):
    t0 = time.time()
    bad_total, n_checks, n_mut = 0, 0, 0
    for gid, desc, muts, fn in GUARDS:
        ck = run_test(fn)
        n_checks += len(ck.items)
        bad = ck.failed()
        bad_total += len(bad)
        print("%-4s %s: %d checks, %s" % (gid, desc, len(ck.items), "ok" if not bad else "FAILED"))
        for name, detail in bad:
            print("       FAIL  %s   <- %s" % (name, detail))
        if mutants:
            for m in muts:
                with mutant(m):
                    mk = run_test(fn)
                caught = bool(mk.failed())
                n_mut += 1
                bad_total += 0 if caught else 1
                print("       mutant %-24s %s%s" % (m, "caught" if caught else "NOT CAUGHT", "  (first failing check: %s)" % mk.failed()[0][0] if caught else ""))
    print("selftest: %d guards, %d checks, %d mutants applied one at a time, %d failure(s), %.1f s" % (len(GUARDS), n_checks, n_mut, bad_total, time.time() - t0))
    return 0 if bad_total == 0 else 1


# ------------------------------------------------------------------------------------------------------------------------
# command line
# ------------------------------------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch", help="download the 19 files into the cache (the only network command)")
    pf.add_argument("--cache", default=CACHE_DEFAULT)
    pf.add_argument("--out", default=OUT_DEFAULT, help="where fetch_log.csv is kept")
    pf.add_argument("--sleep", type=float, default=MIN_SLEEP, help="seconds between request starts (at least 2)")
    pf.add_argument("--max-requests", type=int, default=MAX_REQUESTS)
    pb = sub.add_parser("build", help="offline: validate the cache and write every output")
    pb.add_argument("--cache", default=CACHE_DEFAULT)
    pb.add_argument("--out", default=OUT_DEFAULT)
    ps = sub.add_parser("selftest", help="synthetic data, mutants applied one at a time; no network")
    ps.add_argument("--no-mutants", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest(mutants=not a.no_mutants)
    try:
        if a.cmd == "build":
            ctx = build(a.cache, a.out)
            print("\n".join(report(ctx)))
            print("\nwrote %s to %s (%.0f s)" % (", ".join(sorted(ctx["texts"])), tilde(ctx["target"]), ctx["seconds"]))
            if ctx["failed"]:
                print("FAIL: %s. Outputs went to %s, the committed files were left alone." % (", ".join(c[0] for c in ctx["failed"]), tilde(ctx["target"])),
                      file=sys.stderr)
                return 1
            return 0
        fe = Fetcher(a.cache, a.out, sleep=a.sleep, max_requests=a.max_requests)
        fe.check_stop()
        saved = fe.run(request_table())
        print("requests sent: %d, files saved: %d" % (fe.requests, saved))
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
