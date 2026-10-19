#!/usr/bin/env python3
"""Japanese life insurers' acquisitions and dispositions of foreign long-term debt, monthly, from the Ministry of Finance's "International
Transactions in Securities" files (designated reporters). Python 3 standard library only.

  python3 bin/jp_life_foreign_bonds.py fetch [--cache DIR] [--out DIR] [--sleep 2.05] [--max-requests 20]   # the only network command
  python3 bin/jp_life_foreign_bonds.py build [--cache DIR] [--out DIR]                                      # offline; byte-identical on re-run
  python3 bin/jp_life_foreign_bonds.py selftest [--no-mutants]                                              # synthetic data only; no network

Specification: _research/2026-10-19-JP-Life-Insurers-Foreign-Bonds-Spec.md (committed at 777c976, with the supervisor's rulings of rounds 1 to 3).
The six descriptive questions of its section 4 and the frozen October 2026 rule of its section 5 are applied as written. Nothing here explains
why any investor acquired or disposed of bonds: the words are "net acquisition" and "net disposition", and disposition includes redemptions.

WHAT TOUCHES THE NETWORK. Only `fetch`. Hosts: www.mof.go.jp and www.boj.or.jp (any other host, FRED and sec.gov included, is refused before a
request is made, and each request must be one of the 16 exact URLs of the request table: four MoF CSVs first, then twelve BoJ statements).
GET only; one request at a time; at least 2 s between request starts, remembered across invocations in <cache>/.last_request; at most 20
requests per run; the CLAUDE.md non-SEC identification string (no address, no name); no redirect is followed.
TWO LATCHES. A MoF failure (any status other than 200, or a body that fails its content test) writes <default cache>/STOP and ends the run. A BoJ
failure writes <default cache>/STOP_BOJ and ends only the BoJ part. STOP_BOJ never gates a MoF fetch, a build or the scoring. Only a person deletes
either file: no code path here removes, renames or writes over them (the selftest scans this source to prove it). A socket fault ends the
invocation without latching. Nothing retries. Every request is one row of data/jp_life_foreign_bonds/fetch_log.csv.

WHERE THE FILES LIVE. The cache (default data/vintages/jp_life_foreign_bonds/) holds every raw MoF vintage and BoJ statement. It is gitignored.
A --cache path inside this repository is refused unless git reports it as ignored. Committed files follow the spec's section 6 and are written
by `build` only.

GUARDS AND THE SELFTEST. Every guard of the spec's section 7 (G1-G19) has a test with synthetic data; `selftest` applies each mutant (a
deliberately broken variant, switched on in this process only) and requires the test to notice it. A mutant not caught is a failure.
"""
import argparse
import ast
import contextlib
import csv
import datetime as dt
import hashlib
import http.client
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from fractions import Fraction
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(ROOT, "data", "jp_life_foreign_bonds")
CACHE_DEFAULT = os.path.join(ROOT, "data", "vintages", "jp_life_foreign_bonds")
STOP_PATH = os.path.join(CACHE_DEFAULT, "STOP")                  # fixed, whatever --cache says
STOP_BOJ_PATH = os.path.join(CACHE_DEFAULT, "STOP_BOJ")          # fixed, whatever --cache says
CALENDAR_PATH = os.path.join(ROOT, "CALENDAR.tsv")

# R2: the CLAUDE.md canonical string for every non-SEC host. No address, no name.
UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
HEADERS = {"User-Agent": UA, "Accept-Encoding": "identity", "Accept": "*/*"}
MIN_SLEEP = 2.05                 # the spec says at least 2 s between request starts; the 0.05 is a margin for clock granularity
MAX_REQUESTS = 20
TIMEOUT = 120
BODY_CAP = 64 * 1024 * 1024

MOF_HOST, BOJ_HOST = "www.mof.go.jp", "www.boj.or.jp"
HOST_ALLOW = frozenset({MOF_HOST, BOJ_HOST})
MOF_BASE = "/policy/international_policy/reference/itn_transactions_in_securities/"
MOF_URL = "https://" + MOF_HOST + MOF_BASE
BOJ_BASE = "/en/mopo/mpmdeci/"
TITLE_STEM = "Purchases and Sales of Foreign Securities by Residents by Types of Investors"
# file key, instrument, the title's bracket
MOF_FILES = (("monthb3", "ltd", "(Long-term debt securities)"), ("monthb1", "all", "(Total)"),
             ("monthb2", "equity_funds", "(Equity and investment fund shares)"), ("monthb4", "std", "(Short-term debt securities)"))
TITLES = {k: TITLE_STEM + b for k, _, b in MOF_FILES}
INSTRUMENTS = ("ltd", "equity_funds", "std", "all")
INSTRUMENT_FILE = {i: k for k, i, _ in MOF_FILES}
FILE_ORDER = tuple(k for k, _, _ in MOF_FILES)
OCT8_FU = dt.date(2026, 10, 8)
# the 8 Oct 2026 vintages as observed by the spec author (spec 2.1): sha256 and bytes
OCT8 = {"monthb3": ("5c70e53f3c95d5c7cdb5041195d386cec46e67860cd142e6f3f825bb72d26cc1", 113821),
        "monthb1": ("f9d96ca4553ff7dbe211fbc2d2667276dc25e027cc8f54906ca8290602d28584", 116077),
        "monthb2": ("eb8570560c63c0ae5721e5cf38b6c005fad1dbc4b3b6ff125c3cb7b4f0dad7f6", 96214),
        "monthb4": ("751df62b428c5632546b37c2219de83e7e67f881f52b63f23b1f7e8fa51036d6", 84610)}

# decision date, path under BOJ_BASE, effective date, action, phrase (under 15 words), sha256 first 16, bytes (spec 2.1)
BOJ_ROWS = (
    ("2013-04-04", "mpr_2013/k130404a", "", "introduces", "Quantitative and Qualitative Monetary Easing", "808a67d9016cf22e", 157105),
    ("2016-01-29", "mpr_2016/k160129a", "", "negative rate", "negative interest rate of minus 0.1 percent", "604f4b9bb33f1318", 30533),
    ("2016-09-21", "mpr_2016/k160921a", "", "introduces", "Yield Curve Control", "c15180b02d80fd86", 44389),
    ("2022-12-20", "mpr_2022/k221220a", "", "10-year band widened", "around plus and minus 0.5 percentage points", "7d97749ccc1e3a3b", 207453),
    ("2023-07-28", "mpr_2023/k230728a", "", "fixed-rate purchases", "at 1.0 percent", "fd3f4c4232ee8b71", 465135),
    ("2023-10-31", "mpr_2023/k231031a", "", "reference for the upper bound", "upper bound of 1.0 percent", "575d056d656bd909", 462610),
    ("2024-03-19", "mpr_2024/k240319a", "2024-03-21", "call rate", "around 0 to 0.1 percent", "e07e26da39f4428b", 474660),
    ("2024-07-31", "mpr_2024/k240731a", "2024-08-01", "call rate", "around 0.25 percent", "bbe8f2154393224c", 482007),
    ("2025-01-24", "mpr_2025/k250124a", "2025-01-27", "call rate", "around 0.5 percent", "6924980a4aea9899", 469888),
    ("2025-12-19", "mpr_2025/k251219a", "2025-12-22", "call rate", "around 0.75 percent", "bcef45990da1895d", 228103),
    ("2026-06-16", "mpr_2026/k260616a", "2026-06-17", "call rate", "around 1.0 percent", "93fe8f756750d1b3", 190988),
    ("2026-09-18", "mpr_2026/k260918a", "2026-09-24", "call rate", "around 1.25 percent", "36d7aa63ff283e25", 208861),
)

# The 17 blocks of the files, in the order MoF prints them: NFKC label (exact match), code, raw cell, header row of the raw cell (spec 2.2).
LABELS = (
    ("(a+b+c+d)", "designated_reporters_total", "（a+b+c+ｄ)", 7),
    ("Public Sector", "public", " Public Sector", 7),
    ("Central Bank (a)", "central_bank", "Central Bank (a)", 8),
    ("General Government (c)", "general_govt", "General Government (ｃ)", 8),
    ("Deposit-taking Corporations (b)", "deposit_taking", "Deposit-taking Corporations (b)", 7),
    ("Banks(Banking Accounts)", "banks_banking", "Banks（Banking Accounts)", 8),
    ("Trust Banks(Banking Accounts)", "trust_banks_banking", "Trust Banks(Banking Accounts）", 8),
    ("Other Sectors (d)", "other_sectors", "Other Sectors （d)", 7),
    ("Other Financial Corporations", "other_financial", "Other Financial Corporations", 8),
    ("Banks and Trust banks(Trust Accounts)", "trust_accounts", "Banks and Trust banks（Trust Accounts）", 8),
    ("Banks(Trust Accounts)", "banks_trust", "Banks（Trust Accounts）", 8),
    ("Trust Banks(Trust Accounts)", "trust_banks_trust", "Trust Banks（Trust Accounts）", 8),
    ("Financial Instruments Firms", "fi_firms", "Financial Instruments Firms", 8),
    ("Life Insurance Companies", "life", "Life Insurance Companies", 8),
    ("Non-Life Insurance Companies", "nonlife", "Non-Life Insurance Companies", 8),
    ("Investment Trust Management Companies", "inv_trust", "Investment Trust Management Companies", 8),
    ("Others", "others", "Others", 8),
)
CODES = tuple(c for _, c, _, _ in LABELS)
LABEL_CODE = {lab: c for lab, c, _, _ in LABELS}
REAL_ORDER = CODES
COMMITTED = ("designated_reporters_total", "banks_banking", "trust_accounts", "life", "nonlife", "inv_trust")
MISSING_PRE2014 = ("central_bank", "general_govt", "banks_trust", "trust_banks_trust")
TOTAL = "designated_reporters_total"
FIELDS = ("acquisition", "disposition", "net")
NCOLS = 54
HDR_ROW = 10                       # 0-based row of "Acquisition / Disposition / Net"; month rows follow it

BREAK_2014 = (2014, 1)
TARGET = (2026, 10)                # the month of the registered forecast
BASE_FIRST, BASE_LAST = (2024, 10), (2026, 9)
REGISTERED = (-2886, -782, 746)    # low, point, high in file units (spec 5); G12 requires it to equal the CALENDAR row
REGISTERED_ON = "2026-10-19"
RECORD_FU = dt.date(2026, 11, 10)  # the only Final Update whose October print is of record
# the 24 base Net cells 2024-10 to 2026-09 (spec 8, C10), life insurers, long-term debt, 8 Oct 2026 vintage
BASE_PINS = (746, -1970, -1964, -2128, -2163, -2501, -762, 5309, -46, -1993, 809, 326, -385, -649, -2543, 402, -6187, -6384, -802, 179,
             -413, -106, -1373, -2886)

REQUIRED = ("These are recorded acquisitions and dispositions, redemptions included. They do not show why any investor acquired or disposed "
            "of bonds, or any effect on prices.")

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
    """A technical refusal at MoF: STOP was written (or already existed); the run ends."""


class LatchedBoj(Latched):
    """A refusal at the Bank of Japan: STOP_BOJ was written (or already existed); only the BoJ part ends."""


class SocketFault(Exception):
    """Timeout, reset or TLS error: the invocation ends without latching."""


class DataError(Exception):
    """A hard check on the data failed."""


# ------------------------------------------------------------------------------------------------------------------------
# small helpers: exact arithmetic and text (R8)
# ------------------------------------------------------------------------------------------------------------------------
def tilde(p):
    home = os.path.expanduser("~")
    return str(p).replace(home, "~") if home and home != "~" else str(p)


def sha256_of(b):
    return hashlib.sha256(b).hexdigest()


def nfkc(s):
    return unicodedata.normalize("NFKC", s).strip()


def fmt_dec(x, nd):
    """Fixed-decimal text of an exact value, rounded half away from zero (R8, G10); never Python's round(); no negative zero."""
    if M("py_round"):
        s = format(round(float(x), nd), ".%df" % nd)
        return s[1:] if s.startswith("-") and float(s) == 0 else s
    q = Fraction(x) * (10 ** nd)
    n, d = abs(q.numerator), q.denominator
    r = (2 * n + d) // (2 * d)                       # floor(|q| + 1/2)
    s = str(r).rjust(nd + 1, "0")
    if nd:
        s = s[:-nd] + "." + s[-nd:]
    return ("-" if q < 0 and r != 0 else "") + s


def fmt_bn(x100m):
    """File units (100 million yen) -> yen billion, one decimal."""
    return fmt_dec(Fraction(x100m) / 10, 1)


def fmt_100m1(x):
    """File units, one decimal (the window statistics of C13)."""
    return fmt_dec(x, 1)


def fmt_pct(frac, nd=2):
    return fmt_dec(Fraction(frac) * 100, nd)


def fmt_exact(x):
    """A value in file units as an integer, or with .5 where it is a half (the registered point is an integer)."""
    x = Fraction(x)
    if x.denominator == 1:
        return str(x.numerator)
    return fmt_dec(x, 1)


def fint(n):
    return "{:,}".format(n).replace("-", "−")        # README text: thousands commas and the true minus sign


def ym_text(ym):
    return "%04d-%02d" % ym


