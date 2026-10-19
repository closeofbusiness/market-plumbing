#!/usr/bin/env python3
"""UK customs export declarations of semi-manufactured gold (CN 71081310) to China and Hong Kong. Python 3 standard library only.

  python3 bin/uk_gold_exports.py fetch [--source all|hmrc|comtrade] [--comtrade-max 200] [--sleep-hmrc 2.05] [--sleep-comtrade 6.05]   # the only network command
  python3 bin/uk_gold_exports.py build [--out DIR] [--cache DIR]                                                                   # offline; byte-identical on re-run
  python3 bin/uk_gold_exports.py selftest [--no-mutants] [--mutant NAME]                                                          # synthetic data only; no network

Specification: _research/2026-10-19-UK-Gold-Exports-China-HK-Spec.md (committed at 2e8c81a, with its supervisor rulings; where rounds differ the latest
round is applied). Outputs: data/uk_gold_exports/ (eight CSVs, README.md, SOURCES.md).

WHAT TOUCHES THE NETWORK. Only `fetch`. Two hosts: api.uktradeinfo.com (HMRC Overseas Trade Statistics) and comtradeapi.un.org (the keyless public
preview). Any other host is refused before a request is made. GET only, one request at a time, no redirect followed, the CLAUDE.md non-SEC
identification string (no address, no name). HMRC at least 2 s apart and at most 12 requests a run; Comtrade at least 6 s apart and at most
--comtrade-max (200) a run. Any status other than 200, or a body that fails its content test, writes STOP_hmrc or STOP_comtrade in
data/vintages/uk_gold_exports/ and ends that source's fetch. Nothing retries and nothing routes around a refusal. This script never deletes, renames
over or truncates a STOP file; only a person deletes one.

WHAT IT MEASURES. Kilograms of declared net mass on UK export declarations (non-EU exports) to China and Hong Kong, from HMRC. It is a
physical-movement series. It counts declared shipments, not buyers. Swiss, SAFE and World Gold Council figures are printed as separate magnitudes and no
ratio, multiple or share of any two of them is computed anywhere.
"""
import argparse
import calendar
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
from urllib.parse import quote, unquote, urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(ROOT, "data", "uk_gold_exports")
CACHE_DEFAULT = os.path.join(ROOT, "data", "vintages", "uk_gold_exports")
LEDGER_ANNUAL_DEFAULT = os.path.join(ROOT, "data", "gold", "ledger_annual_reconciliation.csv")
LEDGER_MONTHLY_DEFAULT = os.path.join(ROOT, "data", "gold", "ledger_monthly.csv")
STOP_DIR = CACHE_DEFAULT                      # fixed, whatever --cache says: a latch cannot be dodged by pointing the cache elsewhere

UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
HEADERS = {"User-Agent": UA, "Accept-Encoding": "identity", "Accept": "application/json"}
HMRC_HOST, CT_HOST = "api.uktradeinfo.com", "comtradeapi.un.org"
HOST_ALLOW = frozenset({HMRC_HOST, CT_HOST})
HMRC_SLEEP, HMRC_MAX = 2.05, 12
CT_SLEEP, CT_MAX = 6.05, 200
HMRC_MIN_SLEEP, CT_MIN_SLEEP = 2.0, 6.0
TIMEOUT = 120
BODY_CAP = 64 * 1024 * 1024
ERR_CAP = 4096

# ------------------------------------------------------------------------------------------------------------------------
# spec constants
# ------------------------------------------------------------------------------------------------------------------------
FIRST_MONTH = "2005-01"
SPECIAL_FROM = "2016-05"                      # general trade before, special trade from
SWISS_SCAN_FROM = "2012-01"
PIN_VINTAGE_END = dt.date(2026, 11, 12)       # HMRC's next release: a pin is a one-vintage check until then
PROVISIONAL_MONTHS = 18
CODES = {71081100: "powder", 71081200: "other", 71081380: "other", 71081310: "cn71081310"}
MONETARY = 71082000
KNOWN_CODES = frozenset(set(CODES) | {MONETARY})
SERIES = ("cn71081310", "other", "powder")
PARTNER_IDS = {720: "CN", 740: "HK", 39: "CH"}
CONFIDENTIAL_FROM = 950
PARTNERS = ("CN", "HK", "CN_HK", "CH", "ALL_NON_EU")
BASE_PARTNERS = ("CN", "HK", "CH", "ALL_NON_EU")
OTS_FIELDS = ("MonthId", "FlowTypeId", "SuppressionIndex", "CommodityId", "CommoditySitcId", "CountryId", "PortId", "Value", "NetMass", "SuppUnit")
OTS_FILTER = "CommodityId ge 71080000 and CommodityId le 71089999 and FlowTypeId eq 4"
APPLY_Q = ("filter(CommodityId eq 71081310 and CountryId eq 720 and FlowTypeId eq 4 and MonthId ge 202401 and MonthId le 202412)"
           "/groupby((MonthId),aggregate(NetMass with sum as kg))")
OZ_PER_KG = 32.1507466
PRICE_LO, PRICE_HI = 150.0, 6000.0
CT_REPORTER_CH, CT_REPORTER_UK = 757, 826
CT_PARTNER_IDS = {156: "CN", 344: "HK"}
SWISS_PINS_M = {"2024-01": {"CN": 77807, "HK": 44573}, "2014-01": {"CN": 12000, "HK": 84628}, "2013-12": {"CN": 11000, "HK": 67826}}
SWISS_PINS_A = {2024: {"CN": 336327, "HK": 90145}}
REQUIRED_OPEN = ("This table counts the kilograms of gold that UK customs export declarations sent to China and Hong Kong each month, from HMRC trade "
                 "statistics. It counts declared shipments, not buyers, and it is not a measure of central-bank buying.")
REQUIRED_SENTENCE = "It counts declared shipments, not buyers, and it is not a measure of central-bank buying."
DENIAL_SENTENCE = ("From May 2016 warehouse and free-zone movements are outside the figures, so this series is not an upper bound, ceiling or cap on "
                   "metal leaving the UK.")
TARIFF_TEXT = "semi-manufactured gold (bars, rods, wire, sections, plates, sheets and strips over 0.15 mm)"

# ------------------------------------------------------------------------------------------------------------------------
# the output allowlists: the spec's canonical text, typed here a second time, and its sha256 as the spec prints it
# ------------------------------------------------------------------------------------------------------------------------
MONTHLY_COLS = ["month", "partner", "series", "net_mass_kg", "supp_unit_div_1000", "rows_n", "status", "trade_system", "provisional", "vintage"]
ANNUAL_COLS = ["year", "partner", "series", "net_mass_kg", "net_mass_kg_known_months", "months_n", "months_blank", "trade_system", "provisional_months", "vintage"]
SWISS_COLS = ["year", "partner", "hs6", "net_mass_kg", "net_mass_kg_known_months", "months_n", "months_blank", "net_wgt_estimated_months", "status",
              "comtrade_annual_kg", "monthly_sum_minus_annual_kg"]
CONTEXT_COLS = ["window", "months", "months_blank", "trade_system", "uk_71081310_cn_hk_t", "uk_71081310_cn_t", "uk_71081310_hk_t", "swiss_710812_cn_hk_t",
                "safe_reported_change_t", "wgc_central_banks_t", "wgc_minus_imf_gap_t", "note"]
REVISION_COLS = ["vintage_prev", "vintage_new", "month", "partner", "series", "kg_prev", "kg_new", "change_kg", "provisional_at_prev"]
SUMMARY_COLS = ["question", "window", "partner", "series", "statistic", "value", "blind", "notable"]
CHECK_COLS = ["check_id", "description", "expected", "observed", "status"]
LOG_COLS = ["utc_time", "host", "path_and_query", "status", "bytes", "sha256"]
ALLOW_ORDER = ("monthly.csv", "annual.csv", "swiss_mirror_annual.csv", "context.csv", "revisions.csv", "summary.csv", "checks.csv", "fetch_log.csv")
ALLOW = {"monthly.csv": MONTHLY_COLS, "annual.csv": ANNUAL_COLS, "swiss_mirror_annual.csv": SWISS_COLS, "context.csv": CONTEXT_COLS,
         "revisions.csv": REVISION_COLS, "summary.csv": SUMMARY_COLS, "checks.csv": CHECK_COLS, "fetch_log.csv": LOG_COLS}
SPEC_ALLOW_TEXT = (
    "monthly.csv:month,partner,series,net_mass_kg,supp_unit_div_1000,rows_n,status,trade_system,provisional,vintage\n"
    "annual.csv:year,partner,series,net_mass_kg,net_mass_kg_known_months,months_n,months_blank,trade_system,provisional_months,vintage\n"
    "swiss_mirror_annual.csv:year,partner,hs6,net_mass_kg,net_mass_kg_known_months,months_n,months_blank,net_wgt_estimated_months,status,comtrade_annual_kg,monthly_sum_minus_annual_kg\n"
    "context.csv:window,months,months_blank,trade_system,uk_71081310_cn_hk_t,uk_71081310_cn_t,uk_71081310_hk_t,swiss_710812_cn_hk_t,safe_reported_change_t,wgc_central_banks_t,wgc_minus_imf_gap_t,note\n"
    "revisions.csv:vintage_prev,vintage_new,month,partner,series,kg_prev,kg_new,change_kg,provisional_at_prev\n"
    "summary.csv:question,window,partner,series,statistic,value,blind,notable\n"
    "checks.csv:check_id,description,expected,observed,status\n"
    "fetch_log.csv:utc_time,host,path_and_query,status,bytes,sha256\n")
SPEC_ALLOW_SHA256 = "966c81ab0f63f5dc04100f57f83ae3af9df4cb80e4e4dcd2d9376f214be65796"
COMMITTED = tuple(ALLOW_ORDER) + ("README.md", "SOURCES.md")
BANNED_COL_RX = re.compile(r"multiple|ratio|share|_over_|pct|exceed", re.I)

# wording guards (G12). CAUSAL_RX is bin/hedged_ust_yield.py's final pattern, copied and not imported.
CAUSAL_RX = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|"
                       r"in\s+response\s+to|because\s+of)\b", re.I)
BUYER_RXS = (re.compile(r"(unreported|hidden|secret|undisclosed|covert)\s+(central[- ]bank\s+|official\s+|PBoC\s+)?(buying|purchases|demand)", re.I),
             re.compile(r"(PBoC|central[- ]bank)s?\s+(bought|buying|purchases)", re.I))
BOUND_RXS = (re.compile(r"\bceiling\b", re.I), re.compile(r"\bcaps?\b", re.I), re.compile(r"\bcapped\b", re.I), re.compile(r"\b(upper\s+)?bound(s|ed)?\b", re.I))

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


class MaxRequests(Refused):
    """The request cap for this invocation was reached: an orderly end."""


class Latched(Exception):
    """A technical refusal: STOP was written (or already exists); this source's run ends."""


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


def fnum(v, nd):
    """Fixed-decimal text, '' for None, no negative zero."""
    if v is None:
        return ""
    s = format(round(v, nd), ".%df" % nd)
    return s[1:] if s.startswith("-") and float(s) == 0 else s


def kgs(v):
    """Kilograms as an integer string; '' for None."""
    return "" if v is None else str(int(round(v)))


def to_t(kg):
    """Tonnes from kilograms."""
    return None if kg is None else kg / (1_000_000.0 if M("t_1e6") else 1000.0)


def tons(kg):
    return "" if kg is None else fnum(to_t(kg), 3)


def add_months(d, k):
    y, m0 = divmod(d.year * 12 + d.month - 1 + k, 12)
    m = m0 + 1
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def mkey(d):
    return "%04d-%02d" % (d.year, d.month)


def madd(m, k):
    y, mm = divmod(int(m[:4]) * 12 + int(m[5:7]) - 1 + k, 12)
    return "%04d-%02d" % (y, mm + 1)


def months_between(a, b):
    out, m = [], a
    while m <= b:
        out.append(m)
        m = madd(m, 1)
    return out


def month_first(m):
    return dt.date(int(m[:4]), int(m[5:7]), 1)


def monthid(m):
    return int(m[:4]) * 100 + int(m[5:7])


