#!/usr/bin/env python3
"""Federal Reserve H.8 line 38, "net due to related foreign offices": a weekly descriptive ledger. Python 3 standard library only.

  python3 bin/h8_foreign_offices.py fetch  [--cache DIR] [--out DIR] [--sleep 3.05]     # the only network command; at most 6 requests
  python3 bin/h8_foreign_offices.py build  [--cache DIR] [--out DIR]                      # offline; byte-identical on re-run
  python3 bin/h8_foreign_offices.py selftest [--no-mutants] [--mutant NAME]               # synthetic data only; no network

Specification: _research/2026-10-23-H8-Foreign-Offices-Spec.md (committed at 7a0983d, with its supervisor rulings; where rounds differ the latest round
is applied). Outputs: data/h8_foreign_offices/ (eight CSVs, README.md, SOURCES.md).

WHAT TOUCHES THE NETWORK. Only `fetch`, and only www.federalreserve.gov: the release-page XML zip (primary), the four DDP weekly packages (cross-check and
fallback) and the Notes on Data page. Any other host is refused before a request is made. GET only, one request at a time, at least 3 seconds apart, at most
6 requests a run, no redirect followed, the CLAUDE.md non-SEC identification string (no address, no name). Any status other than 200, or a body that fails
its content test, writes STOP_xml, STOP_ddp or STOP_notes in data/vintages/h8_foreign_offices/ and ends that source's fetch. Nothing retries and nothing
routes around a refusal. This script never deletes, renames over or truncates a STOP file; only a person deletes one.

WHAT IT RECORDS. The Wednesday-close level of H.8 line 38 for foreign-related institutions, domestically chartered banks and all commercial banks, with the
lines it is built from. It records balances at Wednesday closes; it does not say why they changed.
"""
import argparse
import ast
import calendar
import collections
import contextlib
import csv
import datetime as dt
import decimal
import email.utils
import gzip
import hashlib
import html
import html.parser
import http.client
import io
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
import types
import zipfile
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(ROOT, "data", "h8_foreign_offices")
CACHE_DEFAULT = os.path.join(ROOT, "data", "vintages", "h8_foreign_offices")
STOP_DIR = CACHE_DEFAULT                      # fixed, whatever --cache says: a latch cannot be dodged by pointing the cache elsewhere

UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
HEADERS = {"User-Agent": UA, "Accept-Encoding": "identity", "Accept": "*/*"}
HOST = "www.federalreserve.gov"
HOST_ALLOW = frozenset({HOST})
MIN_SLEEP = 3.0
DEFAULT_SLEEP = 3.05
MAX_REQUESTS = 6
TIMEOUT = 240
BODY_CAP = 64 * 1024 * 1024
ERR_CAP = 4096

XML_PATH = "/releases/h8/data/FRB_h8_xml.zip"
NOTES_PATH = "/releases/h8/h8notes.htm"
DDP_FMT = "/datadownload/Output.aspx?rel=H8&series=%s&lastobs=&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package"
DDP_PACKAGES = (("fri_nsa", "0e569516edadaa66168c115e5016ff16", "FRI", "NSA"), ("dom_nsa", "18461c27aa45d43aa804016497d92ece", "DOM", "NSA"),
                ("all_nsa", "c8dfa96ef1d2db40ce57121ffdddf59d", "ALL", "NSA"), ("fri_sa", "53b903ce661b8534202a6d5e36db960d", "FRI", "SA"))
SOURCES = ("xml", "ddp", "notes")

# the 20 series of spec 2.1: four balance-sheet lines of H.8 for each of four groups and bases; matched on the whole identifier
LINES = (("l38", "1100"), ("l40", "1152"), ("l34", "1058"), ("l37", "3094"), ("l39", "3095"))
COMBOS = (("FRI", "NSA", "FRD", "FR"), ("DOM", "NSA", "DMD", "DM"), ("ALL", "NSA", "CBD", "CB"), ("FRI", "SA", "FRA", "FR"))
GROUP_PHRASE = {"FRI": "foreign-related institutions", "DOM": "domestically chartered commercial banks", "ALL": "all commercial banks"}
BASIS_PHRASE = {"NSA": "not seasonally adjusted", "SA": "seasonally adjusted"}
UNIT_MULT_OK = "1000000"
ITEM_NAMES = {"1100": "(38) Net due to related foreign offices", "1152": "(40) Total liabilities", "1058": "(34) Deposits", "3094": "(37) Borrowings",
              "3095": "(39) Other liabilities including trading liabilities"}


def sname(item, suffix):
    return "B%sN%s" % (item, suffix)


WANTED = collections.OrderedDict()
for _g, _sa, _suf, _bg in COMBOS:
    for _line, _item in LINES:
        WANTED[sname(_item, _suf)] = dict(group=_g, sa=_sa, line=_line, item=_item, bg=_bg)
LINE38 = tuple(n for n, w in WANTED.items() if w["line"] == "l38")
FOUR_LINE38 = tuple(sname("1100", s) for s in ("FRD", "DMD", "CBD", "FRA"))

FIRST_WEEK = "2004-06-02"                       # first week of the ledger (the first week of DOM and ALL)
FRI_FIRST_WEEK = "1973-01-03"
FOOTNOTE20_WEEK = "2022-04-06"
FOOTNOTE20_HEAD = "Beginning April 6, 2022, foreign-related institutions no longer report the allowance for loan and lease losses separately"
FOOTNOTE20 = ("Beginning April 6, 2022, foreign-related institutions no longer report the allowance for loan and lease losses separately (currently, the allowance "
              "for credit losses on loans and leases). Any such allowances are included in net due to related foreign offices (line 38).")
FOOTNOTE24 = "Excludes the due-from position with related foreign offices which is included in line 38."
PIN_VINTAGE = "2026-10-16"
SA_NOTE = "derived as residuals"

# the frozen quarter set and the named ordinary Wednesdays (spec 3.7, section 4)
FROZEN_FIRST, FROZEN_LAST = (2019, 1), (2026, 3)
Q1_START = "2019-01-02"
Q1_WEDNESDAYS = ("2019-02-13", "2020-02-12", "2021-02-10", "2022-02-09", "2023-02-08", "2024-02-14", "2025-02-12", "2026-02-11")
Q2_ENDPOINTS = ("2024-02-14", "2025-02-12", "2026-02-11", "2026-08-12")
ON_DATE_QUARTERS = ("2020Q3", "2021Q1", "2021Q2", "2025Q4", "2026Q3")
NOTE_PINS = {"FRI": (("2019-10-02", -3000.0, 0), ("2017-11-29", 5200.0, 0), ("2010-03-31", -12000.0, 1), ("2008-04-02", -18600.0, 0), ("2008-02-06", 12000.0, 0)),
             "DOM": (("2018-04-04", 2000.0, 0), ("2016-03-02", -3100.0, 0), ("2011-01-05", 5700.0, 0), ("2008-08-20", -8600.0, 0), ("2007-03-07", -3200.0, 0),
                     ("2006-10-04", -10000.0, 0), ("2004-12-29", 2000.0, 0))}

# column allowlists: the spec's canonical text (section 5), typed here once; bin/check.sh holds its own literal copy and never reads this one
SPEC_ALLOW_TEXT = (
    "weekly.csv:week_wed,group,sa,series_id,usd_mn,change_usd_mn,total_liabilities_usd_mn,pct_of_total_liabilities,qe_quarter,qe_role,qe_offset_days,segment_start,note_flag,vintage\n"
    "quarter_ends.csv:quarter,qe_date,qe_wed,offset_days,on_date,group,level_qe_wed_usd_mn,delta_qe_wed_usd_mn,delta_next_usd_mn,qe_day_in_window,straddles_break,frozen_set,blind,vintage\n"
    "notes.csv:note_week,group,line38_effect_usd_mn,kind,paragraph_index,text_head\n"
    "revisions.csv:vintage_prev,vintage_new,series_id,week_wed,usd_mn_prev,usd_mn_new,change_usd_mn\n"
    "vintages.csv:vintage,route,xml_prepared,xml_last_modified,xml_sha256,ddp_status,latest_week,rows_fri_nsa\n"
    "summary.csv:question,window,group,statistic,value,unit,blind\n"
    "checks.csv:check_id,description,expected,observed,status\n"
    "fetch_log.csv:utc_time,host,path_and_query,status,bytes,sha256\n")
SPEC_ALLOW_SHA256 = "4ad6cc43d2befbae6df06998a362d818827b0f43cd6b30eed8d65868bf030d59"
ALLOW_ORDER = tuple(l.split(":", 1)[0] for l in SPEC_ALLOW_TEXT.splitlines())
ALLOW = {l.split(":", 1)[0]: l.split(":", 1)[1].split(",") for l in SPEC_ALLOW_TEXT.splitlines()}
COMMITTED = tuple(ALLOW_ORDER) + ("README.md", "SOURCES.md")
RAW_EXT = (".zip", ".xml", ".htm", ".html", ".pdf", ".xsd", ".gz")

# wording guards (G11), pasted from the spec (R2-6) and not imported
CAUSAL_RX = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b", re.I)
EXTRA_RX = re.compile(r"\b(?:in|out)?flows?\b|window[- ]dressing|\b(?:head\s+offices?|parents?)\s+(?:fund|funds|funded|funding|push|pushes|pushed|pull|pulls|pulled|drain|drains|drained)\b|\b(?:dollar\s+)?(?:shortage|squeeze)\b", re.I)

REQUIRED_OPEN = ("This table shows, at each Wednesday close, the net amount that US branches and agencies of foreign banks, with Edge Act and agreement corporations, owe to "
                 "their own offices abroad and to related institutions in the US, from the Federal Reserve's H.8 release. The figure nets those positions and includes "
                 "unremitted profits, capital and reserve accounts and, from April 2022, allowances for credit losses.")
REQUIRED_S3 = "It records balances at Wednesday closes only; it does not show why they changed, and a change in a balance is not a measure of money moved."
DENIAL_SENTENCE = "These weekly changes are not flows of funds, and the table does not test window dressing or any other motive."
CAVEAT_SENTENCE = "Wednesday levels cannot show a position that is not held at a Wednesday close"

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
    """The request cap for this invocation was reached."""


class Latched(Exception):
    """A technical refusal: STOP was written (or already exists); this source's run ends."""


class SocketFault(Exception):
    """Timeout, reset or TLS error: the invocation ends without latching."""


class ContentError(Exception):
    """A body failed its content test (R3b)."""


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


def D_(s):
    return dt.date.fromisoformat(s)


def addd(s, n):
    return (D_(s) + dt.timedelta(days=n)).isoformat()


def is_wed(s):
    return D_(s).weekday() == 2


def weeks_between(a, b):
    out, d, end = [], D_(a), D_(b)
    while d <= end:
        out.append(d.isoformat())
        d += dt.timedelta(days=7)
    return out


def yn(b):
    return "yes" if b else "no"


def assert_ua(ua=UA):
    if not M("g13_at_in_ua_ok"):
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


def read_file(path, mode="rb"):
    with open(path, mode) as fh:
        return fh.read()


# ------------------------------------------------------------------------------------------------------------------------
# requests: the table, the URL check (R1, R3) and the content tests (R3b)
# ------------------------------------------------------------------------------------------------------------------------
def allowed_targets():
    t = {XML_PATH, NOTES_PATH}
    t.update(DDP_FMT % pid for _, pid, _, _ in DDP_PACKAGES)
    return t


def check_url(url):
    """Only plain https GETs to www.federalreserve.gov and only the six request targets of the spec. Returns (host, target)."""
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    target = p.path + ("?" + p.query if p.query else "")
    if M("g13_allow_other_host"):
        return host, target
    if p.scheme != "https" or p.username or p.password or p.port not in (None, 443) or p.fragment:
        raise Refused("only plain https URLs are allowed")
    if host not in HOST_ALLOW:
        raise Refused("host %s is not on the allowlist" % host)
    if target not in allowed_targets():
        raise Refused("that path is not one of the six requests of the spec")
    return host, target


def check_cache(cache, root=ROOT, out_dir=None):
    """The cache may be outside the repository, or inside it only where git ignores it (never in the committed output folder)."""
    real = os.path.realpath(os.path.expanduser(cache))
    rroot = os.path.realpath(root)
    if M("x_cache_check_off"):
        return real
    if real == rroot or real.startswith(rroot + os.sep):
        outd = os.path.realpath(out_dir or os.path.join(root, "data", "h8_foreign_offices"))
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


# ---- units (G5) ----------------------------------------------------------------------------------------------------------
def usd_mn_str(valstr, mult):
    """A value in the file's unit (UNIT_MULT / Multiplier) as US dollars millions, as text. UNIT_MULT 1,000,000 is the identity, and the digits are kept."""
    if M("g5_thousands"):
        mult = int(mult) // 1000
    if M("g5_mult_ignored"):
        mult = 1000000
    factor = decimal.Decimal(int(mult)) / decimal.Decimal(1000000)
    if factor == 1:
        return valstr.strip()
    return format(decimal.Decimal(valstr) * factor, "f")


# ---- XML ----------------------------------------------------------------------------------------------------------------
def wanted_name(nm):
    """The wanted identifier for a SERIES_NAME, matched on the whole string (R2-3); the mutant matches on a substring."""
    if M("g4_substring"):
        for w in WANTED:
            if nm and w in nm:
                return w
        return None
    return nm if nm in WANTED else None


def read_bg(attrs):
    bg = attrs.get("BG")
    if M("g1_bg_misread") and bg == "DM":
        return "FR"
    return bg


def assert_attrs(nm, attrs):
    """The attributes of spec 2.1 for one XML series; a mismatch is a content failure (G1, G2)."""
    w = WANTED[nm]
    if read_bg(attrs) != w["bg"]:
        raise ContentError("%s: BG is %r, expected %r" % (nm, attrs.get("BG"), w["bg"]))
    if attrs.get("SA") != w["sa"]:
        raise ContentError("%s: SA is %r, expected %r" % (nm, attrs.get("SA"), w["sa"]))
    if attrs.get("CATEGORY") != "L" and not M("g2_asset_side"):
        raise ContentError("%s: CATEGORY is %r, expected 'L' (liabilities)" % (nm, attrs.get("CATEGORY")))
    if attrs.get("ITEM") != w["item"]:
        raise ContentError("%s: ITEM is %r, expected %r" % (nm, attrs.get("ITEM"), w["item"]))
    if attrs.get("FREQ") != "19":
        raise ContentError("%s: FREQ is %r, expected '19' (weekly)" % (nm, attrs.get("FREQ")))
    if attrs.get("UNIT_MULT") != UNIT_MULT_OK:
        raise ContentError("%s: UNIT_MULT is %r, expected %s" % (nm, attrs.get("UNIT_MULT"), UNIT_MULT_OK))


def parse_xml_data(stream):
    """Stream H8_data.xml with iterparse: (Prepared text, {wanted name: {attrs, obs: {week: (value text, status)}}})."""
    prepared, series, cur = None, {}, None
    for ev, el in ET.iterparse(stream, events=("start", "end")):
        tag = el.tag.rsplit("}", 1)[-1]
        if ev == "start":
            if tag == "Series":
                nm = wanted_name(el.get("SERIES_NAME"))
                if nm is not None:
                    if nm in series:
                        raise ContentError("series %s appears twice" % nm)
                    cur = series[nm] = dict(attrs=dict(el.attrib), obs={})
                else:
                    cur = None
        else:
            if tag == "Prepared":
                prepared = (el.text or "").strip()
            elif tag == "Obs":
                if cur is not None:
                    cur["obs"][el.get("TIME_PERIOD")] = (el.get("OBS_VALUE"), el.get("OBS_STATUS"))
                el.clear()
            elif tag == "Series":
                cur = None
                el.clear()
    return prepared, series


def parse_xml_struct(stream):
    """Code lists CL_CATEGORY and CL_ITEM of H8_struct.xml: {'cat': {code: text}, 'item': {code: text}}."""
    root = ET.parse(stream).getroot()
    out = {"cat": {}, "item": {}}
    for cl in root.iter():
        if cl.tag.rsplit("}", 1)[-1] != "CodeList":
            continue
        key = {"CL_CATEGORY": "cat", "CL_ITEM": "item"}.get(cl.get("id"))
        if key is None:
            continue
        for code in cl:
            if code.tag.rsplit("}", 1)[-1] != "Code":
                continue
            d = next((x.text or "" for x in code if x.tag.rsplit("}", 1)[-1] == "Description"), "")
            out[key][code.get("value")] = d.strip()
    return out


def parse_prepared(text):
    try:
        return dt.datetime.fromisoformat((text or "").strip()[:19])
    except ValueError:
        raise ContentError("message:Prepared %r is not a date" % text)


def test_xml_zip(body):
    """R3b: the zip opens, holds H8_data.xml and H8_struct.xml, Prepared is a date, the 20 series carry the attributes of 2.1."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(body))
    except (zipfile.BadZipFile, OSError):
        raise ContentError("the body is not a zip")
    names = set(zf.namelist())
    for n in ("H8_data.xml", "H8_struct.xml"):
        if n not in names:
            raise ContentError("the zip lacks %s" % n)
    try:
        with zf.open("H8_struct.xml") as fh:
            codes = parse_xml_struct(fh)
        with zf.open("H8_data.xml") as fh:
            prepared, series = parse_xml_data(fh)
    except ET.ParseError as e:
        raise ContentError("XML does not parse: %s" % e)
    pd = parse_prepared(prepared)
    for nm in WANTED:
        if nm not in series:
            raise ContentError("series %s is missing" % nm)
        assert_attrs(nm, series[nm]["attrs"])
        for wk, (val, st) in series[nm]["obs"].items():
            try:
                D_(wk)
            except (TypeError, ValueError):
                raise ContentError("%s: TIME_PERIOD %r is not a date" % (nm, wk))
            if st == "A":
                try:
                    decimal.Decimal(val)
                except (decimal.InvalidOperation, TypeError):
                    raise ContentError("%s %s: OBS_VALUE %r is not a number" % (nm, wk, val))
    return dict(prepared=pd.strftime("%Y-%m-%dT%H:%M:%S"), series=series, codes=codes)


# ---- DDP ----------------------------------------------------------------------------------------------------------------
def pkg_names(grp, sa):
    return [n for n, w in WANTED.items() if w["group"] == grp and w["sa"] == sa]


def ddp_col(rows, nm, k):
    """The column of identifier H8/H8/<nm> in row 5 (Unique Identifier:), matched on the whole text; the mutant takes position k of the wanted list."""
    if M("g1_select_by_index"):
        return 1 + k if 1 + k < len(rows[4]) else None
    hits = [i for i, x in enumerate(rows[4]) if i > 0 and x.strip() == "H8/H8/" + nm]
    return hits[0] if len(hits) == 1 else None


def ddp_basis(desc):
    d = desc.lower()
    return "NSA" if BASIS_PHRASE["NSA"] in d else ("SA" if BASIS_PHRASE["SA"] in d else None)


def parse_ddp(body, grp, sa):
    """R3b for one DDP package: the first six lines, the wanted identifiers, the multiplier. Returns {name: {week: usd_mn text}}."""
    try:
        text = body.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ContentError("the body is not UTF-8 text")
    rows = list(csv.reader(io.StringIO(text)))
    labels = ("Series Description", "Unit:", "Multiplier:", "Currency:", "Unique Identifier:", "Time Period")
    if len(rows) < 7 or any(not rows[i] or rows[i][0].strip() != labels[i] for i in range(6)):
        raise ContentError("the first six lines do not carry %s" % ", ".join(labels))
    out = {}
    for k, nm in enumerate(pkg_names(grp, sa)):
        c = ddp_col(rows, nm, k)
        if c is None:
            raise ContentError("identifier H8/H8/%s is missing or appears twice" % nm)
        desc = rows[0][c]
        if GROUP_PHRASE[grp] not in desc.lower() or ddp_basis(desc) != sa:
            raise ContentError("%s: the description %r does not name %s / %s" % (nm, desc[:90], GROUP_PHRASE[grp], BASIS_PHRASE[sa]))
        if rows[2][c].strip() != UNIT_MULT_OK:
            raise ContentError("%s: Multiplier is %r, expected %s" % (nm, rows[2][c], UNIT_MULT_OK))
        if rows[1][c].strip() != "Currency" or rows[3][c].strip() != "USD":
            raise ContentError("%s: Unit/Currency are %r/%r" % (nm, rows[1][c], rows[3][c]))
        d = {}
        for r in rows[6:]:
            if not r or c >= len(r) or r[c].strip() == "":
                continue
            try:
                D_(r[0])
                decimal.Decimal(r[c])
            except (ValueError, decimal.InvalidOperation):
                raise ContentError("%s: a data row %r is not a date and a number" % (nm, r[:1]))
            d[r[0]] = usd_mn_str(r[c], rows[2][c])
        out[nm] = d
    return out


# ---- Notes on Data -------------------------------------------------------------------------------------------------------
class _NotesParser(html.parser.HTMLParser):
    """Collects <div class="datanote"> entries: the dated heading <a name="notes_YYYYMMDD"> and every <p> that follows, in order."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.entries, self.cur, self.in_p, self.buf, self.text = [], None, False, [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "div" and "datanote" in (a.get("class") or ""):
            self.cur = dict(date=None, paras=[])
        elif M("g15_index_as_note") and tag == "a" and (a.get("href") or "").startswith("#notes_"):
            self.cur = dict(date=a["href"][7:], paras=[])
            self.entries.append(self.cur)
        elif self.cur is not None and tag == "a" and (a.get("name") or "").startswith("notes_"):
            n = a["name"][6:]
            if len(n) == 8 and n.isdigit():
                self.cur["date"] = "%s-%s-%s" % (n[:4], n[4:6], n[6:])
                self.entries.append(self.cur)
        elif self.cur is not None and tag == "p":
            self.in_p, self.buf = True, []

    def handle_data(self, data):
        if self.in_p:
            self.buf.append(data)
        self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "p" and self.in_p:
            self.in_p = False
            if self.cur is not None:
                self.cur["paras"].append(re.sub(r"\s+", " ", "".join(self.buf)).strip())
        elif tag == "div":
            self.cur = None


def parse_notes_entries(text):
    """[{date: ISO, paras: [text...]}], one per dated entry, in page order. The leading index (a run of dates) is not an entry."""
    p = _NotesParser()
    p.feed(text)
    p.close()
    ents = []
    for e in p.entries:
        if e["date"] is not None:
            d = e["date"]
            if len(d) == 8 and d.isdigit():
                d = "%s-%s-%s" % (d[:4], d[4:6], d[6:])
            ents.append(dict(date=d, paras=e["paras"]))
    return ents, " ".join(p.text)


def test_notes(body):
    """R3b: the page holds the heading text 'Notes on Data' and at least one dated note."""
    try:
        text = body.decode("utf-8", errors="replace")
    except Exception:
        raise ContentError("the body is not text")
    ents, plain = parse_notes_entries(text)
    if "Notes on Data" not in plain and "Notes on Data" not in text:
        raise ContentError("no 'Notes on Data' heading")
    if not ents:
        raise ContentError("no dated note")
    return ents


NAMES_LINE38_RX = re.compile(r"net due to related foreign offices", re.I)
AMOUNT_RX = re.compile(r"net due to related foreign offices,\s*(-?)\$\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*billion", re.I)


def para_group(p):
    """The group of one paragraph: whichever group phrase comes first in its text (per paragraph, not per entry). None if no group is named."""
    low = p.lower()
    best = None
    for g, phrase in GROUP_PHRASE.items():
        i = low.find(phrase)
        if i >= 0 and (best is None or i < best[0]):
            best = (i, g)
    return best[1] if best else None


def text_head_of(p, m):
    """The item clause that carries the amount, as the Board wrote it ("net due to related foreign offices, -$3.0 billion"). The Board's own opening and reason clauses are not
    copied: they give reasons in words that the wording guard (R5) bans in this folder."""
    return re.sub(r"\s+", " ", m.group(0)).strip()


