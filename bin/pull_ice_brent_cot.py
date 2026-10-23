#!/usr/bin/env python3
"""Weekly ICE Brent Commitments-of-Traders ledger, beside the CFTC's NYMEX WTI one (bin/pull_cftc_cot.py). Python 3 standard library
plus xlrd (the EIA .xls, as requirements.txt says).

  python3 bin/pull_ice_brent_cot.py fetch [--years 2012-2017,2019-2025 | --refresh-year YYYY] [--cache DIR] [--out DIR] [--sleep 5.05] [--max-requests 20]
  python3 bin/pull_ice_brent_cot.py build [--cache DIR] [--out DIR]          # offline; byte-identical on re-run
  python3 bin/pull_ice_brent_cot.py selftest [--no-mutants]                  # synthetic rows only; no network

Specification: _research/2026-10-15-ICE-Brent-COT-Spec.md (section 10, the supervisor's amendments, overrides sections 0-9).
Terms: THE_ASK.md E-025, which extends E-024. ICE Futures Europe's site terms forbid robots and automated retrieval. The principal
ruled that the Brent COT files may be scripted on E-024's conditions: non-commercial use; no raw ICE file or row is committed or
redistributed; only derived statistics are published, and they cite ICE; requests are sequential and paced; any technical refusal ends the
run instead of being routed around. The ruling covers the Brent COT files only, not other ICE data (prices, settlements).

WHAT TOUCHES THE NETWORK. Only `fetch`. Hosts: www.ice.com (https://www.ice.com/publicdocs/futures/COTHist<YYYY>.csv) and www.eia.gov
(https://www.eia.gov/dnav/pet/hist_xls/RBRTEd.xls, US government, public domain). GET only; one request at a time; at least 5.05 s between
request starts, persisted across invocations in ~/ice_cot/.last_request (written at full precision, beside the fixed STOP path, so two runs with
different --cache values are paced against each other; the fetch lock ~/ice_cot/.fetch.lock sits there too); at most 20 requests per run; the
CLAUDE.md non-SEC User-Agent (no address, no name); redirects are NOT followed. Any HTTP status other than 200, or a body that is not the
expected file (for ICE a CSV that passes the header test; for EIA an XLS that opens and has the expected layout, tested on the .part file before
it replaces anything), writes ~/ice_cot/STOP and ends the run. While STOP exists every fetch refuses; only a person deletes it. A socket fault
ends the invocation without latching. No retry, ever. Every request is one row of data/ice_brent/fetch_log.csv. `fetch --refresh-year YYYY`
requests that one year's ICE file again although it is cached (the New-Year seam: a past-year file fetched before its last reports were
published) and nothing else; it is paced, capped and latched like any other request.

WHERE THE ICE FILES LIVE. ~/ice_cot/ (override --cache; a path inside this repository is refused). They are read in memory and are
never copied into the repository: .gitignore has COTHist*.csv, bin/check.sh M11 looks for one anywhere in the repository (any letter case) and
for ICE's header line in any file outside bin/ and _research/, and no output carries ICE's gross long, short, spreading or open-interest
columns or any per-class gross figure.

WHAT IS PUBLISHED (all under data/ice_brent/, each file with an exact column allowlist and a `# source:` first line): brent_ledger.csv
(weekly NET position per trader class, in contracts and barrels, their changes, managed-money net as a share of open interest to 0.1pp,
dollars at the EIA Brent spot, and a price_flag for known-bad EIA prints), brent_windows.csv, brent_leadlag.csv (the WTI test, same columns),
brent_file_stats.csv (provenance and identity maxima), checks.csv, fetch_log.csv. Positions are as of Tuesday's close and published by ICE
the following Friday.

THE TWO REPORT TYPES. `fo` is futures only; `combined` is futures and options combined. ICE's file says which in FutOnly_or_Combined.
That column decides the type, never the market name: in 2011 both types carry the identical name `ICE Brent Crude Futures - ICE Futures
Europe`. In later years the combined rows are named `... Futures and Options ...`. The combined figures are whole contracts and the
identities below hold for them only to rounding; the cause (rounding of option-delta conversions) is inferred from the size of the
residuals, not stated by ICE.

THE IDENTITIES (A1) AND THE PERCENTAGE CHECK, asserted on the raw rows in memory before anything is written. ICE leaves Tot_Rept_Positions_*
and the Change_in_* columns blank on every Brent row, so the identities are stated without the reported totals:
    (1) per side: pm + sw + sw_spread + mm + mm_spread + ot + ot_spread + non-reportable  ==  open interest   (spreading on BOTH sides)
        futures only: exact. combined: within 4 contracts per side.
    (2) the five class nets (long - short; spreading drops out) sum to zero: exact for fo, within 8 for combined. Published as resid_net.
    (3) for ALL TEN class/side pairs (pm, sw, mm, ot, nr x long, short), ICE's own Pct_of_OI_<class>_<side>_All column agrees with that
        level / open interest within 0.05pp (ICE's rounding) on every populated value. A hard check. checks.csv K03 reports, per pair, how many
        values were checked and the largest gap, and warns if a pair was populated on fewer rows than there are rows (or on none).
WHAT THEY PROVE. (1) and (2) prove that the cells, as read, add up as one set on each side, so a figure taken from the wrong SIDE, or a class
dropped or counted twice, would stop the build. They cannot see two classes exchanged on the SAME side (pm_long with sw_long, say): the side
sums and the net sum do not change, and each class would simply carry the other's net. (3) can: each level is compared with ICE's own percentage
column of the same name, so a same-side exchange shows as a gap of about the difference between the two classes' shares of open interest. (3)
is certain to see an exchange only if the two shares differ by more than 0.10pp (twice ICE's rounding bound); it does not cover the spreading
columns (an exchange between two of them moves no net and no published figure); and it compares two columns of one ICE file by name, so it
cannot see a column that ICE itself mislabelled in both. The selftest swaps pairs of columns inside the parser and requires the build to stop.
The independent evidence for managed money's level is (3) and the pinned 31 March 2026 nets in checks.csv.
WHAT THEY DO NOT PROVE: that non-reportable is a residual. ICE publishes no total-reportable column, so this build cannot tell whether
non-reportable is measured or is defined as open interest minus the classes. If it is defined that way, (1) holds by construction and cannot
fail, and the nr net is then the least secure number in the table. A blank total is not an error (a total, if ICE fills one in, is checked); a
blank class figure is.

GUARDS AND THE SELFTEST. Every guard is behind on("<name>"). `selftest` runs the whole synthetic suite, then re-runs the relevant part
of it once per guard with that guard switched off (in this process only; there is no command-line or environment switch) and FAILS if
a guard's removal goes unnoticed. The cases the spec requires (A11) are: blank_totals, bom, swap_spelling, monday_dates,
type_by_column, latch_non200, latch_bad_body, socket_no_latch, pacing, host_allowlist, cache_outside_repo, pct_precision,
column_allowlist, fo_identity_exact, duplicate_week. The build adds units, blank_class, pct_agree, seam_gap, price_lag, min_sleep,
max_requests, stop_blocks_fetch, xls_magic, report_year, ua_no_address, source_line, shared_pacing, eia_validate, price_flag. It also swaps
pairs of columns inside the parser (pm_long with sw_long, ot_short with nr_short, ...) and requires each swap to be noticed, and it pins the
window dates, the lead-lag shifts, band and start, and the price precision against independent recomputations.
"""
import argparse
import bisect
import collections
import contextlib
import csv
import datetime as dt
import hashlib
import http.client
import io
import math
import os
import re
import statistics
import sys
import tempfile
import time
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(ROOT, "data", "ice_brent")
WTI_DIR = os.path.join(ROOT, "data", "cftc_cot")
CACHE_DEFAULT = "~/ice_cot"
STOP_PATH = os.path.expanduser("~/ice_cot/STOP")    # fixed, whatever --cache says (A9)

# A16: the CLAUDE.md canonical string for every non-SEC host. No address, no name.
UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
HEADERS = {"User-Agent": UA, "Accept-Encoding": "identity"}
ICE_HOST, EIA_HOST = "www.ice.com", "www.eia.gov"
ICE_PREFIX = "/publicdocs/futures/"
ICE_RX = re.compile(r"/publicdocs/futures/COTHist(20[0-9]{2})\.csv")
EIA_PATH = "/dnav/pet/hist_xls/RBRTEd.xls"
EIA_RAW_NAME = "eia_RBRTEd.xls"
XLS_MAGIC = b"\xd0\xcf\x11\xe0"
FIRST_YEAR = 2011
MIN_SLEEP = 5.05                       # seconds between request starts: the 5 s of E-024 plus a margin for clock granularity (A9)
MAX_REQUESTS = 20
TIMEOUT = 120
BODY_CAP = 20 * 1024 * 1024

BBL_PER_CONTRACT = 1000
UNITS_RX = re.compile(r"\(CONTRACTS OF 1,000 BARRELS\)")
NAME_PREFIX = "ICE Brent Crude Futures"
KNOWN_MONDAYS = frozenset({dt.date(2018, 12, 24), dt.date(2018, 12, 31)})     # A12
KNOWN_HOLIDAY_GAPS = frozenset()       # (last date of one file, first date of the next) pairs 13-15 days apart that were observed and accepted (A12)
TOL_SIDE, TOL_NET = 4, 8               # combined-report rounding bounds (contracts), as pull_cftc_cot.py
PCT_TOL = 0.05                         # pp: ICE's own percentage vs level / open interest (A1)
MAX_PRICE_LAG_DAYS = 5
LATE_SPLIT = dt.date(2024, 1, 1)       # lead-lag sample: report dates from here (A7)
PRICE_RANGE = (1.0, 250.0)             # plausible $/bbl for Brent spot, a unit guard
USD_BASIS = "EIA_Europe_Brent_spot_FOB_not_ICE_settlement"
PRICE_FLAG = "eia_spot_gap_unverified"
# EIA Brent spot prints not reconciled with the futures market (inclusive ranges of the PRINT date). From 2 Oct 2026 EIA's Europe Brent spot has
# printed $125-136, about $20-30 above a Brent futures quote of about $102 on 5 Oct (relayed; Grok checks 13 and 17 Oct). EIA has not retracted the
# prints and they persisted through 14 Oct, so this is an unexplained spot-futures gap, not a confirmed data error. Extend the range weekly while it
# lasts (CALENDAR.tsv, the crude row). A report date whose price_date falls in a range gets price_flag; its USD figures stay as computed.
KNOWN_SUSPECT_PRINTS = ((dt.date(2026, 10, 2), dt.date(2026, 10, 21)),)   # 23 Oct: press-reported Dated Brent premium (Grok g10); EIA issued no notice
KEMP_BBL, KEMP_DATE, KEMP_TOL = 253_000_000, dt.date(2026, 6, 2), 0.01       # relayed, warn only (A14)
PINS = ((dt.date(2026, 3, 31), "fo", 382072), (dt.date(2026, 3, 31), "combined", 429853))     # nets only (A4)
ANCHORS = (("since end-2023", dt.date(2023, 12, 31), dt.date(2023, 12, 26)),
           ("since end-2025 (new)", dt.date(2025, 12, 31), dt.date(2025, 12, 30)))   # label, quarter end, expected report date (A6)

KINDS = ("fo", "combined")
KP = {"fo": "fo_", "combined": "co_"}            # ledger column prefixes, as the WTI ledger
CLASSES = (("pm", "Producer/Merchant/Processor/User"), ("sw", "Swap Dealers"), ("mm", "Managed Money"), ("ot", "Other Reportables"),
           ("nr", "Non-Reportables"))
CK = tuple(k for k, _ in CLASSES)
SPREAD_CLASSES = ("sw", "mm", "ot")
PCT_NAMES = {"pm": "Prod_Merc", "sw": "Swap", "mm": "M_Money", "ot": "Other_Rept", "nr": "NonRept"}     # the class word in ICE's Pct_of_OI_* names
PCT_PAIRS = tuple("%s_%s" % (k, s) for k in CK for s in ("long", "short"))                               # the ten class/side pairs checked against ICE's percentages

# ------------------------------------------------------------------------------------------------------------------------
# guards: every guard is behind on("<name>"); only the selftest ever switches one off, in this process
# ------------------------------------------------------------------------------------------------------------------------
_OFF = set()
_SWAPS = []                    # selftest only: pairs of logical columns whose header positions the parser exchanges (a mapping mutant)


def on(name):
    return name not in _OFF


@contextlib.contextmanager
def mutant(name):
    """Switch guard `name` off for the block. Re-entrant: a test that switches a guard off inside a run that already has it off leaves it off."""
    added = name not in _OFF
    _OFF.add(name)
    try:
        yield
    finally:
        if added:
            _OFF.discard(name)


@contextlib.contextmanager
def swapped(a, b):
    """Selftest only: the parser reads column a where it should read b and b where it should read a (e.g. pm_long and sw_long)."""
    _SWAPS.append((a, b))
    try:
        yield
    finally:
        _SWAPS.pop()


class Refused(Exception):
    """A request, path or setting this script will not honour (host list, cache inside the repo, spacing, cap)."""


class MaxRequests(Refused):
    """--max-requests reached: an orderly end of the invocation, not a refusal by a server."""


class Latched(Exception):
    """A technical refusal: ~/ice_cot/STOP was written (or already existed); the run ends."""


class SocketFault(Exception):
    """Timeout, reset or TLS error: the invocation ends without latching."""


class HeaderError(Exception):
    """The file is not an ICE COT history CSV (A3)."""


class DataError(Exception):
    """A hard check on the data failed. The build stops, names the week and repairs nothing."""


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


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_ua(ua=UA):
    if on("ua_no_address"):
        if "@" in ua:
            raise Refused("User-Agent contains an address")
        for var in ("SEC_UA", "CLAUDE_CODE_USER_EMAIL"):
            v = os.environ.get(var, "").strip()
            if v and (v in ua or ua in v):
                raise Refused("User-Agent contains a configured contact value (not printed)")


assert_ua()


def check_url(url):
    """Only the ICE COTHist files and the EIA Brent file (A9). Returns (host, path)."""
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    if on("host_allowlist"):
        if p.scheme != "https":
            raise Refused("only https is allowed")
        if p.query or p.fragment or p.username or p.password or p.port not in (None, 443):
            raise Refused("no query, fragment, credentials or port are allowed")
        ok = (host == ICE_HOST and ICE_RX.fullmatch(p.path)) or (host == EIA_HOST and p.path == EIA_PATH)
        if not ok:
            raise Refused("host or path outside the E-025 ruling (www.ice.com COTHist files and www.eia.gov RBRTEd.xls only)")
    return host, p.path


def check_cache(cache):
    real = os.path.realpath(os.path.expanduser(cache))
    root = os.path.realpath(ROOT)
    if on("cache_outside_repo") and (real == root or real.startswith(root + os.sep)):
        raise Refused("the cache must be outside the repository (ICE files are never committed)")
    return real


def latest_expected_tuesday(today):
    """The most recent Tuesday at least 3 days before `today` (A9): ICE publishes Tuesday's positions on the Friday."""
    d = today - dt.timedelta(days=3)
    return d - dt.timedelta(days=(d.weekday() - 1) % 7)


def report_year(today):
    """The year of the latest expected report Tuesday: on Fri 1 Jan 2027 this is 2026, not 2027 (A9)."""
    return latest_expected_tuesday(today).year if on("report_year") else today.year


def week_index(d):
    """A consecutive integer per ISO week (Monday-based)."""
    return (d - dt.timedelta(days=d.weekday())).toordinal() // 7


def iso_key(d):
    c = d.isocalendar()
    return (c[0], c[1])


def iso_label(k):
    return "%d-W%02d" % k


# ------------------------------------------------------------------------------------------------------------------------
# CSV tables: allowlists, source lines, verification of the written text
# ------------------------------------------------------------------------------------------------------------------------
LEDGER_COLS = ["report_date", "price_date", "price_lag_days", "price_usd_per_bbl", "usd_basis", "price_flag"]
for _kind in KINDS:
    _p = KP[_kind]
    LEDGER_COLS += [_p + k + "_net" for k in CK] + [_p + k + "_net_bbl" for k in CK] + [_p + "resid_net"] + [_p + k + "_net_chg" for k in CK]
    LEDGER_COLS += [_p + "mm_net_pct_oi", _p + "mm_net_usd_bn"]
WINDOWS_COLS = ["contract", "report_type", "window", "weeks", "from_date", "to_date", "mm_net_from", "mm_net_to", "mm_net_chg", "mm_net_chg_bbl",
                "mm_net_pct_oi_from", "mm_net_pct_oi_to"]
LEADLAG_COLS = ["contract", "report_type", "first_week", "last_week",
                "n_same", "pearson_same_pct", "spearman_same_pct", "pearson_same_abs", "band95_same",
                "n_next", "pearson_next_pct", "spearman_next_pct", "pearson_next_abs", "band95_next",
                "n_prev", "pearson_prev_pct", "spearman_prev_pct", "pearson_prev_abs", "band95_prev"]
FILE_STATS_COLS = ["file_year", "file_name", "sha256", "bytes", "retrieved_utc", "retrieved_src", "header_cols", "swap_spelling", "unnamed_cols",
                   "cols_added_vs_prev", "cols_removed_vs_prev", "market_names", "cftc_contract_market_code", "cftc_commodity_code",
                   "rows_fo", "rows_combined", "first_report_date", "last_report_date", "non_tuesday_dates", "units_rows_checked",
                   "side_resid_max_fo", "net_resid_max_fo", "side_resid_max_co", "net_resid_max_co", "agree_checked_n"]
CHECKS_COLS = ["check_id", "check", "expected", "observed", "status", "note"]
FETCH_LOG_COLS = ["requested_at_utc", "host", "path", "http_status", "outcome", "bytes", "sha256"]
ALLOW = {"brent_ledger.csv": LEDGER_COLS, "brent_windows.csv": WINDOWS_COLS, "brent_leadlag.csv": LEADLAG_COLS,
         "brent_file_stats.csv": FILE_STATS_COLS, "checks.csv": CHECKS_COLS, "fetch_log.csv": FETCH_LOG_COLS}
# share-of-open-interest columns: at most one decimal in the written text (A5). verify_text treats EVERY column whose name contains 'pct' or ends
# '_pp' as a percent column: it must be on this list, or be one of the correlation coefficients below. A gap in percentage points (ICE's percentage
# against the level / open interest) is not a column at all: it is text in checks.csv (K03).
PERCENT_COLS = {"brent_ledger.csv": [KP[k] + "mm_net_pct_oi" for k in KINDS], "brent_windows.csv": ["mm_net_pct_oi_from", "mm_net_pct_oi_to"]}
# lead-lag columns that carry 'pct' because the PRICE CHANGE is in percent; their values are correlation coefficients at 3 decimals, as WTI's leadlag.csv
PCT_EXEMPT = {"brent_leadlag.csv": [c for c in LEADLAG_COLS if re.fullmatch(r"(pearson|spearman)_(same|next|prev)_pct", c)]}
# A header cell is a banned gross name if its '_'-separated words include one of these, or it has open_interest, or `oi` outside pct_oi.
BANNED_HDR = re.compile(r"(^|_)(long|short|spread|spreading|gross)(_|$)|open_interest|(?<!pct)(^|_)oi(_|$)")
SOURCE_ICE = ("# source: ICE Futures Europe, Commitments of Traders historical files (ice.com/publicdocs/futures), derived statistics only; "
              "non-commercial research (THE_ASK.md E-025)")
