#!/usr/bin/env python3
"""AP1: is AI raising productivity and profit margins where it is used?
Registered statements AP1-P1, AP1-P2, AP1-P3, AP1-P4 (version 2 of the spec).

  python3 bin/ap1_ai_productivity.py selftest           # synthetic data only; no network
  python3 bin/ap1_ai_productivity.py fetch              # plain HTTPS GET from apps.bea.gov (3 s apart)
  python3 bin/ap1_ai_productivity.py build [--out DIR]  # offline; writes registered.csv FIRST, then scores

Specification: _research/2026-11-16-AP1-AI-Productivity-Spec.md ("Version 2" governs; its sha256 is pinned in
SPEC_SHA256 below and the build refuses to score if the file differs).
Outputs: data/ap1_ai_productivity/ (registered.csv, scores.csv, detail.csv, vintages.csv, README.md).
Raw downloads: data/vintages/ap1/ (gitignored, never committed).
BTOS inputs and permutation/correlation helpers are imported from bin/aj1_ai_jobs.py (not copied).
"""
import argparse
import csv
import math
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aj1_ai_jobs as aj1  # noqa: E402

load_btos_inputs = aj1.load_btos_inputs
perm_test = aj1.perm_test
label_perm = aj1.label_perm
mc_se_at = aj1.mc_se_at
weighted_pearson = aj1.weighted_pearson
spearman = aj1.spearman

Refused = aj1.Refused
Stop = aj1.Stop
Checks = aj1.Checks
sha256_of = aj1.sha256_of
now_utc = aj1.now_utc
write_text = aj1.write_text
write_bytes = aj1.write_bytes
csv_line = aj1.csv_line
read_manifest = aj1.read_manifest
no_leak = aj1.no_leak
table_text = aj1.table_text
f4 = aj1.f4
pstr = aj1.pstr
test_stats = aj1.test_stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_FILE = "_research/2026-11-16-AP1-AI-Productivity-Spec.md"
SPEC_SHA256 = "822c7c8a7eac38dadabbb1860eb0eaf0972709c6eb8487a237ce8398b5a8866d"
OUT_REL = "data/ap1_ai_productivity"
CACHE_REL = "data/vintages/ap1"
UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"

GAP_SECONDS = 3.0
TIMEOUT = 120

PERM_SEED = 20261116
N_PERM = 100000
ALPHA = 0.05
N_CYCLES = 46
N_CYCLES_2023 = 8
NEEDED_YEARS = (2017, 2019, 2023, 2024, 2025)

BEA_SOURCES = (
    ("bea-valueadded", "raw/ValueAdded.xlsx", "https://apps.bea.gov/industry/Release/XLS/GDPxInd/ValueAdded.xlsx", "xlsx"),
    ("bea-nipa-data-a", "raw/NipaDataA.txt", "https://apps.bea.gov/national/Release/TXT/NipaDataA.txt", "nipa_data"),
    ("bea-series-register", "raw/SeriesRegister.txt", "https://apps.bea.gov/national/Release/TXT/SeriesRegister.txt", "series_reg"),
)

COMP_EMP = "Compensation of employees"
COMP_TAX = "Taxes on production and imports less subsidies"
COMP_GOS = "Gross operating surplus"
NATIONAL_LABEL = "Private industries"
NATIONAL_FTE = "A4303C"

# (code, bea_label, fte_series, ai_kind, ai_key, v2_p12, v2_p34, flag)
INDUSTRIES = (
    ("441", "Motor vehicle and parts dealers", "N4339C", "sub", "441", True, True, ""),
    ("511", "Publishing industries, except internet (includes software)", "N4353C", "sub", "511", True, True, "AI supplier"),
    ("512", "Motion picture and sound recording industries", "N4354C", "sub", "512", True, True, ""),
    ("518_519", "Data processing, internet publishing, and other information services", "N4356C", "sub_mean", ("518", "519"), False, False, "reported only (v2); AI supplier"),
    ("522", "Federal Reserve banks, credit intermediation, and related activities", "N4358C", "sub", "522", False, False, "reported only (v2); includes 521"),
    ("523", "Securities, commodity contracts, and investments", "N4359C", "sub", "523", True, True, "finance"),
    ("524", "Insurance carriers and related activities", "N4360C", "sub", "524", True, True, "finance"),
    ("541", "Professional, scientific, and technical services", "N4365C", "sub", "541", True, True, "AI supplier"),
    ("561", "Administrative and support services", "N4371C", "sub", "561", True, True, ""),
    ("611", "Educational services", "N4373C", "sub", "611", False, True, "out of P1/P2 (input-measured)"),
    ("621", "Ambulatory health care services", "N4375C", "sub", "621", True, True, ""),
    ("624", "Social assistance", "N4392C", "sub", "624", False, True, "out of P1/P2 (input-measured)"),
    ("711", "Performing arts, spectator sports, museums, and related activities", "N4394C", "sub", "711", False, False, "reported only (v2); includes 712"),
    ("713", "Amusements, gambling, and recreation industries", "N4395C", "sub", "713", True, True, ""),
    ("722", "Food services and drinking places", "N4398C", "sub", "722", True, True, ""),
    ("23", "Construction", "N4312C", "sec", "23", True, True, "sector-level AI"),
    ("31-33", "Manufacturing", "N4313C", "sec", "31-33", True, True, "sector-level AI"),
    ("42", "Wholesale trade", "N4335C", "sec", "42", True, True, "sector-level AI"),
    ("48-49", "Transportation and warehousing", "N4343C", "sec", "48-49", False, False, "reported only (v2); sector-level AI"),
    ("81", "Other services, except government", "N4399C", "sec", "81", False, False, "reported only (v2); sector-level AI"),
)

SECTOR_LOOKUP = {"31-33": ("31-33", "31"), "48-49": ("48-49", "48")}

REG_HEADER = ("statement_id", "version", "superseded", "scored", "statement", "statistic", "support_if", "against_if", "treatment_window", "placebo_window", "prereg_sha256")
SCORES_HEADER = ("statement_id", "label", "primary_statistic", "primary_value", "unit", "statistics", "denominators", "caveats")
DETAIL_HEADER = ("statement_id", "item", "value", "unit")
VINTAGES_HEADER = ("source", "key", "url", "fetched_utc", "status", "bytes", "sha256", "note")
IDS = ("AP1-P1", "AP1-P2", "AP1-P3", "AP1-P4")


def cache_dir(root=None):
    return os.path.join(root or ROOT, *CACHE_REL.split("/"))


def out_dir(root=None):
    return os.path.join(root or ROOT, *OUT_REL.split("/"))


def stop_with(cache, reason):
    write_text(os.path.join(cache, "STOP.txt"), reason + "\n")
    raise Stop(reason)


# ------------------------------------------------------------------------------------------------------------------------
# fetch (plain HTTPS GET from apps.bea.gov, no key, no contact details)
# ------------------------------------------------------------------------------------------------------------------------
class BeaFetcher(object):
    """Plain HTTPS GET fetcher. `opener` is injectable for the selftest."""

    def __init__(self, opener=None):
        self.opener = opener or urllib.request.build_opener()

    def get(self, url, headers):
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with self.opener.open(req, timeout=TIMEOUT) as resp:
                return resp.status, resp.read(), dict(resp.headers)
        except urllib.error.HTTPError as e:
            return e.code, e.read() if hasattr(e, "read") else b"", dict(e.headers or {})