def notes_rows(entries, first_week=FIRST_WEEK):
    """notes.csv rows from parsed entries: one row per paragraph naming the line; footnote 20 added. Sorted by week, paragraph index."""
    rows = []
    for e in entries:
        paras = e["paras"][:1] if M("g15_undated_dropped") else e["paras"]
        egroup = para_group(e["paras"][0]) if (e["paras"] and M("g15_group_per_entry")) else None
        for i, p in enumerate(paras):
            m = AMOUNT_RX.search(p)
            if not NAMES_LINE38_RX.search(p):
                continue
            if m is None:
                raise DataError("note %s paragraph %d names the line but carries no amount" % (e["date"], i))
            g = egroup or para_group(p)
            if g is None:
                raise DataError("note %s paragraph %d names the line but no group" % (e["date"], i))
            sign = "" if M("g15_sign_lost") else m.group(1)
            amt = float((sign + m.group(2)).replace(",", "")) * 1000.0
            rows.append(dict(week=e["date"], group=g, amount=amt, kind="note", para=i, head=text_head_of(p, m)))
    rows = [r for r in rows if r["week"] >= first_week]
    rows.append(dict(week=FOOTNOTE20_WEEK, group="FRI", amount=None, kind="footnote", para=None, head=FOOTNOTE20_HEAD))
    rows.sort(key=lambda r: (r["week"], -1 if r["para"] is None else r["para"], r["group"]))
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# the network: one opener, one Fetcher, the STOP latch (R3, R3a, G12, G13)
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
        body = b"".join(chunks)
        if hdrs.get("content-encoding", "").lower() == "gzip":      # asked for identity; a server that compresses anyway is still read
            body = gzip.decompress(body)
        return status, body, hdrs
    except (OSError, EOFError, http.client.HTTPException) as e:
        raise SocketFault(type(e).__name__)
    finally:
        conn.close()


def esc_head(body, n=300):
    return (body or b"")[:n].decode("latin-1").encode("unicode_escape").decode("ascii")


def stop_fields(status, utc_time, url_path, retry_after, body_head):
    lines = ["status: %s" % status, "utc_time: %s" % utc_time, "url_path: %s" % url_path]
    if not M("g12_stop_short"):
        lines.append("retry_after: %s" % retry_after)
    lines.append("body_head: %s" % body_head)
    return "\n".join(lines) + "\n"


def create_stop(path, text):
    """The one place a STOP file is created: exclusive create ("x"), so an existing latch is never overwritten. The AST scan (G12) allows nothing else."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "x", encoding="utf-8") as fh:
            fh.write(text)
    except FileExistsError:
        pass


class Fetcher:
    """One host, three sources (xml, ddp, notes). Opener, clock, sleeper and the STOP directory are injectable so every rule is testable without a network."""

    def __init__(self, cache, out_dir, stop_dir=STOP_DIR, sleep=None, max_requests=None, opener=real_opener, wall=time.time, mono=time.monotonic,
                 sleeper=time.sleep, now_utc=None, root=ROOT):
        self.sleep = float(DEFAULT_SLEEP if sleep is None else sleep)
        if self.sleep < MIN_SLEEP and not M("g13_pacing_off"):
            raise Refused("--sleep must be at least %g seconds" % MIN_SLEEP)
        self.max_requests = MAX_REQUESTS if max_requests is None else max_requests
        if self.max_requests > MAX_REQUESTS or self.max_requests < 1:
            raise Refused("the request cap must be between 1 and %d" % MAX_REQUESTS)
        self.out_dir = out_dir
        self.cache = check_cache(cache, root=root, out_dir=out_dir)
        self.stop_dir = stop_dir
        self.opener, self.wall, self.mono, self.sleeper = opener, wall, mono, sleeper
        self.now_utc = now_utc or (lambda: dt.datetime.now(dt.timezone.utc))
        self.requests = 0
        self._last_mono = None
        self._last_file = os.path.join(self.cache, ".last_request")
        self.log_path = os.path.join(out_dir, "fetch_log.csv")

    def utc_str(self):
        return self.now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")

    def stop_path(self, source):
        return os.path.join(self.stop_dir, "STOP_" + source)

    def check_stop(self, source):
        if os.path.exists(self.stop_path(source)) and not M("g12_stop_ignored"):
            raise Latched("STOP present: %s" % tilde(self.stop_path(source)))

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
        if wait > 0 and not M("g13_pacing_off"):
            self.sleeper(min(wait, self.sleep))

    @staticmethod
    def _stamp(ts):
        return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % int((ts % 1) * 1000)

    def _log(self, ts, target, status, nbytes, sha):
        _, rows = read_csv_rows(self.log_path)
        rows.append([self._stamp(ts), HOST, target, str(status), str(nbytes), sha])
        write_text(self.log_path, render_csv("fetch_log.csv", rows, fetch_source_line(rows)))

    def _latch(self, source, status, target, retry_after, body, why):
        """Write the STOP file (exclusive create) and end this source's run."""
        text = stop_fields(status, self.utc_str(), target, retry_after or "", esc_head(body))
        create_stop(self.stop_path(source), text)
        raise Latched("STOP written: %s (%s)" % (tilde(self.stop_path(source)), why))

    def _get(self, target):
        check_url("https://" + HOST + target)
        if self.requests >= self.max_requests and not M("g13_cap_off"):
            raise MaxRequests("request cap reached (%d)" % self.max_requests)
        self._pace()
        started = self.wall()
        self._last_mono = self.mono()
        os.makedirs(self.cache, exist_ok=True)
        write_text(self._last_file, "%r\n" % started)
        self.requests += 1
        try:
            status, body, rh = self.opener(HOST, target, dict(HEADERS), TIMEOUT, BODY_CAP)
        except SocketFault:
            self._log(started, target, "socket_fault", "", "")
            raise
        return status, body, rh, started

    def get_checked(self, source, target, testfn):
        """GET and test one URL. Anything but a 200 with a body that passes testfn latches this source. Returns (raw bytes, headers, parsed)."""
        self.check_stop(source)
        status, body, rh, started = self._get(target)
        if status in (429, 500) and M("g13_retry"):
            status, body, rh, started = self._get(target)
        if status != 200:
            self._log(started, target, status, "", "")
            if status // 100 == 3 and M("g13_redirect_follow"):
                status, body, rh, started = self._get(target)
            else:
                self._latch(source, status, target, rh.get("retry-after", ""), body, "HTTP %s" % status)
        if body is None:
            self._log(started, target, status, "", "")
            self._latch(source, status, target, "", b"", "body larger than the cap")
        self._log(started, target, status, len(body), sha256_of(body))
        try:
            parsed = testfn(body)
        except (ContentError, DataError) as e:
            self._latch(source, status, target, "", body, "content test: %s" % e)
        return body, rh, parsed


def fetch_source_line(rows):
    ds = sorted({r[0][:10] for r in rows if len(r) > 4 and r[3] == "200" and r[4]})
    return ("# source: Board of Governors of the Federal Reserve System (%s) retrieved %s; request log of bin/h8_foreign_offices.py fetch (one row per request)"
            % (HOST, ", ".join(ds) if ds else "(no logged retrieval)"))


# ------------------------------------------------------------------------------------------------------------------------
# the cache: index of vintages, 20-series subsets, DDP packages, notes pages (R4)
# ------------------------------------------------------------------------------------------------------------------------
INDEX_COLS = ["vintage", "route", "xml_prepared", "xml_last_modified", "xml_sha256", "fetched_utc"]


def vintage_key(route, prepared, fetch_date):
    """The XML's Prepared date on the XML route; fetch-<utc-date> on the DDP fallback (O-9)."""
    if route == "xml" and not M("g8_xml_keyed_by_fetch_date"):
        return prepared[:10]
    return "fetch-" + fetch_date


def order_key(key):
    """Vintages are ordered by the date in their key; on a tie the XML vintage comes before the fallback one."""
    return (key[-10:], 1 if key.startswith("fetch-") else 0)


def index_path(cache):
    return os.path.join(cache, "index.csv")


def read_index(cache):
    _, rows = read_csv_rows(index_path(cache))
    return [dict(zip(INDEX_COLS, r)) for r in rows]


def write_index(cache, rows):
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(INDEX_COLS)
    for r in sorted(rows, key=lambda x: order_key(x["vintage"])):
        w.writerow([r[c] for c in INDEX_COLS])
    write_text(index_path(cache), out.getvalue())


def index_problems(rows):
    """One Prepared date must have one zip hash (R2-9); a vintage key appears once."""
    out, seen, keys = [], {}, collections.Counter(r["vintage"] for r in rows)
    for r in rows:
        if r["route"] != "xml":
            continue
        p, h = r["xml_prepared"], r["xml_sha256"]
        if p in seen and seen[p] != h and not M("g8_same_prepared_accepted"):
            out.append("Prepared %s has two zip hashes (%s..., %s...)" % (p, seen[p][:10], h[:10]))
        seen.setdefault(p, h)
    out += ["vintage %s appears %d times in the index" % (k, n) for k, n in sorted(keys.items()) if n > 1]
    return out


def latest_week_of(vals):
    ws = vals.get(sname("1100", "FRD"), {})
    return max(ws) if ws else ""


def vintage_problems(vints):
    """A vintage whose latest week is earlier than the vintage before it is a FAIL (R2-9)."""
    out = []
    for a, b in zip(vints, vints[1:]):
        la, lb = latest_week_of(a["vals"]), latest_week_of(b["vals"])
        if lb < la and not M("g8_earlier_latest_accepted"):
            out.append("vintage %s ends at %s, earlier than vintage %s which ends at %s" % (b["key"], lb, a["key"], la))
    return out


# ---- subset files --------------------------------------------------------------------------------------------------------
def attrs_line(nm, attrs):
    keys = ("BG", "SA", "CATEGORY", "ITEM", "FREQ", "UNIT_MULT", "SRC", "NONA")
    return "# attrs: %s %s" % (nm, " ".join("%s=%s" % (k, attrs[k]) for k in keys if k in attrs))


def subset_text(key, route, prepared, last_modified, attrs, codes, vals):
    """The 20-series subset of one vintage: comment lines of metadata, then one row per week (union of weeks), values in usd_mn as published."""
    out = ["# vintage: %s" % key, "# route: %s" % route, "# prepared: %s" % prepared, "# last_modified: %s" % last_modified, "# unit: usd_mn"]
    for nm in WANTED:
        out.append(attrs_line(nm, attrs[nm]))
    out.append("# codes: CL_CATEGORY L=%s | CL_ITEM 1100=%s" % (codes.get("cat", {}).get("L", ""), codes.get("item", {}).get("1100", "")))
    weeks = sorted({w for nm in WANTED for w in vals.get(nm, {})})
    buf = io.StringIO()
    wr = csv.writer(buf, lineterminator="\n")
    wr.writerow(["week_wed"] + list(WANTED))
    for w in weeks:
        wr.writerow([w] + [vals.get(nm, {}).get(w, "") for nm in WANTED])
    return "\n".join(out) + "\n" + buf.getvalue()


def parse_subset(text):
    meta, attrs, body = {}, {}, []
    for ln in text.splitlines():
        if ln.startswith("# attrs: "):
            parts = ln[9:].split(" ")
            attrs[parts[0]] = dict(p.split("=", 1) for p in parts[1:] if "=" in p)
        elif ln.startswith("# "):
            k, _, v = ln[2:].partition(": ")
            meta[k] = v
        else:
            body.append(ln)
    rd = list(csv.reader(body))
    hdr = rd[0]
    if hdr[0] != "week_wed" or hdr[1:] != list(WANTED):
        raise DataError("a subset file does not carry the 20 series in the spec's order")
    vals = {nm: {} for nm in WANTED}
    for r in rd[1:]:
        for nm, v in zip(hdr[1:], r[1:]):
            if v != "":
                vals[nm][r[0]] = v
    codes = {"cat": {"L": meta.get("codes", "").split("L=", 1)[-1].split(" | ")[0]}, "item": {"1100": meta.get("codes", "").split("1100=", 1)[-1]}}
    return dict(key=meta.get("vintage", ""), route=meta.get("route", ""), prepared=meta.get("prepared", ""), last_modified=meta.get("last_modified", ""),
                attrs=attrs, codes=codes, vals=vals)


def float_vals(V, nm):
    cache = V.setdefault("_f", {})
    if nm not in cache:
        cache[nm] = {w: float(v) for w, v in V["vals"].get(nm, {}).items()}
    return cache[nm]


def xml_to_vals(parsed):
    """{name: {week: usd_mn text}} for status A, attributes with the count of observations that are not 'A', from a parsed XML zip."""
    vals, attrs = {}, {}
    for nm in WANTED:
        s = parsed["series"][nm]
        mult = s["attrs"]["UNIT_MULT"]
        vals[nm] = {w: usd_mn_str(v, mult) for w, (v, st) in sorted(s["obs"].items()) if st == "A" and v not in (None, "")}
        a = {k: s["attrs"].get(k, "") for k in ("BG", "SA", "CATEGORY", "ITEM", "FREQ", "UNIT_MULT")}
        a["SRC"] = "xml"
        a["NONA"] = str(sum(1 for w, (v, st) in s["obs"].items() if st != "A"))
        attrs[nm] = a
    return vals, attrs


def ddp_to_vals(parts):
    """The same from the four parsed DDP packages (route ddp_fallback). The attributes are the ones the content test asserted."""
    vals, attrs = {}, {}
    for (grp, sa), d in parts.items():
        for nm in pkg_names(grp, sa):
            w = WANTED[nm]
            vals[nm] = d[nm]
            attrs[nm] = dict(BG=w["bg"], SA=w["sa"], CATEGORY="L", ITEM=w["item"], FREQ="19", UNIT_MULT=UNIT_MULT_OK, SRC="ddp", NONA="0")
    return vals, attrs


def subset_path(cache, key):
    return os.path.join(cache, "subset", "h8_%s.csv" % key)


def ingest_xml(cache, body, parsed, last_modified, fetched_utc):
    """Save a validated XML zip as a vintage: the zip (newest only), the 20-series subset, an index row. Returns (key, is_new)."""
    prepared = parsed["prepared"]
    key = vintage_key("xml", prepared, fetched_utc[:10])
    sha = sha256_of(body)
    idx = read_index(cache)
    new_row = dict(vintage=key, route="xml", xml_prepared=prepared, xml_last_modified=last_modified, xml_sha256=sha, fetched_utc=fetched_utc)
    existing = [r for r in idx if r["route"] == "xml" and r["xml_prepared"] == prepared and r["xml_sha256"] == sha]
    if existing:
        return key, False
    probs = index_problems(idx + [new_row])
    if probs:
        raise DataError("; ".join(probs))
    vals, attrs = xml_to_vals(parsed)
    write_bytes(os.path.join(cache, "xml", "FRB_h8_xml_%s.zip" % key), body)
    write_text(subset_path(cache, key), subset_text(key, "xml", prepared, last_modified, attrs, parsed["codes"], vals))
    idx.append(new_row)
    write_index(cache, idx)
    prune_old_zips(cache, idx)
    return key, True


def ingest_ddp_fallback(cache, key, parts, fetched_utc):
    """The four DDP packages as a fallback vintage keyed fetch-<utc-date> (O-9). Returns True when a new vintage was written."""
    idx = read_index(cache)
    if any(r["vintage"] == key for r in idx):
        return False
    vals, attrs = ddp_to_vals(parts)
    write_text(subset_path(cache, key), subset_text(key, "ddp_fallback", "", "", attrs, {}, vals))
    idx.append(dict(vintage=key, route="ddp_fallback", xml_prepared="", xml_last_modified="", xml_sha256="", fetched_utc=fetched_utc))
    write_index(cache, idx)
    return True


def prune_old_zips(cache, idx):
    """Keep only the newest zip. Old zips are removed by their exact file names, taken from the index; never by a glob or a listing (R2-10)."""
    xml_rows = [r for r in idx if r["route"] == "xml"]
    if not xml_rows:
        return []
    newest = max(r["vintage"] for r in xml_rows)
    gone = []
    for r in xml_rows:
        if r["vintage"] != newest:
            name = "FRB_h8_xml_%s.zip" % r["vintage"]
            p = os.path.join(cache, "xml", name)
            if os.path.exists(p):
                os.remove(p)
                gone.append(name)
    return gone


def ddp_path(cache, label, key):
    return os.path.join(cache, "ddp", "%s_%s.csv" % (label, key))


def notes_path(cache, date):
    return os.path.join(cache, "notes", "h8notes_%s.htm" % date)


def newest_notes(cache):
    d = os.path.join(cache, "notes")
    names = sorted(n for n in (os.listdir(d) if os.path.isdir(d) else []) if re.fullmatch(r"h8notes_\d{4}-\d{2}-\d{2}\.htm", n))
    return (os.path.join(d, names[-1]), names[-1][8:18]) if names else (None, None)


def load_vintages(cache):
    """All cached vintages in order, each with its subset; DDP presence per vintage. The index is authoritative."""
    idx = read_index(cache)
    out = []
    for r in sorted(idx, key=lambda x: order_key(x["vintage"])):
        p = subset_path(cache, r["vintage"])
        if not os.path.exists(p):
            raise DataError("the index lists vintage %s but its subset file is missing" % r["vintage"])
        V = parse_subset(read_file(p, "r"))
        if V["key"] != r["vintage"] or V["route"] != r["route"]:
            raise DataError("subset file of %s disagrees with the index" % r["vintage"])
        V["index"] = r
        V["ddp"] = {}
        for label, _, grp, sa in DDP_PACKAGES:
            dp = ddp_path(cache, label, r["vintage"])
            if os.path.exists(dp):
                V["ddp"][label] = parse_ddp(read_file(dp), grp, sa)
        out.append(V)
    return out


def stop_state(stop_dir):
    return {s: os.path.exists(os.path.join(stop_dir, "STOP_" + s)) for s in SOURCES}


def route_state(vints, stops):
    """('ok', '') or ('exit2', why). With no vintage, or STOP_xml together with STOP_ddp, or STOP_xml and no fallback vintage as the newest one, no route is left."""
    if M("g7_both_failed_builds"):
        return ("ok", "") if vints else ("exit2", "no vintage in the cache")
    if not vints:
        return "exit2", "no vintage in the cache; run fetch first"
    if M("g7_ddp404_aborts") and stops.get("ddp"):
        return "exit2", "mutant: a DDP latch aborts the build"
    if M("g7_xml500_refuses") and stops.get("xml"):
        return "exit2", "mutant: an XML latch refuses the build"
    if stops.get("xml") and stops.get("ddp"):
        return "exit2", "STOP_xml together with STOP_ddp: no route is left"
    if stops.get("xml") and vints[-1]["route"] != "ddp_fallback":
        return "exit2", "STOP_xml is present and the newest cached vintage did not come from the DDP"
    return "ok", ""


def ddp_status_of(V):
    n = len(V.get("ddp", {}))
    return "ok" if n == len(DDP_PACKAGES) else ("ddp_unavailable" if n == 0 else "ddp_partial")


# ---- fetch orchestration --------------------------------------------------------------------------------------------------
def do_fetch(fe, say=print):
    """Up to six requests: the XML zip, four DDP packages, the notes page. Returns a dict of outcomes; never retries."""
    res = dict(xml="skipped", ddp="skipped", notes="skipped", key=None, route=None, fallback=False)
    fetched = fe.utc_str()
    date = fetched[:10]
    parts = {}
    if all(os.path.exists(fe.stop_path(s)) for s in ("xml", "ddp")) and not M("g12_stop_ignored"):
        for s in ("xml", "ddp"):
            say("STOP present: %s" % tilde(fe.stop_path(s)))
        return res                                                # no route is left: no request at all
    # XML (primary)
    try:
        body, rh, parsed = fe.get_checked("xml", XML_PATH, test_xml_zip)
        lm = rh.get("last-modified", "")
        try:
            lm = email.utils.parsedate_to_datetime(lm).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if lm else ""
        except (TypeError, ValueError):
            pass
        key, new = ingest_xml(fe.cache, body, parsed, lm, fetched)
        res.update(xml="ok", key=key, route="xml")
        say("xml: vintage %s (%s), prepared %s, %d bytes, sha256 %s" % (key, "new" if new else "already cached", parsed["prepared"], len(body), sha256_of(body)[:16]))
    except Latched as e:
        say(str(e))
        res["xml"] = "latched"
    # DDP (cross-check, and the fallback while the XML is latched)
    key = res["key"] or "fetch-" + date
    got = {}
    try:
        for label, pid, grp, sa in DDP_PACKAGES:
            body, rh, p = fe.get_checked("ddp", DDP_FMT % pid, lambda b, g=grp, s=sa: parse_ddp(b, g, s))
            got[label] = (body, p, grp, sa)
            write_bytes(ddp_path(fe.cache, label, key), body)
            say("ddp: %s saved (%d bytes)" % (label, len(body)))
        res["ddp"] = "ok"
    except Latched as e:
        say(str(e))
        res["ddp"] = "latched" if not got else "partial"
    if res["xml"] != "ok" and len(got) == len(DDP_PACKAGES):
        parts = {(g, s): p for _, (b, p, g, s) in got.items()}
        res["fallback"] = ingest_ddp_fallback(fe.cache, key, parts, fetched)
        res.update(key=key, route="ddp_fallback")
        say("ddp: fallback vintage %s %s" % (key, "written" if res["fallback"] else "already cached"))
    # Notes on Data
    try:
        body, rh, ents = fe.get_checked("notes", NOTES_PATH, test_notes)
        write_bytes(notes_path(fe.cache, date), body)
        res["notes"] = "ok"
        say("notes: %d dated entries, %d bytes" % (len(ents), len(body)))
    except Latched as e:
        say(str(e))
        res["notes"] = "latched"
    return res


def fetch_exit_code(res):
    return 0 if res["xml"] == "ok" or res["fallback"] else 2


# ------------------------------------------------------------------------------------------------------------------------
# the data: groups, identities, binding (spec 2.2, 3.2, 3.4; G1, G2, G3, G4)
# ------------------------------------------------------------------------------------------------------------------------
TOL = 0.5
NEG_FROM = "2019-01-02"
GROUPS_SA = (("FRI", "NSA"), ("DOM", "NSA"), ("ALL", "NSA"), ("FRI", "SA"))
LINE_KEYS = ("l38", "l40", "l34", "l37", "l39")


def assemble(V):
    """{(group, basis): {line: {week: float}}} selected by exact series name. The mutants break exactly this step."""
    out = {}
    for nm, w in WANTED.items():
        d = float_vals(V, nm)
        if M("g2_negate_l38") and w["line"] == "l38":
            d = {k: -v for k, v in d.items()}
        out.setdefault((w["group"], w["sa"]), {})[w["line"]] = d
    if M("g1_swap_l38"):
        a, b = out[("FRI", "NSA")], out[("DOM", "NSA")]
        a["l38"], b["l38"] = b["l38"], a["l38"]
    if M("g1_swap_groups"):
        out[("FRI", "NSA")], out[("DOM", "NSA")] = out[("DOM", "NSA")], out[("FRI", "NSA")]
    return out


def lvl(A, grp, line="l38", sa="NSA"):
    """A level table for statistics: not seasonally adjusted (the choice of 2.1). The mutant reads the seasonally adjusted series for FRI."""
    if M("g4_sa_stat") and grp == "FRI":
        sa = "SA"
    return A[(grp, sa)][line]


def identity_breaches(A, tol=None):
    """Line 38 = line 40 - (34 + 37 + 39) in every group and basis, every week they all have. Returns (breaches, weeks checked per group, max |gap|)."""
    tol = (2.0 if M("g2_breach_unreported") else TOL) if tol is None else tol
    out, counts, mx = [], {}, 0.0
    for key, d in A.items():
        ws = sorted(set.intersection(*[set(d[l]) for l in LINE_KEYS]))
        counts[key] = len(ws)
        for w in ws:
            sub = d["l34"][w] * (2 if M("g2_double_count") else 1) + d["l37"][w] + d["l39"][w]
            gap = d["l38"][w] - (d["l40"][w] - sub)
            mx = max(mx, abs(gap))
            if abs(gap) > tol:
                out.append((key, w, gap))
    return out, counts, mx


def group_breaches(A, tol=None):
    """ALL = DOM + FRI (NSA) on every week ALL has."""
    tol = (2.5 if M("g3_tol_2mn") else TOL) if tol is None else tol
    fri = A[("FRI", "SA" if M("g3_all_from_sa") else "NSA")]["l38"]
    dom, al = A[("DOM", "NSA")]["l38"], A[("ALL", "NSA")]["l38"]
    return [(w, al[w] - (dom[w] + fri[w])) for w in sorted(al) if w in dom and w in fri and abs(al[w] - (dom[w] + fri[w])) > tol]


def dominance(A):
    """DOM line 40 exceeds FRI line 40 on every week both have. Returns (weeks where it does not, minimum ratio)."""
    fri, dom = A[("FRI", "NSA")]["l40"], A[("DOM", "NSA")]["l40"]
    bad = [w for w in sorted(dom) if w in fri and not dom[w] > fri[w]]
    ratios = [dom[w] / fri[w] for w in dom if w in fri and fri[w] > 0]
    return bad, (min(ratios) if ratios else None)


