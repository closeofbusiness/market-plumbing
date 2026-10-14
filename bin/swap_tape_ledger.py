#!/usr/bin/env python3
"""Swap-tape ledger: daily swap-spread, CPI-swap gap and cross-currency-basis statistics from the DTCC public price
dissemination (PPD) CFTC cumulative interest-rate reports. Python 3 standard library only.

  python3 bin/swap_tape_ledger.py fetch --dates 2025-04-09,2026-09-29 | --start D --end D  [--cache DIR] [--sleep 5] [--max-requests 60]
  python3 bin/swap_tape_ledger.py fetch-ust --years 2025,2026         # Treasury par and real CSVs -> data/vintages/swap_tape_ust/
  python3 bin/swap_tape_ledger.py build --start D --end D [--cache DIR] [--out data/swap_tape] [--ust-dir DIR]
  python3 bin/swap_tape_ledger.py selftest                            # synthetic fixture, mutants, stop logic; no network

Specification: _research/2026-10-14-Swap-Tape-Ledger-Spec.md (section 17, the supervisor's amendments, overrides the sections above it).
Terms: THE_ASK.md E-024. The principal chose to script the DTCC PPD files despite DTCC's site terms, for NON-COMMERCIAL research only,
publishing derived statistics only (medians, quartiles, counts, shares) that cite DTCC. No DTCC file, row or identifier is committed or
redistributed: the zips live in a cache OUTSIDE the repository (default ~/dtcc_ppd/, override DTCC_PPD_CACHE or --cache; a cache inside
the repo is refused), are read in memory and are never extracted to disk. CC BY 4.0 covers only this project's computation.

What it does and does not touch:
  fetch / fetch-ust  the ONLY commands that use the network. Hosts: pddata.dtcc.com and home.treasury.gov, nothing else (sec.gov raises).
                     GET only; one request at a time; at least 5 seconds between request starts, persisted across invocations; a
                     neutral User-Agent with no address; redirects are not followed. Any HTTP status other than 200, or a body that is
                     not what was asked for, writes ~/dtcc_ppd/STOP and ends the run; every later fetch refuses while STOP exists and only
                     a human deletes it. A socket fault ends the invocation without latching. No retry, ever.
  build              offline and deterministic: reads cached zips and Treasury CSVs, upserts the rows of the weekdays it is given into
                     data/swap_tape/ (ledger, cells, funnel, diagnostics by year; file_stats, ust_used, summary, SOURCES.md).
  selftest           builds a synthetic tape (no DTCC content) and checks the exact funnel, medians, spreads, the stop logic (fake opener,
                     fake clock), the leak guards and three mutants (noconv, noeror, nowindow); it FAILS if a mutant is not detected.

THE RULES THE BUILD APPLIES (all stated, because a matching rule is a hypothesis; amended spec section 17 in brackets):
 1. One price per executed trade: NEWT rows with Event type TRAD; children (CORR/EROR/REVI) are resolved as in spec section 5; CORR tie-break
    = latest Event timestamp, then the larger Dissemination Identifier; MODI, TERM and NEWT of other Event types are ignored and counted.
 2. Series are identified by UPI FISN and UPI Underlier Name (Product name and Underlier ID are blank in the file). The fixed leg is the
    leg whose fixed rate is filled; its day count and payment frequency are read from either leg when its own are blank [A5].
 3. sofr_ois: F0 FISN/underlier, F1 executed on the file date (UTC), F2 spot start 0-5 days, F3 no upfront, F4 not post-priced and not
    non-standard, F4s no Strike Price, F5 exactly one fixed rate, F6 ACT/360 annual (A004; YEAR/1 or MNTH/12), F6u rate <= 0.25,
    F7 tenor bucket (expiry within +-7 days of effective + N years), F8 platform not BILT, F9 executed 14:30-16:30 New York [A1].
    Variants: headline = F0-F9 (n >= 10 to publish), fullday = F0-F8, all_platforms = F0-F7.
 4. spread_quoted_bp = median swap rate x 10,000 - CMT par x 100 (no conversion; the headline) [A2]. spread_bey_bp converts each trade
    to a semiannual bond-equivalent rate with its own accrual factor (Expiration - Effective days)/(360 N) before the median.
 5. cpi_zc minus the Treasury par breakeven is a gap between TWO instruments: gap_fisher_bp (headline) and gap_simple_bp [A3].
 6. xccy_*: spread on the non-USD leg of OIS-vs-SOFR cross-currency swaps in bp, per tenor (published at n >= 10) and pooled 1-5y [A4].
 7. Publication floor [A4]: n < 5 count only; 5 <= n < 10 count and median; n >= 10 also quartiles, IQR, IQR/sqrt(n) and shares. No min, no
    max, no weighted median, and no output field that is a whole string of 8-19 digits (a Dissemination Identifier).
"""
import argparse
import collections
import csv
import datetime as dt
import hashlib
import http.client
import io
import math
import os
import re
import sys
import tempfile
import time
import zipfile
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(ROOT, "data", "swap_tape")
UST_DEFAULT = os.path.join(ROOT, "data", "vintages", "swap_tape_ust")
CACHE_DEFAULT = "~/dtcc_ppd"
STOP_PATH = os.path.expanduser("~/dtcc_ppd/STOP")  # fixed, whatever --cache says (A8)

# A13: the CLAUDE.md canonical string for every non-SEC host. No address, no name.
UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
HEADERS = {"User-Agent": UA, "Accept-Encoding": "identity"}
HOSTS = {"pddata.dtcc.com": "/ppd/api/report/cumulative/cftc/",
         "home.treasury.gov": "/resource-center/data-chart-center/interest-rates/"}
DTCC_PREFIX = HOSTS["pddata.dtcc.com"]
TSY_TMPL = ("/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{y}/all?type={t}"
            "&field_tdr_date_value={y}&page&_format=csv")
TSY_KINDS = ("daily_treasury_yield_curve", "daily_treasury_real_yield_curve")
BODY_CAP = 50 * 1024 * 1024
TIMEOUT = 120
MIN_SLEEP = 5.0
HARD_CAP_REQUESTS = 100
HOLE_AGE_DAYS = 366
EARLIEST_DATE = dt.date(2024, 10, 11)   # the first date probed (404); nothing earlier is ever requested

# The header of the 13 Oct 2026 file, frozen only to log names added and removed (A11). Column NAMES, no data.
HEADER_V1 = (
    'Dissemination Identifier', 'Original Dissemination Identifier', 'Action type', 'Event type', 'Event timestamp',
    'Amendment indicator', 'Asset Class', 'Product name', 'Cleared', 'Mandatory clearing indicator',
    'Execution Timestamp', 'Effective Date', 'Expiration Date', 'Maturity date of the underlier',
    'Non-standardized term indicator', 'Platform identifier', 'Prime brokerage transaction indicator',
    'Block trade election indicator', 'Large notional off-facility swap election indicator', 'Notional amount-Leg 1',
    'Notional amount-Leg 2', 'Notional currency-Leg 1', 'Notional currency-Leg 2', 'Notional quantity-Leg 1',
    'Notional quantity-Leg 2', 'Total notional quantity-Leg 1', 'Total notional quantity-Leg 2',
    'Quantity frequency multiplier-Leg 1', 'Quantity frequency multiplier-Leg 2', 'Quantity unit of measure-Leg 1',
    'Quantity unit of measure-Leg 2', 'Quantity frequency-Leg 1', 'Quantity frequency-Leg 2',
    'Notional amount in effect on associated effective date-Leg 1',
    'Notional amount in effect on associated effective date-Leg 2', 'Effective date of the notional amount-Leg 1',
    'Effective date of the notional amount-Leg 2', 'End date of the notional amount-Leg 1',
    'End date of the notional amount-Leg 2', 'Call amount', 'Call currency', 'Put amount', 'Put currency',
    'Exchange rate', 'Exchange rate basis', 'First exercise date', 'Fixed rate-Leg 1', 'Fixed rate-Leg 2',
    'Option Premium Amount', 'Option Premium Currency', 'Price', 'Price unit of measure', 'Spread-Leg 1',
    'Spread-Leg 2', 'Spread currency-Leg 1', 'Spread currency-Leg 2', 'Strike Price',
    'Strike price currency/currency pair', 'Post-priced swap indicator', 'Price currency', 'Price notation',
    'Spread notation-Leg 1', 'Spread notation-Leg 2', 'Strike price notation',
    'Fixed rate day count convention-leg 1', 'Fixed rate day count convention-leg 2',
    'Floating rate day count convention-leg 1', 'Floating rate day count convention-leg 2',
    'Floating rate reset frequency period-leg 1', 'Floating rate reset frequency period-leg 2',
    'Floating rate reset frequency period multiplier-leg 1', 'Floating rate reset frequency period multiplier-leg 2',
    'Other payment amount', 'Fixed rate payment frequency period-Leg 1',
    'Floating rate payment frequency period-Leg 1', 'Fixed rate payment frequency period-Leg 2',
    'Floating rate payment frequency period-Leg 2', 'Fixed rate payment frequency period multiplier-Leg 1',
    'Floating rate payment frequency period multiplier-Leg 1', 'Fixed rate payment frequency period multiplier-Leg 2',
    'Floating rate payment frequency period multiplier-Leg 2', 'Other payment type', 'Other payment currency',
    'Settlement currency-Leg 1', 'Settlement currency-Leg 2', 'Settlement location', 'Collateralisation category',
    'Custom basket indicator', 'Index factor', 'Underlier ID-Leg 1', 'Underlier ID-Leg 2',
    'Underlier ID source-Leg 1', 'Underlying Asset Name',
    'Underlying asset subtype or underlying contract subtype-Leg 1',
    'Underlying asset subtype or underlying contract subtype-Leg 2', 'Embedded Option type', 'Option Type',
    'Option Style', 'Package indicator', 'Package transaction price', 'Package transaction price currency',
    'Package transaction price notation', 'Package transaction spread', 'Package transaction spread currency',
    'Package transaction spread notation', 'Physical delivery location-Leg 1', 'Delivery Type',
    'Unique Product Identifier', 'UPI FISN', 'UPI Underlier Name',
)
# The columns the build actually reads (A11): required by name, not by order. Everything else is ignored.
REQUIRED = (
    'Dissemination Identifier', 'Original Dissemination Identifier', 'Action type', 'Event type', 'Event timestamp',
    'Execution Timestamp', 'Effective Date', 'Expiration Date', 'Platform identifier', 'Non-standardized term indicator',
    'Post-priced swap indicator', 'Notional currency-Leg 1', 'Notional currency-Leg 2', 'Fixed rate-Leg 1', 'Fixed rate-Leg 2',
    'Spread-Leg 1', 'Spread-Leg 2', 'Spread notation-Leg 1', 'Spread notation-Leg 2', 'Strike Price',
    'Fixed rate day count convention-leg 1', 'Fixed rate day count convention-leg 2',
    'Fixed rate payment frequency period-Leg 1', 'Fixed rate payment frequency period-Leg 2',
    'Fixed rate payment frequency period multiplier-Leg 1', 'Fixed rate payment frequency period multiplier-Leg 2',
    'Other payment amount', 'Other payment type', 'Package indicator', 'UPI FISN', 'UPI Underlier Name',
)
RENAMES = {}  # old header name -> current name, for known version changes (empty in v1)

OIS_TENORS = (2, 5, 10, 30)
CPI_TENORS = (5, 10, 30)
XCCY_TENORS = (1, 2, 3, 4, 5)
SOFR_NAMES = ("USD-SOFR-OIS Compound", "USD-SOFR-COMPOUND")  # two spellings of one index
OIS_FREQ = (("YEAR", "1"), ("MNTH", "12"))
# series -> (pair currency, RFR token in the upper-cased underlier name, |spread| cap in bp)  [A5]
XCCY = collections.OrderedDict([("xccy_eurusd", ("EUR", "EUROSTR", 50.0)), ("xccy_jpyusd", ("JPY", "TONA", 100.0)),
                                ("xccy_gbpusd", ("GBP", "SONIA", 50.0))])
XCCY_FISN = {"xccy_eurusd": "NA/Swap Flt Flt EUR USD", "xccy_jpyusd": "NA/Swap Flt Flt JPY USD",
             "xccy_gbpusd": "NA/Swap Flt Flt GBP USD"}
PAIR_LABEL = {"xccy_eurusd": "EURUSD", "xccy_jpyusd": "JPYUSD", "xccy_gbpusd": "GBPUSD"}
TERM_FIELDS = ("Fixed rate-Leg 1", "Fixed rate-Leg 2", "Spread-Leg 1", "Spread-Leg 2", "Effective Date", "Expiration Date",
               "Other payment amount")
FLOOR_STD = (5, 10)   # (n for a median, n for quartiles and the rest)  [A4]
FLOOR_TENOR_XCCY = (10, 10)  # a per-tenor cross-currency cell is published only at n >= 10  [A4]
HEADLINE_MIN_N = 10   # [A1]
WINDOW_MIN = (14 * 60 + 30, 16 * 60 + 30)  # [14:30, 16:30) America/New_York  [A1]
LEDGER_COLS = ("date_utc", "measure", "pair", "tenor_y", "n", "spread_quoted_bp", "spread_bey_bp", "bey_adj_bp", "gap_fisher_bp",
               "gap_simple_bp", "xccy_median_bp", "iqr_over_sqrt_n_bp", "swap_median_pct", "ust_par_pct", "ust_real_pct",
               "par_be_fisher_pct", "fullday_quoted_bp", "n_fullday", "allplat_quoted_bp", "n_allplat", "grade", "status")
CELLS_COLS = ("date_utc", "series", "tenor_y", "variant", "unit", "n", "median", "q1", "q3", "iqr_bp", "iqr_over_sqrt_n_bp",
              "share_pkg", "share_gt10bp", "status")
FUNNEL_COLS = ("date_utc", "series", "step", "tenor_y", "n_after")
DIAG_COLS = ("date_utc", "key", "value", "n")
FILE_STATS_COLS = ("file_date", "zip_name", "zip_kb", "zip_sha256", "zip_md5", "csv_kb", "csv_sha256", "rows", "header_ok",
                   "n_NEWT", "n_CORR", "n_MODI", "n_TERM", "n_EROR", "n_REVI", "n_other_action", "newt_TRAD", "newt_COMP",
                   "newt_NOVA", "newt_EXER", "newt_other_event", "newt_exec_on_file_date", "newt_exec_earlier",
                   "newt_exec_placeholder", "newt_exec_other", "self_refs", "orphan_children", "retrieved_utc", "retrieved_src")
UST_COLS = ("date_utc", "par_2y", "par_5y", "par_10y", "par_30y", "real_5y", "real_10y", "real_30y", "par_csv_sha256",
            "real_csv_sha256", "par_fetched", "real_fetched")
SUMMARY_COLS = ("key", "value", "n")
FETCH_LOG_COLS = ("seq", "requested_at_utc", "host", "path", "http_status", "outcome", "kb", "sha256", "elapsed_ms")
HOLES_COLS = ("date_utc", "http_status", "reason", "recorded_utc")

SOURCES_TEXT = """# Sources and terms for data/swap_tape/

Derived from DTCC Public Price Dissemination, CFTC cumulative interest-rate reports (pddata.dtcc.com). Statistics only; no DTCC record is
reproduced. Non-commercial research (THE_ASK.md E-024).

- **DTCC.** The inputs are the daily CFTC cumulative interest-rate files that DTCC publishes under the CFTC's real-time reporting rules
  (https://pddata.dtcc.com). The principal chose to script the downloads despite DTCC's website terms (THE_ASK.md E-024, "(a)"), on
  these conditions: non-commercial use; no raw DTCC file or row is committed or redistributed; only derived statistics (medians,
  quartiles, counts, shares) are published, under a count floor (fewer than 5 observations: the count only; 5 to 9: count and median;
  10 or more: quartiles as well); and every table cites DTCC. The raw files are kept outside the repository and are never
  committed. Requests are sequential and paced, carry a neutral project User-Agent without a name or address, and any refusal
  ends the run. `fetch_log.csv` records every request; `holes.csv` records dates DTCC no longer serves.
- **U.S. Treasury.** Daily Treasury Par Yield Curve Rates and Daily Treasury Real Yield Curve Rates (home.treasury.gov), the constant-maturity
  (CMT) series. U.S. Government work, public domain. `ust_used.csv` holds the values joined to each date, with the sha256 of the file and
  the date it was fetched.
- **Licence.** CC BY 4.0 (the repository's LICENSE) covers only this project's computation and write-up. It does not extend to DTCC or to
  any data of DTCC; the use of DTCC's data is non-commercial under THE_ASK.md E-024 and nothing in this folder licenses anyone else to
  use DTCC's data commercially.
- **Retrieval dates.** Every CSV starts with a `# source:` comment line naming the source and the retrieval dates. Readers must skip lines
  that start with `#`. Per-file retrieval dates are in `file_stats.csv` (`retrieved_utc`) and `fetch_log.csv`.
- **Nothing here says a flow moves a price.** The ledger measures levels and gaps. See README.md for the columns and the caveats.
"""


