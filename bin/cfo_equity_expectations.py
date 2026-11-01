#!/usr/bin/env python3
"""The CFO Survey's mean expected S&P 500 return, 10-year (E1) and 12-month (E2), Q1 2024 to Q1 2026, from the Richmond Fed's historical workbook. Python 3 standard library only.

  python3 bin/cfo_equity_expectations.py fetch --vintage YYYYMMDD [--cache DIR]                                   # network; supervisor only; ONE request; later vintages only
  python3 bin/cfo_equity_expectations.py build --vintage YYYYMMDD --stage pre [--cache DIR] [--out DIR]          # offline; layout only: no S&P value is converted, printed or written
  python3 bin/cfo_equity_expectations.py build --vintage YYYYMMDD --stage dry --out SCRATCH                      # offline; a synthetic workbook with the four pin values planted; writes only to SCRATCH
  python3 bin/cfo_equity_expectations.py build --vintage YYYYMMDD --stage full [--registering [--supersede]]     # offline; --registering is the registering build; supervisor only
  python3 bin/cfo_equity_expectations.py selftest [--no-mutants] [--mutant NAME]                                  # synthetic data only; no network; under 30 s

Specification: _research/2026-11-01-CFO-Equity-Expectations-Spec.md (committed at e371638, with the supervisor's rulings of rounds 1 and 2; a ruling wins over the body).
Outputs: data/cfo_equity_expectations/ (registered.csv, yardstick.csv, checks.csv, README.md committed; path.csv local and gitignored) and, per vintage,
data/vintages/cfo_survey/<YYYYMMDD>/MANIFEST.csv (the workbook sits in its raw/ folder, which git ignores).

WHAT TOUCHES THE NETWORK. Only `fetch`, only www.richmondfed.org, ONE GET of one fixed path, no redirect followed, no retry, timeout 300 s, Accept-Encoding identity, one fixed generic
User-Agent with no name, address or contact. A 3xx is a FAIL (exit 3) and writes no STOP file. Any 403, 429 or other non-200 status, and a 200 body that is not a zip workbook of 50,000
to 2,000,000 bytes, writes STOP_cfo in data/vintages/cfo_survey/ (five lines) and ends with exit 2; with it present no request is made. A timeout prints FAIL network, exits 3 and latches
nothing. This script never deletes, renames over or truncates a STOP file; only a person deletes one. The registering vintage (20261101) is the supervisor's own download and is never fetched.

STAGES (blind order). `pre` reports the layout and the type of each S&P cell from its attributes and converts no S&P value. `dry` builds a synthetic workbook and the whole pipeline
into a scratch folder outside data/. `full` is the real build; with --registering it also writes registered.csv, once, and refuses unless the 4.6 block held below reproduces its sha256.

WHAT IT RECORDS. The change in the mean expected S&P 500 return between two quarters of one vintage of the survey's revised historical file, on two horizons, with a sign. It builds no
equity premium and subtracts no Treasury yield; it reads no other series, and it passes no judgement on any respondent.
"""
import argparse
import contextlib
import csv
import datetime as dt
import decimal
import hashlib
import http.client
import io
import os
import posixpath
import re
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
import zipfile
from decimal import Decimal
from urllib.parse import urlsplit

decimal.getcontext().prec = 28

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
    """A request, path, argument or setting this script will not honour (exit 5)."""


class Halt(Exception):
    """A structural layout fault in the workbook (exit 4): nothing is registered."""


class UnitError(Exception):
    """A pin off by a factor of 5 or more (exit 5): nothing is registered."""


class DataError(Exception):
    """A hard problem with the data or with an output, or a FAIL check (exit 2)."""


class Latched(Exception):
    """A STOP file was written (or already exists); the fetch ends (exit 2)."""


class SocketFault(Exception):
    """Timeout, reset or TLS error: the fetch ends with exit 3, without latching."""


class WbError(Exception):
    """The bytes are not a readable xlsx workbook."""


class Undef(Exception):
    """A cell has no usable number (empty, text, a formula with no cached value, not a finite number)."""


class CrossBreak(Exception):
    """A window that would span the 2020 break."""


# ------------------------------------------------------------------------------------------------------------------------
# constants
# ------------------------------------------------------------------------------------------------------------------------
SPEC_FILE = "_research/2026-11-01-CFO-Equity-Expectations-Spec.md"
SPEC_COMMIT = "e371638"
HOST = "www.richmondfed.org"
URL_PATH = "/-/media/RichmondFedOrg/research/national_economy/cfo_survey/current_historical_cfo_data.xlsx"
URL = "https://" + HOST + URL_PATH
USER_AGENT = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"          # the one neutral string CLAUDE.md fixes (bin/check.sh M10 enforces it): no person, address or contact
TIMEOUT = 300
MIN_BYTES, MAX_BYTES = 50000, 2000000
BODY_CAP = 8 * 1024 * 1024
ERR_CAP = 4096
WB_NAME = "current_historical_cfo_data.xlsx"
STOP_NAME = "STOP_cfo"
REG_VINTAGE = "20261101"
REG_SHA256 = "1b4e215c5626b741182b8a647c7a66d5c6d448616942d27138f18d37acec6bca"
REG_BYTES = 188861
CREDIT = "The CFO Survey (Duke Fuqua School of Business, Federal Reserve Banks of Richmond and Atlanta)"

SH_DUKE, SH_DUKE_D, SH_CUR, SH_CUR_D, SH_DATES = "through_Q1_2020", "through_Q1_2020_dictionary", "CFO_SP500", "from_Q2_2020on_dictionary", "CFO_survey_dates"
SHEETS = (SH_DUKE, SH_DUKE_D, SH_CUR, SH_CUR_D, SH_DATES)
COL_D10, COL_D12, COL_C10, COL_C12 = "sp_10_exp", "sp_1_exp", "sp_10yrexp_2", "sp_12moexp_2"
SERIES = {"DUKE10": (SH_DUKE, COL_D10, "duke", "10y"), "DUKE12": (SH_DUKE, COL_D12, "duke", "12m"),
          "CUR10": (SH_CUR, COL_C10, "current", "10y"), "CUR12": (SH_CUR, COL_C12, "current", "12m")}
SERIES_ORDER = ("DUKE10", "DUKE12", "CUR10", "CUR12")
REQUIRED = {SH_DUKE: (COL_D10, COL_D12), SH_CUR: (COL_C10, COL_C12), SH_DUKE_D: (), SH_CUR_D: (), SH_DATES: ()}
N_DUKE, N_CUR = 74, 25                                   # HALT row counts (the Q4 2026 release will make it 26: the spec's counts are constants to revisit by amendment)
DUKE_KEYS = ((2001, 4), (2020, 1))                       # first and last quarter of the Duke sheet
CUR_KEYS = ((2020, 3), (2026, 3))
BREAK_LAST_DUKE, BREAK_FIRST_CUR = (2020, 1), (2020, 3)
WINDOW = ((2024, 1), (2026, 1))
LAG = 8
ZONE = Decimal("0.10")
UNIT_LO, UNIT_HI = Decimal(-20), Decimal(40)
SPF_STAT = "0.1543"                                      # fixed text, as in the 4.6 block; never read from a file
SPF_DEADLINES = "6 Feb 2024 and 2 Mar 2026"
Y_ENDS = ((2004, 1), (2020, 1))                          # described Duke range: end quarters
YC_ENDS = ((2022, 3), (2026, 3))                         # described current variant: end quarters
Y_NOMINAL, Y_DEFINED, YC_NOMINAL, YC_DEFINED = 65, 63, 17, 16
Y_SPANS, YC_SPANS = 8, 3
PINS = (("CUR12", "2026Q2", "7.8"), ("CUR12", "2026Q3", "7.9"), ("CUR10", "2026Q2", "9.7"), ("CUR10", "2026Q3", "9.6"))
PIN_TOL = Decimal("0.05")
PIN_HI, PIN_LO = Decimal(5), Decimal("0.2")
SIGN_WORD = {"RISE": "rose", "FALL": "fell"}

# the 4.6 block, byte for byte (the interior of the fence), and its sha256 (the one hash)
PREREG_LINES = (
    'DEF|stat=exact_Decimal_difference_of_two_rounded_cells:_round_each_cell_half-even_to_6_decimals,_then_exp(end_quarter)-exp(start_quarter),_no_further_rounding|unit=percentage_points|exp=the_workbook_cell_as_stored_(percent,_not_fraction)|vintage=the_statistic_is_the_change_in_the_named_vintage_of_the_surveys_revised_historical_file,_never_first_published|quarter=calendar_quarter_label_YYYYQn|no_value_imputed_(missing_is_never_zero,_never_interpolated,_never_carried)|parsing=decimal_prec28,_never_float',
    'CUR10|sheet=CFO_SP500|column=sp_10yrexp_2|era=current|quarters=2020Q3..2026Q3|n_expected=25|2020Q2_absent_and_not_invented',
    'CUR12|sheet=CFO_SP500|column=sp_12moexp_2|era=current|quarters=2020Q3..2026Q3|n_expected=25|2020Q2_absent_and_not_invented',
    'SIGN|RISE_if_stat>=0.10;FALL_if_stat<=-0.10;ZERO_if_abs(stat)<0.10|a_convention_equal_to_the_one-decimal_resolution_the_survey_publishes,_fixed_before_data,_not_a_noise_bound|the_signed_stat_is_always_printed_to_two_decimals_beside_the_SPF_figure',
    'SPF|stat_pp=0.1543|sign=RISE|source=STOCK10_mean_Q1_2024_7.1513_percent_to_Q1_2026_7.3056_percent_(CORRECTIONS_C-082)|fixed_text_in_this_block_and_never_read_from_a_file_by_the_build',
    'DIRECTION|described_column_spf_direction,_never_a_verdict|SAME_if_sign==RISE;OPPOSITE_if_sign==FALL;FLAT_if_sign==ZERO;none_if_VOID;na_for_E2|never_written_as_AGREES_or_DISAGREES|set_from_the_sign',
    'VOID|order=endpoint_undefined,unit_odd|endpoint_undefined=either_endpoint_quarter_absent_or_its_cell_empty_or_not_numeric|unit_odd=any_numeric_cell_of_the_used_current_column_outside_-20..40|a_VOID_is_not_a_FAIL|a_VOID_row_carries_label_free_columns_void_reason,_a_sign_only_if_stat_is_defined_(else_none)_and_spf_direction=none',
    'HALT|exit_4_only_for_structural_layout_faults:_a_missing_sheet_or_required_column,_duplicate_or_non-consecutive_quarter_keys,_row_counts_other_than_74_(through_Q1_2020)_and_25_(CFO_SP500)|nothing_is_registered_after_a_halt',
    'PIN|source=Q3_2026_results_page_read_by_the_supervisor_on_1_Nov_2026|CUR12_2026Q2=7.8|CUR12_2026Q3=7.9|CUR10_2026Q2=9.7|CUR10_2026Q3=9.6|MATCH=abs(workbook-pin)<=0.05_for_all_four|NEAR=any_difference_above_0.05_and_no_unit_error_(a_WARN,_the_run_continues,_pins=near_is_written)|UNIT_ERROR=any_pin_off_by_a_factor_of_5_or_more_(workbook/pin>=5_or_<=0.2)|UNIT_ERROR=the_full_stage_halts_with_exit_5_before_any_registered_row_is_written|the_pins_are_never_used_in_a_statistic_and_do_not_reach_the_window',
    'E1|horizon=10y|window=2024Q1..2026Q1|series=CUR10|registered=stat,sign|described=spf_direction|blind=full|mandatory=yes|order=VOID,sign',
    'E2|horizon=12m|window=2024Q1..2026Q1|series=CUR12|registered=stat,sign|blind=full|mandatory=no|use=README_only|order=VOID,sign',
)
SPEC_PREREG_SHA256 = "2324862de97a98ee2b6b9de9576b0a3c43d7e3042b24289d5d3b97f05d2b230a"
SPEC_PREREG_BYTES = 2697

# the header allowlist, canonical text (section 5); bin/check.sh holds its own literal copy of these four lines
SPEC_ALLOW_TEXT = (
    "registered.csv:statement_id,version,superseded,horizon,series,vintage,workbook_sha256,start_quarter,end_quarter,exp_start,exp_end,stat_pp,sign,void_reason,blind,pins,spf_stat_pp,spf_direction,prereg_sha256\n"
    "path.csv:era,horizon,quarter,exp,status,survey_open,survey_close\n"
    "yardstick.csv:yardstick,horizon,first_end_quarter,last_end_quarter,n_nominal,n_defined,min_change_pp,max_change_pp,max_disjoint_spans\n"
    "checks.csv:check_id,description,expected,observed,status\n")
ALLOW = {l.split(":", 1)[0]: l.split(":", 1)[1].split(",") for l in SPEC_ALLOW_TEXT.splitlines()}
ALLOW_ORDER = tuple(l.split(":", 1)[0] for l in SPEC_ALLOW_TEXT.splitlines())
COMMITTED_CSV = ("registered.csv", "yardstick.csv", "checks.csv")
COMMITTED = COMMITTED_CSV + ("README.md",)
LOCAL = ("path.csv",)
KEYS = {"registered.csv": ("statement_id", "version"), "path.csv": ("era", "horizon", "quarter"), "yardstick.csv": ("yardstick",), "checks.csv": ("check_id",)}
ALLOWED_VALUES = {
    "registered.csv": {"statement_id": {"E1", "E2"}, "superseded": {"no", "yes"}, "horizon": {"10y", "12m"}, "series": {"CUR10", "CUR12"}, "sign": {"RISE", "FALL", "ZERO", "none"},
                       "void_reason": {"none", "endpoint_undefined", "unit_odd"}, "blind": {"full", "partial"}, "pins": {"match", "near"}, "spf_direction": {"SAME", "OPPOSITE", "FLAT", "none", "na"}},
    "path.csv": {"era": {"duke", "current"}, "horizon": {"10y", "12m"}, "status": {"ok", "empty"}},
    "yardstick.csv": {"yardstick": {"Y10", "Y12", "YC10", "YC12"}, "horizon": {"10y", "12m"}},
    "checks.csv": {"status": {"PASS", "WARN", "FAIL", "INFO"}},
}
VERDICT_RX = re.compile(r"HELD|FALSIFIED|PROVEN|CAUSED|REFUTED|MATERIAL")        # section 5: no output carries a verdict word
HEX64 = re.compile(r"^[0-9a-f]{64}$")
QRX = re.compile(r"^\d{4}Q[1-4]$")

# the wording guard (section 7): the two G14 patterns pasted, and the additions
CAUSAL_RX = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b", re.I)
EXTRA_RX = re.compile('\\b(?:in|out)flows?\\b|\\bflow(?:s|ed|ing)?\\s+(?:into|out\\s+of|from|to)\\b|\\bmanipulat\\w*|\\bmanag(?:e|ed|es|ing)\\s+(?:earnings|results|revenue)\\b|\\bearnings\\s+management\\b|\\baggressive\\w*|\\bfraud\\w*|\\bmisstat\\w*|\\binflat(?:e|ed|es|ing)\\b|\\bboost(?:s|ed|ing)?\\b|\\bpadd(?:ed|ing)\\b|\\blow[- ]quality\\b|\\bfake\\b|\\b(?:prices?|valuations?|multiples?|stocks?|shares)\\s+(?:rose|fell|rallied|moved|jumped|dropped)\\b|\\bmaterial\\w*|\\boverstat\\w*|\\bpulled\\s+forward\\b|\\bflatter\\w*|\\bwindow[- ]dressing\\b|\\bred\\s+flags?\\b|\\bvelocity\\b|\\bintensity\\b|\\bmultiplier\\b|\\bleverag\\w*|\\bfuel(?:l?ed|s|ing)?\\b|\\bsupport(?:ed|s|ing)?\\s+(?:the\\s+)?(?:rally|prices?|valuations?)\\b|\\bsignifican\\w*|\\bpermissive\\b|\\bpropell\\w*|\\bpow(?:er|ered)\\s+(?:the\\s+)?(?:rally|rise)\\b|\\bproves?\\b|\\bproven\\b', re.I)
ADD_RXS = (("since", re.compile(r"\bsince\s+(?:19|20)\d\d\b", re.I)), ("extremes", re.compile(r"\b(?:highest|lowest|record|peak|trough)\b", re.I)),
           ("comparable", re.compile(r"\bcomparable\b", re.I)), ("unusual", re.compile(r"\bunusual\b", re.I)), ("agrees", re.compile(r"\b(?:dis)?agrees?\b", re.I)),
           ("confirm", re.compile(r"\bconfirm\w*", re.I)))
R_A = "This build measures one leg only, the expected return on the S&P 500 from a panel of financial decision-makers at US firms who say they follow the stock market; it builds no equity premium and subtracts no Treasury yield."
R_B = "Expectations of 12-month returns in this survey have been found to follow past returns (Greenwood and Shleifer 2014); for the 10-year horizon the evidence is weaker, so a change in either is not evidence about the discount rate."
R_C = "The survey changed in 2020 (new sponsors, different question wording and outlier treatment), so levels are never compared across 2020; only changes within each series are."
R_D = "The respondents are financial decision-makers at firms (chief financial officers and others), not investors; the figures are stated expectations, not market prices."
REQUIRED_SENTENCES = (("R-A", R_A), ("R-B", R_B), ("R-C", R_C), ("R-D", R_D))
CHECKSH_COPIED = ("PREREG_SHA",)

STATS = {"conv": 0}                                     # how many S&P cells were converted to a number (pre must leave it at 0)


# ------------------------------------------------------------------------------------------------------------------------
# small helpers
# ------------------------------------------------------------------------------------------------------------------------
def sha256_of(b):
    return hashlib.sha256(b).hexdigest()


def read_file(path, mode="rb"):
    with open(path, mode) as fh:
        return fh.read()


def write_text(path, text):
    """Atomic write via a temporary sibling. Refuses a STOP name and text that holds a local path or an at sign."""
    if os.path.basename(path).upper().startswith("STOP"):
        raise Refused("write_text never touches a STOP file")
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


def vintage_ok(v):
    if not re.match(r"^\d{8}$", v or ""):
        return False
    try:
        dt.datetime.strptime(v, "%Y%m%d")
    except ValueError:
        return False
    return True


def vintage_long(v):
    d = dt.datetime.strptime(v, "%Y%m%d")
    return "%d %s %d" % (d.day, d.strftime("%B"), d.year)


def paths(root=None, cache=None, out=None):
    root = root or ROOT
    return (out or os.path.join(root, "data", "cfo_equity_expectations"), cache or os.path.join(root, "data", "vintages", "cfo_survey"))


def read_csv_text(text):
    """(header, rows) of a csv text with `# ...` lines skipped; ([], []) if empty."""
    lines = [l for l in text.split("\n") if l.strip() and not l.startswith("# source:")]
    rows = list(csv.reader(lines))
    return (rows[0], rows[1:]) if rows else ([], [])


def read_csv_dicts(text):
    h, rows = read_csv_text(text)
    return [dict(zip(h, r)) for r in rows]


def csv_line(cells):
    b = io.StringIO()
    csv.writer(b, lineterminator="\n").writerow(cells)
    return b.getvalue()


# ------------------------------------------------------------------------------------------------------------------------
# quarters (calendar arithmetic, never row position)
# ------------------------------------------------------------------------------------------------------------------------
KEY_RXS = ((re.compile(r"^(\d{4})\s*[-_ /]?\s*[Qq]\s*([1-4])$"), (1, 2), "YYYYQn"), (re.compile(r"^[Qq]\s*([1-4])\s*[-_ /,]?\s*(\d{4})$"), (2, 1), "Qn YYYY"),
           (re.compile(r"^([1-4])\s*[Qq]\s*[-_ /]?\s*(\d{4})$"), (2, 1), "nQ YYYY"))


def parse_key(text):
    """(year, quarter) of a quarter label, or None. The mutant parses the quarter one too low."""
    t = (text or "").strip()
    for rx, (iy, iq), _ in KEY_RXS:
        m = rx.match(t)
        if m:
            y, q = int(m.group(iy)), int(m.group(iq))
            if M("g2_q_off"):
                return (y, q - 1) if q > 1 else (y - 1, 4)
            return (y, q)
    return None


def key_format(text):
    t = (text or "").strip()
    for rx, _, fmt in KEY_RXS:
        if rx.match(t):
            return fmt
    return None


