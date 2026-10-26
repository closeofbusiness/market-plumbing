#!/usr/bin/env python3
"""Who held the 2026 US IPOs at their first quarter-end after listing: shares of each listed class reported on Form 13F, set against the shares the company
had outstanding at that same quarter-end. Python 3 standard library only. NO NETWORK, ever.

  python3 bin/ipo_13f_holders.py scan   --zip-dir DIR --cache DIR [--zip NAME]      # one zip per run; streams INFOTABLE; writes the cache (second scan: after the CUSIP map)
  python3 bin/ipo_13f_holders.py review --zip-dir DIR --cache DIR                   # offline: candidate identifiers, name/identifier conflicts, top filers (no ratio)
  python3 bin/ipo_13f_holders.py build  --zip-dir DIR --cache DIR [--out DIR]       # offline; byte-identical on re-run; exits 2 unless the three reviewed constants match
  python3 bin/ipo_13f_holders.py verify --zip-dir DIR --cache DIR                   # offline: re-checks the cached zips' sizes and sha256 against the stamps
  python3 bin/ipo_13f_holders.py selftest [--no-mutants] [--mutant NAME] [--write-fixture DIR]      # synthetic data only

Specification: _research/2026-10-26-IPO-13F-Holders-Spec.md (committed at 7306996 with its supervisor rulings, rounds 1 to 5; where rounds differ the latest round
is applied). Outputs: data/ipo_13f_holders/ (thirteen CSVs, README.md, SOURCES.md).

WHAT TOUCHES THE NETWORK. Nothing. The supervisor fetches the SEC's Form 13F data sets, the readme, the Official List and the issuers' filings; this script reads
the zips (never SIGNATURE.tsv, never an address, phone or signature column) and its own cache. It imports no network or process module (selftest G14 scans this
source for them), and a file named exactly STOP in --zip-dir makes every mode but selftest print `STOP present: <path>` and exit 2. This script never deletes, renames,
overwrites or truncates a STOP file; only a person deletes one.

WHAT IT MEASURES. The shares of each deal's listed class that Form 13F filers reported holding at the first calendar quarter-end strictly after the pricing date,
summed over all filers, against the listed class outstanding at that quarter-end (the first 10-Q). It records quarter-end holdings by filer number; it does not show
who was allocated shares in an offering, when or at what price anyone bought, or why anyone held.
"""
import argparse
import ast
import collections
import contextlib
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import statistics
import sys
import tempfile
import time
import zipfile
from decimal import Decimal, ROUND_HALF_UP, getcontext, InvalidOperation

getcontext().prec = 50

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(ROOT, "data", "ipo_13f_holders")
ZIPDIR_DEFAULT = os.path.join(ROOT, "data", "vintages", "form13f_zips")
CACHE_DEFAULT = os.path.join(os.path.expanduser("~"), "ipo13f_cache")
SPEC_FILE = os.path.join(ROOT, "_research", "2026-10-26-IPO-13F-Holders-Spec.md")
I2_DIR = os.path.join(ROOT, "data", "i2_ipo_allocation")
I2_MASTER = os.path.join(I2_DIR, "i2_deal_master_summary.csv")
I2_HOLDERS = os.path.join(I2_DIR, "i2_holders_13g_13d_full_detail.csv")
I2_SAMPLE = os.path.join(I2_DIR, "i2_13F_sample_holdings.csv")
I1B_CORNERSTONES = os.path.join(ROOT, "_research", "2026-09-12-I1b-cornerstones.csv")
GITIGNORE = os.path.join(ROOT, ".gitignore")
ZIPDIR_GITIGNORE_LINE = "data/vintages/form13f_zips/"
STOP_NAME = "STOP"

# ------------------------------------------------------------------------------------------------------------------------
# The three reviewed constants (spec 2.3, 3.2, 3.3). `build` exits 2 unless each is set and equal to the sha256 of its file.
# CUSIP_MAP_SHA256 hashes the cache's cusip_map.csv; FILER_REVIEW_SHA256 the cache's filer_review.csv; DEAL_INPUTS_SHA256 the committed deal_inputs.csv.
# ------------------------------------------------------------------------------------------------------------------------
CUSIP_MAP_SHA256 = "d939fb8ec9cd919bd16377c2620e68495b6416656e6cd9b7c9953af288b01714"      # reviewed by the supervisor 26 Oct 2026 (stage 2)
FILER_REVIEW_SHA256 = "d2c369334679d441792dd4b148c70cad68b37ec175cef5696e17d0bcf6828f70"      # reviewed by the supervisor 26 Oct 2026 (stage 2)
DEAL_INPUTS_SHA256 = "d1b2471102068e62f59aeb697352463b03fee9265840e07fb8d645f3a027ffc8"      # checked by the supervisor 26 Oct 2026 (stage 2)

# The canonical header allowlist (spec section 5): thirteen lines, LF-terminated, 1,958 bytes. bin/check.sh holds its own literal copy.
ALLOW_TEXT = """deal_inputs.csv:ticker,class_label,is_listed_class,item,shares,asof,doc_form,doc_filing_date,doc_section,quote
deals.csv:ticker,issuer,pricing_date,first_trade_date,first_trade_source,in_112bn,proceeds_usd,weight_pct_of_measured,offer_price_usd,ipo_shares_base,first_qe,status,den_listed_10q_sh,den_listed_10q_item,den_listed_10q_asof,den_listed_prosp_sh,den_all_classes_10q_sh,vintage
holdings.csv:ticker,quarter_end,n_filers,sh_13f,sh_13f_sole,sh_pre_ipo_flagged,sh_13dg_holders_without_13f,pct_of_listed,pct_of_listed_prosp,pct_of_all_classes,ipo_shares_pct_of_listed,pct_of_ipo_shares,top1_pct_of_13f,top10_pct_of_13f,top10_pct_of_listed,sh_calls,sh_puts,n_filers_calls,n_filers_puts,sh_name_match_other_cusip,median_implied_price_usd,implied_to_offer_ratio,n_rows_value_blank,vintage
reg_category.csv:ticker,quarter_end,reg_category,n_filers,sh_13f,pct_of_13f,pct_of_listed,vintage
top_filers.csv:ticker,quarter_end,rank,filer_label,filed_13g_13d,sh_13f,pct_of_13f,pct_of_listed,vintage
kind_hypothesis.csv:ticker,quarter_end,rank,filer_label,holder_kind,kind_basis,vintage
overlap_i2.csv:ticker,quarter_end,i2_holder_label,i2_form,i2_type,i2_event_date,i2_shares,has_13f_row,sh_13f_matched,gap_sh,vintage
cornerstones.csv:ticker,cornerstone_label,indicated_usd_up_to,offer_price_usd,indicated_sh_up_to_at_offer,quarter_end,n_mapped_filers,sh_13f_mapped,pct_of_indicated_up_to,vintage
coverage.csv:quarter_end,zip_name,n_hr_filers,n_nt_filers,n_conf_omitted,pct_conf_omitted_of_hr,n_restatements,n_new_holdings,n_new_holdings_repeat_cusip,n_amend_orphans,n_amend_duplicates,n_filed_after_due,vintage
summary.csv:question,scope,ticker,quarter_end,statistic,value,unit,denominator,vintage
revisions.csv:vintage_prev,vintage_new,ticker,quarter_end,sh_13f_prev,sh_13f_new,change_sh,change_pct_of_prev
zips.csv:zip_name,window_start,window_end,bytes,sha256,n_submissions,n_infotable_rows,role,vintage
checks.csv:check_id,description,expected,observed,status
"""
SPEC_ALLOW_SHA256 = "ee8cb56e1611e5586421bc59d7b2a87766937889bfb386d862f89a69323c8b65"
COMMITTED_CSV = tuple(l.split(":", 1)[0] for l in ALLOW_TEXT.strip().split("\n"))
COMMITTED_NAMES = frozenset(COMMITTED_CSV) | {"README.md", "SOURCES.md"}

# keys that identify a row, per file: a duplicate key is a FAIL (spec section 5, "Allowed values")
KEYS = {
    "deal_inputs.csv": ("ticker", "class_label", "item"),
    "deals.csv": ("ticker",),
    "holdings.csv": ("ticker", "quarter_end"),
    "reg_category.csv": ("ticker", "quarter_end", "reg_category"),
    "top_filers.csv": ("ticker", "quarter_end", "rank"),
    "kind_hypothesis.csv": ("ticker", "quarter_end", "rank"),
    "overlap_i2.csv": ("ticker", "quarter_end", "i2_holder_label"),
    "cornerstones.csv": ("ticker", "cornerstone_label", "quarter_end"),
    "coverage.csv": ("quarter_end", "zip_name"),
    "summary.csv": ("question", "scope", "ticker", "quarter_end", "statistic"),
    "revisions.csv": ("vintage_prev", "vintage_new", "ticker", "quarter_end"),
    "zips.csv": ("zip_name",),
    "checks.csv": ("check_id",),
}

ITEMS = ("qe_balance_sheet", "qe_cover", "after_offering_base", "ipo_shares_base", "pricing_date", "first_trade_date", "offer_price_usd")      # offer_price_usd: supervisor ruling R6-3
REG_CATEGORIES = ("ria_801", "era_802", "bd_8", "other_prefix", "none")
REG_PREFIXES = (("801-", "ria_801"), ("802-", "era_802"), ("8-", "bd_8"))        # matched longest first (G17)
HOLDER_KINDS = ("asset_manager", "hedge_fund", "bank_broker", "insurer", "pension_endowment_sovereign", "corporate_strategic", "venture_or_pre_ipo", "other")
KIND_BASES = ("13g_type", "name_review")
FIRST_TRADE_PLACEHOLDER = "SUPERVISOR_FIRST_TRADE_DATE_PENDING"
# What an unknown (here: blank) AMENDMENTTYPE does. The spec says it is a FAIL listing all of them, so the default is "all": any such amendment in any period read refuses
# the build. A supervisor ruling may set "measured_quarters_only" (refuse only at a measured deal's first quarter-end; the rest are listed in C10).
UNKNOWN_AMENDTYPE_SCOPE = "measured_quarters_only"       # supervisor ruling R6-1 (the spec-literal value is "all")

# the deals: pattern (literal, re.I) and the listed-class label used to pick i2 rows (spec 3.1, 3.7)
DEAL_PATTERNS = collections.OrderedDict([
    ("SPCX", r"SPACE\s*EXPLORATION|SPACEX"),
    ("CBRS", r"CEREBRAS"),
    ("QNT", r"QUANTINUUM"),
    ("FRVO", r"FERVO"),
    ("INIO", r"INNIO"),
    ("SKHY", r"SK\s*HYNIX"),
    ("JMKE", r"JERSEY\s*MIKE"),
    ("BSP", r"BENDING\s*SPOONS"),
])
MEASURED_NOW = ("SPCX", "CBRS", "QNT", "FRVO", "INIO")          # the five whose first quarter-end is 2026-06-30 (spec 2.1); status is computed from the data
I2_CLASS_RX = {"SPCX": r"class\s*a", "CBRS": r"class\s*a", "QNT": r"class\s*a", "FRVO": r"class\s*a", "INIO": r"common|ordinary|shares"}
CORNERSTONE_DEALS = {"FRVO": "Fervo Energy Company (FRVO)"}                                      # I1b rows with an indicated-interest ceiling and the 13F data in hand
SPCX_REFERENCE = {"SPCX": Decimal("3685578550"), "CBRS": Decimal("88744964")}                   # C19 (R3-9): PortfolioSavvy, 30 Jun 2026, relayed from the round-3 ruling
TOTAL_112 = Decimal("111941660492")
TOTAL_112_EXSPCX = Decimal("36941660567")
WEIGHT_PINS = {"SPCX": "89.158", "CBRS": "6.598", "FRVO": "2.247", "QNT": "1.997", "INIO": "0.000"}
WEIGHT_PINS_EX = {"CBRS": "60.855", "FRVO": "20.724", "INIO": "0.000", "QNT": "18.421"}

AMEND_TYPES = ("RESTATEMENT", "NEW HOLDINGS")
SUB_TYPES = ("13F-HR", "13F-HR/A", "13F-NT", "13F-NT/A")
MONTHS = {m: i + 1 for i, m in enumerate(("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"))}
GERMAN_MONTHS = {m: i + 1 for i, m in enumerate(("JAN", "FEB", "MRZ", "APR", "MAI", "JUN", "JUL", "AUG", "SEP", "OKT", "NOV", "DEZ"))}
MONTH_NAMES = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")

# the only columns ever read from each table (spec 2.2 and R3). FIGI (INFOTABLE), every address, phone and signature column, SIGNATURE.tsv: never.
SUB_COLS = ("ACCESSION_NUMBER", "FILING_DATE", "SUBMISSIONTYPE", "CIK", "PERIODOFREPORT")
COV_COLS = ("ACCESSION_NUMBER", "ISAMENDMENT", "AMENDMENTTYPE", "CONFDENIEDEXPIRED", "REPORTTYPE", "FILINGMANAGER_NAME", "SECFILENUMBER")
SUM_COLS = ("ACCESSION_NUMBER", "ISCONFIDENTIALOMITTED")
INF_COLS = ("ACCESSION_NUMBER", "NAMEOFISSUER", "TITLEOFCLASS", "CUSIP", "VALUE", "SSHPRNAMT", "SSHPRNAMTTYPE", "PUTCALL", "INVESTMENTDISCRETION", "OTHERMANAGER")
FORBIDDEN_MEMBERS = frozenset({"SIGNATURE" + ".tsv"})
FORBIDDEN_COLS_RX = re.compile(r"STREET|CITY|ZIPCODE|STATEORCOUNTRY|PHONE|SIGNATURE|FIGI|^NAME$|TITLE$", re.I)       # NAMEOFISSUER/TITLEOFCLASS are allowed by exact name below
ALLOWED_COL_NAMES = frozenset(SUB_COLS + COV_COLS + SUM_COLS + INF_COLS)
READ_LOG = []                                                                                   # (member, columns) of every table read: the runtime open-hook of G12
OPEN_LOG = []                                                                                   # every zip member opened

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
    """A path or setting this script will not honour."""


class DataError(Exception):
    """The data or a reviewed table fails a rule: exit 2."""


class StopPresent(Exception):
    """A file named STOP is present."""


# ------------------------------------------------------------------------------------------------------------------------
# small helpers
# ------------------------------------------------------------------------------------------------------------------------
def sha256_of(b):
    return hashlib.sha256(b).hexdigest()


def sha256_path(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def D_(s):
    """Decimal from a text value; a blank is None; anything else that is not a number is a DataError."""
    if s is None:
        return None
    s = str(s).strip().replace(",", "")
    if s == "":
        return None
    try:
        v = Decimal(s)
    except InvalidOperation:
        raise DataError("not a number: %r" % s[:40])
    if not v.is_finite():
        raise DataError("not a finite number: %r" % s[:40])
    return v


def qfix(v, nd):
    if v is None:
        return None
    return v.quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)


def dstr(v, nd=None):
    """Text of a Decimal; None is the empty string, never 0. nd None keeps the value's own exponent (integers print without a point)."""
    if v is None:
        return ""
    if nd is not None:
        v = qfix(v, nd)
    s = format(v, "f")
    if nd is None and "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def comma(v, nd=0):
    if v is None:
        return ""
    return format(qfix(Decimal(v), nd), ",.%df" % nd)


def pct(num, den):
    if num is None or den is None or den == 0:
        return None
    return Decimal(100) * Decimal(num) / Decimal(den)


def dsum(values):
    t = Decimal(0)
    for v in values:
        t += v
    return t


def median_dec(vals):
    vals = sorted(vals)
    n = len(vals)
    if n == 0:
        return None
    if n % 2:
        return vals[n // 2]
    return (vals[n // 2 - 1] + vals[n // 2]) / 2


def iso(d):
    return d.isoformat() if d is not None else ""


def parse_iso(s):
    s = (s or "").strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        raise DataError("not an ISO date: %r" % s[:20])
    return dt.date(int(s[:4]), int(s[5:7]), int(s[8:10]))


def parse_dmy(s):
    """`DD-MON-YYYY` with an English month table, never the locale and never month-first (G6). A blank is None."""
    s = (s or "").strip().upper()
    if s == "":
        return None
    m = re.fullmatch(r"(\d{2})-([A-Z]{3})-(\d{4})", s)
    if not m:
        raise DataError("not a DD-MON-YYYY date: %r" % s[:20])
    table = GERMAN_MONTHS if M("g6_locale_months") else MONTHS
    if m.group(2) not in table:
        raise DataError("unknown month in date: %r" % s[:20])
    day, mon = int(m.group(1)), table[m.group(2)]
    if M("g6_day_first_misread") and day <= 12:
        day, mon = mon, day
    try:
        return dt.date(int(m.group(3)), mon, day)
    except ValueError:
        raise DataError("impossible date: %r" % s[:20])


def parse_mdy(s):
    s = (s or "").strip()
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)
    if not m:
        raise DataError("not an MM/DD/YYYY date: %r" % s[:20])
    return dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))


def long_date(d):
    return "%d %s %d" % (d.day, MONTH_NAMES[d.month - 1], d.year)


def quarter_end_on(year, q):
    return {1: dt.date(year, 3, 31), 2: dt.date(year, 6, 30), 3: dt.date(year, 9, 30), 4: dt.date(year, 12, 31)}[q]


def first_qe_after(d, strict=True):
    """The first calendar quarter-end strictly after the pricing date (G5). Pricing on the quarter-end day itself belongs to the next one."""
    cands = []
    for y in (d.year, d.year + 1):
        for q in (1, 2, 3, 4):
            cands.append(quarter_end_on(y, q))
    for c in cands:
        if (c > d) if (strict and not M("g5_qe_on_day")) else (c >= d):
            return c
    raise DataError("no quarter-end after %s" % d)


def is_quarter_end(d):
    return d in (quarter_end_on(d.year, q) for q in (1, 2, 3, 4))


def _nth_weekday(year, month, weekday, n):
    d = dt.date(year, month, 1)
    d += dt.timedelta(days=(weekday - d.weekday()) % 7)
    return d + dt.timedelta(days=7 * (n - 1))


def _last_weekday(year, month, weekday):
    d = dt.date(year, month + 1, 1) - dt.timedelta(days=1) if month < 12 else dt.date(year, 12, 31)
    return d - dt.timedelta(days=(d.weekday() - weekday) % 7)


def us_federal_holidays(year):
    fixed = [dt.date(year, 1, 1), dt.date(year, 6, 19), dt.date(year, 7, 4), dt.date(year, 11, 11), dt.date(year, 12, 25)]
    obs = set()
    for h in fixed:
        if h.weekday() == 5:
            obs.add(h - dt.timedelta(days=1))
        elif h.weekday() == 6:
            obs.add(h + dt.timedelta(days=1))
        else:
            obs.add(h)
    obs |= {_nth_weekday(year, 1, 0, 3), _nth_weekday(year, 2, 0, 3), _last_weekday(year, 5, 0), _nth_weekday(year, 9, 0, 1), _nth_weekday(year, 10, 0, 2), _nth_weekday(year, 11, 3, 4)}
    return obs


def due_date(qe):
    """A 13F-HR is due 45 days after the quarter-end; a weekend or federal holiday rolls to the next business day (spec 2.2: 2026-09-30 -> 2026-11-16)."""
    d = qe + dt.timedelta(days=45)
    if M("g5_due_no_roll"):
        return d
    while d.weekday() >= 5 or d in us_federal_holidays(d.year) or d in us_federal_holidays(d.year + 1):
        d += dt.timedelta(days=1)
    return d


def zip_window(name):
    """`01jun2026-31aug2026_form13f.zip` -> (2026-06-01, 2026-08-31), from the file name only."""
    m = re.fullmatch(r"(\d{2})([a-z]{3})(\d{4})-(\d{2})([a-z]{3})(\d{4})_form13f\.zip", name)
    if not m:
        raise DataError("not a Form 13F data-set zip name: %r" % name)
    a = dt.date(int(m.group(3)), MONTHS[m.group(2).upper()], int(m.group(1)))
    b = dt.date(int(m.group(6)), MONTHS[m.group(5).upper()], int(m.group(4)))
    return a, b


def vintage_of(zip_names):
    """The newest zip's window end, e.g. `13f_to_2026-08-31` (R9). Never the wall clock."""
    ends = sorted(zip_window(n)[1] for n in zip_names)
    if not ends:
        raise DataError("no zip")
    if M("g6_wallclock_vintage"):
        return "13f_to_" + dt.date.today().isoformat()
    pick = ends[0] if M("g6_vintage_not_newest") else ends[-1]
    return "13f_to_" + pick.isoformat()


def source_line(zip_names):
    tail = (" Retrieved " + dt.date.today().isoformat() + ".") if M("g6_wallclock_source") else ""
    return '# source: U.S. Securities and Exchange Commission, "Form 13F Data Sets", ' + ", ".join(sorted(zip_names)) + "." + tail


# ------------------------------------------------------------------------------------------------------------------------
# identifiers (CUSIP): normalised and checked in memory, never written to a committed file (R4)
# ------------------------------------------------------------------------------------------------------------------------
def norm_cusip(s):
    """Strip all whitespace, upper-case. A value that is not 9 characters afterwards is returned as it is, never padded (O-13)."""
    if M("g3_no_normalise"):
        return s or ""
    t = re.sub(r"\s+", "", s or "").upper()
    if M("g3_pad8") and len(t) == 8:
        t = t + "0"
    return t


def cusip_check_ok(c):
    if len(c) != 9 or not re.fullmatch(r"[0-9A-Z*@#]{9}", c):
        return False
    tot = 0
    for i, ch in enumerate(c[:8]):
        v = int(ch) if ch.isdigit() else (ord(ch) - 55 if ch.isalpha() else {"*": 36, "@": 37, "#": 38}[ch])
        if i % 2 == 1:
            v *= 2
        tot += v // 10 + v % 10
    return c[8].isdigit() and (10 - tot % 10) % 10 == int(c[8])


def cusip_valid(c):
    if M("g3_accept_bad_check"):
        return len(c) == 9
    return cusip_check_ok(c)


# ------------------------------------------------------------------------------------------------------------------------
# paths, the STOP latch, writing (R1-R3, G14)
# ------------------------------------------------------------------------------------------------------------------------
def real(p):
    return os.path.realpath(os.path.expanduser(p))


def inside(path, root):
    path, root = real(path), real(root)
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def gitignored_zipdir(path, root=None):
    """The one place inside the repository a zip folder may sit (round 5): exactly data/vintages/form13f_zips/, and only while .gitignore names it."""
    root = root or ROOT
    if real(path) != real(os.path.join(root, "data", "vintages", "form13f_zips")):
        return False
    try:
        with open(os.path.join(root, ".gitignore"), encoding="utf-8") as fh:
            return any(l.strip() == ZIPDIR_GITIGNORE_LINE for l in fh)
    except OSError:
        return False


def check_dirs(zip_dir, cache, root=None):
    """R2/R3: the cache is never inside the repository; the zip folder only at the gitignored place named by the round-5 ruling."""
    root = root or ROOT
    if not M("g14_cache_in_repo_accepted") and inside(cache, root):
        raise Refused("--cache is inside the repository: %s" % cache)
    if not M("g14_zipdir_in_repo_accepted") and inside(zip_dir, root) and not gitignored_zipdir(zip_dir, root):
        raise Refused("--zip-dir is inside the repository and is not the gitignored data/vintages/form13f_zips/: %s" % zip_dir)


def stop_path(zip_dir, cache=None):
    """The path of a file named exactly STOP in --zip-dir (or the cache), else None. `STOP.<date>.<note>` is a preserved record, not the latch."""
    if M("g14_stop_ignored"):
        return None
    for d in (zip_dir, cache):
        if d and os.path.isfile(os.path.join(d, STOP_NAME)):
            return os.path.join(d, STOP_NAME)
    return None


def require_no_stop(zip_dir, cache=None):
    p = stop_path(zip_dir, cache)
    if p:
        raise StopPresent(p)


def write_text(path, text):
    """Write a text file, LF line endings. Never reaches a path named STOP."""
    if os.path.basename(path) == STOP_NAME:
        raise Refused("will not write a STOP path: %s" % path)
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def csv_text(rows, header=None, source=None):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    if header:
        w.writerow(header)
    for r in rows:
        w.writerow(r)
    body = buf.getvalue()
    return (source + "\n" if source else "") + body


def read_csv_rows(path):
    with open(path, encoding="utf-8", newline="") as fh:
        lines = fh.read().split("\n")
    body = [l for l in lines if l.strip() != "" and not l.startswith("# source:")]
    rd = list(csv.reader(body))
    if not rd:
        return [], []
    return rd[0], [dict(zip(rd[0], r)) for r in rd[1:]]


# ------------------------------------------------------------------------------------------------------------------------
# reading the SEC tables (R3, G12): named columns only, by index; SIGNATURE.tsv is never opened
# ------------------------------------------------------------------------------------------------------------------------
def open_member(zf, member):
    base = os.path.basename(member)
    if base in FORBIDDEN_MEMBERS and not M("g12_open_signature"):
        raise Refused("will not open %s" % base)
    OPEN_LOG.append(base)
    return zf.open(member)


def read_table(zf, member, cols):
    """Yield tuples of the named columns of one TSV member. Missing names are all reported together (C14). Streams; never loads a table whole."""
    cols = tuple(cols)
    asked = cols
    if M("g12_read_address") and member == "COVERPAGE.tsv":
        cols = cols + ("FILINGMANAGER_STREET1",)
    elif any(c not in ALLOWED_COL_NAMES for c in cols):
        raise Refused("column not on the read allowlist: %s" % [c for c in cols if c not in ALLOWED_COL_NAMES])
    READ_LOG.append((member, cols))
    with open_member(zf, member) as raw:
        txt = io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="")
        rd = csv.reader(txt, delimiter="\t", quoting=csv.QUOTE_NONE)
        try:
            header = [h.strip().lstrip("﻿") for h in next(rd)]
        except StopIteration:
            raise DataError("%s is empty" % member)
        missing = [c for c in cols if c not in header]
        if missing:
            raise DataError("%s lacks field(s): %s" % (member, ", ".join(missing)))
        idx = [header.index(c) for c in cols]
        top = max(idx)
        keep = idx[:len(asked)]
        for row in rd:
            if len(row) <= top:
                row = row + [""] * (top + 1 - len(row))
            yield tuple(row[i] for i in keep)


# ------------------------------------------------------------------------------------------------------------------------
# the model: one submission, one holdings row
# ------------------------------------------------------------------------------------------------------------------------
class Sub:
    __slots__ = ("acc", "filing", "stype", "cik", "period", "isamend", "amendtype", "conf_denied", "reporttype", "secfile", "name", "conf_omitted", "zip")

    def __init__(self, acc, filing, stype, cik, period, isamend="", amendtype="", conf_denied="", reporttype="", secfile="", name="", conf_omitted="", zip=""):
        self.acc, self.filing, self.stype, self.cik, self.period = acc, filing, stype, cik, period
        self.isamend, self.amendtype, self.conf_denied, self.reporttype = isamend, amendtype, conf_denied, reporttype
        self.secfile, self.name, self.conf_omitted, self.zip = secfile, name, conf_omitted, zip

    def key(self):
        return (self.filing, self.acc)


Row = collections.namedtuple("Row", "acc name title cusip value shares sh_type putcall disc other tick")


def cik_key(c):
    return (c or "").strip().lstrip("0") or "0"


SUB_FIELDS = ("acc", "filing_date", "stype", "cik", "period", "isamend", "amendtype", "conf_denied", "reporttype", "secfile", "name", "conf_omitted")
ROW_FIELDS = ("acc", "name", "title", "cusip", "value", "shares", "sh_type", "putcall", "disc", "other", "tick")


def sub_to_cells(s):
    return [s.acc, iso(s.filing), s.stype, s.cik, iso(s.period), s.isamend, s.amendtype, s.conf_denied, s.reporttype, s.secfile, s.name, s.conf_omitted]


def sub_from_cells(c, zip_name=""):
    return Sub(c["acc"], parse_iso(c["filing_date"]), c["stype"], c["cik"], parse_iso(c["period"]) if c["period"] else None, c["isamend"], c["amendtype"], c["conf_denied"],
               c["reporttype"], c["secfile"], c["name"], c["conf_omitted"], zip_name)


def parse_shares(s):
    """SSHPRNAMT as a Decimal, exactly (R8); a negative amount is a DataError (G4)."""
    if M("g2_shares_float"):
        return Decimal(float((s or "0").replace(",", "") or 0))
    v = D_(s)
    if v is None:
        raise DataError("blank SSHPRNAMT")
    if v < 0 and not M("g4_negative_accepted"):
        raise DataError("negative SSHPRNAMT: %s" % s)
    return v


README_SAYS_THOUSANDS = [False]


def parse_value(s):
    """VALUE in whole US dollars, never rescaled (round 5, G4); blank is None; negative is a DataError."""
    v = D_(s)
    if v is None:
        return None
    if v < 0 and not M("g4_negative_accepted"):
        raise DataError("negative VALUE: %s" % s)
    if M("g4_value_thousands") or (M("g4_value_thousands_readme") and README_SAYS_THOUSANDS[0]):
        v = v * 1000
    return v


# ------------------------------------------------------------------------------------------------------------------------
# the scan (method 1): stream a zip, keep named fields of SUBMISSION, COVERPAGE, SUMMARYPAGE, and the INFOTABLE rows of the deals
# ------------------------------------------------------------------------------------------------------------------------
def combined_rx():
    return re.compile("|".join("(?P<%s>%s)" % (t, p) for t, p in DEAL_PATTERNS.items()), re.I)


def name_ticker(name, rx=None):
    rx = rx or combined_rx()
    m = rx.search(name or "")
    return m.lastgroup if m else ""


CUSIP_MAP_FIELDS = ("ticker", "cusip", "status", "evidence", "reason")
MAP_STATUS = ("listed", "rejected", "option_call", "option_put")       # option_*: supervisor ruling R6-6
MAP_EVIDENCE = ("official_list_2026q2", "filer_consensus", "")


def read_cusip_map(path):
    """Rows of the reviewed map, validated. At most one `listed` CUSIP per ticker; a check-digit failure on a listed row is a DataError (C06)."""
    hdr, rows = read_csv_rows(path)
    if tuple(hdr) != CUSIP_MAP_FIELDS:
        raise DataError("cusip_map.csv header is not %s" % ",".join(CUSIP_MAP_FIELDS))
    out, listed = [], {}
    for r in rows:
        r = {k: (v or "").strip() for k, v in r.items()}
        r["cusip"] = norm_cusip(r["cusip"])
        if r["ticker"] not in DEAL_PATTERNS:
            raise DataError("cusip_map.csv: unknown ticker %r" % r["ticker"])
        if r["status"] not in MAP_STATUS:
            raise DataError("cusip_map.csv: status %r is not one of %s" % (r["status"], MAP_STATUS))
        if r["evidence"] not in MAP_EVIDENCE:
            raise DataError("cusip_map.csv: evidence %r is not one of %s" % (r["evidence"], MAP_EVIDENCE))
        if r["status"] == "listed":
            if not cusip_valid(r["cusip"]):
                raise DataError("cusip_map.csv: a listed identifier for %s fails its check digit" % r["ticker"])
            if r["ticker"] in listed:
                raise DataError("cusip_map.csv: two listed identifiers for %s" % r["ticker"])
            listed[r["ticker"]] = r["cusip"]
        out.append(r)
    return out


def map_listed(map_rows):
    return {r["ticker"]: r["cusip"] for r in map_rows if r["status"] == "listed"}


def map_options(map_rows):
    """{identifier: (ticker, "CALL" or "PUT")} for the Official List's option identifiers of a deal's listed class (R6-6): their rows are options on the listed class."""
    return {r["cusip"]: (r["ticker"], "CALL" if r["status"] == "option_call" else "PUT") for r in map_rows if r["status"] in ("option_call", "option_put")}


def map_all_cusips(map_rows):
    return {r["cusip"] for r in map_rows}


