#!/usr/bin/env python3
"""AJ1: does AI create more jobs than it displaces? Registered statements AJ1-P1, AJ1-P2, AJ1-P3 (version 2 of the spec).
Python 3 standard library plus openpyxl and xlrd (read by the CV1-P6 code this script imports).

  python3 bin/aj1_ai_jobs.py selftest                 # synthetic data only; no network
  python3 bin/aj1_ai_jobs.py fetch                    # BLS Public Data API v1 (2 POSTs, <=25 series each, 3 s apart)
  python3 bin/aj1_ai_jobs.py build [--out DIR]        # offline; writes registered.csv FIRST, then computes every statistic

Specification: _research/2026-11-16-AJ1-AI-Jobs-Spec.md ("Version 2" governs; its sha256 is pinned in SPEC_SHA256 below and the build refuses to score if the file differs).
Outputs: data/aj1_ai_jobs/ (registered.csv, scores.csv, detail.csv, vintages.csv, README.md). Raw downloads: data/vintages/aj1/ (gitignored, never committed).
The BTOS sector and subsector AI-use means come from bin/cv1_confidence_velocity.py (CV1-P6 code path, imported, not copied).

WHAT TOUCHES THE NETWORK. Only `fetch`. api.bls.gov/publicAPI/v1/timeseries/data/ only (POST, no API key, no registration key, no contact details); User-Agent is the neutral string fixed in cv1_confidence_velocity.py.
Any HTTP != 200, non-REQUEST_SUCCEEDED status, stop-message ("does not exist", "threshold", "limit"), or series with no data writes data/vintages/aj1/STOP.txt and exits non-zero.
"""
import argparse
import csv
import json
import math
import os
import random
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv1_confidence_velocity as cv1                          # noqa: E402  (the CV1-P6 BTOS code path, imported)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_FILE = "_research/2026-11-16-AJ1-AI-Jobs-Spec.md"
SPEC_SHA256 = "53b53f49a93d55910f03088a9b5bbbbfcbd46e0bf6617fce8238efc8c45571c1"
OUT_REL = "data/aj1_ai_jobs"
CACHE_REL = "data/vintages/aj1"
Refused = cv1.Refused
Stop = cv1.Stop
sha256_of = cv1.sha256_of
now_utc = cv1.now_utc
write_text = cv1.write_text
write_bytes = cv1.write_bytes
csv_line = cv1.csv_line
spearman = cv1.spearman
UA = cv1.UA
Checks = cv1.Checks

BLS_URL = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
BLS_START_YEAR = "2017"
BLS_END_YEAR = "2026"
GAP_SECONDS = 3.0
TIMEOUT = 120

PERM_SEED = 20261116                                           # fixed; recorded in every output
N_PERM = 100000
ALPHA = 0.05
N_CYCLES = 46                                                  # 2024-2025 cycles before 17 Nov 2025
N_CYCLES_2023 = 8                                              # 202319-202326
MAIN_YEARS = (2017, 2019, 2023, 2025)
ALL_YEARS = (2017, 2018, 2019, 2023, 2024, 2025)

# 19 labelled CES subsectors (version 2)
CES_LABELLED = {
    "238": "CEU2023800001",
    "423": "CEU4142300001",
    "424": "CEU4142400001",
    "441": "CEU4244100001",
    "512": "CEU5051200001",
    "518": "CEU5051800001",
    "522": "CEU5552200001",
    "524": "CEU5552400001",
    "531": "CEU5553100001",
    "541": "CEU6054000001",
    "561": "CEU6056100001",
    "611": "CEU6561000001",
    "621": "CEU6562100001",
    "624": "CEU6562400001",
    "711": "CEU7071100001",
    "713": "CEU7071300001",
    "722": "CEU7072200001",
    "811": "CEU8081100001",
    "812": "CEU8081200001",
}
# 3 reported-only CES subsectors
CES_REPORTED = {
    "513": "CEU5051300001",                                    # matched from BTOS 511
    "519": "CEU5051900001",
    "523": "CEU5552300001",
}
# 3 weight / national CES series
CES_AUX = {
    "05": "CEU0500000001",                                     # total private
    "55": "CEU6055000001",                                     # management of companies
    "56": "CEU6056000001",                                     # administrative and waste services (sector 56)
}
# 15 JOLTS child industries (openings level, NSA) -> (name, BTOS sector mapping)
JOLTS_CODES = (
    ("230000", "Construction", "23"),
    ("320000", "Durable goods manufacturing", "31"),
    ("340000", "Nondurable goods manufacturing", "31"),
    ("420000", "Wholesale trade", "42"),
    ("440000", "Retail trade", "44"),
    ("480099", "Transportation, warehousing, and utilities", "48"),
    ("510000", "Information", "51"),
    ("520000", "Finance and insurance", "52"),
    ("530000", "Real estate and rental and leasing", "53"),
    ("540099", "Professional and business services", "54+56"),
    ("610000", "Educational services", "61"),
    ("620000", "Health care and social assistance", "62"),
    ("710000", "Arts, entertainment, and recreation", "71"),
    ("720000", "Accommodation and food services", "72"),
    ("810000", "Other services", "81"),
)
JOLTS_SERIES = {code: "JTU%s000000000JOL" % code for code, _name, _sec in JOLTS_CODES}

CES_BATCH_IDS = (
    [CES_LABELLED[k] for k in sorted(CES_LABELLED, key=int)]
    + [CES_REPORTED[k] for k in sorted(CES_REPORTED, key=int)]
    + [CES_AUX[k] for k in ("05", "55", "56")]
)                                                              # 25 series
JOLTS_BATCH_IDS = [JOLTS_SERIES[code] for code, _n, _s in JOLTS_CODES]  # 15 series
BATCHES = (
    ("bls-ces", "raw/bls_ces.json", CES_BATCH_IDS),
    ("bls-jolts", "raw/bls_jolts.json", JOLTS_BATCH_IDS),
)

SUBSECTOR_NAMES = {
    "238": "Specialty trade contractors",
    "423": "Merchant wholesalers, durable goods",
    "424": "Merchant wholesalers, nondurable goods",
    "441": "Motor vehicle and parts dealers",
    "454": "Nonstore retailers (abolished in NAICS 2022)",
    "511": "Publishing industries (matched to CES 513)",
    "512": "Motion picture and sound recording industries",
    "513": "Publishing industries (CES NAICS 2022)",
    "518": "Computing infrastructure providers, data processing, web hosting",
    "519": "Web search portals, libraries, archives, and other information services",
    "522": "Credit intermediation and related activities",
    "523": "Securities, commodity contracts, funds, trusts, and other financial vehicles",
    "524": "Insurance carriers and related activities",
    "531": "Real estate",
    "541": "Professional, scientific, and technical services",
    "561": "Administrative and support services",
    "611": "Educational services",
    "621": "Ambulatory health care services",
    "624": "Social assistance",
    "711": "Performing arts, spectator sports, and related industries",
    "713": "Amusement, gambling, and recreation industries",
    "722": "Food services and drinking places",
    "811": "Repair and maintenance",
    "812": "Personal and laundry services",
}

REG_HEADER = ("statement_id", "version", "superseded", "scored", "statement", "statistic", "support_if", "against_if", "treatment_window", "placebo_window", "prereg_sha256")
SCORES_HEADER = ("statement_id", "label", "primary_statistic", "primary_value", "unit", "statistics", "denominators", "caveats")
DETAIL_HEADER = ("statement_id", "item", "value", "unit")
VINTAGES_HEADER = ("source", "key", "url", "fetched_utc", "status", "bytes", "sha256", "note")
LABELS = ("SUPPORT", "AGAINST", "INCONCLUSIVE")
COMMITTED = ("README.md", "registered.csv", "scores.csv", "detail.csv", "vintages.csv")
IDS = ("AJ1-P1", "AJ1-P2", "AJ1-P3")


def cache_dir(root=None):
    return os.path.join(root or ROOT, *CACHE_REL.split("/"))


def out_dir(root=None):
    return os.path.join(root or ROOT, *OUT_REL.split("/"))


