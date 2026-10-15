#!/usr/bin/env python3
"""Gold tonnes ledger: who added gold, in tonnes, month by month, reconciled to the World Gold Council's (WGC) published
aggregates, with the unexplained residual stated -- E-021 follow-up ("where does the money in gold come from").
Standard library plus openpyxl and xlrd (both in requirements.txt).

  python3 bin/build_gold_ledger.py             # pull every source, save the raw files, write every output, print the tables
  python3 bin/build_gold_ledger.py --offline   # rebuild every output from the saved raw files (no network)

SOURCES (all free, anonymous, scripted with the neutral User-Agent below; one request at a time with a pause; the script
retries only where the server says to (429/503, honouring Retry-After), then stops, and never works around a block):
  1. IMF International Liquidity (IL), SDMX 2.1 API, api.imf.org/external/sdmx/2.1/data/IMF.STA,IL/...  No key.
       RGV_REVS  gold volume, fine troy ounces (unit FTO), every reporter, monthly, from 2018-12 (the base month for 2019-01)
       RGOLDMV_REVS  gold at market value, SDR (XDR), World (G001);   TRGMV_REVS  total reserves, USD and XDR, World
     Codelist CL_COUNTRY gives the English names. BEA, EZB, BIS and IMF are institutions (CL_ORGANIZATION: Bank of Central
     African States, European Central Bank, Bank for International Settlements, IMF); G001 = World and the other G-codes are aggregates.
  2. SAFE (China), the State Administration of Foreign Exchange's own monthly "Official Reserve Assets" release, ounces
     ("7747万盎司" = 77.47 million oz). One workbook per year, 2019-2026 (2019 is an HTML table, 2020 a legacy .xls).
  3. SPDR Gold Trust (GLD), the sponsor's historical-archive xlsx (daily "Tonnes of Gold", ounces, NAV). The sponsor's own live
     data feed (api.spdrgoldshares.com/api/v1/data, the feed behind its product page) is saved for the spot check.
  4. iShares Gold Trust (IAU): the product page's own "fundDownload" file (NAV per share and shares outstanding, daily; no tonnes
     history is published) and the product page (stated tonnes and ounces for the latest day).
  5. LBMA London Vault Holdings, monthly, '000 troy oz (custody stock, not purchases; the file's full history from 2016-07).
  6. WGC Gold Demand Trends: the quarterly "Table 1: gold supply and demand by sector, tonnes" that the WGC prints, in HTML, on
     each public release page (gold.org/goldhub/research/gold-demand-trends/...). Public pages carry that table from the Q1 2023
     release. THE WGC'S DOWNLOADABLE XLSX/PDF FILES AND ITS MONTHLY ETF-FLOW DATA FILES ARE BEHIND A LOGIN ("DU1: You are not
     logged in"; the ETF page says registration is free). THIS SCRIPT DOES NOT REQUEST THEM and does not try to get around the
     login: that leg is stopped. Quarters before Q1 2022 therefore have no WGC counterpart here. Each release is kept as a
     separate vintage, because the WGC revises (Q1 2026 central banks: 243.7 t at release, 56.5 t three months later).
     The monthly ETF page's prose (September 2026 holdings and the Q3 change) is read for the latest quarter only.

UNITS. Tonnes (t) everywhere unless a column says otherwise; 1 t = 32,150.7466 troy oz (the repository convention).
IMF stocks are month-end holdings; changes are month-end to month-end. XDR = IMF Special Drawing Right. USD bn = US$ billions.
Quarters are calendar quarters; a quarter's change is the quarter-end stock minus the previous quarter-end stock.

THE OFFICIAL SECTOR: CARRY-FORWARD RULES (explicit, because the later months are always incomplete)
  * A reporter is "fresh" in month m if it has an observation for m. The IMF's latest months hold only a minority of reporters
    (September 2026: 16 of 142). A missing report is NEVER a sale: a reporter's holding in a month without a report is its last
    reported holding, carried forward ("cf"), however old. A reporter that reports again after a gap contributes the whole
    change in the month it returns ("late catch-up"). The first observation of a new reporter is its base, not a purchase.
  * Headline monthly change (official_change_cf_t) = sum over all reporters of cf(m) - cf(m-1). This rule reproduces the IMF's
    own World aggregate (G001) change month by month to <0.01 t, except 2019-09, 2022-11/12 and 2025-12 (<=0.31 t each); G001's
    LEVEL is the sum of the reporters plus a constant ~402 t that no series in the API explains, which is why the ledger shows
    G001 as the level and the reporters' sum only for changes. The like-for-like change (reporters with a report in both m-1
    and m) is shown beside it; the difference is the late catch-up.
  * Coverage is printed for every month: reporters fresh / reporters in the universe (every reporter with an observation in
    2024-01 or later, 142), the share of the carried-forward stock that is fresh, and the tonnes carried flat for more than 6 months.
    A month is "provisional" if fewer than 70% of the universe has reported it; otherwise "reported", which means 70% or more of
    the universe has reported it, not that every reporter has. Provisional months are a FLOOR on buying.
    Even complete-looking months carry Russia (2,326.5 t, last report 2025-11), Lebanon, the ECB and others flat.
  * "official_change_cf_china_safe_t" replaces China's IMF path by SAFE's own release where SAFE has the month (SAFE leads the
    IMF's China series by up to three months). It is the only substitution made.

THE ETFs. GLD tonnes = the sponsor's "Tonnes of Gold" (asserted to equal total ounces / 32,150.7466 within 0.02 t since 2018-12).
GLD-implied gold price = NAV per share / ounces per share (the LBMA PM price the trust's NAV used; the sponsor's feed states
the same $ figure for the latest day). IAU tonnes = shares outstanding x NAV per share / that price / 32,150.7466, checked on
the latest day against the IAU page's stated tonnes. (The alternative price, total NAV / total ounces, is carried in the
printout; it is 0.04% off on the latest day against 0.007% for the per-share price, and noisier.) Month-end = last trading day.

WHAT THE RECONCILIATION MEANS (and does not)
  * gap_wgc_minus_imf_t = WGC "Central banks & other inst." minus the IMF-reported change. It is the WGC's ESTIMATE of unreported
    buying plus timing, coverage and definition differences (swaps, the WGC's own revisions, reporters absent from the IMF
    file such as Russia). It is not a measure of unreported buying.
  * etf coverage = (GLD + IAU change) / (WGC global gold-ETF change). Shown only where the WGC change is at least 20 t in absolute
    size; otherwise the tonnes difference is the useful number.
  * The residual table splits the WGC's total demand (= total supply, by the WGC's construction) into what free data observes
    (IMF-reported official change; GLD; IAU), the two gaps against the WGC's own lines (central banks, ETFs), the lines with
    no free counterpart (jewellery fabrication, technology, bar and coin) and the WGC's balancing item "OTC and other".
    Those components add up to the WGC total demand exactly (asserted within rounding).
  * The value split: world official gold at market value (IMF RGOLDMV_REVS, XDR) = tonnes x price. Each month's change is split
    by the symmetric (midpoint) rule: volume = change in ounces x average of the two prices; price = change in price x
    average of the two ounce stocks. The two parts add to the change exactly. Windows are sums of monthly pieces.

KNOWN DATA ISSUES (reported, not corrected, so that the ledger reproduces the IMF's own aggregate):
  * BIS (the Bank for International Settlements) swings by 20-130 t a month and reverses (custody and swap activity, not purchases);
    in the IMF's World total it adds noise to every monthly change. The countries-only change (official_change_countries_t, and
    gap_wgc_minus_imf_countries_t) is the cleaner series; the headline keeps the institutions because the IMF's World total does.
  * FJI (Fiji) reports 1,001,000 oz for 2019-01 against a 1,000 oz base: +31.1 t in January 2019, -31.1 t in February (an apparent typo).
  * The IMF values gold at a price date of its own: for 2026-08 its value implies $4,316/oz against a GLD-implied month-end $4,563
    (-5.7%); the XDR price effect therefore uses IMF prices, and a GLD-priced USD sensitivity is printed beside it.
  * SAFE's 2024 workbook has no December 2024 row (SAFE's later workbook starts in January 2025), so IMF fills that month for China.
  * Russia (2,326.5 t) has not reported to the IMF since 2025-11; the WGC's own text attributes 2026 sales to Russia, Turkey and
    Azerbaijan, so the IMF-based 2026 change is missing a seller that the WGC can see.

LICENSING (the repository is public). PUBLIC, committed files hold only IMF International Liquidity data (IMF terms allow reuse with
attribution), SAFE's own China releases, and our own computed reconciliation figures (the quarterly and annual IMF-versus-WGC gaps and
residuals, stated as numbers; the few WGC and ETF aggregate figures they compare, quarter by quarter, as cited facts). They carry NO
full time series copied or derived from sponsor or vendor data: no GLD or IAU daily or monthly tonnes, no LBMA vault history, no WGC
table, no price series derived from GLD. Everything of that kind is written to the LOCAL, git-ignored folder data/vintages/gold/derived/,
beside the raw sponsor files in data/vintages/gold/. Source credit for the figures that are quoted: World Gold Council (Gold Demand
Trends, Metals Focus, Refinitiv GFMS, ICE Benchmark Administration); SPDR Gold Trust and iShares Gold Trust (sponsors' published data).

OUTPUTS (two-column files in data/history/ are the repository's disposable cache, overwritten each run; as_of,value)
 PUBLIC (committed):
  data/gold/ledger_monthly.csv                    one row per month 2019-01 to the latest: the official sector (IMF, SAFE) and the IMF value split
  data/gold/ledger_quarterly_reconciliation.csv   one row per quarter 2019Q1 to the latest: IMF versus WGC central banks, GLD+IAU versus WGC ETFs
  data/gold/ledger_annual_reconciliation.csv      calendar years 2019-2025, 2026 H1 (the WGC-matched window), 2026 year to date
  data/gold/official_by_country_changes.csv       top buyers and sellers by window, cf basis, with whole-window totals
  data/history/gold_official_world_tonnes.csv     IMF World (G001), month-end          data/history/gold_china_tonnes.csv   SAFE (IMF fills 2018-12 and Dec 2024)
  data/gold/raw/                                  IMF and SAFE raw pulls (government/IGO data) and pull_log.tsv (url, sha256 of every raw file)
 LOCAL (git-ignored, data/vintages/gold/ and data/vintages/gold/derived/):
  raw SPDR, iShares, LBMA and WGC files (data/vintages/gold/)
  derived/ledger_monthly_full.csv, derived/ledger_quarterly_reconciliation_full.csv, derived/ledger_annual_reconciliation_full.csv   the same tables with
      every GLD, IAU, LBMA and WGC column and the GLD-implied price
  derived/gold_gld_tonnes.csv (daily)   derived/gold_iau_tonnes.csv (daily, reconstructed)   derived/gold_lbma_vault_tonnes.csv (month-end)   as_of,value
  derived/wgc_gdt_table_parsed.csv        every WGC line, every vintage
"""
import os, re, sys, csv, ssl, math, time, html, json, hashlib, calendar, argparse, datetime, urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = os.path.join(ROOT, "data", "history")
GOLD = os.path.join(ROOT, "data", "gold")
RAWG = os.path.join(GOLD, "raw")
VINT = os.path.join(ROOT, "data", "vintages", "gold")
VWGC = os.path.join(VINT, "wgc")
DERIVED = os.path.join(VINT, "derived")          # local only: series derived from sponsor/vendor data
LOG = os.path.join(RAWG, "pull_log.tsv")
UA = {"User-Agent": "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)", "Accept-Encoding": "identity"}

