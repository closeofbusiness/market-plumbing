#!/usr/bin/env python3
"""Pre-registered test of November 2026 equity/treasury/yen selloff positioning.

Implements _research/2026-11-24-Selloff-Positioning-Preregistration.md (Version 2)
using Python 3 standard library only.

MODES
  python3 bin/selloff_positioning.py selftest   # synthetic fixtures only, no network
  python3 bin/selloff_positioning.py fetch      # network mode: pulls CFTC TFF, Fed H.10, MoF week.csv
  python3 bin/selloff_positioning.py build      # offline: reads raw files, writes outputs

AMBIGUITIES
1. Fed H.10 DDP URL series parameter: bin/gold_real_yield_break.py uses hardcoded
   32-hex-char DDP package hashes from Choose.aspx (e.g. D5_SID, D6_SID) in DDP_FMT
   rather than computing them from the series mnemonic. Because fetch cannot be run
   or Choose.aspx queried here, fetch substitutes H10/H10/RXI_N.B.JA directly into
   the series= parameter of the DDP URL pattern; parse_h10() matches on Unique
   Identifier 'H10/H10/RXI_N.B.JA', so it works with either a single-series CSV or
   the multi-column H.10 Daily Rates package.
2. CFTC Socrata $order parameter: the brief specifies `$order=report_date` while the
   selected column is `report_date_as_yyyy_mm_dd` (used by bin/pull_cftc_tff.py).
   fetch sends `$order=report_date` per the brief and sorts rows locally by
   (cftc_contract_market_code, report_date_as_yyyy_mm_dd) before writing raw_tff.csv.
3. VX settlement Wednesday holiday adjustment: per the brief, the third Friday of
   month M+1 is computed without an exchange holiday calendar, and the settlement
   Wednesday is 30 calendar days before that third Friday.
4. Standard deviation (reported for information only, never used to score): computed
   as sample standard deviation (ddof=1) when n >= 2, and 0.0 when n < 2.
5. Seller rule tie-breaking: Leveraged Funds are named seller only if their primary
   E-mini S&P 500 net change is strictly negative (< 0) and strictly less than all
   other four classes' net changes.
6. Yardstick window dates for P5a and P6: P5a uses 097741 report dates; P6 uses the
   common report dates across the six Treasury codes (043602 as reference).
7. MoF week.csv parsing: MoF weekly CSVs may be Shift-JIS (cp932) or UTF-8 with
   Japanese/English multi-row headers; build tries utf-8-sig then cp932 and prints
   the last 6 non-empty rows with header labels if parseable, else notes "unparsed".
"""
import argparse
import contextlib
import csv
import datetime as dt
import hashlib
import io
import json
import math
import os
import re
import ssl
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR_DEFAULT = os.path.join(ROOT, "data", "selloff_positioning")
SPEC_PATH_DEFAULT = os.path.join(ROOT, "_research", "2026-11-24-Selloff-Positioning-Preregistration.md")

UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
REQUEST_SPACING_S = 2.05

CFTC_URL = "https://publicreporting.cftc.gov/resource/gpe5-46if.json"
CFTC_START = "2017-12-01"
CFTC_SELECT = ",".join([
    "report_date_as_yyyy_mm_dd",
    "cftc_contract_market_code",
    "open_interest_all",
    "dealer_positions_long_all",
    "dealer_positions_short_all",
    "asset_mgr_positions_long",
    "asset_mgr_positions_short",
    "lev_money_positions_long",
    "lev_money_positions_short",
    "other_rept_positions_long",
    "other_rept_positions_short",
    "nonrept_positions_long_all",
    "nonrept_positions_short_all",
])

H10_SERIES_ID = "H10/H10/RXI_N.B.JA"
H10_URL = "https://www.federalreserve.gov/releases/h10/hist/dat00_ja.htm"  # H.10 historical table, Japan, yen per dollar (supervisor fix: the DDP needs a package hash, not the mnemonic)
MOF_URL = "https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/week.csv"

CODES = [
    ("13874A", "E-mini S&P 500"),
    ("209742", "E-mini Nasdaq-100"),
    ("239742", "E-mini Russell 2000"),
    ("1170E1", "VIX futures (Cboe)"),
    ("097741", "Japanese yen (CME)"),
    ("042601", "UST 2Y"),
    ("044601", "UST 5Y"),
    ("043602", "UST 10Y"),
    ("043607", "Ultra 10Y"),
    ("020601", "UST Bond"),
    ("020604", "Ultra Bond"),
]
CODE_SET = {c for c, _ in CODES}

TREASURY_DV01 = {
    "042601": 34.0,
    "044601": 42.0,
    "043602": 63.0,
    "043607": 91.0,
    "020601": 137.0,
    "020604": 215.0,
}

CLASSES = [
    ("dealer", "dealer_positions_long_all", "dealer_positions_short_all"),
    ("asset_mgr", "asset_mgr_positions_long", "asset_mgr_positions_short"),
    ("lev_money", "lev_money_positions_long", "lev_money_positions_short"),
    ("other_rept", "other_rept_positions_long", "other_rept_positions_short"),
    ("nonrept", "nonrept_positions_long_all", "nonrept_positions_short_all"),
]

FIELDS = ("net", "gross_long", "gross_short")

PRIMARY_START = "2026-11-10"
PRIMARY_END = "2026-11-24"
SECONDARY_START = "2026-11-10"
SECONDARY_END = "2026-11-17"
YARDSTICK_START_YEAR = 2018
YARDSTICK_END_MAX = "2026-11-10"

# Mutant toggle for selftest
_MUT = set()


def mut(name):
    return name in _MUT


@contextlib.contextmanager
def mutant(*names):
    added = [n for n in names if n not in _MUT]
    _MUT.update(added)
    try:
        yield
    finally:
        for n in added:
            _MUT.discard(n)


