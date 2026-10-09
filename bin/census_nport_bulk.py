#!/usr/bin/env python3
"""Census of the AI build-out's off-balance-sheet debt in US registered funds, from the SEC's
free bulk N-PORT dataset (https://www.sec.gov/dera/data/form-n-port-data-sets). Stdlib only.

  python3 bin/census_nport_bulk.py ZIP OUT_CSV [--reproduce-d2]
  e.g.  python3 bin/census_nport_bulk.py ~/nport/2026q2_nport.zip data/nport/nport_2026Q2.csv --reproduce-d2

Reads FUND_REPORTED_HOLDING.tsv as a stream (about 5 million rows, ~1GB; no pandas, nothing held
but the matched rows), plus SUBMISSION / REGISTRANT / FUND_REPORTED_INFO. Does NOT fetch anything
and does NOT copy any raw holding row into the repo: outputs are aggregates only.

Writes (all beside OUT_CSV, stem = OUT_CSV without .csv):
  OUT_CSV                    one row per name group: value, filings, registrants, sensitivities
  <stem>_registrants.csv     one row per group x registrant (CIK)
  <stem>_period_coverage.csv one row per group x REPORT_DATE (and ALL_FILINGS = the denominator)
  <stem>_file_stats.csv      key,value: file denominators and provenance (zip sha256)
  <stem>_sweep.csv           '* Compute LLC' issuers by name (parent NOT verified - a lead, not a fact)

THE MATCHING RULES (inferred 9 Oct 2026 from the D2 note's section 9 table; verified against the
2026Q2 file, 5,347,869 holding rows, by --reproduce-d2). They are rules about how the data is
WRITTEN DOWN, so they are listed rather than hidden:

 1. Unit of observation = a holding line (a row of FUND_REPORTED_HOLDING). Matching is on
    ISSUER_NAME (case-insensitive regex), NOT on ISSUER_TITLE, plus ISSUER_CUSIP for Beignet.
    A name that appears only in the title/description (repo collateral, CFD counterparties, ADC/VDC
    tranche-named lines) is not matched. The EXT groups below show what that choice costs.
 2. Listed issuers (CoreWeave, TeraWulf, Hut 8, Cipher Mining) drop equity lines: ASSET_CAT EC and
    EP are excluded and EVERYTHING ELSE is kept ("debt only" in D2 means "not equity"). That keeps
    debt (DBT), loans (LON) and also equity-derivative lines named for the issuer (DE: CFDs/swaps).
    Unlisted issuers (Beignet, Vantage, Aligned) take every asset category.
 3. Value = CURRENCY_VALUE, the line's fair value in US dollars (despite the column name: checked
    against PERCENTAGE x NET_ASSETS, see file_stats). Units: $bn in the group file, $m elsewhere.
    D2 CONVENTION: the headline value counts only lines whose CURRENCY_CODE is USD (the lines
    denominated in other currencies are still counted in 'filings'). This is the only simple rule
    that reproduces D2's Vantage $1.09bn; it understates Vantage because the EUR/GBP/CAD tranches
    are real dollars. value_all_ccy_bn is the unrestricted sum and is the better number.
 4. filings = distinct ACCESSION_NUMBER with >=1 matched line. registrants = distinct CIK.
 5. NO amendment de-duplication in the D2 rule: D2's filing counts (Beignet 324 / 146 registrants,
    CoreWeave 506, ...) only reproduce on the raw file. Two de-duplicated variants are reported
    alongside, never instead: value_amend_dedup (keep the latest filing per fund x REPORT_DATE) and
    value_one_per_series (keep only each fund's latest REPORT_DATE: a stock at one as-of date per
    fund). Fund = SERIES_ID, or the registrant CIK when SERIES_ID is blank. The raw sum counts a
    fund once per filing, so a fund that re-filed old periods in the quarter is counted several
    times: small in the 2026Q2 file (Beignet -0.9%), large in 2026Q3 (-6.0%): compare quarters on
    value_one_per_series, not on the raw column.
 6. REPORT_DATE (SUBMISSION) is the as-of date. A quarterly file mixes as-of dates (Feb/Mar/Apr
    for the Q2 file): see period_coverage. REPORT_ENDING_PERIOD is the fiscal year end, not used.
"""
import argparse, collections, csv, datetime, hashlib, io, os, re, sys, time, zipfile
from decimal import Decimal, ROUND_HALF_UP

