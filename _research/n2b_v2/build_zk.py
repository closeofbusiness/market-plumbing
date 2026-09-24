#!/usr/bin/env python3
"""N2b v2: z_k = W/(W+D) on wider perimeters (W1..W3) and stricter denominators (D1..D4),
at every quarter-end 2021Q4 .. latest quarter with all inputs (C-070: full path, no endpoint pairs).

All figures come from files on disk (Dropbox data/ or this scratchpad); nothing from memory.
Units: every input is converted to USD billions BEFORE use; the source unit is recorded in UNITS below.
"""
import csv, os, sys, math
from collections import OrderedDict

SCR = "/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/n2b_v2"
DBX = "/Users/martinschroeder/Dropbox/31 - Claude Cowork/Work/2026.08 - Third Derivative Research/data"
HIST = os.path.join(DBX, "history")
ALF  = os.path.join(DBX, "vintages", "alfred", "alf_M2SL_2026-08-15.csv")
OUT  = os.path.join(SCR, "zk_v2.csv")

# ---- sources / reproduce URLs / units (stated exactly as source states them) ----
SOURCES = {
 "mmf_treasury_repo_bn":       ("OFR MMF Monitor MMF-MMF_RP_T_TOT-M (N-MFP, month-end, all US MMFs)", "https://data.financialresearch.gov/mmf/v1/series/full?mnemonic=MMF-MMF_RP_T_TOT-M", "$bn as stored in data/history (OFR reports $ millions; file already in bn)"),
 "mmf_agency_repo_bn":         ("OFR MMF Monitor MMF-MMF_RP_AG_TOT-M", "https://data.financialresearch.gov/mmf/v1/series/full?mnemonic=MMF-MMF_RP_AG_TOT-M", "$bn"),
 "mmf_repo_other_collateral_bn":("OFR MMF Monitor MMF-MMF_RP_OA_TOT-M", "https://data.financialresearch.gov/mmf/v1/series/full?mnemonic=MMF-MMF_RP_OA_TOT-M", "$bn"),
 "mmf_repo_with_fed_bn":       ("OFR MMF Monitor MMF-MMF_RP_wFR-M", "https://data.financialresearch.gov/mmf/v1/series/full?mnemonic=MMF-MMF_RP_wFR-M", "$bn"),
 "mmf_bank_related_assets_bn": ("OFR MMF Monitor MMF-MMF_BRA_TOT-M", "https://data.financialresearch.gov/mmf/v1/series/full?mnemonic=MMF-MMF_BRA_TOT-M", "$bn"),
 "ltd_h8_bn":                  ("H.8 B1072NCBAM Large time deposits, all commercial banks, SA, monthly (DDP package a01d1f4a5a65d77bcc3a3a97b8fbc03a, release 2026-08-28)", "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H8&series=a01d1f4a5a65d77bcc3a3a97b8fbc03a&lastobs=&from=&to=&filetype=csv&label=include&layout=seriescolumn", "source $ millions (Multiplier=1000000) -> /1000 = $bn"),
 "ltd_v1_bn":                  ("v1 vintage: FRED LTDACBM027NBOG mirror in data/history/large_time_deposits_bn.csv (pulled 2026-08-23)", "file: data/history/large_time_deposits_bn.csv (fred.stlouisfed.org unreachable from sandbox)", "$bn"),
 "dep_h8_bn":                  ("H.8 B1058NCBAM Deposits, all commercial banks, SA, monthly (same DDP package)", "same as ltd_h8_bn", "source $ millions -> /1000 = $bn"),
 "m2_alfred_bn":               ("ALFRED M2SL vintage 2026-08-15 (v1 denominator); 2026-07 = H.6 23,218.0", "file: data/vintages/alfred/alf_M2SL_2026-08-15.csv", "$bn SA"),
 "m2_ddp_bn":                  ("H.6 DDP M2.M SA (SDMX package prepared 2026-08-18)", "https://www.federalreserve.gov/datadownload/Output.aspx?rel=h6&filetype=zip", "$bn (UNIT_MULT=1e9)"),
 "currency_bn":                ("H.6 DDP MCU.M Currency component, SA", "same h6 zip", "$bn"),
 "retail_mmf_bn":              ("H.6 DDP MMFGB.M Retail money market funds, SA", "same h6 zip", "$bn"),
 "hf_reverse_repo_bn":         ("OFR Hedge Fund Monitor FPF-ASSETCLASS_REPO_REVERSEREPO_SUM, Qualifying Hedge Funds (global), quarter-end, current vintage 2026-06-04", "https://data.financialresearch.gov/hf/v1/series/full?mnemonic=FPF-ASSETCLASS_REPO_REVERSEREPO_SUM", "source raw US dollars (magnitude=0) -> /1e9 = $bn"),
 "hh_checkable_currency_bn":   ("Z.1 FL153020005.Q Households & NPOs; checkable deposits and currency; asset (NSA, end of period)", "https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip", "source $ millions -> /1000 = $bn"),
 "hh_time_savings_bn":         ("Z.1 FL153030005.Q Households & NPOs; total time and savings deposits; asset", "same z1 zip", "source $ millions -> /1000 = $bn"),
 "fhlb_advances_bn":           ("Z.1 FL763169335.Q US-chartered depository institutions; FHLB advances (residual); liability", "same z1 zip", "source $ millions -> /1000 = $bn"),
}