def scan_zip(zf, say=print, map_rows=None, rx=None):
    """Returns (subs, rows, stamp_part). Two passes over INFOTABLE: the first finds the identifiers of name-matched rows, the second keeps every row whose name
    matches or whose normalised identifier is a candidate (so a row filed under a differently spelled name is still seen, C-059)."""
    rx = rx or combined_rx()
    if M("g12_open_signature"):
        with open_member(zf, next(iter(FORBIDDEN_MEMBERS))) as fh:
            fh.read(16)
    subs = {}
    for acc, fdate, stype, cik, period in read_table(zf, "SUBMISSION.tsv", SUB_COLS):
        acc = acc.strip()
        if acc in subs:
            raise DataError("accession twice in one SUBMISSION table")
        subs[acc] = Sub(acc, parse_dmy(fdate), stype.strip(), cik.strip(), parse_dmy(period))
    cov = {}
    for acc, isam, atype, cden, rtype, mgr, secf in read_table(zf, "COVERPAGE.tsv", COV_COLS):
        cov[acc.strip()] = (isam.strip().upper(), atype.strip().upper(), cden.strip().upper(), rtype.strip(), mgr.strip(), secf.strip())
    summ = {}
    for acc, conf in read_table(zf, "SUMMARYPAGE.tsv", SUM_COLS):
        summ[acc.strip()] = conf.strip().upper()
    for acc, s in subs.items():
        c = cov.get(acc)
        if c:
            s.isamend, s.amendtype, s.conf_denied, s.reporttype, s.name, s.secfile = c[0], c[1], c[2], c[3], c[4], c[5]
        s.conf_omitted = summ.get(acc, "")
    say("  SUBMISSION %d, COVERPAGE %d, SUMMARYPAGE %d rows" % (len(subs), len(cov), len(summ)))
    cands = (set(map_listed(map_rows).values()) | set(map_options(map_rows))) if map_rows else set()
    n_rows = 0
    for acc, name, title, cusip, value, shares, sht, pc, disc, other in read_table(zf, "INFOTABLE.tsv", INF_COLS):
        n_rows += 1
        if not map_rows and rx.search(name):          # the first scan discovers candidates; the second scan keeps the mapped identifiers (and, as ever, every name match)
            cands.add(norm_cusip(cusip))
    say("  INFOTABLE pass 1: %d rows, %d candidate identifiers" % (n_rows, len(cands)))
    rows, n2 = [], 0
    for acc, name, title, cusip, value, shares, sht, pc, disc, other in read_table(zf, "INFOTABLE.tsv", INF_COLS):
        n2 += 1
        t = name_ticker(name, rx)
        cn = norm_cusip(cusip)
        if t or cn in cands:
            rows.append(Row(acc.strip(), name.strip(), title.strip(), cn, value.strip(), shares.strip(), sht.strip().upper(), pc.strip().upper(), disc.strip().upper(), other.strip(), t))
    if n2 != n_rows:
        raise DataError("INFOTABLE row count differs between the two passes")
    say("  INFOTABLE pass 2: kept %d rows" % len(rows))
    return list(subs.values()), rows, {"n_submissions": len(subs), "n_infotable_rows": n_rows, "n_candidates": len(cands),
                                       "fields": {"SUBMISSION": list(SUB_COLS), "COVERPAGE": list(COV_COLS), "SUMMARYPAGE": list(SUM_COLS), "INFOTABLE": list(INF_COLS)}}


def zip_key(zip_name):
    return zip_name[:-4] if zip_name.endswith(".zip") else zip_name


def write_scan(cache, zip_name, zip_path, subs, rows, part, map_sha):
    d = os.path.join(cache, "scan_" + zip_key(zip_name))
    a, b = zip_window(zip_name)
    sub_rows = [sub_to_cells(s) for s in sorted(subs, key=lambda s: s.acc)]
    write_text(os.path.join(d, "submissions.csv"), csv_text(sub_rows, SUB_FIELDS))
    row_rows = [[r.acc, r.name, r.title, r.cusip, r.value, r.shares, r.sh_type, r.putcall, r.disc, r.other, r.tick]
                for r in sorted(rows, key=lambda r: (r.acc, r.cusip, r.name, r.shares, r.putcall, r.value))]
    write_text(os.path.join(d, "infotable.csv"), csv_text(row_rows, ROW_FIELDS))
    stamp = {"zip_name": zip_name, "zip_bytes": os.path.getsize(zip_path), "zip_sha256": sha256_path(zip_path), "window_start": iso(a), "window_end": iso(b),
             "map_sha256": map_sha, "script": "ipo_13f_holders v1"}
    stamp.update(part)
    write_text(os.path.join(d, "stamp.json"), json.dumps(stamp, indent=1, sort_keys=True) + "\n")
    return stamp


class Scan:
    __slots__ = ("zip_name", "stamp", "subs", "rows")

    def __init__(self, zip_name, stamp, subs, rows):
        self.zip_name, self.stamp, self.subs, self.rows = zip_name, stamp, subs, rows


def load_scan(cache, key):
    d = os.path.join(cache, key)
    with open(os.path.join(d, "stamp.json"), encoding="utf-8") as fh:
        stamp = json.load(fh)
    _, sub_rows = read_csv_rows(os.path.join(d, "submissions.csv"))
    subs = [sub_from_cells(r, stamp["zip_name"]) for r in sub_rows]
    _, row_rows = read_csv_rows(os.path.join(d, "infotable.csv"))
    rows = [Row(r["acc"], r["name"], r["title"], r["cusip"], r["value"], r["shares"], r["sh_type"], r["putcall"], r["disc"], r["other"], r["tick"]) for r in row_rows]
    return Scan(stamp["zip_name"], stamp, subs, rows)


def load_scans(cache):
    keys = sorted(k for k in os.listdir(cache) if k.startswith("scan_") and os.path.isfile(os.path.join(cache, k, "stamp.json")))
    return [load_scan(cache, k) for k in keys]


def accession_problems(scans):
    """C11: an accession seen in two zips is a FAIL."""
    seen, bad = {}, []
    for sc in scans:
        for s in sc.subs:
            if s.acc in seen and seen[s.acc] != sc.zip_name and not M("g11_dup_accession_accepted"):
                bad.append("accession in two zips: %s and %s" % (seen[s.acc], sc.zip_name))
            seen.setdefault(s.acc, sc.zip_name)
    return bad


# ------------------------------------------------------------------------------------------------------------------------
# one report per filer and quarter (method 4)
# ------------------------------------------------------------------------------------------------------------------------
class Res:
    """The consolidation of one (filer, period): the accessions whose rows count, and everything listed on the way."""

    def __init__(self, cik, period):
        self.cik, self.period = cik, period
        self.used, self.base = [], None
        self.severals, self.orphans, self.dups, self.repeats, self.unknown, self.superseded, self.stale, self.mislabelled = [], [], [], [], [], [], [], []


def row_sig(rows):
    return tuple(sorted(tuple(r[1:]) for r in rows))


def consolidate_group(subs, rows_of, cusips=None):
    """subs: every submission of one filer for one period. rows_of(acc) -> that accession's kept rows. cusips: the identifiers a repeat is judged on (default: all)."""
    cik, period = (subs[0].cik, subs[0].period) if subs else ("", None)
    res = Res(cik, period)
    hr = sorted([s for s in subs if s.stype == "13F-HR"], key=Sub.key)
    am = sorted([s for s in subs if s.stype == "13F-HR/A"], key=Sub.key)
    known = []
    for s in am:
        if s.amendtype in AMEND_TYPES:
            known.append(s)
        elif M("g1_unknown_amendtype_accepted"):
            known.append(s)
        else:
            res.unknown.append((s.acc, s.amendtype))
    rest = [s for s in known if s.amendtype == "RESTATEMENT"]
    newh = [s for s in known if s.amendtype != "RESTATEMENT"]
    base = hr[-1] if hr else None
    used = []
    if base is not None:
        used = [base]
        if base.isamend == "Y":
            res.mislabelled.append(base.acc)          # a 13F-HR whose cover page says it is an amendment: kept as the base (its SUBMISSIONTYPE), listed
        if len(hr) > 1:
            res.severals = [s.acc for s in hr[:-1]]
            if M("g1_two_originals_counted"):
                used = list(hr)
    else:
        if not M("g1_orphan_not_listed"):
            res.orphans = [s.acc for s in known]
        if M("g1_orphan_dropped"):
            return res
    if rest:
        latest = rest[0] if M("g1_older_restatement_wins") else rest[-1]
        if base is None:
            base = latest
            used = [latest]
        elif latest.key() > base.key() or M("g1_stale_restatement_wins"):
            used = used + [latest] if M("g1_restatement_summed_with_original") else [latest]
            base = latest
        else:
            res.stale.append(latest.acc)
    res.base = base
    if M("g1_new_holdings_dropped"):
        newh = []
    base_cus = set(r.cusip for r in rows_of(base.acc)) if base is not None else set()
    if cusips is not None:
        base_cus &= set(cusips)
    sigs = []
    for s in newh:
        if base is not None and s.key() <= base.key() and not M("g1_new_holdings_before_restatement_kept"):
            res.superseded.append(s.acc)
            continue
        rows = rows_of(s.acc)
        sig = row_sig(rows)
        if sig and sig in sigs and not M("g1_duplicate_counted_twice"):
            res.dups.append(s.acc)
            continue
        sigs.append(sig)
        mine = set(r.cusip for r in rows)
        if cusips is not None:
            mine &= set(cusips)
        if mine & base_cus and not M("g1_repeat_cusip_not_flagged"):
            res.repeats.append(s.acc)
        used.append(s)
    res.used = [s.acc for s in used]
    if res.base is None and used:
        res.base = used[0]          # a stand-alone new-holdings amendment is its own cover page for the name and file number
    return res


class Results(dict):
    unknown = ()


def consolidate_all(subs, rows_by_acc, cusips=None, fatal_periods="all"):
    """{(cik_key, period): Res} for every 13F-HR/13F-HR/A group. 13F-NT carries no holdings and is not grouped. Unknown AMENDMENTTYPE values are a DataError listing all
    (fatal_periods "all"), only those at the given periods (a set), or never (None: the caller lists them)."""
    groups = collections.defaultdict(list)
    for s in subs:
        if s.stype in ("13F-HR", "13F-HR/A") and s.period is not None:
            groups[(cik_key(s.cik), s.period)].append(s)
    out, unknown = Results(), []
    empty = []

    def rows_of(acc):
        return rows_by_acc.get(acc, empty)

    for k in sorted(groups):
        r = consolidate_group(groups[k], rows_of, cusips)
        out[k] = r
        unknown.extend((a, t, k[1]) for a, t in r.unknown)
    out.unknown = sorted(unknown)
    fatal = [u for u in unknown if fatal_periods == "all" or (fatal_periods and u[2] in fatal_periods)]
    if fatal:
        raise DataError("unknown AMENDMENTTYPE value(s): " + "; ".join("%s=%r (period %s)" % (a, t, iso(p)) for a, t, p in sorted(fatal)[:50]))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# the numerator (method 5)
# ------------------------------------------------------------------------------------------------------------------------
class Pos:
    """One filer's reported position in one deal's listed class at one quarter-end."""

    def __init__(self, cik):
        self.cik, self.name, self.secfile = cik, "", ""
        self.sh, self.sole, self.calls, self.puts = Decimal(0), Decimal(0), Decimal(0), Decimal(0)
        self.val, self.val_sh = Decimal(0), Decimal(0)
        self.n_rows, self.n_value_blank, self.n_prn, self.n_other_type, self.n_nonint, self.n_other_pc = 0, 0, 0, 0, 0, 0
        self.name_other = Decimal(0)
        self.other_opt, self.n_other_opt = Decimal(0), 0
        self.optid_sh, self.n_optid = Decimal(0), 0
        self.n_calls_rows, self.n_puts_rows = 0, 0

    def price(self):
        if self.val_sh > 0:
            return self.val / self.val_sh
        return None


def holdings(results, subs_by_acc, rows_by_acc, ticker, mapped, qe, options=None):
    """{cik_key: Pos} for the deal's listed class (`mapped`, a normalised identifier) over the consolidated reports of period `qe`."""
    out = {}
    for (ck, period), res in sorted(results.items()):
        if period != qe and not M("g2_other_period_counted"):
            continue
        for acc in res.used:
            for r in rows_by_acc.get(acc, ()):
                is_target = (r.cusip == mapped) if not M("g3_name_match_without_map") else (r.tick == ticker)
                role = options.get(r.cusip) if options else None
                if role is not None and role[0] != ticker:
                    role = None
                if not is_target and role is None and r.tick != ticker:
                    continue
                p = out.get(ck)
                if p is None:
                    p = out[ck] = Pos(ck)
                    if res.base is not None:
                        p.name, p.secfile = res.base.name, res.base.secfile
                sh = parse_shares(r.shares)
                if role is not None and not is_target and not M("g2_option_id_ignored"):
                    # R6-6: a row under the Official List's CALL or PUT identifier of the deal is an option on the listed class: counted by PUTCALL, or by the identifier's role
                    # when PUTCALL is blank; never in sh_13f
                    if r.sh_type != "SH":
                        p.n_prn += 1
                        continue
                    side = r.putcall if r.putcall in ("CALL", "PUT") else role[1]
                    p.optid_sh += sh
                    p.n_optid += 1
                    if side == "CALL":
                        p.calls += sh
                        p.n_calls_rows += 1
                    else:
                        p.puts += sh
                        p.n_puts_rows += 1
                    if M("g2_option_id_in_sh13f"):
                        p.sh += sh
                    continue
                if not is_target:
                    if r.sh_type == "SH" and r.putcall == "":
                        p.name_other += sh
                        if M("g2_name_match_added"):
                            p.sh += sh
                    elif r.sh_type == "SH" and r.putcall in ("CALL", "PUT"):
                        p.other_opt += sh              # option rows filed under an option identifier of the issuer: not counted, reported in C17
                        p.n_other_opt += 1
                    continue
                p.n_rows += 1
                if sh != sh.to_integral_value() if not M("g2_shares_float") else False:
                    p.n_nonint += 1
                val = parse_value(r.value)
                if r.sh_type == "PRN":
                    p.n_prn += 1
                    if M("g2_prn_counted"):
                        p.sh += sh
                    continue
                if r.sh_type != "SH":
                    p.n_other_type += 1
                    continue
                if r.putcall == "":
                    if val is None:
                        p.n_value_blank += 1
                        if M("g2_blank_value_dropped_from_shares"):
                            continue
                    p.sh += sh
                    if r.disc == "SOLE":
                        p.sole += sh
                    if M("g2_sole_gt_total"):
                        p.sole += sh
                    if val is not None:
                        p.val += val
                        p.val_sh += sh
                    elif M("g2_blank_value_in_price"):
                        p.val_sh += sh
                elif r.putcall == "CALL":
                    p.calls += sh
                    p.n_calls_rows += 1
                    if M("g2_option_as_shares"):
                        p.sh += sh
                elif r.putcall == "PUT":
                    p.puts += sh
                    p.n_puts_rows += 1
                    if M("g2_option_as_shares"):
                        p.sh += sh
                    if M("g4_puts_subtracted"):
                        p.sh -= 2 * sh
                else:
                    p.n_other_pc += 1
    for p in out.values():
        if p.name_other == 0 and p.n_rows == 0:
            pass
    return out


def rank_filers(poss):
    """Filers with shares, by sh_13f descending; ties by CIK, internally (G9)."""
    items = [p for p in poss.values() if p.sh > 0]
    if M("g9_unstable_ties"):
        return sorted(items, key=lambda p: -p.sh)
    return sorted(items, key=lambda p: (-p.sh, int(p.cik) if p.cik.isdigit() else 0, p.cik))


def reg_category(secfile):
    """Longest prefix first (G17): `801-` registered adviser, `802-` exempt reporting adviser, `8-` broker-dealer; another prefix `other_prefix`; blank `none`."""
    s = (secfile or "").strip().upper()
    if s == "":
        return "none"
    prefixes = REG_PREFIXES
    if M("g17_8_before_801"):
        prefixes = (("8", "bd_8"),) + REG_PREFIXES
    for p, cat in prefixes:
        if s.startswith(p):
            return cat
    return "other_prefix"


def deal_measures(poss, den):
    """Everything holdings.csv needs for one deal, from the positions. `den` is the dict returned by denominators(). Percentages are unrounded Decimals."""
    ranked = rank_filers(poss)
    sh = dsum(p.sh for p in ranked)
    m = {"n_filers": len(ranked), "sh_13f": sh, "sh_13f_sole": dsum(p.sole for p in ranked)}
    m["sh_calls"] = dsum(p.calls for p in poss.values())
    m["sh_puts"] = dsum(p.puts for p in poss.values())
    m["n_filers_calls"] = sum(1 for p in poss.values() if p.calls > 0)
    m["n_filers_puts"] = sum(1 for p in poss.values() if p.puts > 0)
    m["sh_name_match_other_cusip"] = dsum(p.name_other for p in poss.values())
    m["n_rows_value_blank"] = sum(p.n_value_blank for p in poss.values())
    prices = [p.price() for p in ranked if p.price() is not None]
    m["median_implied_price_usd"] = median_dec(prices) if not M("g8_no_median") else None
    top1 = ranked[0].sh if ranked else Decimal(0)
    top10 = dsum(p.sh for p in (ranked[1:11] if M("g9_top10_lt_top1") else ranked[:10]))
    m["top1"], m["top10"] = top1, top10
    m["top1_pct_of_13f"] = pct(top1, sh)
    m["top10_pct_of_13f"] = pct(top10, sh)
    d10 = den.get("den_listed_10q_sh")
    m["pct_of_listed"] = pct(sh, den.get("den_listed_prosp_sh") if M("g7_pct_vs_prosp_at_use") else d10)
    m["pct_of_listed_prosp"] = pct(sh, den.get("den_listed_prosp_sh"))
    m["pct_of_all_classes"] = pct(sh, den.get("den_all_classes_10q_sh"))
    m["ipo_shares_pct_of_listed"] = pct(den.get("ipo_shares_base"), d10)
    m["pct_of_ipo_shares"] = pct(sh, den.get("ipo_shares_base"))
    m["top10_pct_of_listed"] = pct(top10, d10)
    m["implied_to_offer_ratio"] = (m["median_implied_price_usd"] / den["offer_price"]) if (m["median_implied_price_usd"] is not None and den.get("offer_price")) else None
    return m


def reg_rows(poss, den):
    """Per registration category: filers, shares, share of sh_13f and of the listed class. The five categories always sum to sh_13f (C16)."""
    ranked = rank_filers(poss)
    total = dsum(p.sh for p in ranked)
    by = collections.OrderedDict((c, [0, Decimal(0)]) for c in REG_CATEGORIES)
    for p in ranked:
        c = reg_category(p.secfile)
        if M("g9_reg_not_sum") and c == "none":
            continue
        by[c][0] += 1
        by[c][1] += p.sh
    return [(c, n, s, pct(s, total), pct(s, den.get("den_listed_10q_sh"))) for c, (n, s) in by.items() if n]


# ------------------------------------------------------------------------------------------------------------------------
# implied prices, duplicates (C03, C09)
# ------------------------------------------------------------------------------------------------------------------------
def implied_outliers(poss, tol=Decimal("0.01")):
    """Filers whose implied price is more than `tol` (1%) from the deal's median implied price (O-14). WARN, listed; shares are never changed."""
    ranked = rank_filers(poss)
    prices = [(p, p.price()) for p in ranked if p.price() is not None]
    if not prices:
        return None, []
    med = median_dec([v for _, v in prices])
    if M("g4_outlier_not_listed"):
        return med, []
    tol2 = tol if not M("g4_outlier_tol_2pct") else Decimal("0.02")
    return med, [(p, v) for p, v in prices if med > 0 and abs(v - med) / med > tol2]


def median_bounds_problem(med, offer, lo=Decimal("0.2"), hi=Decimal("5")):
    """C03: the deal's median implied price within 0.2-5x the offer price (FAIL)."""
    if M("g4_median_bounds_ignored") or med is None or not offer:
        return None
    r = med / offer
    return None if lo <= r <= hi else "median implied price %s is %s x the offer price %s" % (dstr(med, 2), dstr(r, 3), dstr(offer, 2))


def duplicate_suspects(poss, minimum=Decimal("10000")):
    """C09: CIK pairs reporting identical shares (>= 10,000) of the one identifier at one period; listed by rank, nothing removed."""
    if M("g10_dup_not_flagged"):
        return []
    ranked = rank_filers(poss)
    by = collections.defaultdict(list)
    for i, p in enumerate(ranked):
        if p.sh >= minimum:
            by[p.sh].append((i + 1, p))
    return [(sh, [(rk, p) for rk, p in lst]) for sh, lst in sorted(by.items(), key=lambda kv: -kv[0]) if len(lst) > 1]


# ------------------------------------------------------------------------------------------------------------------------
# denominators (section 2.3, G7): transcribed deal_inputs.csv -> the numbers
# ------------------------------------------------------------------------------------------------------------------------
DEAL_INPUT_FIELDS = tuple(ALLOW_TEXT.strip().split("\n")[0].split(":", 1)[1].split(","))


def int_shares(s, where=""):
    v = D_(s)
    if v is None:
        return None
    if v < 0 or v != v.to_integral_value():
        raise DataError("deal_inputs.csv: %s is not a non-negative whole number of shares: %r" % (where, s))
    return v


def deal_input_problems(rows):
    """Validation of the transcribed table: allowed values, placeholders, quote length, shapes. Returns a list of strings; empty is clean."""
    bad = []
    seen = set()
    for i, r in enumerate(rows, start=1):
        where = "row %d (%s %s)" % (i, r.get("ticker", ""), r.get("item", ""))
        if r.get("item") not in ITEMS:
            bad.append("%s: item %r is not allowed" % (where, r.get("item")))
        if r.get("is_listed_class") not in ("yes", "no", ""):
            bad.append("%s: is_listed_class %r" % (where, r.get("is_listed_class")))
        if r.get("ticker") not in DEAL_PATTERNS:
            bad.append("%s: unknown ticker" % where)
        k = (r.get("ticker"), r.get("class_label"), r.get("item"))
        if k in seen:
            bad.append("%s: duplicate key" % where)
        seen.add(k)
        if FIRST_TRADE_PLACEHOLDER in "|".join(r.values()):
            bad.append("%s: the first trading day is still the placeholder %s" % (where, FIRST_TRADE_PLACEHOLDER))
            continue
        q = r.get("quote", "")
        if len(q.split()) > 25:
            bad.append("%s: quote is %d words (limit 25)" % (where, len(q.split())))
        try:
            if r.get("item") in ("pricing_date", "first_trade_date"):
                parse_iso(r.get("asof"))
                if r.get("shares"):
                    bad.append("%s: shares must be blank on a date row" % where)
            elif r.get("item") == "offer_price_usd":
                v = D_(r.get("shares"))
                if v is None or v <= 0:
                    bad.append("%s: the offer price is not a positive number" % where)
            else:
                int_shares(r.get("shares"), where)
                if r.get("item") in ("qe_balance_sheet", "qe_cover"):
                    parse_iso(r.get("asof"))
                if not r.get("shares"):
                    bad.append("%s: blank shares" % where)
            if r.get("doc_filing_date"):
                parse_iso(r.get("doc_filing_date"))
        except DataError as e:
            bad.append("%s: %s" % (where, e))
        for col in ("class_label", "doc_form", "doc_section", "quote"):
            for tok in re.findall(r"(?<![0-9A-Za-z])[0-9A-Za-z]{9}(?![0-9A-Za-z])", r.get(col, "")):
                if cusip_check_ok(tok.upper()) and re.search(r"[A-Za-z]", tok[:8]):
                    bad.append("%s: %s holds an identifier-shaped token" % (where, col))
    return bad


def i2_class_filter(ticker, title):
    rx = I2_CLASS_RX.get(ticker)
    return True if not rx else bool(re.search(rx, title or "", re.I))


def denominators(rows, ticker, i2_rows=None):
    """The deal's denominators and dates from its deal_inputs rows (G7). A deal without a 10-Q has a BLANK primary: never the prospectus, never 0, never inferred
    from a 13D/13G percentage."""
    mine = [r for r in rows if r["ticker"] == ticker]
    d = {"ticker": ticker, "den_listed_10q_sh": None, "den_listed_10q_item": "", "den_listed_10q_asof": None, "den_listed_prosp_sh": None, "den_all_classes_10q_sh": None,
         "ipo_shares_base": None, "pricing_date": None, "first_trade_date": None, "first_trade_source": "", "listed_class": "", "offer_price": None}
    for r in mine:
        if r["item"] == "offer_price_usd":
            d["offer_price"] = D_(r["shares"])
        elif r["item"] == "pricing_date":
            d["pricing_date"] = parse_iso(r["asof"])
        elif r["item"] == "first_trade_date":
            d["first_trade_date"] = parse_iso(r["asof"])
            verb = "filed" if r["doc_form"] in ("10-Q", "424B4", "8-K") else "dated"
            d["first_trade_source"] = "%s %s %s, %s" % (r["doc_form"], verb, r["doc_filing_date"], r["doc_section"]) if r["doc_filing_date"] else "%s, %s" % (r["doc_form"], r["doc_section"])
    listed = sorted({r["class_label"] for r in mine if r["is_listed_class"] == "yes"})
    if len(listed) > 1:
        raise DataError("%s: more than one class marked is_listed_class" % ticker)
    cls_rows = [r for r in mine if r["item"] in ("qe_balance_sheet", "qe_cover", "after_offering_base", "ipo_shares_base")]
    if cls_rows and not listed:
        raise DataError("%s: no class is marked is_listed_class" % ticker)
    lc = listed[0] if listed else ""
    d["listed_class"] = lc

    def pick(item, label):
        for r in mine:
            if r["item"] == item and r["class_label"] == label:
                return r
        return None

    for r in mine:
        if r["item"] == "ipo_shares_base" and r["class_label"] == lc:
            d["ipo_shares_base"] = int_shares(r["shares"])
    if lc:
        bs, cv, ao = pick("qe_balance_sheet", lc), pick("qe_cover", lc), pick("after_offering_base", lc)
        order = [("qe_cover", cv), ("qe_balance_sheet", bs)] if M("g7_cover_over_balance") else [("qe_balance_sheet", bs), ("qe_cover", cv)]
        chosen = None
        for item, r in order:
            if r is not None:
                chosen = (item, r)
                break
        if ao is not None:
            d["den_listed_prosp_sh"] = int_shares(ao["shares"])
        if chosen:
            item, r = chosen
            d["den_listed_10q_sh"] = int_shares(r["shares"])
            d["den_listed_10q_item"] = item
            d["den_listed_10q_asof"] = parse_iso(r["asof"])
            allc = [x for x in mine if x["item"] == item]
            d["den_all_classes_10q_sh"] = dsum(int_shares(x["shares"]) for x in allc)
            if M("g7_all_classes_as_listed"):
                d["den_listed_10q_sh"] = d["den_all_classes_10q_sh"]
        if M("g7_prosp_for_primary") and d["den_listed_prosp_sh"] is not None:
            d["den_listed_10q_sh"] = d["den_listed_prosp_sh"]
            d["den_listed_10q_item"] = "qe_balance_sheet"
        if d["den_listed_10q_sh"] is None:
            if M("g7_blank_filled_prosp"):
                d["den_listed_10q_sh"] = d["den_listed_prosp_sh"]
            elif M("g7_blank_as_zero"):
                d["den_listed_10q_sh"] = Decimal(0)
            elif M("g7_class_from_13dg_pct") and i2_rows:
                for h in i2_rows:
                    if h["ticker"] == ticker and h.get("percent_of_class"):
                        d["den_listed_10q_sh"] = D_(h["shares_beneficially_owned"]) * 100 / D_(h["percent_of_class"])
                        break
    return d


# ------------------------------------------------------------------------------------------------------------------------
# pooled and weighted (method 8, G8)
# ------------------------------------------------------------------------------------------------------------------------
def weights(proceeds_by_ticker, measured):
    """w_d = primary base proceeds_d / sum over measured deals, unrounded Decimals (INNIO's is 0)."""
    tot = dsum(proceeds_by_ticker[t] for t in measured)
    out = {}
    for t in measured:
        w = proceeds_by_ticker[t] / tot if tot else Decimal(0)
        if t == "INIO" and M("g8_inio_weight"):
            w = Decimal("0.01")
        out[t] = w
    return out


def weight_identity_ok(w, tol=Decimal("1e-12")):
    vals = [qfix(v, 3) for v in w.values()] if M("g8_weights_rounded") else list(w.values())
    return abs(dsum(vals) - 1) < tol


def pooled_weighted(meas, w, exclude=()):
    """meas: {ticker: {sh_13f, den_listed_10q_sh, pct_of_listed}}; deals with a blank primary are excluded and named. Returns a dict of the figures."""
    use = [t for t in meas if t not in exclude or M("g8_exspcx_includes_spcx")]
    have = [t for t in use if meas[t]["den_listed_10q_sh"] is not None or M("g8_blank_in_pooled")]
    blank = [t for t in use if meas[t]["den_listed_10q_sh"] is None]
    out = {"tickers": have, "blank": blank}

    def den(t):
        return meas[t]["den_listed_10q_sh"] or Decimal(0)

    num = dsum(meas[t]["sh_13f"] for t in have)
    dn = dsum(den(t) for t in have)
    out["pooled_pct"] = pct(num, dn)
    out["pooled_num"], out["pooled_den"] = num, dn
    wt = dsum(w.get(t, Decimal(0)) for t in have)
    if have and wt > 0:
        out["weighted_pct"] = dsum((w.get(t, Decimal(0)) / wt) * (meas[t]["pct_of_listed"] if meas[t]["pct_of_listed"] is not None else Decimal(0)) for t in have)
    else:
        out["weighted_pct"] = None
    pcts = sorted(meas[t]["pct_of_listed"] for t in have if meas[t]["pct_of_listed"] is not None)
    out["median_pct"] = None if M("g8_no_median") else median_dec(pcts)
    out["min_pct"] = pcts[0] if pcts and not M("g8_no_median") else None
    out["max_pct"] = pcts[-1] if pcts and not M("g8_no_median") else None
    return out


# ------------------------------------------------------------------------------------------------------------------------
# the committed inputs: deal master, i2 holders, i2 pins, cornerstones (R7)
# ------------------------------------------------------------------------------------------------------------------------
def read_plain_csv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def read_master(path=None):
    rows = read_plain_csv(path or I2_MASTER)
    out = collections.OrderedDict()
    for r in rows:
        if r["ticker"] in DEAL_PATTERNS:
            out[r["ticker"]] = {"ticker": r["ticker"], "issuer": r["issuer"], "ipo_date": parse_iso(r["ipo_date"]), "proceeds": D_(r["base_proceeds_to_company_usd"]),
                                "counts": r["counts_toward_112bn_operating_co_total"].strip() == "True"}
    return out


def master_totals(master):
    in_scope = [m for m in master.values() if m["counts"] and m["ipo_date"].year == 2026]
    return dsum(m["proceeds"] for m in in_scope), len(in_scope)


def norm_person(s):
    return re.sub(r"[^A-Z0-9 ]", "", re.sub(r"\s+", " ", (s or "").upper().replace("&", " AND "))).strip()


def i2_latest(i2_rows, ticker, qe):
    """Method 7: per reporting person on the issuer, the latest filing whose event date is on or before the quarter-end, restricted to the listed class's rows."""
    best = {}
    for r in i2_rows:
        if r["ticker"] != ticker or not i2_class_filter(ticker, r.get("securities_class_title", "")):
            continue
        try:
            ev = parse_mdy(r["event_date_or_date_of_event"])
            fd = parse_iso(r["filing_date"])
        except DataError:
            continue
        if ev > qe:
            continue
        sh = D_(r["shares_beneficially_owned"])
        if sh is None:
            continue
        k = norm_person(r["reporting_person_name"])
        key = (ev, fd, r["accession_number"])
        if k not in best or key > best[k][0]:
            best[k] = (key, {"name": r["reporting_person_name"].strip(), "key": k, "form": r["form_type"].strip(), "type": r["type_of_reporting_person"].strip(), "event": ev,
                             "shares": sh, "filing": fd})
    return [v[1] for k, v in sorted(best.items())]


def read_i2_holders(path=None):
    return read_plain_csv(path or I2_HOLDERS)


# ------------------------------------------------------------------------------------------------------------------------
# the reviewed filer table (cache): public names, kinds, pre-IPO flags, i2 and cornerstone matches
# ------------------------------------------------------------------------------------------------------------------------
FILER_REVIEW_FIELDS = ("cik", "name", "name_public", "holder_kind", "kind_basis", "pre_ipo_flag", "i2_holder_match", "cornerstone_match")


def read_filer_review(path):
    hdr, rows = read_csv_rows(path)
    if tuple(hdr) != FILER_REVIEW_FIELDS:
        raise DataError("filer_review.csv header is not %s" % ",".join(FILER_REVIEW_FIELDS))
    out = []
    for r in rows:
        r = {k: (v or "").strip() for k, v in r.items()}
        if r["name_public"] not in ("yes", "no"):
            raise DataError("filer_review.csv: name_public must be yes or no for %r" % r["name"][:30])
        if r["holder_kind"] and r["holder_kind"] not in HOLDER_KINDS:
            raise DataError("filer_review.csv: holder_kind %r is not allowed" % r["holder_kind"])
        if r["kind_basis"] and r["kind_basis"] not in KIND_BASES:
            raise DataError("filer_review.csv: kind_basis %r is not allowed" % r["kind_basis"])
        if r["pre_ipo_flag"] not in ("", "no") and any(x.strip() not in DEAL_PATTERNS for x in r["pre_ipo_flag"].split(";")):
            raise DataError("filer_review.csv: pre_ipo_flag %r is not blank, no, or a ; list of tickers" % r["pre_ipo_flag"])
        out.append(r)
    return out


class Review:
    """The reviewed table as the build uses it: labels only ever come from here (R5, G12)."""

    def __init__(self, rows):
        self.rows = rows
        self.by_cik = {}
        self.by_name = {}
        for r in rows:
            if r["cik"]:
                self.by_cik[cik_key(r["cik"])] = r
            else:
                self.by_name[norm_person(r["name"])] = r
        self._withheld = {}

    def row(self, cik):
        return self.by_cik.get(cik_key(cik))

    def label(self, cik, scope=""):
        """A public name, or `withheld` (numbered within `scope` so that keys stay unique). A filer absent from the review is a DataError."""
        r = self.row(cik)
        if r is None:
            raise DataError("a filer needed for an output is not in filer_review.csv")
        if r["name_public"] == "yes" or M("g12_unreviewed_name_written"):
            return r["name"]
        return self._number("withheld", cik, scope)

    def _number(self, base, key, scope):
        d = self._withheld.setdefault(scope, {})
        if key not in d:
            d[key] = len(d) + 1
        return "%s #%d" % (base, d[key])

    def i2_label(self, person, scope=""):
        """An i2 reporting person: `individual (withheld)` for type IN; a public name only if the review marks that name public."""
        if person["type"] == "IN" and not M("g12_in_named"):
            return self._number("individual (withheld)", person["key"], scope)
        r = self.by_name.get(person["key"])
        if r is not None and r["name_public"] == "yes":
            return person["name"]
        if M("g12_i2_label_unreviewed"):
            return person["name"]
        return self._number("withheld", person["key"], scope)

    def match_keys(self, r):
        return [norm_person(x) for x in r["i2_holder_match"].split(";") if x.strip()]

    def filers_matching(self, person_key):
        return [r for r in self.rows if r["cik"] and person_key in self.match_keys(r)]

    def flagged_for(self, ticker):
        """Filers the review flags as holders of THIS issuer before its listing (a ; list of tickers in pre_ipo_flag): a hypothesis, deal by deal."""
        return [r for r in self.rows if r["cik"] and ticker in [x.strip() for x in r["pre_ipo_flag"].split(";")]]