# ------------------------------------------------------------------------------------------------------------------------
# fetch (BLS Public Data API v1, POST, no API key)
# ------------------------------------------------------------------------------------------------------------------------
class BlsFetcher(object):
    """POST JSON to api.bls.gov v1. `opener` is injectable for the selftest."""

    def __init__(self, opener=None):
        self.opener = opener or urllib.request.build_opener()

    def post(self, url, body_bytes, headers):
        req = urllib.request.Request(url, data=body_bytes, headers=headers, method="POST")
        try:
            with self.opener.open(req, timeout=TIMEOUT) as resp:
                return resp.status, resp.read(), dict(resp.headers)
        except urllib.error.HTTPError as e:
            return e.code, e.read() if hasattr(e, "read") else b"", dict(e.headers or {})


def stop_with(cache, reason):
    write_text(os.path.join(cache, "STOP.txt"), reason + "\n")
    raise Stop(reason)


def read_manifest(cache):
    p = os.path.join(cache, "manifest.csv")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _validate_bls_response(cache, key, batch_ids, status, body):
    if status != 200:
        stop_with(cache, "%s: HTTP status %s (expected 200)" % (key, status))
    try:
        obj = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        stop_with(cache, "%s: invalid JSON (%s)" % (key, e))
    if obj.get("status") != "REQUEST_SUCCEEDED":
        msgs = "; ".join(str(m) for m in (obj.get("message") or []))
        stop_with(cache, "%s: BLS status %r (%s)" % (key, obj.get("status"), msgs or "no message"))
    for msg in (obj.get("message") or []):
        low = str(msg).lower()
        for bad in ("does not exist", "threshold", "limit"):
            if bad in low:
                stop_with(cache, "%s: BLS message contains %r (%s)" % (key, bad, msg))
    series_list = (obj.get("Results") or {}).get("series") or []
    by_id = {s.get("seriesID"): s.get("data") or [] for s in series_list}
    for sid in batch_ids:
        if not by_id.get(sid):
            stop_with(cache, "%s: series %s returned no data" % (key, sid))
    return obj


def cmd_fetch(root=None, fetcher=None, sleep=time.sleep):
    cache = cache_dir(root)
    os.makedirs(cache, exist_ok=True)
    stop_path = os.path.join(cache, "STOP.txt")
    if os.path.exists(stop_path):
        raise Stop("STOP.txt present in %s; review and delete manually before retrying" % CACHE_REL)
    for _key, rel, _ids in BATCHES:
        if os.path.exists(os.path.join(cache, *rel.split("/"))):
            raise Refused("raw file %s already exists in %s (no refetch)" % (rel, CACHE_REL))
    f = fetcher or BlsFetcher()
    headers = {"Content-Type": "application/json", "User-Agent": UA}
    mp = os.path.join(cache, "manifest.csv")
    for idx, (key, rel, batch_ids) in enumerate(BATCHES):
        assert len(batch_ids) <= 25
        if idx > 0:
            sleep(GAP_SECONDS)
        payload = json.dumps({"seriesid": batch_ids, "startyear": BLS_START_YEAR, "endyear": BLS_END_YEAR}).encode("utf-8")
        status, body, _hdrs = f.post(BLS_URL, payload, headers)
        _validate_bls_response(cache, key, batch_ids, status, body)
        write_bytes(os.path.join(cache, *rel.split("/")), body)
        new = not os.path.exists(mp)
        with open(mp, "a", encoding="utf-8", newline="") as fh:
            if new:
                fh.write("key,url,fetched_utc,status,bytes,sha256,n_series\n")
            fh.write(csv_line([key, BLS_URL, now_utc(), status, len(body), sha256_of(body), len(batch_ids)]))
        print("%s: fetched %d series, %d bytes, sha256 %s" % (key, len(batch_ids), len(body), sha256_of(body)))
    return 0


# ------------------------------------------------------------------------------------------------------------------------
# BLS JSON parsing & windows
# ------------------------------------------------------------------------------------------------------------------------
def parse_bls_json(raw_bytes):
    """Parse one cached BLS API v1 JSON file. Drops period M13. Returns (series_map, release_note)."""
    obj = json.loads(raw_bytes.decode("utf-8"))
    if obj.get("status") != "REQUEST_SUCCEEDED":
        raise Refused("cached BLS JSON has status %r" % obj.get("status"))
    notes = []
    for m in (obj.get("message") or []):
        s = str(m).strip()
        if s and s not in notes:
            notes.append(s)
    foot_texts = []
    series_map = {}
    for s in (obj.get("Results") or {}).get("series") or []:
        sid = s.get("seriesID")
        ym = {}
        for row in s.get("data") or []:
            per = str(row.get("period", "")).strip()
            if per == "M13":
                continue
            m_obj = re.match(r"^M(0[1-9]|1[0-2])$", per)
            if not m_obj:
                continue
            try:
                yr = int(row["year"])
                val = float(row["value"])
            except (KeyError, TypeError, ValueError):
                continue
            ym[(yr, int(m_obj.group(1)))] = val
            for fn in row.get("footnotes") or []:
                ft = str((fn or {}).get("text", "")).strip()
                if ft and ft not in foot_texts:
                    foot_texts.append(ft)
        series_map[sid] = ym
    combined = notes + foot_texts
    return series_map, ("; ".join(combined) if combined else "not stated")


def annual_mean(ym_map, year):
    """Mean over all 12 monthly values (M01..M12) of `year`. Refuses if fewer than 12 months."""
    vals = [ym_map[(year, m)] for m in range(1, 13) if (year, m) in ym_map]
    if len(vals) != 12:
        raise Refused("year %d has %d of 12 months (all 12 required)" % (year, len(vals)))
    mean = sum(vals) / 12.0
    if not mean > 0:
        raise Refused("non-positive annual mean in %d" % year)
    return mean


def common_latest_12(series_maps):
    """Latest 12 (year, month) pairs available in common across all `series_maps`, plus matching 2023 months."""
    if not series_maps:
        return None
    common = set(series_maps[0].keys())
    for ym in series_maps[1:]:
        common &= set(ym.keys())
    ordered = sorted(common)
    if len(ordered) < 12:
        return None
    latest = ordered[-12:]
    if not all(all((2023, m) in ym for _y, m in latest) for ym in series_maps):
        return None
    return latest


def latest_12_growth(ym_map, latest_months):
    m_now = sum(ym_map[ym] for ym in latest_months) / 12.0
    m_23 = sum(ym_map[(2023, m)] for _y, m in latest_months) / 12.0
    if not (m_now > 0 and m_23 > 0):
        raise Refused("non-positive mean in latest-12-months window")
    return math.log(m_now) - math.log(m_23)


def format_ym_span(latest_months):
    (y0, m0), (y1, m1) = latest_months[0], latest_months[-1]
    return "%04d-%02d..%04d-%02d" % (y0, m0, y1, m1)


# ------------------------------------------------------------------------------------------------------------------------
# BTOS inputs (reusing cv1_confidence_velocity.py)
# ------------------------------------------------------------------------------------------------------------------------
def load_btos_inputs(root=None):
    """Load Sector Estimates and Subsector Estimates via cv1.btos_ai_means, for 2024-25 (46 cycles) and 2023 (8 cycles)."""
    inp = cv1.p6_load_inputs(cv1.cache_dir(root))
    cycles = cv1.btos_cycles(inp["date_rows"])
    import openpyxl
    bp = os.path.join(cv1.cache_dir(root), *cv1.BTOS_REL.split("/"))
    wb = openpyxl.load_workbook(bp, read_only=True, data_only=True)
    sub = list(wb["Subsector Estimates"].iter_rows(values_only=True))
    wb.close()
    sec_ai, _sec_miss, sec_cols = cv1.btos_ai_means(inp["sector_header"], inp["sector_rows"], cycles)
    sub_ai, _sub_miss, sub_cols = cv1.btos_ai_means(sub[0], sub[1:], cycles)
    if len(sec_cols) != N_CYCLES or len(sub_cols) != N_CYCLES:
        raise Refused("BTOS 2024-2025 cycle count mismatch: sector=%d subsector=%d (expected %d)" % (len(sec_cols), len(sub_cols), N_CYCLES))
    old_years = cv1.P6_YEARS
    try:
        cv1.P6_YEARS = (2023,)
        sec_ai_23, _, sec_cols_23 = cv1.btos_ai_means(inp["sector_header"], inp["sector_rows"], cycles)
        sub_ai_23, _, sub_cols_23 = cv1.btos_ai_means(sub[0], sub[1:], cycles)
    finally:
        cv1.P6_YEARS = old_years
    if len(sec_cols_23) != N_CYCLES_2023 or len(sub_cols_23) != N_CYCLES_2023:
        raise Refused("BTOS 2023 cycle count mismatch: sector=%d subsector=%d (expected %d)" % (len(sec_cols_23), len(sub_cols_23), N_CYCLES_2023))
    return {
        "sec_2425": sec_ai, "sub_2425": sub_ai, "cycles_2425": len(sec_cols),
        "sec_2023": sec_ai_23, "sub_2023": sub_ai_23, "cycles_2023": len(sec_cols_23),
    }


