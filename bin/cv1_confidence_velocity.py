#!/usr/bin/env python3
"""CV1: the confidence / capital-velocity channel. Registered statements CV1-P1..P6 (P7 is not scored), version 2 of the spec. Python 3 standard library plus openpyxl (and xlrd for the P6 concordance, an old-format .xls).

  python3 bin/cv1_confidence_velocity.py selftest                                   # synthetic data only; no network
  python3 bin/cv1_confidence_velocity.py fetch --what bea|z1|census|frames|submissions|btos|all [--max-requests N] [--budget-seconds S]
  python3 bin/cv1_confidence_velocity.py build [--out DIR]                           # offline; writes registered.csv FIRST, then computes every statistic

Specification: _research/2026-11-13-CV1-Confidence-Velocity-Spec.md ("Registered statements - version 2" is binding; its sha256 is pinned in SPEC_SHA256 below and the build
refuses to score if the file differs). Why each rule exists: _research/2026-11-13-Grok-CV1-Attack.md.
Outputs: data/cv1_confidence_velocity/ (registered.csv, scores.csv, denominators.csv, vintages.csv, README.md). Raw downloads: see CACHE below (gitignored).

WHAT TOUCHES THE NETWORK. Only `fetch`. data.sec.gov (frames, submissions) gets the declared tool name only, at most 5 requests a second; every other host gets the one neutral
string CLAUDE.md fixes. Never www.sec.gov, never FRED, never a key or a login. A 403 or 429 from a host writes STOP_<host> in the cache and no further request is made to that host
(a person deletes the file). Nothing is retried except once after a timeout or a 5xx. Statistics are computed only by `build`, and only after registered.csv is written.
"""
import argparse
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_FILE = "_research/2026-11-13-CV1-Confidence-Velocity-Spec.md"
SPEC_SHA256 = "26672bd1f1632ddab839780b219724773cab83f63dae082c87e838cc1a7a6104"
OUT_REL = "data/cv1_confidence_velocity"
# Raw downloads. data/vintages/cv1/ is NOT covered by .gitignore, and this task could not edit .gitignore, so the cache lives in a folder that .gitignore already ignores
# whole (data/vintages/funding_identity_checks/). The supervisor may add `data/vintages/cv1/` to .gitignore and move it. bin/check.sh M31 checks that the cache is ignored and untracked.
CACHE_REL = "data/vintages/cv1"
UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"          # the one neutral string CLAUDE.md fixes: no person, address or contact
SEC_TOOL = UA.split(";")[1].strip()                                                              # the declared tool name for data.sec.gov only (house rule 12 Sep): no address
SEC_HOST = "data.sec.gov"
HOSTS = {"apps.bea.gov", "www.federalreserve.gov", "www.census.gov", SEC_HOST}
TIMEOUT = 120
SEC_MIN_GAP = 0.25                                                                               # seconds: at most 4 requests a second, under the 5 a second limit

URLS = {
    "bea1": "https://apps.bea.gov/national/Release/XLS/Survey/Section1All_xls.xlsx",
    "bea5": "https://apps.bea.gov/national/Release/XLS/Survey/Section5All_xls.xlsx",
    "z1": "https://www.federalreserve.gov/releases/z1/data/FRB_Z1_csv.zip",
    "c30": "https://www.census.gov/construction/c30/xlsx/privsatime.xlsx",
}
FRAME_URL = "https://data.sec.gov/api/xbrl/frames/us-gaap/%s/USD/%s.json"
SUBM_URL = "https://data.sec.gov/submissions/%s"


class Refused(Exception):
    pass


class Stop(Exception):
    pass


def sha256_of(b):
    return hashlib.sha256(b).hexdigest()


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cache_dir(root=None):
    return os.path.join(root or ROOT, *CACHE_REL.split("/"))


def out_dir(root=None):
    return os.path.join(root or ROOT, *OUT_REL.split("/"))


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


