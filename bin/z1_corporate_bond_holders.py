#!/usr/bin/env python3
"""Who acquired US corporate and foreign bonds, by holder sector, 2024Q1-2026Q2 against 2017-2019 (Federal Reserve Financial Accounts, Z.1 table F3.5). Python 3
standard library only.

  python3 bin/z1_corporate_bond_holders.py fetch --release YYYYMMDD [--cache DIR] [--out DIR]   # the only network command; exactly 1 request
  python3 bin/z1_corporate_bond_holders.py build [--cache DIR] [--out DIR]                       # offline; byte-identical on re-run, over every cached release
  python3 bin/z1_corporate_bond_holders.py selftest [--no-mutants] [--mutant NAME]               # synthetic data only; no network

Specification: _research/2026-10-26-Z1-Corporate-Bond-Holders-Spec.md (committed at bc22c96, with its supervisor rulings of rounds 1 and 2; the latest round wins).
Outputs: data/z1_corporate_bond_holders/ (twelve CSVs, README.md, SOURCES.md).

WHAT TOUCHES THE NETWORK. Only `fetch`, only www.federalreserve.gov, only /releases/z1/<YYYYMMDD>/z1_csv_files.zip, exactly one GET per run, at most two runs a
calendar day and at least 3 seconds apart, no redirect followed, no retry of any kind, the neutral identification string (no address, no name). The release landing
page is never requested. A 404 prints `NOT POSTED <path>` and ends with exit 3 and no latch. Any other status, and a 200 body that is empty, a web page or not a zip,
writes STOP_z1cb in data/vintages/z1_corporate_bond_holders/ and ends with exit 2. A timeout or connection error ends with exit 3 and latches nothing. With the latch
present no request is made. This script never deletes, renames over or truncates a STOP file; only a person deletes one.

WHAT IT RECORDS. The Federal Reserve's own quarterly accounts of the net acquisition of corporate and foreign bonds by each holder sector, the net issuance by each issuer
sector, and the amounts outstanding. It records sector accounts only: it does not identify any issuer or any deal, and a net acquisition is purchases minus sales and
redemptions, not purchases.
"""
import argparse
import ast
import collections
import contextlib
import csv
import datetime as dt
import decimal
import email.utils
import hashlib
import http.client
import io
import os
import re
import sys
import tempfile
import time
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
    """A request, path or setting this script will not honour."""


class Latched(Exception):
    """A technical refusal: STOP was written (or already exists); the fetch ends."""


class SocketFault(Exception):
    """Timeout, reset or TLS error: the invocation ends with exit 3, without latching."""


class NotPosted(Exception):
    """A 404 on a release zip: the release is not posted yet (R1-10)."""


class DataError(Exception):
    """A hard problem with the data or with an output."""


# ------------------------------------------------------------------------------------------------------------------------
# constants
# ------------------------------------------------------------------------------------------------------------------------
OUT_DEFAULT = os.path.join(ROOT, "data", "z1_corporate_bond_holders")
CACHE_DEFAULT = os.path.join(ROOT, "data", "vintages", "z1_corporate_bond_holders")
STOP_DIR = CACHE_DEFAULT                      # fixed, whatever --cache says: a latch cannot be dodged by pointing the cache elsewhere
STOP_NAME = "STOP_z1cb"

UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
HEADERS = {"User-Agent": UA, "Accept-Encoding": "identity", "Accept": "*/*"}
HOST = "www.federalreserve.gov"
BLOCKED_HOSTS = ("sec.gov", "fred.stlouisfed.org", "alfred.stlouisfed.org", "home.treasury.gov", "ticdata.treasury.gov", "treasury.gov")
MIN_SLEEP = 3.0
MAX_RUNS_PER_DAY = 2
TIMEOUT = 300
BODY_CAP = 120 * 1024 * 1024
ERR_CAP = 4096
MEMBER_CAP = 20 * 1024 * 1024
ZIP_PATH_RX = re.compile(r"^/releases/z1/(\d{8})/z1_csv_files\.zip$")
RELEASE_RX = re.compile(r"^\d{8}$")

PIN_RELEASE = "20260911"                       # the release the pins of section 8 and the registered base refer to
ZIP_NAME = "z1_csv_files.zip"
REQUIRED_CSV = ("F3_5_t_tu", "F3_5_t", "F3_5_s", "S1281_1_t_tu", "S1281_1_s", "S1281_2_t_tu", "S1281_2_s")
FIXED_MEMBERS = collections.OrderedDict()      # zip member name -> fixed cache file name (never built from an archive name)
for _b in REQUIRED_CSV:
    FIXED_MEMBERS["csv/%s.csv" % _b] = "%s.csv" % _b
for _b in REQUIRED_CSV:
    FIXED_MEMBERS["data_dictionary/%s.txt" % _b] = "data_dictionary/%s.txt" % _b
PIN_ZIP = {"sha256": "b63af9755437df0fb88b7cf346f8f9eaeb22bf1aa2b5df1709334135c43de4b6", "bytes": 8336582, "last_modified": "2026-09-11T16:00:19Z", "members": 616}
PIN_MEMBER_BYTES = {"F3_5_t_tu.csv": 67645, "F3_5_t.csv": 73944, "F3_5_s.csv": 82820}

# Typed constants (R1-5, R1-6; CREF2 only). Never fetched; they appear in checks.csv and nowhere else among the outputs.
TIC_2024_BN = Decimal("304.5")
TIC_2025_BN = Decimal("392.4")
GROK_SA_2024_BN = Decimal("298.8")
# Review-derived values (CREF1; R1-5): unadjusted insurer sums, 20260911 only.
CREF1 = collections.OrderedDict([
    ("y2024", {"life": 224689, "pc": 70237, "total": 794490, "pct": Decimal("37.12")}),
    ("y2025", {"life": 221483, "pc": 65834, "total": 805405, "pct": Decimal("35.67")}),
])
CREF1_WAVE_PCT = Decimal("33.26")
CREF1_PP_TOL = Decimal("0.005")

# ------------------------------------------------------------------------------------------------------------------------
# the specification's canonical texts (pasted; the hashes are checked at run time)
# ------------------------------------------------------------------------------------------------------------------------
SPEC_ALLOW_TEXT = (
    'quarterly.csv:release,quarter,series_code,line,table,role,group,basis,value_usd_mn\n'
    'levels.csv:release,quarter,series_code,line,table,role,group,valuation,level_usd_mn\n'
    'windows.csv:release,window,from_quarter,to_quarter,n_quarters,side,role,group,basis,flow_usd_mn,avg_per_quarter_usd_mn,share_of_total_pct,total_usd_mn,share_of_positive_pct,positive_total_usd_mn,offset_ratio,stability_flag\n'
    'level_shares.csv:release,quarter,group,level_usd_mn,share_of_holders_pct,holders_total_usd_mn,discrepancy_usd_mn\n'
    'level_change.csv:release,window,group,level_start_usd_mn,level_end_usd_mn,flow_usd_mn,change_minus_flow_usd_mn\n'
    'headline.csv:release,statistic,window,basis,group,flow_usd_mn,value,unit\n'
    'registered.csv:statement_id,group,window,basis,release_base,release_new,share_base_pct,share_new_pct,abs_delta_pp,threshold_pp,label\n'
    'comparisons.csv:release,side,group,basis,window_a,window_b,share_a_pct,share_b_pct,change_pp\n'
    'revisions.csv:release_prev,release_new,window,side,group,basis,flow_prev_usd_mn,flow_new_usd_mn,share_prev_pct,share_new_pct,change_pp\n'
    'checks.csv:check_id,description,expected,observed,status\n'
    'vintages.csv:release,url_path,sha256,bytes,last_modified,retrieved_utc\n'
    'fetch_log.csv:utc_time,host,path,status,bytes,sha256,last_modified\n'
)
SPEC_ALLOW_SHA256 = "da0c7635f50184f044c8ebc04f2affceef805fb7d015ef023a4ca530c52860f9"
SPEC_PREREG_SHA256 = "e4e306b4731b97f94b5e5d5a0acab38ee1287a684ecb9e438352663f0e621f99"
ALLOW_ORDER = tuple(l.split(":", 1)[0] for l in SPEC_ALLOW_TEXT.splitlines())
ALLOW = {l.split(":", 1)[0]: l.split(":", 1)[1].split(",") for l in SPEC_ALLOW_TEXT.splitlines()}
COMMITTED = tuple(ALLOW_ORDER) + ("README.md", "SOURCES.md")

# G14's literal patterns (pasted, not imported), both compiled with re.I
CAUSAL_RX = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b", re.I)
EXTRA_RX = re.compile(r"\b(?:in|out)flows?\b|\bflow(?:s|ed|ing)?\s+(?:into|out\s+of|from|to)\b|\bnet\s+(?:sell|buy)(?:ers?|ing)\b|\bbought\b|\bbuyers?\b|\bdemand\b|\b(?:sell|sells|sold|selling|sale|sales|buy|buys|buying|purchas(?:e|es|ed|ing))\s+(?:of\s+)?(?:equit(?:y|ies)|stocks?|shares|bonds|assets)\b|\bforced\s+(?:sell|sale)\w*|\bliquidat\w*|\bsell[- ]?off\b|\bbid\b|\bdrain\w*|\bdeplet\w*|\bcrisis\b|\b(?:fund|funds|funded|funding|financ\w+)\s+(?:of\s+)?(?:the\s+)?AI\b|\bAI(?:-era)?\s+(?:bond\s+)?(?:wave|boom|bonds?|debt|paper|issuance|supply)\b|\bcomposition\s+of\b", re.I)
DENIAL_SENTENCE = ("These are flows for the whole US corporate and foreign bond market; Z.1 has no line for the AI companies' bonds, so nothing here shows who holds AI debt "
                   "or who bought any deal, and a net acquisition is purchases minus sales and redemptions, not purchases.")
DISCLOSURE_SENTENCE = "The wave-window shares were seen during review, before this spec was committed, so they are reported, not tested."
SHARE_EXPLAIN = ("A share can be below zero or above 100% because the total is a net: groups that reduced their holdings count as negative, so the rest add to more than 100%.")
VERDICT_WORDS = ("HELD", "FALSIFIED", "NOT_HELD", "INSIDE_BAND", "ABOVE_BAND", "BELOW_BAND")      # R1-1: never written to any output
VERDICT_RX = re.compile(r"HELD|FALSIFIED|INSIDE_BAND|ABOVE_BAND|BELOW_BAND")

ALLOWED_VALUES = {
    "role": {"issuer_total", "issuer", "issuer_detail", "holder_total", "holder", "member", "derived", "subline", "discrepancy"},
    "side": {"holder", "issuer"},
    "basis": {"fu", "fa_div4"},
    "valuation": {"lm_market", "fl_unspecified"},
    "table": {"F3.5", "S1281_1", "S1281_2"},
    "group": {"total", "ins", "ins_life", "ins_pc", "ins_life_ga", "ins_life_sa", "pen", "pen_private", "pen_federal", "pen_sl", "funds", "funds_mutual", "funds_cef", "funds_etf",
              "funds_interval", "row", "banks", "hh_residual", "private_funds", "hedge_funds", "private_debt_funds", "hh_plus_private_funds", "gse_bd", "other", "discrepancy",
              "none", "iss_total", "iss_nfc", "iss_domfin", "iss_dom_banks", "iss_dom_abs", "iss_dom_finco", "iss_dom_mreit", "iss_dom_bdc", "iss_dom_bd", "iss_dom_hc",
              "iss_dom_ofb", "iss_row"},
    "stability_flag": {"ok", "offsetting", "void_nonpositive_total"},
    "statistic": {"ins_share_wave_pct", "group_share_wave_pct", "iss_share_wave_pct", "rank_wave"},
    "unit": {"pct", "rank"},
    "statement_id": {"SREV", "SREV-F", "SREV-R"},
    "label": {"STABLE", "MOVED", "PENDING"},
    "status": {"PASS", "WARN", "FAIL", "INFO"},
}
WINDOW_NAMES = ["wave", "wave_ext", "pre1719", "pre2223"] + ["y%d" % y for y in range(2017, 2026)] + ["y2026h1"]
ALLOWED_VALUES["window"] = set(WINDOW_NAMES)
NONE_GROUP_FILES = ("quarterly.csv", "levels.csv")
KEYS = {
    "quarterly.csv": ("release", "quarter", "series_code", "basis"),
    "levels.csv": ("release", "quarter", "series_code"),
    "windows.csv": ("release", "window", "side", "group", "basis"),
    "level_shares.csv": ("release", "quarter", "group"),
    "level_change.csv": ("release", "window", "group"),
    "headline.csv": ("release", "statistic", "group"),
    "registered.csv": ("statement_id", "release_new"),
    "comparisons.csv": ("release", "side", "group", "basis", "window_a", "window_b"),
    "revisions.csv": ("release_prev", "release_new", "window", "side", "group", "basis"),
    "checks.csv": ("check_id",),
    "vintages.csv": ("release",),
    "fetch_log.csv": ("utc_time", "path"),
}

# ------------------------------------------------------------------------------------------------------------------------
# the series of section 2.2, pasted: (line, table, FU code, level code, role, group, parent group). FA codes are the FU codes with FA for FU, same lines (F3.5 only).
# ------------------------------------------------------------------------------------------------------------------------
LINES_RAW = [
    (1, 'F3.5', 'FU893163005.Q', 'FL893163005.Q', 'issuer_total', 'iss_total', 'iss_total'),
    (2, 'F3.5', 'FU103163005.Q', 'FL103163005.Q', 'issuer', 'iss_nfc', 'iss_nfc'),
    (3, 'F3.5', 'FU793163005.Q', 'FL793163005.Q', 'issuer', 'iss_domfin', 'iss_domfin'),
    (4, 'F3.5', 'FU763163005.Q', 'FL763163005.Q', 'issuer_detail', 'iss_dom_banks', 'iss_dom_banks'),
    (5, 'F3.5', 'FU673163005.Q', 'FL673163005.Q', 'issuer_detail', 'iss_dom_abs', 'iss_dom_abs'),
    (6, 'F3.5', 'FU613163005.Q', 'FL613163005.Q', 'issuer_detail', 'iss_dom_finco', 'iss_dom_finco'),
    (7, 'F3.5', 'FU643163075.Q', 'FL643163075.Q', 'issuer_detail', 'iss_dom_mreit', 'iss_dom_mreit'),
    (8, 'F3.5', 'FU453163003.Q', 'FL453163003.Q', 'issuer_detail', 'iss_dom_bdc', 'iss_dom_bdc'),
    (9, 'F3.5', 'FU663163003.Q', 'FL663163003.Q', 'issuer_detail', 'iss_dom_bd', 'iss_dom_bd'),
    (10, 'F3.5', 'FU733163005.Q', 'FL733163005.Q', 'issuer_detail', 'iss_dom_hc', 'iss_dom_hc'),
    (11, 'F3.5', 'FU503163003.Q', 'FL503163003.Q', 'issuer_detail', 'iss_dom_ofb', 'iss_dom_ofb'),
    (12, 'F3.5', 'FU263163005.Q', 'LM263163005.Q', 'issuer', 'iss_row', 'iss_row'),
    (13, 'F3.5', 'FU893063005.Q', 'FL893063005.Q', 'holder_total', 'total', 'total'),
    (14, 'F3.5', 'FU153063005.Q', 'LM153063005.Q', 'holder', 'hh_residual', 'hh_residual'),
    (15, 'F3.5', 'FU123063003.Q', 'LM123063003.Q', 'holder', 'other', 'other'),
    (16, 'F3.5', 'FU313063005.Q', 'FL313063005.Q', 'holder', 'other', 'other'),
    (17, 'F3.5', 'FU213063003.Q', 'LM213063003.Q', 'holder', 'other', 'other'),
    (18, 'F3.5', 'FU713011525.Q', 'FL713011525.Q', 'holder', 'other', 'other'),
    (19, 'F3.5', 'FU763063005.Q', 'LM763063005.Q', 'holder', 'banks', 'banks'),
    (20, 'F3.5', 'FU763063605.Q', 'LM763063605.Q', 'subline', 'none', 'none'),
    (21, 'F3.5', 'FU763063095.Q', 'LM763063095.Q', 'subline', 'none', 'none'),
    (22, 'F3.5', 'FU753063005.Q', 'LM753063005.Q', 'holder', 'banks', 'banks'),
    (23, 'F3.5', 'FU743063005.Q', 'LM743063005.Q', 'holder', 'banks', 'banks'),
    (24, 'F3.5', 'FU473063005.Q', 'LM473063005.Q', 'holder', 'banks', 'banks'),
    (25, 'F3.5', 'FU473063605.Q', 'LM473063605.Q', 'subline', 'none', 'none'),
    (26, 'F3.5', 'FU473063095.Q', 'LM473063095.Q', 'subline', 'none', 'none'),
    (27, 'F3.5', 'FU513063005.Q', 'LM513063005.Q', 'holder', 'ins_pc', 'ins'),
    (28, 'F3.5', 'FU513063605.Q', 'LM513063605.Q', 'subline', 'none', 'none'),
    (29, 'F3.5', 'FU513063095.Q', 'LM513063095.Q', 'subline', 'none', 'none'),
    (30, 'F3.5', 'FU543063005.Q', 'LM543063005.Q', 'holder', 'ins_life', 'ins'),
    (31, 'F3.5', 'FU543063675.Q', 'LM543063675.Q', 'subline', 'none', 'none'),
    (32, 'F3.5', 'FU543063095.Q', 'LM543063095.Q', 'subline', 'none', 'none'),
    (8, 'S1281_1', 'FU543063075.Q', 'LM543063075.Q', 'subline', 'ins_life_ga', 'ins_life_ga'),
    (8, 'S1281_2', 'FU543063085.Q', 'LM543063085.Q', 'subline', 'ins_life_sa', 'ins_life_sa'),
    (33, 'F3.5', 'FU573063005.Q', 'LM573063005.Q', 'holder', 'pen_private', 'pen'),
    (34, 'F3.5', 'FU343063005.Q', 'LM343063005.Q', 'holder', 'pen_federal', 'pen'),
    (35, 'F3.5', 'FU223063045.Q', 'LM223063045.Q', 'holder', 'pen_sl', 'pen'),
    (36, 'F3.5', 'FU633063005.Q', 'FL633063005.Q', 'holder', 'other', 'other'),
    (37, 'F3.5', 'FU653063005.Q', 'LM653063005.Q', 'holder', 'funds_mutual', 'funds'),
    (38, 'F3.5', 'FU553063003.Q', 'LM553063003.Q', 'holder', 'funds_cef', 'funds'),
    (39, 'F3.5', 'FU563063003.Q', 'LM563063003.Q', 'holder', 'funds_etf', 'funds'),
    (40, 'F3.5', 'FU463063005.Q', 'LM463063005.Q', 'holder', 'funds_interval', 'funds'),
    (41, 'F3.5', 'FU623063005.Q', 'LM623063005.Q', 'holder', 'hedge_funds', 'private_funds'),
    (42, 'F3.5', 'FU443063000.Q', 'LM443063000.Q', 'holder', 'private_debt_funds', 'private_funds'),
    (43, 'F3.5', 'FU403063005.Q', 'LM403063005.Q', 'holder', 'gse_bd', 'gse_bd'),
    (44, 'F3.5', 'FU403063605.Q', 'LM403063605.Q', 'subline', 'none', 'none'),
    (45, 'F3.5', 'FU403063095.Q', 'LM403063095.Q', 'subline', 'none', 'none'),
    (46, 'F3.5', 'FU613063003.Q', 'LM613063003.Q', 'holder', 'other', 'other'),
    (47, 'F3.5', 'FU643063073.Q', 'LM643063073.Q', 'holder', 'other', 'other'),
    (48, 'F3.5', 'FU663063005.Q', 'LM663063005.Q', 'holder', 'gse_bd', 'gse_bd'),
    (49, 'F3.5', 'FU733063003.Q', 'LM733063003.Q', 'holder', 'other', 'other'),
    (50, 'F3.5', 'FU503063005.Q', 'FL503063005.Q', 'holder', 'other', 'other'),
    (51, 'F3.5', 'FU263063005.Q', 'LM263063005.Q', 'holder', 'row', 'row'),
    (52, 'F3.5', 'FU263063603.Q', 'LM263063603.Q', 'subline', 'none', 'none'),
    (53, 'F3.5', 'FU263063095.Q', 'LM263063095.Q', 'subline', 'none', 'none'),
    (54, 'F3.5', None, 'LM903063003.Q', 'discrepancy', 'discrepancy', 'discrepancy'),
]

# my own verification keys for C03 (lower case; every key must occur in the dictionary text of the code): taken from the dictionary wording, not from the spec's shortened names
NAME_KEYS = {
    1: ("all sectors",), 2: ("nonfinancial corporate",), 3: ("domestic financial",), 4: ("u.s.-chartered depository",), 5: ("asset-backed securities",), 6: ("finance companies",),
    7: ("mortgage real estate investment trusts",), 8: ("business development",), 9: ("security brokers",), 10: ("holding companies",), 11: ("other financial business",),
    12: ("rest of the world",), 13: ("all sectors",), 14: ("households and nonprofit",), 15: ("equity real estate",), 16: ("federal government",), 17: ("state and local governments",),
    18: ("central bank",), 19: ("depository institutions, including ibfs",), 20: ("depository institutions", "private mbs"), 21: ("depository institutions", "excluding private mbs"),
    22: ("foreign banking offices",), 23: ("banks in u.s.-affiliated",), 24: ("credit unions",), 25: ("credit unions", "mortgage-backed"), 26: ("credit unions", "excluding"),
    27: ("property-casualty",), 28: ("property-casualty", "mortgage-backed"), 29: ("property-casualty", "excluding"), 30: ("life insurance companies",),
    31: ("life insurance companies", "mortgage-backed"), 32: ("life insurance companies", "excluding"), 33: ("private pension",), 34: ("federal government pension",),
    35: ("defined benefit pension",), 36: ("money market",), 37: ("mutual funds",), 38: ("closed-end",), 39: ("exchange-traded",), 40: ("interval",), 41: ("hedge funds",),
    42: ("private debt",), 43: ("government-sponsored",), 44: ("government-sponsored", "mortgage-backed"), 45: ("government-sponsored", "excluding"), 46: ("finance companies",),
    47: ("mortgage real estate",), 48: ("security brokers",), 49: ("holding companies",), 50: ("other financial business",), 51: ("rest of the world",),
    52: ("rest of the world", "mortgage-backed"), 53: ("rest of the world", "excluding"), 54: ("instrument discrepancies",),
}
GA_KEYS = ("general accounts",)
SA_KEYS = ("separate accounts",)
S1281_TABLE_MARK = {"S1281_1": "s1281.1", "S1281_2": "s1281.2"}


class Line(object):
    __slots__ = ("line", "table", "fu", "fa", "lvl", "role", "group", "parent", "keys")

    def __init__(self, line, table, fu, lvl, role, group, parent):
        self.line, self.table, self.fu, self.lvl, self.role, self.group = line, table, fu, lvl, role, group
        self.fa = ("FA" + fu[2:]) if (fu and table == "F3.5") else None
        if role == "issuer_detail":
            parent = "iss_domfin"
        self.parent = parent
        self.keys = NAME_KEYS[line] if table == "F3.5" else (GA_KEYS if table == "S1281_1" else SA_KEYS)


LINES = [Line(*r) for r in LINES_RAW]
F35 = [l for l in LINES if l.table == "F3.5"]
BYLINE = {l.line: l for l in F35}
GA, SA = [l for l in LINES if l.table == "S1281_1"][0], [l for l in LINES if l.table == "S1281_2"][0]
LEAVES = [l for l in F35 if l.role == "holder"]                                          # the 28 leaf holder lines
ISS_LEAVES = [BYLINE[2], BYLINE[3], BYLINE[12]]
ISS_DETAILS = [l for l in F35 if l.role == "issuer_detail"]
GROUPS9 = ["ins", "pen", "funds", "row", "banks", "hh_residual", "private_funds", "gse_bd", "other"]
RANKED7 = ["ins", "pen", "funds", "row", "banks", "hh_residual", "private_funds"]
MEMBERS = collections.OrderedDict([("ins", ["ins_life", "ins_pc"]), ("pen", ["pen_private", "pen_federal", "pen_sl"]),
                                   ("funds", ["funds_mutual", "funds_cef", "funds_etf", "funds_interval"]), ("private_funds", ["hedge_funds", "private_debt_funds"])])
ISS3 = ["iss_nfc", "iss_domfin", "iss_row"]
ISS_DETAIL_GROUPS = [l.group for l in ISS_DETAILS]
HHPF = "hh_plus_private_funds"
CODE_LINE = {}
for _l in LINES:
    if _l.fu:
        CODE_LINE[_l.fu] = _l
    if _l.fa:
        CODE_LINE[_l.fa] = _l
    CODE_LINE[_l.lvl] = _l
FILE_OF = {}                                                                             # code -> the CSV file (without extension) that carries it
for _l in LINES:
    if _l.table == "F3.5":
        if _l.fu:
            FILE_OF[_l.fu] = "F3_5_t_tu"
            FILE_OF[_l.fa] = "F3_5_t"
        FILE_OF[_l.lvl] = "F3_5_s"
    else:
        FILE_OF[_l.fu] = "%s_t_tu" % _l.table
        FILE_OF[_l.lvl] = "%s_s" % _l.table
EXPECT_ORDER = collections.OrderedDict((f, []) for f in REQUIRED_CSV)                   # the order the Fed's F3.5 files carry the codes in (used only by a mutant)
for _l in LINES:
    for _c in (_l.fu, _l.fa, _l.lvl):
        if _c:
            EXPECT_ORDER[FILE_OF[_c]].append(_c)


# ------------------------------------------------------------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------------------------------------------------------------
def tilde(p):
    home = os.path.expanduser("~")
    return str(p).replace(home, "~") if home and home != "~" else str(p)


def sha256_of(b):
    return hashlib.sha256(b).hexdigest()


def D(x):
    if x is None:
        return None
    if isinstance(x, Decimal):
        return x
    return Decimal(str(x).strip())


def fdec(v, nd):
    """Fixed-decimal text of a Decimal, '' for None, no negative zero. Rounding is half-even and happens only here, at write time (R8)."""
    if v is None:
        return ""
    q = Decimal(1).scaleb(-nd)
    s = format(Decimal(v).quantize(q, rounding=decimal.ROUND_HALF_EVEN), "f")
    if s.startswith("-") and Decimal(s) == 0:
        s = s[1:]
    return s


def usd(v):
    """A money cell, millions of dollars, three decimals (R8). The mutant writes billions into the same column (G18)."""
    if v is not None and M("g18_bn_in_mn"):
        v = v / 1000
    return fdec(v, 3)


def pct(v):
    return fdec(v, 3)


def dsum(values):
    """Exact Decimal sum (R8). The mutant sums as binary floating point (G1)."""
    if M("g1_float_sum"):
        f = 0.0
        for v in values:
            f += float(v)
        return Decimal(repr(f))
    t = Decimal(0)
    for v in values:
        t += v
    return t


def assert_ua(ua=UA):
    if not M("g16_at_in_ua_ok"):
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