OZ = 32150.7466                      # troy ounces per tonne
IMF_BASE = "https://api.imf.org/external/sdmx/2.1"
IMF_FLOW = "IMF.STA,IL"
IMF_START = "2018-12"                # base month for the 2019-01 change
LEDGER_START = "2019-01"
UNIVERSE_FROM = "2024-01"            # a reporter is in the coverage universe if it has any observation in or after this month
STALE_MONTHS = 6
PROVISIONAL_BELOW = 0.70             # share of the universe that must have reported for a month not to be provisional
AGG = re.compile(r"^G(X)?\d+$")      # IMF aggregate codes: G001 World, G110, ..., GX010
INSTITUTIONS = {"IMF": "International Monetary Fund", "BIS": "Bank for International Settlements",
                "EZB": "European Central Bank", "BEA": "Bank of Central African States"}   # IMF CL_ORGANIZATION v2.8.0, English names
SAFE_INDEX = "https://www.safe.gov.cn/en/ForexReserves/index.html"
SAFE_YEARS = list(range(2019, 2027))
GLD_URL = "https://api.spdrgoldshares.com/api/v1/historical-archive?product=gld&exchange=NYSE&lang=en"
GLD_LIVE = "https://api.spdrgoldshares.com/api/v1/data?product=gld&exchange=NYSE&lang=en"
IAU_PAGE = "https://www.ishares.com/us/products/239561/ishares-gold-trust-fund"
LBMA_PAGE = "https://www.lbma.org.uk/prices-and-data/london-vault-data"
WGC_BASE = "https://www.gold.org/goldhub/research/gold-demand-trends/"
WGC_ETF_PAGE = "https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2026/10"   # 7 Oct 2026 release, September data
# releases whose public page prints the quarterly table, in publication order
WGC_RELEASES = ["q1-2023", "q2-2023", "q3-2023", "full-year-2023", "q1-2024", "q2-2024", "q3-2024", "full-year-2024",
                "q1-2025", "q2-2025", "q3-2025", "full-year-2025", "q1-2026", "q2-2026"]


# ------------------------------------------------------------------------------------------------ small helpers
def madd(m, k):
    t = int(m[:4]) * 12 + int(m[5:7]) - 1 + k
    return f"{t // 12:04d}-{t % 12 + 1:02d}"

def mrange(a, b):
    out = []
    while a <= b:
        out.append(a); a = madd(a, 1)
    return out

def mdiff(a, b):
    return (int(b[:4]) * 12 + int(b[5:7])) - (int(a[:4]) * 12 + int(a[5:7]))

def mend(m):
    return f"{m}-{calendar.monthrange(int(m[:4]), int(m[5:7]))[1]:02d}"

def qof(m):
    return f"{m[:4]}Q{(int(m[5:7]) - 1) // 3 + 1}"

def qend(q):
    return f"{q[:4]}-{int(q[5]) * 3:02d}"

def qprev(q):
    return qof(madd(qend(q), -3))

def fmt(x, nd=3):
    if x is None or (isinstance(x, float) and math.isnan(x)): return ""
    if isinstance(x, str): return x
    if isinstance(x, bool): return "true" if x else "false"
    if isinstance(x, int): return str(x)
    return f"{round(x, nd) + 0.0:.{nd}f}"

def write_csv(path, fields, rows, nd=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    nd = nd or {}
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(fields)
        for r in rows: w.writerow([fmt(r.get(c), nd.get(c, 3)) for c in fields])

def write_hist(name, pairs, nd=3, folder=None):
    folder = folder or HIST
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, f"gold_{name}.csv"), "w", encoding="utf-8", newline="") as f:
        f.write("as_of,value\n")
        for d, v in pairs: f.write(f"{d},{fmt(v, nd)}\n")

def add(*xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) if xs else None

def sub(a, b):
    return None if a is None or b is None else a - b

def pct(a, b):
    return None if a is None or b in (None, 0) else 100.0 * a / b


# ------------------------------------------------------------------------------------------------ network (pull mode)
def get(url, tries=4, accept=None):
    hdr = dict(UA)
    if accept: hdr["Accept"] = accept
    for k in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=120, context=ssl.create_default_context())
            return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and k < tries - 1:
                wait = int(e.headers.get("Retry-After") or 0) or 15 * (k + 1)
                print(f"  HTTP {e.code}; the server asked for a pause; waiting {wait}s", file=sys.stderr); time.sleep(wait); continue
            raise SystemExit(f"STOP: HTTP {e.code} for {url}. Not retrying further and not working around it.")
        except urllib.error.URLError as e:
            if k < tries - 1: time.sleep(10 * (k + 1)); continue
            raise SystemExit(f"STOP: network error for {url}: {e}")

LOG_ROWS = []

def save(path, data, url):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f: f.write(data)
    LOG_ROWS.append((os.path.relpath(path, ROOT), url, datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                     hashlib.sha256(data).hexdigest(), len(data)))
    print(f"  saved {os.path.relpath(path, ROOT)}  {len(data):,} bytes")
    time.sleep(1.0)