# name heuristics for the PROPOSED review (the supervisor decides; these are hypotheses, not facts)
ORG_TOKENS = re.compile(r"\b(LLC|L\.?L\.?C|LP|L\.?P|LLP|LTD|LIMITED|INC|INCORPORATED|CORP|CORPORATION|CO|COMPANY|TRUST|BANK|BANCORP|N\.?A|GROUP|PARTNERS|CAPITAL|MANAGEMENT|MGMT|ADVISORS|ADVISERS|"
                        r"ADVISORY|INVESTMENTS?|INVESTORS|FUNDS?|ASSET|ASSETS|SECURITIES|FINANCIAL|HOLDINGS?|ASSOCIATES|WEALTH|PLC|SA|AG|NV|GMBH|UNIVERSITY|FOUNDATION|ENDOWMENT|RETIREMENT|PENSION|"
                        r"INSURANCE|ASSURANCE|LIFE|SYSTEM|SYSTEMS|FUTURES|STRATEGIES|ETF|SERVICES|RESEARCH|GLOBAL|INTERNATIONAL|COUNSEL|PRIVATE|OFFICE|OFFICES|TRUSTEES?|BOARD|STATE|PUBLIC|EMPLOYEES)\b", re.I)
KIND_RULES = (
    ("pension_endowment_sovereign", r"PENSION|RETIREMENT|ENDOWMENT|UNIVERSITY|FOUNDATION|TEACHERS|EMPLOYEES|NORGES|SOVEREIGN|INVESTMENT AUTHORITY|STATE OF|BOARD OF|TREASURER|PUBLIC"),
    ("insurer", r"INSURANCE|ASSURANCE|ANNUIT|REINSURANCE|\bLIFE\b"),
    ("venture_or_pre_ipo", r"VENTURE|FOUNDERS FUND|GIGAFUND|VALOR EQUITY|ANDREESSEN|SEQUOIA|KLEINER|BENCHMARK|GROWTH EQUITY|PRIVATE EQUITY|CAPRICORN"),
    ("hedge_fund", r"HEDGE|CITADEL|MILLENNIUM|TWO SIGMA|SHAW|RENAISSANCE|POINT72|BRIDGEWATER|\bAQR\b|ARBITRAGE|LONG/SHORT|OFFSHORE|MASTER FUND|ATREIDES|COATUE|TIGER|VIKING|D1 CAPITAL|DRAGONEER|MARSHALL WACE|SCHONFELD|BALYASNY"),
    ("bank_broker", r"\bBANK\b|BANCORP|SECURITIES|BROKER|MORGAN STANLEY|GOLDMAN|JPMORGAN|J\.?P\.? MORGAN|CITIGROUP|CITIBANK|BARCLAYS|\bUBS\b|WELLS FARGO|BANK OF AMERICA|JEFFERIES|CANTOR|STIFEL|RAYMOND JAMES|LPL|NATIONAL ASSOCIATION|\bN\.?A\.?\b"),
    ("corporate_strategic", r"\b(INC|CORP|CORPORATION|DEVICES|TECHNOLOGIES|COMPANY)\b"),
    ("asset_manager", r"MANAGEMENT|ADVISORS|ADVISERS|CAPITAL|ASSET|INVEST|FUND|WEALTH|TRUST|BLACKROCK|VANGUARD|\bFMR\b|STATE STREET|ROWE|INDEX|ETF|PARTNERS|ADVISORY|RESEARCH|GLOBAL"),
)
I2_TYPE_KIND = {"IA": "asset_manager", "BD": "bank_broker", "BK": "bank_broker", "IC": "insurer", "EP": "pension_endowment_sovereign", "CO": "corporate_strategic"}
CORNERSTONE_KEYS = {"FRVO": (("ATLAS POINT", "Atlas Point"), ("NORGES", "Norges Bank"), ("WELLINGTON", "Wellington Management"), ("CAPITAL RESEARCH GLOBAL", "Capital Research Global Investors"))}


def propose_kind(name, i2_types=()):
    for t in i2_types:
        if t in I2_TYPE_KIND:
            return I2_TYPE_KIND[t], "13g_type"
    u = (name or "").upper()
    for kind, rx in KIND_RULES:
        if re.search(rx, u):
            return kind, "name_review"
    return "other", "name_review"


def propose_public(name, i2_type=""):
    if i2_type == "IN":
        return "no"
    return "yes" if ORG_TOKENS.search(name or "") else "no"


def cik_name_map(scans):
    """{cik_key: name} from the base-report cover pages (cache only; a name is never printed to a committed file unless the review marks it public)."""
    out = {}
    for sc in scans:
        for s in sorted(sc.subs, key=Sub.key):
            if s.name and s.stype in ("13F-HR", "13F-HR/A"):
                out[cik_key(s.cik)] = s.name
    return out


def rows_index(scans):
    by = collections.defaultdict(list)
    subs_by_acc = {}
    for sc in scans:
        for s in sc.subs:
            subs_by_acc[s.acc] = s
        for r in sc.rows:
            by[r.acc].append(r)
    return subs_by_acc, by


def candidate_table(scans):
    """Review (a): each distinct (ticker, identifier, issuer name, class title) among name-matched rows with row and filer counts and the check digit's validity."""
    subs_by_acc, _ = rows_index(scans)
    agg = collections.OrderedDict()
    for sc in scans:
        for r in sc.rows:
            if not r.tick:
                continue
            k = (r.tick, r.cusip, r.name, r.title)
            a = agg.setdefault(k, {"rows": 0, "ciks": set(), "sh": Decimal(0), "sh_options": Decimal(0), "blank_value": 0, "prn": 0})
            a["rows"] += 1
            s = subs_by_acc.get(r.acc)
            a["ciks"].add(cik_key(s.cik) if s else r.acc)
            sh = D_(r.shares) or Decimal(0)
            if r.sh_type == "SH" and r.putcall == "":
                a["sh"] += sh
            elif r.sh_type == "SH":
                a["sh_options"] += sh
            else:
                a["prn"] += 1
            if D_(r.value) is None:
                a["blank_value"] += 1
    return agg


def conflict_table(scans):
    """Review (b): rows with a candidate identifier (that of some name-matched row of the deal) and a name that does not match the deal's pattern (C-059)."""
    cand = collections.defaultdict(set)
    for sc in scans:
        for r in sc.rows:
            if r.tick:
                cand[r.cusip].add(r.tick)
    agg = collections.OrderedDict()
    subs_by_acc, _ = rows_index(scans)
    for sc in scans:
        for r in sc.rows:
            if not r.tick and r.cusip in cand:
                k = (",".join(sorted(cand[r.cusip])), r.cusip, r.name, r.title)
                a = agg.setdefault(k, {"rows": 0, "ciks": set(), "sh": Decimal(0)})
                a["rows"] += 1
                s = subs_by_acc.get(r.acc)
                a["ciks"].add(cik_key(s.cik) if s else r.acc)
                if r.sh_type == "SH" and r.putcall == "":
                    a["sh"] += D_(r.shares) or Decimal(0)
    return agg


# ------------------------------------------------------------------------------------------------------------------------
# compute: the whole build as a pure function of the cache and the reviewed tables
# ------------------------------------------------------------------------------------------------------------------------
COVERAGE_MIN = 100
DEAL_ORDER = ("SPCX", "CBRS", "QNT", "FRVO", "INIO", "BSP", "SKHY", "JMKE")
UNIT_ND = {"pct": 3, "ratio": 4, "usd": 2}
C02_PINS = (        # (i2_13F_sample_holdings.csv data row, ticker, shares rows, VALUE of those rows, puts underlying, VALUE of the put rows, calls underlying, note of the relayed value)
    (1, "SPCX", "171826745", "29358317651", None, None, None, ""),
    (2, "SPCX", "120801820", "20640198965", None, None, None, ""),
    (3, "CBRS", "7011028", None, None, None, None, ""),
    (4, "CBRS", "0", None, "145700", "16340805", None, "relayed: 145,700 shares, VALUE 16,340,805, price 112.15; round 5 found them to be three PUT rows"),
    (5, "CBRS", "3110086", "687329006", None, None, "700000", "relayed: 3,810,086, which is the shares rows plus the calls (supervisor ruling R6-2)"),
    (6, "CBRS", "794467", "175577207", None, None, None, ""),
    (8, "QNT", "150000", None, None, None, None, "relayed: 145,071, which dropped the 4,929 sole-discretion row (supervisor ruling R6-2)"),
    (9, "FRVO", "20000", "584600", None, None, None, ""),
)


class Ctx:
    pass


def fmt_unit(v, unit):
    if v is None:
        return ""
    if unit in UNIT_ND:
        return dstr(v, UNIT_ND[unit])
    if unit == "count":
        return str(int(v))
    if unit == "shares":
        v = Decimal(v)
        return dstr(v) if v == v.to_integral_value() else dstr(v, 2)
    return str(v)


def coverage_rows(scans, results, vintage):
    """Method 12: per quarter-end and zip. Orphans and unknown types come from every filer; duplicates and repeated identifiers only from the deals' kept rows."""
    out = []
    acc_zip = {s.acc: sc.zip_name for sc in scans for s in sc.subs}
    for sc in sorted(scans, key=lambda s: s.zip_name):
        periods = sorted({s.period for s in sc.subs if s.period and is_quarter_end(s.period)})
        for qe in periods:
            subs = [s for s in sc.subs if s.period == qe]
            hr = [s for s in subs if s.stype == "13F-HR"]
            nt = [s for s in subs if s.stype == "13F-NT"]
            hr_ciks = {cik_key(s.cik) for s in hr}
            conf = {cik_key(s.cik) for s in hr if s.conf_omitted == "Y"}
            n_rest = sum(1 for s in subs if s.stype == "13F-HR/A" and s.amendtype == "RESTATEMENT")
            n_new = sum(1 for s in subs if s.stype == "13F-HR/A" and s.amendtype == "NEW HOLDINGS")
            rep = orph = dup = 0
            for (ck, period), res in results.items():
                if period != qe:
                    continue
                rep += sum(1 for a in res.repeats if acc_zip.get(a) == sc.zip_name)
                orph += sum(1 for a in res.orphans if acc_zip.get(a) == sc.zip_name)
                dup += sum(1 for a in res.dups if acc_zip.get(a) == sc.zip_name)
            late = sum(1 for s in hr if s.filing > due_date(qe))
            out.append([iso(qe), sc.zip_name, len(hr_ciks), len({cik_key(s.cik) for s in nt}), len(conf), dstr(pct(len(conf), len(hr_ciks)), 3) if hr_ciks else "", n_rest, n_new, rep, orph, dup,
                        late, vintage])
    return out


def zip_rows(scans, first_qes, vintage):
    out = []
    for sc in sorted(scans, key=lambda s: zip_window(s.zip_name)[1]):
        a, b = zip_window(sc.zip_name)
        has = any(s.stype == "13F-HR" and s.period in first_qes for s in sc.subs)
        out.append([sc.zip_name, iso(a), iso(b), sc.stamp["zip_bytes"], sc.stamp["zip_sha256"], sc.stamp["n_submissions"], sc.stamp["n_infotable_rows"],
                    "first_qe" if has else "pre_listing_control", vintage])
    return out


def revision_rows(scans, deals, listed, existing=None, map_rows_all=None):
    """Regenerated from every cached vintage, never appended to a file (G11): for each pair of consecutive cumulative vintages and each measured deal whose quarter
    already had filings in the earlier one, the shares in both."""
    ends = sorted({zip_window(sc.zip_name)[1] for sc in scans})
    out = list(existing or []) if M("g11_revisions_appended") else []
    for i in range(1, len(ends)):
        prev_sc = [sc for sc in scans if zip_window(sc.zip_name)[1] <= ends[i - 1]]
        new_sc = [sc for sc in scans if zip_window(sc.zip_name)[1] <= ends[i]]
        vals = []
        for group in (prev_sc, new_sc):
            subs = [s for sc in group for s in sc.subs]
            sba, rba = rows_index(group)
            res = consolidate_all(subs, rba, cusips=set(listed.values()), fatal_periods=None)
            vals.append((subs, sba, rba, res))
        for dl in deals:
            if dl["status"] != "measured" or dl["ticker"] not in listed:
                continue
            qe = dl["first_qe"]
            if not any(s.stype == "13F-HR" and s.period == qe for s in vals[0][0]):
                continue
            sh = []
            for subs, sba, rba, res in vals:
                p = holdings(res, sba, rba, dl["ticker"], listed[dl["ticker"]], qe, map_options(map_rows_all or []))
                sh.append(dsum(x.sh for x in p.values()))
            chg = sh[1] - sh[0]
            out.append(["13f_to_" + ends[i - 1].isoformat(), "13f_to_" + ends[i].isoformat(), dl["ticker"], iso(qe), dstr(sh[0]), dstr(sh[1]), dstr(chg), dstr(pct(chg, sh[0]), 3) if sh[0] else ""])
    return out


def i2_block(i2_rows, review, ticker, qe, poss, vintage):
    """Methods 7 and 10 for one deal: overlap rows, the typed 13D/13G count of holders with no 13F row, and the 13F shares of filers that also filed a 13D/13G."""
    persons = i2_latest(i2_rows, ticker, qe)
    rows, without, matched_ciks = [], Decimal(0), set()
    for p in sorted(persons, key=lambda p: (-p["shares"], p["key"])):
        fl = [r for r in review.filers_matching(p["key"]) if cik_key(r["cik"]) in poss and poss[cik_key(r["cik"])].n_rows > 0]
        sh13 = dsum(poss[cik_key(r["cik"])].sh for r in fl)
        for r in fl:
            matched_ciks.add(cik_key(r["cik"]))
        has = bool(fl)
        if not has:
            without += p["shares"]
        label = review.i2_label(p, ticker)
        indiv = label.startswith("individual (withheld)") and not M("g12_individual_shares_shown")
        # R6-17: no share count on the row of a person withheld as an individual, so that the person cannot be re-identified by matching counts against a named filer
        rows.append([ticker, iso(qe), label, p["form"], p["type"], iso(p["event"]), "" if indiv else dstr(p["shares"]), "yes" if has else "no", "" if indiv else dstr(sh13),
                     "" if indiv else dstr(p["shares"] - sh13), vintage])
    return rows, without, matched_ciks, persons


def cornerstone_rows(i1b, review, deal, poss, vintage):
    """Method 11: one aggregate row where no per-investor split is disclosed. Indicated interest up to a ceiling, in shares at the offer price."""
    t = deal["ticker"]
    if t not in CORNERSTONE_DEALS:
        return []
    label_deal = CORNERSTONE_DEALS[t]
    mine = [r for r in i1b if r["deal"].strip() == label_deal]
    if not mine or not deal["offer_price"]:
        return []
    m = re.search(r"aggregate\s+\$([\d,]+)\s+million", mine[0]["amount"])
    if not m:
        raise DataError("cornerstone amount not parsed for %s" % t)
    usd = Decimal(m.group(1).replace(",", "")) * 1000000
    ind = usd / deal["offer_price"]
    mapped = [r for r in review.rows if r["cik"] and r["cornerstone_match"].startswith(t + ":")]
    sh = dsum(poss[cik_key(r["cik"])].sh for r in mapped if cik_key(r["cik"]) in poss)
    n = sum(1 for r in mapped if cik_key(r["cik"]) in poss and poss[cik_key(r["cik"])].sh > 0)
    label = "%d named investors, aggregate (no per-investor split)" % len(mine)
    return [[t, label, dstr(usd, 2), dstr(deal["offer_price"], 2), dstr(ind, 2), iso(deal["first_qe"]), n, dstr(sh), dstr(pct(sh, ind), 3), vintage]]


def pin_observed(scans, i2_sample, row_no, listed_cusip):
    """C02: the accession's own rows for the mapped identifier, before consolidation. The accession is read from the committed i2 sample file by row number."""
    acc = i2_sample[row_no - 1]["accession_number"].strip()
    rows = [r for sc in scans for r in sc.rows if r.acc == acc and r.cusip == listed_cusip]
    present = any(s.acc == acc for sc in scans for s in sc.subs)
    sh = dsum(D_(r.shares) for r in rows if r.sh_type == "SH" and r.putcall == "")
    val = dsum(D_(r.value) or Decimal(0) for r in rows if r.sh_type == "SH" and r.putcall == "")
    puts = dsum(D_(r.shares) for r in rows if r.sh_type == "SH" and r.putcall == "PUT")
    calls = dsum(D_(r.shares) for r in rows if r.sh_type == "SH" and r.putcall == "CALL")
    pval = dsum(D_(r.value) or Decimal(0) for r in rows if r.sh_type == "SH" and r.putcall == "PUT")
    return present, sh, val, puts, pval, calls


def compute(scans, map_rows, deal_rows, master, i2_holders, i2_sample, i1b, review, cfg):
    c = Ctx()
    c.cfg = cfg
    zip_names = [sc.zip_name for sc in scans]
    c.vintage = vintage_of(zip_names)
    c.source = source_line(zip_names)
    c.zip_names = sorted(zip_names)
    listed = map_listed(map_rows)
    c.listed = listed
    c.map_rows = map_rows
    all_subs = [s for sc in scans for s in sc.subs]
    subs_by_acc, rows_by_acc = rows_index(scans)
    c.acc_problems = accession_problems(scans)
    hr_periods = {s.period for s in all_subs if s.stype == "13F-HR"}
    # ---- the deals
    inscope = [t for t in DEAL_ORDER if t in master and master[t]["counts"] and master[t]["ipo_date"].year == 2026]
    c.master_total, c.master_n = master_totals(master)
    c.deals, c.dens = [], {}
    for t in inscope:
        den = denominators(deal_rows, t, i2_holders if M("g7_class_from_13dg_pct") else None)
        if den["pricing_date"] is None:
            raise DataError("deal_inputs.csv has no pricing_date for %s" % t)
        pd_ = den["pricing_date"]
        basis = den["first_trade_date"] if (M("g5_first_trade_instead") and den["first_trade_date"]) else pd_
        fq = first_qe_after(basis)
        status = "measured" if fq in hr_periods else "awaiting_next_zip"
        dl = {"ticker": t, "issuer": master[t]["issuer"], "master_date": master[t]["ipo_date"], "pricing_date": pd_, "first_trade_date": den["first_trade_date"],
              "first_trade_source": den["first_trade_source"], "proceeds": master[t]["proceeds"], "offer_price": den["offer_price"], "ipo_shares_base": den["ipo_shares_base"],
              "first_qe": fq, "status": status, "den": den}
        c.deals.append(dl)
        c.dens[t] = den
    fatal = "all" if UNKNOWN_AMENDTYPE_SCOPE == "all" else {d["first_qe"] for d in c.deals if d["status"] == "measured"}
    results = consolidate_all(all_subs, rows_by_acc, cusips=set(listed.values()), fatal_periods=fatal)
    c.results = results
    c.measured = [d["ticker"] for d in c.deals if d["status"] == "measured"]
    c.awaiting = [d["ticker"] for d in c.deals if d["status"] != "measured"]
    for t in c.measured:
        if t not in listed:
            raise DataError("no listed identifier in the CUSIP map for the measured deal %s" % t)
    proceeds = {d["ticker"]: d["proceeds"] for d in c.deals}
    c.weights = weights(proceeds, c.measured)
    c.weights_ex = weights(proceeds, [t for t in c.measured if t != "SPCX"] if not M("g8_exspcx_includes_spcx") else c.measured)
    # ---- positions and measures per measured deal
    c.poss, c.meas, c.ranked, c.outliers, c.dups, c.medians = {}, {}, {}, {}, {}, {}
    c.i2, c.reg = {}, {}
    holdings_rows, top_rows, kind_rows, overlap_rows, reg_out, corner_rows = [], [], [], [], [], []
    for dl in c.deals:
        t = dl["ticker"]
        if dl["status"] != "measured":
            continue
        qe = dl["first_qe"]
        poss = holdings(results, subs_by_acc, rows_by_acc, t, listed[t], qe, map_options(map_rows))
        c.poss[t] = poss
        den = dict(dl["den"])
        den["offer_price"] = dl["offer_price"]
        m = deal_measures(poss, den)
        ranked = rank_filers(poss)
        c.ranked[t] = ranked
        i2rows, without, matched, persons = i2_block(i2_holders, review, t, qe, poss, c.vintage)
        flagged = {cik_key(r["cik"]) for r in review.flagged_for(t)}
        m["sh_pre_ipo_flagged"] = dsum(p.sh for p in ranked if cik_key(p.cik) in flagged)
        m["sh_13dg_holders_without_13f"] = without
        m["sh_13f_matched_i2"] = dsum(p.sh for p in ranked if cik_key(p.cik) in matched)
        c.meas[t] = m
        c.i2[t] = persons
        overlap_rows.extend(i2rows)
        med, outl = implied_outliers(poss)
        c.medians[t], c.outliers[t] = med, outl
        c.dups[t] = duplicate_suspects(poss)
        holdings_rows.append([t, iso(qe), m["n_filers"], dstr(m["sh_13f"]), dstr(m["sh_13f_sole"]), dstr(m["sh_pre_ipo_flagged"]), dstr(without),
                              dstr(m["pct_of_listed"], 3), dstr(m["pct_of_listed_prosp"], 3), dstr(m["pct_of_all_classes"], 3), dstr(m["ipo_shares_pct_of_listed"], 3),
                              dstr(m["pct_of_ipo_shares"], 3), dstr(m["top1_pct_of_13f"], 3), dstr(m["top10_pct_of_13f"], 3), dstr(m["top10_pct_of_listed"], 3),
                              dstr(m["sh_calls"]), dstr(m["sh_puts"]), m["n_filers_calls"], m["n_filers_puts"], dstr(m["sh_name_match_other_cusip"]),
                              dstr(m["median_implied_price_usd"], 2), dstr(m["implied_to_offer_ratio"], 4), m["n_rows_value_blank"], c.vintage])
        person_keys = {p["key"] for p in persons}
        for rk, p in enumerate(ranked[:10], start=1):
            r = review.row(p.cik)
            lab = review.label(p.cik, t)
            if M("g12_cik_written"):
                lab = lab + " " + p.cik
            if M("g12_accession_written"):
                lab = lab + " " + results[(cik_key(p.cik), qe)].base.acc
            filed = "yes" if r is not None and any(k in person_keys for k in review.match_keys(r)) else "no"
            top_rows.append([t, iso(qe), rk, lab, filed, dstr(p.sh), dstr(pct(p.sh, m["sh_13f"]), 3), dstr(pct(p.sh, den.get("den_listed_10q_sh")), 3), c.vintage])
            if not r["holder_kind"] or not r["kind_basis"]:
                raise DataError("filer_review.csv: a top-10 filer of %s has no holder_kind or kind_basis" % t)
            kind_rows.append([t, iso(qe), rk, lab, r["holder_kind"], r["kind_basis"], c.vintage])
        regs = reg_rows(poss, den)
        c.reg[t] = regs
        if cfg.get("secfile_is_regulatory", True) or M("g17_regcat_when_flag_false"):
            for cat, n, s, pc_all, pc_l in regs:
                reg_out.append([t, iso(qe), cat, n, dstr(s), dstr(pc_all, 3), dstr(pc_l, 3), c.vintage])
        corner_rows.extend(cornerstone_rows(i1b, review, dict(dl, ticker=t), poss, c.vintage))
    # ---- pooled and weighted
    measured_view = {t: {"sh_13f": c.meas[t]["sh_13f"], "den_listed_10q_sh": c.dens[t]["den_listed_10q_sh"], "pct_of_listed": c.meas[t]["pct_of_listed"]} for t in c.measured}
    c.pw_all = pooled_weighted(measured_view, c.weights)
    c.pw_ex = pooled_weighted(measured_view, c.weights_ex, exclude=("SPCX",))
    c.measured_proceeds = dsum(proceeds[t] for t in c.measured)
    c.measured_proceeds_ex = dsum(proceeds[t] for t in c.measured if t != "SPCX")
    c.spcx_proceeds = master["SPCX"]["proceeds"] if "SPCX" in master else Decimal(0)
    # ---- the tables
    T = collections.OrderedDict()
    deals_out = []
    for dl in c.deals:
        t, den = dl["ticker"], dl["den"]
        w = c.weights.get(t)
        deals_out.append([t, dl["issuer"], iso(dl["pricing_date"]), iso(dl["first_trade_date"]), dl["first_trade_source"], "yes", dstr(dl["proceeds"]),
                          dstr(w * 100, 3) if w is not None else "", dstr(dl["offer_price"], 2) if dl["offer_price"] is not None and dl["status"] == "measured" else "",
                          dstr(dl["ipo_shares_base"]) if dl["status"] == "measured" else "", iso(dl["first_qe"]), dl["status"], dstr(den["den_listed_10q_sh"]),
                          den["den_listed_10q_item"], iso(den["den_listed_10q_asof"]), dstr(den["den_listed_prosp_sh"]), dstr(den["den_all_classes_10q_sh"]), c.vintage])
    T["deals.csv"] = deals_out
    T["holdings.csv"] = holdings_rows
    T["reg_category.csv"] = reg_out
    T["top_filers.csv"] = top_rows
    T["kind_hypothesis.csv"] = kind_rows
    T["overlap_i2.csv"] = overlap_rows
    T["cornerstones.csv"] = corner_rows
    c.first_qes = {d["first_qe"] for d in c.deals if d["status"] == "measured"}
    T["coverage.csv"] = coverage_rows(scans, results, c.vintage)
    T["zips.csv"] = zip_rows(scans, c.first_qes, c.vintage)
    T["revisions.csv"] = revision_rows(scans, c.deals, listed, cfg.get("existing_revisions"), map_rows)
    c.tables = T
    c.scans = scans
    c.i2_sample, c.review, c.master = i2_sample, review, master
    c.subs_by_acc, c.rows_by_acc = subs_by_acc, rows_by_acc
    c.deal_rows = deal_rows
    T["summary.csv"] = summary_rows(c)
    c.checks = build_checks(c)
    return c


def S(rows, vintage, q, scope, ticker, qe, stat, value, unit, denom):
    rows.append([q, scope, ticker, qe, stat, fmt_unit(value, unit), unit, denom, vintage])


def summary_rows(c):
    v = c.vintage
    rows = []
    d112 = "eight 2026 deals' primary base proceeds, 111,941,660,492 usd"
    S(rows, v, "Q1", "measured_all", "", "", "measured_proceeds", c.measured_proceeds, "usd", "sum over the measured deals of primary base proceeds")
    S(rows, v, "Q1", "measured_all", "", "", "measured_proceeds_pct_of_112bn", pct(c.measured_proceeds, c.master_total), "pct", d112)
    S(rows, v, "Q1", "measured_ex_spcx", "", "", "measured_proceeds", c.measured_proceeds_ex, "usd", "sum over the measured deals except SPCX of primary base proceeds")
    S(rows, v, "Q1", "measured_ex_spcx", "", "", "measured_proceeds_pct_of_ex_spcx_total", pct(c.measured_proceeds_ex, c.master_total - c.spcx_proceeds), "pct",
      "the eight deals' proceeds without SpaceX, 36,941,660,567 usd")
    S(rows, v, "Q1", "measured_all", "SPCX", "", "spcx_weight_pct_of_measured", c.weights.get("SPCX", Decimal(0)) * 100, "pct", "measured deals' primary base proceeds")
    S(rows, v, "Q1", "measured_all", "", "", "n_measured_deals", Decimal(len(c.measured)), "count", "eight deals in the deal list")
    S(rows, v, "Q1", "measured_all", "", "", "n_awaiting_deals", Decimal(len(c.awaiting)), "count", "eight deals in the deal list")
    blank = [t for t in c.measured if c.dens[t]["den_listed_10q_sh"] is None]
    S(rows, v, "Q1", "measured_all", "", "", "n_measured_deals_with_blank_primary", Decimal(len(blank)), "count", "measured deals")
    for dl in c.deals:
        t = dl["ticker"]
        if t not in c.meas:
            continue
        m, qe, den = c.meas[t], iso(dl["first_qe"]), c.dens[t]
        dsh = "listed-class shares outstanding at %s (first 10-Q)" % iso(den["den_listed_10q_asof"]) if den["den_listed_10q_sh"] is not None else "no 10-Q: blank"
        S(rows, v, "Q2", "deal", t, qe, "sh_13f", m["sh_13f"], "shares", "listed-class shares reported on Form 13F (sum over filers)")
        S(rows, v, "Q2", "deal", t, qe, "n_filers", Decimal(m["n_filers"]), "count", "13F filers reporting shares of the listed class")
        S(rows, v, "Q2", "deal", t, qe, "sh_13f_sole", m["sh_13f_sole"], "shares", "sh_13f")
        S(rows, v, "Q2", "deal", t, qe, "sh_pre_ipo_flagged", m["sh_pre_ipo_flagged"], "shares", "sh_13f")
        S(rows, v, "Q2", "deal", t, qe, "sh_13dg_holders_without_13f", m["sh_13dg_holders_without_13f"], "shares", "typed Schedule 13D/13G counts, not a share of the class")
        S(rows, v, "Q2", "deal", t, qe, "pct_of_listed", m["pct_of_listed"], "pct", dsh)
        S(rows, v, "Q2", "deal", t, qe, "pct_of_listed_prosp", m["pct_of_listed_prosp"], "pct", "listed class outstanding after the offering, base case (424B4)")
        S(rows, v, "Q2", "deal", t, qe, "pct_of_all_classes", m["pct_of_all_classes"], "pct", "all common classes on the same 10-Q item")
        S(rows, v, "Q2", "deal", t, qe, "ipo_shares_pct_of_listed", m["ipo_shares_pct_of_listed"], "pct", dsh)
        S(rows, v, "Q2", "deal", t, qe, "pct_of_ipo_shares", m["pct_of_ipo_shares"], "pct", "shares sold in the offering, base case (memo; can exceed 100)")
        S(rows, v, "Q4", "deal", t, qe, "top1_pct_of_13f", m["top1_pct_of_13f"], "pct", "sh_13f")
        S(rows, v, "Q4", "deal", t, qe, "top10_pct_of_13f", m["top10_pct_of_13f"], "pct", "sh_13f")
        S(rows, v, "Q4", "deal", t, qe, "top10_pct_of_listed", m["top10_pct_of_listed"], "pct", dsh)
        for cat, n, s, pc_all, pc_l in c.reg[t]:
            S(rows, v, "Q5", "deal", t, qe, "pct_of_13f_" + cat, pc_all, "pct", "sh_13f")
        S(rows, v, "Q6", "deal", t, qe, "calls_pct_of_13f", pct(m["sh_calls"], m["sh_13f"]), "pct", "sh_13f")
        S(rows, v, "Q6", "deal", t, qe, "puts_pct_of_13f", pct(m["sh_puts"], m["sh_13f"]), "pct", "sh_13f")
        S(rows, v, "Q6", "deal", t, qe, "calls_pct_of_listed", pct(m["sh_calls"], den["den_listed_10q_sh"]), "pct", dsh)
        S(rows, v, "Q6", "deal", t, qe, "puts_pct_of_listed", pct(m["sh_puts"], den["den_listed_10q_sh"]), "pct", dsh)
        S(rows, v, "Q6", "deal", t, qe, "n_filers_calls", Decimal(m["n_filers_calls"]), "count", "13F filers in the deal's table")
        S(rows, v, "Q6", "deal", t, qe, "n_filers_puts", Decimal(m["n_filers_puts"]), "count", "13F filers in the deal's table")
        S(rows, v, "Q7", "deal", t, qe, "pct_of_13f_held_by_filers_that_also_filed_13d_13g", pct(m["sh_13f_matched_i2"], m["sh_13f"]), "pct", "sh_13f")
    for scope, pw in (("measured_all", c.pw_all), ("measured_ex_spcx", c.pw_ex)):
        den = "sum of listed-class quarter-end shares of the measured deals with a 10-Q: " + ", ".join(pw["tickers"])
        S(rows, v, "Q3", scope, "", "", "pooled_pct_of_listed", pw["pooled_pct"], "pct", den)
        S(rows, v, "Q3", scope, "", "", "weighted_pct_of_listed", pw["weighted_pct"], "pct", "proceeds-weighted mean of pct_of_listed, weights renormalised among deals with a 10-Q: " + ", ".join(pw["tickers"]))
        S(rows, v, "Q3", scope, "", "", "unweighted_median_pct_of_listed", pw["median_pct"], "pct", "pct_of_listed, deals with a 10-Q")
        S(rows, v, "Q3", scope, "", "", "unweighted_min_pct_of_listed", pw["min_pct"], "pct", "pct_of_listed, deals with a 10-Q")
        S(rows, v, "Q3", scope, "", "", "unweighted_max_pct_of_listed", pw["max_pct"], "pct", "pct_of_listed, deals with a 10-Q")
    S(rows, v, "Q3", "measured_all", "INIO", "", "weight_pct_of_measured", c.weights.get("INIO", Decimal(0)) * 100, "pct", "measured deals' primary base proceeds (INNIO's offering was all secondary)")
    for r in c.tables["coverage.csv"]:
        qe, zn = r[0], r[1]
        S(rows, v, "Q9", "measured_all", "", qe, "n_hr_filers_" + zn[:-4], Decimal(r[2]), "count", "13F-HR filers with this period in this zip")
        S(rows, v, "Q9", "measured_all", "", qe, "n_conf_omitted_" + zn[:-4], Decimal(r[4]), "count", "13F-HR filers with this period in this zip")
    S(rows, v, "Q10", "measured_all", "", "", "n_revision_rows", Decimal(len(c.tables["revisions.csv"])), "count", "30 Jun deals compared across consecutive vintages")
    for t, ref in SPCX_REFERENCE.items():
        if t in c.meas:
            S(rows, v, "Q11", "deal", t, iso(c.deals[[d["ticker"] for d in c.deals].index(t)]["first_qe"]), "sh_13f_over_reference_pct", pct(c.meas[t]["sh_13f"], ref), "pct",
              "published third-party aggregate for this deal at 30 Jun 2026 (reference only)")
    for t, cr in ((r[0], r) for r in c.tables["cornerstones.csv"]):
        S(rows, v, "Q8", "deal", t, cr[5], "pct_of_indicated_up_to", D_(cr[8]), "pct", "indicated interest, up to, in shares at the offer price (a ceiling)")
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# G15: wording. The patterns are pasted from the spec (section 7), not imported; bin/check.sh holds its own copy.
# ------------------------------------------------------------------------------------------------------------------------
CAUSAL_RX = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b", re.I)
EXTRA_RX = re.compile(r"\b(?:in|out)?flows?\b|\ballocat(?:e|ed|es|ing|ion|ions)\b|\b(?:ipo\s+)?buyers?\b|\bbought\b|\bpurchas(?:e|ed|es|ing)\b|\bdemand\b|\bappetite\b|\bsmart\s+money\b|"
                      r"\bpiled?\s+in(?:to)?\b|\bsnapped\s+up\b|\bdump(?:ed|ing|s)?\b|\bretail\b|\bunderpric(?:e|ed|ing)\b", re.I)
