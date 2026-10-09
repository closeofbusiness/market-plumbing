#!/usr/bin/env python3
"""Weekly positioning in US Treasury futures by trader class, from the CFTC's free Traders in Financial Futures
(TFF) report, "Futures Only" -- the research programme's missing test of the hedge-fund basis trade. Stdlib only.

  python3 bin/pull_cftc_tff.py             # pull from the CFTC, write every output below, print the checkpoint table
  python3 bin/pull_cftc_tff.py --offline   # rebuild every output from the saved raw snapshot (no network)

SOURCE. CFTC Public Reporting Environment, Socrata API, dataset gpe5-46if "TFF - Futures Only"
(https://publicreporting.cftc.gov/resource/gpe5-46if.json). No key. Anonymous use; the script sends the neutral
User-Agent below and makes one request per contract with a pause between them. If the CFTC throttles or refuses, the
script retries only where the server says to (429/503, honouring Retry-After), then stops; it never works around a block.
The dataset's text fields differ across eras (contract and exchange names change, and cftc_market_code is 'CBT' in
some rows and 'CBT ' in others), so the script selects by cftc_contract_market_code only.

CONTRACTS (CBOT, all in the dataset under these CFTC contract market codes; face per contract is read from the data's
contract_units field and asserted against the table below):
  042601 UST 2Y NOTE   $200,000 face     044601 UST 5Y NOTE     $100,000     043602 UST 10Y NOTE     $100,000
  043607 ULTRA UST 10Y  $100,000          020601 UST BOND        $100,000     020604 ULTRA UST BOND   $100,000

TRADER CLASSES (CFTC definitions): Leveraged Funds = hedge funds and other money managers using leverage; Asset
Managers = pension funds, endowments, insurers, mutual funds; Dealers = sell-side swap dealers and banks. Positions are
reported by reportable traders in futures only; "net" = long - short, excluding each class's SPREAD positions (calendar
spreads are reported in a separate column). A NEGATIVE net is a net SHORT. Week = the dataset's report date: a Tuesday
in 452 of 457 weeks (positions as of Tuesday's close; published the following Friday). Five report dates are the MONDAY
instead -- 2018-12-24, 2018-12-31, 2020-12-21, 2023-07-03 and 2025-11-10 (four of them before a Tuesday holiday; the fifth,
2020-12-21, is not explained by the data). They are kept as the CFTC dates them; the script checks there is exactly one
report in every ISO week, none missing and none doubled.

CONVERSIONS (kept deliberately simple; constants below). Per-contract DV01 in dollars per basis point for the whole
contract, held CONSTANT over the sample:
  * PRIMARY set = the CME Group's worked example of deliverable Treasury futures DV01s labelled January 2024 (CME
    education material on yield futures): 2Y $34, 5Y $42, 10Y $63, Ultra 10Y $91, Bond $137, Ultra Bond $215.
  * ALT set = the figures in CME's "Introduction to Treasuries" course table (undated; larger, probably from a lower-yield
    period): 2Y $36.97, 5Y $47.94, 10Y $76.55, Ultra 10Y $115.84, Bond $213.14, Ultra Bond $289.34. Used only as a
    sensitivity, reported next to the primary set.
  A futures DV01 is the cheapest-to-deliver bond's DV01 divided by its conversion factor, so it moves with yields and
  with which bond is cheapest. A constant is an approximation, best for 2023-26 (10-year yield about 3.9-4.6%) and
  rougher for 2018-22. NOTE: these figures were taken from a search summary of the CME pages; cme.com refused a
  scripted fetch (HTTP 403, IP blocked for scraping) and was not retried, so the primary page has not been read.
  * NOTIONAL ($bn) = net contracts x face per contract. This is the contract's face, not the market value of the
    underlying; 'notional' here follows the contract's own face value.
  * 10-YEAR EQUIVALENT ($bn face of a 10-year par note) = net DV01 / DV01 of $1 of a 10-year par note, with that DV01
    fixed at the modified duration of a 10-year par bond at 4.0% (semiannual closed form, 8.176 years; the form used in
    bin/r2_duration_supply.py, but at a fixed yield rather than each date's yield). The repo's R2 uses each date's
    10-year par yield (8.2 in 2024); in 2018-21, when the 10-year yield was roughly 0.6-3.2%, the date-specific duration
    would have been roughly 8.5-9.6, so this fixed convention overstates 10-year equivalents in those years, by up to
    about 17% at the 2020 low.
  * DV01 ($mn per bp) = net contracts x per-contract DV01 / 1e6. Convention-light: depends only on the DV01 table.

OUTPUTS (data/history/ files are the repo's disposable cache, overwritten each run; two columns, as_of,value):
  data/history/cftc_tff_<contract>_<field>.csv   contract in {ust2y,ust5y,ust10y,ultra10y,ustbond,ultrabond}
      fields (contracts): levfunds_long, levfunds_short, levfunds_net, assetmgr_net, dealer_net, open_interest
      fields (converted, Leveraged Funds net): levfunds_net_notional_bn, levfunds_net_10yeq_bn
  data/history/cftc_tff_all6_<class>_net_{notional_bn,10yeq_bn}.csv   class in {levfunds,assetmgr,dealer}; the sum
      across the six contracts (negative = net short)
  data/history/cftc_tff_all6_levfunds_net_dv01_mn_per_bp.csv
  data/cftc_tff/raw_tff_futonly_treasury.csv     the exact rows pulled (the vintage; --offline rebuilds from it)
  data/cftc_tff/checkpoints.csv                  quarter-end and latest-week table, beside the Form PF series
"""
import os, re, sys, csv, json, ssl, time, argparse, datetime, urllib.request, urllib.parse, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = os.path.join(ROOT, "data", "history")
OUT = os.path.join(ROOT, "data", "cftc_tff")
RAW = os.path.join(OUT, "raw_tff_futonly_treasury.csv")
UA = {"User-Agent": "ThirdDerivativeResearch/1.0", "Accept-Encoding": "identity"}
URL = "https://publicreporting.cftc.gov/resource/gpe5-46if.json"
START = "2018-01-01"