SOURCE_LOG = ("# source: request log for ICE Futures Europe Commitments of Traders historical files (www.ice.com) and the EIA Europe Brent spot "
              "price file (www.eia.gov); each row carries its own UTC time; non-commercial research (THE_ASK.md E-025)")
ONE_DEC = re.compile(r"-?[0-9]+\.[0-9]")


def looks_percent(h):
    return "pct" in h or h.endswith("_pp")


def check_header_allowed(name, header):
    """A10: the header must equal the file's allowlist exactly, and carry no banned gross name (R2)."""
    if not on("column_allowlist"):
        return
    if name not in ALLOW:
        raise DataError("no column allowlist for output file %s" % name)
    if list(header) != ALLOW[name]:
        extra = [h for h in header if h not in ALLOW[name]]
        raise DataError("%s: header differs from its allowlist (not allowed: %s; missing: %s)"
                        % (name, ", ".join(extra) or "-", ", ".join(h for h in ALLOW[name] if h not in header) or "-"))
    bad = [h for h in header if BANNED_HDR.search(h)]
    if bad:
        raise DataError("%s: header carries a banned gross column name: %s" % (name, ", ".join(bad)))


def render_table(header, rows, source):
    out = io.StringIO()
    out.write(source + "\n")
    w = csv.writer(out, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return out.getvalue()


def verify_text(name, text):
    """The written text itself is checked, not the rows it came from: source line, allowlist, one decimal on every percent column (A5).
    Returns (header, body rows)."""
    lines = text.split("\n")
    if on("source_line"):
        want = SOURCE_LOG if name == "fetch_log.csv" else SOURCE_ICE
        if not lines[0].startswith(want):
            raise DataError("%s: the first line is not the required `# source:` line" % name)
    rd = list(csv.reader(io.StringIO("\n".join(l for l in lines if not l.startswith("#")), newline="")))
    header, body = rd[0], rd[1:]
    check_header_allowed(name, header)
    if on("pct_precision"):
        for h in header:
            if looks_percent(h) and h not in PERCENT_COLS.get(name, []) and h not in PCT_EXEMPT.get(name, []):
                raise DataError("%s: column %s looks like a percent column (its name contains 'pct' or ends '_pp') but is not on the percent-precision list"
                                % (name, h))
        for h in PERCENT_COLS.get(name, []):
            j = header.index(h)
            for n, r in enumerate(body, start=1):
                if r[j] != "" and not ONE_DEC.fullmatch(r[j]):
                    raise DataError("%s row %d: percent column %s has %r, not at most one decimal" % (name, n, h, r[j]))
    if name == "brent_ledger.csv":
        j = header.index("price_flag")
        bad = sorted({r[j] for r in body} - {"", PRICE_FLAG})
        if bad:
            raise DataError("%s: price_flag holds %r; only '' and %r are allowed" % (name, bad[0], PRICE_FLAG))
    if os.path.expanduser("~") in text and os.path.expanduser("~") != "~":
        raise DataError("%s: an absolute home path would be published" % name)
    return header, body


def read_table(path, header=None):
    """Data rows of a table written by render_table (comment lines skipped); [] if the file is absent."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh.read().splitlines(True) if not ln.startswith("#")]
    rd = list(csv.reader(io.StringIO("".join(lines))))
    if not rd:
        return []
    if header is not None and list(rd[0]) != list(header):
        raise DataError("unexpected header in " + tilde(path))
    return rd[1:]


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


# ------------------------------------------------------------------------------------------------------------------------
# reading an ICE file: header test, rows, identities. Gross figures live only inside parse_row; what leaves it is nets.
# ------------------------------------------------------------------------------------------------------------------------
# logical field -> acceptable header spellings. REQUIRED must be present in every file (A3); OPTIONAL are used where present.
REQUIRED = {
    "name": ("Market_and_Exchange_Names",), "d6": ("As_of_Date_In_Form_YYMMDD",), "units": ("Contract_Units",),
    "kind": ("FutOnly_or_Combined",), "oi": ("Open_Interest_All",),
    "pm_long": ("Prod_Merc_Positions_Long_All",), "pm_short": ("Prod_Merc_Positions_Short_All",),
    "sw_long": ("Swap_Positions_Long_All",), "sw_short": ("Swap_Positions_Short_All", "Swap__Positions_Short_All"),
    "sw_spread": ("Swap_Positions_Spread_All", "Swap__Positions_Spread_All"),
    "mm_long": ("M_Money_Positions_Long_All",), "mm_short": ("M_Money_Positions_Short_All",), "mm_spread": ("M_Money_Positions_Spread_All",),
    "ot_long": ("Other_Rept_Positions_Long_All",), "ot_short": ("Other_Rept_Positions_Short_All",),
    "ot_spread": ("Other_Rept_Positions_Spread_All",),
    "nr_long": ("NonRept_Positions_Long_All",), "nr_short": ("NonRept_Positions_Short_All",),
}
OPTIONAL = {
    "d10": ("As_of_Date_Form_MM/DD/YYYY",), "cftc_code": ("CFTC_Contract_Market_Code",), "commodity": ("CFTC_Commodity_Code",),
    "tot_long": ("Tot_Rept_Positions_Long_All",), "tot_short": ("Tot_Rept_Positions_Short_All",),
}
for _pair in PCT_PAIRS:                  # ICE's own Pct_of_OI_<class>_<side>_All, all ten class/side pairs (A1, check 3)
    OPTIONAL[_pair + "_pct"] = ("Pct_of_OI_%s_%s_All" % (PCT_NAMES[_pair.split("_")[0]], _pair.split("_")[1].capitalize()),)
INT_KEYS = ("oi",) + tuple("%s_%s" % (k, s) for k in CK for s in ("long", "short")) + tuple("%s_spread" % k for k in SPREAD_CLASSES)
INT_RX = re.compile(r"-?[0-9]+")
PCT_RX = re.compile(r"-?[0-9]+(\.[0-9]+)?")


def canon(name):
    return name.replace("Swap__", "Swap_")


def parse_header(cells):
    """(idx, info) for a header row, or HeaderError. A BOM is stripped (A3). Extra and unnamed columns are ignored and logged."""
    names = [c.strip() for c in cells]
    if names and on("bom"):
        names[0] = names[0].lstrip("\ufeff")
    if not names or names[0] != "Market_and_Exchange_Names":
        raise HeaderError("the first column is not Market_and_Exchange_Names")
    idx = {}
    for table, mandatory in ((REQUIRED, True), (OPTIONAL, False)):
        for key, spellings in table.items():
            spellings = spellings if on("swap_spelling") else spellings[:1]
            present = [s for s in spellings if s in names]
            if len(present) > 1:
                raise HeaderError("both spellings of %s are present" % key)
            if not present:
                if mandatory:
                    raise HeaderError("required column missing: %s" % spellings[0])
                continue
            if names.count(present[0]) != 1:
                raise HeaderError("column %s appears more than once" % present[0])
            idx[key] = names.index(present[0])
    for a, b in _SWAPS:                  # selftest only: a mapping mutant reads a's cell where b's belongs and the reverse
        idx[a], idx[b] = idx[b], idx[a]
    info = dict(ncols=len(names), unnamed=[i for i, n in enumerate(names) if n == ""], canon=[canon(n) for n in names if n],
                spelling="Swap__" if any(n.startswith("Swap__") for n in names) else "Swap_", idx_max=max(idx.values()))
    return idx, info


def decode_text(raw):
    text = raw.decode("utf-8", "replace")
    if on("bom") and text.startswith("\ufeff"):
        text = text[1:]
    return text


def ice_csv_problem(body):
    """None if `body` is an ICE COT history CSV (passes the header test), else a short reason (A3)."""
    if body is None:
        return "body larger than the %d MB cap" % (BODY_CAP // (1024 * 1024))
    try:
        first = next(csv.reader(io.StringIO(decode_text(body), newline="")), None)
    except csv.Error:
        return "200 but the body is not parseable as CSV"
    if not first:
        return "200 but the body is empty"
    try:
        parse_header(first)
    except HeaderError as e:
        return "200 but the body is not the expected CSV (%s)" % e
    return None


def toint(s, what):
    s = s.strip()
    if s == "":
        if on("blank_class"):
            raise DataError("%s: blank class figure" % what)
        return 0
    if not INT_RX.fullmatch(s):
        raise DataError("%s: not an integer" % what)
    return int(s)


def new_stats():
    return dict(rows={k: 0 for k in KINDS}, side={k: 0 for k in KINDS}, net={k: 0 for k in KINDS}, units=0, names=set(), cftc=set(), comm=set(),
                dates={k: [] for k in KINDS}, non_tue=[], agree_n={p: 0 for p in PCT_PAIRS}, agree_max={p: 0.0 for p in PCT_PAIRS}, rel_err=[], bound=[])


def parse_row(cells, idx, year, ln, st):
    """One Brent row -> a record of NETS only (no gross figure leaves this function), or a DataError that names the week."""
    g = lambda k: cells[idx[k]].strip()
    where = "COTHist%d.csv line %d" % (year, ln)
    name, kind_raw = g("name"), g("kind")
    if on("type_by_column"):
        t = {"FutOnly": "fo", "Combined": "combined"}.get(kind_raw)
        if t is None:
            raise DataError("%s: FutOnly_or_Combined is %r" % (where, kind_raw))
    else:
        t = "combined" if "and Options" in name else "fo"
    d6 = g("d6")
    if not re.fullmatch(r"[0-9]{6}", d6):
        raise DataError("%s: As_of_Date_In_Form_YYMMDD is %r" % (where, d6))
    try:
        d = dt.datetime.strptime(d6, "%y%m%d").date()
    except ValueError:
        raise DataError("%s: As_of_Date_In_Form_YYMMDD %r is not a date" % (where, d6))
    if d.year != year:
        raise DataError("%s: report date %s is not in the file's year" % (where, d))
    if "d10" in idx and g("d10"):
        try:
            d10 = dt.datetime.strptime(g("d10"), "%m/%d/%Y").date()
        except ValueError:
            raise DataError("%s: As_of_Date_Form_MM/DD/YYYY %r is not a date" % (where, g("d10")))
        if d10 != d:
            raise DataError("%s: the two date fields disagree (%s vs %s)" % (where, d, d10))
    who = "%s (%s, %s)" % (where, d, t)
    if d.weekday() != 1:
        if not on("monday_dates"):
            raise DataError("%s: the report date is not a Tuesday" % who)
        st["non_tue"].append(d)
    if on("units") and not UNITS_RX.fullmatch(g("units")):
        raise DataError("%s: Contract_Units is %r, not (CONTRACTS OF 1,000 BARRELS)" % (who, g("units")))
    st["units"] += 1
    v = {k: toint(g(k), "%s %s" % (who, k)) for k in INT_KEYS}
    for k, x in v.items():
        if x < 0:
            raise DataError("%s: negative %s" % (who, k))
    oi = v["oi"]
    if oi <= 0:
        raise DataError("%s: open interest is not positive" % who)
    tol_side, tol_net = (0, 0) if (t == "fo" and on("fo_identity_exact")) else (TOL_SIDE, TOL_NET)
    for side in ("long", "short"):
        resid = sum(v["%s_%s" % (k, side)] for k in CK) + sum(v["%s_spread" % k] for k in SPREAD_CLASSES) - oi
        if abs(resid) > tol_side:
            raise DataError("%s: the five classes plus spreading plus non-reportable differ from open interest on the %s side by %d "
                            "(allowed %d); stopped, not repaired" % (who, side, resid, tol_side))
        st["side"][t] = max(st["side"][t], abs(resid))
    nets = {k: v["%s_long" % k] - v["%s_short" % k] for k in CK}
    resid_net = sum(nets.values())
    if abs(resid_net) > tol_net:
        raise DataError("%s: the five class nets sum to %d, not zero (allowed %d); stopped, not repaired" % (who, resid_net, tol_net))
    st["net"][t] = max(st["net"][t], abs(resid_net))
    for side in ("long", "short"):                          # reported totals: blank is not an error (A1); a filled one is checked
        key = "tot_" + side
        if key in idx:
            cell = g(key)
            if cell == "":
                if not on("blank_totals"):
                    raise DataError("%s: blank total reportable %s" % (who, side))
            else:
                total = toint(cell, "%s %s" % (who, key))
                rep = sum(v["%s_%s" % (k, side)] for k in ("pm", "sw", "mm", "ot")) + sum(v["%s_spread" % k] for k in SPREAD_CLASSES)
                if abs(rep - total) > tol_side:
                    raise DataError("%s: the classes plus spreading differ from the reported total reportable (%s) by %d" % (who, side, rep - total))
    for pair in PCT_PAIRS:                                  # ICE's own percentages, all ten class/side pairs (A1, check 3)
        key = pair + "_pct"
        if key in idx and g(key) != "":
            if not PCT_RX.fullmatch(g(key)):
                raise DataError("%s: %s is %r, not a number" % (who, key, g(key)))
            dev = abs(float(g(key)) - 100.0 * v[pair] / oi)
            if on("pct_agree") and dev > PCT_TOL + 1e-9:
                raise DataError("%s: ICE's own %s percentage disagrees with level / open interest by %.4fpp (allowed %.2f); a column may be read "
                                "as the wrong class or side" % (who, pair, dev, PCT_TOL))
            st["agree_n"][pair] += 1
            st["agree_max"][pair] = max(st["agree_max"][pair], dev)
    pct = round(100.0 * nets["mm"] / oi, 1)
    if pct != 0:
        st["rel_err"].append(abs(nets["mm"] / (pct / 100.0) / oi - 1.0))       # for the A5 disclosure: how well a reader could back out OI
        st["bound"].append(0.05 / abs(pct))                                    # ... and the half-width of the rounding interval around it
    st["rows"][t] += 1
    st["names"].add(name)
    st["dates"][t].append(d)
    if "cftc_code" in idx:
        st["cftc"].add(g("cftc_code"))
    if "commodity" in idx:
        st["comm"].add(g("commodity"))
    return dict(date=d, type=t, nets=nets, pct_oi=100.0 * nets["mm"] / oi)


class FileResult:
    def __init__(self, year, sha, nbytes, info, recs, st):
        self.year, self.sha, self.nbytes, self.info, self.recs, self.st = year, sha, nbytes, info, recs, st


def parse_file(raw, year):
    """Header test, then every Brent row. Raises HeaderError or DataError; never returns a gross figure."""
    text = decode_text(raw)
    rows = list(csv.reader(io.StringIO(text, newline="")))
    if not rows:
        raise HeaderError("COTHist%d.csv is empty" % year)
    idx, info = parse_header(rows[0])
    st, recs = new_stats(), []
    for ln, cells in enumerate(rows[1:], start=2):
        if not any(c.strip() for c in cells):
            continue
        if len(cells) <= info["idx_max"]:
            raise DataError("COTHist%d.csv line %d: %d cells, the header needs %d" % (year, ln, len(cells), info["idx_max"] + 1))
        if not cells[idx["name"]].strip().startswith(NAME_PREFIX):
            continue
        recs.append(parse_row(cells, idx, year, ln, st))
    if not recs:
        raise DataError("COTHist%d.csv holds no row whose market name starts with %r" % (year, NAME_PREFIX))
    return FileResult(year, sha256_of(raw), len(raw), info, recs, st)


# ------------------------------------------------------------------------------------------------------------------------
# putting the years together: one report per ISO week per type, no gaps, sane seams (A12)
# ------------------------------------------------------------------------------------------------------------------------
def assemble(files):
    """files: FileResult list. Returns (dates, by) with by[type][date] = record. Raises DataError on a duplicate, a gap or a bad seam."""
    files = sorted(files, key=lambda x: x.year)
    years = [x.year for x in files]
    if years != list(range(years[0], years[-1] + 1)):
        raise DataError("the year files are not an unbroken run: %s" % years)
    by = {t: {} for t in KINDS}
    for t in KINDS:
        seen = {}
        per_year = {}
        for fr in files:
            ds = sorted(r["date"] for r in fr.recs if r["type"] == t)
            per_year[fr.year] = ds
            for r in sorted((r for r in fr.recs if r["type"] == t), key=lambda r: r["date"]):
                k = iso_key(r["date"])
                if k in seen and on("duplicate_week"):
                    raise DataError("duplicate %s report in ISO week %s: %s and %s" % (t, iso_label(k), seen[k], r["date"]))
                seen[k] = r["date"]
                by[t][r["date"]] = r
        for y, ds in per_year.items():
            if not ds:
                raise DataError("COTHist%d.csv holds no %s rows" % (y, t))
            bad = [(a, b) for a, b in zip(ds, ds[1:]) if week_index(b) - week_index(a) != 1]
            if bad:
                raise DataError("%s: missing or doubled ISO week(s) inside COTHist%d.csv, e.g. %s to %s" % (t, y, bad[0][0], bad[0][1]))
        for y in years[:-1]:
            a, b = per_year[y][-1], per_year[y + 1][0]
            gap = (b - a).days
            if on("seam_gap") and not (6 <= gap <= 8 or (13 <= gap <= 15 and (a, b) in KNOWN_HOLIDAY_GAPS)):
                raise DataError("%s: the seam between COTHist%d.csv and COTHist%d.csv is %d days (%s to %s); allowed 6-8, or 13-15 over a known "
                                "holiday gap" % (t, y, y + 1, gap, a, b))
    if set(by["fo"]) != set(by["combined"]):
        diff = sorted(set(by["fo"]) ^ set(by["combined"]))
        raise DataError("futures-only and combined do not share the same report dates (e.g. %s)" % diff[0])
    return sorted(by["fo"]), by


# ------------------------------------------------------------------------------------------------------------------------
# prices: the EIA Europe Brent spot (public domain)
# ------------------------------------------------------------------------------------------------------------------------
def load_eia_brent(path):
    """{date: dollars per barrel} from the EIA workbook. Every failure to read it, whatever xlrd raises, is a DataError: a file that does not open
    or does not have the layout is not the expected file."""
    import xlrd
    try:
        b = xlrd.open_workbook(path)
        s = b.sheet_by_name("Data 1")
        if not ("Europe Brent Spot Price FOB" in s.cell_value(0, 1) and "Dollars per Barrel" in s.cell_value(0, 1) and s.cell_value(2, 0) == "Date"):
            raise DataError("EIA RBRTEd.xls layout changed")
        ser = {}
        for i in range(3, s.nrows):
            dv, v = s.row_values(i)[:2]
            if not isinstance(v, float):
                continue
            d = xlrd.xldate_as_datetime(dv, b.datemode).date()
            if d in ser:
                raise DataError("EIA RBRTEd.xls: duplicate date %s" % d)
            ser[d] = v
    except DataError:
        raise
    except Exception as e:             # xlrd.XLRDError, a corrupt compound document, a short sheet, a bad date serial, an unreadable file
        raise DataError("EIA RBRTEd.xls cannot be read (%s: %s)" % (type(e).__name__, " ".join(str(e).split())[:100]))
    return ser


def attach_prices(dates, series):
    """{date: (price, price_date, lag_days)}: the report-date quote, else the last earlier one; the lag is asserted at most 5 days."""
    ks = sorted(series)
    out = {}
    for d in dates:
        i = bisect.bisect_right(ks, d) - 1
        if i < 0:
            raise DataError("no Brent price on or before %s" % d)
        lag = (d - ks[i]).days
        if on("price_lag") and lag > MAX_PRICE_LAG_DAYS:
            raise DataError("%s: the nearest earlier Brent price is %d days old" % (d, lag))
        p = series[ks[i]]
        if not PRICE_RANGE[0] <= p <= PRICE_RANGE[1]:
            raise DataError("%s: Brent price %s is outside the plausible range" % (d, p))
        out[d] = (p, ks[i], lag)
    return out


def is_suspect_print(d, ranges=KNOWN_SUSPECT_PRINTS):
    """True if the EIA print dated `d` is in a known-bad range (KNOWN_SUSPECT_PRINTS)."""
    return any(a <= d <= b for a, b in ranges)


# ------------------------------------------------------------------------------------------------------------------------
# numbers: windows and the lead-lag test (the same method as pull_cftc_cot.py)
# ------------------------------------------------------------------------------------------------------------------------
def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
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


def leadlag_row(contract, kind, dates, N, P, late_split=LATE_SPLIT):
    """One row of leadlag.csv's columns. N: managed-money net by week; P: price by week; both aligned with `dates` (ISO strings or dates)."""
    ds = [d if isinstance(d, dt.date) else dt.date.fromisoformat(d) for d in dates]
    t0 = max(1, next(i for i, d in enumerate(ds) if d >= late_split))
    ts = list(range(t0, len(ds)))
    dn = {t: N[t] - N[t - 1] for t in ts}
    ret = {t: P[t] / P[t - 1] - 1 for t in range(1, len(ds))}
    dp = {t: P[t] - P[t - 1] for t in range(1, len(ds))}
    row = {"contract": contract, "report_type": kind, "first_week": ds[ts[0]].isoformat(), "last_week": ds[ts[-1]].isoformat()}
    for tag, shift in (("same", 0), ("next", 1), ("prev", -1)):
        tt = [t for t in ts if 1 <= t + shift < len(ds)]      # as pull_cftc_cot.py: next drops the last week; prev needs a price change a week earlier
        x = [dn[t] for t in tt]
        y = [ret[t + shift] for t in tt]
        z = [dp[t + shift] for t in tt]
        row["n_" + tag] = len(tt)
        row["pearson_%s_pct" % tag] = f(pearson(x, y), 3)
        row["spearman_%s_pct" % tag] = f(pearson(ranks(x), ranks(y)), 3)
        row["pearson_%s_abs" % tag] = f(pearson(x, z), 3)
        row["band95_" + tag] = f(1.96 / math.sqrt(len(tt)), 3)
    return row


def window_rows(dates, mm, pct, anchors=ANCHORS):
    """brent_windows.csv rows. mm[kind] = managed-money net per week, pct[kind] = share of OI (exact) per week."""
    rows, i1 = [], len(dates) - 1
    specs = [("4 weeks", i1 - 4), ("12 weeks", i1 - 12), ("52 weeks", i1 - 52)]
    for label, qe, _expect in anchors:
        cand = [i for i, d in enumerate(dates) if d <= qe]
        if not cand:
            raise DataError("no report on or before %s for the window %r" % (qe, label))
        specs.append((label, cand[-1]))
    for kind in KINDS:
        for label, i0 in specs:
            if i0 < 0:
                raise DataError("not enough weeks for the window %r" % label)
            chg = mm[kind][i1] - mm[kind][i0]
            rows.append(["brent", kind, label, str(i1 - i0), dates[i0].isoformat(), dates[i1].isoformat(), str(mm[kind][i0]), str(mm[kind][i1]), str(chg),
                         str(chg * BBL_PER_CONTRACT), f(pct[kind][i0], 1), f(pct[kind][i1], 1)])
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# the build
# ------------------------------------------------------------------------------------------------------------------------
def src_line(span_ice, eia_date=None):
    s = SOURCE_ICE + "; ICE files retrieved " + (span_ice[0] if span_ice[0] == span_ice[1] else span_ice[0] + " to " + span_ice[1])
    if eia_date:
        s += "; EIA Europe Brent spot price (eia.gov, US government, public domain) retrieved " + eia_date
    return s


def log_path(out_dir):
    return os.path.join(out_dir, "fetch_log.csv")


def ice_path(year):
    return "%sCOTHist%d.csv" % (ICE_PREFIX, year)


def log_row_for(rows, host, path, sha):
    """The latest log row that saved or adopted this exact content, or None."""
    hit = [r for r in rows if r[1] == host and r[2] == path and r[3] in ("200", "") and r[4] in ("saved", "adopted_from_cache") and r[6] == sha]
    return sorted(hit, key=lambda r: r[0])[-1] if hit else None


def cache_years(cache):
    out = {}
    if os.path.isdir(cache):
        for n in os.listdir(cache):
            m = re.fullmatch(r"COTHist(20[0-9]{2})\.csv", n)
            if m and int(m.group(1)) >= FIRST_YEAR:
                out[int(m.group(1))] = os.path.join(cache, n)
    return out


def make_checks(ctx):
    """checks.csv rows from the build context. Hard checks that fail raise before this point; they appear here as PASS with the observed value."""
    C = []

    def add(cid, check, expected, observed, status, note=""):
        C.append([cid, check, str(expected), str(observed), status, note])

    st = ctx["stats"]
    add("K01", "futures-only identities (5 classes + spreading + non-reportable = open interest, both sides; five nets = 0)", "0 and 0",
        "%d and %d" % (max(s["side"]["fo"] for s in st), max(s["net"]["fo"] for s in st)), "PASS",
        "maximum absolute residual over all %d futures-only rows, contracts; the cells add up as one set on each side; blind to two classes exchanged on the same side (K03 sees that) and does not show that non-reportable is measured" % ctx["rows"]["fo"])
    add("K02", "combined identities, same, to rounding", "<=%d per side, <=%d on the net sum" % (TOL_SIDE, TOL_NET),
        "%d per side, %d on the net sum" % (max(s["side"]["combined"] for s in st), max(s["net"]["combined"] for s in st)), "PASS",
        "maximum absolute residual over all %d combined rows, contracts" % ctx["rows"]["combined"])
    n_rows = ctx["rows"]["fo"] + ctx["rows"]["combined"]
    pn = {p: sum(s["agree_n"][p] for s in st) for p in PCT_PAIRS}
    px_ = {p: max(s["agree_max"][p] for s in st) for p in PCT_PAIRS}
    short = [p for p in PCT_PAIRS if pn[p] < n_rows]
    add("K03", "ICE's own Pct_of_OI percentages vs level / open interest, all ten class/side pairs (pm, sw, mm, ot, nr x long, short)",
        "<=%.2fpp on every populated value, populated on all %d rows" % (PCT_TOL, n_rows),
        "; ".join("%s n=%d max=%.4fpp" % (p, pn[p], px_[p]) for p in PCT_PAIRS), "WARN" if short else "PASS",
        ("populated on fewer rows than there are: " + ", ".join("%s %d of %d" % (p, pn[p], n_rows) for p in short)) if short else
        "hard check (a gap above the bound stops the build); sees an exchange of two classes on the same side; spreading columns are not covered")
    add("K04", "Contract_Units reads (CONTRACTS OF 1,000 BARRELS)", "every Brent row", "%d rows" % sum(s["units"] for s in st), "PASS")
    add("K05", "one report per ISO week per type, none missing, seams 6-8 days", "no duplicate, no gap",
        "%d weeks, %s to %s" % (len(ctx["dates"]), ctx["dates"][0], ctx["dates"][-1]), "PASS",
        "known 13-15 day holiday gaps accepted: %d" % len(KNOWN_HOLIDAY_GAPS))
    unknown = [d for d in ctx["non_tue"] if d not in KNOWN_MONDAYS]
    add("K06", "report dates that are not Tuesdays", "only the known Mondays %s" % ", ".join(d.isoformat() for d in sorted(KNOWN_MONDAYS)),
        ", ".join(d.isoformat() for d in sorted(ctx["non_tue"])) or "none", "WARN" if unknown else "PASS",
        ("not known: " + ", ".join(d.isoformat() for d in sorted(unknown))) if unknown else "")
    add("K07", "price lag (report date to the quote used)", "<=%d days" % MAX_PRICE_LAG_DAYS, "max %d day(s); %d of %d weeks carried back"
        % (ctx["lag_max"], ctx["lag_n"], len(ctx["dates"])), "PASS")
    for cid, (d, kind, want) in zip(("K08", "K09"), ctx["pins"]):
        got = ctx["mm"][kind][ctx["dates"].index(d)] if d in ctx["dates"] else None
        ok = got == want
        add(cid, "pinned managed-money net, %s, %s" % (d, kind), want, "n/a (date not in the ledger)" if got is None else got, "PASS" if ok else "WARN",
            "" if ok else "ICE may have restated; the build is not stopped")
    if ctx["kemp"] is not None:
        obs = ctx["kemp"]
        rel = obs / KEMP_BBL - 1.0
        add("K10", "Kemp (relayed, not verified at source): combined managed-money net, %s, barrels" % KEMP_DATE, "%d +-%d%%" % (KEMP_BBL, round(KEMP_TOL * 100)),
            "%d (%+.2f%%)" % (obs, rel * 100), "PASS" if abs(rel) <= KEMP_TOL else "WARN", "warn only; futures and options")
    add("K11", "last report date equals the last date in the newest year file", ctx["last_in_file"].isoformat(), ctx["dates"][-1].isoformat(),
        "PASS" if ctx["dates"][-1] == ctx["last_in_file"] else "FAIL")
    exp = ctx["expected_tue"]
    if exp is not None:
        status = "PASS" if ctx["dates"][-1] == exp else ("WARN" if ctx["dates"][-1] < exp else "FAIL")
        add("K12", "last report date equals the latest expected report Tuesday as of the newest file's retrieval (%s)" % ctx["retrieved_last"], exp.isoformat(),
            ctx["dates"][-1].isoformat(), status, "ICE publishes on Fridays; a shortfall means the file may pre-date the release" if status == "WARN" else "")
    for cid, (label, expect, got) in zip(("K13", "K14"), ctx["anchor_dates"]):
        add(cid, "window anchor %r is the %s report" % (label, expect), expect.isoformat(), got.isoformat(), "PASS" if got == expect else "WARN")
    vr = ctx["verified"]               # {file: (header, body)} for the files whose written text was verified before this row was made
    add("K15", "every output header equals its allowlist and carries no banned gross name", "all %d output files" % len(ALLOW),
        "%d of %d verified when this row was made (%s): %d header cells, %d banned names" % (
            len(vr), len(ALLOW), ", ".join(sorted(vr)), sum(len(h) for h, _ in vr.values()), sum(1 for h, _ in vr.values() for c in h if BANNED_HDR.search(c))),
        "PASS" if all(list(h) == ALLOW[n] for n, (h, _) in vr.items()) and not any(BANNED_HDR.search(c) for h, _ in vr.values() for c in h) else "FAIL",
        "checks.csv itself is verified as it is written")
    pcells = [(n, h_, r[hd.index(h_)]) for n, (hd, body) in vr.items() for h_ in PERCENT_COLS.get(n, []) for r in body if r[hd.index(h_)] != ""]
    decs = max((len(c.split(".")[1]) if "." in c else 0) for _, _, c in pcells) if pcells else 0
    add("K16", "percent columns carry at most one decimal in the written text", "at most 1 decimal (0.1pp)",
        "%d cells in %d columns of %d files; most decimals found: %d" % (len(pcells), len({(n, h_) for n, h_, _ in pcells}), len({n for n, _, _ in pcells}), decs),
        "PASS" if decs <= 1 else "FAIL")
    if ctx["rel_err"]:
        q = lambda xs, a: sorted(xs)[int(a * (len(xs) - 1))]
        e, b = ctx["rel_err"], ctx["bound"]
        add("K17", "how well open interest can be back-calculated from managed-money net and its rounded percent (A5)", "about +-0.6% (median half-width, supervisor)",
            "rounding half-width median +-%.2f%%, 90th percentile +-%.2f%%; realised error median %.2f%%, 90th percentile %.2f%%, max %.1f%%; %d of %d week-types (percent rounds to 0.0: not invertible)" % (
                100 * statistics.median(b), 100 * q(b, 0.9), 100 * statistics.median(e), 100 * q(e, 0.9), 100 * max(e), len(e), 2 * len(ctx["dates"])), "INFO",
            "relative error of mm_net / (rounded pct / 100) against the true figure; disclosed in SOURCES_ICE.md")
    add("K18", "column sets across year files (O-1)", "logged", "%d year files; spellings %s" % (len(ctx["files"]), ", ".join(
        "%s x%d" % (s, n) for s, n in sorted(ctx["spellings"].items()))), "INFO", "see brent_file_stats.csv for columns added and removed")
    return C


def build(cache, out_dir, prices=None, eia_date=None, pins=None, anchors=None, kemp=True, say=print, write=True, window_check=True, suspect=None):
    """Offline. Reads the cache, verifies it against fetch_log.csv, validates, computes and (unless write=False) writes every output.
    `prices` ({date: price}) replaces the EIA file (selftest only); so does `suspect` for KNOWN_SUSPECT_PRINTS. Returns a context dict."""
    cache = check_cache(cache)
    pins = PINS if pins is None else pins
    anchors = ANCHORS if anchors is None else anchors
    suspect = KNOWN_SUSPECT_PRINTS if suspect is None else suspect
    avail = cache_years(cache)
    if not avail:
        raise DataError("no COTHist<YYYY>.csv in %s; run: python3 bin/pull_ice_brent_cot.py fetch" % tilde(cache))
    years = sorted(avail)
    if years != list(range(years[0], years[-1] + 1)):
        raise DataError("the cache has years %s: not an unbroken run; run fetch --years for the missing ones" % years)
    log = read_table(log_path(out_dir), FETCH_LOG_COLS)
    files, retr = [], {}
    for y in years:
        raw = open(avail[y], "rb").read()
        row = log_row_for(log, ICE_HOST, ice_path(y), sha256_of(raw))
        if row is None:
            raise DataError("COTHist%d.csv is not in %s with this content; run fetch (it adopts files already in the cache)" % (y, tilde(log_path(out_dir))))
        retr[y] = row
        say("  parsing COTHist%d.csv ..." % y)
        files.append(parse_file(raw, y))
    dates, by = assemble(files)
    eia_log = None
    if prices is None:
        eia_file = os.path.join(out_dir, "raw", EIA_RAW_NAME)
        if not os.path.exists(eia_file):
            raise DataError("%s is missing; run fetch" % tilde(eia_file))
        eia_log = log_row_for(log, EIA_HOST, EIA_PATH, sha256_file(eia_file))
        if eia_log is None:
            raise DataError("%s is not in fetch_log.csv with this content; run fetch" % EIA_RAW_NAME)
        prices = load_eia_brent(eia_file)
        eia_date = eia_log[0][:10]
    px = attach_prices(dates, prices)
    span = (min(r[0][:10] for r in retr.values()), max(r[0][:10] for r in retr.values()))
    source = src_line(span, eia_date)

    nets = {t: {k: [by[t][d]["nets"][k] for d in dates] for k in CK} for t in KINDS}
    mm = {t: nets[t]["mm"] for t in KINDS}
    pct = {t: [by[t][d]["pct_oi"] for d in dates] for t in KINDS}
    P = [px[d][0] for d in dates]

    # ledger
    led = []
    for i, d in enumerate(dates):
        flag = PRICE_FLAG if on("price_flag") and is_suspect_print(px[d][1], suspect) else ""      # the USD figures below stay as computed
        row = [d.isoformat(), px[d][1].isoformat(), str(px[d][2]), f(px[d][0], 4), USD_BASIS, flag]
        for t in KINDS:
            n = {k: nets[t][k][i] for k in CK}
            row += [str(n[k]) for k in CK] + [str(n[k] * BBL_PER_CONTRACT) for k in CK] + [str(sum(n.values()))]
            row += ["" if i == 0 else str(n[k] - nets[t][k][i - 1]) for k in CK]
            row += [f(pct[t][i], 1), f(n["mm"] * BBL_PER_CONTRACT * px[d][0] / 1e9, 6)]
        led.append(row)
    # windows, lead-lag
    win = window_rows(dates, mm, pct, anchors) if window_check else []
    ll = [leadlag_row("brent", t, dates, mm[t], P) for t in KINDS]
    ll_rows = [[str(r[c]) for c in LEADLAG_COLS] for r in ll]
    # file stats
    fs, prev = [], None
    for fr, y in zip(files, years):
        st = fr.st
        cur = set(fr.info["canon"])
        added = "" if prev is None else ";".join(sorted(cur - prev))
        removed = "" if prev is None else ";".join(sorted(prev - cur))
        prev = cur
        alld = sorted(set(st["dates"]["fo"]) | set(st["dates"]["combined"]))
        r = retr[y]
        fs.append([str(y), "COTHist%d.csv" % y, fr.sha, str(fr.nbytes), r[0][:19] + "Z", "fetch_log:" + r[4], str(fr.info["ncols"]), fr.info["spelling"],
                   ";".join(str(i + 1) for i in fr.info["unnamed"]), added, removed, "|".join(sorted(st["names"])), "|".join(sorted(st["cftc"])),
                   "|".join(sorted(st["comm"])), str(st["rows"]["fo"]), str(st["rows"]["combined"]), alld[0].isoformat(), alld[-1].isoformat(),
                   ";".join(d.isoformat() for d in sorted(set(st["non_tue"]))), str(st["units"]), str(st["side"]["fo"]), str(st["net"]["fo"]),
                   str(st["side"]["combined"]), str(st["net"]["combined"]), str(sum(st["agree_n"].values()))])
    # checks
    kemp_obs = None
    if kemp and KEMP_DATE in dates:
        kemp_obs = mm["combined"][dates.index(KEMP_DATE)] * BBL_PER_CONTRACT
    ret_last = retr[years[-1]][0][:10]
    anchor_dates = []
    for label, qe, expect in anchors:
        cand = [d for d in dates if d <= qe]
        anchor_dates.append((label, expect, cand[-1] if cand else expect))
    ctx = dict(dates=dates, by=by, nets=nets, mm=mm, pct=pct, px=px, P=P, files=files, stats=[x.st for x in files], rows={t: sum(x.st["rows"][t] for x in files) for t in KINDS},
               non_tue=sorted({d for x in files for d in x.st["non_tue"]}), lag_max=max(px[d][2] for d in dates), lag_n=sum(1 for d in dates if px[d][2]),
               pins=list(pins), kemp=kemp_obs, n_flagged=sum(1 for d in dates if is_suspect_print(px[d][1], suspect)) if on("price_flag") else 0, last_in_file=max(r["date"] for r in files[-1].recs), expected_tue=latest_expected_tuesday(dt.date.fromisoformat(ret_last)),
               retrieved_last=ret_last, anchor_dates=anchor_dates, rel_err=[e for x in files for e in x.st["rel_err"]], bound=[e for x in files for e in x.st["bound"]],
               spellings=collections.Counter(x.info["spelling"] for x in files), led=led, win=win, ll=ll, ll_rows=ll_rows, fs=fs,
               source=source, span=span, eia_date=eia_date, anchors=anchors)
    texts = {"brent_ledger.csv": render_table(LEDGER_COLS, led, source), "brent_windows.csv": render_table(WINDOWS_COLS, win, source),
             "brent_leadlag.csv": render_table(LEADLAG_COLS, ll_rows, source), "brent_file_stats.csv": render_table(FILE_STATS_COLS, fs, source)}
    ctx["verified"] = {name: verify_text(name, text) for name, text in texts.items()}      # what checks K15 and K16 report, observed
    if os.path.exists(log_path(out_dir)):
        with open(log_path(out_dir), encoding="utf-8", newline="") as fh:
            ctx["verified"]["fetch_log.csv"] = verify_text("fetch_log.csv", fh.read())
    chk = make_checks(ctx)
    ctx["chk"] = chk
    texts["checks.csv"] = render_table(CHECKS_COLS, chk, source)
    verify_text("checks.csv", texts["checks.csv"])
    ctx["texts"] = texts
    if write:
        for name, text in texts.items():
            write_text(os.path.join(out_dir, name), text)
            if open(os.path.join(out_dir, name), encoding="utf-8", newline="").read() != text:
                raise DataError("%s was not written as verified" % name)
    return ctx


def wti_compare(ll):
    """Print n beside WTI's lead-lag row, and say why they differ (dates in one ledger and not the other)."""
    p = os.path.join(WTI_DIR, "leadlag.csv")
    q = os.path.join(WTI_DIR, "wti_ledger.csv")
    if not (os.path.exists(p) and os.path.exists(q)):
        return ["  (WTI files data/cftc_cot/leadlag.csv and wti_ledger.csv not present: no comparison)"]
    out = []
    with open(p, newline="", encoding="utf-8") as fh:
        wti = {r["report_type"]: r for r in csv.DictReader(l for l in fh if not l.startswith("#"))}
    with open(q, newline="", encoding="utf-8") as fh:
        wdates = [r["report_date"] for r in csv.DictReader(l for l in fh if not l.startswith("#"))]
    for r in ll:
        w = wti.get(r["report_type"])
        if not w:
            continue
        out.append("  %-8s Brent n_same/n_next/n_prev = %s/%s/%s (first %s, last %s)   WTI = %s/%s/%s (first %s, last %s)" % (
            r["report_type"], r["n_same"], r["n_next"], r["n_prev"], r["first_week"], r["last_week"], w["n_same"], w["n_next"], w["n_prev"], w["first_week"], w["last_week"]))
    return out


def wti_date_diff(dates):
    q = os.path.join(WTI_DIR, "wti_ledger.csv")
    if not os.path.exists(q):
        return None
    with open(q, newline="", encoding="utf-8") as fh:
        w = {dt.date.fromisoformat(r["report_date"]) for r in csv.DictReader(l for l in fh if not l.startswith("#"))}
    b = {d for d in dates if d >= LATE_SPLIT}
    w = {d for d in w if d >= LATE_SPLIT}
    return sorted(b - w), sorted(w - b)


def report(ctx):
    dates, mm, px = ctx["dates"], ctx["mm"], ctx["px"]
    L = []
    P = L.append
    P("ICE Brent crude COT ledger: %d weekly reports, %s to %s, x 2 report types = %d rows; one report in every ISO week, none missing" % (
        len(dates), dates[0], dates[-1], sum(ctx["rows"].values())))
    P("IDENTITIES (asserted on every row; gross figures never written):")
    P("   futures only: held EXACTLY on all %d rows (largest residual over the five nets or either side: %d)" % (
        ctx["rows"]["fo"], max(max(s["side"]["fo"], s["net"]["fo"]) for s in ctx["stats"])))
    P("   combined: within rounding on all %d rows; per year (largest per-side / net-sum residual, contracts; allowed %d / %d):" % (ctx["rows"]["combined"], TOL_SIDE, TOL_NET))
    P("   %6s %12s %12s %12s %12s %9s %9s" % ("year", "fo side", "fo net-sum", "co side", "co net-sum", "pct n", "pct max"))
    for fr in ctx["files"]:
        s = fr.st
        P("   %6d %12d %12d %12d %12d %9d %8.4f" % (fr.year, s["side"]["fo"], s["net"]["fo"], s["side"]["combined"], s["net"]["combined"],
                                                  sum(s["agree_n"].values()), max(s["agree_max"].values())))
    P("   ICE's own Pct_of_OI percentages agree with level / open interest within %.2fpp on all %d populated values of the ten class/side pairs (largest gap %.4fpp):" % (
        PCT_TOL, sum(sum(s["agree_n"].values()) for s in ctx["stats"]), max(max(s["agree_max"].values()) for s in ctx["stats"])))
    n_rows = ctx["rows"]["fo"] + ctx["rows"]["combined"]
    P("   %-9s %7s %9s" % ("pair", "n/rows", "max gap pp"))
    for pr in PCT_PAIRS:
        P("   %-9s %7s %9.4f" % (pr, "%d/%d" % (sum(s["agree_n"][pr] for s in ctx["stats"]), n_rows), max(s["agree_max"][pr] for s in ctx["stats"])))
    P("DATES: first report %s, last %s; non-Tuesday dates: %s" % (dates[0], dates[-1], ", ".join(d.isoformat() + (" (known)" if d in KNOWN_MONDAYS else " (NOT KNOWN)") for d in ctx["non_tue"]) or "none"))
    P("   market names: %s" % "; ".join(sorted({n for s in ctx["stats"] for n in s["names"]})))
    P("   CFTC_Contract_Market_Code seen: %s; CFTC_Commodity_Code seen: %s" % (sorted({c for s in ctx["stats"] for c in s["cftc"]}), sorted({c for s in ctx["stats"] for c in s["comm"]})))
    P("PRICES: EIA Europe Brent spot FOB; %d of %d weeks carried back (max %d day(s)); range %.2f to %.2f; %d report date(s) flagged %s" % (
        ctx["lag_n"], len(dates), ctx["lag_max"], min(v[0] for v in px.values()), max(v[0] for v in px.values()), ctx["n_flagged"], PRICE_FLAG))
    P("")
    show = sorted({a[2] for a in ctx["anchor_dates"]} | {d for d, _, _ in ctx["pins"] if d in dates} | ({KEMP_DATE} if KEMP_DATE in dates else set())
                  | {dates[-5], dates[-1]})
    P("MANAGED-MONEY NET by report date (long - short; spreading excluded; negative is net short); 1 contract = 1,000 barrels")
    P("   %-11s %-9s %12s %16s %9s %13s" % ("report date", "type", "contracts", "barrels", "% of OI", "$bn at spot"))
    for d in show:
        i = dates.index(d)
        for t in KINDS:
            P("   %-11s %-9s %12d %16d %8.1f%% %13.2f" % (d, t, mm[t][i], mm[t][i] * BBL_PER_CONTRACT, ctx["pct"][t][i], mm[t][i] * BBL_PER_CONTRACT * px[d][0] / 1e9))
    P("")
    P("WINDOWS (change in managed-money net)")
    P("   %-9s %-22s %5s %-10s %-10s %12s %16s" % ("type", "window", "weeks", "from", "to", "chg contr.", "chg barrels"))
    for r in ctx["win"]:
        P("   %-9s %-22s %5s %-10s %-10s %12d %16d" % (r[1], r[2], r[3], r[4], r[5], int(r[8]), int(r[9])))
    P("")
    P("LEAD-LAG, weekly change in managed-money net contracts vs %% change in the Brent spot, report dates from %s" % LATE_SPLIT)
    P("   %-8s %-9s %6s %12s %13s %10s %6s %12s %13s %10s %12s %13s %10s" % ("contract", "type", "n same", "Pearson same", "Spearman same", "abs $ same", "n next",
                                                                            "Pearson next", "Spearman next", "abs $ next", "Pearson prev", "Spearman prev", "band same"))
    for r in ctx["ll"]:
        P("   %-8s %-9s %6d %+12.3f %+13.3f %+10.3f %6d %+12.3f %+13.3f %+10.3f %+12.3f %+13.3f %10s" % (
            r["contract"], r["report_type"], r["n_same"], float(r["pearson_same_pct"]), float(r["spearman_same_pct"]), float(r["pearson_same_abs"]), r["n_next"],
            float(r["pearson_next_pct"]), float(r["spearman_next_pct"]), float(r["pearson_next_abs"]), float(r["pearson_prev_pct"]), float(r["spearman_prev_pct"]),
            r["band95_same"]))
    for ln in wti_compare(ctx["ll"]):
        P(ln)
    dif = wti_date_diff(dates)
    if dif is not None:
        P("   report dates from %s in Brent and not in WTI: %s; in WTI and not in Brent: %s" % (
            LATE_SPLIT, ", ".join(d.isoformat() for d in dif[0]) or "none", ", ".join(d.isoformat() for d in dif[1]) or "none"))
    P("")
    P("CHECKS (data/ice_brent/checks.csv):")
    for c in ctx["chk"]:
        P("   %-4s %-5s %s | expected %s | observed %s%s" % (c[0], c[4], c[1], c[2], c[3], (" | " + c[5]) if c[5] else ""))
    return L


# ------------------------------------------------------------------------------------------------------------------------
# fetching: the only network code. One request at a time, paced, GET only, STOP latch  [E-025, A9]
# ------------------------------------------------------------------------------------------------------------------------
def real_opener(host, target, headers, timeout, cap):
    """GET https://host/target. Returns (status, body); body is None when it exceeds `cap`. No redirect is followed (a 3xx comes back as a
    status and latches), no cookies, the only verb is GET. Socket-level faults raise SocketFault."""
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


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


class Fetcher:
    """All requests go through here. Injectable opener, clock, sleeper and STOP path make it testable without a network."""

    def __init__(self, cache, out_dir, sleep=MIN_SLEEP, max_requests=MAX_REQUESTS, opener=real_opener, wall=time.time, mono=time.monotonic,
                 sleeper=time.sleep, stop_path=STOP_PATH, now_utc=None, pid_alive=None, eia_loader=None):
        if on("min_sleep") and sleep < MIN_SLEEP:
            raise Refused("--sleep must be at least %.2f seconds" % MIN_SLEEP)
        if on("max_requests") and (max_requests > MAX_REQUESTS or max_requests < 1):
            raise Refused("--max-requests must be between 1 and %d" % MAX_REQUESTS)
        self.cache = check_cache(cache)
        self.out_dir = out_dir
        self.sleep, self.max_requests = float(sleep), max_requests
        self.opener, self.wall, self.mono, self.sleeper = opener, wall, mono, sleeper
        self.stop_path = stop_path
        self.now_utc = now_utc or (lambda: dt.datetime.now(dt.timezone.utc))
        self.pid_alive = pid_alive or _pid_alive
        self.eia_loader = eia_loader or load_eia_brent
        self.requests = 0
        self._last_mono = None
        # The pacing record and the lock sit beside the fixed STOP path, not in the cache: the 5 s apply to the host, whichever --cache a run uses.
        self.pace_dir = os.path.dirname(stop_path) if on("shared_pacing") else self.cache
        self._lock = os.path.join(self.pace_dir, ".fetch.lock")
        self._last_file = os.path.join(self.pace_dir, ".last_request")
        self.log_path = log_path(out_dir)
        self._locked = False

    # -- lifecycle ------------------------------------------------------------------------------------------------
    def __enter__(self):
        if on("stop_blocks_fetch") and os.path.exists(self.stop_path):
            with open(self.stop_path, encoding="utf-8") as fh:
                why = fh.read().strip().replace("\n", " ")[:200]
            raise Latched("STOP exists at %s (%s); a human must inspect and delete it" % (tilde(self.stop_path), why))
        os.makedirs(self.cache, exist_ok=True)
        os.makedirs(self.pace_dir, exist_ok=True)
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
                    with open(self._lock, encoding="utf-8") as fh:
                        pid_s, t_s = (fh.read().split() + ["0", "0"])[:2]
                    pid, t0 = int(pid_s), float(t_s)
                except (ValueError, OSError):
                    pid, t0 = 0, 0.0
                if pid > 0 and self.pid_alive(pid) and self.wall() - t0 < 6 * 3600:
                    raise Refused("another fetcher holds %s (pid %d)" % (tilde(self._lock), pid))
                os.remove(self._lock)          # stale: dead pid or older than six hours
                continue
            with os.fdopen(fd, "w") as fh:
                fh.write("%d %.0f\n" % (os.getpid(), self.wall()))
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
            with open(self._last_file, encoding="utf-8") as fh:
                last = float(fh.read().strip())
            wait = max(wait, min(self.sleep, self.sleep - (self.wall() - last)))
        except (OSError, ValueError):
            pass
        if self._last_mono is not None:
            wait = max(wait, self.sleep - (self.mono() - self._last_mono))
        if wait > 0 and on("pacing"):
            self.sleeper(wait)

    def _get(self, host, path):
        """Returns (status, body, started_wall). Raises SocketFault (after logging it, and latching only if the guard is off)."""
        check_url("https://" + host + path)
        if self.requests >= self.max_requests:
            raise MaxRequests("--max-requests reached (%d)" % self.max_requests)
        self._pace()
        started = self.wall()
        self._last_mono = self.mono()
        with open(self._last_file, "w", encoding="utf-8") as fh:
            fh.write("%r\n" % started)               # repr: the float exactly, not rounded to milliseconds
        self.requests += 1
        try:
            status, body = self.opener(host, path, HEADERS, TIMEOUT, BODY_CAP)
        except SocketFault as e:
            self._log(started, host, path, "", "socket_fault:" + str(e), "", "")
            if not on("socket_no_latch"):
                self._latch("socket fault (%s) for %s" % (e, path))
            raise
        return status, body, started

    def _stamp(self, ts):
        return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % int((ts % 1) * 1000)

    def _log(self, ts, host, path, status, outcome, nbytes, sha):
        rows = read_table(self.log_path, FETCH_LOG_COLS)
        rows.append([self._stamp(ts), host, path, str(status), outcome, str(nbytes), sha])
        text = render_table(FETCH_LOG_COLS, rows, SOURCE_LOG)
        verify_text("fetch_log.csv", text)
        write_text(self.log_path, text)

    def _latch(self, reason):
        os.makedirs(os.path.dirname(self.stop_path), exist_ok=True)
        with open(self.stop_path, "w", encoding="utf-8") as fh:
            fh.write("%s UTC  %s\n" % (self.now_utc().strftime("%Y-%m-%dT%H:%M:%S"), reason))
        raise Latched(reason)

    # -- adoption: files that were already in the cache before this script fetched anything -----------------------
    def adopt_cached(self):
        """Files placed in the cache by hand (no network, no request): one `adopted_from_cache` log row per file whose content the log
        does not know, stamped with the file's modification time. Returns the number adopted."""
        rows = read_table(self.log_path, FETCH_LOG_COLS)
        n = 0
        for y, p in sorted(cache_years(self.cache).items()):
            raw = open(p, "rb").read()
            sha = sha256_of(raw)
            if log_row_for(rows, ICE_HOST, ice_path(y), sha) is None:
                rows.append([self._stamp(os.path.getmtime(p)), ICE_HOST, ice_path(y), "", "adopted_from_cache", str(len(raw)), sha])
                n += 1
        if n:
            rows.sort(key=lambda r: r[0])
            text = render_table(FETCH_LOG_COLS, rows, SOURCE_LOG)
            verify_text("fetch_log.csv", text)
            write_text(self.log_path, text)
        return n

    def _done_today(self, host, path, sha=None):
        today = self.now_utc().strftime("%Y-%m-%d")
        return any(r[1] == host and r[2] == path and r[4] == "saved" and r[0][:10] == today for r in read_table(self.log_path, FETCH_LOG_COLS))

    def _refuse_response(self, started, host, path, status, body, bad_body_reason):
        """Common handling: non-200 or a bad body latches (unless that guard is switched off in the selftest)."""
        if status != 200:
            self._log(started, host, path, status, "STOP:http_%d" % status, "", "")
            if on("latch_non200"):
                self._latch("HTTP %d for %s" % (status, path))
            return True
        if bad_body_reason:
            self._log(started, host, path, status, "STOP:bad_body", "", "")
            if on("latch_bad_body"):
                self._latch("%s (%s)" % (bad_body_reason, path))
            return True
        return False

    # -- ICE ------------------------------------------------------------------------------------------------------
    def fetch_ice_year(self, year, cur_year, refresh=False):
        """Returns an outcome word. Raises Latched / SocketFault / MaxRequests / Refused. `refresh` requests a cached past-year file again."""
        if year < FIRST_YEAR or year > cur_year:
            raise Refused("year %d is outside %d..%d (the report year)" % (year, FIRST_YEAR, cur_year))
        name = "COTHist%d.csv" % year
        path = os.path.join(self.cache, name)
        if os.path.exists(path) and year < cur_year and not refresh:
            return "cached"
        if os.path.exists(path) and self._done_today(ICE_HOST, ice_path(year)):
            return "cached_today"
        status, body, started = self._get(ICE_HOST, ice_path(year))
        prob = ice_csv_problem(body) if status == 200 else None
        if self._refuse_response(started, ICE_HOST, ice_path(year), status, body, prob):
            return "refused_unlatched"
        with open(path + ".part", "wb") as fh:
            fh.write(body)
        os.replace(path + ".part", path)
        self._log(started, ICE_HOST, ice_path(year), status, "saved", len(body), sha256_of(body))
        return "saved"

    # -- EIA ------------------------------------------------------------------------------------------------------
    def fetch_eia(self):
        raw_dir = os.path.join(self.out_dir, "raw")
        path = os.path.join(raw_dir, EIA_RAW_NAME)
        if os.path.exists(path) and self._done_today(EIA_HOST, EIA_PATH):
            return "cached_today"
        status, body, started = self._get(EIA_HOST, EIA_PATH)
        part = path + ".part"
        prob = None
        if status == 200:
            if body is None:
                prob = "body larger than the cap"
            elif on("xls_magic") and not body.startswith(XLS_MAGIC):
                prob = "200 but the body is not an XLS file"
            else:
                os.makedirs(raw_dir, exist_ok=True)
                with open(part, "wb") as fh:
                    fh.write(body)
                if on("eia_validate"):                       # the build's own reader must be able to load it, before it replaces anything
                    try:
                        self.eia_loader(part)
                    except DataError as e:
                        prob = "200 but the XLS does not load (%s)" % e
                        os.remove(part)                      # a refused body leaves nothing behind, and the file already saved is untouched
        if self._refuse_response(started, EIA_HOST, EIA_PATH, status, body, prob):
            return "refused_unlatched"
        os.replace(part, path)
        self._log(started, EIA_HOST, EIA_PATH, status, "saved", len(body), sha256_of(body))
        return "saved"


def parse_years(spec, cur):
    out = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"(20[0-9]{2})(?:-(20[0-9]{2}))?", part)
        if not m:
            raise Refused("--years: %r is not a year or a range like 2012-2017" % part)
        a = int(m.group(1))
        b = int(m.group(2) or a)
        if b < a:
            raise Refused("--years: %r runs backwards" % part)
        out.update(range(a, b + 1))
    return sorted(out)


