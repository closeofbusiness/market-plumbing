#!/usr/bin/env python3
"""US-dollar international debt securities (BIS IDS) by issuer sector and residence, with the CGFS Paper 65 comparison. Python 3 standard library only.

  python3 bin/bis_ids_dollar.py fetch [--sleep 2.05] [--max-requests 6]      # the only network command: 6 requests to stats.bis.org
  python3 bin/bis_ids_dollar.py build [--out DIR] [--cache DIR]               # offline; byte-identical on re-run
  python3 bin/bis_ids_dollar.py selftest [--no-mutants] [--mutant NAME]       # synthetic data only; no network

Specification: _research/2026-10-23-BIS-IDS-Dollar-Spec.md (committed at 203112e, with its supervisor rulings, rounds 1 to 4; where rounds differ the latest
round is applied). Outputs: data/bis_ids_dollar/ (nine CSVs, README.md, SOURCES.md).

WHAT TOUCHES THE NETWORK. Only `fetch`, and only stats.bis.org. Any other host is refused before a request is made. GET only, one request at a time, at
least 2 s apart, at most 8 a run, no redirect followed, the CLAUDE.md non-SEC identification string (no address, no name). Any status other than 200, or a
body that fails a hard content test, writes data/vintages/bis_ids_dollar/STOP and ends the run. Nothing retries and nothing routes around a refusal. This
script never deletes, renames over or truncates a STOP file; only a person deletes one. The IDS release dates and the BIS terms are constants of this file,
copied from the spec; the script does not fetch them.

WHAT IT MEASURES. The face value outstanding and the net issues of international debt securities denominated in US dollars, quarterly, by issuer sector and
issuer residence (BIS-published series on a stated perimeter, or sums and differences of them), and the comparison of two of them with a statement in BIS
CGFS Paper 65. It cannot say who holds the securities, why they were issued, or anything about interest rates or the dollar.
"""
import argparse
import ast
import collections
import contextlib
import csv
import datetime as dt
import hashlib
import http.client
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(ROOT, "data", "bis_ids_dollar")
CACHE_DEFAULT = os.path.join(ROOT, "data", "vintages", "bis_ids_dollar")
STOP_PATH = os.path.join(CACHE_DEFAULT, "STOP")                # fixed, whatever --cache says: a latch cannot be dodged by pointing the cache elsewhere

# R2: the CLAUDE.md canonical string for every non-SEC host. No address, no name.
UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
HEADERS = {"User-Agent": UA, "Accept-Encoding": "identity", "Accept": "*/*"}
BIS_HOST = "stats.bis.org"
HOST_ALLOW = frozenset({BIS_HOST})
MIN_SLEEP = 2.0                  # R3: at least 2 s between request starts
DEFAULT_SLEEP = 2.05             # the 0.05 is a margin for clock granularity
MAX_REQUESTS = 8
TIMEOUT = 120
BODY_CAP = 64 * 1024 * 1024
ERR_CAP = 4096

# ------------------------------------------------------------------------------------------------------------------------
# spec constants (section numbers refer to the spec)
# ------------------------------------------------------------------------------------------------------------------------
IDS_FLOW = "WS_DEBT_SEC2_PUB"
LBS_FLOW = "WS_LBS_D_PUB"
IDS_DIMS = ("FREQ", "ISSUER_RES", "ISSUER_NAT", "ISSUER_BUS_IMM", "ISSUER_BUS_ULT", "MARKET", "ISSUE_TYPE", "ISSUE_CUR_GROUP", "ISSUE_CUR", "ISSUE_OR_MAT",
            "ISSUE_RE_MAT", "ISSUE_RATE", "ISSUE_RISK", "ISSUE_COL", "MEASURE")
LBS_DIMS = ("FREQ", "L_MEASURE", "L_POSITION", "L_INSTR", "L_DENOM", "L_CURR_TYPE", "L_PARENT_CTY", "L_REP_BANK_TYPE", "L_REP_CTY", "L_CP_SECTOR",
            "L_CP_COUNTRY", "L_POS_TYPE")
IDS_HEADER = ("FREQ,ISSUER_RES,ISSUER_NAT,ISSUER_BUS_IMM,ISSUER_BUS_ULT,MARKET,ISSUE_TYPE,ISSUE_CUR_GROUP,ISSUE_CUR,ISSUE_OR_MAT,ISSUE_RE_MAT,ISSUE_RATE,"
              "ISSUE_RISK,ISSUE_COL,MEASURE,DECIMALS,UNIT_MEASURE,UNIT_MULT,COLLECTION,TIME_FORMAT,TIME_PERIOD,OBS_VALUE,OBS_STATUS,OBS_PRE_BREAK,OBS_CONF")
LBS_HEADER = ("FREQ,L_MEASURE,L_POSITION,L_INSTR,L_DENOM,L_CURR_TYPE,L_PARENT_CTY,L_REP_BANK_TYPE,L_REP_CTY,L_CP_SECTOR,L_CP_COUNTRY,L_POS_TYPE,DECIMALS,"
              "UNIT_MEASURE,UNIT_MULT,AVAILABILITY,TITLE_GRP,TIME_FORMAT,COLLECTION,ORG_VISIBILITY,TIME_PERIOD,OBS_VALUE,OBS_STATUS,OBS_CONF,OBS_PRE_BREAK")

FIRST_Q = "2013-Q4"                          # first quarter in the data (C12)
OUT_FIRST_Q = "2014-Q3"                      # first quarter written to quarterly.csv (so P4 and 2014-Q4 changes exist)
SHARES_FIRST_Q = "2019-Q1"
CGFS_FIRST, CGFS_LAST = "2014-Q4", "2019-Q4"            # R8, frozen: the five years to the paper's data date
BAND_LO, BAND_HI = 65, 85                    # R8, frozen
C06_FIRST_Q = "2014-Q1"
C06_MIN_NET = 5000
C06_MIN_AGREE = Decimal("0.9")
GAP_TOL = 5                                  # C05, C05b: US$ millions
LBS_PIN_END = dt.date(2026, 10, 30)          # the LBS 2026-Q2 release: LBS-dependent pins are one-vintage checks until then
IDS_PIN_LAST_Q = "2026-Q2"                   # IDS pins FAIL while 2026-Q2 is the latest quarter and WARN once 2026-Q3 is in the file
REGISTERED = ("2026-10-23", "2019-Q4", "2026-Q1", ("ALL", "US"), "ALL", 1.0, 52)       # R8, frozen (section 7)
REG_BASELINE_RELEASE = "2026-09-14"
REG_SCORE_Q = "2026-Q3"
PAPER_TOTAL_USD_M = 22_600_000               # CGFS 65 p 4: "$22.6 trillion as of Q4 2019"
C11_TOL = Decimal("0.03")

# IDS release dates: the "International debt securities" line (category IDS) of the BIS release calendar, never the "Debt securities statistics" (DSS) rows
# (R3-4, spec 2.4). Data quarter -> release date ("no later than"); observed 23 Oct 2026 in https://data.bis.org/api/v0/releasecalendar. Not fetched.
IDS_RELEASES = (("2023-Q1", "2023-06-12"), ("2023-Q2", "2023-09-18"), ("2023-Q3", "2023-12-04"), ("2023-Q4", "2024-03-04"), ("2024-Q1", "2024-06-10"),
                ("2024-Q2", "2024-09-16"), ("2024-Q3", "2024-12-10"), ("2024-Q4", "2025-03-11"), ("2025-Q1", "2025-06-16"), ("2025-Q2", "2025-09-15"),
                ("2025-Q3", "2025-12-08"), ("2025-Q4", "2026-03-16"), ("2026-Q1", "2026-06-15"), ("2026-Q2", "2026-09-14"), ("2026-Q3", "2026-12-07"))

# groups, sectors, measures
GROUPS = ("ALL", "US", "NON_US", "ADV", "EMDE", "INTL_ORG")
GROUP_CODE = {"ALL": "3P", "US": "US", "ADV": "5R", "EMDE": "4T", "INTL_ORG": "1C"}
SECTORS = ("ALL", "GOV", "FIN", "FIN_PRIV_BANK", "FIN_PUB_BANK", "FIN_PRIV_OFI", "FIN_PUB_OFI", "FIN_CENTRAL_BANK", "NFC", "INTL_INST")
SECTOR_CODE = {"ALL": "1", "GOV": "2", "FIN": "B", "FIN_PRIV_BANK": "E", "FIN_PUB_BANK": "I", "FIN_PRIV_OFI": "G", "FIN_PUB_OFI": "K", "FIN_CENTRAL_BANK": "7",
               "NFC": "J", "INTL_INST": "S"}
FIN_PARTS = ("FIN_PRIV_BANK", "FIN_PUB_BANK", "FIN_PRIV_OFI", "FIN_PUB_OFI", "FIN_CENTRAL_BANK")
TOP_PARTS = ("GOV", "FIN", "NFC", "INTL_INST")
SHARE_SECTORS = ("GOV", "FIN", "NFC", "INTL_INST") + FIN_PARTS
NO_US_SERIES = ("FIN_CENTRAL_BANK", "INTL_INST")      # sectors for which the BIS publishes no US series at all
MEAS = ("outstanding", "net_issues")
MEAS_CODE = {"outstanding": "I", "net_issues": "G"}
AGGREGATES = frozenset({"3P", "5R", "4T", "3C", "4Y", "4W", "4U"})       # C04: residence aggregates; every other F5 code is a leaf (1C and 1Z are leaves)

# ------------------------------------------------------------------------------------------------------------------------
# the label allowlist (2.2): semantic labels raise STOP, descriptive labels raise a WARN
# ------------------------------------------------------------------------------------------------------------------------
IDS_SEMANTIC = (
    ("ISSUER_BUS_IMM", "1", "All issuers"), ("ISSUER_BUS_IMM", "2", "General government"), ("ISSUER_BUS_IMM", "B", "Financial corporations"),
    ("ISSUER_BUS_IMM", "E", "Private banks"), ("ISSUER_BUS_IMM", "I", "Public banks"), ("ISSUER_BUS_IMM", "G", "Private other financial institutions"),
    ("ISSUER_BUS_IMM", "K", "Public other financial institutions"), ("ISSUER_BUS_IMM", "7", "Central bank"),
    ("ISSUER_BUS_IMM", "J", "Non-financial corporations"), ("ISSUER_BUS_IMM", "S", "International institutions"), ("ISSUER_BUS_ULT", "1", "All issuers"),
    ("ISSUER_RES", "3P", "All countries excluding residents"), ("ISSUER_RES", "US", "United States"), ("ISSUER_RES", "5R", "Advanced economies"),
    ("ISSUER_RES", "4T", "Emerging market and developing economies"), ("ISSUER_RES", "1C", "International organisations"),
    ("ISSUER_NAT", "3P", "All countries excluding residents"), ("ISSUER_NAT", "US", "United States"),
    ("MARKET", "C", "International markets"), ("MEASURE", "I", "Amounts outstanding"), ("MEASURE", "G", "Net issues"),
    ("ISSUE_CUR", "USD", "US Dollar"), ("ISSUE_CUR_GROUP", "A", "All currencies"))
IDS_DESCRIPTIVE = (
    ("ISSUE_TYPE", "A", "All issue types"), ("ISSUE_OR_MAT", "A", "Total (all maturities)"), ("ISSUE_RE_MAT", "A", "Total (all maturities)"),
    ("ISSUE_RATE", "A", "All interest rates"), ("ISSUE_RISK", "A", "All credit ratings"), ("ISSUE_COL", "A", "All issues"))
LBS_SEMANTIC = (
    ("L_MEASURE", "S", "Amounts outstanding / Stocks"), ("L_MEASURE", "F", "FX and break adjusted change (BIS calculated)"),
    ("L_POSITION", "C", "Total claims"), ("L_INSTR", "G", "Loans and deposits"), ("L_DENOM", "USD", "US dollar"),
    ("L_CURR_TYPE", "A", "All currencies (=D+F+U)"), ("L_REP_CTY", "5A", "All reporting countries"), ("L_CP_SECTOR", "A", "All sectors"),
    ("L_CP_SECTOR", "I", "Banks, related offices"), ("L_CP_COUNTRY", "5J", "All countries"), ("L_CP_COUNTRY", "US", "United States"),
    ("L_POS_TYPE", "N", "Cross-border"))
LBS_DESCRIPTIVE = (
    ("L_REP_BANK_TYPE", "A", "All reporting banks/institutions (domestic, foreign, consortium and unclassified)"), ("L_PARENT_CTY", "5J", "All countries"))
IDS_FLOW_NAME = "International debt securities (BIS-compiled)"
IDS_STRUCT_SUFFIX = "BIS:BIS_DEBT_SEC2(1.0)"
LBS_FLOW_NAME = "Locational banking"
LBS_STRUCT_SUFFIX = "BIS:BIS_LBS_DISS(1.0)"

# ------------------------------------------------------------------------------------------------------------------------
# the output allowlists: the spec's canonical text (section 5), typed here, and its sha256 as the spec prints it
# ------------------------------------------------------------------------------------------------------------------------
QUARTERLY_COLS = ["quarter", "basis", "issuer_group", "sector", "outstanding_usd_m", "net_issues_usd_m", "change_in_outstanding_usd_m", "other_change_usd_m",
                  "status", "derived", "vintage", "ids_release"]
SHARES_COLS = ["quarter", "issuer_group", "sector", "share_pct", "numerator_usd_m", "denominator_usd_m", "denominator"]
WINDOWS_COLS = ["window", "first_quarter", "last_quarter", "issuer_group", "sector", "quarters_n", "quarters_blank", "net_issues_usd_m",
                "change_in_outstanding_usd_m", "other_change_usd_m", "share_of_group_net_issues_pct", "denominator"]
CGFS_COLS = ["variant", "plain_name", "definition", "first_quarter", "last_quarter", "ids_change_usd_m", "lbs_change_usd_m", "lbs_measure", "lbs_flow_sum_usd_m",
             "lbs_break_sum_usd_m", "lbs_break_quarters", "ids_share_of_increase_pct", "denominator", "reading", "note"]
SUMMARY_COLS = ["question", "window", "issuer_group", "sector", "statistic", "value", "denominator", "blind"]
REVISION_COLS = ["vintage_prev", "vintage_new", "quarter", "basis", "issuer_group", "sector", "measure", "value_prev_usd_m", "value_new_usd_m", "change_usd_m",
                 "change_pct"]
SCORE_COLS = ["registered_on", "scored_on", "vintage_prev", "vintage_new", "latest_quarter_new", "cells_checked", "largest_abs_change_pct", "largest_cell",
              "threshold_pct", "result", "note"]
CHECK_COLS = ["check_id", "description", "expected", "observed", "status"]
LOG_COLS = ["utc_time", "host", "path_and_query", "status", "bytes", "sha256"]
ALLOW_ORDER = ("quarterly.csv", "shares.csv", "net_issues_windows.csv", "cgfs_check.csv", "summary.csv", "revisions.csv", "registration_score.csv", "checks.csv",
               "fetch_log.csv")
ALLOW = {"quarterly.csv": QUARTERLY_COLS, "shares.csv": SHARES_COLS, "net_issues_windows.csv": WINDOWS_COLS, "cgfs_check.csv": CGFS_COLS,
         "summary.csv": SUMMARY_COLS, "revisions.csv": REVISION_COLS, "registration_score.csv": SCORE_COLS, "checks.csv": CHECK_COLS, "fetch_log.csv": LOG_COLS}
SPEC_ALLOW_TEXT = (
    "quarterly.csv:quarter,basis,issuer_group,sector,outstanding_usd_m,net_issues_usd_m,change_in_outstanding_usd_m,other_change_usd_m,status,derived,vintage,ids_release\n"
    "shares.csv:quarter,issuer_group,sector,share_pct,numerator_usd_m,denominator_usd_m,denominator\n"
    "net_issues_windows.csv:window,first_quarter,last_quarter,issuer_group,sector,quarters_n,quarters_blank,net_issues_usd_m,change_in_outstanding_usd_m,other_change_usd_m,share_of_group_net_issues_pct,denominator\n"
    "cgfs_check.csv:variant,plain_name,definition,first_quarter,last_quarter,ids_change_usd_m,lbs_change_usd_m,lbs_measure,lbs_flow_sum_usd_m,lbs_break_sum_usd_m,lbs_break_quarters,ids_share_of_increase_pct,denominator,reading,note\n"
    "summary.csv:question,window,issuer_group,sector,statistic,value,denominator,blind\n"
    "revisions.csv:vintage_prev,vintage_new,quarter,basis,issuer_group,sector,measure,value_prev_usd_m,value_new_usd_m,change_usd_m,change_pct\n"
    "registration_score.csv:registered_on,scored_on,vintage_prev,vintage_new,latest_quarter_new,cells_checked,largest_abs_change_pct,largest_cell,threshold_pct,result,note\n"
    "checks.csv:check_id,description,expected,observed,status\n"
    "fetch_log.csv:utc_time,host,path_and_query,status,bytes,sha256\n")
SPEC_ALLOW_SHA256 = "c84601784c545b2722847ad58803ba906564f8325fabd580c7fb0d2ce86735af"
ROUND1_HASH_HEAD, ROUND1_HASH_TAIL = "4a156e71", "a03f9"                      # the superseded round-1 hash, kept as the record (spec 5)
COMMITTED = tuple(ALLOW_ORDER) + ("README.md", "SOURCES.md")
SOURCE_LINE_ID = "Bank for International Settlements, international debt securities statistics"
SOURCE_LINE_LBS = " (and locational banking statistics for cgfs_check.csv)"

# wording guard (R6, 6.3): the literal pattern, copied here and not imported (spec 6.3)
CAUSAL_PATTERN = (r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|"
                  r"in\s+response\s+to|because\s+of|fuell?ed)\b")
CAUSAL_RX = re.compile(CAUSAL_PATTERN, re.I)
CAUSAL_EXTRA_RX = re.compile(r"\blean(?:s|ing)?\s+against\b", re.I)       # stricter than the literal: the literal "leaned?" misses "lean against" (decisions)
NONUS_FUNDING_RX = re.compile(r"funding\s+to\s+non[- ]?U\.?S\.?\s+residents", re.I)
VARIANT_RX = re.compile(r"\bP[1-4]\b")

REQUIRED_S1 = ("This folder shows how many US dollars borrowers owe on bonds and short-term paper sold outside their home markets, split by type of borrower "
               "and by where the borrower is based.")
REQUIRED_S2 = ("It measures amounts owed by issuers, not who holds the securities, and it does not show why the securities were issued or any effect on "
               "interest rates or the dollar.")
OVERLAP_SENTENCE = ("The groups overlap, so do not add them up: ALL contains both US and NON_US, ADV, EMDE and INTL_ORG are a second split of ALL, and the "
                    "US-nationality total cuts across both.")
DISCLOSURE_PREFIX = "Reading rule changed after the reviewers saw P1 and P2 (round 3); the round-1 rule, P1 alone, would read "
N1_LABEL = "not the paper's measure"
BIS_LEGAL_URL = "https://data.bis.org/help/legal"
BIS_QUOTE = "The use of the statistics is unrestricted, provided that"
IDS_TOPIC_URL = "https://data.bis.org/topics/IDS"
RELCAL_URL = "https://data.bis.org/release-calendar"

# ------------------------------------------------------------------------------------------------------------------------
# mutants: deliberately broken variants, switched on only by the selftest, in this process
# ------------------------------------------------------------------------------------------------------------------------
_ACTIVE = set()
_CLOCK_OVERRIDE = []                          # the selftest sets a fake clock here; only the clock mutant and fetch ever read it


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
    """A technical refusal: STOP was written (or already exists); the run ends."""


class SocketFault(Exception):
    """Timeout, reset or TLS error: the invocation ends without latching."""


class DataError(Exception):
    """A hard check on the data failed."""


# ------------------------------------------------------------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------------------------------------------------------------
def tilde(p):
    home = os.path.expanduser("~")
    return str(p).replace(home, "~") if home and home != "~" else str(p)


def sha256_of(b):
    return hashlib.sha256(b).hexdigest()


def now_date():
    """The clock. Read by `fetch` (to name the pull folder) and by nothing else: every date in an output comes from a pull-folder name (R5)."""
    if _CLOCK_OVERRIDE:
        return _CLOCK_OVERRIDE[-1]
    return dt.datetime.now(dt.timezone.utc).date()


def D_(s):
    return dt.date.fromisoformat(s)


def qnum(q):
    return int(q[:4]) * 4 + int(q[6]) - 1


def qadd(q, k):
    y, r = divmod(qnum(q) + k, 4)
    return "%04d-Q%d" % (y, r + 1)


def qrange(a, b):
    out, q = [], a
    while qnum(q) <= qnum(b):
        out.append(q)
        q = qadd(q, 1)
    return out


QRX = re.compile(r"^\d{4}-Q[1-4]$")
DATE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def dstr(v, nd):
    """Fixed-decimal text of a Decimal or number, '' for None, no negative zero."""
    if v is None:
        return ""
    d = Decimal(v).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP) if nd else Decimal(v).quantize(Decimal(1), rounding=ROUND_HALF_UP)
    s = format(d, "f")
    return s[1:] if s.startswith("-") and Decimal(s) == 0 else s


def istr(v):
    """Integer US$ millions as text; '' for None."""
    return "" if v is None else str(int(v))


def lstr(v):
    """LBS-derived US$ millions to 3 decimals; '' for None."""
    return "" if v is None else dstr(v, 3)


def pct2(num, den):
    """num/den*100 to 2 decimals (half up) as a Decimal; None if den is None/zero or num is None."""
    if num is None or den is None or den == 0:
        return None
    return (Decimal(num) / Decimal(den) * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def bn(v):
    """US$ billions, one decimal, from US$ millions."""
    q = (Decimal(v) / Decimal(1000)).quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN if M("bn_half_even") else ROUND_HALF_UP) if v is not None else None
    return "blank" if v is None else "{:,.1f}".format(q)


def tn(v):
    """US$ trillions, two decimals, from US$ millions."""
    q = (Decimal(v) / (Decimal(1000) if M("tn_div_1000") else Decimal(1_000_000))).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN if M("tn_half_even") else ROUND_HALF_UP) if v is not None else None
    return "blank" if v is None else "{:,.2f}".format(q)


def thou(v):
    return "blank" if v is None else "{:,}".format(int(v))


def assert_ua(ua=UA):
    if not M("ua_check_off"):
        if "@" in ua:
            raise Refused("the identification string contains an address")
        for var in ("SEC_UA", "CLAUDE_CODE_USER_EMAIL"):
            v = os.environ.get(var, "").strip()
            if v and (v in ua or ua in v):
                raise Refused("the identification string contains a configured contact value (not printed)")


assert_ua()


def write_text(path, text):
    """Atomic write via a temporary sibling. Refuses any path whose name starts with STOP: this script never writes over a latch."""
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


def read_csv_rows(path):
    """(header, rows) of a csv with comment lines (# ...) skipped; ([], []) if absent."""
    if not os.path.exists(path):
        return [], []
    with open(path, encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh.read().splitlines(True) if not ln.startswith("#")]
    rd = list(csv.reader(io.StringIO("".join(lines))))
    return (rd[0], rd[1:]) if rd else ([], [])


# ------------------------------------------------------------------------------------------------------------------------
# requests: the six fixed targets (2.3) and the URL check (R1, R3)
# ------------------------------------------------------------------------------------------------------------------------
def ids_key(res, nat, imm, measure, ult="1"):
    """The 15-dimension IDS key, in dimension order (2.1). Mutants break one rule each (G1)."""
    if M("key_swap"):
        res, nat = nat, res
    market = "A" if M("key_market_a") else "C"
    grp = "F" if M("key_curgroup_f") else "A"
    sector = imm
    if M("key_ult_sector"):
        sector, ult = ult, imm
    dims = ["Q", res, nat, sector, ult, market, "A", grp, "USD", "A", "A", "A", "A", "A", measure]
    if M("key_14dims"):
        dims = dims[:-2] + dims[-1:]
    return ".".join(dims)


F_PATHS = {
    "F1": "/api/v2/structure/dataflow/BIS/WS_DEBT_SEC2_PUB/1.0?references=all&detail=full",
    "F2": "/api/v2/structure/dataflow/BIS/WS_LBS_D_PUB/1.0?references=all&detail=full",
    "F3": "/api/v2/data/dataflow/BIS/WS_DEBT_SEC2_PUB/1.0/Q.3P+US+5R+4T+1C.3P.1+2+B+J+S+E+I+G+K+7.1.C.A.A.USD.A.A.A.A.A.I+G?startPeriod=2013-Q4&format=csv",
    "F4": "/api/v2/data/dataflow/BIS/WS_DEBT_SEC2_PUB/1.0/Q.3P.US.1.1.C.A.A.USD.A.A.A.A.A.I+G?startPeriod=2013-Q4&format=csv",
    "F5": "/api/v2/data/dataflow/BIS/WS_DEBT_SEC2_PUB/1.0/Q..3P.1.1.C.A.A.USD.A.A.A.A.A.I?startPeriod=2013-Q4&format=csv",
    "F6": "/api/v2/data/dataflow/BIS/WS_LBS_D_PUB/1.0/Q.S+F.C.G.USD.A.5J.A.5A.A+I.5J+US.N?startPeriod=2013-Q4&format=csv",
}
F_FILES = {"F1": "f1_ids_structure.json", "F2": "f2_lbs_structure.json", "F3": "f3_ids_main.csv", "F4": "f4_ids_nationality.csv",
           "F5": "f5_ids_all_residences.csv", "F6": "f6_lbs.csv"}
F_KIND = {"F1": "struct_ids", "F2": "struct_lbs", "F3": "ids_main", "F4": "ids_nat", "F5": "ids_all", "F6": "lbs"}


def built_targets():
    """The same six targets built from the key rules (G1 compares them to the literal F_PATHS)."""
    base = "/api/v2/data/dataflow/BIS/%s/1.0/" % IDS_FLOW
    tail = "?startPeriod=2013-Q4&format=csv"
    f3 = base + ids_key("3P+US+5R+4T+1C", "3P", "1+2+B+J+S+E+I+G+K+7", "I+G") + tail
    f4 = base + ids_key("3P", "US", "1", "I+G") + tail
    f5 = base + ids_key("", "3P", "1", "I") + tail
    return {"F3": f3, "F4": f4, "F5": f5}


def plan():
    return [dict(id=k, target=F_PATHS[k], file=F_FILES[k], kind=F_KIND[k]) for k in ("F1", "F2", "F3", "F4", "F5", "F6")]


def check_method(method):
    if method != "GET" and not M("post_ok"):
        raise Refused("only GET is used")


def check_url(url):
    """Only plain https GETs to stats.bis.org and only the six targets of the spec. Returns (host, target)."""
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    target = p.path + ("?" + p.query if p.query else "")
    if M("allow_other_host"):
        return host, target
    if p.scheme != "https" or p.username or p.password or p.port not in (None, 443) or p.fragment:
        raise Refused("only plain https URLs are allowed")
    if host not in HOST_ALLOW:
        raise Refused("host %s is not on the allowlist" % host)
    if target not in set(F_PATHS.values()):
        raise Refused("that path is not one of the six requests of the spec")
    return host, target


# ------------------------------------------------------------------------------------------------------------------------
# content tests (R3a). A hard problem is a STOP; a soft problem is a WARN in checks.csv
# ------------------------------------------------------------------------------------------------------------------------
def _json(body):
    try:
        return json.loads(body.decode("utf-8-sig")), None
    except (UnicodeDecodeError, ValueError):
        return None, "not JSON"


def _labels_of(doc):
    """{dimension id: {code: label}} for every dimension of the data structure, via its code list."""
    d = doc.get("data", {})
    lists = {c.get("id"): {x.get("id"): (x.get("names", {}).get("en") or x.get("name")) for x in c.get("codes", [])} for c in d.get("codelists", [])}
    out = {}
    for ds in d.get("dataStructures", []):
        for dim in ds.get("dataStructureComponents", {}).get("dimensionList", {}).get("dimensions", []):
            enum = dim.get("localRepresentation", {}).get("enumeration", "")
            m = re.search(r"Codelist=[^:]+:([A-Za-z0-9_]+)\(", enum)
            out[dim.get("id")] = lists.get(m.group(1), {}) if m else {}
    return out


def struct_problems(doc, which):
    """(hard, soft) problems of a structure message. which = 'ids' or 'lbs'."""
    hard, soft = [], []
    if not isinstance(doc, dict) or not isinstance(doc.get("data"), dict):
        return ["the structure message has no data object"], soft
    d = doc["data"]
    flow_id, flow_name, suffix, dims = ((IDS_FLOW, IDS_FLOW_NAME, IDS_STRUCT_SUFFIX, IDS_DIMS) if which == "ids" else (LBS_FLOW, LBS_FLOW_NAME, LBS_STRUCT_SUFFIX, LBS_DIMS))
    flows = [f for f in d.get("dataflows", []) if isinstance(f, dict) and f.get("id") == flow_id]
    if not flows:
        hard.append("dataflow %s is not in the message" % flow_id)
    else:
        f = flows[0]
        nm = f.get("names", {}).get("en") or f.get("name")
        if nm != flow_name:
            (hard if which == "ids" else soft).append("dataflow name is %r, not %r" % (nm, flow_name))
        if not str(f.get("structure", "")).endswith(suffix):
            hard.append("dataflow structure is %r, not ...%s" % (f.get("structure"), suffix))
    structs = [s for s in d.get("dataStructures", []) if isinstance(s, dict) and suffix.split(":")[1].split("(")[0] == s.get("id")]
    if not structs:
        hard.append("data structure %s is not in the message" % suffix)
    else:
        got = [x.get("id") for x in sorted(structs[0].get("dataStructureComponents", {}).get("dimensionList", {}).get("dimensions", []),
                                           key=lambda x: x.get("position", 0))]
        if got != list(dims):
            hard.append("dimension order is %s, not %s" % (",".join(map(str, got)), ",".join(dims)))
    labels = _labels_of(doc)
    sem, desc = ((IDS_SEMANTIC, IDS_DESCRIPTIVE) if which == "ids" else (LBS_SEMANTIC, LBS_DESCRIPTIVE))
    for dim, code, want in sem:
        if M("label_market_off") and dim == "MARKET":
            continue
        if M("label_b_off") and dim == "ISSUER_BUS_IMM" and code == "B":
            continue
        got = labels.get(dim, {}).get(code)
        if got != want:
            hard.append("label of %s %s is %r, not %r" % (dim, code, got, want))
    for dim, code, want in desc:
        got = labels.get(dim, {}).get(code)
        if got != want:
            (hard if M("desc_hard") else soft).append("descriptive label of %s %s is %r, not %r" % (dim, code, got, want))
    return hard, soft


def _quarter_ok(q):
    return bool(QRX.match(q or ""))


def _int_or_none(s):
    s = (s or "").strip()
    if s == "":
        return None
    if not re.fullmatch(r"-?\d+(\.0+)?", s):
        raise ValueError(s)
    return int(Decimal(s))


def _dec_or_none(s):
    s = (s or "").strip()
    if s == "":
        return None
    if not re.fullmatch(r"-?\d+(\.\d+)?", s):
        raise ValueError(s)
    return Decimal(s)


