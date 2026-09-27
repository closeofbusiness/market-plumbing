#!/usr/bin/env python3
"""R2 (supply side): a duration-weighted ("10-year-equivalent") measure of US Treasury
marketable debt, split between the Federal Reserve (SOMA) and everyone else ("public"),
at five month-ends. Duration, not face value, is what matters for yields: a $1 bill adds
almost no duration; a $1 30-year bond adds a lot. The supervisor sets this supply against
holders elsewhere in R2.

Method, security by security, at each date:
  - Remaining maturity in years = (maturity date - record date) / 365.25.
  - A market yield, linearly interpolated on the Treasury's par curve (nominal for
    bills/notes/bonds/FRNs; real for TIPS) at that maturity, on the nearest trading day
    on or before the record date. Below the curve's shortest published point or above its
    longest, the nearest endpoint's yield is used (flat extrapolation) -- this matters
    mainly for TIPS, whose real curve starts at 5 years.
  - A clean price and modified duration from the coupon and that yield:
      * Bills: zero-coupon, price = 100/(1+y*T), duration = T/(1+y*T) -- the task's own
        money-market approximation, not the bank-discount/actual-360 convention bills
        actually settle on.
      * Notes/Bonds/TIPS: the standard closed-form semiannual-coupon price and modified
        duration, with a continuous (fractional) number of semiannual periods n = 2T --
        i.e. this ignores the exact coupon calendar and accrued interest (a clean price,
        as instructed). Verified algebraically and numerically against par_mod_duration()
        below: when coupon == yield (a par bond) the two formulas coincide.
        TIPS are priced on the real curve, against the inflation-adjusted current
        principal (MSPD's outstanding_amt for a TIPS CUSIP already has the inflation
        adjustment folded in -- verified below to 8+ significant figures against
        issued_amt + inflation_adj_amt - redeemed_amt; the NY Fed's SOMA parValue does
        NOT, so inflationCompensation is added there).
      * FRNs: duration fixed at 0.02 years (weekly reset) and price fixed at par (100.0)
        -- stated assumptions, not derived from a curve (FRNs have no fixed coupon).
  - Market value = par (inflation-adjusted for TIPS) x price / 100.
  - The 10-year-equivalent of a security = its market value x its modified duration /
    the modified duration of a 10-year PAR bond at that date's 10-year par yield
    (par_mod_duration, the same closed form bin/r1_treasury_decomposition.py uses).
  - SOMA holdings get the identical treatment, security by security, from the NY Fed's
    own coupon/maturity/par fields. There is no CUSIP join between MSPD and SOMA: the two
    totals (and the weighted-average-maturity numerator, par x maturity) are accumulated
    independently and "public" is simply total minus SOMA -- valid because the
    10-year-equivalent and per-security duration are linear in par for a fixed CUSIP.

Universe and exclusions (MSPD Table 3): each row is one issue/reopening tranche of a
CUSIP; Treasury populates outstanding_amt (the CUSIP's current total, already
inflation-adjusted for TIPS) on exactly one tranche row per CUSIP and leaves it null on
the others, so summing it per CUSIP (null -> 0) gives the right total regardless of which
row carries it. Two kinds of rows are excluded from the priced universe:
  - subtotal/grand-total lines: security_class1_desc starting with "Total" (only "Total
    Marketable" is seen in practice) -- identified by having no CUSIP at all.
  - "Federal Financing Bank": a real class, but with no CUSIP, no maturity date and no
    coupon (cannot be priced), and per MSPD Table 1 it is 100% intragovernmental (held by
    government accounts, not the market) -- economically not part of marketable supply
    to anyone. Any other unmapped class would land here too, logged and reported.
Excluded par is reported in checks.csv as the (small, explained) gap against MSPD Table 1.

Inputs (not redistributed; fetched into data/vintages/r2_treasury/ if missing, ignored by
git):
  - Treasury MSPD Table 3 (security-level marketable debt) and Table 1 (summary totals),
    api.fiscaldata.treasury.gov, one JSON file per table per record date.
  - NY Fed SOMA Treasury holdings, security-level, weekly (Wednesdays): the as-of-dates
    list, and one holdings JSON per as-of date actually used.
  - The Treasury's daily nominal and real par yield curves: read from
    data/vintages/r1_treasury/ (already fetched there by bin/r1_treasury_decomposition.py
    for R1); fetched here too, the same way, if a year's file is missing.
  - For one secondary check only (not part of the pipeline's core inputs): the Fed
    Board's own H.4.1 archive, data/a1_money_creation/FRB_h41.zip, already present
    locally from an unrelated task. Read best-effort, via a bounded text scan (not fetched
    by this script, and skipped with a note if absent).
Outputs: data/r2_rates/duration_supply.csv, duration_supply_changes.csv, checks.csv.
Requires: Python 3 stdlib only. Run from anywhere:
  python3 bin/r2_duration_supply.py
"""
import csv, datetime as dt, json, os, re, time, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "vintages", "r2_treasury")
R1RAW = os.path.join(ROOT, "data", "vintages", "r1_treasury")
OUT = os.path.join(ROOT, "data", "r2_rates")
SERIES_TSV = os.path.join(ROOT, "data", "series.tsv")
H41_ZIP = os.path.join(ROOT, "data", "a1_money_creation", "FRB_h41.zip")
UA = {"User-Agent": "Mozilla/5.0 (research; free public data)"}