# ------------------------------------------------------------------------------------------------------------------------
# selftest: synthetic rows (2030-2031), no ICE content, no network
# ------------------------------------------------------------------------------------------------------------------------
class Checks:
    def __init__(self):
        self.items = []

    def ok(self, name, cond, detail=""):
        self.items.append((name, bool(cond), "" if cond else detail))

    def eq(self, name, got, want):
        self.ok(name, got == want, "got %r, want %r" % (got, want))

    def value(self, name, fn, want):
        """fn() must return `want`; an exception is recorded as a failure instead of ending the suite."""
        try:
            got = fn()
        except Exception as e:
            self.ok(name, False, "raised %s: %s" % (type(e).__name__, e))
        else:
            self.eq(name, got, want)

    def raises(self, name, exc, fn, contains=None):
        try:
            fn()
        except exc as e:
            self.ok(name, contains is None or contains in str(e), "raised %s without %r: %s" % (type(e).__name__, contains, e))
        except Exception as e:
            self.ok(name, False, "raised %s: %s" % (type(e).__name__, e))
        else:
            self.ok(name, False, "did not raise")

    def failed(self):
        return [(n, d) for n, c, d in self.items if not c]


FX_HEAD = ["Market_and_Exchange_Names", "As_of_Date_In_Form_YYMMDD", "As_of_Date_Form_MM/DD/YYYY", "CFTC_Contract_Market_Code", "CFTC_Commodity_Code",
           "Open_Interest_All", "Prod_Merc_Positions_Long_All", "Prod_Merc_Positions_Short_All", "Swap_Positions_Long_All", "{SS}", "{SP}",
           "M_Money_Positions_Long_All", "M_Money_Positions_Short_All", "M_Money_Positions_Spread_All", "Other_Rept_Positions_Long_All",
           "Other_Rept_Positions_Short_All", "Other_Rept_Positions_Spread_All", "Tot_Rept_Positions_Long_All", "Tot_Rept_Positions_Short_All",
           "Change_in_Open_Interest_All", "NonRept_Positions_Long_All", "NonRept_Positions_Short_All", "Pct_of_OI_M_Money_Long_All",
           "Pct_of_OI_M_Money_Short_All", "Pct_of_OI_Prod_Merc_Long_All", "Pct_of_OI_Prod_Merc_Short_All", "Pct_of_OI_Swap_Long_All",
           "Pct_of_OI_Swap_Short_All", "Pct_of_OI_Other_Rept_Long_All", "Pct_of_OI_Other_Rept_Short_All", "Pct_of_OI_NonRept_Long_All",
           "Pct_of_OI_NonRept_Short_All", "Contract_Units", "FutOnly_or_Combined"]