RESIDUAL_RX = re.compile(r"\b(?:rest|remainder|remaining|residual|balance)\b[^.]{0,80}\b(?:held|holds|owned|owns|belongs?|retail|insiders?|non-?filers?)\b", re.I)

README_S1 = ("This table counts the shares of the eight US IPOs of 2026 that raised about $1bn or more, set out in the deal list, that investment managers reported holding on "
             "Form 13F at the first calendar quarter-end after each listing.")
README_S2 = ("Form 13F is the quarterly holdings report that managers with at least $100 million in US-listed stocks file with the Securities and Exchange Commission, and each count "
             "is set against the shares the company had outstanding at that same quarter-end.")
DENIAL = ("Form 13F shows what each manager held at the quarter-end, not what it was allocated in the offering or when or at what price it bought, so none of these figures is an IPO "
          "allocation.")
REST_SENTENCE = "The part of the listed class not counted here is not a group of holders, and this table does not say who holds it."
HIGH_SENTENCE = "A high percentage can consist mostly of shares held by investors who owned the company before it listed."
VERBATIM = (README_S1 + " " + README_S2, DENIAL, REST_SENTENCE, HIGH_SENTENCE)


def wording_problems(name, text):
    """README.md only: no causal, flow, allocation, motive or residual-as-holder wording outside the one denial sentence (R6). The four verbatim sentences must be present."""
    if name != "README.md" or M("g15_off"):
        return []
    probs = []
    body = text
    if M("g15_denial_twice_ok"):
        body = body.replace(DENIAL, "")
    else:
        body = body.replace(DENIAL, "", 1)
    scans = []
    if not M("g15_causal_off"):
        scans.append(CAUSAL_RX)
    if not M("g15_extra_off"):
        scans.append(EXTRA_RX)
    if not M("g15_residual_off"):
        scans.append(RESIDUAL_RX)
    hits = sorted({re.sub(r"\s+", " ", m.group(0).lower()) for rx in scans for m in rx.finditer(body)})
    if hits:
        probs.append("README.md holds banned wording (R6): " + ", ".join(hits[:8]))
    if not M("g15_heading_ok") and re.search(r"^#+\s*Builder decisions", text, re.I | re.M):
        probs.append("README.md has a 'Builder decisions' heading (build decisions belong in SOURCES.md)")
    for s in VERBATIM:
        if s not in text:
            probs.append("README.md lacks the verbatim sentence: " + s[:50])
    return probs


# ------------------------------------------------------------------------------------------------------------------------
# G16: the leak guard over the committed folder (spec section 6)
# ------------------------------------------------------------------------------------------------------------------------
CSV_EXEMPT_RX = re.compile(r"(^sha256$|^sh_|_sh$|_sh_|^shares$|_shares$|^n_|_usd$|^bytes$|^rank$|date|^quarter_end$|^asof$|^first_qe$|^window_|^indicated_sh|^value$|_pct|^pct_|ratio|^change_|^gap_|^proceeds|^ipo_shares)", re.I)
FORBIDDEN_HEADER_RX = re.compile(r"cusip|isin|figi|^cik$|accession", re.I)
ISIN_RX = re.compile(r"(?<![0-9A-Za-z])[A-Z]{2}[0-9A-Z]{9}[0-9](?![0-9A-Za-z])")
FIGI_RX = re.compile(r"(?<![0-9A-Za-z])BBG[0-9A-Z]{9}(?![0-9A-Za-z])")
ACCESSION_RX = re.compile(r"\b\d{10}-\d{2}-\d{6}\b")
TOKEN9_RX = re.compile(r"(?<![0-9A-Za-z,.])[0-9A-Za-z]{9}(?![0-9A-Za-z,])")
PATH_RX = re.compile(r"/Users/|/private/|~")
RAW_EXT = (".tsv", ".zip", ".htm", ".html", ".pdf", ".json", ".xml", ".txt")


def body_lines(text):
    return [l for l in text.split("\n") if l.strip() != "" and not l.startswith("# source:")]


def cusip_like(tok, digits_ok):
    t = tok.upper()
    if not cusip_check_ok(t):
        return False
    return bool(re.search(r"[A-Z]", t[:8])) or digits_ok


def leak_problems(files, cusips=(), ciks=(), nonpublic_names=(), require_all=False):
    """files: {name: text}. Returns a list of strings; empty is clean. Mapped identifiers, filer numbers and unreviewed names are checked only when the cache supplies them."""
    bad = []
    allow = dict(l.split(":", 1) for l in ALLOW_TEXT.strip().split("\n"))
    for n in sorted(files):
        t = files[n]
        low = n.lower()
        if low.endswith(RAW_EXT):
            if not M("g16_skip_tsv"):
                bad.append("raw or unexpected file type: " + n)
            continue
        if n not in COMMITTED_NAMES:
            bad.append("file that is not one of the committed names: " + n)
            continue
        is_csv = n.endswith(".csv")
        if not M("g16_skip_path") and PATH_RX.search(t):
            bad.append(n + " contains a local path (/Users/, /private/ or a tilde)")
        if "@" in t:
            bad.append(n + " contains an at sign")
        if not M("g16_skip_accession") and ACCESSION_RX.search(t):
            bad.append(n + " contains an accession-number shape")
        if not M("g16_skip_isin") and ISIN_RX.search(t):
            bad.append(n + " contains an ISIN shape")
        if not M("g16_skip_figi") and FIGI_RX.search(t):
            bad.append(n + " contains a FIGI shape")
        if not is_csv and not M("g16_skip_cusip"):
            # prose: the letter shape and the bare 9-digit shape both count (numbers in prose are comma-grouped)
            if any(cusip_like(tok, True) for tok in set(TOKEN9_RX.findall(t))):
                bad.append("%s contains a CUSIP-shaped token" % n)
        if is_csv:
            lines = body_lines(t)
            if not lines:
                continue
            head = lines[0].rstrip("\r")
            if n in allow and head != allow[n]:
                bad.append("header of %s is not its exact allowlist" % n)
            cols = next(csv.reader([head]))
            canon = allow[n].split(",") if n in allow else []
            if not M("g16_skip_cikcol") and any(FORBIDDEN_HEADER_RX.search(cn) for cn in cols if cn not in canon):
                bad.append("%s has a column named like cusip, isin, figi, cik or accession" % n)
            found_cusip = found_cik = False
            for ri, r in enumerate(list(csv.reader(lines))[1:], start=2):
                for ci, cell in enumerate(r):
                    cn = cols[ci] if ci < len(cols) else ""
                    exempt = bool(CSV_EXEMPT_RX.search(cn)) and not M("g16_flag_shares")
                    if re.match(r"filer_", cn, re.I) and re.fullmatch(r"\d{1,10}", cell or ""):
                        bad.append("%s row %d: a CIK-shaped number in a filer column" % (n, ri))
                    if not found_cusip and not M("g16_skip_cusip"):
                        if any(cusip_like(tok, digits_ok=not exempt) for tok in TOKEN9_RX.findall(cell)):
                            bad.append("%s row %d column %s: a CUSIP-shaped token" % (n, ri, cn))
                            found_cusip = True
                    if not found_cik and not M("g16_skip_cik_cache") and not exempt:
                        for ck in ciks:
                            if len(ck) >= 5 and re.search(r"(?<![0-9,.])" + re.escape(ck) + r"(?![0-9,]|\.\d)", cell):
                                bad.append("%s row %d column %s: a filer number from the cache" % (n, ri, cn))
                                found_cik = True
                                break
        elif not M("g16_skip_cik_cache"):
            t_nohex = re.sub(r"\b[0-9a-f]{64}\b", "", t)
            for ck in ciks:
                if len(ck) >= 5 and re.search(r"(?<![0-9,.])" + re.escape(ck) + r"(?![0-9,]|\.\d)", t_nohex):
                    bad.append("%s contains a filer number from the cache" % n)
                    break
        if not M("g16_skip_cusip_cache"):
            for cu in cusips:
                if any(frag and re.search(r"(?<![0-9A-Za-z])" + re.escape(frag), t, re.I) for frag in {cu, cu[:8], cu[:6]}):
                    bad.append("%s contains a mapped identifier or its 8- or 6-character prefix" % n)
                    break
        if not M("g16_skip_name"):
            for nm in nonpublic_names:
                if nm and re.search(re.escape(nm), t, re.I):
                    bad.append("%s names a filer that the review does not mark public" % n)
                    break
    if require_all:
        for n in sorted(COMMITTED_NAMES - set(files)):
            bad.append("missing: " + n)
    return bad


def duplicate_key_problems(name, text):
    if name not in KEYS:
        return []
    lines = body_lines(text)
    if not lines:
        return []
    rd = list(csv.reader(lines))
    head = rd[0]
    try:
        idx = [head.index(k) for k in KEYS[name]]
    except ValueError:
        return ["%s lacks a key column" % name]
    seen, dup = set(), []
    for r in rd[1:]:
        k = tuple(r[i] if i < len(r) else "" for i in idx)
        if k in seen:
            dup.append(k)
        seen.add(k)
    return ["duplicate key in %s: %s (%d duplicate row(s))" % (name, "|".join(dup[0]), len(dup))] if dup else []


def allow_problems(text=None):
    """The canonical block hashes to the pinned value (R11 supervisor hash step) and names thirteen CSVs."""
    t = ALLOW_TEXT if text is None else text
    probs = []
    if hashlib.sha256(t.encode("utf-8")).hexdigest() != SPEC_ALLOW_SHA256:
        probs.append("the header allowlist text does not hash to SPEC_ALLOW_SHA256")
    if len(t.strip().split("\n")) != 13:
        probs.append("the header allowlist is not thirteen lines")
    return probs


# ------------------------------------------------------------------------------------------------------------------------
# G14: the static scan of this script's own source (R1, R2)
# ------------------------------------------------------------------------------------------------------------------------
BANNED_MODULES = ("urllib", "urllib3", "http", "httpx", "aiohttp", "requests", "socket", "ssl", "ftplib", "webbrowser", "subprocess", "pty")
DANGEROUS_CALLS = frozenset({"remove", "unlink", "replace", "rename", "rmtree", "move", "truncate", "removedirs", "rmdir", "touch", "write_text", "write_bytes", "copy", "copy2",
                             "copyfile", "copytree"})
PROCESS_CALLS = frozenset({"system", "popen", "execv", "execve", "execvp", "execl", "execle", "execlp", "execvpe", "execlpe", "fork", "spawnl", "spawnv", "posix_spawn"})


def static_problems(src):
    """AST scan: no network or process import; no os.system/os.popen/os.exec*; nothing that deletes, renames, overwrites or truncates a STOP path; no write-mode open of
    one; no zip-member literal that names SIGNATURE outside the FORBIDDEN_MEMBERS definition (G12)."""
    probs = []
    if M("g14_scan_off"):
        return probs
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return ["source does not parse: %s" % e]
    forbidden_def = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "FORBIDDEN_MEMBERS" for t in node.targets):
            for sub in ast.walk(node):
                forbidden_def.add(id(sub))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] in BANNED_MODULES:
                    probs.append("line %d: import %s" % (node.lineno, a.name))
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in BANNED_MODULES:
                probs.append("line %d: from %s import" % (node.lineno, node.module))
        elif isinstance(node, ast.Call):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            recv = ast.unparse(f.value) if isinstance(f, ast.Attribute) else ""
            parts = [ast.unparse(a) for a in node.args] + [ast.unparse(k.value) for k in node.keywords]
            text = " ".join(parts + [recv])
            if name in PROCESS_CALLS and recv.endswith("os"):
                probs.append("line %d: os.%s" % (node.lineno, name))
            if name in DANGEROUS_CALLS and re.search(r"stop", text, re.I):
                probs.append("line %d: %s reaches a STOP path (%s)" % (node.lineno, name, text[:60]))
            if name == "open" and parts and re.search(r"stop", parts[0], re.I):
                mode = None
                if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                    mode = node.args[1].value
                for k in node.keywords:
                    if k.arg == "mode" and isinstance(k.value, ast.Constant):
                        mode = k.value.value
                if mode is not None and any(ch in str(mode) for ch in "wa+x"):
                    probs.append("line %d: open of a STOP path in mode %r" % (node.lineno, mode))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and re.search(r"SIGNATURE\.tsv", node.value) and id(node) not in forbidden_def and not M("g12_ast_scan_skip"):
            if len(node.value) < 40:
                probs.append("line %d: string names the signature table outside FORBIDDEN_MEMBERS" % node.lineno)
    return probs


def own_source():
    with open(os.path.abspath(__file__), encoding="utf-8") as fh:
        return fh.read()


# ------------------------------------------------------------------------------------------------------------------------
# the pinned checks (section 8): checks.csv rows, and the lists SOURCES.md shows for the acceptable WARNs
# ------------------------------------------------------------------------------------------------------------------------
def safe_label(review, cik, scope):
    r = review.row(cik)
    if r is None:
        return "filer outside the review"
    return review.label(cik, scope)


def build_checks(c):
    cfg, rv = c.cfg, c.review
    rows, c.lists = [], collections.OrderedDict()

    def chk(cid, desc, expected, observed, status):
        rows.append([cid, desc, expected, observed, status])

    def st(ok, bad="FAIL"):
        return "PASS" if ok else bad

    m = c.master
    # C01 -------------------------------------------------------------------------------------------------------------
    chk("C01a", "Deal master: the eight 2026-priced rows that count toward the total sum to the page's 112bn (IDENTITY)", "111941660492 usd over 8 deals",
        "%s usd over %d deals" % (dstr(c.master_total), c.master_n), st(c.master_total == TOTAL_112 and c.master_n == 8))
    same = sorted(c.measured) == sorted(MEASURED_NOW)
    chk("C01b", "Measured deals are SPCX, CBRS, QNT, FRVO, INIO and their primary base proceeds sum to 84,119,999,925 usd = 75.146% of the total (IDENTITY)",
        "84119999925 usd; 75.146 pct of 111941660492", "%s usd; %s pct of %s; deals %s" % (dstr(c.measured_proceeds), dstr(pct(c.measured_proceeds, c.master_total), 3), dstr(c.master_total), ",".join(sorted(c.measured))),
        st(same and c.measured_proceeds == Decimal("84119999925") and dstr(pct(c.measured_proceeds, c.master_total), 3) == "75.146"))
    ex = c.measured_proceeds_ex
    chk("C01c", "Without SpaceX the measured proceeds are 9,120,000,000 usd = 24.688% of 36,941,660,567 usd (IDENTITY)", "9120000000 usd; 24.688 pct of 36941660567",
        "%s usd; %s pct of %s" % (dstr(ex), dstr(pct(ex, c.master_total - m["SPCX"]["proceeds"]), 3), dstr(c.master_total - m["SPCX"]["proceeds"])),
        st(same and ex == Decimal("9120000000") and dstr(pct(ex, c.master_total - m["SPCX"]["proceeds"]), 3) == "24.688" and c.master_total - m["SPCX"]["proceeds"] == TOTAL_112_EXSPCX))
    obs_w = {t: dstr(w * 100, 3) for t, w in c.weights.items()}
    obs_wx = {t: dstr(w * 100, 3) for t, w in c.weights_ex.items()}
    chk("C01d", "Weights as a percent of measured proceeds, with and without SpaceX (IDENTITY)", json.dumps({"all": WEIGHT_PINS, "ex_spcx": WEIGHT_PINS_EX}, sort_keys=True),
        json.dumps({"all": obs_w, "ex_spcx": obs_wx}, sort_keys=True), st(same and all(obs_w.get(k) == v for k, v in WEIGHT_PINS.items()) and all(obs_wx.get(k) == v for k, v in WEIGHT_PINS_EX.items())))
    # C02 -------------------------------------------------------------------------------------------------------------
    sample_ok = len(c.i2_sample) >= 9
    for row_no, t, e_sh, e_val, e_puts, e_pval, e_calls, note in C02_PINS:
        cid = "C02-r%d" % row_no
        if not sample_ok or t not in c.listed:
            chk(cid, "Pin: i2 sample row %d (%s), the accession's own rows for the mapped identifier, before consolidation" % (row_no, t), e_sh, "not testable: no mapped identifier or sample row", "FAIL")
            continue
        present, sh, val, puts, pval, calls = pin_observed(c.scans, c.i2_sample, row_no, c.listed[t])
        exp = "shares %s" % e_sh + (", VALUE %s" % e_val if e_val else "") + (", puts %s, put VALUE %s" % (e_puts, e_pval) if e_puts else "") + (", calls %s" % e_calls if e_calls else "")
        obs = "accession not in the zips read" if not present else "shares %s, VALUE %s, puts %s, put VALUE %s, calls %s" % (dstr(sh), dstr(val), dstr(puts), dstr(pval), dstr(calls))
        ok = present and dstr(sh) == e_sh and (e_val is None or dstr(val) == e_val) and (e_puts is None or (dstr(puts) == e_puts and dstr(pval) == e_pval)) and (e_calls is None or dstr(calls) == e_calls)
        chk(cid, "Pin: i2 sample row %d (%s), the accession's own rows for the mapped identifier, before consolidation (pin corrected: %s)" % (row_no, t, note or "as relayed") if note else
            "Pin: i2 sample row %d (%s), the accession's own rows for the mapped identifier, before consolidation" % (row_no, t), exp, obs, st(ok))
    # C03 -------------------------------------------------------------------------------------------------------------
    price1 = None
    if sample_ok and "SPCX" in c.listed:
        present, sh, val, puts, pval, calls = pin_observed(c.scans, c.i2_sample, 1, c.listed["SPCX"])
        price1 = (val / sh) if sh else None
    chk("C03a", "Units: SPCX sample row 1, VALUE over SSHPRNAMT, whole dollars", "170.86", dstr(price1, 2) if price1 is not None else "not testable", st(price1 is not None and dstr(price1, 2) == "170.86"))
    probs = []
    for t in c.measured:
        pbm = median_bounds_problem(c.medians.get(t), c.dens[t]["offer_price"])
        if pbm:
            probs.append("%s: %s" % (t, pbm))
    chk("C03b", "Units: each deal's median implied price is within 0.2 to 5 times the offer price", "all five within bounds", "; ".join("%s %s x" % (t, dstr(c.medians[t] / c.dens[t]["offer_price"], 3)) for t in c.measured if c.medians.get(t) and c.dens[t]["offer_price"]) or "none computed",
        st(not probs))
    n_out = {t: len(c.outliers[t]) for t in c.measured}
    chk("C03c", "Units: filers whose implied price is more than 1% from their deal's median (listed; reasons include VALUE reported in thousands and rounding on small positions)", "listed",
        ", ".join("%s %d of %d filers" % (t, n_out[t], len(c.ranked[t])) for t in c.measured), "WARN" if any(n_out.values()) else "PASS")
    for t in c.measured:
        lst = []
        for p, v in sorted(c.outliers[t], key=lambda x: -x[0].sh)[:12]:
            lst.append("%s: %s shares, implied price %s against median %s" % (safe_label(rv, p.cik, t + "-out"), dstr(p.sh), dstr(v, 2), dstr(c.medians[t], 2)))
        c.lists["C03c " + t] = lst
    # C04 -------------------------------------------------------------------------------------------------------------
    pre = {}
    for t in c.listed:
        dl = next((d for d in c.deals if d["ticker"] == t), None)
        if dl is None:
            continue
        rws = [(r, c.subs_by_acc.get(r.acc)) for sc in c.scans for r in sc.rows if r.cusip == c.listed[t]]
        early = [(r, s) for r, s in rws if s is not None and s.period is not None and s.period < dl["pricing_date"]]
        pre[t] = (len(early), len({cik_key(s.cik) for r, s in early}), dsum(D_(r.shares) or Decimal(0) for r, s in early if r.sh_type == "SH" and r.putcall == ""))
    chk("C04", "Pre-listing rows: rows of a mapped identifier whose report period is before the pricing date, in any zip read (listed; no measure or denominator changes)", "listed",
        ", ".join("%s %d rows / %d filers / %s shares" % (t, a, b, dstr(s)) for t, (a, b, s) in sorted(pre.items())) or "none", "WARN" if any(a for a, b, s in pre.values()) else "PASS")
    # C05 -------------------------------------------------------------------------------------------------------------
    conflict = {}
    for t in c.listed:
        rws = [r for sc in c.scans for r in sc.rows if r.cusip == c.listed[t] and r.tick != t]
        conflict[t] = (len(rws), sorted({r.name for r in rws})[:5])
    if M("g3_nonmatching_name_not_listed"):
        conflict = {t: (0, []) for t in conflict}
    chk("C05a", "Name and identifier: rows of a mapped identifier whose issuer name does not match the deal's pattern (listed)", "listed", ", ".join("%s %d" % (t, n) for t, (n, _) in sorted(conflict.items())) or "none",
        "WARN" if any(n for n, _ in conflict.values()) else "PASS")
    c.lists["C05a"] = ["%s: %d row(s) under other issuer names, e.g. %s" % (t, n, "; ".join(nm)) for t, (n, nm) in sorted(conflict.items()) if n]
    big = [(t, c.meas[t]["sh_name_match_other_cusip"], c.meas[t]["sh_13f"]) for t in c.measured if c.meas[t]["sh_13f"] and c.meas[t]["sh_name_match_other_cusip"] > c.meas[t]["sh_13f"] / 100]
    chk("C05b", "Name and identifier: shares in rows that match the deal's name but carry an unmapped identifier, above 1% of sh_13f", "none above 1 pct",
        ", ".join("%s %s shares = %s pct of sh_13f" % (t, dstr(o), dstr(pct(o, s), 3)) for t, o, s in big) or "none above 1 pct", "WARN" if big else "PASS")
    # C06 -------------------------------------------------------------------------------------------------------------
    bad06 = [t for t, cu in c.listed.items() if not cusip_check_ok(cu)]
    chk("C06", "Every mapped identifier passes its check digit", "all valid", "%d mapped, %d invalid" % (len(c.listed), len(bad06)), st(not bad06))
    # C07 -------------------------------------------------------------------------------------------------------------
    over = ["%s %s" % (t, k) for t in c.measured for k in ("pct_of_listed", "top10_pct_of_13f") if c.meas[t][k] is not None and c.meas[t][k] > 100]
    chk("C07", "Bounds: pct_of_listed or top10_pct_of_13f above 100 (listed)", "none above 100", ", ".join(over) or "none above 100", "WARN" if over else "PASS")
    # C08 -------------------------------------------------------------------------------------------------------------
    n_bsp = 0
    if "BSP" in c.listed:
        n_bsp = sum(1 for sc in c.scans for r in sc.rows if r.cusip == c.listed["BSP"] and (c.subs_by_acc.get(r.acc) is not None and c.subs_by_acc[r.acc].period == dt.date(2026, 6, 30)))
    chk("C08", "BSP at 30 Jun 2026: rows of its mapped identifier (they enter no measure)", "count only", ("%d rows" % n_bsp) if "BSP" in c.listed else "no identifier mapped for BSP", "WARN" if n_bsp else "INFO")
    # C09 -------------------------------------------------------------------------------------------------------------
    nd = {t: len(c.dups[t]) for t in c.measured}
    chk("C09", "Duplicate suspects: pairs of filer numbers reporting identical shares (10,000 or more) of one identifier at one period (listed by rank; nothing removed)", "listed",
        ", ".join("%s %d group(s)" % (t, n) for t, n in nd.items()), "WARN" if any(nd.values()) else "PASS")
    for t in c.measured:
        c.lists["C09 " + t] = ["%s shares reported identically by ranks %s" % (dstr(sh), ", ".join(str(rk) for rk, _ in lst)) for sh, lst in c.dups[t][:10]]
    # C10 -------------------------------------------------------------------------------------------------------------
    anom = collections.Counter()
    for (ck, period), res in c.results.items():
        if period in c.first_qes:
            anom["several originals"] += 1 if res.severals else 0
            anom["orphan amendments"] += len(res.orphans)
            anom["duplicate amendments"] += len(res.dups)
            anom["new-holdings amendments repeating an identifier"] += len(res.repeats)
            anom["restatements not later than the original"] += len(res.stale)
            anom["13F-HR whose cover page says amendment"] += len(res.mislabelled)
            anom["new-holdings amendments superseded by a restatement"] += len(res.superseded)
    if c.results.unknown:
        anom["amendments with an unknown AMENDMENTTYPE, all periods read (a filing at a measured quarter-end would refuse the build, R6-1)"] += len(c.results.unknown)
    chk("C10", "Amendment anomalies at the measured quarter-ends (several originals and orphans over all filers; duplicates and repeats over the deals' rows)", "listed",
        ", ".join("%s %d" % (k, v) for k, v in sorted(anom.items())) or "none", "WARN" if any(anom.values()) else "PASS")
    # C11 -------------------------------------------------------------------------------------------------------------
    zp = list(cfg.get("zip_problems", []))
    chk("C11", "Accessions are unique across zips; each cached zip's size and sha256 equal its stamp", "none", "; ".join(c.acc_problems + zp) or "none", st(not (c.acc_problems or zp)))
    # C12 -------------------------------------------------------------------------------------------------------------
    det = cfg.get("determinism", "pending")
    chk("C12", "Fixed output: a second render of every file is byte-identical", "identical", {"pending": "pending", True: "identical", False: "DIFFERS"}.get(det, str(det)),
        "PASS" if det is True else ("FAIL" if det is False else "INFO"))
    # C13 -------------------------------------------------------------------------------------------------------------
    gates = cfg.get("gates", [])
    chk("C13", "Gates: the three reviewed constants match their files and the cache is stamped with the CUSIP map's hash (review dates in SOURCES.md)", "all three match", "; ".join("%s %s" % (n, "ok" if ok else d) for n, ok, d in gates) or "not run",
        st(bool(gates) and all(ok for _, ok, _ in gates)))
    # C14 -------------------------------------------------------------------------------------------------------------
    miss = list(cfg.get("fields_missing", []))
    pr = allow_problems()
    chk("C14", "Headers and readme: every field of section 2.2 present in the zips; the readme definitions of R11 recorded in SOURCES.md; the allowlist hash", "none missing", "; ".join(miss + pr) or "none missing", st(not (miss or pr)))
    # C15 -------------------------------------------------------------------------------------------------------------
    cov = c.tables["coverage.csv"]
    chk("C15", "Coverage: 13F-HR filers per quarter-end and zip (quarter-ends with at least %d filers; coverage.csv has every period seen, including a few late filings for old periods)" % COVERAGE_MIN, "info",
        "; ".join("%s %s: %s HR filers" % (r[0], r[1][:-4], r[2]) for r in cov if int(r[2]) >= COVERAGE_MIN), "INFO")
    # C16 -------------------------------------------------------------------------------------------------------------
    id_bad = []
    for t in c.measured:
        tot = c.meas[t]["sh_13f"]
        if cfg.get("secfile_is_regulatory", True):
            if sum((r[2] for r in c.reg[t]), Decimal(0)) != tot:
                id_bad.append("%s: reg_category does not sum to sh_13f" % t)
        if dsum(p.sh for p in c.ranked[t][:10]) > tot:
            id_bad.append("%s: top-10 exceeds sh_13f" % t)
        if c.meas[t]["sh_13f_sole"] > tot:
            id_bad.append("%s: sh_13f_sole exceeds sh_13f" % t)
    if not weight_identity_ok(c.weights) or (c.weights_ex and not weight_identity_ok(c.weights_ex)):
        id_bad.append("unrounded weights do not sum to 1 within 1e-12")
    chk("C16", "Identities: the reg_category rows sum to sh_13f; the top ten sum to at most sh_13f; sh_13f_sole is at most sh_13f; unrounded weights sum to 1 within 1e-12", "hold", "; ".join(id_bad) or "hold", st(not id_bad))
    # C17 -------------------------------------------------------------------------------------------------------------
    parts = []
    for t in c.measured:
        ps = c.poss[t].values()
        parts.append("%s: PRN %d, calls %d, puts %d, blank VALUE %d, non-integral %d, other type %d, other PUTCALL %d, of the call and put rows %d rows / %s shares underlying sit under the Official List's option identifiers (counted in sh_calls and sh_puts, never in sh_13f), option rows under unlisted identifier variants (not counted) %d rows / %s shares underlying" % (
            t, sum(p.n_prn for p in ps), sum(p.n_calls_rows for p in ps), sum(p.n_puts_rows for p in ps), sum(p.n_value_blank for p in ps), sum(p.n_nonint for p in ps),
            sum(p.n_other_type for p in ps), sum(p.n_other_pc for p in ps), sum(p.n_optid for p in ps), dstr(dsum(p.optid_sh for p in ps)), sum(p.n_other_opt for p in ps), dstr(dsum(p.other_opt for p in ps))))
    chk("C17", "Excluded rows per deal (rows of the mapped identifier, before and after consolidation as counted on the consolidated reports)", "info", "; ".join(parts), "INFO")
    # C18 -------------------------------------------------------------------------------------------------------------
    gaps = []
    for t in c.measured:
        q, p = c.dens[t]["den_listed_10q_sh"], c.dens[t]["den_listed_prosp_sh"]
        if q is not None and p:
            g = abs(q - p) / p * 100
            if g > 15:
                gaps.append("%s: 10-Q %s against prospectus %s (%s pct)" % (t, comma(q), comma(p), dstr(g, 1)))
    chk("C18", "Typed counts: the listed class's quarter-end 10-Q count against its prospectus count after the offering; gap over 15% listed (typed share counts only)", "listed", "; ".join(gaps) or "no gap over 15 pct", "WARN" if gaps else "PASS")
    # C19 -------------------------------------------------------------------------------------------------------------
    bad19, obs19 = [], []
    for t, ref in SPCX_REFERENCE.items():
        if t in c.meas:
            sh = c.meas[t]["sh_13f"]
            dev = (sh - ref) / ref * 100
            obs19.append("%s %s against %s (%s pct)" % (t, comma(sh), comma(ref), dstr(dev, 2)))
            if abs(dev) > 2:
                bad19.append(t)
    chk("C19", "Reference aggregates: sh_13f at 2026-06-30 within 2% of the published SPCX 3,685,578,550 and CBRS 88,744,964 (reference only; a miss is a result, not tuned)", "within 2 pct", "; ".join(obs19) or "not measured", "WARN" if bad19 else "PASS")
    # C20 -------------------------------------------------------------------------------------------------------------
    blank = [t for t in c.measured if c.dens[t]["den_listed_10q_sh"] is None]
    chk("C20", "Blank primary: measured deals with no first 10-Q (their percentage stays blank)", "count and tickers", "%d: %s" % (len(blank), ",".join(blank) or "none"), "INFO")
    # C21 -------------------------------------------------------------------------------------------------------------
    ev = {r["ticker"]: r["evidence"] for r in c.map_rows if r["status"] == "listed"}
    not_official = [t for t in c.measured if ev.get(t) != "official_list_2026q2"]
    chk("C21", "Official List: each mapped identifier appears in the SEC Official List treated as governing the June reports (its title page reads \"Second Quarter FY 2026\" and prints no as-of date; supervisor ruling R6-10; the supervisor's reading is the map's evidence)", "official_list_2026q2",
        ", ".join("%s %s" % (t, ev.get(t) or "none") for t in c.measured), "WARN" if not_official else "PASS")
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# README.md (generated; G15 scans it) and SOURCES.md
# ------------------------------------------------------------------------------------------------------------------------
SHORT = {"SPCX": "SpaceX", "CBRS": "Cerebras", "QNT": "Quantinuum", "FRVO": "Fervo Energy", "INIO": "INNIO", "BSP": "Bending Spoons", "SKHY": "SK hynix", "JMKE": "Jersey Mike's"}
LISTED_CLASS_WORDS = {"SPCX": "Class A", "CBRS": "Class A", "QNT": "Class A", "FRVO": "Class A", "INIO": "common shares"}
REG_WORDS = {"ria_801": "801- (registered investment adviser)", "era_802": "802- (exempt reporting adviser)", "bd_8": "8- (broker-dealer)", "other_prefix": "another prefix", "none": "no number declared"}


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def pc(v, nd=1):
    return (dstr(v, nd) + "%") if v is not None else "blank"