def read_file(path, mode="rb"):
    with open(path, mode) as fh:
        return fh.read()


def read_csv_rows(path):
    """(header, rows) of a csv with comment lines (# ...) skipped; ([], []) if absent."""
    if not os.path.exists(path):
        return [], []
    with open(path, encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh.read().splitlines(True) if not ln.startswith("#")]
    rd = list(csv.reader(io.StringIO("".join(lines))))
    return (rd[0], rd[1:]) if rd else ([], [])


def http_date_iso(s):
    """An HTTP date (always GMT) as a UTC ISO text. Never local time."""
    d = email.utils.parsedate_to_datetime(s)
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------------------------------------------------------------
# quarters and parsing (R8): the csv module, columns by series code from the header row, `ND` or blank is missing
# ------------------------------------------------------------------------------------------------------------------------
def _qrx():
    return re.compile(r"^(\d{4}):?Q([1-4])$") if M("g1_date_noq_ok") else re.compile(r"^(\d{4}):Q([1-4])$")


def qidx(q):
    m = _qrx().match(q or "")
    if not m:
        raise DataError("not a YYYY:QN date: %r" % (q,))
    return int(m.group(1)) * 4 + int(m.group(2)) - 1


def qname(i):
    return "%d:Q%d" % (i // 4, i % 4 + 1)


def qrange(a, b):
    return [qname(i) for i in range(qidx(a), qidx(b) + 1)]


def cell(s):
    """A data cell as a Decimal; `ND` and blank are missing (None), never zero (C09)."""
    s = s.strip()
    if s in ("ND", ""):
        return Decimal(0) if M("g1_nd_zero") else None
    try:
        v = Decimal(s)
    except decimal.InvalidOperation:
        raise DataError("a data cell is not a number: %r" % s[:20])
    if not v.is_finite():
        raise DataError("a data cell is not finite: %r" % s[:20])
    return v


class Table(object):
    """One Z.1 CSV: the header row, then one row per date. Columns are looked up by series code (with its .Q suffix) in the header, never by position."""

    def __init__(self, name, raw):
        enc = "utf-8" if M("g1_bom_breaks") else "utf-8-sig"
        try:
            text = raw.decode(enc)
        except UnicodeDecodeError:
            raise DataError("%s: not UTF-8" % name)
        rd = list(csv.reader(io.StringIO(text, newline="")))
        if not rd or not rd[0] or rd[0][0] != "date":
            raise DataError("%s: the first header cell is not 'date'" % name)
        self.name = name
        self.head = [h.strip() for h in rd[0]]
        self.pos = {}
        for i, h in enumerate(self.head):
            if i and h in self.pos:
                raise DataError("%s: duplicate column %s" % (name, h))
            self.pos[h] = i
        self.rows = collections.OrderedDict()
        for r in rd[1:]:
            if not r or (len(r) == 1 and not r[0].strip()):
                continue
            if len(r) != len(self.head):
                raise DataError("%s: a row has %d cells, the header %d" % (name, len(r), len(self.head)))
            q = r[0].strip()
            qidx(q)
            if q in self.rows:
                raise DataError("%s: duplicate date %s" % (name, q))
            self.rows[q] = r
        self.quarters = list(self.rows)
        self._cache = {}

    def col(self, code):
        if M("g1_col_by_position"):
            exp = EXPECT_ORDER.get(self.name, [])
            return exp.index(code) + 1 if code in exp else None
        if M("g1_code_no_suffix"):
            stem = code.split(".")[0]
            for h in self.head[1:]:
                if h.split(".")[0] == stem:
                    return self.pos[h]
            return None
        return self.pos.get(code)

    def has(self, code):
        return self.col(code) is not None

    def series(self, code):
        """{quarter: Decimal or None} of one code, or None if the code is not in the header."""
        ck = (code, tuple(sorted(_ACTIVE)))
        if ck in self._cache:
            return self._cache[ck]
        c = self.col(code)
        if c is None:
            self._cache[ck] = None
            return None
        out = collections.OrderedDict((q, cell(r[c])) for q, r in self.rows.items())
        self._cache[ck] = out
        return out

    def n_codes(self):
        return len(self.head) - 1


def parse_dictionary(raw):
    """{code: (description, line text, table text)} from a tab-separated data_dictionary file."""
    out = {}
    for ln in raw.decode("utf-8-sig", errors="replace").splitlines():
        f = ln.split("\t")
        if len(f) >= 4 and f[0].strip():
            out[f[0].strip()] = (f[1].strip(), f[2].strip(), f[3].strip())
    return out


# ------------------------------------------------------------------------------------------------------------------------
# a cached release, and the group mapping (section 2.2)
# ------------------------------------------------------------------------------------------------------------------------
PROV_COLS = ["kind", "name", "sha256", "bytes", "last_modified", "members"]


class Rel(object):
    """One cached release: the seven tables, the seven dictionaries, provenance.csv. `key` is the dated folder in the zip URL."""

    def __init__(self, key, tables, dicts, prov, problems=(), folder=None):
        self.key = key
        self.folder = folder
        self.tables = tables
        self.dicts = dicts
        self.prov = prov                       # list of dict rows of provenance.csv
        self.problems = list(problems)         # structural problems found while loading (reported by C15)
        main = tables.get("F3_5_t_tu")
        self.quarters = list(main.quarters) if main else []
        self.qset = set(self.quarters)
        self.latest = max(self.quarters) if self.quarters else ""

    def series(self, code):
        t = self.tables.get(FILE_OF[code])
        return t.series(code) if t is not None else None

    def q(self, code, q):
        s = self.series(code)
        return s.get(q) if s is not None else None

    def zip_row(self):
        for r in self.prov:
            if r.get("kind") == "zip":
                return r
        return {}


def load_release(folder):
    """Read a cached release folder. Files are opened by fixed name. A missing table is a DataError; a missing dictionary is recorded and reported by C15."""
    key = os.path.basename(os.path.normpath(folder))
    if not RELEASE_RX.match(key):
        raise DataError("not a release folder: %s" % key)
    prov_path = os.path.join(folder, "provenance.csv")
    if not os.path.exists(prov_path):
        raise DataError("release %s has no provenance.csv (the fetch did not finish)" % key)
    h, rows = read_csv_rows(prov_path)
    prov = [dict(zip(h, r)) for r in rows]
    tables, dicts, problems = {}, {}, []
    for b in REQUIRED_CSV:
        p = os.path.join(folder, "%s.csv" % b)
        if not os.path.exists(p):
            raise DataError("release %s lacks %s.csv" % (key, b))
        tables[b] = Table(b, read_file(p))
        dp = os.path.join(folder, "data_dictionary", "%s.txt" % b)
        if os.path.exists(dp):
            dicts[b] = parse_dictionary(read_file(dp))
        else:
            problems.append("missing dictionary %s.txt" % b)
    return Rel(key, tables, dicts, prov, problems, folder)


def list_releases(cache):
    out = []
    if os.path.isdir(cache):
        for n in sorted(os.listdir(cache)):
            if RELEASE_RX.match(n) and os.path.isfile(os.path.join(cache, n, "provenance.csv")):
                out.append(n)
    return out


def flow(rel, basis, line, q, mut="g4_fa_not_div4"):
    """One line's quarterly flow on a basis. fu: the unadjusted flow. fa_div4: the seasonally adjusted annual rate divided by 4 (R8, 2.4). Missing is None."""
    if basis == "fu":
        code = line.lvl if M("g18_level_as_flow") else line.fu
        return rel.q(code, q) if code else None
    if not line.fa:
        return None
    v = rel.q(line.fa, q)
    if v is None:
        return None
    return v if M(mut) else v / 4


def level(rel, line, q):
    return rel.q(line.lvl, q)


def all_member_groups():
    return [m for ms in MEMBERS.values() for m in ms]


def nine():
    return GROUPS9 + ([HHPF] if M("g2_hhpf_in_nine") else [])


def group_lines(g):
    """The lines whose flows (or levels) make up a group. Sub-lines, issuer details and line 54 are never part of a holder group."""
    if g in GROUPS9:
        ls = [l for l in LEAVES if l.parent == g]
        if g == "banks" and M("g2_subline_in_group"):
            ls = ls + [BYLINE[20], BYLINE[21]]
        if g == "ins" and M("g2_ga_in_ins"):
            ls = ls + [GA]
        if g == "other" and M("g2_leaf_twice"):
            ls = ls + [BYLINE[14]]
        if g == "other" and M("g2_leaf_none"):
            ls = [l for l in ls if l.line != 50]
        return ls
    if g in all_member_groups():
        return [l for l in LEAVES if l.group == g]
    if g == "ins_life_ga":
        return [GA]
    if g == "ins_life_sa":
        return [SA]
    if g == HHPF:
        return [l for l in LEAVES if l.parent in ("hh_residual", "private_funds")]
    if g == "total":
        return [BYLINE[13]]
    if g == "iss_total":
        return [BYLINE[1]]
    if g == "iss_nfc":
        return [BYLINE[2]]
    if g == "iss_domfin":
        return [BYLINE[3]] + (ISS_DETAILS if M("g2_issuer_detail_in_domfin") else [])
    if g == "iss_row":
        return [BYLINE[12]]
    if g in ISS_DETAIL_GROUPS:
        return [l for l in ISS_DETAILS if l.group == g]
    raise DataError("unknown group %s" % g)


def mapping_problems():
    """G2: the 28 leaf lines each belong to exactly one of the nine groups; sub-lines, details, line 54 and the derived row are in none."""
    out = []
    if len(LEAVES) != 28:
        out.append("the number of leaf holder lines is %d, not 28" % len(LEAVES))
    seen = collections.Counter()
    for g in nine():
        for l in group_lines(g):
            seen[(l.table, l.line)] += 1
            if l.role != "holder":
                out.append("group %s holds a line of role %s (%s line %s)" % (g, l.role, l.table, l.line))
    for l in LEAVES:
        c = seen[(l.table, l.line)]
        if c != 1:
            out.append("leaf line %s is in %d groups" % (l.line, c))
    if len(nine()) != 9:
        out.append("the holder groups are %d, not nine" % len(nine()))
    if sorted(g for g in nine() if g == HHPF):
        out.append("the derived row %s is counted among the nine" % HHPF)
    dom = sorted(l.line for l in group_lines("iss_domfin"))
    if dom != [3]:
        out.append("iss_domfin holds lines %r, not [3]" % dom)
    return out


# ------------------------------------------------------------------------------------------------------------------------
# windows (section 3.4)
# ------------------------------------------------------------------------------------------------------------------------
def window_defs(latest, for_revisions=False):
    """[(name, from, to)] for a release whose newest quarter is `latest`. `wave` is fixed at 2024:Q1-2026:Q2 in every release (2.8)."""
    wave_to = latest if (M("g4_wave_to_latest") or (for_revisions and M("g9_wave_11"))) else "2026:Q2"
    wave_from = "2024:Q2" if M("g4_wave_start_q2") else "2024:Q1"
    defs = [("wave", wave_from, wave_to)]
    if latest > "2026:Q2" or M("g4_wave_ext_sept"):
        defs.append(("wave_ext", "2024:Q1", latest))
    defs += [("pre1719", "2017:Q1", "2019:Q4"), ("pre2223", "2022:Q1", "2023:Q4")]
    defs += [("y%d" % y, "%d:Q1" % y, "%d:Q4" % y) for y in range(2017, 2026)]
    defs.append(("y2026h1", "2026:Q1", "2026:Q2"))
    return defs


def wsum(rel, basis, line, qs, mut="g4_fa_not_div4"):
    vals = [flow(rel, basis, line, q, mut) for q in qs]
    if any(v is None for v in vals):
        return None
    return dsum(vals)


def ratio_pct(num, den):
    return Decimal(100) * num / den


def holder_order():
    """[(group, role)] in output order: total, then each of the nine with its members, the derived row after private_funds."""
    out = [("total", "holder_total")]
    for g in nine():
        out.append((g, "derived" if g == HHPF else "holder"))
        for m in MEMBERS.get(g, []):
            out.append((m, "member"))
            if m == "ins_life":
                out += [("ins_life_ga", "subline"), ("ins_life_sa", "subline")]
        if g == "private_funds":
            out.append((HHPF, "derived"))
    seen, res = set(), []
    for g, r in out:
        if g not in seen:
            seen.add(g)
            res.append((g, r))
    return res


def issuer_order():
    out = [("iss_total", "issuer_total"), ("iss_nfc", "issuer"), ("iss_domfin", "issuer")]
    out += [(g, "issuer_detail") for g in ISS_DETAIL_GROUPS]
    out.append(("iss_row", "issuer"))
    return out


def stability_flag(total, ratio):
    """void when the total is not positive; offsetting when the offset ratio is below 0.5 (compared unrounded, R8); otherwise ok."""
    if total is None or total <= 0:
        return "void_nonpositive_total"
    r = ratio.quantize(Decimal("0.01"), rounding=decimal.ROUND_HALF_EVEN) if (ratio is not None and M("g5_flag_rounded")) else ratio
    if r is not None and r < Decimal("0.5"):
        return "offsetting"
    return "ok"


def side_rows(rel, w, a, b, qs, basis, side):
    n = len(qs)
    cache = {}

    def ws(l):
        k = (l.table, l.line)
        if k not in cache:
            cache[k] = wsum(rel, basis, l, qs)
        return cache[k]

    def gs(g):
        vals = [ws(l) for l in group_lines(g)]
        return None if any(v is None for v in vals) else dsum(vals)

    if side == "holder":
        order, total_g, ranked, leaves = holder_order(), "total", nine(), LEAVES
    else:
        order, total_g, ranked, leaves = issuer_order(), "iss_total", ISS3, ISS_LEAVES
    fl = {g: gs(g) for g, _ in order}
    total = fl[total_g]
    if total is None:
        return []
    if M("g5_clip_negative"):
        for g in ranked:
            if fl.get(g) is not None and fl[g] < 0:
                fl[g] = Decimal(0)
    if M("g5_other_dropped") and side == "holder":
        fl["other"] = Decimal(0)
    if M("g5_pos_total_over_leaves"):
        lv = [ws(l) for l in leaves]
        pos_total = dsum([v for v in lv if v is not None and v > 0])
    else:
        pos_total = dsum([fl[g] for g in ranked if fl.get(g) is not None and fl[g] > 0])
    if M("g5_offset_on_groups"):
        den_abs = dsum([abs(fl[g]) for g in ranked if fl.get(g) is not None])
    else:
        lv = [ws(l) for l in leaves]
        den_abs = dsum([abs(v) for v in lv if v is not None])
    ratio = (abs(total) / den_abs) if den_abs > 0 else None
    flag = stability_flag(total, ratio)
    void = flag == "void_nonpositive_total"
    den_total = pos_total if M("g5_den_positive") else total
    qmeans = None
    if M("g6_mean_of_shares"):
        qmeans = {}
        for g, _ in order:
            ratios = []
            for q in qs:
                gv = [flow(rel, basis, l, q) for l in group_lines(g)]
                tv = flow(rel, basis, group_lines(total_g)[0], q)
                if tv and None not in gv:
                    ratios.append(ratio_pct(dsum(gv), tv))
            qmeans[g] = dsum(ratios) / len(ratios) if ratios else None
    rows = []
    for g, role in order:
        f = fl.get(g)
        if f is None:
            continue
        s_tot = s_pos = None
        if not void:
            if den_total > 0:
                s_tot = ratio_pct(f, den_total)
                if qmeans is not None:
                    s_tot = qmeans[g]
            if role not in ("holder_total", "issuer_total") and pos_total > 0 and (f > 0 or M("g5_pos_for_negative")):
                s_pos = ratio_pct(f, pos_total)
        rows.append({"release": rel.key, "window": w, "from_quarter": a, "to_quarter": b, "n_quarters": str(n), "side": side, "role": role, "group": g, "basis": basis,
                     "flow_usd_mn": usd(f), "avg_per_quarter_usd_mn": usd(f / (4 if M("g4_avg_div4") else n)), "share_of_total_pct": pct(s_tot),
                     "total_usd_mn": usd(total), "share_of_positive_pct": pct(s_pos), "positive_total_usd_mn": usd(pos_total), "offset_ratio": fdec(ratio, 4),
                     "stability_flag": flag, "_flow": f, "_share": s_tot, "_pos": s_pos})
    return rows


def window_rows(rel, for_revisions=False):
    rows = []
    for w, a, b in window_defs(rel.latest, for_revisions):
        qs = qrange(a, b)
        if not all(q in rel.qset for q in qs):
            continue
        for basis in ("fu", "fa_div4"):
            for side in ("holder", "issuer"):
                rows += side_rows(rel, w, a, b, qs, basis, side)
    return rows


def widx(rows):
    return {(r["window"], r["side"], r["group"], r["basis"]): r for r in rows}


# ------------------------------------------------------------------------------------------------------------------------
# levels (section 3.9)
# ------------------------------------------------------------------------------------------------------------------------
def valuation_of(code):
    if code.startswith("LM"):
        return "lm_market"
    if M("g7_fl_lm_market"):
        return "lm_market"
    return "fl_unspecified"


def glevel(rel, g, q):
    vals = [level(rel, l, q) for l in group_lines(g)]
    return None if any(v is None for v in vals) else dsum(vals)


def holders_total(rel, q):
    """The level-share denominator: the sum of the 28 leaf levels (equal to line 13 within rounding, 2.3). Line 54 is printed beside it, never added."""
    if M("g7_level_over_line1"):
        return level(rel, BYLINE[1], q)
    vals = [level(rel, l, q) for l in LEAVES]
    if any(v is None for v in vals):
        return None
    t = dsum(vals)
    if M("g2_disc_in_holders"):
        d = level(rel, BYLINE[54], q)
        t = t + (d or 0)
    return t


def level_groups():
    out = ["total"] + nine()
    for g in nine():
        for m in MEMBERS.get(g, []):
            out.append(m)
            if m == "ins_life":
                out += ["ins_life_ga", "ins_life_sa"]
    out.append(HHPF)
    seen, res = set(), []
    for g in out:
        if g not in seen:
            seen.add(g)
            res.append(g)
    return res


def level_share_quarters(rel):
    qs = ["2016:Q4", "2019:Q4", "2021:Q4", "2023:Q4", rel.latest]
    seen, out = set(), []
    for q in qs:
        if q not in seen and q in rel.qset:
            seen.add(q)
            out.append(q)
    return out


def level_share_rows(rel):
    rows = []
    for q in level_share_quarters(rel):
        ht = holders_total(rel, q)
        disc = None if M("g7_disc_dropped") else level(rel, BYLINE[54], q)
        for g in level_groups():
            lv = ht if g == "total" else glevel(rel, g, q)
            if lv is None or ht is None:
                continue
            sh = ratio_pct(lv, ht) if ht != 0 else None
            rows.append({"release": rel.key, "quarter": q, "group": g, "level_usd_mn": usd(lv), "share_of_holders_pct": pct(sh), "holders_total_usd_mn": usd(ht),
                         "discrepancy_usd_mn": usd(disc)})
    return rows


def level_change_rows(rel):
    rows = []
    for w, a, b in window_defs(rel.latest):
        qs = qrange(a, b)
        if not all(q in rel.qset for q in qs):
            continue
        start = a if M("g8_start_at_first") else qname(qidx(a) - 1)
        if start not in rel.qset or b not in rel.qset:
            continue
        for g in level_groups():
            ls = group_lines(g)
            fl = [wsum(rel, "fu", l, qs) for l in ls]
            if g == "total":
                lv0, lv1 = holders_total(rel, start), holders_total(rel, b)
            else:
                lv0, lv1 = glevel(rel, g, start), glevel(rel, g, b)
            if None in fl or lv0 is None or lv1 is None:
                continue
            f = dsum(fl)
            rows.append({"release": rel.key, "window": w, "group": g, "level_start_usd_mn": usd(lv0), "level_end_usd_mn": usd(lv1), "flow_usd_mn": usd(f),
                         "change_minus_flow_usd_mn": usd((lv1 - lv0) - f)})
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# quarterly ledger and levels ledger (section 3.3)
# ------------------------------------------------------------------------------------------------------------------------
def quarterly_rows(rel):
    rows = []
    for q in [q for q in rel.quarters if q >= "2017:Q1"]:
        for l in LINES:
            if l.fu:
                v = flow(rel, "fu", l, q)
                rows.append({"release": rel.key, "quarter": q, "series_code": l.fu, "line": str(l.line), "table": l.table, "role": l.role, "group": l.group,
                             "basis": "fu", "value_usd_mn": usd(v)})
            if l.fa:
                v = flow(rel, "fa_div4", l, q, "g18_fa_undivided")
                rows.append({"release": rel.key, "quarter": q, "series_code": l.fa, "line": str(l.line), "table": l.table, "role": l.role, "group": l.group,
                             "basis": "fa_div4", "value_usd_mn": usd(v)})
    return rows


def levels_rows(rel):
    rows = []
    for q in [q for q in rel.quarters if q >= "2016:Q4"]:
        for l in LINES:
            rows.append({"release": rel.key, "quarter": q, "series_code": l.lvl, "line": str(l.line), "table": l.table, "role": l.role, "group": l.group,
                         "valuation": valuation_of(l.lvl), "level_usd_mn": usd(level(rel, l, q))})
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# headline, comparisons, revisions, registered statements
# ------------------------------------------------------------------------------------------------------------------------
def ranked_groups():
    return RANKED7 + (["gse_bd", "other"] if M("g6_rank_other") else [])


def headline_rows(rel, wrows):
    basis = "fa_div4" if M("g6_headline_fa") else "fu"
    ix = widx(wrows)
    out = []

    def get(side, g):
        return ix.get(("wave", side, g, basis))

    r = get("holder", "ins")
    if r:
        out.append([rel.key, "ins_share_wave_pct", "wave", basis, "ins", r["flow_usd_mn"], r["share_of_total_pct"], "HELD" if M("g6_verdict_word") else "pct"])
    for g in nine() + [HHPF]:
        r = get("holder", g)
        if r:
            out.append([rel.key, "group_share_wave_pct", "wave", basis, g, r["flow_usd_mn"], r["share_of_total_pct"], "pct"])
    for g in ISS3:
        r = get("issuer", g)
        if r:
            out.append([rel.key, "iss_share_wave_pct", "wave", basis, g, r["flow_usd_mn"], r["share_of_total_pct"], "pct"])
    flows = {g: get("holder", g)["_flow"] for g in ranked_groups() if get("holder", g)}
    for g in ranked_groups():
        if g in flows:
            rk = 1 + sum(1 for h in flows if flows[h] > flows[g])
            out.append([rel.key, "rank_wave", "wave", basis, g, get("holder", g)["flow_usd_mn"], str(rk), "rank"])
    return out


def comparison_rows(rel, wrows):
    ix = widx(wrows)
    out = []
    for wb in ("pre1719", "pre2223"):
        for basis in ("fu", "fa_div4"):
            for side in ("holder", "issuer"):
                for (w, s, g, bs), r in ix.items():
                    if w != "wave" or s != side or bs != basis or r["role"] in ("holder_total", "issuer_total"):
                        continue
                    o = ix.get((wb, s, g, bs))
                    if o is None or r["_share"] is None or o["_share"] is None:
                        continue
                    out.append({"release": rel.key, "side": s, "group": g, "basis": bs, "window_a": "wave", "window_b": wb, "share_a_pct": pct(r["_share"]),
                                "share_b_pct": pct(o["_share"]), "change_pp": pct(r["_share"] - o["_share"]), "_o": (side, WINDOW_NAMES.index(wb), basis)})
    order = {g: i for i, (g, _) in enumerate(holder_order() + issuer_order())}
    border = {"fu": 0, "fa_div4": 1}
    out.sort(key=lambda r: (r["_o"][1], border[r["_o"][2]], r["_o"][0], order[r["group"]]))
    return out


def revision_rows(rels, existing=()):
    """Regenerated on every build from every adjacent pair of cached releases (never appended, never a release against itself)."""
    rows = list(existing) if M("g9_append") else []
    ordered = sorted(rels, key=lambda r: r.key)
    pairs = list(zip(ordered[:-1], ordered[1:]))
    if M("g9_self_compare"):
        pairs = pairs + [(r, r) for r in ordered]
    for p, n in pairs:
        ip, in_ = widx(window_rows(p, True)), widx(window_rows(n, True))
        for k in sorted(set(ip) & set(in_), key=lambda k: (WINDOW_NAMES.index(k[0]), k[3], k[1], k[2])):
            a, b = ip[k], in_[k]
            ch = (b["_share"] - a["_share"]) if (a["_share"] is not None and b["_share"] is not None) else None
            rows.append({"release_prev": p.key, "release_new": n.key, "window": k[0], "side": k[1], "group": k[2], "basis": k[3], "flow_prev_usd_mn": a["flow_usd_mn"],
                         "flow_new_usd_mn": b["flow_usd_mn"], "share_prev_pct": a["share_of_total_pct"], "share_new_pct": b["share_of_total_pct"], "change_pp": pct(ch)})
    return rows


# ---- registered statements (4.6) ----
STATEMENTS = (
    ("SREV", "ins", ("FU543063005.Q", "FU513063005.Q")),
    ("SREV-F", "funds", ("FU653063005.Q", "FU553063003.Q", "FU563063003.Q", "FU463063005.Q")),
    ("SREV-R", "row", ("FU263063005.Q",)),
)
PREREG_DEN_TRUE = "FU893063005.Q"
PREREG_WINDOW = ("2024:Q1", "2026:Q2")
PREREG_BASE = PIN_RELEASE
THRESHOLD_PP = Decimal("2.0")
NEW_QUARTER = "2026:Q3"


def prereg_text():
    """The canonical text of 4.6, rebuilt from this script's own constants. The sha256 of this text must equal SPEC_PREREG_SHA256 (C11)."""
    lines = []
    for sid, grp, nums in STATEMENTS:
        nums = tuple(n for n in nums if not (M("g10_funds_no_interval") and n == "FU463063005.Q"))
        lines.append("|".join([sid, "group=%s" % grp, "num=%s" % "+".join(nums), "den=%s" % ("FU893063006.Q" if M("g10_const_edit") else PREREG_DEN_TRUE), "window=%s..%s" % PREREG_WINDOW, "basis=fu", "base=%s" % PREREG_BASE,
                               "new=first_release_with_2026:Q3", "STABLE=abs_delta<%spp" % THRESHOLD_PP, "MOVED=abs_delta>=%spp" % THRESHOLD_PP, "PENDING=no_new_release",
                               "compare=unrounded_decimal_prec28"]))
    return "\n".join(lines) + "\n"


def prereg_ok():
    return sha256_of(prereg_text().encode("utf-8")) == SPEC_PREREG_SHA256


def registered_label(delta):
    """STABLE below the threshold, MOVED at or above it, on the unrounded Decimal (R8)."""
    d = delta.quantize(Decimal("0.001"), rounding=decimal.ROUND_HALF_EVEN) if M("g10_round_before_compare") else delta
    if M("g10_equal_stable"):
        return "STABLE" if d <= THRESHOLD_PP else "MOVED"
    return "STABLE" if d < THRESHOLD_PP else "MOVED"


def prereg_share(rel, nums):
    qs = qrange(*PREREG_WINDOW)
    if not all(q in rel.qset for q in qs):
        return None
    num = [rel.q(c, q) for c in nums for q in qs]
    den = [rel.q(PREREG_DEN_TRUE, q) for q in qs]
    if None in num or None in den:
        return None
    d = dsum(den)
    return ratio_pct(dsum(num), d) if d != 0 else None


def registered_rows(rels):
    if not prereg_ok():
        raise DataError("the statement constants do not reproduce the canonical text of 4.6 (sha256 mismatch): registered.csv is not written")
    by = {r.key: r for r in rels}
    base = by.get(PREREG_BASE)
    if base is None:
        raise DataError("the base release %s is not cached: registered.csv cannot be written" % PREREG_BASE)
    new = None
    for r in sorted(rels, key=lambda r: r.key):
        if r.key > PREREG_BASE and NEW_QUARTER in r.qset:
            new = r
            break
    if new is None and M("g10_score_on_base_only"):
        new = base
    rows = []
    for sid, grp, nums in STATEMENTS:
        nums = tuple(n for n in nums if not (M("g10_funds_no_interval") and n == "FU463063005.Q"))
        sb = prereg_share(base, nums)
        if new is None:
            rows.append([sid, grp, "wave", "fu", PREREG_BASE, "", pct(sb), "", "", fdec(THRESHOLD_PP, 3), "PENDING"])
            continue
        sn = prereg_share(new, nums)
        if sb is None or sn is None:
            raise DataError("%s: a share could not be computed" % sid)
        delta = abs(sn - sb)
        rows.append([sid, grp, "wave", "fu", PREREG_BASE, new.key, pct(sb), pct(sn), pct(delta), fdec(THRESHOLD_PP, 3), registered_label(delta)])
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# allowlists, wording, leak and tamper guards (sections 5, 6, 7; G12-G14, G17)
# ------------------------------------------------------------------------------------------------------------------------
def allowlist(name):
    cols = list(ALLOW[name])
    if M("g12_allow_drift") and name == "windows.csv":
        cols[cols.index("share_of_total_pct")] = "share_of_net_pct"
    return cols


def allow_text():
    return "".join("%s:%s\n" % (n, ",".join(allowlist(n))) for n in ALLOW_ORDER)


def allow_hash_ok():
    return sha256_of(allow_text().encode("utf-8")) == SPEC_ALLOW_SHA256


def check_header(name, header):
    allow = allowlist(name)
    if M("g12_extra_col_ok"):
        ok = list(header[:len(allow)]) == allow
    elif M("g12_renamed_ok"):
        ok = len(header) == len(allow)
    else:
        ok = list(header) == allow
    if not ok:
        raise DataError("%s: header %r is not the exact column allowlist" % (name, list(header)))


def csv_body(text):
    """(header, rows) of a committed csv text, skipping every `# source:` line (the mutant reads the source line as the header)."""
    lines = text.splitlines()
    if not M("g12_source_as_header"):
        lines = [l for l in lines if not l.startswith("# source:")]
    rd = list(csv.reader(lines))
    return (rd[0], rd[1:]) if rd else ([], [])


def strip_exempt(text, readme=True):
    """Remove the one denial sentence (README only), once."""
    if not readme:
        return text
    if M("g14_denial_all"):
        return re.sub(r"[^.;]*\bwho\s+bought\b[^.]*\.", "", text)
    if M("g14_denial_loose"):
        return text.replace(DENIAL_SENTENCE, "")
    return text.replace(DENIAL_SENTENCE, "", 1)


def wording_problems(name, text):
    t = strip_exempt(text, readme=name == "README.md")
    out = []
    if not M("g14_causal_off"):
        out += ["causal wording %r" % re.sub(r"\s+", " ", m.group(0).lower()) for m in CAUSAL_RX.finditer(t)]
    if not M("g14_extra_off"):
        out += ["flow, sale, demand or motive wording %r" % re.sub(r"\s+", " ", m.group(0).lower()) for m in EXTRA_RX.finditer(t)]
    return out


def verdict_problems(files):
    out = []
    for n in sorted(files):
        t = files[n] if isinstance(files[n], str) else files[n].decode("utf-8", errors="replace")
        if VERDICT_RX.search(t):
            out.append("%s holds a verdict word (R1-1)" % n)
    return out


def guard_text(name, text):
    probs = wording_problems(name, text) if name != "SOURCES.md" else []
    probs += ["verdict word %s" % m for m in sorted(set(VERDICT_RX.findall(text)))]
    if probs:
        raise DataError("%s: %s" % (name, "; ".join(sorted(set(probs))[:4])))
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
        cells = [r[h] for h in header] if isinstance(r, dict) else list(r)
        if len(cells) != len(header):
            raise DataError("%s: a row has %d cells, the header %d" % (name, len(cells), len(header)))
        w.writerow(cells)
    text = out.getvalue()
    if not text.startswith("# source:"):
        raise DataError("%s: the first line is not a `# source:` line" % name)
    guard_text(name, text)
    return text


def cusip_ok(s):
    total = 0
    for i, ch in enumerate(s[:8]):
        v = int(ch) if ch.isdigit() else ord(ch) - 55
        if i % 2 == 1:
            v *= 2
        total += v // 10 + v % 10
    return (10 - total % 10) % 10 == int(s[8])


CUSIP_RX = re.compile(r"\b[0-9]{3}[0-9A-Z]{5}[0-9]\b")


def leak_problems(files):
    """Section 6: only the fourteen committed names; no zip, json, html or STOP file; no CUSIP-shaped token; no local path; no at sign."""
    out = []
    for n in sorted(files):
        raw = files[n] if isinstance(files[n], bytes) else files[n].encode("utf-8")
        text = raw.decode("utf-8", errors="replace")
        low = n.lower()
        rawfile = low.endswith((".zip", ".html", ".htm", ".gz", ".pdf")) or raw[:2] == b"PK" or raw[:4] == b"%PDF" or n.upper().startswith("STOP")
        if low.endswith(".json") and not M("g13_json_ok"):
            rawfile = True
        if low.endswith(".zip") and M("g13_zip_ok"):
            rawfile = False
        if rawfile:
            out.append("raw or forbidden file in the committed folder: %s" % n)
            continue
        if n not in COMMITTED and n != ".DS_Store" and not M("g12_thirteenth_csv_ok"):
            out.append("file that is not one of the fourteen committed names: %s" % n)
        if not M("g13_cusip_off"):
            for tok in sorted(set(CUSIP_RX.findall(text))):
                if cusip_ok(tok):
                    out.append("a CUSIP-shaped token in %s" % n)
                    break
        if not M("g13_path_ok") and any(p in text for p in ("/Users/", "/private/", "~/")):
            out.append("a local path in %s" % n)
        if "@" in text:
            out.append("an at sign in %s" % n)
    for n in sorted(set(COMMITTED) - set(files)):
        out.append("missing: %s" % n)
    return out


def header_problems(files):
    out = []
    for n in ALLOW_ORDER:
        if n in files:
            try:
                check_header(n, csv_body(files[n])[0])
            except DataError as e:
                out.append(str(e))
    return out


def dup_key_problems(files):
    out = []
    for n, ks in KEYS.items():
        if n not in files:
            continue
        h, rows = csv_body(files[n])
        if list(h) != ALLOW[n]:
            continue
        idx = [h.index(k) for k in ks]
        seen = set()
        for r in rows:
            k = tuple(r[i] for i in idx)
            if k in seen and not M("g12_dup_key_ok"):
                out.append("duplicate key in %s: %s" % (n, "|".join(k)))
            seen.add(k)
    return out


def value_problems(files):
    """Allowed values (section 5): every constrained column holds only its listed values; `none` only in quarterly.csv and levels.csv."""
    out = []
    allowed = {k: set(v) for k, v in ALLOWED_VALUES.items()}
    if M("g12_fl_book"):
        allowed["valuation"].add("fl_book")
    for n in ALLOW_ORDER:
        if n not in files:
            continue
        h, rows = csv_body(files[n])
        if list(h) != ALLOW[n]:
            continue
        for col in h:
            if col in allowed and not (col == "status" and n != "checks.csv"):
                i = h.index(col)
                bad = sorted({r[i] for r in rows if r[i] not in allowed[col] and r[i] != ""})
                if col == "group" and n not in NONE_GROUP_FILES and any(r[i] == "none" for r in rows):
                    bad.append("none")
                if bad:
                    out.append("%s: column %s holds %s" % (n, col, ", ".join(bad[:4])))
    return out


def _dec(s):
    try:
        return Decimal(s)
    except (decimal.InvalidOperation, TypeError):
        return None


def tamper_problems(files):
    """C13 on the committed text: per window, basis and side the group shares of the net sum to 100 (within 0.01), the shares of the positive flows sum to 100 over the
    groups with a positive flow, ins = ins_life + ins_pc and ins_life = GA + SA (within 0.002 $mn); every `wave` row has n_quarters = 10 (M26 holds its own copy)."""
    out = []
    if "windows.csv" not in files:
        return out
    h, rows = csv_body(files["windows.csv"])
    if list(h) != ALLOW["windows.csv"]:
        return out
    ix = {c: h.index(c) for c in h}
    sets = collections.OrderedDict()
    flows = {}
    for r in rows:
        k = (r[ix["release"]], r[ix["window"]], r[ix["basis"]], r[ix["side"]])
        flows[k + (r[ix["group"]],)] = _dec(r[ix["flow_usd_mn"]])
        if r[ix["window"]] == "wave" and r[ix["n_quarters"]] != "10":
            out.append("wave row of %s has n_quarters %s, not 10" % (r[ix["release"]], r[ix["n_quarters"]]))
        if r[ix["role"]] in ("holder", "issuer"):
            sets.setdefault(k, []).append(r)
    for k, rs in sets.items():
        sh = [_dec(r[ix["share_of_total_pct"]]) for r in rs if r[ix["share_of_total_pct"]] != ""]
        if sh and abs(sum(sh) - 100) > Decimal("0.01"):
            out.append("%s: the group shares of the net sum to %s, not 100" % ("|".join(k), fdec(sum(sh), 3)))
        ps = [_dec(r[ix["share_of_positive_pct"]]) for r in rs if r[ix["share_of_positive_pct"]] != ""]
        pos_groups = [r for r in rs if _dec(r[ix["flow_usd_mn"]]) is not None and _dec(r[ix["flow_usd_mn"]]) > 0]
        if pos_groups and ps and abs(sum(ps) - 100) > Decimal("0.01"):
            out.append("%s: the shares of the positive flows sum to %s, not 100" % ("|".join(k), fdec(sum(ps), 3)))
        if len(ps) != len(pos_groups):
            out.append("%s: a share of the positive flows is missing or written for a flow that is not positive" % "|".join(k))
    for k in {kk[:4] for kk in flows}:
        g = lambda name: flows.get(k + (name,))
        if k[3] == "holder":
            a, b, c = g("ins"), g("ins_life"), g("ins_pc")
            if None not in (a, b, c) and abs(a - (b + c)) > Decimal("0.002"):
                out.append("%s: ins is not ins_life + ins_pc" % "|".join(k))
            a, b, c = g("ins_life"), g("ins_life_ga"), g("ins_life_sa")
            if None not in (a, b, c) and abs(a - (b + c)) > Decimal("0.002"):
                out.append("%s: ins_life is not general + separate accounts" % "|".join(k))
    return out


TIC_CONSTS = ("304.5", "392.4")
TIC_WORDS = re.compile(r"\bTIC\b|Treasury|sb0662", re.I)


def pairing_problems(files):
    """R10, G17: the typed TIC constants of CREF2 appear in checks.csv and nowhere else among the committed files. A hit is a line that names TIC, Treasury or sb0662 beside a
    constant, or (in a CSV) a cell that is exactly the constant at one decimal; a Z.1 figure that happens to print the same digits is not a hit."""
    out = []
    for n, t in sorted(files.items()):
        if n == "checks.csv" or not isinstance(t, str) or M("g17_tic_everywhere_ok"):
            continue
        hit = False
        for line in t.splitlines():
            if TIC_WORDS.search(line) and any(re.search(r"(?<![\d.])%s(?!\d)" % re.escape(c), line) for c in TIC_CONSTS):
                hit = True
        if n.endswith(".csv"):
            for row in csv.reader(l for l in t.splitlines() if not l.startswith("# source:")):
                if any(c in TIC_CONSTS for c in row):
                    hit = True
        if hit:
            out.append("%s holds a figure from another source (a typed TIC constant)" % n)
    return out


def label_problems(files):
    out = []
    if "registered.csv" in files:
        h, rows = csv_body(files["registered.csv"])
        if list(h) == ALLOW["registered.csv"]:
            i = h.index("label")
            bad = sorted({r[i] for r in rows if r[i] not in ("STABLE", "MOVED", "PENDING")})
            if bad:
                out.append("registered.csv labels outside STABLE, MOVED, PENDING: %s" % ", ".join(bad))
    return out


def all_folder_problems(files):
    out = leak_problems(files) + header_problems(files) + dup_key_problems(files) + value_problems(files) + tamper_problems(files) + pairing_problems(files)
    out += verdict_problems(files) + label_problems(files)
    for n, t in files.items():
        if n.endswith((".csv", ".md")) and isinstance(t, str) and n != "SOURCES.md":
            out += ["%s: %s" % (n, p) for p in sorted(set(wording_problems(n, t)))]
    return out


def checksh_problems(text):
    """G12: the M26 guard in bin/check.sh holds its own literal copy of the twelve canonical lines and never reads them from this script."""
    a = text.find("z1cb_leak_check() {")
    if a < 0:
        return ["bin/check.sh has no z1cb_leak_check function"]
    region = text[a:text.find("\n}\n", a) + 3]
    out = []
    for l in SPEC_ALLOW_TEXT.splitlines():
        name, hdr = l.split(":", 1)
        if ("%s) want='%s'" % (name, hdr)) not in region:
            out.append("check.sh does not hold the literal header of %s" % name)
    if re.search(r"z1_corporate_bond_holders\.py", region) and not M("g12_checksh_reads_script"):
        out.append("check.sh names the script inside the guard (it must not read the headers from it)")
    return out


# ------------------------------------------------------------------------------------------------------------------------
# pinned and structural checks (section 8)
# ------------------------------------------------------------------------------------------------------------------------
def chk(cid, desc, expected, observed, status):
    return [cid, desc, expected, observed, status]


RANK = {"PASS": 0, "INFO": 0, "WARN": 1, "FAIL": 2}


def worst(statuses):
    s = [x for x in statuses if x in RANK]
    return max(s, key=lambda x: RANK[x]) if s else "PASS"


def pin_status(rel, bad):
    """Pins on the 20260911 release FAIL on that release and WARN on a later one (section 8)."""
    if not bad:
        return "PASS"
    return "FAIL" if rel.key == PIN_RELEASE else "WARN"


def fmt_int(v):
    return "{:,}".format(int(v))


def per_release(rels, fn):
    """Run a per-release check; fn(rel) -> (status, expected, observed). Returns (status, expected, observed) merged across releases."""
    res = [(r.key,) + tuple(fn(r)) for r in rels]
    res = [x for x in res if x[1] is not None]
    if not res:
        return None
    st = worst([x[1] for x in res])
    exp = res[0][2]
    obs = "; ".join("%s: %s" % (k, o) for k, _, _, o in res)
    return st, exp, obs


def c01(rel):
    if rel.key != PIN_RELEASE:
        return None, "", ""
    z = rel.zip_row()
    mem = {r["name"]: r for r in rel.prov if r.get("kind") == "member"}
    got = {"sha256": z.get("sha256", ""), "bytes": z.get("bytes", ""), "last_modified": z.get("last_modified", ""), "members": z.get("members", "")}
    bad = []
    if got["sha256"] != PIN_ZIP["sha256"]:
        bad.append("zip sha256")
    if got["bytes"] != str(PIN_ZIP["bytes"]):
        bad.append("zip bytes")
    if got["last_modified"] != PIN_ZIP["last_modified"]:
        bad.append("Last-Modified")
    if got["members"] != str(PIN_ZIP["members"]):
        bad.append("member count")
    for n, b in PIN_MEMBER_BYTES.items():
        if mem.get(n, {}).get("bytes") != str(b):
            bad.append("%s bytes" % n)
    exp = "zip sha256 %s, %s bytes, Last-Modified %s, %d members; %s" % (PIN_ZIP["sha256"], fmt_int(PIN_ZIP["bytes"]), PIN_ZIP["last_modified"], PIN_ZIP["members"],
                                                                         ", ".join("%s %s bytes" % (n[:-4], fmt_int(b)) for n, b in PIN_MEMBER_BYTES.items()))
    obs = "zip sha256 %s, %s bytes, Last-Modified %s, %s members; %s" % (got["sha256"], fmt_int(got["bytes"] or 0), got["last_modified"], got["members"],
                                                                         ", ".join("%s %s bytes" % (n[:-4], fmt_int(mem.get(n, {}).get("bytes") or 0)) for n in PIN_MEMBER_BYTES))
    if bad:
        obs += " | differs: " + ", ".join(bad)
    return pin_status(rel, bad), exp, obs


def is_quarter_step(a, b):
    return qidx(b) == qidx(a) + 1


def c02(rel):
    t, tf, ts = rel.tables["F3_5_t_tu"], rel.tables["F3_5_t"], rel.tables["F3_5_s"]
    bad = []
    if (t.n_codes(), tf.n_codes(), ts.n_codes()) != (53, 53, 54):
        bad.append("series columns %d/%d/%d, not 53/53/54" % (t.n_codes(), tf.n_codes(), ts.n_codes()))
    for tb in (t, tf, ts):
        if not tb.quarters or tb.quarters[0] != "1945:Q4":
            bad.append("%s starts at %s" % (tb.name, tb.quarters[0] if tb.quarters else "nothing"))
        qs = tb.quarters
        for a, b in zip(qs, qs[1:]):
            if b >= "1952:Q1" and not is_quarter_step(a, b):
                bad.append("%s: a gap between %s and %s" % (tb.name, a, b))
                break
        if tb.quarters != t.quarters:
            bad.append("%s carries different dates from F3_5_t_tu" % tb.name)
    for b in REQUIRED_CSV[3:]:
        if rel.tables[b].quarters != t.quarters:
            bad.append("%s carries different dates from F3_5_t_tu" % b)
    obs = "F3_5_t_tu %d series columns, F3_5_t %d, F3_5_s %d; %d data rows from %s to %s" % (t.n_codes(), tf.n_codes(), ts.n_codes(), len(t.quarters), t.quarters[0], t.quarters[-1])
    exp = "53, 53 and 54 series columns; data rows from 1945:Q4, contiguous quarters from 1952:Q1, the same dates in all seven files"
    if rel.key == PIN_RELEASE:
        exp += "; 305 rows ending 2026:Q2"
        if len(t.quarters) != 305 or t.quarters[-1] != "2026:Q2":
            bad.append("%d rows ending %s, not 305 ending 2026:Q2" % (len(t.quarters), t.quarters[-1]))
    return ("FAIL" if bad else "PASS"), exp, obs + ((" | " + "; ".join(bad[:4])) if bad else "")


def dict_for(rel, code):
    return rel.dicts.get(FILE_OF[code], {}).get(code)


def c03(rel):
    bad = []
    n = 0
    for l in LINES:
        for code, kind in ((l.fu, "t"), (l.fa, "t"), (l.lvl, "s")):
            if not code:
                continue
            n += 1
            d = dict_for(rel, code)
            if d is None:
                bad.append("%s: not in its dictionary" % code)
                continue
            desc, line_txt, tab_txt = d
            if line_txt != "Line %d" % l.line:
                bad.append("%s: dictionary says %r, spec line %d" % (code, line_txt, l.line))
            mark = ("f3.5.%s" % kind) if l.table == "F3.5" else ("%s.%s" % (S1281_TABLE_MARK[l.table], kind))
            if mark not in tab_txt.lower():
                bad.append("%s: table text %r lacks %s" % (code, tab_txt[:40], mark))
            if not all(k in desc.lower() for k in l.keys):
                bad.append("%s: text %r lacks %s" % (code, desc[:50], "/".join(l.keys)))
    exp = "all %d codes of 2.2 on the stated line and table, text containing the sector name" % n
    return ("FAIL" if bad else "PASS"), exp, ("%d mismatch(es): %s" % (len(bad), " | ".join(bad[:5]))) if bad else "%d codes match" % n


def flow_identity_defs(basis):
    L = BYLINE
    details = [l for l in ISS_DETAILS if not (M("g2_line8_missing") and l.line == 8)]
    defs = [("the 28 leaves = line 13", LEAVES, [L[13]]), ("line 1 = line 13", [L[1]], [L[13]]), ("lines 2+3+12 = line 1", [L[2], L[3], L[12]], [L[1]]),
            ("lines 4-11 = line 3", details, [L[3]])]
    for p, a, b in ((19, 20, 21), (24, 25, 26), (27, 28, 29), (30, 31, 32), (43, 44, 45), (51, 52, 53)):
        defs.append(("line %d = %d + %d" % (p, a, b), [L[p]], [L[a], L[b]]))
    if basis == "fu" and not M("g3_ga_sa_skipped"):
        defs.append(("general + separate accounts = line 30", [GA, SA], [L[30]]))
    return defs


def flow_identity_residuals(rel, basis):
    out = []
    for q in [q for q in rel.quarters if q >= "1990:Q1"]:
        for name, lhs, rhs in flow_identity_defs(basis):
            a = [flow(rel, basis, l, q) for l in lhs]
            b = [flow(rel, basis, l, q) for l in rhs]
            out.append((q, name, None if (None in a or None in b) else dsum(a) - dsum(b)))
    return out


def id_status(res, tol):
    new = [x for x in res if x[0] >= "2017:Q1" and (x[2] is None or abs(x[2]) > tol)]
    old = [x for x in res if x[0] < "2017:Q1" and (x[2] is None or abs(x[2]) > tol)]
    if M("g3_pre2017_fail"):
        new = new + old
    return "FAIL" if new else ("WARN" if old else "PASS")


def id_summary(res):
    def mx(sel):
        v = [abs(x[2]) for x in res if sel(x[0]) and x[2] is not None]
        return fmt_int(max(v)) if v else "none"
    nn = sum(1 for x in res if x[2] is None)
    return "max |residual| %s $mn from 2017:Q1, %s $mn before%s" % (mx(lambda q: q >= "2017:Q1"), mx(lambda q: q < "2017:Q1"), ("; %d not evaluable" % nn) if nn else "")


def worst_items(res, tol, k=3):
    bad = [x for x in res if x[2] is None or abs(x[2]) > tol]
    bad.sort(key=lambda x: (-abs(x[2]) if x[2] is not None else -10 ** 18, x[0], x[1]))
    return "; ".join("%s %s %s" % (q, nm, "n/a" if r is None else fmt_int(r)) for q, nm, r in bad[:k])


def c04(rel):
    tol = Decimal(10) if M("g3_tol_wide") else Decimal(2)
    sts, obs, bad = [], [], []
    for basis in ("fu", "fa_div4"):
        res = flow_identity_residuals(rel, basis)
        st = id_status(res, tol)
        sts.append(st)
        obs.append("%s: %d identity-quarters, %s" % (basis, len(res), id_summary(res)))
        if st != "PASS":
            bad.append("%s: %s" % (basis, worst_items(res, tol)))
    return worst(sts), "each flow identity within 2 $mn on both bases (FAIL from 2017:Q1, WARN 1990:Q1-2016:Q4)", " | ".join(obs + bad)


def level_identity_residuals(rel):
    out = []
    for q in [q for q in rel.quarters if q >= "1990:Q1"]:
        leaves = [level(rel, l, q) for l in LEAVES]
        l13, l1, l54 = level(rel, BYLINE[13], q), level(rel, BYLINE[1], q), level(rel, BYLINE[54], q)
        if None in leaves or None in (l13, l1, l54):
            out += [(q, "the 28 leaves = line 13", None), (q, "line 54 = line 1 - line 13", None)]
            continue
        s = dsum(leaves)
        if M("g3_level_with_disc"):
            out += [(q, "the 28 leaves = line 13", s + l54 - l13), (q, "line 54 = line 1 - line 13", l54 - (l1 - l13))]
        else:
            out += [(q, "the 28 leaves = line 13", s - l13), (q, "line 54 = line 1 - line 13", l54 - (l1 - l13))]
    return out


LEVEL_PINS = (("2017:Q4", -290252), ("2018:Q4", 357667), ("2019:Q4", -599833))


def c05(rel):
    res = level_identity_residuals(rel)
    st = id_status(res, Decimal(2))
    obs = "%d identity-quarters, %s" % (len(res), id_summary(res))
    sts = [st]
    if st != "PASS":
        obs += " | " + worst_items(res, Decimal(2))
    exp = "28 leaf levels = line 13 and line 54 = line 1 - line 13, each within 2 $mn (FAIL from 2017:Q1, WARN before)"
    if True:
        pins, bad = [], []
        for q, want in LEVEL_PINS:
            a, b = level(rel, BYLINE[1], q), level(rel, BYLINE[13], q)
            v = (a - b) if (a is not None and b is not None) else None
            pins.append("%s %s" % (q, "n/a" if v is None else fmt_int(v)))
            if v is None or abs(v - want) > 1:
                bad.append(q)
        sts.append(pin_status(rel, bad))
        exp += "; line 1 - line 13 = -290,252 (2017:Q4), 357,667 (2018:Q4), -599,833 (2019:Q4)"
        obs += " | line 1 - line 13: " + ", ".join(pins)
    return worst(sts), exp, obs


def c06(rel):
    worst_d, where, n = Decimal(0), "", 0
    bad = []
    years = sorted({int(q[:4]) for q in rel.quarters if q >= "2017:Q1"})
    for y in years:
        qs = qrange("%d:Q1" % y, "%d:Q4" % y)
        if not all(q in rel.qset for q in qs):
            continue
        for l in F35:
            if not l.fa:
                continue
            fa = wsum(rel, "fa_div4", l, qs, "g18_fa_undivided")
            fu = wsum(rel, "fu", l, qs)
            if fa is None or fu is None:
                bad.append((y, l.line))
                continue
            n += 1
            d = abs(fa - fu)
            if d > worst_d:
                worst_d, where = d, "%d line %d" % (y, l.line)
            if d > 4:
                bad.append((y, l.line))
    obs = "%d year-line pairs, max |sum(FA)/4 - sum(FU)| %s $mn (%s)" % (n, fmt_int(worst_d), where or "none")
    return pin_status(rel, bad), "sum(FA)/4 - sum(FU) within 4 $mn for every complete calendar year from 2017 and every line", obs


def c08(rel):
    got = {}
    for w, a, b in window_defs(rel.latest):
        if w in ("wave", "pre1719", "pre2223"):
            got[w] = len(qrange(a, b))
    want = {"wave": 10, "pre1719": 12, "pre2223": 8}
    ok = got == want
    return ("PASS" if ok else "FAIL"), "wave 10, pre1719 12, pre2223 8 quarters", "wave %s, pre1719 %s, pre2223 %s" % (got.get("wave"), got.get("pre1719"), got.get("pre2223"))


def all_codes(rel_only=None):
    for l in LINES:
        for code, lv in ((l.fu, False), (l.fa, False), (l.lvl, True)):
            if code:
                yield code, lv


def c09(rel):
    n, miss = 0, []
    for code, is_lvl in all_codes():
        s = rel.series(code)
        start = "2016:Q4" if is_lvl else "2017:Q1"
        for q in [q for q in rel.quarters if q >= start]:
            n += 1
            if s is None or s.get(q) is None:
                miss.append("%s %s" % (code, q))
    obs = "%d missing of %d cells" % (len(miss), n) + ((" (e.g. %s)" % ", ".join(miss[:3])) if miss else "")
    return ("FAIL" if miss else "PASS"), "no ND or blank in any code of 2.2 from 2017:Q1 (levels from 2016:Q4) to the latest quarter", obs


def c12(rel):
    lm = rel.zip_row().get("last_modified", "")
    try:
        d = dt.datetime.strptime(lm, "%Y-%m-%dT%H:%M:%SZ").date()
        r = dt.datetime.strptime(rel.key, "%Y%m%d").date()
    except ValueError:
        return "FAIL", "release folder date within 3 days of the zip's Last-Modified date", "Last-Modified %r cannot be compared with %s" % (lm, rel.key)
    gap = abs((d - r).days)
    return ("PASS" if gap <= 3 else "FAIL"), "release folder date within 3 days of the zip's Last-Modified date", "folder %s, Last-Modified %s, gap %d days" % (rel.key, lm[:10], gap)


def c15(rel):
    bad = list(rel.problems)
    names = {r["name"] for r in rel.prov if r.get("kind") == "member"}
    for z, cache_name in FIXED_MEMBERS.items():
        if cache_name not in names:
            bad.append("member %s not in provenance.csv" % z)
    for l in LINES:
        for code in (l.fu, l.fa, l.lvl):
            if code and not rel.tables[FILE_OF[code]].has(code):
                bad.append("%s not in the header of %s" % (code, FILE_OF[code]))
    return ("FAIL" if bad else "PASS"), "14 members present; every series code of 2.2 in its file's header; dictionary line and text (C03)", ("%d content failure(s): %s" % (len(bad), " | ".join(bad[:4]))) if bad else "14 members and all 164 header codes present"


def c17(rel, fetch_rows, old_vint):
    bad = []
    z = rel.zip_row()
    for r in rel.prov:
        if r.get("kind") != "member":
            continue
        p = os.path.join(rel.folder or "", r["name"])
        if not os.path.isfile(p):
            bad.append("%s missing" % r["name"])
            continue
        b = read_file(p)
        if sha256_of(b) != r["sha256"] or str(len(b)) != r["bytes"]:
            bad.append("%s differs from provenance.csv" % r["name"])
    path = "/releases/z1/%s/%s" % (rel.key, ZIP_NAME)
    logged = [r for r in fetch_rows if len(r) > 5 and r[2] == path and r[3] == "200"]
    if not logged:
        bad.append("no 200 row for the zip in fetch_log.csv")
    elif logged[-1][5] != z.get("sha256"):
        bad.append("zip sha256 differs from fetch_log.csv")
    old = old_vint.get(rel.key)
    if old is not None and old.get("sha256") != z.get("sha256"):
        bad.append("zip sha256 differs from the committed vintages.csv row")
    return ("FAIL" if bad else "PASS"), "every cached member equals its provenance.csv row; the zip sha256 equals the fetch_log.csv and vintages.csv rows", ("; ".join(bad[:4]) if bad else "%d members and the zip digest agree" % sum(1 for r in rel.prov if r.get("kind") == "member"))


def cref_shares(rel):
    L = BYLINE
    out = {}
    for w, a, b in (("y2024", "2024:Q1", "2024:Q4"), ("y2025", "2025:Q1", "2025:Q4"), ("wave",) + PREREG_WINDOW):
        qs = qrange(a, b)
        life, pc, tot = wsum(rel, "fu", L[30], qs), wsum(rel, "fu", L[27], qs), wsum(rel, "fu", L[13], qs)
        out[w] = (life, pc, tot, ratio_pct(life + pc, tot) if None not in (life, pc, tot) and tot != 0 else None)
    return out


def cref1(rel):
    got = cref_shares(rel)
    bad, obs = [], []
    for w, c in CREF1.items():
        life, pc, tot, sh = got[w]
        if None in (life, pc, tot) or sh is None:
            bad.append(w)
            continue
        obs.append("%s %s%% (%s + %s of %s $mn)" % (w, fdec(sh, 2), fmt_int(life), fmt_int(pc), fmt_int(tot)))
        if abs(sh - c["pct"]) > CREF1_PP_TOL or abs(life - c["life"]) > 1 or abs(pc - c["pc"]) > 1 or abs(tot - c["total"]) > 1:
            bad.append(w)
    sh = got["wave"][3]
    if sh is None:
        bad.append("wave")
    else:
        obs.append("wave %s%% (of %s $mn)" % (fdec(sh, 2), fmt_int(got["wave"][2])))
        if abs(sh - CREF1_WAVE_PCT) > CREF1_PP_TOL:
            bad.append("wave")
    exp = "ins share of the net, fu basis: y2024 37.12% (224,689 + 70,237 of 794,490 $mn), y2025 35.67% (221,483 + 65,834 of 805,405), wave 33.26%, each within 0.005 pp; the six dollar figures within 1 $mn"
    return ("WARN" if bad else "PASS"), exp, "; ".join(obs) + ((" | differs: " + ", ".join(bad)) if bad else "")


def cref2(rel):
    qs24, qs25 = qrange("2024:Q1", "2024:Q4"), qrange("2025:Q1", "2025:Q4")
    L51 = BYLINE[51]
    fa24, fu24, fu25 = wsum(rel, "fa_div4", L51, qs24, "g18_fa_undivided"), wsum(rel, "fu", L51, qs24), wsum(rel, "fu", L51, qs25)
    a_ok = fa24 is not None and fdec(fa24 / 1000, 1) == fdec(GROK_SA_2024_BN, 1)
    a = ("PASS" if a_ok else "WARN", "line 51 net acquisition for y2024 on fa_div4 rounds to 298.8 $bn (the seasonally adjusted figure read on the published table during review)",
         "line 51, y2024, fa_div4: %s $bn (%s $mn)" % (fdec(fa24 / 1000, 1) if fa24 is not None else "n/a", fmt_int(fa24) if fa24 is not None else "n/a"))
    if None in (fu24, fu25):
        b = ("INFO", "reference only", "line 51 not available")
    else:
        g24, g25 = TIC_2024_BN - fu24 / 1000, TIC_2025_BN - fu25 / 1000
        b = ("INFO", "reference only, never a pass or a fail: Treasury TIC press-release figures (release sb0662, typed in, never fetched) for foreign net transactions in US corporate bonds, "
                     "private plus official, 304.5 $bn (2024) and 392.4 $bn (2025), beside the build's line-51 net acquisition on the fu basis; the gap is expected (TIC includes municipal "
                     "bonds) and the two are not independent (the same Federal Reserve Board staff estimates feed both)",
             "line 51 fu: y2024 %s $bn, y2025 %s $bn; TIC minus Z.1: y2024 %s $bn, y2025 %s $bn" % (fdec(fu24 / 1000, 1), fdec(fu25 / 1000, 1), fdec(g24, 1), fdec(g25, 1)))
    return a, b


def merge(rels, fn, cid, desc):
    """Run fn(rel) -> (status, expected, observed) over releases (a status of None skips the release) and merge into one checks.csv row."""
    res = []
    for r in rels:
        s, e, o = fn(r)
        if s is not None:
            res.append((r.key, s, e, o))
    if not res:
        return None
    return chk(cid, desc, res[0][2], "; ".join("%s: %s" % (k, o) for k, _, _, o in res), worst([x[1] for x in res]))


CHECK_ORDER = ["C01", "C02", "C03", "C04", "C05", "C06", "C08", "C09", "C10", "C11", "C12", "C13", "C15", "C17", "CREF1", "CREF2a", "CREF2b"]


def build_checks(rels, fetch_rows, old_vint, texts, texts_again):
    """texts: the rendered data files; texts_again: a second, independent render (C10)."""
    rows = []
    for cid, fn, desc in (
            ("C01", c01, "Release file of 20260911: zip digest, size, Last-Modified, member count and the three table sizes (a pin: FAIL on that release, WARN on a later one)"),
            ("C02", c02, "Shape: 53, 53 and 54 series columns; data rows from 1945:Q4; contiguous quarters; the same dates in all seven files"),
            ("C03", c03, "Dictionary: every code of 2.2 sits on the stated line and table and its dictionary text contains the sector name (a renumbered line is a FAIL, never followed)"),
            ("C04", c04, "Flow identities of 2.3 on both bases, each within 2 $mn: FAIL from 2017:Q1, WARN 1990:Q1-2016:Q4"),
            ("C05", c05, "Level identities of 2.3 (28 leaf levels = line 13; line 54 = line 1 - line 13) and the pinned differences of line 1 and line 13: FAIL from 2017:Q1, WARN before"),
            ("C06", c06, "Annual bases: sum(FA)/4 minus sum(FU) within 4 $mn on every line and complete calendar year from 2017 (FAIL on 20260911, WARN on a later release)"),
            ("C08", c08, "Window lengths: wave 10, pre1719 12, pre2223 8 quarters"),
            ("C09", c09, "No missing cells: no ND or blank in any code of 2.2, 2017:Q1 to the latest quarter"),
            ("C12", c12, "Release key: the dated folder of the zip URL is within 3 days of the zip's Last-Modified date")):
        r = merge(rels, fn, cid, desc)
        if r:
            rows.append(r)
    same = {n: sha256_of(x.encode("utf-8")) for n, x in texts.items()} == {n: sha256_of(x.encode("utf-8")) for n, x in texts_again.items()}
    rows.append(chk("C10", "Fixed output: a second, independent compute and render over the same cache leaves the sha256 of every output but checks.csv unchanged (a rerun of build must too)",
                    "identical", "identical (%d files)" % len(texts) if same else "DIFFERENT", "PASS" if same else "FAIL"))
    ok = prereg_ok()
    rows.append(chk("C11", "Statement hash: the script's constants reproduce the canonical text of 4.6 byte for byte (FAIL blocks registered.csv)", SPEC_PREREG_SHA256,
                    sha256_of(prereg_text().encode("utf-8")), "PASS" if ok else "FAIL"))
    probs = tamper_problems(texts)
    rows.append(chk("C13", "Tamper: per window, basis and side the nine holder (three issuer) group shares of the net sum to 100 within 0.01, the positive shares sum to 100 over the groups with a "
                           "positive flow, ins = ins_life + ins_pc and ins_life = general + separate accounts within 0.002 $mn", "no problem",
                    "; ".join(probs[:3]) if probs else "no problem", "FAIL" if probs else "PASS"))
    rows.append(merge(rels, c15, "C15", "Content tests (R3b): 14 members, every series code in its file's header, the dictionary text of C03"))
    r17 = merge(rels, lambda r: c17(r, fetch_rows, old_vint), "C17", "Cache integrity: every cached member equals its provenance.csv row and the zip digest equals the fetch_log.csv and vintages.csv rows")
    rows.append(r17)
    pin = [r for r in rels if r.key == PIN_RELEASE]
    if pin:
        st, e, o = cref1(pin[0])
        rows.append(chk("CREF1", "Review-derived values (WARN, 20260911 only): insurers' share of the net on the fu basis for y2024, y2025 and the wave window, with their dollar figures; a WARN is "
                                 "reported to the supervisor and the constant is never edited", e, o, st))
        a, b = cref2(pin[0])
        rows.append(chk("CREF2a", "Reference (WARN): the rest-of-world line-51 net acquisition for y2024 on the fa_div4 basis against the figure read on the published seasonally adjusted table "
                                  "during review", a[1], a[2], a[0]))
        rows.append(chk("CREF2b", "Reference (INFO): typed Treasury TIC figures beside the build's rest-of-world line 51", b[1], b[2], b[0]))
    return sorted(rows, key=lambda r: CHECK_ORDER.index(r[0]))


# ------------------------------------------------------------------------------------------------------------------------
# README.md and SOURCES.md (generated, so the wording guards scan the README)
# ------------------------------------------------------------------------------------------------------------------------
NAMES = {
    "total": "All holders (line 13)", "ins": "US insurers (life and property-casualty)", "pen": "Pension funds", "funds": "Registered funds", "row": "Rest of the world",
    "banks": "Banks and credit unions", "hh_residual": "Households and nonprofits (residual)", "private_funds": "Hedge funds and private debt funds",
    "gse_bd": "Government-sponsored enterprises and security brokers and dealers", "other": "Other holders",
    "ins_life": "Life insurers", "ins_pc": "Property-casualty insurers", "ins_life_ga": "of which life insurers' general accounts", "ins_life_sa": "of which life insurers' separate accounts",
    "pen_private": "Private pension funds", "pen_federal": "Federal government pension funds", "pen_sl": "State and local pension funds",
    "funds_mutual": "Mutual funds", "funds_cef": "Closed-end funds", "funds_etf": "Exchange-traded funds", "funds_interval": "Interval and tender-offer funds",
    "hedge_funds": "Hedge funds (domestic)", "private_debt_funds": "Private debt funds", HHPF: "Households plus hedge funds plus private debt funds (derived)",
    "iss_total": "All issuers (line 1)", "iss_nfc": "Nonfinancial corporate business", "iss_domfin": "Domestic financial sectors", "iss_row": "Rest of the world (foreign bonds US residents acquired)",
    "iss_dom_banks": "of which US-chartered depository institutions", "iss_dom_abs": "of which issuers of asset-backed securities", "iss_dom_finco": "of which finance companies",
    "iss_dom_mreit": "of which mortgage REITs", "iss_dom_bdc": "of which business development companies", "iss_dom_bd": "of which security brokers and dealers",
    "iss_dom_hc": "of which holding companies", "iss_dom_ofb": "of which other financial business",
}
SHORT = {"ins": "Insurers", "pen": "Pensions", "funds": "Registered funds", "row": "Rest of the world", "banks": "Banks", "hh_residual": "Households (residual)",
         "private_funds": "Hedge and private debt funds", "gse_bd": "GSEs and dealers", "other": "Other"}
ORDINAL = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth", 7: "seventh"}
WIN_LABEL = {"wave": "2024Q1-2026Q2", "pre1719": "2017Q1-2019Q4", "pre2223": "2022Q1-2023Q4", "y2026h1": "2026H1"}


def wl(w):
    if w in WIN_LABEL:
        return WIN_LABEL[w]
    return w[1:] if w.startswith("y") else w


def thousands(v, nd):
    return format(Decimal(v).quantize(Decimal(1).scaleb(-nd), rounding=decimal.ROUND_HALF_EVEN), ",.%df" % nd)


def bn(v, nd=1):
    """Millions of dollars as '$741.2bn' (with a minus sign in front of the dollar sign when negative). None is 'n/a'."""
    if v is None:
        return "n/a"
    x = Decimal(v) / 1000
    s = thousands(abs(x), nd)
    return ("-" if Decimal(thousands(x, nd).replace(",", "")) < 0 else "") + "$" + s + "bn"


def pctx(v, nd=2):
    return "n/a" if v is None else thousands(v, nd) + "%"


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(" --- " for _ in head) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out) + "\n"


