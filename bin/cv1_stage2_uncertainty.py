#!/usr/bin/env python3
"""CV1 stage 2 (v2): did managers' perceived uncertainty fall after generative AI spread? Free aggregate proxies. Python 3 standard library plus openpyxl.

  python3 bin/cv1_stage2_uncertainty.py selftest                                  # synthetic inputs with known answers; no network, no files read
  python3 bin/cv1_stage2_uncertainty.py fetch [--only KEY,KEY] [--max-seconds N]  # network; resumable; skips files already in the cache
  python3 bin/cv1_stage2_uncertainty.py build                                     # offline; writes registered.csv FIRST, then scores and descriptive tables

Specification: _research/2026-11-13-CV1-Stage2-Aggregate-Proxies-Spec.md, section "Version 2" (binding; it supersedes the v1 table above it).
build refuses to score when the sha256 of that file differs from PREREG_SHA256 below. Only CV1-S1 v2 and CV1-S4 v2 carry labels (S4 only when S1 is SUPPORT);
S2, S3, S5 and S6 are descriptive and print no label.

Outputs: data/cv1_stage2_uncertainty/ (registered.csv, scores.csv, sensitivity.csv, s2_beigebook_editions.csv, s3_dallas_uncertainty.csv, s5_boe_dmp.csv,
s6_btos.csv, README.md). Raw downloads and the local S1 monthly panel stay in data/vintages/cv1_stage2/ (a nested .gitignore of "*" keeps every file there out of git).

NETWORK. Only `fetch`. One fixed generic User-Agent (no name, address or contact). At most one request per second to any host and under two per second to
federalreserve.gov. A 3xx is followed only inside the same registrable domain, for at most two hops. On a 403 or 429 the request is retried once after ten
seconds; a second refusal writes a STOP latch for that host in the cache and no further request is made to it. This script never deletes a STOP file.
"""
import argparse
import csv
import datetime as dt
import hashlib
import html
import io
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SPEC_FILE = "_research/2026-11-13-CV1-Stage2-Aggregate-Proxies-Spec.md"
PREREG_SHA256 = "7cda4b28fe824781f426ea9f3d76ad6f4caa09c7a104792b5f332c0a6bc7b270"
USER_AGENT = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"

OUT_REL = "data/cv1_stage2_uncertainty"
CACHE_REL = "data/vintages/cv1_stage2"

# ------------------------------------------------------------------------------------------------------------------------
# the registered windows, dictionaries and thresholds (typed from the spec; never changed)
# ------------------------------------------------------------------------------------------------------------------------
S1_BASE = ((2016, 12), (2019, 12))
S1_TREAT = ((2023, 1), (2025, 12))
S4_BASE = ((2016, 12), (2019, 12))
S4_TREAT = ((2024, 1), (2025, 12))
S5_BASE = ((2017, 1), (2019, 12))
S5_TREAT = ((2023, 1), (2025, 12))
S1_SUPPORT_AT, S1_AGAINST_AT = -0.5, 0.0
S4_SUPPORT_FRAC = 0.9
BEIGE_FIRST, BEIGE_LAST = dt.date(2015, 1, 1), dt.date(2026, 10, 31)
BEIGE_FORMAT_CHANGE = dt.date(2017, 1, 18)

UNC_WORDS = ("uncertain", "uncertainty", "uncertainties")
EXCL_WORDS = ("tariff", "tariffs", "election", "elections", "shutdown", "regulation", "regulations", "regulatory", "tax", "taxes", "fiscal",
              "geopolitical", "sanctions", "immigration", "pandemic", "covid", "brexit", "congress", "legislation")
EXCL_PHRASES = ("federal reserve", "interest rate", "interest rates", "debt ceiling", "stock market", "financial market", "financial markets")

DISTRICTS = ("Boston", "New York", "Philadelphia", "Cleveland", "Richmond", "Atlanta", "Chicago", "St. Louis", "Minneapolis", "Kansas City", "Dallas", "San Francisco")
ORDINALS = ("First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth", "Ninth", "Tenth", "Eleventh", "Twelfth")
DISTRICT_SLUGS = {"Boston": "boston", "New York": "new-york", "Philadelphia": "philadelphia", "Cleveland": "cleveland", "Richmond": "richmond", "Atlanta": "atlanta",
                  "Chicago": "chicago", "St. Louis": "st-louis", "Minneapolis": "minneapolis", "Kansas City": "kansas-city", "Dallas": "dallas", "San Francisco": "san-francisco"}
# headings that end a District section whatever their level
BB_TERMINATORS = ("national summary", "other formats", "more information", "board of governors of the federal reserve system", "tools and information", "stay connected",
                  "summary of commentary on current economic conditions by federal reserve district", "full report", "highlights by federal reserve district")
BB_BOILERPLATE_EXACT = ("return to top",)
BB_BOILERPLATE_PREFIX = ("for more information about district economic conditions",)

FED_HOST = "www.federalreserve.gov"


class Refused(Exception):
    """A request, path or output this script will not produce."""


class DataError(Exception):
    """The data do not have the shape the specification needs."""


class Stopped(Exception):
    """A host latched a STOP."""


# ------------------------------------------------------------------------------------------------------------------------
# small helpers
# ------------------------------------------------------------------------------------------------------------------------
def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def month_index(ym):
    return ym[0] * 12 + (ym[1] - 1)


def month_from_index(i):
    return (i // 12, i % 12 + 1)


def months_between(first, last):
    return [month_from_index(i) for i in range(month_index(first), month_index(last) + 1)]


def ym_text(ym):
    return "%04d-%02d" % ym


def mean(xs):
    xs = list(xs)
    if not xs:
        raise DataError("mean of an empty list")
    return sum(xs) / len(xs)


def stdev(xs, ddof=1):
    xs = list(xs)
    n = len(xs)
    if n - ddof <= 0:
        raise DataError("standard deviation needs more observations")
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - ddof))


def fmt(x, nd=6):
    if x is None:
        return ""
    if isinstance(x, float):
        return ("%." + str(nd) + "f") % x
    return str(x)


def safe_text(text):
    """A committed file never holds a local path or an at sign."""
    for bad in ("/Users/", "/private/", "~/", "@"):
        if bad in text:
            raise Refused("refusing to write text that contains %r" % bad)
    return text


def write_text(path, text):
    safe_text(text)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    os.replace(tmp, path)


def csv_text(header, rows, comments=()):
    buf = io.StringIO()
    for c in comments:
        buf.write("# " + c + "\n")
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


