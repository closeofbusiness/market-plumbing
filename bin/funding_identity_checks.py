#!/usr/bin/env python3
"""Rebuild the nominal-GDP and Z.1 figures quoted in _research/funding_identity_adversarial_reviews.md. Stdlib only.

  python3 bin/funding_identity_checks.py fetch [--date YYYYMMDD] [--only z1|bea]   (network; GET only)
  python3 bin/funding_identity_checks.py build [--date YYYYMMDD]                    (offline, deterministic)

fetch  Downloads, into data/vintages/funding_identity_checks/<date>/ :
         - the Z.1 CSV package (www.federalreserve.gov), release 20260611 if still archived, else the current release;
         - BEA NIPA flat files NipaDataQ.txt, NipaDataA.txt and the series register (apps.bea.gov).
       Hosts are whitelisted (anything else is refused, redirects included). Neutral project User-Agent, no contact
       details, GET only, >= 2 s between requests, at most 12 requests per run. A 403/429/block page stops that
       source; there is no retry and no change of identity. Every request is logged in requests_log.csv (no clock).
build  Reads only the files already on disk and writes data/funding_identity_checks/reconciliation.csv
       (the README.md in that folder is hand-written). Same inputs -> same bytes.
"""
import argparse, csv, glob, hashlib, io, os, sys, time, urllib.error, urllib.parse, urllib.request, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VINT = os.path.join(ROOT, "data", "vintages", "funding_identity_checks")
OUT = os.path.join(ROOT, "data", "funding_identity_checks")
UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
ALLOWED = ("www.federalreserve.gov", "apps.bea.gov")
MAX_REQ = 12
GAP_S = 2.0
Z1_URLS = [
    ("20260611", "https://www.federalreserve.gov/releases/z1/20260611/z1_csv_files.zip"),
    ("current", "https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip"),
]
BEA_URLS = [
    "https://apps.bea.gov/national/Release/TXT/NipaDataQ.txt",
    "https://apps.bea.gov/national/Release/TXT/NipaDataA.txt",
    "https://apps.bea.gov/national/Release/TXT/SeriesRegister.txt",
]


# ----------------------------------------------------------------------------- fetch
class Fetcher:
    def __init__(self, d):
        self.d, self.n, self.last = d, 0, 0.0
        self.rows = []
        os.makedirs(d, exist_ok=True)

    def get(self, url):
        """One GET. Returns (status, bytes). Stops the caller's source on 403/429 (raises Blocked)."""
        host = urllib.parse.urlparse(url).hostname
        if host not in ALLOWED:
            raise SystemExit(f"refusing {url}: host not allowed")
        if self.n >= MAX_REQ:
            raise SystemExit("request budget exhausted")
        wait = GAP_S - (time.monotonic() - self.last)
        if wait > 0:
            time.sleep(wait)
        self.n += 1
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        status, body = None, b""
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                if urllib.parse.urlparse(r.geturl()).hostname not in ALLOWED:
                    raise SystemExit(f"refusing: {url} redirected off the allowed hosts")
                status, body = r.status, r.read()
        except urllib.error.HTTPError as e:
            status = e.code
        self.last = time.monotonic()
        p = urllib.parse.urlparse(url)
        print(f"GET {p.hostname}{p.path} -> {status} {len(body)} bytes")
        self.rows.append((host, p.path, status, len(body), hashlib.sha256(body).hexdigest()))
        if status in (403, 429):
            raise Blocked(url, status)
        head = body[:300].lstrip().lower()
        if status == 200 and (head.startswith(b"<!doctype html") or head.startswith(b"<html")) and not url.endswith(".html"):
            raise Blocked(url, "html block page")
        return status, body

    def save_log(self):
        p = os.path.join(self.d, "requests_log.csv")
        new = not os.path.exists(p)
        with open(p, "a", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            if new:
                w.writerow(["host", "path", "status", "bytes", "sha256"])
            w.writerows(self.rows)


class Blocked(Exception):
    pass


def do_fetch(date, only):
    d = os.path.join(VINT, date)
    f = Fetcher(d)
    try:
        if only in (None, "z1"):
            for rel, url in Z1_URLS:
                try:
                    st, body = f.get(url)
                except Blocked as e:
                    print("STOPPED Z.1 source:", e.args)
                    break
                if st == 200:
                    open(os.path.join(d, "z1_csv_files.zip"), "wb").write(body)
                    open(os.path.join(d, "z1_release.txt"), "w").write(f"{rel}\n{url}\n")
                    break
                print(f"Z.1 {rel}: status {st}, trying next")
        if only in (None, "bea"):
            for url in BEA_URLS:
                try:
                    st, body = f.get(url)
                except Blocked as e:
                    print("STOPPED BEA source:", e.args)
                    break
                if st == 200:
                    open(os.path.join(d, os.path.basename(url)), "wb").write(body)
    finally:
        f.save_log()
    return 0


# ----------------------------------------------------------------------------- build
def latest_dir():
    ds = sorted(x for x in glob.glob(os.path.join(VINT, "*")) if os.path.isdir(x))
    if not ds:
        raise SystemExit("no data/vintages/funding_identity_checks/<date>/ directory; run fetch first")
    return ds[-1]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["fetch", "build"])
    ap.add_argument("--date")
    ap.add_argument("--only", choices=["z1", "bea"])
    a = ap.parse_args()
    if a.mode == "fetch":
        return do_fetch(a.date or time.strftime("%Y%m%d"), a.only)
    return do_build(a.date)


class Missing(Exception):
    pass


