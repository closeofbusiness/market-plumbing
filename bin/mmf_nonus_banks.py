#!/usr/bin/env python3
"""US money market funds' holdings of claims on non-US financial institutions, by parent country and instrument, month-ends from 2011 (OFR Money Market
Fund Monitor), with the quarter-end pattern. Python 3 standard library only.

  python3 bin/mmf_nonus_banks.py fetch [--cache DIR] [--out DIR] [--sleep 2.05] [--max-requests N] [--max-seconds S]   # the only network command
  python3 bin/mmf_nonus_banks.py kinds [--cache DIR] [--out DIR]       # offline: parents.csv for the supervisor's review (no quarter-end figure)
  python3 bin/mmf_nonus_banks.py build [--cache DIR] [--out DIR]       # offline; byte-identical on re-run; exits 2 unless the kind table is the reviewed one
  python3 bin/mmf_nonus_banks.py selftest [--no-mutants] [--mutant NAME] [--write-fixture DIR]    # synthetic data only; no network

Specification: _research/2026-10-25-MMF-NonUS-Banks-Spec.md (committed at da6f335, with its supervisor rulings, rounds 1 to 4; where rounds differ the
latest round is applied). Outputs: data/mmf_nonus_banks/ (ten CSVs, README.md, SOURCES.md).

WHAT TOUCHES THE NETWORK. Only `fetch`, and only www.financialresearch.gov (the OFR money-fund monitor's chart files) and data.financialresearch.gov (four
API series). Any other host is refused before a request is made. GET only, one request at a time, at least 2 seconds apart, no redirect followed, the
CLAUDE.md non-SEC identification string (no address, no name), no retry of any kind, at most 3,000 requests per vintage across resumed runs. The monitor's
complete-dataset zip is never requested. Any status other than 200, or a body that fails its content test, writes STOP_ofr (monitor) or STOP_api (API) in
data/vintages/mmf_nonus_banks/ and ends the run; going over the budget writes STOP_budget. This script never deletes, renames over or truncates a STOP
file; only a person deletes one. A socket timeout is not a refusal: it is logged, and the next run fetches only what is not yet saved.

WHAT IT MEASURES. The month-end holdings of US money market funds in claims on financial institutions whose ultimate parent is headquartered outside the
United States (the OFR's own mapping of issuers and repo counterparties to parents and countries), by parent country and instrument, and how the
quarter-end month-ends compare with their neighbours. It records holdings; it does not show why they changed, and a change in holdings is not a measure of
money moved.
"""
import argparse
import ast
import calendar
import collections
import contextlib
import csv
import datetime as dt
import hashlib
import http.client
import io
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from decimal import Decimal, ROUND_HALF_UP, getcontext
from urllib.parse import quote, quote_plus

getcontext().prec = 50

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(ROOT, "data", "mmf_nonus_banks")
CACHE_DEFAULT = os.path.join(ROOT, "data", "vintages", "mmf_nonus_banks")
SPEC_FILE = os.path.join(ROOT, "_research", "2026-10-25-MMF-NonUS-Banks-Spec.md")

# R2: the CLAUDE.md canonical string for every non-SEC host. No address, no name.
UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
HEADERS = {"User-Agent": UA, "Accept-Encoding": "identity", "Accept": "*/*"}
HOST_WWW = "www.financialresearch.gov"
HOST_API = "data.financialresearch.gov"
HOST_ALLOW = frozenset({HOST_WWW, HOST_API})
MIN_SLEEP = 2.0                 # R3: at least 2 s between request starts
DEFAULT_SLEEP = 2.05            # the 0.05 is a margin for clock granularity
BUDGET = 3000                   # R3: requests per vintage, counted across resumed runs
TIMEOUT = 90
BODY_CAP = 64 * 1024 * 1024
ERR_CAP = 4096
STOP_OFR, STOP_API, STOP_BUDGET = "STOP_ofr", "STOP_api", "STOP_budget"
MON_BASE = "/money-market-funds/data/"
ROOT_DIR = "credit_risks_country"
ZIP_NAME = "mmf_data.zip"
API_MNEMONICS = ("MMF-MMF_TOT-M", "MMF-MMF_RP_wFFI-M", "MMF-MMF_RP_wFICC-M", "MMF-MMF_RP_wDFI-M")
IDENT_TOL = Decimal("1.00")     # 3.4: USD
SMALL_ISSUERS = "Aggregated small issuers"
FI_SECTOR = "Financial Institution"
SUPRA_REGION = "Supranational"
USA = "USA"
CITATION = ('Office of Financial Research, "OFR Money Market Fund Monitor", refreshed monthly, '
            'https://www.financialresearch.gov/money-market-funds/.')

# KIND_TABLE_SHA256: set by the supervisor after reviewing parents.csv (spec 3.7); `build` exits 2 unless the kind table below hashes to it.
KIND_TABLE_SHA256 = "372706934150e78332604721c1efde76cdd0b07b09015d4ed8159eec6e6c491b"   # reviewed 25 Oct 2026 (supervisor, after stage 1)
# S1's frozen noise N (spec 4.5): the clean-month sd of ALL_NONUS `secured`, post_reform, as computed by the first build; None until the first build.
S1_N_FROZEN = 6.215782929260888   # frozen from the first build of vintage 2026-10-15 (25 Oct 2026); 6.2158 to four places

# ------------------------------------------------------------------------------------------------------------------------
# mutants: deliberately broken variants, switched on only by the selftest, in this process
# ------------------------------------------------------------------------------------------------------------------------
_ACTIVE = set()
_CLOCK_OVERRIDE = []


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
    """A technical refusal: a STOP file was written (or already exists); the run ends."""


class SocketFault(Exception):
    """Timeout, reset or TLS error: the invocation ends without latching."""


class SliceEnd(Exception):
    """The per-invocation request or time cap was reached: an orderly end, resume later."""


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