def render_readme(c):
    v = c.vintage
    meas = [t for t in DEAL_ORDER if t in c.meas]
    awaiting = [d for d in c.deals if d["status"] != "measured"]
    names = lambda ts: ", ".join("%s (%s)" % (SHORT[t], t) for t in ts)
    first_qe_txt = long_date(c.deals[[d["ticker"] for d in c.deals].index(meas[0])]["first_qe"]) if meas else "the quarter-end"
    L = []
    L.append("# Who held the 2026 IPOs: Form 13F holdings at the first quarter-end\n")
    L.append(README_S1 + " " + README_S2 + "\n")
    L.append(DENIAL + " " + REST_SENTENCE + "\n")
    # 3: which deals
    L.append("## Which deals are measured\n")
    mp = pct(c.measured_proceeds, c.master_total)
    s = ("%d of the %d deals have their first quarter-end on %s and are measured here: %s. Their primary base proceeds to the company, %s, are %s of the %s that the deal list "
         "sums to (secondary sales excluded; SpaceX alone is %s of the measured proceeds)." % (
             len(meas), len(c.deals), first_qe_txt, names(meas), "$" + comma(c.measured_proceeds), pc(mp, 3), "$" + comma(c.master_total),
             pc(c.weights.get("SPCX", Decimal(0)) * 100, 3)))
    L.append(s + "\n")
    if awaiting:
        L.append("%s have a first quarter-end of 30 September 2026. Managers must file within 45 days of the quarter-end, which is 16 November 2026 for that date, and the SEC publishes "
                 "the filings in its next data set, expected around mid-December 2026. Those deals wait for it and have no figures here.\n" % names([d["ticker"] for d in awaiting]))
    blank = [t for t in meas if c.dens[t]["den_listed_10q_sh"] is None]
    if blank:
        L.append("%s: no percentage is shown because the company had not filed a quarterly report for the quarter-end.\n" % names(blank))
    else:
        L.append("All measured companies filed a quarterly report for the period ended 30 June 2026, so every measured deal has a percentage against the shares outstanding at that date.\n")
    # 4: counts first
    L.append("## Shares reported on Form 13F, deal by deal\n")
    L.append("Counts of shares of the listed class (the class that trades; see the dual-class section) that 13F filers reported at the quarter-end, summed over all filers as filed in the "
             "SEC data set (vintage `%s`). A filer here is a filer number, not a manager group.\n" % v)
    rows = []
    for t in meas:
        m = c.meas[t]
        rows.append([SHORT[t], iso(c.deals[[d["ticker"] for d in c.deals].index(t)]["first_qe"]), comma(m["n_filers"]), comma(m["sh_13f"]), comma(m["sh_13f_sole"]), comma(m["sh_pre_ipo_flagged"])])
    L.append(md_table(["Deal", "Quarter-end", "Filers", "Shares reported (sh_13f)", "of which sole discretion", "Reported by filers flagged as pre-listing holders (hypothesis)"], rows) + "\n")
    L.append("The sole-discretion column is a floor that no double report by two managers can inflate. The flagged column is a floor on holdings by investors who owned the company before it "
             "listed, judged by the builder from notes on Schedule 13D/13G filings (filings by holders of more than 5% of a class) and public descriptions; it is a hypothesis.\n")
    L.append("These counts are not comparable with the table above: they are shares of any class that a Schedule 13D/13G filer is deemed to own, including Class B shares that can convert into the listed class, "
             "so for SpaceX one holder's block of mostly Class B shares makes the total larger than the whole listed class.\n")
    rows13 = [[SHORT[t], iso(c.deals[[d["ticker"] for d in c.deals].index(t)]["first_qe"]), comma(c.meas[t]["sh_13dg_holders_without_13f"])] for t in meas]
    L.append(md_table(["Deal", "Quarter-end", "Schedule 13D/13G shares, any class, holders with no 13F row (not comparable; can exceed the listed class)"], rows13) + "\n")
    L.append("The column counts shares as typed on Schedule 13D/13G filings by reporting persons for which no 13F filer with a row in this deal is matched. It is beneficial ownership: it overlaps across the filings of one group "
             "and is never added to a 13F figure or to any percentage of the listed class.\n")
    L.append("## Against the shares outstanding at the quarter-end\n")
    rows = []
    for t in meas:
        m, den = c.meas[t], c.dens[t]
        rows.append([SHORT[t], comma(den["den_listed_10q_sh"]) if den["den_listed_10q_sh"] is not None else "blank", iso(den["den_listed_10q_asof"]) or "", den["den_listed_10q_item"] or "",
                     pc(m["pct_of_listed"], 3), pc(m["ipo_shares_pct_of_listed"], 3), pc(m["pct_of_all_classes"], 3), pc(m["pct_of_ipo_shares"], 1)])
    L.append(md_table(["Deal", "Listed class outstanding at the quarter-end (first 10-Q)", "As of", "10-Q item", "sh_13f as % of that count (pct_of_listed)", "IPO shares as % of that count",
                       "sh_13f as % of all classes", "sh_13f as % of IPO shares (memo)"], rows) + "\n")
    if "CBRS" in c.dens and c.dens["CBRS"]["den_listed_prosp_sh"] is not None:
        L.append("The prospectus count is a different quantity: for Cerebras it counts only the %s Class A shares sold, because every earlier share was then Class B and converted afterwards; the prospectus-based "
                 "percentage is in holdings.csv for comparison only and can exceed 100.\n" % comma(c.dens["CBRS"]["den_listed_prosp_sh"]))
    L.append("The first 10-Q gives the count either in the financial statements at the period end (`qe_balance_sheet`) or on its cover page at a later date (`qe_cover`); the table says which. SpaceX's count at the quarter-end is stated in millions of shares in its financial statements and Fervo Energy's in thousands (shown as issued, with no treasury stock at that date), so both are rounded to the unit stated. Cerebras's primary count is its 30 June figure for Class A, not its cover figure. "
             + HIGH_SENTENCE + " The IPO-shares column shows how small the offering can be against the listed class. The last column is a memo that exceeds 100 wherever pre-listing holders file on Form 13F.\n")
    if "SPCX" in c.meas and c.meas["SPCX"]["ipo_shares_pct_of_listed"] is not None:
        sp = c.dens["SPCX"]
        L.append("For SpaceX the %s shares sold in the offering are %s of the listed class at the quarter-end, mostly pre-listing stock that converted into Class A at the listing, so the percentage "
                 "above says who held the listed class, not who took the offering.\n" % (comma(sp["ipo_shares_base"]), pc(c.meas["SPCX"]["ipo_shares_pct_of_listed"], 1)))
    pa, px = c.pw_all, c.pw_ex
    L.append("Pooled over the measured deals that have a quarterly report, 13F filers reported %s shares against %s shares in the listed classes at the quarter-end, a pooled %s (without SpaceX: "
             "%s shares against %s, %s).\n" % (comma(pa["pooled_num"]), comma(pa["pooled_den"]), pc(pa["pooled_pct"], 3), comma(px["pooled_num"]), comma(px["pooled_den"]), pc(px["pooled_pct"], 3)))
    L.append("A proceeds-weighted mean of the deal percentages is %s with SpaceX and %s without it: SpaceX carries %s of the weight, INNIO carries a weight of 0 "
             "because the company received no proceeds from its offering, and %d of the %d deals are not yet measured. The unweighted median of the deal percentages is %s "
             "(range %s to %s; without SpaceX %s, range %s to %s).\n" % (
                 pc(pa["weighted_pct"], 3), pc(px["weighted_pct"], 3), pc(c.weights.get("SPCX", Decimal(0)) * 100, 3), len(awaiting), len(c.deals), pc(pa["median_pct"], 3), pc(pa["min_pct"], 3),
                 pc(pa["max_pct"], 3), pc(px["median_pct"], 3), pc(px["min_pct"], 3), pc(px["max_pct"], 3)))
    # 5: concentration etc
    L.append("## Concentration, registration numbers and options\n")
    rows = [[SHORT[t], pc(c.meas[t]["top1_pct_of_13f"], 1), pc(c.meas[t]["top10_pct_of_13f"], 1), pc(c.meas[t]["top10_pct_of_listed"], 1)] for t in meas]
    L.append(md_table(["Deal", "Largest filer, % of sh_13f", "Ten largest filers, % of sh_13f", "Ten largest filers, % of the listed class at the quarter-end"], rows) + "\n")
    L.append("Filers are filer numbers, not manager groups: two numbers of one manager count twice.\n")
    if c.cfg.get("secfile_is_regulatory", True):
        L.append("Each report's cover page may declare an SEC file number. Its prefix is a registration status, not an investor type: 801- registered investment adviser, 802- exempt reporting "
                 "adviser, 8- broker-dealer, another prefix, or no number declared. Share of sh_13f by status:\n")
        rows = []
        for t in meas:
            by = {cat: pc_all for cat, n, s, pc_all, pc_l in c.reg[t]}
            rows.append([SHORT[t]] + [pc(by.get(cat, Decimal(0)), 1) for cat in REG_CATEGORIES])
        L.append(md_table(["Deal"] + [REG_WORDS[x] for x in REG_CATEGORIES], rows) + "\n")
    rows = [[SHORT[t], comma(c.meas[t]["sh_calls"]), pc(pct(c.meas[t]["sh_calls"], c.meas[t]["sh_13f"]), 2), comma(c.meas[t]["sh_puts"]), pc(pct(c.meas[t]["sh_puts"], c.meas[t]["sh_13f"]), 2),
             "%d / %d" % (c.meas[t]["n_filers_calls"], c.meas[t]["n_filers_puts"])] for t in meas]
    L.append("Options are shares underlying call and put positions as filed, including rows filed under the Official List's separate call and put identifiers of the same issuer. They are never added to or subtracted from sh_13f.\n")
    L.append(md_table(["Deal", "Shares underlying calls", "as % of sh_13f", "Shares underlying puts", "as % of sh_13f", "Filers with calls / puts"], rows) + "\n")
    L.append("## Filers that also filed a Schedule 13D or 13G, and the prospectus investors\n")
    rows = [[SHORT[t], pc(pct(c.meas[t]["sh_13f_matched_i2"], c.meas[t]["sh_13f"]), 1)] for t in meas]
    L.append("Share of sh_13f reported by filers that the builder matched to a Schedule 13D/13G reporting person on the same issuer (the two filings use different legal tests and are not "
             "expected to reconcile; the gaps are in `overlap_i2.csv`):\n")
    L.append(md_table(["Deal", "% of sh_13f"], rows) + "\n")
    for r in c.tables["cornerstones.csv"]:
        L.append("%s: investors the prospectus named as having indicated an interest in buying up to $%s of shares (a ceiling), %s shares at the $%s offer price. The filers the builder matched to them "
                 "reported %s shares at the quarter-end, %s of that ceiling. An indication of interest is not a holding.\n" % (SHORT[r[0]], comma(D_(r[2])), comma(D_(r[4]), 2), dstr(D_(r[3]), 2),
                                                                                       comma(D_(r[7])), pc(D_(r[8]), 1)))
    L.append("## Coverage of the data set\n")
    rows = [[r[0], r[1][:-4], r[2], r[3], r[4], r[5] + "%" if r[5] else "", r[6], r[7], r[8], r[9], r[10], r[11]] for r in c.tables["coverage.csv"] if int(r[2]) >= COVERAGE_MIN]
    L.append(md_table(["Quarter-end", "Zip", "13F-HR filers", "13F-NT filers", "Confidential holdings omitted", "as % of 13F-HR filers", "Restatements", "New-holdings amendments",
                       "Repeating an identifier*", "Orphan amendments", "Duplicate amendments*", "Filed after the due date"], rows) + "\n")
    L.append("*Counted over the deals' rows only. A manager's confidential holdings are invisible here.\n")
    L.append("## Kinds of holder\n")
    kinds = collections.defaultdict(lambda: collections.Counter())
    for r in c.tables["kind_hypothesis.csv"]:
        kinds[r[0]][r[4]] += 1
    L.append("Kind, judged by the builder from public descriptions (a hypothesis): among the ten largest filers of each deal, the count by kind is in `kind_hypothesis.csv`. 13F itself has no holder-type field "
             "and no manager files a kind.\n")
    rows = [[SHORT[t], ", ".join("%s %d" % (k, n) for k, n in sorted(kinds[t].items()))] for t in meas]
    L.append(md_table(["Deal", "Ten largest filers by kind (hypothesis)"], rows) + "\n")
    L.append("## Dual-class issuers in plain words\n")
    L.append("A company with more than one class of common stock lists one class. Only that class is a Section 13(f) security, so Form 13F reports it and nothing else. Shares held before the listing "
             "in another class (Class B at SpaceX, Cerebras, Quantinuum and Fervo Energy) are not in the 13F figure unless they were converted into the listed class. Percentages here are against the "
             "listed class; `pct_of_all_classes` is printed beside them and is not the measure.\n")
    L.append("## Column dictionary\n")
    L.append(md_table(["Column", "Meaning"], [
        ["sh_13f", "Shares of the listed class reported on Form 13F at the quarter-end, summed over filers after one report per filer and quarter is chosen (original, later restatement, added new-holdings amendments); a filer is counted only if its reported shares are positive"],
        ["sh_13f_sole", "The same over rows with sole investment discretion"],
        ["sh_pre_ipo_flagged", "sh_13f of filers flagged as pre-listing holders (a floor; a hypothesis)"],
        ["sh_13dg_holders_without_13f", "Typed Schedule 13D/13G share counts of reporting persons with no matched 13F row (beneficial ownership; never added to sh_13f)"],
        ["pct_of_listed", "100 times sh_13f over the listed class outstanding at the quarter-end (first 10-Q); blank where no 10-Q exists"],
        ["pct_of_listed_prosp", "The same over the listed class outstanding after the offering in the 424B4 (a variant)"],
        ["pct_of_all_classes", "The same over all common classes on the same 10-Q item"],
        ["ipo_shares_pct_of_listed", "100 times the shares sold in the offering (base case) over the listed class at the quarter-end"],
        ["pct_of_ipo_shares", "100 times sh_13f over the shares sold in the offering (memo)"],
        ["top1_pct_of_13f, top10_pct_of_13f, top10_pct_of_listed", "Largest filer and ten largest filers, as a share of sh_13f and of the listed class"],
        ["sh_calls, sh_puts", "Shares underlying call and put rows; never netted"],
        ["sh_name_match_other_cusip", "Shares in rows whose issuer name matches the deal but whose identifier is not the mapped one; reported, not added"],
        ["median_implied_price_usd, implied_to_offer_ratio", "Median over filers of reported value over reported shares, and its ratio to the offer price; some filers report value in thousands, so this is a check on units"],
        ["status", "measured, or awaiting_next_zip when the first quarter-end's filings are not yet in a data set"],
        ["den_listed_10q_item", "qe_balance_sheet (financial statements at the period end) or qe_cover (cover page, later date)"],
    ]) + "\n")
    L.append("## Identifiers and source\n")
    L.append("Securities are named by ticker and issuer name. The committed files carry no CUSIP, ISIN, FIGI, filer number or accession number: CUSIP Global Services allows its numbers to be "
             "collected from public sources for non-commercial use, and this repository's licence would let others reuse a committed number commercially. Filer names appear only where the "
             "builder's review marked the name as an organisation's public name; otherwise `withheld`.\n")
    L.append('Source: U.S. Securities and Exchange Commission, "Form 13F Data Sets", %s (vintage `%s`); the issuers\' prospectuses (Form 424B4) and first quarterly reports (Form 10-Q). Method, '
             'inputs and every build decision: `SOURCES.md`.\n' % (", ".join(c.zip_names), v))
    return "\n".join(L).replace("\n\n\n", "\n\n")


STATIC_DECISIONS = (
    "**No network, no fetch step.** The spec lists a `fetch` step as optional ('if the spec has one'); it has none. The supervisor fetched every SEC file and the script makes no request and "
    "imports no network or process module (selftest G14). `verify` only re-hashes the cached zips against their stamps.",
    "**Where the zip folder may sit (spec R2 against round 5).** R2 says the script refuses a `--zip-dir` inside the repository; round 5 puts the raw zips in the repository's gitignored "
    "`data/vintages/form13f_zips/`. The latest round governs, so exactly that folder is accepted, and only while `.gitignore` names it; any other folder inside the repository is refused. "
    "The cache (filtered rows, names, the two private reviewed tables) is refused anywhere inside the repository.",
    "**The cache location.** The default `--cache` is the folder `ipo13f_cache` in the user's home folder, as the spec says. This build was run with a cache in the session's scratch folder outside the clone (the instruction to work "
    "only inside the clone, with R3's rule that the cache is outside the repository).",
    "**The live latch is the file named exactly `STOP`.** A preserved record such as `STOP.<date>.<note>` is not a latch and does not stop a run.",
    "**Pricing date means the prospectus date.** `pricing_date` is the date printed on the 424B4 cover ('Prospectus dated'); the 424B4 itself is filed a day later. The three deals that have no "
    "424B4 in the supervisor's copies (BSP, SKHY, JMKE) take the issuer's pricing release date, relayed by the supervisor and marked `issuer_release_relayed` in `deal_inputs.csv` (R6).",
    "**'First 10-Q' means the 10-Q for the first quarter-end.** CBRS and FRVO filed a 10-Q for the period ended 31 March 2026 after listing; that one covers a quarter-end before the offering. "
    "The denominator comes from the 10-Q for the period ended 30 June 2026, the first calendar quarter-end after pricing.",
    "**Rounded share counts.** SpaceX's financial statements give shares in millions (7,607 and 5,569) and Fervo's in thousands (286,869 and 7,785). They are entered as stated, multiplied out, "
    "and the precision (plus or minus half a million, half a thousand) is in the row. Fervo's statement says 'issued'; there is no treasury stock at 30 June 2026, so issued equals outstanding.",
    "**Identifier variants.** Shares are summed only for the mapped identifier after stripping white space and upper-casing (O-13). Rows under other identifier strings that match the deal's name are "
    "reported in `sh_name_match_other_cusip` and never added.",
    "**Duplicates and repeated identifiers** (`n_amend_duplicates`, `n_new_holdings_repeat_cusip`) can only be judged on rows the scan kept, which are the deals' rows. Orphans and several-originals "
    "are judged over every filer.",
    "**Reports 'filed after the due date'** counts 13F-HR originals (not amendments) filed after the 45th day, rolled to the next business day over weekends and federal holidays.",
    "**`sh_13dg_holders_without_13f`** sums each reporting person's typed count (spec 3.7). Several persons in one filing may report the same shares; the column is labelled in the README as beneficial "
    "ownership that may include convertible, unlisted or repeated shares, and is never added to anything.",
    "**Label numbering.** Where a name is withheld the output says `withheld #n` (`individual (withheld) #n` for an i2 reporting person of type IN), numbered within a ticker so that keys stay unique.",
    "**`reg_category` follows round 5** (SECFILENUMBER is a separate field from FORM13FFILENUMBER). The prefix meanings 801-, 802-, 8- are relayed, not defined by the readme.",
    "**A 13F-HR whose cover page says it is an amendment** (ISAMENDMENT Y, type NEW HOLDINGS) is kept as the base because its SUBMISSIONTYPE is 13F-HR, and is listed in C10.",
    "**The second scan** keeps the rows of the mapped listed-class identifier and every row whose issuer name matches a deal pattern; rejected identifiers are not collected.",
    "**Supervisor ruling R6-1 (unknown `AMENDMENTTYPE`).** `UNKNOWN_AMENDTYPE_SCOPE` is `measured_quarters_only`: a blank or unknown type refuses the build only for a filing whose period is a measured quarter-end (30 Jun 2026 now). The spec's literal reading, any period, is the value `all`. The eight blank-type 13F-HR/A filings in the Mar-May zip (periods 2023 to 2025, none with a row of any deal) are listed in C10.",
    "**Supervisor ruling R6-2 (C02 pins).** The supervisor verified both in the zip. Row 5 (Atreides): shares rows 3,110,086, VALUE 687,329,006, calls 700,000; the relayed 3,810,086 was shares plus calls. Row 8 (Maplelane, QNT): shares rows 150,000 (23,597 + 4,929 + 58,377 + 63,097); the relayed 145,071 dropped the 4,929 sole-discretion row. Both pins are corrected, with the relayed values beside them in the checks.csv description.",
    "**Supervisor ruling R6-3 (offer price).** `deal_inputs.csv` has an item `offer_price_usd`: the price sits in the `shares` column and the quote is the 424B4 cover phrase. The script-side price table is gone and `DEAL_INPUTS_SHA256` covers the prices. No header changes; the `item` allowed values gain one.",
    "**Supervisor ruling R6-4 (zip folder).** The builder's reading is accepted: only the gitignored `data/vintages/form13f_zips/` may sit inside the repository; the cache may not.",
    "**Supervisor ruling R6-5 (`pre_ipo_flag`).** A ; list of tickers per filer is accepted, so a flag for one issuer adds nothing to another issuer's `sh_pre_ipo_flagged`.",
    "**Supervisor ruling R6-6 (option identifiers).** Rows under the Official List's CALL and PUT identifiers of a deal are options on that deal's listed class. The CUSIP map gives them the roles `option_call` and `option_put`; their rows are counted in `sh_calls` and `sh_puts` by PUTCALL, or by the identifier's role when PUTCALL is blank, together with option rows under the main identifier, and never in `sh_13f`. C17 reports them separately. Option rows under unlisted identifier variants are not counted and are reported in C17.",
    "**Supervisor ruling R6-7 (rounded counts).** Accepted. The README says SpaceX's quarter-end count is stated in millions and Fervo's in thousands (issued, no treasury stock). Cerebras's primary denominator is its 30 Jun balance-sheet count of 103,220,568 (R3-1).",
    "**Supervisor ruling R6-8 (i2 typed counts).** Accepted as labelled. The README says the 13D/13G column overlaps across the filings of one group and includes convertible Class B shares.",
    "**Supervisor ruling R6-9 (13F-HR with ISAMENDMENT Y).** One 13F-HR whose cover page says it is a NEW HOLDINGS amendment is kept as the base by its SUBMISSIONTYPE and listed in C10.",
    "**Supervisor ruling R6-10 (Official List).** `13flist2026q2` is treated as the list governing the June reports. Its title page reads \"Second Quarter FY 2026\" and prints no as-of date (C21).",
    "**Filer review accepted by the supervisor** (80 organisations public, 15 individuals not named). Kinds remain hypotheses and appear only in `kind_hypothesis.csv`.",
    "**First trading days are relayed.** CBRS comes from its own first 10-Q (read by the supervisor); BSP was verified verbatim by the supervisor; the other six were relayed from a web search with fetched pages and are not re-read by the builder: SPCX (cnbc.com live updates, 12 Jun 2026), QNT (conyers.com note), FRVO (ir.fervoenergy.com investor FAQs), INIO (Nasdaq opening-bell page of 4 Jun 2026; the pricing release said trading was expected on 4 June 2026), SKHY (Nasdaq Trader notice DTN2026-11; when-issued from 10 Jul 2026, regular way from 13 Jul), JMKE (the company's closing release). Each source string is in `first_trade_source`.",
    "**Pricing dates of the three September-quarter deals are relayed from the issuers' releases** (marked `issuer_release_relayed`): BSP 2026-06-30, SKHY 2026-07-09, JMKE 2026-07-29. The deal master's 2026-07-31 for Jersey Mike's is the closing date. No first quarter-end changes.",
    "**Supervisor ruling R6-11 (the 13D/13G column).** The Schedule 13D/13G column left the main README table and has its own small table after it, headed \"Schedule 13D/13G shares, any class, holders with no 13F row (not comparable; can exceed the listed class)\", with a sentence that the counts are not comparable and a gloss of Schedule 13D/13G at first use. No person is named. `holdings.csv` is unchanged.",
    "**Supervisor ruling R6-12 (the prospectus count).** The README table no longer has the percentage against the count after the offering; `holdings.csv` keeps `pct_of_listed_prosp`. One sentence after the table says that the prospectus count is a different quantity (for Cerebras only the Class A shares sold) and that the percentage can exceed 100.",
    "**Supervisor ruling R6-13 (the weighted mean, spec R3-3).** SpaceX's weight, INNIO's zero weight and the count of unmeasured deals now sit in the same sentence as the weighted mean, joined by a colon.",
    "**Supervisor ruling R6-14 (denominator at its point of use).** A selftest check compares `pct_of_listed` in the written `holdings.csv` with 100 x `sh_13f` over the listed class's balance-sheet count read straight from `deal_inputs.csv`, for synthetic deals whose prospectus count differs. Two mutants now fail it: the prospectus count as primary, and `pct_of_listed` computed against the prospectus count at the point of use while `deals.csv` stays right.",
    "**Supervisor ruling R6-15 (stale restatement).** A selftest case files a restatement before the original; it must lose and be listed as stale. The mutant that lets it win now fails.",
    "**Supervisor ruling R6-16 (leak).** The selftest's planted ISIN and FIGI are shape-valid synthetic strings, not real identifiers; the script was searched for any other ISIN-shaped or BBG-shaped string.",
    "**Supervisor ruling R6-17 (small items).** The column dictionary says a filer is counted only if its reported shares are positive. C01d's expected text now equals its observed text, INIO 0.000 included. `overlap_i2.csv` leaves `i2_shares`, `sh_13f_matched` and `gap_sh` blank on the row of a holder withheld as an individual, so that a withheld person cannot be re-identified by matching share counts against a named filer (a mutant that shows them fails the selftest).",
    "**Status** is computed: a deal is `measured` when the cached zips hold 13F-HR filings for its first quarter-end, else `awaiting_next_zip`.",
)


def reject_summary(map_rows):
    by = collections.Counter((r["ticker"], r["reason"]) for r in map_rows if r["status"] == "rejected")
    if not by:
        return []
    return ["**Identifiers rejected from the CUSIP map, by reason (no identifier is committed):** " + "; ".join("%s: %d x %s" % (t, n, why) for (t, why), n in sorted(by.items())) + "."]


def builder_decisions(c):
    out = list(STATIC_DECISIONS) + reject_summary(c.map_rows)
    out.extend(c.cfg.get("extra_decisions", []))
    return out


def render_sources(c):
    v = c.vintage
    cfg = c.cfg
    L = ["# Sources and method: 13F holders of the 2026 IPOs\n"]
    L.append("Specification: `_research/2026-10-26-IPO-13F-Holders-Spec.md` (committed at 7306996, with its supervisor rulings, rounds 1 to 5; where rounds differ the latest round is applied). "
             "Script: `bin/ipo_13f_holders.py`. Vintage `%s`. Guard: `bin/check.sh` M24.\n" % v)
    L.append("## Disclosure of what was seen before the build\n")
    L.append("Observed means seen by the spec author on 26 Oct 2026 between 05:43 and 05:46 UTC with the non-SEC User-Agent, one request per URL, no redirect followed; no sec.gov or data.sec.gov host "
             "was contacted by the spec author. Seen of the answer before any build: eleven hand-read 13F rows in `data/i2_ipo_allocation/i2_13F_sample_holdings.csv`; i2's 13G/13D rows; and, "
             "in the rulings, the SpaceX listed-class count at the first 10-Q (about 7.70bn) and third-party aggregate 13F sums for SPCX and CBRS at 30 Jun 2026. SPCX is therefore not blind. "
             "The builder computed nothing before the selftest passed.\n")
    L.append("## Requests\n")
    L.append("The builder made none. The supervisor fetched the files on 26 Oct 2026 and copied them into the gitignored cache; the supervisor's fetch log holds each status and is not in this "
             "repository. The URLs the spec lists (2.6):\n")
    for u in ("https://www.sec.gov/files/datastandardsinnovation/data/form-13f-data-sets/01jun2026-31aug2026_form13f.zip",
              "https://www.sec.gov/files/structureddata/data/form-13f-data-sets/01mar2026-31may2026_form13f.zip", "https://www.sec.gov/files/form_13f_readme.pdf",
              "the five 424B4s and the five first 10-Qs for the period ended 30 Jun 2026 from the EDGAR filing index (SPCX, CBRS, QNT, FRVO, INIO)",
              "the SEC Official List of Section 13(f) Securities for the quarter ended 30 Jun 2026 (the first-quarter list was also supplied)"):
        L.append("- " + u)
    L.append("\nThe spec author's own requests (2.7): `catalog.data.gov/dataset/form-13f-data-sets` 200 (281,068 bytes); `www.cusip.com` `/terms-of-use.html`, `/about/license-fees.html`, `/robots.txt` "
             "each 303 to `/index.html` (not followed); `/index.html` 200 (94,800); `/services/license-fees.html` 200 (111,955); `experience.cusip.com/license-fees-faq` 200 (924 bytes, a shell).\n")
    L.append("## The 13F readme as read (R11)\n")
    for line in cfg.get("readme_lines", ["(not recorded)"]):
        L.append("- " + line)
    L.append("\n## Deal patterns (literal, case-insensitive)\n")
    L.append(md_table(["Ticker", "Pattern"], [[t, "`%s`" % p] for t, p in DEAL_PATTERNS.items()]) + "\n")
    L.append("## Gates and reviews\n")
    for n, ok, d in cfg.get("gates", []):
        L.append("- %s: %s" % (n, "match" if ok else d))
    for line in cfg.get("review_lines", []):
        L.append("- " + line)
    L.append("- Header allowlist: `SPEC_ALLOW_SHA256 = %s` (also held in `bin/check.sh`)." % SPEC_ALLOW_SHA256)
    L.append("\n## Licence\n")
    L.append("SEC catalogue licence `https://www.usa.gov/government-copyright` (observed). CUSIP Global Services' licence-fee FAQ (observed, `https://www.cusip.com/services/license-fees.html`) allows "
             "collecting its data from public sources for \"non-commercial use, provided that the source of such information permitted the reproduction and use of such information\". The "
             "repository's CC BY 4.0 would let others reuse a committed CUSIP commercially, hence none is committed (R4, O-1). The reference figures of C19 are a third party's published aggregates "
             "used as two expected values only.\n")
    L.append("## Pricing and first trading dates against the deal master\n")
    rows = []
    for d in c.deals:
        diff = "same" if d["pricing_date"] == d["master_date"] else "master %s" % iso(d["master_date"])
        rows.append([d["ticker"], iso(d["pricing_date"]), iso(d["first_trade_date"]), iso(d["first_qe"]), diff])
    L.append(md_table(["Ticker", "Pricing date (prospectus)", "First trading day (supervisor)", "First quarter-end", "Deal master ipo_date"], rows) + "\n")
    L.append("## Pinned checks and the lists behind the acceptable warnings\n")
    for r in c.checks:
        L.append("- %s %s: expected %s; observed %s." % (r[0], r[4], r[2], r[3]))
    for k, lst in c.lists.items():
        if lst:
            L.append("\n%s:" % k)
            for x in lst:
                L.append("- " + x)
    L.append("\n## Builder decisions\n")
    for i, d in enumerate(builder_decisions(c), start=1):
        L.append("%d. %s" % (i, d))
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------------------------------
# rendering every file; the guards that apply before anything is written
# ------------------------------------------------------------------------------------------------------------------------
def render_csv_files(c, deal_inputs_text):
    texts = collections.OrderedDict()
    allow = dict(l.split(":", 1) for l in ALLOW_TEXT.strip().split("\n"))
    texts["deal_inputs.csv"] = deal_inputs_text
    for name in COMMITTED_CSV:
        if name in ("deal_inputs.csv", "checks.csv"):
            continue
        rows = c.tables[name]
        head = allow[name].split(",")
        texts[name] = csv_text(rows, head, c.source)
    texts["checks.csv"] = csv_text(c.checks, allow["checks.csv"].split(","))
    return texts


def render_texts(c, deal_inputs_text):
    t = render_csv_files(c, deal_inputs_text)
    t["README.md"] = render_readme(c)
    t["SOURCES.md"] = render_sources(c)
    return collections.OrderedDict((k, t[k]) for k in sorted(t))


def all_problems(texts, c=None):
    """Every refusal that applies to the files before they are written: allowlist, duplicate keys, wording, leaks (cache names and identifiers when present)."""
    probs = list(allow_problems())
    for n, t in texts.items():
        probs.extend(duplicate_key_problems(n, t))
    probs.extend(wording_problems("README.md", texts.get("README.md", "")))
    cusips, ciks, nonpub = (), (), ()
    if c is not None:
        cusips = sorted(set(c.listed.values()) | {r["cusip"] for r in c.map_rows})
        ciks = sorted({cik_key(s.cik) for sc in c.scans for s in sc.subs if cik_key(s.cik) in c.poss_ciks()})
        nonpub = sorted({r["name"] for r in c.review.rows if r["name_public"] != "yes" and len(r["name"]) >= 6})
    probs.extend(leak_problems(texts, cusips, ciks, nonpub, require_all=True))
    return probs


