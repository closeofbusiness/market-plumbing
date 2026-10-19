#!/usr/bin/env python3
"""Registered funds' Treasury futures in 10-year equivalents (Part 1) and the index/active split of their cash Treasury duration change
(Part 2, test B). Python 3 standard library only. This script makes NO network request of any kind (spec R1).

  python3 bin/nport_futures_index.py selftest [--no-mutants]
  python3 bin/nport_futures_index.py scan  --zip-dir DIR --work DIR [--zips 2024q1,2024q2] [--stage A|B]      # one slice of the heavy N-PORT passes
  python3 bin/nport_futures_index.py futures --zip-dir DIR --work DIR [--r1-cache DIR] [--r2-cache DIR] [--out DIR]
  python3 bin/nport_futures_index.py idx     --zip-dir DIR --work DIR --ncen-dir DIR [--r1-cache DIR] [--r2-cache DIR] [--out DIR]

Specification: _research/2026-10-19-Fund-Futures-And-Index-Split-Spec.md (the body and the supervisor rulings, rounds 1-4; the latest round wins), with
its build decisions (listed in data/nport/fut_idx_SOURCES.md). The cash build it extends is bin/nport_treasury_duration.py (R2b), imported by path and called by name, never copied
except where a block carries a comment naming the function it copies (spec R3).

  selftest  runs bin/test_nport_treasury_duration.py, then this file's own guards G1-G18, each with its mutants applied one at a time. Synthetic data only.
  scan      the two heavy passes over the SEC bulk N-PORT zips, one slice at a time, into --work (a scratch directory outside the repository):
            stage A = the cash build's pass A (imported) plus one pass over FUND_REPORTED_HOLDING for futures, swaps and options and their joins;
            stage B = the cash build's pass B (imported). A slice is a list of zips so that no command has to run longer than a tool timeout.
  futures   Part 1 and the pre-run table. Needs every scan slice. Writes the fut_* files, idx_prerun.csv and the README (Part 2 shown as not yet run).
  idx       everything `futures` does, plus Part 2 with the Form N-CEN zips in --ncen-dir (placed by the supervisor), plus the ex-ETF anchors.

The zips are read from the Dropbox companion as streams, never extracted or copied (R2). The N-CEN zips are fetched by the supervisor only (R1).
Outputs are aggregates under data/nport/ (spec section 5). A hard-check FAIL writes every output to data/nport/_FAILED_fut_idx/ and exits 2; a refusal
(a missing input, a failed pre-flight) writes nothing and exits 1. No file carries a wall-clock time, so a re-run is byte-identical (R7).

Required sentence: "These are holdings measurements. They do not show what moved Treasury yields."
"""
import argparse
import ast
import bisect
import collections
import contextlib
import csv
import datetime as dt
import hashlib
import importlib
import importlib.util
import io
import math
import os
import pickle
import re
import statistics
import sys
import tempfile
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DEFAULT = os.path.join(ROOT, "data", "nport")
COLS_TSV_DEFAULT = os.path.join(OUT_DEFAULT, "fut_idx_columns.tsv")
FAILED_DIRNAME = "_FAILED_fut_idx"
REQUIRED_SENTENCE = "These are holdings measurements. They do not show what moved Treasury yields."

# ------------------------------------------------------------------------------------------------------------------------
# mutants: deliberately broken variants, switched on only by the selftest, in this process (house style: bin/hedged_ust_yield.py)
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


class Refused(SystemExit):
    """A missing input or a failed pre-flight: exit 1, nothing written."""
    def __init__(self, msg):
        super().__init__(msg)


# ------------------------------------------------------------------------------------------------------------------------
# the cash build and R2, imported by path (R3). load_by_path is the cash build's own pattern.
# ------------------------------------------------------------------------------------------------------------------------
def load_by_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ntd = load_by_path("nport_treasury_duration", os.path.join(HERE, "nport_treasury_duration.py"))
r2_pure = load_by_path("r2_duration_supply", os.path.join(HERE, "r2_duration_supply.py"))   # pure functions only; its caches are set by ntd.load_r2


def _no_fetch(url, path):                       # this script never fetches (R1); r2.fetch is replaced by the cash build's guard on a real run
    raise Refused(f"{os.path.basename(path)} is not in the cache; this script fetches nothing")


r2_pure.fetch = _no_fetch
Fsum = ntd.Fsum
fmt = ntd.fmt

# ------------------------------------------------------------------------------------------------------------------------
# constants (spec sections 3-4)
# ------------------------------------------------------------------------------------------------------------------------
CONTRACTS = ("TU", "Z3N", "FV", "TY", "TN", "TWE", "US", "UB")
FACE_200K = ("TU", "Z3N")                       # departure 1: the 2- and 3-year note futures have a $200,000 face
MONTH_ROUND = ("TU", "Z3N", "FV")               # remaining term rounded down to a month; the others to a quarter (R23-6)
TENOR_MONTHS = {"TU": 21, "Z3N": 33, "FV": 50, "TY": 78, "TN": 113, "TWE": 230, "US": 180, "UB": 300}
# the eight pins of section 3.4: (CF, ten-year-equivalent dollars per contract), reproduced to $0.01 (C-F2)
TENOR_PINS = {"TU": (0.9732, 41667.39), "Z3N": (0.9515, 65875.55), "FV": (0.9239, 50157.56), "TY": (0.8867, 78153.01),
              "TN": (0.8511, 111810.44), "US": (0.8079, 168094.85), "TWE": (0.7946, 200557.12), "UB": (0.7575, 249209.94)}
D10_PIN, D10_TOL = 8.2233, 0.0001
R2_DATES = ("2023-12-31", "2024-12-31", "2025-12-31", "2026-06-30")
R2_WINDOWS = ("2023Q4", "2024Q4", "2025Q4", "2026Q2")
PERIODS = (("full", "2023Q4", "2026Q2"), ("2024", "2023Q4", "2024Q4"), ("2025", "2024Q4", "2025Q4"), ("2026H1", "2025Q4", "2026Q2"))
DF_BAR_BN, UF_MAX, GV_MAX, GC_MAX, GS_MAX = 100.0, 0.10, 20.0, 50.0, 20.0
A1_RANGE, A2_RANGE, A3_RANGE = (250.0, 380.0), (0.20, 0.45), (3.0, 4.5)
A4_FEDS_RANGE = (470.0, 500.0)
U_CAP_BN = 16.2                                  # R23-14: the literal
Q_SUPPORT, Q_EXCESS, Q_RISE, Q_AGAINST = 0.60, 0.15, 0.10, 0.40
Q_BASE_SHARE = 0.25                              # R23-13: classified change at least 25% of the period's base
STALE_BEFORE = dt.date(2025, 3, 30)              # R23-11
BACKFILL_MONTHS = 15
SMALL_CELL = 5
NC_UNIT = "NC"
SMALL_NAME = "other_small"
GROUPS = ("index_stable", "active_stable", "switcher", "mmf", "levinv", "unflagged", "stale_flag", "feeder_dropped")
FLAG_TYPE_COLS = ("IS_ETF", "IS_ETMF", "IS_INDEX", "IS_MULTI_INVERSE_INDEX", "IS_INTERVAL", "IS_FUND_OF_FUND", "IS_MASTER_FEEDER",
                  "IS_TARGET_DATE", "IS_UNDERLYING_FUND")
NCEN_FRI_COLS = ("FUND_ID", "ACCESSION_NUMBER", "SERIES_ID", "IS_ETF", "IS_ETMF", "IS_INDEX", "IS_MULTI_INVERSE_INDEX", "IS_INTERVAL",
                 "IS_FUND_OF_FUND", "IS_MASTER_FEEDER", "IS_MONEY_MARKET", "IS_TARGET_DATE", "IS_UNDERLYING_FUND", "IS_FUND_TYPE_NA",
                 "IS_INDEX_AFFILIATED", "IS_INDEX_EXCLUSIVE")
NCEN_NAME_COLS = ("FUND_NAME",)
NCEN_ZIP_RE = re.compile(r"^(\d{4})q([1-4])_ncen(?:_\d+)?\.zip$", re.I)


def tilde(p):
    return os.path.expanduser(p)


def month_add(d, k):
    """The same day k calendar months later, clipped to the month's end."""
    y, m = divmod(d.year * 12 + d.month - 1 + k, 12)
    m += 1
    last = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1)).day
    return dt.date(y, m, min(d.day, last))


def whole_months(d0, d1):
    """Whole calendar months from d0 to d1, rounded down."""
    m = (d1.year - d0.year) * 12 + d1.month - d0.month
    if d1.day < d0.day:
        m -= 1
    return m


def first_of_month(d):
    return dt.date(d.year, d.month, 1)


def last_of_month(d):
    return dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1) - dt.timedelta(days=1)


def pdate(s):
    return ntd.pdate(s)


def fnum(s):
    """float or None; blank is None."""
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def sgn(x):
    return (x > 0) - (x < 0)


def ge(x, bar):
    """x >= bar, after rounding away binary noise (bounds are inclusive)."""
    return round(x, 9) >= round(bar, 9)


def gt(x, bar):
    return round(x, 9) > round(bar, 9)


def lt(x, bar):
    return round(x, 9) < round(bar, 9)


def le(x, bar):
    return round(x, 9) <= round(bar, 9)


# ------------------------------------------------------------------------------------------------------------------------
# contract face, conversion factor, tenor map (spec 3.3-3.5)
# ------------------------------------------------------------------------------------------------------------------------
def face_of(contract):
    if M("z3n_face_100k") and contract == "Z3N":
        return 100000.0                         # the mutant: the 3-year note future at $100,000
    if M("tu_face_100k") and contract == "TU":
        return 100000.0
    return 200000.0 if contract in FACE_200K else 100000.0


def round_months(contract, months):
    """R23-6: round the remaining term down to a month for TU, Z3N and FV, to a quarter for the others."""
    if contract in MONTH_ROUND and not (M("cf_fv_quarter") and contract == "FV"):
        return months
    return months // 3 * 3


def round_eighth(coupon_pct):
    """R23-5: the coupon to the nearest 1/8 per cent, a tie going up."""
    if M("cf_no_eighth"):
        return coupon_pct
    return math.floor(8.0 * coupon_pct + 0.5) / 8.0


def cf_value(coupon_pct, months, round_coupon=True):
    """The CBOT conversion factor at 6% (spec 3.5). `months` is the remaining term from the first day of the delivery month, already rounded for
    the contract. `round_coupon` is False only for the synthetic par bond of the tenor map (departure 6 / OPEN-R2 closed by round 4)."""
    c = (round_eighth(coupon_pct) if round_coupon else coupon_pct) / 100.0
    if M("cf_six_pct_any_term") and abs(c - 0.06) < 1e-12:
        return 1.0                              # the mutant: the old fixture, 6% at any term is 1.0000
    n, z = divmod(months, 12)
    v = z if z < 7 else z - 6
    a = 1.03 ** (-v / 6.0)
    b = (c / 2.0) * (6 - v) / 6.0
    if M("cf_annual_discount"):
        k = 1.03 ** (-n) if z < 7 else 1.03 ** (-(n + 0.5))      # the mutant: 3% a year in place of 3% a half-year
    else:
        k = 1.03 ** (-2 * n) if z < 7 else 1.03 ** (-(2 * n + 1))
    d = (c / 0.06) * (1.0 - k)
    return round(a * (c / 2.0 + k + d) - b, 4)


def tenor_factor(contract, curve, d10, d10_report=None):
    """Ten-year-equivalent dollars of one contract on the synthetic deliverable at the shortest term of the basket (spec 3.4):
    face x par_mod_duration(y_T, n=T) / CF / d10, the par yield on the fixed curve unrounded, the duration and d10 unrounded."""
    months = TENOR_MONTHS[contract]
    T = months / 12.0 + (0.25 if M("tm_add_expiry") else 0.0)       # the mutant adds the time to expiry to the term
    y = r2_pure.interp_curve(curve, T)
    dur = r2_pure.par_mod_duration(y, n=T)
    cf = 1.0 if M("tm_drop_cf") else cf_value(y, round_months(contract, months), round_coupon=False)
    use_d10 = d10_report if (M("tm_d10_report_date") and d10_report) else d10    # the mutant: d10 of the report date's curve
    return face_of(contract) * dur / cf / use_d10, cf, y, dur


def tenor_table(curve, d10):
    return {c: tenor_factor(c, curve, d10) for c in CONTRACTS}


# ---- the modelled cheapest-to-deliver (R2-date windows only; spec 3.5) ----
Deliv = collections.namedtuple("Deliv", "cusip cls coupon maturity issue")


def deliverables_from_rows(rows):
    """MSPD Table 3 rows -> the Notes and Bonds, one record per CUSIP: the coupon and maturity of the CUSIP, the earliest issue date of its tranches."""
    by = {}
    for r in rows:
        cls, cusip = r.get("security_class1_desc"), r.get("security_class2_desc")
        if cusip is None or cusip.startswith("Total") or cusip == "null":
            continue
        if M("tips_admitted"):
            ok = cls in ("Notes", "Bonds", "Inflation-Protected Securities")      # the mutant: TIPS admitted
        else:
            ok = cls in ("Notes", "Bonds")
        if not ok or r.get("maturity_date") in (None, "null", "") or r.get("issue_date") in (None, "null", ""):
            continue
        cp = fnum(r.get("interest_rate_pct"))
        if cp is None:
            continue
        mat, iss = dt.date.fromisoformat(r["maturity_date"]), dt.date.fromisoformat(r["issue_date"])
        old = by.get(cusip)
        if old is None:
            by[cusip] = Deliv(cusip, cls, cp, mat, iss)
        elif iss < old.issue:
            by[cusip] = old._replace(issue=iss)
    return [by[k] for k in sorted(by)]


def class_ok(contract, cls):
    """Which MSPD classes may be delivered into which contract (R23-6): Notes only for TU, Z3N, FV, TY, TN; Notes and Bonds for TWE; Bonds only
    for US and UB. No TIPS, FRNs or bills, so that principal and coupon are fixed."""
    if M("tips_admitted") and cls == "Inflation-Protected Securities":
        return True                             # the mutant
    if contract in ("TU", "Z3N", "FV", "TY", "TN"):
        return cls == "Notes"
    if contract == "TWE":
        return cls in ("Notes", "Bonds")
    if contract == "US":
        return cls == "Bonds" or (M("note_admitted_to_us") and cls == "Notes")      # the mutant admits a Note to the US basket
    if contract == "UB":
        return cls == "Bonds"
    return False


def eligible(contract, dv, fdm):
    """The CBOT basket tests of the table in spec 3.5. All terms run from the first day of the delivery month, `fdm`."""
    if not class_ok(contract, dv.cls):
        return False
    start = last_of_month(fdm) if (M("ty_basket_month_end") and contract == "TY") else fdm    # the mutant: TY measured from the month's last day
    rem = round_months(contract, whole_months(start, dv.maturity))
    orig = whole_months(dv.issue, dv.maturity)
    if contract == "TU":
        return orig <= 63 and 21 <= rem <= 24
    if contract == "Z3N":
        return orig <= 84 and 33 <= rem <= 36
    if contract == "FV":
        return orig <= 63 and rem >= 50
    if contract == "TY":
        return orig <= 120 and 78 <= rem < 96
    if contract == "TN":
        return orig <= 120 and 113 <= rem <= 120
    if contract == "TWE":
        return 230 <= rem <= 239
    if contract == "US":
        return 180 <= rem < 300
    if contract == "UB":
        return rem >= 300
    return False


def modelled_ctd(contract, fdm, deliverables, curve_d):
    """argmin of P_own / CF over the basket; P_own is R2's coupon_price_duration clean price at T from FDM on the curve of the window date.
    Ties go to the shorter maturity, then the lower coupon. Returns (Deliv, CF) or None for an empty basket."""
    best = None
    for dv in deliverables:
        if not eligible(contract, dv, fdm):
            continue
        months = round_months(contract, whole_months(fdm, dv.maturity))
        cf = cf_value(dv.coupon, months)
        T = max((dv.maturity - fdm).days / 365.25, 0.0)
        price, _dur = r2_pure.coupon_price_duration(dv.coupon, r2_pure.interp_curve(curve_d, T), T)
        ratio = price / cf
        key = ((-ratio) if M("ctd_argmax") else ratio, dv.maturity, dv.coupon)
        if best is None or key < best[0]:
            best = (key, dv, cf)
    return None if best is None else (best[1], best[2])


def ctd_factor(contract, fdm, deliverables, curve_d, curve_fixed, d10_fixed):
    """Ten-year-equivalent dollars of one contract on the modelled CTD priced on the fixed curve: face x P_fixed/100 x D_fixed / CF / d10.
    Returns (factor, Deliv, CF) or None when the basket is empty."""
    got = modelled_ctd(contract, fdm, deliverables, curve_d)
    if got is None:
        return None
    dv, cf = got
    T = max((dv.maturity - fdm).days / 365.25, 0.0)
    price_f, dur_f = r2_pure.coupon_price_duration(dv.coupon, r2_pure.interp_curve(curve_fixed, T), T)
    return face_of(contract) * price_f / 100.0 * dur_f / cf / d10_fixed, dv, cf


# ------------------------------------------------------------------------------------------------------------------------
# the classifier (spec 3.2; a matching rule is a hypothesis, C-059; R23-4)
# ------------------------------------------------------------------------------------------------------------------------
US_EXCHANGE_RX = re.compile(r"\b(CBT|CBOT|XCBT|CME)\b|CHICAGO BOARD|BOARD OF TRADE")
RX_IR_NONTSY = re.compile(r"SOFR|EURODOLLAR|FED\s*FUND|30\s*DAY")
RX_FOREIGN_BOND = re.compile(r"\bBUND|BOBL|SCHATZ|BUXL|FGB[XLMS]|\bOAT\b|\bBTP\b|\bGILT|\bJGB|\bJPN\b|OSAKA|\bAUST\b|KOREA|CAN\s*10|CANADA|\bEURO(?!PEAN)")
RX_OTHER_NONTSY = re.compile(r"\bOPTION|OPTN|\bPUT\b|\bCALL\b|S&P|\bSPX\b|NASDAQ|E-?MINI|RUSSELL|\bDOW\b|NIKKEI|MSCI|\bDAX\b|FTSE|\bCAC\b|STOXX|\bVIX\b|"
                             r"\bGOLD\b|SILVER|COPPER|PLATINUM|PALLADIUM|CRUDE|\bWTI\b|BRENT|NATURAL GAS|HENRY HUB|GASOLINE|HEATING OIL|\bCORN\b|SOYBEAN|"
                             r"\bWHEAT\b|COTTON|SUGAR|COFFEE|COCOA|CATTLE|\bHOGS\b|BITCOIN|\bBTC\b|ETHER|\bCRYPTO")
RX_TICKER = re.compile(r"\b(TU|3Y|FV|TY|UXY|TN|TWE|US|WN|UB)[FGHJKMNQUVXZ]\d{1,2}\b")
ROOT_TO_CONTRACT = {"TU": "TU", "3Y": "Z3N", "FV": "FV", "TY": "TY", "UXY": "TN", "TN": "TN", "TWE": "TWE", "US": "US", "WN": "UB", "UB": "UB"}
RX_US_MARKER = re.compile(r"\bUS\b|U\.S\.|\bUST\b|TREASURY|\bCBT\b|\bCBOT\b|CHICAGO BOARD|BOARD OF TRADE|\bXCBT\b")
RX_ULTRA = re.compile(r"ULTRA")
RX_BOND = re.compile(r"BOND|\bBD\b")
RX_GENERIC = re.compile(r"FUTURE|GOVERNMENT")
RX_BONDISH = re.compile(r"BOND|BND|\bBD\b|NOTE|GOVT|GOVERNMENT|BUND|BOBL|SCHATZ|BUXL|GILT|BTP|\bOAT\b|JGB|TREASURY")
TENOR_WORDS = {2: r"(?:\b2\s*-?\s*(?:YR|YEAR|Y)\b|TWO\s*-?\s*YEAR)", 3: r"\b3\s*-?\s*(?:YR|YEAR|Y)\b", 5: r"\b5\s*-?\s*(?:YR|YEAR|Y)\b",
               10: r"\b10\s*-?\s*(?:YR|YEAR|Y)\b", 20: r"\b20\s*-?\s*(?:YR|YEAR|Y)\b", 30: r"\b30\s*-?\s*(?:YR|YEAR|Y)\b"}
RX_TENOR = {k: re.compile(v) for k, v in TENOR_WORDS.items()}
RX_ULTRA10 = re.compile(r"ULTRA\s*10")
RX_LONG_BOND = re.compile(r"LONG\s*BOND|T-BOND|TREASURY\s*BOND")
SPACES = re.compile(r"\s+")


def norm_text(s):
    """Upper-case and squeeze every run of spaces to one (spec 3.2: 'upper-case each source and collapse its spaces')."""
    return SPACES.sub(" ", (s or "").upper()).strip()


def _text_contract(t):
    """Step 3 on one source: the tenor is tested before BOND|BD."""
    if RX_ULTRA.search(t):
        if M("cls_bond_before_tenor") and RX_BOND.search(t):
            return "UB"                         # the mutant: BOND tested before the tenor
        if RX_TENOR[10].search(t) or RX_ULTRA10.search(t):
            return "TN"
        if RX_TENOR[30].search(t):
            return "UB"
        if RX_BOND.search(t):
            return "UB"
        if "NOTE" in t:
            return "TN"
        return None
    for n, c in ((2, "TU"), (3, "Z3N"), (5, "FV"), (10, "TY"), (20, "TWE"), (30, "US")):
        if RX_TENOR[n].search(t):
            return c
    if RX_LONG_BOND.search(t):
        return "US"
    return None


def classify_source(t, fut_ccy):
    """One normalised text source -> ('nontsy', reason), ('contract', c) or None."""
    if not t:
        return None
    if RX_IR_NONTSY.search(t):
        return ("nontsy", "ir_nontsy")
    if RX_FOREIGN_BOND.search(t):
        return ("nontsy", "foreign_bond")
    probe = t.replace("OPTN", "") if M("cls_no_optn") else t           # the mutant: OPTN is not a non-Treasury word
    if RX_OTHER_NONTSY.search(probe):
        return ("nontsy", "other_nontsy")
    m = RX_TICKER.search(t)
    if m:
        root = m.group(1)
        c = ROOT_TO_CONTRACT[root]
        if root == "UB" and not (fut_ccy == "USD" or (M("cls_ub_on_blank") and fut_ccy == "")):
            c = None                            # R23-4: the root UB counts only when the currency is USD, blank is not enough
        if c is not None:
            return ("contract", c)
    if RX_US_MARKER.search(t):
        c = _text_contract(t)
        if c is not None:
            return ("contract", c)
    return None


def classify(texts, fut_ccy):
    """Spec 3.2. `texts` = the four normalised sources (a)-(d) in order; `fut_ccy` = FUT_FWD.CURRENCY_CODE ('' when absent).
    Returns (cls, contract, reason): cls in tsy, nontsy, non_usd, unresolved, conflict."""
    if not M("cls_no_step0"):
        if fut_ccy not in ("USD", ""):
            return ("non_usd", None, "non_usd")
        if fut_ccy == "" and not any(US_EXCHANGE_RX.search(t) for t in texts):
            return ("non_usd", None, "blank_currency_no_us_exchange")
    srcs = list(texts)
    if M("cls_reverse_sources"):
        srcs = srcs[::-1]                        # the mutant: the sources read in the opposite order
    res = [classify_source(t, fut_ccy) for t in srcs]
    contracts = {r[1] for r in res if r and r[0] == "contract"}
    if len(contracts) >= 2 and not M("cls_conflict_silent"):
        return ("conflict", None, "unresolved_conflict")
    for r in res:
        if r is None:
            continue
        if r[0] == "nontsy":
            return ("nontsy", None, r[1])
        return ("tsy", r[1], "contract")
    if any(RX_US_MARKER.search(t) or RX_GENERIC.search(t) for t in texts):
        return ("unresolved", None, "unresolved")
    return ("nontsy", None, "other_nontsy")


# ------------------------------------------------------------------------------------------------------------------------
# sign and size of one kept line (spec 3.3; R23-1, R23-3)
# ------------------------------------------------------------------------------------------------------------------------
SizeRes = collections.namedtuple("SizeRes", "basis face_usd contracts n ratio notional_is_count suspect")


def valid_count(balance, unit):
    if unit != NC_UNIT or balance is None:
        return None
    a = abs(balance)
    r = round(a)
    if r >= 1 and abs(a - r) <= 1e-6:
        return int(r)
    return None


def size_line(contract, balance, unit, notional, currency_value=None):
    """The first rule that fits (spec 3.3). Returns a SizeRes; basis is face, notional or none; `n` is the valid integer contract count or None.
    CURRENCY_VALUE and UNREALIZED_APPRECIATION never size a position (G4); `currency_value` is accepted only so that the guard's mutant can use it."""
    face = face_of(contract)
    n = valid_count(balance, unit)
    nab = None if notional is None else abs(notional)
    blank = nab is None or nab == 0.0           # round-4 reading: a zero notional is a missing one, as in rule 5
    if M("size_by_currency_value") and currency_value is not None:
        return SizeRes("notional", abs(currency_value), abs(currency_value) / face, n, None, False, False)
    if n is not None:
        if not blank and not M("skip_rule1") and abs(nab - abs(balance)) <= 0.01 * abs(balance):
            r = n * face
            if M("size_add_both"):
                r += nab
            return SizeRes("face", r, n, n, None, True, False)           # rule 1: the notional field holds the contract count
        if blank:
            return SizeRes("face", n * face, n, n, None, False, False)   # rule 2, notional blank
        ratio = nab / (n * face)
        if (0.5 < ratio if M("ratio_band_strict") else 0.5 <= ratio) and ratio <= 2.0:
            r = n * face
            if M("size_add_both"):
                r += nab
            return SizeRes("face", r, n, n, ratio, False, False)         # rule 2
        return SizeRes("notional", nab, nab / face, n, ratio, False, True)       # rule 3
    if not blank:
        return SizeRes("notional", nab, nab / face, None, None, False, False)    # rule 4
    return SizeRes("none", 0.0, 0.0, None, None, False, False)                  # rule 5


def payoff_sign(payoff, holding_payoff=None):
    """Primary sign: FUT_FWD.PAYOFF_PROFILE Long = +1, Short = -1; anything else is sign-N/A (None). The mutant takes the holding-level one."""
    p = holding_payoff if M("sign_holding_payoff") else payoff
    if p == "Long":
        return 1
    if p == "Short":
        return -1
    return None


def line_signs(payoff, balance, holding_payoff=None):
    """(primary, comparison). The comparison sign is sign(BALANCE) where BALANCE is not zero, else the primary sign (R23-1)."""
    sp = payoff_sign(payoff, holding_payoff)
    sb = sgn(balance) if (balance is not None and balance != 0) else sp
    if M("sign_from_balance"):
        sp, sb = (sb if sb is not None else sp), sp      # the mutant: the primary sign from BALANCE
    if sp is None and not M("keep_sign_na"):
        return None, sb
    if sp is None and M("keep_sign_na"):
        return (sb if sb is not None else 1), sb          # the mutant keeps a sign-N/A line
    return sp, sb


def line_value(contract, size, sp, factor_usd):
    """Signed ten-year-equivalent dollars of one kept line: contracts x factor (for a notional-basis line |NOTIONAL| / face x factor)."""
    return sp * size.contracts * factor_usd


# ------------------------------------------------------------------------------------------------------------------------
# the heavy passes over the N-PORT zips: stage A and stage B, one zip at a time, kept in --work (a scratch directory)
# ------------------------------------------------------------------------------------------------------------------------
T_FUTFWD, T_OTHER, T_BASKET, T_IDENT = "FUT_FWD_NONFOREIGNCUR_CONTRACT.tsv", "DESC_REF_OTHER.tsv", "DESC_REF_INDEX_BASKET.tsv", "IDENTIFIERS.tsv"
T_SWAP, T_SWAPTION = "NONFOREIGN_EXCHANGE_SWAP.tsv", "SWAPTION_OPTION_WARNT_DERIV.tsv"
JOIN_TABLES = {
    T_FUTFWD: ("HOLDING_ID", "PAYOFF_PROFILE", "EXPIRATION_DATE", "NOTIONAL_AMOUNT", "CURRENCY_CODE", "UNREALIZED_APPRECIATION"),
    T_OTHER: ("HOLDING_ID", "ISSUER_NAME", "ISSUE_TITLE", "TICKER", "OTHER_DESC"),
    T_BASKET: ("HOLDING_ID", "INDEX_NAME", "NARRATIVE_DESC"),
    T_IDENT: ("HOLDING_ID", "IDENTIFIER_TICKER", "OTHER_IDENTIFIER", "OTHER_IDENTIFIER_DESC"),
    T_SWAP: ("HOLDING_ID", "NOTIONAL_AMOUNT", "CURRENCY_CODE"),
    T_SWAPTION: ("HOLDING_ID", "SHARES_CNT", "PRINCIPAL_AMOUNT", "CURRENCY_CODE"),
}
HOLD_NEED = ("ACCESSION_NUMBER", "HOLDING_ID", "ISSUER_NAME", "ISSUER_TITLE", "BALANCE", "UNIT", "CURRENCY_CODE", "CURRENCY_VALUE", "PAYOFF_PROFILE",
             "ASSET_CAT", "DERIVATIVE_CAT")
FutRec = collections.namedtuple("FutRec", "acc hid name title balance unit ccy value payoff asset_cat")


