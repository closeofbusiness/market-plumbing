#!/usr/bin/env python3
"""The 1-5-year cross-currency basis around quarter-ends: a descriptive table with no verdict. Python 3 standard library only.

  python3 bin/quarter_end_basis.py build [--tape DIR] [--out DIR]        # offline; byte-identical on re-run
  python3 bin/quarter_end_basis.py selftest [--no-mutants] [--mutant NAME]   # synthetic data only

Specification: _research/2026-10-23-Quarter-End-Basis-Spec.md (committed at 8507b92, with its supervisor rulings of rounds 1 to 4; where rounds differ the
latest round is applied, and round 3 re-scoped the build to a descriptive table). Outputs: data/quarter_end_basis/ (ten files).

WHAT IT READS. Only the committed derived files of the project's swap-tape ledger: data/swap_tape/cells_YYYY.csv, diagnostics_YYYY.csv and
monthly_short_tenor.csv. It sends no request, opens no archive of the source and reads nothing outside the repository (spec R1, R2). Every number it
writes is a statistic of statistics the ledger already published under its count floor (spec R3).

WHAT IT DESCRIBES. For JPY/USD, EUR/USD and GBP/USD and for every quarter-end on the tape: the median pooled 1-5-year basis in the last five liquid days
before the quarter-end, minus the mean of the medians of ten liquid days before and ten after, placed beside two reference sets of mid-quarter
windows. No row is a test outcome and no row carries a verdict.
"""
import argparse
import bisect
import calendar
import contextlib
import csv
import datetime as dt
import glob
import hashlib
import io
import math
import os
import re
import subprocess
import sys
import tempfile
import time
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, getcontext
from fractions import Fraction

getcontext().prec = 60

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAPE_DEFAULT = os.path.join(ROOT, "data", "swap_tape")
OUT_DEFAULT = os.path.join(ROOT, "data", "quarter_end_basis")
SPEC_REL = "_research/2026-10-23-Quarter-End-Basis-Spec.md"
SPEC_DEFAULT = os.path.join(ROOT, SPEC_REL)
CALENDAR_DEFAULT = os.path.join(ROOT, "CALENDAR.tsv")
CHECK_SH = os.path.join(ROOT, "bin", "check.sh")

# ------------------------------------------------------------------------------------------------------------------------
# the frozen design (spec section 3, R7) and its one-line text (3.10)
# ------------------------------------------------------------------------------------------------------------------------
D_ = dt.date.fromisoformat
ONE = dt.timedelta(days=1)
DESIGN = {"pool": "pool1to5", "window": 5, "buffer": 3, "control": 10, "tolerance": 10, "floor_window": 25, "floor_control": 50,
          "zone_lo": -21, "zone_hi": 7, "band_asof": "2026-11-27", "mix_pct": "95", "tenor_min_window": 2, "tenor_min_control": 3}
DESIGN_TEXT = ("X4-DESIGN v2 descriptive | pool1to5 | liquid = published median, no warn_f0_low | window 5, buffer 3, control 10+10 | tolerance 10 days | "
               "j-17<0 incomplete | floors 25/50/50 | zone -21/+7 | band asof 2026-11-27, dedupe (j,k), nearest rank | ref = ceil(m/2) per stretch | "
               "mix limit P95 | tenor D 2/3/3 | spec is the authority")
WINDOW, BUFFER, CONTROL = DESIGN["window"], DESIGN["buffer"], DESIGN["control"]
TOL = DESIGN["tolerance"]
FLOOR_W, FLOOR_C = DESIGN["floor_window"], DESIGN["floor_control"]
ZLO, ZHI = DESIGN["zone_lo"], DESIGN["zone_hi"]
BAND_ASOF = D_(DESIGN["band_asof"])
TEN_MIN_W, TEN_MIN_C = DESIGN["tenor_min_window"], DESIGN["tenor_min_control"]
QE_FIRST = D_("2024-12-31")
INSAMPLE_END = D_("2026-09-30")
PIN_LAST = D_("2026-10-21")                  # the pinned checks are evaluated on the tape truncated here
PIN_MONTH = "2026-09"                        # and on monthly rows up to this month
LEDGER_COMMIT_SPEC = "b22f51a"
SPEC_COMMIT = "8507b92"

PAIRS = (("JPYUSD", "xccy_jpyusd"), ("EURUSD", "xccy_eurusd"), ("GBPUSD", "xccy_gbpusd"))
PAIR_NAMES = tuple(p for p, _ in PAIRS)
SERIES_OF = dict(PAIRS)
PAIR_OF_SERIES = {s: p for p, s in PAIRS}
TENORS = (1, 2, 3, 4, 5)
ATYPES = ("quarter_end", "month_end", "placebo")

REQUIRED = ("These are medians of reported 1-5-year cross-currency swap prices around quarter-ends. A difference at a quarter-end does not show who "
            "borrowed dollars, why, or that any flow moved a price.")
NEITHER = "Neither identifies the counterparties or the reason."
OPENING = ("Banks and investors swap yen, euros or pounds for dollars. The price of that swap shows how scarce dollars are. This folder asks whether that "
           "price, on swaps of one to five years, looked different in the last days before each quarter-end than on the days around it. A swap of that "
           "length spans every quarter-end whatever day it is struck. Studies place the quarter-end effect in currency contracts of a week to three "
           "months, and this data holds none of those, so a small or absent difference here says nothing against those studies.")
BAND_RX = re.compile(r"overlapping windows from (\d+) stretches; not independent draws")
REF_RX = re.compile(r"one window per stretch; (\d+) values")
_DATE = dt.date
MIX_PHRASE = "tenor mix shifted; not read as a basis move"
INSAMPLE_PHRASE = "In-sample: examined before the build."

# ------------------------------------------------------------------------------------------------------------------------
# the output allowlists: the spec's canonical text typed here a second time, and its sha256 as the spec prints it (R4, G9)
# ------------------------------------------------------------------------------------------------------------------------
ANCHOR_COLS = ["pair", "anchor_date", "anchor_type", "in_sample", "in_band", "in_ref", "status", "window_first", "window_last", "gap_days", "on_date",
               "weekdays_window_span", "post_first", "pre_in_zone_days", "post_in_zone_days", "n_window", "n_pre", "n_post", "med_window_bp",
               "med_pre_bp", "med_post_bp", "d_bp", "band_role", "rank_band", "k_band", "rank_ref", "k_ref", "mean_tenor_window_y",
               "mean_tenor_ctrl_y", "d_mean_tenor_y", "mix_limit_y", "mix_flag"]
TENOR_COLS = ["pair", "anchor_date", "anchor_type", "tenor_y", "days_window", "days_pre", "days_post", "med_window_bp", "med_pre_bp", "med_post_bp",
              "d_bp", "status"]
BAND_COLS = ["pair", "band_role", "asof", "tape_last_date", "k_anchors", "stretches", "p5_bp", "p25_bp", "p50_bp", "p75_bp", "p95_bp", "sd_bp",
             "p5_leave_one_stretch_out_min_bp", "p5_leave_one_stretch_out_max_bp", "k_ref", "ref_min_bp", "ref_median_bp", "ref_max_bp",
             "mix_limit_y", "inputs_sha256"]
QUESTION_COLS = ["question", "pair", "anchor_type", "anchor_date", "statistic", "value", "unit", "denominator", "note"]
SHORT_COLS = ["series", "tenor", "first_month", "last_month", "months", "months_published", "n_total", "n_month_median", "days_with_trades_month_median"]
INPUT_COLS = ["file", "sha256", "rows", "first_date", "last_date"]
CHECK_COLS = ["check_id", "description", "expected", "observed", "status"]
COLUMNS_COLS = ["file", "columns"]
ALLOW_ORDER = ("anchors.csv", "anchors_tenor.csv", "band.csv", "questions.csv", "short_tenor_availability.csv", "inputs.csv", "checks.csv", "columns.tsv")
ALLOW = {"anchors.csv": ANCHOR_COLS, "anchors_tenor.csv": TENOR_COLS, "band.csv": BAND_COLS, "questions.csv": QUESTION_COLS,
         "short_tenor_availability.csv": SHORT_COLS, "inputs.csv": INPUT_COLS, "checks.csv": CHECK_COLS, "columns.tsv": COLUMNS_COLS}
COMMITTED = ("README.md", "SOURCES.md") + ALLOW_ORDER
SPEC_ALLOW_TEXT = (
    "anchors.csv:pair,anchor_date,anchor_type,in_sample,in_band,in_ref,status,window_first,window_last,gap_days,on_date,weekdays_window_span,post_first,pre_in_zone_days,post_in_zone_days,n_window,n_pre,n_post,med_window_bp,med_pre_bp,med_post_bp,d_bp,band_role,rank_band,k_band,rank_ref,k_ref,mean_tenor_window_y,mean_tenor_ctrl_y,d_mean_tenor_y,mix_limit_y,mix_flag\n"
    "anchors_tenor.csv:pair,anchor_date,anchor_type,tenor_y,days_window,days_pre,days_post,med_window_bp,med_pre_bp,med_post_bp,d_bp,status\n"
    "band.csv:pair,band_role,asof,tape_last_date,k_anchors,stretches,p5_bp,p25_bp,p50_bp,p75_bp,p95_bp,sd_bp,p5_leave_one_stretch_out_min_bp,p5_leave_one_stretch_out_max_bp,k_ref,ref_min_bp,ref_median_bp,ref_max_bp,mix_limit_y,inputs_sha256\n"
    "questions.csv:question,pair,anchor_type,anchor_date,statistic,value,unit,denominator,note\n"
    "short_tenor_availability.csv:series,tenor,first_month,last_month,months,months_published,n_total,n_month_median,days_with_trades_month_median\n"
    "inputs.csv:file,sha256,rows,first_date,last_date\n"
    "checks.csv:check_id,description,expected,observed,status\n"
    "columns.tsv:file,columns\n")
SPEC_ALLOW_SHA256 = "3f54fbeb17c65e257af8acd41c1f2b0b2398b432ca18b3bed4f60c1c5e2445e4"
# the ledger's own headers, which the build checks before it reads a value (G13)
CELLS_HEADER = ["date_utc", "series", "tenor_y", "variant", "unit", "n", "median", "q1", "q3", "iqr_bp", "iqr_over_sqrt_n_bp", "share_pkg", "share_gt10bp",
                "status"]
DIAG_HEADER = ["date_utc", "key", "value", "n"]
MONTHLY_HEADER = ["month", "series", "tenor", "n", "median", "q1", "q3", "iqr", "status", "n_days_with_trades"]
SOURCE_LINE = ("# source: derived from DTCC Public Price Dissemination, CFTC cumulative rates reports (pddata.dtcc.com), through the project's swap-tape "
               "ledger (data/swap_tape/); statistics only, no DTCC record is reproduced; non-commercial research (THE_ASK.md E-024)")

# wording guards: G10 (causal and attribution) and G15 (verdict and significance); the spec's literal expressions, copied
CAUSAL_RX = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because|due\s+to|in\s+response\s+to|led\s+to|prompted|pushed|"
                       r"as\s+a\s+result\s+of|reflect(?:s|ed|ing)?|amid|owing\s+to|on\s+the\s+back\s+of|window[- ]dress(?:ed|es|ing)?|borrowed|"
                       r"borrowing\s+by|demand\s+for\s+dollars|hedging\s+demand)\b", re.I)
VERDICT_RX = re.compile(r"\b(SUPPORTS|AGAINST|INCONCLUSIVE|PENDING)\b|(?i:\b(statistically\s+significant|significance|p-value|reject(?:s|ed)?\s+the\s+null)\b)")
PROB_RX = re.compile(r"\bbinomial\b|\bprobabilit(?:y|ies)\b|\bp\s*=\s*0?\.\d", re.I)

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


class DataError(Exception):
    """A hard check on the inputs or on the outputs failed."""


# ------------------------------------------------------------------------------------------------------------------------
# small helpers
# ------------------------------------------------------------------------------------------------------------------------
def sha256_of(b):
    return hashlib.sha256(b).hexdigest()


def pdec(s):
    """A ledger string as a Decimal; None for a blank (a blank is never zero)."""
    s = (s or "").strip()
    if s == "":
        return Decimal(0) if M("blank_as_zero") else None
    try:
        return Decimal(s)
    except InvalidOperation:
        raise DataError("not a number: %r" % s)


def to_dec(x):
    if isinstance(x, Fraction):
        return Decimal(x.numerator) / Decimal(x.denominator)
    if isinstance(x, int):
        return Decimal(x)
    return x


def q3(x):
    """Round half away from zero to 3 decimals, as text. Never Python's round() (R6)."""
    if x is None:
        return ""
    if M("py_round"):
        return "%.3f" % round(float(to_dec(x)), 3)
    s = str(to_dec(x).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))
    return "0.000" if s == "-0.000" else s


def numfmt(x):
    """A count or a median of counts: an integer as an integer, anything else to 3 decimals."""
    if x is None:
        return ""
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else q3(x).rstrip("0").rstrip(".")


def yn(b):
    return "yes" if b else "no"


def weekdays(a, b):
    out, d = [], a
    while d <= b:
        if d.weekday() < 5:
            out.append(d)
        d += ONE
    return out