def pull():
    print("pulling (one request at a time, 1 s apart)")
    imf = lambda key, q="": f"{IMF_BASE}/data/{IMF_FLOW}/{key}{q}"
    save(os.path.join(RAWG, "imf_il_rgv_revs_all.xml"), get(imf("*.RGV_REVS.*.M", f"?startPeriod={IMF_START}")), imf("*.RGV_REVS.*.M", f"?startPeriod={IMF_START}"))
    save(os.path.join(RAWG, "imf_il_rgoldmv_revs_world.xml"), get(imf("G001.RGOLDMV_REVS.*.M", f"?startPeriod={IMF_START}")), imf("G001.RGOLDMV_REVS.*.M", f"?startPeriod={IMF_START}"))
    save(os.path.join(RAWG, "imf_il_trgmv_revs_world.xml"), get(imf("G001.TRGMV_REVS.*.M", f"?startPeriod={IMF_START}")), imf("G001.TRGMV_REVS.*.M", f"?startPeriod={IMF_START}"))
    save(os.path.join(RAWG, "imf_cl_country.xml"), get(f"{IMF_BASE}/codelist/IMF/CL_COUNTRY"), f"{IMF_BASE}/codelist/IMF/CL_COUNTRY")
    # SAFE: the index lists "Official Reserve Assets (YYYY)" pages; each page links a workbook (2019 has none: the page is the table)
    idx = get(SAFE_INDEX); save(os.path.join(RAWG, "safe_forexreserves_index.html"), idx, SAFE_INDEX)
    pages = {}
    for m in re.finditer(r'href="([^"]+)"[^>]*>\s*Official Reserve Assets\s*[(（]\s*(\d{4})\s*[)）]', idx.decode("utf-8", "replace")):
        pages.setdefault(int(m.group(2)), m.group(1))
    for y in SAFE_YEARS:
        assert y in pages, f"SAFE index has no Official Reserve Assets ({y}) link"
        purl = urllib.parse.urljoin(SAFE_INDEX, pages[y]); page = get(purl)
        link = re.search(r'href="(/en/file/file/[^"]+\.(?:xlsx|xls))"', page.decode("utf-8", "replace"))
        if link:
            ext = link.group(1).rsplit(".", 1)[1]; furl = urllib.parse.urljoin(purl, link.group(1))
            save(os.path.join(RAWG, f"safe_oas_{y}.{ext}"), get(furl), furl)
        else:
            save(os.path.join(RAWG, f"safe_oas_{y}.html"), page, purl)
    # sponsors -> data/vintages/gold (git-ignored)
    save(os.path.join(VINT, "spdr_gld_archive.xlsx"), get(GLD_URL), GLD_URL)
    save(os.path.join(VINT, "spdr_gld_live_data.json"), get(GLD_LIVE, accept="application/json"), GLD_LIVE)
    pg = get(IAU_PAGE); save(os.path.join(VINT, "ishares_iau_page.html"), pg, IAU_PAGE)
    dl = re.search(r'href="(https://www\.blackrock\.com/varnish-api/[^"]*component=fundDownload[^"]*)"', pg.decode("utf-8", "replace"))
    assert dl, "IAU page has no fundDownload link"
    durl = html.unescape(dl.group(1)); save(os.path.join(VINT, "ishares_iau_fund.xls"), get(durl), durl)
    lp = get(LBMA_PAGE); save(os.path.join(VINT, "lbma_vault_page.html"), lp, LBMA_PAGE)
    cands = re.findall(r'href="(https://cdn\.lbma\.org\.uk/downloads/LBMA-London-Vault-Holdings-Data-([A-Za-z]+)-(\d{4})\.xlsx)"', lp.decode("utf-8", "replace"))
    assert cands, "LBMA page has no vault-holdings workbook link"
    mon = {n: i for i, n in enumerate(calendar.month_name) if n}
    url = max(cands, key=lambda c: (int(c[2]), mon[c[1]]))[0]; save(os.path.join(VINT, "lbma_london_vault_holdings.xlsx"), get(url), url)
    for r in WGC_RELEASES:
        u = WGC_BASE + "gold-demand-trends-" + r; save(os.path.join(VWGC, f"gdt_{r}.html"), get(u), u)
    save(os.path.join(VWGC, "etf_flows_2026-10.html"), get(WGC_ETF_PAGE), WGC_ETF_PAGE)
    os.makedirs(RAWG, exist_ok=True)
    with open(LOG, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n"); w.writerow(["path", "source_url", "pulled_at_utc", "sha256", "size_bytes"]); w.writerows(LOG_ROWS)


def rd(path):
    with open(path, "rb") as f: return f.read()

def verify_raw():
    """--offline: re-hash every raw file against pull_log.tsv (a mismatch means the saved snapshot was edited)."""
    if not os.path.exists(LOG): print("  (no pull_log.tsv; skipping hash verification)"); return
    n = bad = miss = 0
    with open(LOG, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            p = os.path.join(ROOT, r["path"])
            if not os.path.exists(p): miss += 1; continue
            n += 1; bad += hashlib.sha256(rd(p)).hexdigest() != r["sha256"]
    print(f"  raw files re-hashed against pull_log.tsv: {n} checked, {bad} changed, {miss} absent from this checkout")
    if bad: raise SystemExit("STOP: a saved raw file does not match its logged sha256")


# ------------------------------------------------------------------------------------------------ parsers
def parse_imf(xml_bytes, indicator):
    """{(country, unit): {YYYY-MM: value}} from an SDMX structure-specific message."""
    out = {}
    for s in ET.fromstring(xml_bytes).iter("Series"):
        a = s.attrib
        assert a["INDICATOR"] == indicator and a["FREQUENCY"] == "M", a
        d = {}
        for o in s.findall("Obs"):
            m = re.fullmatch(r"(\d{4})-M(\d{2})", o.attrib["TIME_PERIOD"]); assert m, o.attrib
            v = o.attrib.get("OBS_VALUE")
            if v not in (None, ""): d[f"{m.group(1)}-{m.group(2)}"] = float(v)
        out[(a["COUNTRY"], a["UNIT"])] = d
    return out

def parse_codelist(xml_bytes):
    ns = {"s": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure", "c": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common"}
    lang = "{http://www.w3.org/XML/1998/namespace}lang"; names = {}
    for code in ET.fromstring(xml_bytes).iter("{%s}Code" % ns["s"]):
        en = [n.text for n in code.findall("c:Name", ns) if n.attrib.get(lang) == "en"]
        names[code.attrib["id"]] = en[0] if en else ""
    return names

def parse_safe():
    """{YYYY-MM: ounces} from the yearly Official Reserve Assets workbooks (gold row: "NNNN万盎司" = NNNN x 10,000 oz)."""
    import openpyxl, xlrd
    out = {}
    for y in SAFE_YEARS:
        base = os.path.join(RAWG, f"safe_oas_{y}")
        if os.path.exists(base + ".xlsx"):
            ws = openpyxl.load_workbook(base + ".xlsx", data_only=True).worksheets[0]
            rows = [list(r) for r in ws.iter_rows(values_only=True)]
        elif os.path.exists(base + ".xls"):
            sh = xlrd.open_workbook(base + ".xls").sheet_by_index(0)
            rows = [sh.row_values(i) for i in range(sh.nrows)]
        else:
            h = rd(base + ".html").decode("utf-8", "replace"); rows = []
            for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", h, re.S):
                cells = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
                rows.append(cells)
        oz_rows = [r for r in rows if sum(isinstance(c, str) and c.strip().endswith("万盎司") for c in r) >= 2]
        assert len(oz_rows) == 1, f"SAFE {y}: expected one ounce row, found {len(oz_rows)}"
        vals = [int(re.match(r"(\d+)", c.strip()).group(1)) * 10000 for c in oz_rows[0] if isinstance(c, str) and c.strip().endswith("万盎司")]
        assert len(vals) % 2 == 0 and all(vals[i] == vals[i + 1] for i in range(0, len(vals), 2)), f"SAFE {y}: USD and SDR columns disagree"
        for k in range(len(vals) // 2): out[f"{y}-{k + 1:02d}"] = float(vals[2 * k])
    return out

def parse_gld():
    """{date: {tonnes, ounces, navps, ozps, nav, price}}; price = NAV/share / ounces/share (the PM price the trust used)."""
    import openpyxl
    ws = openpyxl.load_workbook(os.path.join(VINT, "spdr_gld_archive.xlsx"), data_only=True)["US GLD Historical Archive"]
    out = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[0] is None or isinstance(r[1], str): continue          # 'US Holiday' rows
        d = datetime.datetime.strptime(r[0], "%d-%b-%Y").date().isoformat()
        out[d] = dict(tonnes=float(r[9]), ounces=float(r[8]), navps=float(r[3]), ozps=float(r[2]), nav=float(r[10]))
        out[d]["price"] = out[d]["navps"] / out[d]["ozps"]; out[d]["price_tot"] = out[d]["nav"] / out[d]["ounces"]
    return out

def parse_iau():
    t = rd(os.path.join(VINT, "ishares_iau_fund.xls")).decode("utf-8")
    i = t.find('<ss:Worksheet ss:Name="Historical">'); j = t.find("</ss:Worksheet>", i); assert i > 0 and j > i
    out = {}
    for r in re.findall(r"<ss:Row[^>]*>(.*?)</ss:Row>", t[i:j], re.S)[1:]:
        v = [re.sub(r"\s+", " ", x).strip() for x in re.findall(r"<ss:Data[^>]*>(.*?)</ss:Data>", r, re.S)]
        try: out[datetime.datetime.strptime(v[0], "%b %d, %Y").date().isoformat()] = (float(v[1].replace(",", "")), float(v[3].replace(",", "")))
        except (ValueError, IndexError): continue                      # non-trading dates carry '--' shares
    return out

def parse_iau_page():
    u = html.unescape(rd(os.path.join(VINT, "ishares_iau_page.html")).decode("utf-8", "replace"))
    def one(key):
        m = re.search(r'"%s":\{[^{}]*?"formattedValue":"([\d,\.]+)"[^{}]*?"formattedAsOfDate":"([^"]+)"' % key, u); assert m, f"IAU page: {key} not found"
        return float(m.group(1).replace(",", "")), datetime.datetime.strptime(m.group(2), "%b %d, %Y").date().isoformat()
    t, d1 = one("tonnes"); o, d2 = one("ounces"); assert d1 == d2
    return dict(date=d1, tonnes=t, ounces=o)

def parse_gld_live():
    d = json.loads(rd(os.path.join(VINT, "spdr_gld_live_data.json")))["data"]
    num = lambda s: float(re.sub(r"[^\d.]", "", s))
    return dict(date=datetime.datetime.strptime(d["total_tonnes"]["date"], "%B %d, %Y").date().isoformat(),
                tonnes=num(d["total_tonnes"]["value"]), ounces=num(d["total_ounces"]["value"]), pm_fix=num(d["pm_fix_usd"]["value"]))

def parse_lbma():
    import openpyxl
    ws = openpyxl.load_workbook(os.path.join(VINT, "lbma_london_vault_holdings.xlsx"), data_only=True).worksheets[0]
    out = {}
    for r in ws.iter_rows(min_row=4, values_only=True):
        if r[0] is None or r[1] is None: continue
        m = r[0].strftime("%Y-%m") if hasattr(r[0], "strftime") else str(r[0])[:7]
        assert re.fullmatch(r"\d{4}-\d{2}", m), r
        out[m] = float(r[1]) * 1000.0                                   # '000 troy oz -> oz
    return out

WGC_LINES = {"mine production": "mine_production", "net producer hedging": "net_producer_hedging", "recycled gold": "recycled_gold",
             "total supply": "total_supply", "total mine supply": "total_mine_supply", "jewellery fabrication": "jewellery_fabrication",
             "jewellery consumption": "jewellery_consumption", "jewellery inventory": "jewellery_inventory", "technology": "technology",
             "electronics": "electronics", "other industrial": "other_industrial", "dentistry": "dentistry", "investment": "investment",
             "total bar and coin": "bar_coin", "total bar & coin demand": "bar_coin", "bars": "bars", "physical bar demand": "bars",
             "official coins": "official_coins", "official coin": "official_coins", "medals/imitation coins": "medals_imitation",
             "medals/imitation coin": "medals_imitation", "etfs & similar products": "etf", "central banks & other inst": "central_banks",
             "gold demand": "gold_demand", "otc and other": "otc_other", "total demand": "total_demand"}

def parse_wgc_release(slug):
    """-> (publication date, [(period, line, value)]); periods '2024Q3' for 'Q3'24' columns, 'Y2024' for annual columns."""
    h = rd(os.path.join(VWGC, f"gdt_{slug}.html")).decode("utf-8", "replace")
    pub = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})', h).group(1)
    cells = lambda row: [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
    for tb in re.findall(r"<table.*?</table>", h, re.S):
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", tb, re.S)
        if len(rows) < 20: continue
        # the page's rows are ragged (spacer cells come and go, and some rows add a trailing '-' change cell), so align by position
        # AMONG THE NON-EMPTY CELLS, from the left; the identity check on every release (below) would catch any mis-alignment
        hdr = [x for x in cells(rows[0])[1:] if x]
        cols = []
        for i, x in enumerate(hdr):
            q = re.fullmatch(r"Q([1-4])'(\d\d)", x)
            if q: cols.append((i, f"20{q.group(2)}Q{q.group(1)}"))
            elif re.fullmatch(r"\d{4}", x): cols.append((i, f"Y{x}"))
        if not any(p[0] != "Y" for _, p in cols): continue
        out = []
        for r in rows[1:]:
            c = cells(r)
            if not c: continue
            lab = re.sub(r"\s+", " ", c[0].lower().replace("&amp;", "&")).strip().rstrip(".")
            if lab.startswith("lbma gold price"): line = "lbma_price_usd_oz"
            else: line = WGC_LINES.get(lab)
            if not line: continue
            vals = [x for x in c[1:] if x]
            assert len(vals) >= len(hdr), f"WGC {slug}: row {lab!r} has {len(vals)} cells, header {len(hdr)}"     # a row may carry extra trailing '-' change cells
            for i, p in cols:
                try: out.append((p, line, float(vals[i].replace(",", ""))))
                except ValueError: pass
        return pub, out
    raise SystemExit(f"STOP: no quarterly table found on the saved WGC page {slug}")

def parse_wgc_etf_page():
    """Latest-quarter prose from the WGC monthly ETF page: Q3 2026 change in global holdings (t), record holdings (t)."""
    t = rd(os.path.join(VWGC, "etf_flows_2026-10.html")).decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S); t = re.sub(r"<[^>]+>", " ", html.unescape(t)); t = re.sub(r"\s+", " ", t)
    a = re.search(r"During Q3,? global gold ETFs.{0,120}?collective holdings grew by ([\d,]+)t", t)
    b = re.search(r"holdings (?:rose|grew) ([\d,]+)t to a record ([\d,]+)t", t)
    c = re.search(r"Published: (\d+ \w+, \d{4})", t)
    return dict(q3_change_t=float(a.group(1).replace(",", "")) if a else None, sep_holdings_t=float(b.group(2).replace(",", "")) if b else None,
                sep_change_t=float(b.group(1).replace(",", "")) if b else None, published=c.group(1) if c else "")


# ------------------------------------------------------------------------------------------------ 1. the official sector
def build_official(rgv, names):
    series = {c: d for (c, u), d in rgv.items()}
    assert all(u == "FTO" for (_, u) in rgv), "IMF gold volume must be in fine troy ounces (FTO)"
    reporters = sorted(c for c in series if not AGG.match(c))
    last = max(max(series[c]) for c in reporters)
    months = mrange(IMF_START, last)
    L, fresh, age = {}, {}, {}
    for c in reporters:
        s = series[c]; cur = None; a = 0; L[c], fresh[c], age[c] = [], [], []
        for m in months:
            if m in s: cur, a = s[m], 0
            elif cur is not None: a += 1
            L[c].append(cur); fresh[c].append(m in s); age[c].append(a if cur is not None else None)
    universe = [c for c in reporters if max(series[c]) >= UNIVERSE_FROM]
    first_obs = {c: min(series[c]) for c in reporters}
    rows = {}
    for i, m in enumerate(months):
        r = dict(month=m)
        lv = {c: L[c][i] for c in reporters if L[c][i] is not None}
        r["cf_total_oz"] = sum(lv.values())
        r["cf_countries_oz"] = sum(v for c, v in lv.items() if c not in INSTITUTIONS)
        r["cf_inst_oz"] = sum(v for c, v in lv.items() if c in INSTITUTIONS)
        r["fresh_n"] = sum(1 for c in universe if fresh[c][i])
        r["universe_n"] = sum(1 for c in universe if first_obs[c] <= m)
        r["fresh_stock_share"] = sum(L[c][i] for c in reporters if fresh[c][i]) / r["cf_total_oz"]
        r["stale_gt6_oz"] = sum(L[c][i] for c in reporters if L[c][i] is not None and age[c][i] > STALE_MONTHS)
        if i > 0:
            ch = chc = chi = lfl = 0.0; nl = 0; best = (0.0, ""); worst_ = (0.0, "")
            for c in reporters:
                if L[c][i] is None or L[c][i - 1] is None: continue          # first observation = base, not a flow
                d = L[c][i] - L[c][i - 1]; ch += d
                if d > best[0]: best = (d, c)
                if d < worst_[0]: worst_ = (d, c)
                if c in INSTITUTIONS: chi += d
                else: chc += d
                if fresh[c][i] and fresh[c][i - 1]: lfl += d; nl += 1
            r.update(change_oz=ch, change_countries_oz=chc, change_inst_oz=chi, lfl_oz=lfl, lfl_n=nl,
                     top_buyer=best[1], top_buyer_oz=best[0] if best[1] else None, top_seller=worst_[1], top_seller_oz=worst_[0] if worst_[1] else None)
        rows[m] = r
    return dict(series=series, reporters=reporters, months=months, L=L, fresh=fresh, age=age, universe=universe, rows=rows, last=last, first_obs=first_obs)


def top_movers(imf, names, windows, k=10):
    out = []; mi = {m: i for i, m in enumerate(imf["months"])}
    for label, a, b in windows:
        ch = []
        for c in imf["reporters"]:
            la, lb = imf["L"][c][mi[a]], imf["L"][c][mi[b]]
            if la is None or lb is None: continue
            obs = [m for m in imf["series"][c] if m <= b]
            ch.append((c, (lb - la) / OZ, la / OZ, lb / OZ, max(obs)))
        buy = sorted([x for x in ch if x[1] > 0], key=lambda x: (-x[1], x[0])); sell = sorted([x for x in ch if x[1] < 0], key=lambda x: (x[1], x[0]))
        gb = sum(x[1] for x in buy); gs = sum(x[1] for x in sell)
        tot = dict(window=label, rank_type="TOTAL", rank="", country_code="ALL", country="all reporters, carry-forward basis", start_month=a, end_month=b,
                   start_t=sum(x[2] for x in ch), end_t=sum(x[3] for x in ch), change_t=gb + gs, share_of_gross_buying_pct="", last_report_month="",
                   n_buyers=len(buy), n_sellers=len(sell), n_unchanged=len(ch) - len(buy) - len(sell), gross_buying_t=gb, gross_selling_t=gs,
                   top5_share_of_gross_buying_pct=pct(sum(x[1] for x in buy[:5]), gb))
        out.append(tot)
        for typ, lst in (("BUYER", buy), ("SELLER", sell)):
            for n, x in enumerate(lst[:k], 1):
                out.append(dict(window=label, rank_type=typ, rank=n, country_code=x[0], country=INSTITUTIONS.get(x[0]) or names.get(x[0]) or x[0],
                                start_month=a, end_month=b, start_t=x[2], end_t=x[3], change_t=x[1],
                                share_of_gross_buying_pct=pct(x[1], gb) if typ == "BUYER" else pct(x[1], gs), last_report_month=x[4]))
    return out


# ------------------------------------------------------------------------------------------------ main build
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--offline", action="store_true", help="rebuild from the saved raw files; no network")
    a = ap.parse_args()
    print("Gold tonnes ledger" + (" (offline, from the saved raw files)" if a.offline else ""))
    if a.offline: verify_raw()
    else: pull()

    # ---- load everything from the saved raw files (the only path to the data, online or offline)
    rgv = parse_imf(rd(os.path.join(RAWG, "imf_il_rgv_revs_all.xml")), "RGV_REVS")
    names = parse_codelist(rd(os.path.join(RAWG, "imf_cl_country.xml")))
    mv = parse_imf(rd(os.path.join(RAWG, "imf_il_rgoldmv_revs_world.xml")), "RGOLDMV_REVS")[("G001", "XDR")]
    tr = parse_imf(rd(os.path.join(RAWG, "imf_il_trgmv_revs_world.xml")), "TRGMV_REVS")
    usd_per_xdr = {m: tr[("G001", "USD")][m] / tr[("G001", "XDR")][m] for m in tr[("G001", "USD")] if m in tr[("G001", "XDR")]}
    imf = build_official(rgv, names)
    g001 = rgv[("G001", "FTO")]; gx010 = rgv[("GX010", "FTO")]
    safe = parse_safe(); gld = parse_gld(); iau = parse_iau(); iau_page = parse_iau_page(); gld_live = parse_gld_live(); lbma = parse_lbma()
    wgc_pub, wgc_rows = {}, {}
    for r in WGC_RELEASES: wgc_pub[r], wgc_rows[r] = parse_wgc_release(r)
    assert [wgc_pub[r] for r in WGC_RELEASES] == sorted(wgc_pub.values()), "WGC releases are not in publication order"
    etf_prose = parse_wgc_etf_page()
    months = imf["months"]; rows = imf["rows"]; M = {m: i for i, m in enumerate(months)}
    last_imf = imf["last"]

    # ---- checks on the official sector
    gm = sorted(g001); worst = []
    for p, q in zip(gm, gm[1:]):
        if mdiff(p, q) == 1 and q in rows:
            worst.append((abs((g001[q] - g001[p]) / OZ - rows[q]["change_oz"] / OZ), q))
    worst.sort(reverse=True)
    assert worst[0][0] < 0.35, f"reporters' cf change departs from the IMF G001 change by {worst[0]}"
    n_exact = sum(1 for d, _ in worst if d < 0.01)
    assert all(abs(g001[m] - gx010[m] - rgv[("IMF", "FTO")].get(m, 0) - rgv[("BIS", "FTO")].get(m, 0)) < 5 for m in g001 if m in gx010 and m in rgv[("IMF", "FTO")] and m in rgv[("BIS", "FTO")]), "G001 != GX010 + IMF + BIS"
    gap_const = {m: (g001[m] - rows[m]["cf_total_oz"]) / OZ for m in gm if m in rows}
    # China: IMF path vs SAFE's own release
    chn = imf["series"]["CHN"]; both = sorted(m for m in chn if m in safe)
    diffs = [(chn[m] - safe[m]) for m in both]
    china_maxdiff = max(abs(d) for d in diffs); china_exact = sum(1 for d in diffs if d == 0)
    assert china_maxdiff <= 10000, "IMF China departs from SAFE by more than SAFE's 10,000 oz rounding"
    safe_months = sorted(safe); safe_missing = [m for m in mrange(safe_months[0], safe_months[-1]) if m not in safe]
    spikes = []                                                     # one-month jumps that reverse next month (data-quality scan)
    for (c, u), d in rgv.items():
        if AGG.match(c): continue
        ms_ = sorted(d)
        for i_ in range(1, len(ms_) - 1):
            a_, b_, e_ = ms_[i_ - 1], ms_[i_], ms_[i_ + 1]
            if mdiff(a_, b_) != 1 or mdiff(b_, e_) != 1: continue
            up, back = (d[b_] - d[a_]) / OZ, (d[e_] - d[b_]) / OZ
            if abs(up) >= 3 and abs(back) >= 0.8 * abs(up) and up * back < 0: spikes.append((abs(up), c, b_, up, back))
    spikes.sort(reverse=True)
    # ---- ETF monthly series
    gdays = sorted(gld)
    for d in gdays:
        if d >= "2018-12-01": assert abs(gld[d]["tonnes"] - gld[d]["ounces"] / OZ) < 0.02, f"GLD tonnes != ounces/OZ on {d}"
    iau_t = {}                                    # daily reconstructed IAU tonnes
    for d in sorted(iau):
        if d in gld: nav, sh = iau[d]; iau_t[d] = sh * nav / gld[d]["price"] / OZ
    iau_alt = {d: iau[d][1] * iau[d][0] / gld[d]["price_tot"] / OZ for d in iau if d in gld}
    ld = max(iau_t); assert ld == iau_page["date"] == max(gld) == gld_live["date"], (ld, iau_page["date"], max(gld), gld_live["date"])
    assert abs(gld[ld]["tonnes"] - gld_live["tonnes"]) < 0.005 and abs(gld[ld]["price"] - gld_live["pm_fix"]) < 0.01, "GLD archive disagrees with the sponsor's live feed"
    iau_err = 100.0 * (iau_t[ld] / iau_page["tonnes"] - 1.0); iau_err_alt = 100.0 * (iau_alt[ld] / iau_page["tonnes"] - 1.0)
    assert abs(iau_err) < 0.1, f"IAU reconstruction is {iau_err:+.3f}% from the page"
    def month_end_series(daily, key=None):
        out = {}
        for d in sorted(daily):
            if mend(d[:7]) <= max(gld):                                   # a month still running (October to date) is not a month end
                out[d[:7]] = (d, daily[d] if key is None else daily[d][key])
        return out
    gme = month_end_series(gld, "tonnes"); ime = month_end_series(iau_t); pme = month_end_series(gld, "price")
    # daily reconstruction noise (IAU ounces per share should fall ~0.25% a year)
    ozps = {d: iau_t[d] * OZ / iau[d][1] for d in iau_t if d >= "2019-01-01"}; od = sorted(ozps)
    chg = [ozps[b] / ozps[a] - 1.0 for a, b in zip(od, od[1:])]
    iau_noise = (math.sqrt(sum(x * x for x in chg) / len(chg)) * 100, max(abs(x) for x in chg) * 100)
    last_month = max(last_imf, max(gme), max(lbma), safe_months[-1])
    ledger_months = mrange(LEDGER_START, last_month)

    # ---- value of world official gold (IMF, XDR)
    price_xdr = {m: mv[m] / g001[m] for m in g001 if m in mv}            # XDR per oz
    val = {}
    for m in sorted(g001):
        if m in mv and madd(m, -1) in g001 and madd(m, -1) in mv:
            p = madd(m, -1); q0, q1, p0, p1 = g001[p], g001[m], price_xdr[p], price_xdr[m]
            val[m] = dict(vol=(q1 - q0) * (p0 + p1) / 2 / 1e9, price=(p1 - p0) * (q0 + q1) / 2 / 1e9)
            assert abs(val[m]["vol"] + val[m]["price"] - (mv[m] - mv[p]) / 1e9) < 1e-6
    usd_check = {}
    for m in sorted(g001):
        if m in mv and m in usd_per_xdr and m in pme and m <= "2026-08":
            usd_check[m] = 100.0 * ((g001[m] * pme[m][1] / 1e9) / (mv[m] * usd_per_xdr[m] / 1e9) - 1.0)

    # ---- the monthly ledger
    china_best = {}; china_src = {}                      # SAFE where it has the month, else the IMF path (observed, or carried forward)
    for m in [madd(LEDGER_START, -1)] + ledger_months:
        if m in safe: china_best[m], china_src[m] = safe[m], "SAFE"
        elif m in M and imf["L"]["CHN"][M[m]] is not None:
            china_best[m], china_src[m] = imf["L"]["CHN"][M[m]], ("IMF" if m in chn else "IMF carried forward")
    mledger = []
    for m in ledger_months:
        pm = madd(m, -1); r = rows.get(m); rp = rows.get(pm); row = dict(month=m)
        row["imf_world_g001_t"] = g001[m] / OZ if m in g001 else None
        row["imf_world_g001_change_t"] = (g001[m] - g001[pm]) / OZ if m in g001 and pm in g001 else None
        if r:
            row.update(official_reporters_cf_t=r["cf_total_oz"] / OZ, official_change_cf_t=r["change_oz"] / OZ,
                       official_change_countries_t=r["change_countries_oz"] / OZ, official_change_intl_inst_t=r["change_inst_oz"] / OZ,
                       official_change_lfl_t=r["lfl_oz"] / OZ, late_catchup_t=(r["change_oz"] - r["lfl_oz"]) / OZ,
                       reporters_fresh_n=r["fresh_n"], reporters_universe_n=r["universe_n"], fresh_stock_share_pct=100 * r["fresh_stock_share"],
                       stale_gt6m_t=r["stale_gt6_oz"] / OZ, top_buyer=r.get("top_buyer"), top_buyer_change_t=None if r.get("top_buyer_oz") is None else r["top_buyer_oz"] / OZ,
                       top_seller=r.get("top_seller"), top_seller_change_t=None if r.get("top_seller_oz") is None else r["top_seller_oz"] / OZ,
                       official_status="provisional" if r["fresh_n"] < PROVISIONAL_BELOW * r["universe_n"] else "reported")
        ci = imf["L"]["CHN"][M[m]] if m in M else None; ci_p = imf["L"]["CHN"][M[pm]] if pm in M else None
        row["china_imf_t"] = chn[m] / OZ if m in chn else None
        row["china_safe_t"] = safe[m] / OZ if m in safe else None
        if m in china_best and pm in china_best:
            row["china_best_t"] = china_best[m] / OZ; row["china_best_source"] = china_src[m]; row["china_change_t"] = (china_best[m] - china_best[pm]) / OZ
            adj = (china_best[m] - china_best[pm]) - (ci - ci_p)
            row["official_change_cf_china_safe_t"] = (r["change_oz"] + adj) / OZ if r and ci is not None and ci_p is not None else None
        if m in val:
            row.update(official_value_xdr_bn=mv[m] / 1e9, official_vol_effect_xdr_bn=val[m]["vol"], official_price_effect_xdr_bn=val[m]["price"])
        elif m in mv: row["official_value_xdr_bn"] = mv[m] / 1e9
        row["gold_price_usd_oz_me"] = pme[m][1] if m in pme else None
        row["gld_t"] = gme[m][1] if m in gme else None; row["iau_t"] = ime[m][1] if m in ime else None
        if m in gme and pm in gme: row["gld_change_t"] = gme[m][1] - gme[pm][1]
        if m in ime and pm in ime: row["iau_change_t"] = ime[m][1] - ime[pm][1]
        row["gld_iau_change_t"] = add(row.get("gld_change_t"), row.get("iau_change_t")) if "gld_change_t" in row and "iau_change_t" in row else None
        if m in lbma:
            row["lbma_vault_t"] = lbma[m] / OZ
            if pm in lbma: row["lbma_vault_change_t"] = (lbma[m] - lbma[pm]) / OZ
        mledger.append(row)
    MF = ["month", "imf_world_g001_t", "imf_world_g001_change_t", "official_reporters_cf_t", "official_change_cf_t", "official_change_countries_t",
          "official_change_intl_inst_t", "official_change_lfl_t", "late_catchup_t", "official_change_cf_china_safe_t", "reporters_fresh_n",
          "reporters_universe_n", "fresh_stock_share_pct", "stale_gt6m_t", "official_status", "top_buyer", "top_buyer_change_t", "top_seller", "top_seller_change_t", "china_imf_t", "china_safe_t", "china_best_t",
          "china_best_source", "china_change_t", "gld_t", "gld_change_t", "iau_t", "iau_change_t", "gld_iau_change_t", "gold_price_usd_oz_me",
          "lbma_vault_t", "lbma_vault_change_t", "official_value_xdr_bn", "official_vol_effect_xdr_bn", "official_price_effect_xdr_bn"]
    MND = {"official_value_xdr_bn": 2, "official_vol_effect_xdr_bn": 2, "official_price_effect_xdr_bn": 2, "fresh_stock_share_pct": 1, "gold_price_usd_oz_me": 2}
    MF_PUBLIC = [c for c in MF if not re.match(r"(gld|iau|lbma|gold_price)", c)]          # IMF and SAFE columns only
    write_csv(os.path.join(DERIVED, "ledger_monthly_full.csv"), MF, mledger, nd=MND)
    write_csv(os.path.join(GOLD, "ledger_monthly.csv"), MF_PUBLIC, mledger, nd=MND)
    byM = {r["month"]: r for r in mledger}

    # ---- WGC: latest and first vintage of every quarter and year
    latest, first, first_rel, latest_rel = {}, {}, {}, {}
    for rel in WGC_RELEASES:
        for p, line, v in wgc_rows[rel]:
            latest[(p, line)] = v; latest_rel[(p, line)] = rel
            if (p, line) not in first: first[(p, line)] = v; first_rel[(p, line)] = rel
    parsed = [dict(release=rel, published=wgc_pub[rel], period=p, line=l, value=v) for rel in WGC_RELEASES for p, l, v in wgc_rows[rel]]
    write_csv(os.path.join(DERIVED, "wgc_gdt_table_parsed.csv"), ["release", "published", "period", "line", "value"], parsed, nd={"value": 1})
    wq = sorted({p for p, _ in latest if p[0] != "Y"}); wy = sorted({p for p, _ in latest if p[0] == "Y"})
    # identity check on every (period, release): total demand = fabrication + technology + bar and coin + ETFs + central banks + OTC
    for rel in WGC_RELEASES:
        d = {}
        for p, l, v in wgc_rows[rel]: d.setdefault(p, {})[l] = v
        for p, x in d.items():
            parts = [x.get(k) for k in ("jewellery_fabrication", "technology", "bar_coin", "etf", "central_banks", "otc_other")]
            if None in parts or "total_demand" not in x: continue
            assert abs(sum(parts) - x["total_demand"]) < 1.0, f"WGC identity fails {rel} {p}: {sum(parts):.1f} vs {x['total_demand']}"
            if "total_supply" in x: assert abs(x["total_supply"] - x["total_demand"]) < 1.0, f"WGC supply != demand {rel} {p}"

    # ---- the quarterly reconciliation
    quarters = [qof(m) for m in ledger_months if int(m[5:7]) % 3 == 0]
    if qof(ledger_months[-1]) not in quarters: quarters.append(qof(ledger_months[-1]))
    qrows = []
    def qsum(q, key):
        vals = [byM[m].get(key) for m in mrange(madd(qend(q), -2), qend(q)) if m in byM]
        return sum(vals) if len(vals) == 3 and None not in vals else None
    def qlast(q, key):
        return byM.get(qend(q), {}).get(key)
    for q in quarters:
        e = qend(q); r = dict(quarter=q, quarter_end_month=e)
        r["imf_world_g001_change_t"] = qsum(q, "imf_world_g001_change_t")
        r["imf_official_change_t"] = qsum(q, "official_change_cf_t")
        r["imf_official_change_china_safe_t"] = qsum(q, "official_change_cf_china_safe_t")
        r["imf_late_catchup_t"] = qsum(q, "late_catchup_t")
        r["imf_countries_change_t"] = qsum(q, "official_change_countries_t"); r["imf_intl_inst_change_t"] = qsum(q, "official_change_intl_inst_t")
        r["china_change_t"] = qsum(q, "china_change_t")
        r["reporters_fresh_n"] = qlast(q, "reporters_fresh_n"); r["reporters_universe_n"] = qlast(q, "reporters_universe_n")
        r["fresh_stock_share_pct"] = qlast(q, "fresh_stock_share_pct"); r["official_status"] = qlast(q, "official_status")
        r["gld_change_t"] = qsum(q, "gld_change_t"); r["iau_change_t"] = qsum(q, "iau_change_t"); r["gld_iau_change_t"] = qsum(q, "gld_iau_change_t")
        r["lbma_vault_change_t"] = qsum(q, "lbma_vault_change_t")
        cb, et = latest.get((q, "central_banks")), latest.get((q, "etf"))
        if q == "2026Q3" and et is None and etf_prose["q3_change_t"] is not None: et = etf_prose["q3_change_t"]; r["wgc_etf_source"] = "WGC ETF page prose, 7 Oct 2026"
        elif et is not None: r["wgc_etf_source"] = "GDT " + latest_rel[(q, "etf")]
        r["wgc_central_banks_t"] = cb; r["wgc_central_banks_first_release_t"] = first.get((q, "central_banks"))
        r["wgc_central_banks_first_release"] = first_rel.get((q, "central_banks"), "")
        r["wgc_central_banks_latest_release"] = latest_rel.get((q, "central_banks"), "")
        r["wgc_etf_t"] = et
        r["gap_wgc_minus_imf_t"] = sub(cb, r["imf_official_change_t"])
        r["gap_wgc_minus_imf_first_release_t"] = sub(r["wgc_central_banks_first_release_t"], r["imf_official_change_t"])
        r["gap_wgc_minus_imf_countries_t"] = sub(cb, r["imf_countries_change_t"])
        r["gap_share_of_wgc_pct"] = pct(r["gap_wgc_minus_imf_t"], cb)
        r["imf_share_of_wgc_pct"] = pct(r["imf_official_change_t"], cb)
        r["etf_gap_wgc_minus_gld_iau_t"] = sub(et, r["gld_iau_change_t"])
        r["gld_iau_share_of_wgc_etf_pct"] = pct(r["gld_iau_change_t"], et) if et is not None and abs(et) >= 20 else None
        for k, wl in (("wgc_bar_coin_t", "bar_coin"), ("wgc_jewellery_fabrication_t", "jewellery_fabrication"), ("wgc_technology_t", "technology"),
                      ("wgc_otc_other_t", "otc_other"), ("wgc_total_demand_t", "total_demand")):
            r[k] = latest.get((q, wl))
        r["wgc_lbma_price_usd_oz"] = latest.get((q, "lbma_price_usd_oz"))
        if cb is not None and et is not None and r["wgc_total_demand_t"] is not None: r["wgc_other_lines_t"] = r["wgc_total_demand_t"] - cb - et     # bar and coin + jewellery fabrication + technology + OTC and other
        if cb is not None and r["imf_official_change_t"] is not None and et is not None and r["gld_iau_change_t"] is not None and r["wgc_total_demand_t"] is not None:
            r["observed_t"] = r["imf_official_change_t"] + r["gld_iau_change_t"]
            r["observed_share_of_wgc_total_pct"] = pct(r["observed_t"], r["wgc_total_demand_t"])
            r["resid_check_t"] = (r["imf_official_change_t"] + r["gld_iau_change_t"] + r["gap_wgc_minus_imf_t"] + r["etf_gap_wgc_minus_gld_iau_t"]
                                  + r["wgc_bar_coin_t"] + r["wgc_jewellery_fabrication_t"] + r["wgc_technology_t"] + r["wgc_otc_other_t"]) - r["wgc_total_demand_t"]
            assert abs(r["resid_check_t"]) < 1.0, (q, r["resid_check_t"])
        # value split of world official gold, from the monthly pieces
        ms = mrange(madd(e, -2), e)
        if all(m in val for m in ms):
            r["official_value_xdr_bn_end"] = mv[e] / 1e9
            r["official_value_change_xdr_bn"] = (mv[e] - mv[madd(e, -3)]) / 1e9
            r["official_vol_effect_xdr_bn"] = sum(val[m]["vol"] for m in ms); r["official_price_effect_xdr_bn"] = sum(val[m]["price"] for m in ms)
            r["official_price_share_pct"] = pct(r["official_price_effect_xdr_bn"], r["official_value_change_xdr_bn"]) if abs(r["official_value_change_xdr_bn"]) >= 50 else None
        qrows.append(r)
    QF = ["quarter", "quarter_end_month", "imf_world_g001_change_t", "imf_official_change_t", "imf_countries_change_t", "imf_intl_inst_change_t",
          "imf_official_change_china_safe_t", "imf_late_catchup_t", "china_change_t", "reporters_fresh_n", "reporters_universe_n", "fresh_stock_share_pct", "official_status",
          "wgc_central_banks_t", "wgc_central_banks_first_release_t", "wgc_central_banks_first_release", "wgc_central_banks_latest_release",
          "gap_wgc_minus_imf_t", "gap_wgc_minus_imf_first_release_t", "gap_wgc_minus_imf_countries_t", "gap_share_of_wgc_pct", "imf_share_of_wgc_pct",
          "gld_change_t", "iau_change_t", "gld_iau_change_t", "wgc_etf_t", "wgc_etf_source", "etf_gap_wgc_minus_gld_iau_t", "gld_iau_share_of_wgc_etf_pct",
          "wgc_bar_coin_t", "wgc_jewellery_fabrication_t", "wgc_technology_t", "wgc_otc_other_t", "wgc_total_demand_t", "wgc_lbma_price_usd_oz",
          "observed_t", "observed_share_of_wgc_total_pct", "resid_check_t", "lbma_vault_change_t",
          "official_value_xdr_bn_end", "official_value_change_xdr_bn", "official_vol_effect_xdr_bn", "official_price_effect_xdr_bn", "official_price_share_pct"]
    QND = {"gap_share_of_wgc_pct": 1, "imf_share_of_wgc_pct": 1, "gld_iau_share_of_wgc_etf_pct": 1, "observed_share_of_wgc_total_pct": 1, "fresh_stock_share_pct": 1,
           "official_value_xdr_bn_end": 1, "official_value_change_xdr_bn": 1, "official_vol_effect_xdr_bn": 1, "official_price_effect_xdr_bn": 1, "official_price_share_pct": 1,
           "wgc_lbma_price_usd_oz": 1}
    QF_LOCAL_ONLY = {"wgc_bar_coin_t", "wgc_jewellery_fabrication_t", "wgc_technology_t", "wgc_otc_other_t", "wgc_total_demand_t", "wgc_lbma_price_usd_oz", "resid_check_t", "lbma_vault_change_t"}
    QF = QF[:QF.index("observed_t")] + ["wgc_other_lines_t"] + QF[QF.index("observed_t"):]
    write_csv(os.path.join(DERIVED, "ledger_quarterly_reconciliation_full.csv"), QF, qrows, nd=QND)
    write_csv(os.path.join(GOLD, "ledger_quarterly_reconciliation.csv"), [c for c in QF if c not in QF_LOCAL_ONLY], qrows, nd=QND)
    qd = {r["quarter"]: r for r in qrows}

    # ---- annual reconciliation (calendar years; 2026 H1 is the window the WGC covers; 2026 YTD runs to the latest month)
    ytd_end = last_month
    wins = [(str(y), f"{y - 1}-12", f"{y}-12") for y in range(2019, 2026)] + [("2026H1", "2025-12", "2026-06"), ("2026YTD", "2025-12", ytd_end)]
    def msum(a, b, key):
        vals = [byM[m].get(key) for m in mrange(madd(a, 1), b) if m in byM]
        return sum(vals) if vals and None not in vals else None
    arows = []
    gld_daily = sorted(gld); gl = lambda d: gld[d]["tonnes"]
    for label, a, b in wins:
        r = dict(period=label, start_month_end=a, end_month_end=b)
        for k_out, k in (("imf_world_g001_change_t", "imf_world_g001_change_t"), ("imf_official_change_t", "official_change_cf_t"), ("imf_official_countries_t", "official_change_countries_t"),
                         ("imf_official_intl_inst_t", "official_change_intl_inst_t"), ("imf_official_change_china_safe_t", "official_change_cf_china_safe_t"),
                         ("imf_late_catchup_t", "late_catchup_t"), ("china_change_t", "china_change_t"), ("gld_change_t", "gld_change_t"), ("iau_change_t", "iau_change_t"),
                         ("gld_iau_change_t", "gld_iau_change_t"), ("lbma_vault_change_t", "lbma_vault_change_t")):
            r[k_out] = msum(a, b, k)
        r["fresh_stock_share_pct_end"] = byM[b].get("fresh_stock_share_pct"); r["reporters_fresh_n_end"] = byM[b].get("reporters_fresh_n")
        r["official_status_end"] = byM[b].get("official_status")
        qs = [qof(m) for m in mrange(madd(a, 1), b) if int(m[5:7]) % 3 == 0]
        full = len(qs) == (mdiff(a, b) // 3) and mdiff(a, b) % 3 == 0 and all(q in qd and qd[q].get("wgc_central_banks_t") is not None for q in qs)
        def qs_sum(key):
            return sum(qd[q][key] for q in qs) if full and all(qd[q].get(key) is not None for q in qs) else None
        r["wgc_central_banks_t"] = qs_sum("wgc_central_banks_t"); r["wgc_central_banks_first_release_t"] = qs_sum("wgc_central_banks_first_release_t")
        r["wgc_central_banks_fy_published_t"] = latest.get((f"Y{label}", "central_banks")) if label.isdigit() else None
        r["wgc_etf_t"] = qs_sum("wgc_etf_t")
        r["gap_wgc_minus_imf_t"] = sub(r["wgc_central_banks_t"], r["imf_official_change_t"])
        r["gap_wgc_fy_published_minus_imf_t"] = sub(r["wgc_central_banks_fy_published_t"], r["imf_official_change_t"])
        r["gap_wgc_minus_imf_countries_t"] = sub(r["wgc_central_banks_t"], r["imf_official_countries_t"])
        r["gap_share_of_wgc_pct"] = pct(r["gap_wgc_minus_imf_t"], r["wgc_central_banks_t"])
        r["imf_share_of_wgc_pct"] = pct(r["imf_official_change_t"], r["wgc_central_banks_t"])
        r["etf_gap_wgc_minus_gld_iau_t"] = sub(r["wgc_etf_t"], r["gld_iau_change_t"])
        r["gld_iau_share_of_wgc_etf_pct"] = pct(r["gld_iau_change_t"], r["wgc_etf_t"]) if r["wgc_etf_t"] is not None and abs(r["wgc_etf_t"]) >= 20 else None
        for k in ("wgc_bar_coin_t", "wgc_jewellery_fabrication_t", "wgc_technology_t", "wgc_otc_other_t", "wgc_total_demand_t", "wgc_other_lines_t"):
            r[k] = qs_sum(k)
        if r["wgc_total_demand_t"] is not None:
            r["observed_t"] = r["imf_official_change_t"] + r["gld_iau_change_t"]; r["observed_share_of_wgc_total_pct"] = pct(r["observed_t"], r["wgc_total_demand_t"])
        # value split: sums of monthly pieces
        ms = mrange(madd(a, 1), b)
        if a in mv and b in mv and all(m in val for m in ms):
            r["official_value_xdr_bn_end"] = mv[b] / 1e9; r["official_value_change_xdr_bn"] = (mv[b] - mv[a]) / 1e9
            r["official_vol_effect_xdr_bn"] = sum(val[m]["vol"] for m in ms); r["official_price_effect_xdr_bn"] = sum(val[m]["price"] for m in ms)
            r["official_price_share_pct"] = pct(r["official_price_effect_xdr_bn"], r["official_value_change_xdr_bn"])
        # GLD + IAU assets: daily chain of volume and price pieces
        da, db = max(d for d in gld_daily if d[:7] <= a), max(d for d in gld_daily if d[:7] <= b)
        days = [d for d in gld_daily if da <= d <= db and d in iau_t]; vol = pr = 0.0
        for p_, q_ in zip(days, days[1:]):
            t0 = gld[p_]["tonnes"] + iau_t[p_]; t1 = gld[q_]["tonnes"] + iau_t[q_]; p0, p1 = gld[p_]["price"], gld[q_]["price"]
            vol += (t1 - t0) * OZ * (p0 + p1) / 2 / 1e9; pr += (p1 - p0) * (t0 + t1) / 2 * OZ / 1e9
        r["gld_iau_aum_end_usd_bn"] = (gld[days[-1]]["tonnes"] + iau_t[days[-1]]) * OZ * gld[days[-1]]["price"] / 1e9
        r["gld_iau_aum_change_usd_bn"] = vol + pr; r["gld_iau_aum_flow_effect_usd_bn"] = vol; r["gld_iau_aum_price_effect_usd_bn"] = pr
        r["gld_iau_aum_price_share_pct"] = pct(pr, vol + pr) if abs(vol + pr) >= 5 else None
        r["gld_iau_aum_last_day"] = days[-1]
        arows.append(r)
    AF = ["period", "start_month_end", "end_month_end", "imf_world_g001_change_t", "imf_official_change_t", "imf_official_countries_t", "imf_official_intl_inst_t",
          "imf_official_change_china_safe_t", "imf_late_catchup_t", "reporters_fresh_n_end", "fresh_stock_share_pct_end", "official_status_end", "china_change_t",
          "wgc_central_banks_t", "wgc_central_banks_first_release_t", "wgc_central_banks_fy_published_t", "gap_wgc_minus_imf_t", "gap_wgc_fy_published_minus_imf_t", "gap_wgc_minus_imf_countries_t",
          "gap_share_of_wgc_pct", "imf_share_of_wgc_pct", "gld_change_t", "iau_change_t", "gld_iau_change_t", "wgc_etf_t", "etf_gap_wgc_minus_gld_iau_t",
          "gld_iau_share_of_wgc_etf_pct", "wgc_bar_coin_t", "wgc_jewellery_fabrication_t", "wgc_technology_t", "wgc_otc_other_t", "wgc_total_demand_t", "wgc_other_lines_t",
          "observed_t", "observed_share_of_wgc_total_pct", "lbma_vault_change_t", "official_value_xdr_bn_end", "official_value_change_xdr_bn",
          "official_vol_effect_xdr_bn", "official_price_effect_xdr_bn", "official_price_share_pct", "gld_iau_aum_last_day", "gld_iau_aum_end_usd_bn",
          "gld_iau_aum_change_usd_bn", "gld_iau_aum_flow_effect_usd_bn", "gld_iau_aum_price_effect_usd_bn", "gld_iau_aum_price_share_pct"]
    AF_LOCAL_ONLY = {"wgc_bar_coin_t", "wgc_jewellery_fabrication_t", "wgc_technology_t", "wgc_otc_other_t", "wgc_total_demand_t", "lbma_vault_change_t"}
    AND = {k: 1 for k in ("gap_share_of_wgc_pct", "imf_share_of_wgc_pct", "gld_iau_share_of_wgc_etf_pct", "observed_share_of_wgc_total_pct", "fresh_stock_share_pct_end",
                                 "official_value_xdr_bn_end", "official_value_change_xdr_bn", "official_vol_effect_xdr_bn", "official_price_effect_xdr_bn", "official_price_share_pct",
                                 "gld_iau_aum_end_usd_bn", "gld_iau_aum_change_usd_bn", "gld_iau_aum_flow_effect_usd_bn", "gld_iau_aum_price_effect_usd_bn", "gld_iau_aum_price_share_pct")}
    write_csv(os.path.join(DERIVED, "ledger_annual_reconciliation_full.csv"), AF, arows, nd=AND)
    write_csv(os.path.join(GOLD, "ledger_annual_reconciliation.csv"), [c for c in AF if c not in AF_LOCAL_ONLY], arows, nd=AND)
    ad = {r["period"]: r for r in arows}

    # ---- value split from end-2023 to the latest IMF month (headline window) and to the latest quarter end
    v_end = max(m for m in val)
    win_val = {}
    for label, a, b in (("end-2023 to " + v_end, "2023-12", v_end), ("end-2023 to 2026-06", "2023-12", "2026-06")):
        ms = mrange(madd(a, 1), b); vol = sum(val[m]["vol"] for m in ms); pr = sum(val[m]["price"] for m in ms)
        q0, q1, p0, p1 = g001[a], g001[b], price_xdr[a], price_xdr[b]
        one_vol = (q1 - q0) * (p0 + p1) / 2 / 1e9; one_pr = (p1 - p0) * (q0 + q1) / 2 / 1e9
        win_val[label] = dict(a=a, b=b, v0=mv[a] / 1e9, v1=mv[b] / 1e9, dv=(mv[b] - mv[a]) / 1e9, vol=vol, price=pr, one_vol=one_vol, one_price=one_pr,
                              dt=(q1 - q0) / OZ, t0=q0 / OZ, t1=q1 / OZ, p0=p0, p1=p1)

    # ---- by-country movers
    mov_wins = [(str(y), f"{y - 1}-12", f"{y}-12") for y in range(2019, 2026)] + [("2026YTD", "2025-12", last_imf), ("since_end2023", "2023-12", last_imf),
                (f"last12m_to_{last_imf}", madd(last_imf, -12), last_imf)]
    movers = top_movers(imf, names, mov_wins)
    for mrow in movers:               # China only: the change over the same window on SAFE's release (IMF fills Dec 2024), which runs to 2026-09
        if mrow["country_code"] == "CHN" and mrow["start_month"] in china_best and mrow["end_month"] in china_best:
            mrow["china_safe_based_change_t"] = (china_best[mrow["end_month"]] - china_best[mrow["start_month"]]) / OZ
    MVF = ["window", "rank_type", "rank", "country_code", "country", "start_month", "end_month", "start_t", "end_t", "change_t", "share_of_gross_buying_pct",
           "last_report_month", "china_safe_based_change_t", "n_buyers", "n_sellers", "n_unchanged", "gross_buying_t", "gross_selling_t", "top5_share_of_gross_buying_pct"]
    write_csv(os.path.join(GOLD, "official_by_country_changes.csv"), MVF, movers, nd={"share_of_gross_buying_pct": 1, "top5_share_of_gross_buying_pct": 1})

    # ---- history files (two columns, as_of,value)
    write_hist("official_world_tonnes", [(mend(m), g001[m] / OZ) for m in gm])
    cb_m = sorted(m for m in set(safe) | set(chn))
    write_hist("china_tonnes", [(mend(m), (safe[m] if m in safe else chn[m]) / OZ) for m in cb_m])
    write_hist("gld_tonnes", [(d, gld[d]["tonnes"]) for d in gdays if d >= "2004-11-18"], 2, DERIVED)         # LOCAL only (sponsor data)
    write_hist("iau_tonnes", [(d, iau_t[d]) for d in sorted(iau_t)], 3, DERIVED)
    write_hist("lbma_vault_tonnes", [(mend(m), lbma[m] / OZ) for m in sorted(lbma)], 3, DERIVED)

    # ================================================================================== the printout
    P = lambda *x: print(*x)
    P(f"\nvalidated. IMF: {len(imf['reporters'])} reporter series (incl. 4 institutions) + {len(rgv) - len(imf['reporters'])} aggregates; {imf['months'][0]} to {last_imf}; "
      f"reporters' cf change vs G001 change: {n_exact} of {len(worst)} months identical to <0.01 t, worst {worst[0][0]:.3f} t ({worst[0][1]}); "
      f"G001 - reporters' cf level = {gap_const[ '2020-06']:.2f} t (constant from 2019-12)")
    P(f"  worst months vs G001: " + ", ".join(f"{m} {d:.3f} t" for d, m in worst[:4]))
    P(f"  China, IMF vs SAFE: {len(both)} common months {both[0]}..{both[-1]}; identical in {china_exact}; max |difference| {china_maxdiff:,.0f} oz = {china_maxdiff / OZ:.2f} t; SAFE months {safe_months[0]}..{safe_months[-1]}, missing in SAFE's files: {', '.join(safe_missing) or 'none'}")
    P(f"  GLD: {len(gld)} trading days {min(gld)}..{max(gld)}; IAU: {len(iau_t)} reconstructed days; LBMA vault: {len(lbma)} months {min(lbma)}..{max(lbma)}; "
      f"WGC releases parsed: {len(WGC_RELEASES)} ({wgc_pub[WGC_RELEASES[0]]}..{wgc_pub[WGC_RELEASES[-1]]}), quarters {wq[0]}..{wq[-1]}")
    sp_bis = [x for x in spikes if x[1] == "BIS"]; sp_oth = [x for x in spikes if x[1] != "BIS"]
    P(f"  spike-and-reverse scan (|jump| >= 3 t, >=80% reversed next month): {len(spikes)} cases, {len(sp_bis)} are BIS; others, largest first: " + "; ".join(f"{c} {m} {u:+.1f}/{b:+.1f} t" for _, c, m, u, b in sp_oth[:4]))
    P(f"  IAU reconstruction noise since 2019 (daily change in implied ounces/share): rms {iau_noise[0]:.4f}%, max {iau_noise[1]:.3f}%")
    P("\nSPOT CHECKS")
    cl = imf["L"]["CHN"][M["2026-06"]]; ch_last = max(safe)
    P(f"  China, SAFE {ch_last}: {safe[ch_last] / 1e6:.2f} m oz = {safe[ch_last] / OZ:.1f} t   (map: 77.47 m oz at end-Sep 2026).  IMF China last report {max(chn)}: {chn[max(chn)] / 1e6:.2f} m oz = {chn[max(chn)] / OZ:.1f} t; SAFE same month {safe[max(chn)] / 1e6:.2f} m oz")
    P(f"  GLD {ld}: archive {gld[ld]['tonnes']:.2f} t ({gld[ld]['ounces']:,.2f} oz) vs the sponsor's live feed {gld_live['tonnes']:.3f} t ({gld_live['ounces']:,.2f} oz), dated {gld_live['date']}; "
      f"archive-implied price ${gld[ld]['price']:.2f} vs the feed's PM fix ${gld_live['pm_fix']:.2f}")
    P(f"  IAU {ld}: reconstructed {iau_t[ld]:.2f} t vs page {iau_page['tonnes']:.2f} t ({iau_err:+.3f}%); with total-NAV/total-oz price {iau_alt[ld]:.2f} t ({iau_err_alt:+.3f}%); page ounces {iau_page['ounces']:,.2f}")
    P(f"  LBMA {max(lbma)}: {lbma[max(lbma)] / OZ:,.1f} t ({lbma[max(lbma)] / 1e6:,.1f} m oz)   map: 9,821 t")
    P(f"  IMF World G001 {gm[-1]}: {g001[gm[-1]] / OZ:,.1f} t   map: 36,919 t (Aug 2026)")

    def f1(x, w=8, nd=1):
        return " " * (w - 1) + "-" if x is None else f"{x:{w},.{nd}f}"
    P("\nREPORTERS PER MONTH (IMF IL gold volume; universe = reporters with any observation since " + UNIVERSE_FROM + ")")
    P("month    fresh/universe  fresh_stock%  carried_flat>6m_t  status       cf_change_t  lfl_change_t  late_catchup_t  G001_change_t")
    for m in mrange(madd(last_imf, -14), last_imf):
        r = byM[m]; P(f"{m}   {r['reporters_fresh_n']:>4}/{r['reporters_universe_n']:<4}      {r['fresh_stock_share_pct']:6.1f}   {r['stale_gt6m_t']:12,.0f}      {r['official_status']:<11} {f1(r['official_change_cf_t'], 10)} {f1(r['official_change_lfl_t'], 12)} {f1(r['late_catchup_t'], 14)} {f1(r['imf_world_g001_change_t'], 13)}")

    P("\nTONNES ADDED BY EACH COMPONENT (t; window = month-end to month-end)")
    cols = ["2023", "2024", "2025", "2026H1", "2026YTD"]
    P(f"{'component':<64}" + "".join(f"{c:>10}" for c in cols))
    comp = [("IMF-reported official, all reporters, carry-forward (A)", "imf_official_change_t"), ("   of which countries", "imf_official_countries_t"),
            ("   of which IMF/BIS/ECB/BEAC", "imf_official_intl_inst_t"), ("   same, China replaced by SAFE's own release", "imf_official_change_china_safe_t"),
            ("   IMF World G001 change (cross-check)", "imf_world_g001_change_t"), ("   China (SAFE; IMF fills Dec 2024)", "china_change_t"), ("GAP vs IMF countries only (excl. IMF/BIS/ECB/BEAC)", "gap_wgc_minus_imf_countries_t"),
            ("WGC central banks & other inst. (latest vintage, sum of quarters)", "wgc_central_banks_t"), ("WGC central banks, annual as published in FY release", "wgc_central_banks_fy_published_t"),
            ("GAP: WGC central banks minus IMF-reported", "gap_wgc_minus_imf_t"), ("GLD", "gld_change_t"), ("IAU (reconstructed)", "iau_change_t"), ("GLD + IAU (B)", "gld_iau_change_t"),
            ("WGC global gold ETFs", "wgc_etf_t"), ("   GLD+IAU as % of WGC ETF change", "gld_iau_share_of_wgc_etf_pct"), ("WGC bar and coin", "wgc_bar_coin_t"),
            ("WGC jewellery fabrication", "wgc_jewellery_fabrication_t"), ("WGC technology", "wgc_technology_t"), ("WGC OTC and other (balancing item)", "wgc_otc_other_t"),
            ("WGC total demand (= total supply)", "wgc_total_demand_t"), ("LBMA London vault holdings (custody stock change, not purchases)", "lbma_vault_change_t")]
    for lab, k in comp:
        P(f"{lab:<64}" + "".join(f1(ad[c].get(k), 10) for c in cols))
    P(f"{'IMF coverage at window end: reporters fresh / stock fresh %':<64}" + "".join(f"{str(ad[c]['reporters_fresh_n_end']) + ' /' + format(ad[c]['fresh_stock_share_pct_end'], '.0f') + '%':>10}" for c in cols))
    P(f"{'IMF status at window end':<64}" + "".join(f"{ad[c]['official_status_end']:>10}" for c in cols))

    P("\nQUARTERLY RECONCILIATION (t). IMF = reporters' carry-forward change; gap = WGC central banks - IMF; ETF = GLD + IAU vs WGC global ETFs")
    P("quarter  status      fresh%  IMF_off  WGC_CB  WGC_CB(1st)  gap  gap%WGC | GLD   IAU   GLD+IAU  WGC_ETF  ETF_gap  cover% | WGC_total  observed%")
    for r in qrows:
        if r["quarter"] < "2022Q1": continue
        P(f"{r['quarter']}  {r['official_status'] or '':<11} {f1(r['fresh_stock_share_pct'], 5, 0)}  {f1(r['imf_official_change_t'], 7)} {f1(r['wgc_central_banks_t'], 7)} {f1(r['wgc_central_banks_first_release_t'], 9)} "
          f"{f1(r['gap_wgc_minus_imf_t'], 7)} {f1(r['gap_share_of_wgc_pct'], 6, 0)}% | {f1(r['gld_change_t'], 6)} {f1(r['iau_change_t'], 5)} {f1(r['gld_iau_change_t'], 7)} {f1(r['wgc_etf_t'], 7)} {f1(r['etf_gap_wgc_minus_gld_iau_t'], 7)} {f1(r['gld_iau_share_of_wgc_etf_pct'], 6, 0)}% | {f1(r['wgc_total_demand_t'], 8)} {f1(r.get('observed_share_of_wgc_total_pct'), 8, 0)}%")

    P("\nRESIDUAL TABLE (t): WGC total demand = IMF-reported official + GLD + IAU + central-bank gap + ETF gap + bar&coin + jewellery fabrication + technology + OTC&other")
    P(f"{'period':<8}{'IMF_off':>9}{'GLD':>8}{'IAU':>7}{'CB_gap':>8}{'ETF_gap':>9}{'barcoin':>9}{'jewel':>8}{'tech':>7}{'OTC':>8}{'= total':>9}{'check':>7}  observed%  WGC-only%")
    for lab, d in [(r["quarter"], r) for r in qrows if r["quarter"] >= "2024Q1" and r.get("observed_t") is not None] + [(c, ad[c]) for c in ("2024", "2025", "2026H1")]:
        tot = d.get("wgc_total_demand_t"); parts = [d.get("imf_official_change_t"), d.get("gld_change_t"), d.get("iau_change_t"), d.get("gap_wgc_minus_imf_t"), d.get("etf_gap_wgc_minus_gld_iau_t"),
                                                     d.get("wgc_bar_coin_t"), d.get("wgc_jewellery_fabrication_t"), d.get("wgc_technology_t"), d.get("wgc_otc_other_t")]
        wonly = pct(add(parts[5], parts[6], parts[7]), tot)
        P(f"{lab:<8}" + "".join(f1(x, w, 1) for x, w in zip(parts, (9, 8, 7, 8, 9, 9, 8, 7, 8))) + f1(tot, 9) + f1(sum(parts) - tot, 7) + f"  {f1(d.get('observed_share_of_wgc_total_pct'), 8, 0)}%  {f1(wonly, 8, 0)}%")

    P("\nVALUE OF WORLD OFFICIAL GOLD, IMF (XDR bn; G001 tonnes x IMF price; volume/price by monthly midpoint split)")
    for lab, w in win_val.items():
        P(f"  {lab}: value {w['v0']:,.0f} -> {w['v1']:,.0f} XDR bn = {w['dv']:+,.0f}; tonnes {w['t0']:,.0f} -> {w['t1']:,.0f} ({w['dt']:+,.0f} t); price {w['p0']:,.0f} -> {w['p1']:,.0f} XDR/oz ({100 * (w['p1'] / w['p0'] - 1):+.0f}%)")
        P(f"     volume {w['vol']:+,.1f} ({100 * w['vol'] / w['dv']:.1f}%), price {w['price']:+,.1f} ({100 * w['price'] / w['dv']:.1f}%) [monthly chain];  one-step midpoint: volume {w['one_vol']:+,.1f} ({100 * w['one_vol'] / w['dv']:.1f}%), price {w['one_price']:+,.1f} ({100 * w['one_price'] / w['dv']:.1f}%)")
    P("  by year (XDR bn): period  value_end  change  volume  price  price%")
    for c in ("2024", "2025", "2026H1", "2026YTD"):
        d = ad[c]
        if d.get("official_value_change_xdr_bn") is not None:
            P(f"    {c:<8}{d['official_value_xdr_bn_end']:10,.0f}{d['official_value_change_xdr_bn']:9,.0f}{d['official_vol_effect_xdr_bn']:8,.1f}{d['official_price_effect_xdr_bn']:9,.1f}{d['official_price_share_pct']:7.1f}%")
    wm = {}
    for a_, b_ in (("2023-12", "2026-08"),):
        ms_ = mrange(madd(a_, 1), b_); vv = pp = 0.0
        for m_ in ms_:
            p_ = madd(m_, -1); q0, q1, p0, p1 = g001[p_] / OZ, g001[m_] / OZ, pme[p_][1], pme[m_][1]
            vv += (q1 - q0) * OZ * (p0 + p1) / 2 / 1e9; pp += (p1 - p0) * OZ * (q0 + q1) / 2 / 1e9
        P(f"  sensitivity, USD bn, G001 tonnes x GLD-implied month-end PM price, {a_} to {b_}: {g001[a_] / OZ * OZ * pme[a_][1] / 1e9:,.0f} -> {g001[b_] * pme[b_][1] / 1e9:,.0f}; volume {vv:+,.1f} ({100 * vv / (vv + pp):.1f}%), price {pp:+,.1f} ({100 * pp / (vv + pp):.1f}%)")
    P(f"  USD cross-check: tonnes x GLD-implied PM price vs IMF value x (USD/XDR from TRGMV): median {sorted(usd_check.values())[len(usd_check) // 2]:+.2f}%, range {min(usd_check.values()):+.2f}% to {max(usd_check.values()):+.2f}% over {len(usd_check)} months")
    P("\nGLD + IAU ASSETS (USD bn, tonnes x GLD-implied PM price; daily chain of flow and price pieces)")
    for c in ("2024", "2025", "2026YTD"):
        d = ad[c]; P(f"  {c:<8} to {d['gld_iau_aum_last_day']}: end {d['gld_iau_aum_end_usd_bn']:6,.1f}, change {d['gld_iau_aum_change_usd_bn']:+6.1f} = flows {d['gld_iau_aum_flow_effect_usd_bn']:+6.1f} + price {d['gld_iau_aum_price_effect_usd_bn']:+6.1f}")
    # end-2023 to latest daily
    dA = max(d for d in gld_daily if d[:7] <= "2023-12"); days = [d for d in gld_daily if dA <= d <= ld and d in iau_t]; vol = pr = 0.0
    for p_, q_ in zip(days, days[1:]):
        t0 = gld[p_]["tonnes"] + iau_t[p_]; t1 = gld[q_]["tonnes"] + iau_t[q_]; p0, p1 = gld[p_]["price"], gld[q_]["price"]
        vol += (t1 - t0) * OZ * (p0 + p1) / 2 / 1e9; pr += (p1 - p0) * (t0 + t1) / 2 * OZ / 1e9
    a0 = (gld[dA]["tonnes"] + iau_t[dA]) * OZ * gld[dA]["price"] / 1e9; a1 = (gld[ld]["tonnes"] + iau_t[ld]) * OZ * gld[ld]["price"] / 1e9
    P(f"  {dA} to {ld}: {a0:,.1f} -> {a1:,.1f} (+{a1 - a0:,.1f}) = flows {vol:+,.1f} ({100 * vol / (vol + pr):.0f}%) + price {pr:+,.1f} ({100 * pr / (vol + pr):.0f}%)   map: $84.7bn -> $204.1bn, flows 23%, price 77%")
    P(f"  holdings on {ld}: GLD {gld[ld]['tonnes']:,.1f} t + IAU {iau_t[ld]:,.1f} t = {gld[ld]['tonnes'] + iau_t[ld]:,.1f} t; WGC global ETF holdings end-Sep 2026 (page prose): {etf_prose['sep_holdings_t']:,.0f} t "
      f"-> GLD+IAU at end-Sep = {gme['2026-09'][1] + ime['2026-09'][1]:,.1f} t = {100 * (gme['2026-09'][1] + ime['2026-09'][1]) / etf_prose['sep_holdings_t']:.1f}% of it")

    P("\nTOP MOVERS (carry-forward basis, tonnes; full list in data/gold/official_by_country_changes.csv)")
    for w in ("2024", "2025", "2026YTD", "since_end2023"):
        sel = [m for m in movers if m["window"] == w]; tot = sel[0]
        P(f" {w}: net {tot['change_t']:+,.1f} t = buying {tot['gross_buying_t']:,.1f} ({tot['n_buyers']} reporters) - selling {-tot['gross_selling_t']:,.1f} ({tot['n_sellers']}); top-5 = {tot['top5_share_of_gross_buying_pct']:.0f}% of gross buying")
        P("    buyers: " + "; ".join(f"{m['country_code']} {m['change_t']:+.1f}" for m in sel if m["rank_type"] == "BUYER" and m["rank"] <= 6))
        P("    sellers: " + "; ".join(f"{m['country_code']} {m['change_t']:+.1f}" for m in sel if m["rank_type"] == "SELLER" and m["rank"] <= 5))
    stale = sorted(((imf["L"][c][M[last_imf]] / OZ, c, max(imf["series"][c])) for c in imf["reporters"] if imf["L"][c][M[last_imf]] is not None and imf["age"][c][M[last_imf]] > STALE_MONTHS), reverse=True)[:6]
    P("  carried flat for >6 months at " + last_imf + ": " + "; ".join(f"{c} {t:,.1f} t (last report {lm})" for t, c, lm in stale))
    P("  WGC vintages, Q1 2026 central banks: " + " -> ".join(f"{v}" for v in [first[('2026Q1', 'central_banks')], latest[('2026Q1', 'central_banks')]]) + " t")
    P(f"\nwrote PUBLIC: {len(mledger)} months in data/gold/ledger_monthly.csv, {len(qrows)} quarters in ledger_quarterly_reconciliation.csv, {len(arows)} periods in ledger_annual_reconciliation.csv, "
      f"{len(movers)} rows in official_by_country_changes.csv, 2 gold_*.csv files in data/history")
    P("wrote LOCAL (git-ignored): data/vintages/gold/derived/ - the _full tables, gold_gld_tonnes, gold_iau_tonnes, gold_lbma_vault_tonnes, wgc_gdt_table_parsed")


if __name__ == "__main__":
    main()