def load_z1(d):
    """All csv/*.csv members of the Z.1 zip -> {series code: {period: value in $bn}} (levels/flows are $ millions in the file)."""
    out, conflicts = {}, 0
    with zipfile.ZipFile(os.path.join(d, "z1_csv_files.zip")) as z:
        for name in sorted(n for n in z.namelist() if n.startswith("csv/") and n.endswith(".csv")):
            rows = list(csv.reader(io.StringIO(z.read(name).decode("utf-8-sig"))))
            hdr = rows[0]
            for j, code in enumerate(hdr[1:], 1):
                col = out.setdefault(code, {})
                for r in rows[1:]:
                    if j >= len(r) or r[j] in ("", "ND", "NA"):
                        continue
                    try:
                        x = float(r[j]) / 1000.0
                    except ValueError:
                        continue
                    if r[0] in col:
                        conflicts += 1 if abs(col[r[0]] - x) > 1e-9 else 0
                    else:
                        col[r[0]] = x
    return out, conflicts


def load_nipa(path):
    out = {}
    with open(path, newline="") as fh:
        for r in csv.reader(fh):
            if len(r) < 3 or r[0].startswith("%"):
                continue
            try:
                out.setdefault(r[0], {})[r[1]] = float(r[2].replace(",", "")) / 1000.0   # $ millions -> $bn
            except ValueError:
                pass
    return out


def fnum(x, dec):
    return f"{x:.{dec + 2}f}"


def status_of(q, r):
    """q: quoted string; r: re-derived value (float or str) or None. Returns (status, diff text, within-one-unit flag)."""
    if r is None:
        return "NOT FOUND", "", False
    if isinstance(r, str):
        return ("MATCH within rounding" if r == q else "DIFFERS"), "", False
    qv = float(q)
    dec = len(q.split(".")[1]) if "." in q else 0
    d = r - qv
    st = "MATCH within rounding" if abs(d) <= 0.5 * 10 ** (-dec) + 1e-9 else "DIFFERS"
    return st, f"diff {d:+.{dec + 2}f}", (st == "DIFFERS" and abs(d) < 10 ** (-dec))


Z4 = ["2025:Q2", "2025:Q3", "2025:Q4", "2026:Q1"]


