#!/usr/bin/env python3
"""AF1: did industries that use more AI see more new business applications? Registered statements AF1-P1, P2, P1w, P2w, P3 (version 2 of the spec). Python 3 standard library plus openpyxl and xlrd (read by the CV1-P6 code this script imports).

  python3 bin/af1_ai_formation.py selftest                 # synthetic data only; no network
  python3 bin/af1_ai_formation.py fetch                    # the three Census BFS files (GET only, at most 10 requests to census.gov in all, 3 s apart)
  python3 bin/af1_ai_formation.py build [--out DIR]        # offline; writes registered.csv FIRST, then computes every statistic

Specification: _research/2026-11-15-AF1-AI-Company-Formation-Spec.md ("Version 2" governs; its sha256 is pinned in SPEC_SHA256 below and the build refuses to score if the file differs).
Outputs: data/af1_ai_formation/ (registered.csv, scores.csv, detail.csv, vintages.csv, README.md). Raw downloads: data/vintages/af1/ (gitignored, never committed).
The BTOS sector AI-use means come from bin/cv1_confidence_velocity.py (CV1-P6 code path, imported, not copied).

WHAT TOUCHES THE NETWORK. Only `fetch`. www.census.gov only; User-Agent is the one neutral string CLAUDE.md fixes (no person, address or contact). A 403 or 429 writes STOP_www_census_gov
in the cache and no further request is made (a person deletes the file); the script then stops and prints the URL. Nothing is retried except once after a timeout or a 5xx.
"""
import argparse
import csv
import itertools
import math
import os
import random
import re
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv1_confidence_velocity as cv1                          # noqa: E402  (the CV1-P6 BTOS code path, imported)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_FILE = "_research/2026-11-15-AF1-AI-Company-Formation-Spec.md"
SPEC_SHA256 = "5f4a4dd08c08015ebb83e0c76bca531f18f3a6dfaddf5eb36be83e2730f75969"
OUT_REL = "data/af1_ai_formation"
CACHE_REL = "data/vintages/af1"
Refused = cv1.Refused
Stop = cv1.Stop
sha256_of = cv1.sha256_of
now_utc = cv1.now_utc
write_text = cv1.write_text
write_bytes = cv1.write_bytes
csv_line = cv1.csv_line
spearman = cv1.spearman
UA = cv1.UA

BFS_URL = "https://www.census.gov/econ/bfs/csv/bfs_monthly.csv"
PAGE_URL = "https://www.census.gov/econ/bfs/current/index.html"
DICT_URL = "https://www.census.gov/econ/bfs/pdf/bfs_monthly_data_dictionary.pdf"
FILES = (("bfs-monthly-csv", BFS_URL, "raw/bfs_monthly.csv"), ("bfs-current-release-page", PAGE_URL, "raw/bfs_current_page.html"),
         ("bfs-monthly-data-dictionary", DICT_URL, "raw/bfs_monthly_data_dictionary.pdf"))
BFS_REL = "raw/bfs_monthly.csv"
BFS_SHA256 = "47975a1c7bca0aad7e8206bc40cbf4545c84b4cf5cc44aa9aeb8380b1b57b0cf"       # the 12 Nov 2026 release, as fetched on 15 Nov 2026
PAGE_REL = "raw/bfs_current_page.html"
MAX_CENSUS_REQUESTS = 10                                                           # in all, across every run of fetch (counter file in the cache)
GAP_SECONDS = 3.0
COUNT_FILE = "census_request_count.txt"

PERM_SEED = 20261115                                                               # fixed; recorded in every output
N_PERM = 10000
ALPHA = 0.05
N_CYCLES = 46                                                                      # the spec: published in all 46 cycles of 2024-2025
DROP_52 = "52"
YEARS = (2017, 2018, 2019, 2023, 2024, 2025)
MONTHS = 11                                                                        # January to November

# BFS publishes NAICS 31-33, 44-45 and 48-49 as three pre-grouped codes; every other sector as NAICSdd.
BFS_GROUPS = {"NAICSMNF": ("31", "32", "33"), "NAICSRET": ("44", "45"), "NAICSTW": ("48", "49")}
TOTAL_CODE, NONAICS_CODE = "TOTAL", "NONAICS"
SERIES = {"BA": "BA_BA", "WBA": "BA_WBA"}

REG_HEADER = ("statement_id", "version", "superseded", "scored", "statement", "statistic", "support_if", "against_if", "treatment_window", "placebo_window", "prereg_sha256")
SCORES_HEADER = ("statement_id", "label", "primary_statistic", "primary_value", "unit", "statistics", "denominators", "caveats")
DETAIL_HEADER = ("statement_id", "item", "value", "unit")
VINTAGES_HEADER = ("source", "key", "url", "fetched_utc", "status", "bytes", "sha256", "note")
LABELS = ("SUPPORT", "AGAINST", "INCONCLUSIVE")
COMMITTED = ("README.md", "registered.csv", "scores.csv", "detail.csv", "vintages.csv")
IDS = ("AF1-P1", "AF1-P2", "AF1-P1w", "AF1-P2w", "AF1-P3")


def cache_dir(root=None):
    return os.path.join(root or ROOT, *CACHE_REL.split("/"))


def out_dir(root=None):
    return os.path.join(root or ROOT, *OUT_REL.split("/"))


# ------------------------------------------------------------------------------------------------------------------------
# fetch
# ------------------------------------------------------------------------------------------------------------------------
def read_count(cache):
    try:
        return int(open(os.path.join(cache, COUNT_FILE)).read().strip())
    except (OSError, ValueError):
        return 0


def write_count(cache, n):
    write_text(os.path.join(cache, COUNT_FILE), "%d\n" % n)


def hdr(h, name):
    for k, v in (h or {}).items():
        if k.lower() == name.lower():
            return v
    return ""


def read_manifest(cache):
    p = os.path.join(cache, "manifest.csv")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def cmd_fetch(root=None, fetcher=None, sleep=time.sleep):
    cache = cache_dir(root)
    os.makedirs(cache, exist_ok=True)
    f = fetcher or cv1.Fetcher(cache)
    todo = [x for x in FILES if not os.path.exists(os.path.join(cache, *x[2].split("/")))]
    used = read_count(cache)
    if used + len(todo) > MAX_CENSUS_REQUESTS:
        raise Refused("this fetch would take the census.gov request count from %d to %d, over the cap of %d" % (used, used + len(todo), MAX_CENSUS_REQUESTS))
    first = True
    for key, url, rel in todo:
        if not first:
            sleep(GAP_SECONDS)
        first = False
        try:
            status, body, h = f.get(url)
        finally:
            used += 1
            write_count(cache, used)                                           # a request is counted even if it fails
        if status != 200:
            print("%s: HTTP %s (not stored)" % (url, status))
            continue
        write_bytes(os.path.join(cache, *rel.split("/")), body)
        mp = os.path.join(cache, "manifest.csv")
        new = not os.path.exists(mp)
        with open(mp, "a", encoding="utf-8", newline="") as fh:
            if new:
                fh.write("key,url,fetched_utc,status,bytes,sha256,last_modified\n")
            fh.write(csv_line([key, url, now_utc(), status, len(body), sha256_of(body), hdr(h, "last-modified")]))
        print("%s: fetched %d bytes sha256 %s" % (key, len(body), sha256_of(body)))
        if key == "bfs-monthly-csv" and sha256_of(body) != BFS_SHA256:
            print("WARNING: bfs_monthly.csv hashes to %s, not the pinned %s (a newer vintage?): build will refuse until the pin and the README vintage are reviewed" % (sha256_of(body), BFS_SHA256))
    if not todo:
        print("all three files already in the cache; no request made")
    print("census.gov requests so far (all runs): %d of %d" % (used, MAX_CENSUS_REQUESTS))
    return 0


# ------------------------------------------------------------------------------------------------------------------------
# BFS, sector grouping, matched-month means
# ------------------------------------------------------------------------------------------------------------------------
def btos_sector_of_bfs_code(code):
    """BFS sector code -> BTOS sector key ('23', '31', '44', '48', ...); TOTAL, NONAICS and anything else -> None. Works on BFS's pre-grouped codes and on single-sector codes (NAICS31 .. NAICS33 all give '31')."""
    if code in BFS_GROUPS:
        return cv1.NAICS2_TO_BTOS.get(BFS_GROUPS[code][0], BFS_GROUPS[code][0])
    m = re.match(r"^NAICS(\d\d)$", code or "")
    if m:
        return cv1.NAICS2_TO_BTOS.get(m.group(1), m.group(1))
    return None


def parse_months(cells):
    out = []
    for c in cells:
        c = (c or "").strip()
        out.append(float(c) if c != "" else None)
    return out