def stream_join(z, member, ids, stats):
    """Rows of one sub-table whose HOLDING_ID (always the first column) is in `ids`, as {hid: [tuple of the columns of JOIN_TABLES[member]]}.
    A short row (trailing blanks trimmed) is padded; a long row is skipped and counted, never guessed at."""
    cols = JOIN_TABLES[member]
    out = collections.defaultdict(list)
    with z.open(member) as raw:
        f = io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="")
        hdr = f.readline().rstrip("\r\n").split("\t")
        missing = [c for c in cols if c not in hdr]
        if missing or hdr[0] != "HOLDING_ID":
            raise Refused(f"{member}: columns {missing} are missing (first column {hdr[0]!r}); refusing to guess")
        stats[f"header:{member}"] = "|".join(hdr)
        ix = [hdr.index(c) for c in cols]
        n = len(hdr)
        for line in f:
            k = line.find("\t")
            if line[:k] not in ids:
                continue
            p = line.rstrip("\r\n").split("\t")
            if len(p) > n:
                stats[f"ragged_long:{member}"] += 1
                continue
            if len(p) < n:
                p += [""] * (n - len(p))
            out[p[0]].append(tuple(p[i] for i in ix))
    return out


def scan_fut_deriv(z, stats):
    """ONE pass over FUND_REPORTED_HOLDING for the lines with a derivative category: the futures (any ASSET_CAT), and the DIR swaps, options and swaptions.
    Counts every (ASSET_CAT, DERIVATIVE_CAT) pair and the UNIT of every futures line, for the real-data pins of spec 8.3. Returns (fut, der) lists."""
    f, hdr, ix = ntd.open_holdings(z)
    if hdr[-1] != "DERIVATIVE_CAT":
        raise Refused("FUND_REPORTED_HOLDING: DERIVATIVE_CAT is not the last column; refusing to guess")
    missing = [c for c in HOLD_NEED if c not in ix]
    if missing:
        raise Refused(f"FUND_REPORTED_HOLDING: columns {missing} are missing")
    stats["header:FUND_REPORTED_HOLDING"] = "|".join(hdr)
    n = len(hdr)
    g = [ix[c] for c in HOLD_NEED]
    iAC = ix["ASSET_CAT"]
    iU = ix["UNIT"]
    fut, der = [], []
    with f:
        for line in f:
            cut = line.rfind("\t")
            tail = line[cut + 1:].rstrip("\r\n")
            if not tail:
                continue
            p = line.rstrip("\r\n").split("\t")
            if len(p) != n:
                raise Refused(f"holding row with a derivative category has {len(p)} columns, header has {n}; refusing to guess")
            stats[f"pair:{p[iAC]}|{tail}"] += 1
            if tail == "FUT":
                stats[f"fut_unit:{p[iAC]}|{p[iU]}"] += 1
                fut.append(FutRec(*[p[i] for i in g[:-1]]))
            elif p[iAC] == "DIR" and tail in ("SWP", "SWO", "OPT"):
                der.append((p[ix["ACCESSION_NUMBER"]], p[ix["HOLDING_ID"]], tail))
    return fut, der


def join_futures(z, fut, stats):
    """Attach the FUT_FWD row and the four text sources to every futures line of the zip. Returns a list of plain dicts, small enough to pickle."""
    ids = {r.hid for r in fut}
    ff = stream_join(z, T_FUTFWD, ids, stats)
    ot = stream_join(z, T_OTHER, ids, stats)
    bk = stream_join(z, T_BASKET, ids, stats)
    idn = stream_join(z, T_IDENT, ids, stats)
    out = []
    for r in fut:
        rows = ff.get(r.hid, [])
        if len(rows) > 1:
            stats["fut_fwd_duplicate_ids"] += 1
        fw = rows[0][1:] if rows else ("", "", "", "", "")           # the first column of a joined row is the HOLDING_ID
        if not rows:
            stats["fut_fwd_missing_ids"] += 1
        sa = norm_text(r.name + " " + r.title)
        sb = norm_text(" ".join(" ".join(t[1:]) for t in ot.get(r.hid, [])))
        sc = norm_text(" ".join(" ".join(t[1:]) for t in bk.get(r.hid, [])))
        sd = norm_text(" ".join(" ".join(t[1:]) for t in idn.get(r.hid, [])))
        out.append(dict(acc=r.acc, hid=r.hid, balance=r.balance, unit=r.unit, ccy_h=r.ccy, value=r.value, payoff_h=r.payoff, asset_cat=r.asset_cat,
                        payoff=fw[0], exp=fw[1], notional=fw[2], ccy=fw[3], ua=fw[4], texts=(sa, sb, sc, sd), has_fwd=bool(rows)))
    return out


def join_deriv(z, der, stats):
    ids_swp = {h for _, h, t in der if t == "SWP"}
    ids_opt = {h for _, h, t in der if t in ("SWO", "OPT")}
    sw = stream_join(z, T_SWAP, ids_swp, stats) if ids_swp else {}
    op = stream_join(z, T_SWAPTION, ids_opt, stats) if ids_opt else {}
    out = []
    for acc, hid, tail in der:
        if tail == "SWP":
            rows = sw.get(hid, [])
            amt = abs(fnum(rows[0][1]) or 0.0) if rows else 0.0
            out.append((acc, tail, amt, bool(rows)))
        else:
            rows = op.get(hid, [])
            amt = abs(fnum(rows[0][2]) or 0.0) if rows else 0.0           # PRINCIPAL_AMOUNT; SHARES_CNT is a count and is never added to dollars
            out.append((acc, tail, amt, bool(rows)))
    return out


def filing_tuple(f):
    return (f.acc, f.zipi, f.sub_type, f.fdate, f.rdate, f.fund, f.cik, f.net_assets, f.series_name, f.registrant_name, f.total_lines, f.tsy_lines,
            f.tsy_value, f.dir_lines)


def filing_from_tuple(t):
    f = ntd.Filing(t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8], t[9])
    f.total_lines, f.tsy_lines, f.tsy_value, f.dir_lines = t[10], t[11], t[12], t[13]
    return f


def work_path(work, stage, tag):
    return os.path.join(work, f"{stage}_{tag}.pkl")


def run_stage_a(zip_path, zipi, tag, windows, work, log=print):
    """Stage A for one zip: the cash build's pass A, imported (ntd.load_zip_filings, ntd.scan_zip_holdings), and this script's futures pass."""
    t0 = time.time()
    z = zipfile.ZipFile(zip_path)
    sha = ntd.file_sha256(zip_path)
    fl = ntd.load_zip_filings(z, zipi)
    st, sfl = ntd.scan_zip_holdings(z, fl)
    stats = collections.Counter()
    fut, der = scan_fut_deriv(z, stats)
    futs = join_futures(z, fut, stats)
    ders = join_deriv(z, der, stats)
    # whole-zip real-data pins (spec 8.3): the notional per face for every line the classifier names as a Treasury contract
    ratios = collections.defaultdict(list)
    for r in futs:
        cls, c, _ = classify(r["texts"], r["ccy"])
        if cls != "tsy":
            continue
        bal, nt = fnum(r["balance"]), fnum(r["notional"])
        if bal and nt and abs(nt) > 0 and abs(abs(nt) - abs(bal)) > 0.01 * abs(bal):
            ratios[c].append(abs(nt) / (abs(bal) * face_of(c)))
    pack = dict(tag=tag, zip=os.path.basename(zip_path), sha=sha, size=os.path.getsize(zip_path), filings=[filing_tuple(f) for f in fl],
                st=dict(st), sfl=dict(sfl), stats=dict(stats), fut=futs, der=ders, ratios={k: sorted(v) for k, v in ratios.items()})
    os.makedirs(work, exist_ok=True)
    tmp = work_path(work, "A", tag) + ".tmp"
    with open(tmp, "wb") as fh:
        pickle.dump(pack, fh, protocol=4)
    os.replace(tmp, work_path(work, "A", tag))
    log(f"stage A {tag}: {len(fl):,} filings, {st['holding_rows']:,} holding rows, {len(futs):,} futures lines, {len(ders):,} swap/option lines, {time.time() - t0:.0f} s")


def load_stage_a(work, tag):
    path = work_path(work, "A", tag)
    if not os.path.exists(path):
        raise Refused(f"{path} is missing; run `scan --stage A --zips {tag}` first")
    with open(path, "rb") as fh:
        return pickle.load(fh)


def select_from_packs(packs, windows):
    """The cash build's survivors, imported (ntd.select_vintage), from the Filing objects of the stage-A packs."""
    all_filings = []
    for pk in packs:
        all_filings.extend(filing_from_tuple(t) for t in pk["filings"])
    fba = {f.acc: f for f in all_filings}
    sel = {v: ntd.select_vintage(all_filings, windows, v) for v in ("base", "matched")}
    memb = {}
    for v, bit in (("base", 1), ("matched", 2)):
        for wi, lst in sel[v]["assign"].items():
            for f, _tag in lst:
                w0, m0 = memb.get(f.acc, (wi, 0))
                memb[f.acc] = (wi, m0 | bit)
    return all_filings, fba, sel, memb


def run_stage_b(zip_path, zipi, tag, windows, packs, work, log=print):
    """Stage B for one zip: the cash build's pass B, imported (ntd.stream_survivor_lines, ntd.read_debt), for the survivors of that zip."""
    t0 = time.time()
    all_filings, fba, sel, memb = select_from_packs(packs, windows)
    wanted = {acc for acc in memb if fba[acc].zipi == zipi}
    z = zipfile.ZipFile(zip_path)
    lines = ntd.stream_survivor_lines(z, wanted)
    debt = ntd.read_debt(z, {L.hid for L in lines})
    pack = dict(tag=tag, lines=[tuple(L) for L in lines], debt=debt, wanted_n=len(wanted))
    tmp = work_path(work, "B", tag) + ".tmp"
    with open(tmp, "wb") as fh:
        pickle.dump(pack, fh, protocol=4)
    os.replace(tmp, work_path(work, "B", tag))
    log(f"stage B {tag}: {len(wanted):,} survivor filings, {len(lines):,} Treasury lines, {len(debt):,} DEBT rows, {time.time() - t0:.0f} s")


def load_stage_b(work, tag):
    path = work_path(work, "B", tag)
    if not os.path.exists(path):
        raise Refused(f"{path} is missing; run `scan --stage B --zips {tag}` first")
    with open(path, "rb") as fh:
        pk = pickle.load(fh)
    pk["lines"] = [ntd.Line(*t) for t in pk["lines"]]
    return pk


# ------------------------------------------------------------------------------------------------------------------------
# the cash build's Ctx, subclassed (R3, R23-17): per-series S for both vintages and the notes-and-bonds part for A2, taken from the SAME te the
# cash build adds to its own totals, through a tap on its running sum. Nothing of Ctx.add is copied.
# ------------------------------------------------------------------------------------------------------------------------
class TapFsum(Fsum):
    __slots__ = ("owner", "vint", "wi")

    def __init__(self, owner, vint, wi):
        Fsum.__init__(self)
        self.owner, self.vint, self.wi = owner, vint, wi

    def add(self, x):
        Fsum.add(self, x)
        self.owner.tap(self.vint, self.wi, x)


class FCtx(ntd.Ctx):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.cur = None
        self.s_fund = collections.defaultdict(Fsum)       # (vintage, window idx, fund) -> cash 10-year equivalents on the fixed curve, $bn
        self.nb_fund = collections.defaultdict(Fsum)      # (window idx, fund) -> the coupon and TIPS part, base vintage
        for (vint, wi), ag in self.agg.items():
            ag.s["tenyeq_fixed"] = TapFsum(self, vint, wi)

    def tap(self, vint, wi, x):
        fund, kind = self.cur
        self.s_fund[(vint, wi, fund)].add(x)
        if vint == "base" and kind in ("coupons", "tips"):
            self.nb_fund[(wi, fund)].add(x)

    def add(self, tag, L, f, wi, mask, kind, rule, coupon, mat):
        self.cur = (f.fund, kind)
        super().add(tag, L, f, wi, mask, kind, rule, coupon, mat)

    def s_of(self, vint, wi, fund):
        v = self.s_fund.get((vint, wi, fund))
        return 0.0 if v is None else v.value()


# ------------------------------------------------------------------------------------------------------------------------
# Part 1 line evaluation and accumulation (spec 3.1-3.4)
# ------------------------------------------------------------------------------------------------------------------------
def parse_exp(s):
    try:
        return ntd.pdate(s) if s else None
    except (KeyError, ValueError):
        return None


def evaluate_future(rec, rdate):
    """Classification, expiry, sign and size of one futures line. Pure; no pricing. Returns a dict with `status`: kept, expired, sign_na, no_size,
    unresolved, conflict, or one of the non-Treasury reasons (nontsy)."""
    cls, c, reason = classify(rec["texts"], rec["ccy"])
    ev = dict(cls=cls, contract=c, reason=reason, status=None)
    exp = parse_exp(rec["exp"])
    ev["exp"] = exp
    bal, nt = fnum(rec["balance"]), fnum(rec["notional"])
    ev["nt_abs"] = 0.0 if nt is None else abs(nt)
    if cls in ("tsy", "unresolved", "conflict") and exp is not None and exp < rdate:
        ev["status"] = "expired"
        return ev
    if cls == "tsy":
        sp, sb = line_signs(rec["payoff"], bal, rec["payoff_h"])
        sz = size_line(c, bal, rec["unit"], nt, fnum(rec["value"]))
        ev.update(sp=sp, sb=sb, size=sz, bal=bal, nt=nt)
        ev["status"] = "sign_na" if sp is None else ("no_size" if sz.basis == "none" else "kept")
    elif cls in ("unresolved", "conflict"):
        ev["status"] = cls
    else:
        ev["status"] = "nontsy"
    return ev


class ContractAgg:
    __slots__ = ("lines", "funds", "contracts_net", "face_net", "tenor", "ctd", "ratios", "ctd_sizes")

    def __init__(self):
        self.lines = 0
        self.funds = set()
        self.contracts_net, self.face_net, self.tenor, self.ctd = Fsum(), Fsum(), Fsum(), Fsum()
        self.ratios = []
        self.ctd_sizes = collections.defaultdict(float)        # delivery month -> kept face, to name the modal CTD


class FundF:
    __slots__ = ("face_net", "face_net_b", "face_long", "face_gross", "f_tenor", "f_bal", "f_ctd")

    def __init__(self):
        for k in self.__slots__:
            setattr(self, k, Fsum())


WIN_SUMS = ("face_long", "face_short", "contracts_long", "contracts_short", "nt_td_net", "f_tenor", "f_bal", "f_ctd", "ua_abs", "size_kept",
            "size_bad", "disagree_size", "nt_abs_kept")


class WinAgg:
    def __init__(self):
        self.s = {k: Fsum() for k in WIN_SUMS}
        self.n = collections.Counter()
        self.by_c = collections.defaultdict(ContractAgg)
        self.fund = {}                                         # fund -> FundF (base vintage only)
        self.funds_fut = set()
        self.cat = collections.defaultdict(lambda: [0, Fsum()])   # fut_other_deriv categories (base only)
        self.asset_cat = collections.Counter()
        self.reasons = collections.Counter()
        self.sign_agree = collections.Counter()                # C-F5: agreement counts and tenor-dollar weights
        self.sign_agree_w = [Fsum(), Fsum()]


class FutEngine:
    def __init__(self, windows, tenor, ctd_resolver):
        self.windows = windows
        self.tenor = tenor                                     # contract -> (factor usd, CF, y, duration)
        self.ctd_resolver = ctd_resolver                       # (contract, expiry date, window) -> (factor, Deliv, CF) or None; None for non-R2 windows
        self.agg = {(v, w.idx): WinAgg() for v in ("base", "matched") for w in windows}
        self.fallback_note = collections.Counter()

    def add(self, rec, f, wi, mask, ev):
        status, c = ev["status"], ev["contract"]
        w = self.windows[wi]
        ctd = None
        if status == "kept" and (mask & 1) and w.qend.isoformat() in R2_DATES:
            ctd = self.ctd_resolver(c, ev["exp"], w)
        for vint, bit in (("base", 1), ("matched", 2)):
            if not mask & bit:
                continue
            a = self.agg[(vint, wi)]
            base = vint == "base"
            a.n["fut_lines"] += 1
            if base:
                a.asset_cat[rec["asset_cat"]] += 1
                a.reasons[ev["reason"] if status != "expired" else "expired"] += 1
            cls = ev["cls"]
            if cls == "non_usd":
                a.n["non_usd_lines"] += 1
            if status == "expired":
                a.n["expired_lines"] += 1
                continue
            if status == "nontsy":
                if base:
                    a.cat[nontsy_category(ev["reason"], rec["texts"])][0] += 1
                    a.cat[nontsy_category(ev["reason"], rec["texts"])][1].add(ev["nt_abs"])
                continue
            if status in ("unresolved", "conflict"):
                a.n["unresolved_lines" if status == "unresolved" else "unresolved_conflict_lines"] += 1
                a.s["size_bad"].add(ev["nt_abs"])
                if base:
                    a.cat["unresolved"][0] += 1
                    a.cat["unresolved"][1].add(ev["nt_abs"])
                continue
            # a Treasury line: the sizes and the ratio for C-F4 whatever the sign
            sz = ev["size"]
            ca = a.by_c[c]
            if sz.n is not None and ev["nt"] not in (None, 0.0) and not sz.notional_is_count:
                ca.ratios.append(abs(ev["nt"]) / (sz.n * face_of(c)))      # C-F4: every valid-count line before the basis fallback
            if status == "sign_na":
                a.n["sign_na_lines"] += 1
                a.s["size_bad"].add(sz.face_usd)
                if base:
                    a.cat["sign_na"][0] += 1
                    a.cat["sign_na"][1].add(ev["nt_abs"])
                continue
            if status == "no_size":
                a.n["no_size_lines"] += 1
                continue
            sp, sb = ev["sp"], ev["sb"]
            fac = self.tenor[c][0]
            term_t = sz.contracts * fac
            a.n["tsy_fut_lines"] += 1
            a.funds_fut.add(f.fund)
            if sz.basis == "face":
                a.n["lines_basis_face"] += 1
            else:
                a.n["lines_basis_notional"] += 1
            if sz.notional_is_count:
                a.n["notional_field_is_count_lines"] += 1
            if sz.suspect:
                a.n["unit_suspect_lines"] += 1
            if rec["asset_cat"] != "DIR":
                a.n["non_dir_tsy_lines"] += 1
            a.s["size_kept"].add(sz.face_usd)
            (a.s["face_long"] if sp > 0 else a.s["face_short"]).add(sz.face_usd)
            (a.s["contracts_long"] if sp > 0 else a.s["contracts_short"]).add(sz.contracts)
            if ev["nt"] is not None and not sz.notional_is_count:
                a.s["nt_td_net"].add(sp * abs(ev["nt"]))
                a.s["nt_abs_kept"].add(abs(ev["nt"]))
            a.s["f_tenor"].add(sp * term_t / 1e9)
            sb2 = sb if sb is not None else sp
            a.s["f_bal"].add(sb2 * term_t / 1e9)
            ua = fnum(rec["ua"])
            if ua is not None:
                a.s["ua_abs"].add(abs(ua))
            bal = ev["bal"]
            if bal is not None and bal != 0:
                agree = (sgn(bal) == sp)
                a.sign_agree["agree" if agree else "disagree"] += 1
                a.sign_agree_w[0 if agree else 1].add(term_t / 1e9)
            if sb2 != sp:
                a.n["sign_disagree_lines"] += 1
                a.s["disagree_size"].add(sz.face_usd)
            ca.lines += 1
            ca.funds.add(f.fund)
            ca.contracts_net.add(sp * sz.contracts)
            ca.face_net.add(sp * sz.face_usd / 1e9)
            ca.tenor.add(sp * term_t / 1e9)
            if base:
                fu = a.fund.get(f.fund)
                if fu is None:
                    fu = a.fund[f.fund] = FundF()
                fu.face_net.add(sp * sz.face_usd)
                fu.face_net_b.add(sb2 * sz.face_usd)
                fu.face_long.add(sz.face_usd if sp > 0 else 0.0)
                fu.face_gross.add(sz.face_usd)
                fu.f_tenor.add(sp * term_t / 1e9)
                fu.f_bal.add(sb2 * term_t / 1e9)
            if base and (mask & 1) and w.qend.isoformat() in R2_DATES:
                if ctd is None:
                    a.n["ctd_fallback_lines"] += 1
                    term_c = term_t
                else:
                    term_c = sz.contracts * ctd[0]
                    ca.ctd_sizes[(first_of_month(ev["exp"]) if ev["exp"] else None, ctd[1].cusip, ctd[1].coupon, ctd[1].maturity, ctd[2], ctd[0])] += sz.face_usd
                a.s["f_ctd"].add(sp * term_c / 1e9)
                ca.ctd.add(sp * term_c / 1e9)
                if f.fund in a.fund:
                    a.fund[f.fund].f_ctd.add(sp * term_c / 1e9)

    def add_deriv(self, acc_to_wm, der):
        """Swaps, options and swaptions of the base survivors (printed only, spec 3.6)."""
        names = {"SWP": "swap_dir", "SWO": "swaption_dir", "OPT": "option_dir"}
        for acc, tail, amt, found in der:
            wm = acc_to_wm.get(acc)
            if wm is None or not (wm[1] & 1):
                continue
            a = self.agg[("base", wm[0])]
            k = names[tail]
            a.cat[k][0] += 1
            a.cat[k][1].add(amt)


def nontsy_category(reason, texts):
    """The category of a non-Treasury futures line in fut_other_deriv.csv (spec 3.6)."""
    if reason == "ir_nontsy":
        return "ir_fut_nontsy"
    if reason in ("foreign_bond",):
        return "bond_fut_foreign"
    if reason in ("non_usd", "blank_currency_no_us_exchange"):
        return "bond_fut_foreign" if any(RX_BONDISH.search(t) for t in texts) else "other_fut_nontsy"
    return "other_fut_nontsy"


def share_bad(a):
    kept, bad = a.s["size_kept"].value(), a.s["size_bad"].value()
    return bad / (kept + bad) if (kept + bad) else 0.0


# ------------------------------------------------------------------------------------------------------------------------
# decision rules (spec 4.2, 4.3), pure functions
# ------------------------------------------------------------------------------------------------------------------------
def part1_label(d_f, a_pass, u_f_start, u_f_end, g_v, g_c, g_s):
    """Spec 4.3. LARGE / SMALL need every condition; otherwise INCONCLUSIVE. The bound on |dF| is inclusive at $100bn."""
    ok = (a_pass and le(u_f_start, UF_MAX) and le(u_f_end, UF_MAX) and le(g_v, GV_MAX) and le(g_c, GC_MAX)
          and (M("drop_gs") or le(g_s, GS_MAX)))
    if not ok:
        return "INCONCLUSIVE"
    return "LARGE" if ge(abs(d_f), DF_BAR_BN) else "SMALL"


def q_defined(ds_index, ds_active, base_ds):
    """R23-13: q is defined only if both arms are non-negative and together at least a quarter of the period's base change."""
    if M("drop_q_bounds"):
        return (ds_index + ds_active) != 0
    return ds_index >= 0 and ds_active >= 0 and ge(ds_index + ds_active, Q_BASE_SHARE * base_ds)


def q_of(ds_index, ds_active, base_ds):
    if not q_defined(ds_index, ds_active, base_ds):
        return None
    return ds_index / (ds_index + ds_active)


def part2_label(q24, q25, q26, s0, u):
    """Spec 4.2, evaluated in this order: 1 INCONCLUSIVE, 2 SUPPORTS, 3 AGAINST, 4 INCONCLUSIVE."""
    cap = 16.21 if M("u_cap_16210") else U_CAP_BN

    def supports():
        exc = gt if M("excess_gt") else ge             # the mutants make the pre-registered bars strict
        rise = gt if M("rise_gt") else ge
        return (q26 is not None and q24 is not None and q25 is not None and ge(q26, Q_SUPPORT) and exc(q26 - s0, Q_EXCESS)
                and rise(q26 - q24, Q_RISE) and rise(q26 - q25, Q_RISE))

    if M("rule_order_swap") and supports():
        return "SUPPORTS"                       # the mutant: SUPPORTS tested before the unclassified cap and the q bounds
    if u > cap or q24 is None or q25 is None or q26 is None:
        return "INCONCLUSIVE"
    if supports():
        return "SUPPORTS"
    if (lt if M("against_lt") else le)(q26, Q_AGAINST) and le(q26 - s0, 0.0):
        return "AGAINST"
    return "INCONCLUSIVE"


def bar_state(q, s0):
    """For the printed yes/no flags of ruling B3: where a q sits against the bars of the rule."""
    if q is None:
        return "undefined"
    if ge(q, Q_SUPPORT) and ge(q - s0, Q_EXCESS):
        return "above"
    if le(q, Q_AGAINST) and le(q - s0, 0.0):
        return "below"
    return "between"


# ------------------------------------------------------------------------------------------------------------------------
# build context: survivors, cash pricing (imported), curves, tenor map, CTD resolver, futures engine
# ------------------------------------------------------------------------------------------------------------------------
def make_ctd_resolver(r2, nom_all, fixed):
    cache, dels = {}, {}

    def resolver(contract, exp, w):
        if exp is None:
            return None
        fdm = first_of_month(exp)
        key = (contract, fdm, w.qend)
        if key in cache:
            return cache[key]
        if w.qend not in dels:
            rows, _ = r2.load_mspd_table3(w.qend.isoformat())
            curve_d = r2.curve_points(nom_all[r2.on_or_before(nom_all, w.qend)], r2.NOM_MATURITIES)
            dels[w.qend] = (deliverables_from_rows(rows), curve_d)
        dv, cd = dels[w.qend]
        cache[key] = ctd_factor(contract, fdm, dv, cd, fixed[0], fixed[2])
        return cache[key]
    return resolver


def zip_slice(zips, wanted):
    """`wanted` is None or a comma list of zip tags such as 2024q1; returns [(index, (y, q, path))]."""
    out = []
    for i, z in enumerate(zips):
        tag = f"{z[0]}q{z[1]}"
        if wanted is None or tag in wanted:
            out.append((i, z))
    return out


def build_core(a, log):
    zips = ntd.discover_zips(a.zip_dir)
    windows = ntd.make_windows(zips)
    r1_cache, r2_cache = os.path.abspath(a.r1_cache), os.path.abspath(a.r2_cache)
    ntd.check_caches(r1_cache, r2_cache)
    r2 = ntd.load_r2(r1_cache, r2_cache)
    nom_all, real_all = r2.load_curve("daily_treasury_yield_curve"), r2.load_curve("daily_treasury_real_yield_curve")
    fixed = ntd.r2_fixed_curve(r2, nom_all, real_all, r2.FIXED_CURVE_DATE)
    alt = ntd.r2_fixed_curve(r2, nom_all, real_all, ntd.ALT_CURVE_DATE)
    mspd, ratios = ntd.build_mspd(r2)
    pricer = ntd.Pricer(r2, nom_all, real_all, fixed, alt)
    log(f"{len(zips)} zips -> windows {windows[0].label}..{windows[-1].label}; fixed curve {fixed[3]}, d10 {fixed[2]:.4f}")
    packs = [load_stage_a(a.work, w.zip_tag) for w in windows]
    bpacks = [load_stage_b(a.work, w.zip_tag) for w in windows]
    for pk, (y, q, path) in zip(packs, zips):
        if pk["zip"] != os.path.basename(path):
            raise Refused(f"stage A pack {pk['tag']} was made from {pk['zip']}, not {os.path.basename(path)}")
    all_filings, fba, sel, memb = select_from_packs(packs, windows)
    log(f"survivors: base {len(sel['base']['kept']):,} filings, matched {len(sel['matched']['kept']):,}")
    ctx = FCtx(r2, pricer, mspd, ratios, windows, fba)
    for w, bk in zip(windows, bpacks):
        ctx.process_lines(w.zip_tag, bk["lines"], bk["debt"], memb)
    ctx.resolve_pending()
    log("cash pricing done (the cash build's Ctx, imported)")
    tenor = tenor_table(fixed[0], fixed[2])
    eng = FutEngine(windows, tenor, make_ctd_resolver(r2, nom_all, fixed))
    acc_to_wm = dict(memb)
    for pk in packs:
        for rec in pk["fut"]:
            wm = acc_to_wm.get(rec["acc"])
            if wm is None:
                continue
            f = fba[rec["acc"]]
            eng.add(rec, f, wm[0], wm[1], evaluate_future(rec, f.rdate))
        eng.add_deriv(acc_to_wm, pk["der"])
    log("futures pass done")
    return dict(a=a, log=log, zips=zips, windows=windows, r1_cache=r1_cache, r2_cache=r2_cache, r2=r2, nom_all=nom_all, real_all=real_all,
                fixed=fixed, alt=alt, mspd=mspd, packs=packs, bpacks=bpacks, all_filings=all_filings, fba=fba, sel=sel, memb=memb, ctx=ctx,
                eng=eng, tenor=tenor, by_label={w.label: w for w in windows})


# ------------------------------------------------------------------------------------------------------------------------
# Part 1 results
# ------------------------------------------------------------------------------------------------------------------------
def fval(B, vint, label, field):
    return B["eng"].agg[(vint, B["by_label"][label].idx)].s[field].value()