def wdn(d):
    """A running weekday number (Monday 1 January of year 1 is 0)."""
    o = d.toordinal() - 1
    return (o // 7) * 5 + min(o % 7, 4)


def month_last_weekday(y, m):
    d = dt.date(y, m, calendar.monthrange(y, m)[1])
    while d.weekday() >= 5:
        d -= ONE
    return d


def calendar_quarter_ends(y0, y1):
    return [dt.date(y, m, calendar.monthrange(y, m)[1]) for y in range(y0, y1 + 1) for m in (3, 6, 9, 12)]


ZONE_QS = [q for q in calendar_quarter_ends(2024, 2027) if D_("2024-09-30") <= q <= D_("2027-12-31")]


_ZONES = {}


def zones():
    key = M("zone_swapped")
    if key not in _ZONES:
        lo, hi = (-7, 21) if key else (ZLO, ZHI)
        _ZONES[key] = [(q + dt.timedelta(days=lo), q + dt.timedelta(days=hi)) for q in ZONE_QS]
    return _ZONES[key]


_ZDAY = {}


def in_zone(d):
    key = (M("zone_swapped"), d)
    v = _ZDAY.get(key)
    if v is None:
        v = _ZDAY[key] = any(a <= d <= b for a, b in zones())
    return v


def span_touches_zone(first, last):
    return any(first <= b and last >= a for a, b in zones())


def in_sample(d):
    """True for a date on or before the end of the period examined before the build (2026-09-30)."""
    return d < INSAMPLE_END if M("insample_lt") else d <= INSAMPLE_END


def band_caveat(n_stretches):
    """The dependence caveat on a rank among the band windows; each pair names its own stretch count (supervisor ruling, round 5)."""
    if M("caveat_fixed_eight"):
        return "overlapping windows from about eight stretches; not independent draws"
    return "overlapping windows from %d stretches; not independent draws" % n_stretches


def ref_caveat(k_ref):
    if M("caveat_fixed_eight"):
        return "one window per stretch; about eight values"
    return "one window per stretch; %d values" % k_ref


def window_phrase(gap, unit):
    """'a window ending N days before the quarter-end', and '1 day' for the singular (round 5)."""
    return "a window ending %d day%s before the %s" % (gap, "" if gap == 1 else "s", unit)


def count_le(values, bound):
    """How many values are at or below a bound."""
    return sum(1 for v in values if (v < bound if M("count_lt") else v <= bound))


def warn_days(warns, a):
    """warn_f0_low days among the 10 calendar days ending on the anchor (a - 9 days to a)."""
    lo = a - dt.timedelta(days=10 if M("warn_win11") else 9)
    return sum(1 for d in warns if lo <= d <= a)


def stretch_of(d):
    return (d.year, (d.month - 1) // 3)


def stretch_label(s):
    return "%d-Q%d" % (s[0], s[1] + 1)


# ------------------------------------------------------------------------------------------------------------------------
# reading the ledger's derived files (R1, 2.2, G13)
# ------------------------------------------------------------------------------------------------------------------------
class Day(object):
    __slots__ = ("date", "n", "med", "status", "tn", "tmed", "raw")

    def __init__(self, date, n, med, status, tn, tmed, raw):
        self.date, self.n, self.med, self.status, self.tn, self.tmed, self.raw = date, n, med, status, tn, tmed, raw


class Tape(object):
    def __init__(self):
        self.first = None
        self.last = None
        self.days = {p: {} for p in PAIR_NAMES}
        self.warn = {p: set() for p in PAIR_NAMES}
        self.inputs = []                  # (file, sha256, rows, first, last)
        self.monthly = []                 # (month, series, tenor, n, status, days)
        self.hashes = {}

    def truncate(self, d, month=None):
        t = Tape()
        t.first = self.first
        t.last = min(self.last, d)
        for p in PAIR_NAMES:
            t.days[p] = {k: v for k, v in self.days[p].items() if k <= d}
            t.warn[p] = {k for k in self.warn[p] if k <= d}
        t.inputs = list(self.inputs)
        t.hashes = dict(self.hashes)
        t.monthly = [r for r in self.monthly if month is None or r[0] <= month]
        return t


def table_rows(text, header, name):
    """The data rows of one ledger file. Lines starting with # are skipped; the header is the first line that does not start with #."""
    lines = text.splitlines()
    body = lines if M("header_from_hash") else [l for l in lines if not l.startswith("#")]
    if not body:
        raise DataError("%s: empty" % name)
    got = next(csv.reader([body[0]]))
    if got != header and not M("header_unchecked"):
        raise DataError("%s: header is not the one this build reads: %s" % (name, ",".join(got)[:120]))
    rows = [r for r in csv.reader(body[1:]) if r]
    if not M("header_unchecked"):
        for i, r in enumerate(rows):
            if len(r) != len(header):
                raise DataError("%s: row %d has %d cells, the header %d" % (name, i + 2, len(r), len(header)))
    return rows


def parse_int(s, what):
    try:
        return int(s)
    except ValueError:
        raise DataError("%s: not an integer: %r" % (what, s))


def load_tape(texts):
    """texts: {file name: bytes}. Returns a Tape. Only cells_YYYY.csv, diagnostics_YYYY.csv and monthly_short_tenor.csv are read."""
    t = Tape()
    cells = sorted(n for n in texts if re.fullmatch(r"cells_\d{4}\.csv", n))
    diags = sorted(n for n in texts if re.fullmatch(r"diagnostics_\d{4}\.csv", n))
    if not cells:
        raise DataError("no cells_YYYY.csv file")
    if [c[6:10] for c in cells] != [d[12:16] for d in diags]:
        raise DataError("cells and diagnostics files do not cover the same years")
    dates_all = []
    for name in cells:
        raw = texts[name]
        rows = table_rows(raw.decode("utf-8"), CELLS_HEADER, name)
        ds = []
        seen = set()
        for r in rows:
            d = D_(r[0])
            ds.append(d)
            dates_all.append(d)
            series, tenor, variant = r[1], r[2], r[3]
            if series not in PAIR_OF_SERIES:
                continue
            if variant != "headline" and not M("any_variant"):
                continue
            pair = PAIR_OF_SERIES[series]
            if (d, pair, tenor) in seen:
                raise DataError("%s: duplicate cell %s %s %s" % (name, r[0], series, tenor))
            seen.add((d, pair, tenor))
            n, med, status = parse_int(r[5], name), pdec(r[6]), r[13]
            day = t.days[pair].get(d)
            if day is None:
                day = t.days[pair][d] = Day(d, None, None, "absent", [0] * 5, [None] * 5, ["", "", [""] * 5])
            if tenor == DESIGN["pool"]:
                day.n, day.med, day.status = n, med, status
                day.raw[0], day.raw[1] = r[5], r[6]
            elif tenor in ("1", "2", "3", "4", "5"):
                i = int(tenor) - 1
                day.tn[i] = n
                day.tmed[i] = med if (status in ("ok", "thin") and med is not None) else (Decimal(0) if M("tenor_blank_zero") else None)
                day.raw[2][i] = r[5]
            else:
                raise DataError("%s: unknown xccy tenor %r" % (name, tenor))
        t.inputs.append((name, sha256_of(raw), len(rows), min(ds).isoformat() if ds else "", max(ds).isoformat() if ds else ""))
        t.hashes[name] = sha256_of(raw)
    for name in diags:
        raw = texts[name]
        rows = table_rows(raw.decode("utf-8"), DIAG_HEADER, name)
        ds = []
        for r in rows:
            ds.append(D_(r[0]))
            m = re.fullmatch(r"warn_f0_low_(xccy_[a-z]+)", r[1])
            if m and m.group(1) in PAIR_OF_SERIES:
                t.warn[PAIR_OF_SERIES[m.group(1)]].add(D_(r[0]))
        t.inputs.append((name, sha256_of(raw), len(rows), min(ds).isoformat() if ds else "", max(ds).isoformat() if ds else ""))
        t.hashes[name] = sha256_of(raw)
    mname = "monthly_short_tenor.csv"
    if mname in texts:
        raw = texts[mname]
        rows = table_rows(raw.decode("utf-8"), MONTHLY_HEADER, mname)
        for r in rows:
            if r[1] in PAIR_OF_SERIES:
                t.monthly.append((r[0], r[1], r[2], parse_int(r[3], mname), r[8], parse_int(r[9], mname)))
        ms = sorted(r[0] for r in rows)
        t.inputs.append((mname, sha256_of(raw), len(rows), ms[0] if ms else "", ms[-1] if ms else ""))
        t.hashes[mname] = sha256_of(raw)
    t.first, t.last = min(dates_all), max(dates_all)
    return t


def load_tape_dir(tape_dir):
    texts = {}
    for name in sorted(os.listdir(tape_dir)):
        if re.fullmatch(r"cells_\d{4}\.csv|diagnostics_\d{4}\.csv|monthly_short_tenor\.csv", name):
            with open(os.path.join(tape_dir, name), "rb") as f:
                texts[name] = f.read()
    if "monthly_short_tenor.csv" not in texts:
        raise DataError("monthly_short_tenor.csv is missing")
    return load_tape(texts)


# ------------------------------------------------------------------------------------------------------------------------
# liquid days (3.1)
# ------------------------------------------------------------------------------------------------------------------------
def is_liquid(day, warn):
    if warn and not M("warn_liquid"):
        return False
    ok = ("ok",) if M("thin_dropped") else ("ok", "thin")
    return day.status in ok and day.med is not None


class PairData(object):
    def __init__(self, tape, pair):
        self.pair, self.tape = pair, tape
        self.L = []
        for d in weekdays(tape.first, tape.last):
            day = tape.days[pair].get(d)
            if day is None:
                if M("hole_liquid"):
                    self.L.append(Day(d, 0, Decimal(0), "ok", [0] * 5, [None] * 5, ["", "", [""] * 5]))
                continue
            if is_liquid(day, d in tape.warn[pair]):
                self.L.append(day)
        self.dates = [x.date for x in self.L]


def covered_weekdays(tape, asof=None):
    """A weekday inside the covered range is covered whether or not a cell exists for it (2.3). The tape covers date X when tape_last_date >= X."""
    last = tape.last if asof is None else min(asof, tape.last)
    days = weekdays(tape.first, last)
    if M("hole_uncovered"):
        days = [d for d in days if any(d in tape.days[p] for p in PAIR_NAMES)]
    return days


def inputs_sha256(tape, pair, asof):
    """sha256 of one line per covered weekday <= asof: date,pool_n,pool_median,n1..n5,warn (2.3); the strings are the ledger's, verbatim."""
    h = hashlib.sha256()
    for d in covered_weekdays(tape, asof):
        day = tape.days[pair].get(d)
        fields = [""] * 7 if day is None else [day.raw[0], day.raw[1]] + list(day.raw[2])
        h.update((",".join([d.isoformat()] + fields + ["1" if d in tape.warn[pair] else "0"]) + "\n").encode("utf-8"))
    return h.hexdigest()


# ------------------------------------------------------------------------------------------------------------------------
# the difference D (3.4) and exact statistics (R6)
# ------------------------------------------------------------------------------------------------------------------------
def med(vals):
    s = sorted(vals)
    n = len(s)
    if M("mean_not_median"):
        return sum(s) / n
    if n % 2:
        return s[n // 2]
    if M("median_first_of_even"):
        return s[n // 2 - 1]
    return (s[n // 2 - 1] + s[n // 2]) / 2


def diff_d(mw, mp, mq):
    if M("float_math"):
        return Decimal(repr(float(mw) - (float(mp) + float(mq)) / 2))
    if M("pre_only"):
        return mw - mp
    if M("sign_flip"):
        return (mp + mq) / 2 - mw
    return mw - (mp + mq) / 2


def mean_tenor(days):
    num = sum(t * x.tn[t - 1] for x in days for t in TENORS)
    den = sum(x.tn[t - 1] for x in days for t in TENORS)
    return Fraction(num, den) if den else None


def rank_le(values, d):
    if M("rank_lt"):
        return sum(1 for v in values if v < d)
    return sum(1 for v in values if v <= d)


def rank_denominator(values):
    return len(values) + 1 if M("rank_k_plus_1") else len(values)


def nearest_rank(sorted_vals, q):
    """The value at 1-based rank ceil(q x k); q an exact Fraction."""
    k = len(sorted_vals)
    if M("interpolate"):
        h = (k - 1) * q
        lo = int(math.floor(h))
        hi = min(lo + 1, k - 1)
        return sorted_vals[lo] + to_dec(h - lo) * (sorted_vals[hi] - sorted_vals[lo])
    r = max(1, math.ceil(q * k))
    return sorted_vals[r - 1]


def pop_sd(vals):
    fs = [Fraction(v) for v in vals]
    mean = sum(fs) / len(fs)
    var = sum((x - mean) ** 2 for x in fs) / (len(fs) - 1 if M("sd_sample") else len(fs))
    return (Decimal(var.numerator) / Decimal(var.denominator)).sqrt()


# ------------------------------------------------------------------------------------------------------------------------
# windows, controls, tolerance, status (3.3, 3.7)
# ------------------------------------------------------------------------------------------------------------------------
class R(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)


def layout(j, k):
    """Index ranges of the window, the pre-control and the post-control (3.3): L[j-4..j], L[j-17..j-8], L[k+3..k+12]."""
    w, b, c = WINDOW, BUFFER, CONTROL
    if M("window4"):
        w = 4
    if M("window6"):
        w = 6
    if M("buffers0"):
        b = 0
    if M("controls9"):
        c = 9
    wi = range(j - w + 1, j + 1)
    if M("window_holds_post"):
        wi = range(j - w + 2, j + 2)
    return wi, range(j - w - b - c + 1, j - w - b + 1), range(k + b, k + b + c)


def tol_fail(a, dj, dk):
    before, after = (a - dj).days, (dk - a).days
    if M("gap_ge"):
        fail_before = before >= TOL
    elif M("gap_11_ok"):
        fail_before = before > TOL + 1
    else:
        fail_before = before > TOL
    fail_after = False if M("post_unchecked") else after > TOL
    return fail_before or fail_after


def low_n(nw, npre, npost):
    if M("floor_window_only"):
        return nw < FLOOR_W
    return nw < FLOOR_W or npre < FLOOR_C or npost < FLOOR_C


def decide_status(incomplete, gapfail, low):
    """incomplete, then gap, then low_n, then complete (3.7)."""
    if incomplete:
        return "incomplete"
    if M("low_n_first"):
        return "low_n" if low else ("gap" if gapfail else "complete")
    return "gap" if gapfail else ("low_n" if low else "complete")


def trade_count(days):
    return len(days) if M("count_days") else sum(x.n for x in days)


def evaluate(P, a, atype):
    L, dates = P.L, P.dates
    nL = len(L)
    j = bisect.bisect_right(dates, a) - 1
    k = j + 1
    wi, pi, qi = layout(j, k)

    def seg(rng):
        if M("wrap_negative") and rng.stop - 1 < nL:
            return [L[i] for i in rng]
        if rng.start < 0 or rng.stop - 1 >= nL:
            return None
        return [L[i] for i in rng]

    win, pre, post = seg(wi), seg(pi), seg(qi)
    if M("ctrl_weekdays") and 0 <= j < nL and k < nL:
        wj, wk = wdn(L[j].date), wdn(L[k].date)
        win = [x for x in L if wj - 4 <= wdn(x.date) <= wj]
        pre = [x for x in L if wj - 17 <= wdn(x.date) <= wj - 8]
        post = [x for x in L if wk + 3 <= wdn(x.date) <= wk + 12]
    early = (min(wi.start, pi.start) < 0 or j < 0) and not M("wrap_negative")
    late = qi.stop - 1 >= nL
    r = R(pair=P.pair, date=a, type=atype, j=j, k=k, win=win, pre=pre, post=post, gap_days=None, on_date=None, span=None, post_first=None,
          pre_zone=None, post_zone=None, n_window=None, n_pre=None, n_post=None, window_first=None, window_last=None, medw=None, medp=None,
          medq=None, D=None, mtw=None, mtc=None, dmt=None)
    if 0 <= j < nL and win is not None:
        r.gap_days = (a - L[j].date).days
        r.on_date = r.gap_days <= 1 if M("on_date_le1") else r.gap_days == 0
        r.window_first, r.window_last = win[0].date, win[-1].date
        r.span = wdn(r.window_last) - wdn(r.window_first) + 1
        r.n_window = trade_count(win)
    if 0 <= k < nL:
        r.post_first = L[k].date
    if pre is not None:
        r.n_pre = trade_count(pre)
        r.pre_zone = sum(1 for x in pre if in_zone(x.date))
    if post is not None:
        r.n_post = trade_count(post)
        r.post_zone = 0 if M("post_zone_zero") else sum(1 for x in post if in_zone(x.date))
    incomplete = early or late or win is None or pre is None or post is None
    gapfail = low = False
    if not incomplete:
        gapfail = tol_fail(a, L[j].date, L[k].date)
        low = low_n(r.n_window, r.n_pre, r.n_post)
    r.status = decide_status(incomplete, gapfail, low)
    if r.status == "complete":
        r.medw, r.medp, r.medq = med([x.med for x in win]), med([x.med for x in pre]), med([x.med for x in post])
        r.D = diff_d(r.medw, r.medp, r.medq)
        r.mtw, r.mtc = mean_tenor(win), mean_tenor(pre + post)
        r.dmt = r.mtw - r.mtc
    return r


def tenor_cell(r, t):
    """The per-tenor difference on an anchor's own window and control days (3.6): only days where tenor t's own median is published."""
    if r.status != "complete":
        return {"status": "anchor_not_complete"}

    def vals(days):
        out = []
        for x in days:
            v = x.med if M("tenor_pooled") else x.tmed[t - 1]
            if v is None:
                continue
            out.append(v)
        return out

    w, p, q = vals(r.win), vals(r.pre), vals(r.post)
    cell = {"days_window": len(w), "days_pre": len(p), "days_post": len(q)}
    minw = 1 if M("tenor_min1") else TEN_MIN_W
    minc = 2 if M("tenor_ctrl2") else TEN_MIN_C
    if len(w) < minw or len(p) < minc or len(q) < minc:
        cell["status"] = "too_few_days"
        return cell
    cell.update(status="complete", med_window=med(w), med_pre=med(p), med_post=med(q))
    cell["d"] = diff_d(cell["med_window"], cell["med_pre"], cell["med_post"])
    return cell


# ------------------------------------------------------------------------------------------------------------------------
# anchors and the band (3.2, 3.5)
# ------------------------------------------------------------------------------------------------------------------------
def qe_dates(tape):
    out = []
    for y in range(tape.first.year, tape.last.year + 1):
        for m in (3, 6, 9, 12):
            q = dt.date(y, m, calendar.monthrange(y, m)[1])
            a = month_last_weekday(y, m)
            if q >= QE_FIRST and a <= tape.last:
                out.append(a)
    return out


def me_dates(tape):
    out = []
    for y in range(tape.first.year, tape.last.year + 1):
        for m in (1, 2, 4, 5, 7, 8, 10, 11):
            a = month_last_weekday(y, m)
            if tape.first <= a <= tape.last:
                out.append(a)
    return out


def passes_band(r, asof, atype="placebo"):
    """The band tests of 3.5 on one evaluated anchor: complete, span clear of every exclusion zone, last post-control day by asof."""
    if r.status != "complete":
        return False
    if r.post[-1].date > asof and not M("asof_ignored"):
        return False
    if (atype == "placebo" or not M("qe_me_in_band")) and span_touches_zone(r.pre[0].date, r.post[-1].date) and not M("zone_kept"):
        return False
    return True


def band_items(P, asof):
    """The complete placebo windows whose span touches no exclusion zone and ends by asof, one per (j, k), earliest date kept (3.5)."""
    tape = P.tape
    qe, me = set(qe_dates(tape)), set(me_dates(tape))
    cands = [(d, "placebo") for d in weekdays(tape.first, tape.last) if d not in qe and d not in me]
    if M("qe_me_in_band"):
        cands = sorted([(d, "quarter_end") for d in qe] + [(d, "month_end") for d in me] + cands)
    seen, items = set(), []
    for a, atype in cands:
        r = evaluate(P, a, atype)
        if not passes_band(r, asof, atype):
            continue
        key = (r.j, r.k)
        if key in seen and not M("dup_kept"):
            continue
        seen.add(key)
        r.stretch = stretch_of(a)
        items.append(r)
    return items


def pick_reference(items):
    """One band anchor per stretch: the one at position ceil(m/2) in date order (3.5)."""
    by = {}
    for r in items:
        by.setdefault(r.stretch, []).append(r)
    ref = []
    for s in sorted(by):
        grp = sorted(by[s], key=lambda x: x.date)
        m = len(grp)
        if M("ref_all"):
            ref.extend(grp)
        elif M("ref_first"):
            ref.append(grp[0])
        elif M("ref_two"):
            ref.extend(grp[:2])
        else:
            ref.append(grp[-(-m // 2) - 1])
    return ref


def band_summary(items, ref):
    vals = sorted(r.D for r in items)
    k = len(vals)
    s = {"k": k, "stretches": len({r.stretch for r in items}), "vals": vals, "ref": ref, "refvals": sorted(r.D for r in ref)}
    if k == 0:
        s.update(p={}, sd=None, loso=(None, None), mix_limit=None)
        return s
    s["p"] = {q: nearest_rank(vals, Fraction(q, 100)) for q in (5, 25, 50, 75, 95)}
    s["sd"] = pop_sd(vals)
    los = []
    if M("loso_one_anchor"):
        for i in range(k):
            rest = sorted(r.D for n, r in enumerate(items) if n != i)
            if rest:
                los.append(nearest_rank(rest, Fraction(5, 100)))
    else:
        for st in sorted({r.stretch for r in items}):
            rest = sorted(r.D for r in items if r.stretch != st)
            if rest:
                los.append(nearest_rank(rest, Fraction(5, 100)))
    s["loso"] = (min(los), max(los)) if los else (None, None)
    absd = sorted((r.dmt if M("signed_mix") else abs(r.dmt)) for r in items)
    s["mix_limit"] = nearest_rank(absd, Fraction(90 if M("mix_p90") else 95, 100))
    s["lowest_stretches"] = [stretch_of(r.date) for r in sorted(items, key=lambda x: x.D)[:3]]
    return s


def mix_flag(dmt, limit):
    if limit is None or dmt is None:
        return None
    return abs(dmt) > limit


# ------------------------------------------------------------------------------------------------------------------------
# the whole computation for one tape
# ------------------------------------------------------------------------------------------------------------------------
class PairResult(object):
    pass


def roles_for(tape):
    """The band roles written, and the asof the ranks use (3.5, R8)."""
    if tape.last < BAND_ASOF:
        return [("provisional", tape.last)], "provisional", tape.last
    return [("of_record", BAND_ASOF), ("recomputed", BAND_ASOF)], "of_record", BAND_ASOF


def compute_pair(tape, pair, rank_asof):
    pr = PairResult()
    pr.pair = pair
    pr.P = P = PairData(tape, pair)
    pr.items = band_items(P, rank_asof)
    pr.ref = pick_reference(pr.items)
    pr.summ = band_summary(pr.items, pr.ref)
    pr.qe = [evaluate(P, a, "quarter_end") for a in qe_dates(tape)]
    pr.me = [evaluate(P, a, "month_end") for a in me_dates(tape)]
    bvals, rvals = pr.summ["vals"], pr.summ["refvals"]
    for r in pr.qe + pr.me:
        r.in_band = r.in_ref = False
        r.mflag = None
        if r.status == "complete":
            r.rank_band, r.k_band = rank_le(bvals, r.D), rank_denominator(bvals)
            r.rank_ref, r.k_ref = rank_le(rvals, r.D), rank_denominator(rvals)
            r.mflag = mix_flag(r.dmt, pr.summ["mix_limit"])
    refset = {id(x) for x in pr.ref}
    for r in pr.items:
        r.in_band = True
        r.in_ref = id(r) in refset
        r.mflag = None
    pr.tenor = []
    for r in pr.qe + pr.me + sorted(pr.ref, key=lambda x: x.date):
        for t in TENORS:
            pr.tenor.append((r, t, tenor_cell(r, t)))
    return pr


def compute_all(tape):
    roles, rank_role, rank_asof = roles_for(tape)
    w = R(tape=tape, roles=roles, rank_role=rank_role, rank_asof=rank_asof, pairs={})
    for p in PAIR_NAMES:
        w.pairs[p] = compute_pair(tape, p, rank_asof)
    return w


# ------------------------------------------------------------------------------------------------------------------------
# wording guards (R5, G10, G15) and the allowlists (R4, G9)
# ------------------------------------------------------------------------------------------------------------------------
def causal_rx():
    if M("pushed_missing"):
        return re.compile(CAUSAL_RX.pattern.replace("|pushed", ""), re.I)
    if M("because_missing"):
        return re.compile(CAUSAL_RX.pattern.replace("|because", ""), re.I)
    return CAUSAL_RX


def verdict_rx():
    if M("verdict_supports_missing"):
        return re.compile(VERDICT_RX.pattern.replace("SUPPORTS|", ""))
    if M("verdict_significance_missing"):
        return re.compile(VERDICT_RX.pattern.replace("|significance", ""))
    return VERDICT_RX


def strip_exempt(name, text):
    """The two exempt sentences of R5 and, in SOURCES.md, lines carrying a page-cited CGFS reference."""
    t = text
    if M("exempt_whole_line"):
        t = "\n".join("" if REQUIRED in l else l for l in t.split("\n"))
    elif not M("required_not_exempt"):
        t = t.replace(REQUIRED, "")
    t = t.replace(NEITHER, "")
    if M("borrowed_exempt"):
        t = re.sub(r"borrowed", "", t)
    if name == "SOURCES.md" or M("cgfs_exempt_all"):
        t = "\n".join("" if (re.search(r"CGFS", l) and re.search(r"\bpp?\s?\d", l)) else l for l in t.split("\n"))
    return t


def wording_problems(name, text):
    out = []
    for m in causal_rx().finditer(strip_exempt(name, text)):
        out.append("%s: causal or attribution wording %r" % (name, m.group(0)))
    for m in verdict_rx().finditer(text):
        out.append("%s: verdict or significance wording %r" % (name, m.group(0)))
    if not M("binomial_off"):
        for m in PROB_RX.finditer(text):
            out.append("%s: a probability or binomial figure %r" % (name, m.group(0)))
    return out


def allow_cols(name):
    cols = list(ALLOW[name])
    if M("extra_column") and name == "anchors.csv":
        cols.append("extra_col")
    if M("renamed_column") and name == "band.csv":
        cols[cols.index("sd_bp")] = "sd"
    return cols


def allow_text():
    return "".join("%s:%s\n" % (n, ",".join(allow_cols(n))) for n in ALLOW_ORDER)


def spec_sha():
    return "0" * 64 if M("sha_drift") else SPEC_ALLOW_SHA256


def check_header(name, header):
    if list(header) != allow_cols(name):
        raise DataError("%s: header is not its allowlist" % name)


def csv_text(source, header, rows):
    out = io.StringIO()
    out.write(source + "\n")
    w = csv.writer(out, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        if len(r) != len(header):
            raise DataError("a row has %d cells, the header %d" % (len(r), len(header)))
        w.writerow(r)
    return out.getvalue()


def render_csv(name, rows):
    header = allow_cols(name)
    check_header(name, header)
    return csv_text(SOURCE_LINE, header, rows)


def columns_tsv():
    rows = list(ALLOW_ORDER)
    lines = [SOURCE_LINE, "file\tcolumns"]
    for n in rows:
        cols = allow_cols(n)
        if M("columns_drift") and n == "checks.csv":
            cols = cols[:-1]
        lines.append("%s\t%s" % (n, "|".join(cols)))
    return "\n".join(lines) + "\n"


def parse_csv_text(text):
    """(header, rows) of a committed csv: the header is the first line not starting with #."""
    lines = text.splitlines()
    body = lines if M("source_as_header") else [l for l in lines if not l.startswith("#")]
    rows = list(csv.reader(body))
    return rows[0], rows[1:]


# ------------------------------------------------------------------------------------------------------------------------
# rows
# ------------------------------------------------------------------------------------------------------------------------
def iso(d):
    return "" if d is None else d.isoformat()


def fs(x):
    return "" if x is None else str(x)


def pos_text(r):
    """How the window sits against the anchor (R3-4)."""
    if r.gap_days is None:
        return "no window yet"
    if r.gap_days == 0 or (r.gap_days == 1 and M("pos_on_date_le1")):
        return "on_date"
    unit = {"quarter_end": "quarter-end", "month_end": "month-end"}.get(r.type, "anchor")
    return window_phrase(r.gap_days, unit)


def role_label(w):
    return w.rank_role


def anchor_row(w, pr, r):
    comp = r.status == "complete"
    s = pr.summ
    placebo = r.type == "placebo"
    ranked = comp and not placebo
    return [pr.pair, r.date.isoformat(), r.type, yn(in_sample(r.date)), yn(r.in_band), yn(r.in_ref), r.status, iso(r.window_first),
            iso(r.window_last), fs(r.gap_days), "" if r.on_date is None else yn(r.on_date), fs(r.span), iso(r.post_first), fs(r.pre_zone),
            fs(r.post_zone), fs(r.n_window), fs(r.n_pre), fs(r.n_post), q3(r.medw) if comp else "", q3(r.medp) if comp else "",
            q3(r.medq) if comp else "", q3(r.D) if comp else "", w.rank_role if comp else "", fs(r.rank_band) if ranked else "",
            fs(r.k_band) if ranked else "", fs(r.rank_ref) if ranked else "", fs(r.k_ref) if ranked else "",
            q3(r.mtw) if comp else "", q3(r.mtc) if comp else "", q3(r.dmt) if comp else "",
            q3(s["mix_limit"]) if ranked else "", "" if (not ranked or r.mflag is None) else yn(r.mflag)]


def anchor_rows(w):
    rows = []
    for p in PAIR_NAMES:
        pr = w.pairs[p]
        for r in pr.qe + pr.me + pr.items:
            rows.append(anchor_row(w, pr, r))
    return rows


def tenor_rows(w):
    rows = []
    for p in PAIR_NAMES:
        for r, t, c in w.pairs[p].tenor:
            st = c["status"]
            row = [p, r.date.isoformat(), r.type, str(t), fs(c.get("days_window")), fs(c.get("days_pre")), fs(c.get("days_post"))]
            if st == "complete":
                row += [q3(c["med_window"]), q3(c["med_pre"]), q3(c["med_post"]), q3(c["d"])]
            else:
                row += ["", "", "", ""]
            rows.append(row + [st])
    return rows


def band_fields(pair, role, asof, tape, s, sha):
    p = s["p"]
    last = dt.date.today() if M("tape_last_from_clock") else tape.last
    if s["k"] == 0:
        return [pair, role, asof.isoformat(), last.isoformat(), "0", "0"] + [""] * 13 + [sha]
    rv = s["refvals"]
    lo, hi = s["loso"]
    return [pair, role, asof.isoformat(), last.isoformat(), str(s["k"]), str(s["stretches"]), q3(p[5]), q3(p[25]), q3(p[50]), q3(p[75]), q3(p[95]),
            q3(s["sd"]), q3(lo), q3(hi), str(len(rv)), q3(rv[0]), q3(med(rv)), q3(rv[-1]), q3(s["mix_limit"]), sha]


def parse_prev_band(text):
    if not text:
        return {}
    h, rows = parse_csv_text(text)
    return {r[0]: r for r in rows if len(r) == len(h) and r[1] == "of_record"}


def band_rows(w, prev_text):
    """The band.csv rows and the list of warnings (R8). Before 2026-11-27 is covered: one provisional row per pair. After: of_record (copied from the
    committed file when it holds one) and recomputed, always both, so that a rebuild is byte-identical."""
    prev = parse_prev_band(prev_text)
    rows, warns = [], []
    for p in PAIR_NAMES:
        pr = w.pairs[p]
        sha = inputs_sha256(w.tape, p, w.rank_asof)
        if w.rank_role == "provisional":
            rows.append(band_fields(p, "provisional", w.rank_asof, w.tape, pr.summ, sha))
            continue
        fresh = band_fields(p, "recomputed", BAND_ASOF, w.tape, pr.summ, sha)
        rec = band_fields(p, "of_record", BAND_ASOF, w.tape, pr.summ, sha)
        if p in prev and not M("of_record_rewritten"):
            rec = list(prev[p])
        rows.append(rec)
        rows.append(fresh)
        same = [a for i, a in enumerate(rec) if i not in (1, 3)] == [a for i, a in enumerate(fresh) if i not in (1, 3)]
        if not same and not M("diff_not_warned"):
            warns.append("%s: the recomputed band differs from the band of record" % p)
    return rows, warns


def caveated(base, caveat):
    return (base + " " if base else "") + caveat[0].upper() + caveat[1:] + "."


class QBuilder(object):
    def __init__(self):
        self.rows = []

    def add(self, q, pair, atype, adate, stat, value, unit, denom, extra="", caveat=None, insample=False, mix=False):
        note = REQUIRED
        if caveat:
            note += " " + caveat
        if mix:
            note += " Flag: " + MIX_PHRASE + "."
        if insample:
            note += " " + INSAMPLE_PHRASE
        if extra:
            note += " " + extra
        self.rows.append([q, pair, atype, iso(adate) if isinstance(adate, _DATE) else (adate or ""), stat, str(value), unit, denom, note])


def stats_of(rs):
    ds = sorted(r.D for r in rs)
    if not ds:
        return None
    return {"m": len(ds), "mean": sum(Fraction(x) for x in ds) / len(ds), "median": med(ds), "ds": ds}


def question_rows(w):
    qb = QBuilder()
    tape = w.tape
    for p in PAIR_NAMES:
        pr = w.pairs[p]
        s = pr.summ
        kb, kr = len(s["vals"]), len(s["refvals"])
        bcav = "Rank among mid-quarter windows: %s." % band_caveat(s["stretches"])
        rcav = "Rank among reference windows: %s." % ref_caveat(kr)
        bden = "of %d band windows from %d stretches" % (kb, s["stretches"])
        rden = "of %d reference windows" % kr
        for r in pr.qe:
            ins, mix = in_sample(r.date), bool(r.mflag)
            kw = dict(insample=ins, mix=mix)
            qb.add("Q1", p, "quarter_end", r.date, "status", r.status, "text", "1 quarter-end", **kw)
            if r.window_first:
                qb.add("Q1", p, "quarter_end", r.date, "window_dates", "%s to %s" % (r.window_first.isoformat(), r.window_last.isoformat()), "dates",
                       "5 liquid days", **kw)
            qb.add("Q1", p, "quarter_end", r.date, "window_position", pos_text(r), "text", "1 quarter-end", **kw)
            if r.pre_zone is not None:
                qb.add("Q1", p, "quarter_end", r.date, "pre_in_zone_days", r.pre_zone, "days", "of 10 pre-control days", **kw)
            if r.post_zone is not None:
                qb.add("Q1", p, "quarter_end", r.date, "post_in_zone_days", r.post_zone, "days", "of 10 post-control days", **kw)
            if r.status != "complete":
                continue
            qb.add("Q1", p, "quarter_end", r.date, "d_bp", q3(r.D), "bp", "5 window days (%d trades) against 10 + 10 control days (%d, %d trades)" %
                   (r.n_window, r.n_pre, r.n_post), **kw)
            qb.add("Q1", p, "quarter_end", r.date, "rank_band", r.rank_band, "count of band values <= D", bden, caveat=bcav, **kw)
            qb.add("Q1", p, "quarter_end", r.date, "rank_ref", r.rank_ref, "count of reference values <= D", rden, caveat=rcav, **kw)
            qb.add("Q1", p, "quarter_end", r.date, "d_mean_tenor_y", q3(r.dmt), "years", "mean tenor of the window minus that of the 20 control days", **kw)
            qb.add("Q1", p, "quarter_end", r.date, "mix_flag", yn(r.mflag), "flag", "limit %s years, P95 of |d| over %d band windows" %
                   (q3(s["mix_limit"]), kb), **kw)
            for rr, t, c in pr.tenor:
                if rr is r and c["status"] == "complete":
                    qb.add("Q1", p, "quarter_end", r.date, "d_tenor_%dy_bp" % t, q3(c["d"]), "bp",
                           "%d window, %d pre-control, %d post-control days with a published %d-year median" % (c["days_window"], c["days_pre"],
                                                                                                            c["days_post"], t), **kw)
        for qname, atype, rs in (("Q2", "quarter_end", pr.qe), ("Q3", "month_end", pr.me)):
            comp = [r for r in rs if r.status == "complete"]
            st = stats_of(comp)
            note_ctx = "" if atype == "quarter_end" else "Month-end windows are not in the band: every month-end span touches an exclusion zone."
            qb.add(qname, p, atype, "", "m_complete", len(comp), "count", "of %d %ss on the tape" % (len(rs), atype.replace("_", "-")), extra=note_ctx)
            if st is None:
                continue
            den = "%d complete %ss" % (st["m"], atype.replace("_", "-"))
            qb.add(qname, p, atype, "", "mean_d_bp", q3(st["mean"]), "bp", den, extra=note_ctx)
            qb.add(qname, p, atype, "", "median_d_bp", q3(st["median"]), "bp", den, extra=note_ctx)
            if s["k"]:
                n5 = count_le(st["ds"], s["p"][5])
                qb.add(qname, p, atype, "", "count_le_band_p5", n5, "count", den + "; band P5 %s bp" % q3(s["p"][5]), extra=note_ctx, caveat=bcav)
                qb.add(qname, p, atype, "", "count_le_ref_min", count_le(st["ds"], s["refvals"][0]), "count",
                       den + "; reference minimum %s bp" % q3(s["refvals"][0]), extra=note_ctx, caveat=rcav)
        # Q4 thin trading
        warns = tape.warn[p]
        for atype, rs in (("quarter_end", pr.qe), ("month_end", pr.me), ("placebo", pr.items)):
            have = [r for r in rs if r.n_window is not None]
            if not have:
                continue
            den = "%d %s anchors with a window" % (len(have), atype)
            qb.add("Q4", p, atype, "", "median_n_window", numfmt(med([Fraction(r.n_window) for r in have])), "trades", den)
            qb.add("Q4", p, atype, "", "median_gap_days", numfmt(med([Fraction(r.gap_days) for r in have])), "days", den)
            wd = [warn_days(warns, r.date) for r in have]
            qb.add("Q4", p, atype, "", "median_warn_f0_low_days_10d", numfmt(med([Fraction(x) for x in wd])), "days",
                   den + "; warn_f0_low days among the 10 calendar days ending on the anchor")
        for r in pr.qe:
            if r.date.month == 12 and r.window_first:
                qb.add("Q4", p, "quarter_end", r.date, "year_end_window_first", r.window_first.isoformat(), "date", "1 year-end", mix=bool(r.mflag))
                qb.add("Q4", p, "quarter_end", r.date, "year_end_window_last", r.window_last.isoformat(), "date", "1 year-end", mix=bool(r.mflag))
        # Q5 tenor mix and tenors
        for r in pr.qe:
            if r.status != "complete":
                continue
            ins = in_sample(r.date)
            qb.add("Q5", p, "quarter_end", r.date, "d_mean_tenor_y", q3(r.dmt), "years", "against a limit of %s years" % q3(s["mix_limit"]),
                   insample=ins, mix=bool(r.mflag))
        compq = [r for r in pr.qe if r.status == "complete"]
        for t in TENORS:
            n = sum(1 for rr, tt, c in pr.tenor if tt == t and rr.type == "quarter_end" and c["status"] == "complete")
            qb.add("Q5", p, "quarter_end", "", "tenor_%dy_complete_cells" % t, n, "count", "of %d complete quarter-ends" % len(compq))
    for sr in short_rows(tape, None):
        series, tenor = sr[0], sr[1]
        pair = PAIR_OF_SERIES[series]
        for i, stat, unit in ((4, "months", "count"), (5, "months_published", "count"), (6, "n_total", "trades"), (7, "n_month_median", "trades"),
                              (8, "days_with_trades_month_median", "days")):
            qb.add("Q6", pair, "", "", "%s_%s" % (stat, tenor), sr[i], unit, "%s months, %s to %s" % (sr[4], sr[2], sr[3]))
    return qb.rows


def short_rows(tape, upto_month):
    out = []
    for series in ("xccy_jpyusd", "xccy_eurusd"):
        for tenor in ("3m", "1y"):
            rs = sorted(r for r in tape.monthly if r[1] == series and r[2] == tenor and (upto_month is None or r[0] <= upto_month))
            if not rs:
                continue
            out.append([series, tenor, rs[0][0], rs[-1][0], str(len(rs)), str(sum(1 for r in rs if r[4] == "ok")), str(sum(r[3] for r in rs)),
                        numfmt(med([Fraction(r[3]) for r in rs])), numfmt(med([Fraction(r[5]) for r in rs]))])
    return out


def inputs_rows(tape):
    return [list(map(str, r)) for r in tape.inputs]


# ------------------------------------------------------------------------------------------------------------------------
# G15: the descriptive-wording rules applied to a rendered folder
# ------------------------------------------------------------------------------------------------------------------------
def readme_rows(text):
    out = []
    for line in text.split("\n"):
        if re.match(r"\| (JPYUSD|EURUSD|GBPUSD) \| \d{4}-\d\d-\d\d \|", line):
            out.append([c.strip() for c in line.strip().strip("|").split("|")])
    return out


def caveat_problem(text, rx, want):
    """True when the caveat is missing, or names a count other than the pair's own."""
    if M("caveat_off"):
        return False
    m = rx.search(text)
    if m is None:
        return True
    return want is not None and int(m.group(1)) != want and not M("caveat_count_off")


def descriptive_problems(files):
    out = []
    ah, arows = parse_csv_text(files["anchors.csv"])
    anchors = {(r[0], r[1], r[2]): dict(zip(ah, r)) for r in arows}
    bh, brows = parse_csv_text(files["band.csv"])
    counts = {}
    for r in brows:
        b = dict(zip(bh, r))
        counts.setdefault(b["pair"], (int(b["stretches"]), int(b["k_ref"])))
    qh, qrows = parse_csv_text(files["questions.csv"])
    for r in qrows:
        q = dict(zip(qh, r))
        a = anchors.get((q["pair"], q["anchor_date"], q["anchor_type"]))
        st, note = q["statistic"], q["note"]
        ns, nk = counts.get(q["pair"], (None, None))
        if st in ("rank_band", "count_le_band_p5") and caveat_problem(note, BAND_RX, ns):
            out.append("questions.csv: %s %s %s printed without its caveat (or with another pair's count)" % (q["pair"], q["anchor_date"], st))
        if st in ("rank_ref", "count_le_ref_min") and caveat_problem(note, REF_RX, nk):
            out.append("questions.csv: %s %s %s printed without its caveat (or with another pair's count)" % (q["pair"], q["anchor_date"], st))
        if a is None:
            continue
        if a["mix_flag"] == "yes" and MIX_PHRASE not in note and not M("mix_text_off"):
            out.append("questions.csv: %s %s %s on a mix-flagged anchor lacks the mix sentence" % (q["pair"], q["anchor_date"], st))
        if st == "window_position" and a["gap_days"] not in ("", "0") and not M("gap_text_off"):
            unit = "quarter-end" if a["anchor_type"] == "quarter_end" else "month-end"
            if q["value"] != window_phrase(int(a["gap_days"]), unit) or "at the quarter-end" in note:
                out.append("questions.csv: %s %s window position is not 'a window ending N days before the %s'" % (q["pair"], q["anchor_date"], unit))
    for cells in readme_rows(files["README.md"]):
        a = anchors.get((cells[0], cells[1], "quarter_end"))
        if a is None:
            continue
        line = " | ".join(cells)
        gd = a["gap_days"]
        pos = cells[4]
        ns, nk = counts.get(cells[0], (None, None))
        if gd not in ("", "0") and not M("gap_text_off"):
            if window_phrase(int(gd), "quarter-end") not in pos or "at the quarter-end" in pos:
                out.append("README.md: %s %s position is not 'a window ending %s before the quarter-end'" % (cells[0], cells[1], gd))
        elif gd == "0" and pos != "on_date":
            out.append("README.md: %s %s is on the date but is not marked on_date" % (cells[0], cells[1]))
        if cells[6] != "-" and caveat_problem(cells[6], BAND_RX, ns):
            out.append("README.md: %s %s band rank printed without its caveat (or with another pair's count)" % (cells[0], cells[1]))
        if cells[7] != "-" and caveat_problem(cells[7], REF_RX, nk):
            out.append("README.md: %s %s reference rank printed without its caveat (or with another pair's count)" % (cells[0], cells[1]))
        if a["mix_flag"] == "yes" and MIX_PHRASE not in line and not M("mix_text_off"):
            out.append("README.md: %s %s is mix-flagged but its row lacks the mix sentence" % (cells[0], cells[1]))
    for n, t in files.items():
        for m in PROB_RX.finditer(t):
            if not M("binomial_off"):
                out.append("%s: a probability or binomial figure %r" % (n, m.group(0)))
    return out


def all_wording_problems(files):
    out = []
    for n, t in files.items():
        if n in ("README.md", "SOURCES.md"):
            out += wording_problems(n, t)
        elif n == "questions.csv":
            h, rows = parse_csv_text(t)
            i = h.index("note")
            for r in rows:
                out += wording_problems("questions.csv note", r[i])
        else:
            for m in verdict_rx().finditer(t):
                out.append("%s: verdict or significance wording %r" % (n, m.group(0)))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# the pinned checks (section 9)
# ------------------------------------------------------------------------------------------------------------------------
def sign_ok(v):
    return v > 0 if M("sign_check_inverted") else v < 0


def identity_counts(tape):
    ok = total = 0
    for p in PAIR_NAMES:
        for d, day in tape.days[p].items():
            if day.n is None:
                continue
            total += 1
            if M("identity_off") or day.n == sum(day.tn):
                ok += 1
    return ok, total


PIN_C13 = {"JPYUSD": [("2024-12-31", "-0.740"), ("2025-03-31", "3.468"), ("2025-06-30", "0.234"), ("2025-09-30", "3.375"), ("2025-12-31", "-3.499"),
                      ("2026-03-31", "-4.329"), ("2026-06-30", "2.172")],
           "EURUSD": [("2025-03-31", "0.719"), ("2025-06-30", "0.828"), ("2025-09-30", "-0.547"), ("2025-12-31", "-0.156"), ("2026-03-31", "-2.688"),
                      ("2026-06-30", "-0.438"), ("2026-09-30", "0.578")]}
PIN_C14 = {"JPYUSD": [("2024-12-31", 0), ("2025-03-31", 6), ("2025-06-30", 7), ("2025-09-30", 0), ("2025-12-31", 2), ("2026-03-31", 6), ("2026-06-30", 8)],
           "EURUSD": [("2025-03-31", 8), ("2025-06-30", 6), ("2025-09-30", 8), ("2025-12-31", 4), ("2026-03-31", 8), ("2026-06-30", 7), ("2026-09-30", 8)]}
PIN_C07 = {"JPYUSD": "k 52; stretches 8; P5 -3.470; P50 0.469; SD 2.390; LOSO -3.470 to -2.789; k_ref 8; ref -3.033 / 1.234 / 4.469; mix limit 0.663",
           "EURUSD": "k 68; stretches 8; P5 -1.391; P50 0.063; SD 0.945; LOSO -1.406 to -0.938; k_ref 8; ref -1.266 / 0.445 / 1.688; mix limit 0.730",
           "GBPUSD": "k 26; stretches 5; P5 0.016; P50 0.391; SD 0.666; LOSO -0.110 to 0.078; k_ref 5; ref 0.219 / 0.625 / 1.875; mix limit 1.061"}
PIN_C07B = {"JPYUSD": "P25 -1.064; P75 2.657; P95 4.281", "EURUSD": "P25 -0.531; P75 0.547; P95 1.828", "GBPUSD": "P25 0.328; P75 1.063; P95 2.000"}
PIN_C14POST = {"JPYUSD": [0, 2, 2, 2, 0, 0, 0], "EURUSD": [2, 2, 2, 1, 0, 0, 2]}
PIN_REF = {"JPYUSD": "2024-11-15 2025-02-12 2025-05-14 2025-08-13 2025-11-12 2026-02-09 2026-05-14 2026-08-07",
           "EURUSD": "2024-11-12 2025-02-11 2025-05-14 2025-08-08 2025-11-12 2026-02-10 2026-05-12 2026-08-11"}
PIN_HASH = {"cells_2024.csv": "8a93cb1c7dfc542c2f15454550c25989fd0c0d0ded85b9f4b6692b3952584bd2",
            "cells_2025.csv": "fef068669d757fff0ae26611f662de9864a6b6f54dd687d697192b2e06a7a11b"}


def band_text(pr):
    s = pr.summ
    if s["k"] == 0:
        return "no band"
    rv = s["refvals"]
    return "k %d; stretches %d; P5 %s; P50 %s; SD %s; LOSO %s to %s; k_ref %d; ref %s / %s / %s; mix limit %s" % (
        s["k"], s["stretches"], q3(s["p"][5]), q3(s["p"][50]), q3(s["sd"]), q3(s["loso"][0]), q3(s["loso"][1]), len(rv), q3(rv[0]), q3(med(rv)), q3(rv[-1]),
        q3(s["mix_limit"]))


def qe_get(pw, pair, date):
    for r in pw.pairs[pair].qe:
        if r.date.isoformat() == date:
            return r
    return None


def build_checks(w, pw, tape, calendar_text, c10, band_warns):
    """The rows of checks.csv. pw is the computation on the tape truncated at PIN_LAST (C05-C08 and C13-C15 are evaluated there)."""
    ptape = pw.tape
    rows = []

    def add(cid, desc, exp, obs, status=None, warn_on_diff=False):
        if status is None:
            status = "PASS" if exp == obs else ("WARN" if warn_on_diff else "FAIL")
        rows.append([cid, desc, exp, obs, status])

    h_exp = "; ".join("%s %s" % (k, v) for k, v in sorted(PIN_HASH.items()))
    h_obs = "; ".join("%s %s" % (k, tape.hashes.get(k, "absent")) for k in sorted(PIN_HASH))
    add("C01", "closed-year ledger files unchanged (sha256)", h_exp, h_obs, warn_on_diff=True)
    last = "cells_%d.csv" % tape.last.year
    add("C01b", "the current-year ledger file (information)", "n/a", "%s %s" % (last, tape.hashes.get(last, "absent")), "INFO")
    # C02
    cov = weekdays(ptape.first, ptape.last)
    absent = {p: [d for d in cov if d not in ptape.days[p]] for p in PAIR_NAMES}
    n_missing = sum(len(v) for v in absent.values())
    add("C02", "weekdays on the tape at the pinned vintage, contiguous in the cells of every pair", "528 weekdays 2024-10-14 to 2026-10-21; 0 missing",
        "%d weekdays %s to %s; %d missing" % (len(cov), ptape.first, ptape.last, n_missing))
    later = [d for d in weekdays(PIN_LAST + ONE, tape.last) if any(d not in tape.days[p] for p in PAIR_NAMES)] if tape.last > PIN_LAST else []
    add("C02b", "weekdays after the pinned vintage absent from the cells (covered, not liquid)", "none",
        "none" if not later else " ".join(d.isoformat() for d in later), "PASS" if not later else "WARN")
    # C03
    cell = lambda p, d: ptape.days[p].get(D_(d))
    parts = []
    for p, d in (("JPYUSD", "2026-10-15"), ("EURUSD", "2026-10-13"), ("GBPUSD", "2026-10-13")):
        x = cell(p, d)
        parts.append("%s %s n %s %s" % (p, d, x.raw[0] if x else "absent", x.raw[1] if x else ""))
    jl = pw.pairs["JPYUSD"].P.L
    jm = med([x.med for x in jl]) if jl else Decimal(0)
    add("C03", "sign and unit of three pooled cells (bp; negative is the conventional sign of a dollar premium)",
        "JPYUSD 2026-10-15 n 26 -21.875; EURUSD 2026-10-13 n 26 -3.875; GBPUSD 2026-10-13 n 24 2.438", "; ".join(parts))
    add("C03b", "median of all JPY liquid-day medians is negative (bp)", "-33.125", q3(jm), "PASS" if (sign_ok(jm) and q3(jm) == "-33.125") else "FAIL")
    ok, tot = identity_counts(ptape)
    add("C04", "pool n equals the sum of tenor n on every pair-day", "1584 of 1584", "%d of %d" % (ok, tot))
    # C05
    nl = {p: len(pw.pairs[p].P.L) for p in PAIR_NAMES}
    add("C05", "liquid days and warn_f0_low days of 528", "JPYUSD 423; EURUSD 461; GBPUSD 377 of 528; warn_f0_low days 77 / 56 / 71",
        "JPYUSD %d; EURUSD %d; GBPUSD %d of %d; warn_f0_low days %d / %d / %d" % (nl["JPYUSD"], nl["EURUSD"], nl["GBPUSD"], len(cov),
                                                                          len(ptape.warn["JPYUSD"]), len(ptape.warn["EURUSD"]), len(ptape.warn["GBPUSD"])))
    # C06
    def wtext(r):
        if r is None or r.window_first is None:
            return "absent"
        return "%s to %s; gap_days %s; n_window %s; post_first %s; post-control ends %s" % (
            r.window_first, r.window_last, r.gap_days, r.n_window, iso(r.post_first), r.post[-1].date if r.post else "n/a")
    add("C06a", "JPY 2024-12-31 window", "2024-12-12 to 2024-12-23; gap_days 8; n_window 89; post_first 2025-01-06; post-control ends 2025-01-28",
        wtext(qe_get(pw, "JPYUSD", "2024-12-31")))
    add("C06b", "JPY 2025-12-31 window", "2025-12-17 to 2025-12-23; gap_days 8; n_window 128; post_first 2026-01-05; post-control ends 2026-01-22",
        wtext(qe_get(pw, "JPYUSD", "2025-12-31")))
    e = qe_get(pw, "EURUSD", "2025-12-31")
    add("C06c", "EUR 2025-12-31 window", "2025-12-19 to 2025-12-31 n 62", "%s to %s n %s" % (iso(e.window_first), iso(e.window_last), e.n_window) if e else "absent")
    stat_sets = {}
    for p in PAIR_NAMES:
        for r in pw.pairs[p].qe:
            stat_sets.setdefault(r.status, []).append("%s %s" % (p, r.date))
    eg = qe_get(pw, "EURUSD", "2024-12-31")
    add("C06d", "quarter-ends with status gap, and the EUR 2024-12-31 gap in days",
        "EURUSD 2024-12-31 (12 days); GBPUSD 2024-12-31; GBPUSD 2025-12-31",
        "; ".join(sorted(stat_sets.get("gap", []))).replace("EURUSD 2024-12-31", "EURUSD 2024-12-31 (%s days)" % (eg.gap_days if eg else "n/a")))
    add("C06e", "quarter-ends with status incomplete", "GBPUSD 2026-09-30; JPYUSD 2026-09-30", "; ".join(sorted(stat_sets.get("incomplete", []))))
    add("C06f", "quarter-ends with status low_n (information)", "none", "none" if not stat_sets.get("low_n") else "; ".join(sorted(stat_sets["low_n"])),
        "INFO")
    offs = []
    for p in ("JPYUSD", "EURUSD", "GBPUSD"):
        for r in pw.pairs[p].qe:
            if r.on_date is False and (p != "GBPUSD" or r.date == D_("2025-03-31")):
                offs.append("%s %s (%d)" % (p, r.date, r.gap_days))
    add("C06g", "quarter-ends whose window does not end on the date (gap_days); on_date is yes for every other JPY and EUR quarter-end",
        "JPYUSD 2024-12-31 (8); JPYUSD 2025-09-30 (1); JPYUSD 2025-12-31 (8); EURUSD 2024-12-31 (12); GBPUSD 2025-03-31 (3)", "; ".join(offs))
    # C07
    for p in PAIR_NAMES:
        add("C07a_" + p[:3], "%s band at the pinned vintage (bp unless marked)" % p, PIN_C07[p], band_text(pw.pairs[p]), warn_on_diff=True)
        s = pw.pairs[p].summ
        add("C07b_" + p[:3], "%s band percentiles (bp)" % p, PIN_C07B[p],
            "P25 %s; P75 %s; P95 %s" % (q3(s["p"][25]), q3(s["p"][75]), q3(s["p"][95])) if s["k"] else "no band", warn_on_diff=True)
    mep = {}
    for p in PAIR_NAMES:
        mep[p] = sum(1 for r in pw.pairs[p].me if r.status == "complete" and not span_touches_zone(r.pre[0].date, r.post[-1].date) and r.post[-1].date <= pw.rank_asof)
    add("C07c", "month-end anchors that would pass the band tests", "JPYUSD 0; EURUSD 0; GBPUSD 0",
        "; ".join("%s %d" % (p, mep[p]) for p in PAIR_NAMES), warn_on_diff=True)
    # C08
    sr = {(r[0], r[1]): r for r in short_rows(ptape, PIN_MONTH)}
    g = lambda s, t, i: sr[(s, t)][i] if (s, t) in sr else "absent"
    add("C08", "monthly short-tenor counts, months to 2026-09",
        "JPY 3m n 404, 24 months, 19 published, median 14.5 on 7 days; EUR 3m n 545, 24 months, 21 published, median 19 on 9 days; "
        "1y months published JPY 24 of 24 and EUR 24 of 24; 1y totals JPY 1667 and EUR 1750",
        "JPY 3m n %s, %s months, %s published, median %s on %s days; EUR 3m n %s, %s months, %s published, median %s on %s days; "
        "1y months published JPY %s of %s and EUR %s of %s; 1y totals JPY %s and EUR %s" % (
            g("xccy_jpyusd", "3m", 6), g("xccy_jpyusd", "3m", 4), g("xccy_jpyusd", "3m", 5), g("xccy_jpyusd", "3m", 7), g("xccy_jpyusd", "3m", 8),
            g("xccy_eurusd", "3m", 6), g("xccy_eurusd", "3m", 4), g("xccy_eurusd", "3m", 5), g("xccy_eurusd", "3m", 7), g("xccy_eurusd", "3m", 8),
            g("xccy_jpyusd", "1y", 5), g("xccy_jpyusd", "1y", 4), g("xccy_eurusd", "1y", 5), g("xccy_eurusd", "1y", 4),
            g("xccy_jpyusd", "1y", 6), g("xccy_eurusd", "1y", 6)))
    # C09
    has = any("2027-01-29" in l and SPEC_REL in l for l in calendar_text.splitlines())
    add("C09", "the CALENDAR row of 2027-01-29 names the spec", "present", "present" if has else "absent", "PASS" if has else "WARN")
    add("C10", "a second build leaves every sha256 unchanged", c10[0], c10[1], c10[2])
    # C11
    if w.rank_role == "provisional":
        add("C11", "band of record (asof %s)" % BAND_ASOF, "written once the tape covers %s" % BAND_ASOF, "the tape ends %s; provisional rows only" % tape.last, "INFO")
    else:
        add("C11", "recomputed band equals the band of record", "equal", "equal" if not band_warns else "; ".join(band_warns), "PASS" if not band_warns else "WARN")
    # C13
    for p in ("JPYUSD", "EURUSD"):
        got = []
        for d, v in PIN_C13[p]:
            r = qe_get(pw, p, d)
            got.append((d, q3(r.D) if r is not None and r.status == "complete" else (r.status if r else "absent")))
        add("C13_" + p[:3], "%s in-sample D at quarter-ends, computed by the second reviewer before the build (bp)" % p,
            "; ".join("%s %s" % x for x in PIN_C13[p]), "; ".join("%s %s" % x for x in got))
    for p in ("JPYUSD", "EURUSD"):
        got = []
        for d, v in PIN_C14[p]:
            r = qe_get(pw, p, d)
            got.append((d, r.pre_zone if r is not None and r.pre_zone is not None else "n/a"))
        add("C14_" + p[:3], "%s pre_in_zone_days" % p, "; ".join("%s %s" % x for x in PIN_C14[p]), "; ".join("%s %s" % x for x in got))
    for p in ("JPYUSD", "EURUSD"):
        got = []
        for d, v in PIN_C14[p]:
            r = qe_get(pw, p, d)
            got.append((d, r.post_zone if r is not None and r.post_zone is not None else "n/a"))
        add("C14post_" + p[:3], "%s post_in_zone_days (round 4), in quarter-end order" % p,
            "; ".join("%s %s" % (d, v) for (d, _), v in zip(PIN_C14[p], PIN_C14POST[p])), "; ".join("%s %s" % x for x in got))
    # C15
    cells = []
    for p in PAIR_NAMES:
        for r, t, c in sorted(pw.pairs[p].tenor, key=lambda x: (x[0].date, x[1])):
            if r.type == "quarter_end" and c["status"] == "complete":
                cells.append("%s %s %dy" % (p, r.date, t))
    add("C15a", "complete per-tenor cells at complete quarter-ends",
        "JPYUSD 2025-06-30 5y; JPYUSD 2026-03-31 2y; JPYUSD 2026-03-31 5y; JPYUSD 2026-06-30 5y; EURUSD 2026-03-31 5y", "; ".join(cells))
    for p in ("JPYUSD", "EURUSD"):
        add("C15_" + p[:3], "%s reference dates (one per stretch)" % p, PIN_REF[p], " ".join(r.date.isoformat() for r in sorted(pw.pairs[p].ref, key=lambda x: x.date)))
    return rows


def staleness(tape, today):
    """C12, printed to stdout only (R9): the tape's last date against the run date."""
    days = (today - tape.last).days
    return days, ("STALE: the tape ends %s, %d days before today" % (tape.last, days)) if days > 10 else ("tape ends %s, %d days before today" % (tape.last, days))


_SEQ = [0]


# ------------------------------------------------------------------------------------------------------------------------
# README.md and SOURCES.md (section 6)
# ------------------------------------------------------------------------------------------------------------------------
COLDOC = {
    "anchors.csv": [
        ("pair", "JPYUSD, EURUSD or GBPUSD; the non-dollar leg is named first."),
        ("anchor_date", "The anchor weekday: the last weekday on or before a quarter-end or month-end, or a placebo weekday that is in the band."),
        ("anchor_type", "quarter_end, month_end or placebo. A placebo row is written only when its window is in the band."),
        ("in_sample", "yes when the date is on or before 2026-09-30, a period examined before the build."),
        ("in_band", "yes for a mid-quarter window that is in the band."),
        ("in_ref", "yes for the band window picked as the reference window of its stretch."),
        ("status", "complete, incomplete (too little history, or the days after the anchor have not all posted), gap (the nearest liquid day was more than 10 "
                   "days away) or low_n (fewer trades than the floors: 25 in the window, 50 in each control)."),
        ("window_first, window_last", "First and last of the five window days."),
        ("gap_days", "Calendar days from the last liquid day on or before the anchor to the anchor."),
        ("on_date", "yes when gap_days is 0."),
        ("weekdays_window_span", "Weekdays from window_first to window_last inclusive."),
        ("post_first", "The first liquid day after the anchor."),
        ("pre_in_zone_days, post_in_zone_days", "How many of the ten pre-control days, and of the ten post-control days, fall in an exclusion zone."),
        ("n_window, n_pre, n_post", "Trades summed over the pooled cells of the window days, the ten pre-control days and the ten post-control days."),
        ("med_window_bp, med_pre_bp, med_post_bp", "Medians of the daily pooled medians over the window, the pre-control and the post-control days."),
        ("d_bp", "D in bp: med_window_bp minus the mean of med_pre_bp and med_post_bp."),
        ("band_role", "Which band the ranks use: provisional, or of_record once the tape covers 2026-11-27."),
        ("rank_band, k_band", "How many band values are at or below D, of k_band band windows. Quarter-end and month-end rows only. Read it with its caveat: "
                              "overlapping windows from N stretches; not independent draws (N is `stretches` in band.csv, and is different for each pair)."),
        ("rank_ref, k_ref", "The same against the reference windows. Read it with its caveat: one window per stretch; N values (N is `k_ref` in band.csv)."),
        ("mean_tenor_window_y, mean_tenor_ctrl_y, d_mean_tenor_y", "Trade-weighted mean tenor in years of the window days, of the 20 control days, and the "
                                                                    "difference."),
        ("mix_limit_y, mix_flag", "The 95th percentile of the absolute tenor difference over the band, and yes when this row is above it."),
    ],
    "anchors_tenor.csv": [
        ("pair, anchor_date, anchor_type", "As in anchors.csv. Rows are written for quarter-end, month-end and reference anchors."),
        ("tenor_y", "The tenor, 1 to 5 years."),
        ("days_window, days_pre, days_post", "Days among the anchor's own window and control days on which this tenor's own median is published (at least 10 trades)."),
        ("med_window_bp, med_pre_bp, med_post_bp, d_bp", "As in anchors.csv, on those days only."),
        ("status", "complete (at least 2 window days and 3 days in each control), too_few_days, or anchor_not_complete."),
    ],
    "band.csv": [
        ("pair, band_role, asof, tape_last_date", "The band's role, the date it is cut at, and the last date on the tape."),
        ("k_anchors, stretches", "Band windows and the quarters they come from."),
        ("p5_bp to p95_bp, sd_bp", "Nearest-rank percentiles and the population standard deviation of the band's D values."),
        ("p5_leave_one_stretch_out_min_bp, p5_leave_one_stretch_out_max_bp", "The 5th percentile recomputed with each stretch left out in turn: lowest and highest."),
        ("k_ref, ref_min_bp, ref_median_bp, ref_max_bp", "The reference set: one window per stretch."),
        ("mix_limit_y", "The tenor-mix limit."),
        ("inputs_sha256", "sha256 of one line per covered weekday up to asof: the ledger's pooled and tenor counts and the pooled median, verbatim."),
    ],
    "questions.csv": [
        ("question, pair, anchor_type, anchor_date", "Q1 each quarter-end; Q2 quarter-end statistics; Q3 month-end statistics; Q4 thin trading; Q5 tenor mix and "
                                                      "tenors; Q6 short-tenor availability."),
        ("statistic, value, unit, denominator", "What is reported, its value, its unit, and what it is out of."),
        ("note", "The required sentence, and the caveat that goes with each rank."),
    ],
    "short_tenor_availability.csv": [
        ("series, tenor", "The ledger's monthly 3-month and 1-year cells."),
        ("first_month, last_month, months, months_published", "Months on the file, and months whose median is published."),
        ("n_total, n_month_median, days_with_trades_month_median", "Trades in all months, median trades a month, median days with trades a month."),
    ],
    "inputs.csv": [("file, sha256, rows, first_date, last_date", "Each ledger file read, its hash, its data rows and its first and last date or month.")],
    "checks.csv": [("check_id, description, expected, observed, status", "The pinned checks of the spec. Status is PASS, WARN, FAIL or INFO.")],
    "columns.tsv": [("file, columns", "The header of every file, columns joined by a vertical bar.")],
}


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    for r in rows:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def readme_table_rows(w):
    rows = []
    for p in PAIR_NAMES:
        pr = w.pairs[p]
        for r in pr.qe:
            comp = r.status == "complete"
            win = "%s to %s" % (r.window_first, r.window_last) if r.window_first else "-"
            zone = "%s / %s" % (r.pre_zone, r.post_zone) if (r.pre_zone is not None and r.post_zone is not None) else "-"
            rows.append([p, r.date.isoformat(), r.status, win, pos_text(r), q3(r.D) if comp else "-",
                         "%d of %d (%s)" % (r.rank_band, r.k_band, band_caveat(pr.summ["stretches"])) if comp else "-",
                         "%d of %d (%s)" % (r.rank_ref, r.k_ref, ref_caveat(len(pr.summ["refvals"]))) if comp else "-", zone,
                         ("yes: " + MIX_PHRASE if r.mflag else "no") if comp and r.mflag is not None else "-"])
    return rows


def render_readme(w):
    tape = w.tape
    L = []
    A = L.append
    A("# The 1-5-year cross-currency basis around quarter-ends\n")
    A("*A descriptive table. It carries no verdict and tests nothing.*\n")
    A(OPENING + "\n")
    A(REQUIRED + "\n")
    A("## Results\n")
    A("**Sign: negative means dollars cost more.** D below zero means the basis was more negative in the window than around it. The ledger is this "
      "project's daily table of swap prices, built from DTCC's public price dissemination ([data/swap_tape](../swap_tape/README.md)); the tape is the run of "
      "days it covers, here %s to %s. A bp is a basis point, one hundredth of a percentage point. An exclusion zone is the span from 21 days before to 7 days "
      "after a quarter-end; \"Days in zone\" counts how many of the ten days before the window, and of the ten after the anchor, fall inside one. Quarter-ends "
      "on or before 2026-09-30 were examined before the build. A row says \"on_date\" when the window ends on the quarter-end, and otherwise names how many "
      "days before it the window ended.\n" % (tape.first, tape.last))
    A(md_table(["Pair", "Quarter-end", "Status", "Window", "Position", "D (bp)", "Rank among mid-quarter windows", "Rank among reference windows",
                "Days in zone, pre / post", "Mix"], readme_table_rows(w)) + "\n")
    A("Status: `complete` rows carry D. `incomplete` means too little history, or that the days after the quarter-end have not all posted yet. `gap` means "
      "the nearest liquid day was more than 10 days from the quarter-end. `low_n` means fewer trades than the floors (25 in the window, 50 in each control). "
      "Only `complete` rows carry a median, D or a rank. Month-ends and the per-tenor differences are in `anchors.csv` and `anchors_tenor.csv`.\n")
    A("## Defined terms\n")
    A("- **Basis.** The ledger's `xccy` series: the spread, in bp, on the yen, euro or sterling overnight-rate leg of a floating-for-floating swap against flat "
      "SOFR. Negative is the conventional sign of a dollar premium; some of the literature uses the opposite sign.")
    A("- **Window.** The last five liquid days on or before the anchor. A liquid day is a weekday on which the pooled 1-5-year cell has a published median "
      "(5 or more trades) and the ledger raises no low-count warning for that pair.")
    A("- **D.** The median of the five window medians, minus the mean of two medians: that of the ten liquid days before the window (after a three-day gap) "
      "and that of the ten liquid days after the anchor (after a three-day gap).")
    A("- **Band, and reference set.** The band is D computed the same way on mid-quarter-month windows, which sit clear of every exclusion zone, one per "
      "distinct window. The reference set is one band window per stretch between quarter-ends: the middle one in date order.\n")
    A("## Worked anchor\n")
    wa = None
    for r in w.pairs["JPYUSD"].qe:
        if r.date == D_("2025-06-30"):
            wa = r
    if wa is not None and wa.status == "complete":
        ex = lambda x: format(to_dec(x).normalize(), "f")
        A("**JPY 2025-06-30, D = %s.** From its row in `anchors.csv`: the median of the five window days is %s bp, the median of the ten days before is %s bp and "
          "the median of the ten days after is %s bp. D = %s - (%s + %s) / 2 = %s bp. The medians are written here exactly; the columns of `anchors.csv` round "
          "them to three decimals, and a median of ten can have a fourth, so a hand calculation from the rounded columns can differ from D in the "
          "third decimal.\n" % (q3(wa.D), ex(wa.medw), ex(wa.medp), ex(wa.medq), ex(wa.medw), ex(wa.medp), ex(wa.medq), q3(wa.D)))
    else:
        A("The worked anchor is JPY 2025-06-30; it is not complete on this tape.\n")
    A("## Limits\n")
    A("- **What the data cannot say.** A difference in these medians, or its rank among the band windows, says nothing about who traded or why. " + NEITHER +
      " A difference at a quarter-end is a difference between reported prices, nothing more. Nothing here covers short-dated FX swaps or repo, where the "
      "dollar-funding literature places quarter-end pressure; the tape holds no contract of a week to three months that can be read daily.")
    A("- **The band is short and clustered.** It comes only from mid-quarter-month windows, in " + ", ".join(
        "%d (%s)" % (w.pairs[p].summ["stretches"], p) for p in PAIR_NAMES if w.pairs[p].summ["k"]) +
      ", so a rank against it is not a draw from a known distribution. Its lower tail rests on few episodes: " + "; ".join(
          "%s: the three lowest band values come from %s, and leaving out one stretch at a time moves P5 between %s and %s bp" % (
              p, " and ".join(stretch_label(s) for s in sorted(set(w.pairs[p].summ["lowest_stretches"]))), q3(w.pairs[p].summ["loso"][0]),
              q3(w.pairs[p].summ["loso"][1])) for p in PAIR_NAMES if w.pairs[p].summ["k"]) + ".")
    ye = [r for p in PAIR_NAMES for r in w.pairs[p].qe if r.date.month == 12 and r.gap_days]
    A("- **A row describes its window, not necessarily the quarter-end.** Year-end windows can end earlier: over the holidays most days were not liquid "
      "(fewer than 5 trades, or the ledger's low-count warning). On this tape: " +
      ("; ".join("%s %s (%s)" % (r.pair, r.date, window_phrase(r.gap_days, "quarter-end")) for r in ye) if ye else "none") + ".")
    zc = [r.pre_zone for p in PAIR_NAMES for r in w.pairs[p].qe if r.status == "complete"]
    zo = [r.pre_zone for p in PAIR_NAMES for r in w.pairs[p].qe if r.status == "complete" and r.on_date]
    if zc:
        rng = ("Across the %d complete quarter-ends in the table, between %d and %d of the ten days before the window lie inside an exclusion zone%s. " % (
            len(zc), min(zc), max(zc), " (%d to %d where the window ends on the quarter-end)" % (min(zo), max(zo)) if zo else ""))
    else:
        rng = "No quarter-end in the table is complete yet. "
    A("- **Spike or plateau.** " + rng + "A level shift spread over the whole zone shows in D at about half its size; a move confined "
      "to the five window days shows whole. `pre_in_zone_days` and `post_in_zone_days` are printed so that a reader can tell which case a row is closer to.")
    A("- **Tenor mix.** The pooled series mixes tenors, and the mean tenor differs by day. A row above the mix limit says \"" + MIX_PHRASE + "\".")
    A("- **Not general.** The ledger covers US-reported OIS-versus-SOFR basis swaps only. Whether a swap resets its notional is not visible, and trades "
      "reported only outside the US are not in it. The ranks are descriptive and are not tests.\n")
    A("## Column dictionary\n")
    for fn in ALLOW_ORDER:
        A("**`%s`**\n" % fn)
        A(md_table(["Column", "Meaning"], [["`%s`" % c, m] for c, m in COLDOC[fn]]) + "\n")
    A("## Provenance\n")
    A("Derived from DTCC Public Price Dissemination, CFTC cumulative rates reports (pddata.dtcc.com), through the project's swap-tape ledger in "
      "[data/swap_tape](../swap_tape/README.md). Only statistics are published, under the ledger's count floor, as ruled in THE_ASK.md (E-024) for non-commercial "
      "research; the CC BY 4.0 licence of this repository covers this project's computation only. Inputs: the ledger's derived files, whose sha256 and "
      "date ranges are in `inputs.csv` (the specification read the ledger as committed at %s). The script is [bin/quarter_end_basis.py](../../bin/quarter_end_basis.py); "
      "the specification is [%s](../../%s) and is the authority. Choices the specification left open are listed in [SOURCES.md](SOURCES.md).\n"
      % (LEDGER_COMMIT_SPEC, SPEC_REL, SPEC_REL))
    return "\n".join(L)


def decisions(w, tape):
    d = [
        "Inputs. Only `cells_YYYY.csv`, `diagnostics_YYYY.csv` and `monthly_short_tenor.csv` are opened. The ledger's `date_status` rows live in `ledger_YYYY.csv` and are not read: "
        "a weekday absent from the cells inside the covered range is covered but not liquid (2.3). `tape_last_date` is the largest date in the cells files, "
        "whatever the series, and the first date likewise; every weekday between them is covered. Nothing reads a wall clock except the staleness line printed to stdout.",
        "Liquid days. A weekday is liquid for a pair when its pooled cell has status ok or thin, a non-blank median, and no `warn_f0_low_<series>` row for that "
        "date. A blank median is never read as zero.",
        "Anchors. Quarter-end anchors are the last weekday on or before each calendar quarter-end from 2024-12-31 whose anchor date is on or before "
        "`tape_last_date`. Month-end anchors are the last weekday of January, February, April, May, July, August, October and November that fall on the tape "
        "(the first, 2024-10-31, is `incomplete`). A placebo is any other covered weekday and is written only when it is in the band.",
        "`in_sample`. yes for every anchor dated on or before 2026-09-30, of any type, since the band was also examined before the build; no after.",
        "Window geometry. j is the index of the last liquid day on or before the anchor and k = j + 1. `post_first` is L[k]. Window fields (dates, gap_days, "
        "on_date, span, counts) are printed whenever the days exist, including on `incomplete`, `gap` and `low_n` rows, so a reader can see why a row is not "
        "complete; medians, D, ranks and mean tenors are printed only on `complete` rows.",
        "Zones and the band. Exclusion zones are [q - 21 days, q + 7 days] for the calendar quarter-ends 2024-09-30 to 2027-12-31. A stretch is the calendar "
        "quarter that holds the anchor date. Percentiles are nearest rank, rank ceil(q x k), with q an exact fraction. The reference pick is the band anchor "
        "at position ceil(m/2), counted from 1 in date order, in each stretch. The reference median is the usual median (the mean of the two middle values when the count is even). "
        "The standard deviation is the population one, computed on exact fractions and square-rooted at 60 digits.",
        "Band roles. While the tape ends before 2026-11-27 each pair has one `provisional` row (asof = `tape_last_date`). From 2026-11-27 each pair has an "
        "`of_record` row, copied unchanged from the committed `band.csv` when it holds one and computed otherwise, and a `recomputed` row cut at the same asof "
        "(2026-11-27) from the current files, so that a difference can only come from a revised input. Both rows are written on every build from then on, "
        "which keeps a rebuild byte-identical. Ranks use the values recomputed at asof 2026-11-27; the counts at or below band P5 in Q2 and Q3 use the same values.",
        "Mix. The limit is the 95th percentile (nearest rank) of the absolute tenor difference over the band windows. A row is flagged when its absolute "
        "difference is above the limit (strictly). Mean tenor weights each tenor by the ledger's per-tenor trade counts, which are always published.",
        "Per-tenor D. Rows are written for quarter-end, month-end and reference anchors on the anchor's own window and control days, using days where that "
        "tenor's own median is published. `complete` needs at least 2 window days and 3 days in each control.",
        "Questions. Q4 uses anchors for which a window exists; `warn_f0_low` days are counted among the 10 calendar days ending on the anchor. Q2 and Q3 print "
        "no standard error or test statistic. By a supervisor ruling (round 5) the dependence caveat names each pair's own count instead of the specification's "
        "\"about eight\": \"overlapping windows from N stretches; not independent draws\" (N = 8, 8, 5 for JPY, EUR, GBP) and \"one window per stretch; N values\"; "
        "the same ruling writes \"1 day\" for the singular in \"a window ending N days before the quarter-end\".",
        "Rounding. Ledger medians are Decimals parsed from their strings; D, ranks and comparisons are exact; text is rounded half away from zero at 3 decimals. "
        "A value that rounds to -0.000 is printed 0.000.",
        "Allowlist (round 4, O-4). `post_in_zone_days` was added to `anchors.csv` after `pre_in_zone_days`. The canonical allowlist text is now %s bytes and its sha256 is "
        "`%s` (it was 1,078 bytes, `479678adef66bcd7aa9ca5e3f90a89d7b0e1ffebc90d6e97921dd8f76f0c2ed6`). The spec's block and its printed hash were updated "
        "to match before the build, and the hash is held in the script and in `bin/check.sh`." % (format(len(SPEC_ALLOW_TEXT.encode()), ","), SPEC_ALLOW_SHA256),
        "Pinned checks. C05-C08 and C13-C15 are evaluated on the tape truncated at 2026-10-21 and on monthly rows to 2026-09. Only C01, C07 and C09 can WARN on "
        "a difference; any other mismatch is FAIL. C03b fails if the median of the JPY liquid-day medians is not negative or is not the pinned value. C10 is a "
        "second in-process render with the first render's `band.csv` standing in for the committed one. C09 reads `CALENDAR.tsv` and C12 is stdout only.",
        "Fixes made after the first build, which showed two pinned checks failing on formatting alone: the median of a count (check C08) was written 14.500 and "
        "is now written 14.5 (a count median prints without trailing zeros), and the complete per-tenor cells of check C15a were listed in alphabetical order "
        "of pair and are now listed in the order JPYUSD, EURUSD, GBPUSD, then by date and tenor. No computed value changed.",
        "Round 5 fixes (verifier): the year-end sentence of the README now gives the observed reason (most holiday days were not liquid); the README defines "
        "the tape, the ledger, bp and the exclusion zone at first use and states the observed range of pre-control days in a zone; `post_in_zone_days` is pinned "
        "in C14post (JPY 0, 2, 2, 2, 0, 0, 0; EUR 2, 2, 2, 1, 0, 0, 2, in quarter-end order); the selftest replaces the wall clock globally for the rebuild test "
        "and has guards for the counts at or below band P5, the sample-or-population standard deviation, the in-sample end date, the 10-day warn window, the "
        "per-tenor control minimum and the README text at a gap of 1 day.",
        "The values of C13 were computed by the second reviewer on the committed tape before the build and re-derived by the spec author; this build "
        "recomputes them and pins them. The specification's other values (3.8 table, C06, C14, C15) are pinned in the same way.",
    ]
    return d


def render_sources(w, tape):
    L = []
    A = L.append
    A("# Sources, terms and build decisions\n")
    A("## Source and terms\n")
    A("Derived from DTCC Public Price Dissemination, CFTC cumulative rates reports (pddata.dtcc.com), through the project's swap-tape ledger "
      "(`data/swap_tape/`; its specification is `_research/2026-10-14-Swap-Tape-Ledger-Spec.md`). Use is non-commercial research, ruled in THE_ASK.md as E-024: "
      "statistics only, nothing raw committed, no per-trade value, no file name, row or identifier. A pooled daily median enters only where the ledger "
      "published it (5 or more trades) and a tenor median only where it published one (10 or more). The CC BY 4.0 licence covers this project's computation only. "
      "This build downloads nothing and reads nothing outside the repository.\n")
    A("## Ledger files read\n")
    A("The specification read the ledger as committed at %s (cells to 2026-10-21). The files read in this build, with their sha256 and ranges, are in `inputs.csv`."
      " The closed-year files are pinned in `checks.csv` (C01): `cells_2024.csv` %s and `cells_2025.csv` %s.\n"
      % (LEDGER_COMMIT_SPEC, PIN_HASH["cells_2024.csv"], PIN_HASH["cells_2025.csv"]))
    A("## BIS CGFS Papers No 65 (June 2020)\n")
    A("https://www.bis.org/publications/cgfs-paper-65-us-dollar-funding-international-perspective.pdf, sha256 "
      "`0a1d5ce92b9fec5756c729c449e01e9df5ab5db7f90111ef8119d7e3c5a2c504` (3,704,415 bytes, observed 23 Oct 2026). \"Brief excerpts may be reproduced or translated "
      "provided the source is stated\" (CGFS 65, p ii). The quarter-end passages are on printed pages 28, 35, 44 and 73. CGFS 65 p 35: \"US repo rates may spike and "
      "spill over to short-dated FX swaps\". The paper sizes no quarter-end move in 1-5-year basis swaps.\n")
    A("## Papers relayed, not re-read\n")
    A("Relayed by the round-3 attack and marked as such: Du, Tepper and Verdelhan, NBER WP 23170 (one-week contracts, 30 to 40 bp); Georgievska, Karner and "
      "Syrstad 2026, preliminary (4 to 5 bp at three months, \"very small\" at five years). Neither was read for this build.\n")
    A("## Prior work\n")
    A("`_research/2026-10-15-ST1-Swap-Spreads-Inflation-Gap-And-Basis.md` examined basis levels from the same ledger. This build adds the quarter-end "
      "comparison and does not revise those levels.\n")
    A("## Leg convention and corrections\n")
    A("CFTC orders the two floating legs alphabetically by underlier, and the JPY, EUR and GBP legs all sort before USD, so the ledger's foreign-leg-first reading holds "
      "for these pairs. No side (payer or receiver) is disseminated: each daily value is a median of traded spreads, not a mid. Package share and correction "
      "handling are as the ledger specification defines; this build adds no filtering of its own.\n")
    A("## In-sample values\n")
    A("The in-sample differences of check C13 (JPY and EUR, seven quarter-ends each) were computed by the second reviewer on the committed tape before the "
      "build. The spec author re-derived all fourteen exactly, and this build recomputes and pins them. Round 3 of the supervisor's rulings re-scoped the "
      "build to a descriptive table.\n")
    A("## Build decisions\n")
    for i, t in enumerate(decisions(w, tape), 1):
        A("%d. %s" % (i, t))
    A("")
    return "\n".join(L)


# ------------------------------------------------------------------------------------------------------------------------
# rendering the whole folder and the build
# ------------------------------------------------------------------------------------------------------------------------
def render_texts(tape, prev_band, cal_text, c10, today_fn):
    w = compute_all(tape)
    pw = compute_all(tape.truncate(PIN_LAST, PIN_MONTH))
    brows, bwarns = band_rows(w, prev_band)
    checks = build_checks(w, pw, tape, cal_text, c10, bwarns)
    files = {"anchors.csv": render_csv("anchors.csv", anchor_rows(w)), "anchors_tenor.csv": render_csv("anchors_tenor.csv", tenor_rows(w)),
             "band.csv": render_csv("band.csv", brows), "questions.csv": render_csv("questions.csv", question_rows(w)),
             "short_tenor_availability.csv": render_csv("short_tenor_availability.csv", short_rows(tape, None)),
             "inputs.csv": render_csv("inputs.csv", inputs_rows(tape)), "checks.csv": render_csv("checks.csv", checks), "columns.tsv": columns_tsv(),
             "README.md": render_readme(w), "SOURCES.md": render_sources(w, tape)}
    if M("clock_in_output"):
        files["checks.csv"] += "# built %s\n" % today_fn().isoformat()
    if M("rebuild_drift"):
        _SEQ[0] += 1
        files["SOURCES.md"] += "\nbuild %d\n" % _SEQ[0]
    return files, bwarns, w


def guard_files(files):
    bad = all_wording_problems(files) + descriptive_problems(files)
    if bad:
        raise DataError("the rendered folder breaks its wording rules: " + "; ".join(bad[:6]))


def build_folder(tape, prev_band=None, cal_text="", today_fn=None):
    """Three renders: two to test that a rebuild changes nothing (C10), and the final one."""
    today_fn = today_fn or (lambda: dt.date.today())
    t1, _, _ = render_texts(tape, prev_band, cal_text, ("identical", "not run", "INFO"), today_fn)
    t2, _, _ = render_texts(tape, t1["band.csv"], cal_text, ("identical", "not run", "INFO"), today_fn)
    diff = sorted(n for n in t1 if t1[n] != t2[n])
    c10 = ("identical", "identical" if not diff else "changed: " + ", ".join(diff), "PASS" if not diff else "FAIL")
    files, bwarns, w = render_texts(tape, prev_band, cal_text, c10, today_fn)
    guard_files(files)
    return files, bwarns, w


def write_folder(files, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for name, text in files.items():
        with open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)


def read_if(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def run_build(a):
    tape = load_tape_dir(a.tape)
    prev = read_if(os.path.join(a.out, "band.csv"))
    cal = read_if(a.calendar) or ""
    files, bwarns, w = build_folder(tape, prev, cal)
    write_folder(files, a.out)
    h, rows = parse_csv_text(files["checks.csv"])
    print("quarter_end_basis build: tape %s to %s; band role %s; %d files written to %s" % (tape.first, tape.last, w.rank_role, len(files), a.out))
    counts = {}
    for r in rows:
        counts[r[4]] = counts.get(r[4], 0) + 1
        print("  %-4s %-9s %s" % (r[4], r[0], r[1][:90]) if r[4] != "PASS" else "  PASS %-9s" % r[0])
    print("checks: " + ", ".join("%s %d" % kv for kv in sorted(counts.items())))
    for m in bwarns:
        print("WARN: " + m)
    days, text = staleness(tape, dt.date.today())
    print("C12 (stdout only): " + text)
    print(REQUIRED)
    return 0


# ==================================================================================================================================================
# guards that read this very source (G8, G11)
# ==================================================================================================================================================
_NET_MODS = ("urllib", "http", "socket", "ssl", "requests", "ftplib", "smtplib")
_BAN_TOKENS = ("dtcc" + "_ppd", "ST" + "OP")


def offline_problems(src):
    """The build opens no network module and names neither the ledger's cache nor its latch (R1, R2, G11)."""
    out = []
    if not M("scan_net_off"):
        rx = re.compile(r"^[ \t]*(?:import[ \t]+[^#\n]*\b(?:%s)\b|from[ \t]+(?:%s)\b)" % ("|".join(_NET_MODS), "|".join(_NET_MODS)), re.M)
        out += ["imports a network module: %s" % m.group(0).strip() for m in rx.finditer(src)]
    if not M("scan_path_off"):
        for tok in _BAN_TOKENS:
            if tok in src:
                out.append("names %s" % tok)
    return out


def design_line():
    """DESIGN_TEXT rebuilt from the constants (3.10)."""
    d = dict(DESIGN)
    if M("design_const"):
        d["window"] = 6
    return ("X4-DESIGN v2 descriptive | %s | liquid = published median, no warn_f0_low | window %d, buffer %d, control %d+%d | tolerance %d days | "
            "j-%d<0 incomplete | floors %d/%d/%d | zone %d/+%d | band asof %s, dedupe (j,k), nearest rank | ref = ceil(m/2) per stretch | "
            "mix limit P%s | tenor D %d/%d/%d | spec is the authority" % (
                d["pool"], d["window"], d["buffer"], d["control"], d["control"], d["tolerance"], d["window"] + d["buffer"] + d["control"] - 1,
                d["floor_window"], d["floor_control"], d["floor_control"], d["zone_lo"], d["zone_hi"], d["band_asof"], d["mix_pct"],
                d["tenor_min_window"], d["tenor_min_control"], d["tenor_min_control"]))


def design_text():
    return DESIGN_TEXT + " x" if M("design_text_drift") else DESIGN_TEXT


def read_spec(path=None):
    path = path or SPEC_DEFAULT
    with open(path, encoding="utf-8") as f:
        return f.read()


def spec_block(text):
    i = text.index("**Header allowlist, canonical text.**")
    j = text.index("```\n", i)
    k = text.index("\n```", j + 4)
    m = re.search(r"sha256 of that text \([0-9,]+ bytes\): `([0-9a-f]{64})`", text)
    return text[j + 4:k] + "\n", m.group(1)


def spec_design_line(text):
    i = text.index("### 3.10 `DESIGN_TEXT`")
    j = text.index("\n`X4-DESIGN", i) + 2
    k = text.index("`\n", j)
    return " ".join(text[j:k].split("\n"))


# ==================================================================================================================================================
# selftest fixtures: synthetic ledger files (nothing here is a real print)
# ==================================================================================================================================================
class Dy(object):
    """One synthetic pooled cell of a pair-day, and its tenor cells."""

    def __init__(self, n=30, med="-30.000", status=None, tn=None, tmed=None):
        self.n, self.med = n, med
        self.status = status or ("ok" if n >= 10 else ("thin" if n >= 5 else "below_min_n"))
        self.tn = list(tn) if tn is not None else [n // 10] * 4 + [n - 4 * (n // 10)]
        if tmed is None:
            tmed = [("" if self.tn[t] < 10 or med == "" else str(Decimal(med) + Decimal("0.25") * (t - 2))) for t in range(5)]
        self.tmed = list(tmed)


def fx_texts(spec, first, last, warn=None, extra_cells=(), monthly=()):
    """Ledger-shaped files for a synthetic tape: spec = {pair: {date: Dy}}; warn = {pair: {dates}}. Returns {name: bytes}."""
    by_year = {}
    for y in range(first.year, last.year + 1):
        by_year[y] = []
    for p, days in spec.items():
        series = SERIES_OF[p]
        for d, x in sorted(days.items()):
            by_year[d.year].append((d, "%s,%s,pool1to5,headline,bp,%d,%s,,,,,,,%s" % (d, series, x.n, x.med, x.status)))
            for t in range(5):
                tm = x.tmed[t]
                by_year[d.year].append((d, "%s,%s,%d,headline,bp,%d,%s,,,,,,,%s" % (d, series, t + 1, x.tn[t], tm, "ok" if tm != "" else "below_min_n")))
    for d in (first, last):
        by_year[d.year].append((d, "%s,sofr_ois,2,headline,pct,0,,,,,,,,below_min_n" % d))
    for line in extra_cells:
        by_year[D_(line[:10]).year].append((D_(line[:10]), line))
    texts = {}
    for y, rows in by_year.items():
        body = "\n".join(l for _, l in sorted(rows, key=lambda x: x[0]))
        texts["cells_%d.csv" % y] = ("# source: synthetic fixture\n" + ",".join(CELLS_HEADER) + "\n" + body + "\n").encode()
        dl = ["%s,corr_applied,0," % first]
        for p, ds in (warn or {}).items():
            for d in sorted(ds):
                if d.year == y:
                    dl.append("%s,warn_f0_low_%s,F0 n 0 below half the trailing median 52.0," % (d, SERIES_OF[p]))
        texts["diagnostics_%d.csv" % y] = ("# source: synthetic fixture\n" + ",".join(DIAG_HEADER) + "\n" + "\n".join(dl) + "\n").encode()
    texts["monthly_short_tenor.csv"] = ("# source: synthetic fixture\n" + ",".join(MONTHLY_HEADER) + "\n" + "\n".join(monthly) + ("\n" if monthly else "")).encode()
    return texts


def fx_tape(spec, first, last, warn=None, **kw):
    return load_tape(fx_texts(spec, first, last, warn, **kw))


class Lcg(object):
    def __init__(self, seed):
        self.s = seed

    def next(self, m):
        self.s = (self.s * 1103515245 + 12345) % (2 ** 31)
        return (self.s >> 8) % m


def fmt3(x):
    return str(Decimal(x).quantize(Decimal("0.001")))


def synth_spec(first, last, seed=7, extreme_after=None):
    """A year or two of plausible-looking pair-days: holidays, thin and empty days, warn days, a drifting level with noise."""
    rng = Lcg(seed)
    spec = {p: {} for p in PAIR_NAMES}
    warn = {p: set() for p in PAIR_NAMES}
    base = {"JPYUSD": Decimal(-30), "EURUSD": Decimal(-3), "GBPUSD": Decimal(2)}
    wd = weekdays(first, last)
    for i, d in enumerate(wd):
        holiday = (d.month == 12 and d.day >= 24) or (d.month == 1 and d.day <= 2) or i % 37 == 11
        for p in PAIR_NAMES:
            u = rng.next(100)
            if holiday:
                continue
            if u < 8:
                spec[p][d] = Dy(n=3, med="", status="below_min_n")
                continue
            n = 7 if u < 20 else 12 + rng.next(25)
            level = base[p] + Decimal(i) * Decimal("0.02") + (Decimal(rng.next(24)) - 12) * Decimal("0.125")
            if extreme_after is not None and d > extreme_after:
                level += 500
            spec[p][d] = Dy(n=n, med=fmt3(level))
            if rng.next(100) < 6:
                warn[p].add(d)
    return spec, warn


_CACHE = {}


def world_small():
    """A synthetic tape 2024-10-14 to 2025-10-31, and its computation (built once, with no mutant active)."""
    if "w" not in _CACHE:
        first, last = D_("2024-10-14"), D_("2025-10-31")
        spec, warn = synth_spec(first, last)
        tape = fx_tape(spec, first, last, warn)
        _CACHE["tape"] = tape
        _CACHE["w"] = compute_all(tape)
        files, bwarns, w = build_folder(tape, None, "", lambda: dt.date(2030, 1, 1))
        _CACHE["files"], _CACHE["bwarns"] = files, bwarns
    return _CACHE["w"]


def world_files():
    world_small()
    return _CACHE["files"]


@contextlib.contextmanager
def fake_clock(day):
    """Replace date.today, datetime.now / utcnow / today and time.time for every caller in the process."""
    real_date, real_dt, real_time = dt.date, dt.datetime, time.time

    class FDate(real_date):
        @classmethod
        def today(cls):
            return day

    class FDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(day.year, day.month, day.day, 12, 0, 0)

        utcnow = today = now

    dt.date, dt.datetime, time.time = FDate, FDT, (lambda: float(day.toordinal()) * 86400.0)
    try:
        yield
    finally:
        dt.date, dt.datetime, time.time = real_date, real_dt, real_time


@contextlib.contextmanager
def asof_patch(d):
    g = globals()
    old = g["BAND_ASOF"]
    g["BAND_ASOF"] = d
    try:
        yield
    finally:
        g["BAND_ASOF"] = old


def fx_run(pair="JPYUSD", start=D_("2025-02-03"), count=80, holes=(), n=30, value=None):
    """count consecutive weekdays from start, one cell each, a hole at each listed index; value(i) is the median (default: -30 - 0.25 i)."""
    wd = weekdays(start, start + dt.timedelta(days=count * 2))[:count]
    value = value or (lambda i: Decimal(-30) - Decimal("0.25") * i)
    spec = {p: {} for p in PAIR_NAMES}
    for i, d in enumerate(wd):
        if i not in holes:
            spec[pair][d] = Dy(n=n, med=fmt3(value(i)))
    tape = fx_tape(spec, wd[0], wd[-1])
    return tape, wd, PairData(tape, pair)


# ==================================================================================================================================================
# the guards (section 8); each test runs on synthetic data, and each guard's mutants must make it fail
# ==================================================================================================================================================
class Checks:
    def __init__(self):
        self.items = []

    def ok(self, name, cond, detail=""):
        self.items.append((name, bool(cond), "" if cond else detail))

    def eq(self, name, got, want):
        self.ok(name, got == want, "got %r, want %r" % (got, want))

    def failed(self):
        return [(n, d) for n, c, d in self.items if not c]


def t_g1(ck):
    days = weekdays(D_("2025-03-03"), D_("2025-03-14"))
    sp = {p: {} for p in PAIR_NAMES}
    s = sp["JPYUSD"]
    s[days[0]] = Dy(n=20, med="-30.000")
    s[days[1]] = Dy(n=20, med="-31.000")                        # a warn_f0_low day: not liquid
    s[days[2]] = Dy(n=7, med="-32.000", status="thin")          # thin: liquid
    s[days[3]] = Dy(n=3, med="", status="below_min_n")
    s[days[4]] = Dy(n=20, med="", status="ok")                  # a malformed blank median: never zero, never liquid
    s[days[6]] = Dy(n=20, med="-33.000")                        # days[5] is a hole
    s[days[7]] = Dy(n=0, med="", status="below_min_n")
    s[days[8]] = Dy(n=5, med="-34.000", status="thin")
    s[days[9]] = Dy(n=12, med="-35.000")
    warn = {"JPYUSD": {days[1]}}
    tape = fx_tape(sp, days[0], days[-1], warn)
    P = PairData(tape, "JPYUSD")
    ck.eq("liquid days: ok and thin, with a median, no warn_f0_low", [d.isoformat() for d in P.dates], [days[i].isoformat() for i in (0, 2, 6, 8, 9)])
    ck.eq("the tape ends on the last date in the cells files", tape.last, days[-1])
    ck.ok("the hole weekday is covered but not liquid", days[5] in covered_weekdays(tape) and days[5] not in P.dates)
    lines = []
    for i, d in enumerate(days):
        x = s.get(d)
        f = [""] * 7 if x is None else [str(x.n), x.med] + [str(v) for v in x.tn]
        lines.append(",".join([d.isoformat()] + f + ["1" if d in warn["JPYUSD"] else "0"]) + "\n")
    ck.eq("inputs_sha256 hashes one line per covered weekday, the hole included", inputs_sha256(tape, "JPYUSD", days[-1]),
          hashlib.sha256("".join(lines).encode()).hexdigest())
    ck.eq("inputs_sha256 stops at asof", inputs_sha256(tape, "JPYUSD", days[2]), hashlib.sha256("".join(lines[:3]).encode()).hexdigest())


def window_dates(r):
    return [[x.date for x in seg] if seg is not None else None for seg in (r.win, r.pre, r.post)]


def t_g2(ck):
    holes = (3, 9, 14, 20, 21, 33, 38, 44, 52, 60)
    tape, wd, P = fx_run(holes=holes)
    ld = [d for i, d in enumerate(wd) if i not in holes]
    ck.eq("fixture: liquid days", P.dates, ld)
    a = ld[25]
    r = evaluate(P, a, "quarter_end")
    ck.eq("window L[j-4..j], pre-control L[j-17..j-8], post-control L[k+3..k+12] (anchor on a liquid day)", window_dates(r), [ld[21:26], ld[8:18], ld[29:39]])
    ck.eq("status complete and the post-buffer is unused", r.status, "complete")
    ck.ok("fixture has hole weekdays inside the controls", any(wdn(ld[8]) <= wdn(wd[i]) <= wdn(ld[17]) for i in holes))
    hole = wd[44]
    j = ld.index(max(x for x in ld if x < hole))
    r = evaluate(P, hole, "placebo")
    ck.eq("an anchor on a hole weekday: j is the last liquid day before it, k the next", window_dates(r), [ld[j - 4:j + 1], ld[j - 17:j - 7], ld[j + 4:j + 14]])
    ck.ok("the window never holds a day after the anchor", all(x <= hole for x in window_dates(r)[0]))
    ck.eq("gap_days is the distance from the last liquid day", r.gap_days, (hole - ld[j]).days)
    r = evaluate(P, ld[10], "quarter_end")
    ck.eq("j - 17 < 0 is incomplete and indices never wrap", r.status, "incomplete")
    ck.ok("...with no median or D", r.D is None and r.medw is None)
    r = evaluate(P, ld[-3], "quarter_end")
    ck.eq("the tape not reaching L[k+12] is incomplete", r.status, "incomplete")
    ck.eq("...and D is not computed", r.D, None)
    r = evaluate(P, ld[17], "quarter_end")
    ck.eq("j = 17 is the first complete anchor (pre-control starts at L[0])", (r.status, window_dates(r)[1][0]), ("complete", ld[0]))
    r = evaluate(P, ld[16], "quarter_end")
    ck.eq("j = 16 is incomplete", r.status, "incomplete")


def _scenario(E, a, S):
    """Liquid days for 40 weekdays ending on E, none until S, then 20 from S; returns (P, a)."""
    pre = weekdays(E - dt.timedelta(days=80), E)[-40:]
    post = weekdays(S, S + dt.timedelta(days=40))[:20]
    spec = {p: {} for p in PAIR_NAMES}
    for i, d in enumerate(pre + post):
        spec["JPYUSD"][d] = Dy(n=30, med=fmt3(Decimal(-30) - Decimal("0.125") * i))
    tape = fx_tape(spec, pre[0], post[-1])
    return PairData(tape, "JPYUSD"), a


def t_g3(ck):
    fri, mon, tue = D_("2025-05-02"), D_("2025-05-12"), D_("2025-05-13")
    P, a = _scenario(fri, mon, mon + dt.timedelta(days=10))
    r = evaluate(P, a, "quarter_end")
    ck.eq("a gap of exactly 10 days on both sides is accepted", (r.gap_days, r.status), (10, "complete"))
    ck.eq("...and on_date is no", r.on_date, False)
    P, a = _scenario(fri, tue, tue + dt.timedelta(days=10))
    ck.eq("a gap of 11 days before the anchor is a gap", evaluate(P, a, "quarter_end").status, "gap")
    P, a = _scenario(fri, mon, mon + dt.timedelta(days=11))
    ck.eq("11 days to the first liquid day after the anchor is a gap", evaluate(P, a, "quarter_end").status, "gap")
    P, a = _scenario(fri, fri, fri + dt.timedelta(days=10))
    r = evaluate(P, a, "quarter_end")
    ck.eq("an anchor on a liquid day: gap_days 0, on_date yes", (r.gap_days, r.on_date, r.status), (0, True, "complete"))
    mon2 = D_("2025-05-05")
    P, a = _scenario(mon2, tue - dt.timedelta(days=7), tue - dt.timedelta(days=7) + dt.timedelta(days=10))
    r = evaluate(P, a, "quarter_end")
    ck.eq("gap_days 1 is not on_date", (r.gap_days, r.on_date), (1, False))


def need_complete(ck, r):
    """Record that the fixture anchor is complete; a test that cannot go on without D stops here, with a clean failure."""
    ck.eq("the fixture anchor is complete", r.status, "complete")
    return r.status == "complete"


def t_g4(ck):
    tape, wd, P = fx_run()
    r = evaluate(P, P.dates[35], "quarter_end")
    if not need_complete(ck, r):
        return
    ck.eq("a linear trend has D = 0 exactly (the symmetric control removes it)", r.D, Decimal(0))
    ck.eq("the pre-only difference would not be zero (window median minus pre-control median)", r.medw - r.medp, Decimal("-2.625"))
    ck.eq("median of five is the third value; of ten the mean of the fifth and sixth", (med([5, 1, 3, 2, 100]), med([Decimal(x) for x in range(1, 11)])),
          (3, Decimal("5.5")))
    ck.eq("a mean is not a median", med([Decimal(x) for x in (1, 2, 3, 4, 100)]), Decimal(3))
    ck.eq("-0.0625 prints -0.063 (half away from zero, not round())", q3(Decimal("-0.0625")), "-0.063")
    ck.eq("-4.3285 prints -4.329", q3(Decimal("-4.3285")), "-4.329")
    ck.eq("a count median prints exactly: 14.5, 3, 0.333", [numfmt(Fraction(29, 2)), numfmt(Fraction(3)), numfmt(Fraction(1, 3))], ["14.5", "3", "0.333"])
    mw, mp, mq = Decimal("2.364"), Decimal("2.737"), Decimal("1.219")
    d = diff_d(mw, mp, mq)
    ck.eq("D is exact in Decimal", d, Decimal("0.386"))
    ck.eq("a D equal to a band value in Decimal counts in its rank (float would not)", rank_le([Decimal("0.386")], d), 1)


def t_g5(ck):
    tape, wd, P = fx_run(value=lambda i: Decimal(-36) if 31 <= i <= 35 else Decimal(-30))
    r = evaluate(P, P.dates[35], "quarter_end")
    if not need_complete(ck, r):
        return
    ck.eq("a window 6bp more negative than its controls gives D = -6", r.D, Decimal(-6))
    ck.eq("...and the rank is the count of band values at or below D", rank_le([Decimal(x) for x in (-7, -3, 0, 2)], r.D), 1)
    ck.ok("the C03 sign test passes a negative JPY median", sign_ok(Decimal("-33.125")))
    ck.ok("...and fails a positive one", not sign_ok(Decimal("5")))


def brute_calendar(tape):
    qs = [dt.date(y, m, dd) for y in (2024, 2025, 2026, 2027) for m, dd in ((3, 31), (6, 30), (9, 30), (12, 31))]
    zone = [(q - dt.timedelta(days=21), q + dt.timedelta(days=7)) for q in qs]
    anchors = set()
    for y in range(tape.first.year, tape.last.year + 1):
        for m in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):
            d = dt.date(y, m, 28)
            while (d + ONE).month == m:
                d += ONE
            while d.weekday() > 4:
                d -= ONE
            if m in (3, 6, 9, 12) and d < QE_FIRST:
                continue
            anchors.add(d)
    return zone, anchors


def brute_med(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def brute_band(tape, pair, asof):
    """The band, rebuilt with plain loops from the loaded cells: [(anchor, D, stretch)]."""
    days, warn = tape.days[pair], tape.warn[pair]
    liquid = [d for d in sorted(days) if days[d].status in ("ok", "thin") and days[d].med is not None and d not in warn]
    zone, anchors = brute_calendar(tape)
    out, seen = [], set()
    d = tape.first
    while d <= tape.last:
        if d.weekday() < 5 and d not in anchors:
            j = max([i for i, x in enumerate(liquid) if x <= d], default=-1)
            k = j + 1
            if j >= 17 and k + 12 < len(liquid) and (d - liquid[j]).days <= 10 and (liquid[k] - d).days <= 10:
                win, pre, post = liquid[j - 4:j + 1], liquid[j - 17:j - 7], liquid[k + 3:k + 13]
                nw = sum(days[x].n for x in win)
                if nw >= 25 and sum(days[x].n for x in pre) >= 50 and sum(days[x].n for x in post) >= 50 and post[-1] <= asof:
                    if not any(pre[0] <= b and post[-1] >= a for a, b in zone) and (j, k) not in seen:
                        seen.add((j, k))
                        v = brute_med([days[x].med for x in win]) - (brute_med([days[x].med for x in pre]) + brute_med([days[x].med for x in post])) / 2
                        out.append((d, v, (d.year, (d.month - 1) // 3)))
        d += ONE
    return out


def t_g6(ck):
    world_small()
    tape = _CACHE["tape"]
    P = PairData(tape, "JPYUSD")
    items = band_items(P, tape.last)
    want = brute_band(tape, "JPYUSD", tape.last)
    ck.ok("the fixture band is not empty and has several stretches", len(want) >= 8 and len({w[2] for w in want}) >= 3, str(len(want)))
    ck.eq("band windows: complete, clear of every zone [q-21, q+7], one per (j, k), earliest date kept", [(r.date, r.D) for r in items], [(w[0], w[1]) for w in want])
    ck.ok("no quarter-end or month-end anchor is in the band", all(r.type == "placebo" for r in items))
    vals = [Decimal(x) for x in range(1, 53)]
    ck.eq("nearest rank: P5 of 52 values is the 3rd", nearest_rank(vals, Fraction(5, 100)), Decimal(3))
    ck.eq("nearest rank: P25, P50, P75, P95 of 20 values", [nearest_rank([Decimal(x) for x in range(1, 21)], Fraction(q, 100)) for q in (5, 25, 50, 75, 95)],
          [Decimal(1), Decimal(5), Decimal(10), Decimal(15), Decimal(19)])
    if not items:
        return
    s = band_summary(items, pick_reference(items))
    sv = sorted(w[1] for w in want)
    ck.eq("band percentiles from the plain loops", [s["p"][q] for q in (5, 25, 50, 75, 95)], [sv[-(-q * len(sv) // 100) - 1] for q in (5, 25, 50, 75, 95)])
    los = []
    for st in sorted({w[2] for w in want}):
        rest = sorted(w[1] for w in want if w[2] != st)
        los.append(rest[-(-5 * len(rest) // 100) - 1])
    ck.eq("leave-one-stretch-out P5: min and max over dropping one whole stretch", s["loso"], (min(los), max(los)))
    # a planted extreme after asof cannot change the band at asof
    first, last = D_("2024-10-14"), D_("2025-12-12")
    asof = D_("2025-09-26")
    spec_a, warn_a = synth_spec(first, last, extreme_after=D_("2025-10-24"))
    spec_b, warn_b = synth_spec(first, last)
    ta, tb = fx_tape(spec_a, first, last, warn_a), fx_tape(spec_b, first, last, warn_b)
    ba = [(r.date, r.D) for r in band_items(PairData(ta, "JPYUSD"), asof)]
    bb = [(r.date, r.D) for r in band_items(PairData(tb, "JPYUSD"), asof)]
    ck.ok("band at asof is the same whatever the tape holds after asof", ba == bb and len(ba) > 0, "%d vs %d" % (len(ba), len(bb)))
    ck.ok("...and every window ends by asof", all(r.post[-1].date <= asof for r in band_items(PairData(ta, "JPYUSD"), asof)))


def _fake(D, dmt, st, i=0):
    return R(D=Decimal(D), dmt=Fraction(dmt), stretch=st, date=dt.date(2025, 1, 1) + dt.timedelta(days=i))


def t_g7(ck):
    ck.eq("incomplete beats gap beats low_n", [decide_status(True, True, True), decide_status(False, True, True), decide_status(False, False, True),
                                               decide_status(False, False, False)], ["incomplete", "gap", "low_n", "complete"])
    ck.eq("floors 25 / 50 / 50 are inclusive", [low_n(25, 50, 50), low_n(24, 50, 50), low_n(25, 49, 50), low_n(25, 50, 49)], [False, True, True, True])
    tape, wd, P = fx_run()
    r = evaluate(P, P.dates[35], "quarter_end")
    ck.eq("n is trades summed over the days' pool cells, not days", (r.n_window, r.n_pre, r.n_post), (150, 300, 300))
    items = [_fake(i, Fraction(i, 10), (2025, i % 4), i) for i in range(1, 20)] + [_fake(0, Fraction(-30, 10), (2025, 0), 30)]
    s = band_summary(items, [])
    ck.eq("mix limit: P95 of the absolute tenor differences (the 19th of 20)", s["mix_limit"], Fraction(19, 10))
    ck.ok("the flag is strict and symmetric", mix_flag(Fraction(19, 10), Fraction(19, 10)) is False and mix_flag(Fraction(-20, 10), Fraction(19, 10)) is True)
    ck.eq("no limit, no flag", mix_flag(Fraction(1), None), None)


def t_g8(ck):
    spec = read_spec()
    ck.eq("DESIGN_TEXT is the spec's line (3.10)", DESIGN_TEXT, spec_design_line(spec))
    ck.eq("DESIGN_TEXT is rebuilt from the DESIGN constants", design_line(), DESIGN_TEXT)
    ck.eq("the text the build uses is DESIGN_TEXT", design_text(), DESIGN_TEXT)
    ck.eq("the constants in force are the DESIGN ones", (WINDOW, BUFFER, CONTROL, TOL, FLOOR_W, FLOOR_C, ZLO, ZHI, str(BAND_ASOF)),
          (5, 3, 10, 10, 25, 50, -21, 7, "2026-11-27"))
    # the band of record
    first, last = D_("2024-10-14"), D_("2025-12-12")
    spec_s, warn = synth_spec(first, last)
    tape = fx_tape(spec_s, first, last, warn)
    with asof_patch(D_("2025-09-26")):
        w = compute_all(tape)
        rows, warns = band_rows(w, None)
        ck.eq("a tape covering asof writes of_record and recomputed for each pair, equal", ([r[1] for r in rows], warns),
              (["of_record", "recomputed"] * 3, []))
        ck.ok("...with the same statistics", all(rows[i][4:] == rows[i + 1][4:] for i in range(0, 6, 2)))
        text = render_csv("band.csv", rows)
        prev = text.replace(rows[0][6], "-99.000", 1)
        rows2, warns2 = band_rows(w, prev)
        ck.eq("the band of record is copied unchanged from the committed file", rows2[0][6], "-99.000")
        ck.ok("...the recomputed row stays fresh, and the difference is a WARN with both rows kept", rows2[1][6] == rows[1][6] and len(warns2) == 1, str(warns2))
        w2 = compute_all(tape.truncate(D_("2025-08-29")))
        rows3, _ = band_rows(w2, None)
        ck.eq("before asof is covered, one provisional row per pair", [r[1] for r in rows3], ["provisional"] * 3)


def t_g9(ck):
    ck.eq("the canonical allowlist text is the spec author's text", allow_text(), SPEC_ALLOW_TEXT)
    ck.eq("SPEC_ALLOW_SHA256 is the sha256 of that text", hashlib.sha256(allow_text().encode()).hexdigest(), spec_sha())
    blk, printed = spec_block(read_spec())
    ck.eq("the spec's fenced block is the canonical text, and its printed hash is the pinned one", (blk, printed), (allow_text(), spec_sha()))
    names = [l.split("\t") for l in columns_tsv().splitlines() if not l.startswith("#")]
    ck.eq("columns.tsv holds the allowlist, columns joined by |", {n: c.split("|") for n, c in names[1:]}, {n: allow_cols(n) for n in ALLOW_ORDER})
    for name in ("anchors.csv", "band.csv", "checks.csv"):
        text = render_csv(name, [])
        h, _ = parse_csv_text(text)
        ck.eq("the header of %s is the first line not starting with #" % name, h, allow_cols(name))
    ck.ok("post_in_zone_days follows pre_in_zone_days (round 4)", "pre_in_zone_days,post_in_zone_days" in allow_text())


def t_g10(ck):
    ck.eq("the required sentence passes verbatim", wording_problems("README.md", REQUIRED), [])
    ck.eq("'Neither identifies the counterparties or the reason.' passes verbatim", wording_problems("README.md", NEITHER), [])
    ck.eq("the README opening passes", wording_problems("README.md", OPENING), [])
    ck.ok("the required sentence plus 'Prices widened because banks window-dressed.' fails",
          bool(wording_problems("README.md", REQUIRED + " Prices widened because banks window-dressed.")))
    ck.ok("a note 'Japanese banks borrowed dollars' fails", bool(wording_problems("questions.csv note", "Japanese banks borrowed dollars")))
    ck.ok("a 'pushed' fails, even beside the required sentence", bool(wording_problems("SOURCES.md", REQUIRED + " Rates pushed higher.")))
    for w in ("caused", "causing", "drove", "driven", "leaned against", "because", "due to", "in response to", "led to", "prompted", "pushed",
              "as a result of", "reflects", "reflected", "amid", "owing to", "on the back of", "window-dressed", "borrowed", "borrowing by",
              "demand for dollars", "hedging demand"):
        ck.ok("'%s' is found beside the required sentence" % w, bool(wording_problems("README.md", REQUIRED + " Prices widened " + w + " year-end.")))
    cited = 'CGFS 65 p 35: the paper says spill-over was driven by repo.'
    ck.eq("a SOURCES.md line with a page-cited CGFS reference is exempt", wording_problems("SOURCES.md", cited), [])
    ck.ok("...and the same line is not exempt in the README", bool(wording_problems("README.md", cited)))


def t_g11(ck):
    with open(os.path.abspath(__file__), encoding="utf-8") as f:
        src = f.read()
    ck.eq("this source imports no network module and names neither the ledger's cache nor its latch", offline_problems(src), [])
    ck.ok("an inserted 'import urllib.request' is found", bool(offline_problems(src + "\nimport " + "urllib.request\n")))
    ck.ok("an inserted 'import socket' is found", bool(offline_problems(src + "\nimport " + "socket\n")))
    ck.ok("an inserted 'from http import client' is found", bool(offline_problems(src + "\nfrom " + "http import client\n")))
    ck.ok("a path naming the ledger's cache is found", bool(offline_problems(src + "\nP = '~/" + "dtcc" + "_ppd/x'\n")))
    ck.ok("a path naming its latch is found", bool(offline_problems(src + "\nP = '/ST" + "OP'\n")))


# ---- G12: the leak guard M22 of bin/check.sh, run on planted copies of a clean folder ------------------------------------------------------
def m22_source():
    with open(CHECK_SH, encoding="utf-8") as f:
        sh = f.read()
    m = re.search(r"^qeb_leak_check\(\) \{.*?^\}\n", sh, re.S | re.M)
    body = m.group(0)
    py = body[body.index("<<'PY'") + len("<<'PY'"):body.index("\nPY\n")].lstrip("\n")
    return py.replace(" || true", "")


def m22_mutate(py):
    for name, line in (("m22_r1_off", "bad += r1()"), ("m22_r2_off", "bad += r2()"), ("m22_r3_off", "bad += r3()"), ("m22_r4a_off", "bad += r4a()"),
                       ("m22_r4b_off", "bad += r4b()"), ("m22_r5a_off", "bad += r5a()"), ("m22_r5t_off", "bad += r5t()"), ("m22_r5q_off", "bad += r5q()"),
                       ("m22_r6a_off", "bad += r6a()"), ("m22_r6b_off", "bad += r6b()")):
        if M(name):
            if line not in py:
                raise DataError("M22 has no line %r" % line)
            py = py.replace(line, "bad += []")
    return py


def run_m22(py, d, spec):
    old = sys.argv
    buf = io.StringIO()
    try:
        sys.argv = ["m22", d, spec]
        with contextlib.redirect_stdout(buf):
            exec(compile(py, "m22", "exec"), {"__name__": "m22"})
    finally:
        sys.argv = old
    return buf.getvalue()


def plant(files, name, fn):
    f = dict(files)
    f[name] = fn(f[name])
    return f


def csv_edit(text, fn):
    lines = text.splitlines()
    i = next(n for n, l in enumerate(lines) if not l.startswith("#"))
    h = next(csv.reader([lines[i]]))
    rows = [next(csv.reader([l])) for l in lines[i + 1:] if l]
    fn(h, rows)
    return csv_text(lines[0], h, rows) if lines[0].startswith("#") else None


def t_g12(ck):
    files = world_files()
    spec = SPEC_DEFAULT
    py = m22_mutate(m22_source())

    def case(label, f, tag, extra=None):
        with tempfile.TemporaryDirectory() as tmp:
            for n, t in f.items():
                with open(os.path.join(tmp, n), "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(t)
            for n, t in (extra or {}).items():
                with open(os.path.join(tmp, n), "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(t)
            out = run_m22(py, tmp, spec)
        if tag is None:
            ck.ok("clean folder: M22 prints OK", out.strip() == "OK", out[:300])
        else:
            ck.ok("%s: M22 prints a [%s] line" % (label, tag), "[%s]" % tag in out, out[:200])

    def setcell(col, val, pred):
        def fn(h, rows):
            for r in rows:
                if pred(dict(zip(h, r))):
                    r[h.index(col)] = val
                    return
            raise DataError("no row to plant in")
        return fn

    case("the clean folder", files, None)
    case("(a) a planted CFTC_CUMULATIVE_RATES_2026_10_14.csv", files, 3, {"CFTC_CUMULATIVE_RATES_2026_10_14.csv": "x\n"})
    case("(b) a Dissemination Identifier header", plant(files, "inputs.csv", lambda t: t.replace("file,sha256", "Dissemination Identifier,sha256", 1)), 3)
    case("(c) a 12-digit cell", plant(files, "inputs.csv", lambda t: csv_edit(t, setcell("rows", "123456789012", lambda r: True))), 4)
    case("(d) a /Users/ path", plant(files, "SOURCES.md", lambda t: t + "\nsee /Users/x/y\n"), 4)
    case("(e) an extra file", files, 1, {"scratch.csv": "a,b\n"})
    case("(f1) a low_n row carrying d_bp in anchors.csv", plant(files, "anchors.csv", lambda t: csv_edit(
        t, setcell("d_bp", "1.000", lambda r: r["status"] in ("low_n", "gap", "incomplete")))), 5)
    case("(f2) a thin row carrying d_bp in anchors_tenor.csv", plant(files, "anchors_tenor.csv", lambda t: csv_edit(
        t, setcell("d_bp", "1.000", lambda r: r["status"] != "complete"))), 5)

    ah, arows = parse_csv_text(files["anchors.csv"])
    bad_anchor = next(dict(zip(ah, r)) for r in arows if r[ah.index("status")] != "complete")

    def plant_q(h, rows):
        rows.append(["Q1", bad_anchor["pair"], bad_anchor["anchor_type"], bad_anchor["anchor_date"], "d_bp", "1.000", "bp", "x", REQUIRED])
    case("(f3) a row of questions.csv with D for a non-complete anchor", plant(files, "questions.csv", lambda t: csv_edit(t, plant_q)), 5)
    case("(g) a README line 'because banks window-dressed'", plant(files, "README.md", lambda t: t + "\nPrices moved because banks window-dressed.\n"), 6)
    case("(h) a README line 'the 2026 year-end SUPPORTS a widening'", plant(files, "README.md", lambda t: t + "\nThe 2026 year-end SUPPORTS a widening.\n"), 6)
    case("(i) an extra column in a header", plant(files, "band.csv", lambda t: t.replace("sd_bp", "sd_bp,extra", 1)), 2)
    case("(j) a differing columns.tsv", plant(files, "columns.tsv", lambda t: t.replace("|status", "|state", 1)), 2)
    case("(k) a note with a causal word", plant(files, "questions.csv", lambda t: csv_edit(t, setcell("note", "Rates pushed higher.", lambda r: True))), 6)
    bad_spec = read_spec().replace("post_in_zone_days,n_window", "n_window", 1)
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as tmp2:
        for n, t in files.items():
            with open(os.path.join(tmp, n), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(t)
        sp = os.path.join(tmp2, "spec_copy.md")
        with open(sp, "w", encoding="utf-8") as fh:
            fh.write(bad_spec)
        out = run_m22(py, tmp, sp)
    ck.ok("(l) a spec whose allowlist block no longer hashes to the pin: M22 prints a [2] line", "[2]" in out, out[:200])
    if not _ACTIVE:
        # the real shell function, once, on the clean folder and on a copy with an extra file
        with open(CHECK_SH, encoding="utf-8") as f:
            sh = f.read()
        fn = re.search(r"^qeb_leak_check\(\) \{.*?^\}\n", sh, re.S | re.M).group(0)
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as tmp2:
            for n, t in files.items():
                with open(os.path.join(tmp, n), "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(t)
            fp = os.path.join(tmp2, "fn.sh")
            with open(fp, "w", encoding="utf-8") as fh:
                fh.write(fn)
            env = dict(os.environ, QEB_DIR=tmp, QEB_SPEC=SPEC_DEFAULT)
            run = lambda: subprocess.run(["bash", "-c", 'source "%s"; qeb_leak_check' % fp], env=env, capture_output=True, text=True).stdout
            out = run()
            ck.ok("the shell function prints a check mark on the clean folder", "  \u2713 only the ten committed names" in out, out[-300:])
            with open(os.path.join(tmp, "scratch.csv"), "w") as fh:
                fh.write("a\n")
            out = run()
            ck.ok("...and a cross on the folder with an extra file", "  \u2717 [1] file that is not one of the ten committed names: scratch.csv" in out, out[-300:])


def t_g13(ck):
    spec, warn = {p: {} for p in PAIR_NAMES}, None
    d = D_("2025-03-03")
    spec["JPYUSD"][d] = Dy(n=20, med="-30.000")
    tape = fx_tape(spec, d, d + dt.timedelta(days=7))
    ck.eq("a ledger file with a # source line loads: the header is the first line not starting with #", (tape.first, tape.last), (d, d + dt.timedelta(days=7)))
    texts = fx_texts(spec, d, d + dt.timedelta(days=7))
    bad = texts["cells_2025.csv"].decode().replace(",status\n", ",status,extra\n", 1).encode()
    try:
        load_tape(dict(texts, **{"cells_2025.csv": bad}))
        ck.ok("a cells file with an extra column is refused", False, "loaded")
    except DataError:
        ck.ok("a cells file with an extra column is refused", True)
    extra = ["%s,xccy_jpyusd,pool1to5,fullday,bp,25,-99.000,,,,,,,ok" % d]
    t2 = fx_tape(spec, d, d + dt.timedelta(days=7), extra_cells=extra)
    ck.eq("a non-headline variant is not read (the headline median stands)", t2.days["JPYUSD"][d].med, Decimal("-30.000"))
    sp2 = {p: {} for p in PAIR_NAMES}
    sp2["EURUSD"][d] = Dy(n=20, med="-3.000", tn=[1, 2, 3, 4, 9])
    sp2["EURUSD"][d + ONE] = Dy(n=20, med="-3.000", tn=[1, 2, 3, 4, 10])
    t3 = fx_tape(sp2, d, d + dt.timedelta(days=7))
    ok, tot = identity_counts(t3)
    ck.eq("pool n not equal to the sum of tenor n is counted (1 of 2 pair-days)", (ok, tot), (1, 2))
    ck.ok("the other series in the cells files are skipped", "sofr_ois" not in str(t3.days))


def t_g14(ck):
    first, last = D_("2024-10-14"), D_("2025-06-30")
    spec, warn = synth_spec(first, last, seed=3)
    tape = fx_tape(spec, first, last, warn)
    c10 = ("identical", "not run", "INFO")
    f1, _, _ = render_texts(tape, None, "", c10, lambda: dt.date(2030, 1, 1))
    f2, _, _ = render_texts(tape, None, "", c10, lambda: dt.date(2041, 7, 9))
    ck.eq("the same inputs give the same bytes under two different wall clocks passed to the build", {n: sha256_of(t.encode()) for n, t in f1.items()},
          {n: sha256_of(t.encode()) for n, t in f2.items()})
    with fake_clock(D_("2031-03-03")):
        g1, _, _ = render_texts(tape, None, "", c10, lambda: dt.date(2030, 1, 1))
    with fake_clock(D_("2044-11-11")):
        g2, _, _ = render_texts(tape, None, "", c10, lambda: dt.date(2030, 1, 1))
    ck.eq("...and with date.today, datetime.now, utcnow and time.time replaced for every caller (a rogue clock read changes the bytes)",
          {n: sha256_of(t.encode()) for n, t in g1.items()}, {n: sha256_of(t.encode()) for n, t in g2.items()})
    ck.ok("...and the faked and the real clocks give the same bytes", g1 == f1)
    if not _ACTIVE:
        files, _, _ = build_folder(tape, None, "", lambda: dt.date(2030, 1, 1))
        c10r = next(r for r in parse_csv_text(files["checks.csv"])[1] if r[0] == "C10")
        ck.eq("the build's own second render leaves every sha256 unchanged (C10)", c10r[4], "PASS")
    f3, _, _ = render_texts(tape, f1["band.csv"], "", c10, lambda: dt.date(2030, 1, 1))
    ck.ok("a rebuild with the committed band.csv in place changes nothing", f1 == f3)


def t_g15(ck):
    files = world_files()
    ck.eq("the clean folder has no verdict, causal or descriptive-wording problem", all_wording_problems(files) + descriptive_problems(files), [])
    for w in ("SUPPORTS", "AGAINST", "INCONCLUSIVE", "PENDING", "statistically significant", "significance", "p-value", "reject the null"):
        f = plant(files, "README.md", lambda t: t + "\nThe result %s.\n" % w)
        ck.ok("'%s' in committed text is found" % w, bool(all_wording_problems(f)))
    f = plant(files, "README.md", lambda t: t + "\nThe basis moved against the dollar.\n")
    ck.eq("lowercase 'against' is not a verdict word", all_wording_problems(f), [])
    ah, arows = parse_csv_text(files["anchors.csv"])
    comp = next(r for r in arows if r[ah.index("status")] == "complete" and r[ah.index("anchor_type")] == "quarter_end" and r[ah.index("mix_flag")] == "no")
    key = (comp[0], comp[1])

    def set_anchor(col, val):
        def fn(h, rows):
            for r in rows:
                if (r[0], r[1]) == key and r[2] == "quarter_end":
                    r[h.index(col)] = val
        return lambda t: csv_edit(t, fn)

    f = plant(files, "anchors.csv", set_anchor("mix_flag", "yes"))
    ck.ok("a mix_flag = yes row whose text lacks 'tenor mix shifted; not read as a basis move' is found", bool(descriptive_problems(f)))
    f = plant(files, "anchors.csv", set_anchor("gap_days", "3"))
    ck.ok("gap_days > 0 on a row described as on_date is found", bool(descriptive_problems(f)))

    def at_qe(h, rows):
        for r in rows:
            if (r[1], r[3]) == key and r[h.index("statistic")] == "window_position":
                r[h.index("value")] = "at the quarter-end"
    f = plant(plant(files, "anchors.csv", set_anchor("gap_days", "3")), "questions.csv", lambda t: csv_edit(t, at_qe))
    ck.ok("a row with gap_days > 0 described as 'at the quarter-end' is found", any("window position" in p for p in descriptive_problems(f)))

    def no_caveat(h, rows):
        for r in rows:
            if r[h.index("statistic")] == "rank_band":
                r[h.index("note")] = REQUIRED
    ck.ok("a rank printed without its caveat is found", bool(descriptive_problems(plant(files, "questions.csv", lambda t: csv_edit(t, no_caveat)))))
    ck.ok("a README rank cell without its caveat is found", bool(descriptive_problems(plant(files, "README.md", lambda t: BAND_RX.sub("x", t)))))
    bh, brows = parse_csv_text(files["band.csv"])
    gbp = next(dict(zip(bh, r)) for r in brows if r[0] == "GBPUSD")
    jpy = next(dict(zip(bh, r)) for r in brows if r[0] == "JPYUSD")
    ck.ok("the dependence caveat carries each pair's own count (README and notes)", ("from %s stretches; not independent" % gbp["stretches"]) in files["README.md"]
          and ("from %s stretches; not independent" % jpy["stretches"]) in files["README.md"] and "about eight" not in files["README.md"])
    ck.eq("the caveat text names the stretch count and the reference count", (band_caveat(5), ref_caveat(5)),
          ("overlapping windows from 5 stretches; not independent draws", "one window per stretch; 5 values"))
    swap = lambda t: t.replace("from %s stretches" % gbp["stretches"], "from 9 stretches")
    ck.ok("a caveat with another pair's count is found", bool(descriptive_problems(plant(files, "README.md", swap))))
    ck.ok("a caveat that says 'about eight' is found", bool(descriptive_problems(plant(files, "README.md", lambda t: BAND_RX.sub("overlapping windows from about eight stretches; not independent draws", t)))))
    ck.ok("a binomial probability printed is found", bool(descriptive_problems(plant(files, "README.md", lambda t: t + "\nBinomial probability 0.03.\n"))))


def t_g16(ck):
    world_small()
    tape = _CACHE["tape"]
    P = PairData(tape, "JPYUSD")
    items = band_items(P, tape.last)
    ref = pick_reference(items)
    by = {}
    for r in sorted(items, key=lambda x: x.date):
        by.setdefault(r.stretch, []).append(r)
    ck.eq("the reference set is the band anchor at position ceil(m/2) in each stretch", [r.date for r in ref], [by[s][(len(by[s]) + 1) // 2 - 1].date for s in sorted(by)])
    ck.eq("one reference anchor per stretch", len({r.stretch for r in ref}), len(ref))
    spans = sorted((r.pre[0].date, r.post[-1].date) for r in ref)
    ck.ok("reference windows never overlap", all(spans[i][1] < spans[i + 1][0] for i in range(len(spans) - 1)))
    ck.eq("rank counts values <= D, over k", (rank_le([Decimal(x) for x in (1, 2, 2, 3)], Decimal(2)), rank_denominator([1, 2, 2, 3])), (3, 4))
    # tenor cells: tenor 5 published every day; tenor 3 on 3 days of each control and 2 window days; tenor 2 on one window day only; tenor 1 never
    spec = {p: {} for p in PAIR_NAMES}
    wd = weekdays(D_("2025-02-03"), D_("2025-06-30"))[:70]
    for i, d in enumerate(wd):
        tm = [""] * 5
        tm[4] = fmt3(Decimal(-20) - Decimal("0.5") * i)
        if i in (33, 34, 20, 21, 22, 43, 44, 45):
            tm[2] = fmt3(Decimal(-25) + i)
        if i in (34, 20, 21, 22, 43, 44, 45):
            tm[3] = fmt3(Decimal(-22) + i)
        if i in (33, 34, 20, 21, 43, 44, 45):
            tm[0] = fmt3(Decimal(-18) + i)
        spec["JPYUSD"][d] = Dy(n=30, med="-30.000", tn=[3, 3, 3, 3, 18], tmed=tm)
    tp = fx_tape(spec, wd[0], wd[-1])
    P2 = PairData(tp, "JPYUSD")
    r = evaluate(P2, P2.dates[35], "quarter_end")
    if not need_complete(ck, r):
        return
    cells = {t: tenor_cell(r, t) for t in TENORS}
    ck.eq("a tenor never published is too_few_days, values blank (never read as 0, never the pooled median)", (cells[2]["status"], cells[2]["days_window"]), ("too_few_days", 0))
    ck.eq("a tenor with 2 window days, 2 pre-control days and 3 post-control days is too_few_days: each control needs 3", (cells[1]["status"], cells[1]["days_pre"], cells[1]["days_post"]),
          ("too_few_days", 2, 3))
    ck.eq("a tenor with 1 window day and 3 in each control is too_few_days: complete needs 2 window days", (cells[4]["status"], cells[4]["days_window"]),
          ("too_few_days", 1))
    ck.eq("a tenor with 2 window days and 3 in each control is complete", (cells[3]["status"], cells[3]["days_window"], cells[3]["days_pre"], cells[3]["days_post"]),
          ("complete", 2, 3, 3))
    ck.eq("a tenor published every day uses only its own medians", cells[5]["d"], Decimal(0))
    ck.eq("a tenor of an anchor that is not complete is anchor_not_complete", tenor_cell(evaluate(P2, P2.dates[5], "quarter_end"), 5)["status"], "anchor_not_complete")


def t_g17(ck):
    tape, wd, P = fx_run()
    r = evaluate(P, D_("2025-03-31"), "quarter_end")
    ck.eq("zone counts at 2025-03-31: pre-control 6 to 19 Mar has 8 days in [10 Mar, 7 Apr]; post-control 4 to 17 Apr has 2", (r.pre_zone, r.post_zone), (8, 2))
    ck.eq("in_sample: 2026-09-30 and 2024-12-31 yes, 2026-10-01 no", [in_sample(D_(x)) for x in ("2026-09-30", "2024-12-31", "2026-10-01")], [True, True, False])
    a = D_("2025-04-10")
    warns = {a - dt.timedelta(days=10), a - dt.timedelta(days=9), a, a + ONE}
    ck.eq("Q4 warn_f0_low window: the 10 calendar days ending on the anchor (a-9 to a), not a-10 or a+1", warn_days(warns, a), 2)


def t_g18(ck):
    ck.eq("count at or below a bound includes the bound", (count_le([Decimal(x) for x in (1, 2, 3)], Decimal(2)), count_le([Decimal(1)], Decimal(0))), (2, 0))
    ck.eq("the standard deviation is the population one (n, not n - 1)", pop_sd([Decimal(x) for x in (1, 2, 3, 4)]), Decimal("1.25").sqrt())
    mk = lambda g, t="quarter_end": R(gap_days=g, type=t)
    ck.eq("README position text: gap 0 is on_date, gap 1 is '1 day', gap 2 is '2 days'", [pos_text(mk(0)), pos_text(mk(1)), pos_text(mk(2))],
          ["on_date", "a window ending 1 day before the quarter-end", "a window ending 2 days before the quarter-end"])
    ck.eq("...and for a month-end", pos_text(mk(1, "month_end")), "a window ending 1 day before the month-end")
    files = world_files()
    ah, arows = parse_csv_text(files["anchors.csv"])
    row = next(r for r in arows if r[ah.index("status")] == "complete" and r[ah.index("anchor_type")] == "quarter_end" and r[ah.index("on_date")] == "yes")
    key = (row[0], row[1])

    def gap1(h, rows):
        for r in rows:
            if (r[0], r[1]) == key and r[2] == "quarter_end":
                r[h.index("gap_days")] = "1"
                r[h.index("on_date")] = "no"
    f = plant(files, "anchors.csv", lambda t: csv_edit(t, gap1))
    ck.ok("an anchor with gap_days 1 whose README row still says on_date is found", any("README.md" in p for p in descriptive_problems(f)))
    plural = lambda t: re.sub(r"(\| %s \| %s \|[^\n]*?\| )on_date" % (key[0], key[1]), r"\1a window ending 1 days before the quarter-end", t, count=1)
    f2 = plant(f, "README.md", plural)
    ck.ok("...and '1 days' is not the singular", any("README.md" in p and "position" in p for p in descriptive_problems(f2)))


def t_x_build(ck):
    files = world_files()
    ck.eq("ten files", sorted(files), sorted(COMMITTED))
    ck.ok("every csv opens with one # source: line and the header is the allowlist", all(
        files[n].startswith("# source:") and parse_csv_text(files[n])[0] == allow_cols(n) for n in ALLOW_ORDER if n.endswith(".csv")))
    rd = files["README.md"]
    ck.ok("the README opens with the title, the opening paragraph and the required sentence", OPENING in rd and rd.index(OPENING) < rd.index(REQUIRED))
    ck.ok("the build decisions are a section of SOURCES.md and not of the README", "## Build decisions" in files["SOURCES.md"] and "Build decisions" not in rd)
    ck.ok("every note carries the required sentence", all(r[-1].startswith(REQUIRED) for r in parse_csv_text(files["questions.csv"])[1]))
    ck.ok("the README says negative means dollars cost more", "negative means dollars cost more" in rd)
    ck.ok("the new hash is recorded in SOURCES.md", SPEC_ALLOW_SHA256 in files["SOURCES.md"])
    ck.ok("band.csv holds provisional rows only (the synthetic tape ends before 2026-11-27)", {r[1] for r in parse_csv_text(files["band.csv"])[1]} == {"provisional"})
    ck.ok("no thin row carries a value", not [1 for r in parse_csv_text(files["anchors.csv"])[1] if r[6] != "complete" and r[21] != ""])
    ck.ok("post_in_zone_days is a column of anchors.csv", "post_in_zone_days" in parse_csv_text(files["anchors.csv"])[0])


GUARDS = [
    ("G1", "liquid days (3.1, 2.3)", ["warn_liquid", "blank_as_zero", "thin_dropped", "hole_liquid", "hole_uncovered"], t_g1),
    ("G2", "window and controls (3.3)", ["window4", "window6", "buffers0", "controls9", "ctrl_weekdays", "window_holds_post", "wrap_negative"], t_g2),
    ("G3", "tolerance and on_date (3.3)", ["gap_ge", "gap_11_ok", "post_unchecked", "on_date_le1"], t_g3),
    ("G4", "the difference D (3.4, R6)", ["pre_only", "mean_not_median", "median_first_of_even", "py_round", "float_math"], t_g4),
    ("G5", "sign (2.4)", ["sign_flip", "sign_check_inverted"], t_g5),
    ("G6", "band (3.5)", ["interpolate", "zone_kept", "zone_swapped", "dup_kept", "qe_me_in_band", "asof_ignored", "loso_one_anchor"], t_g6),
    ("G7", "status and mix (3.6, 3.7)", ["low_n_first", "floor_window_only", "count_days", "signed_mix", "mix_p90"], t_g7),
    ("G8", "frozen design and band of record (R7, R8)", ["design_const", "design_text_drift", "of_record_rewritten", "diff_not_warned"], t_g8),
    ("G9", "allowlists (R4)", ["extra_column", "renamed_column", "sha_drift", "columns_drift", "source_as_header"], t_g9),
    ("G10", "causal wording (R5)", ["required_not_exempt", "exempt_whole_line", "borrowed_exempt", "pushed_missing", "because_missing", "cgfs_exempt_all"], t_g10),
    ("G11", "offline and latches (R1, R2)", ["scan_net_off", "scan_path_off"], t_g11),
    ("G12", "the commit folder, M22 on planted copies (section 7)", ["m22_r1_off", "m22_r2_off", "m22_r3_off", "m22_r4a_off", "m22_r4b_off", "m22_r5a_off",
                                                                    "m22_r5t_off", "m22_r5q_off", "m22_r6a_off", "m22_r6b_off"], t_g12),
    ("G13", "inputs (2.2)", ["header_from_hash", "header_unchecked", "identity_off", "any_variant"], t_g13),
    ("G14", "rebuild and clock (R9)", ["clock_in_output", "rebuild_drift", "tape_last_from_clock"], t_g14),
    ("G15", "descriptive wording (R3-1, R3-3, R3-4)", ["verdict_supports_missing", "verdict_significance_missing", "mix_text_off", "gap_text_off", "caveat_off",
                                                       "caveat_fixed_eight", "caveat_count_off", "binomial_off"], t_g15),
    ("G16", "reference set and tenors (3.5, 3.6)", ["ref_all", "ref_first", "ref_two", "tenor_pooled", "tenor_blank_zero", "tenor_min1", "tenor_ctrl2", "rank_lt",
                                                    "rank_k_plus_1"], t_g16),
    ("G17", "zone counts, the in-sample end and the Q4 warn window (3.3, 5)", ["post_zone_zero", "insample_lt", "warn_win11"], t_g17),
    ("G18", "counts at or below a bound, the standard deviation, README position text (3.5, 5, R3-4)", ["count_lt", "sd_sample", "pos_on_date_le1"], t_g18),
    ("X1", "an end-to-end synthetic build", [], t_x_build),
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
    world_small()                                  # built first, with no mutant active
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
        print("selftest with mutant %s: %d failing check(s) -> %s" % (only, bad_total, "the selftest FAILS (mutant caught)" if bad_total else
                                                                    "the selftest PASSES (mutant NOT caught)"))
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
                print("       mutant %-28s %s%s" % (m, "FAIL (caught)" if caught else "PASSED -- NOT CAUGHT", "  <- %s" % mk.failed()[0][0][:70] if caught else ""))
    print("selftest: %d guards, %d checks, %d mutants applied one at a time, %d failure(s), %.1f s" % (len(GUARDS), n_checks, n_mut, bad_total, time.time() - t0))
    return 0 if bad_total == 0 else 1


# ==== COMMAND LINE ====
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pb = sub.add_parser("build", help="offline: read the ledger's derived files and write the ten outputs")
    pb.add_argument("--tape", default=TAPE_DEFAULT)
    pb.add_argument("--out", default=OUT_DEFAULT)
    pb.add_argument("--calendar", default=CALENDAR_DEFAULT)
    ps = sub.add_parser("selftest", help="synthetic data, mutants applied one at a time")
    ps.add_argument("--no-mutants", action="store_true")
    ps.add_argument("--mutant", help="run the guards with this one mutant switched on; exit 1 (the selftest fails) when it is caught")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "selftest":
            return selftest(mutants=not a.no_mutants, only=a.mutant)
        return run_build(a)
    except DataError as e:
        print("refused (data): %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