FX_NAME_FO = "ICE Brent Crude Futures - ICE Futures Europe"
FX_NAME_CO = "ICE Brent Crude Futures and Options - ICE Futures Europe"


def fx_classes(i, t):
    """Synthetic class figures for week i. Gross values are not multiples of 1000 (so no barrel figure can equal one); the nets are small.
    The five classes differ in size by tens of percent of open interest, so that two of them exchanged is far above ICE's 0.05pp rounding."""
    base = 100_003 + 3_701 * i + (50_000 if t == "combined" else 0)
    wig = lambda a, m: (i * a + 13) % m - m // 2         # irregular but deterministic: constant weekly changes would have zero variance
    # nets of a few percent of open interest, so that the rounded share (0.1pp) differs from one window end to the other
    nets = {"pm": -(15000 + 110 * i) + wig(104729, 530), "sw": 7000 + 50 * i + wig(7727, 310), "mm": 26000 + 130 * i + wig(7919, 970) - (3000 if t == "combined" else 0),
            "ot": -(4000 + 30 * i) + wig(6571, 410)}
    nets["nr"] = -sum(nets.values())
    longs = {"pm": base + 101, "sw": base // 2 + 203, "mm": base * 3 // 4 + 307 + 17 * i, "ot": base // 3 + 409, "nr": base // 4 + 55 * i + 11}
    spreads = {"sw": 90_001 + i, "mm": 110_003 + 2 * i, "ot": 70_007 + 3 * i}
    shorts = {k: longs[k] - nets[k] for k in longs}
    oi = sum(longs.values()) + sum(spreads.values())
    return longs, shorts, spreads, oi


def fx_pct(x):
    s = "%.1f" % round(x, 1)
    return s[:-2] if s.endswith(".0") else s


def fx_header(swap="Swap_", unnamed_tail=False):
    head = [h.replace("{SS}", swap + "Positions_Short_All").replace("{SP}", swap + "Positions_Spread_All") for h in FX_HEAD]
    return head + [""] if unnamed_tail else head


# logical key -> the canonical header of its level column (the Swap__ spelling is folded to Swap_ by canon())
FX_LEVEL_COL = {"oi": "Open_Interest_All", "pm_long": "Prod_Merc_Positions_Long_All", "pm_short": "Prod_Merc_Positions_Short_All",
                "sw_long": "Swap_Positions_Long_All", "sw_short": "Swap_Positions_Short_All", "sw_spread": "Swap_Positions_Spread_All",
                "mm_long": "M_Money_Positions_Long_All", "mm_short": "M_Money_Positions_Short_All", "mm_spread": "M_Money_Positions_Spread_All",
                "ot_long": "Other_Rept_Positions_Long_All", "ot_short": "Other_Rept_Positions_Short_All", "ot_spread": "Other_Rept_Positions_Spread_All",
                "nr_long": "NonRept_Positions_Long_All", "nr_short": "NonRept_Positions_Short_All"}


def fx_csv(year, dates, swap="Swap_", bom=False, same_name=False, unnamed_tail=False, blank_totals=True, noise=None, units="(CONTRACTS OF 1,000 BARRELS)",
           blank_class=None, bad_pct=False, extra_rows=(), first=0, drop_kind=None, swap_cells=None, full_pct=False, blank_pct=()):
    """A synthetic COTHist-shaped CSV (bytes) and the set of its gross figures (for the leak scan). `dates` is a list of datetime.date and
    week i of the fixture is first + position. noise = {(i, type): (d_long, d_short)} adds rounding noise to non-reportable on that row.
    swap_cells = (a, b) writes class cell a's value in cell b's column and the reverse (e.g. ("pm_long", "sw_long")), while ICE's percentage columns
    keep the true values, as ICE's would. The managed-money percentages are blank on some rows (as ICE's sometimes are) unless full_pct;
    blank_pct names pairs (e.g. "nr_long") whose percentage is blank on every row."""
    head = fx_header(swap, unnamed_tail)
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\r\n")
    w.writerow(head)
    gross = set()
    for i, d in enumerate(dates, start=first):
        for t in KINDS:
            if drop_kind == (i, t):
                continue
            longs, shorts, spreads, oi = fx_classes(i, t)
            dl, ds = (noise or {}).get((i, t), (0, 0))
            rep_l = sum(longs[k] for k in ("pm", "sw", "mm", "ot")) + sum(spreads.values())
            rep_s = sum(shorts[k] for k in ("pm", "sw", "mm", "ot")) + sum(spreads.values())
            longs, shorts = dict(longs), dict(shorts)
            longs["nr"] += dl
            shorts["nr"] += ds
            name = FX_NAME_FO if (t == "fo" or same_name) else FX_NAME_CO
            true = {"oi": oi}
            for k in CK:
                true[k + "_long"], true[k + "_short"] = longs[k], shorts[k]
            for k in SPREAD_CLASSES:
                true[k + "_spread"] = spreads[k]
            written = dict(true)
            if swap_cells:
                a_, b_ = swap_cells
                written[a_], written[b_] = true[b_], true[a_]
            V = {"Market_and_Exchange_Names": name, "As_of_Date_In_Form_YYMMDD": d.strftime("%y%m%d"),
                 "As_of_Date_Form_MM/DD/YYYY": "%d/%d/%d" % (d.month, d.day, d.year) if i % 2 else d.strftime("%m/%d/%Y"),      # ICE mixes padded and unpadded dates
                 "CFTC_Commodity_Code": "B", "Tot_Rept_Positions_Long_All": "" if blank_totals else str(rep_l),
                 "Tot_Rept_Positions_Short_All": "" if blank_totals else str(rep_s), "Contract_Units": units,
                 "FutOnly_or_Combined": "FutOnly" if t == "fo" else "Combined"}
            for key, col in FX_LEVEL_COL.items():
                V[col] = str(written[key])
            for pair in PCT_PAIRS:
                col = "Pct_of_OI_%s_%s_All" % (PCT_NAMES[pair.split("_")[0]], pair.split("_")[1].capitalize())
                val = fx_pct(100.0 * true[pair] / oi)
                if pair in blank_pct:
                    val = ""
                elif pair == "mm_long":
                    val = "" if (i % 5 == 0 and not full_pct) else (fx_pct(100.0 * true[pair] / oi + 0.3) if (bad_pct and i == first + 1) else val)
                elif pair == "mm_short":
                    val = "" if (i % 7 == 0 and not full_pct) else val
                V[col] = val
            if blank_class == (i, t):
                V[FX_LEVEL_COL["mm_long"]] = ""
            cells = [V.get(canon(h), "") for h in head]
            gross.update(true.values())
            w.writerow(cells)
    for ex in extra_rows:
        w.writerow(ex)
    text = out.getvalue()
    if bom:
        text = "\ufeff" + text
    return text.encode("utf-8"), gross


def fx_decoy():
    """A non-Brent row that must be skipped."""
    row = [""] * len(FX_HEAD)
    row[0] = "ICE Gasoil Futures - ICE Futures Europe"
    row[1] = "301231"
    return row


def fx_tuesdays(year, first, n):
    d = dt.date(year, 1, 1)
    while d.weekday() != 1:
        d += dt.timedelta(days=1)
    d += dt.timedelta(days=7 * first)
    return [d + dt.timedelta(days=7 * k) for k in range(n)]


def fx_prices():
    ser = {}
    d = dt.date(2029, 12, 3)
    k = 0
    while d < dt.date(2031, 4, 1):
        if d.weekday() < 5 and d not in (dt.date(2030, 7, 2), dt.date(2031, 1, 27)):
            ser[d] = 70.0 + 8.0 * math.sin(k / 9.0) + 0.03 * k
            k += 1
        d += dt.timedelta(days=1)
    return ser


FX_2030 = fx_tuesdays(2030, 0, 53)                                  # 2030-01-01 .. 2030-12-31; the last one is ISO week 2031-W01
FX_2031 = [dt.date(2031, 1, 7) + dt.timedelta(days=7 * k) for k in range(12)]
FX_2031_MON = [dt.date(2031, 1, 27) if d == dt.date(2031, 1, 28) else d for d in FX_2031]    # one Monday report date


def fx_window_anchors():
    return (("since end-2030", dt.date(2030, 12, 31), dt.date(2030, 12, 31)),)


@contextlib.contextmanager
def allowed_column(name, col):
    """Selftest only: `col` is appended to the allowlist of output file `name` for the length of the block."""
    saved = ALLOW[name]
    ALLOW[name] = saved + [col]
    try:
        yield
    finally:
        ALLOW[name] = saved


def suite_pure(ck):
    # A9 year derivation
    fri, thu, fri8 = dt.date(2027, 1, 1), dt.date(2027, 1, 7), dt.date(2027, 1, 8)
    ck.eq("Fri 2027-01-01 derives report year 2026 (A9)", report_year(fri), 2026)
    ck.eq("Thu 2027-01-07 derives 2026", report_year(thu), 2026)
    ck.eq("Fri 2027-01-08 derives 2027", report_year(fri8), 2027)
    ck.eq("Thu 2026-10-15: latest expected Tuesday is 2026-10-06", latest_expected_tuesday(dt.date(2026, 10, 15)), dt.date(2026, 10, 6))
    ck.eq("Fri 2026-10-16: latest expected Tuesday is 2026-10-13", latest_expected_tuesday(dt.date(2026, 10, 16)), dt.date(2026, 10, 13))
    ck.eq("Tue 2026-10-13: latest expected Tuesday is 2026-10-06", latest_expected_tuesday(dt.date(2026, 10, 13)), dt.date(2026, 10, 6))
    # user agent, host allowlist, cache
    ck.raises("a User-Agent with an address is refused", Refused, lambda: assert_ua("Mozilla" + "/5.0 (x; nobody@example.com)"))
    ck.ok("the User-Agent is the canonical non-SEC string with no address", UA == "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)" and chr(64) not in UA)
    ck.eq("ICE url allowed", check_url("https://www.ice.com/publicdocs/futures/COTHist2012.csv"), (ICE_HOST, "/publicdocs/futures/COTHist2012.csv"))
    ck.eq("EIA url allowed", check_url("https://www.eia.gov/dnav/pet/hist_xls/RBRTEd.xls"), (EIA_HOST, EIA_PATH))
    for bad in ("https://www.sec.gov/Archives/x", "https://example.com/publicdocs/futures/COTHist2012.csv", "http://www.ice.com/publicdocs/futures/COTHist2012.csv",
                "https://www.ice.com/other/COTHist2012.csv", "https://www.ice.com/publicdocs/futures/COTHist2012.csv?x=1", "https://www.eia.gov/dnav/pet/hist_xls/RWTCd.xls",
                "https://ice.com/publicdocs/futures/COTHist2012.csv"):
        ck.raises("url outside the ruling is refused: %s" % bad[:60], Refused, lambda b=bad: check_url(b))
    ck.raises("a cache inside the repository is refused", Refused, lambda: check_cache(os.path.join(ROOT, "data", "ice_cache")))
    ck.raises("the repository root itself is refused as a cache", Refused, lambda: check_cache(ROOT))
    ck.ok("a cache outside the repository is accepted", check_cache(tempfile.gettempdir()) != "")
    ck.eq("the STOP latch is at the fixed path under ~/ice_cot", tilde(STOP_PATH), "~/ice_cot/STOP")
    # numbers
    ck.eq("f() rounds and avoids negative zero", (f(-0.00001, 3), f(2.0449, 3), f(None, 2)), ("0.000", "2.045", ""))
    ck.ok("pearson of a perfect line is 1", abs(pearson([1, 2, 3, 4], [2, 4, 6, 8]) - 1) < 1e-12)
    ck.eq("ranks average ties", ranks([10, 20, 20, 30]), [1.0, 2.5, 2.5, 4.0])
    ck.eq("ISO key of 2030-12-31 is 2031-W01 and of 2031-01-07 is 2031-W02", (iso_key(dt.date(2030, 12, 31)), iso_key(dt.date(2031, 1, 7))), ((2031, 1), (2031, 2)))
    ck.eq("week_index is consecutive across the new year", week_index(dt.date(2031, 1, 7)) - week_index(dt.date(2030, 12, 31)), 1)
    # header test
    ok_hdr = [h.replace("{SS}", "Swap_Positions_Short_All").replace("{SP}", "Swap_Positions_Spread_All") for h in FX_HEAD]
    ck.value("a header with the Swap_ spelling passes", lambda: parse_header(ok_hdr)[0]["sw_short"], 9)
    alt = [h.replace("Swap_Positions_Short_All", "Swap__Positions_Short_All").replace("Swap_Positions_Spread_All", "Swap__Positions_Spread_All") for h in ok_hdr]
    ck.value("a header with the Swap__ spelling passes", lambda: parse_header(alt)[1]["spelling"], "Swap__")
    ck.value("a BOM on the first header cell is stripped", lambda: parse_header(["\ufeff" + ok_hdr[0]] + ok_hdr[1:])[0]["name"], 0)
    ck.raises("a first column that is not Market_and_Exchange_Names fails the header test", HeaderError, lambda: parse_header(["x"] + ok_hdr[1:]))
    ck.raises("a missing required column fails the header test", HeaderError, lambda: parse_header([h for h in ok_hdr if h != "Open_Interest_All"]))
    ck.value("an unnamed trailing column is ignored and logged", lambda: parse_header(ok_hdr + [""])[1]["unnamed"], [len(ok_hdr)])
    ck.ok("ice_csv_problem accepts a header-only CSV", ice_csv_problem((",".join(ok_hdr) + "\r\n").encode()) is None)
    ck.ok("ice_csv_problem rejects HTML", ice_csv_problem(b"<html>blocked</html>") is not None)
    # written text: source line, allowlist, percent precision
    good = render_table(WINDOWS_COLS, [["brent", "fo", "4 weeks", "4", "2030-01-01", "2030-01-29", "1", "2", "1", "1000", "1.5", "2.5"]], SOURCE_ICE)
    ck.eq("a conforming windows file verifies", verify_text("brent_windows.csv", good)[0], WINDOWS_COLS)
    ck.raises("a percent column with two decimals is a hard failure", DataError, lambda: verify_text("brent_windows.csv", good.replace("1.5,2.5", "1.55,2.5")), "decimal")
    ck.raises("a percent column with no decimal is a hard failure", DataError, lambda: verify_text("brent_windows.csv", good.replace("1.5,2.5", "2,2.5")), "decimal")
    ck.raises("a gross-long column written to an output is refused", DataError, lambda: verify_text("brent_windows.csv", good.replace("mm_net_from", "fo_mm_long")), "allowlist")
    ck.raises("an extra column is refused", DataError, lambda: verify_text("brent_windows.csv", good.replace("mm_net_to", "mm_net_to,extra")), "allowlist")
    ck.raises("a missing source line is refused", DataError, lambda: verify_text("brent_windows.csv", good.split("\n", 1)[1]), "source")
    ck.ok("no allowlisted header carries a banned gross name", all(not BANNED_HDR.search(h) for cols in ALLOW.values() for h in cols))
    ck.ok("the banned-name pattern catches long, short, spread, open_interest and bare oi",
          all(BANNED_HDR.search(h) for h in ("fo_mm_long", "co_sw_short", "mm_spread", "open_interest_all", "fo_oi", "gross_x")) and not BANNED_HDR.search("fo_mm_net_pct_oi"))
    ck.ok("every allowlisted column whose name contains 'pct' or ends '_pp' is on the percent-precision list or is a lead-lag correlation coefficient",
          all(h in PERCENT_COLS.get(n, []) or h in PCT_EXEMPT.get(n, []) for n, cols in ALLOW.items() for h in cols if looks_percent(h)))
    ck.eq("the exempt list is the six lead-lag correlation columns and nothing else", PCT_EXEMPT,
          {"brent_leadlag.csv": ["pearson_same_pct", "spearman_same_pct", "pearson_next_pct", "spearman_next_pct", "pearson_prev_pct", "spearman_prev_pct"]})
    ck.eq("looks_percent recognises 'pct' anywhere and a '_pp' ending",
          [looks_percent(h) for h in ("x_pct", "pct_x", "fo_mm_net_pct_oi", "agree_max_dev_pp", "gap_pp", "pp_gap", "fo_mm_net", "price_flag")],
          [True, True, True, True, True, False, False, False])
    ck.ok("brent_file_stats.csv no longer carries a percentage-point column", not any(looks_percent(h) for h in FILE_STATS_COLS))
    # a percent-like column added to an allowlist is held to the precision rule too (agree_max_dev_pp was written at 3 decimals before it was removed)
    wrows = [["brent", "fo", "4 weeks", "4", "2030-01-01", "2030-01-29", "1", "2", "1", "1000", "1.5", "2.5"]]
    for extra in ("agree_max_dev_pp", "mm_gap_pp", "x_pct"):
        with allowed_column("brent_windows.csv", extra):
            txt = render_table(WINDOWS_COLS + [extra], [r + ["0.123"] for r in wrows], SOURCE_ICE)
            ck.raises("a new column %s at 3 decimals is a hard failure" % extra, DataError, lambda: verify_text("brent_windows.csv", txt), "percent")
    with allowed_column("brent_windows.csv", "other_note"):
        txt = render_table(WINDOWS_COLS + ["other_note"], [r + ["0.123"] for r in wrows], SOURCE_ICE)
        ck.eq("a new column that does not look like a percent is not held to it", verify_text("brent_windows.csv", txt)[0][-1], "other_note")
    led_row = ["2030-01-01"] + [""] * (len(LEDGER_COLS) - 1)
    ck.eq("a ledger with an empty price_flag verifies", verify_text("brent_ledger.csv", render_table(LEDGER_COLS, [led_row], SOURCE_ICE))[0], LEDGER_COLS)
    led_flag = list(led_row)
    led_flag[LEDGER_COLS.index("price_flag")] = PRICE_FLAG
    ck.eq("a ledger with price_flag eia_spot_gap_unverified verifies", verify_text("brent_ledger.csv", render_table(LEDGER_COLS, [led_flag], SOURCE_ICE))[0], LEDGER_COLS)
    led_bad = list(led_row)
    led_bad[LEDGER_COLS.index("price_flag")] = "fine"
    ck.raises("a price_flag value other than '' and eia_spot_gap_unverified is refused", DataError, lambda: verify_text("brent_ledger.csv", render_table(LEDGER_COLS, [led_bad], SOURCE_ICE)), "price_flag")
    ck.eq("price_flag is the column after usd_basis", LEDGER_COLS[LEDGER_COLS.index("usd_basis") + 1], "price_flag")
    # known-bad EIA prints
    ck.eq("KNOWN_SUSPECT_PRINTS covers 2026-10-02 to 2026-10-21 and nothing around it",
          [is_suspect_print(dt.date(2026, 10, k)) for k in (1, 2, 9, 21, 22)], [False, True, True, True, False])
    # EIA workbook that will not load: an xlrd error becomes the script's DataError
    with tempfile.TemporaryDirectory() as tmp:
        for label, body in (("XLS magic bytes then garbage", XLS_MAGIC + b"\xa1\xb1\x1a\xe1" + b"x" * 64), ("an empty file", b""), ("HTML", b"<html>x</html>")):
            pth = os.path.join(tmp, "x.xls")
            open(pth, "wb").write(body)
            ck.raises("load_eia_brent maps xlrd's error on %s to DataError" % label, DataError, lambda: load_eia_brent(pth), "cannot be read")
        ck.raises("load_eia_brent maps a missing file to DataError", DataError, lambda: load_eia_brent(os.path.join(tmp, "absent.xls")), "cannot be read")
    # pacing constants
    ck.ok("the spacing floor is 5.05 s", MIN_SLEEP == 5.05)


def fx_build(tmp, a2030=None, a2031=None, **kw):
    """Write a synthetic cache (2030 and 2031), a log, and build into tmp/out. Returns (ctx, cache, out, gross)."""
    cache, out = os.path.join(tmp, "cache"), os.path.join(tmp, "out")
    os.makedirs(cache, exist_ok=True)
    b30, g30 = a2030 or fx_csv(2030, FX_2030, same_name=True, bom=True, swap="Swap__")
    b31, g31 = a2031 or fx_csv(2031, FX_2031_MON, first=len(FX_2030), swap="Swap_", unnamed_tail=True,
                               extra_rows=[fx_decoy()])
    rows = []
    for y, b in ((2030, b30), (2031, b31)):
        open(os.path.join(cache, "COTHist%d.csv" % y), "wb").write(b)
        rows.append(["2031-03-28T10:00:00.000Z", ICE_HOST, ice_path(y), "200", "saved", str(len(b)), sha256_of(b)])
    write_text(log_path(out), render_table(FETCH_LOG_COLS, rows, SOURCE_LOG))
    ctx = build(cache, out, prices=fx_prices(), eia_date="2031-03-27", pins=kw.pop("pins", ()), anchors=fx_window_anchors(), kemp=False, say=lambda *a: None, **kw)
    return ctx, cache, out, g30 | g31


def suite_parse(ck):
    # A: a clean synthetic file, ICE-shaped (blank totals, BOM, Swap__, same-name rows in both types, an unnamed tail, a decoy row)
    raw, gross = fx_csv(2030, FX_2030, same_name=True, bom=True, swap="Swap__", unnamed_tail=True, extra_rows=[fx_decoy()])
    try:
        fr = parse_file(raw, 2030)
        ck.ok("a BOM file with Swap__ spellings, blank totals and same-name rows parses", True)
    except Exception as e:
        ck.ok("a BOM file with Swap__ spellings, blank totals and same-name rows parses", False, "%s: %s" % (type(e).__name__, e))
        fr = None
    if fr is not None:
        ck.eq("2011-style same-name rows split by FutOnly_or_Combined, not by name", (fr.st["rows"]["fo"], fr.st["rows"]["combined"]), (53, 53))
        ck.eq("the non-Brent decoy row is skipped", sum(fr.st["rows"].values()), 106)
        ck.eq("every row's units were checked", fr.st["units"], 106)
        i = 7
        lg, sh, sp, oi = fx_classes(i, "fo")
        rec = [r for r in fr.recs if r["type"] == "fo" and r["date"] == FX_2030[i]][0]
        ck.eq("managed-money net is long minus short, spreading excluded", rec["nets"]["mm"], lg["mm"] - sh["mm"])
        ck.eq("the five nets sum to zero in the futures-only fixture", sum(rec["nets"].values()), 0)
        ck.ok("the record carries nets only", set(rec) == {"date", "type", "nets", "pct_oi"})
        ck.eq("unnamed trailing column is recorded", fr.info["unnamed"], [len(FX_HEAD)])
        want_n = {p: 106 for p in PCT_PAIRS}
        want_n["mm_long"], want_n["mm_short"] = 2 * sum(1 for i in range(53) if i % 5), 2 * sum(1 for i in range(53) if i % 7)     # blank on some rows, as ICE's sometimes are
        ck.eq("ICE's percentages are checked for all ten class/side pairs, blank cells skipped", dict(fr.st["agree_n"]), want_n)
    # B: Monday report dates are accepted (and recorded), a Tuesday-only assumption is not made
    mon = list(FX_2030)
    mon[10] = mon[10] - dt.timedelta(days=1)
    try:
        fm = parse_file(fx_csv(2030, mon)[0], 2030)
        ck.eq("a Monday report date parses and is recorded", fm.st["non_tue"].count(mon[10]), 2)
    except Exception as e:
        ck.ok("a Monday report date parses and is recorded", False, "%s: %s" % (type(e).__name__, e))
    # C: each hard check
    ck.raises("futures-only identity off by 1 (one side) stops the build", DataError, lambda: parse_file(fx_csv(2030, FX_2030, noise={(3, "fo"): (1, 0)})[0], 2030), "differ from open interest")
    ck.raises("futures-only identity off by 1 (net sum) stops the build", DataError, lambda: parse_file(fx_csv(2030, FX_2030, noise={(3, "fo"): (0, -1)})[0], 2030))
    try:
        parse_file(fx_csv(2030, FX_2030, noise={(3, "combined"): (3, -2), (4, "combined"): (-4, 4)})[0], 2030)
        ck.ok("combined rounding noise within 4 per side and 8 on the net sum passes", True)
    except Exception as e:
        ck.ok("combined rounding noise within 4 per side and 8 on the net sum passes", False, str(e))
    ck.raises("combined off by 5 on a side stops the build", DataError, lambda: parse_file(fx_csv(2030, FX_2030, noise={(3, "combined"): (5, 0)})[0], 2030))
    ck.raises("combined off by 5 on the short side stops the build", DataError, lambda: parse_file(fx_csv(2030, FX_2030, noise={(3, "combined"): (0, -5)})[0], 2030))
    ck.raises("a missing Contract_Units match stops the build", DataError, lambda: parse_file(fx_csv(2030, FX_2030, units="(CONTRACTS OF 100 TONNES)")[0], 2030), "Contract_Units")
    ck.raises("a blank class figure stops the build", DataError, lambda: parse_file(fx_csv(2030, FX_2030, blank_class=(2, "fo"))[0], 2030), "blank class figure")
    ck.raises("ICE's own percentage disagreeing with level / OI stops the build", DataError, lambda: parse_file(fx_csv(2030, FX_2030, bad_pct=True)[0], 2030), "percentage")
    # C2: the column mapping. Two classes exchanged on the SAME side leave both identities untouched; ICE's own percentage columns see it.
    clean = parse_file(fx_csv(2030, FX_2030)[0], 2030)
    for a_, b_ in (("pm_long", "sw_long"), ("ot_short", "nr_short"), ("mm_long", "ot_long"), ("sw_short", "pm_short")):
        raw_sw = fx_csv(2030, FX_2030, swap_cells=(a_, b_))[0]
        ck.raises("%s and %s exchanged (same side) are stopped by the percentage check" % (a_, b_), DataError, lambda: parse_file(raw_sw, 2030), "percentage")
        with mutant("pct_agree"):
            try:
                parse_file(raw_sw, 2030)
                ck.ok("%s and %s exchanged: the identities alone do not see it (percentage check off)" % (a_, b_), True)
            except Exception as e:
                ck.ok("%s and %s exchanged: the identities alone do not see it (percentage check off)" % (a_, b_), False, "%s: %s" % (type(e).__name__, e))
    with mutant("pct_agree"):
        ck.raises("pm_long and sw_short exchanged (different sides) are stopped by the identities alone", DataError,
                  lambda: parse_file(fx_csv(2030, FX_2030, swap_cells=("pm_long", "sw_short"))[0], 2030), "differ from open interest")
    try:
        sp_swapped = parse_file(fx_csv(2030, FX_2030, swap_cells=("sw_spread", "mm_spread"))[0], 2030)
        ck.ok("two spreading columns exchanged: nothing notices, and no net changes, so no published figure does", [r["nets"] for r in sp_swapped.recs] == [r["nets"] for r in clean.recs])
    except Exception as e:
        ck.ok("two spreading columns exchanged: nothing notices, and no net changes, so no published figure does", False, "%s: %s" % (type(e).__name__, e))
    try:
        parse_file(fx_csv(2030, FX_2030, blank_totals=False)[0], 2030)
        ck.ok("filled totals that agree with the classes pass", True)
    except Exception as e:
        ck.ok("filled totals that agree with the classes pass", False, str(e))
    ck.raises("a report date outside the file's year stops the build", DataError, lambda: parse_file(fx_csv(2030, FX_2030)[0], 2031), "not in the file's year")
    # D: assembly across files
    two = fx_csv(2030, FX_2030)[0]
    extra_date = FX_2030[5] - dt.timedelta(days=1)       # a second fo report in the same ISO week
    row = list(csv.reader(io.StringIO(two.decode())))[1 + 5 * 2]
    row = list(row)
    row[1] = extra_date.strftime("%y%m%d")
    row[2] = extra_date.strftime("%m/%d/%Y")
    dup_raw = fx_csv(2030, FX_2030, extra_rows=[row])[0]
    ck.raises("a duplicate week is refused", DataError, lambda: assemble([parse_file(dup_raw, 2030), parse_file(fx_csv(2031, FX_2031, first=53)[0], 2031)]), "duplicate")
    f30, f31 = parse_file(fx_csv(2030, FX_2030)[0], 2030), parse_file(fx_csv(2031, FX_2031_MON, first=53)[0], 2031)
    try:
        dates, by = assemble([f30, f31])
        ck.eq("two files assemble: one report per ISO week, 53 + 12 weeks", len(dates), 65)
    except Exception as e:
        ck.ok("two files assemble: one report per ISO week, 53 + 12 weeks", False, "%s: %s" % (type(e).__name__, e))
    gap = [d for k, d in enumerate(FX_2031) if k != 3]
    ck.raises("a missing week inside a year is refused", DataError, lambda: assemble([f30, parse_file(fx_csv(2031, gap, first=53)[0], 2031)]), "missing or doubled")
    late = [d + dt.timedelta(days=21) for d in FX_2031]
    ck.raises("a seam of 28 days between year files is refused", DataError, lambda: assemble([f30, parse_file(fx_csv(2031, late, first=53)[0], 2031)]), "seam")
    ck.raises("a missing year file is refused", DataError, lambda: assemble([f30, parse_file(fx_csv(2032, [dt.date(2032, 1, 6)], first=53)[0], 2032)]), "unbroken")
    ck.raises("futures-only and combined must share their dates", DataError,
              lambda: assemble([f30, parse_file(fx_csv(2031, FX_2031, first=53, drop_kind=(64, "combined"))[0], 2031)]), "share the same report dates")
    # E: prices
    s = {dt.date(2030, 1, 2): 70.0}
    ck.eq("a price is carried back from the last earlier quote", attach_prices([dt.date(2030, 1, 4)], s)[dt.date(2030, 1, 4)], (70.0, dt.date(2030, 1, 2), 2))
    ck.raises("a price older than 5 days is refused", DataError, lambda: attach_prices([dt.date(2030, 1, 9)], s), "days old")
    ck.raises("a report date before the first price is refused", DataError, lambda: attach_prices([dt.date(2030, 1, 1)], s), "no Brent price")


def suite_mapping(ck):
    """The parser's column mapping on a clean fixture. Run once as it is, and once per mapping mutant (two class columns exchanged inside
    the parser, see MAP_MUTANTS); a mutant must make a check here fail."""
    try:
        fr = parse_file(fx_csv(2030, FX_2030)[0], 2030)
    except Exception as e:
        ck.ok("a clean fixture parses with the true column mapping", False, "%s: %s" % (type(e).__name__, e))
        return
    ck.ok("a clean fixture parses with the true column mapping", True)
    wrong = []
    for r in fr.recs:
        lg, sh, sp, oi = fx_classes(FX_2030.index(r["date"]), r["type"])
        if r["nets"] != {k: lg[k] - sh[k] for k in CK}:
            wrong.append((r["type"], r["date"]))
    ck.eq("on every row each of the five class nets is the fixture's long minus short", wrong, [])


def suite_build(ck):
    with tempfile.TemporaryDirectory() as tmp:
        try:
            ctx, cache, out, gross = fx_build(tmp)
        except Exception as e:
            ck.ok("a synthetic cache builds end to end", False, "%s: %s" % (type(e).__name__, e))
            return
        ck.ok("a synthetic cache builds end to end", True)
        names = sorted(ALLOW)
        names.remove("fetch_log.csv")
        first = {n: open(os.path.join(out, n), "rb").read() for n in names}
        ctx2 = build(cache, out, prices=fx_prices(), eia_date="2031-03-27", pins=(), anchors=fx_window_anchors(), kemp=False, say=lambda *a: None)
        ck.ok("a second build is byte-identical for every output", all(open(os.path.join(out, n), "rb").read() == first[n] for n in names))
        ck.ok("every output starts with the `# source:` line naming ICE and E-025",
              all(first[n].decode().startswith(SOURCE_ICE) for n in names))
        ck.ok("the source line carries the ICE and EIA retrieval dates from the log", b"files retrieved 2031-03-28; EIA Europe Brent spot price (eia.gov, US government, public domain) retrieved 2031-03-27" in first["brent_ledger.csv"])
        leak = []
        for n in names:
            for ln in first[n].decode().splitlines()[2:]:
                for cell in next(csv.reader([ln])):
                    if cell.isdigit() and int(cell) in gross:
                        leak.append((n, cell))
        ck.eq("no output field equals any gross figure of the fixture", leak, [])
        hdr = {n: next(csv.reader([first[n].decode().splitlines()[1]])) for n in names}
        ck.ok("every output header equals its allowlist", all(hdr[n] == ALLOW[n] for n in names))
        ck.ok("no output header carries a banned gross name", all(not BANNED_HDR.search(h) for n in names for h in hdr[n]))
        # numbers
        rd = {r[0]: dict(zip(LEDGER_COLS, r)) for r in read_table(os.path.join(out, "brent_ledger.csv"), LEDGER_COLS)}
        d = FX_2030[20]
        lg, sh, sp, oi = fx_classes(20, "fo")
        r = rd[d.isoformat()]
        ck.eq("ledger fo_mm_net equals the fixture's long minus short", int(r["fo_mm_net"]), lg["mm"] - sh["mm"])
        ck.eq("ledger fo_mm_net_bbl is 1,000 barrels per contract", int(r["fo_mm_net_bbl"]), (lg["mm"] - sh["mm"]) * 1000)
        ck.eq("every class net is also published in barrels", [int(r["fo_%s_net_bbl" % k]) // 1000 for k in CK], [int(r["fo_%s_net" % k]) for k in CK])
        ck.eq("resid_net is 0 for futures only", r["fo_resid_net"], "0")
        ck.eq("mm_net_pct_oi is to 0.1pp", r["fo_mm_net_pct_oi"], f(100.0 * (lg["mm"] - sh["mm"]) / oi, 1))
        p = fx_prices()[d]
        ck.eq("dollars are net x 1,000 bbl x price", r["fo_mm_net_usd_bn"], f((lg["mm"] - sh["mm"]) * 1000 * p / 1e9, 6))
        ck.eq("the price is written to four decimals", r["price_usd_per_bbl"], f(p, 4))
        ck.ok("every ledger price has exactly four decimals", all(re.fullmatch(r"[0-9]+\.[0-9]{4}", x["price_usd_per_bbl"]) for x in rd.values()))
        ck.ok("price_flag is empty on every row when no known-bad print is in the data", all(x["price_flag"] == "" for x in rd.values()))
        ck.eq("the first row has no change", rd[FX_2030[0].isoformat()]["fo_mm_net_chg"], "")
        prev = rd[FX_2030[19].isoformat()]
        ck.eq("a change is this week's net minus last week's", int(r["fo_mm_net_chg"]), int(r["fo_mm_net"]) - int(prev["fo_mm_net"]))
        ck.eq("a price lag appears where a quote is missing (2030-07-02)", rd["2030-07-02"]["price_lag_days"], "1")
        ck.eq("the Monday report date is carried back to the last quote (2031-01-27)", rd["2031-01-27"]["price_lag_days"], "3")
        ck.ok("usd_basis names the EIA spot and not ICE settlement", rd[d.isoformat()]["usd_basis"] == USD_BASIS)
        w = read_table(os.path.join(out, "brent_windows.csv"), WINDOWS_COLS)
        ck.eq("windows: 4, 12, 52 weeks and the anchor, for two report types", [(x[1], x[2]) for x in w],
              [(t, lab) for t in KINDS for lab in ("4 weeks", "12 weeks", "52 weeks", "since end-2030")])
        w4 = [x for x in w if x[1] == "fo" and x[2] == "4 weeks"][0]
        ds = sorted(rd)
        ck.eq("a 4-week window changes the net by last week's net minus the net four reports back", int(w4[8]), int(rd[ds[-1]]["fo_mm_net"]) - int(rd[ds[-5]]["fo_mm_net"]))
        ck.eq("a 4-week window runs from the report four back to the last", (w4[3], w4[4], w4[5]), ("4", ds[-5], ds[-1]))
        ck.eq("window barrels are 1,000 per contract", int(w4[9]), 1000 * int(w4[8]))
        # every window row against the ledger it came from: its length, its two dates, the two nets and shares at those dates, and the change
        # (an 11-week "12 weeks", a from and a to exchanged, a share taken from the wrong end all fail here)
        want_weeks = {"4 weeks": 4, "12 weeks": 12, "52 weeks": 52, "since end-2030": len(ds) - 1 - ds.index("2030-12-31")}
        for x in w:
            wr, pre = dict(zip(WINDOWS_COLS, x)), ("fo_" if x[1] == "fo" else "co_")
            n_w = want_weeks[wr["window"]]
            frm, to = ds[-1 - n_w], ds[-1]
            ck.eq("window %s / %s: weeks, dates, nets, shares and change come from the ledger at %s and %s" % (wr["report_type"], wr["window"], frm, to),
                  (wr["weeks"], wr["from_date"], wr["to_date"], wr["mm_net_from"], wr["mm_net_to"], int(wr["mm_net_chg"]), int(wr["mm_net_chg_bbl"]),
                   wr["mm_net_pct_oi_from"], wr["mm_net_pct_oi_to"]),
                  (str(n_w), frm, to, rd[frm][pre + "mm_net"], rd[to][pre + "mm_net"], int(rd[to][pre + "mm_net"]) - int(rd[frm][pre + "mm_net"]),
                   1000 * (int(rd[to][pre + "mm_net"]) - int(rd[frm][pre + "mm_net"])), rd[frm][pre + "mm_net_pct_oi"], rd[to][pre + "mm_net_pct_oi"]))
        ck.ok("the fixture's two window ends have different shares at 0.1pp in most windows, so that a swapped pair shows", sum(1 for x in w if x[10] != x[11]) >= 6)
        ll = read_table(os.path.join(out, "brent_leadlag.csv"), LEADLAG_COLS)
        ck.eq("lead-lag has one row per report type with n_same one more than n_next", [(x[1], int(x[4]) - int(x[9])) for x in ll], [("fo", 1), ("combined", 1)])
        ck.eq("lead-lag first_week is the first report date from 2024-01-01 (needing a prior week)", ll[0][2], FX_2030[1].isoformat())
        # the lead-lag numbers against an independent recomputation from the build's inputs: the same / next / prev shifts, the three correlations, n and
        # the 5% band 1.96/sqrt(n), written here with the literal 1.96 (a shift swapped, or a band of 1.64, fails here)
        def corr(xs, ys):
            n_, mx, my = len(xs), sum(xs) / len(xs), sum(ys) / len(ys)
            return sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))

        def rnk(v):
            return [1 + sum(1 for u in v if u < a) + (sum(1 for u in v if u == a) - 1) / 2.0 for a in v]
        Pn, Dn = ctx["P"], ctx["dates"]
        ck.eq("lead-lag n_same, n_next, n_prev on the 65-week fixture", [(int(x[4]), int(x[9]), int(x[14])) for x in ll], [(64, 63, 63)] * 2)
        for kind, lrow in zip(KINDS, ll):
            L, Nm, want, got = dict(zip(LEADLAG_COLS, lrow)), ctx["mm"][kind], {}, {}
            for tag, sh in (("same", 0), ("next", 1), ("prev", -1)):
                tt = [t for t in range(1, len(Dn)) if 1 <= t + sh < len(Dn)]
                xs = [Nm[t] - Nm[t - 1] for t in tt]
                ys = [Pn[t + sh] / Pn[t + sh - 1] - 1 for t in tt]
                zs = [Pn[t + sh] - Pn[t + sh - 1] for t in tt]
                want[tag] = (len(tt), f(corr(xs, ys), 3), f(corr(rnk(xs), rnk(ys)), 3), f(corr(xs, zs), 3), f(1.96 / math.sqrt(len(tt)), 3))
                got[tag] = (int(L["n_" + tag]), L["pearson_%s_pct" % tag], L["spearman_%s_pct" % tag], L["pearson_%s_abs" % tag], L["band95_" + tag])
            ck.eq("lead-lag %s: n, Pearson, Spearman, absolute and 1.96/sqrt(n) band for same, next and prev equal an independent recomputation" % kind, got, want)
        fs = read_table(os.path.join(out, "brent_file_stats.csv"), FILE_STATS_COLS)
        ck.eq("file_stats has one row per year file", [x[0] for x in fs], ["2030", "2031"])
        ck.eq("file_stats logs the spelling and the unnamed column", (fs[0][7], fs[1][7], fs[1][8]), ("Swap__", "Swap_", str(len(FX_HEAD) + 1)))
        ck.eq("file_stats logs a Monday date", fs[1][18], "2031-01-27")
        chk = read_table(os.path.join(out, "checks.csv"), CHECKS_COLS)
        ck.ok("checks.csv records no FAIL", all(x[4] != "FAIL" for x in chk), str([x for x in chk if x[4] == "FAIL"]))
        ck.ok("a Monday that is not in the known list is a WARN, not a stop", any(x[0] == "K06" and x[4] == "WARN" for x in chk))
        # pinned check: a wrong value warns and does not stop; a right one passes
        c3 = build(cache, out, prices=fx_prices(), eia_date="2031-03-27", pins=((FX_2030[20], "fo", 1), (FX_2030[20], "combined", int(r["co_mm_net"]))),
                   anchors=fx_window_anchors(), kemp=False, say=lambda *a: None, write=False)
        st = {x[0]: x[4] for x in c3["chk"]}
        ck.eq("a pinned value that disagrees is a WARN and does not stop the build", (st["K08"], st["K09"]), ("WARN", "PASS"))
        ck.ok("the WARN carries the restatement hint", "ICE may have restated" in [x for x in c3["chk"] if x[0] == "K08"][0][5])
        # price_flag: report dates whose PRICE date (not the report date) is in a known-bad range, the USD figures untouched
        c4 = build(cache, out, prices=fx_prices(), eia_date="2031-03-27", pins=(), anchors=fx_window_anchors(), kemp=False, say=lambda *a: None, write=False,
                   suspect=((dt.date(2030, 7, 1), dt.date(2030, 7, 1)), (FX_2030[20], FX_2030[20])))
        led4 = {x[0]: dict(zip(LEDGER_COLS, x)) for x in c4["led"]}
        ck.eq("price_flag marks the report dates whose price date is in a known-bad range, a carried-back quote included",
              sorted(k_ for k_, x in led4.items() if x["price_flag"]), sorted(["2030-07-02", FX_2030[20].isoformat()]))
        ck.eq("...with the value eia_spot_gap_unverified", {x["price_flag"] for x in led4.values()} - {""}, {PRICE_FLAG})
        ck.ok("...and nothing else in any row changes (the USD figures stay as computed)",
              all({a: b for a, b in led4[k_].items() if a != "price_flag"} == {a: b for a, b in rd[k_].items() if a != "price_flag"} for k_ in rd))
        ck.eq("the build counts the flagged report dates", c4["n_flagged"], 2)
        # K03 (all ten percentage pairs), K15 and K16 report what was observed
        kk = {x[0]: x for x in chk}
        n_rows = 130
        ck.eq("K03 names the ten pairs", [e.split(" n=")[0] for e in kk["K03"][3].split("; ")], list(PCT_PAIRS))
        ck.eq("K03 warns, and says which pairs fall short, when percentages are blank (the fixture's managed-money ones are, on some rows)",
              (kk["K03"][4], "mm_long %d of %d" % (2 * sum(1 for i in range(65) if i % 5), n_rows) in kk["K03"][5], "mm_short %d of %d" % (2 * sum(1 for i in range(65) if i % 7), n_rows) in kk["K03"][5],
               "pm_long" in kk["K03"][5]), ("WARN", True, True, False))
        ck.ok("K03 reports the count per pair", "pm_long n=%d " % n_rows in kk["K03"][3] and ("mm_long n=%d " % (2 * sum(1 for i in range(65) if i % 5))) in kk["K03"][3])
        ck.eq("K15 reports the files and header cells it verified", (kk["K15"][4], "5 of 6 verified" in kk["K15"][3], "%d header cells, 0 banned names" % sum(
            len(ALLOW[n_]) for n_ in ("brent_ledger.csv", "brent_windows.csv", "brent_leadlag.csv", "brent_file_stats.csv", "fetch_log.csv")) in kk["K15"][3]), ("PASS", True, True))
        n_pct = sum(1 for n_, hs in PERCENT_COLS.items() for h_ in hs for r_ in read_table(os.path.join(out, n_), ALLOW[n_]) if r_[ALLOW[n_].index(h_)] != "")
        ck.eq("K16 counts the percent cells it checked and the most decimals found", (kk["K16"][4], "%d cells in 4 columns of 2 files" % n_pct in kk["K16"][3],
                                                                                         "most decimals found: 1" in kk["K16"][3]), ("PASS", True, True))
        full = lambda: (fx_csv(2030, FX_2030, same_name=True, bom=True, swap="Swap__", full_pct=True, blank_pct=bp),
                        fx_csv(2031, FX_2031_MON, first=len(FX_2030), swap="Swap_", unnamed_tail=True, extra_rows=[fx_decoy()], full_pct=True, blank_pct=bp))
        for bp, label in ((), "every pair populated on every row"), (("nr_long",), "one pair populated on no row"):
            with tempfile.TemporaryDirectory() as tmp2:
                a30, a31 = full()
                cf = fx_build(tmp2, a2030=a30, a2031=a31)[0]
                kf = {x[0]: x for x in cf["chk"]}
                if bp:
                    ck.ok("K03 warns and names the pair that is populated on no row (%s)" % label, kf["K03"][4] == "WARN" and "nr_long 0 of %d" % n_rows in kf["K03"][5], str(kf["K03"][4:6]))
                else:
                    ck.ok("K03 passes with every pair populated on every row (%s)" % label, kf["K03"][4] == "PASS" and all(" n=%d " % n_rows in e + " " for e in kf["K03"][3].split("; ")),
                          str(kf["K03"][3:5]))
        # a build refuses a cache file the log does not know
        open(os.path.join(cache, "COTHist2031.csv"), "ab").write(b"\r\n")
        ck.raises("a cache file whose content is not in fetch_log.csv is refused", DataError, lambda: build(cache, out, prices=fx_prices(), pins=(), anchors=fx_window_anchors(), kemp=False,
                                                                                                             say=lambda *a: None, write=False), "fetch_log")
    lr = leadlag_row("x", "fo", [dt.date(2030, 1, 1) + dt.timedelta(days=7 * k) for k in range(6)], [0, 1, 3, 2, 5, 9], [10, 11, 13, 12, 15, 19])
    ck.eq("lead-lag on a series whose changes equal the price changes: abs correlation 1, n 5 same / 4 next", (lr["pearson_same_abs"], lr["n_same"], lr["n_next"]), ("1.000", 5, 4))
    # the start of the lead-lag sample, on a series that straddles 2024-01-01 (the 2030-2031 fixture cannot test it: all its dates are later)
    sd = [dt.date(2023, 11, 28) + dt.timedelta(days=7 * k) for k in range(10)]
    ls = leadlag_row("x", "fo", sd, [0, 2, 3, 7, 6, 9, 15, 14, 20, 26], [70, 71, 70.5, 72, 73, 72, 74, 75, 74.5, 77])
    ck.eq("the lead-lag sample starts at the first report date on or after 2024-01-01: first and last week, n same / next / prev",
          (ls["first_week"], ls["last_week"], ls["n_same"], ls["n_next"], ls["n_prev"]), ("2024-01-02", "2024-01-30", 5, 4, 5))
    ck.eq("LATE_SPLIT is 2024-01-01", LATE_SPLIT, dt.date(2024, 1, 1))


class FakeClock:
    def __init__(self, t0):
        self.t = t0
        self.slept = []

    def time(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


FX_NOW = dt.datetime(2026, 10, 15, 12, 0, 0, tzinfo=dt.timezone.utc)
SPACING_OK = 5.05 - 1e-6        # 5.05 s less the resolution of a float holding epoch seconds (2.4e-7 s); the test pins MIN_SLEEP == 5.05 separately


def fx_ice_body():
    return (",".join(h.replace("{SS}", "Swap_Positions_Short_All").replace("{SP}", "Swap_Positions_Spread_All") for h in FX_HEAD) + "\r\n").encode()


def suite_fetch(ck):
    good_ice, good_eia = fx_ice_body(), XLS_MAGIC + b"\xa1\xb1\x1a\xe1" + b"x" * 64

    def rig(tmp, script, max_requests=MAX_REQUESTS, sleep=MIN_SLEEP, clock=None, cache="cache", eia_loader=None):
        clock = clock or FakeClock(FX_NOW.timestamp())
        calls = []

        def opener(host, target, headers, timeout, cap):
            calls.append((host, target, dict(headers), clock.time()))
            res = script(host, target) if callable(script) else script
            if isinstance(res, Exception):
                raise res
            return res
        fe = Fetcher(os.path.join(tmp, cache), os.path.join(tmp, "out"), sleep=sleep, max_requests=max_requests, opener=opener, wall=clock.time,
                     mono=clock.time, sleeper=clock.sleep, stop_path=os.path.join(tmp, "STOP"),
                     now_utc=lambda: dt.datetime.fromtimestamp(clock.time(), dt.timezone.utc), pid_alive=lambda p: False,
                     eia_loader=eia_loader or (lambda path: {}))      # the stub accepts any body; the real loader is used where a test says so
        return fe, calls, clock

    def case(label, script, action, expect_stop, expect_exc=None, **kw):
        with tempfile.TemporaryDirectory() as tmp:
            fe, calls, clock = rig(tmp, script, **kw)
            exc, outs = None, []
            try:
                with fe:
                    outs = action(fe)
            except Exception as e:
                exc = e
            stop = os.path.exists(os.path.join(tmp, "STOP"))
            ck.eq("%s: STOP latch %s" % (label, "written" if expect_stop else "not written"), stop, expect_stop)
            if expect_exc is not None:
                ck.ok("%s: raises %s" % (label, expect_exc.__name__), isinstance(exc, expect_exc), "got %r" % (exc,))
            else:
                ck.ok("%s: no exception" % label, exc is None, "got %r" % (exc,))
            ck.ok("%s: lock removed in finally" % label, not os.path.exists(os.path.join(tmp, ".fetch.lock")))
            return outs, calls, tmp

    ice_ok = lambda h, t: (200, good_ice)
    # saved, paced, logged
    with tempfile.TemporaryDirectory() as tmp:
        script = lambda h, t: (200, good_eia) if h == EIA_HOST else (200, good_ice)
        fe, calls, clock = rig(tmp, script)
        with fe:
            outs = [fe.fetch_ice_year(2012, 2026), fe.fetch_ice_year(2013, 2026), fe.fetch_eia()]
        ck.eq("two ICE years and the EIA file are saved", outs, ["saved", "saved", "saved"])
        starts = [c[3] for c in calls]
        ck.ok("consecutive request starts are at least 5.05 s apart", len(starts) == 3 and all(b - a >= SPACING_OK for a, b in zip(starts, starts[1:])), str(starts))
        ck.ok("request headers are exactly User-Agent and Accept-Encoding, the canonical agent", all(sorted(c[2]) == ["Accept-Encoding", "User-Agent"] and c[2]["User-Agent"] == UA for c in calls))
        ck.eq("requests went to www.ice.com and www.eia.gov only", {c[0] for c in calls}, {ICE_HOST, EIA_HOST})
        ck.eq("request targets are the allowlisted paths", [c[1] for c in calls], [ice_path(2012), ice_path(2013), EIA_PATH])
        log = read_table(os.path.join(tmp, "out", "fetch_log.csv"), FETCH_LOG_COLS)
        ck.eq("fetch_log has one row per request with status, bytes and sha256", [(r[1], r[3], r[4], r[5], r[6]) for r in log],
              [(ICE_HOST, "200", "saved", str(len(good_ice)), sha256_of(good_ice))] * 2 + [(EIA_HOST, "200", "saved", str(len(good_eia)), sha256_of(good_eia))])
        ck.ok("the EIA file landed under <out>/raw/, and no .part is left", open(os.path.join(tmp, "out", "raw", EIA_RAW_NAME), "rb").read() == good_eia
              and not os.path.exists(os.path.join(tmp, "out", "raw", EIA_RAW_NAME + ".part")))
        ck.ok("the ICE file landed in the cache, not in the output directory", os.path.exists(os.path.join(tmp, "cache", "COTHist2012.csv")) and not os.path.exists(os.path.join(tmp, "out", "COTHist2012.csv")))
        # spacing persists across invocations; cached past years are not requested
        fe2, calls2, _ = rig(tmp, script, clock=clock)
        with fe2:
            ck.eq("a past-year file already cached is not requested again", (fe2.fetch_ice_year(2012, 2026), len(calls2)), ("cached", 0))
            fe2.fetch_ice_year(2026, 2026)
        ck.ok("the 5.05 s spacing persists across invocations", calls2[0][3] - starts[-1] >= SPACING_OK, "%s %s" % (calls2[0][3], starts[-1]))
        ck.eq("the report-year file is requested even though a past one is cached", len(calls2), 1)
        with fe2.__class__(os.path.join(tmp, "cache"), os.path.join(tmp, "out"), opener=lambda *a: (200, good_ice), wall=clock.time, mono=clock.time, sleeper=clock.sleep,
                           stop_path=os.path.join(tmp, "STOP"), now_utc=lambda: dt.datetime.fromtimestamp(clock.time(), dt.timezone.utc), pid_alive=lambda p: False) as fe3:
            ck.eq("the report-year file fetched today is not requested again", fe3.fetch_ice_year(2026, 2026), "cached_today")
            ck.eq("the EIA file fetched today is not requested again", fe3.fetch_eia(), "cached_today")
    # refusals latch
    for status in (301, 302, 401, 403, 404, 407, 429, 451, 500, 503):
        case("ICE HTTP %d" % status, (lambda s: lambda h, t: (s, b""))(status), lambda fe: [fe.fetch_ice_year(2012, 2026)], True, Latched)
    case("EIA HTTP 403", lambda h, t: (403, b""), lambda fe: [fe.fetch_eia()], True, Latched)
    case("ICE 200 with an HTML body", lambda h, t: (200, b"<html>blocked</html>"), lambda fe: [fe.fetch_ice_year(2012, 2026)], True, Latched)
    case("ICE 200 with a CSV that has the wrong first column", lambda h, t: (200, b"a,b,c\r\n1,2,3\r\n"), lambda fe: [fe.fetch_ice_year(2012, 2026)], True, Latched)
    case("ICE 200 with a body over the cap", lambda h, t: (200, None), lambda fe: [fe.fetch_ice_year(2012, 2026)], True, Latched)
    case("EIA 200 with a body that is not an XLS", lambda h, t: (200, b"<html>login</html>"), lambda fe: [fe.fetch_eia()], True, Latched)
    case("a socket fault ends the invocation", lambda h, t: SocketFault("timeout"), lambda fe: [fe.fetch_ice_year(2012, 2026), fe.fetch_ice_year(2013, 2026)], False, SocketFault)
    outs, calls, tmp = case("a good run", ice_ok, lambda fe: [fe.fetch_ice_year(2012, 2026)], False)
    ck.eq("a good run sends exactly one request", len(calls), 1)
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = rig(tmp, lambda h, t: SocketFault("reset"))
        try:
            with fe:
                fe.fetch_ice_year(2012, 2026)
        except SocketFault:
            pass
        log = read_table(os.path.join(tmp, "out", "fetch_log.csv"), FETCH_LOG_COLS)
        ck.eq("a socket fault is logged", [r[4] for r in log], ["socket_fault:reset"])
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = rig(tmp, ice_ok, max_requests=1)
        raised = None
        with fe:
            fe.fetch_ice_year(2012, 2026)
            try:
                fe.fetch_ice_year(2013, 2026)
            except MaxRequests as e:
                raised = e
        ck.ok("the request beyond --max-requests 1 is refused", raised is not None and len(calls) == 1)
    # years
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = rig(tmp, ice_ok)
        with fe:
            ck.raises("a year after the report year is refused", Refused, lambda: fe.fetch_ice_year(2027, 2026))
            ck.raises("a year before 2011 is refused", Refused, lambda: fe.fetch_ice_year(2010, 2026))
        ck.eq("...and sent no request", len(calls), 0)
    ck.eq("parse_years reads ranges and lists", parse_years("2012-2014,2019", 2026), [2012, 2013, 2014, 2019])
    ck.raises("parse_years refuses a malformed year", Refused, lambda: parse_years("12", 2026))
    # STOP latch refuses later runs; the lock stops a second fetcher
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = rig(tmp, lambda h, t: (403, b""))
        try:
            with fe:
                fe.fetch_ice_year(2012, 2026)
        except Latched:
            pass
        f2, calls2, _ = rig(tmp, ice_ok)
        ck.raises("a later fetch refuses to run while STOP exists", Latched, lambda: f2.__enter__())
        ck.eq("...and sends no request", len(calls2), 0)
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = rig(tmp, ice_ok)
        fe.pid_alive = lambda p: True
        with fe:
            f2, _, _ = rig(tmp, ice_ok)
            f2.pid_alive = lambda p: True
            ck.raises("a live lock stops a second fetcher", Refused, lambda: f2.__enter__())
        f3, _, _ = rig(tmp, ice_ok)
        with f3:
            ck.ok("the lock is free again after the first fetcher leaves", True)
    ck.raises("--sleep below 5 is refused", Refused, lambda: Fetcher(os.path.join(tempfile.gettempdir(), "x_never_used"), "/tmp/y", sleep=4.9))
    ck.raises("--max-requests above 20 is refused", Refused, lambda: Fetcher(os.path.join(tempfile.gettempdir(), "x_never_used"), "/tmp/y", max_requests=21))
    ck.raises("a cache inside the repository is refused by the fetcher", Refused, lambda: Fetcher(os.path.join(ROOT, "data", "cache"), "/tmp/y"))
    # adoption: a file already in the cache gets a log row, no request
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "cache"))
        open(os.path.join(tmp, "cache", "COTHist2011.csv"), "wb").write(good_ice)
        fe, calls, clock = rig(tmp, ice_ok)
        with fe:
            n1 = fe.adopt_cached()
            n2 = fe.adopt_cached()
        log = read_table(os.path.join(tmp, "out", "fetch_log.csv"), FETCH_LOG_COLS)
        ck.eq("a file already in the cache is adopted once, with no request", (n1, n2, len(calls)), (1, 0, 0))
        ck.eq("the adopted row carries the sha256 and outcome adopted_from_cache", [(r[4], r[6]) for r in log], [("adopted_from_cache", sha256_of(good_ice))])
    # pacing and the lock live beside STOP, not in the cache; the time is written exactly
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = rig(tmp, ice_ok, clock=FakeClock(FX_NOW.timestamp() + 0.123456789))
        with fe:
            ck.ok("the fetch lock is beside STOP, not in the cache", os.path.exists(os.path.join(tmp, ".fetch.lock")) and not os.path.exists(os.path.join(tmp, "cache", ".fetch.lock")))
            fe.fetch_ice_year(2012, 2026)
        ck.ok("the last-request record is beside STOP, not in the cache", os.path.exists(os.path.join(tmp, ".last_request")) and not os.path.exists(os.path.join(tmp, "cache", ".last_request")))
        ck.eq("the last-request time is written at full precision", float(open(os.path.join(tmp, ".last_request"), encoding="utf-8").read()), calls[0][3])
    with tempfile.TemporaryDirectory() as tmp:
        clock = FakeClock(FX_NOW.timestamp())
        fa, ca, _ = rig(tmp, ice_ok, clock=clock, cache="cache_a")
        with fa:
            fa.fetch_ice_year(2012, 2026)
        fb, cb, _ = rig(tmp, ice_ok, clock=clock, cache="cache_b")
        with fb:
            fb.fetch_ice_year(2012, 2026)
        ck.ok("two runs with different --cache values are still paced: the second request starts at least 5.05 s after the first",
              len(ca) == 1 and len(cb) == 1 and cb[0][3] - ca[0][3] >= SPACING_OK, "%s %s" % (ca, cb))
    with tempfile.TemporaryDirectory() as tmp:
        fa, _, clock = rig(tmp, ice_ok, cache="cache_a")
        fa.pid_alive = lambda p: True
        with fa:
            fb, _, _ = rig(tmp, ice_ok, clock=clock, cache="cache_b")
            fb.pid_alive = lambda p: True
            ck.raises("a second fetcher with a different --cache is stopped by the same lock", Refused, lambda: fb.__enter__())
    ck.raises("--sleep 5.0 is refused (the floor is 5.05)", Refused, lambda: Fetcher(os.path.join(tempfile.gettempdir(), "x_never_used"), "/tmp/y", sleep=5.0))
    ck.value("--sleep 5.05 is accepted", lambda: Fetcher(os.path.join(tempfile.gettempdir(), "x_never_used"), "/tmp/y", sleep=5.05).sleep, 5.05)
    # EIA: a body with the XLS magic bytes that does not load is a bad body (it latches and leaves nothing behind); a file already saved is untouched
    with tempfile.TemporaryDirectory() as tmp:
        raw_dir = os.path.join(tmp, "out", "raw")
        os.makedirs(raw_dir)
        open(os.path.join(raw_dir, EIA_RAW_NAME), "wb").write(b"previous good file")
        fe, calls, clock = rig(tmp, lambda h, t: (200, good_eia), eia_loader=load_eia_brent)
        raised = None
        try:
            with fe:
                fe.fetch_eia()
        except Latched as e:
            raised = e
        ck.ok("EIA 200 with the XLS magic bytes but no loadable workbook: STOP written", raised is not None and os.path.exists(os.path.join(tmp, "STOP")), "got %r" % (raised,))
        ck.ok("...the file already saved is untouched and no .part is left", open(os.path.join(raw_dir, EIA_RAW_NAME), "rb").read() == b"previous good file"
              and not os.path.exists(os.path.join(raw_dir, EIA_RAW_NAME + ".part")))
        ck.eq("...and the log records STOP:bad_body", [r[4] for r in read_table(os.path.join(tmp, "out", "fetch_log.csv"), FETCH_LOG_COLS)], ["STOP:bad_body"])
    # fetch --refresh-year: one cached past-year file again, still paced, still behind the latch
    new_body = good_ice + b"a,b,c\r\n"
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "cache"))
        open(os.path.join(tmp, "cache", "COTHist2012.csv"), "wb").write(good_ice)
        fe, calls, clock = rig(tmp, lambda h, t: (200, new_body))
        with fe:
            r0 = fe.fetch_ice_year(2012, 2026)
            n0 = len(calls)
            fe.fetch_ice_year(2013, 2026)
            r1 = fe.fetch_ice_year(2012, 2026, refresh=True)
            r2 = fe.fetch_ice_year(2012, 2026, refresh=True)
        ck.eq("a cached past-year file is not requested without refresh; with it, once (a second refresh the same day is not sent)", (r0, n0, r1, r2, len(calls)),
              ("cached", 0, "saved", "cached_today", 2))
        ck.ok("...the refreshed request is paced at least 5.05 s after the one before it", calls[1][3] - calls[0][3] >= SPACING_OK)
        ck.ok("...the file now holds the new body", open(os.path.join(tmp, "cache", "COTHist2012.csv"), "rb").read() == new_body)
        ck.eq("...and the log has a saved row for it with the new sha256", [(r[2], r[4], r[6]) for r in read_table(os.path.join(tmp, "out", "fetch_log.csv"), FETCH_LOG_COLS)][-1],
              (ice_path(2012), "saved", sha256_of(new_body)))
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "cache"))
        open(os.path.join(tmp, "cache", "COTHist2012.csv"), "wb").write(good_ice)
        fe, calls, clock = rig(tmp, lambda h, t: (403, b""))
        try:
            with fe:
                fe.fetch_ice_year(2012, 2026, refresh=True)
        except Latched:
            pass
        ck.ok("a refused refresh latches, and the cached file stays", os.path.exists(os.path.join(tmp, "STOP")) and open(os.path.join(tmp, "cache", "COTHist2012.csv"), "rb").read() == good_ice)
    with tempfile.TemporaryDirectory() as tmp:
        open(os.path.join(tmp, "STOP"), "w").write("test\n")
        fe, calls, clock = rig(tmp, ice_ok)
        ck.raises("a refresh refuses to run while STOP exists", Latched, lambda: fe.__enter__())
        ck.eq("...and sends no request", len(calls), 0)

    def cli(argv, script=ice_ok):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "cache"))
            open(os.path.join(tmp, "cache", "COTHist2012.csv"), "wb").write(good_ice)
            clock, seen = FakeClock(FX_NOW.timestamp()), []

            def opener(host, target, headers, timeout, cap):
                seen.append((host, target))
                return (200, good_eia) if host == EIA_HOST else script(host, target)
            kw = dict(opener=opener, wall=clock.time, mono=clock.time, sleeper=clock.sleep, stop_path=os.path.join(tmp, "STOP"),
                      now_utc=lambda: dt.datetime.fromtimestamp(clock.time(), dt.timezone.utc), pid_alive=lambda p: False, eia_loader=lambda path: {})
            sink = io.StringIO()
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                rc = main(["fetch", "--cache", os.path.join(tmp, "cache"), "--out", os.path.join(tmp, "out")] + argv, _fetcher_kw=kw, _today=dt.date(2026, 10, 15))
            return rc, seen
    ck.eq("fetch --refresh-year 2012 sends one request, for that ICE file, and does not fetch the EIA file", cli(["--refresh-year", "2012"]), (0, [(ICE_HOST, ice_path(2012))]))
    ck.eq("fetch --refresh-year with --years is refused (exit 5), with no request", cli(["--refresh-year", "2012", "--years", "2013"]), (5, []))
    ck.eq("fetch --refresh-year 2027 (after the report year) is refused (exit 5), with no request", cli(["--refresh-year", "2027"]), (5, []))
    ck.eq("fetch with no option asks for the report-year ICE file and the EIA file", cli([]), (0, [(ICE_HOST, ice_path(2026)), (EIA_HOST, EIA_PATH)]))


