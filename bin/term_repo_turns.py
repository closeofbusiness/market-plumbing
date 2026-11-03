#!/usr/bin/env python3
"""On the last business day before a month-end, how far above the overnight rate is the tri-party 2-7 day rate, against ordinary days of the same month?
Office of Financial Research tri-party repo rates, excluding Federal Reserve trades, preliminary vintage. Python 3 standard library only.

  python3 bin/term_repo_turns.py fetch [--vintage YYYYMMDD] [--replace] [--cache DIR] [--sleep S]                    # network; supervisor only; nine GETs to data.financialresearch.gov
  python3 bin/term_repo_turns.py build --vintage YYYYMMDD --stage pre [--cache DIR]                                   # offline; layout, coverage, decimals; prints no rate and no spread
  python3 bin/term_repo_turns.py build --vintage YYYYMMDD --stage dry [--cache DIR] [--fomc-page FILE]                # offline; the rule engine over the real dates with every value hidden
  python3 bin/term_repo_turns.py build --vintage YYYYMMDD --stage describe [--vs YYYYMMDD] [--cache DIR] [--out DIR] # offline; writes everything but registered.csv
  python3 bin/term_repo_turns.py build --vintage YYYYMMDD --stage register [--cache DIR] [--out DIR]                  # offline; on or after the gate; writes registered.csv once
  python3 bin/term_repo_turns.py selftest [--no-mutants] [--mutant NAME]                                              # synthetic data only; no network

Specification: _research/2026-11-02-Term-Repo-Turns-Spec.md (committed at 2b54781, with the supervisor's rulings of rounds 1 and 2; a ruling wins over the body).
Outputs: data/term_repo_turns/ (daily.csv, turns.csv, registered.csv, checks.csv, revisions.csv, README.md) and, per vintage, data/vintages/ofr_repo/<YYYYMMDD>/ (the raw JSON of
nine series and MANIFEST.csv: url, sha256, bytes, fetched_at; US government data, committed).

WHAT TOUCHES THE NETWORK. Only `fetch`, only data.financialresearch.gov, GET only, at least 3 seconds between request starts, no key, no cookie, no redirect followed, no retry,
Accept-Encoding identity, one fixed generic User-Agent with no name, address or contact. Any status other than 200, and any 200 body that is not a JSON list of [date, value] pairs
(a bot check page, say), writes STOP_term_repo in data/vintages/ofr_repo/ and ends the fetch with exit 2, printing which; with the file present no request is made. This script never
deletes, renames over or truncates a STOP file; only a person deletes one. Before the gate (2027-01-05T20:00Z) every request carries end_date no later than 2026-12-23 (today, while that is ahead) and a response holding a later
date is refused and not written. The machine clock must agree with the response's HTTP Date to within one hour.

EXIT CODES. 0 ok. 2 STOP written or present, or a data error. 3 network fault. 4 structural fault (a failing pinned check or a malformed series): nothing is registered. 5 refused: a
wrong argument, a clock fault, a cap breach, `register` before the gate or on a pre-gate vintage, a failed prereg hash, and the second write of registered.csv (O_EXCL, or an earlier
version in git history). 6 `register` found the target PENDING: nothing is written.

BLIND. `pre` prints counts, dates and decimals, never a rate, a spread or a volume. `dry` hides every value. Nobody reads turns.csv or daily.csv before the January vintage has been
registered; the target row of turns.csv is empty and PENDING until the gate.
"""
import argparse
import bisect
import contextlib
import csv
import datetime as dt
import email.utils
import hashlib
import http.client
import io
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
from fractions import Fraction
from decimal import Decimal
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    """A request, argument, clock or write this script will not honour (exit 5)."""


class Latched(Exception):
    """A STOP file was written (or already exists); the fetch ends (exit 2)."""


class SocketFault(Exception):
    """Timeout, reset or TLS error: the fetch ends with exit 3, without latching."""


class Structural(Exception):
    """A malformed series or a failing pinned check (exit 4): nothing is registered."""


class DataError(Exception):
    """A hard problem with an input or an output (exit 2)."""


# ------------------------------------------------------------------------------------------------------------------------
# constants
# ------------------------------------------------------------------------------------------------------------------------
SPEC_FILE = "_research/2026-11-02-Term-Repo-Turns-Spec.md"
SPEC_COMMIT = "2b54781"
HOST = "data.financialresearch.gov"
API_PATH = "/v1/series/timeseries"
USER_AGENT = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"          # the one neutral string CLAUDE.md fixes (bin/check.sh M10 enforces it): no person, address or contact
MIN_SLEEP = 3.0                  # spec 1.1: at least 3 seconds between request starts
DEFAULT_SLEEP = 3.05             # the 0.05 is a margin for clock granularity
TIMEOUT = 90
BODY_CAP = 8 * 1024 * 1024
ERR_CAP = 4096
SKEW_SECONDS = 3600              # spec 1.3: the machine clock against the response's Date
START_DATE = "2025-08-01"
END_CAP = "2026-12-23"           # spec 1.3: the end_date of every pre-gate request
STOP_NAME = "STOP_term_repo"
VROOT_REL = os.path.join("data", "vintages", "ofr_repo")
OUT_REL = os.path.join("data", "term_repo_turns")
REG_NAME = "registered.csv"

MN_B27, MN_OO, MN_TVB, MN_TVO, MN_B830 = "REPO-TRIV1_AR_B27-P", "REPO-TRIV1_AR_OO-P", "REPO-TRIV1_TV_B27-P", "REPO-TRIV1_TV_OO-P", "REPO-TRIV1_AR_B830-P"
PRELIM = (MN_B27, MN_OO, MN_TVB, MN_TVO, MN_B830)
FINALS = tuple(m[:-2] + "-F" for m in PRELIM[:4])
ALL_MN = PRELIM + FINALS
MIN_ROWS = {MN_B27: 302, MN_OO: 310, MN_TVB: 302, MN_TVO: 310, MN_B830: 302}          # spec 2.1 / 7: "at least those in 2.1"
FIRST_B27 = dt.date(2025, 8, 13)
FINALS_THROUGH = dt.date(2026, 6, 30)
TICK_BP = Fraction(1)            # metadata precision 2 on a percent rate: one published tick is 0.01 percent, one basis point

# the five passed quarter-ends and the three months left out of the registered comparison (spec 2.3, 4.3); the other dates come from the fence
QUARTER_T = ("2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30", "2026-09-30")
DESCRIBED_T = ("2025-08-29", "2026-04-30", "2026-11-30")

# United States federal holidays, 13 Aug 2025 to 4 Jan 2027 (observed dates), used only by `pre` to say which absent weekdays are not on this list. From the OPM schedule; UNCERTAIN until
# the supervisor has compared it with the published table.
FED_HOLIDAYS = ("2025-09-01", "2025-10-13", "2025-11-11", "2025-11-27", "2025-12-25", "2026-01-01", "2026-01-19", "2026-02-16", "2026-05-25", "2026-06-19", "2026-07-03",
                "2026-09-07", "2026-10-12", "2026-11-11", "2026-11-26", "2026-12-25", "2027-01-01")

# the registered block, byte for byte (the interior of the fence in spec 4.2), and its sha256 (the one hash)
PREREG_BLOCK = """DEF|S(t)=100*(REPO-TRIV1_AR_B27-P(t)-REPO-TRIV1_AR_OO-P(t))|unit=basis_points|arithmetic=exact_fractions_from_file_strings|even_median=mean_of_middle_two|business_day=date_present_and_non-null_in_both_series
CONTROL|K(T)=business_days_in_month_of_T_with_(T-t)>=7_calendar_days,no_FOMC_effective_date_in_(t,t+7_calendar_days],not_coupon,not_early_close|coupon=the_15th_or_else_the_next_date_after_it_that_is_a_business_day_as_defined_in_DEF
STAT|E(T)=S(T-1)-median(S_over_K(T))|needs_T-1_defined_and_at_least_5_K_days_else_NOT_ASSESSED
PLACEBO|T-1=2025-10-30,2025-11-26,2026-01-29,2026-02-26,2026-05-28,2026-07-30,2026-08-28,2026-10-29|T=2025-10-31,2025-11-28,2026-01-30,2026-02-27,2026-05-29,2026-07-31,2026-08-31,2026-10-30|needs_at_least_7_assessed_else_VOID
FOMC|effective=2025-09-18,2025-10-30,2025-12-11,2026-01-29,2026-03-19,2026-04-30,2026-06-18,2026-07-30,2026-09-17,2026-10-29,2026-12-10
EARLY|close=2025-11-28,2025-12-24,2026-04-03,2026-05-22,2026-07-02,2026-11-27,2026-12-24
TARGET|T=2026-12-31|T-1=2026-12-30|missing_or_null_T-1_is_PENDING_no_write_retry_next_business_day_until_2027-01-29_then_NOT_ASSESSED
LABEL|ABOVE_if_E>max(placebo)_and_E>0;BELOW_if_E<min(placebo)_and_E<0;INSIDE_otherwise;NOT_ASSESSED_or_VOID_as_above
VINTAGE|preliminary|first_fetch_on_or_after_2027-01-05T20:00Z_supplies_target_and_placebo|finals_recorded_later_never_rescored
USE|label_E_range_and_both_legs_go_on_the_page_in_the_fixed_sentence|never_called_a_charge_or_premium|no_comparison_with_reference_rates|n=1
"""
SPEC_PREREG_SHA256 = "0592b8ed2d566d87664abba83196b660cfba4662bd95018b46e379923c325e36"
SPEC_PREREG_BYTES = 1505
CHECKSH_COPIED = ("PREREG_SHA",)


# ------------------------------------------------------------------------------------------------------------------------
# small helpers
# ------------------------------------------------------------------------------------------------------------------------
def sha256_of(b):
    return hashlib.sha256(b).hexdigest()


def read_file(path, mode="rb"):
    with open(path, mode) as fh:
        return fh.read()


