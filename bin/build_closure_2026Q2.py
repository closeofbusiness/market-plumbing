#!/usr/bin/env python3
"""
build_closure_2026Q2.py

Refreshes the N2c "funding closure" table (2026-08-29-N2c-The-Funding-Closure.md,
section 2: US Treasury absorption by sector, Z.1 flows) on the Federal Reserve's
Z.1 release of 11 Sep 2026 (2026:Q2 data), and separately assembles the equity
side (section 4: who holds/issues US corporate equities) from Z.1 F51.1.t data
already pulled for this release (project's data/z1_equity_netbuyers/*_2026Q2.csv,
built by bin/z1_equity_netbuyers.py, supervisor-verified 11 Sep 2026).

TREASURY-TABLE METHOD (this run)
    1. Fetched https://www.federalreserve.gov/releases/z1/ -- confirmed release
       date "September 11, 2026", vintage "2026:Q2" (matches the brief).
    2. Fetched the single bulk CSV package
       https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip
       ONCE (8,336,582 bytes) and extracted locally (no further HTTP requests):
         csv/F3_2_t_tu.csv + data_dictionary/F3_2_t_tu.txt   (F3.2.t "Treasury
             securities" -- the cross-sector instrument table; NSA quarterly
             "_tu" flow series, matching the June-vintage pull's convention)
         csv/S122_t_tu.csv + .txt   (S122.t "Private depository institutions" --
             carries the Banks aggregate line, which F3.2.t does not publish)
         csv/S129_t_tu.csv + .txt   (S129.t "Private and public pension funds" --
             carries the Pensions aggregate line, which F3.2.t does not publish)
    3. Every series code used below was cross-checked BY DESCRIPTION TEXT against
       this release's own data dictionaries (not assumed stable from the doc).

GROUPING -- validated first against the June/2026Q1-vintage raw pull
    (data/vintages/z1_closure/{z1_closure_raw,z1_closure_extra}.json), i.e. this
    script's grouping reproduces the ALREADY-PUBLISHED June-vintage table before
    being pointed at the new vintage. See validate_june_vintage.py in this same
    directory for that check (8 of 9 rows reproduce the published doc exactly;
    the 9th -- "State & local govts, GSEs, corporates, other" -- reproduces to
    within ~$5-10bn/yr; see CAVEATS below and the final report for why).

TWO CODES COULD NOT BE REPRODUCED VERBATIM (both resolved to like-for-like
replacements, confirmed by description text, not by guessing):
    - Broker-dealers: the June pull's code FU663061103.Q does not exist anywhere
      in the 11-Sep-2026 release's data dictionaries. The only Z.1 series for
      "Security brokers and dealers; Treasury securities; asset" in this release
      is FU663061105.Q (appears in both F3.2.t and S125s3.t). Used that instead.
    - Insurers: the June pull's code FU523061105.Q ("Insurers", quarterly
      obs 1946-2026Q1 in the June pull) is NOT present in any QUARTERLY table in
      this release's bulk CSV package -- it exists only in S128.i.a, an ANNUAL
      integrated-account table. The bulk package (the method this brief
      specifies) has no quarterly combined "Insurance companies" line this
      release. Replaced with the sum of its two quarterly published components,
      both confirmed in F3.2.t: Property-casualty insurers (FU513061105.Q) +
      Life insurers (FU543061105.Q).

FREE PUBLIC SOURCE, POLITE FETCHING
    Only https://www.federalreserve.gov contacted, 2 requests total (release
    page + one bulk zip), User-Agent
    "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)",
    no email address anywhere, >=0.6s between requests (well under 2 req/sec).
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
PROJECT = Path("/Users/martinschroeder/Dropbox/31 - Claude Cowork/Work/2026.08 - Third Derivative Research")

JUNE_RAW = PROJECT / "data/vintages/z1_closure/z1_closure_raw.json"
JUNE_EXTRA = PROJECT / "data/vintages/z1_closure/z1_closure_extra.json"
EQUITY_Q = PROJECT / "data/z1_equity_netbuyers/netbuyers_quarterly_2026Q2.csv"

OUT_CLOSURE = HERE / "closure_2026Q2.csv"
OUT_REVISIONS = HERE / "revisions.csv"


def load_wide_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return {row["date"]: row for row in csv.DictReader(f)}


def to_bn(raw_val):
    if raw_val is None:
        return None
    raw_val = raw_val.strip()
    if raw_val in ("", "ND"):
        return None
    try:
        return float(raw_val) / 1000.0
    except ValueError:
        return None


# ---- September (2026:Q2) vintage: load the three tables fetched this run ----
sep_tables = {
    "F3_2_t_tu": load_wide_csv(RAW / "F3_2_t_tu.csv"),
    "S122_t_tu": load_wide_csv(RAW / "S122_t_tu.csv"),
    "S129_t_tu": load_wide_csv(RAW / "S129_t_tu.csv"),
}


def sep_val(code, quarter):
    for tbl in sep_tables.values():
        row = tbl.get(quarter)
        if row and code in row:
            return to_bn(row[code])
    return None


def sep_annual(code, year):
    total, n = 0.0, 0
    for q in (1, 2, 3, 4):
        v = sep_val(code, f"{year}:Q{q}")
        if v is not None:
            total += v
            n += 1
    return total if n == 4 else (total if n else None)


# ---- June (2026:Q1) vintage: the raw per-series JSON pull behind the doc ----
june_series = {**json.load(open(JUNE_RAW)), **json.load(open(JUNE_EXTRA))}


def june_val(code, date_iso):
    v = june_series.get(code)
    if not v or not v.get("obs"):
        return None
    raw = v["obs"].get(date_iso)
    return raw / 1000.0 if raw is not None else None


def june_annual(code, year):
    v = june_series.get(code)
    if not v or not v.get("obs"):
        return None
    total, n = 0.0, 0
    for date, val in v["obs"].items():
        if date.startswith(str(year)) and val is not None:
            total += val
            n += 1
    return total / 1000.0 if n else None


QEND = {1: "-03-31", 2: "-06-30", 3: "-09-30", 4: "-12-31"}


def june_val_by_quarter(code, year, q):
    return june_val(code, f"{year}{QEND[q]}")


# ---- Row definitions: (row label, [(component_label, code), ...]) ----
# Every code below is used IDENTICALLY for both vintages except the two
# substitutions documented in the module docstring (flagged per-component).
ROWS = [
    ("Money market funds", [("Money market funds", "FU633061105.Q")]),
    ("Households + nonprofits", [
        ("Households + nonprofits", "FU153061105.Q"),
        ("Hedge funds, domestic [now broken out separately; June had no separate line -- was already inside the June household residual; added here to preserve the doc's own 'incl. hedge funds' definition]", "FU623061103.Q"),
    ]),
    ("Rest of world", [("Rest of world", "FU263061105.Q")]),
    ("Federal Reserve", [("Federal Reserve (central bank)", "FU713061103.Q")]),
    ("Banks (private depository)", [("Private depository institutions (S122 aggregate)", "FU703061105.Q")]),
    ("Mutual funds + ETFs + closed-end", [
        ("Mutual funds", "FU653061105.Q"),
        ("ETFs", "FU563061103.Q"),
        ("Closed-end funds", "FU553061103.Q"),
    ]),
    ("Insurers + pensions (incl. S&L retirement)", [
        ("Property-casualty insurers [replaces June's combined FU523061105]", "FU513061105.Q"),
        ("Life insurers [replaces June's combined FU523061105]", "FU543061105.Q"),
        ("Pensions (S129 aggregate)", "FU593061105.Q"),
        ("State & local govt employee DB pension funds", "FU223061143.Q"),
    ]),
    ("Broker-dealers", [("Security brokers and dealers [FU663061105, June used FU663061103]", "FU663061105.Q")]),
    ("State & local govts, GSEs, corporates, other", [
        ("GSEs", "FU403061105.Q"),
        ("Nonfinancial corporate business", "FU103061103.Q"),
        ("State & local governments", "FU213061103.Q"),
        ("Other financial business (CCP-held Treasuries)", "FU503061123.Q"),
        ("Issuers of asset-backed securities", "FU673061103.Q"),
        ("Holding companies", "FU733061103.Q"),
    ]),
]
TOTAL_ROW = ("Net issuance (Federal government liability, = all-sector absorption)", "FU313161105.Q")
CHECK_ROW = ("All-sector check (holder side, Treasury securities asset)", "FU893061105.Q")

# June-only codes that map to the same component slot but under a different ID
JUNE_CODE_OVERRIDE = {
    "FU513061105.Q": "FU523061105.Q",  # June: single combined "Insurers" line
    "FU543061105.Q": "FU523061105.Q",  # (added once below, not twice -- see logic)
    "FU663061105.Q": "FU663061103.Q",
}

PERIODS_ANNUAL = [2023, 2024, 2025]
Q_2026 = [("2026Q1", 1), ("2026Q2", 2)]

closure_rows_out = []
revision_rows = []

# Track, for the combined "Insurers" June override, that it should be counted
# ONCE per period (as a single component), not once per P&C and once per Life.
insurer_replacement_codes = {"FU513061105.Q", "FU543061105.Q"}

for row_label, components in ROWS:
    sep_year_vals = {}
    june_year_vals = {}
    for year in PERIODS_ANNUAL:
        s_tot, j_tot = 0.0, 0.0
        j_counted_insurer_combo = False
        for _, code in components:
            s_tot += sep_annual(code, year) or 0.0
            if code in insurer_replacement_codes:
                if not j_counted_insurer_combo:
                    j_tot += june_annual("FU523061105.Q", year) or 0.0
                    j_counted_insurer_combo = True
            else:
                j_code = JUNE_CODE_OVERRIDE.get(code, code)
                j_tot += june_annual(j_code, year) or 0.0
        sep_year_vals[year] = round(s_tot, 1)
        june_year_vals[year] = round(j_tot, 1)

    sep_q_vals = {}
    june_q_vals = {}
    for label, qn in Q_2026:
        s_tot, j_tot = 0.0, 0.0
        j_counted_insurer_combo = False
        for _, code in components:
            s_tot += sep_val(code, f"2026:Q{qn}") or 0.0
            if label == "2026Q1":
                if code in insurer_replacement_codes:
                    if not j_counted_insurer_combo:
                        j_tot += (june_val_by_quarter("FU523061105.Q", 2026, qn) or 0.0)
                        j_counted_insurer_combo = True
                else:
                    j_code = JUNE_CODE_OVERRIDE.get(code, code)
                    j_tot += june_val_by_quarter(j_code, 2026, qn) or 0.0
        sep_q_vals[label] = round(s_tot, 1)
        if label == "2026Q1":
            june_q_vals[label] = round(j_tot, 1)

    closure_rows_out.append({
        "market": "Treasury",
        "row": row_label,
        "2023": sep_year_vals[2023],
        "2024": sep_year_vals[2024],
        "2025": sep_year_vals[2025],
        "2026Q1": sep_q_vals["2026Q1"],
        "2026Q2": sep_q_vals["2026Q2"],
    })

    # revisions at the ROW level for 2023/2024/2025/2026Q1 (periods that exist in both vintages)
    for year in PERIODS_ANNUAL:
        jv, sv = june_year_vals[year], sep_year_vals[year]
        if jv is not None and sv is not None and round(jv, 1) != round(sv, 1):
            revision_rows.append({
                "series": row_label, "period": str(year), "component_of": "",
                "june_value_bn": jv, "september_value_bn": sv,
                "change_bn": round(sv - jv, 1),
            })
    jv, sv = june_q_vals.get("2026Q1"), sep_q_vals.get("2026Q1")
    if jv is not None and sv is not None and round(jv, 1) != round(sv, 1):
        revision_rows.append({
            "series": row_label, "period": "2026Q1", "component_of": "",
            "june_value_bn": jv, "september_value_bn": sv,
            "change_bn": round(sv - jv, 1),
        })

# Total + check rows
for label, code in (TOTAL_ROW, CHECK_ROW):
    sep_year_vals = {y: round(sep_annual(code, y) or 0.0, 1) for y in PERIODS_ANNUAL}
    sep_q_vals = {lab: round(sep_val(code, f"2026:Q{qn}") or 0.0, 1) for lab, qn in Q_2026}
    june_year_vals = {y: round(june_annual(code, y) or 0.0, 1) for y in PERIODS_ANNUAL}
    june_q1 = round(june_val_by_quarter(code, 2026, 1) or 0.0, 1)

    closure_rows_out.append({
        "market": "Treasury", "row": label,
        "2023": sep_year_vals[2023], "2024": sep_year_vals[2024], "2025": sep_year_vals[2025],
        "2026Q1": sep_q_vals["2026Q1"], "2026Q2": sep_q_vals["2026Q2"],
    })
    for year in PERIODS_ANNUAL:
        jv, sv = june_year_vals[year], sep_year_vals[year]
        if jv != sv:
            revision_rows.append({
                "series": label, "period": str(year), "component_of": "",
                "june_value_bn": jv, "september_value_bn": sv, "change_bn": round(sv - jv, 1),
            })
    if june_q1 != sep_q_vals["2026Q1"]:
        revision_rows.append({
            "series": label, "period": "2026Q1", "component_of": "",
            "june_value_bn": june_q1, "september_value_bn": sep_q_vals["2026Q1"],
            "change_bn": round(sep_q_vals["2026Q1"] - june_q1, 1),
        })

# Sum-of-9-rows check (does the refreshed table close?)
sum9 = {p: 0.0 for p in ["2023", "2024", "2025", "2026Q1", "2026Q2"]}
for r in closure_rows_out:
    if r["row"] not in (TOTAL_ROW[0], CHECK_ROW[0]):
        for p in sum9:
            sum9[p] += r[p]
closure_rows_out.append({
    "market": "Treasury", "row": "[diagnostic] sum of 9 buyer rows",
    **{p: round(v, 1) for p, v in sum9.items()},
})

# ---------------------------------------------------------------------------
# EQUITY SIDE -- reuse already-pulled, already-verified F51.1.t data (no new
# HTTP request: data/z1_equity_netbuyers/netbuyers_quarterly_2026Q2.csv, built
# by bin/z1_equity_netbuyers.py, 2026-09-11, this same 2026Q2 Z.1 release).
# Re-aggregated here to calendar years / 2026Q1 / 2026Q2 to match the N2c
# doc's section-4 presentation. June-vintage comparison values for the three
# series revised are taken from data/series.tsv rows dated 2026-09-11T20:25Z,
# which record both the June and September figures for 2025 explicitly.
# ---------------------------------------------------------------------------
equity_quarterly = {}
with EQUITY_Q.open(newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        equity_quarterly.setdefault(row["series_code"], {})[row["quarter"]] = {
            "sector": row["sector"], "role": row["role"],
            "flow_bn": float(row["flow_bn"]) if row["flow_bn"] not in ("", None) else None,
        }

EQUITY_ROWS = [
    ("All sectors (total net issuance)", "total", "FU893064105.Q"),
    ("Nonfinancial corporate business (issuer, net buybacks)", "issuer", "FU103164105.Q"),
    ("Households and nonprofit organizations (holder)", "holder", "FU153064105.Q"),
    ("Exchange-traded funds (holder)", "holder", "FU563064100.Q"),
    ("Rest of the world (holder)", "holder", "FU263064105.Q"),
    ("Mutual funds (holder)", "holder", "FU653064100.Q"),
    ("Hedge funds, domestic (holder)", "holder", "FU623064105.Q"),
]


def equity_annual(code, year):
    total, n = 0.0, 0
    for q in (1, 2, 3, 4):
        cell = equity_quarterly.get(code, {}).get(f"{year}:Q{q}")
        if cell and cell["flow_bn"] is not None:
            total += cell["flow_bn"]
            n += 1
    return round(total, 1) if n == 4 else None


def equity_q(code, year, qn):
    cell = equity_quarterly.get(code, {}).get(f"{year}:Q{qn}")
    return round(cell["flow_bn"], 1) if cell and cell["flow_bn"] is not None else None


for label, role, code in EQUITY_ROWS:
    closure_rows_out.append({
        "market": "Equity",
        "row": label,
        "2023": equity_annual(code, 2023),
        "2024": equity_annual(code, 2024),
        "2025": equity_annual(code, 2025),
        "2026Q1": equity_q(code, 2026, 1),
        "2026Q2": equity_q(code, 2026, 2),
    })

# Equity revisions: from series.tsv's own recorded June-vs-September figures
# (2025 annual only -- that is what series.tsv captured on 2026-09-11).
EQUITY_REVISIONS_2025 = [
    ("Nonfinancial corporate business (issuer, net buybacks)", "2025", -304.0, -348.2),
    ("Rest of the world (holder)", "2025", 643.7, 646.7),
    ("Households and nonprofit organizations (holder)", "2025", 863.5, 824.0),
]
for series, period, jv, sv in EQUITY_REVISIONS_2025:
    revision_rows.append({
        "series": series, "period": period, "component_of": "",
        "june_value_bn": jv, "september_value_bn": sv, "change_bn": round(sv - jv, 1),
    })

# NFC net equity issuance, 2026Q1 -- the doc (June/Q1 vintage) published +$31bn
# for this quarter; recomputed here from the September-vintage F51.1.t data.
_nfc_q1_sep = equity_q("FU103164105.Q", 2026, 1)
if _nfc_q1_sep is not None and _nfc_q1_sep != 31.0:
    revision_rows.append({
        "series": "Nonfinancial corporate business (issuer, net buybacks)", "period": "2026Q1", "component_of": "",
        "june_value_bn": 31.0, "september_value_bn": _nfc_q1_sep,
        "change_bn": round(_nfc_q1_sep - 31.0, 1),
    })

# ---- Granular COMPONENT-level revisions for the two multi-code Treasury
# rows where June's raw pull happened to carry every component individually
# (Mutual funds+ETFs+CEF, and the State/local+GSE+corporate+other bucket) --
# so no revision is hidden inside a row-level aggregate for these two.
COMPONENT_REVISION_CODES = {
    "Mutual funds + ETFs + closed-end": [
        ("Mutual funds", "FU653061105.Q"), ("ETFs", "FU563061103.Q"), ("Closed-end funds", "FU553061103.Q"),
    ],
    "State & local govts, GSEs, corporates, other": [
        ("GSEs", "FU403061105.Q"), ("Nonfinancial corporate business (Treasury holder)", "FU103061103.Q"),
        ("State & local governments", "FU213061103.Q"), ("Other financial business (CCP-held)", "FU503061123.Q"),
        ("Issuers of asset-backed securities", "FU673061103.Q"), ("Holding companies", "FU733061103.Q"),
    ],
}
for row_name, comps in COMPONENT_REVISION_CODES.items():
    for comp_label, code in comps:
        for year in PERIODS_ANNUAL:
            jv = june_annual(code, year)
            sv = sep_annual(code, year)
            jv = round(jv, 1) if jv is not None else None
            sv = round(sv, 1) if sv is not None else None
            if jv is not None and sv is not None and jv != sv:
                revision_rows.append({
                    "series": comp_label, "period": str(year), "component_of": row_name,
                    "june_value_bn": jv, "september_value_bn": sv, "change_bn": round(sv - jv, 1),
                })
        jv = june_val_by_quarter(code, 2026, 1)
        sv = sep_val(code, "2026:Q1")
        jv = round(jv, 1) if jv is not None else None
        sv = round(sv, 1) if sv is not None else None
        if jv is not None and sv is not None and jv != sv:
            revision_rows.append({
                "series": comp_label, "period": "2026Q1", "component_of": row_name,
                "june_value_bn": jv, "september_value_bn": sv, "change_bn": round(sv - jv, 1),
            })

# ---- write outputs ----
with OUT_CLOSURE.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["market", "row", "2023", "2024", "2025", "2026Q1", "2026Q2"])
    w.writeheader()
    for r in closure_rows_out:
        w.writerow(r)

with OUT_REVISIONS.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["series", "component_of", "period", "june_value_bn", "september_value_bn", "change_bn"])
    w.writeheader()
    for r in sorted(revision_rows, key=lambda r: (r["period"], r["series"])):
        w.writerow(r)

print(f"wrote {OUT_CLOSURE} ({len(closure_rows_out)} rows)")
print(f"wrote {OUT_REVISIONS} ({len(revision_rows)} rows)")

print("\n=== TREASURY CLOSURE TABLE, $bn ===")
hdr = f"{'row':55s} {'2023':>9s} {'2024':>9s} {'2025':>9s} {'2026Q1':>9s} {'2026Q2':>9s}"
print(hdr)
for r in closure_rows_out:
    if r["market"] == "Treasury":
        print(f"{r['row'][:55]:55s} {r['2023']:>9} {r['2024']:>9} {r['2025']:>9} {r['2026Q1']:>9} {r['2026Q2']:>9}")

print("\n=== EQUITY TABLE, $bn ===")
print(hdr)
for r in closure_rows_out:
    if r["market"] == "Equity":
        print(f"{r['row'][:55]:55s} {r['2023']:>9} {r['2024']:>9} {r['2025']:>9} {r['2026Q1']:>9} {r['2026Q2']:>9}")

print("\n=== REVISIONS (June vintage value -> September vintage value) ===")
for r in sorted(revision_rows, key=lambda r: (r["period"], r["series"])):
    tag = f"  [component of: {r['component_of']}]" if r["component_of"] else ""
    print(f"{r['period']:8s} {r['series'][:55]:55s} {r['june_value_bn']:>10} -> {r['september_value_bn']:>10}  (change {r['change_bn']:+.1f}){tag}")