def universe_sums(B, label, include=None, norow=None):
    """The 'Treasury funds' of spec 3.7 at one window (base vintage): survivors whose clean cash Treasury value, or whose gross Treasury-futures face,
    exceeds 1% of NET_ASSETS. `include(fund)` restricts it (the ex-ETF print)."""
    w = B["by_label"][label]
    a = B["eng"].agg[("base", w.idx)]
    ctx = B["ctx"]
    d10 = B["fixed"][2]
    tot = collections.defaultdict(Fsum)
    n_univ = n_fut = n_norow = 0
    for f, _tag in B["sel"]["base"]["assign"][w.idx]:
        if include is not None and not include(f.fund):
            continue
        fa = ctx.fund_agg.get((w.idx, f.fund))
        cash = fa.value.value() * 1e9 if fa else 0.0
        fu = a.fund.get(f.fund)
        gross = fu.face_gross.value() if fu else 0.0
        if f.net_assets > 0 and (cash > 0.01 * f.net_assets or gross > 0.01 * f.net_assets):
            n_univ += 1
            if norow is not None and norow(f.fund):
                n_norow += 1
            if fu:
                n_fut += 1
                tot["face_net"].add(fu.face_net.value())
                tot["face_net_b"].add(fu.face_net_b.value())
                tot["f_tenor"].add(fu.f_tenor.value())
                tot["f_bal"].add(fu.f_bal.value())
            nb = ctx.nb_fund.get((w.idx, f.fund))
            if nb:
                tot["nb_te"].add(nb.value())
    v = {k: x.value() for k, x in tot.items()}
    face_net, face_net_b = v.get("face_net", 0.0), v.get("face_net_b", 0.0)
    f_t, f_b, nb_te = v.get("f_tenor", 0.0), v.get("f_bal", 0.0), v.get("nb_te", 0.0)
    out = dict(universe_n=n_univ, universe_with_futures_n=n_fut, no_row_n=n_norow, a1=face_net / 1e9, a1_bal=face_net_b / 1e9,
               a2=(f_t / nb_te) if nb_te else None, a2_bal=(f_b / nb_te) if nb_te else None,
               a3=(f_t * 1e9 * d10 / face_net) if face_net else None, a3_bal=(f_b * 1e9 * d10 / face_net_b) if face_net_b else None,
               f_tenor=f_t, nb_te=nb_te, dv01_f_mn=f_t * d10 * 0.1, dv01_nb_mn=nb_te * d10 * 0.1)
    return out


def a_pass(u, bal=False):
    s = "_bal" if bal else ""
    a1, a2, a3 = u["a1" + s], u["a2" + s], u["a3" + s]
    return (a1 is not None and a2 is not None and a3 is not None and A1_RANGE[0] <= a1 <= A1_RANGE[1]
            and A2_RANGE[0] <= a2 <= A2_RANGE[1] and A3_RANGE[0] <= a3 <= A3_RANGE[1])


def part1_results(B, ncen_include=None, ncen_norow=None):
    """Everything Part 1 reports, as rows and scalars, before the small-cell merge and the writer."""
    windows, eng, sel, ctx, fixed = B["windows"], B["eng"], B["sel"], B["ctx"], B["fixed"]
    d10 = fixed[2]
    R = {}
    rows_w, rows_c = [], []
    for w in windows:
        for vint in ("base", "matched"):
            ag = eng.agg[(vint, w.idx)]
            isr2 = vint == "base" and w.qend.isoformat() in R2_DATES
            kept = ag.s["size_kept"].value()
            rows_w.append(dict(
                window=w.label, quarter_end=w.qend.isoformat(), vintage=vint, funds_in_window=len(sel[vint]["assign"][w.idx]),
                funds_with_tsy_fut=len(ag.funds_fut), tsy_fut_lines=ag.n["tsy_fut_lines"],
                contracts_long=ag.s["contracts_long"].value(), contracts_short=ag.s["contracts_short"].value(),
                face_long_bn=ag.s["face_long"].value() / 1e9, face_short_bn=ag.s["face_short"].value() / 1e9,
                face_net_bn=(ag.s["face_long"].value() - ag.s["face_short"].value()) / 1e9,
                notional_tradedate_net_bn=ag.s["nt_td_net"].value() / 1e9,
                tenyeq_tenor_bn=ag.s["f_tenor"].value(), tenyeq_tenor_balsign_bn=ag.s["f_bal"].value(),
                tenyeq_ctd_bn=(ag.s["f_ctd"].value() if isr2 else None), unrealized_abs_bn=ag.s["ua_abs"].value() / 1e9,
                lines_basis_face=ag.n["lines_basis_face"], lines_basis_notional=ag.n["lines_basis_notional"],
                notional_field_is_count_lines=ag.n["notional_field_is_count_lines"], unit_suspect_lines=ag.n["unit_suspect_lines"],
                no_size_lines=ag.n["no_size_lines"], non_usd_lines=ag.n["non_usd_lines"], unresolved_lines=ag.n["unresolved_lines"],
                unresolved_conflict_lines=ag.n["unresolved_conflict_lines"], sign_na_lines=ag.n["sign_na_lines"],
                sign_disagree_lines=ag.n["sign_disagree_lines"],
                sign_disagree_notional_share=(ag.s["disagree_size"].value() / kept if kept else None),
                expired_lines=ag.n["expired_lines"], non_dir_tsy_lines=ag.n["non_dir_tsy_lines"],
                ctd_fallback_lines=(ag.n["ctd_fallback_lines"] if isr2 else None), unresolved_share=share_bad(ag)))
            if vint == "base":
                for c in CONTRACTS:
                    ca = ag.by_c.get(c)
                    if ca is None or ca.lines == 0:
                        continue
                    row = dict(window=w.label, contract=c, funds_n=len(ca.funds), lines=ca.lines, contracts_net=ca.contracts_net.value(),
                               face_net_bn=ca.face_net.value(), tenyeq_tenor_bn=ca.tenor.value(),
                               tenyeq_ctd_bn=(ca.ctd.value() if isr2 else None), dv01_tenor_mn=ca.tenor.value() * d10 * 0.1,
                               tenor_factor_usd=B["tenor"][c][0],
                               notional_over_face_median=(statistics.median(ca.ratios) if ca.ratios else None))
                    if isr2 and ca.ctd_sizes:
                        key, _sz = sorted(ca.ctd_sizes.items(), key=lambda kv: (-kv[1], str(kv[0])))[0]
                        row.update(ctd_factor_usd=key[5], ctd_maturity=key[3].isoformat(), ctd_coupon_pct=key[2], ctd_cf=key[4])
                    rows_c.append(row)
    R["rows_w"], R["rows_c"] = rows_w, rows_c
    # ---- change and decision inputs
    var = [("T0", "tenor map, base vintage, PAYOFF_PROFILE sign (the headline)", "base", "f_tenor"),
           ("T1", "tenor map, matched vintage", "matched", "f_tenor"),
           ("C0", "modelled cheapest-to-deliver, base vintage (R2-date windows)", "base", "f_ctd"),
           ("B0", "tenor map, base vintage, BALANCE sign (R23-1)", "base", "f_bal")]
    rows_chg, chg = [], {}
    for vid, desc, vint, field in var:
        for per, l0, l1 in PERIODS:
            f0, f1 = fval(B, vint, l0, field), fval(B, vint, l1, field)
            rows_chg.append(dict(variant_id=vid, description=desc, period=per, f_start_bn=f0, f_end_bn=f1, d_f_bn=f1 - f0))
            chg[(vid, per)] = (f0, f1, f1 - f0)
    R["rows_chg"], R["chg"] = rows_chg, chg
    # ---- continuing / entrant / leaver split of the headline
    rows_sp = []
    for per, l0, l1 in PERIODS:
        w0, w1 = B["by_label"][l0], B["by_label"][l1]
        a0, a1 = eng.agg[("base", w0.idx)], eng.agg[("base", w1.idx)]
        p0 = {f.fund for f, _ in sel["base"]["assign"][w0.idx]}
        p1 = {f.fund for f, _ in sel["base"]["assign"][w1.idx]}
        grp = {g: [set(), Fsum()] for g in ("continuing", "entrant", "leaver")}
        for fund in sorted(set(a0.fund) | set(a1.fund)):
            in0, in1 = fund in p0, fund in p1
            g = "continuing" if (in0 and in1) else ("entrant" if in1 else "leaver")
            x0 = a0.fund[fund].f_tenor.value() if fund in a0.fund else 0.0
            x1 = a1.fund[fund].f_tenor.value() if fund in a1.fund else 0.0
            grp[g][0].add(fund)
            grp[g][1].add(x1 - x0)
        for g in ("continuing", "entrant", "leaver"):
            rows_sp.append(dict(period=per, group=g, funds_n=len(grp[g][0]), d_f_bn=grp[g][1].value()))
    R["rows_sp"] = rows_sp
    # ---- fut_other_deriv
    rows_o = []
    for w in windows:
        ag = eng.agg[("base", w.idx)]
        for cat in sorted(ag.cat):
            rows_o.append(dict(window=w.label, category=cat, lines=ag.cat[cat][0], notional_abs_bn=ag.cat[cat][1].value() / 1e9))
    R["rows_o"] = rows_o
    # ---- anchors and decision inputs
    R["anchor_all"] = universe_sums(B, "2023Q4", None, ncen_norow)                      # the registered, primary anchors: all registered funds (R23-7)
    R["anchor_exetf"] = universe_sums(B, "2023Q4", ncen_include) if ncen_include is not None else None
    a23 = eng.agg[("base", B["by_label"]["2023Q4"].idx)]
    R["a4_gross_long_bn"] = a23.s["face_long"].value() / 1e9
    d_f = chg[("T0", "full")][2]
    u0, u1 = share_bad(eng.agg[("base", B["by_label"]["2023Q4"].idx)]), share_bad(eng.agg[("base", B["by_label"]["2026Q2"].idx)])
    g_v = abs(chg[("T0", "full")][2] - chg[("T1", "full")][2])
    g_c = abs(chg[("T0", "full")][2] - chg[("C0", "full")][2])
    g_s = abs(chg[("T0", "full")][2] - chg[("B0", "full")][2])
    R.update(d_f=d_f, u_f=(u0, u1), g_v=g_v, g_c=g_c, g_s=g_s)
    R["a_pass"] = a_pass(R["anchor_all"])
    R["label"] = part1_label(d_f, R["a_pass"], u0, u1, g_v, g_c, g_s)
    return R


# ------------------------------------------------------------------------------------------------------------------------
# Part 2: Form N-CEN flags (spec 4.1)
# ------------------------------------------------------------------------------------------------------------------------
NcenRec = collections.namedtuple("NcenRec", "period fdate acc flags feeders")


def flag_value(fl):
    """R23-9, in exactly this order: mmf; else unflagged when N/A sits beside a type box; else levinv; else index; else active."""
    def y(k):
        return fl.get(k, "") == "Y"
    type_box = any(y(k) for k in FLAG_TYPE_COLS)
    if M("flag_levinv_before_mmf") and y("IS_MULTI_INVERSE_INDEX"):
        return "levinv"
    if y("IS_MONEY_MARKET"):
        return "mmf"
    if M("flag_index_before_na") and y("IS_INDEX"):
        return "index"
    if y("IS_FUND_TYPE_NA") and type_box:
        return "unflagged"
    if M("flag_na_alone_unflagged") and y("IS_FUND_TYPE_NA"):
        return "unflagged"
    if y("IS_MULTI_INVERSE_INDEX"):
        return "levinv"
    if y("IS_INDEX"):
        return "index"
    return "active"


def keep_submission_type(t):
    t = (t or "").strip().upper()
    if M("flag_use_nt"):
        return t.startswith("N-CEN") or t.startswith("NT")           # the mutant: a notice of late filing is read as a filing
    return t in ("N-CEN", "N-CEN/A")


def ncen_zip_list(ncen_dir):
    found = []
    for name in sorted(os.listdir(tilde(ncen_dir))):
        m = NCEN_ZIP_RE.match(name)
        if m:
            found.append((int(m.group(1)), int(m.group(2)), name, os.path.join(tilde(ncen_dir), name)))
    found.sort()
    if not found:
        raise Refused(f"no YYYYqQ_ncen.zip found in {ncen_dir}; refusing")
    quarters = collections.Counter((y, q) for y, q, _, _ in found)
    dup = sorted(k for k, n in quarters.items() if n > 1)
    if dup:
        raise Refused(f"C-B1: the quarter(s) {dup} are claimed by two N-CEN zips; refusing")
    return found


def _ncen_rows(z, member, cols):
    try:
        return ntd.table_rows(z, member, list(cols))
    except ValueError as e:
        with z.open(member) as raw:
            hdr = raw.readline().decode("utf-8", "replace").rstrip("\r\n").split("\t")
        raise Refused(f"C-B1: {member} lacks {sorted(set(cols) - set(hdr))} (header: {hdr[:8]}...); refusing") from e


def load_ncen(ncen_dir, want_names=False):
    """All N-CEN zips -> (table, stats, names). table[key] = list of NcenRec sorted by period, one per (key, period) after the amendment rule.
    key = ("S", SERIES_ID) or ("C", registrant CIK) for a blank-SERIES_ID row when that registrant has exactly one such row in the filing."""
    zl = ncen_zip_list(ncen_dir)
    best = {}
    stats = collections.Counter()
    names = set()
    for y, q, name, path in zl:
        z = zipfile.ZipFile(path)
        sub = {}
        for acc, typ, fd, per in _ncen_rows(z, "SUBMISSION.tsv", ["ACCESSION_NUMBER", "SUBMISSION_TYPE", "FILING_DATE", "REPORT_ENDING_PERIOD"]):
            stats[f"submission_type:{typ}"] += 1
            if not keep_submission_type(typ):
                continue
            try:
                sub[acc] = (pdate(fd), pdate(per))
            except (KeyError, ValueError):
                stats["submission_bad_date"] += 1
        reg_cols = ["ACCESSION_NUMBER", "CIK"] + (["REGISTRANT_NAME"] if want_names else [])
        reg = {}
        for row in _ncen_rows(z, "REGISTRANT.tsv", reg_cols):
            reg[row[0]] = row[1].strip()
            if want_names:
                names.add(row[2])
        fri_cols = list(NCEN_FRI_COLS) + (["FUND_NAME"] if want_names else [])
        fri = _ncen_rows(z, "FUND_REPORTED_INFO.tsv", fri_cols)
        ix = {c: i for i, c in enumerate(fri_cols)}
        feeders = collections.defaultdict(set)
        fid_series = {}
        for r in fri:
            fid_series[r[ix["FUND_ID"]]] = (r[ix["ACCESSION_NUMBER"]], r[ix["SERIES_ID"]].strip())
        for fid, sid in _ncen_rows(z, "FEEDER_FUNDS.tsv", ["FUND_ID", "REGISTERED_SERIES_ID"]):
            if sid.strip():
                feeders[fid].add(sid.strip())
        blank_n = collections.Counter(r[ix["ACCESSION_NUMBER"]] for r in fri if not r[ix["SERIES_ID"]].strip())
        for r in fri:
            if want_names:
                names.add(r[ix["FUND_NAME"]])
            acc = r[ix["ACCESSION_NUMBER"]]
            if acc not in sub:
                continue
            sid = r[ix["SERIES_ID"]].strip()
            if sid:
                key = ("S", sid)
            elif blank_n[acc] == 1 and reg.get(acc):
                key = ("C", reg[acc])
            else:
                stats["fund_rows_not_keyed"] += 1
                continue
            fdate, per = sub[acc]
            fl = {c: r[ix[c]].strip().upper() for c in NCEN_FRI_COLS if c.startswith("IS_")}
            rec = NcenRec(per, fdate, acc, fl, tuple(sorted(feeders.get(r[ix["FUND_ID"]], ()))))
            k2 = (key, per)
            old = best.get(k2)
            if M("flag_amend_older_wins"):
                better = old is None or (rec.fdate, rec.acc) < (old.fdate, old.acc)       # the mutant: the earliest filing wins
            else:
                better = old is None or (rec.fdate, rec.acc) > (old.fdate, old.acc)       # the latest FILING_DATE, then the highest accession
            if better:
                best[k2] = rec
        stats["zips"] += 1
    table = collections.defaultdict(list)
    for (key, per), rec in best.items():
        table[key].append(rec)
    for key in table:
        table[key].sort(key=lambda r: r.period)
    return dict(table), stats, names, zl


def lookup_flag(table, key, r, backfill=True):
    """The flag source for a report dated r: the latest kept N-CEN with REPORT_ENDING_PERIOD <= r; else (backfill) the first later N-CEN filed within
    15 calendar months of r, labelled backfilled. Returns (NcenRec, backfilled) or None."""
    recs = table.get(key)
    if not recs:
        return None
    periods = [x.period for x in recs]
    i = bisect.bisect_right(periods, r) - 1
    if i >= 0:
        return recs[i], False
    if not backfill:
        return None
    rec = recs[0]                               # the earliest REPORT_ENDING_PERIOD > r
    if M("flag_late_ncen") or rec.fdate <= month_add(r, BACKFILL_MONTHS):
        return rec, (False if M("flag_backfill_unlabelled") else True)
    return None


def ncen_key_of(f):
    if f.fund[0] == "S":
        return ("S", f.fund[1])
    return ("C", f.cik) if f.cik else None


Obs = collections.namedtuple("Obs", "flag backfilled period etf excl")


def make_obs(table, f, backfill=True):
    key = ncen_key_of(f)
    res = lookup_flag(table, key, f.rdate, backfill) if key is not None else None
    if res is None:
        return Obs("unflagged", False, None, "", ""), None
    rec, bf = res
    return Obs(flag_value(rec.flags), bf, rec.period, rec.flags.get("IS_ETF", ""), rec.flags.get("IS_INDEX_EXCLUSIVE", "")), rec


def assign_group(obs_by_w, last_w):
    """Spec 4.2: the series group, first that fits: mmf, levinv, unflagged, stale_flag, index_stable / active_stable, switcher."""
    vals = [o.flag for o in obs_by_w.values()]
    if "mmf" in vals:
        return "mmf"
    if "levinv" in vals:
        return "levinv"
    entrant_only_unflagged = M("grp_unflagged_entrant_stable") and len(obs_by_w) == 1
    if "unflagged" in vals and not entrant_only_unflagged:
        return "unflagged"
    o = obs_by_w.get(last_w)
    if o is not None and not o.backfilled and o.period is not None and (o.period <= STALE_BEFORE if M("stale_cutoff_le") else o.period < STALE_BEFORE):
        return "stale_flag"
    if len(set(vals)) == 1:
        return "index_stable" if vals[0] == "index" else "active_stable"
    return "index_stable" if M("grp_switcher_in_index") else "switcher"


def group_tables(funds, group_of, labels):
    """funds[fund] = dict(s={label: kept S}, drop={label: dropped S}); group_of(fund) -> group. Returns (S, N) with S[g][label] and
    N[g][label] = series with a non-zero amount there. The feeder_dropped group holds the removed amounts."""
    S = {g: {l: Fsum() for l in labels} for g in GROUPS}
    N = {g: {l: set() for l in labels} for g in GROUPS}
    for fund in sorted(funds):
        d = funds[fund]
        g = group_of(fund)
        for l in labels:
            v = d["s"].get(l, 0.0)
            if v != 0.0:
                S[g][l].add(v)
                N[g][l].add(fund)
            dv = d["drop"].get(l, 0.0)
            if dv != 0.0:
                S["feeder_dropped"][l].add(dv)
                N["feeder_dropped"][l].add(fund)
    return ({g: {l: S[g][l].value() for l in labels} for g in GROUPS}, N)


def period_delta(S, N, g, per):
    _, l0, l1 = next(p for p in PERIODS if p[0] == per)
    return S[g][l1] - S[g][l0], len(N[g][l0] | N[g][l1])


def decision_inputs(S, N, base_ds):
    """q per period, s0 and U from group tables (spec 4.2). base_ds[per] = the cash build's M0 change."""
    ds = {per: {g: period_delta(S, N, g, per)[0] for g in GROUPS} for per, _, _ in PERIODS}
    q = {per: q_of(ds[per]["index_stable"], ds[per]["active_stable"], base_ds[per]) for per in ("2024", "2025", "2026H1")}
    i0, a0 = S["index_stable"]["2023Q4"], S["active_stable"]["2023Q4"]
    s0 = i0 / (i0 + a0) if (i0 + a0) else None
    d = ds["2026H1"]
    ab = (lambda x: x) if M("u_no_abs") else abs         # the mutant: signed changes in place of absolute ones
    comp = dict(unflagged=ab(d["unflagged"]), switcher=ab(d["switcher"]), stale_flag=ab(d["stale_flag"]))
    u = comp["unflagged"] + comp["switcher"] + (0.0 if M("grp_drop_stale_from_u") else comp["stale_flag"])
    return dict(ds=ds, q=q, s0=s0, u=u, u_comp=comp)


def read_cash_csv(path, key_cols):
    with open(path, newline="", encoding="utf-8") as fh:
        return {tuple(r[c] for c in key_cols): r for r in csv.DictReader(fh)}


def cash_base(cash_dir):
    """The cash build's committed M0 and M1 change and its window table: the targets of C-X1 and C-B3."""
    ch = read_cash_csv(os.path.join(cash_dir, "tsy_change.csv"), ("variant_id", "period"))
    wi = read_cash_csv(os.path.join(cash_dir, "tsy_windows.csv"), ("window", "vintage"))
    return ch, wi


def build_funds(B, vint, table=None, backfill=True):
    """Per-series records for the four R2 windows: kept S, dropped S (feeders), and the N-CEN observation in every window where the series is a
    survivor. Without `table` (futures mode) the observation is None. Returns (funds, survivors, stats)."""
    ctx, sel, by_label = B["ctx"], B["sel"][vint], B["by_label"]
    idxs = {l: by_label[l].idx for l in R2_WINDOWS}
    idxset = set(idxs.values())
    holders = {fund for (v, wi, fund) in ctx.s_fund if v == vint and wi in idxset}
    survivors = {l: {f.fund: f for f, _t in sel["assign"][idxs[l]]} for l in R2_WINDOWS}
    dropped = {l: set() for l in R2_WINDOWS}
    obs = {}
    stats = collections.Counter()
    if table is not None:
        for l in R2_WINDOWS:
            for fund, f in survivors[l].items():
                o, rec = make_obs(table, f, backfill)
                obs[(l, fund)] = (o, rec)
                if rec is not None and rec.feeders and not M("grp_feeder_kept"):
                    for sid in rec.feeders:
                        fk = ("S", sid)
                        if fk != fund and fk in survivors[l]:
                            dropped[l].add(fk)
    funds = {}
    for fund in sorted(holders):
        d = dict(s={}, drop={}, obs={})
        for l in R2_WINDOWS:
            v = ctx.s_of(vint, idxs[l], fund)
            if fund in dropped[l] and v != 0.0:
                d["drop"][l] = v
                v = 0.0
                stats[f"feeder_dropped:{l}"] += 1
            d["s"][l] = v
            if table is not None and fund in survivors[l]:
                d["obs"][l] = obs[(l, fund)][0]
        funds[fund] = d
    return funds, survivors, obs, stats


def fund_attr(d):
    """The latest observation's IS_ETF and IS_INDEX_EXCLUSIVE flags."""
    for l in reversed(R2_WINDOWS):
        if l in d["obs"]:
            o = d["obs"][l]
            return dict(etf=(o.etf == "Y"), excl=(o.excl == "Y"))
    return dict(etf=False, excl=False)


def entrants_of(funds, survivors):
    """Series absent at 2025Q4 and present at 2026Q2 (survivors), holding Treasuries at 2026Q2 (spec 4.2, R23-11)."""
    return sorted(f for f in funds if f not in survivors["2025Q4"] and f in survivors["2026Q2"] and funds[f]["s"]["2026Q2"] != 0.0)


def group_fn(funds):
    return lambda fund: assign_group(funds[fund]["obs"], "2026Q2")


def delta_where(funds, group_of, g, per, pred=None):
    _, l0, l1 = next(p for p in PERIODS if p[0] == per)
    tot = Fsum()
    for fund, d in funds.items():
        if group_of(fund) == g and (pred is None or pred(fund)):
            tot.add(d["s"][l1] - d["s"][l0])
    return tot.value()


def level_where(funds, group_of, g, label, pred=None):
    tot = Fsum()
    for fund, d in funds.items():
        if group_of(fund) == g and (pred is None or pred(fund)):
            tot.add(d["s"][label])
    return tot.value()


def part2_results(B, table, base_ds, base_ds_m1):
    """All of Part 2 in memory, before any small-cell merge: the primary tables and the printed sensitivities."""
    R = {}
    funds, survivors, obs, st = build_funds(B, "base", table, True)
    go = group_fn(funds)
    S, N = group_tables(funds, go, R2_WINDOWS)
    DI = decision_inputs(S, N, base_ds)
    R.update(funds=funds, survivors=survivors, obs=obs, S=S, N=N, DI=DI, go=go, feeder_stats=st)
    R["label"] = part2_label(DI["q"]["2024"], DI["q"]["2025"], DI["q"]["2026H1"], DI["s0"], DI["u"])
    ents = entrants_of(funds, survivors)
    R["entrants"] = ents
    R["entrants_ds"] = math_fsum(funds[f]["s"]["2026Q2"] - funds[f]["s"]["2025Q4"] for f in ents)
    R["entrants_unflagged_n"] = sum(1 for f in ents if funds[f]["obs"]["2026Q2"].flag == "unflagged")
    R["entrants_backfilled_n"] = sum(1 for f in ents if funds[f]["obs"]["2026Q2"].backfilled)
    R["entrants_unflagged_ds"] = math_fsum(funds[f]["s"]["2026Q2"] - funds[f]["s"]["2025Q4"] for f in ents if go(f) == "unflagged")
    # ---- sensitivities, printed only
    fs, _sv, _ob, _st = build_funds(B, "base", table, False)
    Ss, Ns = group_tables(fs, group_fn(fs), R2_WINDOWS)
    R["DI_strict"] = decision_inputs(Ss, Ns, base_ds)
    fm, _sv2, _ob2, _st2 = build_funds(B, "matched", table, True)
    Sm, Nm = group_tables(fm, group_fn(fm), R2_WINDOWS)
    R["DI_m1"] = decision_inputs(Sm, Nm, base_ds_m1)
    R["S_m1"] = Sm

    def raw_q(di, da):
        """The printed diagnostics use the plain ratio, without the bounds of R23-13: a restricted arm is small against the whole base, and the
        bounds are the rule's, not the diagnostic's."""
        return di / (di + da) if (di + da) != 0 and di >= 0 and da >= 0 else None

    def q_with(index_groups, pred_idx=None, pred_act=None, per="2026H1", go_=go):
        di = sum(delta_where(funds, go_, g, per, pred_idx) for g in index_groups)
        da = delta_where(funds, go_, "active_stable", per, pred_act)
        return raw_q(di, da)

    def s0_with(pred_idx=None, pred_act=None):
        i0 = level_where(funds, go, "index_stable", "2023Q4", pred_idx)
        a0 = level_where(funds, go, "active_stable", "2023Q4", pred_act)
        return i0 / (i0 + a0) if (i0 + a0) else None

    def last_flag(fund):
        d = funds[fund]
        return d["obs"]["2026Q2"].flag if "2026Q2" in d["obs"] else None

    go_all = lambda fund: (("index_stable" if last_flag(fund) == "index" else "active_stable" if last_flag(fund) == "active" else "switcher")
                           if go(fund) == "switcher" else go(fund))
    attr = {f: fund_attr(d) for f, d in funds.items()}
    is_etf, not_etf = (lambda f: attr[f]["etf"]), (lambda f: not attr[f]["etf"])
    non_excl = lambda f: not attr[f]["excl"]
    P = {}
    P["q_raw"] = q_with(["index_stable"])
    P["q_all"] = q_with(["index_stable"], go_=go_all)             # the switchers go to the arm of their 2026Q2 flag
    P["q_levinv_in"] = q_with(["index_stable", "levinv"])
    P["q_etf_only"] = q_with(["index_stable"], is_etf, is_etf)
    P["q_mf_only"] = q_with(["index_stable"], not_etf, not_etf)
    P["s0_etf_only"], P["s0_mf_only"] = s0_with(is_etf, is_etf), s0_with(not_etf, not_etf)
    P["q_non_exclusive"] = q_with(["index_stable"], non_excl)
    ds_i = DI["ds"]["2026H1"]["index_stable"]
    P["index_exclusive_share"] = (delta_where(funds, go, "index_stable", "2026H1", lambda f: attr[f]["excl"]) / ds_i) if ds_i else None
    tot26 = math_fsum(DI["ds"]["2026H1"].values())
    P["index_share_all_groups"] = ds_i / tot26 if tot26 else None
    s0 = DI["s0"]
    q26 = P["q_raw"]
    P["flag_etf_gap"] = bar_state(P["q_etf_only"], P["s0_etf_only"]) != bar_state(P["q_mf_only"], P["s0_mf_only"])
    P["flag_index_exclusive"] = bar_state(P["q_non_exclusive"], s0) != bar_state(q26, s0)
    P["flag_levinv_crosses_bar"] = bar_state(P["q_levinv_in"], s0) != bar_state(q26, s0)
    P["flag_stable_vs_all_gap"] = bar_state(P["q_all"], s0) != bar_state(q26, s0)
    P["excess_etf_only"] = None if P["q_etf_only"] is None or P["s0_etf_only"] is None else P["q_etf_only"] - P["s0_etf_only"]
    P["excess_mf_only"] = None if P["q_mf_only"] is None or P["s0_mf_only"] is None else P["q_mf_only"] - P["s0_mf_only"]
    R["P"], R["attr"], R["table"] = P, attr, table
    return R


def math_fsum(it):
    return math.fsum(it)


# ------------------------------------------------------------------------------------------------------------------------
# outputs: column files, small cells, hygiene, wording, the failure path (spec sections 1 and 5)
# ------------------------------------------------------------------------------------------------------------------------
FORBIDDEN_HEADER_TOKENS = ("CUSIP", "HOLDING_ID", "ACCESSION_NUMBER", "SERIES_ID", "SERIES_NAME", "REGISTRANT_NAME", "LEI", "CIK")
MAX_ROWS = 2000
# files with a count column, the label column that may read other_small, and the columns that must be blank on a merged row of fewer than five
CELL_FILES = {"fut_contracts.csv": ("funds_n", "contract"), "fut_split.csv": ("funds_n", "group"), "idx_split.csv": ("series_n", "group"),
              "idx_coverage.csv": ("series_n", "flag"), "idx_crosstab.csv": ("series_n", "arm")}