def par_mod_duration(y_pct, n=10):
    y = y_pct / 100.0
    return (1.0 / y) * (1.0 - 1.0 / (1.0 + y / 2.0) ** (2 * n))


REF_DUR = par_mod_duration(4.0, 10)


def fmt_float(val, nd):
    if val is None:
        return ""
    s = format(round(float(val), nd), f".{nd}f")
    return s[1:] if s.startswith("-") and float(s) == 0.0 else s


def fmt_num(val, is_int=False, nd=4):
    if val is None:
        return ""
    if is_int:
        return str(int(round(val)))
    return fmt_float(val, nd)


def vx_settlement_wednesday(year, month):
    """Wednesday 30 days before the third Friday of month M+1 (no holiday table)."""
    if month == 12:
        ny, nm = year + 1, 1
    else:
        ny, nm = year, month + 1
    first_day = dt.date(ny, nm, 1)
    # Friday is weekday 4
    days_to_fri = (4 - first_day.weekday()) % 7
    third_fri = first_day + dt.timedelta(days=days_to_fri + 14)
    offset = 29 if mut("vx_offset_29") else 30
    return third_fri - dt.timedelta(days=offset)


def vx_settlement_dates(start_year, end_year):
    out = []
    for y in range(start_year, end_year + 1):
        for m in range(1, 13):
            out.append(vx_settlement_wednesday(y, m).isoformat())
    return sorted(set(out))


def qualifying_windows(dates, kind, exclude_dates=None):
    """Return list of (d1, d2) from sorted report dates meeting gap & sample bounds."""
    if kind == "two_week":
        lo, hi = (12, 16) if mut("gap_12_16") else (13, 15)
    elif kind == "one_week":
        lo, hi = (6, 8)
    else:
        raise ValueError(f"Unknown window kind: {kind}")

    eligible = [d for d in sorted(dates) if int(d[:4]) >= YARDSTICK_START_YEAR and d <= YARDSTICK_END_MAX]
    excl = sorted(exclude_dates) if exclude_dates else []
    pairs = []
    for i, d1 in enumerate(eligible):
        dt1 = dt.date.fromisoformat(d1)
        for j in range(i + 1, len(eligible)):
            d2 = eligible[j]
            gap = (dt.date.fromisoformat(d2) - dt1).days
            if gap < lo:
                continue
            if gap > hi:
                break
            if excl and any(d1 < s <= d2 for s in excl):
                continue
            pairs.append((d1, d2))
    return pairs


def compute_score(yardstick_changes, obs_change):
    """Return (percentile, n, sd, flag). obs_change may be None."""
    n = len(yardstick_changes)
    if n == 0:
        return None, 0, None, "-"
    mean = sum(yardstick_changes) / n
    if n >= 2:
        var = sum((x - mean) ** 2 for x in yardstick_changes) / (n - 1)
        sd = math.sqrt(var)
    else:
        sd = 0.0
    if obs_change is None:
        return None, n, sd, "-"
    if mut("pct_strict_lt"):
        cnt = sum(1 for x in yardstick_changes if x < obs_change)
    else:
        cnt = sum(1 for x in yardstick_changes if x <= obs_change)
    pct = cnt / n
    if pct <= 0.10:
        flag = "Low"
    elif pct >= 0.90:
        flag = "High"
    else:
        flag = "-"
    return pct, n, sd, flag


# --------------------------------------------------------------------------------------------------
# FETCH (never called in selftest or by agent)
# --------------------------------------------------------------------------------------------------
class _RateLimiter:
    def __init__(self, spacing=REQUEST_SPACING_S):
        self.spacing = spacing
        self.last_ts = None

    def wait(self):
        if self.last_ts is not None:
            elapsed = time.monotonic() - self.last_ts
            if elapsed < self.spacing:
                time.sleep(self.spacing - elapsed)
        self.last_ts = time.monotonic()


def _http_get(url, limiter):
    limiter.wait()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    ctx = ssl.create_default_context()
    retried = False
    while True:
        try:
            with urllib.request.urlopen(req, timeout=90, context=ctx) as resp:
                if resp.status != 200:
                    print(f"STOP: HTTP {resp.status} for {url}", file=sys.stderr)
                    raise SystemExit(3)
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and not retried:
                ra = e.headers.get("Retry-After")
                if ra and ra.strip().isdigit():
                    retried = True
                    time.sleep(int(ra.strip()))
                    limiter.last_ts = time.monotonic()
                    continue
            print(f"STOP: HTTP {e.code} for {url}", file=sys.stderr)
            raise SystemExit(3)
        except urllib.error.URLError as e:
            print(f"STOP: network error ({e}) for {url}", file=sys.stderr)
            raise SystemExit(3)


