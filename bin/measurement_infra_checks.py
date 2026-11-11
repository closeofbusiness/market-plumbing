#!/usr/bin/env python3
"""Rebuild the Z.1 Financial Accounts figures quoted in _research/measurement_infrastructure_reviews.md. Stdlib only.

  python3 bin/measurement_infra_checks.py build [--date YYYYMMDD]     (offline, deterministic, no network code at all)

build  Reads only files already on disk (the Z.1 CSV package of release 2026-06-11 kept by bin/funding_identity_checks.py
       under data/vintages/funding_identity_checks/<date>/, plus that folder's BEA NipaDataQ.txt for one GDP reading)
       and writes data/measurement_infra_checks/reconciliation.csv. The README.md in that folder is hand-written.
       Same inputs -> same bytes (rows keep the order of the note; no clock, no randomness).

Status (half a unit of the last quoted digit is the tolerance): MATCH within rounding / DIFFERS / NOT FOUND / NOT Z.1.
Where a construction or a quarter is ambiguous, every plausible reading gets its own row ("reading a of n").
"""
import argparse, csv, glob, io, os, re, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VINT = os.path.join(ROOT, "data", "vintages", "funding_identity_checks")
OUT = os.path.join(ROOT, "data", "measurement_infra_checks")
NOTE = "_research/measurement_infrastructure_reviews.md"
HAND = "Shadow_Debt_Measurement_Handbook.md"


class Missing(Exception):
    pass


def latest_dir():
    ds = sorted(x for x in glob.glob(os.path.join(VINT, "*")) if os.path.isdir(x) and os.path.exists(os.path.join(x, "z1_csv_files.zip")))
    if not ds:
        raise SystemExit("no data/vintages/funding_identity_checks/<date>/z1_csv_files.zip on disk")
    return ds[-1]


def load_z1(zpath):
    """-> (series {code: {period: value in $ millions as in the file}}, dictionary {table: [(code, description, line)]}, csv names, dict names, ND count)."""
    out, dic, nd = {}, {}, 0
    with zipfile.ZipFile(zpath) as z:
        names = sorted(z.namelist())
        csvs = [n for n in names if n.startswith("csv/") and n.endswith(".csv")]
        dnames = [n for n in names if n.startswith("data_dictionary/") and n.endswith(".txt")]
        for name in csvs:
            rows = list(csv.reader(io.StringIO(z.read(name).decode("utf-8-sig"))))
            hdr = rows[0]
            for j, code in enumerate(hdr[1:], 1):
                col = out.setdefault(code, {})
                for r in rows[1:]:
                    if j >= len(r):
                        continue
                    if r[j] == "ND":
                        nd += 1
                        continue
                    if r[j] in ("", "NA"):
                        continue
                    try:
                        x = float(r[j])
                    except ValueError:
                        continue
                    col.setdefault(r[0], x)
        for name in dnames:
            t = os.path.basename(name)[:-4]
            for ln in z.read(name).decode("utf-8-sig").splitlines():
                p = ln.split("\t")
                if len(p) >= 3:
                    m = re.match(r"Line (\d+)", p[2])
                    dic.setdefault(t, []).append((p[0], p[1], int(m.group(1)) if m else 0))
    return out, dic, csvs, dnames, nd


def load_nipa(path):
    out = {}
    with open(path, newline="") as fh:
        for r in csv.reader(fh):
            if len(r) < 3 or r[0].startswith("%"):
                continue
            try:
                out.setdefault(r[0], {})[r[1]] = float(r[2].replace(",", ""))
            except ValueError:
                pass
    return out


def status_of(q, r, mode):
    """q quoted string; r re-derived (float / str / None). Returns (status, diff text)."""
    if r is None:
        return "NOT FOUND", ""
    if isinstance(r, str):
        return ("MATCH within rounding" if r == q else "DIFFERS"), ""
    qv = float(q)
    dec = len(q.split(".")[1]) if "." in q else 0
    d = r - qv
    if mode == "le":
        return ("MATCH within rounding" if r <= qv + 0.5 * 10 ** (-dec) + 1e-9 else "DIFFERS"), f"diff {d:+.{dec + 2}f}"
    st = "MATCH within rounding" if abs(d) <= 0.5 * 10 ** (-dec) + 1e-9 else "DIFFERS"
    return st, f"diff {d:+.{dec + 2}f}"


def fnum(x, dec):
    return f"{x + 0.0:.{dec + 2}f}"


QS6 = ["2024:Q4", "2025:Q1", "2025:Q2", "2025:Q3", "2025:Q4", "2026:Q1"]
QS5 = ["2019:Q4", "2024:Q4", "2025:Q3", "2025:Q4", "2026:Q1"]


def qrange(a, b):
    """Quarters after a up to and including b."""
    out = []
    y, q = int(a[:4]), int(a[-1])
    while True:
        q += 1
        if q == 5:
            y, q = y + 1, 1
        out.append(f"{y}:Q{q}")
        if out[-1] == b:
            return out