IDS_REQ = {
    "ids_main": dict(ISSUER_RES={"3P", "US", "5R", "4T", "1C"}, ISSUER_NAT={"3P"}, ISSUER_BUS_IMM={"1", "2", "B", "J", "S", "E", "I", "G", "K", "7"},
                     MEASURE={"I", "G"}),
    "ids_nat": dict(ISSUER_RES={"3P"}, ISSUER_NAT={"US"}, ISSUER_BUS_IMM={"1"}, MEASURE={"I", "G"}),
    "ids_all": dict(ISSUER_RES=None, ISSUER_NAT={"3P"}, ISSUER_BUS_IMM={"1"}, MEASURE={"I"}),
}
IDS_FIXED = dict(FREQ="Q", ISSUER_BUS_ULT="1", MARKET="C", ISSUE_TYPE="A", ISSUE_CUR_GROUP="A", ISSUE_CUR="USD", ISSUE_OR_MAT="A", ISSUE_RE_MAT="A",
                 ISSUE_RATE="A", ISSUE_RISK="A", ISSUE_COL="A")
LBS_REQ = dict(FREQ={"Q"}, L_MEASURE={"S", "F"}, L_POSITION={"C"}, L_INSTR={"G"}, L_DENOM={"USD"}, L_CURR_TYPE={"A"}, L_PARENT_CTY={"5J"},
               L_REP_BANK_TYPE={"A"}, L_REP_CTY={"5A"}, L_CP_SECTOR={"A", "I"}, L_CP_COUNTRY={"5J", "US"}, L_POS_TYPE={"N"})


def parse_ids_csv(text, kind):
    """(problem, rows): R3a for an IDS CSV. rows = [(res, nat, imm, measure, quarter, int or None)]. problem = None when every hard test passes."""
    head = text.split("\n", 1)[0].rstrip("\r")
    if head != IDS_HEADER:
        return "the CSV header is not the literal of 2.3", None
    req = IDS_REQ[kind]
    seen, out = set(), []
    try:
        for r in csv.DictReader(io.StringIO(text)):
            if len(r) != 25 or None in r or None in r.values():
                return "a row has the wrong number of fields", None
            for k, v in IDS_FIXED.items():
                if r[k] != v:
                    return "a row outside the requested key: %s = %r, not %r" % (k, r[k], v), None
            for k in ("ISSUER_RES", "ISSUER_NAT", "ISSUER_BUS_IMM", "MEASURE"):
                allowed = req[k]
                if (allowed is not None and r[k] not in allowed) or (allowed is None and not re.fullmatch(r"[0-9A-Z]{2}", r[k])):
                    return "a row outside the requested key: %s = %r" % (k, r[k]), None
            if r["UNIT_MEASURE"] != "USD":
                return "UNIT_MEASURE is %r, not USD" % r["UNIT_MEASURE"], None
            if r["UNIT_MULT"] != "6" and not M("unit_mult_any"):
                return "UNIT_MULT is %r, not 6" % r["UNIT_MULT"], None
            if r["OBS_CONF"] != "F":
                return "OBS_CONF is %r, not F" % r["OBS_CONF"], None
            if not _quarter_ok(r["TIME_PERIOD"]):
                return "a malformed TIME_PERIOD %r" % r["TIME_PERIOD"], None
            key = (r["ISSUER_RES"], r["ISSUER_NAT"], r["ISSUER_BUS_IMM"], r["MEASURE"], r["TIME_PERIOD"])
            if key in seen:
                return "a duplicate series-quarter %r" % (key,), None
            seen.add(key)
            try:
                v = _int_or_none(r["OBS_VALUE"])
            except ValueError:
                return "OBS_VALUE %r is not an integer" % r["OBS_VALUE"], None
            out.append(key[:4] + (key[4], v))
    except csv.Error as e:
        return "the CSV does not parse (%s)" % e, None
    if not out:
        return "the CSV holds no row", None
    return None, out


def parse_lbs_csv(text):
    """(problem, rows): R3a for the LBS CSV. rows = [(lmeasure, sector, country, quarter, Decimal or None, flagged, pre_break Decimal or None)]."""
    head = text.split("\n", 1)[0].rstrip("\r")
    if head != LBS_HEADER:
        return "the CSV header is not the literal of 2.3", None
    seen, out = set(), []
    try:
        for r in csv.DictReader(io.StringIO(text)):
            if len(r) != 25 or None in r or None in r.values():
                return "a row has the wrong number of fields", None
            for k, allowed in LBS_REQ.items():
                if r[k] not in allowed:
                    return "a row outside the requested key: %s = %r" % (k, r[k]), None
            if r["UNIT_MEASURE"] != "USD":
                return "UNIT_MEASURE is %r, not USD" % r["UNIT_MEASURE"], None
            if r["UNIT_MULT"] != "6" and not M("unit_mult_any"):
                return "UNIT_MULT is %r, not 6" % r["UNIT_MULT"], None
            if r["OBS_CONF"] != "F":
                return "OBS_CONF is %r, not F" % r["OBS_CONF"], None
            if not _quarter_ok(r["TIME_PERIOD"]):
                return "a malformed TIME_PERIOD %r" % r["TIME_PERIOD"], None
            key = (r["L_MEASURE"], r["L_CP_SECTOR"], r["L_CP_COUNTRY"], r["TIME_PERIOD"])
            if key in seen:
                return "a duplicate series-quarter %r" % (key,), None
            seen.add(key)
            try:
                v = _dec_or_none(r["OBS_VALUE"])
                pb = _dec_or_none(r["OBS_PRE_BREAK"])
            except ValueError:
                return "OBS_VALUE or OBS_PRE_BREAK is not a number (%r, %r)" % (r["OBS_VALUE"], r["OBS_PRE_BREAK"]), None
            out.append(key + (v, r["OBS_STATUS"] == "B", pb))
    except csv.Error as e:
        return "the CSV does not parse (%s)" % e, None
    if not out:
        return "the CSV holds no row", None
    return None, out


def c04_rows(allres):
    """C04 per quarter: (quarter, 3P, leaf sum, leaf count, d, US) for each quarter with a 3P value. allres = {(res, q): int}."""
    qs = sorted({q for (res, q), v in allres.items() if res == "3P" and v is not None})
    out = []
    for q in qs:
        if M("leaf_alpha"):
            leaves = [(res, v) for (res, qq), v in allres.items() if qq == q and v is not None and re.fullmatch(r"[A-Z]{2}", res) and res not in AGGREGATES]
        else:
            leaves = [(res, v) for (res, qq), v in allres.items() if qq == q and v is not None and res not in AGGREGATES]
        s = sum(v for _, v in leaves)
        tot = allres[("3P", q)]
        out.append((q, tot, s, len(leaves), tot - s, allres.get(("US", q))))
    return out


def c04_status(rows):
    """(status, stop, detail): the signed test of 3.C04 as the reviewer wrote it (round 4, O-13).
    leg 1: |3P - sum(leaf)| <= 0.1% of 3P; leg 2: |(3P - sum(leaf)) + US| >= 0.9 x US. PASS if both; FAIL and STOP only if leg 2 fails; WARN otherwise."""
    status, stop, worst = "PASS", False, None
    notes = []
    for q, tot, s, n, d, us in rows:
        leg1 = abs(d) <= Decimal("0.01" if M("c04_leg1_loose") else "0.001") * abs(tot)
        leg2 = None if us is None else abs(d + us) >= Decimal("0.7" if M("c04_leg2_07") else "0.9") * us
        if M("c04_no_stop"):
            leg2 = True if leg2 is not None else None
        if M("c04_unsigned") and not leg1:
            leg2 = False
        if leg2 is False:
            status, stop = "FAIL", True
            notes.append("%s: d=%s, US=%s: the second leg fails (3P looks as if it excluded the US)" % (q, thou(d), thou(us)))
        elif not leg1 or leg2 is None:
            if status == "PASS":
                status = "WARN"
            notes.append("%s: d=%s (%.3f%% of 3P)%s" % (q, thou(d), 100 * abs(float(d)) / float(tot) if tot else 0.0, "" if leg2 is not None else "; US absent"))
        if worst is None or abs(d) > abs(worst[4]):
            worst = (q, tot, s, n, d, us)
    return status, stop, worst, notes


def body_problem(kind, body):
    """(hard problem or None) for a response body of the given kind; used by fetch and by the loaders."""
    if kind in ("struct_ids", "struct_lbs"):
        doc, bad = _json(body)
        if bad:
            return bad
        hard, _ = struct_problems(doc, "ids" if kind == "struct_ids" else "lbs")
        return "; ".join(hard[:3]) if hard else None
    try:
        text = body.decode("utf-8-sig")
    except UnicodeDecodeError:
        return "not UTF-8 text"
    if kind == "lbs":
        p, _ = parse_lbs_csv(text)
        return p
    p, rows = parse_ids_csv(text, kind)
    if p:
        return p
    if kind == "ids_all":
        allres = {(res, q): v for res, nat, imm, meas, q, v in rows}
        st, stop, worst, notes = c04_status(c04_rows(allres))
        if stop:
            return "C04 signature of a 3P that excludes the US: " + notes[0]
    return None


# ------------------------------------------------------------------------------------------------------------------------
# fetching: the only network code
# ------------------------------------------------------------------------------------------------------------------------
def real_opener(host, target, headers, timeout, cap):
    """GET https://host/target. Returns (status, body, response headers). No redirect is followed (a 3xx comes back as a status and latches), no
    cookies, the only verb is GET. A non-200 body is read up to ERR_CAP bytes (its head goes into the STOP file). Socket faults raise SocketFault."""
    conn = http.client.HTTPSConnection(host, timeout=timeout)
    try:
        conn.request("GET", target, headers=dict(headers))
        resp = conn.getresponse()
        status = resp.status
        hdrs = {k.lower(): v for k, v in resp.getheaders()}
        if status != 200:
            return status, resp.read(ERR_CAP), hdrs
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


def esc_head(body, n=300):
    return (body or b"")[:n].decode("latin-1").encode("unicode_escape").decode("ascii")


def stop_fields(status, utc_time, url_path, retry_after, body_head):
    lines = ["status: %s" % status, "utc_time: %s" % utc_time, "url_path: %s" % url_path]
    if not M("stop_short"):
        lines.append("retry_after: %s" % retry_after)
    lines.append("body_head: %s" % body_head)
    return "\n".join(lines) + "\n"


def check_cache(cache, root=ROOT, out_dir=None):
    """The cache may be outside the repository, or inside it only where git ignores it (never in the committed output folder)."""
    real = os.path.realpath(os.path.expanduser(cache))
    rroot = os.path.realpath(root)
    if M("cache_check_off"):
        return real
    if real == rroot or real.startswith(rroot + os.sep):
        outd = os.path.realpath(out_dir or os.path.join(root, "data", "bis_ids_dollar"))
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