def wrow(ix, w, side, g, basis="fu"):
    return ix.get((w, side, g, basis))


def join_names(names):
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


def rank_info(ix):
    """(rank of ins among the seven, the groups ranked above it in order) from the fu wave flows."""
    flows = {g: wrow(ix, "wave", "holder", g)["_flow"] for g in RANKED7 if wrow(ix, "wave", "holder", g)}
    rk = 1 + sum(1 for h in flows if flows[h] > flows["ins"])
    ahead = sorted((h for h in flows if flows[h] > flows["ins"]), key=lambda h: -flows[h])
    return rk, ahead, flows


def readme_cell(r, key_share="_share"):
    if r is None or r["_flow"] is None:
        return "n/a"
    return "%s (%s)" % (pctx(r[key_share], 1) if r[key_share] is not None else "n/a", thousands(r["_flow"] / 1000, 1))


def render_readme(c):
    rels = c["rels"]
    rel = rels[-1]
    ix = c["ix"][rel.key]
    ins = wrow(ix, "wave", "holder", "ins")
    tot = wrow(ix, "wave", "holder", "total")
    rk, ahead, _ = rank_info(ix)
    behind = ("behind " + join_names([NAMES[h].lower().split(" (")[0] if h != "row" else "the rest of the world" for h in ahead])) if ahead else "ahead of all six other groups"
    L = []
    A = L.append
    A("# US corporate and foreign bonds: which holders took the net increase, 2024Q1-2026Q2 (Federal Reserve Z.1, table F3.5)\n")
    A("This folder shows which kinds of holders took the net increase in US corporate and foreign bonds from 2024Q1 to 2026Q2, in the Federal Reserve's financial accounts "
      "(Z.1 table F3.5, release %s). US insurers (life and property-casualty) took %s of the all-sector net, %s of %s (unadjusted basis, 2024Q1-2026Q2), "
      "ranking %s of seven holder groups, %s.\n" % (rel.key, pctx(ins["_share"]), bn(ins["_flow"]), bn(tot["_flow"]), ORDINAL[rk], behind))
    A(DENIAL_SENTENCE + "\n")
    A("%s Three statements about how the shares move when the next release arrives are registered in advance: the insurer, registered-fund and rest-of-the-world shares "
      "of the 2024Q1-2026Q2 net each move by less than 2.0 percentage points between the 11 Sep 2026 and the 10 Dec 2026 releases. They are scored on the 10 Dec 2026 release "
      "and read PENDING until it is cached; see \"Revisions and the registered statements\" below.\n" % DISCLOSURE_SENTENCE)

    # ---- 4: issuance first
    A("## What the net was made of, before any holder\n")
    A("Net issuance is new bonds issued minus redemptions. Over 2024Q1-2026Q2 (10 quarters, unadjusted), by issuer sector; the denominator of every share is the all-sector net of %s "
      "(line 1 of the table).\n" % bn(wrow(ix, "wave", "issuer", "iss_total")["_flow"]))
    rows = []
    for g, role in issuer_order():
        r = wrow(ix, "wave", "issuer", g)
        if r:
            rows.append([NAMES[g], bn(r["_flow"]), bn(r["_flow"] / 10), pctx(r["_share"]) if r["_share"] is not None else "n/a"])
    A(md_table(["Issuer sector", "Net issuance", "Per-quarter average", "Share of the net"], rows))
    A("The instrument is all corporate and foreign bonds: investment grade and high yield, financial issuers, private-label ABS and MBS, and foreign bonds held by US residents. "
      "Z.1 has no line for the AI issuers, so this table cannot say who took their bonds. For context only, the BIS Quarterly Review of 16 March 2026 reports that hyperscalers' "
      "gross bond issuance was \"topping $100 billion in 2025\"; that is gross issuance by five firms, so it is not comparable with a net figure and no ratio is computed here.\n")

    # ---- 5: holders
    A("## The holders, 2024Q1-2026Q2\n")
    A("Net acquisition is purchases minus sales and redemptions over the period. The denominator of the share of the net is the all-sector net of %s (line 13); the denominator of the share "
      "of the positive flows is %s, the sum of the positive net acquisitions of the nine groups. The offset ratio (the all-sector net divided by the sum of the absolute net acquisitions "
      "of the 28 holder lines) is %s, so the stability flag is \"%s\".\n" % (bn(tot["_flow"]), bn(Decimal(tot["positive_total_usd_mn"])),
                                                                          tot["offset_ratio"], tot["stability_flag"]))
    rows = []
    for g, role in holder_order():
        r = wrow(ix, "wave", "holder", g)
        if r is None:
            continue
        sp = pctx(r["_pos"]) if r["_pos"] is not None else "-"
        rows.append([("**%s**" % NAMES[g]) if role in ("holder", "holder_total") else NAMES[g], bn(r["_flow"]), bn(r["_flow"] / 10), pctx(r["_share"]) if r["_share"] is not None else "n/a",
                     "-" if role == "holder_total" else sp])
    A(md_table(["Holder group", "Net acquisition", "Per-quarter average", "Share of the net", "Share of the positive flows"], rows))
    A(SHARE_EXPLAIN + "\n")
    flows7 = rank_info(ix)[2]
    A("Ranked by net acquisition among the seven groups (insurers, pension funds, registered funds, rest of the world, banks, households, hedge funds and private debt funds): %s.\n" %
      "; ".join("%d %s" % (1 + sum(1 for h in flows7 if flows7[h] > flows7[g]), NAMES[g].split(" (")[0]) for g in sorted(flows7, key=lambda g: -flows7[g])))

    # ---- 6: pre1719 and the path, one table
    A("## Against 2017-2019, and the yearly path\n")
    A("Each cell is the group's share of the all-sector net for that window, with the net acquisition in $bn in brackets; unadjusted basis. The rows between the two windows are in the "
      "same table; no sentence here compares two windows.\n")
    head = ["Window", "All-sector net ($bn)"] + [SHORT[g] for g in GROUPS9]
    rows = []
    for w in ["pre1719"] + ["y%d" % y for y in range(2017, 2026)] + ["y2026h1", "wave"]:
        t = wrow(ix, w, "holder", "total")
        if t is None:
            continue
        lab = wl(w) + (" (offsetting)" if t["stability_flag"] == "offsetting" else "")
        rows.append([lab, thousands(t["_flow"] / 1000, 1)] + [readme_cell(wrow(ix, w, "holder", g)) for g in GROUPS9])
    A(md_table(head, rows))
    offs = [wl(w) for w in ["pre1719"] + ["y%d" % y for y in range(2017, 2026)] + ["y2026h1", "wave"]
            if wrow(ix, w, "holder", "total") is not None and wrow(ix, w, "holder", "total")["stability_flag"] == "offsetting"]
    if offs:
        A("A window marked offsetting (%s) has an offset ratio below 0.5: groups adding and groups reducing holdings largely cancel, so a small change in any line moves every share "
          "in that row a lot.\n" % ", ".join(offs))

    # ---- 7: insurers and reinsurance
    A("## The insurer line and reinsurance\n")
    A("Only uncollateralised coinsurance moves the bonds to the reinsurer, which is in the rest of the world if it is offshore. Under funds withheld and modified coinsurance the US insurer "
      "keeps investing the assets, and US captives are brought into the life sector (Board FEDS Note, 12 Oct 2018). The size of each structure is unknown, so the insurer line may be "
      "understated by an unknown amount. Bonds held through funds sit in the fund sectors.\n")

    # ---- 8: household residual
    A("## The household line is a residual\n")
    A("Households and nonprofits are what is left of the table after the other 27 holder lines: any error in those lines, and any holder the Fed cannot place, lands in this line, "
      "so it is the least secure number in every table. Domestic hedge funds and private debt funds are separate lines. Over 2024Q1-2026Q2 (unadjusted; the denominator of each share is "
      "the all-sector net of %s):\n" % bn(tot["_flow"]))
    rows = []
    for g in ("hh_residual", "hedge_funds", "private_debt_funds", "private_funds", HHPF):
        r = wrow(ix, "wave", "holder", g)
        if r:
            rows.append([NAMES[g], bn(r["_flow"]), pctx(r["_share"]) if r["_share"] is not None else "n/a"])
    A(md_table(["Line", "Net acquisition", "Share of the net"], rows))

    # ---- 9: levels
    A("## Amounts outstanding, and level change minus net acquisition\n")
    lsr = {(r["quarter"], r["group"]): r for r in c["level_shares"][rel.key]}
    qs = [q for q in level_share_quarters(rel)]
    A("Share of the holders' total of the amounts outstanding at the end of the quarter, with the level in $bn in brackets. The denominator is the sum of the 28 holder lines' levels "
      "(%s at %s); the instrument discrepancy (line 54) is printed beside it in level_shares.csv (%s at %s).\n" % (
          bn(Decimal(lsr[(qs[-1], "total")]["holders_total_usd_mn"])), qs[-1].replace(":", ""), bn(Decimal(lsr[(qs[-1], "total")]["discrepancy_usd_mn"] or "0")), qs[-1].replace(":", "")))
    rows = []
    for g in GROUPS9:
        row = [NAMES[g]]
        for q in qs:
            r = lsr.get((q, g))
            row.append("n/a" if r is None else "%s (%s)" % (pctx(Decimal(r["share_of_holders_pct"]), 1), thousands(Decimal(r["level_usd_mn"]) / 1000, 1)))
        rows.append(row)
    A(md_table(["Holder group"] + [q.replace(":", "") for q in qs], rows))
    A("Change in the amount outstanding over the window minus the window's net acquisition is, for most groups, mainly price changes and other changes in volume; for the household "
      "line it is not (see the note below the table). For 2024Q1-2026Q2, from the end of 2023Q4 to the end of 2026Q2, in $bn:\n")
    lcr = {(r["window"], r["group"]): r for r in c["level_change"][rel.key]}
    rows = []
    for g in ["total"] + GROUPS9:
        r = lcr.get(("wave", g))
        if r:
            rows.append(["All holders (sum of the 28 holder lines)" if g == "total" else NAMES[g], bn(Decimal(r["level_start_usd_mn"])), bn(Decimal(r["level_end_usd_mn"])),
                         bn(Decimal(r["flow_usd_mn"])), bn(Decimal(r["change_minus_flow_usd_mn"]))])
    A(md_table(["Holder group", "Level, start", "Level, end", "Net acquisition", "Level change minus net acquisition"], rows))
    hh = lcr.get(("wave", "hh_residual"))
    if hh:
        A("For households and nonprofits the %s is not a measured price effect: their net acquisition is the figure that closes the flow table, their amount outstanding is a separate "
          "series that moved only from %s to %s, and the two do not reconcile, so read this row, and the all-holder row that includes it, as a gap between two series.\n" % (
              bn(Decimal(hh["change_minus_flow_usd_mn"])), bn(Decimal(hh["level_start_usd_mn"])), bn(Decimal(hh["level_end_usd_mn"]))))

    # ---- 10: revisions and registered
    A("## Revisions and the registered statements\n")
    A("Z.1 revises its history at every release. revisions.csv compares every window, group and basis between adjacent releases; %s. The window 2024Q1-2026Q2 stays fixed in every release; "
      "a later quarter enters only the extended window wave_ext.\n" % (
          "%d release%s cached so far, so it holds %d rows" % (len(rels), "" if len(rels) == 1 else "s", len(c["revisions"]))))
    A("Registered statements (scored on the first release that carries 2026Q3, expected 10 Dec 2026): each group's share of the 2024Q1-2026Q2 net on that release is compared with the "
      "same share on the 11 Sep 2026 release. STABLE means the two differ by less than 2.0 percentage points, MOVED means 2.0 or more, PENDING means no release with 2026Q3 is cached yet. "
      "The 2.0 is not calibrated against any earlier revision. A MOVED is a result, written beside the old value.\n")
    rows = [[r[0], NAMES[r[1]], thousands(Decimal(r[6]), 2) + "%" if r[6] else "", (thousands(Decimal(r[7]), 2) + "%") if r[7] else "-", r[8] or "-", r[10]] for r in c["registered"]]
    A(md_table(["Statement", "Group", "Share, release 20260911", "Share, new release", "Absolute change (pp)", "Label"], rows))

    # ---- 11: dictionary
    A("## Columns and words\n")
    A("- **Net acquisition**: purchases minus sales and redemptions over the period, by holders in a sector. **Net issuance**: new bonds issued minus redemptions, by issuers in a sector.\n"
      "- **Share of the net**: 100 times the group's window sum divided by the all-sector window sum (line 13 for holders, line 1 for issuers); a ratio of sums, never a mean of quarterly shares.\n"
      "- **Share of the positive flows**: 100 times the group's net acquisition divided by the sum of the positive net acquisitions of the nine groups (three issuer groups); blank when the "
      "group's figure is zero or negative.\n"
      "- **Per-quarter average**: the window sum divided by the number of quarters in the window.\n"
      "- **Offset ratio**: the absolute all-sector net divided by the sum of the absolute window sums of the 28 holder lines (lines 2, 3 and 12 for issuers); below 0.5 every share in the "
      "window is marked offsetting.\n"
      "- **Residual**: a figure obtained by subtraction (the household line); every error in the other lines lands in it.\n"
      "- **Seasonally adjusted**: the Fed's annual-rate series divided by 4 (basis fa_div4); the headline basis fu is the unadjusted quarterly figure.\n"
      "- **pp**: percentage points. **Release**: a dated posting of the Z.1 data (the folder date of its zip). **Z.1**: the Fed's Financial Accounts of the United States.\n"
      "- **Level**: the amount outstanding at the end of a quarter; LM codes are market value, FL codes state no valuation basis in the dictionary (valuation fl_unspecified).\n")
    A("The twelve CSV files: quarterly.csv (every flow code, 2017Q1 to the latest quarter, both bases), levels.csv (every level code from 2016Q4), windows.csv (window sums, shares, "
      "offset ratio and stability flag by side, group and basis), level_shares.csv and level_change.csv, headline.csv (the 2024Q1-2026Q2 shares and the ranks), comparisons.csv "
      "(2024Q1-2026Q2 minus each comparison window, in pp), revisions.csv, registered.csv, checks.csv, vintages.csv and fetch_log.csv. "
      "Column names ending _usd_mn are millions of dollars; _pct is percent; _pp is percentage points. SOURCES.md lists every request, the wording of every series code and the "
      "builder's decisions.\n")

    # ---- 12: citations
    A("## Citations\n")
    A("Board of Governors of the Federal Reserve System, Financial Accounts of the United States (Z.1), release %s, tables F3.5 and S1281 (public domain, 17 U.S.C. 105). "
      "BIS Quarterly Review, 16 March 2026 (context figure only). Board of Governors FEDS Note of 12 October 2018 (reinsurance structures). "
      "The specification and the supervisor's rulings are in [the spec](../../_research/2026-10-26-Z1-Corporate-Bond-Holders-Spec.md). How the numbers were fetched, the checks and the "
      "builder's decisions are in [SOURCES.md](SOURCES.md).\n" % ", ".join(r.key for r in rels))
    text = "\n".join(L)
    if M("g8_readme_revaluation"):
        text = text.replace("Level change minus net acquisition", "Revaluation").replace("is not a measured price effect", "is a price effect")
    return text


