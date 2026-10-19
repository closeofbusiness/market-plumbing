#!/usr/bin/env python3
"""The rolling 3-month carry of a currency-hedged 10-year Treasury, for a yen-based and a euro-based investor. Python 3 standard library only.

  python3 bin/hedged_ust_yield.py fetch [--cache DIR] [--out DIR] [--sleep 2.05] [--max-requests 30] [--dks-full]   # the only network command
  python3 bin/hedged_ust_yield.py build [--cache DIR] [--out DIR] [--ledger FILE]                                   # offline; byte-identical on re-run
  python3 bin/hedged_ust_yield.py selftest [--no-mutants]                                                         # synthetic data only; no network

Specification: _research/2026-10-19-FX-Hedged-Treasury-Yield-Spec.md (with its Amendments, the supervisor's rulings and its "Builder decisions"
section). The validation gate of its section 5 is applied as written; a miss beyond it is a FAILED build (outputs go to <out>/_FAILED/, exit 1).

WHAT TOUCHES THE NETWORK. Only `fetch`. Hosts: home.treasury.gov, www.mof.go.jp, data-api.ecb.europa.eu, markets.newyorkfed.org,
www.stat-search.boj.or.jp, jschreger.s3.us-east-2.amazonaws.com and api.statistiken.bundesbank.de. Any other host (FRED, sec.gov, DTCC included) is
refused before a request is made, and each request must be one of the exact URLs of the request table. GET only; one request at a time; at least
2 s between request starts, remembered across invocations; at most 30 requests per run; the CLAUDE.md non-SEC identification string (no address, no
name); no redirect is followed. Any HTTP status other than 200 (206 for the DKS probe), or a body that fails its content test, writes
<cache>/STOP and ends the run. While STOP exists every fetch refuses; only a person deletes it. A socket fault ends the invocation without latching.
Nothing retries. Every request is one row of data/hedged_ust_yield/fetch_log.csv.

WHAT IT NEVER READS. DTCC files. The swap-tape cells (3-month and 1-year OIS and cross-currency medians) come only from the ledger's committed
monthly output, data/swap_tape/monthly_short_tenor.csv (bin/swap_tape_ledger.py monthly, THE_ASK.md E-024).

WHERE THE FILES LIVE. The cache (default data/vintages/hedged_ust_yield/) holds every raw download, every daily series and the yen monthly rows. It is
gitignored. Committed files carry the euro monthly rows and yen annual figures only (spec section 7). "Rolling 3-month carry" is a measure of an
incentive, never the yield an investor earns over ten years.
"""
import argparse
import bisect
import calendar
import contextlib
import csv
import datetime as dt
import hashlib
import http.client
import io
import json
import math
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_rate_gap as fx  # noqa: E402  (read-only: parsers, the Svensson curve, the causal-wording pattern)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(ROOT, "data", "hedged_ust_yield")
CACHE_DEFAULT = os.path.join(ROOT, "data", "vintages", "hedged_ust_yield")
LEDGER_DEFAULT = os.path.join(ROOT, "data", "swap_tape", "monthly_short_tenor.csv")
STOP_PATH = os.path.join(CACHE_DEFAULT, "STOP")            # fixed, whatever --cache says

# R2: the CLAUDE.md canonical string for every non-SEC host. No address, no name.
UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
HEADERS = {"User-Agent": UA, "Accept-Encoding": "identity", "Accept": "*/*"}
MIN_SLEEP = 2.05
MAX_REQUESTS = 30
TIMEOUT = 180
BODY_CAP = 64 * 1024 * 1024
DKS_CAP = 256 * 1024 * 1024
TSY_HOST, MOF_HOST, ECB_HOST, NYF_HOST, BOJ_HOST, DKS_HOST, BBK_HOST = (
    "home.treasury.gov", "www.mof.go.jp", "data-api.ecb.europa.eu", "markets.newyorkfed.org", "www.stat-search.boj.or.jp",
    "jschreger.s3.us-east-2.amazonaws.com", "api.statistiken.bundesbank.de")
HOST_ALLOW = frozenset({TSY_HOST, MOF_HOST, ECB_HOST, NYF_HOST, BOJ_HOST, DKS_HOST, BBK_HOST})
FIRST_TSY_YEAR = 2018
JGB_ALL_PATH = fx.JGB_PATH
JGB_CUR_PATH = "/english/policy/jgbs/reference/interest_rate/jgbcme.csv"
YC_PATH = fx.YC_PATH.replace("startPeriod=2017-12-01", "startPeriod=2018-01-01")
SOFR_PATH = "/api/rates/secured/sofr/search.csv?startDate=2018-04-01&endDate={today}"
EFFR_PATH = "/api/rates/unsecured/effr/search.csv?startDate=2018-01-01&endDate={today}"
SOFRAI_PATH = "/api/rates/secured/sofrai/search.json?startDate=2020-03-02&endDate={today}"
EST_PATH = "/service/data/EST/B.EU000A2X2A25+EU000A2QQF08.WT+CI?format=csvdata&startPeriod=2019-10-01"
TONA_PATH = "/api/v1/getDataCode?format=csv&lang=en&db=FM01&code=STRDCLUCON&startDate=201801"
DKS_PATH = "/cip_dataset_v4.csv"
BBK_PATH = fx.BBK_PATH
DKS_HEADER = "group,currency,tenor,date,diff_y,rho,cip_govt,cip_govt_break_date,rho_ibor,rho_sofr,cip_govt_ibor,cip_govt_sofr"
DKS_SIZE_OBSERVED = 118471039
DKS_ETAG_OBSERVED = "eb058f21fd563d35e00644bdb42120a1-7"
TONA_PAGES_MAX = 3

# Calendar constants of the spec
YEN_RATE_START = dt.date(2018, 4, 2)      # SOFR's first publication; TONA from 2018-01-04
EURO_RATE_START = dt.date(2019, 10, 1)    # the euro short-term rate's first date
EURO_HEADLINE_START = "2024-10"
STALE_DAYS = 5                            # a leg more than 5 calendar days older than d drops the row (3.6)
QE_START_MONTHS = (3, 6, 9, 12)           # the quarter-end flag (3.7, O-7)
BASIS_DAY = {"yen": 365.0, "euro": 360.0}   # B_home; B_us is 360 (SOFR, EFFR)
PAIR_CCY = {"yen": "JPY", "euro": "EUR"}
BOJ_CREDIT = ("This service uses the API provided by the \"Bank of Japan Time-Series Data Search.\" The Bank of Japan does not guarantee the "
              "content of the service.")
REQUIRED_SENTENCE = "This measures an incentive. It does not show what led any investor to buy, sell or hedge."
PRE_FIX_GATE = {("H", "3m"): 10.441, ("P", "3m"): 6.658, ("H", "1y"): 11.183, ("P", "1y"): 10.090}      # the gate medians (bp) before the 19 Oct ledger fix
BUGFIX_NOTE = ("Corrected on 19 Oct 2026 after independent verification: the ledger's monthly stage dropped overnight-index swap trades booked under the COMPOUND "
               "index names (USD-SOFR-COMPOUND and EUR-EuroSTR-COMPOUND), because its first version required the letters OIS in the index name. The euro 3-month "
               "headline moved by at most 2.4bp and the 1-year variant by up to 21bp (September 2026). No yen sign and no 3-month sign changed; the euro 1-year "
               "pickup in July 2026 moved from +0.0002 to -0.0131 percentage points, a sign change around zero. The validation gate still passes. The gate "
               "medians before and after are in `checks.csv`, rows C17.")
E024_TEXT = ("The swap-tape cells in this folder (the 3-month and 1-year overnight-index-swap and cross-currency medians) come from the ledger in data/swap_tape/, "
             "which derives them from DTCC Public Price Dissemination, CFTC cumulative interest-rate reports (https://pddata.dtcc.com), under THE_ASK.md E-024. "
             "E-024, in the principal's choice (a): script the DTCC public price dissemination files despite DTCC's website terms; the use is non-commercial; "
             "no raw DTCC file or row is committed or redistributed; only derived statistics (medians, quartiles, counts) are published, and they cite DTCC; "
             "requests are sequential and paced and carry the neutral project User-Agent; any technical refusal ends the run rather than being routed around. "
             "The ledger's monthly stage extends the same ruling to monthly medians at 10 or more prints. The raw files stay outside the repository, and this "
             "folder's script never reads them. Nothing here licenses anyone to use DTCC's data commercially.")

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


def add_months(d, k):
    """d plus k calendar months, clipped to the end of the month."""
    y, m0 = divmod(d.year * 12 + d.month - 1 + k, 12)
    m = m0 + 1
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def month_key(d):
    return "%04d-%02d" % (d.year, d.month)


def month_end(m):
    y, mm = int(m[:4]), int(m[5:7])
    return dt.date(y, mm, calendar.monthrange(y, mm)[1])