def load_bfs(path):
    """{(series, code): {year: [12 monthly values or None]}} for the NOT seasonally adjusted ('U') United States rows of BA_BA and BA_WBA. Raises Refused if a needed series has no NSA TOTAL row."""
    table = {}
    mon = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["geo"] != "US" or r["sa"] != "U" or r["series"] not in SERIES.values():
                continue
            table.setdefault((r["series"], r["naics_sector"]), {})[int(r["year"])] = parse_months([r[m] for m in mon])
    for s in SERIES.values():
        if (s, TOTAL_CODE) not in table:
            raise Refused("BFS file has no not-seasonally-adjusted US %s TOTAL row" % s)
    return table


def jn_mean(months):
    """Mean monthly value over January to November (11 months). A missing month in that span is an error, never a shorter mean."""
    m = months[:MONTHS]
    if len(m) != MONTHS or any(v is None for v in m):
        raise ValueError("a January-November window needs all 11 months")
    return sum(m) / float(MONTHS)


def group_sectors(table, series):
    """{BTOS sector: {year: [12 months summed over the BFS codes that map to it]}}. BFS already publishes the 31-33, 44-45 and 48-49 groups; separate codes would be summed here."""
    out = {}
    for (s, code), by_year in table.items():
        if s != series:
            continue
        sec = btos_sector_of_bfs_code(code)
        if sec is None:
            continue
        tgt = out.setdefault(sec, {})
        for y, mons in by_year.items():
            if y not in tgt:
                tgt[y] = list(mons)
            else:
                tgt[y] = [None if (a is None or b is None) else a + b for a, b in zip(tgt[y], mons)]
    return out


# ------------------------------------------------------------------------------------------------------------------------
# the registered test
# ------------------------------------------------------------------------------------------------------------------------
def perm_test(ai, y, seed=PERM_SEED, nperm=N_PERM):
    """Spearman of ai against y; one-sided permutation p-values over `nperm` random permutations of the AI values (y held fixed), p = (1 + #{perm as extreme}) / (nperm + 1), and leave-one-out.
    Returns dict rho, p_pos, p_neg, loo [(index, rho or None)], loo_min, loo_max, n."""
    obs = spearman(ai, y)
    if obs is None:
        raise ValueError("Spearman undefined (no variation or fewer than 3 sectors)")
    rng = random.Random(seed)
    xs = list(ai)
    ge = le = 0
    for _ in range(nperm):
        rng.shuffle(xs)
        r = spearman(xs, y)
        if r is None:
            continue
        if round(r - obs, 9) >= 0:
            ge += 1
        if round(r - obs, 9) <= 0:
            le += 1
    loo = []
    for i in range(len(ai)):
        loo.append((i, spearman(list(ai[:i]) + list(ai[i + 1:]), list(y[:i]) + list(y[i + 1:]))))
    vals = [v for _i, v in loo if v is not None]
    return {"rho": obs, "p_pos": (1.0 + ge) / (nperm + 1.0), "p_neg": (1.0 + le) / (nperm + 1.0), "loo": loo, "n": len(ai),
            "loo_min": min(vals) if vals else None, "loo_max": max(vals) if vals else None, "loo_undefined": len(loo) - len(vals), "nperm": nperm, "seed": seed}


def label_perm(res, alpha=ALPHA):
    """SUPPORT: one-sided p for a positive rho <= alpha AND every leave-one-out rho > 0. AGAINST: one-sided p for a negative rho <= alpha. Otherwise INCONCLUSIVE."""
    loo_all_pos = res["loo_undefined"] == 0 and res["loo_min"] is not None and round(res["loo_min"], 9) > 0
    if round(res["p_pos"], 9) <= alpha and loo_all_pos:
        return "SUPPORT"
    if round(res["p_neg"], 9) <= alpha:
        return "AGAINST"
    return "INCONCLUSIVE"


def label_p3(mean_prev, mean_now):
    return "SUPPORT" if mean_now > mean_prev else "AGAINST"


def weighted_pearson(x, y, w):
    tot = float(sum(w))
    if not tot > 0:
        raise ValueError("weights must sum to a positive number")
    mx = sum(a * c for a, c in zip(x, w)) / tot
    my = sum(b * c for b, c in zip(y, w)) / tot
    sxy = sum(c * (a - mx) * (b - my) for a, b, c in zip(x, y, w))
    sxx = sum(c * (a - mx) ** 2 for a, c in zip(x, w))
    syy = sum(c * (b - my) ** 2 for b, c in zip(y, w))
    if sxx == 0 or syy == 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def select_sectors(ai, ncycles, bfs_sectors):
    """ai: cv1.btos_ai_means output. Kept: AI share published (not suppressed) in all `ncycles` cycles, sector in BFS, not 52. Returns (kept sorted, dropped [(sector, reason)])."""
    kept, dropped = [], []
    for s in sorted(ai, key=int):
        used = len(ai[s]["used"])
        if s == DROP_52:
            dropped.append((s, "BTOS excludes NAICS 525 but BFS includes it (spec ruling 7)"))
        elif used < ncycles:
            dropped.append((s, "AI share published in %d of %d cycles (suppressed in %d)" % (used, ncycles, ncycles - used)))
        elif s not in bfs_sectors:
            dropped.append((s, "not a sector in BFS"))
        else:
            kept.append(s)
    return kept, dropped


def compute(table, ai, ncycles, seed=PERM_SEED, nperm=N_PERM):
    """Everything the build reports, from the BFS table and the BTOS means. Pure: no files, no network."""
    series_groups = {name: group_sectors(table, s) for name, s in SERIES.items()}
    kept, dropped = select_sectors(ai, ncycles, set(series_groups["BA"]) & set(series_groups["WBA"]))
    if len(kept) < 4:
        raise Refused("fewer than 4 sectors kept")
    x = [ai[s]["mean"] for s in kept]
    R = {"kept": kept, "dropped": dropped, "ai": {s: ai[s]["mean"] for s in kept}, "ncycles": ncycles, "seed": seed, "nperm": nperm, "series": {}}
    for name, groups in series_groups.items():
        m = {s: {y: jn_mean(groups[s][y]) for y in YEARS} for s in kept}
        for s in kept:
            for y in YEARS:
                if not m[s][y] > 0:
                    raise Refused("%s sector %s has a non-positive mean in %d" % (name, s, y))
        lg = {}
        for s in kept:
            a = m[s]
            lg[s] = {"g_post": math.log(a[2025]) - math.log(a[2023]), "g_pre": math.log(a[2019]) - math.log(a[2017]),
                     "g_post_2425": math.log(a[2025]) - math.log(a[2024]), "g_pre_1819": math.log(a[2019]) - math.log(a[2018])}
            lg[s]["diff"] = lg[s]["g_post"] - lg[s]["g_pre"]
            lg[s]["diff_2425"] = lg[s]["g_post_2425"] - lg[s]["g_pre_1819"]
            lg[s]["diff_2425_regpre"] = lg[s]["g_post_2425"] - lg[s]["g_pre"]
        R["series"][name] = {"means": m, "g": lg}
    T = {}

    def run(key, name, sectors, field):
        sg = R["series"][name]["g"]
        res = perm_test([R["ai"][s] for s in sectors], [sg[s][field] for s in sectors], seed, nperm)
        res["sectors"] = list(sectors)
        T[key] = res
    sub = [s for s in kept if s not in ("51", "54")]
    for key, name, field in (("P1", "BA", "g_post"), ("P2", "BA", "diff"), ("P1w", "WBA", "g_post"), ("P2w", "WBA", "diff")):
        run(key, name, kept, field)
        T[key]["label"] = label_perm(T[key])
    for sfx, name in (("", "BA"), ("w", "WBA")):
        run("P1%s_no5154" % sfx, name, sub, "g_post")
        run("P2%s_no5154" % sfx, name, sub, "diff")
        run("P1%s_2425" % sfx, name, kept, "g_post_2425")
        run("P2%s_2425" % sfx, name, kept, "diff_2425")
        run("P2%s_2425_regpre" % sfx, name, kept, "diff_2425_regpre")
    for k in T:
        if "label" not in T[k]:
            T[k]["label_if_it_were_primary"] = label_perm(T[k])
    R["tests"] = T
    # weighted Pearson (reported, not labelled): weights = each kept sector's mean monthly NSA BA in Jan-Nov 2019
    w = [R["series"]["BA"]["means"][s][2019] for s in kept]
    R["weighted"] = {"weights_total": sum(w), "P1": weighted_pearson(x, [R["series"]["BA"]["g"][s]["g_post"] for s in kept], w),
                     "P2": weighted_pearson(x, [R["series"]["BA"]["g"][s]["diff"] for s in kept], w)}
    # national (TOTAL) and no-NAICS share
    nat = {}
    for name, s in SERIES.items():
        tot = {y: jn_mean(table[(s, TOTAL_CODE)][y]) for y in YEARS}
        non = {y: jn_mean(table[(s, NONAICS_CODE)][y]) for y in YEARS} if (s, NONAICS_CODE) in table else None
        keptsum = {y: sum(R["series"][name]["means"][k][y] for k in kept) for y in YEARS}
        nat[name] = {"total": tot, "nonaics": non, "kept_sum": keptsum}
    R["national"] = nat
    R["p3"] = {"mean_2024": nat["BA"]["total"][2024], "mean_2025": nat["BA"]["total"][2025]}
    R["p3"]["label"] = label_p3(R["p3"]["mean_2024"], R["p3"]["mean_2025"])
    R["p3"]["pct"] = (R["p3"]["mean_2025"] / R["p3"]["mean_2024"] - 1.0) * 100.0
    return R