# slug, CFTC contract market code, label, face per contract ($), DV01 primary ($/bp/contract), DV01 alt
CONTRACTS = [
    ("ust2y",     "042601", "UST 2Y NOTE",    200000,  34.0,  36.97),
    ("ust5y",     "044601", "UST 5Y NOTE",    100000,  42.0,  47.94),
    ("ust10y",    "043602", "UST 10Y NOTE",   100000,  63.0,  76.55),
    ("ultra10y",  "043607", "ULTRA UST 10Y",  100000,  91.0, 115.84),
    ("ustbond",   "020601", "UST BOND",       100000, 137.0, 213.14),
    ("ultrabond", "020604", "ULTRA UST BOND", 100000, 215.0, 289.34),
]
REF_YIELD = 4.0
def par_mod_duration(y_pct, n=10):
    y = y_pct / 100.0
    return (1.0 / y) * (1.0 - 1.0 / (1.0 + y / 2.0) ** (2 * n))
REF_DUR = par_mod_duration(REF_YIELD)          # 8.176 years: DV01 per $1 face of a 10-year par note = REF_DUR x 1e-4

CLASSES = [("levfunds", "lev"), ("assetmgr", "am"), ("dealer", "dl")]
# raw column -> API field
FIELDS = [
    ("report_date", "report_date_as_yyyy_mm_dd"), ("code", "cftc_contract_market_code"),
    ("name", "market_and_exchange_names"), ("units", "contract_units"), ("oi", "open_interest_all"),
    ("lev_long", "lev_money_positions_long"), ("lev_short", "lev_money_positions_short"), ("lev_spread", "lev_money_positions_spread"),
    ("am_long", "asset_mgr_positions_long"), ("am_short", "asset_mgr_positions_short"), ("am_spread", "asset_mgr_positions_spread"),
    ("dl_long", "dealer_positions_long_all"), ("dl_short", "dealer_positions_short_all"), ("dl_spread", "dealer_positions_spread_all"),
    ("ot_long", "other_rept_positions_long"), ("ot_short", "other_rept_positions_short"), ("ot_spread", "other_rept_positions_spread"),
    ("totrep_long", "tot_rept_positions_long_all"), ("totrep_short", "tot_rept_positions_short"),
    ("nonrep_long", "nonrept_positions_long_all"), ("nonrep_short", "nonrept_positions_short_all"),
]
INTS = [c for c, _ in FIELDS if c not in ("report_date", "code", "name", "units")]

