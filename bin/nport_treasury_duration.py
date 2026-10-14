#!/usr/bin/env python3
"""How much of the Treasury duration the public took did US registered funds take? Stdlib only, no network I/O.

  python3 bin/nport_treasury_duration.py [--zip-dir ~/nport] [--r1-cache data/vintages/r1_treasury]
          [--r2-cache data/vintages/r2_treasury] [--z1-dir data/vintages/z1_fund_tsy_20260911]
          [--etf-dir data/vintages/z1_etf1_2026Q2] [--anchors data/nport/tsy_anchors.csv] [--out data/nport]

Spec: _research/2026-10-14-NPORT-Treasury-Duration-Spec.md (section 10 overrides sections 1-9). This is the build of
E-021 item 7, serving R2's open line "which buyers took the duration is not measured". It prices every cash Treasury
line in the SEC's bulk N-PORT data sets on R2's own basis (10-year equivalents at the fixed end-2023 curve, imported from
bin/r2_duration_supply.py, not copied) and sets the funds' change against R2's change in the public's holdings. It measures
a HOLDER SHARE of cash Treasuries. It does not test whether the funds' buying moved yields (C-122), P - S is a residual
that is not "the unregistered holders" until measured (C-098), and these funds already sit inside the Z.1 funds row (C-124).

Inputs (NOT redistributed; none is fetched by this script, it makes no network call of any kind):
  * the SEC bulk N-PORT zips, one per calendar quarter of filing, named YYYYqQ_nport.zip. Landing page:
    https://www.sec.gov/dera/data/form-n-port-data-sets ; file URL pattern
    https://www.sec.gov/files/dera/data/form-n-port-data-sets/YYYYqQ_nport.zip . They are discovered by glob in --zip-dir, read
    as streams and never extracted or copied. Download them with the supervisor's SEC_UA (CLAUDE.md), nothing else does.
    The three pins below are bootstrap only; every zip's sha256 is recorded in tsy_file_stats.csv and compared with the
    previously committed copy of that file on the next run (check C1).
        2024q1 7f391a05a71cec3fde5ce382e8ca8af9b11606ae85c465f99d98846e2d695254
        2026q2 077cc836a978a593b29012219395fbe9c303d5e930f5be3b5f4353c3b02296fc
        2026q3 2f5ee059234d2e28f16d0451d9fcb405aab3dad5d92cded74c8ea9ffc4b66c38
  * R2's caches (gitignored), written by bin/r2_duration_supply.py: --r1-cache holds the Treasury daily nominal and real
    par curves, --r2-cache holds MSPD Table 3 for six record dates and the NY Fed SOMA files for four. A missing file is
    named in the refusal with the command that recreates it (python3 bin/r2_duration_supply.py; after a new year or a
    new R2 date delete the 2026 curve caches first so they are re-fetched).
  * data/r2_rates/duration_supply.csv (committed), the Z.1 tables written by bin/nport_fetch_z1.py (committed, public
    domain), data/vintages/z1_etf1_2026Q2/ (committed), and data/nport/tsy_anchors.csv (committed).

Outputs, all aggregates (no holding row, CUSIP, HOLDING_ID or accession number is written), under --out; on any hard FAIL
they go to --out/_FAILED/ instead and the committed files are left untouched (exit status 2). No file carries a wall-clock
time, so a re-run is byte-identical. The gate is tsy_checks.csv, not the exit code.
  tsy_windows.csv      one row per window x vintage: Treasury value, par, 10-year equivalents, Z.1 levels
  tsy_buckets.csv      window x kind x remaining-maturity bucket (base vintage), beside R2's public figure at R2's dates
  tsy_change.csv       variant x period: dS, dP, r, s0, excess over pro rata, label
  tsy_verdict.csv      the two-arm verdict of section 1 of the spec
  tsy_dv01_check.csv   fund-level |reported DV01| / computed DV01 (a magnitude check, never summed)
  tsy_top_funds.csv    the largest funds and registrants (serves OPEN 1)
  tsy_checks.csv       every check with its observed value; hard checks set the exit status
  tsy_file_stats.csv   file denominators, provenance and exclusion counts

THE MATCHING RULES (spec sections 3 and 4, "listed rather than hidden"; a matching rule is a hypothesis, C-059):
 1. Unit = a holding line (a row of FUND_REPORTED_HOLDING). Keep it when ISSUER_TYPE is UST (or USGA with a 912 CUSIP),
    the CUSIP starts "912", ASSET_CAT is DBT, STIV, SN or OTHER, and CURRENCY_CODE is USD. Repo (RA), derivatives (DIR),
    ABS, non-912 UST lines and blank values are excluded and counted with their $ by reason. ISIN recovery is deferred.
 2. Fund = SERIES_ID, or the registrant CIK when SERIES_ID is blank. Report month = (year, month) of REPORT_DATE. For each
    (fund, report month) across all zips keep the filing with the largest (not-a-stub, FILING_DATE, is NPORT-P/A, accession);
    a stub is an NPORT-P/A with zero holding lines and never replaces a non-empty filing. Survivors with the same CIK,
    REPORT_DATE, NET_ASSETS and Treasury line count under different fund keys are one filing seen twice: the latest is kept.
 3. A window is a quarter-end month. Each fund contributes its survivor for that month, else the month before, else the
    month after. Base vintage = every zip, a filing counts only if FILING_DATE <= REPORT_DATE + 62 days. Matched vintage
    (variant M1) = zips up to the window's home zip (the following calendar quarter's), no lag cut.
 4. Kind: the MSPD class of the CUSIP (R2's own); else prefix 912795/6/7 = bill; else 912803/912820/912821/912833/912834 or
    STRIP in the name = strip; else COUPON_TYPE Floating/Variable = FRN; else a TIPS-like name = TIPS; else coupon note.
 5. Coupon and maturity: MSPD's (R2's own) when the CUSIP is in MSPD; else DEBT_SECURITY (rate x100 when 0 < rate < 0.1);
    else the modal maturity of that CUSIP in the window; else the line is unpriced and its $ is reported.
 6. Par = BALANCE (negated for a Short line). TIPS: when BALANCE is original face (CURRENCY_VALUE sits nearer the value of
    original-face par than of adjusted par, judged against R2's model price; ratio > 1.05) par = BALANCE x the MSPD index
    ratio at the report date. Par is never back-solved from a modelled price.
 7. 10-year equivalent = par x price/100 x modified duration / d10, line by line, with R2's own functions: tenyeq_fixed on
    the fixed end-2023 curve (the quantity-only measure R2 compares), tenyeq_own on the report date's curve. Bucket figures
    are sums of line values, never a bucket factor times dollars.
 8. DV01 is a cross-check on MAGNITUDE only (the sign differs by filer): the median of |reported| / computed over funds
    with Treasuries >= 90% of NAV and a USD row must lie in 0.85-1.15. It is never summed across funds.
Corrections cited: C-059 (the matching rule is a hypothesis), C-098 (P - S is a residual), C-122 (name the weighting),
C-124 (the Z.1 funds row already contains these funds).
"""
import argparse, collections, csv, datetime as dt, glob, hashlib, importlib.util, io, math, os, re, sys, time, unittest, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

HOLDING, DEBT, IRR = "FUND_REPORTED_HOLDING.tsv", "DEBT_SECURITY.tsv", "INTEREST_RATE_RISK.tsv"
ZIP_RE = re.compile(r"^(\d{4})q([1-4])_nport\.zip$", re.I)
LAG_DAYS = 62                      # N2: a filing counts in the base vintage only if FILING_DATE <= REPORT_DATE + 62 days
MAX_LIST_BYTES = 10_000_000        # N9: never list() a member larger than this
KEEP_CATS = ("DBT", "STIV", "SN", "OTHER")
BILL_PREFIXES = ("912795", "912796", "912797")
STRIP_PREFIXES = ("912803", "912820", "912821", "912833", "912834")
TIPS_RX = re.compile(r"INFL|TIPS|\bTII\b|INDEX|PROTECT|LINKED")
TIPS_MIN_RATIO = 1.05              # N4: below this the two readings of BALANCE cannot be told apart
FIRST_ORDER_BN, ITEM_ROUND_BN, BYSTANDER_BN = 460.0, 500.0, 100.0   # N1: dollars, written 14 Oct before any measurement
ALT_CURVE_DATE = "2026-06-30"      # M8: the other endpoint's curve
R2_DATES_USED = ("2023-12-31", "2024-12-31", "2025-12-31", "2026-06-30")
MSPD_DATES = ("2023-12-31", "2024-12-31", "2025-12-31", "2026-06-30", "2026-07-31", "2026-08-31")
SOMA_ASOF = ("2023-12-27", "2024-12-31", "2025-12-31", "2026-06-24")
KINDS = ("bills", "coupons", "tips", "frn", "strips", "unpriced")
BUCKETS = ("0-1", "1-2", "2-3", "3-5", "5-7", "7-10", "10-20", "20+")
BUCKET_EDGES = ((1, "0-1"), (2, "1-2"), (3, "2-3"), (5, "3-5"), (7, "5-7"), (10, "7-10"), (20, "10-20"))
NO_ANCHOR = "N/A (no anchor)"
OUT_FILES = ("tsy_windows", "tsy_buckets", "tsy_change", "tsy_verdict", "tsy_dv01_check", "tsy_top_funds",
             "tsy_checks", "tsy_file_stats")
REFUSE_HEADERS = ("CUSIP", "HOLDING_ID", "ACCESSION_NUMBER")
R2_CMD = "python3 bin/r2_duration_supply.py"


def load_by_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_census = load_by_path("census_nport_bulk", os.path.join(HERE, "census_nport_bulk.py"))
pdate = _census.pdate              # DD-MON-YYYY -> date, the census parser