# ------------------------------------------------------------------------------------------------------------------------
# registered.csv (written before any statistic)
# ------------------------------------------------------------------------------------------------------------------------
def spec_text(root=None):
    with open(os.path.join(root or ROOT, *SPEC_FILE.split("/")), "rb") as fh:
        return fh.read()


def check_spec_hash(root=None, pinned=None):
    got = sha256_of(spec_text(root))
    if got != (pinned or SPEC_SHA256):
        raise Refused("the spec file hashes to %s, not the pinned %s: the build refuses to score" % (got, pinned or SPEC_SHA256))
    return got


def parse_spec_v2(text):
    """The version 2 statements table (after the marker 'Statements (version 2)'): id -> (statement, statistic, support_if, against_if), markdown emphasis removed. The combined row
    'AF1-P1w, P2w' is expanded into AF1-P1w and AF1-P2w (the same statements on WBA)."""
    marker = text.find("**Statements (version 2).**")
    if marker < 0:
        raise Refused("the spec has no 'Statements (version 2)' section")
    rows = {}
    for line in text[marker:].splitlines():
        m = re.match(r"^\|\s*(AF1-P[0-9][^|]*)\|(.*)\|\s*$", line)
        if not m:
            continue
        cells = [c.strip().replace("**", "") for c in m.group(2).split("|")]
        if len(cells) != 4:
            raise Refused("version 2 table row %s does not have four cells" % m.group(1).strip())
        rows[m.group(1).strip()] = tuple(cells)
    need = ["AF1-P1", "AF1-P2", "AF1-P1w, P2w", "AF1-P3"]
    if sorted(rows) != sorted(need):
        raise Refused("the version 2 table does not hold %s: %s" % (need, sorted(rows)))
    p1 = rows["AF1-P1"]
    out = {"AF1-P1": p1, "AF1-P3": rows["AF1-P3"]}
    st, _stat, sup, ag = rows["AF1-P1w, P2w"]
    # 'same rule' in the spec means AF1-P1's rule; it is written out so each registered row stands alone
    out["AF1-P2"] = (rows["AF1-P2"][0], rows["AF1-P2"][1], "%s (AF1-P1's rule: %s)" % (rows["AF1-P2"][2], p1[2]), "%s (AF1-P1's rule: %s)" % (rows["AF1-P2"][3], p1[3]))
    for src, dst in (("AF1-P1", "AF1-P1w"), ("AF1-P2", "AF1-P2w")):
        s0 = rows[src]
        out[dst] = ("%s (%s) on WBA, applications with planned wages. %s" % (src, s0[0], st), s0[1].replace("(BA)", "(WBA)"),
                    "%s (AF1-P1's rule: %s)" % (sup, p1[2]), "%s (AF1-P1's rule: %s)" % (ag, p1[3]))
    return out


WINDOWS = {"AF1-P1": ("Jan-Nov 2023 to Jan-Nov 2025", "none"), "AF1-P1w": ("Jan-Nov 2023 to Jan-Nov 2025", "none"),
           "AF1-P2": ("Jan-Nov 2023 to Jan-Nov 2025", "Jan-Nov 2017 to Jan-Nov 2019"), "AF1-P2w": ("Jan-Nov 2023 to Jan-Nov 2025", "Jan-Nov 2017 to Jan-Nov 2019"),
           "AF1-P3": ("Jan-Nov 2024 to Jan-Nov 2025", "none")}


def write_registered(out, root=None, pinned=None):
    sha = check_spec_hash(root, pinned)
    rows = parse_spec_v2(spec_text(root).decode("utf-8"))
    body = []
    for i in IDS:
        st, stat, sup, ag = rows[i]
        body.append([i, "2", "no", "yes", st, stat, sup, ag, WINDOWS[i][0], WINDOWS[i][1], sha])
    text = "# source: %s (version 2 statements table), sha256 %s; written before any statistic is computed\n" % (SPEC_FILE, sha) + csv_line(REG_HEADER) + "".join(csv_line(r) for r in body)
    path = os.path.join(out, "registered.csv")
    write_text(path, text)
    return path, sha


# ------------------------------------------------------------------------------------------------------------------------
# output rows
# ------------------------------------------------------------------------------------------------------------------------
def f4(x):
    return "n/a" if x is None else "%.4f" % x


def pstr(p):
    return "%.4f" % p


NAMES = {"23": "Construction", "31": "Manufacturing (31-33)", "42": "Wholesale trade", "44": "Retail trade (44-45)", "48": "Transportation and warehousing (48-49)", "51": "Information",
         "53": "Real estate and rental", "54": "Professional, scientific and technical services", "56": "Administrative and waste services", "61": "Educational services",
         "62": "Health care and social assistance", "71": "Arts, entertainment and recreation", "72": "Accommodation and food services", "81": "Other services",
         "11": "Agriculture, forestry, fishing", "21": "Mining", "22": "Utilities", "52": "Finance and insurance", "55": "Management of companies"}


def test_stats(t):
    return "perm_p_pos=%s; perm_p_neg=%s; loo_min=%s; loo_max=%s; permutations=%d; seed=%d" % (pstr(t["p_pos"]), pstr(t["p_neg"]), f4(t["loo_min"]), f4(t["loo_max"]), t["nperm"], t["seed"])