def sha256_path(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def D_(s):
    return dt.date.fromisoformat(s)


def is_month_end(d):
    return (d + dt.timedelta(days=1)).day == 1


def month_end(y, m):
    return dt.date(y, m, calendar.monthrange(y, m)[1])


def next_month_end(d):
    return month_end(d.year + (d.month == 12), d.month % 12 + 1)


def prev_month_end(d):
    return d.replace(day=1) - dt.timedelta(days=1)


def months_between(a, b):
    """Calendar month-ends a..b inclusive (both month-ends)."""
    out, d = [], a
    while d <= b:
        out.append(d)
        d = next_month_end(d)
    return out


def quarter_label(d):
    return "%dQ%d" % (d.year, (d.month - 1) // 3 + 1)


def now_utc():
    if _CLOCK_OVERRIDE:
        return _CLOCK_OVERRIDE[-1]
    return dt.datetime.now(dt.timezone.utc)


MONTHS_LONG = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
DATE_TEXT_RX = re.compile(r"^(" + "|".join(MONTHS_LONG) + r") (\d{1,2}), (\d{4})$")
DATE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_date_text(s):
    """'September 30, 2026' -> date. ValueError if it is not that shape."""
    m = DATE_TEXT_RX.match(s or "")
    if not m:
        raise ValueError("not a date like 'September 30, 2026': %r" % (s,))
    return dt.date(int(m.group(3)), MONTHS_LONG.index(m.group(1)) + 1, int(m.group(2)))


def tz_epoch_ms_to_date(ms):
    """Epoch milliseconds -> the UTC calendar date (G9). The mutant converts in US Eastern time, which turns midnight UTC into the day before."""
    t = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc) + dt.timedelta(milliseconds=int(ms))
    if M("g9_local_tz"):
        t = t - dt.timedelta(hours=5)
    return t.date()


def parse_mdy(s):
    """'MM-DD-YYYY' -> date (G9). The mutant reads it day-first."""
    a, b, y = s.split("-")
    if M("g9_day_first"):
        return dt.date(int(y), int(b), int(a))
    return dt.date(int(y), int(a), int(b))


# ---- numbers (R8) ------------------------------------------------------------------------------------------------------
def to_dec(v):
    if isinstance(v, Decimal):
        return v
    if isinstance(v, bool):
        raise ValueError("boolean where a number was expected")
    if isinstance(v, int):
        return Decimal(v)
    if isinstance(v, float):
        return Decimal(repr(v))
    raise ValueError("not a number: %r" % (v,))


def dsum(values):
    """Sum in Decimal (R8). The mutant sums floats."""
    if M("g8_float_sum"):
        t = 0.0
        for x in values:
            t += float(x)
        return Decimal(repr(t))
    t = Decimal(0)
    for x in values:
        t += x
    return t


def usd_to_mn(usd):
    """USD -> USD millions, unrounded (R8: rounding happens only at write time)."""
    if usd is None:
        return None
    if M("g8_thousands"):
        return Decimal(usd) / Decimal(1000)
    if M("g8_bn_in_mn"):
        return Decimal(usd) / Decimal(1_000_000_000)
    return Decimal(usd) / Decimal(1_000_000)


_QUANT = {n: Decimal(1).scaleb(-n) for n in range(0, 7)}


def qfix(v, nd):
    d = v if isinstance(v, Decimal) else (Decimal(repr(v)) if isinstance(v, float) else Decimal(v))
    return d.quantize(_QUANT[nd], rounding=ROUND_HALF_UP)


def dstr(v, nd):
    """Fixed-decimal text of a Decimal or float, '' for None, no negative zero, '' for nan or inf (a non-number is never written)."""
    if v is None:
        return ""
    if M("g8_wrong_decimals"):
        nd = 2
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        if M("g10_inf_not_blank"):
            return "inf" if v > 0 else "-inf"
        return ""
    q = qfix(v, nd)
    s = format(q, "f")
    return s[1:] if q == 0 and s.startswith("-") else s


def ln_pct(a, b):
    """100 x ln(a/b) from two unrounded Decimal levels (floats at this point only, R8). None if either level is not positive."""
    if a is None or b is None:
        return None
    if a <= 0 or b <= 0:
        if M("g10_inf_not_blank"):
            return float("inf") if a > 0 else float("-inf")
        return None
    fa, fb = float(a), float(b)
    if M("g8_log_on_rounded"):
        fa, fb = float(qfix(usd_to_mn(a), 1)), float(qfix(usd_to_mn(b), 1))
    return 100.0 * (math.log(fa) - math.log(fb))


# ---- the monitor's path rule (2.1, G1) ----------------------------------------------------------------------------------
SEG_SAFE = "-_.!~*'()"


def seg(name):
    """One path segment: the display name lower-cased, every whitespace character (U+00A0 included) replaced by '_', then percent-encoded as JavaScript's
    encodeURIComponent does."""
    s = name.lower()
    safe = SEG_SAFE
    if M("g1_plus_raw"):
        safe += "+"
    if M("g1_amp_raw"):
        safe += "&"
    if M("g1_comma_raw"):
        safe += ","
    if M("g1_paren_enc"):
        safe = safe.replace("(", "").replace(")", "")
    if M("g1_quote_plus"):
        return quote_plus(s, safe=safe)
    if M("g1_first_space"):
        s = s.replace(" ", "_", 1)
    elif M("g1_nbsp"):
        s = s.replace(" ", "_")
    else:
        s = re.sub(r"\s", "_", s)
    return quote(s, safe=safe)


def check_siblings(names, where=""):
    """Two siblings that map to the same segment are a FAIL (G1)."""
    seen = {}
    for n in names:
        k = seg(n)
        if k in seen and seen[k] != n and not M("g1_dup_ok"):
            raise DataError("siblings %r and %r map to one path segment %r%s" % (seen[k], n, k, (" under " + where) if where else ""))
        seen[k] = n


def node_url_path(tpath):
    """The URL path of the data.json holding the children of the node at `tpath` (a tuple of display names from the root)."""
    return MON_BASE + ROOT_DIR + "/" + "".join(seg(n) + "/" for n in tpath) + "data.json"


def api_url_path(mnemonic):
    return "/v1/series/full?mnemonic=" + mnemonic


UPDATED_PATH = MON_BASE + "updated.json"
ASOF_PATH = MON_BASE + "asof.json"


# ------------------------------------------------------------------------------------------------------------------------
# the output allowlists: the spec's canonical text (section 5), typed here, and its sha256 as the spec prints it
# ------------------------------------------------------------------------------------------------------------------------
SPEC_ALLOW_TEXT = (
    "levels_country.csv:month_end,country,country_group,instrument_group,usd_mn,pct_of_mmf_total,pct_of_nonus_fi,vintage\n"
    "levels_group.csv:month_end,country_group,fund_lineage,measure,usd_mn,pct_of_mmf_total,pct_of_lineage_total,vintage\n"
    "quarter_ends.csv:quarter,qe_month,basis,stat_kind,country_group,measure,level_prev_usd_mn,level_qe_usd_mn,level_next_usd_mn,chg_in_pct,chg_out_pct,"
    "below_nbrs_pct,below_nbrs_usd_mn,window,frozen_set,primary,blind,vintage\n"
    "qe_summary.csv:basis,stat_kind,window,country_group,measure,n_quarters,n_blank,mean_below_nbrs_pct,median_below_nbrs_pct,n_negative,sd_below_nbrs_pct,"
    "se_mean_below_nbrs_pct,noise_clean_sd_pct,noise_n,pattern,paired_n_vs_aunz,paired_mean_diff_vs_aunz_pct,paired_se_vs_aunz_pct,primary,blind,vintage\n"
    "parents.csv:parent,country,country_group,kind,first_month,last_month,usd_mn_latest,vintage\n"
    "summary.csv:question,window,country_group,measure,from_month,to_month,statistic,value,unit,primary,blind\n"
    "revisions.csv:vintage_prev,vintage_new,month_end,country,instrument_group,usd_mn_prev,usd_mn_new,change_usd_mn\n"
    "vintages.csv:vintage,ofr_updated,ofr_asof,requests,nodes,manifest_sha256,api_total_check,kind_table_sha256\n"
    "checks.csv:check_id,description,expected,observed,status\n"
    "fetch_log.csv:utc_time,host,path,status,bytes,sha256\n")
SPEC_ALLOW_SHA256 = "07dc8c29cbd4971ada14f2f638cc600f857756dee7f97518cac5b3f189fccf4f"
SUPERSEDED_ALLOW_SHA256 = ("15e3acd47f3a7859937b515753e0561bd8c0618ebf84cd75fe9c7f7814f9f77e",)


def allow_text():
    t = SPEC_ALLOW_TEXT
    if M("g13_extra_col"):
        t = t.replace("checks.csv:check_id,", "checks.csv:check_id,extra,")
    if M("g13_renamed"):
        t = t.replace("below_nbrs_pct,", "dip_pct,", 1)
    return t


def allowlist():
    out = collections.OrderedDict()
    for line in allow_text().splitlines():
        name, cols = line.split(":", 1)
        out[name] = cols.split(",")
    if M("g13_eleventh_csv"):
        out["extra.csv"] = ["a", "b"]
    return out


def allow_sha():
    return sha256_of(allow_text().encode("utf-8"))


def allow_problems(text=None):
    """SPEC_ALLOW_SHA256 must equal the sha256 of the canonical text (G13). The mutant lets a different hash through."""
    if M("g13_spec_hash_bad"):
        return []
    got = allow_sha() if text is None else sha256_of(text.encode("utf-8"))
    return [] if got == SPEC_ALLOW_SHA256 else ["the allowlist text hashes to %s, not the spec's %s" % (got, SPEC_ALLOW_SHA256)]


COMMITTED_NAMES = tuple(l.split(":")[0] for l in SPEC_ALLOW_TEXT.splitlines())
DOC_NAMES = ("README.md", "SOURCES.md")
UNIQUE_KEYS = {
    "levels_country.csv": ("month_end", "country", "instrument_group"),
    "levels_group.csv": ("month_end", "country_group", "fund_lineage", "measure"),
    "quarter_ends.csv": ("quarter", "basis", "country_group", "measure"),
    "qe_summary.csv": ("basis", "window", "country_group", "measure"),
    "parents.csv": ("parent", "country"),
    "summary.csv": ("question", "window", "country_group", "measure", "from_month", "to_month", "statistic"),
    "revisions.csv": ("vintage_prev", "vintage_new", "month_end", "country", "instrument_group"),
    "vintages.csv": ("vintage",),
    "checks.csv": ("check_id",),
}

# ------------------------------------------------------------------------------------------------------------------------
# the literal maps (3.3, 3.5, 3.6). Selection is by name, never by position or substring.
# ------------------------------------------------------------------------------------------------------------------------
# fund categories and their lineages (2.1)
CATEGORIES = (("Prime", "prime"), ("Prime Institutional", "prime"), ("Prime Retail", "prime"),
              ("Government", "government"), ("Government (No Fees & Gates)", "government"), ("Government (Fees & Gates)", "government"),
              ("Tax Exempt", "tax_exempt"), ("Tax Exempt Institutional", "tax_exempt"), ("Tax Exempt Retail", "tax_exempt"))
LINEAGES = ("prime", "government", "tax_exempt")
LINEAGE_ALL = ("all",) + LINEAGES
CAT_EXPECT_COUNTS = (63, 126, 126, 91, 98, 98, 63, 126, 126)          # C07, in CATEGORIES order (2.1, observed at vintage 2026-10-15)
LEGACY_NAME = {"prime": "Prime", "government": "Government", "tax_exempt": "Tax Exempt"}


def all_regions():
    return REGIONS + tuple(BUILDER_REGIONS)


def all_sectors():
    return SECTORS + tuple(BUILDER_SECTORS)


def cat_lineage():
    m = dict(CATEGORIES)
    if M("g3_omit_fg"):
        m.pop("Government (Fees & Gates)")
    return m


REGIONS = ("Asia", "Australia", "Europe", "North America", "South America", "Supranational")
SECTORS = ("Financial Institution", "Government", "Non-Financial Corporate")
EA = ("Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Estonia", "Finland", "France", "Germany", "Greece", "Ireland", "Italy", "Latvia", "Lithuania",
      "Luxembourg", "Malta", "Netherlands", "Portugal", "Slovakia", "Slovenia", "Spain")
NORDIC = ("Sweden", "Norway", "Denmark")
# country labels seen in OFR JSON (2.1) plus the euro-area list; further labels are added by the builder in the open (round 4, O-10) and logged in
# SOURCES.md "Builder decisions"
COUNTRY_EXTRA = ("UK", "Switzerland", "Japan", "Canada", USA, "China", "India", "Israel", "Singapore", "South Korea", "Australia", "New Zealand")
KNOWN_COUNTRIES = tuple(EA) + NORDIC + COUNTRY_EXTRA
GROUP_ORDER = ("EA", "FR", "JP", "CA", "UK", "CH", "NORDIC", "AUNZ", "OTHER_ASIA", "OTHER", "ALL_NONUS", "MEMO_FICC")
NINE = ("EA", "JP", "CA", "UK", "CH", "NORDIC", "AUNZ", "OTHER_ASIA", "OTHER")
EXCL_US, EXCL_SUPRA = "EXCLUDED_US", "EXCLUDED_SUPRANATIONAL"
# country labels the builder added after seeing the first vintage (O-10, round 4): label -> why. Each is logged in SOURCES.md "Builder decisions".
_SEEN = "seen in the 2026-10-15 vintage"
BUILDER_COUNTRIES = {
    "Chile": _SEEN + " under South America; OTHER", "Venezuela": _SEEN + " under South America; OTHER", "Mexico": _SEEN + " under North America; OTHER",
    "Tunisia": _SEEN + " under the new region Africa; OTHER", "Ukraine": _SEEN + " under Europe; OTHER (not euro area, not NORDIC)",
    "Jordan": _SEEN + " under Asia; OTHER_ASIA", "Kuwait": _SEEN + " under Asia; OTHER_ASIA", "Malaysia": _SEEN + " under Asia; OTHER_ASIA",
    "Philippines": _SEEN + " under Asia; OTHER_ASIA", "Qatar": _SEEN + " under Asia; OTHER_ASIA", "Saudi Arabia": _SEEN + " under Asia; OTHER_ASIA",
    "Taiwan": _SEEN + " under Asia; OTHER_ASIA", "Turkey": _SEEN + " under Asia (the OFR's region, not a geographic choice of ours); OTHER_ASIA",
    "United Arab Emirates": _SEEN + " under Asia; OTHER_ASIA"}
# region and sector labels added after seeing the first vintage (O-10): label -> why
BUILDER_REGIONS = {"Africa": _SEEN + ": holds Tunisia only; its countries fall under OTHER"}
BUILDER_SECTORS = {"Municipal": _SEEN + " under the USA only; the USA is outside every non-US total and only its Financial Institution file is read",
                   "Other": _SEEN + " under the USA only; the USA is outside every non-US total and only its Financial Institution file is read"}


def classify_country(region, label):
    """The groups a country belongs to, by OFR label and region. Returns a tuple of groups ('FR' beside 'EA' for France), or (EXCL_US,) / (EXCL_SUPRA,),
    or None for a label that is not in the literal table (an unknown label, C13)."""
    if region == SUPRA_REGION and not M("g5_supra_in"):
        return (EXCL_SUPRA,)
    known = KNOWN_COUNTRIES + tuple(BUILDER_COUNTRIES)
    if M("g5_unknown_ok"):
        known = None
    if known is not None:
        if M("g5_substring"):
            if not any(k in label or label in k for k in known):
                return None
        elif label not in known:
            return None
    if label == USA:
        return ("OTHER",) if M("g5_us_nonus") else (EXCL_US,)
    if label == "UK" and M("g5_uk_in_ea"):
        return ("EA",)
    if label in EA:
        return ("EA", "FR") if label == "France" else ("EA",)
    if label == "Japan":
        return ("JP",)
    if label == "Canada":
        return ("CA",)
    if label == "UK":
        return ("UK",)
    if label == "Switzerland":
        return ("CH",)
    if label in NORDIC:
        return ("NORDIC",)
    if region == "Australia":
        return ("AUNZ",)
    if region == "Asia":
        return ("OTHER_ASIA",)
    return ("OTHER",)


# instrument groups (3.6)
IG_ORDER = ("repo_treasury", "repo_agency", "repo_other", "cd", "time_deposit", "fin_cp", "other_note", "abcp", "misc", "unallocated")
ITYPE_MAP = {
    "Treasury Repurchase Agreement": "repo_treasury", "Government Agency Repurchase Agreement": "repo_agency", "Other Repurchase Agreement": "repo_other",
    "Certificate of Deposit": "cd", "Financial Company Commercial Paper": "fin_cp", "Asset Backed Commercial Paper": "abcp",
    "Other Note": "other_note", "Other Instrument": "other_note",
    "Non-Financial Company Commercial Paper": "misc", "U.S. Treasury Debt": "misc", "Government Agency Debt": "misc"}
# relayed labels (N-MFP investment categories, not seen in OFR JSON when the spec was written): mapped as listed, C13 WARNs when one is seen
RELAYED_ITYPE_MAP = {
    "Non-Negotiable Time Deposit": "time_deposit", "Variable Rate Demand Note": "misc", "Other Municipal Security": "misc", "Tender Option Bond": "misc",
    "Insurance Company Funding Agreement": "misc", "Investment Company": "misc", "Other Asset Backed Securities": "misc",
    "Non-U.S. Sovereign, Sub-Sovereign and Supra-National Debt": "misc",
    # the OFR's own spelling of the last relayed label (lower-case 'debt', seen 40 times in the 2026-10-15 vintage); mapped to misc as the spec lists it, flagged by C13b
    "Non-U.S. Sovereign, Sub-Sovereign and Supra-National debt": "misc"}
# labels the builder added after seeing the first vintage (each is logged in SOURCES.md "Builder decisions"): label -> (group, why)
BUILDER_ITYPE_MAP = {}


def itype_map():
    m = dict(ITYPE_MAP)
    m.update(RELAYED_ITYPE_MAP)
    m.update({k: v[0] for k, v in BUILDER_ITYPE_MAP.items()})
    if M("g7_unknown_ok"):
        class AllMisc(dict):
            def get(self, k, default=None):
                return super().get(k, "misc")
        return AllMisc(m)
    return m


def measure_groups():
    """The instrument groups behind each measure (3.6)."""
    sec = ["repo_treasury", "repo_agency", "repo_other"]
    uns = ["cd", "time_deposit", "fin_cp", "other_note"]
    if M("g7_abcp_unsecured"):
        uns.append("abcp")
    if M("g7_misc_unsecured"):
        uns.append("misc")
    if M("g7_repo_unsecured"):
        uns.append("repo_other")
        sec.remove("repo_other")
    if M("g7_identity_broken"):
        sec.remove("repo_agency")
    return {"secured": tuple(sec), "unsecured": tuple(uns), "abcp": ("abcp",), "misc": ("misc",)}


MEASURES = ("headline", "bank_only", "secured", "unsecured", "abcp", "misc")
QE_MEASURES = ("headline", "bank_only", "secured", "unsecured")
KINDS = ("bank", "insurer", "other_fin")

# ------------------------------------------------------------------------------------------------------------------------
# the kind table (3.7, F10): (parent, country) -> kind. A bank is a deposit-taking institution or a bank holding company; broker-dealer parents are
# other_fin; insurers are insurer. Set by the builder in mode `kinds`, listed in SOURCES.md "Builder decisions", reviewed by the supervisor, who sets
# KIND_TABLE_SHA256. Filled in after the first `kinds` run.
# ------------------------------------------------------------------------------------------------------------------------
def _kt(kind, *pairs):
    return {tuple(p.rsplit("|", 1)): kind for p in pairs}


KIND_TABLE = {}
KIND_TABLE.update(_kt("bank",
    "ABN AMRO|Netherlands", "Abu Dhabi International Bank I|United Arab Emirates", "Agricultural Bank of China|China", "Alternative Bank Switzerland AG|Switzerland",
    "Australia & New Zealand Banking Group|Australia", "Axis|India", "BNP Paribas|France", "Banco Bilbao Vizcaya Argentaria|Spain", "Banco Santander|Spain",
    "Banco de Credito e Inversiones|Chile", "Banco del Estado de Chile|Chile", "Banesco|Venezuela", "Bank Baroda|India", "Bank Hapoalim|Israel", "Bank Leumi|Israel",
    "Bank of Australia|Australia", "Bank of China|China", "Bank of India|India", "Bank of Ireland|Ireland",
    "Bank of Montreal|Canada", "Bank of New Zealand|New Zealand", "Bank of Nova Scotia|Canada", "Bank of Tokyo-Mitsubishi|Japan", "Banque et Caisse|Luxembourg",
    "Barclays|UK", "Bayerische Hypo Vereinsbank|Germany", "Bayerische Landesbank|Germany", "Caisse Centrale Des Jardins|Canada", "Canadian Imperial Bancorp|Canada",
    "Chiba Bank|Japan", "China Construction Bank|China", "Commerzbank|Germany", "Commonwealth Bank of Australia|Australia", "Credit Agricole|France",
    "Credit Industriel|France", "Credit Mutuel|France", "Credit Suisse|Switzerland", "DBS Bank|Singapore", "DNB|Norway", "DZ Bank AG|Germany", "Danske Bank|Denmark",
    "Depfa Bank|Germany", "Deutsche Bank|Germany", "Dexia|Belgium", "Erste Bank|Austria", "Groupe BPCE|France", "HSBC|UK", "Hana Financial Group|South Korea",
    "Helaba|Germany", "ING Groep Nv|Netherlands", "Icici Bank Limited|India", "Industrial & Commercial Bank of China Ltd.|China", "Intesa|Italy",
    "Israel Discount Bank of New York|Israel", "KBC Groep Nv|Belgium", "Kookmin Bank|South Korea", "LA BANQUE POSTALE|France", "Landesbank Baden-wuerttemberg|Germany",
    "Lloyds|UK", "Macquarie|Australia", "Maybank|Malaysia", "Mizuho|Japan", "NatWest Group|UK", "Natexis + Natixis|France",
    "National Australia Bank|Australia", "National Bank of Abu Dhabi|United Arab Emirates", "National Bank of Canada|Canada", "National Bank of Kuwait|Kuwait",
    "Nationwide Building Society|UK", "Norddeutsche Landesbank|Germany", "Nordea|Sweden", "Norinchukin Bank|Japan",
    "OP Financial Group|Finland", "Oversea Chinese Banking|Singapore", "Rabobank|Netherlands", "Royal Bank of Canada|Canada",
    "Royal Bank of Scotland|UK", "SBAB Bank AB|Sweden", "Shinhan Bank|South Korea", "Shizuoka Bank|Japan", "Skandinaviska Enskilda Banken|Sweden",
    "Societe Generale|France", "Standard Chartered Bank|UK", "State Bank Financial|India", "State Bank of India|India", "Sumitomo Mitsui Bank|Japan",
    "Sumitomo Trust|Japan", "Svenska Handelsbanken|Sweden", "Swedbank|Sweden", "The Commercial Bank of Qatar|Qatar", "Toronto Dominion|Canada", "UBS|Switzerland",
    "Unicredit|Italy", "United Overseas Bank|Singapore", "Westpac|Australia", "Zurich Cantonal Bank|Switzerland"))
KIND_TABLE.update(_kt("insurer", "Allianz|Germany", "Axa SA|France", "Prudential Plc|UK"))
KIND_TABLE.update(_kt("other_fin",
    "ABB Ltd.|Switzerland", "Albion Capital|Australia", "Bank Nederlandse Gemeenten|Netherlands", "Nederlandse Waterschapbank|Netherlands", "NRW.Bank|Germany",
    "Oesterreicheische Kontrollbank Ag|Austria", "Asian Development Bank|Philippines", "Brookfield Holdings Canada Inc.|Canada",
    "Canadian Pacer Auto Recievables Trust|Canada", "Cic Eurosecurities, Inc.|France", "Daiwa Securities Group Inc|Japan", "Eaton Capital UnLtd Co|Ireland",
    "Eksportfinans|Norway", "Experian Finance PLC|UK", "Firstmac Mortgage|Australia", "Glencore|Switzerland", "Global Lending Services LLC|Japan", "ITOCHU Corporation|Japan",
    "Japan Finance Corp|Japan", "KFW|Germany", "Kommunalbanken|Norway", "London Stock Exchange Group|UK", "London Stock Exchange Group plc|UK", "Louis Dreyfus|Netherlands",
    "Mirae Asset Financial Group|South Korea", "Nomura Securities|Japan", "Northcross Capital|UK", "Novo Holdings A/S|Denmark", "OMERS Finance Trust|Canada",
    "Pepper Group|UK", "RWE AG|Germany", "Reckitt Benckiser|UK", "Resimac|Australia", "Roche Holdings|Switzerland", "Suncorp|Australia", "Swedish Export Finance|Sweden",
    "TP ICAP|UK", "Wintek Ltd|China", "Zephyr Financiere Inc.|Canada"))
# Judgement calls, shown beside the kind table in SOURCES.md for the supervisor's review
KIND_NOTES = {
    ("Bank Nederlandse Gemeenten", "Netherlands"): "public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence)",
    ("Nederlandse Waterschapbank", "Netherlands"): "public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence)",
    ("NRW.Bank", "Germany"): "public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence)",
    ("Oesterreicheische Kontrollbank Ag", "Austria"): "public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence)",
    ("KFW", "Germany"): "public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence)",
    ("Kommunalbanken", "Norway"): "public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence)",
    ("Eksportfinans", "Norway"): "public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence)",
    ("Swedish Export Finance", "Sweden"): "public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence)",
    ("Japan Finance Corp", "Japan"): "public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence)",
    ("Asian Development Bank", "Philippines"): "multilateral lender, not a bank under any national law; counted other_fin",
    ("Macquarie", "Australia"): "the group includes the deposit-taking Macquarie Bank; kept as a bank by supervisor ruling",
    ("Natexis + Natixis", "France"): "the BPCE group's corporate and investment bank, a licensed French credit institution; kept as a bank by supervisor ruling",
    ("Sumitomo Trust", "Japan"): "trust bank (deposit-taking); kept as a bank by supervisor ruling",
    ("Cic Eurosecurities, Inc.", "France"): "US broker-dealer subsidiary that the OFR maps as its own parent; counted other_fin",
    ("Abu Dhabi International Bank I", "United Arab Emirates"): "name read as a bank; no further information in the OFR file",
    ("Bank of Australia", "Australia"): "name read as a bank; no further information in the OFR file",
    ("State Bank Financial", "India"): "name read as a bank; no further information in the OFR file",
    ("Albion Capital", "Australia"): "name and instrument mix (asset-backed commercial paper) read as a funding vehicle; counted other_fin",
    ("Northcross Capital", "UK"): "same: funding vehicle; counted other_fin",
    ("Zephyr Financiere Inc.", "Canada"): "same: funding vehicle; counted other_fin",
    ("Global Lending Services LLC", "Japan"): "non-bank lender; counted other_fin",
    ("Suncorp", "Australia"): "financial conglomerate (insurance and, until a sale, a bank); neither bank nor insurer fits every date, so other_fin (relayed knowledge, not checked at source)",
    ("Wintek Ltd", "China"): "non-financial company; counted other_fin",
}



def kind_table_text(table=None):
    t = KIND_TABLE if table is None else table
    rows = sorted(((p, c, k) for (p, c), k in t.items()), key=lambda r: (r[0], r[1], r[2]))
    return "".join("%s|%s|%s\n" % r for r in rows)


def kind_table_sha(table=None):
    return sha256_of(kind_table_text(table).encode("utf-8"))


def kind_gate_problems(parent_keys, table=None, expected=None):
    """build exits 2 before writing any output if the current table's sha256 differs from KIND_TABLE_SHA256 or any parent lacks a kind (G19)."""
    t = KIND_TABLE if table is None else table
    exp = KIND_TABLE_SHA256 if expected is None else expected
    out = []
    missing = [k for k in sorted(parent_keys) if k not in t]
    if missing and not M("g19_missing_kind_ok"):
        out.append("%d parent(s) have no kind: %s" % (len(missing), "; ".join("%s (%s)" % k for k in missing[:8])))
    bad = [k for k, v in t.items() if v not in KINDS]
    if bad:
        out.append("kind not in %s for %s" % (KINDS, bad[:3]))
    if not M("g19_hash_ignored"):
        if not exp:
            out.append("KIND_TABLE_SHA256 is not set (the supervisor sets it after reviewing parents.csv)")
        elif kind_table_sha(t) != exp:
            out.append("the kind table hashes to %s, not KIND_TABLE_SHA256 %s" % (kind_table_sha(t), exp))
    return out


def bank_kinds(table=None):
    """The kinds counted in bank_only. The mutants count an insurer or a broker-dealer too."""
    if M("g19_insurer_bank"):
        return ("bank", "insurer")
    if M("g19_broker_bank"):
        return ("bank", "other_fin")
    return ("bank",)


# ------------------------------------------------------------------------------------------------------------------------
# nodes: the monitor's data.json files (2.1), their content tests (R3b) and identities (3.4)
# ------------------------------------------------------------------------------------------------------------------------
class Node:
    """One data.json: the full history of the children of the node at `path` (a tuple of display names from the root)."""
    __slots__ = ("path", "names", "dates", "vals", "idx")

    def __init__(self, path, names, dates, vals):
        self.path, self.names, self.dates, self.vals = tuple(path), list(names), list(dates), vals
        self.idx = {d: i for i, d in enumerate(self.dates)}

    def value(self, name, d):
        """The child's value at month-end d, None if this file has no such month."""
        i = self.idx.get(d)
        return None if i is None else self.vals[name][i]

    def nonzero(self, name):
        return any(v != 0 for v in self.vals[name])

    def nonzero_children(self):
        return [n for n in self.names if self.nonzero(n)]


def json_load(body):
    """JSON with money parsed as Decimal (R8)."""
    text = body.decode("utf-8") if isinstance(body, (bytes, bytearray)) else body
    if M("g8_float_parse"):
        return json.loads(text, parse_float=float)
    return json.loads(text, parse_float=Decimal)


def parse_node(body, path=()):
    """Parse and content-test one monitor node file (R3b, G2, G9). Raises DataError on any breach, whatever the shape of the breach."""
    try:
        return _parse_node(body, path)
    except DataError:
        raise
    except (ValueError, TypeError, KeyError, IndexError, AttributeError, OverflowError, ArithmeticError) as e:
        raise DataError("node file has an unexpected shape (%s: %s)" % (type(e).__name__, str(e)[:80]))


def _parse_node(body, path=()):
    try:
        doc = json_load(body)
    except (ValueError, UnicodeDecodeError) as e:
        raise DataError("not JSON: %s" % str(e)[:80])
    if not isinstance(doc, dict) or "datatable" not in doc or "highcharts" not in doc:
        raise DataError("keys datatable and highcharts missing")
    hc, dtb = doc["highcharts"], doc["datatable"]
    if not isinstance(hc, list) or not hc or not isinstance(dtb, dict) or "columns" not in dtb or "values" not in dtb:
        raise DataError("highcharts or datatable has the wrong shape")
    cols = [c.get("title") if isinstance(c, dict) else None for c in dtb["columns"]]
    names = [s.get("name") for s in hc]
    if cols[:1] != ["Date"] or cols[1:] != names:
        raise DataError("datatable column titles after Date differ from the highcharts names in order")
    if len(set(names)) != len(names):
        raise DataError("duplicate series name")
    dates, vals = None, {}
    for s in hc:
        data = s.get("data")
        if not isinstance(data, list):
            raise DataError("series %r has no data list" % s.get("name"))
        ds = [tz_epoch_ms_to_date(p[0]) for p in data]
        if dates is None:
            dates = ds
        elif ds != dates:
            raise DataError("series %r has different dates from the first series" % s.get("name"))
        vals[s["name"]] = [to_dec(p[1]) for p in data]
    for d in dates:
        if not is_month_end(d) and not M("g9_nonmonthend_ok"):
            raise DataError("date %s is not a calendar month-end" % d)
    if dates != sorted(set(dates)):
        raise DataError("dates are not strictly increasing")
    rows = dtb["values"]
    if len(rows) != len(dates):
        raise DataError("datatable has %d rows, highcharts %d dates" % (len(rows), len(dates)))
    for i, row in enumerate(rows):
        try:
            rd = parse_mdy(row[0])
        except (ValueError, IndexError, AttributeError):
            raise DataError("datatable date %r is not MM-DD-YYYY" % (row[:1],))
        if rd != dates[i]:
            raise DataError("datatable date %s differs from highcharts date %s" % (rd, dates[i]))
        if not M("g2_dt_skip"):
            for j, n in enumerate(names):
                if to_dec(row[j + 1]) != vals[n][i]:
                    raise DataError("datatable differs from highcharts at %s, series %r" % (rd, n))
    return Node(path, names, dates, vals)


def parse_date_json(body, key):
    """asof.json / updated.json: one key, a date like 'September 30, 2026' (R3b). Returns the date."""
    try:
        doc = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise DataError("%s: not JSON" % key)
    if not isinstance(doc, dict) or list(doc.keys()) != [key]:
        raise DataError("%s: expected exactly the key %r" % (key, key))
    try:
        return parse_date_text(doc[key])
    except (ValueError, TypeError) as e:
        raise DataError("%s: %s" % (key, e))


def parse_api(body, mnemonic):
    """API series: top key equals the mnemonic; timeseries.aggregation is a list of [YYYY-MM-DD, number] (R3b). Returns {date: Decimal}."""
    try:
        doc = json_load(body)
    except (ValueError, UnicodeDecodeError):
        raise DataError("API %s: not JSON" % mnemonic)
    if not isinstance(doc, dict) or list(doc.keys()) != [mnemonic]:
        raise DataError("API %s: top key is not the mnemonic" % mnemonic)
    try:
        agg = doc[mnemonic]["timeseries"]["aggregation"]
        out = {}
        for p in agg:
            if len(p) != 2 or not DATE_RX.match(p[0]):
                raise ValueError("bad pair")
            out[D_(p[0])] = to_dec(p[1])
    except (KeyError, TypeError, ValueError):
        raise DataError("API %s: timeseries.aggregation is not a list of [date, number]" % mnemonic)
    if not out:
        raise DataError("API %s: no observations" % mnemonic)
    return out


def body_problem(kind, body, mnemonic=None):
    """The content test for a fetched body: None if it passes, else the reason (R3b). `kind` is updated, asof, node or api."""
    try:
        if kind == "updated":
            parse_date_json(body, "updated")
        elif kind == "asof":
            parse_date_json(body, "asof")
        elif kind == "node":
            parse_node(body)
        elif kind == "api":
            parse_api(body, mnemonic)
        else:
            return "unknown kind %r" % kind
    except DataError as e:
        return str(e)
    return None


# ---- the crawl frontier (2.3, G17) ------------------------------------------------------------------------------------------
def needed(nodes):
    """Node paths still to be fetched, given the nodes already in hand: breadth-first per 2.3. This one function decides what is fetched (by `fetch`)
    and what must be present (by `build`)."""
    root = nodes.get(())
    if root is None:
        return [()]
    out = []
    check_siblings(root.names, "root")
    for cat in root.nonzero_children():
        pc = (cat,)
        cn = nodes.get(pc)
        if cn is None:
            out.append(pc)
            continue
        check_siblings(cn.names, "/".join(pc))
        for reg in cn.nonzero_children():
            pr = pc + (reg,)
            rn = nodes.get(pr)
            if rn is None:
                out.append(pr)
                continue
            if reg == SUPRA_REGION:
                continue
            check_siblings(rn.names, "/".join(pr))
            for cty in rn.nonzero_children():
                pt = pr + (cty,)
                tn = nodes.get(pt)
                if tn is None:
                    out.append(pt)
                    continue
                check_siblings(tn.names, "/".join(pt))
                for sec in tn.nonzero_children():
                    if sec != FI_SECTOR and not M("g17_drill_nonfin"):
                        continue
                    pf = pt + (sec,)
                    fn = nodes.get(pf)
                    if fn is None:
                        out.append(pf)
                        continue
                    if cty == USA and not M("g17_drill_us"):
                        continue          # the FICC memo line: the file is read for the FICC child only, no US parent is drilled
                    check_siblings(fn.names, "/".join(pf))
                    for par in fn.nonzero_children():
                        if par == SMALL_ISSUERS:
                            continue
                        pp = pf + (par,)
                        if pp not in nodes:
                            out.append(pp)
    if M("g17_all_ficc_cats"):
        # mutant: the USA financial-institution file for every category, whether or not the category has a nonzero month
        for cat, _lin in CATEGORIES:
            p = (cat, "North America", USA, FI_SECTOR)
            if p not in nodes and p not in out:
                out.append(p)
    return sorted(set(out), key=lambda p: (len(p), p))


def node_problems(nodes, tol=None):
    """Node identities (3.4): on every node and month, the children sum to the node's value in the parent's file (tolerance 1.00 USD). A month a child
    file lacks counts as zero, so a month the parent has but the child file omits is a breach (G2, G3). Returns a list of problem strings."""
    tol = IDENT_TOL if tol is None else tol
    if M("g2_tol_5"):
        tol = Decimal("5.00")
    probs = []
    for p in sorted(nodes, key=lambda x: (len(x), x)):
        if not p:
            continue
        parent = nodes.get(p[:-1])
        n = nodes[p]
        if parent is None or p[-1] not in parent.vals:
            probs.append("%s: no parent series %r" % ("/".join(p), p[-1]))
            continue
        pvals = parent.vals[p[-1]]
        cols = [n.vals[x] for x in n.names]
        if M("g2_drop_child"):
            cols = cols[1:]
        if M("g2_double_child") and cols:
            cols = cols + [cols[0]]
        for i, d in enumerate(n.dates):
            s = dsum(c[i] for c in cols)
            pv = parent.value(p[-1], d)
            pv = Decimal(0) if pv is None else pv
            if abs(s - pv) > tol:
                probs.append("%s %s: children sum %s, parent %s" % ("/".join(p), d, s, pv))
                break
        if M("g3_fill_zero"):
            continue
        for j, d in enumerate(parent.dates):
            if d not in n.idx and abs(pvals[j]) > tol:
                probs.append("%s %s: month missing from the child file while the parent is %s" % ("/".join(p), d, pvals[j]))
                break
    return probs


def lineage_problems(root):
    """The category lineages (2.1, G3): old and new category names are never both nonzero in one month; 'Government' is a name of 2011-16 and of 2024
    onward, not of 2011-16 alone. Returns problem strings."""
    probs = []
    lin = cat_lineage()
    for ln in LINEAGES:
        legacy = LEGACY_NAME[ln]
        new = [c for c, l in lin.items() if l == ln and c != legacy]
        if legacy not in root.vals:
            continue
        for i, d in enumerate(root.dates):
            if root.vals[legacy][i] != 0 and not M("g3_both_ok") and any(c in root.vals and root.vals[c][i] != 0 for c in new):
                probs.append("%s: %r and a post-2016 name of its lineage are both nonzero" % (d, legacy))
                break
        if M("g3_gov_pre_only") and ln == "government":
            late = [d for i, d in enumerate(root.dates) if root.vals[legacy][i] != 0 and d >= dt.date(2016, 4, 1)]
            if late:
                probs.append("%r nonzero from %s: treated as a pre-2016 name only" % (legacy, late[0]))
    return probs


def category_counts(root):
    """Nonzero month counts of the nine categories in CATEGORIES order (C07)."""
    return [sum(1 for v in root.vals[c] if v != 0) if c in root.vals else 0 for c, _ in CATEGORIES]


def api_total_problems(root, api_total, tol=None):
    """The nine categories sum to MMF-MMF_TOT-M on every month (G4). Returns (problems, max gap in USD)."""
    tol = IDENT_TOL if tol is None else tol
    if M("g4_no_check"):
        return [], Decimal(0)
    probs, gap = [], Decimal(0)
    for i, d in enumerate(root.dates):
        s = dsum(root.vals[n][i] for n in root.names)
        t = api_total.get(d)
        if t is None:
            probs.append("%s: no API total" % d)
            continue
        g = abs(s - t)
        gap = max(gap, g)
        lim = t * Decimal("0.001") if M("g4_tol_0p1pct") else tol
        if g > lim:
            probs.append("%s: categories sum %s, API total %s" % (d, s, t))
    return probs, gap


# ------------------------------------------------------------------------------------------------------------------------
# facts: what the nodes say, by country, parent and instrument (3.3, 3.5, 3.6)
# ------------------------------------------------------------------------------------------------------------------------
def sadd(dst, src):
    """dst[month] += src[month] in Decimal."""
    for d, v in src.items():
        if M("g8_round_before_sum"):
            v = qfix(usd_to_mn(v), 1) * 1_000_000
        dst[d] = dst.get(d, Decimal(0)) + v


def series_of(node, name):
    return {d: v for d, v in zip(node.dates, node.vals[name]) if v != 0}


class Facts:
    def __init__(self):
        self.months = []
        self.unknown = []                                  # (kind, label, where)
        self.relayed = []                                  # (label, where)
        self.small_issuers = []                            # where
        self.cgroups = {}                                  # country -> groups (tuple), non-US countries included in the totals
        self.cregion = {}
        self.head = {}                                     # country -> lineage -> {month: Decimal}   the Financial Institution sector (headline)
        self.pcells = {}                                   # (country, parent) -> lineage -> ig -> {month: Decimal}
        self.unalloc = {}                                  # country -> lineage -> {month: Decimal}   'Aggregated small issuers'
        self.ficc = {l: {} for l in LINEAGES}              # lineage -> {month: Decimal}
        self.total = {}                                    # month -> Decimal (all US MMFs, the root categories)
        self.lin_total = {l: {} for l in LINEAGES}

    def unk(self, kind, label, where):
        self.unknown.append((kind, label, where))


def ingest(nodes):
    """Read the cube. Unknown labels are collected over the whole vintage, not raised one at a time (F11, G7)."""
    F = Facts()
    root = nodes[()]
    F.months = list(root.dates)
    lin = cat_lineage()
    imap = itype_map()
    for c in root.names:
        if c not in lin:
            F.unk("category", c, "root")
    for i, d in enumerate(root.dates):
        F.total[d] = dsum(root.vals[n][i] for n in root.names)
        for l in LINEAGES:
            F.lin_total[l][d] = dsum(root.vals[n][i] for n in root.names if lin.get(n) == l)
    for p in sorted(nodes, key=lambda x: (len(x), x)):
        n, depth = nodes[p], len(p)
        if depth == 0:
            continue
        ln = lin.get(p[0])
        if depth == 1:
            for r in n.names:
                if r not in all_regions():
                    F.unk("region", r, p[0])
        if ln is None:
            continue
        if depth == 2:
            for c in n.names:
                g = classify_country(p[1], c)
                if g is None:
                    F.unk("country", c, "/".join(p))
                elif g[0] not in (EXCL_US, EXCL_SUPRA):
                    F.cgroups[c] = g
                    F.cregion[c] = p[1]
        elif depth == 3:
            for s in n.names:
                if s not in all_sectors():
                    F.unk("sector", s, "/".join(p))
            c = p[2]
            if c in F.cgroups:
                use = [FI_SECTOR]
                if M("g6_gov_counted"):
                    use.append("Government")
                if M("g6_nfc_counted"):
                    use.append("Non-Financial Corporate")
                for s in use:
                    if s in n.vals:
                        sadd(F.head.setdefault(c, {}).setdefault(ln, {}), series_of(n, s))
        elif depth == 4 and p[3] == FI_SECTOR:
            c = p[2]
            if c == USA:
                if "FICC" in n.vals:
                    sadd(F.ficc[ln], series_of(n, "FICC"))
            elif c in F.cgroups:
                if SMALL_ISSUERS in n.vals and n.nonzero(SMALL_ISSUERS):
                    F.small_issuers.append("/".join(p))
                    sadd(F.unalloc.setdefault(c, {}).setdefault(ln, {}), series_of(n, SMALL_ISSUERS))
        elif depth == 5 and p[3] == FI_SECTOR:
            c = p[2]
            if c in F.cgroups:
                cell = F.pcells.setdefault((c, p[4]), {}).setdefault(ln, {})
                for a in n.names:
                    g = imap.get(a)
                    if g is None:
                        F.unk("asset type", a, "/".join(p))
                        continue
                    if a in RELAYED_ITYPE_MAP and a not in ITYPE_MAP:
                        F.relayed.append((a, "/".join(p)))
                    sadd(cell.setdefault(g, {}), series_of(n, a))
    if M("g7_one_at_a_time") and F.unknown:
        F.unknown = F.unknown[:1]
    return F


def unknown_report(F):
    """All unknown labels together, each with the node where it appeared (F11, C13)."""
    seen, out = set(), []
    for kind, label, where in F.unknown:
        if (kind, label, where) in seen:
            continue
        seen.add((kind, label, where))
        out.append((kind, label, where))
    return out


def unknown_text(F):
    rows = unknown_report(F)
    if not rows:
        return "no unknown label"
    by = collections.OrderedDict()
    for kind, label, where in rows:
        by.setdefault((kind, label), []).append(where)
    return "; ".join("%s %r at %s%s" % (k, l, w[0], " (+%d more)" % (len(w) - 1) if len(w) > 1 else "") for (k, l), w in by.items())


# ------------------------------------------------------------------------------------------------------------------------
# levels: group x measure x lineage x month, in Decimal USD (3.5, 3.6)
# ------------------------------------------------------------------------------------------------------------------------
def lineage_sum(per_lineage):
    """{lineage: {month: v}} -> adds the 'all' key (the three lineages summed)."""
    out = {l: dict(per_lineage.get(l, {})) for l in LINEAGES}
    allv = {}
    for l in LINEAGES:
        sadd(allv, out[l])
    out["all"] = allv
    return out


def country_measures(F, kinds):
    """country -> measure -> lineage -> {month: Decimal}, for headline, unallocated, each instrument group, secured, unsecured, abcp, misc, bank_only."""
    mg = measure_groups()
    bk = bank_kinds()
    out = {}
    for c in F.cgroups:
        ms = {}
        ms["headline"] = lineage_sum(F.head.get(c, {}))
        ms["unallocated"] = lineage_sum(F.unalloc.get(c, {}))
        igs = {g: {l: {} for l in LINEAGES} for g in IG_ORDER}
        bankp = {l: {} for l in LINEAGES}
        for (cc, par), per in F.pcells.items():
            if cc != c:
                continue
            for l, byig in per.items():
                for g, s in byig.items():
                    sadd(igs[g][l], s)
                    if kinds.get((par, c)) in bk:
                        sadd(bankp[l], s)
        for g in IG_ORDER:
            if g != "unallocated":
                ms[g] = lineage_sum(igs[g])
        ms["bank_only"] = lineage_sum(bankp)
        for m, parts in mg.items():
            acc = {l: {} for l in LINEAGES}
            for g in parts:
                for l in LINEAGES:
                    sadd(acc[l], ms[g][l])
            ms[m] = lineage_sum(acc)
        out[c] = ms
    return out


def group_levels(F, kinds):
    """(group, measure, lineage) -> {month: Decimal USD}. ALL_NONUS is the sum of the nine groups (3.5); FR sits inside EA; MEMO_FICC is outside every total.
    Also the internal measure 'unallocated' (for C16) and, for ALL_NONUS, nothing else is added."""
    cm = country_measures(F, kinds)
    meas = list(MEASURES) + ["unallocated"]
    G = {}
    for gname in GROUP_ORDER:
        if gname in ("ALL_NONUS", "MEMO_FICC"):
            continue
        members = [c for c, gs in F.cgroups.items() if gname in gs]
        for m in meas:
            for l in LINEAGE_ALL:
                s = {}
                for c in members:
                    sadd(s, cm[c][m][l])
                G[(gname, m, l)] = s
    nine = NINE
    for m in meas:
        for l in LINEAGE_ALL:
            s = {}
            parts = list(nine)
            if M("g5_fr_in_all"):
                parts.append("FR")
            if M("g20_all_skips_other"):
                parts.remove("OTHER")
            for g in parts:
                sadd(s, G[(g, m, l)])
            if M("g5_ficc_in_all") and m == "headline":
                sadd(s, lineage_sum(F.ficc)[l])
            G[("ALL_NONUS", m, l)] = s
    fl = lineage_sum(F.ficc)
    for l in LINEAGE_ALL:
        G[("MEMO_FICC", "headline", l)] = fl[l]
    return G, cm


def measure_identity_problems(G, tol=None):
    """C16: secured + unsecured + abcp + misc + unallocated = headline, for every group, month and lineage (1.00 USD)."""
    tol = IDENT_TOL if tol is None else tol
    probs = []
    for gname in GROUP_ORDER:
        if gname == "MEMO_FICC":
            continue
        for l in LINEAGE_ALL:
            h = G[(gname, "headline", l)]
            parts = [G[(gname, m, l)] for m in ("secured", "unsecured", "abcp", "misc", "unallocated")]
            for d in sorted(set(h).union(*[set(x) for x in parts])):
                s = dsum(x.get(d, Decimal(0)) for x in parts)
                if abs(s - h.get(d, Decimal(0))) > tol:
                    probs.append("%s %s %s: parts %s, headline %s" % (gname, l, d, s, h.get(d, Decimal(0))))
                    break
    return probs


def group_sum_problems(G, tol=Decimal("0.5")):
    """The nine groups sum to ALL_NONUS in every month, measure and lineage (G20). Compared in USD millions rounded to 0.1, as the files hold them."""
    probs = []
    for m in MEASURES:
        for l in LINEAGE_ALL:
            tot = G[("ALL_NONUS", m, l)]
            ms = set(tot)
            for g in NINE:
                ms |= set(G[(g, m, l)])
            for d in sorted(ms):
                s = dsum(qfix(usd_to_mn(G[(g, m, l)].get(d, Decimal(0))), 1) for g in NINE)
                t = qfix(usd_to_mn(tot.get(d, Decimal(0))), 1)
                if abs(s - t) > tol:
                    probs.append("%s %s %s: nine groups %s, ALL_NONUS %s" % (m, l, d, s, t))
                    break
    return probs


def pct(value, total):
    """100 x value / total as a Decimal, None if the total is zero or absent (R8)."""
    if value is None or not total:
        return None
    if M("g20_pct_units"):
        return Decimal(100) * Decimal(value) / usd_to_mn(total)
    return Decimal(100) * Decimal(value) / Decimal(total)


def levels_group_rows(G, F, total, vintage):
    """levels_group.csv rows (month_end, country_group, fund_lineage, measure, usd_mn, pct_of_mmf_total, pct_of_lineage_total, vintage)."""
    rows = []
    months = F.months
    for gname in GROUP_ORDER:
        for l in LINEAGE_ALL:
            ltot = total if l == "all" else F.lin_total[l]
            for m in MEASURES:
                if gname == "MEMO_FICC" and m != "headline":
                    continue
                s = G[(gname, m, l)]
                for d in months:
                    v = s.get(d, Decimal(0))
                    rows.append([d.isoformat(), gname, l, m, dstr(usd_to_mn(v), 1), dstr(pct(v, total.get(d)), 3), dstr(pct(v, ltot.get(d)), 3), vintage])
    rows.sort(key=lambda r: (r[0], GROUP_ORDER.index(r[1]), LINEAGE_ALL.index(r[2]), MEASURES.index(r[3])))
    return rows


def country_cells(F, cm):
    """(month, country, instrument_group or 'total', Decimal USD) for every nonzero cell of the non-US countries (all lineages), one 'total' per country-month."""
    out = []
    for c in sorted(F.cgroups):
        ms = cm[c]
        for d in F.months:
            items = []
            for g in IG_ORDER:
                v = ms[g]["all"].get(d, Decimal(0)) if g != "unallocated" else ms["unallocated"]["all"].get(d, Decimal(0))
                if v != 0:
                    items.append((g, v))
            tot = ms["headline"]["all"].get(d, Decimal(0))
            if not items and tot == 0:
                continue
            items.append(("total", tot))
            out.extend((d, c, g, v) for g, v in items)
    return out


def levels_country_rows(F, cm, G, total, vintage):
    """levels_country.csv: non-US countries, nonzero cells, one 'total' row per country-month."""
    den = G[("ALL_NONUS", "headline", "all")]
    if M("g20_nonus_den_bank"):
        den = G[("ALL_NONUS", "bank_only", "all")]
    rows = []
    for d, c, g, v in country_cells(F, cm):
        rows.append([d.isoformat(), c, F.cgroups[c][0], g, dstr(usd_to_mn(v), 1), dstr(pct(v, total.get(d)), 3), dstr(pct(v, den.get(d)), 3), vintage])
    rows.sort(key=lambda r: (r[0], r[1], (IG_ORDER + ("total",)).index(r[3])))
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# quarter-end statistics (3.8 to 3.11, section 4)
# ------------------------------------------------------------------------------------------------------------------------
BASES = ("calendar", "jp_march", "jp_other", "ca_fiscal")
W_PRE, W_TRANS, W_POST, W_AFTER = "pre_reform", "transition", "post_reform", "after_freeze"
SUMMARY_WINDOWS = (W_POST, W_PRE)                                # transition is written as rows and in no summary (F8)
BLIND_FROM = dt.date(2026, 6, 1)
MIN_N = 8
SQRT2 = math.sqrt(2.0)


def basis_months(basis):
    if basis == "calendar":
        return (3, 6, 9, 12)
    if basis == "jp_march":
        return (3, 6, 9, 12) if M("g10_jp_march_not_march") else (3,)
    if basis == "jp_other":
        return (6, 9, 12)
    return (1, 4, 7, 10)


def basis_stat_kind(basis):
    return "one_sided" if basis == "ca_fiscal" else "two_sided"


def basis_groups(basis):
    if basis == "calendar":
        return GROUP_ORDER
    return ("JP", "AUNZ") if basis.startswith("jp_") else ("CA", "AUNZ")


def group_measures(group):
    return ("headline",) if group == "MEMO_FICC" else QE_MEASURES


def window_of(d):
    """The window of the calendar quarter holding month-end d (4)."""
    idx = d.year * 4 + (d.month - 1) // 3
    if idx <= 2016 * 4 + 1:
        return W_PRE
    if idx <= 2016 * 4 + 3:
        return W_TRANS
    if idx <= 2026 * 4 + 1:
        return W_POST
    return W_AFTER


def stdev1(xs):
    """Sample sd, ddof = 1 (None below two values). The mutant uses ddof = 0."""
    if M("g10_sd_ddof0"):
        return statistics.pstdev(xs) if xs else None
    return statistics.stdev(xs) if len(xs) >= 2 else None


def qe_cell(series, months, i, basis):
    """The quarter-end statistics for the month at months[i] (3.8). `series` is {month: Decimal USD}; a month with no entry is zero."""
    kind = basis_stat_kind(basis)
    if M("g10_ca_two_sided") and basis == "ca_fiscal":
        kind = "two_sided"
    L = lambda j: (series.get(months[j], Decimal(0)) if 0 <= j < len(months) else None)
    lq = L(i)
    step_prev, step_next = 1, 1
    if M("g10_prev_qe_nbr"):
        step_prev, step_next = 3, 3
    if M("g10_ca_next_qe") and basis == "ca_fiscal":
        step_next = 2
    if kind == "two_sided":
        lp, ln_ = L(i - step_prev), L(i + step_next)
        cin = ln_pct(lq, lp) if lp is not None else None
        cout = ln_pct(ln_, lq) if ln_ is not None else None
        below = None
        if cin is not None and cout is not None:
            below = cin if M("g10_chg_in_only") else 0.5 * (cin - cout)
        usd = (lq - (lp + ln_) / 2) if lp is not None and ln_ is not None else None
        used = [months[j] for j in (i - step_prev, i, i + step_next) if 0 <= j < len(months)]
        return dict(prev=lp, qe=lq, next=ln_, cin=cin, cout=cout, below=below, usd=usd, used=used, kind=kind)
    ln_ = L(i + step_next)
    cout = ln_pct(ln_, lq) if ln_ is not None else None
    used = [months[j] for j in (i, i + step_next) if 0 <= j < len(months)]
    return dict(prev=None, qe=lq, next=ln_, cin=None, cout=cout, below=(-cout if cout is not None else None), usd=None, used=used, kind=kind)


def row_blind(window, group, measure, used):
    """`blind` (F8): yes only for a row the author could not have seen the answer to."""
    if window in (W_PRE, W_TRANS, W_AFTER):
        if not (M("g11_blind_pre_reform") and window == W_PRE) and not (M("g11_blind_transition") and window == W_TRANS) \
                and not (M("g11_blind_after_freeze") and window == W_AFTER):
            return "no"
    if any(d >= BLIND_FROM for d in used) and not M("g11_blind_2026"):
        return "no"
    if group == "ALL_NONUS" and measure in ("secured", "headline") and not M("g11_blind_allnonus"):
        return "no"
    return "yes"


def qe_rows_for(series, months, basis, group, measure):
    out = []
    ok = basis_months(basis)
    for i, d in enumerate(months):
        if d.month not in ok:
            continue
        c = qe_cell(series, months, i, basis)
        w = window_of(d)
        frozen = "yes" if (w != W_AFTER or M("g11_post2026_frozen")) else "no"
        primary = "yes" if (basis == "calendar" and group == "ALL_NONUS" and measure == "secured" and w == W_POST) else "no"
        if M("g11_two_primary") and basis == "calendar" and group == "ALL_NONUS" and measure == "headline" and w == W_POST:
            primary = "yes"
        out.append(dict(c, quarter=quarter_label(d), month=d, basis=basis, group=group, measure=measure, window=w, frozen=frozen, primary=primary,
                        blind=row_blind(w, group, measure, c["used"])))
    return out


def qe_all_rows(G, months):
    """Every quarter_ends row: (basis, group, measure) over the all-lineage levels."""
    rows = []
    for basis in BASES:
        for g in basis_groups(basis):
            for m in group_measures(g):
                rows.extend(qe_rows_for(G[(g, m, "all")], months, basis, g, m))
    return rows


def qe_row_strings(rows, vintage):
    out = []
    mn = lambda v: dstr(usd_to_mn(v), 1) if v is not None else ""
    for r in rows:
        out.append([r["quarter"], r["month"].isoformat(), r["basis"], r["kind"], r["group"], r["measure"], mn(r["prev"]), mn(r["qe"]), mn(r["next"]),
                    dstr(r["cin"], 4), dstr(r["cout"], 4), dstr(r["below"], 4), mn(r["usd"]), r["window"], r["frozen"], r["primary"], r["blind"], vintage])
    order = {b: i for i, b in enumerate(BASES)}
    out.sort(key=lambda x: (order[x[2]], GROUP_ORDER.index(x[4]), MEASURES.index(x[5]), x[1]))
    return out


def noise_changes(series, months, window, basis_kind):
    """Month-on-month log changes Jan->Feb, Apr->May, Jul->Aug, Oct->Nov in `window` (3.9): the only changes touching no calendar quarter-end month."""
    out = []
    starts = (1, 4, 7, 10)
    if M("g10_clean_touch_qe"):
        starts = (2, 5, 8, 11)
    for i, d in enumerate(months[:-1]):
        if d.month not in starts or window_of(d) != window:
            continue
        x = ln_pct(series.get(months[i + 1], Decimal(0)), series.get(d, Decimal(0)))
        if x is not None:
            out.append(x)
    return out


def noise_reference(series, months, window, kind):
    """(noise_clean_sd_pct, noise_n, raw sd): the sd of the clean changes divided by sqrt 2 for two-sided rows, the sd itself for one-sided rows."""
    ch = noise_changes(series, months, window, kind)
    sd = stdev1(ch)
    if sd is None:
        return None, len(ch), None
    div = SQRT2 if kind == "two_sided" else 1.0
    if M("g10_no_sqrt2") and kind == "two_sided":
        div = 1.0
    if M("g10_sqrt2_one_sided") and kind == "one_sided":
        div = SQRT2
    return sd / div, len(ch), sd


def pattern_of(n, mean, se):
    if n < (2 if M("g10_n8_off") else MIN_N) or mean is None or se is None:
        return "insufficient"
    if mean == 0:
        return "neither"
    thr = se
    if mean <= -2 * thr:
        return "lower"
    if mean >= 2 * thr:
        return "higher"
    return "neither"


def pattern_with_sd(n, mean, se, sd):
    """The pattern, with the mutant that thresholds on sd instead of se."""
    if M("g10_se_threshold_sd") and n >= MIN_N and sd is not None:
        return pattern_of(n, mean, sd)
    return pattern_of(n, mean, se)


def paired_vs(group_vals, aunz_vals):
    """(n, mean, se) of d(q) = below_g(q) - below_AUNZ(q) over quarters where both are non-blank (3.11)."""
    common = [q for q in group_vals if q in aunz_vals and group_vals[q] is not None and aunz_vals[q] is not None]
    d = [group_vals[q] - aunz_vals[q] for q in common]
    n = len(d)
    if n == 0:
        return 0, None, None
    mean = sum(d) / n
    if M("g10_paired_unpaired"):
        a = [group_vals[q] for q in common]
        b = [aunz_vals[q] for q in common]
        sa, sb = stdev1(a), stdev1(b)
        se = math.sqrt(sa * sa / n + sb * sb / n) if sa is not None and sb is not None else None
        return n, mean, se
    sd = stdev1(d)
    return n, mean, (sd / math.sqrt(n) if sd is not None else None)


def qe_summary_rows(rows, G, months, vintage):
    """qe_summary.csv rows (3.10, 3.11): per (basis, window, group, measure)."""
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["basis"], r["window"], r["group"], r["measure"])].append(r)
    out = []
    for (basis, window, group, measure), rs in by.items():
        if window not in SUMMARY_WINDOWS and not (M("g11_transition_in_summary") and window == W_TRANS):
            continue
        vals = [r["below"] for r in rs if r["below"] is not None]
        n = len(vals)
        mean = sum(vals) / n if n else None
        med = statistics.median(vals) if n else None
        sd = stdev1(vals) if n else None
        se = sd / math.sqrt(n) if sd is not None else None
        kind = rs[0]["kind"]
        nz, nn, _raw = noise_reference(G[(group, measure, "all")], months, window, kind)
        pn = pm = pse = None
        if group != "AUNZ":
            ga = {r["quarter"]: r["below"] for r in rs}
            aun = {r["quarter"]: r["below"] for r in by.get((basis, window, "AUNZ", measure), [])}
            pn, pm, pse = paired_vs(ga, aun)
        primary = "yes" if any(r["primary"] == "yes" for r in rs) else "no"
        if M("g11_summary_yes_from_no"):
            blind = "yes" if any(r["blind"] == "yes" for r in rs) else "no"
        else:
            blind = "yes" if all(r["blind"] == "yes" for r in rs) else "no"
        out.append([basis, kind, window, group, measure, str(n), str(len(rs) - n), dstr(mean, 4), dstr(med, 4), str(sum(1 for v in vals if v < 0)), dstr(sd, 4),
                    dstr(se, 4), dstr(nz, 4), str(nn), pattern_with_sd(n, mean, se, sd), "" if pn is None else str(pn), dstr(pm, 4), dstr(pse, 4), primary,
                    blind, vintage])
    order = {b: i for i, b in enumerate(BASES)}
    wo = {W_POST: 0, W_PRE: 1, W_TRANS: 2}
    out.sort(key=lambda x: (order[x[0]], wo[x[2]], GROUP_ORDER.index(x[3]), MEASURES.index(x[4])))
    return out