# ----------------------------------------------------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------------------------------------------------
class Refused(Exception):
    """A request, path or setting this script will not honour (host list, cache inside the repo, spacing)."""


class MaxRequests(Refused):
    """--max-requests reached: an orderly end of the invocation, not a refusal by the server."""


class Latched(Exception):
    """A technical refusal: STOP was written; the run ends (A8)."""


class SocketFault(Exception):
    """Timeout, reset or TLS error: the invocation ends without latching (A8)."""


def tilde(p):
    home = os.path.expanduser("~")
    return str(p).replace(home, "~") if home and home != "~" else str(p)


def assert_ua(ua=UA):
    if "@" in ua:
        raise Refused("User-Agent contains an address")
    for var in ("SEC_UA", "CLAUDE_CODE_USER_EMAIL"):
        v = os.environ.get(var, "").strip()
        if v and (v in ua or ua in v):
            raise Refused("User-Agent contains a configured contact value (not printed)")


assert_ua()


def check_url(url):
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    if p.scheme != "https":
        raise Refused("only https is allowed")
    if host == "sec.gov" or host.endswith(".sec.gov"):
        raise Refused("sec.gov hosts are outside the E-024 ruling")
    if host not in HOSTS or not p.path.startswith(HOSTS[host]):
        raise Refused("host or path outside the E-024 ruling")
    return host, p.path + ("?" + p.query if p.query else "")


def check_cache(cache):
    real = os.path.realpath(os.path.expanduser(cache))
    root = os.path.realpath(ROOT)
    if real == root or real.startswith(root + os.sep):
        raise Refused("the cache must be outside the repository (DTCC files are never committed)")
    return real


def fnum(s):
    s = (s or "").strip()
    if s.endswith("+"):
        s = s[:-1]
    s = s.replace(",", "")
    if not s:
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    return v if math.isfinite(v) else None


def pdate(s):
    try:
        return dt.date.fromisoformat((s or "").strip()[:10])
    except ValueError:
        return None


def add_years(d, n):
    try:
        return d.replace(year=d.year + n)
    except ValueError:  # 29 Feb + N years -> 28 Feb
        return d.replace(year=d.year + n, day=28)


def bucket(eff, exp, targets, tol=7):
    if eff is None or exp is None:
        return None
    for n in targets:
        if abs((exp - add_years(eff, n)).days) <= tol:
            return n
    return None


def bey(r, a=365.0 / 360.0):
    """Annual ACT/360 rate r (decimal) -> semiannual bond-equivalent rate, accrual factor a per year."""
    return 2.0 * (math.sqrt(1.0 + r * a) - 1.0)


def fisher_breakeven(n, r):
    """Annualised par breakeven consistent with semiannual-compounded nominal n and real r (decimals)  [A3]."""
    return ((1.0 + n / 2.0) / (1.0 + r / 2.0)) ** 2 - 1.0


def q7(xs, p):
    """Type-7 quantile of an already sorted list."""
    n = len(xs)
    h = (n - 1) * p
    lo = int(math.floor(h))
    hi = min(lo + 1, n - 1)
    return xs[lo] + (h - lo) * (xs[hi] - xs[lo])


def idkey(s):
    return (0, int(s)) if s.isdigit() else (1, s)


_NY = None


def ny_parts(ts):
    """(hour, minute of day) in America/New_York for an execution timestamp ending in Z; None if malformed."""
    global _NY
    if _NY is None:
        _NY = ZoneInfo("America/New_York")
    try:
        d = dt.datetime.strptime(ts.strip(), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).astimezone(_NY)
    except ValueError:
        return None
    return d.hour, d.hour * 60 + d.minute


def in_window(ts):
    p = ny_parts(ts)
    return p is not None and WINDOW_MIN[0] <= p[1] < WINDOW_MIN[1]


def assert_window():
    """Run-time guard (verifier S3): the 14:30-16:30 New York window on four known UTC instants, summer and winter."""
    cases = {"2026-10-13T18:30:00Z": True, "2026-10-13T20:29:59Z": True, "2026-10-13T20:30:00Z": False,
             "2026-01-15T19:30:00Z": True, "2026-01-15T18:59:59Z": False, "2026-01-15T21:29:59Z": True}
    for ts, want in cases.items():
        if in_window(ts) != want:
            raise AssertionError("New York window guard failed at %s (want %s)" % (ts, want))


def f6(x):
    return "" if x is None else _nz(format(x, ".6f"))


def f3(x):
    return "" if x is None else _nz(format(x, ".3f"))


def f4(x):
    return "" if x is None else _nz(format(x, ".4f"))


def _nz(s):
    return s[1:] if re.fullmatch(r"-0\.0+", s) else s


def fust(x):
    """A Treasury CMT value as printed: two decimals (4.40), more only if the file has them."""
    if x is None:
        return ""
    s = format(x, ".4f")
    return s[:-2] if s.endswith("00") else s


def weekdays(d0, d1):
    d = d0
    while d <= d1:
        if d.weekday() < 5:
            yield d
        d += dt.timedelta(days=1)


def pd_arg(s):
    return dt.date.fromisoformat(s)


def kb(n_bytes):
    return format(n_bytes / 1000.0, ".1f")


def sha256_of(b):
    return hashlib.sha256(b).hexdigest()


# ----------------------------------------------------------------------------------------------------------------------
# CSV tables: source line, floor-safe writer, upsert
# ----------------------------------------------------------------------------------------------------------------------
LEAK_RX = re.compile(r"[0-9]{8,19}")


def source_line(span_dtcc=None, span_ust=None, extra=None):
    s = ("# source: DTCC Public Price Dissemination, CFTC cumulative rates reports (pddata.dtcc.com); statistics only, no DTCC record is "
         "reproduced; non-commercial research (THE_ASK.md E-024)")
    if span_dtcc is not None:
        s += "; DTCC files retrieved " + (span_dtcc[0] if span_dtcc[0] == span_dtcc[1] else span_dtcc[0] + " to " + span_dtcc[1])
    if span_ust is not None:
        s += ("; U.S. Treasury CMT par and real yield curve CSVs (home.treasury.gov, public domain) retrieved "
              + (span_ust[0] if span_ust[0] == span_ust[1] else span_ust[0] + " to " + span_ust[1]))
    if extra:
        s += "; " + extra
    return s


def check_fields(header, rows):
    for h in header:
        low = h.lower()
        if "min" in low or "max" in low:
            raise AssertionError("header contains min or max: " + h)
    for r in rows:
        if len(r) != len(header):
            raise AssertionError("row width %d != header width %d" % (len(r), len(header)))
        for f in r:
            if LEAK_RX.fullmatch(str(f)):
                raise AssertionError("output field looks like a Dissemination Identifier (8-19 digits)")