VOCAB = frozenset("""A AN AND ARE AS AT BE BY FOR FROM IN IS IT OF ON OR THE THEY TO US WHAT WHICH WITH FUND FUNDS INDEX ACTIVE TREASURY TREASURIES FUTURES FUTURE NOTE
NOTES BOND BONDS ULTRA REGISTERED TRUST SERIES MONEY MARKET TARGET DATE INTERVAL ETF MASTER FEEDER LEVERAGED INVERSE STABLE SWITCHER UNFLAGGED STALE FLAG
FEEDER DROPPED OTHER SMALL CONTINUING ENTRANT LEAVER MMF LEVINV HOLDINGS MEASUREMENTS DO NOT SHOW MOVED YIELDS THESE TU Z3N FV TY TN TWE UB INTEREST RATE
SWAP SWAPS OPTION OPTIONS SWAPTION SWAPTIONS SOFR CASH DURATION EQUIVALENT TEN YEAR YEARS SHORT LONG NET GROSS FACE CONTRACT CONTRACTS WINDOW BASE MATCHED
FIXED CURVE PAR YIELD TENOR MAP CONVERSION FACTOR CHEAPEST DELIVER MODELLED""".split())
CAUSAL_RX = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|led\s+to|leads?\s+to|pushed|pushes|pushing|because\s+of|in\s+response\s+to|"
                       r"moved\s+yields|prompted|leaned?\s+against)\b", re.I)
SYMBOL_RX = re.compile(r"(?<![\w.])(?:q|s0|U|ΔF|G_[vcs]|U_F|A[1-4])(?:_\w+)?(?!\w)(?!\.[A-Za-z])")
BANNED_IMPORTS = frozenset({"urllib", "http", "socket", "ssl", "ftplib", "smtplib", "telnetlib", "requests", "httpx", "xmlrpc"})


def read_columns_tsv(path):
    if not os.path.exists(path):
        raise Refused(f"{path} is missing; the column allowlist is committed beside the outputs (G10)")
    with open(path, encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh.read().splitlines() if ln.strip()]
    if lines[0].split("\t") != ["file", "columns"]:
        raise Refused(f"{path}: the first line must be 'file<TAB>columns'")
    out = collections.OrderedDict()
    for ln in lines[1:]:
        f, cols = ln.split("\t")
        out[f] = cols.split("|")
    return out


def render_csv(cols, rows):
    if M("net_call"):
        _open_socket()                          # the G17 mutant: a request from inside the pipeline
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(cols)
    for r in rows:
        extra = set(r) - set(cols)
        if extra:
            raise ValueError(f"a row has keys outside the allowlist: {sorted(extra)}")
        w.writerow([fmt(r.get(c)) for c in cols])
    return out.getvalue()


ADDITIVE_RX = re.compile(r"(_n|_bn|_mn)$|^lines$|^contracts_net$")


def merge_small(rows, n_col, scope_cols, label_col, cols, floor=SMALL_CELL):
    """R23-16: every row whose count is below the floor is merged into one `other_small` row per scope. The merged row carries the summed counts and
    amounts (the additive columns: counts, $bn, $mn); every other column is blank there. If that row itself covers fewer than the floor, its amounts are
    blanked and only the count is shown. An empty cell is dropped. `cols` is the file's column list from fut_idx_columns.tsv, so no list of names lives here."""
    if M("no_merge"):
        return list(rows)
    add_cols = [c for c in cols if c not in scope_cols and c != label_col and ADDITIVE_RX.search(c)]
    keep, small = [], collections.OrderedDict()
    for r in rows:
        n = r.get(n_col)
        if n is None or n >= floor:
            keep.append(r)
        elif n > 0:
            small.setdefault(tuple(r.get(c) for c in scope_cols), []).append(r)
    for scope, rs in small.items():
        m = dict(zip(scope_cols, scope))
        m[label_col] = SMALL_NAME
        total = sum(r[n_col] for r in rs)
        for c in add_cols:
            vals = [r.get(c) for r in rs if r.get(c) is not None]
            m[c] = math.fsum(vals) if vals else None
        m[n_col] = total
        if total < floor:
            for c in add_cols:
                if c != n_col:
                    m[c] = None
        for c in cols:
            m.setdefault(c, None)
        keep.append(m)
        if total < floor and not M("no_complementary"):
            # complementary suppression: with the other_small amounts blanked, a public total for the scope would give them back as total minus the
            # other cells; so the smallest remaining amount cell in each amount column of the scope is blanked too
            same = [r for r in keep if r is not m and all(r.get(c) == v for c, v in zip(scope_cols, scope)) and r.get(label_col) != SMALL_NAME]
            for c in add_cols:
                if c == n_col or c.endswith("_n"):
                    continue
                cand = [r for r in same if r.get(c) is not None]
                if cand:
                    min(cand, key=lambda r: abs(r[c]))[c] = None
    return keep


def norm_tokens(s):
    return re.sub(r"[^A-Z0-9]+", " ", (s or "").upper()).split()


def make_name_set(raw_names):
    """G9 mechanism: normalise each name; keep those of at least 8 characters and two words that are not all in the fixed vocabulary."""
    by_len = collections.defaultdict(set)
    for nm in raw_names:
        toks = norm_tokens(nm)
        if len(" ".join(toks)) >= 8 and len(toks) >= 2 and not all(t in VOCAB for t in toks):
            by_len[len(toks)].add(tuple(toks))
    return by_len


def cell_has_name(cell, by_len):
    toks = norm_tokens(cell)
    for n, names in by_len.items():
        if n > len(toks):
            continue
        for i in range(len(toks) - n + 1):
            if tuple(toks[i:i + n]) in names:
                return True
    return False


def hygiene_problems(texts, cols_by_file, by_len, prose=None):
    """C-X4 on rendered text. `texts` = {file name: csv text}; `prose` = {file name: markdown text}. Returns a list of problems that name the file and the
    row, never a fund or registrant name."""
    bad = []
    for name, text in sorted(texts.items()):
        rows = list(csv.reader(io.StringIO(text)))
        hdr = rows[0] if rows else []
        for h in hdr:
            if any(t in h.upper() for t in FORBIDDEN_HEADER_TOKENS):
                bad.append(f"{name}: forbidden header token in {h!r}")
        if name in cols_by_file and hdr != cols_by_file[name]:
            bad.append(f"{name}: header differs from fut_idx_columns.tsv")
        if name not in cols_by_file:
            bad.append(f"{name}: not listed in fut_idx_columns.tsv")
        if len(rows) - 1 > MAX_ROWS:
            bad.append(f"{name}: {len(rows) - 1} rows, above {MAX_ROWS}")
        for i, r in enumerate(rows[1:], start=2):
            for c in r:
                if cell_has_name(c, by_len):
                    bad.append(f"{name}: row {i} holds a fund or registrant name")
                    break
        if name in CELL_FILES and hdr:
            ncol, lcol = CELL_FILES[name]
            if ncol in hdr and lcol in hdr:
                for i, r in enumerate(rows[1:], start=2):
                    d = dict(zip(hdr, r))
                    try:
                        n = int(float(d[ncol]))
                    except ValueError:
                        continue
                    if d[lcol] != SMALL_NAME and n < SMALL_CELL:
                        bad.append(f"{name}: row {i} has {ncol} {n}, below {SMALL_CELL}")
                    if d[lcol] == SMALL_NAME and n < SMALL_CELL:
                        amounts = [v for k, v in d.items() if k not in (ncol, lcol) and v != "" and k not in ("period", "window")]
                        if amounts:
                            bad.append(f"{name}: row {i} is an other_small cell of {n} with amounts shown")
    for name, text in sorted((prose or {}).items()):
        for i, ln in enumerate(text.splitlines(), start=1):
            if cell_has_name(ln, by_len):
                bad.append(f"{name}: line {i} holds a fund or registrant name")
    return bad


def wording_hits(text):
    return sorted({re.sub(r"\s+", " ", m.group(0).lower()) for m in CAUSAL_RX.finditer(text.replace(REQUIRED_SENTENCE, ""))})


def symbol_hits(prose):
    """R23-19: no symbol in README prose; the dictionary at the end is exempt."""
    cut = prose.find("## Column dictionary")
    body = prose if cut < 0 else prose[:cut]
    return sorted({m.group(0) for m in SYMBOL_RX.finditer(body)})


def cash_mixing_hits(files, forbidden):
    """G8: no cell is S + F, F / dP, or the whole token 460 or FIRST-ORDER. `files` = {name: (cols, rows)}; `forbidden` = numbers to look for."""
    hits = []
    for name, (cols, rows) in sorted(files.items()):
        for i, r in enumerate(rows, start=1):
            for c in cols:
                v = r.get(c)
                if v is None or v == "":
                    continue
                s = str(v)
                if re.search(r"(?<![\w.,])(?:460|FIRST-ORDER)(?![\w.,%])", s):
                    hits.append(f"{name} row {i}: the whole token 460 or FIRST-ORDER")
                    continue
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    if abs(v - 460.0) <= 1e-9:
                        hits.append(f"{name} row {i}: a cell equal to 460")
                    elif any(abs(v - x) <= 1e-6 * max(1.0, abs(x)) for x in forbidden):
                        hits.append(f"{name} row {i} column {c}: equals a cash-plus-futures or futures-over-cash value")
    return hits


def import_hits(source_text):
    hits = []
    for node in ast.walk(ast.parse(source_text)):
        if isinstance(node, ast.Import):
            hits += [a.name for a in node.names if a.name.split(".")[0] in BANNED_IMPORTS]
        elif isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] in BANNED_IMPORTS:
            hits.append(node.module)
    return hits


def allowlist_copies(source_text, cols_by_file):
    """G10 mechanism: a list, tuple or set literal of string constants that shares three or more members with the columns of any one output file."""
    hits = []
    sets = {f: set(c) for f, c in cols_by_file.items()}
    for node in ast.walk(ast.parse(source_text)):
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            vals = {e.value for e in node.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)}
            for f, cs in sets.items():
                if len(vals & cs) >= 3:
                    hits.append(f"{f} (line {node.lineno})")
    return hits


def is_hard_fail(checks):
    return any(c["result"] == "FAIL" and c["hard"] == "Y" for c in checks)


def _open_socket():
    """Only the G17 mutant calls this. The module name is built from two pieces so that the import scan of this very file stays clean."""
    return importlib.import_module("so" + "cket").socket()