def flt(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


def flt_or_none(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


class Fsum:
    """Order-independent exact running sum (Shewchuk's partials, the algorithm inside math.fsum): the total is the
    correctly rounded sum of the terms whatever order they arrive in, so a re-run is byte-identical (N12)."""
    __slots__ = ("p",)

    def __init__(self):
        self.p = []

    def add(self, x):
        p, i = self.p, 0
        for y in p:
            if abs(x) < abs(y):
                x, y = y, x
            hi = x + y
            lo = y - (hi - x)
            if lo:
                p[i] = lo
                i += 1
            x = hi
        p[i:] = [x]

    def value(self):
        return math.fsum(self.p)


# ======================================================================================================== zips, tables
def discover_zips(zip_dir):
    """N8: zips are found by glob and the windows derived from them. Returns [(year, quarter, path)] sorted."""
    found = []
    for p in glob.glob(os.path.join(os.path.expanduser(zip_dir), "*_nport.zip")):
        m = ZIP_RE.match(os.path.basename(p))
        if m:
            found.append((int(m.group(1)), int(m.group(2)), p))
    found.sort()
    if not found:
        raise SystemExit(f"no YYYYqQ_nport.zip found in {zip_dir}; refusing")
    for (y0, q0, _), (y1, q1, _) in zip(found, found[1:]):
        if y1 * 4 + q1 != y0 * 4 + q0 + 1:
            raise SystemExit(f"the zips skip from {y0}q{q0} to {y1}q{q1}; refusing to build windows over a gap")
    return found


class Window:
    """The window of a zip (filing quarter) is the quarter-end month before it: 2024q1 -> 2023-12 (label 2023Q4)."""
    def __init__(self, idx, y, q):
        self.idx = idx
        self.zip_tag = f"{y}Q{q}"
        self.zip_name = f"{y}q{q}"
        wy, wm = (y - 1, 12) if q == 1 else (y, 3 * (q - 1))
        self.y, self.m = wy, wm
        self.ymi = wy * 12 + wm - 1
        self.label = f"{wy}Q{wm // 3}"
        nxt = dt.date(wy + (wm == 12), wm % 12 + 1, 1)
        self.qend = nxt - dt.timedelta(days=1)
        self.z1_key = f"{wy}:Q{wm // 3}"
        self.home_zipi = idx          # the window's home zip is the zip of the following calendar quarter
        self.months = [f"{(self.ymi + d) // 12}-{(self.ymi + d) % 12 + 1:02d}" for d in (-1, 0, 1)]


def make_windows(zips):
    return [Window(i, y, q) for i, (y, q, _) in enumerate(zips)]


def text_stream(z, member):
    return io.TextIOWrapper(z.open(member), encoding="utf-8", errors="replace", newline="")


def read_columns(z, member, cols):
    """Stream only the named columns of a tab-separated member as tuples; refuse on a column-count mismatch."""
    with z.open(member) as raw:
        f = io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="")
        hdr = f.readline().rstrip("\r\n").split("\t")
        ix = [hdr.index(c) for c in cols]
        n = len(hdr)
        for line in f:
            p = line.rstrip("\r\n").split("\t")
            if len(p) != n:
                raise SystemExit(f"{member}: {len(p)} columns, header has {n}; refusing to guess")
            yield tuple(p[i] for i in ix)


def table_rows(z, member, cols):
    """A small table as a list of column tuples (N9): refuses a member over 10 MB, which must be streamed instead."""
    size = z.getinfo(member).file_size
    if size > MAX_LIST_BYTES:
        raise SystemExit(f"{member} is {size:,} bytes; it must be streamed, not loaded")
    return list(read_columns(z, member, cols))


class Filing:
    __slots__ = ("acc", "zipi", "sub_type", "fdate", "rdate", "ymi", "fund", "cik", "net_assets", "series_name",
                 "registrant_name", "total_lines", "tsy_lines", "tsy_value", "dir_lines")

    def __init__(self, acc, zipi, sub_type, fdate, rdate, fund, cik, net_assets, series_name, registrant_name):
        self.acc, self.zipi, self.sub_type, self.fdate, self.rdate = acc, zipi, sub_type, fdate, rdate
        self.ymi = rdate.year * 12 + rdate.month - 1
        self.fund, self.cik, self.net_assets = fund, cik, net_assets
        self.series_name, self.registrant_name = series_name, registrant_name
        self.total_lines = self.tsy_lines = self.dir_lines = 0
        self.tsy_value = 0.0

    @property
    def ym(self):
        return (self.rdate.year, self.rdate.month)

    @property
    def is_amendment(self):
        return self.sub_type == "NPORT-P/A"


def load_zip_filings(z, zipi):
    """SUBMISSION + FUND_REPORTED_INFO + REGISTRANT, only the columns needed, one Filing per accession."""
    sub = {acc: (pdate(fd), st, pdate(rd)) for acc, fd, st, rd in
           table_rows(z, "SUBMISSION.tsv", ["ACCESSION_NUMBER", "FILING_DATE", "SUB_TYPE", "REPORT_DATE"])}
    info = {acc: (sid.strip(), sname.strip(), flt(nav)) for acc, sid, sname, nav in
            table_rows(z, "FUND_REPORTED_INFO.tsv", ["ACCESSION_NUMBER", "SERIES_ID", "SERIES_NAME", "NET_ASSETS"])}
    reg = {acc: (cik.strip(), rname.strip()) for acc, cik, rname in
           table_rows(z, "REGISTRANT.tsv", ["ACCESSION_NUMBER", "CIK", "REGISTRANT_NAME"])}
    out = []
    for acc in sorted(sub):
        fd, st, rd = sub[acc]
        sid, sname, nav = info.get(acc, ("", "", 0.0))
        cik, rname = reg.get(acc, ("", ""))
        fund = ("S", sid) if sid else ("C", cik or acc)
        out.append(Filing(acc, zipi, st, fd, rd, fund, cik, nav, sname, rname))
    return out


# ======================================================================================================== survivors
def survivor_key(f):
    """The larger key wins. A stub (an NPORT-P/A with zero holding lines) ranks below every non-empty filing."""
    stub = f.is_amendment and f.total_lines == 0
    return (not stub, f.fdate, f.is_amendment, f.acc)


def pick_survivors(filings):
    """One filing per (fund, report month): the one with the largest survivor_key. Returns (chosen, info). The de-duplication
    that matters is the single line that keeps the last candidate of each group."""
    groups = collections.defaultdict(list)
    for f in filings:
        groups[(f.fund, f.ym)].append(f)
    chosen = []
    info = collections.Counter()
    for k in sorted(groups):
        cands = sorted(groups[k], key=survivor_key)
        win = cands[-1]; chosen.append(win)
        if len(cands) > 1:
            info["superseded_filings"] += len(cands) - 1
            if win.is_amendment and cands[-2].total_lines > 0 and win.total_lines * 2 < cands[-2].total_lines:
                info["partial_amendments"] += 1
            info["stubs_ignored"] += sum(1 for c in cands[:-1] if c.is_amendment and c.total_lines == 0)
    return chosen, info


def check_unique_survivors(selection):
    """C2, first assertion. `selection` is any iterable of (fund, report_month, accession) triples (or Filing objects);
    PASS when no (fund, report month) is selected twice. It covers the de-duplicated list of survivors (the output of
    pick_survivors, and the same list after drop_content_duplicates) BEFORE window assignment, and nothing after it: it does
    not see assign_windows, the accession-to-window map or the sums of pass B. check_summed_once covers those."""
    seen = collections.Counter()
    for item in selection:
        if isinstance(item, Filing):
            seen[(item.fund, item.ym)] += 1
        else:
            seen[(item[0], item[1])] += 1
    return "FAIL" if any(n > 1 for n in seen.values()) else "PASS"


def check_summed_once(summed, tsy_lines):
    """C2, second assertion, on the accessions ACTUALLY SUMMED (after window assignment and pass B), not on the list that
    went in. `summed` is {(vintage, window idx): {accession: lines added}} as Ctx.add recorded it; `tsy_lines` is
    {accession: clean Treasury lines pass A counted for it}. PASS when, within each vintage, every summed accession went into
    exactly one window and had its lines added exactly as many times as pass A counted them, that is once each; FAIL
    otherwise (an accession in two windows, or summed twice into one)."""
    window_of = {}
    for (vint, wi), accs in summed.items():
        for acc, n in accs.items():
            if window_of.setdefault((vint, acc), wi) != wi or n != tsy_lines.get(acc):
                return "FAIL"
    return "PASS"


def drop_content_duplicates(chosen):
    """N3: survivors with the same CIK, REPORT_DATE, NET_ASSETS (> 0) and clean Treasury line count (> 0) under different
    fund keys are one filing seen twice. Keep the latest by survivor_key. Returns (kept, dropped)."""
    groups = collections.defaultdict(list)
    for f in chosen:
        if f.tsy_lines > 0 and f.net_assets > 0 and f.cik:
            groups[(f.cik, f.rdate, f.net_assets, f.tsy_lines)].append(f)
    drop = set()
    for g in groups.values():
        if len({f.fund for f in g}) > 1:
            g.sort(key=survivor_key)
            drop.update(f.acc for f in g[:-1])
    return [f for f in chosen if f.acc not in drop], [f for f in chosen if f.acc in drop]


def assign_windows(chosen, windows):
    """Each fund contributes its survivor for the window's quarter-end month, else the month before, else the month after.
    Returns {window idx: [(filing, 'm0'|'m-1'|'m+1')]}."""
    by_fund = collections.defaultdict(dict)
    for f in chosen:
        by_fund[f.fund][f.ymi] = f
    out = {w.idx: [] for w in windows}
    for fund in sorted(by_fund):
        months = by_fund[fund]
        for w in windows:
            for off, tag in ((0, "m0"), (-1, "m-1"), (1, "m+1")):
                f = months.get(w.ymi + off)
                if f is not None:
                    out[w.idx].append((f, tag))
                    break
    return out


def eligible_filings(all_filings, windows, vintage):
    """Filings of the right vintage whose report month falls in a window (m0-1, m0 or m0+1)."""
    win_of = {}
    for w in windows:
        for off in (-1, 0, 1):
            win_of[w.ymi + off] = w
    out = []
    for f in all_filings:
        w = win_of.get(f.ymi)
        if w is None:
            continue
        if vintage == "base":
            if (f.fdate - f.rdate).days > LAG_DAYS:
                continue
        elif f.zipi > w.home_zipi:
            continue
        out.append(f)
    return out


def select_vintage(all_filings, windows, vintage):
    """Full selection for one vintage. Returns a dict with the chosen filings before and after the content-duplicate step,
    the per-window assignment (after), the pre-step assignment, and counts."""
    elig = eligible_filings(all_filings, windows, vintage)
    chosen, info = pick_survivors(elig)
    kept, dropped = drop_content_duplicates(chosen)
    return {"eligible": len(elig), "chosen": chosen, "kept": kept, "dropped": dropped, "info": info,
            "assign": assign_windows(kept, windows), "assign_pre": assign_windows(chosen, windows),
            "c2": check_unique_survivors(chosen), "c2_after": check_unique_survivors(kept)}


# ======================================================================================================== holdings
def classify_line(p, ix):
    """p = the tab-split fields of one FUND_REPORTED_HOLDING row. Returns (status, reason): ('keep', None),
    ('excl', reason) or ('ignore', reason). The first reason that fits wins (spec section 3.2)."""
    it, cusip = p[ix["ISSUER_TYPE"]], p[ix["ISSUER_CUSIP"]]
    is912 = cusip.startswith("912")
    if it != "UST" and it != "USGA":
        # a 912 CUSIP on a line of another issuer type is only a Treasury look-alike in the cash categories (a US Foods
        # equity line carries 912008109); equity and the like are not counted as exclusions
        if is912 and p[ix["ASSET_CAT"]] in KEEP_CATS:
            return ("excl", "912_not_ust_type")
        return ("ignore", "other_issuer_type")
    if not is912:
        return ("excl", "non912_ust") if it == "UST" else ("ignore", "usga_non912")
    cat = p[ix["ASSET_CAT"]]
    if cat == "DIR":
        return ("excl", "derivative")
    if cat == "RA":
        return ("excl", "repo")
    if cat.startswith("ABS"):
        return ("excl", "abs")
    if cat not in KEEP_CATS:
        return ("excl", "other_asset_cat")
    if p[ix["CURRENCY_CODE"]] != "USD":
        return ("excl", "non_usd")
    if flt_or_none(p[ix["BALANCE"]]) is None or flt_or_none(p[ix["CURRENCY_VALUE"]]) is None:
        return ("excl", "blank_value_or_balance")
    return ("keep", None)


PREFILTERS = ("\tUST\t", "\tUSGA\t", "\t912")


def open_holdings(z):
    f = text_stream(z, HOLDING)
    hdr = f.readline().rstrip("\r\n").split("\t")
    return f, hdr, {h: i for i, h in enumerate(hdr)}


def scan_zip_holdings(z, filings):
    """PASS A over one zip's holdings: per filing, the number of holding lines (any), of DIR lines, and of clean Treasury
    lines with their $ value; plus the zip's exclusion and value-check statistics. Fills the Filing fields in place."""
    by_acc = {f.acc: f for f in filings}
    tot, dirs, tl, tv = {}, {}, {}, {}
    st = collections.Counter()
    fl = collections.defaultdict(float)
    nrows = 0
    f, hdr, ix = open_holdings(z)
    iV, iP, iU, iF, iA = ix["CURRENCY_VALUE"], ix["PERCENTAGE"], ix["UNIT"], ix["PAYOFF_PROFILE"], ix["ISSUER_CUSIP"]
    nav = {a: x.net_assets for a, x in by_acc.items()}
    with f:
        for line in f:
            nrows += 1
            k = line.find("\t")
            acc = line[:k]
            tot[acc] = tot.get(acc, 0) + 1
            if "\tDIR\t" in line:
                dirs[acc] = dirs.get(acc, 0) + 1
            if "\tUST\t" not in line and "\tUSGA\t" not in line and "\t912" not in line:
                continue
            p = line.rstrip("\r\n").split("\t")
            if len(p) != len(hdr):
                raise SystemExit(f"holding row {nrows}: {len(p)} columns, header has {len(hdr)}; refusing to guess")
            status, reason = classify_line(p, ix)
            if status == "ignore":
                if reason == "usga_non912":
                    st["usga_non912_lines_ignored"] += 1
                continue
            v = flt(p[iV])
            if status == "excl":
                st[f"excl_lines_{reason}"] += 1
                fl[f"excl_value_bn_{reason}"] += v / 1e9
                continue
            st["tsy_lines_kept"] += 1
            fl["tsy_value_kept_bn"] += v / 1e9
            tl[acc] = tl.get(acc, 0) + 1
            tv[acc] = tv.get(acc, 0.0) + v
            if p[iU] == "NS":
                st["unit_ns_lines"] += 1
            if p[iF] == "Short":
                st["short_lines"] += 1
            pct, n = p[iP], nav.get(acc, 0.0)
            if pct != "" and n:
                st["value_check_lines"] += 1
                if abs(flt(pct) / 100.0 * n - v) > 5 + 1e-4 * abs(v):
                    st["value_check_bad"] += 1
    unknown = 0
    for acc, n in tot.items():
        x = by_acc.get(acc)
        if x is None:
            unknown += n
            continue
        x.total_lines = n
        x.dir_lines = dirs.get(acc, 0)
        x.tsy_lines = tl.get(acc, 0)
        x.tsy_value = tv.get(acc, 0.0)
    st["holding_rows"] = nrows
    st["holding_rows_without_filing"] = unknown
    return st, dict(fl)


Line = collections.namedtuple("Line", "acc hid cusip par value title name short")


def stream_survivor_lines(z, wanted):
    """PASS B over one zip's holdings: the clean Treasury lines of the filings in `wanted` only. Returns a list of Line."""
    out = []
    f, hdr, ix = open_holdings(z)
    iA, iH, iC, iB, iV = ix["ACCESSION_NUMBER"], ix["HOLDING_ID"], ix["ISSUER_CUSIP"], ix["BALANCE"], ix["CURRENCY_VALUE"]
    iT, iN, iF = ix["ISSUER_TITLE"], ix["ISSUER_NAME"], ix["PAYOFF_PROFILE"]
    with f:
        for line in f:
            if "\tUST\t" not in line and "\tUSGA\t" not in line and "\t912" not in line:
                continue
            k = line.find("\t")
            if line[:k] not in wanted:
                continue
            p = line.rstrip("\r\n").split("\t")
            if len(p) != len(hdr):
                raise SystemExit(f"holding row: {len(p)} columns, header has {len(hdr)}; refusing to guess")
            if classify_line(p, ix)[0] != "keep":
                continue
            short = p[iF] == "Short"
            par = float(p[iB])
            if short and par > 0:
                par = -par
            out.append(Line(p[iA], p[iH], p[iC], par, float(p[iV]), p[iT], p[iN], short))
    return out


def read_debt(z, hids):
    """DEBT_SECURITY streamed against an id set: {HOLDING_ID: (maturity date or None, COUPON_TYPE, ANNUALIZED_RATE)}."""
    out = {}
    with z.open(DEBT) as raw:
        f = io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="")
        hdr = f.readline().rstrip("\r\n").split("\t")
        iM, iT, iR = hdr.index("MATURITY_DATE"), hdr.index("COUPON_TYPE"), hdr.index("ANNUALIZED_RATE")
        for line in f:
            k = line.find("\t")
            if line[:k] not in hids:
                continue
            p = line.rstrip("\r\n").split("\t")
            try:
                mat = pdate(p[iM]) if p[iM].strip() else None
            except (KeyError, ValueError):
                mat = None
            out[p[0]] = (mat, p[iT], p[iR])
    return out