class Fetcher:
    """All requests go through here. Opener, clock, sleeper and the STOP path are injectable so every rule is testable without a network."""

    def __init__(self, cache, out_dir, pull_date, stop_path=STOP_PATH, sleep=DEFAULT_SLEEP, max_requests=MAX_REQUESTS, opener=real_opener, wall=time.time,
                 mono=time.monotonic, sleeper=time.sleep, now_utc=None, root=ROOT):
        if float(sleep) < MIN_SLEEP and not M("pacing_off"):
            raise Refused("--sleep must be at least %g seconds" % MIN_SLEEP)
        cap = MAX_REQUESTS * 10 if M("cap_off") else MAX_REQUESTS
        if max_requests > cap or max_requests < 1:
            raise Refused("--max-requests must be between 1 and %d" % MAX_REQUESTS)
        assert DATE_RX.match(pull_date)
        self.sleep, self.max_requests = float(sleep), max_requests
        self.out_dir = out_dir
        self.cache = check_cache(cache, root=root, out_dir=out_dir)
        self.pull_date = pull_date
        self.pull_dir = os.path.join(self.cache, pull_date)
        self.opener, self.wall, self.mono, self.sleeper = opener, wall, mono, sleeper
        self.stop_path = stop_path
        self.now_utc = now_utc or (lambda: dt.datetime.now(dt.timezone.utc))
        self.requests = 0
        self._last_mono = None
        self._last_file = os.path.join(self.cache, ".last_request")
        self.log_path = os.path.join(self.pull_dir, "fetch_log.csv")

    def check_stop(self):
        if os.path.exists(self.stop_path) and not M("stop_ignored"):
            raise Latched("STOP present: %s" % tilde(self.stop_path))

    def _pace(self):
        wait = 0.0
        try:
            with open(self._last_file, encoding="utf-8") as fh:
                last = float(fh.read().strip())
            wait = max(wait, self.sleep - (self.wall() - last))
        except (OSError, ValueError):
            pass
        if self._last_mono is not None:
            wait = max(wait, self.sleep - (self.mono() - self._last_mono))
        if wait > 0 and not M("pacing_off"):
            self.sleeper(min(wait, self.sleep))

    @staticmethod
    def _stamp(ts):
        return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % int((ts % 1) * 1000)

    def _log(self, ts, target, status, nbytes, sha):
        _, rows = read_csv_rows(self.log_path)
        rows.append([self._stamp(ts), BIS_HOST, target, str(status), str(nbytes), sha])
        write_text(self.log_path, render_csv("fetch_log.csv", rows, "# source: request log of bin/bis_ids_dollar.py fetch (stats.bis.org), pull folder " + self.pull_date))

    def _latch(self, status, target, retry_after, body, why):
        """Write the STOP file (exclusive create: an existing one is never overwritten) and end the run."""
        os.makedirs(os.path.dirname(self.stop_path), exist_ok=True)
        text = stop_fields(status, self.now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"), target, retry_after or "", esc_head(body))
        try:
            with open(self.stop_path, "x", encoding="utf-8") as fh:
                fh.write(text)
        except FileExistsError:
            pass
        raise Latched("STOP written: %s (%s)" % (tilde(self.stop_path), why))

    def _get(self, target, method="GET"):
        check_method(method)
        check_url("https://" + BIS_HOST + target)
        if self.requests >= self.max_requests:
            raise MaxRequests("request cap reached (%d)" % self.max_requests)
        self._pace()
        started = self.wall()
        self._last_mono = self.mono()
        os.makedirs(self.cache, exist_ok=True)
        write_text(self._last_file, "%r\n" % started)
        self.requests += 1
        try:
            status, body, rh = self.opener(BIS_HOST, target, dict(HEADERS), TIMEOUT, BODY_CAP)
        except SocketFault:
            self._log(started, target, "socket_fault", "", "")
            raise
        return status, body, rh, started

    def fetch_one(self, req):
        """Returns 'cached' or 'saved'; raises Latched / SocketFault / MaxRequests / Refused."""
        path = os.path.join(self.pull_dir, req["file"])
        if os.path.exists(path):
            return "cached"
        self.check_stop()
        status, body, rh, started = self._get(req["target"])
        if status == 429 and M("retry_429"):
            status, body, rh, started = self._get(req["target"])
        if status != 200:
            self._log(started, req["target"], status, "", "")
            if status // 100 == 3 and M("redirect_ok"):
                return "refused_unlatched"
            self._latch(status, req["target"], rh.get("retry-after", ""), body, "HTTP %s" % status)
        if body is None:
            self._log(started, req["target"], status, "", "")
            self._latch(status, req["target"], "", b"", "body larger than the cap")
        self._log(started, req["target"], status, len(body), sha256_of(body))
        problem = body_problem(req["kind"], body)
        if problem:
            self._latch(status, req["target"], "", body, "content test: %s" % problem)
        write_bytes(path, body)
        return "saved"

    def run(self, reqs, say=print):
        saved = 0
        for req in reqs:
            out = self.fetch_one(req)
            saved += out == "saved"
            say("%-28s %s" % (req["file"], out))
        return saved


# ------------------------------------------------------------------------------------------------------------------------
# a pull: the six cached files of one pull folder, tested again and parsed (R3a is applied on every build as well as on fetch)
# ------------------------------------------------------------------------------------------------------------------------
MEAS_OF = {"I": "outstanding", "G": "net_issues"}


def load_pull(date, files):
    """files = {'F1': bytes, ..., 'F6': bytes}. Returns the parsed pull; raises DataError on any hard problem. `date` is the pull-folder name."""
    for k in ("F1", "F2", "F3", "F4", "F5", "F6"):
        if k not in files:
            raise DataError("pull %s lacks %s" % (date, F_FILES[k]))
        problem = body_problem(F_KIND[k], files[k])
        if problem:
            raise DataError("pull %s, %s: %s" % (date, F_FILES[k], problem))
    soft = []
    for k, which in (("F1", "ids"), ("F2", "lbs")):
        doc, _ = _json(files[k])
        soft += struct_problems(doc, which)[1]
    ids, exists = {}, set()
    _, rows = parse_ids_csv(files["F3"].decode("utf-8-sig"), "ids_main")
    for res, nat, imm, meas, q, v in rows:
        ids[(res, imm, meas, q)] = v
        exists.add((res, imm, meas))
    nat = {}
    _, rows = parse_ids_csv(files["F4"].decode("utf-8-sig"), "ids_nat")
    for res, nt, imm, meas, q, v in rows:
        nat[(meas, q)] = v
    allres = {}
    _, rows = parse_ids_csv(files["F5"].decode("utf-8-sig"), "ids_all")
    for res, nt, imm, meas, q, v in rows:
        allres[(res, q)] = v
    lbs = {}
    _, rows = parse_lbs_csv(files["F6"].decode("utf-8-sig"))
    for m, sec, cty, q, v, flag, pb in rows:
        lbs[(m, sec, cty, q)] = (v, flag, pb)
    latest = max((q for (res, imm, meas, q), v in ids.items() if (res, imm, meas) == ("3P", "1", "I") and v is not None), default=None)
    if latest is None:
        raise DataError("pull %s has no ALL outstanding value" % date)
    return dict(date=date, ids=ids, exists=exists, nat=nat, allres=allres, lbs=lbs, soft=soft, latest=latest)


# the decoy exists for one reason: the G20 mutant that reads release dates from the wrong calendar line. Observed on 23 Oct 2026 in the same JSON feed
# (category DSS, "Debt securities statistics"): the same dates, a different quarter on each. Never used outside that mutant.
IDS_RELEASES_DSS_DECOY = (("2025-Q3", "2026-03-16"), ("2025-Q4", "2026-06-15"), ("2026-Q1", "2026-09-14"), ("2026-Q2", "2026-12-07"), ("2026-Q3", "2027-03-15"))


def release_pair(vintage_date):
    """(release date, data quarter) of the latest IDS release on or before the pull-folder date; ('', '') if none. The date is a label only (2.4)."""
    table = IDS_RELEASES_DSS_DECOY if M("release_from_dss") else IDS_RELEASES
    best = None
    for q, d in table:
        if d <= vintage_date and (best is None or d > best[0]):
            best = (d, q)
    return best if best else ("", "")


def release_of(vintage_date):
    return release_pair(vintage_date)[0]


# ------------------------------------------------------------------------------------------------------------------------
# the model of one pull: source cells, the C05b test, NON_US (3.2, 3.3)
# ------------------------------------------------------------------------------------------------------------------------
class Model:
    def __init__(self, pull):
        self.pull = pull
        self.ids, self.exists = pull["ids"], pull["exists"]
        self.L = pull["latest"]
        self.qs = qrange(FIRST_Q, self.L)
        self._c05b = {}

    def src(self, group, sector, meas, q):
        v = self.ids.get((GROUP_CODE[group], SECTOR_CODE[sector], MEAS_CODE[meas], q))
        if v is None and M("absent_zero"):
            return 0
        return v

    def series_exists(self, group, sector, meas):
        return (GROUP_CODE[group], SECTOR_CODE[sector], MEAS_CODE[meas]) in self.exists

    def us_components_absent(self, q, meas):
        return [s for s in ("ALL", "GOV", "FIN", "NFC") if self.src("US", s, meas, q) is None]

    def c05b_m(self, q, meas):
        """(ok, kind, detail) of the US-only identities of 3.3 for one measure in quarter q. kind: ok, absent (a US value the test needs is missing) or mismatch."""
        key = (q, meas)
        if key in self._c05b:
            return self._c05b[key]
        absent = self.us_components_absent(q, meas)
        if absent:
            res = (False, "absent", "%s: the US %s value is absent" % (meas, ", ".join(absent)))
        else:
            a, g, f, n = (self.src("US", s, meas, q) for s in ("ALL", "GOV", "FIN", "NFC"))
            gap1 = a - (g + f + n)
            parts = [self.src("US", p, meas, q) for p in FIN_PARTS]
            gap2 = f - sum(x for x in parts if x is not None)
            lim = 100 if M("c05b_loose") else GAP_TOL
            ok = abs(gap1) <= lim and abs(gap2) <= lim
            res = (ok, "ok" if ok else "mismatch", "%s: ALL-(GOV+FIN+NFC)=%s, FIN-parts=%s" % (meas, gap1, gap2))
        self._c05b[key] = res
        return res

    def c05b(self, q):
        """(ok, detail) over both measures: the verdict of the one C05b row of quarter q. Each NON_US cell uses the verdict of its own measure (c05b_m)."""
        rs = [self.c05b_m(q, m) for m in MEAS]
        return all(r[0] for r in rs), "; ".join(r[2] for r in rs)

    def c05b_cell(self, q, meas):
        """(ok, kind) deciding the NON_US cell of a sector with no US series: the measure's own verdict (mutant: the joint verdict of both measures)."""
        if M("c05b_joint"):
            rs = [self.c05b_m(q, m) for m in MEAS]
            return all(r[0] for r in rs), ("absent" if any(r[1] == "absent" for r in rs) else "mismatch")
        r = self.c05b_m(q, meas)
        return r[0], r[1]

    def cell(self, group, sector, meas, q):
        """(value or None, status) for a residence group. status in ok, absent, partial, us_series_absent, us_value_absent, us_sum_mismatch."""
        if group != "NON_US":
            v = self.src(group, sector, meas, q)
            return v, ("ok" if v is not None else "absent")
        a = self.src("ALL", sector, meas, q)
        if M("non_us_all"):
            return a, ("ok" if a is not None else "absent")
        if a is None:
            return None, "absent"
        if M("non_us_adv_minus_us"):
            a = self.src("ADV", sector, meas, q)
            if a is None:
                return None, "absent"
        u = self.src("US", sector, meas, q)
        if self.series_exists("US", sector, meas):
            if u is None:
                if M("non_us_partial_filled"):
                    return a, "ok"
                if M("us_absent_misapplied") and self.c05b_cell(q, meas)[0]:
                    return a, "us_series_absent"
                return None, "partial"
            return a - u, "ok"
        ok, kind = self.c05b_cell(q, meas)
        if ok or M("non_us_cb_filled_on_mismatch"):
            return a, "us_series_absent"
        if kind == "absent" and not M("value_absent_as_mismatch"):
            return None, "us_value_absent"
        return None, "us_sum_mismatch"


def row_status(s_out, s_net):
    """The row status from the two measures' cell statuses."""
    ss = {s_out, s_net}
    if ss == {"absent"}:
        return "absent"
    if "us_sum_mismatch" in ss:
        return "us_sum_mismatch"
    if "us_value_absent" in ss:
        return "us_value_absent"
    if "partial" in ss or "absent" in ss:
        return "partial"
    if "us_series_absent" in ss:
        return "us_series_absent"
    return "ok"


def quarter_cells(model, nat):
    """Q[(group, sector, q)] = dict(out, net, chg, oth, status, derived, basis) for every quarter from FIRST_Q to L."""
    Q = {}
    for g in GROUPS:
        for s in SECTORS:
            for q in model.qs:
                vo, so = model.cell(g, s, "outstanding", q)
                vn, sn = model.cell(g, s, "net_issues", q)
                if M("net_negated") and vn is not None:
                    vn = -vn
                Q[(g, s, q)] = dict(out=vo, net=vn, s_out=so, s_net=sn, derived="identity" if g == "NON_US" else "source", basis="residence")
            for q in model.qs:
                c = Q[(g, s, q)]
                prev = Q.get((g, s, qadd(q, -1)))
                if prev is not None and c["out"] is not None and prev["out"] is not None:
                    chg = (prev["out"] - c["out"]) if M("change_reversed") else (c["out"] - prev["out"])
                else:
                    chg = None
                c["chg"] = chg
                c["oth"] = chg - c["net"] if chg is not None and c["net"] is not None else None
                c["status"] = row_status(c["s_out"], c["s_net"])
    for q in model.qs:
        vo, vn = nat.get(("I", q)), nat.get(("G", q))
        Q[("US_NATIONALITY", "ALL", q)] = dict(out=vo, net=vn, derived="source", basis="nationality", s_out="ok" if vo is not None else "absent",
                                              s_net="ok" if vn is not None else "absent")
    for q in model.qs:
        c = Q[("US_NATIONALITY", "ALL", q)]
        prev = Q.get(("US_NATIONALITY", "ALL", qadd(q, -1)))
        c["chg"] = (c["out"] - prev["out"]) if prev is not None and c["out"] is not None and prev["out"] is not None else None
        c["oth"] = c["chg"] - c["net"] if c["chg"] is not None and c["net"] is not None else None
        c["status"] = row_status(c["s_out"], c["s_net"])
    return Q


ALL_GROUPS = GROUPS + ("US_NATIONALITY",)


def groups_sectors():
    """The (group, sector) pairs of quarterly.csv in output order."""
    return [(g, s) for g in GROUPS for s in SECTORS] + [("US_NATIONALITY", "ALL")]


def quarterly_rows(Q, qs, vintage, release):
    rows = []

    def f(v):
        if v is None:
            return ""
        return str(int(v) // 1000) if M("values_div_1000") else str(int(v))
    for q in qs:
        if qnum(q) < qnum(OUT_FIRST_Q):
            continue
        for g, s in groups_sectors():
            c = Q[(g, s, q)]
            rows.append([q, c["basis"], g, s, f(c["out"]), f(c["net"]), f(c["chg"]), f(c["oth"]), c["status"], c["derived"], vintage, release])
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# shares (3.6) and net-issue windows (3.7)
# ------------------------------------------------------------------------------------------------------------------------
def denominator_label(group):
    return "%s ALL-sector outstanding, same quarter" % group


def share_rows(Q, qs):
    rows = []
    for q in qs:
        if qnum(q) < qnum(SHARES_FIRST_Q):
            continue
        for g in GROUPS:
            for s in SHARE_SECTORS:
                nq = qadd(q, -1) if M("share_quarter_mismatch") else q
                num = Q[(g, s, nq)]["out"]
                dg, ds = g, "ALL"
                if M("share_nonus_all") and g == "NON_US":
                    dg = "ALL"
                if M("share_fin_part_over_fin") and s in FIN_PARTS:
                    ds = "FIN"
                den = Q[(dg, ds, q)]["out"]
                sh = pct2(num, den)
                rows.append([q, g, s, "" if sh is None else dstr(sh, 2), istr(num), istr(den), denominator_label(g)])
    return rows


def windows_for(L):
    return [("2024", "2024-Q1", "2024-Q4"), ("2025", "2025-Q1", "2025-Q4"), ("2026_to_%s" % L, "2026-Q1", L), ("2024_to_%s" % L, "2024-Q1", L)]


def window_quarters(name, first, last):
    """The quarters of a window. Mutants widen or shorten one (G8)."""
    if M("win_2023q4") and name == "2024":
        first = "2023-Q4"
    if M("win_L_dropped") and name.startswith("2026_to_"):
        last = qadd(last, -1)
    return qrange(first, last)


def window_sums(Q, g, s, qs):
    """(net sum, change sum, other sum, quarters_blank) over qs; a sum is None if any of its quarters is blank."""
    cs = [Q[(g, s, q)] for q in qs]
    blank = sum(1 for c in cs if c["net"] is None or c["chg"] is None or c["oth"] is None)

    def total(key):
        vals = [c[key] for c in cs]
        return None if any(v is None for v in vals) else sum(vals)
    return total("net"), total("chg"), total("oth"), blank


def window_rows(Q, L):
    rows = []
    for name, first, last in windows_for(L):
        qs = window_quarters(name, first, last)
        for g in ALL_GROUPS:
            secs = ("ALL",) if g == "US_NATIONALITY" else SECTORS
            den = window_sums(Q, g, "ALL", qs)[0]
            positive = den is not None and (den > 0 or (M("share_nonpositive") and den != 0))
            for s in secs:
                n, c, o, blank = window_sums(Q, g, s, qs)
                sh = pct2(n, den) if (n is not None and positive) else None
                rows.append([name, qs[0], qs[-1], g, s, str(len(qs)), str(blank), istr(n), istr(c), istr(o), "" if sh is None else dstr(sh, 2),
                             "%s ALL-sector sum of net issues over the window: %s" % (g, "blank" if den is None else thou(den))])
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# the CGFS comparison (3.8, 3.9)
# ------------------------------------------------------------------------------------------------------------------------
def band():
    return (60, 90) if M("band_60_90") else (BAND_LO, BAND_HI)


def inside(share):
    lo, hi = band()
    return share is not None and lo <= share <= hi


def reading_of(s1, s2):
    """The R3-1 rule. consistent if both inside the band, mixed if one inside and one outside, not_consistent if both outside, undefined if either is blank."""
    if s1 is None or s2 is None:
        return "undefined"
    if M("reading_round1"):
        return "consistent" if inside(s1) else "not_consistent"
    i1, i2 = inside(s1), inside(s2)
    if i1 and i2:
        return "consistent"
    if i1 != i2:
        return "mixed"
    return "not_consistent"


def round1_reading(s1):
    """What the superseded round-1 rule (P1 alone, same band) would print."""
    return "undefined" if s1 is None else ("consistent" if inside(s1) else "not_consistent")


def lbs_v(pull, m, sec, cty, q):
    return pull["lbs"].get((m, sec, cty, q), (None, False, None))


def lbs_stock_change(pull, sec, cty, a, b):
    va, vb = lbs_v(pull, "S", sec, cty, a)[0], lbs_v(pull, "S", sec, cty, b)[0]
    return None if va is None or vb is None else vb - va


def lbs_flow_sum(pull, sec, cty, qs):
    vals = [lbs_v(pull, "F", sec, cty, q)[0] for q in qs]
    return None if not qs or any(v is None for v in vals) else sum(vals, Decimal(0))


def lbs_break_quarters(pull, series, qs):
    """Quarters in qs where any stock series used is flagged B; series = [(sector, country)]."""
    return sum(1 for q in qs if any(lbs_v(pull, "S", sec, cty, q)[1] for sec, cty in series))


def sub(a, b):
    return None if a is None or b is None else a - b


def cgfs_rows(pull, Q):
    """Rows of cgfs_check.csv, in order P1, P2, P3, P4, N1; each row a dict."""
    f0, f1 = CGFS_FIRST, CGFS_LAST
    f0_p1 = "2015-Q1" if M("p1_window_2015q1") else f0
    ids_chg = lambda g, a, b: sub(Q[(g, "ALL", b)]["out"], Q[(g, "ALL", a)]["out"])
    after = lambda a, b: qrange(qadd(a, 1), b)
    out = []

    def add(variant, plain, definition, first, last, ids_change, lbs_change, measure, flow, stock, series):
        qs = after(first, last)
        brk = sub(flow, stock) if M("break_flows_minus_stocks") else sub(stock, flow)
        den = None if ids_change is None or lbs_change is None else ids_change + lbs_change
        if M("share_ids_over_lbs"):
            den = lbs_change
        sh = pct2(ids_change, den) if den is not None and den > 0 else None
        out.append(dict(variant=variant, plain=plain, definition=definition, first=first, last=last, ids_change=ids_change, lbs_change=lbs_change, measure=measure,
                        flow=flow, brk=brk, bq=lbs_break_quarters(pull, series, qs), share=sh, den=den, note=""))

    # P1: the paper's measure
    a_chg = lbs_stock_change(pull, "A", "5J", f0_p1, f1)
    if M("p1_no_related"):
        a_chg = sub(a_chg, lbs_stock_change(pull, "I", "5J", f0_p1, f1))
    add("P1", "The paper's measure: change in published stocks",
        "IDS ALL outstanding %s minus %s; LBS stock, all sectors, counterparties in all countries, %s minus %s" % (f1, f0_p1, f1, f0_p1),
        f0_p1, f1, ids_chg("ALL", f0_p1, f1), a_chg, "stock_difference", lbs_flow_sum(pull, "A", "5J", after(f0_p1, f1)), a_chg, [("A", "5J")])
    # P2: break-adjusted flows
    nets = [Q[("ALL", "ALL", q)]["net"] for q in after(f0, f1)]
    ids_flow = None if any(v is None for v in nets) else sum(nets)
    flow_a = lbs_flow_sum(pull, "A", "5J", after(f0, f1))
    add("P2", "The same, using BIS break-adjusted flows",
        "Sum of IDS ALL net issues, %s to %s; sum of BIS break-adjusted LBS flows, all sectors, counterparties in all countries, same quarters" % (qadd(f0, 1), f1),
        f0, f1, ids_flow, flow_a, "break_adjusted_flows", flow_a, lbs_stock_change(pull, "A", "5J", f0, f1), [("A", "5J")])
    # P3: without related offices
    st3 = sub(lbs_stock_change(pull, "A", "5J", f0, f1), lbs_stock_change(pull, "I", "5J", f0, f1))
    fl3 = sub(lbs_flow_sum(pull, "A", "5J", after(f0, f1)), lbs_flow_sum(pull, "I", "5J", after(f0, f1)))
    add("P3", "Without loans between offices of the same bank",
        "IDS ALL outstanding %s minus %s; LBS stock, all sectors minus banks' related offices, %s minus %s" % (f1, f0, f1, f0),
        f0, f1, ids_chg("ALL", f0, f1), st3, "stock_difference", fl3, st3, [("A", "5J"), ("I", "5J")])
    # P4: one quarter earlier
    g0, g1 = qadd(f0, -1), qadd(f1, -1)
    st4 = lbs_stock_change(pull, "A", "5J", g0, g1)
    add("P4", "Window one quarter earlier",
        "IDS ALL outstanding %s minus %s; LBS stock, all sectors, counterparties in all countries, %s minus %s" % (g1, g0, g1, g0),
        g0, g1, ids_chg("ALL", g0, g1), st4, "stock_difference", lbs_flow_sum(pull, "A", "5J", after(g0, g1)), st4, [("A", "5J")])
    # N1: borrowers outside the US
    st_n = sub(lbs_stock_change(pull, "A", "5J", f0, f1), lbs_stock_change(pull, "A", "US", f0, f1))
    fl_n = sub(lbs_flow_sum(pull, "A", "5J", after(f0, f1)), lbs_flow_sum(pull, "A", "US", after(f0, f1)))
    plain = "Borrowers outside the US only" + ("" if M("n1_unlabeled") else " (%s)" % N1_LABEL)
    add("N1", plain, "IDS NON_US ALL outstanding %s minus %s; LBS stock, all sectors, counterparties in all countries minus the United States, %s minus %s" % (f1, f0, f1, f0),
        f0, f1, ids_chg("NON_US", f0, f1), st_n, "stock_difference", fl_n, st_n, [("A", "5J"), ("A", "US")])
    s1, s2 = out[0]["share"], out[1]["share"]
    rd = reading_of(s1, s2)
    for r in out:
        r["reading"] = "described"
    out[0]["reading"] = rd
    out[1]["reading"] = "described" if M("reading_differs") else rd
    if M("reading_on_p3"):
        out[2]["reading"] = rd
    if not M("note_missing"):
        out[0]["note"] = DISCLOSURE_PREFIX + round1_reading(s1) + "."
    out[1]["note"] = "Same reading as P1 by the reading rule in the README; the flows are BIS break-adjusted, so the stock change and the flow sum differ by the break sum."
    out[2]["note"] = "Banks' related offices are removed from the loan stock; shown without a reading."
    out[3]["note"] = "Window moved one quarter earlier; shown without a reading."
    out[4]["note"] = ("N1 is %s; shown without a reading." % N1_LABEL) if not M("n1_unlabeled") else "Shown without a reading."
    return out


def cgfs_csv_rows(rows):
    out = []
    for r in rows:
        out.append([r["variant"], r["plain"], r["definition"], r["first"], r["last"], istr(r["ids_change"]), lstr(r["lbs_change"]), r["measure"], lstr(r["flow"]),
                    lstr(r["brk"]), str(r["bq"]), "" if r["share"] is None else dstr(r["share"], 2),
                    "IDS change plus LBS change, US$ millions: " + ("blank" if r["den"] is None else dstr(r["den"], 3)), r["reading"], r["note"]])
    return out


def r22_sentence(rows):
    """The R2-2 sentence (round 4, O-12), numbers generated. Printed whenever P1's share is inside the band."""
    p1 = rows[0]
    others = [r["share"] for r in rows[1:4] if r["share"] is not None]
    brk, chg = p1["brk"], p1["lbs_change"]
    if brk is None or chg is None or len(others) < 3:
        return ("P1 reproduces the paper's figure only on LBS stock changes, which contain BIS series breaks (a figure for the break sum, or for one of the other shares, is blank on this "
                "vintage, so the usual numbers cannot be generated here; the table above shows what is available). 'Consistent' means one construction matches, not that the figure is robust.")
    lo, hi = min(others), max(others)
    tail = "outside the band" if all(not inside(s) for s in others) else "and at least one of these lies inside the band"
    return ("P1 reproduces the paper's figure only on LBS stock changes, which contain BIS series breaks (%sbn of %sbn here). On break-adjusted flows, without "
            "related offices, or with the window moved one quarter, the share is %s–%s%%, %s. 'Consistent' means one construction matches, not that the "
            "figure is robust." % (dstr(brk / 1000, 0), dstr(chg / 1000, 0), dstr(lo, 0), dstr(hi, 0), tail))


# ------------------------------------------------------------------------------------------------------------------------
# revisions (2.4) and the registered statement (section 7)
# ------------------------------------------------------------------------------------------------------------------------
GROUP_ORDER = {g: i for i, g in enumerate(ALL_GROUPS)}
SECTOR_ORDER = {s: i for i, s in enumerate(SECTORS)}


def cell_values(pull):
    """{(quarter, basis, group, sector, measure): value or None} for every output quarter of a pull."""
    model = Model(pull)
    Q = quarter_cells(model, pull["nat"])
    out = {}
    for (g, s, q), c in Q.items():
        if qnum(q) < qnum(OUT_FIRST_Q):
            continue
        out[(q, c["basis"], g, s, "outstanding")] = c["out"]
        out[(q, c["basis"], g, s, "net_issues")] = c["net"]
    return out


def rev_sort_key(k):
    q, basis, g, s, meas = k
    return (qnum(q), basis, GROUP_ORDER[g], SECTOR_ORDER[s], meas)


def revision_candidates(prev, new):
    """Changed cells between two pulls, for quarters the earlier pull holds, as csv rows. `prev` and `new` are parsed pulls."""
    cp, cn = cell_values(prev), cell_values(new)
    rows = []
    for k in sorted(cp, key=rev_sort_key):
        if qnum(k[0]) > qnum(prev["latest"]):
            continue
        vp, vn = cp[k], cn.get(k)
        if vp == vn:
            continue
        chg = None if vp is None or vn is None else vn - vp
        pc = None if chg is None or vp == 0 else pct2(chg, vp)
        rows.append([prev["date"], new["date"], k[0], k[1], k[2], k[3], k[4], istr(vp), istr(vn), istr(chg), "" if pc is None else dstr(pc, 2)])
    return rows


def merge_revisions(existing, new_rows, first_pull_date=None):
    """Append-only (2.4): existing rows keep their text and order; a key (the first seven columns) already present is not written again; with no earlier
    pull one `baseline` row is written."""
    out = [list(r) for r in existing]
    if M("rev_reorder"):
        out.sort(key=lambda r: r[::-1])
    keys = {tuple(r[:7]) for r in out}
    cand = list(new_rows)
    if first_pull_date is not None and not M("no_baseline"):
        cand = [["baseline", first_pull_date, "", "", "", "", "", "", "", "", ""]] + cand
    for r in cand:
        k = tuple(r[:7])
        if k in keys and not M("rev_dup_key"):
            continue
        keys.add(k)
        out.append(r)
    if M("rev_rewrite"):
        out = [list(r) for r in cand]
    return out


def registration_row(pulls):
    """registration_score.csv: one row. pulls = parsed pulls in folder-date order. Scoring keys on quarters present, never on the calendar (R2-4, R3-4)."""
    reg = registered()
    on, q0, q1, groups, sector, thr, ncells = reg
    base = None
    for p in pulls:
        if release_of(p["date"]) == REG_BASELINE_RELEASE:
            base = p
            break
    if M("score_vs_other") and len(pulls) >= 2:
        base = pulls[-2]
    newest = pulls[-1]
    row = [on, "", base["date"] if base else "", newest["date"], newest["latest"], "", "", "", dstr(thr, 1), "", ""]
    if base is None:
        row[9], row[10] = "VOID", "No pull exists whose latest IDS release is %s, so there is no baseline to compare with." % REG_BASELINE_RELEASE
        return row
    scoring = None
    for p in pulls:
        if M("score_by_calendar"):
            if p["date"] >= "2026-12-07":
                scoring = p
                break
        elif qnum(p["latest"]) >= qnum(REG_SCORE_Q) and p["date"] > base["date"]:
            scoring = p
            break
    if scoring is None:
        row[9] = "PENDING"
        row[10] = "%s is not in the file yet (newest pull %s ends at %s); scored only when a pull holds %s or later." % (REG_SCORE_Q, newest["date"], newest["latest"], REG_SCORE_Q)
        return row
    row[2], row[3], row[4], row[1] = base["date"], scoring["date"], scoring["latest"], scoring["date"]
    qs = qrange(q0, q1)
    worst, worst_cell, n, void = Decimal(0), "", 0, False
    for g in groups:
        for q in qs:
            key = (GROUP_CODE[g], SECTOR_CODE[sector], "I", q)
            a, b = base["ids"].get(key), scoring["ids"].get(key)
            if a is None or b is None or a == 0:
                void = True
                continue
            n += 1
            ch = abs(Decimal(b - a) / Decimal(a) * 100)
            if ch > worst:
                worst, worst_cell = ch, "%s %s %s outstanding" % (g, sector, q)
    row[5] = str(n)
    row[6] = dstr(worst.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), 2)
    row[7] = worst_cell
    if void or n != ncells:
        row[9], row[10] = "VOID", "%d of the %d registered cells could be compared; a cell is absent in one of the two pulls." % (n, ncells)
    elif worst > Decimal(str(thr)):
        row[9], row[10] = "FALSIFIED", "At least one cell changed by more than %s%%." % dstr(thr, 1)
    else:
        row[9], row[10] = "HELD", "No cell changed by more than %s%%." % dstr(thr, 1)
    return row


def registered():
    """The frozen registration (R8). The mutants edit it to prove the frozen-rules guard (G17)."""
    on, q0, q1, groups, sector, thr, ncells = REGISTERED
    if M("reg_threshold"):
        thr = 1.5
    if M("reg_cells"):
        ncells = 51
    if M("reg_sector"):
        sector = "FIN"
    return (on, q0, q1, groups, sector, thr, ncells)


# ------------------------------------------------------------------------------------------------------------------------
# the checks (section 8)
# ------------------------------------------------------------------------------------------------------------------------
PIN_C01 = dict(out={"2014-Q3": 8683591, "2014-Q4": 8778278, "2019-Q3": 11438948, "2019-Q4": 11586704, "2026-Q1": 15871836, "2026-Q2": 16274316},
               net={"2019-Q4": 147756, "2026-Q1": 346000, "2026-Q2": 402479})
PIN_C02 = dict(out={"2014-Q3": 1485957, "2014-Q4": 1498712, "2019-Q3": 1467852, "2019-Q4": 1453406, "2025-Q4": 1835190, "2026-Q1": 1878256, "2026-Q2": 1952509},
               net={"2019-Q4": -14447, "2026-Q1": 43066})
PIN_C03_ALL = {"GOV": 1187905, "FIN": 8116957, "NFC": 1700325, "INTL_INST": 581517, "FIN_PRIV_BANK": 2673055, "FIN_PUB_BANK": 311352, "FIN_PRIV_OFI": 4544624,
               "FIN_PUB_OFI": 578867, "FIN_CENTRAL_BANK": 9059}
PIN_C03_US = {"GOV": 3535, "FIN": 1141953, "NFC": 307918, "FIN_PRIV_BANK": 242561, "FIN_PUB_BANK": 50, "FIN_PRIV_OFI": 852657, "FIN_PUB_OFI": 46685}
PIN_C04 = dict(d=57, leaves=131)
PIN_C08 = dict(out={"2019-Q4": 2754559, "2013-Q4": 1955757}, net={"2013-Q4": 20953})
D = Decimal
PIN_C10_S = {("A", "5J"): {"2014-Q3": D("10443386.682"), "2014-Q4": D("9975340.668"), "2019-Q3": D("10726269.4"), "2019-Q4": D("10883514.581")},
             ("I", "5J"): {"2014-Q4": D("3632452.557"), "2019-Q4": D("4317263.445")},
             ("A", "US"): {"2014-Q4": D("2748321.699"), "2019-Q4": D("2538435.28")}}
PIN_C10_F = {("A", "5J"): {"2019-Q4": D("107732.184")}}
PIN_C10_PREBREAK = D("10834001.584")
PIN_C11 = D("22470218.581")
PIN_C14 = {  # variant: (ids change, lbs change, flow sum, break sum, share)
    "P1": (2808426, D("908173.913"), D("251396.545"), D("656777.368"), D("75.56")),
    "P2": (2808425, D("251396.545"), D("251396.545"), D("656777.368"), D("91.78")),
    "P3": (2808426, D("223363.025"), D("262792.940"), D("-39429.915"), D("92.63")),
    "P4": (2755357, D("282882.718"), D("-154270.545"), D("437153.263"), D("90.69")),
    "N1": (2853732, D("1118060.332"), D("469838.819"), D("648221.513"), D("71.85")),
}
CAL_NEEDLES = ("52 cells", "sector ALL", "more than 1.0%")
CAL_MARK = "BIS IDS 2026-Q3 release"


def pin_status(ok, kind, vintage, L):
    """PASS when the pin holds. Otherwise FAIL on the vintage the pin was set on, WARN once a later vintage exists (2.4)."""
    if ok:
        return "PASS"
    if kind == "ids":
        return "FAIL" if qnum(L) <= qnum(IDS_PIN_LAST_Q) else "WARN"
    return "FAIL" if vintage < LBS_PIN_END.isoformat() else "WARN"


def sign(x):
    return (x > 0) - (x < 0)


def identity_gap(whole, parts):
    """(gap, number of absent parts) over present parts; (None, n) if the whole is absent."""
    if whole is None:
        return None, len(parts)
    absent = sum(1 for p in parts if p is None)
    return whole - sum(p for p in parts if p is not None), absent


def c05_status(gap, absent):
    if gap is None:
        return "PASS"
    lim = 7 if M("gap6_pass") else GAP_TOL
    if abs(gap) <= lim:
        return "PASS"
    if absent and not M("gap_absent_fail"):
        return "WARN"
    return "FAIL"


def c05_quarter(model, q):
    """(status, max abs gap, absent parts, details) of the C05 identities in quarter q, over both measures."""
    worst, gmax, nabs, notes = "PASS", 0, 0, []
    rank = {"PASS": 0, "WARN": 1, "FAIL": 2}
    for meas in MEAS:
        for g in ("ALL", "US", "ADV", "EMDE", "INTL_ORG"):
            whole = model.src(g, "ALL", meas, q)
            tops = [model.src(g, s, meas, q) for s in TOP_PARTS]
            if M("intl_inst_twice"):
                tops = tops + [model.src(g, "INTL_INST", meas, q)]
            gap, ab = identity_gap(whole, tops)
            st = c05_status(gap, ab)
            fin_parts = FIN_PARTS[:-1] if M("fin_without_cb") else FIN_PARTS
            gap2, ab2 = identity_gap(model.src(g, "FIN", meas, q), [model.src(g, p, meas, q) for p in fin_parts])
            st2 = c05_status(gap2, ab2)
            for lab, gp, a_, s_ in ((g + " ALL=GOV+FIN+NFC+INTL_INST", gap, ab, st), (g + " FIN=parts", gap2, ab2, st2)):
                if gp is not None:
                    gmax = max(gmax, abs(gp))
                    nabs += a_
                    if s_ != "PASS":
                        notes.append("%s %s gap %s, %d absent" % (meas, lab, gp, a_))
                if rank[s_] > rank[worst]:
                    worst = s_
    # the residence identity: ALL = ADV + EMDE + INTL_ORG, sector ALL
    for meas in MEAS:
        gap, ab = identity_gap(model.src("ALL", "ALL", meas, q), [model.src(g, "ALL", meas, q) for g in ("ADV", "EMDE", "INTL_ORG")])
        s_ = c05_status(gap, ab)
        if gap is not None:
            gmax = max(gmax, abs(gap))
            nabs += ab
            if s_ != "PASS":
                notes.append("%s ALL=ADV+EMDE+INTL_ORG gap %s, %d absent" % (meas, gap, ab))
        if rank[s_] > rank[worst]:
            worst = s_
    return worst, gmax, nabs, notes


def c06_result(Q, L):
    rows = []
    for q in qrange(C06_FIRST_Q, L):
        c = Q[("ALL", "ALL", q)]
        if c["net"] is not None and c["chg"] is not None and abs(c["net"]) >= C06_MIN_NET:
            rows.append((q, c["chg"], c["net"]))
    agree = sum(1 for q, chg, net in rows if sign(chg) == sign(net))
    need = Decimal("0.6") if M("c06_lenient") else C06_MIN_AGREE
    ok = bool(rows) and Decimal(agree) / Decimal(len(rows)) >= need
    gaps = "; ".join("%s %+d" % (q, chg - net) for q, chg, net in rows)
    return ok, agree, len(rows), gaps


def first_q_with_value(model, group, sector, meas="outstanding"):
    for q in model.qs:
        if model.src(group, sector, meas, q) is not None:
            return q
    return None


def calendar_check(cal):
    """(observed, status) of C09: absent is INFO; present, the row must hold the three phrases of the registered statement (G17)."""
    lines = [ln for ln in (cal or "").splitlines() if CAL_MARK in ln]
    if not lines:
        return "no CALENDAR row found", "INFO"
    needles = CAL_NEEDLES[:1] if M("c09_loose") else CAL_NEEDLES
    miss = [n for n in needles if n not in lines[0]]
    return ("row present with all three" if not miss else "missing: " + ", ".join(miss)), ("PASS" if not miss else "FAIL")


def pull_order_bad(pulls):
    """Consecutive pulls whose latest quarter goes backwards (a FAIL, 2.4)."""
    if M("earlier_latest_ok"):
        return []
    return [(a["date"], a["latest"], b["date"], b["latest"]) for a, b in zip(pulls, pulls[1:]) if qnum(b["latest"]) < qnum(a["latest"])]


def build_checks(c):
    pull, model, Q, cg = c["pull"], c["model"], c["Q"], c["cgfs"]
    L, vint = model.L, c["vintage"]
    rows = []

    def add(cid, desc, expected, observed, status):
        rows.append([cid, desc, expected, observed, status])

    def val(g, s, meas, q):
        return Q[(g, s, q)]["out" if meas == "outstanding" else "net"]

    def pins(group, spec):
        bad = []
        for meas, key in (("outstanding", "out"), ("net_issues", "net")):
            for q, want in spec[key].items():
                got = val(group, "ALL", meas, q)
                if got != want:
                    bad.append("%s %s %s: %s, pinned %s" % (group, meas, q, "blank" if got is None else thou(got), thou(want)))
        return bad
    kind = "ids"
    rev_note = "; see revisions.csv rows for this vintage" if qnum(L) > qnum(IDS_PIN_LAST_Q) else ""
    # C01, C02
    for cid, group, spec, label in (("C01", "ALL", PIN_C01, "IDS ALL"), ("C02", "US", PIN_C02, "IDS US")):
        bad = pins(group, spec)
        n = len(spec["out"]) + len(spec["net"])
        add(cid, "%s outstanding (%d quarters) and net issues (%d quarters) equal the author's pull of 23 Oct 2026 (IDS release 14 Sep 2026); a one-vintage pin" %
            (label, len(spec["out"]), len(spec["net"])), "%d values equal" % n,
            ("%d of %d equal" % (n - len(bad), n)) + ("" if not bad else "; " + "; ".join(bad[:4]) + rev_note), pin_status(not bad, kind, vint, L))
    # C03
    bad = []
    for g, spec in (("ALL", PIN_C03_ALL), ("US", PIN_C03_US)):
        for s, want in spec.items():
            got = val(g, s, "outstanding", "2019-Q4")
            if got != want:
                bad.append("%s %s: %s, pinned %s" % (g, s, "blank" if got is None else thou(got), thou(want)))
    gaps = []
    for g in ("ALL", "US"):
        gap, _ = identity_gap(val(g, "ALL", "outstanding", "2019-Q4"), [val(g, s, "outstanding", "2019-Q4") for s in TOP_PARTS])
        gap2, _ = identity_gap(val(g, "FIN", "outstanding", "2019-Q4"), [val(g, p, "outstanding", "2019-Q4") for p in FIN_PARTS])
        gaps.append((g, gap, gap2))
        if gap != 0 or gap2 != 0:
            bad.append("%s identity gaps at 2019-Q4: sectors %s, FIN parts %s (exact expected)" % (g, gap, gap2))
    add("C03", "Sector outstanding at 2019-Q4 (ALL nine values, US seven values) equal the pins and the identities are exact", "16 values equal, 4 gaps 0",
        "all equal; gaps 0" if not bad else "; ".join(bad[:4]) + rev_note, pin_status(not bad, kind, vint, L))
    # C04
    allres = pull["allres"]
    c04 = c04_rows(allres)
    st, stop, worst, notes = c04_status(c04)
    row19 = next((r for r in c04 if r[0] == "2019-Q4"), None)
    obs = "%d quarters; worst |d| at %s: d=%s (3P %s, sum of %d leaves %s)" % (len(c04), worst[0], thou(worst[4]), thou(worst[1]), worst[3], thou(worst[2])) if worst else "no 3P value"
    if notes:
        obs += "; " + "; ".join(notes[:3])
    add("C04", "3P includes the US: d = 3P - sum of the F5 leaf codes (all residence codes except 3P, 5R, 4T, 3C, 4Y, 4W, 4U) is within 0.1% of 3P in every quarter and does not match the signature of a 3P that excludes the US",
        "PASS; FAIL and STOP only on the signature", obs, st)
    ok = row19 is not None and row19[4] == PIN_C04["d"] and row19[3] == PIN_C04["leaves"]
    add("C04b", "At 2019-Q4: d = +57 over 131 leaf codes (the author's pull); a one-vintage pin", "d 57, 131 leaves",
        "no 2019-Q4 value" if row19 is None else "d %s over %d leaves" % (thou(row19[4]), row19[3]) + ("" if ok else rev_note), pin_status(ok, kind, vint, L))
    gap19 = identity_gap(val("ALL", "ALL", "outstanding", "2019-Q4"), [val(g, "ALL", "outstanding", "2019-Q4") for g in ("ADV", "EMDE", "INTL_ORG")])[0]
    add("C04c", "At 2019-Q4: ADV + EMDE + INTL_ORG = ALL exactly", "gap 0", "gap %s" % gap19, pin_status(gap19 == 0, kind, vint, L))
    # C05, C05b: every quarter
    for q in model.qs:
        st5, gmax, nabs, notes5 = c05_quarter(model, q)
        add("C05/%s" % q, "Identities in %s: ALL = GOV + FIN + NFC + INTL_INST, FIN = its five parts, for ALL, US, ADV, EMDE and INTL_ORG, both measures; ALL = ADV + EMDE + INTL_ORG" % q,
            "gap at most %d, or WARN with an absent part" % GAP_TOL, "largest gap %d; absent parts %d" % (gmax, nabs) + ("; " + "; ".join(notes5[:3]) if notes5 else ""), st5)
    for q in model.qs:
        ok5, det = model.c05b(q)
        add("C05b/%s" % q, "US-only identities in %s decide whether the NON_US cells of FIN_CENTRAL_BANK and INTL_INST may take the US value as zero (US ALL = GOV + FIN + NFC; US FIN = its published parts; each within %d)" % (q, GAP_TOL),
            "PASS", det, "PASS" if ok5 else "WARN")
    # C06
    ok6, agree, n6, gaps6 = c06_result(Q, L)
    add("C06", "Sign convention: for ALL, in the quarters from %s with |net issues| >= %s, sign(change in outstanding) equals sign(net issues) in at least 90%%; each quarter's gap (change minus net issues) listed" % (C06_FIRST_Q, thou(C06_MIN_NET)),
        ">= 90%", "%d of %d agree; gaps: %s" % (agree, n6, gaps6), "PASS" if ok6 else "FAIL")
    a, u = Q[("ALL", "ALL", "2019-Q4")], Q[("US", "ALL", "2019-Q4")]
    ok6b = (a["chg"], a["net"], u["chg"], u["net"]) == (147756, 147756, -14446, -14447)
    add("C06b", "At 2019-Q4: ALL change 147,756 = net issues 147,756; US change -14,446, net issues -14,447 (one-vintage pin)", "as stated",
        "ALL change %s, net %s; US change %s, net %s" % tuple(thou(x) for x in (a["chg"], a["net"], u["chg"], u["net"])) + ("" if ok6b else rev_note), pin_status(ok6b, kind, vint, L))
    # C07: units are hard tests in R3a; the level range is checked here
    out_of_range = [(q, val("ALL", "ALL", "outstanding", q)) for q in model.qs if val("ALL", "ALL", "outstanding", q) is None or not 5_000_000 <= val("ALL", "ALL", "outstanding", q) <= 50_000_000]
    nrows = len(pull["ids"]) + len(pull["nat"]) + len(pull["allres"]) + len(pull["lbs"])
    add("C07", "Units: every row is USD, UNIT_MULT 6, OBS_CONF F (hard content tests on %d rows) and ALL outstanding is within US$ 5.0 to 50.0 trillion in every quarter" % nrows,
        "all rows pass; range holds", "range holds in all %d quarters" % len(model.qs) if not out_of_range else "outside the range: %s" % out_of_range[:3], "FAIL" if out_of_range else "PASS")
    # C08
    bad = []
    for key, spec in (("out", PIN_C08["out"]), ("net", PIN_C08["net"])):
        for q, want in spec.items():
            got = Q[("US_NATIONALITY", "ALL", q)]["out" if key == "out" else "net"]
            if got != want:
                bad.append("US_NATIONALITY %s %s: %s, pinned %s" % (key, q, "blank" if got is None else thou(got), thou(want)))
    add("C08", "Nationality memo: US_NATIONALITY outstanding 2019-Q4 2,754,559 and 2013-Q4 1,955,757; net issues 2013-Q4 20,953 (a one-vintage pin)", "3 values equal",
        "3 of 3 equal" if not bad else "; ".join(bad) + rev_note, pin_status(not bad, kind, vint, L))
    # C09
    obs, st = calendar_check(c.get("calendar_text"))
    add("C09", "CALENDAR row for the 2026-12-07 revision check contains '52 cells', 'sector ALL' and 'more than 1.0%'", "row present with the three phrases", obs, st)
    # C10
    bad = []
    for (sec, cty), spec in PIN_C10_S.items():
        for q, want in spec.items():
            got = lbs_v(pull, "S", sec, cty, q)[0]
            if got != want:
                bad.append("S %s %s %s: %s, pinned %s" % (sec, cty, q, "blank" if got is None else dstr(got, 3), dstr(want, 3)))
    for (sec, cty), spec in PIN_C10_F.items():
        for q, want in spec.items():
            got = lbs_v(pull, "F", sec, cty, q)[0]
            if got != want:
                bad.append("F %s %s %s: %s, pinned %s" % (sec, cty, q, "blank" if got is None else dstr(got, 3), dstr(want, 3)))
    sv = lbs_v(pull, "S", "A", "5J", "2019-Q4")
    if not (sv[1] and sv[2] == PIN_C10_PREBREAK):
        bad.append("S A 5J 2019-Q4 flag/pre-break: %s/%s" % (sv[1], "blank" if sv[2] is None else dstr(sv[2], 3)))
    nb = sum(1 for q in qrange("2015-Q1", "2019-Q4") if lbs_v(pull, "S", "A", "5J", q)[1])
    if nb != 20:
        bad.append("S A 5J flagged B in %d of 20 quarters 2015-Q1..2019-Q4" % nb)
    add("C10", "LBS stocks and flows equal the author's pull (release of 31 Jul 2026), the 2019-Q4 break flag and pre-break value, and 20 of 20 quarters flagged B; a one-vintage pin",
        "all equal", "all equal; 20 of 20 flagged" if not bad else "; ".join(bad[:4]), pin_status(not bad, "lbs", vint, L))
    # C11
    tot = None if Q[("ALL", "ALL", "2019-Q4")]["out"] is None or sv[0] is None else Q[("ALL", "ALL", "2019-Q4")]["out"] + sv[0]
    if tot is None:
        add("C11", "Paper level: IDS ALL plus LBS S A 5J at 2019-Q4 within 3% of US$ 22.6 trillion", "within 3%", "blank", pin_status(False, "lbs", vint, L))
    else:
        dev = (tot / Decimal(PAPER_TOTAL_USD_M) - 1) * 100
        add("C11", "Paper level: IDS ALL plus LBS S A 5J at 2019-Q4 within 3% of US$ 22.6 trillion (author's pull: 22,470,218.581, -0.57%)", "within 3%",
            "%s, %s%% from 22,600,000" % (dstr(tot, 3), dstr(dev, 2)), pin_status(abs(dev) <= C11_TOL * 100, "lbs", vint, L))
    # C12
    fa, fu = first_q_with_value(model, "ALL", "ALL"), first_q_with_value(model, "US", "ALL")
    missing = [s for s in SECTORS if not any(model.src("ALL", s, "outstanding", q) is not None for q in model.qs)]
    natok = any(Q[("US_NATIONALITY", "ALL", q)]["out"] is not None for q in model.qs)
    ok12 = fa == FIRST_Q and fu == FIRST_Q and qnum(L) >= qnum("2026-Q2") and not missing and natok
    add("C12", "Coverage: first quarter %s for ALL and US; latest >= 2026-Q2; all 10 sectors present for ALL; US_NATIONALITY exists" % FIRST_Q, "as stated",
        "first quarter ALL %s, US %s; latest %s; missing sectors %s; nationality %s" % (fa, fu, L, ",".join(missing) or "none", "present" if natok else "absent"), "PASS" if ok12 else "FAIL")
    # C14
    for r in cg:
        want = PIN_C14[r["variant"]]
        got = (r["ids_change"], r["lbs_change"], r["flow"], r["brk"], r["share"])
        ok14 = (got[0] == want[0] and all(g is not None and abs(g - w) <= D("0.0006") for g, w in zip(got[1:4], want[1:4])) and got[4] is not None
                and abs(got[4] - want[4]) <= D("0.0100001"))
        add("C14/%s" % r["variant"], "Comparison row %s: IDS change, LBS change, LBS flow sum, break sum and share equal the second reviewer's values (share to 0.01 pp)" % r["variant"],
            "%s; %s; %s; %s; %s%%" % (thou(want[0]), dstr(want[1], 3), dstr(want[2], 3), dstr(want[3], 3), dstr(want[4], 2)),
            "%s; %s; %s; %s; %s%%" % (thou(got[0]), lstr(got[1]) or "blank", lstr(got[2]) or "blank", lstr(got[3]) or "blank", "blank" if got[4] is None else dstr(got[4], 2)),
            pin_status(ok14, "lbs", vint, L))
    # C15: soft labels
    soft = pull.get("soft", [])
    add("C15", "Descriptive labels of 2.2 are unchanged (a change is a WARN, not a STOP)", "no change", "no change" if not soft else "; ".join(soft[:3]), "WARN" if soft else "PASS")
    # C16: pulls in order
    pulls = c["pulls"]
    bad = pull_order_bad(pulls)
    add("C16", "A pull's latest quarter is not earlier than the previous pull's", "never earlier",
        "%d pull(s); latest quarters %s" % (len(pulls), ", ".join(p["latest"] for p in pulls)) if not bad else "earlier: %s" % (bad[0],), "FAIL" if bad else "PASS")
    # C17: the release line
    rd, rq = release_pair(vint)
    add("C17", "The IDS release on or before the pull date (from the 'International debt securities' line, never the DSS rows) is the release of the pull's latest quarter",
        "release of %s" % L, "release %s is for %s" % (rd or "none", rq or "none"), "PASS" if rq == L else "WARN")
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# summary.csv (section 4)
# ------------------------------------------------------------------------------------------------------------------------
BLIND_NO = (("2014-Q3", "2019-Q4"), ("2025-Q4", "2026-Q2"))


def blind_of(question, group, quarters):
    """`no` for every Q5 row; for ALL, US or NON_US rows touching 2014-Q3..2019-Q4 or 2025-Q4..2026-Q2; for US_NATIONALITY at 2013-Q4 or 2019-Q4; else `yes`."""
    if M("blind_q5_yes") and question == "Q5":
        return "yes"
    if M("blind_q1_yes") and question == "Q1":
        return "yes"
    if question == "Q5":
        return "no"
    if group in ("ALL", "US", "NON_US"):
        for q in quarters:
            if any(qnum(a) <= qnum(q) <= qnum(b) for a, b in BLIND_NO):
                return "no"
    if group == "US_NATIONALITY" and ("2013-Q4" in quarters or "2019-Q4" in quarters):
        return "no"
    return "yes"


def summary_rows(c):
    Q, L, cg = c["Q"], c["L"], c["cgfs"]
    rows = []

    def add(qn, window, g, s, stat, value, denom, touched):
        rows.append([qn, window, g, s, stat, value, denom, blind_of(qn, g, touched)])
    q19 = "2019-Q4"
    win = "2019-Q1..%s" % L
    wq = qrange(SHARES_FIRST_Q, L)
    # Q1 levels
    for g, s in groups_sectors():
        den = "US$ millions, face value outstanding"
        a, b = Q[(g, s, q19)]["out"], Q[(g, s, L)]["out"]
        add("Q1", q19, g, s, "outstanding_%s" % q19, istr(a), den, [q19])
        add("Q1", L, g, s, "outstanding_%s" % L, istr(b), den, [L])
        add("Q1", "%s..%s" % (q19, L), g, s, "change_%s_to_%s" % (q19, L), istr(sub(b, a)), den, [q19, L])
        vals = [(Q[(g, s, q)]["out"], q) for q in wq if Q[(g, s, q)]["out"] is not None]
        if vals:
            lo, hi = min(vals, key=lambda t: (t[0], qnum(t[1]))), max(vals, key=lambda t: (t[0], -qnum(t[1])))
            add("Q1", win, g, s, "min_outstanding", istr(lo[0]), den, wq)
            add("Q1", win, g, s, "min_outstanding_quarter", lo[1], den, wq)
            add("Q1", win, g, s, "max_outstanding", istr(hi[0]), den, wq)
            add("Q1", win, g, s, "max_outstanding_quarter", hi[1], den, wq)
        else:
            for st in ("min_outstanding", "min_outstanding_quarter", "max_outstanding", "max_outstanding_quarter"):
                add("Q1", win, g, s, st, "", den, wq)
    # Q2 windows
    for name, first, last in windows_for(L):
        qs = window_quarters(name, first, last)
        for g in ALL_GROUPS:
            for s in (("ALL",) if g == "US_NATIONALITY" else SECTORS):
                n, ch, oth, blank = window_sums(Q, g, s, qs)
                negs = [Q[(g, s, q)]["net"] for q in qs]
                nneg = "" if any(v is None for v in negs) else str(sum(1 for v in negs if v < 0))
                den = "US$ millions, summed over %d quarters %s to %s" % (len(qs), qs[0], qs[-1])
                add("Q2", name, g, s, "net_issues_sum", istr(n), den, qs)
                add("Q2", name, g, s, "other_change_sum", istr(oth), den, qs)
                add("Q2", name, g, s, "quarters_with_negative_net_issues", nneg, "number of quarters of %d" % len(qs), qs)
                pv = [(v, q) for v, q in zip(negs, qs) if v is not None]
                if pv:
                    lo, hi = min(pv, key=lambda t: (t[0], qnum(t[1]))), max(pv, key=lambda t: (t[0], -qnum(t[1])))
                    add("Q2", name, g, s, "min_quarterly_net_issues", istr(lo[0]), den, qs)
                    add("Q2", name, g, s, "min_quarterly_net_issues_quarter", lo[1], den, qs)
                    add("Q2", name, g, s, "max_quarterly_net_issues", istr(hi[0]), den, qs)
                    add("Q2", name, g, s, "max_quarterly_net_issues_quarter", hi[1], den, qs)
    # Q3 shares
    srows = {(r[0], r[1], r[2]): r for r in c["shares"]}
    for g in GROUPS:
        for s in SHARE_SECTORS:
            den = "share of %s" % denominator_label(g)
            a, b = srows[(q19, g, s)][3], srows[(L, g, s)][3]
            add("Q3", q19, g, s, "share_pct_%s" % q19, a, den, [q19])
            add("Q3", L, g, s, "share_pct_%s" % L, b, den, [L])
            add("Q3", "%s..%s" % (q19, L), g, s, "share_change_pp", "" if a == "" or b == "" else dstr(Decimal(b) - Decimal(a), 2), den, [q19, L])
            vals = [(Decimal(srows[(q, g, s)][3]), q) for q in wq if srows[(q, g, s)][3] != ""]
            if vals:
                lo, hi = min(vals, key=lambda t: (t[0], qnum(t[1]))), max(vals, key=lambda t: (t[0], -qnum(t[1])))
                add("Q3", win, g, s, "min_share_pct", dstr(lo[0], 2), den, wq)
                add("Q3", win, g, s, "min_share_quarter", lo[1], den, wq)
                add("Q3", win, g, s, "max_share_pct", dstr(hi[0], 2), den, wq)
                add("Q3", win, g, s, "max_share_quarter", hi[1], den, wq)
            else:
                for st in ("min_share_pct", "min_share_quarter", "max_share_pct", "max_share_quarter"):
                    add("Q3", win, g, s, st, "", den, wq)
    # Q4 residence and nationality, two separate totals; no difference row
    for g, what in (("US", "US-resident outstanding (issuer incorporated in the US), all sectors"), ("US_NATIONALITY", "US-nationality outstanding (issuer's parent headquartered in the US), all sectors")):
        a, b = Q[(g, "ALL", q19)]["out"], Q[(g, "ALL", L)]["out"]
        add("Q4", q19, g, "ALL", "outstanding_%s" % q19, istr(a), "US$ millions; " + what, [q19])
        add("Q4", L, g, "ALL", "outstanding_%s" % L, istr(b), "US$ millions; " + what, [L])
        vals = [(Q[(g, "ALL", q)]["out"], q) for q in wq if Q[(g, "ALL", q)]["out"] is not None]
        if vals:
            lo, hi = min(vals, key=lambda t: (t[0], qnum(t[1]))), max(vals, key=lambda t: (t[0], -qnum(t[1])))
            add("Q4", win, g, "ALL", "min_outstanding", istr(lo[0]), "US$ millions; " + what, wq)
            add("Q4", win, g, "ALL", "min_outstanding_quarter", lo[1], "US$ millions; " + what, wq)
            add("Q4", win, g, "ALL", "max_outstanding", istr(hi[0]), "US$ millions; " + what, wq)
            add("Q4", win, g, "ALL", "max_outstanding_quarter", hi[1], "US$ millions; " + what, wq)
    # Q5 the CGFS statement beside the build
    for r in cg:
        g = "NON_US" if r["variant"] == "N1" else "ALL"
        w = "%s..%s" % (r["first"], r["last"])
        den = "IDS change plus LBS change (%s), US$ millions" % r["variant"]
        add("Q5", w, g, "ALL", "%s_ids_share_of_increase_pct" % r["variant"], "" if r["share"] is None else dstr(r["share"], 2), den, [r["first"], r["last"]])
        add("Q5", w, g, "ALL", "%s_lbs_break_sum_usd_m" % r["variant"], lstr(r["brk"]), "LBS stock change minus BIS break-adjusted flows, US$ millions", [r["first"], r["last"]])
        add("Q5", w, g, "ALL", "%s_lbs_break_quarters" % r["variant"], str(r["bq"]), "quarters flagged B in the window", [r["first"], r["last"]])
        add("Q5", w, g, "ALL", "%s_reading" % r["variant"], r["reading"], "the reading rule in the README (band %d-%d%%)" % band(), [r["first"], r["last"]])
    # Q6 revisions
    revs = c["revisions"]
    pairs = sorted({(r[0], r[1]) for r in revs})
    if not pairs:
        add("Q6", "none", "", "", "status", "no pull yet", "", [])
    for a, b in pairs:
        sel = [r for r in revs if (r[0], r[1]) == (a, b)]
        w = "%s..%s" % (a, b) if a != "baseline" else b
        if a == "baseline":
            add("Q6", w, "", "", "status", "baseline pull; no earlier pull to compare with", "cells changed since the previous pull", [])
            continue
        absch = [abs(int(r[9])) for r in sel if r[9] != ""]
        pcs = [abs(Decimal(r[10])) for r in sel if r[10] != ""]
        before24 = sum(1 for r in sel if qnum(r[2]) < qnum("2024-Q1"))
        den = "cells of quarters up to the earlier pull's latest quarter, quarterly.csv basis"
        add("Q6", w, "", "", "cells_changed", str(len(sel)), den, [])
        add("Q6", w, "", "", "largest_abs_change_usd_m", str(max(absch)) if absch else "", den, [])
        add("Q6", w, "", "", "largest_abs_change_pct", dstr(max(pcs), 2) if pcs else "", den, [])
        add("Q6", w, "", "", "cells_changed_before_2024", str(before24), den, [])
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# writing: exact allowlists, source lines, wording and leak guards (G11, G12, G16)
# ------------------------------------------------------------------------------------------------------------------------
def allowlist(name):
    cols = list(ALLOW[name])
    if M("allow_drift") and name == "quarterly.csv":
        cols[cols.index("outstanding_usd_m")] = "outstanding_usd_m_share"
    return cols


def allow_text():
    return "".join("%s:%s\n" % (n, ",".join(allowlist(n))) for n in ALLOW_ORDER)


def spec_hash():
    return "0" * 64 if M("hash_wrong") else SPEC_ALLOW_SHA256


def hash_accepted(h):
    """The sha256 the allowlist must have. The superseded round-1 hash (4a156e71...a03f9) is not accepted."""
    round1_shaped = h.startswith(ROUND1_HASH_HEAD) and h.endswith(ROUND1_HASH_TAIL)
    if round1_shaped and M("round1_hash_ok"):
        return True
    return h == spec_hash() and not round1_shaped


def allow_problems():
    out = []
    if sha256_of(allow_text().encode("utf-8")) != spec_hash():
        out.append("SPEC_ALLOW_SHA256 is not the sha256 of the canonical allowlist text")
    if allow_text() != SPEC_ALLOW_TEXT and not M("allow_drift"):
        out.append("the allowlists differ from the typed canonical text")
    return out


FENCE_RX = re.compile(r"```\n(quarterly\.csv:.*?)```", re.S)


def spec_block_problems(spec_text):
    """The fenced canonical allowlist block of the spec must hash to SPEC_ALLOW_SHA256 (G11, when the spec is in _research/)."""
    if M("spec_drift"):
        spec_text = spec_text.replace("quarterly.csv:quarter,", "quarterly.csv:quarters,", 1)
    m = FENCE_RX.search(spec_text)
    if not m:
        return ["the spec has no fenced canonical allowlist block"]
    block = m.group(1)
    out = []
    if sha256_of(block.encode("utf-8")) != SPEC_ALLOW_SHA256:
        out.append("the spec's fenced block hashes to %s, not SPEC_ALLOW_SHA256" % sha256_of(block.encode("utf-8"))[:12])
    if block != SPEC_ALLOW_TEXT:
        out.append("the spec's fenced block differs from the allowlist text typed in this script")
    return out


def check_header(name, header):
    allow = allowlist(name)
    if M("extra_column_ok"):
        ok = list(header[:len(allow)]) == allow
    elif M("renamed_column_ok"):
        ok = len(header) == len(allow)
    else:
        ok = list(header) == allow
    if not ok:
        raise DataError("%s: header %r is not the exact column allowlist" % (name, list(header)))


def wording_problems(name, text):
    out = []
    if not M("causal_off"):
        out += ["causal wording %r" % h for h in sorted({re.sub(r"\s+", " ", m.group(0).lower()) for rx in (CAUSAL_RX, CAUSAL_EXTRA_RX) for m in rx.finditer(text)})]
    if not M("nonus_off"):
        for ln in text.splitlines():
            if NONUS_FUNDING_RX.search(ln) and VARIANT_RX.search(ln):
                out.append("a P1-P4 line labelled as funding to non-US residents")
                break
    return out


LOCAL_PATH_RX = re.compile(r"/Users/|/private/|/tmp/|~/")


def guard_text(name, text):
    probs = wording_problems(name, text)
    if probs:
        raise DataError("%s: %s" % (name, "; ".join(probs[:4])))
    home = os.path.expanduser("~")
    if home != "~" and home in text:
        raise DataError("%s: an absolute home path would be published" % name)


def render_csv(name, rows, source, header=None):
    header = allowlist(name) if header is None else header
    check_header(name, header)
    out = io.StringIO()
    out.write(source + "\n")
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


def source_line(name, dates):
    ds = ", ".join(dates)
    return "# source: %s%s, retrieved %s" % (SOURCE_LINE_ID, SOURCE_LINE_LBS if name == "cgfs_check.csv" else "", ds)


def csv_body(text):
    """(header, rows) of a committed csv text, skipping every `# source:` line (mutant: the source line is read as the header)."""
    lines = text.splitlines()
    if not M("source_as_header"):
        lines = [l for l in lines if not l.startswith("# source:")]
    rd = list(csv.reader(lines))
    return (rd[0], rd[1:]) if rd else ([], [])


RAW_LINE_RX = re.compile(r"^FREQ,(ISSUER_RES|L_MEASURE)", re.M)


def is_raw_sdmx(text):
    """A raw SDMX file: ANY line beginning FREQ,ISSUER_RES or FREQ,L_MEASURE, or a body containing "dataStructures" (R2-8, spec 6.1)."""
    if M("leak_raw_off"):
        return False
    if M("leak_first_line_only"):
        first = text.split("\n", 1)[0]
        hit = bool(re.match(r"FREQ,(ISSUER_RES|L_MEASURE)", first))
    else:
        hit = bool(RAW_LINE_RX.search(text))
    if not M("leak_json_off") and '"dataStructures"' in text:
        hit = True
    return hit


def leak_problems(files):
    """files = {name: text}. The 11 names, the exact headers, no raw SDMX file, no at sign, no local path (6.1, 6.2)."""
    out = []
    for n in sorted(files):
        t = files[n]
        if is_raw_sdmx(t):
            out.append("raw SDMX file in the committed folder: %s" % n)
        elif n not in COMMITTED and not (M("leak_name_off") or M("twelfth_ok")):
            out.append("file that is not one of the 11 committed names: %s" % n)
        if LOCAL_PATH_RX.search(t) and not M("leak_path_off"):
            out.append("%s contains a local path" % n)
        if "@" in t and not M("leak_at_off"):
            out.append("%s contains an at sign" % n)
    for n in sorted(set(COMMITTED) - set(files)):
        out.append("missing: %s" % n)
    for n in ALLOW_ORDER:
        if n in files and not is_raw_sdmx(files[n]):
            try:
                check_header(n, csv_body(files[n])[0])
            except DataError as e:
                out.append(str(e))
    return out


def tracked_text_files(root):
    """Files git would commit (tracked, or untracked and not ignored), so a raw SDMX file anywhere in the repository outside the cache is found."""
    try:
        r = subprocess.run(["git", "-C", root, "ls-files", "-co", "--exclude-standard", "-z"], capture_output=True, timeout=120)
        if r.returncode == 0:
            return [os.path.join(root, p) for p in r.stdout.decode("utf-8", "replace").split("\0") if p]
    except (OSError, subprocess.SubprocessError):
        pass
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != ".git"]
        out += [os.path.join(dp, f) for f in fn]
    return out