def make_rows(R):
    T, kept = R["tests"], R["kept"]
    ns, nd = len(kept), len(R["dropped"])
    den = ("%d sectors kept of %d BTOS sectors with an AI row (dropped %d: %s); months used = January to November (11) of 2017, 2019, 2023, 2025; permutations %d, seed %d" %
           (ns, ns + nd, nd, ", ".join(s for s, _r in R["dropped"]), R["nperm"], R["seed"]))
    scores = []
    caveat = "SUPPORT or AGAINST says only that the predicted cross-industry pattern is present or absent; neither label identifies AI as the cause; BTOS measures AI use by existing employers, not by new applicants"
    for sid, key, ser, stat in (("AF1-P1", "P1", "BA", "spearman_AI_use_vs_g_post_BA"), ("AF1-P2", "P2", "BA", "spearman_AI_use_vs_g_post_minus_g_pre_BA"),
                                ("AF1-P1w", "P1w", "WBA", "spearman_AI_use_vs_g_post_WBA"), ("AF1-P2w", "P2w", "WBA", "spearman_AI_use_vs_g_post_minus_g_pre_WBA")):
        t = T[key]
        scores.append([sid, t["label"], stat, f4(t["rho"]), "rank correlation", test_stats(t), den + "; outcome = NSA %s" % ser, caveat])
    p3 = R["p3"]
    scores.append(["AF1-P3", p3["label"], "pct_change_national_NSA_BA_mean_JanNov_2025_vs_2024", "%.4f" % p3["pct"], "percent",
                   "mean monthly BA Jan-Nov 2024 = %.1f; mean monthly BA Jan-Nov 2025 = %.1f" % (p3["mean_2024"], p3["mean_2025"]),
                   "national TOTAL row (all sectors plus applications with no NAICS code), not seasonally adjusted, 11 months in each of 2 years; no sector selection",
                   "says nothing about AI; a national time series cannot identify AI"])
    detail = []
    d = detail.append
    d(["AF1-SEC", "bfs_release", R.get("release", ""), "date"])
    d(["AF1-SEC", "btos_cycles_required", str(R["ncycles"]), "cycles"])
    d(["AF1-SEC", "sectors_kept", str(ns), "sectors"])
    d(["AF1-SEC", "sectors_dropped", str(nd), "sectors"])
    d(["AF1-SEC", "kept_list", ",".join(kept), "list"])
    for s, reason in R["dropped"]:
        d(["AF1-SEC", "dropped_sector_%s" % s, reason, "text"])
    for key in ("P1", "P2", "P1w", "P2w"):
        t = T[key]
        sid = "AF1-" + key
        for item, val, unit in (("rho", f4(t["rho"]), "rank correlation"), ("perm_p_pos", pstr(t["p_pos"]), "probability"), ("perm_p_neg", pstr(t["p_neg"]), "probability"),
                                ("loo_min", f4(t["loo_min"]), "rank correlation"), ("loo_max", f4(t["loo_max"]), "rank correlation"), ("loo_undefined", str(t["loo_undefined"]), "count"),
                                ("n_sectors", str(t["n"]), "sectors"), ("permutations", str(t["nperm"]), "count"), ("seed", str(t["seed"]), "integer")):
            d([sid, item, val, unit])
        for i, r in t["loo"]:
            d([sid, "loo_without_sector_%s" % kept[i], f4(r), "rank correlation"])
    d(["AF1-P3", "mean_monthly_BA_JanNov_2024", "%.2f" % p3["mean_2024"], "applications"])
    d(["AF1-P3", "mean_monthly_BA_JanNov_2025", "%.2f" % p3["mean_2025"], "applications"])
    d(["AF1-P3", "months_used_per_year", str(MONTHS), "months"])
    for ser in ("BA", "WBA"):
        for s in kept:
            d(["AF1-TABLE", "sector_%s_ai_mean_pct" % s, "%.4f" % R["ai"][s], "percent of firms"])
            for y in YEARS:
                d(["AF1-TABLE", "sector_%s_%s_mean_monthly_JanNov_%d" % (s, ser, y), "%.2f" % R["series"][ser]["means"][s][y], "applications"])
            for k in ("g_pre", "g_post", "diff", "g_post_2425", "g_pre_1819"):
                d(["AF1-TABLE", "sector_%s_%s_%s" % (s, ser, k), "%.6f" % R["series"][ser]["g"][s][k], "log points"])
    for key in sorted(k for k in T if "label" not in T[k]):
        t = T[key]
        sid = "AF1-R-" + key
        for item, val, unit in (("rho", f4(t["rho"]), "rank correlation"), ("perm_p_pos", pstr(t["p_pos"]), "probability"), ("perm_p_neg", pstr(t["p_neg"]), "probability"),
                                ("loo_min", f4(t["loo_min"]), "rank correlation"), ("loo_max", f4(t["loo_max"]), "rank correlation"), ("n_sectors", str(t["n"]), "sectors"),
                                ("sectors", ",".join(t["sectors"]), "list"), ("label_if_it_were_primary_not_used", t["label_if_it_were_primary"], "text")):
            d([sid, item, val, unit])
    d(["AF1-R-WEIGHTED", "pearson_weighted_AI_vs_g_post_BA", f4(R["weighted"]["P1"]), "correlation"])
    d(["AF1-R-WEIGHTED", "pearson_weighted_AI_vs_g_post_minus_g_pre_BA", f4(R["weighted"]["P2"]), "correlation"])
    d(["AF1-R-WEIGHTED", "weights_sum_mean_monthly_BA_JanNov_2019_kept_sectors", "%.2f" % R["weighted"]["weights_total"], "applications"])
    for ser in ("BA", "WBA"):
        nat = R["national"][ser]
        for y in YEARS:
            if nat["nonaics"] is not None:
                d(["AF1-R-NONAICS", "%s_no_naics_share_JanNov_%d" % (ser, y), "%.6f" % (nat["nonaics"][y] / nat["total"][y]), "share of national total"])
            d(["AF1-R-NONAICS", "%s_kept_sectors_share_of_national_JanNov_%d" % (ser, y), "%.6f" % (nat["kept_sum"][y] / nat["total"][y]), "share of national total"])
            d(["AF1-R-NONAICS", "%s_national_total_mean_monthly_JanNov_%d" % (ser, y), "%.2f" % nat["total"][y], "applications"])
    return scores, detail


def release_date(html):
    t = re.sub(r"<[^>]+>", " ", html)
    m = re.search(r"FOR IMMEDIATE RELEASE:\s*\w+,\s*([A-Z][a-z]+ \d{1,2}, \d{4})", t)
    return m.group(1) if m else ""


def vintage_rows(cache):
    rows = []
    last = {}
    for r in read_manifest(cache):
        last[r["key"]] = r
    rel_note = ""
    pp = os.path.join(cache, *PAGE_REL.split("/"))
    if os.path.exists(pp):
        rel_note = release_date(open(pp, encoding="utf-8", errors="replace").read())
    for key, url, _rel in FILES:
        r = last.get(key)
        if r is None:
            raise Refused("manifest has no row for %s: run fetch" % key)
        if key == "bfs-monthly-csv":
            note = "BFS monthly release of %s; Last-Modified header %s; sha256 pinned in bin/af1_ai_formation.py" % (rel_note or "unknown", r.get("last_modified", ""))
        elif key == "bfs-current-release-page":
            note = "gives the release date (%s)" % (rel_note or "unparsed")
        else:
            note = "documentation only; not read by the script"
        rows.append(["census-bfs", key, url, r["fetched_utc"], r["status"], r["bytes"], r["sha256"], note])
    bp = os.path.join(cv1.cache_dir(), *cv1.BTOS_REL.split("/"))
    rows.append(["census-btos", "btos-ai-core-questions", cv1.BTOS_URL, "2026-11-15", "hand download", os.path.getsize(bp) if os.path.exists(bp) else 0, cv1.BTOS_SHA256,
                 "the CV1-P6 input, downloaded by the principal through a browser and hash-pinned in bin/cv1_confidence_velocity.py; read through its code, never fetched here"])
    return rows


def no_leak(name, text):
    for bad in ("@", "/Users/", "/private/", "~/"):
        if bad in text:
            raise Refused("%s would contain %r" % (name, bad))


def table_text(source_line, header, rows):
    return "# source: %s\n" % source_line + csv_line(header) + "".join(csv_line(r) for r in rows)


# ------------------------------------------------------------------------------------------------------------------------
# README
# ------------------------------------------------------------------------------------------------------------------------
CHOICES = (
    "**Permutation p-value convention:** (1 + count) / (10,000 + 1), so a p-value is never exactly zero; a shuffle that ties the observed correlation counts as at least as extreme (compared after rounding to 9 decimals).",
    "**Seed:** 20261115 (the registration date); every test re-seeds from it, so each is reproducible alone.",
    "**Spearman** is the CV1-P6 function (average ranks for ties), also used for the leave-one-out values. A leave-one-out value that is undefined counts as not positive.",
    "**National total (P3):** BFS's own TOTAL row (all sectors plus applications with no NAICS code), not the sum of kept sectors, so that it is the published national number. The comparison is of the two means, equivalent to comparing the 11-month sums.",
    "**Weighted Pearson:** computed on the raw AI percent and the raw growth (not ranks), for both g_post and g_post minus g_pre, business applications; weights are each kept sector's 2019 January-November mean monthly BA. No p-value.",
    "**No 51 and 54** is computed for business applications and for planned-wage applications, with the same permutation method on the remaining sectors; the label it would carry is stored in detail.csv but is not used.",
    "**The 2024-25 window** is log(mean 2025) minus log(mean 2024). The spec names only the post window, so the pre-period for its P2 version is shown two ways: Grok's matched one-year 2018-to-2019 growth (the main reported line) and the registered 2017-to-2019 growth (two years, so its duration differs).",
    "**Data-quality stops:** the build stops if any kept sector has a missing month in January to November of 2017, 2018, 2019, 2023, 2024 or 2025, or a non-positive mean. 2018 and 2024 are read only for the reported 2024-25 window.",
    "**The sector list** is fixed by BTOS cycle counts and BFS membership alone, before any BFS statistic is computed. Sectors suppressed in most cycles (11, 21, 22, 55) drop on the 46-cycle rule; sector 52 drops by the spec's ruling 7.",
    "**Pinned BFS file:** the build refuses to score if `bfs_monthly.csv` does not hash to the 12 Nov 2026 file; a later vintage needs a reviewed new pin.",
    "**Imported CV1 reader:** the CV1-P6 input reader also hash-checks the SIC-NAICS concordance workbook; it is required to load but not used here.",
    "**The BTOS cycle cutoff (before 17 Nov 2025) and the three cycles missing from the workbook** are inherited unchanged from the CV1-P6 code.",
)