def fetch_all(data_dir=DATA_DIR_DEFAULT):
    os.makedirs(data_dir, exist_ok=True)
    limiter = _RateLimiter()
    raw_cols = [
        "report_date_as_yyyy_mm_dd",
        "cftc_contract_market_code",
        "open_interest_all",
        "dealer_positions_long_all",
        "dealer_positions_short_all",
        "asset_mgr_positions_long",
        "asset_mgr_positions_short",
        "lev_money_positions_long",
        "lev_money_positions_short",
        "other_rept_positions_long",
        "other_rept_positions_short",
        "nonrept_positions_long_all",
        "nonrept_positions_short_all",
    ]
    tff_rows = []
    seen_keys = set()
    for code, _ in CODES:
        params = {
            "$select": CFTC_SELECT,
            "$where": f"cftc_contract_market_code='{code}' AND report_date_as_yyyy_mm_dd >= '{CFTC_START}'",
            "$order": "report_date_as_yyyy_mm_dd",
            "$limit": "5000",
        }
        url = CFTC_URL + "?" + urllib.parse.urlencode(params)
        body = _http_get(url, limiter)
        data = json.loads(body.decode("utf-8"))
        assert len(data) < 5000, f"CFTC page limit reached for {code}"
        for rec in data:
            row = {c: str(rec.get(c, "")).strip() for c in raw_cols}
            row["report_date_as_yyyy_mm_dd"] = row["report_date_as_yyyy_mm_dd"][:10]
            key = (row["cftc_contract_market_code"], row["report_date_as_yyyy_mm_dd"])
            assert key not in seen_keys, f"Duplicate CFTC row for {key}"
            seen_keys.add(key)
            tff_rows.append(row)

    tff_rows.sort(key=lambda r: (r["cftc_contract_market_code"], r["report_date_as_yyyy_mm_dd"]))
    with open(os.path.join(data_dir, "raw_tff.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=raw_cols)
        w.writeheader()
        w.writerows(tff_rows)

    h10_body = _http_get(H10_URL, limiter)
    h10_csv = h10_html_to_csv(h10_body.decode("utf-8", "replace"))
    with open(os.path.join(data_dir, "raw_h10_jpy.csv"), "w", encoding="utf-8") as f:
        f.write(h10_csv)

    mof_body = _http_get(MOF_URL, limiter)
    with open(os.path.join(data_dir, "raw_mof_week.csv"), "wb") as f:
        f.write(mof_body)
    print(f"Fetched {len(tff_rows)} TFF rows, H.10 ({len(h10_body)} B), MoF ({len(mof_body)} B).")


# --------------------------------------------------------------------------------------------------
# PARSERS & HELPERS
# --------------------------------------------------------------------------------------------------
def parse_tff(path):
    """Return (by_code, checks_info) where by_code[code][date] = row dict of ints."""
    by_code = {c: {} for c, _ in CODES}
    dup_count = 0
    neg_count = 0
    int_cols = [
        "open_interest_all",
        "dealer_positions_long_all", "dealer_positions_short_all",
        "asset_mgr_positions_long", "asset_mgr_positions_short",
        "lev_money_positions_long", "lev_money_positions_short",
        "other_rept_positions_long", "other_rept_positions_short",
        "nonrept_positions_long_all", "nonrept_positions_short_all",
    ]
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            code = r["cftc_contract_market_code"].strip()
            d = r["report_date_as_yyyy_mm_dd"].strip()[:10]
            if code not in by_code:
                continue
            if d in by_code[code]:
                dup_count += 1
            parsed = {}
            for col in int_cols:
                v = int(r[col])
                if v < 0:
                    neg_count += 1
                parsed[col] = v
            by_code[code][d] = parsed
    return by_code, dup_count, neg_count



def h10_html_to_csv(html_text):
    """Turn the H.10 historical HTML table (rows like 10-NOV-26 | 158.7600, ND = no data) into the DDP-style CSV that
    parse_h10 reads. Supervisor addition, 24 Nov 2026. Fails loudly if the table is not found."""
    rows = re.findall(r'<th[^>]*>\s*(\d{1,2}-[A-Z]{3}-\d{2})\s*</th>\s*<td[^>]*>\s*([^<]*?)\s*</td>', html_text)
    if len(rows) < 1000:
        raise SystemExit("STOP: H.10 historical table not found or too short (%d rows)" % len(rows))
    out = ['"Series Description","Japan -- spot exchange rate, yen/US$ (H.10 historical table)"',
           '"Unit:","Currency:_Per_USD"', '"Multiplier:","1"', '"Unique Identifier:","%s"' % H10_SERIES_ID, '"Time Period","RXI_N.B.JA"']
    for d, v in rows:
        iso = dt.datetime.strptime(d.title(), "%d-%b-%y").date().isoformat()
        out.append("%s,%s" % (iso, v.strip()))
    return "\n".join(out) + "\n"

def parse_h10(path, want_id=H10_SERIES_ID):
    """Parse Fed DDP H.10 CSV. Returns dict {YYYY-MM-DD: float}."""
    with open(path, "rb") as f:
        text = f.read().decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(text)))
    hdr = {r[0].strip(): r[1:] for r in rows[:10] if r}
    ids = [x.strip() for x in hdr.get("Unique Identifier:", [])]
    if want_id not in ids:
        raise ValueError(f"H.10 CSV lacks Unique Identifier {want_id!r}")
    idx = ids.index(want_id)
    mult_list = hdr.get("Multiplier:", ["1"] * len(ids))
    mult = float(mult_list[idx]) if idx < len(mult_list) and mult_list[idx].strip() else 1.0
    out = {}
    for r in rows:
        if r and re.fullmatch(r"\d{4}-\d{2}-\d{2}", r[0].strip()):
            if idx + 1 >= len(r):
                continue
            v = r[idx + 1].strip()
            if v in ("", "ND", "NA"):
                continue
            try:
                out[r[0].strip()] = float(v) * mult
            except ValueError:
                continue
    return out


def nearest_h10(h10_map, target_date, allow_earlier=True):
    """Return (used_date, rate) for target_date, or (None, None)."""
    if target_date in h10_map:
        return target_date, h10_map[target_date]
    if not allow_earlier:
        return None, None
    earlier = [d for d in h10_map if d < target_date]
    if not earlier:
        return None, None
    best = max(earlier)
    return best, h10_map[best]