def binding(A):
    """The binding of 3.4 and R3-6: groups are bound by identities, never by sign. FAILs and WARNs are returned apart; a negative FRI level is a WARN."""
    fails, warns = [], []
    ib, counts, mx = identity_breaches(A)
    fails += ["identity %s/%s %s gap %.1f" % (k[0], k[1], w, g) for k, w, g in ib[:5]]
    gb = group_breaches(A)
    fails += ["ALL != DOM + FRI on %s by %.1f" % (w, g) for w, g in gb[:5]]
    bad, minratio = dominance(A)
    fails += ["DOM line 40 does not exceed FRI line 40 on %s" % w for w in bad[:5]]
    if M("g3_fri_le_all"):
        fri, al = A[("FRI", "NSA")]["l38"], A[("ALL", "NSA")]["l38"]
        fails += ["FRI exceeds ALL on %s" % w for w in sorted(al) if w in fri and fri[w] > al[w]][:5]
    fri = A[("FRI", "NSA")]["l38"]
    neg = [w for w in sorted(fri) if w >= NEG_FROM and fri[w] < 0]
    if neg:
        (fails if M("g1_negative_fri_fails") else warns).append("FRI NSA is negative on %d week(s) from %s: %s" % (len(neg), NEG_FROM, ", ".join(neg[:8])))
    return dict(fails=fails, warns=warns, identity=ib, counts=counts, maxgap=mx, group=gb, dominance_bad=bad, minratio=minratio, neg=neg)


# ------------------------------------------------------------------------------------------------------------------------
# breaks and segments (3.5, R3-3; G14), the quarter-end calendar (3.7; G6), the named endpoints (section 4; G17)
# ------------------------------------------------------------------------------------------------------------------------
def break_map(notes, grp):
    """{break week: sorted kinds} for one group: its own Notes on Data weeks, plus footnote 20 for FRI and ALL. ALL takes the union."""
    out = {}
    for n in notes:
        g, kind = n["group"], n["kind"]
        use = (g == "FRI" and grp in ("FRI", "ALL")) or (g == "DOM" and grp in ("DOM", "ALL")) or (g == "ALL" and grp == "ALL")
        if M("g14_dom_note_as_fri") and g == "DOM" and grp == "FRI":
            use = True
        if M("g14_footnote_missing") and kind == "footnote":
            use = False
        if use and n["week"] >= FIRST_WEEK:
            out.setdefault(n["week"], set()).add(kind)
    return {w: sorted(k) for w, k in out.items()}


def seg_start(w, brk_sorted, first=FIRST_WEEK):
    """The first week of the segment holding week w: the latest break week on or before it, else the first ledger week. The break week opens the new segment."""
    return max([b for b in brk_sorted if b <= w], default=first)


def seg_change(d, w, brk_sorted):
    """The change ending at week w, or None when it ends at a break week (it belongs to no segment) or has no previous week."""
    p = addd(w, -7)
    if w not in d or p not in d:
        return None
    if w in brk_sorted and not M("g14_change_in_segment"):
        return None
    return d[w] - d[p]


def seg_windows(brk_sorted, start, last):
    """Windows [first week, last week] of the segments inside [start, last]; each break week opens a new one."""
    pts = [start] + [b for b in brk_sorted if start < b <= last]
    return [(s, last if i == len(pts) - 1 else addd(pts[i + 1], -7)) for i, s in enumerate(pts)]


def crosses_break(s, e, brk):
    """True when a break week lies in (s, e]: the change from s to e would span it."""
    return any(s < b <= e for b in brk)


def quarter_end(y, q):
    m = 3 * q
    return dt.date(y, m, calendar.monthrange(y, m)[1])


def qe_wed(D):
    """(W(q), offset): the Wednesday nearest the quarter-end day D, with W - D in -3..+3 days (3.7)."""
    wd = D.weekday()
    if M("g6_last_wed_before"):
        off = -((wd - 2) % 7)
    elif M("g6_first_wed_after"):
        off = (2 - wd) % 7
    else:
        off = (2 - wd + 3) % 7 - 3
    return D + dt.timedelta(days=off), off


def quarter_label(y, q):
    return "%dQ%d" % (y, q)


def quarter_iter(first=(2004, 2), last_year=2030):
    for y in range(first[0], last_year + 1):
        for q in range(1, 5):
            if (y, q) >= first:
                yield y, q


def qe_week_map(L):
    """{week: (quarter label, role, offset)} for every Wednesday that is W(q) (qe) or W(q)+7 (after_qe) up to week L."""
    out = {}
    for y, q in quarter_iter():
        W, off = qe_wed(quarter_end(y, q))
        w = W.isoformat()
        if w > L:
            break
        out[w] = (quarter_label(y, q), "qe", off)
        n = addd(w, 7)
        if n <= L:
            out[n] = (quarter_label(y, q), "qe" if M("g6_after_is_qe") else "after_qe", off)
    return out


def is_frozen(y, q):
    if M("g6_post_frozen"):
        return True
    return FROZEN_FIRST <= (y, q) <= ((2026, 4) if M("g6_frozen_last_q4") else FROZEN_LAST)


def blind_of(kind, label):
    """The blind mark (section 4): 'no' on every Q1, Q2, Q4 and Q6 row, on the 2026Q3 rows, 'yes' on every other row."""
    if kind in ("Q1", "Q2", "Q4", "Q6"):
        return "yes" if M("g16_%s_yes" % kind.lower()) else "no"
    if label.startswith("2026Q3"):
        return "yes" if M("g16_2026q3_yes") else "no"
    return "no" if M("g16_other_no") else "yes"


def quarter_table(A, L, brk, vkey):
    """quarter_ends.csv rows for FRI and DOM (NSA): one per quarter from 2019Q1 with W(q) <= L. Frozen set = 2019Q1..2026Q3 (R2-7)."""
    rows = []
    for y, q in quarter_iter(FROZEN_FIRST):
        D = quarter_end(y, q)
        W, off = qe_wed(D)
        w = W.isoformat()
        if w > L:
            break
        on_date = (abs(off) <= 1) if M("g6_nonwed_on_date") else (off == 0)
        in_window = True if M("g6_window_neg") else off >= 0
        lab = quarter_label(y, q)
        for grp in ("FRI", "DOM"):
            d = lvl(A, grp, "l38")
            wm, wn = addd(w, -7), addd(w, 7)
            lev = d.get(w)
            dq = (lev - d[wm]) if lev is not None and wm in d else None
            dn = (d[wn] - lev) if lev is not None and wn in d and wn <= L else None
            strad = w in brk[grp] or (wn in d and wn <= L and wn in brk[grp])
            if not M("g14_fill_straddle"):                   # R3-3: a change that ends on a break week crosses it and is left blank (straddles_break says why)
                dq = None if w in brk[grp] else dq
                dn = None if wn in brk[grp] else dn
            rows.append([lab, D.isoformat(), w, "%d" % off, yn(on_date), grp, fnum(lev, 1), fnum(dq, 1), fnum(dn, 1), yn(in_window), yn(strad),
                         yn(is_frozen(y, q)), blind_of("Q3", lab), vkey])
    return rows


def qe_days(first_year=2003, last_year=2031):
    return [quarter_end(y, q) for y in range(first_year, last_year + 1) for q in range(1, 5)]


def qe_distance(w):
    d = D_(w)
    return min(abs((d - D).days) for D in qe_days())


def ordinary_problems(w, brk_weeks):
    """An ordinary Wednesday: a Wednesday, at least 7 days from every quarter-end day, not a break week."""
    out = []
    if not is_wed(w):
        out.append("not a Wednesday")
    if qe_distance(w) < (3 if M("g17_qe_lt3") else 7) and not M("g17_near_qe_ok"):
        out.append("within 7 days of a quarter-end day")
    if w in brk_weeks and not M("g17_break_ok"):
        out.append("a break week")
    return out


def named_problems(w, brk_weeks):
    """A named endpoint: ordinary, and the Wednesday between the 8th and the 14th of February or August (R3-4)."""
    out = ordinary_problems(w, brk_weeks)
    d = D_(w)
    if not (d.month in (2, 8) and 8 <= d.day <= 14) and not M("g17_first_wed"):
        out.append("not the Wednesday between the 8th and the 14th of February or August")
    return out


def lo_week(L, brk_weeks):
    """Lo: the latest Wednesday at or before L that is at least 7 days from every quarter-end day and not a break week. Printed, never an endpoint."""
    w = L
    while w >= FIRST_WEEK:
        if not ordinary_problems(w, brk_weeks):
            return w
        w = addd(w, -7)
    return None


def endpoints(L, brk_weeks):
    eps = list(Q2_ENDPOINTS)
    if M("g17_lo_fixed"):
        eps.append(lo_week(L, brk_weeks))
    return eps


# ------------------------------------------------------------------------------------------------------------------------
# the weekly ledger, quarter-ends, summary (3.3, 3.7, section 4)
# ------------------------------------------------------------------------------------------------------------------------
SUFFIX = {("FRI", "NSA"): "FRD", ("DOM", "NSA"): "DMD", ("ALL", "NSA"): "CBD", ("FRI", "SA"): "FRA"}


def weekly_rows(A, L, brk, vkey):
    """weekly.csv: (week, FRI|DOM|ALL, NSA) and (week, FRI, SA) from 2004-06-02 to L. Change = level minus the previous Wednesday's level (3.3)."""
    qmap = qe_week_map(L)
    bs = {g: sorted(brk[g]) for g in brk}
    rows = []
    for w in weeks_between(FIRST_WEEK, L):
        for grp, sa in GROUPS_SA:
            d, t = lvl(A, grp, "l38", sa), lvl(A, grp, "l40", sa)
            if w not in d or w not in t:
                continue
            chg = seg_change(d, w, bs[grp])                 # blank on a break week: that change spans the break and belongs to no segment
            q = qmap.get(w)
            val = d[w] / 1000.0 if M("g5_bn_in_mn") else d[w]
            rows.append([w, grp, sa, sname("1100", SUFFIX[(grp, sa)]), fnum(val, 1), fnum(chg, 1), fnum(t[w], 1), fnum(100.0 * d[w] / t[w] if t[w] else None, 2),
                         q[0] if q else "", q[1] if q else "none", ("%d" % q[2]) if q else "", seg_start(w, bs[grp]), "+".join(brk[grp].get(w, [])), vkey])
    return rows


def level_stats(d, s, e):
    """First, last, minimum and maximum (with their weeks) over the weekly levels from s to e inclusive; ties go to the earliest week."""
    ws = [w for w in weeks_between(s, e) if w in d]
    if not ws:
        return None
    mn = min(ws, key=lambda w: d[w])                  # min and max keep the earliest week on a tie (ws is in week order)
    mx = max(ws, key=lambda w: d[w])
    return dict(first=ws[0], last=ws[-1], vfirst=d[ws[0]], vlast=d[ws[-1]], mn=mn, vmn=d[mn], mx=mx, vmx=d[mx], n=len(ws))


def srow(q, window, grp, stat, value, unit, blind=None, label=""):
    return [q, window, grp, stat, value, unit, blind if blind is not None else blind_of(q, label or window)]


def q1_rows(A, L, brk):
    rows = []
    for grp in ("FRI", "DOM"):
        d, t = lvl(A, grp, "l38"), lvl(A, grp, "l40")
        bs = sorted(brk[grp])
        wins = [(Q1_START, L)] if M("g14_across_break") else seg_windows(bs, Q1_START, L)
        for s, e in wins:
            st = level_stats(d, s, e)
            if st is None:
                continue
            win = "%s..%s" % (s, e)
            rows += [srow("Q1", win, grp, "first_level", fnum(st["vfirst"], 1), "usd_mn"), srow("Q1", win, grp, "last_level", fnum(st["vlast"], 1), "usd_mn"),
                     srow("Q1", win, grp, "min_level", fnum(st["vmn"], 1), "usd_mn"), srow("Q1", win, grp, "min_week", st["mn"], "date"),
                     srow("Q1", win, grp, "max_level", fnum(st["vmx"], 1), "usd_mn"), srow("Q1", win, grp, "max_week", st["mx"], "date")]
            for w in Q1_WEDNESDAYS:
                if s <= w <= e and w in d:
                    rows += [srow("Q1", win, grp, "level_on_%s" % w, fnum(d[w], 1), "usd_mn"),
                             srow("Q1", win, grp, "pct_of_total_liabilities_on_%s" % w, fnum(100.0 * d[w] / t[w], 2), "pct")]
    return rows


def q2_windows(eps):
    return list(zip(eps, eps[1:]))


def window_stats(d, t, s, e):
    st = level_stats(d, s, e)
    if st is None or s not in d or e not in d:
        return None
    st["change"] = d[e] - d[s]
    st["pct"] = 100.0 * st["change"] / t[s] if s in t and t[s] else None
    return st


def q2_rows(A, L, brk, union):
    rows = []
    eps = endpoints(L, union)
    for grp in ("FRI", "DOM", "ALL"):
        d, t = lvl(A, grp, "l38"), lvl(A, grp, "l40")
        for s, e in q2_windows(eps):
            win = "%s..%s" % (s, e)
            if crosses_break(s, e, brk[grp]):
                rows.append(srow("Q2", win, grp, "crosses_break", "yes", "yes_no"))
                continue
            st = window_stats(d, t, s, e)
            if st is None:
                continue
            rows += [srow("Q2", win, grp, "level_start", fnum(d[s], 1), "usd_mn"), srow("Q2", win, grp, "level_end", fnum(d[e], 1), "usd_mn"),
                     srow("Q2", win, grp, "change", fnum(st["change"], 1), "usd_mn"),
                     srow("Q2", win, grp, "change_pct_of_start_total_liabilities", fnum(st["pct"], 2), "pct"),
                     srow("Q2", win, grp, "min_level", fnum(st["vmn"], 1), "usd_mn"), srow("Q2", win, grp, "min_week", st["mn"], "date"),
                     srow("Q2", win, grp, "max_level", fnum(st["vmx"], 1), "usd_mn"), srow("Q2", win, grp, "max_week", st["mx"], "date")]
    lo = lo_week(L, union)
    for grp in ("FRI", "DOM", "ALL"):
        d = lvl(A, grp, "l38")
        if lo and lo in d:
            rows += [srow("Q2", "Lo", grp, "lo_week", lo, "date"), srow("Q2", "Lo", grp, "level_on_lo", fnum(d[lo], 1), "usd_mn")]
    return rows


def q3_rows(qrows):
    """Part A: the five Wednesday quarter-ends, one single row per statistic, FRI and DOM. No average, count, test or flag across quarters (R3-1)."""
    rows = []
    for r in qrows:
        if r[4] != "yes" or r[11] != "yes":
            continue
        lab, grp = r[0], r[5]
        win = "%s (%s)" % (lab, r[1])
        rows += [srow("Q3", win, grp, "level_qe_wed", r[6], "usd_mn", label=lab), srow("Q3", win, grp, "delta_qe_wed", r[7], "usd_mn", label=lab),
                 srow("Q3", win, grp, "delta_next", r[8], "usd_mn", label=lab)]
    if M("g6_avg_written"):
        vals = [float(r[7]) for r in qrows if r[4] == "yes" and r[5] == "FRI" and r[7]]
        rows.append(srow("Q3", "frozen set", "FRI", "mean_delta_qe_wed", fnum(sum(vals) / len(vals), 1), "usd_mn", label="x"))
    return rows


def q4_rows(A, L, brk, union):
    rows = []
    eps = endpoints(L, union)
    for s, e in q2_windows(eps):
        win = "%s..%s" % (s, e)
        ch = {}
        for grp in ("FRI", "DOM", "ALL"):
            d, t = lvl(A, grp, "l38"), lvl(A, grp, "l40")
            if crosses_break(s, e, brk[grp]):
                if grp != "ALL":
                    rows.append(srow("Q4", win, grp, "crosses_break", "yes", "yes_no"))
                continue
            st = window_stats(d, t, s, e)
            if st:
                ch[grp] = st["change"]
                if grp != "ALL":
                    rows.append(srow("Q4", win, grp, "change", fnum(st["change"], 1), "usd_mn"))
        if len(ch) == 3:
            rows.append(srow("Q4", win, "ALL", "identity_gap_all_minus_dom_minus_fri_change", fnum(ch["ALL"] - ch["DOM"] - ch["FRI"], 1), "usd_mn"))
    return rows


def revision_rows(vints, existing=None, weekly_text=None):
    """revisions.csv, regenerated from every adjacent pair of cached subsets (R2-9). The two mutants read the committed files instead."""
    def pair_rows(a, b):
        out = []
        prev_w = {}
        if M("g8_prev_from_weekly") and weekly_text:
            for ln in weekly_text.splitlines():
                c = ln.split(",")
                if len(c) > 4 and c[3].startswith("B1100"):
                    prev_w[(c[3], c[0])] = c[4]
        for nm in WANTED:
            fa, fb = a["vals"][nm], b["vals"][nm]
            for w in sorted(fa):
                pv = prev_w.get((nm, w), fa[w])
                if w in fb:
                    if decimal.Decimal(pv) != decimal.Decimal(fb[w]):
                        out.append([a["key"], b["key"], nm, w, fnum(float(pv), 1), fnum(float(fb[w]), 1), fnum(float(fb[w]) - float(pv), 1)])
                else:
                    out.append([a["key"], b["key"], nm, w, fnum(float(pv), 1), "", ""])
        return out
    pairs = list(zip(vints, vints[1:]))
    if M("g8_incremental") and existing is not None and pairs:
        return [list(r) for r in existing] + pair_rows(*pairs[-1])
    out = []
    for a, b in pairs:
        out += pair_rows(a, b)
    return out


def q6_rows(vints, revs):
    rows = []
    if len(vints) < 2:
        return [srow("Q6", "none", "FRI", "vintage_pairs", "0", "count")]
    for a, b in zip(vints, vints[1:]):
        win = "%s..%s" % (a["key"], b["key"])
        lnew = latest_week_of(b["vals"])
        old_cut = addd(lnew, -26 * 7)
        for grp in ("FRI", "DOM", "ALL"):
            nm = sname("1100", SUFFIX[(grp, "NSA")])
            rr = [r for r in revs if r[0] == a["key"] and r[1] == b["key"] and r[2] == nm]
            rows.append(srow("Q6", win, grp, "cells_changed", str(len(rr)), "count"))
            ch = [r for r in rr if r[6] != ""]
            if ch:
                big = max(ch, key=lambda r: (abs(float(r[6])), r[3]))
                rows += [srow("Q6", win, grp, "largest_abs_change", fnum(abs(float(big[6])), 1), "usd_mn"), srow("Q6", win, grp, "largest_abs_change_week", big[3], "date")]
            rows.append(srow("Q6", win, grp, "old_week_revised", yn(any(r[3] < old_cut for r in rr)), "yes_no"))
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# the checks (section 8)
# ------------------------------------------------------------------------------------------------------------------------
PINS = {
    "C01": ("B1100NFRD", "FRI NSA line 38", [("2019-01-02", "241674.0"), ("2020-03-25", "341831.0"), ("2024-02-14", "704646.0"), ("2025-02-12", "849074.0"),
                                               ("2025-08-06", "954274.0"), ("2026-02-11", "809580.0"), ("2026-08-05", "839732.0"), ("2026-08-12", "798035.0"),
                                               ("2026-09-30", "855694.0"), ("2026-10-07", "836860.0")]),
    "C02": ("B1100NDMD", "DOM NSA line 38", [("2004-06-02", "209549.0"), ("2019-01-02", "-154927.0"), ("2024-02-14", "-360685.0"), ("2025-02-12", "-400102.0"),
                                               ("2026-02-11", "-417299.0"), ("2026-08-12", "-466101.0"), ("2026-09-30", "-502585.0"), ("2026-10-07", "-483558.0")]),
    "C03": ("B1100NCBD", "ALL NSA line 38", [("2024-02-14", "343961.0"), ("2025-02-12", "448972.0"), ("2026-02-11", "392281.0"), ("2026-08-12", "331934.0"),
                                               ("2026-09-30", "353109.0"), ("2026-10-07", "353302.0")]),
    "C05": ("B1100NFRA", "FRI SA line 38 (context)", [("2026-10-07", "869123.5")]),
}


def chk(cid, desc, expected, observed, status):
    return [cid, desc, expected, observed, status]


def pin_mismatches(V, nm, pins):
    out = []
    for w, want in pins:
        got = V["vals"].get(nm, {}).get(w)
        if got is None or decimal.Decimal(got) != decimal.Decimal(want):
            out.append((w, got, want))
    return out


def pin_check(cid, vints, revs):
    nm, label, pins = PINS[cid]
    Vl = vints[-1]
    V0 = next((v for v in vints if v["key"] == PIN_VINTAGE), None)
    recent = [p for p in pins if (D_(latest_week_of(Vl["vals"])) - D_(p[0])).days <= 364]
    parts, status = [], "PASS"
    if V0 is not None:
        m0 = pin_mismatches(V0, nm, pins)
        parts.append("%d of %d pinned weeks match vintage %s exactly" % (len(pins) - len(m0), len(pins), PIN_VINTAGE))
        if m0:
            status = "FAIL"
            parts.append("first mismatch %s: got %s, pinned %s" % m0[0])
    else:
        parts.append("pin vintage %s is not cached" % PIN_VINTAGE)
    if Vl is not V0:
        ml = pin_mismatches(Vl, nm, pins)
        explained_rows = {(r[2], r[3]) for r in revs}
        expl = [m for m in ml if (nm, m[0]) in explained_rows]
        unexpl = [m for m in ml if (nm, m[0]) not in explained_rows]
        parts.append("latest vintage %s: %d match, %d differ (%d with a revisions.csv row, %d without; %d of the pins are recent, %d stable)"
                     % (Vl["key"], len(pins) - len(ml), len(ml), len(expl), len(unexpl), len(recent), len(pins) - len(recent)))
        if unexpl:
            status = "FAIL"
            parts.append("unexplained %s: got %s, pinned %s" % unexpl[0])
        elif expl and status == "PASS":
            status = "WARN"
    return chk(cid, "%s (%s) on the pinned weeks of spec section 8" % (label, nm), "%d pinned weeks equal the 16 Oct 2026 vintage" % len(pins), "; ".join(parts), status)


def route_compare(V, tolerance=None):
    """C10: DDP equals XML exactly on every common week for the four line-38 series. Returns (diff count, common weeks, packages used)."""
    n, common = 0, 0
    for label, _, grp, sa in DDP_PACKAGES:
        d = V["ddp"].get(label)
        if d is None:
            continue
        nm = sname("1100", SUFFIX[(grp, sa)])
        x = V["vals"][nm]
        for w in sorted(set(x) & set(d[nm])):
            common += 1
            a, b = decimal.Decimal(x[w]), decimal.Decimal(d[nm][w])
            same = (abs(a - b) <= 1) if M("g7_tol_1mn") else (a == b)
            if not same:
                n += 1
    return n, common


def c10_row(V):
    desc = "Routes: DDP equals XML on every common week for the four line-38 series"
    if V["route"] == "ddp_fallback":
        return chk("C10", desc, "exact equality", "xml_unavailable (this vintage is built from the DDP packages)", "WARN")
    if not V["ddp"]:
        return chk("C10", desc, "exact equality", "ddp_unavailable (no DDP package is cached for vintage %s)" % V["key"], "WARN")
    n, common = route_compare(V)
    if len(V["ddp"]) < len(DDP_PACKAGES):
        return chk("C10", desc, "exact equality", "ddp_unavailable (%d of %d packages cached; %d of %d common weeks differ)" % (len(V["ddp"]), len(DDP_PACKAGES), n, common),
                   "FAIL" if n else "WARN")
    return chk("C10", desc, "exact equality", "%d of %d common weeks differ (4 packages, vintage %s)" % (n, common, V["key"]), "FAIL" if n else "PASS")