def do_build(date):
    d = os.path.join(VINT, date) if date else latest_dir()
    stamp = os.path.basename(d)
    Z, conflicts = load_z1(d)
    NQ = load_nipa(os.path.join(d, "NipaDataQ.txt"))
    NA = load_nipa(os.path.join(d, "NipaDataA.txt"))
    rel = open(os.path.join(d, "z1_release.txt")).read().split("\n")[0]
    last_z = max(p for p, v in Z["FA106060005.Q"].items() if ":Q" in p)
    last_n = max(NQ["A191RC"], key=lambda p: (int(p[:4]), int(p[-1])))
    zrel = f"Z.1 release {rel[:4]}-{rel[4:6]}-{rel[6:]} (data to {last_z})"
    nrel = f"BEA NIPA flat files fetched {stamp} (data to {last_n}; later vintage than the note)"

    def zq(c, p):
        try:
            return Z[c][p]
        except KeyError:
            raise Missing(f"{c} {p}")

    def z4(c):
        return sum(zq(c, p) for p in Z4) / 4.0

    def za(c, y):     # calendar-year mean of the four SAAR quarters
        return sum(zq(c, f"{y}:Q{i}") for i in range(1, 5)) / 4.0

    def nq(c, p):
        try:
            return NQ[c][p]
        except KeyError:
            raise Missing(f"{c} {p}")

    def na(c, y):
        try:
            return NA[c][str(y)]
        except KeyError:
            raise Missing(f"{c} {y}")

    def n4(c):
        return sum(nq(c, p.replace(":", "")) for p in Z4) / 4.0

    G1 = lambda: nq("A191RC", "2026Q1")
    G4 = lambda: n4("A191RC")
    pct = lambda a, b: 100.0 * a / b

    rows = []

    def R(line, text, q, units, codes, fn, note="", src="z1"):
        assert len(text.split()) <= 15, text
        try:
            val = fn()
        except (Missing, KeyError, ZeroDivisionError) as e:
            val, note = None, (note + " " if note else "") + f"[not computable: {e}]"
        st, dtxt, unit1 = status_of(q, val)
        if unit1:
            dtxt += " (inside one unit of the last quoted digit: would match if the note truncated rather than rounded)"
        full = "; ".join(x for x in (dtxt, note) if x)
        rd = "" if val is None else (val if isinstance(val, str) else fnum(val, len(q.split(".")[1]) if "." in q else 0))
        rows.append([line, text, q, rd, units, codes, zrel if src == "z1" else (nrel if src == "bea" else zrel + " + " + nrel), st, full])

    SAAR = "$bn SAAR"
    T4 = "mean of the four quarters 2025:Q2-2026:Q1 (the note's 'trailing 4 quarters')"
    # ---- release identification (line 9)
    R(9, "Z.1 Financial Accounts, release 2026-06-11 (data through 2026:Q1)", "20260611 2026:Q1", "release id", "S11_1_t / z1_csv_files.zip",
      lambda: f"{rel} {last_z}", "zip fetched from /releases/z1/20260611/; the CSV package has no file named S11_a: the nonfinancial corporate rows are in S11_1_t/_s/_r/_b, the combined nonfinancial business rows in S11_t")

    # ---- Review 1 funding table (lines 28-38)
    und = lambda p: zq("FA106060005.Q", p) - zq("FA106231005.Q", p) - zq("FA106121075.Q", p)
    R(28, "Retained earnings (undistributed profits after tax and dividends) 928", "928", SAAR, "FA106060005.Q - FA106231005.Q - FA106121075.Q",
      lambda: sum(und(p) for p in Z4) / 4, T4 + "; profits before tax ex IVA/CCAdj less tax on corporate income less net dividends")
    R(29, "Depreciation add-back (capital consumption allowance) 2,445", "2445", SAAR, "FA106300015.Q", lambda: z4("FA106300015.Q"), T4)
    R(30, "Foreign earnings retained abroad 0", "0", SAAR, "FA106006065.Q", lambda: z4("FA106006065.Q"), T4)
    R(31, "Inventory valuation adjustment -93", "-93", SAAR, "FA105020601.Q", lambda: z4("FA105020601.Q"), T4)
    R(32, "Net capital transfers received 130", "130", SAAR, "FA105440005.Q (sign reversed: transfers paid)", lambda: -z4("FA105440005.Q"), T4)
    R(33, "INTERNAL FUNDS 3,410", "3410", SAAR, "sum of the five lines above",
      lambda: sum(und(p) + zq("FA106300015.Q", p) + zq("FA106006065.Q", p) + zq("FA105020601.Q", p) - zq("FA105440005.Q", p) for p in Z4) / 4,
      T4 + "; construction a of 2: sum of components")
    R(33, "INTERNAL FUNDS 3,410", "3410", SAAR, "FA106000105.Q", lambda: z4("FA106000105.Q"),
      T4 + "; construction b of 2: Z.1 line 'gross saving including foreign earnings retained abroad less net capital transfers paid'")
    R(34, "Net equity issuance -149", "-149", SAAR, "FA103164105.Q", lambda: z4("FA103164105.Q"), T4)
    R(35, "Net debt securities 271", "271", SAAR, "FA104122005.Q", lambda: z4("FA104122005.Q"), T4)
    R(36, "Net loans 369", "369", SAAR, "FA104135005.Q", lambda: z4("FA104135005.Q"), T4)
    R(37, "USE: gross fixed investment 3,135", "3135", SAAR, "FA105019005.Q", lambda: z4("FA105019005.Q"), T4)
    R(38, "Internal funds less gross fixed investment +275", "275", SAAR, "FA106000105.Q - FA105019005.Q", lambda: z4("FA106000105.Q") - z4("FA105019005.Q"), T4)
    R(39, "...excluding the one-off capital transfer +145", "145", SAAR, "FA106000105.Q - FA105019005.Q + FA105440005.Q",
      lambda: z4("FA106000105.Q") - z4("FA105019005.Q") + z4("FA105440005.Q"), T4)
    R(40, "Net lending (+) / borrowing (-) +50", "50", SAAR, "FA105000005.Q", lambda: z4("FA105000005.Q"), T4 + "; financial-account basis")
    for q, p in zip(("-250", "-253", "-164", "-635"), Z4):
        R(42, f"Z.1 financing gap (FA105005305) {p}: {q}", q, SAAR, "FA105005305.Q", lambda p=p: zq("FA105005305.Q", p), "single quarter " + p)
    R(42, "financing gap negative in five of the last six quarters", "5", "count of quarters (of 6)", "FA105005305.Q",
      lambda: float(sum(1 for p in ["2024:Q4", "2025:Q1"] + Z4 if zq("FA105005305.Q", p) < 0)), "last six quarters 2024:Q4-2026:Q1; negatives counted")
    nine = [f"{y}:Q{q}" for y in (2024, 2025, 2026) for q in (1, 2, 3, 4)][:9]
    res_with = lambda p: (zq("FA106000105.Q", p) - zq("FA105050005.Q", p)) - zq("FA105000005.Q", p) - zq("FA107005005.Q", p)
    R(44, "identity closes exactly, residual 0.000 on all nine quarters tested", "0.000", "max |residual| $bn", "FA106000105.Q, FA105050005.Q, FA105000005.Q, FA107005005.Q",
      lambda: round(max(abs(res_with(p)) for p in nine), 2),
      "construction a of 2: capital-account net lending (gross saving less capex) minus financial-account net lending minus the sector discrepancy, nine quarters 2024:Q1-2026:Q1; "
      "the raw maximum is 0.001 ($1 million), the integer rounding of the Z.1 file, so it is rounded to $10 million before comparing")
    R(44, "identity closes exactly, residual 0.000 on all nine quarters tested", "0.000", "max |residual| $bn", "FA106000105.Q, FA105050005.Q, FA105000005.Q",
      lambda: max(abs(res_with(p) + zq("FA107005005.Q", p)) for p in nine),
      "construction b of 2: same without the sector discrepancy line; the identity only closes when FA107005005.Q is counted")

    # ---- current account, GDP shares (line 46)
    R(46, "current account deficit is $1,065bn SAAR in 2026:Q1", "1065", SAAR, "FA266000005.Q (sign reversed)", lambda: -zq("FA266000005.Q", "2026:Q1"), "ROW balance on current account (NIPA)")
    R(46, "current account deficit ... 3.3% of GDP", "3.3", "% of GDP", "FA266000005.Q / A191RC", lambda: pct(-zq("FA266000005.Q", "2026:Q1"), G1()),
      "2026:Q1 SAAR over BEA 2026:Q1 NGDP SAAR in the CURRENT BEA vintage", src="both")
    R(46, "current account deficit ... 4.1% in 2024", "4.1", "% of GDP", "FA266000005.Q (mean of 2024 quarters) / A191RC annual", lambda: pct(-za("FA266000005.Q", 2024), na("A191RC", 2024)),
      "2024 mean of SAAR quarters over BEA 2024 annual NGDP", src="both")
    R(46, "Rest-of-world purchases of US corporate equities were $119bn SAAR in 2026:Q1", "119", SAAR, "FA263064105.Q", lambda: zq("FA263064105.Q", "2026:Q1"))
    R(46, "versus $1,275bn in 2025:Q2", "1275", SAAR, "FA263064105.Q", lambda: zq("FA263064105.Q", "2025:Q2"))
    R(58, "CA deficit down 0.8pp of GDP since 2024", "0.8", "pp of GDP", "FA266000005.Q / A191RC",
      lambda: pct(-za("FA266000005.Q", 2024), na("A191RC", 2024)) - pct(-zq("FA266000005.Q", "2026:Q1"), G1()), "2024 share minus 2026:Q1 share", src="both")

    # ---- Kalecki line (52)
    fed_def = lambda p: -(zq("FA316010105.Q", p) - zq("FA316900005.Q", p))
    R(52, "Federal current deficit 5.6% of GDP", "5.6", "% of GDP", "FA316010105.Q - FA316900005.Q ; A191RC",
      lambda: pct(fed_def("2026:Q1"), G1()), "construction a of 5: federal current receipts less current expenditures, 2026:Q1 SAAR / 2026:Q1 NGDP (Z.1 'net saving incl. net capital transfers paid', FA316006005.Q)", src="both")
    R(52, "Federal current deficit 5.6% of GDP", "5.6", "% of GDP", "FA316006005.Q ; A191RC",
      lambda: pct(sum(fed_def(p) for p in Z4) / 4, G4()), "construction b of 5: same, trailing four quarters over mean NGDP", src="both")
    R(52, "Federal current deficit 5.6% of GDP", "5.6", "% of GDP", "FA316006005.Q ; A191RC", lambda: pct(fed_def("2025:Q4"), nq("A191RC", "2025Q4")),
      "construction c of 5: same, 2025:Q4 only (last quarter before the 2026:Q1 capital-transfer spike)", src="both")
    R(52, "Federal current deficit 5.6% of GDP", "5.6", "% of GDP", "FA366000105.Q ; A191RC", lambda: pct(-zq("FA366000105.Q", "2026:Q1"), G1()),
      "construction d of 5: GENERAL government gross saving less net capital transfers paid / NGDP, 2026:Q1; matches the digit but is not the federal sector", src="both")
    R(52, "Federal current deficit 5.6% of GDP", "5.6", "% of GDP", "AD02RC ; A191RC", lambda: pct(-nq("AD02RC", "2026Q1"), G1()),
      "construction e of 5: BEA federal net lending/borrowing (NIPA), 2026:Q1 / NGDP", src="bea")
    R(52, "general government gross saving -$1,146bn SAAR", "-1146", SAAR, "FA366006005.Q + FA366300005.Q", lambda: zq("FA366006005.Q", "2026:Q1") + zq("FA366300005.Q", "2026:Q1"),
      "construction a of 3: net saving incl. net capital transfers paid plus consumption of fixed capital, 2026:Q1")
    R(52, "general government gross saving -$1,146bn SAAR", "-1146", SAAR, "FA366000105.Q + FA365440095.Q", lambda: zq("FA366000105.Q", "2026:Q1") + zq("FA365440095.Q", "2026:Q1"),
      "construction b of 3: gross saving less net capital transfers paid, capital transfers added back, 2026:Q1")
    R(52, "general government gross saving -$1,146bn SAAR", "-1146", SAAR, "A927RC", lambda: nq("A927RC", "2026Q1"),
      "construction c of 3: BEA NIPA gross government saving, 2026:Q1 (current vintage)", src="bea")
    R(52, "$2,704->$3,164bn of pre-tax profits (start)", "2704", SAAR, "FA106060005.Q", lambda: za("FA106060005.Q", 2023), "mean of the four 2023 quarters; the note does not date the 2,704")
    R(52, "$2,704->$3,164bn of pre-tax profits (end)", "3164", SAAR, "FA106060005.Q", lambda: zq("FA106060005.Q", "2026:Q1"), "2026:Q1 SAAR")

    # ---- capital transfer episode (line 54)
    R(54, "NFC sector received a net capital transfer of $559bn SAAR", "559", SAAR, "FA105440005.Q (sign reversed)", lambda: -zq("FA105440005.Q", "2026:Q1"), "2026:Q1")
    R(54, "(~$140bn in-quarter)", "140", "$bn per quarter", "FA105440005.Q / 4", lambda: -zq("FA105440005.Q", "2026:Q1") / 4)
    R(54, "federal government net capital transfers paid jumped to $763bn SAAR", "763", SAAR, "FA315440095.Q", lambda: zq("FA315440095.Q", "2026:Q1"), "2026:Q1")
    R(54, "federal ... from ~$100bn", "100", SAAR, "FA315440095.Q", lambda: zq("FA315440095.Q", "2025:Q4"), "2025:Q4; the four prior quarters run 96-128")
    for q, y in (("-611", 2023), ("-398", 2024), ("-304", 2025)):
        R(60, f"Net equity issuance ran {q} ({y})", q, SAAR, "FA103164105.A", lambda y=y: zq("FA103164105.A", str(y)), f"Z.1 annual column {y}")
    R(60, "turned positive +$124bn in 2026:Q1", "124", SAAR, "FA103164105.Q", lambda: zq("FA103164105.Q", "2026:Q1"))
    R(60, "a ~$735bn swing in the sector's net external equity position", "735", SAAR, "FA103164105.Q / .A", lambda: zq("FA103164105.Q", "2026:Q1") - zq("FA103164105.A", "2023"), "2026:Q1 minus 2023 annual")

    # ---- depreciation table (lines 66-71)
    cfc = lambda p: 4 * zq("FU106300003.Q", p)
    R(68, "Gross fixed inv. 2023:Q4 2,871", "2871", SAAR, "FA105019005.Q", lambda: zq("FA105019005.Q", "2023:Q4"))
    R(68, "Gross fixed inv. 2026:Q1 3,240", "3240", SAAR, "FA105019005.Q", lambda: zq("FA105019005.Q", "2026:Q1"))
    R(68, "Economic CFC 2023:Q4 2,196", "2196", SAAR, "FU106300003.Q x 4", lambda: cfc("2023:Q4"), "FU series is not seasonally adjusted quarterly flow; multiplied by 4")
    R(68, "Economic CFC 2026:Q1 2,532", "2532", SAAR, "FU106300003.Q x 4", lambda: cfc("2026:Q1"), "FU series is not seasonally adjusted quarterly flow; multiplied by 4")
    R(68, "Net investment 2023:Q4 675", "675", SAAR, "FA105019005.Q - 4*FU106300003.Q", lambda: zq("FA105019005.Q", "2023:Q4") - cfc("2023:Q4"))
    R(68, "Net investment 2026:Q1 708", "708", SAAR, "FA105019005.Q - 4*FU106300003.Q", lambda: zq("FA105019005.Q", "2026:Q1") - cfc("2026:Q1"))
    R(71, "Gross fixed investment +12.9%", "12.9", "%", "FA105019005.Q", lambda: pct(zq("FA105019005.Q", "2026:Q1") - zq("FA105019005.Q", "2023:Q4"), zq("FA105019005.Q", "2023:Q4")))
    nin = lambda p: zq("FA105019005.Q", p) - cfc(p)
    R(71, "net fixed investment +4.9%", "4.9", "%", "FA105019005.Q - 4*FU106300003.Q", lambda: pct(nin("2026:Q1") - nin("2023:Q4"), nin("2023:Q4")))
    R(71, "Roughly 90% of the increase in gross capex is absorbed by faster depreciation", "90", "%", "FU106300003.Q, FA105019005.Q",
      lambda: pct(cfc("2026:Q1") - cfc("2023:Q4"), zq("FA105019005.Q", "2026:Q1") - zq("FA105019005.Q", "2023:Q4")), "change in CFC over change in gross fixed investment, 2023:Q4 to 2026:Q1")
    for lab, base in (("a", lambda: (nq("A008RC", "2023Q4"), nq("A679RC", "2023Q4"))), ("b", lambda: (na("A008RC", 2023), na("A679RC", 2023)))):
        bname = "2023Q4 quarterly SAAR" if lab == "a" else "2023 annual"
        cc = f"construction {lab} of 2: change from {bname} to 2026Q1 SAAR"
        R(71, "information-processing equipment plus software account for +$585bn", "585", "$bn", "A679RC", lambda b=base: nq("A679RC", "2026Q1") - b()[1], cc, src="bea")
        R(71, "of the +$701bn rise in all private non-residential fixed investment", "701", "$bn", "A008RC", lambda b=base: nq("A008RC", "2026Q1") - b()[0], cc, src="bea")
        R(71, "(83%)", "83", "%", "A679RC / A008RC", lambda b=base: pct(nq("A679RC", "2026Q1") - b()[1], nq("A008RC", "2026Q1") - b()[0]), cc, src="bea")
    R(73, "tax-basis CCA jumps ... (+$317bn in one quarter) at 2025:Q1", "317", SAAR, "FA106300015.Q", lambda: zq("FA106300015.Q", "2025:Q1") - zq("FA106300015.Q", "2024:Q4"), "2025:Q1 minus 2024:Q4")
    R(73, "NIPA economic CFC is perfectly smooth (+$36bn)", "36", SAAR, "FU106300003.Q x 4", lambda: cfc("2025:Q1") - cfc("2024:Q4"), "2025:Q1 minus 2024:Q4; the note does not say which quarters")
    R(73, "Pre-tax profits fall by ... -$348bn", "-348", SAAR, "FA106060005.Q", lambda: zq("FA106060005.Q", "2025:Q1") - zq("FA106060005.Q", "2024:Q4"), "2025:Q1 minus 2024:Q4")
    R(73, "internal funds actually declined $33bn across that quarter", "-33", SAAR, "FA106000105.Q", lambda: zq("FA106000105.Q", "2025:Q1") - zq("FA106000105.Q", "2024:Q4"), "2025:Q1 minus 2024:Q4 (sign: a decline is negative)")

    # ---- limits section (81-85)
    R(81, "trade receivables +$877bn SAAR in 2026:Q1", "877", SAAR, "FA103070005.Q", lambda: zq("FA103070005.Q", "2026:Q1"))
    R(83, "non-financial non-corporate business (capex $625bn", "625", SAAR, "FA115050005.Q", lambda: zq("FA115050005.Q", "2026:Q1"), "2026:Q1")
    R(85, "the $4,014bn SAAR financial-asset acquisition", "4014", SAAR, "FA104090005.Q", lambda: zq("FA104090005.Q", "2026:Q1"))
    R(85, "$2,691bn is 'total miscellaneous assets'", "2691", SAAR, "FA103090005.Q", lambda: zq("FA103090005.Q", "2026:Q1"))

    # ---- Review 2 / synthesis: levels quoted from FRED mirrors of Z.1 (line 124 etc.)
    R(124, "BCNSDODNS 2026Q1 = 14,453.8", "14453.8", "$bn level", "LA104104005.Q", lambda: zq("LA104104005.Q", "2026:Q1"), "FRED BCNSDODNS is the Z.1 NFC debt securities and loans liability, level")
    R(124, "NCBEILQ027S = 69,511.6", "69511.6", "$bn level", "LM103164105.Q", lambda: zq("LM103164105.Q", "2026:Q1"), "NFC corporate equities liability at market value, 2026:Q1")
    R(124, "TNWMVBSNNCB = 38,219.0", "38219.0", "$bn level", "LM102090005.Q", lambda: zq("LM102090005.Q", "2026:Q1"), "NFC net worth at market value, 2026:Q1")
    q_ = lambda p: zq("LM103164105.Q", p) / zq("LM102090005.Q", p)
    R(124, "Tobin's q = 1.819", "1.819", "ratio", "LM103164105.Q / LM102090005.Q", lambda: q_("2026:Q1"), "equity market value over net worth at market value")
    R(124, "the 2025Q3 peak of 1.943", "1.943", "ratio", "LM103164105.Q / LM102090005.Q", lambda: q_("2025:Q3"))
    R(124, "TNWBSHNO = 182,979.9", "182979.9", "$bn level", "FL152090005.Q", lambda: zq("FL152090005.Q", "2026:Q1"), "household and nonprofit net worth")
    R(124, "+$113.1bn Q1 change", "113.1", "$bn", "FL152090005.Q", lambda: zq("FL152090005.Q", "2026:Q1") - zq("FL152090005.Q", "2025:Q4"))
    R(124, "$39,164.8bn 2023-25 increase", "39164.8", "$bn", "FL152090005.Q", lambda: zq("FL152090005.Q", "2025:Q4") - zq("FL152090005.Q", "2022:Q4"), "2022:Q4 to 2025:Q4")
    R(124, "MMMFFAQ027S = 8,289.6", "8289.6", "$bn level", "FL634090005.Q", lambda: zq("FL634090005.Q", "2026:Q1"), "money market funds total financial assets")
    R(124, "W274RC 2026Q1 = 1,244.2", "1244.2", "$bn SAAR", "W274RC", lambda: nq("W274RC", "2026Q1"), "BEA undistributed corporate profits with IVA and CCAdj", src="bea")
    R(124, "AD01RC 2026Q1 = -2,955.2", "-2955.2", "$bn SAAR", "AD01RC", lambda: nq("AD01RC", "2026Q1"), "BEA government net lending/borrowing", src="bea")
    R(124, "AD01RC ... 2025 average -2,293.5", "-2293.5", "$bn SAAR", "AD01RC", lambda: na("AD01RC", 2025), "2025 annual (equals the mean of the four quarters)", src="bea")
    R(140, "current-cost ratio 14,453.8 / 38,219.0 = 37.82%", "37.82", "%", "LA104104005.Q / LM102090005.Q", lambda: pct(zq("LA104104005.Q", "2026:Q1"), zq("LM102090005.Q", "2026:Q1")))
    R(140, "14,453.8 / 69,511.6 = 20.79%", "20.79", "%", "LA104104005.Q / LM103164105.Q", lambda: pct(zq("LA104104005.Q", "2026:Q1"), zq("LM103164105.Q", "2026:Q1")))
    R(140, "Historical checks: 2019Q1 = 33.0%", "33.0", "%", "LA104104005.Q / LM103164105.Q", lambda: pct(zq("LA104104005.Q", "2019:Q1"), zq("LM103164105.Q", "2019:Q1")))
    R(140, "2019Q4 = 31.0%", "31.0", "%", "LA104104005.Q / LM103164105.Q", lambda: pct(zq("LA104104005.Q", "2019:Q4"), zq("LM103164105.Q", "2019:Q4")))
    R(140, "2009Q1 = 68.9%", "68.9", "%", "LA104104005.Q / LM103164105.Q", lambda: pct(zq("LA104104005.Q", "2009:Q1"), zq("LM103164105.Q", "2009:Q1")))
    R(148, "(2025Q3 = 7,774.1", "7774.1", "$bn level", "FL634090005.Q", lambda: zq("FL634090005.Q", "2025:Q3"))
    R(148, "2025Q4 = 8,190.2)", "8190.2", "$bn level", "FL634090005.Q", lambda: zq("FL634090005.Q", "2025:Q4"))
    R(152, "NFC debt grew +4.64% (14,453.8 / 13,813.4)", "4.64", "% y/y", "LA104104005.Q", lambda: pct(zq("LA104104005.Q", "2026:Q1"), zq("LA104104005.Q", "2025:Q1")) - 100.0, "2026:Q1 over 2025:Q1")
    R(152, "14,453.8 / 13,813.4 (denominator)", "13813.4", "$bn level", "LA104104005.Q", lambda: zq("LA104104005.Q", "2025:Q1"))
    R(152, "debt's 9.24% annualised quarterly rate", "9.24", "% annualised", "LA104104005.Q", lambda: 100 * ((zq("LA104104005.Q", "2026:Q1") / zq("LA104104005.Q", "2025:Q4")) ** 4 - 1))
    R(152, "growing at a 9.13% annualised quarterly rate", "9.13", "% annualised", "LA104104005.Q", lambda: 100 * ((zq("LA104104005.Q", "2026:Q1") / zq("LA104104005.Q", "2025:Q4")) ** 4 - 1),
      "this is the figure the Wicksell section printed; it equals the rebuilt value, so the review's 9.24 is the one that does not reproduce")
    R(152, "nominal GDP (+6.07% y/y)", "6.07", "% y/y", "A191RC", lambda: pct(nq("A191RC", "2026Q1"), nq("A191RC", "2025Q1")) - 100.0, "2026Q1 over 2025Q1, current BEA vintage", src="bea")
    R(152, "nominal GDP grew 5.79% ((31,865.7/31,422.5)^4-1)", "5.79", "% annualised", "A191RC", lambda: 100 * ((nq("A191RC", "2026Q1") / nq("A191RC", "2025Q4")) ** 4 - 1), "current BEA vintage", src="bea")
    R(152, "31,865.7 (2026Q1 nominal GDP)", "31865.7", "$bn SAAR", "A191RC", lambda: nq("A191RC", "2026Q1"), "quoted via FRED GDP (note: sources checked 21 Aug 2026); the BEA file here is a later vintage", src="bea")
    R(152, "31,422.5 (2025Q4 nominal GDP)", "31422.5", "$bn SAAR", "A191RC", lambda: nq("A191RC", "2025Q4"), "quoted via FRED GDP (note: sources checked 21 Aug 2026); the BEA file here is a later vintage", src="bea")
    mg = lambda p: 100 * zq("FL663067003.Q", p) / zq("LM103164105.Q", p)
    R(172, "Margin loans are 0.90% of NFC equity market value", "0.90", "%", "FL663067003.Q / LM103164105.Q", lambda: mg("2026:Q1"),
      "broker-dealer receivables due from customers (margin loans and other receivables) over NFC equity market value; the note names no series, this is my construction", src="z1")
    R(172, "below the 0.95% of 2021Q4", "0.95", "%", "FL663067003.Q / LM103164105.Q", lambda: mg("2021:Q4"), "same construction")

    # ---- 110.5% and 3.7% (lines 188-189)
    gs = "FA106000105.Q"
    cons = [
        ("a", "NFC gross saving incl. foreign earnings less net cap transfers / NFC total capital expenditures, trailing 4Q", lambda: z4(gs) / z4("FA105050005.Q"), "FA106000105.Q / FA105050005.Q"),
        ("b", "same, 2026:Q1 only", lambda: zq(gs, "2026:Q1") / zq("FA105050005.Q", "2026:Q1"), "FA106000105.Q / FA105050005.Q"),
        ("c", "NFC gross saving / NFC Z.1 'gross investment' (capex plus financial net lending), 2026:Q1", lambda: zq(gs, "2026:Q1") / zq("FA105090005.Q", "2026:Q1"), "FA106000105.Q / FA105090005.Q"),
        ("d", "NFC gross saving / NFC gross fixed investment, trailing 4Q", lambda: z4(gs) / z4("FA105019005.Q"), "FA106000105.Q / FA105019005.Q"),
        ("e", "nonfinancial business (corporate + noncorporate) gross saving / total capex, 2026:Q1", lambda: zq("FA146000105.Q", "2026:Q1") / zq("FA145050005.Q", "2026:Q1"), "FA146000105.Q / FA145050005.Q"),
        ("f", "nonfinancial business gross saving / Z.1 gross investment, 2026:Q1", lambda: zq("FA146000105.Q", "2026:Q1") / zq("FA145090005.Q", "2026:Q1"), "FA146000105.Q / FA145090005.Q"),
    ]
    for lab, desc, fn, codes in cons:
        R(188, "business gross saving covers 110.5% of business gross investment", "110.5", "%", codes, (lambda fn=fn: 100 * fn()), f"construction {lab} of {len(cons)}: {desc}")
    # private domestic sector balance
    pnipa = lambda p: nq("W162RC", p) - nq("AD01RC", p)
    pz_fin = lambda f: -(f("FA365000005.Q") + f("FA265000005.Q"))
    pcons = [
        ("a", "BEA NIPA: economy net lending (W162RC) minus government net lending (AD01RC) = private domestic, 2026Q1 / NGDP", lambda: pct(pnipa("2026Q1"), G1()), "W162RC - AD01RC ; A191RC"),
        ("b", "same, trailing four quarters over mean NGDP", lambda: pct(sum(pnipa(p.replace(":", "")) for p in Z4) / 4, G4()), "W162RC - AD01RC ; A191RC"),
        ("c", "same, 2025Q4 only", lambda: pct(pnipa("2025Q4"), nq("A191RC", "2025Q4")), "W162RC - AD01RC ; A191RC"),
        ("d", "same, 2025 annual", lambda: pct(na("W162RC", 2025) - na("AD01RC", 2025), na("A191RC", 2025)), "W162RC - AD01RC ; A191RC"),
        ("e", "Z.1 financial accounts: minus (general government + rest of world net lending), 2026:Q1 / NGDP", lambda: pct(pz_fin(lambda c: zq(c, "2026:Q1")), G1()), "FA365000005.Q, FA265000005.Q ; A191RC"),
        ("f", "Z.1 financial accounts: same, trailing four quarters", lambda: pct(pz_fin(z4), G4()), "FA365000005.Q, FA265000005.Q ; A191RC"),
        ("g", "Z.1 sum of households + nonfinancial business + domestic financial net lending, 2026:Q1 / NGDP", lambda: pct(zq("FA155000005.Q", "2026:Q1") + zq("FA145000005.Q", "2026:Q1") + zq("FA795000005.Q", "2026:Q1"), G1()), "FA155000005.Q + FA145000005.Q + FA795000005.Q ; A191RC"),
    ]
    for lab, desc, fn, codes in pcons:
        R(189, "private domestic sector is in surplus (+3.7% of GDP)", "3.7", "% of GDP", codes, fn, f"construction {lab} of {len(pcons)}: {desc}", src="both")

    # ---- Review 2 U4, discrepancy (211, 259)
    R(211, "W020RC spiking to $807.9bn SAAR", "807.9", SAAR, "W020RC", lambda: nq("W020RC", "2026Q1"), "BEA federal capital transfers paid, 2026Q1 current vintage", src="bea")
    R(211, "a one-off ~$168bn IEEPA tariff-refund capital transfer", "168", "$bn per quarter", "FA313190605.Q / 4", lambda: zq("FA313190605.Q", "2026:Q1") / 4,
      "Z.1 federal miscellaneous liabilities: IEEPA tariff line, 2026:Q1 SAAR / 4; the quarterly level FL313190605.Q is 166.2 as well")
    R(259, "NFC capital- and financial-account net lending differ by $133bn per quarter (low end)", "133", "$bn per quarter", "FA107005005.Q / 4",
      lambda: min(abs(zq("FA107005005.Q", p)) / 4 for p in [f"{y}:Q{q}" for y in (2024, 2025) for q in (1, 2, 3, 4)] + ["2026:Q1"]),
      "no window of 3-40 recent quarters reproduces both ends of 133-224 (SAAR or SAAR/4); this row shows the minimum over 2024:Q1-2026:Q1 of |sector discrepancy|/4")
    R(259, "... to $224bn per quarter (high end)", "224", "$bn per quarter", "FA107005005.Q / 4",
      lambda: max(abs(zq("FA107005005.Q", p)) / 4 for p in [f"{y}:Q{q}" for y in (2024, 2025) for q in (1, 2, 3, 4)] + ["2026:Q1"]), "maximum over the same window")

    # ---- Annex: nominal GDP pair, M2 ratios (282-285)
    R(282, "US nominal GDP ($bn) Dec-2008 14,608.2", "14608.2", "$bn SAAR", "A191RC", lambda: nq("A191RC", "2008Q4"), "2008Q4 in the current BEA vintage", src="bea")
    R(282, "US nominal GDP ($bn) Dec-2019 21,933.2", "21933.2", "$bn SAAR", "A191RC", lambda: nq("A191RC", "2019Q4"), "2019Q4", src="bea")
    R(282, "CAGR 3.76%", "3.76", "% per year", "A191RC", lambda: 100 * ((nq("A191RC", "2019Q4") / nq("A191RC", "2008Q4")) ** (1 / 11) - 1), "11 years, 2008Q4 to 2019Q4", src="bea")
    M2a, M2b = 8203.0, 15351.5
    R(283, "M2 / NGDP 56.2%", "56.2", "%", "A191RC (M2 = 8,203.0 as quoted in the note; M2 itself not rebuilt)", lambda: pct(M2a, nq("A191RC", "2008Q4")), "numerator taken from the note", src="bea")
    R(283, "M2 / NGDP 70.0%", "70.0", "%", "A191RC (M2 = 15,351.5 as quoted in the note)", lambda: pct(M2b, nq("A191RC", "2019Q4")), "numerator taken from the note", src="bea")
    R(285, "Had M2 tracked NGDP, Dec-2019 M2 would have been ~$12.3tn", "12.3", "$tn", "A191RC (M2 as quoted)", lambda: M2a * nq("A191RC", "2019Q4") / nq("A191RC", "2008Q4") / 1000, "M2 start value taken from the note", src="bea")
    R(285, "roughly $3.0tn of 'excess' broad money", "3.0", "$tn", "A191RC (M2 as quoted)", lambda: (M2b - M2a * nq("A191RC", "2019Q4") / nq("A191RC", "2008Q4")) / 1000, "M2 values taken from the note", src="bea")
    R(285, "Broad money grew 2.1pp/yr faster than nominal income", "2.1", "pp per year", "A191RC (M2 as quoted)", lambda: 100 * ((M2b / M2a) ** (1 / 11) - 1) - 100 * ((nq("A191RC", "2019Q4") / nq("A191RC", "2008Q4")) ** (1 / 11) - 1), "M2 CAGR from the note's M2 values minus rebuilt NGDP CAGR", src="bea")

    # ---- housing / MMF history (351, 357)
    hm = "FL153165105.Q"
    R(351, "Household mortgage debt: peak 2008Q1 $10,648bn", "10648", "$bn level", hm, lambda: zq(hm, "2008:Q1"), "FRED HHMSDODNS taken as Z.1 households home mortgages liability (FL153165105)")
    R(351, "trough 2015Q1 $9,328bn", "9328", "$bn level", hm, lambda: zq(hm, "2015:Q1"))
    R(351, "(-12.4%)", "-12.4", "%", hm, lambda: pct(zq(hm, "2015:Q1"), zq(hm, "2008:Q1")) - 100)
    R(351, "2019Q4 $10,391bn", "10391", "$bn level", hm, lambda: zq(hm, "2019:Q4"))
    R(351, "still 2.4% below the 2008 peak", "2.4", "% below peak", hm, lambda: 100 - pct(zq(hm, "2019:Q4"), zq(hm, "2008:Q1")))
    def regained():
        p0 = zq(hm, "2008:Q1")
        for p in sorted(k for k in Z[hm] if ":Q" in k and k > "2008:Q1"):
            if Z[hm][p] >= p0:
                return p.replace(":", "")
        raise Missing("never regained")
    R(351, "nominal 2008 peak was not regained until 2020Q3", "2020Q3", "quarter", hm, regained)
    mm = "FL634090005.Q"
    R(357, "MMF total financial assets: peak $3,832bn (2008Q4)", "3832", "$bn level", mm, lambda: zq(mm, "2008:Q4"))
    R(357, "trough $2,785bn (2012Q2)", "2785", "$bn level", mm, lambda: zq(mm, "2012:Q2"))
    R(357, "$3,120bn (2017Q4)", "3120", "$bn level", mm, lambda: zq(mm, "2017:Q4"))

    rows.sort(key=lambda r: r[0])
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "reconciliation.csv"), "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["quote_line", "quoted_text", "quoted_value", "rederived_value", "units", "series_codes", "release", "status", "note"])
        w.writerows(rows)
    from collections import Counter
    c = Counter(r[7] for r in rows)
    print(f"{len(rows)} rows; " + "; ".join(f"{k}: {c[k]}" for k in sorted(c)) + f"; z1 duplicate-code conflicts: {conflicts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
