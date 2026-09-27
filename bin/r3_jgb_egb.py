#!/usr/bin/env python3
"""R3: what moved Japanese and euro-area government bond yields, end-2023 to latest, and who bought.

The two questions R1 and R2 asked of US Treasuries, asked of JGBs and euro-area government bonds.

JAPAN
  1. Prices. The Ministry of Finance's daily JGB yields at constant maturity (semiannual compound, 1-40 years; the
     Ministry's Q&A): the 10-year, the 2-year and the slope. Breakeven inflation at matched maturity, on the Ministry's own
     method (its bei.pdf chart): the newest 10-year inflation-indexed JGB (JGBi) against the nominal curve at the same
     remaining maturity. The JGBi real yield is computed here, semiannual compound, from the JSDA's daily reference price
     (clean, per 100 of indexed principal) and the coupon in the Ministry's auction history; the deflation floor on
     principal is ignored. Real 10-year = nominal 10-year minus that breakeven, a maturity mismatch of about half a year.
  2. A holder's return on a constant-maturity 10-year JGB, fully revalued month by month as in R1, against the 1-year
     yield as the cash leg (the Ministry's curve starts at one year).
  3. Who bought. The Bank of Japan's Flow of Funds: quarterly transactions in central government securities and FILP bonds
     (instrument 311; Treasury discount bills are excluded), by holding sector. Transactions exclude price changes, like
     the Z.1 flows in R2. The sector rows partition the total. The script asserts the identities every quarter and stops if
     one fails, because nested sectors added twice is how the N2c table went wrong (C-124). Securities investment trusts
     sit beside "other financial intermediaries", not inside it; public pensions sit inside general government.

EURO AREA (the German Bund as the benchmark)
  4. Prices. The Bundesbank's daily Svensson yields for listed Federal securities (10-year, 2-year, 1-year, 9-year) and the
     ECB's euro-area AAA and all-issuer curves; monthly 10-year convergence yields for Italy, France and Germany (spreads).
     No free market breakeven exists for Bunds, so the real part is survey-based: the Bundesbank's expected real rate (the
     average 10-year Bund yield minus Consensus inflation forecasts). The implied survey inflation expectation is the
     month's average Svensson 10-year minus that rate, a close stand-in for the average yield the Bundesbank uses. The ECB
     Survey of Professional Forecasters' long-term inflation expectation is shown beside it.
  5. A holder's return on a constant-maturity 10-year Bund, fully revalued month by month, against the 1-year yield.
  6. Who holds. The ECB's Securities Holdings Statistics by Sector: euro-area residents' holdings of euro-area government
     debt securities at face value, summed over the 20 countries that were members for the whole window (Bulgaria, a member
     from 2026, is left out: EUR 26bn). The rest of the world is total outstanding (the ECB's CSEC, nominal value, all
     currencies) minus all euro-area holders. The sector rows partition the holders; the identities are checked every
     quarter ("other financial institutions" contains the investment funds, so it enters net of them). Holdings are
     stocks at face value: their changes are net purchases at face value, before any redemption timing. The Eurosystem's
     own programme holdings (PSPP and PEPP public-sector, amortised cost) are shown for comparison.

Inputs (fetched into data/vintages/r3/ if missing; not redistributed, ignored by git):
  - MoF jgbcme_all.csv (history to the previous month-end) and jgbcme.csv (the current month).
  - MoF jgb_historical_data.xls, sheet "10年物価連動" (JGBi issue, coupon, maturity).
  - JSDA reference prices, S<YYMMDD>.csv, one file per key date. JSDA rate-limits scripted requests (HTTP 429), so the
    script waits between requests and caches every file it gets.
  - BoJ Time-Series Data Search API (www.stat-search.boj.or.jp/api/v1), database FF.
  - ECB Data Portal API (data-api.ecb.europa.eu): YC, IRS, SPF, SHSS, CSEC. Bundesbank API (api.statistiken.bundesbank.de):
    BBSIS, BBSEI. The ECB's APP and PEPP history CSVs (www.ecb.europa.eu/mopo/pdf/).
Outputs: data/r3_rates/jp_levels.csv, jp_changes.csv, jp_holder_return.csv, jp_flows_quarterly.csv, jp_flows_periods.csv,
         jp_boj_stock.csv, ea_levels.csv, ea_changes.csv, ea_holder_return.csv, ea_holders.csv, ea_eurosystem.csv
Requires: Python 3 and xlrd (pip install -r requirements.txt). Run from anywhere:
  python3 bin/r3_jgb_egb.py
"""
import csv, datetime as dt, io, json, math, os, sys, time, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "vintages", "r3")
OUT = os.path.join(ROOT, "data", "r3_rates")
UA = {"User-Agent": "Mozilla/5.0 (compatible; market-plumbing research)"}