def build_checks(c):
    vints, V, A, L = c["vints"], c["V"], c["A"], c["L"]
    revs, brk, union, stops = c["revs"], c["brk"], c["union"], c["stops"]
    out = []
    for cid in ("C01", "C02", "C03"):
        out.append(pin_check(cid, vints, revs))
    # C03 also: each equals DOM + FRI
    fri, dom, al = A[("FRI", "NSA")]["l38"], A[("DOM", "NSA")]["l38"], A[("ALL", "NSA")]["l38"]
    pin3 = [w for w, _ in PINS["C03"][2]]
    bad3 = [w for w in pin3 if w in al and abs(al[w] - (dom.get(w, 1e18) + fri.get(w, 1e18))) > TOL]
    if bad3:
        out[-1][3] += "; ALL != DOM + FRI on %s" % ", ".join(bad3)
        out[-1][4] = "FAIL"
    # C04
    ib, counts, mx = identity_breaches(A)
    wk = "2026-10-07"
    worked = ""
    if wk in A[("FRI", "NSA")]["l40"]:
        f, d_ = A[("FRI", "NSA")], A[("DOM", "NSA")]
        worked = "; %s vintage %s: FRI %s - (%s + %s + %s) = %s; DOM %s - (%s + %s + %s) = %s" % (
            wk, V["key"], fnum(f["l40"][wk], 0), fnum(f["l34"][wk], 0), fnum(f["l37"][wk], 0), fnum(f["l39"][wk], 0), fnum(f["l40"][wk] - f["l34"][wk] - f["l37"][wk] - f["l39"][wk], 1),
            fnum(d_["l40"][wk], 0), fnum(d_["l34"][wk], 0), fnum(d_["l37"][wk], 0), fnum(d_["l39"][wk], 0), fnum(d_["l40"][wk] - d_["l34"][wk] - d_["l37"][wk] - d_["l39"][wk], 1))
    out.append(chk("C04", "Sign identity: line 38 = line 40 - (34 + 37 + 39) on every week, each group and basis (tolerance 0.5 usd_mn)", "0 breaches",
                   "%d breaches over %s weeks (FRI NSA, DOM NSA, ALL NSA, FRI SA); largest gap %s%s" % (
                       len(ib), "/".join(str(counts.get(k, 0)) for k in GROUPS_SA), fnum(mx, 1), worked), "FAIL" if ib else "PASS"))
    # C07, C07w
    b = c["bind"]
    out.append(chk("C07", "Binding by identity (R3-6): ALL = DOM + FRI on every week; DOM line 40 exceeds FRI line 40 on every week", "no breach",
                   "%d group-identity breaches, %d dominance breaches, %d own-identity breaches; minimum DOM/FRI line-40 ratio %s" % (
                       len(b["group"]), len(b["dominance_bad"]), len(b["identity"]), fnum(b["minratio"], 2) if b["minratio"] else "n/a"),
                   "FAIL" if b["fails"] else "PASS"))
    out.append(chk("C07w", "A negative FRI NSA level on any week from %s is a WARN, listed by week (R3-6)" % NEG_FROM, "none expected",
                   ("negative on %d week(s): %s" % (len(b["neg"]), ", ".join(b["neg"][:10]))) if b["neg"] else "none", "WARN" if b["neg"] else "PASS"))
    out.append(pin_check("C05", vints, revs))
    # C08
    probs = []
    for nm in WANTED:
        ws = sorted(V["vals"][nm])
        if not ws:
            probs.append("%s has no weeks" % nm)
            continue
        if any(not is_wed(w) for w in ws):
            probs.append("%s has a non-Wednesday row" % nm)
        if len(weeks_between(ws[0], ws[-1])) != len(ws):
            probs.append("%s has a gap" % nm)
    fri38 = V["vals"][sname("1100", "FRD")]
    if fri38 and min(fri38) != FRI_FIRST_WEEK or fri38.get(FRI_FIRST_WEEK) != "1498.3":
        probs.append("FRI first week/value is %s %s, expected %s 1498.3" % (min(fri38) if fri38 else "-", fri38.get(min(fri38)) if fri38 else "-", FRI_FIRST_WEEK))
    for nm in (sname("1100", "DMD"), sname("1100", "CBD")):
        if V["vals"][nm] and min(V["vals"][nm]) != FIRST_WEEK:
            probs.append("%s starts %s, expected %s" % (nm, min(V["vals"][nm]), FIRST_WEEK))
    if len(fri38) < 2806:
        probs.append("FRI rows %d < 2806" % len(fri38))
    ends = {latest_week_of({sname("1100", "FRD"): V["vals"][nm]}) for nm in LINE38}
    if len(ends) != 1:
        probs.append("the four line-38 series end on different weeks: %s" % ", ".join(sorted(ends)))
    nona = {nm: V["attrs"][nm].get("NONA") for nm in LINE38 if V["attrs"][nm].get("NONA") not in ("0", None)}
    if nona:
        probs.append("observations whose status is not A: %s" % nona)
    out.append(chk("C08", "Coverage: FRI from 1973-01-03 (1,498.3); DOM and ALL from 2004-06-02; Wednesdays only; no gaps; FRI rows >= 2806; status A on the line-38 series",
                   "no problem", ("; ".join(probs[:4])) if probs else "FRI %d weekly rows %s to %s; DOM %s; ALL %s; all 20 series gap-free Wednesdays" % (
                       len(fri38), min(fri38), max(fri38), min(V["vals"][sname("1100", "DMD")]), min(V["vals"][sname("1100", "CBD")])), "FAIL" if probs else "PASS"))
    # C09
    if V["route"] == "ddp_fallback":
        out.append(chk("C09", "XML metadata: the attributes of 2.1; CL_CATEGORY L = Liabilities; CL_ITEM 1100 = (38) Net due to related foreign offices", "XML route", "N/A ddp_fallback", "N/A"))
    else:
        bad = []
        for nm in WANTED:
            try:
                assert_attrs(nm, V["attrs"][nm])
            except ContentError as e:
                bad.append(str(e))
        if V["codes"]["cat"].get("L") != "Liabilities":
            bad.append("CL_CATEGORY L is %r" % V["codes"]["cat"].get("L"))
        if V["codes"]["item"].get("1100") != ITEM_NAMES["1100"]:
            bad.append("CL_ITEM 1100 is %r" % V["codes"]["item"].get("1100"))
        out.append(chk("C09", "XML metadata: the attributes of 2.1 on all 20 series; CL_CATEGORY L = Liabilities; CL_ITEM 1100 = (38) Net due to related foreign offices",
                       "as listed", ("; ".join(bad[:3])) if bad else "20 series carry BG, SA, CATEGORY=L, ITEM, FREQ=19, UNIT_MULT=1000000; L = Liabilities; 1100 = %s" % ITEM_NAMES["1100"],
                       "FAIL" if bad else "PASS"))
    # C10
    out.append(c10_row(V))
    # C11
    nrows = c["notes"]
    probs, extra = [], []
    for grp, pins in NOTE_PINS.items():
        have = {(r["week"], r["amount"], r["para"]) for r in nrows if r["group"] == grp and r["kind"] == "note"}
        for w, amt, pi in pins:
            if (w, amt, pi) not in have:
                probs.append("%s %s %s (paragraph %d) not found" % (grp, w, fnum(amt, 1), pi))
        pinned = {(w, amt, pi) for w, amt, pi in pins}
        extra += ["%s %s %s" % (grp, w, fnum(a, 1)) for w, a, pi in sorted(have - pinned)]
    if not any(r["kind"] == "footnote" and r["week"] == FOOTNOTE20_WEEK and r["group"] == "FRI" for r in nrows):
        probs.append("footnote 20 (%s) is missing" % FOOTNOTE20_WEEK)
    status = "FAIL" if probs else ("WARN" if extra or stops.get("notes") else "PASS")
    obs = ("; ".join(probs[:3])) if probs else "5 FRI notes (31 Mar 2010 -12000.0 from paragraph index 1), 7 DOM notes, footnote 20 at %s" % FOOTNOTE20_WEEK
    if extra:
        obs += "; NEW note(s) naming the line, a new break for the supervisor: " + ", ".join(extra)
    if stops.get("notes") and not probs:
        obs += "; the notes page is the newest cached copy because STOP_notes is present"
    out.append(chk("C11", "Notes on Data: the five FRI notes and seven DOM notes with signed amounts (undated paragraphs kept, group per paragraph) and footnote 20", "as listed", obs, status))
    # C13
    qrows = c["qrows"]
    fr = [r for r in qrows if r[5] == "FRI"]
    frozen = [r for r in fr if r[11] == "yes"]
    ond = [r[0] for r in frozen if r[4] == "yes"]
    pr = []
    if len(frozen) != 31:
        pr.append("%d frozen quarters, expected 31" % len(frozen))
    if ond != list(ON_DATE_QUARTERS):
        pr.append("on_date quarters %s" % ",".join(ond))
    by = {r[0]: r for r in fr}
    q3 = by.get("2019Q3")
    if not q3 or not (q3[2] == "2019-10-02" and q3[3] == "2" and q3[10] == "yes" and q3[7] == ""):
        pr.append("2019Q3 is not W 2019-10-02 (+2) straddling with a blank delta_qe_wed")
    q1_22 = by.get("2022Q1")
    if not q1_22 or not (q1_22[2] == "2022-03-30" and q1_22[3] == "-1" and q1_22[10] == "yes" and q1_22[8] == ""):
        pr.append("2022Q1 is not W 2022-03-30 (-1) straddling with a blank delta_next")
    q3_26 = by.get("2026Q3")
    if not q3_26 or q3_26[2] != "2026-09-30" or q3_26[8] == "" or q3_26[11] != "yes" or addd(q3_26[2], 7) != "2026-10-07":
        pr.append("2026Q3 delta_next does not end 2026-10-07 inside the frozen set")
    out.append(chk("C13", "Quarter-end calendar: 31 frozen quarters; on_date exactly 2020-09-30, 2021-03-31, 2021-06-30, 2025-12-31, 2026-09-30; 2019Q3 and 2022Q1 straddle (their change across the break is left blank); 2026Q3 delta_next ends 2026-10-07",
                   "as listed", ("; ".join(pr)) if pr else "31 frozen quarters; on_date: %s; 2019Q3 W 2019-10-02 (+2) straddles, delta_qe_wed blank; 2022Q1 W 2022-03-30 (-1) delta_next ends 2022-04-06, blank, and straddles; 2026Q3 delta_next ends 2026-10-07" % ", ".join(ond),
                   "FAIL" if pr else "PASS"))
    # C14
    pr, mn = [], None
    named = sorted(set(Q2_ENDPOINTS) | set(Q1_WEDNESDAYS))
    for w in named:
        p = named_problems(w, union)
        if p:
            pr.append("%s: %s" % (w, p[0]))
        dd = qe_distance(w)
        mn = dd if mn is None else min(mn, dd)
    if set(endpoints(L, union)) != set(Q2_ENDPOINTS):
        pr.append("the endpoint list is not the four named Wednesdays")
    lo = lo_week(L, union)
    out.append(chk("C14", "Endpoints: each named Wednesday is a Wednesday, at least 7 days from every quarter-end day, not a break week, and the Wednesday of the 8th-14th of February or August",
                   "all of them", ("; ".join(pr[:3])) if pr else "%d named Wednesdays, nearest quarter-end day %s days away; Lo = %s (printed, not an endpoint)" % (len(named), mn, lo), "FAIL" if pr else "PASS"))
    # C17: the vintage ledger
    vp = index_problems([v["index"] for v in vints]) + vintage_problems(vints)
    out.append(chk("C17", "Vintage ledger: one zip hash per Prepared date; each vintage's latest week not earlier than the one before", "no problem",
                   "; ".join(vp[:2]) if vp else "%d vintage(s): %s" % (len(vints), ", ".join(v["key"] for v in vints)), "FAIL" if vp else "PASS"))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# allowlists, wording, leak guards, the STOP scan, the check.sh copy (G9, G10, G11, G12)
# ------------------------------------------------------------------------------------------------------------------------
def allowlist(name):
    cols = list(ALLOW[name])
    if M("g9_allow_drift") and name == "weekly.csv":
        cols[cols.index("usd_mn")] = "usd_mn_share"
    return cols


def allow_text():
    return "".join("%s:%s\n" % (n, ",".join(allowlist(n))) for n in ALLOW_ORDER)


def check_header(name, header):
    allow = allowlist(name)
    if M("g9_extra_col_ok"):
        ok = list(header[:len(allow)]) == allow
    elif M("g9_renamed_ok"):
        ok = len(header) == len(allow)
    else:
        ok = list(header) == allow
    if not ok:
        raise DataError("%s: header %r is not the exact column allowlist" % (name, list(header)))


def csv_body(text):
    """(header, rows) of a committed csv text, skipping every `# source:` line (mutant: the source line is read as the header)."""
    lines = text.splitlines()
    if not M("g9_source_as_header"):
        lines = [l for l in lines if not l.startswith("# source:")]
    rd = list(csv.reader(lines))
    return (rd[0], rd[1:]) if rd else ([], [])


def strip_exempt(text, readme=True):
    """Remove the one denial sentence (README only), once."""
    if not readme:
        return text
    if M("g11_denial_all"):
        return text.replace(DENIAL_SENTENCE, "")
    if M("g11_denial_loose"):
        return re.sub(r"[^.]*\bflows?\b[^.]*\.", "", text)
    return text.replace(DENIAL_SENTENCE, "", 1)


def wording_problems(name, text):
    t = strip_exempt(text, readme=name == "README.md")
    out = []
    if not M("g11_causal_off"):
        out += ["causal wording %r" % re.sub(r"\s+", " ", m.group(0).lower()) for m in CAUSAL_RX.finditer(t)]
    if not M("g11_extra_off"):
        out += ["flow or motive wording %r" % re.sub(r"\s+", " ", m.group(0).lower()) for m in EXTRA_RX.finditer(t)]
    return out


def guard_text(name, text):
    probs = wording_problems(name, text)
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
        if len(r) != len(header):
            raise DataError("%s: a row has %d cells, the header %d" % (name, len(r), len(header)))
        w.writerow(r)
    text = out.getvalue()
    if not text.startswith("# source:"):
        raise DataError("%s: the first line is not a `# source:` line" % name)
    guard_text(name, text)
    return text


def header_problems(files):
    out = []
    for n in ALLOW_ORDER:
        if n in files:
            try:
                check_header(n, csv_body(files[n])[0])
            except DataError as e:
                out.append(str(e))
    return out


def leak_problems(files):
    """files: {name: text or bytes}. Section 6: only the ten committed names; no raw zip, xml, page or PDF; no DDP package under any name; no local path; no at sign."""
    out = []
    for n in sorted(files):
        raw = files[n] if isinstance(files[n], bytes) else files[n].encode("utf-8")
        text = raw.decode("utf-8", errors="replace")
        if (n.lower().endswith(RAW_EXT) or raw[:2] == b"PK" or raw[:4] == b"%PDF") and not M("g10_zip_ok"):
            out.append("raw file in the committed folder: %s" % n)
        elif n not in COMMITTED and n != ".DS_Store" and not M("g9_eleventh_ok"):
            out.append("file that is not one of the ten committed names: %s" % n)
        first = next((l for l in text.splitlines() if not l.startswith("# source:")), "")
        if first.startswith('"Series Description"') and not M("g10_ddp_renamed_ok"):
            out.append("a DDP package under the name %s" % n)
        if not M("g10_path_ok") and (any(p in text for p in ("/Users/", "/private/", "~"))):
            out.append("a local path in %s" % n)
        if "@" in text:
            out.append("an at sign in %s" % n)
    for n in sorted(set(COMMITTED) - set(files)):
        out.append("missing: %s" % n)
    return out


Q3_STATS = ("level_qe_wed", "delta_qe_wed", "delta_next")


def across_quarter_problems(rows):
    """Q3 may hold single-quarter statistics only: no average, count, test or flag across quarters (R3-1)."""
    return ["Q3 row with statistic %r (%s)" % (r[3], r[1]) for r in rows if r[0] == "Q3" and r[3] not in Q3_STATS]


def all_folder_problems(files):
    out = leak_problems(files) + header_problems(files)
    if isinstance(files.get("summary.csv"), str):
        out += across_quarter_problems(csv_body(files["summary.csv"])[1])
    for n, t in files.items():
        if n.endswith((".csv", ".md")) and isinstance(t, str):
            out += ["%s: %s" % (n, p) for p in sorted(set(wording_problems(n, t)))]
    return out


REMOVERS = {"remove", "unlink", "rmtree", "rmdir"}
MUTATORS = {"replace", "rename", "move", "write_text", "write_bytes", "truncate", "copy", "copyfile", "copy2", "symlink", "link"}
LISTERS = {"glob", "iglob", "listdir", "walk", "scandir", "rglob", "iterdir"}


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


def stop_ast_problems(src):
    """G12 (R2-10): an AST scan. A STOP path may be reached only by create_stop, with open(path, "x"). Removal is allowed only in prune_old_zips, by exact
    names, in a function that lists nothing (a glob, a listing or a walk over the cache root is flagged)."""
    if M("g12_scan_off"):
        return []
    tree = ast.parse(src)
    problems = set()
    scopes = [(n.name, n) for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))] + [("<module>", tree)]
    for fname, scope in scopes:
        nodes = _scope_nodes(scope)
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
                if val is not None and _mentions_stop(val, tainted):
                    for t in tgt:
                        for x in ast.walk(t):
                            if isinstance(x, ast.Name):
                                tainted.add(x.id)
        calls = [n for n in nodes if isinstance(n, ast.Call)]
        listers = [n for n in calls if _fname(n) in LISTERS]
        for call in calls:
            nm = _fname(call)
            where = "%s line %d" % (fname, call.lineno)
            if fname == "create_stop" and nm in ("open", "fdopen") and _open_mode(call) != "x" and not M("g12_ignore_open"):
                problems.add("%s: create_stop opens a file in mode %r (only exclusive create, \"x\", is allowed)" % (where, _open_mode(call)))
            reach = any(_mentions_stop(a, tainted) for a in list(call.args) + [k.value for k in call.keywords]) or (
                isinstance(call.func, ast.Attribute) and _mentions_stop(call.func.value, tainted))
            if nm in REMOVERS:
                if fname != "prune_old_zips":
                    problems.add("%s: %s outside prune_old_zips" % (where, nm))
                elif listers and not M("g12_glob_ok"):
                    problems.add("%s: removal in a function that lists or globs a directory" % where)
                if reach:
                    problems.add("%s: %s reaches a STOP path" % (where, nm))
            elif nm in MUTATORS and reach and not (nm == "replace" and M("g12_replace_ok")):
                problems.add("%s: %s reaches a STOP path" % (where, nm))
            elif nm in ("open", "fdopen") and reach and not M("g12_ignore_open"):
                mode = _open_mode(call)
                if not (fname == "create_stop" and mode == "x") and (mode is None or any(ch in mode for ch in "wax+")):
                    problems.add("%s: open in mode %r reaches a STOP path" % (where, mode))
    return sorted(problems)


def checksh_problems(text):
    """G9 (R2-5): the M21 guard in bin/check.sh holds its own literal copy of the eight canonical lines and never reads them from this script."""
    out = []
    a = text.find("h8fo_leak_check() {")
    region = text[a:text.find("\n}\n", a) + 3] if a >= 0 else ""
    if a < 0:
        return ["bin/check.sh has no h8fo_leak_check function"]
    for l in SPEC_ALLOW_TEXT.splitlines():
        name, hdr = l.split(":", 1)
        if ("%s) want='%s'" % (name, hdr)) not in region:
            out.append("check.sh does not hold the literal header of %s" % name)
    if re.search(r"h8_foreign_offices\.py", region) and not M("g9_checksh_reads_script"):
        out.append("check.sh names the script inside the guard (it must not read the headers from it)")
    return out


# ------------------------------------------------------------------------------------------------------------------------
# compute and render
# ------------------------------------------------------------------------------------------------------------------------
CHECK_ORDER = ["C01", "C02", "C03", "C04", "C05", "C07", "C07w", "C08", "C09", "C10", "C11", "C13", "C14", "C15", "C16", "C17"]


def vintage_rows(vints):
    rows = []
    for v in vints:
        r = v["index"]
        rows.append([v["key"], v["route"], r["xml_prepared"], r["xml_last_modified"], r["xml_sha256"], ddp_status_of(v), latest_week_of(v["vals"]),
                     str(len(v["vals"][sname("1100", "FRD")]))])
    return rows


def notes_csv_rows(notes):
    return [[r["week"], r["group"], fnum(r["amount"], 1) if r["amount"] is not None else "", r["kind"], "" if r["para"] is None else str(r["para"]), r["head"]] for r in notes]


def compute(inp):
    vints = inp["vints"]
    V = vints[-1]
    A = assemble(V)
    L = latest_week_of(V["vals"])
    notes = inp["notes"]
    brk = {g: break_map(notes, g) for g in ("FRI", "DOM", "ALL")}
    union = set(brk["FRI"]) | set(brk["DOM"]) | set(brk["ALL"])
    weekly = weekly_rows(A, L, brk, V["key"])
    qrows = quarter_table(A, L, brk, V["key"])
    revs = revision_rows(vints, inp.get("existing_revisions"), inp.get("existing_weekly"))
    summ = q1_rows(A, L, brk) + q2_rows(A, L, brk, union) + q3_rows(qrows) + q4_rows(A, L, brk, union) + q6_rows(vints, revs)
    c = dict(inp=inp, vints=vints, V=V, A=A, L=L, notes=notes, brk=brk, union=union, weekly=weekly, qrows=qrows, revs=revs, summary=summ, stops=inp["stops"],
             bind=binding(A), vrows=vintage_rows(vints), fetch_rows=inp.get("fetch_rows", []), notes_date=inp.get("notes_date", ""))
    c["checks"] = sorted(build_checks(c), key=lambda r: CHECK_ORDER.index(r[0]))
    return c


def source_main(c):
    V = c["V"]
    rel = V["prepared"][:10] if V["route"] == "xml" else "date not stated on the DDP route"
    return ("# source: Board of Governors of the Federal Reserve System, H.8 release of %s (vintage %s, route %s), retrieved %s; derived by bin/h8_foreign_offices.py build; "
            "public domain, cite to the Board" % (rel, V["key"], V["route"], V["index"]["fetched_utc"][:10]))


def render_data_texts(c):
    V, src = c["V"], source_main(c)
    t = {}
    t["weekly.csv"] = render_csv("weekly.csv", c["weekly"], src)
    t["quarter_ends.csv"] = render_csv("quarter_ends.csv", c["qrows"], src)
    t["notes.csv"] = render_csv("notes.csv", notes_csv_rows(c["notes"]), "# source: Board of Governors of the Federal Reserve System, Notes on Data (%s%s) retrieved %s, and release footnote 20 of the H.8 release"
                                % (HOST, NOTES_PATH, c["notes_date"] or "(date not recorded)"))
    t["revisions.csv"] = render_csv("revisions.csv", c["revs"], "# source: cached 20-series subsets of H.8 vintages %s, compared pair by pair; regenerated on every build from the cache"
                                    % ", ".join(v["key"] for v in c["vints"]))
    t["vintages.csv"] = render_csv("vintages.csv", c["vrows"], "# source: the vintage index and 20-series subsets kept in the git-ignored cache; DDP package presence per vintage")
    t["summary.csv"] = render_csv("summary.csv", c["summary"], src)
    t["fetch_log.csv"] = render_csv("fetch_log.csv", c["fetch_rows"], fetch_source_line(c["fetch_rows"]))
    return t


def digests(texts):
    return {n: sha256_of(x.encode("utf-8")) for n, x in sorted(texts.items()) if n != "checks.csv"}


def finish(c):
    """Add C15 (a second render over the same cache leaves every file unchanged, revisions.csv included) and C16 (the folder guards run on the rendering)."""
    t1 = render_data_texts(c)
    t1["README.md"] = render_readme(c)
    t1["SOURCES.md"] = render_sources(c)
    c2 = compute(c["inp"])
    t2 = render_data_texts(c2)
    t2["README.md"] = render_readme(c2)
    t2["SOURCES.md"] = render_sources(c2)
    if M("x_render_unstable"):
        t2["weekly.csv"] += "x"
    same = digests(t1) == digests(t2)
    c["checks"] = c["checks"] + [chk("C15", "Fixed output: a second build over the same cache leaves every file's sha256 unchanged, revisions.csv included", "identical",
                                     "identical (%d files)" % len(digests(t1)) if same else "DIFFERENT", "PASS" if same else "FAIL")]
    src = source_main(c)
    t1["checks.csv"] = render_csv("checks.csv", c["checks"], "# source: checks of bin/h8_foreign_offices.py build, vintage %s" % c["V"]["key"])
    probs = all_folder_problems(t1)
    c["checks"] = sorted(c["checks"] + [chk("C16", "Folder guards on the rendering: ten names, exact headers, no raw file, no local path, no at sign, no banned wording (R5)",
                                            "no problem", "; ".join(probs[:3]) if probs else "no problem", "FAIL" if probs else "PASS")], key=lambda r: CHECK_ORDER.index(r[0]))
    t1["checks.csv"] = render_csv("checks.csv", c["checks"], "# source: checks of bin/h8_foreign_offices.py build, vintage %s" % c["V"]["key"])
    failed = [r[0] for r in c["checks"] if r[4] == "FAIL"]
    return t1, failed