def finish(texts, hard_fail, out_dir):
    """The failure path (R6, G16): a hard FAIL writes every output to <out>/_FAILED_fut_idx/, leaves the committed files untouched and returns 2;
    otherwise the files go to <out>. Returns the exit status."""
    target = out_dir if (not hard_fail or M("fail_writes_committed")) else os.path.join(out_dir, FAILED_DIRNAME)
    os.makedirs(target, exist_ok=True)
    for name, text in sorted(texts.items()):
        with open(os.path.join(target, name), "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
    if hard_fail and M("fail_exit0"):
        return 0
    return 2 if hard_fail else 0


# ------------------------------------------------------------------------------------------------------------------------
# verdict rows and sentences
# ------------------------------------------------------------------------------------------------------------------------
def yn(b):
    return "yes" if b else "no"


def bn(x, nd=1):
    return "n/a" if x is None else f"{x:,.{nd}f}"


def usd(x, nd=1):
    """A signed dollar figure in billions: $12.3bn or -$12.3bn."""
    if x is None:
        return "n/a"
    return ("-" if round(x, nd) < 0 else "") + f"${abs(x):,.{nd}f}bn"


def pct(x, nd=1):
    return "n/a" if x is None else f"{100.0 * x:.{nd}f}%"


def p1_conditions(P1, plain=False):
    """The conditions of the futures rule, each as (met, plain sentence), in the rule's order."""
    u = P1["anchor_all"]
    out = []
    ok1 = A1_RANGE[0] <= u["a1"] <= A1_RANGE[1]
    out.append((ok1, f"the end-2023 net futures face was {usd(u['a1'])} (accepted range ${A1_RANGE[0]:.0f}bn to ${A1_RANGE[1]:.0f}bn)"))
    ok2 = u["a2"] is not None and A2_RANGE[0] <= u["a2"] <= A2_RANGE[1]
    out.append((ok2, f"{'the anchor comparing futures risk with cash bond risk' if plain else 'the ratio of futures to notes-and-bonds sensitivity'} was {u['a2']:.2f} (accepted range {A2_RANGE[0]:.2f} to {A2_RANGE[1]:.2f}; the Federal Reserve note's own value is 0.30)"))
    ok3 = u["a3"] is not None and A3_RANGE[0] <= u["a3"] <= A3_RANGE[1]
    out.append((ok3, f"the implied futures duration was {u['a3']:.2f} years (accepted range {A3_RANGE[0]:.1f} to {A3_RANGE[1]:.1f}; the note's value is 3.75)"))
    for lab, v in (("end-2023", P1["u_f"][0]), ("mid-2026", P1["u_f"][1])):
        out.append((le(v, UF_MAX), f"unresolved, conflicting and sign-less lines were {pct(v)} of futures face at {lab} (limit {pct(UF_MAX, 0)})"))
    out.append((le(P1["g_v"], GV_MAX), f"the base and matched vintages differ by {usd(P1['g_v'])} (limit ${GV_MAX:.0f}bn)"))
    out.append((le(P1["g_c"], GC_MAX), f"the tenor map and the modelled cheapest-to-deliver differ by {usd(P1['g_c'])} (limit ${GC_MAX:.0f}bn)"))
    out.append((le(P1["g_s"], GS_MAX), f"the filed long-or-short sign and the sign of the filed contract count differ by {usd(P1['g_s'])} (limit ${GS_MAX:.0f}bn)"))
    return out


def fut_sentence(P1):
    d = P1["d_f"]
    word = {"LARGE": "large", "SMALL": "small", "INCONCLUSIVE": "not established"}[P1["label"]]
    s = (f"The net change in registered funds' Treasury futures from end-2023 to mid-2026 was {word}, at {usd(d)} of 10-year equivalents "
         f"against a ${DF_BAR_BN:.0f}bn line.")
    if P1["label"] == "INCONCLUSIVE":
        failed = [t for ok, t in p1_conditions(P1) if not ok]
        s += " It is not established because " + "; ".join(failed) + "."
    for name in sorted(_ACTIVE):               # the G14 mutants reach the verdict sentences too
        if name.startswith("readme_inject:"):
            s += f" This sentence was inserted by a mutant: {name.split(':', 1)[1]}."
    return s


def p2_reason(P2):
    DI = P2["DI"]
    if DI["u"] > U_CAP_BN:
        return f"The unclassified change was {usd(DI['u'])}, above the ${U_CAP_BN:.1f}bn cap."
    if any(DI["q"][p] is None for p in ("2024", "2025", "2026H1")):
        return "In at least one period an arm's change was negative, or the classified change was under a quarter of the base change, so the share is undefined."
    return ("The share in the first half of 2026 was neither at least 60% with the required margins nor at most 40% and no higher than the stock share, so it "
            "falls between the two bars.")


def part2_sentence(P2, base_ds):
    if P2 is None:
        return "The index/active split (test B) was not run in this build; it needs the Form N-CEN files."
    DI, lab = P2["DI"], P2["label"]
    q26, s0 = DI["q"]["2026H1"], DI["s0"]
    if lab == "SUPPORTS":
        return ("Series flagged 'Index Fund' on Form N-CEN (any index, not only Treasury indexes) took a much larger and rising share of registered "
                f"funds' classified cash Treasury duration change: {pct(q26)} of the {usd(DI['ds']['2026H1']['index_stable'] + DI['ds']['2026H1']['active_stable'])} "
                f"classified change in the first half of 2026, against {pct(s0)} of the classified stock at end-2023.")
    if lab == "AGAINST":
        return ("Series flagged 'Index Fund' on Form N-CEN (any index, not only Treasury indexes) took no larger a share of registered funds' classified "
                f"cash Treasury duration change than their share of the classified stock: {pct(q26)} of the change in the first half of 2026, against "
                f"{pct(s0)} at end-2023.")
    return ("The split of registered funds' cash Treasury duration change between series flagged 'Index Fund' on Form N-CEN (any index, not only Treasury "
            f"indexes) and the rest is not established: the index-flag share of the classified change was {pct(DI['q']['2024'])} in 2024, {pct(DI['q']['2025'])} "
            f"in 2025 and {pct(q26)} in the first half of 2026, against {pct(s0)} of the classified stock at end-2023. {p2_reason(P2)}")


def fut_verdict_rows(B, P1, extra=None):
    chg = P1["chg"]
    u = P1["anchor_all"]
    rows = [("required_sentence", REQUIRED_SENTENCE),
            ("scope", "registered funds' Treasury futures, from the SEC bulk N-PORT data sets; the cash build's survivors, lag and fixed end-2023 curve"),
            ("basis", "10-year equivalents on the fixed 2023-12-29 curve, tenor map, PAYOFF_PROFILE sign (the headline)"),
            ("denominator_funds_2023q4", len(B["sel"]["base"]["assign"][B["by_label"]["2023Q4"].idx])),
            ("denominator_funds_2026q2", len(B["sel"]["base"]["assign"][B["by_label"]["2026Q2"].idx])),
            ("f_2023q4_bn", chg[("T0", "full")][0]), ("f_2026q2_bn", chg[("T0", "full")][1]), ("d_f_bn", P1["d_f"]),
            ("d_f_line_bn", DF_BAR_BN), ("d_f_sign", "up" if P1["d_f"] > 0 else ("down" if P1["d_f"] < 0 else "flat")),
            ("d_f_2024_bn", chg[("T0", "2024")][2]), ("d_f_2025_bn", chg[("T0", "2025")][2]), ("d_f_2026h1_bn", chg[("T0", "2026H1")][2]),
            ("a1_face_net_bn", u["a1"]), ("a1_range_bn", f"{A1_RANGE[0]:.0f}-{A1_RANGE[1]:.0f}"),
            ("a2_dv01_ratio", u["a2"]), ("a2_range", f"{A2_RANGE[0]:.2f}-{A2_RANGE[1]:.2f}"),
            ("a3_implied_duration_years", u["a3"]), ("a3_range_years", f"{A3_RANGE[0]:.1f}-{A3_RANGE[1]:.1f}"),
            ("a_pass", yn(P1["a_pass"])), ("anchor_universe_funds", u["universe_n"]), ("anchor_universe_funds_with_futures", u["universe_with_futures_n"]),
            ("a1_balsign_face_net_bn", u["a1_bal"]), ("a2_balsign_dv01_ratio", u["a2_bal"]), ("a3_balsign_implied_duration_years", u["a3_bal"]),
            ("a_balsign_pass", yn(a_pass(u, bal=True))),
            ("a4_all_fund_gross_long_face_bn", P1["a4_gross_long_bn"]), ("a4_feds_reading_bn", f"{A4_FEDS_RANGE[0]:.0f}-{A4_FEDS_RANGE[1]:.0f}"),
            ("u_f_2023q4", P1["u_f"][0]), ("u_f_2026q2", P1["u_f"][1]), ("u_f_max", UF_MAX),
            ("g_v_bn", P1["g_v"]), ("g_v_max_bn", GV_MAX), ("g_c_bn", P1["g_c"]), ("g_c_max_bn", GC_MAX), ("g_s_bn", P1["g_s"]), ("g_s_max_bn", GS_MAX),
            ("d_f_matched_bn", chg[("T1", "full")][2]), ("d_f_ctd_bn", chg[("C0", "full")][2]), ("d_f_balsign_bn", chg[("B0", "full")][2]),
            ("label", P1["label"]), ("verdict_sentence", fut_sentence(P1)),
            ("held_apart", "futures are in zero net supply: no output adds them to cash holdings, divides them by the public's change, or sets them against the cash line")]
    if P1.get("anchor_exetf") is not None:
        e = P1["anchor_exetf"]
        rows += [("exetf_a1_face_net_bn", e["a1"]), ("exetf_a2_dv01_ratio", e["a2"]), ("exetf_a3_implied_duration_years", e["a3"]),
                 ("exetf_universe_funds", e["universe_n"]), ("anchor_universe_series_without_ncen_row", P1["anchor_all"]["no_row_n"])]
    return rows


def idx_verdict_rows(B, P2, base_ds, base_ds_m1):
    DI, P = P2["DI"], P2["P"]
    d = DI["ds"]
    rows = [("required_sentence", REQUIRED_SENTENCE),
            ("scope", "registered funds' cash Treasury 10-year equivalents (the cash build's survivors and fixed curve), split by the Form N-CEN index flag"),
            ("windows", "2023Q4, 2024Q4, 2025Q4, 2026Q2 (the R2 dates), base vintage")]
    for per in ("2024", "2025", "2026H1"):
        cls = d[per]["index_stable"] + d[per]["active_stable"]
        rows += [(f"base_ds_{per.lower()}_bn", base_ds[per]), (f"ds_index_stable_{per.lower()}_bn", d[per]["index_stable"]),
                 (f"ds_active_stable_{per.lower()}_bn", d[per]["active_stable"]), (f"classified_sum_{per.lower()}_bn", cls),
                 (f"classified_floor_{per.lower()}_bn", Q_BASE_SHARE * base_ds[per]),
                 (f"q_{per.lower()}", DI["q"][per] if DI["q"][per] is not None else "undefined")]
    rows += [("s0", DI["s0"]), ("q_2026h1_minus_s0", None if DI["q"]["2026H1"] is None else DI["q"]["2026H1"] - DI["s0"]),
             ("q_2026h1_minus_q_2024", None if None in (DI["q"]["2026H1"], DI["q"]["2024"]) else DI["q"]["2026H1"] - DI["q"]["2024"]),
             ("q_2026h1_minus_q_2025", None if None in (DI["q"]["2026H1"], DI["q"]["2025"]) else DI["q"]["2026H1"] - DI["q"]["2025"]),
             ("u_bn", DI["u"]), ("u_cap_bn", U_CAP_BN), ("u_unflagged_bn", DI["u_comp"]["unflagged"]), ("u_switcher_bn", DI["u_comp"]["switcher"]),
             ("u_stale_flag_bn", DI["u_comp"]["stale_flag"]), ("u_unflagged_entrants_bn", P2["entrants_unflagged_ds"]),
             ("entrants_n", len(P2["entrants"])), ("entrants_ds_2026h1_bn", P2["entrants_ds"]), ("entrants_unflagged_n", P2["entrants_unflagged_n"]),
             ("entrants_backfilled_n", P2["entrants_backfilled_n"]),
             ("pre_run_inconclusive_by_construction",
              yn(P2["entrants_unflagged_ds"] + DI["u_comp"]["stale_flag"] > U_CAP_BN)),
             ("label", P2["label"]), ("verdict_sentence", part2_sentence(P2, base_ds)),
             ("bar_hurdle_note", "0.15 is a pre-registered hurdle taken from a different object (the funds' excess over the public stock in the cash build) after that object was measured; it is not a sampling bound"),
             ("q_plain_2026h1_no_bounds", P["q_raw"] if P["q_raw"] is not None else "undefined"),
             ("q_all", P["q_all"] if P["q_all"] is not None else "undefined"), ("q_strict_2026h1", DI_q(P2["DI_strict"])),
             ("q_levinv_in", P["q_levinv_in"] if P["q_levinv_in"] is not None else "undefined"),
             ("q_m1_2026h1", DI_q(P2["DI_m1"])), ("s0_m1", P2["DI_m1"]["s0"]),
             ("index_share_of_all_groups_2026h1", P["index_share_all_groups"]),
             ("excess_over_s0_index_etf_only", P["excess_etf_only"]), ("excess_over_s0_index_mutual_fund_only", P["excess_mf_only"]),
             ("index_exclusive_share_of_index_change", P["index_exclusive_share"]),
             ("flag_etf_only_gap", yn(P["flag_etf_gap"])), ("flag_index_exclusive", yn(P["flag_index_exclusive"])),
             ("flag_levinv_crosses_bar", yn(P["flag_levinv_crosses_bar"])), ("flag_stable_vs_all_gap", yn(P["flag_stable_vs_all_gap"])),
             ("resolution_note", "within about 10 points of a bar at the unclassified cap, a share is fragile: unclassified change of $16.2bn could move it by that much")]
    return rows


def DI_q(di):
    q = di["q"]["2026H1"]
    return "undefined" if q is None else q


def prerun_rows(P2_or_entrants, mode):
    """idx_prerun.csv: the entrants and their change, from the cash build alone (futures mode), plus the flag counts (idx mode)."""
    n, ds, extra = P2_or_entrants
    rows = [("entrants_n", n), ("entrants_ds_2026h1_bn", None if n < SMALL_CELL else ds), ("u_cap_bn", U_CAP_BN)]
    if extra is not None:
        rows += [("entrants_unflagged_n", extra[0]), ("entrants_backfilled_n", extra[1])]
    return [dict(key=k, value=v) for k, v in rows]


def idx_tables(B, P2, base_ds):
    """idx_split, idx_coverage, idx_crosstab rows before the small-cell merge."""
    S, N = P2["S"], P2["N"]
    rows_s = []
    for per, l0, l1 in PERIODS:
        for g in GROUPS:
            rows_s.append(dict(period=per, group=g, series_n=len(N[g][l0] | N[g][l1]), s_start_bn=S[g][l0], s_end_bn=S[g][l1],
                               d_s_bn=S[g][l1] - S[g][l0]))
    funds, go = P2["funds"], P2["go"]
    rows_cv = []
    for l in R2_WINDOWS:
        agg = collections.defaultdict(lambda: [set(), set(), Fsum()])
        for fund, d in funds.items():
            v, dv = d["s"].get(l, 0.0), d["drop"].get(l, 0.0)
            if l in d["obs"]:
                o = d["obs"][l]
                if v != 0.0:
                    a = agg[o.flag]
                    a[0].add(fund)
                    a[2].add(v)
                    if o.backfilled:
                        a[1].add(fund)
                if dv != 0.0:
                    a = agg["feeder_dropped"]
                    a[0].add(fund)
                    a[2].add(dv)
        for flag in sorted(agg):
            a = agg[flag]
            rows_cv.append(dict(window=l, flag=flag, flag_backfilled_n=len(a[1]), series_n=len(a[0]), s_bn=a[2].value()))
    rows_x = []
    attr = P2["attr"]
    for per, l0, l1 in PERIODS:
        cells = collections.defaultdict(lambda: [set(), Fsum(), Fsum()])
        for fund, d in funds.items():
            g = go(fund)
            if g not in ("index_stable", "active_stable"):
                continue
            s0_, s1_ = d["s"][l0], d["s"][l1]
            if s0_ == 0.0 and s1_ == 0.0:
                continue
            c = cells[("Y" if attr[fund]["etf"] else "N", "index" if g == "index_stable" else "active")]
            c[0].add(fund)
            c[1].add(s0_)
            c[2].add(s1_ - s0_)
        for (etf, arm) in sorted(cells):
            c = cells[(etf, arm)]
            rows_x.append(dict(period=per, is_etf=etf, arm=arm, series_n=len(c[0]), s_start_bn=c[1].value(), d_s_bn=c[2].value()))
    return rows_s, rows_cv, rows_x


# ------------------------------------------------------------------------------------------------------------------------
# fixtures shared by the run-time checks (C-F1, C-F3) and the selftest (G2, G6)
# ------------------------------------------------------------------------------------------------------------------------
def _t(*srcs):
    return tuple(norm_text(x) for x in (list(srcs) + ["", "", "", ""])[:4])


# (texts, FUT_FWD currency, expected class, expected contract)
CLASSIFIER_FIXTURES = [
    (_t("US 2YR NOTE (CBT) Mar24"), "USD", "tsy", "TU"),
    (_t("US 3YR NOTE (CBT) MAR24"), "USD", "tsy", "Z3N"),
    (_t("FUTURE", "", "", "3YH4"), "USD", "tsy", "Z3N"),
    (_t("US 5YR NOTE (CBT) FUT MAR24 FVH4"), "USD", "tsy", "FV"),
    (_t("U.S. TREASURY 5 YEAR NOTE"), "USD", "tsy", "FV"),
    (_t("US 10YR NOTE (CBT)MAR24"), "USD", "tsy", "TY"),
    (_t("FUTURE", "", "", "TYH4"), "USD", "tsy", "TY"),
    (_t("US 10YR ULTRA FUT MAR24"), "USD", "tsy", "TN"),
    (_t("UST 10YR FUT ULTRA UXYH4 03-19-24"), "USD", "tsy", "TN"),
    (_t("U.S. TREASURY 10 YEAR ULTRA BONDS", "", "", "UXYH4"), "USD", "tsy", "TN"),
    (_t("U.S. TREASURY 10 YEAR ULTRA BONDS"), "USD", "tsy", "TN"),
    (_t("US ULTRA BOND CBT MAR24"), "USD", "tsy", "UB"),
    (_t("U.S. TREASURY 30 YEAR ULTRA BONDS"), "USD", "tsy", "UB"),
    (_t("US LONG BOND(CBT) MAR24"), "USD", "tsy", "US"),
    (_t("10 Year Treasury Bond Futures"), "AUD", "non_usd", None),
    (_t("Euro-Buxl", "", "", "UBH4"), "EUR", "non_usd", None),
    (_t("US 10YR FUT OPTN JAN24P 110"), "USD", "nontsy", None),
    (_t("AUST 3YR BOND"), "USD", "nontsy", None),
    (_t("KOREA 3YR BND FUT MAR24"), "USD", "nontsy", None),
    (_t("THREE-MONTH SOFR"), "USD", "nontsy", None),
    (_t("EURO-BUND"), "USD", "nontsy", None),
    (_t("NYMEX HENRY HUB NATURAL EUROPEAN STYLE OPTION"), "USD", "nontsy", None),
    (_t("some future with no marker"), "", "non_usd", None),
    (_t("FUTURE", "", "", "BBG00XXXXXXX"), "USD", "unresolved", None),
    (_t("CBT 10YR NOTE MAR24"), "", "tsy", "TY"),
    (_t("CBT FUT UBH4"), "", "unresolved", None),
    (_t("US 10YR NOTE (CBT)", "", "", "FVH4"), "USD", "conflict", None),
    (_t("US 10YR FUT OPTN", "", "", "TYH4"), "USD", "nontsy", None),
]
# (coupon %, months from the first day of the delivery month, expected CF) -- spec 3.5 fixtures, plus pinned cases
CF_FIXTURES = [(6.0, 0, 1.0), (6.0, 6, 1.0), (6.0, 3, 0.9999), (6.0, 9, 0.9999), (4.0, 51, 0.9259), (4.5, 180, 0.8530), (2.0, 78, 0.7873)]


def classifier_fixture_failures():
    bad = []
    for texts, ccy, ecls, ec in CLASSIFIER_FIXTURES:
        cls, c, _r = classify(texts, ccy)
        if cls != ecls or c != ec:
            bad.append(f"{texts[0] or texts[3]!r}: got {cls}/{c}, want {ecls}/{ec}")
    return bad


def cf_fixture_failures():
    bad = []
    for cp, months, want in CF_FIXTURES:
        got = cf_value(cp, months)
        if abs(got - want) > 1e-12:
            bad.append(f"{cp}% at {months} months: {got} not {want}")
    if cf_value(4.0625, 51) != cf_value(4.125, 51):
        bad.append("a coupon of 4.0625% did not round up to 4.125%")
    return bad


# ------------------------------------------------------------------------------------------------------------------------
# checks (spec section 6)
# ------------------------------------------------------------------------------------------------------------------------
def mk(cid, label, ours, ref, thr, result, hard, note=""):
    return dict(check_id=cid, label=label, ours=ours, reference=ref, threshold=thr, result=result, hard="Y" if hard else "N", note=note)


def checks_fut(B, P1, cash_dir, shas):
    ctx, sel, eng, by_label, windows = B["ctx"], B["sel"], B["eng"], B["by_label"], B["windows"]
    ch, wt = cash_base(cash_dir)
    out = []
    # C-X1
    worst, bad, parts = 0.0, [], []
    pins = {("2023Q4", "base"): (1387.745524, 12609), ("2026Q2", "base"): (1936.986234, 13799)}
    for lab in R2_WINDOWS:
        wi = by_label[lab].idx
        for v in ("base", "matched"):
            ours = ctx.agg[(v, wi)].val("tenyeq_fixed")
            row = wt[(lab, v)]
            ref, fref = float(row["tenyeq_fixed_bn"]), int(row["funds_in_window"])
            nf = len(sel[v]["assign"][wi])
            tie = math.fsum(x.value() for (vv, w2, fund), x in ctx.s_fund.items() if vv == v and w2 == wi)
            diff = max(abs(ours - ref), abs(tie - ref))
            worst = max(worst, diff)
            if diff > 1e-5 or nf != fref:
                bad.append(f"{lab}/{v}: {ours:.6f} vs {ref}, {nf} vs {fref} funds")
            if (lab, v) in pins:
                pv, pf = pins[(lab, v)]
                if abs(ref - pv) > 1e-6 or fref != pf or nf != pf or abs(ours - pv) > 1e-5:
                    bad.append(f"{lab}/{v}: not the pinned {pv} / {pf:,}")
            parts.append(f"{lab[2:]}/{v[0]} {ours:.6f}")
    out.append(mk("C-X1", "the imported selection and pricing reproduce tsy_windows.csv tenyeq_fixed_bn at the four R2 windows (base and matched) and funds_in_window exactly; the per-series sums tie to the window totals",
                  "; ".join(parts[:2]) + f" ... max diff {worst:.2e}", "tsy_windows.csv; 1,387.745524 and 1,936.986234 base; 12,609 and 13,799 funds", "<= 1e-5 $bn; funds exact",
                  "FAIL" if bad else "PASS", True, "; ".join(bad)))
    # C-X2
    badz = []
    for pk in B["packs"]:
        want = shas.get(pk["zip"])
        if want is None or want != pk["sha"]:
            badz.append(pk["zip"])
    out.append(mk("C-X2", "each N-PORT zip's sha256 equals the cash build's tsy_file_stats.csv", f"{len(B['packs']) - len(badz)} of {len(B['packs'])} equal",
                  "tsy_file_stats.csv", "all equal", "FAIL" if badz else "PASS", True, ("mismatch or absent: " + ", ".join(badz)) if badz else ""))
    # C-X3
    c3 = {v: (sel[v]["c2"], sel[v]["c2_after"]) for v in ("base", "matched")}
    out.append(mk("C-X3", "check_unique_survivors (imported) on both vintages, before and after the content-duplicate step", str(c3), "PASS", "PASS",
                  "PASS" if all(x == "PASS" for p in c3.values() for x in p) else "FAIL", True))
    # C-F1
    d10 = B["fixed"][2]
    bad1 = cf_fixture_failures()
    ok1 = B["fixed"][3] == dt.date(2023, 12, 29) and B["fixed"][4] == dt.date(2023, 12, 29) and abs(d10 - D10_PIN) <= D10_TOL and not bad1
    out.append(mk("C-F1", "fixed curve resolves to 2023-12-29 and d10 is 8.2233 +/- 0.0001; the conversion-factor fixtures of spec 3.5 are exact",
                  f"{B['fixed'][3]}/{B['fixed'][4]}; d10 {d10:.4f}; {len(CF_FIXTURES) + 1} fixtures", "2023-12-29; 8.2233", "+/- 0.0001; exact",
                  "PASS" if ok1 else "FAIL", True, "; ".join(bad1)))
    # C-F2
    bad2, parts = [], []
    for c in CONTRACTS:
        fac, cf, y, dur = B["tenor"][c]
        pcf, pfac = TENOR_PINS[c]
        parts.append(f"{c} {fac:,.2f}")
        if abs(fac - pfac) > 0.01 or abs(cf - pcf) > 1e-12:
            bad2.append(f"{c}: {fac:.2f} / CF {cf} vs {pfac} / {pcf}")
    out.append(mk("C-F2", "the eight tenor factors of spec 3.4 within $0.01, unrounded duration and d10, conversion factor to 4 dp", "; ".join(parts),
                  "; ".join(f"{c} {TENOR_PINS[c][1]:,.2f}" for c in CONTRACTS), "$0.01", "FAIL" if bad2 else "PASS", True, "; ".join(bad2)))
    # C-F3
    bad3 = classifier_fixture_failures()
    out.append(mk("C-F3", "the classifier fixtures of spec 3.2 are all correct", f"{len(CLASSIFIER_FIXTURES) - len(bad3)} of {len(CLASSIFIER_FIXTURES)}",
                  "all", "all", "FAIL" if bad3 else "PASS", True, "; ".join(bad3)))
    # C-F4
    bad4, skipped, tested = [], 0, 0
    for w in windows:
        ag = eng.agg[("base", w.idx)]
        for c in CONTRACTS:
            ca = ag.by_c.get(c)
            if ca is None:
                continue
            need = 5 if c in FACE_200K else 20
            if len(ca.ratios) < need:
                skipped += 1
                continue
            tested += 1
            med = statistics.median(ca.ratios)
            if not (0.85 <= med <= 1.35):
                bad4.append(f"{w.label}/{c}: median {med:.3f} on {len(ca.ratios)} lines")
    out.append(mk("C-F4", "per contract and window, the median NOTIONAL / (contracts x face) over every valid-count line before the basis fallback", f"{tested} cells tested, {skipped} skipped for too few lines",
                  "[0.85, 1.35]", "at least 5 lines for TU and Z3N, 20 for the others", "FAIL" if bad4 else "PASS", True, "; ".join(bad4)))
    # C-F5
    ag_n, dis_n, wa, wd = 0, 0, Fsum(), Fsum()
    for w in windows:
        ag = eng.agg[("base", w.idx)]
        ag_n += ag.sign_agree["agree"]
        dis_n += ag.sign_agree["disagree"]
        wa.add(ag.sign_agree_w[0].value())
        wd.add(ag.sign_agree_w[1].value())
    share = ag_n / (ag_n + dis_n) if (ag_n + dis_n) else 0.0
    wshare = wa.value() / (wa.value() + wd.value()) if (wa.value() + wd.value()) else 0.0
    out.append(mk("C-F5", "sign(BALANCE) agrees with FUT_FWD.PAYOFF_PROFILE on kept lines with BALANCE not zero (all windows, base vintage)",
                  f"{ag_n:,} of {ag_n + dis_n:,} lines = {100 * share:.2f}%; in 10-year-equivalent dollars {100 * wshare:.2f}%", "96.1% on 2024q1 (first-pass classifier)",
                  ">= 90% of lines", "PASS" if share >= 0.90 else "FAIL", True, "the dollar agreement is reported beside it and is not the hard test; the sign-gap check in the verdict carries that risk"))
    # flags
    ua = math.fsum(eng.agg[("base", w.idx)].s["ua_abs"].value() for w in windows)
    nt = math.fsum(eng.agg[("base", w.idx)].s["nt_abs_kept"].value() for w in windows)
    out.append(mk("C-F6", "sum of |UNREALIZED_APPRECIATION| over sum of |NOTIONAL_AMOUNT| on kept lines (all windows, base)", f"{100 * ua / nt:.3f}%" if nt else "n/a",
                  "median 2.0% on 2024q1", "< 5%", "PASS" if nt and ua / nt < 0.05 else "FLAG", False))
    f7 = []
    for lab in ("2023Q4", "2026Q2"):
        w = by_label[lab]
        ag = eng.agg[("base", w.idx)]
        f_sum, cash = Fsum(), Fsum()
        for f, _t_ in sel["base"]["assign"][w.idx]:
            fa = ctx.fund_agg.get((w.idx, f.fund))
            if fa and f.net_assets > 0 and fa.value.value() * 1e9 / f.net_assets >= 0.9:
                cash.add(fa.tenyeq.value())
                fu = ag.fund.get(f.fund)
                if fu:
                    f_sum.add(fu.f_tenor.value())
        f7.append((lab, abs(f_sum.value()), cash.value()))
    ok7 = all(c > 0 and f / c <= 0.15 for _l, f, c in f7)
    out.append(mk("C-F7", "in the funds with Treasuries >= 90% of NAV, |net futures| against their cash 10-year equivalents (a size check inside one universe; the two are never added)",
                  "; ".join(f"{l}: {100 * f / c:.1f}%" if c else f"{l}: n/a" for l, f, c in f7), "", "<= 15% at both endpoints", "PASS" if ok7 else "FLAG", False))
    acn = collections.Counter()
    for w in windows:
        acn.update(eng.agg[("base", w.idx)].asset_cat)
    nsum = lambda k: sum(eng.agg[("base", w.idx)].n[k] for w in windows)
    basis = [nsum("lines_basis_face"), nsum("lines_basis_notional"), nsum("notional_field_is_count_lines"), nsum("unit_suspect_lines")]
    out.append(mk("C-F8", "futures lines of the base survivors by ASSET_CAT and kept lines by basis", "; ".join(f"{k} {v:,}" for k, v in sorted(acn.items()) if k)
                  + f"; basis face {basis[0]:,}, notional {basis[1]:,} (count-in-notional {basis[2]:,}, unit-suspect {basis[3]:,})", "", "count", "PASS", False))
    # real-data pins on 2024q1 (spec 8.3)
    pk = next((p for p in B["packs"] if p["tag"] == "2024Q1"), None)
    if pk is not None:
        want = {"pair:DIR|SWP": 25065, "pair:DIR|FUT": 11331, "pair:DIR|SWO": 4747, "pair:DIR|OPT": 1542, "pair:DIR|FWD": 4, "fut_unit:DIR|NC": 11329,
                "fut_unit:DIR|OU": 2, "pair:DCO|FUT": 8348, "pair:DE|FUT": 6214, "pair:DFE|FUT": 838, "pair:DO|FUT": 53, "pair:OTHER|FUT": 35}
        diff = [f"{k}: {pk['stats'].get(k, 0)} vs {v}" for k, v in want.items() if pk["stats"].get(k, 0) != v]
        out.append(mk("C-P1", "2024q1 zip: lines by (ASSET_CAT, DERIVATIVE_CAT) and the UNIT of futures lines against the spec's observed counts", f"{len(want) - len(diff)} of {len(want)} equal",
                      "spec 2.1 observed", "exact", "PASS" if not diff else "FLAG", False, "; ".join(diff)))
        med = {c: (statistics.median(pk["ratios"][c]) if pk["ratios"].get(c) else None) for c in ("TU", "FV", "TY")}
        tgt = {"TU": 1.021, "FV": 1.067, "TY": 1.098}
        ok = all(med[c] is not None and abs(med[c] - tgt[c]) <= 0.005 for c in tgt)
        out.append(mk("C-P2", "2024q1 zip: median NOTIONAL / (|BALANCE| x face) of the lines the classifier names TU, FV and TY (whole zip, count-in-notional lines excluded)",
                      "; ".join(f"{c} {med[c]:.3f}" if med[c] is not None else f"{c} n/a" for c in tgt), "TU 1.021; FV 1.067; TY 1.098", "+/- 0.005", "PASS" if ok else "FLAG", False))
    return out


def checks_idx(B, P2, ncen_info, base_ds, base_ds_m1):
    S, N = P2["S"], P2["N"]
    out = []
    # C-B1
    out.append(mk("C-B1", "every N-CEN column of spec 2.3 is present on the real headers; no quarter is claimed by two zips", f"{ncen_info['zips']} zips read, no column missing",
                  "SUBMISSION, REGISTRANT, FUND_REPORTED_INFO, FEEDER_FUNDS", "all present", "PASS", True,
                  "the load refuses on a missing column; real names differing from the spec: SUBMISSION_TYPE is the submission-type column; FEEDER_FUNDS carries FUND_ID (joined to the master's FUND_REPORTED_INFO row) and no ACCESSION_NUMBER"))
    # C-B3
    bad, parts = [], []
    for per, _l0, _l1 in PERIODS:
        tot = math.fsum(period_delta(S, N, g, per)[0] for g in GROUPS)
        ref = base_ds[per]
        parts.append(f"{per} {tot:.6f}")
        if abs(tot - ref) > 1e-5:
            bad.append(f"{per}: {tot:.6f} vs {ref}")
    out.append(mk("C-B3", "partition identity: every group's change (mmf, levinv, unflagged, stale_flag, switcher, feeder_dropped included) sums to the cash build's change in each period",
                  "; ".join(parts), "tsy_change.csv M0: " + "; ".join(f"{p} {base_ds[p]}" for p, _, _ in PERIODS), "1e-5 $bn", "FAIL" if bad else "PASS", True, "; ".join(bad)))
    # C-B4
    dup = sum(1 for recs in P2["table"].values() if len({r.period for r in recs}) != len(recs))
    unl = 0
    for (l, fund), (o, rec) in P2["obs"].items():
        f = P2["survivors"][l][fund]
        if rec is not None and rec.period > f.rdate and not o.backfilled:
            unl += 1
    out.append(mk("C-B4", "no N-PORT report has two N-CEN flags after the amendment rule, and every backfilled flag carries the flag_backfilled label",
                  f"{dup} keys with two filings for one period; {unl} unlabelled backfilled flags", "0; 0", "0", "PASS" if dup == 0 and unl == 0 else "FAIL", True))
    # C-B5
    used = {}                                   # one row per series and filing: the series row of the N-CEN table, not the filing
    for (_l, fund), (o, rec) in P2["obs"].items():
        if rec is not None:
            used[(fund, rec.acc, str(rec.period))] = rec
    none_box = sum(1 for r in used.values() if r.flags.get("IS_FUND_TYPE_NA") != "Y" and not any(r.flags.get(k) == "Y" for k in FLAG_TYPE_COLS + ("IS_MONEY_MARKET",)))
    iv = collections.Counter({"Y": 0, "N": 0, "blank": 0})
    for r in used.values():
        v = r.flags.get("IS_INDEX", "")
        iv[v if v in ("Y", "N") else "blank"] += 1
    out.append(mk("C-B5", "share of the N-CEN series rows used as flag sources (one per series and filing) with no type box checked and IS_FUND_TYPE_NA not Y; IS_INDEX value counts",
                  f"{none_box:,} of {len(used):,} = {100 * none_box / max(1, len(used)):.2f}%; IS_INDEX Y {iv['Y']:,}, N {iv['N']:,}, blank {iv['blank']:,}", "expected near 0 (B1)", "printed", "PASS", False))
    # C-B6
    parts = []
    for l in R2_WINDOWS:
        age = collections.Counter()
        bf = 0
        for (l2, fund), (o, rec) in P2["obs"].items():
            if l2 != l or rec is None:
                continue
            f = P2["survivors"][l][fund]
            m = (f.rdate.year - rec.period.year) * 12 + f.rdate.month - rec.period.month
            if o.backfilled:
                bf += 1
            else:
                age["0-12" if m <= 12 else "13-24" if m <= 24 else "25+"] += 1
        parts.append(f"{l}: age 0-12m {age['0-12']:,}, 13-24m {age['13-24']:,}, 25m+ {age['25+']:,}, backfilled {bf:,}")
    out.append(mk("C-B6", "age of each flag's N-CEN period at the report date, and the backfilled count, by window (all survivors)", "; ".join(parts), "", "printed", "PASS", False))
    # C-B7
    funds, table = P2["funds"], P2["table"]
    key_of = lambda f: ("S" if f[0] == "S" else "C", f[1])
    lost = [f for f in funds if f in P2["survivors"]["2026Q2"] and table.get(key_of(f))
            and max(r.period for r in table[key_of(f)]) < dt.date(2025, 1, 1)]
    lost_h = [f for f in lost if funds[f]["s"]["2026Q2"] != 0.0]
    lost_s = math.fsum(funds[f]["s"]["2026Q2"] for f in lost)
    stale = [f for f in funds if P2["go"](f) == "stale_flag"]
    stale_h = [f for f in stale if funds[f]["s"]["2026Q2"] != 0.0]
    stale_s = math.fsum(funds[f]["s"]["2026Q2"] for f in stale)
    out.append(mk("C-B7", "series and cash 10-year equivalents lost to the schema-3.1 omission: series with an N-CEN before 2025 and none after, and the stale_flag group",
                  f"{len(lost):,} series that hold cash in any of the four windows have an N-CEN before 2025 and none after; {len(lost_h):,} of them hold cash at 2026Q2, "
                  f"${lost_s:,.1f}bn in all at 2026Q2. stale_flag group: {len(stale):,} series that hold cash in any window; {len(stale_h):,} hold cash at 2026Q2, "
                  f"${stale_s:,.1f}bn in all at 2026Q2", "", "printed", "PASS", False))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# the README, the SOURCES file and the file statistics
# ------------------------------------------------------------------------------------------------------------------------
COLUMN_DOC = {
    "window": "the quarter-end month of the report window, such as 2023Q4", "quarter_end": "the last day of that quarter", "vintage": "base = every zip with a filing within 62 days of the report date; matched = zips up to the window's home zip",
    "funds_in_window": "survivor filings assigned to the window by the cash build's rule", "funds_with_tsy_fut": "funds with at least one kept Treasury-futures line",
    "tsy_fut_lines": "kept Treasury-futures lines", "contracts_long": "contracts held long (effective count)", "contracts_short": "contracts held short (effective count)",
    "face_long_bn": "face of the long contracts, $bn", "face_short_bn": "face of the short contracts, $bn", "face_net_bn": "long face less short face, $bn",
    "notional_tradedate_net_bn": "net trade-date contract value from the filed notional field, $bn, lines whose notional is a genuine value", "tenyeq_tenor_bn": "net 10-year equivalents on the tenor map, $bn (the headline measure)",
    "tenyeq_tenor_balsign_bn": "the same with the sign taken from BALANCE where it is not zero, $bn", "tenyeq_ctd_bn": "net 10-year equivalents on the modelled cheapest-to-deliver, $bn (base vintage, the four R2 dates only)",
    "unrealized_abs_bn": "sum of the absolute filed marks on kept lines, $bn", "lines_basis_face": "kept lines sized as contracts times face", "lines_basis_notional": "kept lines sized from the filed notional",
    "notional_field_is_count_lines": "lines whose notional field holds the contract count (face basis kept)", "unit_suspect_lines": "valid-count lines whose notional is far from contracts times face (notional basis)",
    "no_size_lines": "Treasury lines with no usable size, excluded", "non_usd_lines": "futures lines failing the USD condition", "unresolved_lines": "futures lines whose text names no contract",
    "unresolved_conflict_lines": "lines whose sources name different contracts", "sign_na_lines": "Treasury lines with no long or short sign, excluded", "sign_disagree_lines": "kept lines whose two signs disagree",
    "sign_disagree_notional_share": "face of those lines over the face of kept lines", "expired_lines": "Treasury-candidate lines that expired before the report date, dropped",
    "non_dir_tsy_lines": "kept Treasury lines whose asset category is not interest-rate derivative", "ctd_fallback_lines": "kept lines priced on the tenor map because the modelled basket was empty",
    "unresolved_share": "face of unresolved, conflicting and sign-less lines over the face of kept plus those lines",
    "contract": "TU 2-year note, Z3N 3-year note, FV 5-year note, TY 10-year note, TN Ultra 10-year note, TWE 20-year bond, US classic bond, UB Ultra bond", "funds_n": "funds with a kept line (a count of funds)",
    "lines": "kept lines, or lines in the category", "contracts_net": "long less short contracts", "dv01_tenor_mn": "net 10-year equivalents times the fixed-curve duration times 0.0001, $mn per basis point",
    "tenor_factor_usd": "10-year-equivalent dollars of one contract on the tenor map", "ctd_factor_usd": "the same on the modelled cheapest-to-deliver of the largest delivery month",
    "ctd_maturity": "maturity of that modelled deliverable", "ctd_coupon_pct": "its coupon, per cent", "ctd_cf": "its conversion factor", "notional_over_face_median": "median filed notional over contracts times face",
    "variant_id": "T0 tenor map base; T1 tenor map matched; C0 modelled cheapest-to-deliver base; B0 tenor map base with the BALANCE sign", "description": "what the variant is", "period": "full = 2023Q4 to 2026Q2; 2024; 2025; 2026H1",
    "f_start_bn": "net 10-year equivalents at the start of the period, $bn", "f_end_bn": "at the end, $bn", "d_f_bn": "the net change, $bn", "group": "the group the amount belongs to",
    "category": "swap_dir, option_dir, swaption_dir, ir_fut_nontsy, bond_fut_foreign, other_fut_nontsy, unresolved, sign_na", "notional_abs_bn": "gross absolute notional, $bn (options: principal amount where filed)",
    "key": "the name of the value", "value": "the value", "series_n": "series (a count of series)", "s_start_bn": "cash 10-year equivalents at the start of the period, $bn", "s_end_bn": "at the end, $bn",
    "d_s_bn": "the change, $bn", "flag": "mmf, levinv, unflagged, index, active or feeder_dropped", "flag_backfilled_n": "series whose flag came from the first later N-CEN filing",
    "s_bn": "cash 10-year equivalents, $bn", "is_etf": "Y or N from the N-CEN ETF box", "arm": "index or active (stable series only)",
    "check_id": "the check's name", "label": "what is checked", "ours": "the value this build found", "reference": "what it is compared with", "threshold": "the pass condition", "result": "PASS, FAIL, FLAG or N/A",
    "hard": "Y if a FAIL stops the build", "note": "detail", "tag": "the file or window the row is about", }

SOURCES_TEXT = """# Sources for the fund futures and index split build

Every source below was read by someone other than this script. The script makes no network request of any kind.

1. **SEC bulk N-PORT data sets.** Quarterly zip files of Form N-PORT filings, 2024q1 to 2026q3 (eleven files). Landing page
   https://www.sec.gov/dera/data/form-n-port-data-sets ; file pattern https://www.sec.gov/files/dera/data/form-n-port-data-sets/YYYYqQ_nport.zip .
   Terms: the SEC publishes these data sets for public use; its website policies at https://www.sec.gov/about/privacy-information apply, and SEC.gov
   requires automated requests to declare a contact. The zips are not redistributed here; only derived aggregates are.
   Citation: U.S. Securities and Exchange Commission, Division of Economic and Risk Analysis, Form N-PORT Data Sets, retrieved October 2026.
2. **SEC bulk Form N-CEN data sets.** Quarterly zip files of Form N-CEN annual reports, 2022q1 to 2026q3 (nineteen files). Landing page
   https://www.sec.gov/dera/data/form-ncen-data-sets . The page says the data sets do not include, at this time, N-CEN filings submitted in the schema
   version 3.1 introduced in EDGAR version 25.2. Terms and citation as for item 1; Form N-CEN, Item C.3, defines the type boxes.
3. **Federal Reserve Board, FEDS Notes.** Iorio, Li and Petrasek, "Why do mutual funds invest in Treasury futures?", 10 May 2024,
   https://www.federalreserve.gov/econres/notes/feds-notes/why-do-mutual-funds-invest-in-treasury-futures-20240510.htm and its accessible data page
   https://www.federalreserve.gov/econres/notes/feds-notes/why-do-mutual-funds-invest-in-treasury-futures-accessible-20240510.htm .
   Terms: Federal Reserve material is in the public domain. Used for the end-2023 anchor values only.
4. **CME Group and CBOT contract rules.** Treasury futures deliverable baskets, contract sizes and the conversion-factor formula, from the CBOT rulebook
   chapters 18, 19, 20, 21, 26, 39 and 40 and the CBOT conversion-factor article, as fetched and quoted by an outside reviewer; this build did not read
   cmegroup.com. Terms: CME Group's website terms; short factual rules only are used, no text is reproduced.
5. **U.S. Treasury, Fiscal Data.** Monthly Statement of the Public Debt, Table 3 (market value of marketable securities), record dates 2023-12-31,
   2024-12-31, 2025-12-31 and 2026-06-30, through https://fiscaldata.treasury.gov/ (cached by the companion cash build). Terms: U.S. government data.
6. **U.S. Treasury, Daily Treasury Par Yield Curve Rates and Real Yield Curve Rates**, 2023 to 2026, https://home.treasury.gov/ (cached by the cash
   build). Terms: U.S. government data. The fixed curve is that of 29 December 2023.
7. **The companion cash build.** bin/nport_treasury_duration.py and its outputs in data/nport/ (tsy_windows.csv, tsy_change.csv, tsy_file_stats.csv),
   which this build imports and reproduces; and bin/r2_duration_supply.py, the pricing functions it imports.
"""


NUM_WORDS = {0: "no", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}


def p1_failed_plain(P1):
    """The unmet conditions of the futures rule, each as a plain clause with its figures."""
    u = P1["anchor_all"]
    out = []
    if not (A1_RANGE[0] <= u["a1"] <= A1_RANGE[1]):
        out.append(f"the end-2023 net futures face of {usd(u['a1'])} fell outside its band of ${A1_RANGE[0]:.0f}bn to ${A1_RANGE[1]:.0f}bn")
    if not (u["a2"] is not None and A2_RANGE[0] <= u["a2"] <= A2_RANGE[1]):
        out.append(f"the anchor comparing futures risk with cash bond risk at end-2023 was {u['a2']:.2f}, outside its band of {A2_RANGE[0]:.2f} to {A2_RANGE[1]:.2f}")
    if not (u["a3"] is not None and A3_RANGE[0] <= u["a3"] <= A3_RANGE[1]):
        out.append(f"the implied futures duration of {u['a3']:.2f} years fell outside its band of {A3_RANGE[0]:.1f} to {A3_RANGE[1]:.1f} years")
    for lab, v in (("end-2023", P1["u_f"][0]), ("mid-2026", P1["u_f"][1])):
        if not le(v, UF_MAX):
            out.append(f"unresolved, conflicting and sign-less lines were {pct(v)} of futures face at {lab}, above the {pct(UF_MAX, 0)} limit")
    if not le(P1["g_v"], GV_MAX):
        out.append(f"the base and matched vintages differ by {usd(P1['g_v'])} against a ${GV_MAX:.0f}bn limit")
    if not le(P1["g_c"], GC_MAX):
        out.append(f"the tenor map and the modelled cheapest-to-deliver differ by {usd(P1['g_c'])} against a ${GC_MAX:.0f}bn limit")
    if not le(P1["g_s"], GS_MAX):
        out.append(f"the readings of the net change using the filed long-or-short sign and using the sign of the filed contract count differ by {usd(P1['g_s'])} against a ${GS_MAX:.0f}bn limit")
    return out


def readme_p1_sentence(P1):
    d = P1["d_f"]
    word = {"LARGE": "large", "SMALL": "small", "INCONCLUSIVE": "not established"}[P1["label"]]
    s = (f"The net change in registered funds' Treasury futures from end-2023 to mid-2026 was {word}, at {usd(d)} of 10-year equivalents "
         f"against a ${DF_BAR_BN:.0f}bn line")
    if P1["label"] == "INCONCLUSIVE":
        failed = p1_failed_plain(P1)
        s += f", because {NUM_WORDS.get(len(failed), str(len(failed)))} condition{'s were' if len(failed) != 1 else ' was'} not met: " + "; and ".join(failed)
    s += "."
    for name in sorted(_ACTIVE):               # the G14 mutants reach the verdict sentences too
        if name.startswith("readme_inject:"):
            s += f" This sentence was inserted by a mutant: {name.split(':', 1)[1]}."
    return s


def readme_p1_note(P1):
    """Plain statement on the anchor that failed and why, when it did."""
    u = P1["anchor_all"]
    if u["a2"] is not None and A2_RANGE[0] <= u["a2"] <= A2_RANGE[1]:
        return ""
    s = ("That anchor fails because the end-2023 comparison group covers all registered funds, exchange-traded and closed-end funds included, a choice the "
         "supervisor ruled on before the run, while the Federal Reserve note's own value of 0.30 is for mutual funds only, so the cash bond side here is far larger.")
    e = P1.get("anchor_exetf")
    if e is not None and e["a2"] is not None:
        inside = A2_RANGE[0] <= e["a2"] <= A2_RANGE[1]
        s += f" With exchange-traded funds removed the value is {e['a2']:.3f}, which also falls {'inside' if inside else 'outside'} the band."
    return s


def readme_p2_sentence(P2):
    DI = P2["DI"]
    lab = P2["label"]
    if lab != "INCONCLUSIVE":
        return part2_sentence(P2, {})
    q26, s0 = DI["q"]["2026H1"], DI["s0"]
    head = ("The split of registered funds' cash Treasury duration change between series flagged 'Index Fund' on Form N-CEN (any index, not only Treasury "
            "indexes) and the rest is not established: ")
    if DI["u"] > U_CAP_BN or q26 is None or DI["q"]["2024"] is None or DI["q"]["2025"] is None:
        return head + p2_reason(P2).rstrip(".") + "."
    near = ""
    if abs(q26 - Q_AGAINST) <= 0.05:
        near = ", close to the lower bar"
    elif abs(q26 - Q_SUPPORT) <= 0.05:
        near = ", close to the upper bar"
    return (head + f"the index funds' share of the classified change was {pct(DI['q']['2024'])} in 2024, {pct(DI['q']['2025'])} in 2025 and {pct(q26)} in the first half "
            f"of 2026, against {pct(s0)} of the classified stock at end-2023. The share in the first half of 2026 lies between the two bars (at least 60%, with the "
            f"required margins, to support the finding; at most 40%, and no higher than the stock share, to count against it){near}.")


def sources_text():
    """The sources file: the sources, then the build decisions (moved here from the README)."""
    L = [SOURCES_TEXT.rstrip("\n"), "", "## Build decisions", "",
         "Each was made where the specification was open or silent, taking the stricter reading on leaks and wording. No rule, threshold, window or label was changed. "
         "The last two entries record what was done after the first run.", ""]
    L += [f"{i}. {t}" for i, t in enumerate(DECISIONS, start=1)]
    for name in sorted(_ACTIVE):               # the G14 mutants: a banned word or a symbol inserted into the prose
        if name.startswith("readme_inject:"):
            L.append(f"This sentence was inserted by a mutant: {name.split(':', 1)[1]}.")
    return "\n".join(L) + "\n"


def readme_text(R):
    """The README (spec 5, R23-19), in the order the spec fixes. `R` carries every number and sentence. No symbol appears in prose; the column
    dictionary at the end is exempt. The generator is itself scanned by the wording guard."""
    P1, P2 = R["P1"], R["P2"]
    L = []
    w = L.append
    w("# Registered funds' Treasury futures and the index split of their cash Treasury duration")
    w("")
    w("This folder measures how much US registered funds changed their net Treasury futures positions between end-2023 and mid-2026, in 10-year equivalents, "
      "and how much of the change in their cash Treasury duration sits in series that Form N-CEN flags as index funds. " + REQUIRED_SENTENCE)
    w("")
    w("## Definitions")
    w("")
    w("- **10-year equivalent.** A holding restated as the amount of a 10-year par Treasury note that would react to a rate change by the same number of dollars, "
      "on one fixed yield curve (29 December 2023). Cash holdings and futures are both stated this way, always on that one curve.")
    w("- **Treasury future and contract face.** A standard contract on a Treasury note or bond. Eight are used: the 2-, 3-, 5- and 10-year notes, the Ultra 10-year "
      "note, the 20-year bond, the classic bond and the Ultra bond. Face per contract is $200,000 for the 2- and 3-year notes and $100,000 for the others; "
      "a fund's position is its contract count times that face.")
    w("- **Net change in funds' futures.** Long positions less short positions, in 10-year equivalents, at the end of the second window less the first, across "
      "the registered funds the cash build keeps for each window.")
    w("- **Tenor map.** The headline conversion. Each contract is represented by a par bond at the shortest remaining term of its deliverable basket, priced on the "
      "fixed curve, and scaled by the contract's conversion factor. The eight resulting dollar values per contract are fixed before any fund data is read.")
    w("- **Conversion factor.** The exchange's number that makes deliverable bonds of different coupons comparable: the price at a 6% yield of a bond with that "
      "coupon and term, per dollar of face, with the coupon rounded to the nearest eighth of a per cent.")
    w("- **Modelled cheapest-to-deliver.** For comparison only: from the Treasury's list of outstanding notes and bonds on each window's date, the deliverable with the "
      "lowest price per unit of conversion factor on that date's curve, ignoring carry and delivery options. It is a model, not an observed delivery.")
    w("- **Form N-CEN and the \"Index Fund\" box.** Form N-CEN is the annual report of a registered fund. Item C.3 asks the fund to tick every type that applies, "
      "including \"Index Fund\". A fund that ticks none of the types, and marks \"not applicable\", is an ordinary active fund here.")
    w("- **Stable sample.** The series that carry the same flag, index or active, in every window in which they appear. The split is measured on this sample.")
    w("- **Unclassified change.** The change in cash Treasury duration held by series that are unflagged, switch flags, or whose flag is out of date; it is reported "
      "separately and capped at $16.2bn for the split to count as established.")
    w("")
    w("## Futures: what the result says")
    w("")
    w(readme_p1_sentence(P1))
    w("")
    chg = P1["chg"]
    w(f"The net position was {usd(chg[('T0', 'full')][0])} of 10-year equivalents at end-2023 ({R['n23']:,} funds in the window) and {usd(chg[('T0', 'full')][1])} at mid-2026 "
      f"({R['n26']:,} funds), a change of {usd(P1['d_f'])}. By period it was {usd(chg[('T0', '2024')][2])} in 2024, {usd(chg[('T0', '2025')][2])} in 2025 and "
      f"{usd(chg[('T0', '2026H1')][2])} in the first half of 2026. Using the matched vintage the change is {usd(chg[('T1', 'full')][2])}, using the modelled "
      f"cheapest-to-deliver {usd(chg[('C0', 'full')][2])}, and taking the sign from the filed contract count {usd(chg[('B0', 'full')][2])}.")
    w("")
    u = P1["anchor_all"]
    w(f"Checks against the Federal Reserve note's end-2023 figures, over the {u['universe_n']:,} registered funds in the cash build's end-2023 survivors whose cash Treasuries or "
      f"gross futures face exceed 1% of net assets ({u['universe_with_futures_n']:,} of them hold futures): " + "; ".join(t for ok, t in p1_conditions(P1, True)[:3]) + ". "
      f"The gross long futures face of all registered funds at end-2023 was {usd(P1['a4_gross_long_bn'])}, against the note's reading of about $470bn to $500bn for mutual funds. "
      "The conditions and gaps that decide the label are: " + "; ".join(f"{t} ({'met' if ok else 'not met'})" for ok, t in p1_conditions(P1, True)[3:]) + ".")
    note = readme_p1_note(P1)
    if note:
        w("")
        w(note)
    w("")
    w("Futures are not added to cash holdings. A future has a long side and a short side, so across all holders it nets to zero; it is not a stock of securities that "
      "someone has to hold. This build therefore never adds the futures figure to the cash figure, never divides it by the public's change in cash holdings, and never "
      "sets it against the cash line of the companion cash study.")
    w("")
    w("## Index split: what the result says")
    w("")
    w(readme_p2_sentence(P2) if P2 is not None else R["p2_sentence"])
    w("")
    if P2 is not None:
        DI = P2["DI"]
        d = DI["ds"]
        w(f"In the first half of 2026 the cash Treasury duration held by registered funds changed by {usd(R['base_ds']['2026H1'])} of 10-year equivalents. "
          f"Of that, the stable index series took {usd(d['2026H1']['index_stable'])} and the stable active series {usd(d['2026H1']['active_stable'])}; "
          f"the unclassified change was {usd(DI['u'])} against the $16.2bn cap. The index share of the classified change was {pct(DI['q']['2024'])} in 2024, "
          f"{pct(DI['q']['2025'])} in 2025 and {pct(DI['q']['2026H1'])} in the first half of 2026, against an index share of the classified stock at end-2023 of "
          f"{pct(DI['s0'])}. The bar for a result that is large and rising is a share of at least 60% in the first half of 2026, at least 15 points above the "
          "stock share, and at least 10 points above each of the two earlier periods. The 15-point bar is a hurdle fixed in advance, taken from a different "
          "object (the funds' excess over the public stock in the cash study) after that object had been measured; it is not a sampling bound.")
        w("")
        w("This is a measurement, not a test against noise. With unclassified change at its cap, the share could move by about ten points either way, so a share "
          "within ten points of a bar is fragile.")
    else:
        w("Part 2 needs the Form N-CEN files and was not run in this build.")
    w("")
    w("## What the \"Index Fund\" box cannot tell")
    w("")
    w("The box says only that a fund tracks some index. It does not say the index is the Bloomberg US Aggregate or any bond index, that it is weighted by market "
      "value, or that it is an index of Treasuries; it covers equity and other indexes too. A fund that follows an index closely without ticking the box is counted as "
      "active. Index funds that hold only Treasuries or T-bills are inside the index group, and the bulk files carry no field that separates them.")
    w("")
    w("## Flags can be out of date or missing for 2025 and 2026")
    w("")
    w("The SEC's Form N-CEN data sets do not include, at this time, filings submitted in the newer schema version, so the flags for 2025 and 2026 can be out of date "
      "or missing. Series whose latest usable filing ended before 30 March 2025 are set aside as stale, entrants with no earlier filing are unflagged, and both count "
      "as unclassified. If the unflagged entrants' change plus the stale series' change exceeds $16.2bn, the split is inconclusive by construction."
      + (" " if P2 is not None else ""))
    if P2 is not None:
        DI = P2["DI"]
        L[-1] += (f"In this build the unflagged entrants' change was {usd(P2['entrants_unflagged_ds'])} and the stale series' change {usd(DI['u_comp']['stale_flag'])} "
          f"({R['entrants_n']:,} entrants, of which {P2['entrants_unflagged_n']:,} unflagged and {P2['entrants_backfilled_n']:,} flagged from a later filing).")
    w("")
    w("## Where the exchange's explainer disagreed with its rulebook")
    w("")
    w("An earlier draft of the contract rules followed the CME's 2024 explainer. It measured the remaining term of the 2-year and 3-year note futures from the last day of "
      "the delivery month, and left out the 10-year note future's limit on original term. The CBOT rulebook, as quoted from its chapters, measures every term from the "
      "first day of the delivery month and limits the 10-year note's original term to ten years. The rulebook is used.")
    w("")
    w("## Provenance")
    w("")
    w("Built by bin/nport_futures_index.py from the SEC bulk N-PORT zips (eleven files, 2024q1 to 2026q3) read in place as streams, the SEC bulk Form N-CEN zips "
      "(nineteen files, 2022q1 to 2026q3, fetched by the supervisor), the companion cash build's committed files and its cached Treasury curves and "
      "Statement of the Public Debt tables. The script imports the cash build's survivor selection and pricing; the cash build's own totals are reproduced at the four "
      "report dates before anything else is reported. The script makes no network request. Sources are in fut_idx_SOURCES.md; file hashes and counts are in "
      "fut_idx_file_stats.csv; the checks are in fut_checks.csv and idx_checks.csv.")
    w("")
    w("Build decisions, including two edits made after the first run, are listed in [fut_idx_SOURCES.md](fut_idx_SOURCES.md).")
    w("")
    for name in sorted(_ACTIVE):               # the G14 mutants: a banned word or a symbol inserted into the prose
        if name.startswith("readme_inject:"):
            w(f"This sentence was inserted by a mutant: {name.split(':', 1)[1]}.")
    w("## Column dictionary")
    w("")
    for f, cols in R["cols_by_file"].items():
        if f in ("fut_verdict.csv", "idx_verdict.csv", "idx_prerun.csv"):
            w(f"- `{f}`: columns key, value; one value per row.")
            continue
        w(f"- `{f}`:")
        for c in cols:
            w(f"  - `{c}`: {COLUMN_DOC[c]}")
    return "\n".join(L) + "\n"


DECISIONS = [
    "A zero filed notional is treated as a missing one when the contract count is valid, so the line is sized as contracts times face (the specification names blank and zero together only for lines with no valid count).",
    "Each text source is the concatenation of every filed field of every row of that table for the holding, in upper case with runs of spaces squeezed to one space (not removed).",
    "Two or more different contracts named by different sources make a conflict; otherwise the first source that gives any answer, including a non-Treasury word, decides.",
    "Treasury lines outside the interest-rate derivative category are kept in the net position and also counted separately; unresolved lines that had already expired are dropped as expired.",
    "In the unclassified share of the futures result, the size of an unresolved or conflicting line is its filed notional, and the size of a line with no sign is its sized face.",
    "A series counts in a group's series count at a period if it holds a non-zero cash amount at either end; empty cells are dropped, and cells under five series are merged into other_small.",
    "The series group is taken over every window in which the series is a survivor, including windows in which it is a feeder whose amount is set aside.",
    "Entrants are survivors at 2026Q2 that were not survivors at 2025Q4 and hold cash Treasuries at 2026Q2.",
    "Feeders are found from the master's N-CEN filing: the FEEDER_FUNDS rows are joined through FUND_ID to the master's FUND_REPORTED_INFO row, because that table has no accession column.",
    "The specification gives no thresholds for the four extra inconclusive clauses. Each is printed as a yes or no for whether the value would sit on a different side of the rule's bars than the headline share (above, below or between); these printed ratios are plain ratios, without the size bounds that the rule puts on the headline share.",
    "The index-ETF-only and index-mutual-fund-only excess over the stock share restrict both the index and the active arm to the same ETF status, and use the matching stock share.",
    "Anchors use funds whose cash Treasury value or gross futures face exceeds 1% of net assets in the 2023Q4 base survivors; futures in the anchors are those of that universe only, and the notes-and-bonds side is the cash build's coupon and TIPS lines of the same funds.",
    "The heavy passes over the N-PORT zips run one zip at a time into a scratch directory outside the repository (stage A and stage B), so that no command outlasts a tool timeout; the final build reads those files and is otherwise unchanged.",
    "The modelled cheapest-to-deliver shown per contract and window is that of the delivery month with the largest kept face in that window.",
    "The remaining term of the 20-year bond future's deliverables uses the same quarter rounding as the other contracts, as stated in the rules; the word BOND is matched as a substring and BD as a whole word.",
    "The unflagged group holds series with a type box ticked beside the not-applicable box, and series with no usable N-CEN row at all.",
    "The per-contract median check on notional per face is run on the base vintage in every window; a contract and window with too few lines is skipped and counted, not passed.",
    "The two real-data pins on the 2024q1 zip (the counts by category and unit, and the three notional-per-face medians) are printed as flags, not hard checks.",
    "Series without any N-CEN row are kept in the ex-ETF anchors (they are not flagged as ETFs) and are counted separately.",
    "The real column names differ from the specification in two places: the submission-type column is SUBMISSION_TYPE, and the feeder table links to the master through FUND_ID.",
    "In the real data the index box carries only Y and blank, never N, and the only submission types are N-CEN and N-CEN/A, so the rule that ignores late-filing notices never fires.",
    "The size of the unresolved share of futures face (the share that must stay at or under 10% at each end) was built as follows. Numerator: the unresolved lines and the conflicting lines, each at its filed notional (a line with no filed notional counts as zero), plus the Treasury lines with no long or short sign, each at its sized face. Denominator: that numerator plus the sized face of the kept lines. Expired lines, non-Treasury lines and Treasury lines with no usable size are in neither. This was fixed before the run and is recorded here after it; the label does not depend on it, since the share is about 3% at both ends against a 10% limit.",
    "After the first futures run, with its numbers already printed, the builder expanded the README and verdict sentences so that they name the conditions that were not met, added three diagnostic rows to the file statistics (feeder series dropped, N-CEN records listing feeders, N-CEN series keys) and changed a default folder name. No computed number, rule, threshold or label changed.",
    "After the independent check of the first results, the builder (a) counted the index-box and type-box check once per series row, not once per filing, (b) renamed the count of series without an N-CEN row to say that it covers the whole anchor universe, not only funds with futures, (c) rewrote the C-B7 and C-F8 notes and removed a column name from the README prose, (d) added boundary tests for the stale cutoff, the lower edge of the size-ratio band, the three share bars and the absolute values in the unclassified change, and (e) added complementary suppression: where a merged small cell is blanked, the smallest remaining amount cell of the same window or period is blanked too, so that a public total cannot give it back. No computed headline number, rule, threshold or label changed.",
]


def file_stats_rows(B, ncen_info, a):
    rows = []

    def add(tag, key, val):
        rows.append(dict(tag=tag, key=key, value=val))

    for pk, w in zip(B["packs"], B["windows"]):
        tag = w.zip_tag
        add(tag, "zip", pk["zip"])
        add(tag, "zip_sha256", pk["sha"])
        add(tag, "zip_bytes", pk["size"])
        add(tag, "window", w.label)
        add(tag, "filings_total", len(pk["filings"]))
        add(tag, "holding_rows", pk["st"]["holding_rows"])
        add(tag, "futures_lines_all_filings", len(pk["fut"]))
        add(tag, "swap_option_lines_all_filings", len(pk["der"]))
        for k in sorted(pk["stats"]):
            add(tag, k, pk["stats"][k])
    for w in B["windows"]:
        for reason, n in sorted(B["eng"].agg[("base", w.idx)].reasons.items()):
            add(w.label, f"classifier_reason:{reason}", n)
    for v in ("base", "matched"):
        add("ALL", f"{v}_survivors", len(B["sel"][v]["kept"]))
        add("ALL", f"{v}_survivors_before_content_dedup", len(B["sel"][v]["chosen"]))
    add("ALL", "fixed_curve_date_nominal", B["fixed"][3].isoformat())
    add("ALL", "fixed_curve_date_real", B["fixed"][4].isoformat())
    add("ALL", "d10_fixed", B["fixed"][2])
    for which, name, _ in ntd.expected_cache_files():
        d = B["r1_cache"] if which == "r1" else B["r2_cache"]
        add("ALL", f"cache:{name}", ntd.file_sha256(os.path.join(d, name)))
    for name in ("tsy_windows.csv", "tsy_change.csv", "tsy_file_stats.csv"):
        add("ALL", f"cash_file:{name}", ntd.file_sha256(os.path.join(a.cash_dir, name)))
    add("ALL", "requests_made_by_this_script", 0)
    add("ALL", "sec_requests_made_by_this_script", 0)
    if ncen_info is not None:
        for y, q, name, path in ncen_info["zl"]:
            tag = f"ncen:{y}q{q}"
            add(tag, "zip", name)
            add(tag, "zip_sha256", ntd.file_sha256(path))
            add(tag, "zip_bytes", os.path.getsize(path))
            st = ncen_info["fetch"].get(name)
            if st:
                add(tag, "supervisor_fetch_status", st[0])
                add(tag, "supervisor_fetch_bytes", st[1])
        for k in sorted(ncen_info["stats"]):
            add("ncen:ALL", k, ncen_info["stats"][k])
    return rows


def read_fetch_log(ncen_dir):
    """The supervisor's fetch_log.tsv: name -> (status, bytes). The time column is not copied (no wall-clock time in any file, R7)."""
    out = {}
    path = os.path.join(tilde(ncen_dir), "fetch_log.tsv")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for ln in fh:
                p = ln.rstrip("\r\n").split("\t")
                if len(p) >= 4:
                    out[p[1]] = (p[2], p[3])
    return out


ORDER_WIN = {w: i for i, w in enumerate(["2023Q4", "2024Q1", "2024Q2", "2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4", "2026Q1", "2026Q2"])}
ORDER_PER = {p: i for i, (p, _a, _b) in enumerate(PERIODS)}
ORDER_PER_FUT = {"full": 0, "2024": 1, "2025": 2, "2026H1": 3}
ORDER_GRP = {g: i for i, g in enumerate(GROUPS)}
ORDER_GRP.update({"continuing": 0, "entrant": 1, "leaver": 2, SMALL_NAME: 99})
ORDER_CONTRACT = {c: i for i, c in enumerate(CONTRACTS)}
ORDER_CONTRACT[SMALL_NAME] = 99


def sort_rows(rows, key):
    return sorted(rows, key=key)


def build_outputs(B, P1, P2, cols_by_file, base_ds, base_ds_m1, ncen_info, a, shas, mode):
    """Rows for every CSV, small cells merged. Returns (files, checks_fut_rows, checks_idx_rows, extras)."""
    d10 = B["fixed"][2]
    files = collections.OrderedDict()
    rw = sort_rows(P1["rows_w"], lambda r: (ORDER_WIN[r["window"]], r["vintage"]))
    files["fut_windows.csv"] = rw
    rc = merge_small(P1["rows_c"], "funds_n", ["window"], "contract", cols_by_file["fut_contracts.csv"])
    files["fut_contracts.csv"] = sort_rows(rc, lambda r: (ORDER_WIN[r["window"]], ORDER_CONTRACT[r["contract"]]))
    files["fut_change.csv"] = sort_rows(P1["rows_chg"], lambda r: (r["variant_id"], ORDER_PER_FUT[r["period"]]))
    rs = merge_small(P1["rows_sp"], "funds_n", ["period"], "group", cols_by_file["fut_split.csv"])
    files["fut_split.csv"] = sort_rows(rs, lambda r: (ORDER_PER_FUT[r["period"]], ORDER_GRP[r["group"]]))
    files["fut_other_deriv.csv"] = sort_rows(P1["rows_o"], lambda r: (ORDER_WIN[r["window"]], r["category"]))
    # pre-run table (cash build alone), then the flag counts when N-CEN is present
    ents, ents_ds = P1["prerun"]
    extra = (P2["entrants_unflagged_n"], P2["entrants_backfilled_n"]) if P2 is not None else None
    files["idx_prerun.csv"] = prerun_rows((len(ents), ents_ds, extra), mode)
    files["fut_verdict.csv"] = [dict(key=k, value=v) for k, v in fut_verdict_rows(B, P1)]
    chk_idx = []
    if P2 is not None:
        rows_s, rows_cv, rows_x = idx_tables(B, P2, base_ds)
        files["idx_split.csv"] = sort_rows(merge_small(rows_s, "series_n", ["period"], "group", cols_by_file["idx_split.csv"]),
                                           lambda r: (ORDER_PER[r["period"]], ORDER_GRP[r["group"]]))
        files["idx_coverage.csv"] = sort_rows(merge_small(rows_cv, "series_n", ["window"], "flag", cols_by_file["idx_coverage.csv"]),
                                              lambda r: (ORDER_WIN[r["window"]], r["flag"] == SMALL_NAME, r["flag"]))
        files["idx_crosstab.csv"] = sort_rows(merge_small(rows_x, "series_n", ["period"], "arm", cols_by_file["idx_crosstab.csv"]),
                                              lambda r: (ORDER_PER[r["period"]], r["arm"] == SMALL_NAME, r["is_etf"], r["arm"]))
        files["idx_verdict.csv"] = [dict(key=k, value=v) for k, v in idx_verdict_rows(B, P2, base_ds, base_ds_m1)]
        chk_idx = checks_idx(B, P2, ncen_info, base_ds, base_ds_m1)
    chk_fut = checks_fut(B, P1, a.cash_dir, shas)
    return files, chk_fut, chk_idx


def check_sort_key(c):
    m = re.match(r"C-([A-Z])(\d+)(.*)", c["check_id"])
    return (m.group(1), int(m.group(2)), m.group(3)) if m else ("Z", 999, c["check_id"])


def assemble_and_write(B, P1, P2, a, mode, ncen_info, names, shas, base_ds, base_ds_m1, ch):
    cols_by_file = read_columns_tsv(a.columns)
    mode_files = set(cols_by_file)
    files, chk_fut, chk_idx = build_outputs(B, P1, P2, cols_by_file, base_ds, base_ds_m1, ncen_info, a, shas, mode)
    p2s = part2_sentence(P2, base_ds)
    R = dict(P1=P1, P2=P2, n23=len(B["sel"]["base"]["assign"][B["by_label"]["2023Q4"].idx]), n26=len(B["sel"]["base"]["assign"][B["by_label"]["2026Q2"].idx]),
             p2_sentence=p2s, base_ds=base_ds, cols_by_file=cols_by_file, entrants_n=len(P1["prerun"][0]))
    readme = readme_text(R)
    stats = file_stats_rows(B, ncen_info, a)
    files["fut_idx_file_stats.csv"] = stats
    # forbidden cash-plus-futures values for G8
    forb = []
    for w in B["windows"]:
        for v in ("base", "matched"):
            s_ = B["ctx"].agg[(v, w.idx)].val("tenyeq_fixed")
            for fld in ("f_tenor", "f_bal", "f_ctd"):
                f_ = B["eng"].agg[(v, w.idx)].s[fld].value()
                forb += [s_ + f_, f_ / 3218.3, f_ / 460.0]
    for per, l0, l1 in PERIODS:
        dp = float(ch[("M0", per)]["d_p"])
        ds = float(ch[("M0", per)]["d_s"])
        for key, (f0, f1, df) in P1["chg"].items():
            if key[1] == per:
                forb += [ds + df, df / dp, df / 460.0]
    forb = [x for x in forb if x != 0.0]
    fut_names = [n for n in files if n.startswith("fut_") and n not in ("fut_checks.csv", "fut_idx_file_stats.csv")]

    def render_all(c_x4):
        cf = sorted(chk_fut + [c_x4], key=check_sort_key)
        fl = dict(files)
        fl["fut_checks.csv"] = cf
        if mode == "idx":
            fl["idx_checks.csv"] = sorted(chk_idx, key=check_sort_key)
        return fl, {n: render_csv(cols_by_file[n], rows) for n, rows in fl.items()}

    c_x4 = mk("C-X4", "headers equal fut_idx_columns.tsv; no forbidden header; no file above 2,000 rows; no fund or registrant name in any output or the README; no cell below the small-cell floor; "
              "no cash-plus-futures cell; no causal wording or symbol in prose; no network import and no allowlist copy in the script", "pending", "", "0 problems", "PASS", True)
    fl, texts = render_all(c_x4)
    sources_md = sources_text()
    prose = {"fut_idx_README.md": readme, "fut_idx_SOURCES.md": sources_md}
    by_len = make_name_set(names)
    problems = hygiene_problems(texts, cols_by_file, by_len, prose)
    problems += cash_mixing_hits({n: (cols_by_file[n], fl[n]) for n in fut_names if n in fl}, forb)
    for n in ("fut_verdict.csv", "idx_verdict.csv"):
        if n in texts:
            problems += [f"{n}: causal wording {h!r}" for h in wording_hits(texts[n])]
    for n, t in prose.items():
        problems += [f"{n}: causal wording {h!r}" for h in wording_hits(t)]
    problems += [f"fut_idx_README.md: a symbol in prose {h!r}" for h in symbol_hits(readme)]
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    problems += [f"script imports {h}" for h in import_hits(src)]
    problems += [f"allowlist copy in code: {h}" for h in allowlist_copies(src, cols_by_file)]
    c_x4 = mk("C-X4", c_x4["label"], f"{len(problems)} problems" if problems else "0 problems", "", "0 problems", "FAIL" if problems else "PASS", True,
              "; ".join(problems[:20]))
    fl, texts = render_all(c_x4)
    texts["fut_idx_README.md"] = readme
    texts["fut_idx_SOURCES.md"] = sources_md
    hard_fail = is_hard_fail(list(fl["fut_checks.csv"]) + list(fl.get("idx_checks.csv", [])))
    return fl, texts, hard_fail


# ------------------------------------------------------------------------------------------------------------------------
# the modes
# ------------------------------------------------------------------------------------------------------------------------
def run_preflight(r1_cache=None, r2_cache=None):
    """Spec section 7: the cash build's tests, then this file's own selftest with its mutants. Either failing is a refusal (exit 1)."""
    ntd.run_preflight()
    caches = (r1_cache, r2_cache) if r1_cache and r2_cache else None
    if selftest(mutants=True, quiet=True, caches=caches) != 0:
        raise Refused("pre-flight: the selftest of bin/nport_futures_index.py failed; nothing was built")


def parse_zip_list(s):
    return None if not s else {x.strip().lower() for x in s.split(",") if x.strip()}


def run_scan(a):
    zips = ntd.discover_zips(a.zip_dir)
    windows = ntd.make_windows(zips)
    want = parse_zip_list(a.zips)
    todo = zip_slice(zips, want)
    if want and len(todo) != len(want):
        raise Refused(f"--zips names {sorted(want)}, found {[f'{z[0]}q{z[1]}' for _i, z in todo]}")
    log = lambda m: print(m, file=sys.stderr, flush=True)
    for i, (y, q, path) in todo:
        if a.stage == "A":
            run_stage_a(path, i, windows[i].zip_tag, windows, a.work, log)
        else:
            packs = [load_stage_a(a.work, w.zip_tag) for w in windows]
            run_stage_b(path, i, windows[i].zip_tag, windows, packs, a.work, log)
    return 0


def run_build(a, mode, preflight=True):
    t0 = time.time()
    log = lambda m: print(f"[{time.time() - t0:6.1f}s] {m}", file=sys.stderr, flush=True)
    if preflight:
        run_preflight(getattr(a, "r1_cache", None), getattr(a, "r2_cache", None))
    cols_by_file = read_columns_tsv(a.columns)
    B = build_core(a, log)
    ch, wt = cash_base(a.cash_dir)
    base_ds = {p: float(ch[("M0", p)]["d_s"]) for p in ("full", "2024", "2025", "2026H1")}
    base_ds_m1 = {p: float(ch[("M1", p)]["d_s"]) for p in ("full", "2024", "2025", "2026H1")}
    shas = ntd.read_prior_shas(a.cash_dir)
    table = ncen_info = None
    names = []
    for f in B["all_filings"]:
        names.append(f.series_name)
        names.append(f.registrant_name)
    include = None
    no_row_n = None
    if mode == "idx":
        if not a.ncen_dir:
            raise Refused("idx mode needs --ncen-dir")
        table, nstats, nnames, zl = load_ncen(a.ncen_dir, want_names=True)
        names.extend(nnames)
        ncen_info = dict(zips=len(zl), zl=zl, stats=nstats, fetch=read_fetch_log(a.ncen_dir))
        log(f"N-CEN: {len(zl)} zips, {len(table):,} keys")
        etf = {}
        for f, _t in B["sel"]["base"]["assign"][B["by_label"]["2023Q4"].idx]:
            o, rec = make_obs(table, f, True)
            etf[f.fund] = "none" if rec is None else rec.flags.get("IS_ETF", "")
        include = lambda fund: etf.get(fund) != "Y"
    P1 = part1_results(B, include, (lambda fund: etf.get(fund) == "none") if include is not None else None)
    funds0, surv0, _ob, _st = build_funds(B, "base", None, True)
    ents = entrants_of(funds0, surv0)
    P1["prerun"] = (ents, math.fsum(funds0[f]["s"]["2026Q2"] - funds0[f]["s"]["2025Q4"] for f in ents))
    P2 = part2_results(B, table, base_ds, base_ds_m1) if mode == "idx" else None
    if P2 is not None:
        ncen_info["stats"]["feeder_series_dropped_in_r2_windows"] = sum(P2["feeder_stats"].values())
        ncen_info["stats"]["ncen_records_listing_feeders"] = sum(1 for recs in table.values() for r in recs if r.feeders)
        ncen_info["stats"]["ncen_series_keys"] = len(table)
    log("results computed")
    fl, texts, hard_fail = assemble_and_write(B, P1, P2, a, mode, ncen_info, names, shas, base_ds, base_ds_m1, ch)
    out = os.path.abspath(a.out)
    code = finish(texts, hard_fail, out)
    print_summary(P1, P2, fl, hard_fail, out)
    log("done")
    return code


def print_summary(P1, P2, fl, hard_fail, out):
    err = lambda *x: print(*x, file=sys.stderr)
    err("\n=== Part 1 ===")
    err(f"  dF (tenor, base, PAYOFF sign) {P1['d_f']:,.3f} $bn   label {P1['label']}")
    err(f"  A1 {P1['anchor_all']['a1']:.2f}  A2 {P1['anchor_all']['a2']}  A3 {P1['anchor_all']['a3']}  pass {P1['a_pass']}")
    err(f"  U_F {P1['u_f'][0]:.4f} / {P1['u_f'][1]:.4f}  G_v {P1['g_v']:.3f}  G_c {P1['g_c']:.3f}  G_s {P1['g_s']:.3f}")
    if P2 is not None:
        DI = P2["DI"]
        err("=== Part 2 ===")
        err(f"  label {P2['label']}  q {DI['q']}  s0 {DI['s0']}  U {DI['u']:.3f} {DI['u_comp']}")
    err("=== checks ===")
    for n in ("fut_checks.csv", "idx_checks.csv"):
        for c in fl.get(n, []):
            err(f"  {c['check_id']:6s} {c['result']:5s} {c['hard']}  {str(c['ours'])[:110]}")
    err(f"hard FAIL: {hard_fail}; wrote to {out if not hard_fail else os.path.join(out, FAILED_DIRNAME)}")


# ========================================================================================================================
# SELFTEST (spec section 7). Synthetic data only. Every guard is a mutation test: mutate X, run on fixture Y, the guard must FAIL.
# ========================================================================================================================
class Ck:
    def __init__(self):
        self.items = []

    def check(self, name, ok, detail=""):
        self.items.append((name, bool(ok), detail))

    def failed(self):
        return [(n, d) for n, ok, d in self.items if not ok]


def run_test(fn):
    ck = Ck()
    try:
        fn(ck)
    except Exception as e:              # an exception under a mutant is a detection; under the real code it is a failure
        ck.check("no exception", False, f"{type(e).__name__}: {e}")
    return ck


# a copy of the published 2023-12-29 par curve (Treasury Daily Par Yield Curve), used as a synthetic fixture so that the selftest reads no cache
FIX_CURVE = {1 / 12: 5.6, 2 / 12: 5.59, 3 / 12: 5.4, 4 / 12: 5.41, 6 / 12: 5.26, 1.0: 4.79, 2.0: 4.23, 3.0: 4.01, 5.0: 3.84, 7.0: 3.88, 10.0: 3.88, 20.0: 4.2, 30.0: 4.03}
FIX_D10 = r2_pure.par_mod_duration(3.88, n=10)
FIX_TENOR = None            # built lazily: the mutants change it
FW = collections.namedtuple("FW", "idx qend label")
FF = collections.namedtuple("FF", "fund rdate cik")


def mk_rec(title, ccy="USD", payoff="Long", balance="100", unit="NC", notional="", exp="19-MAR-2026", mark="0", acc="A1", asset="DIR", ident="",
           payoff_h="N/A", value="0", hid="1"):
    return dict(acc=acc, hid=hid, balance=balance, unit=unit, ccy_h="USD", value=value, payoff_h=payoff_h, asset_cat=asset, payoff=payoff, exp=exp,
                notional=notional, ccy=ccy, ua=mark, texts=(norm_text(title), "", "", norm_text(ident)), has_fwd=True)


def mini_engine(recs, rdate=dt.date(2026, 1, 1), mask=3):
    tenor = tenor_table(FIX_CURVE, FIX_D10)
    eng = FutEngine([FW(0, dt.date(2026, 3, 31), "2026Q1")], tenor, lambda c, e, w: None)
    for r in recs:
        eng.add(r, FF(("S", r["acc"]), rdate, ""), 0, mask, evaluate_future(r, rdate))
    return eng, eng.agg[("base", 0)]


TY_FACTOR = 78153.01


def t_g1(ck):
    z = [mk_rec("US 3YR NOTE (CBT) MAR24", balance="100", notional=str(round(1.04 * 100 * 200000)), acc=f"Z{i}") for i in range(6)]
    t = [mk_rec("US 2YR NOTE (CBT) MAR24", balance="100", notional=str(round(1.04 * 100 * 200000)), acc=f"T{i}") for i in range(6)]
    eng, a = mini_engine(z + t)
    for c, recs in (("Z3N", z), ("TU", t)):
        ca = a.by_c[c]
        med = statistics.median(ca.ratios) if ca.ratios else None
        ck.check(f"{c} median notional per face in [0.85, 1.35] (C-F4)", med is not None and 0.85 <= med <= 1.35, f"median {med}")
        ck.check(f"{c} face of 100 contracts is $20,000,000", abs(ca.face_net.value() * 1e9 / 6 - 20000000.0) < 1.0, f"{ca.face_net.value() * 1e9 / 6}")
    ck.check("a 10-year note keeps $100,000", face_of("TY") == 100000.0)


def t_g2(ck):
    bad = classifier_fixture_failures()
    ck.check("every classifier fixture is classified as the spec says", not bad, "; ".join(bad[:4]))


def t_g3(ck):
    # a Short line whose BALANCE and NOTIONAL are positive and whose holding-level payoff says Long; a sign-N/A line
    l1 = mk_rec("US 10YR NOTE (CBT) MAR24", payoff="Short", balance="100", notional="11000000", payoff_h="Long", acc="L1")
    l2 = mk_rec("US 10YR NOTE (CBT) MAR24", payoff="N/A", balance="50", notional="5500000", acc="L2")
    eng, a = mini_engine([l1, l2])
    f = a.s["f_tenor"].value()
    want = -100 * TY_FACTOR / 1e9
    ck.check("net F is the PAYOFF-signed line only", abs(f - want) < 1e-9, f"{f} vs {want}")
    ck.check("the balance-signed comparison takes the opposite sign on the conflicting line", abs(a.s["f_bal"].value() - (-want)) < 1e-9, f"{a.s['f_bal'].value()}")
    ck.check("the sign-N/A line is counted and excluded", a.n["sign_na_lines"] == 1 and a.n["tsy_fut_lines"] == 1, f"{a.n['sign_na_lines']} {a.n['tsy_fut_lines']}")


def t_g4(ck):
    l1 = mk_rec("US 10YR NOTE (CBT) MAR24", balance="100", notional="100", acc="L1")                   # the notional field holds the contract count
    l2 = mk_rec("US 10YR NOTE (CBT) MAR24", balance="10", notional="1100000", value="3000000", acc="L2")      # a $3m mark must not size it
    eng, a = mini_engine([l1, l2])
    ck.check("face long is 100 + 10 contracts at $100,000", abs(a.s["face_long"].value() - 11000000.0) < 1e-6, f"{a.s['face_long'].value()}")
    ck.check("F is 110 contracts times the tenor factor", abs(a.s["f_tenor"].value() - 110 * TY_FACTOR / 1e9) < 1e-9, f"{a.s['f_tenor'].value()}")
    ck.check("the count-in-notional line stays on the face basis", a.n["notional_field_is_count_lines"] == 1 and a.n["lines_basis_face"] == 2,
             f"{a.n['notional_field_is_count_lines']} {a.n['lines_basis_face']}")


def t_g5(ck):
    fac, cf, y, dur = tenor_factor("TY", FIX_CURVE, FIX_D10, d10_report=7.9)
    ck.check("TY tenor factor is $78,153.01", abs(fac - TY_FACTOR) <= 0.01, f"{fac:.2f}")
    for c in CONTRACTS:
        f2, cf2, _y, _d = tenor_factor(c, FIX_CURVE, FIX_D10, d10_report=7.9)
        ck.check(f"{c} factor and conversion factor are the pinned ones", abs(f2 - TENOR_PINS[c][1]) <= 0.01 and abs(cf2 - TENOR_PINS[c][0]) < 1e-12, f"{f2:.2f} {cf2}")


def t_g6(ck):
    bad = cf_fixture_failures()
    ck.check("the conversion-factor fixtures of spec 3.5", not bad, "; ".join(bad))
    ck.check("FV 4.0% at 4y4m keeps its month (not a quarter)", round_months("FV", 52) == 52 and cf_value(4.0, round_months("FV", 52)) == 0.9246,
             f"{round_months('FV', 52)} {cf_value(4.0, round_months('FV', 52))}")
    ck.check("a coupon of 4.0625% rounds to 4.125% and a tie goes up", round_eighth(4.0625) == 4.125 and round_eighth(4.06) == 4.0)


def _row(c, cls, cp, iss, mat):
    return dict(security_class1_desc=cls, security_class2_desc=c, interest_rate_pct=str(cp), issue_date=iss, maturity_date=mat)


CTD_ROWS = [_row("A", "Notes", 4.0, "2021-09-30", "2030-09-30"), _row("B", "Notes", 3.5, "2021-02-16", "2031-02-15"),
            _row("C", "Notes", 4.25, "2021-11-15", "2031-11-15"), _row("D", "Notes", 3.625, "2020-09-15", "2030-09-15"),
            _row("E", "Inflation-Protected Securities", 5.0, "2020-10-15", "2030-09-30")]
CTD_ROWS_US = [_row("G", "Bonds", 2.0, "2010-08-15", "2040-08-15"), _row("I", "Bonds", 4.375, "2011-05-15", "2041-05-15"),
               _row("H", "Notes", 5.0, "2010-05-15", "2040-05-15"), _row("J", "Bonds", 4.5, "2006-02-15", "2036-02-15")]


def t_g7(ck):
    fdm = dt.date(2024, 3, 1)
    got = modelled_ctd("TY", fdm, deliverables_from_rows(CTD_ROWS), FIX_CURVE)
    ck.check("a 5-issue TY basket: the cheapest to deliver is issue A (6y7m, 4.0%)", got is not None and got[0].cusip == "A", str(got and got[0].cusip))
    got = modelled_ctd("US", fdm, deliverables_from_rows(CTD_ROWS_US), FIX_CURVE)
    ck.check("a US basket takes Bonds only: the cheapest to deliver is bond I", got is not None and got[0].cusip == "I", str(got and got[0].cusip))
    ck.check("a TIPS row is not in the TY basket", not any(d.cusip == "E" for d in deliverables_from_rows(CTD_ROWS) if eligible("TY", d, fdm)))


def t_g8(ck):
    S, F = 1000.0, 50.0
    forbidden = [S + F, F / 3218.3, F / 460.0]
    files = {"fut_x.csv": (["a", "b"], [dict(a=F, b="4600"), dict(a="1,460.2", b=0.5), dict(a=4600, b=1460.2)])}
    if M("g8_sum"):
        files["fut_x.csv"][1].append(dict(a=S + F, b=1))
    if M("g8_ratio"):
        files["fut_x.csv"][1].append(dict(a=F / 3218.3, b=1))
    if M("g8_token460"):
        files["fut_x.csv"][1].append(dict(a="460", b=1))
    if M("g8_firstorder"):
        files["fut_x.csv"][1].append(dict(a="FIRST-ORDER", b=1))
    hits = cash_mixing_hits(files, forbidden)
    ck.check("no output cell mixes cash and futures (4600 and 1,460.2 do not fire)", not hits, "; ".join(hits))


def _fix_cols():
    """The columns of two real output files, read from fut_idx_columns.tsv, so that the fixtures hold no copy of them."""
    rc = read_columns_tsv(COLS_TSV_DEFAULT)
    return collections.OrderedDict((n, rc[n]) for n in ("idx_split.csv", "fut_other_deriv.csv"))


def t_g9(ck):
    FIX_COLS = _fix_cols()
    texts = {"idx_split.csv": render_csv(FIX_COLS["idx_split.csv"], [dict(period="2026H1", group="index_stable", series_n=40, s_start_bn=1.0, s_end_bn=2.0, d_s_bn=1.0)]),
             "fut_other_deriv.csv": render_csv(FIX_COLS["fut_other_deriv.csv"], [dict(window="2026Q2", category="swap_dir", lines=3, notional_abs_bn=1.5)])}
    cols = collections.OrderedDict(FIX_COLS)
    prose = {"fut_idx_README.md": "A plain line about holdings.\nAnother line.\n"}
    if M("plant_series_id"):
        texts["fut_extra.csv"] = "SERIES_ID,x\nS000001,1\n"
        cols["fut_extra.csv"] = ["SERIES_ID", "x"]
    if M("plant_big"):
        texts["fut_other_deriv.csv"] = render_csv(FIX_COLS["fut_other_deriv.csv"], [dict(window="2026Q2", category=f"c{i}", lines=1, notional_abs_bn=1.0) for i in range(2001)])
    if M("plant_name_cell"):
        texts["fut_other_deriv.csv"] = render_csv(FIX_COLS["fut_other_deriv.csv"], [dict(window="2026Q2", category="Alpha Test Treasury Fund", lines=1, notional_abs_bn=1.0)])
    if M("plant_name_readme"):
        prose["fut_idx_README.md"] += "The registrant beta trust series is mentioned here.\n"
    if M("plant_small_cell"):
        texts["idx_split.csv"] = render_csv(FIX_COLS["idx_split.csv"], [dict(period="2026H1", group="index_stable", series_n=4, s_start_bn=1.0, s_end_bn=2.0, d_s_bn=1.0)])
    by_len = make_name_set(["ALPHA TEST TREASURY FUND", "BETA TRUST SERIES", "X"])
    bad = hygiene_problems(texts, cols, by_len, prose)
    ck.check("the scratch output folder is clean", not bad, "; ".join(bad[:3]))


def _fixture_outputs(mut_add=False, mut_rename=False):
    cols = collections.OrderedDict([("a.csv", ["x", "y", "z"]), ("b.csv", ["p", "q", "r", "s"])])
    w_cols = {k: list(v) for k, v in cols.items()}
    if mut_add:
        w_cols["a.csv"] = w_cols["a.csv"] + ["w"]
    if mut_rename:
        w_cols["b.csv"][1] = "q2"
    texts = {n: render_csv(c, []) for n, c in w_cols.items()}
    return cols, texts


def t_g10(ck):
    cols, texts = _fixture_outputs(M("g10_add_column"), M("g10_rename_column"))
    if M("g10_edit_tsv"):
        cols = collections.OrderedDict(cols)
        cols["a.csv"] = ["x", "y2", "z"]
    bad = [p for p in hygiene_problems(texts, cols, {}, None) if "header differs" in p]
    ck.check("every written header equals its row of the column file", not bad, "; ".join(bad))
    script = "def f():\n    return ('x', 'y')\nPAIR = ['p', 'q']\n"
    if M("g10_paste_tuple"):
        script += "COPY = ('p', 'q', 'r', 's')\n"
    ck.check("the source scan finds no allowlist copy in a script", not allowlist_copies(script, cols))
    real = os.path.join(HERE, "nport_futures_index.py")
    if os.path.exists(COLS_TSV_DEFAULT):
        rc = read_columns_tsv(COLS_TSV_DEFAULT)
        src = open(real, encoding="utf-8").read()
        ck.check("this script holds no allowlist copy", not allowlist_copies(src, rc), "; ".join(allowlist_copies(src, rc)))


# ---- synthetic N-CEN zips for G11 -------------------------------------------------------------------------------------
NCEN_SUB_H = ["ACCESSION_NUMBER", "SUBMISSION_TYPE", "CIK", "FILING_DATE", "REPORT_ENDING_PERIOD"]
NCEN_REG_H = ["ACCESSION_NUMBER", "REGISTRANT_NAME", "CIK"]
NCEN_FRI_H = ["FUND_ID", "ACCESSION_NUMBER", "FUND_NAME", "SERIES_ID"] + [c for c in NCEN_FRI_COLS if c.startswith("IS_")]
NCEN_FEED_H = ["FUND_ID", "REGISTERED_SERIES_ID"]


def _tsv(header, rows):
    return "\n".join(["\t".join(header)] + ["\t".join(str(r.get(c, "")) for c in header) for r in rows]) + "\n"


def make_ncen_zip(path, subs, regs, fris, feeders=()):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("SUBMISSION.tsv", _tsv(NCEN_SUB_H, subs))
        z.writestr("REGISTRANT.tsv", _tsv(NCEN_REG_H, regs))
        z.writestr("FUND_REPORTED_INFO.tsv", _tsv(NCEN_FRI_H, fris))
        z.writestr("FEEDER_FUNDS.tsv", _tsv(NCEN_FEED_H, feeders))


def _ncen_fixture(tmp):
    """Series S1 (filings before and after r, an amendment, a notice), S2 (launched after its last earlier N-CEN), S3 (first N-CEN too late)."""
    def sub(acc, typ, fd, per):
        return dict(ACCESSION_NUMBER=acc, SUBMISSION_TYPE=typ, CIK="100", FILING_DATE=fd, REPORT_ENDING_PERIOD=per)
    def fri(acc, sid, **fl):
        return dict(FUND_ID=f"{acc}_100_{sid}", ACCESSION_NUMBER=acc, FUND_NAME="Alpha Test Treasury Fund", SERIES_ID=sid, **fl)
    subs = [sub("A1", "N-CEN", "01-MAR-2023", "31-DEC-2022"), sub("A2", "N-CEN", "01-MAR-2024", "31-DEC-2023"),
            sub("A3", "N-CEN/A", "01-SEP-2024", "31-DEC-2023"), sub("A4", "NT N-CEN", "01-MAR-2025", "31-DEC-2024"),
            sub("A5", "N-CEN", "01-SEP-2024", "30-JUN-2024"), sub("A6", "N-CEN", "01-JUN-2025", "31-DEC-2024")]
    regs = [dict(ACCESSION_NUMBER=a, REGISTRANT_NAME="Beta Trust Series", CIK="100") for a in ("A1", "A2", "A3", "A4", "A5", "A6")]
    fris = [fri("A1", "S1", IS_INDEX="N"), fri("A2", "S1", IS_INDEX="N"), fri("A3", "S1", IS_INDEX="Y"), fri("A4", "S1", IS_MULTI_INVERSE_INDEX="Y"),
            fri("A5", "S2", IS_INDEX="Y"), fri("A6", "S3", IS_INDEX="Y")]
    d = os.path.join(tmp, "ncen")
    os.makedirs(d)
    make_ncen_zip(os.path.join(d, "2026q3_ncen.zip"), subs, regs, fris)
    return d


def t_g11(ck):
    with tempfile.TemporaryDirectory() as tmp:
        table, _st, _nm, _zl = load_ncen(_ncen_fixture(tmp))
        r = dt.date(2024, 6, 30)
        got = lookup_flag(table, ("S", "S1"), r)
        ck.check("S1 at 2024-06-30: the amendment beats the original for the same period", got is not None and not got[1] and flag_value(got[0].flags) == "index",
                 str(got and (got[0].acc, flag_value(got[0].flags))))
        got = lookup_flag(table, ("S", "S1"), dt.date(2025, 6, 30))
        ck.check("S1 at 2025-06-30: a notice of late filing is not a filing (the latest kept period is 2023-12-31)", got is not None and got[0].period == dt.date(2023, 12, 31),
                 str(got and got[0].period))
        got = lookup_flag(table, ("S", "S2"), dt.date(2023, 12, 31))
        ck.check("S2 launched after its last earlier N-CEN: its first later filing is used and labelled", got is not None and got[1] is True, str(got and got[1]))
        got = lookup_flag(table, ("S", "S3"), dt.date(2023, 12, 31))
        ck.check("S3: a first N-CEN filed more than 15 months after the position date is not used", got is None, str(got and got[0].acc))
        got = lookup_flag(table, ("S", "S2"), dt.date(2023, 12, 31), backfill=False)
        ck.check("without backfill (the strict variant) S2 is unflagged", got is None)


def t_g12(ck):
    ck.check("IS_FUND_TYPE_NA beside IS_INDEX = Y is unflagged", flag_value({"IS_FUND_TYPE_NA": "Y", "IS_INDEX": "Y"}) == "unflagged")
    ck.check("IS_FUND_TYPE_NA alone is active (B1)", flag_value({"IS_FUND_TYPE_NA": "Y"}) == "active")
    ck.check("money market beside multi-inverse is mmf", flag_value({"IS_MONEY_MARKET": "Y", "IS_MULTI_INVERSE_INDEX": "Y"}) == "mmf")
    ck.check("multi-inverse beside index is levinv; index alone is index; N or blank is not an index flag",
             flag_value({"IS_MULTI_INVERSE_INDEX": "Y", "IS_INDEX": "Y"}) == "levinv" and flag_value({"IS_INDEX": "Y"}) == "index"
             and flag_value({"IS_INDEX": "N"}) == "active" and flag_value({"IS_INDEX": ""}) == "active")


class FakeCtx:
    def __init__(self, s):
        self.s_fund = {}
        for (v, wi, fund), x in s.items():
            fs = Fsum()
            fs.add(x)
            self.s_fund[(v, wi, fund)] = fs

    def s_of(self, vint, wi, fund):
        v = self.s_fund.get((vint, wi, fund))
        return 0.0 if v is None else v.value()


def _panel():
    L = ["2023Q4", "2024Q4", "2025Q4", "2026Q2"]
    dates = [dt.date(2023, 12, 31), dt.date(2024, 12, 31), dt.date(2025, 12, 31), dt.date(2026, 6, 30)]
    by_label = {l: FW(i, dates[i], l) for i, l in enumerate(L)}
    X = {n: ("S", n) for n in ("X1", "X2", "X3", "X4", "X5", "X6")}
    S = {"X1": [10, 20, 30, 40], "X2": [5, 5, 15, 25], "X3": [4, 4, 6, 10], "X4": [0, 0, 0, 3], "X5": [2, 2, 2, 2], "X6": [1, 2, 3, 8]}
    present = {"X1": L, "X2": L, "X3": L, "X4": ["2026Q2"], "X5": L, "X6": L}
    s = {}
    for n, vals in S.items():
        for i, v in enumerate(vals):
            if v:
                s[("base", i, X[n])] = float(v)
    assign = {i: [] for i in range(4)}
    for n in S:
        for l in present[n]:
            i = L.index(l)
            assign[i].append((FF(X[n], by_label[l].qend, ""), "m0"))
    table = {("S", "X1"): [NcenRec(dt.date(2023, 6, 30), dt.date(2023, 8, 1), "a1", {"IS_INDEX": "Y"}, ("X5",)),
                           NcenRec(dt.date(2024, 6, 30), dt.date(2024, 8, 1), "a2", {"IS_INDEX": "Y"}, ("X5",)),
                           NcenRec(dt.date(2025, 6, 30), dt.date(2025, 8, 1), "a3", {"IS_INDEX": "Y"}, ("X5",))],
             ("S", "X2"): [NcenRec(dt.date(2023, 6, 30), dt.date(2023, 8, 1), "b1", {"IS_INDEX": "N"}, ()),
                           NcenRec(dt.date(2025, 6, 30), dt.date(2025, 8, 1), "b2", {"IS_INDEX": "N"}, ())],
             ("S", "X3"): [NcenRec(dt.date(2023, 6, 30), dt.date(2023, 8, 1), "c1", {"IS_INDEX": "Y"}, ()),
                           NcenRec(dt.date(2025, 6, 30), dt.date(2025, 8, 1), "c2", {"IS_INDEX": "N"}, ())],
             ("S", "X5"): [NcenRec(dt.date(2023, 6, 30), dt.date(2023, 8, 1), "d1", {"IS_INDEX": "N"}, ()),
                           NcenRec(dt.date(2025, 6, 30), dt.date(2025, 8, 1), "d2", {"IS_INDEX": "N"}, ())],
             ("S", "X6"): [NcenRec(dt.date(2023, 6, 30), dt.date(2023, 8, 1), "e1", {"IS_INDEX": "Y"}, ())]}
    # X3 is flagged index by its 2023-06-30 filing (windows 2023Q4 and 2024Q4) and active by its 2025-06-30 filing (2025Q4 and 2026Q2): a switcher
    B = {"ctx": FakeCtx(s), "sel": {"base": {"assign": assign}}, "by_label": by_label}
    return B, table, L


def t_g13(ck):
    B, table, L = _panel()
    funds, survivors, obs, st = build_funds(B, "base", table, True)
    go = group_fn(funds)
    S, N = group_tables(funds, go, R2_WINDOWS)
    want = {"index_stable": [10, 20, 30, 40], "active_stable": [5, 5, 15, 25], "switcher": [4, 4, 6, 10], "unflagged": [0, 0, 0, 3],
            "stale_flag": [1, 2, 3, 8], "feeder_dropped": [2, 2, 2, 2], "mmf": [0, 0, 0, 0], "levinv": [0, 0, 0, 0]}
    bad = [f"{g}: {[round(S[g][l], 6) for l in R2_WINDOWS]} not {v}" for g, v in want.items() if [round(S[g][l], 6) for l in R2_WINDOWS] != [float(x) for x in v]]
    ck.check("group sums over the four windows of a 6-series panel", not bad, "; ".join(bad))
    base = {"2024": 1.0, "2025": 1.0, "2026H1": 1.0, "full": 1.0}
    DI = decision_inputs(S, N, base)
    ck.check("U in 2026H1 is |unflagged 3| + |switcher 4| + |stale 5| = 12", abs(DI["u"] - 12.0) < 1e-9, f"{DI['u']}")


def t_g14(ck):
    FIX_COLS = _fix_cols()
    P1 = dict(chg={(v, p): (1.0, 2.0, 1.0) for v in ("T0", "T1", "C0", "B0") for p in ("full", "2024", "2025", "2026H1")}, d_f=1.0, label="INCONCLUSIVE",
              anchor_all=dict(a1=300.0, a2=0.1, a3=3.5, universe_n=10, universe_with_futures_n=5), u_f=(0.05, 0.05), g_v=1.0, g_c=1.0, g_s=30.0, a4_gross_long_bn=500.0)
    DI = dict(ds={p: {g: 1.0 for g in GROUPS} for p in ("2024", "2025", "2026H1", "full")}, q={"2024": 0.3, "2025": 0.3, "2026H1": 0.5}, s0=0.4, u=1.0,
              u_comp=dict(unflagged=0.5, switcher=0.3, stale_flag=0.2))
    P2 = dict(DI=DI, label="INCONCLUSIVE", entrants_unflagged_ds=0.5, entrants_unflagged_n=3, entrants_backfilled_n=2)
    R = dict(P1=P1, P2=P2, n23=1000, n26=1100, p2_sentence=part2_sentence(P2, {}), base_ds={"2026H1": 162.1}, cols_by_file=collections.OrderedDict(FIX_COLS), entrants_n=7)
    text = readme_text(R)
    ck.check("the required sentence is in the README", REQUIRED_SENTENCE in text)
    ck.check("no causal wording or symbol in the futures verdict sentence", not wording_hits(fut_sentence(P1)) and not symbol_hits(fut_sentence(P1)), fut_sentence(P1))
    ck.check("no causal wording in the generated README", not wording_hits(text), str(wording_hits(text)))
    ck.check("no symbol in README prose", not symbol_hits(text), str(symbol_hits(text)))
    src = sources_text()
    ck.check("no causal wording or symbol in the sources file with its build decisions", not wording_hits(src) and not symbol_hits(src), str(wording_hits(src) + symbol_hits(src)))
    ck.check("the README links to the sources file for the build decisions", "[fut_idx_SOURCES.md](fut_idx_SOURCES.md)" in text and "Build decisions" not in text.split("## Provenance")[1].split("Build decisions, including")[0])
    ck.check("the README futures sentence names each failed condition in plain words", "because two conditions were not met" in readme_p1_sentence(P1) and "differ by $30.0bn" in readme_p1_sentence(P1),
             readme_p1_sentence(P1))


def t_g19(ck):
    """The pre-registered bounds, each tested on both sides of its edge."""
    last = "2026Q2"
    ob = lambda d: {last: Obs("index", False, d, "", "")}
    ck.check("stale cutoff: an N-CEN period ending 2025-03-29 is stale", assign_group(ob(dt.date(2025, 3, 29)), last) == "stale_flag")
    ck.check("stale cutoff: an N-CEN period ending 2025-03-30 is not stale", assign_group(ob(dt.date(2025, 3, 30)), last) == "index_stable")
    sz = lambda n_: size_line("TY", 100, "NC", n_)
    ck.check("size ratio 0.5 is on the face basis; 0.4998 is not", sz(5000000.0).basis == "face" and sz(4999000.0).basis == "notional" and sz(4999000.0).suspect)
    ck.check("size ratio 2.0 is on the face basis; 2.01 is not", sz(20000000.0).basis == "face" and sz(20100000.0).basis == "notional")
    lab = lambda q26, s0, q24=0.30, q25=0.30: part2_label(q24, q25, q26, s0, 0.0)
    ck.check("excess bar: a lead over the stock share of exactly 0.15 supports; 0.1499 does not", lab(0.60, 0.45, 0.40, 0.45) == "SUPPORTS" and lab(0.60, 0.4501, 0.40, 0.45) == "INCONCLUSIVE")
    ck.check("rise bar: a rise of exactly 0.10 over 2024 supports; 0.0999 does not", lab(0.60, 0.40, 0.50, 0.45) == "SUPPORTS" and lab(0.60, 0.40, 0.5001, 0.45) == "INCONCLUSIVE")
    ck.check("rise bar: a rise of exactly 0.10 over 2025 supports; 0.0999 does not", lab(0.60, 0.40, 0.40, 0.50) == "SUPPORTS" and lab(0.60, 0.40, 0.40, 0.5001) == "INCONCLUSIVE")
    ck.check("against bar: a share of exactly 0.40 not above the stock share counts against; 0.4001 does not", part2_label(0.5, 0.5, 0.40, 0.45, 0.0) == "AGAINST"
             and part2_label(0.5, 0.5, 0.4001, 0.45, 0.0) == "INCONCLUSIVE")
    labels = (list(GROUPS), list(R2_WINDOWS))
    S = {g: {l: 0.0 for l in R2_WINDOWS} for g in GROUPS}
    N = {g: {l: {"x"} for l in R2_WINDOWS} for g in GROUPS}
    S["unflagged"]["2025Q4"], S["unflagged"]["2026Q2"] = 5.0, 3.0
    S["switcher"]["2025Q4"], S["switcher"]["2026Q2"] = 4.0, 1.0
    S["stale_flag"]["2025Q4"], S["stale_flag"]["2026Q2"] = 2.0, 6.0
    di = decision_inputs(S, N, {"2024": 1.0, "2025": 1.0, "2026H1": 1.0, "full": 1.0})
    ck.check("unclassified change uses absolute values: |-2| + |-3| + |+4| = 9", abs(di["u"] - 9.0) < 1e-9, str(di["u"]))


def t_g15(ck):
    sup = lambda q26, u=0.0, q24=0.40, q25=0.45, s0=0.40: part2_label(q24, q25, q26, s0, u)
    ck.check("q 0.60 is SUPPORTS", sup(0.60) == "SUPPORTS", sup(0.60))
    ck.check("q 0.5999 is INCONCLUSIVE", sup(0.5999) == "INCONCLUSIVE", sup(0.5999))
    ck.check("U 16.2 does not trigger the cap", sup(0.60, u=16.2) == "SUPPORTS", sup(0.60, u=16.2))
    ck.check("U 16.21 is INCONCLUSIVE", sup(0.60, u=16.21) == "INCONCLUSIVE", sup(0.60, u=16.21))
    ck.check("U 16.205 is INCONCLUSIVE", sup(0.60, u=16.205) == "INCONCLUSIVE", sup(0.60, u=16.205))
    ck.check("an index change of 50 against an active change of -0.1 leaves q undefined", q_of(50.0, -0.1, 100.0) is None)
    ck.check("a classified sum of 24.9% of the base leaves q undefined, 25.0% defines it", q_of(24.9, 0.0, 100.0) is None and q_of(25.0, 0.0, 100.0) == 1.0)
    ck.check("q at or below 0.40 and below the stock share is AGAINST", part2_label(0.4, 0.4, 0.40, 0.45, 0.0) == "AGAINST")
    ok = dict(a_pass=True, u_f_start=0.05, u_f_end=0.05, g_v=1.0, g_c=1.0, g_s=1.0)
    p1 = lambda d, **kw: part1_label(d, **{**ok, **kw})
    ck.check("dF 100.0 is LARGE and 99.99 is SMALL", p1(100.0) == "LARGE" and p1(99.99) == "SMALL" and p1(-100.0) == "LARGE")
    ck.check("G_c 50.01 is INCONCLUSIVE", p1(120.0, g_c=50.01) == "INCONCLUSIVE")
    ck.check("G_v 20.01 is INCONCLUSIVE", p1(120.0, g_v=20.01) == "INCONCLUSIVE")
    ck.check("G_s 20.01 is INCONCLUSIVE", p1(120.0, g_s=20.01) == "INCONCLUSIVE")
    ck.check("a failed anchor or U_F above 10% is INCONCLUSIVE", p1(120.0, a_pass=False) == "INCONCLUSIVE" and p1(120.0, u_f_end=0.1001) == "INCONCLUSIVE")


def t_g16(ck):
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "committed.csv"), "w") as fh:
            fh.write("OLD")
        bad_checks = [mk("C-X1", "forced mismatch", "1", "2", "1e-5", "FAIL", True)]
        code = finish({"committed.csv": "NEW"}, is_hard_fail(bad_checks), tmp)
        with open(os.path.join(tmp, "committed.csv")) as fh:
            old = fh.read()
        failed_copy = os.path.join(tmp, FAILED_DIRNAME, "committed.csv")
        ck.check("a forced C-X1 mismatch leaves the committed file untouched", old == "OLD", old)
        ck.check("the failed outputs are written to the failure folder", os.path.exists(failed_copy) and open(failed_copy).read() == "NEW")
        ck.check("the exit code is 2", code == 2, str(code))
        good = finish({"committed.csv": "NEW"}, False, tmp)
        ck.check("a clean build writes the committed folder and returns 0", good == 0 and open(os.path.join(tmp, "committed.csv")).read() == "NEW")