def readme_text(R, scores, sha, nrequests):
    T, kept, ai = R["tests"], R["kept"], R["ai"]
    ns, nd = len(kept), len(R["dropped"])
    rel = R.get("release", "")
    lab = {k: T[k]["label"] for k in ("P1", "P2", "P1w", "P2w")}
    p3 = R["p3"]

    def line(key, title):
        t = T[key]
        return "| %s | %s | %s | %s | %s | %s to %s |" % (title, t["label"], f4(t["rho"]), pstr(t["p_pos"]), pstr(t["p_neg"]), f4(t["loo_min"]), f4(t["loo_max"]))
    L = []
    a = L.append
    a("# AF1: did industries that use more AI see more new business applications? (build of 15 Nov 2026)")
    a("")
    a("## What was asked")
    a("")
    a("A published note argues that AI is raising the formation of new companies. Its charts show US business applications rising, but nothing in them measures AI. This test asks the one "
      "question free Census data can answer: **after 2023, did the industries whose existing firms use more AI see a bigger rise in new business applications than the industries that "
      "use less, and was that bigger than the same ranking showed before AI (2017 to 2019)?** It is a comparison across industries. It was registered before any industry-level "
      "application count was read (`%s`, version 2, sha256 `%s`)." % (SPEC_FILE, sha))
    a("")
    a("## The answer")
    a("")
    outcome = {"SUPPORT": "the predicted pattern is present", "AGAINST": "the predicted pattern is absent or reversed", "INCONCLUSIVE": "the data do not decide"}
    a("- **Growth after 2023 against AI use (P1, business applications):** %s - %s. Spearman rank correlation %s across %d sectors; one-sided permutation p for a positive value %s." %
      (lab["P1"], outcome[lab["P1"]], f4(T["P1"]["rho"]), ns, pstr(T["P1"]["p_pos"])))
    a("- **The change against 2017-19 (P2):** %s - %s. Rank correlation %s; p for a positive value %s." % (lab["P2"], outcome[lab["P2"]], f4(T["P2"]["rho"]), pstr(T["P2"]["p_pos"])))
    a("- **The same two on applications with planned wages (P1w, P2w):** %s and %s." % (lab["P1w"], lab["P2w"]))
    a("- **National applications still rising (P3):** %s. Mean monthly applications in January to November 2025 were %.1f%% %s January to November 2024 (%s against %s)." %
      (p3["label"], abs(p3["pct"]), "above" if p3["pct"] > 0 else "below", "{:,.0f}".format(p3["mean_2025"]), "{:,.0f}".format(p3["mean_2024"])))
    a("")
    a("- **How much weight the labelled result bears:** of the four labelled industry tests, SUPPORT %d, INCONCLUSIVE %d, AGAINST %d. Without sectors 51 and 54 (reported, not labelled), P1 is %s (p %s) and P2 is %s (p %s); "
      "with the %d-sector sample the label can change when one or two sectors move." %
      (sum(1 for k in ("P1", "P2", "P1w", "P2w") if lab[k] == "SUPPORT"), sum(1 for k in ("P1", "P2", "P1w", "P2w") if lab[k] == "INCONCLUSIVE"), sum(1 for k in ("P1", "P2", "P1w", "P2w") if lab[k] == "AGAINST"),
       f4(T["P1_no5154"]["rho"]), pstr(T["P1_no5154"]["p_pos"]), f4(T["P2_no5154"]["rho"]), pstr(T["P2_no5154"]["p_pos"]), ns))
    a("")
    a("SUPPORT here means only that the cross-industry pattern the AI thesis predicts is present; AGAINST means it is absent or reversed. Neither label identifies AI as the cause "
      "(see the limits below).")
    a("")
    a("## Result table")
    a("")
    a("Denominators: %d sectors kept (of %d BTOS sectors with an AI row; %d dropped, listed below); months used = January to November, 11 months, in each of 2017, 2019, 2023 and 2025; "
      "%d random permutations of the AI ranking, seed %d." % (ns, ns + nd, nd, R["nperm"], R["seed"]))
    a("")
    a("| statement | label | rank correlation | p (positive) | p (negative) | leave-one-sector-out range |")
    a("|---|---|---|---|---|---|")
    a(line("P1", "P1: AI use vs growth 2023 to 2025, business applications"))
    a(line("P2", "P2: AI use vs that growth minus 2017-19 growth, business applications"))
    a(line("P1w", "P1w: as P1, applications with planned wages"))
    a(line("P2w", "P2w: as P2, applications with planned wages"))
    a("| P3: national applications, Jan-Nov 2025 vs Jan-Nov 2024 | %s | %+.2f%% | | | |" % (p3["label"], p3["pct"]))
    a("")
    a("Rule (registered): SUPPORT if the one-sided permutation p-value for a positive correlation is at most 0.05 **and** every leave-one-sector-out correlation is positive; AGAINST if the "
      "one-sided p-value for a negative correlation is at most 0.05; otherwise INCONCLUSIVE. P3 is SUPPORT if 2025 is higher, AGAINST if equal or lower.")
    a("")
    a("## The sectors")
    a("")
    a("Mean monthly business applications (not seasonally adjusted, January to November) and growth in log points (0.10 is about 10.5%).")
    a("")
    a("| sector | AI use, mean % of firms | 2017 | 2019 | 2023 | 2025 | g_pre (2017 to 2019) | g_post (2023 to 2025) |")
    a("|---|---|---|---|---|---|---|---|")
    ba = R["series"]["BA"]
    for s in kept:
        m, g = ba["means"][s], ba["g"][s]
        a("| %s %s | %.2f | %s | %s | %s | %s | %.3f | %.3f |" % (s, NAMES.get(s, ""), ai[s], "{:,.0f}".format(m[2017]), "{:,.0f}".format(m[2019]), "{:,.0f}".format(m[2023]), "{:,.0f}".format(m[2025]), g["g_pre"], g["g_post"]))
    a("")
    a("**Kept (%d):** %s." % (ns, ", ".join("%s %s" % (s, NAMES.get(s, "")) for s in kept)))
    a("")
    a("**Dropped (%d):**" % nd)
    a("")
    for s, reason in R["dropped"]:
        a("- %s %s: %s." % (s, NAMES.get(s, ""), reason))
    a("")
    a("A sector is kept only if its AI share is published in all %d survey cycles of 2024-2025, so no sector's average is built from a censored subset, and it is a sector in the Census application series. "
      "The kept sectors hold %.1f%% of national applications in January to November 2025 (the rest: dropped sectors and applications with no industry code)." %
      (R["ncycles"], 100.0 * R["national"]["BA"]["kept_sum"][2025] / R["national"]["BA"]["total"][2025]))
    a("")
    a("## Reported, not labelled")
    a("")
    t = T
    a("Each is a one-off robustness item; none sets a label. Denominators as stated in each line.")
    a("")
    a("- **Without sectors 51 (information) and 54 (professional services), the two largest AI users** (%d sectors; one-sided p for a positive value in brackets): business applications P1 %s (%s), P2 %s (%s); planned wages P1w %s (%s), P2w %s (%s)." %
      (len(t["P1_no5154"]["sectors"]), f4(t["P1_no5154"]["rho"]), pstr(t["P1_no5154"]["p_pos"]), f4(t["P2_no5154"]["rho"]), pstr(t["P2_no5154"]["p_pos"]),
       f4(t["P1w_no5154"]["rho"]), pstr(t["P1w_no5154"]["p_pos"]), f4(t["P2w_no5154"]["rho"]), pstr(t["P2w_no5154"]["p_pos"])))
    a("- **Weighted correlation** (Pearson on the raw AI share and the raw growth, each of the %d sectors weighted by its mean monthly applications in January to November 2019, weights summing to %s): AI use against g_post %s; against g_post minus g_pre %s." %
      (ns, "{:,.0f}".format(R["weighted"]["weights_total"]), f4(R["weighted"]["P1"]), f4(R["weighted"]["P2"])))
    a("- **Grok's shorter post window (2024 to 2025, %d sectors):** AI use against log(mean 2025) minus log(mean 2024): rank correlation %s, p positive %s, leave-one-out range %s to %s (business applications); %s, p %s (planned wages). "
      "Against that growth minus 2018-to-2019 growth, a matched one-year pre-period: %s, p %s (business applications); %s, p %s (planned wages). Against that growth minus the registered 2017-to-2019 growth: %s, p %s (business applications)." %
      (ns, f4(t["P1_2425"]["rho"]), pstr(t["P1_2425"]["p_pos"]), f4(t["P1_2425"]["loo_min"]), f4(t["P1_2425"]["loo_max"]), f4(t["P1w_2425"]["rho"]), pstr(t["P1w_2425"]["p_pos"]),
       f4(t["P2_2425"]["rho"]), pstr(t["P2_2425"]["p_pos"]), f4(t["P2w_2425"]["rho"]), pstr(t["P2w_2425"]["p_pos"]), f4(t["P2_2425_regpre"]["rho"]), pstr(t["P2_2425_regpre"]["p_pos"])))
    nat = R["national"]
    a("- **Applications with no industry code, share of the national January-November total** (11 months in each year): " +
      "; ".join("%d: %.2f%% of business applications, %.2f%% of planned-wage applications" % (y, 100.0 * nat["BA"]["nonaics"][y] / nat["BA"]["total"][y], 100.0 * nat["WBA"]["nonaics"][y] / nat["WBA"]["total"][y]) for y in YEARS) +
      ". They belong to no sector, so they are outside every statistic above.")
    a("")
    a("## Method")
    a("")
    a("- **Applications.** Census Business Formation Statistics, monthly file, **not seasonally adjusted**, United States, by sector: business applications (BA) and applications with planned wages (WBA). "
      "Results speak of applications, not companies. The Census data dictionary labels the grouped codes only as Manufacturing, Retail Trade, and Transportation and Warehousing; they are read here as NAICS 31-33, 44-45 and 48-49. Vintage: the %s release, file `bfs_monthly.csv` (sha256 `%s`)." % (rel or "latest", BFS_SHA256))
    a("- **Growth.** For each sector and year, the mean monthly applications over January to November (the same eleven months every year, which keeps the broken December 2025 and seasonality out). "
      "g_post = log(mean 2025) minus log(mean 2023); g_pre = log(mean 2019) minus log(mean 2017). P1 correlates AI use with g_post; P2 with g_post minus g_pre.")
    a("- **AI use.** Census Business Trends and Outlook Survey, question 7 (\"use AI in producing goods or services\"), share answering Yes, mean over the 46 cycles of 2024-2025 that end before 17 Nov 2025, "
      "per sector, computed by the CV1-P6 code (`bin/cv1_confidence_velocity.py`, imported, not copied).")
    a("- **Sector codes.** BFS already publishes manufacturing (31-33), retail trade (44-45) and transportation and warehousing (48-49) as grouped codes (NAICSMNF, NAICSRET, NAICSTW); these are mapped to BTOS sectors 31, 44 and 48. "
      "The script's grouping function would sum separate two-digit codes if they were published (it is tested), but here no summing was needed.")
    a("- **Label by permutation.** The AI values are shuffled across sectors %d times (fixed seed %d), growth held fixed; the one-sided p-value is (1 + number of shuffles at least as extreme) / (%d + 1)." % (R["nperm"], R["seed"], R["nperm"]))
    a("- **Leave-one-out.** For SUPPORT every one of the %d correlations computed without one sector must be positive." % ns)
    a("- **Requests to census.gov:** %d in all (three discovery requests by hand before the script existed: the data page, the release page and the data file; then the %d the `fetch` command makes), GET only, one neutral user-agent string, no contact details, 3 seconds apart; no refusal." % (nrequests, max(nrequests - 3, 0)))
    a("")
    a("## Limits")
    a("")
    a("- **The test cannot identify AI as the cause.** Anything that ranked industries the way AI use does after 2019 (remote work, venture funding, interest-rate exposure, the shift from goods to services, reopening) "
      "would give the same result. Subtracting 2017-19 growth removes only reasons that were already there before. SUPPORT is never evidence that AI raised company formation, and AGAINST says only that the predicted pattern is missing.")
    a("- **BTOS measures AI use by existing employers, not by new applicants.** Whether the new applicants use AI is not measured by any free series found.")
    a("- **Applications are not companies.** An application is a request for an employer identification number, not a firm that exists or hires; applications with planned wages (WBA) are the subset that report planned wages, a closer proxy for employer firms, and are reported as a second labelled pass.")
    a("- **%d sectors is a small sample:** a rank correlation across %d points moves a lot when one sector moves, which is why SUPPORT also requires every leave-one-out correlation to stay positive." % (ns, ns))
    a("- Sector coverage: the %d kept sectors have all %d survey cycles; the dropped ones (including finance, mining, agriculture, utilities and management of companies) are not tested at all." % (ns, R["ncycles"]))
    a("")
    a("## Choices where the spec was silent")
    a("")
    for c in CHOICES:
        a("- " + c)
    a("")
    a("## Files")
    a("")
    a("`registered.csv` (written before any statistic), `scores.csv` (one row per statement), `detail.csv` (every supporting number, including each leave-one-out value and the sector table for both outcomes), `vintages.csv` (what was downloaded, when, and its sha256). "
      "Raw downloads stay in `%s` (gitignored). Re-run: `python3 bin/af1_ai_formation.py fetch` then `build`; `selftest` needs no network." % CACHE_REL)
    a("")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------------------------------