# ------------------------------------------------------------------------------------------------------------------------
# README.md and SOURCES.md (generated, so the wording guards scan them)
# ------------------------------------------------------------------------------------------------------------------------
def md_table(head, rows, align=None):
    align = align or ["---"] * len(head)
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(align) + "|"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(out)


def money(v, nd=1):
    return "" if v is None else format(round(v, nd), ",.%df" % nd)


def bn(v):
    return "%s" % format(round(v / 1000.0, 1), ",.1f")


def render_readme(c):
    V, A, L, brk, union = c["V"], c["A"], c["L"], c["brk"], c["union"]
    fri, dom, al = lvl(A, "FRI"), lvl(A, "DOM"), lvl(A, "ALL")
    friT, domT, alT = lvl(A, "FRI", "l40"), lvl(A, "DOM", "l40"), lvl(A, "ALL", "l40")
    wk = "2026-10-07" if "2026-10-07" in fri else L
    f = A[("FRI", "NSA")]
    full = float_vals(V, sname("1100", "FRD"))
    negs = [w for w in sorted(full) if full[w] < 0]
    qrows = c["qrows"]
    fr = {r[0]: r for r in qrows if r[5] == "FRI"}
    dm = {r[0]: r for r in qrows if r[5] == "DOM"}
    eps = endpoints(L, union)
    lo = lo_week(L, union)
    rel = V["prepared"][:10] if V["route"] == "xml" else "not stated on the DDP route"
    o = []
    o.append("# Net due to related foreign offices, weekly: the Federal Reserve's H.8 release (\"Assets and Liabilities of Commercial Banks in the United States\")")
    o.append("")
    o.append(REQUIRED_OPEN)
    o.append("")
    o.append(REQUIRED_S3)
    o.append("")
    o.append("**Terms.** H.8 is the Federal Reserve Board's weekly statistical release on the balance sheets of commercial banks in the United States. Edge Act and agreement corporations "
             "are US subsidiaries chartered to do international banking. An IBF is an international banking facility; the H.8 treats IBFs as foreign offices. NSA means not seasonally "
             "adjusted: the raw weekly level, without the correction for regular seasonal patterns. The weekly figures are estimates. The Fed benchmarks them, that is re-bases them, to "
             "Call Reports, the quarterly balance-sheet reports that banks file with US regulators, and re-estimates them when new Call Report data arrive. In the tables, `usd_mn` is "
             "millions of US dollars, `FRI` is the foreign-related institutions of the opening sentence (US branches and agencies of foreign banks with Edge Act and agreement "
             "corporations), `DOM` is domestically chartered commercial banks and `ALL` is all commercial banks in the United States. A vintage is the data as published on one release date; "
             "the Board overwrites its files at each release, so each vintage is kept in a local git-ignored cache when it is fetched.")
    o.append("")
    o.append("## The sign, and the trap")
    o.append("")
    lastneg = negs[-1] if negs else None
    o.append("Positive means the US offices owe their related foreign offices, net. Negative means they are owed, net. **The line for domestically chartered banks is negative (%s $bn on %s, "
             "vintage %s) and is not the foreign banks' line.** Read the `FRI` rows for the foreign banks. The foreign-related line was itself negative on %d weeks of its history from %s, %s, "
             "so the sign alone does not tell a reader which group a number belongs to. The groups are told apart by the series group code (which the script asserts on every series) and by domestic line 40 being larger than foreign-related line 40 on every week; the accounting identity below holds for both groups and does not tell them apart." % (
                 bn(dom[wk]), wk, V["key"], len(negs), FRI_FIRST_WEEK, ("the last on %s" % lastneg) if lastneg else "none after the first week"))
    o.append("")
    o.append("The Board's footnote 24 says: \"%s\" The line is the balance-sheet residual of the liabilities side: line 38 = line 40 (total liabilities) - (line 34 deposits + line 37 borrowings + "
             "line 39 other liabilities). Worked example, foreign-related institutions, NSA, %s (vintage %s, usd_mn): %s - (%s + %s + %s) = %s. Domestically chartered banks on the same "
             "date: %s - (%s + %s + %s) = %s." % (
                 FOOTNOTE24, wk, V["key"], money(f["l40"][wk], 0), money(f["l34"][wk], 0), money(f["l37"][wk], 0), money(f["l39"][wk], 0), money(fri[wk], 0), money(A[("DOM", "NSA")]["l40"][wk], 0),
                 money(A[("DOM", "NSA")]["l34"][wk], 0), money(A[("DOM", "NSA")]["l37"][wk], 0), money(A[("DOM", "NSA")]["l39"][wk], 0), money(dom[wk], 0)))
    o.append("")
    o.append("## What the line contains")
    o.append("")
    o.append("On the reporting form FR 2644 (item 9.a, page LI-7 of the April 2024 instructions) a branch or agency reports one net position against its own foreign offices, its Edge and "
             "agreement subsidiaries, its IBFs, its own head office and other related depository institutions in the US. The instructions say the position should include \"unremitted "
             "profits, any statutory or regulatory capital requirement, any reserve accounts, and any allowance for credit losses\". A net due-from position is reported as an asset (item 5.a), and "
             "the H.8 carries it into line 38 as a negative. **Line 38 is therefore not pure lending between offices.** From 6 April 2022 the allowance for credit losses of foreign-related "
             "institutions is inside the line (release footnote 20); its size is not published. " + DENIAL_SENTENCE)
    o.append("")
    o.append("## Breaks")
    o.append("")
    def blist(g):
        return ", ".join(sorted(brk[g])) if brk[g] else "none"
    o.append("The paths are split at every published break: 6 April 2022 (allowances moved into the line) and each week of the Board's Notes on Data that names the line. Break weeks since "
             "2004-06-02, FRI: %s. DOM: %s. ALL takes the union of both. `segment_start` in `weekly.csv` is the first week of each row's segment; the change that ends on a break week is "
             "left blank and `note_flag` marks the week. No change, minimum or maximum is taken across a break. `notes.csv` lists the stated amounts (signed, usd_mn), group by group." % (
                 blist("FRI"), blist("DOM")))
    o.append("")
    o.append("## Endpoints of the multi-year changes")
    o.append("")
    o.append("Multi-year changes run between named ordinary Wednesdays: the Wednesday between the 8th and the 14th of February or August, each at least 39 days from any quarter-end day. "
             "The endpoints are %s. The reason: the weeks around quarter-ends swing, so an endpoint on such a week would put a quarter-end move into a multi-year change. `Lo`, the latest "
             "Wednesday at least 7 days from every quarter-end day and not a break week, is %s; it is printed in `summary.csv` and never used as an endpoint." % (", ".join(eps), lo))
    o.append("")
    o.append("## Quarter-ends")
    o.append("")
    five = [(q, fr[q], dm[q]) for q in ON_DATE_QUARTERS if q in fr]
    o.append("Only quarter-end days that are themselves Wednesdays count as observations; since 2019 there are five. Each is one row, in usd_mn: the level at that Wednesday close, the change "
             "ending that Wednesday and the change ending the next Wednesday. No average, count or test is taken across them.")
    o.append("")
    rows = []
    for q, a, b in five:
        rows.append([q, a[1], money(float(a[6])), money(float(a[7])), money(float(a[8])) if a[8] else "", money(float(b[6])), money(float(b[7])), money(float(b[8])) if b[8] else ""])
    o.append(md_table(["quarter", "quarter-end day", "FRI level", "FRI change into", "FRI change out of", "DOM level", "DOM change into", "DOM change out of"], rows,
                      ["---", "---", "---:", "---:", "---:", "---:", "---:", "---:"]))
    o.append("")
    o.append(CAVEAT_SENTENCE + ". When the quarter-end day falls before the Wednesday (a negative offset in `quarter_ends.csv`), the day sits in the change that ends one week after "
             "that Wednesday, so the table below gives both changes and marks which one contains the quarter-end day. Two quarters, 2019Q3 and 2022Q1, have a change that ends on a break week.")
    o.append("")
    rows = []
    for q in fr:
        a, b = fr[q], dm[q]
        if a[4] == "yes" or a[11] != "yes":
            continue
        def pair(r):
            inw, oth = (r[7], r[8]) if r[9] == "yes" else (r[8], r[7])
            return [money(float(inw)) if inw else "", money(float(oth)) if oth else "", r[10]]
        rows.append([q, a[1], a[2], a[3]] + pair(a) + pair(b))
    o.append("The other frozen-set quarters (2019Q1 to 2026Q3), usd_mn: the change that contains the quarter-end day, the other change beside it, and whether either ends on a break week.")
    o.append("")
    o.append(md_table(["quarter", "quarter-end day", "Wednesday", "offset", "FRI containing", "FRI other", "FRI break", "DOM containing", "DOM other", "DOM break"], rows,
                      ["---", "---", "---", "---:", "---:", "---:", "---", "---:", "---:", "---"]))
    o.append("")
    o.append("A blank cell is a change that ends on a break week: it spans the break (2 October 2019 for 2019Q3, 6 April 2022 for 2022Q1), so no change is shown; the `break` column says yes for that quarter.")
    o.append("")
    o.append("## Latest levels")
    o.append("")
    o.append("Latest week %s, vintage %s (usd_mn; the share is line 38 as a percentage of the same group's line 40, total liabilities, on the same Wednesday)." % (L, V["key"]))
    o.append("")
    o.append(md_table(["group", "line 38", "line 40", "share of line 40 (%)"], [[g, money(d[L]), money(t[L]), fnum(100.0 * d[L] / t[L], 2)] for g, d, t in (("FRI", fri, friT), ("DOM", dom, domT), ("ALL", al, alT))],
                      ["---", "---:", "---:", "---:"]))
    o.append("")
    o.append("Changes between the named Wednesdays (usd_mn; the share is the change as a percentage of the group's line 40 on the starting Wednesday):")
    o.append("")
    rows = []
    for g, d, t in (("FRI", fri, friT), ("DOM", dom, domT), ("ALL", al, alT)):
        for s, e in q2_windows(eps):
            if crosses_break(s, e, brk[g]):
                rows.append([g, "%s to %s" % (s, e), "crosses a break", "", "", "", ""])
                continue
            st = window_stats(d, t, s, e)
            if st:
                rows.append([g, "%s to %s" % (s, e), money(d[s]), money(d[e]), money(st["change"]), fnum(st["pct"], 2), "%s (%s) to %s (%s)" % (money(st["vmn"]), st["mn"], money(st["vmx"]), st["mx"])])
    o.append(md_table(["group", "window", "start", "end", "change", "share of start line 40 (%)", "minimum to maximum inside the window"], rows, ["---", "---", "---:", "---:", "---:", "---:", "---"]))
    o.append("")
    o.append("## Seasonal adjustment, revisions and vintages")
    o.append("")
    sa = A[("FRI", "SA")]["l38"]
    o.append("Every table here uses the not seasonally adjusted weekly level (NSA), because seasonal adjustment would remove part of any pattern around quarter-ends, and because the Board's "
             "About page says the seasonally adjusted foreign-related data are \"%s\" from other groups. The seasonally adjusted foreign-related line (%s usd_mn on %s, against %s NSA) is "
             "in `weekly.csv` as context so that a reader can match Table 10 of the release; no figure in `summary.csv` or `quarter_ends.csv` is taken from it." % (
                 SA_NOTE, money(sa[L]), L, money(fri[L])))
    o.append("")
    ex = "2026-08-05"
    v0 = next((v for v in c["vints"] if v["key"] == PIN_VINTAGE), None)
    exs = ""
    if v0 is not None and ex in v0["vals"][sname("1100", "FRD")]:
        later = (", and vintage %s has %s" % (V["key"], money(fri[ex], 0) if ex in fri else "no value")) if V["key"] != PIN_VINTAGE else ""
        exs = (" For example, a project note records $834.4 bn for the week of 5 Aug 2026 from the 14 Aug 2026 release (taken from that note, not re-read at the source); vintage %s has %s usd_mn%s."
               % (PIN_VINTAGE, money(float(v0["vals"][sname("1100", "FRD")][ex]), 0), later))
    o.append("The weekly figures use weights carried forward from the latest Call Reports. When new Call Report data arrive the weights are updated, which the Fed calls benchmarking, and the "
             "change is interpolated over the previous quarter; seasonal factors are updated once a year and affect only the seasonally adjusted series." + exs + " Each fetch saves the 20-series "
             "subset of its vintage in a git-ignored cache, and `revisions.csv` is regenerated on every build from all adjacent pairs of cached subsets (vintages so far: %s; `vintages.csv` "
             "lists them with the zip hash). The release XML file is the primary source. If it cannot be fetched, the build can run from the Board's Data Download Program (DDP) "
             "packages instead, the route is then `ddp_fallback`, and the vintage is keyed by the fetch date." % ", ".join(v["key"] for v in c["vints"]))
    o.append("")
    o.append("## Column dictionary")
    o.append("")
    dic = [("weekly.csv", "`week_wed` Wednesday; `group` FRI, DOM or ALL; `sa` NSA or SA (SA only for FRI); `series_id` H.8 identifier; `usd_mn` line 38; `change_usd_mn` level minus the "
                          "previous Wednesday's level, blank on a break week; `total_liabilities_usd_mn` line 40; `pct_of_total_liabilities` 100 x line 38 / line 40; `qe_quarter`, `qe_role` "
                          "(`qe` on the Wednesday nearest the quarter-end day, `after_qe` one week later, else `none`) and `qe_offset_days` (Wednesday minus quarter-end day); `segment_start` "
                          "first week of the segment; `note_flag` `note`, `footnote` or both on a break week; `vintage`."),
           ("quarter_ends.csv", "`quarter`, `qe_date` quarter-end day, `qe_wed` Wednesday nearest it, `offset_days`, `on_date` yes when the quarter-end day is the Wednesday; `group` FRI or DOM (NSA); "
                                "`level_qe_wed_usd_mn`; `delta_qe_wed_usd_mn` change ending that Wednesday; `delta_next_usd_mn` change ending the next one; `qe_day_in_window` yes when the quarter-end "
                                "day falls in the first of the two changes; `straddles_break` yes when either change ends on that group's break week, and that change is then left blank; `frozen_set` yes for the 31 quarters 2019Q1 to 2026Q3; "
                                "`blind` yes when the spec author had not seen the values; `vintage`."),
           ("notes.csv", "`note_week`, `group`, `line38_effect_usd_mn` the Board's stated amount, `kind` note or footnote, `paragraph_index` (0 is the first paragraph of the entry), `text_head` the item clause "
                         "that carries the amount."),
           ("revisions.csv", "Cells whose value differs between two adjacent cached vintages: `vintage_prev`, `vintage_new`, `series_id`, `week_wed`, the two values and the change, all usd_mn."),
           ("vintages.csv", "One row per cached vintage: `route` xml or ddp_fallback; the XML `Prepared` timestamp, `Last-Modified` time and zip sha256; `ddp_status` ok, ddp_partial or ddp_unavailable; "
                            "`latest_week`; `rows_fri_nsa`."),
           ("summary.csv", "`question` is the block label (Q1 paths by segment, Q2 changes between the named Wednesdays and `Lo`, Q3 the five Wednesday quarter-ends, Q4 the FRI and DOM changes "
                           "side by side with the ALL = DOM + FRI gap, Q6 revisions); `window`, `group`, `statistic`, `value`, `unit`, and `blind` (yes when the values had not been seen when "
                           "the build was specified)."),
           ("checks.csv", "`check_id`, `description`, `expected`, `observed`, `status` PASS, WARN, FAIL or N/A."),
           ("fetch_log.csv", "One row per request the script made: time, host, path, status, bytes, sha256.")]
    o.append(md_table(["file", "columns"], [[n, d] for n, d in dic]))
    o.append("")
    o.append("## Provenance")
    o.append("")
    o.append("Source: Board of Governors of the Federal Reserve System, \"Assets and Liabilities of Commercial Banks in the United States - H.8\" (https://www.federalreserve.gov/releases/h8/), release of %s "
             "(vintage %s). The Board's website policy says: \"Unless otherwise indicated, information on Board's website is in the public domain and may be copied and distributed without "
             "permission. Please cite to the Board as the source of the information.\" The Board has announced that its Data Download Program is being retired, with the \"Build Your Package\" "
             "feature to be removed in the week of 9 November 2026; the XML files on the release pages remain. Method, sources and the choices made in building this folder are in "
             "[SOURCES.md](SOURCES.md)." % (rel, V["key"]))
    return "\n".join(o) + "\n"


# ---- SOURCES.md -----------------------------------------------------------------------------------------------------------
DECISIONS = [
    "Seeding. The cache was seeded with the spec author's raw copies of the 16 Oct 2026 vintage (zip sha256 2ce2d425...222b and the four DDP weekly packages, hashes checked first), as the spec allows. "
    "They were put through the same ingest code as a fetch (`ingest_xml`), and the vintage is keyed 2026-10-16. Those requests were made by the spec author on 23 Oct 2026 and are not in `fetch_log.csv`.",
    "Changes that end on a break week. The spec defines `change_usd_mn` as the level minus the previous Wednesday's level, says no change is ever taken across a segment boundary (R3-3), and C13 "
    "words 2019Q3 and 2022Q1 as straddling. The supervisor ruled that R3-3 outranks C13's wording: the change ending on a break week is left blank in `weekly.csv` (with `note_flag`) and, in "
    "`quarter_ends.csv`, FRI 2019Q3 `delta_qe_wed` (ends on the 2 Oct 2019 note week) and FRI 2022Q1 `delta_next` (ends on 6 Apr 2022) are blank, with `straddles_break` = yes kept.",
    "Notes before the ledger. The page also names the line for domestically chartered banks on 21 Apr 2004; that week is before the first ledger week (2004-06-02) and is left out of `notes.csv`, "
    "so the seven DOM notes are the ones of spec 2.2.",
    "`text_head` in `notes.csv` is the item clause of the Board's paragraph that carries the amount (\"net due to related foreign offices\" and the signed amount), not the start of the paragraph: "
    "the Board's opening and reason clauses use words that the wording guard (R5) bans in this folder.",
    "Group of a note paragraph: whichever of the three group phrases (foreign-related institutions, domestically chartered commercial banks, all commercial banks) comes first in the paragraph. "
    "A paragraph that names the line and no group stops the build.",
    "Pins. Mismatches of a pinned week are WARN only when `revisions.csv` has a row for that series and week in some pair of cached vintages; a mismatch without such a row is FAIL, for recent and "
    "stable weeks alike. On the pin vintage 2026-10-16 every mismatch is FAIL. The 52-week rule only decides the label recent or stable in the text of the check.",
    "Q1 covers FRI and DOM, as the spec's closing sentence says (\"the same for DOM\"); the opening parenthesis also mentions ALL, and no ALL rows were added.",
    "Q6 is computed per group (FRI, DOM, ALL) over the NSA line-38 series, and a week counts as old when it is more than 26 weeks before the newer vintage's latest week.",
    "Q3 rows in `summary.csv` repeat the five Wednesday quarter-ends of `quarter_ends.csv`, one row per statistic; no statistic is taken across quarters.",
    "C15 compares two renderings made in one run; the on-disk comparison is a second `build` run, which leaves every sha256 unchanged. C16 and C17 are extra checks (folder guards on the rendering; "
    "the vintage ledger). The retired checks C06 and C12 are not rows.",
    "The STOP scan (G12) allows one creator, `create_stop`, which opens the file with mode \"x\" (exclusive create) because a latch has to be created; it flags every other call that reaches a STOP "
    "path, every removal outside `prune_old_zips`, and a removal in a function that lists or globs a directory.",
    "Stop rules at build: no cached vintage, or STOP_xml together with STOP_ddp, or STOP_xml present with a newest vintage that is not a DDP fallback, ends the build with exit 2 and no file written.",
    "The README defines H.8 in its title line and glosses the other terms in a \"Terms\" paragraph after the two required opening sentences and sentence 3, because those sentences are fixed text "
    "that already use H.8 and Edge Act.",
    "The mutant for \"lines 35 + 36 added to 34\" adds line 34 a second time, because lines 35 and 36 are not among the 20 series and are already inside line 34.",
    "A vintage is ordered by the date in its key (an XML vintage before a DDP fallback vintage of the same date). A cell that is in an older vintage and missing from the next is listed in `revisions.csv` with blank new value and change.",
    "`fetch` makes no request at all, and exits 2, when STOP_xml and STOP_ddp are both present at the start (no route is left; the notes page is not fetched either). With STOP_xml alone it goes on with the DDP and the notes page. "
    "It exits 0 when the XML vintage was saved or a DDP fallback vintage was made, and 2 otherwise; a socket fault exits 4 and latches nothing.",
    "The reader accepts a gzip-encoded reply (the request asks for identity encoding) so that a server that compresses anyway does not trip a content test.",
    "Lo is computed against the union of the break weeks of FRI, DOM and ALL. The Q2 and Q4 windows test a break against the group's own break weeks. Q4 prints, per window, the FRI and DOM changes and the gap ALL change - DOM change - FRI change.",
    "The XML content test asserts BG, SA, CATEGORY, ITEM, FREQ and UNIT_MULT on each of the 20 series (spec 2.1 and R3b); it does not assert the series descriptions, which only the DDP test reads (spec 3.2).",
    "First fetch by this script: 23 Oct 2026, 13:16:31 to 13:16:47 UTC, six requests (the XML zip, the four DDP packages, the notes page), all HTTP 200, no STOP file. The zip has the same sha256 as the seeded copy (Prepared 2026-10-16T10:00:00), so no new vintage was made, `revisions.csv` holds no row and the vintage stays 2026-10-16. The next H.8 release was due at 4:15 p.m. Eastern (20:15 UTC) that day, after this fetch; a later `fetch` brings the 23 Oct vintage.",
    "DDP hash slip in the spec: the spec quotes the hash of the ALL package as 6bbba727 ... a8559. The seeded and the fetched file are byte-identical and both are 6bbba7279a4bc51c...ad8559, so the first eight characters agree and the tail differs by one character; this is read as a typing slip in the spec, and C10 shows the package equals the XML on all 7,946 common weeks of the 16 Oct vintage.",
    "Post-registration fix after the first build on real data (23 Oct 2026): `text_head` in `notes.csv` changed from a window of up to 120 characters ending at the amount (starting after the first clause boundary) to the item clause only. One reason: the window cut some clauses in the middle (an unbalanced parenthesis, a leading \"and\"). No amount, group, week or paragraph index changed. The old values were not kept on disk; they were rebuilt by running the old rule on the cached notes page and agree with the first build's printed output. All 12 old and new values:\n  - 2019-10-02 FRI paragraph 0: old \"borrowings, -$1.6 billion; net due to related foreign offices, -$3.0 billion\"; new \"net due to related foreign offices, -$3.0 billion\"\n  - 2018-04-04 DOM paragraph 0: old \"deposits, other deposits, $45.5 billion; borrowings, -$1.6 billion; net due to related foreign offices, $2.0 billion\"; new \"net due to related foreign offices, $2.0 billion\"\n  - 2017-11-29 FRI paragraph 0: old \"borrowings, $23.3 billion (borrowings from others, $23.3 billion); net due to related foreign offices, $5.2 billion\"; new \"net due to related foreign offices, $5.2 billion\"\n  - 2016-03-02 DOM paragraph 0: old \"borrowings, $4.5 billion (borrowings from others, $4.1 billion); net due to related foreign offices, -$3.1 billion\"; new \"net due to related foreign offices, -$3.1 billion\"\n  - 2011-01-05 DOM paragraph 0: old \"borrowings, $3.0 billion (borrowings from others, $3.0 billion); net due to related foreign offices, $5.7 billion\"; new \"net due to related foreign offices, $5.7 billion\"\n  - 2010-03-31 FRI paragraph 1: old \"borrowings, $21.0 billion (borrowings from others, $21.0 billion); net due to related foreign offices, -$12.0 billion\"; new \"net due to related foreign offices, -$12.0 billion\"\n  - 2008-08-20 DOM paragraph 0: old \"The major liability items affected were the following: net due to related foreign offices, -$8.6 billion\"; new \"net due to related foreign offices, -$8.6 billion\"\n  - 2008-04-02 FRI paragraph 0: old \"and net due to related foreign offices, -$18.6 billion\"; new \"net due to related foreign offices, -$18.6 billion\"\n  - 2008-02-06 FRI paragraph 0: old \"The major liability item affected was the following: net due to related foreign offices, $12.0 billion\"; new \"net due to related foreign offices, $12.0 billion\"\n  - 2007-03-07 DOM paragraph 0: old \"borrowings from others, -$0.7 billion); net due to related foreign offices, -$3.2 billion\"; new \"net due to related foreign offices, -$3.2 billion\"\n  - 2006-10-04 DOM paragraph 0: old \"borrowings, $21.5 billion (borrowings from others, $21.5 billion); net due to related foreign offices, -$10.0 billion\"; new \"net due to related foreign offices, -$10.0 billion\"\n  - 2004-12-29 DOM paragraph 0: old \"The major liability item affected was the following: net due to related foreign offices, $2.0 billion\"; new \"net due to related foreign offices, $2.0 billion\"",
    "In the identity check the tolerance is 0.5 usd_mn on every table. FRI seasonally adjusted values carry half-units, and 1,089 of its weeks show a rounding gap of 0.1 or 0.2 usd_mn; the NSA tables show none.",
]