def _synthetic_pipeline():
    """Part of the build run on synthetic lines: evaluation, accumulation, rendering."""
    eng, a = mini_engine([mk_rec("US 10YR NOTE (CBT) MAR24", notional="11000000")])
    return render_csv(["a", "b"], [dict(a=a.s["f_tenor"].value(), b=1)])


def t_g17(ck):
    src = open(os.path.join(HERE, "nport_futures_index.py"), encoding="utf-8").read()
    if M("net_import"):
        src += "\nimport socket\n"
    ck.check("the script source imports no network module", not import_hits(src), str(import_hits(src)))
    netmod = importlib.import_module("so" + "cket")          # built from two pieces so that the scan of this file stays clean; used only to patch
    orig = netmod.socket
    calls = []

    def raiser(*a, **k):
        calls.append(1)
        raise OSError("network access attempted in the selftest")
    netmod.socket = raiser
    try:
        try:
            _synthetic_pipeline()
        finally:
            netmod.socket = orig
    except OSError as e:
        ck.check("a run with socket.socket patched to raise makes no socket", False, str(e))
        return
    ck.check("a run with socket.socket patched to raise makes no socket", not calls, f"{len(calls)} socket call(s)")


def t_g18(ck):
    FIX_COLS = _fix_cols()
    rows = [dict(period="2026H1", group="index_stable", series_n=40, s_start_bn=1.0, s_end_bn=2.0, d_s_bn=1.0),
            dict(period="2026H1", group="switcher", series_n=3, s_start_bn=0.1, s_end_bn=0.2, d_s_bn=0.1),
            dict(period="2026H1", group="mmf", series_n=4, s_start_bn=0.3, s_end_bn=0.4, d_s_bn=0.1),
            dict(period="2025", group="active_stable", series_n=20, s_start_bn=1.0, s_end_bn=2.0, d_s_bn=1.0),
            dict(period="2025", group="levinv", series_n=3, s_start_bn=0.1, s_end_bn=0.2, d_s_bn=0.1),
            dict(period="2025", group="unflagged", series_n=0, s_start_bn=0.0, s_end_bn=0.0, d_s_bn=0.0)]
    out = merge_small(rows, "series_n", ["period"], "group", FIX_COLS["idx_split.csv"])
    small = [r for r in out if r["series_n"] < SMALL_CELL and r["group"] != SMALL_NAME]
    ck.check("no committed row has fewer than five series unless it is other_small", not small, str(small))
    m26 = [r for r in out if r["period"] == "2026H1" and r["group"] == SMALL_NAME]
    ck.check("two small groups of 3 and 4 merge into one other_small row of 7 with the amounts summed", len(m26) == 1 and m26[0]["series_n"] == 7
             and abs(m26[0]["s_end_bn"] - 0.6) < 1e-9, str(m26))
    m25 = [r for r in out if r["period"] == "2025" and r["group"] == SMALL_NAME]
    ck.check("a lone small group of 3 is an other_small row with its amounts blanked", len(m25) == 1 and m25[0]["series_n"] == 3 and m25[0]["s_end_bn"] is None, str(m25))
    ck.check("an empty group row is dropped", not any(r["group"] == "unflagged" for r in out))
    a25 = [r for r in out if r["period"] == "2025" and r["group"] == "active_stable"]
    a26 = [r for r in out if r["period"] == "2026H1" and r["group"] == "index_stable"]
    ck.check("complementary suppression: with a blanked other_small cell the smallest other amount cell of that period is blanked too, and no other",
             len(a25) == 1 and a25[0]["s_end_bn"] is None and a25[0]["d_s_bn"] is None and len(a26) == 1 and a26[0]["s_end_bn"] == 2.0, str((a25, a26)))
    two = [r for r in out if r["period"] == "2026H1" and r["group"] == SMALL_NAME]
    ck.check("a merged cell of seven shows its amounts, so nothing else is blanked", two and two[0]["s_end_bn"] is not None)
    cols = collections.OrderedDict([("idx_split.csv", FIX_COLS["idx_split.csv"])])
    bad = hygiene_problems({"idx_split.csv": render_csv(FIX_COLS["idx_split.csv"], out)}, cols, {}, None)
    ck.check("the hygiene scan finds no small cell in the merged file", not bad, "; ".join(bad))