def repo_raw_problems(root, cache_dir=None):
    out = []
    cache_dir = os.path.realpath(cache_dir) if cache_dir else None
    for p in tracked_text_files(root):
        rp = os.path.realpath(p)
        if cache_dir and (rp == cache_dir or rp.startswith(cache_dir + os.sep)):
            continue
        try:
            if os.path.getsize(p) > 200 * 1024 * 1024 or os.path.islink(p) or not os.path.isfile(p):
                continue
            with open(p, "rb") as fh:
                head = fh.read()
        except OSError:
            continue
        if b"FREQ,ISSUER_RES" in head or b"FREQ,L_MEASURE" in head or b'"dataStructures"' in head:
            text = head.decode("utf-8", "replace")
            # outside the committed folder a text that merely mentions "dataStructures" (this script, the spec) is not a raw file: a JSON body is
            if M("leak_raw_off"):
                continue
            if RAW_LINE_RX.search(text) or (text.lstrip().startswith("{") and '"dataStructures"' in text):
                out.append("raw SDMX file outside the cache: %s" % os.path.relpath(p, root))
    return out


# ---- the static scan of this script (G14) ------------------------------------------------------------------------------------
REMOVERS = {("os", "remove"), ("os", "unlink"), ("os", "replace"), ("os", "rename"), ("shutil", "rmtree"), ("shutil", "move")}
METHOD_REMOVERS = {"unlink", "rename", "replace", "write_text", "write_bytes", "truncate"}


def static_stop_problems(src):
    """A removal, rename, replace, move or truncating write applied to a STOP path. STOP-ness is read from the argument or receiver text."""
    if M("static_scan_off"):
        return []
    out = []
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = None
        if isinstance(f, ast.Attribute):
            if isinstance(f.value, ast.Name) and (f.value.id, f.attr) in REMOVERS:
                name = "%s.%s" % (f.value.id, f.attr)
                texts = [ast.get_source_segment(src, a) or "" for a in node.args]
            elif f.attr in METHOD_REMOVERS and not (isinstance(f.value, ast.Name) and f.value.id in ("os", "shutil")):
                name = "." + f.attr
                texts = [ast.get_source_segment(src, f.value) or ""] + [ast.get_source_segment(src, a) or "" for a in node.args]
            else:
                continue
        elif isinstance(f, ast.Name) and f.id == "open":
            args = [ast.get_source_segment(src, a) or "" for a in node.args]
            mode = args[1] if len(args) > 1 else ""
            kw = {k.arg: ast.get_source_segment(src, k.value) or "" for k in node.keywords}
            mode = kw.get("mode", mode)
            if any(ch in mode for ch in "wa+") and "stop" in (args[0] if args else "").lower():
                name, texts = "open(..., %s)" % mode, args[:1]
            else:
                continue
        else:
            continue
        if any("stop" in t.lower() for t in texts):
            out.append("%s applied to a STOP path: %s" % (name, (ast.get_source_segment(src, node) or "")[:80]))
    return out


# ---- the frozen rules (R8, G17) ----------------------------------------------------------------------------------------------
SPEC_FROZEN = dict(window=("2014-Q4", "2019-Q4"), band=(65, 85), registered=("2026-10-23", "2019-Q4", "2026-Q1", ("ALL", "US"), "ALL", 1.0, 52),
                   lbs_path="/api/v2/data/dataflow/BIS/WS_LBS_D_PUB/1.0/Q.S+F.C.G.USD.A.5J.A.5A.A+I.5J+US.N?startPeriod=2013-Q4&format=csv",
                   reading=("consistent", "mixed", "mixed", "not_consistent"))
R3_1_MARKER = "R3-1 reading rule"


def frozen_current():
    win = (CGFS_FIRST, CGFS_LAST)
    if M("window_changed"):
        win = ("2015-Q1", CGFS_LAST)
    lbs = F_PATHS["F6"]
    if M("lbs_key_changed"):
        lbs = lbs.replace("A+I", "A")
    probe = lambda a, b: reading_of(Decimal(a), Decimal(b))
    return dict(window=win, band=band(), registered=registered(), lbs_path=lbs, reading=(probe(75, 80), probe(75, 91), probe(91, 75), probe(91, 92)))


def reg_literal(t):
    on, q0, q1, groups, sector, thr, n = t
    return '("%s", "%s", "%s", (%s), "%s", %s, %d)' % (on, q0, q1, ", ".join('"%s"' % g for g in groups), sector, thr, n)


def frozen_problems(sources_text, spec_text=None, cur=None):
    """Each frozen constant must equal the spec's text; a changed one needs a 'Build decisions' entry holding the old value (R8). The R3-1 entry must be present."""
    cur = cur or frozen_current()
    out = []
    dec = sources_text.split("## Build decisions", 1)[1] if "## Build decisions" in sources_text else ""
    if R3_1_MARKER not in dec or "75.56" not in dec or "91.78" not in dec or "would have printed" not in dec:
        out.append("the R3-1 entry (old rule, new rule, P1 75.56, P2 91.78, the old rule would have printed consistent) is missing from Build decisions")
    olds = {"window": " to ".join(SPEC_FROZEN["window"]), "band": "%d-%d" % SPEC_FROZEN["band"], "registered": reg_literal(SPEC_FROZEN["registered"]),
            "lbs_path": SPEC_FROZEN["lbs_path"], "reading": "mixed"}
    for k in ("window", "band", "registered", "lbs_path", "reading"):
        if cur[k] != SPEC_FROZEN[k]:
            old = olds[k]
            if "changed rule: %s" % k not in dec or old not in dec:
                out.append("frozen %s changed (%r, was %r) without a Build decisions entry holding the old value" % (k, cur[k], SPEC_FROZEN[k]))
    if spec_text is not None:
        want = {"registered": reg_literal(cur["registered"]), "window": "%s to %s" % cur["window"], "lbs_path": cur["lbs_path"], "band": "%d ≤ share ≤ %d" % cur["band"]}
        for k, lit in want.items():
            if lit not in spec_text:
                out.append("frozen %s (%s) is not found in the spec text" % (k, lit[:60]))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# README.md and SOURCES.md (generated, so the wording guards scan them)
# ------------------------------------------------------------------------------------------------------------------------
def md_table(head, rows, align=None):
    align = align or ["---"] * len(head)
    lines = ["| " + " | ".join(head) + " |", "|" + "|".join(align) + "|"]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(lines)


GROUP_WORDS = {"ALL": "all countries including the United States", "US": "issuers resident in the United States", "NON_US": "ALL minus US (computed here)",
               "ADV": "advanced economies", "EMDE": "emerging market and developing economies", "INTL_ORG": "the residence group of international organisations, whose issuers are in the sector INTL_INST",
               "US_NATIONALITY": "issuers whose parent is headquartered in the United States, wherever the issuer is incorporated (memo, sector ALL only)"}
SECTOR_WORDS = {"ALL": "all issuers", "GOV": "general government", "FIN": "financial corporations (the five parts below, central banks included)",
                "FIN_PRIV_BANK": "private banks", "FIN_PUB_BANK": "public banks", "FIN_PRIV_OFI": "private other financial institutions (OFI), the non-bank financial firms",
                "FIN_PUB_OFI": "public other financial institutions (OFI)", "FIN_CENTRAL_BANK": "central banks", "NFC": "non-financial corporations",
                "INTL_INST": "international institutions"}

COLUMN_DICT = [
    ("quarterly.csv", "quarter", "Calendar quarter, YYYY-Qn, from 2014-Q3."),
    ("quarterly.csv", "basis", "residence (where the issuer is incorporated) or nationality (where its parent is headquartered)."),
    ("quarterly.csv", "issuer_group", "ALL, US, NON_US, ADV, EMDE, INTL_ORG, or US_NATIONALITY; the groups overlap."),
    ("quarterly.csv", "sector", "ALL, GOV, FIN, the five FIN parts, NFC or INTL_INST."),
    ("quarterly.csv", "outstanding_usd_m", "Face value outstanding at quarter end, US$ millions."),
    ("quarterly.csv", "net_issues_usd_m", "Issues minus redemptions in the quarter, US$ millions."),
    ("quarterly.csv", "change_in_outstanding_usd_m", "Outstanding minus the previous quarter's outstanding; blank if either is blank."),
    ("quarterly.csv", "other_change_usd_m", "Change minus net issues: a residual, with no independent measurement."),
    ("quarterly.csv", "status", "ok, absent, partial, us_series_absent, us_value_absent or us_sum_mismatch (see Blanks)."),
    ("quarterly.csv", "derived", "source (published by the BIS) or identity (computed here from published series)."),
    ("quarterly.csv", "vintage", "Date of the pull folder the row was built from."),
    ("quarterly.csv", "ids_release", "Latest BIS international debt securities release date on or before the pull date."),
    ("shares.csv", "share_pct", "numerator_usd_m as a percentage of denominator_usd_m, two decimals."),
    ("shares.csv", "numerator_usd_m / denominator_usd_m / denominator", "The sector's outstanding, the same group's ALL-sector outstanding in the same quarter, and its label."),
    ("net_issues_windows.csv", "window, first_quarter, last_quarter", "2024; 2025; 2026 to the latest quarter; 2024 to the latest quarter."),
    ("net_issues_windows.csv", "quarters_n, quarters_blank", "Quarters in the window; quarters in which net issues, change or other change is blank."),
    ("net_issues_windows.csv", "net_issues_usd_m, change_in_outstanding_usd_m, other_change_usd_m", "Sums over the window; blank if any quarter is blank."),
    ("net_issues_windows.csv", "share_of_group_net_issues_pct / denominator", "The sector's sum of net issues over the group's ALL-sector sum; blank when that sum is zero or negative."),
    ("cgfs_check.csv", "variant, plain_name, definition", "P1 to P4 and N1, with their plain names and definitions."),
    ("cgfs_check.csv", "first_quarter, last_quarter", "The two quarters whose levels are differenced (P2: the first quarter is the level before the first flow)."),
    ("cgfs_check.csv", "ids_change_usd_m, lbs_change_usd_m, lbs_measure", "Securities increase and loan increase, and whether the loan figure is a stock difference or BIS break-adjusted flows."),
    ("cgfs_check.csv", "lbs_flow_sum_usd_m, lbs_break_sum_usd_m, lbs_break_quarters", "Sum of the BIS break-adjusted flows; stock change minus that sum; quarters flagged as series breaks."),
    ("cgfs_check.csv", "ids_share_of_increase_pct, denominator, reading, note", "Securities increase over the sum of the two increases; the sum; the reading under the rule in the comparison section; a note."),
    ("summary.csv", "question .. blind", "The descriptive questions Q1 to Q6, fixed in advance; blind is no where the reviewers or the author had already seen those values before the build, and yes otherwise."),
    ("revisions.csv", "vintage_prev .. change_pct", "Every cell that changed between two pulls, appended and never rewritten; one baseline row for the first pull."),
    ("registration_score.csv", "all columns", "A statement registered in advance (23 Oct 2026) about how far the BIS revises history at its next release, not about markets; PENDING until 2026-Q3 is in the file."),
    ("checks.csv", "check_id .. status", "Every check with its expected and observed text; PASS, FAIL, WARN or INFO."),
    ("fetch_log.csv", "all columns", "One row per request to stats.bis.org."),
]


def worked_row(Q):
    q = "2019-Q4"
    parts = [Q[("ALL", s, q)]["out"] for s in TOP_PARTS]
    tot = Q[("ALL", "ALL", q)]["out"]
    if None in parts or tot is None:
        return "The worked row could not be built: a 2019-Q4 value is blank."
    return ("Worked row (2019-Q4, group ALL, sector ALL): general government + financial corporations + non-financial corporations + international institutions = "
            "%s + %s + %s + %s = %s US$ millions." % tuple(thou(x) for x in parts + [tot]))


COMP_WORDS = {"ALL": "all-sector", "GOV": "government", "FIN": "financial-corporations", "NFC": "non-financial-corporations"}
MEAS_WORDS = {"outstanding": "outstanding", "net_issues": "net-issue"}


def value_absent_sentences(c):
    """One sentence per quarter and measure in which a NON_US cell is blank with us_value_absent, naming the missing US value (generated from the cells)."""
    Q, model, out = c["Q"], c["model"], []
    for q in model.qs:
        for meas in MEAS:
            secs = [s for s in SECTORS if Q[("NON_US", s, q)]["s_out" if meas == "outstanding" else "s_net"] == "us_value_absent"]
            if not secs:
                continue
            comps = " and ".join("US %s %s value" % (COMP_WORDS[x], MEAS_WORDS[meas]) for x in model.us_components_absent(q, meas))
            other = [m for m in MEAS if m != meas]
            kept = all(Q[("NON_US", s, q)]["s_out" if other[0] == "outstanding" else "s_net"] == "us_series_absent" for s in secs)
            out.append("In %s the %s is absent, so the NON_US %s cells of %s are blank with `us_value_absent`%s." % (
                q, comps, MEAS_WORDS[meas], " and ".join(secs), (", while their %s cells are filled" % MEAS_WORDS[other[0]]) if kept else ""))
    return out