def D(s):
    return dt.date.fromisoformat(s)


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def iso_z(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_z(s):
    """'2027-01-05T20:00:00Z' or '2027-01-05T20:00Z' -> aware datetime."""
    s = s.strip()
    for f in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%MZ"):
        try:
            return dt.datetime.strptime(s, f).replace(tzinfo=dt.timezone.utc)
        except ValueError:
            pass
    raise ValueError("not a UTC time: %r" % s)


def write_text(path, text):
    """Atomic write via a temporary sibling. Refuses a STOP name and registered.csv (that file is written only by write_once)."""
    base = os.path.basename(path)
    if base.upper().startswith("STOP"):
        raise Refused("write_text never touches a STOP file")
    if base == REG_NAME:
        raise Refused("registered.csv is written only by the register stage, once")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


def write_bytes(path, data):
    if os.path.basename(path).upper().startswith("STOP"):
        raise Refused("write_bytes never touches a STOP file")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.replace(tmp, path)


def write_once(path, text):
    """registered.csv: created with O_EXCL, so a second write fails whatever happened before."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | (0 if M("excl_off") else os.O_EXCL) | (os.O_TRUNC if M("excl_off") else 0)
    try:
        fd = os.open(path, flags, 0o644)
    except FileExistsError:
        raise Refused("registered.csv already exists: a registered reading is written once and never re-scored (exit 5)")
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
        fh.flush()
        os.fsync(fh.fileno())


def csv_text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def read_csv_dicts(text):
    return list(csv.DictReader(io.StringIO(text)))


def fmt_fr(f, nd=2):
    """An exact Fraction to a fixed number of decimals, half-even, only here (rounding happens in print and nowhere else)."""
    if f is None:
        return ""
    n = round(Fraction(f) * 10 ** nd)
    sign = "-" if n < 0 else ""
    s = str(abs(n)).rjust(nd + 1, "0")
    return sign + (s[:-nd] + "." + s[-nd:] if nd else s)


def sgn(f, nd=2):
    s = fmt_fr(f, nd)
    return s if s.startswith("-") or float(s) == 0 else "+" + s


def vintage_ok(v):
    if not re.match(r"^\d{8}$", v or ""):
        return False
    try:
        dt.datetime.strptime(v, "%Y%m%d")
    except ValueError:
        return False
    return True


def vroot_of(root=None, cache=None):
    return cache or os.path.join(root or ROOT, VROOT_REL)


def out_of(root=None, out=None):
    return out or os.path.join(root or ROOT, OUT_REL)


# ------------------------------------------------------------------------------------------------------------------------
# the registered block: constants are parsed from it and never restated
# ------------------------------------------------------------------------------------------------------------------------
class Prereg(object):
    pass


def parse_prereg(text):
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    tags = {}
    for ln in lines:
        parts = ln.split("|")
        tags[parts[0]] = parts[1:]
    p = Prereg()
    p.text = text
    control = "|".join(tags["CONTROL"])
    p.k_min_days = int(re.search(r"\(T-t\)>=(\d+)_calendar_days", control).group(1))
    p.fomc_window = int(re.search(r"\(t,t\+(\d+)_calendar_days\]", control).group(1))
    p.coupon_dom = int(re.search(r"coupon=the_(\d+)(?:st|nd|rd|th)_", control).group(1))
    p.min_k = int(re.search(r"at_least_(\d+)_K_days", "|".join(tags["STAT"])).group(1))
    pl = tags["PLACEBO"]
    p.placebo_tm1 = tuple(D(x) for x in pl[0].split("=", 1)[1].split(","))
    p.placebo_t = tuple(D(x) for x in pl[1].split("=", 1)[1].split(","))
    p.min_placebo = int(re.search(r"at_least_(\d+)_assessed", pl[2]).group(1))
    p.fomc = tuple(D(x) for x in tags["FOMC"][0].split("=", 1)[1].split(","))
    p.early = tuple(D(x) for x in tags["EARLY"][0].split("=", 1)[1].split(","))
    tg = tags["TARGET"]
    p.target_t = D(tg[0].split("=", 1)[1])
    p.target_tm1 = D(tg[1].split("=", 1)[1])
    p.retry_until = D(re.search(r"until_(\d{4}-\d\d-\d\d)_then", tg[2]).group(1))
    p.gate = parse_z(re.search(r"on_or_after_(\d{4}-\d\d-\d\dT\d\d:\d\dZ)", "|".join(tags["VINTAGE"])).group(1))
    p.fence_tm1 = {t: m for t, m in zip(p.placebo_t, p.placebo_tm1)}
    p.fence_tm1[p.target_t] = p.target_tm1
    p.early_set = frozenset(p.early)
    return p


def prereg_ok(text=None):
    """The embedded block must hash to the constant; the register stage refuses otherwise."""
    if M("prereg_nocheck"):
        return True
    text = PREREG_BLOCK if text is None else text
    return sha256_of(text.encode("utf-8")) == SPEC_PREREG_SHA256


PR = parse_prereg(PREREG_BLOCK)


def all_turns(P=None):
    """[(date, kind)] sorted: five quarter-ends, eight placebo month-ends, three described months, the target."""
    P = P or PR
    items = [(D(t), "quarter") for t in QUARTER_T] + [(t, "placebo") for t in P.placebo_t] + [(D(t), "described") for t in DESCRIBED_T] + [(P.target_t, "target")]
    return sorted(items)


# ------------------------------------------------------------------------------------------------------------------------
# series and data
# ------------------------------------------------------------------------------------------------------------------------
DATE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _no_const(s):
    raise ValueError("non-finite constant " + s)


class Series(object):
    def __init__(self, name, pairs):
        self.name = name
        self.raw = {}
        self.val = {}
        for d, v in pairs:
            if d in self.raw:
                raise Structural("%s: date %s appears twice" % (name, d))
            self.raw[d] = v
            self.val[d] = None if v is None else _frac(name, d, v)
        self.dates = sorted(self.raw)


def _frac(name, d, v):
    try:
        if M("float_parse"):
            return Fraction(float(v))
        return Fraction(v)
    except (ValueError, ZeroDivisionError):
        raise Structural("%s: value on %s is not a number" % (name, d))


def parse_series(body, name):
    """A JSON list of [date, value] pairs; numbers are kept as their text (parse_float=str), so every value is exact."""
    try:
        text = body.decode("utf-8") if isinstance(body, (bytes, bytearray)) else body
        obj = json.loads(text, parse_float=str, parse_int=str, parse_constant=_no_const)
    except (ValueError, UnicodeDecodeError) as e:
        raise Structural("%s: not a JSON list of [date, value] pairs (%s)" % (name, str(e)[:60]))
    if not isinstance(obj, list):
        raise Structural("%s: not a JSON list" % name)
    pairs = []
    for it in obj:
        if not (isinstance(it, list) and len(it) == 2 and isinstance(it[0], str) and DATE_RX.match(it[0]) and (it[1] is None or isinstance(it[1], str))):
            raise Structural("%s: an item is not [date, value|null]" % name)
        try:
            D(it[0])
        except ValueError:
            raise Structural("%s: %r is not a date" % (name, it[0]))
        pairs.append((D(it[0]), it[1]))
    return Series(name, pairs)


class Data(object):
    """Business days are the dates present and non-null in both B27 and OO (spec 3)."""

    def __init__(self, b27, oo, tvb, tvo, b830=None):
        self.b27, self.oo, self.tvb, self.tvo = b27, oo, tvb, tvo
        self.b830 = b830 if b830 is not None else Series("none", [])
        if M("biz_union"):
            self.biz = sorted(set(b27.dates) | set(oo.dates))
        elif M("null_as_day"):
            self.biz = sorted(d for d in b27.dates if d in oo.val)
        else:
            self.biz = sorted(d for d in b27.dates if b27.val[d] is not None and oo.val.get(d) is not None)
        self.bizset = frozenset(self.biz)
        every = list(b27.dates) + list(oo.dates)
        self.last = max(every) if every else None

    def prev_oo(self, T):
        i = bisect.bisect_left(self.oo.dates, T)
        return self.oo.dates[i - 1] if i > 0 else None


def hidden(d):
    """The same dates and the same nulls with every value replaced by one: for `dry`, which must not be able to show a value."""
    def h(s):
        return Series(s.name, [(t, None if s.raw[t] is None else "1") for t in s.dates])
    return Data(h(d.b27), h(d.oo), h(d.tvb), h(d.tvo), h(d.b830))


# ------------------------------------------------------------------------------------------------------------------------
# the rule engine (spec 3)
# ------------------------------------------------------------------------------------------------------------------------
def median(xs):
    """Exact. An even count gives the mean of the middle two (the registered rule)."""
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        raise ValueError("median of nothing")
    if n % 2:
        return xs[n // 2]
    if M("median_lower"):
        return xs[n // 2 - 1]
    if M("float_median"):
        return (float(xs[n // 2 - 1]) + float(xs[n // 2])) / 2
    return (xs[n // 2 - 1] + xs[n // 2]) / Fraction(2)


def s_bp(d, t):
    return 100 * (d.b27.val[t] - d.oo.val[t])


def fomc_in_window(t, P):
    w = dt.timedelta(P.fomc_window + (1 if M("fomc_window_long") else 0) - (1 if M("fomc_window_short") else 0))
    for e in P.fomc:
        if M("fomc_left_closed"):
            if t <= e <= t + w:
                return True
        elif t < e <= t + w:
            return True
    return False


def coupon_day(d, year, month, P):
    """The 15th, or else the first date after it that is a business day in the data (DEF); None when the data has none."""
    start = dt.date(year, month, P.coupon_dom)
    if M("coupon_no_roll"):
        return start if start in d.bizset else None
    i = bisect.bisect_left(d.biz, start)
    return d.biz[i] if i < len(d.biz) else None


def k_days(T, d, P, restore_coupon=False, restore_early=False, fomc=True, max_dom=None):
    """K(T): business days in T's month with T-t at least 7 calendar days, no FOMC effective date in (t, t+7], not the coupon day, not an early close."""
    cp = coupon_day(d, T.year, T.month, P)
    out = []
    for t in d.biz:
        if (t.year, t.month) != (T.year, T.month) and not M("k_other_month"):
            continue
        gap = (T - t).days
        if (gap <= P.k_min_days) if M("k_edge_gt") else (gap < P.k_min_days):
            continue
        if fomc and fomc_in_window(t, P):
            continue
        if not restore_coupon and t == cp:
            continue
        if not restore_early and t in P.early_set and not M("early_kept"):
            continue
        if max_dom is not None and t.day > max_dom:
            continue
        out.append(t)
    return out


def new_row(T, kind):
    r = {k: None for k in TURN_FIELDS}
    r.update({"t": T, "kind": kind, "status": "PENDING", "why": ""})
    return r


def assess(T, kind, d, P, now):
    """One turn. PENDING when T-1 cannot yet be in the data; NOT_ASSESSED when it is missing, or fewer than 5 control days remain. Never computed on what is not there."""
    r = new_row(T, kind)
    is_target = kind == "target"
    over = is_target and now.date() > P.retry_until and not M("no_deadline")

    def pend(why):
        r["status"] = "NOT_ASSESSED" if over else "PENDING"
        r["why"] = why
        return r

    def na(why):
        r["status"] = "NOT_ASSESSED"
        r["why"] = why
        return r

    if is_target and now < P.gate and not M("target_leak"):
        r["t_minus_1"] = P.target_tm1
        r["why"] = "before the gate"
        return r
    last = d.last
    fence = P.fence_tm1.get(T)
    if fence is not None:
        r["t_minus_1"] = tm1 = fence
        if last is None or fence > last:
            return pend("T-1 is later than the last date in the data")
        if T in d.oo.val and d.prev_oo(T) != fence and tm1 in d.bizset:
            return na("the previous overnight date is not the fence's T-1")
        if tm1 not in d.bizset:
            return pend("T-1 is missing or null in a series") if is_target else na("T-1 is missing or null in a series")
    else:
        if last is None or T > last:
            return pend("T is later than the last date in the data")
        if T not in d.oo.val:
            return na("T is absent from the overnight series")
        tm1 = (T - dt.timedelta(1)) if M("tm1_calendar") else d.prev_oo(T)
        r["t_minus_1"] = tm1
        if tm1 is None or tm1 not in d.bizset:
            return na("T-1 is missing or null in a series")
    K = k_days(T, d, P)
    r["n_k"] = len(K)
    if len(K) < (4 if M("min_k_4") else P.min_k):
        return na("fewer than %d control days" % P.min_k)
    r["K"] = K
    ss = [s_bp(d, t) for t in K]
    cm = median(ss)
    s1 = s_bp(d, tm1)
    r["s_t1"], r["control_median"] = s1, cm
    r["e"] = s1 if M("e_no_control") else s1 - cm
    bm = median([d.b27.val[t] for t in K])
    om = median([d.oo.val[t] for t in K])
    r["db"] = 100 * (d.b27.val[tm1] - bm)
    r["do"] = 100 * (d.oo.val[tm1] - om)
    if d.oo.val.get(T) is not None:
        r["ot"] = 100 * (d.oo.val[T] - om)
    near = [t for t in d.biz if t < T and (T - t).days < P.k_min_days]
    if near:
        r["v1"] = sum((s_bp(d, t) for t in near), Fraction(0)) / len(near) - cm
    if T in d.bizset:
        r["v2"] = s_bp(d, T) - cm

    def alt(**kw):
        k2 = k_days(T, d, P, **kw)
        return s1 - median([s_bp(d, t) for t in k2]) if len(k2) >= P.min_k else None
    r["v3"] = alt(restore_coupon=True, restore_early=True)
    r["v4"] = alt(max_dom=14)
    r["v5"] = alt(fomc=False)
    k6 = [t for t in K if d.b830.val.get(t) is not None]
    if d.b830.val.get(tm1) is not None and len(k6) >= P.min_k:
        r["v6"] = 100 * (d.b830.val[tm1] - d.oo.val[tm1]) - median([100 * (d.b830.val[t] - d.oo.val[t]) for t in k6])
    for key, ser in (("b27", d.tvb), ("oo", d.tvo)):
        r["tv_%s_t1" % key] = ser.val.get(tm1)
        vs = [ser.val[t] for t in K if ser.val.get(t) is not None]
        r["tv_%s_k_mean" % key] = sum(vs, Fraction(0)) / len(vs) if vs else None
    r["status"] = "OK"
    return r


def label_of(status, e, pmin, pmax, n, P):
    """ABOVE if E > max(placebo) and E > 0; BELOW if E < min(placebo) and E < 0; INSIDE otherwise (spec 4.2 LABEL)."""
    if status == "PENDING":
        return "PENDING"
    if status != "OK":
        return "NOT_ASSESSED"
    if n < (6 if M("void_6") else P.min_placebo):
        return "VOID"
    if M("label_ge"):
        up, down = e >= pmax and e > 0, e <= pmin and e < 0
    elif M("label_no_sign"):
        up, down = e > pmax, e < pmin
    else:
        up, down = e > pmax and e > 0, e < pmin and e < 0
    return "ABOVE" if up else ("BELOW" if down else "INSIDE")


def placebo_range(rows):
    es = [r["e"] for r in rows if r["kind"] == "placebo" and r["status"] == "OK"]
    return (min(es), max(es), len(es)) if es else (None, None, 0)


def evaluate_all(d, P, now):
    rows = [assess(T, kind, d, P, now) for T, kind in all_turns(P)]
    pmin, pmax, n = placebo_range(rows)
    seven = [r["e"] for r in rows if r["kind"] in ("placebo", "described") and r["status"] == "OK"]
    for r in rows:
        if r["status"] != "OK":
            continue
        if seven:
            r["v7_min"], r["v7_max"], r["v7_n"] = min(seven), max(seven), len(seven)
        if r["kind"] in ("quarter", "target", "described") and n >= P.min_placebo:
            lab = label_of("OK", r["e"], pmin, pmax, n, P)
            moved = (label_of("OK", r["e"] + TICK_BP, pmin, pmax, n, P), label_of("OK", r["e"] - TICK_BP, pmin, pmax, n, P))
            r["tick_sensitive"] = "no" if M("tick_off") else ("yes" if any(x != lab for x in moved) else "no")
    return rows


def e_second_path(T, d, P):
    """E(T) by a second code path: Decimal text arithmetic over the raw strings, ordinals for the calendar, statistics.median. None when not assessable."""
    mine = lambda t: d.b27.raw.get(t) is not None and d.oo.raw.get(t) is not None
    days = sorted(t for t in set(d.b27.raw) & set(d.oo.raw) if mine(t))
    fence = P.fence_tm1.get(T)
    if fence is None:
        before = [t for t in sorted(d.oo.raw) if t < T]
        fence = before[-1] if before else None
    if fence is None or fence not in days:
        return None
    fo = set(e.toordinal() for e in P.fomc)
    cands = [t for t in days if t.year == T.year and t.month == T.month]
    cp = next((t for t in days if t.toordinal() >= dt.date(T.year, T.month, P.coupon_dom).toordinal()), None)
    keep = []
    for t in cands:
        if T.toordinal() - t.toordinal() < P.k_min_days:
            continue
        if any((t.toordinal() + k) in fo for k in range(1, P.fomc_window + 1)):
            continue
        if t == cp or t in P.early_set:
            continue
        keep.append(t)
    if len(keep) < P.min_k:
        return None
    spread = lambda t: Fraction(Decimal(d.b27.raw[t]) * 100 - Decimal(d.oo.raw[t]) * 100)
    return spread(fence) - statistics.median([spread(t) for t in keep])


# ------------------------------------------------------------------------------------------------------------------------
# vintages on disk
# ------------------------------------------------------------------------------------------------------------------------
MANIFEST_HEAD = ["url", "sha256", "bytes", "fetched_at"]


def vdir_of(vroot, v):
    return os.path.join(vroot, v)


def manifest_rows(vdir):
    p = os.path.join(vdir, "MANIFEST.csv")
    if not os.path.isfile(p):
        return []
    return read_csv_dicts(read_file(p, "r"))


def mn_of_url(url):
    m = re.search(r"mnemonic=([A-Za-z0-9_\-]+)", url)
    return m.group(1) if m else None


def load_vintage(vdir):
    """(prelim Data, finals Data or None, manifest rows). Every file must match its MANIFEST sha256."""
    rows = manifest_rows(vdir)
    if not rows:
        raise Structural("no MANIFEST.csv in %s" % vdir)
    by_mn = {mn_of_url(r["url"]): r for r in rows}
    ser = {}
    for mn in ALL_MN:
        p = os.path.join(vdir, mn + ".json")
        if not os.path.isfile(p):
            if mn in PRELIM:
                raise Structural("missing %s.json" % mn)
            continue
        body = read_file(p)
        r = by_mn.get(mn)
        if r is None or r["sha256"] != sha256_of(body):
            raise Structural("%s.json does not match its MANIFEST.csv row" % mn)
        ser[mn] = parse_series(body, mn)
    d = Data(ser[MN_B27], ser[MN_OO], ser[MN_TVB], ser[MN_TVO], ser[MN_B830])
    fin = Data(ser[FINALS[0]], ser[FINALS[1]], ser[FINALS[2]], ser[FINALS[3]]) if all(m in ser for m in FINALS) else None
    return d, fin, rows


def cap_applies(rows, P):
    return bool(rows) and all(parse_z(r["fetched_at"]) < P.gate for r in rows)


# ------------------------------------------------------------------------------------------------------------------------
# outputs (spec 5)
# ------------------------------------------------------------------------------------------------------------------------
DAILY_HEAD = ["date", "b27", "oo", "tv_b27", "tv_oo", "b830", "s_bp", "coupon", "bill", "early", "fomc_in_7d"]
TURNS_HEAD = ["t", "t_minus_1", "kind", "status", "n_k", "s_t1", "control_median", "e", "db", "do", "ot", "v1", "v2", "v3", "v4", "v5", "v6", "v7_min", "v7_max", "v7_n",
              "tv_b27_t1", "tv_b27_k_mean", "tv_oo_t1", "tv_oo_k_mean", "tick_sensitive"]
TURN_FIELDS = TURNS_HEAD + ["why", "K"]
REG_HEAD = ["prereg_sha256", "vintage", "fetched_at", "t", "t_minus_1", "s_t1", "control_median", "e", "db", "do", "ot", "placebo_min", "placebo_max", "n_placebo", "label", "tick_sensitive"]
CHECKS_HEAD = ["id", "status", "detail"]
REV_HEAD = ["t", "field", "vintage_a", "vintage_b", "a", "b"]
VOLUME_FIELDS = ("tv_b27_t1", "tv_b27_k_mean", "tv_oo_t1", "tv_oo_k_mean")
YES = lambda b: "yes" if b else "no"


def daily_csv(d, P):
    every = sorted(set(d.b27.dates) | set(d.oo.dates) | set(d.tvb.dates) | set(d.tvo.dates) | set(d.b830.dates))
    cps = set(coupon_day(d, y, m, P) for (y, m) in sorted(set((t.year, t.month) for t in every)))
    rows = []
    for t in every:
        def raw(s):
            v = s.raw.get(t)
            return "" if v is None else v
        rows.append([t.isoformat(), raw(d.b27), raw(d.oo), raw(d.tvb), raw(d.tvo), raw(d.b830), fmt_fr(s_bp(d, t), 2) if t in d.bizset else "", YES(t in cps), YES(t.weekday() in (1, 3)),
                     YES(t in P.early_set), YES(fomc_in_window(t, P))])
    return csv_text(DAILY_HEAD, rows)


def turn_cells(r):
    cells = []
    for k in TURNS_HEAD:
        v = r[k]
        if v is None:
            cells.append("")
        elif k in ("t", "t_minus_1"):
            cells.append(v.isoformat())
        elif k in ("kind", "status", "tick_sensitive"):
            cells.append(v)
        elif k in ("n_k", "v7_n"):
            cells.append(str(v))
        elif k in VOLUME_FIELDS:
            cells.append(fmt_fr(v, 0))
        else:
            cells.append(fmt_fr(v, 2))
    return cells


def turns_csv(rows):
    return csv_text(TURNS_HEAD, [turn_cells(r) for r in rows])


def revisions_rows(rows_a, rows_b, va, vb):
    """The same turn in two sets of rows (two vintages, or finals against preliminary): where both are assessed, E and both legs side by side."""
    out = []
    bt = {r["t"]: r for r in rows_b}
    for ra in rows_a:
        rb = bt.get(ra["t"])
        if rb is None or ra["status"] != "OK" or rb["status"] != "OK":
            continue
        for f in ("e", "db", "do"):
            out.append([ra["t"].isoformat(), f, va, vb, fmt_fr(ra[f], 2), fmt_fr(rb[f], 2)])
    return out


# ------------------------------------------------------------------------------------------------------------------------
# pinned checks (spec 7)
# ------------------------------------------------------------------------------------------------------------------------
def pinned_checks(d, fin, rows, P, man, now):
    ck = []

    def add(i, st, detail):
        ck.append((i, st, detail))
    for mn in PRELIM:
        ser = {MN_B27: d.b27, MN_OO: d.oo, MN_TVB: d.tvb, MN_TVO: d.tvo, MN_B830: d.b830}[mn]
        n = len(ser.dates)
        add("rows_" + mn, "PASS" if n >= MIN_ROWS[mn] else "FAIL", "%d rows, at least %d expected" % (n, MIN_ROWS[mn]))
    first = d.b27.dates[0] if d.b27.dates else None
    add("first_b27_date", "PASS" if first == FIRST_B27 else "FAIL", "first B27 date %s, expected %s" % (first, FIRST_B27))
    last = d.last
    missing = [r["t"].isoformat() for r in rows if last is not None and r["t"] <= last and r["t"] not in d.oo.val]
    add("complete_t_in_oo", "PASS" if not missing else "FAIL", "every complete T is a date of the overnight series" if not missing else "absent from the overnight series: " + ", ".join(missing))
    bad = []
    for t, tm1 in zip(P.placebo_t, P.placebo_tm1):
        if last is not None and t <= last and t in d.oo.val and d.prev_oo(t) != tm1:
            bad.append("%s: previous overnight date %s, fence %s" % (t, d.prev_oo(t), tm1))
    if M("fence_check_off"):
        bad = []
    add("fence_t_minus_1", "PASS" if not bad else "FAIL", "the fence's T-1 list equals the computed one for every complete placebo T" if not bad else "; ".join(bad))
    if fin is None:
        add("finals_cover", "WARN", "no finals files in this vintage")
    else:
        diffs = []
        for name, a, b in (("B27", d.b27, fin.b27), ("OO", d.oo, fin.oo), ("TV_B27", d.tvb, fin.tvb), ("TV_OO", d.tvo, fin.tvo)):
            sa = set(t for t in a.dates if t <= FINALS_THROUGH)
            sb = set(t for t in b.dates if t <= FINALS_THROUGH)
            if sa != sb:
                diffs.append("%s: %d dates only in preliminary, %d only in finals" % (name, len(sa - sb), len(sb - sa)))
        add("finals_cover", "PASS" if not diffs else "FAIL", "finals and preliminary cover the same dates up to %s" % FINALS_THROUGH if not diffs else "; ".join(diffs))
    done = [r for r in rows if r["status"] == "OK"]
    if done:
        r0 = done[0]
        e2 = e_second_path(r0["t"], d, P)
        ok = e2 is not None and e2 == r0["e"]
        add("second_path_e", "PASS" if ok else "FAIL", "E for %s re-derived by a second code path: %s" % (r0["t"], "equal" if ok else "DIFFERENT or not derivable"))
    else:
        add("second_path_e", "WARN", "no assessed turn to re-derive")
    if cap_applies(man, P):
        later = [s for s, ser in (("B27", d.b27), ("OO", d.oo), ("TV_B27", d.tvb), ("TV_OO", d.tvo), ("B830", d.b830)) if ser.dates and ser.dates[-1] > D(END_CAP)]
        add("pre_gate_cap", "PASS" if not later else "FAIL", "no date after %s in a vintage fetched before the gate" % END_CAP if not later else "dates after the cap in " + ", ".join(later))
    nb = len(d.biz)
    nulls = sum(1 for s in (d.b27, d.oo) for t in s.dates if s.val[t] is None)
    add("business_days", "INFO", "%d business days (present and non-null in both B27 and OO); %d null cells in B27 and OO" % (nb, nulls))
    decs = sorted(set(len(v.split(".")[1]) if "." in v else 0 for s in (d.b27, d.oo) for v in s.raw.values() if v is not None))
    add("rate_decimals", "INFO", "decimals in the rate strings: %s" % ", ".join(str(x) for x in decs))
    return ck


def structural_fails(ck):
    return [c for c in ck if c[1] == "FAIL"]


# ------------------------------------------------------------------------------------------------------------------------
# the README generator (written by `describe`; nothing is typed by hand)
# ------------------------------------------------------------------------------------------------------------------------
LIMITS = (
    "It does not say why the gap on the day was wider or narrower than usual. A wider gap can come from the overnight rate falling as well as from the 2-7 day rate rising (both legs are always shown), "
    "from a shift in the kinds of collateral (both series pool every class), or from which dealers borrowed; the series has no counterparty detail.",
    "It does not say whether lenders asked for more to lend across the date, and no number here is described that way.",
    "It makes no comparison with SOFR or the other reference rates: the OFR says these averages do not allow direct comparison with those rates.",
    "The overnight figure is not a pure overnight rate. It includes open repo, which can be closed before the date.",
    "It does not describe the turn on the last day itself as a 2-7 day spread. The loan that spans this year-end most directly, from Thursday 31 December to Monday 4 January, is one business day long "
    "and sits in the overnight bucket. That is why the overnight rate on the day itself is shown on its own, in the column ot.",
    "It says nothing about dates before 13 August 2025, nothing about other repo (cleared or bilateral), and nothing about year-ends in general: there is one December and none of the eight comparison months is a year-end.",
    "INSIDE means inside a range of eight, in one spread, on one day. A lender who declines to lend across the date leaves no print, so a quiet spread is not a finding that nothing happened.",
    "Trades on the effective date of a Fed decision may have been agreed before the announcement the previous afternoon. Only trade-level timestamps would settle it, and this file has none.",
)
SOURCE_LIMITS = (
    "Volumes include affiliate repo and rates do not, so a volume is context and not the sample behind the rate; it is never used as a weight.",
    "A missing value means no trading or a disclosure edit. It is never read as zero and never as evidence about activity.",
    "Preliminary prints lag by two business days and are revised. The January fetch decides the registered reading and the comparison months alike; the revisions file shows how far the numbers moved.",
)
FORBIDDEN_RX = re.compile(r"\bcharg\w*|\bpremium\w*|\bcaus\w*|\bbecause\b|\bdue to\b|\bdrov\w*|\bdriv(?:e|es|en|ing)\b|\bled to\b|\bthanks to\b|\bsignifican\w*|\bproves?\b|\bproven\b|\bstress\w*", re.I)
SECTIONS = ("## What the numbers show", "## What this cannot say", "## How to rerun")


def readme_problems(text):
    if M("readme_guard_off"):
        return []
    probs = []
    for s in LIMITS + SOURCE_LIMITS:
        if s not in text:
            probs.append("a required limit sentence is missing: " + s[:50])
    m = FORBIDDEN_RX.search(text)
    if m:
        probs.append("forbidden wording: " + m.group(0))
    pos = [text.find(s) for s in SECTIONS]
    if -1 in pos or pos != sorted(pos):
        probs.append("the sections are missing or out of order (numbers first, then limits, then how to rerun)")
    if "registered.csv" not in text:
        probs.append("README does not point to registered.csv")
    return probs


def _tbl(head, body):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    for r in body:
        out.append("| " + " | ".join(r) + " |")
    return out


def _turn_line(r, pmax):
    if r["status"] != "OK":
        return [r["t"].isoformat(), r["status"], "", "", "", "", ""]
    return [r["t"].isoformat(), sgn(r["s_t1"]), sgn(r["control_median"]), sgn(r["e"]), sgn(r["db"]), sgn(r["do"]), ("" if pmax is None else YES(r["e"] > pmax))]


def readme_text(rows, vintage, P, checks, rev_count=0):
    pmin, pmax, n = placebo_range(rows)
    plac = [r for r in rows if r["kind"] == "placebo"]
    quarters = [r for r in rows if r["kind"] == "quarter"]
    described = [r for r in rows if r["kind"] == "described"]
    target = [r for r in rows if r["kind"] == "target"][0]
    L = ["# Term repo at the month-end turn", "", "Written by `python3 bin/term_repo_turns.py build --stage describe` from the data vintage %s. Do not edit by hand." % vintage, "",
         "## What the numbers show", ""]
    L.append("Take the last business day before a month-end. A tri-party repo loan (a loan against securities, with a clearing bank between lender and borrower) that starts that day in the 2-7 day "
             "bucket lasts more than one business day, so every such loan is still open on the month-end. An overnight loan that starts the same day is not. That is the one start date on which the "
             "two buckets differ in exactly that respect.")
    L.append("")
    L.append("The gap S is the 2-7 day rate minus the overnight/open rate, in basis points (one basis point is one hundredth of a percentage point). The difference E is the gap on that day minus the "
             "median gap on ordinary days of the same month, the control days. The median is the middle value, or the mean of the middle two. The columns dB and dO are the 2-7 day rate and the "
             "overnight rate on the day, each minus its own median over the control days. A median of differences is not a difference of medians, so dB minus dO need not equal E.")
    L.append("")
    if n:
        L.append("At the %d of eight ordinary month-ends that could be assessed, E ran from %s to %s basis points." % (n, sgn(pmin), sgn(pmax)))
    else:
        L.append("None of the eight ordinary month-ends could be assessed on this vintage, so there is no range yet.")
    L.append("")
    head = ["month-end", "gap S on the day before", "median gap on control days", "E", "dB", "dO", "E above the largest of the eight"]
    L.append("The eight ordinary month-ends, in basis points:")
    L.append("")
    L += _tbl(head[:-1], [_turn_line(r, pmax)[:-1] for r in plac])
    L.append("")
    L.append("dB and dO are measured against control days that can lie on the other side of a Fed rate move, so in such a month they mostly show the move (September 2025 and September 2026 among the quarter-ends below, October 2025 here, where the step falls on the day itself). Read them with the Fed dates beside them. E is much less exposed, as the move is in both rates.")
    if n:
        ranked = sorted((r for r in plac if r["status"] == "OK"), key=lambda r: r["e"])
        top = ranked[-1]
        L.append("The top of the range is set by %s alone (%s; the next highest is %s). Only the top decides ABOVE, so one month sets that bar." % (top["t"].isoformat(), sgn(top["e"]), sgn(ranked[-2]["e"]) if len(ranked) > 1 else "none"))
    L.append("")
    qa = [r for r in quarters if r["status"] == "OK"]
    if n >= P.min_placebo and qa:
        above = sum(1 for r in qa if r["e"] > pmax)
        L.append("The five quarter-ends that have passed (September 2025 to September 2026): %d of the %d assessed have an E above the largest of the eight. This is a count and not a test." % (above, len(qa)))
    else:
        L.append("The five quarter-ends that have passed (September 2025 to September 2026): %d of 5 could be assessed, and there is no range of eight to count against yet." % len(qa))
    L.append("")
    L += _tbl(head, [_turn_line(r, pmax if n >= P.min_placebo else None) for r in quarters])
    L.append("")
    L.append("The three months left out of the comparison, described only (August 2025 was the first month of the bucket; at the end of April 2026 the Fed decision took effect inside the loan; "
             "27 November 2026 is a recommended early close): " + ", ".join("%s %s" % (r["t"].isoformat(), ("E " + sgn(r["e"])) if r["status"] == "OK" else r["status"]) for r in described) + ".")
    L.append("")
    if target["status"] == "OK":
        L.append("The queued December statement (T-1 = 30 December 2026): E is %s basis points; the registered reading is in registered.csv, and this line only repeats it." % sgn(target["e"]))
    else:
        L.append("The queued December statement (T-1 = 30 December 2026) is %s. It is filled in by the first fetch on or after 2027-01-05T20:00Z and written once to registered.csv." % target["status"])
    L.append("")
    L.append("The checks file has %s." % ", ".join("%d %s" % (sum(1 for c in checks if c[1] == s), s) for s in ("PASS", "WARN", "FAIL", "INFO")))
    if rev_count:
        L.append("The revisions file lines up %d values from two vintages or from the final and preliminary series." % rev_count)
    L += ["", "## What this cannot say", ""]
    for s in LIMITS:
        if M("readme_drops_limit") and s.startswith("Trades on"):
            continue
        L.append("- " + s)
    for s in SOURCE_LIMITS:
        L.append("- " + s)
    if M("readme_charge"):
        L.append("- A lender may have levied a premium for the date.")
    L += ["", "Why these eight: four months with no Fed decision near the month-end (November 2025, February, May and August 2026) and four where the day before is itself the effective date of the decision, "
          "so no decision falls inside the loan (October 2025, January, July and October 2026). Under exchangeability, a December above all eight has probability 1 in 9; the months are not independent, "
          "so that is a guide and not a test.", ""]
    L += ["## How to rerun", "",
          "Source: Office of Financial Research, tri-party repo rates excluding Federal Reserve trades, preliminary vintage, free public data from data.financialresearch.gov, no key. The OFR says the rates "
          "are not intended to be referenced in contracts.", "",
          "1. `python3 bin/term_repo_turns.py fetch` (supervisor only; nine GETs at least 3 seconds apart; before 2027-01-05T20:00Z it stops at 23 December 2026).",
          "2. `python3 bin/term_repo_turns.py build --vintage YYYYMMDD --stage pre` (layout and coverage; prints no rate and no spread).",
          "3. `python3 bin/term_repo_turns.py build --vintage YYYYMMDD --stage dry` (the rule engine over the real dates with every value hidden).",
          "4. `python3 bin/term_repo_turns.py build --vintage YYYYMMDD --stage describe` (writes this folder, except registered.csv).",
          "5. On or after 2027-01-05T20:00Z, with a vintage fetched then: `python3 bin/term_repo_turns.py build --vintage YYYYMMDD --stage register`. It writes registered.csv once; a second run exits 5; "
          "exit 6 means the December print is not in yet and nothing was written.",
          "6. `python3 bin/term_repo_turns.py selftest` (synthetic data, no network) and `bash bin/check.sh --all` (guard M30).", ""]
    return "\n".join(L)


# ------------------------------------------------------------------------------------------------------------------------
# stages
# ------------------------------------------------------------------------------------------------------------------------
def weekdays_between(a, b):
    out, t = [], a
    while t <= b:
        if t.weekday() < 5:
            out.append(t)
        t += dt.timedelta(1)
    return out


def run_pre(d, fin, man, say):
    """Layout, coverage, decimals, one volume's order of magnitude, calendar-minus-data dates. No rate, no spread."""
    say("pre: layout, coverage and calendar only; no rate and no spread is printed")
    for mn, ser in zip(PRELIM, (d.b27, d.oo, d.tvb, d.tvo, d.b830)):
        nulls = sum(1 for t in ser.dates if ser.val[t] is None)
        say("  %-24s %4d [date, value] pairs  %s to %s  nulls %d" % (mn, len(ser.dates), ser.dates[0] if ser.dates else "-", ser.dates[-1] if ser.dates else "-", nulls))
    for nm, ser in (("B27", d.b27), ("OO", d.oo), ("B830", d.b830)):
        decs = sorted(set(len(v.split(".")[1]) if "." in v else 0 for v in ser.raw.values() if v is not None))
        say("  decimals in the %s rate strings: %s" % (nm, ", ".join(str(x) for x in decs) or "-"))
    vol = next((ser.raw[t] for ser in (d.tvo,) for t in ser.dates if ser.raw[t] is not None), None)
    if vol is not None:
        say("  order of magnitude of one overnight volume: 10^%d (USD, magnitude 0)" % (len(vol.split(".")[0].lstrip("-")) - 1))
    first_b = d.b27.dates[0] if d.b27.dates else None
    only_b = [t for t in d.b27.dates if t not in d.oo.val]
    only_o = [t for t in d.oo.dates if t not in d.b27.val and first_b is not None and t >= first_b]
    nulled = [t for t in d.b27.dates if t in d.oo.val and t not in d.bizset]
    say("  dates in B27 only: %d; in OO only (from the B27 start): %d; present in both but null in one: %d (OO starts earlier by design)" % (len(only_b), len(only_o), len(nulled)))
    if M("pre_prints_rate") and d.oo.dates:
        say("  first overnight rate: %s" % d.oo.raw[d.oo.dates[0]])
    if d.b27.dates and d.last:
        have = set(d.b27.dates) | set(d.oo.dates)
        absent = [t for t in weekdays_between(d.b27.dates[0], d.last) if t not in have]
        hol = set(D(x) for x in FED_HOLIDAYS)
        odd = [t for t in absent if t not in hol]
        say("  weekdays from %s to %s absent from both series: %d; not on the federal-holiday list: %s" % (d.b27.dates[0], d.last, len(absent), ", ".join(t.isoformat() for t in odd) or "none"))
    say("  manifest rows: %d; earliest fetched_at %s" % (len(man), min((r["fetched_at"] for r in man), default="-")))


def fomc_from_text(text):
    """Effective dates (the day after the second meeting day) read from the text of the Board's FOMC calendar page. Tags are stripped first: the page puts month and days in separate elements (read 2 Nov 2026). A single day is a notation vote, not a meeting, so only a two-day range counts."""
    text = re.sub(r"<[^>]+>", " ", text)
    out, year = set(), None
    mon = {m: i + 1 for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])}
    rx = re.compile(r"(\d{4}) FOMC Meetings|(" + "|".join(mon) + r")\s*(\d{1,2})\s*-\s*(?:(" + "|".join(mon) + r")\s*)?(\d{1,2})")
    for m in rx.finditer(text):
        if m.group(1):
            year = int(m.group(1))
            continue
        if year is None:
            continue
        m2 = mon[m.group(4)] if m.group(4) else mon[m.group(2)]
        day = int(m.group(5) or m.group(3))
        try:
            out.add(dt.date(year, m2, day) + dt.timedelta(1))
        except ValueError:
            pass
    return out