SUITES = {"pure": suite_pure, "parse": suite_parse, "mapping": suite_mapping, "build": suite_build, "fetch": suite_fetch}
# the guard -> the part of the suite that must notice when it is removed
GUARDS = [
    ("blank_totals", "parse"), ("bom", "parse"), ("swap_spelling", "parse"), ("monday_dates", "parse"), ("type_by_column", "parse"),
    ("latch_non200", "fetch"), ("latch_bad_body", "fetch"), ("socket_no_latch", "fetch"), ("pacing", "fetch"), ("host_allowlist", "pure"),
    ("cache_outside_repo", "pure"), ("pct_precision", "pure"), ("column_allowlist", "pure"), ("fo_identity_exact", "parse"), ("duplicate_week", "parse"),
    ("units", "parse"), ("blank_class", "parse"), ("pct_agree", "parse"), ("seam_gap", "parse"), ("price_lag", "parse"), ("min_sleep", "fetch"),
    ("max_requests", "fetch"), ("stop_blocks_fetch", "fetch"), ("xls_magic", "fetch"), ("report_year", "pure"), ("ua_no_address", "pure"),
    ("source_line", "pure"), ("shared_pacing", "fetch"), ("eia_validate", "fetch"), ("price_flag", "build"),
]
# pairs of class columns exchanged inside the parser; each is on the SAME side (or the same class), where the two identities are blind. The mapping suite must notice.
MAP_MUTANTS = (("pm_long", "sw_long"), ("sw_short", "pm_short"), ("mm_long", "ot_long"), ("ot_short", "nr_short"), ("pm_long", "nr_long"), ("mm_short", "nr_short"))
A11_GUARDS = ("blank_totals", "bom", "swap_spelling", "monday_dates", "type_by_column", "latch_non200", "latch_bad_body", "socket_no_latch", "pacing",
              "host_allowlist", "cache_outside_repo", "pct_precision", "column_allowlist", "fo_identity_exact", "duplicate_week")