def render_readme(c):
    Q, L, cg, vint, rel = c["Q"], c["L"], c["cgfs"], c["vintage"], c["release"]
    dates = [p["date"] for p in c["pulls"]]
    out = []
    A = out.append
    A("# US-dollar international debt securities by type of borrower and borrower country (BIS)\n")
    A(REQUIRED_S1 + " " + (REQUIRED_S2.replace("does not show why", "shows why") if M("s2_changed") else REQUIRED_S2) + "\n")
    A("Amounts are face value: the principal the issuer owes at maturity, not a market price. A security counts as international when at least one of "
      "its registration location, the law that governs it and its listing location lies outside the issuer's home country (BIS international debt securities "
      "overview); a dollar bond registered, governed and listed in its issuer's own country is outside these figures. Issuers are grouped by residence, the "
      "country where the issuer is incorporated; one memo series groups them by nationality, the country where the issuer's parent is headquartered, so a Cayman "
      "subsidiary of a US company is a non-US resident with US nationality. Central banks count inside the financial corporations (FIN).\n")
    A("The groups are: " + "; ".join("%s (%s)" % (g, GROUP_WORDS[g]) for g in ALL_GROUPS) + ". " + OVERLAP_SENTENCE + "\n")
    A("The sectors are: " + "; ".join("%s (%s)" % (s, SECTOR_WORDS[s]) for s in SECTORS) + ".\n")
    A("## The latest result\n")
    A("The data run to %s. The pull (the download of the BIS data) is dated %s, which is the vintage of every row; the latest BIS release on or before that date is dated %s (the BIS "
      "publishes \"no later than\" that date). An amount outstanding, or stock, is the face value owed at a quarter end; net issues are a flow, issues minus redemptions during the quarter. "
      "Amounts in this README are US$ billions (US$ millions divided by 1,000, one decimal); the csv files are in US$ millions. A blank is a value the BIS does not publish. "
      "A window named for a year, such as 2026 to the latest quarter, covers only the quarters reported so far.\n" % (L, vint, rel))
    for q in (L, "2019-Q4"):
        rows = [[s] + [bn(Q[(g, s, q)]["out"]) for g in GROUPS] for s in SECTORS]
        A("**Outstanding at %s, US$ billions**\n" % q)
        A(md_table(["Sector"] + list(GROUPS), rows) + "\n")
    wnames = [w[0] for w in windows_for(L)]
    wmap = {(r[0], r[3], r[4]): r for r in c["windows"]}
    A("**Net issues (issues minus redemptions), US$ billions, all sectors, by group and window**\n")
    A(md_table(["Group"] + wnames, [[g] + [bn(None if wmap[(w, g, "ALL")][7] == "" else int(wmap[(w, g, "ALL")][7])) for w in wnames] for g in ALL_GROUPS]) + "\n")
    A("**Net issues, US$ billions, group ALL, by sector and window**\n")
    A(md_table(["Sector"] + wnames, [[s] + [bn(None if wmap[(w, "ALL", s)][7] == "" else int(wmap[(w, "ALL", s)][7])) for w in wnames] for s in SECTORS]) + "\n")
    smap = {(r[0], r[1], r[2]): r for r in c["shares"]}
    A("**Sector shares, percent.** Each share is the sector's outstanding divided by the same group's ALL-sector outstanding in the same quarter "
      "(denominator: the group's ALL-sector outstanding, so the shares of GOV, FIN, NFC and INTL_INST add to about 100 within a group, and the five FIN parts add to the FIN share).\n")
    heads = ["Sector"] + ["%s %s" % (g, q) for g in ("ALL", "US", "NON_US") for q in ("2019-Q4", L)]
    rows = [[s] + [("blank" if smap[(q, g, s)][3] == "" else smap[(q, g, s)][3]) for g in ("ALL", "US", "NON_US") for q in ("2019-Q4", L)] for s in SHARE_SECTORS]
    A(md_table(heads, rows) + "\n")
    us, nat = Q[("US", "ALL", "2019-Q4")]["out"], Q[("US_NATIONALITY", "ALL", "2019-Q4")]["out"]
    usL, natL = Q[("US", "ALL", L)]["out"], Q[("US_NATIONALITY", "ALL", L)]["out"]
    A("**US residence and US nationality, two separate totals.** US-resident outstanding (issuer incorporated in the US), all sectors: US$ %sbn at 2019-Q4 and US$ %sbn at %s. "
      "US-nationality outstanding (issuer's parent headquartered in the US), all sectors: US$ %sbn at 2019-Q4 and US$ %sbn at %s. The difference between the two totals is only "
      "the net of two groups: issuers outside the US with a US parent (counted in the nationality total only) and issuers inside the US with a foreign parent "
      "(counted in the residence total only).\n" % (bn(us), bn(usL), L, bn(nat), bn(natL), L))
    # the comparison
    A("## Comparison with BIS CGFS Paper 65\n")
    p1, p2, p3, p4, n1 = cg
    A("Paper No 65 of the BIS Committee on the Global Financial System (CGFS), \"US dollar funding: an international perspective\" (June 2020), says in section 3.4 that about three fourths of the increase over "
      "the past five years in international US dollar funding was in marketable debt securities rather than bank lending (paraphrase). The paper's measure is global: "
      "it counts the international debt securities of every issuer, issuers in the United States included, and cross-border bank loans of all reporting countries "
      "including those in the United States (from the BIS locational banking statistics, LBS, which record banks' claims across borders by the counterparty's country), with loans "
      "between offices of the same bank (related offices) included. P1 to P4 therefore count borrowers everywhere, the United States included; N1 alone keeps securities of issuers outside the "
      "United States against loans to counterparties outside the United States. Here the window is %s to %s, twenty quarters ending at the paper's data date. "
      "The share is the securities increase divided by the sum of the securities increase and the loan increase.\n" % (CGFS_FIRST, CGFS_LAST))
    head = ["Variant", "Plain name", "Window", "Securities increase, US$ tn", "Loan increase, US$ tn", "Break sum, US$ bn", "Break quarters", "Share, %"]
    rows = []
    for r in cg:
        rows.append([r["variant"], r["plain"], "%s to %s" % (r["first"], r["last"]), tn(r["ids_change"]), tn(r["lbs_change"]), bn(r["brk"]),
                     "%d of %d" % (r["bq"], len(qrange(qadd(r["first"], 1), r["last"]))), "blank" if r["share"] is None else dstr(r["share"], 2)])
    if not M("readme_no_table"):
        A(md_table(head, rows) + "\n")
    A("A series break is a change in who reports or how they report, which moves a published stock without any new lending; the BIS flags such quarters, and its own flow series "
      "(adjusted for breaks and exchange rates) leaves them out. The break sum is the loan stock change minus the sum of the BIS break-adjusted flows over the same quarters: the part of the "
      "stock change that the adjusted flows do not count, mostly series breaks; break quarters are the quarters in the window in which a loan stock used is flagged as a series break. "
      "In P2 the loan increase is the sum of the adjusted flows, so P2's break sum is the stock change of P1 minus that sum. N1 is not the paper's measure: it keeps only issuers and borrowers outside the United States.\n")
    reading = p1["reading"]
    A("**Reading on this vintage: %s.** The rule: `consistent` only if the P1 and P2 shares both lie inside %d–%d%%, `mixed` if one lies inside and the other outside, "
      "`not_consistent` if both lie outside, `undefined` if either is blank; P3, P4 and N1 are described without a reading. A `mixed` or `not_consistent` reading is "
      "reported as it stands. The reading rule was set after the reviewers had seen the P1 and P2 values; the earlier rule, which looked at P1 alone, would have read %s.\n"
      % ((reading,) + band() + (round1_reading(p1["share"]),)))
    if inside(p1["share"]) and not M("readme_no_r22"):
        A(r22_sentence(cg) + "\n")
    # blanks
    A("## Blanks, derived series and flags\n")
    A("A blank cell means the BIS publishes no value for that series and quarter (some series start later, and a few never exist, such as a US central-bank series); it is never zero. "
      "NON_US is ALL minus US. It is blank when the ALL value is blank, or when a US series exists but that quarter is missing (`partial`). For the two sectors with no US series at "
      "all, FIN_CENTRAL_BANK and INTL_INST, the US value is taken as zero only in quarters where the US total equals the sum of its published sectors and the US financial total equals the sum "
      "of its published parts, each within 5 (US$ millions); those cells carry `us_series_absent`. The test is applied to each measure separately (outstanding, net issues): where the US values it needs are present but do not add up, the cells of that measure are blank with `us_sum_mismatch`; where a US value it needs is absent, they are blank with `us_value_absent`. "
      "`other_change_usd_m` is a residual, change minus net issues: it holds reclassifications, coverage changes and rounding, and it is not a measurement of any of them; "
      "for US-dollar debt there is no exchange-rate revaluation. The loan statistics' stocks carry series-break flags (%d of %d quarters in P1's window), so a stock change "
      "includes breaks; the BIS-calculated flows adjust for breaks and exchange rates, and both are shown with the gap between them in dollars.\n" % (p1["bq"], len(qrange(qadd(p1["first"], 1), p1["last"]))))
    for t in value_absent_sentences(c):
        A(t + "\n")
    A("## Columns\n")
    A(md_table(["File", "Column", "Meaning"], [[a, b, d] for a, b, d in COLUMN_DICT]) + "\n")
    A(worked_row(Q) + "\n")
    A("## Provenance\n")
    A("Source: Bank for International Settlements (BIS), international debt securities statistics and, for the comparison, locational banking statistics, retrieved %s from the BIS "
      "statistics service at stats.bis.org; the latest release on or before the last pull is dated %s. The BIS terms of use apply to these figures, not this repository's "
      "CC BY licence; the BIS gives no warranty; this is not investment advice; and the BIS does not endorse this work. The request log, the label allowlist, the "
      "window reasoning and the build decisions are in [SOURCES.md](SOURCES.md).\n" % (", ".join(dates), rel))
    return "\n".join(out)


def decisions(c):
    """The Build decisions list (R8, R9): the R3-1 entry first, then the readings chosen where the spec is silent or its rounds differ."""
    L, cg = c["L"], c["cgfs"]
    items = []
    if not M("r31_entry_missing"):
        items.append(
            "**%s (post-registration fix 1, 23 Oct 2026; disclosed in the spec before this script ran).** Old rule (round 1): the verdict rested on P1 alone, band 65-85%%. "
            "New rule (R3-1): `consistent` only if P1 and P2 both lie inside 65-85%%, `mixed` if they fall on opposite sides, `not_consistent` if both fall outside, "
            "`undefined` if either is blank. The values seen when the rule changed: P1 75.56%%, P2 91.78%% (both reviewers had computed them; this script had not run). "
            "The old rule would have printed `consistent` on the 23 Oct 2026 vintage; the new rule can only withhold that reading, never create it. "
            "The window (2014-Q4 to 2019-Q4) and the band were not changed. Old output values: reading `consistent` on the P1 row; new output values: `mixed` on both rows." % R3_1_MARKER)
    items += [
        "**Round 4 outranks the body (O-11, O-12, O-13, O-14).** README sentence 1 is the second reviewer's (\"This folder shows how many US dollars ...\"), not section 5.1's draft; the "
        "R2-2 sentence is round 4's full text with its two numbers generated; the C04 signed test is round 4's (PASS if |3P - sum of leaves| <= 0.1% of 3P and |(3P - sum of leaves) + US| >= 0.9 x US; "
        "FAIL and write STOP only if the second leg fails) and not section 8's earlier \"d < 0 and |d + US| <= 10% of US\"; the BIS terms are linked, quoted in under 15 words and summarised "
        "(O-14), so section 2.5's \"full text\" and section 5's \"SOURCES.md carries the full text\" are not followed and no copy of the terms is committed.",
        "**R2-2 sentence when the other shares are not all outside the band.** Round 4 prints it whenever P1 is inside the band and says the other shares are \"outside the band\". "
        "The numbers are generated; if a later vintage puts one of P2, P3 or P4 inside the band the clause becomes \"and at least one of these lies inside the band\" so the sentence stays true. "
        "On this vintage it is the reviewer's text.",
        "**Disclosure note on the P1 row.** The spec's text ends \"would read consistent\". The last word is generated from the round-1 rule applied to the current P1 share (consistent inside the band, "
        "not_consistent outside), so the note stays true on a later vintage. On the 23 Oct 2026 vintage it is the spec's text.",
        "**C05 covers both measures.** The identities are checked for outstanding and for net issues, for ALL, US, ADV, EMDE and INTL_ORG (ALL = GOV + FIN + NFC + INTL_INST; FIN = its five parts) "
        "and, at sector ALL, ALL = ADV + EMDE + INTL_ORG; one row per quarter from 2013-Q4, status the worst of the identities. The spec does not name the measure; the stricter reading was taken.",
        "**C05b is evaluated per measure (supervisor ruling after the first real-data build).** The US-only identities (US ALL = GOV + FIN + NFC; US FIN = its published parts; each within 5) are tested for outstanding and for net issues "
        "separately, and the verdict of a measure decides the NON_US cells of FIN_CENTRAL_BANK and INTL_INST for that measure only. If the identities hold, the cell takes the US value as zero (`us_series_absent`). If a US value the test needs is absent, "
        "the cell is blank with `us_value_absent`; if the values are present but the gap exceeds 5, it is blank with `us_sum_mismatch`. The one C05b row per quarter in checks.csv reports both measures and is a WARN if either fails. "
        "Old rule (first build): one joint verdict for both measures, so a missing US net-issue value in 2026-Q2 also blanked the outstanding cells as `us_sum_mismatch`; the 2026-Q2 outstanding gaps are -1 and 0, so under the new rule those cells are filled. "
        "Real data had been seen. Status `us_value_absent` is an addition to the spec's list of statuses.",
        "**NON_US status of a row** combines its two measures: both absent -> absent; any us_sum_mismatch -> us_sum_mismatch; any us_value_absent -> us_value_absent; any partial, or one measure absent -> partial; any us_series_absent -> "
        "us_series_absent; else ok. A source row is ok when both measures are present, absent when both are missing, partial otherwise.",
        "**Added check rows.** C04b (2019-Q4 d = +57 over 131 leaves), C04c (ADV + EMDE + INTL_ORG = ALL at 2019-Q4), C06b (2019-Q4 sign pins), C15 (descriptive labels), C16 (pull order), C17 (the release line "
        "of the calendar is the release of the pull's latest quarter, which would differ if the DSS rows were read), C18 (folder guards on the rendering), C19 (no raw SDMX file anywhere in the repository "
        "outside the cache; the files git would commit are scanned) and C13 (a second build leaves every sha256 unchanged). Pins are one-vintage checks: IDS pins FAIL while 2026-Q2 is the latest quarter "
        "and WARN once a later quarter is in the file; C10, C11 and C14 FAIL on a pull dated before 2026-10-30 and WARN after (2.4).",
        "**Scoring uses the first qualifying pull.** The baseline is the earliest pull whose IDS release is 2026-09-14; the score uses the earliest later pull whose latest quarter is 2026-Q3 or later "
        "(section 7 says \"newest\", the CALENDAR text says \"the first pull whose latest quarter is 2026-Q3\"; they agree until a second pull holds 2026-Q3, and the first is the one the statement names). "
        "A cell absent in either pull makes the result VOID. The change is compared unrounded: the registered 1.0% is exceeded when the exact change is above 1.0.",
        "**Revisions.** Cells are the quarterly.csv cells (all groups including NON_US, both measures, from 2014-Q3), compared between the newest pull and the newest earlier one for the quarters the earlier pull holds; "
        "a change from or to blank counts as a change. `value_*`, `change_usd_m` and `change_pct` are blank where a side is blank. The first pull writes one `baseline` row "
        "(`vintage_prev` = baseline).",
        "**cgfs_check.csv details.** `lbs_break_quarters` counts quarters after `first_quarter` up to `last_quarter` in which any stock series used is flagged B (P3: all-sector or related-offices; "
        "N1: all-countries or United States). P2's loan figure is the flow sum and its break sum is the all-sector stock change over the same window minus that sum, as in the spec's C14 table. "
        "LBS-derived values keep the published three decimals (the break sum is 656,777.368, not 656,777). `denominator` is the text of the sum of the two increases.",
        "**Windows.** `quarters_blank` counts quarters in which net issues, change or other change is blank; each sum is blank when its own series has a blank quarter. `first_quarter` and "
        "`last_quarter` are the first and last quarter of the window. The group denominator text carries the ALL-sector sum.",
        "**Summary statistics.** Minimum and maximum take the earliest quarter on a tie; Q1 and Q4 minimum and maximum run over 2019-Q1 to the latest quarter; Q6 summarises every comparison in revisions.csv. "
        "`blind` follows section 4 literally (ALL, US, NON_US only, plus US_NATIONALITY, and every Q5 row `no`); rows for ADV, EMDE and INTL_ORG are `yes` unless they are Q5.",
        "**Request log and dates.** `fetch` names the pull folder from the UTC date of the clock, which is the one place a clock is read; every date in an output comes from a pull-folder name (R5). "
        "Each pull folder keeps its own fetch_log.csv; the committed fetch_log.csv is rebuilt from all of them. The seeded replies the spec author cached were not used. The 2026-10-23 pull took seven requests across two runs: the first sent F1 (200) and F2, which timed out after 120 s (a socket fault, no reply, no STOP); "
        "the supervisor then resumed the fetch, which skipped the saved F1 and sent F2 to F6 (all 200). F2 was therefore requested twice and every other file once; the log shows all seven rows.",
        "**A timeout is not a refusal.** The spec latches STOP on a status other than 200 or a body that fails a content test. A request that gets no reply (a socket timeout or reset) has neither: "
        "the invocation ends, the request is logged with status socket_fault, no STOP file is written, nothing is retried by the script, and the files already saved stay in the pull folder. "
        "Whether to resume (a further fetch skips the saved files and sends only the requests still missing) is left to a person.",
        "**Failed builds.** A build with any FAIL row writes its files to data/bis_ids_dollar/_FAILED/ (gitignored) and leaves the committed files alone, as the earlier builds do.",
        "**LBS dataflow name.** The spec fixes the IDS dataflow name; for the LBS dataflow the observed name \"Locational banking\" is tested as a soft label (WARN) while its id, structure and dimension order are hard.",
        "**Wording.** No generated file labels P1 to P4 with the phrase that section 6.3 bans for them; the README says the paper's measure is global and that N1 is not the paper's measure. "
        "The causal pattern of section 6.3 is the guard, copied as a literal; the planted-phrase test covers each alternative. The literal's lean-clause (inherited from bin/hedged_ust_yield.py) matches the past tense but misses the bare present tense, so a second, stricter pattern covering the present and -ing forms is applied beside it; the literal is unchanged.",
        "**Raw-file rule outside the folder.** Inside data/bis_ids_dollar/ a raw SDMX file is any file with a line beginning with the first two column names of an IDS or LBS CSV header (6.1), or whose body holds "
        "the structure-message key named in 6.1, whatever its name or first line; this file therefore never writes that key out. For the rest of the repository (C19, and the second look in bin/check.sh M20) "
        "the key half applies to JSON bodies only, because the script and the spec name that key in prose and would otherwise be reported; the line rule applies to every file git would commit.",
    ]
    for fix in POST_FIXES:
        items.append(fix)
    return items


POST_FIXES = []        # post-registration fixes made after the first real-data build: date, reason, whether real data had been seen, old and new values (R8)


def render_sources(c):
    L, cg, vint = c["L"], c["cgfs"], c["vintage"]
    dates = [p["date"] for p in c["pulls"]]
    out = []
    A = out.append
    A("# Sources and build decisions: US-dollar international debt securities (BIS)\n")
    A("Specification: `_research/2026-10-23-BIS-IDS-Dollar-Spec.md` (committed at 203112e, with its rulings of rounds 1 to 4). Script: `bin/bis_ids_dollar.py`. Pull dates: %s. "
      "The second reviewer and Grok computed the five comparison rows (P1 75.56%%, P2 91.78%%, P3 92.63%%, P4 90.69%%, N1 71.85%%) on real data before this build, "
      "so the comparison is not blind; the window and the 65-85%% band were not changed afterwards.\n" % ", ".join(dates))
    A("## Requests (all to stats.bis.org, GET, at least 2 s apart, no redirect followed)\n")
    A(md_table(["Id", "What", "Path"], [
        ["F1", "IDS dataflow structure (labels and dimension order)", "`%s`" % F_PATHS["F1"]],
        ["F2", "LBS dataflow structure", "`%s`" % F_PATHS["F2"]],
        ["F3", "IDS main series: five residence groups, ten sectors, outstanding and net issues", "`%s`" % F_PATHS["F3"]],
        ["F4", "IDS nationality memo (issuer nationality US)", "`%s`" % F_PATHS["F4"]],
        ["F5", "IDS all residences, total only, for check C04", "`%s`" % F_PATHS["F5"]],
        ["F6", "LBS: stocks and BIS break-adjusted flows, eight series (comparison only)", "`%s`" % F_PATHS["F6"]]]) + "\n")
    A("Base address `https://stats.bis.org`. Raw replies stay in the gitignored cache `data/vintages/bis_ids_dollar/<pull date>/`; only the selected quarterly aggregates and statistics derived from them are committed.\n")
    A("## BIS terms\n")
    A("The BIS terms of use are at %s (read by hand on 23 Oct 2026). The core condition is: \"%s\" the BIS is cited as the source when the statistics are reproduced. "
      "In plain words, the other conditions are: a translation must say it is not an official BIS translation; use must not mislead or imply endorsement or affiliation; "
      "a commercial product may not charge extra for including them; the BIS gives no warranty and accepts no liability; nothing in the statistics is investment advice; "
      "no other use is permitted. The terms for the API are separate and concern the API itself, which is not redistributed. No copy of the terms is committed.\n" % (BIS_LEGAL_URL, BIS_QUOTE))
    A("## Label allowlist (content test R3a)\n")
    A("A semantic label that differs from the list is a STOP; a descriptive label that differs is a WARN in checks.csv. Semantic, IDS: " +
      "; ".join("%s %s = %s" % t for t in IDS_SEMANTIC) + ". Semantic, LBS: " + "; ".join("%s %s = %s" % t for t in LBS_SEMANTIC) + ". Descriptive: " +
      "; ".join("%s %s = %s" % t for t in IDS_DESCRIPTIVE + LBS_DESCRIPTIVE) + ".\n")
    A("## Release dates\n")
    A("Release dates are the \"International debt securities\" line (category IDS) of the BIS release calendar (%s; the rows load from the calendar's JSON feed), "
      "never the \"Debt securities statistics\" (DSS) rows, which carry a different quarter on the same dates. The script holds %d release dates (%s to %s, as constants); only the latest ones reach the outputs, through the ids_release column, which is the latest date on or before the pull date. The most recent five: " % (RELCAL_URL, len(IDS_RELEASES), IDS_RELEASES[0][0], IDS_RELEASES[-1][0]) +
      ", ".join("%s on %s" % (q, d) for q, d in IDS_RELEASES[-5:]) + ". Locational banking statistics: 2026-Q2 on 2026-10-30. \"Data are released no later than the specified date.\"\n")
    A("## The 3P finding\n")
    A("In this dataflow the residence code `3P` is labelled \"All countries excluding residents\" but is the world total including US residents: at 2019-Q4 (all issuers, outstanding) "
      "3P equals 5R + 4T + 1C exactly, and 3P minus the sum of the 131 leaf residence codes (every code except 3P, 5R, 4T, 3C, 4Y, 4W, 4U; `1C` and `1Z` are leaves) is +57. "
      "An alphabetic leaf rule (two letters only) would drop 1C and 1Z and leave a gap of +899,535. So NON_US = ALL - US. Check C04 guards this each build.\n")
    A("## Window reasoning\n")
    A("The paper states a five-year increase and gives its data date as Q4 2019 (page 4: international debt securities plus cross-border loans \"$22.6 trillion as of Q4 2019\"). "
      "It does not print the start quarter. The window is read as the five years to that date, 2014-Q4 to 2019-Q4 (twenty quarters, level to level); a window one quarter earlier "
      "(2014-Q3 to 2019-Q3) is printed beside it as P4 without a reading. The paper's Graph 10 definition (loans by banks in all reporting countries including interoffice loans, and "
      "debt securities including issuance by entities in the United States) is P1; Graph 1's note 3 (excluding interoffice claims) is P3. The definition check: IDS ALL at 2019-Q4 plus the "
      "all-sector US-dollar cross-border loans is close to the paper's $22.6 trillion (check C11).\n")
    A("## Column provenance\n")
    A("`outstanding_usd_m` and `net_issues_usd_m` are BIS series (measures I and G) for immediate-issuer sector, issuer residence, all currencies-USD, international markets, face value; "
      "`change_in_outstanding_usd_m` and `other_change_usd_m` are differences computed here; NON_US is ALL minus US computed here; US_NATIONALITY is the BIS nationality series with residence 3P and nationality US. "
      "LBS values are the BIS series S (stock) and F (FX and break adjusted change), counterparty-country 5J and US, counterparty sectors A and I.\n")
    A("## Build decisions\n")
    for i, t in enumerate(decisions(c), 1):
        A("%d. %s" % (i, t))
    A("")
    return "\n".join(out)
# ------------------------------------------------------------------------------------------------------------------------
# compute, render, finish
# ------------------------------------------------------------------------------------------------------------------------
def quarterly_cells_from_rows(rows):
    """The previous-vintage cells read back from a committed quarterly.csv. Used only by the G15 mutant that must be caught."""
    out = {}
    for r in rows:
        out[(r[0], r[1], r[2], r[3], "outstanding")] = int(r[4]) if r[4] != "" else None
        out[(r[0], r[1], r[2], r[3], "net_issues")] = int(r[5]) if r[5] != "" else None
    latest = max((r[0] for r in rows), key=qnum)
    return out, latest, rows[0][10]


def compute(inp):
    """inp: pulls (parsed, in pull-folder-date order), existing_revisions, existing_quarterly, fetch_rows, calendar_text, root."""
    pulls = inp["pulls"]
    pull = pulls[-1]
    vintage = now_date().isoformat() if M("clock_vintage") else pull["date"]
    release = release_of(vintage)
    model = Model(pull)
    Q = quarter_cells(model, pull["nat"])
    c = dict(inp=inp, pulls=pulls, pull=pull, vintage=vintage, release=release, model=model, Q=Q, L=model.L, calendar_text=inp.get("calendar_text"))
    c["quarterly"] = quarterly_rows(Q, model.qs, vintage, release)
    c["shares"] = share_rows(Q, model.qs)
    c["windows"] = window_rows(Q, model.L)
    c["cgfs"] = cgfs_rows(pull, Q)
    existing = inp.get("existing_revisions", [])
    if len(pulls) > 1:
        prev = pulls[-2]
        if M("prev_from_quarterly") and inp.get("existing_quarterly"):
            cp, plat, pdate = quarterly_cells_from_rows(inp["existing_quarterly"])
            prev = dict(prev, date=pdate, latest=plat)
            cand = revision_candidates_cells(cp, prev, pull)
        else:
            cand = revision_candidates(prev, pull)
        c["revisions"] = merge_revisions(existing, cand)
    else:
        c["revisions"] = merge_revisions(existing, [], first_pull_date=pull["date"])
    c["score"] = registration_row(pulls)
    c["summary"] = summary_rows(c)
    c["checks"] = build_checks(c)
    return c


def revision_candidates_cells(cp, prev, new):
    cn = cell_values(new)
    rows = []
    for k in sorted(cp, key=rev_sort_key):
        if qnum(k[0]) > qnum(prev["latest"]):
            continue
        vp, vn = cp[k], cn.get(k)
        if vp == vn:
            continue
        chg = None if vp is None or vn is None else vn - vp
        pc = None if chg is None or vp == 0 else pct2(chg, vp)
        rows.append([prev["date"], new["date"], k[0], k[1], k[2], k[3], k[4], istr(vp), istr(vn), istr(chg), "" if pc is None else dstr(pc, 2)])
    return rows


def render_fetch_log(rows, dates):
    return render_csv("fetch_log.csv", rows, "# source: request log of bin/bis_ids_dollar.py fetch (stats.bis.org), pull folders " + (", ".join(dates) if dates else "(none)"))


def render_texts(c):
    inp, vint = c["inp"], c["vintage"]
    dates = [p["date"] for p in c["pulls"]]
    t = {}
    t["quarterly.csv"] = render_csv("quarterly.csv", c["quarterly"], source_line("quarterly.csv", [vint]))
    t["shares.csv"] = render_csv("shares.csv", c["shares"], source_line("shares.csv", [vint]))
    t["net_issues_windows.csv"] = render_csv("net_issues_windows.csv", c["windows"], source_line("net_issues_windows.csv", [vint]))
    t["cgfs_check.csv"] = render_csv("cgfs_check.csv", cgfs_csv_rows(c["cgfs"]), source_line("cgfs_check.csv", [vint]))
    t["summary.csv"] = render_csv("summary.csv", c["summary"], source_line("summary.csv", [vint]))
    t["revisions.csv"] = render_csv("revisions.csv", c["revisions"], source_line("revisions.csv", dates))
    t["registration_score.csv"] = render_csv("registration_score.csv", [c["score"]], source_line("registration_score.csv", dates))
    t["checks.csv"] = render_csv("checks.csv", c["checks"], source_line("checks.csv", [vint]))
    t["fetch_log.csv"] = render_fetch_log(inp.get("fetch_rows", []), dates)
    t["README.md"] = render_readme(c)
    t["SOURCES.md"] = render_sources(c)
    for n in ("README.md", "SOURCES.md"):
        guard_text(n, t[n])
    return t


def texts_digest(texts):
    return {n: sha256_of(x.encode("utf-8")) for n, x in sorted(texts.items()) if n != "checks.csv"}


def finish(c):
    """Add C13 (a second build leaves every file unchanged, revisions.csv included), C18 (the folder guards on the rendering) and C19 (no raw file in the repo)."""
    t1 = render_texts(c)
    inp2 = dict(c["inp"])
    inp2["existing_revisions"] = csv_body(t1["revisions.csv"])[1]
    inp2["existing_quarterly"] = csv_body(t1["quarterly.csv"])[1]
    t2 = render_texts(compute(inp2))
    if M("render_unstable"):
        t2["quarterly.csv"] += "x"
    same = texts_digest(t1) == texts_digest(t2)
    c["checks"] = c["checks"] + [["C13", "Fixed output: a second build over the same cache leaves every file's sha256 unchanged, revisions.csv included", "identical",
                                   "identical (%d files)" % len(texts_digest(t1)) if same else "DIFFERENT", "PASS" if same else "FAIL"]]
    probs = leak_problems(t1)
    probs += [("%s: %s" % (n, p)) for n, tx in t1.items() for p in wording_problems(n, tx)]
    probs += frozen_problems(t1["SOURCES.md"])
    c["checks"] = c["checks"] + [["C18", "Folder guards on the rendering: the 11 names, exact headers, no raw SDMX file, no at sign, no local path, no causal wording, the frozen rules and the R3-1 entry",
                                   "no problem", "; ".join(probs[:3]) if probs else "no problem", "FAIL" if probs else "PASS"]]
    root = c["inp"].get("root")
    if root:
        rp = repo_raw_problems(root, c["inp"].get("cache"))
        c["checks"] = c["checks"] + [["C19", "No raw SDMX file anywhere in the repository outside the cache (any line beginning FREQ,ISSUER_RES or FREQ,L_MEASURE, or a body holding dataStructures)",
                                       "none", "; ".join(rp[:3]) if rp else "none", "FAIL" if rp else "PASS"]]
    texts = render_texts(c)
    failed = [r[0] for r in c["checks"] if r[4] == "FAIL"]
    return texts, failed