DECISIONS_FIXED = [
    ("Zip not kept; member files committed; .gitignore", "R4 says the zip is not kept and the 14 member files are committed under data/vintages/z1_corporate_bond_holders/<release>/; the build instruction "
     "says the raw zip stays in a gitignored cache. Read together: the zip is held in memory only and never written to disk; .gitignore carries `*.zip`, `*.json` and the STOP latch for that folder as a second "
     "line of defence, and the committed member files are exactly R4's. No member CSV is ignored."),
    ("General and separate accounts on the fu basis only", "The seven members of R4 hold no seasonally adjusted file for the S1281 tables, so ins_life_ga and ins_life_sa have no fa_div4 rows; "
     "the identity general + separate accounts = line 30 is checked on the fu basis only. 2.3 says \"both bases\" for the other identities."),
    ("Issuer offset ratio", "3.7 defines the offset ratio for holders only. For issuers it is the absolute line-1 window sum over the sum of the absolute window sums of lines 2, 3 and 12 (the details "
     "4-11 are inside line 3). Same 0.5 threshold."),
    ("levels.csv starts at 2016:Q4", "3.3 says the same quarters as quarterly.csv (2017:Q1 on), but 3.9 needs the 2016:Q4 level for the 2016:Q4 level share and for the start of pre1719 and y2017. "
     "levels.csv therefore starts one quarter earlier, and C09 covers levels from 2016:Q4."),
    ("Total rows carry no share of the positive flows", "3.6 gives share_of_positive_pct to every row whose flow is positive, members and sub-lines included; the all-holder and all-issuer total rows "
     "are left blank (their ratio to the positive total is not a share of anything)."),
    ("A void window writes no share at all", "When the total is not positive, share_of_total_pct and share_of_positive_pct are both blank (3.5 names only the first)."),
    ("Tolerance of the flow identities", "2.3 says within 1 $mn and \"exactly\"; C04 says within 2 $mn for each. The check uses 2 $mn on every identity; the observed maximum is printed in checks.csv."),
    ("Checks across releases", "checks.csv has no release column, so a per-release check prints one clause per cached release in `observed` and takes the worst status. Pins fail on 20260911 and warn on a later release."),
    ("Folder guards refuse instead of adding a check", "The folder guards (names, headers, allowed values, keys, verdict words, CUSIP shapes, paths, at signs, wording, the typed reference constants) are not among the pinned and structural checks of section 8; "
     "when they find a problem the build stops (exit 2) and writes nothing, the way G12-G14 and G17 require \"refuse\"."),
    ("Wording scan on the CSVs as well", "G14 applies to README.md. The same two patterns and the verdict-word scan are also applied to every CSV when it is written (stricter); SOURCES.md is exempt, as the "
     "denial sentence is."),
    ("A corrupt zip latches STOP", "R3a lists empty, HTML and non-zip bodies. A body that starts with PK\\x03\\x04 but cannot be opened as a zip is treated as the same kind of failed content test (STOP)."),
    ("A cached release is not fetched again", "fetch refuses a release whose folder already holds provenance.csv (exit 5); the cache is never overwritten. The two runs a day of R3 are counted from fetch_log.csv."),
    ("provenance.csv layout", "kind,name,sha256,bytes,last_modified,members: one `zip` row (digest, size and Last-Modified of the zip, member count of the archive) and one `member` row per cached file."),
    ("Missing member or table", "A cached release that lacks one of the seven CSV files stops the build (DataError). A missing dictionary file, or a code missing from a header, is a C15 FAIL and the build goes on."),
    ("Which release the README shows", "The README tables use the newest cached release; earlier releases appear in the CSVs and in revisions.csv."),
    ("Outputs written when a check fails", "As R3b says, the build writes its outputs and exits 1 when any check row is FAIL; nothing is moved to a _FAILED folder."),
    ("Statement scoring", "registered.csv holds one row per statement: PENDING with a blank release_new until a release after 20260911 that carries 2026:Q3 is cached, then that release (the first such release only)."),
    ("Names in the README", "NAMES in the script give each group a plain label; `other` is equity REITs, the federal government, state and local governments, the central bank, money market funds, finance companies, "
     "mortgage REITs, holding companies and other financial business (lines 15-18, 36, 46, 47, 49, 50); `gse_bd` is lines 43 and 48."),
]
DECISIONS_POST = [
    ("Folder guard: the TIC pairing test hit a coincidence (R9, fixed before the first outputs were written)",
     "The first `build` stopped with \"README.md holds a figure from another source\": the guard looked for the digits of three reference numbers (the review figure of CREF2a and the two "
     "typed constants of CREF2b) anywhere outside checks.csv, and a README table cell printed the unadjusted 2024 net acquisition of the rest of the world, in $bn, with the same digits as the "
     "review figure: a Z.1 figure that happens to equal it. Old rule: any occurrence of those three numbers outside checks.csv. New rule: only the two typed constants, and only where a line "
     "names the source (TIC, Treasury or sb0662) beside one, or a CSV cell is exactly a constant at one decimal. The review figure is a Fed number read during review, not another source, "
     "and is no longer matched. No rule, threshold, window, registered number or label changed."),
    ("README: quarter labels (presentation only, before the outputs were first written)",
     "The level-share table headed its columns with the data form of a quarter (2016:Q4) while the rest of the README writes 2016Q4. Old: 2016:Q4 ... 2026:Q2 in the README headings and sentences. "
     "New: 2016Q4 ... 2026Q2. The CSVs keep the YYYY:QN form of R8."),
    ("README: two links (presentation only)", "The citations now link SOURCES.md and the specification, so the doc-link check finds both reachable. No number or sentence of the results changed."),
]                   # post-run fixes (R9) are appended here with the old and the new value