# ------------------------------------------------------------------------------------------------------------------------
# statistics: permutation test, version-2 label rule, weighted Pearson
# ------------------------------------------------------------------------------------------------------------------------
def perm_test(ai, y, seed=PERM_SEED, nperm=N_PERM):
    """Spearman of ai against y; one-sided permutation p-values over `nperm` random permutations of AI values (y held fixed),
    p = (1 + #{perm as extreme}) / (nperm + 1), and leave-one-out."""
    obs = spearman(ai, y)
    if obs is None:
        raise ValueError("Spearman undefined (no variation or fewer than 3 items)")
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
    return {
        "rho": obs,
        "p_pos": (1.0 + ge) / (nperm + 1.0),
        "p_neg": (1.0 + le) / (nperm + 1.0),
        "loo": loo,
        "n": len(ai),
        "loo_min": min(vals) if vals else None,
        "loo_max": max(vals) if vals else None,
        "loo_undefined": len(loo) - len(vals),
        "nperm": nperm,
        "seed": seed,
    }


def mc_se_at(alpha=ALPHA, nperm=N_PERM):
    return math.sqrt(alpha * (1.0 - alpha) / float(nperm))


def label_perm(res, alpha=ALPHA):
    """Version 2 rule:
    SUPPORT: p_pos <= alpha (and outside 2 MC SEs of alpha) AND all leave-one-out rho > 0.
    AGAINST: p_neg <= alpha (and outside 2 MC SEs of alpha) AND all leave-one-out rho < 0.
    Otherwise INCONCLUSIVE."""
    se = mc_se_at(alpha, res["nperm"])
    loo_all_pos = res["loo_undefined"] == 0 and res["loo_min"] is not None and round(res["loo_min"], 9) > 0
    loo_all_neg = res["loo_undefined"] == 0 and res["loo_max"] is not None and round(res["loo_max"], 9) < 0
    pos_ok = round(res["p_pos"], 9) <= alpha and abs(res["p_pos"] - alpha) > 2.0 * se
    neg_ok = round(res["p_neg"], 9) <= alpha and abs(res["p_neg"] - alpha) > 2.0 * se
    if pos_ok and loo_all_pos:
        return "SUPPORT"
    if neg_ok and loo_all_neg:
        return "AGAINST"
    return "INCONCLUSIVE"


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


def select_subsectors(sub_ai, ncycles=N_CYCLES):
    """Apply version-2 subsector matching rules. Returns (kept_19, dropped_list)."""
    kept, dropped = [], []
    drop_reasons = {
        "454": "abolished in NAICS 2022 (spec ruling 5)",
        "511": "matched to CES 513, scope changed materially in NAICS 2022 (spec ruling 5; reported only)",
        "519": "scope changed materially in NAICS 2022 (spec ruling 5; reported only)",
        "523": "CES 523 includes NAICS 525, which BTOS excludes (spec ruling 6; reported only)",
    }
    for s in sorted(sub_ai, key=int):
        used = len(sub_ai[s]["used"])
        if used < ncycles:
            dropped.append((s, "AI share published in %d of %d cycles (suppressed in %d)" % (used, ncycles, ncycles - used)))
        elif s in drop_reasons:
            dropped.append((s, drop_reasons[s]))
        elif s not in CES_LABELLED:
            dropped.append((s, "not in version-2 CES 3-digit subsector list"))
        else:
            kept.append(s)
    return kept, dropped


def _series_growth(ym_map, latest_months):
    m = {y: annual_mean(ym_map, y) for y in ALL_YEARS}
    g = {
        "g_post": math.log(m[2025]) - math.log(m[2023]),
        "g_pre": math.log(m[2019]) - math.log(m[2017]),
        "g_post_2425": math.log(m[2025]) - math.log(m[2024]),
        "g_pre_1819": math.log(m[2019]) - math.log(m[2018]),
        "g_1923": math.log(m[2023]) - math.log(m[2019]),
    }
    g["diff"] = g["g_post"] - g["g_pre"]
    g["diff_2425"] = g["g_post_2425"] - g["g_pre_1819"]
    g["diff_2425_regpre"] = g["g_post_2425"] - g["g_pre"]
    if latest_months is not None:
        g["g_latest"] = latest_12_growth(ym_map, latest_months)
        g["diff_latest"] = g["g_latest"] - g["g_pre"]
    return m, g