MOF_ALL = "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv"
MOF_CUR = "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/jgbcme.csv"
MOF_AUCTIONS = "https://www.mof.go.jp/jgbs/reference/appendix/jgb_historical_data.xls"
JSDA = "https://market.jsda.or.jp/shijyo/saiken/baibai/baisanchi/files/{y}/S{d}.csv"
BOJ_API = "https://www.stat-search.boj.or.jp/api/v1/getDataCode?format=csv&lang=en&db=FF&startDate={s}&endDate={e}&code={c}"
TENORS = ["1Y", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y", "10Y", "15Y", "20Y", "25Y", "30Y", "40Y"]

# Key dates: the last JGB trading day of each year, the equity window's end, and the latest date both sources cover.
JP_KEY = [dt.date(2023, 12, 29), dt.date(2024, 12, 30), dt.date(2025, 12, 30), dt.date(2026, 6, 30)]

# Flow of Funds sectors for instrument 311. Rows must partition all holders; the identities below are asserted.
FOF_ROWS = [
    ("Bank of Japan", ["110A"], []),
    ("Depository corporations (banks)", ["120A"], []),
    ("Insurance", ["131A"], []),
    ("Pension funds (private)", ["140A"], []),
    ("Public pensions (inside general government)", ["424A"], []),
    ("Securities investment trusts", ["160A"], []),
    ("Other financial intermediaries (nonbanks; public financial institutions; dealers)", ["150A"], []),
    ("Financial auxiliaries and public captive financial institutions", ["300A", "210A"], []),
    ("Nonfinancial corporations", ["410A"], []),
    ("General government excluding public pensions", ["420A"], ["424A"]),
    ("Households and nonprofits", ["430A", "440A"], []),
    ("Overseas", ["500A"], []),
]
FOF_CODES = sorted({c for _, add, sub in FOF_ROWS for c in add + sub} |
                   {"100A", "130A", "400A", "420A", "421A", "422A", "423A", "100L", "400L"})


def fetch(url, path, wait=0.0, tries=4):
    """Download url to path once and cache it. On HTTP 429, back off (60s, 120s, 240s) and retry, then give up."""
    if os.path.exists(path):
        return True
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for k in range(tries):
        try:
            time.sleep(wait)
            data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
            if b"429 Too Many Requests" in data[:300]:          # an error page served with status 200 must not be cached
                raise urllib.error.HTTPError(url, 429, "rate limited", None, None)
            open(path, "wb").write(data)
            return True
        except urllib.error.HTTPError as e:
            if e.code == 429 and k < tries - 1:
                print(f"  [429] {url} -- waiting {60 * 2 ** k}s")
                time.sleep(60 * 2 ** k)
                continue
            print(f"  [skip] {url}: HTTP {e.code}")
            return False
    return False


# ---------------------------------------------------------------- Japan: prices
def load_mof_curve():
    fetch(MOF_ALL, os.path.join(RAW, "jgbcme_all.csv"))
    fetch(MOF_CUR, os.path.join(RAW, "jgbcme.csv"))
    out = {}
    for f in ("jgbcme_all.csv", "jgbcme.csv"):
        for r in csv.reader(io.StringIO(open(os.path.join(RAW, f), encoding="utf-8-sig", errors="replace").read())):
            if r and r[0][:4].isdigit() and "/" in r[0]:
                y, m, d = map(int, r[0].split("/"))
                out[dt.date(y, m, d)] = {t: (float(v) if v not in ("-", "") else None) for t, v in zip(TENORS, r[1:16])}
    return out


def on_or_before(series, d):
    ks = [k for k in series if k <= d]
    return max(ks) if ks else None


def interp(curve, T):
    pts = sorted((int(t[:-1]), v) for t, v in curve.items() if v is not None)
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if t0 <= T <= t1:
            return v0 + (v1 - v0) * (T - t0) / (t1 - t0)
    return pts[0][1] if T < pts[0][0] else pts[-1][1]


def load_jgbi_issues():
    import xlrd
    path = os.path.join(RAW, "jgb_historical_data.xls")
    fetch(MOF_AUCTIONS, path)
    wb = xlrd.open_workbook(path)
    sh = wb.sheet_by_name("10年物価連動")
    issues = {}
    for r in range(5, sh.nrows):
        try:
            no = int(float(sh.cell_value(r, 0)))
            issue = xlrd.xldate_as_datetime(sh.cell_value(r, 2), wb.datemode).date()
            mat = xlrd.xldate_as_datetime(sh.cell_value(r, 3), wb.datemode).date()
            cpn = float(sh.cell_value(r, 4))
        except (ValueError, TypeError):
            continue
        if no not in issues or issue < issues[no]["first_issue"]:
            issues[no] = {"first_issue": issue, "maturity": mat, "coupon": cpn}
    return issues


def jsda_price(d, issue_no):
    path = os.path.join(RAW, f"S{d:%y%m%d}.csv")
    if not fetch(JSDA.format(y=d.year, d=f"{d:%y%m%d}"), path, wait=10, tries=int(os.environ.get("R3_JSDA_TRIES", "4"))):
        return None
    for r in csv.reader(io.StringIO(open(path, "rb").read().decode("shift_jis", errors="replace"))):
        if len(r) > 7 and r[3].replace(" ", "").replace("　", "") == f"物価連動国債{issue_no}":
            return float(r[7])
    return None


def prev_coupon(d):                      # JGBi coupons fall on 10 March and 10 September
    return dt.date(d.year - 1, 9, 10) if d.month == 3 else dt.date(d.year, 3, 10)


def real_yield(p_clean, cpn, settle, mat):
    cds, d = [], mat
    while d > settle:
        cds.append(d)
        d = prev_coupon(d)
    cds.reverse()
    frac = (settle - d).days / (cds[0] - d).days
    dirty = p_clean + cpn / 2 * frac
    times = [i + (1 - frac) for i in range(len(cds))]   # half-years to each remaining coupon
    pv = lambda y: sum(cpn / 2 / (1 + y / 200) ** t for t in times) + 100 / (1 + y / 200) ** times[-1]
    lo, hi = -5.0, 15.0
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if pv(mid) > dirty else (lo, mid)
    return (lo + hi) / 2


def coupon_price(cpn, y, T):
    c, yy, n = cpn / 100.0, y / 100.0, 2.0 * T
    disc = (1.0 + yy / 2.0) ** (-n)
    return 100.0 * (c / yy * (1.0 - disc) + disc) if abs(yy) > 1e-9 else 100.0 * (1 + c * T)


# ---------------------------------------------------------------- Japan: flows
def load_fof(start="202301", end=None):
    end = end or f"{dt.date.today().year}04"
    path = os.path.join(RAW, f"boj_fof_311_{start}_{end}.csv")
    codes = ",".join(f"FOF_FFAF{c[:3]}{c[3]}311" for c in FOF_CODES)
    stock = ",".join(f"FOF_FFAS{c}311" for c in ("110A", "420L", "100L"))
    fetch(BOJ_API.format(s=start, e=end, c=codes + "," + stock), path)
    rows = list(csv.reader(io.StringIO(open(path, encoding="utf-8-sig").read())))
    i = next(k for k, r in enumerate(rows) if r and r[0] == "SERIES_CODE")
    flows, stocks = {}, {}
    for r in rows[i + 1:]:
        if len(r) < 8 or not r[0].startswith("FOF_FFA") or r[7] in ("", "null"):
            continue
        kind, code = r[0][6:8], r[0][8:12]
        (flows if kind == "AF" else stocks).setdefault(code, {})[r[6]] = int(float(r[7]))
    return flows, stocks


def check_fof_identities(f, q):
    g = lambda c: f[c][q]
    tests = [
        ("total holders = total issuers", g("100A") + g("400A") + g("500A"), g("100L") + g("400L")),
        ("financial institutions = their parts", g("100A"),
         g("110A") + g("120A") + g("130A") + g("150A") + g("160A") + g("210A") + g("300A")),
        ("insurance and pensions = insurance + pension funds", g("130A"), g("131A") + g("140A")),
        ("domestic nonfinancial = its parts", g("400A"), g("410A") + g("420A") + g("430A") + g("440A")),
        ("general government = central + local + social security", g("420A"), g("421A") + g("422A") + g("423A")),
    ]
    rows_sum = sum(sum(g(c) for c in add) - sum(g(c) for c in sub) for _, add, sub in FOF_ROWS)
    tests.append(("the table's rows = total holders", rows_sum, g("100A") + g("400A") + g("500A")))
    bad = [(n, a, b) for n, a, b in tests if a != b]
    if bad:
        raise SystemExit(f"Flow of Funds identity failed in {q}: {bad}. Do not publish the table; find the overlap.")


# ---------------------------------------------------------------- euro area
ECB = "https://data-api.ecb.europa.eu/service/data/{flow}/{key}?format=csvdata&startPeriod={start}"
BBK = "https://api.statistiken.bundesbank.de/rest/data/{flow}/{key}?format=csv&lang=en&startPeriod={start}"
ECB_APP = "https://www.ecb.europa.eu/mopo/pdf/APP_breakdown_history.csv"
ECB_PEPP = "https://www.ecb.europa.eu/mopo/pdf/PEPP_breakdown_history.csv"
EA20 = ["AT", "BE", "CY", "DE", "EE", "ES", "FI", "FR", "GR", "HR", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PT", "SI", "SK"]
EA_KEY = [dt.date(2023, 12, 29), dt.date(2024, 12, 31), dt.date(2025, 12, 31), dt.date(2026, 6, 30)]
SHSS_ROWS = [
    ("Eurosystem (national central banks and the ECB)", ["S121"], []),
    ("Banks (deposit-taking corporations)", ["S122"], []),
    ("Money market funds", ["S123"], []),
    ("Investment funds (non-MMF)", ["S124"], []),
    ("Other financial institutions, excluding investment funds", ["S12P"], ["S124"]),
    ("Insurance corporations", ["S128"], []),
    ("Pension funds", ["S129"], []),
    ("General government", ["S13"], []),
    ("Nonfinancial corporations", ["S11"], []),
    ("Households and nonprofits", ["S1M"], []),
]
SHSS_CODES = ["S1", "S11", "S12", "S121", "S122", "S123", "S124", "S12P", "S128", "S129", "S13", "S1M"]
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September",
                                       "October", "November", "December"], 1)}


