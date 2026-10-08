#!/usr/bin/env python3
"""Rebuild the weekly primary-dealer Treasury "collateral multiplier" c = SO / (SO - SI).

Recipe: Shadow_Debt_Channel_Map.md, "SERIES 1 - WEEKLY US TREASURY COLLATERAL MULTIPLIER FROM FR 2004C"
(Michl-Park / Infante et al.: R_T = SO - SI, c = SO / R_T).  NY Fed Primary Dealer Statistics API,
markets.newyorkfed.org/api/pd, US Treasuries excluding TIPS, $ millions, weekly (Wednesday).

  SO = PDSORA (securities out via repo), SI = PDSIRRA (securities in via reverse repo).
  2013-04-03 .. 2022-01-04 : the published total  PDSORA-UTSETTOT / PDSIRRA-UTSETTOT  (no venue split exists).
  2022-01-05 ..            : published total where it is numeric; else the sum of the venue x maturity
                             components after linear interpolation of each component's own "*" cells
                             (end-fill with the nearest observation).  Components, per leg:
                               SBN2022 (2022-01-05..2024-07-02): venues CBG CBS CBSP GCF TRI UBG UBS   x {"",TAL30,TAG30} = 21
                               SBN2024 (2024-07-03..)          : venues CBG CBS CBSP GCF TRIG TRISP UBG UBS x 3         = 24
  imputed = 1 for a week if EITHER leg used the component sum instead of the published total.
  Sponsored legs = CBSP + TRISP components (CBSP only before 2024-07-03), imputed-interpolated like the rest,
  taken from the component data on every week from 2022-01-05 (blank before that: no venue split).

Usage:  bin/build_collateral_multiplier.py [--cache DIR] [--no-fetch]
  Fetches go to DIR (default: $TMPDIR/pd_api_cache), one request per second, User-Agent
  "ThirdDerivativeResearch/1.0".  A cached file is reused, so an interrupted run resumes.
  Writes data/history/collateral_multiplier_weekly.csv and prints diagnostics.  Run from the repo root.
"""
import csv, json, os, sys, time, tempfile, urllib.request, urllib.error

BASE = "https://markets.newyorkfed.org/api/pd"
UA = "ThirdDerivativeResearch/1.0"
OUT = "data/history/collateral_multiplier_weekly.csv"
SB22_START, SB24_START = "2022-01-05", "2024-07-03"
MATS = ("", "TAL30", "TAG30")
V22 = ("CBG", "CBS", "CBSP", "GCF", "TRI", "UBG", "UBS")
V24 = ("CBG", "CBS", "CBSP", "GCF", "TRIG", "TRISP", "UBG", "UBS")
SPONSORED = ("CBSP", "TRISP")


def get(path, cache, fetch=True):
    fn = os.path.join(cache, path.replace("/", "_"))
    if not os.path.exists(fn):
        if not fetch:
            raise SystemExit("missing cache file %s (run without --no-fetch)" % fn)
        time.sleep(1.0)
        req = urllib.request.Request(BASE + "/" + path, headers={"User-Agent": UA})
        try:
            data = urllib.request.urlopen(req, timeout=60).read()
        except urllib.error.HTTPError as e:   # a block or rate limit: record and stop, never route around
            raise SystemExit("HTTP %s on %s -- stopping" % (e.code, path))
        open(fn, "wb").write(data)
    return json.load(open(fn))["pd"]["timeseries"]


def parse(rows):
    """{date: float $mn, or None for a suppressed / non-numeric cell}"""
    out = {}
    for r in rows:
        v = r["value"]
        try:
            out[r["asofdate"]] = float(v)
        except (TypeError, ValueError):
            out[r["asofdate"]] = None     # "*" suppressed
    return out


def interp(series, dates):
    """Linear interpolation over the week grid, end-fill with nearest; returns ({d: v}, n_filled)."""
    vals = [series.get(d) for d in dates]
    idx = [i for i, v in enumerate(vals) if v is not None]
    if not idx:
        return None, 0
    out, filled = list(vals), 0
    for i, v in enumerate(vals):
        if v is not None:
            continue
        filled += 1
        lo = max((j for j in idx if j < i), default=None)
        hi = min((j for j in idx if j > i), default=None)
        if lo is None:
            out[i] = vals[hi]
        elif hi is None:
            out[i] = vals[lo]
        else:
            out[i] = vals[lo] + (vals[hi] - vals[lo]) * (i - lo) / (hi - lo)
    return dict(zip(dates, out)), filled