DATES = ["2023-12-31", "2024-12-31", "2025-12-31", "2026-06-30", "2026-08-31"]
BILLS_CHECK_DATE = "2026-07-31"          # check 3 only; not one of the 5 report dates
FIXED_CURVE_DATE = "2023-12-31"          # "fixed-curve" 10y-eq: every date priced on this one curve, so the change is quantity only

FISCAL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/debt/mspd/"
MSPD3 = FISCAL + "mspd_table_3_market?filter=record_date:eq:{d}&page%5Bsize%5D=10000"
MSPD1 = FISCAL + "mspd_table_1?filter=record_date:eq:{d}&page%5Bsize%5D=200"
SOMA_DATES_URL = "https://markets.newyorkfed.org/api/soma/asofdates/list.json"
SOMA_HOLDINGS = "https://markets.newyorkfed.org/api/soma/tsy/get/asof/{d}.json"

YEARS = [2023, 2024, 2025, 2026]
TSY = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/"
       "{y}/all?type={t}&field_tdr_date_value={y}&page&_format=csv")

# MSPD security_class1_desc -> our bucket. Anything else is excluded (see docstring).
CLASS_MAP = {"Bills Maturity Value": "bills", "Notes": "coupons", "Bonds": "coupons",
             "Inflation-Protected Securities": "tips", "Floating Rate Notes": "frn"}
# NY Fed SOMA securityType -> the same buckets.
SOMA_KIND = {"Bills": "bills", "NotesBonds": "coupons", "TIPS": "tips", "FRNs": "frn"}

NOM_MATURITIES = {"1 Mo": 1 / 12, "1.5 Month": 1.5 / 12, "2 Mo": 2 / 12, "3 Mo": 3 / 12,
                  "4 Mo": 4 / 12, "6 Mo": 6 / 12, "1 Yr": 1.0, "2 Yr": 2.0, "3 Yr": 3.0,
                  "5 Yr": 5.0, "7 Yr": 7.0, "10 Yr": 10.0, "20 Yr": 20.0, "30 Yr": 30.0}
REAL_MATURITIES = {"5 YR": 5.0, "7 YR": 7.0, "10 YR": 10.0, "20 YR": 20.0, "30 YR": 30.0}

# H.4.1 series RESPPALGUM_N.WW = "Assets: Securities Held Outright: U.S. Treasury
# securities: All: Wednesday level" (CATEGORY=ASSET SUBCATEGORY=ORH COMPONENT=USTS
# DISTRIBUTION=TOT SERIESTYPE=L, UNIT_MULT=1,000,000) -- used only for check 2.
H41_SERIES = "RESPPALGUM_N.WW"


def fetch(url, path):
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    req = urllib.request.Request(url, headers=UA)
    for attempt in (1, 2):
        try:
            data = urllib.request.urlopen(req, timeout=120).read()
            break
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(3)
    open(path, "wb").write(data)


def num(v):
    # '*' is Treasury's own marker for "rounds to zero" (seen on exactly one line per
    # date, "Total Matured Treasury Bills" -- old bills past maturity with a few dollars
    # still unpresented for redemption; below its rounding threshold). Treated as 0.0.
    if v in (None, "", "null"):
        return None
    return 0.0 if v == "*" else float(v)


def on_or_before(seq, d):
    ks = [k for k in seq if k <= d]
    return max(ks) if ks else None


def par_mod_duration(y_pct, n=10):
    """Modified duration of a par bond (coupon == yield), standard semiannual formula --
    identical to bin/r1_treasury_decomposition.py's helper of the same name."""
    y = y_pct / 100.0
    return (1.0 / y) * (1.0 - 1.0 / (1.0 + y / 2.0) ** (2 * n))