def from_monthid(n):
    return "%04d-%02d" % (n // 100, n % 100)


def trade_system_of(m):
    if M("no_general_2016_04"):
        return "general" if m < "2016-04" else "special"
    return "general" if m < SPECIAL_FROM else "special"


def system_of_set(months):
    s = {trade_system_of(m) for m in months}
    if M("annual_not_mixed"):
        return "special" if "special" in s else "general"
    return s.pop() if len(s) == 1 else "mixed"


def D_(s):
    return dt.date.fromisoformat(s)


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
# requests: the table, the URL check (R1, R4) and the content tests (R3a)
# ------------------------------------------------------------------------------------------------------------------------
def hmrc_target(path, query):
    """path plus an ordered list of (option, value); spaces and quotes are percent-encoded, the option names (with their $) are kept."""
    qs = "&".join("%s=%s" % (k, quote(v, safe="()',/=")) for k, v in query)
    return path + ("?" + qs if qs else "")


def hmrc_requests():
    return [dict(key="ots", kind="ots", target=hmrc_target("/OTS", [("$filter", OTS_FILTER), ("$count", "true")]), file="hmrc/ots_7108_f4_{date}.json"),
            dict(key="apply", kind="apply", target=hmrc_target("/OTS", [("$apply", APPLY_Q)]), file="hmrc/apply_c05_{date}.json"),
            dict(key="flowtype", kind="flowtype", target="/FlowType", file="hmrc/lookup_flowtype_{date}.json"),
            dict(key="country", kind="country", target="/Country", file="hmrc/lookup_country_{date}.json"),
            dict(key="commodity", kind="commodity", target=hmrc_target("/Commodity", [("$filter", "Cn8Code ge '71080000' and Cn8Code le '71089999'")]),
                 file="hmrc/lookup_commodity_{date}.json")]


def ct_target(freq, reporter, period, partners, cmd, flow="X"):
    return ("/public/v1/preview/C/%s/HS?reporterCode=%d&period=%s&partnerCode=%s&cmdCode=%s&flowCode=%s"
            % (freq, reporter, period, ",".join(str(p) for p in partners), cmd, flow))


CT_RX = re.compile(r"/public/v1/preview/C/([MA])/HS\?reporterCode=(757|826)&period=(\d{4}|\d{6})&partnerCode=(156,344|156)&cmdCode=(710812|710813)&flowCode=X")


def check_url(url):
    """Only plain https GETs to the two hosts; no $orderby; no or-chain on CommoditySitcId; the exact request shapes. Returns (host, target)."""
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    target = p.path + ("?" + p.query if p.query else "")
    if M("allow_other_host"):
        return host, target
    if p.scheme != "https" or p.username or p.password or p.port not in (None, 443) or p.fragment:
        raise Refused("only plain https URLs are allowed")
    if host not in HOST_ALLOW:
        raise Refused("host %s is not on the allowlist" % host)
    low = unquote(p.query).lower()
    if "$orderby" in low and not M("orderby_ok"):
        raise Refused("$orderby is never used (it returned 403 on 19 Oct)")
    if "commoditysitcid" in low and re.search(r"\bor\b", low):
        raise Refused("no or-chains on CommoditySitcId (a 500)")
    if host == HMRC_HOST:
        ok = {r["target"] for r in hmrc_requests()}
        main = hmrc_requests()[0]["target"]
        if target in ok:
            return host, target
        if p.path == "/OTS" and unquote(target).startswith(unquote(main)):
            return host, target                                   # an @odata.nextLink continuation of the main pull
        raise Refused("that path is not one of the requests of the spec")
    if not CT_RX.fullmatch(target):
        raise Refused("that path is not one of the Comtrade requests of the spec")
    return host, target


def _json(body):
    try:
        return json.loads(body.decode("utf-8-sig")), None
    except (UnicodeDecodeError, ValueError):
        return None, "not JSON"


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _i(v):
    """An integer from an int or an integer-looking string; None otherwise."""
    if _is_int(v):
        return v
    if isinstance(v, str) and re.fullmatch(r"\s*-?\d+\s*", v):
        return int(v)
    return None


def test_ots_page(doc, first, today):
    """R3a for an /OTS page. first: the page that must carry @odata.count."""
    if not isinstance(doc, dict):
        return "the body is not a JSON object"
    if not str(doc.get("@odata.context", "")).endswith("#OTS"):
        return "@odata.context does not end #OTS"
    val = doc.get("value")
    if not isinstance(val, list):
        return "value is not a list"
    if first and not _is_int(doc.get("@odata.count")):
        return "@odata.count is not an integer"
    top = today.year * 100 + today.month
    for r in val:
        if not isinstance(r, dict) or any(k not in r for k in OTS_FIELDS):
            return "a row lacks one of the ten fields"
        if _i(r["FlowTypeId"]) != 4 and not M("flow_any"):
            return "a row with FlowTypeId %r (only 4 is admitted)" % (r["FlowTypeId"],)
        mid = _i(r["MonthId"])
        if mid is None or not (200501 <= mid <= top) or not (1 <= mid % 100 <= 12):
            return "MonthId %r is not a valid YYYYMM from 200501 to the current month" % (mid,)
    return None


def test_apply(doc):
    if not isinstance(doc, dict) or "#OTS" not in str(doc.get("@odata.context", "")):
        return "@odata.context does not name OTS"
    val = doc.get("value")
    if not isinstance(val, list):
        return "value is not a list"
    for r in val:
        if not isinstance(r, dict) or _i(r.get("MonthId")) is None or not (202401 <= _i(r["MonthId"]) <= 202412) or not isinstance(r.get("kg"), (int, float)):
            return "a groupby row is not {MonthId in 2024, kg}"
    return None


def _records(doc):
    if not isinstance(doc, dict) or not isinstance(doc.get("value"), list):
        return None
    return [r for r in doc["value"] if isinstance(r, dict)]


def test_flowtype(doc):
    recs = _records(doc)
    if recs is None:
        return "value is not a list"
    four = [r for r in recs if _i(r.get("FlowTypeId")) == 4]
    if not four:
        return "FlowTypeId 4 is not in the lookup"
    labels = [v.strip() for v in four[0].values() if isinstance(v, str)]
    if M("lookup_label_loose"):
        return None if any(v.startswith("Non-EU") for v in labels) else "FlowType 4 is not a Non-EU label"
    return None if "Non-EU Exports" in labels else "FlowType 4 is not labelled 'Non-EU Exports'"


def test_country(doc):
    recs = _records(doc)
    if recs is None:
        return "value is not a list"
    want = {720: "CN", 740: "HK", 39: "CH", 977: ""}
    for cid, alpha in want.items():
        r = next((x for x in recs if _i(x.get("CountryId")) == cid), None)
        if r is None:
            return "CountryId %d is not in the lookup" % cid
        got = next((str(v or "").strip() for k, v in r.items() if "alpha" in k.lower()), "")
        if got != alpha:
            return "CountryId %d has alpha %r, not %r" % (cid, got, alpha)
    return None


def test_commodity(doc):
    recs = _records(doc)
    if recs is None:
        return "value is not a list"
    got = set()
    for r in recs:
        for v in r.values():
            if isinstance(v, (int, str)) and not isinstance(v, bool) and re.fullmatch(r"7108\d{4}", str(v).strip()):
                got.add(int(str(v).strip()))
    return None if got == set(KNOWN_CODES) else "the 7108 commodity list is %s, not the five codes" % sorted(got)


def test_comtrade(doc, reporter, cmd, period, partners):
    """R3a for Comtrade: an empty data list is a valid reply."""
    if not isinstance(doc, dict):
        return "the body is not a JSON object"
    if doc.get("error"):
        return "the error field is not empty"
    data = doc.get("data")
    if not isinstance(data, list):
        return "data is not a list"
    if not data and M("empty_data_fails"):
        return "data is empty"
    for r in data:
        if not isinstance(r, dict):
            return "a record is not an object"
        if str(r.get("reporterCode")) != str(reporter):
            return "reporterCode is not the requested reporter"
        if r.get("flowCode") != "X" and not (M("comtrade_m_ok") and r.get("flowCode") == "M"):
            return "flowCode %r is not X" % (r.get("flowCode"),)
        if str(r.get("cmdCode")) != str(cmd) or str(r.get("period")) != str(period):
            return "cmdCode or period is not the requested one"
        if str(r.get("partnerCode")) not in {str(p) for p in partners}:
            return "partnerCode is not in the request"
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


class Fetcher:
    """One source per instance. Opener, clock, sleeper and the STOP directory are injectable so every rule is testable without a network."""

    def __init__(self, source, cache, out_dir, stop_dir=STOP_DIR, sleep=None, max_requests=None, opener=real_opener, wall=time.time, mono=time.monotonic,
                 sleeper=time.sleep, now_utc=None, root=ROOT):
        if source == "hmrc":
            self.host, self.min_sleep, dflt_sleep, self.cap = HMRC_HOST, HMRC_MIN_SLEEP, HMRC_SLEEP, HMRC_MAX
            pace_off, cap_off = M("hmrc_pacing_off"), M("hmrc_cap_off")
        elif source == "comtrade":
            self.host, self.min_sleep, dflt_sleep, self.cap = CT_HOST, CT_MIN_SLEEP, CT_SLEEP, CT_MAX
            pace_off, cap_off = M("ct_pacing_off"), M("ct_cap_off")
        else:
            raise Refused("unknown source")
        self.source = source
        self.sleep = float(dflt_sleep if sleep is None else sleep)
        self.max_requests = self.cap if max_requests is None else max_requests
        if self.sleep < self.min_sleep and not pace_off:
            raise Refused("--sleep for %s must be at least %g seconds" % (source, self.min_sleep))
        if (self.max_requests > self.cap and not cap_off) or self.max_requests < 1:
            raise Refused("the request cap for %s must be between 1 and %d" % (source, self.cap))
        self.out_dir = out_dir
        self.cache = check_cache(cache, root=root, out_dir=out_dir)
        self.opener, self.wall, self.mono, self.sleeper = opener, wall, mono, sleeper
        self.stop_path = os.path.join(stop_dir, "STOP_" + source)
        self.now_utc = now_utc or (lambda: dt.datetime.now(dt.timezone.utc))
        self.requests = 0
        self._last_mono = None
        self._last_file = os.path.join(self.cache, ".last_request_" + source)
        self.log_path = os.path.join(out_dir, "fetch_log.csv")

    def today(self):
        return self.now_utc().date()

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
        off = M("hmrc_pacing_off") if self.source == "hmrc" else M("ct_pacing_off")
        if wait > 0 and not off:
            self.sleeper(min(wait, self.sleep))

    @staticmethod
    def _stamp(ts):
        return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % int((ts % 1) * 1000)

    def _log(self, ts, target, status, nbytes, sha):
        _, rows = read_csv_rows(self.log_path)
        rows.append([self._stamp(ts), self.host, target, str(status), str(nbytes), sha])
        write_text(self.log_path, render_csv("fetch_log.csv", rows, fetch_source_line(rows)))

    def _latch(self, status, target, retry_after, body, why):
        """Write the STOP file (exclusive create: an existing one is never overwritten) and end this source's run."""
        os.makedirs(os.path.dirname(self.stop_path), exist_ok=True)
        text = stop_fields(status, self.now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"), target, retry_after or "", esc_head(body))
        try:
            with open(self.stop_path, "x", encoding="utf-8") as fh:
                fh.write(text)
        except FileExistsError:
            pass
        raise Latched("STOP written: %s (%s)" % (tilde(self.stop_path), why))

    def _get(self, target):
        check_url("https://" + self.host + target)
        if self.requests >= self.max_requests:
            raise MaxRequests("request cap reached (%d for %s)" % (self.max_requests, self.source))
        self._pace()
        started = self.wall()
        self._last_mono = self.mono()
        os.makedirs(self.cache, exist_ok=True)
        write_text(self._last_file, "%r\n" % started)
        self.requests += 1
        hdrs = dict(HEADERS)
        try:
            status, body, rh = self.opener(self.host, target, hdrs, TIMEOUT, BODY_CAP)
        except SocketFault:
            self._log(started, target, "socket_fault", "", "")
            raise
        return status, body, rh, started

    def get_doc(self, target, testfn):
        """GET and test one URL. Anything but a 200 with a body that passes testfn latches. Returns (parsed JSON, raw bytes)."""
        self.check_stop()
        status, body, rh, started = self._get(target)
        if status == 429 and M("retry_429"):
            status, body, rh, started = self._get(target)
        if status != 200:
            self._log(started, target, status, "", "")
            if status // 100 == 3 and M("redirect_ok"):
                return None, b""
            self._latch(status, target, rh.get("retry-after", ""), body, "HTTP %s" % status)
        if body is None:
            self._log(started, target, status, "", "")
            self._latch(status, target, "", b"", "body larger than the cap")
        self._log(started, target, status, len(body), sha256_of(body))
        doc, problem = _json(body)
        if problem is None:
            problem = testfn(doc)
        if problem:
            self._latch(status, target, "", body, "content test: %s" % problem)
        return doc, body

    # ---- HMRC ---------------------------------------------------------------------------------------------------------
    def get_ots(self, target):
        today = self.today()
        pages, first = [], True
        while True:
            doc, raw = self.get_doc(target, lambda d, fi=first: test_ots_page(d, fi, today))
            pages.append((doc, raw))
            first = False
            nxt = doc.get("@odata.nextLink")
            if not nxt or M("nextlink_ignored"):
                break
            _, target = check_url(nxt)
        count = pages[0][0]["@odata.count"]
        n = sum(len(d["value"]) for d, _ in pages)
        if n != count and not M("count_mismatch_ok"):
            self._latch(200, target, "", pages[-1][1], "rows %d != @odata.count %d" % (n, count))
        if len(pages) == 1:
            return pages[0][0], pages[0][1]
        merged = dict(pages[0][0])
        merged["value"] = [r for d, _ in pages for r in d["value"]]
        merged.pop("@odata.nextLink", None)
        return merged, json.dumps(merged, separators=(",", ":")).encode("utf-8")

    def fetch_hmrc(self, say=print):
        date = self.today().isoformat()
        tests = {"apply": test_apply, "flowtype": test_flowtype, "country": test_country, "commodity": test_commodity}
        saved = 0
        for req in hmrc_requests():
            path = os.path.join(self.cache, req["file"].format(date=date))
            if os.path.exists(path):
                say("%-34s cached" % os.path.basename(path))
                continue
            self.check_stop()
            if req["kind"] == "ots":
                doc, raw = self.get_ots(req["target"])
            else:
                doc, raw = self.get_doc(req["target"], tests[req["kind"]])
            write_bytes(path, raw)
            saved += 1
            say("%-34s saved (%d bytes)" % (os.path.basename(path), len(raw)))
        return saved

    # ---- Comtrade -----------------------------------------------------------------------------------------------------
    def done_today(self, target):
        today = self.now_utc().strftime("%Y-%m-%d")
        _, rows = read_csv_rows(self.log_path)
        return any(r[1] == self.host and r[2] == target and r[3] == "200" and r[4] and r[0][:10] == today for r in rows)

    def fetch_comtrade(self, plan, say=print):
        saved = 0
        for item in plan:
            path = os.path.join(self.cache, item["file"])
            if os.path.exists(path) and (not item["refresh"] or self.done_today(item["target"])):
                continue
            self.check_stop()
            doc, raw = self.get_doc(item["target"], item["test"])
            write_bytes(path, raw)
            saved += 1
        say("comtrade: %d file(s) saved in this run" % saved)
        return saved


def comtrade_plan(today):
    """The ordered Comtrade requests. Monthly Swiss replies from 2012-01 to two months before today (176 on 19 Oct 2026), the latest 18 months
    refreshed each run; annual replies for each completed year; one UK cross-check call (R3-8)."""
    end = madd(mkey(today), -2)
    plan = [dict(file="comtrade/uk_check_2024.json", target=ct_target("A", CT_REPORTER_UK, "2024", [156], "710813"), refresh=False,
                 test=lambda d: test_comtrade(d, CT_REPORTER_UK, 710813, 2024, [156])), annual_item(2024)]
    for m in months_between(SWISS_SCAN_FROM, end):
        pid = m.replace("-", "")
        plan.append(dict(file="comtrade/%s.json" % pid, target=ct_target("M", CT_REPORTER_CH, pid, [156, 344], "710812"), refresh=m >= madd(end, -17),
                         test=lambda d, pid=pid: test_comtrade(d, CT_REPORTER_CH, 710812, pid, [156, 344])))
    for y in range(int(SWISS_SCAN_FROM[:4]), today.year):
        if y != 2024:
            plan.append(annual_item(y))
    return plan


def annual_item(y):
    return dict(file="comtrade/A%d.json" % y, target=ct_target("A", CT_REPORTER_CH, str(y), [156, 344], "710812"), refresh=False,
                test=lambda d, y=y: test_comtrade(d, CT_REPORTER_CH, 710812, y, [156, 344]))


def check_cache(cache, root=ROOT, out_dir=None):
    """The cache may be outside the repository, or inside it only where git ignores it (never in the committed output folder)."""
    real = os.path.realpath(os.path.expanduser(cache))
    rroot = os.path.realpath(root)
    if M("cache_check_off"):
        return real
    if real == rroot or real.startswith(rroot + os.sep):
        outd = os.path.realpath(out_dir or os.path.join(root, "data", "uk_gold_exports"))
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


def fetch_source_line(rows):
    def dates(host):
        return sorted({r[0][:10] for r in rows if r[1] == host and r[3] == "200" and r[4]})
    parts = []
    for name, host in (("HMRC Overseas Trade Statistics API (api.uktradeinfo.com)", HMRC_HOST), ("UN Comtrade public preview (comtradeapi.un.org)", CT_HOST)):
        ds = dates(host)
        parts.append("%s retrieved %s" % (name, ", ".join(ds) if ds else "(no logged retrieval)"))
    return "# source: " + "; ".join(parts) + "; request log of bin/uk_gold_exports.py fetch (one row per request)"


# ------------------------------------------------------------------------------------------------------------------------
# HMRC rows, partner-month cells (spec 3.1 - 3.4)
# ------------------------------------------------------------------------------------------------------------------------
Row = collections.namedtuple("Row", "month supp code country port value kg unit")
Cell = collections.namedtuple("Cell", "kg supp rows_n status")
RANK = {"suppressed": 3, "unattributable": 2}


def parse_rows(doc):
    mult = 1000.0 if M("netmass_as_tonnes") else 1.0                       # the mutant reads NetMass as tonnes
    return [Row(from_monthid(int(r["MonthId"])), int(r["SuppressionIndex"] or 0), int(r["CommodityId"]), int(r["CountryId"]), r["PortId"],
                float(r["Value"] or 0), float(r["NetMass"] or 0) * mult, float(r["SuppUnit"] or 0)) for r in doc["value"]]


def series_of(code):
    if M("monetary_in_series") and code == MONETARY:
        return "cn71081310"
    if M("powder_in_other") and code == 71081100:
        return "other"
    return CODES.get(code)


def partner_of(country):
    if M("ch_as_cn") and country == 39:
        return "CN"
    return PARTNER_IDS.get(country)


def agg_cell(rm, unattr, series, partner):
    rs = [r for r in rm if series_of(r.code) == series and (partner == "ALL_NON_EU" or partner_of(r.country) == partner)]
    if M("first_row_only"):
        rs = rs[:1]
    if not M("supp_kept") and any(r.supp != 0 for r in rs):
        return Cell(None, None, len(rs), "suppressed")
    if unattr and partner != "CH" and not M("confidential_zero"):
        if partner != "ALL_NON_EU" or not M("all_non_eu_filled"):
            return Cell(None, None, len(rs), "unattributable")
    if not rs:
        if M("absence_blank"):
            return Cell(None, None, 0, "no_rows")
        return Cell(0, 0.0, 0, "no_rows")
    kg = sum(r.kg for r in rs)
    if kg == 0 and M("zero_row_no_rows"):
        return Cell(0, 0.0, len(rs), "no_rows")
    return Cell(kg, sum(r.unit for r in rs) / 1000.0, len(rs), "ok")


def combine(cn, hk):
    if (cn.kg is None or hk.kg is None) and not M("cnhk_fills_blank"):
        worse = max((c.status for c in (cn, hk) if c.kg is None), key=lambda s: RANK.get(s, 0))
        return Cell(None, None, cn.rows_n + hk.rows_n, worse)
    kg = (cn.kg or 0) + (hk.kg or 0)
    st = "ok" if "ok" in (cn.status, hk.status) else "no_rows"
    return Cell(kg, (cn.supp or 0.0) + (hk.supp or 0.0), cn.rows_n + hk.rows_n, st)


def month_range(rows):
    return months_between(FIRST_MONTH, max(r.month for r in rows))


def aggregate(rows, months=None):
    """{(month, partner, series): Cell} over ports and codes. unattributable = any 7108 non-EU-export row that month under CountryId >= 950 or with a
    suppression index; it blanks CN, HK, CN_HK and ALL_NON_EU for every series."""
    months = months or month_range(rows)
    by = collections.defaultdict(list)
    for r in rows:
        by[r.month].append(r)
    cells = {}
    for m in months:
        rm = by.get(m, [])
        unattr = any(r.country >= CONFIDENTIAL_FROM or r.supp != 0 for r in rm)
        for s in SERIES:
            for p in BASE_PARTNERS:
                cells[(m, p, s)] = agg_cell(rm, unattr, s, p)
            cells[(m, "CN_HK", s)] = combine(cells[(m, "CN", s)], cells[(m, "HK", s)])
    return cells


def unknown_codes(rows):
    if M("unknown_dropped"):
        return []
    return sorted({r.code for r in rows if r.code not in KNOWN_CODES})


# ------------------------------------------------------------------------------------------------------------------------
# vintages and the provisional flag (3.6, 3.7)
# ------------------------------------------------------------------------------------------------------------------------
def first_pub(vintages, months, upto=None):
    """{month: first publication date}. A month already in the oldest pull: the month level reading of 'month's end plus 2 months' (first day of month+2),
    because HMRC releases month M in month M+2; otherwise the vintage date of the first pull that holds it."""
    vs = vintages[:upto]
    sets = [(d, {r.month for r in rows}) for d, rows in vs]
    pub = {}
    for m in months:
        if m in sets[0][1] or not any(m in s for _, s in sets):
            pub[m] = month_first(madd(m, 2))
        else:
            pub[m] = next(D_(d) for d, s in sets if m in s)
    return pub


def provisional_flags(vintages, months, upto=None):
    vs = vintages[:upto]
    asof = D_(vs[-1][0])
    newest = max(r.month for r in vs[-1][1])
    pub = first_pub(vintages, months, upto)
    out = {}
    for m in months:
        if M("prov_from_newest"):
            out[m] = m > madd(newest, -PROVISIONAL_MONTHS)
        else:
            out[m] = asof < add_months(pub[m], PROVISIONAL_MONTHS)
    return out


def yn(b):
    return "yes" if b else "no"


# ------------------------------------------------------------------------------------------------------------------------
# revisions.csv: append-only (R2-5)
# ------------------------------------------------------------------------------------------------------------------------
def cells_from_monthly_rows(mrows):
    """The committed monthly.csv as cells: used only by the mutant that reads the previous vintage from it."""
    out = {}
    for r in mrows:
        out[(r[0], r[1], r[2])] = Cell(None if r[3] == "" else float(r[3]), None, 0, r[6])
    return out


def revision_rows(vintages, existing, existing_monthly=None):
    out = [list(r) for r in existing]
    if M("revision_rewrite"):
        out = out[::-1]
    keys = {tuple(r[:5]) for r in out}
    if not vintages:
        return out
    if not M("no_baseline"):
        k = ("baseline", vintages[0][0], "", "", "")
        if k not in keys:
            out.append(list(k) + [""] * 4)
            keys.add(k)
    for i in range(1, len(vintages)):
        (pd, prows), (nd, nrows) = vintages[i - 1], vintages[i]
        pl, nl = max(r.month for r in prows), max(r.month for r in nrows)
        if nl < pl and not M("earlier_latest_ok"):
            raise DataError("vintage %s ends at %s, earlier than %s at %s" % (nd, nl, pd, pl))
        pm = month_range(prows)
        if M("prev_from_monthly") and existing_monthly:
            pc = cells_from_monthly_rows(existing_monthly)
        else:
            pc = aggregate(prows, pm)
        nc = aggregate(nrows, pm)
        prov = provisional_flags(vintages, pm, upto=i)
        for m in pm:
            for s in SERIES:
                for p in PARTNERS:
                    a, b = pc[(m, p, s)].kg, nc[(m, p, s)].kg
                    if a == b:
                        continue
                    key = (pd, nd, m, p, s)
                    if key in keys and not M("revision_dup_key"):
                        continue
                    keys.add(key)
                    out.append([pd, nd, m, p, s, "" if M("kgprev_lost") else kgs(a), kgs(b), kgs(b - a) if a is not None and b is not None else "", yn(prov[m])])
    return out


# ------------------------------------------------------------------------------------------------------------------------
# tables: monthly, annual (3.5, 3.8)
# ------------------------------------------------------------------------------------------------------------------------
def monthly_table(cells, months, prov, vintage):
    rows = []
    for m in months:
        for s in SERIES:
            for p in PARTNERS:
                c = cells[(m, p, s)]
                rows.append([m, p, s, kgs(c.kg), "" if c.kg is None else fnum(c.supp, 3), str(c.rows_n), c.status, trade_system_of(m), yn(prov[m]), vintage])
    return rows


def annual_table(cells, months, prov, vintage):
    years = sorted({m[:4] for m in months})
    rows = []
    for y in years:
        ms = [m for m in months if m[:4] == y]
        ts = system_of_set(ms)
        for s in SERIES:
            for p in PARTNERS:
                cs = [cells[(m, p, s)] for m in ms]
                known = [c.kg for c in cs if c.kg is not None]
                blank = len(cs) - len(known)
                net = sum(known) if (blank == 0 or M("annual_filled")) else None
                rows.append([y, p, s, kgs(net), kgs(sum(known)), str(len(ms)), str(blank), ts, str(sum(1 for m in ms if prov[m])), vintage])
    return rows


def annual_lookup(arows):
    return {(r[0], r[1], r[2]): r for r in arows}


# ------------------------------------------------------------------------------------------------------------------------
# the Swiss mirror (2.2, 3.9)
# ------------------------------------------------------------------------------------------------------------------------
def total_record(r):
    return r.get("motCode") in (None, 0, "0") and r.get("partner2Code") in (None, 0, "0") and r.get("customsCode") in (None, "C00", "")


def comtrade_cells(doc):
    """{'CN': (kg, estimated, usd) or None, 'HK': ...} from one monthly Comtrade reply. Only a total record is used when the reply breaks it down; a
    record is never dropped for isReported = false; a second total record for one partner is a DataError."""
    out = {"CN": None, "HK": None}
    seen = set()
    for r in doc.get("data", []):
        p = CT_PARTNER_IDS.get(r.get("partnerCode"))
        if p is None or not total_record(r):
            continue
        if p in seen:
            raise DataError("more than one total record for partner %s in one month" % p)
        seen.add(p)
        nw = r.get("netWgt")
        if isinstance(nw, (int, float)) and not isinstance(nw, bool):
            out[p] = (float(nw), bool(r.get("isNetWgtEstimated")), r.get("primaryValue"))
    return out


def swiss_years(sw, last_year):
    """Rows of swiss_mirror_annual.csv for completed years from the first year with a record. sw = {'months': {YYYY-MM: {'CN': rec|None, 'HK': ...}},
    'annual': {year: {'CN': kg|None, 'HK': kg|None}}}."""
    mon = sw["months"]
    have = sorted(m for m, v in mon.items() if v.get("CN") or v.get("HK"))
    if not have:
        return [], None
    first = have[0]
    rows = []
    sw["blanked"] = []
    for y in range(int(first[:4]), last_year + 1):
        ms = months_between("%d-01" % y, "%d-12" % y)
        ann = sw["annual"].get(y, {})
        for p in ("CN", "HK", "CN_HK"):
            vals, est = [], 0
            for m in ms:
                cell = mon.get(m, {}) if m >= first else {}
                zero = M("comtrade_missing_zero") and m >= first                  # the mutant: a missing Comtrade record written as 0
                if p == "CN_HK":
                    a, b = cell.get("CN"), cell.get("HK")
                    v = a[0] + b[0] if a and b else ((a[0] if a else 0.0) + (b[0] if b else 0.0) if zero else None)
                    e = bool((a and a[1]) or (b and b[1]))
                else:
                    rec = cell.get(p)
                    v, e = (rec[0], rec[1]) if rec else ((0.0, False) if zero else (None, False))
                vals.append(v)
                est += 1 if (v is not None and e) else 0
            known = [v for v in vals if v is not None]
            blank = len(vals) - len(known)
            complete = blank == 0
            net = sum(known) if complete else None
            if p == "CN_HK":
                aa = ann.get("CN"), ann.get("HK")
                a_kg = aa[0] + aa[1] if None not in aa else None
            else:
                a_kg = ann.get(p)
            fill_ann = complete or M("partial_annual_filled")
            c_ann = a_kg if fill_ann else None
            diff = (sum(known) - a_kg) if (fill_ann and a_kg is not None) else None
            ksum = kgs(sum(known)) if known else ""
            if ksum and not complete and not M("known_months_filled"):
                # a partial year's known-months sum is never published, for any partner: differencing the China, Hong Kong and combined cells would give a month
                sw["blanked"].append((str(y), p))
                ksum = ""
            rows.append([str(y), p, "710812", kgs(net), ksum, "12", str(blank), str(est), "complete" if complete else "partial", kgs(c_ann), kgs(diff)])
    return rows, first


def load_swiss(cache, last_year):
    """(sw dict, why) from the Comtrade files in the cache. None when the monthly or annual cover is not complete: the build then ships UK-only."""
    d = os.path.join(cache, "comtrade")
    if not os.path.isdir(d):
        return None, "no Comtrade files in the cache"
    mon, ann = {}, {}
    for m in months_between(SWISS_SCAN_FROM, "%d-12" % last_year):
        p = os.path.join(d, m.replace("-", "") + ".json")
        if not os.path.exists(p):
            return None, "the Comtrade monthly reply for %s is not in the cache" % m
        with open(p, "rb") as fh:
            doc, bad = _json(fh.read())
        if bad:
            return None, "the Comtrade reply for %s is not JSON" % m
        mon[m] = comtrade_cells(doc)
    for y in range(int(SWISS_SCAN_FROM[:4]), last_year + 1):
        p = os.path.join(d, "A%d.json" % y)
        if not os.path.exists(p):
            return None, "the Comtrade annual reply for %d is not in the cache" % y
        with open(p, "rb") as fh:
            doc, bad = _json(fh.read())
        ann[y] = {"CN": None, "HK": None}
        for r in doc.get("data", []):
            pc = CT_PARTNER_IDS.get(r.get("partnerCode"))
            if pc and isinstance(r.get("netWgt"), (int, float)) and total_record(r):
                ann[y][pc] = float(r["netWgt"])
    uk = None
    p = os.path.join(d, "uk_check_2024.json")
    if os.path.exists(p):
        with open(p, "rb") as fh:
            doc, bad = _json(fh.read())
        if not bad:
            vals = [float(r["netWgt"]) for r in doc.get("data", []) if isinstance(r.get("netWgt"), (int, float)) and total_record(r)]
            uk = sum(vals) if len(vals) == 1 else None
    return {"months": mon, "annual": ann, "uk2024": uk}, None


def swiss_monthly_text(sw):
    """cache swiss_monthly.csv: month, partner, net_wgt_kg, is_net_wgt_estimated, primary_value_usd (never committed)."""
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(["month", "partner", "net_wgt_kg", "is_net_wgt_estimated", "primary_value_usd"])
    for m in sorted(sw["months"]):
        for p in ("CN", "HK"):
            rec = sw["months"][m].get(p)
            if rec:
                w.writerow([m, p, kgs(rec[0]), "yes" if rec[1] else "no", "" if rec[2] is None else rec[2]])
    return out.getvalue()


def swiss_monthly_values(sw):
    """[(partner, kg)] of every cached Swiss monthly value, for the leak guard."""
    return [(p, round(rec[0])) for m, v in sw["months"].items() for p, rec in v.items() if rec]


# ------------------------------------------------------------------------------------------------------------------------
# context windows (3.10)
# ------------------------------------------------------------------------------------------------------------------------
def load_ledger(annual_path, monthly_path):
    ha, ra = read_csv_rows(annual_path)
    hm, rm = read_csv_rows(monthly_path)
    annual = {}
    for r in ra:
        d = dict(zip(ha, r))
        if d.get("period", "").isdigit():
            annual[int(d["period"])] = d
    monthly = {dict(zip(hm, r))["month"]: dict(zip(hm, r)) for r in rm}
    return annual, monthly


def _num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def context_windows(L, first_year=2019):
    y = int(L[:4])
    w = [(str(k), "%d-01" % k, "%d-12" % k) for k in range(first_year, y)]
    w.append(("%d_to_%s" % (y, L), "%d-01" % y, L))
    return w


def context_L(last_uk_month, ledger_monthly):
    cm = [m for m, r in ledger_monthly.items() if _num(r.get("china_change_t")) is not None]
    return min(last_uk_month, max(cm)) if cm else last_uk_month


def context_rows(cells, months, ledger_annual, ledger_monthly, swiss_rows, vintage_year, sw_months=None):
    """-> (rows, L). swiss_rows: swiss_mirror_annual.csv rows or None (UK-only)."""
    L = context_L(months[-1], ledger_monthly)
    sw = {int(r[0]): r for r in (swiss_rows or []) if r[1] == "CN_HK"}
    out = []
    for name, a, b in context_windows(L):
        ms = months_between(a, b)
        full = len(name) == 4
        notes, vals, blank = [], {}, 0
        for p, key in (("CN_HK", "cn_hk"), ("CN", "cn"), ("HK", "hk")):
            cs = [cells[(m, p, "cn71081310")] for m in ms]
            known = [c.kg for c in cs if c.kg is not None]
            vals[key] = sum(known) if (len(known) == len(cs) or M("context_over_blank")) else None
            if p == "CN_HK":
                blank = len(cs) - len(known)
        if blank:
            notes.append("UK magnitudes blank: %d month(s) blank in the window" % blank)
        swt = ""
        if swiss_rows is None:
            notes.append("Swiss column blank: no Swiss data in this build")
        elif not full or int(name) >= vintage_year:
            notes.append("Swiss column blank: not a completed year")
            if M("swiss_2026_filled") and sw_months:                   # the mutant: a part-year Swiss cell summed from the monthly cache
                swt = tons(sum(rec[0] for m in ms for rec in sw_months.get(m, {}).values() if rec))
        else:
            r = sw.get(int(name))
            if r and r[8] == "complete":
                swt = tons(float(r[3]))
            else:
                notes.append("Swiss column blank: %s" % ("partial year" if r else "year before the first Swiss record"))
        if full:
            sf = _num(ledger_annual.get(int(name), {}).get("china_change_t"))
        else:
            mm = months_between(a, b) if not M("safe_longer_window") else [m for m in sorted(ledger_monthly) if m.startswith(a[:4])]
            vs = [_num(ledger_monthly.get(m, {}).get("china_change_t")) for m in mm]
            sf = sum(vs) if all(v is not None for v in vs) else None
        wgc = _num(ledger_annual.get(int(name), {}).get("wgc_central_banks_fy_published_t")) if full else None
        gap = _num(ledger_annual.get(int(name), {}).get("gap_wgc_fy_published_minus_imf_t")) if full else None
        if not full:
            notes.append("WGC annual figures are not published for a part year")
        out.append([name, str(len(ms)), str(blank), system_of_set(ms), tons(vals["cn_hk"]), tons(vals["cn"]), tons(vals["hk"]), swt, fnum(sf, 3),
                    fnum(wgc, 3) if wgc is not None else "", fnum(gap, 3) if gap is not None else "", "; ".join(notes)])
    return out, L


# ------------------------------------------------------------------------------------------------------------------------
# summary.csv: the pre-registered descriptive questions (section 4). No ratio, no comparison flag between two sources.
# ------------------------------------------------------------------------------------------------------------------------
def blind_of(q, a, b):
    """R2-9, R3-7: no for every 2024 and 2025 row, every Q1 row, every Q4 row; otherwise yes."""
    if M("blind_wrong"):
        return "yes"
    if q in ("Q1", "Q4"):
        return "no"
    if a and b and a <= "2025-12" and b >= "2024-01":
        return "no"
    return "yes"


def wlabel(a, b):
    ts = system_of_set(months_between(a, b))
    if a[:4] == b[:4] and a[5:] == "01" and b[5:] == "12":
        base = a[:4]
    else:
        base = a if a == b else "%s..%s" % (a, b)
    return base if M("q_no_ts") else "%s [%s]" % (base, ts)


def srow(q, a, b, partner, series, stat, value, notable="", label=None):
    return [q, label if label is not None else (wlabel(a, b) if a else ""), partner, series, stat, value, blind_of(q, a, b), notable]


def summary_rows(S):
    cells, months, ctx, L = S["cells"], S["months"], S["ctx"], S["ctx_L"]
    arows = annual_lookup(S["annual"])
    last = months[-1]
    out = []
    # Q1: the path. Minimum and maximum months on each side of the May 2016 break; zero months per year 2019-; runs of zero months for CN after 2019.
    for p in ("CN", "HK", "CN_HK"):
        for a, b in ((FIRST_MONTH, madd(SPECIAL_FROM, -1)), (SPECIAL_FROM, last)):
            vals = [(cells[(m, p, "cn71081310")].kg, m) for m in months_between(a, b)]
            known = [(v, m) for v, m in vals if v is not None]
            if known:
                lo, hi = min(v for v, _ in known), max(v for v, _ in known)
                out += [srow("Q1", a, b, p, "cn71081310", "min_kg", kgs(lo)), srow("Q1", a, b, p, "cn71081310", "min_kg_first_month", next(m for v, m in known if v == lo)),
                        srow("Q1", a, b, p, "cn71081310", "max_kg", kgs(hi)), srow("Q1", a, b, p, "cn71081310", "max_kg_first_month", next(m for v, m in known if v == hi))]
            out.append(srow("Q1", a, b, p, "cn71081310", "blank_months_n", str(len(vals) - len(known))))
        for y in range(2019, int(last[:4]) + 1):
            a, b = "%d-01" % y, min("%d-12" % y, last)
            zs = sum(1 for m in months_between(a, b) if cells[(m, p, "cn71081310")].kg == 0)
            out.append(srow("Q1", a, b, p, "cn71081310", "zero_months_n", str(zs)))
    a = "2020-01"
    run = best = 0
    best_end = ""
    for m in months_between(a, last):
        if cells[(m, "CN", "cn71081310")].kg == 0:
            run += 1
            if run > best:
                best, best_end = run, m
        else:
            run = 0
    out += [srow("Q1", a, last, "CN", "cn71081310", "longest_run_zero_months", str(best), "yes" if best >= 3 else "no"),
            srow("Q1", a, last, "CN", "cn71081310", "longest_run_last_month", best_end)]
    # Q2 and Q3: separate magnitudes in their own rows, no comparison
    for r in ctx:
        name = r[0]
        a, b = next((x[1], x[2]) for x in context_windows(L) if x[0] == name)
        out += [srow("Q2", a, b, "CN_HK", "cn71081310", "uk_declared_t", r[4]), srow("Q2", a, b, "CN", "cn71081310", "uk_declared_t", r[5]),
                srow("Q2", a, b, "", "safe", "safe_reported_change_t", r[8])]
        if len(name) == 4 and int(name) >= 2022:
            out += [srow("Q3", a, b, "CN_HK", "cn71081310", "uk_declared_t", r[4]), srow("Q3", a, b, "", "wgc", "wgc_central_banks_t", r[9]),
                    srow("Q3", a, b, "", "ledger_gap", "wgc_minus_imf_gap_t", r[10])]
    # Q4 and Q5: per year
    for y in sorted({m[:4] for m in months}):
        a, b = "%s-01" % y, min("%s-12" % y, last)
        for p in ("CN_HK", "ALL_NON_EU"):
            out.append(srow("Q4", a, b, p, "cn71081310", "net_mass_kg", arows[(y, p, "cn71081310")][3]))
        for s in ("cn71081310", "other", "powder"):
            out.append(srow("Q5", a, b, "CN_HK", s, "net_mass_kg", arows[(y, "CN_HK", s)][3]))
    # Q6: Switzerland beside the UK, completed years, each with its code
    if S["swiss_rows"] is None:
        out.append(srow("Q6", None, None, "CN_HK", "swiss_710812", "not_available", "", label="UK-only build"))
    else:
        for r in S["swiss_rows"]:
            if r[1] == "CN_HK":
                y = r[0]
                a, b = "%s-01" % y, "%s-12" % y
                out += [srow("Q6", a, b, "CN_HK", "swiss_710812", "swiss_hs710812_kg", r[3]),
                        srow("Q6", a, b, "CN_HK", "cn71081310", "uk_cn71081310_kg", arows[(y, "CN_HK", "cn71081310")][3])]
    # Q7: revisions at each vintage
    vd = [v[0] for v in S["vintages"]]
    revs = S["revisions"]
    seq = [(vd[i - 1], vd[i]) for i in range(1, len(vd))]
    pairs = sorted(set(seq) | {(r[0], r[1]) for r in revs if r[0] != "baseline"})
    for r in revs:
        if r[0] == "baseline":
            out.append(srow("Q7", None, None, "", "", "cells_changed", "", label="baseline->%s" % r[1]))
    for pv, nv in pairs:
        rr = [r for r in revs if r[0] == pv and r[1] == nv]
        label = "%s->%s" % (pv, nv)
        final_changes = sum(1 for r in rr if r[8] == "no")
        ch = [abs(int(r[7])) for r in rr if r[7] != ""]
        out += [srow("Q7", None, None, "", "", "cells_changed", str(len(rr)), label=label),
                srow("Q7", None, None, "", "", "largest_abs_change_kg", str(max(ch)) if ch else "0", label=label),
                srow("Q7", None, None, "", "", "changes_to_months_no_longer_provisional", str(final_changes), "yes" if final_changes else "no", label=label)]
    # Q8: the 2016 break
    for y in (2015, 2016, 2017):
        out.append(srow("Q8", "%d-01" % y, "%d-12" % y, "CN_HK", "cn71081310", "net_mass_kg", arows[(str(y), "CN_HK", "cn71081310")][3]))
    for m in months_between("2016-01", "2016-04"):
        out.append(srow("Q8", m, m, "CN_HK", "cn71081310", "net_mass_kg", kgs(cells[(m, "CN_HK", "cn71081310")].kg)))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# checks.csv (section 7)
# ------------------------------------------------------------------------------------------------------------------------
def pin_status(ok, vdate):
    if ok:
        return "PASS"
    return "FAIL" if vdate < PIN_VINTAGE_END and not M("pin_never_fails") else "WARN"


def code_partner_sum(rows, year, code, country):
    rs = [r for r in rows if r.month[:4] == year and r.code == code and r.country == country and r.supp == 0]
    return sum(r.kg for r in rs) if rs else None


def build_checks(c):
    inp, S = c["inp"], c["S"]
    vint = inp["vintages"]
    vdate = D_(vint[-1][0])
    rows = vint[-1][1]
    cells = S["cells"]
    arows = annual_lookup(S["annual"])
    ck = []

    def add(i, d, e, o, s):
        ck.append([i, d, e, o, s])

    def kgv(y, p, s):
        r = arows.get((y, p, s))
        return int(r[3]) if r and r[3] != "" else None
    # C01
    got = (kgv("2024", "CN", "cn71081310"), kgv("2024", "CH", "cn71081310"), kgv("2024", "HK", "cn71081310"))
    add("C01", "2024 annual net mass of CN 71081310 (kg): China, Switzerland, Hong Kong", "CN 382786; CH 305087; HK 26044", "CN %s; CH %s; HK %s" % got,
        pin_status(got == (382786, 305087, 26044), vdate))
    # C02
    exp2 = {(71081200, 720): None, (71081200, 39): 3000, (71081200, 740): 17, (71081380, 720): 1, (71081380, 740): 14, (71081380, 39): 63}
    obs2 = {k: code_partner_sum(rows, "2024", k[0], k[1]) for k in exp2}
    obs2 = {k: (None if v is None else int(round(v))) for k, v in obs2.items()}
    other = (kgv("2024", "CN", "other"), kgv("2024", "HK", "other"), kgv("2024", "HK", "powder"))
    lab = lambda d: "; ".join("%d/%s %s" % (k[0], {720: "CN", 740: "HK", 39: "CH"}[k[1]], "no_rows" if v is None else v) for k, v in sorted(d.items()))
    add("C02", "2024 by code (kg): 71081200 and 71081380 by partner, then the other and powder groups", lab(exp2) + "; other CN 1 HK 31; powder HK 1",
        lab(obs2) + "; other CN %s HK %s; powder HK %s" % other, pin_status(obs2 == exp2 and other == (1, 31, 1), vdate))
    # C03
    exp3 = {"01": 25046, "02": 20017, "03": 41750, "04": 35634, "05": 50194, "06": "no_rows", "07": "no_rows", "08": 0, "09": 60595, "10": 54715, "11": 49931, "12": 44904}
    obs3 = {}
    for mm in exp3:
        cc = cells.get(("2024-" + mm, "CN", "cn71081310"))
        obs3[mm] = "n/a" if cc is None else ("no_rows" if cc.status == "no_rows" else (int(round(cc.kg)) if cc.kg is not None else cc.status))
    add("C03", "2024 China CN 71081310 by month (kg; no_rows where HMRC has no row)", " ".join("%s=%s" % kv for kv in exp3.items()), " ".join("%s=%s" % kv for kv in obs3.items()),
        pin_status(obs3 == exp3, vdate))
    # C04
    first, latest = min(r.month for r in rows), max(r.month for r in rows)
    st = "PASS" if (first == FIRST_MONTH and latest >= "2026-08") else "FAIL"
    if st == "PASS" and len(rows) < 9667:
        st = "WARN"
    add("C04", "Coverage: first month, latest month, row count of the 7108 non-EU-export pull", "first 2005-01; latest >= 2026-08; rows >= 9667",
        "first %s; latest %s; rows %d" % (first, latest, len(rows)), st)
    # C05
    ad = inp.get("apply_doc")
    if ad is None:
        add("C05", "Cross-check: the $apply groupby for 2024 China CN 71081310 equals the row sums of C03", "equal in all 12 months", "the groupby reply is not in the cache", "WARN")
    else:
        g = {from_monthid(int(r["MonthId"])): r["kg"] for r in ad["value"]}
        diffs = []
        for mm in exp3:
            a = g.get("2024-" + mm, 0)
            b = (cells.get(("2024-" + mm, "CN", "cn71081310")) or Cell(0, 0, 0, "")).kg or 0
            if abs(a - b) > 0.5:
                diffs.append("%s: groupby %s, rows %s" % (mm, a, b))
        add("C05", "Cross-check: the $apply groupby for 2024 China CN 71081310 equals the row sums of C03", "equal in all 12 months",
            ("equal in all 12 months (%d groupby rows)" % len(g)) if not diffs else "; ".join(diffs), "PASS" if not diffs else pin_status(False, vdate))
    # C06
    n_supp = sum(1 for r in rows if r.supp != 0)
    n_conf = sum(1 for r in rows if r.country >= CONFIDENTIAL_FROM)
    unatt = sorted({r.month for r in rows if r.supp != 0 or r.country >= CONFIDENTIAL_FROM})
    add("C06", "Suppression census: 7108 rows with SuppressionIndex not 0, rows under CountryId >= 950, and the unattributable months", "0; 0; none (19 Oct 2026)",
        "%d; %d; %s" % (n_supp, n_conf, ", ".join(unatt) if unatt else "none"), "PASS" if n_supp == 0 and n_conf == 0 else "WARN")
    # C07 and C07s
    big = [r for r in rows if r.month >= SPECIAL_FROM and r.kg >= 100]
    out_p = [r for r in big if not (PRICE_LO <= r.value / r.kg / OZ_PER_KG <= PRICE_HI)]
    jan = [r for r in rows if r.month == "2024-01" and r.country == 720 and r.code == 71081310]
    jp = "n/a" if not jan or sum(r.kg for r in jan) == 0 else format(sum(r.value for r in jan) / sum(r.kg for r in jan) / OZ_PER_KG, ",.0f")
    frac = len(out_p) / len(big) if big else 0
    add("C07", "Implied price only: Value / NetMass / 32.1507466 in 150 to 6000 sterling per troy ounce, rows from 2016-05 with NetMass >= 100 kg",
        "all rows in range; fewer than 1% outside", "%d of %d rows outside; 2024-01 China %s sterling per troy ounce" % (len(out_p), len(big), jp),
        "FAIL" if frac > 0.01 else ("WARN" if out_p else "PASS"))
    odd = [r for r in big if not (990 <= r.unit / r.kg <= 1010)]
    add("C07s", "Supplementary-unit census: rows with NetMass >= 100 kg whose SuppUnit / NetMass lies outside 990 to 1010", "about 13% (second review); never a FAIL",
        "%d of %d rows (%s%%)" % (len(odd), len(big), fnum(100.0 * len(odd) / len(big), 1) if big else "0"), "WARN" if odd else "PASS")
    # C08
    lk = inp.get("lookups") or {}
    probs = []
    for name, fn in (("flowtype", test_flowtype), ("country", test_country), ("commodity", test_commodity)):
        if lk.get(name) is None:
            probs.append("%s not in the cache" % name)
        else:
            p = fn(lk[name])
            if p:
                probs.append("%s: %s" % (name, p))
    add("C08", "Lookups: FlowType 4 is 'Non-EU Exports'; Country 720/740/39/977 are CN/HK/CH/blank; the 7108 commodity list is the five codes", "all three hold",
        "all three hold" if not probs else "; ".join(probs), "PASS" if not probs else ("WARN" if all("not in the cache" in x for x in probs) else "FAIL"))
    # C09 (PASS/FAIL only; expected and observed left blank)
    sw = inp.get("swiss")
    if sw is None:
        add("C09", "Swiss pins: months 2024-01, 2014-01 and 2013-12 and annual 2024 against the Comtrade replies (UK-only build: not checked)", "", "", "WARN")
    else:
        ok = True
        for m, d in SWISS_PINS_M.items():
            for p, v in d.items():
                rec = sw["months"].get(m, {}).get(p)
                ok = ok and rec is not None and round(rec[0]) == v
        for y, d in SWISS_PINS_A.items():
            for p, v in d.items():
                a = sw["annual"].get(y, {}).get(p)
                ok = ok and a is not None and round(a) == v
        add("C09", "Swiss pins: months 2024-01, 2014-01 and 2013-12 and annual 2024 against the Comtrade replies (flowCode X)", "", "", "PASS" if ok else "FAIL")
    # C10
    la, lm = inp["ledger_annual"], inp["ledger_monthly"]
    good = []
    for y, key, v in ((2024, "china_change_t", 44.167), (2025, "china_change_t", 26.749), (2024, "wgc_central_banks_fy_published_t", 1092.4),
                      (2025, "wgc_central_banks_fy_published_t", 863.3)):
        x = _num(la.get(y, {}).get(key))
        good.append(x is not None and abs(x - v) < 0.0005)
    msum = []
    for y in range(2019, 2026):
        vs = [_num(lm.get("%d-%02d" % (y, k), {}).get("china_change_t")) for k in range(1, 13)]
        a = _num(la.get(y, {}).get("china_change_t"))
        msum.append(all(v is not None for v in vs) and a is not None and abs(sum(vs) - a) <= 0.01)
    add("C10", "Context pins: ledger china_change_t 2024 and 2025, WGC 2024 and 2025, and the monthly china_change_t summed over each year 2019-2025 equals the annual within 0.01 t",
        "44.167; 26.749; 1092.4; 863.3; seven years within 0.01", "pins %s; years within 0.01: %d of 7" % ("hold" if all(good) else "differ", sum(msum)),
        "PASS" if all(good) and all(msum) else "FAIL")
    # C12
    kg_uk = sum(r.kg for r in rows if r.month[:4] == "2024" and r.country == 720 and r.code in (71081310, 71081380) and r.supp == 0)
    u = sw.get("uk2024") if sw else None
    if u is None:
        add("C12", "UK net mass to China 2024 (71081310 + 71081380) against Comtrade's reporter-826 netWgt for HS 710813 (INFO)", "within 2 kg",
            "UK %d kg; no Comtrade UK record in the cache" % round(kg_uk), "INFO")
    else:
        gap = round(u) - round(kg_uk)
        add("C12", "UK net mass to China 2024 (71081310 + 71081380) against Comtrade's reporter-826 netWgt for HS 710813 (INFO)", "within 2 kg",
            "UK %d kg; Comtrade %d kg; gap %d kg%s" % (round(kg_uk), round(u), gap, "; FLAG: over 2 kg" if abs(gap) > 2 else ""), "INFO")
    # C13, C14, C15, C17
    add("C13", "Monetary gold 71082000 rows in the pull (counted, in no series)", "counted", "%d rows" % sum(1 for r in rows if r.code == MONETARY), "INFO")
    unk = unknown_codes(rows)
    add("C14", "Any 7108 code outside the five known codes (a person classifies it)", "none", "none" if not unk else ", ".join(map(str, unk)), "PASS" if not unk else "FAIL")
    add("C15", "Vintages: the newest pull's latest month is not earlier than the previous pull's", "not earlier", c.get("vintage_error") or "not earlier (%d pull(s) in the cache)" % len(vint),
        "FAIL" if c.get("vintage_error") else "PASS")
    nonint = sum(1 for r in rows if abs(r.kg - round(r.kg)) > 1e-9)
    add("C17", "NetMass values that are not whole kilograms (sums are rounded to integers in the outputs)", "0", str(nonint), "INFO")
    return ck


# ------------------------------------------------------------------------------------------------------------------------
# compute: everything the outputs hold, as data
# ------------------------------------------------------------------------------------------------------------------------
def compute(inp):
    vint = inp["vintages"]
    vd, rows = vint[-1]
    vdate = D_(vd)
    months = month_range(rows)
    cells = aggregate(rows, months)
    prov = provisional_flags(vint, months)
    c = {"inp": inp}
    try:
        revs = revision_rows(vint, inp.get("existing_revisions", []), inp.get("existing_monthly"))
    except DataError as e:
        c["vintage_error"] = str(e)
        revs = [list(r) for r in inp.get("existing_revisions", [])]
    sw = inp.get("swiss")
    swiss_rows = first_sw = None
    if sw:
        swiss_rows, first_sw = swiss_years(sw, vdate.year - 1)
    mt = monthly_table(cells, months, prov, vd)
    at = annual_table(cells, months, prov, vd)
    ctx, L = context_rows(cells, months, inp["ledger_annual"], inp["ledger_monthly"], swiss_rows, vdate.year, sw["months"] if sw else None)
    S = dict(cells=cells, months=months, prov=prov, monthly=mt, annual=at, ctx=ctx, ctx_L=L, swiss_rows=swiss_rows, first_swiss=first_sw, revisions=revs,
             vintages=[(d, None) for d, _ in vint], vdate=vdate)
    c["S"] = S
    S["summary"] = summary_rows(S)
    c["checks"] = build_checks(c)
    return c


# ------------------------------------------------------------------------------------------------------------------------
# writing: exact allowlists, source lines, wording guards (G11, G12)
# ------------------------------------------------------------------------------------------------------------------------
def allowlist(name):
    cols = list(ALLOW[name])
    if M("allow_drift") and name == "monthly.csv":
        cols[cols.index("net_mass_kg")] = "net_mass_kg_share"
    return cols


def allow_text():
    return "".join("%s:%s\n" % (n, ",".join(allowlist(n))) for n in ALLOW_ORDER)


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


def strip_exempt(text, readme=True):
    """Remove the required opening sentence and the one denial sentence (README only), each once."""
    if readme:
        if M("buyer_loose"):
            text = re.sub(r"central[- ]bank buying", "", text)
        text = text.replace(REQUIRED_SENTENCE, "", 1)
        if M("denial_loose"):
            text = re.sub(r"[^.]*\b(ceiling|cap)\b[^.]*\.", "", text)
        elif M("denial_all"):
            text = text.replace(DENIAL_SENTENCE, "")
        else:
            text = text.replace(DENIAL_SENTENCE, "", 1)
    return text


def wording_problems(name, text):
    t = strip_exempt(text, readme=name == "README.md")
    out = []
    if not M("causal_off"):
        out += ["causal wording %r" % h for h in sorted({re.sub(r"\s+", " ", m.group(0).lower()) for m in CAUSAL_RX.finditer(t)})]
    if not M("buyer_off"):
        out += ["buyer wording %r" % re.sub(r"\s+", " ", m.group(0)) for rx in BUYER_RXS for m in rx.finditer(t)]
    if not M("bound_off"):
        out += ["bound wording %r" % m.group(0).lower() for rx in BOUND_RXS for m in rx.finditer(t)]
    if not M("bars_off"):
        out += ["bare 'bars' as a label" for _ in re.finditer(r"\bbars\b", t.replace(TARIFF_TEXT, ""), re.I)]
        if name.endswith(".csv") and name != "fetch_log.csv":
            rows = list(csv.reader(l for l in t.splitlines() if not l.startswith("#")))
            if rows and "series" in rows[0]:
                i = rows[0].index("series")
                out += ["series label 'bars'" for r in rows[1:] if len(r) > i and r[i].strip().lower() == "bars"]
    return out


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


# ---- folder-level guards: the file set, headers, the Swiss places, ratios, cross-route sums -----------------------------
def csv_body(text):
    """(header, rows) of a committed csv text, skipping every `# source:` line (mutant: the source line is read as the header)."""
    lines = text.splitlines()
    if not M("source_as_header"):
        lines = [l for l in lines if not l.startswith("# source:")]
    rd = list(csv.reader(lines))
    return (rd[0], rd[1:]) if rd else ([], [])


def folder_problems(files):
    """files: {name: text}. The ten names, the exact headers, no raw file."""
    out = []
    names = set(files)
    for n in sorted(names - set(COMMITTED)):
        if n.endswith(".json") and M("raw_json_ok"):
            continue
        if M("eleventh_ok") and not n.endswith(".json"):
            continue
        out.append("file that is not one of the ten committed names: %s" % n)
    for n in sorted(set(COMMITTED) - names):
        out.append("missing: %s" % n)
    for n in ALLOW_ORDER:
        if n in files:
            try:
                check_header(n, csv_body(files[n])[0])
            except DataError as e:
                out.append(str(e))
    return out


def num_cells(text, cols=None):
    header, rows = csv_body(text)
    idx = [i for i, h in enumerate(header) if cols is None or h in cols]
    return [(header[i], r[i], r) for r in rows for i in idx if i < len(r) and re.fullmatch(r"-?\d+(\.\d+)?", r[i])]


def swiss_leak_problems(files, monthly_values, asof_year):
    """G10 (6.2): no Swiss-derived cell equals a cached Swiss monthly value (kg, or tonnes to 3 decimals) unless it equals that partner's completed-year
    total; no current-year Swiss cell; no annual comparison on a partial year."""
    out = []
    kgset = {int(kg) for _, kg in monthly_values}
    tset = {fnum(kg / 1000.0, 3) for _, kg in monthly_values}
    sw = files.get("swiss_mirror_annual.csv")
    totals_kg, totals_t = set(), set()
    if sw:
        h, rows = csv_body(sw)
        for r in rows:
            d = dict(zip(h, r))
            if d["status"] == "complete" and d["net_mass_kg"] != "":
                totals_kg.add(int(d["net_mass_kg"]))
                totals_t.add(fnum(int(d["net_mass_kg"]) / 1000.0, 3))
            if int(d["year"]) >= asof_year and any(d[k] != "" for k in ("net_mass_kg", "net_mass_kg_known_months", "comtrade_annual_kg", "monthly_sum_minus_annual_kg")) \
                    and not M("leak_current_swiss_off"):
                out.append("a current-year Swiss cell is filled in swiss_mirror_annual.csv (%s %s)" % (d["year"], d["partner"]))
            if d["status"] == "partial" and (d["comtrade_annual_kg"] != "" or d["monthly_sum_minus_annual_kg"] != "") and not M("leak_partial_off"):
                out.append("a partial Swiss year carries the annual comparison in swiss_mirror_annual.csv (%s %s)" % (d["year"], d["partner"]))
        if not M("leak_kg_off"):
            for col, val, r in num_cells(sw, ("net_mass_kg", "net_mass_kg_known_months", "comtrade_annual_kg", "monthly_sum_minus_annual_kg")):
                if val not in ("0",) and "." not in val and int(val) in kgset and int(val) not in totals_kg:
                    out.append("a Swiss monthly kg value sits in swiss_mirror_annual.csv (%s=%s)" % (col, val))
    cx = files.get("context.csv")
    if cx:
        h, rows = csv_body(cx)
        for r in rows:
            d = dict(zip(h, r))
            v = d["swiss_710812_cn_hk_t"]
            if v == "":
                continue
            yr = d["window"][:4]
            if (not d["window"].isdigit() or int(yr) >= asof_year) and not M("leak_current_context_off"):
                out.append("a current-year Swiss cell is filled in context.csv (%s)" % d["window"])
            if not M("leak_t_off") and v != "0.000" and v in tset and v not in totals_t:
                out.append("a Swiss monthly value in tonnes sits in context.csv (%s)" % v)
    return out


UNIT_RX = re.compile(r"(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?\s*(kg|kilograms?|tonnes?)\b", re.I)
TOKEN_SKIP = ("monthly.csv", "annual.csv", "revisions.csv", "fetch_log.csv", "swiss_mirror_annual.csv", "context.csv")      # the first four carry only HMRC kilograms or the request log; the last two have their own column scans


def numeric_mentions(name, text):
    """[(kind, text)] of the numbers a reader could take as a Swiss value: a whole csv cell or markdown table cell that is a plain number (an integer of 1,000
    or more that is not a year, or a 3-decimal tonnes figure), and any number written with a unit (kg, kilograms, tonnes), with or without a thousands comma."""
    out = []
    cells = []
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        if name.endswith(".md"):
            if line.startswith("|"):
                cells += [c.strip() for c in line.strip().strip("|").split("|")]
        else:
            cells += [c.strip() for c in next(csv.reader([line]))]
    for c in cells:
        if re.fullmatch(r"\d+", c) and int(c) >= 1000 and not (1990 <= int(c) <= 2100):
            out.append(("kg", c))
        elif re.fullmatch(r"\d+\.\d{3}", c):
            out.append(("t", c))
    for m in UNIT_RX.finditer(text):
        whole, dec, unit = m.group(1).replace(",", ""), m.group(2), m.group(3).lower()
        if unit.startswith("kg") or unit.startswith("kilogram"):
            if dec is None:
                out.append(("kg", whole))
        elif dec is not None and len(dec) == 4:
            out.append(("t", whole + dec))
    return out


def swiss_prose_problems(files, monthly_values):
    """G10 (6.2) extended: no number in any other committed file (README.md, SOURCES.md, summary.csv, checks.csv) equals a cached Swiss monthly value, as kilograms
    (with or without a thousands comma) or as tonnes to 3 decimals, unless it equals a completed-year Swiss total."""
    if M("leak_prose_off"):
        return []
    kgset = {int(kg) for _, kg in monthly_values if kg}
    tset = {fnum(kg / 1000.0, 3) for _, kg in monthly_values if kg}
    totals_kg, totals_t = set(), set()
    if "swiss_mirror_annual.csv" in files:
        h, rows = csv_body(files["swiss_mirror_annual.csv"])
        for r in rows:
            d = dict(zip(h, r))
            if d["status"] == "complete" and d["net_mass_kg"] != "":
                totals_kg.add(int(d["net_mass_kg"]))
                totals_t.add(fnum(int(d["net_mass_kg"]) / 1000.0, 3))
    out = []
    for name in sorted(files):
        if name in TOKEN_SKIP:
            continue
        hits = set()
        for kind, tok in numeric_mentions(name, files[name]):
            if kind == "kg" and int(tok) in kgset and int(tok) not in totals_kg:
                hits.add(tok)
            if kind == "t" and tok in tset and tok not in totals_t:
                hits.add(tok)
        out += ["a Swiss monthly value (%s) sits in %s" % (t, name) for t in sorted(hits)]
    return out


def swiss_difference_problems(files, sw):
    """G10 (6.2) extended: in a year with a partial partner, no committed Swiss cells combined by adding or subtracting (two or three cells from different partner
    rows) give a cached monthly value of that year or a sum of that year's known months. This makes the identity China known-months + Hong Kong annual - combined
    known-months impossible: the known-months cells of partial years are blank."""
    if M("difference_off") or not sw or "swiss_mirror_annual.csv" not in files:
        return []
    import itertools
    h, rows = csv_body(files["swiss_mirror_annual.csv"])
    by_year = {}
    for r in rows:
        d = dict(zip(h, r))
        by_year.setdefault(d["year"], {})[d["partner"]] = d
    out = []
    for y, g in sorted(by_year.items()):
        if not any(d["status"] == "partial" for d in g.values()):
            continue
        ms = ["%s-%02d" % (y, k) for k in range(1, 13)]
        forb = {}
        for p in ("CN", "HK"):
            vals = [sw["months"].get(m, {}).get(p) for m in ms]
            for v in vals:
                if v:
                    forb[round(v[0])] = "a monthly value"
            known = [v[0] for v in vals if v]
            if known:
                forb[round(sum(known))] = "a sum of known months"
        both = [(sw["months"].get(m, {}).get("CN"), sw["months"].get(m, {}).get("HK")) for m in ms]
        both = [a[0] + b[0] for a, b in both if a and b]
        if both:
            forb[round(sum(both))] = "a sum of known months"
        cells = [(p, col, int(d[col])) for p, d in g.items() for col in ("net_mass_kg", "net_mass_kg_known_months", "comtrade_annual_kg") if d[col] not in ("", "0")]
        for k in (2, 3):
            for combo in itertools.combinations(cells, k):
                if len({c[0] for c in combo}) < 2:
                    continue
                for signs in itertools.product((1, -1), repeat=k):
                    val = sum(sg * c[2] for sg, c in zip(signs, combo))
                    if val > 0 and val in forb:
                        out.append("committed Swiss cells of %s give %s by addition and subtraction (%s)" % (y, forb[val], " ".join("%+d*%s:%s" % (sg, c[0], c[1]) for sg, c in zip(signs, combo))))
    return sorted(set(out))


def ratio_problems(files):
    """G8: no ratio-like column name; no committed value equal to a quotient of two magnitudes of the same context window."""
    out = []
    if not M("ratio_col_off"):
        for n, t in files.items():
            if n.endswith(".csv"):
                out += ["column %r in %s looks like a ratio, multiple or share" % (h, n) for h in csv_body(t)[0] if BANNED_COL_RX.search(h)]
    cx = files.get("context.csv")
    if cx and not M("quotient_off"):
        h, rows = csv_body(cx)
        sm = csv_body(files["summary.csv"]) if "summary.csv" in files else ([], [])
        for r in rows:
            d = dict(zip(h, r))
            mags = [float(d[k]) for k in h[4:11] if d.get(k, "") != ""]
            quot = {fnum(a / b, 3) for a in mags for b in mags if a != b and b not in (0.0, 1.0) and a != 0.0}
            own = {fnum(a, 3) for a in mags}
            quot -= own
            cells = [v for k, v in zip(h, r) if k in h[4:11] and v != ""]
            for rr in sm[1]:
                if rr[1].split(" ")[0] == d["window"] or rr[1].split(" ")[0] == d["window"][:4]:
                    cells.append(rr[5])
            for v in cells:
                if v in quot:
                    out.append("a committed value (%s) equals a quotient of two magnitudes of window %s" % (v, d["window"]))
    return out


def cross_route_problems(files, uk_annual, sw_rows):
    """G7: no committed number equals UK CH + Swiss CN, or UK CN_HK + Swiss CN_HK, for any completed Swiss year (kg, or tonnes to 3 decimals)."""
    if M("cross_route_off") or not sw_rows:
        return []
    bad = {}
    for r in sw_rows:
        if r[3] == "":
            continue
        y = r[0]
        if r[1] == "CN" and uk_annual.get((y, "CH", "cn71081310")):
            bad[int(uk_annual[(y, "CH", "cn71081310")]) + int(r[3])] = "UK CH + Swiss CN %s" % y
        if r[1] == "CN_HK" and uk_annual.get((y, "CN_HK", "cn71081310")):
            bad[int(uk_annual[(y, "CN_HK", "cn71081310")]) + int(r[3])] = "UK CN_HK + Swiss CN_HK %s" % y
    forb = {}
    for k, why in bad.items():
        forb[str(k)] = why
        forb[fnum(k / 1000.0, 3)] = why
    out = []
    for n, t in files.items():
        if n.endswith(".csv") and n != "fetch_log.csv":
            for col, v, _ in num_cells(t):
                if v in forb:
                    out.append("%s: %s=%s equals %s" % (n, col, v, forb[v]))
    return out


def all_folder_problems(files, sw, asof_year, uk_annual, sw_rows):
    monthly_values = swiss_monthly_values(sw) if sw else []
    out = folder_problems(files)
    for n, t in files.items():
        out += ["%s: %s" % (n, p) for p in wording_problems(n, t)]
    out += swiss_leak_problems(files, monthly_values, asof_year)
    out += swiss_prose_problems(files, monthly_values)
    out += swiss_difference_problems(files, sw)
    out += ratio_problems(files)
    out += cross_route_problems(files, uk_annual, sw_rows)
    return out


# ---- the static scan of this script (G14) ----------------------------------------------------------------------------------
FORBIDDEN_CALLS = re.compile(r"\b(os\.remove|os\.unlink|os\.rename|shutil\.rmtree|shutil\.move)\s*\(|\.(unlink|rename)\s*\(")


def static_stop_problems(src):
    """The script never removes, renames or truncates anything: no such call anywhere, and os.replace only in the two atomic writers."""
    if M("static_scan_off"):
        return []
    out = ["forbidden call: %s" % m.group(0) for m in FORBIDDEN_CALLS.finditer(src)]
    n = len(re.findall(r"os\.replace\s*\(", src))
    if n != 2:
        out.append("os.replace appears %d times (expected 2: write_text and write_bytes)" % n)
    for m in re.finditer(r"os\.replace\s*\([^)]*stop[^)]*\)", src, re.I):
        out.append("os.replace applied to a STOP path: %s" % m.group(0))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# README.md and SOURCES.md (generated, so the wording guards scan them)
# ------------------------------------------------------------------------------------------------------------------------
HELP_URL = "https://www.uktradeinfo.com/trade-data/help-with-using-our-data"          # read once by hand, 19 Oct 2026
HELP_QUOTE = "from the general trade to the special trade system"
OGL = "Contains public sector information licensed under the Open Government Licence v3.0."
HMRC_URL = "https://api.uktradeinfo.com"
CT_URL = "https://comtradeapi.un.org/public/v1/preview/C"


def md_table(head, rows, align=None):
    align = align or ["---"] * len(head)
    lines = ["| " + " | ".join(head) + " |", "|" + "|".join(align) + "|"]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(lines)


def retrieval_dates(fetch_rows, host):
    return sorted({r[0][:10] for r in fetch_rows if r[1] == host and r[3] == "200" and r[4]})


def render_readme(c):
    inp, S = c["inp"], c["S"]
    vd = inp["vintages"][-1][0]
    months, cells, L = S["months"], S["cells"], S["ctx_L"]
    arows = annual_lookup(S["annual"])
    last = months[-1]
    sw_rows = S["swiss_rows"]
    fr = inp.get("fetch_rows", [])
    hd, cd = retrieval_dates(fr, HMRC_HOST), retrieval_dates(fr, CT_HOST)
    t = lambda y, p: arows[(y, p, "cn71081310")]
    tonnes = lambda r: "blank" if r[3] == "" else fnum(int(r[3]) / 1000.0, 3)
    out = []
    A = out.append
    A("# UK customs declarations of semi-manufactured gold to China and Hong Kong\n")
    A(REQUIRED_OPEN + "\n")
    A("CN (the Combined Nomenclature, the UK tariff's classification) 71081310 is the tariff's own heading for %s. The kilograms are the declared net mass "
      "that HMRC (HM Revenue and Customs, the UK customs authority) records on export declarations to non-EU destinations; the "
      "latest HMRC pull in this folder is dated %s and its newest month is %s.\n" % (TARIFF_TEXT, vd, last))
    A("## What it leaves out\n")
    A("- **London vault transfers.** Gold that changes owner by book entry inside a London vault never appears on a customs declaration. This is a "
      "physical-movement series. It is not the change-of-ownership series of the ONS (Office for National Statistics).")
    A("- **The May 2016 break.** %s Months before May 2016 are general trade and are not like-for-like with later months; every annual and window row "
      "carries a `trade_system` column (`general`, `special` or `mixed` for 2016).%s" % (DENIAL_SENTENCE, (
        " HMRC's help page for its data (%s, read by hand on 19 Oct 2026) says that from May 2016 it changed how it compiles non-EU statistics, \"%s\", and "
        "that special trade excludes goods placed in customs warehouses. That page does not mention free zones; the free-zone exclusion comes from the project's written specification and has not been checked against an HMRC page." % (HELP_URL, HELP_QUOTE)) if HELP_QUOTE
        else " The May 2016 date comes from the project's written specification and has not been checked against an HMRC page."))
    A("- **Monetary gold** (CN 71082000) is suppressed by HMRC and is never in these figures.")
    A("- **Other routes into China.** Gold reaches China from Chinese mines, from Switzerland and from elsewhere, none of which this series sees.")
    A("- **Onward movement from Hong Kong.** Hong Kong is a trading hub and is not the reserve account of the People's Bank of China (PBoC); what leaves it for the mainland "
      "is outside this table.\n")
    A("## Why the figures are not compared with other sources\n")
    A("This folder prints three other magnitudes beside the UK kilograms, each in its own column and table, and computes no ratio, multiple or share of any two "
      "of them. The reasons are definitional. HMRC records gross physical declarations. The central-bank total of the World Gold Council (WGC) counts net additions and "
      "includes an estimate for reserves that governments do not report. Hong Kong is not the PBoC's reserve account. China's reserve change, reported by the "
      "State Administration of Foreign Exchange (SAFE), is a stock change. UK declarations and SAFE's reported additions measure different things, so a UK "
      "figure larger or smaller than SAFE's is expected either way and is not a comparison.\n")
    A("## The latest result\n")
    A("**UK declared net mass of CN 71081310, tonnes** (kilograms divided by 1,000; HMRC pull %s). `provisional` counts the months of the year that are within "
      "18 months of first publication; a year with a blank month has no total. Hong Kong and China are separate columns; `CN_HK` is their sum.\n" % vd)
    rows = []
    for y in range(2019, int(last[:4]) + 1):
        ys = str(y)
        cn, hk, ch = t(ys, "CN"), t(ys, "HK"), t(ys, "CN_HK")
        lab = ys if int(ch[5]) == 12 else "%s (%s to %s)" % (ys, "%s-01" % ys, last)
        rows.append([lab, ch[7], tonnes(cn), tonnes(hk), tonnes(ch), ch[8], ch[6]])
    A(md_table(["year", "trade_system", "China", "Hong Kong", "China + Hong Kong", "provisional months", "blank months"], rows, ["---", "---", "---:", "---:", "---:", "---:", "---:"]) + "\n")
    A("**Switzerland's exports of HS (Harmonized System) 710812 (unwrought gold), as reported to UN Comtrade, tonnes, completed years only.** HS 710812 and the UK's CN 71081310 are "
      "different headings, and Switzerland records imports by origin, so these are not a mirror of the UK figures and nothing here adds or compares the two.\n")
    if sw_rows is None:
        A("No Swiss figures are in this build: the Comtrade fetch ended before the cache was complete (%s). The UK series is complete without them.\n"
          % (inp.get("swiss_why") or "no reason recorded"))
    else:
        rows = []
        byy = {}
        for r in sw_rows:
            byy.setdefault(r[0], {})[r[1]] = r
        for y in sorted(byy):
            g = byy[y]
            tt = lambda r: "blank" if r[3] == "" else fnum(int(r[3]) / 1000.0, 3)
            rows.append([y, tt(g["CN"]), tt(g["HK"]), tt(g["CN_HK"]), g["CN_HK"][8]])
        A(md_table(["year", "China", "Hong Kong", "China + Hong Kong", "status"], rows, ["---", "---:", "---:", "---:", "---"]) + "\n")
    A("**Context magnitudes, tonnes, each in its own column.** UK: declared net mass of CN 71081310 to China and Hong Kong. SAFE: China's reported change in official "
      "gold reserves, as the gold ledger in `data/gold/` carries it. WGC: the World Gold Council's published central-bank total for the full year. Gap: the gold "
      "ledger's published WGC total minus the official total based on the IMF (International Monetary Fund), which the ledger itself says is not a measure of reserves that governments do not report. A blank is stated in "
      "`note` in `context.csv`.\n")
    rows = [[r[0], r[3], r[4] or "blank", r[8] or "blank", r[9] or "blank", r[10] or "blank"] for r in S["ctx"]]
    A(md_table(["window", "trade_system", "UK China + Hong Kong", "SAFE reported change", "WGC central banks", "WGC minus IMF gap"], rows,
               ["---", "---", "---:", "---:", "---:", "---:"]) + "\n")
    A("## Blank months\n")
    A("The two sources are treated differently, on purpose. A month for which HMRC has no row for a partner is written as **zero** (`status` `no_rows`): HMRC "
      "publishes every non-zero partner-month and no gold row has ever been suppressed or placed under a confidential country, which is an observed behaviour "
      "(19 Oct 2026) and not an HMRC statement. If any 7108 row in a month is suppressed or sits under a confidential country, the China, Hong Kong and "
      "all-destination cells of that month are blank (`unattributable`), and a suppressed partner row is blank (`suppressed`). A Comtrade month with no record is "
      "**blank**, never zero, because Comtrade is a reporter-submitted mirror and absence there is not evidence of zero. An annual total is blank when any of its "
      "months is blank. For the UK series `net_mass_kg_known_months` then holds the sum of the known months; for the Swiss series it stays blank, so that no single "
      "month can be recovered by subtraction.\n")
    A("## Columns\n")
    A("`monthly.csv`: `month`; `partner` (`CN` China, `HK` Hong Kong, `CN_HK` their sum, `CH` Switzerland as an upstream refining leg, `ALL_NON_EU` every non-EU "
      "destination); `series` (`cn71081310` is %s; `other` is CN 71081200 plus 71081380; `powder` is CN 71081100, kept in no other series); `net_mass_kg` is the sum "
      "of HMRC `NetMass` over ports and codes, over rows with `SuppressionIndex` 0; `supp_unit_div_1000` is the supplementary quantity ÷ 1,000 (grams under the CN), "
      "not reconciled to net mass, and it is not used in any result; `rows_n`; `status`; `trade_system`; `provisional`; `vintage` (the pull date). "
      "Quantities published by WITS (the World Bank's World Integrated Trade Solution) are supplementary quantities and differ from net mass by kilograms (China 2024: "
      "382,802 against 382,786 kg, as read by a reviewer on WITS and not re-read here).\n" % TARIFF_TEXT)
    A("`annual.csv`: the same by calendar year, with `months_n`, `months_blank`, `net_mass_kg_known_months` and `provisional_months`. `swiss_mirror_annual.csv`: Swiss "
      "HS 710812 by completed year, `net_wgt_estimated_months` counting months Comtrade flags as estimated, `comtrade_annual_kg` the annual record and "
      "`monthly_sum_minus_annual_kg` the difference of the two. `context.csv`: the magnitudes above. `revisions.csv`: every changed cell between two HMRC pulls, "
      "append-only. `summary.csv`: the pre-registered descriptive questions, with `blind`. `checks.csv`: the checks. `fetch_log.csv`: every request.\n")
    # worked row
    jan = [r for r in inp["vintages"][-1][1] if r.month == "2024-01" and r.country == 720 and r.code == 71081310 and r.supp == 0]
    mrow = next(r for r in S["monthly"] if r[0] == "2024-01" and r[1] == "CN" and r[2] == "cn71081310")
    A("## One worked row\n")
    A("China, CN 71081310, January 2024: HMRC holds %s; their sum is the single `monthly.csv` row `%s`." % (
        " and ".join("a row for port %s of %s kg" % (r.port, kgs(r.kg)) for r in sorted(jan, key=lambda r: str(r.port))) or "no rows", ",".join(mrow)) + "\n")
    A("## Provenance\n")
    A("%s HMRC Overseas Trade Statistics (`api.uktradeinfo.com`), non-EU exports, retrieved %s. Swiss figures: UN Comtrade public preview (`comtradeapi.un.org`), "
      "reporter Switzerland, retrieved %s. UN Comtrade data are for internal use and may not be re-disseminated without the permission of the United Nations Statistics Division (UNSD), except limited amounts "
      "in a few tables; only completed-year totals per partner are published here, and monthly Swiss values stay in an ignored cache. The first Comtrade backfill "
      "is about 176 calls (about 18 minutes at 6 seconds) and may end on a 429, in which case the build ships UK-only and says so. SAFE: \"Official Reserve "
      "Assets\"; WGC: Gold Demand Trends; both as the gold ledger (`data/gold/`) cites them. "
      "Build decisions, including one fix made after the first build, are listed in [SOURCES.md](SOURCES.md).\n" % (
          OGL, ", ".join(hd) or "(no logged retrieval)", ", ".join(cd) or "(no logged retrieval)"))
    return "\n".join(out)


PARTNER_WORDS = {"CN": "China", "HK": "Hong Kong", "CN_HK": "China plus Hong Kong"}


def decisions(c):
    inp, S = c["inp"], c["S"]
    d = [
        "A month is `unattributable` when any 7108 non-EU-export row of that month, in any code, sits under CountryId 950 or above or carries a suppression index; "
        "the spec's \"that series\" is read as applying the month-level trigger to each series (the stricter reading; no such row exists on the 19 Oct 2026 pull).",
        "First publication for a month already in the oldest pull is the first day of the month two after it (HMRC publishes month M in month M+2). The spec's \"month's "
        "end plus 2 months\" taken to the day gives a different 2025-02, and only the month-level reading reproduces the spec's own statement that 2025-03 onward is "
        "provisional and 2024 is final on the 19 Oct 2026 pull.",
        "Sums of `NetMass` are rounded to whole kilograms in the outputs; the count of rows with fractional kilograms is in `checks.csv`.",
        "`summary.csv` has no `trade_system` column, so every window label carries it in square brackets, and no window crosses May 2016 except 2016 itself (`mixed`).",
        "A Comtrade reply that breaks a partner down by transport mode, second partner or customs procedure is reduced to its total record (modes 0, partner2 0, "
        "customs C00 where those fields exist); two total records for one partner and month stop the Swiss section as a data error.",
        "In the Swiss leak scan a zero is not compared with a monthly value, since zero is not a disclosure.",
        "The HMRC lookups are the entity sets `/FlowType`, `/Country` and `/Commodity` (the last filtered on `Cn8Code`); the spec names the facts, not the paths, and "
        "a path that fails latches the HMRC source as the spec requires.",
        "The cross-check of the 2024 China sums against HMRC's own group-by reply is tested with the relaxed rule that the reply names the Overseas Trade Statistics in its context "
        "and that every row is a 2024 month with a numeric `kg`.",
        "A STOP file holds `status`, `utc_time`, `url_path`, `retry_after` and `body_head` as five `name: value` lines; the file is created exclusively and never rewritten.",
        "Every number in `summary.csv` for a window is the same figure as in `annual.csv` or `context.csv`; none is a new computation across sources.",
        "The pinned 2024 figures in `checks.csv` fail on a pull made before HMRC's next release (12 Nov 2026) and warn afterwards; the Swiss and context pins are pass or fail only.",
    ]
    if S["swiss_rows"] is None:
        d.append("This build is UK-only: %s. `swiss_mirror_annual.csv` holds its header only, the Swiss column of `context.csv` is blank and the Swiss question in `summary.csv` is marked not available."
                 % (inp.get("swiss_why") or "no reason recorded"))
    else:
        d.append("The Swiss section is built from a complete Comtrade cache (monthly replies from 2012-01 and annual replies for each completed year); the first backfill of 191 requests on 19 Oct 2026 ended without a refusal.")
        d.append("Fix made after the first build: a Swiss known-months cell equal to a cached monthly value was blanked after the first build, because the licence rule forbids any Swiss cell "
                 "equal to a cached monthly value unless it equals a completed-year total.")
        d.append("Supervisor ruling after verification: `net_mass_kg_known_months` is left blank for every Swiss partial year and every partner, not only the clashing cell, because a monthly "
                 "value could otherwise be recovered by adding and subtracting the China, Hong Kong and China-plus-Hong-Kong cells of one year, and a month filled in later would show "
                 "as a rise between versions. The UK columns of the same name are unaffected, since the UK source carries an open licence. In this build the blank cells are: %s."
                 % ("; ".join("%s %s" % (y, PARTNER_WORDS[pn]) for y, pn in (inp["swiss"].get("blanked") or [])) or "none"))
        d.append("Supervisor ruling after verification: the Swiss leak scan reads every committed file that can carry Swiss-derived numbers, including this file, the README and "
                 "`summary.csv`, for any cached Swiss monthly value (in kilograms or tonnes); it skips only the three tables of HMRC kilograms and the request log, where a "
                 "coincidence with a Swiss value would not be a disclosure (the two Swiss tables are scanned column by column).")
        d.append("Comtrade may leave a month out when there was no trade; the spec still leaves such years blank.")
    if HELP_QUOTE:
        d.append("The May 2016 date was checked against HMRC's help page, fetched once by hand (not by the script) on 19 Oct 2026 at 13:18 UTC with the neutral user agent: "
                 "HTTP 200, 77,391 bytes, no redirect followed. It confirms the move from general to special trade in May 2016 and the exclusion of goods in customs warehouses.")
    if inp.get("decisions_extra"):
        d += list(inp["decisions_extra"])
    return d


def render_sources(c):
    inp = c["inp"]
    fr = inp.get("fetch_rows", [])
    hd, cd = retrieval_dates(fr, HMRC_HOST), retrieval_dates(fr, CT_HOST)
    o = ["# Sources\n",
         "## HM Revenue and Customs (HMRC) Overseas Trade Statistics\n",
         "- URL: `%s` (entity `/OTS`, lookups `/FlowType`, `/Country`, `/Commodity`); documentation https://www.uktradeinfo.com/api-documentation/. Retrieved: %s." % (HMRC_URL, ", ".join(hd) or "(no logged retrieval)"),
         "- Licence: Open Government Licence v3.0 (\"All content is available under the Open Government Licence v3.0, except where otherwise stated\"). %s" % OGL,
         "- Feeds: `monthly.csv`, `annual.csv`, `revisions.csv`, `summary.csv`, the UK columns of `context.csv`, and the checks.",
         "- Filter: CN8 (eight-digit Combined Nomenclature) codes 71080000 to 71089999, FlowTypeId 4 (non-EU exports), every partner and month; `SuppressionIndex` 0 only; `Value` is used only for the implied-price check and no sterling value is committed.",
         "- Blank-month basis (supervisor ruling): a missing partner-month is zero only when no gold row that month is suppressed or confidential. This rests on HMRC's observed behaviour on 19 Oct 2026 (no 7108 row has ever been suppressed or under a confidential country), not on an HMRC statement.",
         "- Provisional months: a month is provisional until 18 months after its first publication (a rule taken from the project's specification and not checked against an HMRC statement; the revisions summary measures it on real pulls). For months already in the oldest pull the first publication is approximated as the first day of the month two after it.",
         "- Release calendar: September 2026 on 12 Nov 2026, October on 11 Dec, November on 15 Jan 2027.",
         "",
         "## UN Comtrade public preview (Swiss mirror)\n",
         "- URL: `%s` (keyless preview), reporter 757, HS (Harmonized System) 710812, partners 156 and 344, flow X; UK cross-check reporter 826, HS 710813, partner 156, 2024. Retrieved: %s." % (CT_URL, ", ".join(cd) or "(no logged retrieval)"),
         "- Terms: UN Comtrade data are for internal use only and may not be re-disseminated in any form without the permission of the United Nations Statistics Division (UNSD), except publication of limited amounts in a few tables. Only completed-year totals per partner are committed; monthly values stay in the ignored cache.",
         "- Feeds: `swiss_mirror_annual.csv` and the Swiss column of `context.csv`. Fields kept: `netWgt`, `isNetWgtEstimated`; a record is never dropped for `isReported` false.",
         "- Comtrade re-publishes the Swiss customs submission; no scriptable Swiss customs route exists (the tariff-by-country file is a 690 MB archive and its terms are by request).",
         "",
         "## Context magnitudes\n",
         "- `data/gold/ledger_annual_reconciliation.csv` and `data/gold/ledger_monthly.csv` in this repository (SAFE, the State Administration of Foreign Exchange, \"Official Reserve Assets\"; WGC, the World Gold Council, Gold Demand Trends), read-only. The figures are copied as the ledger carries them.",
         ""]
    if HELP_URL:
        o += ["## HMRC help page\n", "- %s, read once by hand on the date in the build decisions below; what it confirms is in the build decisions below." % HELP_URL, ""]
    o += ["## Build decisions\n"] + ["- " + d for d in decisions(c)] + [""]
    return "\n".join(o)


# ------------------------------------------------------------------------------------------------------------------------
# rendering all outputs
# ------------------------------------------------------------------------------------------------------------------------
def src_hmrc(c, what):
    hd = retrieval_dates(c["inp"].get("fetch_rows", []), HMRC_HOST)
    return "# source: HMRC Overseas Trade Statistics API (api.uktradeinfo.com), Open Government Licence v3.0, retrieved %s; %s" % (", ".join(hd) or "(no logged retrieval)", what)


def render_texts(c):
    inp, S = c["inp"], c["S"]
    cd = retrieval_dates(inp.get("fetch_rows", []), CT_HOST)
    t = {}
    t["monthly.csv"] = render_csv("monthly.csv", S["monthly"], src_hmrc(c, "net mass summed over ports and codes; vintage = pull date"))
    t["annual.csv"] = render_csv("annual.csv", S["annual"], src_hmrc(c, "calendar-year sums of monthly.csv"))
    sw_src = ("# source: UN Comtrade public preview (comtradeapi.un.org), Switzerland as reporter, HS 710812, flow X, retrieved %s; completed calendar years only; "
              "monthly values stay in the cache" % (", ".join(cd) or "(no logged retrieval)"))
    t["swiss_mirror_annual.csv"] = render_csv("swiss_mirror_annual.csv", S["swiss_rows"] or [], sw_src if S["swiss_rows"] is not None else
                                                "# source: UN Comtrade public preview (comtradeapi.un.org); no Swiss data in this build (UK-only)")
    t["context.csv"] = render_csv("context.csv", S["ctx"], src_hmrc(c, "with data/gold/ledger_annual_reconciliation.csv and ledger_monthly.csv (SAFE Official Reserve Assets; "
                                                                 "WGC Gold Demand Trends) and UN Comtrade for the Swiss column; separate magnitudes, no ratio"))
    t["revisions.csv"] = render_csv("revisions.csv", S["revisions"], src_hmrc(c, "append-only: one row per changed partner-month cell between two dated pulls"))
    t["summary.csv"] = render_csv("summary.csv", S["summary"], src_hmrc(c, "descriptive questions Q1 to Q8; blind = no where the author or a reviewer had seen the figures"))
    t["checks.csv"] = render_csv("checks.csv", sorted(c["checks"], key=lambda r: r[0]), src_hmrc(c, "checks of bin/uk_gold_exports.py build"))
    fr = inp.get("fetch_rows", [])
    t["fetch_log.csv"] = render_csv("fetch_log.csv", fr, fetch_source_line(fr))
    t["README.md"] = render_readme(c)
    t["SOURCES.md"] = render_sources(c)
    for n in ("README.md", "SOURCES.md"):
        guard_text(n, t[n])
    return t


def texts_digest(texts):
    return {n: sha256_of(x.encode("utf-8")) for n, x in sorted(texts.items()) if n != "checks.csv"}


def guard_files(c, texts):
    inp, S = c["inp"], c["S"]
    sw = inp.get("swiss")
    ua = {(r[0], r[1], r[2]): r[3] for r in S["annual"]}
    return all_folder_problems(texts, sw, S["vdate"].year, ua, S["swiss_rows"])


def finish(c):
    """Add C11 (a second build leaves every file unchanged, revisions.csv included) and C16 (the folder guards run on the real rendering)."""
    t1 = render_texts(c)
    inp2 = dict(c["inp"])
    inp2["existing_revisions"] = [r for r in read_rows_text(t1["revisions.csv"])]
    inp2["existing_monthly"] = read_rows_text(t1["monthly.csv"])
    c2 = compute(inp2)
    t2 = render_texts(c2)
    if M("render_unstable"):
        t2["monthly.csv"] += "x"
    same = texts_digest(t1) == texts_digest(t2)
    c["checks"] = c["checks"] + [["C11", "Fixed output: a second build over the same cache leaves every file's sha256 unchanged, revisions.csv included", "identical",
                                   "identical (%d files)" % len(texts_digest(t1)) if same else "DIFFERENT", "PASS" if same else "FAIL"]]
    probs = guard_files(c, t1)
    c["checks"] = c["checks"] + [["C16", "Folder guards on the rendering: ten names, exact headers, no raw file, Swiss leak places, no ratio, no cross-route sum, wording", "no problem",
                                   "; ".join(probs[:3]) if probs else "no problem", "FAIL" if probs else "PASS"]]
    texts = render_texts(c)
    failed = [r[0] for r in c["checks"] if r[4] == "FAIL"]
    return texts, failed


def read_rows_text(text):
    return csv_body(text)[1]


# ------------------------------------------------------------------------------------------------------------------------
# inputs from the cache
# ------------------------------------------------------------------------------------------------------------------------
VINT_RX = re.compile(r"ots_7108_f4_(\d{4}-\d{2}-\d{2})\.json$")


def load_vintages(cache):
    d = os.path.join(cache, "hmrc")
    out = []
    for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        m = VINT_RX.search(fn)
        if not m:
            continue
        with open(os.path.join(d, fn), "rb") as fh:
            doc, bad = _json(fh.read())
        if bad:
            raise DataError("%s is not JSON" % fn)
        prob = test_ots_page(doc, True, D_(m.group(1)))
        if prob:
            raise DataError("%s: %s" % (fn, prob))
        if len(doc["value"]) != doc["@odata.count"] and not M("count_mismatch_ok"):
            raise DataError("%s: rows %d != @odata.count %d" % (fn, len(doc["value"]), doc["@odata.count"]))
        out.append((m.group(1), parse_rows(doc)))
    return out


def load_dated_json(cache, prefix, date):
    d = os.path.join(cache, "hmrc")
    exact = os.path.join(d, "%s_%s.json" % (prefix, date))
    cands = [exact] if os.path.exists(exact) else sorted(os.path.join(d, f) for f in (os.listdir(d) if os.path.isdir(d) else []) if f.startswith(prefix + "_"))[-1:]
    if not cands:
        return None
    with open(cands[0], "rb") as fh:
        doc, bad = _json(fh.read())
    return None if bad else doc


def load_inputs(cache, out_dir, ledger_annual, ledger_monthly):
    vint = load_vintages(cache)
    if not vint:
        raise DataError("no HMRC pull in the cache (%s/hmrc); run fetch first" % tilde(cache))
    date = vint[-1][0]
    la, lm = load_ledger(ledger_annual, ledger_monthly)
    sw, why = load_swiss(cache, D_(date).year - 1)
    _, rev = read_csv_rows(os.path.join(out_dir, "revisions.csv"))
    _, mon = read_csv_rows(os.path.join(out_dir, "monthly.csv"))
    _, fr = read_csv_rows(os.path.join(out_dir, "fetch_log.csv"))
    return dict(vintages=vint, apply_doc=load_dated_json(cache, "apply_c05", date),
                lookups={k: load_dated_json(cache, "lookup_" + k, date) for k in ("flowtype", "country", "commodity")},
                swiss=sw, swiss_why=why, ledger_annual=la, ledger_monthly=lm, existing_revisions=rev, existing_monthly=mon, fetch_rows=fr,
                decisions_extra=read_decisions_extra(cache))


def read_decisions_extra(cache):
    p = os.path.join(cache, "decisions_extra.txt")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        return [l.strip() for l in fh if l.strip()]


def write_outputs(c, texts, out_dir, cache, failed):
    target = os.path.join(out_dir, "_FAILED") if failed and not M("failed_to_committed") else out_dir
    for n, x in texts.items():
        write_text(os.path.join(target, n), x)
    sw = c["inp"].get("swiss")
    if sw:
        write_text(os.path.join(cache, "swiss_monthly.csv"), swiss_monthly_text(sw))
    return target


def run_build(a):
    t0 = time.time()
    cache = check_cache(a.cache, out_dir=a.out)
    inp = load_inputs(cache, a.out, a.ledger_annual, a.ledger_monthly)
    c = compute(inp)
    texts, failed = finish(c)
    target = write_outputs(c, texts, a.out, cache, failed)
    S = c["S"]
    print("vintage %s; months %s to %s; swiss section: %s" % (inp["vintages"][-1][0], S["months"][0], S["months"][-1], "built" if S["swiss_rows"] is not None else "UK-only"))
    print("== checks")
    for r in c["checks"]:
        print("   %-5s %-5s %s" % (r[0], r[4], r[3][:170]))
    print("== annual tonnes, cn71081310 (year trade_system CN HK CN_HK provisional_months blank_months)")
    arows = annual_lookup(S["annual"])
    for y in range(2019, int(S["months"][-1][:4]) + 1):
        g = lambda p: arows[(str(y), p, "cn71081310")]
        print("   %d %-8s %10s %10s %10s  prov=%s blank=%s" % (y, g("CN_HK")[7], tons(float(g("CN")[3])) if g("CN")[3] else "blank", tons(float(g("HK")[3])) if g("HK")[3] else "blank",
                                                             tons(float(g("CN_HK")[3])) if g("CN_HK")[3] else "blank", g("CN_HK")[8], g("CN_HK")[6]))
    print("== context rows")
    for r in S["ctx"]:
        print("   " + " | ".join(r[:11]))
    print("failed: %s; wrote %d files to %s (%.1f s)" % (", ".join(failed) or "none", len(texts), tilde(target), time.time() - t0))
    return 1 if failed else 0


# ------------------------------------------------------------------------------------------------------------------------
# selftest: synthetic data only. Every guard G1-G18 of the spec's section 8 has a test; each mutant (a deliberately broken variant, switched on in
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


def OR(month, kg=1000.0, code=71081310, country=720, port=428, supp=0, value=None, unit=None):
    """One synthetic HMRC /OTS row."""
    return {"MonthId": monthid(month), "FlowTypeId": 4, "SuppressionIndex": supp, "CommodityId": code, "CommoditySitcId": 97110, "CountryId": country,
            "PortId": port, "Value": kg * 52000.0 if value is None else value, "NetMass": kg, "SuppUnit": kg * 1000.0 if unit is None else unit}


def rows_from(raw):
    return parse_rows({"value": raw})


def ots_doc(raw, count=None, nxt=None):
    d = {"@odata.context": "https://api.uktradeinfo.com/$metadata#OTS", "value": raw}
    if count is not None:
        d["@odata.count"] = count
    if nxt:
        d["@odata.nextLink"] = nxt
    return d


def jb(doc):
    return json.dumps(doc).encode("utf-8")


def synthetic_raw():
    raw = []
    for i, m in enumerate(months_between("2005-01", "2026-08")):
        raw.append(OR(m, 1000 + i, country=720))
        raw.append(OR(m, 100 + (i * 7) % 13, country=740, port=3))
        raw.append(OR(m, 50 + i % 5, country=39, port=7))
        raw.append(OR(m, 500 + i, country=600, port=9))
        if i % 5 == 0:
            raw.append(OR(m, 3 + i % 4, code=71081380, country=740, port=3))
        if i % 17 == 0:
            raw.append(OR(m, 2, code=71081100, country=740, port=3))
    raw = [r for r in raw if not (r["MonthId"] == 202401 and r["CountryId"] == 720)]
    raw += [OR("2024-01", 25046, port=428), OR("2024-01", 0, port=434), OR("2021-03", 5, country=977, port=987)]
    return raw


def synthetic_ledger():
    la = {}
    for y in range(2019, 2026):
        la[y] = {"period": str(y), "china_change_t": "%.3f" % (10 + y % 7), "wgc_central_banks_fy_published_t": ("%.1f" % (1000 + y)) if y >= 2022 else "",
                 "gap_wgc_fy_published_minus_imf_t": ("%.3f" % (500 + y % 11)) if y >= 2022 else ""}
    lm = {m: {"month": m, "china_change_t": "1.000"} for m in months_between("2019-01", "2026-09")}
    return la, lm


def synthetic_swiss():
    mon, ann = {}, {}
    for i, m in enumerate(months_between("2012-01", "2025-12")):
        mon[m] = {"CN": (40000.0 + 13 * i, i % 10 == 0, 1e6), "HK": (20000.0 + 7 * i + (i % 3) * 1000, False, 5e5)}
    mon["2013-05"]["HK"] = None
    for y in range(2012, 2026):
        ms = months_between("%d-01" % y, "%d-12" % y)
        ann[y] = {"CN": sum(mon[m]["CN"][0] for m in ms) + (3 if y == 2020 else 0), "HK": sum(mon[m]["HK"][0] for m in ms if mon[m]["HK"])}
    return {"months": mon, "annual": ann, "uk2024": 382787.0}


def synthetic_inp(raw=None, swiss=True):
    la, lm = synthetic_ledger()
    return dict(vintages=[("2026-10-19", rows_from(raw if raw is not None else synthetic_raw()))], apply_doc=None, lookups={}, swiss=synthetic_swiss() if swiss else None,
                swiss_why="synthetic", ledger_annual=la, ledger_monthly=lm, existing_revisions=[], existing_monthly=[], fetch_rows=[], decisions_extra=[])


_WORLD = {}


def get_world():
    """The synthetic world, built once, with no mutant active (the guard functions are then mutated against its clean files)."""
    if not _WORLD:
        if _ACTIVE:
            raise RuntimeError("the synthetic world must be built before any mutant is switched on")
        inp = synthetic_inp()
        c0 = compute(inp)
        texts, failed = finish(dict(c0))
        _WORLD.update(inp=inp, c0=c0, S=c0["S"], texts=texts, failed=failed)
    return _WORLD


def world_files():
    return {n: t for n, t in get_world()["texts"].items()}


def fake_rig(tmp, source, handler, stop_dir=None, clock=None, **kw):
    clock = clock or FakeClock()
    calls = []

    def opener(host, target, headers, timeout, cap):
        calls.append((host, target, dict(headers), clock.wall()))
        return handler(host, target, headers)
    fe = Fetcher(source, os.path.join(tmp, "cache"), os.path.join(tmp, "out"), stop_dir=stop_dir or os.path.join(tmp, "stop"), opener=opener, wall=clock.wall,
                 mono=clock.wall, sleeper=clock.sleep, now_utc=lambda: dt.datetime(2026, 10, 19, 12, 0, tzinfo=dt.timezone.utc), **kw)
    return fe, calls, clock


def ok200(doc):
    return lambda host, target, hdrs: (200, jb(doc), {})


def t_g1(ck):
    rows = rows_from([OR("2024-01", 0, port=434), OR("2024-01", 25046, port=428), OR("2024-02", 100, port=1), OR("2024-02", 200, port=2), OR("2024-02", 300, port=3)])
    cells = aggregate(rows)
    ck.eq("2024-01 China: port 434 (0 kg) and port 428 (25,046 kg) sum to 25,046", cells[("2024-01", "CN", "cn71081310")].kg, 25046)
    ck.eq("a three-port month sums all three ports", cells[("2024-02", "CN", "cn71081310")].kg, 600)
    ck.eq("rows_n counts the port rows", cells[("2024-02", "CN", "cn71081310")].rows_n, 3)


def t_g2(ck):
    raw = [OR("2024-05", 500), OR("2024-05", 70, country=740), OR("2024-06", 70, country=740), OR("2024-07", 900, country=977, port=987), OR("2024-07", 40),
           OR("2024-08", 0), OR("2024-08", 10, country=740)]
    cells = aggregate(rows_from(raw))
    c = lambda m, p: cells[(m, p, "cn71081310")]
    ck.ok("HMRC absence is zero with status no_rows", c("2024-06", "CN").kg == 0 and c("2024-06", "CN").status == "no_rows")
    ck.ok("a month with a 977 gold row: China is blank, unattributable", c("2024-07", "CN").kg is None and c("2024-07", "CN").status == "unattributable")
    ck.ok("...and so are Hong Kong and CN_HK", c("2024-07", "HK").kg is None and c("2024-07", "CN_HK").kg is None)
    ck.ok("...and ALL_NON_EU is blank in an unattributable month", c("2024-07", "ALL_NON_EU").kg is None)
    ck.ok("...Switzerland is not blanked by the trigger", c("2024-07", "CH").kg == 0)
    ck.ok("a NetMass 0 row is ok with 0 kg, not no_rows", c("2024-08", "CN").status == "ok" and c("2024-08", "CN").kg == 0)
    months = month_range(rows_from(raw))
    ar = annual_lookup(annual_table(cells, months, {m: False for m in months}, "v"))
    r = ar[("2024", "CN", "cn71081310")]
    ck.ok("an annual total is blank when a month is blank, the known months beside it", r[3] == "" and r[4] != "" and r[6] == "1")
    W = get_world()
    la, lm = W["inp"]["ledger_annual"], W["inp"]["ledger_monthly"]
    ctx, L = context_rows(W["S"]["cells"], W["S"]["months"], la, lm, W["S"]["swiss_rows"], 2026, W["inp"]["swiss"]["months"])
    r21 = next(r for r in ctx if r[0] == "2021")
    ck.ok("a context UK magnitude is blank over a blank month (2021-03 has a confidential row), with a note", r21[4] == "" and r21[2] == "1" and "blank" in r21[11])
    ck.ok("...and a clean year is filled", next(r for r in ctx if r[0] == "2022")[4] != "")
    sw = synthetic_swiss()
    sw["months"]["2020-07"]["CN"] = None
    rows, first = swiss_years(sw, 2025)
    r20 = next(r for r in rows if r[0] == "2020" and r[1] == "CN")
    ck.ok("a Comtrade month with no record is blank, never 0: the year is partial", r20[8] == "partial" and r20[3] == "" and r20[6] == "1")


def t_g3(ck):
    cells = aggregate(rows_from([OR("2024-03", 40), OR("2024-03", 99, supp=5), OR("2024-03", 10, country=740)]))
    c = cells[("2024-03", "CN", "cn71081310")]
    ck.ok("a China row with SuppressionIndex 5 makes the cell suppressed and blank", c.kg is None and c.status == "suppressed")
    ck.ok("...and CN_HK is blank with the worse status", cells[("2024-03", "CN_HK", "cn71081310")].kg is None and cells[("2024-03", "CN_HK", "cn71081310")].status == "suppressed")


def t_g4(ck):
    raw = [OR("2024-05", 1000, country=740), OR("2024-05", 7000, code=71082000, country=740), OR("2024-05", 30, code=71081100, country=740),
           OR("2024-05", 200, code=71081200, country=740), OR("2024-05", 50, code=71081380, country=740), OR("2024-05", 9, code=71081390, country=740)]
    rows = rows_from(raw)
    cells = aggregate(rows)
    ck.eq("71082000 is in no series: cn71081310 is 1,000", cells[("2024-05", "HK", "cn71081310")].kg, 1000)
    ck.eq("powder is in no other series: other = 71081200 + 71081380 = 250", cells[("2024-05", "HK", "other")].kg, 250)
    ck.eq("powder is its own row", cells[("2024-05", "HK", "powder")].kg, 30)
    ck.eq("an unknown 7108 code (71081390) is reported", unknown_codes(rows), [71081390])


def t_g5(ck):
    today = D_("2026-10-19")
    ok = ots_doc([OR("2024-01")], 1)
    ck.eq("a flow-4 page passes", test_ots_page(ok, True, today), None)
    for flow in (3, 2):
        bad = ots_doc([dict(OR("2024-01"), FlowTypeId=flow)], 1)
        ck.ok("FlowTypeId %d is refused" % flow, test_ots_page(bad, True, today) is not None)
    good = {"value": [{"FlowTypeId": 4, "FlowTypeDescription": "Non-EU Exports   "}]}
    ck.eq("FlowType 4 labelled 'Non-EU Exports' (space-padded) passes", test_flowtype(good), None)
    ck.ok("a lookup labelling 4 'Non-EU Imports' is refused", test_flowtype({"value": [{"FlowTypeId": 4, "FlowTypeDescription": "Non-EU Imports"}]}) is not None)
    reply = lambda flow: {"error": "", "data": [{"reporterCode": 757, "flowCode": flow, "cmdCode": "710812", "period": "202401", "partnerCode": 156}]}
    ck.eq("Comtrade flowCode X passes", test_comtrade(reply("X"), 757, 710812, "202401", [156, 344]), None)
    ck.ok("Comtrade flowCode M is refused", test_comtrade(reply("M"), 757, 710812, "202401", [156, 344]) is not None)
    ck.raises("a Comtrade request for flowCode M is refused before sending", Refused, lambda: check_url("https://comtradeapi.un.org" + ct_target("M", 757, "202401", [156, 344], "710812", flow="M")))


def t_g6(ck):
    cells = aggregate(rows_from([OR("2024-01", 100), OR("2024-01", 305, country=39), OR("2024-01", 5, country=740), OR("2024-02", 100), OR("2024-02", 8, country=740, supp=5)]))
    ck.eq("720 is China (100), not Switzerland", cells[("2024-01", "CN", "cn71081310")].kg, 100)
    ck.eq("39 is Switzerland (305)", cells[("2024-01", "CH", "cn71081310")].kg, 305)
    ck.eq("CN_HK = CN + HK = 105", cells[("2024-01", "CN_HK", "cn71081310")].kg, 105)
    ck.eq("CN_HK is blank when HK is blank (HK suppressed, CN 100)", cells[("2024-02", "CN_HK", "cn71081310")].kg, None)


def t_g7(ck):
    W = get_world()
    files = world_files()
    ua = {(r[0], r[1], r[2]): r[3] for r in W["S"]["annual"]}
    sw = W["S"]["swiss_rows"]
    ck.eq("the clean folder has no cross-route sum", cross_route_problems(files, ua, sw), [])
    r = next(x for x in sw if x[0] == "2020" and x[1] == "CN")
    s1 = int(ua[("2020", "CH", "cn71081310")]) + int(r[3])
    r2 = next(x for x in sw if x[0] == "2022" and x[1] == "CN_HK")
    s2 = int(ua[("2022", "CN_HK", "cn71081310")]) + int(r2[3])
    for tag, val in (("UK CH + Swiss CN", str(s1)), ("UK CN_HK + Swiss CN_HK", fnum(s2 / 1000.0, 3))):
        f2 = dict(files)
        f2["summary.csv"] = f2["summary.csv"] + "Q6,2022 [special],CN_HK,x,y,%s,yes,\n" % val
        ck.ok("a committed number equal to %s is reported" % tag, bool(cross_route_problems(f2, ua, sw)))


def t_g8(ck):
    ck.eq("NetMass is read as kilograms", rows_from([OR("2024-01", 25046)])[0].kg, 25046.0)
    ck.eq("tonnes = kg / 1,000", tons(25046), "25.046")
    files = world_files()
    ck.eq("the clean folder has no ratio-like column and no quotient value", ratio_problems(files), [])
    f2 = dict(files)
    f2["context.csv"] = f2["context.csv"].replace("swiss_710812_cn_hk_t", "uk_over_safe_multiple", 1)
    ck.ok("a column named like a multiple is reported", bool(ratio_problems(f2)))
    h, rows = csv_body(files["context.csv"])
    r = next(dict(zip(h, x)) for x in rows if x[0] == "2022")
    q = fnum(float(r["uk_71081310_cn_hk_t"]) / float(r["safe_reported_change_t"]), 3)
    f3 = dict(files)
    f3["summary.csv"] = f3["summary.csv"] + "Q2,2022 [special],CN_HK,x,y,%s,yes,\n" % q
    ck.ok("a committed value equal to a quotient of two magnitudes of one window is reported", bool(ratio_problems(f3)))


def fixture_vints():
    v1 = ("2026-10-19", rows_from([OR("2024-01", 25046, port=428), OR("2024-01", 0, port=434), OR("2026-08", 100)]))
    v2 = ("2026-11-12", rows_from([OR("2024-01", 25100, port=428), OR("2024-01", 0, port=434), OR("2026-08", 110), OR("2026-09", 5)]))
    return v1, v2


def t_g9(ck):
    v1, v2 = fixture_vints()
    c1 = aggregate(v1[1])
    bogus = monthly_table(c1, month_range(v1[1]), {m: False for m in month_range(v1[1])}, "x")
    for r in bogus:
        if r[:3] == ["2024-01", "CN", "cn71081310"]:
            r[3] = "99999"
    rr = revision_rows([v1, v2], [], bogus)
    ck.ok("the first vintage gets one baseline marker row", rr and rr[0][0] == "baseline" and rr[0][1] == "2026-10-19" and rr[0][2:] == [""] * 7)
    row = next((r for r in rr if r[2:5] == ["2024-01", "CN", "cn71081310"]), None)
    ck.ok("a changed cell is recorded with kg_prev from the previous dated pull (25046), kg_new, change, provisional_at_prev", row == ["2026-10-19", "2026-11-12", "2024-01", "CN", "cn71081310", "25046", "25100", "54", "no"], str(row))
    r8 = next((r for r in rr if r[2:5] == ["2026-08", "CN", "cn71081310"]), None)
    ck.ok("a recent month was provisional at the previous pull", r8 is not None and r8[8] == "yes")
    ck.ok("a new month is not a revision", not any(r[2] == "2026-09" for r in rr))
    rr2 = revision_rows([v1, v2], rr, bogus)
    ck.ok("a second run appends nothing: no key twice, existing rows unchanged and in order", rr2 == rr, "len %d vs %d" % (len(rr2), len(rr)))
    mid = [["a", "b", "2024-01", "CN", "cn71081310", "1", "2", "1", "no"]] + rr[1:3]
    rr3 = revision_rows([v1, v2], mid, bogus)
    ck.ok("existing rows are never reordered", rr3[:len(mid)] == mid)
    # provisional is measured from first publication
    rows3 = rows_from([OR(m, 1) for m in months_between("2026-01", "2028-03")])
    p_a = provisional_flags([v1, v2, ("2028-05-11", rows3)], ["2026-09", "2026-08"])
    p_b = provisional_flags([v1, v2, ("2028-05-13", rows3)], ["2026-09", "2026-08"])
    ck.ok("a month first published 2026-11-12 is provisional on 2028-05-11", p_a["2026-09"] is True)
    ck.ok("...and final on 2028-05-13", p_b["2026-09"] is False)
    ck.ok("on the 19 Oct 2026 pull 2025-03 onward is provisional and 2024 final (month-level approximation)", provisional_flags([v1], ["2025-02", "2025-03", "2024-12"]) ==
          {"2025-02": False, "2025-03": True, "2024-12": False})
    early = ("2026-12-01", rows_from([OR("2026-06", 5)]))
    ck.raises("a new vintage whose latest month is earlier than the previous one is refused", DataError, lambda: revision_rows([v1, early], [], []))


def swiss_file_text(rows):
    return "# source: x\n" + ",".join(SWISS_COLS) + "\n" + "".join(",".join(r) + "\n" for r in rows)


def t_g10(ck):
    W = get_world()
    files = world_files()
    sw = W["inp"]["swiss"]
    vals = swiss_monthly_values(sw)
    ck.eq("clean folder: no Swiss leak in the two Swiss places", swiss_leak_problems(files, vals, 2026), [])
    ck.eq("clean folder: no Swiss monthly value in any other committed file", swiss_prose_problems(files, vals), [])
    ck.eq("clean folder: no differencing of Swiss cells gives a month", swiss_difference_problems(files, sw), [])
    v = round(sw["months"]["2020-03"]["CN"][0])
    bad_sw = "# source: x\n" + ",".join(SWISS_COLS) + "\n" + "\n".join([
        "2019,CN,710812,,%d,12,11,0,partial,," % v,                         # a monthly kg in the known-months cell of a partial year
        "2026,CN,710812,1000,1000,12,0,0,complete,,",                       # a current-year cell
        "2018,HK,710812,,500,12,6,0,partial,4000,77"]) + "\n"             # a partial year carrying the annual comparison
    bad_cx = "# source: x\n" + ",".join(CONTEXT_COLS) + "\n" + "\n".join([
        "2024,12,0,special,1,1,1,%s,,,," % fnum(v / 1000.0, 3),            # a monthly value in tonnes
        "2026_to_2026-08,8,0,special,1,1,1,1.000,,,,"]) + "\n"
    bad = dict(files, **{"swiss_mirror_annual.csv": bad_sw, "context.csv": bad_cx})
    probs = swiss_leak_problems(bad, vals, 2026)
    has = lambda *words: any(all(w in p for w in words) for p in probs)
    ck.ok("planted: a Swiss monthly kg value in swiss_mirror_annual.csv is reported", has("monthly kg value", "swiss_mirror_annual.csv"), " | ".join(probs))
    ck.ok("planted: the same value as tonnes in context.csv is reported", has("in tonnes", "context.csv"), " | ".join(probs))
    ck.ok("planted: a current-year Swiss cell in swiss_mirror_annual.csv is reported", has("current-year", "swiss_mirror_annual.csv"), " | ".join(probs))
    ck.ok("planted: a current-year Swiss cell in context.csv is reported", has("current-year", "context.csv"), " | ".join(probs))
    ck.ok("planted: a partial year with comtrade_annual_kg filled is reported", has("partial Swiss year"), " | ".join(probs))
    bad2 = dict(files, **{"SOURCES.md": files["SOURCES.md"] + "\nA cell was %s kg.\n" % format(v, ","),
                          "summary.csv": files["summary.csv"] + "Q6,x,CN_HK,y,z,%d,yes,\n" % v,
                          "README.md": files["README.md"] + "\n| 2020 | %s |\n" % fnum(v / 1000.0, 3)})
    p2 = swiss_prose_problems(bad2, vals)
    for fn in ("SOURCES.md", "summary.csv", "README.md"):
        ck.ok("planted: a Swiss monthly value in %s is reported" % fn, any(fn in p for p in p2), " | ".join(p2))
    sw3 = synthetic_swiss()
    sw3["months"]["2020-08"]["CN"] = None
    rows_ok, _ = swiss_years(sw3, 2025)
    blanked = list(sw3["blanked"])
    with mutant("known_months_filled"):
        rows_bad, _ = swiss_years(sw3, 2025)
    ck.ok("the known-months cell is blank for every partner of a partial year", all(r[4] == "" for r in rows_ok if r[8] == "partial") and any(r[8] == "partial" for r in rows_ok))
    ck.ok("...and the blank cells are recorded", ("2020", "CN") in blanked and ("2020", "CN_HK") in blanked, str(blanked))
    ck.eq("with the known-months cells blank, China + Hong Kong - combined cannot give a month", swiss_difference_problems({"swiss_mirror_annual.csv": swiss_file_text(rows_ok)}, sw3), [])
    ck.ok("planted: with the known-months cells restored the identity gives a month and is reported",
          bool(swiss_difference_problems({"swiss_mirror_annual.csv": swiss_file_text(rows_bad)}, sw3)))
    sw2 = synthetic_swiss()
    for m in months_between("2020-01", "2020-12"):
        sw2["months"][m]["CN"] = None
    sw2["months"]["2020-05"]["CN"] = (41111.0, False, 1.0)
    rows2, _ = swiss_years(sw2, 2025)
    r20 = next(r for r in rows2 if r[0] == "2020" and r[1] == "CN")
    ck.ok("a partial year with one known month does not publish that month", r20[8] == "partial" and r20[4] == "", str(r20))


def t_g11(ck):
    files = world_files()
    ck.eq("clean folder: the ten names, exact headers, no raw file (the # source: line is not a header)", folder_problems(files), [])
    ck.eq("the canonical allowlist text equals the spec's text", allow_text(), SPEC_ALLOW_TEXT)
    ck.eq("...and its sha256 equals SPEC_ALLOW_SHA256 (913 bytes)", (sha256_of(allow_text().encode()), len(allow_text().encode())), (SPEC_ALLOW_SHA256, 913))
    f2 = dict(files, **{"monthly.csv": files["monthly.csv"].replace(",vintage\n", ",vintage,extra\n", 1)})
    ck.ok("an extra column is refused", bool(folder_problems(f2)))
    f3 = dict(files, **{"monthly.csv": files["monthly.csv"].replace(",series,", ",serie,", 1)})
    ck.ok("a renamed column is refused", bool(folder_problems(f3)))
    ck.ok("a raw .json file is refused", bool(folder_problems(dict(files, **{"ots_7108.json": "{}"}))))
    ck.ok("an eleventh file is refused", bool(folder_problems(dict(files, **{"notes.txt": "x"}))))
    ck.eq("exactly ten files", len(files), 10)


def t_g12(ck):
    opening = "# T\n\n" + REQUIRED_OPEN + "\n\n" + DENIAL_SENTENCE + " The rest is plain.\n"
    ck.eq("the two opening sentences and the one denial sentence pass", wording_problems("README.md", opening), [])
    bad_open = opening.replace("it is not a measure of central-bank buying", "it is a measure of central-bank buying")
    ck.ok("with 'is a measure of central-bank buying' the opening fails", bool(wording_problems("README.md", bad_open)))
    ck.ok("a second 'ceiling' sentence fails", bool(wording_problems("README.md", opening + "The series is a ceiling on exports.\n")))
    ck.ok("a repeat of the denial sentence fails", bool(wording_problems("README.md", opening + DENIAL_SENTENCE + "\n")))
    for w in ("caused", "drove", "driven", "because of", "led to", "pushed", "in response to"):
        ck.ok("causal word %r is reported" % w, bool(wording_problems("README.md", "Prices %s the move." % w)))
    for ph in ("unreported central-bank buying", "hidden PBoC purchases", "covert official demand", "the PBoC bought gold", "central banks buying"):
        ck.ok("buyer phrase %r is reported" % ph, bool(wording_problems("README.md", "It shows %s here." % ph)))
    for w in ("a cap on exports", "capped at", "an upper bound", "bounds", "bounded", "a ceiling"):
        ck.ok("bound word in %r is reported" % w, bool(wording_problems("SOURCES.md", "This is %s." % w)))
    ck.ok("bare 'bars' as a label is reported", bool(wording_problems("README.md", "The bars series is shown.")))
    ck.eq("'bars' inside the tariff text passes", wording_problems("README.md", "CN 71081310 is %s." % TARIFF_TEXT), [])
    ck.ok("a series column labelled 'bars' is reported", bool(wording_problems("annual.csv", "# source: x\nyear,partner,series\n2024,CN,bars\n")))


def t_g13(ck):
    ck.raises("a non-allowlisted host (sec.gov) is refused before the request", Refused, lambda: check_url("https://www.sec.gov/x"))
    ck.raises("FRED is refused", Refused, lambda: check_url("https://fred.stlouisfed.org/x"))
    ck.raises("plain http is refused", Refused, lambda: check_url("http://api.uktradeinfo.com/OTS"))
    main = hmrc_requests()[0]["target"]
    ck.raises("$orderby is refused", Refused, lambda: check_url("https://api.uktradeinfo.com" + main + "&$orderby=MonthId"))
    ck.raises("an or-chain on CommoditySitcId is refused", Refused, lambda: check_url("https://api.uktradeinfo.com" + main + "&$filter=CommoditySitcId eq 1 or CommoditySitcId eq 2"))
    ck.raises("an address in the user agent is refused", Refused, lambda: assert_ua(UA.replace("research", "research; me" + chr(64) + "example.org")))
    ck.eq("the user agent is the CLAUDE.md string, with no address", (UA, chr(64) in UA), ("Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)", False))
    ck.eq("empty Comtrade data is a valid reply", test_comtrade({"data": [], "error": ""}, 757, 710812, "202401", [156, 344]), None)
    with tempfile.TemporaryDirectory() as tmp:
        ck.raises("an HMRC pace under 2 s is refused", Refused, lambda: Fetcher("hmrc", os.path.join(tmp, "c"), os.path.join(tmp, "o"), sleep=1.0))
        ck.raises("a Comtrade pace under 6 s is refused", Refused, lambda: Fetcher("comtrade", os.path.join(tmp, "c"), os.path.join(tmp, "o"), sleep=5.0))
        ck.raises("more than 12 HMRC requests per run cannot be configured", Refused, lambda: Fetcher("hmrc", os.path.join(tmp, "c"), os.path.join(tmp, "o"), max_requests=13))
        ck.raises("more than 200 Comtrade requests per run cannot be configured", Refused, lambda: Fetcher("comtrade", os.path.join(tmp, "c"), os.path.join(tmp, "o"), max_requests=201))
        fe, calls, clock = fake_rig(os.path.join(tmp, "a"), "hmrc", ok200({"value": []}))
        for _ in range(3):
            fe.get_doc("/FlowType", lambda d: None)
        gaps = [calls[i + 1][3] - calls[i][3] for i in range(2)]
        ck.ok("HMRC requests start at least 2 s apart", all(g >= 2.0 for g in gaps), str(gaps))
        ck.ok("the request carries the neutral user agent and GET only", calls[0][2]["User-Agent"] == UA)
        fe, calls, clock = fake_rig(os.path.join(tmp, "b"), "comtrade", ok200({"data": [], "error": ""}))
        t = ct_target("A", 757, "2024", [156, 344], "710812")
        for _ in range(3):
            fe.get_doc(t, lambda d: None)
        gaps = [calls[i + 1][3] - calls[i][3] for i in range(2)]
        ck.ok("Comtrade requests start at least 6 s apart", all(g >= 6.0 for g in gaps), str(gaps))
        fe, calls, clock = fake_rig(os.path.join(tmp, "c"), "hmrc", ok200({"value": []}))
        for _ in range(12):
            fe.get_doc("/FlowType", lambda d: None)
        ck.raises("the 13th HMRC request is refused", MaxRequests, lambda: fe.get_doc("/FlowType", lambda d: None))
        ck.eq("...and was not sent", len(calls), 12)
        fe, calls, _ = fake_rig(os.path.join(tmp, "d"), "hmrc", lambda h, t_, hd: (429, b"slow down", {"retry-after": "30"}))
        ck.raises("a 429 latches", Latched, lambda: fe.get_doc("/FlowType", lambda d: None))
        ck.eq("...and is not retried (one request)", len(calls), 1)
        fe, calls, _ = fake_rig(os.path.join(tmp, "e"), "hmrc", lambda h, t_, hd: (301, b"", {"location": "https://elsewhere.example/"}))
        ck.raises("a redirect is not followed: it latches", Latched, lambda: fe.get_doc("/FlowType", lambda d: None))
        ck.eq("...with one request", len(calls), 1)


def t_g14(ck):
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    ck.eq("static: no removal, rename or move call anywhere, os.replace only in the two atomic writers", static_stop_problems(src), [])
    for planted in ("os." + "remove(STOP_PATH)", "shutil." + "rmtree(cache)", "os." + "replace(tmp, stop_path)", "p." + "unlink()", "os." + "rename(a, b)", "shutil." + "move(a, b)"):
        ck.ok("static: a planted %r is flagged" % planted, bool(static_stop_problems(src + "\n" + planted + "\n")))
    with tempfile.TemporaryDirectory() as tmp:
        sd = os.path.join(tmp, "stop")
        os.makedirs(sd)
        sp = os.path.join(sd, "STOP_comtrade")
        with open(sp, "w") as fh:
            fh.write("status: 429\nutc_time: x\nurl_path: y\nretry_after: \nbody_head: z\n")
        before = sha256_of(open(sp, "rb").read())
        fe, calls, _ = fake_rig(tmp, "comtrade", ok200({"data": [], "error": ""}), stop_dir=sd, max_requests=3)
        ck.raises("with a planted STOP_comtrade, fetch raises the latch", Latched, lambda: fe.fetch_comtrade(comtrade_plan(D_("2026-10-19")), say=lambda *a: None))
        ck.eq("...makes no Comtrade request", len(calls), 0)
        ck.eq("...and leaves the STOP file byte-identical", sha256_of(open(sp, "rb").read()), before)
        fe, calls, _ = fake_rig(os.path.join(tmp, "x"), "hmrc", lambda h, t_, hd: (503, b"Service Unavailable\r\n<html>", {"retry-after": "120"}))
        ck.raises("a fixture 503 latches", Latched, lambda: fe.get_doc("/FlowType", lambda d: None))
        p = os.path.join(tmp, "x", "stop", "STOP_hmrc")
        got = dict(l.split(": ", 1) for l in open(p, encoding="utf-8").read().splitlines()) if os.path.exists(p) else {}
        ck.eq("the STOP file carries the five fields", list(got), ["status", "utc_time", "url_path", "retry_after", "body_head"])
        ck.ok("...with the status, the Retry-After header, the path and the escaped body head", got.get("status") == "503" and got.get("retry_after") == "120" and
              got.get("url_path") == "/FlowType" and "Service Unavailable\\r\\n" in got.get("body_head", ""))


def t_g15(ck):
    main = hmrc_requests()[0]["target"]
    p1 = ots_doc([OR("2024-01", 1), OR("2024-02", 2), OR("2024-03", 3)], 5, "https://api.uktradeinfo.com" + main + "&$skip=3")
    p2 = ots_doc([OR("2024-04", 4), OR("2024-05", 5)])

    def handler(host, target, hdrs):
        return (200, jb(p2 if "$skip=3" in target else p1), {})
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _ = fake_rig(tmp, "hmrc", handler)
        try:
            doc, raw = fe.get_ots(main)
            n = len(doc["value"])
        except Latched:
            n = -1
        ck.eq("@odata.nextLink is followed: two pages merge to the 5 rows of @odata.count", n, 5)
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _ = fake_rig(tmp, "hmrc", ok200(ots_doc([OR("2024-01", 1), OR("2024-02", 2)], 6)))
        ck.raises("rows (2) different from @odata.count (6) latch", Latched, lambda: fe.get_ots(main))


def t_g16(ck):
    W = get_world()
    la, lm = W["inp"]["ledger_annual"], W["inp"]["ledger_monthly"]
    ctx, L = context_rows(W["S"]["cells"], W["S"]["months"], la, lm, W["S"]["swiss_rows"], 2026, W["inp"]["swiss"]["months"])
    ck.eq("L is the latest month in both the UK series (2026-08) and the ledger (2026-09)", L, "2026-08")
    r = next(x for x in ctx if x[0].startswith("2026_to_"))
    ck.eq("the SAFE sum covers January to August only (8 x 1.000), not January to September", r[8], "8.000")
    ck.eq("the 2026 Swiss cell is blank", r[7], "")
    ck.ok("...with a note", "Swiss" in r[11])
    r25 = next(x for x in ctx if x[0] == "2025")
    ck.ok("a completed year's Swiss cell is filled", r25[7] != "")


def t_g17(ck):
    W = get_world()
    S = W["S"]
    ms = S["months"]
    mt = {(r[0], r[1], r[2]): r for r in monthly_table(S["cells"], ms, {m: False for m in ms}, "v")}
    ck.eq("2016-04 is general trade", mt[("2016-04", "CN", "cn71081310")][7], "general")
    ck.eq("2016-05 is special trade", mt[("2016-05", "CN", "cn71081310")][7], "special")
    ar = annual_lookup(annual_table(S["cells"], ms, {m: False for m in ms}, "v"))
    ck.eq("2015 is general, 2016 mixed, 2017 special", [ar[(y, "CN_HK", "cn71081310")][7] for y in ("2015", "2016", "2017")], ["general", "mixed", "special"])
    rows = summary_rows(S)
    tagged = [r for r in rows if r[0] in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q8")]
    ck.ok("every Q1-Q6 and Q8 row names its trade_system in the window", all(re.search(r"\[(general|special|mixed)\]", r[1]) for r in tagged),
          next((r[1] for r in tagged if not re.search(r"\[(general|special|mixed)\]", r[1])), ""))


def t_g18(ck):
    W = get_world()
    rows = summary_rows(W["S"])
    must_no = [r for r in rows if r[0] in ("Q1", "Q4") or "2024" in r[1] or "2025" in r[1]]
    ck.ok("every 2024 row, 2025 row, Q1 row and Q4 row has blind = no", must_no and all(r[6] == "no" for r in must_no),
          next((str(r) for r in must_no if r[6] != "no"), ""))
    ck.ok("rows that touch neither year nor Q1/Q4 are blind = yes", any(r[6] == "yes" and r[0] in ("Q2", "Q6", "Q8") for r in rows))
    ck.ok("every question Q1 to Q8 has a summary row", {r[0] for r in rows} == {"Q%d" % i for i in range(1, 9)}, str(sorted({r[0] for r in rows})))


def t_x_cache(ck):
    ck.raises("a cache inside the repository, not ignored by git, is refused", Refused, lambda: check_cache(os.path.join(ROOT, "data", "not_ignored_x")))
    ck.ok("the default cache is accepted (git ignores it)", check_cache(CACHE_DEFAULT) is not None)
    ck.raises("the committed output folder as a cache is refused", Refused, lambda: check_cache(os.path.join(OUT_DEFAULT, "cache")))


def t_x_build(ck):
    """An end-to-end build on synthetic inputs: structure, determinism and the folder guards on real renderings."""
    W = get_world()
    c = dict(W["c0"])
    texts, failed = finish(c)
    chk = {r[0]: r for r in c["checks"]}
    ck.eq("C11 (a second build leaves every sha256 unchanged) passes", chk["C11"][4], "PASS")
    ck.eq("C16 (folder guards on the real rendering) passes", chk["C16"][4], "PASS")
    ck.eq("ten files", sorted(texts), sorted(COMMITTED))
    ck.ok("the README opens with the two required sentences", texts["README.md"].split("\n\n")[1].strip() == REQUIRED_OPEN)
    ck.ok("the README carries the denial sentence exactly once and no other bound word", texts["README.md"].count(DENIAL_SENTENCE) == 1 and wording_problems("README.md", texts["README.md"]) == [])
    rd = texts["README.md"]
    ck.ok("the README carries the supervisor's replacement demand sentence and not the withdrawn one", "so a UK figure larger or smaller than SAFE's is expected either way and is not a comparison." in rd.replace("\n", " ")
          and "far exceed" not in rd and "Builder decisions" not in rd)
    ck.ok("the build decisions are a section of SOURCES.md and not of the README", "## Build decisions" in texts["SOURCES.md"] and "## Build decisions" not in rd)
    ck.ok("the README points to SOURCES.md for the build decisions", "Build decisions, including one fix made after the first build, are listed in [SOURCES.md](SOURCES.md)." in rd)
    ck.ok("every committed csv begins with one # source: line", all(t.startswith("# source:") and t.count("\n# source:") == 0 for n, t in texts.items() if n.endswith(".csv")))
    ck.eq("two renderings are byte-identical", texts_digest(texts), texts_digest(W["texts"]))


GUARDS = [
    ("G1", "port sum: sum over PortId", ["first_row_only"], t_g1),
    ("G2", "blank rules (3.4, 3.8-3.10, 2.2)", ["absence_blank", "confidential_zero", "all_non_eu_filled", "zero_row_no_rows", "annual_filled", "context_over_blank",
                                                "comtrade_missing_zero"], t_g2),
    ("G3", "suppression: SuppressionIndex 0 only", ["supp_kept"], t_g3),
    ("G4", "code groups (3.2)", ["monetary_in_series", "powder_in_other", "unknown_dropped"], t_g4),
    ("G5", "flow sign: FlowTypeId 4, flowCode X", ["flow_any", "lookup_label_loose", "comtrade_m_ok"], t_g5),
    ("G6", "partners 720/740/39", ["ch_as_cn", "cnhk_fills_blank"], t_g6),
    ("G7", "no cross-route sum", ["cross_route_off"], t_g7),
    ("G8", "units and no ratios (R3-1)", ["netmass_as_tonnes", "t_1e6", "ratio_col_off", "quotient_off"], t_g8),
    ("G9", "vintages, provisional, revisions (3.6, 3.7)", ["revision_rewrite", "revision_dup_key", "kgprev_lost", "prev_from_monthly", "no_baseline", "prov_from_newest",
                                                           "earlier_latest_ok"], t_g9),
    ("G10", "Swiss leak guard, planted bad folder and clean folder (6.2)", ["leak_kg_off", "leak_t_off", "leak_current_swiss_off", "leak_current_context_off", "leak_partial_off", "leak_prose_off", "difference_off", "known_months_filled"], t_g10),
    ("G11", "allowlists, sha256 and the folder (5, 6.3)", ["extra_column_ok", "renamed_column_ok", "allow_drift", "raw_json_ok", "eleventh_ok", "source_as_header"], t_g11),
    ("G12", "wording (R6)", ["causal_off", "buyer_off", "bound_off", "bars_off", "buyer_loose", "denial_loose", "denial_all"], t_g12),
    ("G13", "fetch safety (R1-R4)", ["allow_other_host", "ua_check_off", "orderby_ok", "hmrc_pacing_off", "ct_pacing_off", "hmrc_cap_off", "ct_cap_off", "retry_429",
                                      "redirect_ok", "empty_data_fails"], t_g13),
    ("G14", "STOP latch: static scan and runtime", ["stop_ignored", "static_scan_off", "stop_short"], t_g14),
    ("G15", "pagination (3.1)", ["nextlink_ignored", "count_mismatch_ok"], t_g15),
    ("G16", "windows (3.10)", ["safe_longer_window", "swiss_2026_filled"], t_g16),
    ("G17", "the May 2016 break (3.5)", ["no_general_2016_04", "annual_not_mixed", "q_no_ts"], t_g17),
    ("G18", "blind (section 4)", ["blind_wrong"], t_g18),
    ("X1", "cache path: outside the repo, or git-ignored inside it", ["cache_check_off"], t_x_cache),
    ("X2", "an end-to-end synthetic build: determinism and the folder guards on real renderings", ["render_unstable"], t_x_build),
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
                print("       mutant %-22s %s%s" % (m, "caught" if caught else "NOT CAUGHT", "  (first failing check: %s)" % mk.failed()[0][0][:70] if caught else ""))
    print("selftest: %d guards, %d checks, %d mutants applied one at a time, %d failure(s), %.1f s" % (len(GUARDS), n_checks, n_mut, bad_total, time.time() - t0))
    return 0 if bad_total == 0 else 1


# ==== COMMAND LINE ====
def run_fetch(a):
    code = 0
    today = dt.datetime.now(dt.timezone.utc).date()
    os.makedirs(a.out, exist_ok=True)
    if a.source in ("all", "hmrc"):
        fe = Fetcher("hmrc", a.cache, a.out, sleep=a.sleep_hmrc)
        try:
            fe.check_stop()
            n = fe.fetch_hmrc()
            print("hmrc: requests sent %d, files saved %d" % (fe.requests, n))
        except Latched as e:
            print("%s" % e, file=sys.stderr)
            print("hmrc: requests sent %d; the HMRC source ends here" % fe.requests)
            code = 2
        except SocketFault as e:
            print("hmrc: socket fault (%s): the invocation ends; nothing was latched and nothing is retried" % e, file=sys.stderr)
            code = code or 4
    if a.source in ("all", "comtrade"):
        fe = Fetcher("comtrade", a.cache, a.out, sleep=a.sleep_comtrade, max_requests=a.comtrade_max)
        try:
            fe.check_stop()
            n = fe.fetch_comtrade(comtrade_plan(today))
            print("comtrade: requests sent %d, files saved %d" % (fe.requests, n))
        except MaxRequests as e:
            print("comtrade: stopped by --comtrade-max (%s); requests sent %d; run fetch again to continue the plan" % (e, fe.requests))
        except Latched as e:
            print("%s" % e, file=sys.stderr)
            print("comtrade: requests sent %d; the Comtrade source ends here (the build ships UK-only unless the cache is complete)" % fe.requests)
            code = 2
        except SocketFault as e:
            print("comtrade: socket fault (%s): the invocation ends; nothing was latched and nothing is retried" % e, file=sys.stderr)
            code = code or 4
    return code


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch", help="download the inputs into the cache (the only network command)")
    pf.add_argument("--source", choices=("all", "hmrc", "comtrade"), default="all")
    pf.add_argument("--cache", default=CACHE_DEFAULT)
    pf.add_argument("--out", default=OUT_DEFAULT, help="where fetch_log.csv is kept")
    pf.add_argument("--sleep-hmrc", type=float, default=HMRC_SLEEP)
    pf.add_argument("--sleep-comtrade", type=float, default=CT_SLEEP)
    pf.add_argument("--comtrade-max", type=int, default=CT_MAX)
    pb = sub.add_parser("build", help="offline: validate the cache and write every output")
    pb.add_argument("--cache", default=CACHE_DEFAULT)
    pb.add_argument("--out", default=OUT_DEFAULT)
    pb.add_argument("--ledger-annual", default=LEDGER_ANNUAL_DEFAULT)
    pb.add_argument("--ledger-monthly", default=LEDGER_MONTHLY_DEFAULT)
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