# ------------------------------------------------------------------------------------------------------------------------
# inputs from the cache, outputs, the commands
# ------------------------------------------------------------------------------------------------------------------------
def pull_folders(cache):
    if not os.path.isdir(cache):
        return []
    return sorted(d for d in os.listdir(cache) if DATE_RX.match(d) and os.path.isdir(os.path.join(cache, d)))


def read_pull_files(folder):
    out = {}
    for k, fn in F_FILES.items():
        p = os.path.join(folder, fn)
        if os.path.exists(p):
            with open(p, "rb") as fh:
                out[k] = fh.read()
    return out


def load_inputs(cache, out_dir, root=ROOT, calendar_path=None):
    pulls, log_rows, skipped = [], [], []
    for d in pull_folders(cache):
        folder = os.path.join(cache, d)
        _, rows = read_csv_rows(os.path.join(folder, "fetch_log.csv"))
        log_rows += rows
        files = read_pull_files(folder)
        if len(files) < 6:
            skipped.append(d)
            continue
        pulls.append(load_pull(d, files))
    if not pulls:
        raise DataError("no complete pull in the cache (%s); run fetch first" % tilde(cache))
    cal = None
    cp = calendar_path or os.path.join(root, "CALENDAR.tsv")
    if os.path.exists(cp):
        with open(cp, encoding="utf-8") as fh:
            cal = fh.read()
    _, rev = read_csv_rows(os.path.join(out_dir, "revisions.csv"))
    _, qrows = read_csv_rows(os.path.join(out_dir, "quarterly.csv"))
    return dict(pulls=pulls, existing_revisions=rev, existing_quarterly=qrows, fetch_rows=log_rows, calendar_text=cal, root=root, cache=cache, skipped=skipped)


def write_outputs(texts, out_dir, failed):
    target = os.path.join(out_dir, "_FAILED") if failed and not M("failed_to_committed") else out_dir
    for n, x in texts.items():
        write_text(os.path.join(target, n), x)
    return target


def run_build(a):
    t0 = time.time()
    cache = check_cache(a.cache, out_dir=a.out)
    inp = load_inputs(cache, a.out)
    c = compute(inp)
    texts, failed = finish(c)
    target = write_outputs(texts, a.out, failed)
    print("vintage %s (pulls: %s); latest quarter %s; IDS release %s" % (c["vintage"], ", ".join(p["date"] for p in c["pulls"]), c["L"], c["release"]))
    if inp["skipped"]:
        print("incomplete pull folders skipped: %s" % ", ".join(inp["skipped"]))
    print("== checks (non-quarterly rows listed; quarterly C05 and C05b rows summarised)")
    quarterly_ids = [r for r in c["checks"] if r[0].startswith(("C05/", "C05b/"))]
    for r in c["checks"]:
        if not r[0].startswith(("C05/", "C05b/")):
            print("   %-8s %-5s %s" % (r[0], r[4], r[3][:170]))
    for pre in ("C05/", "C05b/"):
        rs = [r for r in quarterly_ids if r[0].startswith(pre)]
        cnt = collections.Counter(r[4] for r in rs)
        print("   %-8s %s over %d quarters" % (pre.rstrip("/"), ", ".join("%s %d" % kv for kv in sorted(cnt.items())), len(rs)))
        for r in rs:
            if r[4] != "PASS":
                print("            %s %s %s" % (r[0], r[4], r[3][:150]))
    print("== comparison (variant: ids change | lbs change | flow sum | break sum | break quarters | share | reading)")
    for r in c["cgfs"]:
        print("   %s: %s | %s | %s | %s | %d | %s | %s" % (r["variant"], thou(r["ids_change"]), lstr(r["lbs_change"]), lstr(r["flow"]), lstr(r["brk"]), r["bq"],
                                                          "blank" if r["share"] is None else dstr(r["share"], 2), r["reading"]))
    print("== registration: %s" % " | ".join(c["score"]))
    print("failed: %s; wrote %d files to %s (%.1f s)" % (", ".join(failed) or "none", len(texts), tilde(target), time.time() - t0))
    return 1 if failed else 0


def sync_committed_log(cache, out_dir):
    """Rebuild the committed fetch_log.csv from the pull folders' own logs (the cache is the record; this is its copy)."""
    rows, dates = [], []
    for d in pull_folders(cache):
        _, r = read_csv_rows(os.path.join(cache, d, "fetch_log.csv"))
        if r:
            rows += r
            dates.append(d)
    if rows:
        write_text(os.path.join(out_dir, "fetch_log.csv"), render_fetch_log(rows, dates))


def run_fetch(a, opener=real_opener, stop_path=STOP_PATH, say=print):
    if os.path.exists(stop_path) and not M("stop_ignored"):
        say("STOP present: %s" % tilde(stop_path))
        return 2
    pull_date = now_date().isoformat()
    os.makedirs(a.out, exist_ok=True)
    fe = Fetcher(a.cache, a.out, pull_date, stop_path=stop_path, sleep=a.sleep, max_requests=a.max_requests, opener=opener)
    code = 0
    try:
        fe.check_stop()
        n = fe.run(plan(), say=say)
        say("requests sent %d, files saved %d (pull folder %s)" % (fe.requests, n, pull_date))
    except Latched as e:
        say("%s" % e)
        say("requests sent %d; the run ends here and nothing is retried" % fe.requests)
        code = 2
    except MaxRequests as e:
        say("stopped by the request cap (%s); requests sent %d" % (e, fe.requests))
        code = 3
    except SocketFault as e:
        say("socket fault (%s): the invocation ends; nothing was latched and nothing is retried" % e)
        code = 4
    finally:
        sync_committed_log(fe.cache, a.out)
    return code


# ------------------------------------------------------------------------------------------------------------------------
# selftest: synthetic data only. Every guard G1-G20 of the spec's section 9 has a test; each mutant (a deliberately broken variant, switched on in
# this process only) must make its guard's test fail. A mutant that is not caught is a failure.
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


class FakeClock:
    def __init__(self, t=1_000_000.0):
        self.t = t

    def wall(self):
        return self.t

    def sleep(self, s):
        self.t += s


def fill_path(anchors, qs):
    """Integer path through the anchors {quarter: value}: linear between consecutive anchors, the remainder spread over the first steps."""
    ks = sorted(anchors, key=qnum)
    out = {}
    for a, b in zip(ks, ks[1:]):
        n = qnum(b) - qnum(a)
        diff = anchors[b] - anchors[a]
        base, rem = divmod(diff, n)
        v = anchors[a]
        out[a] = v
        for i in range(1, n + 1):
            v += base + (1 if i <= rem else 0)
            out[qadd(a, i)] = v
    return {q: out[q] for q in qs}


def fill_dec(anchors, qs):
    ks = sorted(anchors, key=qnum)
    out = {}
    for a, b in zip(ks, ks[1:]):
        n = qnum(b) - qnum(a)
        for i in range(0, n + 1):
            out[qadd(a, i)] = (anchors[a] + (anchors[b] - anchors[a]) * i / n).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    for k in ks:
        out[k] = anchors[k]
    return {q: out[q] for q in qs}


def split_milli(total, n):
    """n Decimals with 3 decimals summing exactly to total."""
    m = int((total * 1000).to_integral_value())
    base, rem = divmod(m, n)
    return [Decimal(base + (1 if i < rem else 0)) / 1000 for i in range(n)]


IDS_ROW = "Q,{res},{nat},{imm},1,C,A,A,USD,A,A,A,A,A,{meas},0,USD,6,,,{q},{v},A,,F"
LBS_ROW = "Q,{m},C,G,USD,A,5J,A,5A,{sec},{cty},N,3,USD,6,K,,,S,E,{q},{v},{st},F,{pb}"
RESIDENCE_FIXED = {"3P": "3P", "5R": "5R", "4T": "4T", "1C": "1C", "US": "US"}