def write_bytes(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.replace(tmp, path)


def csv_line(cells):
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerow(cells)
    return buf.getvalue()


# ------------------------------------------------------------------------------------------------------------------------
# network: one place
# ------------------------------------------------------------------------------------------------------------------------
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Fetcher(object):
    """GET only, allowlisted hosts, per-host STOP latch, SEC rate limit, a log row for every request. `opener` and `sleep` are injectable for the selftest."""

    def __init__(self, cache, opener=None, sleep=time.sleep, clock=time.monotonic):
        self.cache = cache
        self.opener = opener or urllib.request.build_opener(_NoRedirect)
        self.sleep = sleep
        self.clock = clock
        self.last_sec = None
        self.requests = 0
        self.log = []

    def stop_path(self, host):
        return os.path.join(self.cache, "STOP_" + host.replace(".", "_"))

    def stopped(self, host):
        return os.path.exists(self.stop_path(host))

    def _latch(self, host, status, url):
        p = self.stop_path(host)
        os.makedirs(self.cache, exist_ok=True)
        with open(p, "x", encoding="utf-8") as fh:
            fh.write("status: %s\nhost: %s\nutc: %s\nurl: %s\nnote: no further request to this host; only a person deletes this file\n" % (status, host, now_utc(), url))

    def get(self, url, accept_gzip=False):
        """Return (status, body, headers). Raises Stop if the host is latched or answers 403/429 (latch written)."""
        sp = urlsplit(url)
        host = sp.hostname
        if sp.scheme != "https" or host not in HOSTS:
            raise Refused("host not on the allowlist: %s" % host)
        if host == "www.sec.gov" or "fred" in host:
            raise Refused("never")
        if self.stopped(host):
            raise Stop("STOP latch present for %s" % host)
        ua = SEC_TOOL if host == SEC_HOST else UA
        hdr = {"User-Agent": ua, "Accept-Encoding": "gzip" if accept_gzip else "identity", "Accept": "*/*"}
        for attempt in (1, 2):
            if host == SEC_HOST and self.last_sec is not None:
                wait = SEC_MIN_GAP - (self.clock() - self.last_sec)
                if wait > 0:
                    self.sleep(wait)
            if host == SEC_HOST:
                self.last_sec = self.clock()
            self.requests += 1
            try:
                resp = self.opener.open(urllib.request.Request(url, headers=hdr), timeout=TIMEOUT)
                status, body, h = resp.status, resp.read(), dict(resp.headers)
            except urllib.error.HTTPError as e:
                status, body, h = e.code, (e.read() or b""), dict(e.headers or {})
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                if attempt == 1:
                    self.sleep(2)
                    continue
                self.log.append((url, now_utc(), "ERR " + type(e).__name__, 0, ""))
                raise
            if status in (403, 429):
                self.log.append((url, now_utc(), status, len(body), ""))
                self._latch(host, status, url)
                raise Stop("HTTP %s from %s: STOP latch written; no further request to this host" % (status, host))
            if status >= 500 and attempt == 1:
                self.sleep(2)
                continue
            if h.get("Content-Encoding", "").lower() == "gzip" or body[:2] == b"\x1f\x8b" and accept_gzip:
                try:
                    body = gzip.decompress(body)
                except OSError:
                    pass
            self.log.append((url, now_utc(), status, len(body), sha256_of(body)))
            return status, body, h
        raise RuntimeError("unreachable")


# ------------------------------------------------------------------------------------------------------------------------
# registered definitions (spec "Registered statements - version 2")
# ------------------------------------------------------------------------------------------------------------------------
AI_SIC_RANGES = ((3559, 3559), (3570, 3579), (3661, 3661), (3663, 3663), (3669, 3669), (3670, 3679), (4812, 4812), (4813, 4813), (7370, 7379))
AI_CIKS = {1018724: "Amazon", 1652044: "Alphabet", 1326801: "Meta", 789019: "Microsoft", 1341439: "Oracle", 1045810: "Nvidia", 1318605: "Tesla"}
UTIL_RANGE = (4900, 4991)
REIT_SIC = 6798
FIN_RANGE = (6000, 6799)
WINDOWS = {"T": (2022, 2025), "P": (2016, 2019)}              # panel (calendar-year frames)
Q_WINDOWS = {"T": ("2022Q4", "2025Q4"), "P": ("2015Q4", "2019Q4")}   # BEA and Z.1 (Q4 to Q4)
PANEL_YEARS = (2016, 2019, 2022, 2025)
FYE_MONTHS = (11, 12, 1)
CAPEX_TAG = "PaymentsToAcquirePropertyPlantAndEquipment"
PPE_TAG = "PropertyPlantAndEquipmentNet"
ACQ_TAG = "PaymentsToAcquireBusinessesNetOfCashAcquired"
CASH_TAG = "CashAndCashEquivalentsAtCarryingValue"
CASH_ALT_TAG = "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"
ASSETS_TAG = "Assets"
PPE_YEARS = (2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025)
ACQ_YEARS = (2017, 2018, 2019, 2023, 2024, 2025)
P4_YEARS = (2015, 2021)                                         # the year-end before each window's base year
HIGH_RANGES = ((1000, 1499), (2000, 3999), (4000, 4899))
LOW_RANGES = ((5000, 5999), (7000, 8999))
TRIM_SICS = (1311, 1381, 1382, 1389, 2911, 3711, 3721)
Z1_SERIES = {
    "FL104001105": ("liquid assets (core measure)", "core liquid assets"),
    "FL103061103": ("treasury securities; asset", "Treasury securities"),
    "FL103061703": ("agency- and gse-backed securities; asset", "agency and GSE-backed securities"),
    "FL103069100": ("commercial paper; asset", "open market paper (commercial paper)"),
}


def frame_list():
    """(tag, period) for every SEC frame the build reads, in fetch order."""
    out = [(CAPEX_TAG, "CY%d" % y) for y in PANEL_YEARS]
    out += [(PPE_TAG, "CY%dQ4I" % y) for y in PPE_YEARS]
    out += [(ACQ_TAG, "CY%d" % y) for y in ACQ_YEARS]
    for tag in (CASH_TAG, CASH_ALT_TAG, ASSETS_TAG):
        out += [(tag, "CY%dQ4I" % y) for y in P4_YEARS]
    return out


def frame_path(cache, tag, period):
    return os.path.join(cache, "raw", "sec", "frames", "%s__%s.json.gz" % (tag, period))


def subm_path(cache, cik):
    return os.path.join(cache, "raw", "sec", "submissions", "CIK%010d.json.gz" % cik)


def older_path(cache, name):
    return os.path.join(cache, "raw", "sec", "submissions", "older", name + ".gz")


def in_ranges(sic, ranges):
    return sic is not None and any(a <= sic <= b for a, b in ranges)


def read_gz_json(path):
    with gzip.open(path, "rb") as fh:
        return json.loads(fh.read())


def manifest_add(cache, key, url, body, status=200):
    p = os.path.join(cache, "manifest.csv")
    new = not os.path.exists(p)
    with open(p, "a", encoding="utf-8", newline="") as fh:
        if new:
            fh.write("key,url,fetched_utc,status,bytes,sha256\n")
        fh.write(csv_line([key, url, now_utc(), status, len(body), sha256_of(body)]))


def read_manifest(cache):
    p = os.path.join(cache, "manifest.csv")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def get_store(fetcher, cache, key, url, path, gz=False, accept_gzip=False):
    """Fetch url into path unless it is there. Returns 'cached', 'fetched' or an HTTP status string for a non-200."""
    if os.path.exists(path):
        return "cached"
    status, body, _h = fetcher.get(url, accept_gzip=accept_gzip)
    if status != 200:
        manifest_add(cache, key, url, body[:0], status)
        return "HTTP %s" % status
    write_bytes(path, gzip.compress(body, 3) if gz else body)
    manifest_add(cache, key, url, body, status)
    return "fetched"


def load_frame(cache, tag, period):
    p = frame_path(cache, tag, period)
    return read_gz_json(p)["data"] if os.path.exists(p) else None


def panel_candidates(cache):
    """CIKs with a positive capex fact in each of the four panel years, a fiscal year-end month of 11, 12 or 1 on each fact, and not an AI CIK. A superset of the final panel
    (the 10-K filter and the SIC test need submissions)."""
    sets = []
    for y in PANEL_YEARS:
        d = load_frame(cache, CAPEX_TAG, "CY%d" % y)
        if d is None:
            return None
        sets.append({r["cik"] for r in d if r["val"] is not None and r["val"] > 0 and int(r["end"][5:7]) in FYE_MONTHS})
    return sorted(set.intersection(*sets) - set(AI_CIKS))


def needed_accns(cache, ciks):
    """accn -> set of CIKs, for every fact of the candidate CIKs in every frame the build reads."""
    want = set(ciks)
    need = {}
    for tag, per in frame_list():
        d = load_frame(cache, tag, per)
        for r in d or ():
            if r["cik"] in want:
                need.setdefault(r["cik"], set()).add(r["accn"])
    return need


def older_pages_needed(cache, cik, accns):
    """Names of the older submissions pages (listed in the main file) that may hold accns the main file's `recent` does not, chosen by the filing year in the accession number."""
    p = subm_path(cache, cik)
    if not os.path.exists(p):
        return []
    j = read_gz_json(p)
    recent = set(j.get("filings", {}).get("recent", {}).get("accessionNumber", []))
    missing = [a for a in accns if a not in recent]
    if not missing:
        return []
    pages = j.get("filings", {}).get("files", [])
    out = []
    for pg in pages:
        a, b = int(pg["filingFrom"][:4]), int(pg["filingTo"][:4])
        for acc in missing:
            yy = int(acc.split("-")[1])
            yr = 2000 + yy if yy < 70 else 1900 + yy
            if a <= yr <= b:
                out.append(pg["name"])
                break
    return out


def cmd_fetch(what, max_requests, budget_seconds, root=None, fetcher=None):
    cache = cache_dir(root)
    os.makedirs(cache, exist_ok=True)
    f = fetcher or Fetcher(cache)
    t0 = time.monotonic()

    def over():
        return f.requests >= max_requests or time.monotonic() - t0 > budget_seconds

    def say(s):
        print(s, flush=True)

    todo = {"bea": ("bea1", "bea5"), "z1": ("z1",), "census": ("c30",)}
    try:
        for grp in ("bea", "z1", "census"):
            if what in (grp, "all"):
                for k in todo[grp]:
                    u = URLS[k]
                    r = get_store(f, cache, k, u, os.path.join(cache, "raw", os.path.basename(u)))
                    say("%s %s" % (k, r))
        if what in ("frames", "all"):
            for tag, per in frame_list():
                if over():
                    say("budget reached in frames; rerun to resume")
                    return 0
                r = get_store(f, cache, "frame:%s:%s" % (tag, per), FRAME_URL % (tag, per), frame_path(cache, tag, per), gz=True, accept_gzip=True)
                say("frame %s %s %s" % (tag, per, r))
        if what in ("submissions", "all"):
            ciks = panel_candidates(cache)
            if ciks is None:
                say("the four capex frames are not all in the cache: run fetch --what frames first")
                return 2
            say("candidate CIKs (positive capex in all four years, FYE month 11/12/1, not an AI CIK): %d" % len(ciks))
            n_new = n_have = n_404 = 0
            for cik in ciks:
                if os.path.exists(subm_path(cache, cik)):
                    n_have += 1
                    continue
                if over():
                    say("budget reached in submissions (fetched %d this run, %d already cached, %d left); rerun to resume" % (n_new, n_have, len(ciks) - n_new - n_have - n_404))
                    return 0
                r = get_store(f, cache, "subm:%d" % cik, SUBM_URL % ("CIK%010d.json" % cik), subm_path(cache, cik), gz=True, accept_gzip=True)
                if r == "fetched":
                    n_new += 1
                elif r != "cached":
                    n_404 += 1
                    say("CIK %d: %s" % (cik, r))
            say("main submissions: %d fetched now, %d already cached, %d non-200" % (n_new, n_have, n_404))
            need = needed_accns(cache, ciks)
            pages = set()
            for cik in ciks:
                for nm in older_pages_needed(cache, cik, need.get(cik, ())):
                    pages.add(nm)
            say("older submissions pages needed to resolve accession numbers: %d" % len(pages))
            n_new = 0
            for nm in sorted(pages):
                if os.path.exists(older_path(cache, nm)):
                    continue
                if over():
                    say("budget reached in older pages (%d fetched this run); rerun to resume" % n_new)
                    return 0
                r = get_store(f, cache, "older:" + nm, SUBM_URL % nm, older_path(cache, nm), gz=True, accept_gzip=True)
                if r == "fetched":
                    n_new += 1
                elif r != "cached":
                    say("older page %s: %s" % (nm, r))
            say("older pages fetched now: %d" % n_new)
        if what in ("submissions-all", "all"):
            d25 = load_frame(cache, CAPEX_TAG, "CY2025")
            if d25 is None:
                say("the CY2025 capex frame is not in the cache: run fetch --what frames first")
                return 2
            ciks = sorted({r["cik"] for r in d25 if r["val"] is not None and r["val"] > 0} - set(AI_CIKS))
            have = sum(1 for c in ciks if os.path.exists(subm_path(cache, c)))
            say("coverage denominator: %d CIKs with positive CY2025 capex (not an AI CIK), %d submissions already cached" % (len(ciks), have))
            n_new = 0
            for cik in ciks:
                if os.path.exists(subm_path(cache, cik)):
                    continue
                if over():
                    say("budget reached in submissions-all (%d fetched this run); rerun to resume" % n_new)
                    return 0
                r = get_store(f, cache, "subm:%d" % cik, SUBM_URL % ("CIK%010d.json" % cik), subm_path(cache, cik), gz=True, accept_gzip=True)
                if r == "fetched":
                    n_new += 1
                elif r != "cached":
                    say("CIK %d: %s" % (cik, r))
            say("submissions-all: %d fetched now" % n_new)
    except Stop as e:
        say("STOP: %s" % e)
        return 2
    finally:
        say("requests this run: %d" % f.requests)
        if f.log:
            p = os.path.join(cache, "fetch_log.csv")
            new = not os.path.exists(p)
            with open(p, "a", encoding="utf-8", newline="") as fh:
                if new:
                    fh.write("url,utc,status,bytes,sha256\n")
                for row in f.log:
                    fh.write(csv_line(row))
    return 0


# ------------------------------------------------------------------------------------------------------------------------
# pure computation (the selftest exercises each of these on small synthetic inputs with known answers)
# ------------------------------------------------------------------------------------------------------------------------
def ann_growth(base, end, years):
    """Annualised growth rate as a fraction: (end/base)^(1/years) - 1. base and end must be positive."""
    if not (base > 0 and end > 0 and years > 0):
        raise ValueError("annualised growth needs positive base, end and years")
    return (end / base) ** (1.0 / years) - 1.0


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        raise ValueError("median of nothing")
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def wmean(xs, ws):
    tot = float(sum(ws))
    if not tot > 0:
        raise ValueError("weights must sum to a positive number")
    return sum(x * w for x, w in zip(xs, ws)) / tot


def pp(x):
    return 100.0 * x


def _ranks(v):
    """Average ranks (ties share the mean of their positions)."""
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def spearman(x, y):
    """Spearman rank correlation (Pearson on average ranks). None if either side has no variation or n < 3."""
    if len(x) != len(y) or len(x) < 3:
        return None
    rx, ry = _ranks(x), _ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    if sxx == 0 or syy == 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def terciles_within_sic2(items):
    """items: list of (key, sic2, ratio). Within each 2-digit SIC group sort ascending by ratio (ties by key) and give the i-th of n firms tercile min(2, floor(3 i / n)):
    0 = bottom, 2 = top. A group of fewer than 3 firms cannot be split and is dropped. Returns (dict key -> tercile, list of dropped keys)."""
    groups = {}
    for key, s2, ratio in items:
        groups.setdefault(s2, []).append((ratio, key))
    out, dropped = {}, []
    for s2 in sorted(groups):
        g = sorted(groups[s2])
        n = len(g)
        if n < 3:
            dropped += [k for _r, k in g]
            continue
        for i, (_r, k) in enumerate(g):
            out[k] = min(2, (3 * i) // n)
    return out, dropped


EPS = 9


def ge(x, t):
    return round(x, EPS) >= t


def gt(x, t):
    return round(x, EPS) > t


def le(x, t):
    return round(x, EPS) <= t


def lt(x, t):
    return round(x, EPS) < t


def _pick(sup, ag):
    if sup and ag:
        return "INCONCLUSIVE"
    return "SUPPORT" if sup else ("AGAINST" if ag else "INCONCLUSIVE")


# Labels. The spec's inequalities are inclusive where it writes >= and <=; a value exactly on such a threshold takes that label. Where it writes > or "more than", exactly on the
# threshold fails the condition, which is why P2 (median exactly +2, weighted exactly 0), P4 (own growth exactly 0) and P3 (stock growth exactly equal to GDP growth) can land on INCONCLUSIVE at equality.
def label_p1(nominal_gap, real_gap):
    return _pick(ge(nominal_gap, 0.15) and ge(real_gap, 0.15), le(nominal_gap, 0.0) and le(real_gap, 0.0))


def label_p2(median_gap, weighted_gap):
    return _pick(ge(median_gap, 2.0) and gt(weighted_gap, 0.0), le(median_gap, 0.0) and le(weighted_gap, 0.0))


def label_p3(diff_pp, stock_fell, stock_growth, gdp_growth):
    return _pick(le(diff_pp, -0.5) and stock_fell, ge(diff_pp, 0.0) or gt(stock_growth - gdp_growth, 0.0))


def label_p4(stat_pp, top_net_of_gdp_pp):
    return _pick(ge(stat_pp, 3.0) and gt(top_net_of_gdp_pp, 0.0), le(stat_pp, 0.0))


def label_p5(trimmed_gap, untrimmed_gap):
    """If only the untrimmed gap clears +2, INCONCLUSIVE (this clause is applied before AGAINST: a trimmed gap at or below 0 with an untrimmed gap at or above +2 is INCONCLUSIVE)."""
    if ge(untrimmed_gap, 2.0) and not ge(trimmed_gap, 2.0):
        return "INCONCLUSIVE"
    return _pick(ge(trimmed_gap, 2.0), le(trimmed_gap, 0.0))


def at_threshold(x, ts, tol=1e-9):
    return [t for t in ts if abs(x - t) <= tol]


# ------------------------------------------------------------------------------------------------------------------------
# readers
# ------------------------------------------------------------------------------------------------------------------------
def read_bea_sheet(path, sheet):
    """Return (published_text, {series_code: {period: value}}, {series_code: label}). Periods are the header strings ('2022Q4' or '2022')."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = list(wb[sheet].iter_rows(values_only=True))
    finally:
        wb.close()
    hi = next(i for i, r in enumerate(rows) if r and r[0] == "Line")
    pub = next((str(r[0]) for r in rows[:hi] if r and r[0] and str(r[0]).startswith("Data published")), "")
    hdr = rows[hi]
    data, labels = {}, {}
    for r in rows[hi + 1:]:
        if r[0] is None or not str(r[0]).strip().isdigit() or not r[2]:
            continue
        code = str(r[2])
        if code in data:                                    # a code listed twice (a memo line repeats a total): keep the first
            continue
        labels[code] = str(r[1]).strip()
        data[code] = {str(hdr[i]): float(r[i]) for i in range(3, len(hdr)) if hdr[i] is not None and isinstance(r[i], (int, float))}
    return pub, data, labels


def read_z1_series(zpath, series_ids):
    """Stream Z1.csv from the zip, keep the quarterly rows of the named series. Returns {id: {"desc": short_description, "unit_mult": ..., "values": {'2022Q4': millions}}}."""
    prefixes = tuple("Z1/Z1/%s.Q," % s for s in series_ids)
    out = {}
    with zipfile.ZipFile(zpath) as z:
        with z.open("Z1.csv") as raw:
            for line in io.TextIOWrapper(raw, encoding="utf-8", newline=""):
                if not line.startswith(prefixes):
                    continue
                r = next(csv.reader([line]))
                sid = r[0].split("/")[-1].split(".")[0]
                d = out.setdefault(sid, {"desc": r[1], "long": r[2], "unit": r[9], "unit_mult": r[10], "series_type": r[8], "values": {}})
                m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", r[11])
                if m and r[12] not in ("", "ND", "NA"):
                    d["values"]["%sQ%d" % (m.group(1), (int(m.group(2)) - 1) // 3 + 1)] = float(r[12])
    return out


def check_z1_descriptions(z1):
    """The build stops (Refused) if any series is missing or its description is not the meaning the spec gives it."""
    bad = []
    for sid, (needle, meaning) in Z1_SERIES.items():
        if sid not in z1:
            bad.append("%s: not in the file" % sid)
        elif needle not in z1[sid]["desc"].lower():
            bad.append("%s: description %r does not contain %r (the spec means %s)" % (sid, z1[sid]["desc"], needle, meaning))
        elif not z1[sid]["desc"].lower().startswith("nonfinancial corporate business"):
            bad.append("%s: description %r is not the nonfinancial corporate business sector" % (sid, z1[sid]["desc"]))
    if bad:
        raise Refused("Z.1 series check failed, P3 stops: " + "; ".join(bad))


def read_c30_data_center(path):
    """{'Dec-25': value or None} for the 'Data center' column of Private SA (millions, SAAR). A blank is None, never 0."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = list(wb["Private SA"].iter_rows(values_only=True))
    finally:
        wb.close()
    hi = next(i for i, r in enumerate(rows) if r and r[0] == "Date")
    col = next(i for i, h in enumerate(rows[hi]) if h and str(h).strip() == "Data center")
    out = {}
    for r in rows[hi + 1:]:
        if r[0] and re.match(r"^[A-Z][a-z]{2}-\d{2}[pr]?$", str(r[0])):
            v = r[col]
            out[str(r[0])] = float(v) if isinstance(v, (int, float)) else None
    return out


# ------------------------------------------------------------------------------------------------------------------------
# panel statistics (pure: they take firm dicts {cik, sic, cap: {year: dollars}, ratio: {'T'|'P': cash/assets}} and fractions for GDP growth)
# ------------------------------------------------------------------------------------------------------------------------
def firm_growth(f, w):
    b, e = WINDOWS[w]
    return ann_growth(f["cap"][b], f["cap"][e], e - b)


def window_summary(firms, w, gdp_g):
    """Median, capex-weighted mean (weights = base-year capex) and aggregate-sum growth of the firms' annualised capex growth, all as fractions, and their gaps to GDP growth."""
    b, e = WINDOWS[w]
    g = [firm_growth(f, w) for f in firms]
    base = [f["cap"][b] for f in firms]
    end = [f["cap"][e] for f in firms]
    return {"n": len(firms), "median": median(g), "weighted": wmean(g, base), "aggregate": ann_growth(sum(base), sum(end), e - b),
            "gdp": gdp_g[w], "base_capex": sum(base), "end_capex": sum(end)}


def p2_stats(firms_t, firms_p, gdp_g):
    t, p = window_summary(firms_t, "T", gdp_g), window_summary(firms_p, "P", gdp_g)
    return {"T": t, "P": p,
            "median_gap_pp": pp((t["median"] - t["gdp"]) - (p["median"] - p["gdp"])),
            "weighted_gap_pp": pp((t["weighted"] - t["gdp"]) - (p["weighted"] - p["gdp"])),
            "aggregate_gap_pp": pp((t["aggregate"] - t["gdp"]) - (p["aggregate"] - p["gdp"]))}


def tercile_growth(firms, w, gdp_g):
    """Split the firms (each with ratio[w]) into terciles within 2-digit SIC; return per-tercile weighted growth, counts, base capex."""
    b, _e = WINDOWS[w]
    items = [(f["cik"], f["sic"] // 100, f["ratio"][w]) for f in firms]
    tmap, dropped = terciles_within_sic2(items)
    by = {0: [], 1: [], 2: []}
    for f in firms:
        if f["cik"] in tmap:
            by[tmap[f["cik"]]].append(f)
    out = {"dropped_small_sic2": len(dropped), "n_sic2_groups_used": len({s2 for k, s2, _r in items if k in tmap})}
    for tier, name in ((0, "bottom"), (1, "middle"), (2, "top")):
        fs = by[tier]
        if not fs:
            out[name] = None
            continue
        g = [firm_growth(f, w) for f in fs]
        base = [f["cap"][b] for f in fs]
        out[name] = {"n": len(fs), "weighted": wmean(g, base), "base_capex": sum(base), "cap_end_year": sum(f["cap"][WINDOWS[w][1]] for f in fs)}
    return out


def p4_stats(firms_t, firms_p, gdp_g):
    t, p = tercile_growth(firms_t, "T", gdp_g), tercile_growth(firms_p, "P", gdp_g)
    if not (t["top"] and t["bottom"] and p["top"] and p["bottom"]):
        raise Refused("a tercile is empty: P4 cannot be scored")
    stat = pp((t["top"]["weighted"] - t["bottom"]["weighted"]) - (p["top"]["weighted"] - p["bottom"]["weighted"]))
    return {"T": t, "P": p, "stat_pp": stat, "top_net_of_gdp_pp": pp(t["top"]["weighted"] - gdp_g["T"]),
            "top_minus_bottom_T_pp": pp(t["top"]["weighted"] - t["bottom"]["weighted"]), "top_minus_bottom_P_pp": pp(p["top"]["weighted"] - p["bottom"]["weighted"])}


def p5_window(firms, w):
    hi = [f for f in firms if in_ranges(f["sic"], HIGH_RANGES)]
    hi_trim = [f for f in hi if f["sic"] not in TRIM_SICS]
    removed = [f for f in hi if f["sic"] in TRIM_SICS]
    lo = [f for f in firms if in_ranges(f["sic"], LOW_RANGES)]
    if not (hi_trim and lo):
        raise Refused("P5 group empty in window " + w)
    mhi, mlo = median([firm_growth(f, w) for f in hi]), median([firm_growth(f, w) for f in lo])
    mtr = median([firm_growth(f, w) for f in hi_trim])
    mrm = median([firm_growth(f, w) for f in removed]) if removed else None
    return {"n_high": len(hi), "n_high_trimmed": len(hi_trim), "n_removed": len(removed), "n_low": len(lo), "med_high": mhi, "med_high_trimmed": mtr, "med_low": mlo, "med_removed": mrm}


def p5_stats(firms_t, firms_p):
    t, p = p5_window(firms_t, "T"), p5_window(firms_p, "P")
    return {"T": t, "P": p,
            "untrimmed_gap_pp": pp((t["med_high"] - t["med_low"]) - (p["med_high"] - p["med_low"])),
            "trimmed_gap_pp": pp((t["med_high_trimmed"] - t["med_low"]) - (p["med_high_trimmed"] - p["med_low"]))}


def p1_residual_share(nrfi, subtract, gdp):
    """Share of GDP (percent) of nonresidential fixed investment less the subtracted lines. All arguments are values at one date."""
    return 100.0 * (nrfi - sum(subtract)) / gdp


def p1_gap(share_t0, share_t1, share_p0, share_p1, years_t=3.0, years_p=4.0):
    """Annualised pp change over the treatment window minus over the placebo window."""
    return (share_t1 - share_t0) / years_t - (share_p1 - share_p0) / years_p


def p3_stats(stock, gdp):
    """stock, gdp: dicts quarter -> level. Ratio in percent; Q4-to-Q4 change (not annualised) over the treatment window minus over the placebo window."""
    r = lambda q: 100.0 * stock[q] / gdp[q]
    t0, t1 = Q_WINDOWS["T"]
    p0, p1 = Q_WINDOWS["P"]
    dt_, dp_ = r(t1) - r(t0), r(p1) - r(p0)
    return {"ratio_t0": r(t0), "ratio_t1": r(t1), "ratio_p0": r(p0), "ratio_p1": r(p1), "change_T_pp": dt_, "change_P_pp": dp_, "diff_pp": dt_ - dp_,
            "stock_fell": stock[t1] < stock[t0], "stock_growth": stock[t1] / stock[t0] - 1.0, "gdp_growth": gdp[t1] / gdp[t0] - 1.0}


# ------------------------------------------------------------------------------------------------------------------------
# SEC panel loader
# ------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------
# P6: sector AI use (Census BTOS) against the P2 statistic by sector. Descriptive: no label. Inputs are two files the principal downloaded by hand; they are never fetched.
# ------------------------------------------------------------------------------------------------------------------------
BTOS_REL = "raw/census/AI Core Questions.xlsx"
BTOS_SHA256 = "e058a098af64427b0cf0c1455435023aeb9a84142a55175d322687e61a3da3ce"
BTOS_URL = "https://www.census.gov/hfp/btos/downloads/AI%20Core%20Questions.xlsx"
CONC_REL = "raw/census/1987_sic_to_2002_naics.xls"
CONC_SHA256 = "fcb8ad7e4162a4d95c39ebe51c12e8ec20dfa6a31f2e81bf8fb1de08fbedc937"
CONC_URL = "https://www2.census.gov/library/reference/naics/technical-documentation/concordance/1987_sic_to_2002_naics.xls"
P6_YEARS = (2024, 2025)
P6_CUTOFF = dt.date(2025, 11, 17)             # a cycle counts only if its collection ended strictly before this date
P6_MIN_FIRMS = 20
BTOS_QID = 7                                   # "...use Artificial Intelligence (AI) in producing goods or services?"
NAICS2_TO_BTOS = {"31": "31", "32": "31", "33": "31", "44": "44", "45": "44", "48": "48", "49": "48"}


def parse_pct(v):
    """'12.3%' -> 12.3 (percent). 'S' (suppressed), blanks and anything else -> None. A bare number is taken as a percentage."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.strip()
        if s.endswith("%"):
            try:
                return float(s[:-1])
            except ValueError:
                return None
    return None


def btos_cycles(date_rows):
    """date_rows: (smpdt, col_start, col_end, ...) rows of the Collection and Reference Dates sheet. Returns {cycle label (str): col_end date} for the rows that parse."""
    out = {}
    for r in date_rows:
        try:
            label = str(int(r[0]))
            m, d, y = [int(x) for x in str(r[2]).split("/")]
            out[label] = dt.date(y, m, d)
        except (TypeError, ValueError, IndexError):
            continue
    return out


def btos_ai_means(header, rows, cycles):
    """header = column names of the Sector Estimates sheet; rows = its data rows. For each numeric sector, Question ID 7, Answer 'Yes': the mean of the unsuppressed percentages over the
    cycle columns whose label begins with 2024 or 2025 and whose collection ended before P6_CUTOFF. Returns (per-sector dict, list of in-window cycles missing from the sheet, cycle columns used)."""
    cols = {}
    for j, h in enumerate(header):
        if j >= 5 and h is not None:
            lab = str(h).strip()
            if re.match(r"^\d{6}$", lab) and int(lab[:4]) in P6_YEARS and lab in cycles and cycles[lab] < P6_CUTOFF:
                cols[lab] = j
    missing = sorted(l for l, d in cycles.items() if int(l[:4]) in P6_YEARS and d < P6_CUTOFF and l not in cols)
    out = {}
    for r in rows:
        sec = r[0]
        if isinstance(sec, float) and sec == int(sec):
            sec = int(sec)
        if not isinstance(sec, int):                      # the 'XX' multi-unit row, the footer, blanks
            continue
        if r[1] != BTOS_QID or str(r[4]).strip() != "Yes":
            continue
        used, supp = [], []
        for lab in sorted(cols):
            x = parse_pct(r[cols[lab]])
            (supp if x is None else used).append(lab if x is None else (lab, x))
        vals = [x for _l, x in used]
        out[str(sec)] = {"mean": (sum(vals) / len(vals)) if vals else None, "used": [l for l, _x in used], "suppressed": supp}
    return out, missing, sorted(cols)


def btos_sector_of_naics(naics):
    n2 = str(naics)[:2]
    return NAICS2_TO_BTOS.get(n2, n2)


def sic_sector_map(conc_rows):
    """conc_rows: (sic, naics) pairs. Returns {sic: (sector or None, kind)}, kind in 'single' (every row reaches one sector), 'majority' (split; the sector with strictly most rows),
    'tie' (split; no unique majority; sector None, the firm is dropped). Rows are counted, not distinct NAICS codes."""
    votes = {}
    for sic, naics in conc_rows:
        votes.setdefault(sic, {})
        s = btos_sector_of_naics(naics)
        votes[sic][s] = votes[sic].get(s, 0) + 1
    out = {}
    for sic, v in votes.items():
        if len(v) == 1:
            out[sic] = (next(iter(v)), "single")
            continue
        top = max(v.values())
        winners = [s for s, c in v.items() if c == top]
        out[sic] = (winners[0], "majority") if len(winners) == 1 else (None, "tie")
    return out


def prefix_sector_map(conc_rows, n):
    """Variant only. {n-digit SIC prefix (SIC zero-padded to 4 digits): (sector or None, kind)}: every concordance row whose SIC starts with the prefix votes, with the split-SIC majority/tie rule."""
    votes = {}
    for sic, naics in conc_rows:
        pre = "%04d" % sic
        pre = pre[:n]
        v = votes.setdefault(pre, {})
        sec = btos_sector_of_naics(naics)
        v[sec] = v.get(sec, 0) + 1
    out = {}
    for pre, v in votes.items():
        top = max(v.values())
        w = [x for x, c in v.items() if c == top]
        out[pre] = (w[0], "single" if len(v) == 1 else "majority") if len(w) == 1 else (None, "tie")
    return out


def read_concordance_xls(path):
    import xlrd                                              # old-format workbook; openpyxl cannot read it
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    rows, skipped = [], 0
    for i in range(1, sh.nrows):
        a, c = sh.row_values(i)[0], sh.row_values(i)[2]
        try:
            sic = int(float(a))
            nstr = str(int(float(str(c).strip())))
        except (TypeError, ValueError):
            skipped += 1                                     # 'Aux' and 'Null Set' rows, blanks
            continue
        if len(nstr) != 6:
            skipped += 1
            continue
        rows.append((sic, nstr))
    return rows, skipped


def p6_load_inputs(cache):
    """Hash-check and read the two hand-downloaded files. Raises Refused (with the reason) if either is missing or differs. No network."""
    paths = {}
    for rel, want in ((BTOS_REL, BTOS_SHA256), (CONC_REL, CONC_SHA256)):
        p = os.path.join(cache, *rel.split("/"))
        if not os.path.exists(p):
            raise Refused("P6 input missing: %s" % rel)
        got = sha256_of(open(p, "rb").read())
        if got != want:
            raise Refused("P6 input %s has sha256 %s, not the pinned %s" % (rel, got, want))
        paths[rel] = p
    import openpyxl
    wb = openpyxl.load_workbook(paths[BTOS_REL], read_only=True, data_only=True)
    sec = list(wb["Sector Estimates"].iter_rows(values_only=True))
    dates = list(wb["Collection and Reference Dates"].iter_rows(values_only=True))
    wb.close()
    conc, skipped = read_concordance_xls(paths[CONC_REL])
    return {"sector_header": sec[0], "sector_rows": sec[1:], "date_rows": dates[1:], "conc_rows": conc, "conc_skipped": skipped}


def p6_stats(firms_t, firms_p, gdp_g, ai, smap, min_firms=P6_MIN_FIRMS, drop_split=False, prefix_maps=None):
    """Per BTOS sector: the P2 median gap (p2_stats, unchanged) on that sector's firms, for sectors with at least min_firms firms in EACH window and a usable AI mean.
    drop_split drops every firm whose SIC is split across sectors (kinds 'majority' and 'tie'). Then Spearman and leave-one-sector-out."""
    def assign(firms):
        by, drop = {}, {"not_in_concordance": 0, "tie": 0, "split_dropped": 0, "sector_without_ai_mean": 0, "prefix_mapped": 0}
        for f in firms:
            m = smap.get(f["sic"])
            if m is None and prefix_maps:
                for n, pm in prefix_maps:                       # 3-digit prefix first, then 2-digit; the first prefix with any rows decides
                    pre = ("%04d" % f["sic"])[:n]
                    if pre in pm:
                        m = pm[pre]
                        drop["prefix_mapped"] += 1
                        break
            if m is None:
                drop["not_in_concordance"] += 1
                continue
            sector, kind = m
            if kind == "tie":
                drop["tie"] += 1
                continue
            if drop_split and kind != "single":
                drop["split_dropped"] += 1
                continue
            if sector not in ai or ai[sector]["mean"] is None:
                drop["sector_without_ai_mean"] += 1
                continue
            by.setdefault(sector, []).append(f)
        return by, drop
    bt, dt_ = assign(firms_t)
    bp, dp_ = assign(firms_p)
    rows, small = [], []
    for s in sorted(set(bt) | set(bp), key=int):
        nt, np_ = len(bt.get(s, [])), len(bp.get(s, []))
        if nt >= min_firms and np_ >= min_firms:
            rows.append({"sector": s, "ai_mean": ai[s]["mean"], "n_t": nt, "n_p": np_, "stat": p2_stats(bt[s], bp[s], gdp_g)["median_gap_pp"]})
        else:
            small.append((s, nt, np_))
    xs, ys = [r["ai_mean"] for r in rows], [r["stat"] for r in rows]
    rho = spearman(xs, ys)
    loo = []
    for i, r in enumerate(rows):
        loo.append((r["sector"], spearman(xs[:i] + xs[i + 1:], ys[:i] + ys[i + 1:])))
    vals = [v for _s, v in loo if v is not None]
    return {"rows": rows, "rho": rho, "n": len(rows), "loo": loo, "loo_min": min(vals) if vals else None, "loo_max": max(vals) if vals else None,
            "small": small, "drop_T": dt_, "drop_P": dp_, "n_firms_T": sum(r["n_t"] for r in rows), "n_firms_P": sum(r["n_p"] for r in rows)}


def compute_p6(cache, H, gdp_g):
    """H = {'T': firms, 'P': firms}, the P2 headline window sets. Returns a dict, or {'refused': reason}."""
    try:
        inp = p6_load_inputs(cache)
    except Refused as e:
        return {"refused": str(e)}
    cycles = btos_cycles(inp["date_rows"])
    ai, missing, used_cols = btos_ai_means(inp["sector_header"], inp["sector_rows"], cycles)
    smap = sic_sector_map(inp["conc_rows"])
    split = {s: v for s, v in smap.items() if v[1] != "single"}
    res = p6_stats(H["T"], H["P"], gdp_g, ai, smap)
    alt = p6_stats(H["T"], H["P"], gdp_g, ai, smap, drop_split=True)
    pre = p6_stats(H["T"], H["P"], gdp_g, ai, smap, prefix_maps=[(3, prefix_sector_map(inp["conc_rows"], 3)), (2, prefix_sector_map(inp["conc_rows"], 2))])
    sic_n = {w: {} for w in ("T", "P")}
    for w in ("T", "P"):
        for f in H[w]:
            if f["sic"] in split:
                sic_n[w][f["sic"]] = sic_n[w].get(f["sic"], 0) + 1
    return {"pre": pre, "ai": ai, "missing_cycles": missing, "used_cols": used_cols, "smap": smap, "res": res, "alt": alt, "n_sic_total": len(smap),
            "n_split": len(split), "n_tie": sum(1 for v in split.values() if v[1] == "tie"),
            "firms_in_split": {w: sum(sic_n[w].values()) for w in ("T", "P")}, "split_sics_with_firms": {w: len(sic_n[w]) for w in ("T", "P")},
            "n_firms": {w: len(H[w]) for w in ("T", "P")}, "conc_rows": len(inp["conc_rows"]), "conc_skipped": inp["conc_skipped"]}


TENK = ("10-K", "10-K/A")


def classify(cik, sic):
    if cik in AI_CIKS:
        return "AI"
    if sic is None:
        return "NOSIC"
    if in_ranges(sic, AI_SIC_RANGES):
        return "AI"
    if sic == REIT_SIC:
        return "REIT"
    if in_ranges(sic, (FIN_RANGE,)):
        return "FIN"
    if in_ranges(sic, (UTIL_RANGE,)):
        return "UTIL"
    return "HEAD"


def load_frames(cache):
    fr = {}
    for tag, per in frame_list():
        d = load_frame(cache, tag, per)
        if d is None:
            raise Refused("frame %s %s is not in the cache: run fetch --what frames" % (tag, per))
        fr[(tag, per)] = {r["cik"]: (r["val"], r["end"], r["accn"]) for r in d}
    return fr


def load_sub(cache, cik, forms=True):
    """SIC and, if asked, the accession number -> form map (main file plus every cached older page)."""
    p = subm_path(cache, cik)
    if not os.path.exists(p):
        return None
    j = read_gz_json(p)
    raw = str(j.get("sic", "")).strip()
    out = {"sic": int(raw) if raw.isdigit() and int(raw) > 0 else None, "name": j.get("name", ""), "fye": j.get("fiscalYearEnd", ""), "forms": {}}
    if forms:
        rec = j.get("filings", {}).get("recent", {})
        out["forms"] = dict(zip(rec.get("accessionNumber", []), rec.get("form", [])))
        for pg in j.get("filings", {}).get("files", []):
            q = older_path(cache, pg["name"])
            if os.path.exists(q):
                pj = read_gz_json(q)
                out["forms"].update(zip(pj.get("accessionNumber", []), pj.get("form", [])))
    return out


class Panel(object):
    pass


def tenk_val(fr, forms, tag, per, cik, stats=None):
    """The fact's value if its accession number resolves to a 10-K or 10-K/A in the submissions; None otherwise (counted in stats when given)."""
    t = fr[(tag, per)].get(cik)
    if t is None:
        return None
    form = forms.get(t[2])
    if form is None:
        if stats is not None:
            stats["unresolved"] = stats.get("unresolved", 0) + 1
        return None
    if form not in TENK:
        if stats is not None:
            stats["not_10k"] = stats.get("not_10k", 0) + 1
        return None
    return t[0]


def acquisition_drop(fr, forms, cik, w, stats):
    """Spec: a firm is dropped from a window if PropertyPlantAndEquipmentNet rose more than 25% in a year with PaymentsToAcquireBusinessesNetOfCashAcquired > 0. Tested for each year after
    the base year of the window (frames of every year in the window are fetched). A year with no usable PPE pair or no acquisition fact cannot trigger the drop (counted as untestable when an acquisition > 0 is present)."""
    b, e = WINDOWS[w]
    for y in range(b + 1, e + 1):
        a = tenk_val(fr, forms, ACQ_TAG, "CY%d" % y, cik)
        if a is None or not a > 0:
            continue
        p0 = tenk_val(fr, forms, PPE_TAG, "CY%dQ4I" % (y - 1), cik)
        p1 = tenk_val(fr, forms, PPE_TAG, "CY%dQ4I" % y, cik)
        if p0 is None or p1 is None or not p0 > 0:
            stats["untestable"] = stats.get("untestable", 0) + 1
            continue
        if p1 / p0 - 1.0 > 0.25:
            return True
    return False


def cash_ratio(fr, forms, cik, year):
    per = "CY%dQ4I" % year
    c = tenk_val(fr, forms, CASH_TAG, per, cik)
    if c is None:
        c = tenk_val(fr, forms, CASH_ALT_TAG, per, cik)
    a = tenk_val(fr, forms, ASSETS_TAG, per, cik)
    if c is None or a is None or not a > 0 or c < 0:
        return None
    return c / a


def build_panel(cache):
    fr = load_frames(cache)
    cands = panel_candidates(cache)
    P = Panel()
    P.cands = cands
    P.counts = {"candidates": len(cands)}
    inter_all = None
    sets = []
    for y in PANEL_YEARS:
        sets.append({c for c, t in fr[(CAPEX_TAG, "CY%d" % y)].items() if t[0] is not None and t[0] > 0 and int(t[1][5:7]) in FYE_MONTHS})
    inter_all = set.intersection(*sets)
    P.counts["ai_ciks_in_intersection"] = len(inter_all & set(AI_CIKS))
    P.counts["frame_facts_by_year"] = {y: len(fr[(CAPEX_TAG, "CY%d" % y)]) for y in PANEL_YEARS}
    firms, subs = {}, {}
    form_stats = {}
    n_no_sub = 0
    for cik in cands:
        s = load_sub(cache, cik)
        if s is None:
            n_no_sub += 1
            continue
        subs[cik] = s
        cap, ok, bad = {}, True, None
        for y in PANEL_YEARS:
            st = {}
            v = tenk_val(fr, s["forms"], CAPEX_TAG, "CY%d" % y, cik, st)
            if v is None:
                ok = False
                bad = "unresolved" if st.get("unresolved") else "not_10k"
                break
            cap[y] = v
        if not ok:
            form_stats[bad] = form_stats.get(bad, 0) + 1
            continue
        firms[cik] = {"cik": cik, "sic": s["sic"], "name": s["name"], "cap": cap, "cls": classify(cik, s["sic"])}
    P.counts["no_submission_file"] = n_no_sub
    P.counts["dropped_form_not_10k"] = form_stats.get("not_10k", 0)
    P.counts["dropped_form_unresolved"] = form_stats.get("unresolved", 0)
    P.counts["common_firms_10k"] = len(firms)
    cls = {}
    for f in firms.values():
        cls[f["cls"]] = cls.get(f["cls"], 0) + 1
    P.counts["by_class"] = cls
    P.firms = firms
    # windows
    P.window = {}
    P.window_stats = {}
    for klass in ("HEAD", "UTIL", "REIT"):
        for w in ("T", "P"):
            keep, dropped, st = [], 0, {}
            for f in firms.values():
                if f["cls"] != klass:
                    continue
                if acquisition_drop(fr, subs[f["cik"]]["forms"], f["cik"], w, st):
                    dropped += 1
                    continue
                keep.append(f)
            P.window[(klass, w)] = keep
            P.window_stats[(klass, w)] = {"dropped_acquisition_rule": dropped, "untestable": st.get("untestable", 0), "n": len(keep)}
    # cash ratio per window for the headline panel
    P.p4_missing = {}
    for w, yr in (("T", 2021), ("P", 2015)):
        have, miss = [], 0
        for f in P.window[("HEAD", w)]:
            r = cash_ratio(fr, subs[f["cik"]]["forms"], f["cik"], yr)
            if r is None:
                miss += 1
                continue
            f.setdefault("ratio", {})[w] = r
            have.append(f)
        P.p4_missing[w] = miss
    P.p4_firms = {w: [f for f in P.window[("HEAD", w)] if w in f.get("ratio", {})] for w in ("T", "P")}
    # coverage denominators: every positive CY2025 capex fact in the frame, classified by the submissions SIC (no form or fiscal-year-end filter)
    tot = {"HEAD": 0.0, "UTIL": 0.0, "REIT": 0.0, "FIN": 0.0, "AI": 0.0, "NOSIC": 0.0}
    cnt = {k: 0 for k in tot}
    for cik, t in fr[(CAPEX_TAG, "CY2025")].items():
        if t[0] is None or not t[0] > 0:
            continue
        if cik in firms:
            k = firms[cik]["cls"]
        else:
            s = load_sub(cache, cik, forms=False)
            k = classify(cik, s["sic"] if s else None)
        tot[k] += t[0]
        cnt[k] += 1
    P.denom_total = tot
    P.denom_count = cnt
    P.sic_fetch_dates = sorted({r["fetched_utc"][:10] for r in read_manifest(cache) if r["key"].startswith("subm:")})
    return P


def coverage(P, firms):
    s = sum(f["cap"][2025] for f in firms)
    ex_ai_all = sum(v for k, v in P.denom_total.items() if k not in ("AI", "NOSIC"))
    return {"n": len(firms), "capex_2025": s, "share_of_ex_ai_all": s / ex_ai_all if ex_ai_all else None, "share_of_headline_class": s / P.denom_total["HEAD"] if P.denom_total["HEAD"] else None}


# ------------------------------------------------------------------------------------------------------------------------
# registration (written BEFORE any statistic is computed)
# ------------------------------------------------------------------------------------------------------------------------
REG_HEADER = ("statement_id", "version", "superseded", "scored", "statement", "statistic", "support_if", "against_if", "treatment_window", "placebo_window", "prereg_sha256")
SCORES_HEADER = ("statement_id", "label", "primary_statistic", "primary_value", "unit", "statistics", "denominators", "caveats")
DETAIL_HEADER = ("statement_id", "item", "value", "unit")
VINTAGES_HEADER = ("source", "key", "url", "fetched_utc", "status", "bytes", "sha256", "note")
LABELS = ("SUPPORT", "AGAINST", "INCONCLUSIVE", "NOT BUILT", "NOT SCORED", "DESCRIPTIVE")
COMMITTED = ("README.md", "registered.csv", "scores.csv", "detail.csv", "vintages.csv")


def spec_text(root=None):
    with open(os.path.join(root or ROOT, *SPEC_FILE.split("/")), "rb") as fh:
        return fh.read()


def check_spec_hash(root=None, pinned=None):
    got = sha256_of(spec_text(root))
    if got != (pinned or SPEC_SHA256):
        raise Refused("the spec file hashes to %s, not the pinned %s: the build refuses to score" % (got, pinned or SPEC_SHA256))
    return got


def parse_spec_table(text):
    """The seven rows of the registered-statements table: id -> (statement, statistic, support_if, against_if), markdown emphasis removed."""
    rows = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*(CV1-P\d)\s*\|(.*)\|\s*$", line)
        if not m:
            continue
        cells = [c.strip().replace("**", "") for c in m.group(2).split("|")]
        if len(cells) != 4:
            raise Refused("registered table row %s does not have four cells" % m.group(1))
        rows[m.group(1)] = tuple(cells)
    if sorted(rows) != ["CV1-P%d" % i for i in range(1, 8)]:
        raise Refused("the registered table does not hold CV1-P1..P7: %s" % sorted(rows))
    return rows


def registered_text(spec_bytes, sha):
    rows = parse_spec_table(spec_bytes.decode("utf-8"))
    scored = {"CV1-P1": "yes", "CV1-P2": "yes", "CV1-P3": "yes", "CV1-P4": "yes", "CV1-P5": "yes", "CV1-P6": "descriptive-no-label", "CV1-P7": "no-inputs-not-yet-available"}
    out = ["# source: %s, registered statements version 2 (spec sha256 %s); written by bin/cv1_confidence_velocity.py build before any statistic is computed\n" % (SPEC_FILE, sha)]
    out.append(csv_line(REG_HEADER))
    for sid in sorted(rows):
        st, stat, sup, ag = rows[sid]
        out.append(csv_line([sid, 2, "no", scored[sid], st, stat, sup, ag, "2022Q4-2025Q4 (panel CY2022-CY2025)", "2015Q4-2019Q4 (panel CY2016-CY2019)", sha]))
    return "".join(out)


def write_registered(out, root=None, pinned=None):
    sha = check_spec_hash(root, pinned)
    p = os.path.join(out, "registered.csv")
    write_text(p, registered_text(spec_text(root), sha))
    return p, sha


# ------------------------------------------------------------------------------------------------------------------------
# the scoring run
# ------------------------------------------------------------------------------------------------------------------------
def f4(x):
    return "n/a" if x is None else "%.4f" % x


def f2(x):
    return "n/a" if x is None else "%.2f" % x


def bn(x):
    return "%.1f" % (x / 1e9)


def p1_variant(nrfi, subs, gdp, t0, t1, p0, p1, yt=3.0, yp=4.0):
    sh = {k: p1_residual_share(nrfi[k], [s[k] for s in subs], gdp[k]) for k in (t0, t1, p0, p1)}
    return {"share": sh, "change_T": (sh[t1] - sh[t0]) / yt, "change_P": (sh[p1] - sh[p0]) / yp, "gap": p1_gap(sh[t0], sh[t1], sh[p0], sh[p1], yt, yp)}


def compute_p1(cache):
    raw = os.path.join(cache, "raw")
    b1, b5 = os.path.join(raw, "Section1All_xls.xlsx"), os.path.join(raw, "Section5All_xls.xlsx")
    pub1, gq_n, _l = read_bea_sheet(b1, "T10105-Q")
    _p, gq_r, _l = read_bea_sheet(b1, "T10106-Q")
    _p, ga_n, _l = read_bea_sheet(b1, "T10105-A")
    _p, ga_r, _l = read_bea_sheet(b1, "T10106-A")
    pub5, q_n, lab = read_bea_sheet(b5, "T50305-Q")
    _p, q_r, _l = read_bea_sheet(b5, "T50306-Q")
    _p, a_n, _l = read_bea_sheet(b5, "T50305-A")
    _p, a_r, _l = read_bea_sheet(b5, "T50306-A")
    _p, e_n, _l = read_bea_sheet(b5, "T50505-A")
    _p, e_r, _l = read_bea_sheet(b5, "T50506-A")
    t0, t1 = Q_WINDOWS["T"]
    p0, p1 = Q_WINDOWS["P"]
    R = {"pub1": pub1, "pub5": pub5, "labels": {c: lab.get(c, "") for c in ("A008RC", "B935RC", "Y034RC", "B985RC", "C307RC", "W003RC", "E318RC")}}
    A_codes = ("Y034", "B985", "C307", "W003", "E318")
    B_codes = ("B935", "B985", "C307", "W003", "E318")
    out = {}
    for name, codes in (("A", A_codes), ("B", B_codes)):
        nom = p1_variant(q_n["A008RC"], [q_n[c + "RC"] for c in codes], gq_n["A191RC"], t0, t1, p0, p1)
        rea = p1_variant(q_r["A008RX"], [q_r[c + "RX"] for c in codes], gq_r["A191RX"], t0, t1, p0, p1)
        out[name] = {"nominal": nom, "real": rea, "label": label_p1(nom["gap"], rea["gap"])}
    c_codes = ("B935", "C275", "B985", "C307", "W003", "E318")
    nsubs = [e_n["B935RC"], e_n["C275RC"], a_n["B985RC"], a_n["C307RC"], a_n["W003RC"], a_n["E318RC"]]
    rsubs = [e_r["B935RX"], e_r["C275RX"], a_r["B985RX"], a_r["C307RX"], a_r["W003RX"], a_r["E318RX"]]
    nom = p1_variant(a_n["A008RC"], nsubs, ga_n["A191RC"], "2022", "2025", "2015", "2019")
    rea = p1_variant(a_r["A008RX"], rsubs, ga_r["A191RX"], "2022", "2025", "2015", "2019")
    out["C"] = {"nominal": nom, "real": rea, "label": label_p1(nom["gap"], rea["gap"])}
    R["variants"] = out
    R["comm_label"] = e_n.get("C275RC") is not None
    # untrimmed pieces for the memo: levels at the four dates (nominal, millions)
    R["levels"] = {c: {k: q_n[c + "RC"][k] for k in (p0, p1, t0, t1)} for c in ("A008", "B935", "Y034", "B985", "C307", "W003", "E318")}
    R["gdp_q"] = {k: gq_n["A191RC"][k] for k in (p0, p1, t0, t1)}
    R["gdp_a"] = {k: ga_n["A191RC"][k] for k in ("2015", "2016", "2019", "2022", "2025")}
    return R, ga_n["A191RC"], gq_n["A191RC"]


def compute_p3(cache, gdp_q):
    z1 = read_z1_series(os.path.join(cache, "raw", "FRB_Z1_csv.zip"), list(Z1_SERIES))
    check_z1_descriptions(z1)
    for sid, d in z1.items():
        if d["unit_mult"] != "Millions":
            raise Refused("%s is not in millions (%s)" % (sid, d["unit_mult"]))
    qs = sorted(set.intersection(*[set(d["values"]) for d in z1.values()]))
    stock = {q: sum(d["values"][q] for d in z1.values()) for q in qs}
    need = list(Q_WINDOWS["T"]) + list(Q_WINDOWS["P"])
    for q in need:
        if q not in stock:
            raise Refused("Z.1 has no value for %s in all four series" % q)
    st = p3_stats(stock, gdp_q)
    st["label"] = label_p3(st["diff_pp"], st["stock_fell"], st["stock_growth"], st["gdp_growth"])
    st["series"] = {sid: {"desc": d["desc"], "unit": d["unit"], "unit_mult": d["unit_mult"], "series_type": d["series_type"], "t0": d["values"][Q_WINDOWS["T"][0]], "t1": d["values"][Q_WINDOWS["T"][1]],
                          "p0": d["values"][Q_WINDOWS["P"][0]], "p1": d["values"][Q_WINDOWS["P"][1]]} for sid, d in z1.items()}
    st["stock"] = {q: stock[q] for q in need}
    st["last_quarter"] = qs[-1]
    return st


def compute_c30(cache, gdp_q):
    dc = read_c30_data_center(os.path.join(cache, "raw", "privsatime.xlsx"))
    memo = {}
    for lab, q in (("Dec-15", "2015Q4"), ("Dec-19", "2019Q4"), ("Dec-22", "2022Q4"), ("Dec-25", "2025Q4")):
        v = dc.get(lab)
        memo[lab] = {"value_millions": v, "pct_of_gdp": (100.0 * v / gdp_q[q]) if v is not None else None}
    return memo


def run_scores(cache, out_note=None):
    R = {}
    p1, gdp_a, gdp_q = compute_p1(cache)
    R["p1"] = p1
    R["p3"] = compute_p3(cache, gdp_q)
    R["c30"] = compute_c30(cache, gdp_q)
    gdp_g = {"T": ann_growth(gdp_a["2022"], gdp_a["2025"], 3), "P": ann_growth(gdp_a["2016"], gdp_a["2019"], 3)}
    R["gdp_g"] = gdp_g
    P = build_panel(cache)
    R["panel"] = P
    H = {w: P.window[("HEAD", w)] for w in ("T", "P")}
    R["p2"] = p2_stats(H["T"], H["P"], gdp_g)
    R["p2"]["label"] = label_p2(R["p2"]["median_gap_pp"], R["p2"]["weighted_gap_pp"])
    R["p2_strata"] = {}
    for klass in ("UTIL", "REIT"):
        a, b = P.window[(klass, "T")], P.window[(klass, "P")]
        R["p2_strata"][klass] = p2_stats(a, b, gdp_g) if len(a) >= 3 and len(b) >= 3 else None
    R["p4"] = p4_stats(P.p4_firms["T"], P.p4_firms["P"], gdp_g)
    R["p4"]["label"] = label_p4(R["p4"]["stat_pp"], R["p4"]["top_net_of_gdp_pp"])
    R["p5"] = p5_stats(H["T"], H["P"])
    R["p5"]["label"] = label_p5(R["p5"]["trimmed_gap_pp"], R["p5"]["untrimmed_gap_pp"])
    R["p6"] = compute_p6(cache, H, gdp_g)
    R["cov"] = {"P2_T": coverage(P, H["T"]), "P2_P": coverage(P, H["P"]), "P4_T": coverage(P, P.p4_firms["T"]), "P4_P": coverage(P, P.p4_firms["P"]),
                "UTIL_T": coverage(P, P.window[("UTIL", "T")]), "REIT_T": coverage(P, P.window[("REIT", "T")])}
    return R


def make_rows(R):
    P = R["panel"]
    scores, detail = [], []

    def D(sid, item, value, unit=""):
        detail.append([sid, item, value, unit])

    # ---- P1
    v = R["p1"]["variants"]
    A = v["A"]
    sec = "; ".join("variant %s: nominal gap %s, real gap %s -> %s" % (k, f4(v[k]["nominal"]["gap"]), f4(v[k]["real"]["gap"]), v[k]["label"]) for k in ("A", "B", "C"))
    scores.append(["CV1-P1", A["label"], "nominal_gap_variant_A", f4(A["nominal"]["gap"]), "pp per year",
                   "real_gap_variant_A=%s; %s" % (f4(A["real"]["gap"]), sec),
                   "national accounts, no firm counts; nominal residual share of GDP Q4 2025 = %s%%, Q4 2022 = %s%%, Q4 2019 = %s%%, Q4 2015 = %s%%" % tuple(f2(A["nominal"]["share"][q]) for q in ("2025Q4", "2022Q4", "2019Q4", "2015Q4")),
                   "variant A (primary) subtracts the whole information processing equipment line because communication equipment is not a separate line of quarterly Tables 5.3.5/5.3.6; see README"])
    for name in ("A", "B", "C"):
        for kind in ("nominal", "real"):
            x = v[name][kind]
            for q, s in x["share"].items():
                D("CV1-P1", "variant %s %s residual share of GDP %s" % (name, kind, q), f4(s), "percent")
            D("CV1-P1", "variant %s %s annualised change, treatment" % (name, kind), f4(x["change_T"]), "pp per year")
            D("CV1-P1", "variant %s %s annualised change, placebo" % (name, kind), f4(x["change_P"]), "pp per year")
            D("CV1-P1", "variant %s %s gap" % (name, kind), f4(x["gap"]), "pp per year")
        D("CV1-P1", "variant %s label" % name, v[name]["label"], "")
    for c, lv in R["p1"]["levels"].items():
        for q, x in lv.items():
            D("CV1-P1", "Table 5.3.5 %s level %s" % (c, q), "%d" % x, "millions of dollars, SAAR")
    for lab, m in R["c30"].items():
        D("CV1-P1", "memo: Census C30 private Data center %s" % lab, "blank" if m["value_millions"] is None else "%d" % m["value_millions"], "millions of dollars, SAAR (memo only, not subtracted)")
        D("CV1-P1", "memo: Census C30 Data center as share of GDP, %s" % lab, f4(m["pct_of_gdp"]), "percent (memo)")
    # ---- P2
    s2 = R["p2"]
    cv = R["cov"]
    scores.append(["CV1-P2", s2["label"], "median_gap", f4(s2["median_gap_pp"]), "pp per year",
                   "weighted_gap=%s; aggregate_gap=%s; median growth T=%s%% P=%s%%; GDP growth T=%s%% P=%s%%" % (f4(s2["weighted_gap_pp"]), f4(s2["aggregate_gap_pp"]), f4(pp(s2["T"]["median"])), f4(pp(s2["P"]["median"])), f4(pp(R["gdp_g"]["T"])), f4(pp(R["gdp_g"]["P"]))),
                   "firms T=%d P=%d; share of 2025 ex-AI capex covered T=%s P=%s; share of headline-class capex T=%s P=%s" % (s2["T"]["n"], s2["P"]["n"], f4(cv["P2_T"]["share_of_ex_ai_all"]), f4(cv["P2_P"]["share_of_ex_ai_all"]), f4(cv["P2_T"]["share_of_headline_class"]), f4(cv["P2_P"]["share_of_headline_class"])),
                   "worldwide consolidated capex against domestic GDP; population is US-GAAP USD filers with the tag, not all listed firms"])
    for w in ("T", "P"):
        x = s2[w]
        D("CV1-P2", "window %s firms" % w, x["n"], "firms")
        D("CV1-P2", "window %s median annualised capex growth" % w, f4(pp(x["median"])), "percent per year")
        D("CV1-P2", "window %s capex-weighted mean growth" % w, f4(pp(x["weighted"])), "percent per year")
        D("CV1-P2", "window %s aggregate (sum) growth" % w, f4(pp(x["aggregate"])), "percent per year")
        D("CV1-P2", "window %s base-year capex of panel" % w, bn(x["base_capex"]), "billions of dollars")
        D("CV1-P2", "window %s annualised nominal GDP growth (calendar years)" % w, f4(pp(R["gdp_g"][w])), "percent per year")
        ws = P.window_stats[("HEAD", w)]
        D("CV1-P2", "window %s dropped by the acquisition rule (PPE up more than 25%% in a year with acquisitions > 0)" % w, ws["dropped_acquisition_rule"], "firms")
        D("CV1-P2", "window %s acquisition-rule years untestable (acquisition > 0 but no usable PPE pair)" % w, ws["untestable"], "firm-years")
    for k, lab in (("T", "treatment"), ("P", "placebo")):
        c = cv["P2_" + k]
        D("CV1-P2", "%s panel CY2025 capex" % lab, bn(c["capex_2025"]), "billions of dollars")
        D("CV1-P2", "%s panel share of 2025 ex-AI capex (AI complex and firms without a SIC out; finance, utilities, REITs in)" % lab, f4(c["share_of_ex_ai_all"]), "fraction")
        D("CV1-P2", "%s panel share of 2025 headline-class capex (AI complex, finance, utilities, REITs, no-SIC out)" % lab, f4(c["share_of_headline_class"]), "fraction")
    for k, v_ in P.counts.items():
        D("CV1-P2", "panel waterfall: " + k, v_, "")
    for k, n in sorted(P.denom_count.items()):
        D("CV1-P2", "CY2025 frame, positive capex, class %s: firms" % k, n, "firms")
        D("CV1-P2", "CY2025 frame, positive capex, class %s: capex" % k, bn(P.denom_total[k]), "billions of dollars")
    for klass in ("UTIL", "REIT"):
        x = R["p2_strata"][klass]
        for w in ("T", "P"):
            D("CV1-P2", "stratum %s window %s firms" % (klass, w), len(P.window[(klass, w)]), "firms")
        if x is None:
            D("CV1-P2", "stratum %s" % klass, "fewer than 3 firms in a window: not computed", "")
        else:
            D("CV1-P2", "stratum %s median gap" % klass, f4(x["median_gap_pp"]), "pp per year")
            D("CV1-P2", "stratum %s weighted gap" % klass, f4(x["weighted_gap_pp"]), "pp per year")
            D("CV1-P2", "stratum %s label rule applied, for information" % klass, label_p2(x["median_gap_pp"], x["weighted_gap_pp"]), "")
    # ---- P3
    p3 = R["p3"]
    scores.append(["CV1-P3", p3["label"], "difference_in_change", f4(p3["diff_pp"]), "pp (Q4-to-Q4 change, treatment minus placebo, not annualised)",
                   "ratio Q4 2015=%s%% Q4 2019=%s%% Q4 2022=%s%% Q4 2025=%s%%; change T=%s change P=%s; stock Q4 2022=%s bn Q4 2025=%s bn (fell=%s); stock growth=%s%% GDP growth=%s%%" % (
                       f4(p3["ratio_p0"]), f4(p3["ratio_p1"]), f4(p3["ratio_t0"]), f4(p3["ratio_t1"]), f4(p3["change_T_pp"]), f4(p3["change_P_pp"]),
                       "%.1f" % (p3["stock"]["2022Q4"] / 1000.0), "%.1f" % (p3["stock"]["2025Q4"] / 1000.0), "yes" if p3["stock_fell"] else "no", f4(100 * p3["stock_growth"]), f4(100 * p3["gdp_growth"])),
                   "four Z.1 series, one sector (nonfinancial corporate business), 2 windows of Q4 values; GDP = Table 1.1.5 Q4 SAAR",
                   "sector includes equity REITs and nonfinancial AI filers, excludes financial holding companies and foreign subsidiaries; time and savings deposits are a remainder; the SOI benchmark year is not named in any file fetched"])
    for sid, d in p3["series"].items():
        D("CV1-P3", "%s description" % sid, d["desc"], "")
        D("CV1-P3", "%s Q4 2015 / Q4 2019 / Q4 2022 / Q4 2025" % sid, "%d / %d / %d / %d" % (d["p0"], d["p1"], d["t0"], d["t1"]), "millions of dollars")
    D("CV1-P3", "sum of the four series, Q4 2015 / Q4 2019 / Q4 2022 / Q4 2025", " / ".join("%d" % p3["stock"][q] for q in ("2015Q4", "2019Q4", "2022Q4", "2025Q4")), "millions of dollars")
    D("CV1-P3", "last quarter in the Z.1 file for all four series", p3["last_quarter"], "")
    # ---- P4
    p4 = R["p4"]
    t, p = p4["T"], p4["P"]
    scores.append(["CV1-P4", p4["label"], "difference_in_top_minus_bottom", f4(p4["stat_pp"]), "pp per year",
                   "top-minus-bottom T=%s P=%s; top tercile growth net of GDP (T)=%s; terciles T: top n=%d bottom n=%d middle n=%d; P: top n=%d bottom n=%d middle n=%d" % (
                       f4(p4["top_minus_bottom_T_pp"]), f4(p4["top_minus_bottom_P_pp"]), f4(p4["top_net_of_gdp_pp"]), t["top"]["n"], t["bottom"]["n"], t["middle"]["n"] if t["middle"] else 0, p["top"]["n"], p["bottom"]["n"], p["middle"]["n"] if p["middle"] else 0),
                   "firms with cash and assets T=%d P=%d (of %d and %d in the P2 sets); 2-digit SIC groups used T=%d P=%d; firms in groups of fewer than 3 dropped T=%d P=%d; share of 2025 ex-AI capex covered T=%s P=%s" % (
                       len(P.p4_firms["T"]), len(P.p4_firms["P"]), len(P.window[("HEAD", "T")]), len(P.window[("HEAD", "P")]), t["n_sic2_groups_used"], p["n_sic2_groups_used"], t["dropped_small_sic2"], p["dropped_small_sic2"],
                       f4(cv["P4_T"]["share_of_ex_ai_all"]), f4(cv["P4_P"]["share_of_ex_ai_all"])),
                   "terciles formed separately in each window; cash is GAAP cash and equivalents, not the Z.1 deposit concept"])
    for w, x in (("T", t), ("P", p)):
        for tier in ("bottom", "middle", "top"):
            if x[tier]:
                D("CV1-P4", "window %s %s tercile firms" % (w, tier), x[tier]["n"], "firms")
                D("CV1-P4", "window %s %s tercile capex-weighted growth" % (w, tier), f4(pp(x[tier]["weighted"])), "percent per year")
                D("CV1-P4", "window %s %s tercile base-year capex" % (w, tier), bn(x[tier]["base_capex"]), "billions of dollars")
        D("CV1-P4", "window %s firms without usable cash and assets (dropped)" % w, P.p4_missing[w], "firms")
    # ---- P5
    p5 = R["p5"]
    scores.append(["CV1-P5", p5["label"], "trimmed_gap", f4(p5["trimmed_gap_pp"]), "pp per year",
                   "untrimmed_gap=%s; median growth high-trimmed T=%s%% P=%s%%; high-untrimmed T=%s%% P=%s%%; low T=%s%% P=%s%%" % (
                       f4(p5["untrimmed_gap_pp"]), f4(pp(p5["T"]["med_high_trimmed"])), f4(pp(p5["P"]["med_high_trimmed"])), f4(pp(p5["T"]["med_high"])), f4(pp(p5["P"]["med_high"])), f4(pp(p5["T"]["med_low"])), f4(pp(p5["P"]["med_low"]))),
                   "firms T: high untrimmed=%d trimmed=%d (removed %d) low=%d; P: high untrimmed=%d trimmed=%d (removed %d) low=%d; high+low firms outside the two bins (SIC 1500-1799 and 4900+, 6000+, 9000+) are not used" % (
                       p5["T"]["n_high"], p5["T"]["n_high_trimmed"], p5["T"]["n_removed"], p5["T"]["n_low"], p5["P"]["n_high"], p5["P"]["n_high_trimmed"], p5["P"]["n_removed"], p5["P"]["n_low"]),
                   "SIC bins are not an irreversibility measure; the removed energy, refining, auto and aircraft SICs are reported separately in detail.csv"])
    for w in ("T", "P"):
        x = p5[w]
        for k in ("n_high", "n_high_trimmed", "n_removed", "n_low"):
            D("CV1-P5", "window %s %s" % (w, k), x[k], "firms")
        D("CV1-P5", "window %s median growth of the removed SICs" % w, f4(pp(x["med_removed"])) if x["med_removed"] is not None else "n/a", "percent per year")
    # ---- P6, P7
    p6 = R["p6"]
    if "refused" in p6:
        scores.append(["CV1-P6", "NOT BUILT", "", "", "", "", "none",
                       "P6 refused: %s. The two Census files are never fetched by this script (www.census.gov answered 403 to a script on 13 Nov 2026); place them in the cache and rebuild" % p6["refused"]])
    else:
        r6, a6, v6 = p6["res"], p6["alt"], p6["pre"]
        f = lambda x: "n/a" if x is None else f4(x)
        scores.append(["CV1-P6", "DESCRIPTIVE", "spearman_sector_AI_use_vs_P2_median_gap", f(r6["rho"]), "rank correlation",
                       "n_sectors=%d; leave_one_sector_out_range=[%s, %s]; variant dropping every firm on a split SIC: n_sectors=%d spearman=%s leave_one_out_range=[%s, %s]; POST HOC variant (not the headline; added after the headline was seen) mapping firms not in the concordance through their 3-digit then 2-digit SIC prefix: n_sectors=%d spearman=%s leave_one_out_range=[%s, %s]" % (
                           r6["n"], f(r6["loo_min"]), f(r6["loo_max"]), a6["n"], f(a6["rho"]), f(a6["loo_min"]), f(a6["loo_max"]), v6["n"], f(v6["rho"]), f(v6["loo_min"]), f(v6["loo_max"])),
                       "sectors kept (at least %d firms in each of the treatment and placebo P2 headline panels) = %d of %d BTOS sectors with an AI mean; firms in kept sectors T=%d of %d, P=%d of %d; "
                       "dropped before the sector filter T: %d not in concordance, %d on tied SICs; P: %d not in concordance, %d on tied SICs" % (
                           P6_MIN_FIRMS, r6["n"], len([1 for v in p6["ai"].values() if v["mean"] is not None]), r6["n_firms_T"], p6["n_firms"]["T"], r6["n_firms_P"], p6["n_firms"]["P"],
                           r6["drop_T"]["not_in_concordance"], r6["drop_T"]["tie"], r6["drop_P"]["not_in_concordance"], r6["drop_P"]["tie"]),
                       "descriptive only, no label by registration; the BTOS question measures AI use in producing goods or services, not decision support, which is the thesis's own channel; sector cross-section, not causal; "
                       "AI use is a mean over %d unsuppressed cycles of 2024-2025 (cycles 202521 to 202523 are not in the workbook and are not filled); SIC is current, mapped through the 1987-SIC to 2002-NAICS concordance" % len(p6["used_cols"])])
        for rr in r6["rows"]:
            sid = rr["sector"]
            D("CV1-P6", "sector %s AI use mean" % sid, f4(rr["ai_mean"]), "percent of firms")
            D("CV1-P6", "sector %s cycles used / suppressed" % sid, "%d / %d" % (len(p6["ai"][sid]["used"]), len(p6["ai"][sid]["suppressed"])), "cycles")
            D("CV1-P6", "sector %s firms treatment / placebo" % sid, "%d / %d" % (rr["n_t"], rr["n_p"]), "firms")
            D("CV1-P6", "sector %s P2 median gap" % sid, f4(rr["stat"]), "pp per year")
        for sid in sorted(p6["ai"], key=int):
            v = p6["ai"][sid]
            D("CV1-P6", "all-sector table: sector %s AI use mean (cycles used %d, suppressed %d)" % (sid, len(v["used"]), len(v["suppressed"])), f4(v["mean"]) if v["mean"] is not None else "n/a", "percent of firms")
        for sid, nt, np_ in r6["small"]:
            D("CV1-P6", "sector %s dropped by the firm filter (firms treatment / placebo)" % sid, "%d / %d" % (nt, np_), "firms")
        for sid, v in r6["loo"]:
            D("CV1-P6", "leave out sector %s: spearman" % sid, f(v), "rank correlation")
        D("CV1-P6", "spearman", f(r6["rho"]), "rank correlation")
        D("CV1-P6", "sectors kept", r6["n"], "sectors")
        D("CV1-P6", "variant dropping split-SIC firms: spearman", f(a6["rho"]), "rank correlation")
        D("CV1-P6", "variant dropping split-SIC firms: sectors kept", a6["n"], "sectors")
        for w in ("T", "P"):
            D("CV1-P6", "window %s panel firms" % w, p6["n_firms"][w], "firms")
            D("CV1-P6", "window %s firms not in the concordance (dropped)" % w, r6["drop_" + w]["not_in_concordance"], "firms")
            D("CV1-P6", "window %s firms on tied SICs (dropped)" % w, r6["drop_" + w]["tie"], "firms")
            D("CV1-P6", "window %s firms in sectors without an AI mean (dropped)" % w, r6["drop_" + w]["sector_without_ai_mean"], "firms")
            D("CV1-P6", "window %s firms on split SICs (kept in the main result unless tied)" % w, p6["firms_in_split"][w], "firms")
        D("CV1-P6", "POST HOC prefix-fallback variant: spearman", f(v6["rho"]), "rank correlation")
        D("CV1-P6", "POST HOC prefix-fallback variant: sectors kept", v6["n"], "sectors")
        D("CV1-P6", "POST HOC prefix-fallback variant: leave-one-out minimum / maximum", "%s / %s" % (f(v6["loo_min"]), f(v6["loo_max"])), "rank correlation")
        for rr in v6["rows"]:
            sid = rr["sector"]
            D("CV1-P6", "prefix variant sector %s AI use mean" % sid, f4(rr["ai_mean"]), "percent of firms")
            D("CV1-P6", "prefix variant sector %s firms treatment / placebo" % sid, "%d / %d" % (rr["n_t"], rr["n_p"]), "firms")
            D("CV1-P6", "prefix variant sector %s P2 median gap" % sid, f4(rr["stat"]), "pp per year")
        for sid, v in v6["loo"]:
            D("CV1-P6", "prefix variant leave out sector %s: spearman" % sid, f(v), "rank correlation")
        for sid, nt, np_ in v6["small"]:
            D("CV1-P6", "prefix variant sector %s dropped by the firm filter (firms treatment / placebo)" % sid, "%d / %d" % (nt, np_), "firms")
        for w in ("T", "P"):
            D("CV1-P6", "prefix variant window %s firms mapped through a prefix" % w, v6["drop_" + w]["prefix_mapped"], "firms")
            D("CV1-P6", "prefix variant window %s firms still unmapped (dropped)" % w, v6["drop_" + w]["not_in_concordance"], "firms")
            D("CV1-P6", "prefix variant window %s firms on tied SICs or tied prefixes (dropped)" % w, v6["drop_" + w]["tie"], "firms")
        D("CV1-P6", "concordance SICs", p6["n_sic_total"], "SICs")
        D("CV1-P6", "concordance SICs split across sectors (of which tied)", "%d (%d)" % (p6["n_split"], p6["n_tie"]), "SICs")
    scores.append(["CV1-P7", "NOT SCORED", "", "", "", "", "none",
                   "inputs not yet available: GoodwillImpairmentLoss for CY2026 to CY2028 (the CY2028 10-Ks are filed from about February 2029); first scorable about April 2029 per the spec"])
    return scores, detail


def vintage_rows(cache):
    rows = []
    man = read_manifest(cache)
    last = {}
    for r in man:
        last[r["key"]] = r
    for k in ("bea1", "bea5", "z1", "c30"):
        r = last[k]
        rows.append([k, k, r["url"], r["fetched_utc"], r["status"], r["bytes"], r["sha256"], "fetched_utc backfilled from the file's modification time" if k in ("bea1", "bea5", "z1", "c30") else ""])
    for key in sorted(last):
        if key.startswith("frame:") or key.startswith("fed-series"):
            r = last[key]
            rows.append(["sec-frame" if key.startswith("frame:") else "fed-series-page", key, r["url"], r["fetched_utc"], r["status"], r["bytes"], r["sha256"], ""])
    for prefix, label in (("subm:", "sec-submissions"), ("older:", "sec-submissions-older-pages")):
        sel = sorted((r for key, r in last.items() if key.startswith(prefix)), key=lambda r: r["key"])
        h = hashlib.sha256("".join(r["sha256"] for r in sel).encode()).hexdigest()
        dates = sorted(r["fetched_utc"] for r in sel)
        rows.append([label, prefix + "*", "https://data.sec.gov/submissions/", "%s .. %s" % (dates[0], dates[-1]) if dates else "", 200, sum(int(r["bytes"]) for r in sel), h,
                     "%d files; sha256 is of the concatenated per-file sha256 values in key order" % len(sel)])
    rows.append(["census-btos", "btos-downloads-page", "https://www.census.gov/hfp/btos/downloads/", "2026-11-13T14:31:01Z", 403, 0, "", "HTTP 403; STOP_www_census_gov written; a first request to the same path without the trailing slash answered 301 (250 bytes)"])
    for key, url, rel, sha in (("btos-ai-core-questions", BTOS_URL, BTOS_REL, BTOS_SHA256), ("sic1987-naics2002-concordance", CONC_URL, CONC_REL, CONC_SHA256)):
        p = os.path.join(cache, *rel.split("/"))
        rows.append(["census-p6-input", key, url, "2026-11-15", "hand download", os.path.getsize(p) if os.path.exists(p) else 0, sha,
                     "downloaded by the principal through a browser on 15 Nov 2026 and placed in the cache; never fetched by this script"])
    return rows


# ------------------------------------------------------------------------------------------------------------------------
# README
# ------------------------------------------------------------------------------------------------------------------------
def p6_readme(R):
    p6 = R["p6"]
    out = []
    if "refused" in p6:
        out.append("NOT BUILT. %s. The build reads the two hand-downloaded Census files from the cache (`%s`, `%s`), checks their sha256 and never fetches them; www.census.gov answered 403 to a script on 13 Nov 2026 and the STOP latch stays.\n" % (p6["refused"], BTOS_REL, CONC_REL))
        return out
    r6, a6, v6 = p6["res"], p6["alt"], p6["pre"]
    f = lambda x: "n/a" if x is None else f4(x)
    out.append("Descriptive only: no label, by registration. The BTOS question measures AI use in producing goods or services, not AI used for decision support, which is the thesis's own channel. A rank correlation across sectors says nothing about cause, and capex is worldwide consolidated while BTOS covers US business units.\n")
    out.append("Inputs (never fetched by the script; downloaded by the principal through the desktop app's browser on 15 Nov 2026, after www.census.gov refused the folder index to a script on 13 Nov (HTTP 403); placed in the cache and checked against the pinned sha256, and the build writes NOT BUILT instead if a file is missing or differs):\n")
    out.append("- Census BTOS, \"AI Core Questions (Original)\" workbook, sheets `Sector Estimates` and `Collection and Reference Dates`; Last-Modified 3 Nov 2026; %s; sha256 `%s`." % (BTOS_URL, BTOS_SHA256))
    out.append("- Census 1987 SIC to 2002 NAICS concordance (old-format .xls, read with xlrd); %s; sha256 `%s`.\n" % (CONC_URL, CONC_SHA256))
    out.append("Method. (1) AI use per BTOS sector: Question ID %d (\"...use Artificial Intelligence (AI) in producing goods or services?\"), answer Yes, the mean of the unsuppressed percentages over the %d cycles whose label begins 2024 or 2025 and whose collection ended before 17 Nov 2025 (%s to %s); suppressed cells (\"S\") are skipped; the in-window cycles missing from the workbook (%s) are not filled; nothing from the 4 Dec 2025 new series. (2) Firm to sector: current SIC from the submissions file, through the concordance to NAICS 2002, the first two digits, then BTOS grouping (31/32/33 to 31, 44/45 to 44, 48/49 to 48). (3) Sector statistic: the P2 median gap (treatment minus placebo of firm annualised capex growth net of annualised nominal GDP growth, `p2_stats`, unchanged) on the sector's firms of the P2 headline window sets; a sector is kept with at least %d firms in each of the two window sets. (4) Spearman rank correlation of sector AI mean and sector statistic across kept sectors, and the range when each kept sector is left out in turn.\n" % (
        BTOS_QID, len(p6["used_cols"]), p6["used_cols"][-1], p6["used_cols"][0], ", ".join(p6["missing_cycles"]) or "none", P6_MIN_FIRMS))
    out.append("Result. Spearman %s across n = %d sectors (of %d BTOS sectors with an AI mean); leave-one-sector-out range [%s, %s]. Variant dropping every firm on a split SIC: Spearman %s across n = %d sectors, leave-one-out range [%s, %s]. Firms in the kept sectors: treatment %d of %d P2 headline firms, placebo %d of %d.\n" % (
        f(r6["rho"]), r6["n"], len([1 for v in p6["ai"].values() if v["mean"] is not None]), f(r6["loo_min"]), f(r6["loo_max"]), f(a6["rho"]), a6["n"], f(a6["loo_min"]), f(a6["loo_max"]),
        r6["n_firms_T"], p6["n_firms"]["T"], r6["n_firms_P"], p6["n_firms"]["P"]))
    out.append("| BTOS sector | AI use mean (%) | cycles used | cycles suppressed | firms treatment | firms placebo | P2 median gap (pp/yr) | Spearman with this sector left out |")
    out.append("|---|---|---|---|---|---|---|---|")
    loo = dict(r6["loo"])
    for rr in r6["rows"]:
        v = p6["ai"][rr["sector"]]
        out.append("| %s | %s | %d | %d | %d | %d | %s | %s |" % (rr["sector"], f4(rr["ai_mean"]), len(v["used"]), len(v["suppressed"]), rr["n_t"], rr["n_p"], f4(rr["stat"]), f(loo[rr["sector"]])))
    out.append("")
    out.append("All BTOS sectors, before the firm filter (mean over unsuppressed cycles; denominators are the cycles):\n")
    out.append("| BTOS sector | AI use mean (%) | cycles used | cycles suppressed | in the kept set |")
    out.append("|---|---|---|---|---|")
    kept = {rr["sector"] for rr in r6["rows"]}
    for sid in sorted(p6["ai"], key=int):
        v = p6["ai"][sid]
        out.append("| %s | %s | %d | %d | %s |" % (sid, f4(v["mean"]) if v["mean"] is not None else "n/a (all suppressed)", len(v["used"]), len(v["suppressed"]), "yes" if sid in kept else "no"))
    out.append("")
    out.append("Sectors with an AI mean but fewer than %d firms in a window (treatment / placebo firms): %s.\n" % (P6_MIN_FIRMS, "; ".join("%s (%d / %d)" % x for x in r6["small"]) or "none"))
    out.append("Post hoc robustness variant (not the headline, not a registered statistic). The headline uses the rule fixed before the result was seen: a firm whose SIC is not in the concordance is dropped. The prefix-fallback variant was added by the supervisor AFTER seeing the headline (n = %d sectors, Spearman %s), because %d of %d treatment-panel firms (%s%%) were unmapped, and these are EDGAR group-level SIC codes (all end in 0). It is a robustness reading chosen post hoc. Rule: a firm whose SIC is not in the concordance is mapped through its 3-digit SIC prefix (every concordance row whose SIC starts with that prefix votes, with the same strict-majority and tie rule as for split SICs); a firm whose 3-digit prefix has no rows is mapped through its 2-digit prefix the same way; firms still unmapped (or on a tie) are dropped and counted. The sector filter (at least %d firms in each window set) is then re-applied.\n" % (
        r6["n"], f(r6["rho"]), r6["drop_T"]["not_in_concordance"], p6["n_firms"]["T"], "%.0f" % (100.0 * r6["drop_T"]["not_in_concordance"] / p6["n_firms"]["T"]), P6_MIN_FIRMS))
    out.append("Variant result. Spearman %s across n = %d sectors; leave-one-sector-out range [%s, %s]. Firms in kept sectors: treatment %d of %d, placebo %d of %d. Mapped through a prefix (treatment / placebo): %d / %d; still unmapped and dropped: %d / %d; dropped on ties (SIC or prefix): %d / %d.\n" % (
        f(v6["rho"]), v6["n"], f(v6["loo_min"]), f(v6["loo_max"]), v6["n_firms_T"], p6["n_firms"]["T"], v6["n_firms_P"], p6["n_firms"]["P"],
        v6["drop_T"]["prefix_mapped"], v6["drop_P"]["prefix_mapped"], v6["drop_T"]["not_in_concordance"], v6["drop_P"]["not_in_concordance"], v6["drop_T"]["tie"], v6["drop_P"]["tie"]))
    out.append("| BTOS sector (variant) | AI use mean (%) | firms treatment | firms placebo | P2 median gap (pp/yr) | Spearman with this sector left out |")
    out.append("|---|---|---|---|---|---|")
    vloo = dict(v6["loo"])
    for rr in v6["rows"]:
        out.append("| %s | %s | %d | %d | %s | %s |" % (rr["sector"], f4(rr["ai_mean"]), rr["n_t"], rr["n_p"], f4(rr["stat"]), f(vloo[rr["sector"]])))
    out.append("")
    out.append("Variant sectors with an AI mean but fewer than %d firms in a window (treatment / placebo): %s.\n" % (P6_MIN_FIRMS, "; ".join("%s (%d / %d)" % x for x in v6["small"]) or "none"))
    out.append("Mapping counts. The concordance has %d distinct SICs (%d usable rows; %d non-numeric rows skipped); %d are split across BTOS sectors (%d of them tied, so their firms are dropped). Firms on split SICs: treatment %d firms on %d SICs of %d, placebo %d firms on %d SICs of %d (tied SICs are dropped in the main result, majority-sector SICs are kept; the variant above drops all of them). Dropped before the sector filter, treatment / placebo: not in the concordance %d / %d, on tied SICs %d / %d, in sectors with no AI mean %d / %d." % (
        p6["n_sic_total"], p6["conc_rows"], p6["conc_skipped"], p6["n_split"], p6["n_tie"], p6["firms_in_split"]["T"], p6["split_sics_with_firms"]["T"], p6["n_firms"]["T"], p6["firms_in_split"]["P"], p6["split_sics_with_firms"]["P"], p6["n_firms"]["P"],
        r6["drop_T"]["not_in_concordance"], r6["drop_P"]["not_in_concordance"], r6["drop_T"]["tie"], r6["drop_P"]["tie"], r6["drop_T"]["sector_without_ai_mean"], r6["drop_P"]["sector_without_ai_mean"]))
    out.append("")
    return out


def readme_text(R, scores, vint, sha):
    P = R["panel"]
    S = {r[0]: r for r in scores}
    v = R["p1"]["variants"]
    p2, p3, p4, p5 = R["p2"], R["p3"], R["p4"], R["p5"]
    cv = R["cov"]
    A = []
    a = A.append
    a("# CV1: did AI-driven managerial confidence move firms outside the AI complex to commit idle cash to capex? Registered statements P1 to P6 (build of 13 Nov 2026)\n")
    a("This folder holds the one-time scoring of statements CV1-P1 to CV1-P6 of the registration `%s` (version 2, registered blind on 13 Nov 2026; sha256 `%s`). `registered.csv` was written by the build before any statistic was computed, from that file; the build refuses to score if the file's hash differs from the one pinned in `bin/cv1_confidence_velocity.py`. P7 is not scored (its inputs do not exist yet). The numbers are derived from public US government data (BEA, Federal Reserve Board, Census Bureau, SEC); the raw files are not redistributed and sit in a gitignored cache.\n" % (SPEC_FILE, sha))
    a("What a label means. The labels are asymmetric by registration. AGAINST on P1 to P3 refutes the stage-4 leg (committed capital outside the AI complex accelerated; liquidity was drawn down) on this free data. SUPPORT says only that the numbers are consistent with that leg. It is never evidence that AI lowered managers' uncertainty, because no statistic here identifies a fall in uncertainty. INCONCLUSIVE means neither condition was met. The treatment window (2022 to 2025) also contains the CHIPS 25% credit, the clean-energy credits, restored 100% bonus depreciation, power and factory construction and acquisition arithmetic; none is separated out.\n")
    a("Capex in P2 to P5 is worldwide consolidated capex of US-GAAP USD filers; GDP is domestic. This is a known limit and applies to every number below.\n")
    a("## Result\n")
    a("| statement | label | statistic | value | denominators |")
    a("|---|---|---|---|---|")
    for sid in ("CV1-P1", "CV1-P2", "CV1-P3", "CV1-P4", "CV1-P5", "CV1-P6", "CV1-P7"):
        r = S[sid]
        a("| %s | %s | %s | %s %s | %s |" % (sid, r[1], r[2] or "-", r[3] or "-", r[4], (r[6] or "-").replace("|", "/")))
    a("")
    a("Full statistics for each statement are in `scores.csv` (one row per statement); every supporting number is a row of `detail.csv`.\n")
    a("## What each statement computes, exactly\n")
    a("### P1: business investment outside the AI build-out and the subsidised factory and power build, share of GDP\n")
    a("Source: BEA NIPA Tables 5.3.5 (nominal) and 5.3.6 (chained 2017 dollars) from `Section5All_xls.xlsx` (%s), and Tables 1.1.5 and 1.1.6 from `Section1All_xls.xlsx` (%s). Quarterly, seasonally adjusted annual rates. Residual = nonresidential fixed investment (A008RC) less the subtracted lines; share = residual over GDP (A191RC), in percent. Annualised pp change = (share at the end quarter minus share at the start quarter) divided by the years (3 for 2022Q4 to 2025Q4, 4 for 2015Q4 to 2019Q4). Statistic = treatment change minus placebo change. The real version is the same arithmetic on chained dollars (A008RX less the same lines over A191RX); chained dollars are not additive, so it is approximate. SUPPORT if both gaps are at least +0.15 pp per year, AGAINST if both are at most 0, otherwise INCONCLUSIVE.\n" % (R["p1"]["pub5"].replace("Data published ", "published "), R["p1"]["pub1"].replace("Data published ", "published ")))
    a("The registration names communication equipment as a subtraction. In this vintage the quarterly Tables 5.3.5 and 5.3.6 no longer show it as a line: it sits inside `Other` information processing equipment together with medical equipment and instruments, nonmedical instruments, photocopy and office equipment. Three variants were computed and all three are in `scores.csv`:\n")
    a("- Variant A (the primary, which sets the label): subtract the whole Information processing equipment line (Y034) with software (B985), manufacturing structures (C307), power and communication structures (W003) and mining exploration, shafts and wells (E318). It removes communication equipment as registered, and also medical equipment and instruments and the other small lines.")
    a("- Variant B: subtract computers and peripheral equipment (B935) only, with the same four other lines. Communication equipment stays in the residual.")
    a("- Variant C: the exact registered list (B935, communication equipment C275 from Tables 5.5.5 and 5.5.6, B985, C307, W003, E318) on annual data (Tables 5.3.5-A, 5.3.6-A, 5.5.5-A, 5.5.6-A, 1.1.5-A, 1.1.6-A, calendar years 2022 to 2025 and 2015 to 2019), because Tables 5.5.5 and 5.5.6 are annual only.")
    a("")
    a("| variant | nominal gap | real gap | label if it were primary |")
    a("|---|---|---|---|")
    for k in ("A", "B", "C"):
        a("| %s | %s | %s | %s |" % (k, f4(v[k]["nominal"]["gap"]), f4(v[k]["real"]["gap"]), v[k]["label"]))
    a("")
    a("Gaps are in pp per year. Census C30 private \"Data center\" construction (monthly, millions of dollars at a seasonally adjusted annual rate, `privsatime.xlsx`) is a memo only: December of 2015, 2019, 2022 and 2025 are in `detail.csv` with a blank kept as blank; it is not subtracted. Denominator: national accounts, no firm counts.\n")
    a("### P2: listed firms outside the AI complex accelerated capex\n")
    a("Panel: SEC frames `CY2016`, `CY2019`, `CY2022`, `CY2025` of `us-gaap` `%s` in USD. A firm is common if in each of the four frames its fact is positive, its fact's period ends in November, December or January, and the fact's accession number resolves to a 10-K or 10-K/A in the SEC submissions data (main file plus the older pages it lists). The 7 named CIKs (Amazon, Alphabet, Meta, Microsoft, Oracle, Nvidia, Tesla) are removed first; then SIC (from the submissions file, fetched %s) sorts firms: AI complex SICs 3559, 3570-3579, 3661, 3663, 3669, 3670-3679, 4812, 4813, 7370-7379 out; finance SIC 6000-6799 out (this includes REITs, SIC 6798); utilities SIC 4900-4991 reported as a separate stratum; firms with no SIC out. A firm is dropped from a window if PPE (`%s`) rose more than 25%% in any year of that window with `%s` above zero in that year. Firm growth = (capex at the end year over capex at the base year) to the power 1/3, minus 1. Statistic: the median of firm growth minus nominal GDP growth over the same years (Table 1.1.5 annual, calendar years: 2022 to 2025 and 2016 to 2019, 3 years each), treatment minus placebo, in pp per year; and the same difference for the capex-weighted mean of firm growth (weights = base-year capex). The aggregate growth of summed capex is also reported. SUPPORT if the median gap is at least +2 and the weighted gap is above 0; AGAINST if both are at most 0; otherwise INCONCLUSIVE.\n" % (CAPEX_TAG, ", ".join(P.sic_fetch_dates), PPE_TAG, ACQ_TAG))
    a("Denominators (firms): frame facts in CY2016, CY2019, CY2022, CY2025 = %s; candidates present in all four years with positive capex and a November, December or January period end (7 named CIKs out) = %d; dropped because a fact was not from a 10-K or 10-K/A = %d (accession not found in any submissions page = %d); common firms with 10-K facts = %d, of which AI complex SIC %d, finance (excluding REITs) %d, REITs %d, utilities %d, headline class %d. Headline windows: treatment %d firms (dropped by the acquisition rule %d), placebo %d firms (dropped %d). Share of 2025 ex-AI capex covered by the headline panel: %s (treatment set) and %s (placebo set), where ex-AI capex is the sum of positive CY2025 frame facts of all firms outside the AI complex with a SIC, any form and any year-end; against the headline-class capex alone (also excluding finance, utilities and REITs) the shares are %s and %s.\n" % (
        ", ".join("%d: %d" % (y, n) for y, n in sorted(P.counts["frame_facts_by_year"].items())), P.counts["candidates"], P.counts["dropped_form_not_10k"] + P.counts["dropped_form_unresolved"], P.counts["dropped_form_unresolved"], P.counts["common_firms_10k"],
        P.counts["by_class"].get("AI", 0), P.counts["by_class"].get("FIN", 0), P.counts["by_class"].get("REIT", 0), P.counts["by_class"].get("UTIL", 0), P.counts["by_class"].get("HEAD", 0),
        p2["T"]["n"], P.window_stats[("HEAD", "T")]["dropped_acquisition_rule"], p2["P"]["n"], P.window_stats[("HEAD", "P")]["dropped_acquisition_rule"],
        f4(cv["P2_T"]["share_of_ex_ai_all"]), f4(cv["P2_P"]["share_of_ex_ai_all"]), f4(cv["P2_T"]["share_of_headline_class"]), f4(cv["P2_P"]["share_of_headline_class"])))
    ut, rt = R["p2_strata"]["UTIL"], R["p2_strata"]["REIT"]
    a("Separate strata, not in the headline (same computation, utilities with %d and %d firms in the treatment and placebo windows, REITs with %d and %d): utilities median gap %s and weighted gap %s; REITs median gap %s and weighted gap %s (pp per year).\n" % (
        len(P.window[("UTIL", "T")]), len(P.window[("UTIL", "P")]), len(P.window[("REIT", "T")]), len(P.window[("REIT", "P")]),
        f4(ut["median_gap_pp"]) if ut else "n/a", f4(ut["weighted_gap_pp"]) if ut else "n/a", f4(rt["median_gap_pp"]) if rt else "n/a", f4(rt["weighted_gap_pp"]) if rt else "n/a"))
    a("### P3: corporate liquidity was drawn down\n")
    a("Source: Fed Z.1 `FRB_Z1_csv.zip` (the release of 11 Sep 2026; its last quarter in these series is %s). Series, with the description in the file (each confirmed against the spec's meaning before scoring; a mismatch stops the build): %s. Sum of the four, millions of dollars, not seasonally adjusted, Q4 values; divided by Table 1.1.5 nominal GDP (Q4, seasonally adjusted annual rate), in percent. Statistic = (ratio at 2025Q4 minus ratio at 2022Q4) minus (ratio at 2019Q4 minus ratio at 2015Q4), in pp; the changes are not annualised. SUPPORT if the difference is at most -0.5 pp and the nominal dollar stock fell from 2022Q4 to 2025Q4; AGAINST if the difference is at least 0 or the stock rose by more than nominal GDP over the same quarters; otherwise INCONCLUSIVE. Denominator: one sector, four series, four Q4 dates.\n" % (
        p3["last_quarter"], "; ".join("%s = \"%s\"" % (sid, d["desc"]) for sid, d in p3["series"].items())))
    a("Required statements for this readout: the sector is domestic nonfinancial corporate business; it includes equity REITs (moved into the sector on 7 Dec 2023, as the attack note quotes the Fed's table description; not re-read here) and the nonfinancial AI filers; it excludes financial holding companies and the foreign subsidiaries of US corporations; time and savings deposits within the core liquid assets series are a remainder. The SOI benchmark year is not named in the Z.1 file or in the series page for FL103020000 (the page says only that after the most recent SOI year the benchmark ratio is fixed); it is recorded as not determined, and the spec's ruling is that this does not make P3 unscorable. The quarterly movement in these stocks rests on the Census QFR, which this build does not read.\n")
    a("### P4: cash-rich firms led the ex-AI capex change\n")
    a("Panel: the P2 headline window sets. Cash = `%s` (else `%s`, never both) over `%s`, from instant frames `CY2015Q4I` (placebo) and `CY2021Q4I` (treatment), each fact a 10-K or 10-K/A fact. Within each window the firms are sorted by cash over assets inside their 2-digit SIC; the i-th of n firms (i from 0) goes to tercile min(2, floor(3i/n)), bottom = 0, top = 2; a 2-digit group of fewer than 3 firms cannot be split and is dropped. Tercile growth = the mean of firm annualised capex growth weighted by base-year capex, pooled across 2-digit groups. Statistic = (top minus bottom) in the treatment window minus (top minus bottom) in the placebo window, pp per year. SUPPORT if at least +3 and the top tercile's own treatment growth net of annualised nominal GDP growth is above 0; AGAINST if at most 0; otherwise INCONCLUSIVE.\n" % (CASH_TAG, CASH_ALT_TAG, ASSETS_TAG))
    a("Denominators (firms): treatment window %d firms with cash and assets of %d in the P2 set (top %d, middle %d, bottom %d; 2-digit groups used %d; %d firms in groups below 3); placebo window %d of %d (top %d, middle %d, bottom %d; groups %d; %d dropped). Share of 2025 ex-AI capex covered: %s (treatment) and %s (placebo).\n" % (
        len(P.p4_firms["T"]), len(P.window[("HEAD", "T")]), p4["T"]["top"]["n"], p4["T"]["middle"]["n"], p4["T"]["bottom"]["n"], p4["T"]["n_sic2_groups_used"], p4["T"]["dropped_small_sic2"],
        len(P.p4_firms["P"]), len(P.window[("HEAD", "P")]), p4["P"]["top"]["n"], p4["P"]["middle"]["n"], p4["P"]["bottom"]["n"], p4["P"]["n_sic2_groups_used"], p4["P"]["dropped_small_sic2"],
        f4(cv["P4_T"]["share_of_ex_ai_all"]), f4(cv["P4_P"]["share_of_ex_ai_all"])))
    a("### P5: manufacturing, mining and non-utility transport capex growth exceeded trade and services (not an irreversibility test)\n")
    a("Panel: the P2 headline window sets. High = SIC 1000-1499, 2000-3999, 4000-4899; low = SIC 5000-5999, 7000-8999 (SIC 7370-7379 is already out as AI complex). Trimmed high removes SIC 1311, 1381, 1382, 1389, 2911, 3711 and 3721 (3559, 4812 and 4813 are already out); the removed firms are reported separately. Statistic = (median growth of high minus median growth of low) in the treatment window minus the same in the placebo window, pp per year, for the trimmed and the untrimmed high group. SUPPORT if the trimmed gap is at least +2 (if only the untrimmed gap clears +2: INCONCLUSIVE); AGAINST if the trimmed gap is at most 0; otherwise INCONCLUSIVE.\n")
    a("Denominators (firms): treatment high %d (trimmed %d, removed %d), low %d; placebo high %d (trimmed %d, removed %d), low %d. Firms with SIC 1500-1799, 4900 and above 5999 (other than the low bin) or 9000 and above are in neither bin.\n" % (
        p5["T"]["n_high"], p5["T"]["n_high_trimmed"], p5["T"]["n_removed"], p5["T"]["n_low"], p5["P"]["n_high"], p5["P"]["n_high_trimmed"], p5["P"]["n_removed"], p5["P"]["n_low"]))
    a("### P6: sector AI use against sector capex change (descriptive, no label)\n")
    for ln in p6_readme(R):
        a(ln)
    a("### P7: not scored\n")
    a("The inputs are not available: P7 needs `GoodwillImpairmentLoss` facts for CY2026, CY2027 and CY2028 10-Ks (the last are filed from about February 2029) and the acquisition-spend and goodwill facts for CY2024 and CY2025 and for the baseline cohorts 2012 to 2015. The spec dates its first scoring to about April 2029. No P7 number is computed or implied.\n")
    a("## Implementation choices (where the spec is silent or cannot be followed as written)\n")
    for i, s in enumerate([
        "Raw cache. `data/vintages/cv1/` is not covered by `.gitignore`, and the build task could not edit it, so raw downloads sit in `%s/raw/`, a folder `.gitignore` already ignores whole. Move them if `data/vintages/cv1/` is later added to `.gitignore`." % CACHE_REL,
        "P1 communication equipment: see the three variants above; variant A sets the label. The label is the same under all three variants: %s." % ("yes" if len({v[k]["label"] for k in v}) == 1 else "NO, it is variant-dependent (A %s, B %s, C %s)" % (v["A"]["label"], v["B"]["label"], v["C"]["label"])),
        "P2 capex tag: `%s` (the tag the attack's amendment names). Facts must be positive. Fiscal year-end is taken from the month of each fact's period end (November, December or January), not from the current `fiscalYearEnd` of the submissions file." % CAPEX_TAG,
        "Form join: a frame fact is matched to its form through its accession number in the submissions data: the `recent` block and every older page listed in the file's `files` array that could hold the accession number (chosen by the filing year inside the number; %d older pages were fetched). Facts from any other form are dropped and counted." % len([r for r in read_manifest(cache_dir()) if r["key"].startswith("older:")]),
        "The same 10-K filter is applied to the PPE, acquisition, cash and assets facts that P2 and P4 use. A missing or non-10-K fact never triggers the acquisition drop; a year with an acquisition above zero and no usable PPE pair is counted as untestable (treatment headline: %d firm-years, placebo: %d)." % (P.window_stats[("HEAD", "T")]["untestable"], P.window_stats[("HEAD", "P")]["untestable"]),
        "The acquisition rule is applied year by year inside each window (PPE of year y against year y-1 for each year after the base year), using frames for every year in the two windows. The base year of a window is not itself tested.",
        "SIC is the current SIC in the submissions file at the fetch date, not the SIC on the filing (the spec accepts this limit). A firm with no SIC is out of the headline and out of the coverage denominators.",
        "Capex-weighted growth is the mean of firm annualised growth weighted by base-year capex (the same weighting P4 uses); the growth of summed capex is reported beside it as the aggregate.",
        "GDP growth for P2 and P4 uses annual nominal GDP (Table 1.1.5 annual, calendar years) over 2022 to 2025 and 2016 to 2019. P1 and P3 use Q4 quarterly values; their placebo spans 4 years, the panel placebo 3.",
        "Ties and groups in P4: firms sorted by cash ratio then CIK; groups below 3 firms dropped; terciles formed separately in each window, so the same firm can sit in different terciles in the two windows.",
        "P5: when the untrimmed gap is at least +2 and the trimmed gap is below +2 the label is INCONCLUSIVE even if the trimmed gap is at most 0 (the INCONCLUSIVE clause is applied before AGAINST).",
        "Thresholds. The spec's inequalities are inclusive where it writes at least or at most, so a value exactly on such a threshold takes the SUPPORT or AGAINST label; where it writes above or more than (P2 weighted gap, P4 own growth, P3 stock against GDP), a value exactly on the threshold fails the condition and the label is INCONCLUSIVE unless the other side holds. Comparisons use values rounded to 9 decimals. If both SUPPORT and AGAINST conditions held the label would be INCONCLUSIVE; none did.",
        "Coverage. Share of 2025 ex-AI capex = sum of the panel's CY2025 capex over the sum of all positive CY2025 `%s` facts of firms that are neither in the AI complex nor without a SIC (any form, any year-end; SIC for all %d CIKs was fetched). Two denominators are given: all ex-AI classes, and the headline class alone." % (CAPEX_TAG, sum(P.denom_count.values()) - P.denom_count.get("NOSIC", 0)),
        "P3 uses Q4 values not seasonally adjusted for the Z.1 stocks and the seasonally adjusted annual rate for GDP.",
        "P6 cycles. A cycle is in the window if its `Smpdt` label begins 2024 or 2025 and its `Col End` (Collection and Reference Dates sheet) is before 17 Nov 2025; the workbook has no column for 202521 to 202523, so no cycle after 202520 is used. The mean is of the unsuppressed percentages; a cell that is not a number followed by a percent sign (\"S\") is skipped. The `XX` row (multi-unit companies, defined in the Data Dictionary as operating in several sectors or states) has no SIC and is ignored. BTOS has no sector 92 (public administration).",
        "P6 SIC to sector. Each concordance row is one vote for the BTOS sector of its NAICS 2002 first two digits (31/32/33 to 31, 44/45 to 44, 48/49 to 48; other two-digit codes stay as they are, including codes BTOS does not publish). A SIC whose rows all reach one sector maps to it; a SIC split across sectors maps to the sector with strictly the most rows; a tie drops the firm. Rows, not distinct NAICS codes, are counted. A firm whose SIC is not in the concordance is dropped and counted. Concordance rows with a non-numeric SIC or a NAICS that is not six digits (Aux, Null Set, blank) are skipped and counted.",
        "P6 sector filter. \"At least 20 common firms\" is read as at least 20 firms in each of the treatment and placebo P2 headline window sets (the window sets differ because the acquisition rule is applied by window, so P2 has no single common panel after that rule; the common-firm requirement across CY2016, 2019, 2022 and 2025 is already inside both sets). The sector statistic is `p2_stats(...)[\"median_gap_pp\"]` on the sector's firms, unchanged. Utilities, REITs, finance and the AI complex are outside the P2 headline sets and so outside P6.",
        "P6 Spearman and leave-one-out. Spearman is the existing average-rank function; the leave-one-sector-out range is the minimum and maximum over the kept sectors of the Spearman with that sector removed (None if fewer than 3 sectors remain). No p-value and no label are given.",
    ], 1):
        a("%d. %s" % (i, s))
    a("")
    a("## Sources and vintages\n")
    a("| source | url | fetched (UTC) | bytes | sha256 |")
    a("|---|---|---|---|---|")
    for r in vint:
        if r[0] in ("bea1", "bea5", "z1", "c30", "fed-series-page", "census-btos", "census-p6-input", "sec-submissions", "sec-submissions-older-pages"):
            a("| %s | %s | %s | %s | %s |" % (r[0], r[2], r[3], r[5], (r[6] or "-")[:16]))
    a("")
    a("The 24 SEC frames (tags %s; periods CY2016, CY2019, CY2022, CY2025, and the PPE, acquisition, cash and assets periods named in the code) are listed one per row in `vintages.csv` with their fetch time, size and sha256. BEA files: %s (Section 5) and %s (Section 1). Z.1 release: Fed Board file dated 11 Sep 2026. C30: file dated 2 Nov 2026, latest month Sep-26. SIC history is not reconstructed. All requests to data.sec.gov carried the declared tool name only and ran at most 4 a second; no request went to www.sec.gov or FRED. The first four rows' fetch times are the files' modification times, because they were downloaded by a first probe before the fetch log existed.\n" % (", ".join(sorted({CAPEX_TAG, PPE_TAG, ACQ_TAG, CASH_TAG, CASH_ALT_TAG, ASSETS_TAG})), R["p1"]["pub5"].replace("Data published ", "published "), R["p1"]["pub1"].replace("Data published ", "published ")))
    a("## Reproduce\n")
    a("```\npython3 bin/cv1_confidence_velocity.py selftest\npython3 bin/cv1_confidence_velocity.py fetch --what bea|z1|census|frames|submissions|submissions-all [--max-requests N] [--budget-seconds S]\npython3 bin/cv1_confidence_velocity.py build\n```\n")
    a("`fetch` is resumable (files already in the cache are skipped); `build` is offline and reads only the cache. Checking the work: `bash bin/check.sh --all` runs gate M31 over this folder.\n")
    # kept verbatim from the committed README, where it had been appended by hand (14 Nov 2026); without this a rebuild would drop it
    for ln in ['## Independent recompute of P3 (14 Nov 2026)', '', 'Gemini 4 Hydrogen (Medium) recomputed CV1-P3 blind from the raw Z.1 CSV package and the BEA Section 1 workbook. It was given the method, not our result. Its results agree with `scores.csv`:', '- the four Z.1 series descriptions;', '- the stock at 2022Q4 ($3,572.386bn) and 2025Q4 ($4,936.617bn);', '- the GDP quarters (2025Q4: $31,462.5bn SAAR);', '- both window changes (+2.3478 and +1.5608 pp) and the difference (+0.7870 pp).', '', 'It also answered two questions about quarters the files do not yet contain (2026Q3 in Z.1, 2026Q4 in NIPA) with "not in the files". The supervisor confirmed both against the files.']:
        a(ln)
    a("")
    return "\n".join(A)


# ------------------------------------------------------------------------------------------------------------------------
# build
# ------------------------------------------------------------------------------------------------------------------------
def no_leak(name, text):
    for bad in ("@", "/Users/", "/private/", "~/"):
        if bad in text:
            raise Refused("%s would contain %r" % (name, bad))


def table_text(source_line, header, rows):
    t = "# source: %s\n" % source_line + csv_line(header) + "".join(csv_line(r) for r in rows)
    return t


def run_build(root=None, out=None, scorer=None):
    root = root or ROOT
    out = out or out_dir(root)
    cache = cache_dir(root)
    reg_path, sha = write_registered(out, root)                                   # first: before any statistic exists
    reg_sha = sha256_of(open(reg_path, "rb").read())
    print("registered.csv written (spec sha256 %s; file sha256 %s)" % (sha, reg_sha), flush=True)
    R = (scorer or run_scores)(cache)
    scores, detail = make_rows(R)
    vint = vintage_rows(cache)
    src = "bin/cv1_confidence_velocity.py build; scores computed after registered.csv (sha256 %s) was written; spec %s sha256 %s" % (reg_sha, SPEC_FILE, sha)
    files = {
        "scores.csv": table_text(src, SCORES_HEADER, scores),
        "detail.csv": table_text(src, DETAIL_HEADER, detail),
        "vintages.csv": table_text("fetch manifest of the raw cache (%s); raw files are not committed" % CACHE_REL, VINTAGES_HEADER, vint),
        "README.md": readme_text(R, scores, vint, sha),
    }
    for name, text in files.items():
        no_leak(name, text)
    for name, text in files.items():
        write_text(os.path.join(out, name), text)
    for r in scores:
        print("%s  %s  %s=%s %s" % (r[0], r[1], r[2], r[3], r[4]))
    return R, scores


# ------------------------------------------------------------------------------------------------------------------------
# selftest: synthetic data only, no network
# ------------------------------------------------------------------------------------------------------------------------
class Checks(object):
    def __init__(self):
        self.items = []

    def ok(self, name, cond, detail=""):
        self.items.append((name, bool(cond), "" if cond else detail))

    def eq(self, name, got, want):
        self.ok(name, got == want, "got %r, want %r" % (got, want))

    def near(self, name, got, want, tol=1e-9):
        self.ok(name, got is not None and abs(got - want) <= tol, "got %r, want %r" % (got, want))

    def raises(self, name, exc, fn):
        try:
            fn()
        except exc:
            self.ok(name, True)
        except Exception as e:
            self.ok(name, False, "raised %s: %s" % (type(e).__name__, e))
        else:
            self.ok(name, False, "did not raise")


class FakeResp(object):
    def __init__(self, status, body=b"{}", headers=None):
        self.status, self._b, self.headers = status, body, headers or {}

    def read(self):
        return self._b


class FakeOpener(object):
    def __init__(self, plan):
        self.plan = list(plan)
        self.calls = []

    def open(self, req, timeout=None):
        self.calls.append((req.full_url, dict((k.lower(), v) for k, v in req.header_items())))
        st = self.plan.pop(0) if self.plan else 200
        if st == 200:
            return FakeResp(200)
        raise urllib.error.HTTPError(req.full_url, st, "x", {}, io.BytesIO(b""))


def synth_firm(cik, sic, base, end_t, end_p=None, ratio_t=None, ratio_p=None):
    """cap: base-year capex 100*base in 2016 and 2022; end-year values end_p (2019) and end_t (2025)."""
    f = {"cik": cik, "sic": sic, "cap": {2016: float(base), 2019: float(end_p if end_p is not None else base), 2022: float(base), 2025: float(end_t)}, "ratio": {}}
    if ratio_t is not None:
        f["ratio"]["T"] = ratio_t
    if ratio_p is not None:
        f["ratio"]["P"] = ratio_p
    return f


def selftest():
    import tempfile
    ck = Checks()
    # growth, median, weighted mean
    ck.near("growth: 100 -> 133.1 over 3 years is 10 percent a year", ann_growth(100, 133.1, 3), 0.10, 1e-12)
    ck.near("growth: flat is 0", ann_growth(50, 50, 4), 0.0)
    ck.raises("growth: zero base refused", ValueError, lambda: ann_growth(0, 5, 3))
    ck.near("median of an odd list", median([5, 1, 3]), 3.0)
    ck.near("median of an even list", median([4, 1, 3, 2]), 2.5)
    ck.near("capex-weighted mean", wmean([0.10, 0.00], [100.0, 300.0]), 0.025)
    ck.near("a gap between medians: (0.10-0.02) - (0.03-0.02) in pp is 7", pp((0.10 - 0.02) - (0.03 - 0.02)), 7.0, 1e-9)
    # terciles within SIC2
    items = [("a%d" % i, 10, float(i)) for i in range(1, 7)] + [("b1", 20, 0.5), ("b2", 20, 0.6)] + [("c%d" % i, 30, float(i)) for i in range(1, 5)]
    tm, dropped = terciles_within_sic2(items)
    ck.eq("terciles: 6 firms in one SIC2 split 2/2/2", [tm["a%d" % i] for i in range(1, 7)], [0, 0, 1, 1, 2, 2])
    ck.eq("terciles: 4 firms split 2/1/1", [tm["c%d" % i] for i in range(1, 5)], [0, 0, 1, 2])
    ck.eq("terciles: a group of 2 is dropped and counted", sorted(dropped), ["b1", "b2"])
    tm2, _d = terciles_within_sic2([("x", 10, 9.0), ("y", 10, 1.0), ("z", 10, 5.0), ("p", 20, 100.0), ("q", 20, 1.0), ("r", 20, 50.0)])
    ck.eq("terciles: formed inside each SIC2, not across", (tm2["y"], tm2["z"], tm2["x"], tm2["q"], tm2["r"], tm2["p"]), (0, 1, 2, 0, 1, 2))
    # Spearman
    ck.near("spearman: identical order is +1", spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
    ck.near("spearman: reversed order is -1", spearman([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)
    ck.near("spearman with a tie (ranks of y 1, 2, 3.5, 5, 3.5; hand answer 8/sqrt(95))", spearman([1, 2, 3, 4, 5], [5, 6, 7, 8, 7]), 8.0 / math.sqrt(95.0), 1e-12)
    ck.eq("spearman: no variation gives None", spearman([1, 2, 3], [4, 4, 4]), None)
    ck.eq("spearman: fewer than 3 gives None", spearman([1, 2], [1, 2]), None)
    # P1 arithmetic
    ck.near("P1 share: (100 - 10 - 20) / 1000 = 7 percent", p1_residual_share(100.0, [10.0, 20.0], 1000.0), 7.0)
    ck.near("P1 gap: (13-10)/3 - (11-10)/4 = 0.75", p1_gap(10.0, 13.0, 10.0, 11.0), 0.75)
    # P3 arithmetic
    stock = {"2015Q4": 100.0, "2019Q4": 120.0, "2022Q4": 200.0, "2025Q4": 190.0}
    gdp = {"2015Q4": 1000.0, "2019Q4": 1000.0, "2022Q4": 1000.0, "2025Q4": 1200.0}
    s3 = p3_stats(stock, gdp)
    ck.near("P3: ratios 10, 12, 20, 15.8333; difference (15.8333-20) - (12-10)", s3["diff_pp"], (190 / 1200 * 100 - 20.0) - 2.0, 1e-9)
    ck.ok("P3: stock fell and its growth is below GDP growth", s3["stock_fell"] and s3["stock_growth"] < s3["gdp_growth"], str(s3))
    ck.eq("P3 label on that example", label_p3(s3["diff_pp"], s3["stock_fell"], s3["stock_growth"], s3["gdp_growth"]), "SUPPORT")
    # labels: P1
    ck.eq("P1: both exactly +0.15 -> SUPPORT (the spec's at-least)", label_p1(0.15, 0.15), "SUPPORT")
    ck.eq("P1: one just under -> INCONCLUSIVE", label_p1(0.1499, 0.9), "INCONCLUSIVE")
    ck.eq("P1: both exactly 0 -> AGAINST (the spec's at-most)", label_p1(0.0, 0.0), "AGAINST")
    ck.eq("P1: one at 0 and one above -> INCONCLUSIVE", label_p1(0.0, 0.01), "INCONCLUSIVE")
    ck.eq("P1: nominal rises, real falls -> INCONCLUSIVE", label_p1(0.4, -0.2), "INCONCLUSIVE")
    ck.eq("P1: float noise at the threshold does not flip it", label_p1(0.15 + 1e-13, 0.15 - 1e-13), "SUPPORT")
    # P2: asymmetric rules
    ck.eq("P2: median exactly 2 and weighted exactly 0 -> INCONCLUSIVE (weighted must be above 0)", label_p2(2.0, 0.0), "INCONCLUSIVE")
    ck.eq("P2: median 2 and weighted just above 0 -> SUPPORT", label_p2(2.0, 0.0001), "SUPPORT")
    ck.eq("P2: both exactly 0 -> AGAINST", label_p2(0.0, 0.0), "AGAINST")
    ck.eq("P2: median 3, weighted negative -> INCONCLUSIVE", label_p2(3.0, -1.0), "INCONCLUSIVE")
    ck.eq("P2: median negative, weighted positive -> INCONCLUSIVE", label_p2(-1.0, 0.5), "INCONCLUSIVE")
    # P3: asymmetric rules
    ck.eq("P3: difference exactly -0.5 and the stock fell -> SUPPORT", label_p3(-0.5, True, -0.1, 0.1), "SUPPORT")
    ck.eq("P3: difference -1 but the stock rose -> INCONCLUSIVE", label_p3(-1.0, False, 0.05, 0.10), "INCONCLUSIVE")
    ck.eq("P3: difference exactly 0 -> AGAINST even though the stock fell", label_p3(0.0, True, -0.1, 0.1), "AGAINST")
    ck.eq("P3: stock rose by more than GDP -> AGAINST even at -1", label_p3(-1.0, False, 0.20, 0.10), "AGAINST")
    ck.eq("P3: stock growth exactly equal to GDP growth is not 'more than' -> INCONCLUSIVE", label_p3(-0.2, False, 0.10, 0.10), "INCONCLUSIVE")
    ck.eq("P3: -0.4999 and the stock fell -> INCONCLUSIVE", label_p3(-0.4999, True, -0.1, 0.1), "INCONCLUSIVE")
    # P4, P5
    ck.eq("P4: exactly +3 with positive own growth -> SUPPORT", label_p4(3.0, 0.1), "SUPPORT")
    ck.eq("P4: +3 but own growth exactly 0 -> INCONCLUSIVE (the gate is strict)", label_p4(3.0, 0.0), "INCONCLUSIVE")
    ck.eq("P4: exactly 0 -> AGAINST whatever the gate", label_p4(0.0, 5.0), "AGAINST")
    ck.eq("P4: 5 but own growth negative -> INCONCLUSIVE", label_p4(5.0, -2.0), "INCONCLUSIVE")
    ck.eq("P5: trimmed exactly 2 -> SUPPORT", label_p5(2.0, 2.0), "SUPPORT")
    ck.eq("P5: only the untrimmed gap clears 2 -> INCONCLUSIVE", label_p5(1.0, 2.5), "INCONCLUSIVE")
    ck.eq("P5: untrimmed 2.5 and trimmed 0 -> INCONCLUSIVE (the untrimmed clause comes first)", label_p5(0.0, 2.5), "INCONCLUSIVE")
    ck.eq("P5: trimmed 1.9, untrimmed 1.9 -> INCONCLUSIVE", label_p5(1.9, 1.9), "INCONCLUSIVE")
    ck.eq("P5: trimmed exactly 0 and untrimmed 1 -> AGAINST", label_p5(0.0, 1.0), "AGAINST")
    ck.eq("at_threshold flags a value on a threshold", at_threshold(0.15, (0.15, 0.0)), [0.15])
    # P2 statistics on a synthetic panel with known answers
    base, end_hi = 100.0, 133.1                                           # 10 percent a year over 3 years
    firms_t = [synth_firm(i, 3000, base, end_hi) for i in range(5)]       # all 10 percent
    firms_p = [synth_firm(i, 3000, base, base) for i in range(5)]         # all 0 percent
    g = {"T": 0.02, "P": 0.03}
    s2 = p2_stats(firms_t, firms_p, g)
    ck.near("P2: median gap = (10-2) - (0-3) = 11 pp", s2["median_gap_pp"], 11.0, 1e-7)
    ck.near("P2: weighted gap equals it here", s2["weighted_gap_pp"], 11.0, 1e-7)
    ck.near("P2: aggregate gap equals it here", s2["aggregate_gap_pp"], 11.0, 1e-7)
    skew_t = [synth_firm(1, 3000, 1000.0, 1000.0), synth_firm(2, 3000, 10.0, 13.31), synth_firm(3, 3000, 10.0, 13.31)]
    s2b = window_summary(skew_t, "T", g)
    ck.near("P2: the median ignores size (10 percent a year)", s2b["median"], 0.10, 1e-9)
    ck.ok("P2: weighted mean is below the median here", s2b["weighted"] < 0.01, str(s2b))
    # P4 on a synthetic panel: six firms, one SIC2 group, tercile structure known
    ft, fp = [], []
    for i in range(6):
        top = i >= 4
        ft.append(synth_firm(100 + i, 2000 + i, 100.0, 133.1 if top else 100.0, ratio_t=0.1 * (i + 1)))
        fp.append(synth_firm(100 + i, 2000 + i, 100.0, 100.0, ratio_p=0.1 * (i + 1)))
    s4 = p4_stats(ft, fp, {"T": 0.02, "P": 0.03})
    ck.near("P4: top 10 percent minus bottom 0, placebo 0: statistic 10 pp", s4["stat_pp"], 10.0, 1e-7)
    ck.near("P4: top tercile net of GDP is 10 - 2 = 8 pp", s4["top_net_of_gdp_pp"], 8.0, 1e-7)
    ck.eq("P4: tercile sizes 2/2/2", (s4["T"]["bottom"]["n"], s4["T"]["middle"]["n"], s4["T"]["top"]["n"]), (2, 2, 2))
    ck.eq("P4: label on the synthetic panel", label_p4(s4["stat_pp"], s4["top_net_of_gdp_pp"]), "SUPPORT")
    ck.raises("P4: an empty tercile stops the scoring", Refused, lambda: p4_stats(ft[:2], fp[:2], {"T": 0.0, "P": 0.0}))
    # P5 on a synthetic panel: high firms grow 10 percent (trimmed ones 30), low firms 0
    ht = [synth_firm(i, 2800 + i, 100.0, 133.1) for i in range(3)] + [synth_firm(10 + i, 2911, 100.0, 219.7) for i in range(3)]
    lt_ = [synth_firm(20 + i, 5400 + i, 100.0, 100.0) for i in range(3)]
    hp = [synth_firm(i, 2800 + i, 100.0, 100.0) for i in range(3)] + [synth_firm(10 + i, 2911, 100.0, 100.0) for i in range(3)]
    lp = [synth_firm(20 + i, 5400 + i, 100.0, 100.0) for i in range(3)]
    s5 = p5_stats(ht + lt_, hp + lp)
    ck.near("P5: trimmed gap = 10 pp", s5["trimmed_gap_pp"], 10.0, 1e-6)
    ck.ok("P5: untrimmed median pulled up by the removed SICs (3 of 6 at 30 percent): above the trimmed gap", s5["untrimmed_gap_pp"] > s5["trimmed_gap_pp"], str(s5))
    ck.eq("P5: removed firms counted", (s5["T"]["n_removed"], s5["T"]["n_high_trimmed"], s5["T"]["n_high"], s5["T"]["n_low"]), (3, 3, 6, 3))
    # classification
    ck.eq("classify: AI SIC", classify(5, 3576), "AI")
    ck.eq("classify: AI SIC 7372", classify(5, 7372), "AI")
    ck.eq("classify: named AI CIK whatever the SIC", classify(1018724, 5961), "AI")
    ck.eq("classify: semiconductor equipment 3559 is AI", classify(5, 3559), "AI")
    ck.eq("classify: REIT before finance", classify(5, 6798), "REIT")
    ck.eq("classify: bank is finance", classify(5, 6021), "FIN")
    ck.eq("classify: electric utility is its own stratum", classify(5, 4911), "UTIL")
    ck.eq("classify: refinery is headline", classify(5, 2911), "HEAD")
    ck.eq("classify: no SIC", classify(5, None), "NOSIC")
    # synthetic workbook and zip readers
    with tempfile.TemporaryDirectory() as td:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "T-Q"
        ws.append(["Table x"])
        ws.append(["Data published October 29, 2026"])
        for _ in range(5):
            ws.append([None])
        ws.append(["Line", None, None, "2022Q4", "2025Q4"])
        ws.append([1, "    Gross domestic product", "A191RC", 26774117, 31462523])
        ws.append([2, "Nonresidential", "A008RC", "---", 5])
        ws.append(["Note.", "x"])
        xp = os.path.join(td, "t.xlsx")
        wb.save(xp)
        pub, data, labels = read_bea_sheet(xp, "T-Q")
        ck.eq("BEA reader: data, a non-number skipped, labels trimmed", (data["A191RC"], data["A008RC"], labels["A191RC"], pub), ({"2022Q4": 26774117.0, "2025Q4": 31462523.0}, {"2025Q4": 5.0}, "Gross domestic product", "Data published October 29, 2026"))
        hdr = "series_name,short_description,long_description,currency,frequency,series_instrument,series_prefix,series_sector,series_type,unit,unit_mult,date,value\n"
        lines = [hdr]
        for sid, desc in (("FL104001105", "Nonfinancial corporate business; liquid assets (core measure) (FSIs)"), ("FL103061103", "Nonfinancial corporate business; Treasury securities; asset"),
                          ("FL103061703", "Nonfinancial corporate business; agency- and GSE-backed securities; asset"), ("FL103069100", "Nonfinancial corporate business; commercial paper; asset")):
            lines.append("Z1/Z1/%s.Q,%s,%s,c,Quarterly,i,p,s,t,Currency,Millions,2022-12-31,100\n" % (sid, desc, desc))
            lines.append("Z1/Z1/%s.Q,%s,%s,c,Quarterly,i,p,s,t,Currency,Millions,2025-12-31,150\n" % (sid, desc, desc))
        lines.append("Z1/Z1/FL999999999.Q,other,other,c,Quarterly,i,p,s,t,Currency,Millions,2025-12-31,1\n")
        zp = os.path.join(td, "z.zip")
        with zipfile.ZipFile(zp, "w") as z:
            z.writestr("Z1.csv", "".join(lines))
        z1 = read_z1_series(zp, list(Z1_SERIES))
        ck.eq("Z.1 reader: only the four series, quarters keyed", sorted(z1), sorted(Z1_SERIES))
        ck.eq("Z.1 reader: value at 2025Q4", z1["FL104001105"]["values"]["2025Q4"], 150.0)
        check_z1_descriptions(z1)
        ck.ok("Z.1 descriptions match the spec's meaning", True)
        z1["FL103061103"]["desc"] = "Nonfinancial corporate business; municipal securities; asset"
        ck.raises("Z.1 description mismatch stops the build", Refused, lambda: check_z1_descriptions(z1))
        del z1["FL103069100"]
        ck.raises("Z.1 missing series stops the build", Refused, lambda: check_z1_descriptions(z1))
    # registration: hash pin, parse, order
    with tempfile.TemporaryDirectory() as td:
        spec_dir = os.path.join(td, "_research")
        os.makedirs(spec_dir)
        real = spec_text()
        with open(os.path.join(td, *SPEC_FILE.split("/")), "wb") as fh:
            fh.write(real)
        rows = parse_spec_table(real.decode("utf-8"))
        ck.eq("the spec table parses to P1..P7", sorted(rows), ["CV1-P%d" % i for i in range(1, 8)])
        ck.ok("the pinned hash is the hash of the spec in the repository", sha256_of(real) == SPEC_SHA256, sha256_of(real))
        with open(os.path.join(td, *SPEC_FILE.split("/")), "wb") as fh:
            fh.write(real + b" ")
        called = []
        ck.raises("a changed spec file: the build refuses to score", Refused, lambda: run_build(root=td, out=os.path.join(td, "o1"), scorer=lambda c: called.append(1)))
        ck.ok("a changed spec file: the scorer never ran and registered.csv was not written", not called and not os.path.exists(os.path.join(td, "o1", "registered.csv")), str(called))
        with open(os.path.join(td, *SPEC_FILE.split("/")), "wb") as fh:
            fh.write(real)

        def boom(cache):
            ck.ok("registered.csv exists before the scorer starts", os.path.exists(os.path.join(td, "o2", "registered.csv")))
            raise RuntimeError("stop here")
        ck.raises("scorer runs after registered.csv is written", RuntimeError, lambda: run_build(root=td, out=os.path.join(td, "o2"), scorer=boom))
        t = open(os.path.join(td, "o2", "registered.csv"), encoding="utf-8").read()
        body = [l for l in t.splitlines() if not l.startswith("# source:")]
        ck.eq("registered.csv header and seven rows", (body[0], len(body) - 1), (",".join(REG_HEADER), 7))
        ck.ok("every registered row carries the spec hash, and the file has no at sign or local path", t.count(SPEC_SHA256) >= 8 and "@" not in t and "/Users/" not in t and "/private/" not in t)
        ck.ok("scores.csv was not written by the failed run", not os.path.exists(os.path.join(td, "o2", "scores.csv")))
    # fetcher: user agents, rate limit, STOP latch, host allowlist
    with tempfile.TemporaryDirectory() as td:
        clock = [0.0]
        slept = []

        def sleep(s):
            slept.append(s)
            clock[0] += s
        op = FakeOpener([200, 200, 200])
        f = Fetcher(td, opener=op, sleep=sleep, clock=lambda: clock[0])
        f.get("https://data.sec.gov/api/xbrl/frames/us-gaap/Assets/USD/CY2022Q4I.json", accept_gzip=True)
        f.get("https://data.sec.gov/submissions/CIK0000000001.json")
        f.get("https://apps.bea.gov/national/Release/XLS/Survey/Section1All_xls.xlsx")
        ck.eq("data.sec.gov gets the declared tool name only (name/version, no spaces, brackets or address)", (op.calls[0][1]["user-agent"], op.calls[0][1]["user-agent"] == SEC_TOOL, bool(re.match(r"^[A-Za-z]+/[0-9.]+$", SEC_TOOL))), (SEC_TOOL, True, True))
        ck.eq("another host gets the neutral string", op.calls[2][1]["user-agent"], UA)
        ck.ok("no at sign in either string", "@" not in SEC_TOOL and "@" not in UA)
        ck.ok("the second SEC request waited for the 0.25 s gap (at most 4 a second)", len(slept) >= 1 and abs(sum(slept) - SEC_MIN_GAP) < 1e-9, str(slept))
        ck.raises("www.sec.gov is refused", Refused, lambda: f.get("https://www.sec.gov/cgi-bin/browse-edgar"))
        ck.raises("a host off the allowlist is refused", Refused, lambda: f.get("https://fred.stlouisfed.org/series/X"))
        ck.raises("plain http is refused", Refused, lambda: f.get("http://data.sec.gov/submissions/CIK0000000001.json"))
        op2 = FakeOpener([403])
        f2 = Fetcher(td, opener=op2, sleep=sleep, clock=lambda: clock[0])
        ck.raises("a 403 raises Stop", Stop, lambda: f2.get("https://www.census.gov/hfp/btos/downloads/"))
        ck.ok("the STOP latch file exists", f2.stopped("www.census.gov"))
        n_before = len(op2.calls)
        ck.raises("after a 403 no further request to that host", Stop, lambda: f2.get("https://www.census.gov/construction/c30/xlsx/privsatime.xlsx"))
        ck.eq("the opener was not called again", len(op2.calls), n_before)
        ck.ok("another host is still allowed", f2.get("https://apps.bea.gov/x")[0] == 200)
        op3 = FakeOpener([429])
        f3 = Fetcher(os.path.join(td, "c3"), opener=op3, sleep=sleep, clock=lambda: clock[0])
        ck.raises("a 429 raises Stop and is not retried", Stop, lambda: f3.get("https://data.sec.gov/submissions/CIK0000000002.json"))
        ck.eq("one request only for the 429", len(op3.calls), 1)
    # frames list is what the build reads
    fl = frame_list()
    ck.eq("frame list: 4 capex, 8 PPE, 6 acquisition, 6 cash and assets", len(fl), 24)
    ck.ok("every frame period is CY####, or CY####Q4I for instants", all(re.match(r"^CY\d{4}(Q4I)?$", per) for _t, per in fl))
    # P6: BTOS means, SIC to sector map, sector filter, input refusal
    ck.eq("parse_pct: percent, suppressed, blank", (parse_pct("12.5%"), parse_pct("S"), parse_pct(None)), (12.5, None, None))
    cyc = btos_cycles([(202426, "12/16/2024", "12/29/2024"), (202501, "12/30/2024", "01/12/2025"), (202523, "11/03/2025", "11/16/2025"), (202524, "11/17/2025", "11/30/2025"), (202326, "12/18/2023", "12/31/2023")])
    hdr = ("Sector", "Question ID", "Question", "Answer ID", "Answer", "202524", "202501", "202426", "202326")
    rws = [(54, 7, "q", 1, "Yes", "9.0%", "10.0%", "S", "1.0%"), (54, 7, "q", 2, "No", "50.0%", "50.0%", "50.0%", "50.0%"), (54, 24, "q", 1, "Yes", "9.0%", "9.0%", "9.0%", "9.0%"),
           (55, 7, "q", 1, "Yes", "S", "S", "S", "S"), ("XX", 7, "q", 1, "Yes", "8.0%", "8.0%", "8.0%", "8.0%")]
    aim, miss, ucols = btos_ai_means(hdr, rws, cyc)
    ck.eq("BTOS means: only Question 7 Yes, only 2024/2025 cycles ended before 17 Nov 2025, S skipped, 2023 and 202524 excluded", (aim["54"]["mean"], aim["54"]["used"], aim["54"]["suppressed"], ucols), (10.0, ["202501"], ["202426"], ["202426", "202501"]))
    ck.eq("BTOS means: a sector with every cell suppressed has no mean; XX is ignored", (aim["55"]["mean"], sorted(aim)), (None, ["54", "55"]))
    ck.eq("BTOS means: an in-window cycle missing from the sheet is reported, not filled", miss, ["202523"])
    smp = sic_sector_map([(100, "111110"), (100, "112111"), (200, "311111"), (200, "322222"), (200, "334444"), (300, "441110"), (300, "541110"), (400, "541110"), (400, "541120"), (400, "441110"), (400, "451110"), (500, "481111"), (500, "491111")])
    ck.eq("SIC map: every row in one sector", smp[100], ("11", "single"))
    ck.eq("SIC map: 31/32/33 group to 31 so a SIC across them is not split", smp[200], ("31", "single"))
    ck.eq("SIC map: 44/45 and 48/49 group", (smp[500], sic_sector_map([(1, "441110"), (1, "451110")])[1]), (("48", "single"), ("44", "single")))
    ck.eq("SIC map: split SIC with one row each is a tie, no sector", smp[300], (None, "tie"))
    ck.eq("SIC map: split SIC with rows 2 to 2 is a tie; 3 to 1 would go to the majority", (smp[400], sic_sector_map([(9, "541110"), (9, "541120"), (9, "541130"), (9, "441110")])[9]), ((None, "tie"), ("54", "majority")))
    ck.ok("SIC map: an unmapped SIC is absent", 999 not in smp)
    ai6 = {"54": {"mean": 20.0, "used": [], "suppressed": []}, "44": {"mean": 5.0, "used": [], "suppressed": []}, "52": {"mean": 15.0, "used": [], "suppressed": []}, "55": {"mean": None, "used": [], "suppressed": []}}
    sm6 = {5400: ("54", "single"), 4400: ("44", "single"), 5200: ("52", "majority"), 5500: ("55", "single"), 7000: (None, "tie"), 7100: ("54", "majority")}
    ggt = {"T": 0.02, "P": 0.02}

    def fleet(sic, n, k0, endt):
        return [synth_firm(k0 + i, sic, 100.0, endt) for i in range(n)]
    ft = fleet(5400, 20, 0, 133.1) + fleet(4400, 20, 100, 100.0) + fleet(5200, 19, 200, 110.0) + fleet(5500, 25, 300, 100.0) + fleet(7000, 3, 400, 100.0) + fleet(6000, 2, 500, 100.0) + fleet(7100, 2, 600, 100.0)
    fp = fleet(5400, 20, 0, 100.0) + fleet(4400, 20, 100, 100.0) + fleet(5200, 20, 200, 100.0) + fleet(5500, 25, 300, 100.0) + fleet(7000, 3, 400, 100.0) + fleet(6000, 2, 500, 100.0) + fleet(7100, 2, 600, 100.0)
    r = p6_stats(ft, fp, ggt, ai6, sm6)
    ck.eq("sector filter: 20 and 20 kept; 19 in one window dropped; no AI mean dropped; tied SIC and unmapped SIC dropped", ([x["sector"] for x in r["rows"]], r["small"]), (["44", "54"], [("52", 19, 20)]))
    ck.eq("sector filter: drop counts (treatment): not in concordance 2, tie 3, sector without AI mean 25", (r["drop_T"]["not_in_concordance"], r["drop_T"]["tie"], r["drop_T"]["sector_without_ai_mean"]), (2, 3, 25))
    ck.near("sector statistic is the P2 median gap: sector 54 grows 10 percent a year in T, 0 in P, GDP 2 percent in both -> 10 pp", [x["stat"] for x in r["rows"] if x["sector"] == "54"][0], 10.0, 1e-9)
    ck.eq("sector filter: fewer than 3 sectors gives no Spearman", r["rho"], None)
    rd = p6_stats(ft, fp, ggt, ai6, sm6, drop_split=True)
    ck.eq("split-SIC variant drops the majority-mapped firms too (treatment: 19 on SIC 5200 and 2 on SIC 7100; the 3 tied firms stay counted as ties)", (rd["drop_T"]["split_dropped"], rd["drop_T"]["tie"]), (21, 3))
    r4 = p6_stats(ft + fleet(5200, 1, 700, 110.0) + fleet(5100, 20, 800, 120.0), fp + fleet(5100, 20, 800, 100.0), ggt, dict(ai6, **{"51": {"mean": 30.0, "used": [], "suppressed": []}}), dict(list(sm6.items()) + [(5100, ("51", "single"))]))
    ck.eq("Spearman and leave-one-out run once 4 sectors are kept (AI means 5, 15, 20, 30; statistics 0, 0, 10, 10 pp... ranks hand-checked in the next line)", (r4["n"], len(r4["loo"])), (4, 4))
    ck.ok("leave-one-out minimum and maximum are among the four leave-out values", r4["loo_min"] == min(v for _s, v in r4["loo"] if v is not None) and r4["loo_max"] == max(v for _s, v in r4["loo"] if v is not None))
    pm3, pm2 = prefix_sector_map([(2860, "325110"), (2869, "325199"), (2865, "325110"), (2810, "325120"), (2800, "999999")], 3), prefix_sector_map([(2860, "325110"), (2900, "324110"), (2950, "324121"), (2960, "541110"), (2961, "551111")], 2)
    ck.eq("prefix map: 3-digit prefix 286 votes across its SICs (majority 31 -> single sector)", pm3["286"], ("31", "single"))
    ck.eq("prefix map: 2-digit prefix 29 has rows for 31, 31, 54, 55: majority 31", pm2["29"], ("31", "majority"))
    ck.eq("prefix map: a 1-1 split across prefix rows is a tie", prefix_sector_map([(3001, "541110"), (3002, "441110")], 3)["300"], (None, "tie"))
    fb = [(3, {"540": ("54", "single"), "510": (None, "tie")}), (2, {"44": ("44", "single")})]
    ft2 = fleet(5401, 20, 0, 133.1) + fleet(4410, 20, 100, 100.0) + fleet(5101, 3, 200, 100.0) + fleet(9999, 4, 300, 100.0)
    fp2 = fleet(5401, 20, 0, 100.0) + fleet(4410, 20, 100, 100.0) + fleet(5101, 3, 200, 100.0) + fleet(9999, 4, 300, 100.0)
    rv = p6_stats(ft2, fp2, ggt, ai6, {}, prefix_maps=fb)
    ck.eq("prefix variant: 3-digit prefix, then 2-digit prefix, tie dropped, no-rows dropped; sector filter re-applied", ([x["sector"] for x in rv["rows"]], rv["drop_T"]["prefix_mapped"], rv["drop_T"]["tie"], rv["drop_T"]["not_in_concordance"]), (["44", "54"], 43, 3, 4))
    ck.eq("headline rule unchanged by the variant code: without prefix maps the same firms are dropped as unmapped", p6_stats(ft2, fp2, ggt, ai6, {})["rows"], [])
    with tempfile.TemporaryDirectory() as td:
        ck.ok("P6 inputs missing: refused with the file named", "missing" in compute_p6(td, {"T": [], "P": []}, ggt).get("refused", ""))
        os.makedirs(os.path.join(td, "raw", "census"))
        for rel in (BTOS_REL, CONC_REL):
            with open(os.path.join(td, *rel.split("/")), "wb") as fh:
                fh.write(b"not the pinned file")
        ck.ok("P6 inputs with a different hash: refused, nothing read", "pinned" in compute_p6(td, {"T": [], "P": []}, ggt).get("refused", ""))
    # leak guard
    ck.raises("an at sign in an output is refused", Refused, lambda: no_leak("x", "a@b"))
    ck.raises("a local path in an output is refused", Refused, lambda: no_leak("x", "see /Users/x"))
    bad = ck.items
    failed = [(n, d) for n, c, d in bad if not c]
    for n, c, d in bad:
        print(("PASS  " if c else "FAIL  ") + n + ("" if c else "   <- " + d))
    print("selftest: %d checks, %d failed" % (len(bad), len(failed)))
    return 0 if not failed else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="CV1 confidence-velocity scorer (spec version 2)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    fp = sub.add_parser("fetch")
    fp.add_argument("--what", required=True, choices=("bea", "z1", "census", "frames", "submissions", "submissions-all", "all"))
    fp.add_argument("--max-requests", type=int, default=500)
    fp.add_argument("--budget-seconds", type=float, default=140.0)
    bp = sub.add_parser("build")
    bp.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "fetch":
        return cmd_fetch(a.what, a.max_requests, a.budget_seconds)
    try:
        run_build(out=a.out)
    except Refused as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
