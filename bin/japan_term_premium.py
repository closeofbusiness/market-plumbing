#!/usr/bin/env python3
"""Japan's 10-year yield rise split into term premium and expected rates, on Jouchi Nakajima's published decomposition. Python 3 standard library only.

  python3 bin/japan_term_premium.py fetch [--cache DIR] [--out DIR] [--sleep 2.05] [--max-requests 15]     # the only network command
  python3 bin/japan_term_premium.py build [--cache DIR] [--out DIR] [--mof FILE] [--amend "reason"]      # offline; byte-identical on re-run
  python3 bin/japan_term_premium.py selftest [--no-mutants] [--spec PATH]                                  # synthetic data only; no network

Specification: _research/2026-10-19-Japan-Term-Premium-Spec.md (with the supervisor's rulings of rounds 1 to 4, the latest round winning where they
conflict). Every number here is one model's residual, not a measurement: the split depends on the model and on the vintage of its file.

WHAT TOUCHES THE NETWORK. Only `fetch`. Hosts: raw.githubusercontent.com, api.github.com, sites.google.com and takujiokubo.github.io. Any other host
(FRED, sec.gov included) is refused before a request is made, and each request must be one of the exact URL forms of the spec (raw files are pinned
to a 40-hex commit, never /main/). GET only; one request at a time; at least 2 s between request starts, remembered across invocations; at most 15
requests per run (11 expected); the CLAUDE.md non-SEC identification string (no address, no name); no redirect is followed. Any HTTP status other than
200, or a body that fails its content test, writes <cache>/STOP and ends the run; a 403 or 429 from GitHub is reported as rate limiting and never as
an absent file, and it still latches. While STOP exists every fetch refuses. Only a person deletes STOP: no code in this file removes or renames it.

WHERE THE FILES LIVE. The cache (default ~/jgb_term_premium_cache/, which must resolve outside the repository) holds every raw download. Nakajima's
files are never committed, in any form or under any name; the folder data/japan_term_premium/ holds derived statistics and at most four level points
per vintage (pins.csv). Rebuilds are byte-identical: every timestamp in a committed file comes from the fetch log or from the commit list.
"""
import argparse
import ast
import calendar
import contextlib
import copy
import csv
import datetime as dt
import hashlib
import html as htmllib
import http.client
import io
import json
import math
import os
import re
import statistics
import sys
import tempfile
import time
from urllib.parse import urlsplit, unquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_rate_gap as fx  # noqa: E402  (read-only: the causal-wording pattern, imported unchanged)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(ROOT, "data", "japan_term_premium")
CACHE_DEFAULT = os.path.join(os.path.expanduser("~"), "jgb_term_premium_cache")
STOP_PATH = os.path.join(CACHE_DEFAULT, "STOP")                     # fixed, whatever --cache says
MOF_DEFAULT = os.path.join(ROOT, "data", "vintages", "hedged_ust_yield", "mof_jgbcme_all.csv")
MOF_FALLBACK = os.path.join(ROOT, "data", "vintages", "fx_rate_gap", "mof_jgbcme_all.csv")
SPEC_DEFAULT = os.path.join(ROOT, "_research", "2026-10-19-Japan-Term-Premium-Spec.md")

# R2: the CLAUDE.md canonical string for every non-SEC host. No address, no name.
UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
HEADERS = {"User-Agent": UA, "Accept-Encoding": "identity", "Accept": "*/*"}
MIN_SLEEP = 2.05
MAX_REQUESTS = 15
TIMEOUT = 120
BODY_CAP = 8 * 1024 * 1024

GH_RAW, GH_API, SITES, JMA_HOST = "raw.githubusercontent.com", "api.github.com", "sites.google.com", "takujiokubo.github.io"
HOST_ALLOW = frozenset({GH_RAW, GH_API, SITES, JMA_HOST})
REPO = "/jouchinakajima/program"
FILES_N = ("yield_M.csv", "yield_D.csv")
COMMITS_PATH = "/repos/jouchinakajima/program/commits?path={f}&per_page=100"
CONTENTS_PATH = "/repos/jouchinakajima/program/contents/{f}?ref={sha}"
RAW_PATH = REPO + "/{sha}/{f}"
PAGE_PATH = "/site/jnakajimaweb/yield"
JMA_CSV_PATH = "/jma-data/jgb-yield-curve-main/data/curve-panel.csv"
JMA_PAGE_PATH = "/jma-data/jgb-yield-curve-main/"
HEX40 = re.compile(r"[0-9a-f]{40}")

# the vintages the spec names
EXPECTED_VINTAGE = "2026-10-06_33118433fe95"
EXPECTED_SHA12 = "33118433fe95"
EXPECTED_COMMITS = 9
JULY_SHA = "80f7108a1637ac71d62a30fe97a7ce8a3bc88046"
APRIL_SHA = "8f940a0141eefc0d63a426ae5b3a2f6c11e236d0"
PAGE_LINKS = ("github.com/jouchinakajima/program/blob/main/yield_M.csv", "github.com/jouchinakajima/program/blob/main/yield_D.csv")

TENORS = ("2Y", "5Y", "10Y", "20Y")
TK = {"2Y": 2, "5Y": 5, "10Y": 10, "20Y": 20}
FIT_K = (2, 5, 7, 10, 15, 20)
WINDOWS = {"FULL": ("202312", "202609"), "A": ("202312", "202407"), "BRIDGE": ("202407", "202408"), "B": ("202408", "202609"),
           "BOJ_MATCH": ("202408", "202606"), "Y2024": ("202312", "202412"), "Y2025_26": ("202412", "202609")}
WINDOW_ORDER = ("FULL", "A", "BRIDGE", "B", "BOJ_MATCH", "Y2024", "Y2025_26")
REV_WINDOWS = {"REV_2606": ("202312", "202606"), "REV_2603": ("202312", "202603")}
MONTH_LIST = ("202312", "202407", "202408", "202412", "202603", "202606", "202609")
DY_MIN = 0.25
BAND = (0.40, 0.60)
TOL_PUB = 0.00015                  # R4-2: an identity between 4-decimal published cells and a MoF yield (monthly or daily)
TOL_RECOMP = 1e-6                  # R4-2: only where the build recomputes a value from cells it already holds
TOL_ADD = 1e-9                     # additivity of windows, unrounded
TOL_DY_COMMITTED = 2e-4            # d_yield = d_tp + d_er on committed 4-decimal cells
MIN_MOF_DAYS = 10

REQUIRED_SENTENCE = "This is one model's split of the yield change. Other models split it differently, and it does not show why yields rose."
R27_LABEL = ("The full-window result was read before this build. The sub-windows and the BoJ-matched window were chosen after looking at the data.")
CONVENTION_SENTENCE = ("Reading \"roughly the same degree\" as a share from 0.40 to 0.60 is this spec's convention, not the Bank's.")
CITE_IU = ("Ichiue, H., and Y. Ueno (2013), \"Estimating term premia at the zero bound: An analysis of Japanese, US, and UK yields\", Bank of Japan Working "
           "Paper 13-E-8")
CITE_NAK = ("Nakajima, J. (2025), \"Impact of US monetary policy spillovers and yield curve control policy\", Discussion Paper A.760, Institute of Economic "
            "Research, Hitotsubashi University")
JMA_ATTRIB = "free to use and reproduce with attribution to Japan Macro Advisors"
CITE_LINE = ("# cite: " + CITE_IU + "; " + CITE_NAK + "; Japan Macro Advisors (JMA) JGB yield curve model; Ministry of Finance Japan (JGB yields). Not the "
             "official view of the Bank of Japan.")

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
_CLOCK = [None]


def now_utc():
    """The wall clock. The build never calls it (R10); only fetch does, and the G21 mutant."""
    return _CLOCK[0]() if _CLOCK[0] else dt.datetime.now(dt.timezone.utc)


def tilde(p):
    home = os.path.expanduser("~")
    return str(p).replace(home, "~") if home and home != "~" else str(p)


def f(v, nd):
    """Fixed-decimal text, '' for None, no negative zero, no scientific notation (byte-stable outputs)."""
    if v is None:
        return ""
    s = format(round(v, nd), ".%df" % nd)
    return s[1:] if s.startswith("-") and float(s) == 0 else s


def fs(v, nd):
    """Signed fixed-decimal text for the distance column."""
    s = f(v, nd)
    return s if s == "" or s.startswith("-") else "+" + s if float(s) != 0 else s


def sha256_of(b):
    return hashlib.sha256(b).hexdigest()


def git_blob_sha(body):
    """`git hash-object` of the raw bytes. The G19 mutant hashes decoded, newline-normalised text instead of the bytes."""
    if M("blob_on_text"):
        body = body.decode("utf-8", "replace").replace("\r\n", "\n").encode("utf-8")
    return hashlib.sha1(b"blob %d\x00" % len(body) + body).hexdigest()


def mean(xs):
    xs = list(xs)
    return math.fsum(xs) / len(xs) if xs else None


def median(xs):
    xs = list(xs)
    return statistics.median(xs) if xs else None