def _validate_bea_response(cache, key, kind, status, body):
    if status != 200:
        stop_with(cache, "%s: HTTP status %s (expected 200)" % (key, status))
    if kind == "xlsx":
        if len(body) < 2 or body[:2] != b"PK":
            stop_with(cache, "%s: body is not a zip/xlsx (missing PK magic)" % key)
        return
    try:
        head = body[:4096].decode("utf-8")
    except UnicodeDecodeError as e:
        stop_with(cache, "%s: invalid UTF-8 header (%s)" % (key, e))
    first_line = head.splitlines()[0].lstrip("\ufeff").strip() if head.splitlines() else ""
    if kind == "nipa_data" and first_line != "%SeriesCode,Period,Value":
        stop_with(cache, "%s: unexpected first line %r (expected %%SeriesCode,Period,Value)" % (key, first_line))
    if kind == "series_reg" and not first_line.startswith("%SeriesCode,SeriesLabel"):
        stop_with(cache, "%s: unexpected first line %r (expected starting %%SeriesCode,SeriesLabel)" % (key, first_line))


def cmd_fetch(root=None, fetcher=None, sleep=time.sleep):
    cache = cache_dir(root)
    os.makedirs(cache, exist_ok=True)
    if os.path.exists(os.path.join(cache, "STOP.txt")):
        raise Stop("STOP.txt present in %s; review and delete manually before retrying" % CACHE_REL)
    for _key, rel, _url, _kind in BEA_SOURCES:
        if os.path.exists(os.path.join(cache, *rel.split("/"))):
            raise Refused("raw file %s already exists in %s (no refetch)" % (rel, CACHE_REL))
    f = fetcher or BeaFetcher()
    headers = {"User-Agent": UA}
    mp = os.path.join(cache, "manifest.csv")
    for idx, (key, rel, url, kind) in enumerate(BEA_SOURCES):
        if idx > 0:
            sleep(GAP_SECONDS)
        status, body, _hdrs = f.get(url, headers)
        _validate_bea_response(cache, key, kind, status, body)
        write_bytes(os.path.join(cache, *rel.split("/")), body)
        new = not os.path.exists(mp)
        with open(mp, "a", encoding="utf-8", newline="") as fh:
            if new:
                fh.write("key,url,fetched_utc,status,bytes,sha256\n")
            fh.write(csv_line([key, url, now_utc(), status, len(body), sha256_of(body)]))
        print("%s: fetched %d bytes, sha256 %s" % (key, len(body), sha256_of(body)))
    return 0


# ------------------------------------------------------------------------------------------------------------------------
# BEA workbook & NIPA flat-file parsing
# ------------------------------------------------------------------------------------------------------------------------
def clean_bea_label(val):
    """Strip leading/trailing spaces and footnote markers like \\1\\."""
    if val is None:
        return ""
    s = re.sub(r"\\[0-9]+\\", "", str(val))
    return s.strip()


def _parse_year_cell(val):
    if isinstance(val, bool) or val is None:
        return None
    if isinstance(val, (int, float)):
        if isinstance(val, float) and val != int(val):
            return None
        yr = int(val)
        return yr if 1900 <= yr <= 2100 else None
    s = str(val).strip()
    if re.match(r"^(19|20)\d{2}$", s):
        return int(s)
    return None


def _parse_num_cell(val):
    if isinstance(val, bool) or val is None:
        return None
    if isinstance(val, (int, float)):
        f = float(val)
        return None if math.isnan(f) or math.isinf(f) else f
    s = str(val).strip().replace(",", "")
    if not s or s in ("...", "--", "(NA)", "NA", "n.a."):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _find_header_and_release(rows, sheet_name):
    """Locate the year header row (must contain all NEEDED_YEARS) and extract release/vintage text from top rows."""
    header_idx = None
    year_cols = {}
    for i, r in enumerate(rows):
        ymap = {}
        for j, cell in enumerate(r):
            yr = _parse_year_cell(cell)
            if yr is not None and yr not in ymap:
                ymap[yr] = j
        if len(ymap) >= 5 and all(y in ymap for y in NEEDED_YEARS):
            header_idx = i
            year_cols = ymap
            break
    if header_idx is None:
        # Check if a year header exists with fewer years so we report the missing year clearly
        for i, r in enumerate(rows):
            ymap = {}
            for j, cell in enumerate(r):
                yr = _parse_year_cell(cell)
                if yr is not None and yr not in ymap:
                    ymap[yr] = j
            if len(ymap) >= 3:
                missing = [y for y in NEEDED_YEARS if y not in ymap]
                raise Refused("sheet %s missing needed year(s): %s" % (sheet_name, missing))
        raise Refused("sheet %s has no year header row" % sheet_name)

    first_yr_col = min(year_cols.values())
    if first_yr_col == 0:
        raise Refused("sheet %s has no label column before year columns" % sheet_name)
    # label column = the column before the years holding the most text cells below the header
    # (real BEA sheets: Line | label | blank | years; supervisor fix, 16 Nov)
    def _text_count(c):
        return sum(1 for r in rows[header_idx + 1:] if c < len(r) and isinstance(r[c], str) and clean_bea_label(r[c]) and _parse_num_cell(r[c]) is None)
    label_col = max(range(first_yr_col), key=lambda c: (_text_count(c), -c))

    release_parts = []
    for r in rows[:header_idx]:
        line_txt = " ".join(clean_bea_label(c) for c in r if clean_bea_label(c))
        if line_txt and re.search(r"release|revis|updat|vintage|date", line_txt, re.I):
            release_parts.append(line_txt)
    release = "; ".join(release_parts) if release_parts else "not stated"
    return header_idx, label_col, year_cols, release


def _extract_year_vals(row, year_cols, sheet_name, label):
    vals = {}
    for y in NEEDED_YEARS:
        col = year_cols[y]
        v = _parse_num_cell(row[col] if col < len(row) else None)
        if v is None:
            raise Refused("sheet %s row %r missing/non-numeric value for year %d" % (sheet_name, label, y))
        vals[y] = v
    return vals