def months_between(a, b):
    out = []
    y, m = int(a[:4]), int(a[5:7])
    while "%04d-%02d" % (y, m) <= b:
        out.append("%04d-%02d" % (y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def median(xs):
    xs = list(xs)
    return statistics.median(xs) if xs else None


def assert_ua(ua=UA):
    if not M("ua_check_off"):
        if "@" in ua:
            raise Refused("the identification string contains an address")
        for var in ("SEC_UA", "CLAUDE_CODE_USER_EMAIL"):
            v = os.environ.get(var, "").strip()
            if v and (v in ua or ua in v):
                raise Refused("the identification string contains a configured contact value (not printed)")


assert_ua()


def decode_text(body):
    try:
        return body.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise DataError("not UTF-8 text")


def decode_mof(body):
    """MoF files are ASCII except for a Shift-JIS note line at the foot of the current-month file; decode as UTF-8, else as CP932."""
    try:
        return body.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            return body.decode("cp932")
        except UnicodeDecodeError:
            raise DataError("not UTF-8 or CP932 text")


# ------------------------------------------------------------------------------------------------------------------------
# the request table (R1, R3): the exact URLs, in fetch order
# ------------------------------------------------------------------------------------------------------------------------
def request_table(today):
    """The requests of the spec (section 2). today: a date; the NY Fed paths carry it."""
    td = today.isoformat()
    reqs = []
    for y in range(FIRST_TSY_YEAR, today.year + 1):
        reqs.append(dict(key="tsy%d" % y, host=TSY_HOST, target=fx.TSY_PATH.format(Y=y), file="tsy_%d.csv" % y, kind="tsy", arg=y,
                         immutable=y < today.year, ok=(200,)))
    reqs += [dict(key="jgb_all", host=MOF_HOST, target=JGB_ALL_PATH, file="mof_jgbcme_all.csv", kind="jgb_all", arg=None, immutable=False, ok=(200,)),
             dict(key="jgb_cur", host=MOF_HOST, target=JGB_CUR_PATH, file="mof_jgbcme.csv", kind="jgb_cur", arg=None, immutable=False, ok=(200,)),
             dict(key="yc", host=ECB_HOST, target=YC_PATH, file="ecb_yc.csv", kind="yc", arg=None, immutable=False, ok=(200,)),
             dict(key="sofr", host=NYF_HOST, target=SOFR_PATH.format(today=td), file="nyfed_sofr.csv", kind="sofr", arg=None, immutable=False, ok=(200,)),
             dict(key="effr", host=NYF_HOST, target=EFFR_PATH.format(today=td), file="nyfed_effr.csv", kind="effr", arg=None, immutable=False, ok=(200,)),
             dict(key="sofrai", host=NYF_HOST, target=SOFRAI_PATH.format(today=td), file="nyfed_sofrai.json", kind="sofrai", arg=None, immutable=False,
                  ok=(200,)),
             dict(key="est", host=ECB_HOST, target=EST_PATH, file="ecb_est.csv", kind="est", arg=None, immutable=False, ok=(200,)),
             dict(key="tona", host=BOJ_HOST, target=TONA_PATH, file="boj_tona.csv", kind="tona", arg=None, immutable=False, ok=(200,)),
             dict(key="dks_probe", host=DKS_HOST, target=DKS_PATH, file="dks_probe.bin", kind="dks_probe", arg=None, immutable=False, ok=(206,),
                  extra={"Range": "bytes=0-65535"}, every_run=True),
             dict(key="bbk", host=BBK_HOST, target=BBK_PATH, file="bbk_svensson.csv", kind="bbk", arg=None, immutable=False, ok=(200,))]
    return reqs


def allowed_targets(today):
    """Every (host, target) that a run on `today` may request, the TONA continuation pages and the DKS full body included."""
    s = {(r["host"], r["target"]) for r in request_table(today)}
    return s


def check_url(url, today):
    """Only the exact requests of the table, over https, on the allowlisted hosts. Returns (host, target)."""
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    target = p.path + ("?" + p.query if p.query else "")
    if M("allow_fred"):
        return host, target
    if p.scheme != "https" or p.username or p.password or p.port not in (None, 443) or p.fragment:
        raise Refused("only plain https URLs are allowed")
    if host not in HOST_ALLOW:
        raise Refused("host %s is not on the allowlist" % host)
    boj_page = host == BOJ_HOST and re.fullmatch(re.escape(TONA_PATH) + r"&startPosition=\d+", target) is not None
    if (host, target) not in allowed_targets(today) and not boj_page:
        raise Refused("that path is not one of the requests of the spec")
    return host, target


def check_cache(cache, root=ROOT, out_dir=None):
    """The cache may be outside the repository, or inside it only where git ignores it (never in the committed output folder)."""
    real = os.path.realpath(os.path.expanduser(cache))
    rroot = os.path.realpath(root)
    if M("cache_check_off"):
        return real
    if real == rroot or real.startswith(rroot + os.sep):
        outd = os.path.realpath(out_dir or os.path.join(root, "data", "hedged_ust_yield"))
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
# parsers (every one also serves as the content test of its downloaded file) -- G16
# ------------------------------------------------------------------------------------------------------------------------
DATE_US = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
DATE_JP = re.compile(r"(\d{4})/(\d{1,2})/(\d{1,2})")
MONTHS3 = {m: i + 1 for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"))}


def parse_tsy10(text, year=None, min_rows=1):
    """The 10-year par yield BY HEADER NAME ('10 Yr'); the 2025-26 files carry an extra '1.5 Month' column, so positions differ. -> {date: float}"""
    rows = list(csv.reader(io.StringIO(text.lstrip("﻿"))))
    if not rows:
        raise DataError("empty Treasury file")
    hdr = [h.strip() for h in rows[0]]
    for need in ("Date", "10 Yr"):
        if need not in hdr:
            raise DataError("Treasury header lacks %r" % need)
    i10 = 11 if M("positional_treasury") else hdr.index("10 Yr")      # the mutant: the pre-2025 position, wrong once '1.5 Month' exists
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
        v = r[i10].strip() if i10 < len(r) else ""
        if v in ("", "N/A"):
            continue
        if d in out:
            raise DataError("Treasury duplicate date %s" % d)
        out[d] = float(v)
    if len(out) < min_rows:
        raise DataError("Treasury file has %d usable rows (need %d)" % (len(out), min_rows))
    return out


def parse_mof10(text, min_rows=1):
    """MoF constant-maturity file: a 'Date,1Y,...' header line, unpadded Y/M/D dates, '-' = missing, footer note lines skipped. -> {date: 10Y or None}"""
    lines = text.lstrip("﻿").splitlines()
    hi = next((i for i, ln in enumerate(lines[:10]) if ln.split(",")[0].strip() == "Date"), None)
    if hi is None:
        raise DataError("MoF yield file: no 'Date' header line")
    hdr = [h.strip() for h in lines[hi].split(",")]
    if "10Y" not in hdr:
        raise DataError("MoF yield file lacks 10Y")
    i10 = hdr.index("10Y")
    out = {}
    for ln in lines[hi + 1:]:
        cells = ln.split(",")
        c0 = cells[0].strip()
        if not c0:
            continue
        m = DATE_JP.fullmatch(c0)
        if not m:
            if M("mof_footer_as_data"):
                raise DataError("MoF footer line read as data: %r" % c0[:30])
            if c0[0].isdigit():
                raise DataError("MoF yield date %r" % c0)
            continue                                       # a footer note line
        d = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        s = cells[i10].strip() if i10 < len(cells) else ""
        if d in out:
            raise DataError("MoF duplicate date %s" % d)
        if s == "-" or s == "":
            out[d] = None
        else:
            try:
                out[d] = float(s)
            except ValueError:
                raise DataError("MoF yield value %r" % s)
    if len(out) < min_rows:
        raise DataError("MoF yield file has %d rows (need %d)" % (len(out), min_rows))
    return out


def merge_mof10(a, b):
    """The history file and the current-month file overlap and must agree on every shared date."""
    out = dict(a)
    for d, v in b.items():
        if d in out and out[d] != v:
            raise DataError("MoF files disagree on %s: %r against %r" % (d, out[d], v))
        out.setdefault(d, v)
    return out


def parse_nyfed(text, rate_type, min_rows=1):
    """NY Fed reference-rate search.csv: columns by header name ('Effective Date', 'Rate Type', 'Rate (%)'), newest row first, MM/DD/YYYY. -> {date: float}"""
    rows = list(csv.reader(io.StringIO(text.lstrip("﻿"))))
    if not rows:
        raise DataError("empty NY Fed file")
    hdr = [h.strip() for h in rows[0]]
    for need in ("Effective Date", "Rate Type", "Rate (%)"):
        if need not in hdr:
            raise DataError("NY Fed header lacks %r" % need)
    idate, itype, irate = hdr.index("Effective Date"), hdr.index("Rate Type"), hdr.index("Rate (%)")
    if M("nyfed_positional"):
        irate = 3                                           # the mutant: the first percentile column
    dates, vals = [], []
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        if r[itype].strip() != rate_type:
            raise DataError("NY Fed rate type %r (want %s)" % (r[itype], rate_type))
        m = DATE_US.fullmatch(r[idate].strip())
        if not m:
            raise DataError("NY Fed date %r" % r[idate])
        d = dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        if r[irate].strip() == "":
            continue
        dates.append(d)
        vals.append(float(r[irate]))
    if M("nyfed_oldest_first"):
        dates = sorted(dates)                               # the mutant: the file read as if the oldest row came first
    out = {}
    for d, v in zip(dates, vals):
        if d in out:
            raise DataError("NY Fed duplicate date %s" % d)
        out[d] = v
    if len(out) < min_rows:
        raise DataError("NY Fed file has %d rows (need %d)" % (len(out), min_rows))
    return out


def parse_sofrai(text, min_rows=1):
    """NY Fed SOFR Index JSON. -> {date: index}"""
    try:
        js = json.loads(text.lstrip("﻿"))
        rr = js["refRates"]
    except (ValueError, KeyError, TypeError):
        raise DataError("SOFR Index JSON")
    out = {}
    for r in rr:
        if r.get("type") != "SOFRAI" or "index" not in r:
            raise DataError("SOFR Index row %r" % (r,))
        d = dt.date.fromisoformat(r["effectiveDate"])
        if d in out:
            raise DataError("SOFR Index duplicate date %s" % d)
        out[d] = float(r["index"])
    if len(out) < min_rows:
        raise DataError("SOFR Index file has %d rows (need %d)" % (len(out), min_rows))
    return out


def parse_est(text, min_rows=1):
    """ECB euro short-term rate: the volume-weighted trimmed mean (.WT, percent) and the compounded index (.CI, 1 Oct 2019 = 100). -> (rate, index)"""
    rd = csv.reader(io.StringIO(text.lstrip("﻿")))
    hdr = next(rd, None)
    if not hdr:
        raise DataError("empty ECB EST file")
    try:
        ik, it, id_, iv = hdr.index("KEY"), hdr.index("DATA_TYPE_EST"), hdr.index("TIME_PERIOD"), hdr.index("OBS_VALUE")
    except ValueError:
        raise DataError("ECB EST header")
    rate, idx = {}, {}
    for r in rd:
        if not r or r[iv] == "":
            continue
        if not r[ik].startswith("EST.B.EU000A2"):
            raise DataError("ECB EST series key %r" % r[ik])
        d = dt.date.fromisoformat(r[id_])
        kind = r[it]
        if kind == "WT" and r[ik] == "EST.B.EU000A2X2A25.WT":
            tgt = rate
        elif kind == "CI" and r[ik] == "EST.B.EU000A2QQF08.CI":
            tgt = rate if M("est_ci_as_rate") else idx      # the mutant: the index read as a rate
        else:
            raise DataError("ECB EST series %r" % r[ik])
        if d in tgt:
            raise DataError("ECB EST duplicate %s %s" % (kind, d))
        tgt[d] = float(r[iv])
    if len(rate) < min_rows or len(idx) < min_rows:
        raise DataError("ECB EST file has %d rates and %d index values (need %d)" % (len(rate), len(idx), min_rows))
    return rate, idx


def parse_tona(text, min_rows=1):
    """Bank of Japan time-series API, CSV, call rate uncollateralised overnight (TONA), db FM01 code STRDCLUCON. A header block (STATUS, MESSAGEID, ...,
    NEXTPOSITION) comes first; the series name is a quoted field that contains a comma; 'null' is a non-business day. -> ({date: float}, nextposition)"""
    lines = text.lstrip("﻿").splitlines()
    nextpos = ""
    status = None
    start = None
    i_date = i_val = None
    for i, ln in enumerate(lines):
        if ln.startswith("SERIES_CODE,"):
            start = i + 1
            cols = ln.split(",")
            i_date, i_val = cols.index("SURVEY_DATES"), cols.index("VALUES")
            break
        c = next(csv.reader([ln]), [])
        if len(c) >= 2 and c[0] == "STATUS":
            status = c[1]
        if c and c[0] == "NEXTPOSITION":
            nextpos = c[1] if len(c) > 1 else ""
    if M("boj_header_as_data"):
        start = 0                                           # the mutant: the header block is read as data rows
    if start is None or (status != "200" and not M("boj_header_as_data")):
        raise DataError("BoJ API header block (STATUS %r)" % status)
    out = {}
    for ln in lines[start:]:
        if not ln.strip():
            continue
        c = ln.split(",") if M("boj_naive_split") else next(csv.reader([ln]))      # the mutant splits the quoted name on its comma
        if M("boj_header_as_data"):
            i_date, i_val = -2, -1
        d_s, v_s = (c[i_date].strip(), c[i_val].strip()) if len(c) > max(i_date, i_val) else ("", "")
        if not re.fullmatch(r"\d{8}", d_s):
            raise DataError("BoJ date %r" % d_s[:20])
        if c[0] != "STRDCLUCON" and not M("boj_naive_split"):
            raise DataError("BoJ series code %r" % c[0])
        d = dt.date(int(d_s[:4]), int(d_s[4:6]), int(d_s[6:]))
        if v_s == "null":
            if M("boj_null_as_zero"):
                out[d] = 0.0                                # the mutant: a non-business day becomes a 0% rate
            continue
        try:
            out[d] = float(v_s)
        except ValueError:
            raise DataError("BoJ value %r" % v_s[:20])
    if len(out) < min_rows:
        raise DataError("BoJ file has %d values (need %d)" % (len(out), min_rows))
    return out, nextpos


def parse_dks_date(s):
    """'08feb2007' -> 2007-02-08."""
    m = re.fullmatch(r"(\d{2})([a-z]{3})(\d{4})", s.strip().lower())
    if not m or m.group(2) not in MONTHS3:
        raise DataError("DKS date %r" % s)
    if M("dks_date_misparse"):
        return dt.date(int(m.group(3)), int(m.group(1)), 1)   # the mutant: the day read as the month
    return dt.date(int(m.group(3)), MONTHS3[m.group(2)], int(m.group(1)))


def parse_dks_rows(text, min_rows=1):
    """The extracted DKS rows (JPY and EUR, 3m and 1y). -> {(currency, tenor): {date: dict(rho, rho_ibor, rho_sofr)}}"""
    rd = csv.reader(io.StringIO(text.lstrip("﻿")))
    hdr = next(rd, None)
    if not hdr or ",".join(hdr) != DKS_HEADER:
        raise DataError("DKS header")
    ix = {c: i for i, c in enumerate(hdr)}
    out = {}
    n = 0
    for r in rd:
        if not r:
            continue
        if len(r) != len(hdr):
            raise DataError("DKS row width")
        key = (r[ix["currency"]], r[ix["tenor"]])
        rec = {}
        for c in ("rho", "rho_ibor", "rho_sofr"):
            rec[c] = float(r[ix[c]]) if r[ix[c]] not in ("", "NA") else None
        d = parse_dks_date(r[ix["date"]])
        slot = out.setdefault(key, {})
        if d in slot:
            raise DataError("DKS duplicate %s %s" % (key, d))
        slot[d] = rec
        n += 1
    if n < min_rows:
        raise DataError("DKS extract has %d rows (need %d)" % (n, min_rows))
    return out


def extract_dks(body_text):
    """From the full DKS panel keep the currency in (JPY, EUR) and tenor in (3m, 1y) rows. -> (extract text, n rows)"""
    rd = csv.reader(io.StringIO(body_text))
    hdr = next(rd, None)
    if not hdr or ",".join(hdr) != DKS_HEADER:
        raise DataError("DKS header")
    ic, it = hdr.index("currency"), hdr.index("tenor")
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(hdr)
    n = 0
    for r in rd:
        if r and r[ic] in ("JPY", "EUR") and r[it] in ("3m", "1y"):
            w.writerow(r)
            n += 1
    return out.getvalue(), n


def dks_probe_problem(status, body, headers):
    """None if the ranged probe looks like the DKS file: 206, the CSV header first, a Content-Range with a total size."""
    if status != 206:
        return "status %s, not 206" % status
    if body is None or not body.startswith(DKS_HEADER.encode()):
        return "206 but the body does not start with the DKS header"
    if not re.fullmatch(r"bytes 0-65535/\d+", headers.get("content-range", "")):
        return "206 without the expected Content-Range"
    return None


def body_problem(kind, arg, body, today=None):
    """The content test of a downloaded body: None if it is the expected file, else the reason."""
    try:
        if kind == "tsy":
            parse_tsy10(decode_text(body), year=arg, min_rows=100 if (today is None or arg < today.year) else 20)
        elif kind == "jgb_all":
            parse_mof10(decode_mof(body), min_rows=12000)
        elif kind == "jgb_cur":
            parse_mof10(decode_mof(body), min_rows=5)
        elif kind == "yc":
            yc = fx.parse_ecb_yc(decode_text(body), min_dates=1500)
            if sum(1 for p in yc.values() if all(k in p for k in fx.PARAM_KEYS)) < 1500:
                raise DataError("too few dates with a full parameter set")
        elif kind == "sofr":
            parse_nyfed(decode_text(body), "SOFR", min_rows=1500)
        elif kind == "effr":
            parse_nyfed(decode_text(body), "EFFR", min_rows=1500)
        elif kind == "sofrai":
            parse_sofrai(decode_text(body), min_rows=1000)
        elif kind == "est":
            parse_est(decode_text(body), min_rows=1500)
        elif kind == "tona":
            parse_tona(decode_text(body), min_rows=1000)
        elif kind == "bbk":
            fx.parse_bundesbank(decode_text(body), min_rows=1500)
        elif kind == "dks_full":
            if not body.startswith(DKS_HEADER.encode()):
                raise DataError("DKS header")
            if len(body) < 50_000_000:
                raise DataError("DKS body too small")
        else:
            return "unknown file kind"
    except (DataError, ValueError, UnicodeDecodeError, KeyError) as e:
        return "%s: %s" % (type(e).__name__, e)
    return None


# ------------------------------------------------------------------------------------------------------------------------
# the fetch log and fetching: the only network code
# ------------------------------------------------------------------------------------------------------------------------
LOG_COLS = ["utc_time", "host", "path", "status", "bytes", "sha256"]
PIN_COLS = ["source", "series", "pin_date", "value", "unit"]
CHECK_COLS = ["check_id", "description", "expected", "observed", "status"]


def read_csv_rows(path):
    """(header, rows) of a csv with comment lines (# ...) skipped; ([], []) if absent."""
    if not os.path.exists(path):
        return [], []
    with open(path, encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh.read().splitlines(True) if not ln.startswith("#")]
    rd = list(csv.reader(io.StringIO("".join(lines))))
    return (rd[0], rd[1:]) if rd else ([], [])


PUBLISHERS = (("U.S. Department of the Treasury (home.treasury.gov)", TSY_HOST), ("Ministry of Finance Japan (www.mof.go.jp)", MOF_HOST),
              ("European Central Bank (data-api.ecb.europa.eu)", ECB_HOST), ("Federal Reserve Bank of New York (markets.newyorkfed.org)", NYF_HOST),
              ("Bank of Japan (www.stat-search.boj.or.jp)", BOJ_HOST), ("Du, Keerati and Schreger panel (jschreger.s3.us-east-2.amazonaws.com)", DKS_HOST),
              ("Deutsche Bundesbank (api.statistiken.bundesbank.de)", BBK_HOST))


def retrieval_dates(log_rows, hosts):
    return sorted({r[0][:10] for r in log_rows if r[1] in hosts and r[3] in ("200", "206") and r[4]})


def source_line(log_rows, hosts, what):
    parts = []
    for name, host in PUBLISHERS:
        if host in hosts:
            ds = retrieval_dates(log_rows, {host})
            parts.append("%s retrieved %s" % (name, ", ".join(ds) if ds else "(no logged retrieval)"))
    return "# source: " + "; ".join(parts) + "; " + what


def real_opener(host, target, headers, timeout, cap):
    """GET https://host/target. Returns (status, body, response headers); body is None when it exceeds `cap`. No redirect is followed (a 3xx comes back as
    a status and latches), no cookies, the only verb is GET. Socket-level faults raise SocketFault."""
    conn = http.client.HTTPSConnection(host, timeout=timeout)
    try:
        conn.request("GET", target, headers=dict(headers))
        resp = conn.getresponse()
        status = resp.status
        hdrs = {k.lower(): v for k, v in resp.getheaders()}
        if status not in (200, 206):
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


class Fetcher:
    """All requests go through here. Injectable opener, clock, sleeper and STOP path make it testable without a network."""

    def __init__(self, cache, out_dir, sleep=MIN_SLEEP, max_requests=MAX_REQUESTS, opener=real_opener, wall=time.time, mono=time.monotonic,
                 sleeper=time.sleep, stop_path=STOP_PATH, now_utc=None, root=ROOT):
        if sleep < 2.0 and not M("no_pacing"):
            raise Refused("--sleep must be at least 2 seconds")
        if (max_requests > MAX_REQUESTS and not M("no_request_cap")) or max_requests < 1:
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
        self.warnings = []

    def today(self):
        return self.now_utc().date()

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
        text = render_csv("fetch_log.csv", rows, source_line(rows, HOST_ALLOW, "request log of bin/hedged_ust_yield.py fetch (one row per request)"))
        write_text(self.log_path, text)

    def _latch(self, reason):
        os.makedirs(os.path.dirname(self.stop_path), exist_ok=True)
        with open(self.stop_path, "w", encoding="utf-8") as fh:
            fh.write("%s UTC  %s\n" % (self.now_utc().strftime("%Y-%m-%dT%H:%M:%S"), reason))
        raise Latched(reason)

    def _get(self, host, target, extra=None, cap=BODY_CAP):
        check_url("https://" + host + target, self.today())
        if self.requests >= self.max_requests:
            raise MaxRequests("--max-requests reached (%d)" % self.max_requests)
        self._pace()
        started = self.wall()
        self._last_mono = self.mono()
        os.makedirs(self.cache, exist_ok=True)
        with open(self._last_file, "w", encoding="utf-8") as fh:
            fh.write("%r\n" % started)
        self.requests += 1
        hdrs = dict(HEADERS)
        hdrs.update(extra or {})
        try:
            status, body, rh = self.opener(host, target, hdrs, TIMEOUT, cap)
        except SocketFault as e:
            self._log(started, host, target, "socket_fault", "", "")
            if M("latch_on_socket"):
                self._latch("socket fault (%s) for %s" % (e, target))
            raise
        return status, body, rh, started

    def _done_today(self, host, target):
        today = self.now_utc().strftime("%Y-%m-%d")
        _, rows = read_csv_rows(self.log_path)
        return any(r[1] == host and r[2] == target and r[3] == "200" and r[4] and r[0][:10] == today for r in rows)

    def _refuse(self, status, host, target, started):
        self._log(started, host, target, status, "", "")
        if status // 100 == 3:
            if not M("no_latch_redirect"):
                self._latch("HTTP %d (a redirect, not followed) for %s" % (status, target[:80]))
        elif not M("no_latch_non200"):
            self._latch("HTTP %d for %s" % (status, target[:80]))
        return "refused_unlatched"

    def fetch_one(self, req, dks_full=False):
        """Returns an outcome word; raises Latched / SocketFault / MaxRequests / Refused."""
        path = os.path.join(self.cache, req["file"])
        every = req.get("every_run", False)
        if os.path.exists(path) and not every and (req["immutable"] or self._done_today(req["host"], req["target"])):
            return "cached"
        self.check_stop()
        status, body, rh, started = self._get(req["host"], req["target"], req.get("extra"))
        if status not in req["ok"]:
            return self._refuse(status, req["host"], req["target"], started)
        if req["kind"] == "dks_probe":
            problem = "body larger than the cap" if body is None else dks_probe_problem(status, body, rh)
        else:
            problem = "body larger than the cap" if body is None else body_problem(req["kind"], req["arg"], body, self.today())
        self._log(started, req["host"], req["target"], status, len(body or b""), sha256_of(body or b""))
        if problem:
            if not M("no_latch_bad_body"):
                self._latch("%s but not the expected file (%s) for %s" % (status, problem, req["target"][:80]))
            return "refused_unlatched"
        os.makedirs(self.cache, exist_ok=True)
        if req["kind"] == "dks_probe":
            probe = dict(etag=rh.get("etag", "").strip('"'), last_modified=rh.get("last-modified", ""), content_range=rh.get("content-range", ""),
                         size=int(rh["content-range"].split("/")[1]), status=status, fetched=self._stamp(started)[:10])
            write_text(os.path.join(self.cache, "dks_probe.json"), json.dumps(probe, indent=1, sort_keys=True) + "\n")
            if probe["etag"] != DKS_ETAG_OBSERVED or probe["size"] != DKS_SIZE_OBSERVED:
                self.warnings.append("DKS probe: ETag %s / size %d differ from the observed %s / %d (a new vintage); nothing latched"
                                     % (probe["etag"], probe["size"], DKS_ETAG_OBSERVED, DKS_SIZE_OBSERVED))
            need_full = dks_full or not os.path.exists(os.path.join(self.cache, "dks_3m_1y.csv"))
            if need_full:
                self.fetch_dks_full()
            return "saved"
        if req["kind"] == "tona":
            body = self.tona_pages(req, body)
        with open(path + ".part", "wb") as fh:
            fh.write(body)
        os.replace(path + ".part", path)
        return "saved"

    def tona_pages(self, req, body):
        """A non-empty NEXTPOSITION means another page (at most TONA_PAGES_MAX pages); the pages are merged into one file."""
        txt = decode_text(body)
        _, nxt = parse_tona(txt, min_rows=1)
        pages = 1
        lines = txt.splitlines()
        while nxt:
            if pages >= TONA_PAGES_MAX:
                self._latch("BoJ API wants more than %d pages" % TONA_PAGES_MAX)
            target = TONA_PATH + "&startPosition=%s" % nxt
            status, b2, rh, started = self._get(BOJ_HOST, target)
            if status != 200:
                return self._refuse(status, BOJ_HOST, target, started)
            problem = "body larger than the cap" if b2 is None else body_problem("tona", None, b2)
            self._log(started, BOJ_HOST, target, status, len(b2 or b""), sha256_of(b2 or b""))
            if problem:
                self._latch("200 but not the expected file (%s) for %s" % (problem, target[:80]))
            t2 = decode_text(b2)
            _, nxt = parse_tona(t2, min_rows=1)
            start = next(i for i, ln in enumerate(t2.splitlines()) if ln.startswith("SERIES_CODE,")) + 1
            lines += t2.splitlines()[start:]
            pages += 1
        return ("\n".join(lines) + "\n").encode("utf-8")

    def fetch_dks_full(self):
        """The 118 MB panel: once, into memory, the JPY and EUR 3m and 1y rows kept, the body deleted (never written), its sha256 logged."""
        status, body, rh, started = self._get(DKS_HOST, DKS_PATH, None, cap=DKS_CAP)
        if status != 200:
            return self._refuse(status, DKS_HOST, DKS_PATH, started)
        problem = "body larger than the cap" if body is None else body_problem("dks_full", None, body)
        self._log(started, DKS_HOST, DKS_PATH, status, len(body or b""), sha256_of(body or b""))
        if problem:
            self._latch("200 but not the expected file (%s) for %s" % (problem, DKS_PATH))
        text, n = extract_dks(decode_text(body))
        if n < 1000:
            self._latch("the DKS extract has only %d rows" % n)
        del body
        write_text(os.path.join(self.cache, "dks_3m_1y.csv"), text)
        return "saved"

    def run(self, reqs, say=print, dks_full=False):
        saved = 0
        for req in reqs:
            out = self.fetch_one(req, dks_full=dks_full)
            saved += out == "saved"
            say("%-22s %s" % (req["file"], out))
        for w in self.warnings:
            say("WARN " + w)
        return saved


# ------------------------------------------------------------------------------------------------------------------------
# writing outputs: exact column allowlists, source lines, no causal wording (G13, G14)
# ------------------------------------------------------------------------------------------------------------------------
PANEL_COLS = ["date", "pair", "tokyo_or_target_date", "ust10", "home10", "r_us", "r_us_rt", "r_us_effr", "r_home", "r_home_rt", "D_days", "h_A_rt",
              "h_A_hist", "h_A_effr", "h_B", "gap_A_rt", "gap_A_hist", "gap_B", "h_dks", "qe_turn_early", "drop_reason"]
MONTHLY_COLS = ["month", "pair", "variant", "role", "n_days", "partial", "qe_turn_early", "ust10_pct", "home10_pct", "rate_gap_term_pp", "basis_term_pp",
                "hedged_carry_pct", "pickup_pp", "form_gap_bp", "basis_tenor", "hedge_days_mean", "n_ois_us", "n_ois_home", "n_basis"]
YEN_COLS = ["period", "variant", "statistic", "value", "credit"]
SUMMARY_COLS = ["run_label", "L", "question", "pair", "variant", "statistic", "value", "notable"]
REF_COLS = ["ref_id", "source", "ref_date", "pair", "form", "tenor", "published", "rounding_bp", "build_value", "gap_bp", "tolerance", "status", "note"]
# The allowlists exactly as the spec prints them, typed separately from the constants above so that the selftest compares two independent copies
# and a hash of them. G13 fails if ALLOW or the written headers drift from these.
SPEC_ALLOW = {
    "daily_panel.csv": "date, pair, tokyo_or_target_date, ust10, home10, r_us, r_us_rt, r_us_effr, r_home, r_home_rt, D_days, h_A_rt, h_A_hist, h_A_effr, h_B, gap_A_rt, gap_A_hist, gap_B, h_dks, qe_turn_early, drop_reason",
    "monthly.csv": "month, pair, variant, role, n_days, partial, qe_turn_early, ust10_pct, home10_pct, rate_gap_term_pp, basis_term_pp, hedged_carry_pct, pickup_pp, form_gap_bp, basis_tenor, hedge_days_mean, n_ois_us, n_ois_home, n_basis",
    "yen_summary.csv": "period, variant, statistic, value, credit",
    "summary.csv": "run_label, L, question, pair, variant, statistic, value, notable",
    "references.csv": "ref_id, source, ref_date, pair, form, tenor, published, rounding_bp, build_value, gap_bp, tolerance, status, note",
    "checks.csv": "check_id, description, expected, observed, status",
    "pins.csv": "source, series, pin_date, value, unit",
    "fetch_log.csv": "utc_time, host, path, status, bytes, sha256",
}
SPEC_ALLOW_SHA256 = ""      # set below, after ALLOW exists
ALLOW = {"daily_panel.csv": PANEL_COLS, "monthly.csv": MONTHLY_COLS, "yen_summary.csv": YEN_COLS, "summary.csv": SUMMARY_COLS, "references.csv": REF_COLS,
         "checks.csv": CHECK_COLS, "pins.csv": PIN_COLS, "fetch_log.csv": LOG_COLS}
COMMITTED = ("monthly.csv", "yen_summary.csv", "summary.csv", "references.csv", "checks.csv", "pins.csv", "fetch_log.csv")

# G14: the wording the spec bans (R5). The required sentence of section 0 is the one exemption.
CAUSAL_RX = re.compile(fx.CAUSAL_RX.pattern[:-3] + r"|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b", re.I) if fx.CAUSAL_RX.pattern.endswith(r")\b") else None
if CAUSAL_RX is None:
    raise SystemExit("fx_rate_gap.CAUSAL_RX changed shape; update CAUSAL_RX here")


def causal_hits(text):
    text = text.replace(REQUIRED_SENTENCE, "")
    rx = fx.CAUSAL_RX if M("causal_rx_narrow") else CAUSAL_RX      # the mutant: fx_rate_gap's shorter list, without the spec's extra words
    return sorted({re.sub(r"\s+", " ", m.group(0).lower()) for m in rx.finditer(text)})


def allowlist(name):
    cols = list(ALLOW[name])
    if M("allow_drift") and name == "monthly.csv":
        cols[cols.index("pickup_pp")] = "share"
    return cols


def allow_digest():
    return sha256_of("\n".join("%s:%s" % (n, SPEC_ALLOW[n].replace(" ", "")) for n in sorted(SPEC_ALLOW)).encode())


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


def guard_text(name, text):
    hits = causal_hits(text)
    if hits and not M("causal_guard_off"):
        raise DataError("%s: causal wording %s" % (name, hits))
    if os.path.expanduser("~") != "~" and os.path.expanduser("~") in text:
        raise DataError("%s: an absolute home path would be published" % name)


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


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


SPEC_ALLOW_SHA256 = allow_digest()


# ------------------------------------------------------------------------------------------------------------------------
# arithmetic (spec 3.2-3.4): the bond-basis form H, the plain-subtraction form P, spot (A) and realised (B) diagnostics
# ------------------------------------------------------------------------------------------------------------------------
def day_basis(leg):
    """B in the day count of each leg: SOFR and EFFR ACT/360; TONA ACT/365; the euro short-term rate ACT/360."""
    if leg == "us":
        return 365.0 if M("sofr_365") else 360.0
    if leg == "yen":
        return 360.0 if M("tona_360") else 365.0
    return 360.0


def hedge_days(d, k):
    """Days from d to the same day k months later, clipped to the month end (3.3)."""
    return (add_months(d, k) - d).days


def g_simple(o, D, leg):
    """A single-payment swap pays simple interest: G = 1 + o D / (100 B)."""
    if M("d_quarter"):
        return 1.0 + o / 400.0                  # the mutant: a quarter of a year in place of D / B
    return 1.0 + o * D / (100.0 * day_basis(leg))


def g_spot(r, D, leg):
    """The overnight rate held for D days: G = (1 + r / (100 B)) ^ D (3.4 A)."""
    return (1.0 + r / (100.0 * day_basis(leg))) ** D


def forward_h(y_us, G_us, G_home, D, b, leg_home):
    """Bond-basis form (3.2). R = (G_home + (b/10000) D / B_home) / G_us; c = 100 ln(R) 365 / D; y_c = 200 ln(1 + y_us/200);
    H = 200 (exp((y_c + c)/200) - 1). -> (H, h0) with h0 = H at b = 0."""
    Bh = day_basis(leg_home)
    y_c = 200.0 * math.log(1.0 + y_us / 200.0)

    def H_of(bb):
        adj = (bb / 10000.0) * D / Bh
        if M("basis_sign"):
            adj = -adj                          # the mutant: the sign of the basis flipped
        num, den = G_home + adj, G_us
        if M("basis_usd"):
            num, den = G_home, G_us + (bb / 10000.0) * D / day_basis("us")   # the mutant: the basis added to the USD leg
        c = 100.0 * math.log(num / den) * 365.0 / D
        return 200.0 * (math.exp((y_c + c) / 200.0) - 1.0)
    return H_of(b), H_of(0.0)


def plain_p(y_us, o_us, o_home, b):
    """Plain subtraction (3.2): rate_gap_term = -(o_us - o_home) as quoted, basis_term = b/100. -> (P, rate_gap_term, basis_term)"""
    if M("swap_rates"):
        o_us, o_home = o_home, o_us
    gap = -(o_us - o_home)
    if M("p_daycount"):
        gap = -(o_us * 365.0 / 360.0 - o_home)  # the mutant: a day-count change inside the plain form
    basis = b / 100.0
    return y_us + gap + basis, gap, basis


def headline(y_us, o_us, o_home, b, D, pair):
    """The locked-forward headline for one month: both forms. -> dict"""
    if M("swap_rates"):
        o_us, o_home = o_home, o_us             # the mutant: home and US rates swapped (undone for P, which swaps by itself)
    Dh = 90 if M("d_fixed90") else D
    G_us, G_home = g_simple(o_us, Dh, "us"), g_simple(o_home, Dh, pair)
    H, h0 = forward_h(y_us, G_us, G_home, Dh, b, pair)
    if M("swap_rates"):
        o_us, o_home = o_home, o_us
    P, pgap, pbasis = plain_p(y_us, o_us, o_home, b)
    if M("h_as_p"):
        H = P                                   # the mutant: H computed as P
    gap_term = h0 - y_us
    basis_term = b / 100.0 if M("basis_inside") else H - h0
    if M("h_as_p"):
        gap_term, basis_term = pgap, pbasis
    return dict(H=H, h0=h0, rate_gap_term=gap_term, basis_term=basis_term, P=P, p_gap=pgap, p_basis=pbasis, form_gap_bp=100.0 * (H - P), D=Dh)


def spot_h(y_us, r_us, r_home, D, pair):
    """Diagnostic A: the overnight rates held over the hedge window, no basis (3.4). -> (h, rate_gap_term)"""
    if M("swap_rates"):
        r_us, r_home = r_home, r_us
    G_us, G_home = g_spot(r_us, D, "us"), g_spot(r_home, D, pair)
    H, h0 = forward_h(y_us, G_us, G_home, D, 0.0, pair)
    return H, H - y_us


def rho_signed(rho, sign=None):
    """DKS rho in the 3.2 convention (negative = a cost of hedging). Read on 19 Oct 2026: JPY 3m rho is -2.75 on 3 Jun 2019 (SOFR 2.3, TONA -0.05) and
    -5.55 on 15 Mar 2024, so the file is already in the carry convention and the sign is +1 (O-4)."""
    s = DKS_SIGN if sign is None else sign
    return (-1.0 if M("dks_sign_flip") else 1.0) * s * rho


DKS_SIGN = 1.0


# ------------------------------------------------------------------------------------------------------------------------
# rate series, windows and closures
# ------------------------------------------------------------------------------------------------------------------------
class RateSeries:
    """A dated overnight-rate series: latest on or before a date, latest strictly before, and the compounded window (3.4 B)."""

    def __init__(self, values):
        self.v = {d: x for d, x in values.items() if x is not None}
        self.dates = sorted(self.v)

    def leq(self, d):
        i = bisect.bisect_right(self.dates, d)
        return self.dates[i - 1] if i else None

    def lt(self, d):
        i = bisect.bisect_left(self.dates, d)
        return self.dates[i - 1] if i else None

    def geq(self, d):
        i = bisect.bisect_left(self.dates, d)
        return self.dates[i] if i < len(self.dates) else None

    def compound(self, d, e, B):
        """G = prod (1 + r_i n_i / (100 B)) over the rate dates i whose accrual meets [d, e); n_i runs to the next business day and is CLIPPED at e (and at d on
        the left). The ARRC / ISDA convention: a weekend is one period at Friday's rate, not compounded daily. None unless a rate dated on or after e exists
        (the window is covered) -- and unless a rate dated on or before d exists."""
        dates = self.dates
        if not dates:
            return None
        if M("window_backward"):
            d, e = d - (e - d), d                # the mutant: a window that looks backward
        if dates[-1] < e and not M("window_partial_ok"):
            return None
        i = bisect.bisect_right(dates, d) - 1
        if i < 0:
            return None
        G, S = 1.0, 0.0
        last = (lambda x: x <= e) if M("window_includes_end") else (lambda x: x < e)
        while i < len(dates) and last(dates[i]):
            s = max(dates[i], d)
            nxt = dates[i + 1] if i + 1 < len(dates) else None
            end = e if nxt is None else min(nxt, e)
            if M("window_includes_end") and dates[i] == e:
                end = e + dt.timedelta(days=1)
            n = (end - s).days
            if M("no_clip") and nxt is not None:
                n = (nxt - dates[i]).days
            r = self.v[dates[i]]
            if M("weekend_daily"):
                G *= (1.0 + r / (100.0 * B)) ** n
            elif M("simple_sum"):
                S += r * n / (100.0 * B)
            else:
                G *= 1.0 + r * n / (100.0 * B)
            i += 1
        return 1.0 + S if M("simple_sum") else G


def easter(y):
    """Gregorian Easter Sunday (the anonymous Gregorian algorithm)."""
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f_ = (b + 8) // 25
    g = (b - f_ + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mo = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    return dt.date(y, mo, day)


def closure_day(ccy, d):
    """KNOWN_CLOSURES (3.4): Tokyo New Year 31 Dec - 3 Jan and Golden Week; TARGET Easter, 1 May, 25-26 Dec. ccy in {'JPY', 'EUR'}; anything else has none."""
    if ccy == "JPY":
        return (d.month, d.day) in {(12, 31), (1, 1), (1, 2), (1, 3), (4, 29), (5, 3), (5, 4), (5, 5), (5, 6)}
    if ccy == "EUR":
        e = easter(d.year)
        return d in (e - dt.timedelta(days=2), e + dt.timedelta(days=1)) or (d.month, d.day) in {(5, 1), (12, 25), (12, 26), (1, 1)}
    return False


def unexplained_gaps(dates, ccy, limit=4):
    """Gaps of more than `limit` calendar days between consecutive published rates that KNOWN_CLOSURES do not explain."""
    out = []
    for a, b in zip(dates, dates[1:]):
        if (b - a).days > limit:
            between = [a + dt.timedelta(days=k) for k in range(1, (b - a).days)]
            if not all(x.weekday() >= 5 or closure_day(ccy, x) for x in between):
                out.append((a, b))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# inputs
# ------------------------------------------------------------------------------------------------------------------------
class Inputs:
    pass


def read_cache_bytes(cache, name):
    p = os.path.join(cache, name)
    if not os.path.exists(p):
        raise DataError("%s is missing from the cache; run `fetch` first" % name)
    with open(p, "rb") as fh:
        return fh.read()


def load_inputs(cache):
    inp = Inputs()
    tsy = {}
    for y in range(FIRST_TSY_YEAR, 2100):
        p = "tsy_%d.csv" % y
        if not os.path.exists(os.path.join(cache, p)):
            if y > FIRST_TSY_YEAR + 7:
                break
            raise DataError("%s is missing from the cache; run `fetch` first" % p)
        part = parse_tsy10(decode_text(read_cache_bytes(cache, p)), year=y)
        if set(part) & set(tsy):
            raise DataError("Treasury years overlap")
        tsy.update(part)
    inp.tsy = tsy
    ja = parse_mof10(decode_mof(read_cache_bytes(cache, "mof_jgbcme_all.csv")))
    jc = parse_mof10(decode_mof(read_cache_bytes(cache, "mof_jgbcme.csv")))
    inp.jgb_overlap = len(set(ja) & set(jc))
    inp.jgb_hist_end, inp.jgb_cur_start = max(ja), min(jc)
    try:
        inp.jgb, inp.jgb_err = merge_mof10(ja, jc), None
    except DataError as e:
        inp.jgb, inp.jgb_err = dict(ja), str(e)
    inp.yc_raw = fx.parse_ecb_yc(decode_text(read_cache_bytes(cache, "ecb_yc.csv")))
    clean, incomplete, quar = fx.usable_yc(inp.yc_raw)
    inp.yc_incomplete, inp.yc_quar = incomplete, quar
    inp.aaa = {d: fx.ea_semiannual(10, fx.params_of(p)) for d, p in clean.items()}
    inp.aaa_published = {d: p for d, p in clean.items()}
    inp.sofr = parse_nyfed(decode_text(read_cache_bytes(cache, "nyfed_sofr.csv")), "SOFR")
    inp.effr = parse_nyfed(decode_text(read_cache_bytes(cache, "nyfed_effr.csv")), "EFFR")
    inp.sofrai = parse_sofrai(decode_text(read_cache_bytes(cache, "nyfed_sofrai.json")))
    inp.estr, inp.estr_ci = parse_est(decode_text(read_cache_bytes(cache, "ecb_est.csv")))
    raw_tona = decode_text(read_cache_bytes(cache, "boj_tona.csv"))
    inp.tona, inp.tona_next = parse_tona(raw_tona)
    inp.tona_nulls = raw_tona.count(",null")
    inp.bbk = fx.parse_bundesbank(decode_text(read_cache_bytes(cache, "bbk_svensson.csv")))
    inp.dks = parse_dks_rows(decode_text(read_cache_bytes(cache, "dks_3m_1y.csv"))) if os.path.exists(os.path.join(cache, "dks_3m_1y.csv")) else {}
    pp = os.path.join(cache, "dks_probe.json")
    inp.dks_probe = json.loads(open(pp, encoding="utf-8").read()) if os.path.exists(pp) else None
    return inp


def read_fetch_log(out_dir):
    return read_csv_rows(os.path.join(out_dir, "fetch_log.csv"))[1]


# ------------------------------------------------------------------------------------------------------------------------
# the ledger's committed monthly output (the only place the tape cells come from)
# ------------------------------------------------------------------------------------------------------------------------
LEDGER_COLS = ["month", "series", "tenor", "n", "median", "q1", "q3", "iqr", "status", "n_days_with_trades"]
LEDGER_FLOOR = 10


def read_ledger(path):
    """-> {(month, series, tenor): dict(n, median, status)}. A row with a median at n < 10 is a hard error (spec 3.5): the floor is re-asserted on read."""
    header, rows = read_csv_rows(path)
    if header != LEDGER_COLS:
        raise DataError("ledger monthly file: unexpected header %r" % header)
    out = {}
    for r in rows:
        month, series, tenor, n_s, med = r[0], r[1], r[2], r[3], r[4]
        n = int(n_s)
        if med != "" and n < LEDGER_FLOOR and not M("ledger_floor_off"):
            raise DataError("ledger monthly file: %s %s %s has a median at n=%d (floor %d)" % (month, series, tenor, n, LEDGER_FLOOR))
        if (r[8] == "ok") != (med != ""):
            raise DataError("ledger monthly file: status %r does not match the median of %s %s %s" % (r[8], month, series, tenor))
        key = (month, series, tenor)
        if key in out:
            raise DataError("ledger monthly file: duplicate %r" % (key,))
        out[key] = dict(n=n, median=float(med) if med != "" else None, status=r[8])
    return out


def ledger_cell(ledger, month, series, tenor):
    """The month's own cell if it publishes a median, else None. Nothing is carried forward and no other tenor is borrowed (G12)."""
    if M("tenor_mix") and tenor == "3m":
        tenor = "1y"
    c = ledger.get((month, series, tenor))
    if c is None and M("ledger_ffill_stale"):
        last_m = max(m for (m, s_, t_) in ledger)                  # the mutant: a ledger file that ends early is carried forward
        if month > last_m:
            c = ledger.get((last_m, series, tenor))
    if (c is None or c["median"] is None) and M("carry_forward"):
        m = months_between(month[:4] + "-01", month)       # the mutant: the last month that had a cell
        for mm in reversed(m[:-1]):
            c2 = ledger.get((mm, series, tenor))
            if c2 is not None and c2["median"] is not None:
                c = c2
                break
    if c is None or c["median"] is None:
        return None
    return c


HOME_SERIES = {"yen": ("tona_ois", "xccy_jpyusd"), "euro": ("estr_ois", "xccy_eurusd")}


# ------------------------------------------------------------------------------------------------------------------------
# the daily panel (3.6) and the legs
# ------------------------------------------------------------------------------------------------------------------------
def pick_legs(d, series_list):
    """The latest date on or before d of each leg's series. The G6 mutant takes the first date on or after d (a leg from the future)."""
    out = []
    for s in series_list:
        out.append(s.geq(d) if M("next_day_leg") else s.leq(d))
    return out


def build_panel(inp, pair, tsy_dates=None):
    """One row per New York Treasury date for the pair. Floats in memory; formatting happens when the file is written. -> list of dict"""
    ccy = PAIR_CCY[pair]
    sofr_s, effr_s = RateSeries(inp.sofr), RateSeries(inp.effr)
    if pair == "yen":
        rate_s = RateSeries(inp.tona)
        yld = {d: v for d, v in inp.jgb.items() if v is not None}
        start = YEN_RATE_START
    else:
        rate_s = RateSeries(inp.estr)
        yld = inp.aaa
        start = EURO_RATE_START
    yld_s = RateSeries(yld)
    dks = inp.dks.get((ccy, "3m"), {})
    rows = []
    for d in (tsy_dates if tsy_dates is not None else sorted(inp.tsy)):
        if d < start:
            continue
        row = dict(date=d, pair=pair, leg_date=None, ust10=inp.tsy[d], home10=None, r_us=None, r_us_rt=None, r_effr=None, r_home=None, r_home_rt=None,
                   D=hedge_days(d, 3), h_A_rt=None, h_A_hist=None, h_A_effr=None, h_B=None, gap_A_rt=None, gap_A_hist=None, gap_B=None, h_dks=None,
                   qe=1 if d.month in QE_START_MONTHS else 0, drop="")
        ts, te, th, ty = pick_legs(d, [sofr_s, effr_s, rate_s, yld_s])
        row["leg_date"] = th
        if None in (ts, te, th, ty):
            row["drop"] = "no_leg"
            rows.append(row)
            continue
        if not M("no_stale_check") and any((d - x).days > STALE_DAYS for x in (ts, te, th, ty)):
            row["drop"] = "stale_leg"
            rows.append(row)
            continue
        D, y_us = row["D"], row["ust10"]
        row["home10"] = yld[ty]
        row["r_us"], row["r_effr"], row["r_home"] = sofr_s.v[ts], effr_s.v[te], rate_s.v[th]
        us_rt = ts if M("a_rt_dated") else sofr_s.lt(d)          # the mutant: A_rt reads the dated SOFR, not yet published at the snapshot
        hr = rate_s.lt(th)
        if us_rt is None or hr is None:
            row["drop"] = "no_leg"
            rows.append(row)
            continue
        row["r_us_rt"], row["r_home_rt"] = sofr_s.v[us_rt], rate_s.v[hr]
        row["h_A_rt"], row["gap_A_rt"] = spot_h(y_us, row["r_us_rt"], row["r_home_rt"], D, pair)
        row["h_A_hist"], row["gap_A_hist"] = spot_h(y_us, row["r_us"], row["r_home"], D, pair)
        row["h_A_effr"] = spot_h(y_us, row["r_effr"], row["r_home"], D, pair)[0]
        e = add_months(d, 3)
        G_us, G_h = sofr_s.compound(d, e, day_basis("us")), rate_s.compound(d, e, day_basis(pair))
        if G_us is not None and G_h is not None:
            row["h_B"], _ = forward_h(y_us, G_us, G_h, D, 0.0, pair)
            row["gap_B"] = row["h_B"] - y_us
        rec = dks.get(d)
        if rec is not None and rec["rho"] is not None:
            row["h_dks"] = y_us + rho_signed(rec["rho"])
        rows.append(row)
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# months: completeness, the headline and the diagnostics
# ------------------------------------------------------------------------------------------------------------------------
def month_status(panel, tsy_dates, month):
    """-> (n_kept, partial). A month is partial if its last business day is missing for any leg, or if the Treasury data do not run past its end."""
    rows = [r for r in panel if month_key(r["date"]) == month]
    kept = [r for r in rows if not r["drop"]]
    if M("partial_counted"):
        return len(kept), False
    ust_in_month = [d for d in tsy_dates if month_key(d) == month]
    if not ust_in_month or max(tsy_dates) <= month_end(month):
        return len(kept), True
    last = max(ust_in_month)
    last_row = next((r for r in rows if r["date"] == last), None)
    return len(kept), last_row is None or bool(last_row["drop"])


def diag_row(month, pair, variant, role, kept, key_h, key_gap, qe, partial, tenor_label="none"):
    """The monthly mean of a daily diagnostic over the days where it exists. Every term is averaged, so the identity holds in the means."""
    ds = [r for r in kept if r[key_h] is not None]
    if not ds:
        return None
    ust, home = mean(r["ust10"] for r in ds), mean(r["home10"] for r in ds)
    gap, carry = mean(r[key_gap] for r in ds), mean(r[key_h] for r in ds)
    return dict(month=month, pair=pair, variant=variant, role=role, n_days=len(ds), partial=int(partial), qe=qe, ust10=ust, home10=home,
                rate_gap_term=gap, basis_term=0.0, carry=carry, pickup=carry - home, form_gap_bp=None, basis_tenor=tenor_label,
                hedge_days_mean=mean(r["D"] for r in ds), n_ois_us=None, n_ois_home=None, n_basis=None)


def headline_rows(month, pair, kept, ledger, tsy_dates, qe, partial):
    """H3, P3 (3-month) and H12, P12 (1-year) for the month; a form exists only if all three cells publish a median (3.3)."""
    out = []
    if not kept:
        return out
    ois_home, xccy = HOME_SERIES[pair]
    for ten, k, vh, vp, role_h, role_p in (("3m", 3, "H3", "P3", "HEADLINE", "MAIN"), ("1y", 12, "H12", "P12", "MAIN", "MAIN")):
        c_us, c_h, c_b = (ledger_cell(ledger, month, s, ten) for s in ("sofr_ois", ois_home, xccy))
        if pair == "euro" and month < EURO_HEADLINE_START:
            continue
        if None in (c_us, c_h, c_b):
            continue
        Dm = mean(hedge_days(d, k) for d in tsy_dates if month_key(d) == month)
        y_us, y_home = mean(r["ust10"] for r in kept), mean(r["home10"] for r in kept)
        h = headline(y_us, c_us["median"], c_h["median"], c_b["median"], Dm, pair)
        base = dict(month=month, pair=pair, n_days=len(kept), partial=int(partial), qe=qe, ust10=y_us, home10=y_home, basis_tenor=ten,
                    hedge_days_mean=Dm, n_ois_us=c_us["n"], n_ois_home=c_h["n"], n_basis=c_b["n"])
        out.append(dict(base, variant=vh, role=role_h, rate_gap_term=h["rate_gap_term"], basis_term=h["basis_term"], carry=h["H"], pickup=h["H"] - y_home,
                        form_gap_bp=h["form_gap_bp"]))
        out.append(dict(base, variant=vp, role=role_p, rate_gap_term=h["p_gap"], basis_term=h["p_basis"], carry=h["P"], pickup=h["P"] - y_home,
                        form_gap_bp=h["form_gap_bp"]))
    return out


DIAG_DEFS = (("A_rt", "h_A_rt", "gap_A_rt"), ("A_hist", "h_A_hist", "gap_A_hist"), ("A_effr", "h_A_effr", "gap_A_hist"), ("B", "h_B", "gap_B"))


def monthly_rows(panel_by_pair, ledger, tsy_dates):
    """All monthly rows for both pairs: the headline and main forms, then the diagnostics. -> (rows, status {(pair, month): (n_kept, partial)})"""
    rows, status = [], {}
    for pair, panel in panel_by_pair.items():
        months = sorted({month_key(r["date"]) for r in panel})
        for m in months:
            n_kept, partial = month_status(panel, tsy_dates, m)
            status[(pair, m)] = (n_kept, partial)
            kept = [r for r in panel if month_key(r["date"]) == m and not r["drop"]]
            qe = 1 if int(m[5:7]) in QE_START_MONTHS else 0
            rows += headline_rows(m, pair, kept, ledger, tsy_dates, qe, partial)
            for variant, kh, kg in DIAG_DEFS:
                if variant == "A_effr":
                    # A_effr's gap is h - ust10 with EFFR in place of SOFR: its own term, not A_hist's
                    ds = [dict(r, gap_E=r["h_A_effr"] - r["ust10"]) for r in kept if r["h_A_effr"] is not None]
                    rr = diag_row(m, pair, variant, "DIAGNOSTIC", ds, kh, "gap_E", qe, partial)
                else:
                    rr = diag_row(m, pair, variant, "DIAGNOSTIC", kept, kh, kg, qe, partial)
                if rr:
                    rows.append(rr)
    order = {"H3": 0, "P3": 1, "H12": 2, "P12": 3, "A_rt": 4, "A_hist": 5, "A_effr": 6, "B": 7}
    rows.sort(key=lambda r: (r["pair"], r["month"], order[r["variant"]]))
    return rows, status




# ------------------------------------------------------------------------------------------------------------------------
# references and the validation gate (section 5)
# ------------------------------------------------------------------------------------------------------------------------
GATE_TOL_BP = 25.0
GINNIE = (("2025-04", 0.77, 2.14), ("2025-05", 0.77, 2.13), ("2025-11", 1.14, 2.44), ("2026-06", 1.56, 2.92))
GINNIE_INFO = (("2024-09", 0.09, 2.48), ("2024-08", -0.18, 2.50))
V1_QUOTE, V1_MONTH = 2.0, "2026-09"       # BlackRock weekly commentary, 8 Sep 2026: "versus 2% on a 10-year Treasury after hedging", rolling 3-month forwards
V2_QUOTE, V2_MONTH = 1.3, "2026-03"       # TD Economics, 31 Mar 2026: "closer to 1.3% on a fully hedged U.S. Treasury"
V4_POINTS = (("2025-04", -35.0, -35.0), ("2026-01", -20.0, -15.0))   # Banque de France blog 444: premium 35bp on 9 Apr 2025; 15-20bp at the start of 2026
V5_THRESHOLDS = (10.0, 15.0)
V5_MIN_CORR_N = 8


def quote_gap_bp(value, quote, half_width):
    """The distance in bp from the build value to the quote's rounding interval [quote - half_width, quote + half_width] (zero inside it). The O-9 ruling
    applies this to whole-percent quotes only (half_width 0.5); a quote given to a tenth or a hundredth is scored at its printed value (half_width 0)."""
    if M("rounding_to_status"):
        half_width = 0.0 if half_width == 0.5 else half_width
    lo, hi = quote - half_width, quote + half_width
    if lo <= value <= hi:
        return 0.0
    return 100.0 * (lo - value if value < lo else value - hi)


def gate_median(gaps):
    """The gate statistic: the MEDIAN of the group's absolute gaps (a median above 25bp is a FAILED build)."""
    if M("gate_min"):
        return min(gaps)                        # the mutant: the best point stands for the group
    return statistics.median(gaps)


def gate_status(gaps, expected_n):
    if M("gate_rounding_credit"):
        gaps = [max(0.0, g - 5.0) for g in gaps]    # the mutant: the quote's rounding credited against the gate
    if len(gaps) != expected_n:
        return "FAIL"                           # a gate that cannot be computed on all its points is not passed
    return "FAIL" if gate_median(gaps) > GATE_TOL_BP else "PASS"


def month_end_ust(inp, month):
    ds = [d for d in inp.tsy if month_key(d) == month]
    return inp.tsy[max(ds)] if ds else None


def ginnie_build(inp, ledger, tsy_dates, pair, month):
    """H12 and P12 with that month's 1y cells and the MONTH-END Treasury yield (V3). -> dict or None"""
    ois_home, xccy = HOME_SERIES[pair]
    cells = [ledger_cell(ledger, month, s, "1y") for s in ("sofr_ois", ois_home, xccy)]
    y_me = month_end_ust(inp, month)
    if None in cells or y_me is None:
        return None
    Dm = mean(hedge_days(d, 12) for d in tsy_dates if month_key(d) == month)
    return headline(y_me, cells[0]["median"], cells[1]["median"], cells[2]["median"], Dm, pair)


def v5_ref_rows(v5):
    out = []
    for v in v5:
        s_ = v["stats"]
        out.append(dict(ref_id="V5", source="Du, Keerati and Schreger (cache only): the all-in forward premium rho, 3m", ref_date=v["window"], pair=v["pair"], form=v["form"],
                        tenor="3m", published=None, rounding_bp=None, build_value=None, gap_bp=s_["med_abs_bp"], tolerance=V5_THRESHOLDS[0], status=s_["status"],
                        note="n=%d months; median absolute monthly difference in bp (gap_bp); median signed difference (build minus DKS) %s bp; correlation %s%s"
                        % (s_["n"], fmt(s_["med_signed_bp"], 2), fmt(s_["corr"], 3) if s_["corr"] is not None else "n/a (needs n >= 8)",
                           "; the A form has no basis term, the DKS rho has it inside" if v["form"] == "A_hist" else ""),
                        note_com="n=%d months; the yen statistics are kept in the cache (Bank of Japan terms)%s" % (
                            s_["n"], "; the A form has no basis term, the DKS rho has it inside" if v["form"] == "A_hist" else "")))
    return out


def build_references(inp, ledger, tsy_dates, mrows):
    """-> (refs [dict], gate {(form, tenor): (status, median or None, n)}). Full rows (yen build values included); the committed version blanks them."""
    by = {(r["pair"], r["month"], r["variant"]): r for r in mrows}
    refs, gaps = [], {("H", "3m"): [], ("P", "3m"): [], ("H", "1y"): [], ("P", "1y"): []}

    def add(**kw):
        d = dict(ref_id="", source="", ref_date="", pair="", form="", tenor="", published=None, rounding_bp=None, build_value=None, gap_bp=None,
                 tolerance=GATE_TOL_BP, status="", note="")
        d.update(kw)
        refs.append(d)
    for form, var in (("H", "H3"), ("P", "P3")):
        r = by.get(("yen", V1_MONTH, var))
        v = None if r is None else r["carry"]
        g = None if v is None else quote_gap_bp(v, V1_QUOTE, 0.5)
        if g is not None:
            gaps[(form, "3m")].append(g)
        add(ref_id="V1", source="BlackRock weekly commentary, 8 Sep 2026", ref_date="2026-09-08", pair="yen", form=form, tenor="3m", published=V1_QUOTE,
            rounding_bp=50.0, build_value=v, gap_bp=g, status="NO_BUILD" if g is None else ("PASS" if g <= GATE_TOL_BP else "MISS"),
            note="whole-percent quote scored against its rounding interval [1.5, 2.5] (O-9); the gap is the distance to the interval; the exact date is not given, "
                 "so the month of September 2026 stands")
    for form, var in (("H", "H3"), ("P", "P3")):
        r = by.get(("yen", V2_MONTH, var))
        v = None if r is None else r["carry"]
        g = None if v is None else quote_gap_bp(v, V2_QUOTE, 0.0)
        if g is not None:
            gaps[(form, "3m")].append(g)
        add(ref_id="V2", source="TD Economics, 31 Mar 2026", ref_date="2026-03-31", pair="yen", form=form, tenor="3m", published=V2_QUOTE, rounding_bp=5.0,
            build_value=v, gap_bp=g, status="NO_BUILD" if g is None else ("PASS" if g <= GATE_TOL_BP else "MISS"),
            note="scored at the printed value (one decimal); the data date and the 3-month rates (bills or OIS) are not stated; "
                 + ("within quote rounding" if g is not None and GATE_TOL_BP < g <= GATE_TOL_BP + 5.0 else "month of March 2026 stands"))
    r = by.get(("yen", V2_MONTH, "P3"))
    if r is not None:
        v = r["ust10"] + r["rate_gap_term"]
        add(ref_id="V2", source="TD Economics, 31 Mar 2026", ref_date="2026-03-31", pair="yen", form="P_no_basis", tenor="3m", published=V2_QUOTE,
            rounding_bp=5.0, build_value=v, gap_bp=100.0 * abs(v - V2_QUOTE), status="INFO",
            note="TD's formula has no basis term: the like-for-like plain subtraction, not scored")
    for pair in ("yen", "euro"):
        for month, pub_y, pub_e in GINNIE:
            pub = pub_y if pair == "yen" else pub_e
            gb = ginnie_build(inp, ledger, tsy_dates, pair, month)
            for form in ("H", "P"):
                v = None if gb is None else gb[form]
                g = None if v is None else 100.0 * abs(v - pub)
                if g is not None:
                    gaps[(form, "1y")].append(g)
                add(ref_id="V3", source="Ginnie Mae Global Markets Analysis (Bloomberg data), month-end", ref_date=month, pair=pair, form=form, tenor="1y",
                    published=pub, rounding_bp=0.5, build_value=v, gap_bp=g, status="NO_BUILD" if g is None else ("PASS" if g <= GATE_TOL_BP else "MISS"),
                    note="monthly-median 1y cells with the month-end Treasury yield; Bloomberg forwards are FX-swap prices, the cells are currency-swap prints")
    for pair in ("yen", "euro"):
        for month, pub_y, pub_e in GINNIE_INFO:
            pub = pub_y if pair == "yen" else pub_e
            add(ref_id="V3-info", source="Ginnie Mae Global Markets Analysis, Oct 2024 issue", ref_date=month, pair=pair, form="H", tenor="1y", published=pub,
                rounding_bp=0.5, status="INFO", note="before the tape starts: no build value")
    # V4: Banque de France, the 3-month yen premium (non-independent: the windows were set after a rough look)
    for month, lo, hi in V4_POINTS:
        c = ledger_cell(ledger, month, "xccy_jpyusd", "3m")
        v = None if c is None else c["median"]
        mid = (lo + hi) / 2.0
        g = None if v is None else abs(v - mid)
        add(ref_id="V4", source="Banque de France blog 444, 13 Apr 2026, Chart 3 note", ref_date=month, pair="yen", form="basis", tenor="3m", published=mid,
            rounding_bp=abs(hi - lo) / 2.0, build_value=v, gap_bp=g, tolerance=10.0,
            status="NO_BUILD" if g is None else ("PASS" if g <= 10.0 + abs(hi - lo) / 2.0 else "WARN"),
            note="CHECK, non-independent (these windows were chosen after a rough look); basis in bp, negative = a premium to borrow dollars")
    # V6: CFR 18 Mar 2024, sign only
    for var, kh in (("A_hist", "A_hist"), ("B", "B")):
        r = by.get(("yen", "2024-03", var))
        ok = r is not None and r["carry"] < 0.5 and r["pickup"] < 0
        add(ref_id="V6", source="Council on Foreign Relations, 18 Mar 2024", ref_date="2024-03", pair="yen", form=var, tenor="3m", published=None,
            build_value=None if r is None else r["carry"], gap_bp=None if r is None else 100.0 * r["pickup"], tolerance=None,
            status="NO_BUILD" if r is None else ("PASS" if ok else "FAIL"),
            note="sign only: carry below 0.5 percent and pickup below zero in March 2024 (gap_bp here is the pickup in bp)")
    gate = {}
    for (form, ten), g in gaps.items():
        exp_n = 2 if ten == "3m" else 8
        st = gate_status(g, exp_n)
        gate[(form, ten)] = (st, gate_median(g) if g else None, len(g))
        add(ref_id="GATE_%s_%s" % (form, ten), source="the median |build - published| over the group's points (section 5)", ref_date="", pair="yen" if ten == "3m" else "both",
            form=form, tenor=ten, build_value=None, gap_bp=gate[(form, ten)][1], status=st,
            note="%d points of %d; a median above 25bp is a FAILED build" % (len(g), exp_n))
    return refs, gate


# ------------------------------------------------------------------------------------------------------------------------
# V5: the DKS panel, statistics only
# ------------------------------------------------------------------------------------------------------------------------
def pearson(a, b):
    n = len(a)
    if n < 2:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    sa = sum((x - ma) ** 2 for x in a)
    sb = sum((y - mb) ** 2 for y in b)
    if sa <= 0 or sb <= 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(sa * sb)


def v5_stats(pairs):
    """pairs: [(build, dks)] monthly values in percent. -> dict(n, med_abs_bp, med_signed_bp, corr or None, status)"""
    n = len(pairs)
    if n == 0:
        return dict(n=0, med_abs_bp=None, med_signed_bp=None, corr=None, status="INFO")
    d = [100.0 * (a - b) for a, b in pairs]
    ma = statistics.median(abs(x) for x in d)
    corr = pearson([a for a, _ in pairs], [b for _, b in pairs]) if n >= V5_MIN_CORR_N else None
    if n < V5_MIN_CORR_N:
        st = "INFO"
    elif corr is not None and corr < 0 and not M("v5_neg_ok"):
        st = "FAIL"                              # a negative overlap correlation: the sign convention of rho is open (O-4)
    else:
        st = "PASS" if ma <= V5_THRESHOLDS[0] else ("WARN" if ma <= V5_THRESHOLDS[1] else "FAIL")
    return dict(n=n, med_abs_bp=ma, med_signed_bp=statistics.median(d), corr=corr, status=st)


def dks_monthly(panel, key):
    """{month: mean of (the panel's `key` carry, h_dks)} over the kept days where both exist, with at least 10 such days."""
    by = {}
    for r in panel:
        if not r["drop"] and r["h_dks"] is not None and r[key] is not None:
            by.setdefault(month_key(r["date"]), []).append((r[key], r["h_dks"]))
    return {m: (mean(a for a, _ in v), mean(b for _, b in v)) for m, v in by.items() if len(v) >= 10}


def v5_results(panel_by_pair, mrows):
    """-> list of dict(pair, form, window, stats). H3 against the DKS monthly mean on the months both exist; A_hist against it over the whole panel."""
    out = []
    for pair, panel in panel_by_pair.items():
        by_m = {}
        for r in panel:
            if not r["drop"] and r["h_dks"] is not None:
                by_m.setdefault(month_key(r["date"]), []).append(r["h_dks"])
        dks_mean = {m: mean(v) for m, v in by_m.items() if len(v) >= 10}
        h3 = {r["month"]: r["carry"] for r in mrows if r["pair"] == pair and r["variant"] == "H3" and not r["partial"]}
        pairs = [(h3[m], dks_mean[m]) for m in sorted(h3) if m in dks_mean]
        out.append(dict(pair=pair, form="H3", window="H3 months to 2025-06", stats=v5_stats(pairs), months=[m for m in sorted(h3) if m in dks_mean]))
        am = dks_monthly(panel, "h_A_hist")
        pairs = [am[m] for m in sorted(am)]
        out.append(dict(pair=pair, form="A_hist", window="2018-2025", stats=v5_stats(pairs), months=sorted(am)))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# section 4 (spec only): descriptive questions; summary.csv, yen_summary.csv
# ------------------------------------------------------------------------------------------------------------------------
def latest_complete(status):
    """L: the latest month that is complete (not partial, with kept days) for both pairs."""
    months = sorted({m for (_, m) in status})
    ok = [m for m in months if all(status.get((p, m), (0, True))[0] > 0 and not status.get((p, m), (0, True))[1] for p in ("yen", "euro"))]
    return ok[-1] if ok else None


def path_of(mrows, pair, variant, lo, hi):
    return {r["month"]: r for r in mrows if r["pair"] == pair and r["variant"] == variant and not r["partial"] and lo <= r["month"] <= hi}


def yen_anchor(ledger):
    months = sorted({m for (m, s, t) in ledger})
    for m in months:
        if all(ledger_cell(ledger, m, s, "3m") is not None for s in ("tona_ois", "sofr_ois", "xccy_jpyusd")):
            return m
    return None


def sign(x):
    return (x > 0) - (x < 0)


def section4(mrows, status, ledger, L, v5, label):
    """-> list of [question, pair, variant, statistic, value, notable] (values in the pair's own units; the committed version blanks the yen values)."""
    out = []

    def add(q, pair, var, stat, value, notable=""):
        out.append([q, pair, var, stat, value, notable])
    anchors = {"yen": yen_anchor(ledger), "euro": EURO_HEADLINE_START}
    # Q1 yen pickup sign
    a = anchors["yen"]
    pth = path_of(mrows, "yen", "H3", a, L) if a else {}
    pos = [m for m in sorted(pth) if pth[m]["pickup"] > 0]
    add("Q1", "yen", "H3", "months_pickup_gt_0", len(pos), "yes" if pos else "no")
    if pth:
        lo_m = min(pth, key=lambda m: pth[m]["pickup"])
        hi_m = max(pth, key=lambda m: pth[m]["pickup"])
        add("Q1", "yen", "H3", "min_pickup_pp", pth[lo_m]["pickup"])
        add("Q1", "yen", "H3", "min_pickup_month", lo_m)
        add("Q1", "yen", "H3", "max_pickup_pp", pth[hi_m]["pickup"])
        add("Q1", "yen", "H3", "max_pickup_month", hi_m)
        add("Q1", "yen", "H3", "n_months", len(pth))
    # Q2 euro pickup sign
    for var, lo in (("H3", EURO_HEADLINE_START), ("A_hist", "2023-01")):
        pth = path_of(mrows, "euro", var, lo, L)
        ms = sorted(pth)
        signs = [sign(pth[m]["pickup"]) for m in ms]
        changes = sum(1 for x, y in zip(signs, signs[1:]) if x != y and x != 0 and y != 0)
        add("Q2", "euro", var, "months_pickup_gt_0", sum(1 for x in signs if x > 0))
        add("Q2", "euro", var, "months_pickup_lt_0", sum(1 for x in signs if x < 0))
        add("Q2", "euro", var, "sign_changes", changes, "yes" if changes else "no")
        if ms:
            lo_m = min(ms, key=lambda m: pth[m]["pickup"])
            hi_m = max(ms, key=lambda m: pth[m]["pickup"])
            add("Q2", "euro", var, "min_pickup_pp", pth[lo_m]["pickup"])
            add("Q2", "euro", var, "min_pickup_month", lo_m)
            add("Q2", "euro", var, "max_pickup_pp", pth[hi_m]["pickup"])
            add("Q2", "euro", var, "max_pickup_month", hi_m)
            add("Q2", "euro", var, "n_months", len(ms))
    # Q3 where the change came from
    for pair in ("yen", "euro"):
        a = anchors[pair]
        pth = path_of(mrows, pair, "H3", a, L) if a else {}
        if a in pth and L in pth:
            r0, r1 = pth[a], pth[L]
            d = dict(ust10=r1["ust10"] - r0["ust10"], rate_gap_term=r1["rate_gap_term"] - r0["rate_gap_term"], basis_term=r1["basis_term"] - r0["basis_term"],
                     home10=r1["home10"] - r0["home10"])
            dp = r1["pickup"] - r0["pickup"]
            largest = max(d, key=lambda k: abs(d[k]))
            add("Q3", pair, "H3", "anchor_month", a)
            add("Q3", pair, "H3", "d_pickup_pp", dp)
            for k in ("ust10", "rate_gap_term", "basis_term", "home10"):
                add("Q3", pair, "H3", "d_%s_pp" % k, d[k])
            add("Q3", pair, "H3", "identity_residual_pp", dp - (d["ust10"] + d["rate_gap_term"] + d["basis_term"] - d["home10"]))
            add("Q3", pair, "H3", "largest_abs_term", largest, "yes" if largest != "rate_gap_term" else "no")
    # Q4 basis share
    for pair in ("yen", "euro"):
        a = anchors[pair]
        pth = path_of(mrows, pair, "H3", a, L) if a else {}
        sh = {m: abs(r["basis_term"]) / abs(r["rate_gap_term"] + r["basis_term"]) for m, r in pth.items() if r["rate_gap_term"] + r["basis_term"] != 0}
        if sh:
            med = statistics.median(sh.values())
            mx_m = max(sh, key=lambda m: sh[m])
            mn_m = min(sh, key=lambda m: sh[m])
            add("Q4", pair, "H3", "median_share", med, "yes" if (med > 0.10 or sh[mx_m] > 0.20) else "no")
            add("Q4", pair, "H3", "max_share", sh[mx_m])
            add("Q4", pair, "H3", "max_share_month", mx_m)
            add("Q4", pair, "H3", "min_share", sh[mn_m])
            add("Q4", pair, "H3", "min_share_month", mn_m)
            add("Q4", pair, "H3", "n_months", len(sh))
    # Q5 construction and form wedges
    for pair in ("yen", "euro"):
        a = anchors[pair]
        h3 = path_of(mrows, pair, "H3", a, L) if a else {}
        meds, dis = {}, {}
        for var in ("A_rt", "A_hist", "B", "P3"):
            ox = path_of(mrows, pair, var, a, L) if a else {}
            both = [m for m in sorted(h3) if m in ox]
            if both:
                meds[var] = statistics.median(abs(h3[m]["carry"] - ox[m]["carry"]) * 100.0 for m in both)
                dis[var] = sum(1 for m in both if sign(h3[m]["pickup"]) != sign(ox[m]["pickup"]))
                add("Q5", pair, "H3", "median_abs_H3_minus_%s_bp" % var, meds[var])
                add("Q5", pair, "H3", "sign_disagree_months_vs_%s" % var, dis[var])
        if h3:
            fg = statistics.median(abs(r["form_gap_bp"]) for r in h3.values())
            add("Q5", pair, "H3", "median_abs_form_gap_bp", fg)
            union = sum(1 for m in h3 if any(sign(h3[m]["pickup"]) != sign(path_of(mrows, pair, v, a, L)[m]["pickup"])
                                              for v in ("A_rt", "A_hist", "B", "P3") if m in path_of(mrows, pair, v, a, L)))
            wide = [x for k, x in meds.items() if x > 25.0] + ([fg] if fg > 25.0 else [])
            add("Q5", pair, "H3", "months_with_any_sign_disagreement", union)
            add("Q5", pair, "H3", "share_months_with_any_sign_disagreement", union / len(h3), "yes" if (wide or union / len(h3) > 0.10) else "no")
    # Q6 tenor
    for pair in ("yen", "euro"):
        a = anchors[pair]
        h3 = path_of(mrows, pair, "H3", a, L) if a else {}
        h12 = path_of(mrows, pair, "H12", a, L) if a else {}
        both = [m for m in sorted(h3) if m in h12]
        if both:
            med = statistics.median(abs(h3[m]["carry"] - h12[m]["carry"]) * 100.0 for m in both)
            add("Q6", pair, "H3", "median_abs_H3_minus_H12_bp", med, "yes" if med > 25.0 else "no")
            add("Q6", pair, "H3", "n_months", len(both))
    # Q7 DKS
    for v in v5:
        s = v["stats"]
        add("Q7", v["pair"], v["form"], "n_months", s["n"])
        add("Q7", v["pair"], v["form"], "median_abs_diff_bp", s["med_abs_bp"])
        add("Q7", v["pair"], v["form"], "median_signed_diff_bp", s["med_signed_bp"])
        add("Q7", v["pair"], v["form"], "correlation", s["corr"], s["status"])
    return out


def summary_texts(s4, L, label):
    """-> (committed rows, full rows)."""
    def val(v):
        if v is None or v == "":
            return ""
        if isinstance(v, float):
            return f(v, 6)
        return str(v)
    full, com = [[label, L, "L", "", "", "latest_complete_month", "", ""]], [[label, L, "L", "", "", "latest_complete_month", "", ""]]
    for q, pair, var, stat, v, nb in s4:
        full.append([label, L, q, pair, var, stat, val(v), nb])
        com.append([label, L, q, pair, var, stat, "" if pair == "yen" else val(v), nb])
    return com, full


def yen_summary_rows(mrows, status, L, ledger):
    """Annual means of the complete months plus the anchor and L months. At most 8 values per (variant, statistic). -> rows"""
    anchor = yen_anchor(ledger)
    rows = []
    stats = (("hedged_carry_mean", "carry"), ("pickup_mean", "pickup"), ("rate_gap_term_mean", "rate_gap_term"), ("basis_term_mean", "basis_term"))
    periods = [("2023", "2023-01", "2023-12"), ("2024", "2024-01", "2024-12"), ("2025", "2025-01", "2025-12"), ("2026_ytd", "2026-01", L)]
    if anchor:
        periods.append(("anchor_" + anchor, anchor, anchor))
    periods.append(("L_" + L, L, L))
    for variant in ("H3", "P3", "H12", "A_hist", "B"):
        for per, lo, hi in periods:
            pth = path_of(mrows, "yen", variant, lo, hi)
            if not pth:
                continue
            for stat, key in stats:
                rows.append([per, variant, stat, f(mean(r[key] for r in pth.values()), 6), BOJ_CREDIT])
            rows.append([per, variant, "n_months", str(len(pth)), BOJ_CREDIT])
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# the licence and leak guards (section 7, G10)
# ------------------------------------------------------------------------------------------------------------------------
def raw_monthly_means(inp):
    """{series name: {month: mean}} of every raw input series, for the rounded comparison of G10d."""
    out = {}
    series = {"tsy": inp.tsy, "sofr": inp.sofr, "effr": inp.effr, "estr": inp.estr, "tona": inp.tona, "jgb": {d: v for d, v in inp.jgb.items() if v is not None},
             "aaa": inp.aaa, "bund": inp.bbk}
    for name, s in series.items():
        by = {}
        for d, v in s.items():
            by.setdefault(month_key(d), []).append(v)
        out[name] = {m: mean(v) for m, v in by.items()}
    return out


def parse_rows(text, name=None):
    h, rows = read_csv_rows_text(text)
    return h, rows


def read_csv_rows_text(text):
    lines = [ln for ln in text.splitlines(True) if not ln.startswith("#")]
    rd = list(csv.reader(io.StringIO("".join(lines))))
    return (rd[0], rd[1:]) if rd else ([], [])


def leak_guard(texts, raw_means):
    """texts: {committed file name: text}. -> list of problems (an empty list is a pass). Section 7 / G10 (a)-(g)."""
    bad = []
    month_rx, period_rx = re.compile(r"\d{4}-\d{2}"), re.compile(r"(\d{4}|\d{4}_ytd|anchor_\d{4}-\d{2}|L_\d{4}-\d{2})")
    for name, text in texts.items():
        h, rows = read_csv_rows_text(text)
        for c in h:
            if re.search(r"dks|rho", c, re.I) and not M("leak_dks_off"):
                bad.append("%s: a DKS-tagged column %r" % (name, c))                 # (b)
            if re.fullmatch(r"(tona|sofr|estr|effr|jgb|aaa|bund)(_?\w*)?_pct", c, re.I) and c not in ("ust10_pct", "home10_pct") and not M("leak_numeric_off"):
                bad.append("%s: a raw-input column %r" % (name, c))                   # (d), by name
    if "monthly.csv" in texts:
        h, rows = read_csv_rows_text(texts["monthly.csv"])
        ix = {c: i for i, c in enumerate(h)}
        for r in rows:
            if not month_rx.fullmatch(r[ix["month"]]) and not M("leak_date_off"):
                bad.append("monthly.csv: a date column that is not YYYY-MM: %r" % r[ix["month"]])          # (a)
            if r[ix["pair"]] != "euro" and not M("leak_yenrow_off"):
                bad.append("monthly.csv: a %s row (euro only is committed)" % r[ix["pair"]])                 # (e)
        for c in h:
            if c in ("ust10_pct", "home10_pct") or c not in ix:
                continue
            col = []
            for r in rows:
                try:
                    col.append((r[ix["month"]], float(r[ix[c]])))
                except ValueError:
                    pass
            nd = max((len(v.split(".")[1]) for r in rows for v in [r[ix[c]]] if "." in v), default=6)
            for name, mm in raw_means.items():
                if name == "tsy":
                    continue
                hits = [m for m, v in col if m in mm and abs(round(mm[m], nd) - v) <= 1e-6]
                if len(col) >= 5 and len(hits) >= 0.9 * len(col) and not M("leak_numeric_off"):
                    bad.append("monthly.csv: column %s equals the monthly mean of raw input %s (G10d)" % (c, name))
    if "yen_summary.csv" in texts:
        h, rows = read_csv_rows_text(texts["yen_summary.csv"])
        cnt = {}
        for r in rows:
            if not period_rx.fullmatch(r[0]):
                bad.append("yen_summary.csv: period %r" % r[0])
            cnt[(r[1], r[2])] = cnt.get((r[1], r[2]), 0) + 1
        for k, n in cnt.items():
            if n > 8 and not M("leak_cap_off"):
                bad.append("yen_summary.csv: %d values for %s (at most 8)" % (n, k))                  # (f)
    if "summary.csv" in texts:
        h, rows = read_csv_rows_text(texts["summary.csv"])
        for r in rows:
            if r[3] == "yen" and r[6] != "":
                bad.append("summary.csv: a yen value in %s %s" % (r[2], r[5]))
    if "references.csv" in texts:
        h, rows = read_csv_rows_text(texts["references.csv"])
        ix = {c: i for i, c in enumerate(h)}
        for r in rows:
            if r[ix["pair"]] == "yen" and (r[ix["build_value"]] != "" or r[ix["gap_bp"]] != "") and not r[ix["ref_id"]].startswith("GATE") and not M("leak_refs_off"):
                bad.append("references.csv: a yen build value or gap in %s" % r[ix["ref_id"]])            # (g)
            if r[ix["ref_id"]] == "GATE_H_3m" or r[ix["ref_id"]] == "GATE_P_3m":
                if r[ix["gap_bp"]] != "":
                    bad.append("references.csv: the yen 3m gate carries a gap")
    if "pins.csv" in texts:
        h, rows = read_csv_rows_text(texts["pins.csv"])
        cnt = {}
        for r in rows:
            cnt[r[0]] = cnt.get(r[0], 0) + 1
        for k, n in cnt.items():
            if n > 5:
                bad.append("pins.csv: %d pins for %s (at most 5)" % (n, k))
    return bad




# ------------------------------------------------------------------------------------------------------------------------
# checks (section 8)
# ------------------------------------------------------------------------------------------------------------------------
def close(a, b, tol):
    return a is not None and abs(a - b) <= tol


def age_flag(asof, last, limit):
    """C12 (R7): an input older than its limit is a WARN (its series ends at its last date; nothing is forward-filled)."""
    if M("stale_ok"):
        return "PASS"                           # the mutant: a 20-day-old file passes silently
    return "PASS" if last is not None and (asof - last).days <= limit else "WARN"


def index_pair_diff(idx_a, idx_b, rate_a, ndays):
    """Index(b)/Index(a) minus 1 + rate_a * ndays / 36000 (the NY Fed index rule; the ECB's compounded index follows the same rule)."""
    exp = (1.0 + rate_a / 36000.0) ** ndays if M("index_daily_compound") else 1.0 + rate_a * ndays / 36000.0
    return idx_b / idx_a - exp


def index_checks(index, rate, B, start, tol, month_from):
    """C04 / C05: the pairwise rule and the 3-month window test against the compounding of B. -> dict(n_pairs, max_pair, bad_pairs, n_windows, max_win, bad_windows)"""
    dates = [d for d in sorted(index) if d >= start]
    bad_p, max_p, n_p = [], 0.0, 0
    for a, b in zip(dates, dates[1:]):
        if a not in rate:
            continue
        n_p += 1
        diff = abs(index_pair_diff(index[a], index[b], rate[a], (b - a).days))
        max_p = max(max_p, diff)
        if diff > tol:
            bad_p.append(a)
    rs = RateSeries(rate)
    bad_w, max_w, n_w = [], 0.0, 0
    seen = set()
    for d in rs.dates:
        m = month_key(d)
        if m < month_from or m in seen or d not in index:
            continue
        seen.add(m)                                          # the first business day of the month
        e = next((x for x in dates if x >= add_months(d, 3)), None)
        if e is None:
            continue
        G = rs.compound(d, e, B)
        if G is None:
            continue
        n_w += 1
        diff = abs(index[e] / index[d] - G)
        max_w = max(max_w, diff)
        if diff > tol:
            bad_w.append(d)
    return dict(n_pairs=n_p, max_pair=max_p, bad_pairs=bad_p, n_windows=n_w, max_win=max_w, bad_windows=bad_w)


EXPECTED_TRIPLES = (("2025-01-02", "2024-12-30", "2025-01-02"), ("2025-04-21", "2025-04-21", "2025-04-17"),
                    ("2025-12-26", "2025-12-26", "2025-12-24"), ("2026-05-06", "2026-05-01", "2026-05-06"))


def triple(d, tona_s, jgb_s, estr_s):
    """(d, Tokyo date, TARGET date): the latest date on or before d on which the Tokyo (TONA and JGB) and TARGET (euro short-term rate) legs exist."""
    tk = [x for x in pick_legs(d, [tona_s, jgb_s]) if x]
    return d, (min(tk) if tk else None), pick_legs(d, [estr_s])[0]


def build_checks(c):
    """c: the build context. -> list of [id, description, expected, observed, status]"""
    inp, ledger, asof = c["inp"], c["ledger"], c["asof"]
    ck = []

    def add(cid, desc, exp, obs, st):
        ck.append([cid, desc, str(exp), str(obs), st])

    def pins(cid, desc, series, pairs, nd, tol=1e-9):
        got = [(d, series.get(d)) for d, _ in pairs]
        ok = all(close(g, e, tol) for (d, g), (_, e) in zip(got, pairs))
        add(cid, desc, "; ".join("%s %s" % (d, e) for d, e in pairs), "; ".join("%s %s" % (d, "missing" if g is None else f(g, nd)) for d, g in got),
            "PASS" if ok else "FAIL")
    D = dt.date.fromisoformat
    pins("C01", "Treasury 10 Yr read by header name", inp.tsy, [(D("2024-03-21"), 4.27), (D("2026-09-18"), 5.01), (D("2026-10-15"), 5.10)], 2)
    pins("C02", "MoF 10Y (history file merged with the current-month file)", inp.jgb, [(D("2024-03-22"), 0.762), (D("2026-09-18"), 2.981), (D("2026-10-01"), 3.092)], 3)
    add("C02b", "MoF: the history file and the current-month file agree on every shared date", "no disagreement",
        ("agree on %d shared dates (the history file ends %s, the current-month file starts %s)" % (c["jgb_overlap"], iso(c["jgb_hist_end"]), iso(c["jgb_cur_start"]))
         if not inp.jgb_err else inp.jgb_err), "PASS" if not inp.jgb_err else "FAIL")
    pins("C03", "NY Fed SOFR", inp.sofr, [(D("2018-04-02"), 1.80), (D("2026-10-15"), 3.89)], 2)
    pins("C03b", "NY Fed EFFR", inp.effr, [(D("2026-10-15"), 3.88)], 2)
    r4 = index_checks(inp.sofrai, inp.sofr, 360.0, D("2020-03-02"), 2e-8, "2020-03")
    add("C04", "SOFR Index: Index(b)/Index(a) = 1 + SOFR(a)(b-a)/36000 within 2e-8 for each consecutive pair, and the 3-month window test against B's compounding",
        "0 misses", "%d pairs, max %.2e, %d misses; %d windows, max %.2e, %d misses" % (r4["n_pairs"], r4["max_pair"], len(r4["bad_pairs"]), r4["n_windows"],
                                                                                   r4["max_win"], len(r4["bad_windows"])),
        "PASS" if not r4["bad_pairs"] and not r4["bad_windows"] and r4["n_pairs"] > 1000 and r4["n_windows"] > 60 else "FAIL")
    pins("C04b", "SOFR Index pin", inp.sofrai, [(D("2026-10-16"), 1.26303308)], 8)
    pins("C05a", "euro short-term rate (volume-weighted trimmed mean)", inp.estr, [(D("2019-10-01"), -0.549), (D("2026-10-16"), 2.441)], 3)
    pins("C05b", "compounded euro short-term rate index", inp.estr_ci, [(D("2026-10-19"), 110.03236357)], 8)
    r5 = index_checks(inp.estr_ci, inp.estr, 360.0, D("2019-10-01"), 1e-9, "2019-10")
    add("C05", "euro short-term rate index: the same rule within 1e-9, pairwise and on the window test", "0 misses",
        "%d pairs, max %.2e, %d misses; %d windows, max %.2e, %d misses" % (r5["n_pairs"], r5["max_pair"], len(r5["bad_pairs"]), r5["n_windows"],
                                                                           r5["max_win"], len(r5["bad_windows"])),
        "PASS" if not r5["bad_pairs"] and not r5["bad_windows"] and r5["n_pairs"] > 1000 and r5["n_windows"] > 60 else "FAIL")
    pins("C06", "TONA from the Bank of Japan API ('null' is missing, the header block and the quoted series name parse)", inp.tona,
         [(D("2018-01-04"), -0.047), (D("2026-10-15"), 1.228)], 3)
    add("C06b", "TONA: the header block's NEXTPOSITION is empty (no further page) and 'null' days are not values", "empty; no 0 on a null day",
        "NEXTPOSITION %r; %d null days read as missing" % (inp.tona_next, c["tona_nulls"]), "PASS" if inp.tona_next == "" and c["tona_nulls"] > 0 else "FAIL")
    p = fx.params_of(inp.aaa_published[D("2026-09-18")]) if D("2026-09-18") in inp.aaa_published else None
    v = fx.ea_semiannual(10, p) if p else None
    add("C07", "ECB AAA 10-year, semiannual par recomputed from the Svensson parameters (ea10_sa)", "2026-09-18 3.533452 within 1e-5",
        "2026-09-18 %s; %d date(s) quarantined, %d incomplete" % ("missing" if v is None else f(v, 6), len(inp.yc_quar), len(inp.yc_incomplete)),
        "PASS" if close(v, 3.533452, 1e-5) else "FAIL")
    pr = inp.dks_probe
    if pr is None:
        add("C08", "DKS probe", "206, header, size and ETag as observed", "no probe file in the cache", "FAIL")
    else:
        ok = pr["status"] == 206 and pr["size"] == DKS_SIZE_OBSERVED
        st = "PASS" if ok and pr["etag"] == DKS_ETAG_OBSERVED else ("WARN" if ok else "FAIL")
        add("C08", "DKS ranged probe: 206 with the header, size and ETag as observed", "206; %d bytes; ETag %s" % (DKS_SIZE_OBSERVED, DKS_ETAG_OBSERVED),
            "%s; %d bytes; ETag %s" % (pr["status"], pr["size"], pr["etag"]), st)
    have = {k: len(v) for k, v in inp.dks.items()}
    full = [r for r in c["fetch_rows"] if r[1] == DKS_HOST and r[3] == "200" and r[4] == str(DKS_SIZE_OBSERVED)]
    add("C08b", "DKS extract holds the JPY and EUR 3m and 1y rows; the full body was deleted and its sha256 is in the fetch log",
        "4 series of more than 1000 rows; one logged full body", "%s; logged full bodies: %d" % (", ".join("%s %s %d" % (k[0], k[1], n) for k, n in sorted(have.items())), len(full)),
        "PASS" if len(have) == 4 and all(n > 1000 for n in have.values()) and full else "FAIL")
    tenors = [ledger_cell(ledger, EURO_HEADLINE_START, s, "3m") for s in ("sofr_ois", "estr_ois", "xccy_eurusd")]
    anc = c["anchor"]
    add("C09", "Ledger monthly cells: the file exists, every median has n >= 10, the euro 3m cells exist for 2024-10, the yen anchor month is recorded",
        "all four", "file read (%d cells); euro 2024-10 3m cells %s; yen anchor %s" % (len(ledger), "present" if all(tenors) else "MISSING", anc),
        "PASS" if all(tenors) and anc else "FAIL")
    # C10: the reviewer's real-data pins
    pin_rows = {p["pair"]: p for p in c["panels"]["yen"] + c["panels"]["euro"] if p["date"] == D("2026-10-15")}
    for pair, g, h in (("yen", -2.766265, 2.333735), ("euro", -1.501968, 3.598032)):
        r = pin_rows.get(pair)
        ok = r is not None and r["D"] == 92 and close(r["gap_A_hist"], g, 1e-6) and close(r["h_A_hist"], h, 1e-6)
        add("C10-" + pair, "A_hist on 2026-10-15 with D = 92 (the reviewer's re-derivation)", "gap %s, h %s" % (g, h),
            "missing" if r is None else "gap %s, h %s, D %d" % (f(r["gap_A_hist"], 6), f(r["h_A_hist"], 6), r["D"]), "PASS" if ok else "FAIL")
    # C11: alignment triples
    tona_s, jgb_s, estr_s = RateSeries(inp.tona), RateSeries({d: v for d, v in inp.jgb.items() if v is not None}), RateSeries(inp.estr)
    got = [triple(D(d), tona_s, jgb_s, estr_s) for d, _, _ in EXPECTED_TRIPLES]
    ok = all((iso(a), iso(b), iso(e)) == t for (a, b, e), t in zip(got, EXPECTED_TRIPLES))
    add("C11", "Alignment triples (d / Tokyo date / TARGET date)", "; ".join(" / ".join(t) for t in EXPECTED_TRIPLES),
        "; ".join("%s / %s / %s" % (iso(a), iso(b), iso(e)) for a, b, e in got), "PASS" if ok else "FAIL")
    # C12: staleness against the as-of date (the last logged retrieval), not the clock
    def age(name, last, limit):
        a = (asof - last).days if last else None
        add("C12-" + name, "%s is no older than %d days at the as-of date %s" % (name, limit, asof), "<= %d" % limit,
            "latest %s, %s days" % (iso(last), a), age_flag(asof, last, limit))
    age("SOFR", max(inp.sofr), 7)
    age("EFFR", max(inp.effr), 7)
    age("euro short-term rate", max(inp.estr), 7)
    age("TONA", max(inp.tona), 7)
    age("Treasury", max(inp.tsy), 7)
    age("MoF current month", max(d for d, v in inp.jgb.items() if v is not None), 7)
    age("ECB yield curve", max(inp.aaa), 7)
    lm = c["ledger_mtime"]
    add("C12-ledger", "ledger monthly file is no older than 14 days at the as-of date", "<= 14", "file dated %s, %s days" % (iso(lm), None if lm is None else (asof - lm).days),
        age_flag(asof, lm, 14))
    # C13: the Bund against the ECB AAA curve, a statistic only
    by = {}
    for d, v in inp.bbk.items():
        if d in inp.aaa:
            by.setdefault(month_key(d), []).append(inp.aaa[d] - v)
    mm = {m: statistics.median(v) for m, v in by.items() if len(v) >= 10}
    if mm:
        add("C13", "Bund 10-year against the ECB AAA 10-year (INFO): the median of the monthly medians of AAA minus Bund", "statistic only",
            "median %s pp over %d months (min %s in %s, max %s in %s)" % (f(statistics.median(mm.values()), 3), len(mm), f(min(mm.values()), 3),
                                                                           min(mm, key=mm.get), f(max(mm.values()), 3), max(mm, key=mm.get)), "INFO")
    # C15: unexplained gaps in the published rates
    gaps = {n: unexplained_gaps(s.dates, ccy) for n, s, ccy in (("SOFR", RateSeries(inp.sofr), "USD"), ("TONA", tona_s, "JPY"), ("euro short-term rate", estr_s, "EUR"))}
    add("C15", "gaps of more than 4 calendar days between published rates that KNOWN_CLOSURES do not explain", "none",
        "; ".join("%s %d%s" % (n, len(g), " (" + ", ".join("%s to %s" % (a, b) for a, b in g[:3]) + ")" if g else "") for n, g in gaps.items()),
        "PASS" if not any(gaps.values()) else "WARN")
    for (form, ten), (st, med, n) in sorted(c["gate"].items(), key=lambda kv: (kv[0][1], kv[0][0])):
        add("C17-%s-%s" % (form, ten), "post-registration bug fix of 19 Oct 2026 (ledger monthly stage, exact index-name list): gate median in bp, %s form, %s hedge"
            % (form, ten), "before the fix %s" % f(PRE_FIX_GATE[(form, ten)], 3), "after the fix %s (%s)" % (f(med, 3), st), "INFO")
    ck.sort(key=lambda r: r[0])
    return ck


def pins_rows(inp):
    D = dt.date.fromisoformat
    rows = []
    for d in ("2024-03-21", "2026-09-18", "2026-10-15"):
        rows.append(["U.S. Treasury", "10 Yr par yield", d, f(inp.tsy[D(d)], 2), "percent"])
    for d in ("2024-03-22", "2026-09-18", "2026-10-01"):
        rows.append(["MoF Japan", "10Y constant-maturity yield", d, f(inp.jgb[D(d)], 3), "percent"])
    for d in ("2018-04-02", "2026-10-15"):
        rows.append(["NY Fed", "SOFR", d, f(inp.sofr[D(d)], 2), "percent"])
    rows.append(["NY Fed", "EFFR", "2026-10-15", f(inp.effr[D("2026-10-15")], 2), "percent"])
    rows.append(["NY Fed", "SOFR Index", "2026-10-16", f(inp.sofrai[D("2026-10-16")], 8), "index"])
    for d in ("2019-10-01", "2026-10-16"):
        rows.append(["ECB", "euro short-term rate", d, f(inp.estr[D(d)], 3), "percent"])
    rows.append(["ECB", "compounded euro short-term rate index", "2026-10-19", f(inp.estr_ci[D("2026-10-19")], 8), "index"])
    rows.append(["ECB", "AAA 10-year, semiannual par recomputed from the parameters", "2026-09-18", f(inp.aaa[D("2026-09-18")], 6), "percent"])
    for d in ("2018-01-04", "2026-10-15"):
        rows.append(["Bank of Japan", "TONA (call rate, uncollateralised overnight, average)", d, f(inp.tona[D(d)], 3), "percent"])
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# formatting the files
# ------------------------------------------------------------------------------------------------------------------------
def monthly_text_rows(rows, nd=6, nd_bp=3):
    out = []
    for r in rows:
        out.append([r["month"], r["pair"], r["variant"], r["role"], str(r["n_days"]), str(r["partial"]), str(r["qe"]), f(r["ust10"], nd), f(r["home10"], nd),
                    f(r["rate_gap_term"], nd), f(r["basis_term"], nd), f(r["carry"], nd), f(r["pickup"], nd), f(r["form_gap_bp"], nd_bp), r["basis_tenor"],
                    f(r["hedge_days_mean"], 3), "" if r["n_ois_us"] is None else str(r["n_ois_us"]), "" if r["n_ois_home"] is None else str(r["n_ois_home"]),
                    "" if r["n_basis"] is None else str(r["n_basis"])])
    return out


def panel_text_rows(panel):
    out = []
    for r in panel:
        out.append([iso(r["date"]), r["pair"], iso(r["leg_date"]), f(r["ust10"], 6), f(r["home10"], 6), f(r["r_us"], 6), f(r["r_us_rt"], 6), f(r["r_effr"], 6),
                    f(r["r_home"], 6), f(r["r_home_rt"], 6), str(r["D"]), f(r["h_A_rt"], 9), f(r["h_A_hist"], 9), f(r["h_A_effr"], 9), f(r["h_B"], 9),
                    f(r["gap_A_rt"], 9), f(r["gap_A_hist"], 9), f(r["gap_B"], 9), f(r["h_dks"], 9), str(r["qe"]), r["drop"]])
    return out


def refs_text_rows(refs, committed):
    out = []
    for r in refs:
        yen = r["pair"] == "yen"
        bv, gp = (None, None) if (committed and yen) else (r["build_value"], r["gap_bp"])
        out.append([r["ref_id"], r["source"], r["ref_date"], r["pair"], r["form"], r["tenor"], f(r["published"], 4), f(r["rounding_bp"], 1), f(bv, 6), f(gp, 3),
                    f(r["tolerance"], 1), r["status"], r["note_com"] if (committed and yen and r.get("note_com")) else r["note"]])
    return out


def gate_line(gate):
    return "; ".join("%s %s %s" % (k[0], k[1], v[0]) for k, v in sorted(gate.items()))


ECB_LABEL = "euro 10-year yield: derived from ECB statistics (recomputed on a semiannual basis from the ECB AAA Svensson parameters)"


def committed_source(fetch_rows, what):
    return source_line(fetch_rows, HOST_ALLOW - {DKS_HOST, BBK_HOST}, what)


def render_texts(c):
    """The committed texts and the cache texts, rendered from the context. -> (committed {name: text}, cache {name: text})"""
    rows = c["mrows"]
    euro = [r for r in rows if r["pair"] == "euro"]
    fr = c["fetch_rows"]
    com, cache = {}, {}
    com["monthly.csv"] = render_csv("monthly.csv", monthly_text_rows(euro), committed_source(fr, "euro rows only; one row per month and variant; monthly means of daily values "
                                                                                          "(10-year yields, diagnostics) and the ledger's monthly medians (DTCC, THE_ASK.md E-024); " + ECB_LABEL))
    com["yen_summary.csv"] = render_csv("yen_summary.csv", c["yen_rows"], committed_source(fr, "yen annual means of complete months and two anchor months only (Bank of Japan "
                                                                                          "terms); the credit is in each row"))
    com["summary.csv"] = render_csv("summary.csv", c["summary_com"], "# source: computed by bin/hedged_ust_yield.py from the files of this folder; yen values are blank by design")
    com["references.csv"] = render_csv("references.csv", refs_text_rows(c["refs"], True), "# source: published references named in each row; build values are this folder's "
                                       "computation; yen build values and gaps are blank by design (Bank of Japan terms)")
    com["checks.csv"] = render_csv("checks.csv", c["checks"], "# source: input checks of bin/hedged_ust_yield.py build against the files fetched (see fetch_log.csv)")
    com["pins.csv"] = render_csv("pins.csv", c["pins"], committed_source(fr, "at most five pinned values per source"))
    cache["daily_panel.csv"] = render_csv("daily_panel.csv", panel_text_rows(c["panels"]["yen"] + c["panels"]["euro"]), committed_source(fr, "CACHE ONLY, never committed"))
    cache["monthly_all.csv"] = render_csv("monthly.csv", monthly_text_rows(rows, 12, 6), committed_source(fr, "CACHE ONLY, never committed: both pairs"))
    cache["references_full.csv"] = render_csv("references.csv", refs_text_rows(c["refs"], False), "# source: CACHE ONLY, never committed: yen build values included")
    cache["summary_full.csv"] = render_csv("summary.csv", c["summary_full"], "# source: CACHE ONLY, never committed: yen values included")
    return com, cache


# ------------------------------------------------------------------------------------------------------------------------
# README and SOURCES
# ------------------------------------------------------------------------------------------------------------------------
NYF_NOTICE = ("The SOFR, EFFR and SOFR Index data are subject to the Terms of Use posted at newyorkfed.org. The New York Fed is not responsible for publication of "
              "the data by this project, does not sanction or endorse any particular republication, and has no liability for your use. The data here are modified "
              "(monthly means of daily values, and the hedged carry computed from them) and the modifications are this project's, not the New York Fed's. This "
              "project is not affiliated with the New York Fed, which does not sanction, endorse, or recommend any products or services offered by it. The SOFR "
              "data are calculated by the New York Fed using data provided under a license granted to it by DTCC Solutions LLC.")


def fmt(x, nd=3):
    return "n/a" if x is None else f(x, nd)


def render_readme(c):
    rows, L = c["mrows"], c["L"]
    h3 = sorted([r for r in rows if r["pair"] == "euro" and r["variant"] == "H3"], key=lambda r: r["month"])
    last = [r for r in h3 if not r["partial"]][-1] if [r for r in h3 if not r["partial"]] else None
    out = []
    w = out.append
    w("# FX-hedged 10-year Treasury: the rolling 3-month carry\n")
    w("This folder measures the rolling 3-month carry of a currency-hedged 10-year US Treasury for euro-based and yen-based investors, month by month, and sets it "
      "against the 10-year government yield at home. %s\n" % REQUIRED_SENTENCE)
    w("## The latest result\n")
    w("**Euro-based investor**, headline variant H3 (the locked 3-month forward built from overnight-index swap rates and the 3-month cross-currency basis). Every "
      "figure is in percent or percentage points; a month marked `partial` is incomplete. `pickup` is the hedged carry minus the euro 10-year yield "
      "(ECB AAA curve); it is a comparison of two yields, not a gain anyone received. Months with no row had fewer than 10 swap prints in one of the three cells the "
      "headline needs (see `n_basis` and the ledger). The October 2024 cells use prints from 14 October only, the first day in the archive. No FX forward quote is used: "
      "the forward rate is built from the overnight-index swap rates and the basis, so the spot rate cancels.\n")
    w("| month | 10y Treasury | euro 10y | rate-gap term | basis term | hedged carry | pickup |")
    w("|---|---:|---:|---:|---:|---:|---:|")
    for r in h3:
        w("| %s%s | %s | %s | %s | %s | %s | %s |" % (r["month"], " (partial)" if r["partial"] else "", f(r["ust10"], 3), f(r["home10"], 3), f(r["rate_gap_term"], 3),
                                                     f(r["basis_term"], 3), f(r["carry"], 3), f(r["pickup"], 3)))
    w("")
    yr = c["yen_rows"]
    w("**Yen-based investor**, annual means of complete months (the Bank of Japan's terms keep monthly yen figures out of this folder; see below). Variant H3 and the "
      "diagnostics (A_hist: the dated overnight rates, no basis; B: the realised overnight rates) are shown where they exist.\n")
    w("| period | variant | hedged carry | pickup | rate-gap term | basis term | months |")
    w("|---|---|---:|---:|---:|---:|---:|")
    keyed = {}
    for per, var, stat, val, _ in yr:
        keyed.setdefault((per, var), {})[stat] = val
    vorder, porder = {"H3": 0, "A_hist": 1, "B": 2}, lambda p: (p.startswith("anchor_"), p.startswith("L_"), p)
    for (per, var), d in sorted(keyed.items(), key=lambda kv: (vorder.get(kv[0][1], 9), porder(kv[0][0]))):
        if var in ("H3", "A_hist", "B"):
            w("| %s | %s | %s | %s | %s | %s | %s |" % (per, var, d.get("hedged_carry_mean", ""), d.get("pickup_mean", ""), d.get("rate_gap_term_mean", ""),
                                                      d.get("basis_term_mean", ""), d.get("n_months", "")))
    w("")
    w("Validation: the build was compared with hedged yields published by Ginnie Mae, TD Economics and BlackRock (`references.csv`). The test is whether the median "
      "gap between this build and the published figures stays within 25 basis points (0.25 percentage points), separately for the two forms (H and P) and the two "
      "hedge lengths (3 months and 1 year). Results: %s. The rules, including how whole-percent quotes are scored, "
      "are in the table's `note` column.\n" % gate_line(c["gate"]))
    w("**Correction.** %s\n" % BUGFIX_NOTE)
    w("## Columns\n")
    w("`monthly.csv` (euro rows only):\n")
    for col, txt in (("month", "calendar month, YYYY-MM"), ("pair", "`euro`"), ("variant", "H3 and P3 (3-month, headline and plain form), H12 and P12 (1-year), and the "
                     "diagnostics A_rt, A_hist, A_effr (spot overnight rates) and B (realised overnight rates)"),
                    ("role", "HEADLINE, MAIN or DIAGNOSTIC"), ("n_days", "Treasury business days in the month's means"),
                    ("partial", "1 if the month's last business day is missing for any leg"),
                    ("qe_turn_early", "1 if the month is March, June, September or December, so that the quarter end falls in the first 30 days of the hedge windows"),
                    ("ust10_pct", "the 10-year Treasury par yield (semiannual), monthly mean"),
                    ("home10_pct", "the euro 10-year yield, derived from ECB statistics (recomputed on a semiannual basis), monthly mean"),
                    ("rate_gap_term_pp", "the contribution to the hedged carry of the gap between the dollar and the euro short rate over the hedge"),
                    ("basis_term_pp", "the contribution to the hedged carry of the cross-currency basis (zero for the diagnostics)"),
                    ("hedged_carry_pct", "the 10-year Treasury yield plus the two terms above, an exact sum of those columns"),
                    ("pickup_pp", "the hedged carry minus `home10_pct`, an exact difference of those columns"), ("form_gap_bp", "100 x (H - P), in bp, on the H and P rows"),
                    ("basis_tenor", "`3m`, `1y` or `none`"), ("hedge_days_mean", "the mean number of days in the hedge windows of the month's business days"),
                    ("n_ois_us, n_ois_home, n_basis", "the number of prints behind the month's SOFR, euro short-term-rate and cross-currency cells")):
        w("- `%s`: %s." % (col, txt))
    w("\n`yen_summary.csv`: `period`, `variant`, `statistic`, `value`, `credit`. Each value is the mean of the complete months in the period. A `period` of `2023`, "
      "`2024` or `2025` is that calendar year; `2026_ytd` is January 2026 to the latest complete month; `anchor_YYYY-MM` is the single first month in which the yen "
      "headline exists (the first month with 10 or more swap prints in each of the three cells it needs), here `anchor_%s`; and `L_YYYY-MM` is the latest complete "
      "month, here `L_%s`.\n" % (c["anchor"], c["L"]))
    w("`summary.csv`: the descriptive "
      "questions; yen values are blank and only a `notable` flag is given. `references.csv`: the published figures the build is compared with. `checks.csv`, `pins.csv` "
      "and `fetch_log.csv`: input checks, pinned values and the request log.\n")
    w("## Why yen appears only as annual figures\n")
    w("The Bank of Japan's copyright page allows copying with credit but excludes commercial copying, and its API notice asks for a prescribed credit. This project "
      "therefore commits no monthly series built from the Bank's TONA: the yen rows of `yen_summary.csv` are annual means of complete months plus two anchor "
      "months, and the yen monthly path is kept in a local cache. %s\n" % BOJ_CREDIT)
    w("## Defined terms\n")
    for t, d in (("Swap print and swap tape", "a print is one reported swap trade. The swap tape is the public record of such trades that US rules require (the "
                  "Depository Trust and Clearing Corporation publishes it); the ledger in `data/swap_tape/` turns the tape into monthly medians, which are the only "
                  "place the swap rates and the basis enter this folder."),
                 ("Hedging cost", "what a rolled currency hedge costs per year: the gap between the dollar and the home short rate over the hedge tenor, plus any premium "
                  "that dollar borrowers pay on top of it. The rate-gap term and the basis term are minus that cost."),
                 ("Cross-currency basis", "the spread on the yen or euro overnight-rate leg of a currency swap against flat SOFR, in bp, as on the US-reported swap tape. "
                  "A negative basis is a premium to borrow dollars and lowers the carry. It is a median of swap prints and is not the price of FX-swap forward points."),
                 ("Pickup", "the hedged carry minus the 10-year government yield at home."),
                 ("OIS", "an overnight-index swap: a fixed rate exchanged for the compounded overnight rate. The 3-month and 1-year fixed rates are used here as the "
                  "market's price of the overnight rate over the hedge window."),
                 ("Rolling carry", "the yield plus the annualised gain or loss of a hedge that is renewed every 3 months (or every year for H12 and P12), at the month's "
                  "prices. It is not the return from holding a hedged bond to maturity, which depends on ten years of future short rates."),
                 ("Bond-basis form (H) and plain-subtraction form (P)", "H converts the forward rate with day counts and compounding before it is added to the yield "
                  "(a semiannual rate, like the yields); P subtracts the quoted rate gap and adds the basis as quoted. `form_gap_bp` is their difference.")):
        w("- **%s.** %s%s" % (t, d[0].upper(), d[1:]))
    w("")
    w("## One worked row\n")
    if last:
        w("`monthly.csv`, euro, H3, %s: 10-year Treasury %s + rate-gap term %s + basis term %s = hedged carry %s. Minus the euro 10-year yield %s, the pickup is %s. "
          "The rate-gap term uses the %d SOFR and %d euro short-term-rate swap prints and the basis the %d cross-currency prints of the month (ledger, DTCC).\n"
          % (last["month"], f(last["ust10"], 6), f(last["rate_gap_term"], 6), f(last["basis_term"], 6), f(last["carry"], 6), f(last["home10"], 6), f(last["pickup"], 6),
             last["n_ois_us"], last["n_ois_home"], last["n_basis"]))
    w("## Provenance and terms\n")
    w("- **U.S. Treasury** (home.treasury.gov): daily par yield curve, 10-year; a US government work.")
    w("- **Ministry of Finance Japan** (www.mof.go.jp): the JGB 10-year; Public Data License 1.0, attribution given.")
    w("- **European Central Bank** (data-api.ecb.europa.eu): the euro short-term rate and its compounded index, and the AAA yield-curve parameters. The euro 10-year yield "
      "in this folder is derived from ECB statistics (recomputed on a semiannual basis) and is not an ECB publication.")
    w("- **Federal Reserve Bank of New York** (markets.newyorkfed.org): SOFR, EFFR and the SOFR Index. %s" % NYF_NOTICE)
    w("- **Bank of Japan** (www.stat-search.boj.or.jp): TONA. %s" % BOJ_CREDIT)
    w("- **Du, Keerati and Schreger** panel and the **Deutsche Bundesbank** series are used for checks only and stay in the local cache.")
    w("- **DTCC.** %s" % E024_TEXT)
    w("")
    text = "\n".join(out) + "\n"
    guard_text("README.md", text)
    return text


def render_sources(c):
    fr = c["fetch_rows"]
    out = ["# Sources and terms for data/hedged_ust_yield/\n",
           "Each source below is public and free. Retrieval dates are in `fetch_log.csv`. The committed files are derived statistics; raw downloads, the daily panel and the "
           "yen monthly rows are in a gitignored cache. %s\n" % REQUIRED_SENTENCE]
    src = (("U.S. Treasury", "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/", "daily par yield curve (10 Yr, read by column name)",
            "US government work; no restriction.", "U.S. Department of the Treasury, Daily Treasury Par Yield Curve Rates."),
           ("Ministry of Finance Japan", "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/", "JGB yields (jgbcme_all.csv and jgbcme.csv), 10Y",
            "Public Data License 1.0 per the notice page: commercial use allowed with attribution; numerical data are outside copyright.",
            "Ministry of Finance Japan, Interest Rate (JGB), https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/"),
           ("European Central Bank", "https://data-api.ecb.europa.eu/", "YC (AAA Svensson parameters) and EST (euro short-term rate, compounded index)",
            "Free use if the ECB is cited and the data appear accurately; modifications must be stated. The euro 10-year yield is derived (recomputed on a semiannual "
            "basis) and is labelled as such.", "European Central Bank, euro area yield curves and the euro short-term rate (EST), data-api.ecb.europa.eu."),
           ("Federal Reserve Bank of New York", "https://markets.newyorkfed.org/", "SOFR, EFFR, SOFR Index", "https://www.newyorkfed.org/privacy/termsofuse: use and "
            "distribution allowed with the reference-rate notice; modified content must be labelled. " + NYF_NOTICE, "Federal Reserve Bank of New York, Reference Rates."),
           ("Bank of Japan", "https://www.stat-search.boj.or.jp/", "TONA, FM01 STRDCLUCON", "Copying allowed with the Bank credited; commercial copying excluded. API notice "
            "(https://www.stat-search.boj.or.jp/info/api_notice_en.pdf): a user who releases a service that uses the API should notify the Bank's Research and Statistics "
            "Department and show the credit. " + BOJ_CREDIT + " Whether a public repository counts as a service is a question for the principal; no notice has been sent.",
            "Bank of Japan, Time-Series Data Search."),
           ("Du, Keerati and Schreger", "https://jschreger.s3.us-east-2.amazonaws.com/cip_dataset_v4.csv", "a check only: all-in forward premium (rho), 3-month",
            "The data page asks for three citations; redistribution is not stated, so the panel stays in the local cache and only overlap statistics are committed.",
            "Du, Keerati and Schreger, government-bond covered interest parity deviations dataset (version 4)."),
           ("Deutsche Bundesbank", "https://api.statistiken.bundesbank.de/", "a check only: Svensson 10-year yield", "Terms not read; a statistic only.",
            "Deutsche Bundesbank, BBSIS."),
           ("DTCC (through the swap-tape ledger)", "https://pddata.dtcc.com", "the monthly OIS and cross-currency cells in data/swap_tape/monthly_short_tenor.csv",
            E024_TEXT, "DTCC Public Price Dissemination, CFTC cumulative interest-rate reports."))
    for name, url, what, lic, cite in src:
        out.append("- **%s.** %s. Series: %s. Licence: %s Cite as: %s" % (name, url, what, lic, cite))
    out.append("\n## Column provenance\n")
    for col, prov in (("ust10_pct", "U.S. Treasury 10 Yr par yield, monthly mean of daily values (US government work)."),
                      ("home10_pct", "euro rows: ECB AAA Svensson parameters, 10-year par yield recomputed on a semiannual basis, monthly mean (derived from ECB statistics)."),
                      ("rate_gap_term_pp, basis_term_pp, hedged_carry_pct, pickup_pp, form_gap_bp", "computed here from the monthly OIS and cross-currency medians "
                       "of the swap-tape ledger (DTCC), the Treasury and ECB yields, and, for the diagnostics, SOFR, EFFR and the euro short-term rate."),
                      ("n_ois_us, n_ois_home, n_basis", "counts from the ledger's monthly cells (DTCC)."),
                      ("yen_summary.csv value", "annual means of the above for the yen pair, with TONA (Bank of Japan) among the inputs; the credit is in each row."),
                      ("references.csv published", "the figures named in each row's source; build_value is this folder's computation."),
                      ("pins.csv", "single published values, at most five per source.")):
        out.append("- `%s`: %s" % (col, prov))
    text = "\n".join(out) + "\n"
    guard_text("SOURCES.md", text)
    return text




# ------------------------------------------------------------------------------------------------------------------------
# build: the whole pipeline, offline
# ------------------------------------------------------------------------------------------------------------------------
def read_frozen_L(out_dir):
    """L is the latest complete month at the FIRST build, kept in the `L` row of summary.csv; later builds read it and never change it."""
    if M("l_recomputed"):
        return None
    _, rows = read_csv_rows(os.path.join(out_dir, "summary.csv"))
    for r in rows:
        if len(r) >= 3 and r[2] == "L":
            return r[1]
    return None


def asof_date(fetch_rows):
    ds = retrieval_dates(fetch_rows, HOST_ALLOW)
    if not ds:
        raise DataError("fetch_log.csv has no logged retrieval; run `fetch` first")
    return dt.date.fromisoformat(ds[-1])


def compute(cache, ledger_path, out_dir):
    inp = load_inputs(cache)
    ledger = read_ledger(ledger_path)
    fetch_rows = read_fetch_log(out_dir)
    asof = asof_date(fetch_rows)
    tsy_dates = sorted(inp.tsy)
    panels = {"yen": build_panel(inp, "yen"), "euro": build_panel(inp, "euro")}
    mrows, status = monthly_rows(panels, ledger, tsy_dates)
    L = read_frozen_L(out_dir) or latest_complete(status)
    if L is None:
        raise DataError("no complete month")
    refs, gate = build_references(inp, ledger, tsy_dates, mrows)
    v5 = v5_results(panels, mrows)
    refs = [r for r in refs if not r["ref_id"].startswith("GATE")] + v5_ref_rows(v5) + [r for r in refs if r["ref_id"].startswith("GATE")]
    label = "L_" + L
    s4 = section4(mrows, status, ledger, L, v5, label)
    s_com, s_full = summary_texts(s4, L, label)
    mt = os.path.getmtime(ledger_path)
    c = dict(inp=inp, ledger=ledger, fetch_rows=fetch_rows, asof=asof, tsy_dates=tsy_dates, panels=panels, mrows=mrows, status=status, L=L, refs=refs, gate=gate,
             v5=v5, s4=s4, summary_com=s_com, summary_full=s_full, yen_rows=yen_summary_rows(mrows, status, L, ledger), pins=pins_rows(inp),
             anchor=yen_anchor(ledger), ledger_mtime=dt.datetime.fromtimestamp(mt, dt.timezone.utc).date(), jgb_overlap=inp.jgb_overlap, jgb_hist_end=inp.jgb_hist_end, jgb_cur_start=inp.jgb_cur_start, tona_nulls=inp.tona_nulls,
             checks=[])
    return c


def texts_digest(c):
    com, cache = render_texts(c)
    return {n: sha256_of(t.encode("utf-8")) for n, t in sorted(list(com.items()) + list(cache.items())) if n != "checks.csv"}


def finish(c):
    """Checks, the determinism check C14, the leak guard, the README and SOURCES. -> (committed texts, cache texts, failed list)"""
    ck = build_checks(c)
    c["checks"] = []
    d1, d2 = texts_digest(c), texts_digest(c)
    if M("render_unstable"):
        d2 = dict(d2, **{"monthly.csv": "x"})
    ck.append(["C14", "Fixed output: rendering every file twice gives the same sha256 (a second `build` is compared on disk by the caller)", "identical",
               "identical (%d files)" % len(d1) if d1 == d2 else "DIFFERENT", "PASS" if d1 == d2 else "FAIL"])
    c["checks"] = sorted(ck, key=lambda r: r[0])
    com, cache = render_texts(c)
    com["README.md"] = render_readme(c)
    com["SOURCES.md"] = render_sources(c)
    problems = leak_guard({n: t for n, t in com.items() if n.endswith(".csv")}, raw_monthly_means(c["inp"]))
    ck2 = list(c["checks"]) + [["C16", "Licence and leak guard (section 7): no yen monthly row, no raw-series column, no daily date column, no DKS column, caps on yen and pins",
                                "no problem", "; ".join(problems) if problems else "no problem", "FAIL" if problems else "PASS"]]
    c["checks"] = sorted(ck2, key=lambda r: r[0])
    com, cache = render_texts(c)
    com["README.md"] = render_readme(c)
    com["SOURCES.md"] = render_sources(c)
    failed = [r[0] for r in c["checks"] if r[4] == "FAIL"] + ["GATE_%s_%s" % k for k, v in c["gate"].items() if v[0] == "FAIL"]
    return com, cache, failed


def write_outputs(com, cache_texts, out_dir, cache, failed):
    target = os.path.join(out_dir, "_FAILED") if (failed and not M("failed_to_committed")) else out_dir
    for n, t in com.items():
        write_text(os.path.join(target, n), t)
    for n, t in cache_texts.items():
        write_text(os.path.join(cache, n), t)
    return target


def report(c, failed, target):
    L = ["", "== validation gate (section 5), median |build - published| in bp per form and tenor group"]
    for (form, ten), (st, med, n) in sorted(c["gate"].items(), key=lambda kv: (kv[0][1], kv[0][0])):
        L.append("   GATE %s %s: %s  (median %s bp over %d points, tolerance %g)" % (form, ten, st, fmt(med, 2), n, GATE_TOL_BP))
    L.append("   each reference point (full table in the cache, references_full.csv):")
    for r in c["refs"]:
        if r["ref_id"].startswith("GATE"):
            continue
        L.append("   %-8s %-5s %-4s %-5s %-8s published %-7s build %-9s gap %-8s %s" % (r["ref_id"], r["pair"], r["form"], r["tenor"], r["ref_date"], fmt(r["published"], 4),
                                                                                    fmt(r["build_value"], 4), fmt(r["gap_bp"], 2), r["status"]))
    L.append("")
    L.append("== euro, H3 (headline) by month: month n  10y  euro10y  rate_gap  basis  carry  pickup")
    for r in sorted((r for r in c["mrows"] if r["pair"] == "euro" and r["variant"] == "H3"), key=lambda r: r["month"]):
        L.append("   %s%s n=%2d  %.3f %.3f %+.3f %+.3f  %.3f  %+.3f" % (r["month"], "*" if r["partial"] else " ", r["n_days"], r["ust10"], r["home10"], r["rate_gap_term"],
                                                                           r["basis_term"], r["carry"], r["pickup"]))
    L.append("== yen summary (cache values shown here; the committed file carries the same annual figures)")
    for per, var, stat, val, _ in c["yen_rows"]:
        if stat in ("hedged_carry_mean", "pickup_mean", "n_months"):
            L.append("   %-14s %-7s %-18s %s" % (per, var, stat, val))
    L.append("== checks")
    for r in c["checks"]:
        L.append("   %-10s %-5s %s" % (r[0], r[4], r[3][:150]))
    L.append("== section 4 (full values)")
    for q, pair, var, stat, v, nb in c["s4"]:
        L.append("   %s %-5s %-6s %-40s %-12s %s" % (q, pair, var, stat, f(v, 4) if isinstance(v, float) else v, nb))
    L.append("")
    L.append("L = %s; as-of %s; failed: %s; wrote the committed files to %s" % (c["L"], c["asof"], ", ".join(failed) if failed else "none", tilde(target)))
    return L


def run_build(a):
    t0 = time.time()
    cache = check_cache(a.cache, out_dir=a.out)
    c = compute(cache, a.ledger, a.out)
    com, cache_texts, failed = finish(c)
    target = write_outputs(com, cache_texts, a.out, cache, failed)
    print("\n".join(report(c, failed, target)))
    print("(%.1f s)" % (time.time() - t0))
    if failed:
        print("FAIL: %s. Outputs went to %s; the committed files were left alone." % (", ".join(failed), tilde(target)), file=sys.stderr)
        return 1
    return 0




# ------------------------------------------------------------------------------------------------------------------------
# selftest: synthetic data only. Every guard of the spec's section 9 (G1-G19) has a test; each mutant (a deliberately broken variant, switched on in
# this process only) must make its test fail. A mutant not caught is a failure.
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


class FakeClock:
    def __init__(self, t=1_000_000.0):
        self.t = t

    def wall(self):
        return self.t

    def sleep(self, s):
        self.t += s


D_ = dt.date.fromisoformat


def t_g1(ck):
    r = headline(4.5, 4.3, 0.5, -20.0, 92, "yen")
    ck.close("yen 3m fixture: H", r["H"], 0.4144953188, 1e-9)
    ck.close("yen 3m fixture: rate_gap_term", r["rate_gap_term"], -3.8851920011, 1e-9)
    ck.close("yen 3m fixture: basis_term", r["basis_term"], -0.2003126801, 1e-9)
    ck.close("yen 3m fixture: P", r["P"], 0.50, 1e-9)
    ck.close("yen 3m fixture: form gap (bp)", r["form_gap_bp"], -8.5504681189, 1e-6)
    ck.ok("a negative basis lowers h (H below h0)", r["H"] < r["h0"], "H %r h0 %r" % (r["H"], r["h0"]))
    e = headline(4.5, 4.3, 2.0, -5.0, 92, "euro")
    ck.close("euro 3m fixture: H", e["H"], 2.0972732816, 1e-9)
    ck.close("euro 3m fixture: P", e["P"], 2.15, 1e-9)
    y1, e1 = headline(4.5, 4.0, 0.8, -15.0, 365, "yen"), headline(4.5, 4.0, 2.1, -3.0, 365, "euro")
    ck.close("yen 1y fixture: H", y1["H"], 1.1256986972, 1e-9)
    ck.close("yen 1y fixture: P", y1["P"], 1.15, 1e-9)
    ck.close("euro 1y fixture: H", e1["H"], 2.5680226188, 1e-9)
    ck.close("euro 1y fixture: P", e1["P"], 2.57, 1e-9)


def t_g2(ck):
    r = headline(4.5, 4.3, 0.5, -20.0, 92, "yen")
    ck.ok("o_us above o_home: the rate-gap term is negative in H and in P", r["rate_gap_term"] < 0 and r["p_gap"] < 0)
    h, gap = spot_h(4.5, 4.3, 0.5, 92, "yen")
    c = 100.0 * 365.0 * (math.log(1 + 0.5 / (100 * 365.0)) - math.log(1 + 4.3 / (100 * 360.0)))
    want = 200.0 * (math.exp((200.0 * math.log(1 + 4.5 / 200.0) + c) / 200.0) - 1.0) - 4.5
    ck.close("A: the gap is negative and equals the closed form", gap, want, 1e-9)
    h2, gap2 = spot_h(4.5, 0.5, 4.3, 92, "yen")
    ck.ok("home above the dollar: positive", gap2 > 0)
    ck.close("P: gap = -(o_us - o_home)", plain_p(4.5, 4.3, 0.5, 0.0)[1], -3.8, 1e-12)


def t_g3(ck):
    ck.eq("day bases: SOFR 360, TONA 365, euro short-term rate 360", (day_basis("us"), day_basis("yen"), day_basis("euro")), (360.0, 365.0, 360.0))
    r = headline(4.5, 4.3, 0.5, -20.0, 92, "yen")
    ck.close("yen H on the 360 / 365 / 360 convention", r["H"], 0.4144953188, 1e-9)
    ck.close("simple interest in G: 1 + o D / (100 B), TONA", g_simple(0.5, 92, "yen"), 1 + 0.5 * 92 / 36500.0, 1e-15)


def t_g4(ck):
    r = headline(4.5, 4.3, 0.5, -20.0, 92, "yen")
    ck.close("H is the bond-basis form (0.4144953188), not P (0.50)", r["H"], 0.4144953188, 1e-9)
    ck.ok("H and P differ on the fixture", abs(r["H"] - r["P"]) > 0.05)
    ck.close("P uses the quoted rates, no day-count change", r["P"], 4.5 - (4.3 - 0.5) - 0.2, 1e-12)


def t_g5(ck):
    ck.eq("D examples: 2025-11-30 -> 90, 2026-01-31 -> 89, 2024-02-29 -> 90", (hedge_days(D_("2025-11-30"), 3), hedge_days(D_("2026-01-31"), 3),
                                                                             hedge_days(D_("2024-02-29"), 3)), (90, 89, 90))
    ck.eq("D at 12 months: 2024-02-29 -> 2025-02-28 = 365", hedge_days(D_("2024-02-29"), 12), 365)
    r = headline(4.5, 4.3, 0.5, -20.0, 92, "yen")
    ck.close("H at D = 92 (a 90-day D would give 0.4139834352)", r["H"], 0.4144953188, 1e-9)
    ck.ok("D = 92 is used, not 90 (miss of 5.1e-4)", abs(r["H"] - 0.4139834352) > 1e-4)
    ledger = {}
    for s_, v in (("sofr_ois", 4.3), ("tona_ois", 0.5), ("xccy_jpyusd", -20.0)):
        ledger[("2026-01", s_, "3m")] = dict(n=12, median=v, status="ok")
    kept = [dict(ust10=4.5, home10=2.0)]
    rows = headline_rows("2026-01", "yen", kept, ledger, [D_("2026-01-30"), D_("2026-01-31")], 0, False)
    h3 = [x for x in rows if x["variant"] == "H3"]
    ck.eq("hedge_days_mean is the mean of the month's D (90 and 89)", h3[0]["hedge_days_mean"] if h3 else None, 89.5)
    h, gap = spot_h(4.5, 4.3, 0.5, 92, "yen")
    h2, gap2 = spot_h(4.5, 4.3, 0.5, 90, "yen")
    ck.close("A's annualisation cancels D (tolerance 1e-7)", gap, gap2, 1e-7)


def syn_calendar():
    """Fixture calendars for G6: Tokyo, TARGET and US business days, 2024-12 to 2026-06, with the closures the spec's triples rely on."""
    a, b = dt.date(2024, 12, 1), dt.date(2026, 6, 30)
    tokyo = lambda d: closure_day("JPY", d) or (d == D_("2025-12-31"))
    out = {"jp": [], "ea": [], "us": []}
    d = a
    while d <= b:
        if d.weekday() < 5:
            if not tokyo(d):
                out["jp"].append(d)
            if not closure_day("EUR", d):
                out["ea"].append(d)
            if (d.month, d.day) not in ((12, 25), (1, 1)):
                out["us"].append(d)
        d += dt.timedelta(days=1)
    return out


def syn_inputs(cal, tona_gap=None):
    inp = Inputs()
    inp.tsy = {d: 4.0 for d in cal["us"]}
    inp.sofr = {d: 4.00 + 0.01 * i for i, d in enumerate(cal["us"])}
    inp.effr = {d: 4.00 + 0.01 * i for i, d in enumerate(cal["us"])}
    jp = [d for d in cal["jp"] if not (tona_gap and tona_gap[0] <= d <= tona_gap[1])]
    inp.tona = {d: 0.50 + 0.001 * i for i, d in enumerate(jp)}
    inp.jgb = {d: 1.0 for d in jp}
    inp.estr = {d: 2.00 + 0.001 * i for i, d in enumerate(cal["ea"])}
    inp.aaa = {d: 2.5 for d in cal["ea"]}
    inp.dks = {}
    return inp


def t_g6(ck):
    cal = syn_calendar()
    tona_s, jgb_s, estr_s = RateSeries({d: 0.5 for d in cal["jp"]}), RateSeries({d: 1.0 for d in cal["jp"]}), RateSeries({d: 2.0 for d in cal["ea"]})
    for d, tk, ta in EXPECTED_TRIPLES:
        got = triple(D_(d), tona_s, jgb_s, estr_s)
        ck.eq("triple for %s (Tokyo %s, TARGET %s)" % (d, tk, ta), (iso(got[1]), iso(got[2])), (tk, ta))
    inp = syn_inputs(cal)
    yen = {r["date"]: r for r in build_panel(inp, "yen")}
    r = yen[D_("2025-01-02")]
    ck.eq("panel leg date on 2025-01-02 is the last Tokyo date, 2024-12-30", r["leg_date"], D_("2024-12-30"))
    prev_us = max(x for x in cal["us"] if x < D_("2025-01-02"))
    ck.close("A_hist reads the SOFR dated d", r["r_us"], inp.sofr[D_("2025-01-02")], 1e-12)
    ck.close("A_rt reads only the SOFR already published at the snapshot (dated before d)", r["r_us_rt"], inp.sofr[prev_us], 1e-12)
    prev_jp = max(x for x in inp.tona if x < r["leg_date"])
    ck.close("A_rt reads the TONA dated before the leg date", r["r_home_rt"], inp.tona[prev_jp], 1e-12)
    # Golden Week with a 10-day gap in the Tokyo leg: the stale rule drops the row
    inp2 = syn_inputs(cal, tona_gap=(D_("2026-04-28"), D_("2026-05-08")))
    y2 = {r["date"]: r for r in build_panel(inp2, "yen")}
    ck.eq("a 10-day Golden Week gap drops 2026-05-06 as stale_leg", y2[D_("2026-05-06")]["drop"], "stale_leg")
    ck.eq("a 5-day gap (the real Golden Week 2026) keeps 2026-05-06", yen[D_("2026-05-06")]["drop"], "")


def t_g7(ck):
    v = {D_("2026-01-05"): 4.30, D_("2026-01-06"): 4.31, D_("2026-01-07"): 4.32, D_("2026-01-08"): 4.33, D_("2026-01-09"): 4.40, D_("2026-01-12"): 4.40}
    s = RateSeries(v)
    ck.close("clipped at d + D: Mon 5 - Sat 10 Jan, G", s.compound(D_("2026-01-05"), D_("2026-01-10"), 360), 1.000601811483, 1e-12)
    ck.close("unclipped weekend inside the window: Mon 5 - Mon 12, G", s.compound(D_("2026-01-05"), D_("2026-01-12"), 360), 1.000846373146, 1e-12)
    ck.ok("a window that ends past the last rate is blank", s.compound(D_("2026-01-05"), D_("2026-01-20"), 360) is None)
    ck.ok("a window that starts before the first rate is blank", s.compound(D_("2026-01-02"), D_("2026-01-09"), 360) is None)
    ck.close("the window is [d, d + D): the rate dated d + D does not enter", s.compound(D_("2026-01-05"), D_("2026-01-09"), 360),
             (1 + 4.30 / 36000) * (1 + 4.31 / 36000) * (1 + 4.32 / 36000) * (1 + 4.33 / 36000), 1e-12)


def t_g8(ck):
    v = {D_("2026-01-05"): 4.30, D_("2026-01-06"): 4.31, D_("2026-01-07"): 4.32, D_("2026-01-08"): 4.33, D_("2026-01-09"): 4.40, D_("2026-01-12"): 4.40}
    s = RateSeries(v)
    ck.close("ARRC: the weekend is one period at Friday's rate (not compounded daily: 1.000846417984)", s.compound(D_("2026-01-05"), D_("2026-01-12"), 360),
             1.000846373146, 1e-12)
    ck.ok("not the simple sum either (1.000846111111)", abs(s.compound(D_("2026-01-05"), D_("2026-01-12"), 360) - 1.000846111111) > 1e-8)
    idx = {D_("2026-01-09"): 1.20000000, D_("2026-01-12"): 1.20000000 * (1 + 4.40 * 3 / 36000.0)}
    ck.close("the index rule on a fixture: Index(b)/Index(a) = 1 + SOFR(a)(b-a)/36000", index_pair_diff(idx[D_("2026-01-09")], idx[D_("2026-01-12")], 4.40, 3), 0.0, 2e-8)


def t_g9(ck):
    r = headline(4.5, 4.3, 0.5, -20.0, 92, "yen")
    ck.close("rate_gap_term + basis_term = H - y_us (identity)", r["rate_gap_term"] + r["basis_term"], r["H"] - 4.5, 1e-12)
    ck.close("basis_term = H - h0", r["basis_term"], r["H"] - r["h0"], 1e-12)
    ck.close("rate_gap_term = h0 - y_us", r["rate_gap_term"], r["h0"] - 4.5, 1e-12)


FX_MONTHLY_HDR = ",".join(MONTHLY_COLS)


def fx_monthly_text(rows, header=None):
    h = header or MONTHLY_COLS
    out = io.StringIO()
    out.write("# source: fixture\n")
    w = csv.writer(out, lineterminator="\n")
    w.writerow(h)
    for r in rows:
        w.writerow(r)
    return out.getvalue()


def fx_mrow(month, pair="euro", variant="H3", **kw):
    d = dict(zip(MONTHLY_COLS, [month, pair, variant, "HEADLINE", "20", "0", "0", "4.000000", "2.500000", "-1.500000", "-0.010000", "2.490000", "-0.010000", "-3.000",
                               "3m", "91.000", "50", "50", "20"]))
    d.update(kw)
    return [d[c] for c in MONTHLY_COLS]


def t_g10(ck):
    good = fx_monthly_text([fx_mrow("2030-01"), fx_mrow("2030-02"), fx_mrow("2030-03"), fx_mrow("2030-04"), fx_mrow("2030-05")])
    ck.eq("a clean fixture passes the guard", leak_guard({"monthly.csv": good}, {}), [])
    ck.ok("(a) a daily date column is caught", leak_guard({"monthly.csv": fx_monthly_text([fx_mrow("2030-01-15")])}, {}))
    h2 = list(MONTHLY_COLS[:-1]) + ["dks_rho"]
    ck.ok("(b) a DKS-tagged column is caught", leak_guard({"monthly.csv": fx_monthly_text([fx_mrow("2030-01")], h2)}, {}))
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "m.csv")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# source: fixture\n" + ",".join(LEDGER_COLS) + "\n2030-01,xccy_jpyusd,3m,9,-30.5,,,,ok,5\n")
        ck.raises("(c) a ledger row with a median at n = 9 is refused on read", DataError, lambda: read_ledger(p))
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# source: fixture\n" + ",".join(LEDGER_COLS) + "\n2030-01,xccy_jpyusd,3m,10,-30.5,-31,-30,1.0,ok,5\n2030-02,xccy_jpyusd,3m,9,,,,,count_only,4\n")
        ck.eq("(c) n = 10 publishes and n = 9 is count_only", (read_ledger(p)[("2030-01", "xccy_jpyusd", "3m")]["median"], read_ledger(p)[("2030-02", "xccy_jpyusd", "3m")]["median"]),
              (-30.5, None))
    raw = {"sofr": {"2030-0%d" % m: 4.1234567 + 0.1 * m for m in range(1, 6)}}
    leak = [fx_mrow("2030-0%d" % m, basis_term_pp=f(raw["sofr"]["2030-0%d" % m], 6)) for m in range(1, 6)]
    ck.ok("(d) a column equal to a raw input's monthly mean is caught by the rounded comparison", leak_guard({"monthly.csv": fx_monthly_text(leak)}, raw))
    h3 = list(MONTHLY_COLS[:-1]) + ["tona_pct"]
    ck.ok("(d) a tona_pct column is caught by name", leak_guard({"monthly.csv": fx_monthly_text([fx_mrow("2030-01")], h3)}, {}))
    ck.ok("(e) a yen row in monthly.csv is caught", leak_guard({"monthly.csv": fx_monthly_text([fx_mrow("2030-01", pair="yen")])}, {}))
    ys = io.StringIO()
    ys.write("# source: fixture\nperiod,variant,statistic,value,credit\n")
    for i in range(9):
        ys.write("%d,H3,pickup_mean,0.1,c\n" % (2020 + i))
    ck.ok("(f) a ninth value per variant and statistic is caught", leak_guard({"yen_summary.csv": ys.getvalue()}, {}))
    rf = "# source: fixture\n" + ",".join(REF_COLS) + "\nV1,s,2026-09-08,yen,H,3m,2.0,50,1.99,0,25,PASS,n\n"
    ck.ok("(g) a yen build_value in references.csv is caught", leak_guard({"references.csv": rf}, {}))


def t_g11(ck):
    asof = D_("2026-10-19")
    ck.eq("a TONA file 20 days old is a WARN, not a silent pass", age_flag(asof, D_("2026-09-29"), 7), "WARN")
    ck.eq("a fresh file passes", age_flag(asof, D_("2026-10-15"), 7), "PASS")
    ledger = {("2030-01", s_, "3m"): dict(n=12, median=v, status="ok") for s_, v in (("sofr_ois", 4.3), ("tona_ois", 0.5), ("xccy_jpyusd", -20.0))}
    rows = headline_rows("2030-03", "yen", [dict(ust10=4.5, home10=2.0)], ledger, [D_("2030-03-15")], 0, False)
    ck.eq("a ledger file that ends in January gives no March row (nothing forward-filled)", rows, [])


def t_g12(ck):
    ledger = {}
    for m, bn in (("2030-01", 12), ("2030-02", 9)):
        for s_, v in (("sofr_ois", 4.3), ("tona_ois", 0.5)):
            ledger[(m, s_, "3m")] = dict(n=12, median=v, status="ok")
        ledger[(m, "xccy_jpyusd", "3m")] = dict(n=bn, median=-20.0 if bn >= 10 else None, status="ok" if bn >= 10 else "count_only")
    for s_, v in (("sofr_ois", 3.0), ("tona_ois", 1.5), ("xccy_jpyusd", -50.0)):
        ledger[("2030-01", s_, "1y")] = dict(n=30, median=v, status="ok")
    kept = [dict(ust10=4.5, home10=2.0)]
    dts = [D_("2030-03-15")]
    ck.eq("a count_only basis month has no H3 or P3 (no last-month basis)", [r["variant"] for r in headline_rows("2030-02", "yen", kept, ledger, dts, 0, False)], [])
    jan = {r["variant"]: r for r in headline_rows("2030-01", "yen", kept, ledger, [D_("2030-01-15")], 0, False)}
    ck.eq("January has all four forms (3m and 1y cells are both there)", sorted(jan), ["H12", "H3", "P12", "P3"])
    ck.close("H3 uses its own 3m cells", jan["H3"]["basis_term"], headline(4.5, 4.3, 0.5, -20.0, hedge_days(D_("2030-01-15"), 3), "yen")["basis_term"], 1e-9)
    ck.close("a 1y cell is not used in H3 (the 1y cells would give another basis term)", jan["H3"]["carry"], headline(4.5, 4.3, 0.5, -20.0, hedge_days(D_("2030-01-15"), 3), "yen")["H"], 1e-9)


def t_g13(ck):
    for name, spec in SPEC_ALLOW.items():
        ck.eq("ALLOW equals the spec's printed list: %s" % name, allowlist(name), [x.strip() for x in spec.split(",")])
    ck.eq("the sha256 of the printed lists", allow_digest(), SPEC_ALLOW_SHA256)
    ck.eq("the sha256 of the lists is stable (anchor)", SPEC_ALLOW_SHA256[:12], "da19d10f2ca5")
    ck.raises("an extra column is refused", DataError, lambda: check_header("pins.csv", PIN_COLS + ["extra"]))
    ck.raises("a renamed column is refused", DataError, lambda: check_header("pins.csv", PIN_COLS[:-1] + ["units"]))
    ck.raises("a missing column is refused", DataError, lambda: check_header("pins.csv", PIN_COLS[:-1]))
    ck.ok("the exact header is accepted", check_header("pins.csv", PIN_COLS) is None)


def t_g14(ck):
    bad = ["the move was caused by x", "yields drove the carry", "it is driven by rates", "because of the basis", "this led to a sale", "it prompted a hedge",
           "which pushed it up", "in response to a move"]
    for t in bad:
        ck.ok("causal wording is flagged: %r" % t, causal_hits(t))
    ck.eq("the required sentence passes", causal_hits(REQUIRED_SENTENCE), [])
    ck.ok("the same sentence with 'led to' added fails", causal_hits(REQUIRED_SENTENCE.replace("led any", "led to any")))
    ck.raises("render_csv refuses causal wording in a source line", DataError, lambda: render_csv("pins.csv", [], "# source: this was driven by flows"))
    ck.ok("render_csv accepts the required sentence in a source line", render_csv("pins.csv", [], "# source: " + REQUIRED_SENTENCE).startswith("# source:"))
    ck.raises("the README guard refuses a home path", DataError, lambda: guard_text("README.md", "see " + os.path.expanduser("~") + "/x"))


def fake_rig(tmp, script, max_requests=30, sleep=MIN_SLEEP, clock=None, today=None):
    clock = clock or FakeClock()
    calls = []

    def opener(host, target, headers, timeout, cap):
        calls.append((host, target, dict(headers), clock.wall()))
        res = script(host, target, headers) if callable(script) else script
        if isinstance(res, Exception):
            raise res
        return res
    fe = Fetcher(os.path.join(tmp, "cache"), os.path.join(tmp, "out"), sleep=sleep, max_requests=max_requests, opener=opener, wall=clock.wall, mono=clock.wall,
                 sleeper=clock.sleep, stop_path=os.path.join(tmp, "cache", "STOP"),
                 now_utc=lambda: dt.datetime(2026, 10, 19, 12, 0, 0, tzinfo=dt.timezone.utc), root=os.path.join(tmp, "norepo"))
    return fe, calls, clock


def syn_nyfed(n=1600, rtype="SOFR"):
    hdr = "Effective Date,Rate Type,Rate (%),1st Percentile (%),25th Percentile (%),75th Percentile (%),99th Percentile (%),Volume ($Billions),Target Rate From (%)"
    d = dt.date(2018, 4, 2)
    rows = []
    while len(rows) < n:
        if d.weekday() < 5:
            rows.append("%02d/%02d/%d,%s,3.89,3.85,3.87,3.94,3.97,3025," % (d.month, d.day, d.year, rtype))
        d += dt.timedelta(days=1)
    return (hdr + "\n" + "\n".join(reversed(rows)) + "\n").encode()


def syn_dks_probe():
    return (DKS_HEADER + "\n" + "eme,BRL,10y,08feb2007,,5.9,,26dec2023,5.9,,,\n").encode()


def t_g15(ck):
    today = dt.date(2026, 10, 19)
    sofr_req = next(r for r in request_table(today) if r["key"] == "sofr")
    tsy_req = next(r for r in request_table(today) if r["key"] == "tsy2018")
    probe_req = next(r for r in request_table(today) if r["key"] == "dks_probe")
    good = lambda h, t, hd: (200, syn_nyfed(), {})

    def latches(label, script, req=sofr_req, expect=True):
        with tempfile.TemporaryDirectory() as tmp:
            fe, calls, _ = fake_rig(tmp, script)
            exc = None
            try:
                fe.fetch_one(req)
            except Latched as e:
                exc = e
            stop = os.path.exists(os.path.join(tmp, "cache", "STOP"))
            ck.eq("%s: STOP %s" % (label, "written" if expect else "not written"), stop, expect)
    for st in (403, 404, 429, 500):
        latches("HTTP %d latches" % st, (lambda s: lambda h, t, hd: (s, b"", {}))(st))
    for st in (301, 302):
        latches("a redirect (%d) latches, and is not followed" % st, (lambda s: lambda h, t, hd: (s, b"", {"location": "https://example.com"}))(st))
    latches("a 200 that is not the file latches", lambda h, t, hd: (200, b"<html>blocked</html>", {}))
    latches("a 206 on an ordinary request latches (only the DKS probe may answer 206)", lambda h, t, hd: (206, syn_nyfed(), {}))
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "cache"))
        with open(os.path.join(tmp, "cache", "dks_3m_1y.csv"), "w") as fh:
            fh.write("x")
        fe, calls, _ = fake_rig(tmp, lambda h, t, hd: (206, syn_dks_probe(), {"content-range": "bytes 0-65535/118471039", "etag": '"' + DKS_ETAG_OBSERVED + '"',
                                                                             "last-modified": "x"}))
        out = fe.fetch_one(probe_req)
        ck.eq("the DKS probe's 206 is accepted and does not latch", (out, os.path.exists(os.path.join(tmp, "cache", "STOP"))), ("saved", False))
        ck.eq("the DKS probe asks for bytes 0-65535", calls[0][2].get("Range"), "bytes=0-65535")
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _ = fake_rig(tmp, SocketFault("timeout"))
        try:
            fe.fetch_one(sofr_req)
        except SocketFault:
            pass
        ck.eq("a socket fault does not latch", os.path.exists(os.path.join(tmp, "cache", "STOP")), False)
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _ = fake_rig(tmp, good)
        os.makedirs(os.path.join(tmp, "cache"))
        with open(os.path.join(tmp, "cache", "STOP"), "w") as fh:
            fh.write("x\n")
        ck.raises("an existing STOP blocks every fetch", Latched, fe.check_stop)
    for url in ("https://fred.stlouisfed.org/graph/fredgraph.csv?id=SOFR", "https://www.sec.gov/cgi-bin/browse-edgar", "https://data.sec.gov/submissions/x.json",
                "https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/x.zip", "https://example.com/x"):
        ck.raises("refused before any request: %s" % url.split("/")[2], Refused, lambda u=url: check_url(u, today))
    ck.raises("plain http is refused", Refused, lambda: check_url("http://home.treasury.gov" + tsy_req["target"], today))
    ck.raises("a path that is not in the table is refused", Refused, lambda: check_url("https://markets.newyorkfed.org/api/rates/secured/sofr/last/1.json", today))
    ck.ok("a table request is accepted", check_url("https://home.treasury.gov" + tsy_req["target"], today)[0] == "home.treasury.gov")
    ck.raises("an address in the identification string is refused", Refused, lambda: assert_ua("research tool (a" + chr(64) + "b.example)"))
    ck.ok("the identification string has no address", chr(64) not in UA)
    ck.ok("the identification string says non-commercial research and names no person", "non-commercial research" in UA and UA.count("(") == 1)
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = fake_rig(tmp, good)
        for r in request_table(today)[:3]:
            try:
                fe.fetch_one(dict(r, kind="sofr", ok=(200,), file="x_" + r["key"]))
            except Latched:
                pass
        starts = [c[3] for c in calls]
        ck.ok("request starts are at least 2 s apart", len(starts) >= 3 and all(b - a >= 2.0 for a, b in zip(starts, starts[1:])), str(starts))
    ck.raises("--max-requests 31 is refused (the spec allows 30)", Refused, lambda: Fetcher("/tmp/x_never_used", "/tmp/y", max_requests=31))
    ck.raises("--sleep below 2 is refused", Refused, lambda: Fetcher("/tmp/x_never_used", "/tmp/y", sleep=1.0))
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = fake_rig(tmp, good, max_requests=2)
        raised = None
        try:
            for r in request_table(today)[:3]:
                try:
                    fe.fetch_one(dict(r, kind="sofr", ok=(200,), file="x_" + r["key"]))
                except Latched:
                    pass
        except MaxRequests as e:
            raised = e
        ck.ok("the request beyond the cap is not sent", raised is not None and len(calls) == 2)


SYN_TSY_2026 = ('Date,"1 Mo","1.5 Month","2 Mo","3 Mo","4 Mo","6 Mo","1 Yr","2 Yr","3 Yr","5 Yr","7 Yr","10 Yr","20 Yr","30 Yr"\n'
                '10/15/2026,3.7,3.71,3.72,3.73,3.74,3.75,3.76,3.77,3.78,3.79,3.80,5.10,5.20,5.30\n10/14/2026,3.7,3.7,3.7,3.7,3.7,3.7,3.7,3.7,3.7,3.7,3.7,5.05,3.7,3.7\n')
SYN_MOF = ("Interest Rate (October 2026),,,,,,,,,,,,,,,(Unit : %)\r\nDate,1Y,2Y,3Y,4Y,5Y,6Y,7Y,8Y,9Y,10Y,15Y,20Y,25Y,30Y,40Y\r\n"
           "2026/10/1,1.668,1.939,2.077,2.274,2.407,2.534,2.657,2.82,2.952,3.092,3.62,3.91,4.154,4.122,4.125\r\n"
           "2026/10/2,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-\r\n,,,,,,,,,,,,,,,\r\n\" * If you cannot download the latest csv data, please clear the cache.\",,,,,,,,,,,,,,,\r\n")
SYN_EST = ("KEY,FREQ,BENCHMARK_ITEM,DATA_TYPE_EST,TIME_PERIOD,OBS_VALUE,OBS_STATUS\n"
           "EST.B.EU000A2QQF08.CI,B,EU000A2QQF08,CI,2019-10-01,100,A\nEST.B.EU000A2QQF08.CI,B,EU000A2QQF08,CI,2019-10-02,99.998475,A\n"
           "EST.B.EU000A2X2A25.WT,B,EU000A2X2A25,WT,2019-10-01,-0.549,A\nEST.B.EU000A2X2A25.WT,B,EU000A2X2A25,WT,2019-10-02,-0.55,A\n")
SYN_TONA = ("STATUS,200\nMESSAGEID,M181000I\nMESSAGE,Successfully completed\nDATE,2026-10-19T19:16:02.560+09:00\nPARAMETER,FORMAT,CSV\nNEXTPOSITION,\n"
            "SERIES_CODE,NAME_OF_TIME_SERIES,UNIT,FREQUENCY,CATEGORY,LAST_UPDATE,SURVEY_DATES,VALUES\n"
            'STRDCLUCON,"Call Rate, Uncollateralized Overnight, Average (Daily)",percent per annum,DAILY,Call Rate,20261019,20180103,null\n'
            'STRDCLUCON,"Call Rate, Uncollateralized Overnight, Average (Daily)",percent per annum,DAILY,Call Rate,20261019,20180104,-0.047\n'
            'STRDCLUCON,"Call Rate, Uncollateralized Overnight, Average (Daily)",percent per annum,DAILY,Call Rate,20261019,20261015,1.228\n')
SYN_DKS = DKS_HEADER + "\nJPY,JPY,3m,08feb2007,1,-2.5,0.1,26dec2023,-2.5,,,\n".replace("JPY,JPY", "g10,JPY")


def t_g16(ck):
    t = parse_tsy10(SYN_TSY_2026)
    ck.eq("Treasury 10 Yr by name in the 2026 layout (with '1.5 Month')", (t.get(D_("2026-10-15")), t.get(D_("2026-10-14"))), (5.10, 5.05))
    m = parse_mof10(SYN_MOF)
    ck.eq("MoF: unpadded dates, '-' missing, the footer lines skipped", (m.get(D_("2026-10-01")), m.get(D_("2026-10-02")), len(m)), (3.092, None, 2))
    ny = parse_nyfed("Effective Date,Rate Type,Rate (%),1st Percentile (%),25th Percentile (%)\n10/15/2026,SOFR,3.89,3.85,3.87\n10/14/2026,SOFR,3.88,3.83,3.86\n"
                     "10/13/2026,SOFR,3.87,3.80,3.85\n", "SOFR")
    ck.eq("NY Fed by header name, newest row first", (ny.get(D_("2026-10-15")), ny.get(D_("2026-10-13"))), (3.89, 3.87))
    r, i = parse_est(SYN_EST)
    ck.eq("ECB EST: the rate and the index are separate", (r.get(D_("2019-10-02")), i.get(D_("2019-10-02"))), (-0.55, 99.998475))
    tona, nxt = parse_tona(SYN_TONA)
    ck.eq("BoJ: 'null' is missing, the header block is skipped, the quoted comma is kept", (D_("2018-01-03") in tona, tona.get(D_("2018-01-04")), tona.get(D_("2026-10-15")), len(tona)),
          (False, -0.047, 1.228, 2))
    ck.eq("BoJ: an empty NEXTPOSITION means no further page", nxt, "")
    ck.eq("DKS date 08feb2007", parse_dks_date("08feb2007"), D_("2007-02-08"))


def t_g17(ck):
    ck.ok("rho in the 3.2 convention is negative when the home rate is below the dollar rate", rho_signed(-2.75) < 0)
    ck.close("rho_signed keeps the file's sign (O-4: read on 19 Oct 2026)", rho_signed(-2.75), -2.75, 1e-12)
    pairs = [(4.00 + 0.01 * k, 4.07 - 0.01 * k) for k in range(8)]
    st = v5_stats(pairs)
    ck.eq("a negative overlap correlation with H3 (n >= 8) is a FAIL that names O-4", (st["status"], st["corr"] is not None and st["corr"] < 0), ("FAIL", True))
    pos = v5_stats([(4.00 + 0.01 * k, 4.00 + 0.01 * k + 0.02) for k in range(8)])
    ck.eq("a positive correlation with 2bp difference passes", pos["status"], "PASS")
    ck.eq("fewer than 8 months is INFO", v5_stats(pairs[:7])["status"], "INFO")


def syn_panel_two_months():
    cal = syn_calendar()
    inp = syn_inputs(cal)
    tsy = sorted(d for d in inp.tsy if d <= D_("2025-03-14"))
    inp.tsy = {d: inp.tsy[d] for d in tsy}
    return inp, build_panel(inp, "euro"), sorted(inp.tsy)


def t_g18(ck):
    inp, panel, tsy = syn_panel_two_months()
    n, partial = month_status(panel, tsy, "2025-03")
    ck.eq("a month whose data end mid-month is partial", partial, True)
    n2, partial2 = month_status(panel, tsy, "2025-02")
    ck.eq("a month with data past its end and a kept last day is complete", partial2, False)
    rows = [dict(month="2025-01", pair="euro", variant="H3", partial=0, pickup=0.10), dict(month="2025-02", pair="euro", variant="H3", partial=0, pickup=0.20),
            dict(month="2025-03", pair="euro", variant="H3", partial=1, pickup=-9.0)]
    mr, status = monthly_rows({"euro": panel}, {}, tsy)
    flags = {(r["month"]): r["partial"] for r in mr if r["variant"] == "A_hist"}
    ck.eq("section 4 helper takes complete months only", sorted(path_of([dict(r, pair="euro") for r in rows], "euro", "H3", "2025-01", "2025-03")), ["2025-01", "2025-02"])
    ck.eq("the partial flag reaches the monthly rows (March is partial)", flags.get("2025-03"), 1)
    ck.eq("L is the latest complete month", latest_complete({("yen", "2025-02"): (20, False), ("euro", "2025-02"): (20, False), ("yen", "2025-03"): (9, True),
                                                           ("euro", "2025-03"): (9, True)}), "2025-02")
    with tempfile.TemporaryDirectory() as tmp:
        write_text(os.path.join(tmp, "summary.csv"), "# source: x\nrun_label,L,question,pair,variant,statistic,value,notable\nL_2030-01,2030-01,L,,,latest_complete_month,,\n")
        ck.eq("L is read back from the L row and never recomputed", read_frozen_L(tmp), "2030-01")


def t_g19(ck):
    ck.eq("gate: the median of [20, 40, 100] is 40, a FAIL", gate_status([20.0, 40.0, 100.0], 3), "FAIL")
    ck.eq("gate: the median of [10, 30] is 20, a PASS", gate_status([10.0, 30.0], 2), "PASS")
    ck.eq("gate: a point at 27bp is not forgiven for the quote's rounding", gate_status([27.0, 27.0], 2), "FAIL")
    ck.eq("gate: a group missing a point cannot pass", gate_status([10.0], 2), "FAIL")
    ck.close("O-9: 1.4 against the whole-percent quote 2 is 10bp from the interval [1.5, 2.5]", quote_gap_bp(1.4, 2.0, 0.5), 10.0, 1e-9)
    ck.close("O-9: 1.7 is inside the interval, gap zero", quote_gap_bp(1.7, 2.0, 0.5), 0.0, 1e-9)
    ck.close("a quote to a tenth is scored at its printed value: 1.09 against 1.3 is 21bp", quote_gap_bp(1.09, 1.3, 0.0), 21.0, 1e-9)
    ck.close("the same 0.5 half-width does NOT apply to a tenth", quote_gap_bp(1.0, 1.3, 0.0), 30.0, 1e-9)
    with tempfile.TemporaryDirectory() as tmp:
        write_outputs({"monthly.csv": "x\n"}, {}, tmp, os.path.join(tmp, "cache"), ["GATE_H_3m"])
        ck.eq("a failed build writes to _FAILED and not to the committed folder", (os.path.exists(os.path.join(tmp, "_FAILED", "monthly.csv")),
                                                                              os.path.exists(os.path.join(tmp, "monthly.csv"))), (True, False))
        write_outputs({"monthly.csv": "y\n"}, {}, tmp, os.path.join(tmp, "cache"), [])
        ck.eq("a passing build writes the committed folder", os.path.exists(os.path.join(tmp, "monthly.csv")), True)


def t_x_cache(ck):
    ck.raises("a cache inside the repository, not ignored by git, is refused", Refused, lambda: check_cache(os.path.join(ROOT, "data", "not_ignored_x")))
    ck.ok("the default cache is accepted (git ignores it)", check_cache(CACHE_DEFAULT) is not None)
    ck.raises("the committed output folder as a cache is refused", Refused, lambda: check_cache(os.path.join(OUT_DEFAULT, "cache")))


def t_x_stop(ck):
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _ = fake_rig(tmp, lambda h, t, hd: (200, b"", {}))
        os.makedirs(os.path.join(tmp, "cache"))
        with open(os.path.join(tmp, "cache", "STOP"), "w") as fh:
            fh.write("x\n")
        ck.raises("fetch_one refuses while STOP exists", Latched, lambda: fe.fetch_one(next(r for r in request_table(dt.date(2026, 10, 19)) if r["key"] == "sofr")))
        ck.eq("...and sends no request", len(calls), 0)


def t_x_build(ck):
    """An end-to-end build on synthetic inputs: structure, determinism and the leak guard on real renderings."""
    cal = syn_calendar()
    a, b = dt.date(2018, 1, 1), dt.date(2026, 10, 16)
    days = []
    d = a
    while d <= b:
        if d.weekday() < 5 and (d.month, d.day) not in ((12, 25), (1, 1)):
            days.append(d)
        d += dt.timedelta(days=1)
    inp = Inputs()
    inp.tsy = {d: 4.0 + 0.0001 * i for i, d in enumerate(days)}
    inp.tsy[D_("2024-03-21")], inp.tsy[D_("2026-09-18")], inp.tsy[D_("2026-10-15")] = 4.27, 5.01, 5.10
    inp.sofr = {d: 3.5 for d in days if d >= D_("2018-04-02") and d <= D_("2026-10-15")}
    inp.effr = {d: 3.4 for d in days if d <= D_("2026-10-15")}
    inp.sofrai = {d: 1.0 + 0.00001 * i for i, d in enumerate(d for d in days if d >= D_("2020-03-02"))}
    jp = [d for d in days if not closure_day("JPY", d) and d <= D_("2026-10-15")]
    inp.tona = {d: 1.0 for d in jp}
    inp.jgb = {d: 2.0 for d in jp}
    ea = [d for d in days if not closure_day("EUR", d) and d >= D_("2019-10-01")]
    inp.estr = {d: 2.0 for d in ea}
    inp.estr_ci = {d: 100.0 + 0.00001 * i for i, d in enumerate(ea)}
    inp.estr_ci[D_("2026-10-19")] = 110.03236357
    inp.sofrai[D_("2026-10-16")] = 1.26303308
    prm = dict(BETA0=1.608146049, BETA1=0.6677584932, BETA2=2.8889513654, BETA3=6.8503522231, TAU1=1.0445730922, TAU2=13.8644399107)
    inp.aaa = {d: fx.ea_semiannual(10, fx.params_of(prm)) for d in ea}
    inp.aaa_published = {d: dict(prm) for d in ea}
    inp.bbk = {d: 2.4 for d in ea}
    inp.dks = {}
    inp.dks_probe = None
    inp.yc_quar, inp.yc_incomplete = {}, []
    inp.jgb_err, inp.jgb_overlap, inp.jgb_hist_end, inp.jgb_cur_start = None, 0, D_("2026-09-30"), D_("2026-10-01")
    inp.tona_next, inp.tona_nulls = "", 3
    ledger = {}
    months = months_between("2024-10", "2026-09")
    for m in months:
        for s_, v in (("sofr_ois", 3.6), ("estr_ois", 2.0), ("tona_ois", 0.9), ("xccy_jpyusd", -20.0), ("xccy_eurusd", -2.0)):
            for t_ in ("3m", "1y"):
                ledger[(m, s_, t_)] = dict(n=20, median=v, status="ok")
    fetch_rows = [["2026-10-19T10:00:00.000Z", TSY_HOST, "/x", "200", "10", "ab"]]
    tsy_dates = sorted(inp.tsy)
    panels = {"yen": build_panel(inp, "yen"), "euro": build_panel(inp, "euro")}
    mrows, status = monthly_rows(panels, ledger, tsy_dates)
    L = latest_complete(status)
    ck.eq("synthetic: L is the latest complete month (2026-09)", L, "2026-09")
    refs, gate = build_references(inp, ledger, tsy_dates, mrows)
    v5 = v5_results(panels, mrows)
    refs = [r for r in refs if not r["ref_id"].startswith("GATE")] + v5_ref_rows(v5) + [r for r in refs if r["ref_id"].startswith("GATE")]
    s4 = section4(mrows, status, ledger, L, v5, "L_" + L)
    s_com, s_full = summary_texts(s4, L, "L_" + L)
    c = dict(inp=inp, ledger=ledger, fetch_rows=fetch_rows, asof=D_("2026-10-19"), tsy_dates=tsy_dates, panels=panels, mrows=mrows, status=status, L=L, refs=refs,
             gate=gate, v5=v5, s4=s4, summary_com=s_com, summary_full=s_full, yen_rows=yen_summary_rows(mrows, status, L, ledger), pins=pins_rows(inp),
             anchor=yen_anchor(ledger), ledger_mtime=D_("2026-10-19"), jgb_overlap=0, jgb_hist_end=D_("2026-09-30"), jgb_cur_start=D_("2026-10-01"), tona_nulls=3, checks=[])
    com, cache, failed = finish(c)
    com2, cache2, failed2 = finish(c)
    ck.ok("synthetic: two renderings are byte-identical", com == com2 and cache == cache2)
    ck.ok("synthetic: monthly.csv has euro rows only", all(r.split(",")[1] == "euro" for r in com["monthly.csv"].splitlines()[2:]))
    ck.ok("synthetic: the committed files carry no yen monthly row", "yen" not in "\n".join(l.split(",")[1] for l in com["monthly.csv"].splitlines()[2:]))
    ck.ok("synthetic: the README carries the required sentence", REQUIRED_SENTENCE in com["README.md"])
    ck.ok("synthetic: the README opens with two sentences, the second the required sentence", com["README.md"].split("\n\n")[1].endswith(REQUIRED_SENTENCE))
    ck.ok("synthetic: the yen monthly path is in the cache only", "yen" in cache["monthly_all.csv"] and "yen" not in com["monthly.csv"])
    ck.eq("synthetic: C14 (rendering twice) passes", [r for r in c["checks"] if r[0] == "C14"][0][4], "PASS")
    ck.eq("synthetic: the leak guard passes on the real rendering", [r for r in c["checks"] if r[0] == "C16"][0][4], "PASS")
    ck.ok("synthetic: monthly.csv identity (carry = ust + gap + basis, pickup = carry - home) holds at 2e-6", all(
        abs(float(r[11]) - (float(r[7]) + float(r[9]) + float(r[10]))) <= 2e-6 and abs(float(r[12]) - (float(r[11]) - float(r[8]))) <= 2e-6
        for r in csv.reader(l for l in com["monthly.csv"].splitlines() if not l.startswith("#") and not l.startswith("month,"))))


GUARDS = [
    ("G1", "basis sign: a negative basis lowers h; the 3m and 1y fixtures", ["basis_sign", "basis_usd"], t_g1),
    ("G2", "gap direction: o_us above o_home gives a negative gap", ["swap_rates"], t_g2),
    ("G3", "day count: SOFR 360, TONA 365, euro short-term rate 360", ["tona_360", "sofr_365"], t_g3),
    ("G4", "bond-basis form (3.2) exactly, and P without a day-count change", ["h_as_p", "p_daycount"], t_g4),
    ("G5", "tenor D: actual days clipped to the month end; hedge_days_mean", ["d_fixed90", "d_quarter"], t_g5),
    ("G6", "alignment: legs dated on or before d; A_rt reads only published rates; the stale rule; the triples", ["next_day_leg", "a_rt_dated", "no_stale_check"], t_g6),
    ("G7", "B window: [d, d+D), complete windows, clipping", ["window_includes_end", "window_backward", "window_partial_ok", "no_clip"], t_g7),
    ("G8", "B compounding: ARRC (a weekend is one period); the index rule", ["weekend_daily", "simple_sum", "index_daily_compound"], t_g8),
    ("G9", "decomposition: basis_term = H - h0", ["basis_inside"], t_g9),
    ("G10", "licence and leak guard (section 7), items (a) to (g)", ["leak_date_off", "leak_dks_off", "ledger_floor_off", "leak_numeric_off", "leak_yenrow_off", "leak_cap_off", "leak_refs_off"], t_g10),
    ("G11", "staleness: a stale input is a WARN; nothing is forward-filled", ["stale_ok", "ledger_ffill_stale"], t_g11),
    ("G12", "no carry-forward: each month's own cells, 3m only in H3", ["carry_forward", "tenor_mix"], t_g12),
    ("G13", "exact column allowlists, anchored to the spec's printed lists and their sha256", ["extra_column", "renamed_column", "allow_drift"], t_g13),
    ("G14", "no causal text; the required sentence passes; with 'led to' added it fails", ["causal_guard_off", "causal_rx_narrow"], t_g14),
    ("G15", "fetch safety: latches, redirects, socket fault, FRED / sec.gov / DTCC, identification string, pacing, 30 requests",
     ["no_latch_non200", "no_latch_redirect", "no_latch_bad_body", "latch_on_socket", "allow_fred", "ua_check_off", "no_pacing", "no_request_cap"], t_g15),
    ("G16", "parsers (section 2): BoJ, NY Fed, ECB EST, Treasury, MoF, DKS date", ["boj_null_as_zero", "boj_header_as_data", "boj_naive_split", "nyfed_positional",
                                                                                "nyfed_oldest_first", "est_ci_as_rate", "positional_treasury", "mof_footer_as_data",
                                                                                "dks_date_misparse"], t_g16),
    ("G17", "DKS sign (rho in the 3.2 convention) and the O-4 verdict", ["dks_sign_flip", "v5_neg_ok"], t_g17),
    ("G18", "months and L: complete months only; L frozen", ["partial_counted", "l_recomputed"], t_g18),
    ("G19", "the gate: the median, no rounding credit, a failed build stays out of the committed folder", ["gate_min", "gate_rounding_credit", "rounding_to_status",
                                                                                                          "failed_to_committed"], t_g19),
    ("X1", "cache path: outside the repo, or git-ignored inside it", ["cache_check_off"], t_x_cache),
    ("X2", "an existing STOP file blocks fetching", ["stop_ignored"], t_x_stop),
    ("X3", "an end-to-end synthetic build: structure, determinism, the leak guard on real renderings", ["render_unstable"], t_x_build),
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




# ==== COMMAND LINE ====
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch", help="download the inputs into the cache (the only network command)")
    pf.add_argument("--cache", default=CACHE_DEFAULT)
    pf.add_argument("--out", default=OUT_DEFAULT, help="where fetch_log.csv is kept")
    pf.add_argument("--sleep", type=float, default=MIN_SLEEP, help="seconds between request starts (at least 2)")
    pf.add_argument("--max-requests", type=int, default=MAX_REQUESTS)
    pf.add_argument("--dks-full", action="store_true", help="fetch the 118 MB DKS panel again even if dks_3m_1y.csv is in the cache")
    pb = sub.add_parser("build", help="offline: validate the cache and write every output")
    pb.add_argument("--cache", default=CACHE_DEFAULT)
    pb.add_argument("--out", default=OUT_DEFAULT)
    pb.add_argument("--ledger", default=LEDGER_DEFAULT)
    ps = sub.add_parser("selftest", help="synthetic data, mutants applied one at a time; no network")
    ps.add_argument("--no-mutants", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "selftest":
            return selftest(mutants=not a.no_mutants)
        if a.cmd == "build":
            return run_build(a)
        fe = Fetcher(a.cache, a.out, sleep=a.sleep, max_requests=a.max_requests)
        fe.check_stop()
        saved = fe.run(request_table(fe.today()), dks_full=a.dks_full)
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