def parse_q(s):
    m = re.match(r"^(\d{4})Q([1-4])$", s or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def qi(k):
    return k[0] * 4 + k[1] - 1


def qk(i):
    return (i // 4, i % 4 + 1)


def qs(k):
    return "%dQ%d" % k


def qadd(k, n):
    return qk(qi(k) + n)


def era_of(k):
    if k <= BREAK_LAST_DUKE:
        return "duke"
    if k >= BREAK_FIRST_CUR:
        return "current"
    return None


# ------------------------------------------------------------------------------------------------------------------------
# the xlsx reader: zipfile and ElementTree only; shared strings, cached values, hidden rows and columns
# ------------------------------------------------------------------------------------------------------------------------
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
NS_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


class Sheet(object):
    def __init__(self, name, state="visible"):
        self.name, self.state = name, state
        self.cells = {}                       # row number -> {col index -> (kind, text)}; kind in empty, numeric, text, nocache
        self.hidden_rows, self.hidden_cols = set(), set()

    def max_col(self):
        return max([max(r) for r in self.cells.values() if r] or [-1]) + 1


def col_index(ref):
    n = 0
    for ch in ref:
        if not ch.isalpha():
            break
        n = n * 26 + ord(ch.upper()) - 64
    return n - 1


def _text_of(si):
    """The plain text of a shared-string item: its <t> runs, never the phonetic runs."""
    out = []
    for ch in si:
        if ch.tag == NS + "t":
            out.append(ch.text or "")
        elif ch.tag == NS + "r":
            for t in ch:
                if t.tag == NS + "t":
                    out.append(t.text or "")
    return "".join(out)


def classify(c, sst):
    """(kind, text) of one <c> element from its attributes; no value is converted."""
    t = c.get("t")
    has_f = c.find(NS + "f") is not None
    v = c.find(NS + "v")
    vt = v.text if (v is not None and v.text is not None) else None
    if t == "inlineStr":
        is_ = c.find(NS + "is")
        s = _text_of(is_) if is_ is not None else ""
        return ("text", s) if s != "" else ("empty", "")
    if t == "s":
        if vt is None or vt.strip() == "":
            return ("nocache", "") if has_f else ("empty", "")
        try:
            i = int(vt.strip()) + (1 if M("g1_sst_off") else 0)
            s = sst[i]
        except (ValueError, IndexError):
            return ("text", "")
        return ("text", s) if s != "" else ("empty", "")
    if t in ("str", "b", "e", "d"):
        if vt is None or vt == "":
            return ("nocache", "") if has_f else ("empty", "")
        return ("text", vt)
    if vt is None or vt.strip() == "":
        return ("nocache", "") if has_f else ("empty", "")
    return ("numeric", vt.strip())


def read_workbook(data):
    """{sheet name: Sheet}, in workbook order. Raises WbError if the bytes are not a readable xlsx."""
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        names = set(z.namelist())
        if "xl/workbook.xml" not in names:
            raise WbError("no xl/workbook.xml")
        wbx = ET.fromstring(z.read("xl/workbook.xml"))
        rels = {}
        if "xl/_rels/workbook.xml.rels" in names:
            for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels")):
                rels[r.get("Id")] = r.get("Target")
        sst = []
        if "xl/sharedStrings.xml" in names:
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")):
                if si.tag == NS + "si":
                    sst.append(_text_of(si))
        out = {}
        for s in wbx.iter(NS + "sheet"):
            name, target = s.get("name"), rels.get(s.get(NS_R + "id"))
            if not name or not target:
                raise WbError("a sheet without a name or a relationship")
            path = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join("xl", target))
            if path not in names:
                raise WbError("sheet part missing: " + name)
            sh = Sheet(name, s.get("state") or "visible")
            root = ET.fromstring(z.read(path))
            for cols in root.iter(NS + "cols"):
                for col in cols:
                    if (col.get("hidden") or "") in ("1", "true"):
                        lo, hi = int(col.get("min", "1")), min(int(col.get("max", "1")), 16384)
                        if not M("g1_hidden_ignored"):
                            sh.hidden_cols.update(range(lo - 1, hi))
            nxt = 0
            for row in root.iter(NS + "row"):
                nxt = int(row.get("r")) if row.get("r") else nxt + 1
                if (row.get("hidden") or "") in ("1", "true"):
                    sh.hidden_rows.add(nxt)
                cur = -1
                cells = {}
                for c in row:
                    if c.tag != NS + "c":
                        continue
                    ref = c.get("r")
                    cur = col_index(ref) if ref else cur + 1
                    cells[cur] = classify(c, sst)
                if cells:
                    sh.cells[nxt] = cells
            out[name] = sh
        return out
    except (zipfile.BadZipFile, ET.ParseError, KeyError, ValueError) as e:
        raise WbError("%s: %s" % (type(e).__name__, e))


# ------------------------------------------------------------------------------------------------------------------------
# layout: tables, keys, the HALT faults
# ------------------------------------------------------------------------------------------------------------------------
class Table(object):
    def __init__(self, name):
        self.name = name
        self.header_row = None
        self.header = {}                      # col index -> header text
        self.cols = {}                        # header text -> col index (first occurrence)
        self.dups = []
        self.rows = []                        # [(row number, {col: (kind, text)})] below the header with any non-empty cell
        self.key_desc = None                  # ("col", name, format) or ("pair", yname, qname)
        self.keys = []                        # [(y, q) or None] aligned with rows
        self.faults = []


def _nonempty(cells):
    return {c: v for c, v in cells.items() if v[0] != "empty"}


def header_row_of(sheet, required):
    rows = sorted(sheet.cells)
    for r in rows[:15]:
        texts = {v[1].strip() for v in sheet.cells[r].values() if v[0] == "text"}
        if required and any(n in texts for n in required):
            return r
    for r in rows:
        if sum(1 for v in sheet.cells[r].values() if v[0] == "text") >= 2:
            return r
    return rows[0] if rows else None


def find_key(header, rows):
    for col in sorted(header):
        vals = [cells.get(col, ("empty", "")) for _, cells in rows]
        ne = [v for v in vals if v[0] != "empty"]
        if ne and all(v[0] == "text" and parse_key(v[1]) for v in ne):
            return ("col", header[col], key_format(ne[0][1]), col)
    y = next((c for c, h in header.items() if h.strip().lower() in ("year", "yr")), None)
    q = next((c for c, h in header.items() if h.strip().lower() in ("quarter", "qtr", "q")), None)
    if y is not None and q is not None:
        ok = all(cells.get(y, ("empty",))[0] == "numeric" and cells.get(q, ("empty",))[0] == "numeric" for _, cells in rows if _nonempty(cells))
        if ok and rows:
            return ("pair", header[y], header[q], (y, q))
    return None


def make_table(sheet, required):
    t = Table(sheet.name)
    hr = header_row_of(sheet, required)
    if hr is None:
        t.faults.append("sheet %s is empty" % sheet.name)
        return t
    t.header_row = hr
    for c, v in sorted(sheet.cells[hr].items()):
        if v[0] == "text" and v[1].strip():
            nm = v[1].strip()
            t.header[c] = nm
            if nm in t.cols:
                t.dups.append(nm)
            else:
                t.cols[nm] = c
    t.rows = [(r, sheet.cells[r]) for r in sorted(sheet.cells) if r > hr and _nonempty(sheet.cells[r])]
    for nm in required:
        if nm not in t.cols:
            t.faults.append("sheet %s lacks the required column %s" % (sheet.name, nm))
        elif nm in t.dups:
            t.faults.append("sheet %s holds the column %s more than once" % (sheet.name, nm))
    k = find_key(t.header, t.rows)
    if k is None:
        t.faults.append("sheet %s: no quarter key column (a column whose every cell parses as YYYYQn, or year and quarter columns)" % sheet.name)
        return t
    t.key_desc = k
    for r, cells in t.rows:
        if k[0] == "col":
            v = cells.get(k[3], ("empty", ""))
            key = parse_key(v[1]) if v[0] == "text" else None
        else:
            try:
                key = (int(Decimal(cells[k[3][0]][1])), int(Decimal(cells[k[3][1]][1])))
            except (KeyError, decimal.InvalidOperation, ValueError):
                key = None
        t.keys.append(key)
        if key is None:
            t.faults.append("sheet %s row %d has no parsable quarter key" % (sheet.name, r))
    return t


def key_faults(t, n_expected, first, last):
    out = []
    ks = [k for k in t.keys if k is not None]
    if len(set(ks)) != len(ks) and not M("g2_dup_ok"):
        out.append("sheet %s: duplicate quarter keys" % t.name)
    if len(t.rows) != n_expected and not M("g2_count_lax"):
        out.append("sheet %s: %d data rows, %d expected" % (t.name, len(t.rows), n_expected))
    if ks and not M("g2_count_lax"):
        if ks[0] != first or ks[-1] != last:
            out.append("sheet %s: keys run %s to %s, expected %s to %s" % (t.name, qs(ks[0]), qs(ks[-1]), qs(first), qs(last)))
    if ks and any(qi(b) - qi(a) != 1 for a, b in zip(ks, ks[1:])) and not (M("g2_gap_ok") or M("g2_dup_ok")):
        out.append("sheet %s: quarter keys are not consecutive" % t.name)
    return out


class Layout(object):
    def __init__(self):
        self.sheets = {}
        self.tables = {}
        self.faults = []
        self.series = {}                      # series name -> {(y, q): (kind, text)}


def analyse(data):
    """Read the workbook and test the structure. Layout.faults is the HALT list (exit 4)."""
    lay = Layout()
    wb = read_workbook(data)
    lay.sheets = wb
    for name in SHEETS:
        if name not in wb and not M("g2_sheet_ok"):
            lay.faults.append("missing sheet %s" % name)
    for name in (SH_DUKE, SH_CUR):
        if name not in wb:
            continue
        t = make_table(wb[name], REQUIRED[name])
        lay.tables[name] = t
        lay.faults.extend(t.faults)
        if t.key_desc is not None:
            first, last = DUKE_KEYS if name == SH_DUKE else CUR_KEYS
            lay.faults.extend(key_faults(t, N_DUKE if name == SH_DUKE else N_CUR, first, last))
        if name == SH_CUR and any(k == (2020, 2) for k in t.keys):
            lay.faults.append("sheet %s holds 2020Q2, which must be absent" % name)
    for sname, (tn, col, era, hz) in SERIES.items():
        t = lay.tables.get(tn)
        if t is None or col not in t.cols or t.key_desc is None:
            continue
        c = t.cols[col]
        lay.series[sname] = {k: cells.get(c, ("empty", "")) for k, (r, cells) in zip(t.keys, t.rows) if k is not None}
    if M("g2_empty_halts"):
        for sname, cells in lay.series.items():
            exp_empty = {(2019, 1), (2020, 1)} if sname.startswith("DUKE") else set()
            if {k for k, v in cells.items() if v[0] != "numeric"} - exp_empty:
                lay.faults.append("%s has an empty cell (mutant: a halt)" % sname)
    return lay


# ------------------------------------------------------------------------------------------------------------------------
# values (R8): Decimal, never float; each cell rounded half-even to 6 decimals; the statistic is the exact difference
# ------------------------------------------------------------------------------------------------------------------------
Q6 = Decimal("0.000001")


def to_dec(kind, text):
    """The Decimal of one cell. Only a numeric cell qualifies: empty, text and formula-without-value cells are undefined (missing is never zero)."""
    STATS["conv"] += 1
    if kind == "numeric" or (M("g1_text_ok") and kind == "text"):
        pass
    elif M("g1_nocache_ok") and kind == "nocache":
        return Decimal(0)
    elif M("g1_empty_zero") and kind == "empty":
        return Decimal(0)
    else:
        raise Undef(kind)
    try:
        d = Decimal(float(text)) if M("g1_float") else Decimal(text.strip())
    except (decimal.InvalidOperation, ValueError):
        raise Undef("not a number")
    if not d.is_finite():
        raise Undef("not finite")
    return d


def r6(d):
    try:
        return d.quantize(Q6, rounding=decimal.ROUND_HALF_UP if M("g1_half_up") else decimal.ROUND_HALF_EVEN)
    except decimal.InvalidOperation:
        raise Undef("out of range")


def cell_r6(cell):
    d = to_dec(*cell)
    return d if M("g1_no_round") else r6(d)


def fmt6(d):
    if d is None:
        return ""
    s = format(d.quantize(Q6, rounding=decimal.ROUND_HALF_EVEN), "f")
    return s[1:] if s.startswith("-") and Decimal(s) == 0 else s


def fmt_n(d, n):
    s = format(d.quantize(Decimal(1).scaleb(-n), rounding=decimal.ROUND_HALF_EVEN), "f")
    return s[1:] if s.startswith("-") and Decimal(s) == 0 else s


def signed2(d):
    s = fmt_n(d, 2)
    return s if s.startswith("-") else "+" + s


def sign_of(stat, start=None, end=None):
    """RISE if stat >= +0.10, FALL if stat <= -0.10, ZERO inside (4.6 SIGN). The sign is taken from the exact difference of the rounded cells."""
    zone = Decimal("0.15") if M("g3_wide") else ZONE
    if M("g3_float") and start is not None:
        f = float(end) - float(start)
        return "RISE" if f >= 0.1 else "FALL" if f <= -0.1 else "ZERO"
    if M("g3_nozone"):
        return "RISE" if stat > 0 else "FALL" if stat < 0 else "ZERO"
    if M("g3_gt"):
        return "RISE" if stat > zone else "FALL" if stat <= -zone else "ZERO"
    if M("g3_neg_lt"):
        return "RISE" if stat >= zone else "FALL" if stat < -zone else "ZERO"
    return "RISE" if stat >= zone else "FALL" if stat <= -zone else "ZERO"


def spf_value(vdir=None):
    """The SPF's +0.1543 is fixed text of the 4.6 block and is never read from a file (the mutant looks for a file)."""
    if M("g5_spf_file") and vdir and os.path.isfile(os.path.join(vdir, "spf.txt")):
        return read_file(os.path.join(vdir, "spf.txt"), "r").strip()
    if M("g5_spf_wrong"):
        return "0.15"
    return SPF_STAT


def direction_of(sid, sign, void):
    if sid != "E1":
        return "na" if not M("g5_e2_dir") else {"RISE": "SAME", "FALL": "OPPOSITE", "ZERO": "FLAT"}.get(sign, "none")
    if void and not M("g4_dir_on_void"):
        return "none"
    if M("g5_map_swap"):
        return {"RISE": "OPPOSITE", "FALL": "SAME", "ZERO": "FLAT"}.get(sign, "none")
    if M("g5_zero_same"):
        return {"RISE": "SAME", "FALL": "OPPOSITE", "ZERO": "SAME"}.get(sign, "none")
    if M("g5_agrees_word"):
        return {"RISE": "AGREES", "FALL": "DISAGREES", "ZERO": "FLAT"}.get(sign, "none")
    return {"RISE": "SAME", "FALL": "OPPOSITE", "ZERO": "FLAT"}.get(sign, "none")


def unit_odd(cells):
    """True if any numeric cell of the used current column lies outside -20..40 (inclusive limits are not odd)."""
    lo, hi = (UNIT_LO, UNIT_HI) if not M("g4_unit_lax") else (Decimal("-20.001"), Decimal("40.001"))
    for cell in cells.values():
        if cell[0] != "numeric":
            continue
        try:
            d = to_dec(*cell)
        except Undef:
            continue
        if (M("g4_unit_edge") and (d <= lo or d >= hi)) or (not M("g4_unit_edge") and (d < lo or d > hi)):
            return True
    return False


def change_between(eras, s, e):
    """The exact difference of two rounded cells of ONE era. A window across the 2020 break raises CrossBreak. eras: {'duke': cells, 'current': cells}."""
    es, ee = era_of(s), era_of(e)
    if es is None or ee is None:
        raise CrossBreak("%s or %s lies in the missing 2020Q2" % (qs(s), qs(e)))
    if es != ee and not M("g7_cross_ok"):
        raise CrossBreak("%s to %s spans the 2020 break" % (qs(s), qs(e)))
    a = eras[es].get(s)
    b = eras[ee].get(e)
    if a is None or b is None:
        raise Undef("endpoint quarter absent")
    ra, rb = cell_r6(a), cell_r6(b)
    return ra, rb, rb - ra


def statement(sid, horizon, sname, cells, start, end, pins, wb_sha, vintage, version=1, vdir=None):
    """One registered row (a dict of the 19 columns). VOID order: endpoint_undefined, unit_odd. A VOID is not a FAIL."""
    ra = rb = stat = None
    reason = "none"
    try:
        ra = cell_r6(cells[start]) if start in cells else None
        if ra is None:
            raise Undef("absent")
    except Undef:
        ra = None
    try:
        rb = cell_r6(cells[end]) if end in cells else None
        if rb is None:
            raise Undef("absent")
    except Undef:
        rb = None
    if M("g4_void_fail") and (ra is None or rb is None):
        raise DataError("an empty endpoint is a FAIL (mutant)")
    if M("g6_pin_in_stat"):
        for sn, q, p in PINS:
            if sn == sname and parse_q(q) == end:
                rb = Decimal(p)
            if sn == sname and parse_q(q) == start:
                ra = Decimal(p)
    odd_first = M("g4_order_swapped") and unit_odd(cells)
    if odd_first:
        reason = "unit_odd"
    elif ra is None or rb is None:
        reason = "endpoint_undefined"
    elif unit_odd(cells):
        reason = "unit_odd"
    if ra is not None and rb is not None:
        stat = rb - ra
        if M("g1_diff_round"):
            stat = stat.quantize(Decimal("0.01"), rounding=decimal.ROUND_HALF_EVEN)
    sign = sign_of(stat, ra, rb) if stat is not None else "none"
    if M("g4_sign_on_undef") and stat is None:
        sign = "ZERO"
    void = reason != "none"
    return {"statement_id": sid, "version": str(version), "superseded": "no", "horizon": horizon, "series": sname, "vintage": vintage, "workbook_sha256": wb_sha,
            "start_quarter": qs(start), "end_quarter": qs(end), "exp_start": fmt6(ra), "exp_end": fmt6(rb), "stat_pp": fmt6(stat), "sign": sign, "void_reason": reason,
            "blind": "full", "pins": pins, "spf_stat_pp": spf_value(vdir) if sid == "E1" else "", "spf_direction": direction_of(sid, sign, void),
            "prereg_sha256": prereg_sha_out()}


# ------------------------------------------------------------------------------------------------------------------------
# the registered block and its hash (R5): the script refuses to write registered.csv unless its constants reproduce the hash
# ------------------------------------------------------------------------------------------------------------------------
def prereg_text():
    return "\n".join(PREREG_LINES) + "\n"


def prereg_ok():
    if M("g8_no_refuse"):
        return True
    t = prereg_text().encode("utf-8")
    return sha256_of(t) == SPEC_PREREG_SHA256 and len(t) == SPEC_PREREG_BYTES


def prereg_sha_out():
    if M("g8_hash_wrong"):
        return sha256_of(prereg_text().rstrip("\n").encode("utf-8"))
    return sha256_of(prereg_text().encode("utf-8"))


# ------------------------------------------------------------------------------------------------------------------------
# pins (4.6 PIN): never used in a statistic
# ------------------------------------------------------------------------------------------------------------------------
def pin_status(series):
    """('match' | 'near' | 'unit_error', [(id, workbook text, pin, verdict)])."""
    tol = PIN_TOL
    if M("g6_tol_wide"):
        tol = Decimal("0.06")
    out, worst = [], "match"
    for sname, q, pin in PINS:
        cell = series.get(sname, {}).get(parse_q(q))
        pid = "%s_%s" % (sname, q)
        try:
            if not cell:
                raise Undef("absent")
            d = to_dec(*cell)
        except Undef:
            out.append((pid, "undefined", pin, "near"))
            worst = "near" if worst == "match" else worst
            continue
        p = Decimal(pin)
        ratio = d / p
        hi_bad = ratio > PIN_HI if M("g6_factor_gt") else ratio >= PIN_HI
        lo_bad = False if M("g6_no_fraction") else (ratio < PIN_LO if M("g6_factor_low") else ratio <= PIN_LO)
        diff = abs(d - p)
        near = diff >= tol if M("g6_tol_strict") else diff > tol
        if hi_bad or lo_bad:
            out.append((pid, text_of(cell), pin, "unit_error"))
            worst = "unit_error"
        elif near:
            out.append((pid, text_of(cell), pin, "near"))
            worst = "near" if worst == "match" else worst
        else:
            out.append((pid, text_of(cell), pin, "match"))
    if M("g6_near_silent") and worst == "near":
        worst = "match"
    return worst, out


def text_of(cell):
    return cell[1].strip() if cell[0] == "numeric" else cell[0]


# ------------------------------------------------------------------------------------------------------------------------
# windows and the described ranges (2.2)
# ------------------------------------------------------------------------------------------------------------------------
def y_ends():
    lo, hi = Y_ENDS
    if M("g7_y_lo_out"):
        lo = (2003, 4)
    if M("g7_y_lo_in"):
        lo = (2004, 2)
    if M("g7_y_hi_out"):
        hi = (2019, 4)
    if M("g7_y_hi_in"):
        hi = (2020, 2)
    return [qk(i) for i in range(qi(lo), qi(hi) + 1)]


def yc_ends():
    lo, hi = YC_ENDS
    if M("g7_yc_lo_out"):
        lo = (2022, 2)
    if M("g7_yc_lo_in"):
        lo = (2022, 4)
    if M("g7_yc_hi_out"):
        hi = (2026, 2)
    if M("g7_yc_hi_in"):
        hi = (2026, 4)
    return [qk(i) for i in range(qi(lo), qi(hi) + 1)]


def window_changes(eras, ends, exclude=()):
    """[(start, end, change)] for every end quarter whose start (eight calendar quarters earlier) and end cells are both numeric. The start is found by calendar arithmetic."""
    out = []
    keys = sorted(set(eras["duke"]) | set(eras["current"]))
    for e in ends:
        if e in exclude:
            continue
        if M("g7_row_pos"):
            cells = eras[era_of(e) or "duke"]
            ks = sorted(cells)
            if e not in cells:
                continue
            i = ks.index(e)
            s = ks[i - LAG] if i >= LAG else None
            if s is None:
                continue
        else:
            s = qadd(e, -LAG)
        try:
            a, b, c = change_between(eras, s, e)
        except (Undef, CrossBreak):
            continue
        out.append((s, e, c))
    return out


def yardstick_rows(series):
    """The four rows of yardstick.csv. Y10, Y12: Duke-era changes with end quarters 2004Q1 to 2020Q1. YC10, YC12: current-series changes with end quarters 2022Q3 to 2026Q3 minus the registered window."""
    rows = []
    for yid, hz, dn, cn in (("Y10", "10y", "DUKE10", "CUR10"), ("Y12", "12m", "DUKE12", "CUR12")):
        eras = {"duke": series.get(cn if M("g7_duke_from_current") else dn, {}), "current": {}}
        ends = y_ends()
        ch = window_changes(eras, ends)
        rows.append(yrow(yid, hz, ends, ch, Y_SPANS))
    for yid, hz, cn in (("YC10", "10y", "CUR10"), ("YC12", "12m", "CUR12")):
        eras = {"duke": {}, "current": series.get(cn, {})}
        ends = yc_ends()
        ex = () if M("g7_yc_keeps_window") else (WINDOW[1],)
        ch = window_changes(eras, ends, exclude=ex)
        rows.append(yrow(yid, hz, ends, ch, YC_SPANS))
    return rows


def yrow(yid, hz, ends, ch, spans):
    vals = [c for _, _, c in ch]
    return {"yardstick": yid, "horizon": hz, "first_end_quarter": qs(ends[0]), "last_end_quarter": qs(ends[-1]), "n_nominal": str(len(ends)), "n_defined": str(len(ch)),
            "min_change_pp": fmt6(min(vals)) if vals else "", "max_change_pp": fmt6(max(vals)) if vals else "", "max_disjoint_spans": str(spans)}


# ------------------------------------------------------------------------------------------------------------------------
# dates and dictionary text (no S&P value is read here)
# ------------------------------------------------------------------------------------------------------------------------
def serial_date(text):
    try:
        n = int(Decimal(text))
    except (decimal.InvalidOperation, ValueError):
        return None
    if not 30000 <= n <= 80000:
        return None
    return (dt.date(1899, 12, 30) + dt.timedelta(days=n)).isoformat()


def date_text(cell):
    kind, text = cell
    if kind == "numeric":
        return serial_date(text) or text
    if kind != "text":
        return ""
    t = text.strip()
    for f in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y", "%m/%d/%y", "%d %b %Y", "%d %B %Y", "%B %d, %Y", "%b %d, %Y", "%d-%b-%Y", "%d-%b-%y"):
        try:
            return dt.datetime.strptime(t, f).date().isoformat()
        except ValueError:
            pass
    return t


def survey_dates(lay):
    """{(y, q): (open, close)} from CFO_survey_dates, or {} if the sheet does not give them. The open and close columns are found by header words."""
    sh = lay.sheets.get(SH_DATES)
    if sh is None:
        return {}, "no CFO_survey_dates sheet"
    t = make_table(sh, ())
    if t.key_desc is None or t.faults:
        return {}, "CFO_survey_dates has no quarter key"
    low = {c: h.lower() for c, h in t.header.items()}
    kc = t.key_desc[3] if t.key_desc[0] == "col" else None
    op = next((c for c, h in low.items() if any(w in h for w in ("open", "start", "begin", "launch"))), None)
    cl = next((c for c, h in low.items() if any(w in h for w in ("close", "end", "final"))), None)
    if op is None or cl is None:
        rest = [c for c in sorted(t.header) if c != kc and not (t.key_desc[0] == "pair" and c in t.key_desc[3])]
        if len(rest) < 2:
            return {}, "CFO_survey_dates has no open and close columns"
        op, cl = rest[0], rest[1]
    out = {}
    for k, (r, cells) in zip(t.keys, t.rows):
        if k is not None:
            out[k] = (date_text(cells.get(op, ("empty", ""))), date_text(cells.get(cl, ("empty", ""))))
    return out, "open=%s close=%s" % (t.header[op], t.header[cl])


def clip_words(s, n=15):
    w = s.split()
    return " ".join(w) if len(w) <= n else " ".join(w[:n]) + " [...]"


def dict_lines(lay):
    """(duke lines, current lines): the dictionary rows that name the S&P variables used, each a text of its non-empty cells (clipped to 15 words)."""
    duke_names = {"sp_10_low", "sp_10_exp", "sp_10_high", "sp_1_low", "sp_1_exp", "sp_1_high"}
    out = ([], [])
    picks = ((SH_DUKE_D, lambda t: t in duke_names), (SH_CUR_D, lambda t: (t.startswith("sp_12mo") or t.startswith("sp_10yr")) and "med" not in t))
    for i, (sn, pick) in enumerate(picks):
        sh = lay.sheets.get(sn)
        if sh is None:
            continue
        for r in sorted(sh.cells):
            cells = sh.cells[r]
            texts = [v[1].strip() for c, v in sorted(cells.items()) if v[0] == "text" and v[1].strip()]
            if any(pick(t.lower()) for t in texts):
                out[i].append(clip_words(" | ".join(texts)))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# guards on what is written: headers, keys, values, leaks, wording (the writer refuses what bin/check.sh M29 would flag)
# ------------------------------------------------------------------------------------------------------------------------
def source_line(vintage, what, synthetic=False):
    pre = "SYNTHETIC fixture built in code, not survey data; layout only. " if synthetic else ""
    return "# source: %s%s, Richmond Fed historical workbook %s, vintage %s; %s" % (pre, CREDIT, WB_NAME, vintage, what)


def csv_problems(name, text):
    """Header, keys, allowed values, hex fields, verdict words, leaks and the credit line of one CSV text."""
    out = []
    lines = text.split("\n")
    first = lines[0] if lines else ""
    if CREDIT not in first or not first.startswith("# source:"):
        if not M("g12_credit_ok"):
            out.append("%s: the first line is not a `# source:` line that credits the survey" % name)
    body = [l for l in lines if l.strip() and not l.startswith("# source:")]
    if M("g12_source_as_header"):
        body = [l for l in lines if l.strip()]
    if not body:
        return out + ["%s: no header" % name]
    head = next(csv.reader([body[0]]))
    want = ALLOW.get(name)
    if want is None:
        return out + ["%s: not one of the four allowlisted files" % name]
    if head != want and not M("g12_header_lax"):
        out.append("%s: the header is not the allowlist (%s)" % (name, ",".join(head)[:80]))
    rows = [dict(zip(head, r)) for r in csv.reader(body[1:])]
    k = KEYS[name]
    if all(c in head for c in k):
        seen = set()
        for r in rows:
            key = tuple(r[c] for c in k)
            if key in seen and not M("g12_dup_ok"):
                out.append("%s: duplicate key %s" % (name, "/".join(key)))
            seen.add(key)
    for col, ok in ALLOWED_VALUES.get(name, {}).items():
        bad = sorted({r.get(col, "") for r in rows if r.get(col, "") not in ok})
        if bad:
            out.append("%s: %s holds a value outside the allowed list: %s" % (name, col, ", ".join(bad[:4])))
    for col in ("workbook_sha256", "prereg_sha256"):
        bad = [r[col] for r in rows if col in r and not HEX64.match(r[col])]
        if bad:
            out.append("%s: %s is not 64 hex digits" % (name, col))
    for col in ("start_quarter", "end_quarter", "quarter", "first_end_quarter", "last_end_quarter"):
        bad = [r[col] for r in rows if col in r and not QRX.match(r[col])]
        if bad:
            out.append("%s: %s is not YYYYQn: %s" % (name, col, bad[0]))
    return out


def leak_problems(name, text):
    out = []
    if re.search(r"/Users/|/private/|~/", text) and not M("g12_users_ok"):
        out.append("%s: holds a local path" % name)
    if "@" in text and not M("g12_at_ok"):
        out.append("%s: holds an at sign" % name)
    if VERDICT_RX.search(text) and not M("g9_verdict_off"):
        out.append("%s: holds a banned verdict word" % name)
    return out


def wording_problems(text):
    """The patterns of section 7 applied to README.md. No exemption: a banned pattern anywhere, dictionary lines included, is a problem."""
    hits = []
    if not M("g9_causal_off"):
        hits += [m.group(0) for m in CAUSAL_RX.finditer(text)]
    if not M("g9_extra_off"):
        hits += [m.group(0) for m in EXTRA_RX.finditer(text)]
    for nm, rx in ADD_RXS:
        if M("g9_%s_off" % nm):
            continue
        hits += [m.group(0) for m in rx.finditer(text)]
    return sorted({re.sub(r"\s+", " ", h.lower()) for h in hits})


def readme_problems(text):
    out = []
    w = wording_problems(text)
    if w:
        out.append("README.md: banned wording (R6): " + ", ".join(w[:6]))
    if not M("g9_required_lax"):
        for tag, s in REQUIRED_SENTENCES:
            if s not in text:
                out.append("README.md lacks the required sentence %s verbatim" % tag)
    out += leak_problems("README.md", text)
    return out


def registered_problems(rows):
    """Semantic rules of registered.csv: one live row per statement, versions, the hash, the SPF text, VOID consistency."""
    out = []
    live = {}
    seen = set()
    for r in rows:
        sid = r.get("statement_id")
        key = (sid, r.get("version"))
        if key in seen:
            out.append("registered.csv: duplicate (statement_id, version) %s" % "/".join(map(str, key)))
        seen.add(key)
        if not (r.get("version", "").isdigit() and int(r["version"]) >= 1):
            out.append("registered.csv: version is not a positive integer")
        if r.get("prereg_sha256") != SPEC_PREREG_SHA256:
            out.append("registered.csv: %s prereg_sha256 is not the 4.6 hash" % sid)
        if r.get("superseded") == "no":
            live[sid] = live.get(sid, 0) + 1
        if sid == "E1" and r.get("spf_stat_pp") != SPF_STAT:
            out.append("registered.csv: E1 spf_stat_pp is not %s" % SPF_STAT)
        if sid == "E2" and (r.get("spf_stat_pp") != "" or r.get("spf_direction") != "na"):
            out.append("registered.csv: E2 must have an empty spf_stat_pp and spf_direction na")
        void = r.get("void_reason") != "none"
        if r.get("stat_pp") == "" and r.get("void_reason") != "endpoint_undefined":
            out.append("registered.csv: %s has an empty stat_pp without endpoint_undefined" % sid)
        if r.get("stat_pp") == "" and r.get("sign") != "none":
            out.append("registered.csv: %s has a sign on an undefined statistic" % sid)
        if r.get("stat_pp") != "" and r.get("sign") == "none":
            out.append("registered.csv: %s has no sign on a defined statistic" % sid)
        if sid == "E1" and void and r.get("spf_direction") != "none":
            out.append("registered.csv: a VOID E1 row must have spf_direction none")
    if not M("g8_validator_lax"):
        for sid in ("E1", "E2"):
            if live.get(sid, 0) != 1:
                out.append("registered.csv: %s has %d non-superseded rows, must have exactly one" % (sid, live.get(sid, 0)))
    return out


def folder_problems(files):
    """files: {name: text or bytes} of a folder that is meant to be the committed one. Raw files, local paths, at signs, a path.csv, a fifth name, headers, keys, values."""
    out = []
    for n, x in sorted(files.items()):
        b = x if isinstance(x, bytes) else x.encode("utf-8")
        text = b.decode("utf-8", errors="replace")
        low = n.lower()
        if n == ".DS_Store":
            continue
        if (M("g12_path_ok") and n == "path.csv") or (M("g12_xlsx_ok") and low.endswith(".xlsx")) or (M("g12_json_ok") and low.endswith(".json")) or (M("g12_fifth_ok") and n.endswith(".csv")):
            out += leak_problems(n, text)
            continue
        if (low.endswith((".xlsx", ".xls", ".zip", ".htm", ".html", ".gz", ".pdf", ".json")) or n.upper().startswith("STOP") or b[:2] == b"PK"):
            out.append("%s: a raw file (workbook, zip, json, page or STOP file) in a committed folder" % n)
            continue
        if n == "path.csv":
            out.append("path.csv: the full quarterly series is local and gitignored (R1-15), never in a committed list")
            continue
        if n not in COMMITTED and n != "path.csv":
            out.append("%s: not one of the four committed names" % n)
            continue
        out += leak_problems(n, text)
        if n.endswith(".csv"):
            out += csv_problems(n, text)
    return out


# ------------------------------------------------------------------------------------------------------------------------
# a synthetic workbook, in memory with zipfile (the fixture of the dry stage and of every selftest)
# ------------------------------------------------------------------------------------------------------------------------
DUKE_HEAD = ("quarter", "sp_10_low", "sp_10_exp", "sp_10_high", "sp_1_low", "sp_1_exp", "sp_1_high")
CUR_HEAD = ("quarter", "sp_12moexp_1", "sp_12moexp_2", "sp_12moexp_3", "sp_10yrexp_1", "sp_10yrexp_2", "sp_10yrexp_3",
            "sp_12moexp_1_med", "sp_12moexp_2_med", "sp_12moexp_3_med", "sp_10yrexp_1_med", "sp_10yrexp_2_med", "sp_10yrexp_3_med")
PIN_PLANT = {("CFO_SP500", "sp_12moexp_2", (2026, 2)): "7.8", ("CFO_SP500", "sp_12moexp_2", (2026, 3)): "7.9",
             ("CFO_SP500", "sp_10yrexp_2", (2026, 2)): "9.7000000000000002", ("CFO_SP500", "sp_10yrexp_2", (2026, 3)): "9.6"}
SYN_EPOCH = (2026, 11, 1, 0, 0, 0)


def col_letter(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def q_list(first, last, drop=()):
    return [qk(i) for i in range(qi(first), qi(last) + 1) if qk(i) not in drop]


def base_value(i, j):
    """A deterministic two-decimal text between 4.00 and 10.99: the fixture's S&P cells (only the fixture's)."""
    return "%d.%02d" % (4 + ((i * 37 + j * 11) % 700) // 100, ((i * 37 + j * 11) % 700) % 100)


def synth_sheets(over=None, duke_keys=None, cur_keys=None, omit_sheet=None, omit_col=None, rename_col=None, key_fmt="{y}Q{q}", pins=True):
    """{sheet: list of rows}, each row a list of cell specs: None (empty), ('n', text), ('s', text), ('f',), ('fv', text), ('is', text)."""
    over = over or {}
    dk = duke_keys if duke_keys is not None else q_list(*DUKE_KEYS)
    ck = cur_keys if cur_keys is not None else q_list(*CUR_KEYS)

    def key(k):
        return ("s", key_fmt.format(y=k[0], q=k[1]))

    def cell(sheet, col, k, v):
        spec = over.get((sheet, col, k), v)
        if spec is None:
            return None
        if isinstance(spec, str):
            return ("n", spec)
        return spec
    sheets = {}
    rows = [[("s", h) for h in DUKE_HEAD]]
    for i, k in enumerate(dk):
        r = [key(k)]
        for j, h in enumerate(DUKE_HEAD[1:]):
            v = base_value(i, j + 1)
            if h in ("sp_10_exp", "sp_1_exp") and k in ((2019, 1), (2020, 1)):
                v = None
            r.append(cell(SH_DUKE, h, k, v))
        rows.append(r)
    sheets[SH_DUKE] = rows
    rows = [[("s", h) for h in CUR_HEAD]]
    for i, k in enumerate(ck):
        r = [key(k)]
        for j, h in enumerate(CUR_HEAD[1:]):
            v = PIN_PLANT.get((SH_CUR, h, k)) if pins else None
            if v is None:
                v = base_value(i + 100, j + 1)
            r.append(cell(SH_CUR, h, k, v))
        rows.append(r)
    sheets[SH_CUR] = rows
    sheets[SH_DUKE_D] = [[("s", "variable"), ("s", "description")]] + [[("s", n), ("s", "fixture dictionary line for %s over the next period" % n)] for n in DUKE_HEAD[1:]]
    sheets[SH_CUR_D] = [[("s", "variable"), ("s", "description")], [("s", "Percent change (mean)")]] + [[("s", n), ("s", "fixture expectation for S&P return over the next period, band %s" % n[-1])] for n in CUR_HEAD[1:7]]
    d0 = dt.date(1899, 12, 30)
    rows = [[("s", "quarter"), ("s", "field open"), ("s", "field close")]]
    for k in q_list((2020, 2), (2026, 3)):
        o = dt.date(k[0], (k[1] - 1) * 3 + 2, 10)
        rows.append([("s", "%dQ%d" % k), ("n", str((o - d0).days)), ("n", str((o + dt.timedelta(days=17) - d0).days))])
    sheets[SH_DATES] = rows
    if omit_sheet:
        sheets.pop(omit_sheet, None)
    if omit_col or rename_col:
        for sn, rows in sheets.items():
            if not rows:
                continue
            head = rows[0]
            for j, c in enumerate(head):
                if c and c[0] == "s" and omit_col and c[1] == omit_col:
                    for r in rows:
                        r[j] = None
                    head[j] = None
                if c and c[0] == "s" and rename_col and c[1] == rename_col[0]:
                    head[j] = ("s", rename_col[1])
    return sheets


def write_xlsx(sheets, hidden_cols=None, hidden_rows=None, pad_to=None, order=None):
    """The xlsx bytes of {sheet: rows}. Deterministic (fixed zip times). pad_to: grow the file to exactly this size with a stored member."""
    hidden_cols = hidden_cols or {}
    hidden_rows = hidden_rows or {}
    names = [n for n in (order or SHEETS) if n in sheets]
    sst, sidx = [], {}

    def sid(s):
        if s not in sidx:
            sidx[s] = len(sst)
            sst.append(s)
        return sidx[s]

    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    parts = {}
    for n, sname in enumerate(names, 1):
        rows = sheets[sname]
        x = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">']
        hc = sorted(hidden_cols.get(sname, ()))
        if hc:
            x.append("<cols>" + "".join('<col min="%d" max="%d" width="9" hidden="1" customWidth="1"/>' % (c + 1, c + 1) for c in hc) + "</cols>")
        x.append("<sheetData>")
        for ri, row in enumerate(rows, 1):
            attrs = ' hidden="1"' if ri in hidden_rows.get(sname, ()) else ""
            x.append('<row r="%d"%s>' % (ri, attrs))
            for ci, c in enumerate(row):
                if c is None:
                    continue
                ref = "%s%d" % (col_letter(ci), ri)
                t = c[0]
                if t == "n":
                    x.append('<c r="%s"><v>%s</v></c>' % (ref, c[1]))
                elif t == "s":
                    x.append('<c r="%s" t="s"><v>%d</v></c>' % (ref, sid(c[1])))
                elif t == "f":
                    x.append('<c r="%s"><f>SUM(A1:A2)</f></c>' % ref)
                elif t == "fv":
                    x.append('<c r="%s"><f>SUM(A1:A2)</f><v>%s</v></c>' % (ref, c[1]))
                elif t == "is":
                    x.append('<c r="%s" t="inlineStr"><is><t>%s</t></is></c>' % (ref, esc(c[1])))
            x.append("</row>")
        x.append("</sheetData></worksheet>")
        parts["xl/worksheets/sheet%d.xml" % n] = "".join(x)
    ss = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="%d" uniqueCount="%d">' % (len(sst), len(sst))
    ss += "".join("<si><t>%s</t></si>" % esc(s) for s in sst) + "</sst>"
    wbx = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
    wbx += "".join('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (esc(s), i, i) for i, s in enumerate(names, 1)) + "</sheets></workbook>"
    rel = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    rel += "".join('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>' % (i, i) for i in range(1, len(names) + 1))
    rel += '<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/></Relationships>' % (len(names) + 1)
    ct = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/>'
    ct += '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/></Types>'
    root_rel = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'

    def pack(pad):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for nm, body in (("[Content_Types].xml", ct), ("_rels/.rels", root_rel), ("xl/workbook.xml", wbx), ("xl/_rels/workbook.xml.rels", rel), ("xl/sharedStrings.xml", ss)) + tuple(sorted(parts.items())):
                zi = zipfile.ZipInfo(nm, SYN_EPOCH)
                zi.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(zi, body)
            if pad is not None:
                zi = zipfile.ZipInfo("docProps/pad.bin", SYN_EPOCH)
                zi.compress_type = zipfile.ZIP_STORED
                z.writestr(zi, b"\0" * pad)
        return buf.getvalue()
    data = pack(None)
    if pad_to is not None:
        n0 = pack(0)
        data = pack(pad_to - len(n0))
        assert len(data) == pad_to, (len(data), pad_to)
    return data


def synth_workbook(**kw):
    wk = {k: kw.pop(k) for k in ("hidden_cols", "hidden_rows", "pad_to", "order") if k in kw}
    return write_xlsx(synth_sheets(**kw), **wk)


# ------------------------------------------------------------------------------------------------------------------------
# checks (section 8), README (section 5) and the pipeline
# ------------------------------------------------------------------------------------------------------------------------
def kind_counts(cells):
    c = {"numeric": 0, "text": 0, "empty": 0, "nocache": 0}
    for k, v in cells.items():
        c[v[0]] += 1
    return c


def non_numeric_quarters(cells):
    return [qs(k) + "(" + v[0] + ")" for k, v in sorted(cells.items()) if v[0] != "numeric"]


def hidden_report(lay):
    rows = sum(len(s.hidden_rows) for s in lay.sheets.values())
    cols = sum(len(s.hidden_cols) for s in lay.sheets.values())
    return rows, cols


def manifest_rows(vdir):
    p = os.path.join(vdir, "MANIFEST.csv")
    return read_csv_dicts(read_file(p, "r")) if os.path.isfile(p) else []


MANIFEST_HEAD = ["vintage", "host", "url_path", "status", "bytes", "sha256", "retrieved_utc", "elapsed_s"]


def manifest_text(vintage, row, how):
    return "# source: %s, Richmond Fed historical workbook %s, vintage %s; the request or supply record of this vintage's workbook (%s)\n" % (CREDIT, WB_NAME, vintage, how) + csv_line(MANIFEST_HEAD) + csv_line([row[h] for h in MANIFEST_HEAD])


def vintage_problems(vintage, rows, sha, nbytes, reg_rows):
    """A build reads one vintage only: its MANIFEST row names this vintage and this file, and the registered rows were not made from a later vintage or from other bytes of the same one."""
    if M("g11_mixed_ok"):
        return []
    out = []
    if len(rows) != 1:
        out.append("MANIFEST.csv has %d rows, must have 1" % len(rows))
    for r in rows:
        if r.get("vintage") != vintage:
            out.append("MANIFEST.csv names vintage %s, not %s" % (r.get("vintage"), vintage))
        if r.get("sha256") != sha or r.get("bytes") != str(nbytes):
            out.append("the workbook does not match its MANIFEST.csv row (bytes or sha256)")
    for r in reg_rows:
        if r.get("vintage", "") > vintage:
            out.append("registered.csv was made from the later vintage %s" % r["vintage"])
        if r.get("vintage") == vintage and r.get("workbook_sha256") != sha:
            out.append("registered.csv was made from other bytes of vintage %s" % vintage)
    return out


class Ctx(object):
    pass


def make_checks(c):
    """The C01-C13 rows for the stage in c.stage ('pre' reads layout only)."""
    ck = []
    A = ck.append
    full = c.stage != "pre"
    lay = c.lay
    # C01
    if c.synthetic:
        A(("C01", "Workbook is a valid zip with xl/workbook.xml; its bytes and sha256 equal the MANIFEST row", "equal", "fixture workbook: %d bytes, sha256 %s" % (c.nbytes, c.sha[:12]), "INFO"))
    else:
        problems = []
        if c.manifest:
            m = c.manifest[0]
            if m.get("sha256") != c.sha or m.get("bytes") != str(c.nbytes):
                problems.append("MANIFEST.csv differs")
        else:
            problems.append("no MANIFEST.csv row")
        st = "FAIL" if problems else "PASS"
        obs = "%d bytes, sha256 %s; MANIFEST %s" % (c.nbytes, c.sha, "equal" if not problems else "; ".join(problems))
        if not problems:
            scout = c.sha == REG_SHA256 and c.nbytes == REG_BYTES
            if c.vintage == REG_VINTAGE and not M("g11_scout_lax"):
                if not scout:
                    st, obs = "FAIL", obs + "; differs from the supplied workbook's scouting values (%d bytes, sha256 %s)" % (REG_BYTES, REG_SHA256)
            elif not scout:
                st, obs = "WARN", obs + "; differs from the registering vintage's workbook (expected for a later vintage)"
        A(("C01", "Workbook is a valid zip with xl/workbook.xml; its bytes and sha256 equal the MANIFEST row (and the scouting values for the registering vintage)", "equal", obs, st))
    # C02
    hr, hc = hidden_report(lay)
    A(("C02", "Five sheets, required columns, 74 and 25 rows, unique consecutive keys, 2020Q2 absent", "no layout fault",
       "5 sheets; %d and %d rows; keys %s to %s and %s to %s; hidden rows %d, hidden columns %d" % (len(lay.tables[SH_DUKE].rows), len(lay.tables[SH_CUR].rows), qs(DUKE_KEYS[0]), qs(DUKE_KEYS[1]), qs(CUR_KEYS[0]), qs(CUR_KEYS[1]), hr, hc), "PASS"))
    # C03 (cell types from attributes: no value is converted)
    expect_empty = {(2019, 1), (2020, 1)}
    bad = []
    for sn in ("DUKE10", "DUKE12"):
        got = {k for k, v in lay.series[sn].items() if v[0] != "numeric"}
        if got != expect_empty:
            bad.append("%s non-numeric at %s" % (sn, ",".join(qs(k) for k in sorted(got)) or "none"))
    for sn in ("CUR10", "CUR12"):
        nn = non_numeric_quarters(lay.series[sn])
        if nn:
            bad.append("%s non-numeric at %s" % (sn, ",".join(nn)))
    A(("C03", "sp_10_exp and sp_1_exp empty exactly at 2019Q1 and 2020Q1 and numeric at the other 72; the two current _2 columns numeric at all 25", "as described", "; ".join(bad) or "as described", "WARN" if bad else "PASS"))
    if full:
        # C04
        st = {"match": "PASS", "near": "WARN", "unit_error": "FAIL"}[c.pin_state]
        A(("C04", "Pins: the Q3 2026 results page values against the workbook (match within 0.05; near is a WARN; a factor of 5 is a unit error)", "match",
           "; ".join("%s workbook=%s pin=%s %s" % d for d in c.pin_detail), st))
        # C05
        odd = [sn for sn in ("CUR10", "CUR12") if unit_odd(lay.series[sn])]
        A(("C05", "Every numeric cell of the two current _2 columns lies in -20 to 40", "inside", ("outside in " + ",".join(odd)) if odd else "inside", "WARN" if odd else "PASS"))
        # C06
        ys = {r["yardstick"]: r for r in c.yard}
        bad = [y for y in ("Y10", "Y12") if (ys[y]["n_nominal"], ys[y]["n_defined"]) != (str(Y_NOMINAL), str(Y_DEFINED))] + [y for y in ("YC10", "YC12") if (ys[y]["n_nominal"], ys[y]["n_defined"]) != (str(YC_NOMINAL), str(YC_DEFINED))]
        A(("C06", "Described-range counts: 65 nominal and 63 defined for Y10 and Y12; 17 and 16 for YC10 and YC12", "65/63, 65/63, 17/16, 17/16",
           ", ".join("%s %s/%s" % (y, ys[y]["n_nominal"], ys[y]["n_defined"]) for y in ("Y10", "Y12", "YC10", "YC12")), "WARN" if bad else "PASS"))
        # C07
        regs = c.reg_rows
        ok = prereg_ok() and all(r["prereg_sha256"] == SPEC_PREREG_SHA256 for r in regs)
        A(("C07", "The constants reproduce the 4.6 hash; prereg_sha256 in registered.csv equals it", SPEC_PREREG_SHA256, sha256_of(prereg_text().encode("utf-8")), "PASS" if ok else "FAIL"))
        # C08
        probs = recompute_problems(c)
        A(("C08", "stat_pp equals the difference of the rounded endpoints (and of the path.csv cells); yardstick min, max and n equal the windows recomputed from path.csv", "equal", "; ".join(probs[:3]) or "equal", "FAIL" if probs else "PASS"))
        # C10
        ends_y = y_ends()
        ends_c = yc_ends()
        bad = []
        if not all(qadd(e, -LAG) >= (2002, 1) and e <= BREAK_LAST_DUKE for e in ends_y):
            bad.append("a Duke window leaves 2002Q1-2020Q1")
        if not all(qadd(e, -LAG) >= BREAK_FIRST_CUR for e in ends_c if e not in (WINDOW[1],)):
            bad.append("a current window starts before 2020Q3")
        if not all(BREAK_FIRST_CUR <= parse_q(r["start_quarter"]) and parse_q(r["end_quarter"]) <= CUR_KEYS[1] for r in regs):
            bad.append("a registered window leaves 2020Q3-2026Q3")
        A(("C10", "No window crosses the 2020 break (Duke start >= 2002Q1 and end <= 2020Q1; current start >= 2020Q3; registered inside 2020Q3-2026Q3)", "none", "; ".join(bad) or "none", "FAIL" if bad else "PASS"))
    # C09
    if c.stage == "pre":
        A(("C09", "Blind order: pre printed and wrote no S&P value; the dry stage wrote nothing under data/", "no value", "pre converted %d S&P cell(s)" % c.conversions, "PASS" if c.conversions == 0 else "FAIL"))
    else:
        A(("C09", "Blind order: pre printed and wrote no S&P value; the dry stage wrote nothing under data/", "no value", "asserted by the pre and dry stages' own refusals and by selftest G11", "INFO"))
    # C11
    d = c.dates
    parts = []
    for k in (WINDOW[0], WINDOW[1]):
        o, cl = d.get(k, ("", ""))
        parts.append("%s %s to %s" % (qs(k), o or "n/a", cl or "n/a"))
    A(("C11", "CFO field dates of 2024Q1 and 2026Q1 (open and close)", "dates", "; ".join(parts) + ("" if d else "; " + c.dates_note), "INFO"))
    # C12
    if full:
        if c.vintage == c.reg_vintage or not c.reg_rows:
            A(("C12", "Revision between vintages: the window values and stat_pp against the registered row", "registering vintage", "this is the registering vintage", "INFO"))
        else:
            diffs = []
            for r in c.reg_rows:
                if r["superseded"] == "yes":
                    continue
                n = next((x for x in c.cur_rows if x["statement_id"] == r["statement_id"]), None)
                if n is not None and (n["exp_start"], n["exp_end"], n["stat_pp"]) != (r["exp_start"], r["exp_end"], r["stat_pp"]):
                    diffs.append("%s: registered %s/%s/%s, now %s/%s/%s" % (r["statement_id"], r["exp_start"], r["exp_end"], r["stat_pp"], n["exp_start"], n["exp_end"], n["stat_pp"]))
            A(("C12", "Revision between vintages: the window values and stat_pp against the registered row", "equal", "; ".join(diffs) or "no revision", "INFO"))
    # C13
    dl = c.dict_lines
    A(("C13", "Dictionary lines for the six Duke variables and the S&P block of the current dictionary, verbatim (each clipped to 15 words)", "lines", " || ".join(dl[0] + dl[1]) or "none found", "INFO"))
    ck.sort(key=lambda x: x[0])
    return ck


def recompute_problems(c):
    """C08: the registered statistics recompute from their own endpoints; for rows of this vintage the endpoints equal the path cells; the yardstick equals the windows recomputed from path.csv text."""
    out = []
    for r in c.reg_rows:
        if r["superseded"] == "yes" or r["void_reason"] == "endpoint_undefined":
            continue
        a, b = Decimal(r["exp_start"]), Decimal(r["exp_end"])
        if r["stat_pp"] != fmt6(b - a):
            out.append("%s stat_pp is not exp_end - exp_start" % r["statement_id"])
    pr = {}
    for r in read_csv_dicts(c.path_text):
        pr[(r["era"], r["horizon"], r["quarter"])] = r
    for r in c.reg_rows:
        if r["superseded"] == "yes" or r["vintage"] != c.vintage or r["void_reason"] == "endpoint_undefined":
            continue
        for qf, vf in (("start_quarter", "exp_start"), ("end_quarter", "exp_end")):
            p = pr.get(("current", r["horizon"], r[qf]))
            if p is None or p["exp"] != r[vf]:
                out.append("%s %s differs from path.csv" % (r["statement_id"], vf))
    for y in c.yard:
        era = "duke" if y["yardstick"].startswith("Y") and not y["yardstick"].startswith("YC") else "current"
        ends = [qk(i) for i in range(qi(parse_q(y["first_end_quarter"])), qi(parse_q(y["last_end_quarter"])) + 1)]
        ch = []
        for e in ends:
            if era == "current" and e == WINDOW[1]:
                continue
            a, b = pr.get((era, y["horizon"], qs(qadd(e, -LAG)))), pr.get((era, y["horizon"], qs(e)))
            if a and b and a["status"] == "ok" and b["status"] == "ok":
                ch.append(Decimal(b["exp"]) - Decimal(a["exp"]))
        if (str(len(ch)), fmt6(min(ch)) if ch else "", fmt6(max(ch)) if ch else "") != (y["n_defined"], y["min_change_pp"], y["max_change_pp"]):
            out.append("%s min, max or n differs from path.csv" % y["yardstick"])
    return out


def path_rows(lay, dates):
    rows = []
    for sn in SERIES_ORDER:
        tn, col, era, hz = SERIES[sn]
        t = lay.tables[tn]
        for k, (r, cells) in zip(t.keys, t.rows):
            cell = cells.get(t.cols[col], ("empty", ""))
            try:
                v, stt = fmt6(cell_r6(cell)), "ok"
            except Undef:
                v, stt = "", "empty"
            o, cl = dates.get(k, ("", "")) if era == "current" else ("", "")
            rows.append({"era": era, "horizon": hz, "quarter": qs(k), "exp": v, "status": stt, "survey_open": o, "survey_close": cl})
    order = {("duke", "10y"): 0, ("duke", "12m"): 1, ("current", "10y"): 2, ("current", "12m"): 3}
    rows.sort(key=lambda r: (order[(r["era"], r["horizon"])], parse_q(r["quarter"])))
    return rows


def render_csv(name, rows, source):
    out = io.StringIO()
    out.write(source + "\n")
    w = csv.writer(out, lineterminator="\n")
    head = list(ALLOW[name])
    if M("g12_extra_col") and name == "yardstick.csv":
        head = head + ["note"]
    w.writerow(head)
    for r in rows:
        w.writerow([r.get(h, "") for h in head])
    return out.getvalue()


def horizon_word(h):
    return "10-year" if h == "10y" else "12-month"


def pts(d):
    return "point" if abs(d) < 1 else "points"


VOID_WORDS = {"endpoint_undefined": "an endpoint quarter is absent or its cell is empty or not a number",
              "unit_odd": "a cell of the column lies outside -20 to 40, which points to a unit error"}


def change_phrase(r):
    if r["void_reason"] != "none":
        base = "could not be tested (%s)" % VOID_WORDS[r["void_reason"]]
        if r["stat_pp"] != "":
            base += "; the exact difference was %s points, sign %s" % (signed2(Decimal(r["stat_pp"])), r["sign"])
        return base
    d = Decimal(r["stat_pp"])
    a = fmt_n(abs(d), 2)
    if r["sign"] == "RISE":
        return "rose by %s %s" % (a, pts(d))
    if r["sign"] == "FALL":
        return "fell by %s %s" % (a, pts(d))
    return "changed by %s %s, inside the 0.10-point zone this build treats as unchanged" % (signed2(d), pts(d))


def readme_text(c):
    regs = [r for r in c.reg_rows]
    live = {r["statement_id"]: r for r in regs if r["superseded"] == "no"}
    sup = [r for r in regs if r["superseded"] == "yes"]
    e1, e2 = live["E1"], live["E2"]
    ys = {r["yardstick"]: r for r in c.yard}
    lay = c.lay
    L = []
    A = L.append
    if c.synthetic:
        A(source_line(c.vintage, "README of the dry stage", True))
        A("")
    A("# The CFO Survey's expected S&P 500 return, Q1 2024 to Q1 2026")
    if M("g8_nondeterministic"):
        A("<!-- built %r -->" % time.time())
    A("")
    A("Credit: %s. The numbers below are derived from the Richmond Fed's revised historical workbook, vintage %s (sha256 %s)." % (CREDIT, vintage_long(c.vintage), c.sha))
    A("")
    A("This build measures the change in the CFO Survey's mean expected S&P 500 return, on a 10-year and a 12-month horizon, between 2024Q1 and 2026Q1 in the %s vintage of the survey's revised historical file, and whether the change has the sign of the Philadelphia Fed forecasters' survey." % vintage_long(e1["vintage"]))
    if e1["void_reason"] != "none" and e1["stat_pp"] == "":
        A("For the 10-year horizon the comparison %s; the forecasters' survey stays at +%s point (0.15), spf_direction is %s, blind is %s." % (change_phrase(e1), SPF_STAT, e1["spf_direction"], e1["blind"]))
    else:
        A("For the 10-year horizon (E1) the mean expected return (the series whose recent values the results pages give for firms that closely follow the stock market; see What is not known) was %s%% in %s and %s%% in %s: it %s (sign %s). The forecasters' survey (STOCK10, CORRECTIONS.md C-082) rose by 0.15 point (+%s) over the same quarters, so spf_direction is %s. Blind: %s."
          % (fmt_n(Decimal(e1["exp_start"]), 2), e1["start_quarter"], fmt_n(Decimal(e1["exp_end"]), 2), e1["end_quarter"], change_phrase(e1), e1["sign"], SPF_STAT, e1["spf_direction"], e1["blind"]))
    A("")
    A(R_A)
    A("")
    A(R_B)
    A("")
    A(R_C)
    A("")
    A(R_D)
    A("")
    if e2["void_reason"] != "none" and e2["stat_pp"] == "":
        A("For the 12-month horizon (E2, shown here only) the comparison %s." % change_phrase(e2))
    else:
        A("For the 12-month horizon (E2, shown here only) the mean expected return was %s%% in %s and %s%% in %s: it %s (sign %s); no forecasters' figure is held for this horizon, so spf_direction is na."
          % (fmt_n(Decimal(e2["exp_start"]), 2), e2["start_quarter"], fmt_n(Decimal(e2["exp_end"]), 2), e2["end_quarter"], change_phrase(e2), e2["sign"]))
    if e1["sign"] != e2["sign"] and e1["void_reason"] == "none" and e2["void_reason"] == "none":
        A("The 10-year sign (%s) and the 12-month sign (%s) differ; they are two horizons and are not merged." % (e1["sign"], e2["sign"]))
    A("")
    A("## What the zone means")
    A("")
    A("The sign uses a zone of 0.10 point: RISE at +0.10 or more, FALL at -0.10 or less, ZERO inside. The zone is a convention equal to the one-decimal resolution of the published pages, fixed before any value was read; it is not a noise bound. Sampling noise is not published for these means (N is about 340-370 per quarter, from the pages' figures for 2026Q2 and 2026Q3), so nothing here says whether a change is large or small against noise. The signed change is always printed to two decimals beside the forecasters' 0.15, so a move of the same direction under 0.10 shows as a number.")
    A("")
    A("## For scale: the described ranges")
    A("")
    A("These are described, never registered or tested, and carry no rank and no label. The Duke-era survey (question form and treatment differ from 2020) had eight-quarter changes with end quarters %s to %s (2002-2020): for the 10-year return from %s to %s points (n = %s of %s windows; at most eight disjoint spans), and for the 12-month return from %s to %s points (n = %s of %s). The variant inside the current series has end quarters %s to %s without the registered window: 10-year %s to %s points (n = %s of %s), 12-month %s to %s points (n = %s of %s); at most three disjoint spans, and they overlap each other."
      % (ys["Y10"]["first_end_quarter"], ys["Y10"]["last_end_quarter"], ys["Y10"]["min_change_pp"] and fmt_n(Decimal(ys["Y10"]["min_change_pp"]), 2), ys["Y10"]["max_change_pp"] and fmt_n(Decimal(ys["Y10"]["max_change_pp"]), 2), ys["Y10"]["n_defined"], ys["Y10"]["n_nominal"],
         ys["Y12"]["min_change_pp"] and fmt_n(Decimal(ys["Y12"]["min_change_pp"]), 2), ys["Y12"]["max_change_pp"] and fmt_n(Decimal(ys["Y12"]["max_change_pp"]), 2), ys["Y12"]["n_defined"], ys["Y12"]["n_nominal"],
         ys["YC10"]["first_end_quarter"], ys["YC10"]["last_end_quarter"], ys["YC10"]["min_change_pp"] and fmt_n(Decimal(ys["YC10"]["min_change_pp"]), 2), ys["YC10"]["max_change_pp"] and fmt_n(Decimal(ys["YC10"]["max_change_pp"]), 2), ys["YC10"]["n_defined"], ys["YC10"]["n_nominal"],
         ys["YC12"]["min_change_pp"] and fmt_n(Decimal(ys["YC12"]["min_change_pp"]), 2), ys["YC12"]["max_change_pp"] and fmt_n(Decimal(ys["YC12"]["max_change_pp"]), 2), ys["YC12"]["n_defined"], ys["YC12"]["n_nominal"]))
    A("")
    A("## What was known before the build")
    A("")
    A("The only numbers known to the authors were the forecasters' result (STOCK10 7.1513%% in Q1 2024 to 7.3056%% in Q1 2026, CORRECTIONS.md C-082) and four values from the Q3 2026 results page for firms that closely follow the stock market: 12-month 7.8%% (2026Q2) and 7.9%% (2026Q3), 10-year 9.7%% (2026Q2) and 9.6%% (2026Q3). No cell of the window or of the Duke-era series had been seen by anyone writing or briefing the build. The two pinned quarters sit after the window, so the pins do not reach the window values; and the Bank revises the historical file each year (a March 2026 page said data from Q2 2020 to Q4 2025 were revised, which includes 2024Q1). The pins compared as: %s." % e1["pins"])
    A("")
    A("## What is not known")
    A("")
    A("- Winsorisation: the methods document says S&P 500 expectations are winsorized at 2.5 and 97.5 percent; the Q3 2026 results page says winsorized at 5%. Both are recorded here and neither is resolved.")
    A("- The population: the results page gives its figures for firms that closely follow the stock market, unweighted. The workbook does not state whether its _2 columns carry the same filter.")
    A("")
    A("## Dates")
    A("")
    d = c.dates
    po, pc = d.get(WINDOW[0], ("", ""))
    qo, qc = d.get(WINDOW[1], ("", ""))
    if d:
        A("CFO Survey field dates: 2024Q1 %s to %s; 2026Q1 %s to %s. The forecasters' survey responses were due %s (the 2026 date was delayed by a government shutdown). The quarter labels are not the same days in the two surveys." % (po or "n/a", pc or "n/a", qo or "n/a", qc or "n/a", SPF_DEADLINES))
    else:
        A("CFO Survey field dates were not available from the workbook (%s). The forecasters' survey responses were due %s." % (c.dates_note, SPF_DEADLINES))
    A("")
    A("## Dictionary text, verbatim (each line clipped to 15 words)")
    A("")
    for ln in c.dict_lines[0]:
        A("- through_Q1_2020_dictionary: " + ln)
    for ln in c.dict_lines[1]:
        A("- from_Q2_2020on_dictionary: " + ln)
    if not (c.dict_lines[0] or c.dict_lines[1]):
        A("- none found")
    A("")
    A("## Coverage")
    A("")
    kd = {sn: kind_counts(lay.series[sn]) for sn in SERIES_ORDER}
    A("- Duke sheet: %d quarters, %s to %s; sp_10_exp is numeric at %d and not at %s; sp_1_exp is numeric at %d and not at %s." % (len(lay.tables[SH_DUKE].rows), qs(DUKE_KEYS[0]), qs(DUKE_KEYS[1]), kd["DUKE10"]["numeric"], ", ".join(non_numeric_quarters(lay.series["DUKE10"])) or "none", kd["DUKE12"]["numeric"], ", ".join(non_numeric_quarters(lay.series["DUKE12"])) or "none"))
    A("- Current sheet: %d quarters, %s to %s (2020Q2 absent); sp_10yrexp_2 is numeric at %d and not at %s; sp_12moexp_2 is numeric at %d and not at %s." % (len(lay.tables[SH_CUR].rows), qs(CUR_KEYS[0]), qs(CUR_KEYS[1]), kd["CUR10"]["numeric"], ", ".join(non_numeric_quarters(lay.series["CUR10"])) or "none", kd["CUR12"]["numeric"], ", ".join(non_numeric_quarters(lay.series["CUR12"])) or "none"))
    A("")
    A("## Superseded rows")
    A("")
    if sup:
        for r in sup:
            A("- %s version %s (%s, vintage %s) is superseded: stat_pp was %s." % (r["statement_id"], r["version"], r["sign"], r["vintage"], r["stat_pp"] or "undefined"))
    else:
        A("No row has been superseded.")
    A("")
    if c.vintage != c.reg_vintage and c.reg_rows and c.stage != "pre":
        rv = next((x for x in c.checks if x[0] == "C12"), None)
        if rv:
            A("## Revision since the registering vintage")
            A("")
            A("Vintage %s against the registered rows (vintage %s): %s." % (c.vintage, c.reg_vintage, rv[3]))
            A("")
    A("## Column dictionary")
    A("")
    A("- expected return: the answer to the survey's question about the S&P 500 return over the stated horizon, in percent a year.")
    A("- mean: the survey's mean of the answers for the quarter (the median columns are not used).")
    A("- percentage point (pp): the difference of two percentages; 7.3 percent less 7.1 percent is 0.2 point.")
    A("- vintage: the date of the copy of the revised historical file the numbers come from.")
    A("- winsorized: extreme answers are replaced by the value at a set percentile before the mean is taken.")
    A("- sign: RISE, FALL or ZERO from the exact difference of the two rounded cells and the 0.10-point zone.")
    A("- spf_direction: SAME, OPPOSITE or FLAT from the sign beside the forecasters' rise; none for a void row, na for the 12-month horizon. It describes and decides nothing.")
    A("- void_reason: none, endpoint_undefined (an endpoint quarter is absent, empty or not a number) or unit_odd (a cell outside -20 to 40).")
    A("- pins: match or near, the comparison of four published values with the workbook; never used in a statistic.")
    A("")
    A("## Builder decisions")
    A("")
    A("- The quarter key is the first column whose every cell parses as a quarter label (or year and quarter columns); the survey dates sheet's open and close columns are found by header words.")
    A("- A pin whose workbook cell is not a number counts as near; a text cell in a path.csv series is written as status empty.")
    A("- unit_odd tests the stored value, not the rounded one. Dictionary lines are clipped to 15 words and are subject to the wording guard like the rest of this file.")
    A("")
    A("## Sources")
    A("")
    A("- Workbook: %s (retrieved or supplied, vintage %s). %s" % (URL, vintage_long(c.vintage), CREDIT))
    A("- Forecasters' survey figure: CORRECTIONS.md C-082 in this repository (Federal Reserve Bank of Philadelphia, Survey of Professional Forecasters).")
    A("- Greenwood and Shleifer (2014), Expectations of Returns and Expected Returns, Review of Financial Studies (relayed in the spec; not read by the build).")
    A("")
    return "\n".join(L)


def build_files(c):
    """Fills c with the pipeline's results and returns {name: text} for the committed files and path.csv. Raises Halt, UnitError, Refused, DataError."""
    lay = analyse(c.data)
    c.lay = lay
    if lay.faults:
        raise Halt("; ".join(lay.faults))
    c.dates, c.dates_note = survey_dates(lay)
    c.dict_lines = dict_lines(lay)
    series = lay.series
    c.pin_state, c.pin_detail = pin_status(series)
    if (c.pin_state == "unit_error" and not M("g6_unit_continues")) or (M("g6_near_halts") and c.pin_state == "near"):
        raise UnitError("; ".join("%s workbook=%s pin=%s %s" % d for d in c.pin_detail if d[3] == "unit_error" or M("g6_near_halts")))
    pins = "near" if c.pin_state in ("near", "unit_error") else "match"
    if M("g6_near_silent"):
        pins = "match"
    existing = read_csv_dicts(c.reg_text) if c.reg_text else []
    version = 1
    if c.supersede and existing:
        version = max(int(r["version"]) for r in existing) + (0 if M("g8_supersede_noversion") else 1)
    c.cur_rows = []
    for sid, hz, sn in (("E1", "10y", "CUR10"), ("E2", "12m", "CUR12")):
        c.cur_rows.append(statement(sid, hz, sn, series[sn], WINDOW[0], WINDOW[1], pins, c.sha, c.vintage, version, c.vdir))
    write_registered = False
    if c.registering and not existing:
        if not prereg_ok():
            raise Refused("the 4.6 block held in this script does not reproduce its sha256: registered.csv is not written")
        c.reg_rows, write_registered = c.cur_rows, True
    elif c.registering and c.supersede:
        if not prereg_ok():
            raise Refused("the 4.6 block held in this script does not reproduce its sha256: registered.csv is not written")
        old = [dict(r) for r in existing]
        if not M("g8_two_live"):
            for r in old:
                if r["superseded"] == "no":
                    r["superseded"] = "yes"
        c.reg_rows = c.cur_rows if M("g8_supersede_deletes") else old + c.cur_rows
        write_registered = True
    else:
        c.reg_rows = existing if not M("g8_rewrite_registered") else c.cur_rows
        write_registered = M("g8_rewrite_registered")
    c.reg_vintage = min([r["vintage"] for r in c.reg_rows] or [c.vintage])
    probs = registered_problems(c.reg_rows)
    if probs:
        raise DataError("; ".join(probs))
    c.yard = yardstick_rows(series)
    path_rows_ = path_rows(lay, c.dates)
    src = lambda what: source_line(c.vintage, what, c.synthetic)
    c.path_text = render_csv("path.csv", path_rows_, src("the four series used, all quarters (local, gitignored)"))
    c.checks = make_checks(c)
    files = {}
    if write_registered:
        files["registered.csv"] = render_csv("registered.csv", c.reg_rows, src("registered statements E1 and E2"))
    files["yardstick.csv"] = render_csv("yardstick.csv", c.yard, src("described ranges of eight-quarter changes; nothing is registered against them"))
    files["checks.csv"] = render_csv("checks.csv", [dict(zip(ALLOW["checks.csv"], x)) for x in c.checks], src("checks C01 to C13"))
    files["README.md"] = readme_text(c)
    fails = [x for x in c.checks if x[4] == "FAIL"]
    if fails:
        raise DataError("FAIL check(s): " + "; ".join("%s %s" % (x[0], x[3][:100]) for x in fails))
    committed = {n: t for n, t in files.items() if n in COMMITTED}
    probs = folder_problems(committed)
    probs += readme_problems(files["README.md"])
    if c.synthetic:
        pass
    probs += csv_problems("path.csv", c.path_text)
    if probs:
        raise DataError("output guard: " + "; ".join(dict.fromkeys(probs)))
    files["path.csv"] = c.path_text
    return files


# ------------------------------------------------------------------------------------------------------------------------
# the pre stage: layout only; no S&P value is converted, printed or written
# ------------------------------------------------------------------------------------------------------------------------
def pre_report(c):
    lay = c.lay
    L = []
    for name in SHEETS:
        sh = lay.sheets.get(name)
        if sh is None:
            L.append("sheet %s: MISSING" % name)
            continue
        rows = sorted(sh.cells)
        hn = [lay.tables[name].header.get(i, "") for i in sorted(sh.hidden_cols)] if name in lay.tables else []
        L.append("sheet %s: state %s, %d non-empty rows (rows %s to %s), %d columns, hidden rows %d, hidden columns %d%s"
                 % (name, sh.state, len(rows), rows[0] if rows else "-", rows[-1] if rows else "-", sh.max_col(), len(sh.hidden_rows), len(sh.hidden_cols), (" (" + ", ".join(h or "?" for h in hn) + ")") if hn else ""))
    for name in (SH_DUKE, SH_CUR):
        t = lay.tables.get(name)
        if t is None:
            continue
        L.append("  %s: header on row %s; columns: %s" % (name, t.header_row, ", ".join(t.header[c_] for c_ in sorted(t.header))))
        if t.key_desc:
            ks = [k for k in t.keys if k]
            L.append("  %s: key %s (format %s); %d rows; keys %s to %s; unique %s; consecutive %s" % (
                name, t.key_desc[1] if t.key_desc[0] == "col" else "%s+%s" % (t.key_desc[1], t.key_desc[2]), t.key_desc[2] if t.key_desc[0] == "col" else "year and quarter columns", len(t.rows),
                qs(ks[0]) if ks else "-", qs(ks[-1]) if ks else "-", len(set(ks)) == len(ks), all(qi(b) - qi(a) == 1 for a, b in zip(ks, ks[1:]))))
    for sn in SERIES_ORDER:
        if sn not in lay.series:
            continue
        cells = lay.series[sn]
        kc = kind_counts(cells)
        L.append("  %s (%s.%s): cell types numeric %d, text %d, empty %d, formula without a cached value %d%s" % (
            sn, SERIES[sn][0], SERIES[sn][1], kc["numeric"], kc["text"], kc["empty"], kc["nocache"], ("; not numeric at " + ", ".join(non_numeric_quarters(cells))) if 0 < len(non_numeric_quarters(cells)) <= 12 else ("; not numeric at %d quarters" % len(non_numeric_quarters(cells)) if non_numeric_quarters(cells) else "")))
    L.append("survey dates (%s):" % c.dates_note)
    for k in WINDOW:
        o, cl = c.dates.get(k, ("n/a", "n/a"))
        L.append("  %s: open %s, close %s" % (qs(k), o or "n/a", cl or "n/a"))
    L.append("dictionary lines (each clipped to 15 words):")
    for ln in c.dict_lines[0] + c.dict_lines[1]:
        L.append("  " + ln)
    return L


def run_pre(c, out_dir, say):
    lay = analyse(c.data)
    c.lay = lay
    c.dates, c.dates_note = survey_dates(lay)
    c.dict_lines = dict_lines(lay)
    before = STATS["conv"]
    if M("g11_pre_converts"):
        for sn in lay.series:
            for cell in lay.series[sn].values():
                try:
                    to_dec(*cell)
                except Undef:
                    pass
    lines = pre_report(c)
    if M("g11_pre_prints_value"):
        k = next(iter(lay.series["CUR10"]))
        lines.append("sample cell %s" % lay.series["CUR10"][WINDOW[1]][1])
    if lay.faults:
        lines.append("LAYOUT FAULTS (the full stage would halt with exit 4):")
        lines += ["  " + f for f in lay.faults]
    c.conversions = STATS["conv"] - before
    c.stage = "pre"
    if lay.faults:
        for ln in lines:
            say(ln)
        raise Halt("; ".join(lay.faults))
    c.pin_state, c.pin_detail, c.yard, c.reg_rows, c.cur_rows, c.reg_vintage = "match", [], [], [], [], c.vintage
    ck = make_checks(c)
    src = source_line(c.vintage, "checks of the pre stage (layout only; no S&P value is read)", c.synthetic)
    text = render_csv("checks.csv", [dict(zip(ALLOW["checks.csv"], x)) for x in ck], src)
    if M("g11_pre_writes_value"):
        text += "# sample %s\n" % lay.series["CUR10"][WINDOW[1]][1]
    for ln in lines:
        say(ln)
    for x in ck:
        say("  %s %s: %s" % (x[0], x[4], x[3][:150]))
    probs = csv_problems("checks.csv", text) + leak_problems("checks.csv", text)
    if probs:
        raise DataError("output guard: " + "; ".join(probs))
    write_text(os.path.join(out_dir, "checks.csv"), text)
    return 2 if any(x[4] == "FAIL" for x in ck) else 0


# ------------------------------------------------------------------------------------------------------------------------
# build: the stages and their file handling
# ------------------------------------------------------------------------------------------------------------------------
def inside(path, folder):
    p, f = os.path.realpath(path), os.path.realpath(folder)
    return p == f or p.startswith(f + os.sep)


def run_build(a, say=print, root=None):
    root = root or ROOT
    v = a.vintage
    if not vintage_ok(v):
        raise Refused("--vintage must be a valid YYYYMMDD date")
    out_default, cache_default = paths(root)
    stage = a.stage
    c = Ctx()
    c.vintage, c.stage, c.synthetic = v, stage, stage == "dry"
    c.registering, c.supersede = bool(a.registering), bool(a.supersede)
    c.reg_text = None
    if stage == "dry":
        if not a.out and not M("g11_dry_default_out"):
            raise Refused("--stage dry requires --out (a scratch folder outside data/)")
        out = a.out or out_default
        if inside(out, os.path.join(root, "data")) and not (M("g11_dry_data_ok") or M("g11_dry_default_out")):
            raise Refused("--out for the dry stage must lie outside data/")
        if c.registering or c.supersede:
            raise Refused("--registering and --supersede do not apply to the dry stage")
        c.data = synth_workbook()
        c.sha, c.nbytes, c.manifest, c.vdir = sha256_of(c.data), len(c.data), None, None
        c.registering = True
        files = build_files(c)
        if M("g11_synthetic_leak"):
            files["README.md"] += "\nSYNTHETIC\n"
        for n, t in files.items():
            write_text(os.path.join(out, n), t)
        say("dry stage: wrote %s to the scratch folder (synthetic workbook, %d bytes); checks: %s" % (", ".join(sorted(files)), c.nbytes, status_counts(c.checks)))
        return 0
    out = a.out or out_default
    cache = a.cache or cache_default
    vdir = os.path.join(cache, v)
    raw = os.path.join(vdir, "raw", WB_NAME)
    if not os.path.isfile(raw):
        raise DataError("no workbook at the vintage's raw/ folder: drop %s there first" % WB_NAME)
    c.data = read_file(raw)
    c.sha, c.nbytes, c.vdir = sha256_of(c.data), len(c.data), vdir
    reg_path = os.path.join(out, "registered.csv")
    c.reg_text = read_file(reg_path, "r") if os.path.isfile(reg_path) else None
    reg_rows = read_csv_dicts(c.reg_text) if c.reg_text else []
    mp = os.path.join(vdir, "MANIFEST.csv")
    if not os.path.isfile(mp):
        row = {"vintage": v, "host": "", "url_path": "", "status": "supplied", "bytes": str(c.nbytes), "sha256": c.sha, "retrieved_utc": "", "elapsed_s": ""}
        write_text(mp, manifest_text(v, row, "supplied by the supervisor"))
    c.manifest = manifest_rows(vdir)
    probs = vintage_problems(v, c.manifest, c.sha, c.nbytes, reg_rows)
    if probs:
        raise Refused("a build reads one vintage only: " + "; ".join(probs))
    if stage == "pre":
        if c.reg_text:
            raise Refused("registered.csv exists in the output folder: pre is a pre-registration stage")
        return run_pre(c, out, say)
    # full
    if c.registering and c.reg_text and not c.supersede and not M("g8_registering_twice"):
        raise Refused("registered.csv already exists: it is written once by the first registering build; use --registering --supersede for a bug found after registration")
    if c.supersede and not c.registering:
        raise Refused("--supersede is part of a registering build")
    if c.supersede and not c.reg_text:
        raise Refused("--supersede needs an existing registered.csv")
    if not c.registering and not c.reg_text:
        if M("g11_full_no_flag"):
            c.registering = True
        else:
            raise Refused("no registered.csv yet: the registering build needs --registering (supervisor only)")
    files = build_files(c)
    for n, t in files.items():
        write_text(os.path.join(out, n), t)
    say("full stage: wrote %s; checks: %s" % (", ".join(sorted(files)), status_counts(c.checks)))
    return 0


def status_counts(checks):
    cnt = {}
    for x in checks:
        cnt[x[4]] = cnt.get(x[4], 0) + 1
    return ", ".join("%s %d" % (k, cnt[k]) for k in ("PASS", "WARN", "FAIL", "INFO") if k in cnt)


# ------------------------------------------------------------------------------------------------------------------------
# fetch: ONE request, one host
# ------------------------------------------------------------------------------------------------------------------------
def check_url(url):
    """A plain https GET of the one workbook path on www.richmondfed.org. Any other host, path, query or port is refused before a request is made. Returns (host, path)."""
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    if M("g10_other_host"):
        return host, p.path
    if p.scheme != "https" or p.username or p.password or p.port not in (None, 443) or p.fragment or p.query:
        raise Refused("only a plain https URL without a query is allowed")
    if host != HOST:
        raise Refused("host %s is not on the allowlist (only %s is)" % (host, HOST))
    if p.path != URL_PATH:
        raise Refused("only the workbook path is requested")
    return host, p.path


def real_opener(host, target, headers, timeout, cap):
    """GET https://host/target. No redirect is followed (a 3xx comes back as a status), no cookies, the only verb is GET. A non-200 body is read up to ERR_CAP bytes. Socket faults raise SocketFault."""
    conn = http.client.HTTPSConnection(host, timeout=timeout)
    try:
        conn.request("GET", target, headers=dict(headers))
        resp = conn.getresponse()
        status = resp.status
        hdrs = {k.lower(): v for k, v in resp.getheaders()}
        if status != 200:
            return status, resp.read(ERR_CAP), hdrs
        body = resp.read(cap + 1)
        return status, (body if len(body) <= cap else None), hdrs
    except (OSError, EOFError, http.client.HTTPException) as e:
        raise SocketFault(type(e).__name__)
    finally:
        conn.close()


STOP_FIELDS = ("status", "utc_time", "url_path", "retry_after", "body_head")


def esc_head(body, n=300):
    return (body or b"")[:n].decode("latin-1").encode("unicode_escape").decode("ascii").replace("@", "[at]")


def stop_text(status, utc_time, url_path, retry_after, body_head):
    lines = ["status: %s" % status, "utc_time: %s" % utc_time, "url_path: %s" % url_path]
    if not M("g10_stop_short"):
        lines.append("retry_after: %s" % retry_after)
    lines.append("body_head: %s" % body_head)
    return "\n".join(lines) + "\n"


def stop_text_ok(text):
    return [l.split(":", 1)[0] for l in text.splitlines()] == list(STOP_FIELDS)


def create_stop(path, text):
    """The one place a STOP file is created: exclusive create, so an existing latch is never overwritten."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "x", encoding="utf-8") as fh:
            fh.write(text)
    except FileExistsError:
        pass


def looks_like_page(body):
    return body.lstrip()[:15].lower().startswith((b"<!", b"<html"))


def body_problem(body):
    """R3: a 200 body that is not an xlsx of 50,000 to 2,000,000 bytes. Returns the reason or ''."""
    n = len(body) if body else 0
    lo = MIN_BYTES - 1 if M("g10_size_lo") else MIN_BYTES
    hi = MAX_BYTES + 1 if M("g10_size_hi") else MAX_BYTES
    if n == 0:
        return "" if M("g10_empty_ok") else "empty body"
    if looks_like_page(body):
        return "" if M("g10_html_ok") else "the body is a web page"
    if n < lo or n > hi:
        return "the body is %d bytes, outside %d to %d" % (n, MIN_BYTES, MAX_BYTES)
    if body[:2] != b"PK":
        return "" if M("g10_nonzip_ok") else "the body is not a zip file"
    try:
        z = zipfile.ZipFile(io.BytesIO(body))
        if "xl/workbook.xml" not in z.namelist():
            return "the zip holds no xl/workbook.xml"
    except zipfile.BadZipFile:
        return "" if M("g10_nonzip_ok") else "the body is not a readable zip"
    return ""


def run_fetch(a, opener=real_opener, now_utc=None, say=print, url=URL, root=None):
    root = root or ROOT
    _, cache_default = paths(root)
    cache = a.cache or cache_default
    stop_path = os.path.join(cache_default, STOP_NAME)          # fixed, whatever --cache says: a latch cannot be dodged by pointing the cache elsewhere
    now = (now_utc or (lambda: dt.datetime.now(dt.timezone.utc)))()
    v = a.vintage
    if not vintage_ok(v):
        raise Refused("--vintage must be a valid YYYYMMDD date")
    if v == REG_VINTAGE:
        raise Refused("the registering vintage %s is the supervisor's own download and is never fetched" % REG_VINTAGE)
    if v != now.strftime("%Y%m%d"):
        raise Refused("the vintage of a fetch is today's UTC date (%s)" % now.strftime("%Y%m%d"))
    host, path = check_url(url)
    if os.path.exists(stop_path) and not M("g10_stop_ignored"):
        say("STOP: %s exists; no request is made. Only a person deletes it." % STOP_NAME)
        return 2
    vdir = os.path.join(cache, v)
    raw = os.path.join(vdir, "raw", WB_NAME)
    mp = os.path.join(vdir, "MANIFEST.csv")
    if os.path.isfile(raw) and not M("g10_recache"):
        rows = manifest_rows(vdir)
        if rows and rows[0].get("sha256") == sha256_of(read_file(raw)):
            say("cached: vintage %s already holds a body matching its MANIFEST.csv row; no request is made" % v)
            return 0
        raise Refused("the vintage already holds a workbook that does not match its MANIFEST.csv row")
    headers = {"User-Agent": USER_AGENT + (" (contact" + chr(64) + "invalid)" if M("g10_ua_contact") else ""), "Accept-Encoding": "identity", "Accept": "*/*"}
    t0 = time.monotonic()
    utc = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    def latch(status, body, hdrs, why):
        create_stop(stop_path, stop_text(status, utc, path, (hdrs or {}).get("retry-after", ""), esc_head(body)))
        say("STOP: %s (%s); %s written" % (why, status, STOP_NAME))
        return 2
    try:
        status, body, hdrs = opener(host, path, headers, TIMEOUT, BODY_CAP)
        if M("g10_retry") and status >= 500:
            status, body, hdrs = opener(host, path, headers, TIMEOUT, BODY_CAP)
        if 300 <= status < 400:
            if M("g10_follow_redirect"):
                status, body, hdrs = opener(host, path, headers, TIMEOUT, BODY_CAP)
            elif M("g10_3xx_stop"):
                return latch(status, body, hdrs, "a redirect")
            else:
                say("FAIL redirect (%s): a redirect is not followed; no STOP file is written" % status)
                return 3
        if M("g10_two_requests"):
            opener(host, path, headers, TIMEOUT, BODY_CAP)
    except SocketFault as e:
        if M("g10_timeout_stop"):
            create_stop(stop_path, stop_text("timeout", utc, path, "", ""))
        say("FAIL network (%s)" % e)
        return 3
    if status != 200:
        if M("g10_429_nostop") and status == 429:
            say("FAIL status 429")
            return 2
        return latch(status, body, hdrs, "HTTP status")
    problem = ("the body exceeds %d bytes" % BODY_CAP) if body is None else body_problem(body)
    if problem:
        return latch(status, body, hdrs, problem)
    sha = sha256_of(body)
    write_bytes(raw, body)
    row = {"vintage": v, "host": host, "url_path": path, "status": str(status), "bytes": str(len(body)), "sha256": sha, "retrieved_utc": utc, "elapsed_s": "%.3f" % (time.monotonic() - t0)}
    write_text(mp, manifest_text(v, row, "fetched"))
    say("fetched: status %d, bytes %d, sha256 %s" % (status, len(body), sha))
    if sha != REG_SHA256 or len(body) != REG_BYTES:
        say("WARN: size or sha256 differs from the registering vintage's workbook (expected for a later vintage)")
    return 0


# ------------------------------------------------------------------------------------------------------------------------
# command line
# ------------------------------------------------------------------------------------------------------------------------
def make_parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch", help="ONE request to www.richmondfed.org (network; supervisor only; later vintages only)")
    pf.add_argument("--vintage", required=True, help="YYYYMMDD: today's UTC date")
    pf.add_argument("--cache", default=None)
    pb = sub.add_parser("build", help="offline: validate the cached workbook and write the outputs of one stage")
    pb.add_argument("--vintage", required=True)
    pb.add_argument("--stage", required=True, choices=("pre", "dry", "full"))
    pb.add_argument("--cache", default=None)
    pb.add_argument("--out", default=None, help="the output folder (required for the dry stage; outside data/)")
    pb.add_argument("--registering", action="store_true", help="full stage only: the registering build (supervisor only); writes registered.csv once")
    pb.add_argument("--supersede", action="store_true", help="with --registering: mark the registered rows superseded and add corrected ones with the next version (P-S)")
    ps = sub.add_parser("selftest", help="synthetic data, mutants applied one at a time; no network")
    ps.add_argument("--no-mutants", action="store_true")
    ps.add_argument("--mutant", help="run every guard with this one mutant switched on; exit 1 when it is caught")
    return ap


def dispatch(a, root=None, say=print, err=None, opener=real_opener, now_utc=None):
    """Run one build or fetch and map every refusal to its exit code (0 ok; 2 data or STOP; 3 network or redirect; 4 HALT; 5 refused or UNIT_ERROR)."""
    err = err or (lambda s: print(s, file=sys.stderr))
    try:
        if a.cmd == "build":
            return run_build(a, say=say, root=root)
        return run_fetch(a, opener=opener, now_utc=now_utc, say=say, root=root)
    except Refused as e:
        err("refused: %s" % e)
        return 5
    except UnitError as e:
        err("UNIT_ERROR (exit 5): nothing is registered: %s" % e)
        return 5
    except Halt as e:
        err("HALT (exit 4): nothing is registered: %s" % e)
        return 4
    except WbError as e:
        err("HALT (exit 4): the workbook is not readable: %s" % e)
        return 4
    except DataError as e:
        err("STOP (data): %s" % e)
        return 2


def main(argv=None):
    a = make_parser().parse_args(argv)
    if a.cmd == "selftest":
        return selftest(mutants=not a.no_mutants, only=a.mutant)
    return dispatch(a)


# ==============================================================================================================================
# SELFTEST: synthetic data only. Every guard applies its own mutants one at a time; an uncaught mutant fails the selftest.
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


class FakeClock(object):
    """2026-11-02 12:00:00 UTC: not the registering vintage's day."""

    def __init__(self, t=1_793_620_800.0):
        self.t = t

    def now_utc(self):
        return dt.datetime.fromtimestamp(self.t, dt.timezone.utc)


@contextlib.contextmanager
def patched(**kw):
    g = globals()
    old = {k: g[k] for k in kw}
    g.update(kw)
    try:
        yield
    finally:
        g.update(old)


_CACHE = {}


def base_wb():
    if "wb" not in _CACHE:
        _CACHE["wb"] = synth_workbook()
    return _CACHE["wb"]


def big_body(n):
    if ("big", n) not in _CACHE:
        _CACHE[("big", n)] = synth_workbook(pad_to=n)
    return _CACHE[("big", n)]


class Tree(object):
    """A scratch repository root with one or more vintages of a synthetic workbook, built and run in-process."""

    def __init__(self, data=None, vintage="20261101"):
        self.td = tempfile.TemporaryDirectory(prefix="cfo_t_", ignore_cleanup_errors=True)
        self.root = self.td.name
        if data is not None:
            self.put(vintage, data)

    def put(self, vintage, data):
        p = os.path.join(self.root, "data", "vintages", "cfo_survey", vintage, "raw", WB_NAME)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(data)

    def out(self, *a):
        return os.path.join(self.root, "data", "cfo_equity_expectations", *a)

    def vdir(self, vintage="20261101"):
        return os.path.join(self.root, "data", "vintages", "cfo_survey", vintage)

    def read(self, name, vintage=None):
        p = self.out(name) if vintage is None else os.path.join(self.vdir(vintage), name)
        return read_file(p, "r") if os.path.isfile(p) else None

    def snapshot(self):
        d = os.path.join(self.root, "data")
        out = {}
        for r, _, fs in os.walk(d):
            for f in fs:
                p = os.path.join(r, f)
                out[os.path.relpath(p, self.root)] = sha256_of(read_file(p))
        return out

    def run(self, stage, vintage="20261101", registering=False, supersede=False, out=None, scout=None):
        ns = argparse.Namespace(cmd="build", vintage=vintage, stage=stage, cache=None, out=out, registering=registering, supersede=supersede)
        raw = os.path.join(self.vdir(vintage), "raw", WB_NAME)
        ref = scout if scout is not None else (read_file(raw) if os.path.isfile(raw) else b"")
        o, e = [], []
        with patched(REG_SHA256=sha256_of(ref), REG_BYTES=len(ref)):
            rc = dispatch(ns, root=self.root, say=o.append, err=e.append)
        return rc, o, e

    def close(self):
        self.td.cleanup()


@contextlib.contextmanager
def tree(data=None, vintage="20261101"):
    t = Tree(data, vintage)
    try:
        yield t
    finally:
        t.close()


def cell_over(a, b, col=COL_C10, sheet=SH_CUR, qa=WINDOW[0], qb=WINDOW[1]):
    return {(sheet, col, qa): a, (sheet, col, qb): b}


def stmt(over=None, sid="E1", sn="CUR10", start=WINDOW[0], end=WINDOW[1], pins="match", vdir=None, **kw):
    lay = analyse(synth_workbook(over=over or {}, **kw))
    hz = "10y" if sn == "CUR10" else "12m"
    return statement(sid, hz, sn, lay.series[sn], start, end, pins, "0" * 64, "20261101", 1, vdir)


def checks_by_id(text):
    return {r["check_id"]: r for r in read_csv_dicts(text)}


# ---- G1: parsing and rounding ----
def t_g1(ck):
    r = stmt(cell_over("9.123456", "9.223457"))
    ck.eq("the statistic is the exact difference of the rounded cells", r["stat_pp"], "0.100001")
    r = stmt(cell_over("0", "0.0999995"))
    ck.eq("0.0999995 rounds half-even to 0.100000", r["exp_end"], "0.100000")
    ck.eq("... so the difference is RISE", r["sign"], "RISE")
    r = stmt(cell_over("0", "0.1000005"))
    ck.eq("0.1000005 is a tie and goes to the even 0.100000", r["exp_end"], "0.100000")
    r = stmt(cell_over("9.6", "9.7000000000000002"))
    ck.eq("binary noise: 9.7000000000000002 less 9.6 is 0.100000", r["stat_pp"], "0.100000")
    r = stmt(cell_over("0.1", "0.3"))
    ck.eq("0.3 less 0.1 is exactly 0.2 (Decimal, not float)", r["stat_pp"], "0.200000")
    r = stmt(cell_over(None, "9.7"))
    ck.eq("an empty cell is not zero: VOID endpoint_undefined", (r["void_reason"], r["stat_pp"], r["exp_start"]), ("endpoint_undefined", "", ""))
    r = stmt(cell_over(("s", "9.6"), "9.7"))
    ck.eq("a text cell '9.6' is not a number: VOID", r["void_reason"], "endpoint_undefined")
    r = stmt(cell_over(("f",), "9.7"))
    ck.eq("a formula cell with no cached value is VOID", r["void_reason"], "endpoint_undefined")
    r = stmt(cell_over(("fv", "9.6"), "9.7"))
    ck.eq("a formula cell WITH a cached value is read", (r["void_reason"], r["stat_pp"]), ("none", "0.100000"))
    # the reader: shared strings, hidden rows and columns
    lay = analyse(base_wb())
    ck.eq("the fixture has no layout fault", lay.faults, [])
    ck.eq("shared strings land in the right cells (the required column is where the header says)", lay.tables[SH_CUR].cols.get(COL_C10), 5)
    lay = analyse(synth_workbook(hidden_cols={SH_CUR: {12}}, hidden_rows={SH_DUKE: {3}}))
    ck.eq("hidden rows and columns are counted", hidden_report(lay), (1, 1))
    try:
        import openpyxl
    except ImportError:
        openpyxl = None
    if openpyxl is not None:
        w = openpyxl.Workbook()
        s = w.active
        s.title = "t"
        s["A1"], s["B1"], s["A2"], s["B2"], s["C2"] = "hdr", 9.6, "x", 0.0999995, "=A1+B1"
        buf = io.BytesIO()
        w.save(buf)
        cells = read_workbook(buf.getvalue())["t"].cells
        ck.eq("another writer's workbook (openpyxl): text, numeric and a formula with no cached value read as such", (cells[1][0], cells[1][1], cells[2][2][0]), (("text", "hdr"), ("numeric", "9.6"), "nocache"))


# ---- G2: layout and keys ----
def halt_case(ck, name, **kw):
    lay = analyse(synth_workbook(**kw))
    ck.ok("%s: a layout fault" % name, bool(lay.faults), "no fault")
    with tree(synth_workbook(**kw)) as t:
        rc, o, e = t.run("full", registering=True)
        ck.eq("%s: exit 4 and nothing registered" % name, (rc, t.read("registered.csv")), (4, None))


def t_g2(ck):
    ck.eq("the full fixture has no fault", analyse(base_wb()).faults, [])
    for sn in SHEETS:
        halt_case(ck, "missing sheet " + sn, omit_sheet=sn)
    for col in (COL_D10, COL_D12, COL_C10, COL_C12):
        halt_case(ck, "missing column " + col, omit_col=col)
    dk, ck_ = q_list(*DUKE_KEYS), q_list(*CUR_KEYS)
    halt_case(ck, "73 Duke rows", duke_keys=dk[:-1])
    halt_case(ck, "75 Duke rows", duke_keys=dk + [(2020, 2)])
    halt_case(ck, "24 current rows", cur_keys=ck_[:-1])
    halt_case(ck, "26 current rows", cur_keys=ck_ + [(2026, 4)])
    d2 = list(dk)
    d2[34] = d2[33]
    halt_case(ck, "a duplicate quarter", duke_keys=d2)
    d3 = list(dk)
    d3[30], d3[31] = d3[31], d3[30]
    halt_case(ck, "non-consecutive quarters", duke_keys=d3)
    halt_case(ck, "2020Q2 present in the current sheet", cur_keys=[(2020, 2)] + ck_[:-1])
    for fmt in ("Q{q} {y}", "{q}Q{y}", "{y} Q{q}", "{y}-Q{q}"):
        lay = analyse(synth_workbook(key_fmt=fmt))
        ck.ok("key format %r parses" % fmt, lay.faults == [] and set(lay.series["CUR10"]) == set(analyse(base_wb()).series["CUR10"]), str(lay.faults)[:100])
    ck.eq("2020Q3 is read as 2020Q3", min(analyse(base_wb()).series["CUR10"]), (2020, 3))
    # two-sided: a stray empty is a WARN or a VOID, never a halt
    with tree(synth_workbook(over={(SH_DUKE, COL_D10, (2018, 4)): None})) as t:
        rc, o, e = t.run("full", registering=True)
        c = checks_by_id(t.read("checks.csv") or "") if rc == 0 else {}
        ck.eq("a Duke empty at 2018Q4: exit 0, C03 WARN", (rc, c.get("C03", {}).get("status")), (0, "WARN"))
    with tree(synth_workbook(over={(SH_CUR, COL_C10, (2022, 1)): None})) as t:
        rc, o, e = t.run("full", registering=True)
        c = checks_by_id(t.read("checks.csv") or "") if rc == 0 else {}
        ck.eq("an empty current _2 cell (not an endpoint): exit 0, C03 WARN", (rc, c.get("C03", {}).get("status")), (0, "WARN"))
    with tree(synth_workbook(over={(SH_CUR, COL_C10, WINDOW[1]): None})) as t:
        rc, o, e = t.run("full", registering=True)
        rows = read_csv_dicts(t.read("registered.csv") or "")
        ck.eq("an empty endpoint: exit 0 and a VOID E1 row", (rc, [r["void_reason"] for r in rows if r["statement_id"] == "E1"]), (0, ["endpoint_undefined"]))


# ---- G3: sign ----
def t_g3(ck):
    cases = ((("9.6", "9.6999"), "ZERO", "+0.0999"), (("9.6", "9.7"), "RISE", "+0.1000"), (("9.7", "9.6001"), "ZERO", "-0.0999"), (("9.7", "9.6"), "FALL", "-0.1000"),
             (("9.6", "9.7000000000000002"), "RISE", "binary noise"), (("9.6", "9.6"), "ZERO", "0"), (("9.6", "9.75"), "RISE", "+0.15"), (("9.75", "9.6"), "FALL", "-0.15"), (("0", "0.0999995"), "RISE", "0.0999995"))
    for (a, b), want, label in cases:
        r = stmt(cell_over(a, b))
        ck.eq("%s gives %s" % (label, want), r["sign"], want)


# ---- G4: VOID ----
def t_g4(ck):
    r = stmt(cell_over(None, "9.7"))
    ck.eq("empty endpoint: VOID row, no stat, sign none, spf_direction none", (r["void_reason"], r["stat_pp"], r["sign"], r["spf_direction"]), ("endpoint_undefined", "", "none", "none"))
    over = cell_over(None, "9.7")
    over[(SH_CUR, COL_C10, (2022, 1))] = "55"
    ck.eq("an empty endpoint and an out-of-bound cell: endpoint_undefined first", stmt(over)["void_reason"], "endpoint_undefined")
    for v, want in (("-20.0001", "unit_odd"), ("40.0001", "unit_odd"), ("-20", "none"), ("40", "none"), ("55", "unit_odd"), ("-25", "unit_odd")):
        r = stmt({(SH_CUR, COL_C10, (2022, 1)): v})
        ck.eq("a cell of %s: %s" % (v, want), r["void_reason"], want)
    r = stmt({(SH_CUR, COL_C10, (2022, 1)): "55"})
    ck.ok("unit_odd keeps its statistic and sign but spf_direction is none", r["stat_pp"] != "" and r["sign"] in ("RISE", "FALL", "ZERO") and r["spf_direction"] == "none", str(r))
    r2 = stmt({(SH_CUR, COL_C10, (2022, 1)): "55"}, sid="E2", sn="CUR12")
    ck.eq("the other horizon's column is tested on its own cells", r2["void_reason"], "none")
    with tree(synth_workbook(over=cell_over(None, "9.7"))) as t:
        rc, o, e = t.run("full", registering=True)
        ck.eq("an empty endpoint writes a VOID row, not a FAIL", (rc, ",FAIL" in (t.read("checks.csv") or "")), (0, False))


# ---- G5: direction ----
def t_g5(ck):
    for a, b, want in (("9.6", "9.8", "SAME"), ("9.8", "9.6", "OPPOSITE"), ("9.6", "9.65", "FLAT")):
        r = stmt(cell_over(a, b))
        ck.eq("%s to %s: %s" % (a, b, want), r["spf_direction"], want)
    r = stmt(cell_over("9.6", "9.8"), sid="E2", sn="CUR12", **{})
    ck.eq("E2 has spf_direction na and no SPF figure", (r["spf_direction"], r["spf_stat_pp"]), ("na", ""))
    r = stmt(cell_over("9.6", "9.8"))
    ck.eq("E1 carries 0.1543", r["spf_stat_pp"], "0.1543")
    with tempfile.TemporaryDirectory(prefix="cfo_v_", ignore_cleanup_errors=True) as vd:
        write_text(os.path.join(vd, "spf.txt"), "9.9999\n")
        r = stmt(cell_over("9.6", "9.8"), vdir=vd)
        ck.eq("a file next to the workbook does not change the SPF figure", r["spf_stat_pp"], "0.1543")
    with tree(base_wb()) as t:
        rc, o, e = t.run("full", registering=True)
        allt = "".join((t.read(n) or "") for n in COMMITTED)
        ck.ok("the words AGREES and DISAGREES appear in no output", rc == 0 and not re.search(r"AGREES|DISAGREES", allt), str(rc))


# ---- G6: pins ----
def pin_state(over):
    return pin_status(analyse(synth_workbook(over=over)).series)[0]


def t_g6(ck):
    ck.eq("the dry fixture's four planted pin values give match", pin_state({}), "match")
    ck.eq("+0.05 is still a match", pin_state({(SH_CUR, COL_C10, (2026, 2)): "9.75"}), "match")
    ck.eq("+0.0501 is near", pin_state({(SH_CUR, COL_C10, (2026, 2)): "9.7501"}), "near")
    ck.eq("-0.0501 is near", pin_state({(SH_CUR, COL_C12, (2026, 3)): "7.8499"}), "near")
    ck.eq("a pin 5 times the workbook value is a unit error", pin_state({(SH_CUR, COL_C10, (2026, 3)): "48"}), "unit_error")
    ck.eq("a pin 0.2 times the value is a unit error", pin_state({(SH_CUR, COL_C10, (2026, 3)): "1.92"}), "unit_error")
    ck.eq("a fraction (0.096 for 9.6) is a unit error", pin_state({(SH_CUR, COL_C10, (2026, 3)): "0.096"}), "unit_error")
    ck.eq("4.99 times is only near", pin_state({(SH_CUR, COL_C10, (2026, 3)): "47.904"}), "near")
    ck.eq("0.21 times is only near", pin_state({(SH_CUR, COL_C10, (2026, 3)): "2.016"}), "near")
    ck.eq("a pin cell with no number is near, not a unit error", pin_state({(SH_CUR, COL_C10, (2026, 3)): None}), "near")
    with tree(synth_workbook(over={(SH_CUR, COL_C10, (2026, 3)): "48"})) as t:
        rc, o, e = t.run("full", registering=True)
        ck.eq("a factor-5 pin: exit 5 and no registered.csv", (rc, t.read("registered.csv")), (5, None))
    with tree(synth_workbook(over={(SH_CUR, COL_C10, (2026, 2)): "9.7501"})) as t:
        rc, o, e = t.run("full", registering=True)
        rows = read_csv_dicts(t.read("registered.csv") or "")
        c = checks_by_id(t.read("checks.csv") or "")
        ck.eq("NEAR: the run continues, pins = near is written, C04 is a WARN", (rc, {r["pins"] for r in rows}, c.get("C04", {}).get("status")), (0, {"near"}, "WARN"))
    with tree(base_wb()) as t:
        rc, o, e = t.run("full", registering=True)
        rows = read_csv_dicts(t.read("registered.csv") or "")
        ck.eq("MATCH: pins = match", (rc, {r["pins"] for r in rows}), (0, {"match"}))
    # a pin never enters a statistic
    r = stmt({(SH_CUR, COL_C10, (2026, 2)): "9.74", (SH_CUR, COL_C10, (2026, 3)): "9.66"}, start=(2026, 2), end=(2026, 3))
    ck.eq("a statistic over the pinned quarters uses the workbook cells, not the pins", r["stat_pp"], "-0.080000")


# ---- G7: windows and break ----
def duke_reference(col_j):
    """Independent recomputation of the Duke range from the fixture's own formula (not from the library)."""
    ks = q_list(*DUKE_KEYS)
    val = {}
    for i, k in enumerate(ks):
        if k in ((2019, 1), (2020, 1)):
            continue
        val[k] = Decimal(base_value(i, col_j))
    ch = []
    for i in range(qi((2004, 1)), qi((2020, 1)) + 1):
        e = qk(i)
        s = qk(i - 8)
        if e in val and s in val:
            ch.append(val[e] - val[s])
    return len(ch), min(ch), max(ch)


def t_g7(ck):
    lay = analyse(base_wb())
    ys = {r["yardstick"]: r for r in yardstick_rows(lay.series)}
    ck.eq("Y10: end quarters 2004Q1 to 2020Q1", (ys["Y10"]["first_end_quarter"], ys["Y10"]["last_end_quarter"]), ("2004Q1", "2020Q1"))
    ck.eq("Y10 and Y12: 65 nominal, 63 defined", [(ys[y]["n_nominal"], ys[y]["n_defined"]) for y in ("Y10", "Y12")], [("65", "63")] * 2)
    ck.eq("YC10 and YC12: end quarters 2022Q3 to 2026Q3, 17 nominal, 16 defined", [(ys[y]["first_end_quarter"], ys[y]["last_end_quarter"], ys[y]["n_nominal"], ys[y]["n_defined"]) for y in ("YC10", "YC12")], [("2022Q3", "2026Q3", "17", "16")] * 2)
    ck.eq("disjoint spans 8 and 3", [ys[y]["max_disjoint_spans"] for y in ("Y10", "YC10")], ["8", "3"])
    n, mn, mx = duke_reference(2)
    ck.eq("Y10 min, max and n equal an independent recomputation", (ys["Y10"]["n_defined"], ys["Y10"]["min_change_pp"], ys["Y10"]["max_change_pp"]), (str(n), fmt6(mn), fmt6(mx)))
    n, mn, mx = duke_reference(5)
    ck.eq("Y12 min, max and n equal an independent recomputation", (ys["Y12"]["n_defined"], ys["Y12"]["min_change_pp"], ys["Y12"]["max_change_pp"]), (str(n), fmt6(mn), fmt6(mx)))
    ye = y_ends()
    ce = yc_ends()
    ck.eq("Y end quarters: 2003Q4 out, 2004Q1 in, 2020Q1 in, 2020Q2 out", ((2003, 4) in ye, (2004, 1) in ye, (2020, 1) in ye, (2020, 2) in ye), (False, True, True, False))
    ck.eq("YC end quarters: 2022Q2 out, 2022Q3 in, 2026Q3 in, 2026Q4 out", ((2022, 2) in ce, (2022, 3) in ce, (2026, 3) in ce, (2026, 4) in ce), (False, True, True, False))
    # q-8 by calendar arithmetic across a deleted row
    cells = dict(lay.series["DUKE10"])
    del cells[(2010, 1)]
    ch = window_changes({"duke": cells, "current": {}}, ye)
    ck.eq("with 2010Q1 deleted, the window ending 2012Q1 is not defined and no other is moved", ((2012, 1) in [e for _, e, _ in ch], len(ch)), (False, 61))
    ck.ok("every window starts exactly eight calendar quarters before its end", all(qi(e) - qi(s) == 8 for s, e, _ in ch), "")
    # the 2020 break
    eras = {"duke": lay.series["DUKE10"], "current": lay.series["CUR10"]}
    ck.raises("a window from 2020Q1 to 2020Q3 is refused", CrossBreak, lambda: change_between(eras, (2020, 1), (2020, 3)))
    ck.raises("a window from 2019Q4 to 2020Q2 is refused", CrossBreak, lambda: change_between(eras, (2019, 4), (2020, 2)))
    ck.raises("a Duke level subtracted from a current level is refused", CrossBreak, lambda: change_between(eras, (2019, 4), (2024, 1)))
    ck.eq("inside one era a change is returned", change_between(eras, (2024, 1), (2026, 1))[2], cell_r6(eras["current"][(2026, 1)]) - cell_r6(eras["current"][(2024, 1)]))
    ck.eq("YC leaves out the registered window (16 changes, none ends 2026Q1)", (len(window_changes({"duke": {}, "current": lay.series["CUR10"]}, ce, (WINDOW[1],))), (2026, 1) in [e for _, e, _ in window_changes({"duke": {}, "current": lay.series["CUR10"]}, ce, (WINDOW[1],))]), (16, False))


# ---- G8: registered write-once, supersede, the hash ----
def t_g8(ck):
    with tree(base_wb()) as t:
        rc, o, e = t.run("full", registering=True)
        ck.eq("the registering build succeeds", rc, 0)
        reg0 = t.read("registered.csv")
        ck.ok("registered.csv exists with E1 and E2, version 1, superseded no", reg0 is not None and [(r["statement_id"], r["version"], r["superseded"]) for r in read_csv_dicts(reg0)] == [("E1", "1", "no"), ("E2", "1", "no")], str(reg0)[:80])
        snap = {n: t.read(n) for n in COMMITTED + LOCAL}
        rc, o, e = t.run("full")
        ck.eq("a repeat build of the same vintage succeeds", rc, 0)
        ck.eq("... and is byte-identical in every file", {n: t.read(n) for n in COMMITTED + LOCAL}, snap)
        rcr, o, e = t.run("full", registering=True)
        ck.eq("a second registering build is refused", rcr, 5)
        ck.eq("... and registered.csv is unchanged", t.read("registered.csv"), reg0)
        # a later vintage
        t.put("20261220", synth_workbook(over={(SH_CUR, COL_C10, WINDOW[1]): "9.9", (SH_CUR, COL_C12, (2026, 3)): "7.9"}))
        rc, o, e = t.run("full", vintage="20261220", scout=base_wb())
        ck.eq("a later vintage builds", rc, 0)
        ck.eq("... and does not rewrite registered.csv", t.read("registered.csv"), reg0)
        c12 = checks_by_id(t.read("checks.csv") or "").get("C12", {}).get("observed", "")
        ck.ok("... C12 reports the revision and the README says so", "registered" in c12 and "Revision since the registering vintage" in (t.read("README.md") or ""), c12[:80])
        # supersede
        rc, o, e = t.run("full", vintage="20261220", registering=True, supersede=True, scout=base_wb())
        ck.eq("--registering --supersede succeeds", rc, 0)
        rows = read_csv_dicts(t.read("registered.csv") or "")
        old0 = read_csv_dicts(reg0)
        ck.eq("the old rows are kept with superseded = yes, the new ones are version 2 with superseded = no",
              [(r["statement_id"], r["version"], r["superseded"]) for r in rows], [("E1", "1", "yes"), ("E2", "1", "yes"), ("E1", "2", "no"), ("E2", "2", "no")])
        ck.ok("... the old rows are otherwise unchanged", all({k: v for k, v in o_.items() if k != "superseded"} == {k: v for k, v in n_.items() if k != "superseded"} for o_, n_ in zip(old0, rows[:2])), "")
        ck.ok("... the README lists the superseded rows", "is superseded" in (t.read("README.md") or ""), "")
    with tree(base_wb()) as t:
        edited = tuple(PREREG_LINES[:-1]) + (PREREG_LINES[-1] + "x",)
        with patched(PREREG_LINES=edited):
            rc, o, e = t.run("full", registering=True)
        ck.eq("a constant edited: the build refuses (exit 5) and writes no registered.csv", (rc, t.read("registered.csv")), (5, None))
    with tree(base_wb()) as t:
        rc, o, e = t.run("full", registering=True)
        rows = read_csv_dicts(t.read("registered.csv") or "")
        recomputed = sha256_of(("\n".join(PREREG_LINES) + "\n").encode("utf-8"))
        ck.ok("prereg_sha256 is the hash of the 4.6 block recomputed from the constants and equals the spec's", rows and all(r["prereg_sha256"] == recomputed == SPEC_PREREG_SHA256 for r in rows), "")
    good = dict(zip(ALLOW["registered.csv"], ["E1", "1", "no", "10y", "CUR10", "20261101", "a" * 64, "2024Q1", "2026Q1", "1.000000", "1.500000", "0.500000", "RISE", "none", "full", "match", "0.1543", "SAME", SPEC_PREREG_SHA256]))
    good2 = dict(good, statement_id="E2", horizon="12m", series="CUR12", spf_stat_pp="", spf_direction="na")
    ck.eq("two clean live rows pass the registered-row rules", registered_problems([good, good2]), [])
    ck.ok("a second non-superseded E1 row is reported", bool(registered_problems([good, good2, dict(good, version="2")])), "")
    ck.ok("a hash that is not the 4.6 hash is reported", bool(registered_problems([dict(good, prereg_sha256="b" * 64), good2])), "")


# ---- G9: wording ----
def t_g9(ck):
    with tree(base_wb()) as t:
        t.run("full", registering=True)
        readme = t.read("README.md") or ""
    ck.eq("the real README passes the wording guard and holds R-A to R-D", readme_problems(readme), [])
    for label, bad in (("expectations rose because of the rally", "because of"), ("a significant rise", "significan"), ("the highest since 2001", "highest"), ("the surveys agree", "agree"),
                       ("comparable two-year changes", "comparable"), ("an unusual rise", "unusual"), ("the rise was driven by earnings", "driven"), ("this confirms the page", "confirm"),
                       ("a level since 2001 held", "since 2001"), ("the highest level", "highest"), ("the lowest print", "lowest"), ("a record rise", "record")):
        ck.ok("%r is caught" % label, bool(readme_problems(readme + "\n" + label + "\n")), "")
    for tag, s in REQUIRED_SENTENCES:
        ck.ok("a README without %s is caught" % tag, bool(readme_problems(readme.replace(s, "removed"))), "")
    ck.ok("a banned verdict word is caught", bool(readme_problems(readme + "\nHELD\n")), "")
    ck.ok("the sentence 'since' without a year is allowed", not wording_problems("They have been asked since the survey began."), "")


# ---- G10: fetch safety ----
class Opener(object):
    def __init__(self, status=200, body=None, hdrs=None, fault=False, seq=None):
        self.calls, self.status, self.body, self.hdrs, self.fault, self.seq = [], status, body, hdrs or {}, fault, seq

    def __call__(self, host, target, headers, timeout, cap):
        self.calls.append((host, target, dict(headers), timeout))
        if self.fault:
            raise SocketFault("TimeoutError")
        if self.seq:
            i = min(len(self.calls) - 1, len(self.seq) - 1)
            return self.seq[i]
        return self.status, self.body, self.hdrs


def fetch(opener, vintage="20261102", url=URL, pre_stop=False, t=None):
    own = t is None
    t = t or Tree()
    try:
        if pre_stop:
            os.makedirs(t.vdir("").rstrip(os.sep), exist_ok=True)
            write_via_open(os.path.join(os.path.dirname(t.vdir("x")), STOP_NAME), "status: 403\n")
        ns = argparse.Namespace(cmd="fetch", vintage=vintage, cache=None)
        o, e = [], []
        try:
            rc = run_fetch(ns, opener=opener, now_utc=FakeClock().now_utc, say=o.append, url=url, root=t.root)
        except Refused as ex:
            rc = "refused"
        stop = os.path.join(t.root, "data", "vintages", "cfo_survey", STOP_NAME)
        return rc, o, (read_file(stop, "r") if os.path.isfile(stop) else None), t
    finally:
        if own:
            t.close()


def write_via_open(p, text):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "x", encoding="utf-8") as fh:
        fh.write(text)


def t_g10(ck):
    good = big_body(60000)
    op = Opener(200, good)
    rc, o, stop, t = fetch(op, t=Tree())
    try:
        ck.eq("a good response: exit 0, exactly one request", (rc, len(op.calls)), (0, 1))
        h, tg, hd, to = op.calls[0] if op.calls else ("", "", {}, 0)
        ck.eq("the request goes to www.richmondfed.org and the one path, timeout 300", (h, tg, to), (HOST, URL_PATH, 300))
        ua = hd.get("User-Agent")
        ck.ok("the agent string is the neutral one: no at sign, no http, no dotted address", bool(ua) and chr(64) not in ua and "http" not in ua.lower() and not re.search(r"\d+[.]\d+[.]\d+[.]\d+", ua), str(ua))
        ck.eq("... and it is the one string the script defines", ua, USER_AGENT)
        ck.eq("Accept-Encoding is identity", hd.get("Accept-Encoding"), "identity")
        mr = manifest_rows(t.vdir("20261102"))
        ck.eq("MANIFEST has 1 row: host, status 200, bytes and sha256", [(r["host"], r["status"], r["bytes"], r["sha256"]) for r in mr], [(HOST, "200", "60000", sha256_of(good))])
        ck.ok("the body is in raw/ and no STOP file exists", os.path.isfile(os.path.join(t.vdir("20261102"), "raw", WB_NAME)) and stop is None, "")
        op2 = Opener(200, good)
        rc2, o2, stop2, _ = fetch(op2, t=t)
        ck.eq("a repeat run on the same day makes no request", (rc2, len(op2.calls)), (0, 0))
    finally:
        t.close()
    for label, url in (("another host", "https://example.com" + URL_PATH), ("http", "http://" + HOST + URL_PATH), ("a query", URL + "?x=1"), ("another path", "https://" + HOST + "/other.xlsx"), ("a port", "https://" + HOST + ":8443" + URL_PATH)):
        op = Opener(200, good)
        rc, o, stop, _ = fetch(op, url=url)
        ck.eq("%s: refused before any request" % label, (rc, len(op.calls)), ("refused", 0))
    op = Opener(301, b"moved", {"location": "https://" + HOST + "/x"})
    rc, o, stop, _ = fetch(op)
    ck.eq("a 3xx is a FAIL (exit 3), one request, no STOP", (rc, len(op.calls), stop), (3, 1, None))
    for st in (403, 429, 500):
        op = Opener(st, b"<html>nope</html>", {"retry-after": "60"})
        rc, o, stop, _ = fetch(op)
        ck.ok("%d: exit 2, one request, a STOP with five fields" % st, rc == 2 and len(op.calls) == 1 and stop is not None and stop_text_ok(stop), "%r %r %r" % (rc, len(op.calls), stop))
    html = b"<html>" + b" " * 60000
    for label, body in (("an empty body", b""), ("an HTML body", html), ("a non-zip 200 body", b"x" * 60000), ("a valid but small workbook", base_wb()), ("49,999 bytes", big_body(49999)), ("2,000,001 bytes", big_body(2000001))):
        op = Opener(200, body)
        rc, o, stop, _ = fetch(op)
        ck.ok("%s: exit 2 and a STOP with five fields" % label, rc == 2 and stop is not None and stop_text_ok(stop), "%r %r" % (rc, stop))
    for n in (50000, 2000000):
        op = Opener(200, big_body(n))
        rc, o, stop, _ = fetch(op)
        ck.eq("%d bytes: accepted, no STOP" % n, (rc, stop), (0, None))
    op = Opener(200, good)
    rc, o, stop, _ = fetch(op, pre_stop=True)
    ck.eq("a planted STOP_cfo blocks the request (exit 2)", (rc, len(op.calls)), (2, 0))
    op = Opener(fault=True)
    rc, o, stop, _ = fetch(op)
    ck.eq("a timeout: exit 3, one request, no STOP", (rc, len(op.calls), stop), (3, 1, None))
    op = Opener(200, good)
    rc, o, stop, _ = fetch(op, vintage="20261101")
    ck.eq("the registering vintage is never fetched", (rc, len(op.calls)), ("refused", 0))
    rc, o, stop, _ = fetch(op, vintage="20261103")
    ck.eq("a vintage that is not today's UTC date is refused", (rc, len(op.calls)), ("refused", 0))


# ---- G11: stages ----
def decimals_in(lines):
    return [l for l in lines if re.search(r"[0-9]+\.[0-9]{2,}", l)]


def t_g11(ck):
    lay = analyse(base_wb())
    cell_texts = {v[1] for sn in SERIES_ORDER for v in lay.series[sn].values() if v[0] == "numeric"}
    with tree(base_wb()) as t:
        before = STATS["conv"]
        rc, o, e = t.run("pre")
        conv = STATS["conv"] - before
        files = {n: t.read(n) or "" for n in ("checks.csv",)}
        blob = "\n".join(o) + "\n" + "\n".join(files.values())
        found = sorted(x for x in cell_texts if re.search(r"(?<![\d.])" + re.escape(x) + r"(?![\d.])", blob))
        ck.eq("pre: exit 0 and writes only checks.csv", (rc, sorted(os.listdir(t.out()))), (0, ["checks.csv"]))
        ck.eq("pre converts no S&P cell", conv, 0)
        ck.eq("pre prints and writes no S&P cell text", found, [])
        ck.eq("pre prints no number with two decimals outside dates and sha256 text", decimals_in(o), [])
        ck.ok("pre's checks.csv holds no FAIL", ",FAIL" not in files["checks.csv"], "")
    with tree(base_wb()) as t:
        snap = t.snapshot()
        out = os.path.join(t.root, "scratch")
        rc, o, e = t.run("dry")
        ck.eq("dry without --out is refused and writes nothing", (rc, t.snapshot() == snap), (5, True))
        rc, o, e = t.run("dry", out=os.path.join(t.root, "data", "cfo_equity_expectations"))
        ck.eq("dry with --out under data/ is refused and writes nothing", (rc, t.snapshot() == snap), (5, True))
        rc, o, e = t.run("dry", out=out)
        ck.eq("dry with --out succeeds, writes five files there and nothing under data/", (rc, sorted(os.listdir(out)) if os.path.isdir(out) else None, t.snapshot() == snap),
              (0, ["README.md", "checks.csv", "path.csv", "registered.csv", "yardstick.csv"], True))
        bad = []
        for n in os.listdir(out) if os.path.isdir(out) else []:
            for l in read_file(os.path.join(out, n), "r").splitlines():
                if re.search("synthetic", l, re.I) and not l.startswith("# source:"):
                    bad.append("%s: %s" % (n, l[:50]))
        ck.eq("SYNTHETIC appears only in a `# source:` line", bad, [])
        ck.ok("the dry fixture plants the four pins (match) and the dry checks hold no FAIL", ",FAIL" not in read_file(os.path.join(out, "checks.csv"), "r") and "pins" in read_file(os.path.join(out, "registered.csv"), "r") and ",match," in read_file(os.path.join(out, "registered.csv"), "r"), "")
    with tree(base_wb()) as t:
        rc, o, e = t.run("full")
        ck.eq("full without --registering and without a registered.csv is refused", (rc, t.read("registered.csv")), (5, None))
        rc, o, e = t.run("full", supersede=True)
        ck.eq("--supersede without --registering is refused", rc, 5)
        rc, o, e = t.run("full", registering=True, scout=b"other bytes")
        ck.eq("the registering vintage with other bytes than the scouting values is a FAIL (exit 2), nothing registered", (rc, t.read("registered.csv")), (2, None))
    # mixing vintages
    with tree(base_wb()) as t:
        rc, o, e = t.run("pre")
        mp = os.path.join(t.vdir(), "MANIFEST.csv")
        write_via_open_over(mp, read_file(mp, "r").replace("20261101,", "20260101,", 1))
        rc, o, e = t.run("full", registering=True)
        ck.eq("a MANIFEST row that names another vintage is refused", (rc, t.read("registered.csv")), (5, None))
    with tree(base_wb()) as t:
        rc, o, e = t.run("pre")
        t.put("20261101", base_wb() + b"x")
        rc, o, e = t.run("full", registering=True, scout=base_wb())
        ck.eq("a workbook that no longer matches its MANIFEST row is refused", (rc, t.read("registered.csv")), (5, None))
    with tree(base_wb()) as t:
        rc, o, e = t.run("full", registering=True)
        t.put("20261001", base_wb())
        rc, o, e = t.run("full", vintage="20261001", scout=base_wb())
        ck.eq("a vintage older than the registering one is refused", rc, 5)


def write_via_open_over(p, text):
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


# ---- G12: outputs and leak ----
def clean_files():
    with tree(base_wb()) as t:
        t.run("full", registering=True)
        return {n: t.read(n) for n in COMMITTED}


def checksh_problems(text):
    """The M29 guard in bin/check.sh holds its own literal copy of the four allowlist lines and of the 4.6 hash, and never reads them from this script."""
    if M("g12_checksh_lax"):
        return []
    a = text.find("cfo_leak_check() {")
    region = text[a:text.find("\n}\n", a) + 3] if a >= 0 else ""
    if not region:
        return ["bin/check.sh has no cfo_leak_check function"]
    out = []
    for l in SPEC_ALLOW_TEXT.splitlines():
        name, hdr = l.split(":", 1)
        if name == "path.csv":
            ok = ("'%s'" % hdr) in region
        else:
            ok = ("%s) want='%s'" % (name, hdr)) in region
        if not ok:
            out.append("check.sh does not hold the literal header of %s" % name)
    if ("local PREREG_SHA='%s'" % SPEC_PREREG_SHA256) not in region:
        out.append("check.sh does not hold the literal 4.6 hash")
    if re.search(r"cfo_equity_expectations\.py", region):
        out.append("check.sh names the script inside the guard (it must not read the headers from it)")
    return out


def t_g12(ck):
    files = clean_files()
    ck.eq("the clean folder passes every rule", folder_problems(files), [])
    y = files["yardstick.csv"]
    lines = y.split("\n")
    ck.ok("an extra column is reported", bool(folder_problems(dict(files, **{"yardstick.csv": "\n".join([lines[0], lines[1] + ",note"] + [l + ",x" for l in lines[2:-1]]) + "\n"}))), "")
    ck.ok("a renamed column is reported", bool(folder_problems(dict(files, **{"yardstick.csv": y.replace("n_defined", "n_def", 1)}))), "")
    ck.ok("a fifth CSV is reported", bool(folder_problems(dict(files, **{"extra.csv": "a,b\n1,2\n"}))), "")
    ck.ok("a duplicate key is reported", bool(folder_problems(dict(files, **{"yardstick.csv": y + lines[2] + "\n"}))), "")
    ck.ok("path.csv in the committed list is reported", bool(folder_problems(dict(files, **{"path.csv": "era,horizon,quarter,exp,status,survey_open,survey_close\n"}))), "")
    ck.ok("a committed file without the credit line is reported", bool(folder_problems(dict(files, **{"checks.csv": files["checks.csv"].split("\n", 1)[1]}))), "")
    ck.ok("an .xlsx in the folder is reported", bool(folder_problems(dict(files, **{"w.xlsx": b"PK\x03\x04plain"}))), "")
    ck.ok("a .json in the folder is reported", bool(folder_problems(dict(files, **{"w.json": "{}"}))), "")
    ck.ok("a /Users/ path is reported", bool(folder_problems(dict(files, **{"README.md": files["README.md"] + "\n/Users/x/y\n"}))), "")
    ck.ok("an at sign is reported", bool(folder_problems(dict(files, **{"README.md": files["README.md"] + "\nname at" + chr(64) + "host\n"}))), "")
    ck.ok("a STOP file is reported", bool(folder_problems(dict(files, **{"STOP_cfo": "x"}))), "")
    ck.ok("a header read from the `# source:` line would flag the clean folder", folder_problems(files) == [], "")
    # the writer: a build whose writer adds a column would be caught by its own guard
    with tree(base_wb()) as t:
        rc, o, e = t.run("full", registering=True)
        ck.eq("a build writes exactly the five files", (rc, sorted(os.listdir(t.out()))), (0, ["README.md", "checks.csv", "path.csv", "registered.csv", "yardstick.csv"]))
    # M29 holds its own literal copies
    cs = read_file(os.path.join(ROOT, "bin", "check.sh"), "r")
    ck.eq("bin/check.sh M29 holds the four allowlist lines and the hash as literals", checksh_problems(cs), [])
    ck.ok("a check.sh with an edited header is reported", bool(checksh_problems(cs.replace("n_defined,min_change_pp", "n_defined,min_pp", 1))), "")
    ck.ok("a check.sh with an edited hash is reported", bool(checksh_problems(cs.replace(SPEC_PREREG_SHA256, "0" * 64))), "")


# ---- X1: end to end, and M29 on a clean and a planted copy ----
def m29_run(files, extra=None, reg_sha=None, vint_files=None):
    """Run the bash function cfo_leak_check of bin/check.sh on a scratch copy; returns the lines that carry a cross."""
    cs = read_file(os.path.join(ROOT, "bin", "check.sh"), "r")
    a = cs.find("cfo_leak_check() {")
    region = cs[a:cs.find("\n}\n", a) + 3] if a >= 0 else ""
    with tempfile.TemporaryDirectory(prefix="cfo_m29_", ignore_cleanup_errors=True) as tmp:
        d, v = os.path.join(tmp, "out"), os.path.join(tmp, "vint")
        os.makedirs(d)
        os.makedirs(os.path.join(v, "20261101", "raw"))
        for n, x in dict(files, **(extra or {})).items():
            with open(os.path.join(d, n), "wb") as fh:
                fh.write(x if isinstance(x, bytes) else x.encode("utf-8"))
        for n, x in (vint_files or {"MANIFEST.csv": "a,b\n"}).items():
            with open(os.path.join(v, "20261101", n), "w") as fh:
                fh.write(x)
        script = os.path.join(tmp, "m29.sh")
        with open(script, "w") as fh:
            fh.write(region + '\nCFO_DIR="$1" CFO_VDIR="$2" cfo_leak_check\n')
        env = dict(os.environ)
        if reg_sha:
            env["CFO_REG_SHA"] = reg_sha
        r = subprocess.run(["bash", script, d, v], capture_output=True, text=True, timeout=120, env=env)
    return [l for l in r.stdout.splitlines() if "✗" in l], r.stdout, r.stderr


def t_x1(ck):
    files = clean_files()
    crosses, out, err = m29_run(files)
    ck.eq("M29 prints no cross on the clean folder", crosses, [])
    ck.ok("M29 prints a pass line on the clean folder", "✓" in out, out[:200])
    reg_hash = sha256_of(files["registered.csv"].encode("utf-8"))
    crosses, out, err = m29_run(files, reg_sha=reg_hash)
    ck.eq("M29 with REG_SHA equal to the file's hash prints no cross", crosses, [])
    faults = {
        "a changed registered byte (prereg_sha256)": ({"registered.csv": files["registered.csv"].replace(SPEC_PREREG_SHA256, "f" + SPEC_PREREG_SHA256[1:])}, None, "prereg_sha256"),
        "a registered byte against REG_SHA": ({"registered.csv": files["registered.csv"].replace("RISE", "FALL", 1).replace("ZERO", "FALL", 1)}, reg_hash, "REG_SHA"),
        "a renamed header": ({"yardstick.csv": files["yardstick.csv"].replace("n_defined", "n_def", 1)}, None, "header of yardstick.csv"),
        "a README missing R-B": ({"README.md": files["README.md"].replace(R_B, "")}, None, "R-B"),
        "a yardstick row that crosses 2020": ({"yardstick.csv": files["yardstick.csv"].replace("Y10,10y,2004Q1,2020Q1", "Y10,10y,2004Q1,2020Q3", 1)}, None, "Y10"),
        "a YC row that reaches back before 2022Q3": ({"yardstick.csv": files["yardstick.csv"].replace("YC10,10y,2022Q3", "YC10,10y,2022Q2", 1)}, None, "YC10"),
        "a registered window that starts before 2020Q3": ({"registered.csv": files["registered.csv"].replace(",2024Q1,", ",2020Q1,", 1)}, None, "start_quarter"),
        "a README line 'the highest since 2001'": ({"README.md": files["README.md"] + "\nthe highest since 2001\n"}, None, "README.md holds wording"),
        "a planted path.csv in the committed folder": ({"path.csv": "era,horizon,quarter,exp,status,survey_open,survey_close\n"}, None, "path.csv in the committed folder"),
        "a planted .xlsx": ({"w.xlsx": b"PK\x03\x04plain"}, None, "raw file"),
        "a planted .json": ({"w.json": "{}"}, None, "raw file"),
        "a local path in a committed file": ({"README.md": files["README.md"] + "\n/Users/x/y\n"}, None, "local path"),
        "an at sign in a committed file": ({"README.md": files["README.md"] + "\nx" + chr(64) + "y\n"}, None, "at sign"),
        "a fifth name": ({"extra.csv": "a\n"}, None, "four committed names"),
    }
    for label, (extra, rs, needle) in faults.items():
        crosses, out, err = m29_run(files, extra=extra, reg_sha=rs)
        ck.ok("M29 prints at least one line for %s" % label, any(needle in c for c in crosses), "%s | %s" % (needle, crosses[:3]))
    crosses, out, err = m29_run(files, vint_files={"MANIFEST.csv": "a\n", "current_historical_cfo_data.xlsx": "x"})
    ck.ok("M29 reports a workbook in a vintage folder", any("vintage folder" in c for c in crosses), str(crosses[:2]))
    # M29 on a folder that does not exist prints a pass line
    cs = read_file(os.path.join(ROOT, "bin", "check.sh"), "r")
    a0 = cs.find("cfo_leak_check() {")
    region = cs[a0:cs.find("\n}\n", a0) + 3] if a0 >= 0 else ""
    with tempfile.TemporaryDirectory(prefix="cfo_m29_", ignore_cleanup_errors=True) as tmp:
        script = os.path.join(tmp, "m29.sh")
        with open(script, "w") as fh:
            fh.write(region + '\nCFO_DIR="$1" cfo_leak_check\n')
        r = subprocess.run(["bash", script, os.path.join(tmp, "absent")], capture_output=True, text=True, timeout=60)
    ck.ok("M29 on an absent folder prints a pass line", "absent" in r.stdout and "✗" not in r.stdout, r.stdout[:100] + r.stderr[:100])


# ---- the table of guards and the runner ----
GUARDS = [
    ("G1", "parsing and rounding (Decimal, empty is not 0, text and formula cells, half-even to 6 decimals, the exact difference, shared strings, hidden columns)",
     ["g1_float", "g1_empty_zero", "g1_text_ok", "g1_nocache_ok", "g1_no_round", "g1_diff_round", "g1_half_up", "g1_sst_off", "g1_hidden_ignored"], t_g1),
    ("G2", "layout and keys (HALT exit 4: sheets, columns, 74/25 rows, duplicates, gaps, 2020Q3 read as 2020Q3; a stray empty is a WARN or a VOID)",
     ["g2_q_off", "g2_count_lax", "g2_gap_ok", "g2_dup_ok", "g2_sheet_ok", "g2_empty_halts"], t_g2),
    ("G3", "sign (+0.0999, +0.1000, -0.0999, -0.1000, binary noise)", ["g3_float", "g3_gt", "g3_wide", "g3_nozone", "g3_neg_lt"], t_g3),
    ("G4", "VOID (order, -20 and 40 inside, -20.0001 and 40.0001 outside, no FAIL, no sign on an undefined statistic, spf_direction none)",
     ["g4_void_fail", "g4_order_swapped", "g4_unit_edge", "g4_unit_lax", "g4_sign_on_undef", "g4_dir_on_void"], t_g4),
    ("G5", "direction (SAME, OPPOSITE, FLAT; na for E2; never AGREES or DISAGREES; the SPF figure is fixed text)",
     ["g5_map_swap", "g5_zero_same", "g5_agrees_word", "g5_e2_dir", "g5_spf_file", "g5_spf_wrong"], t_g5),
    ("G6", "pins (match at 0.05, near at 0.0501, a factor of 5 or 0.2 is a unit error with exit 5, near continues, no pin in a statistic)",
     ["g6_tol_strict", "g6_tol_wide", "g6_factor_gt", "g6_factor_low", "g6_no_fraction", "g6_near_halts", "g6_near_silent", "g6_unit_continues", "g6_pin_in_stat"], t_g6),
    ("G7", "windows and the break (q-8 by calendar, end quarters at the edges, 65/63 and 17/16, no window across 2020, no current value in the Duke range)",
     ["g7_row_pos", "g7_y_lo_out", "g7_y_lo_in", "g7_y_hi_out", "g7_y_hi_in", "g7_yc_lo_out", "g7_yc_lo_in", "g7_yc_hi_out", "g7_yc_hi_in", "g7_yc_keeps_window", "g7_cross_ok", "g7_duke_from_current"], t_g7),
    ("G8", "registered write-once (not rewritten by a later vintage, byte-identical repeat, supersede keeps the old row, one live row, the hash, a constant edited refuses)",
     ["g8_rewrite_registered", "g8_nondeterministic", "g8_supersede_deletes", "g8_two_live", "g8_supersede_noversion", "g8_hash_wrong", "g8_no_refuse", "g8_validator_lax", "g8_registering_twice"], t_g8),
    ("G9", "wording (causal, price and misconduct patterns plus since, extremes, comparable, unusual, agrees, confirm; R-A to R-D; verdict words)",
     ["g9_causal_off", "g9_extra_off", "g9_since_off", "g9_extremes_off", "g9_comparable_off", "g9_unusual_off", "g9_agrees_off", "g9_confirm_off", "g9_required_lax", "g9_verdict_off"], t_g9),
    ("G10", "fetch safety (one host, one request, no redirect, no retry, STOP rules and sizes, generic User-Agent, cache, planted STOP, timeout)",
     ["g10_other_host", "g10_two_requests", "g10_follow_redirect", "g10_retry", "g10_3xx_stop", "g10_ua_contact", "g10_recache", "g10_429_nostop", "g10_stop_short", "g10_stop_ignored", "g10_timeout_stop",
      "g10_empty_ok", "g10_html_ok", "g10_nonzip_ok", "g10_size_lo", "g10_size_hi"], t_g10),
    ("G11", "stages (pre converts, prints and writes no S&P value; dry needs --out, writes nothing under data/, SYNTHETIC only in `# source:`; registering needs its flag; one vintage per build)",
     ["g11_pre_converts", "g11_pre_prints_value", "g11_pre_writes_value", "g11_dry_default_out", "g11_dry_data_ok", "g11_synthetic_leak", "g11_full_no_flag", "g11_mixed_ok", "g11_scout_lax"], t_g11),
    ("G12", "outputs and leak (headers, extra and renamed columns, `# source:` not a header, fifth CSV, keys, path.csv, workbook, json, local path, at sign, credit line, M29's literal copies)",
     ["g12_header_lax", "g12_extra_col", "g12_source_as_header", "g12_fifth_ok", "g12_dup_ok", "g12_path_ok", "g12_xlsx_ok", "g12_json_ok", "g12_users_ok", "g12_at_ok", "g12_credit_ok", "g12_checksh_lax"], t_g12),
    ("X1", "end-to-end: M29 on a clean copy and on copies with each planted fault", [], t_x1),
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
    try:
        base_wb()
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
                print("       %s caught%s" % (gid, " (%d of %d mutants)" % (len(muts), len(muts)) if muts else " (no mutant: an end-to-end run)"))
        print("live guards: %s" % " ".join(g[0] for g in GUARDS))
        print("selftest: %d guards, %d checks, %d mutants applied one at a time, %d caught, %d failure(s), %.1f s" % (len(GUARDS), n_checks, n_mut, n_caught, bad_total, time.time() - t0))
        return 0 if bad_total == 0 else 1
    finally:
        pass


if __name__ == "__main__":
    sys.exit(main())