HOLDING = "FUND_REPORTED_HOLDING.tsv"
EQUITY_CATS = {"EC", "EP"}
MONTHS = {m: i + 1 for i, m in enumerate("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split())}


def is_debt_cat(c):
    return c in ("DBT", "LON") or c.startswith("ABS")


# kind D2 = the seven rows of D2 section 9; kind EXT = same issuers with the aliases that D2's
# name-only rule misses (chosen from the 2026Q2 file and frozen BEFORE the 2026Q3 run).
GROUPS = [
    dict(id="beignet", kind="D2", label="Beignet Investor LLC 6.581% 2049 (CUSIP 076912AA2)",
         name=r"beignet", cusips={"076912AA2"}, listed=False),
    dict(id="coreweave", kind="D2", label="CoreWeave (bonds, converts, loans)",
         name=r"core\s*weave", listed=True),
    dict(id="vantage", kind="D2", label="Vantage Data Centers (ABS, loans)",
         name=r"vantage data", listed=False),
    dict(id="aligned", kind="D2", label="Aligned Data Centers (loans, ABS)",
         name=r"aligned data", listed=False),
    dict(id="terawulf", kind="D2", label="TeraWulf (debt)",
         name=r"tera\s*wulf", listed=True),
    dict(id="hut8", kind="D2", label="Hut 8 (debt)",
         name=r"\bhut\s*8\b", listed=True),
    dict(id="cipher_mining", kind="D2", label="Cipher Mining (debt)",
         name=r"cipher mining", listed=True),
    dict(id="x_terawulf_wulf", kind="EXT", label="TeraWulf + WULF Compute LLC (name-evident)",
         name=r"tera\s*wulf|\bwulf\b", listed=True),
    dict(id="x_cipher_all", kind="EXT", label="Cipher Mining / Digital / Compute LLC (name-evident)",
         name=r"cipher\s*(mining|digital|compute)", listed=True),
    dict(id="x_vantage_alias", kind="EXT", label="Vantage Data Centers incl. tranche-named lines (ISSUER_TITLE)",
         name=r"vantage data", title=r"vantage data", listed=False),
    dict(id="x_aligned_alias", kind="EXT", label="Aligned Data Centers incl. tranche-named lines (ISSUER_TITLE)",
         name=r"aligned data", title=r"aligned data", listed=False),
]
for g in GROUPS:
    g["name_rx"] = re.compile(g["name"], re.I)
    g["title_rx"] = re.compile(g["title"], re.I) if g.get("title") else None
    g.setdefault("cusips", set())
SWEEP_RX = re.compile(r"\bcompute\s+ll", re.I)
SWEEP_KEY = re.compile(r"^(.*?\bcompute)\b", re.I)
PREFILTER = re.compile("|".join(
    [g["name"] for g in GROUPS] + [g["title"] for g in GROUPS if g.get("title")]
    + [re.escape(c) for g in GROUPS for c in g["cusips"]] + [SWEEP_RX.pattern]), re.I)

# D2 section 9 (2026Q2): (value $bn as printed, filings, registrants or None)
D2_TARGETS = {
    "beignet": (9.81, 324, 146), "coreweave": (2.87, 506, None), "vantage": (1.09, 227, None),
    "aligned": (1.06, 123, None), "terawulf": (0.48, 100, None), "hut8": (0.23, 66, None),
    "cipher_mining": (0.005, 2, None),
}
D2_BEIGNET_REGISTRANTS = [  # as printed in D2, $m
    ("PIMCO Funds", 6232), ("BlackRock Funds V", 718), ("Bridge Builder Trust", 295),
    ("Prudential Investment Portfolios 17", 258), ("PIMCO ETF Trust", 177), ("Advanced Series Trust", 140),
    ("Loomis Sayles Funds II", 138), ("Fidelity Rutland Square II", 116), ("PIMCO VIT", 104),
    ("PIMCO Managed Accounts", 87)]


def pdate(s):
    d, m, y = s.strip().split("-")
    return datetime.date(int(y), MONTHS[m.upper()], int(d))


def read_table(z, name):
    with z.open(name) as raw:
        f = io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="")
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def flt(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


def survivors(sub, info, reg):
    """Two de-duplications of amended / repeated filings. Returns (amend_dedup, one_per_series).
    Fund identity = SERIES_ID; a filing with no SERIES_ID (closed-end funds) is identified by its
    registrant CIK. Why this matters: in the Q3 file a series can appear three times (an NPORT-P/A
    for 31 Dec, another for 31 Mar, and the NPORT-P for 30 Jun), and a raw sum counts it three times."""
    best_a, best_s = {}, {}
    for acc, s in sub.items():
        sid = (info.get(acc) or {}).get("SERIES_ID", "").strip()
        fund = ("S", sid) if sid else ("C", (reg.get(acc) or {}).get("CIK", acc))
        rd, fd = pdate(s["REPORT_DATE"]), pdate(s["FILING_DATE"])
        ka, ks = (fund, rd), fund
        va, vs = (fd, acc), (rd, fd, acc)  # tie-break on accession: arbitrary but deterministic
        if ka not in best_a or va > best_a[ka][0]:
            best_a[ka] = (va, acc)
        if ks not in best_s or vs > best_s[ks][0]:
            best_s[ks] = (vs, acc)
    return {v[1] for v in best_a.values()}, {v[1] for v in best_s.values()}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("zip_path")
    ap.add_argument("out_csv")
    ap.add_argument("--reproduce-d2", action="store_true",
                    help="print the D2 section 9 table next to the rebuilt one (use on the 2026Q2 file)")
    a = ap.parse_args()
    stem = a.out_csv[:-4] if a.out_csv.endswith(".csv") else a.out_csv
    m = re.search(r"(\d{4})q([1-4])", os.path.basename(a.zip_path), re.I)
    tag = f"{m.group(1)}Q{m.group(2)}" if m else os.path.basename(a.zip_path)
    os.makedirs(os.path.dirname(os.path.abspath(a.out_csv)), exist_ok=True)
    t0 = time.time()
    z = zipfile.ZipFile(a.zip_path)

    sub = {r["ACCESSION_NUMBER"]: r for r in read_table(z, "SUBMISSION.tsv")}
    reg = {r["ACCESSION_NUMBER"]: r for r in read_table(z, "REGISTRANT.tsv")}
    info = {r["ACCESSION_NUMBER"]: r for r in read_table(z, "FUND_REPORTED_INFO.tsv")}
    surv_amend, surv_ops = survivors(sub, info, reg)
    cik_names = collections.defaultdict(collections.Counter)
    for acc, r in reg.items():
        cik_names[r["CIK"]][r["REGISTRANT_NAME"].strip()] += 1

    # ---- stream the holdings ------------------------------------------------------------
    recs = []      # (gid, acc, cusip, cat, ccy, value, pct)
    sweep = []     # (key, acc, cat, ccy, value)
    nrows = 0
    with z.open(HOLDING) as raw:
        f = io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="")
        hdr = f.readline().rstrip("\r\n").split("\t")
        ix = {h: i for i, h in enumerate(hdr)}
        iN, iT, iC, iA = ix["ISSUER_NAME"], ix["ISSUER_TITLE"], ix["ISSUER_CUSIP"], ix["ASSET_CAT"]
        iV, iK, iP, iX = ix["CURRENCY_VALUE"], ix["CURRENCY_CODE"], ix["PERCENTAGE"], ix["ACCESSION_NUMBER"]
        for line in f:
            nrows += 1
            if nrows % 1000000 == 0:
                print(f"  {nrows:,} rows, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
            if not PREFILTER.search(line):
                continue
            p = line.rstrip("\r\n").split("\t")
            if len(p) != len(hdr):
                raise SystemExit(f"row {nrows}: {len(p)} columns, header has {len(hdr)}; refusing to guess")
            name, title, cusip, cat = p[iN], p[iT], p[iC], p[iA]
            val, ccy = flt(p[iV]), p[iK]
            for g in GROUPS:
                if g["listed"] and cat in EQUITY_CATS:
                    continue
                if (g["name_rx"].search(name) or (g["title_rx"] and g["title_rx"].search(title))
                        or cusip in g["cusips"]):
                    recs.append((g["id"], p[iX], cusip, cat, ccy, val, p[iP]))
            if cat not in EQUITY_CATS and SWEEP_RX.search(name):
                k = SWEEP_KEY.match(name.upper())
                key = re.sub(r"[^A-Z0-9 ]", "", k.group(1)).strip() if k else name.upper()[:40]
                sweep.append((key, p[iX], cat, ccy, val))
    secs = time.time() - t0

    # ---- aggregate ----------------------------------------------------------------------
    na = {acc: flt(i.get("NET_ASSETS")) for acc, i in info.items()}
    by_g = collections.defaultdict(list)
    for r in recs:
        by_g[r[0]].append(r)
    dev_n = dev_bad = 0
    dev_max = 0.0
    group_rows, reg_rows, per_rows = [], [], []
    summary = {}
    for g in GROUPS:
        rs = by_g.get(g["id"], [])
        accs = {r[1] for r in rs}
        usd = [r for r in rs if r[4] == "USD"]
        strict = [r for r in rs if is_debt_cat(r[3])]
        v_all = sum(r[5] for r in rs)
        v_d2 = sum(r[5] for r in usd)
        v_strict = sum(r[5] for r in strict)
        ser = collections.defaultdict(float)
        for r in rs:
            ser[r[1]] += r[5]
            n = na.get(r[1], 0.0)
            if r[6] not in ("", None) and n:
                dev = abs(flt(r[6]) / 100.0 * n - r[5])
                dev_n += 1
                dev_max = max(dev_max, dev)
                if dev > 5 + 1e-4 * abs(r[5]):
                    dev_bad += 1
        big = max(ser, key=ser.get) if ser else None
        a_rs = [r for r in rs if r[1] in surv_amend]
        o_rs = [r for r in rs if r[1] in surv_ops]
        cus = collections.defaultdict(lambda: [0, 0.0])
        for r in rs:
            cus[r[2]][0] += 1
            cus[r[2]][1] += r[5]
        ccy = collections.defaultdict(float)
        for r in rs:
            ccy[r[4]] += r[5]
        ciks = {reg[x]["CIK"] for x in accs}
        group_rows.append(dict(
            tag=tag, group_id=g["id"], kind=g["kind"], label=g["label"],
            rule=f"ISSUER_NAME~/{g['name']}/" + (f" or ISSUER_TITLE~/{g['title']}/" if g.get("title") else "")
                 + (f" or CUSIP in {sorted(g['cusips'])}" if g["cusips"] else "")
                 + ("; excl ASSET_CAT EC,EP" if g["listed"] else "; all ASSET_CAT"),
            rows=len(rs), filings=len(accs), registrants=len(ciks),
            value_d2conv_bn=round(v_d2 / 1e9, 6), value_all_ccy_bn=round(v_all / 1e9, 6),
            value_strict_debt_bn=round(v_strict / 1e9, 6), filings_strict_debt=len({r[1] for r in strict}),
            filings_usd_lines=len({r[1] for r in usd}), value_nonusd_m=round((v_all - v_d2) / 1e6, 3),
            largest_series=(info[big]["SERIES_NAME"].strip() + " / " + reg[big]["REGISTRANT_NAME"].strip()) if big else "",
            largest_series_value_m=round(ser[big] / 1e6, 3) if big else 0,
            largest_series_pct_nav=round(100 * ser[big] / na[big], 3) if big and na.get(big) else "",
            value_amend_dedup_bn=round(sum(r[5] for r in a_rs) / 1e9, 6), filings_amend_dedup=len({r[1] for r in a_rs}),
            value_one_per_series_bn=round(sum(r[5] for r in o_rs) / 1e9, 6), filings_one_per_series=len({r[1] for r in o_rs}),
            distinct_cusips=len(cus),
            cusip_breakdown="; ".join(f"{c}:{v[1] / 1e6:.1f}m/{v[0]}" for c, v in sorted(cus.items(), key=lambda kv: -kv[1][1])[:6]),
            ccy_breakdown="; ".join(f"{c}:{v / 1e6:.1f}m" for c, v in sorted(ccy.items(), key=lambda kv: -kv[1])),
        ))
        # per registrant
        rr = collections.defaultdict(lambda: [set(), 0, 0.0, 0.0, 0.0])
        for r in rs:
            e = rr[reg[r[1]]["CIK"]]
            e[0].add(r[1]); e[1] += 1; e[3] += r[5]
            if r[4] == "USD":
                e[2] += r[5]
            if r[1] in surv_ops:
                e[4] += r[5]
        for cik, e in sorted(rr.items(), key=lambda kv: -kv[1][2]):
            reg_rows.append(dict(tag=tag, group_id=g["id"], cik=cik,
                                 registrant_name=cik_names[cik].most_common(1)[0][0], filings=len(e[0]),
                                 rows=e[1], value_d2conv_m=round(e[2] / 1e6, 3), value_all_ccy_m=round(e[3] / 1e6, 3),
                                 value_one_per_series_m=round(e[4] / 1e6, 3)))
        # per report date
        pd_ = collections.defaultdict(lambda: [set(), 0.0])
        for r in rs:
            e = pd_[sub[r[1]]["REPORT_DATE"]]
            e[0].add(r[1]); e[1] += r[5]
        for d, e in sorted(pd_.items(), key=lambda kv: pdate(kv[0])):
            per_rows.append(dict(tag=tag, scope=g["id"], report_date=pdate(d).isoformat(),
                                 filings=len(e[0]), value_all_ccy_m=round(e[1] / 1e6, 3)))
        summary[g["id"]] = dict(v_d2=v_d2, v_all=v_all, filings=len(accs), regs=len(ciks))
    all_dates = collections.Counter(pdate(s["REPORT_DATE"]) for s in sub.values())
    for d, n in sorted(all_dates.items()):
        per_rows.append(dict(tag=tag, scope="ALL_FILINGS", report_date=d.isoformat(), filings=n, value_all_ccy_m=""))

    sw = collections.defaultdict(lambda: [set(), 0.0, collections.Counter()])
    for key, acc, cat, ccy, val in sweep:
        e = sw[key]; e[0].add(acc); e[1] += val; e[2][cat] += 1
    sweep_rows = [dict(tag=tag, issuer_key=k, filings=len(e[0]), value_all_ccy_m=round(e[1] / 1e6, 3),
                       asset_cats="; ".join(f"{c}:{n}" for c, n in e[2].most_common()),
                       status="parent NOT verified from this file")
                  for k, e in sorted(sw.items(), key=lambda kv: -kv[1][1])]

    sha = hashlib.sha256()
    with open(a.zip_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            sha.update(chunk)
    fds = [pdate(s["FILING_DATE"]) for s in sub.values()]
    top_dates = all_dates.most_common(3)
    stats = [
        ("tag", tag), ("zip", os.path.basename(a.zip_path)), ("zip_sha256", sha.hexdigest()),
        ("holding_rows", nrows), ("holding_rows_matched_any_group", len(recs)),
        ("filings_total", len(sub)),
        ("filings_NPORT-P", sum(1 for s in sub.values() if s["SUB_TYPE"] == "NPORT-P")),
        ("filings_NPORT-P/A", sum(1 for s in sub.values() if s["SUB_TYPE"] == "NPORT-P/A")),
        ("registrants_distinct_cik", len({r["CIK"] for r in reg.values()})),
        ("series_distinct", len({i["SERIES_ID"] for i in info.values() if i["SERIES_ID"].strip()})),
        ("filings_without_series_id", sum(1 for i in info.values() if not i["SERIES_ID"].strip())),
        ("filing_date_min", min(fds).isoformat()), ("filing_date_max", max(fds).isoformat()),
        ("report_date_min", min(all_dates).isoformat()), ("report_date_max", max(all_dates).isoformat()),
        ("report_date_top3", "; ".join(f"{d.isoformat()}:{n}" for d, n in top_dates)),
        ("share_filings_in_top3_report_dates", round(sum(n for _, n in top_dates) / len(sub), 4)),
        ("net_assets_sum_all_filings_bn", round(sum(na.values()) / 1e9, 1)),
        ("net_assets_note", "sum over filings, not de-duplicated, as-of dates differ: a scale, not a stock"),
        ("filings_surviving_amend_dedup", len(surv_amend)), ("filings_surviving_one_per_series", len(surv_ops)),
        ("value_check_lines", dev_n), ("value_check_max_abs_dev_usd", round(dev_max, 2)),
        ("value_check_lines_off_by_over_5usd_plus_0.01pct", dev_bad),
        ("value_check_meaning", "CURRENCY_VALUE vs PERCENTAGE/100*NET_ASSETS on matched lines; ~0 means CURRENCY_VALUE is USD fair value"),
        ("stream_seconds", round(secs, 1)),
    ]

    def dump(path, rows, cols=None):
        cols = cols or list(rows[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
            w.writeheader(); w.writerows(rows)
    dump(a.out_csv, group_rows)
    dump(stem + "_registrants.csv", reg_rows)
    dump(stem + "_period_coverage.csv", per_rows)
    dump(stem + "_sweep.csv", sweep_rows, ["tag", "issuer_key", "filings", "value_all_ccy_m", "asset_cats", "status"])
    with open(stem + "_file_stats.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n"); w.writerow(["key", "value"]); w.writerows(stats)

    # ---- console summary ----------------------------------------------------------------
    print(f"\n{tag}: {nrows:,} holding rows, {len(sub):,} filings, streamed in {secs:.0f}s")
    print("report dates (top 3): " + "; ".join(f"{d.isoformat()} x{n}" for d, n in top_dates))
    print(f"{'group':58s} {'D2conv $bn':>10s} {'all-ccy $bn':>11s} {'strict $bn':>10s} {'filings':>7s} {'regs':>5s}")
    for r in group_rows:
        print(f"{r['label'][:58]:58s} {r['value_d2conv_bn']:10.4f} {r['value_all_ccy_bn']:11.4f} "
              f"{r['value_strict_debt_bn']:10.4f} {r['filings']:7d} {r['registrants']:5d}  [{r['kind']}]")
    if a.reproduce_d2:
        print("\nD2 section 9 vs rebuilt (value = D2-convention column, USD-denominated lines):")
        print(f"{'row':58s} {'D2':>16s} {'rebuilt':>18s}  verdict")
        for g in GROUPS:
            if g["id"] not in D2_TARGETS:
                continue
            tv, tf, tr = D2_TARGETS[g["id"]]
            dp = max(0, len(str(tv).split(".")[1])) if "." in str(tv) else 0
            s = summary[g["id"]]
            v = s["v_d2"] / 1e9
            vq = Decimal(repr(round(v, 9))).quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_UP)
            ok_v, ok_f = float(vq) == tv, s["filings"] == tf
            ok_r = tr is None or s["regs"] == tr
            tx = f"{tv}bn/{tf}" + (f"/{tr}" if tr else "")
            rb = f"{v:.4f}bn/{s['filings']}" + (f"/{s['regs']}" if tr else "")
            print(f"{g['label'][:58]:58s} {tx:>16s} {rb:>18s}  {'MATCH' if ok_v and ok_f and ok_r else 'DIFFERS'}"
                  + ("" if ok_v else " (value)") + ("" if ok_f else " (filings)") + ("" if ok_r else " (registrants)"))
        top = [r for r in reg_rows if r["group_id"] == "beignet"][:10]
        print("\nBeignet by registrant, $m (D2 | rebuilt):")
        for (dn, dv), r in zip(D2_BEIGNET_REGISTRANTS, top):
            vv = Decimal(repr(r["value_d2conv_m"])).quantize(Decimal(1), rounding=ROUND_HALF_UP)
            print(f"  {dn:38s} {dv:6d} | {r['registrant_name'][:40]:40s} {r['value_d2conv_m']:10.1f}  "
                  f"{'MATCH' if int(vv) == dv else 'DIFFERS'}")


if __name__ == "__main__":
    main()