SPEC_AUTHOR_REQUESTS = """| UTC (26 Oct 2026) | URL | Status | Bytes | Note |
|---|---|---|---|---|
| 19:43:08 | https://www.federalreserve.gov/releases/z1/20260911/z1_csv_files.zip | 200 | 8,336,582 | sha256 b63af9755437df0fb88b7cf346f8f9eaeb22bf1aa2b5df1709334135c43de4b6; 616 members |
| 19:45:22 | https://home.treasury.gov/data/treasury-international-capital-tic-system | 200 | 78,207 | read for the Form S and CSLT notes; not used by the build |
| 19:45:25 | https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/cslt.zip | 200 | 8,910,770 | metadata only; not used by the build |
| 19:46:30 | https://www.federalreserve.gov/releases/z1/20260911/default.htm | 404 | 82,134 | not retried; never requested by the build |
| 19:46:33 | https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FA653063005&t=F.213 | 200 | 73,549 | the Financial Accounts Guide's error page; not retried |
"""

DISCLOSURE_BLOCK = """Before any build, during the review of the specification, some holder shares were seen:

- Grok (an attack parcel that carried no blind clause) read the published seasonally adjusted F3.5.t table on federalreserve.gov and reported wave-window shares of about 32% (life plus
  property-casualty insurers), 47% (registered funds), 41% (rest of the world) and -35% (household residual).
- The supervisor then confirmed from the cached 11 Sep zip, unadjusted sums: insurers 33.26% of 2,228,428 $mn over the ten quarters; 2024 37.12% (224,689 + 70,237 of 794,490); 2025 35.67%
  (221,483 + 65,834 of 805,405).
- The second reviewer stayed blind on 2024-26 and computed 2017-2019 shares (observed during review): registered funds 39.98%, insurers 34.36%, rest of the world 31.23% of 1,329,619 $mn.
- The spec author saw no holder share for any window and no 2024-26 value; read the dictionaries, the identity residuals on 2017Q1-2019Q4, the FA/4-versus-FU annual gaps for 2017-2019, the flows
  of lines 18, 41, 42 and 50 for 2020Q1-2021Q4, a count of ND cells (zero) and CSLT metadata only.
"""

IDENTITIES_BLOCK = """Checked on every quarter from 1990:Q1 (FAIL from 2017:Q1, WARN before), within 2 $mn:

- Flows, both bases: the 28 leaf lines sum to line 13; line 1 = line 13; lines 2 + 3 + 12 = line 1; lines 4-11 = line 3; 19 = 20 + 21; 24 = 25 + 26; 27 = 28 + 29; 30 = 31 + 32; 43 = 44 + 45;
  51 = 52 + 53; general + separate accounts = line 30 (fu basis only).
- Levels: the 28 leaf levels sum to line 13 and line 54 = line 1 - line 13. Line 1 minus line 13 was -290,252 (2017Q4), +357,667 (2018Q4) and -599,833 (2019Q4) $mn on the 11 Sep release.
  The spec's first draft wrongly said line 13 is not the sum of the leaves; the level-share denominator is that sum, and line 54 is printed beside it.
- Bases: over each complete calendar year from 2017, sum(FA)/4 equals sum(FU) within 4 $mn on all 53 lines.
"""


def sources_requests_table(fetch_rows):
    out = ["| UTC | host | path | status | bytes | sha256 | Last-Modified |", "|---|---|---|---|---|---|---|"]
    for r in fetch_rows:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out) + "\n"


def sources_dictionary_table(rel):
    out = ["| Series code | Line | Dictionary text |", "|---|---|---|"]
    for l in LINES:
        for code in (l.fu, l.fa, l.lvl):
            if code:
                d = dict_for(rel, code)
                out.append("| %s | %s | %s |" % (code, l.line if d is None else d[1].replace("Line ", ""), "(not in the dictionary)" if d is None else d[0].replace("|", "/")))
    return "\n".join(out) + "\n"


def render_sources(c):
    rel = c["rels"][-1]
    L = []
    A = L.append
    A("# Sources, requests and builder decisions: net acquisition of corporate and foreign bonds by holder sector (Z.1 table F3.5)\n")
    A("The specification is `_research/2026-10-26-Z1-Corporate-Bond-Holders-Spec.md`, committed at bc22c96 (with the supervisor's rulings of rounds 1 and 2) before the first request.\n")
    A("## Requests\n")
    A("**By the spec author, first draft, 26 Oct 2026** (5 requests, all GET, sequential, at least 2.5 s apart, the User-Agent of R2, no redirect followed, no retry, no 403 or 429; the rewrite made no request):\n")
    A(SPEC_AUTHOR_REQUESTS)
    A("**By others during review (relayed from the round-1 rulings, not logged by the spec author):** Grok read the published F3.5.t table on federalreserve.gov; the supervisor read the cached "
      "11 Sep zip and checked a Treasury press release. No request by anyone went to sec.gov or FRED.\n")
    A("**By this build (`fetch`, one request per run; the request log is fetch_log.csv):**\n")
    A(sources_requests_table(c["fetch_rows"]))
    A("## Disclosure: what was seen before any build\n")
    A(DISCLOSURE_SENTENCE + "\n")
    A(DISCLOSURE_BLOCK)
    A("## Identities (section 2.3)\n")
    A(IDENTITIES_BLOCK)
    A("## Wording of every series code\n")
    A("From the data dictionaries of release %s (the FU, FA and level code of every line; the four S1281 codes). Level codes beginning LM are market value; FL codes state no basis.\n" % rel.key)
    A(sources_dictionary_table(rel))
    A("## Other sources\n")
    A("- Board of Governors of the Federal Reserve System, FEDS Notes, 12 October 2018, on reinsurance structures (relayed in the specification by the supervisor; not read by the builder, who does not "
      "have its title).\n"
      "- Treasury TIC press release sb0662, used only for the typed constants of check CREF2 (relayed; checked verbatim by the supervisor; not read by the builder).\n"
      "- BIS Quarterly Review, 16 March 2026, for one context figure in the README (supervisor ruling, round 2).\n")
    A("## Builder decisions\n")
    A("Where the specification is ambiguous the stricter reading about leaks and causal wording was taken. None of these changes a rule, a threshold, a window, a registered number or a label.\n")
    for i, (t, d) in enumerate(DECISIONS_FIXED, 1):
        A("%d. **%s.** %s\n" % (i, t, d))
    if DECISIONS_POST:
        A("### Fixes after the first run (R9)\n")
        for t, d in DECISIONS_POST:
            A("- **%s.** %s\n" % (t, d))
    return "\n".join(L)


# ------------------------------------------------------------------------------------------------------------------------
# inputs, compute, render, build
# ------------------------------------------------------------------------------------------------------------------------
def read_fetch_rows(out_dir):
    return read_csv_rows(os.path.join(out_dir, "fetch_log.csv"))[1]


def read_old_vintages(out_dir):
    h, rows = read_csv_rows(os.path.join(out_dir, "vintages.csv"))
    return {r[0]: dict(zip(h, r)) for r in rows if r}


def load_inputs(cache, out_dir):
    rels = [load_release(os.path.join(cache, n)) for n in list_releases(cache)]
    if not rels:
        raise DataError("no complete release in the cache %s: run fetch first" % tilde(cache))
    return {"rels": rels, "fetch_rows": read_fetch_rows(out_dir), "old_vint": read_old_vintages(out_dir)}


def zip_path(key):
    return "/releases/z1/%s/%s" % (key, ZIP_NAME)


def retrieved(fetch_rows, key):
    rows = [r for r in fetch_rows if len(r) > 3 and r[2] == zip_path(key) and r[3] == "200"]
    return rows[-1][0] if rows else ""


def source_line(c, tic=False):
    keys = [r.key for r in c["rels"]]
    dates = sorted({retrieved(c["fetch_rows"], k)[:10] for k in keys if retrieved(c["fetch_rows"], k)})
    s = ("# source: Board of Governors of the Federal Reserve System, Financial Accounts of the United States (Z.1), release%s %s, tables F3.5 and S1281; retrieved %s (fetch_log.csv)" %
         ("s" if len(keys) > 1 else "", ", ".join(keys), ", ".join(dates) if dates else "(no logged retrieval)"))
    if tic:
        s += "; CREF2 also cites Treasury TIC release sb0662 (typed constants)"
    return s


def fetch_source_line(rows):
    ds = sorted({r[0][:10] for r in rows if len(r) > 3 and r[3] == "200"})
    return "# source: request log of bin/z1_corporate_bond_holders.py fetch against %s, retrieved %s; one row per request" % (HOST, ", ".join(ds) if ds else "(no logged retrieval)")


def compute(inp):
    rels = sorted(inp["rels"], key=lambda r: r.key)
    c = {"rels": rels, "fetch_rows": inp["fetch_rows"], "old_vint": inp["old_vint"], "W": {}, "ix": {}, "level_shares": {}, "level_change": {}}
    for r in rels:
        w = window_rows(r)
        c["W"][r.key] = w
        c["ix"][r.key] = widx(w)
        c["level_shares"][r.key] = level_share_rows(r)
        c["level_change"][r.key] = level_change_rows(r)
    c["registered"] = registered_rows(rels)
    c["revisions"] = revision_rows(rels, inp.get("existing_revs", ()))
    return c


def vintage_rows(c):
    out = []
    for r in c["rels"]:
        z = r.zip_row()
        out.append([r.key, zip_path(r.key), z.get("sha256", ""), z.get("bytes", ""), z.get("last_modified", ""), retrieved(c["fetch_rows"], r.key)])
    return out


def render_all(c):
    """Every output but checks.csv and fetch_log.csv (the request log is written by fetch and only read here)."""
    src = source_line(c)
    rels = c["rels"]
    t = collections.OrderedDict()
    t["quarterly.csv"] = render_csv("quarterly.csv", [x for r in rels for x in quarterly_rows(r)], src)
    t["levels.csv"] = render_csv("levels.csv", [x for r in rels for x in levels_rows(r)], src)
    t["windows.csv"] = render_csv("windows.csv", [x for r in rels for x in c["W"][r.key]], src)
    t["level_shares.csv"] = render_csv("level_shares.csv", [x for r in rels for x in c["level_shares"][r.key]], src)
    t["level_change.csv"] = render_csv("level_change.csv", [x for r in rels for x in c["level_change"][r.key]], src)
    t["headline.csv"] = render_csv("headline.csv", [x for r in rels for x in headline_rows(r, c["W"][r.key])], src)
    t["registered.csv"] = render_csv("registered.csv", c["registered"], src)
    t["comparisons.csv"] = render_csv("comparisons.csv", [x for r in rels for x in comparison_rows(r, c["W"][r.key])], src)
    t["revisions.csv"] = render_csv("revisions.csv", c["revisions"], src)
    t["vintages.csv"] = render_csv("vintages.csv", vintage_rows(c), src)
    rd = render_readme(c)
    guard_text("README.md", rd)
    t["README.md"] = rd
    t["SOURCES.md"] = render_sources(c)
    return t


def finish(c, out_dir, cache):
    """Render, add the checks (C10 from a second independent compute), run the folder guards. Returns (texts, failed check ids)."""
    if not allow_hash_ok():
        raise DataError("the column allowlist in this script does not hash to SPEC_ALLOW_SHA256")
    t1 = render_all(c)
    c2 = compute(load_inputs(cache, out_dir))
    t2 = render_all(c2)
    if M("x_render_unstable"):
        t2["README.md"] += "x"
    checks = build_checks(c["rels"], c["fetch_rows"], c["old_vint"], t1, t2)
    t1["checks.csv"] = render_csv("checks.csv", checks, source_line(c, tic=True))
    files = dict(t1)
    fl = os.path.join(out_dir, "fetch_log.csv")
    files["fetch_log.csv"] = read_file(fl, "r") if os.path.exists(fl) else render_csv("fetch_log.csv", [], fetch_source_line([]))
    probs = all_folder_problems(files)
    if probs:
        raise DataError("folder guards: " + "; ".join(probs[:5]))
    c["checks"] = checks
    return t1, [r[0] for r in checks if r[4] == "FAIL"]


def write_outputs(texts, out_dir):
    for n, x in texts.items():
        write_text(os.path.join(out_dir, n), x)


def check_cache(cache, root=ROOT, out_dir=None):
    """The cache may be outside the repository, or inside it only under data/vintages/ (never in the committed output folder)."""
    real = os.path.realpath(os.path.expanduser(cache))
    rroot = os.path.realpath(root)
    if real == rroot or real.startswith(rroot + os.sep):
        outd = os.path.realpath(out_dir or os.path.join(root, "data", "z1_corporate_bond_holders"))
        if real == outd or real.startswith(outd + os.sep):
            raise Refused("the cache may not live in the committed output folder")
        rel = os.path.relpath(real, rroot).replace(os.sep, "/") + "/"
        if not rel.startswith("data/vintages/"):
            raise Refused("a cache inside the repository must be under data/vintages/")
    return real


def run_build(a):
    t0 = time.time()
    out_dir = a.out
    cache = check_cache(a.cache, out_dir=out_dir)
    try:
        inp = load_inputs(cache, out_dir)
        if not inp["fetch_rows"]:
            raise DataError("fetch_log.csv holds no request: run fetch first")
        c = compute(inp)
        texts, failed = finish(c, out_dir, cache)
    except DataError as e:
        print("STOP (data): %s" % e, file=sys.stderr)
        return 2
    write_outputs(texts, out_dir)
    rel = c["rels"][-1]
    ix = c["ix"][rel.key]
    ins, tot = wrow(ix, "wave", "holder", "ins"), wrow(ix, "wave", "holder", "total")
    print("releases cached: %s" % ", ".join(r.key for r in c["rels"]))
    print("== ins_share_wave_pct (release %s, fu, 2024:Q1-2026:Q2): %s%% = %s of %s $mn (all-sector net)" % (rel.key, pct(ins["_share"]), usd(ins["_flow"]), usd(tot["_flow"])))
    print("== checks")
    for r in c["checks"]:
        print("   %-6s %-5s %s" % (r[0], r[4], r[3][:230]))
    print("failed: %s; wrote %d files to %s (%.1f s)" % (", ".join(failed) or "none", len(texts), tilde(out_dir), time.time() - t0))
    return 1 if failed else 0


# ------------------------------------------------------------------------------------------------------------------------
# requests: the URL check (R1, R3), the content tests (R3a) and the fetcher
# ------------------------------------------------------------------------------------------------------------------------
def check_url(url):
    """Only a plain https GET to www.federalreserve.gov for /releases/z1/<YYYYMMDD>/z1_csv_files.zip. Returns (host, target)."""
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    target = p.path
    if M("g16_allow_other_host"):
        return host, target + ("?" + p.query if p.query else "")
    if p.scheme != "https" or p.username or p.password or p.port not in (None, 443) or p.fragment or p.query:
        raise Refused("only plain https URLs without a query are allowed")
    for b in BLOCKED_HOSTS:
        if host == b or host.endswith("." + b):
            raise Refused("host %s is never requested (Treasury, SEC and FRED are out of scope)" % host)
    if host != HOST:
        raise Refused("host %s is not on the allowlist" % host)
    if M("g16_default_htm_ok") and re.match(r"^/releases/z1/\d{8}/default\.htm$", target):
        return host, target
    if not ZIP_PATH_RX.match(target):
        raise Refused("only /releases/z1/<YYYYMMDD>/z1_csv_files.zip is requested; the release page never is")
    return host, target


def real_opener(host, target, headers, timeout, cap):
    """GET https://host/target. Returns (status, body, response headers). No redirect is followed (a 3xx comes back as a status and latches), no cookies, the only verb is GET.
    A non-200 body is read up to ERR_CAP bytes (its head goes into the STOP file). Socket faults raise SocketFault."""
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
    except (OSError, EOFError, http.client.HTTPException) as e:
        raise SocketFault(type(e).__name__)
    finally:
        conn.close()


def esc_head(body, n=300):
    return (body or b"")[:n].decode("latin-1").encode("unicode_escape").decode("ascii")


STOP_FIELDS = ("status", "utc_time", "url_path", "retry_after", "body_head")


def stop_fields(status, utc_time, url_path, retry_after, body_head):
    lines = ["status: %s" % status, "utc_time: %s" % utc_time, "url_path: %s" % url_path]
    if not M("g15_stop_short"):
        lines.append("retry_after: %s" % retry_after)
    lines.append("body_head: %s" % body_head)
    return "\n".join(lines) + "\n"


def stop_text_ok(text):
    return [l.split(":", 1)[0] for l in text.splitlines()] == list(STOP_FIELDS)