# ---- S1 (4.5) ----------------------------------------------------------------------------------------------------------
def s1_noise_n(G, months):
    """The clean-month sd (before dividing by sqrt 2) of ALL_NONUS `secured` in the post_reform window, as this build computes it."""
    _nz, _nn, raw = noise_reference(G[("ALL_NONUS", "secured", "all")], months, W_POST, "two_sided")
    return raw


def s1_history(rows, n_value):
    """Historical hit rate: the share of the 9 frozen year-ends (Decembers 2017 to 2025) with chg_in_pct <= -N for ALL_NONUS `secured`. Returns
    (hits, total, list of (month, chg_in))."""
    got = []
    for r in rows:
        if r["basis"] == "calendar" and r["group"] == "ALL_NONUS" and r["measure"] == "secured" and r["month"].month == 12 and 2017 <= r["month"].year <= 2025:
            got.append((r["month"], r["cin"]))
    got.sort()
    hits = sum(1 for _d, c in got if c is not None and n_value is not None and c <= -n_value)
    return hits, len(got), got


# ------------------------------------------------------------------------------------------------------------------------
# the cache and the vintages (R3c, R4, 2.4)
# ------------------------------------------------------------------------------------------------------------------------
VKEY_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MANIFEST = "manifest.csv"
REQCOUNT = "requests.txt"
VLOG = "fetch_log.csv"
OTHER_LOG = "fetch_log_other.csv"


def assert_ua(ua=UA):
    if not M("g17_ua_check_off"):
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


def check_url(host, target, method="GET"):
    """R1, R3: the host allowlist, GET only, never the complete-dataset zip, only the chart files and the four API series."""
    if method != "GET":
        raise Refused("only GET is used (got %s)" % method)
    if not M("g17_host_off"):
        if host not in HOST_ALLOW or host.endswith("sec.gov"):
            raise Refused("host %s is not on the allowlist" % host)
    if ZIP_NAME in target.lower() and not M("g17_zip_ok"):
        raise Refused("the complete-dataset zip is never requested")
    if host == HOST_WWW:
        if not target.startswith(MON_BASE) or not target.endswith(".json") or "?" in target or ".." in target:
            raise Refused("not a monitor chart file path: %s" % target)
    elif host == HOST_API:
        if target not in [api_url_path(m) for m in API_MNEMONICS]:
            raise Refused("not one of the four API series: %s" % target)


def file_name(url_path):
    """One file per node, named by the sha256 of its URL path (R4)."""
    return sha256_of(url_path.encode("utf-8")) + ".json"