# build
# ------------------------------------------------------------------------------------------------------------------------
def load_inputs(root=None):
    cache = cache_dir(root)
    p = os.path.join(cache, *BFS_REL.split("/"))
    if not os.path.exists(p):
        raise Refused("BFS file missing: %s (run fetch)" % BFS_REL)
    got = sha256_of(open(p, "rb").read())
    if got != BFS_SHA256:
        raise Refused("BFS file has sha256 %s, not the pinned %s" % (got, BFS_SHA256))
    table = load_bfs(p)
    inp = cv1.p6_load_inputs(cv1.cache_dir(root))
    cycles = cv1.btos_cycles(inp["date_rows"])
    ai, _missing, cols = cv1.btos_ai_means(inp["sector_header"], inp["sector_rows"], cycles)
    if len(cols) != N_CYCLES:
        raise Refused("BTOS cycles in the 2024-2025 window: %d, the spec says %d" % (len(cols), N_CYCLES))
    return table, ai, len(cols)


def run_build(root=None, out=None):
    root = root or ROOT
    out = out or out_dir(root)
    cache = cache_dir(root)
    reg_path, sha = write_registered(out, root)                                   # first: before any statistic exists
    reg_sha = sha256_of(open(reg_path, "rb").read())
    print("registered.csv written (spec sha256 %s; file sha256 %s)" % (sha, reg_sha), flush=True)
    table, ai, ncycles = load_inputs(root)
    R = compute(table, ai, ncycles)
    pp = os.path.join(cache, *PAGE_REL.split("/"))
    R["release"] = release_date(open(pp, encoding="utf-8", errors="replace").read()) if os.path.exists(pp) else ""
    scores, detail = make_rows(R)
    vint = vintage_rows(cache)
    src = "bin/af1_ai_formation.py build; scores computed after registered.csv (sha256 %s) was written; spec %s sha256 %s; BFS release %s; permutations %d seed %d" % (reg_sha, SPEC_FILE, sha, R["release"], R["nperm"], R["seed"])
    files = {
        "scores.csv": table_text(src, SCORES_HEADER, scores),
        "detail.csv": table_text(src, DETAIL_HEADER, detail),
        "vintages.csv": table_text("fetch manifest of the raw cache (%s); raw files are not committed" % CACHE_REL, VINTAGES_HEADER, vint),
        "README.md": readme_text(R, scores, sha, read_count(cache)),
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
Checks = cv1.Checks


def synth_table(sectors, g_by_code, dec_boost=0.0):
    """A BFS-shaped table. Each code has a flat monthly level in 2016-2019 and exp(growth * (year - 2022) / 3) times it afterwards; December can be inflated (it must never matter)."""
    table = {}
    for ser in SERIES.values():
        tot = {y: [0.0] * 12 for y in range(2016, 2027)}
        for code, lvl in sectors.items():
            by = {}
            for y in range(2016, 2027):
                v = lvl * (1.0 if y <= 2019 else math.exp(g_by_code[code] * (y - 2022) / 3.0))
                row = [v] * 11 + [v * (1 + dec_boost)]
                by[y] = row
                tot[y] = [a + b for a, b in zip(tot[y], row)]
            table[(ser, code)] = by
        table[(ser, TOTAL_CODE)] = tot
        table[(ser, NONAICS_CODE)] = {y: [10.0] * 12 for y in range(2016, 2027)}
    return table


def selftest():
    ck = Checks()
    # sector grouping
    ck.eq("grouping: NAICSMNF is BTOS 31", btos_sector_of_bfs_code("NAICSMNF"), "31")
    ck.eq("grouping: NAICSRET is BTOS 44", btos_sector_of_bfs_code("NAICSRET"), "44")
    ck.eq("grouping: NAICSTW is BTOS 48", btos_sector_of_bfs_code("NAICSTW"), "48")
    ck.eq("grouping: NAICS32 and NAICS33 fold into 31", (btos_sector_of_bfs_code("NAICS32"), btos_sector_of_bfs_code("NAICS33")), ("31", "31"))
    ck.eq("grouping: NAICS45 into 44 and NAICS49 into 48", (btos_sector_of_bfs_code("NAICS45"), btos_sector_of_bfs_code("NAICS49")), ("44", "48"))
    ck.eq("grouping: NAICS54 stays 54; TOTAL and NONAICS belong to no sector", (btos_sector_of_bfs_code("NAICS54"), btos_sector_of_bfs_code("TOTAL"), btos_sector_of_bfs_code("NONAICS")), ("54", None, None))
    t = {("BA_BA", "NAICS31"): {2020: [1.0] * 12}, ("BA_BA", "NAICS32"): {2020: [2.0] * 12}, ("BA_BA", "NAICS33"): {2020: [4.0] * 12},
         ("BA_BA", "NAICS44"): {2020: [10.0] * 12}, ("BA_BA", "NAICS45"): {2020: [20.0] * 12}, ("BA_BA", "NAICS49"): {2020: [3.0] * 12}, ("BA_BA", "NAICS48"): {2020: [5.0] * 12},
         ("BA_BA", "NAICSMNF"): {2021: [7.0] * 12}, ("BA_BA", "TOTAL"): {2020: [999.0] * 12}, ("BA_WBA", "NAICS31"): {2020: [100.0] * 12}}
    g = group_sectors(t, "BA_BA")
    ck.eq("grouping: 31+32+33 applications are summed into sector 31", g["31"][2020][0], 7.0)
    ck.eq("grouping: 44+45 summed into 44 and 48+49 into 48", (g["44"][2020][3], g["48"][2020][3]), (30.0, 8.0))
    ck.eq("grouping: a pre-grouped code lands on its sector; TOTAL is excluded; another series is not mixed in", (g["31"][2021][0], "TOTAL" in g, sorted(g)), (7.0, False, ["31", "44", "48"]))
    # matched-month means
    jan_dec = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 99999.0]
    ck.near("matched months: mean is over January to November only (December ignored)", jn_mean(jan_dec), 60.0)
    ck.raises("matched months: a missing month inside January-November is refused", ValueError, lambda: jn_mean([1.0] * 5 + [None] + [1.0] * 6))
    ck.near("matched months: a missing December does not matter", jn_mean([5.0] * 11 + [None]), 5.0)
    ck.raises("matched months: fewer than eleven values refused", ValueError, lambda: jn_mean([1.0] * 10))
    # spearman / weighted pearson
    ck.near("spearman: perfectly monotone is 1", spearman([1, 2, 3, 4], [10, 20, 40, 80]), 1.0)
    ck.near("weighted pearson: equal weights give the plain Pearson", weighted_pearson([1, 2, 3, 4], [2, 4, 6, 8], [1, 1, 1, 1]), 1.0)
    ck.near("weighted pearson: known value (weights 1,1,2 on x=1,2,3 and y=1,3,2 give 1/sqrt(5.5))", weighted_pearson([1, 2, 3], [1, 3, 2], [1, 1, 2]), 1.0 / math.sqrt(5.5), 1e-12)
    ck.raises("weighted pearson: zero weights refused", ValueError, lambda: weighted_pearson([1, 2], [1, 2], [0, 0]))
    # permutation p-value: exact enumeration on 6 items; Monte Carlo must agree
    xs, ys = [1, 2, 3, 4, 5, 6], [1, 3, 2, 5, 4, 6]
    obs = spearman(xs, ys)
    perms = list(itertools.permutations(xs))
    ge_exact = sum(1 for p in perms if round(spearman(list(p), ys) - obs, 9) >= 0) / float(len(perms))
    r1 = perm_test(xs, ys, seed=7, nperm=6000)
    ck.ok("permutation: Monte Carlo p matches the exact enumeration of 720 permutations (%.4f) to within 0.02" % ge_exact, abs(r1["p_pos"] - ge_exact) < 0.02, "mc %s exact %s" % (r1["p_pos"], ge_exact))
    ck.near("permutation: a perfect rank match on 12 items has the smallest possible p, (1+0)/(N+1)", perm_test(list(range(12)), list(range(12)), seed=3, nperm=999)["p_pos"], 1.0 / 1000.0)
    rn = perm_test(list(range(12)), list(range(11, -1, -1)), seed=3, nperm=999)
    ck.ok("permutation: a perfectly reversed ranking has p_neg = 1/(N+1) and p_pos near 1", abs(rn["p_neg"] - 0.001) < 1e-12 and rn["p_pos"] > 0.99, "%s %s" % (rn["p_neg"], rn["p_pos"]))
    ck.eq("permutation: the same seed gives the same p", perm_test(xs, ys, 11, 500)["p_pos"], perm_test(xs, ys, 11, 500)["p_pos"])
    ck.ok("permutation: a null relation (a shuffled y) is not significant on 14 items", perm_test(list(range(14)), [5, 11, 2, 9, 0, 13, 7, 3, 12, 1, 8, 4, 10, 6], seed=2, nperm=2000)["p_pos"] > 0.05)
    # leave-one-out rule, through the real functions
    res = perm_test([float(i) for i in range(1, 13)], [float(i) for i in range(1, 13)], seed=1, nperm=2000)
    ck.eq("label: a clean positive relation is SUPPORT", label_perm(res), "SUPPORT")
    ck.ok("leave-one-out: every one-out correlation is reported (12 of them) and all are positive", len(res["loo"]) == 12 and res["loo_min"] > 0)
    fx = perm_test([1.0, 2, 3, 4, 5, 6, 7], [1.0, 2, 6, 7, 4, 5, 3], seed=1, nperm=500)       # rho 0.357, but without the first-listed sector or others it dips below zero
    ck.ok("leave-one-out: a positive rho whose leave-one-out minimum is negative exists (rho %.3f, min %.3f)" % (fx["rho"], fx["loo_min"]), fx["rho"] > 0 and fx["loo_min"] < 0)
    ck.eq("label: even with a small p-value that fragile relation is INCONCLUSIVE", label_perm(dict(fx, p_pos=0.01)), "INCONCLUSIVE")
    base = dict(rho=0.5, p_pos=0.01, p_neg=0.99, loo=[], n=10, loo_min=0.2, loo_max=0.7, loo_undefined=0, nperm=100, seed=1)
    ck.eq("label: small p and all leave-one-out positive is SUPPORT", label_perm(base), "SUPPORT")
    ck.eq("label: small p but a leave-one-out value of 0 is INCONCLUSIVE", label_perm(dict(base, loo_min=0.0)), "INCONCLUSIVE")
    ck.eq("label: small p but an undefined leave-one-out value is INCONCLUSIVE", label_perm(dict(base, loo_undefined=1)), "INCONCLUSIVE")
    ck.eq("label: p exactly 0.05 counts (SUPPORT)", label_perm(dict(base, p_pos=0.05)), "SUPPORT")
    ck.eq("label: p just over 0.05 is INCONCLUSIVE", label_perm(dict(base, p_pos=0.0501)), "INCONCLUSIVE")
    ck.eq("label: negative side p <= 0.05 is AGAINST whatever the leave-one-out values", label_perm(dict(base, rho=-0.5, p_pos=0.99, p_neg=0.02, loo_min=-0.9)), "AGAINST")
    ck.eq("label: neither side significant is INCONCLUSIVE", label_perm(dict(base, p_pos=0.4, p_neg=0.7)), "INCONCLUSIVE")
    ck.eq("label P3: higher is SUPPORT, equal is AGAINST, lower is AGAINST", (label_p3(100, 101), label_p3(100, 100), label_p3(100, 99)), ("SUPPORT", "AGAINST", "AGAINST"))
    # sector selection
    ai = {"23": {"mean": 2.0, "used": ["x"] * 46}, "52": {"mean": 9.0, "used": ["x"] * 46}, "55": {"mean": 18.0, "used": ["x"] * 7}, "22": {"mean": 10.0, "used": ["x"] * 4},
          "99": {"mean": 1.0, "used": ["x"] * 46}, "54": {"mean": 16.0, "used": ["x"] * 46}}
    kept, dropped = select_sectors(ai, 46, {"23", "54", "52", "55", "22"})
    ck.eq("selection: only 46-cycle sectors that are in BFS and are not 52 are kept", kept, ["23", "54"])
    ck.eq("selection: dropped are 22, 52, 55, 99", [s for s, _r in dropped], ["22", "52", "55", "99"])
    ck.ok("selection: 52's reason names NAICS 525; 55's names the cycle count", "525" in dict(dropped)["52"] and "7 of 46" in dict(dropped)["55"])
    # end-to-end synthetic: December inflation must not change anything; growth tracks AI
    order = {"NAICS23": "23", "NAICSMNF": "31", "NAICS42": "42", "NAICSRET": "44", "NAICSTW": "48", "NAICS51": "51", "NAICS53": "53", "NAICS54": "54", "NAICS56": "56", "NAICS61": "61",
             "NAICS62": "62", "NAICS71": "71", "NAICS72": "72", "NAICS81": "81"}
    levels = {c: 300.0 + 100.0 * i for i, c in enumerate(order)}
    aiv = {"23": 2.4, "31": 3.3, "42": 3.9, "44": 4.2, "48": 2.1, "51": 20.9, "53": 9.4, "54": 16.2, "56": 6.1, "61": 12.2, "62": 7.0, "71": 6.5, "72": 1.9, "81": 3.1}
    gby = {c: 0.02 * aiv[order[c]] for c in order}                                     # growth rises with AI use
    ai_in = {s: {"mean": v, "used": ["x"] * 46} for s, v in aiv.items()}
    ai_in["52"] = {"mean": 9.6, "used": ["x"] * 46}
    ai_in["55"] = {"mean": 18.0, "used": ["x"] * 7}
    RA = compute(synth_table(levels, gby), ai_in, 46, seed=5, nperm=500)
    RB = compute(synth_table(levels, gby, dec_boost=5.0), ai_in, 46, seed=5, nperm=500)
    ck.eq("end to end: 14 sectors kept; 52 and 55 dropped", (len(RA["kept"]), [s for s, _r in RA["dropped"]]), (14, ["52", "55"]))
    ck.near("end to end: P1 rho is 1 when growth is monotone in AI use", RA["tests"]["P1"]["rho"], 1.0)
    ck.eq("end to end: P1 is SUPPORT", RA["tests"]["P1"]["label"], "SUPPORT")
    ck.near("end to end: a December blow-up changes nothing (P1 rho plus a sector mean)", RB["tests"]["P1"]["rho"] + RB["series"]["BA"]["means"]["23"][2025], RA["tests"]["P1"]["rho"] + RA["series"]["BA"]["means"]["23"][2025])
    ck.near("end to end: g_post for sector 23 is log(mean 2025) - log(mean 2023)", RA["series"]["BA"]["g"]["23"]["g_post"], math.log(math.exp(gby["NAICS23"]) / math.exp(gby["NAICS23"] / 3.0)), 1e-12)
    ck.near("end to end: g_pre is 0 because 2017 and 2019 are equal", RA["series"]["BA"]["g"]["23"]["g_pre"], 0.0, 1e-12)
    ck.ok("end to end: P2 equals P1 when g_pre is flat", abs(RA["tests"]["P2"]["rho"] - RA["tests"]["P1"]["rho"]) < 1e-12)
    ck.eq("end to end: the no-51-54 variant uses 12 sectors", RA["tests"]["P1_no5154"]["n"], 12)
    ck.ok("end to end: P3 compares TOTAL Jan-Nov 2025 with 2024 (higher: SUPPORT)", RA["p3"]["label"] == "SUPPORT" and RA["p3"]["pct"] > 0)
    RN = compute(synth_table(levels, {c: -v for c, v in gby.items()}), ai_in, 46, seed=5, nperm=500)
    ck.eq("end to end: growth falling with AI use is AGAINST on P1, and a falling national total is AGAINST on P3", (RN["tests"]["P1"]["label"], RN["p3"]["label"]), ("AGAINST", "AGAINST"))
    # BFS file reading: NSA rows only
    with tempfile.TemporaryDirectory() as td:
        pth = os.path.join(td, "b.csv")
        with open(pth, "w", encoding="utf-8") as fh:
            fh.write("sa,naics_sector,series,geo,year,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,dec\n")
            fh.write("U,TOTAL,BA_BA,US,2025,1,1,1,1,1,1,1,1,1,1,1,1\nA,TOTAL,BA_BA,US,2025,9,9,9,9,9,9,9,9,9,9,9,9\nU,TOTAL,BA_BA,CA,2025,5,5,5,5,5,5,5,5,5,5,5,5\n")
            fh.write("U,TOTAL,BA_WBA,US,2025,2,2,2,2,2,2,2,2,2,2,2,\nU,NAICS11,BA_HBA,US,2025,3,3,3,3,3,3,3,3,3,3,3,3\n")
        tb = load_bfs(pth)
        ck.eq("BFS read: only the not-seasonally-adjusted US rows of BA and WBA", (sorted(tb), tb[("BA_BA", "TOTAL")][2025][0], tb[("BA_WBA", "TOTAL")][2025][11]), ([("BA_BA", "TOTAL"), ("BA_WBA", "TOTAL")], 1.0, None))
        with open(pth, "w", encoding="utf-8") as fh:
            fh.write("sa,naics_sector,series,geo,year,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,dec\nA,TOTAL,BA_BA,US,2025,9,9,9,9,9,9,9,9,9,9,9,9\n")
        ck.raises("BFS read: a file with only seasonally adjusted rows is refused", Refused, lambda: load_bfs(pth))
    # spec parsing and hash refusal
    spec_bytes = spec_text()
    ck.eq("spec: the file on disk hashes to the pinned value", sha256_of(spec_bytes), SPEC_SHA256)
    rows = parse_spec_v2(spec_bytes.decode("utf-8"))
    ck.eq("spec: five registered statements parsed from the version 2 table", sorted(rows), sorted(IDS))
    ck.ok("spec: P1w is P1's rule on WBA", "WBA" in rows["AF1-P1w"][1] and rows["AF1-P1"][2] in rows["AF1-P1w"][2] and rows["AF1-P1"][3] in rows["AF1-P2w"][3] and rows["AF1-P1"][2] in rows["AF1-P2"][2])
    ck.raises("spec: a changed spec file is refused", Refused, lambda: check_spec_hash(pinned="0" * 64))
    ck.raises("spec: a text without the version 2 section is refused", Refused, lambda: parse_spec_v2("| AF1-P1 | a | b | c | d |"))
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "_research"))
        with open(os.path.join(td, *SPEC_FILE.split("/")), "wb") as fh:
            fh.write(spec_bytes + b"\nedit\n")
        ck.raises("spec: a tampered copy stops write_registered", Refused, lambda: write_registered(os.path.join(td, "out"), root=td))
        ck.ok("spec: and nothing was written", not os.path.exists(os.path.join(td, "out", "registered.csv")))
    # fetch: counts requests, spaces them, latches on 403
    with tempfile.TemporaryDirectory() as td:
        slept = []
        op = cv1.FakeOpener([200, 200, 200])
        f = cv1.Fetcher(cache_dir(td), opener=op)
        cmd_fetch(td, fetcher=f, sleep=slept.append)
        ck.eq("fetch: three files, three requests, two 3-second gaps, user agent exactly the house string", (len(op.calls), slept, op.calls[0][1]["user-agent"]), (3, [3.0, 3.0], UA))
        ck.ok("fetch: the user agent holds no contact address", chr(64) not in op.calls[0][1]["user-agent"])
        cmd2 = cmd_fetch(td, fetcher=f, sleep=slept.append)
        ck.eq("fetch: the request counter is 3 and a second run makes no request", (read_count(cache_dir(td)), cmd2, len(op.calls)), (3, 0, 3))
    with tempfile.TemporaryDirectory() as td:
        op = cv1.FakeOpener([200, 403])
        f = cv1.Fetcher(cache_dir(td), opener=op)
        ck.raises("fetch: a 403 stops with Stop", Stop, lambda: cmd_fetch(td, fetcher=f, sleep=lambda s: None))
        ck.ok("fetch: STOP_www_census_gov is written", os.path.exists(os.path.join(cache_dir(td), "STOP_www_census_gov")))
        n0 = len(op.calls)
        ck.raises("fetch: the latch blocks the next run", Stop, lambda: cmd_fetch(td, fetcher=f, sleep=lambda s: None))
        ck.eq("fetch: no further HTTP call after the latch", len(op.calls), n0)
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(cache_dir(td))
        write_count(cache_dir(td), 9)
        ck.raises("fetch: the cap of 10 census.gov requests in all is enforced", Refused, lambda: cmd_fetch(td, fetcher=cv1.Fetcher(cache_dir(td), opener=cv1.FakeOpener([])), sleep=lambda s: None))
    ck.eq("release date parsed from the release page text", release_date("<p>FOR IMMEDIATE RELEASE: Thursday, November 12, 2026 Business</p>"), "November 12, 2026")
    ck.raises("no_leak: an at sign is refused", Refused, lambda: no_leak("x", "a@b"))
    bad = [(n, d) for n, c, d in ck.items if not c]
    for n, c, d in ck.items:
        print(("ok   " if c else "FAIL ") + n + ("" if c else "  <- " + d))
    print("%d checks, %d failed" % (len(ck.items), len(bad)))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="AF1 AI-use vs business-applications scorer (spec version 2)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sub.add_parser("fetch")
    bp = sub.add_parser("build")
    bp.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    try:
        if a.cmd == "fetch":
            return cmd_fetch()
        run_build(out=a.out)
    except Stop as e:
        print("STOP: %s" % e, file=sys.stderr)
        return 4
    except Refused as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