def write_table(path, header, rows, source):
    check_fields(header, rows)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(source + "\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    os.replace(tmp, path)


def read_table(path, header=None):
    """Data rows of a table written by write_table (comment lines skipped); [] if the file is absent."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        lines = [ln for ln in f.read().splitlines(True) if not ln.startswith("#")]
    rd = list(csv.reader(io.StringIO("".join(lines))))
    if not rd:
        return []
    if header is not None and tuple(rd[0]) != tuple(header):
        raise AssertionError("unexpected header in " + tilde(path))
    return rd[1:]


def upsert_table(path, header, new_rows, dates, source_fn, date_col=0):
    """Replace the rows of `dates` (ISO strings) by new_rows, keep the others; stable sort by date; write."""
    keep = [r for r in read_table(path, header) if r[date_col] not in dates]
    allrows = keep + [list(r) for r in new_rows]
    allrows.sort(key=lambda r: r[date_col])
    write_table(path, header, allrows, source_fn(allrows))
    return allrows


# ----------------------------------------------------------------------------------------------------------------------
# statistics and the publication floor  [A4]
# ----------------------------------------------------------------------------------------------------------------------
def cell_stats(vals, floor, scale_bp, pkgs=None):
    """vals in native units (decimal rate or bp); scale_bp converts a native difference to bp. The floor decides what is
    computed AT ALL: below it the statistic does not exist in the result, so it cannot leak into an output."""
    n = len(vals)
    st = {"n": n, "median": None, "q1": None, "q3": None, "iqr": None, "ios": None, "share_pkg": None, "share_gt10": None}
    if n >= floor[0]:
        s = sorted(vals)
        st["median"] = q7(s, 0.5)
        if n >= floor[1]:
            st["q1"], st["q3"] = q7(s, 0.25), q7(s, 0.75)
            st["iqr"] = (st["q3"] - st["q1"]) * scale_bp
            st["ios"] = st["iqr"] / math.sqrt(n)
            st["share_gt10"] = sum(1 for v in vals if abs(v - st["median"]) * scale_bp > 10.0) / n
            if pkgs is not None:
                st["share_pkg"] = sum(1 for p in pkgs if p) / n
    st["status"] = "ok" if n >= floor[1] else ("thin" if n >= floor[0] else "below_min_n")
    return st


def cell_row(date, series, tenor, variant, unit, st):
    if unit == "pct":
        med, q1, q3 = (f6(None if st[k] is None else st[k] * 100.0) for k in ("median", "q1", "q3"))
    else:
        med, q1, q3 = (f3(st[k]) for k in ("median", "q1", "q3"))
    return [date, series, str(tenor), variant, unit, str(st["n"]), med, q1, q3, f3(st["iqr"]), f3(st["ios"]),
            f4(st["share_pkg"]), f4(st["share_gt10"]), st["status"]]


# ----------------------------------------------------------------------------------------------------------------------
# Treasury CMT files
# ----------------------------------------------------------------------------------------------------------------------
PAR_COLS = {2: "2yr", 5: "5yr", 10: "10yr", 30: "30yr"}
REAL_COLS = {5: "5yr", 10: "10yr", 30: "30yr"}


def parse_ust_text(text, kind):
    """Treasury CSV -> {date: {tenor: percent or None}}. Header names matched case-insensitively and without spaces
    ("5 Yr" and "5 YR" are one column); the date column is 'Date' (A7)."""
    rd = csv.reader(io.StringIO(text.lstrip("﻿")))
    header = next(rd, None)
    if not header:
        raise AssertionError("empty Treasury CSV")
    norm = [re.sub(r"\s+", "", h.strip().lower()) for h in header]
    need = PAR_COLS if kind == "par" else REAL_COLS
    if "date" not in norm:
        raise AssertionError("Treasury CSV has no Date column")
    idx = {}
    for n, name in need.items():
        if name not in norm:
            raise AssertionError("Treasury CSV lacks column " + name)
        idx[n] = norm.index(name)
    di = norm.index("date")
    out = {}
    for row in rd:
        if not row or not row[di].strip():
            continue
        d = dt.datetime.strptime(row[di].strip(), "%m/%d/%Y").date()
        vals = {}
        for n, i in idx.items():
            v = row[i].strip() if i < len(row) else ""
            vals[n] = float(v) if v not in ("", "N/A") else None
        out[d] = vals
    return out


class Ust:
    """The Treasury CSVs found in a directory: newest copy per (kind, year)."""

    def __init__(self, ust_dir):
        self.par, self.real, self.info = {}, {}, {}
        best = {}
        if ust_dir and os.path.isdir(ust_dir):
            for name in sorted(os.listdir(ust_dir)):
                m = re.fullmatch(r"(daily_treasury_yield_curve|daily_treasury_real_yield_curve)_(\d{4})_fetched-(\d{8})\.csv", name)
                if not m:
                    continue
                key = (m.group(1), m.group(2))
                if key not in best or m.group(3) > best[key][1]:
                    best[key] = (name, m.group(3))
        for (t, y), (name, fetched) in sorted(best.items()):
            with open(os.path.join(ust_dir, name), "rb") as f:
                raw = f.read()
            kind = "par" if t == "daily_treasury_yield_curve" else "real"
            tbl = parse_ust_text(raw.decode("utf-8-sig"), kind)
            sha = sha256_of(raw)
            fetched_iso = fetched[:4] + "-" + fetched[4:6] + "-" + fetched[6:]
            for d, vals in tbl.items():
                (self.par if kind == "par" else self.real)[d] = vals
                self.info[(kind, d)] = (sha, fetched_iso)

    def for_date(self, d):
        if d not in self.par:
            return None
        return {"par": self.par[d], "real": self.real.get(d, {}),
                "par_sha": self.info[("par", d)][0], "par_fetched": self.info[("par", d)][1],
                "real_sha": self.info.get(("real", d), ("", ""))[0], "real_fetched": self.info.get(("real", d), ("", ""))[1]}

    def cmt_dates(self):
        return sorted(self.par)


# ----------------------------------------------------------------------------------------------------------------------
# fetching: the only network code. One request at a time, paced, GET only, STOP latch  [E-024, A8]
# ----------------------------------------------------------------------------------------------------------------------
def real_opener(host, target, headers, timeout, cap):
    """GET https://host/target. Returns (status, body); body is None when it exceeds `cap`. No redirects are followed
    (a 3xx comes back as a status), no cookies, and the only verb is GET. Socket-level faults raise SocketFault."""
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


def dtcc_name(d, ext="zip"):
    return "CFTC_CUMULATIVE_RATES_%04d_%02d_%02d.%s" % (d.year, d.month, d.day, ext)


def zip_problem(body, d):
    """None if `body` is the zip we asked for, else a short reason (A8: anything else latches)."""
    if body is None:
        return "body larger than the %d MB cap" % (BODY_CAP // (1024 * 1024))
    if not body.startswith(b"PK\x03\x04"):
        return "200 but the body is not a zip"
    try:
        z = zipfile.ZipFile(io.BytesIO(body))
        bad = z.testzip()
        names = z.namelist()
    except zipfile.BadZipFile:
        return "200 but the zip is unreadable"
    if bad is not None:
        return "zip member fails its CRC"
    if names != [dtcc_name(d, "csv")]:
        return "zip does not hold exactly the member for the requested date"
    return None


class Fetcher:
    """All requests go through here. Injectable opener, clock, sleeper and STOP path make it testable without a network."""

    def __init__(self, cache, out_dir, sleep=MIN_SLEEP, max_requests=60, opener=real_opener, wall=time.time, mono=time.monotonic,
                 sleeper=time.sleep, stop_path=STOP_PATH, now_utc=None, pid_alive=None):
        if sleep < MIN_SLEEP:
            raise Refused("--sleep must be at least %d seconds" % MIN_SLEEP)
        if max_requests > HARD_CAP_REQUESTS or max_requests < 1:
            raise Refused("--max-requests must be between 1 and %d" % HARD_CAP_REQUESTS)
        self.cache = check_cache(cache)
        self.out_dir = out_dir
        self.sleep, self.max_requests = float(sleep), max_requests
        self.opener, self.wall, self.mono, self.sleeper = opener, wall, mono, sleeper
        self.stop_path = stop_path
        self.now_utc = now_utc or (lambda: dt.datetime.now(dt.timezone.utc))
        self.pid_alive = pid_alive or _pid_alive
        self.requests = 0
        self._last_mono = None
        self._lock = os.path.join(self.cache, ".fetch.lock")
        self._last_file = os.path.join(self.cache, ".last_request")
        self.log_path = os.path.join(out_dir, "fetch_log.csv")
        self.holes_path = os.path.join(out_dir, "holes.csv")
        self._locked = False

    # -- lifecycle ------------------------------------------------------------------------------------------------
    def __enter__(self):
        if os.path.exists(self.stop_path):
            with open(self.stop_path, encoding="utf-8") as f:
                why = f.read().strip().replace("\n", " ")[:200]
            raise Latched("STOP exists at %s (%s); a human must inspect and delete it" % (tilde(self.stop_path), why))
        os.makedirs(self.cache, exist_ok=True)
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
                    with open(self._lock, encoding="utf-8") as f:
                        pid_s, t_s = (f.read().split() + ["0", "0"])[:2]
                    pid, t0 = int(pid_s), float(t_s)
                except (ValueError, OSError):
                    pid, t0 = 0, 0.0
                age = self.wall() - t0
                if pid > 0 and self.pid_alive(pid) and age < 6 * 3600:
                    raise Refused("another fetcher holds %s (pid %d)" % (tilde(self._lock), pid))
                os.remove(self._lock)  # stale: dead pid or older than six hours
                continue
            with os.fdopen(fd, "w") as f:
                f.write("%d %.0f\n" % (os.getpid(), self.wall()))
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
            with open(self._last_file, encoding="utf-8") as f:
                last = float(f.read().strip())
            wait = max(wait, min(self.sleep, self.sleep - (self.wall() - last)))
        except (OSError, ValueError):
            pass
        if self._last_mono is not None:
            wait = max(wait, self.sleep - (self.mono() - self._last_mono))
        if wait > 0:
            self.sleeper(wait)

    def _get(self, host, target):
        """Returns (status, body, started_wall, elapsed_ms). Raises SocketFault (after logging it)."""
        check_url("https://" + host + target)
        if self.requests >= self.max_requests:
            raise MaxRequests("--max-requests reached (%d)" % self.max_requests)
        self._pace()
        started = self.wall()
        self._last_mono = self.mono()
        t0 = self._last_mono
        with open(self._last_file, "w", encoding="utf-8") as f:
            f.write("%.3f\n" % started)
        self.requests += 1
        try:
            status, body = self.opener(host, target, HEADERS, TIMEOUT, BODY_CAP)
        except SocketFault as e:
            self._log(started, host, target, "", "socket_fault:" + str(e), "", "", int((self.mono() - t0) * 1000))
            raise
        return status, body, started, int((self.mono() - t0) * 1000)

    def _log(self, started, host, target, status, outcome, size_kb, sha, elapsed_ms):
        rows = read_table(self.log_path, FETCH_LOG_COLS)
        stamp = dt.datetime.fromtimestamp(started, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + \
            "%03dZ" % int((started % 1) * 1000)
        path = target  # the full request target (no personal data in it); the Treasury query says which curve
        rows.append([str(len(rows) + 1), stamp, host, path, str(status), outcome, size_kb, sha, str(elapsed_ms)])
        write_table(self.log_path, FETCH_LOG_COLS, rows,
                    "# source: request log for DTCC Public Price Dissemination (pddata.dtcc.com) and U.S. Treasury (home.treasury.gov) "
                    "files; each row carries its own UTC time; non-commercial research (THE_ASK.md E-024)")

    def _latch(self, reason):
        os.makedirs(os.path.dirname(self.stop_path), exist_ok=True)
        with open(self.stop_path, "w", encoding="utf-8") as f:
            f.write("%s UTC  %s\n" % (self.now_utc().strftime("%Y-%m-%dT%H:%M:%S"), reason))
        raise Latched(reason)

    # -- DTCC -----------------------------------------------------------------------------------------------------
    def known_holes(self):
        return {r[0] for r in read_table(self.holes_path, HOLES_COLS)}

    def fetch_date(self, d):
        """Returns an outcome word. Raises Latched / SocketFault / Refused."""
        if d.weekday() >= 5:
            return "weekend"
        if d < EARLIEST_DATE:
            return "before_archive"
        name = dtcc_name(d)
        path = os.path.join(self.cache, name)
        if os.path.exists(path):
            return "cached"
        if d.isoformat() in self.known_holes():
            return "hole_known"
        today = self.now_utc().date()
        if d > today - dt.timedelta(days=2):
            return "not_yet"
        status, body, started, ms = self._get("pddata.dtcc.com", DTCC_PREFIX + name)
        if status == 404 and (today - d).days > HOLE_AGE_DAYS:
            reason = "404 for a date more than %d days old: undocumented by DTCC, recorded as a hole, not a refusal" % HOLE_AGE_DAYS
            rows = read_table(self.holes_path, HOLES_COLS)
            rows = [r for r in rows if r[0] != d.isoformat()] + [[d.isoformat(), "404", reason,
                                                                  self.now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")]]
            rows.sort(key=lambda r: r[0])
            write_table(self.holes_path, HOLES_COLS, rows,
                        source_line(extra="dates DTCC no longer serves; a 404 older than %d days is recorded here and does not stop the run"
                                    % HOLE_AGE_DAYS))
            self._log(started, "pddata.dtcc.com", DTCC_PREFIX + name, status, "hole", "", "", ms)
            return "hole"
        if status != 200:
            self._log(started, "pddata.dtcc.com", DTCC_PREFIX + name, status, "STOP:http_%d" % status, "", "", ms)
            self._latch("HTTP %d for %s" % (status, name))
        prob = zip_problem(body, d)
        if prob:
            self._log(started, "pddata.dtcc.com", DTCC_PREFIX + name, status, "STOP:bad_body", "", "", ms)
            self._latch("%s (%s)" % (prob, name))
        part = path + ".part"
        with open(part, "wb") as f:
            f.write(body)
        os.replace(part, path)
        self._log(started, "pddata.dtcc.com", DTCC_PREFIX + name, status, "saved", kb(len(body)), sha256_of(body), ms)
        return "saved"

    # -- Treasury -------------------------------------------------------------------------------------------------
    def fetch_ust(self, year, kind, ust_dir):
        today_s = self.now_utc().strftime("%Y%m%d")
        os.makedirs(ust_dir, exist_ok=True)
        have = [n for n in os.listdir(ust_dir) if n.startswith("%s_%d_fetched-" % (kind, year))]
        if any(n.endswith(today_s + ".csv") for n in have):
            return "cached_today"
        final_from = "%d0103" % (year + 1)   # a copy fetched on or after 3 Jan of the next year holds the year's last rows
        if any(n[-12:-4] >= final_from for n in have):
            return "cached_final_year"
        target = TSY_TMPL.format(y=year, t=kind)
        status, body, started, ms = self._get("home.treasury.gov", target)
        if status != 200:
            self._log(started, "home.treasury.gov", target, status, "STOP:http_%d" % status, "", "", ms)
            self._latch("HTTP %d for Treasury %s %d" % (status, kind, year))
        try:
            if body is None:
                raise AssertionError("body larger than the cap")
            text = body.decode("utf-8-sig")
            parse_ust_text(text, "par" if kind == "daily_treasury_yield_curve" else "real")
        except (AssertionError, ValueError, UnicodeDecodeError) as e:
            self._log(started, "home.treasury.gov", target, status, "STOP:bad_body", "", "", ms)
            self._latch("Treasury body is not the expected CSV (%s)" % str(e)[:80])
        path = os.path.join(ust_dir, "%s_%d_fetched-%s.csv" % (kind, year, today_s))
        with open(path + ".part", "wb") as f:
            f.write(body)
        os.replace(path + ".part", path)
        self._log(started, "home.treasury.gov", target, status, "saved", kb(len(body)), sha256_of(body), ms)
        return "saved"


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


# ----------------------------------------------------------------------------------------------------------------------
# reading a file, resolving versions, one price per executed trade  [spec section 5]
# ----------------------------------------------------------------------------------------------------------------------
class Cfg:
    """mutant: None, or one of noconv / noeror / nowindow (selftest and diagnostics only)."""

    def __init__(self, mutant=None):
        if mutant not in (None, "noconv", "noeror", "nowindow"):
            raise ValueError("unknown mutant")
        self.mutant = mutant
        self.noconv, self.noeror, self.nowindow = (mutant == "noconv", mutant == "noeror", mutant == "nowindow")


class SchemaMismatch(Exception):
    pass


def project(rows_iter, header):
    """Rename-map the header, check the required columns by name (A11), return (rows as dicts of REQUIRED columns, added, removed)."""
    names = [RENAMES.get(h, h) for h in header]
    missing = [c for c in REQUIRED if c not in names]
    if missing:
        raise SchemaMismatch("missing required columns: " + "; ".join(missing))
    idx = {c: names.index(c) for c in REQUIRED}
    added = [h for h in names if h not in HEADER_V1]
    removed = [h for h in HEADER_V1 if h not in names]
    out = []
    width = len(header)
    for row in rows_iter:
        if not row:
            continue
        if len(row) < width:
            row = row + [""] * (width - len(row))
        out.append({c: row[i] for c, i in idx.items()})
    return out, added, removed


def read_zip(path, d):
    """-> (rows, info) for the cached zip of date d. Reads in memory; nothing is extracted. Raises SchemaMismatch."""
    with open(path, "rb") as f:
        raw = f.read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    member = dtcc_name(d, "csv")
    if z.namelist() != [member]:
        raise AssertionError("zip member name does not match the date")
    data = z.read(member)
    rd = csv.reader(io.TextIOWrapper(io.BytesIO(data), encoding="utf-8-sig", newline=""))
    header = next(rd, None)
    if not header:
        raise SchemaMismatch("empty file")
    rows, added, removed = project(rd, header)
    info = {"zip_name": os.path.basename(path), "zip_kb": kb(len(raw)), "zip_sha256": sha256_of(raw),
            "zip_md5": hashlib.md5(raw).hexdigest(), "csv_kb": kb(len(data)), "csv_sha256": sha256_of(data),
            "added": added, "removed": removed}
    return rows, info


def resolve_trades(rows, cfg, file_date):
    """One resolved version per NEWT/TRAD row. Returns (trades, counters, file_counts)."""
    by_id = {}
    for r in rows:
        i = r["Dissemination Identifier"]
        if i in by_id:
            raise AssertionError("Dissemination Identifier is not unique within the file")
        by_id[i] = r
    kids = collections.defaultdict(list)
    self_refs = orphans = 0
    for r in rows:
        o = r["Original Dissemination Identifier"]
        if not o:
            continue
        if o == r["Dissemination Identifier"]:
            self_refs += 1
            continue
        if o not in by_id:
            orphans += 1
        kids[o].append(r)

    def has_eror(c):
        return any(k["Action type"] == "EROR" for k in kids.get(c["Dissemination Identifier"], ()))

    fc = collections.Counter()
    for r in rows:
        a = r["Action type"]
        fc["n_" + a if a in ("NEWT", "CORR", "MODI", "TERM", "EROR", "REVI") else "n_other_action"] += 1
        if a == "NEWT":
            ev = r["Event type"]
            fc["newt_" + ev if ev in ("TRAD", "COMP", "NOVA", "EXER") else "newt_other_event"] += 1
            xd = r["Execution Timestamp"][:10]
            if xd == file_date:
                fc["newt_exec_on_file_date"] += 1
            elif xd == "2000-01-01":
                fc["newt_exec_placeholder"] += 1
            elif xd and xd < file_date:
                fc["newt_exec_earlier"] += 1
            else:
                fc["newt_exec_other"] += 1
    fc["self_refs"], fc["orphan_children"] = self_refs, orphans

    cnt = collections.Counter()
    trades = []
    for r in rows:
        if r["Action type"] != "NEWT" or r["Event type"] != "TRAD":
            continue
        cur, steps, dropped, revived = r, 0, False, False
        for _ in range(10):
            ch = kids.get(cur["Dissemination Identifier"], [])
            if not cfg.noeror:
                ch = [c for c in ch if not has_eror(c)]  # step 1
                eror = [c for c in ch if c["Action type"] == "EROR"]
                if eror:  # step 2
                    last = max(c["Event timestamp"] for c in eror)
                    if any(c["Action type"] == "REVI" and c["Event timestamp"] > last for c in ch):
                        revived = True
                    else:
                        dropped = True
                        break
            corr = [c for c in ch if c["Action type"] == "CORR"]
            if not corr:
                break
            cur = max(corr, key=lambda c: (c["Event timestamp"], idkey(c["Dissemination Identifier"])))  # step 3
            steps += 1
        if dropped:
            cnt["eror_dropped"] += 1
            continue
        final = dict(cur)
        final["Event type"] = r["Event type"]  # step 4
        if steps:
            cnt["corr_applied"] += 1
            if any(final[k] != r[k] for k in TERM_FIELDS):
                cnt["corr_changed_terms"] += 1
        if revived:
            cnt["revived"] += 1
        final["_xd"] = final["Execution Timestamp"][:10]
        final["_eff"] = pdate(final["Effective Date"])
        final["_exp"] = pdate(final["Expiration Date"])
        trades.append(final)
    for r in rows:
        if r["Action type"] == "MODI":
            p = by_id.get(r["Original Dissemination Identifier"])
            if p is not None and (p["Fixed rate-Leg 1"], p["Fixed rate-Leg 2"]) != (r["Fixed rate-Leg 1"], r["Fixed rate-Leg 2"]):
                cnt["modi_rate_changed"] += 1
    cnt["placeholder_rows"] = sum(1 for t in trades if t["_xd"] == "2000-01-01")
    return trades, cnt, fc


# ----------------------------------------------------------------------------------------------------------------------
# series pipelines. Each returns funnel rows and the records per (tenor, variant).
# ----------------------------------------------------------------------------------------------------------------------
class Funnel:
    def __init__(self, series):
        self.series, self.rows = series, []

    def step(self, name, items, pred=None, tenor=""):
        if pred is not None:
            items = [x for x in items if pred(x)]
        self.rows.append((self.series, name, str(tenor), len(items)))
        return items


def spot_ok(t):
    return t["_eff"] is not None and pdate(t["_xd"]) is not None and 0 <= (t["_eff"] - pdate(t["_xd"])).days <= 5


def flags_ok(t):
    return t["Post-priced swap indicator"].strip().lower() != "true" and t["Non-standardized term indicator"].strip().upper() != "TRUE"


def conv(t, leg):
    """Fixed-leg day count and payment frequency, read from the other leg when this leg's are blank  [A5, CR5]."""
    other = "2" if leg == "1" else "1"
    dc = t["Fixed rate day count convention-leg " + leg].strip() or t["Fixed rate day count convention-leg " + other].strip()
    per = t["Fixed rate payment frequency period-Leg " + leg].strip()
    mul = t["Fixed rate payment frequency period multiplier-Leg " + leg].strip()
    if not per:
        per = t["Fixed rate payment frequency period-Leg " + other].strip()
        mul = t["Fixed rate payment frequency period multiplier-Leg " + other].strip()
    return dc, per, mul


def one_fixed_leg(items):
    """F5: exactly one of the two fixed rates is filled (and numeric). Returns [{'t','L','r'}]."""
    out = []
    for t in items:
        a, b = t["Fixed rate-Leg 1"].strip(), t["Fixed rate-Leg 2"].strip()
        if bool(a) == bool(b):
            continue
        leg = "1" if a else "2"
        r = fnum(a or b)
        if r is not None:
            out.append({"t": t, "L": leg, "r": r})
    return out


def rec_common(x, n_years, cfg):
    t = x["t"]
    p = ny_parts(t["Execution Timestamp"])
    days = (t["_exp"] - t["_eff"]).days
    rec = {"v": x["r"], "N": n_years, "plat": t["Platform identifier"].strip(), "pkg": t["Package indicator"].strip().upper() == "TRUE",
           "hr": None if p is None else p[0], "mn": None if p is None else p[1]}
    rec["bey"] = x["r"] if cfg.noconv else bey(x["r"], days / (360.0 * n_years))
    return rec


def tenor_split(fn, items, targets, cfg):
    """F7 per tenor; returns {N: [records]}."""
    by = {n: [] for n in targets}
    for x in items:
        n = bucket(x["t"]["_eff"], x["t"]["_exp"], targets)
        if n is not None:
            by[n].append((x, n))
    out = {}
    for n in targets:
        out[n] = [rec_common(x, n, cfg) for x, _ in by[n]]
        fn.rows.append((fn.series, "F7", str(n), len(out[n])))
    return out


def run_ois(trades, d, cfg):
    fn = Funnel("sofr_ois")
    cur = fn.step("F0", trades, lambda t: t["UPI FISN"] == "NA/Swap OIS USD" and t["UPI Underlier Name"] in SOFR_NAMES)
    cur = fn.step("F1", cur, lambda t: t["_xd"] == d)
    cur = fn.step("F2", cur, spot_ok)
    cur = fn.step("F3", cur, lambda t: not t["Other payment amount"].strip())
    cur = fn.step("F4", cur, flags_ok)
    cur = fn.step("F4s", cur, lambda t: not t["Strike Price"].strip())
    legs = fn.step("F5", one_fixed_leg(cur))
    legs = fn.step("F6", legs, lambda x: conv(x["t"], x["L"])[0] == "A004" and conv(x["t"], x["L"])[1:] in OIS_FREQ)
    pct_unit = sum(1 for x in legs if x["r"] > 0.25)
    legs = fn.step("F6u", legs, lambda x: 0.0 < x["r"] <= 0.25)
    by = tenor_split(fn, legs, OIS_TENORS, cfg)
    groups = {}
    for n in OIS_TENORS:
        allp = by[n]
        full = [r for r in allp if r["plat"] != "BILT"]
        head = full if cfg.nowindow else [r for r in full if r["mn"] is not None and WINDOW_MIN[0] <= r["mn"] < WINDOW_MIN[1]]
        fn.rows.append((fn.series, "F8", str(n), len(full)))
        fn.rows.append((fn.series, "F9", str(n), len(head)))
        groups[(n, "all_platforms")], groups[(n, "fullday")], groups[(n, "headline")] = allp, full, head
    return fn.rows, groups, {"pct_unit_rows": pct_unit}


def run_cpi(trades, d, cfg):
    fn = Funnel("cpi_zc")
    cur = fn.step("F0", trades, lambda t: t["UPI FISN"] == "NA/Swap Infl Idx USD" and t["UPI Underlier Name"] == "USA-CPI-U")
    cur = fn.step("F1", cur, lambda t: t["_xd"] == d)
    cur = fn.step("F2", cur, spot_ok)
    cur = fn.step("F3", cur, lambda t: not t["Other payment amount"].strip())
    cur = fn.step("F4", cur, flags_ok)
    cur = fn.step("F4s", cur, lambda t: not t["Strike Price"].strip())
    legs = fn.step("F5", one_fixed_leg(cur))

    def zc_shape(x):
        _, per, mul = conv(x["t"], x["L"])
        return (per == "EXPI" and mul == "1") or (per == "YEAR" and mul.isdigit() and int(mul) >= 1)

    legs = fn.step("F6", legs, zc_shape)
    # F7 also requires that a YEAR period equals the bucket's tenor (a zero coupon pays once, at N years)
    keep = []
    for x in legs:
        n = bucket(x["t"]["_eff"], x["t"]["_exp"], CPI_TENORS)
        if n is None:
            continue
        _, per, mul = conv(x["t"], x["L"])
        if per == "YEAR" and int(mul) != n:
            continue
        keep.append(x)
    by = tenor_split(fn, keep, CPI_TENORS, cfg)
    groups = {}
    for n in CPI_TENORS:
        allp = by[n]
        full = [r for r in allp if r["plat"] != "BILT"]
        win = [r for r in full if r["mn"] is not None and WINDOW_MIN[0] <= r["mn"] < WINDOW_MIN[1]]
        fn.rows.append((fn.series, "F8", str(n), len(full)))
        fn.rows.append((fn.series, "F9", str(n), len(win)))
        groups[(n, "all_platforms")], groups[(n, "headline")], groups[(n, "cmt_window")] = allp, full, win
    return fn.rows, groups, {}


def xccy_match(t, series):
    ccy, rfr, _ = XCCY[series]
    und = t["UPI Underlier Name"].upper()
    return t["UPI FISN"] == XCCY_FISN[series] and "SOFR" in und and rfr in und and "IBOR" not in und


def run_xccy(trades, d, cfg, series):
    ccy, _, cap = XCCY[series]
    fn = Funnel(series)
    cur = fn.step("F0", trades, lambda t: xccy_match(t, series))
    cur = fn.step("F1", cur, lambda t: t["_xd"] == d)
    cur = fn.step("F2", cur, spot_ok)
    cur = fn.step("F3", cur, lambda t: "UFRO" not in [p.strip() for p in t["Other payment type"].split(";")])
    cur = fn.step("F4", cur, flags_ok)
    cur = fn.step("F4s", cur, lambda t: not t["Strike Price"].strip())
    legs = []
    for t in cur:
        c1, c2 = t["Notional currency-Leg 1"].strip(), t["Notional currency-Leg 2"].strip()
        if t["Fixed rate-Leg 1"].strip() or t["Fixed rate-Leg 2"].strip():
            continue
        if (c1, c2) == ("USD", ccy):
            legs.append((t, "1", "2"))
        elif (c1, c2) == (ccy, "USD"):
            legs.append((t, "2", "1"))
    fn.rows.append((series, "F5", "", len(legs)))
    notation, usd_only = collections.Counter(), 0
    vals = []
    for t, u, x in legs:
        su, sx = fnum(t["Spread-Leg " + u]), fnum(t["Spread-Leg " + x])
        if t["Spread-Leg " + u].strip() and su not in (None, 0.0) and not t["Spread-Leg " + x].strip():
            usd_only += 1
            continue
        if sx is None or su not in (None, 0.0) or (t["Spread-Leg " + u].strip() and su is None):
            continue
        nt = t["Spread notation-Leg " + x].strip()
        notation[nt if nt in ("3", "4") else "other"] += 1
        if nt == "3":
            bp = sx * 10000.0
        elif nt == "4":
            bp = sx
        else:
            continue
        if abs(bp) > cap:
            continue
        vals.append((t, bp))
    fn.rows.append((series, "F6", "", len(vals)))
    by = {n: [] for n in XCCY_TENORS}
    for t, bp in vals:
        n = bucket(t["_eff"], t["_exp"], XCCY_TENORS)
        if n is not None:
            by[n].append({"v": bp, "pkg": t["Package indicator"].strip().upper() == "TRUE", "plat": t["Platform identifier"].strip(),
                          "hr": None, "mn": None})
    groups = {}
    pooled = []
    for n in XCCY_TENORS:
        fn.rows.append((series, "F7", str(n), len(by[n])))
        groups[(n, "headline")] = by[n]
        pooled += by[n]
    groups[("pool1to5", "headline")] = pooled
    return fn.rows, groups, {"notation": notation, "usd_only": usd_only}


# ----------------------------------------------------------------------------------------------------------------------
# one day: funnel, cells, diagnostics
# ----------------------------------------------------------------------------------------------------------------------
CELL_DEFS = [("sofr_ois", OIS_TENORS, ("headline", "fullday", "all_platforms"), "pct"),
             ("sofr_ois_bey", OIS_TENORS, ("headline",), "pct"),
             ("cpi_zc", CPI_TENORS, ("headline", "all_platforms", "cmt_window"), "pct")] + \
            [(s, XCCY_TENORS + ("pool1to5",), ("headline",), "bp") for s in XCCY]


class Day:
    def __init__(self, d):
        self.d = d
        self.funnel, self.cells, self.diag, self.warn = [], [], [], []
        self.groups = {}   # (series, tenor, variant) -> records
        self.cs = {}       # (series, tenor, variant) -> stats
        self.fc = {}
        self.cnt = {}


def unmatched_top10(trades, series):
    cnt = collections.Counter()
    for t in trades:
        fisn, und = t["UPI FISN"], t["UPI Underlier Name"]
        u = und.upper()
        if series == "sofr_ois":
            if fisn == "NA/Swap OIS USD" and und in SOFR_NAMES:
                continue
            cand = fisn in ("NA/Swap OIS USD", "NA/Swap Flt Flt OIS USD") or \
                ("SOFR" in u and fisn not in XCCY_FISN.values() and not fisn.startswith("NA/Swap Flt Flt"))
        elif series == "cpi_zc":
            if fisn == "NA/Swap Infl Idx USD" and und == "USA-CPI-U":
                continue
            cand = ("CPI" in u and "USA" in u) or ("Infl" in fisn and "USD" in fisn)
        else:
            if xccy_match(t, series):
                continue
            cand = fisn == XCCY_FISN[series]
        if cand:
            cnt[fisn + " | " + und] += 1
    top = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    return "; ".join("%s = %d" % (k, v) for k, v in top)


def process_day(rows, d, cfg):
    day = Day(d)
    trades, cnt, fc = resolve_trades(rows, cfg, d)
    day.fc, day.cnt = fc, cnt
    pipes = [("sofr_ois", run_ois(trades, d, cfg)), ("cpi_zc", run_cpi(trades, d, cfg))]
    for s in XCCY:
        pipes.append((s, run_xccy(trades, d, cfg, s)))
    extra = {}
    for series, (frows, groups, ex) in pipes:
        day.funnel += [[d, a, b, c, str(e)] for (a, b, c, e) in frows]
        extra[series] = ex
        for (ten, var), recs in groups.items():
            day.groups[(series, ten, var)] = recs
    for n in OIS_TENORS:  # the converted spread has its own cell series (headline only)
        day.groups[("sofr_ois_bey", n, "headline")] = day.groups[("sofr_ois", n, "headline")]
    # cells
    for series, tenors, variants, unit in CELL_DEFS:
        for ten in tenors:
            for var in variants:
                recs = day.groups.get((series, ten, var), [])
                if series == "sofr_ois_bey":
                    vals, scale = [r["bey"] for r in recs], 1e4
                elif unit == "pct":
                    vals, scale = [r["v"] for r in recs], 1e4
                else:
                    vals, scale = [r["v"] for r in recs], 1.0
                floor = FLOOR_TENOR_XCCY if (series in XCCY and ten != "pool1to5") else FLOOR_STD
                if series in ("sofr_ois", "sofr_ois_bey") and var == "headline":
                    floor = (HEADLINE_MIN_N, HEADLINE_MIN_N)   # A1: a headline needs n >= 10 in every file
                st = cell_stats(vals, floor, scale, [r["pkg"] for r in recs])
                if unit == "pct" and st["median"] is not None and not (0.0 < st["median"] < 0.25):
                    raise AssertionError("cell median outside (0, 0.25): %s %s %s" % (series, ten, var))
                day.cs[(series, ten, var)] = st
                day.cells.append(cell_row(d, series, ten, var, unit, st))
    # diagnostics: every statistic obeys the floor (n < 5: blank)
    dg = day.diag

    def put(key, value, n=""):
        dg.append([d, key, value, str(n)])

    for k in ("corr_applied", "corr_changed_terms", "eror_dropped", "revived", "modi_rate_changed", "placeholder_rows"):
        put(k, str(cnt.get(k, 0)))
    for n in OIS_TENORS:
        allp, full = day.groups[("sofr_ois", n, "all_platforms")], day.groups[("sofr_ois", n, "fullday")]
        bilt = [r for r in allp if r["plat"] == "BILT"]
        put("bilt_n_%d" % n, str(len(bilt)))
        if len(bilt) >= 5 and len(full) >= 5:
            mb = q7(sorted(r["v"] for r in bilt), 0.5)
            mf = q7(sorted(r["v"] for r in full), 0.5)
            put("bilt_median_dev_bp_%d" % n, f3((mb - mf) * 1e4), len(bilt))
        st = day.cs[("sofr_ois", n, "fullday")]
        if st["n"] >= 10:
            put("gt10bp_nonbilt_%d" % n, str(sum(1 for r in full if abs(r["v"] - st["median"]) * 1e4 > 10.0)), st["n"])
        byh = collections.defaultdict(list)
        for r in full:
            if r["hr"] is not None:
                byh[r["hr"]].append(r["v"])
        for h in sorted(byh):
            if len(byh[h]) >= 10:
                put("hourly_median_pct_%dy_ny%02d" % (n, h), f6(q7(sorted(byh[h]), 0.5) * 100.0), len(byh[h]))
    put("pct_unit_rows_dropped", str(extra["sofr_ois"]["pct_unit_rows"]))
    nt = collections.Counter()
    uo = 0
    for s in XCCY:
        nt.update(extra[s]["notation"])
        uo += extra[s]["usd_only"]
    for k in ("3", "4", "other"):
        put("xccy_notation_" + k, str(nt.get(k, 0)))
    put("xccy_usd_leg_only", str(uo))
    for s in ("sofr_ois", "cpi_zc") + tuple(XCCY):
        put("unmatched_top10_" + s, unmatched_top10(trades, s))
    return day


# ----------------------------------------------------------------------------------------------------------------------
# the ledger rows of one day  [A1-A4]
# ----------------------------------------------------------------------------------------------------------------------
SPREAD_BANDS = {2: (-35.0, 5.0), 5: (-50.0, -5.0), 10: (-70.0, -15.0), 30: (-110.0, -40.0)}  # conventions lens, its judgement


def blank_row(**kw):
    row = {c: "" for c in LEDGER_COLS}
    row.update(kw)
    return row


def date_status_row(ds, status):
    return [ds, "date_status", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", status]


def make_ledger(day, u):
    """-> (rows as lists, warnings). `u` is Ust.for_date(d) or None."""
    d, out, warns = day.d, [], []
    par = (u or {}).get("par", {})
    real = (u or {}).get("real", {})
    for n in OIS_TENORS:
        hs, fs, ap = (day.cs[("sofr_ois", n, v)] for v in ("headline", "fullday", "all_platforms"))
        bs = day.cs[("sofr_ois_bey", n, "headline")]
        p = par.get(n)
        row = blank_row(date_utc=d, measure="swap_spread", tenor_y=str(n), n=str(hs["n"]), grade="MEASURED",
                        n_fullday=str(fs["n"]), n_allplat=str(ap["n"]), ust_par_pct=fust(p))
        if hs["n"] >= HEADLINE_MIN_N:  # A1: a headline cell needs n >= 10
            row["swap_median_pct"] = f6(hs["median"] * 100.0)
            row["iqr_over_sqrt_n_bp"] = f3(hs["ios"])
            if p is None:
                row["status"] = "no_ust"
            else:
                q = hs["median"] * 1e4 - p * 100.0
                b = bs["median"] * 1e4 - p * 100.0
                if abs(b - q) > 3.0:
                    raise AssertionError("|bey_adj_bp| > 3 at %dy" % n)
                row.update(spread_quoted_bp=f3(q), spread_bey_bp=f3(b), bey_adj_bp=f3(b - q), status="ok")
                lo, hi = SPREAD_BANDS[n]
                if not lo <= q <= hi:
                    warns.append(("warn_spread_%dy_outside_band" % n, "quoted %.3f bp outside [%g, %g]" % (q, lo, hi)))
                if n == 30 and q >= 0:
                    warns.append(("warn_spread_30y_not_negative", "quoted %.3f bp" % q))
                if n == 10 and hs["iqr"] is not None and hs["iqr"] > 5.0:
                    warns.append(("warn_iqr_10y_gt_5bp", "iqr %.3f bp" % hs["iqr"]))
        else:
            row["status"] = "below_min_n" if p is not None else "no_ust"
        if p is not None:
            if fs["median"] is not None:
                row["fullday_quoted_bp"] = f3(fs["median"] * 1e4 - p * 100.0)
            if ap["median"] is not None:
                row["allplat_quoted_bp"] = f3(ap["median"] * 1e4 - p * 100.0)
        out.append(row)
    for n in CPI_TENORS:
        hs = day.cs[("cpi_zc", n, "headline")]
        nom, rl = par.get(n), real.get(n)
        row = blank_row(date_utc=d, measure="cpi_zc_minus_ust_par_be", tenor_y=str(n), n=str(hs["n"]), grade="MEASURED",
                        ust_par_pct=fust(nom), ust_real_pct=fust(rl))
        if hs["median"] is None:
            row["status"] = "below_min_n"
        else:
            row["swap_median_pct"] = f6(hs["median"] * 100.0)
            if hs["ios"] is not None:
                row["iqr_over_sqrt_n_bp"] = f3(hs["ios"])
            if nom is None or rl is None:
                row["status"] = "no_ust"
            else:
                be_simple = nom - rl                                      # percent; IDENTITY
                be_fisher = fisher_breakeven(nom / 100.0, rl / 100.0) * 100.0
                if abs(be_fisher - be_simple) >= 0.1:
                    raise AssertionError("Fisher and simple par breakevens differ by >= 0.1pp at %dy" % n)
                gap_f = (hs["median"] * 100.0 - be_fisher) * 100.0
                gap_s = (hs["median"] * 100.0 - be_simple) * 100.0
                row.update(gap_fisher_bp=f3(gap_f), gap_simple_bp=f3(gap_s), par_be_fisher_pct=f6(be_fisher),
                           status="ok" if hs["n"] >= FLOOR_STD[1] else "thin")
                if not -10.0 <= gap_f <= 60.0:
                    warns.append(("warn_cpi_gap_%dy_outside_band" % n, "gap_fisher %.3f bp outside [-10, 60]" % gap_f))
        out.append(row)
    for s in XCCY:
        for ten in XCCY_TENORS + ("pool1to5",):
            st = day.cs[(s, ten, "headline")]
            row = blank_row(date_utc=d, measure="xccy_basis", pair=PAIR_LABEL[s], tenor_y=str(ten), n=str(st["n"]), grade="MEASURED",
                            status=st["status"])
            if st["median"] is not None:
                row["xccy_median_bp"] = f3(st["median"])
                row["iqr_over_sqrt_n_bp"] = f3(st["ios"])
                if s == "xccy_jpyusd" and ten == "pool1to5" and st["median"] >= 0:
                    warns.append(("warn_jpyusd_pool_not_negative", "median %.3f bp" % st["median"]))
                if s != "xccy_jpyusd" and abs(st["median"]) > 30.0:
                    warns.append(("warn_%s_%s_gt_30bp" % (PAIR_LABEL[s].lower(), ten), "median %.3f bp" % st["median"]))
            out.append(row)
    return [[r[c] for c in LEDGER_COLS] for r in out], warns


# ----------------------------------------------------------------------------------------------------------------------
# cross-date summary: resolution, the CMT slope, the back-fill acceptance numbers  [A1, A14]
# ----------------------------------------------------------------------------------------------------------------------
def _sd(xs):
    n = len(xs)
    if n < 3:
        return None
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def _ols_slope(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


MIN_CROSS = 5   # verifier N4: no cross-date statistic on fewer than 5 dates or pairs


def _min5(x, n):
    return x if n >= MIN_CROSS else ""


def compute_summary(out_dir, ust):
    li = {c: i for i, c in enumerate(LEDGER_COLS)}
    rows = []
    for name in sorted(os.listdir(out_dir)):
        if re.fullmatch(r"ledger_\d{4}\.csv", name):
            rows += read_table(os.path.join(out_dir, name), LEDGER_COLS)
    ledger_dates = sorted({r[0] for r in rows})
    out = []
    if not ledger_dates:
        return out
    cmt = [x for x in ust.cmt_dates() if ledger_dates[0] <= x.isoformat() <= ledger_dates[-1] and x.isoformat() in set(ledger_dates)]
    cmt_s = [x.isoformat() for x in cmt]
    spread = {}
    for r in rows:
        if r[li["measure"]] == "swap_spread" and r[li["status"]] == "ok":
            spread[(int(r[li["tenor_y"]]), r[0])] = float(r[li["spread_quoted_bp"]])
    out.append(["ledger_dates", str(len(ledger_dates)), str(len(ledger_dates))])
    out.append(["cmt_dates_in_ledger", str(len(cmt_s)), str(len(cmt_s))])
    ok10 = sum(1 for x in cmt_s if (10, x) in spread)
    out.append(["share_cmt_dates_headline_10y_n_ge_10", _min5(f4(ok10 / len(cmt_s)) if cmt_s else "", len(cmt_s)), str(len(cmt_s))])
    v30 = [v for (t, x), v in spread.items() if t == 30 and x in set(cmt_s)]
    out.append(["share_30y_quoted_spread_negative", _min5(f4(sum(1 for v in v30 if v < 0) / len(v30)) if v30 else "", len(v30)), str(len(v30))])
    # day-on-day = two ADJACENT Treasury dates (the previous CMT row), both present in the ledger; a gap in the ledger makes no pair
    allc = [x.isoformat() for x in ust.cmt_dates()]
    in_ledger = set(cmt_s)
    prev = {allc[i]: allc[i - 1] for i in range(1, len(allc)) if allc[i] in in_ledger and allc[i - 1] in in_ledger}
    for t in OIS_TENORS:
        dq, dc = [], []
        quiet = []
        for x, p in prev.items():
            if (t, x) in spread and (t, p) in spread and ust.par.get(dt.date.fromisoformat(x), {}).get(t) is not None \
                    and ust.par.get(dt.date.fromisoformat(p), {}).get(t) is not None:
                dspread = spread[(t, x)] - spread[(t, p)]
                dcmt = (ust.par[dt.date.fromisoformat(x)][t] - ust.par[dt.date.fromisoformat(p)][t]) * 100.0
                dq.append(dspread)
                dc.append(dcmt)
                if abs(round(dcmt, 6)) <= 2.0:   # rounded: CMT steps are whole basis points, and float error dropped exact 2bp moves
                    quiet.append(dspread)
        out.append(["dod_sd_quoted_bp_%dy" % t, _min5(f3(_sd(dq)), len(dq)), str(len(dq))])
        out.append(["ols_slope_dspread_on_dcmt_%dy" % t, _min5(f4(_ols_slope(dc, dq)), len(dq)), str(len(dq))])
        if t == 10:
            out.append(["dod_sd_quoted_bp_10y_cmt_move_le_2bp", _min5(f3(_sd(quiet)), len(quiet)), str(len(quiet))])
            small = sum(1 for v in dq if abs(v) < 10.0)
            out.append(["share_dod_abs_change_10y_lt_10bp", _min5(f4(small / len(dq)) if dq else "", len(dq)), str(len(dq))])
            big = []
            for x, p in sorted(prev.items()):
                if (10, x) in spread and (10, p) in spread and abs(spread[(10, x)] - spread[(10, p)]) >= 10.0:
                    big.append("%s: %+.3f" % (x, spread[(10, x)] - spread[(10, p)]))
            out.append(["dod_outliers_10y_ge_10bp", "; ".join(big), str(len(big))])
    return out


# ----------------------------------------------------------------------------------------------------------------------
# build: offline upsert of the weekdays it is given
# ----------------------------------------------------------------------------------------------------------------------
def retrieval(path, name, log_rows):
    saved = [r for r in log_rows if r[5] == "saved" and r[3].endswith("/" + name)]
    if saved:
        return saved[-1][1][:10], "fetch_log"
    m = dt.datetime.fromtimestamp(os.path.getmtime(path), dt.timezone.utc)
    return m.strftime("%Y-%m-%d"), "file_mtime"


def load_funnel_history(out_dir):
    hist = collections.defaultdict(dict)
    for name in sorted(os.listdir(out_dir)):
        if re.fullmatch(r"funnel_\d{4}\.csv", name):
            for r in read_table(os.path.join(out_dir, name), FUNNEL_COLS):
                if r[2] == "F0":
                    hist[r[1]][r[0]] = int(r[4])
    return hist


def f0_warning(prior, n):
    """A5: warn when a series' F0 count is below half its trailing median (needs at least 5 prior dates)."""
    if len(prior) < 5:
        return None
    m = q7(sorted(prior), 0.5)
    return "F0 n %d below half the trailing median %.1f" % (n, m) if n < 0.5 * m else None


def span(values):
    v = sorted(x for x in values if x)
    return (v[0], v[-1]) if v else None


def build(start, end, cache, out_dir, ust_dir, cfg, say=print):
    if start > end:
        raise Refused("--start is after --end")
    assert_window()
    check_cache(cache)
    cache = os.path.expanduser(cache)
    os.makedirs(out_dir, exist_ok=True)
    ust = Ust(ust_dir)
    log_rows = read_table(os.path.join(out_dir, "fetch_log.csv"), FETCH_LOG_COLS)
    dates = list(weekdays(start, end))
    run_set = {x.isoformat() for x in dates}
    hist = load_funnel_history(out_dir)
    for s in hist:
        for x in list(hist[s]):
            if x in run_set:
                del hist[s][x]
    per_year = collections.defaultdict(lambda: {"ledger": [], "cells": [], "funnel": [], "diag": []})
    fs_rows, ust_rows = [], []
    errors = 0
    for d in dates:
        ds, y = d.isoformat(), d.year
        u = ust.for_date(d)
        if u:
            ust_rows.append([ds] + [fust(u["par"].get(n)) for n in (2, 5, 10, 30)] + [fust(u["real"].get(n)) for n in (5, 10, 30)]
                            + [u["par_sha"], u["real_sha"], u["par_fetched"], u["real_fetched"]])
        name = dtcc_name(d)
        path = os.path.join(cache, name)
        bucket_y = per_year[y]
        if not os.path.exists(path):
            bucket_y["ledger"].append(date_status_row(ds, "no_file"))
            say("%s  no_file" % ds)
            continue
        info = None
        try:
            rows, info = read_zip(path, d)
            got, src = retrieval(path, name, log_rows)
            day = process_day(rows, ds, cfg)
            lrows, warns = make_ledger(day, u)
            for fr in day.funnel:  # F0 against its trailing 20-date median (A5)
                if fr[2] == "F0":
                    prior = [hist[fr[1]][k] for k in sorted(hist[fr[1]]) if k < ds][-20:]
                    w = f0_warning(prior, int(fr[4]))
                    if w:
                        warns.append(("warn_f0_low_" + fr[1], w))
                    hist[fr[1]][ds] = int(fr[4])
        except SchemaMismatch as e:
            bucket_y["ledger"].append(date_status_row(ds, "schema_mismatch"))
            say("%s  schema_mismatch: %s" % (ds, e))
            continue
        except (AssertionError, zipfile.BadZipFile, KeyError, ValueError) as e:
            bucket_y["ledger"].append(date_status_row(ds, "error"))
            say("%s  ERROR: %s" % (ds, str(e)[:200]))
            errors += 1
            continue
        fc = day.fc
        fs_rows.append([ds, info["zip_name"], info["zip_kb"], info["zip_sha256"], info["zip_md5"], info["csv_kb"], info["csv_sha256"],
                        str(len(rows)), "1"] + [str(fc.get(k, 0)) for k in FILE_STATS_COLS[9:27]] + [got, src])
        bucket_y["ledger"] += lrows
        bucket_y["cells"] += day.cells
        bucket_y["funnel"] += day.funnel
        day.diag.append([ds, "header_added", str(len(info["added"])), ""])
        day.diag.append([ds, "header_removed", str(len(info["removed"])), ""])
        if info["added"]:
            day.diag.append([ds, "header_added_names", "; ".join(info["added"]), ""])
        if info["removed"]:
            day.diag.append([ds, "header_removed_names", "; ".join(info["removed"]), ""])
        for k, v in warns:
            say("%s  WARN %s: %s" % (ds, k, v))
            day.diag.append([ds, k, v, ""])
        bucket_y["diag"] += day.diag
        h = {(r[2], r[3]): r for r in lrows}
        say("%s  ok  rows=%d  sofr_ois headline n=%s  swap_spread(quoted bp)=%s" % (
            ds, len(rows), "/".join(r[4] for r in lrows[:4]), "/".join(r[5] or "-" for r in lrows[:4])))
    # --- write: file_stats and ust_used first (the source lines of the others read them)
    fs_path, ust_path = os.path.join(out_dir, "file_stats.csv"), os.path.join(out_dir, "ust_used.csv")
    fs_all = upsert_table(fs_path, FILE_STATS_COLS, fs_rows, run_set,
                          lambda rows: source_line(span([r[27] for r in rows])))
    ust_all = upsert_table(ust_path, UST_COLS, ust_rows, run_set,
                           lambda rows: source_line(None, span([r[11] for r in rows] + [r[10] for r in rows]),
                                                    "Treasury CMT values joined by date"))
    fs_ret = {r[0]: r[27] for r in fs_all}
    ust_ret = {r[0]: [r[10], r[11]] for r in ust_all}

    def src_for(rows):
        ds_ = {r[0] for r in rows}
        sp_d = span([fs_ret[x] for x in ds_ if x in fs_ret])
        sp_u = span([v for x in ds_ if x in ust_ret for v in ust_ret[x]])
        return source_line(sp_d, sp_u)

    def src_dtcc_only(rows):
        ds_ = {r[0] for r in rows}
        return source_line(span([fs_ret[x] for x in ds_ if x in fs_ret]))

    for y, parts in sorted(per_year.items()):
        ydates = {x for x in run_set if x.startswith("%04d-" % y)}
        upsert_table(os.path.join(out_dir, "ledger_%04d.csv" % y), LEDGER_COLS, parts["ledger"], ydates, src_for)
        upsert_table(os.path.join(out_dir, "cells_%04d.csv" % y), CELLS_COLS, parts["cells"], ydates, src_dtcc_only)
        upsert_table(os.path.join(out_dir, "funnel_%04d.csv" % y), FUNNEL_COLS, parts["funnel"], ydates, src_dtcc_only)
        upsert_table(os.path.join(out_dir, "diagnostics_%04d.csv" % y), DIAG_COLS, parts["diag"], ydates, src_dtcc_only)
    summ = compute_summary(out_dir, ust)
    allret = span([r[27] for r in fs_all])
    write_table(os.path.join(out_dir, "summary.csv"), SUMMARY_COLS, summ, source_line(allret, None, "recomputed from the ledger files at every build"))
    with open(os.path.join(out_dir, "SOURCES.md"), "w", encoding="utf-8", newline="") as f:
        f.write(SOURCES_TEXT)
    return errors


# ----------------------------------------------------------------------------------------------------------------------
# selftest: synthetic tape (ids T0001..., dates in 2030, no DTCC content), pure checks, stop logic, mutants
# ----------------------------------------------------------------------------------------------------------------------
class Checks:
    def __init__(self):
        self.items = []

    def ok(self, name, cond, detail=""):
        self.items.append((name, bool(cond), "" if cond else detail))

    def eq(self, name, got, want):
        self.ok(name, got == want, "got %r, want %r" % (got, want))

    def near(self, name, got, want, tol):
        self.ok(name, got is not None and abs(got - want) <= tol, "got %r, want %r +- %r" % (got, want, tol))

    def raises(self, name, exc, fn):
        try:
            fn()
        except exc:
            self.ok(name, True)
        except Exception as e:  # wrong exception type
            self.ok(name, False, "raised %s" % type(e).__name__)
        else:
            self.ok(name, False, "did not raise")

    def failed(self):
        return [(n, d) for n, c, d in self.items if not c]


FX_DAY = "2030-03-12"   # a Tuesday in EDT (US DST began 2030-03-10)
FX_WIN = "2030-01-15"   # a Tuesday in EST
FX_EFF, FX_EXP = "2030-03-14", {1: "2031-03-14", 2: "2032-03-14", 3: "2033-03-14", 4: "2034-03-14", 5: "2035-03-14",
                                10: "2040-03-14", 30: "2060-03-14"}


class Tape:
    def __init__(self):
        self.rows, self.n = [], 0

    def add(self, fields):
        self.n += 1
        r = {h: "" for h in HEADER_V1}
        r["Dissemination Identifier"] = "T%04d" % self.n
        r.update(fields)
        self.rows.append(r)
        return r["Dissemination Identifier"]

    def child(self, parent_id, action, ts, base=None, **over):
        f = dict(base or {})
        f.update({"Action type": action, "Event type": "", "Event timestamp": ts, "Original Dissemination Identifier": parent_id})
        f.update(over)
        return self.add(f)


def fx_ts(h, m=0, s=0, day=FX_DAY):
    return "%sT%02d:%02d:%02dZ" % (day, h, m, s)


def fx_ois(rate, ts, tenor=10, leg="1", plat="TWSF", und="USD-SOFR-OIS Compound", dc="A004", per="YEAR", mul="1", eff=FX_EFF, exp=None,
           fisn="NA/Swap OIS USD", **over):
    f = {"Action type": "NEWT", "Event type": "TRAD", "Event timestamp": ts, "Execution Timestamp": ts, "Effective Date": eff,
         "Expiration Date": exp or FX_EXP[tenor], "Platform identifier": plat, "Notional currency-Leg 1": "USD",
         "Notional currency-Leg 2": "USD", "Post-priced swap indicator": "false", "Non-standardized term indicator": "FALSE",
         "Package indicator": "FALSE", "UPI FISN": fisn, "UPI Underlier Name": und,
         "Fixed rate-Leg " + leg: str(rate), "Fixed rate day count convention-leg " + leg: dc,
         "Fixed rate payment frequency period-Leg " + leg: per, "Fixed rate payment frequency period multiplier-Leg " + leg: mul}
    f.update(over)
    return f


def fx_xccy(ccy, bp, tenor, ts, usd_leg="1", notation="3", fisn=None, und=None, other_type="PEXH;PEXH", **over):
    x_leg = "2" if usd_leg == "1" else "1"
    val = str(bp / 10000.0) if notation == "3" else str(bp)
    f = {"Action type": "NEWT", "Event type": "TRAD", "Event timestamp": ts, "Execution Timestamp": ts, "Effective Date": FX_EFF,
         "Expiration Date": FX_EXP[tenor], "Platform identifier": "TPSE", "Post-priced swap indicator": "false",
         "Non-standardized term indicator": "FALSE", "Package indicator": "FALSE",
         "Notional currency-Leg " + usd_leg: "USD", "Notional currency-Leg " + x_leg: ccy,
         "Spread-Leg " + x_leg: val, "Spread notation-Leg " + x_leg: notation, "Spread-Leg " + usd_leg: "0",
         "Spread notation-Leg " + usd_leg: "3", "Other payment type": other_type, "Other payment amount": "1;2",
         "UPI FISN": fisn or "NA/Swap Flt Flt %s USD" % ccy,
         "UPI Underlier Name": und or {"EUR": "EUR-EuroSTR-OIS Compound vs USD-SOFR-OIS Compound",
                                       "GBP": "GBP-SONIA-OIS Compound vs USD-SOFR-OIS Compound",
                                       "JPY": "JPY-TONA-OIS Compound vs USD-SOFR-OIS Compound"}[ccy]}
    f.update(over)
    return f


def fx_cpi(rate, ts, tenor, per="EXPI", mul="1", plat="TWSF", **over):
    f = fx_ois(rate, ts, tenor, plat=plat, und="USA-CPI-U", per=per, mul=mul, fisn="NA/Swap Infl Idx USD", dc="A020")
    f.update(over)
    return f


def build_fixture_tape():
    t = Tape()
    # --- sofr_ois 10y, in the window (18:30:00Z <= t < 20:30:00Z in EDT): six at 0.0479, six at 0.0481 -----------------------
    for hh, mm in ((18, 30), (18, 45), (19, 15), (19, 30), (19, 45)):
        t.add(fx_ois(0.0479, fx_ts(hh, mm)))
    modi_parent = t.add(fx_ois(0.0479, fx_ts(19, 0)))
    t.child(modi_parent, "MODI", fx_ts(19, 1), fx_ois(0.0700, fx_ts(19, 0)))   # a MODI changing the rate: ignored, counted
    for hh, mm, ss in ((20, 0, 0), (20, 10, 0), (20, 20, 0), (20, 29, 59)):
        t.add(fx_ois(0.0481, fx_ts(hh, mm, ss)))
    a = t.add(fx_ois(0.0600, fx_ts(19, 50)))                                    # wrong, then corrected twice (depth 2) to 0.0481
    c1 = t.child(a, "CORR", fx_ts(19, 52), fx_ois(0.0550, fx_ts(19, 50)))
    t.child(c1, "CORR", fx_ts(19, 55), fx_ois(0.0481, fx_ts(19, 50)))
    b = t.add(fx_ois(0.0481, fx_ts(19, 55)))                                    # a bogus CORR that is itself an error: ignored
    cb = t.child(b, "CORR", fx_ts(19, 56), fx_ois(0.0999, fx_ts(19, 55)))
    t.child(cb, "EROR", fx_ts(19, 57), {})
    # --- out of the window, not BILT: 14 at 0.0500 (08:00 NY, and one second either side of the window) ----------------------
    for k in range(12):
        t.add(fx_ois(0.0500, fx_ts(12, 0, k)))
    t.add(fx_ois(0.0500, fx_ts(18, 29, 59)))
    t.add(fx_ois(0.0500, fx_ts(20, 30, 0)))
    # --- BILT, in the window: 3 at 0.0420 (only in all_platforms) -------------------------------------------------------------
    for k in range(3):
        t.add(fx_ois(0.0420, fx_ts(19, k), plat="BILT"))
    # --- an errored trade (dropped; the noeror mutant lets it in) ------------------------------------------------------------
    g4 = t.add(fx_ois(0.0490, fx_ts(19, 15, 30)))
    t.child(g4, "EROR", fx_ts(19, 16), {})
    # --- 5y: three on leg 1, two with the fixed rate on leg 2, one with its conventions only on the other leg ---------------
    for k in range(3):
        t.add(fx_ois(0.0470, fx_ts(19, 10 + k), tenor=5))
    for k in range(2):
        t.add(fx_ois(0.0472, fx_ts(19, 20 + k), tenor=5, leg="2"))
    t.add(fx_ois(0.0472, fx_ts(19, 30), tenor=5, dc="", per="", mul="",
                 **{"Fixed rate day count convention-leg 2": "A004", "Fixed rate payment frequency period-Leg 2": "YEAR",
                    "Fixed rate payment frequency period multiplier-Leg 2": "1"}))
    for k in range(3):                                                           # 2y: three
        t.add(fx_ois(0.0450, fx_ts(19, 40 + k), tenor=2))
    # --- the excluded rows, each at 0.0300 so that a leak would move a median ------------------------------------------------
    low = 0.0300
    t.add(fx_ois(low, fx_ts(19, 5), **{"Event type": "COMP"}))                      # not a trade
    t.add(fx_ois(low, "%sT19:00:00Z" % "2030-03-11"))                                 # F1 other day
    t.add(fx_ois(low, "2000-01-01T00:00:00Z"))                                        # F1 placeholder
    t.add(fx_ois(low, fx_ts(19, 6), eff="2030-03-10", exp="2040-03-10"))               # F2 backdated
    t.add(fx_ois(low, fx_ts(19, 7), eff="2030-03-30", exp="2040-03-30"))               # F2 forward start
    t.add(fx_ois(low, fx_ts(19, 8), **{"Other payment amount": "1000.0", "Other payment type": "UFRO"}))   # F3 upfront
    t.add(fx_ois(low, fx_ts(19, 9), **{"Post-priced swap indicator": "true"}))        # F4
    t.add(fx_ois(low, fx_ts(19, 10), **{"Non-standardized term indicator": "TRUE"}))  # F4
    t.add(fx_ois(low, fx_ts(19, 11), **{"Strike Price": "0.045"}))                    # F4s
    t.add(fx_ois(low, fx_ts(19, 12), **{"Fixed rate-Leg 2": "0.0310"}))               # F5 two fixed rates
    t.add(fx_ois(low, fx_ts(19, 13), **{"Fixed rate-Leg 1": ""}))                     # F5 none
    t.add(fx_ois(low, fx_ts(19, 14), dc="A001"))                                      # F6 day count
    t.add(fx_ois(low, fx_ts(19, 15), dc="", per="", mul=""))                          # F6 conventions blank on both legs
    t.add(fx_ois(low, fx_ts(19, 16), per="EXPI"))                                     # F6 zero-coupon frequency
    t.add(fx_ois(4.8, fx_ts(19, 17)))                                                 # F6u percent units
    t.add(fx_ois(low, fx_ts(19, 18), und="USD-SOFR"))                                 # F0 other index (listed as unmatched)
    # --- CPI zero-coupon -----------------------------------------------------------------------------------------------------
    for k in range(3):
        t.add(fx_cpi(0.0245, fx_ts(10, k), 5))
        t.add(fx_cpi(0.0247, fx_ts(10, 10 + k), 5, per="YEAR", mul="5"))
    t.add(fx_cpi(0.0300, fx_ts(10, 20), 5, plat="BILT"))                              # all_platforms only
    t.add(fx_cpi(0.0300, fx_ts(10, 21), 5, **{"Other payment amount": "5000"}))       # F3
    t.add(fx_cpi(0.0300, fx_ts(10, 22), 5, per="YEAR", mul="3"))                      # F7: YEAR 3 on a 5y bucket
    for k in range(5):
        t.add(fx_cpi(0.0240, fx_ts(11, k), 10))
        t.add(fx_cpi(0.0242, fx_ts(19, 30 + k), 10))                                  # these five are inside the window
    # --- cross-currency ------------------------------------------------------------------------------------------------------
    ts0 = fx_ts(9, 0)
    eur = [(-4.0, 1, "1", "3"), (-4.0, 1, "2", "3"), (-3.0, 1, "1", "3"), (-3.0, 2, "1", "3"), (-3.0, 2, "2", "3"), (-3.0, 2, "1", "3"),
           (-3.0, 3, "1", "3"), (-3.0, 3, "2", "3"), (-2.5, 4, "1", "4"), (-2.0, 4, "2", "3"), (-2.0, 5, "1", "3"), (-1.0, 5, "2", "3")]
    for i, (bp, ten, usd_leg, nt) in enumerate(eur):
        t.add(fx_xccy("EUR", bp, ten, fx_ts(9, i), usd_leg=usd_leg, notation=nt))
    t.add(fx_xccy("EUR", -9.0, 1, ts0, other_type="UFRO;PEXH"))                       # F3 upfront
    t.add(fx_xccy("EUR", -9.0, 1, ts0, und="EUR-EURIBOR-Reuters vs USD-SOFR-OIS Compound"))   # F0 EURIBOR label
    t.add(fx_xccy("EUR", -60.0, 1, ts0))                                              # F6 cap breach (50bp for EUR)
    t.add(fx_xccy("EUR", -9.0, 1, ts0, notation="3", **{"Spread notation-Leg 2": "2", "Spread notation-Leg 1": "2"}))  # F6 notation
    t.add(fx_xccy("EUR", -9.0, 1, ts0, **{"Spread-Leg 2": "", "Spread-Leg 1": "-0.0002"}))      # spread on the USD leg only
    t.add(fx_xccy("EUR", -9.0, 1, "2030-03-11T09:00:00Z"))                            # F1 other day
    t.add(fx_xccy("EUR", -9.0, 1, ts0, **{"Post-priced swap indicator": "true"}))      # F4
    t.add(fx_xccy("EUR", -9.0, 1, ts0, **{"Fixed rate-Leg 1": "0.04"}))                 # F5
    for bp, ten in ((2.5, 1), (2.5, 1), (2.5, 2), (2.0, 4), (1.5, 5)):
        t.add(fx_xccy("GBP", bp, ten, ts0))
    t.add(fx_xccy("JPY", 75.0, 5, ts0))                                               # kept: the JPY cap is 100bp
    t.add(fx_xccy("JPY", 120.0, 5, ts0))                                              # dropped
    t.add(fx_xccy("JPY", -10.0, 5, ts0))
    return t


def build_winter_tape():
    t = Tape()
    for k in range(12):                                   # in the EST window: 19:30:00Z <= t < 21:30:00Z
        m = 30 + 10 * k                                   # 19:30, 19:40, ... 21:20
        t.add(fx_ois(0.0480, fx_ts(19 + m // 60, m % 60, 0, FX_WIN), eff="2030-01-17", exp="2040-01-17"))
    for k in range(4):                                    # inside an EDT window, outside the EST one
        t.add(fx_ois(0.0300, fx_ts(18, 45, k, FX_WIN), eff="2030-01-17", exp="2040-01-17"))
    for k in range(4):                                    # outside both
        t.add(fx_ois(0.0300, fx_ts(21, 45, k, FX_WIN), eff="2030-01-17", exp="2040-01-17"))
    return t


FX_PAR_CSV = ('Date,"1 Mo","2 Yr","5 Yr","10 Yr","30 Yr"\n"03/12/2030",4.10,4.40,4.60,4.90,5.20\n"01/15/2030",4.10,4.30,4.50,4.80,5.10\n')
FX_REAL_CSV = ('Date,"5 YR","7 YR","10 YR","20 YR","30 YR"\n03/12/2030,2.20,2.30,2.50,2.60,2.70\n01/15/2030,2.10,2.20,2.40,2.50,2.60\n')


def tape_to_zip(tape, d):
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(HEADER_V1)
    for r in tape.rows:
        w.writerow([r[h] for h in HEADER_V1])
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(dtcc_name(d, "csv"), buf.getvalue().encode("utf-8"))
    return out.getvalue()


def make_fixture_dirs(root):
    cache, ust = os.path.join(root, "cache"), os.path.join(root, "ust")
    os.makedirs(cache)
    os.makedirs(ust)
    for tape, ds in ((build_fixture_tape(), FX_DAY), (build_winter_tape(), FX_WIN)):
        d = dt.date.fromisoformat(ds)
        p = os.path.join(cache, dtcc_name(d))
        with open(p, "wb") as f:
            f.write(tape_to_zip(tape, d))
        os.utime(p, (1792000000, 1792000000))   # a fixed mtime keeps the retrieval date stable
    for kind, txt in (("daily_treasury_yield_curve", FX_PAR_CSV), ("daily_treasury_real_yield_curve", FX_REAL_CSV)):
        with open(os.path.join(ust, "%s_2030_fetched-20300401.csv" % kind), "w", encoding="utf-8", newline="") as f:
            f.write(txt)
    return cache, ust


def _t(out, name):
    return read_table(os.path.join(out, name))


def fixture_checks(out, tape_rows):
    ck = Checks()
    cells = {(r[0], r[1], r[2], r[3]): r for r in _t(out, "cells_2030.csv")}
    ledger = {(r[0], r[1], r[2], r[3]): r for r in _t(out, "ledger_2030.csv")}
    fun = {(r[0], r[1], r[2], r[3]): r[4] for r in _t(out, "funnel_2030.csv")}
    diag = {(r[0], r[1]): r for r in _t(out, "diagnostics_2030.csv")}
    D = FX_DAY
    LC = {c: i for i, c in enumerate(LEDGER_COLS)}
    CC = {c: i for i, c in enumerate(CELLS_COLS)}

    def cl(series, ten, var, col):
        r = cells.get((D, series, str(ten), var))
        return None if r is None else r[CC[col]]

    def lg(measure, pair, ten, col, d=D):
        r = ledger.get((d, measure, pair, str(ten)))
        return None if r is None else r[LC[col]]

    for step, want in (("F0", 52), ("F1", 50), ("F2", 48), ("F3", 47), ("F4", 45), ("F4s", 44), ("F5", 42), ("F6", 39), ("F6u", 38)):
        ck.eq("funnel sofr_ois %s" % step, fun.get((D, "sofr_ois", step, "")), str(want))
    for step, want in (("F7", (3, 6, 29, 0)), ("F8", (3, 6, 26, 0)), ("F9", (3, 6, 12, 0))):
        got = tuple(fun.get((D, "sofr_ois", step, str(n))) for n in OIS_TENORS)
        ck.eq("funnel sofr_ois %s 2/5/10/30" % step, got, tuple(str(w) for w in want))
    ck.eq("cell 10y headline n/median/status", (cl("sofr_ois", 10, "headline", "n"), cl("sofr_ois", 10, "headline", "median"),
                                                cl("sofr_ois", 10, "headline", "status")), ("12", "4.800000", "ok"))
    ck.eq("cell 10y fullday n/median", (cl("sofr_ois", 10, "fullday", "n"), cl("sofr_ois", 10, "fullday", "median")), ("26", "5.000000"))
    ck.eq("cell 10y all_platforms n/median", (cl("sofr_ois", 10, "all_platforms", "n"), cl("sofr_ois", 10, "all_platforms", "median")),
          ("29", "4.810000"))
    ck.eq("cell 5y headline n/median/status", (cl("sofr_ois", 5, "headline", "n"), cl("sofr_ois", 5, "headline", "median"),
                                               cl("sofr_ois", 5, "headline", "status")), ("6", "", "below_min_n"))   # A1: a headline needs n >= 10
    ck.eq("thin cell publishes no quartiles", (cl("sofr_ois", 5, "headline", "q1"), cl("sofr_ois", 5, "headline", "iqr_bp")), ("", ""))
    ck.eq("cell 2y n=3 publishes the count only", (cl("sofr_ois", 2, "headline", "n"), cl("sofr_ois", 2, "headline", "median"),
                                                  cl("sofr_ois", 2, "headline", "status")), ("3", "", "below_min_n"))
    ck.eq("cell 10y quartiles (type 7)", (cl("sofr_ois", 10, "headline", "q1"), cl("sofr_ois", 10, "headline", "q3"),
                                          cl("sofr_ois", 10, "headline", "iqr_bp"), cl("sofr_ois", 10, "headline", "iqr_over_sqrt_n_bp")),
          ("4.790000", "4.810000", "2.000", "0.577"))
    ck.eq("cell 10y converted median (pct)", cl("sofr_ois_bey", 10, "headline", "median"), "4.812760")
    ck.eq("ledger 10y quoted / bey / adj", (lg("swap_spread", "", 10, "spread_quoted_bp"), lg("swap_spread", "", 10, "spread_bey_bp"),
                                            lg("swap_spread", "", 10, "bey_adj_bp")), ("-10.000", "-8.724", "1.276"))
    ck.eq("ledger 10y fullday / all_platforms quoted", (lg("swap_spread", "", 10, "fullday_quoted_bp"), lg("swap_spread", "", 10, "n_fullday"),
                                                        lg("swap_spread", "", 10, "allplat_quoted_bp"), lg("swap_spread", "", 10, "n_allplat")),
          ("10.000", "26", "-9.000", "29"))
    ck.eq("ledger 10y status and iqr/sqrt(n)", (lg("swap_spread", "", 10, "status"), lg("swap_spread", "", 10, "iqr_over_sqrt_n_bp")),
          ("ok", "0.577"))
    ck.eq("ledger 5y: n=6 is below the headline floor of 10", (lg("swap_spread", "", 5, "status"), lg("swap_spread", "", 5, "spread_quoted_bp"),
                                                               lg("swap_spread", "", 5, "fullday_quoted_bp")), ("below_min_n", "", "11.000"))
    ck.eq("ledger 30y has no trades", (lg("swap_spread", "", 30, "n"), lg("swap_spread", "", 30, "status")), ("0", "below_min_n"))
    # CPI
    ck.eq("cpi funnel F7 5/10/30 (the BILT row is still in)", tuple(fun.get((D, "cpi_zc", "F7", str(n))) for n in CPI_TENORS), ("7", "10", "0"))
    ck.eq("cpi funnel F8 5/10/30", tuple(fun.get((D, "cpi_zc", "F8", str(n))) for n in CPI_TENORS), ("6", "10", "0"))
    ck.eq("cpi 5y headline / all_platforms n", (cl("cpi_zc", 5, "headline", "n"), cl("cpi_zc", 5, "all_platforms", "n")), ("6", "7"))
    ck.eq("cpi 5y median", cl("cpi_zc", 5, "headline", "median"), "2.460000")
    ck.eq("cpi 5y gap simple / fisher / par breakeven", (lg("cpi_zc_minus_ust_par_be", "", 5, "gap_simple_bp"),
                                                         lg("cpi_zc_minus_ust_par_be", "", 5, "gap_fisher_bp"),
                                                         lg("cpi_zc_minus_ust_par_be", "", 5, "par_be_fisher_pct"),
                                                         lg("cpi_zc_minus_ust_par_be", "", 5, "status")),
          ("6.000", "7.202", "2.387976", "thin"))
    ck.eq("cpi 10y n / status / gap simple", (lg("cpi_zc_minus_ust_par_be", "", 10, "n"), lg("cpi_zc_minus_ust_par_be", "", 10, "status"),
                                              lg("cpi_zc_minus_ust_par_be", "", 10, "gap_simple_bp")), ("10", "ok", "1.000"))
    ck.eq("cpi cmt_window n 5y/10y", (cl("cpi_zc", 5, "cmt_window", "n"), cl("cpi_zc", 10, "cmt_window", "n")), ("0", "5"))
    # cross-currency
    ck.eq("xccy_eurusd funnel F0..F7", tuple(fun.get((D, "xccy_eurusd", s, t)) for s, t in (("F0", ""), ("F1", ""), ("F3", ""), ("F4", ""),
                                                                                           ("F5", ""), ("F6", ""))), ("19", "18", "17", "16", "15", "12"))
    ck.eq("xccy_eurusd F7 1..5", tuple(fun.get((D, "xccy_eurusd", "F7", str(n))) for n in XCCY_TENORS), ("3", "3", "2", "2", "2"))
    ck.eq("xccy_eurusd per-tenor cells below 10 publish nothing", (lg("xccy_basis", "EURUSD", 1, "n"), lg("xccy_basis", "EURUSD", 1, "xccy_median_bp"),
                                                                lg("xccy_basis", "EURUSD", 1, "status")), ("3", "", "below_min_n"))
    ck.eq("xccy_eurusd pool1to5 n / median / ios / status", (lg("xccy_basis", "EURUSD", "pool1to5", "n"),
                                                             lg("xccy_basis", "EURUSD", "pool1to5", "xccy_median_bp"),
                                                             lg("xccy_basis", "EURUSD", "pool1to5", "iqr_over_sqrt_n_bp"),
                                                             lg("xccy_basis", "EURUSD", "pool1to5", "status")), ("12", "-3.000", "0.180", "ok"))
    ck.eq("xccy_gbpusd pool1to5 n / median / status", (lg("xccy_basis", "GBPUSD", "pool1to5", "n"), lg("xccy_basis", "GBPUSD", "pool1to5", "xccy_median_bp"),
                                                       lg("xccy_basis", "GBPUSD", "pool1to5", "status")), ("5", "2.500", "thin"))
    ck.eq("xccy_jpyusd cap 100bp (75 kept, 120 dropped)", (lg("xccy_basis", "JPYUSD", "pool1to5", "n"), lg("xccy_basis", "JPYUSD", "pool1to5", "status")),
          ("2", "below_min_n"))
    ck.eq("xccy notation 3/4/other and usd-leg-only counts", (diag[(D, "xccy_notation_3")][2], diag[(D, "xccy_notation_4")][2],
                                                             diag[(D, "xccy_notation_other")][2], diag[(D, "xccy_usd_leg_only")][2]),
          ("20", "1", "1", "1"))
    # diagnostics
    ck.eq("diagnostics resolution counters", tuple(diag[(D, k)][2] for k in ("corr_applied", "corr_changed_terms", "eror_dropped", "revived",
                                                                          "modi_rate_changed", "placeholder_rows", "pct_unit_rows_dropped")),
          ("1", "1", "1", "0", "1", "1", "1"))
    ck.eq("diagnostics bilt_n_10 and floor on the BILT deviation (n=3: absent)", (diag[(D, "bilt_n_10")][2], (D, "bilt_median_dev_bp_10") in diag),
          ("3", False))
    ck.eq("diagnostics hourly median: only hours with n >= 10", ((D, "hourly_median_pct_10y_ny08") in diag, (D, "hourly_median_pct_10y_ny15") in diag,
                                                                 diag[(D, "hourly_median_pct_10y_ny08")][2:] if (D, "hourly_median_pct_10y_ny08") in diag else None),
          (True, False, ["5.000000", "12"]))
    ck.ok("diagnostics list the unmatched sofr label", "USD-SOFR = 1" in (diag.get((D, "unmatched_top10_sofr_ois")) or ["", "", ""])[2])
    ck.ok("diagnostics list the EURIBOR label", "EURIBOR" in (diag.get((D, "unmatched_top10_xccy_eurusd")) or ["", "", ""])[2])
    # file stats
    fs = {r[0]: r for r in _t(out, "file_stats.csv")}
    cnt = collections.Counter(r["Action type"] for r in tape_rows)
    row = fs.get(D)
    ck.ok("file_stats row", row is not None)
    if row:
        F = {c: i for i, c in enumerate(FILE_STATS_COLS)}
        ck.eq("file_stats rows / NEWT / CORR / MODI / EROR", (row[F["rows"]], row[F["n_NEWT"]], row[F["n_CORR"]], row[F["n_MODI"]], row[F["n_EROR"]]),
              (str(len(tape_rows)), str(cnt["NEWT"]), str(cnt["CORR"]), str(cnt["MODI"]), str(cnt["EROR"])))
        ck.eq("file_stats header_ok / COMP / placeholder", (row[F["header_ok"]], row[F["newt_COMP"]], row[F["newt_exec_placeholder"]]), ("1", "1", "1"))
    # winter date: the window is 19:30-21:30 UTC in EST
    r = cells.get((FX_WIN, "sofr_ois", "10", "headline"))
    ck.eq("EST date 2030-01-15: 10y headline n/median", None if r is None else (r[CC["n"]], r[CC["median"]]), ("12", "4.800000"))
    r = cells.get((FX_WIN, "sofr_ois", "10", "fullday"))
    ck.eq("EST date 2030-01-15: 10y fullday n", None if r is None else r[CC["n"]], "20")
    # ust_used
    uu = {r[0]: r for r in _t(out, "ust_used.csv")}
    ck.eq("ust_used values 2030-03-12", uu.get(D, [None] * 8)[1:8], ["4.40", "4.60", "4.90", "5.20", "2.20", "2.50", "2.70"])
    return ck


def wire_check(ck):
    """What real_opener puts on the wire, seen by a loopback server (no external network): GET, and exactly the
    User-Agent, Accept-Encoding and Host headers -- no cookie, no authorization, no referer."""
    import http.server
    import threading
    seen = []

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append((self.command, self.path, dict(self.headers)))
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *a):
            pass

    name = "wire: real_opener sends GET with only User-Agent, Accept-Encoding and Host"
    try:
        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    except OSError:
        ck.ok(name + " (skipped: no loopback socket)", True)
        return
    port = srv.server_address[1]
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    orig = http.client.HTTPSConnection
    http.client.HTTPSConnection = lambda host, timeout: http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    try:
        status, body = real_opener("pddata.dtcc.com", DTCC_PREFIX + "x.zip", HEADERS, 5, 1000)
    finally:
        http.client.HTTPSConnection = orig
        srv.shutdown()
        srv.server_close()
    ok = bool(seen) and seen[0][0] == "GET" and sorted(seen[0][2]) == ["Accept-Encoding", "Host", "User-Agent"] \
        and seen[0][2]["User-Agent"] == UA and seen[0][2]["Accept-Encoding"] == "identity" and (status, body) == (200, b"ok")
    ck.ok(name, ok, str(seen))


def pure_checks():
    ck = Checks()
    ck.near("bey(0.048) - 0.048 at 365/360 = +0.885bp", (bey(0.048) - 0.048) * 1e4, 0.885, 0.001)
    ck.ok("run-time New York window guard passes on the real window", assert_window() is None)
    ck.eq("cross-date statistics need 5 dates or pairs", (_min5("x", 4), _min5("x", 5)), ("", "x"))
    ck.near("bey(0.05556) = 0.05556 (the sign flips at 5.556%)", bey(0.05556) * 1e4, 555.6, 0.01)
    ck.near("bey(0.10) - 0.10 = -10.585bp", (bey(0.10) - 0.10) * 1e4, -10.585, 0.001)
    ck.eq("type-7 quartiles of [1,2,3,4]", (q7([1, 2, 3, 4], 0.25), q7([1, 2, 3, 4], 0.5), q7([1, 2, 3, 4], 0.75)), (1.75, 2.5, 3.25))
    e = dt.date(2030, 3, 14)
    ck.eq("bucket: +7 days in", bucket(e, add_years(e, 10) + dt.timedelta(days=7), (2, 5, 10, 30)), 10)
    ck.eq("bucket: +8 days out", bucket(e, add_years(e, 10) + dt.timedelta(days=8), (2, 5, 10, 30)), None)
    ck.eq("bucket: -7 days in", bucket(e, add_years(e, 5) - dt.timedelta(days=7), (2, 5, 10, 30)), 5)
    ck.eq("29 Feb 2028 + 2y -> 28 Feb 2030", add_years(dt.date(2028, 2, 29), 2), dt.date(2030, 2, 28))
    ck.eq("window EDT: 18:29:59Z out, 18:30:00Z in, 20:29:59Z in, 20:30:00Z out",
          tuple(in_window("2030-03-12T%sZ" % t) for t in ("18:29:59", "18:30:00", "20:29:59", "20:30:00")), (False, True, True, False))
    ck.eq("window EST: 19:29:59Z out, 19:30:00Z in, 21:29:59Z in, 21:30:00Z out",
          tuple(in_window("2030-01-15T%sZ" % t) for t in ("19:29:59", "19:30:00", "21:29:59", "21:30:00")), (False, True, True, False))
    ck.eq("fisher breakeven (n=4.6%, r=2.2%) in pct", format(fisher_breakeven(0.046, 0.022) * 100, ".6f"), "2.387976")
    ck.eq("floor: n=4 / 5 / 9 / 10 statuses", tuple(cell_stats([1.0] * n, FLOOR_STD, 1.0)["status"] for n in (4, 5, 9, 10)),
          ("below_min_n", "thin", "thin", "ok"))
    s4 = cell_stats([1.0, 2.0, 3.0, 4.0], FLOOR_STD, 1.0)
    ck.eq("floor: n=4 holds no statistic at all", (s4["median"], s4["q1"], s4["iqr"], s4["share_gt10"]), (None, None, None, None))
    s7 = cell_stats([1.0] * 7, FLOOR_STD, 1.0)
    ck.eq("floor: n=7 holds a median and no quartile", (s7["median"], s7["q1"]), (1.0, None))
    ck.eq("floor: per-tenor xccy has no thin level", cell_stats([1.0] * 9, FLOOR_TENOR_XCCY, 1.0)["status"], "below_min_n")
    ck.eq("no -0.000", (f3(-0.0001), f6(-0.0000001)), ("0.000", "0.000000"))
    ck.eq("F0 warning: needs 5 prior dates; fires below half the median",
          (f0_warning([100] * 4, 1), f0_warning([100] * 5, 50), f0_warning([100] * 5, 49) is not None), (None, None, True))
    # writers refuse identifiers, min and max
    ck.raises("writer refuses a 19-digit field", AssertionError, lambda: check_fields(("a",), [["1234567890123456789"]]))
    ck.raises("writer refuses an 8-digit field (legacy ids)", AssertionError, lambda: check_fields(("a",), [["12345678"]]))
    ck.raises("writer refuses a header with min", AssertionError, lambda: check_fields(("a_min",), []))
    ck.raises("writer refuses a header with max", AssertionError, lambda: check_fields(("MaxValue",), []))
    ck.ok("writer accepts a kB size with a decimal point", check_fields(("a",), [["15103.3"]]) is None)
    # user agent and hosts
    ck.ok("user agent has no @", "@" not in UA)
    ck.ok("user agent is the CLAUDE.md non-SEC string", UA == "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)")
    ck.eq("request headers are exactly User-Agent and Accept-Encoding: identity", sorted(HEADERS), ["Accept-Encoding", "User-Agent"])
    ck.eq("Accept-Encoding is identity", HEADERS["Accept-Encoding"], "identity")
    ck.raises("www.sec.gov is refused", Refused, lambda: check_url("https://www.sec.gov/cgi-bin/browse-edgar"))
    ck.raises("data.sec.gov is refused", Refused, lambda: check_url("https://data.sec.gov/submissions/x.json"))
    ck.raises("an unlisted host is refused", Refused, lambda: check_url("https://example.com/x"))
    ck.raises("the DTCC S3 host is refused", Refused, lambda: check_url("https://kgc0418-tdw-data-0.s3.amazonaws.com/cftc/eod/x.zip"))
    ck.raises("a DTCC path outside the cumulative CFTC prefix is refused", Refused, lambda: check_url("https://pddata.dtcc.com/ppd/cftcdashboard"))
    ck.raises("plain http is refused", Refused, lambda: check_url("http://pddata.dtcc.com" + DTCC_PREFIX + "x.zip"))
    ck.ok("the cumulative CFTC file URL is allowed", check_url("https://pddata.dtcc.com" + DTCC_PREFIX + dtcc_name(dt.date(2026, 10, 13)))[0] == "pddata.dtcc.com")
    ck.ok("the Treasury CSV URL is allowed", check_url("https://home.treasury.gov" + TSY_TMPL.format(y=2026, t=TSY_KINDS[0]))[0] == "home.treasury.gov")
    ck.raises("a cache inside the repo is refused", Refused, lambda: check_cache(os.path.join(ROOT, "data", "x")))
    ck.raises("the repo root as a cache is refused", Refused, lambda: check_cache(ROOT))
    ck.ok("a cache outside the repo is accepted", check_cache(tempfile.gettempdir()) is not None)
    import inspect
    src = inspect.getsource(real_opener)
    ck.ok("the opener sends GET and never HEAD", '"GET"' in src and "HEAD" not in src)
    ck.ok("tilde() hides the home directory", tilde(os.path.expanduser("~/x")) == "~/x")
    wire_check(ck)
    # Treasury parser: a 2024-style and a 2025-style header (A7), case-insensitive
    t24 = 'Date,"1 Mo","2 Mo","2 Yr","5 Yr","10 Yr","30 Yr"\n12/31/2024,4.40,4.39,4.25,4.38,4.58,4.78\n'
    t25 = 'Date,"1 Mo","1.5 Month","2 Yr","5 Yr","10 YR","30 yr"\n12/31/2025,3.74,3.75,3.47,3.73,4.18,4.84\n'
    r24, r25 = parse_ust_text(t24, "par"), parse_ust_text(t25, "par")
    ck.eq("treasury parser, 2024-style row", r24[dt.date(2024, 12, 31)], {2: 4.25, 5: 4.38, 10: 4.58, 30: 4.78})
    ck.eq("treasury parser, 2025-style row (extra column, mixed case)", r25[dt.date(2025, 12, 31)], {2: 3.47, 5: 3.73, 10: 4.18, 30: 4.84})
    ck.eq("treasury real parser ('5 YR' style)", parse_ust_text('Date,"5 YR","10 YR","30 YR"\n10/13/2026,2.67,2.88,3.28\n', "real")[dt.date(2026, 10, 13)],
          {5: 2.67, 10: 2.88, 30: 3.28})
    ck.raises("treasury parser refuses a missing tenor", AssertionError, lambda: parse_ust_text('Date,"2 Yr"\n01/02/2025,4.0\n', "par"))
    return ck


class FakeClock:
    def __init__(self, t0):
        self.t = t0
        self.slept = []

    def time(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


def fake_zip(d, member=None, junk=False):
    if junk:
        return b"<html>blocked</html>"
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as z:
        z.writestr(member or dtcc_name(d, "csv"), "a,b\n1,2\n")
    return out.getvalue()


def fetch_checks():
    ck = Checks()
    now0 = dt.datetime(2026, 10, 14, 12, 0, 0, tzinfo=dt.timezone.utc)

    def rig(tmp, script, max_requests=60, sleep=5.0, clock=None):
        clock = clock or FakeClock(now0.timestamp())
        calls = []

        def opener(host, target, headers, timeout, cap):
            calls.append((host, target, dict(headers), clock.time()))
            res = script(host, target) if callable(script) else script
            if isinstance(res, Exception):
                raise res
            return res
        f = Fetcher(os.path.join(tmp, "cache"), os.path.join(tmp, "out"), sleep=sleep, max_requests=max_requests, opener=opener,
                    wall=clock.time, mono=clock.time, sleeper=clock.sleep, stop_path=os.path.join(tmp, "STOP"),
                    now_utc=lambda: dt.datetime.fromtimestamp(clock.time(), dt.timezone.utc), pid_alive=lambda p: False)
        return f, calls, clock

    def case(label, script, dates, expect_stop, expect_exc=None, **kw):
        with tempfile.TemporaryDirectory() as tmp:
            f, calls, clock = rig(tmp, script, **kw)
            exc = None
            outcomes = []
            try:
                with f:
                    for d in dates:
                        outcomes.append(f.fetch_date(d))
            except Exception as e:
                exc = e
            stop = os.path.exists(os.path.join(tmp, "STOP"))
            ck.eq("%s: STOP latch %s" % (label, "written" if expect_stop else "not written"), stop, expect_stop)
            if expect_exc is not None:
                ck.ok("%s: raises %s" % (label, expect_exc.__name__), isinstance(exc, expect_exc), "got %r" % (exc,))
            else:
                ck.ok("%s: no exception" % label, exc is None, "got %r" % (exc,))
            ck.ok("%s: lock removed in finally" % label, not os.path.exists(os.path.join(tmp, "cache", ".fetch.lock")))
            return outcomes, calls, tmp

    d1, d2, d3 = dt.date(2026, 9, 29), dt.date(2026, 9, 30), dt.date(2026, 10, 1)
    ok = lambda h, t: (200, fake_zip(dt.date(2026, 9, 29)))   # only used by cases that must send no request
    # saved, with 5 s spacing and the log
    with tempfile.TemporaryDirectory() as tmp:
        script = lambda h, t: (200, fake_zip(dt.date(int(t[-14:-10]), int(t[-9:-7]), int(t[-6:-4]))))
        f, calls, clock = rig(tmp, script)
        with f:
            outs = [f.fetch_date(d) for d in (d1, d2, d3)]
        ck.eq("three weekday files are saved", outs, ["saved", "saved", "saved"])
        starts = [c[3] for c in calls]
        ck.ok("consecutive request starts are >= 5 s apart", all(b - a >= 5.0 for a, b in zip(starts, starts[1:])), str(starts))
        ck.ok("request headers are exactly the two allowed", all(sorted(c[2]) == ["Accept-Encoding", "User-Agent"] for c in calls))
        ck.eq("every request went to pddata.dtcc.com", {c[0] for c in calls}, {"pddata.dtcc.com"})
        log = read_table(os.path.join(tmp, "out", "fetch_log.csv"), FETCH_LOG_COLS)
        ck.eq("fetch_log has one row per request", [r[5] for r in log], ["saved", "saved", "saved"])
        # spacing persists across invocations: a second Fetcher on the same cache must wait
        f2, calls2, clock2 = rig(tmp, script, clock=clock)
        t_before = clock.time()
        with f2:
            ck.eq("a cached file is not requested again", f2.fetch_date(d1), "cached")
            f2.fetch_date(dt.date(2026, 10, 2))
        ck.ok("the 5 s spacing persists across invocations", calls2[0][3] - starts[-1] >= 5.0, "%s %s" % (calls2[0][3], starts[-1]))
    outs, calls, _ = case("weekend / not_yet", ok, [dt.date(2026, 10, 10), dt.date(2026, 10, 13)], False)
    ck.eq("weekend and not_yet send no request", (outs, len(calls)), (["weekend", "not_yet"], 0))
    # 404 zones
    outs, calls, tmp = case("recent 404", lambda h, t: (404, b""), [dt.date(2026, 10, 8)], True, Latched)
    outs, calls, tmp = case("old 404 (> 366 days) is a hole", lambda h, t: (404, b""), [dt.date(2024, 10, 11), dt.date(2024, 10, 14)], False)
    ck.eq("old 404 returns hole and the run goes on (2 requests)", (outs, len(calls)), (["hole", "hole"], 2))
    with tempfile.TemporaryDirectory() as tmp:
        f, calls, clock = rig(tmp, lambda h, t: (404, b""))
        with f:
            f.fetch_date(dt.date(2024, 10, 11))
        holes = read_table(os.path.join(tmp, "out", "holes.csv"), HOLES_COLS)
        ck.eq("holes.csv records the date and status", [(r[0], r[1]) for r in holes], [("2024-10-11", "404")])
        f, calls, clock = rig(tmp, lambda h, t: (404, b""))
        with f:
            ck.eq("a recorded hole is not requested again", (f.fetch_date(dt.date(2024, 10, 11)), len(calls)), ("hole_known", 0))
    for status in (401, 403, 407, 429, 451, 301, 302, 500, 503):
        case("HTTP %d" % status, (lambda s: lambda h, t: (s, b""))(status), [d1], True, Latched)
    case("200 with an HTML body", lambda h, t: (200, fake_zip(d1, junk=True)), [d1], True, Latched)
    case("200 with the wrong member name", lambda h, t: (200, fake_zip(d1, member="CFTC_CUMULATIVE_RATES_2026_09_30.csv")), [d1], True, Latched)
    case("200 with a body over the cap", lambda h, t: (200, None), [d1], True, Latched)
    case("socket fault ends the invocation without latching", lambda h, t: SocketFault("timeout"), [d1, d2], False, SocketFault)
    with tempfile.TemporaryDirectory() as tmp:
        f, calls, clock = rig(tmp, lambda h, t: (200, fake_zip(dt.date(int(t[-14:-10]), int(t[-9:-7]), int(t[-6:-4])))), max_requests=1)
        raised = None
        with f:
            f.fetch_date(d1)
            try:
                f.fetch_date(d2)
            except Refused as e:
                raised = e
        ck.ok("the second request beyond --max-requests 1 is refused", raised is not None and len(calls) == 1)
    # STOP latch refuses later runs; the lock stops a second fetcher
    with tempfile.TemporaryDirectory() as tmp:
        f, calls, clock = rig(tmp, lambda h, t: (403, b""))
        try:
            with f:
                f.fetch_date(d1)
        except Latched:
            pass
        f2, calls2, _ = rig(tmp, lambda h, t: (200, b""))
        ck.raises("a later fetch refuses to run while STOP exists", Latched, lambda: f2.__enter__())
        ck.eq("...and sends no request", len(calls2), 0)
    with tempfile.TemporaryDirectory() as tmp:
        f, calls, clock = rig(tmp, lambda h, t: (200, b""))
        f.pid_alive = lambda p: True
        with f:
            f2, _, _ = rig(tmp, lambda h, t: (200, b""))
            f2.pid_alive = lambda p: True
            ck.raises("a live lock stops a second fetcher", Refused, lambda: f2.__enter__())
        f3, _, _ = rig(tmp, lambda h, t: (200, b""))
        with f3:
            ck.ok("the lock is free again after the first fetcher leaves", True)
        os.makedirs(os.path.join(tmp, "cache"), exist_ok=True)
        with open(os.path.join(tmp, "cache", ".fetch.lock"), "w") as fh:
            fh.write("999999 %.0f\n" % now0.timestamp())
        f4, _, _ = rig(tmp, lambda h, t: (200, b""))
        with f4:
            ck.ok("a lock held by a dead pid is replaced", True)
    ck.raises("--sleep below 5 is refused", Refused, lambda: Fetcher("/tmp/x_never_used", "/tmp/y", sleep=4.9))
    ck.raises("--max-requests above 100 is refused", Refused, lambda: Fetcher("/tmp/x_never_used", "/tmp/y", max_requests=101))
    with tempfile.TemporaryDirectory() as tmp:
        f, calls, clock = rig(tmp, lambda h, t: (200, b""))
        with f:
            ck.eq("a date before the first probed date (2024-10-11) is never requested", (f.fetch_date(dt.date(2024, 10, 10)), len(calls)),
                  ("before_archive", 0))
    ck.eq("the STOP latch is at the fixed path under ~/dtcc_ppd", tilde(STOP_PATH), "~/dtcc_ppd/STOP")
    # Treasury
    with tempfile.TemporaryDirectory() as tmp:
        body = FX_PAR_CSV.encode()
        f, calls, clock = rig(tmp, lambda h, t: (200, body))
        with f:
            r1 = f.fetch_ust(2030, TSY_KINDS[0], os.path.join(tmp, "ust"))
        ck.eq("treasury file saved, host home.treasury.gov", (r1, calls[0][0]), ("saved", "home.treasury.gov"))
        ck.ok("treasury file name carries the fetch date", any(n.startswith("daily_treasury_yield_curve_2030_fetched-") for n in os.listdir(os.path.join(tmp, "ust"))))
    with tempfile.TemporaryDirectory() as tmp:
        f, calls, clock = rig(tmp, lambda h, t: (200, b"<html>login</html>"))
        try:
            with f:
                f.fetch_ust(2030, TSY_KINDS[0], os.path.join(tmp, "ust"))
        except Latched:
            pass
        ck.ok("a Treasury body that is not a CSV latches STOP", os.path.exists(os.path.join(tmp, "STOP")))
    # verifier S1: a past year is final only once a copy was fetched on or after 3 Jan of the next year
    body = FX_PAR_CSV.encode()
    for fetched, want in (("20301226", "saved"), ("20310105", "cached_final_year")):
        with tempfile.TemporaryDirectory() as tmp:
            ud = os.path.join(tmp, "ust")
            os.makedirs(ud)
            with open(os.path.join(ud, "%s_2030_fetched-%s.csv" % (TSY_KINDS[0], fetched)), "wb") as fh:
                fh.write(body)
            f, calls, clock = rig(tmp, lambda h, t: (200, body), clock=FakeClock(dt.datetime(2031, 1, 6, 12, tzinfo=dt.timezone.utc).timestamp()))
            with f:
                got = f.fetch_ust(2030, TSY_KINDS[0], ud)
            ck.eq("past year with a copy fetched %s -> %s" % (fetched, want), got, want)
    return ck


def selftest():
    import shutil
    allck = []
    t0 = time.time()
    pure = pure_checks()
    allck.append(("pure checks", pure))
    allck.append(("stop logic (fake opener, fake clock, no network)", fetch_checks()))
    root = tempfile.mkdtemp(prefix="swaptape_selftest_")
    try:
        cache, ust = make_fixture_dirs(root)
        tape_rows = build_fixture_tape().rows
        outs = []
        errs = 0
        for k in (1, 2):
            out = os.path.join(root, "out%d" % k)
            for ds in (FX_WIN, FX_DAY):   # two builds into one directory: the second is an upsert beside the first
                errs += build(dt.date.fromisoformat(ds), dt.date.fromisoformat(ds), cache, out, ust, Cfg(), say=lambda *a: None)
            outs.append(out)
        base = fixture_checks(outs[0], tape_rows)
        base.eq("fixture build raised no error", errs, 0)
        allck.append(("fixture: exact funnel, cells, ledger, diagnostics", base))
        det = Checks()
        names = sorted(os.listdir(outs[0]))
        det.eq("two builds list the same files", names, sorted(os.listdir(outs[1])))
        same = all(open(os.path.join(outs[0], n), "rb").read() == open(os.path.join(outs[1], n), "rb").read() for n in names)
        det.ok("two builds of the fixture are byte-identical", same)
        # upsert: rebuilding one date into an existing directory leaves the other date's rows alone
        before = open(os.path.join(outs[0], "ledger_2030.csv"), "rb").read()
        build(dt.date.fromisoformat(FX_DAY), dt.date.fromisoformat(FX_DAY), cache, outs[0], ust, Cfg(), say=lambda *a: None)
        det.ok("upsert: rebuilding one date reproduces the ledger byte for byte", open(os.path.join(outs[0], "ledger_2030.csv"), "rb").read() == before)
        leak = []
        for n in names:
            if n.endswith(".csv"):
                with open(os.path.join(outs[0], n), encoding="utf-8") as fh:
                    first = fh.readline()
                    det.ok("%s starts with a '# source:' line naming DTCC" % n, first.startswith("# source: DTCC Public Price Dissemination") and
                           "pddata.dtcc.com" in first)
                    for ln in fh:
                        if re.search(r"(^|,)[0-9]{8,19}(,|$)", ln):
                            leak.append(n)
        det.eq("no output field is a whole string of 8-19 digits", leak, [])
        det.ok("no absolute home path in any output", not any(os.path.expanduser("~") in open(os.path.join(outs[0], n), encoding="utf-8").read() for n in names))
        det.ok("SOURCES.md carries the R3 citation", "Derived from DTCC Public Price Dissemination, CFTC cumulative interest-rate reports (pddata.dtcc.com). "
               "Statistics only; no DTCC record is reproduced." in " ".join(open(os.path.join(outs[0], "SOURCES.md"), encoding="utf-8").read().split()))
        allck.append(("determinism and leak guards", det))
        mutant_results = []
        for m in ("noconv", "noeror", "nowindow"):
            out = os.path.join(root, "mut_" + m)
            why = None
            try:
                for ds in (FX_WIN, FX_DAY):
                    build(dt.date.fromisoformat(ds), dt.date.fromisoformat(ds), cache, out, ust, Cfg(m), say=lambda *a: None)
                ck = fixture_checks(out, tape_rows)
                bad = ck.failed()
                if bad:
                    why = "%d check(s) failed, first: %s" % (len(bad), bad[0][0])
            except Exception as e:
                why = "raised %s" % type(e).__name__
            mutant_results.append((m, why))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    bad_total = 0
    for title, ck in allck:
        print("== %s: %d checks" % (title, len(ck.items)))
        for name, cond, detail in ck.items:
            print("  %s  %s%s" % ("PASS" if cond else "FAIL", name, "" if cond else "   <- " + detail))
            bad_total += 0 if cond else 1
    print("== mutants (each must make at least one fixture check fail)")
    for m, why in mutant_results:
        print("  %s  %s%s" % ("DETECTED" if why else "NOT DETECTED", m, "  (" + why + ")" if why else ""))
        bad_total += 0 if why else 1
    n_checks = sum(len(ck.items) for _, ck in allck)
    print("selftest: %d checks, %d mutants, %d failure(s), %.1f s" % (n_checks, len(mutant_results), bad_total, time.time() - t0))
    return 0 if bad_total == 0 else 1


# ----------------------------------------------------------------------------------------------------------------------
# command line
# ----------------------------------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch", help="download DTCC cumulative CFTC rates zips into the cache (the only DTCC network command)")
    pf.add_argument("--dates", help="comma-separated YYYY-MM-DD")
    pf.add_argument("--start")
    pf.add_argument("--end")
    pf.add_argument("--cache", default=os.environ.get("DTCC_PPD_CACHE") or CACHE_DEFAULT)
    pf.add_argument("--out", default=OUT_DEFAULT, help="where fetch_log.csv and holes.csv are kept")
    pf.add_argument("--sleep", type=float, default=MIN_SLEEP)
    pf.add_argument("--max-requests", type=int, default=60)
    pu = sub.add_parser("fetch-ust", help="download the Treasury par and real yield CSVs")
    pu.add_argument("--years", required=True)
    pu.add_argument("--ust-dir", default=UST_DEFAULT)
    pu.add_argument("--cache", default=os.environ.get("DTCC_PPD_CACHE") or CACHE_DEFAULT, help="holds the lock and the spacing file")
    pu.add_argument("--out", default=OUT_DEFAULT)
    pu.add_argument("--sleep", type=float, default=MIN_SLEEP)
    pb = sub.add_parser("build", help="offline: upsert the ledger rows of the weekdays in [start, end]")
    pb.add_argument("--start", required=True)
    pb.add_argument("--end", required=True)
    pb.add_argument("--cache", default=os.environ.get("DTCC_PPD_CACHE") or CACHE_DEFAULT)
    pb.add_argument("--out", default=OUT_DEFAULT)
    pb.add_argument("--ust-dir", default=UST_DEFAULT)
    pb.add_argument("--mutant", choices=("noconv", "noeror", "nowindow"),
                    help="diagnostic: build with a deliberately broken rule; refused for the repository's data/swap_tape")
    sub.add_parser("selftest", help="synthetic fixture, mutants and stop logic; no network")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    try:
        if a.cmd == "build":
            if a.mutant and os.path.realpath(a.out) == os.path.realpath(OUT_DEFAULT):
                raise Refused("--mutant may not write into the repository's data/swap_tape")
            errs = build(pd_arg(a.start), pd_arg(a.end), a.cache, a.out, a.ust_dir, Cfg(a.mutant))
            return 2 if errs else 0
        with Fetcher(a.cache, a.out, sleep=a.sleep, max_requests=getattr(a, "max_requests", 60)) as f:
            if a.cmd == "fetch-ust":
                for y in [int(x) for x in a.years.split(",")]:
                    for kind in TSY_KINDS:
                        print("treasury %s %d: %s" % (kind, y, f.fetch_ust(y, kind, a.ust_dir)))
                return 0
            if a.dates:
                dates = sorted({pd_arg(x) for x in a.dates.split(",")})
            elif a.start and a.end:
                dates = list(weekdays(pd_arg(a.start), pd_arg(a.end)))
            else:
                raise Refused("fetch needs --dates or --start and --end")
            for d in dates:
                print("%s: %s" % (d.isoformat(), f.fetch_date(d)))
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


if __name__ == "__main__":
    sys.exit(main())