Ctx.poss_ciks = lambda self: {cik_key(p.cik) for ps in self.poss.values() for p in ps.values()} | {cik_key(r["cik"]) for r in self.review.rows if r["cik"]}


# ------------------------------------------------------------------------------------------------------------------------
# the readme of the SEC data set (R11): what the zip's own FORM13F_readme.htm says about the fields that matter
# ------------------------------------------------------------------------------------------------------------------------
def readme_facts(html_bytes):
    t = html_bytes.decode("utf-8", errors="replace")
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"&nbsp;|&#160;", " ", t)
    t = re.sub(r"\s+", " ", t)
    facts = {}
    m = re.search(r"VALUE\s*\|?\s*(Market value\..{0,200}?thousands\.)", t)
    facts["value"] = m.group(1).strip() if m else ""
    if not facts["value"]:
        m = re.search(r"(Market value\..{0,220})", t)
        facts["value"] = m.group(1).strip() if m else ""
    facts["value_whole_dollars"] = "nearest dollar" in facts["value"]
    facts["value_says_thousands_now"] = bool(re.search(r"thousands", facts["value"])) and "nearest dollar" not in facts["value"]
    facts["secfilenumber"] = "SEC File Number (if applicable)" if "SEC File Number (if applicable)" in t else ""
    facts["form13ffilenumber"] = "FORM 13F file number" if re.search(r"FORM 13F file number", t, re.I) else ""
    facts["secfile_is_regulatory"] = bool(facts["secfilenumber"]) and bool(facts["form13ffilenumber"])
    facts["amendmenttype"] = "Amendment type is a restatement or adds new holdings" if "Amendment type is a restatement or adds new holdings" in t else ""
    facts["date_format"] = "DD-MON-YYYY" if "DD-MON-YYYY" in t else ""
    facts["submission_types"] = [x for x in SUB_TYPES if x in t]
    return facts


# ------------------------------------------------------------------------------------------------------------------------
# scan, review, verify, build
# ------------------------------------------------------------------------------------------------------------------------
def list_zips(zip_dir):
    return sorted(n for n in os.listdir(zip_dir) if re.fullmatch(r"\d{2}[a-z]{3}\d{4}-\d{2}[a-z]{3}\d{4}_form13f\.zip", n))


def run_scan(a, say=print):
    zip_dir, cache = real(a.zip_dir), real(a.cache)
    check_dirs(zip_dir, cache)
    require_no_stop(zip_dir, cache)
    names = list_zips(zip_dir)
    if a.zip:
        if a.zip not in names:
            raise Refused("zip not in --zip-dir: %s" % a.zip)
        names = [a.zip]
    elif len(names) != 1:
        raise Refused("one zip per run: name it with --zip (found %d)" % len(names))
    name = names[0]
    path = os.path.join(zip_dir, name)
    map_rows, map_sha = None, "none"
    if a.with_map:
        mp = os.path.join(cache, "cusip_map.csv")
        if not os.path.isfile(mp):
            raise DataError("--with-map: %s does not exist" % mp)
        map_rows = read_cusip_map(mp)
        map_sha = sha256_path(mp)
    say("scan %s (map %s)" % (name, map_sha[:12]))
    with zipfile.ZipFile(path) as zf:
        have = {os.path.basename(i.filename) for i in zf.infolist()}
        missing = [x for x in ("SUBMISSION.tsv", "COVERPAGE.tsv", "SUMMARYPAGE.tsv", "INFOTABLE.tsv") if x not in have]
        if missing:
            raise DataError("zip lacks %s" % ", ".join(missing))
        facts = {}
        if "FORM13F_readme.htm" in have:
            with open_member(zf, "FORM13F_readme.htm") as fh:
                facts = readme_facts(fh.read())
        subs, rows, part = scan_zip(zf, say, map_rows)
    part["readme"] = facts
    stamp = write_scan(cache, name, path, subs, rows, part, map_sha)
    say("wrote %s: %d submissions, %d INFOTABLE rows, %d kept" % ("scan_" + zip_key(name), stamp["n_submissions"], stamp["n_infotable_rows"], len(rows)))
    return 0


def propose_map(scans):
    """The proposed CUSIP map: per deal the identifier reported by the most filers on shares rows (filer consensus); every other identifier of the name is rejected with a reason."""
    agg = candidate_table(scans)
    by = collections.defaultdict(lambda: collections.defaultdict(lambda: {"filers": 0, "title": set(), "name": set()}))
    for (t, cu, nm, ti), a in agg.items():
        d = by[t][cu]
        d["filers"] = max(d["filers"], len(a["ciks"]))
        d["title"].add(ti)
        d["name"].add(nm)
    rows = []
    for t in DEAL_PATTERNS:
        if t not in by:
            continue
        ranked = sorted(by[t].items(), key=lambda kv: (not cusip_check_ok(kv[0]), -kv[1]["filers"], kv[0]))
        for i, (cu, d) in enumerate(ranked):
            if not cusip_check_ok(cu):
                rows.append([t, cu, "rejected", "", "fails its check digit or is not 9 characters (%d filers); title(s): %s" % (d["filers"], "; ".join(sorted(d["title"]))[:60])])
            elif i == 0:
                rows.append([t, cu, "listed", "filer_consensus", "most filers on shares rows (%d); to be checked against the Official List" % d["filers"]])
            else:
                rows.append([t, cu, "rejected", "", "other identifier under a matching name (%d filers); title(s): %s" % (d["filers"], "; ".join(sorted(d["title"]))[:60])])
    return rows


def name_matches(a, b):
    ta, tb = norm_person(a).split(), norm_person(b).split()
    STOP_TOK = {"LLC", "LP", "INC", "LTD", "CORP", "CO", "THE", "OF", "AND", "L", "P", "NA", "PLC", "LLP", "GROUP", "MANAGEMENT", "CAPITAL", "FUND", "FUNDS", "PARTNERS", "HOLDINGS"}
    ca, cb = [x for x in ta if x not in STOP_TOK], [x for x in tb if x not in STOP_TOK]
    if not ca or not cb:
        return False
    if ca == cb:
        return True
    short, long_ = (ca, cb) if len(ca) <= len(cb) else (cb, ca)
    return len(short) >= 2 and long_[:len(short)] == short


def run_review(a, say=print):
    zip_dir, cache = real(a.zip_dir), real(a.cache)
    check_dirs(zip_dir, cache)
    require_no_stop(zip_dir, cache)
    scans = load_scans(cache)
    if not scans:
        raise DataError("no scan in the cache: run scan first")
    rd = os.path.join(cache, "review")
    os.makedirs(rd, exist_ok=True)
    subs_by_acc, rows_by_acc = rows_index(scans)
    names = cik_name_map(scans)
    say("review: %d zip(s) in the cache; NO ratio to shares outstanding is printed" % len(scans))
    agg = candidate_table(scans)
    rows_a = []
    for (t, cu, nm, ti), x in sorted(agg.items()):
        rows_a.append([t, cu, nm, ti, x["rows"], len(x["ciks"]), dstr(x["sh"]), dstr(x["sh_options"]), x["blank_value"], x["prn"], "yes" if cusip_check_ok(cu) else ("no" if len(cu) == 9 else "wrong length %d" % len(cu))])
    write_text(os.path.join(rd, "review_a_identifiers.csv"), csv_text(rows_a, ["ticker", "cusip", "nameofissuer", "titleofclass", "n_rows", "n_filers", "shares_raw_sh_no_putcall", "shares_raw_options", "n_value_blank", "n_prn_rows", "check_digit_ok"]))
    say("(a) distinct (ticker, identifier, issuer name, class title): %d" % len(rows_a))
    for r in rows_a:
        say("   %s | %s | %s | %s | rows %s filers %s shares(raw) %s options(raw) %s check %s" % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[10]))
    conf = conflict_table(scans)
    rows_b = [[k[0], k[1], k[2], k[3], x["rows"], len(x["ciks"]), dstr(x["sh"])] for k, x in sorted(conf.items())]
    write_text(os.path.join(rd, "review_b_conflicts.csv"), csv_text(rows_b, ["tickers", "cusip", "nameofissuer", "titleofclass", "n_rows", "n_filers", "shares_raw_sh_no_putcall"]))
    say("(b) rows with a candidate identifier and a non-matching name: %d distinct" % len(rows_b))
    for r in rows_b:
        say("   %s | %s | %s | %s | rows %s filers %s shares(raw) %s" % tuple(r))
    mp = os.path.join(cache, "cusip_map.csv")
    if os.path.isfile(mp):
        map_rows = read_cusip_map(mp)
        say("using the reviewed map %s" % "cusip_map.csv")
    else:
        prop = propose_map(scans)
        write_text(os.path.join(cache, "cusip_map.proposed.csv"), csv_text(prop, CUSIP_MAP_FIELDS))
        map_rows = read_cusip_map(os.path.join(cache, "cusip_map.proposed.csv"))
        say("no reviewed map yet: ranking with the PROPOSED map (cusip_map.proposed.csv)")
    listed = map_listed(map_rows)
    all_subs = [s for sc in scans for s in sc.subs]
    results = consolidate_all(all_subs, rows_by_acc, cusips=set(listed.values()), fatal_periods=None)
    for a_, t_, p_ in results.unknown:
        say("   NOTE amendment with an unknown AMENDMENTTYPE %r (period %s): a build would refuse; see the report" % (t_, p_))
    master = read_master()
    i2 = read_i2_holders()
    proposals, seen = [], set()
    top_rows = []
    all_persons = {}
    for t in DEAL_PATTERNS:
        if t in listed and t in master:
            all_persons[t] = i2_latest(i2, t, first_qe_after(master[t]["ipo_date"]))
    for t in DEAL_PATTERNS:
        if t not in listed or t not in master:
            continue
        qe = first_qe_after(master[t]["ipo_date"])
        poss = holdings(results, subs_by_acc, rows_by_acc, t, listed[t], qe)
        ranked = rank_filers(poss)
        persons = all_persons[t]
        say("(c) %s at %s: %d filers with shares of the proposed identifier; top 25 by shares (no ratio):" % (t, qe, len(ranked)))
        for rk, p in enumerate(ranked[:25], start=1):
            nm = names.get(cik_key(p.cik), "")
            match = [x["name"] for x in persons if name_matches(nm, x["name"])]
            pre = (p.secfile.split("-")[0] + "-") if "-" in p.secfile else (p.secfile[:3] if p.secfile else "none")
            top_rows.append([t, rk, p.cik, nm, pre, dstr(p.sh), "; ".join(match)])
            say("   %2d %s | %s | %s | %s | i2: %s" % (rk, p.cik, nm[:48], pre, dstr(p.sh), "; ".join(match)[:60]))
            if cik_key(p.cik) not in seen:
                seen.add(cik_key(p.cik))
                proposals.append((p.cik, nm))
        for rk, p in enumerate(ranked, start=1):
            nm = names.get(cik_key(p.cik), "")
            if cik_key(p.cik) in seen:
                continue
            hit = any(name_matches(nm, x["name"]) for x in persons) or any(frag in nm.upper() for frag, _ in CORNERSTONE_KEYS.get(t, ()))
            if hit:
                seen.add(cik_key(p.cik))
                proposals.append((p.cik, nm))
                say("   (also proposed: rank %d, %s, matches an i2 reporting person or a named cornerstone)" % (rk, nm[:48]))
    write_text(os.path.join(rd, "review_c_top_filers.csv"), csv_text(top_rows, ["ticker", "rank", "cik", "filer_name", "secfile_prefix", "shares", "i2_name_match"]))
    # cornerstone and i2 candidates among all filers named in any deal's positions
    prop_rows = []
    i2_types = collections.defaultdict(set)
    for h in i2:
        i2_types[norm_person(h["reporting_person_name"])].add(h["type_of_reporting_person"].strip())
    every = [x for ps in all_persons.values() for x in ps]
    for cik, nm in proposals:
        match = sorted({x["name"] for x in every if name_matches(nm, x["name"])})
        types = set()
        for x in every:
            if x["name"] in match:
                types.add(x["type"])
        kind, basis = propose_kind(nm, sorted(types))
        cm = ""
        for t, keys in CORNERSTONE_KEYS.items():
            for frag, label in keys:
                if frag in nm.upper():
                    cm = "%s:%s" % (t, label)
        prop_rows.append([cik, nm, propose_public(nm), kind, basis, "no", "; ".join(match), cm])
    for t in DEAL_PATTERNS:
        if t not in listed or t not in master:
            continue
        qe = first_qe_after(master[t]["ipo_date"])
        for x in i2_latest(i2, t, qe):
            k = norm_person(x["name"])
            if any(norm_person(r[1]) == k and not r[0] for r in prop_rows):
                continue
            prop_rows.append(["", x["name"], propose_public(x["name"], x["type"]), "", "", "", x["name"], ""])
    write_text(os.path.join(cache, "filer_review.proposed.csv"), csv_text(prop_rows, FILER_REVIEW_FIELDS))
    say("wrote review files to %s and filer_review.proposed.csv (%d rows) to the cache" % (rd, len(prop_rows)))
    return 0


def run_verify(a, say=print):
    zip_dir, cache = real(a.zip_dir), real(a.cache)
    check_dirs(zip_dir, cache)
    require_no_stop(zip_dir, cache)
    bad = zip_problems(zip_dir, load_scans(cache))
    for b in bad:
        say("  FAIL " + b)
    say("verify: %d problem(s)" % len(bad))
    return 2 if bad else 0


def zip_problems(zip_dir, scans):
    bad = []
    for sc in scans:
        p = os.path.join(zip_dir, sc.zip_name)
        if not os.path.isfile(p):
            bad.append("%s is not in the zip folder" % sc.zip_name)
        elif os.path.getsize(p) != sc.stamp["zip_bytes"] or sha256_path(p) != sc.stamp["zip_sha256"]:
            bad.append("%s differs from its stamp (size or sha256)" % sc.zip_name)
    return bad


def gate_state(cache, deal_inputs_path, scans, consts=None):
    """The three constants and the cache stamps. Returns (gates, problems). A gate is (name, ok, detail)."""
    consts = consts or {"CUSIP_MAP_SHA256": CUSIP_MAP_SHA256, "FILER_REVIEW_SHA256": FILER_REVIEW_SHA256, "DEAL_INPUTS_SHA256": DEAL_INPUTS_SHA256}
    paths = {"CUSIP_MAP_SHA256": os.path.join(cache, "cusip_map.csv"), "FILER_REVIEW_SHA256": os.path.join(cache, "filer_review.csv"), "DEAL_INPUTS_SHA256": deal_inputs_path}
    gates, probs = [], []
    for name in ("CUSIP_MAP_SHA256", "FILER_REVIEW_SHA256", "DEAL_INPUTS_SHA256"):
        want = consts.get(name, "")
        if not want:
            gates.append((name, False, "not set"))
            probs.append("%s is not set" % name)
            continue
        if not os.path.isfile(paths[name]):
            gates.append((name, False, "file missing"))
            probs.append("%s: file missing" % name)
            continue
        got = sha256_path(paths[name])
        ok = got == want
        if M("g7_build_hash_mismatch_accepted") and name == "DEAL_INPUTS_SHA256":
            ok = True
        gates.append((name, ok, "differs from the file"))
        if not ok:
            probs.append("%s differs from the sha256 of its file" % name)
    want = consts.get("CUSIP_MAP_SHA256", "")
    stale = [sc.zip_name for sc in scans if sc.stamp.get("map_sha256") != want]
    if M("g3_stale_stamp_accepted"):
        stale = []
    gates.append(("cache stamp", not stale, "stamped with another map: " + ", ".join(stale)))
    if stale:
        probs.append("the cache is not stamped with CUSIP_MAP_SHA256 (run the second scan): " + ", ".join(stale))
    return gates, probs


def read_deal_inputs(path):
    hdr, rows = read_csv_rows(path)
    if tuple(hdr) != DEAL_INPUT_FIELDS:
        raise DataError("deal_inputs.csv header is not the allowlist")
    return rows


def build_inputs(zip_dir, cache, out, consts=None, deal_inputs_path=None):
    """Everything `build` reads, validated. Returns a dict, or raises DataError."""
    deal_inputs_path = deal_inputs_path or os.path.join(out, "deal_inputs.csv")
    scans = load_scans(cache)
    if not scans:
        raise DataError("no scan in the cache")
    gates, probs = gate_state(cache, deal_inputs_path, scans, consts)
    if probs:
        raise DataError("; ".join(probs))
    deal_rows = read_deal_inputs(deal_inputs_path)
    dp = deal_input_problems(deal_rows)
    if dp:
        raise DataError("deal_inputs.csv: " + "; ".join(dp[:12]))
    zp = zip_problems(zip_dir, scans)
    facts = [sc.stamp.get("readme", {}) for sc in scans]
    miss = []
    for sc in scans:
        flds = sc.stamp.get("fields", {})
        for tbl, want in (("SUBMISSION", SUB_COLS), ("COVERPAGE", COV_COLS), ("SUMMARYPAGE", SUM_COLS), ("INFOTABLE", INF_COLS)):
            miss += ["%s.%s" % (tbl, w) for w in want if w not in flds.get(tbl, ())]
    README_SAYS_THOUSANDS[0] = any(f.get("value_says_thousands_now") for f in facts)
    lines = []
    f0 = facts[-1] if facts else {}
    lines.append("`VALUE`: " + (f0.get("value") or "(not found)") + (" -> whole US dollars; never rescaled." if f0.get("value_whole_dollars") else " -> NOT whole dollars: reported to the supervisor, not rescaled."))
    lines.append("`SECFILENUMBER`: \"%s\", a separate field from `FORM13FFILENUMBER` (\"%s\") -> reg_category.csv is %s (round 5, R3-6). The prefix meanings 801-, 802-, 8- are relayed, not defined by the readme."
                 % (f0.get("secfilenumber", ""), f0.get("form13ffilenumber", ""), "produced" if f0.get("secfile_is_regulatory") else "NOT produced"))
    lines.append("`AMENDMENTTYPE`: \"%s\"; values found in the data: RESTATEMENT, NEW HOLDINGS (an unknown value is a FAIL listing all)." % f0.get("amendmenttype", ""))
    lines.append("Dates: %s; submission types listed: %s." % (f0.get("date_format", "?"), ", ".join(f0.get("submission_types", []))))
    cfg = {"gates": gates, "zip_problems": zp, "fields_missing": sorted(set(miss)), "secfile_is_regulatory": bool(f0.get("secfile_is_regulatory", True)), "readme_lines": lines,
           "readme_recorded": bool(facts and facts[0]),
           "review_lines": ["`CUSIP_MAP_SHA256 = %s`: the identifier map, reviewed and set by the supervisor on 26 Oct 2026 (stage 2); the cache's scans are stamped with it." % (consts or {}).get("CUSIP_MAP_SHA256", CUSIP_MAP_SHA256),
                            "`FILER_REVIEW_SHA256 = %s`: the filer table (public names, kinds, pre-listing flags, 13D/13G and cornerstone matches), reviewed and accepted by the supervisor on 26 Oct 2026." % (consts or {}).get("FILER_REVIEW_SHA256", FILER_REVIEW_SHA256),
                            "`DEAL_INPUTS_SHA256 = %s`: the transcribed `deal_inputs.csv`, checked and set by the supervisor on 26 Oct 2026 (stage 2), with the first trading days and the three September-quarter pricing dates entered from the supervisor's reply." % (consts or {}).get("DEAL_INPUTS_SHA256", DEAL_INPUTS_SHA256)]}
    return {"scans": scans, "deal_rows": deal_rows, "cfg": cfg, "deal_inputs_text": open(deal_inputs_path, encoding="utf-8", newline="").read()}


def load_reviewed(cache):
    map_rows = read_cusip_map(os.path.join(cache, "cusip_map.csv"))
    review = Review(read_filer_review(os.path.join(cache, "filer_review.csv")))
    return map_rows, review


def hard_fail(c):
    return [r for r in c.checks if r[4] == "FAIL"]


def render_final(c, deal_inputs_text):
    """Render twice, compare (C12), then render the final files with C12 filled in. Returns (texts, determinism)."""
    t1 = render_texts(c, deal_inputs_text)
    t2 = render_texts(c, deal_inputs_text)
    det = t1 == t2
    c.cfg["determinism"] = det
    for r in c.checks:
        if r[0] == "C12":
            r[3] = "identical" if det else "DIFFERS"
            r[4] = "PASS" if det else "FAIL"
    return render_texts(c, deal_inputs_text), det


def finish_build(c, deal_inputs_text, say=print):
    """Refuses on any leak, wording or key problem. Returns (texts, determinism)."""
    texts, det = render_final(c, deal_inputs_text)
    probs = all_problems(texts, c)
    if probs:
        raise DataError("refusing to write: " + "; ".join(probs[:10]))
    return texts, det


def run_build(a, say=print):
    zip_dir, cache, out = real(a.zip_dir), real(a.cache), real(a.out)
    check_dirs(zip_dir, cache)
    require_no_stop(zip_dir, cache)
    if os.path.basename(out.rstrip(os.sep)) != "ipo_13f_holders":
        raise Refused("--out must be a folder named ipo_13f_holders (the committed outputs live in data/ipo_13f_holders/)")
    inp = build_inputs(zip_dir, cache, out)
    map_rows, review = load_reviewed(cache)
    master = read_master()
    i2_holders = read_i2_holders()
    i2_sample = read_plain_csv(I2_SAMPLE)
    i1b = read_plain_csv(I1B_CORNERSTONES)
    c = compute(inp["scans"], map_rows, inp["deal_rows"], master, i2_holders, i2_sample, i1b, review, inp["cfg"])
    texts, det = finish_build(c, inp["deal_inputs_text"], say)
    fails = hard_fail(c)
    dest = out if not fails else os.path.join(out, "_FAILED")
    for n, t in texts.items():
        if n == "deal_inputs.csv":
            continue
        write_text(os.path.join(dest, n), t)
    for r in c.checks:
        if r[4] in ("FAIL", "WARN"):
            say("  %s %s: %s" % (r[4], r[0], r[3][:200]))
    say("build: %d files written to %s; %d hard FAIL(s); deterministic %s" % (len(texts) - 1, dest, len(fails), det))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("scan", "review", "build", "verify"):
        p = sub.add_parser(name)
        p.add_argument("--zip-dir", default=ZIPDIR_DEFAULT)
        p.add_argument("--cache", default=CACHE_DEFAULT)
        if name == "build":
            p.add_argument("--out", default=OUT_DEFAULT)
        if name == "scan":
            p.add_argument("--zip", default=None, help="the zip to scan (one per run)")
            p.add_argument("--with-map", action="store_true", help="second scan: keep the rows of every mapped identifier and stamp the cache with the map's hash")
    ps = sub.add_parser("selftest")
    ps.add_argument("--no-mutants", action="store_true")
    ps.add_argument("--mutant", help="run every guard with this one mutant switched on; exit 1 (the selftest fails) when it is caught")
    ps.add_argument("--write-fixture", help="write the clean synthetic output folder to DIR (used to show that bin/check.sh M24 fires on a planted copy)")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "selftest":
            if a.write_fixture:
                return write_fixture(a.write_fixture)
            return selftest(mutants=not a.no_mutants, only=a.mutant)
        return {"scan": run_scan, "review": run_review, "build": run_build, "verify": run_verify}[a.cmd](a)
    except StopPresent as e:
        print("STOP present: %s" % e)
        return 2
    except Refused as e:
        print("refused: %s" % e, file=sys.stderr)
        return 2
    except DataError as e:
        print("STOP (data): %s" % e, file=sys.stderr)
        return 2


# ------------------------------------------------------------------------------------------------------------------------
# selftest: synthetic data only. Every guard of the spec's section 7 has a test; each mutant (a deliberately broken variant, switched on in this process only)
# must make its guard's test fail. A mutant that is not caught is a failure.
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


SIG_NAME = next(iter(FORBIDDEN_MEMBERS))


def cusip_with_check(base8):
    tot = 0
    for i, ch in enumerate(base8):
        v = int(ch) if ch.isdigit() else ord(ch) - 55
        if i % 2 == 1:
            v *= 2
        tot += v // 10 + v % 10
    return base8 + str((10 - tot % 10) % 10)


SYN_TICKERS = ("SPCX", "CBRS", "QNT", "FRVO", "INIO")
SYN_CUSIP = {"SPCX": "TSTA01102", "CBRS": "TSTB02108", "QNT": "ZZZZZZ104", "FRVO": cusip_with_check("TSTD0410"), "INIO": cusip_with_check("TSTE0510")}
SYN_OTHER = cusip_with_check("TSTA0120")
SYN_OPT_CALL = "ZZZZZZ904"
SYN_OPT_PUT = "ZZZZZZ954"
SYN_NAME = {"SPCX": "SPACE EXPLORATION TECHNOLOGIES CORP", "CBRS": "CEREBRAS SYSTEMS INC", "QNT": "QUANTINUUM INC", "FRVO": "FERVO ENERGY CO", "INIO": "INNIO N V"}
SYN_DEN = {"SPCX": (7607000000, 5569000000, 7380196910, 555555555), "CBRS": (103220568, 121301359, 30000000, 30000000), "QNT": (36134196, 226771877, 32862895, 28000000),
           "FRVO": (286869000, 7785000, 275776919, 70000000), "INIO": (750000000, None, 750000000, 90000000)}
SYN_OFFER = {"SPCX": "135.00", "CBRS": "185.00", "QNT": "60.00", "FRVO": "27.00", "INIO": "27.00"}
SYN_PRICE = {"SPCX": Decimal("170.86"), "CBRS": Decimal("221"), "QNT": Decimal("81.7"), "FRVO": Decimal("29.23"), "INIO": Decimal("27.5")}
PLANT_ADDR = "ZZ Planted Street 99"
PLANT_SIG = "Zed Signatory Planted"
PLANT_PHONE = "555-0100-PLANT"


def syn_acc(n):
    return "9%09d-26-%06d" % (n, n)


def mk_sub(acc, cik, filing, stype="13F-HR", period="2026-06-30", amend="", name="Syn Filer LLC", secfile="", conf=""):
    a = amend.upper()
    return Sub(acc, parse_iso(filing), stype, str(cik), parse_iso(period), "Y" if stype.endswith("/A") else "N", a, "", "13F HOLDINGS REPORT", secfile, name, conf)


def mk_row(acc, cusip="TSTA01102", shares="100", value="1000", sh_type="SH", pc="", disc="SOLE", name="SPACE EXPLORATION TECHNOLOGIES CORP", tick="SPCX", title="CL A"):
    return Row(acc, name, title, cusip, value, shares, sh_type, pc, disc, "", tick)


def poss_of(subs, rows, ticker="SPCX", cusip="TSTA01102", qe="2026-06-30", cusips=None):
    by = collections.defaultdict(list)
    for r in rows:
        by[r.acc].append(r)
    res = consolidate_all(subs, by, cusips=cusips or {cusip})
    sba = {s.acc: s for s in subs}
    return holdings(res, sba, by, ticker, cusip, parse_iso(qe)), res


def tsv_bytes(header, rows):
    return ("\t".join(header) + "\n" + "".join("\t".join(r) + "\n" for r in rows)).encode("utf-8")


def d2dmy(iso_s):
    d = parse_iso(iso_s)
    return "%02d-%s-%d" % (d.day, list(MONTHS)[d.month - 1], d.year)


COV_HEADER = ["ACCESSION_NUMBER", "REPORTCALENDARORQUARTER", "ISAMENDMENT", "AMENDMENTNO", "AMENDMENTTYPE", "CONFDENIEDEXPIRED", "DATEDENIEDEXPIRED", "DATEREPORTED",
              "REASONFORNONCONFIDENTIALITY", "FILINGMANAGER_NAME", "FILINGMANAGER_STREET1", "FILINGMANAGER_STREET2", "FILINGMANAGER_CITY", "FILINGMANAGER_STATEORCOUNTRY",
              "FILINGMANAGER_ZIPCODE", "REPORTTYPE", "FORM13FFILENUMBER", "CRDNUMBER", "SECFILENUMBER", "PROVIDEINFOFORINSTRUCTION5", "ADDITIONALINFORMATION"]
INF_HEADER = ["ACCESSION_NUMBER", "INFOTABLE_SK", "NAMEOFISSUER", "TITLEOFCLASS", "CUSIP", "FIGI", "VALUE", "SSHPRNAMT", "SSHPRNAMTTYPE", "PUTCALL", "INVESTMENTDISCRETION",
              "OTHERMANAGER", "VOTING_AUTH_SOLE", "VOTING_AUTH_SHARED", "VOTING_AUTH_NONE"]
SYN_README = ("<html><body><p>Form 13F Data Sets</p><table><tr><td>VALUE</td><td>Market value. Starting on January 3, 2023, market value is reported rounded to the nearest "
              "dollar. Previously, market value was reported in thousands.</td></tr><tr><td>SECFILENUMBER</td><td>SEC File Number (if applicable)</td></tr><tr><td>FORM13FFILENUMBER</td>"
              "<td>FORM 13F file number.</td></tr><tr><td>AMENDMENTTYPE</td><td>Amendment type is a restatement or adds new holdings entries.</td></tr><tr><td>x</td>"
              "<td>Filing date (DD-MON-YYYY) 13F-HR 13F-HR/A 13F-NT 13F-NT/A</td></tr></table></body></html>")