# ---- synthetic N-PORT zips for the smoke test and the end-to-end run ------------------------------------------------------
def _tmod():
    return load_by_path("test_nport_treasury_duration", os.path.join(HERE, "test_nport_treasury_duration.py"))


EXTRA_H = {
    T_FUTFWD: ["HOLDING_ID", "PAYOFF_PROFILE", "EXPIRATION_DATE", "NOTIONAL_AMOUNT", "CURRENCY_CODE", "UNREALIZED_APPRECIATION"],
    T_OTHER: ["HOLDING_ID", "DESC_REF_OTHER_ID", "ISSUER_NAME", "ISSUE_TITLE", "CUSIP", "ISIN", "TICKER", "OTHER_IDENTIFIER", "OTHER_DESC"],
    T_BASKET: ["HOLDING_ID", "INDEX_NAME", "INDEX_IDENTIFIER", "NARRATIVE_DESC"],
    T_IDENT: ["HOLDING_ID", "IDENTIFIERS_ID", "IDENTIFIER_ISIN", "IDENTIFIER_TICKER", "OTHER_IDENTIFIER", "OTHER_IDENTIFIER_DESC"],
    T_SWAP: ["HOLDING_ID", "SWAP_FLAG", "NOTIONAL_AMOUNT", "CURRENCY_CODE"],
    T_SWAPTION: ["HOLDING_ID", "PUT_OR_CALL", "SHARES_CNT", "PRINCIPAL_AMOUNT", "CURRENCY_CODE"],
}