# Form PF series already in the repo (OFR Hedge Fund Monitor, qualifying hedge funds, quarter-end, $bn)
PF = [("pf_long_treasury_bn", "hf_long_treasury_exposure_bn"), ("pf_short_treasury_bn", "hf_short_treasury_exposure_bn"),
      ("pf_repo_borrowing_bn", "hf_repo_borrowing_bn"), ("pf_reverse_repo_bn", "hf_reverse_repo_exposure_bn")]
QUARTER_ENDS = [("end-2023", "2023-12-31"), ("end-2024", "2024-12-31"), ("end-2025", "2025-12-31"), ("2026-06-30", "2026-06-30")]


def get(params, tries=4):
    u = URL + "?" + urllib.parse.urlencode(params)
    for k in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90, context=ssl.create_default_context())
            return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and k < tries - 1:
                wait = int(e.headers.get("Retry-After") or 0) or 15 * (k + 1)
                print(f"  HTTP {e.code}; the server asked for a pause; waiting {wait}s", file=sys.stderr); time.sleep(wait); continue
            raise SystemExit(f"STOP: CFTC returned HTTP {e.code} for {u}. Not retrying further and not working around it.")
        except urllib.error.URLError as e:
            if k < tries - 1: time.sleep(10 * (k + 1)); continue
            raise SystemExit(f"STOP: network error for {u}: {e}")


def pull():
    rows = []
    select = ",".join(a for _, a in FIELDS)
    for slug, code, label, face, *_ in CONTRACTS:
        d = get({"$select": select, "$where": f"cftc_contract_market_code = '{code}' AND report_date_as_yyyy_mm_dd >= '{START}T00:00:00.000'",
                 "$order": "report_date_as_yyyy_mm_dd", "$limit": "5000"})
        assert len(d) < 5000, "page limit reached; add paging"
        print(f"  {code} {label}: {len(d)} weekly rows")
        for r in d:
            rows.append({c: (r.get(a) or "").strip() for c, a in FIELDS})
        time.sleep(1.0)
    for r in rows: r["report_date"] = r["report_date"][:10]
    os.makedirs(OUT, exist_ok=True)
    with open(RAW, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[c for c, _ in FIELDS]); w.writeheader(); w.writerows(rows)
    return rows