def parse_value_added_xlsx(path, target_labels):
    """Parse TVA105-A, TVA106-A, TVA113-A from ValueAdded.xlsx for `target_labels`."""
    import openpyxl

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        for req in ("TVA105-A", "TVA106-A", "TVA113-A"):
            if req not in wb.sheetnames:
                raise Refused("ValueAdded.xlsx missing sheet %s" % req)

        targets = set(target_labels)
        releases = {}

        def read_flat_sheet(sname):
            rows = list(wb[sname].iter_rows(values_only=True))
            hidx, lcol, ycols, rel = _find_header_and_release(rows, sname)
            releases[sname] = rel
            out = {}
            for r in rows[hidx + 1:]:
                lab = clean_bea_label(r[lcol] if lcol < len(r) else None)
                if lab in targets:
                    if lab in out:
                        raise Refused("duplicate label %r in sheet %s" % (lab, sname))
                    out[lab] = _extract_year_vals(r, ycols, sname, lab)
            for t in target_labels:
                if t not in out:
                    raise Refused("missing row %r in sheet %s" % (t, sname))
            return out

        va_curr = read_flat_sheet("TVA105-A")
        va_real = read_flat_sheet("TVA106-A")

        # TVA113-A: component rows nested directly under each industry label
        rows_113 = list(wb["TVA113-A"].iter_rows(values_only=True))
        hidx, lcol, ycols, rel113 = _find_header_and_release(rows_113, "TVA113-A")
        releases["TVA113-A"] = rel113
        comp_names = {COMP_EMP, COMP_TAX, COMP_GOS}
        gos = {}
        i = hidx + 1
        while i < len(rows_113):
            lab = clean_bea_label(rows_113[i][lcol] if lcol < len(rows_113[i]) else None)
            if lab in targets:
                if lab in gos:
                    raise Refused("duplicate label %r in sheet TVA113-A" % lab)
                found_comps = {}
                j = i + 1
                while j < len(rows_113) and len(found_comps) < 3:
                    sub_lab = clean_bea_label(rows_113[j][lcol] if lcol < len(rows_113[j]) else None)
                    if sub_lab in comp_names:
                        found_comps[sub_lab] = _extract_year_vals(rows_113[j], ycols, "TVA113-A", "%s -> %s" % (lab, sub_lab))
                        j += 1
                    elif not sub_lab:
                        j += 1
                    else:
                        break
                if len(found_comps) != 3:
                    missing_c = sorted(comp_names - set(found_comps))
                    raise Refused("sheet TVA113-A under %r missing component row(s): %s" % (lab, missing_c))
                gos[lab] = found_comps[COMP_GOS]
                i = j
            else:
                i += 1
        for t in target_labels:
            if t not in gos:
                raise Refused("missing row %r in sheet TVA113-A" % t)
    finally:
        wb.close()

    return {"va_curr": va_curr, "va_real": va_real, "gos": gos, "releases": releases}