def read_csv_plain(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        return [r for r in csv.reader(fh) if r]


def append_csv(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerow(row)
    with open(path, "a", encoding="utf-8", newline="") as fh:
        fh.write(buf.getvalue())


def read_manifest(folder):
    rows = read_csv_plain(os.path.join(folder, MANIFEST))
    if rows and rows[0] == ["url_path", "sha256", "bytes"]:
        rows = rows[1:]
    return rows


def manifest_sha(rows):
    """The vintage's manifest hash: sha256 of the sorted 'url_path,sha256,bytes' lines, so it does not depend on the order the files landed."""
    return sha256_of("".join("%s,%s,%s\n" % (r[0], r[1], r[2]) for r in sorted(rows, key=lambda r: r[0])).encode("utf-8"))


def vintage_dirs(cache):
    """Complete vintages only (folders named by the ISO key). A '.partial' folder is never a vintage (G18)."""
    if not os.path.isdir(cache):
        return []
    out = []
    for n in sorted(os.listdir(cache)):
        full = os.path.join(cache, n)
        if not os.path.isdir(full):
            continue
        if VKEY_RX.match(n) or (M("g18_partial_vintage") and n.endswith(".partial") and VKEY_RX.match(n[:-8])):
            out.append(n if VKEY_RX.match(n) else n[:-8])
    return out


def vintage_folder(cache, key):
    full = os.path.join(cache, key)
    if os.path.isdir(full):
        return full
    return full + ".partial"


class Vintage:
    pass


def load_vintage(folder, key=None):
    """Read one cached vintage in full: re-test every body, verify the manifest, and walk the tree with `needed` (the same frontier `fetch` used). Raises
    DataError for anything incomplete, changed or unexpected."""
    base = os.path.basename(folder.rstrip(os.sep))
    if base.endswith(".partial") and not M("g18_partial_vintage"):
        raise DataError("a .partial folder is not a vintage: %s" % base)
    rows = read_manifest(folder)
    by = {}
    for r in rows:
        if r[0] in by:
            raise DataError("manifest lists %s twice" % r[0])
        by[r[0]] = r
    V = Vintage()
    V.folder, V.manifest, V.manifest_sha = folder, rows, manifest_sha(rows)

    def body(url):
        if url not in by:
            raise DataError("incomplete vintage: %s is not in the manifest" % url)
        p = os.path.join(folder, file_name(url))
        if not os.path.exists(p):
            raise DataError("file for %s is missing" % url)
        with open(p, "rb") as fh:
            b = fh.read()
        if sha256_of(b) != by[url][1] or str(len(b)) != by[url][2]:
            raise DataError("file for %s does not match its manifest row" % url)
        used.add(url)
        return b

    used = set()
    V.updated = parse_date_json(body(UPDATED_PATH), "updated")
    V.asof = parse_date_json(body(ASOF_PATH), "asof")
    V.key = V.updated.isoformat()
    if base.replace(".partial", "") != V.key:
        raise DataError("folder %s is not named by the updated.json date %s" % (base, V.key))
    V.api = {m: parse_api(body(api_url_path(m)), m) for m in API_MNEMONICS}
    nodes = {}
    while True:
        need = needed(nodes)
        if not need:
            break
        for p in need:
            nodes[p] = parse_node(body(node_url_path(p)), p)
    extra = sorted(set(by) - used)
    if extra:
        raise DataError("manifest holds %d file(s) the tree walk does not use: %s" % (len(extra), extra[0]))
    V.nodes = nodes
    V.requests = 0
    try:
        V.requests = int(open(os.path.join(folder, REQCOUNT), encoding="utf-8").read().strip())
    except (OSError, ValueError):
        V.requests = len(read_csv_plain(os.path.join(folder, VLOG)))
    lg = read_csv_plain(os.path.join(folder, VLOG))
    V.retrieved = max((r[0][:10] for r in lg if r and DATE_RX.match(r[0][:10])), default=None)
    return V


def vintage_order_problems(vints, committed_rows=None):
    """G18: an asof earlier than the previous vintage's is a FAIL; the same key with a different manifest sha256 is a FAIL."""
    probs = []
    last = None
    for v in sorted(vints, key=lambda x: x.key):
        if last is not None and v.asof < last.asof and not M("g18_earlier_asof_ok"):
            probs.append("vintage %s has asof %s, earlier than %s of vintage %s" % (v.key, v.asof, last.asof, last.key))
        last = v
    for r in committed_rows or []:
        for v in vints:
            if r[0] == v.key and r[5] != v.manifest_sha and not M("g18_same_key_ok"):
                probs.append("vintage %s was built from manifest %s and now has %s" % (v.key, r[5][:12], v.manifest_sha[:12]))
    return probs


# ---- the request log, as committed (fetch_log.csv) ---------------------------------------------------------------------
def all_log_rows(cache):
    """Every request ever logged in this cache: the rows of requests outside any vintage, then each vintage's own log, in key order."""
    rows = list(read_csv_plain(os.path.join(cache, OTHER_LOG)))
    if os.path.isdir(cache):
        for n in sorted(os.listdir(cache)):
            if os.path.isdir(os.path.join(cache, n)) and (VKEY_RX.match(n) or (n.endswith(".partial") and VKEY_RX.match(n[:-8]))):
                rows.extend(read_csv_plain(os.path.join(cache, n, VLOG)))
    return rows


def render_csv(name, rows, source, header=None):
    cols = header or allowlist()[name]
    buf = io.StringIO()
    buf.write(source.rstrip("\n") + "\n")
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(cols)
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def fetch_log_source(cache):
    keys = [n[:-8] if n.endswith(".partial") else n for n in sorted(os.listdir(cache)) if VKEY_RX.match(n.replace(".partial", ""))] if os.path.isdir(cache) else []
    return ("# source: request log of bin/mmf_nonus_banks.py fetch (www.financialresearch.gov, data.financialresearch.gov), vintage(s) %s; "
            "Office of Financial Research, OFR Money Market Fund Monitor; %s" % (", ".join(keys) or "none yet", CITATION))


def sync_fetch_log(cache, out_dir):
    """Write the committed fetch_log.csv from the cache's logs. Deterministic given the cache; no other file is touched."""
    write_text(os.path.join(out_dir, "fetch_log.csv"), render_csv("fetch_log.csv", all_log_rows(cache), fetch_log_source(cache)))


# ------------------------------------------------------------------------------------------------------------------------
# fetch (R1 to R3c)
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
    return "status: %s\nutc_time: %s\nurl_path: %s\nretry_after: %s\nbody_head: %s\n" % (status, utc_time, url_path, retry_after, body_head)


def stamp(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % int((ts % 1) * 1000)


class Fetcher:
    """All requests go through here. Opener, clock, sleeper and the STOP directories are injectable so every rule is testable without a network."""

    def __init__(self, cache, out_dir, stop_dirs=None, opener=real_opener, wall=time.time, mono=time.monotonic, sleeper=time.sleep, utc=None,
                 sleep=DEFAULT_SLEEP, budget=BUDGET, max_requests=None, max_seconds=None, say=print):
        if float(sleep) < MIN_SLEEP and not M("g17_pacing_off"):
            raise Refused("--sleep must be at least %g seconds" % MIN_SLEEP)
        self.cache, self.out_dir = os.path.abspath(os.path.expanduser(cache)), out_dir
        self.stop_dirs = list(stop_dirs) if stop_dirs is not None else [self.cache, CACHE_DEFAULT]
        self.opener, self.wall, self.mono, self.sleeper = opener, wall, mono, sleeper
        self.utc = utc or (lambda: dt.datetime.now(dt.timezone.utc))
        self.sleep, self.budget = float(sleep), budget
        self.max_requests, self.max_seconds = max_requests, max_seconds
        self.say = say
        self.requests_run = 0
        self.key = None
        self.partial = None
        self.count = 0
        self.pre = []
        self._last_mono = None
        self._t0 = mono()
        self._last_file = os.path.join(self.cache, ".last_request")

    # -- latches --------------------------------------------------------------------------------------------------------
    def stop_present(self):
        for d in self.stop_dirs:
            for n in (STOP_OFR, STOP_API, STOP_BUDGET):
                if os.path.exists(os.path.join(d, n)):
                    return os.path.join(d, n)
        return None

    def check_stop(self):
        p = self.stop_present()
        if p and not M("g17_stop_ignored"):
            raise Latched("STOP present: %s" % os.path.basename(p))

    def _latch(self, name, status, target, retry_after, body, why):
        """Write the STOP file (exclusive create: an existing one is never overwritten) and end the run."""
        os.makedirs(self.cache, exist_ok=True)
        path = os.path.join(self.cache, name)
        text = stop_fields(status, self.utc().strftime("%Y-%m-%dT%H:%M:%SZ"), target, retry_after or "", esc_head(body))
        try:
            with open(path, "x", encoding="utf-8") as fh:
                fh.write(text)
        except FileExistsError:
            pass
        raise Latched("STOP written: %s (%s)" % (name, why))

    # -- bookkeeping ----------------------------------------------------------------------------------------------------
    def _log(self, ts, host, target, status, nbytes, sha):
        row = [stamp(ts), host, target, str(status), str(nbytes), sha]
        if self.partial:
            append_csv(os.path.join(self.partial, VLOG), row)
        else:
            self.pre.append(row)

    def _bump(self):
        self.count += 1
        if self.partial:
            write_text(os.path.join(self.partial, REQCOUNT), "%d\n" % self.count)

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
        if wait > 0 and not M("g17_pacing_off"):
            self.sleeper(min(wait, self.sleep))

    def _get(self, host, target, kind, mnemonic=None):
        """One request. Returns the body of a 200 that passed its content test; otherwise latches or raises."""
        check_url(host, target)
        self.check_stop()
        if self.key and self.count >= self.budget and not M("g16_no_budget"):
            self._latch(STOP_BUDGET, "budget", target, "", b"", "request %d of the budget %d" % (self.count + 1, self.budget))
        if self.max_requests is not None and self.requests_run >= self.max_requests:
            raise SliceEnd("per-invocation request cap reached (%d)" % self.max_requests)
        if self.max_seconds is not None and self.mono() - self._t0 >= self.max_seconds:
            raise SliceEnd("per-invocation time cap reached (%d s)" % self.max_seconds)
        self._pace()
        started = self.wall()
        self._last_mono = self.mono()
        os.makedirs(self.cache, exist_ok=True)
        write_text(self._last_file, "%r\n" % started)
        self.requests_run += 1
        self._bump()
        stop_name = STOP_API if host == HOST_API else STOP_OFR
        try:
            status, body, rh = self.opener(host, target, dict(HEADERS), TIMEOUT, BODY_CAP)
        except SocketFault:
            self._log(started, host, target, "socket_fault", "", "")
            raise
        if status == 429 and M("g17_retry"):
            self._log(started, host, target, status, len(body or b""), sha256_of(body or b""))
            started = self.wall()
            self.requests_run += 1
            self._bump()
            status, body, rh = self.opener(host, target, dict(HEADERS), TIMEOUT, BODY_CAP)
        if 300 <= status < 400 and M("g17_redirect_ok") and rh.get("location"):
            self._log(started, host, target, status, len(body or b""), sha256_of(body or b""))
            started = self.wall()
            self.requests_run += 1
            self._bump()
            target = rh["location"]
            status, body, rh = self.opener(host, target, dict(HEADERS), TIMEOUT, BODY_CAP)
        if status != 200:
            self._log(started, host, target, status, len(body or b""), sha256_of(body or b""))
            if M("g16_no_latch_403"):
                raise Latched("HTTP %s (mutant: no STOP written)" % status)
            self._latch(stop_name, status, target, rh.get("retry-after", ""), body, "HTTP %s" % status)
        if body is None:
            self._log(started, host, target, status, "", "")
            self._latch(stop_name, status, target, "", b"", "body larger than the cap")
        self._log(started, host, target, status, len(body), sha256_of(body))
        problem = body_problem(kind, body, mnemonic)
        if problem:
            self._latch(stop_name, status, target, "", body, "content test: %s" % problem)
        return body

    def _save(self, url_path, body):
        write_bytes(os.path.join(self.partial, file_name(url_path)), body)
        append_csv(os.path.join(self.partial, MANIFEST), [url_path, sha256_of(body), str(len(body))])

    def _move_pre_to_other(self):
        for r in self.pre:
            append_csv(os.path.join(self.cache, OTHER_LOG), r)
        self.pre = []

    # -- the run --------------------------------------------------------------------------------------------------------
    def run(self):
        """Returns the exit code: 0 complete (or already complete), 2 STOP or release changed, 3 slice ended, 4 socket fault."""
        try:
            return self._run()
        except Latched as e:
            self.say(str(e))
            return 2
        except SliceEnd as e:
            self.say("slice ends: %s; run fetch again to resume (%d requests so far for vintage %s)" % (e, self.count, self.key))
            return 3
        except SocketFault as e:
            self.say("socket fault (%s): not a refusal, nothing latched; run fetch again to resume (%d requests so far)" % (e, self.count))
            return 4
        except DataError as e:
            self.say("STOP (data): %s" % e)
            return 2
        finally:
            if self.pre:
                self._move_pre_to_other()
            if self.out_dir:
                sync_fetch_log(self.cache, self.out_dir)

    def _run(self):
        self.check_stop()
        body = self._get(HOST_WWW, UPDATED_PATH, "updated")
        upd = parse_date_json(body, "updated")
        key = now_utc().date().isoformat() if M("g18_key_clock") else upd.isoformat()
        if os.path.isdir(os.path.join(self.cache, key)) and not M("g17_recrawl"):
            self._move_pre_to_other()
            self.say("vintage %s is already complete in the cache; nothing to fetch" % key)
            return 0
        self.key = key
        self.partial = os.path.join(self.cache, key + ".partial")
        os.makedirs(self.partial, exist_ok=True)
        prior = 0
        try:
            prior = int(open(os.path.join(self.partial, REQCOUNT), encoding="utf-8").read().strip())
        except (OSError, ValueError):
            pass
        self.count = prior + self.requests_run
        write_text(os.path.join(self.partial, REQCOUNT), "%d\n" % self.count)
        for r in self.pre:
            append_csv(os.path.join(self.partial, VLOG), r)
        self.pre = []
        done = {r[0]: r for r in read_manifest(self.partial)}
        if UPDATED_PATH not in done:
            self._save(UPDATED_PATH, body)
            done[UPDATED_PATH] = [UPDATED_PATH]
        if ASOF_PATH not in done:
            self._save(ASOF_PATH, self._get(HOST_WWW, ASOF_PATH, "asof"))
            done[ASOF_PATH] = [ASOF_PATH]
        for m in API_MNEMONICS:
            u = api_url_path(m)
            if u not in done:
                self._save(u, self._get(HOST_API, u, "api", m))
                done[u] = [u]
        nodes = {}
        while True:
            need = needed(nodes)
            if not need:
                break
            for p in need:
                url = node_url_path(p)
                if url in done and not M("g17_refetch_manifest"):
                    with open(os.path.join(self.partial, file_name(url)), "rb") as fh:
                        nodes[p] = parse_node(fh.read(), p)
                    continue
                b = self._get(HOST_WWW, url, "node")
                self._save(url, b)
                done[url] = [url]
                nodes[p] = parse_node(b, p)
        self.say("frontier empty: %d node files for vintage %s (%d requests so far)" % (len(nodes), key, self.count))
        again = parse_date_json(self._get(HOST_WWW, UPDATED_PATH, "updated"), "updated")
        if again != upd and not M("g17_keep_changed"):
            for r in read_csv_plain(os.path.join(self.partial, VLOG)):
                append_csv(os.path.join(self.cache, OTHER_LOG), r)
            shutil.rmtree(self.partial)                       # that one .partial folder, by its exact path (R3c)
            self.say("release changed during crawl: updated.json said %s, now %s; the partial crawl was removed; run fetch again" % (upd, again))
            return 2
        final = os.path.join(self.cache, key)
        os.rename(self.partial, final)
        self.say("vintage %s complete: %d node files, %d requests; saved under %s" % (key, len(nodes), self.count, tilde(final)))
        return 0


# ------------------------------------------------------------------------------------------------------------------------
# guards on the committed folder: allowlists, leaks, wording (5, 6, 7 G13 to G15)
# ------------------------------------------------------------------------------------------------------------------------
CAUSAL_RX = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|"
                       r"in\s+response\s+to|because\s+of)\b", re.I)
EXTRA_RX = re.compile(r"\b(?:in|out)?flows?\b|window[- ]dressing|\b(?:head\s+offices?|parents?)\s+(?:fund|funds|funded|funding|push|pushes|pushed|pull|pulls|"
                      r"pulled|drain|drains|drained)\b|\b(?:dollar\s+)?(?:shortage|squeeze)\b|\bpull(?:ed|ing|s)?\s+(?:back|out)\b|\bretreat(?:ed|ing|s)?\b|"
                      r"\bruns?\s+on\b|\bflight\b|\blog[- ]points?\b|\bdips?\b", re.I)
DENIAL = "These month-end changes are not flows of funds, and the table does not test window dressing or any other motive."
README_S1 = ("This table shows how much US money market funds held at each month-end since January 2011 in claims on banks and other financial institutions "
             "whose ultimate parent, the company at the top of the group, is headquartered outside the United States, by that parent's home country and by "
             "type of instrument.")
README_S2 = ("The figures come from the funds' own monthly holdings reports to the Securities and Exchange Commission, called Form N-MFP, as compiled by the "
             "Treasury's Office of Financial Research (OFR), which assigns each security's issuer, or for a repurchase agreement (repo) the firm on the other "
             "side of the trade, called the repo counterparty, to its ultimate parent.")
README_S3 = "It records month-end holdings only; it does not show why they changed, and a change in holdings is not a measure of money moved."
README_FICC = "A fall in a country line may be offset by a rise in the FICC line shown next to it."
SOURCE_RX = re.compile(r"^# source:")


def wording_problems(name, text):
    """G15: the spec's two patterns applied to README.md everywhere but the one denial sentence. SOURCES.md is not scanned (it quotes reviews)."""
    if name != "README.md" or M("g15_scan_off"):
        return []
    t = text.replace(DENIAL, "", 1)                      # exactly the one sentence
    if M("g15_denial_everywhere"):
        t = re.sub(r"[^.]*\bflows?\b[^.]*\.", "", t)        # mutant: every sentence about flows is exempt
    rxs = (CAUSAL_RX,) if M("g15_only_causal") else (CAUSAL_RX, EXTRA_RX)
    hits = sorted({re.sub(r"\s+", " ", m.group(0).lower()) for rx in rxs for m in rx.finditer(t)})
    return ["README.md holds banned wording (R5): %s" % ", ".join(hits[:6])] if hits else []


def csv_body_lines(text):
    return [l for l in text.split("\n") if not SOURCE_RX.match(l)]


def check_header(name, text):
    want = ",".join(allowlist()[name])
    lines = text.split("\n") if M("g13_source_as_header") else csv_body_lines(text)
    got = (lines[0] if lines else "").rstrip("\r")
    return [] if got == want else ["header of %s is not its exact allowlist" % name]


def duplicate_key_problems(name, text):
    key = UNIQUE_KEYS.get(name)
    if not key or (name == "summary.csv" and M("g13_dup_summary_key")):
        return []
    rows = list(csv.reader(csv_body_lines(text)))
    if not rows:
        return []
    head = rows[0]
    if any(k not in head for k in key):
        return []
    idx = [head.index(k) for k in key]
    seen, dup = set(), []
    for r in rows[1:]:
        if len(r) <= max(idx):
            continue
        k = tuple(r[i] for i in idx)
        if k in seen:
            dup.append(k)
        seen.add(k)
    return ["duplicate key in %s: %s (%d duplicate row(s))" % (name, "|".join(dup[0]), len(dup))] if dup else []


def is_raw_json(text):
    for l in text.split("\n"):
        if SOURCE_RX.match(l) or not l.strip():
            continue
        s = l.lstrip()
        return s.startswith('{"datatable"') or s.startswith('{"highcharts"') or s.startswith("{") and ('"datatable"' in text[:2000] or '"highcharts"' in text[:2000])
    return False


def leak_problems(files):
    """G14 and the folder rules: `files` is {name: text}. Only the ten CSVs, README.md and SOURCES.md; no raw node JSON under any name; no local path; no at
    sign; every CSV header the exact allowlist; no duplicate key. Returns problem strings."""
    probs = []
    allowed = set(COMMITTED_NAMES) | set(DOC_NAMES)
    if M("g13_eleventh_csv"):
        allowed = set(allowed)
    for n in sorted(files):
        t = files[n]
        low = n.lower()
        if (low.endswith((".json", ".zip", ".html", ".pdf")) and not M("g14_json_ok")) or (is_raw_json(t) and not M("g14_renamed_ok")):
            probs.append("raw file in the committed folder: %s" % n)
            continue
        if n not in allowed:
            probs.append("file that is not one of the twelve committed names: %s" % n)
            continue
        if not M("g14_path_ok") and re.search(r"/Users/|/private/|~", t):
            probs.append("%s contains a local path (/Users/, /private/ or a tilde)" % n)
        if "@" in t:
            probs.append("%s contains an at sign" % n)
        if n.endswith(".csv"):
            probs.extend(check_header(n, t))
            probs.extend(duplicate_key_problems(n, t))
        probs.extend(wording_problems(n, t))
    for n in sorted(allowed - set(files)):
        probs.append("missing: %s" % n)
    return probs


def check_sh_problems(sh_text):
    """G13: bin/check.sh holds its own literal copy of the ten header lines (M23) and never reads them from the script."""
    i = sh_text.find("mmfnb_leak_check()")
    if i < 0:
        return ["bin/check.sh has no mmfnb_leak_check function (M23)"]
    block = re.split(r"\n(?:# --- M\d+|[a-z_0-9]+\(\) \{)", sh_text[i + 20:], maxsplit=1)[0]
    probs = []
    for line in SPEC_ALLOW_TEXT.splitlines():
        if line not in block:
            probs.append("M23 does not hold the canonical line for %s" % line.split(":")[0])
    if re.search(r"mmf_nonus_banks\.py", block) and not M("g13_check_reads_script"):
        probs.append("M23 refers to the build script: the header lines must be its own literal copy")
    return probs


# ------------------------------------------------------------------------------------------------------------------------
# pinned checks (8): values in USD to the cent, vintage 2026-10-15, as re-derived by the spec author from its cache
# ------------------------------------------------------------------------------------------------------------------------
PIN_VINTAGE = "2026-10-15"
GOV = "Government"
FR_FI = (GOV, "Europe", "France", FI_SECTOR)
PINS = (
    # (id, description, node path, child (None = sum of all children), month-end, expected USD)
    ("C01a", "sum of the nine root categories", (), None, "2026-09-30", "8396822287018.74"),
    ("C01b", "sum of the nine root categories", (), None, "2011-01-31", "3011802131036.00"),
    ("C02a", "France, Financial Institution sector, government funds", (GOV, "Europe", "France"), FI_SECTOR, "2026-09-30", "216102500879.82"),
    ("C02b", "sum of the seven French financial-institution parents, government funds", FR_FI, None, "2026-09-30", "216102500879.82"),
    ("C02c", "BNP Paribas, government funds", FR_FI, "BNP Paribas", "2026-09-30", "119064967826.42"),
    ("C02d", "Credit Agricole, government funds", FR_FI, "Credit Agricole", "2026-09-30", "51474585053.40"),
    ("C02e", "Societe Generale, government funds", FR_FI, "Societe Generale", "2026-09-30", "26237948000.00"),
    ("C02f", "Natexis + Natixis, government funds", FR_FI, "Natexis + Natixis", "2026-09-30", "19325000000.00"),
    ("C02g", "Axa SA, government funds", FR_FI, "Axa SA", "2026-09-30", "0"),
    ("C02h", "Credit Mutuel, government funds", FR_FI, "Credit Mutuel", "2026-09-30", "0"),
    ("C02i", "Groupe BPCE, government funds", FR_FI, "Groupe BPCE", "2026-09-30", "0"),
    ("C02j", "BNP Paribas Treasury repurchase agreements", FR_FI + ("BNP Paribas",), "Treasury Repurchase Agreement", "2026-09-30", "86062527564.34"),
    ("C02k", "BNP Paribas Government Agency repurchase agreements", FR_FI + ("BNP Paribas",), "Government Agency Repurchase Agreement", "2026-09-30",
     "33002440262.08"),
    ("C02l", "BNP Paribas asset types, sum", FR_FI + ("BNP Paribas",), None, "2026-09-30", "119064967826.42"),
    ("C03a", "Japan, all sectors, government funds", (GOV, "Asia"), "Japan", "2026-09-30", "113982689785.25"),
    ("C03b", "Canada, all sectors, government funds", (GOV, "North America"), "Canada", "2026-09-30", "237451088980.92"),
    ("C03c", "USA, all sectors, government funds", (GOV, "North America"), "USA", "2026-09-30", "6179508927720.00"),
    ("C03d", "region Europe, government funds", (GOV,), "Europe", "2026-09-30", "335544661517.19"),
    ("C03e", "France, all sectors, government funds", (GOV, "Europe"), "France", "2016-03-31", "55610766012.58"),
    ("C03f", "France, all sectors, government funds", (GOV, "Europe"), "France", "2024-06-30", "183349026908.53"),
    ("C04", "France, Financial Institution sector, government funds", (GOV, "Europe", "France"), FI_SECTOR, "2026-06-30", "209083190057.81"),
    ("C05a", "Prime Institutional, region Europe", ("Prime Institutional",), "Europe", "2026-09-30", "97894050668.11"),
    ("C05b", "Prime, region Europe", ("Prime",), "Europe", "2011-01-31", "885581940544.21"),
    ("C05c", "Prime, region Europe", ("Prime",), "Europe", "2016-03-31", "481729017251.35"),
    ("C05d", "Prime Institutional, region Europe", ("Prime Institutional",), "Europe", "2016-04-30", "530959993340.79"),
    ("C05e", "Government (Fees & Gates), region Europe", ("Government (Fees & Gates)",), "Europe", "2016-04-30", "63230004856.22"),
    ("C05f", "Government (Fees & Gates), region North America", ("Government (Fees & Gates)",), "North America", "2020-03-31", "4528754694.53"),
    ("C06", "FICC, USA Financial Institution sector, government funds", (GOV, "North America", USA, FI_SECTOR), "FICC", "2026-09-30", "909754515958.22"),
)


PIN_TABLE = PINS                   # the pins `build` checks; the selftest swaps in the synthetic world's own


def pin_value(nodes, path, child, d):
    n = nodes.get(tuple(path))
    if n is None:
        return None
    if child is None:
        if d not in n.idx:
            return None
        return dsum(n.vals[x][n.idx[d]] for x in n.names)
    if child not in n.vals:
        return None
    return n.value(child, d)


def pin_is_recent(d, asof):
    return (asof.year * 12 + asof.month) - (d.year * 12 + d.month) <= 12


def pin_status(observed, expected, d, asof, vintage_key, revised):
    """Recent pins FAIL on the pinned vintage and WARN on later ones; stable pins WARN if the cell was revised between the vintages, else FAIL."""
    if observed is not None and observed == expected:
        return "PASS"
    if pin_is_recent(d, asof):
        return "FAIL" if vintage_key == PIN_VINTAGE else "WARN"
    return "WARN" if revised else "FAIL"


def pin_rows(V, prevV, pins=PINS):
    out = []
    for pid, desc, path, child, ds, exp in pins:
        d = D_(ds)
        e = Decimal(exp)
        o = pin_value(V.nodes, path, child, d)
        rev = False
        if prevV is not None:
            po = pin_value(prevV.nodes, path, child, d)
            rev = po is not None and o is not None and po != o
        st = pin_status(o, e, d, V.asof, V.key, rev)
        where = "/".join(path) + ("" if child is None else (" / " if path else "") + child) if (path or child) else "root"
        out.append([pid, "%s: %s on %s" % (desc, where, ds), format(e, "f"), "absent" if o is None else format(o, "f"), st])
    return out


# ------------------------------------------------------------------------------------------------------------------------
# parents, revisions, vintages, summary
# ------------------------------------------------------------------------------------------------------------------------
def parent_series(F):
    """(country, parent) -> {month: Decimal} over all lineages and instruments."""
    out = {}
    for key, per in F.pcells.items():
        tot = {}
        for l in per:
            for g, s in per[l].items():
                sadd(tot, s)
        out[key] = tot
    return out


def parent_kind_keys(F):
    """(parent, country) for every non-US parent with a file: the key of the kind table."""
    return sorted((par, c) for (c, par) in parent_series(F))


def parents_rows(F, kinds, asof, vintage):
    rows = []
    for (c, par), tot in parent_series(F).items():
        nz = sorted(d for d, v in tot.items() if v != 0)
        if not nz:
            continue
        row = [par, c, F.cgroups[c][0], kinds.get((par, c), ""), nz[0].isoformat(), nz[-1].isoformat(), dstr(usd_to_mn(tot.get(asof, Decimal(0))), 1), vintage]
        if M("g19_parents_qe_col"):
            row.append("0.0")
        rows.append(row)
    rows.sort(key=lambda r: (r[0], r[1]))
    return rows


def vintage_cells(V):
    """The country-level cells of one vintage (for revisions): {(month, country, instrument_group): Decimal USD millions rounded to 0.1}."""
    F = ingest(V.nodes)
    cm = country_measures(F, {})
    return {(d, c, g): qfix(usd_to_mn(v), 1) for d, c, g, v in country_cells(F, cm)}


def revision_rows(prev_cells, new_cells, kp, kn):
    rows = []
    for k in set(prev_cells) | set(new_cells):
        a, b = prev_cells.get(k, Decimal(0)), new_cells.get(k, Decimal(0))
        if a != b:
            rows.append((k, [kp, kn, k[0].isoformat(), k[1], k[2], dstr(a, 1), dstr(b, 1), dstr(b - a, 1)]))
    rows.sort(key=lambda t: (t[0][0], t[0][1], (IG_ORDER + ("total",)).index(t[0][2])))
    return [r for _k, r in rows]


def all_revisions(vints, cells_by_key, existing=None):
    """Regenerated on every build from all adjacent pairs of complete cached vintages, never appended and never read from committed files (2.4).
    The mutant merges the committed file in."""
    keys = sorted(v.key for v in vints)
    rows = []
    for a, b in zip(keys, keys[1:]):
        rows.extend(revision_rows(cells_by_key[a], cells_by_key[b], a, b))
    if M("g18_revisions_incremental") and existing:
        have = {tuple(r) for r in rows}
        rows = [r for r in existing if tuple(r) not in have] + rows
    return rows


def api_check_text(V):
    probs, gap = api_total_problems(V.nodes[()], V.api["MMF-MMF_TOT-M"])
    return "ok, largest gap %s USD" % format(gap.quantize(Decimal("0.01")), "f") if not probs else "FAIL: " + probs[0]


def vintages_rows(vints, kt_sha):
    rows = []
    for v in sorted(vints, key=lambda x: x.key):
        rows.append([v.key, v.updated.isoformat(), v.asof.isoformat(), str(v.requests), str(len(v.nodes)), v.manifest_sha, api_check_text(v), kt_sha])
    return rows


def feb_endpoints(months):
    out = [d for d in months if d.month == 2]
    named = dt.date(2026, 8, 31)
    if named in months:
        out.append(named)
    if M("g12_qe_endpoint"):
        out.append(dt.date(2026, 9, 30))
    return out


Q2_ENDPOINTS = (dt.date(2024, 2, 29), dt.date(2025, 2, 28), dt.date(2026, 2, 28), dt.date(2026, 8, 31))


def summary_rows(G, F, total, vints, revs, qe_rows, s1, vintage):
    """summary.csv (F8 grammar): one statistic per row. Q1 and Q2 are for lineage `all` (the column set has no lineage; levels_group.csv holds every lineage)."""
    rows = []
    months = set(F.months)
    bl = "yes" if M("g11_blind_q") else "no"

    def add(q, window, g, m, a, b, stat, v, unit):
        rows.append([q, window, g, m, a.isoformat() if a else "", b.isoformat() if b else "", stat, v, unit, "no", bl])

    for g in GROUP_ORDER:
        for m in MEASURES:
            if g == "MEMO_FICC" and m != "headline":
                continue
            s = G[(g, m, "all")]
            for d in feb_endpoints(F.months):
                v = s.get(d, Decimal(0))
                add("Q1", "", g, m, d, d, "level", dstr(usd_to_mn(v), 1), "usd_mn")
                add("Q1", "", g, m, d, d, "pct_of_mmf_total", dstr(pct(v, total.get(d)), 3), "pct")
                add("Q1", "", g, m, d, d, "pct_of_lineage_total", dstr(pct(v, total.get(d)), 3), "pct")
            for a, b in zip(Q2_ENDPOINTS, Q2_ENDPOINTS[1:]):
                if a not in months or b not in months:
                    continue
                va, vb = s.get(a, Decimal(0)), s.get(b, Decimal(0))
                add("Q2", "", g, m, a, b, "change_usd_mn", dstr(usd_to_mn(vb - va), 1), "usd_mn")
                lc = ln_pct(vb, va)
                if lc is not None:
                    add("Q2", "", g, m, a, b, "change_chg_pct", dstr(lc, 4), "chg_pct")
                pa, pb = pct(va, total.get(a)), pct(vb, total.get(b))
                if pa is not None and pb is not None:
                    add("Q2", "", g, m, a, b, "change_pp", dstr(pb - pa, 3), "pp")
    keys = sorted(v.key for v in vints)
    for a, b in zip(keys, keys[1:]):
        rs = [r for r in revs if r[0] == a and r[1] == b]
        vb = next(v for v in vints if v.key == b)
        add("Q6", "", "", "", D_(a), D_(b), "cells_changed", str(len(rs)), "count")
        mx = max((abs(Decimal(r[7])) for r in rs), default=Decimal(0))
        add("Q6", "", "", "", D_(a), D_(b), "max_abs_change_usd_mn", dstr(mx, 1), "usd_mn")
        old = any((vb.asof.year * 12 + vb.asof.month) - (D_(r[2]).year * 12 + D_(r[2]).month) > 12 for r in rs)
        add("Q6", "", "", "", D_(a), D_(b), "old_month_revised", "yes" if old else "no", "yes_no")
    hits, n, got = s1
    if n:
        add("Q7", W_POST, "ALL_NONUS", "secured", got[0][0], got[-1][0], "hit_rate", dstr(Decimal(hits) / Decimal(n), 4), "share")
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# compute: everything the build writes, from the loaded vintages
# ------------------------------------------------------------------------------------------------------------------------
class Ctx:
    pass


def source_line(c, name=None):
    """The one '# source:' line that begins every CSV (5): the monitor, the vintage's updated and asof dates, the retrieval date, the citation."""
    V = c.V
    return ("# source: Office of Financial Research, OFR Money Market Fund Monitor (https://www.financialresearch.gov/money-market-funds/); vintage updated %s, "
            "data as of %s; retrieved %s (fetch_log.csv); derived statistics by bin/mmf_nonus_banks.py. %s"
            % (V.updated.isoformat(), V.asof.isoformat(), V.retrieved or "unknown", CITATION))


def compute(vints, kinds=None, pins=None, committed_vintage_rows=None, existing_revisions=None, kt_expected=None, determinism="pending", s1_frozen=None):
    kinds = KIND_TABLE if kinds is None else kinds
    pins = PIN_TABLE if pins is None else pins
    c = Ctx()
    vints = sorted(vints, key=lambda v: v.key)
    c.vints, c.kinds, c.pins = vints, kinds, pins
    c.V = V = vints[-1]
    c.prevV = vints[-2] if len(vints) > 1 else None
    c.F = F = ingest(V.nodes)
    c.api = V.api
    c.api_probs, c.api_gap = api_total_problems(V.nodes[()], V.api["MMF-MMF_TOT-M"])
    c.total = {d: V.api["MMF-MMF_TOT-M"][d] for d in F.months if d in V.api["MMF-MMF_TOT-M"]}
    c.G, c.cm = group_levels(F, kinds)
    c.vintage = V.key
    c.node_probs = node_problems(V.nodes)
    c.lineage_probs = lineage_problems(V.nodes[()])
    c.measure_probs = measure_identity_problems(c.G)
    c.group_probs = group_sum_problems(c.G)
    c.kt_sha = kind_table_sha(kinds)
    c.kt_expected = KIND_TABLE_SHA256 if kt_expected is None else kt_expected
    c.parent_keys = parent_kind_keys(F)
    c.gate = kind_gate_problems(c.parent_keys, kinds, c.kt_expected)
    c.determinism = determinism
    # tables
    c.lg_rows = levels_group_rows(c.G, F, c.total, c.vintage)
    c.lc_rows = levels_country_rows(F, c.cm, c.G, c.total, c.vintage)
    c.qe = qe_all_rows(c.G, F.months)
    c.qe_rows = qe_row_strings(c.qe, c.vintage)
    c.qs_rows = qe_summary_rows(c.qe, c.G, F.months, c.vintage)
    c.n_value = s1_frozen if s1_frozen is not None else (S1_N_FROZEN if S1_N_FROZEN is not None else s1_noise_n(c.G, F.months))
    c.n_computed = s1_noise_n(c.G, F.months)
    c.s1 = s1_history(c.qe, c.n_value)
    c.parents = parents_rows(F, kinds, V.asof, c.vintage)
    c.cells = {v.key: vintage_cells(v) for v in vints}
    c.revs = all_revisions(vints, c.cells, existing_revisions)
    c.vint_rows = vintages_rows(vints, c.kt_sha)
    c.summary = summary_rows(c.G, F, c.total, vints, c.revs, c.qe, c.s1, c.vintage)
    c.order_probs = vintage_order_problems(vints, committed_vintage_rows)
    c.checks = build_checks(c)
    return c


def basis_rule_problems(qe):
    """C21: no basis other than `calendar` may use a calendar quarter-end month as a neighbour; one-sided rows carry no previous month."""
    probs = []
    for r in qe:
        if r["basis"] == "calendar":
            continue
        nb = [d for d in r["used"] if d != r["month"]]
        if any(d.month in (3, 6, 9, 12) for d in nb):
            probs.append("%s %s %s/%s uses a calendar quarter-end month as a neighbour" % (r["basis"], r["quarter"], r["group"], r["measure"]))
            break
        if r["basis"] == "ca_fiscal" and (r["kind"] != "one_sided" or r["prev"] is not None):
            probs.append("ca_fiscal %s is not one-sided" % r["quarter"])
            break
        if r["basis"] == "jp_march" and r["month"].month != 3:
            probs.append("jp_march row in month %d" % r["month"].month)
            break
    return probs


def share_problems(c):
    """G20: every pct_ value in 0-100 (levels_group and levels_country); ALL_NONUS headline equals the independent sum over countries."""
    probs = []
    for r in c.lg_rows:
        for v in (r[5], r[6]):
            if v != "" and not (0 <= Decimal(v) <= 100):
                probs.append("levels_group %s %s %s: share %s outside 0-100" % (r[0], r[1], r[3], v))
                return probs
    for r in c.lc_rows:
        for v in (r[5], r[6]):
            if v != "" and not (0 <= Decimal(v) <= 100):
                probs.append("levels_country %s %s %s: share %s outside 0-100" % (r[0], r[1], r[3], v))
                return probs
    indep = {}
    for ctry in c.F.cgroups:
        sadd(indep, c.cm[ctry]["headline"]["all"])
    allv = c.G[("ALL_NONUS", "headline", "all")]
    for d in sorted(set(indep) | set(allv)):
        if abs(indep.get(d, Decimal(0)) - allv.get(d, Decimal(0))) > IDENT_TOL:
            probs.append("ALL_NONUS headline %s differs from the sum over countries on %s" % (allv.get(d, Decimal(0)), d))
            break
    return probs


def build_checks(c):
    V, F, G = c.V, c.F, c.G
    pinned = V.key == PIN_VINTAGE
    rows = pin_rows(V, c.prevV, c.pins)
    add = lambda cid, desc, exp, obs, st: rows.append([cid, desc, exp, obs, st])
    root = V.nodes[()]
    api = V.api["MMF-MMF_TOT-M"]
    for cid, ds in (("C01c", "2026-09-30"), ("C01d", "2011-01-31")):
        d = D_(ds)
        s = pin_value(V.nodes, (), None, d)
        t = api.get(d)
        ok = s is not None and t is not None and abs(s - t) <= IDENT_TOL
        add(cid, "sum of the nine root categories equals MMF-MMF_TOT-M on %s" % ds, "within 1.00 USD", "categories %s, API %s" % (s, t), "PASS" if ok else "FAIL")
    add("C01e", "the nine categories equal MMF-MMF_TOT-M in every month", "within 1.00 USD", "largest gap %s USD in %d months" % (c.api_gap.quantize(Decimal("0.01")),
        len(root.dates)), "PASS" if not c.api_probs else "FAIL")
    cnt = category_counts(root)
    add("C07", "nonzero month counts of the nine fund categories (Prime, Prime Institutional, Prime Retail, Government, Government No Fees and Gates, "
        "Government Fees and Gates, Tax Exempt, Tax Exempt Institutional, Tax Exempt Retail)", ",".join(map(str, CAT_EXPECT_COUNTS)), ",".join(map(str, cnt)),
        "PASS" if tuple(cnt) == CAT_EXPECT_COUNTS else ("FAIL" if V.key == PIN_VINTAGE else "WARN"))
    exp_months = months_between(dt.date(2011, 1, 31), V.asof)
    ok8 = root.dates == exp_months and is_month_end(V.asof)
    add("C08", "root months: calendar month-ends from 2011-01-31 to asof, no gaps", "%d months to %s" % (len(exp_months), V.asof),
        "%d months, %s to %s" % (len(root.dates), root.dates[0], root.dates[-1]), "PASS" if ok8 and (len(root.dates) == 189 or not pinned) else "FAIL")
    s = G[("ALL_NONUS", "secured", "all")]
    ffi = V.api["MMF-MMF_RP_wFFI-M"]
    gaps = [(abs(s.get(d, Decimal(0)) - ffi[d]), d) for d in F.months if d in ffi]
    mg = max(gaps) if gaps else (Decimal(0), None)
    last = F.months[-1]
    add("C09", "non-US secured (repo) against MMF-MMF_RP_wFFI-M in every month (gap printed; definitions may differ)", "gap 0",
        "largest gap %s USD on %s; on %s secured %s, API %s" % (mg[0].quantize(Decimal("0.01")), mg[1], last, s.get(last, Decimal(0)), ffi.get(last)),
        "PASS" if mg[0] <= IDENT_TOL else "WARN")
    add("C10", "no 'Aggregated small issuers' child", "none", "%d node(s)" % len(F.small_issuers) if F.small_issuers else "none", "WARN" if F.small_issuers else "PASS")
    fr = G[("FR", "headline", "government")].get(D_("2026-09-30"))
    obs = dstr(usd_to_mn(fr), 1) if fr is not None else "absent"
    add("C11", "levels_group FR / government / headline / 2026-09-30, USD millions", "216102.5", obs, "PASS" if obs == "216102.5" else ("FAIL" if pinned else "WARN"))
    add("C12", "a second build leaves every sha256 unchanged", "identical", c.determinism, "PASS" if c.determinism == "identical" else "FAIL")
    unk = unknown_report(F)
    add("C13", "no unknown label (categories, regions, countries, sectors, asset types)", "none", unknown_text(F), "FAIL" if unk else "PASS")
    rel = sorted({l for l, _w in F.relayed})
    add("C13b", "relayed asset-type labels seen (mapped as listed)", "none", ", ".join(rel) if rel else "none", "WARN" if rel else "PASS")
    ff = G[("MEMO_FICC", "headline", "all")]
    fi = V.api["MMF-MMF_RP_wFICC-M"]
    fg = [(abs(ff.get(d, Decimal(0)) - fi[d]), d) for d in F.months if d in fi]
    fm = max(fg) if fg else (Decimal(0), None)
    add("C14", "MEMO_FICC against MMF-MMF_RP_wFICC-M in every month (gap printed)", "gap 0",
        "largest gap %s USD on %s; on %s MEMO_FICC %s, API %s" % (fm[0].quantize(Decimal("0.01")), fm[1], last, ff.get(last, Decimal(0)), fi.get(last)),
        "PASS" if fm[0] <= IDENT_TOL else "WARN")
    add("C15", "the kind table hashes to KIND_TABLE_SHA256 and every parent has a kind (review date in SOURCES.md, Builder decisions)",
        c.kt_expected or "(not set)", c.kt_sha + ("" if not c.gate else "; " + "; ".join(c.gate)), "PASS" if not c.gate else "FAIL")
    add("C16", "secured + unsecured + abcp + misc + unallocated = headline, every group, month and lineage", "within 1.00 USD",
        "no breach" if not c.measure_probs else c.measure_probs[0], "PASS" if not c.measure_probs else "FAIL")
    add("C17", "node identities: children sum to the parent's value on every node and month", "within 1.00 USD",
        "%d nodes, no breach" % len(V.nodes) if not c.node_probs else "%d breach(es), first: %s" % (len(c.node_probs), c.node_probs[0]), "PASS" if not c.node_probs else "FAIL")
    add("C18", "category lineages: old and new names never both nonzero in one month", "none", "none" if not c.lineage_probs else c.lineage_probs[0],
        "PASS" if not c.lineage_probs else "FAIL")
    sp = c.group_probs or share_problems(c)
    add("C19", "the nine groups sum to ALL_NONUS in every month, measure and lineage; ALL_NONUS equals the sum over countries; every share is within 0-100", "none",
        "none" if not sp else sp[0], "PASS" if not sp else "FAIL")
    add("C20", "vintages: asof never earlier than the previous vintage's; the same key never has a different manifest", "none",
        "none" if not c.order_probs else c.order_probs[0], "PASS" if not c.order_probs else "FAIL")
    bp = basis_rule_problems(c.qe)
    add("C21", "no basis other than calendar uses a calendar quarter-end month as a neighbour; ca_fiscal is one-sided; jp_march is March", "none",
        "none" if not bp else bp[0], "PASS" if not bp else "FAIL")
    hits, n, got = c.s1
    nv = c.n_value
    add("S1", "historical hit rate of the pre-registered statement (chg_in_pct <= -N on the 9 year-ends 2017-2025, ALL_NONUS secured); N is the clean-month sd, "
        "frozen at the first build", "at least 8 of 9",
        "%d of %d with N = %s%s" % (hits, n, dstr(nv, 4), "" if S1_N_FROZEN is not None else " (computed by this build, not yet frozen in the script)"),
        "PASS" if n == 9 and hits >= 8 else "WARN")
    rows.sort(key=lambda r: r[0])
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# README.md (generated; G15 scans it) and SOURCES.md
# ------------------------------------------------------------------------------------------------------------------------
GROUP_WORDS = {
    "EA": "euro area (2026 membership applied to every date)", "FR": "France (also inside EA)", "JP": "Japan", "CA": "Canada", "UK": "United Kingdom",
    "CH": "Switzerland", "NORDIC": "Sweden, Norway and Denmark", "AUNZ": "Australia and New Zealand (every country the OFR lists under its region Australia)",
    "OTHER_ASIA": "every other country the OFR lists under Asia", "OTHER": "every other non-US country", "ALL_NONUS": "the sum of the nine groups EA, JP, CA, UK, CH, "
    "NORDIC, AUNZ, OTHER_ASIA and OTHER (FR is inside EA and is not added again)", "MEMO_FICC": "repo cleared through FICC, which the OFR maps to the USA; "
    "outside every non-US total"}


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def bn_text(usd):
    """USD -> billions of dollars, one decimal, thousands separators; 'n/a' for None."""
    if usd is None:
        return "n/a"
    return "{:,.1f}".format(qfix(Decimal(usd) / Decimal(1_000_000_000), 1))


def long_date(d):
    return "%d %s %d" % (d.day, MONTHS_LONG[d.month - 1], d.year)


def qs_lookup(c, basis, window, group, measure):
    for r in c.qs_rows:
        if r[0] == basis and r[2] == window and r[3] == group and r[4] == measure:
            return r
    return None


def fmt_pm(mean, se):
    return "n/a" if mean in (None, "") else "%s (se %s)" % (mean, se or "n/a")


def readme_levels_tables(c):
    G, F = c.G, c.F
    ends = feb_endpoints(F.months)
    cols = ["ALL_NONUS", "EA", "FR", "JP", "CA", "UK", "CH", "NORDIC", "AUNZ", "OTHER_ASIA", "OTHER", "MEMO_FICC"]
    t1 = [[d.isoformat()] + [bn_text(G[(g, "headline", "all")].get(d, Decimal(0))) for g in cols] for d in ends]
    t2 = []
    for d in ends:
        tot = c.total.get(d)
        sh = pct(G[("ALL_NONUS", "headline", "all")].get(d, Decimal(0)), tot)
        t2.append([d.isoformat()] + [bn_text(G[("ALL_NONUS", m, "all")].get(d, Decimal(0))) for m in MEASURES] + ["n/a" if sh is None else dstr(sh, 3), bn_text(tot)])
    return (md_table(["Month-end"] + cols, t1),
            md_table(["Month-end"] + list(MEASURES) + ["headline, percent of all US money funds", "all US money funds"], t2))


def readme_changes_table(c):
    G, F = c.G, c.F
    months = set(F.months)
    ends = [d for d in Q2_ENDPOINTS if d in months]
    if len(ends) < 2:
        return "The 2024-2026 endpoints are not all in this vintage."
    rows = []
    for g, m in (("ALL_NONUS", "headline"), ("ALL_NONUS", "secured"), ("ALL_NONUS", "unsecured"), ("EA", "headline"), ("FR", "headline"), ("JP", "headline"), ("CA", "headline"),
                 ("UK", "headline"), ("CH", "headline"), ("NORDIC", "headline"), ("AUNZ", "headline"), ("OTHER_ASIA", "headline"), ("OTHER", "headline"), ("MEMO_FICC", "headline")):
        s = G[(g, m, "all")]
        lev = [bn_text(s.get(d, Decimal(0))) for d in ends]
        ch = ln_pct(s.get(ends[-1], Decimal(0)), s.get(ends[0], Decimal(0)))
        pa, pb = pct(s.get(ends[0], Decimal(0)), c.total.get(ends[0])), pct(s.get(ends[-1], Decimal(0)), c.total.get(ends[-1]))
        rows.append([g, m] + lev + ["n/a" if ch is None else dstr(ch, 1), "n/a" if pa is None or pb is None else dstr(pb - pa, 3)])
    head = ["Group", "Measure"] + [d.isoformat() for d in ends] + ["percent change, first to last", "change in share of all US money funds, points"]
    return md_table(head, rows)


def readme_quarter_table(c):
    rows = []
    for g, m in (("ALL_NONUS", "headline"), ("ALL_NONUS", "bank_only"), ("ALL_NONUS", "secured"), ("ALL_NONUS", "unsecured")) + tuple((g, "secured") for g in GROUP_ORDER[:10]):
        r = qs_lookup(c, "calendar", W_POST, g, m)
        if r:
            rows.append([g, m, r[5], fmt_pm(r[7], r[11]), r[8], r[12], r[14], "" if r[15] in ("", "0") or r[16] == "" else "%s: %s (se %s)" % (r[15], r[16], r[17] or "n/a")])
    return md_table(["Group", "Measure", "Quarters (n)", "Mean fall below neighbours, percent (standard error)", "Median", "Noise reference, percent", "Pattern",
                     "Minus AUNZ: n, mean (se)"], rows)


def readme_japan_canada(c):
    rows = []
    for basis in ("jp_march", "jp_other", "ca_fiscal"):
        g = "CA" if basis == "ca_fiscal" else "JP"
        for m in ("headline", "secured"):
            r = qs_lookup(c, basis, W_POST, g, m)
            if r:
                rows.append([basis, g, m, r[1], r[5], fmt_pm(r[7], r[11]), r[12], r[14]])
    return md_table(["Basis", "Group", "Measure", "Statistic", "Quarters (n)", "Mean fall below neighbours, percent (standard error)", "Noise reference, percent", "Pattern"], rows)


CGFS_QUOTES = (
    ("p 20", "now obtain less funding from US MMFs"), ("p 35", "some non-US banks significantly reduce their matched book repo activity at quarter-ends"),
    ("p 67", "mainly via overnight repos from US MMFs"), ("pp 67-68", "have become the most important repo counterparties to French banks"),
    ("p 73", "are not subject to the quarter- or year-end balance sheet constraints"), ("p 27", "has shortened considerably"))


def readme_cgfs_table(c):
    G = c.G
    f16, f26 = D_("2016-02-29"), D_("2026-02-28")
    have = f16 in c.F.months and f26 in c.F.months
    allsh = lambda d: dstr(pct(G[("ALL_NONUS", "headline", "all")].get(d, Decimal(0)), c.total.get(d)), 3)
    frs = lambda d: bn_text(G[("FR", "secured", "all")].get(d, Decimal(0)))
    prim = qs_lookup(c, "calendar", W_POST, "ALL_NONUS", "secured")
    aunz = qs_lookup(c, "calendar", W_POST, "AUNZ", "secured")
    rows = [
        ["Non-US banks \"%s\" (%s), after the 2016 reform cut prime funds by about 1 trillion dollars (p 20)." % (CGFS_QUOTES[0][1], CGFS_QUOTES[0][0]),
         ("ALL_NONUS headline: %s billion dollars on 2016-02-29 and %s billion on 2026-02-28; share of all US money funds %s percent and %s percent."
          % (bn_text(G[("ALL_NONUS", "headline", "all")].get(f16, Decimal(0))), bn_text(G[("ALL_NONUS", "headline", "all")].get(f26, Decimal(0))), allsh(f16), allsh(f26)))
         if have else "The 2016-02 and 2026-02 endpoints are not both in this vintage."],
        ["French banks raise dollars \"%s\" (%s) and US money funds \"%s\" (%s)." % (CGFS_QUOTES[2][1], CGFS_QUOTES[2][0], CGFS_QUOTES[3][1], CGFS_QUOTES[3][0]),
         ("FR secured (repo): %s billion dollars on 2016-02-29 and %s billion on 2026-02-28. Repo cleared through FICC is in MEMO_FICC, not in FR." % (frs(f16), frs(f26)))
         if have else "n/a"],
        ["\"%s\" (%s); no country is named." % (CGFS_QUOTES[1][1], CGFS_QUOTES[1][0]),
         ("Primary row, ALL_NONUS secured, calendar quarter-ends, post_reform: n %s, mean fall below the neighbouring months %s percent (standard error %s)."
          % (prim[5], prim[7], prim[11])) if prim else "n/a"],
        ["Australian banks \"%s\" (%s)." % (CGFS_QUOTES[4][1], CGFS_QUOTES[4][0]),
         ("AUNZ secured, same basis and window: n %s, mean %s percent (standard error %s). The paired differences against AUNZ are in qe_summary.csv."
          % (aunz[5], aunz[7], aunz[11])) if aunz else "n/a"],
        ["Tenor \"%s\" (%s)." % (CGFS_QUOTES[5][1], CGFS_QUOTES[5][0]), "Not measured here: the OFR monitor has no maturity by country."]]
    return md_table(["What CGFS Paper 65 says (BIS, June 2020)", "What this table holds"], rows)


COLUMN_DICT = (
    ("levels_country.csv", "Month-end holdings by the OFR's parent country and instrument, all fund types together, non-US countries only, nonzero cells; one `total` row "
     "per country and month.",
     (("month_end", "calendar month-end"), ("country", "the OFR's country label for the ultimate parent"), ("country_group", "the group of section above (France is shown "
      "under EA)"), ("instrument_group", "repo_treasury, repo_agency, repo_other, cd, time_deposit, fin_cp, other_note, abcp, misc, unallocated, or total"),
      ("usd_mn", "millions of US dollars"), ("pct_of_mmf_total", "percent of the total investments of all US money funds that month-end"),
      ("pct_of_nonus_fi", "percent of the ALL_NONUS headline that month-end"), ("vintage", "the OFR release the row comes from (its updated date)"))),
    ("levels_group.csv", "Month-end holdings by country group, fund type and measure.",
     (("month_end", "calendar month-end"), ("country_group", "EA, FR, JP, CA, UK, CH, NORDIC, AUNZ, OTHER_ASIA, OTHER, ALL_NONUS or MEMO_FICC"),
      ("fund_lineage", "all, prime, government or tax_exempt (each lineage joins the OFR's category names before and after 2016 and 2024)"),
      ("measure", "headline (all instruments), bank_only (parents classed as banks), secured (repo), unsecured (certificates of deposit, time deposits, financial "
       "commercial paper, other notes), abcp, misc"), ("usd_mn", "millions of US dollars"), ("pct_of_mmf_total", "percent of all US money funds"),
      ("pct_of_lineage_total", "percent of the same fund lineage's total"), ("vintage", "as above"))),
    ("quarter_ends.csv", "One row per quarter-end month, group, measure and basis.",
     (("quarter", "calendar quarter holding the month"), ("qe_month", "the month-end examined"), ("basis", "calendar, jp_march, jp_other or ca_fiscal"),
      ("stat_kind", "two_sided, or one_sided for ca_fiscal"), ("country_group", "as above"), ("measure", "headline, bank_only, secured or unsecured"),
      ("level_prev_usd_mn, level_qe_usd_mn, level_next_usd_mn", "levels at the previous, examined and next month-end, millions of dollars"),
      ("chg_in_pct, chg_out_pct", "percent change into and out of the examined month-end (100 times the natural log of the ratio)"),
      ("below_nbrs_pct", "how far the examined month-end falls below the neighbouring months, percent; negative means lower than the neighbours"),
      ("below_nbrs_usd_mn", "the same in millions of dollars, level minus the average of the neighbours"), ("window", "post_reform, transition, pre_reform or "
       "after_freeze"), ("frozen_set", "yes for quarters up to 2026Q2"), ("primary", "yes on the single primary row set"), ("blind", "yes only for rows whose answer "
       "was not seen before the build"), ("vintage", "as above"))),
    ("qe_summary.csv", "The summary of quarter_ends.csv per basis, window, group and measure.",
     (("n_quarters, n_blank", "quarters with and without a computed value"), ("mean_below_nbrs_pct, median_below_nbrs_pct, n_negative, sd_below_nbrs_pct, "
       "se_mean_below_nbrs_pct", "mean, median, count of negative values, sample standard deviation and standard error of the mean"),
      ("noise_clean_sd_pct, noise_n", "the noise reference and the number of changes it uses"), ("pattern", "lower, higher, neither or insufficient: a description of "
       "the sample"), ("paired_n_vs_aunz, paired_mean_diff_vs_aunz_pct, paired_se_vs_aunz_pct", "the paired difference against AUNZ over quarters where both are "
       "computed: n, mean, standard error"), ("primary, blind, vintage", "as above"))),
    ("parents.csv", "The OFR's non-US financial-institution parents, with the builder's classification.",
     (("parent, country, country_group", "the OFR's parent name, country label and group"), ("kind", "bank, insurer or other_fin"), ("first_month, last_month",
      "first and last month-end with a nonzero holding"), ("usd_mn_latest", "millions of dollars at the latest month-end"), ("vintage", "as above"))),
    ("summary.csv", "Levels, shares and changes at the named endpoints, revision counts and the hit rate. One statistic per row.",
     (("question, window, country_group, measure, from_month, to_month", "what the row answers"), ("statistic, value, unit", "the statistic, its value and unit"),
      ("primary, blind", "as above"))),
    ("revisions.csv", "Cells whose value differs between two adjacent cached OFR releases (rewritten on every build).",
     (("vintage_prev, vintage_new, month_end, country, instrument_group", "the pair and the cell"), ("usd_mn_prev, usd_mn_new, change_usd_mn", "values in millions of dollars"))),
    ("vintages.csv", "One row per cached OFR release.",
     (("vintage, ofr_updated, ofr_asof", "the release key and the OFR's own updated and as-of dates"), ("requests, nodes", "requests made and chart files held"),
      ("manifest_sha256", "hash of the list of files held"), ("api_total_check", "result of the comparison with the OFR's total series"),
      ("kind_table_sha256", "hash of the classification table"))),
    ("checks.csv", "The checks run by the build and their results.", (("check_id, description, expected, observed, status", "PASS, WARN or FAIL"),)),
    ("fetch_log.csv", "Every request the fetch made.", (("utc_time, host, path, status, bytes, sha256", "when, to which OFR host, for which file, with what result"),)))


def render_readme(c):
    V, F = c.V, c.F
    t1, t2 = readme_levels_tables(c)
    prim = qs_lookup(c, "calendar", W_POST, "ALL_NONUS", "secured")
    unal = any(v != 0 for l in c.G[("ALL_NONUS", "unallocated", "all")].values() for v in [l])
    L = []
    w = L.append
    w("# US money market funds' claims on non-US financial institutions, by parent country and instrument\n")
    w(README_S1 + " " + README_S2 + "\n")
    w(README_S3 + " The months run from 31 January 2011 to %s; this vintage is the OFR release updated %s.\n" % (long_date(V.asof), long_date(V.updated)))
    w("## Country basis\n")
    w("The country is the home country of the ultimate parent, not the place where a branch sits: a US branch of a Japanese bank counts as Japan. The OFR takes it from "
      "the address of the ultimate parent's headquarters or, if that differs, the country where its sources suggest the parent has its most substantial operations. "
      "It is the only basis the OFR offers, and it matches how the BIS paper below discusses bank funding; a residence basis is not available from this source.\n")
    w("Repo cleared through the Fixed Income Clearing Corporation (FICC) is reported with FICC as the counterparty, and the OFR maps FICC to the United States, so a "
      "non-US bank's cleared repo does not appear under its own country. The table carries FICC as a separate memo line, MEMO_FICC, outside every non-US total. "
      + README_FICC + "\n")
    w("The OFR's parent mapping is imperfect: for example `Natexis + Natixis` and `Groupe BPCE` are separate parents, and so are two Northwestern Mutual entries. "
      "This table takes the OFR's parents and countries as published and never re-maps them. The country groups are:\n")
    for g in GROUP_ORDER:
        w("- **%s**: %s" % (g, GROUP_WORDS[g]))
    w("")
    w("## What is counted\n")
    w("Only the OFR's `Financial Institution` sector of non-US countries, summed over prime, government and tax-exempt funds (the OFR renamed its fund categories in "
      "April 2016 and again in 2024, and the build joins the old and new names). Instruments: repo (by collateral: Treasury, government agency, other), unsecured "
      "(certificates of deposit, time deposits, financial commercial paper, other notes), asset-backed commercial paper (ABCP, which the OFR assigns to the sponsoring "
      "bank's parent and which stays in the total) and other (non-financial commercial paper, Treasury and agency debt%s). Repo + unsecured + ABCP + other = total. %s\n"
      % (", and any amount the OFR does not allocate" if unal else "", DENIAL))
    w("The measure `bank_only` counts only parents the builder classed as banks (deposit-taking institutions and bank holding companies); broker-dealers are classed "
      "`other_fin` and insurers `insurer`, and both are left out of `bank_only`. The classification is in `parents.csv`.\n")
    w("## Levels and shares\n")
    w("Billions of US dollars at month-end, all fund types, by country group. The endpoints are every February from 2011 to 2026 and 31 August 2026: all are "
      "mid-quarter months, because a quarter-end month can be unusually low or high, and an endpoint there would put a quarter-end move into a multi-year change.\n")
    w(t1 + "\n")
    w("All US money funds' claims on non-US financial institutions (ALL_NONUS) by measure, with the share of all US money funds' investments:\n")
    w(t2 + "\n")
    w("## Change from 2024 to 2026\n")
    w("Month-end levels in billions of dollars at the first and last of the 2024-2026 endpoints, the percent change between them (100 times the natural log of the "
      "ratio), and the change in the share of all US money funds' investments in percentage points. The in-between endpoints are in `summary.csv`.\n")
    w(readme_changes_table(c) + "\n")
    w("## Quarter-ends\n")
    w("The question is how far a quarter-end month-end falls below the neighbouring month-ends, in percent. For a group's level L at the quarter-end month q, with q-1 "
      "and q+1 the month-ends on either side, the fall below the neighbouring months is 100 x [ln L(q) - 1/2 (ln L(q-1) + ln L(q+1))], half of the percent change "
      "into q minus the percent change out of q. A negative number means q is lower than the average of its neighbours. For Canadian banks' fiscal quarter-ends "
      "(31 January, 30 April, 31 July, 31 October) the previous month-end is a calendar quarter-end, so only the next month is used: the fall is minus the percent "
      "change from the fiscal month-end to the next one. No basis other than the calendar one uses a calendar quarter-end month as a neighbour.\n")
    w("**Noise reference.** The standard deviation of the month-on-month percent changes from January to February, April to May, July to August and October to "
      "November (the only changes that touch no calendar quarter-end month) in the same window, divided by the square root of 2 for the two-sided rows. "
      "**Comparison with Australia and New Zealand.** For each other group, the paired difference between its fall below the neighbouring months and the AUNZ "
      "fall in the same quarters, with n, mean and standard error. **Windows.** `post_reform` is the 38 quarters 2017Q1 to 2026Q2 (after the 14 October 2016 "
      "prime-fund reform), frozen; `pre_reform` is 2011Q1 to 2016Q2 (22 quarters); the third and fourth quarters of 2016 are written as rows but in no summary; 2026Q3 onward is "
      "`after_freeze`, and a quarter whose next month-end is not yet published carries only the change into it.\n")
    if prim:
        w("**The single primary row** is repo (`secured`) held by ALL_NONUS at calendar quarter-ends in the `post_reform` window: n = %s, mean fall below the "
          "neighbouring months %s percent (standard error %s, median %s), noise reference %s percent, pattern `%s`. The prediction fixed before the build was a mean "
          "fall of 5 percent or more. **Every other row, group, basis and window is exploratory.** `pattern` is `lower` when the mean is at least twice its standard "
          "error below zero, `higher` when at least twice above, `neither` otherwise and `insufficient` below 8 quarters; it describes the sample and says nothing about "
          "why.\n" % (prim[5], prim[7], prim[11], prim[8], prim[12], prim[14]))
    w("Calendar basis, `post_reform` window (exploratory except the first secured row):\n")
    w(readme_quarter_table(c) + "\n")
    w("Japan's fiscal year ends in March (n = 10 March quarter-ends in the window, a small number), set beside its other quarter-ends (n = 28); Canada's fiscal "
      "quarter-ends use the next month only, for the reason above:\n")
    w(readme_japan_canada(c) + "\n")
    w("## Set beside the BIS CGFS Paper 65\n")
    w("The paper's words are quoted briefly with their printed page numbers; the right-hand column is descriptive and carries no verdict.\n")
    w(readme_cgfs_table(c) + "\n")
    w("## Tenor is not available\n")
    w("The OFR monitor has no maturity by country, so nothing here says how long the repo or paper runs. The SEC's N-MFP data sets would supply it and would be a "
      "separate piece of work.\n")
    w("## Revisions and vintages\n")
    w("Each OFR release revises the complete series, and the monitor's files are overwritten in place. Each complete crawl is kept as a vintage (`vintages.csv`), "
      "and `revisions.csv` is rewritten on every build from all adjacent pairs of cached vintages. Vintages held: %d (%s). Cells changed in the latest pair: %s.\n"
      % (len(c.vints), ", ".join(v.key for v in c.vints), str(len([r for r in c.revs if r[1] == V.key])) if len(c.vints) > 1 else "none yet, only one vintage"))
    w("## Columns\n")
    for name, desc, cols in COLUMN_DICT:
        w("**%s**: %s" % (name, desc))
        for cname, cdesc in cols:
            w("- `%s`: %s" % (cname, cdesc))
        w("")
    w("## Source and copyright\n")
    w("%s The OFR's legal notice says works of its federal employees carry no copyright and asks for credit; the OFR's own notes say its parent and country mapping "
      "draws on regulatory filings, company disclosures and commercial data, so the raw chart files are not republished here and only derived statistics are. "
      "Build script: `bin/mmf_nonus_banks.py`. Provenance, labels, builder decisions and the request record are in `SOURCES.md`.\n" % CITATION)
    text = "\n".join(L).rstrip("\n") + "\n"
    probs = wording_problems("README.md", text)
    if probs:
        raise DataError("the README the build wrote would hold banned wording: %s" % probs[0])
    for s in (README_S1, README_S2, README_S3, README_FICC):
        if s not in text:
            raise DataError("a required README sentence is missing")
    return text


# ---- SOURCES.md ----------------------------------------------------------------------------------------------------------
REQUESTS_BY_AUTHOR = (
    "- Spec author, 25 Oct 2026, 14:06-14:25 UTC, the CLAUDE.md non-SEC User-Agent, one request per URL: 32 requests, 31 returning 200 and one 403.",
    "- `www.financialresearch.gov` (27 requests): `/money-market-funds/`, its three chart pages, `/robots.txt`, `/about/policies/`, `/legal-notices/`, "
    "`/short-term-funding-monitor/datasets/mmf/`, three `/assets/js/mmf/` scripts, `asof.json`, `updated.json` and 13 node files (two of them the encoding tests): all 200.",
    "- `/money-market-funds/data/mmf_data.zip`: **403 `AccessDenied`** (CloudFront/S3, 111 bytes), not retried. It is never requested by this build.",
    "- `data.financialresearch.gov` (3 requests): the mnemonic list, `MMF-MMF_TOT-M`, `MMF-MMF_RP_wFFI-M`: all 200.",
    "- `www.bis.org`: the CGFS Paper 65 PDF, 200. `catalog.data.gov/dataset/form-n-mfp-data-sets`: 200.")

DISCLOSURE = ("What was seen of the answer before any build: the spec author saw the pinned node levels and, from the OFR API, the aggregate \"repo with foreign "
              "financial institutions\" series (MMF-MMF_RP_wFFI-M), including its 2011-16 noise and its 2017Q1-2026Q2 dip spread. The second reviewer computed that "
              "aggregate's calendar and Canadian-fiscal dips and the history of statement S1 on it (9 of 9). No country-group statistic had been computed. The `blind` "
              "marks follow from this: every ALL_NONUS `secured` and `headline` row is marked not blind.")

SPEC_REF = "_research/2026-10-25-MMF-NonUS-Banks-Spec.md (committed at da6f335, supervisor rulings rounds 1 to 4)"


def builder_decisions(c):
    nv, comp = c.n_value, c.n_computed
    frozen = ("frozen in the script (S1_N_FROZEN) at %s" % dstr(S1_N_FROZEN, 4)) if S1_N_FROZEN is not None else (
        "computed by this build as %s and not yet frozen in the script; the builder freezes it after the first build" % dstr(comp, 4))
    kt = sorted(c.kinds.items(), key=lambda kv: (kv[0][0], kv[0][1]))
    new_lab = ["asset type %s -> %s (%s)" % (k, v[0], v[1]) for k, v in sorted(BUILDER_ITYPE_MAP.items())] + \
              ["region %s (%s)" % (k, v) for k, v in sorted(BUILDER_REGIONS.items())] + \
              ["sector %s (%s)" % (k, v) for k, v in sorted(BUILDER_SECTORS.items())] + \
              ["country %s (%s)" % (k, v) for k, v in sorted(BUILDER_COUNTRIES.items())]
    items = [
        "**Crawl set (reading of 2.3).** The frontier is one function, `needed()`, used by `fetch` and by `build`: the root; each category with a nonzero month; each region "
        "with a nonzero month; each country with a nonzero month, USA included (its file lists the sectors); the `Financial Institution` file of every non-US country "
        "with a nonzero financial-institution month; the asset-type file of every non-US parent with a nonzero month except a child named exactly "
        "\"Aggregated small issuers\"; and, for FICC, the USA `Financial Institution` file of a category only where the chain category, region, USA, "
        "Financial Institution is nonzero in the files already read (so no file the OFR may not serve is requested). The region `Supranational` is fetched as a "
        "region file but its countries are not drilled (it is outside every total). No US parent and no non-financial sector is drilled.",
        "**Latches.** Any STOP file in the cache stops the whole fetch before a request, not only that source's: the strict reading. The budget counts every request of the "
        "vintage across resumed runs, both `updated.json` fetches included; the 3,001st attempt writes `STOP_budget`.",
        "**Slices.** `fetch --max-requests N --max-seconds S` ends a run in an orderly way (exit 3) so the crawl fits a tool timeout; the next run resumes from the manifest. A "
        "socket fault is logged with status `socket_fault`, nothing is latched (exit 4). Exit codes: 0 complete, 2 STOP or release changed or data error, 3 slice ended, "
        "4 socket fault, 5 refused.",
        "**Cache and log layout.** Each vintage folder holds its files (named by the sha256 of the URL path), `manifest.csv`, `requests.txt` and its own `fetch_log.csv`; requests "
        "outside any vintage (an `updated.json` read when the vintage was already complete, a removed partial crawl) go to `fetch_log_other.csv`. The committed "
        "`fetch_log.csv` is the concatenation of all of them. The retrieval date in each `# source:` line is the latest date in the vintage's own log. "
        "`manifest_sha256` is the sha256 of the manifest lines sorted by URL path, so it does not depend on the order files landed.",
        "**Headline and unallocated.** The headline is the `Financial Institution` series of the non-US country's own file; the instrument groups come from the parent "
        "files; `unallocated` is the \"Aggregated small issuers\" child. C16 compares the two routes, so it is not an identity by construction.",
        "**Stable pins and revisions.** A stable pin that differs from the spec's value WARNs if the same cell differs between this vintage and the previous complete "
        "vintage (a revision), else FAILs; the comparison is made on the node cell itself because `revisions.csv` holds country-level cells, not node cells. A recent "
        "pin FAILs on vintage 2026-10-15 and WARNs on later ones. C07 follows the recent-pin rule.",
        "**Quarter-end implementation.** (a) AUNZ rows are also written on the jp_march, jp_other and ca_fiscal bases so that the paired difference is computed on the "
        "same basis and months from rows in the file. (b) `qe_summary.csv` covers the windows `post_reform` and `pre_reform`; `transition` is in no summary (F8) and "
        "`after_freeze` has no computed fall. (c) When a standard error is zero and the mean is zero, `pattern` is `neither`. (d) `frozen_set` is `yes` for quarters up to "
        "2026Q2 (all windows but `after_freeze`). (e) `quarter_ends.csv` carries the four measures of Q3 (headline, bank_only, secured, unsecured); MEMO_FICC has "
        "headline only. (f) The literal `blind` rule marks any row containing a 2026-06 or later month-end `no`, so every calendar and jp_other summary whose window includes 2026Q2 is "
        "`no`. (g) The noise reference of a basis row is that of the group and window (it does not depend on the basis's months).",
        "**summary.csv.** Q1 and Q2 are for fund lineage `all`: the grammar has no lineage column, and `levels_group.csv` holds every lineage in every month. For lineage "
        "`all`, `pct_of_lineage_total` equals `pct_of_mmf_total`. Q6 rows carry the two vintage dates in `from_month` and `to_month`; the month and country of the "
        "largest change are found in `revisions.csv`. Q7 is the hit rate as a share of the 9 year-ends, 2017-2025 (the count is in `checks.csv`, row S1).",
        "**levels_group.csv** holds every group, lineage, measure and month, zeros included, so that the nine-groups-sum-to-ALL_NONUS test sees every cell.",
        "**Extra checks.** `checks.csv` also holds C01c to C01e (the API comparison), C13b, C17 (node identities), C18 (category lineages), C19 (nine groups, shares), "
        "C20 (vintage order), C21 (the neighbour rule) and S1. Pin ids carry letters.",
        "**Kind table.** Keyed by (parent, country); the sha256 is taken over the lines `parent|country|kind\\n`. %d parents are "
        "classified; the table and its review date follow. Reviewed by the supervisor: %s. `KIND_TABLE_SHA256` in the script: `%s`; the table in this build hashes to `%s`."
        % (len(kt), "25 Oct 2026", c.kt_expected or "(not set)", c.kt_sha),
        "**Labels added after the first vintage (O-10, round 4).** %s" % ("; ".join(new_lab) if new_lab else "none."),
        "**Supervisor rulings after stage 1 (25 Oct 2026), applied.** (1) Kind rule: every public development, agency or export-credit lender is `other_fin`, whether or not it "
        "holds a banking licence, because it takes no deposits from the public (Bank Nederlandse Gemeenten, Nederlandse Waterschapbank, NRW.Bank, Oesterreicheische "
        "Kontrollbank, KfW, Kommunalbanken, Japan Finance Corp, Eksportfinans, Swedish Export Finance). Macquarie (its group includes the deposit-taking Macquarie Bank), "
        "Natexis + Natixis and Sumitomo Trust stay `bank`; Nomura, Daiwa, the asset-backed commercial paper conduits (Albion, Northcross, Zephyr) and Suncorp stay `other_fin`. "
        "Every judgement call is marked in the Note column of the kind table below. (2) The exact serialization hashed for `KIND_TABLE_SHA256`: one line per classified parent, "
        "`parent|country|kind` followed by one line feed, UTF-8, the rows sorted by (parent, country) in Unicode code-point order, no header and no final blank line; the "
        "sha256 of that byte string. (3) The unknown labels were accepted and mapped as listed under \"Labels added\" (by region: Africa, the 14 countries, the USA sectors "
        "Municipal and Other; the lower-case \"Supra-National debt\" asset type to `misc`). (4) The six readings of this list (the crawl set, the whole-fetch latch, the pin "
        "revision test, summary.csv for lineage `all`, the literal blind rule, AUNZ rows on every basis) were accepted.",
        "**Edits to the script after the first vintage was fetched (25 Oct 2026, before any `build`).** (a) The builder-added labels above and the kind table (the report of "
        "`kinds` was the first sight of them). (b) The spelling variant \"...Supra-National debt\" of a relayed asset-type label, mapped to `misc` as the spec lists the "
        "label and flagged by C13b. (c) A faster number-formatting routine (`qfix`, `dstr`) with identical output, re-proved by the selftest. (d) `S1_N_FROZEN` set to the first build's value, 6.215782929260888, as spec 4.5 requires (old value `None`; the build had printed N = 6.2158, the spec author's proxy 6.22). No rule, threshold, window or "
        "spec label was changed. Before the fetch: `parse_node` was made to turn any malformed-body error into a content failure (a STOP latch) rather than an "
        "exception.",
        "**S1.** N, the clean-month sd of ALL_NONUS `secured` in `post_reform` (before dividing by the square root of 2), is %s. Historical hit rate: %d of %d year-ends."
        % (frozen, c.s1[0], c.s1[1]),
        "**Honesty note on S1 (spec 4.5).** At 9 of 9 on the proxy a HELD is near-certain, so S1 checks that a known pattern persists and carries little information.",
    ]
    return items


def render_sources(c, extra_decisions=()):
    V = c.V
    L = []
    w = L.append
    w("# Sources, access record and builder decisions: US money funds' claims on non-US financial institutions\n")
    w("Specification: `%s`. Build script: `bin/mmf_nonus_banks.py`. Vintage: OFR release updated %s, data as of %s, retrieved %s.\n" % (SPEC_REF, V.updated.isoformat(),
      V.asof.isoformat(), V.retrieved or "unknown"))
    w("## 1. Source and licence\n")
    w("Office of Financial Research, OFR U.S. Money Market Fund Monitor, built from SEC Form N-MFP, refreshed monthly: https://www.financialresearch.gov/money-market-funds/ . "
      "The data are read from the monitor's chart files (`/money-market-funds/data/credit_risks_country/.../data.json`), crawled politely under the principal's ruling "
      "E-027 (requests at least 2 s apart, the neutral User-Agent, a STOP latch on any 403, 429 or other non-200, no retry), and from four series of the OFR API "
      "(`MMF-MMF_TOT-M`, `MMF-MMF_RP_wFFI-M`, `MMF-MMF_RP_wFICC-M`, `MMF-MMF_RP_wDFI-M`). The complete-dataset zip is never requested.\n")
    w("OFR Legal Notices (observed 25 Oct 2026): \"No copyright may be claimed for any work on this website that was created by a federal employee in the course of his "
      "or her duties. However, credit is requested\". The monitor footnote says the parent and country mapping draws on \"regulatory filings, company disclosures and "
      "commercial data\", so raw JSON stays in the gitignored cache and committed files are derived aggregates and the OFR's parent names with countries. Citation: "
      + CITATION + " `robots.txt` (observed) does not disallow `/money-market-funds/` or `/assets/`.\n")
    w("## 2. Requests\n")
    for r in REQUESTS_BY_AUTHOR:
        w(r)
    w("- This build's crawl: %d requests for vintage %s (budget %d), %d chart files plus `asof.json`, `updated.json` and the four API series; the full record is "
      "`fetch_log.csv`.\n" % (V.requests, V.key, BUDGET, len(V.nodes)))
    w("## 3. Drill levels and literal maps\n")
    w("Drill levels (monitor metadata): Category (MFS002), Region (MFS019), Country (MFS009), Sector (MFS006), Credit, i.e. ultimate parent (MFS008), Asset Type (MFS005). "
      "Measure MFS015, assets under management, USD. A path segment is the child's display name, lower-cased, whitespace replaced by `_`, percent-encoded as "
      "JavaScript's `encodeURIComponent`.\n")
    w("- Fund categories and lineages: " + "; ".join("%s = %s" % (k, v) for k, v in CATEGORIES))
    w("- Regions in the literal table: " + ", ".join(all_regions()) + ". Sectors: " + ", ".join(all_sectors()) + ".")
    w("- Country labels in the literal table: " + ", ".join(KNOWN_COUNTRIES + tuple(BUILDER_COUNTRIES)) + ".")
    w("- Euro area (2026 membership, every date): " + ", ".join(EA) + ". NORDIC: " + ", ".join(NORDIC) + ". AUNZ: every country under region Australia. OTHER_ASIA: every "
      "other country under region Asia. Region Supranational is excluded from every non-US total.")
    w("- Asset types seen: " + "; ".join("%s -> %s" % (k, v) for k, v in ITYPE_MAP.items()) + ".")
    w("- Relayed asset-type labels (N-MFP investment categories, not seen in OFR JSON when the spec was written; mapped as listed and flagged by C13b if seen): "
      + "; ".join("%s -> %s" % (k, v) for k, v in RELAYED_ITYPE_MAP.items()) + ".\n")
    w("## 4. CGFS Paper 65 (BIS, June 2020), quotes with printed page numbers\n")
    for p, q in CGFS_QUOTES:
        w("- %s: \"%s\"" % (p, q))
    w("- The paper does not single out Japanese and Canadian banks as money-fund dependent. Its money-fund charts (Graph 14, p 28) use Crane Data, which is not free.\n")
    w("## 5. Disclosure\n")
    w(DISCLOSURE + "\n")
    w("## 6. Builder decisions\n")
    for i, t in enumerate(list(builder_decisions(c)) + list(extra_decisions), 1):
        w("%d. %s" % (i, t))
    w("")
    w("### Kind table\n")
    w("The kinds rest on the builder's knowledge of each institution (relayed, not an OFR field); a note marks each judgement call.\n")
    w("| Parent | Country | Kind | Note |\n|---|---|---|---|")
    for (p, ct), k in sorted(c.kinds.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        w("| %s | %s | %s | %s |" % (p, ct, k, KIND_NOTES.get((p, ct), "")))
    w("")
    return "\n".join(L).rstrip("\n") + "\n"


# ------------------------------------------------------------------------------------------------------------------------
# build, kinds, fetch commands
# ------------------------------------------------------------------------------------------------------------------------
def render_texts(c, fetch_log_text, extra_decisions=()):
    src = source_line(c)
    t = collections.OrderedDict()
    t["levels_country.csv"] = render_csv("levels_country.csv", c.lc_rows, src)
    t["levels_group.csv"] = render_csv("levels_group.csv", c.lg_rows, src)
    t["quarter_ends.csv"] = render_csv("quarter_ends.csv", c.qe_rows, src)
    t["qe_summary.csv"] = render_csv("qe_summary.csv", c.qs_rows, src)
    t["parents.csv"] = render_csv("parents.csv", c.parents, src)
    t["summary.csv"] = render_csv("summary.csv", c.summary, src)
    t["revisions.csv"] = render_csv("revisions.csv", c.revs, src)
    t["vintages.csv"] = render_csv("vintages.csv", c.vint_rows, src)
    t["checks.csv"] = render_csv("checks.csv", c.checks, src)
    t["fetch_log.csv"] = fetch_log_text
    t["README.md"] = render_readme(c)
    t["SOURCES.md"] = render_sources(c, extra_decisions)
    return t


def texts_digest(texts):
    return sha256_of("".join("%s\0%s\0" % (k, v) for k, v in sorted(texts.items())).encode("utf-8"))


def read_data_rows(path):
    """Data rows (header and '# source:' line skipped) of a committed csv, [] if absent."""
    rows = read_csv_plain(path)
    rows = [r for r in rows if not (r and r[0].startswith("# source:"))]
    return rows[1:] if rows else []


def finish(vints, kinds, fetch_log_text, committed_vintage_rows=None, existing_revisions=None, kt_expected=None, pins=None):
    """compute twice for the determinism check, then once more with its result in checks.csv. Returns (ctx, texts)."""
    c1 = compute(vints, kinds, pins, committed_vintage_rows, existing_revisions, kt_expected)
    t1 = render_texts(c1, fetch_log_text)
    c2 = compute(vints, kinds, pins, committed_vintage_rows, existing_revisions, kt_expected)
    t2 = render_texts(c2, fetch_log_text)
    c1.determinism = "identical" if texts_digest(t1) == texts_digest(t2) else "DIFFERENT"
    c1.checks = build_checks(c1)
    return c1, render_texts(c1, fetch_log_text)


def run_build(a, say=print):
    cache = os.path.abspath(os.path.expanduser(a.cache))
    out = os.path.abspath(a.out)
    keys = vintage_dirs(cache)
    if not keys:
        say("no complete vintage in %s: run fetch first" % tilde(cache))
        return 2
    try:
        vints = [load_vintage(vintage_folder(cache, k)) for k in keys]
    except DataError as e:
        say("STOP (data): %s" % e)
        return 2
    V = vints[-1]
    F0 = ingest(V.nodes)
    gate = kind_gate_problems(parent_kind_keys(F0))
    if gate:
        for g in gate:
            say("kind gate: %s" % g)
        say("build exits 2 before writing any output (spec 3.7)")
        return 2
    log_text = render_csv("fetch_log.csv", all_log_rows(cache), fetch_log_source(cache))
    committed = read_data_rows(os.path.join(out, "vintages.csv"))
    existing = read_data_rows(os.path.join(out, "revisions.csv"))
    try:
        c, texts = finish(vints, KIND_TABLE, log_text, committed, existing)
    except DataError as e:
        say("STOP (data): %s" % e)
        return 2
    n = collections.Counter(r[4] for r in c.checks)
    bad = [r for r in c.checks if r[4] != "PASS"]
    for r in bad:
        say("%-5s %s: %s | expected %s | observed %s" % (r[4], r[0], r[1][:90], r[2][:60], r[3][:200]))
    say("checks: %d PASS, %d WARN, %d FAIL" % (n["PASS"], n["WARN"], n["FAIL"]))
    dest = out
    if n["FAIL"]:
        dest = os.path.join(out, "_FAILED")
        say("a check FAILED: outputs go to %s and the committed files are left alone" % tilde(dest))
    for name, text in texts.items():
        write_text(os.path.join(dest, name), text)
    say("wrote %d files to %s (vintage %s, data as of %s)" % (len(texts), tilde(dest), V.key, V.asof))
    return 1 if n["FAIL"] else 0


def run_kinds(a, say=print):
    cache = os.path.abspath(os.path.expanduser(a.cache))
    out = os.path.abspath(a.out)
    keys = vintage_dirs(cache)
    if not keys:
        say("no complete vintage in %s: run fetch first" % tilde(cache))
        return 2
    V = load_vintage(vintage_folder(cache, keys[-1]))
    F = ingest(V.nodes)
    rows = parents_rows(F, KIND_TABLE, V.asof, V.key)
    ctx = Ctx()
    ctx.V = V
    text = render_csv("parents.csv", rows, source_line(ctx))
    if "quarter" in text.split("\n")[1]:
        raise DataError("parents.csv must carry no quarter-end column")
    write_text(os.path.join(out, "parents.csv"), text)
    say("vintage %s (data as of %s): %d non-US financial-institution parents; parents.csv written to %s" % (V.key, V.asof, len(rows), tilde(out)))
    say("PARENT LIST (parent | country | group | kind | first | last | usd_mn_latest)")
    for r in rows:
        say(" | ".join(r[:7]))
    keys_p = parent_kind_keys(F)
    miss = [k for k in keys_p if k not in KIND_TABLE]
    say("")
    say("parents without a kind: %d%s" % (len(miss), "" if not miss else " -> " + "; ".join("%s (%s)" % k for k in miss[:12])))
    say("kind table sha256 (parent|country|kind lines, sorted): %s  (KIND_TABLE_SHA256 in the script: %s)" % (kind_table_sha(), KIND_TABLE_SHA256 or "not set"))
    say("UNKNOWN LABEL REPORT: %s" % unknown_text(F))
    for kind, label, where in unknown_report(F):
        say("  unknown %s: %r at %s" % (kind, label, where))
    rel = sorted({(l, w) for l, w in F.relayed})
    say("relayed asset-type labels seen: %s" % (", ".join(sorted({l for l, _ in rel})) or "none"))
    say("Aggregated small issuers nodes: %s" % (", ".join(F.small_issuers) or "none"))
    return 0


def run_fetch(a, say=print):
    fe = Fetcher(a.cache, a.out, sleep=a.sleep, max_requests=a.max_requests, max_seconds=a.max_seconds, say=say)
    return fe.run()


# ==== COMMAND LINE ====
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch", help="crawl the OFR monitor's chart files into the cache (the only network command); resumable")
    pf.add_argument("--cache", default=CACHE_DEFAULT)
    pf.add_argument("--out", default=OUT_DEFAULT, help="where the committed fetch_log.csv is kept")
    pf.add_argument("--sleep", type=float, default=DEFAULT_SLEEP)
    pf.add_argument("--max-requests", type=int, default=None, help="end this invocation after N requests (exit 3); run again to resume")
    pf.add_argument("--max-seconds", type=int, default=None, help="end this invocation after S seconds (exit 3); run again to resume")
    pk = sub.add_parser("kinds", help="offline: write parents.csv (no quarter-end figure) and print the parent list and unknown labels")
    pk.add_argument("--cache", default=CACHE_DEFAULT)
    pk.add_argument("--out", default=OUT_DEFAULT)
    pb = sub.add_parser("build", help="offline: validate the cache and write every output")
    pb.add_argument("--cache", default=CACHE_DEFAULT)
    pb.add_argument("--out", default=OUT_DEFAULT)
    ps = sub.add_parser("selftest", help="synthetic data, mutants applied one at a time; no network")
    ps.add_argument("--no-mutants", action="store_true")
    ps.add_argument("--mutant", help="run every guard with this one mutant switched on; exit 1 (the selftest fails) when it is caught")
    ps.add_argument("--write-fixture", help="write the clean synthetic output folder to DIR (used to show that bin/check.sh M23 fires on a planted copy)")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "selftest":
            if a.write_fixture:
                return write_fixture(a.write_fixture)
            return selftest(mutants=not a.no_mutants, only=a.mutant)
        if a.cmd == "build":
            return run_build(a)
        if a.cmd == "kinds":
            return run_kinds(a)
        return run_fetch(a)
    except Refused as e:
        print("refused: %s" % e, file=sys.stderr)
        return 5
    except DataError as e:
        print("STOP (data): %s" % e, file=sys.stderr)
        return 2



# ------------------------------------------------------------------------------------------------------------------------
# G16: the static scan of this script's own source (R3a): nothing deletes, renames, overwrites or truncates a STOP file
# ------------------------------------------------------------------------------------------------------------------------
DANGEROUS_CALLS = frozenset({"remove", "unlink", "replace", "rename", "rmtree", "move", "write_text", "write_bytes", "truncate", "removedirs", "rmdir"})
CACHE_ROOT_RX = re.compile(r"^(?:self\.)?cache$|CACHE_DEFAULT|^cache_dir$|glob", re.I)


def static_stop_problems(src):
    """AST scan. Flags: a dangerous call (os.remove, os.unlink, os.replace, os.rename, shutil.rmtree, shutil.move, Path.unlink, Path.rename, Path.write_text,
    Path.write_bytes ...) with an argument or receiver that mentions a STOP path; open() of a STOP path in any mode but 'x'; a delete or rmtree over the cache root
    or by glob (removing one <key>.partial by exact path is allowed)."""
    probs = []
    if M("g16_scan_off"):
        return probs
    dang = DANGEROUS_CALLS - {"rename", "replace"} if M("g16_scan_skip_rename") else DANGEROUS_CALLS
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return ["source does not parse: %s" % e]
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
        parts = [ast.unparse(a) for a in node.args] + [ast.unparse(k.value) for k in node.keywords]
        recv = ast.unparse(f.value) if isinstance(f, ast.Attribute) else ""
        text = " ".join(parts + [recv])
        if name in dang and re.search(r"stop", text, re.I):
            probs.append("line %d: %s reaches a STOP path (%s)" % (node.lineno, name, text[:60]))
        elif name in ("rmtree", "remove", "removedirs", "rmdir", "unlink") and parts and any(CACHE_ROOT_RX.search(p.strip()) for p in parts):
            probs.append("line %d: %s over the cache root or by glob (%s)" % (node.lineno, name, text[:60]))
        elif name == "open" and parts and re.search(r"stop", parts[0], re.I):
            mode = None
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                mode = node.args[1].value
            for k in node.keywords:
                if k.arg == "mode" and isinstance(k.value, ast.Constant):
                    mode = k.value.value
            if mode is not None and any(ch in str(mode) for ch in ("wa+" if not M("g16_scan_allow_w") else "")):
                probs.append("line %d: open of a STOP path in mode %r (only 'x' is allowed)" % (node.lineno, mode))
    return probs


def own_source():
    with open(os.path.abspath(__file__), encoding="utf-8") as fh:
        return fh.read()


# ------------------------------------------------------------------------------------------------------------------------
# selftest: synthetic data only. Every guard G1-G20 of the spec's section 7 has a test; each mutant (a deliberately broken variant, switched on in this
# process only) must make its guard's test fail. A mutant that is not caught is a failure.
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
    def __init__(self, t=1_761_400_000.0):
        self.t = t

    def wall(self):
        return self.t

    def sleep(self, s):
        self.t += s

    def tick(self, s=0.4):
        self.t += s


# ---- the synthetic world -----------------------------------------------------------------------------------------------
ALL_MONTHS = months_between(dt.date(2011, 1, 31), dt.date(2026, 9, 30))
LEGACY_END = dt.date(2016, 3, 31)
GOV_RETURN = dt.date(2024, 6, 30)
GOV_NEW_END = dt.date(2024, 5, 31)
REPO3 = ("Treasury Repurchase Agreement", "Government Agency Repurchase Agreement", "Other Repurchase Agreement")
W_PARENTS = (
    # (region, country, parent, {lineage: asset types})
    ("Europe", "France", "BNP Paribas", {"government": REPO3[:2], "prime": ("Certificate of Deposit", "Financial Company Commercial Paper", "Asset Backed Commercial Paper")}),
    ("Europe", "France", "Societe Generale", {"government": REPO3[:1], "prime": ("Certificate of Deposit",)}),
    ("Europe", "France", "Credit Agricole", {"government": ("Treasury Repurchase Agreement", "Other Repurchase Agreement"), "prime": ("Financial Company Commercial Paper",)}),
    ("Europe", "France", "Natexis + Natixis", {"government": REPO3[:1]}),
    ("Europe", "France", "Axa SA", {"government": REPO3[:1]}),
    ("Europe", "France", "Credit Mutuel", {}),
    ("Europe", "France", "Groupe BPCE", {}),
    ("Europe", "Germany", "Deutsche Bank AG", {"government": REPO3[:1], "prime": ("Certificate of Deposit",)}),
    ("Europe", "UK", "Barclays PLC", {"government": REPO3[:2], "prime": ("Certificate of Deposit", "Other Note")}),
    ("Europe", "Switzerland", "UBS Group AG", {"government": REPO3[:1], "prime": ("Financial Company Commercial Paper",)}),
    ("Europe", "Sweden", "Skandinaviska Enskilda Banken AB", {"prime": ("Certificate of Deposit", "Other Note")}),
    ("Asia", "Japan", "Mizuho Financial Group", {"government": REPO3[:2], "prime": ("Certificate of Deposit", "Non-Financial Company Commercial Paper")}),
    ("Asia", "Japan", "Nomura Holdings", {"government": REPO3[:2]}),
    ("Asia", "China", "Bank of China", {"prime": ("Certificate of Deposit",)}),
    ("Australia", "Australia", "Commonwealth Bank of Australia", {"government": REPO3[:1], "prime": ("Certificate of Deposit", "Financial Company Commercial Paper")}),
    ("North America", "Canada", "Royal Bank of Canada", {"government": REPO3[:2], "prime": ("Certificate of Deposit",)}),
    ("South America", "Brazil", "Itau Unibanco", {"prime": ("Certificate of Deposit",)}),
)
W_US_PARENTS = ("JPMorgan Chase", "Bank of America")
W_COUNTRIES = {"Europe": ["France", "Germany", "UK", "Switzerland", "Sweden"], "Asia": ["Japan", "China"], "Australia": ["Australia"], "North America": ["Canada", USA],
               "South America": ["Brazil"], "Supranational": ["Supranational"]}
W_REGIONS = ("Europe", "Asia", "Australia", "North America", "South America", "Supranational")
W_KINDS = {("Axa SA", "France"): "insurer", ("Nomura Holdings", "Japan"): "other_fin"}
for _r, _c, _p, _t in W_PARENTS:
    W_KINDS.setdefault((_p, _c), "bank")


def cat_active(cat, d):
    pre = d <= LEGACY_END
    if cat in ("Prime", "Tax Exempt"):
        return pre
    if cat in ("Prime Institutional", "Prime Retail", "Tax Exempt Institutional", "Tax Exempt Retail"):
        return not pre
    if cat == "Government":
        return pre or d >= GOV_RETURN
    return (not pre) and d <= GOV_NEW_END


def zlib_crc(s):
    import zlib
    return zlib.crc32(s.encode("utf-8"))


FR_PINNED = {
    # (parent, itype, month) -> cents, for the government category: the spec's France pins at 2026-09-30 and 2026-06-30
    ("BNP Paribas", "Treasury Repurchase Agreement", dt.date(2026, 9, 30)): 8606252756434,
    ("BNP Paribas", "Government Agency Repurchase Agreement", dt.date(2026, 9, 30)): 3300244026208,
    ("Societe Generale", "Treasury Repurchase Agreement", dt.date(2026, 9, 30)): 2623794800000,
    ("Credit Agricole", "Treasury Repurchase Agreement", dt.date(2026, 9, 30)): 5147458505340,
    ("Credit Agricole", "Other Repurchase Agreement", dt.date(2026, 9, 30)): 0,
    ("Natexis + Natixis", "Treasury Repurchase Agreement", dt.date(2026, 9, 30)): 1932500000000,
    ("BNP Paribas", "Treasury Repurchase Agreement", dt.date(2026, 6, 30)): 8500000000000,
    ("BNP Paribas", "Government Agency Repurchase Agreement", dt.date(2026, 6, 30)): 3000000000000,
    ("Societe Generale", "Treasury Repurchase Agreement", dt.date(2026, 6, 30)): 2500000000000,
    ("Credit Agricole", "Treasury Repurchase Agreement", dt.date(2026, 6, 30)): 5000000000000,
    ("Credit Agricole", "Other Repurchase Agreement", dt.date(2026, 6, 30)): 0,
    ("Natexis + Natixis", "Treasury Repurchase Agreement", dt.date(2026, 6, 30)): 1908319005781,
    ("Axa SA", "Treasury Repurchase Agreement", dt.date(2026, 9, 30)): 0,
    ("Axa SA", "Treasury Repurchase Agreement", dt.date(2026, 6, 30)): 0,
}
CAT_WEIGHT = {"Prime": 60, "Prime Institutional": 70, "Prime Retail": 20, "Government": 100, "Government (No Fees & Gates)": 90, "Government (Fees & Gates)": 15,
              "Tax Exempt": 5, "Tax Exempt Institutional": 6, "Tax Exempt Retail": 3}


def cell_cents(cat, parent, itype, di, d, repo_dip=True):
    """A deterministic positive value in cents for one parent, asset type and month."""
    key = (parent, itype, d)
    if cat == "Government" and key in FR_PINNED:
        return FR_PINNED[key]
    h = zlib_crc(parent + "|" + itype)
    base = 20_000_000_00 + (h % 997) * 2_000_000_00
    trend = 100 + (di * (1 + h % 3)) // 3
    jitter = 96 + ((h // 7 + di * 7919) % 9)
    v = base * CAT_WEIGHT[cat] * trend * jitter // 10_000
    if repo_dip and d.month in (3, 6, 9, 12) and itype.endswith("Repurchase Agreement") and parent != "Commonwealth Bank of Australia":
        v = v * 80 // 100
    return max(v, 1)


def epoch_ms(d):
    return (d - dt.date(1970, 1, 1)).days * 86_400_000


def cents_text(c):
    return float(Decimal(c) / 100)


def node_body_from(names, dates, vals):
    """JSON bytes of a node file (datatable and highcharts) from {name: [cents ints]}."""
    hc = [{"name": n, "data": [[epoch_ms(d), cents_text(vals[n][i])] for i, d in enumerate(dates)]} for n in names]
    dtb = {"columns": [{"title": "Date"}] + [{"title": n} for n in names],
           "values": [[d.strftime("%m-%d-%Y")] + [cents_text(vals[n][i]) for n in names] for i, d in enumerate(dates)]}
    return json.dumps({"datatable": dtb, "highcharts": hc}).encode("utf-8")


class World:
    pass


def zero_list(n):
    return [0] * n


def gen_world(months=None, zero_cat=None, revise=None, extra_us_fi=True):
    """The whole synthetic tree: {tpath: (names, dates, {name: [cents]})}. `zero_cat` makes one category zero everywhere (the fetch test);
    `revise` = (parent, itype, month, cents) overrides one cell (a revised vintage)."""
    nodes = {}
    months = list(months or ALL_MONTHS)
    cats = [c for c, _l in CATEGORIES]
    lin = dict(CATEGORIES)
    root_vals = {}
    for cat in cats:
        dates = [d for d in months if cat_active(cat, d) and cat != zero_cat]
        di = {d: i for i, d in enumerate(ALL_MONTHS)}
        L = len(dates)
        ln = lin[cat]
        region_vals = {}
        for region in W_REGIONS:
            country_vals = {}
            for ctry in W_COUNTRIES.get(region, []):
                fi_parents = [p for r, c, p, t in W_PARENTS if c == ctry]
                fi_vals = {}
                for r, c, p, t in W_PARENTS:
                    if c != ctry:
                        continue
                    types = t.get(ln, ())
                    pv = {}
                    for it in types:
                        series = []
                        for d in dates:
                            v = cell_cents(cat, p, it, di[d], d)
                            if revise and (p, it, d) == revise[:3] and cat == "Government":
                                v = revise[3]
                            series.append(v)
                        pv[it] = series
                    if types and L:
                        nodes[(cat, region, ctry, FI_SECTOR, p)] = (list(types), dates, pv)
                    fi_vals[p] = [sum(pv[it][i] for it in types) for i in range(L)] if types else zero_list(L)
                if ctry == USA:
                    fi_vals = {"FICC": [(50_000_000_000_00 * CAT_WEIGHT[cat] // 100 + di[d] * 1_000_000_00) if ln == "government" else 0 for d in dates]}
                    for k, us in enumerate(W_US_PARENTS):
                        fi_vals[us] = [(30_000_000_000_00 + k * 5_000_000_000_00 + di[d] * 2_000_000_00) * CAT_WEIGHT[cat] // 100 if ln != "tax_exempt" else 0 for d in dates]
                    fi_parents = list(fi_vals)
                    if extra_us_fi:
                        us_types = ["Treasury Repurchase Agreement", "Certificate of Deposit"]
                        nodes[(cat, region, ctry, FI_SECTOR, W_US_PARENTS[0])] = (us_types, dates, {t: [fi_vals[W_US_PARENTS[0]][i] // 2 for i in range(L)] for t in us_types})
                if ctry == "Supranational":
                    fi_vals = {"European Investment Bank": [(10_000_000_00 + di[d] * 100_000_00) * CAT_WEIGHT[cat] // 100 for d in dates]}
                    fi_parents = list(fi_vals)
                fi_sum = [sum(fi_vals[p][i] for p in fi_parents) for i in range(L)] if fi_parents else zero_list(L)
                gov_sector = [(5_000_000_000_00 + di[d] * 300_000_00) * CAT_WEIGHT[cat] // 100 if ctry in ("Japan", USA, "Canada", "France") else 0 for d in dates]
                nfc_sector = [(1_000_000_00 + di[d] * 10_000_00) * CAT_WEIGHT[cat] // 100 if ctry in ("Japan", "Germany") else 0 for d in dates]
                if ctry == USA and ln == "tax_exempt":
                    gov_sector = [(40_000_000_000_00 + di[d] * 100_000_00) * CAT_WEIGHT[cat] // 100 for d in dates]
                if any(fi_sum):
                    nodes[(cat, region, ctry, FI_SECTOR)] = (fi_parents, dates, fi_vals)
                    if ctry != USA and extra_us_fi and ctry == "Japan":
                        nodes[(cat, region, ctry, "Government")] = (["Japan Ministry of Finance"], dates, {"Japan Ministry of Finance": list(gov_sector)})
                sectors = {FI_SECTOR: fi_sum, "Government": gov_sector, "Non-Financial Corporate": nfc_sector}
                country_vals[ctry] = [sum(sectors[s][i] for s in SECTORS) for i in range(L)]
                if any(country_vals[ctry]):
                    nodes[(cat, region, ctry)] = (list(SECTORS), dates, sectors)
            region_vals[region] = [sum(country_vals[c][i] for c in country_vals) for i in range(L)] if country_vals else zero_list(L)
            if any(region_vals[region]):
                nodes[(cat, region)] = (list(country_vals), dates, country_vals)
        cat_total = [sum(region_vals[r][i] for r in W_REGIONS) for i in range(L)]
        if any(cat_total):
            nodes[(cat,)] = (list(W_REGIONS), dates, region_vals)
        root_vals[cat] = {d: cat_total[i] for i, d in enumerate(dates)}
    root_series = {c: [root_vals[c].get(d, 0) for d in months] for c in cats}
    nodes[()] = (cats, months, root_series)
    return nodes


def api_body(m, series):
    return json.dumps({m: {"timeseries": {"aggregation": [[d.isoformat(), cents_text(v)] for d, v in series]}}}).encode("utf-8")


def world_files(nodes, updated="October 15, 2026", asof="September 30, 2026"):
    """{(host, url_path): bytes} for everything the synthetic OFR serves."""
    files = {}
    for p, (names, dates, vals) in nodes.items():
        files[(HOST_WWW, node_url_path(p))] = node_body_from(names, dates, vals)
    files[(HOST_WWW, UPDATED_PATH)] = json.dumps({"updated": updated}).encode()
    files[(HOST_WWW, ASOF_PATH)] = json.dumps({"asof": asof}).encode()
    root = nodes[()]
    tot = [(d, sum(root[2][c][i] for c in root[0])) for i, d in enumerate(root[1])]
    pre = [(dt.date(2010, 11, 30), tot[0][1]), (dt.date(2010, 12, 31), tot[0][1])]
    repo, ficc_by = collections.defaultdict(int), collections.defaultdict(int)
    for p, (names, dates, vals) in nodes.items():
        if len(p) == 5 and p[3] == FI_SECTOR and p[2] not in (USA, "Supranational"):
            for i, d in enumerate(dates):
                repo[d] += sum(vals[n][i] for n in names if n.endswith("Repurchase Agreement"))
        if len(p) == 4 and p[2] == USA and p[3] == FI_SECTOR:
            for i, d in enumerate(dates):
                ficc_by[d] += vals["FICC"][i]
    ffi = [(d, repo[d]) for d in root[1]]
    ficc = [(d, ficc_by[d]) for d in root[1]]
    files[(HOST_API, api_url_path("MMF-MMF_TOT-M"))] = api_body("MMF-MMF_TOT-M", pre + tot)
    files[(HOST_API, api_url_path("MMF-MMF_RP_wFFI-M"))] = api_body("MMF-MMF_RP_wFFI-M", ffi)
    files[(HOST_API, api_url_path("MMF-MMF_RP_wFICC-M"))] = api_body("MMF-MMF_RP_wFICC-M", ficc)
    files[(HOST_API, api_url_path("MMF-MMF_RP_wDFI-M"))] = api_body("MMF-MMF_RP_wDFI-M", [(d, 1000_00) for d in root[1]])
    return files


def make_vintage(files, key="2026-10-15", asof=dt.date(2026, 9, 30), requests=412, retrieved="2026-10-25"):
    """A Vintage built straight from the served bodies (what `load_vintage` does from disk)."""
    V = Vintage()
    V.key, V.updated, V.asof = key, D_(key), asof
    V.nodes = {}
    nodes_by_url = {u: b for (h, u), b in files.items() if h == HOST_WWW}
    while True:
        need = needed(V.nodes)
        if not need:
            break
        for p in need:
            V.nodes[p] = parse_node(nodes_by_url[node_url_path(p)], p)
    V.api = {m: parse_api(files[(HOST_API, api_url_path(m))], m) for m in API_MNEMONICS}
    reach = {node_url_path(p) for p in V.nodes}
    rows = [[u, sha256_of(b), str(len(b))] for (h, u), b in sorted(files.items()) if not u.startswith(MON_BASE + ROOT_DIR) or u in reach]
    V.manifest, V.manifest_sha, V.requests, V.retrieved, V.folder = rows, manifest_sha(rows), requests, retrieved, None
    return V


_WORLD = {}


def synth_pins(V, kinds=None):
    """The synthetic world's pins: the spec's France pins (the world is built to hit them) and a few cells of its own."""
    out = [p for p in PINS if p[0] in ("C02a", "C02b", "C02c", "C02d", "C02e", "C02f", "C02g", "C02h", "C02i", "C02j", "C02k", "C02l", "C04")]
    nodes = V.nodes
    extra = [("C01a", "sum of the nine root categories", (), None, "2026-09-30"), ("C01b", "sum of the nine root categories", (), None, "2011-01-31"),
             ("C03a", "Japan, all sectors, government funds", (GOV, "Asia"), "Japan", "2026-09-30"),
             ("C06", "FICC, government funds", (GOV, "North America", USA, FI_SECTOR), "FICC", "2026-09-30")]
    for pid, desc, path, child, ds in extra:
        out.append((pid, desc, path, child, ds, format(pin_value(nodes, path, child, D_(ds)), "f")))
    return tuple(out)


@contextlib.contextmanager
def world_labels():
    """The synthetic world uses one country label the real table does not hold (Brazil): added the way the builder adds one, for the test only."""
    added = "Brazil" not in BUILDER_COUNTRIES
    if added:
        BUILDER_COUNTRIES["Brazil"] = "synthetic"
    try:
        yield
    finally:
        if added:
            BUILDER_COUNTRIES.pop("Brazil", None)


def get_world():
    if _WORLD:
        return _WORLD
    with world_labels():
        nodes = gen_world()
        files = world_files(nodes)
        V = make_vintage(files)
        pins = synth_pins(V)
        log_text = render_csv("fetch_log.csv", [["2026-10-25T10:00:00.000Z", HOST_WWW, UPDATED_PATH, "200", "28", "0" * 64]], "# source: synthetic request log")
        kt = kind_table_sha(W_KINDS)
        c, texts = finish([V], W_KINDS, log_text, None, None, kt, pins)
        _WORLD.update(nodes=nodes, files=files, V=V, pins=pins, c=c, texts=texts, log_text=log_text, kt=kt)
    return _WORLD


# ---- fixtures ----------------------------------------------------------------------------------------------------------
D3 = [dt.date(2024, 6, 30), dt.date(2024, 7, 31), dt.date(2024, 8, 31)]


def dd(x):
    return Decimal(str(x))


def mini_nodes(parents, extra_sectors=None, small=None, region="Asia", country="Japan", cat="Government", dates=None, cat_dates=None):
    """A consistent little tree: root > category > region > country > Financial Institution > parents > asset types. `parents` = {name: {asset type: [3 values]}}."""
    dates = dates or D3
    n = len(dates)
    nodes = {}
    fi_vals = {}
    for p, types in parents.items():
        names = list(types)
        nodes[(cat, region, country, FI_SECTOR, p)] = Node((cat, region, country, FI_SECTOR, p), names, dates, {t: [dd(x) for x in types[t]] for t in names})
        fi_vals[p] = [sum(dd(types[t][i]) for t in names) for i in range(n)]
    if small:
        fi_vals[SMALL_ISSUERS] = [dd(x) for x in small]
    fi_names = list(fi_vals)
    nodes[(cat, region, country, FI_SECTOR)] = Node((cat, region, country, FI_SECTOR), fi_names, dates, fi_vals)
    fi_tot = [sum(fi_vals[p][i] for p in fi_names) for i in range(n)]
    sectors = {FI_SECTOR: fi_tot}
    for s, v in (extra_sectors or {}).items():
        sectors[s] = [dd(x) for x in v]
    nodes[(cat, region, country)] = Node((cat, region, country), list(sectors), dates, sectors)
    c_tot = [sum(sectors[s][i] for s in sectors) for i in range(n)]
    nodes[(cat, region)] = Node((cat, region), [country], dates, {country: c_tot})
    nodes[(cat,)] = Node((cat,), [region], cat_dates or dates, {region: c_tot if not cat_dates else [c_tot[dates.index(d)] for d in cat_dates]})
    root_vals = {c: [Decimal(0)] * n for c, _ in CATEGORIES}
    root_vals[cat] = c_tot
    nodes[()] = Node((), [c for c, _ in CATEGORIES], dates, root_vals)
    return nodes


MINI_P = {"Bank A": {"Treasury Repurchase Agreement": ["1000000.01", "2000000.02", "3000000.03"], "Certificate of Deposit": ["500.50", "600.60", "700.70"],
                     "Asset Backed Commercial Paper": ["10", "20", "30"], "Non-Financial Company Commercial Paper": ["1", "2", "3"]},
          "Bank B": {"Other Repurchase Agreement": ["7", "8", "9"], "Government Agency Repurchase Agreement": ["11", "12", "13"], "Financial Company Commercial Paper": ["70", "80", "90"], "Other Note": ["3", "3", "3"]}}


def month_series(start, vals, months=None):
    """{month-end: Decimal} from consecutive months starting at `start`."""
    out, d = {}, start
    for v in vals:
        out[d] = dd(v)
        d = next_month_end(d)
    return out


def flat_series(months, base, qe_value=None, pairs=None):
    """A series flat at `base` except calendar quarter-end months at `qe_value`."""
    s = {}
    for d in months:
        s[d] = Decimal(qe_value if (qe_value is not None and d.month in (3, 6, 9, 12)) else base)
    return s


def node_body(names, dates, vals, dt_vals=None):
    hc = [{"name": n, "data": [[epoch_ms(d), float(vals[n][i])] for i, d in enumerate(dates)]} for n in names]
    dv = dt_vals or vals
    dtb = {"columns": [{"title": "Date"}] + [{"title": n} for n in names], "values": [[d.strftime("%m-%d-%Y")] + [float(dv[n][i]) for n in names] for i, d in enumerate(dates)]}
    return json.dumps({"datatable": dtb, "highcharts": hc}).encode("utf-8")


# ---- G1 ----------------------------------------------------------------------------------------------------------------
def t_g1(ck):
    ck.eq("'Natexis + Natixis' keeps its plus encoded", seg("Natexis + Natixis"), "natexis_%2B_natixis")
    ck.eq("'Government (Fees & Gates)' keeps its brackets and encodes the ampersand", seg("Government (Fees & Gates)"), "government_(fees_%26_gates)")
    ck.eq("accented letters are percent-encoded as UTF-8", seg("Société Générale"), "soci%C3%A9t%C3%A9_g%C3%A9n%C3%A9rale")
    ck.eq("U+00A0 is whitespace and a comma is encoded", seg("Loop Capital\xa0Holdings, LLC."), "loop_capital_holdings%2C_llc.")
    ck.eq("every space, not only the first, becomes an underscore", seg("a b c d"), "a_b_c_d")
    ck.eq("a node path is the root folder plus one segment per name", node_url_path(("Government (Fees & Gates)",)),
          "/money-market-funds/data/credit_risks_country/government_(fees_%26_gates)/data.json")
    ck.eq("the root path", node_url_path(()), "/money-market-funds/data/credit_risks_country/data.json")
    ck.raises("two siblings mapping to one segment are a FAIL", DataError, lambda: check_siblings(["Bank A", "bank_a"]))
    ck.raises("...also when they differ by an NBSP", DataError, lambda: check_siblings(["Loop Capital Holdings", "Loop Capital\xa0Holdings"]))
    check_siblings(["Bank A", "Bank B"])
    ck.ok("distinct siblings pass", True)


# ---- G2 ----------------------------------------------------------------------------------------------------------------
def t_g2(ck):
    nodes = mini_nodes(MINI_P)
    ck.eq("a consistent tree has no identity breach (no dropped child, none counted twice)", node_problems(nodes), [])
    bad = mini_nodes(MINI_P)
    fi = bad[("Government", "Asia", "Japan", FI_SECTOR)]
    fi.vals["Bank B"] = [fi.vals["Bank B"][0] + Decimal("5.00")] + fi.vals["Bank B"][1:]
    ck.ok("a 5 USD breach is reported", bool(node_problems(bad)), "no problem reported")
    ok1 = mini_nodes(MINI_P)
    fi = ok1[("Government", "Asia", "Japan", FI_SECTOR)]
    fi.vals["Bank B"] = [fi.vals["Bank B"][0] + Decimal("0.99")] + fi.vals["Bank B"][1:]
    ck.eq("...a 0.99 USD difference is within the 1.00 tolerance", node_problems(ok1), [])
    names = ["Bank A", "Bank B"]
    vals = {"Bank A": [1, 2, 3], "Bank B": [4, 5, 6]}
    good = node_body(names, D3, vals)
    ck.eq("a node whose datatable equals its highcharts passes the content test", body_problem("node", good), None)
    off = node_body(names, D3, vals, {"Bank A": [1, 2, 3], "Bank B": [4, 5.01, 6]})
    ck.ok("one datatable cell differing from highcharts is reported", body_problem("node", off) is not None)
    renamed = json.loads(good)
    renamed["datatable"]["columns"][1]["title"] = "Other"
    ck.ok("datatable column titles differing from the series names are reported", body_problem("node", json.dumps(renamed).encode()) is not None)


# ---- G3 ----------------------------------------------------------------------------------------------------------------
def lineage_root():
    d = [dt.date(2011, 1, 31), dt.date(2018, 5, 31), dt.date(2025, 5, 31)]
    vals = {c: [Decimal(0)] * 3 for c, _ in CATEGORIES}
    vals["Government"] = [Decimal(5), Decimal(0), Decimal(7)]
    vals["Government (No Fees & Gates)"] = [Decimal(0), Decimal(4), Decimal(0)]
    vals["Government (Fees & Gates)"] = [Decimal(0), Decimal(1), Decimal(0)]
    vals["Prime"] = [Decimal(3), Decimal(0), Decimal(0)]
    vals["Prime Institutional"] = [Decimal(0), Decimal(2), Decimal(2)]
    return Node((), [c for c, _ in CATEGORIES], d, vals)


def t_g3(ck):
    root = lineage_root()
    ck.eq("'Government' nonzero in 2011 and 2025, the fees-and-gates names in 2018: no lineage problem", lineage_problems(root), [])
    both = lineage_root()
    both.vals["Government (No Fees & Gates)"][2] = Decimal(1)
    ck.ok("the old and a new name both nonzero in one month is reported", bool(lineage_problems(both)))
    W = get_world()
    F = ingest(W["V"].nodes)
    ck.eq("the world's nine category names are all known, 'Government (Fees & Gates)' included", [u for u in unknown_report(F) if u[0] == "category"], [])
    d = dt.date(2018, 5, 31)
    ck.ok("the government lineage total in a fees-and-gates month is the sum of both new names",
          F.lin_total["government"][d] == sum(W["V"].nodes[()].vals[n][W["V"].nodes[()].idx[d]] for n in ("Government (No Fees & Gates)", "Government (Fees & Gates)", "Government")))
    gap = mini_nodes(MINI_P, dates=[D3[0], D3[2]])
    rv = {c: [Decimal(0)] * 3 for c, _ in CATEGORIES}
    rv["Government"] = [gap[()].vals["Government"][0], Decimal(777), gap[()].vals["Government"][1]]
    gap[()] = Node((), [c for c, _ in CATEGORIES], D3, rv)
    ck.ok("a month the category file omits while the root is nonzero is a breach, not a zero", bool(node_problems(gap)))
    ck.eq("category counts follow the CATEGORIES order", [category_counts(W["V"].nodes[()])[3]], [91])


# ---- G4 ----------------------------------------------------------------------------------------------------------------
def t_g4(ck):
    root = lineage_root()
    tot = {d: sum(root.vals[n][i] for n in root.names) for i, d in enumerate(root.dates)}
    ck.eq("categories equal the API total", api_total_problems(root, tot)[0], [])
    root2 = lineage_root()
    root2.vals["Government"] = [Decimal(1_000_000_000) + x for x in root2.vals["Government"]]
    tot2 = {d: sum(root2.vals[n][i] for n in root2.names) for i, d in enumerate(root2.dates)}
    off = dict(tot2)
    off[root2.dates[1]] = tot2[root2.dates[1]] * Decimal("1.0009")
    ck.ok("a 0.09% difference in the total is reported", bool(api_total_problems(root2, off)[0]))
    off5 = dict(tot2)
    off5[root2.dates[0]] += Decimal("5.00")
    ck.ok("a 5 USD difference is reported", bool(api_total_problems(root2, off5)[0]))
    ck.ok("a missing API month is reported", bool(api_total_problems(root2, {root2.dates[0]: tot2[root2.dates[0]]})[0]))


# ---- G5 ----------------------------------------------------------------------------------------------------------------
def t_g5(ck):
    with world_labels():
        cc = classify_country
        ck.eq("France is EA and FR", cc("Europe", "France"), ("EA", "FR"))
        ck.eq("UK is UK and not EA", cc("Europe", "UK"), ("UK",))
        ck.eq("USA is excluded from the non-US totals", cc("North America", "USA"), (EXCL_US,))
        ck.eq("the region Supranational is excluded", cc("Supranational", "Supranational"), (EXCL_SUPRA,))
        ck.eq("Japan is JP, China is OTHER_ASIA, Australia is AUNZ, Brazil is OTHER", (cc("Asia", "Japan"), cc("Asia", "China"), cc("Australia", "Australia"), cc("South America", "Brazil")),
              (("JP",), ("OTHER_ASIA",), ("AUNZ",), ("OTHER",)))
        ck.eq("an unknown label is not accepted", cc("Europe", "Atlantis"), None)
        ck.eq("selection is by whole name, not substring ('Korea' is not 'South Korea')", cc("Asia", "Korea"), None)
        W = get_world()
        G, _cm = group_levels(W["c"].F, W_KINDS)
        indep = {}
        for c in W["c"].F.cgroups:
            sadd(indep, W["c"].cm[c]["headline"]["all"])
        allv = G[("ALL_NONUS", "headline", "all")]
        ck.ok("ALL_NONUS equals the sum over countries: FR and MEMO_FICC are not added", all(abs(allv.get(d, 0) - indep.get(d, 0)) <= IDENT_TOL for d in set(allv) | set(indep)))
        ficc = G[("MEMO_FICC", "headline", "all")]
        ck.ok("MEMO_FICC is positive and outside ALL_NONUS", any(v > 0 for v in ficc.values()))
        d = W["V"].asof
        ck.ok("FR is inside EA", G[("FR", "headline", "all")][d] <= G[("EA", "headline", "all")][d])


# ---- G6 ----------------------------------------------------------------------------------------------------------------
def t_g6(ck):
    nodes = mini_nodes(MINI_P, extra_sectors={"Government": ["90000", "90000", "90000"], "Non-Financial Corporate": ["5000", "5000", "5000"]})
    F = ingest(nodes)
    fi = [sum(dd(MINI_P[p][t][i]) for p in MINI_P for t in MINI_P[p]) for i in range(3)]
    ck.eq("Japan's headline is its Financial Institution sector only", [F.head["Japan"]["government"][d] for d in D3], fi)
    ck.eq("the other two sectors are known labels, so nothing is reported unknown", unknown_report(F), [])


# ---- G7 ----------------------------------------------------------------------------------------------------------------
def t_g7(ck):
    nodes = mini_nodes(MINI_P, small=["5", "5", "5"])
    F = ingest(nodes)
    G, cm = group_levels(F, {("Bank A", "Japan"): "bank", ("Bank B", "Japan"): "other_fin"})
    d = D3[0]
    g = lambda m: G[("JP", m, "all")].get(d, Decimal(0))
    ck.eq("secured is the three repo groups", g("secured"), dd("1000000.01") + dd(7) + dd(11))
    ck.eq("unsecured is cd + time deposit + financial CP + other note, not ABCP or misc", g("unsecured"), dd("500.50") + dd(70) + dd(3))
    ck.eq("abcp is alone", g("abcp"), dd(10))
    ck.eq("misc is non-financial CP", g("misc"), dd(1))
    ck.eq("unallocated is the small-issuers child", g("unallocated"), dd(5))
    ck.eq("the identity secured + unsecured + abcp + misc + unallocated = headline holds", measure_identity_problems(G), [])
    ck.eq("bank_only counts Bank A only", g("bank_only"), dd("1000000.01") + dd("500.50") + dd(10) + dd(1))
    bad = mini_nodes({"Bank A": {"Strange Instrument": ["1", "1", "1"]}, "Bank B": {"Another Strange One": ["2", "2", "2"], "Treasury Repurchase Agreement": ["1", "1", "1"]}},
                     extra_sectors={"Weird Sector": ["1", "1", "1"]})
    bad[("Government", "Asia")] = Node(("Government", "Asia"), ["Japan", "Narnia"], D3, {"Japan": bad[("Government", "Asia")].vals["Japan"], "Narnia": [Decimal(0)] * 3})
    Fb = ingest(bad)
    kinds = sorted((k, l) for k, l, _w in unknown_report(Fb))
    ck.eq("all unknown labels are reported together, with their node", kinds, [("asset type", "Another Strange One"), ("asset type", "Strange Instrument"), ("country", "Narnia"),
                                                                               ("sector", "Weird Sector")])
    ck.ok("each unknown label names the node where it appeared", all(w for _k, _l, w in unknown_report(Fb)))
    rel = mini_nodes({"Bank A": {"Non-Negotiable Time Deposit": ["4", "4", "4"]}})
    Fr = ingest(rel)
    ck.eq("a relayed label is mapped as listed and flagged", ([l for l, _w in Fr.relayed], Fr.pcells[("Japan", "Bank A")]["government"]["time_deposit"][D3[0]]), (["Non-Negotiable Time Deposit"], dd(4)))


# ---- G8 ----------------------------------------------------------------------------------------------------------------
def float_fixture():
    vals, x = [], 12345
    for _ in range(10000):
        x = (x * 1103515245 + 12345) % (2 ** 31)
        vals.append(Decimal(10_000_000_000_000 + x % 9_000_000_000_000 + (x // 3) % 100) / 100)
    return vals


def t_g8(ck):
    vals = float_fixture()
    exact = Decimal(0)
    for v in vals:
        exact += v
    flt = 0.0
    for v in vals:
        flt += float(v)
    ck.ok("fixture precondition: the float sum of 10,000 cents-valued children is off by more than 0.005", abs(Decimal(repr(flt)) - exact) > Decimal("0.005"),
          "off by %s" % abs(Decimal(repr(flt)) - exact))
    ck.eq("dsum is exact", dsum(vals), exact)
    ck.eq("USD to USD millions is divided by 10^6", dstr(usd_to_mn(Decimal("123456789012.34")), 1), "123456.8")
    ck.eq("...and not by 10^3 or 10^9", usd_to_mn(Decimal("5000000")), Decimal(5))
    n = mini_nodes({"P%d" % i: {"Treasury Repurchase Agreement": ["40000", "40000", "40000"]} for i in range(10)})
    F = ingest(n)
    G8, _cm8 = group_levels(F, {})
    ck.eq("ten cells of 0.04 USD million sum to 0.4 before any rounding", dstr(usd_to_mn(G8[("JP", "secured", "all")][D3[0]]), 1), "0.4")
    c = qe_cell(month_series(dt.date(2024, 1, 31), [100049000, 100049000, 90049000, 110049000]), list(month_series(dt.date(2024, 1, 31), [1, 1, 1, 1])), 2, "calendar")
    ck.eq("logs are taken on the unrounded levels", dstr(c["below"], 4), dstr(0.5 * (100.0 * math.log(90049000 / 100049000) - 100.0 * math.log(110049000 / 90049000)), 4))
    ck.eq("usd_mn has 1 decimal, a share 3, a percent change 4, a count none", (dstr(Decimal("1.25"), 1), dstr(Decimal("12.3456"), 3), dstr(-15.30164, 4), str(3)), ("1.3", "12.346", "-15.3016", "3"))
    ck.eq("rounding is half up", (dstr(Decimal("0.25"), 1), dstr(Decimal("-0.25"), 1)), ("0.3", "-0.3"))
    ck.eq("no negative zero", dstr(Decimal("-0.04"), 1), "0.0")
    try:
        r = json_load(b'{"a": 0.07}')
        ck.ok("JSON money is parsed as Decimal", isinstance(r["a"], Decimal))
    except Exception as e:
        ck.ok("JSON money is parsed as Decimal", False, str(e))


# ---- G9 ----------------------------------------------------------------------------------------------------------------
def t_g9(ck):
    ck.eq("epoch 1296432000000 is 2011-01-31 in UTC", tz_epoch_ms_to_date(1296432000000), dt.date(2011, 1, 31))
    ck.eq("the 2026-09-30 epoch", tz_epoch_ms_to_date(epoch_ms(dt.date(2026, 9, 30))), dt.date(2026, 9, 30))
    ck.eq("MM-DD-YYYY is read month first", parse_mdy("02-28-2011"), dt.date(2011, 2, 28))
    ck.eq("...also for 01-31-2011", parse_mdy("01-31-2011"), dt.date(2011, 1, 31))
    nm = node_body(["A"], [dt.date(2011, 1, 30)], {"A": [1]})
    ck.ok("a date that is not a calendar month-end is a content failure", body_problem("node", nm) is not None)
    ck.eq("a month-end passes", body_problem("node", node_body(["A"], [dt.date(2011, 1, 31)], {"A": [1]})), None)
    ck.eq("asof.json parses 'September 30, 2026'", parse_date_json(b'{"asof": "September 30, 2026"}', "asof"), dt.date(2026, 9, 30))
    ck.ok("asof.json with two keys is a content failure", body_problem("asof", b'{"asof": "September 30, 2026", "x": 1}') is not None)
    ck.ok("updated.json that is not a date is a content failure", body_problem("updated", b'{"updated": "yesterday"}') is not None)


# ---- G10 ---------------------------------------------------------------------------------------------------------------
M2020 = [month_end(2020, m) for m in range(1, 13)]


def three(a, b, c):
    s = {d: Decimal(100_000_000) for d in M2020}
    s[dt.date(2020, 2, 29)], s[dt.date(2020, 3, 31)], s[dt.date(2020, 4, 30)] = (dd(a * 1_000_000), dd(b * 1_000_000), dd(c * 1_000_000))
    return s


def calendar_fall_series(years, fall=80):
    ms = months_between(dt.date(years[0], 1, 31), dt.date(years[1], 12, 31))
    return ms, flat_series(ms, 100_000_000, fall * 1_000_000)


def t_g10(ck):
    c1 = qe_cell(three(100, 90, 110), M2020, 2, "calendar")
    ck.eq("levels (100, 90, 110) give -15.3016", dstr(c1["below"], 4), "-15.3016")
    c2 = qe_cell(three(100, 80, 100), M2020, 2, "calendar")
    ck.eq("levels (100, 80, 100) give -22.3144", dstr(c2["below"], 4), "-22.3144")
    ck.eq("...as half of (chg_in - chg_out)", dstr(0.5 * (c2["cin"] - c2["cout"]), 4), "-22.3144")
    ck.eq("below_nbrs_usd_mn is the level minus the average of the neighbours", dstr(usd_to_mn(c1["usd"]), 1), "-15.0")
    ms, ser = calendar_fall_series((2017, 2019))
    rows = qe_rows_for(ser, ms, "calendar", "ALL_NONUS", "secured")
    qs = [r["below"] for r in rows if r["window"] == W_POST and r["below"] is not None]
    mean = sum(qs) / len(qs)
    ck.eq("a fixture of eleven such quarters gives 'lower'", pattern_with_sd(len(qs), mean, 0.0, 0.0), "lower")
    ck.eq("...with n = 11 (the last quarter has no next month)", len(qs), 11)
    cal = qe_rows_for(ser, ms, "ca_fiscal", "CA", "secured")
    cb = [r["below"] for r in cal if r["below"] is not None]
    cmean = sum(cb) / len(cb)
    csd = stdev1(cb)
    cse = csd / math.sqrt(len(cb))
    ck.eq("a series with a calendar-only fall reads 'neither' on the ca_fiscal basis", pattern_with_sd(len(cb), cmean, cse, csd), "neither")
    ck.eq("ca_fiscal rows are one-sided with no previous month", {(r["kind"], r["prev"], r["cin"]) for r in cal}, {("one_sided", None, None)})
    ck.eq("no non-calendar basis uses a calendar quarter-end month as a neighbour", basis_rule_problems(cal + qe_rows_for(ser, ms, "jp_march", "JP", "secured") +
          qe_rows_for(ser, ms, "jp_other", "JP", "secured")), [])
    jm = qe_rows_for(ser, ms, "jp_march", "JP", "secured")
    ck.ok("jp_march rows are all March", jm and all(r["month"].month == 3 for r in jm))
    ck.eq("jp_other rows are June, September, December", sorted({r["month"].month for r in qe_rows_for(ser, ms, "jp_other", "JP", "secured")}), [6, 9, 12])
    zero = three(100, 0, 100)
    zc = qe_cell(zero, M2020, 2, "calendar")
    ck.eq("a zero level leaves the affected cells blank", (dstr(zc["cin"], 4), dstr(zc["cout"], 4), dstr(zc["below"], 4)), ("", "", ""))
    ck.eq("...and no infinity", zc["below"], None)
    # noise
    ms2 = months_between(dt.date(2017, 1, 31), dt.date(2019, 12, 31))
    base = [100.0 + ((i * 7) % 5) for i in range(len(ms2))]
    s2 = {d: dd(base[i] * 1_000_000) for i, d in enumerate(ms2)}
    for d in ms2:
        if d.month in (3, 6, 9, 12):
            s2[d] = dd(40 * 1_000_000)
    clean = []
    for i, d in enumerate(ms2[:-1]):
        if d.month in (1, 4, 7, 10) and window_of(d) == W_POST:
            clean.append(100 * math.log(float(s2[ms2[i + 1]]) / float(s2[d])))
    sd = statistics.stdev(clean)
    nz, nn, raw = noise_reference(s2, ms2, W_POST, "two_sided")
    ck.eq("the clean changes are Jan-Feb, Apr-May, Jul-Aug, Oct-Nov", nn, len(clean))
    ck.ok("two-sided noise is the sd of the clean changes divided by sqrt 2, untouched by the quarter-end months", abs(nz - sd / math.sqrt(2)) < 1e-9, "%r vs %r" % (nz, sd / math.sqrt(2)))
    nz1, _n1, _r1 = noise_reference(s2, ms2, W_POST, "one_sided")
    ck.ok("one-sided noise is the sd itself", abs(nz1 - sd) < 1e-9)
    ck.ok("sd uses n - 1", abs(stdev1([1.0, 2.0, 3.0, 4.0]) - 1.2909944487358056) < 1e-12)
    ck.eq("a mean of -1 with se 0.375 (sd 1.5) is 'lower': the threshold is on the standard error", pattern_with_sd(16, -1.0, 0.375, 1.5), "lower")
    ck.eq("seven quarters are 'insufficient', eight are not", (pattern_with_sd(7, -5.0, 0.1, 0.26), pattern_with_sd(8, -5.0, 0.1, 0.28)), ("insufficient", "lower"))
    ck.eq("'higher' and 'neither'", (pattern_with_sd(10, 3.0, 1.0, 3.0), pattern_with_sd(10, 1.0, 1.0, 3.0)), ("higher", "neither"))
    g = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]
    a = [9.0, 19.0, 29.0, 39.0, 49.0, 59.0, 69.0, 79.0]
    n_, m_, se_ = paired_vs(dict(enumerate(g)), dict(enumerate(a)))
    ck.ok("the paired difference has its own standard error (here zero), not the unpaired one", n_ == 8 and abs(m_ - 1.0) < 1e-12 and abs(se_) < 1e-9, "n %s mean %s se %s" % (n_, m_, se_))
    n2, m2, s2_ = paired_vs({1: 5.0, 2: None, 3: 4.0}, {1: 1.0, 2: 1.0, 3: None})
    ck.eq("only quarters where both are non-blank are paired", (n2, m2), (1, 4.0))


# ---- G11 ---------------------------------------------------------------------------------------------------------------
def oracle_blind(r):
    if r["window"] in (W_PRE, W_TRANS, W_AFTER):
        return "no"
    if any(d >= dt.date(2026, 6, 1) for d in r["used"]):
        return "no"
    if r["group"] == "ALL_NONUS" and r["measure"] in ("secured", "headline"):
        return "no"
    return "yes"


def t_g11(ck):
    W = get_world()
    c = W["c"]
    qe = qe_all_rows(c.G, c.F.months)
    qs = qe_summary_rows(qe, c.G, c.F.months, "v")
    ck.eq("the windows by quarter", [window_of(D_(x)) for x in ("2016-06-30", "2016-09-30", "2016-12-31", "2017-03-31", "2026-06-30", "2026-09-30")],
          [W_PRE, W_TRANS, W_TRANS, W_POST, W_POST, W_AFTER])
    ck.eq("the transition quarters 2016Q3-Q4 are written as rows", sorted({r["quarter"] for r in qe if r["window"] == W_TRANS}), ["2016Q3", "2016Q4"])
    ck.eq("...and are in no summary", sorted({r[2] for r in qs}), [W_POST, W_PRE])
    ck.eq("the frozen post_reform window holds 38 quarters", len({r["quarter"] for r in qe if r["window"] == W_POST and r["basis"] == "calendar"}), 38)
    ck.ok("a row after 2026Q2 is never frozen; every earlier row is", all((r["frozen"] == "no") == (r["window"] == W_AFTER) for r in qe))
    wrong = [(r["basis"], r["quarter"], r["group"], r["measure"]) for r in qe if r["blind"] != oracle_blind(r)]
    ck.eq("blind follows the rule on every quarter_ends row", wrong[:3], [])
    exp = {}
    for r in qe:
        exp.setdefault((r["basis"], r["window"], r["group"], r["measure"]), []).append(oracle_blind(r))
    bad = [r[:5] for r in qs if r[19] != ("yes" if all(x == "yes" for x in exp[(r[0], r[2], r[3], r[4])]) else "no")]
    ck.eq("a summary row is yes only if every row it is built from is yes", bad[:3], [])
    ck.ok("the calendar and jp_other post_reform summaries are all no: they contain the 2026-06 quarter", all(r[19] == "no" for r in qs if r[2] == W_POST and r[0] in ("calendar", "jp_other")))
    ck.eq("exactly one primary row in qe_summary.csv", [r[:5] for r in qs if r[18] == "yes"], [["calendar", "two_sided", W_POST, "ALL_NONUS", "secured"]])
    early = [dt.date(2020, 1, 31), dt.date(2020, 2, 29), dt.date(2020, 3, 31)]
    ck.eq("row_blind: pre_reform, transition and after_freeze rows are no whatever their months", [row_blind(w, "UK", "unsecured", early) for w in (W_PRE, W_TRANS, W_AFTER)],
          ["no", "no", "no"])
    ck.eq("row_blind: a post_reform row before 2026-06 for a country group is yes", row_blind(W_POST, "UK", "unsecured", early), "yes")
    ck.eq("row_blind: a month from 2026-06 on is no", row_blind(W_POST, "UK", "unsecured", [dt.date(2026, 5, 31), dt.date(2026, 6, 30)]), "no")
    ck.eq("row_blind: ALL_NONUS secured and headline are no, bank_only is yes", [row_blind(W_POST, "ALL_NONUS", m, early) for m in ("secured", "headline", "bank_only")], ["no", "no", "yes"])
    prim = [r for r in qe if r["primary"] == "yes"]
    ck.ok("the primary quarter_ends rows are the 38 ALL_NONUS secured calendar post_reform rows only",
          len(prim) == 38 and all(r["group"] == "ALL_NONUS" and r["measure"] == "secured" and r["basis"] == "calendar" and r["window"] == W_POST for r in prim))


def s11_summary(ck):
    W = get_world()
    c = W["c"]
    rows = summary_rows(c.G, c.F, c.total, c.vints, c.revs, c.qe, c.s1, "v")
    ck.ok("the Q1, Q2, Q6 and Q7 rows are all blind = no", rows and all(r[10] == "no" for r in rows))
    ck.eq("the summary grammar key is unique", len({(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows}), len(rows))
    ck.ok("statistics are in the grammar", {r[6] for r in rows} <= {"level", "pct_of_mmf_total", "pct_of_lineage_total", "change_usd_mn", "change_chg_pct", "change_pp", "hit_rate",
                                                                  "cells_changed", "max_abs_change_usd_mn", "old_month_revised"})


# ---- G12 ---------------------------------------------------------------------------------------------------------------
def t_g12(ck):
    W = get_world()
    ends = feb_endpoints(W["c"].F.months)
    ck.eq("the named endpoints are the Februaries and 2026-08-31", (sorted({d.month for d in ends}), dt.date(2026, 8, 31) in ends), ([2, 8], True))
    ck.ok("no endpoint is a calendar quarter-end month", all(d.month not in (3, 6, 9, 12) for d in ends))
    ck.ok("the 2024-26 endpoints are all mid-quarter", all(d.month not in (3, 6, 9, 12) for d in Q2_ENDPOINTS))
    ck.eq("16 Februaries and one August", len(ends), 17)


# ---- G13 ---------------------------------------------------------------------------------------------------------------
def slim_texts(texts, n=120):
    out = {}
    for k, v in texts.items():
        if k.endswith(".csv"):
            lines = v.split("\n")
            out[k] = "\n".join(lines[:n]) + "\n"
        else:
            out[k] = v
    return out


def t_g13(ck):
    W = get_world()
    ck.eq("the allowlist text hashes to the spec's sha256", allow_problems(), [])
    ck.eq("...and a tampered text does not", bool(allow_problems(SPEC_ALLOW_TEXT.replace("below_nbrs_pct", "dip_pct", 1))), True)
    ck.eq("ten CSV allowlists", len(allowlist()), 10)
    ck.eq("the superseded hash is not the current one", SPEC_ALLOW_SHA256 in SUPERSEDED_ALLOW_SHA256, False)
    if os.path.exists(SPEC_FILE):
        with open(SPEC_FILE, encoding="utf-8") as fh:
            st = fh.read()
        m = re.search(r"```\n(levels_country\.csv:.*?)```", st, re.S)
        ck.ok("the spec's canonical block is the script's text", bool(m) and m.group(1) == SPEC_ALLOW_TEXT)
        ck.ok("...and its printed sha256 is SPEC_ALLOW_SHA256", SPEC_ALLOW_SHA256 in st)
    sl = slim_texts(W["texts"])
    ck.eq("the clean folder passes: names, headers (the '# source:' line is skipped), no duplicate key", leak_problems(sl), [])
    wrong = dict(sl)
    wrong["checks.csv"] = sl["checks.csv"].replace("check_id,description,expected,observed,status", "check_id,description,expected,observed,status,extra")
    ck.ok("an extra column is reported", any("header of checks.csv" in p for p in leak_problems(wrong)))
    wrong["checks.csv"] = sl["checks.csv"].replace("description", "details")
    ck.ok("a renamed column is reported", any("header of checks.csv" in p for p in leak_problems(wrong)))
    eleventh = dict(sl)
    eleventh["extra.csv"] = "a,b\n1,2\n"
    ck.ok("an eleventh csv is reported", any("extra.csv" in p for p in leak_problems(eleventh)))
    dup = dict(sl)
    lines = sl["summary.csv"].split("\n")
    dup["summary.csv"] = "\n".join(lines + [lines[3]]) + "\n"
    ck.ok("a duplicate key in summary.csv is reported", any("duplicate key in summary.csv" in p for p in leak_problems(dup)))
    sh_path = os.path.join(ROOT, "bin", "check.sh")
    if os.path.exists(sh_path):
        with open(sh_path, encoding="utf-8") as fh:
            sh = fh.read()
        ck.eq("bin/check.sh holds its own literal copy of the ten lines", check_sh_problems(sh), [])
        i = sh.find("mmfnb_leak_check()")
        bad = sh[:i] + sh[i:].replace("python3 -c", "python3 bin/mmf_nonus_banks.py ; python3 -c", 1)
        ck.ok("a check.sh whose M23 reads the script is reported", bool(check_sh_problems(bad)))
        ck.ok("a check.sh without one of the lines is reported", bool(check_sh_problems(sh.replace("checks.csv:check_id,description,expected,observed,status", "", 1))))


# ---- G14 ---------------------------------------------------------------------------------------------------------------
def t_g14(ck):
    W = get_world()
    clean = slim_texts(W["texts"])
    ck.eq("the clean folder passes", leak_problems(clean), [])
    bad = dict(clean)
    bad["node.json"] = '{"datatable": {"columns": []}, "highcharts": []}'
    bad["renamed.csv"] = '{"datatable": {"columns": [{"title": "Date"}], "values": []}, "highcharts": []}'
    bad["notes.json"] = '{"a": 1}'
    bad["SOURCES.md"] = clean["SOURCES.md"] + "\nsee /Users/someone/file\n"
    probs = leak_problems(bad)
    ck.ok("any .json file is reported as a raw file, whatever it holds", any("notes.json" in p and "raw file" in p for p in probs), str(probs[:5]))
    ck.ok("a raw node JSON is reported", any("node.json" in p and "raw file" in p for p in probs), str(probs[:4]))
    ck.ok("a node JSON renamed .csv is reported", any("renamed.csv" in p and "raw file" in p for p in probs), str(probs[:4]))
    ck.ok("a /Users/ path in SOURCES is reported", any("SOURCES.md" in p and "local path" in p for p in probs))
    at = dict(clean)
    at["README.md"] = clean["README.md"] + "\nwrite to a" + chr(64) + "b.org\n"
    ck.ok("an at sign is reported", any("at sign" in p for p in leak_problems(at)))
    ck.eq("a first non-comment line starting {\"datatable\" is raw even behind a source line", is_raw_json('# source: x\n{"datatable": {}}'), True)


# ---- G15 ---------------------------------------------------------------------------------------------------------------
def t_g15(ck):
    base = README_S1 + " " + README_S2 + "\n\n" + README_S3 + "\n\n" + README_FICC + "\n\n" + DENIAL + "\n"
    ck.eq("the opening, sentence 3, the FICC sentence and the denial sentence pass", wording_problems("README.md", base), [])
    ck.ok("'because of quarter-end window dressing' fails", bool(wording_problems("README.md", base + "Holdings fell because of quarter-end window dressing.\n")))
    ck.ok("a second sentence with 'flows' fails", bool(wording_problems("README.md", base + "These are flows of funds.\n")))
    ck.ok("'banks pulled back from money funds' fails", bool(wording_problems("README.md", base + "Banks pulled back from money funds.\n")))
    ck.ok("'a dip of 5 log points' fails", bool(wording_problems("README.md", base + "A dip of 5 log points.\n")))
    ck.ok("a second copy of the denial sentence fails: it is allowed once", bool(wording_problems("README.md", base + DENIAL + "\n")))
    ck.eq("SOURCES.md is not scanned", wording_problems("SOURCES.md", "A reviewer wrote that flows drove window dressing."), [])
    ck.eq("the README the build writes passes", wording_problems("README.md", get_world()["texts"]["README.md"]), [])


# ---- G16 ---------------------------------------------------------------------------------------------------------------
BAD_SNIPS = ("os.remove(STOP_PATH)", "os.unlink(os.path.join(cache, STOP_OFR))", "os.replace(tmp, stop_file)", "os.rename(stop_file, other)", "shutil.rmtree(cache)",
             "shutil.move(stop_file, other)", "Path(stop_file).unlink()", "Path(stop_file).rename(other)", "Path(stop_file).write_text('')", "Path(stop_file).write_bytes(b'')",
             "open(stop_file, 'w')", "open(os.path.join(c, 'STOP_ofr'), 'a')", "shutil.rmtree(glob.glob(c + '/*')[0])")
OK_SNIPS = ("open(stop_path, 'x')", "shutil.rmtree(self.partial)", "os.rename(self.partial, final)", "os.replace(tmp, path)")


def fetch_world():
    if not _FW:
        with world_labels():
            nodes = gen_world(months=ALL_MONTHS[-4:])
            _FW.update(nodes=nodes, files=world_files(nodes))
            _FW["V"] = make_vintage(_FW["files"])
    return _FW


_FW = {}


def fetch_rig(tmp, files=None, handler=None, clock=None, **kw):
    files = fetch_world()["files"] if files is None else files
    clock = clock or FakeClock()
    calls = []

    def opener(host, target, headers, timeout, cap):
        calls.append((host, target, dict(headers), clock.wall()))
        clock.tick(0.3)
        if handler:
            r = handler(host, target, len(calls))
            if r is not None:
                return r
        b = files.get((host, target))
        return (200, b, {}) if b is not None else (404, b"<Error>NotFound</Error>", {})
    cache = os.path.join(tmp, "cache")
    fe = Fetcher(cache, os.path.join(tmp, "out"), stop_dirs=[cache], opener=opener, wall=clock.wall, mono=clock.wall, sleeper=clock.sleep,
                 utc=lambda: dt.datetime(2026, 10, 25, 12, 0, tzinfo=dt.timezone.utc), say=lambda *a: None, **kw)
    return fe, calls, clock, cache


def read_stop(path):
    d = {}
    for line in open(path, encoding="utf-8").read().splitlines():
        k, _, v = line.partition(": ")
        d[k] = v
    return d


def t_g16(ck):
    src = own_source()
    ck.eq("this script holds no operation on a STOP path other than exclusive creation", static_stop_problems(src), [])
    for sn in BAD_SNIPS:
        ck.ok("the scan flags: %s" % sn, bool(static_stop_problems("import os, shutil, glob\n" + sn + "\n")))
    for sn in OK_SNIPS:
        ck.eq("the scan allows: %s" % sn, static_stop_problems("x = 1\n" + sn + "\n"), [])
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _c, cache = fetch_rig(tmp)
        os.makedirs(cache)
        p = os.path.join(cache, STOP_OFR)
        with open(p, "x") as fh:
            fh.write("status: 403\n")
        before = sha256_path(p)
        rc = fe.run()
        ck.eq("with a planted STOP_ofr, fetch exits 2", rc, 2)
        ck.eq("...makes no request", calls, [])
        ck.eq("...and leaves the file unchanged", sha256_path(p), before)
    for status, hdr, name in ((403, {}, "403"), (429, {"retry-after": "120"}, "429")):
        with tempfile.TemporaryDirectory() as tmp:
            target = node_url_path((GOV,))
            fe, calls, _c, cache = fetch_rig(tmp, handler=lambda h, t, n, s=status, hd=hdr: (s, b"<Error>Denied</Error>", hd) if t == target else None)
            rc = fe.run()
            sp = os.path.join(cache, STOP_OFR)
            ck.eq("a fixture %s exits 2" % name, rc, 2)
            ck.ok("...and writes STOP_ofr", os.path.exists(sp))
            if os.path.exists(sp):
                f = read_stop(sp)
                ck.eq("...with the five fields", list(f), ["status", "utc_time", "url_path", "retry_after", "body_head"])
                ck.eq("...status and path recorded", (f["status"], f["url_path"], f["retry_after"]), (str(status), target, hdr.get("retry-after", "")))
                ck.ok("...and the body head escaped", "Denied" in f["body_head"])
            ck.eq("...and the target was requested once", sum(1 for c in calls if c[1] == target), 1)
    with tempfile.TemporaryDirectory() as tmp:
        t = api_url_path("MMF-MMF_TOT-M")
        fe, calls, _c, cache = fetch_rig(tmp, handler=lambda h, tg, n: (403, b"no", {}) if tg == t else None)
        rc = fe.run()
        ck.eq("a 403 from the API host writes STOP_api", (rc, os.path.exists(os.path.join(cache, STOP_API)), os.path.exists(os.path.join(cache, STOP_OFR))), (2, True, False))
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _c, cache = fetch_rig(tmp)
        part = os.path.join(cache, "2026-10-15.partial")
        os.makedirs(part)
        write_text(os.path.join(part, REQCOUNT), "%d\n" % (BUDGET - 1))
        rc = fe.run()
        ck.eq("request 3,001 writes STOP_budget and exits 2", (rc, os.path.exists(os.path.join(cache, STOP_BUDGET))), (2, True))
        ck.eq("...after the one updated.json request", len(calls), 1)
        if os.path.exists(os.path.join(cache, STOP_BUDGET)):
            ck.eq("...with the five fields", list(read_stop(os.path.join(cache, STOP_BUDGET))), ["status", "utc_time", "url_path", "retry_after", "body_head"])
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _c, cache = fetch_rig(tmp)
        try:
            fe._latch(STOP_OFR, 403, "/a", "", b"first", "t")
        except Latched:
            pass
        first = open(os.path.join(cache, STOP_OFR)).read()
        try:
            fe._latch(STOP_OFR, 429, "/b", "", b"second", "t")
        except Latched:
            pass
        ck.eq("a second latch never overwrites an existing STOP file", open(os.path.join(cache, STOP_OFR)).read(), first)
    with tempfile.TemporaryDirectory() as tmp:
        target = node_url_path((GOV,))
        fe, calls, _c, cache = fetch_rig(tmp, handler=lambda h, t, n: (200, b"<html>not json</html>", {}) if t == target else None)
        rc = fe.run()
        ck.eq("a 200 body that fails its content test latches STOP_ofr", (rc, os.path.exists(os.path.join(cache, STOP_OFR))), (2, True))


# ---- G17 ---------------------------------------------------------------------------------------------------------------
def s17_host(ck):
    for h, t in (("www.sec.gov", "/cgi-bin/browse-edgar"), ("fred.stlouisfed.org", "/graph/fredgraph.csv"), ("data.sec.gov", "/x.json"), ("www.example.com", MON_BASE + "asof.json")):
        ck.raises("%s is refused before the request" % h, Refused, lambda h=h, t=t: check_url(h, t))
    ck.raises("the complete-dataset zip is never requested", Refused, lambda: check_url(HOST_WWW, MON_BASE + "mmf_data.zip"))
    ck.raises("...in any letter case", Refused, lambda: check_url(HOST_WWW, MON_BASE + "MMF_DATA.ZIP"))
    ck.raises("...and not as a path segment of a chart-file path either", Refused, lambda: check_url(HOST_WWW, MON_BASE + "credit_risks_country/mmf_data.zip/data.json"))
    ck.raises("a POST is refused", Refused, lambda: check_url(HOST_WWW, UPDATED_PATH, "POST"))
    ck.raises("an unknown API series is refused", Refused, lambda: check_url(HOST_API, "/v1/series/full?mnemonic=FNYR-SOFR-A"))
    check_url(HOST_WWW, node_url_path((GOV, "Europe")))
    check_url(HOST_API, api_url_path("MMF-MMF_TOT-M"))
    ck.ok("allowed requests pass", True)
    ck.raises("an identification string holding an at sign is refused", Refused, lambda: assert_ua(UA.replace(")", "; me" + chr(64) + "x.org)")))
    ck.ok("the identification string is the neutral one and holds no at sign", UA.endswith("non-commercial research)") and chr(64) not in UA)
    ck.raises("--sleep below 2 s is refused", Refused, lambda: Fetcher(tempfile.gettempdir(), None, sleep=1.0))


HDR_KEY = "User" + "-Agent"


def crawl_ok(ck, tmp, **kw):
    fe, calls, clock, cache = fetch_rig(tmp, **kw)
    rc = fe.run()
    return fe, calls, clock, cache, rc


def s17_crawl(ck):
    F = fetch_world()
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock, cache, rc = crawl_ok(ck, tmp)
        ck.eq("a full crawl of the synthetic monitor completes", rc, 0)
        paths = [c[1] for c in calls]
        hosts = {c[0] for c in calls}
        ck.ok("every host is on the allowlist", hosts <= HOST_ALLOW)
        ck.ok("the zip is never requested", not any("mmf_data.zip" in p for p in paths))
        ck.ok("no request carries an at sign and every request carries the neutral string", all(c[2][HDR_KEY] == UA and chr(64) not in c[2][HDR_KEY] for c in calls))
        gaps = [b[3] - a[3] for a, b in zip(calls, calls[1:])]
        ck.ok("requests are at least 2 s apart", gaps and min(gaps) >= 2.0, "smallest gap %.2f" % (min(gaps) if gaps else -1))
        ck.ok("no US parent is drilled (FICC included)", not any("/usa/financial_institution/" in p and not p.endswith("/usa/financial_institution/data.json") for p in paths))
        ck.ok("no non-financial sector is drilled", not any(re.search(r"/(japan|france|germany|usa|canada)/(government|non-financial_corporate)/", p) for p in paths))
        ficc = [p for p in paths if p.endswith("/usa/financial_institution/data.json")]
        ck.eq("the USA financial-institution file is fetched for the categories that have one only", len(ficc), len({p for p in ficc}))
        ck.ok("...and never for a category with no nonzero month", not any("fees_%26_gates" in p or "/prime/" in p or "/tax_exempt/" in p for p in ficc), str(ficc))
        want = {node_url_path(p) for p in F["V"].nodes}
        got = {p for p in paths if p.startswith(MON_BASE + ROOT_DIR)}
        ck.eq("exactly the frontier's node files were requested, none twice", (got == want, len([p for p in paths if p.startswith(MON_BASE + ROOT_DIR)]) == len(want)), (True, True))
        folder = os.path.join(cache, "2026-10-15")
        ck.ok("the folder is complete and named by the updated.json date", os.path.isdir(folder) and not os.path.exists(folder + ".partial"))
        if os.path.isdir(folder):
            V = load_vintage(folder)
            ck.eq("the cached vintage reloads and walks to the same tree", len(V.nodes), len(F["V"].nodes))
            ck.eq("requests counted: every node, asof, four API series, updated.json twice", V.requests, len(want) + 1 + 4 + 2)
        sync = open(os.path.join(tmp, "out", "fetch_log.csv"), encoding="utf-8").read()
        ck.ok("the committed log lists every request", sync.count("\n") >= len(calls) + 2)


def s17_retry(ck):
    with tempfile.TemporaryDirectory() as tmp:
        target = node_url_path((GOV,))
        fe, calls, _c, cache = fetch_rig(tmp, handler=lambda h, t, n: (429, b"slow down", {"retry-after": "1"}) if t == target else None)
        rc = fe.run()
        ck.eq("a 429 is not retried", (rc, sum(1 for c in calls if c[1] == target)), (2, 1))


def s17_redirect(ck):
    with tempfile.TemporaryDirectory() as tmp:
        target = node_url_path((GOV,))
        other = node_url_path(("Prime",))
        fe, calls, _c, cache = fetch_rig(tmp, handler=lambda h, t, n: (302, b"", {"location": other}) if t == target else None)
        rc = fe.run()
        ck.eq("a redirect is not followed and latches", (rc, os.path.exists(os.path.join(cache, STOP_OFR)), sum(1 for c in calls if c[1] == other)), (2, True, 0))


def s17_recrawl(ck):
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock, cache, rc = crawl_ok(ck, tmp)
        n1 = len(calls)
        fe2, calls2, _c2, cache2 = fetch_rig(tmp, clock=clock)
        rc2 = fe2.run()
        ck.eq("a second fetch for a key already complete reads updated.json only and exits 0", (rc2, len(calls2)), (0, 1))
        ck.ok("...and the complete folder is untouched", os.path.isdir(os.path.join(cache, "2026-10-15")))


def s17_resume(ck):
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock, cache = fetch_rig(tmp, max_requests=20)
        rc = fe.run()
        ck.eq("a run with a request cap ends in a slice (exit 3)", rc, 3)
        man = {r[0] for r in read_manifest(os.path.join(cache, "2026-10-15.partial"))}
        ck.ok("...with a manifest of what landed", len(man) >= 10)
        fe2, calls2, _c, _cache = fetch_rig(tmp, clock=clock)
        rc2 = fe2.run()
        ck.eq("the resumed run completes", rc2, 0)
        again = [c[1] for c in calls2 if c[1] in man and c[1] != UPDATED_PATH]
        ck.eq("...and requests no path already in the manifest", again, [])
        allp = [c[1] for c in calls + calls2 if c[1] != UPDATED_PATH]
        ck.eq("...so no path is requested twice across the two runs", len(allp), len(set(allp)))


def s17_changed(ck):
    with tempfile.TemporaryDirectory() as tmp:
        files = dict(fetch_world()["files"])
        state = {"n": 0}

        def handler(h, t, n):
            if t == UPDATED_PATH:
                state["n"] += 1
                if state["n"] >= 2:
                    return 200, json.dumps({"updated": "November 18, 2026"}).encode(), {}
            return None
        fe, calls, _c, cache = fetch_rig(tmp, files=files, handler=handler)
        rc = fe.run()
        ck.eq("a release that changed during the crawl exits 2", rc, 2)
        ck.ok("...removes that partial folder and keeps no vintage", not os.path.exists(os.path.join(cache, "2026-10-15.partial")) and not os.path.exists(os.path.join(cache, "2026-10-15")))


def t_g17(ck):
    s17_host(ck)
    s17_crawl(ck)
    s17_retry(ck)
    s17_redirect(ck)
    s17_recrawl(ck)
    s17_resume(ck)
    s17_changed(ck)


# ---- G18 ---------------------------------------------------------------------------------------------------------------
_W2 = {}


def get_w2():
    if not _W2:
        with world_labels():
            nodes2 = gen_world(months=ALL_MONTHS[-4:], revise=("Credit Agricole", "Treasury Repurchase Agreement", ALL_MONTHS[-3], 987654321012))
            files2 = world_files(nodes2, updated="November 18, 2026")
            V1 = fetch_world()["V"]
            V2 = make_vintage(files2, key="2026-11-18")
            _W2.update(V1=V1, V2=V2, c1=vintage_cells(V1), c2=vintage_cells(V2))
    return _W2


def s18_rev(ck):
    W = get_w2()
    cells = {W["V1"].key: W["c1"], W["V2"].key: W["c2"]}
    rows = all_revisions([W["V1"], W["V2"]], cells)
    ck.ok("the revised cell appears in revisions.csv", any(r[3] == "France" and r[4] == "repo_treasury" for r in rows), str(rows[:2]))
    stale = ["2020-01-01", "2020-02-01", "2019-01-31", "Japan", "cd", "1.0", "2.0", "1.0"]
    again = all_revisions([W["V1"], W["V2"]], cells, [stale])
    ck.eq("revisions are regenerated from all cached pairs, never merged with a committed file", again, rows)
    ck.eq("one vintage gives no revision rows", all_revisions([W["V1"]], {W["V1"].key: W["c1"]}), [])


def s18_order(ck):
    W = get_w2()
    V1, V2 = W["V1"], W["V2"]
    ck.eq("two ordered vintages pass", vintage_order_problems([V1, V2]), [])
    old = Vintage()
    old.__dict__.update(V2.__dict__)
    old.asof = dt.date(2026, 8, 31)
    ck.ok("an asof earlier than the previous vintage's is reported", bool(vintage_order_problems([V1, old])))
    committed = [[V1.key, "2026-10-15", "2026-09-30", "1", "1", "0" * 64, "ok", "k"]]
    ck.ok("the same key with a different manifest sha256 is reported", bool(vintage_order_problems([V1, V2], committed)))
    same = [[V1.key, "2026-10-15", "2026-09-30", "1", "1", V1.manifest_sha, "ok", "k"]]
    ck.eq("...and the same key with the same manifest is fine", vintage_order_problems([V1, V2], same), [])


def s18_partial(ck):
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "2026-10-15.partial"))
        ck.eq("a .partial folder is not a vintage", vintage_dirs(tmp), [])
        os.makedirs(os.path.join(tmp, "2026-09-15"))
        ck.eq("a complete folder is", vintage_dirs(tmp), ["2026-09-15"])
        ck.raises("...and load_vintage refuses a .partial folder", DataError, lambda: load_vintage(os.path.join(tmp, "2026-10-15.partial")))


def s18_key(ck):
    _CLOCK_OVERRIDE.append(dt.datetime(2026, 10, 25, 3, 0, tzinfo=dt.timezone.utc))
    try:
        with tempfile.TemporaryDirectory() as tmp:
            fe, calls, clock, cache, rc = crawl_ok(ck, tmp)
            ck.eq("the vintage key is the updated.json date, not the clock's", (rc, os.path.isdir(os.path.join(cache, "2026-10-15"))), (0, True))
    finally:
        _CLOCK_OVERRIDE.pop()


def t_g18(ck):
    s18_rev(ck)
    s18_order(ck)
    s18_partial(ck)
    s18_key(ck)


# ---- G19 ---------------------------------------------------------------------------------------------------------------
def t_g19(ck):
    W = get_world()
    F = W["c"].F
    keys = parent_kind_keys(F)
    kt = kind_table_sha(W_KINDS)
    ck.eq("every parent has a kind and the table hashes to the constant: no problem", kind_gate_problems(keys, W_KINDS, kt), [])
    short = dict(W_KINDS)
    short.pop(("Barclays PLC", "UK"))
    ck.ok("a parent without a kind is reported", bool(kind_gate_problems(keys, short, kind_table_sha(short))))
    ck.ok("a kind table whose sha256 differs from the constant is reported", bool(kind_gate_problems(keys, W_KINDS, "0" * 64)))
    ck.ok("an unset constant is reported", bool(kind_gate_problems(keys, W_KINDS, "")))
    G, _cm = group_levels(F, W_KINDS)
    d = W["V"].asof
    ps = parent_series(F)
    exp = sum(ps[(c, p)].get(d, Decimal(0)) for (p, c), k in W_KINDS.items() if k == "bank" and (c, p) in ps)
    ck.ok("Axa SA (insurer) and Nomura Holdings (broker-dealer) have positive holdings in the world", ps[("France", "Axa SA")][W["V"].nodes[()].dates[5]] > 0 and ps[("Japan", "Nomura Holdings")][dt.date(2020, 1, 31)] > 0)
    ck.eq("bank_only counts bank parents only: no insurer, no broker-dealer", G[("ALL_NONUS", "bank_only", "all")].get(d, Decimal(0)), exp)
    d2 = dt.date(2026, 8, 31)
    exp2 = sum(ps[(c, p)].get(d2, Decimal(0)) for (p, c), k in W_KINDS.items() if k == "bank" and (c, p) in ps)
    ck.ok("Axa SA holds something on 2026-08-31", ps[("France", "Axa SA")].get(d2, Decimal(0)) > 0)
    ck.eq("...and bank_only leaves it out on that month too", G[("ALL_NONUS", "bank_only", "all")].get(d2, Decimal(0)), exp2)
    ck.ok("bank_only is below the headline", G[("ALL_NONUS", "bank_only", "all")][d] < G[("ALL_NONUS", "headline", "all")][d])
    rows = parents_rows(F, W_KINDS, d, "v")
    n_cols = len(allowlist()["parents.csv"])
    ck.ok("parents.csv rows carry exactly the allowlisted columns: no quarter-end column", all(len(r) == n_cols for r in rows))
    head = W["texts"]["parents.csv"].split("\n")[1]
    ck.ok("...and its header names no quarter-end figure", "quarter" not in head and "below" not in head and "chg" not in head)


# ---- G20 ---------------------------------------------------------------------------------------------------------------
def t_g20(ck):
    W = get_world()
    c = W["c"]
    G, cm = group_levels(c.F, W_KINDS)
    ck.eq("the nine groups sum to ALL_NONUS in every month, measure and lineage", group_sum_problems(G), [])
    lg = levels_group_rows(G, c.F, c.total, "v")
    lc = levels_country_rows(c.F, cm, G, c.total, "v")
    ck.ok("every share in levels_group.csv is within 0-100", all(0 <= Decimal(x) <= 100 for r in lg for x in (r[5], r[6]) if x != ""))
    ck.ok("...and in levels_country.csv", all(0 <= Decimal(x) <= 100 for r in lc for x in (r[5], r[6]) if x != ""))
    d = c.V.asof
    row = next(r for r in lc if r[0] == d.isoformat() and r[1] == "Japan" and r[3] == "total")
    want = dstr(Decimal(100) * c.cm["Japan"]["headline"]["all"][d] / G[("ALL_NONUS", "headline", "all")][d], 3)
    ck.eq("pct_of_nonus_fi is the country over the ALL_NONUS headline, not over bank_only", row[6], want)
    r2 = next(r for r in lg if r[0] == d.isoformat() and r[1] == "JP" and r[2] == "all" and r[3] == "headline")
    ck.eq("pct_of_mmf_total is the value over all US money funds", r2[5], dstr(Decimal(100) * c.cm["Japan"]["headline"]["all"][d] / c.total[d], 3))
    ck.eq("share_problems finds no breach in the clean world", share_problems(c), [])


# ---- the builds, end to end --------------------------------------------------------------------------------------------
def write_vintage_to_cache(cache, files, key="2026-10-15"):
    """What a completed crawl leaves in the cache: only the files the frontier reaches (the synthetic OFR also serves files fetch never asks for)."""
    folder = os.path.join(cache, key)
    os.makedirs(folder, exist_ok=True)
    rows = []
    reach = {node_url_path(p) for p in make_vintage(files).nodes}
    for (h, u), b in sorted(files.items()):
        if u.startswith(MON_BASE + ROOT_DIR) and u not in reach:
            continue
        write_bytes(os.path.join(folder, file_name(u)), b)
        rows.append([u, sha256_of(b), str(len(b))])
    for r in rows:
        append_csv(os.path.join(folder, MANIFEST), r)
    write_text(os.path.join(folder, REQCOUNT), "412\n")
    append_csv(os.path.join(folder, VLOG), ["2026-10-25T10:00:00.000Z", HOST_WWW, UPDATED_PATH, "200", "28", "0" * 64])


class _Args:
    pass


def t_x_build(ck):
    W = get_world()
    c, texts = W["c"], W["texts"]
    ck.eq("the clean build's folder passes every guard (twelve names, headers, no duplicate key, no raw file, no local path, no at sign, README wording)", leak_problems(texts), [])
    bad = [r for r in c.checks if r[4] == "FAIL"]
    ck.eq("no check FAILs on the synthetic world", [(r[0], r[3][:80]) for r in bad], [])
    ids = {r[0] for r in c.checks}
    ck.ok("the spec's checks are all present", {"C01a", "C02a", "C03a", "C04", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "S1"} <= ids, str(sorted(ids)))
    ck.eq("C12: a second build is identical", [r[4] for r in c.checks if r[0] == "C12"], ["PASS"])
    ck.eq("C15: the kind gate", [r[4] for r in c.checks if r[0] == "C15"], ["PASS"])
    ck.eq("C07 and C08 pass on the 189-month category structure", sorted((r[0], r[4]) for r in c.checks if r[0] in ("C07", "C08")), [("C07", "PASS"), ("C08", "PASS")])
    ck.eq("the opening and sentence 3 are in the README", (README_S1 in texts["README.md"], README_S2 in texts["README.md"], README_S3 in texts["README.md"], README_FICC in texts["README.md"]),
          (True, True, True, True))
    ck.ok("the README names the single primary row before everything else", "The single primary row" in texts["README.md"] and "exploratory" in texts["README.md"])
    ck.ok("the README never mentions the question numbers", not re.search(r"\bQ[1-7]\b", texts["README.md"]))
    ck.ok("every csv begins with one # source: line", all(t.split("\n")[0].startswith("# source:") and not t.split("\n")[1].startswith("# source:") for k, t in texts.items() if k.endswith(".csv") and k != "fetch_log.csv"))
    with tempfile.TemporaryDirectory() as tmp:
        cache = os.path.join(tmp, "cache")
        write_vintage_to_cache(cache, W["files"])
        a = _Args()
        a.cache, a.out = cache, os.path.join(tmp, "out")
        out = []
        rc0 = run_build(a, say=lambda *x: out.append(" ".join(map(str, x))))
        ck.eq("build with an unreviewed kind table (KIND_TABLE_SHA256 unset) exits 2 before writing any output", (rc0, os.path.exists(a.out)), (2, False))
        old = (KIND_TABLE.copy(), globals()["KIND_TABLE_SHA256"], globals()["PIN_TABLE"])
        KIND_TABLE.clear()
        KIND_TABLE.update(W_KINDS)
        globals()["KIND_TABLE_SHA256"] = kind_table_sha(W_KINDS)
        globals()["PIN_TABLE"] = W["pins"]
        try:
            with world_labels():
                out1 = []
                rc1 = run_build(a, say=lambda *x: out1.append(" ".join(map(str, x))))
                h1 = {n: sha256_path(os.path.join(a.out, n)) for n in sorted(os.listdir(a.out))}
                rc2 = run_build(a, say=lambda *x: None)
                h2 = {n: sha256_path(os.path.join(a.out, n)) for n in sorted(os.listdir(a.out))}
        finally:
            KIND_TABLE.clear()
            KIND_TABLE.update(old[0])
            globals()["KIND_TABLE_SHA256"] = old[1]
            globals()["PIN_TABLE"] = old[2]
        ck.eq("build from a cached vintage exits 0 (WARN allowed)", rc1, 0)
        ck.eq("...writes the twelve files", sorted(h1), sorted(COMMITTED_NAMES + DOC_NAMES))
        ck.eq("a second build leaves every sha256 unchanged", h1, h2)
        ck.eq("...and matches the in-process texts", {n: sha256_of(texts[n].encode()) for n in h1 if n != "fetch_log.csv"}, {n: v for n, v in h1.items() if n != "fetch_log.csv"})
        b = _Args()
        b.cache, b.out = cache, os.path.join(tmp, "out2")
        KIND_TABLE.clear()
        KIND_TABLE.update(W_KINDS)
        try:
            outk = []
            rck = run_kinds(b, say=lambda *x: outk.append(" ".join(map(str, x))))
        finally:
            KIND_TABLE.clear()
            KIND_TABLE.update(old[0])
        ck.eq("kinds exits 0 and writes parents.csv only", (rck, sorted(os.listdir(b.out))), (0, ["parents.csv"]))
        ck.ok("...with no quarter-end column and the parent list printed", "quarter" not in open(os.path.join(b.out, "parents.csv")).read().split("\n")[1] and any("BNP Paribas" in x for x in outk))


# ---- the guards --------------------------------------------------------------------------------------------------------
GUARDS = [
    ("G1", "path encoding", ["g1_quote_plus", "g1_plus_raw", "g1_amp_raw", "g1_comma_raw", "g1_paren_enc", "g1_first_space", "g1_nbsp", "g1_dup_ok"], t_g1),
    ("G2", "node identities", ["g2_drop_child", "g2_double_child", "g2_tol_5", "g2_dt_skip"], t_g2),
    ("G3", "category lineage", ["g3_gov_pre_only", "g3_omit_fg", "g3_both_ok", "g3_fill_zero"], t_g3),
    ("G4", "total cross-check", ["g4_tol_0p1pct", "g4_no_check"], t_g4),
    ("G5", "country map", ["g5_unknown_ok", "g5_uk_in_ea", "g5_us_nonus", "g5_supra_in", "g5_substring", "g5_fr_in_all", "g5_ficc_in_all"], t_g5),
    ("G6", "sector", ["g6_gov_counted", "g6_nfc_counted"], t_g6),
    ("G7", "instruments", ["g7_unknown_ok", "g7_abcp_unsecured", "g7_misc_unsecured", "g7_repo_unsecured", "g7_identity_broken", "g7_one_at_a_time"], t_g7),
    ("G8", "numbers", ["g8_float_sum", "g8_thousands", "g8_bn_in_mn", "g8_round_before_sum", "g8_log_on_rounded", "g8_wrong_decimals"], t_g8),
    ("G9", "dates", ["g9_local_tz", "g9_day_first", "g9_nonmonthend_ok"], t_g9),
    ("G10", "quarter-end arithmetic", ["g10_chg_in_only", "g10_prev_qe_nbr", "g10_ca_two_sided", "g10_ca_next_qe", "g10_jp_march_not_march", "g10_inf_not_blank", "g10_clean_touch_qe",
                                       "g10_no_sqrt2", "g10_sqrt2_one_sided", "g10_sd_ddof0", "g10_se_threshold_sd", "g10_n8_off", "g10_paired_unpaired"], t_g10),
    ("G11", "windows and blind", ["g11_transition_in_summary", "g11_post2026_frozen", "g11_blind_pre_reform", "g11_blind_transition", "g11_blind_after_freeze", "g11_blind_2026",
                                  "g11_blind_allnonus", "g11_summary_yes_from_no", "g11_two_primary", ("g11_blind_q", s11_summary)], t_g11),
    ("G12", "endpoints", ["g12_qe_endpoint"], t_g12),
    ("G13", "allowlists", ["g13_extra_col", "g13_renamed", "g13_spec_hash_bad", "g13_source_as_header", "g13_eleventh_csv", "g13_check_reads_script", "g13_dup_summary_key"], t_g13),
    ("G14", "leak guard", ["g14_json_ok", "g14_renamed_ok", "g14_path_ok"], t_g14),
    ("G15", "wording", ["g15_scan_off", "g15_denial_everywhere", "g15_only_causal"], t_g15),
    ("G16", "STOP latch", ["g16_scan_off", "g16_scan_skip_rename", "g16_scan_allow_w", "g16_no_latch_403", "g16_no_budget", "g17_stop_ignored"], t_g16),
    ("G17", "fetch safety", [("g17_host_off", s17_host), ("g17_zip_ok", s17_host), ("g17_ua_check_off", s17_host), ("g17_redirect_ok", s17_redirect), ("g17_pacing_off", s17_crawl),
                             ("g17_retry", s17_retry), ("g17_drill_us", s17_crawl), ("g17_drill_nonfin", s17_crawl), ("g17_all_ficc_cats", s17_crawl), ("g17_recrawl", s17_recrawl),
                             ("g17_refetch_manifest", s17_resume), ("g17_keep_changed", s17_changed)], t_g17),
    ("G18", "vintages and revisions", [("g18_revisions_incremental", s18_rev), ("g18_same_key_ok", s18_order), ("g18_partial_vintage", s18_partial), ("g18_key_clock", s18_key),
                                       ("g18_earlier_asof_ok", s18_order)], t_g18),
    ("G19", "kind", ["g19_missing_kind_ok", "g19_hash_ignored", "g19_insurer_bank", "g19_broker_bank", "g19_parents_qe_col"], t_g19),
    ("G20", "shares and sums", ["g20_pct_units", "g20_all_skips_other", "g20_nonus_den_bank"], t_g20),
    ("X", "build end to end, kinds, determinism", [], t_x_build),
]


def run_test(fn):
    ck = Checks()
    try:
        with world_labels():
            fn(ck)
    except Exception as e:                      # a test that crashes under a mutant has noticed it
        ck.ok("test ran to completion", False, "%s: %s" % (type(e).__name__, e))
    return ck


def mut_parts(m):
    return (m, None) if isinstance(m, str) else m


def selftest(mutants=True, only=None):
    t0 = time.time()
    with world_labels():
        get_world()                              # built first, with no mutant active
        fetch_world()
        get_w2()
    bad_total, n_checks, n_mut = 0, 0, 0
    if only:
        names = {mut_parts(m)[0] for _, _, ms, _ in GUARDS for m in ms}
        if only not in names:
            print("unknown mutant %r" % only)
            return 2
        with mutant(only):
            for gid, desc, muts, fn in GUARDS:
                over = {mut_parts(m)[0]: mut_parts(m)[1] for m in muts}
                if only not in over:
                    continue
                ck = run_test(over[only] or fn)
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
                name, override = mut_parts(m)
                with mutant(name):
                    mk = run_test(override or fn)
                caught = bool(mk.failed())
                n_mut += 1
                bad_total += 0 if caught else 1
                print("       mutant %-30s %s%s" % (name, "caught" if caught else "NOT CAUGHT", "  (first failing check: %s)" % mk.failed()[0][0][:70] if caught else ""))
    print("selftest: %d guards, %d checks, %d mutants applied one at a time, %d failure(s), %.1f s" % (len(GUARDS), n_checks, n_mut, bad_total, time.time() - t0))
    return 0 if bad_total == 0 else 1


def write_fixture(dest):
    """The clean synthetic output folder, for showing that bin/check.sh M23 passes on it and fires on a planted copy."""
    W = get_world()
    for name, text in W["texts"].items():
        write_text(os.path.join(dest, name), text)
    print("wrote %d files to %s" % (len(W["texts"]), dest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