def months_between(a, b):
    out = []
    y, m = int(a[:4]), int(a[4:6])
    while "%04d%02d" % (y, m) <= b:
        out.append("%04d%02d" % (y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


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
# URL and cache rules (R1, R3, R4, R5) -- G12, G16
# ------------------------------------------------------------------------------------------------------------------------
_RAW_RX = re.compile(r"/jouchinakajima/program/[0-9a-f]{40}/yield_[MD]\.csv")
_RAW_MAIN_RX = re.compile(r"/jouchinakajima/program/[^/]+/yield_[MD]\.csv")
_CONTENTS_RX = re.compile(r"/repos/jouchinakajima/program/contents/yield_[MD]\.csv\?ref=[0-9a-f]{40}")
_COMMITS_RX = re.compile(r"/repos/jouchinakajima/program/commits\?path=yield_[MD]\.csv&per_page=100")
_EXACT = {(SITES, PAGE_PATH), (JMA_HOST, JMA_CSV_PATH), (JMA_HOST, JMA_PAGE_PATH)}


def check_url(url):
    """Only the exact request forms of the spec, over https, on the four allowlisted hosts. Returns (host, target)."""
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    target = p.path + ("?" + p.query if p.query else "")
    if M("allow_any_host"):
        return host, target
    if p.scheme != "https" or p.username or p.password or p.port not in (None, 443) or p.fragment:
        raise Refused("only plain https URLs are allowed")
    if host not in HOST_ALLOW:
        raise Refused("host %s is not on the allowlist" % host)
    if host == GH_RAW:
        ok = _RAW_RX.fullmatch(target) or (M("allow_main") and _RAW_MAIN_RX.fullmatch(target))
    elif host == GH_API:
        ok = _CONTENTS_RX.fullmatch(target) or _COMMITS_RX.fullmatch(target)
    else:
        ok = (host, target) in _EXACT
    if not ok:
        raise Refused("that path is not one of the requests of the spec (raw files must be pinned to a 40-hex commit)")
    return host, target


def check_cache(cache, root=ROOT):
    """R4: the cache must resolve outside the repository root. (The ICE and DTCC precedent; stricter than 'inside but git-ignored'.)"""
    real = os.path.realpath(os.path.expanduser(cache))
    rroot = os.path.realpath(root)
    if M("cache_check_off"):
        return real
    if real == rroot or real.startswith(rroot + os.sep):
        raise Refused("the cache must resolve outside the repository (Nakajima's files are never committed)")
    return real


def status_phrase(host, status):
    """R3 / R2-8: a 403 or 429 from GitHub is rate limiting, never an absent file."""
    if host in (GH_API, GH_RAW) and status in (403, 429):
        if M("rate_as_absent"):
            return "HTTP %d: file absent" % status
        return "HTTP %d: rate limited by GitHub (not a missing file)" % status
    if status == 404:
        return "HTTP 404: not found"
    return "HTTP %d" % status


# ------------------------------------------------------------------------------------------------------------------------
# parsers (every one also serves as the content test of its downloaded file) -- G1, G8, G9, G14
# ------------------------------------------------------------------------------------------------------------------------
NAK_KS = (2, 5, 7, 10, 15, 20)
NAK_COLS = ["ShadowRate"] + ["TermPremium-%dY" % k for k in NAK_KS] + ["ExpectedRate-%dY" % k for k in NAK_KS]
HEADER_SIG_M = '"YYYYMM","ShadowRate","TermPremium-2Y"'
HEADER_SIG_D = '"YYYYMMDD","ShadowRate"'


class Nak:
    def __init__(self, periods, rows, daily):
        self.periods, self.rows, self.daily = periods, rows, daily


def parse_cell(c):
    """Any cell Python's float() parses (scientific notation included). A 4-decimal pattern test is a defect (R3-5, G8)."""
    c = c.strip()
    if c == "":
        raise DataError("blank cell")
    if M("pattern4") and not re.fullmatch(r"-?\d+\.\d{4}", c):
        raise DataError("cell %r is not a 4-decimal number" % c)
    try:
        v = float(c)
    except ValueError:
        raise DataError("cell %r does not parse as a number" % c)
    if not math.isfinite(v):
        raise DataError("cell %r is not finite" % c)
    if M("sign_dropped"):
        v = abs(v)
    if M("scaled100"):
        v *= 100.0
    return v


def parse_nakajima(text, daily=False):
    """The quoted header is read with the csv module (quotes removed) and every column is looked up BY NAME. -> Nak"""
    text = text.lstrip("﻿")
    key = "YYYYMMDD" if daily else "YYYYMM"
    need = [key] + NAK_COLS
    if M("quotes_kept"):
        rows = [ln.split(",") for ln in text.splitlines() if ln.strip()]
    else:
        rows = [r for r in csv.reader(io.StringIO(text, newline=""), skipinitialspace=True) if r and any(c.strip() for c in r)]
    if not rows:
        raise DataError("empty file")
    hdr = [h.strip() for h in rows[0]]
    for n in need:
        if n not in hdr:
            raise DataError("header lacks %r (read by name)" % n)
    idx = {n: i for i, n in enumerate(need)} if M("positional_columns") else {n: hdr.index(n) for n in need}
    periods, out = [], {}
    prx = re.compile(r"\d{8}" if daily else r"\d{6}")
    for r in rows[1:]:
        if len(r) != len(hdr):
            raise DataError("a row has %d cells, the header %d" % (len(r), len(hdr)))
        p = r[idx[key]].strip()
        if not prx.fullmatch(p):
            raise DataError("period %r is not %s" % (p, key))
        if p in out:
            raise DataError("period %s appears twice" % p)
        out[p] = {n: parse_cell(r[idx[n]]) for n in NAK_COLS}
        periods.append(p)
    if not periods:
        raise DataError("no data rows")
    return Nak(periods, out, daily)


def shape_problems(nak, expect_rows=None, expect_last=None):
    """C03: consecutive months from 199501 (monthly file), strictly increasing dates (daily file), the expected row count on the expected vintage."""
    bad = []
    ps = nak.periods
    if nak.daily:
        for a, b in zip(ps, ps[1:]):
            if not a < b:
                bad.append("dates not strictly increasing at %s" % b[:6])
                break
        for p in ps:
            try:
                dt.date(int(p[:4]), int(p[4:6]), int(p[6:8]))
            except ValueError:
                bad.append("impossible date in the %s block" % p[:6])
                break
    else:
        if ps[0] != "199501":
            bad.append("first month is not 199501")
        want = months_between(ps[0], ps[-1])
        if want != ps:
            bad.append("months are not consecutive")
    if expect_rows is not None and len(ps) != expect_rows:
        bad.append("%d rows, expected %d" % (len(ps), expect_rows))
    if expect_last is not None and ps[-1][:6] != expect_last:
        bad.append("last month %s, expected %s" % (ps[-1][:6], expect_last))
    return bad


def parse_mof(text):
    """MoF constant-maturity yields (semiannual compounding, percent, '-' for missing; never 'par yield'). -> {date: {k: float|None}}"""
    rows = list(csv.reader(io.StringIO(text.lstrip("﻿"), newline="")))
    hi = 0 if M("mof_title_as_data") else next((i for i, r in enumerate(rows) if r and r[0].strip() == "Date"), None)
    if hi is None:
        raise DataError("MoF file: no Date header row")
    hdr = [h.strip() for h in rows[hi]]
    if "Date" not in hdr:
        raise DataError("MoF header lacks Date")
    cols = {}
    for i, h in enumerate(hdr):
        m = re.fullmatch(r"(\d+)Y", h)
        if m:
            cols[int(m.group(1))] = i
    if not all(k in cols for k in FIT_K):
        raise DataError("MoF header lacks one of the tenors %r" % (FIT_K,))
    out = {}
    drx = re.compile(r"(\d{4})/(\d{1,2})/(\d{1,2})")
    for r in rows[hi + 1:]:
        if not r:
            continue
        m = drx.fullmatch(r[0].strip())
        if not m:
            continue                                            # footer notes
        d = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        vals = {}
        for k, i in cols.items():
            c = r[i].strip() if i < len(r) else ""
            if c in ("-", ""):
                vals[k] = 0.0 if (M("mof_dash_zero") and c == "-") else None
            else:
                vals[k] = float(c)
        out[d] = vals
    if not out:
        raise DataError("MoF file: no data rows")
    return out


def parse_jma(text):
    """JMA curve-panel: actual rows only (a forecast row is never an end month; G14). -> ({month: {k: (yield, rn, tp)}}, info)"""
    rd = csv.DictReader(io.StringIO(text.lstrip("﻿"), newline=""))
    need = ["YM", "Type"] + ["%s_%dY" % (p, k) for k in (2, 5, 10, 20) for p in ("Yield", "RN", "TP")]
    for n in need:
        if n not in (rd.fieldnames or []):
            raise DataError("JMA header lacks %r" % n)
    out, types, n_rows = {}, {}, 0
    for r in rd:
        n_rows += 1
        ty = (r["Type"] or "").strip().lower()
        types[ty] = types.get(ty, 0) + 1
        if ty != "actual" and not M("jma_forecast_ok"):
            continue
        ym = (r["YM"] or "").strip()
        if not re.fullmatch(r"\d{4}-\d{2}", ym):
            raise DataError("JMA YM %r is not YYYY-MM" % ym)
        row = {}
        for k in (2, 5, 10, 20, 30, 40):
            try:
                tri = tuple(float(r["%s_%dY" % (p, k)]) for p in ("Yield", "RN", "TP"))
            except (KeyError, TypeError, ValueError):
                tri = None
            row[k] = tri
        out[ym[:4] + ym[5:7]] = row
    if not out:
        raise DataError("JMA file: no actual rows")
    return out, dict(types=types, n_rows=n_rows)


def parse_commits(text, fname):
    """The commit list: newest first, each with a 40-hex sha and commit.committer.date. -> [(sha, 'YYYY-MM-DD', 'YYYY-MM-DDTHH:MM:SSZ')]"""
    try:
        js = json.loads(text)
    except ValueError:
        raise DataError("commit list is not JSON")
    if not isinstance(js, list) or not js:
        raise DataError("commit list is not a non-empty list")
    out = []
    for c in js:
        try:
            sha = c["sha"]
            when = c["commit"]["committer"]["date"]
        except (KeyError, TypeError):
            raise DataError("a commit lacks sha or committer date")
        if not HEX40.fullmatch(sha or "") or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", when or ""):
            raise DataError("a commit has a malformed sha or date")
        out.append((sha, when[:10], when))
    return out


def vintage_id(commit):
    """<commit date>_<first 12 hex of the commit sha> (3.6)."""
    return "%s_%s" % (commit[1], commit[0][:12])


def parse_contents(text, fname):
    try:
        js = json.loads(text)
    except ValueError:
        raise DataError("contents reply is not JSON")
    if not isinstance(js, dict) or not HEX40.fullmatch(str(js.get("sha", ""))) or js.get("name", fname) != fname:
        raise DataError("contents reply lacks a blob sha for %s" % fname)
    return js["sha"]


def strip_page(htmltext):
    """Tags removed, entities decoded, all whitespace removed (the page splits its sentences across tags)."""
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", htmltext, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", "", htmllib.unescape(t))


def page_hrefs(htmltext):
    """Every href value, entities decoded and percent-decoded; JSON-escaped slashes undone."""
    raw = htmltext.replace("\\/", "/").replace("\\u003d", "=").replace("\\u0026", "&")
    out = []
    for m in re.finditer(r"""href\s*=\s*(?:"([^"]*)"|'([^']*)')""", raw, flags=re.I):
        out.append(unquote(htmllib.unescape(m.group(1) or m.group(2))))
    return out


def parse_page_status(htmltext):
    """('1995/Jan.', '2026/Sep.', '2026/Oct.') from 'From 1995/Jan. to 2026/Sep. (updated in 2026/Oct.)' after whitespace is stripped."""
    s = strip_page(htmltext)
    m = re.search(r"From(\d{4}/[A-Za-z]{3}\.?)to(\d{4}/[A-Za-z]{3}\.?)\(updatedin(\d{4}/[A-Za-z]{3}\.?)\)", s, flags=re.I)
    return m.groups() if m else None


_MON = {m: i + 1 for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"))}
_MONTH_NAMES = {m: i + 1 for i, m in enumerate(("january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november",
                                                  "december"))}


def page_month(s):
    """'2026/Sep.' -> '202609'."""
    y, m = s.split("/")
    return "%04d%02d" % (int(y), _MON[m.strip(".").lower()[:3]])


def parse_jma_vintage(htmltext):
    """'Model vintage: October 2026, origin September 2026' -> ('2026-10', '2026-09')."""
    t = re.sub(r"<[^>]+>", " ", htmltext)
    t = re.sub(r"\s+", " ", htmllib.unescape(t))
    m = re.search(r"Model vintage:\s*([A-Za-z]+)\s+(\d{4})\s*,\s*origin\s+([A-Za-z]+)\s+(\d{4})", t, flags=re.I)
    if not m:
        return None
    mo, oo = _MONTH_NAMES.get(m.group(1).lower()), _MONTH_NAMES.get(m.group(3).lower())
    if not mo or not oo:
        return None
    return "%s-%02d" % (m.group(2), mo), "%s-%02d" % (m.group(4), oo)


def body_problem(kind, arg, body):
    """The content test of each download: '' if the body is what the request is for, else the reason. Lenient on shape (C03 is strict at build)."""
    try:
        if kind == "commits":
            parse_commits(decode_text(body), arg)
        elif kind == "raw_M":
            n = parse_nakajima(decode_text(body), daily=False)
            if len(n.periods) < 300:
                return "only %d monthly rows" % len(n.periods)
        elif kind == "raw_D":
            n = parse_nakajima(decode_text(body), daily=True)
            if len(n.periods) < 1000:
                return "only %d daily rows" % len(n.periods)
        elif kind == "contents":
            parse_contents(decode_text(body), arg)
        elif kind == "page":
            t = decode_text(body)
            if len(t) < 500 or "nakajima" not in t.lower():
                return "not the Nakajima page"
        elif kind == "jma_csv":
            parse_jma(decode_text(body))
        elif kind == "jma_page":
            t = decode_text(body)
            if len(t) < 200 or "yield" not in t.lower():
                return "not the JMA page"
        else:
            return "unknown kind"
    except DataError as e:
        return str(e)
    return ""


# ------------------------------------------------------------------------------------------------------------------------
# csv output: exact column allowlists, source and citation lines, no causal wording (G11, G13)
# ------------------------------------------------------------------------------------------------------------------------
LOG_COLS = ["utc_time", "host", "path", "status", "bytes", "sha256"]
DEC_COLS = ["vintage_id", "variant", "tenor", "window_id", "start_month", "end_month", "d_yield_pp", "d_tp_pp", "d_er_pp", "tp_share", "distance_bp",
            "classification", "opposite_signs", "role"]
VERDICT_COLS = ["verdict_id", "vintage_id", "tenor", "d_yield_pp", "tp_share", "distance_bp", "classification", "tp_share_2y", "tp_share_5y", "tp_share_10y",
                "tp_share_20y", "d_variant_tp_share", "d_variant_classification", "headline_reading", "jma_tp_share", "jma_label", "jma_arms_fired",
                "boj_match_tp_share", "status", "superseded_by", "vintage_retrieved_utc"]
REV_COLS = ["window_id", "start_month", "end_month", "vintage_id", "d_yield_pp", "d_tp_pp", "d_er_pp", "tp_share", "classification"]
FIT_COLS = ["vintage_id", "file", "tenor", "scope", "basis", "n_periods", "max_abs_gap_pp", "median_abs_gap_pp", "n_over_tol", "status"]
VINT_COLS = ["vintage_id", "source", "file", "commit_sha", "commit_utc", "blob_sha", "sha256", "first_period", "last_period", "n_rows", "stated_update",
             "retrieved_utc", "role"]
PIN_COLS = ["vintage_id", "source", "series", "period", "value", "unit"]
CHECK_COLS = ["check_id", "description", "expected", "observed", "status"]
FILES = ["decomposition.csv", "verdict.csv", "vintage_revisions.csv", "fitted_check.csv", "vintages.csv", "pins.csv", "checks.csv", "fetch_log.csv",
         "README.md", "SOURCES.md"]
ALLOW = {"decomposition.csv": DEC_COLS, "verdict.csv": VERDICT_COLS, "vintage_revisions.csv": REV_COLS, "fitted_check.csv": FIT_COLS,
         "vintages.csv": VINT_COLS, "pins.csv": PIN_COLS, "checks.csv": CHECK_COLS, "fetch_log.csv": LOG_COLS}
CSV_FILES = tuple(ALLOW)

# G13 (R7, R4-5): the project's causal-wording pattern, imported unchanged, plus the local words the spec adds. The guard is the union.
LOCAL_CAUSAL_RX = re.compile(r"\b(led\s+to|prompted|pushed|in\s+response\s+to)\b", re.I)


def causal_hits(text):
    text = text.replace(REQUIRED_SENTENCE, "")
    hits = set()
    if not M("causal_local_only"):
        hits |= {re.sub(r"\s+", " ", m.group(0).lower()) for m in fx.CAUSAL_RX.finditer(text)}
    if not M("causal_fx_only"):
        hits |= {re.sub(r"\s+", " ", m.group(0).lower()) for m in LOCAL_CAUSAL_RX.finditer(text)}
    return sorted(hits)


BOJ_RX = re.compile(r"\b(BoJ|Bank of Japan|the Bank)\b")
VERDICT_RX = re.compile(r"\b(consistent\s+with|agrees?|agreed|agreement|disagrees?|disagreed|disagreement|contradicts?|contradicted|confirms?|confirmed|"
                        r"in\s+line\s+with|supports?)\b", re.I)


def boj_label_hits(text):
    """G20 (R3-8): an agree-or-disagree verdict on the Bank's wording, i.e. a verdict word in the same paragraph as a mention of the Bank."""
    hits = []
    for para in re.split(r"\n\s*\n", text):
        if BOJ_RX.search(para):
            for m in VERDICT_RX.finditer(para):
                hits.append(m.group(0).lower())
    if M("boj_label_ok"):
        return []
    return sorted(set(hits))


def allowlist(name):
    cols = list(ALLOW[name])
    if M("allow_extra_col") and name == "decomposition.csv":
        cols.append("extra")
    return cols


def files_list():
    out = list(FILES)
    if M("file_not_in_files"):
        out.append("notes.md")
    return out


def check_header(name, header):
    if list(header) != allowlist(name):
        raise DataError("%s: header %r is not the exact column allowlist" % (name, list(header)))


def guard_text(name, text):
    hits = causal_hits(text)
    if hits and not M("causal_guard_off"):
        raise DataError("%s: causal wording %s" % (name, hits))
    if name in ("README.md",) + CSV_FILES and boj_label_hits(text):
        raise DataError("%s: a verdict word beside the Bank of Japan (R3-8)" % name)
    home = os.path.expanduser("~")
    if home != "~" and home in text:
        raise DataError("%s: an absolute home path would be published" % name)


def render_csv(name, rows, source, header=None, extra_comments=()):
    header = allowlist(name) if header is None else header
    check_header(name, header)
    out = io.StringIO()
    out.write(source + "\n")
    out.write(CITE_LINE + "\n")
    for c in extra_comments:
        out.write(c + "\n")
    w = csv.writer(out, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        if len(r) != len(header):
            raise DataError("%s: a row has %d cells, the header %d" % (name, len(r), len(header)))
        w.writerow(r)
    text = out.getvalue()
    guard_text(name, text)
    return text


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


def read_csv_rows(path):
    """(header, rows) of a csv with comment lines (# ...) skipped; ([], []) if absent."""
    if not os.path.exists(path):
        return [], []
    with open(path, encoding="utf-8", newline="") as fh:
        return read_csv_text(fh.read())


def read_csv_text(text):
    lines = [ln for ln in text.splitlines(True) if not ln.startswith("#")]
    rd = list(csv.reader(io.StringIO("".join(lines), newline="")))
    return (rd[0], rd[1:]) if rd else ([], [])


# ------------------------------------------------------------------------------------------------------------------------
# the static STOP scan (G12): no code in this file removes or renames the STOP file
# ------------------------------------------------------------------------------------------------------------------------
_REMOVERS_ANY = {"unlink", "rename", "rmdir", "rmtree", "remove", "removedirs", "move", "renames"}
_STOP_NAMES = {"STOP", "STOP_PATH", "stop_path", "stop_file"}


def static_stop_scan(source):
    """AST scan: a function that mentions the STOP path or the string 'STOP' and also calls remove, unlink, rename, os.replace, rmtree or move is
    reported as 'function:line'. Returns a list of strings."""
    tree = ast.parse(source)
    hits = []

    def mentions_stop(node):
        for n in ast.walk(node):
            if isinstance(n, ast.Name) and n.id in _STOP_NAMES:
                return True
            if isinstance(n, ast.Attribute) and n.attr in _STOP_NAMES:
                return True
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and re.search(r"\bSTOP\b", n.value) and len(n.value) < 40:
                return True
        return False

    def removers(node):
        out = []
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                fn = n.func
                name = fn.attr if isinstance(fn, ast.Attribute) else fn.id if isinstance(fn, ast.Name) else ""
                base = fn.value.id if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name) else ""
                if name in _REMOVERS_ANY and (base in ("os", "shutil", "pathlib") or (isinstance(fn, ast.Attribute) and name in ("unlink", "rename", "rmdir"))):
                    out.append(n.lineno)
                elif name == "replace" and base in ("os", "shutil"):
                    out.append(n.lineno)
        return out

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            r = removers(node)
            if r and mentions_stop(node):
                hits.append("%s:%d" % (node.name, r[0]))
    return hits


STOP_REMOVER_SOURCE = "\ndef clear_stop():\n    import os\n    os.remove(STOP_PATH)\n"


def own_source():
    with open(os.path.abspath(__file__), encoding="utf-8") as fh:
        return fh.read()


# ------------------------------------------------------------------------------------------------------------------------
# the fetch log and fetching: the only network code
# ------------------------------------------------------------------------------------------------------------------------
def real_opener(host, target, headers, timeout, cap):
    """GET https://host/target. Returns (status, body, response headers); body is None when it exceeds `cap`. No redirect is followed (a 3xx comes back as
    a status and latches), no cookies, the only verb is GET. Socket-level faults raise SocketFault."""
    conn = http.client.HTTPSConnection(host, timeout=timeout)
    try:
        conn.request("GET", target, headers=dict(headers))
        resp = conn.getresponse()
        status = resp.status
        hdrs = {k.lower(): v for k, v in resp.getheaders()}
        if status != 200:
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


def log_source(rows):
    days = sorted({r[0][:10] for r in rows if r[3] == "200" and r[4]})
    return "# source: request log of bin/japan_term_premium.py fetch (one row per request; hosts %s); retrieved %s" % (
        ", ".join(sorted(HOST_ALLOW)), ", ".join(days) if days else "(no logged retrieval)")


class Fetcher:
    """All requests go through here. Injectable opener, clock, sleeper and STOP path make it testable without a network."""

    def __init__(self, cache, out_dir, sleep=MIN_SLEEP, max_requests=MAX_REQUESTS, opener=real_opener, wall=time.time, mono=time.monotonic,
                 sleeper=time.sleep, stop_path=STOP_PATH, utc=None, root=ROOT):
        if sleep < 2.0 and not M("no_pacing"):
            raise Refused("--sleep must be at least 2 seconds")
        if (max_requests > MAX_REQUESTS and not M("no_request_cap")) or max_requests < 1:
            raise Refused("--max-requests must be between 1 and %d" % MAX_REQUESTS)
        self.out_dir = out_dir
        self.cache = check_cache(cache, root=root)
        self.sleep, self.max_requests = float(sleep), max_requests
        self.opener, self.wall, self.mono, self.sleeper = opener, wall, mono, sleeper
        self.stop_path = stop_path
        self.utc = utc or (lambda: dt.datetime.now(dt.timezone.utc))
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
        write_text(self.log_path, render_csv("fetch_log.csv", rows, log_source(rows)))

    def _latch(self, reason):
        os.makedirs(os.path.dirname(self.stop_path), exist_ok=True)
        with open(self.stop_path, "w", encoding="utf-8") as fh:
            fh.write("%s UTC  %s\n" % (self.utc().strftime("%Y-%m-%dT%H:%M:%S"), reason))
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
            status, body, rh = self.opener(host, target, dict(HEADERS), TIMEOUT, BODY_CAP)
        except SocketFault:
            self._log(started, host, target, "socket_fault", "", "")
            raise
        return status, body, rh, started

    def _done_today(self, host, target):
        today = self.utc().strftime("%Y-%m-%d")
        _, rows = read_csv_rows(self.log_path)
        return any(r[1] == host and r[2] == target and r[3] == "200" and r[4] and r[0][:10] == today for r in rows)

    def fetch_one(self, req):
        """Returns an outcome word; raises Latched / SocketFault / MaxRequests / Refused."""
        path = os.path.join(self.cache, req["file"])
        if os.path.exists(path) and (req["immutable"] or self._done_today(req["host"], req["target"])):
            return "cached"
        self.check_stop()
        status, body, rh, started = self._get(req["host"], req["target"])
        if status != 200:
            self._log(started, req["host"], req["target"], status, "", "")
            redirect = status // 100 == 3
            if not M("no_latch_redirect" if redirect else "no_latch_non200"):
                what = status_phrase(req["host"], status)
                self._latch("%s%s for %s" % ("a redirect (not followed), " if redirect else "", what, req["target"][:90]))
            return "refused_unlatched"
        problem = "body larger than the cap" if body is None else body_problem(req["kind"], req["arg"], body)
        self._log(started, req["host"], req["target"], status, len(body or b""), sha256_of(body or b""))
        if problem:
            if not M("no_latch_bad_body"):
                self._latch("200 but not the expected file (%s) for %s" % (problem, req["target"][:90]))
            return "refused_unlatched"
        os.makedirs(self.cache, exist_ok=True)
        with open(path + ".part", "wb") as fh:
            fh.write(body)
        os.replace(path + ".part", path)
        return "saved"


def req_commits(fname):
    return dict(host=GH_API, target=COMMITS_PATH.format(f=fname), file="commits_%s.json" % fname[:-4], kind="commits", arg=fname, immutable=False)


def req_raw(fname, sha):
    return dict(host=GH_RAW, target=RAW_PATH.format(sha=sha, f=fname), file="%s_%s.csv" % (fname[:-4], sha), kind="raw_" + fname[6], arg=fname,
                immutable=True)


def req_contents(fname, sha):
    return dict(host=GH_API, target=CONTENTS_PATH.format(f=fname, sha=sha), file="contents_%s_%s.json" % (fname[:-4], sha), kind="contents", arg=fname,
                immutable=True)


STATIC_REQS = [dict(host=SITES, target=PAGE_PATH, file="nakajima_page.html", kind="page", arg=None, immutable=False),
               dict(host=JMA_HOST, target=JMA_CSV_PATH, file="jma_curve_panel.csv", kind="jma_csv", arg=None, immutable=False),
               dict(host=JMA_HOST, target=JMA_PAGE_PATH, file="jma_page.html", kind="jma_page", arg=None, immutable=False)]


def newest_sha(cache, fname):
    with open(os.path.join(cache, req_commits(fname)["file"]), encoding="utf-8") as fh:
        return parse_commits(fh.read(), fname)[0][0]


def run_fetch(fe, say=print):
    """The 11 requests, in order: the two commit lists; the raw files at the newest commit of each; the two contents replies at that commit; the page;
    the two JMA files; the July and April vintages of the monthly file."""
    saved = 0
    for r in [req_commits(fn) for fn in FILES_N]:
        out = fe.fetch_one(r)
        saved += out == "saved"
        say("%-48s %s" % (r["file"], out))
    shas = {fn: newest_sha(fe.cache, fn) for fn in FILES_N}
    later = [req_raw(fn, shas[fn]) for fn in FILES_N] + [req_contents(fn, shas[fn]) for fn in FILES_N] + STATIC_REQS + [
        req_raw("yield_M.csv", JULY_SHA), req_raw("yield_M.csv", APRIL_SHA)]
    seen = set()
    for r in later:
        if r["file"] in seen:
            continue
        seen.add(r["file"])
        out = fe.fetch_one(r)
        saved += out == "saved"
        say("%-48s %s" % (r["file"], out))
    return saved


# ------------------------------------------------------------------------------------------------------------------------
# series, changes, the share and the rule (spec sections 3.1 to 3.4) -- G1 to G7, G14, G15, G17
# ------------------------------------------------------------------------------------------------------------------------
class Ser:
    """One variant's term premium and expected rate by month and tenor (percent)."""

    def __init__(self, tp, er, label=""):
        self.tp, self.er, self.label = tp, er, label


def nak_to_ser(nak, label="M"):
    return Ser({k: {p: nak.rows[p]["TermPremium-%dY" % k] for p in nak.periods} for k in NAK_KS},
               {k: {p: nak.rows[p]["ExpectedRate-%dY" % k] for p in nak.periods} for k in NAK_KS}, label)


def daily_to_ser(nak, label="D"):
    """D: the monthly mean of the month's daily rows (G17). The month-end value is the mutant."""
    by = {}
    for p in nak.periods:
        by.setdefault(p[:6], []).append(p)
    tp, er = {k: {} for k in NAK_KS}, {k: {} for k in NAK_KS}
    for m, ps in by.items():
        for k in NAK_KS:
            xs = [nak.rows[p]["TermPremium-%dY" % k] for p in ps]
            ys = [nak.rows[p]["ExpectedRate-%dY" % k] for p in ps]
            tp[k][m] = xs[-1] if M("d_month_end") else mean(xs)
            er[k][m] = ys[-1] if M("d_month_end") else mean(ys)
    return Ser(tp, er, label)


def jma_to_ser(jma, label="JMA"):
    tp, er = {k: {} for k in (2, 5, 10, 20)}, {k: {} for k in (2, 5, 10, 20)}
    for m, row in jma.items():
        for k in (2, 5, 10, 20):
            if row.get(k):
                tp[k][m] = row[k][2]
                er[k][m] = row[k][1]
    return Ser(tp, er, label)


def month_value(sers, which, k, m):
    """The value in month m from the FIRST vintage only (R6, G7). The `fill_older` mutant falls back to the next one."""
    for s in sers:
        v = getattr(s, which)[k].get(m)
        if v is not None:
            return v
        if not M("fill_older"):
            break
    raise DataError("month %s is missing at %dY in this vintage (months are never filled from another vintage)" % (m, k))


def stat_vintage(sers, k, a, b):
    """(d_tp, d_er) over the window a -> b from ONE vintage (sers[0]); the base is the first named month (O-3). sers: newest first."""
    s_start = [sers[-1]] if (M("mix_vintages") and len(sers) > 1) else sers
    tp_a, er_a = month_value(s_start, "tp", k, a), month_value(s_start, "er", k, a)
    tp_b, er_b = month_value(sers, "tp", k, b), month_value(sers, "er", k, b)
    if M("change_reversed"):
        return tp_a - tp_b, er_a - er_b
    return tp_b - tp_a, er_b - er_a


def window_months(wid):
    a, b = WINDOWS[wid]
    if M("b_from_202407") and wid == "B":
        a = "202407"
    if M("bridge_dropped") and wid == "BRIDGE":
        b = a
    if M("y2526_from_202501") and wid == "Y2025_26":
        a = "202501"
    if M("y2024_to_202411") and wid == "Y2024":
        b = "202411"
    return a, b


class Stat:
    __slots__ = ("d_tp", "d_er", "d_yield", "share", "distance", "cls", "opposite")

    def __init__(self, d_tp, d_er, d_yield, share, distance, cls, opposite):
        self.d_tp, self.d_er, self.d_yield, self.share, self.distance, self.cls, self.opposite = d_tp, d_er, d_yield, share, distance, cls, opposite


def classify(wid, d_tp, d_er):
    """The rule of 3.2 as amended by R3-1, checked in this order: dy under 0.25 -> NOT_CLASSIFIED; the BRIDGE window -> NOT_APPLICABLE; 0.40 <= s <= 0.60
    inclusive -> CLOSE_TO_EVEN; above -> TERM_PREMIUM_LARGER; below -> EXPECTED_RATES_LARGER. The share is computed unrounded; the comparisons use it
    rounded to 9 decimals so that float error cannot move an edge (the cells carry 4 decimals)."""
    opposite = d_tp * d_er < 0
    if M("abs_share"):
        a_tp, a_er = abs(d_tp), abs(d_er)
        dy = a_tp + a_er
    else:
        a_tp, a_er = d_tp, d_er
        dy = d_tp + d_er
    thr = 0.24 if M("dy_classifies_2499") else DY_MIN
    dyr = round(dy, 9)
    below = dyr <= thr if M("dy_025_excluded") else dyr < thr
    if below:
        sh = None
        if M("share_filled_nc") and dy != 0:
            sh = a_tp / dy
        return Stat(d_tp, d_er, d_tp + d_er, sh, None, "NOT_CLASSIFIED", opposite)
    if wid == "BRIDGE":
        return Stat(d_tp, d_er, d_tp + d_er, None, None, "NOT_APPLICABLE", opposite)
    if M("share_er_numerator"):
        s = a_er / dy
    elif M("share_tp_over_er"):
        s = a_tp / a_er if a_er != 0 else 0.0
    else:
        s = a_tp / dy
    sr = s if M("band_unrounded") else round(s, 9)
    lo, hi = BAND
    if M("band_low_wide"):
        lo = 0.39
    if M("band_high_wide"):
        hi = 0.61
    inside = (lo < sr < hi) if M("band_exclusive") else (lo <= sr <= hi)
    if M("no_close_band"):
        cls = "TERM_PREMIUM_LARGER" if sr > 0.5 else "EXPECTED_RATES_LARGER"
    elif inside:
        cls = "CLOSE_TO_EVEN"
    elif sr > hi:
        cls = "TERM_PREMIUM_LARGER"
    else:
        cls = "EXPECTED_RATES_LARGER"
    dist = (s - 0.5) * 100.0 if M("distance_no_dy") else (s - 0.5) * dy * 100.0
    return Stat(d_tp, d_er, d_tp + d_er, s, dist, cls, opposite)


def window_stat(sers, k, wid):
    a, b = window_months(wid)
    d_tp, d_er = stat_vintage(sers, k, a, b)
    return classify(wid, d_tp, d_er)


def r6(x):
    return round(x, 6)


def jma_arms(m_dtp, j_dtp, s_m, s_j):
    """3.4 (R2-1, R3-3): three strict arms on values rounded to 6 decimals. -> (label, arms_fired_text)"""
    le = M("arm_le")
    arms = []
    if m_dtp > 0:
        lo, hi, j = r6(0.5 * m_dtp), r6(2.0 * m_dtp), r6(j_dtp)
        fire = (j <= lo or j >= hi) if le else (j < lo or j > hi)
    else:
        fire = (math.copysign(1, j_dtp) != math.copysign(1, m_dtp) and j_dtp != 0) or r6(abs(j_dtp)) < r6(0.5 * abs(m_dtp)) or r6(abs(j_dtp)) > r6(2.0 * abs(m_dtp))
    if fire and not M("arm_dropped_ratio"):
        arms.append("ratio")
    if s_m is not None and s_j is not None:
        if not M("arm_dropped_share"):
            diff = abs(s_m - s_j) if M("arms_unrounded") else r6(abs(s_m - s_j))
            if (diff >= 0.15) if le else (diff > 0.15):
                arms.append("share")
        if not M("arm_dropped_side"):
            prod = r6(s_m - 0.5) * r6(s_j - 0.5)
            if (prod <= 0) if le else (prod < 0):
                arms.append("side")
    if M("arms_missing") and arms:
        arms = arms[:-1]
    return ("model_sensitive" if arms else "not_flagged"), "+".join(arms)


def headline_reading(cls_m, cls_d):
    """R2-2: close to even and model-dependent when M and D are both inside the band; the shared classification when both are outside it and agree;
    otherwise the two files differ. The `headline_ignores_d` mutant reads M twice."""
    if M("headline_ignores_d"):
        cls_d = cls_m
    if cls_m == "CLOSE_TO_EVEN" and cls_d == "CLOSE_TO_EVEN":
        return "close_to_even_and_model_dependent"
    if cls_m == cls_d and cls_m in ("TERM_PREMIUM_LARGER", "EXPECTED_RATES_LARGER"):
        return cls_m
    return "differs_between_monthly_and_daily_files"


def role_of(variant, wid, tenor):
    if variant == "D":
        return "SENSITIVITY"
    if variant == "JMA":
        return "CROSSCHECK"
    if wid == "FULL":
        return "REGISTERED" if tenor == "10Y" else "SAME_RULE"
    if wid in ("A", "B"):
        return "SUBWINDOW"
    if wid == "BRIDGE":
        return "BRIDGE"
    return "CROSSCHECK_NONINDEPENDENT"


def decomposition(variant, ser, vid):
    """The 28 rows of one variant: 4 tenors x 7 windows. -> (rows, {(tenor, wid): Stat})"""
    stats, rows = {}, []
    for wid in WINDOW_ORDER:
        for t in TENORS:
            st = window_stat([ser], TK[t], wid)
            stats[(t, wid)] = st
            a, b = WINDOWS[wid]
            rows.append([vid, variant, t, wid, a, b, f(st.d_yield, 4), f(st.d_tp, 4), f(st.d_er, 4), f(st.share, 4), fs(st.distance, 1), st.cls,
                         "yes" if st.opposite else "no", role_of(variant, wid, t)])
    return rows, stats


def identity_problems(stats):
    """C12: FULL = A + BRIDGE + B and FULL = Y2024 + Y2025_26, on d_tp, d_er and d_yield, unrounded, 1e-9."""
    bad = []
    for t in TENORS:
        full = stats[(t, "FULL")]
        for label, parts in (("A+BRIDGE+B", ("A", "BRIDGE", "B")), ("Y2024+Y2025_26", ("Y2024", "Y2025_26"))):
            for fld in ("d_tp", "d_er", "d_yield"):
                tot = sum(getattr(stats[(t, w)], fld) for w in parts)
                if abs(getattr(full, fld) - tot) > TOL_ADD:
                    bad.append("%s %s: FULL != %s" % (t, fld, label))
        for w in WINDOW_ORDER:
            st = stats[(t, w)]
            if abs(st.d_yield - (st.d_tp + st.d_er)) > TOL_ADD:
                bad.append("%s %s: d_yield != d_tp + d_er" % (t, w))
    return bad


# ------------------------------------------------------------------------------------------------------------------------
# the fitted-yield check (3.7) -- G9
# ------------------------------------------------------------------------------------------------------------------------
def tol_pub():
    return 0.002 if M("tol_loose_pub") else TOL_PUB


def tol_recomp():
    return 1e-4 if M("tol_loose_recomp") else TOL_RECOMP


def within_pub(gap):
    return abs(gap) <= tol_pub()


def within_recomp(a, b):
    return abs(a - b) <= tol_recomp()


def mof_by_month(mof, k):
    """{month: [(date, value)] sorted, non-missing only} for the k-year constant-maturity yield."""
    out = {}
    for d in sorted(mof):
        v = mof[d].get(k)
        if v is not None:
            out.setdefault("%04d%02d" % (d.year, d.month), []).append((d, v))
    return out


def fitted_monthly(ser, bym, k, months, basis="mean"):
    """gap_m = TP_k(m) + ER_k(m) minus the MoF reference of month m; only months with at least 10 non-missing MoF days. -> [(month, gap)]"""
    gaps = []
    for m in months:
        vals = bym.get(m, [])
        if len(vals) < MIN_MOF_DAYS or m not in ser.tp[k] or m not in ser.er[k]:
            continue
        use_end = (basis == "month_end") != bool(M("fit_month_end_basis") and basis == "mean")
        ref = vals[-1][1] if use_end else mean(v for _, v in vals)
        model = ser.tp[k][m] - ser.er[k][m] if M("fit_tp_minus_er") else ser.tp[k][m] + ser.er[k][m]
        gaps.append((m, model - ref))
    return gaps


def fitted_daily(nak, mof, k, d_lo, d_hi):
    """D: the gap on each date present in both files over the window. -> (gaps [(date, gap)], n_only_d, n_only_mof)"""
    gaps, only_d = [], 0
    dd = {}
    for p in nak.periods:
        d = dt.date(int(p[:4]), int(p[4:6]), int(p[6:8]))
        if d_lo <= d <= d_hi:
            dd[d] = nak.rows[p]
    md = {d: mof[d].get(k) for d in mof if d_lo <= d <= d_hi and mof[d].get(k) is not None}
    for d, row in sorted(dd.items()):
        if d in md:
            gaps.append((d, row["TermPremium-%dY" % k] + row["ExpectedRate-%dY" % k] - md[d]))
        else:
            only_d += 1
    only_m = sum(1 for d in md if d not in dd)
    return gaps, only_d, only_m


def gap_summary(gaps):
    """(n, max |gap|, median |gap|, n over the published-cell tolerance)"""
    a = [abs(g) for _, g in gaps]
    n_over = sum(1 for x in a if not within_pub(x))
    return len(a), (max(a) if a else None), (median(a) if a else None), n_over


def recomputed_mean_problems(nak, months):
    """C12: the monthly mean of the daily rows, recomputed a second way (sequential sum) agrees at 1e-6."""
    by = {}
    for p in nak.periods:
        by.setdefault(p[:6], []).append(p)
    bad = []
    for m in months:
        for k in NAK_KS:
            for col in ("TermPremium-%dY" % k, "ExpectedRate-%dY" % k):
                xs = [nak.rows[p][col] for p in by.get(m, [])]
                if not xs:
                    continue
                tot = 0.0
                for x in xs:
                    tot += x
                if not within_recomp(mean(xs), tot / len(xs)):
                    bad.append("%s %s" % (m, col))
    return bad


# ------------------------------------------------------------------------------------------------------------------------
# the frozen verdict (R9, 3.6) -- G7, G18
# ------------------------------------------------------------------------------------------------------------------------
V_IX = {c: i for i, c in enumerate(VERDICT_COLS)}
V_CONTENT = [c for c in VERDICT_COLS if c not in ("verdict_id", "status", "superseded_by", "vintage_retrieved_utc")]


def reconcile_verdict(existing, fresh, vid, retrieved, amend=None):
    """existing: the committed verdict rows (lists); fresh: {tenor: content dict of V_CONTENT} for the vintage `vid`.
    - no live row for this vintage: append `registered` rows if the file has no registered row at all, else `later_vintage` rows;
    - live rows for this vintage whose content equals the fresh content are kept byte for byte;
    - a changed frozen value raises DataError unless `amend` (a reason) is given: then the old row becomes `superseded` (never deleted) and an
      `amended` row is appended.
    -> (rows, notes)"""
    rows = [list(r) for r in existing]
    live = {r[V_IX["verdict_id"]]: r for r in rows if r[V_IX["vintage_id"]] == vid and r[V_IX["status"]] in ("registered", "later_vintage", "amended")}
    has_reg = any(r[V_IX["status"]] in ("registered", "superseded") for r in rows)
    notes = []
    for t in TENORS:
        content = fresh[t]
        key = [r for r in live.values() if r[V_IX["tenor"]] == t]
        if key:
            old = key[0]
            if all(old[V_IX[c]] == content[c] for c in V_CONTENT):
                continue
            if not amend and not M("silent_overwrite"):
                diffs = [c for c in V_CONTENT if old[V_IX[c]] != content[c]]
                raise DataError("frozen verdict row %s changed (%s); a rebuild on the same vintage may not change it without --amend" % (
                    old[V_IX["verdict_id"]], ", ".join(diffs)))
            if M("silent_overwrite") and not amend:
                for c in V_CONTENT:
                    old[V_IX[c]] = content[c]
                continue
            n_am = sum(1 for r in rows if r[V_IX["status"]] == "amended" and r[V_IX["tenor"]] == t) + 1
            new_id = "M-%s-FULL@%s#%d" % (t, vid, n_am)
            if M("amend_deletes_old"):
                rows.remove(old)
            else:
                old[V_IX["status"]] = "superseded"
                old[V_IX["superseded_by"]] = new_id
            new = [""] * len(VERDICT_COLS)
            for c in V_CONTENT:
                new[V_IX[c]] = content[c]
            new[V_IX["verdict_id"]], new[V_IX["vintage_id"]], new[V_IX["status"]] = new_id, vid, "amended"
            new[V_IX["vintage_retrieved_utc"]] = retrieved
            rows.append(new)
            notes.append("amended %s: %s" % (old[V_IX["verdict_id"]], amend))
            continue
        new = [""] * len(VERDICT_COLS)
        for c in V_CONTENT:
            new[V_IX[c]] = content[c]
        first = not has_reg
        new[V_IX["verdict_id"]] = "M-%s-FULL" % t if first else "M-%s-FULL@%s" % (t, vid)
        new[V_IX["vintage_id"]], new[V_IX["status"]] = vid, "registered" if first else "later_vintage"
        new[V_IX["vintage_retrieved_utc"]] = retrieved
        if M("rewrite_registered") and has_reg:
            for r in rows:
                if r[V_IX["status"]] == "registered" and r[V_IX["tenor"]] == t:
                    for c in V_CONTENT:
                        r[V_IX[c]] = content[c]
                    r[V_IX["vintage_id"]] = vid
            continue
        rows.append(new)
    return rows, notes


# ------------------------------------------------------------------------------------------------------------------------
# the licence and leak guard (section 6) -- G10
# ------------------------------------------------------------------------------------------------------------------------
PIN_CAPS = {"nakajima_monthly": 4, "nakajima_daily": 0, "mof": 4, "jma": 3}
PIN_SERIES_NAK = ("TermPremium-10Y", "ExpectedRate-10Y")
JULY_VID_PREFIX, APRIL_VID_PREFIX = "2026-07-06_80f7108a1637", "2026-04-20_8f940a0141ee"
MONTH_RX = re.compile(r"(?<![0-9A-Za-z_.])(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?![0-9A-Za-z_])")
DAY_RX = re.compile(r"(?<![0-9A-Za-z_.])(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])(?![0-9A-Za-z_])")
NUM4_RX = re.compile(r"(?<![0-9A-Za-z_.])-?\d+\.\d{3,}(?![0-9A-Za-z_])")
LEVEL_NAME_RX = re.compile(r"(?:\b(?:TP|ER)\d{1,2}\b|\bShadowRate\b|\b(?:TermPremium|ExpectedRate)\b)[^|]{0,24}?-?\d+\.\d{3,}")
HDR_SIG_RX = re.compile(r'^\s*"YYYYMM(?:DD)?"\s*,\s*"ShadowRate"', re.M)


def raw_triples(raw, nd):
    """The set of three consecutive raw levels (same column, consecutive rows), rounded to nd decimals, ignoring three equal values."""
    out = set()
    for nak in raw:
        for col in NAK_COLS:
            vals = [round(nak.rows[p][col], nd) for p in nak.periods]
            for i in range(len(vals) - 2):
                t = (vals[i], vals[i + 1], vals[i + 2])
                if len(set(t)) > 1:
                    out.add(t)
    return out


def _num_columns(text):
    h, rows = read_csv_text(text)
    cols = []
    for i, name in enumerate(h):
        vals, dec = [], []
        for r in rows:
            if i >= len(r):
                continue
            c = r[i].strip()
            if re.fullmatch(r"[+-]?\d+\.\d+", c):
                vals.append(float(c))
                dec.append(len(c.split(".")[1]))
        if len(vals) == len(rows) and vals:
            cols.append((name, vals, min(dec)))
    return cols


def leak_guard(texts, raw=None):
    """texts: {file name: text} for the whole folder. -> list of problems, each starting '(a)' to '(g)'. An empty list is a pass.
    (a) a line that is Nakajima's quoted header; (b) a file not on the FILES list; (c) a header that is not the exact allowlist; (d) pin caps by vintage
    and source; (e) a numeric column (3 or more decimals) that holds three consecutive raw levels; (f) a month or a daily date outside the seven-month
    list; (g) a level in checks.csv beyond the pins."""
    bad = []
    names = list(texts)
    for name in names:
        t = texts[name]
        if HDR_SIG_RX.search(t) and not M("leak_a_off"):
            bad.append("(a) %s holds Nakajima's quoted header line" % name)
        if name not in files_list() and not M("leak_b_off"):
            bad.append("(b) %s is not on the FILES list" % name)
    for name in CSV_FILES:
        if name in texts and not M("leak_c_off"):
            h, _ = read_csv_text(texts[name])
            if h != allowlist(name):
                bad.append("(c) %s: header is not the exact column allowlist" % name)
    if "pins.csv" in texts:
        h, rows = read_csv_text(texts["pins.csv"])
        if h == PIN_COLS:
            cnt = {}
            for r in rows:
                src = r[1]
                if src != "nakajima_daily":
                    cnt[(r[0], src)] = cnt.get((r[0], src), 0) + 1
                if src == "nakajima_daily" and not M("leak_d_daily_off"):
                    bad.append("(d) pins.csv: a pin for a daily-file vintage (%s)" % r[0])
                if src == "nakajima_monthly":
                    if r[0].startswith(APRIL_VID_PREFIX) and not M("leak_d_april_off"):
                        bad.append("(d) pins.csv: a pin for the April vintage")
                    if r[0].startswith(JULY_VID_PREFIX) and r[3] != "202606":
                        bad.append("(d) pins.csv: the July vintage may pin only one month")
                    if r[2] not in PIN_SERIES_NAK or r[3] not in MONTH_LIST:
                        bad.append("(d) pins.csv: %s %s is outside the permitted pins" % (r[2], r[3]))
            for (vid, src), n in cnt.items():
                cap = PIN_CAPS.get(src, 0)
                if n > cap and not M("leak_d_cap_off"):
                    bad.append("(d) pins.csv: %d pins for %s %s (cap %d)" % (n, src, vid, cap))
    if raw and not M("leak_e_off"):
        t3 = {nd: raw_triples(raw, nd) for nd in (3, 4)}
        for name in CSV_FILES:
            if name not in texts or name in ("fetch_log.csv", "pins.csv"):
                continue
            for cname, vals, nd in _num_columns(texts[name]):
                if nd < 3 or len(vals) < 3:
                    continue
                nd = min(nd, 4)
                tri = t3[nd]
                for i in range(len(vals) - 2):
                    a = (round(vals[i], nd), round(vals[i + 1], nd), round(vals[i + 2], nd))
                    if len(set(a)) > 1 and (a in tri or a[::-1] in tri):
                        bad.append("(e) %s column %s holds three consecutive raw monthly levels" % (name, cname))
                        break
    if not M("leak_f_off"):
        allowed = set(MONTH_LIST)
        for name in names:
            t = texts[name]
            if name == "fetch_log.csv":
                h, rows = read_csv_text(t)
                t = "\n".join(",".join(r[:4]) for r in rows)
            found = set(MONTH_RX.findall(t)) - allowed
            days = set(DAY_RX.findall(t))
            if found or days:
                bad.append("(f) %s holds %s outside the seven-month list" % (name, ", ".join(sorted(found | days))[:60]))
    if "checks.csv" in texts and not M("leak_g_off"):
        h, rows = read_csv_text(texts["checks.csv"])
        pin_vals = set()
        if "pins.csv" in texts:
            ph, pr = read_csv_text(texts["pins.csv"])
            pin_vals = {float(r[4]) for r in pr if len(r) > 4 and r[1].startswith("nakajima") and re.fullmatch(r"[+-]?\d+\.\d+", r[4])}
        for r in rows:
            if len(r) != 5:
                continue
            cell = " | ".join(r[1:4])
            if r[0].startswith(("C04", "C08")) and r[3] and NUM4_RX.search(r[3]):
                bad.append("(g) checks.csv %s: a number in a level check's observed cell" % r[0])
            if LEVEL_NAME_RX.search(cell):
                bad.append("(g) checks.csv %s: a named level" % r[0])
            for tok in NUM4_RX.findall(cell):
                if float(tok) in pin_vals:
                    bad.append("(g) checks.csv %s: a pinned level value" % r[0])
                    break
    return bad


# ------------------------------------------------------------------------------------------------------------------------
# inputs, vintages and the build (sections 3.6, 5, 7)
# ------------------------------------------------------------------------------------------------------------------------
class Inputs:
    pass


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def load_inputs(cache, mof_path):
    inp = Inputs()
    inp.cache = cache
    inp.commits = {}
    for fn in FILES_N:
        inp.commits[fn] = parse_commits(decode_text(read_bytes(os.path.join(cache, req_commits(fn)["file"]))), fn)
    inp.newest = {fn: inp.commits[fn][0] for fn in FILES_N}
    inp.raw = {}
    for fn, sha in (("yield_M.csv", inp.newest["yield_M.csv"][0]), ("yield_D.csv", inp.newest["yield_D.csv"][0]), ("yield_M.csv", JULY_SHA),
                    ("yield_M.csv", APRIL_SHA)):
        body = read_bytes(os.path.join(cache, req_raw(fn, sha)["file"]))
        inp.raw[(fn, sha)] = (body, parse_nakajima(decode_text(body), daily=fn == "yield_D.csv"))
    inp.contents = {}
    for fn in FILES_N:
        sha = inp.newest[fn][0]
        inp.contents[fn] = parse_contents(decode_text(read_bytes(os.path.join(cache, req_contents(fn, sha)["file"]))), fn)
    inp.page = decode_text(read_bytes(os.path.join(cache, "nakajima_page.html")))
    inp.jma_bytes = read_bytes(os.path.join(cache, "jma_curve_panel.csv"))
    inp.jma_page = decode_text(read_bytes(os.path.join(cache, "jma_page.html")))
    inp.jma, inp.jma_info = parse_jma(decode_text(inp.jma_bytes))
    inp.mof_bytes = read_bytes(mof_path)
    inp.mof = parse_mof(decode_mof(inp.mof_bytes))
    inp.mof_path = mof_path
    return inp


def commit_of(inp, fn, sha):
    for c in inp.commits[fn]:
        if c[0] == sha:
            return c
    return None


def retrieval_utc(log_rows, host, target):
    """The logged time of the successful request for (host, target): from the fetch log, never from the clock (R10, G21)."""
    if M("clock_stamp"):
        return now_utc().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    for r in log_rows:
        if r[1] == host and r[2] == target and r[3] == "200" and r[4]:
            return r[0]
    return ""


def cell4(v):
    return f(v, 4)


def pins_rows(R):
    m_vid, jul_vid = R["vid_m"], R["vid_july"]
    s = R["ser_m"]
    rows = []
    for period in ("202312", "202609"):
        for col, which in (("TermPremium-10Y", "tp"), ("ExpectedRate-10Y", "er")):
            rows.append([m_vid, "nakajima_monthly", col, period, cell4(getattr(s, which)[10][period]), "percent"])
    for col, which in (("TermPremium-10Y", "tp"), ("ExpectedRate-10Y", "er")):
        rows.append([jul_vid, "nakajima_monthly", col, "202606", cell4(getattr(R["ser_july"], which)[10]["202606"]), "percent"])
    bym = R["mof_bym10"]
    rows.append([R["vid_mof"], "mof", "10Y_monthly_mean", "202312", cell4(mean(v for _, v in bym["202312"])), "percent"])
    rows.append([R["vid_mof"], "mof", "10Y_monthly_mean", "202609", cell4(mean(v for _, v in bym["202609"])), "percent"])
    rows.append([R["vid_mof"], "mof", "10Y_last_value_of_month", "202609", f(bym["202609"][-1][1], 3), "percent"])
    j = R["jma_row"]
    for name, i in (("Yield_10Y", 0), ("RN_10Y", 1), ("TP_10Y", 2)):
        rows.append([R["vid_j"], "jma", name, "202609", cell4(j[10][i]), "percent"])
    return rows


def vintage_rows(inp, R, log_rows):
    rows = []
    for fn, src in (("yield_M.csv", "nakajima_monthly"), ("yield_D.csv", "nakajima_daily")):
        for c in inp.commits[fn]:
            sha = c[0]
            used = c == inp.newest[fn]
            rev = fn == "yield_M.csv" and sha in (JULY_SHA, APRIL_SHA)
            role = "used" if used else "revision" if rev else "listed"
            blob = sh = fp = lp = nr = rt = upd = ""
            if (fn, sha) in inp.raw:
                body, nak = inp.raw[(fn, sha)]
                blob, sh = git_blob_sha(body), sha256_of(body)
                fp = nak.periods[0][:4]
                lm = nak.periods[-1][:6]
                lp = lm if lm in MONTH_LIST else ""
                nr = str(len(nak.periods))
                rq = req_raw(fn, sha)
                rt = retrieval_utc(log_rows, rq["host"], rq["target"])
            if used:
                upd = R["stated_update"]
            rows.append([vintage_id(c), src, fn, sha, c[2], blob, sh, fp, lp, nr, upd, rt, role])
    jm = R["jma_last_actual"]
    rows.append([R["vid_j"], "jma", "curve-panel.csv", "", "", "", sha256_of(inp.jma_bytes), "2002", jm if jm in MONTH_LIST else "", str(inp.jma_info["n_rows"]),
                 R["jma_vintage_text"], retrieval_utc(log_rows, JMA_HOST, JMA_CSV_PATH), "used"])
    mm = R["mof_last_month"]
    rows.append([R["vid_mof"], "mof", "mof_jgbcme_all.csv", "", "", "", sha256_of(inp.mof_bytes), str(min(inp.mof).year), mm if mm in MONTH_LIST else "",
                 str(len(inp.mof)), "", "", "used"])
    return rows


def window_months_needed():
    ms = set()
    for a, b in WINDOWS.values():
        ms |= {a, b}
    return ms


def compute(inp, log_rows, out_dir, amend=None):
    """Everything the build writes, from the cache and the existing verdict file. Pure apart from reading the existing verdict. -> R (dict)"""
    R = {}
    mnew_commit = inp.newest["yield_M.csv"]
    dnew_commit = inp.newest["yield_D.csv"]
    body_m, nak_m = inp.raw[("yield_M.csv", mnew_commit[0])]
    body_d, nak_d = inp.raw[("yield_D.csv", dnew_commit[0])]
    R["vid_m"], R["vid_d"] = vintage_id(mnew_commit), vintage_id(dnew_commit)
    jul = commit_of(inp, "yield_M.csv", JULY_SHA) or (JULY_SHA, "2026-07-06", "2026-07-06T00:00:00Z")
    apr = commit_of(inp, "yield_M.csv", APRIL_SHA) or (APRIL_SHA, "2026-04-20", "2026-04-20T00:00:00Z")
    R["vid_july"], R["vid_april"] = vintage_id(jul), vintage_id(apr)
    if nak_m.periods[-1] < "202609":
        raise DataError("vintage %s ends at %s, before 202609: no classification is made (3.6)" % (R["vid_m"], nak_m.periods[-1]))
    if nak_d.periods[-1][:6] < "202609":
        raise DataError("daily vintage %s ends at %s, before 202609" % (R["vid_d"], nak_d.periods[-1][:6]))
    R["ser_m"], R["ser_d"] = nak_to_ser(nak_m, "M"), daily_to_ser(nak_d, "D")
    R["ser_july"] = nak_to_ser(inp.raw[("yield_M.csv", JULY_SHA)][1])
    R["ser_april"] = nak_to_ser(inp.raw[("yield_M.csv", APRIL_SHA)][1])
    R["ser_j"] = jma_to_ser(inp.jma)
    R["nak_m"], R["nak_d"] = nak_m, nak_d
    R["jma_last_actual"] = sorted(inp.jma)[-1]
    if "202609" not in inp.jma:
        raise DataError("JMA actual rows end before 202609")
    R["jma_row"] = inp.jma["202609"]
    jv = parse_jma_vintage(inp.jma_page)
    R["jma_vintage"] = jv
    R["vid_j"] = "jma_%s_%s" % (jv[0] if jv else "unknown", sha256_of(inp.jma_bytes)[:12])
    R["jma_vintage_text"] = ("model vintage %s, origin %s" % jv) if jv else ""
    R["mof_last_month"] = "%04d%02d" % (max(inp.mof).year, max(inp.mof).month)
    R["vid_mof"] = "mof_%s_%s" % (R["mof_last_month"], sha256_of(inp.mof_bytes)[:12])
    R["mof_bym10"] = mof_by_month(inp.mof, 10)
    ps = parse_page_status(inp.page)
    R["page_status"] = ps
    R["stated_update"] = ps[2] if ps else ""
    # decomposition: 3 variants x 4 tenors x 7 windows
    dec_m, st_m = decomposition("M", R["ser_m"], R["vid_m"])
    dec_d, st_d = decomposition("D", R["ser_d"], R["vid_d"])
    dec_j, st_j = decomposition("JMA", R["ser_j"], R["vid_j"])
    R["dec_rows"] = dec_m + dec_d + dec_j
    R["st"] = {"M": st_m, "D": st_d, "JMA": st_j}
    # vintage revisions (10Y, M, changes only; each row from one vintage)
    rev, rev_stats = [], {}
    for wid, (a, b) in REV_WINDOWS.items():
        for vid, ser, is_apr in ((R["vid_m"], R["ser_m"], False), (R["vid_july"], R["ser_july"], False), (R["vid_april"], R["ser_april"], True)):
            if wid == "REV_2606" and is_apr:
                continue
            d_tp, d_er = stat_vintage([ser], 10, a, b)
            st = classify(wid, d_tp, d_er)
            rev_stats[(wid, vid)] = st
            rev.append([wid, a, b, vid, f(st.d_yield, 4), f(st.d_tp, 4), f(st.d_er, 4), f(st.share, 4), st.cls])
    R["rev_rows"], R["rev_stats"] = rev, rev_stats
    # the headline pieces
    full10_m, full10_d, full10_j = st_m[("10Y", "FULL")], st_d[("10Y", "FULL")], st_j[("10Y", "FULL")]
    reg_stats = st_d if M("d_in_registered") else st_m
    R["headline"] = headline_reading(full10_m.cls, full10_d.cls)
    R["jma_label"], R["jma_arms"] = jma_arms(full10_m.d_tp, full10_j.d_tp, full10_m.share, full10_j.share)
    boj = st_m[("10Y", "BOJ_MATCH")]
    R["retrieved_m"] = retrieval_utc(log_rows, GH_RAW, req_raw("yield_M.csv", mnew_commit[0])["target"])
    fresh = {}
    for t in TENORS:
        reg = reg_stats[(t, "FULL")]
        d = st_d[(t, "FULL")]
        j = st_j[(t, "FULL")]
        is10 = t == "10Y"
        fresh[t] = {"vintage_id": R["vid_m"], "tenor": t, "d_yield_pp": f(reg.d_yield, 4), "tp_share": f(reg.share, 4), "distance_bp": fs(reg.distance, 1),
                    "classification": reg.cls, "tp_share_2y": f(st_m[("2Y", "FULL")].share, 4), "tp_share_5y": f(st_m[("5Y", "FULL")].share, 4),
                    "tp_share_10y": f(st_m[("10Y", "FULL")].share, 4), "tp_share_20y": f(st_m[("20Y", "FULL")].share, 4),
                    "d_variant_tp_share": f(d.share, 4), "d_variant_classification": d.cls, "headline_reading": R["headline"] if is10 else "",
                    "jma_tp_share": f(j.share, 4), "jma_label": R["jma_label"] if is10 else "", "jma_arms_fired": R["jma_arms"] if is10 else "",
                    "boj_match_tp_share": f(boj.share, 4) if is10 else ""}
    R["verdict_fresh"] = fresh
    vpath = os.path.join(out_dir, "verdict.csv")
    h, existing = read_csv_rows(vpath)
    if existing and h != VERDICT_COLS:
        raise DataError("the existing verdict.csv has a different header")
    R["verdict_rows"], R["verdict_notes"] = reconcile_verdict(existing, fresh, R["vid_m"], R["retrieved_m"], amend)
    R["amend_comments"] = []
    if os.path.exists(vpath):
        with open(vpath, encoding="utf-8") as fh:
            R["amend_comments"] = [ln.rstrip("\n") for ln in fh if ln.startswith("# amendment")]
    if amend and R["verdict_notes"]:
        R["amend_comments"] += ["# amendment: %s" % n.replace("\n", " ") for n in R["verdict_notes"]]
    # decomposition rows of an existing vintage are frozen too
    dh, drows = read_csv_rows(os.path.join(out_dir, "decomposition.csv"))
    mine = (R["vid_m"], R["vid_d"], R["vid_j"])
    old_same = {tuple(r[:4]): r for r in drows if r and r[0] in mine}
    new_by = {tuple(r[:4]): r for r in R["dec_rows"]}
    changed = [k for k, r in new_by.items() if k in old_same and old_same[k] != r]
    if changed and not amend and not M("silent_overwrite"):
        raise DataError("%d decomposition rows for an existing vintage changed (e.g. %s); a rebuild may not change them without --amend" % (len(changed), changed[0]))
    R["dec_all"] = [r for r in drows if r and r[0] not in mine] + R["dec_rows"]
    # the fitted-yield check
    mof = inp.mof
    wmonths = months_between("202312", "202609")
    fit_rows, fit_summ = [], {}
    d_lo, d_hi = dt.date(2023, 12, 1), dt.date(2026, 9, 30)
    for k in FIT_K:
        bym = mof_by_month(mof, k)
        for scope, months in (("window", wmonths), ("full_history", nak_m.periods)):
            for basis in ("monthly_mean", "month_end"):
                gaps = fitted_monthly(R["ser_m"], bym, k, months, "mean" if basis == "monthly_mean" else "month_end")
                n, mx, md, nov = gap_summary(gaps)
                hard = scope == "window" and basis == "monthly_mean"
                status = ("PASS" if nov == 0 and n > 0 else "FAIL") if hard else "INFO"
                fit_summ[("M", k, scope, basis)] = (n, mx, md, nov, status, gaps)
                fit_rows.append([R["vid_m"], "yield_M.csv", "%dY" % k, scope, basis, str(n), f(mx, 5), f(md, 5), str(nov), status])
    for k in FIT_K:
        gaps, only_d, only_m = fitted_daily(nak_d, mof, k, d_lo, d_hi)
        n, mx, md, nov = gap_summary(gaps)
        status = "PASS" if nov == 0 and n > 0 else "FAIL"
        fit_summ[("D", k)] = (n, mx, md, nov, status, gaps, only_d, only_m)
        fit_rows.append([R["vid_d"], "yield_D.csv", "%dY" % k, "window", "daily", str(n), f(mx, 5), f(md, 5), str(nov), status])
    R["fit_rows"], R["fit_summ"] = fit_rows, fit_summ
    R["vint_rows"] = vintage_rows(inp, R, log_rows)
    R["pin_rows"] = pins_rows(R)
    return R


# ------------------------------------------------------------------------------------------------------------------------
# the pinned checks (section 7)
# ------------------------------------------------------------------------------------------------------------------------
def chk(cid, desc, expected, observed, status):
    return [cid, desc, expected, observed, status]


def yn(b):
    return "yes" if b else "no"


def ok_mm(b):
    return "match" if b else "mismatch"


def check_sort_key(row):
    m = re.fullmatch(r"C(\d+)([a-z]?)", row[0])
    return (int(m.group(1)), m.group(2)) if m else (99, row[0])


def make_checks(inp, R, log_rows, stop_exists):
    """C01 to C12 and C15 (C13 and C14 are added by the caller). Level checks commit `match` or `mismatch` and never the value (section 6, item 3)."""
    out = []
    expected_vintage = R["vid_m"] == EXPECTED_VINTAGE
    nak_m, nak_d, s_m, s_d, s_j = R["nak_m"], R["nak_d"], R["ser_m"], R["ser_d"], R["ser_j"]
    # C01
    hrefs = page_hrefs(inp.page)
    links_ok = all(any(l in h for h in hrefs) for l in PAGE_LINKS)
    ps = R["page_status"]
    last_ok = bool(ps) and page_month(ps[1]) == nak_m.periods[-1][:6]
    out.append(chk("C01", "The Sites page links to the two GitHub files on main; its stated last month equals the file's; the stated update is recorded in vintages.csv",
                   "both links present; page last month = file last month", "links present: %s; page last month equals the file's: %s; stated update recorded: %s" % (
                       yn(links_ok), yn(last_ok), yn(bool(R["stated_update"]))), "PASS" if links_ok and last_ok and R["stated_update"] else "FAIL"))
    # C02
    blob_ok = {}
    for fn in FILES_N:
        body, _ = inp.raw[(fn, inp.newest[fn][0])]
        blob_ok[fn] = True if M("blob_skip") else git_blob_sha(body) == inp.contents[fn]
    out.append(chk("C02", "git hash-object of each raw body, as bytes, equals the contents API blob sha at that commit",
                   "equal for both files", "monthly file: %s; daily file: %s" % (ok_mm(blob_ok["yield_M.csv"]), ok_mm(blob_ok["yield_D.csv"])),
                   "PASS" if all(blob_ok.values()) else "FAIL"))
    # C03
    probs = []
    for (fn, sha), (body, nak) in sorted(inp.raw.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        exp_rows = 381 if (fn == "yield_M.csv" and sha == inp.newest[fn][0] and R["vid_m"] == EXPECTED_VINTAGE) else None
        exp_last = "202609" if exp_rows else None
        for p in shape_problems(nak, exp_rows, exp_last):
            probs.append("%s %s: %s" % (fn, sha[:7], p))
    out.append(chk("C03", "Shape: the quoted header matched by name; every cell parses as a float (scientific notation included); months consecutive from the first; dates "
                          "strictly increasing; no blank cell; 381 monthly rows on the expected vintage",
                   "no problem in 4 files", "; ".join(probs) if probs else "no problem in %d files" % len(inp.raw), "FAIL" if probs else "PASS"))
    # C04: level checks, committed as match or mismatch only
    nm = nak_m.rows
    pins_ok = (f(s_m.tp[10]["202312"], 4) == "-0.0583" and f(s_m.er[10]["202312"], 4) == "0.7444" and f(s_m.tp[10]["202609"], 4) == "1.1768"
               and f(s_m.er[10]["202609"], 4) == "1.8154")
    shadow_ok = "201609" in nm and f(nm["201609"]["ShadowRate"], 4) == "-3.2823"
    drow = nak_d.rows.get("20260930")
    d_ok = bool(drow) and f(drow["TermPremium-10Y"], 4) == "1.0082" and f(drow["ExpectedRate-10Y"], 4) == "2.0488"
    sep = [p for p in nak_d.periods if p[:6] == "202609"]
    dm_ok = len(sep) == 19 and f(mean(nak_d.rows[p]["TermPremium-10Y"] for p in sep), 4) == "1.0090"
    for cid, desc, ok in (("C04a", "Level pins on the expected vintage: four October pins (the two 10-year series at the two window ends)", pins_ok),
                          ("C04b", "The shadow rate is negative in the negative-rate era (one month)", shadow_ok),
                          ("C04c", "Daily file, one late-September date: the two 10-year series", d_ok),
                          ("C04d", "Daily file: mean of the 19 September rows of the 10-year term premium", dm_ok)):
        out.append(chk(cid, desc, "match", ok_mm(ok) if expected_vintage else "new vintage; not tested", ("PASS" if ok else "FAIL") if expected_vintage else "WARN"))
    # C05
    fs_ = R["fit_summ"]
    mx_m = max(fs_[("M", k, "window", "monthly_mean")][1] for k in FIT_K)
    n_m = sum(fs_[("M", k, "window", "monthly_mean")][0] for k in FIT_K)
    nov_m = sum(fs_[("M", k, "window", "monthly_mean")][3] for k in FIT_K)
    mx_d = max(fs_[("D", k)][1] for k in FIT_K)
    n_d = sum(fs_[("D", k)][0] for k in FIT_K)
    nov_d = sum(fs_[("D", k)][3] for k in FIT_K)
    only_d = sum(fs_[("D", k)][6] for k in FIT_K)
    only_m = sum(fs_[("D", k)][7] for k in FIT_K)
    mof_last_ok = max(inp.mof) >= dt.date(2026, 9, 30)
    bym10 = R["mof_bym10"]
    me_gap = None
    try:
        me_gap = s_m.tp[10]["202609"] + s_m.er[10]["202609"] - bym10["202609"][-1][1]
    except KeyError:
        pass
    mean_gap10 = {m: s_m.tp[10][m] + s_m.er[10][m] - mean(v for _, v in bym10[m]) for m in ("202312", "202609") if m in bym10}
    c05_ok = nov_m == 0 and n_m > 0 and nov_d == 0 and n_d > 0 and mof_last_ok
    out.append(chk("C05", "Fitted-yield identity: the file's term premium plus expected rate equals the MoF monthly-average constant-maturity yield, six tenors, "
                          "window; the daily file against the MoF value on each common date; tolerance 0.00015 (two 4-decimal roundings plus float error); the MoF file "
                          "runs to the window end",
                   "no gap above 0.00015", "monthly file: max abs gap %s over %d comparisons, %d over; daily file: max abs gap %s over %d dates, %d over (dates only in "
                                           "the daily file %d, only in the MoF file %d); MoF file reaches the window end: %s" % (
                       f(mx_m, 5), n_m, nov_m, f(mx_d, 5), n_d, nov_d, only_d, only_m, yn(mof_last_ok)), "PASS" if c05_ok else "FAIL"))
    out.append(chk("C05b", "10-year gap at the two window ends against the MoF monthly mean, and at the later end against the month's last MoF value (INFO)",
                   "0.0000 on the mean basis; clearly larger on the month-end basis",
                   "mean basis gaps: %s; month-end basis gap: %s" % (", ".join("%s" % f(g, 4) for _, g in sorted(mean_gap10.items())), f(me_gap, 4)), "INFO"))
    # C06
    wmonths = months_between("202312", "202609")
    parts = []
    for t in TENORS:
        k = TK[t]
        diffs = [abs(s_m.tp[k][m] - s_d.tp[k][m]) for m in wmonths if m in s_m.tp[k] and m in s_d.tp[k]]
        parts.append("%s %s" % (t, f(median(diffs), 4)))
    out.append(chk("C06", "Daily file against monthly file: the median absolute difference of the term premium, monthly file against the monthly mean of the daily rows, window (INFO)",
                   "informational", "; ".join(parts), "INFO"))
    # C07
    n_c = len(inp.commits["yield_M.csv"])
    c07_ok = R["vid_m"] == EXPECTED_VINTAGE and n_c == EXPECTED_COMMITS
    out.append(chk("C07", "Vintage: the newest monthly-file commit is the expected one and 9 commits are listed", "%s, %d commits" % (EXPECTED_VINTAGE, EXPECTED_COMMITS),
                   "%s, %d commits (daily file newest: %s)" % (R["vid_m"], n_c, R["vid_d"]), "PASS" if c07_ok else "WARN"))
    # C08
    m_vint = [nak for (fn, sha), (body, nak) in inp.raw.items() if fn == "yield_M.csv"]
    same202312 = all(nak.rows.get("202312") == nak_m.rows.get("202312") for nak in m_vint)
    tper = [c for c in NAK_COLS if c != "ShadowRate"]
    same_tper = all(all(nak.rows["202312"][c] == nak_m.rows["202312"][c] for c in tper) for nak in m_vint)
    n_other = sum(1 for nak in m_vint if nak.rows["202312"] != nak_m.rows["202312"])
    jul = R["ser_july"]
    jul_ok = f(jul.tp[10]["202606"], 4) == "1.0720" and f(jul.er[10]["202606"], 4) == "1.5821"
    out.append(chk("C08a", "Revisions: the first window month is identical across the three monthly-file vintages fetched (INFO)", "identical", "identical" if same202312 else (
        "the term-premium and expected-rate columns are identical in all three; another column differs in %d older vintage(s)" % n_other if same_tper
        else "differs in the term-premium or expected-rate columns of %d older vintage(s)" % n_other), "INFO"))
    out.append(chk("C08b", "Revisions: the July vintage's two pins at the revision end (INFO)", "match", ok_mm(jul_ok), "INFO"))
    # C09
    jma = inp.jma
    jlog = [r for r in log_rows if r[1] == JMA_HOST and r[3] == "200" and r[4]]
    shape_bad = []
    if len(jlog) < 2:
        shape_bad.append("status 200 logged for %d of 2 JMA requests" % len(jlog))
    if R["jma_last_actual"] != "202609":
        shape_bad.append("actual rows end at a month other than the window end")
    for m, row in jma.items():
        for k in (2, 5, 10, 20):
            tri = row.get(k)
            if tri and abs(tri[1] + tri[2] - tri[0]) > 0.0002:
                shape_bad.append("RN + TP differs from Yield by more than 0.0002 at %dY in one actual row" % k)
                break
        if len(shape_bad) > 3:
            break
    out.append(chk("C09a", "JMA shape: reachable without a login; the Yield, RN and TP columns for 2, 5, 10 and 20 years; actual rows run to the window end; RN + TP = Yield within 0.0002 on every actual row",
                   "no problem", "; ".join(shape_bad) if shape_bad else "no problem", "FAIL" if shape_bad else "PASS"))
    jr = R["jma_row"][10]
    jv_ok = f(jr[0], 4) == "3.0656" and f(jr[1], 4) == "2.3281" and f(jr[2], 4) == "0.7375"
    out.append(chk("C09b", "JMA window-end values at 10 years (INFO); the page's model-vintage text is recorded in vintages.csv", "match",
                   "%s; vintage text recorded: %s" % (ok_mm(jv_ok), yn(bool(R["jma_vintage"]))), "INFO"))
    # C10
    need = sorted(window_months_needed())
    miss = []
    for label, ser in (("M", s_m), ("D", s_d), ("JMA", s_j)):
        for k in (2, 5, 10, 20):
            for m in need:
                if m not in ser.tp[k] or m not in ser.er[k]:
                    miss.append("%s %dY %s" % (label, k, m))
    for label, ser in (("M July", R["ser_july"]), ("M April", R["ser_april"])):
        for m in ("202312", "202603"):
            if m not in ser.tp[10]:
                miss.append("%s 10Y %s" % (label, m))
    out.append(chk("C10", "Every window month is present in every variant, at the four tenors (and the revision months in the older vintages)", "none missing",
                   "none missing" if not miss else "; ".join(miss[:6]), "FAIL" if miss else "PASS"))
    # C11
    st = R["st"]["M"]
    f10 = st[("10Y", "FULL")]
    g4 = [("d_tp", f(f10.d_tp, 4), "1.2351"), ("d_er", f(f10.d_er, 4), "1.0710"), ("d_yield", f(f10.d_yield, 4), "2.3061"), ("share", f(f10.share, 4), "0.5356"),
          ("distance_bp", fs(f10.distance, 1), "+8.2"), ("classification", f10.cls, "CLOSE_TO_EVEN")]
    g3 = [("10Y Y2024 share", f(st[("10Y", "Y2024")].share, 3), "0.055"), ("10Y Y2025_26 share", f(st[("10Y", "Y2025_26")].share, 3), "0.635"),
          ("10Y B share", f(st[("10Y", "B")].share, 3), "0.581"), ("10Y BOJ_MATCH share", f(st[("10Y", "BOJ_MATCH")].share, 3), "0.643"),
          ("2Y FULL share", f(st[("2Y", "FULL")].share, 3), "0.360"), ("5Y FULL share", f(st[("5Y", "FULL")].share, 3), "0.442"),
          ("20Y FULL share", f(st[("20Y", "FULL")].share, 3), "0.615")]
    for cid, desc, items in (("C11a", "Supervisor pins, monthly file, 10-year, full window, at 4 decimals", g4),
                             ("C11b", "Supervisor pins (round 3), monthly file, shares at 3 decimals", g3)):
        bad = [n for n, got, want in items if got != want]
        obs = "; ".join("%s %s" % (n, got) for n, got, want in items)
        out.append(chk(cid, desc, "; ".join("%s %s" % (n, want) for n, got, want in items), obs if bad else "all match (" + obs + ")",
                       ("FAIL" if bad else "PASS") if expected_vintage else "WARN"))
    dsh, jsh = R["st"]["D"][("10Y", "FULL")].share, R["st"]["JMA"][("10Y", "FULL")].share
    near = [("daily file 10Y full-window share", dsh, 0.44), ("JMA 10Y full-window share", jsh, 0.29)]
    bad = [n for n, v, w in near if v is None or abs(v - w) > 0.005]
    out.append(chk("C11c", "Reviewer values, reproduced within 0.005 or explained (round 2)", "daily file 0.44; JMA 0.29",
                   "; ".join("%s %s" % (n, f(v, 4)) for n, v, w in near), "WARN" if bad else "PASS"))
    # C12
    idb = []
    for v in ("M", "D", "JMA"):
        for p in identity_problems(R["st"][v]):
            idb.append("%s %s" % (v, p))
    comm_bad = []
    for r in R["dec_rows"]:
        if r[6] and r[7] and r[8] and abs(float(r[6]) - (float(r[7]) + float(r[8]))) > TOL_DY_COMMITTED:
            comm_bad.append(r[1] + r[2] + r[3])
    rm = recomputed_mean_problems(nak_d, wmonths)
    out.append(chk("C12", "Identities: d_yield = d_tp + d_er (1e-9 unrounded, 2e-4 committed); FULL = A + BRIDGE + B and FULL = Y2024 + Y2025_26 for each variant and tenor (1e-9); "
                          "the daily file's monthly means recomputed a second way are equal within 1e-6",
                   "no problem", "; ".join((idb + comm_bad + rm)[:5]) if (idb or comm_bad or rm) else "no problem in 84 rows",
                   "FAIL" if (idb or comm_bad or rm) else "PASS"))
    # C15
    out.append(chk("C15", "Fetch: at most 15 requests, all logged, and STOP absent", "at most 15 logged requests; no STOP", "%d logged requests; STOP %s" % (
        len(log_rows), "present" if stop_exists else "absent"), "PASS" if len(log_rows) <= MAX_REQUESTS and not stop_exists and len(log_rows) > 0 else "FAIL"))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# README and SOURCES (generated; scanned by G13 and G20)
# ------------------------------------------------------------------------------------------------------------------------
PAPER_READING = {
    "iu2013": ("checked. The short rate is a constant, written rho and carrying no time index, plus two zero-mean Gaussian factors, and the paper calls rho the "
               "long-run level of the short rate (equation 1, printed page 7, which is page 8 of the PDF; the shadow-rate model repeats it on printed page 11). "
               "The long-run level is one estimated number for the whole sample"),
    "nak2025": ("the same constant is kept. The appendix (printed page 10, page 11 of the PDF) writes the shadow rate as rho plus a linear function of the factors, "
                "following Ichiue and Ueno (2013), with rho again a single parameter with no time index; only the lower bound on the short rate is set to vary by "
                "date. The paper defines the term premium simply as the yield minus the expected rate (printed page 11)"),
}
DECISIONS = []          # replaced below


def cls_words(c):
    return {"CLOSE_TO_EVEN": "close to even (a share from 0.40 to 0.60 names no larger part)",
            "TERM_PREMIUM_LARGER": "the term premium is the larger part",
            "EXPECTED_RATES_LARGER": "expected rates are the larger part",
            "NOT_CLASSIFIED": "not classified (the yield change is under 0.25 percentage points)",
            "NOT_APPLICABLE": "not classified (a bridge window)"}.get(c, c)


CLS_SHORT = {"CLOSE_TO_EVEN": "close to even", "TERM_PREMIUM_LARGER": "term premium larger", "EXPECTED_RATES_LARGER": "expected rates larger",
             "NOT_CLASSIFIED": "not classified", "NOT_APPLICABLE": "not applicable"}


def headline_words(h):
    return {"close_to_even_and_model_dependent": "close to even in both of the author's files, and dependent on the model",
            "differs_between_monthly_and_daily_files": "the author's monthly and daily files do not fall in the same class, so the answer depends on the model",
            "TERM_PREMIUM_LARGER": "term premium the larger part in both of the author's files",
            "EXPECTED_RATES_LARGER": "expected rates the larger part in both of the author's files"}.get(h, h)


def shr(st):
    return f(st.share, 4) if st.share is not None else "n/a (%s)" % ("bridge window" if st.cls == "NOT_APPLICABLE" else "not classified")


def dist(st):
    return fs(st.distance, 1) if st.distance is not None else "n/a"


def md_table(head, rows, align=None):
    align = align or ["---"] * len(head)
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(align) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


WIN_NAMES = {"FULL": "full window, December 2023 to September 2026", "A": "window A, December 2023 to July 2024",
             "BRIDGE": "bridge, July 2024 to August 2024 (never classified)", "B": "window B, August 2024 to September 2026",
             "BOJ_MATCH": "BoJ-matched window, August 2024 to June 2026", "Y2024": "first path window, December 2023 to December 2024",
             "Y2025_26": "second path window, December 2024 to September 2026"}


def render_readme(R, log_rows):
    st, sd, sj = R["st"]["M"], R["st"]["D"], R["st"]["JMA"]
    vrows = R["verdict_rows"]
    live = [r for r in vrows if r[V_IX["status"]] in ("registered", "amended") and r[V_IX["tenor"]] == "10Y"]
    r10 = live[-1] if live else None
    f10 = st[("10Y", "FULL")]
    rev = R["rev_stats"]
    P = []
    P.append("# Japan's 10-year yield: term premium and expected rates")
    P.append("This folder splits the change in Japan's 10-year government bond yield from December 2023 to September 2026 into a term premium and an expected path of short-term rates, using one researcher's published model. " + REQUIRED_SENTENCE)
    P.append("## The result")
    P.append("**Registered reading** (monthly file, 10-year, full window December 2023 to September 2026). The monthly-average 10-year constant-maturity yield changed by %s percentage points over the window. "
             "The model's term premium is %s of that change (denominator: the %s-point change in the monthly-average 10-year yield), which is %s basis points of yield change from an even split "
             "(distance = (share - 0.5) x change in yield x 100). Classification under the rule fixed before the data run: **%s**. "
             "\"Registered\" means that the rule, the full window and this row were written down before any data were run." % (
                 f(f10.d_yield, 4), shr(f10), f(f10.d_yield, 4), dist(f10), cls_words(f10.cls)))
    if r10 and r10[V_IX["vintage_id"]] != R["vid_m"]:
        P.append("The registered row was made on an earlier vintage (%s). The newest vintage in the cache is %s, shown above and below; the registered row in `verdict.csv` is unchanged." % (
            r10[V_IX["vintage_id"]], R["vid_m"]))
    P.append("**The four tenors, monthly file, full window.** Each share is the term premium's part of that tenor's own change in the monthly-average constant-maturity yield.")
    rows = []
    for t in TENORS:
        s = st[(t, "FULL")]
        rows.append([t, f(s.d_yield, 4), f(s.d_tp, 4), f(s.d_er, 4), shr(s), dist(s), CLS_SHORT[s.cls]])
    P.append(md_table(["tenor", "change in yield (pp)", "change in term premium (pp)", "change in expected rates (pp)", "term-premium share of the change", "distance from an even split (bp)", "classification"],
                      rows, ["---", "---:", "---:", "---:", "---:", "---:", "---"]))
    shares = [(st[(t, "FULL")].share, t) for t in TENORS if st[(t, "FULL")].share is not None]
    straddle = bool(shares) and min(shares)[0] < 0.5 < max(shares)[0]
    if shares and min(shares)[0] < 0.5 < max(shares)[0]:
        P.append("The four tenors fall on both sides of one half: the share runs from %s at %s to %s at %s." % (f(min(shares)[0], 4), min(shares)[1], f(max(shares)[0], 4), max(shares)[1]))
    elif shares:
        P.append("The four tenors all fall on one side of one half: the share runs from %s at %s to %s at %s." % (f(min(shares)[0], 4), min(shares)[1], f(max(shares)[0], 4), max(shares)[1]))
    P.append("**The monthly file and the daily file side by side, full window** (the daily file is a separate estimate by the same author, averaged by month here; it never enters the registered classification). Each share is the term premium's part of that file's own change in the yield at that tenor.")
    rows = []
    for t in TENORS:
        rows.append([t, shr(st[(t, "FULL")]), CLS_SHORT[st[(t, "FULL")].cls], shr(sd[(t, "FULL")]), CLS_SHORT[sd[(t, "FULL")].cls]])
    P.append(md_table(["tenor", "monthly-file share", "monthly-file class", "daily-file share", "daily-file class"], rows, ["---", "---:", "---", "---:", "---"]))
    P.append("**Headline reading at 10 years: %s.** The author's monthly file gives %s and his daily file %s (a separate estimate by the same author; why the two differ is not established); JMA's own model gives %s%s. "
             "This is one model's split, and a different model can move it." % (
                 headline_words(R["headline"]), shr(st[("10Y", "FULL")]), shr(sd[("10Y", "FULL")]), shr(sj[("10Y", "FULL")]),
                 "; and the other tenors fall on both sides of one half" if straddle else ""))
    P.append("**Sub-windows and the path.** Each cell is the term premium's share of that window's own change in the yield at that tenor (monthly file); the last column is the 10-year change in points. "
             "A bridge window is never classified. The path windows split the full window in two at December 2024.")
    rows = []
    for w in ("A", "BRIDGE", "B", "BOJ_MATCH", "Y2024", "Y2025_26"):
        rows.append([WIN_NAMES[w]] + [shr(st[(t, w)]) if st[(t, w)].share is not None else ("bridge" if w == "BRIDGE" else "not classified") for t in TENORS] + [f(st[("10Y", w)].d_yield, 4)])
    P.append(md_table(["window"] + list(TENORS) + ["10-year change (pp)"], rows, ["---", "---:", "---:", "---:", "---:", "---:"]))
    y1, y2 = st[("10Y", "Y2024")], st[("10Y", "Y2025_26")]
    if y1.share is not None and y2.share is not None:
        P.append("The share moves a lot between windows: at 10 years it is %s in the first path window and %s in the second, so the full-window figure combines two stretches that look very different." % (f(y1.share, 4), f(y2.share, 4)))
    P.append("Window B (August 2024 to September 2026) straddles the two path windows (December 2023 to December 2024, and December 2024 to September 2026): it starts inside the first and runs to the end of the second. The full window equals window A plus the bridge plus window B exactly, and equals the two path windows added, in changes of the term premium, of expected rates and of the yield (checked to 1e-9; `checks.csv` row C12).")
    P.append("## What was fixed in advance")
    P.append("The rule, the full window, the tenors and the 0.40 to 0.60 band were written down before this build ran on any data (the band was amended once, before the build, so that no larger part is named inside it). Two things were not independent of the data:")
    P.append(R27_LABEL)
    P.append("## Definitions")
    P.append("- **Term premium** (here): the part of the yield that Nakajima's model does not attribute to its expected path of short rates. Nakajima (2025), appendix, defines it simply as the yield minus the expected rate, and the data match: the two add to the Ministry of Finance monthly-average yield (see the fitted-yield section).\n"
             "- **Expected rates**: the model's expected average short rate over the bond's life, under the real-world (not the risk-neutral) measure, as published.\n"
             "- **Residual**: the change in the term premium is the change in the yield minus the change in expected rates, so every error in the model's expected path lands in it. It is not a measurement.\n"
             "- **Monthly average**: the mean of the month's daily values, not the month-end value.\n"
             "- **Constant-maturity yield**: the Ministry of Finance series (semiannual compounding, percent), read for the 10-year and the other tenors.\n"
             "- **Vintage**: one dated upload of the author's file (a GitHub commit). Every row names its vintage (the commit date and the first 12 characters of its code); no statistic mixes two.\n"
             "- **Tenor**: the bond's maturity; 2Y is a 2-year bond. A **basis point** (bp) is one hundredth of a percentage point (pp).\n"
             "- **Abbreviations**: JGB is a Japanese government bond, the Bank is the Bank of Japan (BoJ), MoF is Japan's Ministry of Finance, JMA is Japan Macro Advisors. Nakajima's published files estimate the Ichiue–Ueno shadow-rate model, so the two names refer to one model.")
    P.append("## The model caveat (a property of the cited model, not a finding)")
    P.append("The Ichiue–Ueno model holds the long-run short rate constant, so a rise in long-run expected rates can be recorded as term premium. Japan Macro Advisors makes this criticism of the standard model; it states that standard models \"significantly overestimate the premium\".")
    P.append("In plain terms: the model expects the short-term interest rate to drift back, over the long run, toward one fixed level. If the true long-run level has moved up, the model can record such a rise as term premium.")
    P.append("Reading of the papers (a manual step outside the script; one request per file): Ichiue and Ueno (2013), pages 8 to 9: %s. Nakajima (2025): %s." % (PAPER_READING["iu2013"], PAPER_READING["nak2025"]))
    P.append("## What it cannot say")
    P.append("It cannot say why yields rose, or that purchases, flows or positions moved any price. It does not test the project's breakeven split (C-126), which divides the nominal yield into inflation compensation and the real yield. This split cuts across it: expected inflation sits inside expected nominal rates, and an inflation risk premium sits inside the term premium. "
             "The term premium here is one model's residual; the author's own monthly and daily files already differ.")
    j10 = sj[("10Y", "FULL")]
    P.append("**Japan Macro Advisors (JMA), cross-check.** JMA's own model gives a 10-year full-window share of %s (denominator: JMA's %s-point change in its own 10-year yield), against %s in the monthly file. JMA's label: **%s**%s. "
             "The label is model_sensitive if any of three arms fires: ratio (JMA's change in term premium is under half or over twice the monthly file's), share (the two shares differ by more than 0.15) or side (the two shares sit on opposite sides of one half). "
             "JMA's yield is a spot (zero-coupon) yield, probably a month-end value rather than a monthly average, and it benchmarks its premia to their 2004 to 2012 averages, so it is not on the same basis. "
             "Its model is proprietary, and its updated estimates are for paid users; its files are %s. Raw JMA files stay in the local cache." % (
                 shr(j10), f(j10.d_yield, 4), shr(f10), R["jma_label"], " (arms fired: %s)" % R["jma_arms"] if R["jma_arms"] else " (no arm fired)", JMA_ATTRIB))
    boj = st[("10Y", "BOJ_MATCH")]
    P.append("**The Bank's Review, side by side.** Bank of Japan Review 2026-E-10, from summer 2024: both factors \"contributed to roughly the same degree\". "
             "The monthly file's share over the matched window (August 2024 to June 2026, the Review's end point) is %s (denominator: the %s-point change in the 10-year yield over that window). "
             "The two are set next to each other and no verdict is given. %s "
             "The Bank used a different model (Imakubo and Nakajima 2015, anchored on Consensus Forecasts) and a window that had already been read before this build. The data are as of end-June 2026 in its chart." % (
                 shr(boj), f(boj.d_yield, 4), CONVENTION_SENTENCE))
    P.append("## Why the yield change here differs from the project's earlier JGB note's +243bp")
    P.append("The project's earlier JGB note reports +243bp for the 10-year JGB from 29 December 2023 to 24 September 2026 on daily values. This folder uses monthly averages (the December 2023 average to the September 2026 average, which holds 19 days), and the change is %s points. Different end points, a different averaging; neither is wrong." % f(f10.d_yield, 4))
    P.append("## The fitted-yield check")
    fs_ = R["fit_summ"]
    mx_m = max(fs_[("M", k, "window", "monthly_mean")][1] for k in FIT_K)
    n_m = sum(fs_[("M", k, "window", "monthly_mean")][0] for k in FIT_K)
    mx_d = max(fs_[("D", k)][1] for k in FIT_K)
    n_d = sum(fs_[("D", k)][0] for k in FIT_K)
    me = fs_[("M", 10, "window", "month_end")]
    P.append("Over the window, the monthly file's term premium plus expected rate equals the Ministry of Finance monthly-average constant-maturity yield to within %s percentage points at six tenors (%d comparisons; tolerance 0.00015); the daily file against the MoF value on each common date, within %s (%d comparisons). "
             "Against the month's last value instead, the 10-year gap is larger (maximum %s over the window; `fitted_check.csv`). This shows the basis (percent, monthly average) and that the term premium is, in effect, the observed yield minus the model's expected path. It cannot test the model's fit: the sum matches whatever the model's expected path is." % (
                 f(mx_m, 5), n_m, f(mx_d, 5), n_d, f(me[1], 5)))
    P.append("## Vintage and revisions")
    marg_hi = BAND[1] * f10.d_yield - f10.d_tp
    marg_lo = f10.d_tp - BAND[0] * f10.d_yield
    P.append("The monthly file used is the vintage `%s`; the daily file `%s`; JMA `%s`. The registered row is the first successful build and is never rewritten; a later vintage adds rows and a changed classification would be stated with both. "
             "" % (R["vid_m"], R["vid_d"], R["vid_j"]))
    by_w = {}
    for (wid, vid), rs in rev.items():
        if rs.share is not None:
            by_w.setdefault(wid, []).append(rs.share)
    span = max([max(v) - min(v) for v in by_w.values()] or [0.0])
    gap_hi, gap_lo = (BAND[1] - f10.share, f10.share - BAND[0]) if f10.share is not None else (None, None)
    inband = lambda x: x is not None and BAND[0] <= round(x, 9) <= BAND[1]
    where = lambda x: "inside the band" if inband(x) else ("above it" if x is not None and x > BAND[1] else "below it")
    P.append("**How far a revision moves the share.** On the two revision windows below, which end earlier than the full window and so move more for the same revision, the 10-year share moved by at most %s between vintages. "
             "The registered share (%s) lies %s below the band's upper edge (0.60) and %s above its lower edge (0.40); as term premium that is %s and %s percentage points. %s "
             "A change of model moves it further: the daily file reads %s (%s) and JMA %s (%s)." % (
                 f(span, 4), shr(f10), f(gap_hi, 4), f(gap_lo, 4), f(marg_hi, 3), f(marg_lo, 3),
                 "A revision of the size seen would not by itself carry it out of the band." if gap_hi is not None and span < min(gap_hi, gap_lo) else
                 "A revision of the size seen could carry it out of the band.",
                 shr(sd[("10Y", "FULL")]), where(sd[("10Y", "FULL")].share), shr(sj[("10Y", "FULL")]), where(sj[("10Y", "FULL")].share)))
    rows = []
    for (wid, vid), s in sorted(rev.items()):
        rows.append([{"REV_2606": "December 2023 to June 2026", "REV_2603": "December 2023 to March 2026"}[wid], vid, f(s.d_yield, 4), shr(s), CLS_SHORT[s.cls]])
    P.append(md_table(["revision window (10-year)", "vintage", "change in yield (pp)", "term-premium share of that change", "class"], rows, ["---", "---", "---:", "---:", "---"]))
    P.append("## Provenance")
    P.append("- Model: %s; %s. Data: Jouchi Nakajima's published files (the page says \"Cite the below articles when using this dataset\"), estimated and released within his research activity, not the official view of the Bank of Japan, used at the user's own risk.\n"
             "- Nakajima's repository states no licence. This repository's own CC BY 4.0 licence does not extend to his files, which are therefore never committed here, in any form; only changes over listed windows, shares, and at most four level points per vintage (`pins.csv`) are.\n"
             "- JMA: %s. Ministry of Finance Japan JGB yields: Public Data License 1.0.\n"
             "- Every URL, commit and licence text is in `SOURCES.md`.\n"
             "- Build decisions, including two text fixes made after the first build, are listed in [SOURCES.md](SOURCES.md)." % (CITE_IU, CITE_NAK, JMA_ATTRIB))
    return "\n\n".join(P) + "\n"


def render_sources(R, inp, log_rows):
    L = []
    L.append("# Sources and terms for data/japan_term_premium/")
    L.append("Each source below is public and free. Request times are in `fetch_log.csv`. Raw downloads stay in a cache outside the repository. " + REQUIRED_SENTENCE)
    L.append("- **Nakajima, monthly and daily files.** Page: https://sites.google.com/site/jnakajimaweb/yield (links to https://github.com/jouchinakajima/program/blob/main/yield_M.csv and .../yield_D.csv). "
             "Fetched only as commit-pinned raw files, https://raw.githubusercontent.com/jouchinakajima/program/<commit>/yield_M.csv and yield_D.csv; the commit lists and blob identities come from https://api.github.com/repos/jouchinakajima/program/. "
             "Licence: none stated for the repository (the API's licence field is null); the page asks users to cite the two articles below, says the data are estimated and released within his research, are not the official view of the Bank of Japan, and are used at the user's own risk. "
             "This repository's own CC BY 4.0 licence does not extend to his files, which are never committed. Cite as: %s; %s." % (CITE_IU, CITE_NAK))
    L.append("- **Vintages.** Monthly file, newest commit used: `%s` (commit %s); daily file `%s` (commit %s). Older monthly vintages read for the revision table: July `%s`, April `%s`." % (
        R["vid_m"], inp.newest["yield_M.csv"][0], R["vid_d"], inp.newest["yield_D.csv"][0], R["vid_july"], R["vid_april"]))
    L.append("- **Every commit listed** (newest first; sha, committer date): monthly file: %s. Daily file: %s." % (
        "; ".join("%s %s" % (c[0], c[2]) for c in inp.commits["yield_M.csv"]), "; ".join("%s %s" % (c[0], c[2]) for c in inp.commits["yield_D.csv"])))
    L.append("- **Japan Macro Advisors.** https://takujiokubo.github.io/jma-data/jgb-yield-curve-main/ and .../data/curve-panel.csv. Licence text on the live page: \"%s\". Details of the model are proprietary; updated estimates are for paid users. Vintage `%s`. Cite as: Japan Macro Advisors, JGB yield curve model." % (JMA_ATTRIB, R["vid_j"]))
    L.append("- **Ministry of Finance Japan.** https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/ (jgbcme_all.csv, read from the local cache of the hedged-yield build; never written here). Constant-maturity yield, semiannual compounding, percent, `-` for missing. Licence: Public Data License 1.0. Cite as: Ministry of Finance Japan, Interest Rate (JGB). Vintage `%s`." % R["vid_mof"])
    L.append("- **Bank of Japan Review 2026-E-10** (words only; not fetched by the script): https://www.boj.or.jp/en/research/wps_rev/rev_2026/rev26e10.htm and .../data/rev26e10.pdf. Quoted in fewer than 15 words, with credit.")
    L.append("## Column provenance")
    L.append("- `decomposition.csv`, `verdict.csv`, `vintage_revisions.csv`: changes and shares computed here from the files above; no level is committed.\n"
             "- `fitted_check.csv`: gaps between the file's term premium plus expected rate and the Ministry of Finance yield.\n"
             "- `pins.csv`: single published values, at most four per Nakajima vintage, three for JMA, four for the Ministry of Finance.\n"
             "- `vintages.csv`: commits, blob identities, sha256 of the downloaded bytes and the logged retrieval times.")
    L.append("## Build decisions")
    L.append("These are choices the builder made where the specification was silent or inconsistent, and the manual paper reading. They matter to a reviewer, not to a reader of the result.")
    L.append("\n".join("%d. %s" % (k + 1, d) for k, d in enumerate(DECISIONS)))
    return "\n\n".join(L) + "\n"


DECISIONS = [
    "A bridge window (July to August 2024) whose yield change is under 0.25 percentage points reads \"not classified\", because the specification's checks are applied in the order written; otherwise it reads \"not applicable\". Both leave the share and the distance blank, as the rule says for any unclassified window.",
    "The band test uses the share rounded to 9 decimals, and the 0.25 test uses the yield change rounded to 9 decimals, so floating-point error cannot move an edge. The published cells carry 4 decimals, so no real value is moved.",
    "The daily file is compared with the Ministry of Finance yield on each common date at a tolerance of 0.00015 percentage points, not 1e-6. Section 3.7 of the specification and its selftest table give 1e-6 (the supervisor's round-2 ruling on the daily-file tolerance). The round-4 ruling limits 1e-6 to values the build recomputes from cells it already holds, and the later ruling wins. The 1e-6 test is applied to the monthly means of the daily rows, recomputed a second way.",
    "Leak rules read strictly. The first-period column of `vintages.csv` gives the year only, and the last-period column gives a month only when it is one of the seven listed months (otherwise blank). No daily date is committed anywhere. The two level checks (the pinned-level check and the revisions check) say match or mismatch and nothing else. The date at which the Ministry of Finance file ends is described in words, not as a date.",
    "The headline reading, the JMA label, the list of JMA arms that fired and the Bank-matched share are filled on the 10-year verdict row only, because each is a statement about the 10-year result. The other tenors carry their own share, distance and classification, the daily-file share and the JMA share.",
    "For the JMA ratio arm, when the monthly file's change in term premium is not positive, the arm compares magnitudes and fires on a sign flip. For the positive case it is the literal rule: under half or over twice.",
    "The cache must resolve outside the repository (the specification's rule that raw files stay outside it). A cache inside the repository is refused even if git ignores it, which is stricter than the hedged-yield build.",
    "On a hard check failure the build writes every output into a `_FAILED/` folder inside the cache and leaves the committed folder alone, so a failed build cannot register a verdict.",
    "Paper reading (a manual step, from the supervisor's round-3 and round-4 rulings on the model caveat), 19 October 2026: one request for each PDF, with the neutral identification string, HTTP 200, no redirect, no retry, on hosts outside the script's allowlist. Ichiue and Ueno (2013): https://www.boj.or.jp/en/research/wps_rev/wps_2013/data/wp13e08.pdf (444,767 bytes). Nakajima (2025): https://www.ier.hit-u.ac.jp/Common/publication/DP/DPS-A760.pdf (545,272 bytes). The links come from the Sites page already in the cache (the Bank's link there is to the paper's landing page; the PDF address follows the Bank's pattern for its other papers). The specification's \"pages 8 to 9\" are PDF pages; the statement that rho is the long-run level of the short rate is on printed page 7 (PDF page 8). The equations were read from page images, because the text extraction drops the symbols.",
    "The JMA rows use the same rule as the monthly file, with the yield change taken as the sum of the term-premium change and the expected-rate change. The JMA shape check tests that expected rate plus term premium equals the yield within 0.0002 on every actual row.",
    "Two text fixes after the first build, made because the first wording was wrong, not because of a rule. (a) The README's revision paragraph first read: \"The one revision seen is small next to those margins; a change of model is not.\" That was written from the specification's single observed revision; the cache holds four, so the paragraph is now computed from the revision rows (the largest move in the 10-year share between vintages on the revision windows, set against the registered share's distance to each edge of the band). (b) The revisions check on the first window month first printed only \"differs\"; it now says that the term-premium and expected-rate columns of that month are identical in all three vintages and that another column differs in the older vintage (the specification had observed July against October only). No frozen value, rule or threshold changed.",
    "The leak guard's consecutive-level test looks at columns with 3 or more decimals (2 decimals would match by chance). Its level-in-checks test is structural (named levels, numbers in level checks, pinned values), because a plain value match collides with legitimate changes.",
]


def readme_problems(text):
    """G13, G20: the required sentences are there and the wording guards pass."""
    bad = []
    paras = text.split("\n\n")
    if not any(p.strip().endswith(REQUIRED_SENTENCE) for p in paras[:3]):
        bad.append("the opening does not end with the required sentence")
    if R27_LABEL not in text:
        bad.append("the pre-reading label (R2-7) is missing")
    if CONVENTION_SENTENCE not in text and not M("convention_not_required"):
        bad.append("the 'this spec's convention' sentence on the Bank's wording is missing")
    if "straddles" not in text:
        bad.append("the note that window B straddles the path windows is missing")
    h = causal_hits(text)
    if h:
        bad.append("causal wording %s" % h)
    hb = boj_label_hits(text)
    if hb:
        bad.append("a verdict word beside the Bank of Japan: %s" % hb)
    return bad


def retrieval_days(log_rows, hosts=None):
    return sorted({r[0][:10] for r in log_rows if r[3] == "200" and r[4] and (hosts is None or r[1] in hosts)})


def src_line(R, what, log_rows):
    days = retrieval_days(log_rows)
    return ("# source: Jouchi Nakajima's term-premium files (monthly vintage %s, daily vintage %s; github.com/jouchinakajima/program), Japan Macro Advisors' curve panel (%s), "
            "Ministry of Finance Japan constant-maturity yields (%s); retrieved %s; %s" % (R["vid_m"], R["vid_d"], R["vid_j"], R["vid_mof"],
                                                                                        ", ".join(days) if days else "(no logged retrieval)", what))


def render_all(inp, R, log_rows, c13, c14, stop_exists, fetch_text):
    checks = make_checks(inp, R, log_rows, stop_exists)
    checks.append(chk("C13", "Leak guard (section 6) on the committed folder: files, headers, pins, consecutive levels, months, level values in checks.csv",
                      "no problem", "no problem" if c13 == "PASS" else "a problem was found; see the build report", c13))
    checks.append(chk("C14", "Fixed output: a second build, with the clock moved forward, leaves every file unchanged", "identical",
                      "identical" if c14 == "PASS" else "differs", c14))
    checks.sort(key=check_sort_key)
    R["checks"] = checks
    texts = {}
    texts["decomposition.csv"] = render_csv("decomposition.csv", R["dec_all"], src_line(R, "changes, shares and distances computed here", log_rows))
    texts["verdict.csv"] = render_csv("verdict.csv", R["verdict_rows"], src_line(R, "the frozen verdict (status registered is never rewritten)", log_rows),
                                      extra_comments=R["amend_comments"])
    texts["vintage_revisions.csv"] = render_csv("vintage_revisions.csv", R["rev_rows"], src_line(R, "10-year changes on each vintage, one vintage per row", log_rows))
    texts["fitted_check.csv"] = render_csv("fitted_check.csv", R["fit_rows"], src_line(R, "gaps against the Ministry of Finance constant-maturity yield, in percentage points", log_rows))
    texts["vintages.csv"] = render_csv("vintages.csv", R["vint_rows"], src_line(R, "every commit listed; retrieval times from the fetch log", log_rows))
    texts["pins.csv"] = render_csv("pins.csv", R["pin_rows"], src_line(R, "single published values, at most four per Nakajima vintage", log_rows))
    texts["checks.csv"] = render_csv("checks.csv", checks, src_line(R, "pinned checks C01 to C15", log_rows))
    texts["fetch_log.csv"] = fetch_text
    readme = render_readme(R, log_rows)
    probs = readme_problems(readme)
    if probs:
        raise DataError("README: " + "; ".join(probs))
    guard_text("README.md", readme)
    sources = render_sources(R, inp, log_rows)
    guard_text("SOURCES.md", sources)
    texts["README.md"], texts["SOURCES.md"] = readme, sources
    return texts


def finish(inp, log_rows, out_dir, amend, stop_exists, fetch_text):
    """Compute and render twice (the second time with the clock moved forward); C14 is whether they are identical. -> (R, texts, leak problems, c14)"""
    def one(c13, c14):
        R = compute(inp, log_rows, out_dir, amend)
        return R, render_all(inp, R, log_rows, c13, c14, stop_exists, fetch_text)
    R1, t1 = one("PASS", "PASS")
    leak = leak_guard(dict(t1), raw=[R1["nak_m"], R1["nak_d"]])
    saved = _CLOCK[0]
    base = now_utc()
    _CLOCK[0] = lambda: base + dt.timedelta(days=1, seconds=7)
    try:
        R2, t2 = one("PASS", "PASS")
    finally:
        _CLOCK[0] = saved
    c14 = "PASS" if t1 == t2 else "FAIL"
    c13 = "FAIL" if leak else "PASS"
    R, final = one(c13, c14)
    return R, final, leak, c14


def read_fetch_text(out_dir, cache):
    for p in (os.path.join(out_dir, "fetch_log.csv"), os.path.join(cache, "fetch_log.csv")):
        if os.path.exists(p):
            with open(p, encoding="utf-8", newline="") as fh:
                return fh.read()
    raise DataError("no fetch_log.csv in the output folder or the cache: run fetch first")


def build(cache, out_dir, mof_path, amend=None, say=print):
    cache = check_cache(cache)
    fetch_text = read_fetch_text(out_dir, cache)
    _, log_rows = read_csv_text(fetch_text)
    inp = load_inputs(cache, mof_path)
    stop_exists = os.path.exists(STOP_PATH) or os.path.exists(os.path.join(cache, "STOP"))
    R, texts, leak, c14 = finish(inp, log_rows, out_dir, amend, stop_exists, fetch_text)
    fails = [c for c in R["checks"] if c[4] == "FAIL"]
    warns = [c for c in R["checks"] if c[4] == "WARN"]
    target = out_dir if not fails else os.path.join(cache, "_FAILED")
    for name in FILES:
        if name == "fetch_log.csv" and target == out_dir:
            continue
        write_text(os.path.join(target, name), texts[name])
    say("build: vintage %s (monthly), %s (daily), %s (JMA); %d checks, %d FAIL, %d WARN" % (R["vid_m"], R["vid_d"], R["vid_j"], len(R["checks"]), len(fails), len(warns)))
    for c in R["checks"]:
        say("  %-5s %-5s %s" % (c[0], c[4], c[1][:90]))
    for c in fails:
        say("FAIL %s: %s" % (c[0], c[3][:300]))
    for c in warns:
        say("WARN %s: %s" % (c[0], c[3][:300]))
    for p in leak:
        say("LEAK " + p)
    for n in R["verdict_notes"]:
        say("NOTE " + n)
    if fails:
        say("outputs written to %s, not to the committed folder" % tilde(target))
        return 1
    return 0


# ==================================================================================================================================
# SELFTEST: synthetic data only. Every guard applies its own mutants one at a time; a mutant that does not make its guard fail fails the selftest.
# ==================================================================================================================================
D_ = dt.date.fromisoformat
UTC = dt.timezone.utc
SPEC_PATH = [SPEC_DEFAULT]
MOF_KS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 40)


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


# ---- fixtures -----------------------------------------------------------------------------------------------------------------
def bdays(a, b):
    d, end, out = D_(a), D_(b), []
    while d <= end:
        if d.weekday() < 5:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def mkey(d):
    return "%04d%02d" % (d.year, d.month)


def mof_value(k, i):
    return round(0.30 + 0.0009 * i + 0.045 * MOF_KS.index(k) + 0.02 * math.sin(i / 9.0), 3)


def mof_text(days, dash_days=(), title=True, last_bump=None):
    """MoF layout: a title row, the header row, unpadded y/m/d dates, '-' for missing, a footer note. last_bump: {date: extra} added to every tenor."""
    lines = []
    if title:
        lines.append("Interest Rate (October 2026)" + "," * 14 + "(Unit : %)")
    lines.append("Date," + ",".join("%dY" % k for k in MOF_KS))
    for i, d in enumerate(days):
        cells = []
        for k in MOF_KS:
            if d in dash_days:
                cells.append("-")
            else:
                cells.append("%.3f" % (mof_value(k, i) + (last_bump or {}).get(d, 0.0)))
        lines.append("%d/%d/%d," % (d.year, d.month, d.day) + ",".join(cells))
    lines.append("," * 15)
    lines.append('" * If you cannot download the latest csv data, please clear the cache.",' + "," * 14)
    return "\r\n".join(lines) + "\r\n"


def nak_text(rows, daily=False, order="default"):
    """The real layout: a quoted header, unquoted data. rows: [(period, {col: float|str})]; a str cell is written as it is (scientific notation)."""
    key = "YYYYMMDD" if daily else "YYYYMM"
    cols = NAK_COLS if order == "default" else ["ShadowRate"] + NAK_COLS[7:] + NAK_COLS[1:7]
    out = ['"%s",' % key + ",".join('"%s"' % c for c in cols)]
    for p, vals in rows:
        out.append(p + "," + ",".join(vals[c] if isinstance(vals[c], str) else "%.4f" % vals[c] for c in cols))
    return "\r\n".join(out) + "\r\n"


def jma_text(actual, forecast, dup_forecast=None):
    cols = ["YM", "Type"] + ["%s_%dY" % (p, k) for k in (2, 5, 10, 20, 30, 40) for p in ("Yield", "RN", "TP")]
    lines = [",".join(cols)]

    def row(ym, ty, j):
        cells = [ym, ty]
        for kk, k in enumerate((2, 5, 10, 20, 30, 40)):
            y = round(1.0 + 0.02 * j + 0.1 * kk, 4)
            tp = round(0.30 * y, 4)
            cells += ["%.4f" % y, "%.4f" % round(y - tp, 4), "%.4f" % tp]
        return ",".join(cells)
    for j, ym in enumerate(actual):
        lines.append(row(ym, "actual", j))
    for j, ym in enumerate(forecast):
        lines.append(row(ym, "forecast", len(actual) + j + 50))
    if dup_forecast:
        lines.append(row(dup_forecast, "forecast", 999))
    return "\n".join(lines) + "\n"


def ym_range(a, b):
    out, y, m = [], int(a[:4]), int(a[5:7])
    while "%04d-%02d" % (y, m) <= b:
        out.append("%04d-%02d" % (y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


class World:
    pass


def sha1_hex(s):
    return hashlib.sha1(s.encode()).hexdigest()


def build_world(tmp):
    """A complete synthetic cache (and MoF file) in which TP + ER equals the MoF monthly mean. The monthly file splits 0.55 / 0.45 (close to even), the daily
    file 0.80 / 0.20, JMA 0.30 / 0.70, so the three variants differ and every arm and reading can be reached."""
    w = World()
    w.cache = os.path.join(tmp, "cache")
    os.makedirs(w.cache)
    days = bdays("2023-12-01", "2026-09-30")
    mofv = {k: [mof_value(k, i) for i in range(len(days))] for k in MOF_KS}
    by = {}
    for i, d in enumerate(days):
        by.setdefault(mkey(d), []).append(i)
    mon = {m: {k: math.fsum(mofv[k][i] for i in idx) / len(idx) for k in MOF_KS} for m, idx in by.items()}
    months = months_between("199501", "202609")
    rows = []
    for j, m in enumerate(months):
        vals = {"ShadowRate": round(-1.0 + 0.01 * (j % 50), 4)}
        for kk, k in enumerate(NAK_KS):
            if m in mon:
                y = mon[m][k]
                er = round(0.45 * y, 4)
                vals["ExpectedRate-%dY" % k], vals["TermPremium-%dY" % k] = er, round(y - er, 4)
            else:
                vals["TermPremium-%dY" % k] = round(0.02 * math.sin(j / 9.0) + 0.01 * kk, 4)
                vals["ExpectedRate-%dY" % k] = round(0.5 + 0.001 * j + 0.01 * kk, 4)
        rows.append((m, vals))
    rows[0][1]["ShadowRate"] = "-1e-04"
    w.m_text = nak_text(rows)

    def variant(last, tweak_period, delta):
        out = []
        for p, v in rows:
            if p > last:
                break
            v2 = dict(v)
            if p == tweak_period:
                v2["TermPremium-10Y"] = round(v2["TermPremium-10Y"] + delta, 4)
                v2["ExpectedRate-10Y"] = round(v2["ExpectedRate-10Y"] - delta, 4)
            out.append((p, v2))
        return nak_text(out)
    w.july_text, w.april_text = variant("202606", "202606", 0.0178), variant("202603", "202603", 0.0100)
    drows = []
    for i, d in enumerate(days):
        vals = {"ShadowRate": -0.5}
        for k in NAK_KS:
            tp = round(0.8 * mofv[k][i] + 0.003 * math.sin(i), 4)
            vals["TermPremium-%dY" % k], vals["ExpectedRate-%dY" % k] = tp, round(mofv[k][i] - tp, 4)
        drows.append(("%04d%02d%02d" % (d.year, d.month, d.day), vals))
    w.d_text = nak_text(drows, daily=True)
    w.mof_text = mof_text(days)
    w.jma_text = jma_text(ym_range("2002-07", "2026-09"), ym_range("2026-10", "2029-09"))
    w.page = ("<html><head><title>Nakajima</title></head><body><h2>Yield curve and term premium, J. Nakajima</h2><p>Cite the below articles when using this dataset. "
              "The data are estimated and released by J. Nakajima within his research activity and are not the official view of the Bank of Japan." + " filler" * 40 +
              "</p><div>From 1995/Jan.</div> <div>to 2026/Sep.</div><span> (updated in</span><span> 2026/Oct.)</span>"
              '<a href="https://github.com/jouchinakajima/program/blob/main/yield_M.csv">Monthly</a> <a href="https://github.com/jouchinakajima/program/blob/main/yield_D.csv">Daily</a>'
              "</body></html>")
    w.jma_page = "<html><body><h1>JGB yield curve</h1><p>Model vintage: October 2026, origin September 2026</p>" + "<p>yield curve model text</p>" * 12 + "</body></html>"
    shaM, shaD = sha1_hex("newM"), sha1_hex("newD")
    w.shaM, w.shaD = shaM, shaD
    dates = ["2026-10-06", "2026-07-06", "2026-04-20", "2025-12-31", "2025-12-04", "2025-09-24", "2025-06-05", "2025-04-04", "2025-02-06"]
    shas = [shaM, JULY_SHA, APRIL_SHA] + [sha1_hex("old%d" % i) for i in range(6)]

    def commits(sl, dl):
        return json.dumps([{"sha": s, "commit": {"committer": {"date": d + "T00:48:15Z"}}} for s, d in zip(sl, dl)])
    bodies = []

    def put(req, body):
        if isinstance(body, str):
            body = body.encode("utf-8")
        with open(os.path.join(w.cache, req["file"]), "wb") as fh:
            fh.write(body)
        bodies.append((req, body))
    put(req_commits("yield_M.csv"), commits(shas, dates))
    put(req_commits("yield_D.csv"), commits([shaD, sha1_hex("d1"), sha1_hex("d2")], dates[:3]))
    put(req_raw("yield_M.csv", shaM), w.m_text)
    put(req_raw("yield_D.csv", shaD), w.d_text)
    put(req_contents("yield_M.csv", shaM), json.dumps({"name": "yield_M.csv", "sha": git_blob_sha(w.m_text.encode())}))
    put(req_contents("yield_D.csv", shaD), json.dumps({"name": "yield_D.csv", "sha": git_blob_sha(w.d_text.encode())}))
    put(STATIC_REQS[0], w.page)
    put(STATIC_REQS[1], w.jma_text)
    put(STATIC_REQS[2], w.jma_page)
    put(req_raw("yield_M.csv", JULY_SHA), w.july_text)
    put(req_raw("yield_M.csv", APRIL_SHA), w.april_text)
    w.mof_path = os.path.join(tmp, "mof.csv")
    with open(w.mof_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(w.mof_text)
    rows_log = [["2026-10-19T12:00:%02d.%03dZ" % (2 * i, 100 + i), r["host"], r["target"], "200", str(len(b)), sha256_of(b)] for i, (r, b) in enumerate(bodies)]
    w.fetch_text = render_csv("fetch_log.csv", rows_log, log_source(rows_log))
    w.log_rows = rows_log
    return w


_WORLD = [None, None, None]        # world, tempdir, parsed inputs


def world():
    if _WORLD[0] is None:
        _WORLD[1] = tempfile.TemporaryDirectory()
        _WORLD[0] = build_world(_WORLD[1].name)
        _WORLD[2] = load_inputs(_WORLD[0].cache, _WORLD[0].mof_path)
    return _WORLD[0], _WORLD[2]


def world_close():
    if _WORLD[1] is not None:
        _WORLD[1].cleanup()
    _WORLD[:] = [None, None, None]


def world_out(tmp):
    w, inp = world()
    out = os.path.join(tmp, "out")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "fetch_log.csv"), "w", encoding="utf-8", newline="") as fh:
        fh.write(w.fetch_text)
    return out


def mini_world(dash=()):
    """Three months of MoF days with the monthly file's TP + ER set to the mean of the non-missing days (the identity holds)."""
    days = []
    for m in (1, 2, 3):
        days += [d for d in bdays("2025-%02d-01" % m, "2025-%02d-28" % m)][:15]
    text = mof_text(days, dash_days=set(dash))
    by = {}
    for i, d in enumerate(days):
        if d not in dash:
            by.setdefault(mkey(d), []).append(i)
    rows = []
    for m, idx in sorted(by.items()):
        vals = {"ShadowRate": 0.0}
        for k in NAK_KS:
            y = math.fsum(mof_value(k, i) for i in idx) / len(idx)
            tp = round(0.55 * y, 4)
            vals["TermPremium-%dY" % k], vals["ExpectedRate-%dY" % k] = tp, round(y - tp, 4)
        rows.append((m, vals))
    return text, rows


def nak_rows_for(periods, tp10, er10=None):
    out = []
    for p, t in zip(periods, tp10):
        vals = {c: 0.1 for c in NAK_COLS}
        vals["TermPremium-10Y"] = t
        vals["ExpectedRate-10Y"] = er10 if er10 is not None else 0.5
        out.append((p, vals))
    return out


def ser_of(tp, er):
    """tp, er: {month: value}, used at every tenor."""
    return Ser({k: dict(tp) for k in NAK_KS}, {k: dict(er) for k in NAK_KS})


# ---- tests --------------------------------------------------------------------------------------------------------------------
def t_g1(ck):
    row = {c: 0.0 for c in NAK_COLS}
    row.update({"TermPremium-10Y": 0.1234, "ExpectedRate-10Y": 0.9876, "TermPremium-2Y": 0.0111, "ExpectedRate-2Y": 0.0222})
    for order in ("default", "swapped"):
        n = parse_nakajima(nak_text([("199501", row)], order=order))
        ck.close("TermPremium-10Y read by name (%s column order)" % order, n.rows["199501"]["TermPremium-10Y"], 0.1234, 1e-12)
        ck.close("ExpectedRate-10Y read by name (%s)" % order, n.rows["199501"]["ExpectedRate-10Y"], 0.9876, 1e-12)
        ck.close("TermPremium-2Y read by name (%s)" % order, n.rows["199501"]["TermPremium-2Y"], 0.0111, 1e-12)
    ck.raises("a header without a required column is refused", DataError, lambda: parse_nakajima('"YYYYMM","ShadowRate"\r\n199501,0.1\r\n'))


def t_g2(ck):
    ser = Ser({10: {"202312": 0.10, "202609": 0.70}}, {10: {"202312": 0.60, "202609": 0.90}})
    d_tp, d_er = stat_vintage([ser], 10, "202312", "202609")
    ck.close("d_tp = end - start", d_tp, 0.60, 1e-12)
    ck.close("d_er = end - start", d_er, 0.30, 1e-12)
    st = classify("FULL", d_tp, d_er)
    ck.close("d_yield = d_tp + d_er is positive for a rising yield", st.d_yield, 0.90, 1e-12)


def t_g3(ck):
    s1 = classify("FULL", 0.8, 0.4)
    ck.close("s = d_tp / d_yield (0.8 / 1.2)", s1.share, 0.8 / 1.2, 1e-12)
    s2 = classify("FULL", 0.3, 0.9)
    ck.close("s = d_tp / d_yield (0.3 / 1.2 = 0.25)", s2.share, 0.25, 1e-12)
    ck.eq("0.25 is expected rates larger", s2.cls, "EXPECTED_RATES_LARGER")


def t_g4(ck):
    nc = classify("FULL", 0.1, 0.1499)
    ck.eq("dy 0.2499 is not classified", nc.cls, "NOT_CLASSIFIED")
    ck.eq("...and tp_share and distance_bp are blank for it", (nc.share, nc.distance), (None, None))
    ck.eq("...as committed text", (f(nc.share, 4), fs(nc.distance, 1)), ("", ""))
    c25 = classify("FULL", 0.1, 0.15)
    ck.eq("dy 0.25 exactly is classified", c25.cls, "CLOSE_TO_EVEN")
    ng = classify("FULL", -0.2, -0.1)
    ck.eq("a negative dy is not classified", ng.cls, "NOT_CLASSIFIED")
    r = classify("FULL", 1.2351, 1.0710)
    ck.eq("s 0.5356 is CLOSE_TO_EVEN, not a larger part", r.cls, "CLOSE_TO_EVEN")
    ck.eq("s 0.5356 is committed as 0.5356", f(r.share, 4), "0.5356")
    ck.eq("distance_bp is +8.2 (share - 0.5, times the yield change, times 100)", fs(r.distance, 1), "+8.2")
    ck.close("distance_bp unrounded", r.distance, (1.2351 - 1.0710) / 2 * 100, 1e-9)
    ck.eq("s exactly 0.40 is CLOSE_TO_EVEN", classify("FULL", 0.8, 1.2).cls, "CLOSE_TO_EVEN")
    ck.eq("s exactly 0.60 is CLOSE_TO_EVEN", classify("FULL", 1.2, 0.8).cls, "CLOSE_TO_EVEN")
    ck.eq("s 0.3999 is EXPECTED_RATES_LARGER, not close to even", classify("FULL", 0.3999, 0.6001).cls, "EXPECTED_RATES_LARGER")
    ck.eq("s 0.6001 is TERM_PREMIUM_LARGER", classify("FULL", 0.6001, 0.3999).cls, "TERM_PREMIUM_LARGER")
    ck.eq("float error cannot move the 0.60 edge (0.1506 / 0.2510 is 0.6000000000000001)", classify("FULL", 0.1506, 0.1004).cls, "CLOSE_TO_EVEN")
    ck.eq("float error cannot move the 0.40 edge (0.1002 / 0.2505 is 0.39999999999999997)", classify("FULL", 0.1002, 0.1503).cls, "CLOSE_TO_EVEN")
    br = classify("BRIDGE", 0.3, 0.2)
    ck.eq("a bridge window with dy 0.5 is NOT_APPLICABLE with blank share", (br.cls, br.share, br.distance), ("NOT_APPLICABLE", None, None))


def t_g5(ck):
    r = classify("FULL", -0.10, 0.50)
    ck.close("d_tp -0.10, d_er +0.50: s = -0.25", r.share, -0.25, 1e-12)
    ck.eq("...EXPECTED_RATES_LARGER", r.cls, "EXPECTED_RATES_LARGER")
    ck.eq("...opposite signs", r.opposite, True)
    ck.close("...dy is 0.40 (signed sum)", r.d_yield, 0.40, 1e-12)
    ck.eq("...distance is -30.0", fs(r.distance, 1), "-30.0")
    ck.eq("same signs: not opposite", classify("FULL", 0.3, 0.4).opposite, False)


WIN_MONTHS_T = ["202312", "202407", "202408", "202411", "202412", "202501", "202603", "202606", "202609"]


def t_g6(ck):
    tp = {m: round(0.05 * i * i + 0.01, 4) for i, m in enumerate(WIN_MONTHS_T)}
    er = {m: round(0.30 + 0.17 * i, 4) for i, m in enumerate(WIN_MONTHS_T)}
    ser = ser_of(tp, er)
    rows, stats = decomposition("M", ser, "v")
    want = {"FULL": ("202312", "202609"), "A": ("202312", "202407"), "BRIDGE": ("202407", "202408"), "B": ("202408", "202609"), "BOJ_MATCH": ("202408", "202606"),
            "Y2024": ("202312", "202412"), "Y2025_26": ("202412", "202609")}
    for wid, (a, b) in want.items():
        ck.close("window %s d_tp = tp[%s] - tp[%s]" % (wid, b, a), stats[("10Y", wid)].d_tp, tp[b] - tp[a], 1e-12)
        ck.close("window %s d_er" % wid, stats[("10Y", wid)].d_er, er[b] - er[a], 1e-12)
    ck.eq("28 rows from one variant", len(rows), 28)
    ck.eq("FULL = A + BRIDGE + B and FULL = Y2024 + Y2025_26 (1e-9)", identity_problems(stats), [])
    ck.eq("the window table: B starts at 202408, the first named month", WINDOWS["B"], ("202408", "202609"))


def t_g7(ck):
    new = ser_of({"202312": 0.10, "202407": 0.2, "202408": 0.3, "202606": 0.9}, {"202312": 0.5, "202407": 0.6, "202408": 0.7, "202606": 1.0})
    old = ser_of({"202312": 0.12, "202407": 0.2, "202408": 0.3, "202606": 0.9, "202609": 1.5}, {"202312": 0.55, "202407": 0.6, "202408": 0.7, "202606": 1.0, "202609": 1.6})
    ck.raises("a month missing in the newest vintage is not filled from an older one", DataError, lambda: stat_vintage([new, old], 10, "202312", "202609"))
    new2 = ser_of({"202312": 0.10, "202609": 1.0}, {"202312": 0.5, "202609": 1.5})
    d_tp, d_er = stat_vintage([new2, old], 10, "202312", "202609")
    ck.close("one vintage per statistic: start and end both from the newest (d_tp 0.90, not 1.38)", d_tp, 0.90, 1e-12)
    ck.close("...d_er 1.0", d_er, 1.0, 1e-12)
    # the frozen verdict: a later vintage never rewrites a registered row
    fresh1 = {t: dict({c: "x1" for c in V_CONTENT}, vintage_id="V1", tenor=t) for t in TENORS}
    rows1, _ = reconcile_verdict([], fresh1, "V1", "T1")
    ck.eq("first build: four registered rows", [r[V_IX["status"]] for r in rows1], ["registered"] * 4)
    fresh2 = {t: dict({c: "x2" for c in V_CONTENT}, vintage_id="V2", tenor=t) for t in TENORS}
    rows2, _ = reconcile_verdict(rows1, fresh2, "V2", "T2")
    ck.eq("later vintage: the registered rows are untouched", rows2[:4], rows1)
    ck.eq("...and four later_vintage rows are added", [r[V_IX["status"]] for r in rows2[4:]], ["later_vintage"] * 4)
    ck.eq("...with the later vintage in them", {r[V_IX["vintage_id"]] for r in rows2[4:]}, {"V2"})


def t_g8(ck):
    row = {c: 0.1 for c in NAK_COLS}
    row.update({"TermPremium-10Y": -0.0583, "TermPremium-5Y": "-1e-04", "ExpectedRate-10Y": 0.7444})
    txt = nak_text([("199501", row)])
    ck.ok("the fixture has the real quoted header", txt.startswith('"YYYYMM","ShadowRate","TermPremium-2Y"'))
    n = parse_nakajima(txt)
    ck.close("a -1e-04 cell parses as -0.0001", n.rows["199501"]["TermPremium-5Y"], -0.0001, 1e-15)
    ck.close("-0.0583 keeps its sign", n.rows["199501"]["TermPremium-10Y"], -0.0583, 1e-15)
    ck.ok("column names carry no quote", all('"' not in c for c in NAK_COLS) and "TermPremium-10Y" in n.rows["199501"])
    mtext, mrows = mini_world()
    mn = parse_nakajima(nak_text(mrows))
    ser = nak_to_ser(mn)
    mof = parse_mof(mtext)
    gaps = fitted_monthly(ser, mof_by_month(mof, 10), 10, ["202501", "202502", "202503"])
    ck.ok("values are percent as published (not scaled): the fitted identity holds on the fixture", len(gaps) == 3 and all(within_pub(g) for _, g in gaps), str(gaps))
    ck.ok("a daily-file fixture parses with the daily key", parse_nakajima(nak_text([("20250102", row)], daily=True), daily=True).periods == ["20250102"])


def t_g9(ck):
    mtext, mrows = mini_world()
    ser = nak_to_ser(parse_nakajima(nak_text(mrows)))
    mof = parse_mof(mtext)
    months = ["202501", "202502", "202503"]
    for k in (2, 10, 20):
        g = fitted_monthly(ser, mof_by_month(mof, k), k, months)
        ck.ok("monthly-mean basis: every %dY gap within 0.00015" % k, len(g) == 3 and all(within_pub(x) for _, x in g), str(g))
    days = bdays("2025-01-01", "2025-01-28")[:15]
    mtext2 = mof_text(days, last_bump={days[-1]: 0.0694})
    vals = [round(mof_value(10, i) + (0.0694 if i == 14 else 0.0), 3) for i in range(15)]
    mean_y = math.fsum(vals) / 15
    tp2 = round(0.55 * mean_y, 4)
    ser2 = ser_of({"202501": tp2}, {"202501": round(mean_y - tp2, 4)})
    bym = mof_by_month(parse_mof(mtext2), 10)
    g_mean = fitted_monthly(ser2, bym, 10, ["202501"], "mean")
    g_end = fitted_monthly(ser2, bym, 10, ["202501"], "month_end")
    ck.ok("mean basis passes on the fixture", g_mean and within_pub(g_mean[0][1]), str(g_mean))
    ck.ok("month-end basis shows the 0.06 gap and fails the tolerance", g_end and abs(g_end[0][1]) > 0.05 and not within_pub(g_end[0][1]), str(g_end))
    dash_days = {days[i] for i in (2, 5, 7)}
    dtext, drows = mini_world(dash=dash_days)
    dser = nak_to_ser(parse_nakajima(nak_text(drows)))
    dmof = parse_mof(dtext)
    dg = fitted_monthly(dser, mof_by_month(dmof, 10), 10, ["202501"])
    ck.ok("MoF '-' is missing, not zero: the 12-day mean fits", dg and within_pub(dg[0][1]), str(dg))
    ck.eq("a '-' cell is None", dmof[sorted(dash_days)[0]][10], None)
    ck.eq("the title row is skipped (45 data rows)", len(mof), 45)
    ck.ok("TP + ER, not TP - ER: the fixture gap is small", all(abs(x) < 0.01 for _, x in g_mean), str(g_mean))
    ck.ok("0.00014 passes the published-cell tolerance", within_pub(0.00014))
    ck.ok("0.00016 fails the published-cell tolerance", not within_pub(0.00016))
    ck.ok("a recomputed mean within 5e-7 passes the 1e-6 tolerance", within_recomp(1.0, 1.0 + 5e-7))
    ck.ok("a recomputed mean 5e-6 off fails the 1e-6 tolerance", not within_recomp(1.0, 1.0 + 5e-6))
    one = {c: 0.0 for c in NAK_COLS}
    one.update({"TermPremium-10Y": 0.3, "ExpectedRate-10Y": 0.0})
    gd, od, om = fitted_daily(parse_nakajima(nak_text([("20250102", one)], daily=True), daily=True),
                              {D_("2025-01-02"): {10: 0.3001}, D_("2025-01-03"): {10: 0.5}}, 10, D_("2025-01-01"), D_("2025-01-31"))
    ck.eq("daily gap on the one common date (0.3 + 0 - 0.3001), one date only in the MoF file", (len(gd), od, om, round(gd[0][1], 6)), (1, 0, 1, -0.0001))


def t_g10(ck):
    nak = parse_nakajima(nak_text(nak_rows_for(["202501", "202502", "202503", "202504", "202505"], [0.1234, 0.2345, 0.3456, 0.4567, 0.5678])))
    src = "# source: test fixture"
    oct_id = "2026-10-06_33118433fe95"
    pins_ok = [[oct_id, "nakajima_monthly", "TermPremium-10Y", "202312", "-0.0583", "percent"], [oct_id, "nakajima_monthly", "ExpectedRate-10Y", "202312", "0.7444", "percent"],
               [oct_id, "nakajima_monthly", "TermPremium-10Y", "202609", "1.1768", "percent"], [oct_id, "nakajima_monthly", "ExpectedRate-10Y", "202609", "1.8154", "percent"]]
    dec = [[oct_id, "M", "10Y", "FULL", "202312", "202609", "2.3061", "1.2351", "1.0710", "0.5356", "+8.2", "CLOSE_TO_EVEN", "no", "REGISTERED"]]
    fit = [[oct_id, "yield_M.csv", "10Y", "window", "monthly_mean", "34", "0.00010", "0.00005", "0", "PASS"]]
    chk_ = [["C04a", "four October pins", "match", "match", "PASS"], ["C11a", "supervisor pins", "d_tp 1.2351", "d_tp 1.2351", "PASS"]]
    log = [["2026-10-19T12:00:00.000Z", "api.github.com", "/repos/x", "200", "10", "ab"]]

    def folder(**over):
        t = {"decomposition.csv": render_csv("decomposition.csv", dec, src), "verdict.csv": render_csv("verdict.csv", [], src),
             "vintage_revisions.csv": render_csv("vintage_revisions.csv", [], src), "fitted_check.csv": render_csv("fitted_check.csv", fit, src),
             "vintages.csv": render_csv("vintages.csv", [], src), "pins.csv": render_csv("pins.csv", pins_ok, src), "checks.csv": render_csv("checks.csv", chk_, src),
             "fetch_log.csv": render_csv("fetch_log.csv", log, src), "README.md": "A readme.\n", "SOURCES.md": "Sources.\n"}
        t.update(over)
        return t
    tags = lambda texts: {p[1] for p in leak_guard(texts, [nak])}
    ck.eq("the clean folder passes", leak_guard(folder(), [nak]), [])
    ck.ok("(a) a copy of the monthly file is caught", "a" in tags(folder(**{"yield_M.csv": nak_text(nak_rows_for(["202501"], [0.1]))})))
    ck.ok("(b) the same bytes as x.csv are caught as a file not on the list", "b" in tags(folder(**{"x.csv": nak_text(nak_rows_for(["202501"], [0.1]))})))
    bad_hdr = folder(**{"decomposition.csv": render_csv("decomposition.csv", dec, src).replace("tp_share", "tp10_level")})
    ck.ok("(c) a tp10_level column is caught", "c" in tags(bad_hdr))
    fifth = pins_ok + [[oct_id, "nakajima_monthly", "TermPremium-10Y", "202407", "0.3000", "percent"]]
    ck.ok("(d) a fifth October pin is caught", "d" in tags(folder(**{"pins.csv": render_csv("pins.csv", fifth, src)})))
    april = [["2026-04-20_8f940a0141ee", "nakajima_monthly", "TermPremium-10Y", "202312", "-0.0583", "percent"]]
    ck.ok("(d) a pin for the April vintage is caught", "d" in tags(folder(**{"pins.csv": render_csv("pins.csv", april, src)})))
    daily = [["2026-10-06_aaaaaaaaaaaa", "nakajima_daily", "TermPremium-10Y", "202312", "-0.0583", "percent"]]
    ck.ok("(d) a pin for a daily-file vintage is caught", "d" in tags(folder(**{"pins.csv": render_csv("pins.csv", daily, src)})))
    trip = [[oct_id, "yield_M.csv", "10Y", "window", "monthly_mean", "34", f(nak.rows[p]["TermPremium-10Y"], 4), "0.00005", "0", "PASS"] for p in nak.periods[:3]]
    ck.ok("(e) a column of three consecutive raw monthly levels is caught", "e" in tags(folder(**{"fitted_check.csv": render_csv("fitted_check.csv", trip, src)})))
    out_month = [dec[0][:4] + ["202501"] + dec[0][5:]]
    ck.ok("(f) a month outside the seven-month list is caught", "f" in tags(folder(**{"decomposition.csv": render_csv("decomposition.csv", out_month, src)})))
    out_day = [dec[0][:4] + ["20260930"] + dec[0][5:]]
    ck.ok("(f) a daily date is caught", "f" in tags(folder(**{"decomposition.csv": render_csv("decomposition.csv", out_day, src)})))
    lv = [["C04a", "four October pins", "match", "1.1768", "PASS"]]
    ck.ok("(g) a pinned level value in checks.csv is caught", "g" in tags(folder(**{"checks.csv": render_csv("checks.csv", lv, src)})))
    lv2 = [["C05x", "a level", "match", "ShadowRate 201609 -3.2823", "INFO"]]
    ck.ok("(g) a named level in checks.csv is caught", "g" in tags(folder(**{"checks.csv": render_csv("checks.csv", lv2, src)})))
    lv3 = [["C04a", "a level check", "match", "-0.0583", "PASS"]]
    ck.ok("(g) a number in a level check's observed cell is caught", "g" in tags(folder(**{"checks.csv": render_csv("checks.csv", lv3, src)})))


def t_g11(ck):
    with open(SPEC_PATH[0], encoding="utf-8") as fh:
        spec = fh.read()
    if M("spec_edit"):
        spec = spec.replace("d_tp_pp", "d_tp_pq", 1)
    m = re.search(r"```ALLOWLIST\n(.*?)```", spec, re.S)
    ck.ok("the spec carries an ALLOWLIST block", bool(m))
    allow, files = {}, None
    for ln in (m.group(1).splitlines() if m else []):
        if ln.startswith("FILES:"):
            files = [x.strip() for x in ln[len("FILES:"):].split(",")]
        elif ": " in ln:
            name, cols = ln.split(":", 1)
            allow[name.strip()] = [c.strip() for c in cols.split(",")]
    ck.eq("the spec's file list equals FILES", files, files_list())
    ck.eq("the spec names exactly the files that have an allowlist", sorted(allow), sorted(ALLOW))
    for name in sorted(allow):
        ck.eq("ALLOW equals the spec's block: %s" % name, allow[name], allowlist(name) if name in ALLOW else None)
    ck.raises("an extra column is refused", DataError, lambda: check_header("pins.csv", PIN_COLS + ["extra"]))
    ck.raises("a renamed column is refused", DataError, lambda: check_header("pins.csv", PIN_COLS[:-1] + ["units"]))
    ck.ok("the exact header is accepted", check_header("pins.csv", PIN_COLS) is None)


def fake_rig(tmp, script, max_requests=MAX_REQUESTS, sleep=MIN_SLEEP, clock=None):
    clock = clock or FakeClock()
    calls = []

    def opener(host, target, headers, timeout, cap):
        calls.append((host, target, dict(headers), clock.wall()))
        res = script(host, target, headers) if callable(script) else script
        if isinstance(res, Exception):
            raise res
        return res
    fe = Fetcher(os.path.join(tmp, "cache"), os.path.join(tmp, "out"), sleep=sleep, max_requests=max_requests, opener=opener, wall=clock.wall, mono=clock.wall,
                 sleeper=clock.sleep, stop_path=os.path.join(tmp, "cache", "STOP"), utc=lambda: dt.datetime(2026, 10, 19, 12, 0, 0, tzinfo=UTC),
                 root=os.path.join(tmp, "norepo"))
    return fe, calls, clock


def good_commits_body():
    return json.dumps([{"sha": "a" * 40, "commit": {"committer": {"date": "2026-10-06T00:48:15Z"}}}]).encode()


def t_g12(ck):
    req = req_commits("yield_M.csv")

    def latches(label, script, want_text=None, avoid_text=None):
        with tempfile.TemporaryDirectory() as tmp:
            fe, calls, _ = fake_rig(tmp, script)
            msg = ""
            try:
                fe.fetch_one(req)
            except Latched as e:
                msg = str(e)
            stop = os.path.exists(os.path.join(tmp, "cache", "STOP"))
            ck.eq("%s: STOP written" % label, stop, True)
            if want_text:
                txt = open(os.path.join(tmp, "cache", "STOP")).read() if stop else ""
                ck.ok("%s: reported as %r" % (label, want_text), want_text in msg and want_text in txt, msg)
            if avoid_text:
                ck.ok("%s: not reported as %r" % (label, avoid_text), avoid_text not in msg, msg)
    for st in (403, 404, 500):
        latches("HTTP %d latches" % st, (lambda s: lambda h, t, hd: (s, b"", {}))(st))
    for st in (403, 429):
        latches("HTTP %d from GitHub is rate limiting" % st, (lambda s: lambda h, t, hd: (s, b"", {}))(st), "rate limited", "file absent")
    for st in (301, 302):
        latches("a redirect (%d) latches and is not followed" % st, (lambda s: lambda h, t, hd: (s, b"", {"location": "https://example.com"}))(st))
    latches("a 200 that is not the file latches", lambda h, t, hd: (200, b"<html>blocked</html>", {}))
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _ = fake_rig(tmp, lambda h, t, hd: (200, good_commits_body(), {}))
        ck.eq("a good body is saved without a latch", (fe.fetch_one(req), os.path.exists(os.path.join(tmp, "cache", "STOP"))), ("saved", False))
        ck.eq("the request carries the neutral User-Agent", calls[0][2].get("User-Agent"), UA)
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _ = fake_rig(tmp, SocketFault("timeout"))
        try:
            fe.fetch_one(req)
        except SocketFault:
            pass
        ck.eq("a socket fault does not latch", os.path.exists(os.path.join(tmp, "cache", "STOP")), False)
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _ = fake_rig(tmp, lambda h, t, hd: (200, good_commits_body(), {}))
        os.makedirs(os.path.join(tmp, "cache"))
        with open(os.path.join(tmp, "cache", "STOP"), "w") as fh:
            fh.write("x\n")
        ck.raises("fetch refuses to run while STOP exists", Latched, lambda: fe.fetch_one(req))
        ck.eq("...and sends no request", len(calls), 0)
    sha = "0123456789abcdef0123456789abcdef01234567"
    for url in ("https://fred.stlouisfed.org/graph/fredgraph.csv?id=JPN", "https://www.sec.gov/cgi-bin/browse-edgar", "https://data.sec.gov/submissions/x.json",
                "https://github.com/jouchinakajima/program/blob/main/yield_M.csv", "https://example.com/x",
                "https://raw.githubusercontent.com/jouchinakajima/program/main/yield_M.csv",
                "https://raw.githubusercontent.com/jouchinakajima/program/%s/other.csv" % sha, "http://raw.githubusercontent.com/jouchinakajima/program/%s/yield_M.csv" % sha):
        ck.raises("refused before any request: %s" % url[:70], Refused, lambda u=url: check_url(u))
    for url in ("https://raw.githubusercontent.com/jouchinakajima/program/%s/yield_M.csv" % sha, "https://api.github.com" + COMMITS_PATH.format(f="yield_D.csv"),
                "https://api.github.com" + CONTENTS_PATH.format(f="yield_M.csv", sha=sha), "https://sites.google.com" + PAGE_PATH, "https://takujiokubo.github.io" + JMA_CSV_PATH,
                "https://takujiokubo.github.io" + JMA_PAGE_PATH):
        ck.ok("accepted: %s" % url[8:70], check_url(url)[0] in HOST_ALLOW)
    ck.raises("an address in the identification string is refused", Refused, lambda: assert_ua("research tool (a" + chr(64) + "b.example)"))
    ck.ok("the identification string is the CLAUDE.md string, with no address", UA == "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)" and chr(64) not in UA)
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = fake_rig(tmp, lambda h, t, hd: (200, good_commits_body(), {}))
        for i in range(3):
            fe.fetch_one(dict(req, file="x%d.json" % i))
        starts = [c[3] for c in calls]
        ck.ok("request starts are at least 2 s apart", len(starts) == 3 and all(b - a >= 2.0 for a, b in zip(starts, starts[1:])), str(starts))
    ck.raises("--max-requests 16 is refused (the cap is 15)", Refused, lambda: Fetcher("/tmp/x_never_used", "/tmp/y", max_requests=16, root="/nonexistent_root"))
    ck.raises("--sleep below 2 is refused", Refused, lambda: Fetcher("/tmp/x_never_used", "/tmp/y", sleep=1.0, root="/nonexistent_root"))
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _ = fake_rig(tmp, lambda h, t, hd: (200, good_commits_body(), {}), max_requests=2)
        raised = None
        try:
            for i in range(3):
                fe.fetch_one(dict(req, file="y%d.json" % i))
        except MaxRequests as e:
            raised = e
        ck.ok("the request beyond the cap is not sent", raised is not None and len(calls) == 2)
    src = own_source() + (STOP_REMOVER_SOURCE if M("stop_remover") else "")
    ck.eq("a static scan finds no code that removes or renames STOP", static_stop_scan(src), [])
    ck.ok("...and the scan does find a function that removes it", static_stop_scan(own_source() + STOP_REMOVER_SOURCE) != [])
    ck.ok("...and one that renames it", static_stop_scan("import os\ndef f():\n    os.rename(STOP_PATH, 'x')\n") != [])
    ck.eq("...but not a plain file replace", static_stop_scan("import os\ndef f(p):\n    os.replace(p + '.part', p)\n"), [])


def t_g13(ck):
    bad = ["the move was caused by x", "yields drove the curve", "it is driven by purchases", "this led to a rise", "it prompted a sale", "which pushed it up", "in response to purchases"]
    for t in bad:
        ck.ok("causal wording is flagged: %r" % t, causal_hits(t))
    ck.eq("the required sentence passes", causal_hits(REQUIRED_SENTENCE), [])
    ck.ok("the required sentence with 'driven by purchases' added fails", causal_hits(REQUIRED_SENTENCE + " It was driven by purchases."))
    ck.ok("the required sentence with 'in response to purchases' added fails", causal_hits(REQUIRED_SENTENCE + " It rose in response to purchases."))
    ck.raises("guard_text refuses causal wording", DataError, lambda: guard_text("README.md", "A rise caused by flows."))
    ck.ok("guard_text accepts the required sentence", guard_text("README.md", REQUIRED_SENTENCE) is None)
    ck.ok("the project's pattern is the one imported from fx_rate_gap, unchanged", fx.CAUSAL_RX.pattern.startswith("\\b(caus(?:e|ed|es|ing)|drove|driv"))


def t_g14(ck):
    txt = jma_text(ym_range("2026-07", "2026-09"), ym_range("2026-10", "2026-12"), dup_forecast="2026-09")
    jma, info = parse_jma(txt)
    ck.eq("only actual rows are used (the forecast months are absent)", sorted(jma), ["202607", "202608", "202609"])
    ck.ok("a forecast row for an actual month does not overwrite it", abs(jma["202609"][10][0] - round(1.0 + 0.02 * 2 + 0.2, 4)) < 1e-9, str(jma["202609"][10]))
    ser = jma_to_ser(jma)
    ck.ok("a forecast month cannot be an end month", "202610" not in ser.tp[10] and "202612" not in ser.er[10])
    ck.eq("the file's row types are counted", info["types"].get("forecast"), 4)


def t_g15(ck):
    arms = jma_arms
    ck.eq("ratio: 0.49 x fires", arms(1.0, 0.49, 0.30, 0.30), ("model_sensitive", "ratio"))
    ck.eq("ratio: 0.50 x does not", arms(1.0, 0.50, 0.30, 0.30), ("not_flagged", ""))
    ck.eq("ratio: 2.01 x fires", arms(1.0, 2.01, 0.30, 0.30), ("model_sensitive", "ratio"))
    ck.eq("ratio: 2.00 x does not", arms(1.0, 2.00, 0.30, 0.30), ("not_flagged", ""))
    ck.eq("ratio: 0.5 x of 1.2351 does not fire (rounded comparison)", arms(1.2351, 0.61755, 0.30, 0.30), ("not_flagged", ""))
    ck.eq("share: 0.3000 against 0.4501 fires", arms(1.0, 1.0, 0.3000, 0.4501), ("model_sensitive", "share"))
    ck.eq("share: 0.3000 against 0.4500 (exactly 0.15) does not", arms(1.0, 1.0, 0.3000, 0.4500), ("not_flagged", ""))
    ck.eq("side: 0.51 against 0.49 fires", arms(1.0, 1.0, 0.51, 0.49), ("model_sensitive", "side"))
    ck.eq("side: 0.51 against exactly 0.50 does not", arms(1.0, 1.0, 0.51, 0.50), ("not_flagged", ""))
    ck.eq("share and side together are joined with +", arms(1.0, 1.0, 0.54, 0.29), ("model_sensitive", "share+side"))
    ck.eq("all three arms", arms(1.0, 0.3, 0.60, 0.40), ("model_sensitive", "ratio+share+side"))
    ck.eq("a missing JMA share cannot fire the share and side arms", arms(1.0, 1.0, 0.54, None), ("not_flagged", ""))


def t_g16(ck):
    ck.raises("a cache inside the repository is refused", Refused, lambda: check_cache(os.path.join(ROOT, "data", "vintages", "x")))
    ck.raises("the repository root as a cache is refused", Refused, lambda: check_cache(ROOT))
    ck.ok("the default cache is accepted", check_cache(CACHE_DEFAULT) is not None)
    with tempfile.TemporaryDirectory() as tmp:
        ck.ok("a temporary directory is accepted", check_cache(tmp) is not None)
        ck.raises("the Fetcher refuses a cache in the repository", Refused, lambda: Fetcher(os.path.join(ROOT, "data", "x_cache"), tmp))


def t_g17(ck):
    one = lambda tp: dict({c: 0.0 for c in NAK_COLS}, **{"TermPremium-10Y": tp, "ExpectedRate-10Y": 0.0})
    n = parse_nakajima(nak_text([("20250102", one(1.0)), ("20250103", one(2.0)), ("20250106", one(6.0))], daily=True), daily=True)
    ser = daily_to_ser(n)
    ck.close("D is the monthly mean of the month's daily rows (3.0, not the last value 6.0)", ser.tp[10]["202501"], 3.0, 1e-12)
    w, inp = world()
    with tempfile.TemporaryDirectory() as tmp:
        out = world_out(tmp)
        R = compute(inp, w.log_rows, out)
    m10, d10 = R["st"]["M"][("10Y", "FULL")], R["st"]["D"][("10Y", "FULL")]
    ck.eq("fixture: the monthly file is close to even, the daily file is not", (m10.cls, d10.cls), ("CLOSE_TO_EVEN", "TERM_PREMIUM_LARGER"))
    ck.eq("the registered classification is the monthly file's", R["verdict_fresh"]["10Y"]["classification"], "CLOSE_TO_EVEN")
    ck.eq("the daily file's class sits beside it", R["verdict_fresh"]["10Y"]["d_variant_classification"], "TERM_PREMIUM_LARGER")
    ck.eq("the headline reading uses both files", R["headline"], "differs_between_monthly_and_daily_files")
    ck.eq("both inside the band: close to even and model-dependent", headline_reading("CLOSE_TO_EVEN", "CLOSE_TO_EVEN"), "close_to_even_and_model_dependent")
    ck.eq("both outside and agreeing: the shared class", headline_reading("TERM_PREMIUM_LARGER", "TERM_PREMIUM_LARGER"), "TERM_PREMIUM_LARGER")
    ck.eq("M inside, D outside: they differ", headline_reading("CLOSE_TO_EVEN", "EXPECTED_RATES_LARGER"), "differs_between_monthly_and_daily_files")


def t_g18(ck):
    fresh = {t: dict({c: "x" for c in V_CONTENT}, vintage_id="V1", tenor=t) for t in TENORS}
    rows, _ = reconcile_verdict([], fresh, "V1", "T")
    again, _ = reconcile_verdict(rows, fresh, "V1", "T")
    ck.eq("a rebuild on the same vintage with the same values leaves the rows unchanged", again, rows)
    changed = {t: dict(fresh[t], tp_share="y") for t in TENORS}
    ck.raises("a changed frozen value fails without --amend", DataError, lambda: reconcile_verdict(rows, changed, "V1", "T"))
    am, notes = reconcile_verdict(rows, changed, "V1", "T", amend="a reason")
    ck.eq("--amend keeps the old rows (8 rows)", len(am), 8)
    ck.eq("...four superseded and four amended", sorted(r[V_IX["status"]] for r in am), ["amended"] * 4 + ["superseded"] * 4)
    ck.ok("...each superseded row points at its successor", all(r[V_IX["superseded_by"]] for r in am if r[V_IX["status"]] == "superseded"))
    ck.ok("...and the old values are still there", all(r[V_IX["tp_share"]] == "x" for r in am if r[V_IX["status"]] == "superseded"))
    w, inp = world()
    with tempfile.TemporaryDirectory() as tmp:
        out = world_out(tmp)
        R = compute(inp, w.log_rows, out)
        rows_ = [list(r) for r in R["dec_all"]]
        rows_[0][7] = "9.9999"
        write_text(os.path.join(out, "decomposition.csv"), render_csv("decomposition.csv", rows_, "# source: x"))
        ck.raises("a changed decomposition row for an existing vintage fails without --amend", DataError, lambda: compute(inp, w.log_rows, out))


def t_g19(ck):
    body = b"line one\r\nline two\r\n"
    want = hashlib.sha1(b"blob %d\x00" % len(body) + body).hexdigest()
    ck.eq("the blob sha is computed on the raw bytes (CRLF kept)", git_blob_sha(body), want)
    w, inp = world()
    inp2 = copy.copy(inp)
    inp2.contents = dict(inp.contents)
    inp2.contents["yield_M.csv"] = "0" * 40
    with tempfile.TemporaryDirectory() as tmp:
        out = world_out(tmp)
        R = compute(inp, w.log_rows, out)
        ck.eq("a matching API sha passes C02", [c for c in make_checks(inp, R, w.log_rows, False) if c[0] == "C02"][0][4], "PASS")
        ck.eq("a mismatching API sha fails C02", [c for c in make_checks(inp2, R, w.log_rows, False) if c[0] == "C02"][0][4], "FAIL")


def t_g20(ck):
    w, inp = world()
    with tempfile.TemporaryDirectory() as tmp:
        out = world_out(tmp)
        R = compute(inp, w.log_rows, out)
        texts = render_all(inp, R, w.log_rows, "PASS", "PASS", False, w.fetch_text)
    readme = texts["README.md"]
    ck.eq("the generated README passes every wording check", readme_problems(readme), [])
    ck.ok("it prints the Bank's words and the share with no verdict word", "roughly the same degree" in readme and boj_label_hits(readme) == [])
    ck.ok("it carries the convention sentence", CONVENTION_SENTENCE in readme)
    for w_ in ("is consistent with", "agrees with", "disagrees with", "contradicts", "confirms"):
        bad = readme.replace("no verdict is given.", "The model %s the Bank of Japan Review." % w_)
        ck.ok("a README saying %r beside the Bank is refused" % w_, readme_problems(bad) != [])
    ck.ok("a README without the convention sentence is refused", readme_problems(readme.replace(CONVENTION_SENTENCE, "")) != [])
    ck.ok("verdict.csv carrying 'agrees' is refused", boj_label_hits(texts["verdict.csv"].replace("registered", "agrees", 1)) != [])
    ck.ok("verdict.csv as written has no verdict word", boj_label_hits(texts["verdict.csv"]) == [])


def t_g21(ck):
    w, inp = world()
    outs = []
    for shift in (0, 40):
        base = dt.datetime(2026, 10, 20, 9, 0, 0, tzinfo=UTC)
        saved = _CLOCK[0]
        _CLOCK[0] = (lambda b=base, s=shift: b + dt.timedelta(days=s))
        try:
            with tempfile.TemporaryDirectory() as tmp:
                out = world_out(tmp)
                R, texts, leak, c14 = finish(inp, w.log_rows, out, None, False, w.fetch_text)
        finally:
            _CLOCK[0] = saved
        outs.append((texts, c14))
    ck.eq("a second build with the clock moved forward is byte-identical (C14)", outs[0][1], "PASS")
    ck.ok("two builds 40 days apart write identical files", outs[0][0] == outs[1][0])


def t_x1(ck):
    w, inp = world()
    with tempfile.TemporaryDirectory() as tmp:
        out = world_out(tmp)
        rc = build(w.cache, out, w.mof_path, say=lambda s: None)
        ck.eq("the synthetic build has no FAIL (return code 0)", rc, 0)
        names = sorted(os.listdir(out))
        ck.eq("the folder holds exactly the FILES list", names, sorted(FILES))
        sums = {n: sha256_of(read_bytes(os.path.join(out, n))) for n in names}
        rc2 = build(w.cache, out, w.mof_path, say=lambda s: None)
        sums2 = {n: sha256_of(read_bytes(os.path.join(out, n))) for n in names}
        ck.ok("a second build leaves every sha256 unchanged", rc2 == 0 and sums == sums2, str([n for n in sums if sums[n] != sums2.get(n)]))
        texts = {n: read_bytes(os.path.join(out, n)).decode("utf-8") for n in names}
        ck.eq("the leak guard passes on the written folder", leak_guard(texts, [parse_nakajima(w.m_text), parse_nakajima(w.d_text, daily=True)]), [])
        ck.ok("every CSV opens with a # source: line and a citation line", all(texts[n].startswith("# source:") and texts[n].split("\n")[1].startswith("# cite:") for n in CSV_FILES))
        dec = read_csv_text(texts["decomposition.csv"])[1]
        ck.eq("84 decomposition rows", len(dec), 84)
        ck.eq("verdict.csv has four registered rows", [r[V_IX["status"]] for r in read_csv_text(texts["verdict.csv"])[1]], ["registered"] * 4)
        ck.ok("the README opens with two sentences, the second the required sentence", texts["README.md"].split("\n\n")[1].endswith(REQUIRED_SENTENCE))
        fails = [c for c in read_csv_text(texts["checks.csv"])[1] if c[4] == "FAIL"]
        ck.ok("no check is FAIL", not fails, str([c[:1] + c[3:] for c in fails]))
        ck.ok("headers contain no spaces", all(" " not in h for n in CSV_FILES for h in read_csv_text(texts[n])[0]))


GUARDS = [
    ("G1", "columns by name: the quoted header, TP and ER blocks swapped", ["positional_columns"], t_g1),
    ("G2", "change direction: end minus start", ["change_reversed"], t_g2),
    ("G3", "share numerator: d_tp over d_yield", ["share_er_numerator", "share_tp_over_er"], t_g3),
    ("G4", "the rule and the band (3.2): 0.25, 0.40, 0.60, no larger label inside, blank share, distance x change",
     ["dy_classifies_2499", "dy_025_excluded", "no_close_band", "band_exclusive", "band_low_wide", "band_high_wide", "band_unrounded", "share_filled_nc", "distance_no_dy"], t_g4),
    ("G5", "opposite signs: the literal rule, not absolute values", ["abs_share"], t_g5),
    ("G6", "window additivity: base is the first named month; FULL = A + BRIDGE + B and FULL = Y2024 + Y2025_26",
     ["b_from_202407", "bridge_dropped", "y2526_from_202501", "y2024_to_202411"], t_g6),
    ("G7", "one vintage per statistic; no filling; a later vintage never rewrites a registered row", ["fill_older", "mix_vintages", "rewrite_registered"], t_g7),
    ("G8", "parsing: quoted header, -1e-04, sign, percent not scaled", ["pattern4", "quotes_kept", "sign_dropped", "scaled100"], t_g8),
    ("G9", "fitted identity: monthly mean not month-end, TP + ER, '-' is missing, title row skipped, each tolerance at its own level",
     ["fit_month_end_basis", "fit_tp_minus_er", "mof_dash_zero", "mof_title_as_data", "tol_loose_pub", "tol_loose_recomp"], t_g9),
    ("G10", "licence and leak guard (section 6), items (a) to (g) on planted folders",
     ["leak_a_off", "leak_b_off", "leak_c_off", "leak_d_cap_off", "leak_d_april_off", "leak_d_daily_off", "leak_e_off", "leak_f_off", "leak_g_off"], t_g10),
    ("G11", "allowlist anchor: the spec's ALLOWLIST block equals ALLOW and FILES", ["allow_extra_col", "spec_edit", "file_not_in_files"], t_g11),
    ("G12", "fetch safety: hosts, /main/, redirects, non-200, rate limiting, UA, 15 requests, pacing, STOP",
     ["allow_any_host", "allow_main", "no_latch_redirect", "no_latch_non200", "no_latch_bad_body", "rate_as_absent", "ua_check_off", "no_request_cap", "no_pacing", "stop_ignored",
      "stop_remover"], t_g12),
    ("G13", "no causal text: the project's pattern plus the local words; the required sentence passes", ["causal_guard_off", "causal_local_only", "causal_fx_only"], t_g13),
    ("G14", "JMA rows: actual only", ["jma_forecast_ok"], t_g14),
    ("G15", "JMA arms: each strict, on values rounded to 6 decimals", ["arm_le", "arm_dropped_ratio", "arm_dropped_share", "arm_dropped_side", "arms_missing", "arms_unrounded"], t_g15),
    ("G16", "cache location: outside the repository", ["cache_check_off"], t_g16),
    ("G17", "D aggregation: monthly mean; D never in the registered classification; the headline reads both", ["d_month_end", "d_in_registered", "headline_ignores_d"], t_g17),
    ("G18", "amendments: a changed frozen value fails; --amend keeps the old row", ["silent_overwrite", "amend_deletes_old"], t_g18),
    ("G19", "blob identity on bytes, and compared", ["blob_on_text", "blob_skip"], t_g19),
    ("G20", "the Bank's comparison carries no verdict; the convention sentence is required", ["boj_label_ok", "convention_not_required"], t_g20),
    ("G21", "timestamps come from the cache, never the clock", ["clock_stamp"], t_g21),
    ("X1", "an end-to-end synthetic build: structure, FILES, leak guard, byte-identical rebuild", [], t_x1),
]


def run_test(fn):
    ck = Checks()
    try:
        fn(ck)
    except Exception as e:                      # a test that crashes under a mutant has noticed it
        ck.ok("test ran to completion", False, "%s: %s" % (type(e).__name__, e))
    return ck


def selftest(mutants=True, only=None):
    t0 = time.time()
    bad_total, n_checks, n_mut = 0, 0, 0
    try:
        try:
            world()
        except Exception as e:                  # a forced mutant can break the synthetic world itself; the guards then record it
            print("setup: the synthetic world failed to build (%s: %s)" % (type(e).__name__, e))
            bad_total += 1
            world_close()
        for gid, desc, muts, fn in GUARDS:
            if only and gid not in only:
                continue
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
    finally:
        world_close()
    print("selftest: %d guards, %d checks, %d mutants applied one at a time, %d failure(s), %.1f s" % (len(GUARDS) if not only else len(only), n_checks, n_mut, bad_total, time.time() - t0))
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
    pb = sub.add_parser("build", help="offline: validate the cache and write every output")
    pb.add_argument("--cache", default=CACHE_DEFAULT)
    pb.add_argument("--out", default=OUT_DEFAULT)
    pb.add_argument("--mof", default=None, help="the MoF jgbcme_all.csv (read only)")
    pb.add_argument("--amend", default=None, help="a reason: appends an amended verdict row and marks the old one superseded")
    ps = sub.add_parser("selftest", help="synthetic data, mutants applied one at a time; no network")
    ps.add_argument("--no-mutants", action="store_true")
    ps.add_argument("--only", default=None, help="comma-separated guard ids (for development)")
    ps.add_argument("--spec", default=SPEC_DEFAULT)
    ps.add_argument("--force-mutant", default=None, help="run the whole selftest with this one mutant switched on (it must FAIL); used by the external proof loop")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "selftest":
            SPEC_PATH[0] = a.spec
            if a.force_mutant:
                _ACTIVE.add(a.force_mutant)
            return selftest(mutants=not a.no_mutants, only=set(a.only.split(",")) if a.only else None)
        if a.cmd == "build":
            mof = a.mof or (MOF_DEFAULT if os.path.exists(MOF_DEFAULT) else MOF_FALLBACK)
            if not os.path.exists(mof):
                raise Refused("no MoF file at %s (use --mof)" % tilde(mof))
            return build(a.cache, a.out, mof, amend=a.amend)
        fe = Fetcher(a.cache, a.out, sleep=a.sleep, max_requests=a.max_requests)
        fe.check_stop()
        saved = run_fetch(fe)
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