def load_raw():
    with open(RAW, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def validate(rows):
    """Hard checks on the pulled rows; raises on any failure. Returns {slug: {date: row-with-ints}}."""
    by = {s: {} for s, *_ in CONTRACTS}; code2slug = {c: s for s, c, *_ in CONTRACTS}; face = {s: fc for s, _, _, fc, *_ in CONTRACTS}
    for r in rows:
        s = code2slug[r["code"]]
        for c in INTS: r[c] = int(r[c])
        assert r["report_date"] not in by[s], f"duplicate {s} {r['report_date']}"
        by[s][r["report_date"]] = r
    for s, d in by.items():
        ds = sorted(d)
        assert ds and ds[0] >= START, (s, ds[:1])
        wd = {x: datetime.date.fromisoformat(x).weekday() for x in ds}
        assert all(v in (0, 1) for v in wd.values()), f"{s}: a report date is neither a Tuesday nor a Monday"
        mon = lambda x: datetime.date.fromisoformat(x) - datetime.timedelta(days=wd[x])      # Monday of that ISO week
        gaps = [(a, b) for a, b in zip(ds, ds[1:]) if (mon(b) - mon(a)).days != 7]            # one report per ISO week, none missing
        assert not gaps, f"{s}: gaps in the weekly series: {gaps[:5]}"
        for x in ds:
            r = d[x]
            m = re.search(r"\$([\d,]+)", r["units"]); assert m and int(m.group(1).replace(",", "")) == face[s], f"{s} {x}: face {r['units']!r} != {face[s]}"
            # accounting identities of the TFF report (all positions are contracts)
            for side in ("long", "short"):
                tot = sum(r[f"{k}_{side}"] for k in ("lev", "am", "dl", "ot")) + sum(r[f"{k}_spread"] for k in ("lev", "am", "dl", "ot"))
                assert tot == r[f"totrep_{side}"], f"{s} {x}: reportable classes do not sum to total reportable ({side}): {tot} vs {r[f'totrep_{side}']}"
                assert r[f"totrep_{side}"] + r[f"nonrep_{side}"] == r["oi"], f"{s} {x}: reportable + nonreportable != open interest ({side})"
    sets = {s: set(d) for s, d in by.items()}
    assert len({frozenset(v) for v in sets.values()}) == 1, "the six contracts do not share the same report dates"
    return by


def hist(name, pairs, nd=None):
    os.makedirs(HIST, exist_ok=True)
    with open(os.path.join(HIST, f"cftc_tff_{name}.csv"), "w", encoding="utf-8") as f:
        f.write("as_of,value\n")
        for d, v in pairs: f.write(f"{d},{v if nd is None else round(v, nd)}\n")


def build(by):
    dates = sorted(by["ust10y"]); agg = {(c, m): {d: 0.0 for d in dates} for c, _ in CLASSES for m in ("notional", "10yeq")}
    dv01 = {d: 0.0 for d in dates}
    seen = []
    for s, code, label, face, dv, dv_alt in CONTRACTS:
        k10 = dv / (REF_DUR * 1e-4) / 1e9          # $bn of 10y-equivalent face per contract
        for cname, p in CLASSES:
            net = {d: by[s][d][f"{p}_long"] - by[s][d][f"{p}_short"] for d in dates}
            for d in dates:
                agg[(cname, "notional")][d] += net[d] * face / 1e9
                agg[(cname, "10yeq")][d] += net[d] * k10
            if cname == "levfunds":
                for d in dates: dv01[d] += net[d] * dv / 1e6
                hist(f"{s}_levfunds_long", [(d, by[s][d]["lev_long"]) for d in dates])
                hist(f"{s}_levfunds_short", [(d, by[s][d]["lev_short"]) for d in dates])
                hist(f"{s}_levfunds_net", [(d, net[d]) for d in dates])
                hist(f"{s}_levfunds_net_notional_bn", [(d, net[d] * face / 1e9) for d in dates], 4)
                hist(f"{s}_levfunds_net_10yeq_bn", [(d, net[d] * k10) for d in dates], 4)
            else:
                hist(f"{s}_{cname}_net", [(d, net[d]) for d in dates])
        hist(f"{s}_open_interest", [(d, by[s][d]["oi"]) for d in dates])
    for (cname, m), ser in agg.items():
        hist(f"all6_{cname}_net_{'notional_bn' if m == 'notional' else '10yeq_bn'}", [(d, ser[d]) for d in dates], 4)
    hist("all6_levfunds_net_dv01_mn_per_bp", [(d, dv01[d]) for d in dates], 3)
    return dates, agg, dv01


def form_pf():
    out = {}
    for col, key in PF:
        p = os.path.join(HIST, key + ".csv")
        out[col] = {}
        if os.path.exists(p):
            with open(p, newline="", encoding="utf-8") as f:
                for r in csv.DictReader(f): out[col][r["as_of"]] = float(r["value"])
    return out


def checkpoints(by, dates, agg, dv01):
    pf = form_pf(); rows = []
    pts = [(lab, qe, max(d for d in dates if d <= qe)) for lab, qe in QUARTER_ENDS] + [("latest week", "", dates[-1])]
    for lab, qe, d in pts:
        r = {"label": lab, "quarter_end": qe, "report_date": d}
        for s, *_ in CONTRACTS: r[f"levfunds_net_{s}"] = by[s][d]["lev_long"] - by[s][d]["lev_short"]
        r["levfunds_net_contracts_sum"] = sum(r[f"levfunds_net_{s}"] for s, *_ in CONTRACTS)
        r["levfunds_net_notional_bn"] = round(agg[("levfunds", "notional")][d], 1)
        r["levfunds_net_10yeq_bn"] = round(agg[("levfunds", "10yeq")][d], 1)
        r["levfunds_net_10yeq_bn_altdv01"] = round(sum((by[s][d]["lev_long"] - by[s][d]["lev_short"]) * dva / (REF_DUR * 1e-4) / 1e9 for s, _, _, _, _, dva in CONTRACTS), 1)
        r["levfunds_net_dv01_mn_per_bp"] = round(dv01[d], 2)
        r["assetmgr_net_10yeq_bn"] = round(agg[("assetmgr", "10yeq")][d], 1)
        r["dealer_net_10yeq_bn"] = round(agg[("dealer", "10yeq")][d], 1)
        for col, _ in PF: r[col] = pf[col].get(qe, "") if qe else ""
        r["pf_net_treasury_bn"] = round(r["pf_long_treasury_bn"] - r["pf_short_treasury_bn"], 1) if qe and r["pf_long_treasury_bn"] != "" else ""
        rows.append(r)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "checkpoints.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--offline", action="store_true", help="rebuild from the saved raw snapshot; no network")
    a = ap.parse_args()
    print("CFTC TFF futures-only, Treasury futures" + (" (offline, from the saved snapshot)" if a.offline else ""))
    rows = load_raw() if a.offline else pull()
    by = validate(rows)
    dates, agg, dv01 = build(by)
    print(f"validated: 6 contracts x {len(dates)} weekly reports, {dates[0]} to {dates[-1]}; identities hold (classes sum to reportable; reportable + non-reportable = open interest)")
    print(f"10-year-equivalent reference: modified duration of a 10-year par bond at {REF_YIELD}% = {REF_DUR:.3f} years")
    print("conversion table (per contract): face $ | DV01 $/bp primary | alt | implied duration yrs (DV01/face/1e-4) | 10y-eq face $ per contract")
    for s, code, label, face, dv, dva in CONTRACTS:
        print(f"  {s:9s} {code} {label:15s} {face:>8,d} | {dv:7.2f} | {dva:7.2f} | {dv / face * 1e4:5.2f} | {dv / (REF_DUR * 1e-4):>9,.0f}")
    cp = checkpoints(by, dates, agg, dv01)
    print("\nLeveraged Funds, net across the six contracts (negative = net short); latest report date = " + dates[-1])
    hdr = ["label", "report_date", "levfunds_net_contracts_sum", "levfunds_net_notional_bn", "levfunds_net_10yeq_bn", "levfunds_net_10yeq_bn_altdv01",
           "levfunds_net_dv01_mn_per_bp", "pf_long_treasury_bn", "pf_short_treasury_bn", "pf_net_treasury_bn", "pf_repo_borrowing_bn", "pf_reverse_repo_bn"]
    print("\t".join(hdr))
    for r in cp: print("\t".join(str(r[h]) for h in hdr))
    print("\nLeveraged Funds net contracts by contract (negative = net short)")
    cs = [s for s, *_ in CONTRACTS]; print("label\treport_date\t" + "\t".join(cs))
    for r in cp: print(f"{r['label']}\t{r['report_date']}\t" + "\t".join(str(r[f'levfunds_net_{c}']) for c in cs))
    print("\nChanges between checkpoints (to - from); Form PF changes only where both ends are Form PF quarter-ends, $bn")
    ch = ["levfunds_net_contracts_sum", "levfunds_net_notional_bn", "levfunds_net_10yeq_bn", "pf_long_treasury_bn", "pf_short_treasury_bn", "pf_net_treasury_bn", "pf_repo_borrowing_bn", "pf_reverse_repo_bn"]
    print("from -> to\t" + "\t".join(ch))
    for i, j in [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]:
        print(f"{cp[i]['label']} -> {cp[j]['label']}\t" + "\t".join(
            ("" if cp[i][c] == "" or cp[j][c] == "" else str(round(cp[j][c] - cp[i][c], 1))) for c in ch))
    n = len([x for x in os.listdir(HIST) if x.startswith("cftc_tff_")])
    print(f"\nwrote {n} cftc_tff_*.csv files in data/history, {os.path.relpath(RAW, ROOT)}, and {os.path.relpath(os.path.join(OUT, 'checkpoints.csv'), ROOT)}")


if __name__ == "__main__":
    main()