def render_sources(c):
    V, vints = c["V"], c["vints"]
    o = ["# Sources", "", "## Federal Reserve Board, H.8 release: XML file (primary source)", ""]
    o.append("- URL: `https://%s%s`, fetched by `bin/h8_foreign_offices.py fetch`. The zip holds `H8_data.xml` (SDMX-ML compact), `H8_struct.xml` and two schema files; the script streams "
             "`H8_data.xml` with `iterparse` and never reads it with a regular expression. Vintages so far, with the time each was retrieved (UTC) and the XML `Prepared` timestamp: %s." % (
                 HOST, XML_PATH, "; ".join("%s (%s, retrieved %s%s)" % (v["key"], v["route"], v["index"]["fetched_utc"], (", prepared " + v["prepared"]) if v["prepared"] else "") for v in vints)))
    o.append("- Series: matched on the whole `SERIES_NAME`, never on a substring or a column position (`NFRD` is weekly NSA, `NFRDM` monthly NSA, `NFRA` weekly SA). The script asserts, for each of "
             "the 20 series: `BG`, `SA`, `CATEGORY` = `L`, `ITEM`, `FREQ` = `19`, `UNIT_MULT` = `1000000`. `CL_CATEGORY` L is \"Liabilities\" and `CL_ITEM` 1100 is \"%s\"." % ITEM_NAMES["1100"])
    rows = []
    for nm, w in WANTED.items():
        rows.append(["`%s`" % nm, w["group"], w["sa"], w["bg"], w["item"], ITEM_NAMES[w["item"]]])
    o.append("")
    o.append(md_table(["series", "group", "basis", "BG", "ITEM", "line"], rows))
    o.append("")
    o.append("- Units: millions of US dollars (`UNIT_MULT` 1000000; DDP `Multiplier:` 1000000). Weekly levels are Wednesday close-of-business values.")
    o.append("- Breaks and notes: footnote 20 of the release (\"%s\") and footnote 24 (\"%s\"). The Board's About page says the seasonally adjusted foreign-related data \"%s\" from other groups." % (
        FOOTNOTE20, FOOTNOTE24, SA_NOTE))
    o.append("- Licence: the Board's website policy (https://www.federalreserve.gov/disclaimer.htm, read by hand on 23 Oct 2026): \"Unless otherwise indicated, information on Board's website is in the "
             "public domain and may be copied and distributed without permission. Please cite to the Board as the source of the information.\" Derived tables are committed with that citation; raw "
             "files stay in the git-ignored cache for size.")
    o += ["", "## Data Download Program (DDP) packages: cross-check and fallback", ""]
    o.append("- URL pattern: `https://%s/datadownload/Output.aspx?rel=H8&series=<package>&lastobs=&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package`; packages %s." % (
        HOST, ", ".join("%s `%s`" % (l, p) for l, p, _, _ in DDP_PACKAGES)))
    o.append("- The script selects on the `Unique Identifier:` row (`H8/H8/<series>`) and asserts that the series description names the group and the basis and that `Multiplier:` is 1000000. "
             "The Board's Data Download Program is being retired (notice of 16 Jul 2026; the \"Build Your Package\" feature is to go in the week of 9 Nov 2026); a package that fails leaves the "
             "XML route untouched, and C10 is then WARN.")
    o += ["", "## Notes on Data", ""]
    o.append("- URL: `https://%s%s`, newest cached copy retrieved %s. The leading index of dates is not an entry; an undated paragraph belongs to the dated entry before it; the group is read per paragraph." % (
        HOST, NOTES_PATH, c.get("notes_date") or "(not recorded)"))
    o.append("")
    o.append("Quoted clauses that carry the amounts (the Board's text, in the stated paragraph):")
    o.append("")
    for r in c["notes"]:
        if r["kind"] == "note":
            o.append("- %s, %s, paragraph %d: \"%s\" (%s usd_mn)" % (r["week"], r["group"], r["para"], r["head"], fnum(r["amount"], 1)))
    o += ["", "## Other pages read by hand (not fetched by the script)", ""]
    o.append("- Read on 23 Oct 2026 between 12:02 and 12:10 UTC by the spec author with the CLAUDE.md User-Agent and one request per URL (16 requests, all HTTP 200), under `https://%s`: "
             "`/releases/h8/current/default.htm` (current release, footnotes 1, 20 and 24), `/releases/h8/about.htm`, `/releases/h8/h8_technical_qa.html`, `/releases/h8/default.htm`, "
             "`/datadownload/Choose.aspx?rel=H8`, `/data/data-download-fred-information.htm` (the DDP notice), `/disclaimer.htm` (the website policy), `/apps/reportingforms/Report/Index/FR_2644` "
             "and the FR 2644 instructions PDF (`/apps/reportingforms/Download/DownloadAttachment?guid=386cbedb-80c8-4cce-a618-a7f3e943b747`, footer \"April 2024\", item 9.a on page LI-7)." % HOST)
    o.append("- FR 2644 instructions, item 9.a: the positions reported \"should include unremitted profits, any statutory or regulatory capital requirement, any reserve accounts, and any allowance for "
             "credit losses\"; a net due-from position is reported in item 5.a and a net due-to position in item 9.a.")
    o += ["", "## Builder decisions", ""]
    for d in DECISIONS + list(c["inp"].get("decisions_extra", [])):
        o.append("- " + d)
    return "\n".join(o) + "\n"


# ------------------------------------------------------------------------------------------------------------------------
# build
# ------------------------------------------------------------------------------------------------------------------------
def read_decisions_extra(cache):
    p = os.path.join(cache, "decisions_extra.txt")
    if not os.path.exists(p):
        return []
    return [l.strip() for l in read_file(p, "r").splitlines() if l.strip()]


def load_inputs(cache, out_dir, stop_dir):
    vints = load_vintages(cache)
    stops = stop_state(stop_dir)
    state, why = route_state(vints, stops)
    if state != "ok":
        raise DataError(why)
    p, nd = newest_notes(cache)
    if p is None:
        raise DataError("no cached Notes on Data page; run fetch first")
    ents, _ = parse_notes_entries(read_file(p, "r"))
    notes = notes_rows(ents)
    _, fr = read_csv_rows(os.path.join(out_dir, "fetch_log.csv"))
    return dict(vints=vints, stops=stops, notes=notes, notes_date=nd, fetch_rows=fr, decisions_extra=read_decisions_extra(cache))


def write_outputs(texts, out_dir, failed):
    target = os.path.join(out_dir, "_FAILED") if failed and not M("x_failed_to_committed") else out_dir
    for n, x in texts.items():
        if n == "fetch_log.csv" and target == out_dir and os.path.exists(os.path.join(out_dir, n)):
            continue                                              # the request log is written by fetch and only read here
        write_text(os.path.join(target, n), x)
    return target


def run_build(a):
    t0 = time.time()
    stop_dir = getattr(a, "stop_dir", STOP_DIR)
    cache = check_cache(a.cache, out_dir=a.out)
    try:
        inp = load_inputs(cache, a.out, stop_dir)
    except DataError as e:
        print("STOP (data): %s" % e, file=sys.stderr)
        return 2
    c = compute(inp)
    texts, failed = finish(c)
    target = write_outputs(texts, a.out, failed)
    V, A, L = c["V"], c["A"], c["L"]
    fri, dom, al = lvl(A, "FRI"), lvl(A, "DOM"), lvl(A, "ALL")
    print("vintage %s (%s); latest week %s; %d vintage(s) cached; %d notes rows" % (V["key"], V["route"], L, len(c["vints"]), len(c["notes"])))
    print("== headline, usd_mn, NSA, week %s: FRI %s, DOM %s, ALL %s" % (L, fnum(fri[L], 1), fnum(dom[L], 1), fnum(al[L], 1)))
    print("== checks")
    for r in c["checks"]:
        print("   %-5s %-5s %s" % (r[0], r[4], r[3][:200]))
    print("failed: %s; wrote %d files to %s (%.1f s)" % (", ".join(failed) or "none", len(texts), tilde(target), time.time() - t0))
    return 1 if failed else 0


# ------------------------------------------------------------------------------------------------------------------------
# selftest: synthetic data only. Every guard G1-G17 of the spec's section 7 has a test; each mutant (a deliberately broken variant, switched on in this
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

    def quiet(self, name, fn):
        try:
            fn()
        except Exception as e:
            self.ok(name, False, "raised %s: %s" % (type(e).__name__, e))
        else:
            self.ok(name, True)

    def failed(self):
        return [(n, d) for n, c, d in self.items if not c]


class FakeClock:
    def __init__(self, t=1_000_000.0):
        self.t = t

    def wall(self):
        return self.t

    def sleep(self, s):
        self.t += s


ITEM_OF = dict(LINES)


def make_vint(key, vals, route="xml", ddp=None, fetched="2026-10-23T12:05:34Z", prepared=None):
    prepared = (key + "T10:00:00") if prepared is None and route == "xml" else (prepared or "")
    attrs = {nm: dict(BG=w["bg"], SA=w["sa"], CATEGORY="L", ITEM=w["item"], FREQ="19", UNIT_MULT=UNIT_MULT_OK, SRC="xml" if route == "xml" else "ddp", NONA="0")
             for nm, w in WANTED.items()}
    return dict(key=key, route=route, prepared=prepared, last_modified="", attrs=attrs, codes={"cat": {"L": "Liabilities"}, "item": {"1100": ITEM_NAMES["1100"]}},
                vals=vals, index=dict(vintage=key, route=route, xml_prepared=prepared, xml_last_modified="", xml_sha256=("a" * 64) if route == "xml" else "", fetched_utc=fetched),
                ddp=ddp or {})


def put(vals, grp, sa, line, w, v):
    vals[sname(ITEM_OF[line], SUFFIX[(grp, sa)])][w] = v if isinstance(v, str) else "%.1f" % v


def tiny_vals(n=6, start="2026-08-26", fri=None, dom=None):
    """Six weeks of all 20 series with the identities exact. FRI and DOM line 38 can be set; ALL = DOM + FRI; FRI SA = FRI NSA + 30,000.5."""
    weeks = [addd(start, 7 * i) for i in range(n)]
    fri = fri or [800000.0 + 1000 * i for i in range(n)]
    dom = dom or [-480000.0 - 500 * i for i in range(n)]
    comp = {"FRI": (1600000.0, 980000.0, 210000.0), "DOM": (18100000.0, 1370000.0, 880000.0)}
    vals = {nm: {} for nm in WANTED}
    for i, w in enumerate(weeks):
        t = {}
        for g, v in (("FRI", fri[i]), ("DOM", dom[i])):
            c34, c37, c39 = comp[g]
            t[g] = dict(l38=v, l40=v + c34 + c37 + c39, l34=c34, l37=c37, l39=c39)
        t["ALL"] = {k: t["FRI"][k] + t["DOM"][k] for k in t["FRI"]}
        sa = dict(t["FRI"])
        sa["l38"] = fri[i] + 30000.5
        sa["l40"] = sa["l38"] + comp["FRI"][0] + comp["FRI"][1] + comp["FRI"][2]
        for g, b, d in (("FRI", "NSA", t["FRI"]), ("DOM", "NSA", t["DOM"]), ("ALL", "NSA", t["ALL"]), ("FRI", "SA", sa)):
            for line in LINE_KEYS:
                put(vals, g, b, line, w, d[line])
    return vals


def synth_world(last="2026-10-07", seed=11):
    """The full-length synthetic vintage: FRI weekly from 1973-01-03, DOM and ALL from 2004-06-02, the pinned weeks of section 8 set exactly."""
    rng = random.Random(seed)
    pins = {nm: dict(pl) for _, (nm, _, pl) in PINS.items()}
    vals = {nm: {} for nm in WANTED}
    weeks = weeks_between(FRI_FIRST_WEEK, last)
    i2012 = weeks.index("2012-01-04")
    for i, w in enumerate(weeks):
        base = -120000.0 + rng.gauss(0, 20000) if i < i2012 else 150000.0 + 330.0 * (i - i2012) + rng.gauss(0, 15000)
        f38 = "1498.3" if w == FRI_FIRST_WEEK else pins["B1100NFRD"].get(w, "%.1f" % round(base))
        comp = {"FRI": [1600000.0 + rng.randint(-90000, 90000), 980000.0 + rng.randint(-60000, 60000), 210000.0 + rng.randint(-20000, 20000)],
                "DOM": [18100000.0 + rng.randint(-300000, 300000), 1370000.0 + rng.randint(-80000, 80000), 880000.0 + rng.randint(-40000, 40000)]}
        comp = {g: [float(round(x)) for x in c] for g, c in comp.items()}
        sa38 = pins["B1100NFRA"].get(w) or "%.1f" % (float(f38) + 20000.5 + rng.randint(-3000, 3000))
        put(vals, "FRI", "NSA", "l38", w, f38)
        put(vals, "FRI", "SA", "l38", w, sa38)
        for line, x in zip(("l34", "l37", "l39"), comp["FRI"]):
            put(vals, "FRI", "NSA", line, w, x)
            put(vals, "FRI", "SA", line, w, x)
        put(vals, "FRI", "NSA", "l40", w, float(f38) + sum(comp["FRI"]))
        put(vals, "FRI", "SA", "l40", w, float(sa38) + sum(comp["FRI"]))
        if w >= FIRST_WEEK:
            d38 = pins["B1100NDMD"].get(w) or "%.1f" % round(-150000.0 - 250.0 * (i - i2012) + rng.gauss(0, 20000))
            put(vals, "DOM", "NSA", "l38", w, d38)
            for line, x in zip(("l34", "l37", "l39"), comp["DOM"]):
                put(vals, "DOM", "NSA", line, w, x)
            put(vals, "DOM", "NSA", "l40", w, float(d38) + sum(comp["DOM"]))
            put(vals, "ALL", "NSA", "l38", w, float(f38) + float(d38))
            for line, x in zip(("l34", "l37", "l39"), range(3)):
                put(vals, "ALL", "NSA", line, w, comp["FRI"][x] + comp["DOM"][x])
            put(vals, "ALL", "NSA", "l40", w, float(f38) + sum(comp["FRI"]) + float(d38) + sum(comp["DOM"]))
    return vals


def world_ddp(vals):
    return {label: {nm: dict(vals[nm]) for nm in pkg_names(g, s)} for label, _, g, s in DDP_PACKAGES}


NOTE_FR = lambda amt: "Foreign-related institutions acquired $4.0 billion in assets and liabilities of nonbank institutions. The major liability items affected were the following: deposits, $0.5 billion; net due to related foreign offices, %s billion; and other liabilities, $1.0 billion." % amt
NOTE_DM = lambda amt: "Domestically chartered commercial banks acquired $5.0 billion in assets and liabilities of nonbank institutions. The major liability items affected were the following: borrowings, $1.0 billion; net due to related foreign offices, %s billion." % amt
NOTE_NONE = "Domestically chartered commercial banks acquired $9.0 billion in assets and liabilities of nonbank institutions. The major liability items affected were deposits, $9.0 billion."
NOTE_REASON_FR = lambda amt: ("Because of the deconsolidation of some variable interest entities, the assets and liabilities of foreign-related institutions decreased $20.0 billion. "
                              "The major liability items affected were the following: borrowings, -$1.0 billion; net due to related foreign offices, %s billion." % amt)
NOTE_REASON_DM = lambda amt: ("Because of the conversion of a thrift institution to a commercial bank, the assets and liabilities of domestically chartered commercial banks "
                              "increased $9.0 billion. The major liability items affected were the following: net due to related foreign offices, %s billion." % amt)


def notes_html(extra_entries=()):
    """A page in the Board's layout: an index run of dates, then <div class="datanote"> entries. The entries mimic the twelve in-sample notes, one
    pre-sample note (21 Apr 2004), the 31 Mar 2010 entry with its undated second paragraph and the 6 Feb 2008 entry with a Foreign paragraph followed by DOM paragraphs."""
    fr, dm, none, reason_fr, reason_dm = NOTE_FR, NOTE_DM, NOTE_NONE, NOTE_REASON_FR, NOTE_REASON_DM
    E = [("20191002", [fr("-$3.0")]), ("20180404", [dm("$2.0")]), ("20171129", [fr("$5.2")]), ("20160302", [reason_dm("-$3.1")]), ("20110105", [reason_dm("$5.7")]),
         ("20100331", [none, reason_fr("-$12.0")]), ("20080820", [dm("-$8.6")]), ("20080402", [reason_fr("-$18.6")]), ("20080206", [reason_fr("$12.0"), none, none]),
         ("20070307", [dm("-$3.2")]), ("20061004", [dm("-$10.0")]), ("20041229", [dm("$2.0")]), ("20040421", [none, dm("-$1.1")]), ("20200108", [none])] + list(extra_entries)
    index = "".join('<a href="#notes_%s">%s<a/><br>' % (d, d) for d, _ in E)
    body = "".join('<div class="datanote">\n<center><h3><a name="notes_%s">%s</a></h3></center>%s\n</div>' % (d, d, "".join("<p>%s</p>" % p for p in ps)) for d, ps in E)
    return "<html><head><title>Notes on Data</title></head><body><a title=\"Notes on Data\" href=\"/releases/h8/h8notes.htm\">Notes on Data</a>\n%s\n%s</body></html>" % (index, body)


def small_xml_zip(vals, prepared="2026-10-16T10:00:00", edits=None, decoys=True, struct=True):
    edits = edits or {}
    NS = ('xmlns:message="http://www.SDMX.org/resources/SDMXML/schemas/v1_0/message" xmlns:common="http://www.SDMX.org/resources/SDMXML/schemas/v1_0/common" '
          'xmlns:frb="http://www.federalreserve.gov/structure/compact/common" xmlns:kf="http://www.federalreserve.gov/structure/compact/H8_H8"')
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<message:MessageGroup %s>\n<message:Header><message:ID>H8</message:ID><message:Prepared>%s</message:Prepared></message:Header>\n'
           '<frb:DataSet id="H8">' % (NS, prepared)]

    def ser(nm, attrs, obs):
        a = " ".join('%s="%s"' % (k, v) for k, v in sorted(attrs.items()))
        return '<kf:Series %s SERIES_NAME="%s"><frb:Annotations/>%s</kf:Series>' % (
            a, nm, "".join('<frb:Obs OBS_STATUS="A" OBS_VALUE="%s" TIME_PERIOD="%s" />' % (v, w) for w, v in sorted(obs.items())))
    for nm, w in WANTED.items():
        if nm == "B1100NFRD" and decoys:
            out.append(ser("B1100NFRDM", dict(BG="FR", SA="NSA", CATEGORY="L", ITEM="1100", FREQ="129", UNIT_MULT=UNIT_MULT_OK), {"2026-08-01": "111.0", "2026-09-01": "222.0"}))
            out.append(ser("B1001NCBA", dict(BG="CB", SA="SA", CATEGORY="A", ITEM="1001", FREQ="19", UNIT_MULT=UNIT_MULT_OK), {"2026-08-26": "5.0"}))
        attrs = dict(BG=w["bg"], SA=w["sa"], CATEGORY="L", ITEM=w["item"], FREQ="19", UNIT_MULT=UNIT_MULT_OK, CURRENCY="USD", UNIT="Currency")
        attrs.update(edits.get(nm, {}))
        out.append(ser(nm, attrs, vals[nm]))
        if nm == "B1100NFRD" and decoys:
            pass
    out.append("</frb:DataSet></message:MessageGroup>")
    st = ('<message:Structure xmlns:message="http://www.SDMX.org/resources/SDMXML/schemas/v1_0/message" xmlns:structure="http://www.SDMX.org/resources/SDMXML/schemas/v1_0/structure"><message:CodeLists>'
          '<structure:CodeList id="CL_CATEGORY" agency="FRB"><structure:Name>Balance sheet category</structure:Name><structure:Code value="A"><structure:Description>Assets</structure:Description></structure:Code>'
          '<structure:Code value="L"><structure:Description>Liabilities</structure:Description></structure:Code></structure:CodeList>'
          '<structure:CodeList id="CL_ITEM" agency="FRB">%s</structure:CodeList></message:CodeLists></message:Structure>'
          % "".join('<structure:Code value="%s"><structure:Description>%s</structure:Description></structure:Code>' % (k, v) for k, v in ITEM_NAMES.items()))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("H8_data.xml", "\n".join(out))
        if struct:
            zf.writestr("H8_struct.xml", st)
        zf.writestr("H8_H8.xsd", "<xs/>")
    return buf.getvalue()


def ddp_csv(grp, sa, vals, order=None, mult="1000000", group_text=None):
    names = pkg_names(grp, sa)
    cols = order or names
    weeks = sorted({w for nm in names for w in vals[nm]})
    descs = ["%s, %s, %s" % (ITEM_NAMES[WANTED[n]["item"]].split(") ", 1)[1], GROUP_PHRASE[grp] if group_text is None else group_text, BASIS_PHRASE[sa]) for n in cols]
    rows = [["Series Description"] + descs, ["Unit:"] + ["Currency"] * len(cols), ["Multiplier:"] + [mult] * len(cols), ["Currency:"] + ["USD"] * len(cols),
            ["Unique Identifier:"] + ["H8/H8/" + n for n in cols], ["Time Period"] + cols]
    for w in weeks:
        rows.append([w] + [vals[n].get(w, "") for n in cols])
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\r\n").writerows(rows)
    return buf.getvalue().encode("utf-8")


_WORLD = {}


def get_world():
    """The synthetic world, built once with no mutant active: the 2026-10-07 vintage (all four DDP packages equal), a longer one to 2027-04-14, the notes and the clean outputs."""
    if not _WORLD:
        if _ACTIVE:
            raise RuntimeError("the synthetic world must be built before any mutant is switched on")
        vals = synth_world()
        V = make_vint(PIN_VINTAGE, vals, ddp=world_ddp(vals))
        ents, _ = parse_notes_entries(notes_html())
        notes = notes_rows(ents)
        inp = dict(vints=[V], stops={"xml": False, "ddp": False, "notes": False}, notes=notes, notes_date="2026-10-23", fetch_rows=[], decisions_extra=[])
        c0 = compute(inp)
        texts, failed = finish(dict(c0))
        v2 = synth_world(last="2027-04-14")
        V2 = make_vint("2027-04-16", v2)
        _WORLD.update(vals=vals, V=V, inp=inp, c0=c0, texts=texts, failed=failed, notes=notes, V2=V2, A2=assemble(V2), brk=c0["brk"], union=c0["union"])
    return _WORLD


def world_files():
    return dict(get_world()["texts"])


def fake_rig(tmp, handler, stop_dir=None, clock=None, **kw):
    clock = clock or FakeClock()
    calls = []

    def opener(host, target, headers, timeout, cap):
        calls.append((host, target, dict(headers), clock.wall()))
        return handler(host, target, headers)
    fe = Fetcher(os.path.join(tmp, "cache"), os.path.join(tmp, "out"), stop_dir=stop_dir or os.path.join(tmp, "stop"), opener=opener, wall=clock.wall, mono=clock.wall,
                 sleeper=clock.sleep, now_utc=lambda: dt.datetime(2026, 10, 23, 12, 0, tzinfo=dt.timezone.utc), **kw)
    return fe, calls, clock