def ecb_rows(flow, key, start, name):
    path = os.path.join(RAW, f"ecb_{name}.csv")
    fetch(ECB.format(flow=flow, key=key, start=start), path, wait=2)
    return list(csv.DictReader(open(path, encoding="utf-8")))


def bbk_series(flow, key, start, name):
    path = os.path.join(RAW, f"bbk_{name}.csv")
    fetch(BBK.format(flow=flow, key=key, start=start), path, wait=2)
    out = {}
    for line in open(path, encoding="utf-8-sig").read().splitlines():
        parts = line.split(",")
        if len(parts) >= 2 and parts[0][:4].isdigit() and parts[1] not in ("", "."):
            out[parts[0]] = float(parts[1])
    return out


def ecb_history_holdings(url, name, col):
    """End-of-month holdings from the ECB's APP/PEPP history CSV; the year is written only on each January row."""
    path = os.path.join(RAW, name)
    fetch(url, path, wait=1)
    out, year = {}, None
    for r in csv.reader(open(path, encoding="utf-8-sig", errors="replace")):
        if len(r) > col and r[1].strip() in MONTHS:
            if r[0].strip().isdigit():
                year = int(r[0])
            try:
                out[f"{year}-{MONTHS[r[1].strip()]:02d}"] = float(r[col].replace(",", ""))
            except ValueError:
                pass
    return out