def ym_next(ym, k=1):
    i = ym[0] * 12 + ym[1] - 1 + k
    return (i // 12, i % 12 + 1)


def ym_range(a, b):
    out, c = [], a
    while c <= b:
        out.append(c)
        c = ym_next(c)
    return out


def month_end(ym):
    return dt.date(ym[0] + (ym[1] == 12), ym[1] % 12 + 1, 1) - dt.timedelta(days=1)


def assert_ua(ua=UA):
    if not M("ua_check_off"):
        if chr(64) in ua:
            raise Refused("the identification string contains an address")
        for var in ("SEC_UA", "CLAUDE_CODE_USER_EMAIL"):
            v = os.environ.get(var, "").strip()
            if v and (v in ua or ua in v):
                raise Refused("the identification string contains a configured contact value (not printed)")


assert_ua()


def max_requests_cap():
    return 21 if M("max_requests_21") else MAX_REQUESTS


# ------------------------------------------------------------------------------------------------------------------------
# the request table: four MoF files first, then twelve BoJ statements (R1, R3)
# ------------------------------------------------------------------------------------------------------------------------
def request_table():
    mof = [dict(key=k, kind="mof", host=MOF_HOST, target=MOF_BASE + k + ".csv", file=k + ".csv", arg=k) for k, _, _ in MOF_FILES]
    boj = [dict(key="boj" + d, kind="boj", host=BOJ_HOST, target=BOJ_BASE + p + ".pdf", file="boj_%s.pdf" % d, arg=d)
           for d, p, _, _, _, _, _ in BOJ_ROWS]
    return (boj + mof) if M("boj_first") else (mof + boj)


ALLOWED = frozenset((r["host"], r["target"]) for r in request_table())


def check_url(url):
    """Only the 16 exact requests of the table, over https, on the two allowed hosts. Returns (host, target)."""
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
        raise Refused("that path is not one of the 16 requests of the spec")
    return host, target


def check_cache(cache, root=ROOT, out_dir=None):
    """The cache may be outside the repository, or inside it only where git ignores it (never in the committed output folder)."""
    real = os.path.realpath(os.path.expanduser(cache))
    rroot = os.path.realpath(root)
    if M("cache_check_off"):
        return real
    if real == rroot or real.startswith(rroot + os.sep):
        outd = os.path.realpath(out_dir or os.path.join(root, "data", "jp_life_foreign_bonds"))
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


def refuse_latch_path(path):
    """No writer of this script may touch a latch file: the latch writer (`_latch`) is the only code that creates one."""
    if M("latch_overwrite_ok"):
        return
    if os.path.basename(str(path)).upper() in ("STOP", "STOP_BOJ"):
        raise Refused("a latch file is never written, replaced or removed by a general writer")


# ------------------------------------------------------------------------------------------------------------------------
# parsing a MoF file (also the content test of a fetched body, 2.4)
# ------------------------------------------------------------------------------------------------------------------------
MONTH_NUM = {m: i + 1 for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"))}
FU_RX = re.compile(r"Final Update\s+([A-Z][a-z]+ \d{1,2}, \d{4})")
TOTAL_RX = re.compile(r"(\d{4})(CY|FY)\s*$")


class Parsed:
    """One MoF file: months {(y, m): {code: (acq, disp, net)}}, blank months, total rows {('CY'|'FY', y): {code: (a, d, n)}}."""

    def __init__(self):
        self.title = ""
        self.fu = None
        self.months = {}
        self.blank = []
        self.totals = {}
        self.n_month_rows = 0
        self.jp_disagree = []
        self.codes = ()


def parse_fu_text(s):
    mon, day, year = re.match(r"([A-Z][a-z]+) (\d{1,2}), (\d{4})", s).groups()
    return dt.date(int(year), MONTH_NUM[mon[:3].lower()], int(day))


def find_final_update(rows):
    if M("final_update_col18"):
        m = FU_RX.search(nfkc(rows[1][18])) if len(rows[1]) > 18 else None
        if not m:
            raise DataError("no Final Update date at column 18")
        return parse_fu_text(m.group(1))
    for r in rows[:HDR_ROW + 1]:
        for c in r:
            m = FU_RX.search(nfkc(c))
            if m:
                return parse_fu_text(m.group(1))
    raise DataError("no 'Final Update <Month> <day>, <year>' cell in the header rows")


def match_label(lab):
    if M("substring_labels"):
        for l, code, _, _ in LABELS:
            if l in lab or lab in l:
                return code
        raise DataError("label %r not found" % lab)
    code = LABEL_CODE.get(lab)
    if code is None:
        raise DataError("block label %r is not one of the 17 expected labels" % lab)
    return code


def block_codes(rows):
    """The sector code of each of the 17 blocks, by label: first non-empty cell of header rows 7 and 8 that begins with an ASCII character
    after NFKC and stripping, matched by exact equality (spec 2.2)."""
    if M("fixed_index_life"):
        return list(REAL_ORDER)
    codes = []
    for k in range(17):
        col = 3 + 3 * k
        lab = None
        for ri in (7, 8):
            if col >= len(rows[ri]):
                continue
            s = rows[ri][col].strip() if M("no_nfkc") else nfkc(rows[ri][col])
            if s and ord(s[0]) < 128:
                lab = s
                break
        if lab is None:
            raise DataError("block %d (column %d) has no ASCII label in header rows 7 and 8" % (k + 1, col))
        codes.append(match_label(lab))
    if sorted(codes) != sorted(CODES):
        raise DataError("the 17 blocks do not map one-to-one onto the 17 sectors: %s" % codes)
    return codes


def cell_value(c, blank_zero=False):
    s = nfkc(c)
    if s == "":
        return 0 if blank_zero else None
    if s == "-":
        return 0 if M("dash_as_zero") else None
    s = s.replace(",", "")
    if not re.fullmatch(r"-?\d+", s):
        raise DataError("cell %r is not an integer, a dash or blank" % c)
    return int(s)


def parse_mof(raw, title=None, min_month_rows=1):
    """MoF monthbN.csv (CP932). Header rows are found by text; blocks are mapped by label; the year is carried down from January; the month
    comes from the English column only; '-' and blank are missing; a row with no value at all is an unpublished month; CY/FY rows never enter
    the monthly series. -> Parsed"""
    try:
        text = raw.decode("cp932")
    except UnicodeDecodeError:
        raise DataError("not CP932 text")
    rows = list(csv.reader(io.StringIO(text)))
    if len(rows) <= HDR_ROW + 1:
        raise DataError("too few lines for a MoF file")
    p = Parsed()
    if title is not None and not any(title in nfkc(c) for c in rows[1]):
        raise DataError("line 2 does not carry the expected title %r" % title)
    p.title = " ".join(nfkc(c) for c in rows[1] if c.strip())
    p.fu = find_final_update(rows)
    h = next((i for i, r in enumerate(rows[:20]) if len(r) > 5 and nfkc(r[3]) == "Acquisition"), None)
    if h != HDR_ROW:
        raise DataError("the Acquisition/Disposition/Net row is not 0-based row %d" % HDR_ROW)
    if not any("100 mil Yen" in nfkc(c) for r in rows[:h] for c in r):
        raise DataError("no '100 mil Yen' unit line")
    p.codes = tuple(block_codes(rows))
    year = None
    prev = None
    for r in rows[h + 1:]:
        if not r:
            continue
        c0 = nfkc(r[0])
        tm = TOTAL_RX.search(c0)
        if tm:
            if len(r) != NCOLS:
                raise DataError("total row %r has %d cells" % (c0, len(r)))
            vals = [cell_value(c) for c in r[3:NCOLS]]
            p.totals[(tm.group(2), int(tm.group(1)))] = {code: tuple(vals[3 * k:3 * k + 3]) for k, code in enumerate(p.codes)}
            if M("total_as_month"):
                ym = (int(tm.group(1)), 12 if tm.group(2) == "CY" else 3)
                p.months[ym] = dict(p.totals[(tm.group(2), int(tm.group(1)))])
            continue
        en = nfkc(r[2]).lower() if len(r) > 2 else ""
        if en not in MONTH_NUM:
            continue                                      # notes, blank lines, anything that is not a month row
        if len(r) != NCOLS:
            raise DataError("month row %r has %d cells (54 expected)" % (en, len(r)))
        mi = MONTH_NUM[en]
        jp = re.search(r"\d+", nfkc(r[1]))
        if M("month_from_japanese") and jp:
            mi = int(jp.group(0))
        elif jp and int(jp.group(0)) != mi:
            p.jp_disagree.append((year, en, nfkc(r[1])))
        if re.fullmatch(r"\d{4}", c0):
            year = int(c0)
        elif M("year_not_carried"):
            continue
        if year is None:
            raise DataError("a month row before any year")
        ym = (year, mi)
        if prev is not None and ym != ym_next(prev):
            raise DataError("month sequence broken: %s after %s" % (ym_text(ym), ym_text(prev)))
        prev = ym
        p.n_month_rows += 1
        cells = r[3:NCOLS]
        if all(c.strip() == "" for c in cells) and not M("blank_as_zero"):
            p.blank.append(ym)
            continue
        vals = [cell_value(c, blank_zero=M("blank_as_zero") and all(x.strip() == "" for x in cells)) for c in cells]
        d = {}
        for k, code in enumerate(p.codes):
            a, dd, n = vals[3 * k:3 * k + 3]
            if M("swap_acq_disp"):
                a, dd = dd, a
            d[code] = (a, dd, n)
        p.months[ym] = d
    if p.n_month_rows < min_month_rows:
        raise DataError("only %d month rows parse with 54 cells (need %d)" % (p.n_month_rows, min_month_rows))
    return p


def mof_content_test(raw, key):
    """The content test of a fetched MoF body, exactly spec 2.4: CP932 decodes; line 2 carries the expected English title; a label cell normalises to
    `Life Insurance Companies`; a `Final Update <Month> <day>, <year>` cell; the unit line; at least 250 month rows of 54 cells. The strict parse is
    the build's job, so a quirk in a cell cannot latch a fetch. -> (problem or None, Final Update date or None)"""
    try:
        rows = list(csv.reader(io.StringIO(raw.decode("cp932"))))
    except (UnicodeDecodeError, csv.Error):
        return "not CP932 text", None
    if len(rows) <= HDR_ROW + 1:
        return "too few lines for a MoF file", None
    head = rows[:HDR_ROW + 1]
    if not any(TITLES[key] in nfkc(c) for c in rows[1]):
        return "line 2 does not carry the expected title", None
    if not any(nfkc(c) == "Life Insurance Companies" for r in head for c in r):
        return "no Life Insurance Companies label cell", None
    try:
        fu = find_final_update(rows)
    except DataError as e:
        return str(e), None
    if not any("100 mil Yen" in nfkc(c) for r in head for c in r):
        return "no '100 mil Yen' unit line", None
    n = sum(1 for r in rows[HDR_ROW + 1:] if len(r) == NCOLS and nfkc(r[2]).lower() in MONTH_NUM)
    if n < 250:
        return "only %d month rows have 54 cells (need 250)" % n, None
    return None, fu


def boj_problem(body, sha16):
    if not body.startswith(b"%PDF"):
        return "not a PDF"
    if len(body) < 20000:
        return "under 20,000 bytes"
    if sha256_of(body)[:16] != sha16:
        return "sha256 differs from the recorded first 16 characters"
    return None


# ------------------------------------------------------------------------------------------------------------------------
# the fetch log and fetching: the only network code
# ------------------------------------------------------------------------------------------------------------------------
LOG_COLS = ["utc_time", "host", "path", "status", "bytes", "sha256"]


def read_csv_rows(path):
    """(header, rows) of a csv with comment lines (# ...) skipped; ([], []) if absent."""
    if not os.path.exists(path):
        return [], []
    with open(path, encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh.read().splitlines(True) if not ln.startswith("#")]
    rd = list(csv.reader(io.StringIO("".join(lines))))
    return (rd[0], rd[1:]) if rd else ([], [])


def retrieval_dates(log_rows, host=None):
    return sorted({r[0][:10] for r in log_rows if (host is None or r[1] == host) and r[3] == "200" and r[4]})


CITATION = ('Ministry of Finance Japan, "International Transactions in Securities" (designated reporters, monthly; monthb1-b4.csv), %s, PDL1.0, '
            'retrieved %s. Processed by the Third Derivative project (re-laid out and summed; values unchanged).')


def source_line(log_rows):
    ds = retrieval_dates(log_rows, MOF_HOST)
    return "# source: " + CITATION % (MOF_URL, ", ".join(ds) if ds else "(no logged retrieval)")


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


VINTAGE_RX = re.compile(r"(monthb\d)_(\d{4}-\d{2}-\d{2})_([0-9a-f]{12})\.csv")


def save_vintage(cache, key, body, fu):
    """Save a MoF body as <key>_<Final Update>_<sha first 12>.csv only when its sha256 differs from every cached vintage of that file (2.5).
    -> (outcome, file name)"""
    sha = sha256_of(body)
    os.makedirs(cache, exist_ok=True)
    name = "%s_%s_%s.csv" % (key, fu.isoformat(), sha[:12])
    for f in sorted(os.listdir(cache)):
        m = VINTAGE_RX.fullmatch(f)
        if m and m.group(1) == key:
            with open(os.path.join(cache, f), "rb") as fh:
                if sha256_of(fh.read()) == sha and not M("save_unchanged_vintage"):
                    return "unchanged", f
    refuse_latch_path(name)
    path = os.path.join(cache, name)
    with open(path + ".part", "wb") as fh:
        fh.write(body)
    os.replace(path + ".part", path)
    return "saved", name


class Fetcher:
    """All requests go through here. Injectable opener, clock, sleeper and latch paths make it testable without a network."""

    def __init__(self, cache, out_dir, sleep=MIN_SLEEP, max_requests=MAX_REQUESTS, opener=real_opener, wall=time.time, mono=time.monotonic,
                 sleeper=time.sleep, stop_path=STOP_PATH, stop_boj_path=STOP_BOJ_PATH, now_utc=None, root=ROOT, boj_expect=None):
        if sleep < 2.0 and not M("no_pacing"):
            raise Refused("--sleep must be at least 2 seconds")
        if max_requests > max_requests_cap() or max_requests < 1:
            raise Refused("--max-requests must be between 1 and %d" % MAX_REQUESTS)
        self.out_dir = out_dir
        self.cache = check_cache(cache, root=root, out_dir=out_dir)
        self.sleep, self.max_requests = float(sleep), max_requests
        self.opener, self.wall, self.mono, self.sleeper = opener, wall, mono, sleeper
        self.stop_path, self.stop_boj_path = stop_path, stop_boj_path
        self.now_utc = now_utc or (lambda: dt.datetime.now(dt.timezone.utc))
        self.boj_expect = boj_expect or {"boj" + d: s for d, _, _, _, _, s, _ in BOJ_ROWS}
        self.requests = 0
        self._last_mono = None
        self._last_file = os.path.join(self.cache, ".last_request")
        self.log_path = os.path.join(out_dir, "fetch_log.csv")

    @staticmethod
    def _why(path):
        with open(path, encoding="utf-8") as fh:
            return fh.read().strip().replace("\n", " ")[:200]

    def check_stop(self):
        if os.path.exists(self.stop_path) and not M("stop_ignored"):
            raise Latched("STOP exists at %s (%s); a person must inspect it and delete it" % (tilde(self.stop_path), self._why(self.stop_path)))

    def check_stop_boj(self):
        if os.path.exists(self.stop_boj_path):
            raise LatchedBoj("STOP_BOJ exists at %s (%s); a person must inspect it and delete it" % (tilde(self.stop_boj_path),
                                                                                                     self._why(self.stop_boj_path)))

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
        write_text(self.log_path, render_csv("fetch_log.csv", rows, source_line(rows)))

    def _latch(self, boj, reason):
        """The only code that creates a latch file. It creates it exclusively: an existing latch is never written over."""
        if boj and not M("boj_writes_stop"):
            path = self.stop_boj_path
        else:
            path = self.stop_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        mode = "w" if M("latch_overwrite_ok") else "x"
        try:
            with open(path, mode, encoding="utf-8") as fh:
                fh.write("%s UTC  %s\n" % (self.now_utc().strftime("%Y-%m-%dT%H:%M:%S"), reason))
        except FileExistsError:
            pass
        raise (LatchedBoj if boj else Latched)(reason)

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
                self._latch(False, "socket fault (%s) for %s" % (e, target))
            raise
        return status, body, started

    def _done_today(self, host, target):
        today = self.now_utc().strftime("%Y-%m-%d")
        _, rows = read_csv_rows(self.log_path)
        return any(r[1] == host and r[2] == target and r[3] == "200" and r[4] and r[0][:10] == today for r in rows)

    def fetch_one(self, req):
        """Returns an outcome word; raises Latched / LatchedBoj / SocketFault / MaxRequests / Refused."""
        boj = req["kind"] == "boj"
        path = os.path.join(self.cache, req["file"])
        if boj:
            if os.path.exists(path):
                return "cached"
            self.check_stop_boj()
        else:
            if self._done_today(req["host"], req["target"]) and not M("no_done_today"):
                return "cached"
            self.check_stop()
            if M("stop_boj_blocks_mof"):
                self.check_stop_boj()
        status, body, started = self._get(req["host"], req["target"])
        if status != 200:
            self._log(started, req["host"], req["target"], status, "", "")
            if status // 100 == 3:
                if not M("no_latch_redirect"):
                    self._latch(boj, "HTTP %d (a redirect, not followed) for %s" % (status, req["target"][-60:]))
            elif not M("no_latch_non200"):
                self._latch(boj, "HTTP %d for %s" % (status, req["target"][-60:]))
            return "refused_unlatched"
        fu = None
        if body is None:
            problem = "body larger than the cap"
        elif boj:
            problem = boj_problem(body, self.boj_expect[req["key"]])
        else:
            problem, fu = mof_content_test(body, req["arg"])
        self._log(started, req["host"], req["target"], status, len(body or b""), sha256_of(body or b""))
        if problem:
            if not M("no_latch_bad_body"):
                self._latch(boj, "200 but not the expected file (%s) for %s" % (problem, req["target"][-60:]))
            return "refused_unlatched"
        if boj:
            refuse_latch_path(req["file"])
            os.makedirs(self.cache, exist_ok=True)
            with open(path + ".part", "wb") as fh:
                fh.write(body)
            os.replace(path + ".part", path)
            return "saved"
        outcome, _ = save_vintage(self.cache, req["arg"], body, fu)
        return outcome


def fetch_all(fe, reqs, say=print):
    """Run the request table in order. A MoF latch propagates (the run ends); a BoJ latch ends only the BoJ part. -> (saved, boj_latch)"""
    saved, boj_latch = 0, None
    for req in reqs:
        if req["kind"] == "boj" and boj_latch is not None:
            say("%-26s skipped (BoJ part ended: %s)" % (req["file"], boj_latch))
            continue
        try:
            out = fe.fetch_one(req)
        except LatchedBoj as e:
            boj_latch = str(e)[:120]
            say("%-26s BoJ LATCH: %s" % (req["file"], boj_latch))
            continue
        saved += out == "saved"
        say("%-26s %s" % (req["file"], out))
    return saved, boj_latch


def write_text(path, text):
    refuse_latch_path(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


# ------------------------------------------------------------------------------------------------------------------------
# writing outputs: exact column allowlists, source lines, no causal wording, no leaks (G14, G15, G17)
# ------------------------------------------------------------------------------------------------------------------------
MONTHLY_COLS = ["month", "instrument", "sector", "acquisition_100m_yen", "disposal_100m_yen", "net_100m_yen", "basis"]
ANNUAL_COLS = ["period_type", "period", "basis", "instrument", "sector", "months", "acquisition_100m_yen", "disposal_100m_yen", "net_100m_yen",
               "file_total_net_100m_yen", "diff_100m_yen"]
BOJ_COLS = ["decision_date", "effective_date", "month", "action", "phrase", "url", "sha256"]
QUESTION_COLS = ["run_label", "question", "window", "instrument", "sector", "statistic", "value", "unit", "denominator", "notable"]
FORECAST_COLS = ["registered_on", "target_month", "vintage_final_update", "vintage_sha256", "point_100m_yen", "low_100m_yen", "high_100m_yen",
                 "print_100m_yen", "status", "of_record", "band_recomputed_low", "band_recomputed_point", "band_recomputed_high", "note"]
VINTAGE_COLS = ["file", "final_update", "retrieved_utc", "bytes", "sha256", "months_published", "last_month"]
REVISION_COLS = ["file", "vintage_from", "vintage_to", "row_label", "sector", "field", "old_value", "new_value", "kind"]
CHECK_COLS = ["check_id", "description", "expected", "observed", "status"]
PIN_COLS = ["source", "series", "pin_date", "value", "unit"]

# The allowlists exactly as the spec prints them (section 6), typed separately from the lists above so that the selftest compares two
# independent copies. G14 fails if ALLOW or a written header drifts from these.
SPEC_ALLOW = {
    "monthly.csv": "month, instrument, sector, acquisition_100m_yen, disposal_100m_yen, net_100m_yen, basis",
    "annual.csv": "period_type, period, basis, instrument, sector, months, acquisition_100m_yen, disposal_100m_yen, net_100m_yen, file_total_net_100m_yen, diff_100m_yen",
    "boj_dates.csv": "decision_date, effective_date, month, action, phrase, url, sha256",
    "questions.csv": "run_label, question, window, instrument, sector, statistic, value, unit, denominator, notable",
    "forecast_score.csv": "registered_on, target_month, vintage_final_update, vintage_sha256, point_100m_yen, low_100m_yen, high_100m_yen, print_100m_yen, status, of_record, band_recomputed_low, band_recomputed_point, band_recomputed_high, note",
    "vintages.csv": "file, final_update, retrieved_utc, bytes, sha256, months_published, last_month",
    "revisions.csv": "file, vintage_from, vintage_to, row_label, sector, field, old_value, new_value, kind",
    "checks.csv": "check_id, description, expected, observed, status",
    "pins.csv": "source, series, pin_date, value, unit",
    "fetch_log.csv": "utc_time, host, path, status, bytes, sha256",
}
ALLOW = {"monthly.csv": MONTHLY_COLS, "annual.csv": ANNUAL_COLS, "boj_dates.csv": BOJ_COLS, "questions.csv": QUESTION_COLS,
         "forecast_score.csv": FORECAST_COLS, "vintages.csv": VINTAGE_COLS, "revisions.csv": REVISION_COLS, "checks.csv": CHECK_COLS,
         "pins.csv": PIN_COLS, "fetch_log.csv": LOG_COLS}
COMMITTED_NAMES = tuple(sorted(list(ALLOW) + ["README.md", "SOURCES.md"]))

# G15: fx_rate_gap.CAUSAL_RX as it stands, extended as the spec lists, plus a separate ban on the words for a sale
CAUSAL_BASE = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention)\b", re.I)
CAUSAL_EXT = re.compile(r"\b(because|due\s+to|in\s+response\s+to|led\s+to|prompted|pushed|as\s+a\s+result\s+of|reaction|reflecting|amid|owing\s+to|"
                        r"thanks\s+to|on\s+the\s+back\s+of|weighed)\b|\bas\b.{0,40}\b(rose|fell|rising|falling)\b", re.I)
SOLD_RX = re.compile(r"\bsold\b|\bnet\s+sales\b", re.I)


def text_hits(text):
    """Causal wording and the words for a sale in generated text; the required sentence is the one exemption."""
    if M("scan_off"):
        return []
    t = text.replace(REQUIRED, "")
    hits = {m.group(0).lower() for m in CAUSAL_BASE.finditer(t)}
    if not M("rx_base_only"):
        hits |= {m.group(0).lower() for m in CAUSAL_EXT.finditer(t)}
    if not M("no_sold_ban"):
        hits |= {m.group(0).lower() for m in SOLD_RX.finditer(t)}
    return sorted(hits)


def allowlist(name):
    cols = list(ALLOW[name])
    if M("allow_drift") and name == "questions.csv":
        cols[cols.index("unit")] = "units"
    if M("annual_without_basis") and name == "annual.csv":
        cols.remove("basis")
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


def guard_text(name, text):
    hits = text_hits(text)
    if hits:
        raise DataError("%s: wording %s" % (name, hits))
    home = os.path.expanduser("~")
    if home != "~" and home in text:
        raise DataError("%s: an absolute home path would be published" % name)
    for bad in ("/Users/", "/private/tmp", chr(64)):
        if bad in text:
            raise DataError("%s: %r would be published" % (name, bad))


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
        w.writerow(["" if c is None else str(c) for c in r])
    text = out.getvalue()
    if not text.startswith("# source:"):
        raise DataError("%s: the first line is not a `# source:` line" % name)
    guard_text(name, text)
    return text


def committed_header(text):
    """The header of a committed CSV is the first line that does not start with '#'."""
    lines = text.splitlines()
    if M("header_from_source_line"):
        return lines[0] if lines else ""
    return next((ln for ln in lines if not ln.startswith("#")), "")


def commit_guard(folder):
    """G17: what the committed folder may hold. -> list of problems (empty if clean)."""
    problems = []
    for f in sorted(os.listdir(folder)):
        if f == ".DS_Store":
            continue
        p = os.path.join(folder, f)
        if os.path.isdir(p):
            problems.append("directory %s" % f)
            continue
        if f not in COMMITTED_NAMES and not M("no_name_check"):
            problems.append("%s is not one of the 12 committed names" % f)
        with open(p, "rb") as fh:
            data = fh.read()
        if (data.startswith(b"%PDF") or f.lower().endswith(".pdf")) and not M("no_pdf_check"):
            problems.append("%s is a PDF" % f)
        text = data.decode("utf-8", "replace")
        if "/Users/" in text and not M("no_path_check"):
            problems.append("%s contains /Users/" % f)
        if "/private/tmp" in text and not M("no_private_check"):
            problems.append("%s contains /private/tmp" % f)
        if chr(64) in text and not M("no_at_check"):
            problems.append("%s contains an at sign" % f)
        if f.endswith(".csv"):
            lines = text.splitlines()
            if len(lines) > 1 and TITLE_STEM in lines[1] and not M("no_title_check"):
                problems.append("%s: its second line is a MoF title (a raw file)" % f)
            if f in SPEC_ALLOW and committed_header(text) != SPEC_ALLOW[f].replace(", ", ","):
                problems.append("%s: header is not its exact allowlist" % f)
    return problems


# G16: the source scan. Latch files are created by `_latch` and by nothing else; no call that removes, renames, replaces or writes may name one.
DESTRUCTIVE = {"remove", "unlink", "rename", "renames", "replace", "rmdir", "rmtree", "move", "truncate", "write_text", "write_bytes", "copy", "copyfile",
               "copy2", "copytree", "symlink", "link"}
TEST_FUNC = re.compile(r"^(t_|x_|fx_|synth|selftest|run_test|mk_|plant)")


def latch_scan(source):
    """-> list of (line, text) for every destructive call or write-mode open() that names a latch file outside the latch writer."""
    if M("latch_scan_blind"):
        return []
    tree = ast.parse(source)
    found = []

    def visit(node, func, exempt):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func = node.name
            exempt = exempt or bool(TEST_FUNC.match(node.name))
        if isinstance(node, ast.Call):
            f = node.func
            name = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
            write_open = False
            if name == "open":
                mode = None
                if len(node.args) > 1:
                    mode = node.args[1]
                for kw in node.keywords:
                    if kw.arg == "mode":
                        mode = kw.value
                write_open = mode is not None and not (isinstance(mode, ast.Constant) and isinstance(mode.value, str)
                                                       and not set(mode.value) & set("wax+"))
            if (name in DESTRUCTIVE or write_open) and not exempt:
                txt = ast.unparse(node)
                if "stop" in txt.lower() and not (func == "_latch" and name == "open"):
                    found.append((node.lineno, txt[:100]))
        for ch in ast.iter_child_nodes(node):
            visit(ch, func, exempt)
    visit(tree, None, False)
    return found


def own_source():
    with open(os.path.abspath(__file__), encoding="utf-8") as fh:
        src = fh.read()
    if M("latch_delete_code"):
        src += "\n\ndef _evil():\n    os.remove(STOP_PATH)\n"
    return src


# ------------------------------------------------------------------------------------------------------------------------
# the cache: every vintage of the four MoF files
# ------------------------------------------------------------------------------------------------------------------------
class Vint:
    def __init__(self, key, name, sha, nbytes, parsed, retrieved=""):
        self.key, self.name, self.sha, self.nbytes, self.parsed, self.retrieved = key, name, sha, nbytes, parsed, retrieved
        self.fu = parsed.fu

    @property
    def label(self):
        return "%s_%s" % (self.fu.isoformat(), self.sha[:12])

    @property
    def months(self):
        return self.parsed.months


def first_retrieved(log_rows, key, sha):
    for r in log_rows:
        if r[1] == MOF_HOST and r[2].endswith("/" + key + ".csv") and r[3] == "200" and r[5] == sha:
            return r[0]
    return ""


def load_cache(cache, log_rows, min_month_rows=250):
    """{file key: [Vint, oldest .. newest by (Final Update, retrieval time, sha)]}. The file name must agree with the content."""
    if not os.path.isdir(cache):
        raise DataError("no cache folder: run `fetch` first")
    out = {k: [] for k in FILE_ORDER}
    for f in sorted(os.listdir(cache)):
        m = VINTAGE_RX.fullmatch(f)
        if not m:
            continue
        with open(os.path.join(cache, f), "rb") as fh:
            raw = fh.read()
        sha = sha256_of(raw)
        if sha[:12] != m.group(3):
            raise DataError("%s: the name does not match the content's sha256" % f)
        p = parse_mof(raw, title=TITLES[m.group(1)], min_month_rows=min_month_rows)
        if p.fu.isoformat() != m.group(2):
            raise DataError("%s: the name does not match the file's own Final Update date" % f)
        out[m.group(1)].append(Vint(m.group(1), f, sha, len(raw), p, first_retrieved(log_rows, m.group(1), sha)))
    for k in FILE_ORDER:
        if not out[k]:
            raise DataError("no cached vintage of %s: run `fetch` first" % k)
        out[k].sort(key=lambda v: (v.fu, v.retrieved, v.sha))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# validation (spec 3.2): sign identity, additivity within and across files, annual sums
# ------------------------------------------------------------------------------------------------------------------------
SIGN_TOL_POST, SIGN_TOL_PRE = 1, 4
WITHIN_TOL = 3
CROSS_TOL_ALL, CROSS_TOL_COMMITTED = 4, 2
ANNUAL_TOL = 12
WITHIN_EQ = (("other_financial", ("trust_accounts", "fi_firms", "life", "nonlife", "inv_trust"), None),
             ("designated_reporters_total", ("public", "deposit_taking", "other_sectors"), None),
             ("trust_accounts", ("banks_trust", "trust_banks_trust"), BREAK_2014))


def sign_check(parsed):
    """Net = Acquisition - Disposition in every non-missing cell: within 1 from 2014, within 4 before (2.3)."""
    res = {"post": dict(cells=0, over1=0, max=0), "pre": dict(cells=0, over1=0, max=0)}
    for ym, d in parsed.months.items():
        b = res["post" if ym >= BREAK_2014 else "pre"]
        for code, (a, dd, n) in d.items():
            if a is None or dd is None or n is None:
                continue
            gap = abs(n - ((dd - a) if M("sign_inverted") else (a - dd)))
            b["cells"] += 1
            b["over1"] += gap > 1
            b["max"] = max(b["max"], gap)
    return res


def sign_violations(res):
    if M("sign_check_off"):
        return []
    v = []
    if res["post"]["max"] > SIGN_TOL_POST:
        v.append("post-2014 gap %d > %d" % (res["post"]["max"], SIGN_TOL_POST))
    if res["pre"]["max"] > SIGN_TOL_PRE:
        v.append("pre-2014 gap %d > %d" % (res["pre"]["max"], SIGN_TOL_PRE))
    return v


def within_additivity(parsed):
    """Net column: the parents against their parts. -> ({parent: max gap}, violations)"""
    mx = {lhs: 0 for lhs, _, _ in WITHIN_EQ}
    tol = 10 ** 9 if M("within_off") else WITHIN_TOL
    viol = []
    for ym in sorted(parsed.months):
        d = parsed.months[ym]
        for lhs, parts, since in WITHIN_EQ:
            if since is not None and ym < since:
                continue
            vals = [d[c][2] for c in (lhs,) + parts]
            if any(v is None for v in vals):
                continue
            gap = abs(vals[0] - sum(vals[1:]))
            mx[lhs] = max(mx[lhs], gap)
            if gap > tol:
                viol.append((lhs, ym_text(ym), gap))
    return mx, viol


def cross_tol(code):
    if code in COMMITTED:
        return 4 if M("cross_tol_loose_committed") else CROSS_TOL_COMMITTED
    return 5 if M("cross_tol_loose_noncommitted") else CROSS_TOL_ALL


def cross_additivity(parsed_by_key):
    """b1 = b2 + b3 + b4 for every sector, field and month. -> dict(max_all, max_committed, max_net, worst=[...], violations=[...], cells)"""
    p1, p2, p3, p4 = (parsed_by_key[k] for k in ("monthb1", "monthb2", "monthb3", "monthb4"))
    months = sorted(set(p1.months) & set(p2.months) & set(p3.months) & set(p4.months))
    res = dict(max_all=0, max_committed=0, max_net=0, worst=[], violations=[], cells=0)
    for ym in months:
        for code in CODES:
            for fi, fname in enumerate(FIELDS):
                vals = [p.months[ym][code][fi] for p in (p1, p2, p3, p4)]
                if any(v is None for v in vals):
                    continue
                gap = abs(vals[0] - (vals[1] + vals[2] + vals[3]))
                res["cells"] += 1
                if gap > res["max_all"]:
                    res["max_all"], res["worst"] = gap, []
                if gap == res["max_all"] and gap > 0:
                    res["worst"].append((code, fname, ym_text(ym), vals))
                if code in COMMITTED:
                    res["max_committed"] = max(res["max_committed"], gap)
                if fname == "net":
                    res["max_net"] = max(res["max_net"], gap)
                if gap > cross_tol(code):
                    res["violations"].append((code, fname, ym_text(ym), gap))
    return res


def cross_status(res, fus):
    """PASS / WARN / FAIL for the cross-file check: the four files are compared only when their Final Update dates are equal."""
    if len(set(fus)) != 1:
        return "FAIL" if M("fu_mismatch_fail") else "WARN"
    return "FAIL" if res["violations"] else "PASS"


def period_months(kind, y):
    if kind == "CY" or M("fy_as_calendar"):
        return [(y, m) for m in range(1, 13)]
    start = (y + 1, 4) if M("fy_label_end_year") else (y, 4)
    return ym_range(start, ym_next(start, 11))


def annual_check(parsed):
    """The 12 months against the file's own CY and FY cells, all sectors and fields. -> dict"""
    tol = 99 if M("annual_gap_passes") else ANNUAL_TOL
    res = dict(max_cy=0, max_fy=0, net_cy=0, net_fy=0, worst=[], violations=[], periods=0)
    for (kind, y), tot in sorted(parsed.totals.items()):
        ms = period_months(kind, y)
        if not all(m in parsed.months for m in ms):
            continue
        res["periods"] += 1
        for code in CODES:
            for fi in range(3):
                cell = tot[code][fi]
                vals = [parsed.months[m][code][fi] for m in ms]
                if cell is None or any(v is None for v in vals):
                    continue
                gap = abs(sum(vals) - cell)
                k = "max_cy" if kind == "CY" else "max_fy"
                if gap > res[k]:
                    res[k] = gap
                    res["worst"] = [w for w in res["worst"] if w[0] != kind] + [(kind, code, FIELDS[fi], y, gap)]
                if fi == 2:
                    nk = "net_cy" if kind == "CY" else "net_fy"
                    res[nk] = max(res[nk], gap)
                if gap > tol:
                    res["violations"].append((kind, y, code, FIELDS[fi], gap))
    return res


def missing_pattern(parsed):
    """C07: '-' only where the spec says, and nowhere else. -> dict(dash=, other=, pre_published=)"""
    r = dict(dash=0, other=0, pre_published=0)
    for ym, d in parsed.months.items():
        for code, t in d.items():
            for v in t:
                pre_missing = ym < BREAK_2014 and code in MISSING_PRE2014
                if v is None:
                    r["dash" if pre_missing else "other"] += 1
                elif pre_missing:
                    r["pre_published"] += 1
    return r


# ------------------------------------------------------------------------------------------------------------------------
# tables: monthly, annual (with year-to-date), BoJ, vintages, revisions
# ------------------------------------------------------------------------------------------------------------------------
def basis_of(ym):
    return "old_to_2013" if ym < BREAK_2014 else "new_from_2014"


def annual_basis(kind, y):
    if y == 2007:
        return "mixed_2007"
    if kind == "FY" and y == 2013:
        return "new_from_2014" if M("basis_fy2013_wrong") else "mixed_2013_2014"
    if kind == "CY":
        return "old_to_2013" if y <= 2013 else "new_from_2014"
    return "old_to_2013" if y <= 2012 else "new_from_2014"


def itext(v):
    return "" if v is None else str(v)


def monthly_rows(latest):
    """Six sectors x four instruments x every published month of the latest vintage (spec 3.3)."""
    rows = []
    for ii, inst in enumerate(INSTRUMENTS):
        p = latest[INSTRUMENT_FILE[inst]].parsed
        for ym in sorted(p.months):
            for si, code in enumerate(COMMITTED):
                a, d, n = p.months[ym][code]
                rows.append(((ym, ii, si), [ym_text(ym), inst, code, itext(a), itext(d), itext(n), basis_of(ym)]))
    rows.sort(key=lambda r: r[0])
    return [r for _, r in rows]


def ytd_periods(L):
    """Year-to-date periods for the latest published month L (spec 3.4). -> [(type, [months])]"""
    y, m = L
    out = []
    if m != 12:
        out.append(("CY_YTD", [(y, k) for k in range(1, m + 1)]))
    if m != 3:
        start = (y if (m >= 4 or M("fy_ytd_wrong_start")) else y - 1, 4)
        out.append(("FY_YTD", ym_range(start, L)))
    return out


def annual_rows(latest):
    rows = []
    for inst in INSTRUMENTS:
        p = latest[INSTRUMENT_FILE[inst]].parsed
        if not p.months:
            continue
        for (kind, y), tot in sorted(p.totals.items(), key=lambda kv: (kv[0][0], kv[0][1])):
            ms = period_months(kind, y)
            if not all(m in p.months for m in ms):
                continue
            for code in COMMITTED:
                v = [p.months[m][code] for m in ms]
                a, d, n = (sum(t[i] for t in v) for i in range(3))
                f = tot[code][2]
                rows.append(((0 if kind == "CY" else 1, y, INSTRUMENTS.index(inst), COMMITTED.index(code)),
                             [kind, str(y), annual_basis(kind, y), inst, code, len(ms), a, d, n, itext(f), "" if f is None else n - f]))
        L = max(p.months)
        for kind, ms in ytd_periods(L):
            for code in COMMITTED:
                v = [p.months[m][code] for m in ms]
                a, d, n = (sum(t[i] for t in v) for i in range(3))
                basis = "old_to_2013" if ms[0] < BREAK_2014 else "new_from_2014"
                rows.append(((2 if kind == "CY_YTD" else 3, ms[-1][0], INSTRUMENTS.index(inst), COMMITTED.index(code)),
                             [kind, "%s..%s" % (ym_text(ms[0]), ym_text(ms[-1])), basis, inst, code, len(ms), a, d, n, "", ""]))
    rows.sort(key=lambda r: r[0])
    return [r for _, r in rows]


def boj_rows(cache):
    rows = []
    for d, p, eff, action, phrase, sha16, nbytes in BOJ_ROWS:
        fp = os.path.join(cache, "boj_%s.pdf" % d) if cache else ""
        sha = ""
        if fp and os.path.exists(fp):
            with open(fp, "rb") as fh:
                sha = sha256_of(fh.read())
        rows.append([d, eff, d[:7], action, phrase, "https://" + BOJ_HOST + BOJ_BASE + p + ".pdf", sha])
    return rows


def vintage_rows(vints):
    rows = []
    for k in FILE_ORDER:
        for v in vints[k]:
            p = v.parsed
            rows.append([k, v.fu.isoformat(), v.retrieved, v.nbytes, v.sha, len(p.months), ym_text(max(p.months)) if p.months else ""])
    return rows


def vintage_diff(key, old, new):
    """Cell-by-cell differences between two consecutive vintages of one file, over month and total rows, for the six committed sectors only."""
    codes = CODES if M("revisions_all_sectors") else COMMITTED
    rows = []

    def emit(label, code, fi, ov, nv):
        if ov == nv:
            return
        if ov is None:
            kind = "revised" if M("blank_to_number_revised") else "new"
        elif nv is None:
            kind = "removed"
        else:
            kind = "revised"
        rows.append([key, old.label, new.label, label, code, FIELDS[fi], itext(ov), itext(nv), kind])
    for ym in sorted(set(old.months) | set(new.months)):
        for code in codes:
            o, n = old.months.get(ym, {}).get(code), new.months.get(ym, {}).get(code)
            for fi in range(3):
                emit(ym_text(ym), code, fi, o[fi] if o else None, n[fi] if n else None)
    if not M("revisions_skip_totals"):
        for tk in sorted(set(old.parsed.totals) | set(new.parsed.totals), key=lambda t: (t[0], t[1])):
            for code in codes:
                o, n = old.parsed.totals.get(tk, {}).get(code), new.parsed.totals.get(tk, {}).get(code)
                for fi in range(3):
                    emit("%d%s" % (tk[1], tk[0]), code, fi, o[fi] if o else None, n[fi] if n else None)
    return rows


def revision_rows(vints):
    rows = []
    for k in FILE_ORDER:
        vs = vints[k]
        for a, b in zip(vs, vs[1:]):
            rows += vintage_diff(k, a, b)
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# the descriptive questions (spec 4), exact rational arithmetic throughout
# ------------------------------------------------------------------------------------------------------------------------
def window_defs(L):
    w0_start = (2013, 1) if M("pre2014_in_window") else (2014, 1)
    w2_start = (2024, 4) if M("w2_from_april") else (2024, 3)
    return [("W0", w0_start, (2018, 12)), ("W1", (2019, 1), (2023, 12)), ("W2", w2_start, L), ("W2b", (2024, 4), L)]


def window_months(parsed, start, end):
    """Published months only: an unpublished (blank) month never enters a window."""
    avail = set(parsed.months)
    if M("blank_counted"):
        avail |= set(parsed.blank)
        end = max(avail)
    return [ym for ym in sorted(avail) if start <= ym <= end]


def triple(parsed, ym, code):
    if ym in parsed.months:
        t = parsed.months[ym][code]
    elif M("blank_counted") and ym in parsed.blank:
        t = (0, 0, 0)
    else:
        raise DataError("month %s is not published" % ym_text(ym))
    if any(v is None for v in t):
        raise DataError("%s %s has a missing cell inside a window" % (code, ym_text(ym)))
    return t


def median_of(vals):
    s = sorted(vals)
    n = len(s)
    if n == 0:
        raise DataError("median of nothing")
    return Fraction(s[n // 2]) if n % 2 else Fraction(s[n // 2 - 1] + s[n // 2], 2)


def win_stats(parsed, code, start, end):
    ms = window_months(parsed, start, end)
    if not ms:
        raise DataError("empty window %s..%s" % (ym_text(start), ym_text(end)))
    ts = [triple(parsed, ym, code) for ym in ms]
    n = len(ms)
    acq, disp, net = [t[0] for t in ts], [t[1] for t in ts], [t[2] for t in ts]
    neg = sum(1 for x in net if x < 0)
    return dict(ms=ms, n=n, sum_acq=sum(acq), sum_disp=sum(disp), sum_net=sum(net), mean_net=Fraction(sum(net), n), median_net=median_of(net),
                n_neg=neg, share_neg=Fraction(neg, n), mean_acq=Fraction(sum(acq), n), mean_disp=Fraction(sum(disp), n))


def net_ratio(life_net, total_net):
    """Life net over the total's net: reported only when both nets have the same sign and |ratio| <= 1 (Q3)."""
    if total_net == 0:
        return "exceeds_total" if life_net != 0 else Fraction(0)
    r = Fraction(life_net, total_net)
    if r < 0 and not M("share_negative"):
        return "opposite_sign"
    if r > 1 and not M("share_above_one"):
        return "exceeds_total"
    return r


def share_block(sums):
    """Q3 for one window. sums = {code: (sum_acq, sum_disp, sum_net)}. -> [(sector, statistic, value text, unit, denominator)]"""
    den = "other_financial" if M("denominator_other_financial") else TOTAL
    la, ld, ln = sums["life"]
    ta, td, tn = sums[den]
    out = []
    label = "" if M("share_unlabelled") else "share of reported gross contracts (dealer-inclusive), over "

    def share(a, b):
        return fmt_pct(Fraction(a, b)) if b else "n/a"
    out.append(("life", "share_gross_acquisitions", share(la, ta), "percent", "%s%s acquisitions, window sum %s yen billion" % (label, den, fmt_bn(ta))))
    out.append(("life", "share_gross_dispositions", share(ld, td), "percent", "%s%s dispositions, window sum %s yen billion" % (label, den, fmt_bn(td))))
    if not M("dealer_share_missing"):
        fa, fd, _ = sums["fi_firms"]
        out.append(("fi_firms", "share_gross_acquisitions", share(fa, ta), "percent", "%s%s acquisitions, window sum %s yen billion" % (label, den, fmt_bn(ta))))
        out.append(("fi_firms", "share_gross_dispositions", share(fd, td), "percent", "%s%s dispositions, window sum %s yen billion" % (label, den, fmt_bn(td))))
    out.append(("life", "sum_net", fmt_bn(ln), "¥ billion", "window sum of the Net cells"))
    out.append((den, "sum_net", fmt_bn(tn), "¥ billion", "window sum of the Net cells"))
    r = net_ratio(ln, tn)
    out.append(("life", "net_ratio_to_total", r if isinstance(r, str) else fmt_dec(r, 2), "ratio",
                "life net over %s net, window sums; a ratio only when both nets have the same sign and the ratio is at most 1" % den))
    return out


def rolling12(nets):
    """nets: [(ym, net)] in consecutive months from the first month. -> [(ym, rolling 12-month sum)] from the 12th month."""
    out = []
    for i in range(11, len(nets)):
        out.append((nets[i][0], sum(v for _, v in nets[i - 11:i + 1])))
    return out


def sign_changes(roll):
    """Months where the sign of the rolling sum changes (a zero keeps the previous sign). -> [(ym, 'to_negative'|'to_positive', value)]"""
    out, prev = [], 0
    for ym, v in roll:
        s = (v > 0) - (v < 0)
        if s != 0:
            if prev != 0 and s != prev:
                out.append((ym, "to_negative" if s < 0 else "to_positive", v))
            prev = s
    return out


class Q:
    """Rows of questions.csv and the numbers the checks and the printout use."""

    def __init__(self, run_label):
        self.run_label, self.rows, self.ws, self.sums, self.q = run_label, [], {}, {}, {}

    def add(self, question, window, instrument, sector, statistic, value, unit, denominator, notable=""):
        self.rows.append([self.run_label, question, window, instrument, sector, statistic, value, unit, denominator, notable])


QORDER = ("life", "nonlife", "banks_banking", "trust_accounts", "inv_trust", TOTAL)


def build_questions(p3, p2, L, run_label):
    q = Q(run_label)
    wd = window_defs(L)
    for wname, s, e in wd:
        for code in CODES:
            if code in COMMITTED or code in ("fi_firms", "other_financial"):
                q.ws[(code, wname)] = win_stats(p3, code, s, e)
        q.sums[wname] = {code: (q.ws[(code, wname)]["sum_acq"], q.ws[(code, wname)]["sum_disp"], q.ws[(code, wname)]["sum_net"])
                         for code in CODES if (code, wname) in q.ws}
    q.windows = wd
    life1, life2 = q.ws[("life", "W1")], q.ws[("life", "W2")]
    q1_flag = life2["mean_net"] < life1["mean_net"]
    q.q["q1_flag"] = q1_flag
    for wname, s, e in wd:
        for code in QORDER:
            w = q.ws[(code, wname)]
            span = "%d months %s..%s" % (w["n"], ym_text(w["ms"][0]), ym_text(w["ms"][-1]))
            question = "Q1" if code == "life" else ("Q3" if code == TOTAL else "Q4")
            nb = ""
            if wname == "W2" and code == "life":
                nb = "yes" if q1_flag else "no"
            if wname == "W2" and question == "Q4":
                opp = (w["mean_net"] > 0) != (life2["mean_net"] > 0) and w["mean_net"] != 0
                nb = "yes" if opp else "no"
                q.q.setdefault("opposite", []).append(code) if opp else None
            q.add(question, wname, "ltd", code, "months", str(w["n"]), "months", "the window", "")
            q.add(question, wname, "ltd", code, "sum_net", fmt_bn(w["sum_net"]), "¥ billion", span)
            q.add(question, wname, "ltd", code, "mean_net", fmt_bn(w["mean_net"]), "¥ billion", span, nb)
            q.add(question, wname, "ltd", code, "median_net", fmt_bn(w["median_net"]), "¥ billion", span)
            q.add(question, wname, "ltd", code, "months_net_disposition", str(w["n_neg"]), "months", span)
            q.add(question, wname, "ltd", code, "share_months_net_disposition", fmt_pct(w["share_neg"]), "percent", span)
            q.add(question, wname, "ltd", code, "mean_acquisitions", fmt_bn(w["mean_acq"]), "¥ billion", span)
            q.add(question, wname, "ltd", code, "mean_dispositions", fmt_bn(w["mean_disp"]), "¥ billion", span)
    q.add("Q1", "W1", "ltd", "life", "window_contains", "2022 and 2023", "text", "the window")
    q.add("Q1", "W2", "ltd", "life", "note_disposition", "dispositions include redemptions of overseas government bonds (MoF FAQ A5)", "text",
          "the window")
    # Q2: the change in mean net from W1 to W2 is the change in mean acquisitions less the change in mean dispositions
    da, dd, dn = life2["mean_acq"] - life1["mean_acq"], life2["mean_disp"] - life1["mean_disp"], life2["mean_net"] - life1["mean_net"]
    q.q.update(d_acq=da, d_disp=dd, d_net=dn)
    larger = "acquisitions" if abs(da) > abs(dd) else "dispositions"
    den2 = "W1 (%d months) to W2 (%d months), life insurers" % (life1["n"], life2["n"])
    q.add("Q2", "W1_to_W2", "ltd", "life", "delta_mean_acquisitions", fmt_bn(da), "¥ billion", den2)
    q.add("Q2", "W1_to_W2", "ltd", "life", "delta_mean_dispositions", fmt_bn(dd), "¥ billion", den2)
    q.add("Q2", "W1_to_W2", "ltd", "life", "delta_mean_net", fmt_bn(dn), "¥ billion", den2, "larger term: " + larger)
    # Q3: shares of reported gross contracts (dealer-inclusive)
    q.q["shares"] = {}
    for wname, _, _ in wd:
        blk = share_block(q.sums[wname])
        q.q["shares"][wname] = blk
        for sector, stat, val, unit, den in blk:
            q.add("Q3", wname, "ltd", sector, stat, val, unit, den)
    # Q5: the sign of the rolling 12-month net
    nets = [(ym, triple(p3, ym, "life")[2]) for ym in window_months(p3, (2014, 1), L)]
    roll = rolling12(nets)
    chg = sign_changes(roll)
    den5 = "rolling 12-month sum of life insurers' Net cells, from %s to %s (%d months)" % (ym_text(roll[0][0]), ym_text(roll[-1][0]), len(roll))
    q.q.update(roll=roll, chg=chg)
    q.add("Q5", "rolling12", "ltd", "life", "sign_changes", str(len(chg)), "count", den5)
    for i, (ym, direction, v) in enumerate(chg, 1):
        q.add("Q5", "rolling12", "ltd", "life", "sign_change_%d_month" % i, ym_text(ym), "month", den5)
        q.add("Q5", "rolling12", "ltd", "life", "sign_change_%d_direction" % i, direction, "text", den5)
        q.add("Q5", "rolling12", "ltd", "life", "sign_change_%d_value" % i, fmt_bn(v), "¥ billion", den5)
    to_neg = [c for c in chg if c[1] == "to_negative"]
    last_neg = to_neg[-1] if to_neg else None
    if last_neg:
        stayed = all(v < 0 for ym, v in roll if ym >= last_neg[0])
        q.add("Q5", "rolling12", "ltd", "life", "latest_change_to_negative_month", ym_text(last_neg[0]), "month", den5)
        q.add("Q5", "rolling12", "ltd", "life", "negative_through_latest_month", "yes" if stayed else "no", "text", den5)
        q.q["stayed"] = stayed
    mn = min(roll, key=lambda t: (t[1], t[0]))
    q.q["min"] = mn
    q.q["last_roll"] = roll[-1]
    q.add("Q5", "rolling12", "ltd", "life", "minimum_month", ym_text(mn[0]), "month", den5)
    q.add("Q5", "rolling12", "ltd", "life", "minimum_value", fmt_bn(mn[1]), "¥ billion", den5)
    q.add("Q5", "rolling12", "ltd", "life", "latest_value", fmt_bn(roll[-1][1]), "¥ billion", den5)
    # Q6: life insurers' fund-share flows beside long-term debt, no offset reading
    q.q["q6"] = {}
    for wname in ("W1", "W2"):
        s, e = next((a, b) for n, a, b in wd if n == wname)
        w2 = win_stats(p2, "life", s, e)
        q.q["q6"][wname] = w2["sum_net"]
        q.add("Q6", wname, "equity_funds", "life", "sum_net", fmt_bn(w2["sum_net"]), "¥ billion", "%d months, monthb2: equities and all investment-fund shares" % w2["n"])
        q.add("Q6", wname, "ltd", "life", "sum_net", fmt_bn(q.ws[("life", wname)]["sum_net"]), "¥ billion", "%d months, monthb3" % q.ws[("life", wname)]["n"])
    return q


# ------------------------------------------------------------------------------------------------------------------------
# the registered October forecast (spec 5)
# ------------------------------------------------------------------------------------------------------------------------
def registered():
    return (-2885, -782, 746) if M("registered_edited") else REGISTERED


def base_months():
    first, last = BASE_FIRST, BASE_LAST
    if M("band_window_back"):
        first, last = ym_next(first, -1), ym_next(last, -1)
    if M("band_window_fwd"):
        first, last = ym_next(first, 1), ym_next(last, 1)
    if M("band_median23"):
        first = ym_next(first, 1)
    return ym_range(first, last)


def band_of(nets):
    """Order statistics of the 24 base Net cells: low = 3rd, point = mean of the 12th and 13th, high = 22nd. -> (low, point, high) as Fractions."""
    if len(nets) != 24:
        raise DataError("the band needs exactly 24 Net cells, got %d" % len(nets))
    s = sorted(nets)
    lo, hi = (1, 22) if M("band_2nd_23rd") else (2, 21)
    point = Fraction(s[11] + s[12], 2)
    if M("band_float"):
        point = Fraction(round(round((s[11] + s[12]) / 2.0 / 10, 1) * 10))
    return Fraction(s[lo]), point, Fraction(s[hi])


def base_nets(months):
    return [months[ym]["life"][2] for ym in base_months()]


def score_status(net, acq, disp, band=None):
    low, _, high = band if band is not None else registered()
    x = (acq - disp) if M("score_acq_minus_disp") else net
    if M("print_in_bn"):
        x = x * 10
    inside = (low < x < high) if M("strict_edges") else (low <= x <= high)
    return "INSIDE" if inside else ("BELOW" if x < low else "ABOVE")


def scoring_gate(cache_dir):
    """The scoring never looks at a latch (R3 and R2-7). The mutant makes STOP_BOJ block it."""
    if M("stop_boj_blocks_scoring") and cache_dir and os.path.exists(os.path.join(cache_dir, "STOP_BOJ")):
        raise Latched("STOP_BOJ exists")


FORECAST_NOTE = ("Frozen rule on the Net cell of life insurers' long-term debt, redemptions included; it is not a forecast of sales.")


def forecast_rows(vints, cache_dir=None):
    """The rows of forecast_score.csv for monthb3 vintages (oldest first). Only a vintage whose Final Update is 2026-11-10 can be of record."""
    scoring_gate(cache_dir)
    low, point, high = registered()
    pub = [v for v in vints if TARGET in v.months]

    def row(v, printv, status, rec, band, note):
        return [REGISTERED_ON, ym_text(TARGET), v.fu.isoformat(), v.sha, itext(point), itext(low), itext(high), itext(printv), status, rec,
                *(fmt_exact(b) if band else "" for b in (band or (None, None, None))), note + " " + FORECAST_NOTE]
    if not pub:
        return [row(vints[-1], None, "PENDING", "no", None, "October 2026 is not yet published in any cached vintage.")]
    rows = []
    for i, v in enumerate(pub):
        t = v.months[TARGET]["life"]
        net = t[2]
        base = [v.months[ym]["life"][2] for ym in base_months()] if all(ym in v.months for ym in base_months()) else None
        band = band_of(base) if base is not None and base != list(BASE_PINS) else None
        if i == 0:
            if v.fu == RECORD_FU or (M("late_vintage_of_record") and v.fu >= RECORD_FU):
                use = band if (M("band_recomputed_scores") and band) else None
                rows.append(row(v, net, score_status(net, t[0], t[1], use), "yes",
                                band, "Scored on the registered band against the Net cell of the 10 Nov 2026 vintage."
                                + (" A base month is revised in this vintage: the recomputed band is information only." if band else "")))
            else:
                rows.append(row(v, net, "LATE_VINTAGE", "no", band, "First cached vintage with October published has another Final Update date; "
                                "the print is recorded and the scoring is left to the supervisor."))
        else:
            st = score_status(net, t[0], t[1]) if M("rescore_later") else "LATE_VINTAGE"
            rows.append(row(v, net, st, "no", band, "A later vintage: the print is recorded and is never re-scored."))
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# the CALENDAR row and the pinned checks (spec 8)
# ------------------------------------------------------------------------------------------------------------------------
CAL_RX = re.compile(r"POINT\s+([+\-−]?)¥([\d,]+(?:\.\d+)?)bn;\s*RANGE\s+([+\-−]?)¥([\d,]+(?:\.\d+)?)bn\s+to\s+"
                    r"([+\-−]?)¥([\d,]+(?:\.\d+)?)bn")


def parse_calendar_registration(text):
    """The registered (low, point, high) in file units from a CALENDAR row's POINT/RANGE text, or None."""
    if M("calendar_unmatched"):
        return None
    m = CAL_RX.search(text)
    if not m:
        return None

    def val(sign, num):
        v = Fraction(num.replace(",", "")) * 10
        return -v if sign in ("-", "−") else v
    g = m.groups()
    return (val(g[2], g[3]), val(g[0], g[1]), val(g[4], g[5]))


def calendar_state(path):
    """-> ('absent', None) | ('unparsed', None) | ('present', (low, point, high))"""
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return "absent", None
    rows = [ln for ln in lines if ln.startswith("2026-11-10\t") and "monthb3" in ln]
    if not rows:
        return "absent", None
    reg = parse_calendar_registration(rows[0])
    return ("present", reg) if reg is not None else ("unparsed", None)


def calendar_status(state, reg):
    if state == "absent":
        return "WARN"
    if state == "unparsed" or reg is None:
        return "FAIL"
    return "PASS" if tuple(reg) == tuple(registered()) else "FAIL"


C02_MONTHS = {(2026, 9): (5487, 8374, -2886), (2024, 3): (11783, 13790, -2007), (2005, 1): (5271, 9384, -4113)}
# C07: the spec prints "exactly 324 cells (108 rows x 3 fields x 4 sectors)". 108 x 3 x 4 is 1,296; 324 = 108 x 3 is the count for ONE sector. The first build on the
# 8 Oct 2026 file (19 Oct 2026) failed on the literal 324 and observed 1,296 (324 in each of the four sectors, none elsewhere); the pin is the spec's own factorisation.
C07_DASH = 108 * 3 * 4
C03_MONTH = (2026, 9)
C03 = {TOTAL: (494609, 508869, -14260), "banks_banking": (None, None, -24856), "trust_accounts": (54154, 42200, 11953),
       "inv_trust": (None, None, -2001), "nonlife": (0, 5, -5)}
C13 = dict(
    sum={"W0": 190365, "W1": -142291, "W2": -38408, "W2b": -36401},
    mean={"W0": "3172.8", "W1": "-2371.5", "W2": "-1239.0", "W2b": "-1213.4"},
    median={"W0": "1937.5", "W1": "-815.0", "W2": "-1237.0", "W2b": "-1019.5"},
    neg={"W0": (18, 60), "W1": (39, 60), "W2": (23, 31), "W2b": (22, 30)},
    share_w2="74.19", share_w1="65.00",
    q2=("-3177.7", "-4310.3", "1132.5"),
    life_share={"W0": ("4.98", "3.96"), "W1": ("2.92", "3.57"), "W2": ("2.06", "2.38")},
    dealer_acq={"W0": "62.9", "W1": "63.5", "W2": "63.9"},
    total_net={"W0": 444594, "W1": 390290, "W2": 83347},
    ratio={"W0": "0.43", "W1": "opposite_sign", "W2": "opposite_sign"},
    trust_w2_mean="7332.6",
    q5=dict(n=1, month=(2020, 6), value=-2091, minimum=((2023, 2), -131051), last=((2026, 9), -21147)),
    q6=dict(W1=41328, W2=2102),
)


def find_ref(vints, key):
    """The cached vintage of a file whose Final Update is 8 Oct 2026, or None."""
    return next((v for v in vints[key] if v.fu == OCT8_FU), None)


def window_numbers(q):
    """The numbers C13 pins, from a Q object, as text. -> dict"""
    ws = q.ws
    out = {}
    for w in ("W0", "W1", "W2", "W2b"):
        s = ws[("life", w)]
        out["sum_" + w] = s["sum_net"]
        out["mean_" + w] = fmt_100m1(s["mean_net"])
        out["median_" + w] = fmt_100m1(s["median_net"])
        out["neg_" + w] = (s["n_neg"], s["n"])
    out["share_w2"], out["share_w1"] = fmt_pct(ws[("life", "W2")]["share_neg"]), fmt_pct(ws[("life", "W1")]["share_neg"])
    out["q2"] = (fmt_100m1(q.q["d_acq"]), fmt_100m1(q.q["d_disp"]), fmt_100m1(q.q["d_net"]))
    for w in ("W0", "W1", "W2"):
        sums = q.sums[w]
        la, ld, ln = sums["life"]
        ta, td, tn = sums[TOTAL]
        out["life_share_" + w] = (fmt_pct(Fraction(la, ta)), fmt_pct(Fraction(ld, td)))
        out["dealer_acq_" + w] = fmt_pct(Fraction(sums["fi_firms"][0], ta), 1)
        out["total_net_" + w] = tn
        r = net_ratio(ln, tn)
        out["ratio_" + w] = r if isinstance(r, str) else fmt_dec(r, 2)
    out["opposite_w2"] = sorted(q.q.get("opposite", []))
    out["trust_w2_mean"] = fmt_100m1(ws[("trust_accounts", "W2")]["mean_net"])
    out["q5_n"] = len(q.q["chg"])
    out["q5_first"] = q.q["chg"][0] if q.q["chg"] else None
    out["q5_min"] = q.q["min"]
    out["q5_last"] = q.q["last_roll"]
    out["q6"] = dict(q.q["q6"])
    return out


def c13_expected_actual(n):
    """-> list of (check id, description, expected text, observed text, ok)"""
    P = C13
    rows = []
    exp_a = "life net W0/W1/W2/W2b: sum %s; mean %s; median %s; net-disposition months %s" % (
        " / ".join(fint(P["sum"][w]) for w in P["sum"]), " / ".join(P["mean"][w] for w in P["mean"]), " / ".join(P["median"][w] for w in P["median"]),
        " / ".join("%d of %d" % P["neg"][w] for w in P["neg"]))
    obs_a = "sum %s; mean %s; median %s; net-disposition months %s" % (
        " / ".join(fint(n["sum_" + w]) for w in P["sum"]), " / ".join(n["mean_" + w] for w in P["mean"]), " / ".join(n["median_" + w] for w in P["median"]),
        " / ".join("%d of %d" % n["neg_" + w] for w in P["neg"]))
    ok_a = (all(n["sum_" + w] == P["sum"][w] and n["mean_" + w] == P["mean"][w] and n["median_" + w] == P["median"][w] and n["neg_" + w] == P["neg"][w]
                for w in P["sum"]))
    rows.append(("C13a", "Life net (long-term debt) by window, in 100m yen: sum, mean and median (one decimal), months with net disposition", exp_a, obs_a, ok_a))
    exp_b = "Q1 flag does not fire; share of months with net disposition W2 %s%% against W1 %s%%" % (P["share_w2"], P["share_w1"])
    rows.append(("C13b", "Q1: shares of months with net disposition, W2 against W1 (the Q1 flag is the W2 mean below the W1 mean)", exp_b,
                 "share W2 %s%% against W1 %s%%; flag %s" % (n["share_w2"], n["share_w1"], "fires" if n.get("flag") else "does not fire"),
                 n["share_w2"] == P["share_w2"] and n["share_w1"] == P["share_w1"] and not n.get("flag")))
    rows.append(("C13c", "Q2, W1 to W2, in 100m yen: change in mean acquisitions, in mean dispositions, in mean net",
                 "%s / %s / +%s" % P["q2"], "%s / %s / %s%s" % (n["q2"][0], n["q2"][1], "+" if not n["q2"][2].startswith("-") else "", n["q2"][2]),
                 tuple(n["q2"]) == tuple(P["q2"])))
    exp_d = "life share of gross acquisitions / dispositions (percent) %s; dealer share of acquisitions %s; total nets %s; net ratio %s" % (
        "; ".join("%s %s%% / %s%%" % (w, *P["life_share"][w]) for w in P["life_share"]), " / ".join(P["dealer_acq"][w] + "%" for w in P["dealer_acq"]),
        " / ".join("+" + fint(P["total_net"][w]) for w in P["total_net"]), ", ".join("%s %s" % (w, P["ratio"][w]) for w in P["ratio"]))
    obs_d = "life share %s; dealer share of acquisitions %s; total nets %s; net ratio %s" % (
        "; ".join("%s %s%% / %s%%" % (w, *n["life_share_" + w]) for w in P["life_share"]), " / ".join(n["dealer_acq_" + w] + "%" for w in P["dealer_acq"]),
        " / ".join(("+" if n["total_net_" + w] >= 0 else "") + fint(n["total_net_" + w]) for w in P["total_net"]),
        ", ".join("%s %s" % (w, n["ratio_" + w]) for w in P["ratio"]))
    ok_d = all(tuple(n["life_share_" + w]) == tuple(P["life_share"][w]) and n["dealer_acq_" + w] == P["dealer_acq"][w]
               and n["total_net_" + w] == P["total_net"][w] and n["ratio_" + w] == P["ratio"][w] for w in P["life_share"])
    rows.append(("C13d", "Q3: life insurers' share of reported gross contracts (dealer-inclusive), the dealers' share, the nets and the net ratio", exp_d, obs_d, ok_d))
    rows.append(("C13e", "Q4: the comparator with a W2 mean monthly net of the opposite sign to life insurers', and its mean in 100m yen",
                 "trust_accounts only, mean +%s" % P["trust_w2_mean"], "%s, mean %s" % (", ".join(n["opposite_w2"]) or "none", n["trust_w2_mean"]),
                 n["opposite_w2"] == ["trust_accounts"] and n["trust_w2_mean"] == P["trust_w2_mean"]))
    p5 = P["q5"]
    first = n["q5_first"]
    rows.append(("C13f", "Q5: sign changes of the rolling 12-month net (100m yen), its minimum and its latest value",
                 "%d change, to negative at %s (%s), negative since; minimum %s at %s; latest %s at %s" % (
                     p5["n"], ym_text(p5["month"]), fint(p5["value"]), fint(p5["minimum"][1]), ym_text(p5["minimum"][0]), fint(p5["last"][1]),
                     ym_text(p5["last"][0])),
                 "%d change(s)%s; minimum %s at %s; latest %s at %s" % (
                     n["q5_n"], ", first %s at %s (%s)" % (first[1], ym_text(first[0]), fint(first[2])) if first else "", fint(n["q5_min"][1]),
                     ym_text(n["q5_min"][0]), fint(n["q5_last"][1]), ym_text(n["q5_last"][0])),
                 n["q5_n"] == p5["n"] and first is not None and first[0] == p5["month"] and first[1] == "to_negative" and first[2] == p5["value"]
                 and tuple(n["q5_min"]) == (p5["minimum"][0], p5["minimum"][1]) and tuple(n["q5_last"]) == (p5["last"][0], p5["last"][1])))
    rows.append(("C13g", "Q6: life insurers' fund-share (monthb2) net, W1 and W2, in 100m yen", "W1 +%s, W2 +%s" % (fint(P["q6"]["W1"]), fint(P["q6"]["W2"])),
                 "W1 %s, W2 %s" % (fint(n["q6"]["W1"]), fint(n["q6"]["W2"])), n["q6"]["W1"] == P["q6"]["W1"] and n["q6"]["W2"] == P["q6"]["W2"]))
    return rows


def pin_status(ok, have_ref):
    if not have_ref:
        return "WARN"
    return "PASS" if ok else "FAIL"


def tri(t):
    return " / ".join("." if v is None else fint(v) for v in t)


def run_checks(ctx):
    """All rows of checks.csv except C11. Pins are tested on the 8 Oct 2026 vintage when it is cached."""
    vints, latest, q, today = ctx["vints"], ctx["latest"], ctx["q"], ctx["today"]
    rows = []

    def add(cid, desc, exp, obs, status):
        rows.append([cid, desc, exp, obs, status])
    ref3 = find_ref(vints, "monthb3")
    have = ref3 is not None
    lat3 = latest["monthb3"]
    p3 = lat3.parsed
    nref = "the 8 Oct 2026 vintage of monthb3 is not cached, so the pin is not tested; latest vintage shown"
    # C01 vintage
    c1_exp = "monthb3 8 Oct 2026 vintage: sha256 %s, %s bytes, Final Update October 8, 2026, 261 published months 2005-01 to 2026-09, 2026-10 to 2026-12 blank, monthly.csv %s rows" % (
        OCT8["monthb3"][0], fint(OCT8["monthb3"][1]), fint(6 * 4 * 261))
    nrows = len(ctx["monthly"])
    if have:
        rp = ref3.parsed
        ok = (ref3.sha == OCT8["monthb3"][0] and ref3.nbytes == OCT8["monthb3"][1] and len(rp.months) == 261 and min(rp.months) == (2005, 1)
              and max(rp.months) == (2026, 9) and rp.blank == [(2026, 10), (2026, 11), (2026, 12)] and (lat3 is not ref3 or nrows == 6 * 4 * 261))
        obs = "sha256 %s, %s bytes, Final Update %s, %d published months %s to %s, blank %s; monthly.csv %s rows (latest vintage %s)" % (
            ref3.sha, fint(ref3.nbytes), ref3.fu.isoformat(), len(rp.months), ym_text(min(rp.months)), ym_text(max(rp.months)),
            ", ".join(ym_text(m) for m in rp.blank) or "none", fint(nrows), lat3.fu.isoformat())
        add("C01", "Vintage of the scored file: the 8 Oct 2026 monthb3 is the one the spec pins", c1_exp, obs, "PASS" if ok else "FAIL")
    else:
        add("C01", "Vintage of the scored file: the 8 Oct 2026 monthb3 is the one the spec pins", c1_exp,
            "%s: %s, Final Update %s, %d published months to %s; monthly.csv %s rows" % (nref, lat3.sha[:12], lat3.fu.isoformat(), len(p3.months),
                                                                                      ym_text(max(p3.months)), fint(nrows)), "WARN")
    dis = {k: len(latest[k].parsed.jp_disagree) for k in FILE_ORDER}
    add("C01b", "The Japanese and English month columns agree (the output follows the English column)", "0 disagreements in each file",
        ", ".join("%s %d" % (k, dis[k]) for k in FILE_ORDER), "PASS" if not any(dis.values()) else "WARN")
    # C02 raw cells
    pp = ref3.parsed if have else p3
    bad = [ym_text(ym) for ym, t in C02_MONTHS.items() if pp.months.get(ym, {}).get("life") != t]
    tot = pp.totals
    c_cy22 = tot.get(("CY", 2022), {}).get("life", (None,) * 3)[2]
    c_fy25 = tot.get(("FY", 2025), {}).get("life")
    c_cy25 = tot.get(("CY", 2025), {}).get("life", (None,) * 3)[2]
    s25 = sum(pp.months[(2025, m)]["life"][2] for m in range(1, 13)) if all((2025, m) in pp.months for m in range(1, 13)) else None
    ok2 = not bad and c_cy22 == -114641 and c_fy25 == (95993, 108098, -12105) and c_cy25 == -6727 and s25 == -6726
    add("C02", "Life insurers' raw cells (acquisition / disposition / net, 100m yen): three months, the file's CY and FY cells, and 2025's monthly sum",
        "2026-09 5,487 / 8,374 / −2,886; 2024-03 11,783 / 13,790 / −2,007; 2005-01 5,271 / 9,384 / −4,113; 2022CY net −114,641; 2025FY 95,993 / 108,098 / −12,105; "
        "2025CY net cell −6,727, its 12 monthly Net cells sum −6,726",
        "; ".join("%s %s" % (ym_text(ym), tri(pp.months[ym]["life"])) for ym in C02_MONTHS if ym in pp.months) + "; 2022CY net %s; 2025FY %s; 2025CY net cell %s, monthly sum %s%s" % (
            fint(c_cy22) if c_cy22 is not None else ".", tri(c_fy25) if c_fy25 else ".", fint(c_cy25) if c_cy25 is not None else ".",
            fint(s25) if s25 is not None else ".", "" if have else "; " + nref), pin_status(ok2, have))
    # C03 comparators
    ok3 = True
    parts = []
    for code, t in C03.items():
        got = pp.months.get(C03_MONTH, {}).get(code)
        if got is None:
            ok3 = False
            continue
        for i, v in enumerate(t):
            if v is not None and got[i] != v:
                ok3 = False
        parts.append("%s %s" % (code, tri(got)))
    add("C03", "Comparators in 2026-09 (acquisition / disposition / net, 100m yen): they catch a block swap that additivity cannot",
        "designated_reporters_total 494,609 / 508,869 / −14,260; banks_banking net −24,856; trust_accounts 54,154 / 42,200 / 11,953; inv_trust net −2,001; nonlife 0 / 5 / −5",
        "; ".join(parts) + ("" if have else "; " + nref), pin_status(ok3, have))
    # C04 sign identity, each file (tolerance gates the build; the pinned counts are descriptive)
    sres = {k: sign_check(latest[k].parsed) for k in FILE_ORDER}
    viol = {k: sign_violations(sres[k]) for k in FILE_ORDER}
    rp = sres["monthb3"]
    pins4 = (rp["post"]["cells"], rp["post"]["over1"], rp["pre"]["cells"], rp["pre"]["over1"], rp["pre"]["max"])
    pin_ok4 = have and lat3 is ref3 and pins4 == (2601, 0, 1404, 17, 4)
    st4 = "FAIL" if any(viol.values()) else ("PASS" if (pin_ok4 or not have or lat3 is not ref3) else "WARN")
    add("C04", "Sign identity: Net = Acquisition minus Disposition in every non-missing cell of all four files (within 1 from 2014, within 4 before)",
        "monthb3 post-2014 cells off by more than 1: 0 of 2,601; pre-2014: 17 of 1,404, largest gap 4; every file within tolerance",
        "; ".join("%s: post-2014 %d of %s over 1 (max %d), pre-2014 %d of %s over 1 (max %d)" % (
            k, sres[k]["post"]["over1"], fint(sres[k]["post"]["cells"]), sres[k]["post"]["max"], sres[k]["pre"]["over1"], fint(sres[k]["pre"]["cells"]),
            sres[k]["pre"]["max"]) for k in FILE_ORDER) + ("; " + "; ".join(k + " " + ", ".join(v) for k, v in viol.items() if v) if any(viol.values()) else ""),
        st4)
    # C05 additivity
    wres = {k: within_additivity(latest[k].parsed) for k in FILE_ORDER}
    wviol = [(k, v) for k in FILE_ORDER for v in wres[k][1]]
    fus = [latest[k].fu for k in FILE_ORDER]
    cres = cross_additivity({k: latest[k].parsed for k in FILE_ORDER})
    cst = cross_status(cres, fus)
    wm = wres["monthb3"][0]
    desc_ok = have and lat3 is ref3 and (wm["other_financial"], wm["designated_reporters_total"], wm["trust_accounts"]) == (2, 1, 1) and \
        cres["max_all"] == 4 and cres["max_committed"] == 1 and cres["max_net"] == 3
    st5 = "FAIL" if (wviol or cst == "FAIL") else ("WARN" if cst == "WARN" or (have and lat3 is ref3 and not desc_ok) else "PASS")
    add("C05", "Additivity: within each file (net column, tolerance 3) and across files, b1 = b2 + b3 + b4 (tolerance 4 over 17 sectors, 2 over the six committed; "
               "compared only when the Final Update dates are equal)",
        "monthb3 within-file maxima other_financial / designated_reporters_total / trust_accounts 2 / 1 / 1; cross-file all fields: 17 sectors max 4, six committed sectors max 1, net field alone max 3",
        "within-file maxima (monthb3) %d / %d / %d, other files %s; cross-file %s: 17 sectors max %d, six committed max %d, net alone max %d%s" % (
            wm["other_financial"], wm["designated_reporters_total"], wm["trust_accounts"],
            "; ".join("%s %d / %d / %d" % (k, wres[k][0]["other_financial"], wres[k][0]["designated_reporters_total"], wres[k][0]["trust_accounts"])
                      for k in FILE_ORDER if k != "monthb3"),
            "compared" if len(set(fus)) == 1 else "NOT compared (Final Update dates differ)", cres["max_all"], cres["max_committed"], cres["max_net"],
            "; worst " + "; ".join("%s %s %s: %s against %s" % (c, f, m, tri(v[:1]), tri([v[1] + v[2] + v[3]])) for c, f, m, v in cres["worst"][:2])
            if cres["worst"] and cres["max_all"] > 3 else ""), st5)
    # C06 annual sums
    ares = {k: annual_check(latest[k].parsed) for k in FILE_ORDER}
    a3 = ares["monthb3"]
    aviol = [(k, v) for k in FILE_ORDER for v in ares[k]["violations"]]
    desc6 = have and lat3 is ref3 and (a3["max_cy"], a3["max_fy"], a3["net_cy"], a3["net_fy"]) == (7, 6, 4, 3)
    add("C06", "Annual sums: the 12 months against the file's own CY and FY cells, all 17 sectors and fields, every file (tolerance 12)",
        "monthb3 largest gap 7 (CY) and 6 (FY), both in other_financial; net field alone 4 and 3",
        "monthb3 largest gap %d (CY) and %d (FY)%s; net field alone %d and %d; other files %s; %d periods checked in monthb3" % (
            a3["max_cy"], a3["max_fy"], "".join(", %s in %s" % (w[0], w[1]) for w in a3["worst"]), a3["net_cy"], a3["net_fy"],
            "; ".join("%s %d / %d" % (k, ares[k]["max_cy"], ares[k]["max_fy"]) for k in FILE_ORDER if k != "monthb3"), a3["periods"]),
        "FAIL" if aviol else ("PASS" if (desc6 or not have or lat3 is not ref3) else "WARN"))
    # C07 missing pattern (monthb3 is the pinned file)
    mp = missing_pattern(pp)
    ok7 = mp == dict(dash=C07_DASH, other=0, pre_published=0)
    others = "; ".join("%s %d" % (k, missing_pattern(latest[k].parsed)["dash"]) for k in FILE_ORDER if k != "monthb3")
    add("C07", "Missing marker: '-' in every cell of four sectors from 2005-01 to 2013-12 (108 rows x 3 fields = 324 cells per sector, %s in all) and nowhere else; published from 2014-01"
        % fint(C07_DASH),
        "%s dashes in central_bank, general_govt, banks_trust and trust_banks_trust before 2014 (324 in each); no other blank or dash in a published month" % fint(C07_DASH),
        "monthb3: %d dashes in those four sectors before 2014, %d other blank or dash cells, %d of those four sectors published before 2014; other files' dash counts: %s%s" % (
            mp["dash"], mp["other"], mp["pre_published"], others, "" if have else "; " + nref), pin_status(ok7, have))
    # C08 BoJ
    cache = ctx["cache"]
    miss, wrong = [], []
    for d, _, _, _, _, s16, _ in BOJ_ROWS:
        fp = os.path.join(cache, "boj_%s.pdf" % d)
        if not os.path.exists(fp):
            miss.append(d)
            continue
        with open(fp, "rb") as fh:
            if sha256_of(fh.read())[:16] != s16:
                wrong.append(d)
    n_ok = len(BOJ_ROWS) - len(miss) - len(wrong)
    add("C08", "Bank of Japan statements: the 12 cached PDFs carry the sha256 prefixes of the spec (a mismatch is a FAIL of this check only; it does not stop the build)",
        "12 of 12 match", "%d of 12 match%s%s" % (n_ok, "; not cached: " + ", ".join(miss) if miss else "", "; sha256 differs: " + ", ".join(wrong) if wrong else ""),
        "PASS" if n_ok == 12 else "FAIL")
    # C09 calendar
    state, reg = ctx["calendar"]
    st9 = calendar_status(state, reg)
    add("C09", "The CALENDAR row 2026-11-10 carries the registered point and range",
        "POINT -¥78.2bn; RANGE -¥288.6bn to +¥74.6bn",
        {"absent": "row absent (moved or resolved after a recorded outcome)", "unparsed": "row present, point and range not found in its text"}.get(
            state, "point %s, range %s to %s (100m yen)" % tuple(fmt_exact(x) for x in (reg[1], reg[0], reg[2])) if reg else ""), st9)
    # C10 band
    if have:
        base, src = base_nets(ref3.months), "the 8 Oct 2026 vintage"
    else:
        base, src = list(BASE_PINS), "the 24 pins of the spec (the 8 Oct 2026 vintage is not cached)"
    band = band_of(base)
    ok10 = tuple(band) == tuple(Fraction(x) for x in registered()) and (not have or base == list(BASE_PINS))
    ok10 = ok10 or M("c10_lenient")
    add("C10", "The registered band reproduces from the 24 base Net cells 2024-10 to 2026-09 (a FAIL stops the build)",
        "point −782, low −2,886 (3rd), high +746 (22nd), in 100m yen; sum −27,484; 18 months of net disposition and 6 of net acquisition",
        "from %s: point %s, low %s, high %s; sum %s; %d months of net disposition and %d of net acquisition" % (
            src, fmt_exact(band[1]), fmt_exact(band[0]), fmt_exact(band[2]), fint(sum(base)), sum(1 for x in base if x < 0), sum(1 for x in base if x > 0)),
        "PASS" if ok10 else "FAIL")
    # C12 staleness
    end = month_end(max(p3.months))
    age = (today - end).days
    add("C12", "Staleness: the end of the latest published month is not more than 45 days before the run date (a missed release)",
        "at most 45 days", "latest published month %s; %s" % (ym_text(max(p3.months)), "more than 45 days old" if age > 45 else "within 45 days"),
        "PASS" if age <= 45 else "WARN")
    # C13 window statistics
    if have:
        qref = q if lat3 is ref3 else build_questions(ref3.parsed, (find_ref(vints, "monthb2") or latest["monthb2"]).parsed, max(ref3.months), "ref")
        have13 = True
    else:
        qref, have13 = q, False
    nn = window_numbers(qref)
    nn["flag"] = qref.q["q1_flag"]
    for cid, desc, exp, obs, ok in c13_expected_actual(nn):
        add(cid, desc + ("" if have13 else " (information only: the 8 Oct 2026 vintage is not cached)"), exp, obs, ("PASS" if ok else "FAIL") if have13 else "INFO")
    # C14 press reference points
    c = p3.totals.get(("CY", 2022), {}).get("life", (None,) * 3)[2]
    msum = sum(p3.months[(2022, m)]["life"][2] for m in range(1, 13))
    add("C14", "Press reference points (information only): the 2022 life net, December 2022 and November 2022, against the figures the press gave",
        "2022 file cell -114,641 and monthly Net cells -114,640; December 2022 -22,466; November 2022 -19,269 (100m yen)",
        "2022 file cell %s and monthly Net cells %s; December 2022 %s; November 2022 %s. Press: a little over 11 trillion yen for 2022 (Nikkei, 21 Feb 2023); 1.9 trillion yen for November 2022 "
        "(Japan Times, 8 Dec 2022); wording in SOURCES.md" % (fint(c) if c is not None else ".", fint(msum), fint(p3.months[(2022, 12)]["life"][2]),
                                                                fint(p3.months[(2022, 11)]["life"][2])), "INFO")
    # C15 pins against the cache
    if have:
        add("C15", "Pins against the cache (information only)", "listed only when C10 runs from the pins", "not needed: C10 ran on the 8 Oct 2026 vintage", "INFO")
    else:
        earliest = vints["monthb3"][0]
        diffs = [(ym_text(ym), pin, earliest.months[ym]["life"][2]) for ym, pin in zip(base_months(), BASE_PINS)
                 if ym in earliest.months and earliest.months[ym]["life"][2] != pin]
        add("C15", "Pins against the cache (information only): the 24 pins diffed against the earliest cached monthb3 vintage", "no difference",
            ("%d differences: " % len(diffs) + "; ".join("%s pin %s cache %s" % d for d in diffs)) if diffs else
            "no difference against the earliest cached vintage (Final Update %s)" % earliest.fu.isoformat(), "INFO")
    return rows


def pins_rows():
    rows = []
    src = "MoF monthb3.csv, Final Update October 8, 2026"
    for ym, v in zip(base_months(), BASE_PINS):
        rows.append([src, "life insurers, long-term debt, Net cell", ym_text(ym), v, "100m yen"])
    for ym, t in sorted(C02_MONTHS.items()):
        for f, v in zip(FIELDS, t):
            rows.append([src, "life insurers, long-term debt, %s cell" % f, ym_text(ym), v, "100m yen"])
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# README and SOURCES (generated, scanned by G15)
# ------------------------------------------------------------------------------------------------------------------------
def worked_row(p3):
    t = p3.months.get((2024, 3), {}).get("life")
    if not t:
        return "March 2024 is not in this file."
    a, d, n = t
    s = "**March 2024, life insurers: %s − %s = %s** (¥100 million)" % (fint(a), fint(d), fint(a - d))
    if n != a - d:
        s += "; the Net cell is %s" % fint(n)
    return s + ". MoF rounds each cell separately, so Net can differ from the subtraction by 1."


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---:" if i > 2 else "---" for i in range(len(header))) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


DECISIONS = (
    "A later vintage of October 2026 adds a `forecast_score.csv` row with `of_record = no` and status `LATE_VINTAGE` (the spec says only that such a row is recorded and never re-scored; "
    "a scored word on it could be read as a second score).",
    "A STOP file makes the whole `fetch` command refuse, not only the MoF files (a MoF failure ends the run, and the BoJ part comes after the MoF part); STOP_BOJ blocks only the BoJ part.",
    "A failed C08 (the Bank of Japan checksums) is written to `checks.csv` and does not send the build to `_FAILED/`; every other FAIL does.",
    "In C04, C05 and C06 a gap above the spec's tolerance is a FAIL; the spec's observed maxima are descriptive pins, and a difference from them with the tolerance met is a WARN. C07 is exact and "
    "tested on monthb3 only; the other files' dash counts are listed beside it.",
    "Within-file additivity, annual sums and the sign identity are tested on all four files; the pinned values belong to monthb3.",
    "`questions.csv` keeps the rows of earlier runs (`run_label` names the vintage) beside the current run.",
    "`pins.csv` holds the 24 base Net cells of the registered rule and the nine life-insurer raw cells of C02.",
    "A zero in the denominator of a net ratio is reported as `exceeds_total`.",
    "The wording check runs over every cell of every committed file, not only over the named text fields.",
    "Fix after the first build (19 Oct 2026): check C07 first expected 324 dash cells in all, as the spec prints. The spec's own factorisation (108 rows x 3 fields x 4 sectors) is 1,296, "
    "and 324 is the count for one sector. The first build observed 1,296 (324 in each of the four sectors, none elsewhere) and failed on the literal 324; the pin is now 1,296.",
    "Fix after the first build (19 Oct 2026): the Q3 rows of `questions.csv` first named only the total in their `denominator` column; they now begin with the spec's label "
    "\"share of reported gross contracts (dealer-inclusive)\". No value changed. Nothing else was changed after the first build.",
)

COLUMN_DICT = (
    ("monthly.csv", "`month` (YYYY-MM); `instrument` (`ltd` long-term debt = monthb3, `equity_funds` = monthb2, `std` short-term debt = monthb4, `all` = monthb1); `sector`; "
                    "`acquisition_100m_yen`, `disposal_100m_yen` (the file's disposition) and `net_100m_yen` in ¥100 million, the Net cell as MoF prints it; `basis` (`old_to_2013` or `new_from_2014`)."),
    ("annual.csv", "`period_type` (CY calendar year, FY fiscal year April to March labelled by its starting year, CY_YTD and FY_YTD year to date); `period`; `basis` (also `mixed_2013_2014` for FY2013 and "
                   "`mixed_2007` for 2007); `months` summed; the three sums; `file_total_net_100m_yen` (the file's own CY or FY Net cell) and `diff_100m_yen` (sum of months minus the file's cell)."),
    ("boj_dates.csv", "`decision_date`, `effective_date`, `month`, `action`, `phrase` (under 15 words), `url` and the `sha256` of the cached statement (Bank of Japan, Statement on Monetary Policy)."),
    ("questions.csv", "`run_label` (instrument, vintage and latest month), `question` (Q1 to Q6), `window`, `instrument`, `sector`, `statistic`, `value`, `unit` and `denominator`; `notable` is `yes` or `no` where a rule exists."),
    ("forecast_score.csv", "The registered point, low and high and the October 2026 Net cell, in file units; `status` (PENDING, INSIDE, BELOW, ABOVE or LATE_VINTAGE); `of_record`; the recomputed band where a base month is revised."),
    ("vintages.csv", "One row per cached MoF file: Final Update date, retrieval time, bytes, sha256, published months and the last month."),
    ("revisions.csv", "Differences between consecutive vintages of the same file for the six committed sectors, with old and new values; `kind` is `revised`, `new` (a month or cell that was blank) or `removed`."),
    ("checks.csv", "`check_id`, what was tested, what was expected, what was observed, and PASS, FAIL, WARN or INFO."),
    ("pins.csv", "Published values the spec pins, with their source and unit."),
    ("fetch_log.csv", "One row per request: UTC time, host, path, status, bytes and sha256."),
)


def trn(x100m):
    """File units (100 million yen) -> yen trillion, two decimals, with the sign."""
    t = fmt_dec(Fraction(x100m) / 10000, 2)
    return ("\u2212" + t[1:] if t.startswith("-") else "+" + t) + " trillion yen"


def window_sentences(q):
    """The windows named, then life insurers' net per window in yen trillion and the months of net disposition, from the same values as questions.csv."""
    w0, w1, w2 = (q.ws[("life", n)] for n in ("W0", "W1", "W2"))
    if M("windows_hardcoded"):
        w0, w1, w2 = (dict(sum_net=v, n_neg=a, n=b) for v, a, b in ((190365, 18, 60), (-142291, 39, 60), (-38408, 23, 31)))
    return ("The windows used below and in `questions.csv`: W0 is 2014 to 2018, W1 is 2019 to 2023, W2 runs from March 2024 to the latest month, and W2b from April 2024.\n\n"
            "Life insurers' net, long-term debt: %s over W0 (%d of %d months of net disposition), %s over W1 (%d of %d) and %s over W2 (%d of %d)." % (
                trn(w0["sum_net"]), w0["n_neg"], w0["n"], trn(w1["sum_net"]), w1["n_neg"], w1["n"], trn(w2["sum_net"]), w2["n_neg"], w2["n"]))


def render_readme(ctx):
    latest, q, L = ctx["latest"], ctx["q"], ctx["L"]
    p3 = latest["monthb3"].parsed
    ds = retrieval_dates(ctx["log_rows"], MOF_HOST)
    life = [r for r in ctx["annual"] if r[3] == "ltd" and r[4] == "life"]
    rows = []
    for r in life:
        if r[0] in ("CY", "FY") and int(r[1]) < 2014:
            continue
        rows.append((r[0], r[1], r[2], r[5], fmt_bn(int(r[6])), fmt_bn(int(r[7])), fmt_bn(int(r[8]))))
    fc = ctx["forecast"]
    fc_text = ("PENDING: October 2026 is not yet published in any cached vintage; MoF publishes it on 10 Nov 2026 at 08:50 JST." if fc[0][8] == "PENDING"
               else "; ".join("vintage %s: print %s (100m yen), status %s, of record %s" % (r[2], r[7], r[8], r[9]) for r in fc))
    out = []
    w = out.append
    w("# Japanese life insurers' foreign long-term bonds: monthly acquisitions and dispositions")
    w("")
    w("Japanese life insurers' monthly acquisitions and dispositions of foreign bonds issued with an original maturity of more than one year, as reported to the "
      "Ministry of Finance by designated major investors, with other investor types beside them. " + REQUIRED)
    w("")
    w("**Coverage.** Designated major investors only: the survey is narrower than balance-of-payments portfolio investment and is released earlier (the month "
      "after the month it covers, against the month after next). The total block is therefore `designated_reporters_total`, never all residents.")
    w("")
    w("## The latest result")
    w("")
    w("Life insurers, long-term debt (monthb3), Final Update %s, latest published month %s. Amounts are ¥ billion (the file's ¥100 million divided by 10); plus is net "
      "acquisition and minus is net disposition. `basis` is explained under the breaks below. The rows are sums of the months in the file." % (
          latest["monthb3"].fu.isoformat(), ym_text(L)))
    w("")
    w(window_sentences(q))
    w("")
    w(md_table(["period type", "period", "basis", "months", "acquisitions", "dispositions", "net"], rows))
    w("")
    w("**The October 2026 rule.** The Net cell of life insurers' long-term debt for October 2026 is compared with a rule registered on %s, before the print: "
      "point −¥78.2 billion, range −¥288.6 billion to +¥74.6 billion (the 24 monthly Net cells from 2024-10 to 2026-09; point is the median, range the 3rd "
      "to the 22nd order statistic; a print equal to an edge is inside). Status: %s This is a frozen rule on this net, redemptions included. It is not a forecast of sales." % (
          REGISTERED_ON, fc_text))
    w("")
    w("## Defined terms")
    w("")
    w("- **Acquisition**: an increase in holdings of foreign long-term debt (MoF: an increase of assets).")
    w("- **Disposition**: sales, redemptions and other reductions in holdings (the file's term); redemptions of overseas government bonds are included, MoF FAQ A5. "
      "Whether redemptions of other bonds are included is not stated.")
    w("- **Net acquisition and net disposition**: the file's Net cell. Plus is net acquisition; minus is net disposition (file Note 2).")
    w("- **Recorded at contract**: purchases and sales on the execution date, redemptions on the redemption date (MoF FAQ A6). These are flows of contracts, not holdings.")
    w("- **Long-term debt**: bonds issued with an original maturity of more than one year, classified by the residence of the issuer, not by currency.")
    w("- **Designated reporters**: the designated major investors named by the Finance Minister.")
    w("- **Dealers** (`fi_firms`, financial instruments firms) and their share of reported gross contracts: the share is of all designated reporters' acquisitions or dispositions in a window. "
      "Life insurers' share of reported gross contracts is dealer-inclusive and is printed beside the dealers' own.")
    w("- **Trust accounts** (`trust_accounts`): the trust accounts of banks and trust banks.")
    w("- **Investment trusts** (`inv_trust`): investment trust management companies, including asset management companies (file Note 4); for the classification see BoJ FAQ No. 14.")
    w("- **Fiscal year**: the Japanese fiscal year, April to March, labelled by its starting year.")
    w("")
    w("## What this series cannot say")
    w("")
    for s in ("why any investor acquired or disposed of bonds, or any effect on a yield, spread or exchange rate;",
              "how much of a disposition was a sale and how much a redemption;",
              "anything about US Treasuries alone, about currency, or about hedged against unhedged bonds (the file mixes all three);",
              "anything about holdings (these are flows of contracts);",
              "anything about bonds held through funds: since 2014 fund shares sit with equities in monthb2, with no split between bonds and equities."):
        w("- " + s)
    w("")
    w("## Breaks and the March 2024 note")
    w("")
    w("- **January 2014.** From 2014 open-end contractual investment trusts, previously in long-term debt, are counted in equity and investment fund shares, and the five-sector split "
      "is not applied to earlier months. MoF did not restate earlier months; the questions in `questions.csv` use 2014 onward only.")
    w("- **October 2007.** Securities companies and investment trust companies became financial instruments firms and investment trust management companies (file Note 3); months to "
      "September 2007 use the old categories.")
    w("- **Sign.** The file's own: plus is net acquisition. Before January 2014 MoF recompiled only the sign of the net for earlier months; the file confirms the identity "
      "Net = Acquisition − Disposition within 1 unit from 2014 and within 4 before. The English index page's older sign banner is stale and is not used.")
    w("- **March 2024.** The 19 March 2024 decision took effect on 21 March, so most of March 2024 is before it. Window W2 starts in March 2024 as registered; W2b starts in April 2024 and leaves it out.")
    w("")
    w("## A worked row")
    w("")
    w(worked_row(p3))
    w("")
    w("## Columns")
    w("")
    for name, text in COLUMN_DICT:
        w("- `%s`: %s" % (name, text))
    w("")
    if M("decisions_in_readme"):
        w("## Decisions where the specification left a choice")
        for d in DECISIONS:
            w("- " + d)
    w("## Provenance")
    w("")
    w("Source: " + CITATION % (MOF_URL, ", ".join(ds) if ds else "(no logged retrieval)"))
    w("")
    w("Bank of Japan, Statement on Monetary Policy, on the dates in `boj_dates.csv`; only dates and phrases under 15 words are cited.")
    w("")
    w("Build decisions, including two fixes made after the first build, are listed in [SOURCES.md](SOURCES.md).")
    w("")
    w("Vintages cached (file, Final Update, sha256 first 12): " + "; ".join("%s %s %s" % (v.key, v.fu.isoformat(), v.sha[:12]) for k in FILE_ORDER for v in ctx["vints"][k]) + ".")
    if M("volatile_output"):
        w("generated %d" % time.time_ns())
    return "\n".join(out) + "\n"


def render_sources(ctx):
    ds = retrieval_dates(ctx["log_rows"], MOF_HOST)
    out = []
    w = out.append
    w("# Sources and terms for data/jp_life_foreign_bonds/")
    w("")
    w("Each source below is public and free. Retrieval dates are in `fetch_log.csv`. The committed files are derived tables; the raw MoF files and the Bank of Japan statements are in a "
      "gitignored cache. " + REQUIRED)
    w("")
    w("- **Ministry of Finance Japan, International Transactions in Securities.** %s: `monthb3.csv` (long-term debt), `monthb1.csv` (total), `monthb2.csv` (equity and investment fund shares), "
      "`monthb4.csv` (short-term debt). Licence: the copyright page (https://www.mof.go.jp/about_mof/notice/index.html) puts site content under the Public Data License 1.0 unless marked otherwise; "
      "commercial use is allowed, numerical data are outside copyright, the source is to be cited, and processed content is to be labelled as such. Cite as: Source: %s" % (
          MOF_URL, CITATION % (MOF_URL, ", ".join(ds) if ds else "(no logged retrieval)")))
    w("- **MoF English FAQ** (https://www.mof.go.jp/english/policy/international_policy/reference/itn_transactions_in_securities/faq_its_english.html): A1 scope, A5 redemptions of overseas government "
      "bonds are included in the disposition, A6 recording dates. Read once, not fetched by the build.")
    w("- **MoF pages read once** (not fetched by the build): the index, the data notes (`data.htm`), the terms (`terms.html`), the English release schedule (`schedule.htm`) and the notice of "
      "27 December 2013 (`notice/notice20131227.pdf`).")
    w("- **Bank of Japan, Statement on Monetary Policy** (https://www.boj.or.jp/en/mopo/mpmdeci/): the twelve statements of `boj_dates.csv`. Only dates and phrases under 15 words are cited; "
      "copying with credit is allowed and commercial copying is excluded. Credit: Bank of Japan, Statement on Monetary Policy, with the decision date. The PDFs stay in the cache.")
    w("- **BoJ FAQ No. 14** (https://www.boj.or.jp/en/statistics/outline/exp/faqbpsm6.htm): the classification of investor types, cited for the investment trust column.")
    w("")
    w("## Column provenance")
    w("")
    w("- `monthly.csv`, `annual.csv`: MoF monthb1 to monthb4, re-laid out and summed; the amounts are the file's integers in ¥100 million. `file_total_net_100m_yen` is the file's own CY or FY Net cell.")
    w("- `questions.csv`: computed here from the monthly Net, acquisition and disposition cells, with exact fractions, rounded half away from zero when written.")
    w("- `boj_dates.csv`: the Bank of Japan statements named in its `url` column; `sha256` is of the cached PDF.")
    w("- `forecast_score.csv`: the rule registered in CALENDAR.tsv on %s, applied to the monthb3 Net cell." % REGISTERED_ON)
    w("- `pins.csv`, `checks.csv`: values the spec pins and the tests run on them.")
    w("")
    w("## The sign banner on MoF's English index page")
    w("")
    w("The English index page still describes the convention used before January 2014. The file's Note 2 says plus is net acquisition and minus is net disposition, and the files confirm the identity "
      "Net = Acquisition − Disposition. The banner is recorded here as stale and is never used in the code.")
    w("")
    w("## Related material, not an input")
    w("")
    w("The life insurers' hedge ratios (the project's FX list, item F9) and the yen-hedged Treasury carry file (`data/hedged_ust_yield/yen_summary.csv`) are related material. No number from either "
      "is used here, and no statistic joins them to this series.")
    w("")
    w("## Press reference points (information only)")
    w("")
    w("- Nikkei, 21 Feb 2023, gives the 2022 figure for Japanese life insurers as \"a bit over ¥11 trillion\" (C14 in `checks.csv`).")
    w("- The Japan Times, 8 Dec 2022, gives ¥1.9 trillion for November 2022 (C14).")
    w("")
    w("## Build decisions")
    w("")
    w("Choices made where the specification left one open, and the fixes made after the first build.")
    w("")
    for d in DECISIONS:
        w("- " + d)
    return "\n".join(out) + "\n"


def render_all(ctx, checks):
    log_rows = ctx["log_rows"]
    src = source_line(log_rows)
    out = {}
    out["monthly.csv"] = render_csv("monthly.csv", ctx["monthly"], src)
    out["annual.csv"] = render_csv("annual.csv", ctx["annual"], src)
    out["boj_dates.csv"] = render_csv("boj_dates.csv", ctx["boj"], src, extra_comments=("credit: Bank of Japan, Statement on Monetary Policy, on the dates shown",))
    out["questions.csv"] = render_csv("questions.csv", ctx["questions"], src)
    out["forecast_score.csv"] = render_csv("forecast_score.csv", ctx["forecast"], src)
    out["vintages.csv"] = render_csv("vintages.csv", ctx["vintage_rows"], src)
    out["revisions.csv"] = render_csv("revisions.csv", ctx["revisions"], src)
    out["checks.csv"] = render_csv("checks.csv", checks, "# source: input checks of bin/jp_life_foreign_bonds.py build against the files fetched (see fetch_log.csv)")
    out["pins.csv"] = render_csv("pins.csv", pins_rows(), src)
    out["README.md"] = render_readme(ctx)
    out["SOURCES.md"] = render_sources(ctx)
    for name in ("README.md", "SOURCES.md"):
        guard_text(name, out[name])
    return out


# ------------------------------------------------------------------------------------------------------------------------
# build
# ------------------------------------------------------------------------------------------------------------------------
HARD_EXEMPT = ("C08",)


def analyze(vints, log_rows, cache, today, calendar_path=CALENDAR_PATH):
    latest = {k: vints[k][0 if M("latest_is_first") else -1] for k in FILE_ORDER}
    p3 = latest["monthb3"].parsed
    if not p3.months:
        raise DataError("monthb3 has no published month")
    L = max(p3.months)
    label = "ltd_%s_L%s" % (latest["monthb3"].fu.isoformat(), ym_text(L))
    q = build_questions(p3, latest["monthb2"].parsed, L, label)
    ctx = dict(vints=vints, latest=latest, L=L, q=q, log_rows=log_rows, cache=cache, today=today)
    ctx["monthly"] = monthly_rows(latest)
    ctx["annual"] = annual_rows(latest)
    ctx["boj"] = boj_rows(cache)
    ctx["vintage_rows"] = vintage_rows(vints)
    ctx["revisions"] = revision_rows(vints)
    ctx["forecast"] = forecast_rows(vints["monthb3"], cache_dir=cache)
    ctx["calendar"] = calendar_state(calendar_path)
    ctx["questions"] = q.rows
    return ctx


def merge_question_rows(existing, rows):
    """Earlier runs stay beside the current one (same run_label is replaced)."""
    labels = {r[0] for r in rows}
    return [r for r in existing if r[0] not in labels] + rows


def write_outputs(texts, target):
    for name, text in texts.items():
        write_text(os.path.join(target, name), text)


def build(cache, out_dir, today=None, calendar_path=CALENDAR_PATH, say=print):
    cache = check_cache(cache, out_dir=out_dir)
    if M("stop_blocks_build") and (os.path.exists(os.path.join(cache, "STOP")) or os.path.exists(os.path.join(cache, "STOP_BOJ"))):
        raise Latched("a latch file exists in the cache")
    t0 = time.time()
    today = today or dt.datetime.now(dt.timezone.utc).date()
    _, log_rows = read_csv_rows(os.path.join(out_dir, "fetch_log.csv"))
    vints = load_cache(cache, log_rows)
    ctx = analyze(vints, log_rows, cache, today, calendar_path)
    _, old_q = read_csv_rows(os.path.join(out_dir, "questions.csv"))
    ctx["questions"] = merge_question_rows(old_q, ctx["q"].rows)
    checks = run_checks(ctx)
    t1, t2 = render_all(ctx, checks), render_all(ctx, checks)
    same = all(t1[k] == t2[k] for k in t1)
    checks.append(["C11", "Fixed output: the outputs rendered twice in this run have identical sha256 (the on-disk comparison is the second `build`)", "identical",
                   "identical" if same else "DIFFERENT: " + ", ".join(k for k in t1 if t1[k] != t2[k]), "PASS" if same else "FAIL"])
    checks.sort(key=lambda c: c[0])
    texts = render_all(ctx, checks)
    failed = [c for c in checks if c[4] == "FAIL" and c[0] not in HARD_EXEMPT]
    target = os.path.join(out_dir, "_FAILED") if (failed and not M("failed_to_committed")) else out_dir
    write_outputs(texts, target)
    ctx.update(checks=checks, failed=failed, target=target, texts=texts, seconds=time.time() - t0)
    return ctx


def report(ctx):
    q, L = ctx["q"], ctx["L"]
    out = ["%-5s %-5s %s" % (c[0], c[4], c[3][:200]) for c in ctx["checks"]]
    out.append("")
    out.append("== life insurers, long-term debt (monthb3 Final Update %s, latest published month %s); 100m yen, plus is net acquisition, minus is net disposition ==" % (
        ctx["latest"]["monthb3"].fu.isoformat(), ym_text(L)))
    for w, s, e in q.windows:
        x = q.ws[("life", w)]
        out.append("%-3s %s..%s (%d months): sum %s, mean %s, median %s, months with net disposition %d of %d (%s%%)" % (
            w, ym_text(x["ms"][0]), ym_text(x["ms"][-1]), x["n"], fint(x["sum_net"]), fmt_100m1(x["mean_net"]), fmt_100m1(x["median_net"]), x["n_neg"], x["n"],
            fmt_pct(x["share_neg"])))
    out.append("Q1 flag (W2 mean below W1 mean): %s" % ("fires" if q.q["q1_flag"] else "does not fire"))
    out.append("Q5 rolling 12-month net: %d sign change(s); minimum %s at %s; latest %s at %s" % (
        len(q.q["chg"]), fint(q.q["min"][1]), ym_text(q.q["min"][0]), fint(q.q["last_roll"][1]), ym_text(q.q["last_roll"][0])))
    for r in ctx["forecast"]:
        out.append("October 2026 rule (registered %s; point %s, low %s, high %s, 100m yen): vintage %s, print %s, status %s, of record %s" % (
            r[0], r[4], r[5], r[6], r[2], r[7] or "none", r[8], r[9]))
    out.append(REQUIRED)
    revised = sum(1 for r in ctx["revisions"] if r[8] == "revised")
    out.append("revisions.csv: %d row(s)%s" % (len(ctx["revisions"]), "; no revisions" if revised == 0 else "; %d revised" % revised))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# selftest: synthetic data only; each guard G1-G19 has a test, and every mutant of it must make that test fail
# ------------------------------------------------------------------------------------------------------------------------
class Checks:
    def __init__(self):
        self.items = []

    def ok(self, name, cond, detail=""):
        self.items.append((name, bool(cond), "" if cond else detail))

    def eq(self, name, got, want):
        self.ok(name, got == want, "got %r, want %r" % (got, want))

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

    def int(self, n):
        self.s = (self.s * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        return (self.s >> 33) % n


class FakeClock:
    def __init__(self, t=1_000_000.0):
        self.t = t

    def wall(self):
        return self.t

    def mono(self):
        return self.t

    def sleep(self, s):
        self.t += s


class FakeV:
    """A vintage as the forecast and revision code sees it."""

    def __init__(self, fu, sha, months, totals=None, parsed=None):
        self.fu, self.sha, self.months = fu, sha, months
        self.parsed = parsed
        if parsed is None:
            self.parsed = Parsed()
            self.parsed.months, self.parsed.totals = months, totals or {}
        self.key, self.nbytes, self.retrieved = "monthb3", 0, ""

    @property
    def label(self):
        return "%s_%s" % (self.fu.isoformat(), self.sha[:12])


MONTH_ABBR = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
# Japanese header cells (rows 4 to 7), attached to their block so they travel with it when a fixture reorders the blocks
JP_HDR = {
    4: {"designated_reporters_total": "各部門計", "public": "公的部門", "deposit_taking": "預金取扱機関",
        "other_sectors": "その他部門"},
    5: {"central_bank": "中央銀行", "general_govt": "一般政府", "banks_banking": "銀行等（銀行勘定）",
        "trust_banks_banking": "信託銀行（銀行勘定）", "other_financial": "その他金融機関",
        "others": "その他"},
    6: {"trust_accounts": "銀行等及び信託銀行（信託勘定）", "fi_firms": "金融商品取引業者",
        "life": "生命保険会社", "nonlife": "損害保険会社", "inv_trust": "投資信託委託会社等"},
    7: {"banks_trust": "銀行等（信託勘定）", "trust_banks_trust": "信託銀行（信託勘定）"},
}


def fx_cell(v):
    return "-" if v is None else format(v, ",")


def fx_csv(months, vals, order=None, title=None, fu_text="October 8, 2026", fu_col=18, jp_override=None, totals=None, blank_tail=True):
    """Text of a MoF-shaped file. vals(ym, code) -> (acq, disp, net) with None for '-'; totals = (keys, fn(kind, y, code) -> triple)."""
    order = list(order or REAL_ORDER)
    title = title or TITLES["monthb3"]
    R = [[""] * NCOLS for _ in range(HDR_ROW + 1)]
    R[0][0], R[0][fu_col] = "投資家部門別対外証券投資", "最終更新日  令和8年10月8日"
    R[1][0], R[1][fu_col] = title, "Final Update  " + fu_text
    R[2][52], R[3][52] = "（単位：億円）", "（Unit: 100 mil Yen）"
    raw = {c: (r, row) for _, c, r, row in LABELS}
    for k, code in enumerate(order):
        col = 3 + 3 * k
        txt, row = raw[code]
        R[row][col] = txt
        for r2, d in JP_HDR.items():
            if code in d:
                R[r2][col] = d[code]
        R[9][col:col + 3] = ["取得", "処分", "ネット"]
        R[10][col:col + 3] = ["Acquisition", "Disposition", "Net"]
    rows = list(R)
    allm = list(months)
    if blank_tail and allm:
        allm += ym_range(ym_next(allm[-1]), (allm[-1][0], 12))
    pub = set(months)
    for ym in allm:
        r = [""] * NCOLS
        r[0] = str(ym[0]) if ym[1] == 1 else ""
        r[1] = (jp_override or {}).get(ym, "%d月" % ym[1])
        r[2] = MONTH_ABBR[ym[1] - 1]
        if ym in pub:
            for k, code in enumerate(order):
                for j, v in enumerate(vals(ym, code)):
                    r[3 + 3 * k + j] = fx_cell(v)
        rows.append(r)
    if totals:
        keys, fn = totals
        for kind, y in keys:
            r = [""] * NCOLS
            r[0] = ("%d年(1月～12月）  %dCY" % (y, y)) if kind == "CY" else ("%d年4月～%d年3月  %dFY" % (y, y + 1, y))
            for k, code in enumerate(order):
                for j, v in enumerate(fn(kind, y, code)):
                    r[3 + 3 * k + j] = fx_cell(v)
            rows.append(r)
    rows.append([""] * NCOLS)
    for note in (["（備考）", "①", "四捨五入のため、合計に合わないことがある。"],
                 ["", "  (Note 1)", "Totals may not add due to rounding."],
                 ["", "  (Note 2)", "International Transactions in Securities show net aquisition with a plus sign and net disposition with a minus sign."]):
        r = [""] * NCOLS
        r[:3] = note
        rows.append(r)
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    for r in rows:
        w.writerow(r)
    return out.getvalue()


def fx_parse(months, vals, min_month_rows=1, **kw):
    return parse_mof(fx_csv(months, vals, **kw).encode("cp932"), min_month_rows=min_month_rows)


def tri_add(*ts):
    if any(t[0] is None for t in ts):
        return (None, None, None)
    return tuple(sum(t[i] for t in ts) for i in range(3))


_SYN = {}


def synth_data(first=(2005, 1), last=(2026, 9), seed=7):
    """Four files' worth of exact synthetic cells: net = acquisition - disposition, parents are exact sums, b1 = b2 + b3 + b4. {file: {ym: {code: triple}}}"""
    key = (first, last, seed)
    if key in _SYN:
        return _SYN[key]
    g = Lcg(seed)
    data = {k: {} for k in FILE_ORDER}

    def lf():
        a, d = 500 + g.int(5000), 500 + g.int(5000)
        return (a, d, a - d)
    for ym in ym_range(first, last):
        per = {}
        for k in ("monthb2", "monthb3", "monthb4"):
            c = {n: lf() for n in ("banks_banking", "trust_banks_banking", "fi_firms", "life", "nonlife", "inv_trust", "others")}
            if ym >= BREAK_2014:
                for n in MISSING_PRE2014:
                    c[n] = lf()
                c["public"] = tri_add(c["central_bank"], c["general_govt"])
                c["trust_accounts"] = tri_add(c["banks_trust"], c["trust_banks_trust"])
            else:
                for n in MISSING_PRE2014:
                    c[n] = (None, None, None)
                c["public"], c["trust_accounts"] = lf(), lf()
            c["deposit_taking"] = tri_add(c["banks_banking"], c["trust_banks_banking"])
            c["other_financial"] = tri_add(c["trust_accounts"], c["fi_firms"], c["life"], c["nonlife"], c["inv_trust"])
            c["other_sectors"] = tri_add(c["other_financial"], c["others"])
            c[TOTAL] = tri_add(c["public"], c["deposit_taking"], c["other_sectors"])
            per[k] = c
        for k in ("monthb2", "monthb3", "monthb4"):
            data[k][ym] = per[k]
        data["monthb1"][ym] = {c: tri_add(per["monthb2"][c], per["monthb3"][c], per["monthb4"][c]) for c in CODES}
    _SYN[key] = data
    return data


def synth_totals(months_data):
    keys, tot = [], {}
    ys = sorted({y for y, _ in months_data})
    for y in ys:
        for kind, ms in (("CY", [(y, m) for m in range(1, 13)]), ("FY", ym_range((y, 4), (y + 1, 3)))):
            if all(m in months_data for m in ms):
                keys.append((kind, y))
                tot[(kind, y)] = {c: tri_add(*[months_data[m][c] for m in ms]) for c in CODES}
    return keys, (lambda kind, y, code: tot[(kind, y)][code])


_SYN_BYTES = {}


def synth_bytes(key, fu_text="August 7, 2026", first=(2005, 1), last=(2026, 9), tweak=None):
    ck_ = (key, fu_text, first, last)
    if tweak is None and ck_ in _SYN_BYTES:
        return _SYN_BYTES[ck_]
    md = synth_data(first, last)[key]
    vals = (lambda ym, code: md[ym][code]) if tweak is None else (lambda ym, code: tweak(ym, code, md[ym][code]))
    text = fx_csv(sorted(md), vals, title=TITLES[key], fu_text=fu_text, fu_col=19 if key == "monthb4" else 18, totals=synth_totals(md))
    b = text.encode("cp932")
    if tweak is None:
        _SYN_BYTES[ck_] = b
    return b


def synth_cache(tmp, fu_text="August 7, 2026", tweaks=None):
    cache = os.path.join(tmp, "cache")
    for k in FILE_ORDER:
        body = synth_bytes(k, fu_text=fu_text, tweak=(tweaks or {}).get(k))
        save_vintage(cache, k, body, parse_mof(body).fu)
    return cache


CAL_FIXTURE = ("2026-11-10\tPRE-REGISTERED 19 Oct. MoF monthb3.csv, Life Insurance Companies, OCTOBER 2026. Rule: the 24 monthly nets. "
               "POINT -¥78.2bn; RANGE -¥288.6bn to +¥74.6bn (both edges are historical months). FALSIFIED IF below or above.\tclaim\tsource\tOPEN\n")
TODAY = dt.date(2026, 10, 19)


def synth_build(tmp, tweaks=None, fu_text="August 7, 2026", cal=True, stop=False):
    cache = synth_cache(tmp, fu_text=fu_text, tweaks=tweaks)
    out = os.path.join(tmp, "out")
    os.makedirs(out, exist_ok=True)
    calp = os.path.join(tmp, "CALENDAR.tsv")
    with open(calp, "w", encoding="utf-8") as fh:
        fh.write("date\titem\tx\ty\tz\n" + (CAL_FIXTURE if cal else ""))
    if stop:
        for n in ("STOP", "STOP_BOJ"):
            with open(os.path.join(cache, n), "w", encoding="utf-8") as fh:
                fh.write("test\n")
    return build(cache, out, today=TODAY, calendar_path=calp), cache, out


_SYN_TEXTS = {}


def synth_texts():
    """The committed texts of an unmutated synthetic build, made once."""
    if not _SYN_TEXTS:
        if _ACTIVE:
            raise RuntimeError("the clean synthetic build must be made with no mutant active")
        tmp = tempfile.mkdtemp(prefix="jpst_")
        ctx, _, _ = synth_build(tmp)
        _SYN_TEXTS.update(ctx["texts"])
        _SYN_TEXTS["_ctx"] = ctx
    return _SYN_TEXTS


def synth_clean_folder():
    d = tempfile.mkdtemp(prefix="jpst_")
    t = synth_texts()
    for name in COMMITTED_NAMES:
        if name == "fetch_log.csv":
            write_text(os.path.join(d, name), render_csv(name, [], "# source: " + CITATION % (MOF_URL, "(no logged retrieval)")))
        else:
            write_text(os.path.join(d, name), t[name])
    return d


def mk_parsed(key, first, last, seed=7):
    """A fresh Parsed (deep copy) from the synthetic data, for tests that edit cells."""
    p = Parsed()
    for ym, d in synth_data(first, last, seed)[key].items():
        p.months[ym] = {c: tuple(t) for c, t in d.items()}
    p.codes = REAL_ORDER
    return p


# ---- the tests --------------------------------------------------------------------------------------------------------
def t_g1(ck):
    order = list(REAL_ORDER)
    order = order[5:] + order[:5]
    order[0], order[10] = order[10], order[0]
    months = ym_range((2013, 1), (2013, 3))

    def vals(ym, code):
        base = 100000 * CODES.index(code) + 100 * ym[1]
        return (base + 1, base + 2, base - 1)
    text = fx_csv(months, vals, order=order)
    ck.ok("the fixture carries the real full-width raw labels", all(rawc in text for _, _, rawc, _ in LABELS), "a raw label is missing")
    for fu_col, key in ((18, "monthb3"), (19, "monthb4")):
        p = parse_mof(fx_csv(months, vals, order=order, title=TITLES[key], fu_col=fu_col).encode("cp932"), title=TITLES[key], min_month_rows=3)
        ck.eq("%s: the 17 blocks are read by label, in the file's order" % key, list(p.codes), order)
        ck.ok("%s: every sector's three cells arrive from its own block" % key, all(p.months[ym][c] == vals(ym, c) for ym in months for c in CODES), "values differ")
        ck.eq("%s: Final Update found by text (column %d)" % (key, fu_col), p.fu, dt.date(2026, 10, 8))
    bad = fx_csv(months, vals).replace("Life Insurance Companies", "Life Insurance Companies2")
    ck.raises("a label that is not exactly one of the 17 is refused", DataError, lambda: parse_mof(bad.encode("cp932"), min_month_rows=1))


def t_g2(ck):
    months = ym_range((2013, 1), (2013, 6))
    vals = lambda ym, code: (CODES.index(code) * 10 + ym[1], 1, 2)
    p = parse_mof(fx_csv(months, vals, jp_override={(2013, 4): "３月"}).encode("cp932"), min_month_rows=6)
    ck.eq("the output follows the English column: months Jan to Jun", sorted(p.months), months)
    ck.eq("the row with the English month Apr is April", p.months[(2013, 4)]["life"][0], vals((2013, 4), "life")[0])
    ck.eq("the disagreement is recorded", len(p.jp_disagree), 1)


def t_g3(ck):
    months = ym_range((2012, 1), (2013, 6))
    p = fx_parse(months, lambda ym, code: (ym[0] + ym[1], 1, 2), min_month_rows=18)
    ck.eq("the year, written on January only, is carried to every month", sorted(p.months), months)
    ck.eq("a February row carries its year", p.months[(2013, 2)]["life"][0], 2015)


def t_g4(ck):
    months = ym_range((2013, 1), (2014, 3))

    def vals(ym, code):
        if ym < BREAK_2014 and code in MISSING_PRE2014:
            return (None, None, None)
        return (100 + ym[1], 50, 50 + ym[1])
    p = fx_parse(months, vals, min_month_rows=15)
    ck.eq("a dash before 2014 is a missing cell, not zero", p.months[(2013, 6)]["central_bank"], (None, None, None))
    ck.eq("the same sector is published from 2014", p.months[(2014, 1)]["central_bank"], (101, 50, 51))
    ck.eq("144 missing cells in 12 months (4 sectors x 3 fields x 12)", missing_pattern(p)["dash"], 144)


def t_g5(ck):
    months = ym_range((2024, 1), (2026, 9))
    idx = lambda ym: len(ym_range((2024, 1), ym))
    vals = lambda ym, code: (1000 + 3 * idx(ym), 1000 + 2 * idx(ym), idx(ym))
    p = fx_parse(months, vals, min_month_rows=33)
    ck.eq("33 published months", len(p.months), 33)
    ck.eq("October to December are blank and never a month", p.blank, [(2026, 10), (2026, 11), (2026, 12)])
    ck.ok("no blank month has a cell", all(ym not in p.months for ym in p.blank), "a blank month was read")
    rows = forecast_rows([FakeV(dt.date(2026, 10, 8), "a" * 64, p.months)])
    ck.eq("October is PENDING while it is blank", [r[8] for r in rows], ["PENDING"])
    L = max(p.months)
    s = win_stats(p, "life", (2024, 3), L)
    ck.eq("W2 keeps 31 months with three trailing blank rows", s["n"], 31)
    ck.eq("and its mean is unchanged (the nets 3 to 33 average 18)", s["mean_net"], Fraction(18))


def t_g6(ck):
    months = ym_range((2013, 1), (2014, 12))

    def clean(ym, code):
        if ym < BREAK_2014 and code in MISSING_PRE2014:
            return (None, None, None)
        ci = CODES.index(code)
        a, d = 3000 + 37 * ci + 11 * ym[1], 1000 + 53 * ci + 7 * ym[1]
        return (a, d, a - d)

    def old(ym, code):
        t = clean(ym, code)
        return (t[0], t[1], t[1] - t[0]) if ym < BREAK_2014 and t[0] is not None else t
    p = fx_parse(months, clean, min_month_rows=24)
    ck.eq("the clean fixture passes the identity", sign_violations(sign_check(p)), [])
    ck.eq("acquisition and disposition are read in their own columns", p.months[(2014, 3)]["life"][:2], clean((2014, 3), "life")[:2])
    ck.ok("pre-2014 nets on the old sign (plus is disposition) are flagged", bool(sign_violations(sign_check(fx_parse(months, old, min_month_rows=24)))), "not flagged")
    for tag, ym, off, want in (("post-2014 gap 1 passes", (2014, 5), 1, False), ("post-2014 gap 2 is flagged", (2014, 5), 2, True),
                               ("pre-2014 gap 4 passes", (2013, 5), 4, False), ("pre-2014 gap 5 is flagged", (2013, 5), 5, True)):
        q = fx_parse(months, clean, min_month_rows=24)
        a, d, n = q.months[ym]["life"]
        q.months[ym]["life"] = (a, d, n + off)
        ck.eq(tag, bool(sign_violations(sign_check(q))), want)


def t_g7(ck):
    months = ym_range((2012, 1), (2013, 12))
    vals = lambda ym, code: (100 * ym[0] + ym[1], 7, 100 * ym[0] + ym[1] - 7)
    keys = [("CY", 2012), ("CY", 2013), ("FY", 2012)]
    p = fx_parse(months, vals, totals=(keys, lambda kind, y, code: (999999, 1, 999998)), min_month_rows=24)
    ck.eq("24 months, no total row among them", sorted(p.months), months)
    ck.eq("December 2012 is the December row, not the 2012CY row", p.months[(2012, 12)]["life"][0], vals((2012, 12), "life")[0])
    ck.eq("the CY and FY rows are kept as totals", sorted(p.totals), keys)


def t_g8(ck):
    months = ym_range((2012, 1), (2014, 12))
    vals = lambda ym, code: ((100 + CODES.index(code)) * 10 + ym[1] + 12 * (ym[0] - 2012), 5 + ym[1], (100 + CODES.index(code)) * 10 + ym[1] + 12 * (ym[0] - 2012) - 5 - ym[1])
    md = {ym: {c: vals(ym, c) for c in CODES} for ym in months}
    keys = [("CY", 2012), ("CY", 2013), ("FY", 2012), ("FY", 2013)]
    tot = {}
    for kind, y in keys:
        ms = [(y, m) for m in range(1, 13)] if kind == "CY" else ym_range((y, 4), (y + 1, 3))
        tot[(kind, y)] = {c: tri_add(*[md[m][c] for m in ms]) for c in CODES}
    mk = lambda: fx_parse(months, vals, totals=(keys, lambda kind, y, code: tot[(kind, y)][code]), min_month_rows=36)
    p = mk()
    res = annual_check(p)
    ck.eq("exact totals: no violation", res["violations"], [])
    ck.eq("four periods are compared (CY2012, CY2013, FY2012, FY2013)", res["periods"], 4)
    for gap, want in ((12, False), (13, True)):
        q = mk()
        a, d, n = q.totals[("FY", 2012)]["life"]
        q.totals[("FY", 2012)]["life"] = (a, d, n + gap)
        ck.eq("a gap of %d in an FY cell %s" % (gap, "is flagged" if want else "passes"), bool(annual_check(q)["violations"]), want)
    latest = {k: FakeV(dt.date(2026, 10, 8), "b" * 64, p.months, parsed=p) for k in FILE_ORDER}
    rows = annual_rows(latest)
    life = {(r[0], r[1]): r for r in rows if r[3] == "ltd" and r[4] == "life"}
    fy13 = sum(md[m]["life"][2] for m in ym_range((2013, 4), (2014, 3)))
    cy13 = sum(md[(2013, m)]["life"][2] for m in range(1, 13))
    ck.eq("FY2013 sums April 2013 to March 2014", life[("FY", "2013")][8], fy13)
    ck.eq("CY2013 sums January to December", life[("CY", "2013")][8], cy13)
    ck.eq("FY2013 is basis mixed_2013_2014", life[("FY", "2013")][2], "mixed_2013_2014")
    ck.eq("FY2012 and CY2013 are old_to_2013", (life[("FY", "2012")][2], life[("CY", "2013")][2]), ("old_to_2013", "old_to_2013"))
    ck.eq("the file's cell and the difference sit beside the sum", (life[("FY", "2013")][9], life[("FY", "2013")][10]), (str(fy13), 0))
    ck.eq("2007 is mixed_2007 for CY and FY", (annual_basis("CY", 2007), annual_basis("FY", 2007)), ("mixed_2007", "mixed_2007"))
    ck.eq("CY and FY from 2014 are new_from_2014", (annual_basis("CY", 2014), annual_basis("FY", 2014)), ("new_from_2014", "new_from_2014"))
    ytd = {k: ms for k, ms in ytd_periods((2027, 2))}
    ck.eq("L = 2027-02: CY_YTD is January and February", ytd.get("CY_YTD"), [(2027, 1), (2027, 2)])
    ck.eq("L = 2027-02: FY_YTD starts in April 2026", (ytd.get("FY_YTD") or [None])[0], (2026, 4))
    ck.eq("L = 2027-02: FY_YTD has 11 months", len(ytd.get("FY_YTD") or []), 11)
    y9 = {k: ms for k, ms in ytd_periods((2026, 9))}
    ck.eq("L = 2026-09: CY_YTD 2026-01..09 and FY_YTD 2026-04..09", (y9["CY_YTD"][0], y9["CY_YTD"][-1], y9["FY_YTD"][0], y9["FY_YTD"][-1]),
          ((2026, 1), (2026, 9), (2026, 4), (2026, 9)))
    ck.eq("L = December: no CY_YTD", sorted(k for k, _ in ytd_periods((2026, 12))), ["FY_YTD"])
    ck.eq("L = March: no FY_YTD", sorted(k for k, _ in ytd_periods((2027, 3))), ["CY_YTD"])


def syn_small():
    return {k: mk_parsed(k, (2013, 6), (2014, 6)) for k in FILE_ORDER}


def t_g9(ck):
    fu = dt.date(2026, 10, 8)
    ps = syn_small()
    for k in FILE_ORDER:
        ck.eq("%s: clean within-file additivity" % k, within_additivity(ps[k])[1], [])
    cres = cross_additivity(ps)
    ck.eq("clean cross-file additivity: no violation", cres["violations"], [])
    ck.eq("clean cross-file status with equal Final Update dates", cross_status(cres, [fu] * 4), "PASS")
    p3 = syn_small()["monthb3"]
    for ym, d in p3.months.items():
        a, dd, n = d["life"]
        d["life"] = (dd, n, a)
    ck.ok("a one-column offset in one sector is caught by within-file additivity", bool(within_additivity(p3)[1]), "not caught")

    def bump(code, field, by, ym=(2014, 1)):
        q = syn_small()
        t = list(q["monthb1"].months[ym][code])
        t[field] += by
        q["monthb1"].months[ym][code] = tuple(t)
        return cross_additivity(q)
    ck.ok("a cross-file gap of 5 in a non-committed sector is caught", bool(bump("others", 0, 5)["violations"]), "passed")
    ck.ok("a gap of 4 in a non-committed sector passes", not bump("others", 0, 4)["violations"], "flagged")
    ck.ok("a gap of 3 in a committed sector is caught", bool(bump("life", 0, 3)["violations"]), "passed")
    ck.ok("a gap of 2 in a committed sector passes", not bump("life", 0, 2)["violations"], "flagged")
    bad = bump("life", 0, 3)
    ck.eq("different Final Update dates give WARN, not FAIL", cross_status(bad, [fu, fu, dt.date(2026, 9, 8), fu]), "WARN")
    ck.eq("equal dates and a violation give FAIL", cross_status(bad, [fu] * 4), "FAIL")


def t_g10(ck):
    ck.eq("the 24 base months are 2024-10 to 2026-09", (len(base_months()), base_months()[0], base_months()[-1]), (24, (2024, 10), (2026, 9)))
    band = band_of(list(BASE_PINS))
    ck.eq("the 24 pins give point -782, low -2,886, high +746", (band[1], band[0], band[2]), (-782, -2886, 746))
    ck.eq("REGISTERED is (low, point, high) = (-2886, -782, 746)", registered(), (-2886, -782, 746))
    nets = [-50, -40, -30, -20, -19, -18, -17, -16, -15, -14, -13, -7, -6, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    b = band_of(nets)
    ck.eq("a half-integer median is exact: (-7 + -6) / 2", b[1], Fraction(-13, 2))
    ck.eq("low is the 3rd and high the 22nd order statistic", (b[0], b[2]), (-30, 9))
    ck.raises("23 values are refused", DataError, lambda: band_of(nets[:23]))
    ck.eq("-2.5 in 100m yen prints -0.3 yen billion (half away from zero)", fmt_bn(Fraction(-5, 2)), "-0.3")
    ck.eq("+2.5 prints 0.3", fmt_bn(Fraction(5, 2)), "0.3")
    ck.eq("-0.05 yen billion prints -0.1", fmt_dec(Fraction(-1, 20), 1), "-0.1")
    ck.eq("a value that rounds to zero has no sign", fmt_dec(Fraction(-1, 100), 1), "0.0")
    ck.eq("-1,239.0 in 100m yen is -123.9 yen billion", fmt_bn(Fraction(-12390, 10)), "-123.9")


def t_g11(ck):
    ck.eq("the Net cell -2,886 is INSIDE (edge inclusive; acquisition minus disposition would be -2,887)", score_status(-2886, 5487, 8374), "INSIDE")
    ck.eq("+746 is INSIDE", score_status(746, 1000, 254), "INSIDE")
    ck.eq("-2,887 is BELOW", score_status(-2887, 0, 0), "BELOW")
    ck.eq("+747 is ABOVE", score_status(747, 0, 0), "ABOVE")
    ck.eq("a print of -2,000 in 100m yen is INSIDE (not read as yen billion)", score_status(-2000, 0, 2000), "INSIDE")
    v = FakeV(dt.date(2026, 11, 10), "c" * 64, {**fx_base_months(), TARGET: {"life": (5487, 8374, -2886)}})
    rows = forecast_rows([v])
    ck.eq("end to end: the Net cell of the 10 Nov vintage is scored", (rows[0][7], rows[0][8], rows[0][9]), ("-2886", "INSIDE", "yes"))


def fx_base_months(nets=BASE_PINS):
    return {ym: {"life": (n + 1000, 1000, n)} for ym, n in zip(ym_range(BASE_FIRST, BASE_LAST), nets)}


def t_g12(ck):
    ck.eq("REGISTERED equals the registered point and range", registered(), (-2886, -782, 746))
    state, reg = ("present", parse_calendar_registration(CAL_FIXTURE))
    ck.eq("the CALENDAR text carries point -78.2bn and range -288.6bn to +74.6bn", calendar_status(state, reg), "PASS")
    wrong = parse_calendar_registration(CAL_FIXTURE.replace("-¥288.6bn", "-¥288.5bn"))
    ck.eq("a different range is a FAIL", calendar_status("present", wrong), "FAIL")
    ck.eq("an absent row is a WARN", calendar_status("absent", None), "WARN")
    d = tempfile.mkdtemp(prefix="jpst_")
    with open(os.path.join(d, "c.tsv"), "w", encoding="utf-8") as fh:
        fh.write("2026-11-10\tother row without the file\n" + CAL_FIXTURE)
    st = calendar_state(os.path.join(d, "c.tsv"))
    ck.eq("calendar_state reads the row", calendar_status(*st), "PASS")
    base = fx_base_months()
    sha = lambda c: c * 64
    with_oct = lambda net, acq=0, disp=0, b=None: {**(b if b is not None else base), TARGET: {"life": (acq, disp, net)}}
    r = forecast_rows([FakeV(dt.date(2026, 10, 8), sha("a"), base)])
    ck.eq("no October: one PENDING row, not of record", (len(r), r[0][8], r[0][9], r[0][7]), (1, "PENDING", "no", ""))
    r = forecast_rows([FakeV(dt.date(2026, 10, 8), sha("a"), base), FakeV(dt.date(2026, 11, 10), sha("b"), with_oct(-2886))])
    ck.eq("the 10 Nov vintage is scored and of record", (len(r), r[0][8], r[0][9]), (1, "INSIDE", "yes"))
    r = forecast_rows([FakeV(dt.date(2026, 12, 8), sha("c"), with_oct(-100))])
    ck.eq("a vintage with Final Update 2026-12-08 is LATE_VINTAGE and not of record", (r[0][8], r[0][9], r[0][7]), ("LATE_VINTAGE", "no", "-100"))
    r = forecast_rows([FakeV(dt.date(2026, 11, 10), sha("b"), with_oct(-2886)), FakeV(dt.date(2026, 12, 8), sha("c"), with_oct(-3000))])
    ck.eq("a later vintage adds a row of record no and is never re-scored", [(x[8], x[9], x[7]) for x in r], [("INSIDE", "yes", "-2886"), ("LATE_VINTAGE", "no", "-3000")])
    revised = list(BASE_PINS)
    revised[23] = -2000
    r = forecast_rows([FakeV(dt.date(2026, 11, 10), sha("b"), with_oct(-2886, b=fx_base_months(revised)))])
    ck.eq("a revised base month: the score stays on the registered band", (r[0][8], r[0][9]), ("INSIDE", "yes"))
    ck.eq("and the recomputed band (low -2543, point, high) is information only", (r[0][10], r[0][12]), ("-2543", "746"))


def mk_vint_pair():
    old = {(2026, 8): {"life": (10, 5, 5), "banks_banking": (20, 10, 10), "fi_firms": (7, 3, 4)},
           (2026, 9): {"life": (11, 5, 6), "banks_banking": (21, 10, 11), "fi_firms": (7, 3, 4)}}
    new = {(2026, 8): {"life": (10, 5, 5), "banks_banking": (20, 9, 11), "fi_firms": (7, 3, 5)},
           (2026, 9): {"life": (11, 5, 6), "banks_banking": (21, 10, 11), "fi_firms": (7, 3, 4)},
           (2026, 10): {"life": (12, 6, 6), "banks_banking": (22, 10, 12), "fi_firms": (7, 3, 4)}}
    ot = {("CY", 2025): {"life": (100, 50, 50), "banks_banking": (1, 1, 0), "fi_firms": (1, 1, 0)}}
    nt = {("CY", 2025): {"life": (100, 50, 51), "banks_banking": (1, 1, 0), "fi_firms": (2, 1, 1)}}
    return FakeV(dt.date(2026, 10, 8), "d" * 64, old, ot), FakeV(dt.date(2026, 11, 10), "e" * 64, new, nt)


def t_g13(ck):
    a, b = mk_vint_pair()
    rows = vintage_diff("monthb3", a, b)
    kinds = {(r[3], r[4], r[5]): r[8] for r in rows}
    ck.eq("a changed cell in a total row is found (CY 2025 life net)", kinds.get(("2025CY", "life", "net")), "revised")
    ck.eq("a month that goes from blank to a number is new, not revised (October life net)", kinds.get(("2026-10", "life", "net")), "new")
    ck.eq("a revised month cell is revised (August banks disposition)", kinds.get(("2026-08", "banks_banking", "disposition")), "revised")
    ck.ok("a revision in fi_firms (not a committed sector) is not written", not any(r[4] == "fi_firms" for r in rows), "fi_firms present")
    ck.eq("old and new values are kept", [(r[6], r[7]) for r in rows if r[3] == "2026-08" and r[5] == "disposition"], [("10", "9")])
    ck.eq("vintage labels name the Final Update date", (rows[0][1][:10], rows[0][2][:10]), ("2026-10-08", "2026-11-10"))
    c = tempfile.mkdtemp(prefix="jpst_")
    body = synth_bytes("monthb3")
    fu = parse_mof(body).fu
    r1 = save_vintage(c, "monthb3", body, fu)
    r2 = save_vintage(c, "monthb3", body, fu)
    r3 = save_vintage(c, "monthb3", body + b"\n", fu)
    ck.eq("a new body is saved", r1[0], "saved")
    ck.eq("an unchanged sha256 is not saved as a new vintage", r2[0], "unchanged")
    ck.eq("a changed body (same Final Update) is a new vintage", r3[0], "saved")
    ck.eq("two vintage files in the cache", len([f for f in os.listdir(c) if VINTAGE_RX.fullmatch(f)]), 2)


def t_g14(ck):
    for name in sorted(SPEC_ALLOW):
        ck.eq("%s: ALLOW equals the spec's list" % name, allowlist(name), [x.strip() for x in SPEC_ALLOW[name].split(",")])
    ck.eq("twelve committed names", len(COMMITTED_NAMES), 12)
    ck.ok("annual.csv carries basis", "basis" in allowlist("annual.csv"), "basis missing")
    src = "# source: x"
    ck.raises("a header with an extra column is refused", DataError, lambda: render_csv("pins.csv", [], src, header=PIN_COLS + ["extra"]))
    ck.raises("a header with a renamed column is refused", DataError, lambda: render_csv("pins.csv", [], src, header=PIN_COLS[:-1] + ["unit2"]))
    ck.raises("a header missing a column is refused", DataError, lambda: render_csv("pins.csv", [], src, header=PIN_COLS[:-1]))
    text = render_csv("pins.csv", [["a", "b", "c", "d", "e"]], src)
    ck.eq("the header is the first line that does not start with #", committed_header(text), ",".join(PIN_COLS))
    ck.raises("a row of the wrong width is refused", DataError, lambda: render_csv("pins.csv", [["a"]], src))
    ck.raises("a first line that is not a source line is refused", DataError, lambda: render_csv("pins.csv", [], "no source"))


def t_g15(ck):
    ck.eq("the required sentence passes", text_hits(REQUIRED), [])
    ck.ok("the required sentence plus 'because the hedged carry fell' fails", bool(text_hits(REQUIRED + " because the hedged carry fell")), "passed")
    ck.ok("'as hedging costs rose' fails", bool(text_hits("Purchases fell as hedging costs rose.")), "passed")
    ck.ok("a note saying 'life insurers sold' fails", bool(text_hits("life insurers sold")), "passed")
    ck.ok("'net sales' fails", bool(text_hits("a month of net sales")), "passed")
    ck.eq("the gloss 'sales, redemptions and other reductions' passes", text_hits("Disposition: sales, redemptions and other reductions in holdings (the file's term)."), [])
    for w in ("because", "due to", "in response to", "led to", "prompted", "pushed", "as a result of", "reaction", "reflecting", "amid", "owing to", "thanks to",
              "on the back of", "weighed", "caused", "drove", "driving", "as yields rose", "as the yen fell", "as it was rising", "as prices were falling"):
        ck.ok("the scanner sees %r" % w, bool(text_hits("the flow was " + w + " something")), "not seen")
    src = "# source: x"
    bad = "life insurers sold because of the carry"
    cases = (("forecast_score.csv", FORECAST_COLS, "note"), ("questions.csv", QUESTION_COLS, "notable"), ("boj_dates.csv", BOJ_COLS, "phrase"),
             ("boj_dates.csv", BOJ_COLS, "action"), ("checks.csv", CHECK_COLS, "description"), ("checks.csv", CHECK_COLS, "observed"),
             ("questions.csv", QUESTION_COLS, "statistic"))
    for name, cols, field in cases:
        row = ["x"] * len(cols)
        row[cols.index(field)] = bad
        ck.raises("%s %s: wording is refused at render time" % (name, field), DataError, lambda: render_csv(name, [row], src))
    ctx = synth_texts()["_ctx"]
    ck.eq("the generated README carries none", text_hits(synth_texts()["README.md"]), [])
    ck.eq("the generated SOURCES carries none", text_hits(synth_texts()["SOURCES.md"]), [])
    ck.eq("the printout carries none", text_hits("\n".join(report(ctx))), [])
    ck.ok("the README carries the required sentence", REQUIRED in synth_texts()["README.md"], "missing")
    ck.ok("the README says disposition includes redemptions", "redemptions of overseas government bonds are included, MoF FAQ A5" in synth_texts()["README.md"], "missing")
    ck.ok("the README never calls trust accounts or investment trusts pensions", "pension" not in synth_texts()["README.md"].lower(), "pension")


def fx_opener(overrides=None):
    mof = {k: synth_bytes(k) for k in FILE_ORDER}
    boj = {d: b"%PDF-1.4\n" + (("x" + d) * 4000).encode() for d, *_ in BOJ_ROWS}

    def opener(host, target, headers, timeout, cap):
        for r in request_table():
            if r["host"] == host and r["target"] == target:
                if overrides and r["key"] in overrides:
                    return overrides[r["key"]]
                return (200, mof[r["arg"]]) if r["kind"] == "mof" else (200, boj[r["arg"]])
        return 404, b""
    opener.boj_expect = {"boj" + d: sha256_of(b)[:16] for d, b in boj.items()}
    return opener


def fx_fetcher(tmp, opener, clock=None, **kw):
    clock = clock or FakeClock()
    return Fetcher(os.path.join(tmp, "cache"), os.path.join(tmp, "out"), opener=opener, wall=clock.wall, mono=clock.mono, sleeper=clock.sleep,
                   stop_path=os.path.join(tmp, "cache", "STOP"), stop_boj_path=os.path.join(tmp, "cache", "STOP_BOJ"),
                   now_utc=lambda: dt.datetime(2026, 10, 19, 12, 0, 0, tzinfo=dt.timezone.utc), root=os.path.join(tmp, "norepo"),
                   boj_expect=getattr(opener, "boj_expect", None), **kw), clock


def t_g16(ck):
    quiet = lambda *a: None
    req = {r["key"]: r for r in request_table()}
    mof0, boj0 = req["monthb3"], req["boj2013-04-04"]
    # an all-good run: 16 requests, MoF first, starts at least 2 s apart
    tmp = tempfile.mkdtemp(prefix="jpst_")
    clock = FakeClock()
    starts, hosts = [], []
    base = fx_opener()

    def timed(host, target, headers, timeout, cap):
        starts.append(clock.t)
        hosts.append(host)
        clock.t += 0.2
        ck.ok("the request carries the neutral identification string", headers["User-Agent"] == UA and chr(64) not in headers["User-Agent"])
        return base(host, target, headers, timeout, cap)
    timed.boj_expect = base.boj_expect
    fe, _ = fx_fetcher(tmp, timed, clock=clock)
    saved, bl = fetch_all(fe, request_table(), say=quiet)
    ck.eq("16 requests on a first run", fe.requests, 16)
    ck.eq("the four MoF files come first, then the twelve BoJ statements", hosts, [MOF_HOST] * 4 + [BOJ_HOST] * 12)
    gaps = [b - a for a, b in zip(starts, starts[1:])]
    ck.ok("request starts are at least 2 s apart", len(gaps) == 15 and min(gaps) >= 2.0, "gaps %s" % gaps[:4])
    ck.eq("16 files saved and no BoJ latch", (saved, bl), (16, None))
    ck.ok("neither latch exists after a clean run", not os.path.exists(fe.stop_path) and not os.path.exists(fe.stop_boj_path), "a latch exists")
    ck.eq("every request is logged", len(read_csv_rows(fe.log_path)[1]), 16)

    def fresh(opener, **kw):
        t = tempfile.mkdtemp(prefix="jpst_")
        return t, fx_fetcher(t, opener, **kw)[0]
    clock2 = FakeClock(t=dt.datetime(2026, 10, 19, 12, 0, 0, tzinfo=dt.timezone.utc).timestamp())
    t2, f2 = fresh(base, clock=clock2)
    fetch_all(f2, request_table(), say=quiet)
    n1 = f2.requests
    fetch_all(f2, request_table(), say=quiet)
    ck.eq("a second fetch on the same day makes no request (MoF files done today, BoJ files cached)", (n1, f2.requests), (16, 16))

    def latches(opener, req_, boj=False):
        t, f = fresh(opener)
        try:
            f.fetch_one(req_)
            return t, False
        except LatchedBoj:
            return t, "boj"
        except Latched:
            return t, "mof"
    for label, op in (("HTTP 403", lambda *a: (403, b"")), ("a redirect (301, not followed)", lambda *a: (301, b"")),
                      ("a 200 with the wrong title", lambda *a: (200, b"<html>Access denied</html>"))):
        t, got = latches(op, mof0)
        ck.eq("MoF: %s latches STOP" % label, got, "mof")
        ck.ok("MoF: %s writes STOP and not STOP_BOJ" % label, os.path.exists(os.path.join(t, "cache", "STOP")) and not os.path.exists(os.path.join(t, "cache", "STOP_BOJ")),
              "latch files wrong")
    t, f = fresh(lambda *a: (403, b""))
    ck.raises("MoF: the first failure raises Latched", Latched, lambda: f.fetch_one(mof0))
    ck.raises("while STOP exists the next MoF fetch refuses (and no request is made)", Latched, lambda: f.fetch_one(req["monthb1"]))
    ck.eq("only one request was made", f.requests, 1)
    t, got = latches(lambda *a: (403, b""), boj0)
    ck.eq("BoJ: a failure latches STOP_BOJ", got, "boj")
    ck.ok("BoJ: STOP_BOJ is written and STOP is not", os.path.exists(os.path.join(t, "cache", "STOP_BOJ")) and not os.path.exists(os.path.join(t, "cache", "STOP")),
          "wrong latch file")
    t, got = latches(lambda *a: (200, b"%PDF-1.4\n" + b"y" * 30000), boj0)
    ck.eq("BoJ: a PDF whose sha256 differs latches STOP_BOJ", got, "boj")
    # STOP_BOJ never gates a MoF fetch
    t, f = fresh(base)
    os.makedirs(os.path.join(t, "cache"), exist_ok=True)
    with open(os.path.join(t, "cache", "STOP_BOJ"), "w") as fh:
        fh.write("test\n")
    ck.eq("STOP_BOJ does not block a MoF fetch", f.fetch_one(mof0), "saved")
    ck.raises("STOP_BOJ blocks the BoJ part", LatchedBoj, lambda: f.fetch_one(boj0))
    ck.eq("scoring ignores STOP_BOJ", forecast_rows([FakeV(dt.date(2026, 11, 10), "b" * 64, {**fx_base_months(), TARGET: {"life": (0, 0, -2886)}})],
                                                 cache_dir=os.path.join(t, "cache"))[0][8], "INSIDE")
    # a BoJ failure ends only the BoJ part
    t, f = fresh(lambda host, target, h, to, cap: base(host, target, h, to, cap) if host == MOF_HOST else (403, b""))
    saved, bl = fetch_all(f, request_table(), say=quiet)
    ck.eq("a BoJ failure: the four MoF files are saved and the BoJ part ends after one request", (saved, f.requests), (4, 5))
    ck.ok("a BoJ failure leaves STOP_BOJ and no STOP", os.path.exists(os.path.join(t, "cache", "STOP_BOJ")) and not os.path.exists(os.path.join(t, "cache", "STOP")),
          "latch files wrong")
    # a socket fault ends the invocation without latching

    def sock(*a):
        raise SocketFault("timeout")
    t, f = fresh(sock)
    try:
        f.fetch_one(mof0)
        ck.ok("a socket fault ends the run", False, "no exception")
    except SocketFault:
        ck.ok("a socket fault ends the run", True)
        ck.ok("a socket fault does NOT latch", not os.path.exists(os.path.join(t, "cache", "STOP")), "latched")
    except Latched:
        ck.ok("a socket fault ends the run without latching", False, "latched")
    # hosts, paths, scheme
    ck.raises("FRED is refused", Refused, lambda: check_url("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2"))
    ck.raises("sec.gov is refused", Refused, lambda: check_url("https://www.sec.gov/cgi-bin/browse-edgar"))
    ck.raises("a path outside the table is refused", Refused, lambda: check_url("https://www.mof.go.jp/other.csv"))
    ck.raises("plain http is refused", Refused, lambda: check_url("http://www.mof.go.jp" + mof0["target"]))
    ck.eq("a table URL is accepted", check_url("https://www.mof.go.jp" + mof0["target"]), (MOF_HOST, mof0["target"]))
    ck.eq("the request table has 16 rows", len(request_table()), 16)
    # identification string
    at = chr(64)
    ck.raises("an address in the identification string is refused", Refused, lambda: assert_ua(UA + " x" + at + "y.org"))
    ck.ok("the identification string is the CLAUDE.md one and has no address", UA == "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
          and at not in UA)
    old = os.environ.get("SEC_UA")
    os.environ["SEC_UA"] = "ThirdDerivativeResearch/1.0"
    try:
        ck.raises("a configured contact value inside the string is refused", Refused, lambda: assert_ua(UA))
    finally:
        if old is None:
            os.environ.pop("SEC_UA", None)
        else:
            os.environ["SEC_UA"] = old
    # cap
    ck.raises("--max-requests 21 is refused", Refused, lambda: fx_fetcher(tempfile.mkdtemp(prefix="jpst_"), base, max_requests=21))
    ck.raises("--sleep under 2 s is refused", Refused, lambda: fx_fetcher(tempfile.mkdtemp(prefix="jpst_"), base, sleep=1.0))
    t, f = fresh(base, max_requests=2)
    f.fetch_one(mof0)
    f.fetch_one(req["monthb1"])
    ck.raises("the cap stops a third request", MaxRequests, lambda: f.fetch_one(req["monthb2"]))
    # latch files: nothing in this source removes, renames or writes over one
    ck.eq("no code path in this source deletes, renames or writes over a latch file", latch_scan(own_source()), [])
    ck.ok("the scan sees a planted os.remove(STOP_PATH)", bool(latch_scan("import os\ndef f():\n    os.remove(STOP_PATH)\n")), "not seen")
    ck.ok("the scan sees a planted write-open of STOP_BOJ", bool(latch_scan("def g():\n    open(STOP_BOJ_PATH, 'w')\n")), "not seen")
    ck.ok("the scan sees a planted rename", bool(latch_scan("import os\ndef g():\n    os.rename(p, STOP_PATH)\n")), "not seen")
    ck.eq("the latch writer's own exclusive open is the one allowed use", latch_scan("def _latch(self):\n    open(self.stop_path, 'x')\n"), [])
    t, f = fresh(base)
    os.makedirs(os.path.join(t, "cache"), exist_ok=True)
    with open(f.stop_path, "w") as fh:
        fh.write("keep\n")
    try:
        f._latch(False, "again")
    except Latched:
        pass
    with open(f.stop_path) as fh:
        ck.eq("an existing latch is never written over", fh.read(), "keep\n")
    ck.raises("a general writer refuses a latch path", Refused, lambda: write_text(f.stop_path, "x"))
    ck.raises("a general writer refuses STOP_BOJ too", Refused, lambda: write_text(f.stop_boj_path, "x"))


def t_g17(ck):
    def planted(fn):
        d = synth_clean_folder()
        fn(d)
        return commit_guard(d)

    def append(name, text):
        def f(d):
            with open(os.path.join(d, name), "a", encoding="utf-8") as fh:
                fh.write(text)
        return f

    def put(name, text):
        def f(d):
            with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
                fh.write(text)
        return f
    ck.eq("the clean folder passes", commit_guard(synth_clean_folder()), [])
    raw = synth_bytes("monthb3").decode("cp932")
    plants = (("(a) a planted raw monthb3.csv", put("monthb3.csv", raw)),
              ("(b) a file not on the name list", put("notes.txt", "x\n")),
              ("(c) a raw PDF", put("README.md", "%PDF-1.4\n1 0 obj\n")),
              ("(d) a checks.csv cell containing /Users/", append("checks.csv", "X1,/Users/someone/work,,,PASS\n")),
              ("(e) a pins.csv cell containing /private/tmp", append("pins.csv", "a,/private/tmp/x,c,d,e\n")),
              ("(f) a committed file containing an at sign", append("SOURCES.md", "mail " + chr(64) + "example\n")),
              ("(g) a csv whose second line is a MoF title", put("vintages.csv", "# source: x\n# " + TITLES["monthb3"] + "\n" + ",".join(VINTAGE_COLS) + "\n")),
              ("(h) a renamed header", put("annual.csv", "# source: x\n" + ",".join(c if c != "basis" else "bases" for c in ANNUAL_COLS) + "\n")))
    for label, fn in plants:
        ck.ok("the guard fails on %s" % label, bool(planted(fn)), "not detected")
    d = synth_clean_folder()
    os.makedirs(os.path.join(d, "_FAILED"))
    ck.ok("the guard fails on a directory", bool(commit_guard(d)), "not detected")


def t_g18(ck):
    p = parse_mof(synth_bytes("monthb3"), title=TITLES["monthb3"], min_month_rows=250)
    L = max(p.months)
    ck.eq("L is the latest published month, 2026-09, with three blank rows after it", (L, len(p.blank)), ((2026, 9), 3))
    got = {}
    for w, s, e in window_defs(L):
        st = win_stats(p, "life", s, e)
        got[w] = (st["n"], st["ms"][0], st["ms"][-1])
    ck.eq("W0: 60 months, 2014-01 to 2018-12", got["W0"], (60, (2014, 1), (2018, 12)))
    ck.eq("W1: 60 months, 2019-01 to 2023-12", got["W1"], (60, (2019, 1), (2023, 12)))
    ck.eq("W2: 31 months from 2024-03 to 2026-09", got["W2"], (31, (2024, 3), (2026, 9)))
    ck.eq("W2b: 30 months from 2024-04", got["W2b"], (30, (2024, 4), (2026, 9)))
    ck.ok("no pre-2014 month enters any window", all(v[1] >= (2014, 1) for v in got.values()), "a pre-2014 month")
    ck.eq("monthly.csv would hold 6 x 4 x 261 = 6,264 rows", 6 * 4 * len(p.months), 6264)


def t_g19(ck):
    def sums(**kw):
        d = {"life": (100, 80, 20), "fi_firms": (600, 500, 100), TOTAL: (1000, 800, 40), "other_financial": (400, 300, 10)}
        d.update(kw)
        return d
    get = lambda blk, sector, stat: next(v for s, st, v, u, den in blk if s == sector and st == stat)
    b = share_block(sums())
    ck.eq("life share of acquisitions is over designated_reporters_total (10.00%), not other_financial (25.00%)", get(b, "life", "share_gross_acquisitions"), "10.00")
    ck.eq("life share of dispositions", get(b, "life", "share_gross_dispositions"), "10.00")
    ck.eq("the dealers' share of acquisitions is reported beside it", get(b, "fi_firms", "share_gross_acquisitions"), "60.00")
    ck.ok("every share row is labelled 'share of reported gross contracts (dealer-inclusive)'",
          all("share of reported gross contracts (dealer-inclusive)" in den for s, st, v, u, den in b if st.startswith("share")), "label missing")
    ck.eq("same-sign net ratio 20 / 40 = 0.50", get(b, "life", "net_ratio_to_total"), "0.50")
    ck.eq("opposite-sign nets give the word opposite_sign", get(share_block(sums(life=(100, 180, -80))), "life", "net_ratio_to_total"), "opposite_sign")
    ck.eq("a ratio above 1 gives the word exceeds_total", get(share_block(sums(life=(100, 20, 80))), "life", "net_ratio_to_total"), "exceeds_total")
    ck.eq("a ratio of exactly 1 is printed", get(share_block(sums(life=(100, 60, 40))), "life", "net_ratio_to_total"), "1.00")
    ck.ok("no printed share is negative", all(not v.startswith("-") for s, st, v, u, den in share_block(sums(life=(100, 180, -80))) if st.startswith("share") or st == "net_ratio_to_total"),
          "negative share")


def x_cache(ck):
    tmp = tempfile.mkdtemp(prefix="jpst_")
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
    ck.ok("a cache outside the repo is accepted", check_cache(tempfile.mkdtemp(prefix="jpst_"), root=tmp, out_dir=out) is not None)


def x_failed(ck):
    tmp = tempfile.mkdtemp(prefix="jpst_")
    os.makedirs(os.path.join(tmp, "out"))
    with open(os.path.join(tmp, "out", "README.md"), "w") as fh:
        fh.write("committed\n")
    tweak = lambda ym, code, t: (t[0], t[1], t[2] + 5) if (ym == (2020, 3) and code == "life") else t
    ctx, cache, out = synth_build(tmp, tweaks={"monthb3": tweak})
    ck.ok("a hard FAIL (the sign identity) sends the outputs to _FAILED", ctx["target"].endswith("_FAILED") and os.path.exists(os.path.join(out, "_FAILED", "checks.csv")),
          "target %s" % ctx["target"])
    ck.ok("C04 is the FAIL", "C04" in [c[0] for c in ctx["failed"]], "failed: %s" % [c[0] for c in ctx["failed"]])
    with open(os.path.join(out, "README.md")) as fh:
        ck.eq("the committed README was left alone", fh.read(), "committed\n")


def x_fixed(ck):
    tmp = tempfile.mkdtemp(prefix="jpst_")
    ctx, cache, out = synth_build(tmp, stop=True)
    ck.eq("a build runs with STOP and STOP_BOJ in the cache", ctx["target"], out)
    ck.eq("monthly.csv has 6 x 4 x 261 = 6,264 rows", len(ctx["monthly"]), 6264)
    ck.eq("forecast_score says PENDING before 10 Nov", [r[8] for r in ctx["forecast"]], ["PENDING"])
    names = sorted(f for f in os.listdir(out) if os.path.isfile(os.path.join(out, f)))
    ck.eq("build writes the eleven committed files except fetch_log.csv", names, sorted(n for n in COMMITTED_NAMES if n != "fetch_log.csv"))
    h1 = {n: sha256_of(open(os.path.join(out, n), "rb").read()) for n in names}
    ctx2 = build(cache, out, today=TODAY, calendar_path=os.path.join(tmp, "CALENDAR.tsv"))
    h2 = {n: sha256_of(open(os.path.join(out, n), "rb").read()) for n in names}
    ck.eq("a second build leaves every sha256 unchanged", h2, h1)
    c11 = next(c for c in ctx["checks"] if c[0] == "C11")
    ck.eq("C11 passes", c11[4], "PASS")
    ck.eq("no check fails on the synthetic data (C08 is the BoJ files, which a synthetic cache does not hold)",
          sorted(c[0] for c in ctx["checks"] if c[4] == "FAIL"), ["C08"])


def x_oct8(ck):
    tmp = tempfile.mkdtemp(prefix="jpst_")
    ctx, cache, out = synth_build(tmp, fu_text="October 8, 2026")
    ids = [c[0] for c in ctx["failed"]]
    ck.ok("a vintage labelled 8 Oct 2026 whose base months differ from the pins fails C10", "C10" in ids, "failed: %s" % ids)
    ck.ok("and C01 (sha256 differs from the pinned file)", "C01" in ids, "failed: %s" % ids)
    ck.ok("and the outputs go to _FAILED", ctx["target"].endswith("_FAILED"), ctx["target"])


def x_c13(ck):
    P = C13
    n = {}
    for w in P["sum"]:
        n.update({"sum_" + w: P["sum"][w], "mean_" + w: P["mean"][w], "median_" + w: P["median"][w], "neg_" + w: P["neg"][w]})
    n.update(share_w2=P["share_w2"], share_w1=P["share_w1"], q2=P["q2"], flag=False, opposite_w2=["trust_accounts"], trust_w2_mean=P["trust_w2_mean"],
             q5_n=1, q5_first=((2020, 6), "to_negative", -2091), q5_min=((2023, 2), -131051), q5_last=((2026, 9), -21147), q6=dict(P["q6"]))
    for w in P["life_share"]:
        n.update({"life_share_" + w: P["life_share"][w], "dealer_acq_" + w: P["dealer_acq"][w], "total_net_" + w: P["total_net"][w], "ratio_" + w: P["ratio"][w]})
    rows = c13_expected_actual(n)
    ck.eq("the pinned window statistics are 7 check rows", [r[0] for r in rows], ["C13a", "C13b", "C13c", "C13d", "C13e", "C13f", "C13g"])
    ck.eq("numbers equal to the pins pass every C13 row", [r[4] for r in rows], [True] * 7)
    for key, val in (("sum_W2", -38409), ("share_w2", "74.20"), ("ratio_W0", "0.44"), ("opposite_w2", ["banks_banking", "trust_accounts"]), ("q5_n", 2)):
        m = dict(n)
        m[key] = val
        ck.ok("changing %s fails a C13 row" % key, not all(r[4] for r in c13_expected_actual(m)), "still passes")
    ck.eq("the Q1 flag firing fails C13b", [r[4] for r in c13_expected_actual(dict(n, flag=True))][1], False)
    p = parse_mof(synth_bytes("monthb3"), min_month_rows=250)
    ck.eq("C07: four sectors x 3 fields x 108 months of dashes before 2014 (324 per sector), none elsewhere", missing_pattern(p),
          dict(dash=C07_DASH, other=0, pre_published=0))
    ck.eq("C07 pin is 1,296 = 4 x 324", (C07_DASH, C07_DASH // 4), (1296, 324))


def x_readme(ck):
    ctx = synth_texts()["_ctx"]
    rd, so = render_readme(ctx), render_sources(ctx)
    q = ctx["q"]
    ck.ok("the decisions are not in the README", "Decisions where the specification left a choice" not in rd and "Fix after the first build" not in rd, "still there")
    ck.ok("SOURCES.md has a 'Build decisions' section", "\n## Build decisions\n" in so, "missing")
    ck.eq("both post-run fixes are in SOURCES.md word for word", [d in so for d in DECISIONS if d.startswith("Fix after the first build")], [True, True])
    ck.ok("every decision is in SOURCES.md", all("- " + d in so for d in DECISIONS), "missing")
    ck.ok("the README links SOURCES.md from Provenance", "Build decisions, including two fixes made after the first build, are listed in [SOURCES.md](SOURCES.md)." in rd, "missing")
    ck.ok("the windows are named before the annual table", rd.index("W0 is 2014 to 2018") < rd.index("| period type |"), "order")
    exp = "Life insurers' net, long-term debt: %s over W0 (%d of %d months of net disposition), %s over W1 (%d of %d) and %s over W2 (%d of %d)." % tuple(
        x for n in ("W0", "W1", "W2") for x in (trn(q.ws[("life", n)]["sum_net"]), q.ws[("life", n)]["n_neg"], q.ws[("life", n)]["n"]))
    ck.ok("the per-window sentence is computed from the same values as questions.csv", exp in rd, "not found")
    ck.eq("trillion yen: +190,365 (100m yen) is +19.04, -142,291 is -14.23, -38,408 is -3.84", [trn(190365), trn(-142291), trn(-38408)],
          ["+19.04 trillion yen", "\u221214.23 trillion yen", "\u22123.84 trillion yen"])
    ck.eq("neither file carries causal or sale wording", text_hits(rd) + text_hits(so), [])


def x_two_vintages(ck):
    tmp = tempfile.mkdtemp(prefix="jpst_")
    cache = synth_cache(tmp)
    out = os.path.join(tmp, "out")
    os.makedirs(out)
    calp = os.path.join(tmp, "CALENDAR.tsv")
    with open(calp, "w", encoding="utf-8") as fh:
        fh.write("date\titem\tx\ty\tz\n" + CAL_FIXTURE)
    build(cache, out, today=TODAY, calendar_path=calp)
    for k in FILE_ORDER:
        body = synth_bytes(k, fu_text="November 10, 2026", last=(2026, 10))
        save_vintage(cache, k, body, parse_mof(body).fu)
    ctx = build(cache, out, today=dt.date(2026, 11, 11), calendar_path=calp)
    oct_ = synth_data((2005, 1), (2026, 10))["monthb3"][TARGET]["life"]
    fc = ctx["forecast"]
    ck.eq("one forecast row, from the vintage with Final Update 2026-11-10", (len(fc), fc[0][2]), (1, "2026-11-10"))
    ck.eq("it is of record and scored on the Net cell", (fc[0][9], fc[0][7], fc[0][8]), ("yes", str(oct_[2]), score_status(oct_[2], oct_[0], oct_[1])))
    ck.ok("the synthetic base months differ from the pins, so the recomputed band is filled", fc[0][10] != "" and fc[0][12] != "", "blank")
    rev = ctx["revisions"]
    ck.eq("revisions.csv: October rows are new (6 sectors x 3 fields x 4 files), nothing revised", (len(rev), {r[8] for r in rev}), (72, {"new"}))
    ck.eq("the earlier run stays in questions.csv beside the new one", sorted({r[0] for r in ctx["questions"]}),
          ["ltd_2026-08-07_L2026-09", "ltd_2026-11-10_L2026-10"])
    ck.eq("the README states the new latest month", "latest published month 2026-10" in ctx["texts"]["README.md"], True)
    ck.eq("vintages.csv lists both vintages of each file", len(ctx["vintage_rows"]), 8)
    ck.ok("no check fails except C08 (no Bank of Japan files in the synthetic cache)", sorted(c[0] for c in ctx["checks"] if c[4] == "FAIL") == ["C08"],
          str([c[0] for c in ctx["checks"] if c[4] == "FAIL"]))


GUARDS = [
    ("G1", "blocks by label: NFKC, exact equality, Final Update by text", ["fixed_index_life", "substring_labels", "no_nfkc", "final_update_col18"], t_g1),
    ("G2", "month column: the English month governs", ["month_from_japanese"], t_g2),
    ("G3", "year carry: the year is written on January only", ["year_not_carried"], t_g3),
    ("G4", "missing marker: '-' is missing, never zero", ["dash_as_zero"], t_g4),
    ("G5", "unpublished months: blank rows never enter anything", ["blank_as_zero"], t_g5),
    ("G6", "sign: Net = Acquisition minus Disposition (within 1 from 2014, within 4 before)", ["sign_check_off", "sign_inverted", "swap_acq_disp"], t_g6),
    ("G7", "total rows: CY and FY rows are not months", ["total_as_month"], t_g7),
    ("G8", "annual sums, fiscal years and year to date", ["fy_as_calendar", "fy_label_end_year", "annual_gap_passes", "fy_ytd_wrong_start", "basis_fy2013_wrong"], t_g8),
    ("G9", "additivity: within files, across files, Final Update dates", ["within_off", "cross_tol_loose_noncommitted", "cross_tol_loose_committed", "fu_mismatch_fail"], t_g9),
    ("G10", "band and rounding: order statistics, exact fractions, half away from zero",
     ["band_2nd_23rd", "band_window_back", "band_window_fwd", "band_median23", "band_float", "py_round"], t_g10),
    ("G11", "scoring: the Net cell, edges inclusive, 100m yen", ["score_acq_minus_disp", "strict_edges", "print_in_bn"], t_g11),
    ("G12", "frozen registration: REGISTERED, CALENDAR text, of_record only for the 10 Nov file",
     ["registered_edited", "calendar_unmatched", "band_recomputed_scores", "rescore_later", "late_vintage_of_record"], t_g12),
    ("G13", "vintages and revisions", ["revisions_skip_totals", "blank_to_number_revised", "save_unchanged_vintage", "revisions_all_sectors"], t_g13),
    ("G14", "exact column allowlists, held twice", ["extra_column", "renamed_column", "allow_drift", "header_from_source_line", "annual_without_basis"], t_g14),
    ("G15", "wording: causal and sale words over every committed text", ["scan_off", "rx_base_only", "no_sold_ban"], t_g15),
    ("G16", "fetch safety: latches, STOP_BOJ, pacing, caps, hosts, identification string, no latch deletion",
     ["no_latch_non200", "no_latch_redirect", "no_latch_bad_body", "allow_fred", "ua_check_off", "no_pacing", "max_requests_21", "boj_writes_stop", "stop_boj_blocks_mof",
      "stop_boj_blocks_scoring", "boj_first", "latch_delete_code", "latch_scan_blind", "latch_overwrite_ok", "latch_on_socket", "stop_ignored", "no_done_today"], t_g16),
    ("G17", "commit folder: names, raw files, paths, at signs", ["no_name_check", "no_title_check", "no_pdf_check", "no_path_check", "no_private_check", "no_at_check",
                                                              "header_from_source_line"], t_g17),
    ("G18", "windows: W2 from 2024-03, 2014 onward, blank months never counted", ["w2_from_april", "pre2014_in_window", "blank_counted"], t_g18),
    ("G19", "shares: denominators, signs, dealers", ["share_negative", "share_above_one", "denominator_other_financial", "dealer_share_missing", "share_unlabelled"], t_g19),
    ("X1", "cache path: outside the repo, or git-ignored inside it", ["cache_check_off"], x_cache),
    ("X2", "a hard FAIL writes to _FAILED and leaves the committed files alone", ["failed_to_committed"], x_failed),
    ("X3", "build is offline, ignores both latches and is byte-identical on re-run; 6,264 rows", ["stop_blocks_build", "volatile_output"], x_fixed),
    ("X4", "a vintage labelled 8 Oct 2026 is held to the pins (C01, C10)", ["c10_lenient"], x_oct8),
    ("X6", "the 10 Nov workflow: a second vintage is the latest, is scored, adds revisions and keeps the earlier questions run", ["latest_is_first"], x_two_vintages),
    ("X7", "README: windows named and the per-window net computed; build decisions live in SOURCES.md", ["windows_hardcoded", "decisions_in_readme"], x_readme),
    ("X5", "C13 reproduces the reviewer's pinned window statistics from numbers equal to them, and fails on any difference", [], x_c13),
]


def selftest_one(name):
    """The whole selftest with one mutant switched on from the start: it must fail, and the guards that fail are named."""
    synth_texts()                                   # the clean synthetic build is made first, with nothing switched on
    failing = []
    with mutant(name):
        for gid, desc, muts, fn in GUARDS:
            if run_test(fn).failed():
                failing.append(gid)
    print("mutant %s switched on for the whole selftest: failing guard(s): %s" % (name, ", ".join(failing) or "NONE"))
    return 1 if failing else 0


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
                print("       mutant %-30s %s%s" % (m, "FAIL (caught)" if caught else "NOT CAUGHT", "  (first failing check: %s)" % mk.failed()[0][0][:90] if caught else ""))
    print("selftest: %d guards, %d checks, %d mutants applied one at a time, %d failure(s), %.1f s" % (len(GUARDS), n_checks, n_mut, bad_total, time.time() - t0))
    return 0 if bad_total == 0 else 1


# ------------------------------------------------------------------------------------------------------------------------
# command line
# ------------------------------------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch", help="download the 4 MoF files and the 12 BoJ statements into the cache (the only network command)")
    pf.add_argument("--cache", default=CACHE_DEFAULT)
    pf.add_argument("--out", default=OUT_DEFAULT, help="where fetch_log.csv is kept")
    pf.add_argument("--sleep", type=float, default=MIN_SLEEP, help="seconds between request starts (at least 2)")
    pf.add_argument("--max-requests", type=int, default=MAX_REQUESTS)
    pb = sub.add_parser("build", help="offline: validate the cache and write every output")
    pb.add_argument("--cache", default=CACHE_DEFAULT)
    pb.add_argument("--out", default=OUT_DEFAULT)
    ps = sub.add_parser("selftest", help="synthetic data, mutants applied one at a time; no network")
    ps.add_argument("--no-mutants", action="store_true")
    ps.add_argument("--mutant", help="switch one named mutant on for the whole selftest (exit 1 expected)")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        if a.mutant:
            known = {m for _, _, ms, _ in GUARDS for m in ms}
            if a.mutant not in known:
                print("unknown mutant %r" % a.mutant, file=sys.stderr)
                return 2
            return selftest_one(a.mutant)
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
        saved, boj_latch = fetch_all(fe, request_table())
        print("requests sent: %d, files saved: %d" % (fe.requests, saved))
        if boj_latch:
            print("STOP_BOJ: %s" % boj_latch, file=sys.stderr)
            return 6
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