# ------------------------------------------------------------------------------------------------------------------------
# pure statistics: OLS, effect size, labels, ratio of means
# ------------------------------------------------------------------------------------------------------------------------
def solve_linear(A, b):
    """Gaussian elimination with partial pivoting; A is a list of rows."""
    n = len(A)
    M = [list(map(float, A[i])) + [float(b[i])] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-12:
            raise DataError("singular normal equations")
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                if f:
                    for k in range(c, n + 1):
                        M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


def ols(X, y):
    """OLS of y on the columns of X (X holds the constant if one is wanted). Returns (beta, residuals)."""
    n, k = len(X), len(X[0])
    if n <= k:
        raise DataError("fewer observations than parameters")
    XtX = [[sum(X[i][a] * X[i][b] for i in range(n)) for b in range(k)] for a in range(k)]
    Xty = [sum(X[i][a] * y[i] for i in range(n)) for a in range(k)]
    beta = solve_linear(XtX, Xty)
    resid = [y[i] - sum(X[i][a] * beta[a] for a in range(k)) for i in range(n)]
    return beta, resid


def effect_size(d, baseline_resid, ddof=1):
    return d / stdev(baseline_resid, ddof)


def s1_label(eff):
    """Spec: SUPPORT if effect size <= -0.5; AGAINST if >= 0; otherwise INCONCLUSIVE (no label). The registered inequalities are inclusive."""
    if eff <= S1_SUPPORT_AT:
        return "SUPPORT"
    if eff >= S1_AGAINST_AT:
        return "AGAINST"
    return "INCONCLUSIVE"


def ratio_of_means(num, den):
    """R = (window mean of numerator) / (window mean of denominator); not the mean of monthly ratios."""
    return mean(num) / mean(den)


def s4_label(r_t, r_b, s1):
    """Spec: labelled only if S1 v2 is SUPPORT. SUPPORT if R_T <= 0.9 * R_B; AGAINST if R_T >= R_B; otherwise INCONCLUSIVE."""
    if s1 != "SUPPORT":
        return "UNLABELLED_S1_NOT_SUPPORT"
    if r_t <= S4_SUPPORT_FRAC * r_b:
        return "SUPPORT"
    if r_t >= r_b:
        return "AGAINST"
    return "INCONCLUSIVE"


def s1_fit(rows):
    """rows: list of dicts with y, epu, vix, spf (the raw levels) and treat (0/1). Fits Y = a + b1 log EPU + b2 log VIX + b3 log SPF + d Treatment."""
    X = [[1.0, math.log(r["epu"]), math.log(r["vix"]), math.log(r["spf"]), float(r["treat"])] for r in rows]
    y = [r["y"] for r in rows]
    beta, resid = ols(X, y)
    base_resid = [resid[i] for i, r in enumerate(rows) if not r["treat"]]
    return beta, resid, base_resid


# ------------------------------------------------------------------------------------------------------------------------
# text: sentence splitter and the two whole-word dictionaries
# ------------------------------------------------------------------------------------------------------------------------
ABBREV = frozenset("st mt ft mr mrs ms dr jr sr inc corp co ltd vs approx jan feb aug sept oct nov dec".split())
_TERM = re.compile(r"([.?!]+)([\"'”’)\]]*)(\s+)")
_INITIALS = re.compile(r"(?:[A-Za-z]\.)*[A-Za-z]")


def norm_ws(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ").replace("​", "")).strip()


def split_sentences(text):
    """Split on . ? ! followed by whitespace, except after an abbreviation: initials chained with periods (U.S., U.K., D.C., e.g.) and a short list
    (St., Mt., Inc., Corp., Co., Mr., Dr., month abbreviations ...). Every non-empty remainder counts as a sentence, with or without a final stop."""
    text = norm_ws(text)
    out, start = [], 0
    for m in _TERM.finditer(text):
        term = m.group(1)
        if term == "." and not m.group(2):
            before = text[start:m.start()]
            token = before.rsplit(" ", 1)[-1]
            tok = token.lstrip("\"'“‘([")
            if _INITIALS.fullmatch(tok) and (len(tok) == 1 or "." in tok):
                continue
            if tok.lower() in ABBREV:
                continue
        piece = text[start:m.end()].strip()
        if piece:
            out.append(piece)
        start = m.end()
    rest = text[start:].strip()
    if rest:
        out.append(rest)
    return [s for s in out if re.search(r"[A-Za-z0-9]", s)]


UNC_RX = re.compile(r"\b(?:" + "|".join(UNC_WORDS) + r")\b", re.I)
EXCL_RX = re.compile(r"\b(?:" + "|".join(EXCL_WORDS) + r")\b|\b(?:" + "|".join(r"\s+".join(map(re.escape, p.split())) for p in EXCL_PHRASES) + r")\b", re.I)


def dict_a(sentence):
    """(a) whole-word match on uncertain | uncertainty | uncertainties (case-insensitive)."""
    return UNC_RX.search(sentence) is not None


def policy_linked(sentence):
    """True if the sentence holds a whole word of the registered exclusion list or one of its phrases."""
    return EXCL_RX.search(sentence) is not None


def dict_b(sentence):
    """(b) dictionary (a), dropping the sentence only if it is policy- or market-linked by the registered list."""
    return dict_a(sentence) and not policy_linked(sentence)


def count_sentences(sentences):
    n = len(sentences)
    a = sum(1 for s in sentences if dict_a(s))
    b = sum(1 for s in sentences if dict_b(s))
    return n, a, b


def per_1000(k, n):
    return 1000.0 * k / n if n else float("nan")


# ------------------------------------------------------------------------------------------------------------------------
# Beige Book html: blocks, District sections
# ------------------------------------------------------------------------------------------------------------------------
class _Blocks(HTMLParser):
    BLOCK = {"p", "div", "li", "ul", "ol", "table", "tr", "td", "th", "blockquote", "section", "article", "header", "footer", "nav", "aside", "br", "hr",
             "form", "dl", "dt", "dd", "figure", "figcaption", "main", "tbody", "thead"}
    EMPH = {"strong", "b", "em", "i"}
    SKIP = {"script", "style", "noscript", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []
        self.buf = []
        self.nonemph = False
        self.emph = 0
        self.skip = 0
        self.hlevel = None
        self.hbuf = []

    def flush(self):
        text = norm_ws("".join(self.buf))
        if text:
            self.items.append(("t", text, not self.nonemph))
        self.buf, self.nonemph = [], False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        if re.fullmatch(r"h[1-6]", tag):
            self.flush()
            self.hlevel, self.hbuf = int(tag[1]), []
        elif tag in self.EMPH:
            self.emph += 1
        elif tag in self.BLOCK:
            self.flush()

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if re.fullmatch(r"h[1-6]", tag):
            if self.hlevel is not None:
                self.items.append(("h", self.hlevel, norm_ws("".join(self.hbuf))))
            self.hlevel, self.hbuf = None, []
        elif tag in self.EMPH:
            self.emph = max(0, self.emph - 1)
        elif tag in self.BLOCK:
            self.flush()

    def handle_data(self, data):
        if self.skip:
            return
        if self.hlevel is not None:
            self.hbuf.append(data)
            return
        self.buf.append(data)
        if data.strip() and self.emph == 0:
            self.nonemph = True

    def close(self):
        super().close()
        self.flush()


def parse_blocks(html_text):
    p = _Blocks()
    p.feed(html_text)
    p.close()
    return p.items


_DIST_ALT = "|".join(re.escape(d) for d in DISTRICTS)
_ORD_ALT = "|".join(ORDINALS)
DIST_HEAD_A = re.compile(r"^(?:%s)\s+District\s*[-–—]+\s*(%s)\s*$" % (_ORD_ALT, _DIST_ALT), re.I)
DIST_HEAD_B = re.compile(r"^(?:Federal Reserve Bank of\s+)*(%s)\s*$" % _DIST_ALT, re.I)   # also the Board's own typos: a doubled prefix (Jan, Apr, Jun 2019) and a bare city name (Mar 2019)


def district_of(heading_text):
    t = norm_ws(heading_text)
    for rx in (DIST_HEAD_A, DIST_HEAD_B):
        m = rx.match(t)
        if m:
            name = m.group(1)
            for d in DISTRICTS:
                if d.lower() == name.lower():
                    return d
    return None


def is_boilerplate(text):
    t = text.lower().strip()
    return t in BB_BOILERPLATE_EXACT or any(t.startswith(p) for p in BB_BOILERPLATE_PREFIX)


def district_sections(items):
    """From parsed blocks: {district: [text segments]}. A section starts at a District heading and ends at the next heading that is a District heading, sits at the
    same or a shallower level, or is in the fixed terminator list. Headings, emphasis-only lines (section titles) and the fixed boilerplate lines are not text."""
    out, cur, cur_level = {}, None, None
    for it in items:
        if it[0] == "h":
            _, lvl, text = it
            d = district_of(text)
            if d is not None:
                cur, cur_level = d, lvl
                out.setdefault(d, [])
                continue
            if cur is not None and (lvl <= cur_level or norm_ws(text).lower() in BB_TERMINATORS):
                cur = None
            continue
        if cur is None:
            continue
        _, text, emph_only = it
        if emph_only or is_boilerplate(text):
            continue
        out[cur].append(text)
    return out


def edition_counts(sections):
    sentences = []
    for d in DISTRICTS:
        for seg in sections.get(d, []):
            sentences.extend(split_sentences(seg))
    return count_sentences(sentences)


def title_date(html_text):
    m = re.search(r"Beige Book\s*-\s*([A-Z][a-z]+ \d{1,2}, \d{4})", html_text)
    if not m:
        return None
    return dt.datetime.strptime(m.group(1), "%B %d, %Y").date()


# ------------------------------------------------------------------------------------------------------------------------
# workbook readers
# ------------------------------------------------------------------------------------------------------------------------
def open_xlsx(path):
    import openpyxl
    with open(path, "rb") as f:
        data = f.read()
    return openpyxl.load_workbook(io.BytesIO(data), data_only=True)


def sheet_rows(wb, name):
    if name not in wb.sheetnames:
        raise DataError("sheet %r missing; sheets are %r" % (name, wb.sheetnames))
    return list(wb[name].iter_rows(values_only=True))


def header_index(rows, first_cell, strip=True):
    for i, r in enumerate(rows):
        c = r[0]
        if isinstance(c, str) and (c.strip() if strip else c) == first_cell:
            return i
    raise DataError("header row %r not found" % first_cell)


def as_ym(v):
    if isinstance(v, (dt.datetime, dt.date)):
        return (v.year, v.month)
    return None


def num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)) and math.isfinite(v):
        return float(v)
    if isinstance(v, str):
        s = v.strip().rstrip("%").replace(",", "")
        try:
            x = float(s)
            return x if math.isfinite(x) else None
        except ValueError:
            return None
    return None


def sbu_unsmoothed(wb):
    """{ym: sales-revenue subjective uncertainty} from the unsmoothed sheet (the sheet name carries a trailing space)."""
    rows = sheet_rows(wb, "Index Values (unsmoothed) ")
    h = header_index(rows, "date")
    col = [str(c).strip() if c is not None else "" for c in rows[h]].index("SalesRevGrowthUnc_percent")
    out = {}
    for r in rows[h + 1:]:
        ym = as_ym(r[0])
        v = num(r[col])
        if ym is not None and v is not None:
            out[ym] = v
    return out


def sbu_realized_spread(wb):
    """({ym: p90 - p10}, rows_with_projection_only) from 'Distrib. of Realized Sales Gr. '. A month is observed when both realised percentiles are numbers."""
    rows = sheet_rows(wb, "Distrib. of Realized Sales Gr. ")
    h = header_index(rows, "date")
    names = [str(c).strip() if c is not None else "" for c in rows[h]]
    c10, c90 = names.index("RealizedSalesGrowth_p10"), names.index("RealizedSalesGrowth_p90")
    post = [i for i, n in enumerate(names) if n.startswith("postline")]
    spread, projected = {}, []
    for r in rows[h + 1:]:
        ym = as_ym(r[0])
        if ym is None:
            continue
        p10, p90 = num(r[c10]), num(r[c90])
        if p10 is not None and p90 is not None:
            spread[ym] = p90 - p10
        elif any(num(r[i]) is not None for i in post):
            projected.append(ym)
    return spread, projected


def sbu_vintage_date(wb):
    for ws in wb.worksheets:
        for r in ws.iter_rows(values_only=True):
            for c in r:
                if isinstance(c, str):
                    m = re.search(r"Last updated:\s*(\d{1,2})/(\d{1,2})/(\d{4})", c)
                    if m:
                        return dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
    return None


def epu_monthly(wb):
    rows = sheet_rows(wb, "Main News Index")
    out = {}
    for r in rows[1:]:
        try:
            y, m = int(str(r[0]).strip()), int(r[1])
        except (TypeError, ValueError):
            continue
        v = num(r[2])
        if v is not None and 1 <= m <= 12:
            out[(y, m)] = v
    return out


def vix_monthly(csv_text_in):
    """{ym: (mean of the daily CLOSE, n trading days)} over every row of that calendar month."""
    sums, ns = {}, {}
    rd = csv.reader(io.StringIO(csv_text_in))
    head = next(rd)
    ci = [h.strip().upper() for h in head].index("CLOSE")
    di = [h.strip().upper() for h in head].index("DATE")
    for r in rd:
        if len(r) <= max(ci, di):
            continue
        m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", r[di].strip())
        v = num(r[ci])
        if not m or v is None:
            continue
        ym = (int(m.group(3)), int(m.group(1)))
        sums[ym] = sums.get(ym, 0.0) + v
        ns[ym] = ns.get(ym, 0) + 1
    return {k: (sums[k] / ns[k], ns[k]) for k in sums}


def quarter_months(q):
    m = re.fullmatch(r"(\d{4})Q([1-4])", str(q).strip())
    if not m:
        return None
    y, qq = int(m.group(1)), int(m.group(2))
    return [(y, 3 * (qq - 1) + k) for k in (1, 2, 3)]


def spf_cpi_dispersion(wb, horizon="T+4"):
    """{ym: D1} where D1 = P75 - P25 of the SPF CPI forecasts for the given horizon, each quarter's value mapped to the three calendar months of that quarter."""
    rows = sheet_rows(wb, "CPI")
    h = header_index(rows, "Survey_Date(T)")
    names = [str(c).strip() if c is not None else "" for c in rows[h]]
    col = names.index("CPI_D1(%s)" % horizon)
    out = {}
    for r in rows[h + 1:]:
        ms = quarter_months(r[0]) if r[0] is not None else None
        v = num(r[col])
        if ms and v is not None:
            for ym in ms:
                out[ym] = v
    return out


def dallas_balances(path):
    """{ym: (inc, dec)} from the not-seasonally-adjusted sheet's uncri and uncrd columns (header match is case-insensitive). Also returns the sheet name."""
    wb = open_xlsx(path)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    names = [str(c).strip().lower() if c is not None else "" for c in rows[0]]
    ci, cd, cu = names.index("uncri"), names.index("uncrd"), names.index("uncr")
    out = {}
    for r in rows[1:]:
        s = str(r[0]).strip() if r[0] is not None else ""
        m = re.fullmatch(r"([A-Za-z]{3})-(\d{2})", s)
        if not m:
            continue
        mon = dt.datetime.strptime(m.group(1), "%b").month
        ym = (2000 + int(m.group(2)), mon)
        i, d, u = num(r[ci]), num(r[cd]), num(r[cu])
        if i is not None and d is not None:
            if u is not None and abs((i - d) - u) > 0.15:
                raise DataError("uncr differs from uncri - uncrd at %s" % ym_text(ym))
            out[ym] = (i, d)
    return out, ws.title


def dmp_sales_uncertainty(wb):
    """{ym: (single month, 3-month average)} from sheet 'Subjective uncertainty', the 'Sales growth uncertainty (%)' block; 'n/a' cells are skipped."""
    rows = sheet_rows(wb, "Subjective uncertainty")
    h = header_index(rows, "Survey date/reference period")
    out = {}
    for r in rows[h + 1:]:
        s = str(r[0]).strip() if r[0] is not None else ""
        m = re.fullmatch(r"([A-Za-z]{3})-(\d{2})", s)
        if not m:
            continue
        ym = (2000 + int(m.group(2)), dt.datetime.strptime(m.group(1), "%b").month)
        out[ym] = (num(r[1]), num(r[2]))
    return out


def dmp_notes_lines(wb):
    out = []
    for name in wb.sheetnames:
        if name.strip() == "Notes":
            for r in wb[name].iter_rows(values_only=True):
                s = " ".join(str(c) for c in r if c not in (None, ""))
                if "standard deviation" in s.lower() and "within firms" in s.lower():
                    out.append(norm_ws(s))
    return out


def btos_series(path, text_start, answers):
    """From a BTOS National workbook: [(smpdt, share_pct or None)] summed over the named answers for the question whose text begins text_start (never by number)."""
    wb = open_xlsx(path)
    sheet = "Response Estimates" if "Response Estimates" in wb.sheetnames else "National Estimates"
    rows = sheet_rows(wb, sheet)
    hdr = rows[0]
    cols = [(i, str(h).strip()) for i, h in enumerate(hdr) if i >= 4 and h is not None and re.fullmatch(r"\d{6}", str(h).strip())]
    pick = [r for r in rows[1:] if r[1] and str(r[1]).startswith(text_start) and str(r[3]).strip() in answers]
    if len(pick) != len(answers):
        raise DataError("expected %d answer rows for %r, found %d" % (len(answers), text_start, len(pick)))
    out = []
    for i, code in cols:
        vals = [num(r[i]) for r in pick]
        out.append((code, sum(vals) if all(v is not None for v in vals) else None))
    return out, sheet


def btos_cycle_dates(path):
    wb = open_xlsx(path)
    rows = sheet_rows(wb, "Collection and Reference Dates")
    out = {}
    for r in rows[1:]:
        if r[3] is None:
            continue
        out[str(r[3]).strip()] = {"start": r[4], "end": r[5], "pub": r[8] if len(r) > 8 else None}
    return out


# ------------------------------------------------------------------------------------------------------------------------
# network (fetch only)
# ------------------------------------------------------------------------------------------------------------------------
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def reg_domain(host):
    return ".".join(host.split(".")[-2:])


class Fetcher:
    def __init__(self, cache_dir, say=print):
        self.cache = cache_dir
        self.say = say
        self.last = {}
        self.opener = urllib.request.build_opener(_NoRedirect)
        self.log_path = os.path.join(cache_dir, "fetch_log.csv")
        self.n_requests = 0

    def stop_path(self, host):
        return os.path.join(self.cache, "STOP_cv1_" + host)

    def _wait(self, host):
        gap = 0.65 if host == FED_HOST else 1.1
        t = self.last.get(host)
        if t is not None:
            d = gap - (time.monotonic() - t)
            if d > 0:
                time.sleep(d)
        self.last[host] = time.monotonic()

    def _log(self, url, status, nbytes, digest, dest):
        new = not os.path.exists(self.log_path)
        with open(self.log_path, "a", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            if new:
                w.writerow(["utc_time", "url", "http_status", "bytes", "sha256", "file"])
            w.writerow([dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), url, status, nbytes, digest, dest])

    def get(self, url, dest, min_bytes=1, must_start=None):
        """Returns True if the file now exists in the cache. Existing files are never re-requested."""
        if os.path.exists(dest) and os.path.getsize(dest) >= min_bytes:
            return True
        cur, hops = url, 0
        while True:
            host = urllib.parse.urlsplit(cur).hostname
            if os.path.exists(self.stop_path(host)):
                raise Stopped("STOP latch exists for %s; no request is made" % host)
            attempts = 0
            while True:
                self._wait(host)
                self.n_requests += 1
                req = urllib.request.Request(cur, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
                status, body, loc = None, b"", None
                try:
                    with self.opener.open(req, timeout=120) as resp:
                        status, body = resp.status, resp.read()
                except urllib.error.HTTPError as e:
                    status, loc = e.code, e.headers.get("Location")
                    try:
                        body = e.read()[:2000]
                    except Exception:
                        body = b""
                except (urllib.error.URLError, TimeoutError, OSError) as e:
                    self._log(cur, "NETERR " + type(e).__name__, 0, "", "")
                    self.say("network error for %s: %s" % (cur, type(e).__name__))
                    return False
                if status in (403, 429):
                    self._log(cur, status, len(body), "", "")
                    attempts += 1
                    if attempts == 1:
                        self.say("HTTP %s from %s; one retry after ten seconds" % (status, host))
                        time.sleep(10)
                        continue
                    with open(self.stop_path(host), "x", encoding="utf-8") as f:
                        f.write("status: %s\nhost: %s\nurl: %s\nutc_time: %s\n" % (status, host, cur, dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")))
                    raise Stopped("HTTP %s twice from %s: STOP latch written, host abandoned" % (status, host))
                break
            if status in (301, 302, 303, 307, 308) and loc:
                nxt = urllib.parse.urljoin(cur, loc)
                self._log(cur, status, 0, "", "redirect to " + nxt)
                if hops >= 2 or reg_domain(urllib.parse.urlsplit(nxt).hostname or "") != reg_domain(host):
                    self.say("redirect from %s to %s not followed" % (cur, nxt))
                    return False
                hops += 1
                cur = nxt
                continue
            if status != 200:
                self._log(cur, status, len(body), "", "")
                self.say("HTTP %s for %s" % (status, cur))
                return False
            if len(body) < min_bytes or (must_start is not None and not body.startswith(must_start)):
                self._log(cur, status, len(body), sha256_bytes(body), "REJECTED body")
                self.say("body of %s is not the expected kind (%d bytes); not saved" % (cur, len(body)))
                return False
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(body)
            self._log(cur, status, len(body), sha256_bytes(body), os.path.relpath(dest, self.cache))
            return True


FIXED_SOURCES = [
    # key, url, file name in raw/, minimum bytes, required first bytes
    ("sbu", "https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/research-and-data/surveys/business-uncertainty/sbu-data.xlsx", "sbu-data.xlsx", 20000, b"PK"),
    ("epu", "https://www.policyuncertainty.com/media/US_Policy_Uncertainty_Data.xlsx", "US_Policy_Uncertainty_Data.xlsx", 20000, b"PK"),
    ("vix", "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv", "VIX_History.csv", 100000, b"DATE"),
    ("spf", "https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/survey-of-professional-forecasters/historical-data/Dispersion_1.xlsx", "Dispersion_1.xlsx", 100000, b"PK"),
    ("dallas", "https://www.dallasfed.org/~/media/Documents/research/surveys/tmos/documents/alldata.xls", "tmos_alldata.xls", 50000, b"PK"),
    ("dallas", "https://www.dallasfed.org/~/media/Documents/research/surveys/tssos/documents/tssos_alldata.xls", "tssos_alldata.xls", 50000, b"PK"),
    ("dmp", "https://www.bankofengland.co.uk/-/media/boe/files/decision-maker-panel-survey/2026/monthly-dmp-data-october-2026.xlsx", "monthly-dmp-data-october-2026.xlsx", 50000, b"PK"),
    ("btos", "https://www.census.gov/hfp/btos/downloads/National.xlsx", "National.xlsx", 50000, b"PK"),
    ("btos", "https://www.census.gov/hfp/btos/downloads/AI%20Core%20Questions.xlsx", "AI_Core_Questions_original.xlsx", 100000, b"PK"),
    ("btos", "https://www.census.gov/hfp/btos/downloads/AI%20Question%20Wording%20Updates.pdf", "AI_Question_Wording_Updates.pdf", 10000, b"%PDF"),
]


def beige_index_url(year):
    if year >= 2026:
        return "https://%s/monetarypolicy/publications/beige-book-default.htm" % FED_HOST
    return "https://%s/monetarypolicy/beigebook%d.htm" % (FED_HOST, year)


_PAGE_RX = re.compile(r"""href="(?:https://www\.federalreserve\.gov)?(/monetarypolicy/(?:beigebook/)?beigebook(\d{6,8})(-summary)?\.htm)\"""", re.I)
_PDF_RX = re.compile(r"BeigeBook_(\d{8})\.pdf", re.I)


def discover_editions(year, index_html):
    """From a year's index page: [{'code', 'summary', 'path'}] for that year, in code order, and the PDF release dates listed for the year."""
    seen, eds = set(), []
    for m in _PAGE_RX.finditer(index_html):
        path, code, summ = m.group(1), m.group(2), bool(m.group(3))
        if not code.startswith(str(year)) or code in seen:
            continue
        seen.add(code)
        eds.append({"code": code, "summary": summ, "path": path})
    eds.sort(key=lambda e: e["code"])
    pdfs = sorted({dt.datetime.strptime(d, "%Y%m%d").date() for d in _PDF_RX.findall(index_html) if d.startswith(str(year))})
    return eds, pdfs


def edition_pages(ed):
    """(local file name, url path) for each page that holds the Districts' text."""
    if not ed["summary"]:
        return [("beigebook%s.html" % ed["code"], ed["path"])]
    out = []
    for d in DISTRICTS:
        out.append(("beigebook%s-%s.html" % (ed["code"], DISTRICT_SLUGS[d]), ed["path"].replace("-summary.htm", "-%s.htm" % DISTRICT_SLUGS[d])))
    return out


def run_fetch(args, say=print):
    cache = os.path.join(ROOT, CACHE_REL)
    raw = os.path.join(cache, "raw")
    bb = os.path.join(raw, "beige")
    os.makedirs(bb, exist_ok=True)
    gi = os.path.join(cache, ".gitignore")
    if not os.path.exists(gi):
        with open(gi, "w", encoding="utf-8") as f:
            f.write("*\n")
    only = set(args.only.split(",")) if args.only else None
    f = Fetcher(cache, say)
    t0 = time.monotonic()
    failures = []

    def over():
        return args.max_seconds and time.monotonic() - t0 > args.max_seconds

    try:
        for key, url, name, minb, start in FIXED_SOURCES:
            if only and key not in only:
                continue
            ok = f.get(url, os.path.join(raw, name), minb, start)
            say("%-6s %-40s %s" % (key, name, "ok" if ok else "FAILED"))
            if not ok:
                failures.append(name)
        if not only or "beige" in only:
            pending = 0
            for year in range(BEIGE_FIRST.year, BEIGE_LAST.year + 1):
                idx = os.path.join(bb, "index_%d.html" % year)
                if over():
                    pending += 1
                    continue
                if not f.get(beige_index_url(year), idx, 5000):
                    failures.append("index_%d" % year)
                    continue
                eds, pdfs = discover_editions(year, open(idx, encoding="utf-8", errors="replace").read())
                for ed in eds:
                    for fname, path in edition_pages(ed):
                        dest = os.path.join(bb, fname)
                        if os.path.exists(dest):
                            continue
                        if over():
                            pending += 1
                            continue
                        if not f.get("https://%s%s" % (FED_HOST, path), dest, 5000):
                            failures.append(fname)
            say("beige: %d pages/indexes still pending; requests this run: %d" % (pending, f.n_requests))
            if pending:
                say("TIME BUDGET REACHED: run fetch again to resume (cached files are not re-requested)")
    except Stopped as e:
        say("STOP: %s" % e)
        return 2
    if failures:
        say("FAILED: %s" % ", ".join(failures))
        return 3
    return 0


# ------------------------------------------------------------------------------------------------------------------------
# build
# ------------------------------------------------------------------------------------------------------------------------
def paths():
    cache = os.path.join(ROOT, CACHE_REL)
    return {"cache": cache, "raw": os.path.join(cache, "raw"), "bb": os.path.join(cache, "raw", "beige"), "out": os.path.join(ROOT, OUT_REL)}


RAW_FILES = {
    "sbu": "sbu-data.xlsx", "epu": "US_Policy_Uncertainty_Data.xlsx", "vix": "VIX_History.csv", "spf": "Dispersion_1.xlsx", "tmos": "tmos_alldata.xls",
    "tssos": "tssos_alldata.xls", "dmp": "monthly-dmp-data-october-2026.xlsx", "btos": "National.xlsx", "btos_orig": "AI_Core_Questions_original.xlsx",
    "btos_pdf": "AI_Question_Wording_Updates.pdf",
}


def input_hashes(P):
    h = {}
    for k, name in RAW_FILES.items():
        p = os.path.join(P["raw"], name)
        if not os.path.exists(p):
            raise DataError("missing input %s; run fetch" % name)
        h[name] = sha256_file(p)
    files = sorted(n for n in os.listdir(P["bb"]) if n.endswith(".html"))
    lines = "".join("%s %s\n" % (n, sha256_file(os.path.join(P["bb"], n))) for n in files)
    h["beige_pages(%d files)" % len(files)] = sha256_bytes(lines.encode())
    return h


REG_HEADER = ["statement_id", "version", "labelled", "support_if", "against_if", "baseline_window", "treatment_window", "controls", "input_files", "input_sha256", "prereg_sha256"]


def registered_rows(hashes):
    def ins(*names):
        pick = [(k, v) for k, v in hashes.items() if any(k.startswith(n) for n in names)]
        return ";".join(k for k, _ in pick), ";".join(v for _, v in pick)

    rows = []
    f, s = ins("sbu-data", "US_Policy", "VIX_History", "Dispersion_1")
    rows.append(["CV1-S1", "2", "yes", "effect size <= -0.5", "effect size >= 0", "2016-12..2019-12", "2023-01..2025-12",
                 "log monthly 10-paper EPU (Main News Index); log monthly mean VIX close; log SPF one-year (T+4) CPI forecast dispersion D1; Treatment dummy", f, s, PREREG_SHA256])
    rows.append(["CV1-S4", "2", "only if CV1-S1 v2 is SUPPORT", "R_T <= 0.9 * R_B", "R_T >= R_B", "2016-12..2019-12", "2024-01..2025-12", "none (window ratio of means)",
                 ins("sbu-data")[0], ins("sbu-data")[1], PREREG_SHA256])
    f, s = ins("beige_pages")
    rows.append(["CV1-S2", "2", "no (descriptive)", "none", "none", "editions 2015-01..2026-10", "same table", "none", f, s, PREREG_SHA256])
    f, s = ins("tmos", "tssos")
    rows.append(["CV1-S3", "2", "no (descriptive)", "none", "none", "2018-01..2026-10", "same table", "none", f, s, PREREG_SHA256])
    f, s = ins("monthly-dmp")
    rows.append(["CV1-S5", "2", "no (descriptive)", "none", "none", "2017-01..2019-12", "2023-01..2025-12", "none", f, s, PREREG_SHA256])
    f, s = ins("National.xlsx", "AI_Core", "AI_Question")
    rows.append(["CV1-S6", "2", "no (descriptive)", "none", "none", "none (no pre-AI baseline)", "all published cycles", "none", f, s, PREREG_SHA256])
    return rows


def write_registered(P, hashes):
    path = os.path.join(P["out"], "registered.csv")
    if os.path.exists(path):
        old = list(csv.DictReader(l for l in open(path, encoding="utf-8", newline="") if not l.startswith("# ")))
        new = registered_rows(hashes)
        for o, n in zip(old, new):
            if o["input_sha256"] != n[REG_HEADER.index("input_sha256")] or o["prereg_sha256"] != PREREG_SHA256:
                raise Refused("registered.csv exists and its frozen input hashes differ from the cache for %s; refusing to score" % o["statement_id"])
        return "kept"
    write_text(path, csv_text(REG_HEADER, registered_rows(hashes), ["source: CV1 stage 2 v2 registration of 13 Nov 2026; one row per statement; input hashes are of the frozen raw files, written before any statistic is computed"]))
    return "written"


def window_months(w):
    return months_between(w[0], w[1])


def s1_panel(sbu, epu, vix, spf, base, treat):
    rows, missing = [], []
    for treated, w in ((0, base), (1, treat)):
        for ym in window_months(w):
            y, e, v, s = sbu.get(ym), epu.get(ym), vix.get(ym), spf.get(ym)
            if None in (y, e, v, s):
                missing.append((ym_text(ym), [n for n, x in (("sbu", y), ("epu", e), ("vix", v), ("spf", s)) if x is None]))
                continue
            vm = v[0]
            if e <= 0 or vm <= 0 or s <= 0:
                raise DataError("a control is not positive at %s, so its log is undefined" % ym_text(ym))
            rows.append({"ym": ym, "treat": treated, "y": y, "epu": e, "vix": vm, "vix_days": v[1], "spf": s})
    return rows, missing


def s1_result(rows):
    beta, resid, base_resid = s1_fit(rows)
    nb = sum(1 for r in rows if not r["treat"])
    nt = len(rows) - nb
    sd1, sd0 = stdev(base_resid, 1), stdev(base_resid, 0)
    return {"a": beta[0], "b1": beta[1], "b2": beta[2], "b3": beta[3], "d": beta[4], "sd_ddof1": sd1, "sd_ddof0": sd0, "eff": beta[4] / sd1, "eff0": beta[4] / sd0,
            "n_base": nb, "n_treat": nt, "label": s1_label(beta[4] / sd1)}


def s4_window(num_series, spread, window, ok=None):
    ms = [ym for ym in window_months(window) if ym in num_series and ym in spread and (ok is None or ok(ym))]
    n, d = [num_series[ym] for ym in ms], [spread[ym] for ym in ms]
    return {"n": len(ms), "months": ms, "mean_num": mean(n), "mean_den": mean(d), "R": ratio_of_means(n, d), "expected": len(window_months(window))}


def build_s2(P):
    rows, problems = [], []
    index_files = sorted(n for n in os.listdir(P["bb"]) if n.startswith("index_"))
    for n in index_files:
        year = int(re.search(r"(\d{4})", n).group(1))
        idx = open(os.path.join(P["bb"], n), encoding="utf-8", errors="replace").read()
        eds, pdfs = discover_editions(year, idx)
        single = [e for e in eds if not e["summary"]]
        dists = [e for e in eds if e["summary"]]
        if dists:
            if len(pdfs) != len(dists):
                problems.append("%d: %d summary pages but %d release dates on the index; not paired" % (year, len(dists), len(pdfs)))
                continue
            dated = list(zip(dists, pdfs))
        else:
            dated = [(e, None) for e in single]
        for ed, rel in dated:
            secs, ok = {}, True
            for fname, _ in edition_pages(ed):
                p = os.path.join(P["bb"], fname)
                if not os.path.exists(p):
                    problems.append("%s: page missing" % fname)
                    ok = False
                    continue
                text = open(p, encoding="utf-8", errors="replace").read()
                if rel is None:
                    td = title_date(text)
                    if td is None:
                        problems.append("%s: no edition date in the title" % fname)
                        ok = False
                        continue
                    rel = td
                for d, segs in district_sections(parse_blocks(text)).items():
                    secs.setdefault(d, []).extend(segs)
            if not ok:
                continue
            if rel < BEIGE_FIRST or rel > BEIGE_LAST:
                continue
            found = [d for d in DISTRICTS if secs.get(d)]
            if len(found) != 12:
                problems.append("%s: %d of 12 District sections found (%s missing)" % (ed["code"], len(found), ",".join(d for d in DISTRICTS if d not in found)))
                continue
            n, a, b = edition_counts(secs)
            rows.append({"date": rel, "code": ed["code"], "fmt": "district_pages" if ed["summary"] else "single_page", "n_dist": len(found), "n": n, "a": a, "b": b})
    rows.sort(key=lambda r: r["date"])
    return rows, problems


def s6_series(P):
    cur = os.path.join(P["raw"], RAW_FILES["btos"])
    orig = os.path.join(P["raw"], RAW_FILES["btos_orig"])
    dates = btos_cycle_dates(cur)
    forecast, _ = btos_series(cur, "Thinking about the future performance of this business", ("Difficult to forecast future performance", "Very difficult to forecast future performance"))
    ai_cur, _ = btos_series(cur, "In the last two weeks, did this business use", ("Yes",))
    ai_orig, _ = btos_series(orig, "In the last two weeks, did this business use Artificial Intelligence (AI) in producing goods or services", ("Yes",))
    return dates, forecast, ai_cur, ai_orig


SI_WORDING_START = dt.datetime(2026, 10, 19)
BF_WORDING_START = dt.datetime(2025, 11, 17)


def tidy_date(v):
    if isinstance(v, (dt.datetime, dt.date)):
        return v.strftime("%Y-%m-%d")
    return ""


def run_build(args, say=print):
    P = paths()
    spec_path = os.path.join(ROOT, SPEC_FILE)
    got = sha256_file(spec_path)
    if got != PREREG_SHA256:
        raise Refused("the spec file hashes to %s, not the pinned %s; build refuses to score" % (got, PREREG_SHA256))
    hashes = input_hashes(P)
    state = write_registered(P, hashes)
    say("registered.csv %s (before any statistic; %d inputs hashed)" % (state, len(hashes)))
    out = P["out"]
    notes = []

    # ---- inputs
    sbu_wb = open_xlsx(os.path.join(P["raw"], RAW_FILES["sbu"]))
    sbu = sbu_unsmoothed(sbu_wb)
    spread, projected = sbu_realized_spread(sbu_wb)
    vintage = sbu_vintage_date(sbu_wb)
    epu = epu_monthly(open_xlsx(os.path.join(P["raw"], RAW_FILES["epu"])))
    vix = vix_monthly(open(os.path.join(P["raw"], RAW_FILES["vix"]), encoding="utf-8", errors="replace").read())
    spf_wb = open_xlsx(os.path.join(P["raw"], RAW_FILES["spf"]))
    spf = spf_cpi_dispersion(spf_wb, "T+4")

    # ---- S1 v2
    rows, missing = s1_panel(sbu, epu, vix, spf, S1_BASE, S1_TREAT)
    s1 = None
    if missing:
        say("S1 STOPPED: months with a missing input: %r" % missing)
        notes.append("S1 NOT BUILT: months with a missing input %r" % missing)
    else:
        s1 = s1_result(rows)
        panel = csv_text(["month", "treatment", "sbu_unc_unsmoothed", "epu_main_news", "vix_close_monthly_mean", "vix_trading_days", "spf_cpi_D1_Tplus4"],
                         [[ym_text(r["ym"]), r["treat"], fmt(r["y"], 4), fmt(r["epu"], 4), fmt(r["vix"], 4), r["vix_days"], fmt(r["spf"], 4)] for r in rows])
        os.makedirs(P["cache"], exist_ok=True)
        with open(os.path.join(P["cache"], "s1_panel.csv"), "w", encoding="utf-8", newline="") as f:
            f.write(panel)
        say("S1: N base=%d treat=%d, effect size %.4f, label %s" % (s1["n_base"], s1["n_treat"], s1["eff"], s1["label"]))

    # ---- S4 v2
    s4 = None
    sens = []
    if sbu and spread:
        wb_, wt_ = s4_window(sbu, spread, S4_BASE), s4_window(sbu, spread, S4_TREAT)
        s1l = s1["label"] if s1 else "NOT_BUILT"
        s4 = {"B": wb_, "T": wt_, "label": s4_label(wt_["R"], wb_["R"], s1l), "ratio": wt_["R"] / wb_["R"]}
        cutoff = month_index((vintage.year, vintage.month)) - 12 if vintage else None
        ok12 = (lambda ym: month_index(ym) <= cutoff) if cutoff is not None else None
        wb12, wt12 = s4_window(sbu, spread, S4_BASE, ok12), s4_window(sbu, spread, S4_TREAT, ok12)
        s4["alt12"] = {"B": wb12, "T": wt12, "ratio": wt12["R"] / wb12["R"]}
        say("S4: R_B=%.4f R_T=%.4f label %s" % (wb_["R"], wt_["R"], s4["label"]))

    # ---- scores.csv and sensitivity.csv
    score_rows = []
    if s1:
        nb, nt = s1["n_base"], s1["n_treat"]
        for item, key, note in (("coef_a_constant", "a", ""), ("coef_b1_log_epu", "b1", ""), ("coef_b2_log_vix", "b2", ""), ("coef_b3_log_spf_cpi_dispersion", "b3", ""),
                                ("coef_d_treatment", "d", "")):
            score_rows.append(["CV1-S1 v2", item, fmt(s1[key]), nb, nt, note])
        score_rows.append(["CV1-S1 v2", "baseline_residual_sd_ddof1", fmt(s1["sd_ddof1"]), nb, nt, "sample SD (n-1) of the residuals in the %d baseline months, residuals from the full regression" % nb])
        score_rows.append(["CV1-S1 v2", "effect_size", fmt(s1["eff"]), nb, nt, "d / baseline residual SD"])
        score_rows.append(["CV1-S1 v2", "label", s1["label"], nb, nt, "SUPPORT if effect size <= -0.5; AGAINST if >= 0; else INCONCLUSIVE"])
    else:
        score_rows.append(["CV1-S1 v2", "label", "NOT_BUILT", "", "", "; ".join(notes)])
    if s4:
        B, T = s4["B"], s4["T"]
        for item, v in (("mean_numerator_baseline", B["mean_num"]), ("mean_denominator_baseline", B["mean_den"]), ("R_B", B["R"]),
                        ("mean_numerator_treatment", T["mean_num"]), ("mean_denominator_treatment", T["mean_den"]), ("R_T", T["R"]), ("R_T_over_R_B", s4["ratio"])):
            score_rows.append(["CV1-S4 v2", item, fmt(v), B["n"], T["n"], ""])
        score_rows.append(["CV1-S4 v2", "label", s4["label"], B["n"], T["n"], "labelled only if CV1-S1 v2 is SUPPORT; SUPPORT if R_T <= 0.9 R_B; AGAINST if R_T >= R_B"])
    write_text(os.path.join(out, "scores.csv"), csv_text(["statement_id", "item", "value", "n_baseline_months", "n_treatment_months", "note"], score_rows,
                                                           ["source: bin/cv1_stage2_uncertainty.py build; SBU workbook vintage %s; inputs hashed in registered.csv" % (vintage.isoformat() if vintage else "unknown")]))

    if s1:
        for h in ("T", "T+1", "T+2", "T+3", "T+4"):
            sp = spf_cpi_dispersion(spf_wb, h)
            rr, miss = s1_panel(sbu, epu, vix, sp, S1_BASE, S1_TREAT)
            if miss:
                sens.append(["CV1-S1 v2", "spf_horizon_%s" % h, "", "", "", "months missing: %r" % miss])
                continue
            r = s1_result(rr)
            sens.append(["CV1-S1 v2", "spf_horizon_%s%s" % (h, " (registered)" if h == "T+4" else ""), fmt(r["eff"]), r["n_base"], r["n_treat"], "effect size with the SPF dispersion taken at this horizon; %s" % ("this is the registered horizon (same as scores.csv)" if h == "T+4" else "a non-registered variant, no label")])
        sens.append(["CV1-S1 v2", "sd_ddof0 (population SD of baseline residuals)", fmt(s1["eff0"]), s1["n_base"], s1["n_treat"], "effect size using n instead of n-1"])
    if s4:
        a = s4["alt12"]
        sens.append(["CV1-S4 v2", "R_B_under_12_month_rule", fmt(a["B"]["R"]), a["B"]["n"], a["T"]["n"], "denominator months restricted to at least 12 months before the workbook's last-updated date"])
        sens.append(["CV1-S4 v2", "R_T_under_12_month_rule", fmt(a["T"]["R"]), a["B"]["n"], a["T"]["n"], "same restriction; treatment loses the months after 2025-10"])
        sens.append(["CV1-S4 v2", "R_T_over_R_B_under_12_month_rule", fmt(a["ratio"]), a["B"]["n"], a["T"]["n"], "reported for transparency; the registered rule is the one in scores.csv"])
    write_text(os.path.join(out, "sensitivity.csv"), csv_text(["statement_id", "variant", "value", "n_baseline_months", "n_treatment_months", "note"], sens,
                                                                ["source: non-registered variants, printed for transparency only; none carries a label"]))

    # ---- S2
    s2rows, s2problems = build_s2(P)
    s2_text = csv_text(["edition_date", "release_month", "page_code", "page_format", "after_2017_01_18_redesign", "n_district_sections", "n_sentences", "n_dictionary_a", "n_dictionary_b",
                        "rate_a_per_1000", "rate_b_per_1000"],
                       [[r["date"].isoformat(), r["date"].strftime("%Y-%m"), r["code"], r["fmt"], "yes" if r["date"] >= BEIGE_FORMAT_CHANGE else "no", r["n_dist"], r["n"], r["a"], r["b"],
                         fmt(per_1000(r["a"], r["n"]), 4), fmt(per_1000(r["b"], r["n"]), 4)] for r in s2rows],
                       ["source: Federal Reserve Board Beige Book pages (public domain); twelve District texts pooled per edition; the national summary is excluded; no residualising; no label",
                        "dictionaries: (a) whole word uncertain|uncertainty|uncertainties; (b) (a) minus sentences with a whole word or phrase of the registered exclusion list; the 18 Jan 2017 redesign is flagged in column 5"])
    write_text(os.path.join(out, "s2_beigebook_editions.csv"), s2_text)

    # ---- S3
    tm, tm_sheet = dallas_balances(os.path.join(P["raw"], RAW_FILES["tmos"]))
    ts, ts_sheet = dallas_balances(os.path.join(P["raw"], RAW_FILES["tssos"]))
    allm = sorted(set(tm) | set(ts))
    def cells(d, ym):
        if ym not in d:
            return ["", "", ""]
        i, dd = d[ym]
        return [fmt(i, 1), fmt(dd, 1), fmt(i - dd, 1)]

    s3_text = csv_text(["month", "tmos_uncri", "tmos_uncrd", "tmos_uncri_minus_uncrd", "tssos_uncri", "tssos_uncrd", "tssos_uncri_minus_uncrd"],
                       [[ym_text(ym)] + cells(tm, ym) + cells(ts, ym) for ym in allm],
                       ["source: Dallas Fed Texas Manufacturing Outlook Survey and Texas Service Sector Outlook Survey, not-seasonally-adjusted sheets %s and %s of the frozen vintage" % (tm_sheet, ts_sheet),
                        "caption: negative = more firms said uncertainty fell this month than rose (a month-on-month change question); not averaged, not residualised, not compared with 2018-2019 as a level; no label"])
    write_text(os.path.join(out, "s3_dallas_uncertainty.csv"), s3_text)

    # ---- S5
    dmp_wb = open_xlsx(os.path.join(P["raw"], RAW_FILES["dmp"]))
    dmp = dmp_sales_uncertainty(dmp_wb)
    dmp_notes = dmp_notes_lines(dmp_wb)
    s5_rows = []
    s5_ratio = {}
    if dmp_notes:
        for pos, label in ((0, "single_month"), (1, "three_month_average")):
            vb = [dmp[ym][pos] for ym in window_months(S5_BASE) if ym in dmp and dmp[ym][pos] is not None]
            vt = [dmp[ym][pos] for ym in window_months(S5_TREAT) if ym in dmp and dmp[ym][pos] is not None]
            if vb and vt:
                s5_ratio[label] = (mean(vt) / mean(vb), len(vb), len(vt), mean(vb), mean(vt))
                s5_rows.append([label, "2017-01..2019-12", len(vb), fmt(mean(vb), 4), "2023-01..2025-12", len(vt), fmt(mean(vt), 4), fmt(mean(vt) / mean(vb), 4)])
    else:
        s5_rows.append(["not in the free monthly file", "", "", "", "", "", "", ""])
    s5_text = csv_text(["series", "baseline_window", "n_baseline_months", "baseline_mean_pct", "treatment_window", "n_treatment_months", "treatment_mean_pct", "ratio_treatment_to_baseline"], s5_rows,
                       ["source: Bank of England Decision Maker Panel monthly workbook, sheet Subjective uncertainty, block Sales growth uncertainty (%); no label",
                        "caveat: this comparison mixes Brexit, the UK energy shock and carried-forward scenario answers, and is not in US residual units"])
    write_text(os.path.join(out, "s5_boe_dmp.csv"), s5_text)

    # ---- S6
    dates, forecast, ai_cur, ai_orig = s6_series(P)
    s6_rows = []
    for code, v in forecast:
        d = dates.get(code, {})
        s6_rows.append(["difficult_or_very_difficult_to_forecast", "question text begins: Thinking about the future performance of this business", code, tidy_date(d.get("start")), tidy_date(d.get("end")), tidy_date(d.get("pub")), fmt(v, 1) if v is not None else "not asked"])
    for code, v in ai_orig:
        if v is None:
            continue
        d = dates.get(code, {})
        s6_rows.append(["ai_use_original_wording", "in producing goods or services (Census original series, to 2025-10-05)", code, "", "", "", fmt(v, 1)])
    for code, v in ai_cur:
        if v is None:
            continue
        d = dates.get(code, {})
        start = d.get("start")
        line = "ai_use_super_intelligence_wording" if isinstance(start, dt.datetime) and start >= SI_WORDING_START else "ai_use_business_functions_wording"
        desc = "Super Intelligence (formerly AI) wording from 2026-10-19" if line.endswith("super_intelligence_wording") else "AI, in any of its business functions (Census series from 2025-12-04)"
        s6_rows.append([line, desc, code, tidy_date(start), tidy_date(d.get("end")), tidy_date(d.get("pub")), fmt(v, 1)])
    s6_text = csv_text(["line", "wording", "cycle_smpdt", "collection_start", "collection_end", "publication_date", "share_pct"], s6_rows,
                       ["source: Census Bureau Business Trends and Outlook Survey national workbook and its AI Core (original) workbook; lines are never spliced, never correlated, and not referred to by question number; no label"])
    write_text(os.path.join(out, "s6_btos.csv"), s6_text)

    # ---- README
    write_text(os.path.join(out, "README.md"), readme_text(P, hashes, vintage, s1, s4, rows, missing, s2rows, s2problems, tm, ts, tm_sheet, ts_sheet, dmp, dmp_notes, s5_ratio, forecast, ai_orig, ai_cur, dates, projected, sens))
    say("wrote %s" % OUT_REL)
    return 0 if not s2problems and s1 else 4


def readme_text(P, hashes, vintage, s1, s4, rows, missing, s2rows, s2problems, tm, ts, tm_sheet, ts_sheet, dmp, dmp_notes, s5_ratio, forecast, ai_orig, ai_cur, dates, projected, sens):
    L = []
    A = L.append
    fmtlog = {}
    lp = os.path.join(P["cache"], "fetch_log.csv")
    if os.path.exists(lp):
        for r in csv.DictReader(open(lp, encoding="utf-8", newline="")):
            if r["http_status"] == "200" and r["file"]:
                fmtlog[os.path.basename(r["file"])] = (r["utc_time"], r["url"])
    A("# CV1 stage 2 v2: did managers' perceived uncertainty fall? Aggregate proxies, build output")
    A("")
    A("Specification: `%s` (section Version 2, binding). Its sha256, pinned in `bin/cv1_stage2_uncertainty.py` and in `bin/check.sh` (M31), is `%s`; `build` refuses to score if the file differs." % (SPEC_FILE, PREREG_SHA256))
    A("Built by `python3 bin/cv1_stage2_uncertainty.py build` from raw files frozen in the ignored cache `%s/raw/`. `registered.csv` was written before any statistic was computed." % CACHE_REL)
    A("")
    A("What these numbers can and cannot show: an aggregate series cannot attribute a change to AI. Only CV1-S1 v2 and CV1-S4 v2 carry labels. SUPPORT means consistent, not attributed. S2, S3, S5 and S6 are descriptive: none may be read as supporting or weakening stage 2.")
    A("")
    A("## Labelled statements")
    A("")
    if s1:
        A("### CV1-S1 v2")
        A("")
        A("Y = a + b1 log(EPU) + b2 log(VIX) + b3 log(SPF dispersion) + d Treatment + e, OLS, N = %d months (baseline Dec 2016 to Dec 2019: %d; treatment Jan 2023 to Dec 2025: %d)." % (len(rows), s1["n_base"], s1["n_treat"]))
        A("")
        A("| a | b1 (log EPU) | b2 (log VIX) | b3 (log SPF) | d | baseline residual SD (n-1, N=%d) | effect size d / SD | label |" % s1["n_base"])
        A("|---|---|---|---|---|---|---|---|")
        A("| %.4f | %.4f | %.4f | %.4f | %.4f | %.4f | %.4f | %s |" % (s1["a"], s1["b1"], s1["b2"], s1["b3"], s1["d"], s1["sd_ddof1"], s1["eff"], s1["label"]))
    else:
        A("### CV1-S1 v2: NOT BUILT")
        A("")
        A("Months with a missing input: %r" % (missing,))
    A("")
    if s4:
        B, T = s4["B"], s4["T"]
        A("### CV1-S4 v2")
        A("")
        A("Numerator: unsmoothed `SalesRevGrowthUnc_percent`; denominator: `RealizedSalesGrowth_p90` minus `_p10`, observed rows only. R is the ratio of window means. N months baseline %d of %d, treatment %d of %d." % (B["n"], B["expected"], T["n"], T["expected"]))
        A("")
        A("| window | N months | mean numerator | mean denominator | R |")
        A("|---|---|---|---|---|")
        A("| baseline Dec 2016 to Dec 2019 | %d | %.4f | %.4f | %.4f |" % (B["n"], B["mean_num"], B["mean_den"], B["R"]))
        A("| treatment Jan 2024 to Dec 2025 | %d | %.4f | %.4f | %.4f |" % (T["n"], T["mean_num"], T["mean_den"], T["R"]))
        A("")
        A("R_T / R_B = %.4f. Label: **%s**%s." % (s4["ratio"], s4["label"], " (the statement is labelled only if CV1-S1 v2 is SUPPORT, and it is not)" if s4["label"].startswith("UNLABELLED") else ""))
        a = s4["alt12"]
        A("")
        A("Under the spec's fall-back rule for a sheet with no observed/projected flag (months at least 12 months before the workbook's last-updated date, %s), R_B = %.4f (N=%d) and R_T = %.4f (N=%d); this variant is printed in `sensitivity.csv` only." % (vintage.isoformat() if vintage else "unknown", a["B"]["R"], a["B"]["n"], a["T"]["R"], a["T"]["n"]))
    A("")
    A("## Descriptive outputs (no label)")
    A("")
    A("- `s2_beigebook_editions.csv`: %d editions from %s to %s; per edition the sentence count of the twelve District texts, the dictionary (a) and (b) counts and their rates per 1,000 sentences. %d editions could not be parsed: %s." % (
        len(s2rows), s2rows[0]["date"].isoformat() if s2rows else "-", s2rows[-1]["date"].isoformat() if s2rows else "-", len(s2problems), "; ".join(s2problems) if s2problems else "none"))
    nt = [m for m in tm if (2018, 1) <= m]
    A("- `s3_dallas_uncertainty.csv`: not-seasonally-adjusted `uncri - uncrd` by month, TMOS (%d months) and TSSOS (%d months) separately, sheets `%s` and `%s`. Negative = more firms said uncertainty fell this month than rose." % (len(tm), len(ts), tm_sheet, ts_sheet))
    if s5_ratio:
        for k, (r, nb, nt_, mb, mt) in s5_ratio.items():
            A("- `s5_boe_dmp.csv` (%s): Jan 2023 to Dec 2025 mean %.4f (N=%d months) over Jan 2017 to Dec 2019 mean %.4f (N=%d months) = ratio %.4f. This comparison mixes Brexit, the UK energy shock and carried-forward answers; it is not in US residual units." % (k, mt, nt_, mb, nb, r))
    else:
        A("- `s5_boe_dmp.csv`: not in the free monthly file.")
    nf = [v for _, v in forecast if v is not None]
    A("- `s6_btos.csv`: forecast-difficulty share (difficult or very difficult): %d cycle(s) with a value out of %d in the free national workbook; AI use, original wording: %d cycles; AI use, current workbook: %d cycles with a value. Lines are never spliced." % (
        len(nf), len(forecast), sum(1 for _, v in ai_orig if v is not None), sum(1 for _, v in ai_cur if v is not None)))
    A("")
    A("## Sources, retrieval and file hashes")
    A("")
    A("| file | URL | retrieved (UTC) | sha256 |")
    A("|---|---|---|---|")
    for k, name in RAW_FILES.items():
        t, u = fmtlog.get(name, ("", ""))
        A("| %s | %s | %s | %s |" % (name, u.replace("|", "%7C").replace("~/", "%7E/"), t, hashes[name]))
    bk = [k for k in hashes if k.startswith("beige_pages")][0]
    A("| Beige Book pages (%s) | https://www.federalreserve.gov/monetarypolicy/beigebook<YYYY>.htm year indexes and the pages they link (the 2026 index is beige-book-default.htm) | see the cache fetch log | %s (sha256 of the sorted list of file name and file sha256) |" % (bk.split("(")[1].rstrip(")"), hashes[bk]))
    A("")
    A("SBU workbook last-updated date (from the workbook): %s. Dallas workbooks: the one sheet in each is `%s` and `%s`; the names confirm not seasonally adjusted. Dispersion file last updated 14 Aug 2026 (from the Philadelphia Fed page). BoE workbook: October 2026." % (vintage.isoformat() if vintage else "unknown", tm_sheet, ts_sheet))
    A("")
    A("## Computations")
    A("")
    A("- **S1 monthly inputs.** Y: `SalesRevGrowthUnc_percent` on sheet `Index Values (unsmoothed) `. EPU: `News_Based_Policy_Uncert_Index` on sheet `Main News Index`, taken as the monthly 10-paper index, logged. VIX: the mean of the daily `CLOSE` over every row of the calendar month, logged. SPF: D1 (75th minus 25th percentile) of the CPI forecast for horizon T+4 from the Philadelphia Fed's Dispersion_1 workbook, sheet `CPI`, each survey quarter's value assigned to the three calendar months of that quarter, logged. The local monthly panel is written to the ignored cache, not committed.")
    A("- **OLS.** Normal equations solved by Gaussian elimination with partial pivoting (`ols`); tested against a hand-computed case in `selftest`. Effect size = d divided by the sample standard deviation (n-1) of the residuals of the baseline months.")
    A("- **S4.** Months present in both the unsmoothed numerator and the observed denominator within each window; R = mean(numerator) / mean(denominator). Thresholds: SUPPORT if R_T <= 0.9 R_B, AGAINST if R_T >= R_B, else INCONCLUSIVE; unlabelled unless S1 v2 is SUPPORT.")
    A("- **S2.** Per edition, text of the twelve District sections pooled; sentences counted as in `split_sentences`; (a) = whole-word match of uncertain, uncertainty, uncertainties (case-insensitive); (b) = (a) and no whole word of {%s} and no phrase of {%s}. Rate = 1,000 x count / sentences." % (", ".join(EXCL_WORDS), ", ".join(EXCL_PHRASES)))
    A("- **S3.** `uncri` minus `uncrd` per month, per survey; the workbook's own `uncr` column was checked to equal that difference to within 0.15 for every month.")
    A("- **S5.** Means of the workbook's sales-growth uncertainty column, over the two registered windows; ratio of the treatment mean to the baseline mean.")
    A("- **S6.** Shares copied from the workbooks; forecast difficulty is the sum of the two answers named in the spec's wording.")
    if dmp_notes:
        A("")
        A("Workbook note defining the S5 column (verbatim): \"%s\"" % dmp_notes[0])
    A("")
    A("## Implementation choices")
    A("")
    for c in IMPL_CHOICES:
        A("- " + c)
    A("")
    A("Projected-only rows in the realised-growth sheet (no observed percentiles, only `postline*` columns): %s." % (", ".join(ym_text(m) for m in projected) if projected else "none"))
    return "\n".join(L) + "\n"


IMPL_CHOICES = [
    "Cache location: the spec says the raw files go in an ignored path, and `data/vintages/` is not ignored as a whole; the script creates `data/vintages/cv1_stage2/` with its own `.gitignore` holding `*`, so nothing in it can be committed. No existing file was edited for this.",
    "Label boundaries are inclusive as the spec writes them: an effect size of exactly -0.5 is SUPPORT and exactly 0 is AGAINST; exactly 0.9 x R_B is SUPPORT and exactly R_B is AGAINST. Only values strictly between the thresholds are INCONCLUSIVE.",
    "SPF 'one-year CPI forecast dispersion': the Philadelphia Fed publishes cross-sectional dispersion for the quarterly CPI forecasts at horizons T to T+4 (annualised quarterly inflation). The horizon four quarters ahead, T+4, is taken as the one-year forecast; D1 = 75th minus 25th percentile. The other horizons are in `sensitivity.csv`. The annual-average CPI forecasts have no dispersion file there.",
    "VIX: the CBOE URL answers with a 307 to the same organisation's other host (cdn-api.cboe.com); the redirect was followed once inside the same registrable domain.",
    "EPU: the sheet is called `Main News Index` and its column `News_Based_Policy_Uncert_Index`; it is read as the monthly 10-paper index the spec names.",
    "Baseline residual SD uses the n-1 divisor; the n divisor is in `sensitivity.csv`.",
    "S4 'observed rows only': the sheet has no explicit flag column, but the observed rows are those with the realised percentiles filled in; the projected rows carry only `postline*` columns and are never used. The spec's fall-back rule (months at least 12 months before the vintage date) is therefore not the registered rule here; it is printed as a variant in `sensitivity.csv`.",
    "S4 months: a month enters a window only if both the numerator and the denominator exist; the counts are printed.",
    "S2 pages: for 2015 to 2023 each edition is one page with all twelve District sections, found by the fixed District headings (First District--Boston ... or Federal Reserve Bank of Boston ...); for 2024 onwards each District has its own page, built from the edition's summary-page link. The summary pages themselves are not fetched. The national summary is excluded because a section starts only at a District heading.",
    "S2 headings: four 2019 editions carry mistyped District headings on the Board's pages ('Federal Reserve Bank of Federal Reserve Bank of New York'; a bare 'St. Louis'); the District heading pattern accepts a repeated or missing 'Federal Reserve Bank of' prefix, still against the fixed twelve city names.",
    "S2 edition dates: release dates. For 2015 to 2023 from the page title; for 2024 onwards the page file name carries a cycle month that can differ from the release month (the March 2024 release sits in a file named 202402), so the summary pages on the year's index are paired in order with the release dates of the PDF links on the same index. The 2026 editions come from beige-book-default.htm, the 2026 year index returning 404.",
    "S2 sentence counting: text blocks are cut at paragraph and line breaks; section titles (lines wholly in bold or italic, headings) and two fixed boilerplate lines (Return to top; For more information about District economic conditions ...) are not text; every other piece counts as a sentence whether or not it ends with a stop. The splitter breaks on . ? ! followed by whitespace except after initials chained with periods (U.S., U.K., D.C.) and the abbreviations st, mt, ft, mr, mrs, ms, dr, jr, sr, inc, corp, co, ltd, vs, approx and the month abbreviations jan, feb, aug, sept, oct, nov, dec. A sentence that ends in U.S. and is followed by a new sentence is therefore not split.",
    "S2 dictionaries: whole-word, case-insensitive; phrases match with any run of whitespace between their words. No stems.",
    "S3: the Dallas files carry one sheet each, named for not seasonally adjusted data; the file with the .xls name is an xlsx container and was read as one.",
    "S5: the workbook has no column headed in the spec's words; its sheet `Subjective uncertainty` has `Sales growth uncertainty (%)` and its Notes sheet defines that as the average standard deviation of expected sales growth within firms, so the column is used. Both the single-month and the three-month-average columns are reported; v1 named the three-month average and v2 is silent.",
    "S6: lines are told apart by the question text and by collection dates, not by question number. The original AI series comes from Census's AI Core (original) workbook (to the cycle collected up to 5 Oct 2025); the current national workbook's AI-use cycles from collection start 17 Nov 2025 carry the business-functions wording until the cycle collected from 19 Oct 2026, where the Super Intelligence wording starts. The three groups are written as separate lines and never combined.",
    "The Beige Book fetch honours at most two requests a second to federalreserve.gov (about one every 0.65 s).",
]


# ------------------------------------------------------------------------------------------------------------------------
# selftest
# ------------------------------------------------------------------------------------------------------------------------
def close(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def run_selftest(say=print):
    results = []

    def check(name, cond):
        results.append((name, bool(cond)))
        say("  [%s] %s" % ("ok" if cond else "FAIL", name))

    say("selftest (synthetic inputs, known answers)")

    # OLS with a treatment dummy: hand-computed case. x = 0,1,2,3 in both groups; baseline y = 1,2,2,4; treatment y = 6,7,9,10.
    # Pooled within-group slope = (4.5 + 7) / (5 + 5) = 1.15; baseline intercept = 2.25 - 1.15 * 1.5 = 0.525; treatment intercept = 8 - 1.725 = 6.275; d = 5.75.
    # Baseline residuals 0.475, 0.325, -0.825, 0.025; sample variance 1.0125 / 3 = 0.3375.
    X, y = [], []
    for treat, ys in ((0, [1, 2, 2, 4]), (1, [6, 7, 9, 10])):
        for x, v in zip(range(4), ys):
            X.append([1.0, float(x), float(treat)])
            y.append(float(v))
    beta, resid = ols(X, y)
    check("OLS constant 0.525", close(beta[0], 0.525))
    check("OLS slope 1.15", close(beta[1], 1.15))
    check("OLS treatment dummy d = 5.75", close(beta[2], 5.75))
    base_resid = resid[:4]
    check("baseline residuals 0.475 0.325 -0.825 0.025", all(close(a, b) for a, b in zip(base_resid, [0.475, 0.325, -0.825, 0.025])))
    check("baseline residual SD (n-1) = sqrt(0.3375)", close(stdev(base_resid, 1), math.sqrt(0.3375)))
    check("effect size = 5.75 / sqrt(0.3375)", close(effect_size(beta[2], base_resid), 5.75 / math.sqrt(0.3375)))

    # exact recovery with three controls and the dummy (no noise), through the S1 fit that takes logs
    rows = []
    import random
    rnd = random.Random(7)
    for i in range(30):
        treat = 1 if i >= 15 else 0
        e, v, s = rnd.uniform(50, 300), rnd.uniform(10, 40), rnd.uniform(0.3, 1.2)
        yv = 1.0 + 0.5 * math.log(e) - 2.0 * math.log(v) + 0.25 * math.log(s) + 3.0 * treat
        rows.append({"y": yv, "epu": e, "vix": v, "spf": s, "treat": treat})
    b, r_all, r_base = s1_fit(rows)
    check("S1 fit recovers a, b1, b2, b3, d exactly on noiseless data", all(close(x, t, 1e-7) for x, t in zip(b, [1.0, 0.5, -2.0, 0.25, 3.0])))
    check("S1 fit residuals are zero and the baseline slice has 15 of them", len(r_base) == 15 and max(abs(x) for x in r_all) < 1e-7)

    # label rules (the spec's inequalities are inclusive)
    check("S1 label: -0.6 is SUPPORT", s1_label(-0.6) == "SUPPORT")
    check("S1 label: exactly -0.5 is SUPPORT (spec: <= -0.5)", s1_label(-0.5) == "SUPPORT")
    check("S1 label: -0.4999 is INCONCLUSIVE", s1_label(-0.4999) == "INCONCLUSIVE")
    check("S1 label: -0.0001 is INCONCLUSIVE", s1_label(-0.0001) == "INCONCLUSIVE")
    check("S1 label: exactly 0 is AGAINST (spec: >= 0)", s1_label(0.0) == "AGAINST")
    check("S1 label: 0.3 is AGAINST", s1_label(0.3) == "AGAINST")

    # S4: ratio of means is not the mean of ratios; label only if S1 is SUPPORT
    num, den = [1.0, 2.0, 3.0], [2.0, 2.0, 8.0]
    check("ratio of means = 2/4 = 0.5 (mean of ratios would be 0.625)", close(ratio_of_means(num, den), 0.5) and not close(mean(a / b for a, b in zip(num, den)), 0.5))
    check("S4 label: R_T 0.9 R_B exactly is SUPPORT when S1 is SUPPORT", s4_label(0.9, 1.0, "SUPPORT") == "SUPPORT")
    check("S4 label: R_T below 0.9 R_B is SUPPORT", s4_label(0.8, 1.0, "SUPPORT") == "SUPPORT")
    check("S4 label: R_T = R_B is AGAINST", s4_label(1.0, 1.0, "SUPPORT") == "AGAINST")
    check("S4 label: R_T above R_B is AGAINST", s4_label(1.1, 1.0, "SUPPORT") == "AGAINST")
    check("S4 label: 0.95 R_B is INCONCLUSIVE", s4_label(0.95, 1.0, "SUPPORT") == "INCONCLUSIVE")
    check("S4 unlabelled when S1 is AGAINST", s4_label(0.5, 1.0, "AGAINST") == "UNLABELLED_S1_NOT_SUPPORT")
    check("S4 unlabelled when S1 is INCONCLUSIVE", s4_label(0.5, 1.0, "INCONCLUSIVE") == "UNLABELLED_S1_NOT_SUPPORT")
    check("S4 unlabelled when S1 is not built", s4_label(0.5, 1.0, "NOT_BUILT") == "UNLABELLED_S1_NOT_SUPPORT")

    # windows and mapping
    check("S1 baseline window Dec 2016 to Dec 2019 is 37 months", len(window_months(S1_BASE)) == 37)
    check("S1 treatment window Jan 2023 to Dec 2025 is 36 months", len(window_months(S1_TREAT)) == 36)
    check("S4 treatment window Jan 2024 to Dec 2025 is 24 months", len(window_months(S4_TREAT)) == 24)
    check("SPF quarter 2016Q4 maps to Oct, Nov, Dec 2016", quarter_months("2016Q4") == [(2016, 10), (2016, 11), (2016, 12)])
    csv_in = "DATE,OPEN,HIGH,LOW,CLOSE\n01/02/2020,1,1,1,10\n01/03/2020,1,1,1,20\n02/03/2020,1,1,1,40\n"
    vm = vix_monthly(csv_in)
    check("VIX monthly mean of closes: Jan 2020 = 15 over 2 days, Feb = 40", vm[(2020, 1)] == (15.0, 2) and vm[(2020, 2)] == (40.0, 1))

    # dictionaries
    check("(a) matches 'uncertainty' case-insensitively", dict_a("Contacts reported high Uncertainty about demand."))
    check("(a) matches 'uncertain' and 'uncertainties'", dict_a("Many were uncertain.") and dict_a("Several uncertainties remain."))
    check("(a) does not match 'certain' or 'uncertainly'", not dict_a("Certain contacts spoke.") and not dict_a("He spoke uncertainly."))
    toward = "Contacts were uncertain as growth moderates toward trend in retail trade."
    check("'toward' is not an exclusion", not policy_linked("growth heads toward trend"))
    check("'moderates' is not an exclusion", not policy_linked("growth moderates"))
    check("'retail trade' is not an exclusion", not policy_linked("retail trade contacts"))
    check("a sentence with toward, moderates and retail trade stays in (b)", dict_a(toward) and dict_b(toward))
    check("'tariffs' IS an exclusion and removes the sentence from (b)", policy_linked("Uncertainty about tariffs rose.") and dict_a("Uncertainty about tariffs rose.") and not dict_b("Uncertainty about tariffs rose."))
    check("'tariff' (singular) is an exclusion", policy_linked("A new tariff was announced"))
    check("'taxi' and 'syntax' do not match 'tax'", not policy_linked("taxi syntax"))
    check("phrase 'interest rates' and 'Federal Reserve' are exclusions", policy_linked("higher interest rates") and policy_linked("the Federal Reserve met") and policy_linked("federal  reserve"))
    check("'warned' and 'wage rates' are not exclusions (no stems)", not policy_linked("Firms warned that wage rates rose"))
    check("'regulatory' is an exclusion, 'regulate' is not", policy_linked("regulatory change") and not policy_linked("to regulate"))
    check("'COVID-19' is an exclusion (whole word before the hyphen)", policy_linked("COVID-19 cases"))

    # sentence splitter
    s = split_sentences("The U.S. economy grew. Contacts in St. Louis were uncertain. Did it slow? Yes! It was 1.5 percent.")
    check("splitter keeps 'U.S.' and 'St. Louis' whole: 5 sentences", len(s) == 5 and s[0] == "The U.S. economy grew." and s[1] == "Contacts in St. Louis were uncertain.")
    check("splitter: U.K. and Inc. do not break", len(split_sentences("The U.K. firm Acme Inc. reported uncertainty. Then it stopped.")) == 2)
    check("splitter: a title-less remainder counts as one sentence", len(split_sentences("Plain bullet without a stop")) == 1)
    check("splitter: empty text has no sentences", split_sentences("  ") == [])

    # html: District sections, titles, national summary, boilerplate
    old = ("<html><body><h1>Board</h1><h2>Beige Book - January 14, 2015</h2><h2>Summary of Commentary on Current Economic Conditions by Federal Reserve District</h2>"
           "<p>National text is uncertain. Prices rose.</p><h2>First District--Boston</h2>Boston sales rose. Uncertainty was high.<p><strong>Retail</strong><br/>Stores were uncertain about tariffs. The U.S. outlook is mixed.</p>"
           "<p><a href='#top'>Return to top</a></p><h2>Second District--New York</h2><p>New York was calm.</p><h4>Other Formats</h4><p>PDF uncertain</p></body></html>")
    secs = district_sections(parse_blocks(old))
    check("old format: only the District sections are read, the national summary and trailer are not", sorted(secs) == ["Boston", "New York"])
    sent = [x for seg in secs["Boston"] for x in split_sentences(seg)]
    check("old format: Boston has 4 sentences (title and 'Return to top' dropped)", len(sent) == 4)
    check("old format: counts (a)=2 (b)=1 for Boston", count_sentences(sent)[1:] == (2, 1))
    new = ("<html><body><h4>National Summary</h4><p>Uncertain national.</p><h4>Federal Reserve Bank of St. Louis</h4><p><strong>Summary of Economic Activity</strong><br/>"
           "Activity was flat. Contacts were uncertain.</p><p><em>For more information about District economic conditions visit: x</em></p><h6>Board of Governors of the Federal Reserve System</h6><p>uncertain footer</p></body></html>")
    secs2 = district_sections(parse_blocks(new))
    s2 = [x for seg in secs2.get("St. Louis", []) for x in split_sentences(seg)]
    check("new format: St. Louis section read once, 2 sentences, footer and national summary excluded", list(secs2) == ["St. Louis"] and len(s2) == 2 and count_sentences(s2) == (2, 1, 1))
    page = ("<html><body><h3>Federal Reserve Bank of Boston</h3><h4>Summary of Economic Activity</h4><p>One. Two uncertain.</p><h4>Labor Markets</h4><p>Three.</p>"
            "<h6>Board of Governors of the Federal Reserve System</h6><p>Out.</p></body></html>")
    secs3 = district_sections(parse_blocks(page))
    check("district page: sub-headings stay inside the section, trailer ends it", edition_counts({"Boston": secs3["Boston"]}) == (3, 1, 1))
    check("title date parses", title_date("<title>FRB: Beige Book - January 14, 2015</title>") == dt.date(2015, 1, 14))
    idx = '<a href="/monetarypolicy/beigebook202402-summary.htm">x</a><a href="/monetarypolicy/files/BeigeBook_20240306.pdf">p</a><a href="/monetarypolicy/beigebook202301.htm">y</a>'
    eds, pdfs = discover_editions(2024, idx)
    check("edition discovery: one 2024 summary page and its PDF release date", len(eds) == 1 and eds[0]["summary"] and pdfs == [dt.date(2024, 3, 6)])
    check("district page url built from the summary link", edition_pages(eds[0])[7][1] == "/monetarypolicy/beigebook202402-st-louis.htm" and len(edition_pages(eds[0])) == 12)

    # output guard
    try:
        safe_text("a path /Users/x")
        guard = False
    except Refused:
        guard = True
    check("output guard refuses a local path and an at sign", guard)

    bad = [n for n, ok in results if not ok]
    say("selftest: %d checks, %d failed" % (len(results), len(bad)))
    return 1 if bad else 0


def make_parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    f = sub.add_parser("fetch")
    f.add_argument("--only", help="comma-separated keys: sbu,epu,vix,spf,dallas,dmp,btos,beige")
    f.add_argument("--max-seconds", type=int, default=0, help="stop requesting after this many seconds; run again to resume")
    sub.add_parser("build")
    return ap


def main(argv=None):
    a = make_parser().parse_args(argv)
    try:
        if a.cmd == "selftest":
            return run_selftest()
        if a.cmd == "fetch":
            return run_fetch(a)
        if a.cmd == "build":
            return run_build(a)
    except (Refused, DataError) as e:
        print("REFUSED/ERROR: %s" % e)
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