def fetch_handler(vals, xml=200, ddp=200, notes=200, xml_body=None, location=None):
    pid_to = {pid: (g, s) for _, pid, g, s in DDP_PACKAGES}

    def h(host, target, headers):
        if target == XML_PATH:
            if xml != 200:
                return xml, b"server said no", ({"location": location} if location else {"retry-after": "30"})
            return 200, xml_body or small_xml_zip(vals), {"last-modified": "Fri, 16 Oct 2026 20:15:04 GMT"}
        if target == NOTES_PATH:
            return (200, notes_html().encode("utf-8"), {}) if notes == 200 else (notes, b"no", {})
        for pid, (g, s) in pid_to.items():
            if pid in target:
                return (200, ddp_csv(g, s, vals), {}) if ddp == 200 else (ddp, b"<html>not found</html>", {})
        return 404, b"", {}
    return h


def tiny_V(key=PIN_VINTAGE, **kw):
    return make_vint(key, tiny_vals(**kw))


def tiny_A(**kw):
    return assemble(tiny_V(**kw))


def silent(fn):
    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
        return fn()


def t_g1(ck):
    A = tiny_A()
    ck.eq("clean fixture: no identity, group or dominance failure", binding(A)["fails"], [])
    b = binding(tiny_A(fri=[800000.0, 810000.0, -5000.0, 820000.0, 830000.0, 840000.0]))
    ck.eq("a negative FRI level is not a FAIL (R3-6)", b["fails"], [])
    ck.ok("...it is one WARN that names the week", len(b["warns"]) == 1 and "2026-09-09" in b["warns"][0], str(b["warns"]))
    sw = dict(A)
    sw[("FRI", "NSA")], sw[("DOM", "NSA")] = dict(A[("FRI", "NSA")]), dict(A[("DOM", "NSA")])
    sw[("FRI", "NSA")]["l38"], sw[("DOM", "NSA")]["l38"] = A[("DOM", "NSA")]["l38"], A[("FRI", "NSA")]["l38"]
    ck.ok("the per-group identity reports line-38 columns swapped with labels kept", bool(binding(sw)["identity"]))
    both = dict(A)
    both[("FRI", "NSA")], both[("DOM", "NSA")] = A[("DOM", "NSA")], A[("FRI", "NSA")]
    bb = binding(both)
    ck.ok("DOM line 40 > FRI line 40 reports whole groups swapped (every column), which the identities cannot see", bool(bb["dominance_bad"]) and not bb["identity"] and not bb["group"])
    good = dict(BG="DM", SA="NSA", CATEGORY="L", ITEM="1100", FREQ="19", UNIT_MULT=UNIT_MULT_OK)
    ck.quiet("a DM series with BG=DM passes the attribute test", lambda: assert_attrs("B1100NDMD", good))
    ck.raises("B1100NFRD labelled BG=DM is refused", ContentError, lambda: assert_attrs("B1100NFRD", dict(good)))
    vals = tiny_vals()
    names = pkg_names("FRI", "NSA")
    got = parse_ddp(ddp_csv("FRI", "NSA", vals, order=list(reversed(names))), "FRI", "NSA")
    ck.ok("DDP columns are selected by identifier, whatever their position", all(got[n] == vals[n] for n in names), "values moved to the wrong series")
    ck.raises("a DDP description naming another group is refused", ContentError, lambda: parse_ddp(ddp_csv("FRI", "NSA", vals, group_text="all commercial banks"), "FRI", "NSA"))


def t_g2(ck):
    ib, counts, mx = identity_breaches(tiny_A())
    ck.eq("line 38 = line 40 - (34 + 37 + 39) on the clean fixture, all four tables", ib, [])
    ck.eq("six weeks checked in each of the four tables", sorted(counts.values()), [6, 6, 6, 6])
    v = tiny_vals()
    v["B1100NFRD"]["2026-09-09"] = "%.1f" % (float(v["B1100NFRD"]["2026-09-09"]) + 1.0)
    ib, _, _ = identity_breaches(assemble(make_V(v)))
    ck.eq("a one-week breach of 1 usd_mn is reported, once", [(k, w) for k, w, g in ib], [(("FRI", "NSA"), "2026-09-09")])
    v["B1100NFRD"]["2026-09-09"] = "%.1f" % (float(tiny_vals()["B1100NFRD"]["2026-09-09"]) + 0.3)
    ck.eq("a gap of 0.3 is inside the 0.5 tolerance", identity_breaches(assemble(make_V(v)))[0], [])
    vals = tiny_vals()
    ck.raises("CATEGORY A (the asset side) on a line-38 series is refused", ContentError, lambda: test_xml_zip(small_xml_zip(vals, edits={"B1100NFRD": {"CATEGORY": "A"}})))
    ck.quiet("the clean zip passes the content test", lambda: test_xml_zip(small_xml_zip(vals)))


def make_V(vals, key=PIN_VINTAGE, **kw):
    return make_vint(key, vals, **kw)


def t_g3(ck):
    A = tiny_A()
    ck.eq("ALL = DOM + FRI (NSA) on the clean fixture", group_breaches(A), [])
    v = tiny_vals()
    v["B1100NCBD"]["2026-09-02"] = "%.1f" % (float(v["B1100NCBD"]["2026-09-02"]) + 2.0)
    ck.eq("ALL off by 2 usd_mn is reported", [w for w, g in group_breaches(assemble(make_V(v)))], ["2026-09-02"])
    ck.eq("no 'FRI <= ALL' limit is applied: DOM is negative, so FRI exceeds ALL and binding has no FAIL", binding(A)["fails"], [])


def t_g4(ck):
    vals = tiny_vals()
    r = test_xml_zip(small_xml_zip(vals))
    ser = r["series"]
    ck.eq("the weekly NSA series is selected by its whole identifier (the monthly decoy comes first in the file)", {w: v for w, (v, s) in ser["B1100NFRD"]["obs"].items()}, vals["B1100NFRD"])
    ck.ok("the monthly and other-line decoys are not selected", "B1100NFRDM" not in ser and "B1001NCBA" not in ser, str(sorted(ser)))
    A = assemble(make_V(vals))
    ck.eq("statistics read the NSA table for FRI", lvl(A, "FRI")["2026-09-02"], float(vals["B1100NFRD"]["2026-09-02"]))
    ck.ok("...which differs from the SA table in the fixture", A[("FRI", "SA")]["l38"]["2026-09-02"] != lvl(A, "FRI")["2026-09-02"])


def t_g5(ck):
    ck.eq("UNIT_MULT 1,000,000 keeps the published digits", usd_mn_str("836860.0", 1000000), "836860.0")
    ck.eq("a value in thousands is divided by 1,000 into usd_mn", float(usd_mn_str("5000.0", 1000)), 5.0)
    ck.eq("a value in billions is multiplied by 1,000 into usd_mn", float(usd_mn_str("5.0", 1000000000)), 5000.0)
    ck.raises("UNIT_MULT 1000 on a series is refused by the content test", ContentError, lambda: test_xml_zip(small_xml_zip(tiny_vals(), edits={"B1100NFRD": {"UNIT_MULT": "1000"}})))
    ck.raises("a DDP Multiplier of 1000 is refused", ContentError, lambda: parse_ddp(ddp_csv("FRI", "NSA", tiny_vals(), mult="1000"), "FRI", "NSA"))
    r = test_xml_zip(small_xml_zip(tiny_vals()))
    vals, _ = xml_to_vals(r)
    ck.eq("the XML route stores usd_mn as published", vals["B1100NFRD"]["2026-08-26"], "800000.0")
    A = tiny_A()
    rows = weekly_rows(A, "2026-09-30", {"FRI": {}, "DOM": {}, "ALL": {}}, "k")
    x = next(x for x in rows if x[0] == "2026-08-26" and x[1] == "FRI" and x[2] == "NSA")
    ck.eq("weekly.csv writes line 38 in usd_mn, not billions", x[4], "800000.0")


def t_g6(ck):
    W = get_world()
    A, L = W["c0"]["A"], W["c0"]["L"]
    q = quarter_table(A, L, W["brk"], "k")
    fri = [r for r in q if r[5] == "FRI"]
    ck.eq("31 frozen quarters, 2019Q1 to 2026Q3", sum(1 for r in fri if r[11] == "yes"), 31)
    ck.eq("on_date = yes for exactly the five Wednesday quarter-ends", [r[1] for r in fri if r[4] == "yes"], ["2020-09-30", "2021-03-31", "2021-06-30", "2025-12-31", "2026-09-30"])
    for D, want, off in ((dt.date(2026, 6, 30), "2026-07-01", 1), (dt.date(2026, 12, 31), "2026-12-30", -1), (dt.date(2024, 3, 31), "2024-04-03", 3)):
        w, o = qe_wed(D)
        ck.eq("W(%s) is %s at offset %+d" % (D, want, off), (w.isoformat(), o), (want, off))
    m = qe_week_map("2026-10-07")
    ck.eq("W(q) is marked qe", m.get("2026-09-30"), ("2026Q3", "qe", 0))
    ck.eq("W(q)+7 is after_qe, never qe", m.get("2026-10-07"), ("2026Q3", "after_qe", 0))
    r26 = next(r for r in fri if r[0] == "2026Q2")
    ck.eq("2026-06-30 (a Tuesday): not on date, offset +1, the day is in the first change", (r26[4], r26[3], r26[9]), ("no", "1", "yes"))
    r22 = next(r for r in fri if r[0] == "2022Q1")
    ck.eq("2022-03-31 (a Thursday): offset -1, the day is in the NEXT change", (r22[3], r22[9]), ("-1", "no"))
    s3 = q3_rows(q)
    ck.eq("the summary holds no statistic across quarters", across_quarter_problems(s3), [])
    ck.eq("five Wednesday quarter-ends x FRI and DOM x three statistics", len(s3), 30)
    q2 = quarter_table(W["A2"], "2027-04-14", W["brk"], "k")
    r27 = [r for r in q2 if r[0] == "2027Q1"]
    r26q4 = [r for r in q2 if r[0] == "2026Q4"]
    ck.ok("2026Q4 is in the table (data run to 2027-04-14) but not in the frozen set", len(r26q4) == 2 and all(r[11] == "no" for r in r26q4) and not is_frozen(2026, 4), str([r[11] for r in r26q4]))
    ck.ok("a quarter after 2026Q3 is appended with frozen_set = no", len(r27) == 2 and all(r[11] == "no" for r in r27), str([r[11] for r in r27]))
    ck.ok("...and 2027-03-31, a Wednesday, is on date", all(r[4] == "yes" for r in r27) and len(r27) == 2)


def t_g7(ck):
    vals = tiny_vals()
    V = make_V(vals, ddp=world_ddp(vals))
    ck.eq("DDP equals XML on the clean fixture: 0 differences in 24 common weeks", route_compare(V), (0, 24))
    d2 = world_ddp(vals)
    d2["fri_nsa"]["B1100NFRD"]["2026-09-09"] = "%.1f" % (float(vals["B1100NFRD"]["2026-09-09"]) + 1.0)
    ck.eq("a 1 usd_mn difference between XML and DDP is a difference", route_compare(make_V(vals, ddp=d2))[0], 1)
    ck.eq("C10 is FAIL on that difference", c10_row(make_V(vals, ddp=d2))[4], "FAIL")
    ck.eq("C10 is PASS on the clean fixture", c10_row(V)[4], "PASS")
    r = c10_row(make_V(vals))
    ck.ok("C10 is WARN ddp_unavailable when no package is cached", r[4] == "WARN" and "ddp_unavailable" in r[3], str(r))
    ck.eq("a DDP latch alone does not stop a build whose XML is fine", route_state([V], {"xml": False, "ddp": True, "notes": False})[0], "ok")
    ck.eq("STOP_xml with STOP_ddp: no route is left", route_state([V], {"xml": True, "ddp": True, "notes": False})[0], "exit2")
    ck.eq("no cached vintage: no route", route_state([], {"xml": False, "ddp": False, "notes": False})[0], "exit2")
    fb = make_V(vals, key="fetch-2026-10-23", route="ddp_fallback")
    ck.eq("an XML latch with a fallback vintage as the newest one builds", route_state([fb], {"xml": True, "ddp": False, "notes": False})[0], "ok")
    ck.ok("C10 is WARN xml_unavailable on a fallback vintage", "xml_unavailable" in c10_row(fb)[3] and c10_row(fb)[4] == "WARN")
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = fake_rig(tmp, fetch_handler(vals, xml=500))
        res = do_fetch(fe, say=lambda *a: None)
        stop = os.path.join(tmp, "stop", "STOP_xml")
        ck.ok("an XML 500 writes STOP_xml", os.path.exists(stop))
        lines = read_file(stop, "r").splitlines() if os.path.exists(stop) else []
        ck.eq("STOP_xml holds status, utc_time, url_path, retry_after, body_head", [l.split(":")[0] for l in lines], ["status", "utc_time", "url_path", "retry_after", "body_head"])
        ck.eq("...with the status 500", lines[0] if lines else "", "status: 500")
        ck.eq("the four DDP packages then make a fallback vintage keyed by the fetch date", (res["route"], res["key"], res["fallback"]), ("ddp_fallback", "fetch-2026-10-23", True))
        ck.eq("six requests were made: XML, four packages, notes", len(calls), 6)
        vs = load_vintages(fe.cache)
        sd = os.path.join(tmp, "stop")
        ck.eq("the fallback vintage loads from the cache", [v["route"] for v in vs], ["ddp_fallback"])
        ck.eq("the build falls back to the DDP", route_state(vs, stop_state(sd))[0], "ok")
        create_stop(os.path.join(sd, "STOP_ddp"), "status: 404\nutc_time: x\nurl_path: /x\nretry_after: \nbody_head: x\n")
        ck.eq("with STOP_ddp as well, no route is left", route_state(vs, stop_state(sd))[0], "exit2")
        out = os.path.join(tmp, "out2")
        code = silent(lambda: run_build(types.SimpleNamespace(cache=fe.cache, out=out, stop_dir=sd)))
        ck.eq("both routes failed: the build exits 2 and writes no file", (code, os.path.exists(out)), (2, False))


def t_g8(ck):
    base = tiny_vals()
    v1 = make_V(base, key="2026-10-16")
    b2 = {k: dict(v) for k, v in base.items()}
    b2["B1100NFRD"]["2026-09-09"] = "%.1f" % (float(base["B1100NFRD"]["2026-09-09"]) + 5)
    v2 = make_V(b2, key="2026-10-23")
    b3 = {k: dict(v) for k, v in b2.items()}
    b3["B1100NDMD"]["2026-09-16"] = "%.1f" % (float(b2["B1100NDMD"]["2026-09-16"]) - 2)
    b3["B1100NFRD"]["2026-09-23"] = "%.1f" % (float(b2["B1100NFRD"]["2026-09-23"]) + 7)
    v3 = make_V(b3, key="2026-10-30")
    rr = revision_rows([v1, v2, v3])
    key = lambda rows: sorted((r[0], r[1], r[2], r[3], r[6]) for r in rows)
    ck.eq("regenerated from the two adjacent pairs: three cells", key(rr), sorted([("2026-10-16", "2026-10-23", "B1100NFRD", "2026-09-09", "5.0"),
                                                                                  ("2026-10-23", "2026-10-30", "B1100NDMD", "2026-09-16", "-2.0"),
                                                                                  ("2026-10-23", "2026-10-30", "B1100NFRD", "2026-09-23", "7.0")]))
    bogus = [["2026-10-16", "2026-10-23", "B1100NFRD", "2026-01-07", "1.0", "2.0", "1.0"]]
    ck.eq("a stale committed revisions.csv changes nothing (build after two fetches)", revision_rows([v1, v2, v3], existing=bogus), rr)
    weekly = "2026-09-09,FRI,NSA,B1100NFRD,123.0,,,,,,,,,k\n"
    ck.eq("the previous vintage is never read from weekly.csv", revision_rows([v1, v2, v3], weekly_text=weekly), rr)
    row = lambda v, p, h: dict(vintage=v, route="xml", xml_prepared=p, xml_last_modified="", xml_sha256=h, fetched_utc="x")
    ck.eq("one Prepared date, one hash: no problem", index_problems([row("2026-10-16", "2026-10-16T10:00:00", "a" * 64), row("2026-10-23", "2026-10-23T10:00:00", "b" * 64)]), [])
    ck.ok("one Prepared date with two hashes is a problem", bool(index_problems([row("2026-10-16", "2026-10-16T10:00:00", "a" * 64), row("2026-10-17", "2026-10-16T10:00:00", "b" * 64)])))
    ck.eq("an equal latest week is not a regression", vintage_problems([v1, v2]), [])
    late = tiny_vals(n=5)
    ck.ok("a vintage whose latest week is earlier than the one before is a problem", bool(vintage_problems([v1, make_V(late, key="2026-10-23")])))
    ck.eq("an XML vintage is keyed by the Prepared date", vintage_key("xml", "2026-10-16T10:00:00", "2026-10-23"), "2026-10-16")
    ck.eq("a DDP fallback vintage is keyed by the fetch date", vintage_key("ddp_fallback", "", "2026-10-23"), "fetch-2026-10-23")
    with tempfile.TemporaryDirectory() as tmp:
        cache = os.path.join(tmp, "cache")
        zA = small_xml_zip(base, prepared="2026-10-16T10:00:00")
        k, new = ingest_xml(cache, zA, test_xml_zip(zA), "", "2026-10-23T12:05:34Z")
        ck.eq("ingest: keyed by Prepared and new", (k, new), ("2026-10-16", True))
        ck.eq("ingest of the same bytes again changes nothing", ingest_xml(cache, zA, test_xml_zip(zA), "", "2026-10-24T00:00:00Z"), ("2026-10-16", False))
        zB = small_xml_zip(b2, prepared="2026-10-16T10:00:00")
        ck.raises("the same Prepared date with different bytes is refused", DataError, lambda: ingest_xml(cache, zB, test_xml_zip(zB), "", "2026-10-24T00:00:00Z"))
        zC = small_xml_zip(b2, prepared="2026-10-23T10:00:00")
        ck.eq("a newer Prepared date is a new vintage", ingest_xml(cache, zC, test_xml_zip(zC), "", "2026-10-24T09:00:00Z"), ("2026-10-23", True))
        ck.ok("the older zip is pruned by its exact name and the newest kept", not os.path.exists(os.path.join(cache, "xml", "FRB_h8_xml_2026-10-16.zip"))
              and os.path.exists(os.path.join(cache, "xml", "FRB_h8_xml_2026-10-23.zip")))
        ck.eq("the index keeps both zip hashes", [r["xml_sha256"] for r in read_index(cache)], [sha256_of(zA), sha256_of(zC)])
        vs = load_vintages(cache)
        ck.eq("both vintages load from their subsets", [v["key"] for v in vs], ["2026-10-16", "2026-10-23"])
        ck.eq("one revision between them", [(r[2], r[3], r[6]) for r in revision_rows(vs)], [("B1100NFRD", "2026-09-09", "5.0")])


def synthetic_checksh(clean=True):
    arms = "\n".join("      %s) want='%s' ;;" % tuple(l.split(":", 1)) for l in SPEC_ALLOW_TEXT.splitlines())
    body = "h8fo_leak_check() {\n  case $name in\n%s\n  esac\n%s}\n" % (arms, "" if clean else "  want=$(python3 bin/h8_foreign_offices.py print-allowlist)\n")
    return "#!/bin/bash\n" + body + "\nnext_function() {\n  :\n}\n"


def t_g9(ck):
    ck.eq("SPEC_ALLOW_SHA256 is the sha256 of the canonical text", hashlib.sha256(allow_text().encode("utf-8")).hexdigest(), SPEC_ALLOW_SHA256)
    ck.eq("the canonical text is 817 bytes", len(allow_text().encode("utf-8")), 817)
    for n in ALLOW_ORDER:
        ck.quiet("the exact header of %s passes" % n, lambda n=n: check_header(n, ALLOW[n]))
    ck.raises("an extra column is refused", DataError, lambda: check_header("weekly.csv", ALLOW["weekly.csv"] + ["extra"]))
    ren = list(ALLOW["summary.csv"])
    ren[3] = "stat"
    ck.raises("a renamed column is refused", DataError, lambda: check_header("summary.csv", ren))
    h, rows = csv_body("# source: x\n" + ",".join(ALLOW["checks.csv"]) + "\nC01,d,e,o,PASS\n")
    ck.eq("the # source: line is skipped, not compared as a header", h, ALLOW["checks.csv"])
    files = world_files()
    files["extra.csv"] = "a,b\n1,2\n"
    ck.ok("an eleventh file is reported", any("not one of the ten" in p for p in leak_problems(files)), str(leak_problems(files)))
    ck.eq("the clean synthetic check.sh holds its own copy of the eight lines", checksh_problems(synthetic_checksh()), [])
    ck.ok("a check.sh that reads the headers from the script is reported", bool(checksh_problems(synthetic_checksh(clean=False))))
    ck.ok("a check.sh missing a header is reported", bool(checksh_problems(synthetic_checksh().replace("summary.csv) want=", "summary.csv) wnt="))))
    p = os.path.join(ROOT, "bin", "check.sh")
    if os.path.exists(p):
        ck.eq("bin/check.sh (guard M21) holds the eight canonical lines and does not read the script", checksh_problems(read_file(p, "r")), [])


def t_g10(ck):
    files = world_files()
    ck.eq("the clean folder passes the leak guard", leak_problems(files), [])
    f2 = dict(files)
    f2["FRB_h8_xml.zip"] = b"PK\x03\x04 raw zip"
    ck.ok("a raw .zip is reported", any("raw file" in p for p in leak_problems(f2)), str(leak_problems(f2)))
    f3 = dict(files)
    f3["notes.csv"] = '"Series Description","Net due to related foreign offices"\n"Unit:","Currency"\n'
    ck.ok("a DDP package renamed .csv is reported", any("DDP package" in p for p in leak_problems(f3)), str(leak_problems(f3)))
    f4 = dict(files)
    f4["SOURCES.md"] = f4["SOURCES.md"] + "\ncache at /Users/someone/data\n"
    ck.ok("a /Users/ path in SOURCES is reported", any("local path" in p for p in leak_problems(f4)), str(leak_problems(f4)))
    f5 = dict(files)
    f5["README.md"] = f5["README.md"] + "\nwrite to someone" + chr(64) + "example.org\n"
    ck.ok("an at sign is reported", any("at sign" in p for p in leak_problems(f5)))


def t_g11(ck):
    ok_text = REQUIRED_OPEN + "\n\n" + REQUIRED_S3 + "\n\nThe line includes unremitted profits. " + DENIAL_SENTENCE + "\n"
    ck.eq("the opening, sentence 3 and the denial sentence pass", wording_problems("README.md", ok_text), [])
    ck.ok("'because of quarter-end timing' is reported", bool(wording_problems("README.md", ok_text + "The gap rose because of quarter-end timing.\n")))
    ck.ok("'window dressing' outside the denial sentence is reported", bool(wording_problems("README.md", ok_text + "Banks show window dressing.\n")))
    ck.ok("a second sentence with 'flows' is reported", bool(wording_problems("README.md", ok_text + "Quarterly flows are large.\n")))
    ck.ok("'head offices funded the branches' is reported", bool(wording_problems("README.md", ok_text + "Head offices funded the branches.\n")))
    ck.ok("a causal verb is reported", bool(wording_problems("README.md", ok_text + "A shock drove the line.\n")))
    ck.ok("the denial sentence twice is reported (it is exempt once)", bool(wording_problems("README.md", ok_text + DENIAL_SENTENCE + "\n")))
    ck.ok("a flow sentence next to the denial sentence is reported", bool(wording_problems("README.md", ok_text + "Money flows freely.\n")))
    ck.ok("the denial sentence is not exempt outside the README", bool(wording_problems("summary.csv", DENIAL_SENTENCE)))
    ck.ok("a CSV cell with causal wording is reported", bool(wording_problems("notes.csv", "a,b\nx,led to a rise\n")))
    ck.eq("'due to' is the series name and is not banned", wording_problems("README.md", "Net due to related foreign offices.\n"), [])