def read_dv01(z, accs):
    """INTEREST_RATE_RISK USD rows: {accession: sum of the five key-rate DV01s, $ per bp, as filed}."""
    cols = ["ACCESSION_NUMBER", "CURRENCY_CODE", "INTRST_RATE_CHANGE_3MON_DV01", "INTRST_RATE_CHANGE_1YR_DV01",
            "INTRST_RATE_CHANGE_5YR_DV01", "INTRST_RATE_CHANGE_10YR_DV01", "INTRST_RATE_CHANGE_30YR_DV01"]
    out = {}
    for row in table_rows(z, IRR, cols):
        if row[0] in accs and row[1] == "USD" and row[0] not in out:
            vals = [flt_or_none(x) for x in row[2:]]
            if any(v is not None for v in vals):
                out[row[0]] = sum(v for v in vals if v is not None)
    return out


# ======================================================================================================== R2 as a library
def make_fetch_guard():
    """N7: replaces r2.fetch. Returns when the cached file exists; raises SystemExit, naming the file and the command that
    recreates it, when it does not. This script never touches the network."""
    def guard(url, path):
        if os.path.exists(path):
            return
        raise SystemExit(f"{os.path.basename(path)} is not in the cache {os.path.dirname(path)} and this script fetches "
                         f"nothing. Recreate it with: {R2_CMD}")
    return guard


def expected_cache_files():
    """N7: the explicit list (not a glob) of cache files this script reads, as (cache, name, hint)."""
    r1 = [("r1", f"daily_treasury_{k}yield_curve_{y}.csv", R2_CMD)
          for y in (2023, 2024, 2025, 2026) for k in ("", "real_")]
    mspd = [("r2", f"mspd_table3_{d}_p1.json", R2_CMD) for d in MSPD_DATES]
    soma = [("r2", "soma_asofdates_list.json", R2_CMD)] + [("r2", f"soma_tsy_{d}.json", R2_CMD) for d in SOMA_ASOF]
    return r1 + mspd + soma


def check_caches(r1_cache, r2_cache):
    missing = []
    for which, name, hint in expected_cache_files():
        d = r1_cache if which == "r1" else r2_cache
        if not os.path.exists(os.path.join(d, name)):
            missing.append(os.path.join(d, name))
    if missing:
        raise SystemExit("missing cache files:\n  " + "\n  ".join(missing) + f"\nrecreate them with: {R2_CMD}")


def load_r2(r1_cache, r2_cache):
    r2 = load_by_path("r2_duration_supply", os.path.join(HERE, "r2_duration_supply.py"))
    r2.fetch = make_fetch_guard()
    r2.R1RAW, r2.RAW = r1_cache, r2_cache
    return r2


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


class Mspd:
    __slots__ = ("kind", "maturity", "coupon")

    def __init__(self, kind, maturity, coupon):
        self.kind, self.maturity, self.coupon = kind, maturity, coupon


def tips_ratios_from_rows(rows, num):
    """MSPD Table 3 rows -> {TIPS CUSIP: index ratio} = sum(issued + inflation_adj - redeemed) / sum(issued - redeemed)
    over the CUSIP's tranche rows (`num` is r2.num, which reads Treasury's '*' as zero)."""
    iss, adj, red = collections.defaultdict(float), collections.defaultdict(float), collections.defaultdict(float)
    for r in rows:
        c = r["security_class2_desc"]
        if r["security_class1_desc"] == "Inflation-Protected Securities" and not c.startswith("Total"):
            iss[c] += num(r["issued_amt"]) or 0.0
            adj[c] += num(r["inflation_adj_amt"]) or 0.0
            red[c] += num(r["redeemed_amt"]) or 0.0
    return {c: (iss[c] + adj[c] - red[c]) / (iss[c] - red[c]) for c in sorted(iss) if iss[c] - red[c] > 0}


def build_mspd(r2):
    """CUSIP -> Mspd(kind, maturity date, coupon pct), first occurrence in record-date order; and the TIPS index ratio per
    CUSIP per record date (tips_ratios_from_rows)."""
    union, ratios = {}, collections.defaultdict(list)
    for d in MSPD_DATES:
        rows, _ = r2.load_mspd_table3(d)
        buckets, _, _, _ = r2.cusips_from_table3(rows, d)
        for kind, recs in buckets.items():
            for cusip, rec in recs.items():
                if cusip == "__MATURED__":
                    continue
                union.setdefault(cusip, Mspd(kind, dt.date.fromisoformat(rec["maturity"]), rec["coupon"]))
        for c, ratio in tips_ratios_from_rows(rows, r2.num).items():
            ratios[c].append((dt.date.fromisoformat(d), ratio))
    return union, {c: sorted(v) for c, v in ratios.items()}


def tips_ratio_at(series, d):
    """Linear interpolation in days between the bracketing MSPD record dates, flat outside them. None if no series."""
    if not series:
        return None
    if d <= series[0][0]:
        return series[0][1]
    if d >= series[-1][0]:
        return series[-1][1]
    for (d0, r0), (d1, r1) in zip(series, series[1:]):
        if d0 <= d <= d1:
            return r0 + (r1 - r0) * (d - d0).days / (d1 - d0).days
    return series[-1][1]


def tips_original_face(value, par, ratio, price_model):
    """N4: BALANCE is original face when CURRENCY_VALUE is nearer, in log terms, to the value original-face par would have
    (par x ratio x price/100) than to the value adjusted par would have (par x price/100). The model price chooses between
    the two readings only; par is never back-solved from it."""
    if ratio is None or ratio <= TIPS_MIN_RATIO or par <= 0 or value <= 0 or price_model <= 0:
        return False
    return math.log(value / (par * price_model / 100.0)) > 0.5 * math.log(ratio)


def decide_kind(cusip, title, name, ctype, mspd):
    """Spec section 3.3 kind precedence. Returns (kind, rule number)."""
    m = mspd.get(cusip)
    if m is not None:
        return m.kind, 1
    pre = cusip[:6]
    if pre in BILL_PREFIXES:
        return "bills", 2
    text = (title + " " + name).upper()
    if pre in STRIP_PREFIXES or "STRIP" in text:
        return "strips", 3
    if ctype.strip().lower() in ("floating", "variable"):
        return "frn", 4
    if TIPS_RX.search(text):
        return "tips", 5
    return "coupons", 6


def decide_coupon(cusip, mspd, rate_str):
    """Returns (coupon pct or None, source). MSPD's rate is R2's own; DEBT's ANNUALIZED_RATE x100 when 0 < rate < 0.1."""
    m = mspd.get(cusip)
    if m is not None and m.coupon is not None:
        return m.coupon, "mspd"
    r = flt_or_none(rate_str)
    if r is None:
        return None, "none"
    if 0 < r < 0.1:
        return r * 100.0, "rate_x100"
    return r, "rate"


def bucket_of(T):
    for edge, label in BUCKET_EDGES:
        if T < edge:
            return label
    return "20+"


class Pricer:
    """Per-line price and modified duration on three curve sets, with R2's own functions: the fixed curve (base), the
    alternative fixed curve (M8) and the report date's own curve. Cached on (kind, coupon, maturity, report date)."""
    def __init__(self, r2, nom_all, real_all, fixed, alt):
        self.r2, self.nom_all, self.real_all, self.fixed, self.alt = r2, nom_all, real_all, fixed, alt
        self.cache, self.own_cache = {}, {}

    def own(self, rdate):
        v = self.own_cache.get(rdate)
        if v is None:
            r2 = self.r2
            nrow = self.nom_all[r2.on_or_before(self.nom_all, rdate)]
            rrow = self.real_all[r2.on_or_before(self.real_all, rdate)]
            v = (r2.curve_points(nrow, r2.NOM_MATURITIES), r2.curve_points(rrow, r2.REAL_MATURITIES),
                 r2.par_mod_duration(nrow["10 Yr"], n=10))
            self.own_cache[rdate] = v
        return v

    def _pd(self, kind, coupon, T, nom, real):
        if kind == "strips":     # semiannual zeros
            return self.r2.coupon_price_duration(0.0, self.r2.interp_curve(nom, T), T)
        return self.r2.price_one(kind, coupon, T, nom, real)

    def price(self, kind, coupon, mat, rdate):
        key = (kind, coupon, mat, rdate)
        v = self.cache.get(key)
        if v is None:
            T = max((mat - rdate).days / 365.25, 0.0)
            on, orr, od = self.own(rdate)
            v = (T, self._pd(kind, coupon, T, self.fixed[0], self.fixed[1]),
                 self._pd(kind, coupon, T, self.alt[0], self.alt[1]), self._pd(kind, coupon, T, on, orr), od)
            self.cache[key] = v
        return v


SUM_FIELDS = ("value", "value_series", "value_noseries", "par", "tenyeq_fixed", "tenyeq_fixed_series", "tenyeq_alt",
              "tenyeq_own", "pardur_fixed", "dv01_own", "strips_tenyeq_fixed", "short_value", "unpriced_value",
              "value_rule123", "tips_orig_par_added", "tips_orig_tenyeq_fixed")


class Agg:
    """Accumulators for one (vintage, window): exact sums, so the order of lines never matters."""
    __slots__ = ("lines", "unpriced_lines", "tips_orig_lines", "funds", "s", "buckets")

    def __init__(self):
        self.lines = self.unpriced_lines = self.tips_orig_lines = 0
        self.funds = set()
        self.s = {k: Fsum() for k in SUM_FIELDS}
        self.buckets = {}

    def val(self, k):
        return self.s[k].value()


class FundAgg:
    __slots__ = ("f", "value", "tenyeq", "dv01_mn", "lines")

    def __init__(self, f):
        self.f, self.value, self.tenyeq, self.dv01_mn, self.lines = f, Fsum(), Fsum(), Fsum(), 0