def write_syn_zip(path, subs, rows, padding=0):
    """A synthetic Form 13F data-set zip: the real column layout, with a planted address, phone and signatory that no output may carry."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("SUBMISSION.tsv", tsv_bytes(list(SUB_COLS), [[s.acc, d2dmy(iso(s.filing)), s.stype, s.cik, d2dmy(iso(s.period))] for s in subs]))
        cov = []
        for s in subs:
            row = {h: "" for h in COV_HEADER}
            row.update({"ACCESSION_NUMBER": s.acc, "ISAMENDMENT": s.isamend, "AMENDMENTTYPE": s.amendtype, "FILINGMANAGER_NAME": s.name, "FILINGMANAGER_STREET1": PLANT_ADDR,
                        "FILINGMANAGER_CITY": "Planted City", "FILINGMANAGER_ZIPCODE": "00000", "REPORTTYPE": s.reporttype, "SECFILENUMBER": s.secfile})
            cov.append([row[h] for h in COV_HEADER])
        zf.writestr("COVERPAGE.tsv", tsv_bytes(COV_HEADER, cov))
        zf.writestr("SUMMARYPAGE.tsv", tsv_bytes(list(SUM_COLS), [[s.acc, s.conf_omitted or "N"] for s in subs]))
        inf = []
        for i, r in enumerate(rows):
            inf.append([r.acc, str(i), r.name, r.title, r.cusip, "BBG000PLANT0", r.value, r.shares, r.sh_type, r.putcall, r.disc, r.other, r.shares, "0", "0"])
        for j in range(padding):
            inf.append([subs[0].acc, str(10 ** 6 + j), "FILLER %d CORP" % j, "COM", "FILL%05d" % j + "0", "", "100", "10", "SH", "", "SOLE", "", "10", "0", "0"])
        zf.writestr("INFOTABLE.tsv", tsv_bytes(INF_HEADER, inf))
        zf.writestr(SIG_NAME, tsv_bytes(["ACCESSION_NUMBER", "NAME", "TITLE", "PHONE", "SIGNATURE", "CITY", "STATEORCOUNTRY", "SIGNATUREDATE"],
                                               [[s.acc, PLANT_SIG, "CFO", PLANT_PHONE, PLANT_SIG, "Planted City", "NY", "01-JUL-2026"] for s in subs]))
        zf.writestr("FORM13F_metadata.json", b"{}")
        zf.writestr("FORM13F_readme.htm", SYN_README.encode("utf-8"))


class World:
    pass


SYN_FILERS = [
    # cik, name, secfile, public
    (1000001, "Alpha Capital Management LLC", "801-10001", "yes"), (1000002, "Beta Advisors LP", "801-10002", "yes"), (1000003, "Gamma Trust Bank NA", "8-20001", "yes"),
    (1000004, "Delta Public Pension Fund", "", "yes"), (1000005, "Jane Q Sample", "", "no"), (1000006, "Epsilon Hedge Partners LP", "802-30001", "yes"),
    (1000007, "Norges Bank", "028-5555", "yes"), (1000008, "Eta Quantitative Strategies LLC", "801-10008", "yes"), (1000009, "Theta Holdings Inc", "", "yes"),
    (1000010, "Iota Wealth Group LLC", "801-10010", "yes"), (1000011, "Kappa Family Office", "", "no"), (1000012, "Lambda Insurance Co", "801-10012", "yes"),
]
SYN_FILLER = [(1000100 + i, "Filler Investors %d LLC" % i, "801-4%04d" % i, "yes") for i in range(16)]
SYN_PINS = {      # synthetic accessions that reproduce the pins of C02 (the i2 sample rows by number)
    1: ("SPCX", 9001, 1000001, "171826745", "29358317651"), 2: ("SPCX", 9002, 1000002, "120801820", "20640198965"), 3: ("CBRS", 9003, 1000003, "7011028", None),
    5: ("CBRS", 9005, 1000005, "3110086", "687329006"), 6: ("CBRS", 9006, 1000006, "794467", "175577207"), 8: ("QNT", 9008, 1000008, "150000", None), 9: ("FRVO", 9009, 1000009, "20000", "584600"),
}


def build_syn_world():
    subs, rows = [], []
    n = 0
    sample = [dict(accession_number="") for _ in range(11)]
    pin_acc = {}
    for rn, (t, an, cik, sh, val) in SYN_PINS.items():
        acc = syn_acc(an)
        pin_acc[rn] = acc
        f = next(x for x in SYN_FILERS if x[0] == cik)
        subs.append(mk_sub(acc, cik, "2026-07-%02d" % (10 + rn), name=f[1], secfile=f[2]))
        rows.append(mk_row(acc, SYN_CUSIP[t], sh, val if val else str(int(Decimal(sh) * SYN_PRICE[t])), name=SYN_NAME[t], tick=t))
    rows.append(mk_row(pin_acc[5], SYN_CUSIP["CBRS"], "700000", "154700000", pc="CALL", name=SYN_NAME["CBRS"], tick="CBRS"))
    # row 4: three PUT rows, no shares row
    acc4 = syn_acc(9004)
    pin_acc[4] = acc4
    subs.append(mk_sub(acc4, 1000004, "2026-07-14", name="Delta Public Pension Fund"))
    for sh, v in (("40000", "4020800"), ("65700", "7085285"), ("40000", "5234720")):
        rows.append(mk_row(acc4, SYN_CUSIP["CBRS"], sh, v, pc="PUT", name=SYN_NAME["CBRS"], tick="CBRS"))
    for rn, acc in pin_acc.items():
        sample[rn - 1] = {"accession_number": acc}
    # every filer holds every deal: the 12 named filers (their pinned rows are above) and the fillers
    base = {"SPCX": 900000, "CBRS": 40000, "QNT": 12000, "FRVO": 90000, "INIO": 700000}
    k = 100
    allf = SYN_FILERS + SYN_FILLER
    for fi, (cik, nm, sec, pub) in enumerate(allf):
        for t in SYN_TICKERS:
            if any(v[0] == t and v[2] == cik for v in SYN_PINS.values()) or (t == "CBRS" and cik == 1000004):
                continue
            k += 1
            acc = syn_acc(k)
            subs.append(mk_sub(acc, cik, "2026-07-%02d" % (1 + fi % 25), name=nm, secfile=sec, conf="Y" if fi == 3 else "N"))
            sh = (fi + 1) * base[t] // 3 + 11 * (fi + 1)
            if cik in (1000005, 1000011):
                sh *= 100
            rows.append(mk_row(acc, SYN_CUSIP[t], str(sh), str(int(Decimal(sh) * SYN_PRICE[t])), name=SYN_NAME[t], tick=t, disc="SOLE" if fi % 2 == 0 else "DFND"))
    # extras: options, PRN, blank VALUE, a name-match row under another identifier, a restatement, a new-holdings amendment, an orphan, a duplicate pair, a late filing, an NT filer
    ex = syn_acc(8001)
    subs.append(mk_sub(ex, 1000001, "2026-08-01", "13F-HR/A", amend="RESTATEMENT", name="Alpha Capital Management LLC", secfile="801-10001"))
    rows.append(mk_row(ex, SYN_CUSIP["QNT"], "5000", "408500", name=SYN_NAME["QNT"], tick="QNT"))
    rows.append(mk_row(ex, SYN_CUSIP["QNT"], "1000", "81700", pc="CALL", name=SYN_NAME["QNT"], tick="QNT"))
    rows.append(mk_row(ex, SYN_CUSIP["QNT"], "300", "24510", sh_type="PRN", name=SYN_NAME["QNT"], tick="QNT"))
    rows.append(mk_row(ex, SYN_OTHER, "777", "100", name=SYN_NAME["QNT"], tick="QNT"))
    rows.append(mk_row(ex, SYN_OPT_CALL, "2000", "10", pc="CALL", name=SYN_NAME["QNT"], tick="QNT"))
    rows.append(mk_row(ex, SYN_OPT_PUT, "500", "10", pc="", name=SYN_NAME["QNT"], tick="QNT"))
    rows.append(mk_row(ex, SYN_CUSIP["QNT"], "60", "", name=SYN_NAME["QNT"], tick="QNT"))
    nh = syn_acc(8002)
    subs.append(mk_sub(nh, 1000002, "2026-08-02", "13F-HR/A", amend="NEW HOLDINGS", name="Beta Advisors LP", secfile="801-10002"))
    rows.append(mk_row(nh, SYN_CUSIP["INIO"], "25000", str(int(25000 * SYN_PRICE["INIO"])), name=SYN_NAME["INIO"], tick="INIO"))
    orph = syn_acc(8003)
    subs.append(mk_sub(orph, 1000300, "2026-08-03", "13F-HR/A", amend="NEW HOLDINGS", name="Orphan Capital LLC", secfile="801-99999"))
    rows.append(mk_row(orph, SYN_CUSIP["FRVO"], "15000", str(int(15000 * SYN_PRICE["FRVO"])), name=SYN_NAME["FRVO"], tick="FRVO"))
    for j, cik in enumerate((1000401, 1000402)):          # two filer numbers reporting identical shares
        a = syn_acc(8010 + j)
        subs.append(mk_sub(a, cik, "2026-08-05", name="Twin Fund %d LP" % j, secfile="801-7777%d" % j))
        rows.append(mk_row(a, SYN_CUSIP["INIO"], "123456", str(int(123456 * SYN_PRICE["INIO"])), name=SYN_NAME["INIO"], tick="INIO"))
    late = syn_acc(8020)
    subs.append(mk_sub(late, 1000500, "2026-09-01", name="Late Filer LLC", secfile="801-5"))
    rows.append(mk_row(late, SYN_CUSIP["FRVO"], "9000", str(int(9000 * SYN_PRICE["FRVO"])), name=SYN_NAME["FRVO"], tick="FRVO"))
    nt = syn_acc(8030)
    subs.append(mk_sub(nt, 1000600, "2026-08-04", "13F-NT", name="Notice Filer LLC"))
    # a Mar-quarter zip with one control filing
    ctl = syn_acc(7001)
    ctl_sub = [mk_sub(ctl, 1000001, "2026-05-01", period="2026-03-31", name="Alpha Capital Management LLC", secfile="801-10001")]
    ctl_rows = [mk_row(ctl, SYN_CUSIP["SPCX"], "1000", "100000", name=SYN_NAME["SPCX"], tick="SPCX")]
    w = World()
    w.subs, w.rows, w.sample = subs, rows, sample
    w.ctl_sub, w.ctl_rows = ctl_sub, ctl_rows
    return w


def syn_deal_inputs():
    rows = []

    def add(t, cl, lc, item, sh, asof, form, fd, sec, q):
        rows.append([t, cl, lc, item, sh, asof, form, fd, sec, q])

    syn_dates = {"SPCX": "2026-06-11", "CBRS": "2026-05-13", "QNT": "2026-06-03", "FRVO": "2026-05-12", "INIO": "2026-06-03", "BSP": "2026-06-30", "SKHY": "2026-07-09", "JMKE": "2026-07-31"}
    ftd = {"SPCX": "2026-06-12", "CBRS": "2026-05-14", "QNT": "2026-06-04", "FRVO": "2026-05-13", "INIO": "2026-06-04", "BSP": "2026-07-01", "SKHY": "2026-07-10", "JMKE": "2026-08-01"}
    for t in DEAL_ORDER:
        add(t, "", "", "pricing_date", "", syn_dates[t], "424B4" if t in SYN_DEN else "deal_master", "2026-06-12" if t in SYN_DEN else "", "Cover page", "")
        add(t, "", "", "first_trade_date", "", ftd[t], "exchange notice", "", "synthetic", "synthetic note")
        if t in SYN_DEN:
            a, b, c_, ipo = SYN_DEN[t]
            cls = ["Class A", "Class B"] if b else ["Common shares"]
            for i, cl in enumerate(cls):
                lc = "yes" if i == 0 else "no"
                add(t, cl, lc, "qe_balance_sheet", str((a, b)[i]), "2026-06-30", "10-Q", "2026-08-12", "Item 1, balance sheet", "synthetic quote")
                add(t, cl, lc, "qe_cover", str((a, b)[i] + 1000), "2026-08-05", "10-Q", "2026-08-12", "Cover page", "synthetic quote")
            add(t, cls[0], "yes", "after_offering_base", str(c_), "", "424B4", "2026-06-12", "The Offering", "synthetic quote")
            add(t, cls[0], "yes", "ipo_shares_base", str(ipo), "", "424B4", "2026-06-12", "Cover page", "synthetic quote")
            add(t, "", "", "offer_price_usd", str(SYN_OFFER[t]), "", "424B4", "2026-06-12", "Cover page", "synthetic quote")
    return csv_text(rows, DEAL_INPUT_FIELDS)


def syn_i2_holders():
    h = ["ticker", "issuer_name_in_filing", "issuer_cik", "form_type", "filing_date", "event_date_or_date_of_event", "reporting_person_name", "shares_beneficially_owned", "percent_of_class",
         "type_of_reporting_person", "citizenship_or_organization", "securities_class_title", "accession_number", "source_url"]

    def row(t, form, fd, ev, name, sh, pctc, typ, cls="Class A Common Stock"):
        return dict(zip(h, [t, SYN_NAME[t], "0", form, fd, ev, name, sh, pctc, typ, "DE", cls, "0000000000-26-000001", ""]))

    return [row("SPCX", "SCHEDULE 13G", "2026-08-14", "06/30/2026", "Alpha Capital Management LLC", "50000000.00", "0.6", "IA"),
            row("SPCX", "SCHEDULE 13G", "2026-08-14", "06/30/2026", "Zeta Ventures LP", "155393350.00", "2.0", "PN"),
            row("SPCX", "SCHEDULE 13D", "2026-08-14", "06/30/2026", "Founder Person", "6418547515.00", "48.0", "IN"),
            row("SPCX", "SCHEDULE 13G", "2026-03-14", "03/31/2026", "Zeta Ventures LP", "1.00", "0.1", "PN"),
            row("SPCX", "SCHEDULE 13G", "2026-08-14", "06/30/2026", "Zeta Ventures LP", "9.00", "0.1", "PN", cls="Class B Common Stock"),
            row("SPCX", "SCHEDULE 13G", "2026-08-14", "06/30/2026", "Unreviewed Org LLC", "1000000.00", "0.01", "IA"),
            row("CBRS", "SCHEDULE 13G", "2026-08-14", "06/30/2026", "Epsilon Hedge Partners LP", "10543836.00", "10.7", "IA"),
            row("FRVO", "SCHEDULE 13D", "2026-08-14", "06/30/2026", "Strategic Energy Corp", "36000000.00", "12.5", "CO")]


def syn_i1b():
    return [dict(deal="Fervo Energy Company (FRVO)", investor=i, amount="Part of an aggregate $350 million (4 named investors jointly; no individual split disclosed)", source_line="")
            for i in ("Atlas Point Energy Infrastructure Fund, LLC", "Norges Bank Investment Management", "Wellington Management", "Funds/accounts managed by Capital Research Global Investors")]


def syn_review_rows():
    rows = []
    kinds = ["asset_manager", "asset_manager", "bank_broker", "pension_endowment_sovereign", "other", "hedge_fund", "pension_endowment_sovereign", "hedge_fund", "corporate_strategic",
             "asset_manager", "other", "insurer"]
    for (cik, nm, sec, pub), kd in zip(SYN_FILERS, kinds):
        match = ""
        if nm == "Alpha Capital Management LLC":
            match = "Alpha Capital Management LLC"
        elif nm == "Epsilon Hedge Partners LP":
            match = "Epsilon Hedge Partners LP"
        rows.append([str(cik), nm, pub, kd, "name_review", "SPCX;QNT" if nm.startswith("Alpha") else "no", match, "FRVO:Norges Bank" if nm == "Norges Bank" else ""])
    for cik, nm, sec, pub in SYN_FILLER:
        rows.append([str(cik), nm, pub, "asset_manager", "name_review", "no", "", ""])
    for cik, nm in ((1000401, "Twin Fund 0 LP"), (1000402, "Twin Fund 1 LP"), (1000300, "Orphan Capital LLC"), (1000500, "Late Filer LLC")):
        rows.append([str(cik), nm, "yes", "other", "name_review", "no", "", ""])
    rows.append(["", "Zeta Ventures LP", "yes", "", "", "", "Zeta Ventures LP", ""])
    rows.append(["", "Founder Person", "yes", "", "", "", "Founder Person", ""])      # a reviewer slip: the rule for type IN must still withhold it
    rows.append(["", "Strategic Energy Corp", "yes", "", "", "", "Strategic Energy Corp", ""])
    return rows


def syn_map_rows():
    out = [{"ticker": t, "cusip": cu, "status": "listed", "evidence": "official_list_2026q2", "reason": ""} for t, cu in SYN_CUSIP.items()]
    out.append({"ticker": "QNT", "cusip": SYN_OTHER, "status": "rejected", "evidence": "", "reason": "synthetic other identifier"})
    out.append({"ticker": "QNT", "cusip": SYN_OPT_CALL, "status": "option_call", "evidence": "official_list_2026q2", "reason": "synthetic call identifier"})
    out.append({"ticker": "QNT", "cusip": SYN_OPT_PUT, "status": "option_put", "evidence": "official_list_2026q2", "reason": "synthetic put identifier"})
    return out


def syn_scans(w, tmp):
    """Write the two synthetic zips, scan them through the real code path, and load the scans back."""
    zdir = os.path.join(tmp, "zips")
    os.makedirs(zdir, exist_ok=True)
    cache = os.path.join(tmp, "cache")
    os.makedirs(cache, exist_ok=True)
    p1 = os.path.join(zdir, "01jun2026-31aug2026_form13f.zip")
    p0 = os.path.join(zdir, "01mar2026-31may2026_form13f.zip")
    write_syn_zip(p1, w.subs, w.rows, padding=50)
    write_syn_zip(p0, w.ctl_sub, w.ctl_rows, padding=5)
    for p in (p0, p1):
        with zipfile.ZipFile(p) as zf:
            subs, rows, part = scan_zip(zf, say=lambda *a: None)
            part["readme"] = readme_facts(zf.read("FORM13F_readme.htm"))
        write_scan(cache, os.path.basename(p), p, subs, rows, part, "none")
    return zdir, cache, load_scans(cache)


_WORLD = {}


def get_world():
    if "w" in _WORLD:
        return _WORLD["w"]
    w = build_syn_world()
    tmp = tempfile.mkdtemp(prefix="ipo13f_selftest_")
    zdir, cache, scans = syn_scans(w, tmp)
    w.tmp, w.zdir, w.cache, w.scans = tmp, zdir, cache, scans
    w.master = read_master()
    w.deal_text = syn_deal_inputs()
    w.deal_rows = read_csv_rows_text(w.deal_text)
    w.i2, w.i1b = syn_i2_holders(), syn_i1b()
    w.review = Review([dict(zip(FILER_REVIEW_FIELDS, r)) for r in syn_review_rows()])
    w.maps = syn_map_rows()
    w.cfg = {"gates": [("CUSIP_MAP_SHA256", True, ""), ("FILER_REVIEW_SHA256", True, ""), ("DEAL_INPUTS_SHA256", True, ""), ("cache stamp", True, "")], "zip_problems": [], "fields_missing": [],
             "secfile_is_regulatory": True, "readme_lines": ["`VALUE`: synthetic"], "readme_recorded": True}
    _WORLD["w"] = w
    return w


def read_csv_rows_text(text):
    lines = [l for l in text.split("\n") if l.strip() and not l.startswith("# source:")]
    rd = list(csv.reader(lines))
    return [dict(zip(rd[0], r)) for r in rd[1:]]


def world_compute(w=None, cfg=None, review=None, i2=None, deal_rows=None, scans=None, maps=None):
    w = w or get_world()
    cfg = dict(w.cfg if cfg is None else cfg)
    return compute(scans or w.scans, maps or w.maps, deal_rows or w.deal_rows, w.master, i2 if i2 is not None else w.i2, [dict(accession_number=a["accession_number"]) for a in w.sample],
                   w.i1b, review or w.review, cfg)


def world_texts(**kw):
    w = get_world()
    c = world_compute(**kw)
    texts, det = finish_build(c, w.deal_text)
    return c, texts


def world_texts_checked(**kw):
    """The same without the refusal: (compute, texts, problems), so that a guard test can say what failed."""
    w = get_world()
    c = world_compute(**kw)
    texts, det = render_final(c, w.deal_text)
    return c, texts, all_problems(texts, c)


# ------------------------------------------------------------------------------------------------------------------------
# the guard tests
# ------------------------------------------------------------------------------------------------------------------------
def total_sh(subs, rows, **kw):
    poss, res = poss_of(subs, rows, **kw)
    return dsum(p.sh for p in poss.values()), res, poss


def t_g1(ck):
    O = lambda acc, f, stype="13F-HR", **k: mk_sub(acc, 1, f, stype, **k)
    other = lambda acc: mk_row(acc, "TSTB02108", "1", "1", name="OTHER CO", tick="")
    # an amendment is not summed with its original
    s, res, _ = total_sh([O("A1", "2026-07-10"), O("A2", "2026-07-20", "13F-HR/A", amend="RESTATEMENT")], [mk_row("A1", shares="100"), mk_row("A2", shares="150")])
    ck.eq("original 100 + later RESTATEMENT 150 -> 150, not 250", s, Decimal(150))
    # a restatement filed BEFORE the original loses
    s, res, _ = total_sh([O("A1", "2026-07-20"), O("A2", "2026-07-10", "13F-HR/A", amend="RESTATEMENT")], [mk_row("A1", shares="100"), mk_row("A2", shares="150")])
    ck.eq("a RESTATEMENT filed before the original loses: 100, not 150", s, Decimal(100))
    ck.eq("it is listed as stale", [r.stale for r in res.values()], [["A2"]])
    # a NEW HOLDINGS is added
    s, res, _ = total_sh([O("A1", "2026-07-10"), O("A3", "2026-07-20", "13F-HR/A", amend="NEW HOLDINGS")], [other("A1"), mk_row("A3", shares="40")])
    ck.eq("original without the identifier + later NEW HOLDINGS 40 -> 40", s, Decimal(40))
    # a NEW HOLDINGS filed before the latest RESTATEMENT is superseded
    s, res, _ = total_sh([O("A1", "2026-07-10"), O("A3", "2026-07-12", "13F-HR/A", amend="NEW HOLDINGS"), O("A2", "2026-07-20", "13F-HR/A", amend="RESTATEMENT")],
                         [other("A1"), mk_row("A3", shares="40"), mk_row("A2", shares="150")])
    ck.eq("NEW HOLDINGS filed before a later RESTATEMENT is not kept: 150, not 190", s, Decimal(150))
    # the later of two restatements wins
    s, res, _ = total_sh([O("A1", "2026-07-10"), O("R1", "2026-07-20", "13F-HR/A", amend="RESTATEMENT"), O("R2", "2026-07-25", "13F-HR/A", amend="RESTATEMENT")],
                         [mk_row("A1", shares="100"), mk_row("R1", shares="150"), mk_row("R2", shares="180")])
    ck.eq("the later of two RESTATEMENTs wins: 180", s, Decimal(180))
    # several originals: the latest wins, the others listed
    s, res, _ = total_sh([O("O1", "2026-07-10"), O("O2", "2026-07-12")], [mk_row("O1", shares="100"), mk_row("O2", shares="120")])
    ck.eq("two originals: the latest only, 120", s, Decimal(120))
    ck.eq("the earlier original is listed", [r.severals for r in res.values()], [["O1"]])
    # orphans
    s, res, _ = total_sh([O("N1", "2026-07-20", "13F-HR/A", amend="NEW HOLDINGS")], [mk_row("N1", shares="40")])
    ck.eq("an orphan NEW HOLDINGS stands alone: 40", s, Decimal(40))
    ck.eq("the orphan is listed", [r.orphans for r in res.values()], [["N1"]])
    s, res, _ = total_sh([O("N2", "2026-07-20", "13F-HR/A", amend="RESTATEMENT")], [mk_row("N2", shares="150")])
    ck.eq("an orphan RESTATEMENT becomes the base: 150", s, Decimal(150))
    # a duplicate amendment is counted once and listed
    s, res, _ = total_sh([O("A1", "2026-07-10"), O("D1", "2026-07-20", "13F-HR/A", amend="NEW HOLDINGS"), O("D2", "2026-07-21", "13F-HR/A", amend="NEW HOLDINGS")],
                         [other("A1"), mk_row("D1", shares="40"), mk_row("D2", shares="40")])
    ck.eq("two amendments with identical rows count once: 40", s, Decimal(40))
    ck.eq("the duplicate is listed", [r.dups for r in res.values()], [["D2"]])
    # a repeated identifier is flagged and still added
    s, res, _ = total_sh([O("A1", "2026-07-10"), O("P1", "2026-07-20", "13F-HR/A", amend="NEW HOLDINGS")], [mk_row("A1", shares="100"), mk_row("P1", shares="30")])
    ck.eq("a NEW HOLDINGS repeating an identifier is still added: 130", s, Decimal(130))
    ck.eq("the repeat is flagged", [r.repeats for r in res.values()], [["P1"]])
    # an unknown AMENDMENTTYPE is a failure listing it
    ck.raises("an unknown AMENDMENTTYPE is refused", DataError, lambda: total_sh([O("A1", "2026-07-10"), O("U1", "2026-07-20", "13F-HR/A", amend="BOGUS TYPE")], [mk_row("A1"), mk_row("U1")]))
    try:
        total_sh([O("A1", "2026-07-10"), O("U1", "2026-07-20", "13F-HR/A", amend="BOGUS TYPE")], [mk_row("A1"), mk_row("U1")])
    except DataError as e:
        ck.ok("the refusal names the value", "BOGUS TYPE" in str(e), str(e))
    except Exception:
        pass


def t_g2(ck):
    subs = [mk_sub("F1", 1, "2026-07-10"), mk_sub("F0", 1, "2026-05-10", period="2026-03-31")]
    rows = [mk_row("F1", shares="100", value="1000"), mk_row("F1", shares="50", value="500", disc="DFND"), mk_row("F1", shares="10", value=""),
            mk_row("F1", shares="30", value="300", pc="CALL"), mk_row("F1", shares="20", value="200", pc="PUT"), mk_row("F1", shares="999", value="9", sh_type="PRN"),
            mk_row("F1", cusip="TSTA0120" + "7", shares="77", value="77"), mk_row("F0", shares="5", value="50")]
    poss, res = poss_of(subs, rows)
    p = poss["1"]
    ck.eq("shares: SH, blank PUTCALL, all discretion types (blank VALUE included): 160", p.sh, Decimal(160))
    ck.eq("sole discretion only: 110", p.sole, Decimal(110))
    ck.eq("calls and puts are kept apart", (p.calls, p.puts), (Decimal(30), Decimal(20)))
    ck.eq("PRN row excluded and counted", p.n_prn, 1)
    ck.eq("a name match under another identifier goes to its own column: 77", p.name_other, Decimal(77))
    ck.eq("the blank-VALUE row is counted", p.n_value_blank, 1)
    ck.eq("implied price excludes the blank-VALUE row: 1500/150 = 10", p.price(), Decimal(10))
    ck.ok("sole is at most the total", p.sole <= p.sh, "%s > %s" % (p.sole, p.sh))
    ck.ok("shares are Decimal", isinstance(p.sh, Decimal), type(p.sh).__name__)
    optmap = {"ZZZZZZ904": ("SPCX", "CALL"), "ZZZZZZ954": ("SPCX", "PUT")}
    orows = [mk_row("F1", shares="100", value="1000"), mk_row("F1", cusip="ZZZZZZ904", shares="30", value="30", pc="CALL"), mk_row("F1", cusip="ZZZZZZ904", shares="20", value="20", pc=""),
             mk_row("F1", cusip="ZZZZZZ954", shares="7", value="7", pc="PUT"), mk_row("F1", cusip="ZZZZZZ954", shares="3", value="3", pc=""), mk_row("F1", shares="11", pc="CALL")]
    by = collections.defaultdict(list)
    for r in orows:
        by[r.acc].append(r)
    sba = {s.acc: s for s in subs}
    res0 = consolidate_all(subs, by, cusips={"TSTA01102"})
    po = holdings(res0, sba, by, "SPCX", "TSTA01102", dt.date(2026, 6, 30), optmap)["1"]
    ck.eq("rows under the CALL and PUT identifiers are options: calls = 30 + 20 (role when PUTCALL is blank) + 11 on the main identifier", po.calls, Decimal(61))
    ck.eq("puts = 7 + 3", po.puts, Decimal(10))
    ck.eq("option-identifier rows never enter sh_13f", po.sh, Decimal(100))
    ck.eq("option-identifier rows are counted for C17: 4 rows, 60 shares underlying", (po.n_optid, po.optid_sh), (4, Decimal(60)))
    p2, _ = poss_of([mk_sub("G1", 2, "2026-07-10")], [mk_row("G1", shares="0.1"), mk_row("G1", shares="0.2")])
    q = p2["2"]
    ck.ok("0.1 + 0.2 is exactly 0.3 (no float)", isinstance(q.sh, Decimal) and q.sh == Decimal("0.3"), repr(q.sh))
    ck.eq("non-integral rows are kept and counted", q.n_nonint, 2)


def t_g3(ck):
    ck.eq("lower case and a trailing space are normalised", norm_cusip("tsta01102 "), "TSTA01102")
    ck.eq("an internal space is stripped", norm_cusip("TSTA 01102"), "TSTA01102")
    ck.eq("an 8-character value is not padded", norm_cusip("TSTA0110"), "TSTA0110")
    ck.ok("the check digit of a valid identifier passes", cusip_valid("TSTA01102"))
    ck.ok("a bad check digit is refused", not cusip_valid("TSTA01103"))
    ck.ok("a short value is not valid", not cusip_valid("TSTA0110"))
    subs = [mk_sub("F1", 1, "2026-07-10")]
    rows = [mk_row("F1", shares="100"), mk_row("F1", cusip=SYN_OTHER, shares="77")]
    poss, _ = poss_of(subs, rows)
    ck.eq("a name match without the mapped identifier is not added to sh_13f", poss["1"].sh, Decimal(100))
    # a stale stamp
    tmp = tempfile.mkdtemp(prefix="ipo13f_g3_")
    di = os.path.join(tmp, "deal_inputs.csv")
    write_text(os.path.join(tmp, "cusip_map.csv"), "ticker,cusip,status,evidence,reason\nSPCX,TSTA01102,listed,official_list_2026q2,\n")
    write_text(os.path.join(tmp, "filer_review.csv"), ",".join(FILER_REVIEW_FIELDS) + "\n")
    write_text(di, "a\n")
    consts = {"CUSIP_MAP_SHA256": sha256_path(os.path.join(tmp, "cusip_map.csv")), "FILER_REVIEW_SHA256": sha256_path(os.path.join(tmp, "filer_review.csv")), "DEAL_INPUTS_SHA256": sha256_path(di)}

    class FakeScan:
        zip_name = "z.zip"

        def __init__(self, h):
            self.stamp = {"map_sha256": h}

    _, probs = gate_state(tmp, di, [FakeScan("oldhash")], consts)
    ck.ok("a cache stamped with another map hash is refused", any("stamped" in p for p in probs), str(probs))
    _, probs = gate_state(tmp, di, [FakeScan(consts["CUSIP_MAP_SHA256"])], consts)
    ck.eq("a cache stamped with the current hash passes", probs, [])
    # a mapped identifier under a non-matching name is listed
    w = get_world()
    sc0 = next(s for s in w.scans if s.zip_name.startswith("01jun"))
    extra = Row(sc0.rows[0].acc, "SOMETHING ELSE LTD", "COM", SYN_CUSIP["SPCX"], "100", "10", "SH", "", "SOLE", "", "")
    scans = [Scan(sc0.zip_name, sc0.stamp, sc0.subs, sc0.rows + [extra])] + [s for s in w.scans if s is not sc0]
    c = world_compute(scans=scans)
    ck.eq("C05a lists a mapped identifier filed under another name", [r[4] for r in c.checks if r[0] == "C05a"], ["WARN"])


def t_g4(ck):
    ck.raises("a negative SSHPRNAMT is refused", DataError, lambda: parse_shares("-5"))
    ck.raises("a negative VALUE is refused", DataError, lambda: parse_value("-1"))
    ck.eq("VALUE is whole dollars: 1000 stays 1000", parse_value("1000"), Decimal(1000))
    old = README_SAYS_THOUSANDS[0]
    README_SAYS_THOUSANDS[0] = True
    try:
        ck.eq("VALUE is not rescaled even when a readme says thousands", parse_value("1000"), Decimal(1000))
    finally:
        README_SAYS_THOUSANDS[0] = old
    poss, _ = poss_of([mk_sub("F1", 1, "2026-07-10")], [mk_row("F1", shares="100"), mk_row("F1", shares="40", pc="PUT")])
    ck.eq("a put is never subtracted from shares", poss["1"].sh, Decimal(100))
    subs = [mk_sub("S%d" % i, i, "2026-07-10") for i in range(1, 8)]
    prices = ["10.00", "10.00", "10.00", "10.00", "10.20", "10.15", "10.09"]       # off the median by 2%, 1.5% and 0.9%
    rows = [mk_row("S%d" % (i + 1), shares="10000", value=str(int(Decimal(prices[i]) * 10000))) for i in range(7)]
    poss, _ = poss_of(subs, rows)
    med, outl = implied_outliers(poss)
    ck.eq("the median implied price is 10.00", med, Decimal("10"))
    ck.eq("filers more than 1% off the median are listed: the 2% and 1.5% filers, not the 0.9% filer", sorted(p.cik for p, _ in outl), ["5", "6"])
    ck.ok("a deal median 10x the offer price is a problem", median_bounds_problem(Decimal(100), Decimal(10)) is not None)
    ck.ok("a deal median 0.1x the offer price is a problem", median_bounds_problem(Decimal(1), Decimal(10)) is not None)
    ck.ok("a median at the offer price is fine", median_bounds_problem(Decimal(10), Decimal(10)) is None)


def t_g5(ck):
    ck.eq("pricing on a quarter-end day goes to the next quarter-end", first_qe_after(dt.date(2026, 6, 30)), dt.date(2026, 9, 30))
    ck.eq("2026-05-13 -> 2026-06-30", first_qe_after(dt.date(2026, 5, 13)), dt.date(2026, 6, 30))
    ck.eq("2026-12-31 -> 2027-03-31", first_qe_after(dt.date(2026, 12, 31)), dt.date(2027, 3, 31))
    ck.eq("due date for 2026-09-30 is Monday 2026-11-16", due_date(dt.date(2026, 9, 30)), dt.date(2026, 11, 16))
    ck.eq("due date for 2026-06-30 is 2026-08-14", due_date(dt.date(2026, 6, 30)), dt.date(2026, 8, 14))
    ck.eq("due date for 2026-12-31 skips Presidents Day: 2027-02-16", due_date(dt.date(2026, 12, 31)), dt.date(2027, 2, 16))
    w = get_world()
    rows = [dict(r) for r in w.deal_rows]
    for r in rows:
        if r["ticker"] == "SPCX" and r["item"] == "pricing_date":
            r["asof"] = "2026-06-29"
        if r["ticker"] == "SPCX" and r["item"] == "first_trade_date":
            r["asof"] = "2026-07-01"
    c = world_compute(deal_rows=rows)
    ck.eq("the pricing date, not the first trading day, drives first_qe", [d["first_qe"] for d in c.deals if d["ticker"] == "SPCX"], [dt.date(2026, 6, 30)])


def t_g6(ck):
    for i, m in enumerate(MONTHS, start=1):
        try:
            got = parse_dmy("15-%s-2026" % m)
        except DataError:
            got = None
        ck.eq("15-%s-2026 parses in English" % m, got, dt.date(2026, i, 15))
    ck.eq("30-JUN-2026", parse_dmy("30-JUN-2026"), dt.date(2026, 6, 30))
    ck.eq("05-MAR-2026 is 5 March, not 3 May", parse_dmy("05-MAR-2026"), dt.date(2026, 3, 5))
    names = ["01mar2026-31may2026_form13f.zip", "01jun2026-31aug2026_form13f.zip"]
    ck.eq("the vintage is the newest window end", vintage_of(names), "13f_to_2026-08-31")
    ck.eq("the vintage does not depend on the order", vintage_of(names[::-1]), "13f_to_2026-08-31")
    sl = source_line(names)
    ck.ok("the source line has no retrieval date", dt.date.today().isoformat() not in sl and "etrieved" not in sl and sl.endswith("form13f.zip."), sl)
    ck.ok("the vintage is not today's date", dt.date.today().isoformat() not in vintage_of(names))


def t_g7(ck):
    w = get_world()
    d = denominators(w.deal_rows, "CBRS")
    ck.eq("primary is the listed class's balance-sheet count", (d["den_listed_10q_sh"], d["den_listed_10q_item"]), (Decimal(103220568), "qe_balance_sheet"))
    ck.eq("the prospectus count is the variant", d["den_listed_prosp_sh"], Decimal(30000000))
    ck.eq("the offer price comes from the offer_price_usd row of deal_inputs.csv", d["offer_price"], Decimal("185.00"))
    ck.eq("all classes sum the same item", d["den_all_classes_10q_sh"], Decimal(103220568 + 121301359))
    no10q = [r for r in w.deal_rows if not (r["ticker"] == "CBRS" and r["item"] in ("qe_balance_sheet", "qe_cover"))]
    d2 = denominators(no10q, "CBRS", w.i2)
    ck.ok("a deal without a 10-Q has a BLANK primary (not the prospectus, not 0, not inferred)", d2["den_listed_10q_sh"] is None, repr(d2["den_listed_10q_sh"]))
    ck.eq("the prospectus variant is still available", d2["den_listed_prosp_sh"], Decimal(30000000))
    cover_only = [r for r in w.deal_rows if not (r["ticker"] == "CBRS" and r["item"] == "qe_balance_sheet")]
    d3 = denominators(cover_only, "CBRS")
    ck.eq("the cover count is used only when there is no balance-sheet count", d3["den_listed_10q_item"], "qe_cover")
    ck.ok("the listed class is not the all-classes sum", d["den_listed_10q_sh"] != d["den_all_classes_10q_sh"])
    # the denominator at its point of use: pct_of_listed in holdings.csv against the balance-sheet count read straight from deal_inputs.csv, for deals whose prospectus count differs
    c, texts, wp = world_texts_checked()
    hold = {r["ticker"]: r for r in read_csv_rows_text(texts["holdings.csv"])}
    differs = 0
    for t in ("SPCX", "CBRS", "QNT", "FRVO", "INIO"):
        lc = [r for r in w.deal_rows if r["ticker"] == t and r["is_listed_class"] == "yes" and r["item"] == "qe_balance_sheet"][0]
        ao = [r for r in w.deal_rows if r["ticker"] == t and r["is_listed_class"] == "yes" and r["item"] == "after_offering_base"][0]
        differs += lc["shares"] != ao["shares"]
        want = qfix(Decimal(100) * Decimal(hold[t]["sh_13f"]) / Decimal(lc["shares"]), 3)
        ck.eq("%s: pct_of_listed in holdings.csv = 100 x sh_13f / the quarter-end balance-sheet count" % t, hold[t]["pct_of_listed"], dstr(want, 3))
    ck.ok("the synthetic deals include ones whose prospectus count differs", differs >= 3, str(differs))
    # the build gate
    tmp = tempfile.mkdtemp(prefix="ipo13f_g7_")
    di = os.path.join(tmp, "deal_inputs.csv")
    write_text(os.path.join(tmp, "cusip_map.csv"), "x\n")
    write_text(os.path.join(tmp, "filer_review.csv"), "y\n")
    write_text(di, "z\n")
    good = {"CUSIP_MAP_SHA256": sha256_path(os.path.join(tmp, "cusip_map.csv")), "FILER_REVIEW_SHA256": sha256_path(os.path.join(tmp, "filer_review.csv")), "DEAL_INPUTS_SHA256": sha256_path(di)}
    _, probs = gate_state(tmp, di, [], good)
    ck.eq("matching constants pass", probs, [])
    bad = dict(good, DEAL_INPUTS_SHA256="0" * 64)
    _, probs = gate_state(tmp, di, [], bad)
    ck.ok("a DEAL_INPUTS_SHA256 mismatch is refused", any("DEAL_INPUTS_SHA256" in p for p in probs), str(probs))
    _, probs = gate_state(tmp, di, [], dict(good, FILER_REVIEW_SHA256=""))
    ck.ok("an unset constant is refused", any("not set" in p for p in probs), str(probs))
    ck.ok("a placeholder first trading day is refused", any("placeholder" in p for p in deal_input_problems([dict(r, asof=FIRST_TRADE_PLACEHOLDER) if r["item"] == "first_trade_date" else r for r in w.deal_rows])))
    ck.eq("the clean synthetic inputs have no problem", deal_input_problems(w.deal_rows), [])


def t_g8(ck):
    wts = weights({"A": Decimal(100), "B": Decimal(300), "INIO": Decimal(0)}, ["A", "B", "INIO"])
    ck.eq("INNIO's weight is exactly 0", wts["INIO"], Decimal(0))
    ck.eq("weights are proceeds shares", (wts["A"], wts["B"]), (Decimal("0.25"), Decimal("0.75")))
    third = {k: Decimal(1) / Decimal(3) for k in "ABC"}
    ck.ok("the weight identity is tested on unrounded weights", weight_identity_ok(third))
    meas = {"SPCX": {"sh_13f": Decimal(50), "den_listed_10q_sh": Decimal(100), "pct_of_listed": Decimal(50)},
            "AAA": {"sh_13f": Decimal(10), "den_listed_10q_sh": Decimal(100), "pct_of_listed": Decimal(10)},
            "BBB": {"sh_13f": Decimal(30), "den_listed_10q_sh": Decimal(100), "pct_of_listed": Decimal(30)},
            "NOQ": {"sh_13f": Decimal(99), "den_listed_10q_sh": None, "pct_of_listed": None}}
    w = {"SPCX": Decimal("0.5"), "AAA": Decimal("0.2"), "BBB": Decimal("0.2"), "NOQ": Decimal("0.1")}
    a = pooled_weighted(meas, w)
    ck.eq("a blank-primary deal is not in the pooled or weighted figure", sorted(a["tickers"]), ["AAA", "BBB", "SPCX"])
    ck.eq("it is named", a["blank"], ["NOQ"])
    ck.eq("pooled = 90 / 300 = 30", a["pooled_pct"], Decimal(30))
    ck.eq("weights are renormalised among the rest: (0.5*50+0.2*10+0.2*30)/0.9", qfix(a["weighted_pct"], 6), qfix(Decimal("33") / Decimal("0.9"), 6))
    x = pooled_weighted(meas, w, exclude=("SPCX",))
    ck.ok("the ex-SpaceX figure does not include SPCX", "SPCX" not in x["tickers"], str(x["tickers"]))
    ck.eq("ex-SpaceX pooled = 40/200 = 20", x["pooled_pct"], Decimal(20))
    ck.ok("the median and range sit beside the weighted figure", a["median_pct"] is not None and a["min_pct"] == Decimal(10) and a["max_pct"] == Decimal(50), str((a["median_pct"], a["min_pct"], a["max_pct"])))


def t_g9(ck):
    subs, rows = [], []
    secs = ["801-1", "802-2", "8-3", "", "028-4", "801-5", "801-6", "8-7", "", "801-8", "801-9", "802-10"]
    for i, sec in enumerate(secs, start=1):
        subs.append(mk_sub("F%d" % i, i, "2026-07-10", secfile=sec))
        rows.append(mk_row("F%d" % i, shares=str(1000 * i)))
    poss, _ = poss_of(subs, rows)
    den = {"den_listed_10q_sh": Decimal(100000), "ipo_shares_base": Decimal(1000), "offer_price": Decimal(10)}
    m = deal_measures(poss, den)
    regs = reg_rows(poss, den)
    ck.eq("reg_category sums to sh_13f", dsum(r[2] for r in regs), m["sh_13f"])
    ck.ok("all five categories appear", {r[0] for r in regs} == set(REG_CATEGORIES), str([r[0] for r in regs]))
    ck.ok("top-10 is at least top-1", m["top10"] >= m["top1"], "%s < %s" % (m["top10"], m["top1"]))
    ck.eq("top-10 is the ten largest", m["top10"], Decimal(sum(1000 * i for i in range(3, 13))))
    # tie order must not depend on insertion order
    import random
    tied = [(str(i), "2026-07-10") for i in (9, 10, 100, 2, 33, 1000)]
    orders = set()
    for seed in (1, 2, 3, 4):
        r = random.Random(seed)
        items = list(tied)
        r.shuffle(items)
        subs2 = [mk_sub("T%s" % c, c, f) for c, f in items]
        rows2 = [mk_row("T%s" % c, shares="5000") for c, f in items]
        poss2, _ = poss_of(subs2, rows2)
        orders.add(tuple(p.cik for p in rank_filers(poss2)))
    ck.eq("equal holders rank in the same order whatever the input order (by filer number)", len(orders), 1)
    ck.eq("and that order is ascending filer number (numeric, not text)", list(orders)[0], tuple(str(i) for i in (2, 9, 10, 33, 100, 1000)))


def t_g10(ck):
    subs = [mk_sub("D%d" % i, i, "2026-07-10") for i in (1, 2, 3, 4, 5)]
    rows = [mk_row("D1", shares="123456"), mk_row("D2", shares="123456"), mk_row("D3", shares="9999"), mk_row("D4", shares="9999"), mk_row("D5", shares="55555")]
    poss, _ = poss_of(subs, rows)
    dup = duplicate_suspects(poss)
    ck.eq("two filer numbers with identical shares of 10,000 or more are flagged", [(sh, [rk for rk, _ in lst]) for sh, lst in dup], [(Decimal(123456), [1, 2])])
    ck.ok("identical small holdings are not flagged", all(sh >= 10000 for sh, _ in dup))


def t_g11(ck):
    s1 = Sub("DUP-1", dt.date(2026, 7, 1), "13F-HR", "1", dt.date(2026, 6, 30))
    s2 = Sub("DUP-1", dt.date(2026, 9, 1), "13F-HR", "1", dt.date(2026, 6, 30))
    a = Scan("01jun2026-31aug2026_form13f.zip", {}, [s1], [])
    b = Scan("01sep2026-30nov2026_form13f.zip", {}, [s2], [])
    ck.ok("one accession in two zips is a FAIL", bool(accession_problems([a, b])))
    ck.eq("distinct accessions are fine", accession_problems([a, Scan(b.zip_name, {}, [Sub("OTHER-1", dt.date(2026, 9, 1), "13F-HR", "2", dt.date(2026, 6, 30))], [])]), [])
    # revisions are regenerated from the cached vintages, never appended
    w = get_world()
    third_sub = mk_sub(syn_acc(6001), 1000001, "2026-09-20", "13F-HR/A", amend="NEW HOLDINGS", name="Alpha Capital Management LLC", secfile="801-10001")
    third = Scan("01sep2026-30nov2026_form13f.zip", dict(w.scans[0].stamp, zip_name="01sep2026-30nov2026_form13f.zip", n_submissions=1, n_infotable_rows=1, zip_bytes=1, zip_sha256="0" * 64),
                 [third_sub], [mk_row(third_sub.acc, SYN_CUSIP["SPCX"], "2500", "427150", name=SYN_NAME["SPCX"], tick="SPCX")])
    scans = list(w.scans) + [third]
    c = world_compute(scans=scans)
    r1 = c.tables["revisions.csv"]
    ck.ok("revisions.csv has a row per 30 Jun deal for the new vintage", len(r1) >= 5 and all(r[1] == "13f_to_2026-11-30" for r in r1), str(r1[:2]))
    spcx = [r for r in r1 if r[2] == "SPCX"]
    ck.eq("SPCX moves by the added 2,500 shares", [r[6] for r in spcx], ["2500"])
    again = revision_rows(scans, c.deals, c.listed, existing=r1)
    ck.eq("a second run over an existing file gives the same rows (regenerated, not appended)", again, r1)


def t_g12(ck):
    w = get_world()
    tmp = tempfile.mkdtemp(prefix="ipo13f_g12_")
    OPEN_LOG.clear()
    READ_LOG.clear()
    p = os.path.join(w.zdir, "01jun2026-31aug2026_form13f.zip")
    with zipfile.ZipFile(p) as zf:
        subs, rows, part = scan_zip(zf, say=lambda *a: None)
    cache = os.path.join(tmp, "cache")
    write_scan(cache, os.path.basename(p), p, subs, rows, part, "none")
    ck.ok("the signature table was never opened (runtime hook)", SIG_NAME not in OPEN_LOG, str(OPEN_LOG))
    cols = [c for _, cs in READ_LOG for c in cs]
    ck.ok("only allowlisted columns were read", all(c in ALLOWED_COL_NAMES for c in cols), str([c for c in cols if c not in ALLOWED_COL_NAMES]))
    ck.ok("no address, phone or signature column was read", not any(re.search(r"STREET|CITY|ZIPCODE|STATEORCOUNTRY|PHONE|SIGNATURE|FIGI", c) for c in cols), str(cols))
    blob = ""
    for fn in ("submissions.csv", "infotable.csv", "stamp.json"):
        blob += open(os.path.join(cache, "scan_" + zip_key(os.path.basename(p)), fn), encoding="utf-8").read()
    ck.ok("no planted address, signatory, phone or FIGI in the cache", not any(x in blob for x in (PLANT_ADDR, PLANT_SIG, PLANT_PHONE, "BBG000PLANT0")), "planted text found")
    ck.ok("the AST scan flags a literal that names the signature table", any("signature" in x for x in static_problems('zf.open("' + SIG_NAME + '")\n')), "not flagged")
    src = own_source()
    ck.eq("the source never names the signature table outside its definition", [x for x in static_problems(src) if "signature" in x], [])
    # outputs
    c, texts, wp = world_texts_checked()
    ck.eq("the build's own refusals find nothing in the clean synthetic folder", wp, [])
    alltext = "\n".join(texts.values())
    ck.ok("an unreviewed filer name is never written (Jane Q Sample, Kappa Family Office)", "Jane Q Sample" not in alltext and "Kappa Family Office" not in alltext)
    ck.ok("an i2 reporting person of type IN is not named", "Founder Person" not in alltext)
    ov0 = [r for r in c.tables["overlap_i2.csv"] if r[2].startswith("individual (withheld)")]
    ck.ok("an individual withheld in overlap_i2.csv has no share count on its row (i2_shares, sh_13f_matched, gap_sh blank)", bool(ov0) and all(r[6] == "" and r[8] == "" and r[9] == "" for r in ov0), str(ov0))
    ck.ok("the individual's typed count does not appear in overlap_i2.csv", "6418547515" not in texts["overlap_i2.csv"])
    ck.ok("an i2 holder not in the review is not named", "Unreviewed Org LLC" not in alltext)
    ck.ok("a reviewed public organisation is named", "Alpha Capital Management LLC" in alltext)
    ciks = sorted({cik_key(s.cik) for sc in c.scans for s in sc.subs})
    probs = leak_problems(texts, cusips=sorted(c.listed.values()), ciks=ciks, nonpublic_names=["Jane Q Sample", "Kappa Family Office"])
    ck.eq("the leak guard finds nothing in the clean folder", probs, [])
    ck.ok("no accession-shaped token", not ACCESSION_RX.search(alltext))
    ov = [r for r in c.tables["overlap_i2.csv"]]
    ck.ok("overlap labels are public names or numbered withheld labels", all(r[2].startswith(("withheld #", "individual (withheld) #")) or r[2] in ("Alpha Capital Management LLC", "Zeta Ventures LP", "Epsilon Hedge Partners LP", "Strategic Energy Corp") for r in ov), str([r[2] for r in ov]))


def t_g14(ck):
    bad = ("import urllib.request", "import subprocess", "from http import client", "import socket", "import requests", "import ssl", "from urllib3 import PoolManager", "import ftplib",
           "import webbrowser", "import pty", "import httpx", "import aiohttp", "os.system('x')", "os.popen('x')", "os.execv('a', ['b'])",
           "os.remove(STOP_PATH)", "os.unlink(os.path.join(zd, 'STOP'))", "os.rename(stop_file, other)", "os.replace(tmp, stop_file)", "os.truncate(stop_file, 0)", "shutil.rmtree(stop_dir)",
           "shutil.move(stop_file, o)", "shutil.copy(a, stop_file)", "shutil.copyfile(a, stop_file)", "Path(stop_file).unlink()", "Path(stop_file).rename(o)", "Path(stop_file).replace(o)",
           "Path(stop_file).touch()", "Path(stop_file).write_text('')", "open(stop_file, 'w')", "open(os.path.join(d, 'STOP'), 'a')", "open(stop_file, mode='w')")
    for snip in bad:
        ck.ok("flagged: " + snip, bool(static_problems("import os, shutil\n" + snip + "\n")), "not flagged")
    for snip in ("import json", "open(path, 'w')", "os.path.join(a, b)", "open(stop_file)", "open(stop_file, 'r')"):
        ck.eq("not flagged: " + snip, static_problems("import os\n" + snip + "\n"), [])
    ck.eq("this script's own source is clean", static_problems(own_source()), [])
    # runtime: a planted STOP latch ends scan, review and build with exit 2 and is never touched
    w = get_world()
    tmp = tempfile.mkdtemp(prefix="ipo13f_g14_")
    zd = os.path.join(tmp, "zips")
    os.makedirs(zd)
    cache = os.path.join(tmp, "cache")
    os.makedirs(cache)
    latch = os.path.join(zd, STOP_NAME)
    with open(latch, "w") as fh:
        fh.write("429\n2026-10-26T00:00:00Z\n/x\nNone\nplanted\n")
    before = sha256_path(latch)
    for mode in ("scan", "review", "build", "verify"):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = main([mode, "--zip-dir", zd, "--cache", cache] + (["--out", os.path.join(tmp, "ipo_13f_holders")] if mode == "build" else []))
        ck.eq("%s exits 2 with a STOP present" % mode, rc, 2)
        ck.ok("%s prints the STOP path" % mode, "STOP present: " + real(latch) in buf.getvalue(), buf.getvalue()[:80])
    ck.ok("the STOP file is untouched", os.path.isfile(latch) and sha256_path(latch) == before)
    rec = os.path.join(tmp, "zips2")
    os.makedirs(rec)
    recname = "STOP." + "2026-10-26T0623Z.redirect-200-not-refusal"
    with open(os.path.join(rec, recname), "w") as fh:
        fh.write("200\n")
    ck.ok("a preserved record named STOP.<date>.<note> is not the latch", stop_path(rec, None) is None)
    # paths
    root = os.path.join(tmp, "repo")
    os.makedirs(os.path.join(root, "data", "vintages", "form13f_zips"))
    write_text(os.path.join(root, ".gitignore"), "data/vintages/form13f_zips/\n")
    outside = os.path.join(tmp, "outside_cache")
    check_dirs(os.path.join(root, "data", "vintages", "form13f_zips"), outside, root)
    ck.ok("the gitignored zip folder named by round 5 is accepted", True)
    ck.raises("a cache inside the repository is refused", Refused, lambda: check_dirs(zd, os.path.join(root, "cache"), root))
    ck.raises("a zip folder inside the repository that is not the gitignored one is refused", Refused, lambda: check_dirs(os.path.join(root, "zips"), outside, root))
    write_text(os.path.join(root, ".gitignore"), "something_else/\n")
    ck.raises("the zip folder is refused when .gitignore does not name it", Refused, lambda: check_dirs(os.path.join(root, "data", "vintages", "form13f_zips"), outside, root))
    planted_path = os.path.join(tmp, STOP_NAME)
    ck.raises("write_text refuses a path named STOP", Refused, lambda: write_text(planted_path, "x"))


def t_g15(ck):
    base = README_S1 + " " + README_S2 + "\n\n" + DENIAL + " " + REST_SENTENCE + "\n\n" + HIGH_SENTENCE + "\n"
    ck.eq("the opening, the denial sentence and the two other verbatim sentences pass", wording_problems("README.md", base), [])
    for txt in ("IPO buyers piled in.", "Demand for SpaceX drove the price.", "Funds were allocated 20% of the deal.", "Retail held the rest.", "The remaining 52% is held by non-filers.",
                "Flows into the stock rose.", "Rising prices caused the change.", "That pushed holders to file.", "The listing led to more filers.", "Investors bought the stock early.", "Shares were purchased on day two.", "The stock was underpriced."):
        ck.ok("fails: " + txt, bool(wording_problems("README.md", base + txt + "\n")), "passed")
    ck.ok("a heading 'Builder decisions' fails", bool(wording_problems("README.md", base + "\n## Builder decisions\n")))
    ck.ok("a second copy of the denial sentence fails", bool(wording_problems("README.md", base + DENIAL + "\n")))
    ck.ok("a missing verbatim sentence fails", bool(wording_problems("README.md", README_S1 + "\n")))
    ck.eq("SOURCES.md is not scanned", wording_problems("SOURCES.md", "Demand drove flows; retail held the rest."), [])
    c, texts, wp = world_texts_checked()
    ck.eq("the README the build writes passes", wording_problems("README.md", texts["README.md"]), [])


def planted_folder(clean):
    bad = dict(clean)
    bad["holdings.csv"] = clean["holdings.csv"].rstrip("\n") + "\nTSTA01102,2026-06-30\n"
    bad["README.md"] = clean["README.md"] + "\nProse with 999999105 in it.\n"
    bad["SOURCES.md"] = clean["SOURCES.md"] + "\nAn ISIN ZZTESTSYN017 here.\nA FIGI BBGSYNTH0001 here.\nAn accession 0001234567-26-000123 here.\nSee /Users/someone/x.\n"
    bad["top_filers.csv"] = clean["top_filers.csv"].replace("ticker,quarter_end,rank,filer_label", "ticker,quarter_end,rank,cik,filer_label", 1)
    bad["extra.tsv"] = "raw\n"
    bad["zips.csv"] = clean["zips.csv"] + "Jane Q Sample\n"
    return bad


def t_g16(ck):
    c, clean, wp = world_texts_checked()
    ciks = sorted({cik_key(s.cik) for sc in c.scans for s in sc.subs})
    cus = sorted(c.listed.values())
    kw = dict(cusips=cus, ciks=ciks, nonpublic_names=["Jane Q Sample", "Kappa Family Office"])
    ck.eq("the build's own refusals pass the clean folder", wp, [])
    ck.eq("the clean folder passes", leak_problems(clean, **kw), [])
    t = clean["holdings.csv"].replace("\nSPCX,", "\nSPCX,", 1)
    lines = t.split("\n")
    hdr = [i for i, l in enumerate(lines) if l.startswith("ticker,")][0]
    cols = lines[hdr].split(",")
    row = lines[hdr + 1].split(",")
    row[cols.index("sh_13f")] = "171826745"
    row[cols.index("sh_calls")] = "999999105"
    lines[hdr + 1] = ",".join(row)
    shares_folder = dict(clean, **{"holdings.csv": "\n".join(lines)})
    ck.eq("share counts in sh_ columns do not trip it (171826745, and one with a valid CUSIP check digit, 999999105)", leak_problems(shares_folder, **kw), [])
    bad = planted_folder(clean)
    probs = leak_problems(bad, **kw)
    text = "\n".join(probs)
    ck.ok("a CSV cell with TSTA01102 is reported", "holdings.csv" in text and "CUSIP-shaped" in text, text[:200])
    ck.ok("README prose with 999999105 is reported", any("README.md" in p and "CUSIP-shaped" in p for p in probs), text[:200])
    ck.ok("an ISIN shape is reported", "ISIN" in text)
    ck.ok("a FIGI shape is reported", "FIGI" in text)
    ck.ok("an accession shape is reported", "accession-number" in text)
    ck.ok("a column named cik is reported", any("top_filers.csv" in p and "column named like" in p for p in probs), text[:300])
    ck.ok("a .tsv file is reported", any("extra.tsv" in p for p in probs))
    ck.ok("a /Users/ path is reported", "local path" in text)
    ck.ok("an unreviewed filer name is reported", "does not mark public" in text)
    mapped = dict(clean)
    mapped["README.md"] = clean["README.md"] + "\nThe first eight: %s.\n" % SYN_CUSIP["SPCX"][:8]
    ck.ok("a mapped identifier's first eight characters are reported", any("mapped identifier" in p for p in leak_problems(mapped, **kw)))
    cikf = dict(clean)
    cikf["README.md"] = clean["README.md"] + "\nFiler %s reported.\n" % ciks[0]
    ck.ok("a filer number from the cache is reported", any("filer number" in p for p in leak_problems(cikf, **kw)))
    ck.ok("a missing file is reported", any("missing" in p for p in leak_problems({k: v for k, v in clean.items() if k != "README.md"}, require_all=True)))


def t_g17(ck):
    ck.eq("801- -> ria_801", reg_category("801-12345"), "ria_801")
    ck.eq("802- -> era_802", reg_category("802-1"), "era_802")
    ck.eq("8- -> bd_8", reg_category("8-45678"), "bd_8")
    ck.eq("another prefix", reg_category("028-12345"), "other_prefix")
    ck.eq("blank -> none", reg_category(""), "none")
    ck.eq("8- is not matched before 801- (80 is not a prefix)", reg_category("801-9"), "ria_801")
    c = world_compute()
    ck.ok("reg_category.csv is written when the readme defines the column", len(c.tables["reg_category.csv"]) > 0)
    c2 = world_compute(cfg=dict(get_world().cfg, secfile_is_regulatory=False))
    ck.eq("reg_category.csv is not written when the readme flag says the column is not the regulatory file number", len(c2.tables["reg_category.csv"]), 0)


def t_x_pipeline(ck):
    """The whole path on synthetic data: the world's pins, identities and gates."""
    c, texts = world_texts()
    st = {r[0]: r[4] for r in c.checks}
    for cid in ("C01a", "C01b", "C01c", "C01d", "C03a", "C03b", "C06", "C11", "C12", "C13", "C14", "C16"):
        ck.eq("%s passes on the synthetic world" % cid, st.get(cid), "PASS")
    for r in c.checks:
        if r[0].startswith("C02-r"):
            ck.eq("%s passes" % r[0], r[4], "PASS")
    ck.eq("C20 is INFO", st["C20"], "INFO")
    ck.eq("five measured, three awaiting", (len(c.measured), len(c.awaiting)), (5, 3))
    ck.eq("BSP priced on the quarter-end day waits for the next zip", [d["status"] for d in c.deals if d["ticker"] == "BSP"], ["awaiting_next_zip"])
    ck.eq("every file has the thirteen CSV headers or is README or SOURCES", sorted(texts), sorted(COMMITTED_NAMES))
    ck.eq("no problem in the clean folder", all_problems(texts, c), [])
    ck.eq("two renders are identical", render_texts(c, get_world().deal_text), texts)
    h = collections.OrderedDict((n, body_lines(t)[0]) for n, t in texts.items() if n.endswith(".csv"))
    allow = dict(l.split(":", 1) for l in ALLOW_TEXT.strip().split("\n"))
    ck.eq("every header is its allowlist line", dict(h), dict(allow))
    ck.ok("every CSV except deal_inputs and checks begins with a source line", all(t.startswith("# source:") for n, t in texts.items() if n.endswith(".csv") and n not in ("deal_inputs.csv", "checks.csv")))
    ck.ok("no CSV has a duplicate key", not [p for n, t in texts.items() for p in duplicate_key_problems(n, t)])
    # a renamed or extra column is refused
    renamed = dict(texts, **{"holdings.csv": texts["holdings.csv"].replace("n_filers", "n_filer", 1)})
    ck.ok("a renamed column is refused", bool(leak_problems(renamed, require_all=True)))
    extra = dict(texts, **{"holdings.csv": texts["holdings.csv"].replace("vintage\n", "vintage,extra\n", 1)})
    ck.ok("an extra column is refused", bool(leak_problems(extra, require_all=True)))
    ck.ok("the allowlist text hashes to its pin", not allow_problems())
    ck.eq("the allowlist is 1,958 bytes", len(ALLOW_TEXT.encode("utf-8")), 1958)
    ck.eq("the three constants are unset in this source until the supervisor sets them (a build refuses)", [bool(CUSIP_MAP_SHA256), bool(FILER_REVIEW_SHA256), bool(DEAL_INPUTS_SHA256)].count(True) in (0, 3), True)