def run_suite(name):
    ck = Checks()
    try:
        SUITES[name](ck)
    except Exception as e:          # a suite that crashes under a removed guard has noticed it
        ck.ok("suite %s ran to completion" % name, False, "%s: %s" % (type(e).__name__, e))
    return ck


def selftest(mutants=True):
    t0 = time.time()
    results = [(n, run_suite(n)) for n in ("pure", "parse", "mapping", "build", "fetch")]
    bad_total = 0
    for title, ck in results:
        print("== %s: %d checks" % (title, len(ck.items)))
        for name, cond, detail in ck.items:
            print("  %s  %s%s" % ("PASS" if cond else "FAIL", name, "" if cond else "   <- " + detail))
            bad_total += 0 if cond else 1
    mres = []
    if mutants:
        print("== guards (each must make at least one check fail when switched off; A11 cases marked *)")
        for g, suite in GUARDS:
            with mutant(g):
                ck = run_suite(suite)
            bad = ck.failed()
            mres.append((g, bool(bad)))
            print("  %s  %s%s  (%s)%s" % ("DETECTED    " if bad else "NOT DETECTED", g, " *" if g in A11_GUARDS else "", suite,
                                          "   first failing check: " + bad[0][0] if bad else ""))
            bad_total += 0 if bad else 1
        print("== column-mapping mutants (two class columns exchanged inside the parser; each must make a check fail)")
        for a_, b_ in MAP_MUTANTS:
            with swapped(a_, b_):
                ck = run_suite("mapping")
            bad = ck.failed()
            mres.append(("%s<->%s" % (a_, b_), bool(bad)))
            print("  %s  swap %s <-> %s  (mapping)%s" % ("DETECTED    " if bad else "NOT DETECTED", a_, b_, "   first failing check: " + bad[0][0] if bad else ""))
            bad_total += 0 if bad else 1
    n_checks = sum(len(ck.items) for _, ck in results)
    print("selftest: %d checks, %d guards switched off and column swaps applied, one at a time, %d failure(s), %.1f s" % (n_checks, len(mres), bad_total, time.time() - t0))
    return 0 if bad_total == 0 else 1