def main():
    cache = os.path.join(tempfile.gettempdir(), "pd_api_cache")
    if "--cache" in sys.argv:
        cache = sys.argv[sys.argv.index("--cache") + 1]
    fetch = "--no-fetch" not in sys.argv
    os.makedirs(cache, exist_ok=True)

    tot = {leg: parse(get("get/%s-UTSETTOT.json" % leg, cache, fetch)) for leg in ("PDSORA", "PDSIRRA")}
    weeks = sorted(d for d in tot["PDSORA"] if d >= "2013-04-03")
    assert weeks == sorted(d for d in tot["PDSIRRA"] if d >= "2013-04-03"), "SO/SI week grids differ"
    # the venue-component grid, one per vintage
    comp = {}   # (leg, sb) -> {venue_mat_key: {date: val}}
    for leg in ("PDSORA", "PDSIRRA"):
        for sb, venues, start, end in (("SBN2022", V22, SB22_START, SB24_START), ("SBN2024", V24, SB24_START, "9999")):
            grid = [d for d in weeks if start <= d < end]
            comp[(leg, sb)] = {}
            for v in venues:
                for m in MATS:
                    key = "%s-%sUTSET%s" % (leg, v, m)
                    s = parse(get("get/%s/timeseries/%s.json" % (sb, key), cache, fetch))
                    s = {d: x for d, x in s.items() if d in grid}
                    miss = [d for d in grid if d not in s]
                    assert not miss, "%s %s lacks %d weeks, e.g. %s" % (sb, key, len(miss), miss[:3])
                    series, filled = interp(s, grid)
                    assert series is not None, "%s %s entirely suppressed" % (sb, key)
                    comp[(leg, sb)][(v, m)] = (series, filled, sum(1 for x in s.values() if x is None))
    sb_of = lambda d: "SBN2024" if d >= SB24_START else "SBN2022"

    rows, stats = [], {"cells_total": 0, "cells_star": 0}
    val_err = {"PDSORA": [], "PDSIRRA": []}
    for d in weeks:
        legs, imp = {}, 0
        sponsored = {}
        for leg in ("PDSORA", "PDSIRRA"):
            published = tot[leg][d]
            if d >= SB22_START:
                cs = comp[(leg, sb_of(d))]
                csum = sum(series[d] for (series, _, _) in cs.values())
                sponsored[leg] = sum(cs[k][0][d] for k in cs if k[0] in SPONSORED)
                if published is not None:
                    val_err[leg].append((d, csum / published - 1))
            if published is not None:
                legs[leg] = published
            else:
                assert d >= SB22_START, "total suppressed before the venue split: %s %s" % (leg, d)
                legs[leg] = csum
                imp = 1
        so, si = legs["PDSORA"] / 1000.0, legs["PDSIRRA"] / 1000.0
        rt = so - si
        rows.append(dict(week=d, SO_bn=round(so, 3), SI_bn=round(si, 3), RT_bn=round(rt, 3),
                         c=round(so / rt, 4),
                         sponsored_out_bn=round(sponsored["PDSORA"] / 1000.0, 3) if sponsored else "",
                         sponsored_in_bn=round(sponsored["PDSIRRA"] / 1000.0, 3) if sponsored else "",
                         imputed=imp))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["week", "SO_bn", "SI_bn", "RT_bn", "c", "sponsored_out_bn", "sponsored_in_bn", "imputed"])
        w.writeheader()
        w.writerows(rows)
    print("wrote %s: %d weekly rows, %s .. %s, imputed weeks %d" % (OUT, len(rows), rows[0]["week"], rows[-1]["week"], sum(r["imputed"] for r in rows)))
    # diagnostics
    for (leg, sb), cs in comp.items():
        n = sum(len(s) for s, _, _ in cs.values())
        star = sum(st for _, _, st in cs.values())
        print("  %-7s %s: %d components, %d cells, %d suppressed (interpolated/filled)" % (leg, sb, len(cs), n, star))
    # Step-5 validation of the imputation: component sum vs the published total, weeks where both exist
    for leg in val_err:
        for label, sel in (("SBN2022", lambda d: d < SB24_START), ("SBN2024 to 2026-08-12", lambda d: SB24_START <= d <= "2026-08-12"),
                           ("SBN2024 to latest", lambda d: d >= SB24_START)):
            v = [(d, x) for d, x in val_err[leg] if sel(d)]
            nweeks = sum(1 for d in weeks if sel(d) and d >= SB22_START)
            if v:
                worst = max(v, key=lambda t: abs(t[1]))
                print("  %s %-22s published total on %d of %d weeks; component sum vs total: mean %+.4f%%, worst %+.3f%% (%s)"
                      % (leg, label, len(v), nweeks, 100 * sum(x for _, x in v) / len(v), 100 * worst[1], worst[0]))

def durable_check():
    """Weeks where the durable history files hold a value: our SO / SI (and sponsored legs) must equal them (to their 0.1bn rounding)."""
    R = {r["week"]: r for r in csv.DictReader(open(OUT))}
    for fn, col in (("pd_ust_repo_out_bn", "SO_bn"), ("pd_ust_reverse_in_bn", "SI_bn"),
                    ("pd_ust_repo_sponsored_bn", "sponsored_out_bn"), ("pd_ust_rev_sponsored_dvp_bn", "sponsored_in_bn")):
        d = {r["as_of"]: float(r["value"]) for r in csv.DictReader(open("data/history/%s.csv" % fn))}
        cmp_ = [w for w in d if w in R and R[w][col] != ""]
        bad = [w for w in cmp_ if abs(round(float(R[w][col]), 1) - d[w]) > 1e-9]
        print("  durable check %-28s vs %-17s compared %d, matched %d" % (fn, col, len(cmp_), len(cmp_) - len(bad)))
        assert not bad, "durable mismatch %s: %s" % (fn, bad[:5])


if __name__ == "__main__":
    main()
    durable_check()