GUARDS = (
    ("G1", "amendments (3.4)", ["g1_restatement_summed_with_original", "g1_new_holdings_dropped", "g1_older_restatement_wins", "g1_new_holdings_before_restatement_kept", "g1_two_originals_counted",
                                "g1_stale_restatement_wins", "g1_orphan_dropped", "g1_orphan_not_listed", "g1_duplicate_counted_twice", "g1_repeat_cusip_not_flagged", "g1_unknown_amendtype_accepted"], t_g1),
    ("G2", "numerator (3.5)", ["g2_option_as_shares", "g2_prn_counted", "g2_name_match_added", "g2_other_period_counted", "g2_blank_value_dropped_from_shares", "g2_blank_value_in_price",
                               "g2_sole_gt_total", "g2_shares_float", "g2_option_id_in_sh13f", "g2_option_id_ignored"], t_g2),
    ("G3", "CUSIP (3.1-3.2)", ["g3_no_normalise", "g3_pad8", "g3_accept_bad_check", "g3_name_match_without_map", "g3_stale_stamp_accepted", "g3_nonmatching_name_not_listed"], t_g3),
    ("G4", "signs and units (2.2)", ["g4_negative_accepted", "g4_value_thousands", "g4_value_thousands_readme", "g4_puts_subtracted", "g4_outlier_not_listed", "g4_outlier_tol_2pct",
                                     "g4_median_bounds_ignored"], t_g4),
    ("G5", "quarter-ends (2.1)", ["g5_qe_on_day", "g5_first_trade_instead", "g5_due_no_roll"], t_g5),
    ("G6", "dates (R9)", ["g6_locale_months", "g6_day_first_misread", "g6_wallclock_vintage", "g6_wallclock_source", "g6_vintage_not_newest"], t_g6),
    ("G7", "denominators (2.3)", ["g7_prosp_for_primary", "g7_blank_filled_prosp", "g7_blank_as_zero", "g7_cover_over_balance", "g7_all_classes_as_listed", "g7_pct_vs_prosp_at_use", "g7_class_from_13dg_pct",
                                  "g7_build_hash_mismatch_accepted"], t_g7),
    ("G8", "pooled and weights (3.8)", ["g8_inio_weight", "g8_blank_in_pooled", "g8_weights_rounded", "g8_exspcx_includes_spcx", "g8_no_median"], t_g8),
    ("G9", "identities (3.9, C16)", ["g9_reg_not_sum", "g9_top10_lt_top1", "g9_unstable_ties"], t_g9),
    ("G10", "duplicates (C09)", ["g10_dup_not_flagged"], t_g10),
    ("G11", "cross-zip (C11)", ["g11_dup_accession_accepted", "g11_revisions_appended"], t_g11),
    ("G12", "personal data (R3, R5)", ["g12_open_signature", "g12_read_address", "g12_ast_scan_skip", "g12_unreviewed_name_written", "g12_cik_written", "g12_accession_written", "g12_in_named", "g12_individual_shares_shown",
                                       "g12_i2_label_unreviewed"], t_g12),
    ("G14", "network, STOP, paths (R1-R2)", ["g14_scan_off", "g14_stop_ignored", "g14_cache_in_repo_accepted", "g14_zipdir_in_repo_accepted"], t_g14),
    ("G15", "wording (R6)", ["g15_off", "g15_causal_off", "g15_extra_off", "g15_residual_off", "g15_heading_ok", "g15_denial_twice_ok"], t_g15),
    ("G16", "leak guard (6)", ["g16_skip_cusip", "g16_skip_cusip_cache", "g16_skip_isin", "g16_skip_figi", "g16_skip_accession", "g16_skip_cikcol", "g16_skip_tsv", "g16_skip_path",
                              "g16_skip_name", "g16_skip_cik_cache", "g16_flag_shares"], t_g16),
    ("G17", "registration number (2.4)", ["g17_8_before_801", "g17_regcat_when_flag_false"], t_g17),
    ("X", "synthetic pipeline: pins, identities, gates, headers", [], t_x_pipeline),
)


def run_test(fn):
    ck = Checks()
    try:
        fn(ck)
    except Exception as e:                      # a test that crashes under a mutant has noticed it
        ck.ok("test ran to completion", False, "%s: %s" % (type(e).__name__, e))
    return ck


def selftest(mutants=True, only=None):
    t0 = time.time()
    get_world()                                  # built first, with no mutant active
    bad_total, n_checks, n_mut = 0, 0, 0
    if only:
        names = {m for _, _, ms, _ in GUARDS for m in ms}
        if only not in names:
            print("unknown mutant %r" % only)
            return 2
        with mutant(only):
            for gid, desc, muts, fn in GUARDS:
                if only not in muts:
                    continue
                ck = run_test(fn)
                bad = ck.failed()
                print("%-4s %s: %d checks, %s" % (gid, desc, len(ck.items), "FAILED (%d)" % len(bad) if bad else "ok"))
                for name, detail in bad[:3]:
                    print("       FAIL  %s   <- %s" % (name, detail[:140]))
                bad_total += len(bad)
        print("selftest with mutant %s: %d failing check(s) -> %s" % (only, bad_total, "the selftest FAILS (mutant caught)" if bad_total else "the selftest PASSES (mutant NOT caught)"))
        return 1 if bad_total else 0
    for gid, desc, muts, fn in GUARDS:
        ck = run_test(fn)
        n_checks += len(ck.items)
        bad = ck.failed()
        bad_total += len(bad)
        print("%-4s %s: %d checks, %s" % (gid, desc, len(ck.items), "ok" if not bad else "FAILED"))
        for name, detail in bad:
            print("       FAIL  %s   <- %s" % (name, detail[:200]))
        if mutants:
            for m in muts:
                with mutant(m):
                    mk = run_test(fn)
                caught = bool(mk.failed())
                n_mut += 1
                bad_total += 0 if caught else 1
                print("       mutant %-40s %s%s" % (m, "caught" if caught else "NOT CAUGHT", "  (first failing check: %s)" % mk.failed()[0][0][:70] if caught else ""))
    print("selftest: %d guards, %d checks, %d mutants applied one at a time, %d failure(s), %.1f s" % (len(GUARDS), n_checks, n_mut, bad_total, time.time() - t0))
    return 0 if bad_total == 0 else 1


def write_fixture(dest):
    """The clean synthetic output folder, for showing that bin/check.sh M24 passes on it and fires on a planted copy."""
    c, texts = world_texts()
    for name, text in texts.items():
        write_text(os.path.join(dest, name), text)
    print("wrote %d files to %s" % (len(texts), dest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