class Ctx:
    """Everything the line-level pass needs and accumulates."""
    def __init__(self, r2, pricer, mspd, ratios, windows, filings_by_acc):
        self.r2, self.pricer, self.mspd, self.ratios = r2, pricer, mspd, ratios
        self.windows, self.fba = windows, filings_by_acc
        self.d10f, self.d10a = pricer.fixed[2], pricer.alt[2]
        self.agg = {(v, w.idx): Agg() for v in ("base", "matched") for w in windows}
        self.fund_agg = {}                       # (window idx, fund) -> FundAgg, base vintage only
        self.pending = []                        # lines waiting for the modal maturity of their CUSIP in the window
        self.mat_counter = collections.defaultdict(collections.Counter)    # (window idx, cusip) -> Counter of maturities
        self.zstats = collections.defaultdict(collections.Counter)         # tag -> counters (survivor lines)
        self.zfl = collections.defaultdict(lambda: collections.defaultdict(float))
        self.irr = {}                            # accession -> reported DV01 sum
        self.summed = collections.defaultdict(dict)    # (vintage, window idx) -> {accession: lines added}, for check_summed_once

    def add(self, tag, L, f, wi, mask, kind, rule, coupon, mat):
        """Price one resolved line and add it to every accumulator it belongs to. mat may be None (unpriced)."""
        par, value = L.par, L.value
        T = 0.0
        pr = None
        par_added = 0.0                       # par added by reading an original-face TIPS balance at its adjusted value
        if mat is not None:
            pr = self.pricer.price(kind, coupon, mat, f.rdate)
            T = pr[0]
            if kind == "tips":
                ratio = tips_ratio_at(self.ratios.get(L.cusip), f.rdate)
                if tips_original_face(value, par, ratio, pr[3][0]):
                    self.zstats[tag]["tips_original_face_lines"] += 1
                    par_added = par * (ratio - 1.0)
                    self.zfl[tag]["tips_original_face_par_added_bn"] += par_added / 1e9
                    par = par + par_added
        par_bn, value_bn = par / 1e9, value / 1e9
        series = f.fund[0] == "S"
        for vint, bit in (("base", 1), ("matched", 2)):
            if not mask & bit:
                continue
            a = self.agg[(vint, wi)]
            sm = self.summed[(vint, wi)]
            sm[f.acc] = sm.get(f.acc, 0) + 1
            a.lines += 1
            a.funds.add(f.fund)
            a.s["value"].add(value_bn)
            a.s["value_series" if series else "value_noseries"].add(value_bn)
            a.s["par"].add(par_bn)
            if L.short:
                a.s["short_value"].add(value_bn)
            if kind == "unpriced" or pr is None:
                a.unpriced_lines += 1
                a.s["unpriced_value"].add(value_bn)
                bk = ("unpriced", "n/a")
                te = 0.0
            else:
                (price_f, dur_f), (price_a, dur_a), (price_o, dur_o), d10o = pr[1], pr[2], pr[3], pr[4]
                te = par_bn * price_f / 100.0 * dur_f / self.d10f
                a.s["tenyeq_fixed"].add(te)
                if par_added:
                    a.tips_orig_lines += 1
                    a.s["tips_orig_par_added"].add(par_added / 1e9)
                    a.s["tips_orig_tenyeq_fixed"].add(par_added / 1e9 * price_f / 100.0 * dur_f / self.d10f)
                if series:
                    a.s["tenyeq_fixed_series"].add(te)
                a.s["tenyeq_alt"].add(par_bn * price_a / 100.0 * dur_a / self.d10a)
                a.s["tenyeq_own"].add(par_bn * price_o / 100.0 * dur_o / d10o)
                a.s["pardur_fixed"].add(par_bn * dur_f)
                dv = par_bn * price_o / 100.0 * dur_o * 0.1
                a.s["dv01_own"].add(dv)
                if kind == "strips":
                    a.s["strips_tenyeq_fixed"].add(te)
                if rule <= 3:
                    a.s["value_rule123"].add(value_bn)
                bk = (kind, bucket_of(T))
            if vint == "base":
                b = a.buckets.get(bk)
                if b is None:
                    b = a.buckets[bk] = [0, Fsum(), Fsum(), Fsum()]
                b[0] += 1
                b[1].add(value_bn)
                b[2].add(par_bn)
                b[3].add(te)
                fa = self.fund_agg.get((wi, f.fund))
                if fa is None:
                    fa = self.fund_agg[(wi, f.fund)] = FundAgg(f)
                fa.lines += 1
                fa.value.add(value_bn)
                fa.tenyeq.add(te)
                if pr is not None:
                    fa.dv01_mn.add(dv)

    def process_lines(self, tag, lines, debt, memb):
        """Resolve kind, coupon and maturity of each surviving line (spec 3.3) and price it, or park it as pending."""
        zs, zf = self.zstats[tag], self.zfl[tag]
        for L in lines:
            f = self.fba[L.acc]
            wi, mask = memb[L.acc]
            d = debt.get(L.hid)
            mat_debt, ctype, rate = d if d else (None, "", "")
            if d:
                zs["debt_rows_joined"] += 1
            kind, rule = decide_kind(L.cusip, L.title, L.name, ctype, self.mspd)
            zs[f"kind_rule_{rule}_lines"] += 1
            zf[f"kind_rule_{rule}_value_bn"] += L.value / 1e9
            coupon, src = decide_coupon(L.cusip, self.mspd, rate)
            if kind in ("coupons", "tips"):
                zs[f"coupon_src_{src}"] += 1
            if kind == "strips":
                coupon = 0.0
            m = self.mspd.get(L.cusip)
            mat = None
            if m is not None:
                mat = m.maturity
                if mat_debt is not None:
                    zs["maturity_both_lines"] += 1
                    if mat_debt == m.maturity:
                        zs["maturity_both_agree_lines"] += 1
            elif mat_debt is not None:
                mat = mat_debt
            if mat is not None and m is None:
                self.mat_counter[(wi, L.cusip)][mat] += 1
            if mat is None:
                self.pending.append((tag, L, f, wi, mask, kind, rule, coupon))
                continue
            self.add(tag, L, f, wi, mask, kind, rule, coupon, mat)

    def resolve_pending(self):
        """Lines with no MSPD or DEBT maturity take the modal maturity of the same CUSIP in the window, else are unpriced."""
        for tag, L, f, wi, mask, kind, rule, coupon in self.pending:
            ctr = self.mat_counter.get((wi, L.cusip))
            mat = None
            if ctr:
                mat = sorted(ctr.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
                self.zstats[tag]["maturity_modal_lines"] += 1
            else:
                self.zstats[tag]["maturity_unpriced_lines"] += 1
            self.add(tag, L, f, wi, mask, "unpriced" if mat is None else kind, rule, coupon, mat)
        self.pending = []


# ======================================================================================================== R2 rebuild (C10)
def r2_fixed_curve(r2, nom_all, real_all, iso):
    fd = dt.date.fromisoformat(iso)
    nd, rd = r2.on_or_before(nom_all, fd), r2.on_or_before(real_all, fd)
    nrow, rrow = nom_all[nd], real_all[rd]
    return (r2.curve_points(nrow, r2.NOM_MATURITIES), r2.curve_points(rrow, r2.REAL_MATURITIES),
            r2.par_mod_duration(nrow["10 Yr"], n=10), nd, rd)


def r2_public_rebuild(r2, date_iso, fixed):
    """R2's public 10-year equivalents (total less SOMA) at one record date on a fixed curve, by kind and remaining-maturity
    bucket, from R2's own functions. Returns (total, {(kind, bucket): public tenyeq}, aggregate-check difference)."""
    f_nom, f_real, f_d10 = fixed[0], fixed[1], fixed[2]
    rd = dt.date.fromisoformat(date_iso)
    rows, _ = r2.load_mspd_table3(date_iso)
    buckets, _, _, _ = r2.cusips_from_table3(rows, date_iso)
    soma_dates = r2.load_soma_dates()
    asof = r2.on_or_before(soma_dates, rd)
    soma_by_kind, _ = r2.soma_securities(r2.load_soma_holdings(asof.isoformat()), asof)
    out = collections.defaultdict(Fsum)
    check_total = check_agg = 0.0
    for kind in ("bills", "coupons", "tips", "frn"):
        # a copy of the ten-line closure `securities_for` inside r2.compute_date (it is not importable): same arithmetic
        secs = [(rec["par"] / 1000.0, rec["coupon"], max((dt.date.fromisoformat(rec["maturity"]) - rd).days / 365.25, 0.0))
                for rec in buckets[kind].values()]
        for sign, items in ((1.0, secs), (-1.0, soma_by_kind[kind])):
            for par_bn, coupon, T in items:
                price, dur = r2.price_one(kind, coupon, T, f_nom, f_real)
                eq = par_bn * price / 100.0 * dur / f_d10
                out[(kind, bucket_of(T))].add(sign * eq)
            check_total += sign * r2.aggregate(items, kind, f_nom, f_real, f_d10)[2]
    total = math.fsum(v.value() for v in out.values())
    return total, {k: v.value() for k, v in out.items()}, abs(total - check_total)


# ======================================================================================================== Z.1
def z1_series(csv_path, code):
    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        return {r["date"]: float(r[code]) for r in csv.DictReader(fh) if r.get(code) not in (None, "", "ND")}


def z1_code_ok(txt_path, code, needle="Treasury securities"):
    """Cross-check a series code against the table's own data dictionary text (the description must name Treasuries)."""
    with open(txt_path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith(code):
                return needle in line
    return False


def load_z1(z1_dir, etf_dir):
    spec = [("mf", z1_dir, "S124_1_s", "LM653061105.Q"), ("cef", z1_dir, "S124_2_s", "LM553061103.Q"),
            ("etf", etf_dir, "S124_3_s", "LM563061103.Q"),
            ("mf_flow", z1_dir, "S124_1_t_tu", "FU653061105.Q"), ("cef_flow", z1_dir, "S124_2_t_tu", "FU553061103.Q"),
            ("etf_flow", etf_dir, "S124_3_t_tu", "FU563061103.Q")]
    out, notes = {}, []
    for name, d, table, code in spec:
        csvp, txtp = os.path.join(d, table + ".csv"), os.path.join(d, table + ".txt")
        for p in (csvp, txtp):
            if not os.path.exists(p):
                raise SystemExit(f"{p} is missing; run python3 bin/nport_fetch_z1.py (S.124.1, S.124.2) or restore {etf_dir}")
        if not z1_code_ok(txtp, code):
            raise SystemExit(f"{code} is not described as Treasury securities in {txtp}; refusing")
        out[name] = z1_series(csvp, code)     # $ millions
        notes.append(f"{code}={table}")
    return out, notes


def read_key_value(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return {r["key"]: r["value"] for r in csv.DictReader(fh)}


def par_bond_factor(r2, fixed, n):
    """10-year equivalent of $1 of an n-year par bond on the fixed curve: par_mod_duration at that curve's n-year yield, over d10."""
    return r2.par_mod_duration(r2.interp_curve(fixed[0], n), n=n) / fixed[2]


def dv01_ratio(reported, computed):
    """N6: DV01 is compared on magnitude only, since the sign differs by filer."""
    return abs(reported) / abs(computed)


# ======================================================================================================== verdict
def verdict_label(ds, first, bystander):
    """N1, one arm. `ds` is a number, or a (lo, hi) band (the Z.1-scaled arm)."""
    lo, hi = (ds, ds) if not isinstance(ds, tuple) else ds
    if lo >= first:
        return "FIRST-ORDER SINK"
    if hi < bystander:
        return "BYSTANDER"
    return "PARTICIPANT"


def combine_verdicts(measured, scaled):
    return measured if measured == scaled else "NOT ESTABLISHED"


# ======================================================================================================== anchors, checks
def load_anchors(path):
    if not os.path.exists(path):
        raise SystemExit(f"{path} is missing; it is committed beside the outputs (N8)")
    with open(path, newline="", encoding="utf-8") as fh:
        return {(r["scope"], r["key"]): (r["value"], r["tolerance"]) for r in csv.DictReader(fh)}


def anchor_num(anchors, scope, key):
    v = anchors.get((scope, key))
    if v is None or v[0].startswith("N/A"):
        return None, None
    return float(v[0]), (float(v[1]) if v[1] not in ("", "exact") else 0.0)


def check_c1(shas, anchors, prior):
    """C1. shas {zip name: sha256}; anchors from tsy_anchors.csv (the pins, bootstrap only); prior {zip name: sha256} from
    the previously committed tsy_file_stats.csv. Returns (result, note, details)."""
    bad, compared = [], 0
    for name, sha in sorted(shas.items()):
        pin = anchors.get((name.replace("_nport.zip", ""), "zip_sha256"), (NO_ANCHOR, ""))[0]
        for ref in (pin if not pin.startswith("N/A") else None, prior.get(name)):
            if ref is None:
                continue
            compared += 1
            if ref != sha:
                bad.append(name)
    return ("FAIL" if bad else "PASS"), bad, compared


def mk(cid, scope, label, ours, ref, thr, result, hard, note=""):
    return {"check_id": cid, "scope": scope, "label": label, "ours": ours, "reference": ref, "threshold": thr,
            "result": result, "hard": "Y" if hard else "N", "note": note}


def fmt(x):
    if isinstance(x, float):
        x = round(x, 6)
        return 0.0 if x == 0 else x
    return "" if x is None else x


def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: fmt(r.get(c)) for c in cols})


def pct_q(sorted_vals, q):
    """Linear-interpolated quantile of an already sorted list."""
    if not sorted_vals:
        return None
    pos = (len(sorted_vals) - 1) * q
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


# ======================================================================================================== pre-flight
def run_preflight():
    """N11: the script runs its own test file before it builds anything."""
    path = os.path.join(HERE, "test_nport_treasury_duration.py")
    if not os.path.exists(path):
        raise SystemExit(f"{path} is missing; refusing to build without the tests")
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    sys.modules.setdefault("nport_treasury_duration", sys.modules[__name__])
    mod = load_by_path("test_nport_treasury_duration", path)
    suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
    res = unittest.TextTestRunner(stream=sys.stderr, verbosity=0).run(suite)
    if not res.wasSuccessful():
        raise SystemExit("pre-flight tests failed; nothing was built")
    print(f"pre-flight: {res.testsRun} tests passed", file=sys.stderr)


# ======================================================================================================== main build
def build(a):
    t0 = time.time()

    def log(msg):
        print(f"[{time.time() - t0:6.1f}s] {msg}", file=sys.stderr, flush=True)

    zips = discover_zips(a.zip_dir)
    windows = make_windows(zips)
    r1_cache, r2_cache = os.path.abspath(a.r1_cache), os.path.abspath(a.r2_cache)
    check_caches(r1_cache, r2_cache)
    anchors = load_anchors(a.anchors)
    r2 = load_r2(r1_cache, r2_cache)
    if not set(R2_DATES_USED) <= set(r2.DATES):
        raise SystemExit("R2_DATES_USED is not inside R2's DATES; the spec's four R2 dates changed")
    log(f"{len(zips)} zips -> windows {windows[0].label}..{windows[-1].label}")

    # ---- R2's curves, MSPD union, fixed curves -------------------------------------------------------------------
    nom_all, real_all = r2.load_curve("daily_treasury_yield_curve"), r2.load_curve("daily_treasury_real_yield_curve")
    fixed = r2_fixed_curve(r2, nom_all, real_all, r2.FIXED_CURVE_DATE)
    alt = r2_fixed_curve(r2, nom_all, real_all, ALT_CURVE_DATE)
    mspd, ratios = build_mspd(r2)
    pricer = Pricer(r2, nom_all, real_all, fixed, alt)
    log(f"fixed curve {fixed[3]} / {fixed[4]}, d10 {fixed[2]:.4f}; MSPD union {len(mspd)} CUSIPs")

    # ---- sha256, metadata, pass A ---------------------------------------------------------------------------------
    shas = {os.path.basename(p): file_sha256(p) for _, _, p in zips}
    log("sha256 of all zips")
    all_filings, zinfo, subcounts = [], [], {}
    for i, (y, q, path) in enumerate(zips):
        z = zipfile.ZipFile(path)
        fl = load_zip_filings(z, i)
        st, sfl = scan_zip_holdings(z, fl)
        tag = windows[i].zip_tag
        zinfo.append((tag, os.path.basename(path), fl, st, sfl))
        subcounts[os.path.basename(path)] = (len(fl), collections.Counter(x.rdate for x in fl))
        all_filings.extend(fl)
        log(f"pass A {tag}: {len(fl):,} filings, {st['holding_rows']:,} holding rows, {st['tsy_lines_kept']:,} Treasury lines")
    fba = {f.acc: f for f in all_filings}

    # ---- survivors ------------------------------------------------------------------------------------------------
    sel = {v: select_vintage(all_filings, windows, v) for v in ("base", "matched")}
    memb = {}
    for v, bit in (("base", 1), ("matched", 2)):
        for wi, lst in sel[v]["assign"].items():
            for f, _tag in lst:
                w0, m0 = memb.get(f.acc, (wi, 0))
                memb[f.acc] = (wi, m0 | bit)
    log(f"survivors: base {len(sel['base']['kept']):,} filings, matched {len(sel['matched']['kept']):,}")

    # ---- pass B ---------------------------------------------------------------------------------------------------
    ctx = Ctx(r2, pricer, mspd, ratios, windows, fba)
    for i, (y, q, path) in enumerate(zips):
        z = zipfile.ZipFile(path)
        wanted = {acc for acc, (wi, mask) in memb.items() if fba[acc].zipi == i}
        lines = stream_survivor_lines(z, wanted)
        debt = read_debt(z, {L.hid for L in lines})
        ctx.irr.update(read_dv01(z, wanted))
        ctx.process_lines(windows[i].zip_tag, lines, debt, memb)
        log(f"pass B {windows[i].zip_tag}: {len(wanted):,} filings, {len(lines):,} lines, {len(debt):,} DEBT rows")
    ctx.resolve_pending()
    log("pending maturities resolved")

    return dict(a=a, t0=t0, log=log, zips=zips, windows=windows, shas=shas, anchors=anchors, r2=r2, nom_all=nom_all,
                real_all=real_all, fixed=fixed, alt=alt, mspd=mspd, ratios=ratios, zinfo=zinfo, subcounts=subcounts,
                all_filings=all_filings, fba=fba, sel=sel, memb=memb, ctx=ctx, r1_cache=r1_cache, r2_cache=r2_cache)


def r2_rows(B):
    """C10 and the public buckets: rebuild R2's public totals at the four R2 dates on the base fixed curve and on the M8 curve."""
    r2 = B["r2"]
    with open(os.path.join(ROOT, "data", "r2_rates", "duration_supply.csv"), newline="", encoding="utf-8") as fh:
        base_csv = {r["record_date"]: r for r in csv.DictReader(fh)}
    pub, pub_alt, buckets = {}, {}, {}
    for d in R2_DATES_USED:
        tot, bk, diff = r2_public_rebuild(r2, d, B["fixed"])
        pub[d] = (tot, diff, float(base_csv[d]["public_10yeq_fixed_bn"]))
        buckets[d] = bk
        tot_a, _, _ = r2_public_rebuild(r2, d, B["alt"])
        pub_alt[d] = tot_a
    return pub, pub_alt, buckets


def derive_main(B, a):
    """After the line pass: Z.1 levels, R2 rebuilds, the window, bucket, change and verdict tables."""
    log, windows, ctx, sel = B["log"], B["windows"], B["ctx"], B["sel"]
    r2, anchors = B["r2"], B["anchors"]
    by_label = {w.label: w for w in windows}
    pub, pub_alt, pub_bk = r2_rows(B)
    log("R2 public totals rebuilt at four dates on two fixed curves")
    z1, z1_notes = load_z1(a.z1_dir, a.etf_dir)
    z1_prov = read_key_value(os.path.join(a.z1_dir, "z1_provenance.csv"))
    r2w = {}                                      # window label -> R2 date, for the windows that are R2 dates
    for w in windows:
        if w.qend.isoformat() in R2_DATES_USED:
            r2w[w.label] = w.qend.isoformat()

    def z1v(name, w):
        v = z1[name].get(w.z1_key)
        return None if v is None else v / 1000.0

    # ---- tsy_windows ----------------------------------------------------------------------------------------------
    rows_w, winvals = [], {}
    for w in windows:
        for vint in ("base", "matched"):
            ag = ctx.agg[(vint, w.idx)]
            sel_v = sel[vint]
            lst = sel_v["assign"][w.idx]
            pos = collections.Counter(t for _, t in lst)
            mf, et, ce = z1v("mf", w), z1v("etf", w), z1v("cef", w)
            zsum = None if None in (mf, et, ce) else mf + et + ce
            val = ag.val("value")
            d = r2w.get(w.label)
            pubv = pub[d][2] if d else None
            te = ag.val("tenyeq_fixed")
            row = dict(window=w.label, quarter_end=w.qend.isoformat(), vintage=vint, months="|".join(w.months),
                       funds_in_window=len(lst), funds_m_minus1=pos["m-1"], funds_m0=pos["m0"], funds_m_plus1=pos["m+1"],
                       funds_with_tsy=len(ag.funds), tsy_lines=ag.lines, tsy_value_bn=val,
                       tsy_value_series_bn=ag.val("value_series"), tsy_value_noseries_bn=ag.val("value_noseries"),
                       tsy_par_bn=ag.val("par"), tenyeq_fixed_bn=te, tenyeq_fixed_alt_bn=ag.val("tenyeq_alt"),
                       tenyeq_own_bn=ag.val("tenyeq_own"), pardur_fixed_bn_yrs=ag.val("pardur_fixed"),
                       dv01_own_mn=ag.val("dv01_own"), strips_tenyeq_fixed_bn=ag.val("strips_tenyeq_fixed"),
                       short_value_bn=ag.val("short_value"), unpriced_lines=ag.unpriced_lines,
                       unpriced_value_bn=ag.val("unpriced_value"), tips_orig_lines=ag.tips_orig_lines,
                       tips_orig_par_added_bn=ag.val("tips_orig_par_added"),
                       tips_orig_tenyeq_fixed_bn=ag.val("tips_orig_tenyeq_fixed"), z1_mf_bn=mf, z1_etf_bn=et, z1_cef_bn=ce, z1_sum_bn=zsum,
                       nport_over_z1=(val / zsum if zsum else None), r2_public_10yeq_fixed_bn=pubv,
                       share_of_public_fixed=(te / pubv if pubv else None))
            rows_w.append(row)
            winvals[(vint, w.label)] = row
    log("tsy_windows built")

    # ---- tsy_buckets ----------------------------------------------------------------------------------------------
    rows_b = []
    for w in windows:
        ag = ctx.agg[("base", w.idx)]
        d = r2w.get(w.label)
        for kind in KINDS:
            for bk in BUCKETS + ("n/a",):
                b = ag.buckets.get((kind, bk))
                pubv = pub_bk[d].get((kind, bk), 0.0) if d and kind in ("bills", "coupons", "tips", "frn") else None
                if b is None and not pubv:
                    continue
                n, val, par, te = (b[0], b[1].value(), b[2].value(), b[3].value()) if b else (0, 0.0, 0.0, 0.0)
                rows_b.append(dict(window=w.label, kind=kind, bucket=bk, lines=n, value_bn=val, par_bn=par,
                                   tenyeq_fixed_bn=te, eff_factor=(te / par if par else None),
                                   public_tenyeq_fixed_bn=pubv, share_of_public=(te / pubv if pubv and pubv > 0 else None)))
    # ---- tsy_change -----------------------------------------------------------------------------------------------
    order = sorted(r2w, key=lambda k: by_label[k].idx)
    if len(order) < 2:
        raise SystemExit("fewer than two windows fall on R2 dates; the change cannot be formed")
    periods = [("full", order[0], order[-1])]
    for i in range(len(order) - 1):
        lab = ("2024", "2025", "2026H1")[i] if len(order) == 4 else f"{order[i]}-{order[i + 1]}"
        periods.append((lab, order[i], order[i + 1]))
    base_row = {lab: winvals[("base", lab)] for lab in by_label}

    def s_of(variant, lab):
        b, m = winvals[("base", lab)], winvals[("matched", lab)]
        if variant in ("M0", "D6"):
            return b["tenyeq_fixed_bn"]
        if variant == "M1":
            return m["tenyeq_fixed_bn"]
        if variant == "M8":
            return b["tenyeq_fixed_alt_bn"]
        w = by_label[lab]
        ag = ctx.agg[("base", w.idx)]
        if variant == "P1":
            return b["tenyeq_fixed_bn"] * b["z1_sum_bn"] / b["tsy_value_bn"]
        if variant == "P2":
            return ag.val("tenyeq_fixed_series") * (b["z1_mf_bn"] + b["z1_etf_bn"]) / b["tsy_value_series_bn"]
        raise KeyError(variant)

    def p_of(variant, lab):
        d = r2w[lab]
        return pub_alt[d] if variant == "M8" else pub[d][2]      # the R2 column as published; C10 checks the rebuild against it

    VARIANTS = [("M0", "base", "MEASURED", "base: all zips with FILING_DATE <= REPORT_DATE + 62 days, R2 basis, fixed 2023-12-29 curve",
                 "public_10yeq_fixed_bn"),
                ("M1", "method", "MEASURED", "matched vintage: zips up to each window's home zip, no lag cut", "public_10yeq_fixed_bn"),
                ("M8", "method", "MEASURED", f"fixed curve of {ALT_CURVE_DATE} in place of 2023-12-29 (P rebuilt per section 4.2)",
                 f"public_10yeq_fixed_bn rebuilt on the {ALT_CURVE_DATE} curve"),
                ("P1", "population", "HYPOTHESIS", "S x (Z.1 mutual funds + ETFs + closed-end) / N-PORT window value", "public_10yeq_fixed_bn"),
                ("P2", "population", "HYPOTHESIS", "series funds only x (Z.1 mutual funds + ETFs) / N-PORT series-fund value", "public_10yeq_fixed_bn"),
                ("D6", "diagnostic", "MEASURED", "ISIN recovery switched off (identical to base: recovery is deferred)", "public_10yeq_fixed_bn")]
    dp_base = None
    rows_c, chg = [], {}
    for vid, arm, grade, desc, comp in VARIANTS:
        for per, a0, a1 in periods:
            s0v, s1v = s_of(vid, a0), s_of(vid, a1)
            p0, p1 = p_of(vid, a0), p_of(vid, a1)
            ds, dp = s1v - s0v, p1 - p0
            sh0 = s0v / p0
            r = ds / dp
            scale = (dp / (pub[r2w[a1]][2] - pub[r2w[a0]][2])) if vid == "M8" else 1.0
            lab = verdict_label(ds, FIRST_ORDER_BN * scale, BYSTANDER_BN * scale) if per == "full" else ""
            rows_c.append(dict(variant_id=vid, arm=arm, grade=grade, description=desc, comparator=comp, period=per,
                               s_start=s0v, s_end=s1v, d_s=ds, p_start=p0, p_end=p1, d_p=dp, r=r, s0=sh0,
                               excess_pp=(r - sh0) * 100.0, excess_bn=ds - sh0 * dp, label=lab))
            chg[(vid, per)] = rows_c[-1]
    log("tsy_change built")

    # ---- tsy_verdict ----------------------------------------------------------------------------------------------
    M0, P1, P2 = chg[("M0", "full")], chg[("P1", "full")], chg[("P2", "full")]
    dP = M0["d_p"]
    lo, hi = min(P1["d_s"], P2["d_s"]), max(P1["d_s"], P2["d_s"])
    meas_label = verdict_label(M0["d_s"], FIRST_ORDER_BN, BYSTANDER_BN)
    scaled_label = verdict_label((lo, hi), FIRST_ORDER_BN, BYSTANDER_BN)
    published = combine_verdicts(meas_label, scaled_label)
    s_meas = 1 if M0["excess_pp"] > 0 else -1
    s_p1, s_p2 = (1 if P1["excess_pp"] > 0 else -1), (1 if P2["excess_pp"] > 0 else -1)
    if s_p1 != s_p2:
        sign_text = "sign not established (P1 and P2 disagree)"
    elif s_meas != s_p1:
        sign_text = "sign not established (the arms differ)"
    else:
        sign_text = "both arms above pro rata" if s_meas > 0 else "both arms below pro rata"
    V = [("scope", "cash Treasuries only"),
         ("population", "registered funds filing Form N-PORT (mutual funds, ETFs, closed-end and interval funds); money market funds (Form N-MFP) and every other holder are outside S"),
         ("basis", "10-year equivalents at the fixed end-2023 curve (R2 public_10yeq_fixed_bn), line by line"),
         ("period", f"{order[0]} ({r2w[order[0]]}) to {order[-1]} ({r2w[order[-1]]})"),
         ("p_start_bn", M0["p_start"]), ("p_end_bn", M0["p_end"]), ("delta_p_bn", dP),
         ("line_first_order_bn", FIRST_ORDER_BN),
         ("line_first_order_note", f"one-seventh of delta_p = {dP / 7.0:.2f}; the item's rounder ${ITEM_ROUND_BN:.0f}bn is printed beside it and does not decide"),
         ("line_item_round_bn", ITEM_ROUND_BN), ("line_bystander_bn", BYSTANDER_BN),
         ("lines_source", "E-021 item 7 research item of 14 Oct 2026, written before any N-PORT file was opened"),
         ("disclosure", "the spec author and a reviewer saw provisional numbers before the build; the dollar lines predate both"),
         ("measured_arm", "N-PORT's own lines, base vintage (variant M0)"),
         ("measured_s_start_bn", M0["s_start"]), ("measured_s_end_bn", M0["s_end"]), ("measured_ds_bn", M0["d_s"]),
         ("measured_r", M0["r"]), ("measured_s0", M0["s0"]), ("measured_excess_pp", M0["excess_pp"]),
         ("measured_excess_bn", M0["excess_bn"]), ("measured_label", meas_label),
         ("z1scaled_arm", "Z.1-scaled: the band over P1 and P2"),
         ("z1scaled_p1_s_start_bn", P1["s_start"]), ("z1scaled_p1_s_end_bn", P1["s_end"]), ("z1scaled_p1_ds_bn", P1["d_s"]),
         ("z1scaled_p1_r", P1["r"]), ("z1scaled_p1_s0", P1["s0"]), ("z1scaled_p1_excess_pp", P1["excess_pp"]),
         ("z1scaled_p1_excess_bn", P1["excess_bn"]),
         ("z1scaled_p2_s_start_bn", P2["s_start"]), ("z1scaled_p2_s_end_bn", P2["s_end"]), ("z1scaled_p2_ds_bn", P2["d_s"]),
         ("z1scaled_p2_r", P2["r"]), ("z1scaled_p2_s0", P2["s0"]), ("z1scaled_p2_excess_pp", P2["excess_pp"]),
         ("z1scaled_p2_excess_bn", P2["excess_bn"]),
         ("z1scaled_band_lo_bn", lo), ("z1scaled_band_hi_bn", hi),
         ("z1scaled_margin_to_first_order_line_bn", lo - FIRST_ORDER_BN), ("z1scaled_label", scaled_label),
         ("verdict", published),
         ("verdict_note", "the arms agree" if meas_label == scaled_label else "the arms give different labels, so the published verdict is NOT ESTABLISHED; both rows are printed"),
         ("excess_over_pro_rata", sign_text),
         ("sensitivity_M1_label", chg[("M1", "full")]["label"]), ("sensitivity_M1_ds_bn", chg[("M1", "full")]["d_s"]),
         ("sensitivity_M8_label", chg[("M8", "full")]["label"]), ("sensitivity_M8_ds_bn", chg[("M8", "full")]["d_s"]),
         ("futures", "not measured in this landing"),
         ("holder_share_not_price_effect", "r is a holder share of cash Treasuries; it says nothing about whether the funds' buying moved yields (C-122), and P - S is a residual (C-098)")]
    rows_v = [dict(key=k, value=v) for k, v in V]

    return dict(rows_w=rows_w, rows_b=rows_b, rows_c=rows_c, rows_v=rows_v, chg=chg, pub=pub, pub_alt=pub_alt,
                winvals=winvals, z1=z1, z1_notes=z1_notes, z1_prov=z1_prov, r2w=r2w, order=order, periods=periods,
                published=published, meas_label=meas_label, scaled_label=scaled_label, by_label=by_label)


def derive_funds(B, F, a):
    """Fund-level tables: the DV01 magnitude check and the largest funds and registrants."""
    windows, ctx, sel, zinfo = B["windows"], B["ctx"], B["sel"], B["zinfo"]
    anchors, shas, r2 = B["anchors"], B["shas"], B["r2"]
    winvals, by_label, r2w, pub = F["winvals"], F["by_label"], F["r2w"], F["pub"]

    # ---- tsy_dv01_check -------------------------------------------------------------------------------------------
    rows_d, dv01_med = [], {}
    for w in windows:
        funds = [fa for (wi, fund), fa in ctx.fund_agg.items() if wi == w.idx]
        tot_val = math.fsum(fa.value.value() for fa in funds)
        usd = [fa for fa in funds if fa.f.acc in ctx.irr]
        rows_d.append(dict(window=w.label, universe="any_tsy", n_funds=len(funds),
                           n_pos=sum(1 for fa in usd if ctx.irr[fa.f.acc] > 0), n_neg=sum(1 for fa in usd if ctx.irr[fa.f.acc] < 0),
                           n_zero=sum(1 for fa in usd if ctx.irr[fa.f.acc] == 0),
                           tsy_value_covered_bn=math.fsum(fa.value.value() for fa in usd), tsy_value_bn=tot_val))
        for uni in ("tsy90_usd", "tsy90_usd_no_dir"):
            sub = []
            for fa in usd:
                nav = fa.f.net_assets
                comp = fa.dv01_mn.value() * 1e6          # $ per bp
                if nav > 0 and fa.value.value() * 1e9 / nav >= 0.9 and comp != 0 and (uni == "tsy90_usd" or fa.f.dir_lines == 0):
                    sub.append((dv01_ratio(ctx.irr[fa.f.acc], comp), ctx.irr[fa.f.acc], fa))
            ratios_ = sorted(x[0] for x in sub)
            med = pct_q(ratios_, 0.5)
            dv01_med[(uni, w.label)] = (med, len(sub))
            rows_d.append(dict(window=w.label, universe=uni, n_funds=len(sub), n_pos=sum(1 for x in sub if x[1] > 0),
                               n_neg=sum(1 for x in sub if x[1] < 0), n_zero=sum(1 for x in sub if x[1] == 0),
                               median_ratio=med, p25_ratio=pct_q(ratios_, 0.25), p75_ratio=pct_q(ratios_, 0.75),
                               tsy_value_covered_bn=math.fsum(x[2].value.value() for x in sub), tsy_value_bn=tot_val))

    # ---- tsy_top_funds --------------------------------------------------------------------------------------------
    w_first, w_last = F["by_label"][F["order"][0]], F["by_label"][F["order"][-1]]
    sA, sB = F["order"][0], F["order"][-1]
    f_a = {fund: fa for (wi, fund), fa in ctx.fund_agg.items() if wi == w_first.idx}
    f_b = {fund: fa for (wi, fund), fa in ctx.fund_agg.items() if wi == w_last.idx}
    rows_t = []

    def fund_row(rank_by, rank, fund, a_, b_):
        fa = b_ or a_
        sa = a_.tenyeq.value() if a_ else 0.0
        sb = b_.tenyeq.value() if b_ else 0.0
        return {"rank_by": rank_by, "rank": rank, "fund_key": fund[1], "series_name": fa.f.series_name,
                    "registrant_name": fa.f.registrant_name, f"s_{sA}": sa, f"s_{sB}": sb, "d_s": sb - sa,
                    f"value_{sA}_bn": (a_.value.value() if a_ else 0.0), f"value_{sB}_bn": (b_.value.value() if b_ else 0.0)}
    allf = sorted(set(f_a) | set(f_b))
    for rank_by, keyf in ((f"s_{sB}", lambda fd: -(f_b[fd].tenyeq.value() if fd in f_b else 0.0)),
                          ("d_s", lambda fd: -((f_b[fd].tenyeq.value() if fd in f_b else 0.0) - (f_a[fd].tenyeq.value() if fd in f_a else 0.0)))):
        for i, fd in enumerate(sorted(allf, key=lambda fd: (keyf(fd), fd))[:25], 1):
            rows_t.append(fund_row(rank_by, i, fd, f_a.get(fd), f_b.get(fd)))
    regs = collections.defaultdict(lambda: [Fsum(), Fsum(), Fsum(), Fsum(), "", ""])
    for side, dct in ((0, f_a), (1, f_b)):
        for fd, fa in dct.items():
            r = regs[fa.f.cik or fd[1]]
            r[2 * side].add(fa.tenyeq.value())
            r[2 * side + 1].add(fa.value.value())
            if side == 1 or not r[4]:
                r[4] = fa.f.registrant_name
    rr = []
    for cik, r in regs.items():
        rr.append((-(r[3].value() - r[1].value()), cik, r))
    for i, (_, cik, r) in enumerate(sorted(rr)[:20], 1):
        rows_t.append({"rank_by": "registrant_d_value", "rank": i, "fund_key": cik, "series_name": "", "registrant_name": r[4],
                       f"s_{sA}": r[0].value(), f"s_{sB}": r[2].value(), "d_s": r[2].value() - r[0].value(),
                       f"value_{sA}_bn": r[1].value(), f"value_{sB}_bn": r[3].value()})

    return rows_d, rows_t, dv01_med


# ======================================================================================================== checks and stats
EXCL_REASONS = ("912_not_ust_type", "non912_ust", "derivative", "repo", "abs", "other_asset_cat", "non_usd",
                "blank_value_or_balance")
ANCHOR_CHECK_IDS = {"2026q3": "C3", "2024q1": "C4"}           # SUBMISSION anchors, by zip
WINDOW_CHECK_IDS = {"2023Q4": "C5", "2026Q2": "C6"}           # matched-window anchors, by window
UNVERIFIED_L = ("lens provisional results (base r 16.9%, method arm 16.5-18.0%, population arm 13.5-14.1%, stress floor 8.3%, "
                "s0 14.5%): check C15 dropped; Grok-filter share (13.2% of $1,394.8bn at 2026-06-30); DV01 sign split at "
                "2026-06-30 (600 / 684 / 4); 144 NPORT-P/A filings for 2023-12-31 in five later zips; N-PORT / Z.1 coverage "
                "on the all-zip vintage (95.4%, 101.8%) and the +788.0 / +656.7 changes; 37 of 30,257 value-check lines; "
                "net face of futures; 67 same-CUSIP pairs; par/value medians by kind")


def read_prior_shas(out_dir):
    path = os.path.join(out_dir, "tsy_file_stats.csv")
    if not os.path.exists(path):
        return {}
    by_tag = collections.defaultdict(dict)
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["key"] in ("zip", "zip_sha256"):
                by_tag[r["tag"]][r["key"]] = r["value"]
    return {v["zip"]: v["zip_sha256"] for v in by_tag.values() if "zip" in v and "zip_sha256" in v}


def derive_checks(B, F, D, a):
    windows, ctx, sel, zinfo, shas, anchors = B["windows"], B["ctx"], B["sel"], B["zinfo"], B["shas"], B["anchors"]
    winvals, pub, pub_alt, by_label = F["winvals"], F["pub"], F["pub_alt"], F["by_label"]
    r2, fixed, alt = B["r2"], B["fixed"], B["alt"]
    rows_d, rows_t, dv01_med = D
    checks = []
    PASS, FAIL = "PASS", "FAIL"

    # C1: hashes
    prior = read_prior_shas(a.out)
    res, bad, compared = check_c1(shas, anchors, prior)
    pins = sum(1 for k in shas if not anchors.get((k.replace("_nport.zip", ""), "zip_sha256"), (NO_ANCHOR, ""))[0].startswith("N/A"))
    print(f"C1: {len(shas)} zips hashed; {compared} comparisons ({pins} pins, {len(prior)} previously committed); "
          f"mismatches: {bad or 'none'}", file=sys.stderr)
    checks.append(mk("C1", "ALL", "sha256 of every zip recorded; compared with the pins in tsy_anchors.csv and with the previously committed tsy_file_stats.csv",
                     f"{len(shas)} recorded; {len(bad)} mismatches", f"{pins} pins in tsy_anchors.csv; previous tsy_file_stats.csv compared when present",
                     "0 mismatches", res, True,
                     ("mismatch: " + ", ".join(bad)) if bad else "pins are bootstrap only; the others are N/A (no anchor) until the next run compares them"))

    # C2: unique survivors (before window assignment), then every summed accession summed once (what pass B actually added)
    c2 = {v: (sel[v]["c2"], sel[v]["c2_after"], len(sel[v]["chosen"]), len(sel[v]["kept"])) for v in ("base", "matched")}
    once = check_summed_once(ctx.summed, {acc: f.tsy_lines for acc, f in B["fba"].items()})
    n_summed = {v: len({acc for (vv, _wi), accs in ctx.summed.items() if vv == v for acc in accs}) for v in ("base", "matched")}
    ok = all(x[0] == PASS and x[1] == PASS for x in c2.values()) and once == PASS
    checks.append(mk("C2", "base+matched", "no (fund, report month) has more than one survivor, and no accession is summed twice into one window",
                     "; ".join(f"{v}: {x[0]}/{x[1]} on {x[2]:,}/{x[3]:,} selections" for v, x in c2.items())
                     + f"; summed once: {once} on {n_summed['base']:,}/{n_summed['matched']:,} accessions",
                     "no duplicate (fund, report month); each summed accession in one window, its lines added once", "0 duplicates", PASS if ok else FAIL, True,
                     "check_unique_survivors on the selection before and after the content-duplicate step (both before window assignment); "
                     "check_summed_once on the accessions Ctx.add actually summed, against pass A's Treasury line count"))

    # C3/C4: SUBMISSION anchors
    seen_nonanchor = []
    for name, (n, dates) in sorted(B["subcounts"].items()):
        scope = name.replace("_nport.zip", "")
        exp_total, _ = anchor_num(anchors, scope, "filings_total")
        dkeys = sorted(k for (s, k) in anchors if s == scope and k.startswith("report_date:") and not anchors[(s, k)][0].startswith("N/A"))
        if exp_total is None and not dkeys:
            seen_nonanchor.append(scope)
            continue
        parts_o, parts_r, good = [f"{n} filings"], [f"{int(exp_total)} filings"], (n == int(exp_total))
        for k in dkeys:
            d = dt.date.fromisoformat(k.split(":", 1)[1])
            exp = int(float(anchors[(scope, k)][0]))
            parts_o.append(f"{d} {dates.get(d, 0)}")
            parts_r.append(f"{d} {exp}")
            good = good and dates.get(d, 0) == exp
        cid = ANCHOR_CHECK_IDS.get(scope, f"C3-{scope}")
        checks.append(mk(cid, scope, f"{name} SUBMISSION: filing count and REPORT_DATE counts", "; ".join(parts_o), "; ".join(parts_r),
                         "exact", PASS if good else FAIL, True, "[S] anchor from tsy_anchors.csv"))
    if seen_nonanchor:
        checks.append(mk("C3/C4", ",".join(seen_nonanchor), "SUBMISSION counts for the zips with no anchor", "recorded in tsy_file_stats.csv",
                         NO_ANCHOR, "", "N/A", False, "no anchor to compare with"))

    # C5/C6: matched window, section 3.1 rule before the content-duplicate step
    for w in windows:
        cid = WINDOW_CHECK_IDS.get(w.label)
        lst = sel["matched"]["assign_pre"][w.idx]
        funds = len(lst)
        val = math.fsum(f.tsy_value for f, _ in lst) / 1e9
        fmin, _ = anchor_num(anchors, w.label, "matched_funds_min")
        fmax, _ = anchor_num(anchors, w.label, "matched_funds_max")
        fx, _ = anchor_num(anchors, w.label, "matched_funds")
        vx, vtol = anchor_num(anchors, w.label, "matched_value_bn")
        if cid is None or vx is None:
            continue
        lo, hi = (fmin, fmax) if fmin is not None else (fx, fx)
        good = lo <= funds <= hi and abs(val - vx) <= vtol + 1e-9
        checks.append(mk(cid, w.label, f"{w.label} matched window, section 3.1 rule before the content-duplicate step: funds and Treasury value (no ISIN recovery)",
                         f"{funds:,} funds; ${val:,.1f}bn", f"{int(lo):,}-{int(hi):,} funds; ${vx:,.1f}bn +/- {vtol}",
                         "funds in range; value within tolerance", PASS if good else FAIL, True, "[S] anchor from tsy_anchors.csv; base uses N2 and N3 so differs"))
    # C7: kind rules 1-3
    shares = []
    for w in windows:
        ag = ctx.agg[("base", w.idx)]
        v = ag.val("value")
        shares.append((ag.val("value_rule123") / v if v else 1.0, w.label))
    mn = min(shares)
    checks.append(mk("C7", "base, all windows", "kind rules (1)-(3) classify at least 99.9% of each window's Treasury value", f"min {mn[0] * 100:.4f}% ({mn[1]})",
                     ">= 99.9%", ">= 99.9%", PASS if mn[0] >= 0.999 else FAIL, True, "2026Q2 reference 99.99% [S]"))
    # C8: bucket identity
    worst = 0.0
    for w in windows:
        ag = ctx.agg[("base", w.idx)]
        sv = math.fsum(b[1].value() for b in ag.buckets.values())
        sp = math.fsum(b[2].value() for b in ag.buckets.values())
        st = math.fsum(b[3].value() for b in ag.buckets.values())
        worst = max(worst, abs(sv - ag.val("value")), abs(sp - ag.val("par")), abs(st - ag.val("tenyeq_fixed")))
    checks.append(mk("C8", "base, all windows", "bucket sums equal window totals (value, par, 10-year equivalents): an IDENTITY, not evidence",
                     f"max abs diff {worst:.2e} $bn", "0", "<= 1e-6 $bn", PASS if worst <= 1e-6 else FAIL, True, "identity"))
    # C9: fixed curve
    nd, rd, d10 = fixed[3], fixed[4], fixed[2]
    f10, f2, f30 = (par_bond_factor(r2, fixed, n) for n in (10, 2, 30))
    ax = {k: anchor_num(anchors, "ALL", k) for k in ("d10_fixed", "factor_10y", "factor_2y", "factor_30y")}
    good = (nd == dt.date(2023, 12, 29) and rd == dt.date(2023, 12, 29) and abs(d10 - ax["d10_fixed"][0]) <= ax["d10_fixed"][1]
            and abs(f10 - ax["factor_10y"][0]) <= ax["factor_10y"][1] and abs(f2 - ax["factor_2y"][0]) <= ax["factor_2y"][1]
            and abs(f30 - ax["factor_30y"][0]) <= ax["factor_30y"][1])
    checks.append(mk("C9", "ALL", "fixed curve resolves to 2023-12-29; d10_fixed and the 10y/2y/30y fixed-curve par-bond factors",
                     f"{nd}/{rd}; d10 {d10:.4f}; 10y {f10:.4f}; 2y {f2:.4f}; 30y {f30:.4f}",
                     f"2023-12-29; d10 {ax['d10_fixed'][0]}; 10y {ax['factor_10y'][0]}; 2y {ax['factor_2y'][0]}; 30y {ax['factor_30y'][0]}",
                     "+/- 0.0001", PASS if good else FAIL, True, "[S] anchors from tsy_anchors.csv"))
    # C10: R2 replication
    for d in R2_DATES_USED:
        tot, diff, ref = pub[d]
        checks.append(mk("C10", d, "rebuilt public 10yeq on the fixed curve (R2's own functions) vs duration_supply.csv public_10yeq_fixed_bn",
                         f"{tot:.4f}", f"{ref}", "|diff| <= 0.1", PASS if abs(tot - ref) <= 0.1 else FAIL, True,
                         f"diff {tot - ref:+.4f}; r2.aggregate cross-check of the bucketed copy: {diff:.2e}"))
    # C11: unpriced
    worst = max(((ctx.agg[("base", w.idx)].val("unpriced_value") / ctx.agg[("base", w.idx)].val("value")), w.label,
                 ctx.agg[("base", w.idx)].unpriced_lines, ctx.agg[("base", w.idx)].val("unpriced_value")) for w in windows)
    checks.append(mk("C11", "base, all windows", "unpriced value as a share of window value", f"max {worst[0] * 100:.4f}% ({worst[1]}: {worst[2]} lines, ${worst[3]:.3f}bn)",
                     "lens: 110-114 lines, $1.3-1.4bn [L]", "<= 0.5%", PASS if worst[0] <= 0.005 else FAIL, True, ""))
    # C12: DV01 magnitude
    w0, w1 = F["order"][0], F["order"][-1]                  # the first and last windows that sit on R2 dates
    m0, m1 = dv01_med[("tsy90_usd", w0)], dv01_med[("tsy90_usd", w1)]
    good = all(x[0] is not None and 0.85 <= x[0] <= 1.15 for x in (m0, m1))
    checks.append(mk("C12", f"{w0}, {w1}", "median of |reported DV01| / computed DV01, funds with Treasuries >= 90% of NAV and a USD row (a magnitude check; the sign is as filed)",
                     f"{w0}: {m0[0]:.4f} on {m0[1]} funds; {w1}: {m1[0]:.4f} on {m1[1]} funds" if m0[0] and m1[0] else "n/a",
                     "reviewer: 0.999 on 350 funds", "in [0.85, 1.15]", PASS if good else FAIL, True,
                     "also printed for the stricter universe tsy90_usd_no_dir in tsy_dv01_check.csv"))
    # C13: coverage of Z.1
    c13, other = [], []
    for w in windows:
        r_ = winvals[("base", w.label)]["nport_over_z1"]
        (c13 if w.label in (w0, w1) else other).append((w.label, r_))
    good = all(r_ is not None and 0.90 <= r_ <= 1.10 for _, r_ in c13)
    checks.append(mk("C13", f"{w0}, {w1}", "N-PORT window Treasury value / Z.1 three-row sum, base vintage", "; ".join(f"{l} {r_ * 100:.2f}%" for l, r_ in c13),
                     "lens: 95.4% and 101.8% on the all-zip vintage [L]", "[90%, 110%]", PASS if good else FAIL, True, ""))
    outside = [f"{l} {r_ * 100:.2f}%" for l, r_ in other if r_ is None or not 0.90 <= r_ <= 1.10]
    checks.append(mk("C13b", "other windows", "the same ratio at the other windows (FLAG outside [90%, 110%])",
                     "; ".join(f"{l} {r_ * 100:.1f}%" for l, r_ in other if r_ is not None), "", "[90%, 110%]", "FLAG" if outside else PASS, False,
                     ("outside: " + ", ".join(outside)) if outside else ""))
    # C14, C16 (flags), C17, C19
    vcl = sum(st["value_check_lines"] for _, _, _, st, _ in zinfo)
    vcb = sum(st["value_check_bad"] for _, _, _, st, _ in zinfo)
    checks.append(mk("C14", "all zips", "CURRENCY_VALUE vs PERCENTAGE/100 x NET_ASSETS differs by more than $5 + 0.01%, share of Treasury lines with a PERCENTAGE",
                     f"{vcb:,} of {vcl:,} = {100.0 * vcb / vcl:.3f}%" if vcl else "n/a", "37 of 30,257 at 2026-06-30 [L]", "<= 1%",
                     "PASS" if vcl and vcb / vcl <= 0.01 else "FLAG", False, "all filings in the zips, not only survivors"))
    mb = sum(ctx.zstats[w.zip_tag]["maturity_both_lines"] for w in windows)
    ma = sum(ctx.zstats[w.zip_tag]["maturity_both_agree_lines"] for w in windows)
    checks.append(mk("C16", "survivor lines", "MSPD and DEBT maturities agree where both exist", f"{ma:,} of {mb:,} = {100.0 * ma / mb:.4f}%" if mb else "n/a",
                     "53,783 of 53,785 in the 2026Q2 window [S]", ">= 99.9%", "PASS" if mb and ma / mb >= 0.999 else "FLAG", False, ""))
    pa = {v: sel[v]["info"]["partial_amendments"] for v in ("base", "matched")}
    checks.append(mk("C17", "base, matched", "superseding NPORT-P/A with under 50% of the holding lines of the filing it replaces",
                     f"base {pa['base']}; matched {pa['matched']}", "", "count", "FLAG" if pa["base"] else PASS, False,
                     "line counts only: whether a P/A is a complete restatement is OPEN 5"))
    dd = {v: (len(sel[v]["dropped"]), math.fsum(f.tsy_value for f in sel[v]["dropped"]) / 1e9) for v in ("base", "matched")}
    st_ = {v: sel[v]["info"]["stubs_ignored"] for v in ("base", "matched")}
    t0_, t1_ = winvals[("base", w0)], winvals[("base", w1)]
    tips_note = (f"TIPS read as original face (base): {w0} {t0_['tips_orig_lines']:,} lines, +${t0_['tips_orig_par_added_bn']:.3f}bn par, "
                 f"+${t0_['tips_orig_tenyeq_fixed_bn']:.3f}bn 10yeq; {w1} {t1_['tips_orig_lines']:,} lines, +${t1_['tips_orig_par_added_bn']:.3f}bn par, "
                 f"+${t1_['tips_orig_tenyeq_fixed_bn']:.3f}bn 10yeq; effect on dS +${t1_['tips_orig_tenyeq_fixed_bn'] - t0_['tips_orig_tenyeq_fixed_bn']:.3f}bn")
    checks.append(mk("C19", "base, matched", "N3/N4 adjustments: content duplicates removed, zero-line amendments ignored, TIPS lines read as original face",
                     f"duplicates removed base {dd['base'][0]} (${dd['base'][1]:.3f}bn), matched {dd['matched'][0]} (${dd['matched'][1]:.3f}bn); "
                     f"stubs ignored base {st_['base']}, matched {st_['matched']}; {tips_note}", "", "count",
                     "FLAG" if (dd["base"][0] or st_["base"] or t0_["tips_orig_lines"] or t1_["tips_orig_lines"]) else PASS, False,
                     "reported, not assumed; the content-duplicate step is dormant when the lag cut already removes the later filing"))
    # C20: Z.1 flows (printed, never forced)
    z1 = F["z1"]
    span = windows[by_label[w0].idx + 1: by_label[w1].idx + 1]
    flows = {k: math.fsum(z1[k].get(w.z1_key, 0.0) for w in span) / 1000.0 for k in ("mf_flow", "etf_flow", "cef_flow")}
    fsum_ = sum(flows.values())
    zl0, zl1 = winvals[("base", w0)]["z1_sum_bn"], winvals[("base", w1)]["z1_sum_bn"]
    dpar = {v: winvals[(v, w1)]["tsy_par_bn"] - winvals[(v, w0)]["tsy_par_bn"] for v in ("base", "matched")}
    dval = {v: winvals[(v, w1)]["tsy_value_bn"] - winvals[(v, w0)]["tsy_value_bn"] for v in ("base", "matched")}
    checks.append(mk("C20", f"{windows[by_label[w0].idx + 1].label}-{w1}", "Z.1 reconciliation, printed and never forced: change in N-PORT par and value against Z.1 unadjusted flows and level change",
                     f"d par base {dpar['base']:+.1f} matched {dpar['matched']:+.1f}; d value base {dval['base']:+.1f} matched {dval['matched']:+.1f}",
                     f"Z.1 flows {fsum_:+.1f} (MF {flows['mf_flow']:+.1f}, ETF {flows['etf_flow']:+.1f}, CEF {flows['cef_flow']:+.1f}); Z.1 level change {zl1 - zl0:+.1f}; "
                     f"Grok's seasonally adjusted sum 640.0 [L]", "printed", "FLAG", False,
                     "par is not market value and TIPS accrue inflation without trades; the gap is OPEN 1 (spec section 9)"))
    checks.append(mk("C15", "ALL", "|r(M1) - 16.9%| <= 1.0pp against the lens's independent implementation", "not computed", "16.9% [L]", "", "N/A", False,
                     "dropped (N13): an [L] value the build cannot reproduce; listed as unverified in tsy_file_stats.csv"))
    return checks


def build_file_stats(B, F, D, a):
    windows, ctx, sel, zinfo, shas = B["windows"], B["ctx"], B["sel"], B["zinfo"], B["shas"]
    rows = []

    def add(tag, key, val):
        rows.append({"tag": tag, "key": key, "value": val})

    for (tag, zname, fl, st, sfl), w in zip(zinfo, windows):
        add(tag, "zip", zname)
        add(tag, "zip_sha256", shas[zname])
        add(tag, "window", w.label)
        add(tag, "holding_rows", st["holding_rows"])
        add(tag, "holding_rows_without_filing", st["holding_rows_without_filing"])
        add(tag, "filings_total", len(fl))
        add(tag, "filings_NPORT-P", sum(1 for f in fl if f.sub_type == "NPORT-P"))
        add(tag, "filings_NPORT-P/A", sum(1 for f in fl if f.sub_type == "NPORT-P/A"))
        add(tag, "filings_with_zero_holding_lines", sum(1 for f in fl if f.total_lines == 0))
        add(tag, "report_date_min", min(f.rdate for f in fl).isoformat())
        add(tag, "report_date_max", max(f.rdate for f in fl).isoformat())
        add(tag, "filing_date_min", min(f.fdate for f in fl).isoformat())
        add(tag, "filing_date_max", max(f.fdate for f in fl).isoformat())
        add(tag, "tsy_lines_kept", st["tsy_lines_kept"])
        add(tag, "tsy_value_kept_bn", fmt(sfl.get("tsy_value_kept_bn", 0.0)))
        for r in EXCL_REASONS:
            add(tag, f"excl_lines_{r}", st[f"excl_lines_{r}"])
            add(tag, f"excl_value_bn_{r}", fmt(sfl.get(f"excl_value_bn_{r}", 0.0)))
        add(tag, "usga_non912_lines_ignored", st["usga_non912_lines_ignored"])
        add(tag, "value_check_lines", st["value_check_lines"])
        add(tag, "value_check_bad", st["value_check_bad"])
        add(tag, "unit_ns_lines", st["unit_ns_lines"])
        add(tag, "short_lines", st["short_lines"])
        zs, zf = ctx.zstats[tag], ctx.zfl[tag]
        add(tag, "survivor_lines", sum(zs[f"kind_rule_{r}_lines"] for r in range(1, 7)))
        add(tag, "debt_rows_joined", zs["debt_rows_joined"])
        for r in range(1, 7):
            add(tag, f"kind_rule_{r}_lines", zs[f"kind_rule_{r}_lines"])
            add(tag, f"kind_rule_{r}_value_bn", fmt(zf.get(f"kind_rule_{r}_value_bn", 0.0)))
        for src in ("mspd", "rate", "rate_x100", "none"):
            add(tag, f"coupon_src_{src}", zs[f"coupon_src_{src}"])
        add(tag, "maturity_both_lines", zs["maturity_both_lines"])
        add(tag, "maturity_both_agree_lines", zs["maturity_both_agree_lines"])
        add(tag, "maturity_modal_lines", zs["maturity_modal_lines"])
        add(tag, "maturity_unpriced_lines", zs["maturity_unpriced_lines"])
        add(tag, "tips_original_face_lines", zs["tips_original_face_lines"])
        add(tag, "tips_original_face_par_added_bn", fmt(zf.get("tips_original_face_par_added_bn", 0.0)))
    # global
    for v in ("base", "matched"):
        s = sel[v]
        add("ALL", f"{v}_eligible_filings", s["eligible"])
        add("ALL", f"{v}_survivors_before_content_dedup", len(s["chosen"]))
        add("ALL", f"{v}_survivors", len(s["kept"]))
        add("ALL", f"{v}_content_duplicates_removed", len(s["dropped"]))
        add("ALL", f"{v}_content_duplicates_removed_tsy_value_bn", fmt(math.fsum(f.tsy_value for f in s["dropped"]) / 1e9))
        add("ALL", f"{v}_superseded_filings", s["info"]["superseded_filings"])
        add("ALL", f"{v}_stubs_ignored", s["info"]["stubs_ignored"])
        add("ALL", f"{v}_partial_amendments", s["info"]["partial_amendments"])
    add("ALL", "lag_days", LAG_DAYS)
    add("ALL", "windows", "|".join(w.label for w in windows))
    add("ALL", "mspd_union_cusips", len(B["mspd"]))
    add("ALL", "tips_cusips_with_index_ratio", len(B["ratios"]))
    add("ALL", "fixed_curve_date_nominal", B["fixed"][3].isoformat())
    add("ALL", "fixed_curve_date_real", B["fixed"][4].isoformat())
    add("ALL", "d10_fixed", fmt(B["fixed"][2]))
    add("ALL", "alt_curve_date_nominal", B["alt"][3].isoformat())
    add("ALL", "d10_alt", fmt(B["alt"][2]))
    for which, name, _ in expected_cache_files():
        d = B["r1_cache"] if which == "r1" else B["r2_cache"]
        add("ALL", f"cache:{name}", file_sha256(os.path.join(d, name)))
    add("ALL", "file:duration_supply.csv", file_sha256(os.path.join(ROOT, "data", "r2_rates", "duration_supply.csv")))
    add("ALL", "file:tsy_anchors.csv", file_sha256(a.anchors))
    add("ALL", "z1_release_zip_sha256", F["z1_prov"]["zip_sha256"])
    add("ALL", "z1_release", F["z1_prov"]["release"])
    for k in sorted(F["z1_prov"]):
        if k.startswith("file:") and k.endswith(":sha256"):
            add("ALL", "z1_" + k, F["z1_prov"][k])
    for n in ("S124_3_s.csv", "S124_3_t_tu.csv"):
        add("ALL", f"z1_etf_file:{n}:sha256", file_sha256(os.path.join(a.etf_dir, n)))
    add("ALL", "z1_series_used", "; ".join(F["z1_notes"]))
    add("ALL", "unverified_L_anchors", UNVERIFIED_L)
    return rows


# ======================================================================================================== output, main
COLS = {
    "tsy_windows": ["window", "quarter_end", "vintage", "months", "funds_in_window", "funds_m_minus1", "funds_m0", "funds_m_plus1",
                    "funds_with_tsy", "tsy_lines", "tsy_value_bn", "tsy_value_series_bn", "tsy_value_noseries_bn", "tsy_par_bn",
                    "tenyeq_fixed_bn", "tenyeq_fixed_alt_bn", "tenyeq_own_bn", "pardur_fixed_bn_yrs", "dv01_own_mn",
                    "strips_tenyeq_fixed_bn", "short_value_bn", "unpriced_lines", "unpriced_value_bn", "tips_orig_lines",
                    "tips_orig_par_added_bn", "tips_orig_tenyeq_fixed_bn", "z1_mf_bn", "z1_etf_bn",
                    "z1_cef_bn", "z1_sum_bn", "nport_over_z1", "r2_public_10yeq_fixed_bn", "share_of_public_fixed"],
    "tsy_buckets": ["window", "kind", "bucket", "lines", "value_bn", "par_bn", "tenyeq_fixed_bn", "eff_factor",
                    "public_tenyeq_fixed_bn", "share_of_public"],
    "tsy_change": ["variant_id", "arm", "grade", "description", "comparator", "period", "s_start", "s_end", "d_s", "p_start",
                   "p_end", "d_p", "r", "s0", "excess_pp", "excess_bn", "label"],
    "tsy_verdict": ["key", "value"],
    "tsy_dv01_check": ["window", "universe", "n_funds", "n_pos", "n_neg", "n_zero", "median_ratio", "p25_ratio", "p75_ratio",
                       "tsy_value_covered_bn", "tsy_value_bn"],
    "tsy_checks": ["check_id", "scope", "label", "ours", "reference", "threshold", "result", "hard", "note"],
    "tsy_file_stats": ["tag", "key", "value"],
}


def check_sort_key(c):
    m = re.match(r"C(\d+)(.*)", c["check_id"])
    return (int(m.group(1)), m.group(2), c["scope"]) if m else (999, c["check_id"], c["scope"])


def hygiene_check(files):
    """C18 (N12): no output header contains CUSIP, HOLDING_ID or ACCESSION_NUMBER, and no output exceeds 2,000 rows."""
    bad_h = [f"{n}.{c}" for n, (cols, _) in files.items() for c in cols if any(t in c.upper() for t in REFUSE_HEADERS)]
    big = [f"{n} ({len(rows)})" for n, (_, rows) in files.items() if len(rows) > 2000]
    return mk("C18", "outputs", "no output header contains CUSIP, HOLDING_ID or ACCESSION_NUMBER, and no output exceeds 2,000 rows",
              f"{len(bad_h)} bad headers; largest file {max(len(r) for _, r in files.values())} rows", "0 bad headers; <= 2,000 rows", "<= 2,000 rows",
              "FAIL" if bad_h or big else "PASS", True, "; ".join(bad_h + big))


def print_summary(B, F, D, checks, files, out_dir, hard_fail):
    err = lambda *x: print(*x, file=sys.stderr)
    err("\n=== verdict ===")
    for r in F["rows_v"]:
        err(f"  {r['key']:34s} {fmt(r['value'])}")
    err("\n=== checks ===")
    for c in checks:
        err(f"  {c['check_id']:6s} {c['result']:5s} {c['hard']}  {c['scope'][:24]:24s} {str(c['ours'])[:100]}")
    n_fail = sum(1 for c in checks if c["result"] == "FAIL")
    err(f"\nhard FAIL count: {sum(1 for c in checks if c['result'] == 'FAIL' and c['hard'] == 'Y')}; any FAIL: {n_fail}")
    err(f"wrote {len(files)} files to {out_dir}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--zip-dir", default="~/nport")
    ap.add_argument("--r1-cache", default=os.path.join(ROOT, "data", "vintages", "r1_treasury"))
    ap.add_argument("--r2-cache", default=os.path.join(ROOT, "data", "vintages", "r2_treasury"))
    ap.add_argument("--z1-dir", default=os.path.join(ROOT, "data", "vintages", "z1_fund_tsy_20260911"))
    ap.add_argument("--etf-dir", default=os.path.join(ROOT, "data", "vintages", "z1_etf1_2026Q2"))
    ap.add_argument("--anchors", default=os.path.join(ROOT, "data", "nport", "tsy_anchors.csv"))
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "nport"))
    a = ap.parse_args(argv)
    run_preflight()
    B = build(a)
    F = derive_main(B, a)
    B["log"]("tables derived")
    D = derive_funds(B, F, a)
    checks = derive_checks(B, F, D, a)
    rows_d, rows_t, _ = D
    sA, sB = F["order"][0], F["order"][-1]
    top_cols = ["rank_by", "rank", "fund_key", "series_name", "registrant_name", f"s_{sA}", f"s_{sB}", "d_s",
                f"value_{sA}_bn", f"value_{sB}_bn"]
    files = {"tsy_windows": (COLS["tsy_windows"], F["rows_w"]), "tsy_buckets": (COLS["tsy_buckets"], F["rows_b"]),
             "tsy_change": (COLS["tsy_change"], F["rows_c"]), "tsy_verdict": (COLS["tsy_verdict"], F["rows_v"]),
             "tsy_dv01_check": (COLS["tsy_dv01_check"], rows_d), "tsy_top_funds": (top_cols, rows_t),
             "tsy_checks": (COLS["tsy_checks"], checks),
             "tsy_file_stats": (COLS["tsy_file_stats"], build_file_stats(B, F, D, a))}
    checks.append(hygiene_check(files))
    checks.sort(key=check_sort_key)
    hard_fail = any(c["result"] == "FAIL" and c["hard"] == "Y" for c in checks)
    out_dir = os.path.join(a.out, "_FAILED") if hard_fail else a.out
    os.makedirs(out_dir, exist_ok=True)
    for name, (cols, rows) in files.items():
        write_csv(os.path.join(out_dir, name + ".csv"), cols, rows)
    print_summary(B, F, D, checks, files, out_dir, hard_fail)
    B["log"]("done")
    return 2 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main())