def compute(series_data, btos, seed=PERM_SEED, nperm=N_PERM, ncycles=N_CYCLES, ncycles_2023=N_CYCLES_2023):
    """Pure computation of all AJ1 version-2 primary and reported statistics. No files, no network."""
    sub_2425 = btos["sub_2425"]
    sec_2425 = btos["sec_2425"]
    sub_2023 = btos["sub_2023"]
    sec_2023 = btos["sec_2023"]

    kept, dropped = select_subsectors(sub_2425, ncycles)
    if sorted(kept, key=int) != sorted(CES_LABELLED, key=int):
        raise Refused("kept subsectors %s do not match spec version 2 list %s" % (kept, sorted(CES_LABELLED, key=int)))

    ces_labelled_maps = [series_data[CES_LABELLED[s]] for s in kept]
    ces_all_maps = ces_labelled_maps + [series_data[CES_REPORTED[k]] for k in sorted(CES_REPORTED, key=int)] + [series_data[CES_AUX["05"]]]
    ces_latest = common_latest_12(ces_all_maps)

    ces_stats = {}
    for s in kept:
        m, g = _series_growth(series_data[CES_LABELLED[s]], ces_latest)
        ces_stats[s] = {"means": m, "g": g, "ai": sub_2425[s]["mean"]}

    ces_rep_stats = {}
    rep_ai_src = {"513": "511", "519": "519", "523": "523"}
    for s, sid in CES_REPORTED.items():
        m, g = _series_growth(series_data[sid], ces_latest)
        bcode = rep_ai_src[s]
        ai_val = sub_2425[bcode]["mean"] if bcode in sub_2425 else None
        ces_rep_stats[s] = {"means": m, "g": g, "ai": ai_val}

    # Auxiliary CES series (05 total private, 55, 56)
    m_05, g_05 = _series_growth(series_data[CES_AUX["05"]], ces_latest)
    emp19_54 = annual_mean(series_data[CES_LABELLED["541"]], 2019)
    emp19_55 = annual_mean(series_data[CES_AUX["55"]], 2019)
    emp19_56 = annual_mean(series_data[CES_AUX["56"]], 2019)
    share_55 = emp19_55 / (emp19_54 + emp19_55 + emp19_56)

    for sec_needed in ("23", "31", "42", "44", "48", "51", "52", "53", "54", "56", "61", "62", "71", "72", "81"):
        if sec_needed not in sec_2425 or len(sec_2425[sec_needed]["used"]) < ncycles:
            raise Refused("BTOS sector %s missing or suppressed in 2024-25 cycles" % sec_needed)
    ai_54_56 = (sec_2425["54"]["mean"] * emp19_54 + sec_2425["56"]["mean"] * emp19_56) / (emp19_54 + emp19_56)

    jolts_all_maps = [series_data[JOLTS_SERIES[code]] for code, _n, _s in JOLTS_CODES]
    jolts_latest = common_latest_12(jolts_all_maps)
    jolts_stats = {}
    jolts_codes = [c for c, _n, _s in JOLTS_CODES]
    for code, name, sec_map in JOLTS_CODES:
        m, g = _series_growth(series_data[JOLTS_SERIES[code]], jolts_latest)
        ai_val = ai_54_56 if sec_map == "54+56" else sec_2425[sec_map]["mean"]
        jolts_stats[code] = {"name": name, "btos_sector": sec_map, "means": m, "g": g, "ai": ai_val}

    T = {}

    def run_ces(key, members, field, ai_map=None):
        amap = ai_map or {s: ces_stats[s]["ai"] for s in members}
        gmap = {s: (ces_stats[s]["g"] if s in ces_stats else ces_rep_stats[s]["g"]) for s in members}
        res = perm_test([amap[s] for s in members], [gmap[s][field] for s in members], seed, nperm)
        res["members"] = list(members)
        T[key] = res

    def run_jolts(key, members, field, ai_map=None):
        amap = ai_map or {c: jolts_stats[c]["ai"] for c in members}
        res = perm_test([amap[c] for c in members], [jolts_stats[c]["g"][field] for c in members], seed, nperm)
        res["members"] = list(members)
        T[key] = res

    # Primary labelled tests (version 2)
    run_ces("P1", kept, "g_post")
    run_ces("P2", kept, "diff")
    run_jolts("P3", jolts_codes, "g_post")
    for k in ("P1", "P2", "P3"):
        T[k]["label"] = label_perm(T[k])

    # Reported CES drop/add variants
    no_441_518 = [s for s in kept if s not in ("441", "518")]
    no_518_541 = [s for s in kept if s not in ("518", "541")]
    run_ces("P1_no441_518", no_441_518, "g_post")
    run_ces("P2_no441_518", no_441_518, "diff")
    run_ces("P1_no518_541", no_518_541, "g_post")
    run_ces("P2_no518_541", no_518_541, "diff")

    with_513_519 = sorted(kept + ["513", "519"], key=int)
    ai_with_513_519 = {s: (ces_stats[s]["ai"] if s in ces_stats else ces_rep_stats[s]["ai"]) for s in with_513_519}
    run_ces("P1_with_513_519", with_513_519, "g_post", ai_with_513_519)
    run_ces("P2_with_513_519", with_513_519, "diff", ai_with_513_519)

    # Reported CES alternative windows & 2019-23
    run_ces("P1_2425", kept, "g_post_2425")
    run_ces("P2_2425", kept, "diff_2425")
    run_ces("P2_2425_regpre", kept, "diff_2425_regpre")
    run_ces("P1_1923", kept, "g_1923")
    if ces_latest is not None:
        run_ces("P1_latest", kept, "g_latest")
        run_ces("P2_latest", kept, "diff_latest")

    # Reported 2023-cycle AI means (subsectors/sectors with all 8 cycles published)
    kept_23 = [s for s in kept if s in sub_2023 and len(sub_2023[s]["used"]) == ncycles_2023]
    if len(kept_23) >= 4:
        ai23_sub = {s: sub_2023[s]["mean"] for s in kept_23}
        run_ces("P1_2023ai", kept_23, "g_post", ai23_sub)
        run_ces("P2_2023ai", kept_23, "diff", ai23_sub)

    # Reported JOLTS variants
    jolts_no52 = [c for c in jolts_codes if c != "520000"]
    jolts_no540099 = [c for c in jolts_codes if c != "540099"]
    jolts_no52_540099 = [c for c in jolts_codes if c not in ("520000", "540099")]
    run_jolts("P3_no52", jolts_no52, "g_post")
    run_jolts("P3_no540099", jolts_no540099, "g_post")
    run_jolts("P3_no52_540099", jolts_no52_540099, "g_post")
    run_jolts("P3_diff", jolts_codes, "diff")
    run_jolts("P3_2425", jolts_codes, "g_post_2425")
    run_jolts("P3_1923", jolts_codes, "g_1923")
    if jolts_latest is not None:
        run_jolts("P3_latest", jolts_codes, "g_latest")

    # JOLTS with 2023-cycle AI means
    jolts_23_ai = {}
    for code, _n, sec_map in JOLTS_CODES:
        if sec_map == "54+56":
            ok54 = "54" in sec_2023 and len(sec_2023["54"]["used"]) == ncycles_2023
            ok56 = "56" in sec_2023 and len(sec_2023["56"]["used"]) == ncycles_2023
            if ok54 and ok56:
                jolts_23_ai[code] = (sec_2023["54"]["mean"] * emp19_54 + sec_2023["56"]["mean"] * emp19_56) / (emp19_54 + emp19_56)
        elif sec_map in sec_2023 and len(sec_2023[sec_map]["used"]) == ncycles_2023:
            jolts_23_ai[code] = sec_2023[sec_map]["mean"]
    jolts_23_members = [c for c in jolts_codes if c in jolts_23_ai]
    if len(jolts_23_members) >= 4:
        run_jolts("P3_2023ai", jolts_23_members, "g_post", jolts_23_ai)

    for k in T:
        if "label" not in T[k]:
            T[k]["label_if_it_were_primary"] = label_perm(T[k])

    # Weighted Pearson (reported, not labelled): weights = 2019 annual mean CES employment
    w19 = [ces_stats[s]["means"][2019] for s in kept]
    ai_19 = [ces_stats[s]["ai"] for s in kept]
    weighted = {
        "n": len(kept),
        "members": list(kept),
        "weights_total": sum(w19),
        "P1": weighted_pearson(ai_19, [ces_stats[s]["g"]["g_post"] for s in kept], w19),
        "P2": weighted_pearson(ai_19, [ces_stats[s]["g"]["diff"] for s in kept], w19),
    }

    return {
        "kept": kept,
        "dropped": dropped,
        "jolts_codes": jolts_codes,
        "ces": ces_stats,
        "ces_reported": ces_rep_stats,
        "jolts": jolts_stats,
        "national": {"means": m_05, "g": g_05},
        "weights": {"emp19_54": emp19_54, "emp19_55": emp19_55, "emp19_56": emp19_56, "share_55": share_55, "ai_54_56": ai_54_56},
        "ces_latest": ces_latest,
        "jolts_latest": jolts_latest,
        "tests": T,
        "weighted": weighted,
        "ncycles": ncycles,
        "ncycles_2023": ncycles_2023,
        "sub_2023": sub_2023,
        "sec_2023": sec_2023,
        "seed": seed,
        "nperm": nperm,
    }


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
    """Parse the version-2 Statements table (after '**Statements (version 2).**')."""
    marker = text.find("**Statements (version 2).**")
    if marker < 0:
        raise Refused("the spec has no 'Statements (version 2)' section")
    rows = {}
    for line in text[marker:].splitlines():
        m = re.match(r"^\|\s*(AJ1-P[0-9][^|]*)\|(.*)\|\s*$", line)
        if not m:
            continue
        cells = [c.strip().replace("**", "") for c in m.group(2).split("|")]
        if len(cells) != 4:
            raise Refused("version 2 table row %s does not have four cells" % m.group(1).strip())
        rows[m.group(1).strip()] = tuple(cells)
    need = list(IDS)
    if sorted(rows) != sorted(need):
        raise Refused("the version 2 table does not hold %s: %s" % (need, sorted(rows)))
    p1 = rows["AJ1-P1"]
    out = {"AJ1-P1": p1}
    for sid in ("AJ1-P2", "AJ1-P3"):
        st, stat, sup, ag = rows[sid]
        sup_full = ("%s (AJ1-P1's rule: %s)" % (sup, p1[2])) if sup.lower() == "same rule" else sup
        ag_full = ("%s (AJ1-P1's rule: %s)" % (ag, p1[3])) if ag.lower() == "same rule" else ag
        out[sid] = (st, stat, sup_full, ag_full)
    return out