def check_shss(h, q, country):
    g = lambda c: h.get((country, c), {}).get(q, 0.0)          # a sector a country does not report counts as zero
    tests = [("total = NFC + financial + government + households", g("S1"), g("S11") + g("S12") + g("S13") + g("S1M")),
             ("financial = its parts", g("S12"), g("S121") + g("S122") + g("S123") + g("S12P") + g("S128") + g("S129"))]
    worst = max(abs(a - b) / max(abs(a), 1.0) for _, a, b in tests)
    if worst > 0.005:
        raise SystemExit(f"SHSS identity off by {worst:.2%} for {country} {q}: {tests}. Do not publish; find the overlap.")
    return worst


def main_euro():
    # ---- prices
    bund = {t: bbk_series("BBSIS", f"D.I.ZST.ZI.EUR.S1311.B.A604.{t}.R.A.A._Z._Z.A", "2023-12-01", f"bund_{t}")
            for t in ("R10XX", "R09XX", "R02XX", "R01XX")}
    real = bbk_series("BBSEI", "M.ERZ.GVB.DE._Z.R10XX", "2023-12", "expected_real_10y")
    yc = {}
    for r in ecb_rows("YC", "B.U2.EUR.4F.G_N_A+G_N_C.SV_C_YM.SR_2Y+SR_10Y", "2023-12-01", "yc"):
        yc.setdefault(("AAA" if r["INSTRUMENT_FM"] == "G_N_A" else "ALL") + "_" + r["DATA_TYPE_FM"].split("_")[1],
                      {})[r["TIME_PERIOD"]] = float(r["OBS_VALUE"])
    conv = {}
    for r in ecb_rows("IRS", "M.IT+FR+DE.L.L40.CI.0000.EUR.N.Z", "2023-12", "irs10"):
        conv.setdefault(r["REF_AREA"], {})[r["TIME_PERIOD"]] = float(r["OBS_VALUE"])
    spf = {r["TIME_PERIOD"]: float(r["OBS_VALUE"]) for r in ecb_rows("SPF", "Q.U2.HICP.POINT.LT.Q.AVG", "2023-Q4", "spf_lt")}
    dates = lambda ser: {dt.date.fromisoformat(k): v for k, v in ser.items()}
    b10, b9, b2, b1 = (dates(bund[t]) for t in ("R10XX", "R09XX", "R02XX", "R01XX"))
    aaa10, aaa2, all10 = (dates(yc[k]) for k in ("AAA_10Y", "AAA_2Y", "ALL_10Y"))
    latest = min(max(b10), max(aaa10))
    keys = EA_KEY + [latest]
    last_m = lambda ser, d: max(k for k in ser if k <= f"{d:%Y-%m}")
    lv = []
    for k in keys:
        d, e = on_or_before(b10, k), on_or_before(aaa10, k)
        m = f"{k:%Y-%m}"
        month_avg = [v for dd, v in b10.items() if f"{dd:%Y-%m}" == m]
        mr = last_m(real, k)
        q = max(x for x in spf if x <= f"{k.year}-Q{(k.month - 1) // 3 + 1}")
        mc = last_m(conv["DE"], k)
        row = {"key_date": k.isoformat(), "bund_date": d.isoformat(), "bund10": b10[d], "bund2": b2[on_or_before(b2, k)],
               "bund_slope_10y_2y": round(b10[d] - b2[on_or_before(b2, k)], 4), "ecb_date": e.isoformat(),
               "aaa10": round(aaa10[e], 4), "aaa2": round(aaa2[on_or_before(aaa2, k)], 4), "all_issuers10": round(all10[on_or_before(all10, k)], 4),
               "conv_month": mc, "it10_conv": conv["IT"][mc], "fr10_conv": conv["FR"][mc], "de10_conv": conv["DE"][mc],
               "spread_it_de_bp": round(100 * (conv["IT"][mc] - conv["DE"][mc])), "spread_fr_de_bp": round(100 * (conv["FR"][mc] - conv["DE"][mc])),
               "real_month": mr, "expected_real10": real[mr],
               "bund10_month_avg": round(sum(month_avg) / len(month_avg), 4) if m == mr and month_avg else "",
               "survey_inflation_implied": round(sum(month_avg) / len(month_avg) - real[mr], 4) if m == mr and month_avg else "",
               "spf_quarter": q, "spf_longterm_hicp": spf[q]}
        lv.append(row)
    with open(os.path.join(OUT, "ea_levels.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lv[0])); w.writeheader(); w.writerows(lv)
    L = {r["key_date"]: r for r in lv}
    ks = [k.isoformat() for k in keys]
    periods = [("2024", ks[0], ks[1]), ("2025", ks[1], ks[2]), ("2026 to 30 Jun", ks[2], ks[3]),
               ("30 Jun to latest", ks[3], ks[4]), ("end-2023 to 30 Jun 2026 (the equity window)", ks[0], ks[3]),
               ("end-2023 to latest", ks[0], ks[4])]
    ch = []
    for name, a, b in periods:
        A, B = L[a], L[b]
        dd = lambda col: round(100 * (B[col] - A[col])) if A[col] != "" and B[col] != "" else ""
        ch.append({"period": name, "from": A["bund_date"], "to": B["bund_date"], "d_bund10_bp": dd("bund10"), "d_bund2_bp": dd("bund2"),
                   "d_bund_slope_bp": dd("bund_slope_10y_2y"), "d_aaa10_bp": dd("aaa10"), "d_all_issuers10_bp": dd("all_issuers10"),
                   "d_spread_it_de_bp": B["spread_it_de_bp"] - A["spread_it_de_bp"], "d_spread_fr_de_bp": B["spread_fr_de_bp"] - A["spread_fr_de_bp"],
                   "d_expected_real10_bp": dd("expected_real10"), "d_survey_inflation_implied_bp": dd("survey_inflation_implied"),
                   "d_spf_longterm_bp": dd("spf_longterm_hicp")})
    with open(os.path.join(OUT, "ea_changes.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ch[0])); w.writeheader(); w.writerows(ch)

    # ---- a holder's return on a constant-maturity 10-year Bund (as for JGBs)
    start = on_or_before(b10, EA_KEY[0])
    months = sorted({(d.year, d.month) for d in b10 if start <= d <= latest})
    ends = [max(d for d in b10 if (d.year, d.month) == ym and d <= latest) for ym in months]
    hr = []
    for p0, c0 in zip(ends, ends[1:]):
        y0, frac = b10[p0], (c0 - p0).days / 365.25
        y_end = b10[c0] - (b10[c0] - b9[on_or_before(b9, c0)]) * frac
        hr.append({"full": coupon_price(y0, y_end, 10.0 - frac) - 100.0 + y0 * frac, "cash": b1[on_or_before(b1, p0)] * frac,
                   "from": p0, "to": c0})
    agg = []
    for name, a, b in periods:
        a_, b_ = on_or_before(b10, dt.date.fromisoformat(a)), on_or_before(b10, dt.date.fromisoformat(b))
        sub = [x for x in hr if x["from"] >= a_ - dt.timedelta(days=3) and x["to"] <= b_ + dt.timedelta(days=3)]
        comp = lambda col: round(100.0 * (math.prod(1 + x[col] / 100.0 for x in sub) - 1.0), 3)
        agg.append({"period": name, "months": len(sub), "bund10_full_reval_compounded_pct": comp("full"),
                    "cash_1y_compounded_pct": comp("cash")})
    with open(os.path.join(OUT, "ea_holder_return.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(agg[0])); w.writeheader(); w.writerows(agg)

    # ---- who holds: SHSS (face value) by sector, summed over EA20; the rest of the world by residual against CSEC
    key = f"Q.N.U2.{'+'.join(EA20)}.{'+'.join(SHSS_CODES)}.S13.N.A.LE.F3.T._Z.XDC._T.F.V.N._T"
    h = {}
    for r in ecb_rows("SHSS", key, "2023-Q4", "shss_face"):
        h.setdefault((r["COUNTERPART_AREA"], r["REF_SECTOR"]), {})[r["TIME_PERIOD"]] = float(r["OBS_VALUE"])
    tot = {}
    for r in ecb_rows("CSEC", f"M.N.{'+'.join(EA20)}.W0.S13.S1.N.L.LE.F3.T._Z.EUR._T.N.V.N._T", "2023-12", "csec_total"):
        tot.setdefault(r["REF_AREA"], {})[r["TIME_PERIOD"]] = float(r["OBS_VALUE"])
    qs = sorted(q for q in h[("DE", "S1")] if all(q in h.get((c, "S1"), {}) for c in EA20))
    absent = sorted({(c, s_) for c in EA20 for s_ in SHSS_CODES if (c, s_) not in h})
    if absent:
        print(f"  [note] SHSS series not reported, counted as zero: {absent}")
    qmonth = lambda q: f"{q[:4]}-{int(q[-1]) * 3:02d}"
    qs = [q for q in qs if all(qmonth(q) in tot.get(c, {}) for c in EA20)]
    worst = max(check_shss(h, q, c) for q in qs for c in EA20)
    S = lambda code, q: sum(h.get((c, code), {}).get(q, 0.0) for c in EA20)
    q0, q1 = qs[0], qs[-1]
    hrows = []
    for label, add, sub in SHSS_ROWS:
        v = lambda q: sum(S(c, q) for c in add) - sum(S(c, q) for c in sub)
        hrows.append({"holder": label, "codes": "+".join(add) + ("-" + "-".join(sub) if sub else ""), q0: round(v(q0) / 1e3, 1),
                      q1: round(v(q1) / 1e3, 1), "change_eur_bn": round((v(q1) - v(q0)) / 1e3, 1)})
    total = lambda q: sum(tot[c][qmonth(q)] for c in EA20)
    row_ = lambda q: total(q) - S("S1", q)
    hrows.append({"holder": "Rest of the world (total outstanding minus all euro-area holders)", "codes": "CSEC-S1",
                  q0: round(row_(q0) / 1e3, 1), q1: round(row_(q1) / 1e3, 1), "change_eur_bn": round((row_(q1) - row_(q0)) / 1e3, 1)})
    hrows.append({"holder": "Total outstanding (CSEC, nominal value, all currencies)", "codes": "CSEC",
                  q0: round(total(q0) / 1e3, 1), q1: round(total(q1) / 1e3, 1), "change_eur_bn": round((total(q1) - total(q0)) / 1e3, 1)})
    with open(os.path.join(OUT, "ea_holders.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(hrows[0])); w.writeheader(); w.writerows(hrows)

    # ---- the Eurosystem's programme holdings (amortised cost), for comparison with its SHSS row
    pspp = ecb_history_holdings(ECB_APP, "APP_breakdown_history.csv", 13)
    pepp = ecb_history_holdings(ECB_PEPP, "PEPP_breakdown_history.csv", 17)
    erows = [{"month": m, "pspp_eur_bn": round(pspp[m] / 1e3, 1), "pepp_public_eur_bn": round(pepp[m] / 1e3, 1),
              "total_eur_bn": round((pspp[m] + pepp[m]) / 1e3, 1)} for m in sorted(set(pspp) & set(pepp)) if m >= "2023-12"]
    with open(os.path.join(OUT, "ea_eurosystem.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(erows[0])); w.writeheader(); w.writerows(erows)
    print(f"[euro area] prices to {latest}; holders {q0}-{q1}, SHSS identities within {worst:.3%} in every quarter and country")


def main_japan():
    os.makedirs(OUT, exist_ok=True)
    # ---- Japan: prices
    mof = load_mof_curve()
    issues = load_jgbi_issues()
    latest = max(mof)
    keys = JP_KEY + [latest]
    lv = []
    for k in keys:
        d = on_or_before(mof, k)
        c = mof[d]
        bench = max((n for n, v in issues.items() if v["first_issue"] <= d), default=None)
        row = {"key_date": k.isoformat(), "mof_date": d.isoformat(), "jgb10": c["10Y"], "jgb2": c["2Y"],
               "slope_10y_2y": round(c["10Y"] - c["2Y"], 4), "jgb30": c["30Y"], "jgbi_issue": bench,
               "jgbi_price": "", "jgbi_real_yield": "", "nominal_at_jgbi_maturity": "", "breakeven": "", "real10_implied": ""}
        p = jsda_price(d, bench) if bench else None
        if p is not None:
            iv = issues[bench]
            T = (iv["maturity"] - d).days / 365.25
            ry = real_yield(p, iv["coupon"], d, iv["maturity"])
            nom = interp(c, T)
            row.update({"jgbi_price": p, "jgbi_real_yield": round(ry, 4), "nominal_at_jgbi_maturity": round(nom, 4),
                        "breakeven": round(nom - ry, 4), "real10_implied": round(c["10Y"] - (nom - ry), 4)})
        lv.append(row)
    with open(os.path.join(OUT, "jp_levels.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lv[0])); w.writeheader(); w.writerows(lv)
    L = {r["key_date"]: r for r in lv}
    ks = [k.isoformat() for k in keys]
    periods = [("2024", ks[0], ks[1]), ("2025", ks[1], ks[2]), ("2026 to 30 Jun", ks[2], ks[3]),
               ("30 Jun to latest", ks[3], ks[4]), ("end-2023 to 30 Jun 2026 (the equity window)", ks[0], ks[3]),
               ("end-2023 to latest", ks[0], ks[4])]
    ch = []
    for name, a, b in periods:
        A, B = L[a], L[b]
        dd = lambda col: round(100 * (B[col] - A[col])) if A[col] != "" and B[col] != "" else ""
        ch.append({"period": name, "from": A["mof_date"], "to": B["mof_date"], "d_jgb10_bp": dd("jgb10"), "d_jgb2_bp": dd("jgb2"),
                   "d_slope_bp": dd("slope_10y_2y"), "d_jgb30_bp": dd("jgb30"), "d_breakeven_bp": dd("breakeven"),
                   "d_real10_implied_bp": dd("real10_implied")})
    with open(os.path.join(OUT, "jp_changes.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ch[0])); w.writeheader(); w.writerows(ch)

    # ---- Japan: a holder's return on a constant-maturity 10-year JGB, fully revalued month by month (as R1)
    start = on_or_before(mof, JP_KEY[0])
    months = sorted({(d.year, d.month) for d in mof if start <= d <= latest})
    ends = [max(d for d in mof if (d.year, d.month) == ym and d <= latest) for ym in months]
    hr = []
    for p, c in zip(ends, ends[1:]):
        y0, frac = mof[p]["10Y"], (c - p).days / 365.25
        y_end = mof[c]["10Y"] - (mof[c]["10Y"] - mof[c]["9Y"]) * frac      # yield at 10 - frac years
        hr.append({"from": p.isoformat(), "to": c.isoformat(), "jgb10_start": y0, "jgb10_end": mof[c]["10Y"],
                   "full_reval_pct": round(coupon_price(y0, y_end, 10.0 - frac) - 100.0 + y0 * frac, 4),
                   "cash_1y_pct": round(mof[p]["1Y"] * frac, 4)})
    agg = []
    for name, a, b in periods:
        a_, b_ = on_or_before(mof, dt.date.fromisoformat(a)), on_or_before(mof, dt.date.fromisoformat(b))
        sub = [x for x in hr if dt.date.fromisoformat(x["from"]) >= a_ - dt.timedelta(days=3)
               and dt.date.fromisoformat(x["to"]) <= b_ + dt.timedelta(days=3)]
        comp = lambda col: round(100.0 * (math.prod(1 + x[col] / 100.0 for x in sub) - 1.0), 3)
        agg.append({"period": name, "months": len(sub), "jgb10_full_reval_compounded_pct": comp("full_reval_pct"),
                    "cash_1y_compounded_pct": comp("cash_1y_pct")})
    with open(os.path.join(OUT, "jp_holder_return.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(agg[0])); w.writeheader(); w.writerows(agg)

    # ---- Japan: who bought (Flow of Funds transactions, instrument 311)
    flows, stocks = load_fof()
    qs = sorted(q for q in flows["110A"] if all(q in flows[c] for c in FOF_CODES))
    qs = [q for q in qs if q >= "202401"]
    for q in qs:
        check_fof_identities(flows, q)
    tril = lambda v: round(v / 1e4, 2)                   # 100 million yen -> trillion yen
    qrows = []
    for label, add, sub in FOF_ROWS:
        rec = {"sector": label, "codes": "+".join(add) + ("-" + "-".join(sub) if sub else "")}
        for q in qs:
            rec[q] = tril(sum(flows[c][q] for c in add) - sum(flows[c][q] for c in sub))
        qrows.append(rec)
    qrows.append({"sector": "Net issuance (issuers' liabilities)", "codes": "100L+400L",
                  **{q: tril(flows["100L"][q] + flows["400L"][q]) for q in qs}})
    with open(os.path.join(OUT, "jp_flows_quarterly.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["sector", "codes"] + qs); w.writeheader(); w.writerows(qrows)
    yrs = [("2024", "2024"), ("2025", "2025"), ("2026H1", "2026")]
    prows = []
    for r in qrows:
        rec = {"sector": r["sector"]}
        for name, y in yrs:
            rec[name] = round(sum(r[q] for q in qs if q.startswith(y)), 1)
        rec["2024Q1-" + qs[-1]] = round(sum(r[q] for q in qs), 1)
        prows.append(rec)
    with open(os.path.join(OUT, "jp_flows_periods.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(prows[0])); w.writeheader(); w.writerows(prows)
    # the BoJ's holdings and the stock outstanding, at market value (Flow of Funds stocks)
    srows = []
    for q in sorted(q for q in stocks["110A"] if q >= "202304" and q in stocks["420L"] and q in stocks["100L"]):
        tot = stocks["420L"][q] + stocks["100L"][q]
        srows.append({"quarter": q, "boj_holdings_mv_tril_yen": tril(stocks["110A"][q]), "outstanding_mv_tril_yen": tril(tot),
                      "boj_share_pct": round(100.0 * stocks["110A"][q] / tot, 2)})
    with open(os.path.join(OUT, "jp_boj_stock.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(srows[0])); w.writeheader(); w.writerows(srows)
    print(f"[japan] prices to {latest}; flows {qs[0]}-{qs[-1]}, identities hold in all {len(qs)} quarters")


def main():
    os.makedirs(OUT, exist_ok=True)
    main_japan()
    main_euro()


if __name__ == "__main__":
    main()