def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def hist(name):
    """data/history/<name>.csv: as_of,value -> dict keyed by YYYY-MM (OFR files are month-end dated, H.8 mirror is month-start dated)."""
    d = {}
    for r in read_csv(os.path.join(HIST, name + ".csv")):
        if r["value"] in ("", "."): continue
        d[r["as_of"][:7]] = float(r["value"])
    return d

# ---- load monthly inputs, keyed by YYYY-MM ----
tsy  = hist("mmf_treasury_repo_bn")
agy  = hist("mmf_agency_repo_bn")
oth  = hist("mmf_repo_other_collateral_bn")
fed  = hist("mmf_repo_with_fed_bn")
bra  = hist("mmf_bank_related_assets_bn")
ltd_v1 = hist("large_time_deposits_bn")

h8 = {r["as_of"]: (float(r["total_deposits_bn"]), float(r["large_time_deposits_bn"])) for r in read_csv(os.path.join(SCR, "h8.csv"))}
m2ddp = {r["as_of"][:7]: (float(r["m2_bn"]), float(r["currency_bn"]), float(r["retail_mmf_bn"])) for r in read_csv(os.path.join(SCR, "m2.csv"))}
m2alf = {}
for r in read_csv(ALF):
    v = r["M2SL_20260815"]
    if v not in ("", "."): m2alf[r["observation_date"][:7]] = float(v)
if "2026-07" not in m2alf:
    m2alf["2026-07"] = 23218.0   # H.6 July 2026, per brief; equals DDP M2.M 2026-07 in m2.csv
    assert abs(m2ddp["2026-07"][0] - 23218.0) < 0.05, "July 2026 M2 in DDP m2.csv does not equal 23,218.0"

# ---- quarterly inputs ----
hf = {}
for r in read_csv(os.path.join(SCR, "formpf.csv")):
    if r["mnemonic"] == "FPF-ASSETCLASS_REPO_REVERSEREPO_SUM":
        hf[r["as_of"][:7]] = float(r["value"]) / 1e9      # raw USD -> $bn
z1 = {}
for r in read_csv(os.path.join(SCR, "z1.csv")):
    y, q = r["as_of"].split("Q"); mm = {"1": "03", "2": "06", "3": "09", "4": "12"}[q]
    z1[f"{y}-{mm}"] = (float(r["hh_checkable_currency_bn"]), float(r["hh_time_savings_bn"]), float(r["fhlb_advances_bn"]))

# ---- quarter-end grid ----
quarters = []
y, m = 2021, 12
while (y, m) <= (2026, 6):
    quarters.append(f"{y}-{m:02d}")
    m += 3
    if m > 12: y, m = y + 1, 3

def z(W, D):
    return None if (W is None or D is None) else 100.0 * W / (W + D)
def f(x, nd=1):
    return "" if x is None else f"{x:.{nd}f}"

rows = []
for q in quarters:
    r = OrderedDict(quarter=q)
    # monthly W1 inputs
    ok = all(q in d for d in (tsy, agy, oth, fed, bra))
    r["mmf_treasury_repo_bn"] = tsy.get(q); r["mmf_agency_repo_bn"] = agy.get(q)
    r["mmf_repo_other_collateral_bn"] = oth.get(q); r["mmf_repo_with_fed_bn"] = fed.get(q)
    r["mmf_bank_related_assets_bn"] = bra.get(q)
    r["ltd_h8_bn"] = h8[q][1] if q in h8 else None
    r["dep_h8_bn"] = h8[q][0] if q in h8 else None
    r["ltd_v1_bn"] = ltd_v1.get(q)
    r["m2_alfred_bn"] = m2alf.get(q)
    r["m2_ddp_bn"], r["currency_bn"], r["retail_mmf_bn"] = m2ddp.get(q, (None, None, None))
    r["hf_reverse_repo_bn"] = hf.get(q)
    r["hh_checkable_currency_bn"], r["hh_time_savings_bn"], r["fhlb_advances_bn"] = z1.get(q, (None, None, None))

    priv_repo = (tsy[q] + agy[q] + oth[q] - fed[q]) if ok else None
    r["mmf_private_repo_bn"] = priv_repo
    # Perimeters (W_low convention: bank-related MMF assets assumed inside large time deposits, so counted once via LTD)
    W1   = (priv_repo + r["ltd_h8_bn"]) if (ok and r["ltd_h8_bn"] is not None) else None
    W1v1 = (priv_repo + r["ltd_v1_bn"]) if (ok and r["ltd_v1_bn"] is not None) else None   # v1-vintage LTD, continuity check
    W1fed = (W1 + fed[q]) if W1 is not None else None                                         # Fed-inclusive: NOT z_k
    W2   = (W1 + r["hf_reverse_repo_bn"]) if (W1 is not None and r["hf_reverse_repo_bn"] is not None) else None
    W3   = (W2 + r["fhlb_advances_bn"]) if (W2 is not None and r["fhlb_advances_bn"] is not None) else None
    r["W1_bn"], r["W1_v1ltd_bn"], r["W1_fedincl_bn"], r["W2_bn"], r["W3_bn"] = W1, W1v1, W1fed, W2, W3
    # Denominators
    D1 = r["m2_alfred_bn"]
    D1d = r["m2_ddp_bn"]
    D2 = (D1d - r["currency_bn"] - r["retail_mmf_bn"]) if D1d is not None else None
    D3 = (r["dep_h8_bn"] - r["ltd_h8_bn"]) if r["dep_h8_bn"] is not None else None
    D4 = (r["hh_checkable_currency_bn"] + r["hh_time_savings_bn"]) if r["hh_checkable_currency_bn"] is not None else None
    r["D1_m2_bn"], r["D1ddp_m2_bn"], r["D2_m2_ex_curr_rmmf_bn"], r["D3_h8_dep_ex_ltd_bn"], r["D4_z1_hh_dep_bn"] = D1, D1d, D2, D3, D4
    # z_k grid (percent)
    for wn, W in (("W1", W1), ("W2", W2), ("W3", W3)):
        for dn, D in (("D1", D1), ("D2", D2), ("D3", D3), ("D4", D4)):
            r[f"z_{wn}_{dn}_pct"] = z(W, D)
    r["z_W1_D1ddp_pct"] = z(W1, D1d)           # M2 vintage sensitivity
    r["z_W1v1ltd_D1_pct"] = z(W1v1, D1)        # should reproduce v1 table (z_k private, W_low)
    r["NOT_zk_W1_fedincl_D1_pct"] = z(W1fed, D1)  # Fed-inclusive continuity series; the Fed is not a bank
    rows.append(r)