WINDOWS = {
    "AJ1-P1": ("Jan-Dec 2023 to Jan-Dec 2025", "none"),
    "AJ1-P2": ("Jan-Dec 2023 to Jan-Dec 2025", "Jan-Dec 2017 to Jan-Dec 2019"),
    "AJ1-P3": ("Jan-Dec 2023 to Jan-Dec 2025", "none"),
}


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
    return "%.5f" % p


def test_stats(t):
    se = mc_se_at(ALPHA, t["nperm"])
    return "perm_p_pos=%s; perm_p_neg=%s; loo_min=%s; loo_max=%s; permutations=%d; seed=%d; mc_se_at_0.05=%.6f" % (
        pstr(t["p_pos"]), pstr(t["p_neg"]), f4(t["loo_min"]), f4(t["loo_max"]), t["nperm"], t["seed"], se
    )


def make_rows(R):
    T, kept = R["tests"], R["kept"]
    scores = []
    caveat = (
        "SUPPORT or AGAINST names only the cross-industry pattern, never that AI caused it (rates, the end of the post-pandemic hiring boom, "
        "software-sector cycles, or fast-growing industries adopting AI can rank industries similarly). Neither label measures the economy-wide net; "
        "BTOS measures AI use by existing employers in a suppression-selected set of industries; three statements, no multiplicity adjustment."
    )
    spec_rows = (
        ("AJ1-P1", "P1", "spearman_AI_use_vs_g_post_CES_employment", "19 CES 3-digit subsectors (2017-25, 12 months/yr)"),
        ("AJ1-P2", "P2", "spearman_AI_use_vs_g_post_minus_g_pre_CES_employment", "19 CES 3-digit subsectors (2023-25 vs 2017-19, 12 months/yr)"),
        ("AJ1-P3", "P3", "spearman_AI_use_vs_g_post_JOLTS_openings_level", "15 JOLTS private child industries (2023-25, 12 months/yr)"),
    )
    for sid, key, stat, desc in spec_rows:
        t = T[key]
        den = "n=%d; members=%s; %s; permutations=%d; seed=%d" % (t["n"], ",".join(t["members"]), desc, R["nperm"], R["seed"])
        scores.append([sid, t["label"], stat, f4(t["rho"]), "rank correlation", test_stats(t), den, caveat])

    detail = []
    d = detail.append
    d(["AJ1-SEC", "ces_release_note", R.get("ces_release", "not stated"), "text"])
    d(["AJ1-SEC", "jolts_release_note", R.get("jolts_release", "not stated"), "text"])
    d(["AJ1-SEC", "btos_cycles_required_2024_2025", str(R["ncycles"]), "cycles"])
    d(["AJ1-SEC", "btos_cycles_required_2023", str(R["ncycles_2023"]), "cycles"])
    d(["AJ1-SEC", "subsectors_kept", str(len(kept)), "subsectors"])
    d(["AJ1-SEC", "subsectors_dropped", str(len(R["dropped"])), "subsectors"])
    d(["AJ1-SEC", "kept_subsectors_list", ",".join(kept), "list"])
    d(["AJ1-SEC", "jolts_industries_count", str(len(R["jolts_codes"])), "industries"])
    d(["AJ1-SEC", "jolts_industries_list", ",".join(R["jolts_codes"]), "list"])
    if R["ces_latest"] is not None:
        d(["AJ1-SEC", "ces_latest_12_months_span", format_ym_span(R["ces_latest"]), "YYYY-MM"])
    if R["jolts_latest"] is not None:
        d(["AJ1-SEC", "jolts_latest_12_months_span", format_ym_span(R["jolts_latest"]), "YYYY-MM"])
    for s, reason in R["dropped"]:
        d(["AJ1-SEC", "dropped_subsector_%s" % s, reason, "text"])

    w = R["weights"]
    d(["AJ1-SEC", "ces_2019_emp_sector_54", "%.2f" % w["emp19_54"], "thousands"])
    d(["AJ1-SEC", "ces_2019_emp_sector_55", "%.2f" % w["emp19_55"], "thousands"])
    d(["AJ1-SEC", "ces_2019_emp_sector_56", "%.2f" % w["emp19_56"], "thousands"])
    d(["AJ1-SEC", "sector_55_share_of_54_55_56_emp_2019", "%.6f" % w["share_55"], "share"])
    d(["AJ1-SEC", "jolts_540099_weighted_ai_mean_pct", "%.4f" % w["ai_54_56"], "percent of firms"])
    d(["AJ1-SEC", "utilities_22_share_of_48_49_22_emp_2019", "not fetched (no CES 22 or 48-49 series in spec 40-series list)", "note"])

    se = mc_se_at(ALPHA, R["nperm"])
    for key in ("P1", "P2", "P3"):
        t = T[key]
        sid = "AJ1-" + key
        within_pos = abs(t["p_pos"] - ALPHA) <= 2.0 * se
        within_neg = abs(t["p_neg"] - ALPHA) <= 2.0 * se
        for item, val, unit in (
            ("rho", f4(t["rho"]), "rank correlation"),
            ("perm_p_pos", pstr(t["p_pos"]), "probability"),
            ("perm_p_neg", pstr(t["p_neg"]), "probability"),
            ("loo_min", f4(t["loo_min"]), "rank correlation"),
            ("loo_max", f4(t["loo_max"]), "rank correlation"),
            ("loo_undefined", str(t["loo_undefined"]), "count"),
            ("n", str(t["n"]), "industries"),
            ("members", ",".join(t["members"]), "list"),
            ("permutations", str(t["nperm"]), "count"),
            ("seed", str(t["seed"]), "integer"),
            ("mc_se_at_0.05", "%.6f" % se, "probability"),
            ("within_2_mc_se_of_0.05", "pos=%s;neg=%s" % (within_pos, within_neg), "boolean"),
        ):
            d([sid, item, val, unit])
        for i, r in t["loo"]:
            d([sid, "loo_without_%s" % t["members"][i], f4(r), "rank correlation"])

    # Per-subsector table (19 labelled + 3 reported-only)
    for s in kept:
        st = R["ces"][s]
        d(["AJ1-TABLE", "ces_%s_ai_mean_2024_2025_pct" % s, "%.4f" % st["ai"], "percent of firms"])
        if s in R["sub_2023"] and len(R["sub_2023"][s]["used"]) == R["cycles_2023" if "cycles_2023" in R else "ncycles_2023"]:
            d(["AJ1-TABLE", "ces_%s_ai_mean_2023_pct" % s, "%.4f" % R["sub_2023"][s]["mean"], "percent of firms"])
        for y in ALL_YEARS:
            d(["AJ1-TABLE", "ces_%s_mean_%d" % (s, y), "%.2f" % st["means"][y], "thousands"])
        for k in ("g_pre", "g_post", "diff", "g_1923", "g_post_2425", "g_pre_1819"):
            d(["AJ1-TABLE", "ces_%s_%s" % (s, k), "%.6f" % st["g"][k], "log points"])
        if "g_latest" in st["g"]:
            d(["AJ1-TABLE", "ces_%s_g_latest" % s, "%.6f" % st["g"]["g_latest"], "log points"])
    for s in sorted(R["ces_reported"], key=int):
        st = R["ces_reported"][s]
        if st["ai"] is not None:
            d(["AJ1-TABLE", "ces_reported_%s_ai_mean_2024_2025_pct" % s, "%.4f" % st["ai"], "percent of firms"])
        for y in ALL_YEARS:
            d(["AJ1-TABLE", "ces_reported_%s_mean_%d" % (s, y), "%.2f" % st["means"][y], "thousands"])
        for k in ("g_pre", "g_post", "diff", "g_1923", "g_post_2425"):
            d(["AJ1-TABLE", "ces_reported_%s_%s" % (s, k), "%.6f" % st["g"][k], "log points"])

    # Per-JOLTS-industry table
    for code in R["jolts_codes"]:
        jt = R["jolts"][code]
        d(["AJ1-TABLE", "jolts_%s_ai_mean_2024_2025_pct" % code, "%.4f" % jt["ai"], "percent of firms"])
        for y in ALL_YEARS:
            d(["AJ1-TABLE", "jolts_%s_mean_%d" % (code, y), "%.2f" % jt["means"][y], "thousands"])
        for k in ("g_pre", "g_post", "diff", "g_1923", "g_post_2425"):
            d(["AJ1-TABLE", "jolts_%s_%s" % (code, k), "%.6f" % jt["g"][k], "log points"])
        if "g_latest" in jt["g"]:
            d(["AJ1-TABLE", "jolts_%s_g_latest" % code, "%.6f" % jt["g"]["g_latest"], "log points"])

    # Reported variants (every statistic row carries n and members)
    for key in sorted(k for k in T if "label" not in T[k]):
        t = T[key]
        sid = "AJ1-R-" + key
        for item, val, unit in (
            ("rho", f4(t["rho"]), "rank correlation"),
            ("perm_p_pos", pstr(t["p_pos"]), "probability"),
            ("perm_p_neg", pstr(t["p_neg"]), "probability"),
            ("loo_min", f4(t["loo_min"]), "rank correlation"),
            ("loo_max", f4(t["loo_max"]), "rank correlation"),
            ("n", str(t["n"]), "industries"),
            ("members", ",".join(t["members"]), "list"),
            ("label_if_it_were_primary_not_used", t["label_if_it_were_primary"], "text"),
        ):
            d([sid, item, val, unit])

    wp = R["weighted"]
    d(["AJ1-R-WEIGHTED", "pearson_weighted_AI_vs_g_post_CES", f4(wp["P1"]), "correlation"])
    d(["AJ1-R-WEIGHTED", "pearson_weighted_AI_vs_g_post_minus_g_pre_CES", f4(wp["P2"]), "correlation"])
    d(["AJ1-R-WEIGHTED", "weights_total_2019_emp", "%.2f" % wp["weights_total"], "thousands"])
    d(["AJ1-R-WEIGHTED", "n", str(wp["n"]), "subsectors"])
    d(["AJ1-R-WEIGHTED", "members", ",".join(wp["members"]), "list"])

    nat = R["national"]
    d(["AJ1-R-NATIONAL", "n", "1", "series"])
    d(["AJ1-R-NATIONAL", "members", CES_AUX["05"], "series"])
    for y in ALL_YEARS:
        d(["AJ1-R-NATIONAL", "ces_private_mean_%d" % y, "%.2f" % nat["means"][y], "thousands"])
    for k in ("g_pre", "g_post", "diff", "g_1923", "g_post_2425"):
        d(["AJ1-R-NATIONAL", "ces_private_%s" % k, "%.6f" % nat["g"][k], "log points"])
    if "g_latest" in nat["g"]:
        d(["AJ1-R-NATIONAL", "ces_private_g_latest", "%.6f" % nat["g"]["g_latest"], "log points"])
    return scores, detail