def interp_curve(curve, T):
    """Linear interpolation of a {maturity_years: yield_pct} curve at T; flat
    extrapolation past the shortest/longest published point."""
    pts = sorted(curve.items())
    if T <= pts[0][0]:
        return pts[0][1]
    if T >= pts[-1][0]:
        return pts[-1][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= T <= x1:
            return y0 if x1 == x0 else y0 + (T - x0) / (x1 - x0) * (y1 - y0)
    return pts[-1][1]  # unreachable


def bill_price_duration(yield_pct, T):
    """Zero-coupon money-market approximation: price = 100/(1+y*T),
    duration = T/(1+y*T) (the task's specified formula, not the bank-discount/BEY
    convention bills actually settle on)."""
    y = yield_pct / 100.0
    return 100.0 / (1.0 + y * T), T / (1.0 + y * T)


def coupon_price_duration(coupon_pct, yield_pct, T):
    """Standard semiannual-coupon closed-form clean price and modified duration, with a
    continuous number of semiannual periods n = 2T (ignores the exact coupon calendar/
    stub and accrued interest, as instructed). Derivation check: at coupon == yield
    (a par bond) this reduces algebraically to par_mod_duration(yield_pct, n=T) -- see
    the assertions in _selftest() below, run once at import time."""
    c, y = coupon_pct / 100.0, yield_pct / 100.0
    n = 2.0 * T
    i = y / 2.0
    if abs(i) < 1e-9:
        i = 1e-9 if i >= 0 else -1e-9
    g = c / 2.0
    df_n = (1.0 + i) ** (-n)
    price = 100.0 * g * (1.0 - df_n) / i + 100.0 * df_n
    denom = g * ((1.0 + i) ** n - 1.0) + i
    if abs(denom) < 1e-12:
        denom = 1e-12
    mac_periods = (1.0 + i) / i - ((1.0 + i) + n * (g - i)) / denom
    mod_duration = (mac_periods / 2.0) / (1.0 + i)
    return price, mod_duration


def _selftest():
    for c, y, T in ((3.0, 3.0, 10.0), (0.5, 4.2, 7.0), (7.5, 4.5, 2.0), (2.0, 2.0, 0.25)):
        if abs(c - y) < 1e-9:
            price, dur = coupon_price_duration(c, y, T)
            assert abs(price - 100.0) < 1e-6, (c, y, T, price)
            assert abs(dur - par_mod_duration(y, n=T)) < 1e-9, (c, y, T, dur, par_mod_duration(y, n=T))
    p0, d0 = bill_price_duration(5.0, 0.25)
    assert abs(p0 - 100.0 / 1.0125) < 1e-9 and abs(d0 - 0.25 / 1.0125) < 1e-9


_selftest()


def load_curve(kind):
    """kind: 'daily_treasury_yield_curve' (nominal) or 'daily_treasury_real_yield_curve'
    (real). Same source and on-disk cache as bin/r1_treasury_decomposition.py; fetched
    here too if a year's file is missing."""
    out = {}
    for y in YEARS:
        p = os.path.join(R1RAW, f"{kind}_{y}.csv")
        if not os.path.exists(p):
            fetch(TSY.format(y=y, t=kind), p)
        for r in csv.DictReader(open(p, encoding="utf-8-sig")):
            d = dt.datetime.strptime(r["Date"], "%m/%d/%Y").date()
            out[d] = {k.strip(): (float(v) if v not in ("", "N/A") else None) for k, v in r.items() if k != "Date"}
    return out


def curve_points(row, mapping):
    return {mapping[k]: v for k, v in row.items() if k in mapping and v is not None}


def load_mspd_table3(record_date):
    """All rows for one record_date, paginated defensively (every date seen so far is
    under 1,200 rows, well inside one page[size]=10000 call, but this does not assume it)."""
    rows, page, total = [], 1, None
    while True:
        path = os.path.join(RAW, f"mspd_table3_{record_date}_p{page}.json")
        fetch(MSPD3.format(d=record_date) + f"&page%5Bnumber%5D={page}", path)
        d = json.load(open(path, encoding="utf-8"))
        rows += d["data"]
        total = int(d["meta"]["total-count"])
        if len(rows) >= total or not d["data"]:
            break
        page += 1
    return rows, total


def load_mspd_table1(record_date):
    path = os.path.join(RAW, f"mspd_table1_{record_date}.json")
    fetch(MSPD1.format(d=record_date), path)
    return json.load(open(path, encoding="utf-8"))["data"]


def table1_totals(t1_rows):
    bills = next(r for r in t1_rows if r["security_type_desc"] == "Marketable" and r["security_class_desc"] == "Bills")
    total = next(r for r in t1_rows if r["security_type_desc"] == "Total Marketable")
    return float(bills["total_mil_amt"]) / 1000.0, float(total["total_mil_amt"]) / 1000.0


def cusips_from_table3(rows, record_date):
    """Group MSPD table-3 tranche rows into one record per CUSIP per bucket (par summed,
    null -> 0; coupon/maturity taken from whichever tranche states them -- identical
    across a CUSIP's tranches since it is the same bond). Returns (buckets, excluded,
    class_totals, table3_total_bn) -- see module docstring for what is excluded and why.

    Beyond the top-level "Total Marketable" grand-total line, Table 3 also carries, once
    per class, three MORE subtotal rows with a text label in security_class2_desc instead
    of a CUSIP: "Total Unmatured Treasury {Notes,Bonds,Bills}" (== the sum of that class's
    individual CUSIP rows -- checked, matches to the dollar -- so dropped as pure
    redundancy), "Total Treasury {class}" (the class grand total, == MSPD Table 1's figure
    for that class -- kept in class_totals for a per-class check, not added to par), and
    "Total Matured Treasury {class}" -- which is NOT redundant: it is real principal that
    has passed its maturity date but has not yet been presented for redemption (no CUSIP,
    no forward maturity date to price against). At 2023-12-31 this is $0.03-0.14bn for
    bills/bonds but $136.4bn for notes -- material enough to move the total-marketable
    check outside 0.5% if simply dropped. Economically this is already-due principal, so
    it is folded into the matching bucket as a synthetic entry priced at par with the
    record date as its own "maturity" (T=0 -> price 100, duration 0 through the same
    formulas used for a security actually maturing that day -- no special-cased pricing
    needed). "Federal Financing Bank" (no CUSIP, no maturity, no class-3 breakdown at all)
    remains excluded outright, as does any other class this script does not recognise."""
    buckets = {"bills": {}, "coupons": {}, "tips": {}, "frn": {}}
    excluded, class_totals, table3_total_mm = {}, {}, None
    for r in rows:
        cls = r["security_class1_desc"]
        oa = num(r["outstanding_amt"]) or 0.0
        if cls.startswith("Total"):
            table3_total_mm = oa
            continue
        cusip, mat = r["security_class2_desc"], r["maturity_date"]
        bucket = CLASS_MAP.get(cls)
        if bucket is not None and cusip.startswith("Total "):
            if cusip.startswith("Total Matured Treasury "):
                rec = buckets[bucket].setdefault("__MATURED__", {"coupon": 0.0, "maturity": record_date, "par": 0.0})
                rec["par"] += oa
            elif cusip.startswith("Total Treasury "):
                class_totals[cls] = oa / 1000.0
            # "Total Unmatured Treasury {class}" is dropped here: it duplicates the sum
            # of the individual CUSIP rows accumulated below.
            continue
        if bucket is None or cusip in (None, "null") or mat in (None, "null"):
            excluded[cls] = excluded.get(cls, 0.0) + oa
            continue
        rec = buckets[bucket].setdefault(cusip, {"coupon": None, "maturity": mat, "par": 0.0})
        rec["par"] += oa
        cp = num(r["interest_rate_pct"])
        if cp is not None:
            rec["coupon"] = cp
    return buckets, excluded, class_totals, (table3_total_mm / 1000.0 if table3_total_mm is not None else None)


def load_soma_dates():
    path = os.path.join(RAW, "soma_asofdates_list.json")
    fetch(SOMA_DATES_URL, path)
    d = json.load(open(path, encoding="utf-8"))
    return sorted(dt.date.fromisoformat(x) for x in d["soma"]["asOfDates"])


def load_soma_holdings(as_of_iso):
    path = os.path.join(RAW, f"soma_tsy_{as_of_iso}.json")
    fetch(SOMA_HOLDINGS.format(d=as_of_iso), path)
    return json.load(open(path, encoding="utf-8"))["soma"]["holdings"]


def soma_securities(holdings, as_of_date):
    """SOMA holdings JSON -> {bucket: [(par_bn, coupon_pct_or_None, years_to_maturity), ...]}.
    parValue is raw dollars and, for TIPS, is the ORIGINAL (non-inflation-adjusted) face;
    inflationCompensation (also raw dollars) is added to get the current adjusted
    principal -- verified against the Fed's own H.4.1 total (see checks.csv, check 2)."""
    by_kind = {"bills": [], "coupons": [], "tips": [], "frn": []}
    unmapped = {}
    for h in holdings:
        kind = SOMA_KIND.get(h["securityType"])
        par_bn = float(h["parValue"]) / 1e9
        if kind is None:
            unmapped[h["securityType"]] = unmapped.get(h["securityType"], 0.0) + par_bn
            continue
        if kind == "tips" and h.get("inflationCompensation") not in (None, ""):
            par_bn += float(h["inflationCompensation"]) / 1e9
        coupon = num(h.get("coupon"))
        T = max((dt.date.fromisoformat(h["maturityDate"]) - as_of_date).days / 365.25, 0.0)
        by_kind[kind].append((par_bn, coupon, T))
    return by_kind, unmapped


def price_one(kind, coupon_pct, T, nom_curve, real_curve):
    if kind == "bills":
        return bill_price_duration(interp_curve(nom_curve, T), T)
    if kind == "coupons":
        return coupon_price_duration(coupon_pct or 0.0, interp_curve(nom_curve, T), T)
    if kind == "tips":
        return coupon_price_duration(coupon_pct or 0.0, interp_curve(real_curve, T), T)
    if kind == "frn":
        return 100.0, 0.02          # stated assumption: weekly reset, priced at par
    raise ValueError(kind)


def aggregate(securities, kind, nom_curve, real_curve, d10):
    """securities: [(par_bn, coupon_pct_or_None, years_to_maturity), ...].
    Returns (par_bn, mv_bn, tenyeq_bn, par_years_bn) -- the last is the numerator
    (par x maturity) for a par-weighted average maturity."""
    par_t = mv_t = eq10_t = pty_t = 0.0
    for par_bn, coupon, T in securities:
        price, dur = price_one(kind, coupon, T, nom_curve, real_curve)
        mv = par_bn * price / 100.0
        par_t += par_bn; mv_t += mv; eq10_t += mv * dur / d10; pty_t += par_bn * T
    return par_t, mv_t, eq10_t, pty_t


def load_series_tsv_latest(key):
    """Latest (last-in-file) row of data/series.tsv for series_key == key; series.tsv is
    append-only, so the last occurrence is the latest vintage (the same convention
    bin/check.sh uses)."""
    if not os.path.exists(SERIES_TSV):
        return None
    rows = [r for r in csv.DictReader(open(SERIES_TSV, encoding="utf-8"), delimiter="\t") if r["series_key"] == key]
    return rows[-1] if rows else None


def h41_soma_treasury_obs(wanted_isodates):
    """Best-effort, bounded text scan of the Fed Board's own H.4.1 archive (already on
    disk locally at H41_ZIP for an unrelated task; NOT fetched by this script) for the
    dates in wanted_isodates, series H41_SERIES only. Returns {iso_date: value_bn}; {} if
    the archive is not present. A full XML parse of a 126MB file is not needed: this
    scans lines until it finds the one series' block (identified by SERIES_NAME) and
    stops at the following <kf:Series line, so a document = 4552.337 mm figure for
    2026-09-09 could be checked here for internal consistency with data/series.tsv."""
    if not os.path.exists(H41_ZIP):
        return {}
    import zipfile
    wanted = set(wanted_isodates)
    out, in_series = {}, False
    with zipfile.ZipFile(H41_ZIP) as z, z.open("H41_data.xml") as f:
        for line_bytes in f:
            line = line_bytes.decode("utf-8", "ignore")
            if f'SERIES_NAME="{H41_SERIES}"' in line:
                in_series = True
                continue
            if not in_series:
                continue
            if "<kf:Series " in line:
                break
            m = re.search(r'OBS_VALUE="([\d.]+)"\s+TIME_PERIOD="([\d-]+)"', line)
            if m and m.group(2) in wanted:
                out[m.group(2)] = float(m.group(1)) / 1000.0   # $mm -> $bn
    return out


def mk_check(check_id, date, label, ours, ref, threshold_pct, note):
    diff = ours - ref
    diffp = (diff / ref * 100.0) if ref else float("nan")
    result = "PASS" if abs(diffp) <= threshold_pct else "FAIL"
    return {"check_id": check_id, "date": date, "label": label, "ours": round(ours, 2),
             "reference": round(ref, 2), "diff": round(diff, 2), "diff_pct": round(diffp, 4),
             "threshold_pct": threshold_pct, "result": result, "note": note}


def compute_date(record_date, nom_all, real_all, soma_all_dates, fixed=None):
    rd = dt.date.fromisoformat(record_date)
    t3_rows, _ = load_mspd_table3(record_date)
    buckets, excluded, class_totals, table3_total_bn = cusips_from_table3(t3_rows, record_date)
    bills_t1_bn, total_t1_bn = table1_totals(load_mspd_table1(record_date))

    curve_date_nom = on_or_before(nom_all, rd)
    curve_date_real = on_or_before(real_all, rd)
    nom_row, real_row = nom_all[curve_date_nom], real_all[curve_date_real]
    nom_curve, real_curve = curve_points(nom_row, NOM_MATURITIES), curve_points(real_row, REAL_MATURITIES)
    y10 = nom_row["10 Yr"]
    d10 = par_mod_duration(y10, n=10)

    def securities_for(bucket):
        return [(rec["par"] / 1000.0, rec["coupon"], max((dt.date.fromisoformat(rec["maturity"]) - rd).days / 365.25, 0.0))
                for rec in bucket.values()]

    par_bn, mv_bn, eq10_bn, pty_bn = {}, {}, {}, {}
    for kind in ("bills", "coupons", "tips", "frn"):
        par_bn[kind], mv_bn[kind], eq10_bn[kind], pty_bn[kind] = aggregate(
            securities_for(buckets[kind]), kind, nom_curve, real_curve, d10)
    total_par, total_mv, total_eq10, total_pty = (sum(x.values()) for x in (par_bn, mv_bn, eq10_bn, pty_bn))
    wam_total = total_pty / total_par

    soma_asof = on_or_before(soma_all_dates, rd)
    soma_by_kind, soma_unmapped = soma_securities(load_soma_holdings(soma_asof.isoformat()), soma_asof)
    s_par, s_mv, s_eq10, s_pty = {}, {}, {}, {}
    for kind in ("bills", "coupons", "tips", "frn"):
        s_par[kind], s_mv[kind], s_eq10[kind], s_pty[kind] = aggregate(
            soma_by_kind[kind], kind, nom_curve, real_curve, d10)
    soma_par, soma_eq10, soma_pty = sum(s_par.values()), sum(s_eq10.values()), sum(s_pty.values())

    public_par, public_eq10 = total_par - soma_par, total_eq10 - soma_eq10
    # Quantity-only measure: the same securities (with today's remaining maturities, so ageing counts) priced on
    # the FIXED_CURVE_DATE curve. Changes in it exclude the valuation effect of yield moves.
    f_nom, f_real, f_d10 = fixed
    kinds = ("bills", "coupons", "tips", "frn")
    fx_total = sum(aggregate(securities_for(buckets[k]), k, f_nom, f_real, f_d10)[2] for k in kinds)
    fx_soma = sum(aggregate(soma_by_kind[k], k, f_nom, f_real, f_d10)[2] for k in kinds)
    wam_public = (total_pty - soma_pty) / public_par

    row = {"record_date": record_date, "soma_asof": soma_asof.isoformat(),
           "total_par_bn": round(total_par, 1), "bills_par_bn": round(par_bn["bills"], 1),
           "notes_bonds_par_bn": round(par_bn["coupons"], 1), "tips_par_bn": round(par_bn["tips"], 1),
           "frn_par_bn": round(par_bn["frn"], 1), "total_mv_bn": round(total_mv, 1),
           "total_10yeq_bn": round(total_eq10, 1), "bills_10yeq_bn": round(eq10_bn["bills"], 1),
           "coupons_10yeq_bn": round(eq10_bn["coupons"], 1), "tips_10yeq_bn": round(eq10_bn["tips"], 1),
           "soma_par_bn": round(soma_par, 1), "soma_10yeq_bn": round(soma_eq10, 1),
           "public_par_bn": round(public_par, 1), "public_10yeq_bn": round(public_eq10, 1),
           "wam_total_years": round(wam_total, 2), "wam_public_years": round(wam_public, 2),
           "d10_par_duration": round(d10, 3), "total_10yeq_fixed_bn": round(fx_total, 1),
           "soma_10yeq_fixed_bn": round(fx_soma, 1), "public_10yeq_fixed_bn": round(fx_total - fx_soma, 1)}
    ctx = {"table3_total_bn": table3_total_bn, "excluded": excluded, "class_totals": class_totals,
           "our_total_par_bn": total_par, "our_bills_par_bn": par_bn["bills"], "our_par_bn": par_bn,
           "table1_total_bn": total_t1_bn, "table1_bills_bn": bills_t1_bn,
           "soma_asof": soma_asof, "soma_par_bn": soma_par, "soma_unmapped": soma_unmapped,
           "frn_10yeq_bn": eq10_bn["frn"]}
    return row, ctx


def check1_table1(context):
    out = []
    for d in DATES:
        c = context[d]
        ffb_bn = c["excluded"].get("Federal Financing Bank", 0.0) / 1000.0
        other = {k: v / 1000.0 for k, v in c["excluded"].items() if k != "Federal Financing Bank"}
        out.append(mk_check("1_total_marketable_vs_table1", d,
                             "our total marketable par (bills+notes/bonds+tips+frn) vs MSPD Table 1 total marketable ($bn)",
                             c["our_total_par_bn"], c["table1_total_bn"], 0.5,
                             f"ours excludes Federal Financing Bank (${ffb_bn:.2f}bn: no CUSIP/maturity, 100% intragovernmental "
                             f"per MSPD Table 1, not priceable or part of market supply)" + (f" and other unmapped classes {other}" if other else "")))
        out.append(mk_check("1_bills_vs_table1", d, "our bills par vs MSPD Table 1 bills ($bn)",
                             c["our_bills_par_bn"], c["table1_bills_bn"], 0.5, ""))
    return out


def check0_table3_internal(context):
    """Bonus, not one of the four requested checks: our per-CUSIP sum (priced total,
    which now includes the "Total Matured Treasury {class}" balances folded in at par/
    zero duration -- see cusips_from_table3 -- plus the separately-excluded classes such
    as Federal Financing Bank) against MSPD Table 3's own 'Total Marketable' subtotal
    line -- validates the CUSIP grouping/summation logic against the table's own
    arithmetic, independent of Table 1."""
    out = []
    for d in DATES:
        c = context[d]
        ours = c["our_total_par_bn"] + sum(c["excluded"].values()) / 1000.0
        out.append(mk_check("0_table3_self_consistency_bonus", d,
                             "(our priced total, incl. matured-but-unpresented balances + our excluded) vs MSPD "
                             "Table 3's own Total Marketable subtotal line ($bn)",
                             ours, c["table3_total_bn"], 0.01, "bonus check, not one of the four requested"))
        ct, op = c["class_totals"], c["our_par_bn"]
        per_class = [("Bills Maturity Value", op["bills"]), ("Inflation-Protected Securities", op["tips"]),
                     ("Floating Rate Notes", op["frn"])]
        if "Notes" in ct and "Bonds" in ct:
            out.append(mk_check("0b_per_class_self_consistency_bonus", d,
                                 "our notes+bonds par vs MSPD Table 3's own per-class grand-total lines for Notes and Bonds, summed ($bn)",
                                 op["coupons"], ct["Notes"] + ct["Bonds"], 0.01, "bonus check, not one of the four requested"))
        for cls, ours_cls in per_class:
            if cls in ct:
                out.append(mk_check("0b_per_class_self_consistency_bonus", d,
                                     f"our {cls} par vs MSPD Table 3's own per-class grand-total line for that class ($bn)",
                                     ours_cls, ct[cls], 0.01, "bonus check, not one of the four requested"))
    return out


def bracketing_wednesdays(d):
    """The nearest Wednesday on or before, and on or after, date d (d itself if it is
    already a Wednesday). H.4.1 only reports Wednesday levels, so a SOMA as-of date that
    falls on some other day of the week (seen once: 2024-12-31, a Tuesday) needs its
    actual bracketing Wednesdays, not a blind +/-7 days -- which for a Tuesday would land
    on two other Tuesdays, 6 and 1 days short of the true brackets respectively."""
    before = d - dt.timedelta(days=(d.weekday() - 2) % 7)
    after = d + dt.timedelta(days=(2 - d.weekday()) % 7)
    return before, after


def check2_soma(context):
    out = []
    asofs = {d: context[d]["soma_asof"] for d in DATES}
    wanted = set()
    for asof in asofs.values():
        before, after = bracketing_wednesdays(asof)
        wanted |= {asof.isoformat(), before.isoformat(), after.isoformat()}
    h41 = h41_soma_treasury_obs(wanted)
    for d in DATES:
        asof, ours = asofs[d], context[d]["soma_par_bn"]
        key = asof.isoformat()
        if not h41:
            out.append({"check_id": "2_soma_vs_h41", "date": d,
                         "label": "our SOMA Treasury par vs Fed H.4.1 (RESPPALGUM_N.WW)",
                         "ours": round(ours, 2), "reference": "", "diff": "", "diff_pct": "",
                         "threshold_pct": 1.0, "result": "N/A",
                         "note": "data/a1_money_creation/FRB_h41.zip not found locally; check skipped"})
        elif key in h41:
            out.append(mk_check("2_soma_vs_h41", d,
                                 f"our SOMA Treasury par ({key}) vs Fed H.4.1 'Securities Held Outright: "
                                 f"U.S. Treasury securities: All: Wednesday level' ($bn), exact-date match",
                                 ours, h41[key], 1.0, "data/a1_money_creation/FRB_h41.zip, series RESPPALGUM_N.WW"))
        else:
            before, after = bracketing_wednesdays(asof)
            bk, ak = before.isoformat(), after.isoformat()
            if bk in h41 and ak in h41:
                span = (dt.date.fromisoformat(ak) - dt.date.fromisoformat(bk)).days
                frac = (asof - dt.date.fromisoformat(bk)).days / span
                ref = h41[bk] + frac * (h41[ak] - h41[bk])
                out.append(mk_check("2_soma_vs_h41_interpolated", d,
                                     f"our SOMA Treasury par ({key}, not a Wednesday -- H.4.1 has none) vs H.4.1 linearly "
                                     f"day-count interpolated between {bk} (${h41[bk]:.1f}bn) and {ak} (${h41[ak]:.1f}bn)",
                                     ours, ref, 1.0,
                                     "data/a1_money_creation/FRB_h41.zip, series RESPPALGUM_N.WW; interpolated reference, not a direct observation"))
            else:
                out.append({"check_id": "2_soma_vs_h41", "date": d,
                             "label": "our SOMA Treasury par vs Fed H.4.1 (RESPPALGUM_N.WW)",
                             "ours": round(ours, 2), "reference": "", "diff": "", "diff_pct": "",
                             "threshold_pct": 1.0, "result": "N/A",
                             "note": f"no H.4.1 observation for {key} or its bracketing Wednesdays {bk}/{ak}"})
    srow = load_series_tsv_latest("soma_treasuries_held_outright_bn")
    if srow:
        s_asof = dt.date.fromisoformat(srow["as_of"])
        nearest_d = min(DATES, key=lambda d: abs((asofs[d] - s_asof).days))
        gap = (s_asof - asofs[nearest_d]).days
        out.append(mk_check("2_soma_vs_series_tsv_bonus", nearest_d,
                             f"our SOMA Treasury par ({asofs[nearest_d].isoformat()}) vs data/series.tsv "
                             f"soma_treasuries_held_outright_bn (as_of {srow['as_of']}, {gap:+d}d gap)",
                             context[nearest_d]["soma_par_bn"], float(srow["value"]), 1.0,
                             "secondary corroboration only (dates do not match exactly); source=" + srow["source"]))
    return out


def check3_bills_july(context):
    rows, _ = load_mspd_table3(BILLS_CHECK_DATE)
    buckets, _, _, _ = cusips_from_table3(rows, BILLS_CHECK_DATE)
    bills_par_bn = sum(rec["par"] for rec in buckets["bills"].values()) / 1000.0
    srow = load_series_tsv_latest("bills_outstanding_total_bn")
    ref = float(srow["value"]) if srow else 6988.9
    note = f"series.tsv as_of={srow['as_of']}, source={srow['source']}" if srow else "series.tsv row not found; used the value given in the brief (6988.9)"
    return [mk_check("3_bills_20260731_vs_series_tsv", BILLS_CHECK_DATE,
                      "our bills par at 2026-07-31 (computed only for this check) vs data/series.tsv bills_outstanding_total_bn ($bn)",
                      bills_par_bn, ref, 0.5, note)]


def check4_sanity(results):
    out = []
    for d in DATES:
        r = results[d]
        ok = 7.0 <= r["d10_par_duration"] <= 8.5
        out.append({"check_id": "4_d10_sanity", "date": d, "label": "10-year par duration in [7, 8.5] years",
                     "ours": r["d10_par_duration"], "reference": "[7, 8.5]", "diff": "", "diff_pct": "",
                     "threshold_pct": "", "result": "PASS" if ok else "FAIL", "note": ""})
        ratio = (r["bills_10yeq_bn"] / r["bills_par_bn"] * 100.0) if r["bills_par_bn"] else float("nan")
        out.append({"check_id": "4_bills_10yeq_sanity", "date": d,
                     "label": "bills' 10-year-equivalents as a % of their par, must be under 5%",
                     "ours": round(ratio, 3), "reference": "<5%", "diff": "", "diff_pct": "",
                     "threshold_pct": 5.0, "result": "PASS" if ratio < 5.0 else "FAIL", "note": ""})
    return out


def main():
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    nom_all = load_curve("daily_treasury_yield_curve")
    real_all = load_curve("daily_treasury_real_yield_curve")
    soma_all_dates = load_soma_dates()
    fd = dt.date.fromisoformat(FIXED_CURVE_DATE)
    f_nom_row, f_real_row = nom_all[on_or_before(nom_all, fd)], real_all[on_or_before(real_all, fd)]
    fixed = (curve_points(f_nom_row, NOM_MATURITIES), curve_points(f_real_row, REAL_MATURITIES),
             par_mod_duration(f_nom_row["10 Yr"], n=10))

    results, context = {}, {}
    for record_date in DATES:
        results[record_date], context[record_date] = compute_date(record_date, nom_all, real_all, soma_all_dates, fixed)

    fieldnames = ["record_date", "soma_asof", "total_par_bn", "bills_par_bn", "notes_bonds_par_bn", "tips_par_bn",
                  "frn_par_bn", "total_mv_bn", "total_10yeq_bn", "bills_10yeq_bn", "coupons_10yeq_bn", "tips_10yeq_bn",
                  "soma_par_bn", "soma_10yeq_bn", "public_par_bn", "public_10yeq_bn", "wam_total_years",
                  "wam_public_years", "d10_par_duration", "total_10yeq_fixed_bn", "soma_10yeq_fixed_bn",
                  "public_10yeq_fixed_bn"]
    with open(os.path.join(OUT, "duration_supply.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames); w.writeheader()
        for d in DATES:
            w.writerow(results[d])

    periods = [("2024", "2023-12-31", "2024-12-31"), ("2025", "2024-12-31", "2025-12-31"),
               ("2026 to 30 Jun", "2025-12-31", "2026-06-30"), ("30 Jun to 31 Aug", "2026-06-30", "2026-08-31"),
               ("2023-12-31 to 2026-08-31", "2023-12-31", "2026-08-31")]
    chg = []
    for name, a, b in periods:
        A, B = results[a], results[b]
        d = lambda col: round(B[col] - A[col], 1)
        chg.append({"period": name, "from": a, "to": b, "d_total_par_bn": d("total_par_bn"),
                    "d_total_10yeq_bn": d("total_10yeq_bn"), "d_public_par_bn": d("public_par_bn"),
                    "d_public_10yeq_bn": d("public_10yeq_bn"), "d_soma_par_bn": d("soma_par_bn"),
                    "d_soma_10yeq_bn": d("soma_10yeq_bn"), "d_total_10yeq_fixed_bn": d("total_10yeq_fixed_bn"),
                    "d_public_10yeq_fixed_bn": d("public_10yeq_fixed_bn"), "d_soma_10yeq_fixed_bn": d("soma_10yeq_fixed_bn")})
    with open(os.path.join(OUT, "duration_supply_changes.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(chg[0])); w.writeheader(); w.writerows(chg)

    checks = (check0_table3_internal(context) + check1_table1(context) + check2_soma(context)
              + check3_bills_july(context) + check4_sanity(results))
    with open(os.path.join(OUT, "checks.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(checks[0])); w.writeheader(); w.writerows(checks)

    fails = [c for c in checks if c["result"] == "FAIL"]
    print(f"[done] wrote duration_supply.csv, duration_supply_changes.csv, checks.csv "
          f"({len(checks)} checks, {len(fails)} FAIL) for {DATES}")


if __name__ == "__main__":
    main()