def do_build(date):
    d = os.path.join(VINT, date) if date else latest_dir()
    zpath = os.path.join(d, "z1_csv_files.zip")
    rel = open(os.path.join(d, "z1_release.txt")).read().split("\n")[0]
    if rel != "20260611":
        raise SystemExit(f"the package on disk is release {rel}, not 20260611; refusing to rebuild against another release")
    Z, DIC, csvs, dnames, ndcount = load_z1(zpath)
    NQ = load_nipa(os.path.join(d, "NipaDataQ.txt"))

    def M(c, p):               # $ millions, raw
        try:
            return Z[c][p]
        except KeyError:
            raise Missing(f"{c} {p}")

    def B(c, p):               # $ billions
        return M(c, p) / 1000.0

    def S(c, ps):
        return sum(M(c, p) for p in ps)

    def lineno(table, code):
        for c, _, ln in DIC.get(table, []):
            if c == code:
                return ln
        raise Missing(f"{code} not in {table}")

    rows = []

    def R(line, text, q, units, codes, quarter, fn, note="", src=NOTE, mode="round"):
        assert len(text.split()) <= 15, text
        try:
            val = fn()
        except (Missing, KeyError, ZeroDivisionError, ValueError) as e:
            val, note = None, (note + " " if note else "") + f"[not computable from the package: {e}]"
        st, dtxt = status_of(q, val, mode)
        if st == "DIFFERS" and val is not None and not isinstance(val, str) and mode == "round":
            dd = len(q.split(".")[1]) if "." in q else 0
            if abs(val - float(q)) < 10 ** (-dd):
                dtxt += " (inside one unit of the last quoted digit: would match if the note truncated rather than rounded)"
        full = "; ".join(x for x in (dtxt, note) if x)
        rd = "" if val is None else (val if isinstance(val, str) else fnum(val, len(q.split(".")[1]) if "." in q else 0))
        rows.append([src, line, text, q, rd, units, codes, quarter, st, full])

    def NZ(line, text, q, units, codes, quarter, note, src=NOTE):
        assert len(text.split()) <= 15, text
        rows.append([src, line, text, q, "", units, codes, quarter, "NOT Z.1", note])

    def NF(line, text, q, units, codes, quarter, note, src=NOTE):
        assert len(text.split()) <= 15, text
        rows.append([src, line, text, q, "", units, codes, quarter, "NOT FOUND", note])

    PKG = "release 2026-06-11 package"
    # ------------------------------------------------------------------ section 0-2: package facts
    R(6, "Vintage: Z.1 released 11 June 2026, data through 2026:Q1", "2026:Q1", "last quarter", "FL103163005.Q", "2026:Q1",
      lambda: max(p for p in Z["FL103163005.Q"] if ":Q" in p), "z1_release.txt on disk says 20260611; the package ends 2026:Q1")
    R(34, "286 files, one per table", "286", "csv files", "csv/*.csv", "n/a", lambda: float(len(csvs)))
    R(34, "data_dictionary/ (286 tab-delimited files)", "286", "dictionary files", "data_dictionary/*.txt", "n/a", lambda: float(len(dnames)))
    sq = sorted(p for p in Z["FL103163005.Q"] if ":Q" in p)
    R(34, "periods 1945:Q4 ... 2026:Q1", "1945:Q4", "first period", "any level series", "n/a",
      lambda: min(p for c in Z if c.startswith("FL") for p in Z[c] if ":Q" in p),
      "earliest quarter of any FL series in the package; FL103163005 itself starts " + sq[0])
    R(34, "missing = ND", "ND", "marker", "csv/*.csv", "n/a", lambda: "ND" if ndcount > 0 else "none", f"{ndcount} ND cells in the package")
    R(32, "z1_csv_files.zip (8.08 MB, HTTP 200)", "8.08", "MB (10^6 bytes)", "zip file", "n/a", lambda: os.path.getsize(zpath) / 1e6,
      "file size on disk; the HTTP status is not checkable offline")
    R(979, "z1_csv_files.zip (8,075,952 bytes)", "8075952", "bytes", "zip file", "n/a", lambda: float(os.path.getsize(zpath)))
    for ln, txt, q, nm in ((20, "96 code changes in 2026q1, of which 41 outright deletions", "96", "z1_code_changes.txt"),
                           (20, "of which 41 outright deletions", "41", "z1_code_changes.txt"),
                           (24, "z1_code_changes.txt (857 KB, 6,484 rows, back to 2009q4)", "6484", "z1_code_changes.txt"),
                           (16, "The complete crosswalk is a 205-line CSV", "205", "z1_table_mapping.csv")):
        NF(ln, txt, q, "count", nm, "2026q1", f"{nm} is a separate download, not in z1_csv_files.zip; the package cannot test it")
    for c, ln in (("FL894123005.Q", 20), ("FL624123035.Q", 260)):
        R(ln, f"{c[:-2]} no longer exists in the release", "0", "series present", c, "n/a", lambda c=c: float(c in Z),
          "count of columns with this code in the 286 csv files (0 = absent, as the note says)")
    # digit-4 flag counts (line 92)
    cores = {}
    for c in Z:
        m = re.match(r"^[A-Z]{2}(\d{9})\.[QA]$", c)
        if m:
            cores.setdefault(m.group(1), set()).add(c[:2])
    fl_cores = {k for k, v in cores.items() if "FL" in v}
    a_all = sum(1 for k in cores if k[3] == "0"); l_all = sum(1 for k in cores if k[3] == "1")
    a_fl = sum(1 for k in fl_cores if k[3] == "0"); l_fl = sum(1 for k in fl_cores if k[3] == "1")
    R(92, "Verified across 1,536 asset-side series", "1536", "series", "9-digit cores, digit 4 = 0", "n/a", lambda: float(a_all),
      "reading a of 2: distinct nine-digit cores, any prefix, quarterly and annual csv columns")
    R(92, "Verified across 1,536 asset-side series", "1536", "series", "9-digit cores, digit 4 = 0, FL only", "n/a", lambda: float(a_fl),
      "reading b of 2: distinct nine-digit cores that have an FL (level) column")
    R(92, "and 745 liability-side series", "745", "series", "9-digit cores, digit 4 = 1", "n/a", lambda: float(l_all),
      "reading a of 2: distinct nine-digit cores, any prefix")
    R(92, "and 745 liability-side series", "745", "series", "9-digit cores, digit 4 = 1, FL only", "n/a", lambda: float(l_fl),
      "reading b of 2: distinct nine-digit cores that have an FL (level) column")
    # table line counts
    for ln, txt, q, tab, nm in ((100, "Line map of S11.1.t (58 lines)", "58", "S11_1_t", "S11.1.t"),
                                (147, "sector discrepancy table is S0.t, 21 lines", "21", "S0_t", "S0.t"),
                                (207, "table F0.t (old F.8), 14 lines", "14", "F0_t", "F0.t"),
                                (290, "REST OF THE WORLD (S2.s / S2.t) - 53 lines", "53", "S2_s", "S2.s"),
                                (267, "This 66-line instrument table", "66", "F4_6_s", "F4.6.s"),
                                (258, "S124.7.b is a 34-line balance sheet", "34", "S124_7_b", "S124.7.b"),
                                (264, "read the 31 line descriptions", "31", "S127_2_s", "S127.2.s"),
                                (342, "Table F89.3c lists all 40 lines", "40", "F89_3c_s", "F89.3c.s")):
        R(ln, txt, q, "lines", nm, "n/a", lambda tab=tab: float(max(x[2] for x in DIC[tab])),
          "highest 'Line n' in the table's data dictionary")
    # S11.1.t line map (106-117)
    for ln, code, q in ((6, "FA106006065.Q", "6"), (7, "FA105440005.Q", "7"), (8, "FA106000105.Q", "8"), (9, "FA105090005.Q", "9"),
                        (10, "FA105050005.Q", "10"), (11, "FA105019005.Q", "11"), (14, "FA105000005.Q", "14"),
                        (47, "FA103170005.Q", "47"), (55, "FA103164105.Q", "55"), (57, "FA107005005.Q", "57"), (58, "FA105005305.Q", "58")):
        R(106, f"S11.1.t line {q} is {code[:-2]}", q, "line number", code, "n/a", lambda code=code: float(lineno("S11_1_t", code)))
    lines39 = ["FA104122005.Q", "FA103163005.Q", "FA104135005.Q", "FA103168005.Q", "FA103169005.Q", "FA103165005.Q"]
    R(113, "lines 39-46 debt securities ... mortgages (first code)", "39", "line number", "FA104122005.Q", "n/a",
      lambda: float(min(lineno("S11_1_t", c) for c in lines39)), "lowest line among the six listed codes")
    R(113, "lines 39-46 debt securities ... mortgages (last code)", "46", "line number", "FA103165005.Q", "n/a",
      lambda: float(max(lineno("S11_1_t", c) for c in lines39)), "highest line among the six listed codes")

    # ------------------------------------------------------------------ section 2: net worth
    R(74, "Household net worth FL152090005 = 182,979,889", "182979889", "$m level", "FL152090005.Q", "2026:Q1", lambda: M("FL152090005.Q", "2026:Q1"))
    R(74, "Household net worth rose $0.1tn in 2026:Q1", "0.1", "$tn", "FL152090005.Q", "2026:Q1",
      lambda: (M("FL152090005.Q", "2026:Q1") - M("FL152090005.Q", "2025:Q4")) / 1e6, "level change over the quarter")
    R(74, "equity revaluation negative $1.8tn", "-1.8", "$tn", "FR153064105.Q", "2026:Q1", lambda: M("FR153064105.Q", "2026:Q1") / 1e6,
      "reading a of 3: direct corporate equities only")
    R(74, "equity revaluation negative $1.8tn", "-1.8", "$tn", "FR153064105.Q + FR153064205.Q", "2026:Q1",
      lambda: (M("FR153064105.Q", "2026:Q1") + M("FR153064205.Q", "2026:Q1")) / 1e6, "reading b of 3: corporate equities plus mutual fund shares")
    R(74, "equity revaluation negative $1.8tn", "-1.8", "$tn", "FR154090005.Q", "2026:Q1", lambda: M("FR154090005.Q", "2026:Q1") / 1e6,
      "reading c of 3: revaluation of ALL household financial assets (-1.8546, which rounds to -1.9, not -1.8)")

    # ------------------------------------------------------------------ section 3: financing gap
    cap, gs, fera, nct, gap, nl, sd, gi = ("FA105050005.Q", "FA106000105.Q", "FA106006065.Q", "FA105440005.Q",
                                           "FA105005305.Q", "FA105000005.Q", "FA107005005.Q", "FA105090005.Q")
    tab = {
        "2024:Q4": (2936715, 3108975, 178544, -27667, 6284, 598421, -426161),
        "2025:Q1": (3165153, 3075644, 52615, -28252, 142124, 375394, -464903),
        "2025:Q2": (2993219, 3071355, -171707, 1907, -249844, -700259, 778396),
        "2025:Q3": (3042531, 3227901, -67451, 3302, -252822, -681091, 866462),
        "2025:Q4": (3101771, 3361815, 95607, 34085, -164438, 610069, -350025),
        "2026:Q1": (3199548, 3978741, 144283, -558933, -634910, 969568, -190375),
    }
    names = (("capex (10)", cap), ("gross saving (8)", gs), ("FERA (6)", fera), ("NCT paid (7)", nct), ("gap (58)", gap),
             ("net lending (14)", nl), ("sector disc (57)", sd))
    for p in QS6:
        for k, (nm, code) in enumerate(names):
            v = tab[p][k]
            R(130, f"{p} {nm} {v:,}", str(v), "$m SAAR", code, p, lambda code=code, p=p: M(code, p))
    R(126, "identity holds to +/-$1m in every one of the last ten quarters", "1", "max abs diff $m", "line10-(line8-line6) vs FA105005305.Q",
      "2023:Q4-2026:Q1", lambda: max(abs(M(cap, p) - (M(gs, p) - M(fera, p)) - M(gap, p)) for p in qrange("2023:Q3", "2026:Q1")),
      "largest absolute difference over the ten quarters ending 2026:Q1; MATCH when it is at most the quoted 1", mode="le")
    for y, v in ((2019, -13531), (2020, -140001), (2021, -168164), (2022, 265020), (2023, 7749), (2024, 97749), (2025, -131245)):
        R(137, f"Annual average of quarterly SAAR gap {y} {v:+,}", str(v), "$m SAAR", gap, str(y),
          lambda y=y: S(gap, [f"{y}:Q{i}" for i in (1, 2, 3, 4)]) / 4.0, "mean of the four quarterly SAAR values")
    R(139, "net capital transfers received of $558,933m SAAR", "558933", "$m SAAR", nct + " (sign reversed)", "2026:Q1", lambda: -M(nct, "2026:Q1"),
      "the Z.1 line is 'paid' and is -558,933; 'received' is its negative")
    prior = qrange("2021:Q4", "2025:Q4")
    R(139, "sixteen quarters run between -$47,889m", "-47889", "$m SAAR", nct + " (sign reversed)", "2022:Q1-2025:Q4",
      lambda: min(-M(nct, p) for p in prior), "reading a of 2: transfers RECEIVED (= minus the paid line); minimum over the 16 quarters before 2026:Q1")
    R(139, "sixteen quarters run ... and +$103,700m", "103700", "$m SAAR", nct + " (sign reversed)", "2022:Q1-2025:Q4",
      lambda: max(-M(nct, p) for p in prior), "reading a of 2: transfers RECEIVED; maximum over the same 16 quarters")
    R(139, "sixteen quarters run between -$47,889m", "-47889", "$m SAAR", nct, "2022:Q1-2025:Q4",
      lambda: min(M(nct, p) for p in prior), "reading b of 2: the line as printed (paid); minimum")
    R(139, "sixteen quarters run ... and +$103,700m", "103700", "$m SAAR", nct, "2022:Q1-2025:Q4",
      lambda: max(M(nct, p) for p in prior), "reading b of 2: the line as printed (paid); maximum")
    R(142, "3,419,808 = gross saving less the transfer", "3419808", "$m SAAR", gs + " + " + nct, "2026:Q1", lambda: M(gs, "2026:Q1") + M(nct, "2026:Q1"))
    R(142, "underlying gap 3,199,548 - (3,419,808 - 144,283) = -75,977", "-75977", "$m SAAR", f"{cap} - ({gs} + {nct} - {fera})", "2026:Q1",
      lambda: M(cap, "2026:Q1") - (M(gs, "2026:Q1") + M(nct, "2026:Q1") - M(fera, "2026:Q1")))
    R(145, "roughly -$76bn, not -$635bn", "-76", "$bn SAAR", f"{cap} - ({gs} + {nct} - {fera})", "2026:Q1",
      lambda: (M(cap, "2026:Q1") - (M(gs, "2026:Q1") + M(nct, "2026:Q1") - M(fera, "2026:Q1"))) / 1000.0, "also quoted at lines 377 and 974 (-76 / -635)")
    R(145, "Eighty-eight percent of the apparent 2026:Q1 surplus is one transfer", "88", "%", nct + " / " + gap, "2026:Q1",
      lambda: 100.0 * (-M(nct, "2026:Q1")) / (-M(gap, "2026:Q1")), "transfer received / absolute gap")
    R(147, "gross investment (9) 4,169,116", "4169116", "$m SAAR", gi, "2026:Q1", lambda: M(gi, "2026:Q1"))
    R(147, "gross investment (9) = capex (10) + net lending (14)", "4169116", "$m SAAR", cap + " + " + nl, "2026:Q1", lambda: M(cap, "2026:Q1") + M(nl, "2026:Q1"))
    R(147, "3,978,741 - 4,169,116 = -190,375 = FA107005005", "-190375", "$m SAAR", gs + " - " + gi, "2026:Q1", lambda: M(gs, "2026:Q1") - M(gi, "2026:Q1"))
    R(147, "disagree by $190bn to $866bn SAAR (smallest)", "190", "$bn SAAR", sd, "2024:Q4-2026:Q1",
      lambda: min(abs(M(sd, p)) for p in QS6) / 1000.0, "reading a of 2: the six quarters printed in the note's table")
    R(147, "disagree by $190bn to $866bn SAAR (largest)", "866", "$bn SAAR", sd, "2024:Q4-2026:Q1",
      lambda: max(abs(M(sd, p)) for p in QS6) / 1000.0, "reading a of 2: the six quarters printed in the note's table")
    R(147, "disagree by $190bn to $866bn SAAR (smallest)", "190", "$bn SAAR", sd, "2023:Q4-2026:Q1",
      lambda: min(abs(M(sd, p)) for p in qrange("2023:Q3", "2026:Q1")) / 1000.0, "reading b of 2: the last ten quarters")
    R(147, "disagree by $190bn to $866bn SAAR (largest)", "866", "$bn SAAR", sd, "2023:Q4-2026:Q1",
      lambda: max(abs(M(sd, p)) for p in qrange("2023:Q3", "2026:Q1")) / 1000.0, "reading b of 2: the last ten quarters")
    c, o, m = "FL103163005.Q", "FL104135005.Q", "FL103168005.Q"
    R(149, "NFC corporate bonds FL103163005 = 8,036,583 ($8.04tn)", "8036583", "$m level", c, "2026:Q1", lambda: M(c, "2026:Q1"))
    R(149, "NFC corporate bonds outstanding ($8.04tn", "8.04", "$tn", c, "2026:Q1", lambda: M(c, "2026:Q1") / 1e6)
    R(149, "from $7.80tn a year earlier", "7.80", "$tn", c, "2025:Q1", lambda: M(c, "2025:Q1") / 1e6)
    R(46, "FRED returns 8,036,583 for 2026-01-01", "8036583", "$m level", c, "2026:Q1", lambda: M(c, "2026:Q1"),
      "FRED id BOGZ1FL103163005Q is not reachable offline; this checks the package value the note says FRED equalled")
    R(149, "total loans liability FL104135005 = 5,510,767", "5510767", "$m level", o, "2026:Q1", lambda: M(o, "2026:Q1"))
    R(149, "depository institution loans n.e.c. FL103168005 = 1,184,780", "1184780", "$m level", m, "2026:Q1", lambda: M(m, "2026:Q1"))
    R(149, "(from 1,061,735", "1061735", "$m level", m, "2025:Q1", lambda: M(m, "2025:Q1"))
    R(149, "+11.6% y/y", "11.6", "%", m, "2025:Q1-2026:Q1", lambda: 100.0 * (M(m, "2026:Q1") / M(m, "2025:Q1") - 1))
    R(149, "other loans and advances FL103169005 = 2,850,427", "2850427", "$m level", "FL103169005.Q", "2026:Q1", lambda: M("FL103169005.Q", "2026:Q1"))
    e = "FA103164105.Q"
    R(149, "Net equity issuance FA103164105 +124,412 SAAR", "124412", "$m SAAR", e, "2026:Q1", lambda: M(e, "2026:Q1"))
    R(149, "(-646,776 in 2024:Q1)", "-646776", "$m SAAR", e, "2024:Q1", lambda: M(e, "2024:Q1"))

    def neg_run():
        n = 0
        ps = qrange("2015:Q4", "2025:Q4")[::-1]
        for p in ps:
            if M(e, p) < 0:
                n += 1
            else:
                break
        return float(n)
    R(149, "after eight straight quarters of net retirement", "8", "quarters", e, "2024:Q1-2025:Q4", neg_run,
      "reading a of 2: run of consecutive negative quarters ending 2025:Q4, before the positive 2026:Q1")
    R(149, "after eight straight quarters of net retirement", "8", "quarters", e, "2024:Q1-2025:Q4",
      lambda: float(sum(1 for p in qrange("2023:Q4", "2025:Q4") if M(e, p) < 0)),
      "reading b of 2: negative quarters within the window the note anchors at 2024:Q1; the run actually reaches back much further (reading a)")
    R(149, "Domestic nonfinancial business debt grew 7.0% SAAR in 2026:Q1", "7.0", "% SAAR", "FG144104005.Q", "2026:Q1", lambda: M("FG144104005.Q", "2026:Q1"),
      "'nonfinancial business' (corporate plus noncorporate), table D3.g")
    R(149, "nonfinancial corporate alone 8.8%", "8.8", "% SAAR", "FG104104005.Q", "2026:Q1", lambda: M("FG104104005.Q", "2026:Q1"))
    R(149, "against household debt at 2.6%", "2.6", "% SAAR", "FG154104005.Q", "2026:Q1", lambda: M("FG154104005.Q", "2026:Q1"))

    # ------------------------------------------------------------------ section 4a
    secs = ["FU155000905", "FU115000905", "FU105000905", "FU795000995", "FU315000995", "FU215000995"]
    ann = {2019: (-511185, 454148, 57037, 0), 2020: (-691299, 570717, 120582, 0), 2021: (-914347, 876515, 37832, -1),
           2022: (-1001838, 1002240, -401, 1), 2023: (-1271195, 945340, 325857, 2), 2024: (-1473428, 1177132, 296296, 0),
           2025: (-1364010, 1134388, 229623, 1)}
    for y, (sdm, row, disc, res) in ann.items():
        yy = str(y)
        sa = lambda yy=yy: M("FU885000985.A", yy)
        sb = lambda yy=yy: sum(M(c + ".A", yy) for c in secs)
        R(176, f"{y} sum of domestic sectors {sdm:,}", str(sdm), "$m", "FU885000985.A", yy, sa, "reading a of 2: the published all-domestic-sectors line")
        R(176, f"{y} sum of domestic sectors {sdm:,}", str(sdm), "$m", "+".join(secs), yy, sb, "reading b of 2: the six listed sectors added up")
        R(176, f"{y} rest of world {row:,}", str(row), "$m", "FU265000905.A", yy, lambda yy=yy: M("FU265000905.A", yy))
        R(176, f"{y} statistical discrepancy {disc:,}", str(disc), "$m", "FU087005995.A", yy, lambda yy=yy: M("FU087005995.A", yy))
        R(176, f"{y} residual {res:+,}" if res else f"{y} residual 0", str(res), "$m", "FU885000985.A + FU265000905.A + FU087005995.A", yy,
          lambda yy=yy: sa() + M("FU265000905.A", yy) + M("FU087005995.A", yy), "reading a of 2: published domestic total")
        R(176, f"{y} residual {res:+,}" if res else f"{y} residual 0", str(res), "$m", "six sectors + FU265000905.A + FU087005995.A", yy,
          lambda yy=yy: sb() + M("FU265000905.A", yy) + M("FU087005995.A", yy), "reading b of 2: six listed sectors")
    qres = (("2025:Q1", 22140), ("2025:Q2", -21033), ("2025:Q3", -22831), ("2025:Q4", 21726))
    for p, v in qres:
        R(187, f"Recomputed 2025 quarters residual {p} {v:+,}", str(v), "$m", "FU885000985.Q + FU265000905.Q + FU087005995.Q", p,
          lambda p=p: M("FU885000985.Q", p) + M("FU265000905.Q", p) + M("FU087005995.Q", p), "reading a of 2: published domestic total, NSA quarterly amounts")
        R(187, f"Recomputed 2025 quarters residual {p} {v:+,}", str(v), "$m", "six sectors + FU265000905.Q + FU087005995.Q", p,
          lambda p=p: sum(M(c + ".Q", p) for c in secs) + M("FU265000905.Q", p) + M("FU087005995.Q", p), "reading b of 2: six listed sectors")
    R(187, "summing to +2 over the year", "2", "$m", "FU885000985.Q + FU265000905.Q + FU087005995.Q", "2025",
      lambda: sum(M("FU885000985.Q", p) + M("FU265000905.Q", p) + M("FU087005995.Q", p) for p in QS6[1:5]), "reading a of 2: published domestic total")
    R(187, "summing to +2 over the year", "2", "$m", "six sectors + FU265000905.Q + FU087005995.Q", "2025",
      lambda: sum(sum(M(c + ".Q", p) for c in secs) + M("FU265000905.Q", p) + M("FU087005995.Q", p) for p in QS6[1:5]), "reading b of 2: six listed sectors")
    for nm, code, v in (("HH", "FU155000905", 284721), ("nonfinancial noncorp", "FU115000905", 66557), ("NFC", "FU105000905", 72606),
                        ("domestic financial", "FU795000995", 169513), ("federal", "FU315000995", -602672), ("state & local", "FU215000995", -54729),
                        ("ROW", "FU265000905", 231062), ("statistical discrepancy", "FU087005995", -133080)):
        R(189, f"2026:Q1 {nm} {v:+,}", str(v), "$m", code + ".Q", "2026:Q1", lambda code=code: M(code + ".Q", "2026:Q1"), "NSA quarterly amount (FU, .Q)")
    R(189, "government (federal + S&L) -$1,116bn combined", "-1116", "$bn", "FU315000995.A + FU215000995.A", "2025",
      lambda: (M("FU315000995.A", "2025") + M("FU215000995.A", "2025")) / 1000.0, "annual capital-account net lending, federal plus state and local")
    R(189, "the 2025 annual federal balance is the dominant term", "-1908", "$bn", "FU315000995.A", "2025", lambda: M("FU315000995.A", "2025") / 1000.0,
      "the note's '-$1,908bn-scale' phrase is garbled; this tests the 2025 annual federal figure as one reading of it")
    R(189, "ROW +$1,134bn", "1134", "$bn", "FU265000905.A", "2025", lambda: M("FU265000905.A", "2025") / 1000.0, "also line 183 (1,134,388)")

    # ------------------------------------------------------------------ section 4b
    cols = (("HH", "FA155000005"), ("Nonfin bus", "FA145000005"), ("Federal", "FA315000005"), ("S&L", "FA215000005"),
            ("Domestic fin", "FA795000005"), ("ROW", "FA265000005"), ("All sectors", "FA895000005"), ("Instrument disc", "FA905000005"))
    fa = {
        "2019:Q4": (2298846, 162921, -1127623, -404070, 78614, 206154, 1214842, -1214842),
        "2024:Q4": (1478965, 505423, -2454832, -295850, -52652, 1125620, 306674, -306674),
        "2025:Q3": (1695997, -767717, -2163708, -389398, 386915, 1459399, 221487, -221487),
        "2025:Q4": (434850, 526509, -1593949, -375933, 127729, -344155, -1224949, 1224949),
        "2026:Q1": (2246009, 980680, -2670491, -334250, 947742, 1057846, 2227535, -2227535),
    }
    for p in QS5:
        for k, (nm, code) in enumerate(cols):
            v = fa[p][k]
            R(199 + QS5.index(p), f"{p} {nm} {v:+,}", str(v), "$m SAAR", code + ".Q", p, lambda code=code, p=p: M(code + ".Q", p))
    R(205, "FA895000005 + FA905000005 = 0 every quarter", "0", "max abs sum $m", "FA895000005.Q + FA905000005.Q", "2019:Q4-2026:Q1",
      lambda: max(abs(M("FA895000005.Q", p) + M("FA905000005.Q", p)) for p in qrange("2019:Q3", "2026:Q1")), "largest absolute sum over every quarter 2019:Q4-2026:Q1; MATCH when 0", mode="le")
    R(205, "instrument discrepancy running $0.2tn to $2.2tn (low)", "0.2", "$tn SAAR", "FA905000005.Q", "table quarters",
      lambda: min(abs(M("FA905000005.Q", p)) for p in QS5) / 1e6, "reading a of 2: smallest absolute value over the five quarters in the note's table")
    R(205, "instrument discrepancy running $0.2tn to $2.2tn (high)", "2.2", "$tn SAAR", "FA905000005.Q", "table quarters",
      lambda: max(abs(M("FA905000005.Q", p)) for p in QS5) / 1e6, "reading a of 2: largest absolute value over the five quarters in the note's table")
    R(205, "instrument discrepancy running $0.2tn to $2.2tn (low)", "0.2", "$tn SAAR", "FA905000005.Q", "2019:Q4-2026:Q1",
      lambda: min(abs(M("FA905000005.Q", p)) for p in qrange("2019:Q3", "2026:Q1")) / 1e6, "reading b of 2: every quarter 2019:Q4-2026:Q1; a small quarter breaks the stated floor")
    R(205, "instrument discrepancy running $0.2tn to $2.2tn (high)", "2.2", "$tn SAAR", "FA905000005.Q", "2019:Q4-2026:Q1",
      lambda: max(abs(M("FA905000005.Q", p)) for p in qrange("2019:Q3", "2026:Q1")) / 1e6, "reading b of 2: every quarter 2019:Q4-2026:Q1")
    f0 = (("Total miscellaneous assets", "FA903090005", 2612575, -3046125), ("Fed funds and repo", "FA902050005", -1049788, 575905),
          ("Taxes receivable", "FA903078005", -422547, -219998), ("Interbank", "FA904010005", 75412, 189017),
          ("Total discrepancy", "FA907005005", 995518, -2514576))
    for nm, code, a, b in f0:
        R(209, f"F0.t {nm} 2025:Q4 {a:+,}", str(a), "$m SAAR", code + ".Q", "2025:Q4", lambda code=code: M(code + ".Q", "2025:Q4"))
        R(209, f"F0.t {nm} 2026:Q1 {b:+,}", str(b), "$m SAAR", code + ".Q", "2026:Q1", lambda code=code: M(code + ".Q", "2026:Q1"))

    # ------------------------------------------------------------------ section 5: NBFI, hedge funds, derivatives
    desc_all = [(c, ds, t) for t, lst in DIC.items() for (c, ds, ln) in lst]
    for ln, s in ((247, "private equity"), (247, "private credit"), (247, "business development"), (247, "private fund")):
        R(ln, f"scanned all 286 data dictionaries for '{s}': zero hits", "0", "hits", "data_dictionary/*.txt", "n/a",
          lambda s=s: float(len({c for c, ds, t in desc_all if s in ds.lower()})), "distinct series codes whose description contains the string (case-insensitive)")
    dv = {c for c, ds, t in desc_all if "derivativ" in ds.lower()}
    R(249, "scan for derivativ returns exactly six series", "6", "series", "data_dictionary/*.txt", "n/a", lambda: float(len(dv)),
      "reading a of 2: distinct mnemonics (with frequency suffix) whose description contains 'derivativ'; " + ", ".join(sorted(dv)))
    R(249, "scan for derivativ returns ... across four concepts", "4", "concepts", "data_dictionary/*.txt", "n/a",
      lambda: float(len({c[2:11] for c in dv})), "distinct nine-digit cores among those mnemonics")
    R(250, "FL263098013 asset $1,967,834 at 2025:Q4", "1967834", "$m level", "FL263098013.Q", "2025:Q4", lambda: M("FL263098013.Q", "2025:Q4"))
    R(250, "FL263198013 liability $1,959,210 at 2025:Q4", "1959210", "$m level", "FL263198013.Q", "2025:Q4", lambda: M("FL263198013.Q", "2025:Q4"))
    R(250, "ROW derivatives are one quarter stale (last non-ND quarter)", "2025:Q4", "quarter", "FL263098013.Q", "n/a",
      lambda: max(p for p in Z["FL263098013.Q"] if ":Q" in p))
    R(258, "S124.7.b data run through 2025:Q4", "2025:Q4", "quarter", "FL622000623.Q", "n/a", lambda: max(p for p in Z["FL622000623.Q"] if ":Q" in p))
    R(258, "hedge funds total assets FL622000623 = 3,596,778", "3596778", "$m level", "FL622000623.Q", "2025:Q4", lambda: M("FL622000623.Q", "2025:Q4"))
    R(258, "total financial assets FL624090005 = 3,442,787", "3442787", "$m level", "FL624090005.Q", "2025:Q4", lambda: M("FL624090005.Q", "2025:Q4"))
    R(258, "total loans liability FL624135005 = 1,098,114", "1098114", "$m level", "FL624135005.Q", "2025:Q4", lambda: M("FL624135005.Q", "2025:Q4"))
    R(260, "FL624135035 prime brokerage borrowing = 774,026 at 2025:Q4", "774026", "$m level", "FL624135035.Q", "2025:Q4", lambda: M("FL624135035.Q", "2025:Q4"))
    R(260, "up from 536,466 at 2024:Q4", "536466", "$m level", "FL624135035.Q", "2024:Q4", lambda: M("FL624135035.Q", "2024:Q4"))
    R(260, "(+44.3%)", "44.3", "%", "FL624135035.Q", "2024:Q4-2025:Q4", lambda: 100.0 * (M("FL624135035.Q", "2025:Q4") / M("FL624135035.Q", "2024:Q4") - 1))
    R(264, "S127.2 total financial assets FL504090005 = 1,529,292", "1529292", "$m level", "FL504090005.Q", "2026:Q1", lambda: M("FL504090005.Q", "2026:Q1"))
    R(264, "(up from 1,324,646 a year earlier)", "1324646", "$m level", "FL504090005.Q", "2025:Q1", lambda: M("FL504090005.Q", "2025:Q1"))
    R(264, "other loans and advances FL503069005 is 99,278", "99278", "$m level", "FL503069005.Q", "2026:Q1", lambda: M("FL503069005.Q", "2026:Q1"))

    # holders of NFC other loans (268-280)
    R(271, "Holder of NFC other loans and advances ($2,850,427 total)", "2850427", "$m level", "FL103169005.Q", "2026:Q1", lambda: M("FL103169005.Q", "2026:Q1"))
    R(272, "Rest of the world FL263069500 1,192,393", "1192393", "$m level", "FL263069500.Q", "2026:Q1", lambda: M("FL263069500.Q", "2026:Q1"))
    R(273, "Finance companies FL613069505 706,410", "706410", "$m level", "FL613069505.Q", "2026:Q1", lambda: M("FL613069505.Q", "2026:Q1"),
      "reading a of 2: the asset line named in the note (includes loans to noncorporate business and PPP loans)")
    R(273, "Finance companies FL613069505 706,410", "706410", "$m level", "FL103169535.Q", "2026:Q1", lambda: M("FL103169535.Q", "2026:Q1"),
      "reading b of 2: NFC-liability line for finance-company loans (the note uses 635,014 / 635.0bn for this at lines 323 and 793)")
    R(274, "ABS issuers 361,947 (syndicated + securitised)", "361947", "$m level", "FL673069803.Q + FL673069505.Q", "2026:Q1",
      lambda: M("FL673069803.Q", "2026:Q1") + M("FL673069505.Q", "2026:Q1"), "F4.6.s lists FL673069505 on two lines (52, 53); counted once here")
    R(275, "Federal government 259,538", "259538", "$m level", "FL103169205.Q", "2026:Q1", lambda: M("FL103169205.Q", "2026:Q1"),
      "NFC 'U.S. government loans' liability line; the note gives no code for this row")
    R(276, "Households and nonprofits FL153069803 130,993", "130993", "$m level", "FL153069803.Q", "2026:Q1", lambda: M("FL153069803.Q", "2026:Q1"))
    R(277, "Mutual funds FL653069803 103,444", "103444", "$m level", "FL653069803.Q", "2026:Q1", lambda: M("FL653069803.Q", "2026:Q1"))
    R(278, "Broker-dealers FL663069803 58,740", "58740", "$m level", "FL663069803.Q", "2026:Q1", lambda: M("FL663069803.Q", "2026:Q1"))
    R(279, "Life insurers, general accounts FL543069873 36,766", "36766", "$m level", "FL543069873.Q", "2026:Q1", lambda: M("FL543069873.Q", "2026:Q1"))
    R(280, "Other financial business FL503069805 10,155", "10155", "$m level", "FL503069805.Q", "2026:Q1", lambda: M("FL503069805.Q", "2026:Q1"))
    R(282, "FL153069803 sits in lines 45-51 of F4.6 (first syndicated line)", "45", "line number", "FL103169803.Q", "n/a", lambda: float(lineno("F4_6_s", "FL103169803.Q")))
    R(282, "syndicated-loan block ends at line 51 of F4.6", "51", "line number", "FL503069805.Q", "n/a", lambda: float(lineno("F4_6_s", "FL503069805.Q")))
    R(282, "At $130,993 it is far too small", "130993", "$m level", "FL153069803.Q", "2026:Q1", lambda: M("FL153069803.Q", "2026:Q1"), "repeat of line 276")
    R(284, "FL663168005 broker-dealer depository loans = 589,456", "589456", "$m level", "FL663168005.Q", "2026:Q1", lambda: M("FL663168005.Q", "2026:Q1"))
    R(284, "from 404,207 a year earlier", "404207", "$m level", "FL663168005.Q", "2025:Q1", lambda: M("FL663168005.Q", "2025:Q1"))
    R(284, "(+45.8%)", "45.8", "%", "FL663168005.Q", "2025:Q1-2026:Q1", lambda: 100.0 * (M("FL663168005.Q", "2026:Q1") / M("FL663168005.Q", "2025:Q1") - 1),
      "also quoted at line 378 (+45.8% y/y)")
    R(284, "margin receivables FL663067005 in F4.6 line 35", "35", "line number", "FL663067005.Q", "n/a", lambda: float(lineno("F4_6_s", "FL663067005.Q")))
    R(284, "margin receivables FL663067003 in F4.6 line 36", "36", "line number", "FL663067003.Q", "n/a", lambda: float(lineno("F4_6_s", "FL663067003.Q")))

    # ROW (290-299)
    R(294, "FL263069563 U.S. nonfinancial business loans held by CLOs = 658,951", "658951", "$m level", "FL263069563.Q", "2026:Q1", lambda: M("FL263069563.Q", "2026:Q1"))
    R(294, "(from 633,188 a year earlier)", "633188", "$m level", "FL263069563.Q", "2025:Q1", lambda: M("FL263069563.Q", "2025:Q1"))
    R(295, "LM263163063 collateralized loan obligation bonds = 598,112", "598112", "$m level", "LM263163063.Q", "2026:Q1", lambda: M("LM263163063.Q", "2026:Q1"))
    R(295, "(from 550,468)", "550468", "$m level", "LM263163063.Q", "2025:Q1", lambda: M("LM263163063.Q", "2025:Q1"))
    R(296, "FL263140005 life insurance reserve credit liability = 140,215", "140215", "$m level", "FL263140005.Q", "2026:Q1", lambda: M("FL263140005.Q", "2026:Q1"))
    R(296, "US cedant's FL543076035 = 1,125,345", "1125345", "$m level", "FL543076035.Q", "2026:Q1", lambda: M("FL543076035.Q", "2026:Q1"))
    R(299, "Z.1 cession flow printed negative in 2025 (sign test)", "-1", "sign", "FA543076035.Q", "2025:Q1-2025:Q4",
      lambda: -1.0 if all(M("FA543076035.Q", p) < 0 for p in QS6[1:5]) else 1.0, "all four 2025 quarters negative; the number itself is quoted at Handbook line 346")

    # ------------------------------------------------------------------ section 7: FWTW (Enhanced Financial Accounts, a different Fed release)
    FW = "DIFFERENT RELEASE: holder split comes from the Fed Enhanced Financial Accounts FWTW file (fwtw_data.csv, updated 2026-06-18), not from the Z.1 package; a difference would be possible revision, not error. "

    def fw(line, text, q, codes, note_zcheck=None, ztot=None):
        """FWTW holder values: not in the zip. Look for the same number in any 2026:Q1 level series as a courtesy and say so."""
        hits = sorted(c for c, v in Z.items() if c.startswith(("FL", "LM")) and abs(v.get("2026:Q1", 1e18) - float(q)) <= 0.5) if float(q) >= 100000 else []
        if hits:
            rows.append([NOTE, line, text, q, q, "$m level", ", ".join(hits[:3]), "2026:Q1", "MATCH within rounding",
                         FW + "The same number sits in the Z.1 package as " + ", ".join(hits[:3]) + "; matched by value, so the holder mapping is inferred."])
        else:
            NF(line, text, q, "$m level", codes, "2026:Q1", FW + "No Z.1 level series carries this number at 2026:Q1.")
    totals = (("Corporate & foreign bonds total 8,036,583", "8036583", "FL103163005.Q"), ("Unidentified misc. financial claims 12,101,882", "12101882", "FL103193005.Q"),
              ("Trade credit total 4,523,214", "4523214", "FL103170005.Q"), ("Other loans and advances total 2,850,427", "2850427", "FL103169005.Q"),
              ("Commercial mortgages total 1,202,775", "1202775", "FL103165505.Q"), ("Depository loans n.e.c. total 1,184,780", "1184780", "FL103168005.Q"))
    for txt, q, code in totals:
        R(320, txt, q, "$m level", code, "2026:Q1", lambda code=code: M(code, "2026:Q1"), "instrument total, which is in the Z.1 package; reading a of 2 for commercial mortgages (FL103165505)" if "mortgages" in txt else "instrument total, which is in the Z.1 package")
    R(320, "Commercial mortgages total 1,202,775", "1202775", "$m level", "FL103165005.Q", "2026:Q1", lambda: M("FL103165005.Q", "2026:Q1"),
      "reading b of 2: ALL NFC mortgages; the row above uses FL103165505 (commercial mortgages), which is the match")
    for line, txt, q in ((320, "bonds: Rest of world 3,094,914", "3094914"), (320, "bonds: life insurers 1,508,358", "1508358"), (320, "bonds: mutual funds 1,122,251", "1122251"),
                         (320, "bonds: pensions 637,988", "637988"), (320, "bonds: ETFs 612,278", "612278"), (320, "bonds: P&C 392,818", "392818"),
                         (320, "bonds: US banks 291,056", "291056"), (321, "misc claims: NFC itself 7,436,191", "7436191"), (321, "misc claims: nonfin noncorp 4,201,860", "4201860"),
                         (321, "misc claims: pensions 1,425,434", "1425434"), (322, "Trade credit: NFC 3,234,897", "3234897"), (322, "Trade credit: nonfin noncorp 813,270", "813270"),
                         (322, "Trade credit: ROW 345,670", "345670"), (323, "Other loans: ROW 1,192,393", "1192393"), (323, "Other loans: finance cos 635,014", "635014"),
                         (323, "Other loans: ABS 361,947", "361947"), (324, "Commercial mortgages: US banks 672,042", "672042"), (324, "Commercial mortgages: ABS 155,440", "155440"),
                         (324, "Commercial mortgages: life 153,513", "153513"), (325, "Depository loans: US banks 921,600", "921600"),
                         (325, "Depository loans: foreign banking offices in US 252,417", "252417")):
        fw(line, txt, q, "FWTW holder cell (no Z.1 code)")
    NF(309, "fwtw_data.csv (77.8 MB, 921,121 rows, verified)", "921121", "rows", "fwtw_data.csv", "1945Q4-2026Q1", FW + "File not in the package.")
    NF(312, "Coverage 1945Q4 through 2026Q1, updated 18 June 2026", "2026Q1", "last quarter", "fwtw_data.csv", "n/a", FW + "File not in the package.")

    # ------------------------------------------------------------------ section 8
    R(333, "FL663193005 broker-dealer unidentified misc = -439,865", "-439865", "$m level", "FL663193005.Q", "2026:Q1", lambda: M("FL663193005.Q", "2026:Q1"))
    R(333, "FL663093005 = -351,250", "-351250", "$m level", "FL663093005.Q", "2026:Q1", lambda: M("FL663093005.Q", "2026:Q1"))
    R(339, "All sectors unidentified misc assets FL893093005 23,532,650", "23532650", "$m level", "FL893093005.Q", "2026:Q1", lambda: M("FL893093005.Q", "2026:Q1"))
    R(340, "unidentified misc liabilities FL893193005 18,636,711", "18636711", "$m level", "FL893193005.Q", "2026:Q1", lambda: M("FL893193005.Q", "2026:Q1"))
    R(341, "Instrument discrepancy FL903090005 -4,895,939", "-4895939", "$m level", "FL903090005.Q", "2026:Q1", lambda: M("FL903090005.Q", "2026:Q1"))
    R(343, "$23.5tn of assets", "23.5", "$tn", "FL893093005.Q", "2026:Q1", lambda: M("FL893093005.Q", "2026:Q1") / 1e6)
    R(343, "$18.6tn of liabilities", "18.6", "$tn", "FL893193005.Q", "2026:Q1", lambda: M("FL893193005.Q", "2026:Q1") / 1e6)
    R(343, "fail to reconcile by $4.9tn", "4.9", "$tn", "FL893093005.Q - FL893193005.Q", "2026:Q1", lambda: (M("FL893093005.Q", "2026:Q1") - M("FL893193005.Q", "2026:Q1")) / 1e6,
      "reading a of 2: assets minus liabilities of the all-sectors line")
    R(343, "fail to reconcile by $4.9tn", "4.9", "$tn", "FL903090005.Q", "2026:Q1", lambda: -M("FL903090005.Q", "2026:Q1") / 1e6, "reading b of 2: the instrument discrepancy, sign reversed")
    R(343, "nonfinancial corporate business alone carries $12,101,882", "12101882", "$m level", "FL103193005.Q", "2026:Q1", lambda: M("FL103193005.Q", "2026:Q1"))
    R(343, "nonfinancial noncorporate $4,434,951", "4434951", "$m level", "FL113193003.Q", "2026:Q1", lambda: M("FL113193003.Q", "2026:Q1"),
      "the note gives no code; the noncorporate unidentified-miscellaneous liability line is FL113193003 (FL113193005 does not exist)")
    R(343, "grew $1.88tn on the asset side in one year", "1.88", "$tn", "FL893093005.Q", "2025:Q1-2026:Q1", lambda: (M("FL893093005.Q", "2026:Q1") - M("FL893093005.Q", "2025:Q1")) / 1e6)
    R(343, "(from 21,649,093 at 2025:Q1)", "21649093", "$m level", "FL893093005.Q", "2025:Q1", lambda: M("FL893093005.Q", "2025:Q1"))

    # ------------------------------------------------------------------ shadow-money section: Z.1-based pieces
    R(612, "$3,040.7bn Z.1 GAAP-netted measure (broker-dealer repo)", "3040.7", "$bn level", "FL662151003.Q", "2026:Q1", lambda: B("FL662151003.Q", "2026:Q1"),
      "the note gives no code; FL662151003 'Security brokers and dealers; security repurchase agreements; liability' is the match by value and label")
    R(644, "FL663168005 $541.8bn at 2025:Q4", "541.8", "$bn level", "FL663168005.Q", "2025:Q4", lambda: B("FL663168005.Q", "2025:Q4"),
      "this section names no Z.1 release; if it came from the 2026-03-19 release (first with 2025:Q4) a difference is possible revision")
    R(644, "+53.5% y/y", "53.5", "%", "FL663168005.Q", "2024:Q4-2025:Q4", lambda: 100.0 * (M("FL663168005.Q", "2025:Q4") / M("FL663168005.Q", "2024:Q4") - 1),
      "reading a of 2: 2025:Q4 over 2024:Q4")
    R(644, "+53.5% y/y", "53.5", "%", "FL663168005.Q", "2025:Q1-2026:Q1", lambda: 100.0 * (M("FL663168005.Q", "2026:Q1") / M("FL663168005.Q", "2025:Q1") - 1),
      "reading b of 2: 2026:Q1 over 2025:Q1 (the +45.8% of line 284)")
    R(644, "FL613168005 depository loans to finance companies $289.8bn", "289.8", "$bn level", "FL613168005.Q", "2026:Q1", lambda: B("FL613168005.Q", "2026:Q1"))
    R(648, "trade credit $895.5bn SAAR for nonfinancial corporates (F81.t)", "895.5", "$bn SAAR", "FA103170005.Q", "2026:Q1", lambda: B("FA103170005.Q", "2026:Q1"),
      "reading a of 2: trade payables liability line (the note gives no code)")
    R(648, "trade credit $895.5bn SAAR for nonfinancial corporates (F81.t)", "895.5", "$bn SAAR", "FA103070005.Q", "2026:Q1", lambda: B("FA103070005.Q", "2026:Q1"),
      "reading b of 2: trade receivables asset line")
    for nm, q, ds in (("Total runnable money-like liabilities", "27033", "Fed FSR May 2026 Table 4.1"), ("Domestic MMFs", "7746", "Fed FSR"),
                      ("Repurchase agreements", "5887", "Fed FSR"), ("Commercial paper", "1368", "Fed FSR")):
        NZ(499, f"FSR runnables {nm} {q}", q, "$bn", "FL634090005.Q etc. are inputs", "2025:Q4",
           f"{ds}, not a Z.1 table; out of scope. Z.1 comparator: MMF total financial assets FL634090005 = {B('FL634090005.Q', '2025:Q4'):.1f} $bn at 2025:Q4, a different measure")

    # ------------------------------------------------------------------ critiques: D3.s table, debt/GDP
    d3 = (("Domestic nonfinancial sectors", "LA384104005", (36547, 55251, 66532, 81855)), ("Nonfinancial corporate", "LA104104005", (6478, 10886, 12696, 14454)),
          ("Households & NPO", "LA154104005", (14003, 16081, 18204, 21069)), ("Federal government", "LA314104005", (8883, 19040, 25304, 34473)),
          ("Domestic financial sectors", "LA794104005", (18471, 18684, 22401, 26108)))
    D4 = ("2009:Q4", "2019:Q4", "2021:Q4", "2026:Q1")
    for nm, code, vals in d3:
        for p, v in zip(D4, vals):
            R(767, f"{nm} {p} {v:,}", str(v), "$bn level", code + ".Q", p, lambda code=code, p=p: B(code + ".Q", p))
    gdpz = lambda p: 4.0 * M("FU086902005.Q", p)
    gdpb = lambda p: NQ["A191RC"][p.replace(":", "")] if "A191RC" in NQ else None
    for p, v in zip(D4, ("44.2", "49.6", "51.2", "45.4")):
        R(773, f"NFC debt/GDP {v}% ({p})", v, "%", "LA104104005.Q / (4 x FU086902005.Q)", p, lambda p=p: 100.0 * M("LA104104005.Q", p) / gdpz(p),
          "reading a of 3: GDP = Z.1 'GDP sum of pieces' quarterly amount x 4 (same release)")
        R(773, f"NFC debt/GDP {v}% ({p})", v, "%", "LA104104005.Q / BEA A191RC SAAR", p, lambda p=p: 100.0 * M("LA104104005.Q", p) / gdpb(p),
          "reading b of 3: GDP = BEA NipaDataQ A191RC SAAR as fetched 2026-11-11 (later vintage than the note's)")
        R(773, f"NFC debt/GDP {v}% ({p})", v, "%", "LA104104005.Q / sum of 4 quarters FU086902005.Q", p,
          lambda p=p: 100.0 * M("LA104104005.Q", p) / sum(M("FU086902005.Q", q) for q in qrange(prev4(p), p)),
          "reading c of 3: GDP = sum of the four quarters ending at p (Z.1 amounts)")
    R(773, "fallen 5.8pp since end-2021", "5.8", "pp", "LA104104005.Q / (4 x FU086902005.Q)", "2021:Q4-2026:Q1",
      lambda: 100.0 * (M("LA104104005.Q", "2021:Q4") / gdpz("2021:Q4") - M("LA104104005.Q", "2026:Q1") / gdpz("2026:Q1")), "reading a of 3 (Z.1 GDP x 4)")
    R(773, "fallen 5.8pp since end-2021", "5.8", "pp", "LA104104005.Q / BEA A191RC SAAR", "2021:Q4-2026:Q1",
      lambda: 100.0 * (M("LA104104005.Q", "2021:Q4") / gdpb("2021:Q4") - M("LA104104005.Q", "2026:Q1") / gdpb("2026:Q1")), "reading b of 3 (BEA SAAR)")
    R(773, "fallen 5.8pp since end-2021", "5.8", "pp", "LA104104005.Q / 4q sum", "2021:Q4-2026:Q1",
      lambda: 100.0 * (M("LA104104005.Q", "2021:Q4") / sum(M("FU086902005.Q", q) for q in qrange(prev4("2021:Q4"), "2021:Q4")) -
                       M("LA104104005.Q", "2026:Q1") / sum(M("FU086902005.Q", q) for q in qrange(prev4("2026:Q1"), "2026:Q1"))), "reading c of 3 (4-quarter sum)")
    R(781, "$69.5trn of NFC corporate equity liability", "69.5", "$tn", "FL103164105.Q", "2026:Q1", lambda: M("FL103164105.Q", "2026:Q1") / 1e6,
      "the note gives no code; LM103164105 holds the same value")
    R(185, "statistical discrepancy ... $326bn in 2023", "326", "$bn", "FU087005995.A", "2023", lambda: M("FU087005995.A", "2023") / 1000.0)
    R(185, "statistical discrepancy ... $296bn in 2024", "296", "$bn", "FU087005995.A", "2024", lambda: M("FU087005995.A", "2024") / 1000.0)
    R(779, "domestic financial sectors' own debt LA794104005 $26,108bn", "26108", "$bn level", "LA794104005.Q", "2026:Q1", lambda: B("LA794104005.Q", "2026:Q1"), "repeat of line 771")
    R(954, "$22,401bn (2021:Q4) -> $26,108bn (2026:Q1), +$3,707bn", "3707", "$bn", "LA794104005.Q", "2021:Q4-2026:Q1",
      lambda: B("LA794104005.Q", "2026:Q1") - B("LA794104005.Q", "2021:Q4"))
    # F4.6.s sums
    six = ("FL153069803.Q", "FL543069873.Q", "FL653069803.Q", "FL673069803.Q", "FL663069803.Q", "FL503069805.Q")
    for nm, q, code in (("households residual", "131.0", six[0]), ("life GA", "36.8", six[1]), ("mutual funds", "103.4", six[2]),
                        ("ABS issuers", "358.1", six[3]), ("brokers", "58.7", six[4]), ("other financial business", "10.2", six[5])):
        R(785, f"F4.6.s lines 46-51 {nm} ${q}bn", q, "$bn level", code, "2026:Q1", lambda code=code: B(code, "2026:Q1"))
    R(785, "sum of lines 46-51 = $698.2bn", "698.2", "$bn level", " + ".join(six), "2026:Q1", lambda: sum(B(c, "2026:Q1") for c in six))
    R(785, "equals FL103169803 $698.2bn, the NFC syndicated-loan liability", "698.2", "$bn level", "FL103169803.Q", "2026:Q1", lambda: B("FL103169803.Q", "2026:Q1"),
      "also at lines 400 and 408 of the shadow-money section (698.2 total)")
    R(785, "trade credit table fails to reconcile by -$889.3bn", "-889.3", "$bn level", "FL903070005.Q", "2026:Q1", lambda: B("FL903070005.Q", "2026:Q1"),
      "instrument discrepancy, trade receivables (F81 / F0)")
    R(793, "Finance-company loans to NFCs add $635.0bn (FL103169535)", "635.0", "$bn level", "FL103169535.Q", "2026:Q1", lambda: B("FL103169535.Q", "2026:Q1"))
    R(793, "US government loans $259.5bn", "259.5", "$bn level", "FL103169205.Q", "2026:Q1", lambda: B("FL103169205.Q", "2026:Q1"))
    R(796, "FL263069500 $830.8bn (2019:Q4)", "830.8", "$bn level", "FL263069500.Q", "2019:Q4", lambda: B("FL263069500.Q", "2019:Q4"))
    R(796, "-> $1,192.4bn (2026:Q1)", "1192.4", "$bn level", "FL263069500.Q", "2026:Q1", lambda: B("FL263069500.Q", "2026:Q1"))
    R(796, "+43.5%", "43.5", "%", "FL263069500.Q", "2019:Q4-2026:Q1", lambda: 100.0 * (M("FL263069500.Q", "2026:Q1") / M("FL263069500.Q", "2019:Q4") - 1))
    R(796, "F4.6.s line 66, FL263069500", "66", "line number", "FL263069500.Q", "n/a", lambda: float(max(ln for c, _, ln in DIC["F4_6_s"] if c == "FL263069500.Q")),
      "the code is listed on two lines, 65 and 66; the highest is tested")
    R(797, "S11.1.s line 44, FL103193005", "44", "line number", "FL103193005.Q", "n/a", lambda: float(lineno("S11_1_s", "FL103193005.Q")))
    R(797, "FL103193005 $9,422.8bn (2019:Q4)", "9422.8", "$bn level", "FL103193005.Q", "2019:Q4", lambda: B("FL103193005.Q", "2019:Q4"))
    R(797, "-> $12,101.9bn (2026:Q1)", "12101.9", "$bn level", "FL103193005.Q", "2026:Q1", lambda: B("FL103193005.Q", "2026:Q1"))
    R(797, "A $12.1trn residual ... larger than the entire measured debt stock", "1", "1 = larger", "FL103193005.Q vs LA104104005.Q", "2026:Q1",
      lambda: 1.0 if M("FL103193005.Q", "2026:Q1") > M("LA104104005.Q", "2026:Q1") else 0.0,
      "12,101.9 vs 14,454 $bn: not larger on the package's own numbers (the Handbook line 83 repeats the claim)")
    R(797, "larger than the entire $14.45trn measured debt stock", "14.45", "$tn", "LA104104005.Q", "2026:Q1", lambda: M("LA104104005.Q", "2026:Q1") / 1e6)
    R(799, "FL153069803 $131.0bn", "131.0", "$bn level", "FL153069803.Q", "2026:Q1", lambda: B("FL153069803.Q", "2026:Q1"))

    # ------------------------------------------------------------------ valuation trap (3.2)
    def fu_of(code):
        stem = code[2:-2]
        for tail in (stem, stem[:-1] + "5"):
            if "FU" + tail + ".Q" in Z:
                return "FU" + tail + ".Q"
        raise Missing(f"no FU series for {code}")

    def decomp(code, a, b):
        lv = M(code, b) - M(code, a)
        tr = S(fu_of(code), qrange(a, b))
        return lv / 1000.0, tr / 1000.0, (lv - tr) / 1000.0, 100.0 * (lv - tr) / lv

    W = ("2009:Q4", "2019:Q4", "2021:Q4", "2026:Q1")
    val = [
        ("Domestic financial sectors", "FL794090005.Q", "2009:Q4", "2019:Q4", ("36667.3", "20794.8", "15872.4", "43.3")),
        ("Domestic financial sectors", "FL794090005.Q", "2019:Q4", "2021:Q4", ("26987.5", "17086.1", "9901.5", "36.7")),
        ("Domestic financial sectors", "FL794090005.Q", "2021:Q4", "2026:Q1", ("20605.9", "16289.5", "4316.4", "20.9")),
        ("Domestic financial sectors", "FL794090005.Q", "2009:Q4", "2026:Q1", ("84260.7", "54170.4", "30090.3", "35.7")),
        ("Mutual funds", "LM654090000.Q", "2009:Q4", "2026:Q1", ("15229.4", "68.1", "15161.3", "99.6")),
        ("Exchange-traded funds", "LM564090005.Q", "2009:Q4", "2026:Q1", ("12775.1", "8165.0", "4610.2", "36.1")),
        ("Money market funds", "FL634090005.Q", "2019:Q4", "2026:Q1", ("4287.1", "4287.1", "0.0", "0.0")),
        ("Mortgage REITs", "FL644090075.Q", "2009:Q4", "2026:Q1", ("538.6", "539.8", "-1.2", "-0.2")),
        ("Issuers of ABS", "FL674090005.Q", "2021:Q4", "2026:Q1", ("492.1", "497.5", "-5.4", "-1.1")),
        ("Life insurance companies", "FL544090005.Q", "2009:Q4", "2026:Q1", ("5665.8", "3352.9", "2312.9", "40.8")),
        ("Households corporate equities", "LM153064105.Q", "2009:Q4", "2026:Q1", ("37510.7", "4947.3", "32563.4", "86.8")),
    ]
    for nm, code, a, b, qs in val:
        for k, (lab, unit) in enumerate((("change in level", "$bn"), ("transactions (sum of FU)", "$bn"), ("residual", "$bn"), ("residual share", "%"))):
            R(817, f"{nm} {a}-{b} {lab} {qs[k]}", qs[k], unit, f"{code} change; FU sum", f"{a}->{b}", lambda code=code, a=a, b=b, k=k: decomp(code, a, b)[k],
              "residual = change in level minus the sum of unadjusted transactions (FU, quarters after the start quarter up to and including the end quarter)")
    R(839, "brokers -1.4% since 2021:Q4", "-1.4", "%", "FL664090005.Q; FU664090005.Q", "2021:Q4->2026:Q1", lambda: decomp("FL664090005.Q", "2021:Q4", "2026:Q1")[3])
    R(732, "MMF change 2019:Q4 to 2026:Q1 is $4,287.1bn", "4287.1", "$bn", "FL634090005.Q", "2019:Q4->2026:Q1", lambda: decomp("FL634090005.Q", "2019:Q4", "2026:Q1")[0], "also lines 823, 838")
    R(732, "$3,084.1bn increase in US MMF assets since 2021:Q4", "3084.1", "$bn", "FL634090005.Q", "2021:Q4->2026:Q1", lambda: decomp("FL634090005.Q", "2021:Q4", "2026:Q1")[0],
      "also line 952")
    R(732, "transaction total is identical to the penny, residual 0.0%", "0.0", "%", "FL634090005.Q; FU634090005.Q", "2019:Q4->2026:Q1", lambda: decomp("FL634090005.Q", "2019:Q4", "2026:Q1")[3])
    R(720, "Z.1 money market funds' total financial assets FL634090005 = $8,289.6bn", "8289.6", "$bn level", "FL634090005.Q", "2026:Q1", lambda: B("FL634090005.Q", "2026:Q1"))
    R(720, "≈$5.26trn of par-on-demand claims outside M2", "5.26", "$tn", "FL634090005.Q minus H.6 RMF 3,027.0 (taken from the note)", "2026:Q1",
      lambda: (B("FL634090005.Q", "2026:Q1") - 3027.0) / 1000.0, "mixed: the H.6 retail-MMF input (3,027.0 $bn, 2026-05) is the note's own ALFRED figure, not in the package; only the Z.1 term is rederived")
    R(720, "up from ≈$2.71trn at 2019:Q4", "2.71", "$tn", "FL634090005.Q minus H.6 RMF 1,294.0 (taken from the note)", "2019:Q4",
      lambda: (B("FL634090005.Q", "2019:Q4") - 1294.0) / 1000.0, "mixed: H.6 input 1,294.0 (2019-12, line 865) is the note's own figure; only the Z.1 term is rederived")
    R(720, "(+94% in 6.25 years)", "94", "%", "as the two rows above", "2019:Q4->2026:Q1",
      lambda: 100.0 * (((B("FL634090005.Q", "2026:Q1") - 3027.0) / (B("FL634090005.Q", "2019:Q4") - 1294.0)) - 1), "mixed Z.1 / H.6 as above; the M2 +50.8% half is not Z.1")
    # household net worth (3.2, second table)
    hw = (("2009:Q4", "2019:Q4", ("54173.3", "14370.6", "36118.8", "3683.8", "66.7")),
          ("2019:Q4", "2021:Q4", ("35926.9", "6009.7", "30158.8", "-241.7", "83.9")),
          ("2021:Q4", "2026:Q1", ("31382.0", "9289.1", "22597.9", "-505.0", "72.0")))
    for a, b, qs in hw:
        qq = qrange(a, b)
        fx = (lambda qq=qq: S("FC152090005.Q", qq) / 1000.0, lambda qq=qq: S("FU152090005.Q", qq) / 1000.0, lambda qq=qq: S("FR152090005.Q", qq) / 1000.0,
              lambda qq=qq: S("FV152090005.Q", qq) / 1000.0, lambda qq=qq: 100.0 * S("FR152090005.Q", qq) / S("FC152090005.Q", qq))
        for k, (lab, unit, code) in enumerate((("change in net worth", "$bn", "FC152090005.Q"), ("transactions", "$bn", "FU152090005.Q"), ("revaluation (FR)", "$bn", "FR152090005.Q"),
                                              ("other volume change (FV)", "$bn", "FV152090005.Q"), ("revaluation share", "%", "FR / FC"))):
            R(831, f"Households {a}-{b} {lab} {qs[k]}", qs[k], unit, code + " summed", f"{a}->{b}", fx[k], "sum of the quarterly S1M.r values after the start quarter up to and including the end quarter")
    R(845, "FV +$3,683.8bn over 2009-2019 - 6.8% of the total change", "6.8", "%", "FV152090005.Q / FC152090005.Q", "2009:Q4->2019:Q4",
      lambda: 100.0 * S("FV152090005.Q", qrange("2009:Q4", "2019:Q4")) / S("FC152090005.Q", qrange("2009:Q4", "2019:Q4")))
    R(845, "-$505.0bn since 2021:Q4", "-505.0", "$bn", "FV152090005.Q", "2021:Q4->2026:Q1", lambda: S("FV152090005.Q", qrange("2021:Q4", "2026:Q1")) / 1000.0)

    # ------------------------------------------------------------------ five findings / ZIRP table (Z.1 rows)
    gsr, cpx = "FA106000105.Q", "FA105050005.Q"
    R(674, "NFC gross saving is $3,979bn SAAR at 2026:Q1", "3979", "$bn SAAR", gsr, "2026:Q1", lambda: B(gsr, "2026:Q1"))
    R(674, "against total capex of $3,200bn", "3200", "$bn SAAR", cpx, "2026:Q1", lambda: B(cpx, "2026:Q1"))
    R(674, "a financing gap of -$635bn", "-635", "$bn SAAR", gap, "2026:Q1", lambda: B(gap, "2026:Q1"))
    for nm, code, a, b, ch in (("NFC gross saving", gsr, "2366", "3979", "68"), ("NFC total capex", cpx, "2152", "3200", "49")):
        R(945, f"{nm} 2019:Q4 {a}", a, "$bn SAAR", code, "2019:Q4", lambda code=code: B(code, "2019:Q4"))
        R(945, f"{nm} 2026:Q1 {b}", b, "$bn SAAR", code, "2026:Q1", lambda code=code: B(code, "2026:Q1"))
        R(945, f"{nm} change +{ch}%", ch, "%", code, "2019:Q4-2026:Q1", lambda code=code: 100.0 * (M(code, "2026:Q1") / M(code, "2019:Q4") - 1))
    R(947, "NFC financing gap 2019:Q4 -86", "-86", "$bn SAAR", gap, "2019:Q4", lambda: B(gap, "2019:Q4"))
    R(947, "NFC financing gap 2026:Q1 -635", "-635", "$bn SAAR", gap, "2026:Q1", lambda: B(gap, "2026:Q1"))
    R(948, "NFC net lending 2019:Q4 +261", "261", "$bn SAAR", nl, "2019:Q4", lambda: B(nl, "2019:Q4"))
    R(948, "NFC net lending 2026:Q1 +970", "970", "$bn SAAR", nl, "2026:Q1", lambda: B(nl, "2026:Q1"))
    for p, v in (("2013:Q4", "-21"), ("2019:Q4", "-86"), ("2021:Q4", "94"), ("2023:Q4", "-3"), ("2024:Q4", "6"), ("2025:Q2", "-250"), ("2025:Q4", "-164"), ("2026:Q1", "-635")):
        R(950, f"the financing gap was {v} ({p})", v, "$bn SAAR", gap, p, lambda p=p: B(gap, p))

    # ------------------------------------------------------------------ Handbook lines that quote the note
    H = HAND
    R(83, "FL263069500 $830.8bn (2019:Q4)", "830.8", "$bn level", "FL263069500.Q", "2019:Q4", lambda: B("FL263069500.Q", "2019:Q4"), src=H)
    R(83, "-> $1,192.4bn (2026:Q1)", "1192.4", "$bn level", "FL263069500.Q", "2026:Q1", lambda: B("FL263069500.Q", "2026:Q1"), src=H)
    R(83, "+43.5%", "43.5", "%", "FL263069500.Q", "2019:Q4-2026:Q1", lambda: 100.0 * (M("FL263069500.Q", "2026:Q1") / M("FL263069500.Q", "2019:Q4") - 1), src=H)
    R(83, "FL103193005 NFC unidentified miscellaneous liabilities, $12,101.9bn", "12101.9", "$bn level", "FL103193005.Q", "2026:Q1", lambda: B("FL103193005.Q", "2026:Q1"), src=H)
    R(83, "larger than the entire measured NFC debt stock", "1", "1 = larger", "FL103193005.Q vs LA104104005.Q", "2026:Q1",
      lambda: 1.0 if M("FL103193005.Q", "2026:Q1") > M("LA104104005.Q", "2026:Q1") else 0.0, "12,101.9 vs 14,454 $bn: NOT larger. The note itself (line 797) says '$12.1trn ... larger than the entire $14.45trn', which is false on its own numbers", src=H)
    for q, u, nm in (("84260.7", "$bn", "increase in domestic financial sectors' total financial assets"), ("30090.3", "$bn", "not transactions"), ("35.7", "%", "share not transactions")):
        k = {"84260.7": 0, "30090.3": 2, "35.7": 3}[q]
        R(171, f"{nm} {q}", q, u, "FL794090005.Q; FU794090005.Q", "2009:Q4->2026:Q1", lambda k=k: decomp("FL794090005.Q", "2009:Q4", "2026:Q1")[k], src=H)
    for q, code, nm in (("99.6", "LM654090000.Q", "Mutual funds"), ("86.8", "LM153064105.Q", "Households' equity holdings"), ("0.0", "FL634090005.Q", "MMFs"),
                        ("-0.2", "FL644090075.Q", "mREITs"), ("-1.1", "FL674090005.Q", "ABS issuers")):
        a = "2021:Q4" if code == "FL674090005.Q" else ("2019:Q4" if code == "FL634090005.Q" else "2009:Q4")
        R(171, f"{nm} {q}%", q, "%", code, f"{a}->2026:Q1", lambda code=code, a=a: decomp(code, a, "2026:Q1")[3],
          src=H, note="window as in the note's table (the Handbook does not state one)")
    R(289, "$23,532,650m of assets", "23532650", "$m level", "FL893093005.Q", "2026:Q1", lambda: M("FL893093005.Q", "2026:Q1"), src=H)
    R(289, "$18,636,711m of liabilities", "18636711", "$m level", "FL893193005.Q", "2026:Q1", lambda: M("FL893193005.Q", "2026:Q1"), src=H)
    R(289, "unreconciled by $4.9trn", "4.9", "$tn", "FL893093005.Q - FL893193005.Q", "2026:Q1", lambda: (M("FL893093005.Q", "2026:Q1") - M("FL893193005.Q", "2026:Q1")) / 1e6, src=H,
      note="reading a of 2: assets minus liabilities")
    R(289, "unreconciled by $4.9trn", "4.9", "$tn", "FL903090005.Q", "2026:Q1", lambda: -M("FL903090005.Q", "2026:Q1") / 1e6, src=H, note="reading b of 2: instrument discrepancy, sign reversed")
    R(289, "asset side grew $1.88trn in one year", "1.88", "$tn", "FL893093005.Q", "2025:Q1-2026:Q1", lambda: (M("FL893093005.Q", "2026:Q1") - M("FL893093005.Q", "2025:Q1")) / 1e6, src=H)
    R(289, "NFC alone carries $12.1trn of it on the liability side", "12.1", "$tn", "FL103193005.Q", "2026:Q1", lambda: M("FL103193005.Q", "2026:Q1") / 1e6, src=H)
    R(346, "FL543076035 = $1,125,345m at 2026:Q1", "1125345", "$m level", "FL543076035.Q", "2026:Q1", lambda: M("FL543076035.Q", "2026:Q1"), src=H)
    R(346, "Z.1 flow printed -$23.0bn in 2025", "-23.0", "$bn", "FA543076035.Q", "2025",
      lambda: sum(M("FA543076035.Q", p) for p in QS6[1:5]) / 4000.0, src=H, note="reading a of 2: mean of the four SAAR quarters (= the SAAR annual rate)")
    R(346, "Z.1 flow printed -$23.0bn in 2025", "-23.0", "$bn", "FU543076035.Q", "2025", lambda: sum(M("FU543076035.Q", p) for p in QS6[1:5]) / 1000.0, src=H,
      note="reading b of 2: sum of the four unadjusted quarterly amounts")
    R(345, "successors x4035005 / x4135005 (series code check: FL894135005 present)", "1", "series present", "FL894135005.Q", "n/a", lambda: float("FL894135005.Q" in Z), src=H)

    return rows, rel, ndcount


def prev4(p):
    """The first quarter of the four quarters ending at p, minus one (so qrange(prev4(p), p) is the four quarters ending at p)."""
    return f"{int(p[:4]) - 1}:Q{p[-1]}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["build"])
    ap.add_argument("--date")
    a = ap.parse_args()
    rows, rel, nd = do_build(a.date)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "reconciliation.csv"), "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["source_file", "quote_line", "quoted_text", "quoted_value", "rederived_value", "units", "series_codes", "quarter", "status", "note"])
        w.writerows(rows)
    from collections import Counter
    c = Counter(r[8] for r in rows)
    print(f"{len(rows)} rows (Z.1 release {rel}); " + "; ".join(f"{k}: {c[k]}" for k in sorted(c)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