def vintage_rows(cache):
    rows = []
    last = {}
    for r in read_manifest(cache):
        last[r["key"]] = r
    for key, _rel, batch_ids in BATCHES:
        r = last.get(key)
        if r is None:
            raise Refused("manifest has no row for %s: run fetch" % key)
        rows.append(["bls-api-v1", key, BLS_URL, r["fetched_utc"], r["status"], r["bytes"], r["sha256"],
                     "BLS Public Data API v1 POST (%d series, 2017-2026)" % len(batch_ids)])
    bp = os.path.join(cv1.cache_dir(), *cv1.BTOS_REL.split("/"))
    rows.append(["census-btos", "btos-ai-core-questions", cv1.BTOS_URL, "2026-11-15", "hand download",
                 os.path.getsize(bp) if os.path.exists(bp) else 0, cv1.BTOS_SHA256,
                 "AI Core Questions (Original), hash-pinned in bin/cv1_confidence_velocity.py; read through its code, never fetched here"])
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
def readme_text(R, sha):
    T, kept = R["tests"], R["kept"]
    L = []
    a = L.append
    a("# AJ1: does AI create more jobs than it displaces? (build of 16 Nov 2026)")
    a("")
    a("## What was asked")
    a("")
    a("Since 2023, have industries that use more AI gained or lost employment and job openings, compared with other industries "
      "and with their own 2017-19 trend? Registered blind before any employment or job-openings figure by industry was read "
      "(`%s`, version 2, sha256 `%s`)." % (SPEC_FILE, sha))
    a("")
    a("## Result table")
    a("")
    a("| statement | label | n | rank correlation | p (positive) | p (negative) | leave-one-out range |")
    a("|---|---|---|---|---|---|---|")
    for sid, key, title in (
        ("AJ1-P1", "P1", "P1: AI use vs CES employment growth 2023-25"),
        ("AJ1-P2", "P2", "P2: AI use vs CES growth 2023-25 minus 2017-19"),
        ("AJ1-P3", "P3", "P3: AI use vs JOLTS openings level growth 2023-25"),
    ):
        t = T[key]
        a("| %s (%s) | %s | %d | %s | %s | %s | %s to %s |" % (
            sid, title, t["label"], t["n"], f4(t["rho"]), pstr(t["p_pos"]), pstr(t["p_neg"]), f4(t["loo_min"]), f4(t["loo_max"])
        ))
    a("")
    a("Rule (version 2): SUPPORT if one-sided permutation p <= 0.05 (positive) and outside two Monte Carlo standard errors of 0.05, "
      "and every leave-one-out rho > 0; AGAINST if one-sided permutation p <= 0.05 (negative) and outside two Monte Carlo standard errors of 0.05, "
      "and every leave-one-out rho < 0; otherwise INCONCLUSIVE. %d permutations of the AI values, seed %d, p = (1 + k) / (%d + 1)." % (
          R["nperm"], R["seed"], R["nperm"]
      ))
    a("")
    a("## Asymmetry and limits")
    a("")
    a("- **Neither label identifies AI as the cause.** Labels name the cross-industry pattern, never the cause: rates, the end of the post-pandemic hiring boom, "
      "software-sector cycles, or fast-growing industries adopting AI because they are growing can rank industries similarly.")
    a("- **Neither label measures the economy-wide net.** Jobs AI creates in other industries (data-centre construction, power, chips) and displaced workers hired elsewhere "
      "are outside an industry cross-section.")
    a("- **BTOS series and coverage.** The BTOS series is the original wording (`AI Core Questions (Original)`), cycles 2024-2025 (46 cycles ending before 17 Nov 2025). "
      "BTOS measures AI use by existing employers, and this test is a rank association among firm-weighted AI rates in a suppression-selected set of industries.")
    a("- **Multiplicity.** Three statements are scored with no multiplicity adjustment.")
    a("- **Release dates:** CES: %s; JOLTS: %s." % (R.get("ces_release", "not stated"), R.get("jolts_release", "not stated")))
    a("")
    a("## Denominators and weights")
    a("")
    a("- **CES labelled subsectors (n=%d):** %s." % (len(kept), ", ".join(kept)))
    a("- **CES dropped subsectors (n=%d):** %s." % (len(R["dropped"]), "; ".join("%s (%s)" % (s, r) for s, r in R["dropped"])))
    a("- **JOLTS private child industries (n=%d):** %s." % (len(R["jolts_codes"]), ", ".join(R["jolts_codes"])))
    a("- **Sector 55 share of 54+55+56 2019 CES employment:** %.2f%%. **Utilities (22) 2019 share:** not fetched (no CES 22 or 48-49 series in spec's 40-series list)." % (100.0 * R["weights"]["share_55"]))
    a("- **National CES private employment (`CEU0500000001`):** g_post (2023-25) = %.4f, g_pre (2017-19) = %.4f, diff = %.4f, g_1923 = %.4f." % (
        R["national"]["g"]["g_post"], R["national"]["g"]["g_pre"], R["national"]["g"]["diff"], R["national"]["g"]["g_1923"]
    ))
    a("- **Weighted Pearson (2019 CES employment weights, n=%d):** P1 = %s, P2 = %s." % (
        R["weighted"]["n"], f4(R["weighted"]["P1"]), f4(R["weighted"]["P2"])
    ))
    a("")
    a("## Files")
    a("")
    a("`registered.csv` (written before any statistic), `scores.csv`, `detail.csv`, `vintages.csv`, `README.md`. Raw JSON replies stay in `%s` (gitignored)." % CACHE_REL)
    a("")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------------------------------