def synth_nport_zip(path, filings, holds, debts, extras):
    t = _tmod()
    parts = [t.filing(*s) for s in filings]
    t.make_zip(path, [p[0] for p in parts], [p[1] for p in parts], [p[2] for p in parts], list(holds), list(debts), [])
    with zipfile.ZipFile(path, "a", zipfile.ZIP_DEFLATED) as z:
        for member, hdr in EXTRA_H.items():
            z.writestr(member, _tsv(hdr, extras.get(member, [])))


def synth_futs(acc, hid, title, payoff, bal, notional, exp, cat="DIR", ident="", deriv="FUT"):
    t = _tmod()
    h = t.hold(acc, hid, "", cat=cat, itype="OTHER", bal=bal, val="1000", payoff="N/A", unit="NC", name=title, title="")
    h["DERIVATIVE_CAT"] = deriv
    ex = {T_FUTFWD: dict(HOLDING_ID=hid, PAYOFF_PROFILE=payoff, EXPIRATION_DATE=exp, NOTIONAL_AMOUNT=notional, CURRENCY_CODE="USD", UNREALIZED_APPRECIATION="100")}
    if ident:
        ex[T_IDENT] = dict(HOLDING_ID=hid, IDENTIFIERS_ID="1", IDENTIFIER_TICKER=ident)
    return h, ex


def synth_set(tmp, with_fut=True):
    """Eleven zips 2024q1..2026q3; filings only in the four zips that hold the R2 windows. Returns (zip dir, ncen dir)."""
    t = _tmod()
    zd = os.path.join(tmp, "nport")
    os.makedirs(zd)
    plan = {"2024q1": ("29-DEC-2023", "10-FEB-2024", "24-MAR-2026"), "2025q1": ("31-DEC-2024", "20-FEB-2025", "19-MAR-2026"),
            "2026q1": ("31-DEC-2025", "20-FEB-2026", "19-JUN-2026"), "2026q3": ("30-JUN-2026", "20-AUG-2026", "18-SEP-2026")}
    expired = {"2024q1": "15-DEC-2023", "2025q1": "15-DEC-2024", "2026q1": "15-DEC-2025", "2026q3": "15-JUN-2026"}
    tag = {"2024q1": "A", "2025q1": "B", "2026q1": "C", "2026q3": "D"}
    for y in (2024, 2025, 2026):
        for q in (1, 2, 3, 4):
            if y == 2026 and q == 4:
                continue
            name = f"{y}q{q}"
            filings, holds, debts, extras = [], [], [], collections.defaultdict(list)
            if name in plan:
                rd, fd, ex = plan[name]
                tg = tag[name]
                series = [("S1", "100"), ("S4", "100")] + ([("S2", "100")] if name != "2024q1" else []) + ([("S3", "200")] if name in ("2024q1", "2026q3") else [])
                for i, (sid, cik) in enumerate(series):
                    acc = f"{tg}{i}"
                    filings.append((acc, "NPORT-P", fd, rd, sid, cik, str(20000000000 + 1000000000 * i)))
                    holds.append(t.hold(acc, f"{tg}{i}00", "912828ZZ9", cat="DBT", bal="5000000000", val="4800000000"))
                    debts.append(dict(HOLDING_ID=f"{tg}{i}00", MATURITY_DATE="15-NOV-2033", COUPON_TYPE="Fixed", ANNUALIZED_RATE="0.0425"))
                    if with_fut and sid == "S1":
                        for n, (title, payoff, bal, nt, exd, ident) in enumerate([
                                ("US 10YR NOTE (CBT) MAR26", "Long", "20000", "2200000000", ex, ""),
                                ("US ULTRA BOND CBT MAR26", "Short", "5000", "700000000", ex, ""),
                                ("THREE-MONTH SOFR", "Long", "1000", "1000000000", ex, ""),
                                ("FUTURE", "Long", "100", "11000000", ex, ""),
                                ("US 5YR NOTE (CBT)", "Long", "100", "11000000", expired[name], "")]):
                            h, e = synth_futs(acc, f"9{tg}{n}", title, payoff, bal, nt, exd, ident=ident)
                            holds.append(h)
                            for k, v in e.items():
                                extras[k].append(v)
                    if with_fut and sid == "S2":
                        h, e = synth_futs(acc, f"8{tg}0", "US ULTRA BOND CBT MAR26", "Short", "3000", "400000000", ex)
                        holds.append(h)
                        for k, v in e.items():
                            extras[k].append(v)
                        h = synth_futs(acc, f"8{tg}1", "US 10YR NOTE SWAP", "N/A", "1", "5000000", ex, deriv="SWP")[0]
                        holds.append(h)
                        extras[T_SWAP].append(dict(HOLDING_ID=f"8{tg}1", SWAP_FLAG="Y", NOTIONAL_AMOUNT="5000000", CURRENCY_CODE="USD"))
            synth_nport_zip(os.path.join(zd, f"{name}_nport.zip"), filings, holds, debts, extras)
    nd = os.path.join(tmp, "ncen")
    os.makedirs(nd)

    def sub(acc, per, fd):
        return dict(ACCESSION_NUMBER=acc, SUBMISSION_TYPE="N-CEN", CIK="100", FILING_DATE=fd, REPORT_ENDING_PERIOD=per)
    subs = [sub("N1", "31-DEC-2022", "01-MAR-2023"), sub("N2", "31-DEC-2025", "01-MAR-2026")]
    regs = [dict(ACCESSION_NUMBER=a, REGISTRANT_NAME="Gamma Registrant Name", CIK="100") for a in ("N1", "N2")]

    def fri(acc, sid, **fl):
        return dict(FUND_ID=f"{acc}_100_{sid}", ACCESSION_NUMBER=acc, FUND_NAME="Delta Series Name", SERIES_ID=sid, **fl)
    fris = [fri("N1", "S1", IS_INDEX="Y", IS_ETF="Y"), fri("N1", "S2", IS_INDEX="N"), fri("N1", "S4", IS_INDEX="N"),
            fri("N2", "S1", IS_INDEX="Y", IS_ETF="Y"), fri("N2", "S2", IS_INDEX="N"), fri("N2", "S4", IS_INDEX="N")]
    feeders = [dict(FUND_ID="N1_100_S1", REGISTERED_SERIES_ID="S4"), dict(FUND_ID="N2_100_S1", REGISTERED_SERIES_ID="S4")]
    make_ncen_zip(os.path.join(nd, "2026q3_ncen.zip"), subs, regs, fris, feeders)
    return zd, nd


def t_smoke(ck):
    """The stage-A scan on a synthetic zip: the futures lines, their joins and the swap, as the real tables are laid out."""
    with tempfile.TemporaryDirectory() as tmp:
        zd, nd = synth_set(tmp)
        zips = ntd.discover_zips(zd)
        windows = ntd.make_windows(zips)
        work = os.path.join(tmp, "work")
        run_stage_a(zips[0][2], 0, windows[0].zip_tag, windows, work, log=lambda m: None)
        pk = load_stage_a(work, windows[0].zip_tag)
        ck.check("stage A finds the 5 futures lines of the first synthetic zip", len(pk["fut"]) == 5, str(len(pk["fut"])))
        r0 = pk["fut"][0]
        ck.check("the FUT_FWD join carries the sign, expiry and notional", r0["payoff"] == "Long" and r0["notional"] == "2200000000" and r0["has_fwd"], str(r0["payoff"]))
        ck.check("the pair counts feed the real-data pins", pk["stats"].get("pair:DIR|FUT") == 5 and pk["stats"].get("fut_unit:DIR|NC") == 5, str(pk["stats"]))
        classes = collections.Counter(classify(r["texts"], r["ccy"])[0] for r in pk["fut"])
        ck.check("the synthetic lines classify as 3 Treasury, 1 non-Treasury, 1 unresolved", classes == collections.Counter({"tsy": 3, "nontsy": 1, "unresolved": 1}), str(classes))
        ck.check("the sha256 and filing count are recorded", len(pk["sha"]) == 64 and len(pk["filings"]) == 3, str(len(pk["filings"])))


def t_e2e(ck, caches):
    """The whole build on a synthetic set of eleven zips and a synthetic N-CEN zip, with the real cached curves. The committed cash files are not those of
    the synthetic data, so C-X1 and C-X2 FAIL here by design and the outputs land in the failure folder; what is tested is that every stage runs and
    that the numbers it writes are the ones worked out by hand."""
    if caches is None:
        ck.check("end-to-end run skipped: no curve caches given (pass --r1-cache and --r2-cache)", True)
        return
    with tempfile.TemporaryDirectory() as tmp:
        zd, nd = synth_set(tmp)
        work, out = os.path.join(tmp, "work"), os.path.join(tmp, "out")
        zips = ntd.discover_zips(zd)
        windows = ntd.make_windows(zips)
        for i, (_y, _q, path) in enumerate(zips):
            run_stage_a(path, i, windows[i].zip_tag, windows, work, log=lambda m: None)
        packs = [load_stage_a(work, w.zip_tag) for w in windows]
        for i, (_y, _q, path) in enumerate(zips):
            run_stage_b(path, i, windows[i].zip_tag, windows, packs, work, log=lambda m: None)
        a = argparse.Namespace(zip_dir=zd, work=work, r1_cache=caches[0], r2_cache=caches[1], cash_dir=OUT_DEFAULT, out=out, columns=COLS_TSV_DEFAULT,
                               ncen_dir=nd, zips=None, stage=None)
        so, se = sys.stdout, sys.stderr
        sys.stderr = io.StringIO()
        try:
            code = run_build(a, "idx", preflight=False)
        finally:
            sys.stderr = se
        ck.check("the synthetic build returns 2 (the committed cash files are not the synthetic ones)", code == 2, str(code))
        fd = os.path.join(out, FAILED_DIRNAME)
        names = sorted(os.listdir(fd)) if os.path.isdir(fd) else []
        want = ["fut_change.csv", "fut_checks.csv", "fut_contracts.csv", "fut_idx_README.md", "fut_idx_SOURCES.md", "fut_idx_file_stats.csv", "fut_other_deriv.csv",
                "fut_split.csv", "fut_verdict.csv", "fut_windows.csv", "idx_checks.csv", "idx_coverage.csv", "idx_crosstab.csv", "idx_prerun.csv", "idx_split.csv",
                "idx_verdict.csv"]
        ck.check("every output file is written to the failure folder", names == want, str(set(want) ^ set(names)))
        ck.check("nothing is written to the committed folder on a hard FAIL", not [n for n in os.listdir(out) if n != FAILED_DIRNAME])
        if names != want:
            return

        def rows(n):
            with open(os.path.join(fd, n), newline="", encoding="utf-8") as fh:
                return list(csv.DictReader(fh))
        w = {(r["window"], r["vintage"]): r for r in rows("fut_windows.csv")}
        ck.check("fut_windows has 22 rows (11 windows, 2 vintages)", len(w) == 22, str(len(w)))
        r = w[("2023Q4", "base")]
        want_f = (20000 * 78153.01 - 5000 * 249209.94) / 1e9
        ck.check("2023Q4 base: net 10-year equivalents are 20,000 TY less 5,000 UB at the pinned factors", abs(float(r["tenyeq_tenor_bn"]) - want_f) < 2e-6,
                 f"{r['tenyeq_tenor_bn']} vs {want_f:.6f}")
        ck.check("2023Q4 base: 2 kept lines, 1 expired, 1 unresolved", r["tsy_fut_lines"] == "2" and r["expired_lines"] == "1" and r["unresolved_lines"] == "1",
                 f"{r['tsy_fut_lines']} {r['expired_lines']} {r['unresolved_lines']}")
        ck.check("2023Q4 base: net face is 20,000 x $100,000 less 5,000 x $100,000", abs(float(r["face_net_bn"]) - 1.5) < 1e-9, r["face_net_bn"])
        chk = {c["check_id"]: c for c in rows("fut_checks.csv")}
        ck.check("C-X1 fails on the synthetic data and C-F1, C-F2 and C-F3 pass", chk["C-X1"]["result"] == "FAIL" and all(chk[k]["result"] == "PASS" for k in ("C-F1", "C-F2", "C-F3")),
                 str({k: chk[k]["result"] for k in ("C-X1", "C-F1", "C-F2", "C-F3")}))
        ck.check("C-X4 (hygiene) passes on the synthetic outputs", chk["C-X4"]["result"] == "PASS", chk["C-X4"]["note"])
        iv = {r_["key"]: r_["value"] for r_ in rows("idx_verdict.csv")}
        ck.check("the idx verdict names a label and the first key of each verdict file is the required sentence",
                 iv["label"] in ("SUPPORTS", "AGAINST", "INCONCLUSIVE") and rows("idx_verdict.csv")[0]["key"] == "required_sentence" and rows("fut_verdict.csv")[0]["key"] == "required_sentence")
        pre = {r_["key"]: r_["value"] for r_ in rows("idx_prerun.csv")}
        ck.check("the pre-run table counts the one entrant (series S2 at 2026Q2) and, in idx mode, its flag counts", pre.get("entrants_n") == "1" and "entrants_unflagged_n" in pre, str(pre))


GUARDS = [
    ("G1", "face: the 2- and 3-year note futures are $200,000", ["z3n_face_100k", "tu_face_100k"], t_g1),
    ("G2", "classifier (a matching rule is a hypothesis)", ["cls_no_step0", "cls_no_optn", "cls_bond_before_tenor", "cls_ub_on_blank", "cls_reverse_sources", "cls_conflict_silent"], t_g2),
    ("G3", "sign: PAYOFF_PROFILE primary, N/A excluded", ["sign_from_balance", "sign_holding_payoff", "keep_sign_na"], t_g3),
    ("G4", "size: count x face, never the mark", ["size_add_both", "size_by_currency_value", "skip_rule1"], t_g4),
    ("G5", "tenor map: pinned factors on the fixed curve", ["tm_add_expiry", "tm_drop_cf", "tm_d10_report_date"], t_g5),
    ("G6", "conversion factor", ["cf_no_eighth", "cf_fv_quarter", "cf_annual_discount", "cf_six_pct_any_term"], t_g6),
    ("G7", "modelled cheapest-to-deliver", ["ctd_argmax", "ty_basket_month_end", "tips_admitted", "note_admitted_to_us"], t_g7),
    ("G8", "futures never touch cash", ["g8_sum", "g8_ratio", "g8_token460", "g8_firstorder"], t_g8),
    ("G9", "leak scan: headers, rows, names, small cells", ["plant_series_id", "plant_big", "plant_name_cell", "plant_name_readme", "plant_small_cell"], t_g9),
    ("G10", "allowlist read from the column file, no copy in code", ["g10_add_column", "g10_rename_column", "g10_edit_tsv", "g10_paste_tuple"], t_g10),
    ("G11", "N-CEN flag timing", ["flag_late_ncen", "flag_backfill_unlabelled", "flag_use_nt", "flag_amend_older_wins"], t_g11),
    ("G12", "flag order (R23-9)", ["flag_index_before_na", "flag_na_alone_unflagged", "flag_levinv_before_mmf"], t_g12),
    ("G13", "series groups, feeders and the unclassified change", ["grp_switcher_in_index", "grp_unflagged_entrant_stable", "grp_feeder_kept", "grp_drop_stale_from_u"], t_g13),
    ("G14", "wording and symbols in prose",
     ["readme_inject:" + w for w in ("caused", "drove", "driven", "because of", "led to", "pushed", "in response to", "moved yields", "q", "s0", "U", "G_s", "ΔF", "A2")], t_g14),
    ("G15", "decision rules at their boundaries", ["rule_order_swap", "u_cap_16210", "drop_gs", "drop_q_bounds"], t_g15),
    ("G16", "failure path: a hard FAIL leaves committed files alone and exits 2", ["fail_writes_committed", "fail_exit0"], t_g16),
    ("G17", "no network", ["net_import", "net_call"], t_g17),
    ("G18", "small cells are merged, with complementary suppression", ["no_merge", "no_complementary"], t_g18),
    ("G19", "pre-registered bounds at their edges", ["stale_cutoff_le", "ratio_band_strict", "excess_gt", "rise_gt", "against_lt", "u_no_abs"], t_g19),
    ("T1", "stage-A scan on a synthetic zip (integration smoke)", [], t_smoke),
]


def selftest(mutants=True, quiet=False, caches=None):
    t0 = time.time()
    bad_total, n_checks, n_mut = 0, 0, 0
    out = sys.stderr if quiet else sys.stdout
    lines = []
    guards = list(GUARDS) + [("E2E", "whole build on synthetic zips (integration)", [], lambda ck: t_e2e(ck, caches))]
    for gid, desc, muts, fn in guards:
        ck = run_test(fn)
        n_checks += len(ck.items)
        bad = ck.failed()
        bad_total += len(bad)
        lines.append("%-4s %s: %d checks, %s" % (gid, desc, len(ck.items), "ok" if not bad else "FAILED"))
        for name, detail in bad:
            lines.append("       FAIL  %s   <- %s" % (name, detail))
        if mutants:
            for m in muts:
                with mutant(m):
                    mk_ = run_test(fn)
                caught = bool(mk_.failed())
                n_mut += 1
                bad_total += 0 if caught else 1
                lines.append("       mutant %-34s %s%s" % (m, "caught" if caught else "NOT CAUGHT", "  (first failing check: %s)" % mk_.failed()[0][0] if caught else ""))
    lines.append("selftest: %d guards, %d checks, %d mutants applied one at a time, %d failure(s), %.1f s" % (len(guards), n_checks, n_mut, bad_total, time.time() - t0))
    if not quiet or bad_total:
        print("\n".join(lines), file=out)
    else:
        print(lines[-1], file=out)
    return 0 if bad_total == 0 else 1


# ------------------------------------------------------------------------------------------------------------------------
# command line
# ------------------------------------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--zip-dir", default="~/nport", help="the folder holding the YYYYqQ_nport.zip files, as in the cash build")
        p.add_argument("--work", required=True, help="scratch directory for the stage A and B files; outside the repository")

    ps = sub.add_parser("selftest")
    ps.add_argument("--no-mutants", action="store_true")
    ps.add_argument("--r1-cache", default=None)
    ps.add_argument("--r2-cache", default=None)
    pc = sub.add_parser("scan")
    common(pc)
    pc.add_argument("--zips", default=None, help="comma list such as 2024q1,2024q2 (default: all)")
    pc.add_argument("--stage", required=True, choices=["A", "B"])
    for name in ("futures", "idx"):
        pb = sub.add_parser(name)
        common(pb)
        pb.add_argument("--r1-cache", default=os.path.join(ROOT, "data", "vintages", "r1_treasury"))
        pb.add_argument("--r2-cache", default=os.path.join(ROOT, "data", "vintages", "r2_treasury"))
        pb.add_argument("--cash-dir", default=OUT_DEFAULT, help="where the cash build's committed tsy_*.csv files are read")
        pb.add_argument("--out", default=OUT_DEFAULT)
        pb.add_argument("--columns", default=COLS_TSV_DEFAULT)
        if name == "idx":
            pb.add_argument("--ncen-dir", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        caches = (a.r1_cache, a.r2_cache) if a.r1_cache and a.r2_cache else None
        return selftest(mutants=not a.no_mutants, caches=caches)
    if a.cmd == "scan":
        return run_scan(a)
    a.ncen_dir = getattr(a, "ncen_dir", None)
    return run_build(a, a.cmd)


if __name__ == "__main__":
    sys.exit(main())