cols = list(rows[0].keys())
with open(OUT, "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(cols)
    for r in rows:
        w.writerow([r["quarter"]] + [("" if v is None else (f"{v:.4f}" if "pct" in k else f"{v:.3f}")) for k, v in list(r.items())[1:]])
print("wrote", OUT, len(rows), "rows,", len(cols), "cols")

# ---- console report ----
print("\nquarter | W1 | W2 | W3 | D1 | D2 | D3 | D4 | W1/D1 | W2/D1 | W2/D2 | W2/D3 | W2/D4 | W3/D1 | W1v1/D1 | NOTzk_fed")
for r in rows:
    print(r["quarter"], f(r["W1_bn"]), f(r["W2_bn"]), f(r["W3_bn"]), f(r["D1_m2_bn"]), f(r["D2_m2_ex_curr_rmmf_bn"]), f(r["D3_h8_dep_ex_ltd_bn"]), f(r["D4_z1_hh_dep_bn"]),
          f(r["z_W1_D1_pct"],2), f(r["z_W2_D1_pct"],2), f(r["z_W2_D2_pct"],2), f(r["z_W2_D3_pct"],2), f(r["z_W2_D4_pct"],2), f(r["z_W3_D1_pct"],2), f(r["z_W1v1ltd_D1_pct"],2), f(r["NOT_zk_W1_fedincl_D1_pct"],2), sep=" | ")

# sensitivity: OFR 26-03 US repo census HF lending 1,007bn vs Form PF 1,335bn at 2025Q4 (figures from N2b note section 7)
r = [x for x in rows if x["quarter"] == "2025-12"][0]
W2us = r["W1_bn"] + 1007.0
print("\n2025Q4 sensitivity: W2 with Form PF HF leg (1,335) z=%.2f%% ; with OFR 26-03 US census HF leg (1,007) z=%.2f%% (on D1)" % (r["z_W2_D1_pct"], z(W2us, r["D1_m2_bn"])))
print("2025Q4 Form PF leg in file = %.1f" % r["hf_reverse_repo_bn"])
# all-quarter D1 vintage gap
print("\nmax |D1 ALFRED - D1 DDP| over grid: %.1f bn" % max(abs(x["m2_alfred_bn"] - x["m2_ddp_bn"]) for x in rows if x["m2_ddp_bn"] is not None))
print("max |z W1/D1 ALFRED - DDP| pp: %.3f" % max(abs(x["z_W1_D1_pct"] - x["z_W1_D1ddp_pct"]) for x in rows if x["z_W1_D1ddp_pct"] is not None))
print("max |ltd_h8 - ltd_v1| bn: %.1f" % max(abs(x["ltd_h8_bn"] - x["ltd_v1_bn"]) for x in rows if x["ltd_v1_bn"] is not None and x["ltd_h8_bn"] is not None))
print("max |z W1/D1 (h8 ltd) - (v1 ltd)| pp: %.3f" % max(abs(x["z_W1_D1_pct"] - x["z_W1v1ltd_D1_pct"]) for x in rows if x["z_W1v1ltd_D1_pct"] is not None and x["z_W1_D1_pct"] is not None))
missing = [(x["quarter"], [k for k, v in x.items() if v is None]) for x in rows if any(v is None for v in x.values())]
print("\nmissing inputs by quarter:"); [print(" ", q, m) for q, m in missing]