G12_BAD = [
    ("os.remove on a STOP path", "import os\ndef f(stop_path):\n    os.remove(stop_path)\n"),
    ("Path.unlink on a STOP path", "import pathlib\ndef f(d):\n    p = pathlib.Path(d) / 'STOP_xml'\n    p.unlink()\n"),
    ("open w on a STOP path", "def f(d):\n    open(d + '/STOP_xml', 'w').write('x')\n"),
    ("open a on a STOP path", "def f(stop_file):\n    with open(stop_file, 'a') as fh:\n        fh.write('x')\n"),
    ("open x on a STOP path outside create_stop", "def f(stop_file):\n    with open(stop_file, 'x') as fh:\n        fh.write('x')\n"),
    ("os.replace onto a STOP path", "import os\ndef f(tmp, stop_path):\n    os.replace(tmp, stop_path)\n"),
    ("os.rename onto a STOP path", "import os\ndef f(tmp):\n    os.rename(tmp, 'STOP_ddp')\n"),
    ("shutil.move onto a STOP path", "import shutil\ndef f(tmp, stop_dir):\n    shutil.move(tmp, stop_dir)\n"),
    ("Path.write_text on a STOP path", "import pathlib\ndef f():\n    pathlib.Path('STOP_notes').write_text('x')\n"),
    ("Path.write_bytes on a STOP path", "import pathlib\ndef f(stop):\n    pathlib.Path(stop).write_bytes(b'x')\n"),
    ("shutil.rmtree of the cache", "import shutil\ndef f(cache):\n    shutil.rmtree(cache)\n"),
    ("pruning by a glob over the cache root", "import glob, os\ndef prune_old_zips(cache):\n    for p in glob.glob(os.path.join(cache, '*')):\n        os.remove(p)\n"),
]
G12_CLEAN = [
    ("pruning by exact name", "import os\ndef prune_old_zips(cache, names):\n    for n in names:\n        os.remove(os.path.join(cache, 'xml', n))\n"),
    ("the sanctioned exclusive create", "def create_stop(path, text):\n    with open(path, 'x') as fh:\n        fh.write(text)\n"),
    ("a write that is not a STOP path", "def f(path):\n    with open(path, 'w') as fh:\n        fh.write('x')\n"),
    ("reading a STOP file", "def f(stop_path):\n    return open(stop_path).read()\n"),
]


def t_g12(ck):
    for name, src in G12_BAD:
        ck.ok("the AST scan flags: " + name, bool(stop_ast_problems(src)), "not flagged")
    for name, src in G12_CLEAN:
        ck.eq("the AST scan accepts: " + name, stop_ast_problems(src), [])
    ck.eq("the script itself passes the AST scan", stop_ast_problems(read_file(os.path.abspath(__file__), "r")), [])
    vals = tiny_vals()
    body = "status: 500\nutc_time: x\nurl_path: /x\nretry_after: \nbody_head: x\n"
    with tempfile.TemporaryDirectory() as tmp:
        sd = os.path.join(tmp, "stop")
        for s in ("xml", "ddp"):
            create_stop(os.path.join(sd, "STOP_" + s), body)
        before = {s: sha256_of(read_file(os.path.join(sd, "STOP_" + s))) for s in ("xml", "ddp")}
        fe, calls, _ = fake_rig(tmp, fetch_handler(vals), stop_dir=sd)
        said = []
        res = do_fetch(fe, say=said.append)
        ck.eq("with STOP_xml and STOP_ddp planted, fetch makes no request", len(calls), 0)
        ck.eq("...and exits 2", fetch_exit_code(res), 2)
        ck.ok("...and prints STOP present: <file>", sum(1 for s in said if s.startswith("STOP present: ")) == 2, str(said))
        ck.eq("...and both latch files are unchanged", {s: sha256_of(read_file(os.path.join(sd, "STOP_" + s))) for s in ("xml", "ddp")}, before)
    with tempfile.TemporaryDirectory() as tmp:
        sd = os.path.join(tmp, "stop")
        create_stop(os.path.join(sd, "STOP_xml"), body)
        fe, calls, _ = fake_rig(tmp, fetch_handler(vals), stop_dir=sd)
        res = do_fetch(fe, say=lambda *a: None)
        ck.ok("with only STOP_xml planted, no XML request is made", all(c[1] != XML_PATH for c in calls), str([c[1][:30] for c in calls]))
        ck.eq("...and the DDP and notes still go ahead (5 requests)", len(calls), 5)
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _ = fake_rig(tmp, fetch_handler(vals, xml=500))
        do_fetch(fe, say=lambda *a: None)
        p = os.path.join(tmp, "stop", "STOP_xml")
        h0 = sha256_of(read_file(p))
        create_stop(p, "status: 999\nutc_time: y\nurl_path: /y\nretry_after: \nbody_head: y\n")
        ck.eq("create_stop never overwrites an existing latch", sha256_of(read_file(p)), h0)
        lines = read_file(p, "r").splitlines()
        ck.eq("a 500 on the XML writes STOP_xml with status, utc_time, url_path, retry_after and body_head", [l.split(":")[0] for l in lines], ["status", "utc_time", "url_path", "retry_after", "body_head"])


def t_g13(ck):
    ck.raises("a non-allowlisted host (FRED) is refused before any request", Refused, lambda: check_url("https://fred.stlouisfed.org/series/H8B1100NFRD"))
    ck.raises("plain http is refused", Refused, lambda: check_url("http://" + HOST + XML_PATH))
    ck.raises("a path that is not one of the six requests is refused", Refused, lambda: check_url("https://" + HOST + "/releases/h8/default.htm"))
    ck.quiet("the XML request passes", lambda: check_url("https://" + HOST + XML_PATH))
    ck.raises("an address in the identification string is refused", Refused, lambda: assert_ua(UA + " x" + chr(64) + "y.org"))
    ck.ok("the identification string is the CLAUDE.md string, with no address", HEADERS["User-Agent"] == UA and chr(64) not in UA)
    vals = tiny_vals()
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _ = fake_rig(tmp, lambda h, t, hd: (301, b"moved", {"location": "https://elsewhere.example.org/x"}))
        ck.raises("a 301 latches", Latched, lambda: fe.get_checked("xml", XML_PATH, test_xml_zip))
        ck.eq("...with one request and no redirect followed", len(calls), 1)
        ck.ok("...and STOP_xml records the 301", os.path.exists(os.path.join(tmp, "stop", "STOP_xml")) and read_file(os.path.join(tmp, "stop", "STOP_xml"), "r").startswith("status: 301"))
    for status in (429, 500):
        with tempfile.TemporaryDirectory() as tmp:
            fe, calls, _ = fake_rig(tmp, lambda h, t, hd, s=status: (s, b"slow", {"retry-after": "60"}))
            ck.raises("a %d latches" % status, Latched, lambda: fe.get_checked("xml", XML_PATH, test_xml_zip))
            ck.eq("...with no retry (one request)", len(calls), 1)
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, clock = fake_rig(tmp, fetch_handler(vals))
        fe.get_checked("notes", NOTES_PATH, test_notes)
        fe.get_checked("notes", NOTES_PATH, test_notes)
        ck.ok("two requests are at least 3 seconds apart", calls[1][3] - calls[0][3] >= 3.0, "gap %.2f s" % (calls[1][3] - calls[0][3]))
        ck.ok("every request carries the same neutral User-Agent", all(c[2]["User-Agent"] == UA for c in calls))
        ck.ok("every request is to the one allowed host", all(c[0] == HOST for c in calls))
    with tempfile.TemporaryDirectory() as tmp:
        fe, calls, _ = fake_rig(tmp, fetch_handler(vals))
        for _ in range(6):
            fe.get_checked("notes", NOTES_PATH, test_notes)
        ck.raises("a 7th request is refused", MaxRequests, lambda: fe.get_checked("notes", NOTES_PATH, test_notes))
        ck.eq("...so six requests were made", len(calls), 6)
    with tempfile.TemporaryDirectory() as tmp:
        ck.raises("a pause under 3 seconds is refused", Refused, lambda: fake_rig(tmp, fetch_handler(vals), sleep=1.0))


def t_g14(ck):
    W = get_world()
    notes = W["notes"]
    f, d, a = break_map(notes, "FRI"), break_map(notes, "DOM"), break_map(notes, "ALL")
    ck.eq("FRI break weeks: its five notes and footnote 20", sorted(f), ["2008-02-06", "2008-04-02", "2010-03-31", "2017-11-29", "2019-10-02", "2022-04-06"])
    ck.eq("DOM break weeks: its seven notes, no footnote 20", sorted(d), ["2004-12-29", "2006-10-04", "2007-03-07", "2008-08-20", "2011-01-05", "2016-03-02", "2018-04-04"])
    ck.eq("ALL takes the union", sorted(a), sorted(set(f) | set(d)))
    ck.eq("footnote 20 opens a segment at 2022-04-06 for FRI", f.get("2022-04-06"), ["footnote"])
    dd = {"2019-09-25": 100.0, "2019-10-02": 160.0, "2019-10-09": 165.0}
    ck.eq("the change ending at a break week belongs to no segment", seg_change(dd, "2019-10-02", ["2019-10-02"]), None)
    ck.eq("the next change is taken", seg_change(dd, "2019-10-09", ["2019-10-02"]), 5.0)
    ck.eq("segment windows from 2019-01-02 for FRI", seg_windows(sorted(f), Q1_START, "2026-10-07"),
          [("2019-01-02", "2019-09-25"), ("2019-10-02", "2022-03-30"), ("2022-04-06", "2026-10-07")])
    ck.eq("a window that spans a break is detected, one that starts on it is not", (crosses_break("2022-03-30", "2022-04-13", ["2022-04-06"]), crosses_break("2022-04-06", "2022-05-04", ["2022-04-06"])), (True, False))
    A, L = W["c0"]["A"], W["c0"]["L"]
    rows = q1_rows(A, L, W["brk"])
    ck.eq("Q1 windows: three for FRI, one for DOM", sorted({(r[2], r[1]) for r in rows}),
          [("DOM", "2019-01-02..2026-10-07"), ("FRI", "2019-01-02..2019-09-25"), ("FRI", "2019-10-02..2022-03-30"), ("FRI", "2022-04-06..2026-10-07")])
    d38 = A[("FRI", "NSA")]["l38"]
    seg2 = [d38[w] for w in weeks_between("2019-10-02", "2022-03-30")]
    mn = next(r for r in rows if r[2] == "FRI" and r[1] == "2019-10-02..2022-03-30" and r[3] == "min_level")
    ck.eq("the minimum of a segment is taken inside it", mn[4], fnum(min(seg2), 1))
    wk = W["c0"]["weekly"]
    r = next(x for x in wk if x[0] == "2019-10-02" and x[1] == "FRI" and x[2] == "NSA")
    ck.eq("the weekly row of a break week: no change, a note flag, the segment opens there", (r[5], r[12], r[11]), ("", "note", "2019-10-02"))
    r = next(x for x in wk if x[0] == "2019-09-25" and x[1] == "FRI" and x[2] == "NSA")
    ck.eq("the week before: its segment started at the previous break", r[11], "2017-11-29")
    qf = {(r[0], r[5]): r for r in quarter_table(A, L, W["brk"], "k")}
    ck.eq("FRI 2019Q3: delta_qe_wed ends on the 2019-10-02 note week, is blank, straddles_break yes", (qf[("2019Q3", "FRI")][7], qf[("2019Q3", "FRI")][10]), ("", "yes"))
    ck.eq("FRI 2022Q1: delta_next ends on 2022-04-06, is blank, straddles_break yes", (qf[("2022Q1", "FRI")][8], qf[("2022Q1", "FRI")][10]), ("", "yes"))
    ck.ok("...while the other change of each is filled", qf[("2019Q3", "FRI")][8] != "" and qf[("2022Q1", "FRI")][7] != "")
    r = next(x for x in wk if x[0] == "2022-04-06" and x[1] == "DOM")
    ck.eq("footnote 20 is not a DOM break", r[12], "")


def t_g15(ck):
    ents, plain = parse_notes_entries(notes_html())
    ck.eq("14 dated entries; the index run of dates is not an entry", len(ents), 14)
    rows = notes_rows(ents)
    got = [(r["week"], r["group"], r["amount"], r["para"]) for r in rows if r["kind"] == "note"]
    want = [("2006-10-04", "DOM", -10000.0, 0), ("2007-03-07", "DOM", -3200.0, 0), ("2008-02-06", "FRI", 12000.0, 0), ("2008-04-02", "FRI", -18600.0, 0), ("2008-08-20", "DOM", -8600.0, 0),
            ("2010-03-31", "FRI", -12000.0, 1), ("2011-01-05", "DOM", 5700.0, 0), ("2016-03-02", "DOM", -3100.0, 0), ("2017-11-29", "FRI", 5200.0, 0), ("2018-04-04", "DOM", 2000.0, 0),
            ("2019-10-02", "FRI", -3000.0, 0), ("2004-12-29", "DOM", 2000.0, 0)]
    ck.eq("the twelve in-sample notes with signed amounts (the sign of -$3.0 billion kept; the undated -$12.0 kept)", sorted(got), sorted(want))
    ents2, _ = parse_notes_entries(notes_html(extra_entries=[("20120201", [NOTE_FR("$1.0"), NOTE_DM("-$1.5"), NOTE_NONE])]))
    r2 = [(r["group"], r["amount"], r["para"]) for r in notes_rows(ents2) if r["week"] == "2012-02-01"]
    ck.eq("the group is read per paragraph: an FRI paragraph, then a DOM paragraph in one entry", r2, [("FRI", 1000.0, 0), ("DOM", -1500.0, 1)])
    ck.ok("the footnote 20 row is added with the week 2022-04-06 and no amount", any(r["kind"] == "footnote" and r["week"] == "2022-04-06" and r["amount"] is None for r in rows))
    ck.quiet("the notes page passes its content test", lambda: test_notes(notes_html().encode("utf-8")))
    ck.raises("a page without a dated note fails the content test", ContentError, lambda: test_notes(b"<html>Notes on Data and nothing else</html>"))
    ck.ok("text_head is the clause that carries the amount, and does not start with the Board's reason clause",
          all(not r["head"].lower().startswith("because") and "billion" in r["head"] for r in rows if r["kind"] == "note"))


def t_g16(ck):
    W = get_world()
    A, L, brk, union = W["c0"]["A"], W["c0"]["L"], W["brk"], W["union"]
    bad = []
    for r in q1_rows(A, L, brk) + q2_rows(A, L, brk, union) + q4_rows(A, L, brk, union):
        if r[6] != "no":
            bad.append(r[0])
    two = [tiny_V(key="2026-10-16"), tiny_V(key="2026-10-23", fri=[800000.0 + 1000 * i + (3 if i == 1 else 0) for i in range(6)])]
    for r in q6_rows(two, revision_rows(two)):
        if r[6] != "no":
            bad.append(r[0])
    ck.eq("every Q1, Q2, Q4 and Q6 row is blind = no", sorted(set(bad)), [])
    q = quarter_table(A, L, brk, "k")
    ck.eq("only the 2026Q3 rows of quarter_ends.csv are blind = no", sorted({r[0] for r in q if r[12] == "no"}), ["2026Q3"])
    s3 = q3_rows(q)
    ck.eq("Q3 summary rows: blind = no only for 2026Q3", sorted({r[1][:6] for r in s3 if r[6] == "no"}), ["2026Q3"])
    ck.ok("...and yes for the others", all(r[6] == "yes" for r in s3 if not r[1].startswith("2026Q3")))


def t_g17(ck):
    W = get_world()
    union = W["union"]
    ck.eq("the endpoints are the four named Wednesdays; Lo is not among them", endpoints("2026-10-07", union), list(Q2_ENDPOINTS))
    for w in sorted(set(Q2_ENDPOINTS) | set(Q1_WEDNESDAYS)):
        ck.eq("named endpoint %s passes" % w, named_problems(w, union), [])
    ck.eq("the nearest quarter-end day to any named Wednesday is 39 days away", min(qe_distance(w) for w in set(Q2_ENDPOINTS) | set(Q1_WEDNESDAYS)), 39)
    ck.ok("a Wednesday within 7 days of a quarter-end day is refused", bool(ordinary_problems("2026-04-01", set())))
    ck.ok("a break week is refused", bool(ordinary_problems("2021-05-12", {"2021-05-12"})))
    ck.ok("a Wednesday 6 days from a quarter-end day (2027-01-06, after 2026-12-31) is refused", bool(ordinary_problems("2027-01-06", set())))
    ck.eq("...and one 7 days away is not", ordinary_problems("2026-10-07", set()), [])
    ck.ok("the first Wednesday of the year is refused", bool(named_problems("2025-01-01", set())))
    ck.ok("an ordinary Wednesday that is not the 8th-14th of February or August is refused as a named endpoint", bool(named_problems("2025-01-08", set())))
    ck.eq("Lo on 2026-10-07 is 2026-10-07 (7 days from 2026-09-30)", lo_week("2026-10-07", set()), "2026-10-07")
    ck.eq("Lo from 2026-09-30 steps back to 2026-09-23", lo_week("2026-09-30", set()), "2026-09-23")


def t_x_cache(ck):
    ck.quiet("a cache outside the repository is accepted", lambda: check_cache(os.path.join(tempfile.gettempdir(), "h8_cache_x")))
    ck.raises("the committed output folder is refused as a cache", Refused, lambda: check_cache(os.path.join(ROOT, "data", "h8_foreign_offices", "cachex")))
    ck.raises("a path inside the repository that git does not ignore is refused", Refused, lambda: check_cache(os.path.join(ROOT, "bin", "cache_x")))


def t_x_build(ck):
    W = get_world()
    if _ACTIVE:
        texts, failed = finish(compute(W["inp"]))                # under a mutant the rendering is made again, so C15 and the guards see it
        checks = compute(W["inp"])["checks"]
    else:
        texts, failed, checks = W["texts"], W["failed"], W["c0"]["checks"]
    ck.eq("the synthetic build fails no check", failed, [])
    st = {r[0]: r[4] for r in checks}
    ck.eq("...and the checks that always run are PASS", [st[k] for k in ("C01", "C02", "C03", "C04", "C05", "C07", "C07w", "C08", "C09", "C10", "C11", "C13", "C14")], ["PASS"] * 13)
    ck.eq("C15 and C16 are PASS in the rendering", sorted((r[0], r[4]) for r in parse_checks(texts["checks.csv"]) if r[0] in ("C15", "C16")), [("C15", "PASS"), ("C16", "PASS")])
    ck.eq("every committed file is present, nothing else", sorted(texts), sorted(COMMITTED))
    ck.eq("the folder guards pass on the rendering", all_folder_problems(texts), [])
    rd = texts["README.md"]
    pos = [rd.find(REQUIRED_OPEN), rd.find(REQUIRED_S3), rd.find("## The sign, and the trap"), rd.find("## What the line contains"), rd.find("## Breaks"), rd.find("## Endpoints"),
           rd.find("## Quarter-ends"), rd.find("## Latest levels"), rd.find("## Seasonal adjustment"), rd.find("## Column dictionary"), rd.find("## Provenance")]
    ck.ok("the README has its sections in the order of the spec", all(p >= 0 for p in pos) and pos == sorted(pos), str(pos))
    ck.ok("the README carries the denial sentence once and the caveat sentence", rd.count(DENIAL_SENTENCE) == 1 and CAVEAT_SENTENCE in rd)
    ck.ok("SOURCES.md has a Builder decisions section", "## Builder decisions" in texts["SOURCES.md"])
    t2 = render_data_texts(compute(W["inp"]))
    ck.eq("a second render over the same inputs is byte-identical", {n: sha256_of(t.encode()) for n, t in t2.items() if n in ("weekly.csv", "revisions.csv", "summary.csv")},
          {n: sha256_of(texts[n].encode()) for n in ("weekly.csv", "revisions.csv", "summary.csv")})


def parse_checks(text):
    return csv_body(text)[1]


GUARDS = [
    ("G1", "group binding: groups told apart by group code, identity and line 40, never by sign", ["g1_swap_l38", "g1_swap_groups", "g1_bg_misread", "g1_select_by_index", "g1_negative_fri_fails"], t_g1),
    ("G2", "sign identity: line 38 = 40 - 34 - 37 - 39", ["g2_negate_l38", "g2_asset_side", "g2_double_count", "g2_breach_unreported"], t_g2),
    ("G3", "group identity: ALL = DOM + FRI, no 'FRI <= ALL' limit", ["g3_all_from_sa", "g3_tol_2mn", "g3_fri_le_all"], t_g3),
    ("G4", "NSA and exact suffix", ["g4_sa_stat", "g4_substring"], t_g4),
    ("G5", "units: usd_mn", ["g5_mult_ignored", "g5_thousands", "g5_bn_in_mn"], t_g5),
    ("G6", "quarter-ends: nearest Wednesday, on-date only, no statistic across quarters, frozen set", ["g6_last_wed_before", "g6_first_wed_after", "g6_after_is_qe", "g6_nonwed_on_date", "g6_window_neg", "g6_avg_written", "g6_post_frozen", "g6_frozen_last_q4"], t_g6),
    ("G7", "routes: XML primary, DDP cross-check and fallback", ["g7_tol_1mn", "g7_ddp404_aborts", "g7_xml500_refuses", "g7_both_failed_builds"], t_g7),
    ("G8", "vintages and revisions", ["g8_incremental", "g8_prev_from_weekly", "g8_same_prepared_accepted", "g8_earlier_latest_accepted", "g8_xml_keyed_by_fetch_date"], t_g8),
    ("G9", "allowlists: exact headers, canonical hash, check.sh keeps its own copy", ["g9_extra_col_ok", "g9_renamed_ok", "g9_allow_drift", "g9_source_as_header", "g9_eleventh_ok", "g9_checksh_reads_script"], t_g9),
    ("G10", "leak guard: raw files, DDP packages, local paths", ["g10_zip_ok", "g10_ddp_renamed_ok", "g10_path_ok"], t_g10),
    ("G11", "wording: causal, flow and motive patterns", ["g11_causal_off", "g11_extra_off", "g11_denial_all", "g11_denial_loose"], t_g11),
    ("G12", "STOP latch: AST scan and runtime", ["g12_scan_off", "g12_ignore_open", "g12_replace_ok", "g12_glob_ok", "g12_stop_ignored", "g12_stop_short"], t_g12),
    ("G13", "fetch safety: host, identification string, redirects, pacing, cap, retries", ["g13_allow_other_host", "g13_at_in_ua_ok", "g13_redirect_follow", "g13_pacing_off", "g13_cap_off", "g13_retry"], t_g13),
    ("G14", "breaks and segments", ["g14_across_break", "g14_change_in_segment", "g14_footnote_missing", "g14_dom_note_as_fri", "g14_fill_straddle"], t_g14),
    ("G15", "notes parse", ["g15_sign_lost", "g15_undated_dropped", "g15_group_per_entry", "g15_index_as_note"], t_g15),
    ("G16", "blind marks", ["g16_q1_yes", "g16_q2_yes", "g16_q4_yes", "g16_q6_yes", "g16_2026q3_yes", "g16_other_no"], t_g16),
    ("G17", "endpoints", ["g17_near_qe_ok", "g17_break_ok", "g17_first_wed", "g17_lo_fixed", "g17_qe_lt3"], t_g17),
    ("X1", "cache path: outside the repo, or git-ignored inside it", ["x_cache_check_off"], t_x_cache),
    ("X2", "an end-to-end synthetic build: determinism and the folder guards on the rendering", ["x_render_unstable"], t_x_build),
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
                print("       mutant %-28s %s%s" % (m, "caught" if caught else "NOT CAUGHT", "  (first failing check: %s)" % mk.failed()[0][0][:70] if caught else ""))
    print("selftest: %d guards, %d checks, %d mutants applied one at a time, %d failure(s), %.1f s" % (len(GUARDS), n_checks, n_mut, bad_total, time.time() - t0))
    return 0 if bad_total == 0 else 1


# ==== COMMAND LINE ====
def run_fetch(a):
    os.makedirs(a.out, exist_ok=True)
    fe = Fetcher(a.cache, a.out, sleep=a.sleep)
    try:
        res = do_fetch(fe)
    except SocketFault as e:
        print("socket fault (%s): the invocation ends; nothing was latched and nothing is retried" % e, file=sys.stderr)
        print("requests sent %d" % fe.requests)
        return 4
    print("requests sent %d; xml %s, ddp %s, notes %s" % (fe.requests, res["xml"], res["ddp"], res["notes"]))
    return fetch_exit_code(res)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch", help="download the inputs into the cache (the only network command; at most 6 requests)")
    pf.add_argument("--cache", default=CACHE_DEFAULT)
    pf.add_argument("--out", default=OUT_DEFAULT, help="where fetch_log.csv is kept")
    pf.add_argument("--sleep", type=float, default=DEFAULT_SLEEP)
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