def pinned_values(L="2026-Q2"):
    """IDS cells of a synthetic world whose pinned cells equal the spec's C01-C08 values and whose identities are exact.
    Returns {(res, imm, meas, q): int}, the nationality memo {(meas, q): int} and the leaf-by-leaf level vectors."""
    qs = qrange(FIRST_Q, L)
    a3 = {"2013-Q4": 8_000_000, "2014-Q3": 8_683_591, "2014-Q4": 8_778_278, "2019-Q3": 11_438_948, "2019-Q4": 11_586_704, "2025-Q4": 15_525_836,
          "2026-Q1": 15_871_836, "2026-Q2": 16_274_316}
    au = {"2013-Q4": 1_400_000, "2014-Q3": 1_485_957, "2014-Q4": 1_498_712, "2019-Q3": 1_467_852, "2019-Q4": 1_453_406, "2025-Q4": 1_835_190,
          "2026-Q1": 1_878_256, "2026-Q2": 1_952_509}
    an = {"2013-Q4": 1_955_757, "2019-Q3": 2_700_000, "2019-Q4": 2_754_559, "2026-Q2": 3_600_000}
    if L == "2026-Q3":
        a3["2026-Q3"], au["2026-Q3"], an["2026-Q3"] = 16_700_000, 1_990_000, 3_700_000
    t3, tu = fill_path(a3, qs), fill_path(au, qs)
    p3p = dict(PIN_C03_ALL)
    pus = dict(PIN_C03_US)
    us_secs = ("GOV", "FIN_PRIV_BANK", "FIN_PUB_BANK", "FIN_PRIV_OFI", "FIN_PUB_OFI", "NFC")
    wus = {s: pus[s] for s in us_secs}
    leaf = ("GOV", "FIN_PRIV_BANK", "FIN_PUB_BANK", "FIN_PRIV_OFI", "FIN_PUB_OFI", "FIN_CENTRAL_BANK", "NFC", "INTL_INST")
    lev = {}
    for s in us_secs:
        lev[("US", s)] = {q: (tu[q] * wus[s] + 726_703) // 1_453_406 for q in qs}
    for q in qs:
        lev[("US", "FIN_PRIV_OFI")][q] = tu[q] - sum(lev[("US", s)][q] for s in us_secs if s != "FIN_PRIV_OFI")
    c1 = {q: (578_267 * t3[q] + 5_793_352) // 11_586_704 for q in qs}
    lev[("INTL_ORG", "INTL_INST")] = c1
    r19 = {s: p3p[s] - pus.get(s, 0) - (578_267 if s == "INTL_INST" else 0) for s in leaf}
    rtot19 = sum(r19.values())
    f_num, f_den = 7_533_432, rtot19
    for q in qs:
        r = t3[q] - tu[q] - c1[q]
        rs = {s: (r * r19[s] + rtot19 // 2) // rtot19 for s in leaf}
        rs["GOV"] += r - sum(rs.values())
        adv = {s: (rs[s] * f_num + f_den // 2) // f_den for s in leaf}
        adv_total = (r * f_num + f_den // 2) // f_den
        adv["GOV"] += adv_total - sum(adv.values())
        for s in leaf:
            lev.setdefault(("ADVREST", s), {})[q] = adv[s]
            lev.setdefault(("EMDE", s), {})[q] = rs[s] - adv[s]
    # net issues = change minus a residual that is zero except in the quarters the pins need
    oth = collections.defaultdict(int)
    oth[("ADVREST", "GOV", "2017-Q1")] = 1          # sum of ALL net issues 2015-Q1..2019-Q4 is the sum of changes minus 1
    oth[("US", "GOV", "2019-Q4")] = 1               # US net issues -14,447 against a change of -14,446
    oth[("ADVREST", "GOV", "2019-Q4")] = -1         # ALL 2019-Q4 net issues equal the change
    oth[("ADVREST", "GOV", "2026-Q2")] = 1          # ALL 2026-Q2 net issues 402,479 against a change of 402,480
    ids = {}

    def put(res, imm, meas, q, v):
        ids[(res, imm, meas, q)] = v
    sec_code = SECTOR_CODE
    for meas in ("I", "G"):
        for q in qs:
            tot = collections.defaultdict(int)
            grp_tot = collections.defaultdict(int)
            for (g, s), path in lev.items():
                if meas == "I":
                    v = path[q]
                else:
                    prev = path.get(qadd(q, -1))
                    v = (path[q] - prev - oth.get((g, s, q), 0)) if prev is not None else path[q] // 250
                res_list = {"US": ["US", "5R", "3P"], "ADVREST": ["5R", "3P"], "EMDE": ["4T", "3P"], "INTL_ORG": ["1C", "3P"]}[g]
                for res in res_list:
                    tot[(res, s)] += v
            for (res, s), v in tot.items():
                put(res, sec_code[s], meas, q, v)
            for res in ("US", "5R", "4T", "1C", "3P"):
                fin = sum(tot.get((res, p), 0) for p in FIN_PARTS if (res, p) in tot)
                if any((res, p) in tot for p in FIN_PARTS):
                    put(res, "B", meas, q, fin)
                allv = sum(tot.get((res, s), 0) for s in ("GOV", "NFC", "INTL_INST") if (res, s) in tot) + (fin if any((res, p) in tot for p in FIN_PARTS) else 0)
                put(res, "1", meas, q, allv)
    nat = fill_path(an, qs)
    natn = {q: (20_953 if q == FIRST_Q else nat[q] - nat[qadd(q, -1)]) for q in qs}
    nat_cells = {("I", q): nat[q] for q in qs}
    nat_cells.update({("G", q): natn[q] for q in qs})
    return ids, nat_cells


def pinned_lbs(lbs_last="2026-Q1"):
    qs = qrange(FIRST_Q, lbs_last)
    S = {("A", "5J"): fill_dec({"2013-Q4": D("9600000"), "2014-Q3": D("10443386.682"), "2014-Q4": D("9975340.668"), "2019-Q3": D("10726269.4"),
                                "2019-Q4": D("10883514.581"), lbs_last: D("12000000")}, qs),
         ("I", "5J"): fill_dec({"2013-Q4": D("3500000"), "2014-Q4": D("3632452.557"), "2019-Q4": D("4317263.445"), lbs_last: D("5000000")}, qs),
         ("A", "US"): fill_dec({"2013-Q4": D("2700000"), "2014-Q4": D("2748321.699"), "2019-Q4": D("2538435.28"), lbs_last: D("3000000")}, qs),
         ("I", "US"): fill_dec({"2013-Q4": D("1000000"), lbs_last: D("1200000")}, qs)}
    win = qrange("2015-Q1", "2019-Q4")
    F = {}
    a_win = split_milli(D("251396.545") - D("107732.184"), 19)
    F[("A", "5J")] = {q: D("1000.000") + D(i) for i, q in enumerate(qs[1:])}
    for q, v in zip(win[:-1], a_win):
        F[("A", "5J")][q] = v
    F[("A", "5J")]["2019-Q4"] = D("107732.184")
    F[("A", "5J")]["2014-Q4"] = D("-297934.906")
    for key, total in ((("I", "5J"), D("-11396.395")), (("A", "US"), D("-218442.274"))):
        F[key] = {q: D("500.000") for q in qs[1:]}
        for q, v in zip(win, split_milli(total, 20)):
            F[key][q] = v
    F[("I", "US")] = {q: D("250.000") for q in qs[1:]}
    flagged = {("A", "5J"): set(win), ("I", "5J"): set(win[:7]), ("A", "US"): set(win[3:12]), ("I", "US"): set()}
    return S, F, flagged, qs


def ids_csv(rows):
    return "\n".join([IDS_HEADER] + rows) + "\n"


def lbs_csv(rows):
    return "\n".join([LBS_HEADER] + rows) + "\n"


def f3_text(ids, drop=(), extra=()):
    rows = []
    for (res, imm, meas, q), v in sorted(ids.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2], qnum(kv[0][3]))):
        if (res, imm, meas, q) in drop:
            continue
        rows.append(IDS_ROW.format(res=res, nat="3P", imm=imm, meas=meas, q=q, v="" if v is None else v))
    return ids_csv(rows + list(extra))


def f4_text(nat):
    rows = [IDS_ROW.format(res="3P", nat="US", imm="1", meas=m, q=q, v=v) for (m, q), v in sorted(nat.items(), key=lambda kv: (kv[0][0], qnum(kv[0][1])))]
    return ids_csv(rows)


def f5_values(ids, d=57, nleaves=131, qs=None):
    """{(res, q): int} for F5 with 131 leaf codes (US, 1C, 1Z and 128 filler codes), summing to 3P minus d in every quarter."""
    out = {}
    qs = qs or sorted({q for (_, _, m, q) in ids}, key=qnum)
    fill = ["%s%s" % (a, b) for a in "ABCDEFGHJKLMNPQRSTUVWXYZ" for b in "0123456789"][:nleaves - 3]
    for q in qs:
        tot = ids[("3P", "1", "I", q)]
        us, c1 = ids[("US", "1", "I", q)], ids[("1C", "1", "I", q)]
        z = 321_211
        rest = tot - d - us - c1 - z
        base, rem = divmod(rest, len(fill))
        out[("3P", q)] = tot
        out[("US", q)], out[("1C", q)], out[("1Z", q)] = us, c1, z
        for i, code in enumerate(fill):
            out[(code, q)] = base + (1 if i < rem else 0)
        out[("5R", q)], out[("4T", q)] = ids[("5R", "1", "I", q)], ids[("4T", "1", "I", q)]
        out[("3C", q)] = 1_000
    return out


def f5_text(allres):
    rows = [IDS_ROW.format(res=res, nat="3P", imm="1", meas="I", q=q, v=v) for (res, q), v in sorted(allres.items(), key=lambda kv: (kv[0][0], qnum(kv[0][1])))]
    return ids_csv(rows)


def f6_text(S, F, flagged, qs):
    rows = []
    for (sec, cty), path in S.items():
        for q in qs:
            fl = q in flagged[(sec, cty)]
            pb = ""
            if fl:
                pb = "10834001.584" if (sec, cty, q) == ("A", "5J", "2019-Q4") else dstr(path[q] - D("10000"), 3)
            rows.append(LBS_ROW.format(m="S", sec=sec, cty=cty, q=q, v=dstr(path[q], 3), st="B" if fl else "A", pb=pb))
    for (sec, cty), path in F.items():
        for q, v in sorted(path.items(), key=lambda kv: qnum(kv[0])):
            rows.append(LBS_ROW.format(m="F", sec=sec, cty=cty, q=q, v=dstr(v, 3), st="A", pb=""))
    return lbs_csv(rows)


def synth_structure(which, overrides=None, drop_flow=False, swap_dims=False, flow_name=None):
    """A minimal SDMX-JSON structure message with the dataflow, the data structure and a code list per dimension."""
    overrides = overrides or {}
    dims = list(IDS_DIMS if which == "ids" else LBS_DIMS)
    sem, desc = (IDS_SEMANTIC, IDS_DESCRIPTIVE) if which == "ids" else (LBS_SEMANTIC, LBS_DESCRIPTIVE)
    labels = collections.defaultdict(dict)
    for dim, code, lab in sem + desc:
        labels[dim][code] = overrides.get((dim, code), lab)
    codelists = [{"id": "CL_" + d, "codes": [{"id": k, "name": v, "names": {"en": v}} for k, v in labels[d].items()]} for d in dims]
    if swap_dims:
        dims[1], dims[2] = dims[2], dims[1]
    flow, suffix, nm = (IDS_FLOW, IDS_STRUCT_SUFFIX, IDS_FLOW_NAME) if which == "ids" else (LBS_FLOW, LBS_STRUCT_SUFFIX, LBS_FLOW_NAME)
    doc = {"data": {"dataflows": [] if drop_flow else [{"id": flow, "name": flow_name or nm, "names": {"en": flow_name or nm},
                                                        "structure": "urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=" + suffix}],
                    "dataStructures": [{"id": suffix.split(":")[1].split("(")[0], "dataStructureComponents": {"dimensionList": {"dimensions": [
                        {"id": d, "position": i + 1, "localRepresentation": {"enumeration": "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:CL_%s(1.0)" % d}}
                        for i, d in enumerate(dims)]}}}],
                    "codelists": codelists}}
    return json.dumps(doc).encode("utf-8")


def pinned_files(date_unused=None, L="2026-Q2", tweak=None):
    """The six files of a synthetic pull whose pinned cells equal the spec's pins (so C01-C14 PASS on it). tweak(ids, nat, S, F, flagged) may edit the cells."""
    ids, nat = pinned_values(L)
    S, F, flagged, lq = pinned_lbs()
    if tweak:
        tweak(ids, nat, S, F, flagged)
    allres = f5_values(ids)
    return {"F1": synth_structure("ids"), "F2": synth_structure("lbs"), "F3": f3_text(ids).encode(), "F4": f4_text(nat).encode(), "F5": f5_text(allres).encode(),
            "F6": f6_text(S, F, flagged, lq).encode()}


_CACHE_FILES = {}


def cached_pinned_files():
    if "base" not in _CACHE_FILES:
        _CACHE_FILES["base"] = pinned_files()
    return _CACHE_FILES["base"]


def make_pull(date, files=None):
    return load_pull(date, files or cached_pinned_files())


def mini_pull(ids, latest="2014-Q2"):
    """A pull holding only the IDS cells given (G5-G7 fixtures); the rest of the pull is empty."""
    exists = {(r, i, m) for (r, i, m, q) in ids}
    return dict(date="2026-10-23", ids=dict(ids), exists=exists, nat={}, allres={}, lbs={}, soft=[], latest=latest)


def mini_ids(over=None, drop=()):
    """Three quarters of a tiny consistent world: US (no central bank, no international institutions), ADV and ALL."""
    base = {}
    us = {"2": (100, 1), "E": (200, 2), "I": (2, 0), "G": (300, 3), "K": (20, 1), "J": (400, 4)}
    allv = {"2": (1000, 10), "E": (2000, 20), "I": (300, 3), "G": (4000, 40), "K": (500, 5), "7": (9, 0), "J": (1700, 17), "S": (580, 6)}
    adv = {"2": (900, 9), "E": (1500, 15), "I": (250, 2), "G": (3500, 35), "K": (400, 4), "7": (9, 0), "J": (1500, 15), "S": (500, 5)}
    for q in ("2013-Q4", "2014-Q1", "2014-Q2"):
        for res, secs in (("US", us), ("3P", allv), ("5R", adv)):
            for imm, (i, g) in secs.items():
                base[(res, imm, "I", q)] = i
                base[(res, imm, "G", q)] = g
            fin = ("E", "I", "G", "K", "7")
            for k, mi in (("I", 0), ("G", 1)):
                base[(res, "B", k, q)] = sum(secs[x][mi] for x in fin if x in secs)
                base[(res, "1", k, q)] = base[(res, "B", k, q)] + sum(secs[x][mi] for x in secs if x not in fin)
    for q in ("2013-Q4", "2014-Q1", "2014-Q2"):
        for imm in list(allv) + ["B", "1"]:
            for k in ("I", "G"):
                base[("4T", imm, k, q)] = base[("3P", imm, k, q)] - base[("5R", imm, k, q)]
    base.update(over or {})
    for k in drop:
        base.pop(k, None)
    return base


def distinct_Q(L):
    """Q with a different value in every cell, for the shares and windows tests."""
    Q = {}
    for gi, g in enumerate(ALL_GROUPS):
        for si, s in enumerate(SECTORS):
            for q in qrange(FIRST_Q, L):
                n = 1_000_000 * (gi + 1) + 10_000 * si + qnum(q) - qnum(FIRST_Q) + 1
                Q[(g, s, q)] = dict(out=n, net=n // 10, chg=n // 10 + 1, oth=1, status="ok", derived="source", basis="residence")
    return Q


_WORLD = {}


def get_world():
    """The synthetic world, built once, with no mutant active (the guard functions are then mutated against its clean files)."""
    if not _WORLD:
        if _ACTIVE:
            raise RuntimeError("the synthetic world must be built before any mutant is switched on")
        pull = make_pull("2026-10-23")
        inp = dict(pulls=[pull], existing_revisions=[], existing_quarterly=[], fetch_rows=[], calendar_text=None, root=None)
        c0 = compute(inp)
        texts, failed = finish(c0)
        _WORLD.update(pull=pull, inp=inp, c0=c0, texts=texts, failed=failed, Q=c0["Q"], model=c0["model"])
    return _WORLD


def fake_rig(tmp, handler, clock=None, date="2026-10-23", **kw):
    clock = clock or FakeClock()
    calls = []

    def opener(host, target, headers, timeout, cap):
        calls.append((host, target, dict(headers), clock.wall()))
        return handler(host, target, headers)
    fe = Fetcher(os.path.join(tmp, "cache"), os.path.join(tmp, "out"), date, stop_path=os.path.join(tmp, "cache", "STOP"), opener=opener, wall=clock.wall,
                 mono=clock.wall, sleeper=clock.sleep, now_utc=lambda: dt.datetime(2026, 10, 23, 12, 0, tzinfo=dt.timezone.utc), **kw)
    return fe, calls, clock


def ok200(body):
    return lambda host, target, hdrs: (200, body, {})


def serve_files(files):
    """A handler that answers each of the six paths with the matching synthetic file."""
    by_path = {F_PATHS[k]: files[k] for k in files}
    return lambda host, target, hdrs: (200, by_path[target], {}) if target in by_path else (404, b"", {})


def fresh_Q(pull=None):
    """Quarter cells recomputed now, so that an active mutant acts on them."""
    pull = pull or get_world()["pull"]
    return quarter_cells(Model(pull), pull["nat"])


def row_text(**kw):
    cols = IDS_HEADER.split(",")
    base = IDS_ROW.format(res="3P", nat="3P", imm="1", meas="I", q="2019-Q4", v=11586704).split(",")
    for k, v in kw.items():
        base[cols.index(k)] = v
    return ",".join(base)


def t_g1(ck):
    b = built_targets()
    for k in ("F3", "F4", "F5"):
        ck.eq("the %s target built from the key rules equals the spec's URL" % k, b[k], F_PATHS[k])
    ck.eq("an IDS key has 15 dimensions", len(ids_key("3P", "3P", "1", "I").split(".")), 15)
    ck.eq("...and 12 for LBS (the F6 key)", len(F_PATHS["F6"].split("/1.0/")[1].split("?")[0].split(".")), 12)
    for k, p in F_PATHS.items():
        try:
            check_url("https://" + BIS_HOST + p)
            ok = True
        except Refused:
            ok = False
        ck.ok("%s passes the URL check" % k, ok)
    ck.eq("a good F3 row passes the content test", parse_ids_csv(ids_csv([row_text()]), "ids_main")[0], None)
    bad = {"ISSUER_RES and ISSUER_NAT swapped": row_text(ISSUER_RES="3P", ISSUER_NAT="US"),
           "MARKET A": row_text(MARKET="A"), "MARKET 1": row_text(MARKET="1"), "ISSUE_CUR_GROUP F": row_text(ISSUE_CUR_GROUP="F"),
           "ISSUER_BUS_ULT used as the sector": row_text(ISSUER_BUS_ULT="2"), "a sector outside the key": row_text(ISSUER_BUS_IMM="X"),
           "a 14-field row": ",".join(row_text().split(",")[:-1])}
    for name, r in bad.items():
        ck.ok("a row with %s is outside the requested key" % name, parse_ids_csv(ids_csv([r]), "ids_main")[0] is not None)


def t_g2(ck):
    hard, soft = struct_problems(json.loads(synth_structure("ids")), "ids")
    ck.eq("the allowlisted IDS labels give no problem", (hard, soft), ([], []))
    hard, soft = struct_problems(json.loads(synth_structure("lbs")), "lbs")
    ck.eq("the allowlisted LBS labels give no problem", (hard, soft), ([], []))
    hard, _ = struct_problems(json.loads(synth_structure("ids", {("MARKET", "C"): "Domestic market"})), "ids")
    ck.ok("MARKET C reading 'Domestic market' is a STOP", bool(hard))
    hard, _ = struct_problems(json.loads(synth_structure("ids", {("ISSUER_BUS_IMM", "B"): "Banks"})), "ids")
    ck.ok("ISSUER_BUS_IMM B reading 'Banks' is a STOP", bool(hard))
    hard, soft = struct_problems(json.loads(synth_structure("ids", {("ISSUE_TYPE", "A"): "Some issue types"})), "ids")
    ck.ok("a descriptive-label change is a WARN, not a STOP", not hard and bool(soft), "hard %r soft %r" % (hard, soft))
    hard, soft = struct_problems(json.loads(synth_structure("lbs", {("L_REP_BANK_TYPE", "A"): "Foreign banks"})), "lbs")
    ck.ok("...also for the LBS descriptive labels", not hard and bool(soft))
    ck.ok("a missing dataflow is a STOP", bool(body_problem("struct_ids", synth_structure("ids", drop_flow=True))))
    ck.ok("a changed dimension order is a STOP", bool(body_problem("struct_ids", synth_structure("ids", swap_dims=True))))
    ck.ok("a changed dataflow name is a STOP", bool(body_problem("struct_ids", synth_structure("ids", flow_name="Domestic debt"))))
    ck.ok("a body that is not JSON is a STOP", bool(body_problem("struct_ids", b"<html>")))
    ck.eq("the real-shaped structure passes", body_problem("struct_ids", synth_structure("ids")), None)


def t_g3(ck):
    ck.ok("UNIT_MULT 9 is a STOP", parse_ids_csv(ids_csv([row_text(UNIT_MULT="9")]), "ids_main")[0] is not None)
    ck.ok("OBS_CONF other than F is a STOP", parse_ids_csv(ids_csv([row_text(OBS_CONF="C")]), "ids_main")[0] is not None)
    ck.ok("UNIT_MEASURE other than USD is a STOP", parse_ids_csv(ids_csv([row_text(UNIT_MEASURE="EUR")]), "ids_main")[0] is not None)
    Q = fresh_Q()
    rows = quarterly_rows(Q, ["2019-Q4"], "v", "r")
    r = next(x for x in rows if x[2] == "ALL" and x[3] == "ALL")
    ck.eq("the 2019-Q4 ALL outstanding is written as published, in US$ millions", r[4], "11586704")
    ck.eq("README trillions are millions divided by 1,000,000, two decimals", tn(11586704), "11.59")
    ck.eq("README billions are millions divided by 1,000, one decimal", bn(11586704), "11,586.7")
    ck.eq("...rounding half up: 50 million is 0.1 billion, not 0.0", (bn(50), bn(250), bn(-50), bn(49)), ("0.1", "0.3", "-0.1", "0.0"))
    ck.eq("...and trillions likewise: 5,000 million is 0.01 trillion", (tn(5000), tn(25000), tn(4999)), ("0.01", "0.03", "0.00"))


def t_g4(ck):
    Q = fresh_Q()
    a, p = Q[("ALL", "ALL", "2019-Q4")], Q[("ALL", "ALL", "2019-Q3")]
    ck.eq("ALL net issues 2019-Q4 keep their sign", a["net"], 147756)
    ck.eq("the change is this quarter minus the previous one", a["chg"], a["out"] - p["out"])
    ck.eq("...so ALL 2019-Q4 change is +147,756", a["chg"], 147756)
    ok, agree, n, gaps = c06_result(Q, "2026-Q2")
    ck.ok("C06 passes on the synthetic world", ok, "%d of %d" % (agree, n))

    def fx(opposite):
        Qs = {}
        for i, q in enumerate(qrange("2014-Q1", "2016-Q4")):
            big = i < 10
            net = 10_000 if big else 100
            chg = -net if (big and i < opposite) else net
            Qs[("ALL", "ALL", q)] = dict(net=net, chg=chg)
        return Qs
    ck.ok("signs opposite in 1 of 10 large quarters (90%) pass", c06_result(fx(1), "2016-Q4")[0])
    ck.ok("signs opposite in 3 of 10 large quarters (70%) fail", not c06_result(fx(3), "2016-Q4")[0])
    ck.ok("quarters under 5,000 are left out of the test", c06_result(fx(0), "2016-Q4")[2] == 10)


def t_g5(ck):
    m = Model(mini_pull(mini_ids()))
    ck.eq("NON_US = ALL - US where both exist", m.cell("NON_US", "GOV", "outstanding", "2014-Q1"), (900, "ok"))
    m = Model(mini_pull(mini_ids(drop=[("5R", "2", "I", "2014-Q2")])))
    ck.eq("an absent source cell is blank, never zero", m.cell("ADV", "GOV", "outstanding", "2014-Q2"), (None, "absent"))
    m = Model(mini_pull(mini_ids(drop=[("US", "2", "I", "2014-Q1")])))
    ck.eq("NON_US is blank when the US series exists but that quarter is absent (partial)", m.cell("NON_US", "GOV", "outstanding", "2014-Q1"), (None, "partial"))
    m = Model(mini_pull(mini_ids(over={("US", "1", "I", "2014-Q2"): 1062})))
    ck.ok("C05b fails when US ALL differs from GOV + FIN + NFC by 40", not m.c05b("2014-Q2")[0])
    ck.eq("...and NON_US FIN_CENTRAL_BANK is blank with us_sum_mismatch", m.cell("NON_US", "FIN_CENTRAL_BANK", "outstanding", "2014-Q2"), (None, "us_sum_mismatch"))
    ck.eq("...and so is NON_US INTL_INST", m.cell("NON_US", "INTL_INST", "outstanding", "2014-Q2"), (None, "us_sum_mismatch"))
    ck.eq("a US ALL gap in outstanding does not blank the net-issue cells: C05b is per measure", m.cell("NON_US", "FIN_CENTRAL_BANK", "net_issues", "2014-Q2"), (0, "us_series_absent"))
    m = Model(mini_pull(mini_ids(drop=[("US", "2", "G", "2014-Q2")])))
    ck.ok("an absent US GOV net-issue value fails C05b for net issues only", m.c05b_m("2014-Q2", "net_issues")[:2] == (False, "absent") and m.c05b_m("2014-Q2", "outstanding")[0])
    ck.eq("...so NON_US FIN_CENTRAL_BANK net issues are blank with us_value_absent", m.cell("NON_US", "FIN_CENTRAL_BANK", "net_issues", "2014-Q2"), (None, "us_value_absent"))
    ck.eq("...and NON_US INTL_INST net issues likewise", m.cell("NON_US", "INTL_INST", "net_issues", "2014-Q2"), (None, "us_value_absent"))
    ck.eq("...while the outstanding cells of that quarter are filled", (m.cell("NON_US", "FIN_CENTRAL_BANK", "outstanding", "2014-Q2"), m.cell("NON_US", "INTL_INST", "outstanding", "2014-Q2")), ((9, "us_series_absent"), (580, "us_series_absent")))
    ck.eq("...and a US source value that exists elsewhere is partial for NON_US GOV net issues", m.cell("NON_US", "GOV", "net_issues", "2014-Q2"), (None, "partial"))
    ck.eq("a row with one filled and one us_value_absent measure has status us_value_absent", row_status("us_series_absent", "us_value_absent"), "us_value_absent")
    m = Model(mini_pull(mini_ids(over={("US", "1", "I", "2014-Q2"): 1062})))
    ck.eq("in a quarter where C05b passes, NON_US FIN_CENTRAL_BANK takes the US value as zero (us_series_absent)", m.cell("NON_US", "FIN_CENTRAL_BANK", "outstanding", "2014-Q1"), (9, "us_series_absent"))
    ck.eq("...and NON_US INTL_INST likewise", m.cell("NON_US", "INTL_INST", "outstanding", "2014-Q1"), (580, "us_series_absent"))
    over = {("US", "B", "I", "2014-Q2"): 520, ("US", "1", "I", "2014-Q2"): 1020}
    m = Model(mini_pull(mini_ids(over=over, drop=[("US", "I", "I", "2014-Q2")])))
    ck.ok("C05b passes with a published US FIN part absent, the FIN total having been adjusted", m.c05b("2014-Q2")[0])
    ck.eq("us_series_absent is not applied to a series that exists: NON_US FIN_PUB_BANK is partial", m.cell("NON_US", "FIN_PUB_BANK", "outstanding", "2014-Q2"), (None, "partial"))


def t_g6(ck):
    ck.eq("a gap of 5 passes", c05_status(5, 0), "PASS")
    ck.eq("a gap of 6 with no absent part is a FAIL", c05_status(6, 0), "FAIL")
    ck.eq("the same gap with an absent part is a WARN", c05_status(6, 1), "WARN")
    ck.eq("an absent whole is not checked", c05_status(None, 3), "PASS")
    m = Model(mini_pull(mini_ids()))
    st, gmax, nabs, notes = c05_quarter(m, "2014-Q1")
    ck.eq("the consistent mini world passes C05 (central bank inside FIN, INTL_INST once)", (st, gmax), ("PASS", 0))
    m = Model(mini_pull(mini_ids(over={("3P", "2", "I", "2014-Q1"): 1006, ("3P", "1", "I", "2014-Q1"): 10089})))
    ck.eq("a 6-unit sector gap with no absent part is a FAIL", c05_quarter(m, "2014-Q1")[0], "FAIL")
    m = Model(mini_pull(mini_ids(over={("3P", "2", "I", "2014-Q1"): 1006}, drop=[("3P", "J", "I", "2014-Q1")])))
    ck.ok("a gap above 5 with an absent part is a WARN, not a FAIL", c05_quarter(m, "2014-Q1")[0] == "WARN")


def alloc(q, d, us, c1, z, gb):
    """One F5 quarter: 3P = sum of leaves + d."""
    de = 1_000_000 - 57 - us - c1 - z - gb
    leaves = {"US": us, "1C": c1, "1Z": z, "GB": gb, "DE": de}
    out = {("3P", q): sum(leaves.values()) + d}
    out.update({(k, q): v for k, v in leaves.items()})
    out.update({("5R", q): 700_000, ("4T", q): 250_000, ("3C", q): 1_000, ("4Y", q): 100, ("4W", q): 100, ("4U", q): 100})
    return out


def t_g7(ck):
    m = Model(mini_pull(mini_ids()))
    ck.eq("NON_US = ALL - US", m.cell("NON_US", "ALL", "outstanding", "2014-Q1"), (9067, "ok"))
    ck.eq("...not ADV - US and not ALL", m.cell("NON_US", "ALL", "outstanding", "2014-Q1")[0] not in (8559 - 1022, 10089), True)
    good = alloc("2019-Q4", 57, 100_000, 50_000, 30_000, 400_000)
    st, stop, worst, notes = c04_status(c04_rows(good))
    ck.eq("with 1C and 1Z as leaves a 3P that includes the US passes C04 (d = +57)", (st, stop, worst[4]), ("PASS", False, 57))
    excl = alloc("2019-Q4", -100_000, 100_000, 50_000, 30_000, 400_000)
    st, stop, _, _ = c04_status(c04_rows(excl))
    ck.eq("a 3P that excludes the US (d = -US) is a FAIL with STOP", (st, stop), ("FAIL", True))
    third = alloc("2019-Q4", -30_000, 100_000, 50_000, 30_000, 400_000)
    st, stop, _, _ = c04_status(c04_rows(third))
    ck.eq("d = -0.3 x US fails the 0.9 x US leg: FAIL with STOP", (st, stop), ("FAIL", True))
    half = alloc("2019-Q4", 5_000, 100_000, 50_000, 30_000, 400_000)
    st, stop, _, _ = c04_status(c04_rows(half))
    ck.eq("a gap of about 0.5% of 3P fails the 0.1% leg: WARN, no STOP", (st, stop), ("WARN", False))
    inside_ = alloc("2019-Q4", 900, 100_000, 50_000, 30_000, 400_000)
    ck.eq("a gap of 0.09% of 3P passes", c04_status(c04_rows(inside_))[:2], ("PASS", False))
    big = alloc("2019-Q4", 899_535, 100_000, 50_000, 30_000, 400_000)
    st, stop, _, _ = c04_status(c04_rows(big))
    ck.eq("a gap of +899,535 is a WARN and not a STOP", (st, stop), ("WARN", False))
    ck.eq("the F5 content test passes the +899,535 body", body_problem("ids_all", f5_text(big).encode()), None)
    ck.ok("...and refuses the body that looks like a 3P without the US", body_problem("ids_all", f5_text(excl).encode()) is not None)
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _ = fake_rig(tmp, ok200(f5_text(excl).encode()))
        req = [r for r in plan() if r["id"] == "F5"][0]
        ck.raises("fetching that body latches", Latched, lambda: fe.fetch_one(req))
        ck.ok("...and writes the STOP file", os.path.exists(os.path.join(tmp, "cache", "STOP")))


def t_g8(ck):
    Q = distinct_Q("2026-Q2")
    rows = window_rows(Q, "2026-Q2")
    w = {(r[0], r[3], r[4]): r for r in rows}
    r = w[("2024", "ALL", "ALL")]
    ck.eq("window 2024 holds 2024-Q1 to 2024-Q4, four quarters", (r[1], r[2], r[5]), ("2024-Q1", "2024-Q4", "4"))
    ck.eq("...and sums the four quarters' net issues", r[7], str(sum(Q[("ALL", "ALL", q)]["net"] for q in qrange("2024-Q1", "2024-Q4"))))
    r = w[("2026_to_2026-Q2", "ALL", "ALL")]
    ck.eq("the 2026 window runs to L, two quarters", (r[1], r[2], r[5]), ("2026-Q1", "2026-Q2", "2"))
    ck.eq("...with their sum", r[7], str(sum(Q[("ALL", "ALL", q)]["net"] for q in ("2026-Q1", "2026-Q2"))))
    r = w[("2024_to_2026-Q2", "ALL", "ALL")]
    ck.eq("the 2024-to-L window has ten quarters", r[5], "10")
    ck.ok("a share over a positive denominator is filled", w[("2024", "ALL", "GOV")][10] != "")
    Qn = {k: dict(v) for k, v in Q.items()}
    for q in qrange("2024-Q1", "2024-Q4"):
        Qn[("ALL", "ALL", q)]["net"] = -100
    ck.eq("a share over a negative denominator is blank", {(r[0], r[3], r[4]): r for r in window_rows(Qn, "2026-Q2")}[("2024", "ALL", "GOV")][10], "")
    for q in qrange("2024-Q1", "2024-Q4"):
        Qn[("ALL", "ALL", q)]["net"] = 0
    ck.eq("...and over a zero denominator", {(r[0], r[3], r[4]): r for r in window_rows(Qn, "2026-Q2")}[("2024", "ALL", "GOV")][10], "")
    Qb = {k: dict(v) for k, v in Q.items()}
    Qb[("ALL", "GOV", "2024-Q2")]["net"] = None
    rb = {(r[0], r[3], r[4]): r for r in window_rows(Qb, "2026-Q2")}[("2024", "ALL", "GOV")]
    ck.ok("a window with a blank quarter has a blank sum and quarters_blank above zero", rb[7] == "" and rb[6] == "1")


def t_g9(ck):
    Q = distinct_Q("2019-Q2")
    rows = {(r[0], r[1], r[2]): r for r in share_rows(Q, qrange(FIRST_Q, "2019-Q2"))}
    r = rows[("2019-Q2", "NON_US", "GOV")]
    ck.eq("NON_US GOV: numerator is NON_US GOV in the same quarter", r[4], str(Q[("NON_US", "GOV", "2019-Q2")]["out"]))
    ck.eq("...and the denominator is NON_US's own ALL-sector total, not ALL's", r[5], str(Q[("NON_US", "ALL", "2019-Q2")]["out"]))
    r = rows[("2019-Q2", "ALL", "FIN_PRIV_BANK")]
    ck.eq("a FIN part is divided by the group's ALL-sector total, not by FIN", r[5], str(Q[("ALL", "ALL", "2019-Q2")]["out"]))
    ck.eq("the denominator label names the group", r[6], denominator_label("ALL"))
    ck.eq("the share is the ratio to two decimals", r[3], dstr(pct2(Q[("ALL", "FIN_PRIV_BANK", "2019-Q2")]["out"], Q[("ALL", "ALL", "2019-Q2")]["out"]), 2))
    ck.eq("shares start in 2019-Q1", min(k[0] for k in rows), "2019-Q1")


def t_g10(ck):
    W = get_world()
    Q, pull = fresh_Q(), W["pull"]
    cg = cgfs_rows(pull, Q)
    r1, r2, r3, r4, n1 = cg
    ck.eq("P1 runs 2014-Q4 to 2019-Q4", (r1["first"], r1["last"]), ("2014-Q4", "2019-Q4"))
    ck.eq("P1 securities increase is ALL 2019-Q4 minus 2014-Q4", r1["ids_change"], 2808426)
    ck.eq("P1 keeps related offices: the loan increase is the all-sector stock change", r1["lbs_change"], D("908173.913"))
    ck.eq("P1 share is the increase over the sum of both increases", r1["share"], D("75.56"))
    ck.eq("P2 share", r2["share"], D("91.78"))
    ck.eq("the break sum is the stock change minus the adjusted flows", r1["brk"], D("656777.368"))
    ck.eq("P1 break quarters: all 20", r1["bq"], 20)
    ck.ok("N1 carries its label", "not the paper's measure" in n1["plain"])
    ck.eq("P1 and P2 read the same; on the pinned numbers that is mixed", (r1["reading"], r2["reading"]), ("mixed", "mixed"))
    ck.eq("P3, P4 and N1 are described, with no reading", (r3["reading"], r4["reading"], n1["reading"]), ("described",) * 3)
    ck.ok("the P1 row carries the disclosure note, with the old rule's reading", r1["note"] == DISCLOSURE_PREFIX + "consistent.", r1["note"])
    ck.eq("the reading rule: inside and outside is mixed", reading_of(D("75.56"), D("91.78")), "mixed")
    ck.eq("...both inside is consistent", reading_of(D("75"), D("80")), "consistent")
    ck.eq("...both outside is not_consistent", reading_of(D("91"), D("92")), "not_consistent")
    ck.eq("...a blank share is undefined", reading_of(None, D("80")), "undefined")
    ck.eq("...outside then inside is mixed too", reading_of(D("91"), D("80")), "mixed")
    ck.ok("the band is 65 to 85, ends included", inside(D("65")) and inside(D("85")) and not inside(D("62")) and not inside(D("85.01")))
    c = dict(W["c0"], cgfs=cg)
    rd = render_readme(c)
    ck.ok("with P1 inside the band the README prints the P1-P4 table with break sums and break quarters", "Break sum, US$ bn" in rd and "| P4 |" in rd and "Break quarters" in rd)
    ck.ok("...and the R2-2 sentence with its numbers generated (657bn of 908bn, 91–93%)", "(657bn of 908bn here)" in rd and "the share is 91–93%, outside the band." in rd)
    ck.ok("...and says N1 is not the paper's measure", "N1 is not the paper's measure" in rd)
    ck.ok("...and that the earlier rule would have read consistent", "would have read consistent" in rd)


def t_g11(ck):
    ck.eq("the allowlists equal the typed canonical text and its sha256", allow_problems(), [])
    ck.eq("the sha256 is the spec's", sha256_of(SPEC_ALLOW_TEXT.encode()), "c84601784c545b2722847ad58803ba906564f8325fabd580c7fb0d2ce86735af")
    ck.ok("the constant hash is accepted", hash_accepted(SPEC_ALLOW_SHA256))
    ck.ok("the superseded round-1 hash (4a156e71...a03f9) is not accepted", not hash_accepted(ROUND1_HASH_HEAD + "0" * 51 + ROUND1_HASH_TAIL))
    spec = "# spec\n\n```\n" + SPEC_ALLOW_TEXT + "```\n"
    ck.eq("a spec whose fenced block is the canonical text passes", spec_block_problems(spec), [])
    ck.ok("a spec whose fenced block differs is reported", bool(spec_block_problems(spec.replace("net_issues_usd_m", "net_issues"))))
    real = os.path.join(ROOT, "_research", "2026-10-23-BIS-IDS-Dollar-Spec.md")
    if os.path.exists(real):
        with open(real, encoding="utf-8") as fh:
            ck.eq("the committed spec's fenced block hashes to SPEC_ALLOW_SHA256", spec_block_problems(fh.read()), [])
    h = ALLOW["quarterly.csv"]
    ck.raises("an extra column is refused", DataError, lambda: check_header("quarterly.csv", h + ["extra"]))
    ck.raises("a renamed column is refused", DataError, lambda: check_header("quarterly.csv", h[:-1] + ["vintage_x"]))
    ck.raises("a missing column is refused", DataError, lambda: check_header("quarterly.csv", h[:-1]))
    files = dict(get_world()["texts"])
    ck.eq("the clean folder has no folder problem (the # source: line is not compared as a header)", leak_problems(files), [])
    files["twelfth.txt"] = "x"
    ck.ok("a 12th file is reported", any("twelfth.txt" in p for p in leak_problems(files)))


WORDING_PLANTS = ["caused", "cause", "causes", "causing", "drove", "drive", "drives", "driven", "driving", "leaned against", "lean against",
                  "because of the intervention", "because of intervention", "led to", "prompted", "pushed", "in response to", "because of", "fuelled", "fueled"]


def t_g12(ck):
    for w in WORDING_PLANTS:
        ck.ok("'%s' planted in a README fixture is found" % w, bool(wording_problems("README.md", "The table shows that issuance %s the rise." % w)))
    for w in ("because", "causal", "driver", "ledger"):
        ck.ok("'%s' is not a false alarm" % w, not wording_problems("README.md", "A %s sentence." % w))
    ck.ok("'funding to non-US residents' applied to P1 is found", bool(wording_problems("README.md", "P1 measures funding to non-US residents.")))
    ck.ok("...also applied to P4 in a csv row", bool(wording_problems("cgfs_check.csv", "P4,dollar funding to non-U.S. residents,x")))
    ck.ok("the phrase on a line without P1-P4 is not flagged here", not wording_problems("README.md", "A sentence about funding to non-US residents in general."))
    ck.ok("the two opening sentences pass the guard", not wording_problems("README.md", REQUIRED_S1 + " " + REQUIRED_S2))
    ck.ok("...and the overlap sentence", not wording_problems("README.md", OVERLAP_SENTENCE))
    c = get_world()["c0"]
    ck.ok("...and the R2-2 sentence", not wording_problems("README.md", r22_sentence(c["cgfs"])))
    rd = render_readme(c)
    ck.eq("the generated README passes the wording guard", wording_problems("README.md", rd), [])
    ck.ok("the README opens with sentence 1 and sentence 2 exactly", REQUIRED_S1 + " " + REQUIRED_S2 in rd)
    ck.ok("...and carries the overlap sentence", OVERLAP_SENTENCE in rd)
    ck.ok("...and never says the table 'shows why' securities were issued", "shows why" not in rd)
    ck.ok("...and sentence 2 is the exact text", REQUIRED_S2 == "It measures amounts owed by issuers, not who holds the securities, and it does not show why the securities were issued or any effect on interest rates or the dollar.")
    for n, t in get_world()["texts"].items():
        ck.eq("%s passes the wording guard" % n, wording_problems(n, t), [])


def t_g13(ck):
    ck.raises("a non-allowlisted host (sec.gov) is refused before the request", Refused, lambda: check_url("https://www.sec.gov/x"))
    ck.raises("FRED is refused", Refused, lambda: check_url("https://fred.stlouisfed.org/x"))
    ck.raises("www.bis.org (the page that returned 403) is refused", Refused, lambda: check_url("https://www.bis.org/statistics/secstats.htm"))
    ck.raises("plain http is refused", Refused, lambda: check_url("http://stats.bis.org" + F_PATHS["F1"]))
    ck.raises("a stats.bis.org path outside the six is refused", Refused, lambda: check_url("https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/D.JP.JPY.A"))
    ck.raises("an address in the user agent is refused", Refused, lambda: assert_ua(UA.replace("research", "research; me" + chr(64) + "example.org")))
    ck.eq("the user agent is the CLAUDE.md string, with no address", (UA, chr(64) in UA), ("Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)", False))
    ck.raises("a POST is refused", Refused, lambda: check_method("POST"))
    with tempfile.TemporaryDirectory() as tmp:
        ck.raises("a pace under 2 s is refused", Refused, lambda: Fetcher(os.path.join(tmp, "c"), os.path.join(tmp, "o"), "2026-10-23", sleep=1.0))
        ck.raises("a ninth request per run cannot be configured", Refused, lambda: Fetcher(os.path.join(tmp, "c"), os.path.join(tmp, "o"), "2026-10-23", max_requests=9))
        fe, calls, clock = fake_rig(os.path.join(tmp, "a"), ok200(b"{}"))
        for _ in range(3):
            fe._get(F_PATHS["F1"])
        gaps = [calls[i + 1][3] - calls[i][3] for i in range(2)]
        ck.ok("requests start at least 2 s apart", all(g >= 2.0 for g in gaps), str(gaps))
        ck.ok("the request carries the neutral user agent and no address anywhere", calls[0][2]["User-Agent"] == UA and all(chr(64) not in str(v) for v in calls[0][2].values()))
        fe, calls, clock = fake_rig(os.path.join(tmp, "b"), ok200(b"{}"))
        for _ in range(8):
            fe._get(F_PATHS["F1"])
        ck.raises("the ninth request is refused", MaxRequests, lambda: fe._get(F_PATHS["F1"]))
        ck.eq("...and was not sent", len(calls), 8)
        fe, calls, _ = fake_rig(os.path.join(tmp, "c"), lambda h, t, hd: (429, b"slow down", {"retry-after": "30"}))
        ck.raises("a 429 latches", Latched, lambda: fe.fetch_one(plan()[0]))
        ck.eq("...and is not retried (one request)", len(calls), 1)
        fe, calls, _ = fake_rig(os.path.join(tmp, "d"), lambda h, t, hd: (301, b"", {"location": "https://elsewhere.example/"}))
        ck.raises("a redirect is not followed: it latches", Latched, lambda: fe.fetch_one(plan()[0]))
        ck.eq("...with one request", len(calls), 1)
        ck.ok("the opener only ever sends GET", 'conn.request("GET"' in open(os.path.abspath(__file__), encoding="utf-8").read())

        def hang(h, t, hd):
            raise SocketFault("TimeoutError")
        fe, calls, _ = fake_rig(os.path.join(tmp, "e"), hang)
        ck.raises("a timeout ends the invocation as a socket fault", SocketFault, lambda: fe.fetch_one(plan()[1]))
        ck.eq("...with one request, no retry", len(calls), 1)
        ck.ok("...logged as socket_fault, and no STOP file (a timeout has no status)", "socket_fault" in open(fe.log_path, encoding="utf-8").read() and
              not os.path.exists(os.path.join(tmp, "e", "cache", "STOP")))


def t_g14(ck):
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    ck.eq("static: no removal, rename, replace, move or truncating write is applied to a STOP path", static_stop_problems(src), [])
    plants = ["os.remove(STOP_PATH)", "os.unlink(self.stop_path)", "os.replace(tmp, stop_path)", "os.rename(a, STOP_PATH)", "shutil.rmtree(stop_dir)",
              "shutil.move(stop_path, other)", "stop_path.unlink()", "Path(stop).rename(other)", "open(STOP_PATH, 'w')", "os.replace(tmp, os.path.join(d, 'STOP'))"]
    for p in plants:
        ck.ok("static: a planted %r is flagged" % p, bool(static_stop_problems(src + "\n" + p + "\n")))
    ck.ok("static: a removal of an ordinary temporary file is not flagged", not static_stop_problems("import os\nos.remove(tmpfile)\n"))
    with tempfile.TemporaryDirectory() as tmp:
        sp = os.path.join(tmp, "cache", "STOP")
        os.makedirs(os.path.dirname(sp))
        with open(sp, "w") as fh:
            fh.write("status: 429\nutc_time: x\nurl_path: y\nretry_after: \nbody_head: z\n")
        before = sha256_of(open(sp, "rb").read())
        calls = []
        lines = []
        _CLOCK_OVERRIDE.append(dt.date(2026, 10, 23))
        try:
            a = argparse.Namespace(cache=os.path.join(tmp, "cache"), out=os.path.join(tmp, "out"), sleep=DEFAULT_SLEEP, max_requests=6)
            code = run_fetch(a, opener=lambda *x: calls.append(x) or (200, b"", {}), stop_path=sp, say=lambda *x: lines.append(" ".join(map(str, x))))
        finally:
            _CLOCK_OVERRIDE.pop()
        ck.eq("with a planted STOP, fetch exits 2", code, 2)
        ck.eq("...makes no request", len(calls), 0)
        ck.ok("...and prints 'STOP present:'", any(l.startswith("STOP present:") for l in lines), str(lines))
        ck.eq("...and leaves the STOP file byte-identical", sha256_of(open(sp, "rb").read()), before)
        fe, calls, _ = fake_rig(os.path.join(tmp, "x"), lambda h, t, hd: (503, b"Service Unavailable\r\n<html>", {"retry-after": "120"}))
        ck.raises("a fixture 503 latches", Latched, lambda: fe.fetch_one(plan()[0]))
        p = os.path.join(tmp, "x", "cache", "STOP")
        got = dict(l.split(": ", 1) for l in open(p, encoding="utf-8").read().splitlines()) if os.path.exists(p) else {}
        ck.eq("the STOP file carries the five fields", list(got), ["status", "utc_time", "url_path", "retry_after", "body_head"])
        ck.ok("...with the status, the Retry-After header, the path and the escaped body head", got.get("status") == "503" and got.get("retry_after") == "120" and
              got.get("url_path") == F_PATHS["F1"] and "Service Unavailable\\r\\n" in got.get("body_head", ""))
        fe2, calls2, _ = fake_rig(os.path.join(tmp, "x"), ok200(b"{}"))
        ck.raises("a second fetcher over the same cache refuses at once", Latched, lambda: fe2.fetch_one(plan()[1]))
        ck.eq("...with no request", len(calls2), 0)


def t_g15(ck):
    p_a = make_pull("2026-09-20")

    def bump(ids, nat, S, F, flagged):
        ids[("3P", "1", "I", "2025-Q4")] += 1_000_000       # a revised cell in the earlier quarters
    p_b = make_pull("2026-11-02", pinned_files(tweak=bump))
    cand = revision_candidates(p_a, p_b)
    ck.ok("revisions list the changed cell", any(r[2] == "2025-Q4" and r[5] == "ALL" and r[4] == "ALL" and r[6] == "outstanding" for r in cand), str(len(cand)))
    ck.ok("...and nothing for an unchanged quarter", not any(r[2] == "2019-Q4" for r in cand))
    existing = [["a", "b", "2019-Q1", "residence", "ALL", "ALL", "outstanding", "3", "4", "1", "33.33"], ["a", "b", "2020-Q1", "residence", "ALL", "ALL", "outstanding", "1", "2", "1", "100.00"]]
    merged = merge_revisions(existing, cand)
    ck.eq("existing rows keep their text and order", merged[:2], existing)
    ck.eq("new rows are appended", len(merged), 2 + len(cand))
    again = merge_revisions(merged, cand)
    ck.eq("a key already present is not written again", again, merged)
    first = merge_revisions([], [], first_pull_date="2026-09-20")
    ck.ok("the first pull writes one baseline row", len(first) == 1 and first[0][0] == "baseline" and first[0][1] == "2026-09-20", str(first))
    ck.eq("...and not on a second build of the same pull", merge_revisions(first, [], first_pull_date="2026-09-20"), first)
    inp = dict(pulls=[p_a, p_b], existing_revisions=[], existing_quarterly=[["2019-Q4", "residence", "ALL", "ALL", "5", "5", "", "", "ok", "source", "2000-01-01", ""]],
               fetch_rows=[], calendar_text=None, root=None)
    c = compute(inp)
    ck.ok("the previous vintage is the previous pull, not quarterly.csv", all(r[0] == "2026-09-20" and r[1] == "2026-11-02" for r in c["revisions"]) and bool(c["revisions"]),
          str(c["revisions"][:1]))
    c1 = compute(dict(inp, pulls=[p_a]))
    ck.ok("one pull gives one baseline row", len(c1["revisions"]) == 1 and c1["revisions"][0][0] == "baseline", str(c1["revisions"]))
    p_early = dict(p_a, date="2026-09-21", latest="2026-Q1")
    ck.ok("a pull whose latest quarter is earlier than the previous pull's is reported", pull_order_bad([p_a, p_early]))
    ck.ok("...and a later latest quarter is not", not pull_order_bad([p_early, p_a]))


def t_g16(ck):
    W = get_world()
    clean = dict(W["texts"])
    ck.eq("the clean folder passes", leak_problems(clean), [])
    f3 = cached_pinned_files()["F3"].decode()
    f1 = cached_pinned_files()["F1"].decode()
    f6 = cached_pinned_files()["F6"].decode()
    bad = dict(clean)
    bad["raw_f3.csv"] = f3
    bad["raw_f3_with_source.csv"] = "# source: BIS\n" + f3
    bad["structure.json"] = f1
    bad["raw_lbs.csv"] = f6
    bad["SOURCES.md"] = clean["SOURCES.md"] + "\nsee /Users/someone/file\n"
    bad["README.md"] = clean["README.md"] + "\ncontact me" + chr(64) + "example.org\n"
    bad["twelfth.txt"] = "hello"
    probs = leak_problems(bad)
    for n in ("raw_f3.csv", "raw_f3_with_source.csv", "raw_lbs.csv"):
        ck.ok("%s is reported as a raw SDMX file" % n, any(n in p and "raw SDMX" in p for p in probs), str(probs[:3]))
    ck.ok("a JSON structure file is reported as raw", any("structure.json" in p and "raw SDMX" in p for p in probs))
    ck.ok("a file containing /Users/ is reported", any("SOURCES.md" in p and "local path" in p for p in probs))
    ck.ok("an at sign is reported", any("README.md" in p and "at sign" in p for p in probs))
    ck.ok("a 12th name is reported", any("twelfth.txt" in p and "11 committed names" in p for p in probs))
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "data", "x"))
        os.makedirs(os.path.join(tmp, "data", "vintages", "bis_ids_dollar", "2026-10-23"))
        with open(os.path.join(tmp, "data", "x", "stray.csv"), "w") as fh:
            fh.write("# source: x\n" + f3)
        with open(os.path.join(tmp, "data", "vintages", "bis_ids_dollar", "2026-10-23", "f3.csv"), "w") as fh:
            fh.write(f3)
        with open(os.path.join(tmp, "data", "x", "fine.csv"), "w") as fh:
            fh.write("a,b\n1,2\n")
        with open(os.path.join(tmp, "data", "x", "stray.json"), "w") as fh:
            fh.write(f1)
        with open(os.path.join(tmp, "data", "x", "notes.md"), "w") as fh:
            fh.write('A note that names "dataStructures" in prose.\n')
        rp = repo_raw_problems(tmp, os.path.join(tmp, "data", "vintages", "bis_ids_dollar"))
        ck.ok("a raw file anywhere in the repository outside the cache is found (a csv with a source line in front, a JSON body)",
              len(rp) == 2 and any("stray.csv" in x for x in rp) and any("stray.json" in x for x in rp), str(rp))


def spec_frozen_text():
    real = os.path.join(ROOT, "_research", "2026-10-23-BIS-IDS-Dollar-Spec.md")
    if os.path.exists(real):
        with open(real, encoding="utf-8") as fh:
            return fh.read()
    return ("Window 2014-Q4 to 2019-Q4. With the band 65 ≤ share ≤ 85. REGISTERED = " + reg_literal(SPEC_FROZEN["registered"]) + " and F6 " + SPEC_FROZEN["lbs_path"])


def t_g17(ck):
    c0 = get_world()["c0"]
    ck.eq("the frozen rules equal the spec's text and the sources carry the R3-1 entry", frozen_problems(render_sources(c0), spec_frozen_text()), [])
    ck.eq("REGISTERED is the spec's tuple", REGISTERED, ("2026-10-23", "2019-Q4", "2026-Q1", ("ALL", "US"), "ALL", 1.0, 52))
    ck.eq("the window is 2014-Q4 to 2019-Q4 and the band 65 to 85", (CGFS_FIRST, CGFS_LAST, BAND_LO, BAND_HI), ("2014-Q4", "2019-Q4", 65, 85))
    ck.eq("the registered statement counts 52 cells (2 groups x 26 quarters)", len(qrange("2019-Q4", "2026-Q1")) * 2, 52)
    row = "2026-12-07\tBIS IDS 2026-Q3 release (no later than) ... changes by more than 1.0% ... 52 cells ... sector ALL ... PENDING"
    ck.eq("a CALENDAR row with the three phrases passes C09", calendar_check(row)[1], "PASS")
    ck.eq("...one with 51 cells fails", calendar_check(row.replace("52 cells", "51 cells"))[1], "FAIL")
    ck.eq("...one with 1.5% fails", calendar_check(row.replace("more than 1.0%", "more than 1.5%"))[1], "FAIL")
    ck.eq("...one for another sector fails", calendar_check(row.replace("sector ALL", "sector FIN"))[1], "FAIL")
    ck.eq("...and no row is INFO", calendar_check("2026-11-12\tsomething else")[1], "INFO")
    s = render_sources(c0)
    ck.ok("the R3-1 entry holds the old rule, the new rule, P1 75.56, P2 91.78 and that the old rule would have printed consistent",
          R3_1_MARKER in s and "75.56" in s and "91.78" in s and "would have printed `consistent`" in s)
    ck.ok("...and sits first in Build decisions", s.split("## Build decisions\n", 1)[1].lstrip().startswith("1. **" + R3_1_MARKER))
    changed = dict(frozen_current(), band=(60, 90))
    ck.ok("a changed band with no Build decisions entry is reported", any("band" in p for p in frozen_problems(s, None, changed)))
    s2 = s.replace("## Build decisions\n", "## Build decisions\nchanged rule: band was 65-85, now 60-90 (date, reason, real data seen: yes)\n")
    ck.ok("...and accepted once an entry holds the old value", not any("band" in p for p in frozen_problems(s2, None, changed)))


def t_g18(ck):
    ck.eq("a Q5 row is blind = no", blind_of("Q5", "ALL", ["2020-Q1"]), "no")
    ck.eq("...also for NON_US", blind_of("Q5", "NON_US", ["2020-Q1"]), "no")
    ck.eq("a Q1 row using 2019-Q4 ALL is blind = no", blind_of("Q1", "ALL", ["2019-Q4"]), "no")
    ck.eq("ALL at 2014-Q3 is blind = no", blind_of("Q2", "ALL", ["2014-Q3"]), "no")
    ck.eq("US at 2026-Q2 is blind = no", blind_of("Q1", "US", ["2026-Q2"]), "no")
    ck.eq("ALL over 2024 only is blind = yes", blind_of("Q2", "ALL", qrange("2024-Q1", "2024-Q4")), "yes")
    ck.eq("ADV at 2019-Q4 is blind = yes (the rule names ALL, US and NON_US)", blind_of("Q1", "ADV", ["2019-Q4"]), "yes")
    ck.eq("US_NATIONALITY at 2019-Q4 is blind = no", blind_of("Q1", "US_NATIONALITY", ["2019-Q4"]), "no")
    ck.eq("US_NATIONALITY at 2026-Q2 is blind = yes", blind_of("Q1", "US_NATIONALITY", ["2026-Q2"]), "yes")
    rows = summary_rows(get_world()["c0"])
    ck.eq("summary.csv holds a row for every question Q1 to Q6", sorted({r[0] for r in rows}), ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"])
    ck.ok("every Q5 row is blind = no", all(r[7] == "no" for r in rows if r[0] == "Q5"))
    ck.ok("the Q1 ALL 2019-Q4 row is blind = no", all(r[7] == "no" for r in rows if r[0] == "Q1" and r[2] == "ALL" and r[4] == "outstanding_2019-Q4"))
    ck.ok("no difference row is committed in Q4", not any("differ" in r[4] for r in rows if r[0] == "Q4"))


def t_g19(ck):
    _CLOCK_OVERRIDE.append(dt.date(2027, 1, 1))
    try:
        p = make_pull("2026-09-20")
        inp = dict(pulls=[p], existing_revisions=[], existing_quarterly=[], fetch_rows=[], calendar_text=None, root=None)
        c = compute(inp)
        texts = render_texts(c)
    finally:
        _CLOCK_OVERRIDE.pop()
    ck.eq("every row's vintage is the pull-folder date, not the clock", {r[10] for r in c["quarterly"]}, {"2026-09-20"})
    ck.eq("...and ids_release is the 14 Sep release", {r[11] for r in c["quarterly"]}, {"2026-09-14"})
    ck.ok("no text holds a date from the clock (2027)", not any("2027" in t for t in texts.values()))
    ck.ok("the registration row carries pull-folder dates only", c["score"][2] == "2026-09-20" and c["score"][3] == "2026-09-20" and c["score"][1] == "")
    ck.ok("the README and SOURCES name the pull-folder date", "2026-09-20" in texts["README.md"] and "2026-09-20" in texts["SOURCES.md"])


def reg_pull(date, latest, scale=None):
    """A bare pull with ALL and US sector-ALL outstanding for 2019-Q4 to `latest`, for the registration tests; scale = {(res, q): factor}."""
    ids = {}
    for res, base in (("3P", 11_000_000), ("US", 1_400_000)):
        for i, q in enumerate(qrange("2019-Q4", latest)):
            v = base + 10_000 * i
            f = (scale or {}).get((res, q))
            ids[(res, "1", "I", q)] = int(v * f) if f else v
    return dict(date=date, ids=ids, latest=latest)


def t_g20(ck):
    ck.eq("the release on or before 2026-09-20 is the 14 Sep release of 2026-Q2", release_pair("2026-09-20"), ("2026-09-14", "2026-Q2"))
    ck.eq("...and on 2026-12-07 it is the 7 Dec release of 2026-Q3", release_pair("2026-12-07"), ("2026-12-07", "2026-Q3"))
    ck.eq("before the first release there is none", release_pair("2020-01-01"), ("", ""))
    ck.eq("the latest quarter of the pinned world matches its release's quarter (C17)", release_pair("2026-10-23")[1], get_world()["pull"]["latest"])
    base = reg_pull("2026-09-20", "2026-Q2")
    dec = reg_pull("2026-12-07", "2026-Q2")
    r = registration_row([base, dec])
    ck.ok("a pull dated 2026-12-07 whose latest quarter is 2026-Q2 is PENDING, not HELD", r[9] == "PENDING", str(r))
    ck.ok("...with the baseline and newest pull named", r[2] == "2026-09-20" and r[3] == "2026-12-07" and r[1] == "")
    q3 = reg_pull("2026-12-08", "2026-Q3")
    r = registration_row([base, q3])
    ck.ok("with 2026-Q3 in the file and no cell moving, the result is HELD", r[9] == "HELD" and r[5] == "52" and r[1] == "2026-12-08", str(r))
    q3b = reg_pull("2026-12-08", "2026-Q3", {("US", "2024-Q1"): 1.02})
    r = registration_row([base, q3b])
    ck.ok("a cell changed by 2% is FALSIFIED", r[9] == "FALSIFIED" and "US ALL 2024-Q1" in r[7], str(r))
    mid = reg_pull("2026-11-02", "2026-Q2", {("3P", "2020-Q1"): 1.05})
    r = registration_row([base, mid, q3])
    ck.ok("the score is against the 14 Sep baseline, not the previous pull", r[9] == "HELD" and r[2] == "2026-09-20", str(r))
    r = registration_row([reg_pull("2026-12-08", "2026-Q3")])
    ck.ok("with no pull of the 14 Sep release the result is VOID", r[9] == "VOID", str(r))
    r = registration_row([base])
    ck.ok("one baseline pull gives PENDING", r[9] == "PENDING" and r[6] == "" and r[3] == "2026-09-20", str(r))
    ck.eq("the registered statement is 52 cells at 1.0 percent", (registered()[5], registered()[6]), (1.0, 52))


def t_x_cache(ck):
    ck.raises("a cache inside the repository, not ignored by git, is refused", Refused, lambda: check_cache(os.path.join(ROOT, "data", "not_ignored_x")))
    ck.ok("the default cache is accepted (git ignores it)", check_cache(CACHE_DEFAULT) is not None)
    ck.raises("the committed output folder as a cache is refused", Refused, lambda: check_cache(os.path.join(OUT_DEFAULT, "cache")))


def t_x_build(ck):
    """An end-to-end build on the pinned synthetic pull: structure, determinism, the pins and the folder guards on real renderings."""
    W = get_world()
    c = compute(W["inp"])
    texts, failed = finish(c)
    chk = {r[0]: r for r in c["checks"]}
    ck.eq("no check FAILs on the pinned synthetic pull", failed, [])
    ck.eq("C13 (a second build leaves every sha256 unchanged) passes", chk["C13"][4], "PASS")
    ck.eq("C18 (folder guards on the real rendering) passes", chk["C18"][4], "PASS")
    for cid in ("C01", "C02", "C03", "C04", "C04b", "C04c", "C06", "C06b", "C07", "C08", "C10", "C11", "C12", "C14/P1", "C14/P2", "C14/P3", "C14/P4", "C14/N1", "C15", "C16", "C17"):
        ck.eq("%s passes on the pinned synthetic pull" % cid, chk[cid][4], "PASS")
    ck.eq("C09 is INFO with no CALENDAR row", chk["C09"][4], "INFO")
    ck.ok("C05 and C05b have one row per quarter", len([k for k in chk if k.startswith("C05/")]) == len(qrange(FIRST_Q, "2026-Q2")) == len([k for k in chk if k.startswith("C05b/")]))
    ck.eq("eleven names", sorted(texts), sorted(COMMITTED))
    ck.ok("every committed csv begins with one # source: line", all(t.startswith("# source:") and t.count("\n# source:") == 0 for n, t in texts.items() if n.endswith(".csv")))
    ck.ok("the quarterly.csv source line cites the BIS and the pull date", texts["quarterly.csv"].startswith("# source: " + SOURCE_LINE_ID + ", retrieved 2026-10-23\n"))
    ck.ok("the cgfs_check.csv source line also cites the locational banking statistics", texts["cgfs_check.csv"].startswith("# source: " + SOURCE_LINE_ID + SOURCE_LINE_LBS))
    for n in ALLOW_ORDER:
        ck.eq("%s has the canonical header" % n, csv_body(texts[n])[0], ALLOW[n])
    rd = texts["README.md"]
    ck.ok("the build decisions are a section of SOURCES.md and not of the README", "## Build decisions" in texts["SOURCES.md"] and "Build decisions" not in rd.split("## Provenance")[0])
    ck.ok("the README ends with the provenance paragraph", rd.rstrip().split("\n")[-1].startswith("Source: Bank for International Settlements") and "## Provenance" in rd)
    ck.ok("...which says the BIS terms apply, no warranty, not investment advice, not endorsed", all(s in rd for s in ("BIS terms of use apply", "no warranty", "not investment advice", "does not endorse")))
    ck.ok("SOURCES.md links the terms and quotes under 15 words", BIS_LEGAL_URL in texts["SOURCES.md"] and len(BIS_QUOTE.split()) < 15)
    ck.ok("the worked row is in the README", "1,187,905 + 8,116,957 + 1,700,325 + 581,517 = 11,586,704" in rd)
    ck.eq("the registration is PENDING on a 2026-Q2 pull", csv_body(texts["registration_score.csv"])[1][0][9], "PENDING")
    ck.eq("the pinned world reads mixed", [r[13] for r in csv_body(texts["cgfs_check.csv"])[1]], ["mixed", "mixed", "described", "described", "described"])
    ck.eq("two renderings are byte-identical", texts_digest(render_texts(c)), texts_digest(texts))
    with tempfile.TemporaryDirectory() as tmp:
        write_outputs({"README.md": "x"}, tmp, ["C01"])
        ck.ok("a build with a FAIL row writes to _FAILED and leaves the committed folder alone", os.path.exists(os.path.join(tmp, "_FAILED", "README.md")) and not os.path.exists(os.path.join(tmp, "README.md")))
        write_outputs({"README.md": "x"}, tmp, [])
        ck.ok("a clean build writes to the committed folder", os.path.exists(os.path.join(tmp, "README.md")))


def blank_run(tweak):
    pull = make_pull("2026-10-23", pinned_files(tweak=tweak))
    c = compute(dict(pulls=[pull], existing_revisions=[], existing_quarterly=[], fetch_rows=[], calendar_text=None, root=None))
    texts, failed = finish(c)
    return c, texts, failed, {r[0]: r for r in c["checks"]}


def t_x_blanks(ck):
    """Cells the BIS does not publish are blank all the way through to the README (no crash, no zero)."""
    def t1(ids, nat, S, F, fl):
        for m in "IG":
            ids.pop(("5R", "S", m, "2013-Q4"))
            ids.pop(("4T", "S", m, "2013-Q4"))

    def t3(ids, nat, S, F, fl):
        F[("A", "5J")].pop("2017-Q2")

    def t5(ids, nat, S, F, fl):
        ids[("3P", "1", "G", "2026-Q2")] = None
        nat.pop(("I", "2026-Q2"))
    c, texts, failed, chk = blank_run(t1)
    q = {(r[0], r[2], r[3]): r for r in csv_body(texts["quarterly.csv"])[1]}
    ck.eq("ADV and EMDE INTL_INST absent in the first quarter: C05 is a WARN, not a FAIL", (chk["C05/2013-Q4"][4], failed), ("WARN", []))
    ck.ok("...and the rows for the later quarters are untouched", q[("2014-Q3", "ADV", "INTL_INST")][8] == "ok")
    c, texts, failed, chk = blank_run(t3)
    r = {x[0]: x for x in csv_body(texts["cgfs_check.csv"])[1]}
    ck.eq("a missing break-adjusted flow blanks the flow sum and break sum of every variant that uses it", (r["P1"][8], r["P1"][9], r["P2"][11], r["P2"][13]), ("", "", "", "undefined"))
    ck.ok("...P1 keeps its share and the README still prints the R2-2 sentence with a stated fallback", r["P1"][11] == "75.56" and "blank on this vintage" in texts["README.md"])
    ck.ok("...and the pins that need the flow FAIL rather than pass", chk["C14/P1"][4] == "FAIL" and chk["C14/P2"][4] == "FAIL")
    def t6(ids, nat, S, F, fl):
        ids.pop(("US", "2", "G", "2026-Q2"))
    c, texts, failed, chk = blank_run(t6)
    q = {(r[0], r[2], r[3]): r for r in csv_body(texts["quarterly.csv"])[1]}
    r = q[("2026-Q2", "NON_US", "FIN_CENTRAL_BANK")]
    ck.ok("an absent US GOV net-issue value: NON_US central-bank outstanding is filled, net issues blank, status us_value_absent", r[4] != "" and r[5] == "" and r[8] == "us_value_absent", str(r))
    ck.ok("...the README names the quarter and the missing value", "In 2026-Q2 the US government net-issue value is absent, so the NON_US net-issue cells of FIN_CENTRAL_BANK and INTL_INST are blank with `us_value_absent`, while their outstanding cells are filled." in texts["README.md"])
    ck.ok("...and a vintage without such a gap carries no such sentence", "is absent, so the NON_US" not in get_world()["texts"]["README.md"])
    c, texts, failed, chk = blank_run(t5)
    q = {(r[0], r[2], r[3]): r for r in csv_body(texts["quarterly.csv"])[1]}
    row = q[("2026-Q2", "ALL", "ALL")]
    ck.ok("a blank ALL net-issues cell stays blank (never zero) with status partial", row[5] == "" and row[7] == "" and row[8] == "partial", str(row))
    ck.ok("...the NON_US net issues cell is blank too, and the nationality row is partial", q[("2026-Q2", "NON_US", "ALL")][5] == "" and q[("2026-Q2", "US_NATIONALITY", "ALL")][8] == "partial")
    w = {(r[0], r[3], r[4]): r for r in csv_body(texts["net_issues_windows.csv"])[1]}
    ck.ok("...so the windows that contain it are blank with quarters_blank above zero", w[("2026_to_2026-Q2", "ALL", "ALL")][7] == "" and int(w[("2026_to_2026-Q2", "ALL", "ALL")][6]) > 0)
    ck.eq("the summary still holds every question", sorted({r[0] for r in csv_body(texts["summary.csv"])[1]}), ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"])


def t_x_vintages(ck):
    """Two pulls: the baseline of 23 Oct and a later pull that holds 2026-Q3. Revisions are appended, the registration is scored, one-vintage pins turn to WARN."""
    pa = make_pull("2026-10-23")

    def small(ids, nat, S, F, fl):
        ids[("3P", "1", "I", "2024-Q1")] += 10_000
        ids[("3P", "1", "I", "2019-Q4")] += 1

    def large(ids, nat, S, F, fl):
        ids[("3P", "1", "I", "2024-Q1")] += 200_000
    existing = [["baseline", "2026-10-23", "", "", "", "", "", "", "", "", ""]]
    base = dict(existing_revisions=existing, existing_quarterly=[], fetch_rows=[], calendar_text=None, root=None)
    pb = load_pull("2026-12-08", pinned_files(L="2026-Q3", tweak=small))
    c = compute(dict(base, pulls=[pa, pb]))
    chk = {r[0]: r for r in c["checks"]}
    ck.eq("the baseline row stays first and the new comparison is appended", (c["revisions"][0], c["revisions"][1][:2]), (existing[0], ["2026-10-23", "2026-12-08"]))
    ck.ok("...with the changed ALL cell (14.4 million up by 10,000) and its percentage", any(r[2] == "2024-Q1" and r[4] == "ALL" and r[5] == "ALL" and r[6] == "outstanding" and r[9] == "10000" for r in c["revisions"]))
    ck.eq("the registration is HELD when the 52 cells moved by at most 1.0 percent", (c["score"][9], c["score"][1], c["score"][5]), ("HELD", "2026-12-08", "52"))
    ck.eq("a pinned IDS value that changed is a WARN once 2026-Q3 is in the file", chk["C01"][4], "WARN")
    ck.eq("the vintage and the release come from the newest pull folder", (c["vintage"], c["release"]), ("2026-12-08", "2026-12-07"))
    ck.eq("the later pull is not an earlier-latest-quarter FAIL", chk["C16"][4], "PASS")
    pc = load_pull("2026-12-08", pinned_files(L="2026-Q3", tweak=large))
    c = compute(dict(base, pulls=[pa, pc]))
    ck.eq("a cell that moved by more than 1.0 percent is FALSIFIED, naming the cell", (c["score"][9], c["score"][7]), ("FALSIFIED", "ALL ALL 2024-Q1 outstanding"))
    pd_ = load_pull("2026-11-02", pinned_files(tweak=small))
    c = compute(dict(base, pulls=[pa, pd_]))
    chk = {r[0]: r for r in c["checks"]}
    ck.eq("a changed pinned value on a pull that still ends at 2026-Q2 is a FAIL", chk["C01"][4], "FAIL")
    ck.eq("...and the registration is still PENDING", c["score"][9], "PENDING")


def t_x_e2e(ck):
    """fetch (with a fake server) then build over the cache it wrote, in a temporary folder: the same files as the in-memory world."""
    files = cached_pinned_files()
    with tempfile.TemporaryDirectory() as tmp:
        calls, clock = [], FakeClock()
        handler = serve_files(files)

        def opener(h, t, hd, to, cap):
            calls.append((t, clock.wall()))
            return handler(h, t, hd)
        real_sleep = time.sleep
        a = argparse.Namespace(cache=os.path.join(tmp, "cache"), out=os.path.join(tmp, "out"), sleep=DEFAULT_SLEEP, max_requests=6)
        _CLOCK_OVERRIDE.append(dt.date(2026, 10, 23))
        fe_out = []
        try:
            fe = Fetcher(a.cache, a.out, "2026-10-23", stop_path=os.path.join(tmp, "cache", "STOP"), opener=opener, wall=clock.wall, mono=clock.wall, sleeper=clock.sleep)
            n = fe.run(plan(), say=lambda *x: fe_out.append(x))
            sync_committed_log(fe.cache, a.out)
        finally:
            _CLOCK_OVERRIDE.pop()
        ck.eq("fetch saves the six files", n, 6)
        ck.eq("...with six requests, the targets of the spec, in order", [t for t, _ in calls], [F_PATHS[k] for k in ("F1", "F2", "F3", "F4", "F5", "F6")])
        ck.ok("...at least 2 s apart", all(calls[i + 1][1] - calls[i][1] >= 2.0 for i in range(5)))
        ck.eq("...and the pull folder holds the six files and its log", sorted(os.listdir(os.path.join(tmp, "cache", "2026-10-23"))),
              sorted(list(F_FILES.values()) + ["fetch_log.csv"]))
        _, lr = read_csv_rows(os.path.join(tmp, "out", "fetch_log.csv"))
        ck.ok("the committed log has six rows, status 200, with the sha256 of each file", len(lr) == 6 and all(r[3] == "200" and r[1] == BIS_HOST for r in lr) and
              lr[2][5] == sha256_of(files["F3"]))
        ck.ok("a second fetch over the same pull folder makes no request (the pull is not repeated)", fe.run(plan(), say=lambda *x: None) == 0 and len(calls) == 6)
        inp = load_inputs(os.path.join(tmp, "cache"), os.path.join(tmp, "out"), root=tmp)
        c = compute(inp)
        texts, failed = finish(c)
        ck.eq("a build over that cache FAILs nothing", failed, [])
        ck.eq("...and writes the 11 names to the committed folder", (write_outputs(texts, os.path.join(tmp, "out"), failed) == os.path.join(tmp, "out"), sorted(f for f in os.listdir(os.path.join(tmp, "out")) if os.path.isfile(os.path.join(tmp, "out", f)))),
              (True, sorted(COMMITTED)))
        w = get_world()["texts"]
        same = {n: sha256_of(t.encode()) for n, t in texts.items() if n not in ("checks.csv", "fetch_log.csv")}
        ck.eq("...equal to the in-memory build of the same pull (fetch_log.csv aside)", same, {n: sha256_of(t.encode()) for n, t in w.items() if n not in ("checks.csv", "fetch_log.csv")})
        before = {n: sha256_of(open(os.path.join(tmp, "out", n), "rb").read()) for n in COMMITTED}
        inp2 = load_inputs(os.path.join(tmp, "cache"), os.path.join(tmp, "out"), root=tmp)
        t2, f2 = finish(compute(inp2))
        write_outputs(t2, os.path.join(tmp, "out"), f2)
        after = {n: sha256_of(open(os.path.join(tmp, "out", n), "rb").read()) for n in COMMITTED}
        ck.eq("a second build over the written folder leaves every sha256 unchanged, revisions.csv included", after, before)
        ck.ok("the committed revisions.csv holds one baseline row", csv_body(open(os.path.join(tmp, "out", "revisions.csv"), encoding="utf-8").read())[1][0][0] == "baseline")


GUARDS = [
    ("G1", "key (2.1, 2.3)", ["key_swap", "key_market_a", "key_curgroup_f", "key_ult_sector", "key_14dims"], t_g1),
    ("G2", "labels (2.2, R3a)", ["label_market_off", "label_b_off", "desc_hard"], t_g2),
    ("G3", "units (2.1, C07)", ["unit_mult_any", "values_div_1000", "tn_div_1000", "bn_half_even", "tn_half_even"], t_g3),
    ("G4", "sign (3.4, 3.10)", ["net_negated", "change_reversed", "c06_lenient"], t_g4),
    ("G5", "blanks and C05b (2.2, 3.3)", ["absent_zero", "non_us_partial_filled", "non_us_cb_filled_on_mismatch", "us_absent_misapplied", "c05b_loose", "value_absent_as_mismatch", "c05b_joint"], t_g5),
    ("G6", "identities (3.5)", ["fin_without_cb", "intl_inst_twice", "gap6_pass", "gap_absent_fail"], t_g6),
    ("G7", "NON_US and C04 (3.2)", ["non_us_adv_minus_us", "non_us_all", "leaf_alpha", "c04_no_stop", "c04_unsigned", "c04_leg1_loose", "c04_leg2_07"], t_g7),
    ("G8", "windows (3.7)", ["win_2023q4", "win_L_dropped", "share_nonpositive"], t_g8),
    ("G9", "shares (3.6)", ["share_nonus_all", "share_fin_part_over_fin", "share_quarter_mismatch"], t_g9),
    ("G10", "CGFS (3.8, 3.9, 5)", ["p1_window_2015q1", "p1_no_related", "share_ids_over_lbs", "reading_round1", "reading_differs", "reading_on_p3", "band_60_90",
                                   "break_flows_minus_stocks", "n1_unlabeled", "readme_no_table", "readme_no_r22", "note_missing"], t_g10),
    ("G11", "allowlists, folder (5, 6.1)", ["extra_column_ok", "renamed_column_ok", "allow_drift", "hash_wrong", "round1_hash_ok", "twelfth_ok", "source_as_header", "spec_drift"], t_g11),
    ("G12", "wording (R6, 6.3)", ["causal_off", "nonus_off", "s2_changed"], t_g12),
    ("G13", "fetch safety (R1-R3)", ["allow_other_host", "ua_check_off", "redirect_ok", "pacing_off", "retry_429", "cap_off", "post_ok"], t_g13),
    ("G14", "STOP latch: static scan and runtime", ["stop_ignored", "static_scan_off", "stop_short"], t_g14),
    ("G15", "revisions (2.4)", ["rev_rewrite", "rev_reorder", "rev_dup_key", "prev_from_quarterly", "no_baseline", "earlier_latest_ok"], t_g15),
    ("G16", "leak guard on a planted bad folder (6.1, 6.2)", ["leak_first_line_only", "leak_json_off", "leak_raw_off", "leak_path_off", "leak_name_off", "leak_at_off"], t_g16),
    ("G17", "frozen rules (R8, 7)", ["reg_threshold", "reg_cells", "reg_sector", "band_60_90", "window_changed", "lbs_key_changed", "reading_round1", "r31_entry_missing", "c09_loose"], t_g17),
    ("G18", "blind (4)", ["blind_q5_yes", "blind_q1_yes"], t_g18),
    ("G19", "dates from the pull folder (R5)", ["clock_vintage"], t_g19),
    ("G20", "calendar and scoring (2.4, 7)", ["release_from_dss", "score_by_calendar", "score_vs_other"], t_g20),
    ("X1", "cache path: outside the repo, or git-ignored inside it", ["cache_check_off"], t_x_cache),
    ("X2", "an end-to-end synthetic build on the pinned pull: pins, determinism, folder guards", ["render_unstable", "failed_to_committed"], t_x_build),
    ("X3", "fetch then build over the cache it wrote, in a temporary folder", [], t_x_e2e),
    ("X4", "blank cells all the way through to the README", [], t_x_blanks),
    ("X5", "two pulls: revisions appended, registration scored, pins WARN after 2026-Q3", [], t_x_vintages),
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
    get_world()                                  # built first, with no mutant active
    bad_total, n_checks, n_mut = 0, 0, 0
    if only:
        names = {m for _, _, ms, _ in GUARDS for m in ms}
        if only not in names:
            print("unknown mutant %r" % only)
            return 2
        with mutant(only):
            for gid, desc, muts, fn in GUARDS:
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
                print("       mutant %-30s %s%s" % (m, "caught" if caught else "NOT CAUGHT", "  (first failing check: %s)" % mk.failed()[0][0][:70] if caught else ""))
    print("selftest: %d guards, %d checks, %d mutants applied one at a time, %d failure(s), %.1f s" % (len(GUARDS), n_checks, n_mut, bad_total, time.time() - t0))
    return 0 if bad_total == 0 else 1




# ==== COMMAND LINE ====
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch", help="download the six inputs into the cache (the only network command)")
    pf.add_argument("--cache", default=CACHE_DEFAULT)
    pf.add_argument("--out", default=OUT_DEFAULT, help="where fetch_log.csv is kept")
    pf.add_argument("--sleep", type=float, default=DEFAULT_SLEEP)
    pf.add_argument("--max-requests", type=int, default=6)
    pb = sub.add_parser("build", help="offline: validate the cache and write every output")
    pb.add_argument("--cache", default=CACHE_DEFAULT)
    pb.add_argument("--out", default=OUT_DEFAULT)
    ps = sub.add_parser("selftest", help="synthetic data, mutants applied one at a time; no network")
    ps.add_argument("--no-mutants", action="store_true")
    ps.add_argument("--mutant", help="run every guard with this one mutant switched on; exit 1 (the selftest fails) when it is caught")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "selftest":
            return selftest(mutants=not a.no_mutants, only=a.mutant)
        if a.cmd == "build":
            return run_build(a)
        return run_fetch(a)
    except Refused as e:
        print("refused: %s" % e, file=sys.stderr)
        return 5
    except DataError as e:
        print("STOP (data): %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