def parse_series_register(path, needed_codes):
    """Confirm each needed FTE series code exists in SeriesRegister.txt and belongs to table T60500D."""
    needed = set(needed_codes)
    found = {}
    with open(path, encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
        if not header or not header[0].lstrip("\ufeff").startswith("%SeriesCode"):
            raise Refused("SeriesRegister.txt has unexpected header %r" % (header,))
        for row in reader:
            if not row:
                continue
            code = row[0].strip()
            if code in needed:
                if not any("T60500D" in cell for cell in row):
                    raise Refused("SeriesRegister.txt code %s does not belong to table T60500D: %r" % (code, row))
                found[code] = row[1].strip() if len(row) > 1 else ""
    missing = sorted(needed - set(found))
    if missing:
        raise Refused("SeriesRegister.txt missing FTE code(s): %s" % missing)
    return found


def parse_nipa_data_a(path, needed_codes):
    """Parse NipaDataA.txt for `needed_codes` across NEEDED_YEARS; strip thousands commas."""
    needed = set(needed_codes)
    need_yrs = {str(y): y for y in NEEDED_YEARS}
    out = {c: {} for c in needed}
    with open(path, encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
        if not header or [h.lstrip("\ufeff").strip() for h in header[:3]] != ["%SeriesCode", "Period", "Value"]:
            raise Refused("NipaDataA.txt has unexpected header %r" % (header,))
        for row in reader:
            if len(row) < 3:
                continue
            code = row[0].strip()
            if code not in needed:
                continue
            per = row[1].strip()
            if per not in need_yrs:
                continue
            yr = need_yrs[per]
            val = _parse_num_cell(row[2])
            if val is None:
                raise Refused("NipaDataA.txt series %s year %d has non-numeric value %r" % (code, yr, row[2]))
            out[code][yr] = val
    for c in needed_codes:
        missing_y = [y for y in NEEDED_YEARS if y not in out[c]]
        if missing_y:
            raise Refused("NipaDataA.txt series %s missing year(s): %s" % (c, missing_y))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# BTOS lookup & pure computation
# ------------------------------------------------------------------------------------------------------------------------
def _lookup_btos(ai_kind, ai_key, sub_map, sec_map, req_cycles):
    if ai_kind == "sub":
        entry = sub_map.get(ai_key)
        if not entry or len(entry["used"]) < req_cycles or entry["mean"] is None:
            got = len(entry["used"]) if entry else 0
            return None, "BTOS subsector %s published %d of %d cycles" % (ai_key, got, req_cycles)
        return entry["mean"], None
    if ai_kind == "sub_mean":
        vals = []
        for k in ai_key:
            entry = sub_map.get(k)
            if not entry or len(entry["used"]) < req_cycles or entry["mean"] is None:
                got = len(entry["used"]) if entry else 0
                return None, "BTOS subsector %s (in %s) published %d of %d cycles" % (k, "+".join(ai_key), got, req_cycles)
            vals.append(entry["mean"])
        return sum(vals) / float(len(vals)), None
    # sector
    candidates = SECTOR_LOOKUP.get(ai_key, (ai_key,))
    entry = None
    for ck in candidates:
        if ck in sec_map:
            entry = sec_map[ck]
            break
    if not entry or len(entry["used"]) < req_cycles or entry["mean"] is None:
        got = len(entry["used"]) if entry else 0
        return None, "BTOS sector %s published %d of %d cycles" % (ai_key, got, req_cycles)
    return entry["mean"], None


def compute(bea, fte_data, btos, seed=PERM_SEED, nperm=N_PERM, ncycles=N_CYCLES, ncycles_2023=N_CYCLES_2023):
    """Pure computation of all AP1 version-2 primary and reported statistics. No files, no network."""
    sub_2425 = btos["sub_2425"]
    sec_2425 = btos["sec_2425"]
    sub_2023 = btos["sub_2023"]
    sec_2023 = btos["sec_2023"]

    va_curr = bea["va_curr"]
    va_real = bea["va_real"]
    gos = bea["gos"]

    # Stop rules (ruling 9): non-positive current-dollar VA or FTE stops the build
    for _code, label, fte_code, _ak, _akey, _p12, _p34, _fl in INDUSTRIES:
        for y in NEEDED_YEARS:
            if not va_curr[label][y] > 0:
                raise Refused("non-positive current-dollar VA in %r (%d): %s" % (label, y, va_curr[label][y]))
            if not fte_data[fte_code][y] > 0:
                raise Refused("non-positive FTE in %s (%r, %d): %s" % (fte_code, label, y, fte_data[fte_code][y]))
    for y in NEEDED_YEARS:
        if not va_real[NATIONAL_LABEL][y] > 0:
            raise Refused("non-positive national real VA (%d)" % y)
        if not fte_data[NATIONAL_FTE][y] > 0:
            raise Refused("non-positive national FTE (%d)" % y)

    ind = {}
    dropped_ai = []
    dropped_real_va = []

    for code, label, fte_code, ai_kind, ai_key, v2_p12, v2_p34, flag in INDUSTRIES:
        ai24, drop_reason = _lookup_btos(ai_kind, ai_key, sub_2425, sec_2425, ncycles)
        if drop_reason is not None:
            dropped_ai.append((code, drop_reason))
            continue

        ai23, _ = _lookup_btos(ai_kind, ai_key, sub_2023, sec_2023, ncycles_2023)

        # Margin shares in percentage points (negative GOS kept per ruling 9)
        s = {y: 100.0 * gos[label][y] / va_curr[label][y] for y in NEEDED_YEARS}
        d_post = s[2025] - s[2023]
        d_pre = s[2019] - s[2017]
        d_diff = d_post - d_pre
        d_post_2425 = s[2025] - s[2024]
        d_diff_2425 = d_post_2425 - d_pre
        d_1923 = s[2023] - s[2019]

        # Productivity: non-positive real VA drops the industry from P1/P2 and is listed
        bad_real = [y for y in NEEDED_YEARS if not va_real[label][y] > 0]
        if bad_real:
            dropped_real_va.append((code, "non-positive real VA in year(s) %s (dropped from P1/P2)" % bad_real))
            q = None
            g_post = g_pre = g_diff = g_post_2425 = g_diff_2425 = g_1923 = None
        else:
            q = {y: va_real[label][y] / fte_data[fte_code][y] for y in NEEDED_YEARS}
            g_post = math.log(q[2025]) - math.log(q[2023])
            g_pre = math.log(q[2019]) - math.log(q[2017])
            g_diff = g_post - g_pre
            g_post_2425 = math.log(q[2025]) - math.log(q[2024])
            g_diff_2425 = g_post_2425 - g_pre
            g_1923 = math.log(q[2023]) - math.log(q[2019])

        ind[code] = {
            "code": code, "label": label, "fte_code": fte_code, "ai_kind": ai_kind,
            "v2_p12": v2_p12, "v2_p34": v2_p34, "flag": flag,
            "ai": ai24, "ai_2023": ai23,
            "va19": va_curr[label][2019],
            "s": s, "d_post": d_post, "d_pre": d_pre, "d_diff": d_diff,
            "d_post_2425": d_post_2425, "d_diff_2425": d_diff_2425, "d_1923": d_1923,
            "q": q, "g_post": g_post, "g_pre": g_pre, "g_diff": g_diff,
            "g_post_2425": g_post_2425, "g_diff_2425": g_diff_2425, "g_1923": g_1923,
        }

    # National private-industry real VA per FTE
    nq = {y: va_real[NATIONAL_LABEL][y] / fte_data[NATIONAL_FTE][y] for y in NEEDED_YEARS}
    nat_g = {
        "g_post": math.log(nq[2025]) - math.log(nq[2023]),
        "g_pre": math.log(nq[2019]) - math.log(nq[2017]),
        "g_post_2425": math.log(nq[2025]) - math.log(nq[2024]),
        "g_1923": math.log(nq[2023]) - math.log(nq[2019]),
    }
    nat_g["g_diff"] = nat_g["g_post"] - nat_g["g_pre"]

    p12_kept = [c for c, *_ in INDUSTRIES if c in ind and ind[c]["v2_p12"] and ind[c]["g_post"] is not None]
    p34_kept = [c for c, *_ in INDUSTRIES if c in ind and ind[c]["v2_p34"]]
    v1_p12 = [c for c, *_ in INDUSTRIES if c in ind and ind[c]["g_post"] is not None]
    v1_p34 = [c for c, *_ in INDUSTRIES if c in ind]

    T = {}

    def run_test(key, members, field, ai_field="ai"):
        xs = [ind[c][ai_field] for c in members]
        ys = [ind[c][field] for c in members]
        res = perm_test(xs, ys, seed, nperm)
        res["members"] = list(members)
        T[key] = res

    # Primary labelled tests (version 2)
    run_test("P1", p12_kept, "g_post")
    run_test("P2", p12_kept, "g_diff")
    run_test("P3", p34_kept, "d_post")
    run_test("P4", p34_kept, "d_diff")
    for k in ("P1", "P2", "P3", "P4"):
        T[k]["label"] = label_perm(T[k])

    # Reported: all 20 version-1 rows
    run_test("P1_v1_20", v1_p12, "g_post")
    run_test("P2_v1_20", v1_p12, "g_diff")
    run_test("P3_v1_20", v1_p34, "d_post")
    run_test("P4_v1_20", v1_p34, "d_diff")

    # Reported: subsector-matched rows only (without sector-level AI rows 23, 31-33, 42)
    p12_sub = [c for c in p12_kept if ind[c]["ai_kind"] == "sub"]
    p34_sub = [c for c in p34_kept if ind[c]["ai_kind"] == "sub"]
    run_test("P1_subsectors_only", p12_sub, "g_post")
    run_test("P2_subsectors_only", p12_sub, "g_diff")
    run_test("P3_subsectors_only", p34_sub, "d_post")
    run_test("P4_subsectors_only", p34_sub, "d_diff")

    # Reported: without finance (523, 524)
    p12_nofin = [c for c in p12_kept if c not in ("523", "524")]
    p34_nofin = [c for c in p34_kept if c not in ("523", "524")]
    run_test("P1_no_finance", p12_nofin, "g_post")
    run_test("P2_no_finance", p12_nofin, "g_diff")
    run_test("P3_no_finance", p34_nofin, "d_post")
    run_test("P4_no_finance", p34_nofin, "d_diff")

    # Reported: without AI suppliers (511, 541)
    p12_nosup = [c for c in p12_kept if c not in ("511", "541")]
    p34_nosup = [c for c in p34_kept if c not in ("511", "541")]
    run_test("P1_no_ai_suppliers", p12_nosup, "g_post")
    run_test("P2_no_ai_suppliers", p12_nosup, "g_diff")
    run_test("P3_no_ai_suppliers", p34_nosup, "d_post")
    run_test("P4_no_ai_suppliers", p34_nosup, "d_diff")

    # Reported: 2024-25 window
    run_test("P1_2425", p12_kept, "g_post_2425")
    run_test("P2_2425", p12_kept, "g_diff_2425")
    run_test("P3_2425", p34_kept, "d_post_2425")
    run_test("P4_2425", p34_kept, "d_diff_2425")

    # Reported: 2019-23 change
    run_test("P1_1923", p12_kept, "g_1923")
    run_test("P3_1923", p34_kept, "d_1923")

    # Reported: 2023-cycle AI means where all 8 cycles are published
    p12_23 = [c for c in p12_kept if ind[c]["ai_2023"] is not None]
    p34_23 = [c for c in p34_kept if ind[c]["ai_2023"] is not None]
    if len(p12_23) >= 4:
        run_test("P1_2023ai", p12_23, "g_post", "ai_2023")
        run_test("P2_2023ai", p12_23, "g_diff", "ai_2023")
    if len(p34_23) >= 4:
        run_test("P3_2023ai", p34_23, "d_post", "ai_2023")
        run_test("P4_2023ai", p34_23, "d_diff", "ai_2023")

    for k in T:
        if "label" not in T[k]:
            T[k]["label_if_it_were_primary"] = label_perm(T[k])

    # Weighted Pearson (weights = 2019 nominal value added)
    w12 = [ind[c]["va19"] for c in p12_kept]
    w34 = [ind[c]["va19"] for c in p34_kept]
    ai12 = [ind[c]["ai"] for c in p12_kept]
    ai34 = [ind[c]["ai"] for c in p34_kept]
    weighted = {
        "P1": {"r": weighted_pearson(ai12, [ind[c]["g_post"] for c in p12_kept], w12), "n": len(p12_kept), "members": list(p12_kept), "weights_total": sum(w12)},
        "P2": {"r": weighted_pearson(ai12, [ind[c]["g_diff"] for c in p12_kept], w12), "n": len(p12_kept), "members": list(p12_kept), "weights_total": sum(w12)},
        "P3": {"r": weighted_pearson(ai34, [ind[c]["d_post"] for c in p34_kept], w34), "n": len(p34_kept), "members": list(p34_kept), "weights_total": sum(w34)},
        "P4": {"r": weighted_pearson(ai34, [ind[c]["d_diff"] for c in p34_kept], w34), "n": len(p34_kept), "members": list(p34_kept), "weights_total": sum(w34)},
    }

    return {
        "ind": ind,
        "p12_kept": p12_kept,
        "p34_kept": p34_kept,
        "dropped_ai": dropped_ai,
        "dropped_real_va": dropped_real_va,
        "national": {"q": nq, "g": nat_g},
        "tests": T,
        "weighted": weighted,
        "releases": bea.get("releases", {}),
        "ncycles": ncycles,
        "ncycles_2023": ncycles_2023,
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
    """Parse version 1 table and apply version 2 section amendments."""
    if "**Statements (version 2).**" not in text:
        raise Refused("the spec has no 'Statements (version 2)' section")
    rows = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*(AP1-P[1-4])\s*\|(.*)\|\s*$", line)
        if not m:
            continue
        cells = [c.strip().replace("**", "") for c in m.group(2).split("|")]
        if len(cells) != 4:
            raise Refused("table row %s does not have four cells" % m.group(1).strip())
        rows[m.group(1).strip()] = tuple(cells)
    if sorted(rows) != sorted(IDS):
        raise Refused("the spec table does not hold %s: %s" % (list(IDS), sorted(rows)))

    sup_rule = "one-sided permutation p <= 0.05 (positive, outside 2 MC SEs of 0.05) and every leave-one-out rho > 0"
    ag_rule = "one-sided permutation p <= 0.05 (negative, outside 2 MC SEs of 0.05) and every leave-one-out rho < 0"
    return {
        "AP1-P1": (rows["AP1-P1"][0], "Spearman, AI use vs g_post, 13 industries", sup_rule, ag_rule),
        "AP1-P2": (rows["AP1-P2"][0], "Spearman, AI use vs g_post - g_pre, 13 industries", sup_rule, ag_rule),
        "AP1-P3": ("The gross operating surplus share of value added rose more after 2023 where AI use is higher", "Spearman, AI use vs d_post, 15 industries", sup_rule, ag_rule),
        "AP1-P4": ("...relative to its own 2017-19 change", "Spearman, AI use vs d_post - d_pre, 15 industries", sup_rule, ag_rule),
    }


WINDOWS = {
    "AP1-P1": ("2023 to 2025", "none"),
    "AP1-P2": ("2023 to 2025", "2017 to 2019"),
    "AP1-P3": ("2023 to 2025", "none"),
    "AP1-P4": ("2023 to 2025", "2017 to 2019"),
}


def write_registered(out, root=None, pinned=None):
    sha = check_spec_hash(root, pinned)
    rows = parse_spec_v2(spec_text(root).decode("utf-8"))
    body = []
    for i in IDS:
        st, stat, sup, ag = rows[i]
        body.append([i, "2", "no", "yes", st, stat, sup, ag, WINDOWS[i][0], WINDOWS[i][1], sha])
    text = "# source: %s (version 2), sha256 %s; written before any statistic is computed\n" % (SPEC_FILE, sha) + csv_line(REG_HEADER) + "".join(csv_line(r) for r in body)
    path = os.path.join(out, "registered.csv")
    write_text(path, text)
    return path, sha


# ------------------------------------------------------------------------------------------------------------------------
# output rows & README
# ------------------------------------------------------------------------------------------------------------------------
def make_rows(R):
    T = R["tests"]
    scores = []
    caveat_prod = (
        "SUPPORT or AGAINST names only the cross-industry pattern, never AI as its cause (rates, prices, post-pandemic recovery, "
        "or fast-growing industries adopting AI can rank industries similarly). Real value added in finance is partly measured from inputs; "
        "FTE counts employees, not the self-employed; BTOS measures AI use by existing employers, firm-weighted; four statements, no multiplicity adjustment."
    )
    caveat_gos = (
        "SUPPORT or AGAINST names only the cross-industry pattern, never AI as its cause. P3 and P4 measure the gross-operating-surplus share of value added, "
        "NOT profit margins (GOS includes depreciation, proprietors' income, net interest, and own-account software investment, and BEA revises this component most). "
        "BTOS measures AI use by existing employers, firm-weighted; four statements, no multiplicity adjustment."
    )
    spec_rows = (
        ("AP1-P1", "P1", "spearman_AI_use_vs_g_post_real_VA_per_FTE", "13 productivity industries (2023-25)", caveat_prod),
        ("AP1-P2", "P2", "spearman_AI_use_vs_g_post_minus_g_pre_real_VA_per_FTE", "13 productivity industries (2023-25 vs 2017-19)", caveat_prod),
        ("AP1-P3", "P3", "spearman_AI_use_vs_d_post_GOS_share_of_VA", "15 margin industries (2023-25)", caveat_gos),
        ("AP1-P4", "P4", "spearman_AI_use_vs_d_post_minus_d_pre_GOS_share_of_VA", "15 margin industries (2023-25 vs 2017-19)", caveat_gos),
    )
    for sid, key, stat, desc, cav in spec_rows:
        t = T[key]
        den = "n=%d; members=%s; %s; dropped_ai=%d; dropped_real_va=%d; permutations=%d; seed=%d" % (
            t["n"], ",".join(t["members"]), desc, len(R["dropped_ai"]), len(R["dropped_real_va"]), R["nperm"], R["seed"]
        )
        scores.append([sid, t["label"], stat, f4(t["rho"]), "rank correlation", test_stats(t), den, cav])

    detail = []
    d = detail.append
    for sname in ("TVA105-A", "TVA106-A", "TVA113-A"):
        d(["AP1-SEC", "bea_release_%s" % sname, R["releases"].get(sname, "not stated"), "text"])
    d(["AP1-SEC", "btos_cycles_required_2024_2025", str(R["ncycles"]), "cycles"])
    d(["AP1-SEC", "btos_cycles_required_2023", str(R["ncycles_2023"]), "cycles"])
    d(["AP1-SEC", "p1_p2_kept_count", str(len(R["p12_kept"])), "industries"])
    d(["AP1-SEC", "p1_p2_kept_list", ",".join(R["p12_kept"]), "list"])
    d(["AP1-SEC", "p3_p4_kept_count", str(len(R["p34_kept"])), "industries"])
    d(["AP1-SEC", "p3_p4_kept_list", ",".join(R["p34_kept"]), "list"])
    d(["AP1-SEC", "dropped_ai_count", str(len(R["dropped_ai"])), "industries"])
    for code, reason in R["dropped_ai"]:
        d(["AP1-SEC", "dropped_ai_%s" % code, reason, "text"])
    d(["AP1-SEC", "dropped_real_va_count", str(len(R["dropped_real_va"])), "industries"])
    for code, reason in R["dropped_real_va"]:
        d(["AP1-SEC", "dropped_real_va_%s" % code, reason, "text"])

    se = mc_se_at(ALPHA, R["nperm"])
    for key in ("P1", "P2", "P3", "P4"):
        t = T[key]
        sid = "AP1-" + key
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

    # Per-industry table
    for code, *_rest in INDUSTRIES:
        if code not in R["ind"]:
            continue
        it = R["ind"][code]
        d(["AP1-TABLE", "ind_%s_ai_mean_2024_2025_pct" % code, "%.4f" % it["ai"], "percent of firms"])
        if it["ai_2023"] is not None:
            d(["AP1-TABLE", "ind_%s_ai_mean_2023_pct" % code, "%.4f" % it["ai_2023"], "percent of firms"])
        d(["AP1-TABLE", "ind_%s_va_curr_2019" % code, "%.2f" % it["va19"], "millions USD"])
        for k in ("d_pre", "d_post", "d_diff", "d_1923", "d_post_2425"):
            d(["AP1-TABLE", "ind_%s_%s" % (code, k), "%.4f" % it[k], "percentage points"])
        if it["g_post"] is not None:
            for k in ("g_pre", "g_post", "g_diff", "g_1923", "g_post_2425"):
                d(["AP1-TABLE", "ind_%s_%s" % (code, k), "%.6f" % it[k], "log points"])

    # Reported variants (each with n and members)
    for key in sorted(k for k in T if "label" not in T[k]):
        t = T[key]
        sid = "AP1-R-" + key
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

    # Weighted Pearson (each as its own row with n and members)
    for key in ("P1", "P2", "P3", "P4"):
        wp = R["weighted"][key]
        sid = "AP1-R-WEIGHTED-" + key
        d([sid, "pearson_weighted_2019_nominal_va", f4(wp["r"]), "correlation"])
        d([sid, "weights_total_2019_nominal_va", "%.2f" % wp["weights_total"], "millions USD"])
        d([sid, "n", str(wp["n"]), "industries"])
        d([sid, "members", ",".join(wp["members"]), "list"])

    # National private-industry real VA per FTE
    nat = R["national"]
    d(["AP1-R-NATIONAL", "n", "1", "industry"])
    d(["AP1-R-NATIONAL", "members", "%s (%s)" % (NATIONAL_LABEL, NATIONAL_FTE), "series"])
    for y in NEEDED_YEARS:
        d(["AP1-R-NATIONAL", "private_real_va_per_fte_%d" % y, "%.6f" % nat["q"][y], "millions 2017 USD per thousand FTE"])
    for k in ("g_pre", "g_post", "g_diff", "g_1923", "g_post_2425"):
        d(["AP1-R-NATIONAL", "private_%s" % k, "%.6f" % nat["g"][k], "log points"])
    return scores, detail


def vintage_rows(cache):
    rows = []
    last = {r["key"]: r for r in read_manifest(cache)}
    for key, _rel, url, _kind in BEA_SOURCES:
        r = last.get(key)
        if r is None:
            raise Refused("manifest has no row for %s: run fetch" % key)
        rows.append(["bea", key, url, r["fetched_utc"], r["status"], r["bytes"], r["sha256"], "BEA plain HTTPS GET"])
    bp = os.path.join(aj1.cv1.cache_dir(), *aj1.cv1.BTOS_REL.split("/"))
    rows.append([
        "census-btos", "btos-ai-core-questions", aj1.cv1.BTOS_URL, "2026-11-15", "hand download",
        os.path.getsize(bp) if os.path.exists(bp) else 0, aj1.cv1.BTOS_SHA256,
        "AI Core Questions (Original), hash-pinned in bin/cv1_confidence_velocity.py; read through aj1.load_btos_inputs",
    ])
    return rows


def readme_text(R, sha):
    T = R["tests"]
    L = []
    a = L.append
    a("# AP1: is AI raising productivity and profit margins where it is used? (build of 16 Nov 2026)")
    a("")
    a("## What was asked")
    a("")
    a("Since 2023, have industries that use more AI seen faster growth in output per worker and a larger rise in the "
      "gross operating surplus share of value added, compared with other industries and with their own 2017-19 change? "
      "Registered blind before any industry figure was read (`%s`, version 2, sha256 `%s`)." % (SPEC_FILE, sha))
    a("")
    a("## Result table")
    a("")
    a("| statement | label | n | rank correlation | p (positive) | p (negative) | leave-one-out range |")
    a("|---|---|---|---|---|---|---|")
    for sid, key, title in (
        ("AP1-P1", "P1", "P1: AI use vs real VA per FTE growth 2023-25"),
        ("AP1-P2", "P2", "P2: AI use vs real VA per FTE growth 2023-25 minus 2017-19"),
        ("AP1-P3", "P3", "P3: AI use vs GOS share change 2023-25 (pp)"),
        ("AP1-P4", "P4", "P4: AI use vs GOS share change 2023-25 minus 2017-19 (pp)"),
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
    a("- **Version-2 asymmetry.** Neither label identifies AI as the cause: SUPPORT says the pattern T4 predicts is present "
      "(industries that use more AI gained more in output per worker or in gross-operating-surplus share), and does not show AI as the cause: "
      "rates, prices, post-pandemic recovery, or fast-growing firms adopting AI because they are growing can rank industries similarly. "
      "AGAINST says the pattern is absent or reversed on this data (a significant negative correlation; near zero is INCONCLUSIVE).")
    a("- **P3 and P4 are gross-operating-surplus shares, not profit margins (ruling 2).** P3 and P4 measure the gross operating surplus "
      "share of value added (`GOS / VA`), not profit margins: gross operating surplus includes depreciation (so heavier software and "
      "data-centre investment raises it), proprietors' income, net interest, and own-account software investment, and BEA revises this component most.")
    a("- **Definitions (ruling 10).** The two BEA files share the 2017 NAICS rows; the surplus is an establishment-basis residual "
      "built partly from company tax data; BTOS is a separate survey of employer firms.")
    a("- **Revision re-score (ruling 6).** Because 2023 and 2025 remain open to BEA revision, this build records each sheet's file vintage; "
      "a calendar row re-runs AP1 after BEA's 2027 annual update and reports any label change.")
    a("- **BTOS series and coverage.** The BTOS series is the original wording (`AI Core Questions (Original)`), cycles 2024-2025 "
      "(46 cycles ending before 17 Nov 2025). BTOS measures AI use by existing employers, firm-weighted. FTE counts employees, not the self-employed.")
    a("- **Multiplicity.** Four statements are scored with no multiplicity adjustment.")
    a("- **BEA release/vintage text:** TVA105-A: %s; TVA106-A: %s; TVA113-A: %s." % (
        R["releases"].get("TVA105-A", "not stated"),
        R["releases"].get("TVA106-A", "not stated"),
        R["releases"].get("TVA113-A", "not stated"),
    ))
    a("")
    a("## Denominators and national benchmark")
    a("")
    a("- **P1/P2 kept industries (n=%d):** %s." % (len(R["p12_kept"]), ", ".join(R["p12_kept"])))
    a("- **P3/P4 kept industries (n=%d):** %s." % (len(R["p34_kept"]), ", ".join(R["p34_kept"])))
    a("- **Dropped for 46-cycle AI rule (n=%d):** %s." % (len(R["dropped_ai"]), "; ".join("%s (%s)" % x for x in R["dropped_ai"]) or "none"))
    a("- **Dropped from P1/P2 for non-positive real VA (n=%d):** %s." % (len(R["dropped_real_va"]), "; ".join("%s (%s)" % x for x in R["dropped_real_va"]) or "none"))
    a("- **National private industries (`%s`, FTE `%s`):** g_post (2023-25) = %.4f, g_pre (2017-19) = %.4f, diff = %.4f." % (
        NATIONAL_LABEL, NATIONAL_FTE, R["national"]["g"]["g_post"], R["national"]["g"]["g_pre"], R["national"]["g"]["g_diff"]
    ))
    a("- **Weighted Pearson (2019 nominal VA weights):** P1=%s (n=%d), P2=%s (n=%d), P3=%s (n=%d), P4=%s (n=%d)." % (
        f4(R["weighted"]["P1"]["r"]), R["weighted"]["P1"]["n"],
        f4(R["weighted"]["P2"]["r"]), R["weighted"]["P2"]["n"],
        f4(R["weighted"]["P3"]["r"]), R["weighted"]["P3"]["n"],
        f4(R["weighted"]["P4"]["r"]), R["weighted"]["P4"]["n"],
    ))
    a("")
    a("## Files")
    a("")
    a("`registered.csv` (written before any statistic), `scores.csv`, `detail.csv`, `vintages.csv`, `README.md`. Raw downloads stay in `%s` (gitignored)." % CACHE_REL)
    a("")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------------------------------
# build
# ------------------------------------------------------------------------------------------------------------------------
def load_cached_bea(root=None):
    cache = cache_dir(root)
    if os.path.exists(os.path.join(cache, "STOP.txt")):
        raise Refused("STOP.txt present in %s; resolve before building" % CACHE_REL)
    paths = {}
    for key, rel, _url, _kind in BEA_SOURCES:
        p = os.path.join(cache, *rel.split("/"))
        if not os.path.exists(p):
            raise Refused("missing cached BEA file %s (run fetch)" % rel)
        paths[key] = p

    target_labels = [row[1] for row in INDUSTRIES] + [NATIONAL_LABEL]
    needed_fte = [row[2] for row in INDUSTRIES] + [NATIONAL_FTE]
    bea = parse_value_added_xlsx(paths["bea-valueadded"], target_labels)
    parse_series_register(paths["bea-series-register"], needed_fte)
    fte_data = parse_nipa_data_a(paths["bea-nipa-data-a"], needed_fte)
    return bea, fte_data


def run_build(root=None, out=None):
    root = root or ROOT
    out = out or out_dir(root)
    cache = cache_dir(root)
    reg_path, sha = write_registered(out, root)  # FIRST: before any statistic
    reg_sha = sha256_of(open(reg_path, "rb").read())
    print("registered.csv written (spec sha256 %s; file sha256 %s)" % (sha, reg_sha), flush=True)

    bea, fte_data = load_cached_bea(root)
    btos = load_btos_inputs(root)
    R = compute(bea, fte_data, btos)
    scores, detail = make_rows(R)
    vint = vintage_rows(cache)
    src = "bin/ap1_ai_productivity.py build; scores computed after registered.csv (sha256 %s) was written; spec %s sha256 %s; permutations %d seed %d" % (
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
# selftest: clearly synthetic data only, no network, no real BEA data
# ------------------------------------------------------------------------------------------------------------------------
class _FakeBeaFetcher(object):
    def __init__(self, handler):
        self.handler = handler
        self.calls = []

    def get(self, url, headers):
        self.calls.append((url, headers))
        return self.handler(len(self.calls) - 1, url, headers)


def _write_synth_xlsx(path, btos, neg_gos_label=None, neg_real_label=None, missing_year=False, dup_label=None):
    import openpyxl

    wb = openpyxl.Workbook()
    ws105 = wb.active
    ws105.title = "TVA105-A"
    ws106 = wb.create_sheet("TVA106-A")
    ws113 = wb.create_sheet("TVA113-A")

    years = [2017, 2019, 2023, 2024] if missing_year else list(NEEDED_YEARS)
    for ws, title in ((ws105, "Value Added (current)"), (ws106, "Real Value Added"), (ws113, "Components")):
        ws.append([title])
        ws.append(["Release Date: Synthetic Test Vintage 2026-11-16"])
        ws.append(["Line", "Industry"] + years)

    all_rows = [(c, lbl, fte, ak, akey) for c, lbl, fte, ak, akey, _p12, _p34, _fl in INDUSTRIES]
    all_rows.append(("NAT", NATIONAL_LABEL, NATIONAL_FTE, "nat", "nat"))

    for idx, (code, label, _fte, ai_kind, ai_key) in enumerate(all_rows):
        if code == "NAT":
            ai_val = 5.0
        else:
            ai_val, _ = _lookup_btos(ai_kind, ai_key, btos["sub_2425"], btos["sec_2425"], N_CYCLES)
            ai_val = ai_val or 5.0

        # Synthetic monotone levels: higher AI -> faster 2023-25 productivity and margin growth
        va_curr_vals = {y: 1000.0 + 50.0 * idx for y in years}
        ws105.append([idx + 1, "  " + label + ("\\1\\" if idx == 0 else "")] + [va_curr_vals[y] for y in years])
        if dup_label == label:
            ws105.append([idx + 99, label] + [va_curr_vals[y] for y in years])

        real_vals = {}
        r23 = 1000.0 + 2.0 * idx
        for y in years:
            if neg_real_label == label and y == 2025:
                real_vals[y] = -10.0
            elif y in (2017, 2019):
                real_vals[y] = 1000.0
            elif y == 2023:
                real_vals[y] = r23
            elif y == 2024:
                real_vals[y] = r23 * math.exp(0.005 * ai_val)
            else:
                real_vals[y] = r23 * math.exp(0.01 * ai_val)
        ws106.append([idx + 1, label] + [real_vals[y] for y in years])

        ws113.append([idx + 1, label] + [va_curr_vals[y] for y in years])
        gos_vals = {}
        s23 = 0.30 + 0.0005 * idx
        for y in years:
            if neg_gos_label == label:
                gos_vals[y] = -50.0 if y == 2023 else (-30.0 if y == 2025 else -40.0)
            elif y in (2017, 2019):
                gos_vals[y] = 0.30 * va_curr_vals[y]
            elif y == 2023:
                gos_vals[y] = s23 * va_curr_vals[y]
            elif y == 2024:
                gos_vals[y] = (s23 + 0.002 * ai_val) * va_curr_vals[y]
            else:
                gos_vals[y] = (s23 + 0.005 * ai_val) * va_curr_vals[y]
        emp_vals = {y: 0.60 * va_curr_vals[y] for y in years}
        tax_vals = {y: va_curr_vals[y] - gos_vals[y] - emp_vals[y] for y in years}
        ws113.append(["", "    " + COMP_EMP] + [emp_vals[y] for y in years])
        ws113.append(["", "    " + COMP_TAX] + [tax_vals[y] for y in years])
        ws113.append(["", "    " + COMP_GOS] + [gos_vals[y] for y in years])

    wb.save(path)


def _synth_nipa_texts(missing_code=None, bad_table=False):
    reg_lines = ["%SeriesCode,SeriesLabel,TableId"]
    data_lines = ["%SeriesCode,Period,Value"]
    codes = [r[2] for r in INDUSTRIES] + [NATIONAL_FTE]
    for c in codes:
        if c == missing_code:
            continue
        tbl = "T99999X" if bad_table else "T60500D"
        reg_lines.append("%s,Synthetic FTE for %s,%s" % (c, c, tbl))
        for y in NEEDED_YEARS:
            data_lines.append('"%s","%d","1,000"' % (c, y))
    return ("\n".join(reg_lines) + "\n").encode("utf-8"), ("\n".join(data_lines) + "\n").encode("utf-8")


def selftest():
    ck = Checks()
    # 1. Spec hash & version-2 parsing
    spec_bytes = spec_text()
    ck.eq("spec: file on disk hashes to pinned sha256", sha256_of(spec_bytes), SPEC_SHA256)
    rows = parse_spec_v2(spec_bytes.decode("utf-8"))
    ck.eq("spec: 4 registered statements parsed", sorted(rows), sorted(IDS))
    ck.raises("spec: tampered hash refused", Refused, lambda: check_spec_hash(pinned="0" * 64))

    # 2. Fetcher: 3 GETs, UA, 3s sleep, no refetch, STOP conditions
    btos = aj1._synth_btos()
    with tempfile.TemporaryDirectory() as td:
        xlsx_p = os.path.join(td, "synth.xlsx")
        _write_synth_xlsx(xlsx_p, btos)
        xlsx_bytes = open(xlsx_p, "rb").read()
        reg_bytes, data_bytes = _synth_nipa_texts()
        replies = [(200, xlsx_bytes, {}), (200, data_bytes, {}), (200, reg_bytes, {})]
        slept = []
        ff = _FakeBeaFetcher(lambda idx, url, hdrs: replies[idx])
        cmd_fetch(td, fetcher=ff, sleep=slept.append)
        ck.eq("fetch: 3 GETs made", len(ff.calls), 3)
        ck.eq("fetch: User-Agent is exact house string", ff.calls[0][1]["User-Agent"], UA)
        ck.eq("fetch: 3.0s sleep between GETs", slept, [3.0, 3.0])
        ck.ok("fetch: manifest.csv written", os.path.exists(os.path.join(cache_dir(td), "manifest.csv")))
        ck.raises("fetch: refuses to refetch if raw files exist", Refused, lambda: cmd_fetch(td, fetcher=ff, sleep=slept.append))

    # STOP conditions
    for label_case, bad_reply in (
        ("HTTP 403", (403, b"forbidden", {})),
        ("non-PK xlsx", (200, b"<html>not zip</html>", {})),
    ):
        with tempfile.TemporaryDirectory() as td:
            ff = _FakeBeaFetcher(lambda idx, url, hdrs, r=bad_reply: r)
            ck.raises("fetch STOP: %s writes STOP.txt" % label_case, Stop, lambda: cmd_fetch(td, fetcher=ff, sleep=lambda s: None))
            ck.ok("fetch STOP: STOP.txt created on %s" % label_case, os.path.exists(os.path.join(cache_dir(td), "STOP.txt")))
            ck.raises("fetch STOP: existing STOP.txt blocks retry", Stop, lambda: cmd_fetch(td, fetcher=ff, sleep=lambda s: None))

    with tempfile.TemporaryDirectory() as td:
        ff = _FakeBeaFetcher(lambda idx, url, hdrs: (200, b"PK\x03\x04", {}) if idx == 0 else (200, b"BadHeader\n", {}))
        ck.raises("fetch STOP: bad NipaDataA header stops", Stop, lambda: cmd_fetch(td, fetcher=ff, sleep=lambda s: None))

    # 3. Parsing & stop rules (missing year, duplicate label, bad table, negative GOS kept, non-positive real VA dropped)
    with tempfile.TemporaryDirectory() as td:
        p_miss = os.path.join(td, "miss_yr.xlsx")
        _write_synth_xlsx(p_miss, btos, missing_year=True)
        ck.raises("parse: missing 2025 column stops", Refused, lambda: parse_value_added_xlsx(p_miss, [r[1] for r in INDUSTRIES]))

        p_dup = os.path.join(td, "dup.xlsx")
        _write_synth_xlsx(p_dup, btos, dup_label="Construction")
        ck.raises("parse: duplicate label stops", Refused, lambda: parse_value_added_xlsx(p_dup, [r[1] for r in INDUSTRIES]))

        reg_bad = os.path.join(td, "reg_bad.txt")
        rb, _ = _synth_nipa_texts(bad_table=True)
        write_bytes(reg_bad, rb)
        ck.raises("parse: non-T60500D series stops", Refused, lambda: parse_series_register(reg_bad, ["N4339C"]))

    # 4. End-to-end compute & output generation with synthetic monotone data
    with tempfile.TemporaryDirectory() as td:
        p_ok = os.path.join(td, "ok.xlsx")
        _write_synth_xlsx(p_ok, btos, neg_gos_label="Food services and drinking places", neg_real_label="Construction")
        reg_p = os.path.join(td, "SeriesRegister.txt")
        data_p = os.path.join(td, "NipaDataA.txt")
        rb, db = _synth_nipa_texts()
        write_bytes(reg_p, rb)
        write_bytes(data_p, db)
        bea = parse_value_added_xlsx(p_ok, [r[1] for r in INDUSTRIES] + [NATIONAL_LABEL])
        fte = parse_nipa_data_a(data_p, [r[2] for r in INDUSTRIES] + [NATIONAL_FTE])

        R = compute(bea, fte, btos, seed=PERM_SEED, nperm=1000)
        ck.eq("end-to-end: negative real VA dropped Construction from P1/P2 (n=12), kept in P3/P4 (n=15)", (len(R["p12_kept"]), len(R["p34_kept"])), (12, 15))
        ck.eq("end-to-end: dropped_real_va lists 23", [c for c, _ in R["dropped_real_va"]], ["23"])
        ck.near("end-to-end: P1 rho is 1.0", R["tests"]["P1"]["rho"], 1.0)
        ck.near("end-to-end: P2 rho is 1.0", R["tests"]["P2"]["rho"], 1.0)
        ck.eq("end-to-end: P1 and P2 SUPPORT", (R["tests"]["P1"]["label"], R["tests"]["P2"]["label"]), ("SUPPORT", "SUPPORT"))
        ck.ok("end-to-end: v1_20, no_finance, no_ai_suppliers, 2425, 1923, 2023ai present", all(
            k in R["tests"] for k in ("P1_v1_20", "P3_v1_20", "P1_no_finance", "P1_no_ai_suppliers", "P1_2425", "P1_1923", "P1_2023ai")
        ))
        scores, detail = make_rows(R)
        ck.eq("end-to-end: 4 score rows", len(scores), 4)
        out_td = os.path.join(td, "out")
        _rp, sha = write_registered(out_td)
        rd = readme_text(R, sha)
        for name, txt in (
            ("scores.csv", table_text("selftest", SCORES_HEADER, scores)),
            ("detail.csv", table_text("selftest", DETAIL_HEADER, detail)),
            ("README.md", rd),
        ):
            no_leak(name, txt)
            write_text(os.path.join(out_td, name), txt)
        ck.ok("README: required clauses present", (
            "Neither label identifies AI as the cause" in rd
            and "not profit margins" in rd
            and "establishment-basis residual" in rd
            and "2027 annual update" in rd
            and "original wording" in rd
            and "2024-2025" in rd
        ))

    bad = [(n, d) for n, c, d in ck.items if not c]
    for n, c, d in ck.items:
        print(("ok   " if c else "FAIL ") + n + ("" if c else "  <- " + d))
    print("%d checks, %d failed" % (len(ck.items), len(bad)))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="AP1 AI-use vs productivity & gross operating surplus share scorer (spec version 2)")
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