# build
# ------------------------------------------------------------------------------------------------------------------------
def load_cached_bls(root=None):
    cache = cache_dir(root)
    stop_path = os.path.join(cache, "STOP.txt")
    if os.path.exists(stop_path):
        raise Refused("STOP.txt present in %s; resolve before building" % CACHE_REL)
    series_data = {}
    notes = {}
    for key, rel, batch_ids in BATCHES:
        p = os.path.join(cache, *rel.split("/"))
        if not os.path.exists(p):
            raise Refused("missing cached BLS JSON %s (run fetch)" % rel)
        smap, note = parse_bls_json(open(p, "rb").read())
        for sid in batch_ids:
            if sid not in smap or not smap[sid]:
                raise Refused("series %s missing or empty in %s" % (sid, rel))
        series_data.update(smap)
        notes[key] = note
    return series_data, notes


def run_build(root=None, out=None):
    root = root or ROOT
    out = out or out_dir(root)
    cache = cache_dir(root)
    reg_path, sha = write_registered(out, root)                                   # first: before any statistic exists
    reg_sha = sha256_of(open(reg_path, "rb").read())
    print("registered.csv written (spec sha256 %s; file sha256 %s)" % (sha, reg_sha), flush=True)
    series_data, notes = load_cached_bls(root)
    btos = load_btos_inputs(root)
    R = compute(series_data, btos)
    R["ces_release"] = notes.get("bls-ces", "not stated")
    R["jolts_release"] = notes.get("bls-jolts", "not stated")
    scores, detail = make_rows(R)
    vint = vintage_rows(cache)
    src = "bin/aj1_ai_jobs.py build; scores computed after registered.csv (sha256 %s) was written; spec %s sha256 %s; permutations %d seed %d" % (
        reg_sha, SPEC_FILE, sha, R["nperm"], R["seed"]
    )
    files = {
        "scores.csv": table_text(src, SCORES_HEADER, scores),
        "detail.csv": table_text(src, DETAIL_HEADER, detail),
        "vintages.csv": table_text("fetch manifest of the raw cache (%s); raw files are not committed" % CACHE_REL, VINTAGES_HEADER, vint),
        "README.md": readme_text(R, sha),
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
class _FakeResp(object):
    def __init__(self, status, body):
        self.status = status
        self._body = body
        self.headers = {"Content-Type": "application/json"}

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class _FakeBlsFetcher(object):
    def __init__(self, handler):
        self.handler = handler
        self.calls = []

    def post(self, url, body_bytes, headers):
        self.calls.append((url, json.loads(body_bytes.decode("utf-8")), headers))
        return self.handler(len(self.calls) - 1, url, json.loads(body_bytes.decode("utf-8")), headers)


def _synth_bls_reply(series_ids, growth_by_sid=None, include_m13=True, message=None, status="REQUEST_SUCCEEDED", empty_sid=None):
    growth_by_sid = growth_by_sid or {}
    out = []
    for i, sid in enumerate(series_ids):
        if sid == empty_sid:
            out.append({"seriesID": sid, "data": []})
            continue
        g = growth_by_sid.get(sid, 0.01 * (i + 1))
        rows = []
        for y in (2017, 2018, 2019, 2023, 2024, 2025):
            lvl = 100.0 * (1.0 if y <= 2019 else math.exp(g * (y - 2022) / 3.0))
            for m in range(1, 13):
                rows.append({"year": str(y), "period": "M%02d" % m, "value": "%.3f" % (lvl + 0.1 * m), "footnotes": []})
            if include_m13:
                rows.append({"year": str(y), "period": "M13", "value": "999999.0", "footnotes": []})
        out.append({"seriesID": sid, "data": rows})
    return 200, json.dumps({"status": status, "message": message or [], "Results": {"series": out}}).encode("utf-8"), {}


def _synth_btos():
    sub_vals = {
        "238": 2.4, "423": 3.9, "424": 3.5, "441": 4.2, "454": 10.0, "511": 21.0, "512": 12.0,
        "518": 25.0, "519": 18.0, "522": 9.5, "523": 14.0, "524": 8.0, "531": 9.4, "541": 16.2,
        "561": 6.1, "611": 12.2, "621": 7.0, "624": 5.0, "711": 6.5, "713": 4.0, "722": 1.9,
        "811": 3.1, "812": 2.8,
    }
    sec_vals = {
        "23": 2.4, "31": 3.3, "42": 3.9, "44": 4.2, "48": 2.1, "51": 20.9, "52": 9.6,
        "53": 9.4, "54": 16.2, "56": 6.1, "61": 12.2, "62": 7.0, "71": 6.5, "72": 1.9, "81": 3.1,
    }
    sub_2425 = {s: {"mean": v, "used": ["x"] * N_CYCLES} for s, v in sub_vals.items()}
    sub_2425["111"] = {"mean": 1.0, "used": ["x"] * 5}  # suppressed -> dropped
    sec_2425 = {s: {"mean": v, "used": ["x"] * N_CYCLES} for s, v in sec_vals.items()}
    sub_2023 = {s: {"mean": v * 0.8, "used": ["x"] * N_CYCLES_2023} for s, v in sub_vals.items()}
    sec_2023 = {s: {"mean": v * 0.8, "used": ["x"] * N_CYCLES_2023} for s, v in sec_vals.items()}
    return {"sub_2425": sub_2425, "sec_2425": sec_2425, "sub_2023": sub_2023, "sec_2023": sec_2023}


def selftest():
    ck = Checks()
    # 1. Spec hash & version-2 table parsing
    spec_bytes = spec_text()
    ck.eq("spec: file on disk hashes to pinned sha256", sha256_of(spec_bytes), SPEC_SHA256)
    rows = parse_spec_v2(spec_bytes.decode("utf-8"))
    ck.eq("spec: 3 registered statements parsed from version-2 table", sorted(rows), sorted(IDS))
    ck.raises("spec: tampered hash refused", Refused, lambda: check_spec_hash(pinned="0" * 64))
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "_research"))
        with open(os.path.join(td, *SPEC_FILE.split("/")), "wb") as fh:
            fh.write(spec_bytes + b"\ntamper\n")
        ck.raises("spec: tampered file stops write_registered", Refused, lambda: write_registered(os.path.join(td, "out"), root=td))
        ck.ok("spec: nothing written when refused", not os.path.exists(os.path.join(td, "out", "registered.csv")))

    # 2. Fetcher: 2 POSTs, <=25 series, UA, 3s sleep, no refetch, STOP conditions
    with tempfile.TemporaryDirectory() as td:
        slept = []
        ff = _FakeBlsFetcher(lambda idx, url, body, hdrs: _synth_bls_reply(body["seriesid"]))
        cmd_fetch(td, fetcher=ff, sleep=slept.append)
        ck.eq("fetch: 2 POSTs made (25 CES + 15 JOLTS = 40 series)", [len(c[1]["seriesid"]) for c in ff.calls], [25, 15])
        ck.eq("fetch: User-Agent is exact house string", ff.calls[0][2]["User-Agent"], UA)
        ck.eq("fetch: 3.0s sleep between POSTs", slept, [3.0])
        ck.ok("fetch: no API key in POST body", "registrationkey" not in ff.calls[0][1] and "api_key" not in ff.calls[0][1])
        ck.ok("fetch: manifest.csv written", os.path.exists(os.path.join(cache_dir(td), "manifest.csv")))
        ck.raises("fetch: refuses to refetch if raw files already exist", Refused, lambda: cmd_fetch(td, fetcher=ff, sleep=slept.append))

    # STOP on HTTP != 200
    with tempfile.TemporaryDirectory() as td:
        ff = _FakeBlsFetcher(lambda idx, url, body, hdrs: (429, b"rate limited", {}))
        ck.raises("fetch STOP: HTTP 429 writes STOP.txt", Stop, lambda: cmd_fetch(td, fetcher=ff, sleep=lambda s: None))
        ck.ok("fetch STOP: STOP.txt created on HTTP 429", os.path.exists(os.path.join(cache_dir(td), "STOP.txt")))
        ck.raises("fetch STOP: existing STOP.txt blocks subsequent run", Stop, lambda: cmd_fetch(td, fetcher=ff, sleep=lambda s: None))

    # STOP on status != REQUEST_SUCCEEDED
    with tempfile.TemporaryDirectory() as td:
        ff = _FakeBlsFetcher(lambda idx, url, body, hdrs: _synth_bls_reply(body["seriesid"], status="REQUEST_FAILED"))
        ck.raises("fetch STOP: non-REQUEST_SUCCEEDED stops", Stop, lambda: cmd_fetch(td, fetcher=ff, sleep=lambda s: None))

    # STOP on message containing does not exist / threshold / limit
    for kw in ("Series does not exist", "Daily threshold reached", "Request limit exceeded"):
        with tempfile.TemporaryDirectory() as td:
            ff = _FakeBlsFetcher(lambda idx, url, body, hdrs, k=kw: _synth_bls_reply(body["seriesid"], message=[k]))
            ck.raises("fetch STOP: message %r stops" % kw, Stop, lambda: cmd_fetch(td, fetcher=ff, sleep=lambda s: None))

    # STOP on empty series data
    with tempfile.TemporaryDirectory() as td:
        ff = _FakeBlsFetcher(lambda idx, url, body, hdrs: _synth_bls_reply(body["seriesid"], empty_sid=body["seriesid"][0]))
        ck.raises("fetch STOP: empty series data stops", Stop, lambda: cmd_fetch(td, fetcher=ff, sleep=lambda s: None))

    # 3. M13 dropped & annual mean requires 12 months
    raw = _synth_bls_reply(["CEU2023800001"], include_m13=True)[1]
    smap, rel = parse_bls_json(raw)
    ck.eq("M13 dropped and release defaults to 'not stated'", (len(smap["CEU2023800001"]), rel), (72, "not stated"))
    ck.ok("annual_mean ignores M13 (999999.0)", annual_mean(smap["CEU2023800001"], 2025) < 500.0)
    bad_ym = dict(smap["CEU2023800001"])
    del bad_ym[(2025, 12)]
    ck.raises("annual_mean refuses year with 11 months", Refused, lambda: annual_mean(bad_ym, 2025))

    # 4. Version-2 label rules (symmetric LOO + 2 MC SE band around 0.05)
    se = mc_se_at(0.05, 100000)
    base = dict(rho=0.6, p_pos=0.001, p_neg=0.999, loo=[], n=19, loo_min=0.4, loo_max=0.7, loo_undefined=0, nperm=100000, seed=PERM_SEED)
    ck.eq("label v2: clean positive is SUPPORT", label_perm(base), "SUPPORT")
    ck.eq("label v2: clean negative with all LOO < 0 is AGAINST", label_perm(dict(base, rho=-0.6, p_pos=0.999, p_neg=0.001, loo_min=-0.7, loo_max=-0.4)), "AGAINST")
    ck.eq("label v2: negative p<=0.05 but LOO max >= 0 is INCONCLUSIVE", label_perm(dict(base, rho=-0.6, p_pos=0.999, p_neg=0.001, loo_min=-0.7, loo_max=0.01)), "INCONCLUSIVE")
    ck.eq("label v2: p within 2 MC SE of 0.05 (0.0495) is INCONCLUSIVE", label_perm(dict(base, p_pos=0.05 - 0.5 * se)), "INCONCLUSIVE")
    ck.eq("label v2: p outside 2 MC SE below 0.05 is SUPPORT", label_perm(dict(base, p_pos=0.05 - 2.5 * se)), "SUPPORT")

    # 5. End-to-end compute & output generation with synthetic monotone data
    btos = _synth_btos()
    g_map = {}
    for s, sid in CES_LABELLED.items():
        g_map[sid] = 0.01 * btos["sub_2425"][s]["mean"]
    for s, sid in CES_REPORTED.items():
        g_map[sid] = 0.02
    for s, sid in CES_AUX.items():
        g_map[sid] = 0.03
    for code, _n, sec_map in JOLTS_CODES:
        ai_v = 12.0 if sec_map == "54+56" else btos["sec_2425"][sec_map]["mean"]
        g_map[JOLTS_SERIES[code]] = 0.01 * ai_v
    sdata = {}
    for _k, _rel, bids in BATCHES:
        _, b, _ = _synth_bls_reply(bids, growth_by_sid=g_map)
        parsed, _ = parse_bls_json(b)
        sdata.update(parsed)

    R = compute(sdata, btos, seed=PERM_SEED, nperm=1000)
    ck.eq("end-to-end: 19 CES kept, 5 dropped (111, 454, 511, 519, 523)", (len(R["kept"]), [s for s, _ in R["dropped"]]), (19, ["111", "454", "511", "519", "523"]))
    ck.near("end-to-end: P1 rho is 1.0", R["tests"]["P1"]["rho"], 1.0)
    ck.near("end-to-end: P2 rho is 1.0 (g_pre=0)", R["tests"]["P2"]["rho"], 1.0)
    ck.near("end-to-end: P3 rho is 1.0 (15 JOLTS)", R["tests"]["P3"]["rho"], 1.0)
    ck.eq("end-to-end: all 3 primary labels SUPPORT", (R["tests"]["P1"]["label"], R["tests"]["P2"]["label"], R["tests"]["P3"]["label"]), ("SUPPORT", "SUPPORT", "SUPPORT"))
    ck.eq("end-to-end: reported drop variants have n=17", (R["tests"]["P1_no441_518"]["n"], R["tests"]["P1_no518_541"]["n"]), (17, 17))
    ck.eq("end-to-end: P3_no52 has n=14, P3_no52_540099 has n=13", (R["tests"]["P3_no52"]["n"], R["tests"]["P3_no52_540099"]["n"]), (14, 13))
    ck.ok("end-to-end: 2023-cycle AI variants present", "P1_2023ai" in R["tests"] and "P3_2023ai" in R["tests"])
    scores, detail = make_rows(R)
    ck.eq("end-to-end: 3 score rows", len(scores), 3)
    ck.ok("end-to-end: every score row carries n= and members=", all("n=" in r[6] and "members=" in r[6] for r in scores))
    ck.raises("no_leak: at sign refused", Refused, lambda: no_leak("x", "a@b"))
    ck.raises("no_leak: /Users/ refused", Refused, lambda: no_leak("x", "/Users/foo"))
    with tempfile.TemporaryDirectory() as td:
        out_td = os.path.join(td, "out")
        reg_p, sha = write_registered(out_td)
        rd_txt = readme_text(R, sha)
        for name, txt in (
            ("scores.csv", table_text("selftest", SCORES_HEADER, scores)),
            ("detail.csv", table_text("selftest", DETAIL_HEADER, detail)),
            ("README.md", rd_txt),
        ):
            no_leak(name, txt)
            write_text(os.path.join(out_td, name), txt)
        ck.ok("build outputs: registered.csv, scores.csv, detail.csv, README.md written", all(os.path.exists(os.path.join(out_td, n)) for n in ("registered.csv", "scores.csv", "detail.csv", "README.md")))
        ck.ok("README: states asymmetry and BTOS original wording 2024-2025", "Neither label identifies AI as the cause" in rd_txt and "Neither label measures the economy-wide net" in rd_txt and "original wording" in rd_txt and "2024-2025" in rd_txt)

    bad = [(n, d) for n, c, d in ck.items if not c]
    for n, c, d in ck.items:
        print(("ok   " if c else "FAIL ") + n + ("" if c else "  <- " + d))
    print("%d checks, %d failed" % (len(ck.items), len(bad)))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="AJ1 AI-use vs employment & job openings scorer (spec version 2)")
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