def parse_mof_last6(path):
    """Best-effort parse of MoF week.csv; returns (ok, lines)."""
    if not os.path.exists(path):
        return False, ["unparsed (file missing)"]
    raw = open(path, "rb").read()
    text = None
    for enc in ("utf-8-sig", "cp932", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        return False, ["unparsed"]
    rows = [r for r in csv.reader(io.StringIO(text)) if any(c.strip() for c in r)]
    if len(rows) < 2:
        return False, ["unparsed"]
    # Find header row (last row before data rows containing non-numeric labels)
    data_idx = None
    for i in range(len(rows) - 1, -1, -1):
        if rows[i] and re.search(r"\d{4}", rows[i][0]):
            data_idx = i
        elif data_idx is not None:
            break
    if data_idx is None or data_idx == 0:
        return False, ["unparsed"]
    header = [c.strip() for c in rows[data_idx - 1]]
    data_rows = rows[data_idx:]
    if not data_rows:
        return False, ["unparsed"]
    last6 = data_rows[-6:]
    lines = []
    for r in last6:
        pairs = [f"{header[k] if k < len(header) and header[k] else f'col{k}'}={r[k].strip()}" for k in range(len(r))]
        lines.append(", ".join(pairs))
    return True, lines


def class_field_val(row, cls_name, long_col, short_col, field):
    if field == "net":
        return row[long_col] - row[short_col]
    if field == "gross_long":
        return row[long_col]
    if field == "gross_short":
        return row[short_col]
    raise ValueError(field)


def treasury_p6_10yeq_bn(by_code, d):
    total = 0.0
    for code, dv01 in TREASURY_DV01.items():
        if d not in by_code[code]:
            return None
        short_contracts = by_code[code][d]["lev_money_positions_short"]
        total += short_contracts * dv01 / (REF_DUR * 1e-4) / 1e9
    return total


# --------------------------------------------------------------------------------------------------
# BUILD
# --------------------------------------------------------------------------------------------------
def build_all(data_dir=DATA_DIR_DEFAULT, spec_path=SPEC_PATH_DEFAULT, quiet=False):
    raw_tff = os.path.join(data_dir, "raw_tff.csv")
    raw_h10 = os.path.join(data_dir, "raw_h10_jpy.csv")
    raw_mof = os.path.join(data_dir, "raw_mof_week.csv")

    by_code, dup_count, neg_count = parse_tff(raw_tff)
    h10_map = parse_h10(raw_h10) if os.path.exists(raw_h10) else {}
    mof_ok, mof_lines = parse_mof_last6(raw_mof)

    vx_excl = set(vx_settlement_dates(YARDSTICK_START_YEAR, 2027))

    results_rows = []
    yardstick_dates_seen = set()

    # 1. All 11 CFTC contracts x 5 classes x 3 fields x 2 windows
    for code, _ in CODES:
        dates = sorted(by_code[code].keys())
        win_two = qualifying_windows(dates, "two_week")
        win_one = qualifying_windows(dates, "one_week")
        for d1, d2 in win_two + win_one:
            yardstick_dates_seen.add(d2)

        for cls_name, lcol, scol in CLASSES:
            for field in FIELDS:
                for win_name, start_d, end_d, wlist in (
                    ("primary", PRIMARY_START, PRIMARY_END, win_two),
                    ("secondary", SECONDARY_START, SECONDARY_END, win_one),
                ):
                    ys = [
                        class_field_val(by_code[code][d2], cls_name, lcol, scol, field)
                        - class_field_val(by_code[code][d1], cls_name, lcol, scol, field)
                        for d1, d2 in wlist
                    ]
                    if start_d in by_code[code] and end_d in by_code[code]:
                        obs = (
                            class_field_val(by_code[code][end_d], cls_name, lcol, scol, field)
                            - class_field_val(by_code[code][start_d], cls_name, lcol, scol, field)
                        )
                    else:
                        obs = None
                    pct, n, sd, flag = compute_score(ys, obs)
                    results_rows.append({
                        "code": code,
                        "class": cls_name,
                        "field": field,
                        "window": win_name,
                        "start": start_d,
                        "end": end_d,
                        "change": fmt_num(obs, is_int=True),
                        "percentile": fmt_num(pct, nd=4),
                        "n": str(n),
                        "sd": fmt_num(sd, nd=4),
                        "flag": flag,
                    })

    # Special P4 line: 1170E1 lev_money gross_short secondary_no_vx
    vix_dates = sorted(by_code["1170E1"].keys())
    win_one_novx = qualifying_windows(vix_dates, "one_week", exclude_dates=vx_excl)
    for _, d2 in win_one_novx:
        yardstick_dates_seen.add(d2)
    p4_ys = [
        by_code["1170E1"][d2]["lev_money_positions_short"] - by_code["1170E1"][d1]["lev_money_positions_short"]
        for d1, d2 in win_one_novx
    ]
    if SECONDARY_START in by_code["1170E1"] and SECONDARY_END in by_code["1170E1"]:
        p4_obs = (
            by_code["1170E1"][SECONDARY_END]["lev_money_positions_short"]
            - by_code["1170E1"][SECONDARY_START]["lev_money_positions_short"]
        )
    else:
        p4_obs = None
    p4_pct, p4_n, p4_sd, p4_flag = compute_score(p4_ys, p4_obs)
    results_rows.append({
        "code": "1170E1",
        "class": "lev_money",
        "field": "gross_short",
        "window": "secondary_no_vx",
        "start": SECONDARY_START,
        "end": SECONDARY_END,
        "change": fmt_num(p4_obs, is_int=True),
        "percentile": fmt_num(p4_pct, nd=4),
        "n": str(p4_n),
        "sd": fmt_num(p4_sd, nd=4),
        "flag": p4_flag,
    })

    # 2. P5a H10_JPY (primary)
    jpy_dates = sorted(by_code["097741"].keys())
    jpy_two = qualifying_windows(jpy_dates, "two_week")
    p5a_ys = []
    for d1, d2 in jpy_two:
        _, r1 = nearest_h10(h10_map, d1, allow_earlier=True)
        _, r2 = nearest_h10(h10_map, d2, allow_earlier=True)
        if r1 is not None and r2 is not None and r1 > 0 and r2 > 0:
            p5a_ys.append(math.log(r2 / r1))
    s_used, r_start = nearest_h10(h10_map, PRIMARY_START, allow_earlier=True)
    e_used, r_end = nearest_h10(h10_map, PRIMARY_END, allow_earlier=False)
    if r_start is not None and r_end is not None and r_start > 0 and r_end > 0:
        p5a_obs = math.log(r_end / r_start)
    else:
        p5a_obs = None
    p5a_pct, p5a_n, p5a_sd, p5a_flag = compute_score(p5a_ys, p5a_obs)
    results_rows.append({
        "code": "H10_JPY",
        "class": "fx",
        "field": "log_change",
        "window": "primary",
        "start": PRIMARY_START,
        "end": PRIMARY_END,
        "change": fmt_num(p5a_obs, nd=6),
        "percentile": fmt_num(p5a_pct, nd=4),
        "n": str(p5a_n),
        "sd": fmt_num(p5a_sd, nd=6),
        "flag": p5a_flag,
    })

    # 3. P6 UST_ALL6 10y-eq gross short (primary)
    ust_common_dates = sorted(set.intersection(*(set(by_code[c].keys()) for c in TREASURY_DV01)))
    ust_two = qualifying_windows(ust_common_dates, "two_week")
    p6_ys = []
    for d1, d2 in ust_two:
        v1 = treasury_p6_10yeq_bn(by_code, d1)
        v2 = treasury_p6_10yeq_bn(by_code, d2)
        if v1 is not None and v2 is not None:
            p6_ys.append(v2 - v1)
    p6_v1 = treasury_p6_10yeq_bn(by_code, PRIMARY_START)
    p6_v2 = treasury_p6_10yeq_bn(by_code, PRIMARY_END)
    p6_obs = (p6_v2 - p6_v1) if (p6_v1 is not None and p6_v2 is not None) else None
    p6_pct, p6_n, p6_sd, p6_flag = compute_score(p6_ys, p6_obs)
    results_rows.append({
        "code": "UST_ALL6",
        "class": "lev_money",
        "field": "gross_short_10yeq_bn",
        "window": "primary",
        "start": PRIMARY_START,
        "end": PRIMARY_END,
        "change": fmt_num(p6_obs, nd=4),
        "percentile": fmt_num(p6_pct, nd=4),
        "n": str(p6_n),
        "sd": fmt_num(p6_sd, nd=4),
        "flag": p6_flag,
    })

    # Lookup helper for registration_score.csv
    res_map = {(r["code"], r["class"], r["field"], r["window"]): r for r in results_rows}

    def score_fire(id_, rule, pred, cred, key, want_flag, primary_inconclusive=False):
        r = res_map[key]
        if r["change"] == "":
            return {"id": id_, "rule": rule, "prediction": pred, "credence": cred, "status": "PENDING", "outcome": "n/a", "detail": "missing end row"}
        fired = (r["flag"] == want_flag)
        if fired:
            status = "FIRED"
        else:
            status = "INCONCLUSIVE" if (primary_inconclusive and not mut("no_inconclusive")) else "NOT_FIRED"
        if pred == "fires":
            outcome = "RIGHT" if fired else "WRONG"
        else:
            outcome = "WRONG" if fired else "RIGHT"
        detail = f"chg={r['change']} pct={r['percentile']} n={r['n']} flag={r['flag']}"
        return {"id": id_, "rule": rule, "prediction": pred, "credence": cred, "status": status, "outcome": outcome, "detail": detail}

    # P2: Asset Manager net change > Leveraged Funds net change (13874A, primary)
    am_r = res_map[("13874A", "asset_mgr", "net", "primary")]
    lm_r = res_map[("13874A", "lev_money", "net", "primary")]
    if am_r["change"] == "" or lm_r["change"] == "":
        p2_row = {"id": "P2", "rule": "am_net_chg > lev_net_chg", "prediction": "holds", "credence": "55%", "status": "PENDING", "outcome": "n/a", "detail": "missing end row"}
    else:
        holds = int(am_r["change"]) > int(lm_r["change"])
        p2_row = {
            "id": "P2", "rule": "am_net_chg > lev_net_chg", "prediction": "holds", "credence": "55%",
            "status": "HOLDS" if holds else "FAILS",
            "outcome": "RIGHT" if holds else "WRONG",
            "detail": f"am_chg={am_r['change']} lev_chg={lm_r['change']}",
        }

    # Seller rule: 13874A primary, lev_money net change is largest decline among all 5 classes
    all5_chg = {c: res_map[("13874A", c, "net", "primary")]["change"] for c, _, _ in CLASSES}
    if any(v == "" for v in all5_chg.values()):
        seller_row = {"id": "SELLER", "rule": "lev_money most negative of 5 classes (13874A primary)", "prediction": "n/a", "credence": "n/a", "status": "PENDING", "outcome": "n/a", "detail": "missing end row"}
    else:
        vals = {c: int(v) for c, v in all5_chg.items()}
        lm_v = vals["lev_money"]
        others = [v for c, v in vals.items() if c != "lev_money"]
        is_seller = (lm_v < 0) and all(lm_v < v for v in others)
        seller_row = {
            "id": "SELLER",
            "rule": "lev_money most negative of 5 classes (13874A primary)",
            "prediction": "n/a",
            "credence": "n/a",
            "status": "MET" if is_seller else "NOT_MET",
            "outcome": "n/a",
            "detail": " ".join(f"{c}={vals[c]}" for c, _, _ in CLASSES),
        }

    reg_rows = [
        score_fire("P1", "13874A lev_money net primary Low", "fires", "50%", ("13874A", "lev_money", "net", "primary"), "Low", primary_inconclusive=True),
        score_fire("P1s", "13874A lev_money net secondary Low", "fires", "55%", ("13874A", "lev_money", "net", "secondary"), "Low"),
        p2_row,
        score_fire("P3", "209742 lev_money net primary Low", "fires", "45%", ("209742", "lev_money", "net", "primary"), "Low", primary_inconclusive=True),
        score_fire("P3s", "209742 lev_money net secondary Low", "fires", "50%", ("209742", "lev_money", "net", "secondary"), "Low"),
        score_fire("P4", "1170E1 lev_money gross_short secondary_no_vx Low", "fires", "45%", ("1170E1", "lev_money", "gross_short", "secondary_no_vx"), "Low"),
        {
            **score_fire("P5a", "H10_JPY log_change primary Low", "does_not_fire", "60%", ("H10_JPY", "fx", "log_change", "primary"), "Low"),
            "detail": (
                "missing 2026-11-24 H.10" if res_map[("H10_JPY", "fx", "log_change", "primary")]["change"] == ""
                else f"start_used={s_used} end_used={e_used} chg={res_map[('H10_JPY', 'fx', 'log_change', 'primary')]['change']} pct={res_map[('H10_JPY', 'fx', 'log_change', 'primary')]['percentile']}"
            ),
        },
        score_fire("P5b", "097741 lev_money net primary High", "does_not_fire", "55%", ("097741", "lev_money", "net", "primary"), "High"),
        score_fire("P6", "UST_ALL6 lev_money gross_short_10yeq_bn primary Low", "does_not_fire", "70%", ("UST_ALL6", "lev_money", "gross_short_10yeq_bn", "primary"), "Low"),
        seller_row,
    ]

    # Checks
    present_codes = [c for c, _ in CODES if by_code[c]]
    missing_codes = [c for c, _ in CODES if not by_code[c]]
    date_sets = {frozenset(by_code[c].keys()) for c in present_codes}
    spec_ok = os.path.exists(spec_path) and ("Version 2" in open(spec_path, encoding="utf-8").read())
    ys_max_ok = all(d <= YARDSTICK_END_MAX for d in yardstick_dates_seen)
    pri_excl_ok = PRIMARY_END not in yardstick_dates_seen
    assert ys_max_ok, f"Yardstick exceeded {YARDSTICK_END_MAX}: {max(yardstick_dates_seen)}"
    assert pri_excl_ok, f"Primary end {PRIMARY_END} leaked into yardstick"

    checks_rows = [
        {"check": "unique_code_date", "status": "PASS" if dup_count == 0 else "FAIL", "reason": f"duplicates={dup_count}"},
        {"check": "all_11_codes", "status": "PASS" if not missing_codes else "FAIL", "reason": f"present={len(present_codes)} missing={missing_codes}"},
        {"check": "identical_report_dates", "status": "PASS" if len(date_sets) == 1 else "WARN", "reason": f"distinct_date_sets={len(date_sets)}"},
        {"check": "no_negative_positions", "status": "PASS" if neg_count == 0 else "FAIL", "reason": f"negative_values={neg_count}"},
        {"check": "spec_v2_present", "status": "PASS" if spec_ok else "FAIL", "reason": "Version 2 marker checked"},
        {"check": "yardstick_end_bound", "status": "PASS" if ys_max_ok else "FAIL", "reason": f"max_end={max(yardstick_dates_seen) if yardstick_dates_seen else 'none'} <= {YARDSTICK_END_MAX}"},
        {"check": "primary_end_excluded", "status": "PASS" if pri_excl_ok else "FAIL", "reason": f"{PRIMARY_END} not in yardstick"},
        {"check": "h10_jpy_present", "status": "PASS" if h10_map else "WARN", "reason": f"h10_days={len(h10_map)}"},
        {"check": "mof_week_descriptive", "status": "PASS" if mof_ok else "WARN", "reason": "parsed" if mof_ok else "unparsed"},
    ]

    os.makedirs(data_dir, exist_ok=True)
    _write_csv(os.path.join(data_dir, "results.csv"), ["code", "class", "field", "window", "start", "end", "change", "percentile", "n", "sd", "flag"], results_rows)
    _write_csv(os.path.join(data_dir, "registration_score.csv"), ["id", "rule", "prediction", "credence", "status", "outcome", "detail"], reg_rows)
    _write_csv(os.path.join(data_dir, "checks.csv"), ["check", "status", "reason"], checks_rows)

    if not quiet:
        print("MoF week.csv (descriptive, last 6 rows):" if mof_ok else "MoF week.csv: unparsed")
        for ln in mof_lines:
            print("  ", ln)
        print("Checks:", ", ".join(f"{c['check']}={c['status']}" for c in checks_rows))

    return results_rows, reg_rows, checks_rows


def _write_csv(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


# --------------------------------------------------------------------------------------------------
# SELFTEST (synthetic fixtures only, no network)
# --------------------------------------------------------------------------------------------------
def _make_synthetic_dataset(td, include_nov24=True, include_h10_nov24=True, lev_most_negative=True, lev_fires=True):
    # Generate weekly Tuesday dates from 2018-01-02 to 2026-11-24 (with a Monday-dated holiday report)
    dates = []
    d = dt.date(2018, 1, 2)
    end_d = dt.date(2026, 11, 24) if include_nov24 else dt.date(2026, 11, 17)
    while d <= end_d:
        # Simulate CFTC Monday-dated report for 2025-11-11 -> 2025-11-10
        if d == dt.date(2025, 11, 11):
            dates.append("2025-11-10")
        else:
            dates.append(d.isoformat())
        d += dt.timedelta(days=7)

    raw_cols = [
        "report_date_as_yyyy_mm_dd", "cftc_contract_market_code", "open_interest_all",
        "dealer_positions_long_all", "dealer_positions_short_all",
        "asset_mgr_positions_long", "asset_mgr_positions_short",
        "lev_money_positions_long", "lev_money_positions_short",
        "other_rept_positions_long", "other_rept_positions_short",
        "nonrept_positions_long_all", "nonrept_positions_short_all",
    ]
    rows = []
    for code, _ in CODES:
        for i, ds in enumerate(dates):
            # Deterministic smooth pattern + spike on Nov 24 if requested
            lm_l, lm_s = 10000 + (i % 10) * 100, 10000
            am_l, am_s = 20000 + (i % 7) * 50, 15000
            dl_l, dl_s = 5000, 5000
            ot_l, ot_s = 3000, 3000
            nr_l, nr_s = 2000, 2000
            if ds == PRIMARY_END:
                if lev_fires:
                    lm_l = 5000  # big drop in net (-5000)
                else:
                    lm_l = 12000  # rise (+2000) -> INCONCLUSIVE
                if not lev_most_negative:
                    am_l = 1000  # Asset Manager drops more than Leveraged Funds
            rows.append({
                "report_date_as_yyyy_mm_dd": ds,
                "cftc_contract_market_code": code,
                "open_interest_all": str(lm_l + am_l + dl_l + ot_l + nr_l),
                "dealer_positions_long_all": str(dl_l), "dealer_positions_short_all": str(dl_s),
                "asset_mgr_positions_long": str(am_l), "asset_mgr_positions_short": str(am_s),
                "lev_money_positions_long": str(lm_l), "lev_money_positions_short": str(lm_s),
                "other_rept_positions_long": str(ot_l), "other_rept_positions_short": str(ot_s),
                "nonrept_positions_long_all": str(nr_l), "nonrept_positions_short_all": str(nr_s),
            })
    _write_csv(os.path.join(td, "raw_tff.csv"), raw_cols, rows)

    # Synthetic H.10 JPY (skip 2026-11-10 to test nearest-earlier rule on start date)
    h10_lines = [
        '"Series Description","Japan -- Spot Exchange Rate, Yen/US$"',
        '"Unit:","Currency:_Per_USD"',
        '"Multiplier:","1"',
        '"Currency:","JPY"',
        f'"Unique Identifier: ","{H10_SERIES_ID}"',
        '"Time Period","RXI_N.B.JA"',
    ]
    hd = dt.date(2018, 1, 2)
    h_end = dt.date(2026, 11, 24) if include_h10_nov24 else dt.date(2026, 11, 23)
    while hd <= h_end:
        if hd.weekday() < 5:
            val = "ND" if hd == dt.date(2026, 11, 10) else f"{150.0 + (hd.toordinal() % 5):.2f}"
            h10_lines.append(f"{hd.isoformat()},{val}")
        hd += dt.timedelta(days=1)
    with open(os.path.join(td, "raw_h10_jpy.csv"), "w", encoding="utf-8") as f:
        f.write("\n".join(h10_lines) + "\n")

    with open(os.path.join(td, "raw_mof_week.csv"), "w", encoding="utf-8") as f:
        f.write("Week,Foreign_Bonds_Net\n2026-11-14,100.5\n2026-11-21,-50.2\n")


def run_selftest():
    guards = []

    def check(name, fn):
        try:
            ok, msg = fn()
            guards.append((name, bool(ok), msg))
        except Exception as e:
            guards.append((name, False, f"exception: {e}"))

    # 1. Percentile computation
    def g_percentile():
        ys = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        pct, n, sd, flag = compute_score(ys, 1)
        assert n == 10 and abs(pct - 0.1) < 1e-12 and flag == "Low"
        pct2, _, _, flag2 = compute_score(ys, 9)
        assert abs(pct2 - 0.9) < 1e-12 and flag2 == "High"
        return True, "pct=0.1000 Low, 0.9000 High"

    # 2. Gap rule (13/14/15 kept, 12/16 dropped; Monday-dated report kept)
    def g_gap():
        base = dt.date(2024, 1, 2)  # Tuesday
        ds = [
            base.isoformat(),
            (base + dt.timedelta(days=12)).isoformat(),
            (base + dt.timedelta(days=13)).isoformat(),  # Monday-dated report (+13d)
            (base + dt.timedelta(days=14)).isoformat(),
            (base + dt.timedelta(days=15)).isoformat(),
            (base + dt.timedelta(days=16)).isoformat(),
        ]
        # Only pairs starting from base: gaps 13 (Monday), 14, 15 kept; 12, 16 dropped
        w = qualifying_windows(ds, "two_week")
        gaps = [(dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days for a, b in w if a == ds[0]]
        assert gaps == [13, 14, 15], f"got {gaps}"
        assert (base.isoformat(), (base + dt.timedelta(days=13)).isoformat()) in w
        return True, f"gaps={gaps} (Monday +13d kept)"

    # 3. VX settlement Nov 2026 = 2026-11-18 and expiry-window exclusion
    def g_vx():
        wed = vx_settlement_wednesday(2026, 11).isoformat()
        assert wed == "2026-11-18", f"got {wed}"
        ds = ["2026-11-03", "2026-11-10", "2026-11-17"]
        # Use 2026-11-18 exclusion? No, 2026-11-10..2026-11-17 does not contain 2026-11-18;
        # test an earlier month: Oct 2026 3rd Fri = Nov 20, -30d = 2026-10-21
        oct_wed = vx_settlement_wednesday(2026, 10).isoformat()
        assert oct_wed == "2026-10-21", f"got {oct_wed}"
        ds2 = ["2026-10-13", "2026-10-20", "2026-10-27"]
        w = qualifying_windows(ds2, "one_week", exclude_dates={oct_wed})
        assert ("2026-10-20", "2026-10-27") not in w and ("2026-10-13", "2026-10-20") in w
        return True, f"nov26_vx={wed}, oct26_vx_excluded={oct_wed}"

    # 4. P6 10y-equivalent arithmetic
    def g_p6():
        by = {c: {"2026-11-10": {"lev_money_positions_short": 1000 if c == "043602" else 0}} for c in TREASURY_DV01}
        got = treasury_p6_10yeq_bn(by, "2026-11-10")
        exp = 1000 * 63.0 / (par_mod_duration(4.0, 10) * 1e-4) / 1e9
        assert abs(got - exp) < 1e-12
        return True, f"1000x043602={got:.6f}bn"

    # 5. PENDING when end row missing + P5a PENDING & nearest-earlier start
    def g_pending_and_p5a():
        with tempfile.TemporaryDirectory() as td:
            _make_synthetic_dataset(td, include_nov24=False, include_h10_nov24=False)
            _, reg, _ = build_all(td, quiet=True)
            rmap = {r["id"]: r for r in reg}
            assert rmap["P1"]["status"] == "PENDING"
            assert rmap["P5a"]["status"] == "PENDING"
            assert rmap["P1s"]["status"] != "PENDING"
        with tempfile.TemporaryDirectory() as td:
            _make_synthetic_dataset(td, include_nov24=True, include_h10_nov24=True)
            _, reg, _ = build_all(td, quiet=True)
            rmap = {r["id"]: r for r in reg}
            assert rmap["P5a"]["status"] != "PENDING"
            assert "start_used=2026-11-09" in rmap["P5a"]["detail"], rmap["P5a"]["detail"]
        return True, "PENDING & nearest-earlier start verified"

    # 6. Seller rule both ways & INCONCLUSIVE wording
    def g_seller_and_inconclusive():
        with tempfile.TemporaryDirectory() as td:
            _make_synthetic_dataset(td, lev_most_negative=True, lev_fires=True)
            _, reg, _ = build_all(td, quiet=True)
            rmap = {r["id"]: r for r in reg}
            assert rmap["SELLER"]["status"] == "MET", rmap["SELLER"]
            assert rmap["P1"]["status"] == "FIRED", rmap["P1"]
        with tempfile.TemporaryDirectory() as td:
            _make_synthetic_dataset(td, lev_most_negative=False, lev_fires=False)
            _, reg, _ = build_all(td, quiet=True)
            rmap = {r["id"]: r for r in reg}
            assert rmap["SELLER"]["status"] == "NOT_MET", rmap["SELLER"]
            assert rmap["P1"]["status"] == "INCONCLUSIVE", rmap["P1"]
            assert rmap["P3"]["status"] == "INCONCLUSIVE", rmap["P3"]
        return True, "SELLER MET/NOT_MET & INCONCLUSIVE verified"

    # 7. Byte-identical build on two runs
    def g_byte_identical():
        with tempfile.TemporaryDirectory() as td:
            _make_synthetic_dataset(td)
            build_all(td, quiet=True)
            h1 = {fn: hashlib.sha256(open(os.path.join(td, fn), "rb").read()).hexdigest() for fn in ("results.csv", "registration_score.csv", "checks.csv")}
            build_all(td, quiet=True)
            h2 = {fn: hashlib.sha256(open(os.path.join(td, fn), "rb").read()).hexdigest() for fn in ("results.csv", "registration_score.csv", "checks.csv")}
            assert h1 == h2
        return True, "sha256 identical across 2 builds"

    # 8. Mutants (must fail when enabled)
    def g_mutant_gap():
        with mutant("gap_12_16"):
            try:
                g_gap()
                return False, "missed gap_12_16"
            except AssertionError:
                return True, "caught gap_12_16"

    def g_mutant_vx():
        with mutant("vx_offset_29"):
            try:
                g_vx()
                return False, "missed vx_offset_29"
            except AssertionError:
                return True, "caught vx_offset_29"

    def g_mutant_inconclusive():
        with mutant("no_inconclusive"):
            try:
                g_seller_and_inconclusive()
                return False, "missed no_inconclusive"
            except AssertionError:
                return True, "caught no_inconclusive"

    def g_mutant_pct():
        with mutant("pct_strict_lt"):
            try:
                g_percentile()
                return False, "missed pct_strict_lt"
            except AssertionError:
                return True, "caught pct_strict_lt"

    for name, fn in [
        ("percentile", g_percentile),
        ("gap_rule", g_gap),
        ("vx_settlement", g_vx),
        ("p6_10yeq", g_p6),
        ("pending_and_p5a", g_pending_and_p5a),
        ("seller_and_inconclusive", g_seller_and_inconclusive),
        ("byte_identical", g_byte_identical),
        ("mutant_gap_12_16", g_mutant_gap),
        ("mutant_vx_offset_29", g_mutant_vx),
        ("mutant_no_inconclusive", g_mutant_inconclusive),
        ("mutant_pct_strict_lt", g_mutant_pct),
    ]:
        check(name, fn)

    all_ok = all(ok for _, ok, _ in guards)
    for name, ok, msg in guards:
        print(f"{'PASS' if ok else 'FAIL'} {name}: {msg}")
    return 0 if all_ok else 1


def main():
    ap = argparse.ArgumentParser(description="Selloff positioning pre-registered test")
    ap.add_argument("mode", choices=["selftest", "fetch", "build"])
    args = ap.parse_args()
    if args.mode == "selftest":
        raise SystemExit(run_selftest())
    if args.mode == "fetch":
        fetch_all()
        return
    if args.mode == "build":
        build_all()
        return


if __name__ == "__main__":
    main()