def create_stop(path, text):
    """The one place a STOP file is created: exclusive create ("x"), so an existing latch is never overwritten. The AST scan (G15) allows nothing else."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "x", encoding="utf-8") as fh:
            fh.write(text)
    except FileExistsError:
        if M("g15_overwrite"):
            _clobber(path, text)                  # the mutant: what create_stop must never do; run-time test only


def _clobber(p, text):
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


def looks_like_page(body):
    return body.lstrip()[:15].lower().startswith((b"<!", b"<html"))


def body_problem(body):
    """R3a: a 200 body that is empty, a web page, or not a zip latches the STOP file."""
    if not body and not M("g15_empty_ok"):
        return "empty body"
    if body and looks_like_page(body) and not M("g15_html_ok"):
        return "the body is a web page"
    if body and body[:4] != b"PK\x03\x04" and not M("g15_nonzip_ok"):
        return "the body is not a zip (first four bytes are not PK\\x03\\x04)"
    return ""


def _member_write(folder, name, data):
    """Mutant only (g11_member_path): a write path built from an archive member name. Never called in a real run."""
    write_bytes(os.path.join(folder, name), data)


class ContentFailure(Exception):
    pass


def cache_zip(body, release, cache, last_modified_iso):
    """Write the 14 members of R4 under <cache>/<release>/ by exact member name and fixed file name, then provenance.csv. The zip itself is never written.
    Returns (members written, member names missing from the archive)."""
    try:
        z = zipfile.ZipFile(io.BytesIO(body))
    except zipfile.BadZipFile:
        raise ContentFailure("the body starts like a zip but cannot be opened as one")
    names = set(z.namelist())
    final = os.path.join(cache, release)
    prov = []
    missing = []
    if M("g11_member_path"):
        for mname in z.namelist():
            if mname.endswith(".csv"):
                _member_write(final, mname, z.read(mname))
    for zname, cname in FIXED_MEMBERS.items():
        if zname not in names:
            missing.append(zname)
            continue
        info = z.getinfo(zname)
        if info.file_size > MEMBER_CAP:
            missing.append(zname)
            continue
        data = z.read(zname)
        write_bytes(os.path.join(final, cname), data)
        prov.append(["member", cname, sha256_of(data), str(len(data)), "", ""])
    prov.sort(key=lambda r: r[1])
    rows = [["zip", ZIP_NAME, sha256_of(body), str(len(body)), last_modified_iso, str(len(z.namelist()))]] + prov
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(PROV_COLS)
    w.writerows(rows)
    write_text(os.path.join(final, "provenance.csv"), out.getvalue())
    return len(prov), missing


class Fetcher(object):
    """One host, one URL, one request. Opener, clock, sleeper and the STOP directory are injectable so every rule is testable without a network."""

    def __init__(self, cache, out_dir, stop_dir=STOP_DIR, opener=real_opener, wall=time.time, sleeper=time.sleep, now_utc=None, root=ROOT):
        self.out_dir = out_dir
        self.cache = check_cache(cache, root=root, out_dir=out_dir)
        self.stop_dir = stop_dir
        self.opener, self.wall, self.sleeper = opener, wall, sleeper
        self.now_utc = now_utc or (lambda: dt.datetime.now(dt.timezone.utc))
        self.requests = 0
        self.log_path = os.path.join(out_dir, "fetch_log.csv")

    def utc_str(self):
        return self.now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")

    def stop_path(self):
        return os.path.join(self.stop_dir, STOP_NAME)

    def check_stop(self):
        if os.path.exists(self.stop_path()) and not M("g15_stop_ignored"):
            raise Latched("STOP present: %s" % tilde(self.stop_path()))

    def _log(self, ts, target, status, nbytes, sha, lm):
        _, rows = read_csv_rows(self.log_path)
        rows.append([ts, HOST, target, str(status), str(nbytes), sha, lm])
        os.makedirs(self.out_dir, exist_ok=True)
        write_text(self.log_path, render_csv("fetch_log.csv", rows, fetch_source_line(rows)))

    def _latch(self, status, target, retry_after, body, why):
        text = stop_fields(status, self.utc_str(), target, retry_after or "", esc_head(body))
        create_stop(self.stop_path(), text)
        raise Latched("STOP written: %s (%s)" % (tilde(self.stop_path()), why))

    def run_gate(self):
        """R3: at most two runs a calendar day (counted from fetch_log.csv) and at least 3 seconds after the last request."""
        _, rows = read_csv_rows(self.log_path)
        today = self.utc_str()[:10]
        if sum(1 for r in rows if r and r[0][:10] == today) >= MAX_RUNS_PER_DAY and not M("g16_daily_cap_off"):
            raise Refused("at most %d runs a calendar day: fetch_log.csv already holds %d for %s" % (MAX_RUNS_PER_DAY, MAX_RUNS_PER_DAY, today))
        if rows and not M("g16_pacing_off"):
            last = dt.datetime.strptime(rows[-1][0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
            wait = MIN_SLEEP - (self.now_utc() - last).total_seconds()
            if wait > 0:
                self.sleeper(wait)

    def _get(self, target):
        check_url("https://" + HOST + target)
        self.requests += 1
        started = self.now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            status, body, rh = self.opener(HOST, target, dict(HEADERS), TIMEOUT, BODY_CAP)
        except SocketFault:
            self._log(started, target, "socket_fault", "", "", "")
            if M("g15_stop_on_timeout"):
                create_stop(self.stop_path(), stop_fields("timeout", self.utc_str(), target, "", ""))
            raise
        return status, body, rh, started

    def run(self, release, say=print):
        """Returns the exit code: 0 done, 2 STOP present or written, 3 not posted or network fault. Refusals raise Refused."""
        if not RELEASE_RX.match(release or ""):
            raise Refused("--release must be YYYYMMDD")
        try:
            dt.datetime.strptime(release, "%Y%m%d")
        except ValueError:
            raise Refused("--release is not a date")
        try:
            self.check_stop()
        except Latched as e:
            say(str(e))
            return 2
        target = "/releases/z1/%s/%s" % (release, ZIP_NAME)
        check_url("https://" + HOST + target)
        if os.path.isfile(os.path.join(self.cache, release, "provenance.csv")):
            raise Refused("release %s is already cached; the cache is never overwritten" % release)
        self.run_gate()
        try:
            status, body, rh, started = self._get(target)
            if status in (429, 500) and M("g16_retry"):
                status, body, rh, started = self._get(target)
            if status == 404 and not M("g15_404_latches"):
                self._log(started, target, 404, "", "", "")
                say("NOT POSTED %s" % target)
                return 3
            if status != 200:
                self._log(started, target, status, "", "", "")
                if status // 100 == 3 and M("g15_3xx_ignored"):
                    return 0
                if status // 100 == 3 and M("g16_redirect_follow"):
                    status, body, rh, started = self._get(rh.get("location", target))
                else:
                    self._latch(status, target, rh.get("retry-after", ""), body, "HTTP %s" % status)
            lm = http_date_iso(rh["last-modified"]) if rh.get("last-modified") else ""
            if body is None:
                self._log(started, target, status, "", "", lm)
                self._latch(status, target, "", b"", "body larger than the cap")
            self._log(started, target, status, len(body), sha256_of(body), lm)
            prob = body_problem(body)
            if prob:
                self._latch(status, target, "", body, "content test: %s" % prob)
            if M("g16_second_request"):
                self.opener(HOST, "/releases/z1/%s/default.htm" % release, dict(HEADERS), TIMEOUT, BODY_CAP)
                self.requests += 1
            try:
                n, missing = cache_zip(body, release, self.cache, lm)
            except ContentFailure as e:
                self._latch(status, target, "", body, "content test: %s" % e)
            say("saved %d of %d members of %s (%s bytes, sha256 %s, Last-Modified %s)%s" % (n, len(FIXED_MEMBERS), ZIP_NAME, fmt_int(len(body)), sha256_of(body), lm or "none",
                                                                                         ("; missing from the archive: " + ", ".join(missing)) if missing else ""))
            return 0
        except Latched as e:
            say(str(e))
            return 2
        except SocketFault:
            say("FAIL network %s: the run ends; nothing was latched and nothing is retried" % target)
            return 3


# ------------------------------------------------------------------------------------------------------------------------
# static scans of this script's own source: the STOP latch (G15), zip handling (G11) and isolation (G17)
# ------------------------------------------------------------------------------------------------------------------------
REMOVERS = {"remove", "unlink", "rmtree", "rmdir"}
MUTATORS = {"replace", "rename", "move", "write_text", "write_bytes", "truncate", "copy", "copyfile", "copy2", "symlink", "link"}


def _mentions_stop(node, tainted):
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and ("stop" in n.id.lower() or n.id in tainted):
            return True
        if isinstance(n, ast.Attribute) and "stop" in n.attr.lower():
            return True
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and "stop" in n.value.lower():
            return True
    return False


def _fname(call):
    f = call.func
    return f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")


def _open_mode(call):
    """The mode of an open() call: the literal string, '' when absent (read), None when it is not a literal."""
    node = call.args[1] if len(call.args) > 1 else next((k.value for k in call.keywords if k.arg == "mode"), None)
    if node is None:
        return ""
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _scope_nodes(scope):
    """The nodes of one scope, not descending into nested functions (each function is scanned as its own scope)."""
    out, stack = [], [scope]
    while stack:
        n = stack.pop()
        out.append(n)
        for ch in ast.iter_child_nodes(n):
            if not isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                stack.append(ch)
    return out


def _taint(nodes, mentions):
    tainted = set()
    for _ in range(3):
        for n in nodes:
            tgt, val = None, None
            if isinstance(n, ast.Assign):
                tgt, val = n.targets, n.value
            elif isinstance(n, (ast.AnnAssign, ast.AugAssign)) and n.value is not None:
                tgt, val = [n.target], n.value
            elif isinstance(n, ast.For):
                tgt, val = [n.target], n.iter
            if val is not None and mentions(val, tainted):
                for t in tgt:
                    for x in ast.walk(t):
                        if isinstance(x, ast.Name):
                            tainted.add(x.id)
    return tainted


def stop_ast_problems(src):
    """G15: an AST scan. A STOP path may be reached only by create_stop, with open(path, "x"). No function removes, renames over or truncates anything that reaches a STOP path."""
    if M("g15_scan_off"):
        return []
    tree = ast.parse(src)
    problems = set()
    scopes = [(n.name, n) for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))] + [("<module>", tree)]
    for fname, scope in scopes:
        nodes = _scope_nodes(scope)
        tainted = _taint(nodes, _mentions_stop)
        for call in [n for n in nodes if isinstance(n, ast.Call)]:
            nm = _fname(call)
            where = "%s line %d" % (fname, call.lineno)
            if fname == "create_stop" and nm in ("open", "fdopen") and _open_mode(call) != "x" and not M("g15_ignore_open"):
                problems.add("%s: create_stop opens a file in mode %r (only exclusive create, \"x\", is allowed)" % (where, _open_mode(call)))
            reach = any(_mentions_stop(a, tainted) for a in list(call.args) + [k.value for k in call.keywords]) or (
                isinstance(call.func, ast.Attribute) and _mentions_stop(call.func.value, tainted))
            if nm in REMOVERS:
                problems.add("%s: %s (this script removes nothing)" % (where, nm))
            elif nm in MUTATORS and reach and not (nm == "replace" and M("g15_replace_ok")):
                problems.add("%s: %s reaches a STOP path" % (where, nm))
            elif nm in ("open", "fdopen") and reach and not M("g15_ignore_open"):
                mode = _open_mode(call)
                if not (fname == "create_stop" and mode == "x") and (mode is None or any(ch in mode for ch in "wax+")):
                    problems.add("%s: open in mode %r reaches a STOP path" % (where, mode))
    return sorted(problems)


def _mentions_archive(node, tainted):
    for n in ast.walk(node):
        if isinstance(n, ast.Call) and _fname(n) in ("namelist", "infolist"):
            return True
        if isinstance(n, ast.Attribute) and n.attr in ("filename", "orig_filename"):
            return True
        if isinstance(n, ast.Name) and n.id in tainted:
            return True
    return False


WRITERS = {"write_bytes", "write_text", "open", "makedirs", "join", "replace", "rename", "mkdir"}


def zip_ast_problems(src):
    """G11: extract/extractall is never called, and no write path is built from an archive member name."""
    if M("g11_scan_off"):
        return []
    tree = ast.parse(src)
    problems = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and _fname(n) in ("extractall", "extract"):
            problems.add("line %d: %s is called" % (n.lineno, _fname(n)))
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        nodes = _scope_nodes(fn)
        tainted = _taint(nodes, _mentions_archive)
        for call in [n for n in nodes if isinstance(n, ast.Call)]:
            if _fname(call) in WRITERS and any(_mentions_archive(a, tainted) for a in list(call.args) + [k.value for k in call.keywords]):
                problems.add("%s line %d: %s builds a path from an archive member name" % (fn.name, call.lineno, _fname(call)))
    return sorted(problems)


FORBIDDEN_FRAGMENTS = ("series.tsv", "data/history", "calendar.tsv", "handover.tsv", "the_ask", "research_state", "dropbox", "data/nport", "nport_", "data/census", "data/ipo_13f",
                       "form13f", "secrets.env")
PATH_CALLS = {"open", "read_file", "read_csv_rows", "join", "exists", "listdir", "isdir", "isfile", "write_text", "write_bytes", "makedirs", "glob", "walk"}


def isolation_problems(src):
    """G17: the script opens paths from its cache and its output folder only. No path call names a project file outside them, an absolute path or a parent directory."""
    if M("g17_scan_off"):
        return []
    tree = ast.parse(src)
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _fname(node) in PATH_CALLS:
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Constant):
                continue                                  # "sep".join(...)
            for a in list(node.args) + [k.value for k in node.keywords]:
                for s in ast.walk(a):
                    if isinstance(s, ast.Constant) and isinstance(s.value, str):
                        v = s.value.lower()
                        if any(fr in v for fr in FORBIDDEN_FRAGMENTS):
                            out.add("line %d: %s(...) names %r" % (node.lineno, _fname(node), s.value))
                        elif _fname(node) in ("open", "read_file", "read_csv_rows") and (s.value.startswith("/") or ".." in s.value):
                            out.add("line %d: %s(...) opens the absolute or parent path %r" % (node.lineno, _fname(node), s.value))
    return sorted(out)


# ------------------------------------------------------------------------------------------------------------------------
# selftest: synthetic data only. Every guard G1-G18 of the spec's section 7 has a test; each mutant (a deliberately broken variant, switched on in this process
# only) must make its guard's test fail. A mutant that is not caught is a failure.
# ------------------------------------------------------------------------------------------------------------------------
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

    def quiet(self, name, fn):
        try:
            fn()
        except Exception as e:
            self.ok(name, False, "raised %s: %s" % (type(e).__name__, e))
        else:
            self.ok(name, True)

    def failed(self):
        return [(n, d) for n, c, d in self.items if not c]


class FakeClock(object):
    def __init__(self, t=1_800_000_000.0):
        self.t = t

    def wall(self):
        return self.t

    def sleep(self, s):
        self.t += s

    def now_utc(self):
        return dt.datetime.fromtimestamp(self.t, dt.timezone.utc)


SUBS = ((19, 20, 21), (24, 25, 26), (27, 28, 29), (30, 31, 32), (43, 44, 45), (51, 52, 53))
EXPECT_GROUPS = {"ins": [27, 30], "pen": [33, 34, 35], "funds": [37, 38, 39, 40], "row": [51], "banks": [19, 22, 23, 24], "hh_residual": [14], "private_funds": [41, 42],
                 "gse_bd": [43, 48], "other": [15, 16, 17, 18, 36, 46, 47, 49, 50]}                 # typed a second time from 2.2, for the tests only


class Lcg(object):
    def __init__(self, s):
        self.s = s & 0x7fffffff

    def next(self, lo, hi):
        self.s = (self.s * 1103515245 + 12345) & 0x7fffffff
        return lo + (self.s >> 8) % (hi - lo + 1)


def world_quarters(last):
    return ["%d:Q4" % y for y in range(1945, 1952)] + qrange("1952:Q1", last)


def adj_fa(key, q):
    """A quarter-of-year pattern that sums to zero over a calendar year: annual sum(FA)/4 equals annual sum(FU)."""
    if q <= "1951:Q4":
        return 0
    k = 2 + (sum(ord(ch) for ch in key) % 3)
    return [k, -k, 1, -1][int(q[-1]) - 1]


def flows_at(b, q, scale, adj):
    v = {}
    for l in LEAVES:
        v[l.line] = scale * (b["L%d" % l.line] + adj("L%d" % l.line, q))
    for p, a, bb in SUBS:
        av = scale * (b["A%d" % p] + adj("A%d" % p, q))
        v[a], v[bb] = av, v[p] - av
    v[13] = sum(v[l.line] for l in LEAVES)
    v[2] = scale * (b["N"] + adj("N", q))
    for l in ISS_DETAILS:
        v[l.line] = scale * (b["D%d" % l.line] + adj("D%d" % l.line, q))
    v[3] = sum(v[l.line] for l in ISS_DETAILS)
    v[1] = v[13]
    v[12] = v[13] - v[2] - v[3]
    return v


def levels_at(b):
    v = {}
    for l in LEAVES:
        v[l.line] = b["V%d" % l.line]
    for p, a, bb in SUBS:
        av = b["VA%d" % p]
        v[a], v[bb] = av, v[p] - av
    v[13] = sum(v[l.line] for l in LEAVES)
    v[54] = b["VDISC"]
    v[1] = v[13] + v[54]
    v[2] = b["VN"]
    for l in ISS_DETAILS:
        v[l.line] = b["VD%d" % l.line]
    v[3] = sum(v[l.line] for l in ISS_DETAILS)
    v[12] = b["V12"]
    return v


def fmt_cell(x):
    return "ND" if x is None else str(x)


def gen_world(last="2026:Q2", seed=7, revise=None, bo=None, out_tweak=None):
    """The 14 member files of a synthetic release, and raw[code][quarter] (ints, None for ND). Every identity of 2.3 holds by construction unless out_tweak breaks it."""
    rng = Lcg(seed)
    qs = world_quarters(last)
    base = {}
    for q in qs:
        b = {}
        for l in LEAVES:
            lo, hi = (-9000, 1500) if l.line == 14 else (-1500, 9000)
            b["L%d" % l.line] = rng.next(lo, hi)
        for p, a, bb in SUBS:
            b["A%d" % p] = rng.next(-800, 800)
        b["N"] = rng.next(-2000, 6000)
        for l in ISS_DETAILS:
            b["D%d" % l.line] = rng.next(-500, 3000)
        b["GA"] = rng.next(-700, 700)
        for l in LEAVES:
            b["V%d" % l.line] = rng.next(1000, 90000) * 10
        for p, a, bb in SUBS:
            b["VA%d" % p] = rng.next(-300, 300) * 10
        b["VN"] = rng.next(1000, 90000) * 10
        for l in ISS_DETAILS:
            b["VD%d" % l.line] = rng.next(1000, 9000) * 10
        b["V12"] = rng.next(1000, 90000) * 10
        b["VGA"] = rng.next(-2000, 2000) * 10
        b["VDISC"] = rng.next(-5000, 5000) * 10
        base[q] = b
    for (q, key), d in (revise or {}).items():
        if q in base:
            base[q][key] += d
    if bo:
        for q in qs:
            bo(q, base[q])
    raw = collections.OrderedDict()
    zero = lambda key, q: 0
    for q in qs:
        b = base[q]
        fu = flows_at(b, q, 1, zero)
        fa = flows_at(b, q, 4, adj_fa)
        lv = levels_at(b)
        ga = b["GA"]
        for l in F35:
            if l.fu:
                raw.setdefault(l.fu, {})[q] = None if q == "1945:Q4" else fu[l.line]
                raw.setdefault(l.fa, {})[q] = None if q <= "1951:Q4" else fa[l.line]
            raw.setdefault(l.lvl, {})[q] = lv[l.line]
        raw.setdefault(GA.fu, {})[q] = None if q == "1945:Q4" else ga
        raw.setdefault(SA.fu, {})[q] = None if q == "1945:Q4" else fu[30] - ga
        raw.setdefault(GA.lvl, {})[q] = b["VGA"]
        raw.setdefault(SA.lvl, {})[q] = lv[30] - b["VGA"]
    files = {}
    heads = {"F3_5_t_tu": [l.fu for l in F35 if l.fu], "F3_5_t": [l.fa for l in F35 if l.fa], "F3_5_s": [l.lvl for l in F35],
             "S1281_1_t_tu": ["FU544090075.Q", GA.fu, "FU543020075.Q"], "S1281_1_s": ["FL544090075.Q", GA.lvl],
             "S1281_2_t_tu": ["FU544090085.Q", SA.fu], "S1281_2_s": ["FL544090085.Q", SA.lvl]}
    for fb, head in heads.items():
        lines = ["date," + ",".join(head)]
        for q in qs:
            vals = []
            for c in head:
                x = raw[c][q] if c in raw else 777
                if x is not None and out_tweak and (fb, c, q) in out_tweak:
                    x += out_tweak[(fb, c, q)]
                vals.append(fmt_cell(x))
            lines.append(q + "," + ",".join(vals))
        files["%s.csv" % fb] = ("\n".join(lines) + "\n").encode("utf-8")
        d = []
        for c in head:
            l = CODE_LINE.get(c)
            if l is None:
                d.append("%s\tDecoy series; not used\tLine 99\tZ.1 decoy table\tMillions of dollars" % c)
                continue
            kind = "s" if fb.endswith("_s") else "t"
            tab = ("F3.5.%s Corporate and foreign bonds" % kind) if l.table == "F3.5" else ("%s.%s Life insurance companies" % (S1281_TABLE_MARK[l.table].upper().replace("S1281", "S1281"), kind))
            d.append("%s\t%s; corporate and foreign bonds; asset\tLine %d\t%s\tMillions of dollars" % (c, "; ".join(l.keys), l.line, tab))
        files["data_dictionary/%s.txt" % fb] = ("\n".join(d) + "\n").encode("utf-8")
    return files, raw


def prov_rows(files, zip_sha, lm_iso, members=616, zbytes=8336582):
    rows = [{"kind": "zip", "name": ZIP_NAME, "sha256": zip_sha, "bytes": str(zbytes), "last_modified": lm_iso, "members": str(members)}]
    for z, cname in FIXED_MEMBERS.items():
        if cname in files:
            data = files[cname]
            rows.append({"kind": "member", "name": cname, "sha256": sha256_of(data), "bytes": str(len(data)), "last_modified": "", "members": ""})
    return rows


def make_rel(key, files, lm_iso=None, folder=None):
    lm_iso = lm_iso or "%s-%s-%sT16:00:19Z" % (key[:4], key[4:6], key[6:])
    tables = {b: Table(b, files["%s.csv" % b]) for b in REQUIRED_CSV}
    dicts = {b: parse_dictionary(files["data_dictionary/%s.txt" % b]) for b in REQUIRED_CSV}
    prov = prov_rows(dict(files), sha256_of(("zip" + key).encode()), lm_iso)
    return Rel(key, tables, dicts, prov, [], folder)


def write_release(cache, key, files, lm_iso=None):
    lm_iso = lm_iso or "%s-%s-%sT16:00:19Z" % (key[:4], key[4:6], key[6:])
    folder = os.path.join(cache, key)
    for cname in list(files):
        write_bytes(os.path.join(folder, cname), files[cname])
    prov = prov_rows(files, sha256_of(("zip" + key).encode()), lm_iso)
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(PROV_COLS)
    for r in prov:
        w.writerow([r[c] for c in PROV_COLS])
    write_text(os.path.join(folder, "provenance.csv"), out.getvalue())
    return folder


_WORLD = {}


def get_world():
    """The base synthetic releases (built once, no mutant active): sep (last 2026:Q2) and dec (last 2026:Q3, with 2025:Q1 mutual funds revised by +1000)."""
    if not _WORLD:
        fs, rs = gen_world("2026:Q2")
        fd, rd = gen_world("2026:Q3", revise={("2025:Q1", "L37"): 1000})
        _WORLD["sep"], _WORLD["sep_raw"] = make_rel("20260911", fs), rs
        _WORLD["dec"], _WORLD["dec_raw"] = make_rel("20261210", fd), rd
        _WORLD["sep_files"], _WORLD["dec_files"] = fs, fd
    return _WORLD


def get_world_c():
    if "c" not in _WORLD:
        w = get_world()
        _WORLD["c"] = compute({"rels": [w["sep"], w["dec"]], "fetch_rows": [], "old_vint": {}})
    return _WORLD["c"]


def psum(raw, code, qs):
    return sum(raw[code][q] for q in qs)


def line_codes(lines, kind="fu"):
    return [BYLINE[n].fu if kind == "fu" else (BYLINE[n].fa if kind == "fa" else BYLINE[n].lvl) for n in lines]


def Dm(x):
    return Decimal(x)


WAVEQ = qrange("2024:Q1", "2026:Q2")
Y18 = qrange("2018:Q1", "2018:Q4")


# ---- tests ----
def t_g1(ck):
    txt = "date,FU543063005.A,FU543063005.Q,FU513063005.Q\n2024:Q1,111,222,333\n2024:Q2,ND,444,\n"
    t = Table("F3_5_t_tu", txt.encode())
    s = t.series("FU543063005.Q")
    ck.eq("a column is chosen by its code in the header, whatever the order (a decoy .A column comes first)", [s["2024:Q1"], s["2024:Q2"]], [Dm(222), Dm(444)])
    ck.eq("...and the .Q suffix is part of the code", t.col("FU543063005.A"), 1)
    s2 = t.series("FU513063005.Q")
    ck.eq("ND and a blank cell are missing, never zero", [s2["2024:Q1"], s2["2024:Q2"]], [Dm(333), None])
    ck.eq("a byte-order mark does not break the first header", Table("x", b"\xef\xbb\xbf" + txt.encode()).series("FU543063005.Q")["2024:Q1"], Dm(222))
    ck.eq("a window sum is an exact Decimal sum", dsum([Dm("0.1"), Dm("0.2"), Dm("0.3")]), Dm("0.6"))
    ck.raises("a YYYYQN date is refused", DataError, lambda: qidx("2024Q1"))
    ck.eq("a YYYY:QN date is read", qidx("2024:Q2") - qidx("2024:Q1"), 1)
    ck.raises("a header without 'date' first is refused", DataError, lambda: Table("x", b"quarter,FU1.Q\n2024:Q1,1\n"))
    ck.raises("a non-numeric cell is refused", DataError, lambda: Table("x", b"date,A.Q\n2024:Q1,abc\n").series("A.Q"))
    ck.eq("the Decimal context has precision 28", decimal.getcontext().prec, 28)


def flow_for(rel, basis, g, qs):
    return dsum([wsum(rel, basis, l, qs) for l in group_lines(g)])


def t_g2(ck):
    w = get_world()
    rel, raw = w["sep"], w["sep_raw"]
    ck.eq("the mapping is sound (28 leaves, each in exactly one of the nine groups, no sub-line, detail or line 54)", mapping_problems(), [])
    for g, lines in EXPECT_GROUPS.items():
        ck.eq("group %s holds exactly its lines" % g, sorted(l.line for l in group_lines(g)), sorted(lines))
    ck.eq("the holder groups are nine and the derived row is not among them", nine(), GROUPS9)
    for g, lines in EXPECT_GROUPS.items():
        want = sum(psum(raw, BYLINE[n].fu, Y18) for n in lines)
        ck.eq("the 2018 net acquisition of %s sums its own lines only" % g, flow_for(rel, "fu", g, Y18), Dm(want))
    ck.eq("domestic financial is line 3, not line 3 plus its details", flow_for(rel, "fu", "iss_domfin", Y18), Dm(psum(raw, BYLINE[3].fu, Y18)))
    ck.eq("the life-insurer general account is its own line", flow_for(rel, "fu", "ins_life_ga", Y18), Dm(psum(raw, GA.fu, Y18)))
    ht = holders_total(rel, "2018:Q4")
    ck.eq("the level denominator is the sum of the 28 leaf levels, not plus line 54", ht, Dm(sum(raw[BYLINE[n].lvl]["2018:Q4"] for n in sum(EXPECT_GROUPS.values(), []))))
    bad = [x for x in flow_identity_residuals(rel, "fu") if x[2] != 0]
    ck.eq("every flow identity of the synthetic release closes (line 8 included in lines 4-11 = line 3)", bad[:2], [])


def tweaked(cell_file, code, q, delta, key="20260911"):
    files, raw = gen_world("2026:Q2", out_tweak={(cell_file, code, q): delta})
    return make_rel(key, files)


def t_g3(ck):
    w = get_world()
    rel = w["sep"]
    ck.eq("clean synthetic release: C04 PASS on both bases", c04(rel)[0], "PASS")
    ck.eq("clean synthetic release: C05 level identities PASS (28 leaves = line 13; line 54 = line 1 - line 13)", level_identity_residuals(rel) and id_status(level_identity_residuals(rel), Decimal(2)), "PASS")
    r18 = tweaked("F3_5_t_tu", BYLINE[37].fu, "2018:Q2", 5)
    ck.eq("the 28 leaves missing line 13 by 5 $mn in 2018 is a FAIL", c04(r18)[0], "FAIL")
    r05 = tweaked("F3_5_t_tu", BYLINE[37].fu, "2005:Q2", 5)
    ck.eq("the same miss in 2005 is a WARN", c04(r05)[0], "WARN")
    rg = tweaked("S1281_1_t_tu", GA.fu, "2019:Q3", 5)
    ck.eq("general + separate accounts missing line 30 by 5 $mn is a FAIL", c04(rg)[0], "FAIL")
    rl = tweaked("F3_5_s", BYLINE[37].lvl, "2018:Q2", 50)
    ck.eq("a level miss of 50 $mn in 2018 fails C05", c05(rl)[0], "FAIL")
    ck.ok("C05 names the pinned differences of line 1 and line 13", "line 1 - line 13" in c05(rel)[2], c05(rel)[2][:100])
    ck.eq("the pinned differences fail on 20260911 (synthetic) and only warn on the later release", (c05(rel)[0], c05(w["dec"])[0]), ("FAIL", "WARN"))
    ck.eq("a pin fails on the 20260911 release", pin_status(rel, ["x"]), "FAIL")
    ck.eq("...and warns on a later one", pin_status(w["dec"], ["x"]), "WARN")


def sep_rows(rel=None):
    rel = rel or get_world()["sep"]
    return widx(window_rows(rel))


def t_g4(ck):
    w = get_world()
    d = {n: (a, b, len(qrange(a, b))) for n, a, b in window_defs("2026:Q2")}
    ck.eq("wave is 2024:Q1-2026:Q2, 10 quarters", d["wave"], ("2024:Q1", "2026:Q2", 10))
    ck.eq("pre1719 is 12 quarters and pre2223 is 8", (d["pre1719"][2], d["pre2223"][2]), (12, 8))
    ck.ok("wave_ext is not defined on a September release", "wave_ext" not in d, str(sorted(d)))
    dd = {n: (a, b, len(qrange(a, b))) for n, a, b in window_defs("2026:Q3")}
    ck.eq("on a December release wave stays 10 quarters", dd["wave"], ("2024:Q1", "2026:Q2", 10))
    ck.eq("...and wave_ext runs to the latest quarter, 11 quarters", dd["wave_ext"], ("2024:Q1", "2026:Q3", 11))
    ix = sep_rows(w["sep"])
    ck.ok("no wave_ext row is written on the September release", not any(k[0] == "wave_ext" for k in ix), "")
    ixd = widx(window_rows(w["dec"]))
    r = ixd[("wave_ext", "holder", "total", "fu")]
    ck.eq("wave_ext on the December fixture has 11 quarters", (r["from_quarter"], r["to_quarter"], r["n_quarters"]), ("2024:Q1", "2026:Q3", "11"))
    r = ixd[("wave", "holder", "total", "fu")]
    ck.eq("wave on the December fixture is 2024:Q1-2026:Q2, 10 quarters", (r["from_quarter"], r["to_quarter"], r["n_quarters"]), ("2024:Q1", "2026:Q2", "10"))
    raw = w["sep_raw"]
    want = Dm(sum(raw[BYLINE[37].fa][q] for q in Y18)) / 4
    got = Dm(ix[("y2018", "holder", "funds_mutual", "fa_div4")]["flow_usd_mn"])
    ck.eq("fa_div4 is the annual-rate value divided by 4", got, want)
    r = ix[("wave", "holder", "ins", "fu")]
    ck.eq("the per-quarter average divides by n_quarters (10)", Dm(r["avg_per_quarter_usd_mn"]), (Dm(r["flow_usd_mn"]) / 10).quantize(Dm("0.001")))
    ck.eq("the wave flow of insurers is its two lines over 2024:Q1-2026:Q2", Dm(r["flow_usd_mn"]), Dm(psum(raw, BYLINE[27].fu, WAVEQ) + psum(raw, BYLINE[30].fu, WAVEQ)))


def bo_negleaf(q, b):
    """Money market funds (a leaf of `other`) are strongly negative in every quarter: a positive group with a negative leaf."""
    b["L36"] = -20000


def t_g5(ck):
    files, raw = gen_world("2026:Q2", bo=bo_negleaf)
    rel = make_rel("20260911", files)
    ix = widx(window_rows(rel))
    tot = ix[("wave", "holder", "total", "fu")]
    T = Dm(psum(raw, BYLINE[13].fu, WAVEQ))
    ck.eq("the total row is line 13", Dm(tot["flow_usd_mn"]), T)
    shares, pos, posflows = [], [], {}
    for g in GROUPS9:
        r = ix[("wave", "holder", g, "fu")]
        f = Dm(sum(psum(raw, BYLINE[n].fu, WAVEQ) for n in EXPECT_GROUPS[g]))
        ck.eq("%s: share of the net is 100 x its window sum / line 13's window sum" % g, Dm(r["share_of_total_pct"]), (100 * f / T).quantize(Dm("0.001"), rounding=decimal.ROUND_HALF_EVEN))
        shares.append(Dm(r["share_of_total_pct"]))
        if f > 0:
            posflows[g] = f
            ck.ok("%s: a share of the positive flows is written" % g, r["share_of_positive_pct"] != "", "")
        else:
            ck.eq("%s: no share of the positive flows for a flow that is not positive" % g, r["share_of_positive_pct"], "")
    ck.ok("the nine shares of the net sum to 100 within 0.01 (a negative group stays negative)", abs(sum(shares) - 100) <= Dm("0.01"), str(sum(shares)))
    ck.ok("the synthetic household line is negative", Dm(ix[("wave", "holder", "hh_residual", "fu")]["flow_usd_mn"]) < 0, "")
    P = sum(posflows.values())
    ck.eq("the positive total is over the nine groups", Dm(tot["positive_total_usd_mn"]), P.quantize(Dm("0.001")))
    ck.ok("the shares of the positive flows sum to 100", abs(sum(Dm(ix[("wave", "holder", g, "fu")]["share_of_positive_pct"]) for g in posflows) - 100) <= Dm("0.01"), "")
    leaves = sum(abs(psum(raw, BYLINE[n].fu, WAVEQ)) for n in sum(EXPECT_GROUPS.values(), []))
    ck.eq("the offset ratio is |line 13| over the sum of the 28 leaves' absolute window sums", Dm(tot["offset_ratio"]), (abs(T) / Dm(leaves)).quantize(Dm("0.0001"), rounding=decimal.ROUND_HALF_EVEN))
    ck.eq("a ratio of 0.4999 is flagged offsetting", stability_flag(Dm(1), Dm("0.4999")), "offsetting")
    ck.eq("a ratio of 0.5 is ok", stability_flag(Dm(1), Dm("0.5")), "ok")
    ck.eq("a non-positive total is void", stability_flag(Dm(0), Dm("0.9")), "void_nonpositive_total")
    ck.eq("the total row has no share of the positive flows", tot["share_of_positive_pct"], "")
    ck.ok("fixture is valid: `other` is positive although one of its leaves is negative", Dm(ix[("wave", "holder", "other", "fu")]["flow_usd_mn"]) > 0 and psum(raw, BYLINE[36].fu, WAVEQ) < 0, "")
    ck.eq("the stability flag is written on every row of the window", {r["stability_flag"] for k, r in ix.items() if k[0] == "wave" and k[1] == "holder" and k[3] == "fu"}, {tot["stability_flag"]})


def bo_extremes(q, b):
    """Two wave quarters whose insurer share is very different: 50% of a small net, then 0.01% of a large one."""
    if q in ("2024:Q1", "2024:Q2"):
        for l in LEAVES:
            b["L%d" % l.line] = 0
        for p, a, bb in SUBS:
            b["A%d" % p] = 0
        if q == "2024:Q1":
            b["L30"], b["L51"] = 1000, 1000
        else:
            b["L30"], b["L51"] = 10, 99990


def t_g6(ck):
    files, raw = gen_world("2026:Q2", bo=bo_extremes)
    rel = make_rel("20260911", files)
    ix = widx(window_rows(rel))
    r = ix[("wave", "holder", "ins", "fu")]
    qsh = [Dm(raw[BYLINE[27].fu][q] + raw[BYLINE[30].fu][q]) / Dm(raw[BYLINE[13].fu][q]) * 100 for q in WAVEQ]
    ratio = 100 * Dm(psum(raw, BYLINE[27].fu, WAVEQ) + psum(raw, BYLINE[30].fu, WAVEQ)) / Dm(psum(raw, BYLINE[13].fu, WAVEQ))
    ck.ok("fixture is valid: the mean of quarterly shares differs from the ratio of sums by more than 1 pp", abs(sum(qsh) / 10 - ratio) > 1, "%s vs %s" % (sum(qsh) / 10, ratio))
    ck.eq("a window share is the ratio of window sums, not the mean of quarterly shares", Dm(r["share_of_total_pct"]), ratio.quantize(Dm("0.001"), rounding=decimal.ROUND_HALF_EVEN))
    wr = window_rows(get_world()["sep"])
    hl = headline_rows(get_world()["sep"], wr)
    ck.eq("exactly one ins_share_wave_pct row", sum(1 for h in hl if h[1] == "ins_share_wave_pct"), 1)
    ck.eq("rank_wave ranks the seven groups only", sorted(h[4] for h in hl if h[1] == "rank_wave"), sorted(RANKED7))
    ck.eq("headline.csv is on the fu basis", {h[3] for h in hl}, {"fu"})
    ck.eq("group_share_wave_pct has the nine groups and the derived row", sorted(h[4] for h in hl if h[1] == "group_share_wave_pct"), sorted(GROUPS9 + [HHPF]))
    ck.eq("iss_share_wave_pct has the three issuer groups", sorted(h[4] for h in hl if h[1] == "iss_share_wave_pct"), sorted(ISS3))
    ranks = sorted(int(h[6]) for h in hl if h[1] == "rank_wave")
    ck.eq("the ranks are 1 to 7 on distinct flows", ranks, list(range(1, 8)))
    ck.quiet("headline.csv renders: no verdict word is written", lambda: render_csv("headline.csv", hl, "# source: test"))
    ck.raises("a verdict word in a cell is refused", DataError, lambda: render_csv("headline.csv", [[x if i != 7 else "ABOVE_BAND" for i, x in enumerate(h)] for h in hl[:1]], "# source: test"))


def t_g7(ck):
    w = get_world()
    rel, raw = w["sep"], w["sep_raw"]
    rows = {(r["quarter"], r["group"]): r for r in level_share_rows(rel)}
    q = "2019:Q4"
    leaf_sum = sum(raw[BYLINE[n].lvl][q] for n in sum(EXPECT_GROUPS.values(), []))
    for g in ("ins", "row", "hh_residual"):
        lv = sum(raw[BYLINE[n].lvl][q] for n in EXPECT_GROUPS[g])
        r = rows[(q, g)]
        ck.eq("level share of %s is over the sum of the 28 leaf levels" % g, Dm(r["share_of_holders_pct"]), (100 * Dm(lv) / Dm(leaf_sum)).quantize(Dm("0.001"), rounding=decimal.ROUND_HALF_EVEN))
        ck.eq("line 54 is printed beside it (%s)" % g, Dm(r["discrepancy_usd_mn"]), Dm(raw[BYLINE[54].lvl][q]))
    ck.eq("the level quarters are 2016:Q4, 2019:Q4, 2021:Q4, 2023:Q4 and the latest", level_share_quarters(rel), ["2016:Q4", "2019:Q4", "2021:Q4", "2023:Q4", "2026:Q2"])
    ck.eq("an LM code is lm_market", valuation_of("LM153063005.Q"), "lm_market")
    ck.eq("an FL code is fl_unspecified, never market value or book", valuation_of("FL893063005.Q"), "fl_unspecified")
    ck.ok("the levels ledger labels no FL code lm_market", all((r["valuation"] == "fl_unspecified") == r["series_code"].startswith("FL") for r in levels_rows(rel)[:200]), "")


def t_g8(ck):
    w = get_world()
    rel, raw = w["sep"], w["sep_raw"]
    rows = {(r["window"], r["group"]): r for r in level_change_rows(rel)}
    r = rows[("wave", "row")]
    start, end = raw[BYLINE[51].lvl]["2023:Q4"], raw[BYLINE[51].lvl]["2026:Q2"]
    flow_ = psum(raw, BYLINE[51].fu, WAVEQ)
    ck.eq("the start level is the quarter before the window (2023:Q4)", Dm(r["level_start_usd_mn"]), Dm(start))
    ck.eq("the end level is the window's last quarter", Dm(r["level_end_usd_mn"]), Dm(end))
    ck.eq("change minus flow is end - start - the window's net acquisition", Dm(r["change_minus_flow_usd_mn"]), Dm(end - start - flow_))
    text = render_readme(get_world_c())
    ck.ok("the README never calls the residual revaluation", "evaluation" not in text and "price changes and other changes in volume" in text.lower(), "")
    ck.ok("the README says the household gap is not a measured price effect", "is not a measured price effect" in text, "")


def t_g9(ck):
    w = get_world()
    sep, dec = w["sep"], w["dec"]
    ck.eq("one release: no revision rows", revision_rows([sep]), [])
    rv = revision_rows([sep, dec])
    ck.ok("two releases: rows exist", len(rv) > 100, str(len(rv)))
    ck.ok("no row compares a release with itself", all(r["release_prev"] != r["release_new"] for r in rv), "")
    keys = [(r["window"], r["side"], r["group"], r["basis"]) for r in rv]
    ck.eq("every key is unique", len(keys), len(set(keys)))
    ck.eq("regenerated, not appended: rows passed in are ignored", len(revision_rows([sep, dec], existing=rv)), len(rv))
    row = [r for r in rv if (r["window"], r["side"], r["group"], r["basis"]) == ("wave", "holder", "funds_mutual", "fu")][0]
    want_new = psum(w["dec_raw"], BYLINE[37].fu, WAVEQ)
    ck.eq("wave on the December release is the same 10 quarters", Dm(row["flow_new_usd_mn"]), Dm(want_new))
    ck.eq("the revised quarter shows in the revision (+1000 $mn)", Dm(row["flow_new_usd_mn"]) - Dm(row["flow_prev_usd_mn"]), Dm(1000))
    ck.ok("wave_ext is in no revision row (it exists only on the later release)", not any(r["window"] == "wave_ext" for r in rv), "")


def t_g10(ck):
    ck.eq("1.9996 pp is STABLE on the unrounded Decimal (it rounds to 2.000)", registered_label(Dm("1.9996")), "STABLE")
    ck.eq("2.0000 pp is MOVED", registered_label(Dm("2.0000")), "MOVED")
    ck.eq("2.0004 pp is MOVED", registered_label(Dm("2.0004")), "MOVED")
    ck.eq("0.4 pp is STABLE", registered_label(Dm("0.4")), "STABLE")
    w = get_world()
    ck.eq("the statement constants reproduce the canonical text of 4.6", prereg_ok(), True)
    rows = registered_rows([w["sep"]])
    ck.eq("a statement is never scored on the September release alone: all three are PENDING", [r[10] for r in rows], ["PENDING"] * 3)
    ck.eq("...with no release_new", [r[5] for r in rows], [""] * 3)
    rows = registered_rows([w["sep"], w["dec"]])
    ck.eq("with the December release cached the three statements are scored", [r[0] for r in rows], ["SREV", "SREV-F", "SREV-R"])
    ck.ok("...with a label of STABLE or MOVED", all(r[10] in ("STABLE", "MOVED") for r in rows), str([r[10] for r in rows]))
    ck.eq("...against release 20261210", {r[5] for r in rows}, {"20261210"})
    sep_raw = w["sep_raw"]
    ins = Dm(psum(sep_raw, BYLINE[27].fu, WAVEQ) + psum(sep_raw, BYLINE[30].fu, WAVEQ))
    fund = Dm(sum(psum(sep_raw, BYLINE[n].fu, WAVEQ) for n in (37, 38, 39, 40)))
    T = Dm(psum(sep_raw, BYLINE[13].fu, WAVEQ))
    ck.eq("SREV base share = 100 x (life + P&C) / line 13", Dm(rows[0][6]), (100 * ins / T).quantize(Dm("0.001"), rounding=decimal.ROUND_HALF_EVEN))
    ck.eq("SREV-F base share includes interval funds (lines 37 to 40)", Dm(rows[1][6]), (100 * fund / T).quantize(Dm("0.001"), rounding=decimal.ROUND_HALF_EVEN))
    ck.eq("SREV-F is revised by the +1000 $mn in 2025:Q1 (only the funds line moves)", Dm(rows[1][7]) > Dm(rows[1][6]) or Dm(rows[1][7]) < Dm(rows[1][6]), True)
    with mutant("g10_const_edit"):
        ck.raises("a constant edited so the text's sha256 changes: registered.csv is refused", DataError, lambda: registered_rows([w["sep"], w["dec"]]))
    ck.eq("the canonical text is the 755 bytes the spec hashes", len(prereg_text().encode("utf-8")), 755)


def zip_fixture(extra=(), members=True):
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as z:
        if members:
            for zname in FIXED_MEMBERS:
                z.writestr(zname, b"date,X.Q\n2024:Q1,1\n" if zname.endswith(".csv") else b"X.Q\tdesc\tLine 1\tT\tU\n")
        for n in extra:
            z.writestr(n, b"evil")
        z.writestr("csv/F4_1_s.csv", b"not used")
    return bio.getvalue()


def tree_files(root):
    out = []
    for dp, dn, fn in os.walk(root):
        for f in fn:
            out.append(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/"))
    return sorted(out)


def t_g11(ck):
    src = read_file(os.path.abspath(__file__), "r")
    ck.eq("the script's own source passes the zip scan (no extractall, no path from a member name)", zip_ast_problems(src), [])
    bad = {"extractall": "import zipfile\ndef f(b, d):\n    zipfile.ZipFile(b).extractall(d)\n",
           "extract": "def f(z, d):\n    z.extract('a', d)\n",
           "a path from namelist": "import os\ndef f(z, d):\n    for n in z.namelist():\n        open(os.path.join(d, n), 'wb').write(z.read(n))\n",
           "a path from filename": "def f(z, d):\n    for i in z.infolist():\n        write_bytes(d + '/' + i.filename, z.read(i))\n",
           "a path from a derived name": "def f(z, d):\n    names = z.namelist()\n    n = names[0]\n    write_text(d + n, 'x')\n"}
    for k, s in bad.items():
        ck.ok("the zip scan reports: %s" % k, bool(zip_ast_problems(s)), "not reported")
    good = "def f(z, d):\n    data = z.read('csv/F3_5_t.csv')\n    write_bytes(d + '/F3_5_t.csv', data)\n"
    ck.eq("reading a member by an exact constant name and writing a fixed file name is allowed", zip_ast_problems(good), [])
    with tempfile.TemporaryDirectory(prefix="z1cb_g11_", ignore_cleanup_errors=True) as tmp:
        cache = os.path.join(tmp, "a", "cache")
        body = zip_fixture(extra=("../../x.csv", "csv/../../../y.csv", "/abs.csv", "csv/evil/../z.csv"))
        n, missing = cache_zip(body, "20260911", cache, "2026-09-11T16:00:19Z")
        files = tree_files(os.path.join(tmp, "a"))
        ck.eq("14 members written", (n, missing), (14, []))
        ck.ok("nothing is written outside the release folder (no ../x.csv, no absolute path, no zip)", all(f.startswith("cache/20260911/") for f in files), str([f for f in files if not f.startswith("cache/20260911/")]))
        ck.ok("no other member of the 600-odd is written (F4_1_s.csv)", not any("F4_1" in f for f in files), "")
        ck.eq("the 14 fixed names and provenance.csv are all that is written", len(files), 15)
        h, rows = read_csv_rows(os.path.join(cache, "20260911", "provenance.csv"))
        ck.eq("provenance.csv: a zip row first, then 14 member rows", (h, rows[0][0], len(rows)), (PROV_COLS, "zip", 15))
        ck.eq("the zip row holds the digest of the whole archive and its member count", (rows[0][2], rows[0][5]), (sha256_of(body), str(len(zipfile.ZipFile(io.BytesIO(body)).namelist()))))


def t_g12(ck):
    ck.eq("SPEC_ALLOW_SHA256 is the hash of the canonical allowlist text", allow_text(), SPEC_ALLOW_TEXT)
    ck.eq("...and the text hashes to it", allow_hash_ok(), True)
    ck.eq("the allowlist has twelve lines", len(ALLOW_ORDER), 12)
    good = allowlist("checks.csv")
    ck.quiet("the exact header passes", lambda: check_header("checks.csv", good))
    ck.raises("an extra column fails", DataError, lambda: check_header("checks.csv", good + ["extra"]))
    ck.raises("a renamed column fails", DataError, lambda: check_header("checks.csv", ["check_id", "description", "expected", "seen", "status"]))
    ck.raises("windows.csv: a renamed share column fails", DataError, lambda: check_header("windows.csv", [c if c != "share_of_total_pct" else "share_of_net_pct" for c in ALLOW["windows.csv"]]))
    text = "# source: x\n" + ",".join(good) + "\nC01,d,e,o,PASS\n"
    ck.eq("the # source: line is skipped, not read as the header", csv_body(text)[0], good)
    clean = {n: "# source: x\n" + ",".join(ALLOW[n]) + "\n" for n in ALLOW_ORDER}
    clean["README.md"] = "x\n"
    clean["SOURCES.md"] = "x\n"
    ck.eq("a clean folder has no leak problem", leak_problems(clean), [])
    ck.eq("a clean folder has no header problem", header_problems(clean), [])
    c13 = dict(clean)
    c13["tic_check.csv"] = "# source: x\na,b\n"
    ck.ok("a thirteenth CSV (tic_check.csv) is reported", any("tic_check.csv" in p for p in leak_problems(c13)), "")
    c13 = dict(clean)
    c13["tests.csv"] = "# source: x\na,b\n"
    ck.ok("a thirteenth CSV (tests.csv) is reported", any("tests.csv" in p for p in leak_problems(c13)), "")
    dup = dict(clean)
    dup["vintages.csv"] = clean["vintages.csv"] + "20260911,/p,s,1,2,3\n20260911,/p,s,1,2,3\n"
    ck.ok("a duplicate key is reported", bool(dup_key_problems(dup)), "")
    lv = dict(clean)
    lv["levels.csv"] = clean["levels.csv"] + "20260911,2024:Q1,LM1.Q,14,F3.5,holder,hh_residual,fl_book,5.000\n"
    ck.ok("fl_book is not an allowed valuation", any("fl_book" in p for p in value_problems(lv)), str(value_problems(lv)))
    nn = dict(clean)
    nn["windows.csv"] = clean["windows.csv"] + "20260911,wave,2024:Q1,2026:Q2,10,holder,holder,none,fu,1.000,0.100,1.000,1.000,,1.000,0.9000,ok\n"
    ck.ok("group none is allowed only in quarterly.csv and levels.csv", any("none" in p for p in value_problems(nn)), str(value_problems(nn)))
    good_sh = ("z1cb_leak_check() {\n" + "".join("      %s) want='%s' ;;\n" % tuple(l.split(":", 1)) for l in SPEC_ALLOW_TEXT.splitlines()) + "}\n")
    ck.eq("a check.sh with its own literal copy passes", checksh_problems(good_sh), [])
    bad_sh = good_sh.replace("      quarterly.csv) want=", "      quarterly.csv) want=$(python3 bin/z1_corporate_bond_holders.py) #", 1)
    ck.ok("a check.sh that reads the headers from the script is reported", bool(checksh_problems(good_sh.replace("}\n", "  python3 bin/z1_corporate_bond_holders.py allow\n}\n"))), "")
    ck.ok("a check.sh with an altered literal header is reported", bool(checksh_problems(bad_sh)), "")


def t_g13(ck):
    clean = {n: "# source: x\n" + ",".join(ALLOW[n]) + "\n1,2,3\n" for n in ALLOW_ORDER}
    clean["README.md"] = "A plain README.\n"
    clean["SOURCES.md"] = "Plain sources.\n"
    ck.eq("on the clean folder the leak guard passes", leak_problems(clean), [])
    ck.ok("the check digit test accepts a real CUSIP-shaped token and rejects a wrong one", cusip_ok("037833100") and not cusip_ok("037833101"), "")
    bad = dict(clean)
    bad["release.zip"] = b"PK\x03\x04junk"
    ck.ok("a .zip is reported as a raw file", any("raw or forbidden" in p and "release.zip" in p for p in leak_problems(bad)), str(leak_problems(bad)))
    bad = dict(clean)
    bad["cslt.json"] = "{}"
    ck.ok("a .json is reported as a raw file", any("raw or forbidden" in p and "cslt.json" in p for p in leak_problems(bad)), str(leak_problems(bad)))
    bad = dict(clean)
    bad["STOP_z1cb"] = "status: 403\n"
    ck.ok("a STOP file is reported", any("STOP_z1cb" in p for p in leak_problems(bad)), "")
    bad = dict(clean)
    bad["checks.csv"] = clean["checks.csv"] + "C99,a 037833100 b,e,o,PASS\n"
    ck.ok("a valid CUSIP in a CSV is reported", any("CUSIP" in p for p in leak_problems(bad)), "")
    bad = dict(clean)
    bad["checks.csv"] = clean["checks.csv"] + "C99,a 037833101 b,e,o,PASS\n"
    ck.eq("a nine-character token that fails the check digit is not a CUSIP", [p for p in leak_problems(bad) if "CUSIP" in p], [])
    bad = dict(clean)
    bad["SOURCES.md"] = "see /Users/someone/file\n"
    ck.ok("a /Users/ path in SOURCES.md is reported", any("local path" in p for p in leak_problems(bad)), "")
    bad = dict(clean)
    bad["README.md"] = "write to a@b\n"
    ck.ok("an at sign is reported", any("at sign" in p for p in leak_problems(bad)), "")


OPENING = ("This folder shows which kinds of holders took the net increase in US corporate and foreign bonds from 2024Q1 to 2026Q2, in the Federal Reserve's financial accounts "
           "(Z.1 table F3.5, release 20260911). US insurers (life and property-casualty) took 33.26% of the all-sector net, $741.2bn of $2,228.4bn (unadjusted basis, 2024Q1-2026Q2), "
           "ranking third of seven holder groups, behind registered funds and the rest of the world.")
R13 = ("The instrument is all corporate and foreign bonds: investment grade and high yield, financial issuers, private-label ABS and MBS, and foreign bonds held by US residents. "
       "Z.1 has no line for the AI issuers, so this table cannot say who took their bonds.")
R17 = ("Only uncollateralised coinsurance moves the bonds to the reinsurer, which is in the rest of the world if it is offshore. Under funds withheld and modified coinsurance the US insurer "
       "keeps investing the assets, and US captives are brought into the life sector (Board FEDS Note, 12 Oct 2018). The size of each structure is unknown, so the insurer line may be "
       "understated by an unknown amount. Bonds held through funds sit in the fund sectors.")


def t_g14(ck):
    for name, s in (("the opening template", OPENING), ("the R1-3 sentences", R13), ("the R1-4 sentence", SHARE_EXPLAIN), ("the R1-7 sentences", R17), ("the disclosure sentence", DISCLOSURE_SENTENCE)):
        ck.eq("%s passes" % name, wording_problems("README.md", s), [])
    ck.eq("the denial sentence is exempt, once", wording_problems("README.md", "Intro. " + DENIAL_SENTENCE + " Outro."), [])
    ck.ok("a second copy of the denial sentence is not exempt", bool(wording_problems("README.md", DENIAL_SENTENCE + "\n" + DENIAL_SENTENCE)), "")
    ck.ok("the denial sentence is not exempt outside the README", bool(wording_problems("checks.csv", DENIAL_SENTENCE)), "")
    ck.ok("a sentence that merely contains 'who bought' is not exempt", bool(wording_problems("README.md", "Nobody knows who bought the deals. " + DENIAL_SENTENCE)), "")
    for s in ("insurers were the main buyers", "foreign demand rose", "US residents bought foreign bonds", "pensions funded the AI build-out", "money flowed into credit funds",
              "the composition of holders", "spreads fell because of insurers"):
        ck.ok("'%s' fails" % s, bool(wording_problems("README.md", s)), "passed")


def make_good_zip_response():
    return zip_fixture()


def rig(tmp, resp, clock=None, log_rows=None):
    clock = clock or FakeClock()
    calls = []
    cache, out = os.path.join(tmp, "cache"), os.path.join(tmp, "out")

    def opener(host, target, headers, timeout, cap):
        calls.append((host, target, dict(headers)))
        r = resp(target) if callable(resp) else resp
        if isinstance(r, Exception):
            raise r
        return r

    if log_rows:
        os.makedirs(out, exist_ok=True)
        write_text(os.path.join(out, "fetch_log.csv"), render_csv("fetch_log.csv", log_rows, fetch_source_line(log_rows)))
    fe = Fetcher(cache, out, stop_dir=cache, opener=opener, wall=clock.wall, sleeper=clock.sleep, now_utc=clock.now_utc)
    return fe, calls, clock


GOOD_HDR = {"last-modified": "Fri, 11 Sep 2026 16:00:19 GMT"}


def log_len(fe):
    return len(read_csv_rows(fe.log_path)[1])


def t_g15(ck):
    src = read_file(os.path.abspath(__file__), "r")
    ck.eq("the script's own source passes the STOP scan", stop_ast_problems(src), [])
    bad_sources = {
        "os.remove": "import os\ndef f(cache):\n    os.remove(os.path.join(cache, 'STOP_z1cb'))\n",
        "os.unlink via a name": "import os\ndef f(cache):\n    sp = os.path.join(cache, 'STOP_z1cb')\n    os.unlink(sp)\n",
        "os.replace": "import os\ndef f(tmp):\n    os.replace(tmp, STOP_PATH)\n",
        "os.rename": "import os\ndef f(a):\n    os.rename(a, stop_path)\n",
        "Path.unlink": "from pathlib import Path\ndef f(stop):\n    Path(stop).unlink()\n",
        "Path.write_text": "from pathlib import Path\ndef f(stop):\n    Path(stop).write_text('x')\n",
        "Path.write_bytes": "from pathlib import Path\ndef f(stop):\n    Path(stop).write_bytes(b'x')\n",
        "open w": "def f(stop):\n    open(stop, 'w').write('x')\n",
        "open a": "def f(stop):\n    open(stop, 'a').write('x')\n",
        "shutil.move": "import shutil\ndef f(stop):\n    shutil.move(stop, 'x')\n",
        "shutil.rmtree": "import shutil\ndef f(cache):\n    shutil.rmtree(cache)\n",
        "create_stop with a": "def create_stop(path, text):\n    open(path, 'a').write(text)\n",
    }
    for name, s in bad_sources.items():
        ck.ok("the scan reports: %s" % name, bool(stop_ast_problems(s)), "not reported")
    good = ("import os\ndef create_stop(path, text):\n    with open(path, 'x') as fh:\n        fh.write(text)\n"
            "def check(stop):\n    return os.path.exists(stop) and open(stop).read()\n")
    ck.eq("exclusive create and a read of the latch are allowed", stop_ast_problems(good), [])
    zbody = make_good_zip_response()
    with tempfile.TemporaryDirectory(prefix="z1cb_g15_", ignore_cleanup_errors=True) as tmp:
        fe, calls, clock = rig(os.path.join(tmp, "a"), (200, zbody, GOOD_HDR))
        create_stop(fe.stop_path(), "status: 429\nutc_time: x\nurl_path: y\nretry_after: 5\nbody_head: z\n")
        before = sha256_of(read_file(fe.stop_path()))
        say = []
        code = fe.run("20260911", say.append)
        ck.eq("with a planted STOP_z1cb, fetch makes no request and exits 2", (code, len(calls)), (2, 0))
        ck.eq("...the STOP file is unchanged", sha256_of(read_file(fe.stop_path())), before)
        ck.ok("...and prints STOP present", any(s.startswith("STOP present") for s in say), str(say))
        create_stop(fe.stop_path(), "something else\n")
        ck.eq("create_stop never overwrites an existing latch", sha256_of(read_file(fe.stop_path())), before)
        cases = [("301", (301, b"", {"location": "/releases/z1/20260911/default.htm"}), "HTTP 301"), ("403", (403, b"Forbidden", {}), "HTTP 403"),
                 ("429", (429, b"slow down", {"retry-after": "60"}), "HTTP 429"), ("500", (500, b"oops", {}), "HTTP 500"),
                 ("an empty body", (200, b"", GOOD_HDR), "empty body"), ("an HTML body", (200, b"<html><body>blocked</body></html>", GOOD_HDR), "web page"),
                 ("an HTML body after a space", (200, b"  \n<!DOCTYPE html><html>", GOOD_HDR), "web page"), ("a non-zip body", (200, b"hello there, not a zip at all", GOOD_HDR), "not a zip"),
                 ("a corrupt zip", (200, b"PK\x03\x04" + b"\x00" * 40, GOOD_HDR), "cannot be opened")]
        for i, (label, resp, msg) in enumerate(cases):
            fe, calls, clock = rig(os.path.join(tmp, "b%d" % i), resp)
            said = []
            code = fe.run("20260911", said.append)
            ck.ok("...and says why (%s)" % msg, any(msg in s for s in said), str(said))
            has = os.path.exists(fe.stop_path())
            ck.ok("a reply of %s writes STOP_z1cb, ends the fetch (exit 2) after exactly one request" % label, has and code == 2 and len(calls) == 1 and log_len(fe) == 1,
                  "exit %s, %d calls, stop %s" % (code, len(calls), has))
            if has:
                ck.ok("...with the five fields in order", stop_text_ok(read_file(fe.stop_path(), "r")), read_file(fe.stop_path(), "r")[:200])
        fe, calls, clock = rig(os.path.join(tmp, "n404"), (404, b"<html>Not found</html>", {}))
        say = []
        code = fe.run("20261210", say.append)
        ck.eq("a 404 on a release zip exits 3", code, 3)
        ck.ok("...writes no STOP", not os.path.exists(fe.stop_path()), "")
        ck.ok("...prints NOT POSTED with the path", say == ["NOT POSTED /releases/z1/20261210/z1_csv_files.zip"], str(say))
        ck.ok("...logs the request", log_len(fe) == 1 and len(calls) == 1, "")
        fe, calls, clock = rig(os.path.join(tmp, "tmo"), SocketFault("TimeoutError"))
        say = []
        code = fe.run("20260911", say.append)
        ck.ok("a timeout exits 3, writes no STOP, retries nothing and prints FAIL network", code == 3 and not os.path.exists(fe.stop_path()) and len(calls) == 1 and say and say[0].startswith("FAIL network"), str((code, say)))
        fe, calls, clock = rig(os.path.join(tmp, "ok"), (200, zbody, GOOD_HDR))
        code = fe.run("20260911", lambda s: None)
        ck.ok("a good zip writes no STOP and exits 0", code == 0 and not os.path.exists(fe.stop_path()), str(code))


def t_g16(ck):
    for u in ("https://www.sec.gov/Archives/x", "https://fred.stlouisfed.org/series/DGS10", "https://home.treasury.gov/x", "https://ticdata.treasury.gov/Publish/mfh.txt",
              "https://api.stlouisfed.org/x", "https://www.example.com/releases/z1/20260911/z1_csv_files.zip", "https://www.federalreserve.gov/releases/z1/20260911/default.htm",
              "http://www.federalreserve.gov/releases/z1/20260911/z1_csv_files.zip", "https://www.federalreserve.gov/releases/z1/20260911/z1_csv_files.zip?x=1",
              "https://www.federalreserve.gov/releases/z1/latest/z1_csv_files.zip"):
        ck.raises("refused before any request: %s" % u[:60], Refused, lambda u=u: check_url(u))
    ck.eq("the one allowed target", check_url("https://www.federalreserve.gov/releases/z1/20260911/z1_csv_files.zip"), (HOST, "/releases/z1/20260911/z1_csv_files.zip"))
    marked = UA[:-1] + chr(64) + ")"
    ck.raises("an address in the identification string is refused", Refused, lambda: assert_ua(marked))
    ck.ok("the identification string is the neutral one (pinned by its digest), with no at sign", chr(64) not in UA and sha256_of(UA.encode("utf-8")) == "8f9a46cd98203d55028d0b9fcb577ef18185c9522c627e664d9d8d529ec84cf5", "")
    zbody = make_good_zip_response()
    with tempfile.TemporaryDirectory(prefix="z1cb_g16_", ignore_cleanup_errors=True) as tmp:
        fe, calls, clock = rig(os.path.join(tmp, "a"), (200, zbody, GOOD_HDR))
        code = fe.run("20260911", lambda s: None)
        ck.eq("a good fetch makes exactly one request", (code, len(calls)), (0, 1))
        if calls:
            ck.eq("...to the Fed host and the zip path", calls[0][:2], (HOST, "/releases/z1/20260911/z1_csv_files.zip"))
            ck.eq("...with the neutral User-Agent and identity encoding", (calls[0][2].get("User-Agent"), calls[0][2].get("Accept-Encoding")), (UA, "identity"))
        ck.eq("...and one fetch_log row", log_len(fe), 1)
        fe2, calls2, _ = rig(os.path.join(tmp, "a"), (200, zbody, GOOD_HDR), clock=clock)
        ck.raises("a release already cached is not fetched again", Refused, lambda: fe2.run("20260911", lambda s: None))
        ck.eq("...and makes no request", len(calls2), 0)
        fe, calls, clock = rig(os.path.join(tmp, "r301"), (301, b"", {"location": "/releases/z1/20260911/z1_csv_files.zip"}))
        fe.run("20260911", lambda s: None)
        ck.eq("a redirect is not followed", len(calls), 1)
        fe, calls, clock = rig(os.path.join(tmp, "r500"), (500, b"x", {}))
        fe.run("20260911", lambda s: None)
        ck.eq("a 500 is never retried", len(calls), 1)
        fe, calls, clock = rig(os.path.join(tmp, "r429"), (429, b"x", {}))
        fe.run("20260911", lambda s: None)
        ck.eq("a 429 is never retried", len(calls), 1)
        t0 = 1_800_000_000.0
        last = dt.datetime.fromtimestamp(t0 - 1, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        fe, calls, clock = rig(os.path.join(tmp, "pace"), (200, zbody, GOOD_HDR), clock=FakeClock(t0), log_rows=[[last, HOST, "/x", "404", "", "", ""]])
        fe.run("20260911", lambda s: None)
        ck.ok("requests are at least 3 seconds apart (the clock waits at least 2 s)", clock.t - t0 >= 2, "waited %.1f s" % (clock.t - t0))
        today = dt.datetime.fromtimestamp(t0, dt.timezone.utc).strftime("%Y-%m-%d")
        rows = [[today + "T01:00:00Z", HOST, "/x", "404", "", "", ""], [today + "T02:00:00Z", HOST, "/x", "404", "", "", ""]]
        fe, calls, clock = rig(os.path.join(tmp, "cap"), (200, zbody, GOOD_HDR), clock=FakeClock(t0), log_rows=rows)
        ck.raises("at most two runs a calendar day", Refused, lambda: fe.run("20260911", lambda s: None))
        ck.eq("...and the third makes no request", len(calls), 0)


def t_g17(ck):
    src = read_file(os.path.abspath(__file__), "r")
    ck.eq("the script's own source passes the isolation scan", isolation_problems(src), [])
    ck.ok("a read of data/nport/nport_2026Q3.csv is reported", bool(isolation_problems("def f():\n    open('data/nport/nport_2026Q3.csv')\n")), "")
    ck.ok("a read of the series table is reported", bool(isolation_problems("def f():\n    read_file('data/series.tsv')\n")), "")
    ck.ok("an absolute path is reported", bool(isolation_problems("def f():\n    open('/etc/passwd')\n")), "")
    ck.eq("a path under the script's own folders is allowed", isolation_problems("def f(cache):\n    open(os.path.join(cache, 'F3_5_t.csv'))\n"), [])
    files = {"README.md": "TIC said 304.5 for 2024.\n", "checks.csv": "# source: x\ncheck_id\nCREF2b,TIC 304.5\n"}
    ck.ok("a TIC constant beside the word TIC in the README is reported", any("README.md" in p for p in pairing_problems(files)), "")
    ck.eq("...and in checks.csv it is not", [p for p in pairing_problems(files) if "checks.csv" in p], [])
    ck.ok("392.4 beside Treasury in SOURCES.md is reported", bool(pairing_problems({"SOURCES.md": "Treasury release: 392.4", "README.md": ""})), "")
    ck.ok("a CSV cell that is exactly 304.5 is reported", bool(pairing_problems({"windows.csv": "# source: x\na,b\n304.5,2\n"})), "")
    ck.eq("a longer number is not a hit", pairing_problems({"README.md": "TIC 1304.5 and 304.51"}), [])
    ck.eq("a Z.1 figure that prints the same digits (no TIC, Treasury or sb0662 beside it, not a bare cell) is not a hit", pairing_problems({"README.md": "| 2024 | 37.6% (304.5) |\n", "windows.csv": "# source: x\na,b\n304.500,2\n"}), [])


def t_g18(ck):
    w = get_world()
    rel, raw = w["sep"], w["sep_raw"]
    qr = [r for r in quarterly_rows(rel) if r["series_code"] == BYLINE[37].fa and r["quarter"] == "2019:Q2"][0]
    ck.eq("the quarterly fa_div4 value is the annual rate divided by 4", Dm(qr["value_usd_mn"]), Dm(raw[BYLINE[37].fa]["2019:Q2"]) / 4)
    qf = [r for r in quarterly_rows(rel) if r["series_code"] == BYLINE[37].fu and r["quarter"] == "2019:Q2"][0]
    ck.eq("a flow is the FU series, not a level", Dm(qf["value_usd_mn"]), Dm(raw[BYLINE[37].fu]["2019:Q2"]))
    ck.eq("flow() reads the flow code", flow(rel, "fu", BYLINE[37], "2019:Q2"), Dm(raw[BYLINE[37].fu]["2019:Q2"]))
    ck.eq("a money column is in millions: 5,000 $mn is written 5000.000", usd(Dm(5000)), "5000.000")
    ck.eq("a window total is a sum of flows, not of annual rates", Dm(sep_rows(rel)[("y2018", "holder", "total", "fa_div4")]["flow_usd_mn"]), Dm(psum(raw, BYLINE[13].fa, Y18)) / 4)


# ---- end-to-end ----
def build_world_cache(tmp, with_dec=True):
    w = get_world()
    cache, out = os.path.join(tmp, "cache"), os.path.join(tmp, "out")
    write_release(cache, "20260911", w["sep_files"])
    if with_dec:
        write_release(cache, "20261210", w["dec_files"])
    rows = [["2026-10-27T10:00:00Z", HOST, zip_path("20260911"), "200", "8336582", sha256_of(b"zip20260911"), "2026-09-11T16:00:19Z"]]
    if with_dec:
        rows.append(["2026-12-10T10:00:00Z", HOST, zip_path("20261210"), "200", "8300000", sha256_of(b"zip20261210"), "2026-12-10T16:00:19Z"])
    os.makedirs(out, exist_ok=True)
    write_text(os.path.join(out, "fetch_log.csv"), render_csv("fetch_log.csv", rows, fetch_source_line(rows)))
    return cache, out


def run_world_build(cache, out):
    inp = load_inputs(cache, out)
    c = compute(inp)
    texts, failed = finish(c, out, cache)
    return c, texts, failed


def t_x_build(ck):
    with tempfile.TemporaryDirectory(prefix="z1cb_x1_", ignore_cleanup_errors=True) as tmp:
        cache, out = build_world_cache(tmp)
        c, texts, failed = run_world_build(cache, out)
        write_outputs(texts, out)
        names = sorted(os.listdir(out))
        ck.eq("the fourteen committed names", names, sorted(COMMITTED))
        ck.eq("the folder guards find nothing", all_folder_problems({n: read_file(os.path.join(out, n), "r") for n in names}), [])
        st = {r[0]: r[4] for r in c["checks"]}
        ck.eq("C10 fixed output PASS", st.get("C10"), "PASS")
        ck.eq("C11 statement hash PASS", st.get("C11"), "PASS")
        ck.eq("C13 tamper PASS", st.get("C13"), "PASS")
        ck.eq("C04 PASS on the synthetic releases; C05 FAILs only on the pinned differences (the synthetic 20260911 is not the real file)", (st.get("C04"), st.get("C05")), ("PASS", "FAIL"))
        ck.eq("C09 no missing cells, C08 window lengths, C02 shape, C03 dictionary, C15 content", [st.get(k) for k in ("C09", "C08", "C02", "C03", "C15")], ["PASS"] * 5)
        ck.eq("C17 cache integrity PASS", st.get("C17"), "PASS")
        ck.eq("C01 fails: the synthetic release is not the real 11 Sep zip (a pin FAILs on 20260911)", st.get("C01"), "FAIL")
        ck.eq("CREF1 and CREF2a warn on the synthetic numbers; CREF2b is INFO", (st.get("CREF1"), st.get("CREF2a"), st.get("CREF2b")), ("WARN", "WARN", "INFO"))
        ck.ok("no check row is PASS and INFO at once for CREF2b", dict((r[0], r[4]) for r in c["checks"])["CREF2b"] == "INFO", "")
        ck.eq("the check ids are unique and ordered", [r[0] for r in c["checks"]], [x for x in CHECK_ORDER if x in st])
        h = csv_body(texts["registered.csv"])[1]
        ck.eq("registered.csv: three rows for the December release", [(r[0], r[5]) for r in h], [("SREV", "20261210"), ("SREV-F", "20261210"), ("SREV-R", "20261210")])
        w = csv_body(texts["windows.csv"])[1]
        ck.ok("windows.csv: wave rows have 10 quarters in both releases, wave_ext 11 in December", {r[4] for r in w if r[1] == "wave"} == {"10"} and {r[4] for r in w if r[1] == "wave_ext"} == {"11"}, "")
        ck.ok("no TIC constant outside checks.csv", pairing_problems(texts) == [], str(pairing_problems(texts)))
        ck.ok("README: the denial sentence appears once, exactly", texts["README.md"].count(DENIAL_SENTENCE) == 1, "")
        ck.ok("README: the disclosure sentence appears, and SOURCES.md has it too", DISCLOSURE_SENTENCE in texts["README.md"] and DISCLOSURE_SENTENCE in texts["SOURCES.md"], "")
        ck.ok("README: no verdict word, no bought/buyer/demand", not VERDICT_RX.search(texts["README.md"]) and not re.search(r"\b(bought|buyers?|demand)\b", texts["README.md"].replace(DENIAL_SENTENCE, ""), re.I), "")
        d1 = {n: sha256_of(x.encode("utf-8")) for n, x in texts.items()}
        c2, texts2, _ = run_world_build(cache, out)
        ck.eq("a second build over the same cache is byte-identical", {n: sha256_of(x.encode("utf-8")) for n, x in texts2.items()}, d1)
        build_cache1 = os.path.join(tmp, "cache1")
        write_release(build_cache1, "20260911", get_world()["sep_files"])
        os.makedirs(os.path.join(tmp, "out1"), exist_ok=True)
        write_text(os.path.join(tmp, "out1", "fetch_log.csv"), read_file(os.path.join(out, "fetch_log.csv"), "r"))
        c1, texts1, _ = run_world_build(build_cache1, os.path.join(tmp, "out1"))
        ck.eq("with one release only: registered.csv is PENDING", [r[10] for r in csv_body(texts1["registered.csv"])[1]], ["PENDING"] * 3)
        ck.eq("...and revisions.csv has no row", csv_body(texts1["revisions.csv"])[1], [])


def t_x_cache(ck):
    with tempfile.TemporaryDirectory(prefix="z1cb_x2_", ignore_cleanup_errors=True) as tmp:
        cache, out = build_world_cache(tmp, with_dec=False)
        write_bytes(os.path.join(cache, "20260911", "F3_5_t_tu.csv"), read_file(os.path.join(cache, "20260911", "F3_5_t_tu.csv")) + b" ")
        c, texts, failed = run_world_build(cache, out)
        ck.ok("an edited cached member fails C17", "C17" in failed, str(failed))
        ck.raises("a cache inside the committed output folder is refused", Refused, lambda: check_cache(os.path.join(ROOT, "data", "z1_corporate_bond_holders", "cache")))
        ck.raises("a cache elsewhere in the repository is refused", Refused, lambda: check_cache(os.path.join(ROOT, "bin", "cache")))
        ck.quiet("the default cache under data/vintages/ is accepted", lambda: check_cache(CACHE_DEFAULT))


GUARDS = [
    ("G1", "parsing (csv module, header codes with .Q, ND, Decimal sums, YYYY:QN, BOM)", ["g1_col_by_position", "g1_code_no_suffix", "g1_nd_zero", "g1_float_sum", "g1_date_noq_ok", "g1_bom_breaks"], t_g1),
    ("G2", "line mapping (leaf groups, no sub-line, detail, line 54 or derived row in a group)", ["g2_subline_in_group", "g2_ga_in_ins", "g2_issuer_detail_in_domfin", "g2_disc_in_holders", "g2_hhpf_in_nine",
                                                                                              "g2_leaf_twice", "g2_leaf_none", "g2_line8_missing"], t_g2),
    ("G3", "identities (C04 FAIL from 2017:Q1, WARN before; levels; general + separate accounts)", ["g3_tol_wide", "g3_pre2017_fail", "g3_level_with_disc", "g3_ga_sa_skipped"], t_g3),
    ("G4", "windows (quarters, wave fixed, wave_ext, fa_div4 / 4, per-quarter average)", ["g4_wave_start_q2", "g4_wave_to_latest", "g4_fa_not_div4", "g4_wave_ext_sept", "g4_avg_div4"], t_g4),
    ("G5", "shares (denominators, negative groups, positive shares, offset ratio, flag)", ["g5_den_positive", "g5_clip_negative", "g5_other_dropped", "g5_pos_for_negative", "g5_pos_total_over_leaves",
                                                                                         "g5_offset_on_groups", "g5_flag_rounded"], t_g5),
    ("G6", "headline (ratio of sums, no verdict word, seven ranked groups, fu basis)", ["g6_mean_of_shares", "g6_verdict_word", "g6_rank_other", "g6_headline_fa"], t_g6),
    ("G7", "levels (denominator, line 54, FL/LM labels)", ["g7_level_over_line1", "g7_disc_dropped", "g7_fl_lm_market"], t_g7),
    ("G8", "level change (quarter before the window; not revaluation alone)", ["g8_start_at_first", "g8_readme_revaluation"], t_g8),
    ("G9", "revisions (regenerated, no self-comparison, wave stays 10 quarters)", ["g9_append", "g9_self_compare", "g9_wave_11"], t_g9),
    ("G10", "registered statements (PENDING, unrounded compare, boundary, SREV-F, statement hash)", ["g10_score_on_base_only", "g10_round_before_compare", "g10_equal_stable", "g10_funds_no_interval",
                                                                                                      "g10_const_edit"], t_g10),
    ("G11", "zip handling (no extractall, no path from a member name, fixed names)", ["g11_scan_off", "g11_member_path"], t_g11),
    ("G12", "allowlists (headers, hash, # source:, fourteen names, check.sh copy, keys, allowed values)", ["g12_extra_col_ok", "g12_renamed_ok", "g12_allow_drift", "g12_source_as_header", "g12_thirteenth_csv_ok",
                                                                                                          "g12_checksh_reads_script", "g12_dup_key_ok", "g12_fl_book"], t_g12),
    ("G13", "leak guard (zip, json, STOP, CUSIP, local path, at sign)", ["g13_zip_ok", "g13_json_ok", "g13_cusip_off", "g13_path_ok"], t_g13),
    ("G14", "wording (causal, flow, buyer, demand, composition; the one denial sentence)", ["g14_causal_off", "g14_extra_off", "g14_denial_loose", "g14_denial_all"], t_g14),
    ("G15", "STOP latch (AST scan, statuses, bodies, 404, timeout, corrupt zip)", ["g15_scan_off", "g15_ignore_open", "g15_replace_ok", "g15_stop_ignored", "g15_overwrite", "g15_stop_short", "g15_html_ok",
                                                                               "g15_empty_ok", "g15_nonzip_ok", "g15_3xx_ignored", "g15_stop_on_timeout", "g15_404_latches"], t_g15),
    ("G16", "fetch safety (hosts, default.htm, user-agent, redirect, retry, second request, pacing, daily cap)", ["g16_allow_other_host", "g16_default_htm_ok", "g16_at_in_ua_ok", "g16_redirect_follow",
                                                                                                                 "g16_retry", "g16_second_request", "g16_pacing_off", "g16_daily_cap_off"], t_g16),
    ("G17", "isolation (AST scan, TIC constants only in checks.csv)", ["g17_scan_off", "g17_tic_everywhere_ok"], t_g17),
    ("G18", "units (FA divided by 4, a flow is not a level, millions not billions)", ["g18_fa_undivided", "g18_level_as_flow", "g18_bn_in_mn"], t_g18),
    ("X1", "end-to-end build on the synthetic releases (checks, outputs, guards, fixed output)", ["x_render_unstable"], t_x_build),
    ("X2", "cache integrity and cache location", [], t_x_cache),
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
    get_world_c()
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
                print("       mutant %-28s %s%s" % (m, "caught" if caught else "SURVIVED", "  (first failing check: %s)" % mk.failed()[0][0][:70] if caught else ""))
    print("selftest: %d guards, %d checks, %d mutants applied one at a time, %d failure(s), %.1f s" % (len(GUARDS), n_checks, n_mut, bad_total, time.time() - t0))
    return 0 if bad_total == 0 else 1


# ==== COMMAND LINE ====
def run_fetch(a):
    os.makedirs(a.out, exist_ok=True)
    fe = Fetcher(a.cache, a.out)
    code = fe.run(a.release)
    print("requests sent in this invocation: %d" % fe.requests)
    return code


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch", help="download one release's z1_csv_files.zip (the only network command; exactly 1 request)")
    pf.add_argument("--release", required=True, help="YYYYMMDD, the dated folder in the zip URL")
    pf.add_argument("--cache", default=CACHE_DEFAULT)
    pf.add_argument("--out", default=OUT_DEFAULT, help="where fetch_log.csv is kept")
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