# ------------------------------------------------------------------------------------------------------------------------
# command line
# ------------------------------------------------------------------------------------------------------------------------
def main(argv=None, _fetcher_kw=None, _today=None):
    """_fetcher_kw and _today are for the selftest only (an injected opener, clock and STOP path; a fixed date)."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch", help="download ICE COTHist<YYYY>.csv files into the cache and the EIA Brent file (the only network command)")
    pf.add_argument("--years", help="years and ranges, e.g. 2012-2017,2019-2025 (default: the report year)")
    pf.add_argument("--refresh-year", type=int, metavar="YYYY",
                    help="request this one year's ICE file again although it is cached (the New-Year seam); nothing else is requested")
    pf.add_argument("--cache", default=os.environ.get("ICE_COT_CACHE") or CACHE_DEFAULT)
    pf.add_argument("--out", default=OUT_DEFAULT, help="where fetch_log.csv and raw/eia_RBRTEd.xls are kept")
    pf.add_argument("--sleep", type=float, default=MIN_SLEEP, help="seconds between request starts (at least %.2f)" % MIN_SLEEP)
    pf.add_argument("--max-requests", type=int, default=MAX_REQUESTS)
    pb = sub.add_parser("build", help="offline: validate the cache and write every output")
    pb.add_argument("--cache", default=os.environ.get("ICE_COT_CACHE") or CACHE_DEFAULT)
    pb.add_argument("--out", default=OUT_DEFAULT)
    ps = sub.add_parser("selftest", help="synthetic rows, guards switched off one at a time; no network")
    ps.add_argument("--no-mutants", action="store_true", help="run the suite once, without switching guards off")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest(mutants=not a.no_mutants)
    try:
        if a.cmd == "build":
            ctx = build(a.cache, a.out)
            print("\n".join(report(ctx)))
            print("\nwrote %s in %s" % (", ".join(sorted(n for n in ALLOW if n != "fetch_log.csv")), tilde(a.out)))
            return 0
        cur = report_year(_today or dt.datetime.now(dt.timezone.utc).date())
        if a.refresh_year is not None and a.years:
            raise Refused("--refresh-year is one file on its own; do not combine it with --years")
        years = [a.refresh_year] if a.refresh_year is not None else (parse_years(a.years, cur) if a.years else [cur])
        with Fetcher(a.cache, a.out, sleep=a.sleep, max_requests=a.max_requests, **(_fetcher_kw or {})) as fe:
            n = fe.adopt_cached()
            if n:
                print("adopted %d file(s) already in the cache into fetch_log.csv (no request)" % n)
            for y in years:
                print("ICE COTHist%d.csv: %s" % (y, fe.fetch_ice_year(y, cur, refresh=a.refresh_year is not None)))
            if a.refresh_year is None:
                print("EIA RBRTEd.xls: %s" % fe.fetch_eia())
            print("requests sent: %d" % fe.requests)
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
    except (HeaderError, DataError) as e:
        print("STOP (data): %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