def register_refusals(P, vdir, now, root, git):
    """Every reason `register` would refuse, in order: the hash, the gate, the vintage, the git history. Writes nothing."""
    out = []
    if not prereg_ok():
        out.append("the embedded prereg block does not hash to SPEC_PREREG_SHA256")
    if now < P.gate and not M("gate_off"):
        out.append("the gate %s has not passed (clock %s)" % (iso_z(P.gate), iso_z(now)))
    man = manifest_rows(vdir)
    if not man:
        out.append("the vintage has no MANIFEST.csv")
    elif not M("manifest_check_off"):
        early = [r["fetched_at"] for r in man if parse_z(r["fetched_at"]) < P.gate]
        if early:
            out.append("the vintage holds %d file(s) fetched before the gate (earliest %s)" % (len(early), min(early)))
    try:
        rc, hist = git(root)
    except Exception as e:                                  # fail closed: a history that cannot be read is not an empty one
        rc, hist = 1, "git could not be run: %s" % type(e).__name__
    if rc != 0:
        out.append("git history of registered.csv could not be read: %s" % hist.strip()[:80])
    elif hist.strip() and not M("git_off"):
        out.append("registered.csv has an earlier version in git history (%s)" % hist.split()[0][:12])
    return out


def real_git(root):
    r = subprocess.run(["git", "-C", root, "log", "--all", "--format=%H", "--", "data/term_repo_turns/registered.csv"], capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout if r.returncode == 0 else r.stderr


def run_dry(d, P, vdir, now, root, git, say, fomc_text=None):
    say("dry: the rule engine over the real dates; every value is replaced by one before anything runs, so no value can appear")
    h = hidden(d)
    rows = [assess(T, kind, h, P, now) for T, kind in all_turns(P)]
    say("  %-10s %-9s %-10s %-9s %4s  %s" % ("T", "kind", "T-1", "fence", "|K|", "status"))
    for r in rows:
        fence = P.fence_tm1.get(r["t"])
        fm = "-" if fence is None else ("match" if r["t_minus_1"] == fence and (r["t"] not in h.oo.val or h.prev_oo(r["t"]) == fence) else "DIFFERS")
        say("  %-10s %-9s %-10s %-9s %4d  %s" % (r["t"], r["kind"], r["t_minus_1"] or "-", fm, len(k_days(r["t"], h, P)), r["status"] + ((" (" + r["why"] + ")") if r["why"] else "")))
    kd = k_days(P.target_t, h, P)
    say("  target control days (%d): %s" % (len(kd), " ".join(str(t.day) for t in kd)))
    if fomc_text is None:
        say("  WARN FOMC recheck not done: no --fomc-page file was given and this script never fetches federalreserve.gov")
    else:
        got = fomc_from_text(fomc_text)
        if not got:
            say("  WARN FOMC recheck: no meeting dates could be read from the page text")
        else:
            window = set(t for t in P.fomc if min(got) <= t <= max(got))
            miss, extra = sorted(window - got), sorted(x for x in got - set(P.fomc) if min(P.fomc) <= x <= max(P.fomc))
            if miss or extra:
                say("  WARN FOMC recheck differs: in the fence but not on the page: %s; on the page but not in the fence: %s" % (miss or "none", extra or "none"))
            else:
                say("  FOMC recheck: the page and the fence agree on %d effective dates" % len(window))
    if M("dry_prints_value") and d.b27.dates:
        say("  first 2-7 day rate: %s" % d.b27.raw[d.b27.dates[0]])
    why = register_refusals(P, vdir, now, root, git)
    say("  register would %s%s" % ("REFUSE: " if why else "not refuse on these grounds", "; ".join(why)))
    return rows


def describe_files(d, fin, man, v, P, now, vs_rows=None, vs_label=None):
    rows = evaluate_all(d, P, now)
    ck = pinned_checks(d, fin, rows, P, man, now)
    rev = []
    if fin is not None:
        frows = evaluate_all(fin, P, now)
        rev += revisions_rows(rows, frows, "preliminary", "final")
    if vs_rows is not None:
        rev += revisions_rows(vs_rows, rows, vs_label, v)
    files = {"daily.csv": daily_csv(d, P), "turns.csv": turns_csv(rows), "checks.csv": csv_text(CHECKS_HEAD, ck), "revisions.csv": csv_text(REV_HEAD, rev)}
    files["README.md"] = readme_text(rows, v, P, ck, len(rev))
    if M("describe_writes_registered"):
        files[REG_NAME] = "x\n"
    return rows, ck, files


def run_build(a, say=print, root=None, now_utc=None, git=real_git):
    now = (now_utc or utc_now)()
    P = PR
    v = a.vintage
    if not vintage_ok(v):
        raise Refused("--vintage must be a valid YYYYMMDD date")
    vroot = vroot_of(root, getattr(a, "cache", None))
    vdir = vdir_of(vroot, v)
    st = a.stage
    if st == "register":                       # the gate, the vintage and the history are judged before anything is read: today this refuses
        why = register_refusals(P, vdir, now, root or ROOT, git)
        if why:
            raise Refused("register refuses: " + "; ".join(why))
    d, fin, man = load_vintage(vdir)
    if st == "pre":
        run_pre(d, fin, man, say)
        return 0
    if st == "dry":
        ft = None
        if getattr(a, "fomc_page", None):
            ft = read_file(a.fomc_page, "r")
        run_dry(d, P, vdir, now, root or ROOT, git, say, ft)
        return 0
    if st == "describe":
        vs_rows = vs_label = None
        if getattr(a, "vs", None):
            if not vintage_ok(a.vs):
                raise Refused("--vs must be a valid YYYYMMDD date")
            d2, _, _ = load_vintage(vdir_of(vroot, a.vs))
            vs_rows, vs_label = evaluate_all(d2, P, now), a.vs
        rows, ck, files = describe_files(d, fin, man, v, P, now, vs_rows, vs_label)
        probs = readme_problems(files["README.md"])
        if probs:
            raise DataError("README wording or structure: " + "; ".join(probs))
        out = out_of(root, getattr(a, "out", None))
        for name, text in files.items():
            write_text(os.path.join(out, name), text)
        fails = structural_fails(ck)
        say("describe: wrote %s to %s (%d turns: %s)" % (", ".join(sorted(files)), out, len(rows), ", ".join("%s %d" % (s, sum(1 for r in rows if r["status"] == s)) for s in ("OK", "PENDING", "NOT_ASSESSED"))))
        for c in fails:
            say("  FAIL %s: %s" % (c[0], c[2]))
        if fails:
            raise Structural("%d pinned check(s) failed" % len(fails))
        return 0
    return run_register(a, d, fin, man, vdir, v, P, now, root, git, say)


def run_register(a, d, fin, man, vdir, v, P, now, root, git, say):
    why = register_refusals(P, vdir, now, root or ROOT, git)
    if why:
        raise Refused("register refuses: " + "; ".join(why))
    rows = evaluate_all(d, P, now)
    ck = pinned_checks(d, fin, rows, P, man, now)
    fails = structural_fails(ck)
    if fails:
        for c in fails:
            say("  FAIL %s: %s" % (c[0], c[2]))
        raise Structural("%d pinned check(s) failed; nothing is registered" % len(fails))
    tgt = [r for r in rows if r["kind"] == "target"][0]
    if tgt["status"] == "PENDING":
        say("PENDING: %s; nothing is written (retry on the next business day until %s, then NOT_ASSESSED)" % (tgt["why"], P.retry_until))
        return 6
    pmin, pmax, n = placebo_range(rows)
    lab = label_of(tgt["status"], tgt["e"], pmin, pmax, n, P)
    ok = tgt["status"] == "OK"
    f2 = lambda x: fmt_fr(x, 2) if (ok and x is not None) else ""
    row = [SPEC_PREREG_SHA256, v, min(r["fetched_at"] for r in man), P.target_t.isoformat(), P.target_tm1.isoformat(), f2(tgt["s_t1"]), f2(tgt["control_median"]), f2(tgt["e"]), f2(tgt["db"]),
           f2(tgt["do"]), f2(tgt["ot"]), fmt_fr(pmin, 2), fmt_fr(pmax, 2), str(n), lab, tgt["tick_sensitive"] or ""]
    write_once(os.path.join(out_of(root, getattr(a, "out", None)), REG_NAME), csv_text(REG_HEAD, [row]))
    say("register: wrote %s once (label %s, %d of 8 placebo months assessed); it is never re-scored" % (REG_NAME, lab, n))
    return 0


# ------------------------------------------------------------------------------------------------------------------------
# fetch (spec 1.1, 1.3)
# ------------------------------------------------------------------------------------------------------------------------
def real_opener(host, target, headers, timeout, cap):
    """GET https://host/target. No redirect is followed (a 3xx comes back as a status and latches), no cookies, the only verb is GET. A non-200 body is read up to ERR_CAP bytes.
    Returns (status, body, lower-cased response headers); socket faults raise SocketFault."""
    conn = http.client.HTTPSConnection(host, timeout=timeout)
    try:
        conn.request("GET", target, headers=dict(headers))
        resp = conn.getresponse()
        hdrs = {k.lower(): v for k, v in resp.getheaders()}
        if resp.status != 200:
            return resp.status, resp.read(ERR_CAP), hdrs
        chunks, total = [], 0
        while True:
            b = resp.read(1 << 16)
            if not b:
                break
            total += len(b)
            if total > cap:
                return resp.status, None, hdrs
            chunks.append(b)
        return resp.status, b"".join(chunks), hdrs
    except (OSError, http.client.HTTPException) as e:
        raise SocketFault(type(e).__name__)
    finally:
        conn.close()


def check_url(host, target):
    if (host != HOST and not M("host_any")) or not target.startswith(API_PATH + "?mnemonic="):
        raise Refused("only GET https://%s%s?mnemonic=... is allowed" % (HOST, API_PATH))


def series_url(mn, capped, today=None):
    """Pre-gate, end_date is the cap, or today when the cap is still ahead: the API answers 400 to a future end_date (seen 2 Nov 2026; ruling R3-1)."""
    q = "mnemonic=%s&start_date=%s" % (quote(mn, safe="-_"), START_DATE)
    if capped and not M("cap_url_missing"):
        q += "&end_date=" + (min(today, END_CAP) if today and not M("cap_no_today") else END_CAP)
    return q


def esc_head(body, n=300):
    return (body or b"")[:n].decode("latin-1").encode("unicode_escape").decode("ascii")


def stop_text(status, utc, target, why, body_head):
    return "status: %s\nutc_time: %s\nurl_path: %s\nwhy: %s\nbody_head: %s\n" % (status, utc, target, why, body_head)


def run_fetch(a, opener=real_opener, now_utc=None, sleeper=time.sleep, mono=time.monotonic, say=print, root=None):
    now = (now_utc or utc_now)()
    P = PR
    vroot = vroot_of(root, getattr(a, "cache", None))
    stop_path = os.path.join(vroot_of(root), STOP_NAME)                # fixed, whatever --cache says: a latch cannot be dodged by pointing the cache elsewhere
    sleep = float(getattr(a, "sleep", None) or DEFAULT_SLEEP)
    if sleep < MIN_SLEEP and not M("pacing_off"):
        raise Refused("--sleep must be at least %g seconds" % MIN_SLEEP)
    v = getattr(a, "vintage", None) or now.strftime("%Y%m%d")
    if not vintage_ok(v):
        raise Refused("--vintage must be a valid YYYYMMDD date")
    if v != now.strftime("%Y%m%d"):
        raise Refused("the vintage of a fetch is today's UTC date (%s)" % now.strftime("%Y%m%d"))
    if os.path.exists(stop_path) and not M("stop_ignored"):
        say("STOP: %s exists; no request is made. Only a person deletes it." % STOP_NAME)
        return 2
    vdir = vdir_of(vroot, v)
    if os.path.exists(os.path.join(vdir, "MANIFEST.csv")) and not getattr(a, "replace", False) and not M("replace_off"):
        raise Refused("vintage %s was already fetched; a second fetch on one day needs --replace" % v)
    capped = now < P.gate
    headers = {"User-Agent": USER_AGENT + (" (contact" + chr(64) + "invalid)" if M("ua_contact") else ""), "Accept-Encoding": "identity", "Accept": "application/json"}
    got, last_start = [], None

    def latch(status, body, target, why):
        text = stop_text(status, iso_z(now), target, why, esc_head(body))
        if not M("no_latch"):
            os.makedirs(os.path.dirname(stop_path), exist_ok=True)
            try:
                with open(stop_path, "x", encoding="utf-8") as fh:
                    fh.write(text)
            except FileExistsError:
                pass
        say("STOP: %s (HTTP %s); %s written; no retry, nothing from this fetch is kept" % (why, status, STOP_NAME))
        return 2
    for mn in ALL_MN:
        target = API_PATH + "?" + series_url(mn, capped, now.strftime("%Y-%m-%d"))
        check_url(HOST, target)
        if last_start is not None and not M("pacing_off"):
            wait = sleep - (mono() - last_start)
            if wait > 0:
                sleeper(wait)
        last_start = mono()
        started = (now_utc or utc_now)()
        try:
            status, body, rh = opener(HOST, target, dict(headers), TIMEOUT, BODY_CAP)
        except SocketFault as e:
            say("FAIL network (%s) on %s; no STOP file, no retry" % (e, mn))
            return 3
        if M("retry") and status != 200:
            status, body, rh = opener(HOST, target, dict(headers), TIMEOUT, BODY_CAP)
        say("  GET %s -> %s, %s bytes" % (target, status, "?" if body is None else len(body)))
        if status != 200:
            kind = "a refusal (403)" if status == 403 else ("rate limit (429)" if status == 429 else "a non-200 status")
            return latch(status, body, target, kind)
        if body is None:
            return latch(status, b"", target, "body larger than the cap")
        try:
            ser = parse_series(body, mn)
        except Structural as e:
            if not M("bot_ok"):
                return latch(status, body, target, "bot check or non-JSON body (%s)" % e)
            ser = Series(mn, [])
        hd = rh.get("date")
        try:
            srv = email.utils.parsedate_to_datetime(hd) if hd else None
        except (TypeError, ValueError):
            srv = None
        if not M("skew_off"):
            if srv is None:
                raise Refused("the response has no usable HTTP Date header: the machine clock cannot be checked")
            skew = abs((srv - started).total_seconds())
            if skew > (86400 if M("skew_loose") else SKEW_SECONDS):
                raise Refused("the machine clock differs from the server's Date by %d s (more than one hour)" % skew)
        if capped and ser.dates and ser.dates[-1] > D(END_CAP) and not M("cap_off"):
            raise Refused("%s holds a date (%s) later than the pre-gate cap %s: nothing is written" % (mn, ser.dates[-1], END_CAP))
        got.append((mn, target, body, iso_z(started)))
    rows = []
    for mn, target, body, at in got:
        write_bytes(os.path.join(vdir, mn + ".json"), body)
        rows.append(["https://%s%s" % (HOST, target), sha256_of(body), str(len(body)), at])
    write_text(os.path.join(vdir, "MANIFEST.csv"), csv_text(MANIFEST_HEAD, rows))
    say("fetched: %d series into %s%s" % (len(rows), vdir, " (pre-gate: capped at %s)" % END_CAP if capped else ""))
    return 0


# ------------------------------------------------------------------------------------------------------------------------
# command line
# ------------------------------------------------------------------------------------------------------------------------
def make_parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch", help="nine GETs to data.financialresearch.gov (network; supervisor only)")
    pf.add_argument("--vintage", default=None, help="YYYYMMDD: today's UTC date (the default)")
    pf.add_argument("--replace", action="store_true", help="replace a vintage already fetched today")
    pf.add_argument("--cache", default=None)
    pf.add_argument("--sleep", default=None, help="seconds between request starts (at least 3)")
    pb = sub.add_parser("build", help="offline: one stage on one vintage")
    pb.add_argument("--vintage", required=True)
    pb.add_argument("--stage", required=True, choices=("pre", "dry", "describe", "register"))
    pb.add_argument("--cache", default=None)
    pb.add_argument("--out", default=None)
    pb.add_argument("--vs", default=None, help="describe: a second vintage to put beside this one in revisions.csv")
    pb.add_argument("--fomc-page", dest="fomc_page", default=None, help="dry: a saved copy of the Board's FOMC calendar page, for the recheck")
    ps = sub.add_parser("selftest", help="synthetic data, mutants applied one at a time; no network")
    ps.add_argument("--no-mutants", action="store_true")
    ps.add_argument("--mutant", help="run every guard with this one mutant switched on; exit 1 when it is caught")
    return ap


def dispatch(a, root=None, say=print, err=None, opener=real_opener, now_utc=None, sleeper=time.sleep, mono=time.monotonic, git=real_git):
    err = err or (lambda s: print(s, file=sys.stderr))
    try:
        if a.cmd == "build":
            return run_build(a, say=say, root=root, now_utc=now_utc, git=git)
        return run_fetch(a, opener=opener, now_utc=now_utc, sleeper=sleeper, mono=mono, say=say, root=root)
    except Refused as e:
        err("refused: %s" % e)
        return 5
    except Structural as e:
        err("STRUCTURAL FAULT (exit 4): %s" % e)
        return 4
    except (Latched, DataError) as e:
        err("STOP (data): %s" % e)
        return 2


def main(argv=None):
    a = make_parser().parse_args(argv)
    if a.cmd == "selftest":
        return selftest(mutants=not a.no_mutants, only=a.mutant)
    return dispatch(a)


# ==============================================================================================================================
# SELFTEST: synthetic data only. Every number below is invented (rates 9.xx, volumes 10^11 and 10^12 plus a day count); nothing is read from any site.
# Every guard applies its own mutants one at a time; an uncaught mutant fails the selftest.
# ==============================================================================================================================
class Checks(object):
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


@contextlib.contextmanager
def patched(**kw):
    g = globals()
    old = {k: g[k] for k in kw}
    g.update(kw)
    try:
        yield
    finally:
        g.update(old)


UTC = dt.timezone.utc
T_PRE = dt.datetime(2026, 11, 2, 12, 0, 0, tzinfo=UTC)                  # today: before the gate
T_GATE = dt.datetime(2027, 1, 5, 20, 0, 0, tzinfo=UTC)
T_POST = dt.datetime(2027, 1, 5, 20, 30, 0, tzinfo=UTC)
HOLS = frozenset(D(x) for x in FED_HOLIDAYS)


def dset(xs):
    return set(D(x) if isinstance(x, str) else x for x in (xs or ()))


def bizdays(a, b):
    out, t, end = [], D(a), D(b)
    while t <= end:
        if t.weekday() < 5 and t not in HOLS:
            out.append(t)
        t += dt.timedelta(1)
    return out


def cents(c):
    return "%d.%02d" % divmod(c, 100)


def jtxt(pairs):
    return ("[" + ",".join('["%s",%s]' % (t.isoformat(), "null" if v is None else v) for t, v in pairs) + "]").encode("utf-8")


def synth_world(end=END_CAP, s_over=None, oo_over=None, flat=True, drop=(), drop_b27=(), drop_oo=(), null_b27=(), null_oo=(), fin_b27=None):
    """Nine invented series. OO is 9.20 (flat) and B27 = OO + S with S = 4 bp unless overridden, so every expected value below can be worked by hand."""
    s_over = {D(k) if isinstance(k, str) else k: v for k, v in (s_over or {}).items()}
    oo_over = {D(k) if isinstance(k, str) else k: v for k, v in (oo_over or {}).items()}
    fin_b27 = {D(k) if isinstance(k, str) else k: v for k, v in (fin_b27 or {}).items()}
    drop, drop_b27, drop_oo, null_b27, null_oo = dset(drop), dset(drop_b27), dset(drop_oo), dset(null_b27), dset(null_oo)
    d_oo = [t for t in bizdays("2025-08-01", end) if t not in drop and t not in drop_oo]
    d_b = [t for t in bizdays("2025-08-13", end) if t not in drop and t not in drop_b27]
    oo_c = lambda t: 920 + (0 if flat else t.toordinal() % 3) + oo_over.get(t, 0)
    s_c = lambda t: s_over.get(t, 4 + (0 if flat else t.toordinal() % 3))
    w = {}
    w[MN_OO] = jtxt([(t, None if t in null_oo else cents(oo_c(t))) for t in d_oo])
    w[MN_B27] = jtxt([(t, None if t in null_b27 else cents(oo_c(t) + s_c(t))) for t in d_b])
    w[MN_TVB] = jtxt([(t, str(200000000000 + t.toordinal())) for t in d_b])
    w[MN_TVO] = jtxt([(t, str(1000000000000 + 3 * t.toordinal())) for t in d_oo])
    w[MN_B830] = jtxt([(t, None if i % 14 == 13 else cents(oo_c(t) + 9)) for i, t in enumerate(d_b)])
    cut = lambda ds: [t for t in ds if t <= FINALS_THROUGH]
    w[FINALS[0]] = jtxt([(t, None if t in null_b27 else cents(fin_b27.get(t, oo_c(t) + s_c(t)))) for t in cut(d_b)])
    w[FINALS[1]] = jtxt([(t, None if t in null_oo else cents(oo_c(t))) for t in cut(d_oo)])
    w[FINALS[2]] = jtxt([(t, str(200000000000 + t.toordinal())) for t in cut(d_b)])
    w[FINALS[3]] = jtxt([(t, str(1000000000000 + 3 * t.toordinal())) for t in cut(d_oo)])
    return w


def data_of(world):
    return Data(*(parse_series(world[m], m) for m in PRELIM[:4]), parse_series(world[MN_B830], MN_B830))


def write_vintage(root, v, world, at="2027-01-05T20:30:00Z", vroot=None):
    vd = os.path.join(vroot or os.path.join(root, VROOT_REL), v)
    rows = []
    for mn in ALL_MN:
        write_bytes(os.path.join(vd, mn + ".json"), world[mn])
        rows.append(["https://%s%s?%s" % (HOST, API_PATH, series_url(mn, False)), sha256_of(world[mn]), str(len(world[mn])), at])
    write_text(os.path.join(vd, "MANIFEST.csv"), csv_text(MANIFEST_HEAD, rows))
    return vd


class Args(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __getattr__(self, k):
        return None


def swap_line(tag, line, text=None):
    text = PREREG_BLOCK if text is None else text
    out = [line if l.startswith(tag + "|") else l for l in text.split("\n")]
    return "\n".join(out)


def p_with(**kw):
    t = PREREG_BLOCK
    if "fomc" in kw:
        t = swap_line("FOMC", "FOMC|effective=" + ",".join(kw["fomc"]), t)
    if "min_k" in kw:
        t = t.replace("at_least_5_K_days", "at_least_%d_K_days" % kw["min_k"])
    return parse_prereg(t)


def det(t):
    return t.isoformat() if hasattr(t, "isoformat") else t


def row_for(rows, T):
    return [r for r in rows if r["t"] == D(T)][0]


NOGIT = lambda root: (0, "")                                              # git history empty
SOMEGIT = lambda root: (0, "0123456789abcdef0123456789abcdef01234567\n")  # one earlier commit touched registered.csv


def quiet():
    lines = []
    return lines, lines.append


# ---- G1: calendar -------------------------------------------------------------------------------------------------------
def t_g1(ck):
    w = synth_world()
    d = data_of(w)
    for T, want in (("2026-08-31", "2026-08-28"), ("2026-01-20", "2026-01-16"), ("2026-09-08", "2026-09-04")):
        r = assess(D(T), "described", d, PR, T_PRE)
        ck.eq("T-1 of %s across a weekend%s is %s" % (T, " and a holiday" if T != "2026-08-31" else "", want), det(r["t_minus_1"]), want)
    # null and one-series dates are not business days
    w2 = synth_world(drop_oo=["2026-08-12"], drop_b27=["2026-08-13"], null_b27=["2026-08-14"], null_oo=["2026-08-18"])
    d2 = data_of(w2)
    for x in ("2026-08-12", "2026-08-13", "2026-08-14", "2026-08-18"):
        ck.ok("%s is not a business day (present in one series only, or null in one)" % x, D(x) not in d2.bizset)
    ck.ok("an ordinary date is a business day", D("2026-08-19") in d2.bizset)
    k = k_days(D("2026-08-31"), d2, PR)
    ck.ok("dropped dates are not control days", not (set(k) & dset(["2026-08-12", "2026-08-13", "2026-08-14", "2026-08-18"])), str(k))
    # an incomplete series date is not turned into a zero or a day
    w3 = synth_world(null_oo=["2026-08-28"])
    r3 = assess(D("2026-08-31"), "placebo", data_of(w3), PR, T_PRE)
    ck.eq("a null T-1 on a non-target turn is NOT_ASSESSED", r3["status"], "NOT_ASSESSED")


# ---- G2: control days ---------------------------------------------------------------------------------------------------
def t_g2(ck):
    d = data_of(synth_world())
    aug = lambda xs: set(D("2026-08-%02d" % x) for x in xs)
    k = set(k_days(D("2026-08-31"), d, PR))
    ck.eq("K(31 Aug 2026) is 3-14, 18-21 and 24 Aug: the 17th (a Saturday 15th rolls to Monday) is out", k, aug([3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 18, 19, 20, 21, 24]))
    ck.ok("T-t = 7 (24 Aug) is in K", D("2026-08-24") in k)
    ck.ok("T-t = 6 (25 Aug) is not in K", D("2026-08-25") not in k)
    P1 = p_with(fomc=["2026-08-19"])
    ck.ok("an FOMC date at calendar t+7 excludes t", D("2026-08-12") not in k_days(D("2026-08-31"), d, P1))
    ck.ok("...and at t+1 excludes it", D("2026-08-18") not in k_days(D("2026-08-31"), d, P1))
    P2 = p_with(fomc=["2026-08-20"])
    ck.ok("an FOMC date at calendar t+8 keeps t", D("2026-08-12") in k_days(D("2026-08-31"), d, P2))
    P3 = p_with(fomc=["2026-08-12"])
    ck.ok("an FOMC date at t itself keeps t", D("2026-08-12") in k_days(D("2026-08-31"), d, P3))
    kf = set(k_days(D("2026-02-27"), d, PR))
    ck.ok("15 Feb 2026 is a Sunday and 16 Feb a holiday: 17 Feb is the coupon day and is out", D("2026-02-17") not in kf and D("2026-02-13") in kf and D("2026-02-18") in kf, str(sorted(kf)))
    ko = set(k_days(D("2025-10-31"), d, PR))
    ck.ok("when the 15th is a business day it is out", D("2025-10-15") not in ko and D("2025-10-14") in ko)
    km = k_days(D("2026-05-29"), d, PR)
    ck.ok("the 22 May 2026 early close is out of K", D("2026-05-22") not in km)
    ck.ok("...and V3 restores it", D("2026-05-22") in k_days(D("2026-05-29"), d, PR, restore_early=True))
    dec = [t.day for t in k_days(D("2026-12-31"), d, PR)]
    ck.eq("K(31 Dec 2026) is 1, 2, 10, 11, 14, 16, 17, 18, 21, 22, 23 Dec (R1-5)", dec, [1, 2, 10, 11, 14, 16, 17, 18, 21, 22, 23])
    sep = [t.day for t in k_days(D("2026-09-30"), d, PR)]
    ck.eq("K(30 Sep 2026): the FOMC 17 Sep date at t keeps the 17th", sep, [1, 2, 3, 4, 8, 9, 17, 18, 21, 22, 23])
    ck.ok("all days of another month stay out", all(t.month == 12 for t in k_days(D("2026-12-31"), d, PR)))


# ---- G3: statuses -------------------------------------------------------------------------------------------------------
def t_g3(ck):
    sep_k = ["2026-09-%02d" % x for x in (1, 2, 3, 4, 8, 9, 17)]
    d4 = data_of(synth_world(drop=sep_k))
    r = assess(D("2026-09-30"), "quarter", d4, PR, T_PRE)
    ck.eq("|K| = 4 is NOT_ASSESSED", (r["status"], r["n_k"]), ("NOT_ASSESSED", 4))
    d5 = data_of(synth_world(drop=sep_k[:-1]))
    r = assess(D("2026-09-30"), "quarter", d5, PR, T_PRE)
    ck.eq("|K| = 5 is assessed", (r["status"], r["n_k"]), ("OK", 5))
    P6 = p_with(min_k=6)
    ck.eq("the minimum comes from the block: with 'at least 6', |K| = 5 is NOT_ASSESSED", assess(D("2026-09-30"), "quarter", d5, P6, T_PRE)["status"], "NOT_ASSESSED")
    # incomplete T: data ending 28 Oct 2026
    rows = evaluate_all(data_of(synth_world(end="2026-10-28")), PR, T_PRE)
    pend = [r["t"].isoformat() for r in rows if r["status"] == "PENDING"]
    ck.eq("on data ending 28 Oct 2026, 14 of 17 turns are complete and Oct, Nov and Dec 2026 are PENDING", (len(rows) - len(pend), pend), (14, ["2026-10-30", "2026-11-30", "2026-12-31"]))
    ck.eq("the 17 turns are 5 quarter, 8 placebo, 3 described and 1 target", sorted((k, sum(1 for r in rows if r["kind"] == k)) for k in ("quarter", "placebo", "described", "target")),
          [("described", 3), ("placebo", 8), ("quarter", 5), ("target", 1)])
    # the target
    wp = synth_world(end="2027-01-05", null_b27=["2026-12-30"])
    rt = lambda now, world=wp: row_for(evaluate_all(data_of(world), PR, now), "2026-12-31")
    ck.eq("a null T-1 on the target is PENDING", rt(T_POST)["status"], "PENDING")
    ck.eq("...and is NOT_ASSESSED after 29 Jan 2027", rt(dt.datetime(2027, 1, 30, 9, 0, tzinfo=UTC))["status"], "NOT_ASSESSED")
    ck.eq("...and is still PENDING on 29 Jan 2027", rt(dt.datetime(2027, 1, 29, 23, 0, tzinfo=UTC))["status"], "PENDING")
    wd = synth_world(end="2027-01-05", drop=["2026-12-30"])
    ck.eq("a missing T-1 on the target is PENDING", rt(T_POST, wd)["status"], "PENDING")
    ck.eq("the target before the gate is PENDING with every value empty even when the data are there", [(r["status"], r["e"], r["db"], r["ot"], r["tick_sensitive"]) for r in evaluate_all(data_of(synth_world(end="2027-01-05")), PR, T_GATE - dt.timedelta(seconds=1)) if r["kind"] == "target"],
          [("PENDING", None, None, None, None)])
    ck.eq("...and is computed at the gate", rt(T_GATE, synth_world(end="2027-01-05"))["status"], "OK")
    # VOID at six placebo months
    mk = lambda mm: ["%s" % t for t in sorted(set(t.isoformat() for t in k_days(D(mm), data_of(synth_world()), PR))) ][:-4]
    w6 = synth_world(drop=mk("2025-11-28") + mk("2026-02-27"))
    r6 = evaluate_all(data_of(w6), PR, T_PRE)
    ck.eq("two placebo months with |K| = 4 leave 6 assessed", placebo_range(r6)[2], 6)
    w7 = synth_world(drop=mk("2025-11-28"))
    ck.eq("one such month leaves 7 assessed", placebo_range(evaluate_all(data_of(w7), PR, T_PRE))[2], 7)
    ck.eq("6 assessed placebo months make the label VOID", label_of("OK", Fraction(5), Fraction(0), Fraction(1), 6, PR), "VOID")
    ck.eq("7 assessed placebo months do not", label_of("OK", Fraction(5), Fraction(0), Fraction(1), 7, PR), "ABOVE")


# ---- G4: label ---------------------------------------------------------------------------------------------------------
def t_g4(ck):
    F = Fraction
    L = lambda e, lo, hi: label_of("OK", F(e), F(lo), F(hi), 8, PR)
    ck.eq("E equal to the maximum is INSIDE", L(3, -2, 3), "INSIDE")
    ck.eq("E just above the maximum and positive is ABOVE", L(F(7, 2), -2, 3), "ABOVE")
    ck.eq("E above the maximum but not positive is INSIDE", L(-1, -5, -2), "INSIDE")
    ck.eq("E = 0 above a negative maximum is INSIDE", L(0, -5, -1), "INSIDE")
    ck.eq("E equal to the minimum is INSIDE", L(-2, -2, 3), "INSIDE")
    ck.eq("E just below the minimum and negative is BELOW", L(-3, -2, 3), "BELOW")
    ck.eq("E below the minimum but not negative is INSIDE", L(1, 2, 5), "INSIDE")
    ck.eq("E = 0 below a positive minimum is INSIDE", L(0, 1, 5), "INSIDE")
    ck.eq("a PENDING turn is PENDING and a NOT_ASSESSED one NOT_ASSESSED", (label_of("PENDING", None, None, None, 0, PR), label_of("NOT_ASSESSED", None, None, None, 0, PR)), ("PENDING", "NOT_ASSESSED"))
    # tick sensitivity: a target one tick above a zero-width range flips to INSIDE if the control median moves one tick
    s = {"2026-12-30": 5}
    rows = evaluate_all(data_of(synth_world(end="2027-01-05", s_over=s)), PR, T_POST)
    t = row_for(rows, "2026-12-31")
    ck.eq("E = 1 over a range [0, 0] is tick sensitive", (fmt_fr(t["e"]), t["tick_sensitive"]), ("1.00", "yes"))
    rows = evaluate_all(data_of(synth_world(end="2027-01-05", s_over={"2026-12-30": 10})), PR, T_POST)
    t = row_for(rows, "2026-12-31")
    ck.eq("E = 6 over a range [0, 0] is not", (fmt_fr(t["e"]), t["tick_sensitive"]), ("6.00", "no"))


# ---- G5: values --------------------------------------------------------------------------------------------------------
def dec_world():
    """December 2026 with S set by hand: low (2) on 1, 2, 16, 17, 18; mid (6) on 21; high (9) on 10, 11, 14, 22, 23; the FOMC-window days 3, 4, 7, 8, 9 high; coupon and early-close days low."""
    s = {}
    for x in (1, 2, 16, 17, 18, 15, 24):
        s["2026-12-%02d" % x] = 2
    s["2026-12-21"] = 6
    for x in (10, 11, 14, 22, 23, 3, 4, 7, 8, 9):
        s["2026-12-%02d" % x] = 9
    s["2026-12-30"] = 10
    s["2026-12-28"] = 4
    s["2026-12-29"] = 4
    s["2026-12-31"] = 7
    return synth_world(end="2027-01-05", s_over=s, oo_over={"2026-12-30": 5, "2026-12-31": 30})


def t_g5(ck):
    F = Fraction
    ck.eq("median of two values is their exact mean", median([F("0.1"), F("0.2")]), F(3, 20))
    ck.ok("...and is a Fraction, not a float", isinstance(median([F("0.1"), F("0.2")]), Fraction))
    ck.eq("median of an odd count is the middle value", median([F(5), F(1), F(3)]), F(3))
    ck.eq("a rate string keeps its exact value", parse_series(b'[["2026-01-02", 9.35]]', "x").val[D("2026-01-02")], F(935, 100))
    ck.eq("fmt_fr rounds half to even and shows no negative zero", (fmt_fr(F(1, 8)), fmt_fr(F(-1, 1000)), fmt_fr(F(5, 2), 0), fmt_fr(F(7, 2), 0)), ("0.12", "0.00", "2", "4"))
    d = data_of(dec_world())
    r = row_for(evaluate_all(d, PR, T_POST), "2026-12-31")
    ck.eq("status OK with 11 control days", (r["status"], r["n_k"]), ("OK", 11))
    ck.eq("S(T-1) = 10 bp and the control median is 6", (fmt_fr(r["s_t1"]), fmt_fr(r["control_median"])), ("10.00", "6.00"))
    ck.eq("E = 4 bp", fmt_fr(r["e"]), "4.00")
    ck.eq("legs: dB = 9 bp, dO = 5 bp", (fmt_fr(r["db"]), fmt_fr(r["do"])), ("9.00", "5.00"))
    ck.eq("OT = 30 bp", fmt_fr(r["ot"]), "30.00")
    ck.eq("V1 (mean of S on 24 < t < T, 28-30 Dec: 4, 4, 10) minus the control median = 0", fmt_fr(r["v1"]), "0.00")
    ck.eq("V2 = S(T) - median = 1", fmt_fr(r["v2"]), "1.00")
    ck.eq("V3 (coupon and early close restored) = 10 - 2 = 8", fmt_fr(r["v3"]), "8.00")
    ck.eq("V4 (K limited to the 14th and earlier) = 10 - 9 = 1", fmt_fr(r["v4"]), "1.00")
    ck.eq("V5 (no FOMC exclusion) = 10 - 9 = 1", fmt_fr(r["v5"]), "1.00")
    ck.ok("V6 is defined where the 8-30 day print exists", r["v6"] is not None, str(r["v6"]))
    ck.eq("volumes: T-1 and the K mean are printed in whole units", (fmt_fr(r["tv_b27_t1"], 0), fmt_fr(r["tv_b27_k_mean"], 0)[:3]), (str(200000000000 + D("2026-12-30").toordinal()), "200"))
    ck.eq("E by a second code path equals E", e_second_path(D("2026-12-31"), d, PR), r["e"])
    rd = row_for(evaluate_all(d, PR, T_POST), "2026-04-30")
    ck.eq("a described month is computed like the others", rd["kind"], "described")
    # the daily flags
    txt = read_csv_dicts(daily_csv(d, PR))
    day = {x["date"]: x for x in txt}
    ck.eq("daily.csv flags the 15 Dec coupon, a Tuesday bill day, the 24 Dec early close and an FOMC-window day",
          (day["2026-12-15"]["coupon"], day["2026-12-15"]["bill"], day["2026-12-24"]["early"], day["2026-12-04"]["fomc_in_7d"], day["2026-12-17"]["fomc_in_7d"]), ("yes", "yes", "yes", "yes", "no"))
    ck.eq("daily.csv shows S in basis points on business days", day["2026-12-30"]["s_bp"], "10.00")


# ---- G6: the registered block ------------------------------------------------------------------------------------------
def t_g6(ck):
    b = PREREG_BLOCK.encode("utf-8")
    ck.eq("the embedded block is 1505 bytes and 10 lines, ending in one LF", (len(b), PREREG_BLOCK.count("\n"), PREREG_BLOCK.endswith("\n") and not PREREG_BLOCK.endswith("\n\n")), (SPEC_PREREG_BYTES, 10, True))
    ck.eq("it hashes to SPEC_PREREG_SHA256", sha256_of(b), SPEC_PREREG_SHA256)
    ck.ok("prereg_ok accepts the block", prereg_ok())
    ck.ok("prereg_ok refuses a block with one byte changed", not prereg_ok(PREREG_BLOCK.replace("at_least_5", "at_least_4")))
    ck.ok("...and one with a line removed", not prereg_ok("\n".join(PREREG_BLOCK.split("\n")[1:])))
    spec = os.path.join(ROOT, SPEC_FILE)
    if os.path.isfile(spec):
        t = read_file(spec, "r")
        i = t.index("### 4.2")
        a = t.index("```\n", i) + 4
        ck.eq("the block equals the interior of the spec's fence", t[a:t.index("```", a)], PREREG_BLOCK)
    p = PR
    ck.eq("constants parsed: 7 days, window 7, the 15th, 5 control days, 7 placebo months", (p.k_min_days, p.fomc_window, p.coupon_dom, p.min_k, p.min_placebo), (7, 7, 15, 5, 7))
    ck.eq("...8 placebo months, 11 FOMC dates, 7 early closes", (len(p.placebo_t), len(p.fomc), len(p.early)), (8, 11, 7))
    ck.eq("...target 2026-12-31 with T-1 2026-12-30, retry until 2027-01-29, gate 2027-01-05 20:00 UTC", (p.target_t.isoformat(), p.target_tm1.isoformat(), p.retry_until.isoformat(), iso_z(p.gate)),
          ("2026-12-31", "2026-12-30", "2027-01-29", "2027-01-05T20:00:00Z"))
    ck.eq("...and an edited FOMC line changes the parsed dates", len(p_with(fomc=["2026-08-19"]).fomc), 1)
    ck.eq("the 17 turn dates are distinct", len(set(all_turns(PR))), 17)
    ck.eq("every placebo T-1 is before its T", all(a < b for a, b in zip(PR.placebo_tm1, PR.placebo_t)), True)


# ---- G7: register ------------------------------------------------------------------------------------------------------
def reg_run(root, v, now, git=NOGIT, out=None):
    lines, say = quiet()
    a = Args(cmd="build", vintage=v, stage="register", out=out)
    err = []
    rc = dispatch(a, root=root, say=say, err=err.append, now_utc=lambda: now, git=git)
    return rc, lines, err


def t_g7(ck):
    world = dec_world()
    with tempfile.TemporaryDirectory(prefix="trt_g7_", ignore_cleanup_errors=True) as tmp:
        write_vintage(tmp, "20270105", world)
        regp = os.path.join(tmp, OUT_REL, REG_NAME)
        rc, lines, err = reg_run(tmp, "20270105", T_GATE - dt.timedelta(seconds=1))
        ck.eq("register refuses one second before the gate (exit 5) and writes nothing", (rc, os.path.exists(regp)), (5, False))
        ck.ok("...and says why", any("gate" in e for e in err), str(err))
        rc, lines, err = reg_run(tmp, "20270105", T_GATE)
        ck.eq("register writes at the gate itself (exit 0)", (rc, os.path.exists(regp)), (0, True))
        row = read_csv_dicts(read_file(regp, "r"))
        ck.eq("one row, the registered columns", (len(row), list(row[0].keys())), (1, REG_HEAD))
        r0 = row[0]
        ck.eq("the row: prereg hash, E 4.00, legs 9.00 and 5.00, OT 30.00", (r0["prereg_sha256"], r0["e"], r0["db"], r0["do"], r0["ot"]), (SPEC_PREREG_SHA256, "4.00", "9.00", "5.00", "30.00"))
        ck.eq("the row: 8 placebo months in [0.00, 0.00], label ABOVE", (r0["n_placebo"], r0["placebo_min"], r0["placebo_max"], r0["label"]), ("8", "0.00", "0.00", "ABOVE"))
        ck.eq("the row: t, t_minus_1, vintage", (r0["t"], r0["t_minus_1"], r0["vintage"]), ("2026-12-31", "2026-12-30", "20270105"))
        first = read_file(regp, "r")
        rc, lines, err = reg_run(tmp, "20270105", T_POST)
        ck.eq("a second run exits 5 and leaves the file byte-identical", (rc, read_file(regp, "r") == first), (5, True))
        rc, lines, err = reg_run(tmp, "20300101", T_POST)
        ck.eq("a vintage that does not exist refuses (exit 5) and does not crash", rc, 5)
        os.remove(regp)
        rc, lines, err = reg_run(tmp, "20270105", T_POST, git=SOMEGIT)
        ck.eq("an earlier version in git history refuses (exit 5) even when the file is gone", (rc, os.path.exists(regp)), (5, False))
        rc, lines, err = reg_run(tmp, "20270105", T_POST, git=lambda r: (128, "fatal: not a git repository"))
        ck.eq("a git history that cannot be read refuses (fail closed)", (rc, os.path.exists(regp)), (5, False))
        with patched(PREREG_BLOCK=PREREG_BLOCK.replace("at_least_5", "at_least_4")):
            rc, lines, err = reg_run(tmp, "20270105", T_POST)
            ck.eq("a changed embedded block refuses", (rc, os.path.exists(regp)), (5, False))
    with tempfile.TemporaryDirectory(prefix="trt_g7b_", ignore_cleanup_errors=True) as tmp:
        write_vintage(tmp, "20270104", world, at="2027-01-04T10:00:00Z")
        write_vintage(tmp, "20270105", world, at="2027-01-05T19:59:59Z")
        for v in ("20270104", "20270105"):
            rc, lines, err = reg_run(tmp, v, T_POST)
            ck.eq("a vintage with a file fetched before the gate is refused (%s)" % v, (rc, os.path.exists(os.path.join(tmp, OUT_REL, REG_NAME))), (5, False))
    with tempfile.TemporaryDirectory(prefix="trt_g7c_", ignore_cleanup_errors=True) as tmp:
        write_vintage(tmp, "20270105", synth_world(end="2027-01-05", drop=["2026-12-30"]))
        rc, lines, err = reg_run(tmp, "20270105", T_POST)
        ck.eq("a target with no T-1 print gives exit 6 and writes nothing", (rc, os.path.exists(os.path.join(tmp, OUT_REL, REG_NAME))), (6, False))
        ck.ok("...and the output says PENDING", any("PENDING" in l for l in lines), str(lines))
    with tempfile.TemporaryDirectory(prefix="trt_g7d_", ignore_cleanup_errors=True) as tmp:
        write_vintage(tmp, "20270105", synth_world(end="2027-01-05", drop=["2026-12-%02d" % x for x in (1, 2, 10, 11, 14, 16, 17)]))
        rc, lines, err = reg_run(tmp, "20270105", T_POST)
        ck.eq("a target with fewer than 5 control days is written as NOT_ASSESSED", (rc, read_csv_dicts(read_file(os.path.join(tmp, OUT_REL, REG_NAME), "r"))[0]["label"] if rc == 0 else None), (0, "NOT_ASSESSED"))


# ---- G8: fetch ---------------------------------------------------------------------------------------------------------
class FakeClock(object):
    def __init__(self, now):
        self.now, self.t, self.sleeps = now, 1000.0, []

    def utc(self):
        return self.now

    def mono(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


class FakeServer(object):
    """Stands in for data.financialresearch.gov: serves the invented world, records every request, and can refuse, send a page, skew its Date or add a later row."""

    def __init__(self, clock, world, status_at=None, body_at=None, date_skew=0, no_date=False, later=None):
        self.clock, self.world, self.status_at, self.body_at = clock, world, status_at or {}, body_at or {}
        self.date_skew, self.no_date, self.later = date_skew, no_date, later
        self.calls = []

    def __call__(self, host, target, headers, timeout, cap):
        self.calls.append((host, target, dict(headers), self.clock.t))
        i = len(self.calls)
        if i in self.status_at:
            return self.status_at[i], b"refused", {}
        if i in self.body_at:
            return 200, self.body_at[i], {"date": email.utils.format_datetime(self.clock.now, usegmt=True)}
        mn = re.search(r"mnemonic=([A-Za-z0-9_\-]+)", target).group(1)
        body = self.world[mn]
        if self.later and mn == MN_OO:
            body = body[:-1] + (',["%s",9.20]]' % self.later).encode()
        hd = {} if self.no_date else {"date": email.utils.format_datetime(self.clock.now + dt.timedelta(seconds=self.date_skew), usegmt=True)}
        return 200, body, hd


def fetch_run(tmp, clock, server, replace=False, sleep=None, vintage=None):
    lines, say = quiet()
    err = []
    a = Args(cmd="fetch", vintage=vintage, replace=replace, sleep=sleep)
    rc = dispatch(a, root=tmp, say=say, err=err.append, opener=server, now_utc=clock.utc, sleeper=clock.sleep, mono=clock.mono)
    return rc, lines, err


def t_g8(ck):
    world = synth_world()
    stop_rel = os.path.join(VROOT_REL, STOP_NAME)
    with tempfile.TemporaryDirectory(prefix="trt_g8a_", ignore_cleanup_errors=True) as tmp:
        clock = FakeClock(T_PRE)
        srv = FakeServer(clock, world)
        rc, lines, err = fetch_run(tmp, clock, srv)
        ck.eq("a pre-gate fetch makes nine requests and exits 0", (rc, len(srv.calls)), (0, 9))
        ck.ok("every pre-gate request carries end_date=today while the cap is ahead (the API refuses a future date)", all("&end_date=" + clock.utc().strftime("%Y-%m-%d") in c[1] for c in srv.calls), str([c[1] for c in srv.calls][:2]))
        ck.eq("after the cap has passed, end_date stays at the cap", series_url("REPO-TRIV1_AR_B27-P", True, "2026-12-30").rsplit("&end_date=", 1)[1], "2026-12-23")
        ck.eq("before it, end_date is today", series_url("REPO-TRIV1_AR_B27-P", True, "2026-11-02").rsplit("&end_date=", 1)[1], "2026-11-02")
        ck.ok("every request is a GET of https on the one host, with start_date and no key", all(c[0] == "data.financialresearch.gov" and c[1].startswith("/v1/series/timeseries?mnemonic=") and "start_date=2025-08-01" in c[1] and "key" not in c[1].lower() for c in srv.calls))
        starts = [c[3] for c in srv.calls]
        ck.ok("request starts are at least 3 seconds apart", all(b - a >= 3.0 for a, b in zip(starts, starts[1:])), str([round(b - a, 2) for a, b in zip(starts, starts[1:])]))
        ck.ok("the User-Agent is the neutral string, no address anywhere in any header", all(c[2]["User-Agent"] == USER_AGENT and not any(chr(64) in str(v) for v in c[2].values()) for c in srv.calls), str(srv.calls[0][2]))
        ck.eq("the source constant carries no at sign and is the CLAUDE.md string", (chr(64) in USER_AGENT, USER_AGENT), (False, "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"))
        vd = os.path.join(tmp, VROOT_REL, T_PRE.strftime("%Y%m%d"))
        man = manifest_rows(vd)
        ck.eq("MANIFEST.csv has nine rows with url, sha256, bytes and fetched_at", (len(man), list(man[0].keys())), (9, MANIFEST_HEAD))
        ck.ok("...and each file matches its sha256", all(sha256_of(read_file(os.path.join(vd, mn_of_url(r["url"]) + ".json"))) == r["sha256"] for r in man))
        srv2 = FakeServer(clock, world)
        rc, lines, err = fetch_run(tmp, clock, srv2)
        ck.eq("a second fetch on one day refuses (exit 5) with no request", (rc, len(srv2.calls)), (5, 0))
        rc, lines, err = fetch_run(tmp, clock, FakeServer(clock, world), replace=True)
        ck.eq("...unless --replace", rc, 0)
        rc, lines, err = fetch_run(tmp, clock, FakeServer(clock, world), vintage="20261101")
        ck.eq("a vintage that is not today's UTC date is refused", rc, 5)
        rc, lines, err = fetch_run(tmp, clock, FakeServer(clock, world), sleep="1")
        ck.eq("--sleep below 3 is refused", rc, 5)
        ck.raises("any other host is refused", Refused, lambda: check_url("www.sec.gov", API_PATH + "?mnemonic=X"))
    with tempfile.TemporaryDirectory(prefix="trt_g8b_", ignore_cleanup_errors=True) as tmp:
        clock = FakeClock(T_POST)
        srv = FakeServer(clock, synth_world(end="2027-01-05"))
        rc, lines, err = fetch_run(tmp, clock, srv)
        ck.eq("a post-gate fetch exits 0 and sends no end_date", (rc, any("end_date" in c[1] for c in srv.calls)), (0, False))
    with tempfile.TemporaryDirectory(prefix="trt_g8c_", ignore_cleanup_errors=True) as tmp:
        clock = FakeClock(T_PRE)
        srv = FakeServer(clock, world, later="2026-12-24")
        rc, lines, err = fetch_run(tmp, clock, srv)
        ck.eq("a pre-gate response holding a later date is refused and nothing is written", (rc, os.path.exists(os.path.join(tmp, VROOT_REL, T_PRE.strftime("%Y%m%d")))), (5, False))
    for label, kw in (("two hours ahead", dict(date_skew=7200)), ("two hours behind", dict(date_skew=-7200)), ("absent", dict(no_date=True))):
        with tempfile.TemporaryDirectory(prefix="trt_g8d_", ignore_cleanup_errors=True) as tmp:
            clock = FakeClock(T_PRE)
            rc, lines, err = fetch_run(tmp, clock, FakeServer(clock, world, **kw))
            ck.eq("an HTTP Date %s refuses (exit 5), nothing written" % label, (rc, os.path.exists(os.path.join(tmp, VROOT_REL, T_PRE.strftime("%Y%m%d")))), (5, False))
    with tempfile.TemporaryDirectory(prefix="trt_g8e_", ignore_cleanup_errors=True) as tmp:
        clock = FakeClock(T_PRE)
        rc, lines, err = fetch_run(tmp, clock, FakeServer(clock, world, date_skew=3000))
        ck.eq("an HTTP Date 50 minutes off is accepted", rc, 0)
    for label, kw, why in (("a 403", dict(status_at={3: 403}), "403"), ("a 429", dict(status_at={3: 429}), "429"), ("a redirect", dict(status_at={3: 302}), "non-200"),
                           ("a 200 bot-check page", dict(body_at={3: b"<html><title>Just a moment...</title>checking your browser</html>"}), "bot check")):
        with tempfile.TemporaryDirectory(prefix="trt_g8f_", ignore_cleanup_errors=True) as tmp:
            clock = FakeClock(T_PRE)
            srv = FakeServer(clock, world, **kw)
            rc, lines, err = fetch_run(tmp, clock, srv)
            sp = os.path.join(tmp, stop_rel)
            ck.eq("%s on request 3 stops the fetch: exit 2, STOP_term_repo written, no further request" % label, (rc, os.path.exists(sp), len(srv.calls)), (2, True, 3))
            ck.ok("...it says which (%s) and writes nothing else" % why, any(why in l for l in lines) and not os.path.exists(os.path.join(tmp, VROOT_REL, T_PRE.strftime("%Y%m%d"))), str(lines[-1:]))
            srv2 = FakeServer(clock, world)
            rc2, _, _ = fetch_run(tmp, clock, srv2, replace=True)
            ck.eq("with the STOP file present, the next fetch makes no request (exit 2)", (rc2, len(srv2.calls)), (2, 0))
    with tempfile.TemporaryDirectory(prefix="trt_g8g_", ignore_cleanup_errors=True) as tmp:
        clock = FakeClock(T_PRE)

        def boom(host, target, headers, timeout, cap):
            raise SocketFault("TimeoutError")
        rc, lines, err = fetch_run(tmp, clock, boom)
        ck.eq("a socket fault exits 3 and latches nothing", (rc, os.path.exists(os.path.join(tmp, stop_rel))), (3, False))
    src = read_file(os.path.abspath(__file__), "r")
    ck.ok("the script never deletes, renames over or truncates a STOP path (static scan)", not re.search(r"(os\.(remove|unlink|rename)|shutil\.rmtree|os\.replace)\([^)]*STOP", src))


# ---- G9: stages and README ----------------------------------------------------------------------------------------------
def stage_run(tmp, v, stage, now=T_PRE, git=NOGIT, **kw):
    lines, say = quiet()
    err = []
    rc = dispatch(Args(cmd="build", vintage=v, stage=stage, **kw), root=tmp, say=say, err=err.append, now_utc=lambda: now, git=git)
    return rc, lines, err


def t_g9(ck):
    rate_rx = re.compile(r"\b9\.\d{1,3}\b")
    world = synth_world(drop=["2026-04-02"], flat=False)
    with tempfile.TemporaryDirectory(prefix="trt_g9_", ignore_cleanup_errors=True) as tmp:
        write_vintage(tmp, "20261102", world, at="2026-11-02T12:00:00Z")
        rc, lines, err = stage_run(tmp, "20261102", "pre")
        out = "\n".join(lines)
        ck.eq("pre exits 0", rc, 0)
        ck.ok("pre output holds no rate (no 9.xx token) and no spread", not rate_rx.search(out) and not re.search(r"[-+]\d+\.\d\d\b", out), out[:300])
        ck.ok("pre output holds no volume digits (only the order of magnitude)", "2000000" not in out and "1000000000" not in out, out[:300])
        ck.ok("pre reports the decimals, the span, nulls and the order of magnitude", "decimals in the B27 rate strings: 2" in out and "10^12" in out and "nulls" in out, out[:400])
        ck.ok("pre names a weekday absent from both series that is not a federal holiday", "2026-04-02" in out, out[-300:])
        rc, lines, err = stage_run(tmp, "20261102", "dry")
        out = "\n".join(lines)
        ck.eq("dry exits 0", rc, 0)
        ck.ok("dry holds no rate and no spread", not rate_rx.search(out) and not re.search(r"[-+]\d+\.\d\d\b", out), out[:300])
        ck.ok("dry shows |K| = 11 for 31 Dec 2026 and its control days", re.search(r"2026-12-31\s+target\s+2026-12-30\s+match\s+11", out) is not None and "(11): 1 2 10 11 14 16 17 18 21 22 23" in out, out[-900:])
        ck.ok("dry shows the placebo T-1 matches", len(re.findall(r"placebo\s+\S+\s+match", out)) == 8, out[:900])
        ck.ok("dry shows register refusing", "register would REFUSE" in out and "gate" in out, out[-300:])
        # the FOMC recheck
        page = "2026 FOMC Meetings\nJanuary\n27-28\nMarch\n17-18\nApril\n28-29\nJune\n16-17\nJuly\n28-29\nSeptember\n15-16\nOctober\n27-28\nDecember\n8-9\n2025 FOMC Meetings\nOctober\n28-29\nDecember\n9-10\nSeptember\n16-17\n"
        pf = os.path.join(tmp, "fomc.txt")
        write_text(pf, page)
        rc, lines, err = stage_run(tmp, "20261102", "dry", fomc_page=pf)
        out = "\n".join(lines)
        ck.ok("the FOMC recheck agrees with the fence on a matching page", "the page and the fence agree" in out, out[-500:])
        write_text(pf, page.replace("December\n8-9", "December\n7-8"))
        rc, lines, err = stage_run(tmp, "20261102", "dry", fomc_page=pf)
        ck.ok("...and a changed meeting date warns", any("FOMC recheck differs" in l for l in lines), "\n".join(lines)[-400:])
        # describe
        outd = os.path.join(tmp, "out")
        rc, lines, err = stage_run(tmp, "20261102", "describe", out=outd)
        names = sorted(os.listdir(outd)) if os.path.isdir(outd) else []
        ck.eq("describe writes the five outputs and no registered.csv", (rc, names), (0, ["README.md", "checks.csv", "daily.csv", "revisions.csv", "turns.csv"]))
        if rc == 0:
            tr = read_csv_dicts(read_file(os.path.join(outd, "turns.csv"), "r"))
            ck.eq("turns.csv: the header, 17 rows", (list(tr[0].keys()), len(tr)), (TURNS_HEAD, 17))
            tg = [r for r in tr if r["kind"] == "target"][0]
            ck.eq("the target row is PENDING with every value empty", (tg["status"], [k for k, v in tg.items() if v and k not in ("t", "t_minus_1", "kind", "status")]), ("PENDING", []))
            ck.eq("daily.csv header", list(read_csv_dicts(read_file(os.path.join(outd, "daily.csv"), "r"))[0].keys()), DAILY_HEAD)
            ck.eq("checks.csv header", list(read_csv_dicts(read_file(os.path.join(outd, "checks.csv"), "r"))[0].keys()), CHECKS_HEAD)
            readme = read_file(os.path.join(outd, "README.md"), "r")
            ck.eq("the generated README passes its own guard", readme_problems(readme), [])
            ck.ok("the README leads with the numbers, then the limits, then how to rerun", readme.index(SECTIONS[0]) < readme.index(SECTIONS[1]) < readme.index(SECTIONS[2]))
            ck.ok("the README never says charge, premium or a cause", not FORBIDDEN_RX.search(readme), str(FORBIDDEN_RX.search(readme)))
            ck.ok("the README states the R2-4 limit and the open-repo limit", LIMITS[7] in readme and LIMITS[3] in readme)
            ck.ok("the README says dB minus dO need not equal E", "need not equal E" in readme)
            ck.ok("the README prints the queued December statement as PENDING", "is PENDING" in readme)
        # revisions between two vintages
        w2 = synth_world(drop=["2026-04-02"], flat=False, s_over={"2025-10-30": 9})
        write_vintage(tmp, "20261103", w2, at="2026-11-03T12:00:00Z")
        rc, lines, err = stage_run(tmp, "20261103", "describe", out=outd, vs="20261102")
        rv = read_csv_dicts(read_file(os.path.join(outd, "revisions.csv"), "r"))
        ck.eq("revisions.csv carries the columns", list(rv[0].keys()), REV_HEAD)
        moved = [r for r in rv if r["vintage_a"] == "20261102" and r["field"] == "e" and r["a"] != r["b"]]
        ck.ok("...and shows the placebo month whose S changed between vintages", [r["t"] for r in moved] == ["2025-10-31"], str(moved))
    # the README guard on bad text
    good = readme_text(evaluate_all(data_of(synth_world()), PR, T_PRE), "x", PR, [], 0)
    ck.eq("readme_problems is empty on a generated README", readme_problems(good), [])
    for label, bad in (("a premium", good + "\nA premium for the date.\n"), ("a charge", good + "\nlenders charged more\n"), ("a cause", good + "\nit was caused by balance sheets\n"), ("a missing limit", good.replace(LIMITS[7], "")),
                       ("sections out of order", good.replace("## What this cannot say", "## TMP").replace("## How to rerun", "## What this cannot say").replace("## TMP", "## How to rerun"))):
        ck.ok("readme_problems catches %s" % label, bool(readme_problems(bad)), label)


# ---- G10: pinned checks ------------------------------------------------------------------------------------------------
def checks_of(world, now=T_PRE, fin_ok=True, at="2026-11-02T12:00:00Z"):
    with tempfile.TemporaryDirectory(prefix="trt_g10_", ignore_cleanup_errors=True) as tmp:
        vd = write_vintage(tmp, "20261102", world, at=at)
        d, fin, man = load_vintage(vd)
        rows = evaluate_all(d, PR, now)
        return {c[0]: c for c in pinned_checks(d, fin, rows, PR, man, now)}


def t_g10(ck):
    c = checks_of(synth_world())
    ck.ok("a clean synthetic vintage passes every pinned check", not [k for k, v in c.items() if v[1] == "FAIL"], str([v for v in c.values() if v[1] == "FAIL"]))
    ck.eq("the second-code-path check ran and passed", c["second_path_e"][1], "PASS")
    c = checks_of(synth_world(end="2026-09-30"))
    ck.eq("row counts below the spec's minimums fail", c["rows_" + MN_B27][1], "PASS" if len(bizdays("2025-08-13", "2026-09-30")) >= 302 else "FAIL")
    short = synth_world(end="2026-05-29")
    c = checks_of(short)
    ck.ok("a vintage that ends early fails the row-count check", c["rows_" + MN_B27][1] == "FAIL" and c["rows_" + MN_OO][1] == "FAIL", str(c["rows_" + MN_B27]))
    ck.eq("a first B27 date other than 2025-08-13 fails", checks_of(synth_world(drop_b27=["2025-08-13"]))["first_b27_date"][1], "FAIL")
    c = checks_of(synth_world(drop_oo=["2026-09-30"], drop_b27=["2026-09-30"]))
    ck.eq("a complete T missing from the overnight series fails", c["complete_t_in_oo"][1], "FAIL")
    c = checks_of(synth_world(drop_oo=["2026-02-26"], drop_b27=["2026-02-26"]))
    ck.eq("a placebo T-1 that is not the previous overnight date fails", c["fence_t_minus_1"][1], "FAIL")
    c = checks_of(synth_world(drop_oo=["2026-03-02"], drop_b27=["2026-03-02"]))
    ck.eq("a one-day hole elsewhere does not trip the fence check", c["fence_t_minus_1"][1], "PASS")
    w = synth_world()
    w[FINALS[1]] = re.sub(rb'\["2026-03-03",[^\]]*\],?', b"", w[FINALS[1]], count=1)
    ck.eq("finals and preliminary with different dates up to 2026-06-30 fail", checks_of(w)["finals_cover"][1], "FAIL")
    w = synth_world(end="2027-01-05")
    ck.eq("a vintage fetched before the gate that holds a later date fails the cap check", checks_of(w, at="2026-11-02T12:00:00Z")["pre_gate_cap"][1], "FAIL")
    ck.ok("...and a post-gate vintage has no cap check", "pre_gate_cap" not in checks_of(w, now=T_POST, at="2027-01-05T20:30:00Z"))
    with tempfile.TemporaryDirectory(prefix="trt_g10b_", ignore_cleanup_errors=True) as tmp:
        write_vintage(tmp, "20261102", short, at="2026-11-02T12:00:00Z")
        rc, lines, err = stage_run(tmp, "20261102", "describe", out=os.path.join(tmp, "out"))
        ck.ok("describe on a failing vintage exits 4", rc == 4, "rc %s %s" % (rc, err))
    with tempfile.TemporaryDirectory(prefix="trt_g10c_", ignore_cleanup_errors=True) as tmp:
        write_vintage(tmp, "20261102", synth_world(), at="2026-11-02T12:00:00Z")
        p = os.path.join(tmp, VROOT_REL, "20261102", MN_OO + ".json")
        write_bytes(p, read_file(p) + b" ")
        rc, lines, err = stage_run(tmp, "20261102", "pre")
        ck.eq("a file that no longer matches its MANIFEST row is a structural fault (exit 4)", rc, 4)
        write_bytes(p, b"<html>not json</html>")
        rc, lines, err = stage_run(tmp, "20261102", "pre")
        ck.eq("a non-JSON file is a structural fault (exit 4)", rc, 4)
    for label, body in (("a duplicate date", b'[["2026-01-02",9.1],["2026-01-02",9.2]]'), ("a bad date", b'[["2026-13-02",9.1]]'), ("a non-number", b'[["2026-01-02","abc"]]'), ("a boolean", b'[["2026-01-02",true]]'),
                        ("a triple", b'[["2026-01-02",9.1,3]]'), ("NaN", b'[["2026-01-02",NaN]]'), ("an object", b'{"a":1}')):
        ck.raises("parse_series rejects %s" % label, Structural, lambda b=body: parse_series(b, "x"))


# ---- G11: M30 end to end -----------------------------------------------------------------------------------------------
def m30_region():
    cs = read_file(os.path.join(ROOT, "bin", "check.sh"), "r")
    a0 = cs.find("term_repo_check() {")
    return cs[a0:cs.find("\n}\n", a0) + 3] if a0 >= 0 else ""


def m30_run(region, files=None, now="2026-11-02T12:00:00Z", reg_sha=None, script_text=None, absent=False):
    with tempfile.TemporaryDirectory(prefix="trt_m30_", ignore_cleanup_errors=True) as tmp:
        d = os.path.join(tmp, "data")
        if not absent:
            os.makedirs(d)
            for n, t in (files or {}).items():
                with open(os.path.join(d, n), "w", encoding="utf-8", newline="") as fh:
                    fh.write(t)
        sp = os.path.join(tmp, "s.py")
        with open(sp, "w") as fh:
            fh.write(script_text if script_text is not None else 'SPEC_PREREG_SHA256 = "%s"\n' % SPEC_PREREG_SHA256)
        sh = os.path.join(tmp, "m30.sh")
        with open(sh, "w") as fh:
            fh.write(region + "\nterm_repo_check\n")
        env = dict(os.environ, TERMREPO_DIR=d, TERMREPO_SCRIPT=sp, TERMREPO_NOW=now)
        if reg_sha is not None:
            env["TERMREPO_REG_SHA"] = reg_sha
        r = subprocess.run(["bash", sh], capture_output=True, text=True, timeout=60, env=env)
        return [l for l in r.stdout.splitlines() if "✗" in l], [l for l in r.stdout.splitlines() if "⚠" in l], r.stdout, r.stderr


def t_g11(ck):
    region = m30_region()
    ck.ok("check.sh holds term_repo_check", region.startswith("term_repo_check() {"))
    if M("m30_literal"):
        region = region.replace("0592b8ed", "0592b8ee")
    if M("m30_gate_inverted"):
        region = region.replace('now < GATE', 'now > GATE')
    if M("m30_empty_ok"):
        region = region.replace('bad.append("registered.csv is present but REG_SHA in check.sh is empty (the literal lands in the same commit as the file)")', 'pass')
    pend = TURNS_HEAD
    tg = lambda **kw: ",".join([kw.get(k, {"t": "2026-12-31", "t_minus_1": "2026-12-30", "kind": "target", "status": "PENDING"}.get(k, "")) for k in pend]) + "\n"
    hdr = ",".join(pend) + "\n"
    clean = {"turns.csv": hdr + tg()}
    cr, wr, out, err = m30_run(region, clean)
    ck.eq("M30 prints no cross on a clean pre-gate folder (empty REG_SHA, no registered.csv)", cr, [])
    ck.ok("...and a pass line", "✓" in out, out[:200] + err[:200])
    cr, wr, out, err = m30_run(region, absent=True)
    ck.eq("M30 passes when the folder does not exist", (cr, "absent" in out), ([], True))
    cr, wr, out, err = m30_run(region, {"turns.csv": hdr + tg(e="1.00")})
    ck.ok("a target value before the gate is a cross", any("target value" in c for c in cr), out)
    cr, wr, out, err = m30_run(region, {"turns.csv": hdr + tg(status="OK")})
    ck.ok("a target status other than PENDING before the gate is a cross", any("target value" in c for c in cr), out)
    cr, wr, out, err = m30_run(region, {"turns.csv": hdr + tg(e="1.00")}, now="2027-01-06T00:00:00Z")
    ck.eq("...but not after the gate", cr, [])
    cr, wr, out, err = m30_run(region, {"registered.csv": "x\n"})
    ck.ok("registered.csv before the gate is a cross", any("before the gate" in c for c in cr), out)
    reg = "prereg_sha256\nabc\n"
    sha = sha256_of(reg.encode())
    cr, wr, out, err = m30_run(region, {"registered.csv": reg}, now="2027-01-06T00:00:00Z", reg_sha=sha)
    ck.eq("registered.csv after the gate that hashes to REG_SHA: no cross", cr, [])
    cr, wr, out, err = m30_run(region, {"registered.csv": reg + "z\n"}, now="2027-01-06T00:00:00Z", reg_sha=sha)
    ck.ok("registered.csv that does not hash to REG_SHA is a cross", any("REG_SHA" in c for c in cr), out)
    cr, wr, out, err = m30_run(region, {"registered.csv": reg}, now="2027-01-06T00:00:00Z")
    ck.ok("registered.csv present with an empty REG_SHA is a cross", any("is empty" in c for c in cr), out)
    cr, wr, out, err = m30_run(region, {}, now="2027-01-30T00:00:00Z")
    ck.eq("registered.csv still absent after 29 Jan 2027 is a warning and no cross", (cr, len(wr)), ([], 1))
    cr, wr, out, err = m30_run(region, {}, now="2027-01-29T12:00:00Z")
    ck.eq("...and not yet on 29 Jan", (cr, wr), ([], []))
    cr, wr, out, err = m30_run(region, clean, script_text='SPEC_PREREG_SHA256 = "%s"\n' % ("f" + SPEC_PREREG_SHA256[1:]))
    ck.ok("a script whose prereg constant differs from the literal is a cross", any("prereg hash" in c for c in cr), out)


# ---- the table of guards and the runner --------------------------------------------------------------------------------
GUARDS = [
    ("G1", "calendar (T-1 across a weekend and a holiday; dates present in one series only or null are not business days)",
     ["tm1_calendar", "biz_union", "null_as_day"], t_g1),
    ("G2", "control days (T-t at 7 and 6; FOMC at t, t+7, t+8; coupon on a weekend and a holiday; early close; December and September exactly)",
     ["k_edge_gt", "fomc_left_closed", "fomc_window_short", "fomc_window_long", "coupon_no_roll", "early_kept", "k_other_month"], t_g2),
    ("G3", "statuses (NOT_ASSESSED at |K| = 4, PENDING for an incomplete T and a null T-1, the 29 Jan deadline, VOID at 6 placebo months, a blank target before the gate)",
     ["min_k_4", "no_deadline", "target_leak", "void_6"], t_g3),
    ("G4", "label edges and tick sensitivity", ["label_ge", "label_no_sign", "tick_off"], t_g4),
    ("G5", "values by hand (exact Fractions, even median, E, both legs, OT, V1 to V6, volumes, second code path)",
     ["float_median", "median_lower", "float_parse", "e_no_control"], t_g5),
    ("G6", "the registered block (bytes, lines, sha256, constants parsed from it)", ["prereg_nocheck"], t_g6),
    ("G7", "register (the gate to the second, a pre-gate vintage, O_EXCL, git history, a changed block, exit 6 on PENDING, NOT_ASSESSED written)",
     ["gate_off", "manifest_check_off", "excl_off", "git_off", "prereg_nocheck"], t_g7),
    ("G8", "fetch safety (end_date cap and a later date, Date against the clock, refusals stop the fetch, pacing, one host, neutral User-Agent, one fetch a day)",
     ["cap_url_missing", "cap_no_today", "cap_off", "skew_off", "skew_loose", "no_latch", "retry", "stop_ignored", "bot_ok", "pacing_off", "host_any", "ua_contact", "replace_off"], t_g8),
    ("G9", "stages and README (pre prints no rate, dry hides every value and shows |K| and T-1, FOMC recheck, describe writes no registered.csv, README wording and order)",
     ["pre_prints_rate", "dry_prints_value", "describe_writes_registered", "readme_guard_off", "readme_charge", "readme_drops_limit"], t_g9),
    ("G10", "pinned checks and malformed input (row counts, first date, complete T in OO, fence T-1, finals dates, cap, manifest hash, JSON shapes)",
     ["fence_check_off"], t_g10),
    ("G11", "M30 end to end (clean, absent, target value, registered.csv early, REG_SHA, the 29 Jan warning, a script literal)",
     ["m30_literal", "m30_gate_inverted", "m30_empty_ok"], t_g11),
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
    bad_total, n_checks, n_mut, n_caught = 0, 0, 0, 0
    if only:
        names = {m for _, _, ms, _ in GUARDS for m in ms}
        if only not in names:
            print("unknown mutant %r" % only)
            return 2
        with mutant(only):
            for gid, desc, muts, fn in GUARDS:
                ck = run_test(fn)
                bad = ck.failed()
                print("%-4s %s: %d checks, %s" % (gid, desc[:60], len(ck.items), "FAILED (%d)" % len(bad) if bad else "ok"))
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
        survived = 0
        if mutants:
            for m in muts:
                with mutant(m):
                    mk = run_test(fn)
                caught = bool(mk.failed())
                n_mut += 1
                n_caught += 1 if caught else 0
                bad_total += 0 if caught else 1
                survived += 0 if caught else 1
                print("       mutant %-26s %s%s" % (m, "caught" if caught else "SURVIVED", "  (first failing check: %s)" % mk.failed()[0][0][:70] if caught else ""))
        if not bad and not survived:
            print("       %s caught%s" % (gid, " (%d of %d mutants)" % (len(muts), len(muts)) if muts else " (no mutant)"))
    print("live guards: %s" % " ".join(g[0] for g in GUARDS))
    print("selftest: %d guards, %d checks, %d mutants applied one at a time, %d caught, %d failure(s), %.1f s" % (len(GUARDS), n_checks, n_mut, n_caught, bad_total, time.time() - t0))
    return 0 if bad_total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
