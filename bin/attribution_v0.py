#!/usr/bin/env python3
"""
Attribution v0 -- P3 sensitivity-envelope test.

Reads (read-only, no writes to these):
  - data/z1_equity_netbuyers/netbuyers_quarterly_2026Q2.csv   (primary source for all flow/level arithmetic)
  - data/z1_equity_netbuyers/netbuyers_periods_2026Q2.csv     (cross-check only, not primary)
  - data/p2a_decomposition/decomp_annual.csv                  (S&P 500 return decomposition, annual)

Computes, for two windows (2015Q1-2019Q4, 2024Q1-2026Q2):
  - three flow objects: A = total net issuance, B = nonfinancial-corporate net issuance,
    C = ETF holder flow minus mutual-fund holder flow ("the switching object")
  - four benchmarks: B1 = change in total equity market value (Z.1 levels), B2 = revaluation
    component of B1, B3 = multiple-expansion's share of B2 (via the log price/EPS/PE decomposition
    of decomp_annual.csv), B4 = a constant-risk-premium counterfactual gap applied to B1's end level
  - 3 multipliers M in {2,5,9} applied to each object, compared against B1..B4 as ratios.

Outputs (this directory):
  - attribution_v0.csv : one row per window x object x M
  - benchmarks.csv      : one row per window, B1-B4 plus every input used to build them

Arithmetic only. No conclusions are drawn here; ambiguous choices are logged to stdout with the
alternative computation shown alongside, for the caller to judge materiality.
"""
import csv
import math
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root, wherever it is cloned (was the author's Dropbox path before 24 Sep 2026)
NETBUYERS_Q = os.path.join(BASE, "data/z1_equity_netbuyers/netbuyers_quarterly_2026Q2.csv")
NETBUYERS_P = os.path.join(BASE, "data/z1_equity_netbuyers/netbuyers_periods_2026Q2.csv")
DECOMP_A = os.path.join(BASE, "data/p2a_decomposition/decomp_annual.csv")

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

M_VALUES = [2, 5, 9]

# The 2015-2019 average ERP is used as a FIXED counterfactual anchor for both windows
# (per the brief: "hold the equity risk premium at its 2015-2019 average"), so it is
# defined once, outside the per-window loop.
BASELINE_ERP_YEARS = ["2015", "2016", "2017", "2018", "2019"]


def qrange(start_y, start_q, end_y, end_q):
    """Inclusive list of 'YYYY:QN' strings from (start_y,start_q) to (end_y,end_q)."""
    out = []
    y, q = start_y, start_q
    while (y, q) <= (end_y, end_q):
        out.append(f"{y}:Q{q}")
        q += 1
        if q > 4:
            q = 1
            y += 1
    return out


WINDOW_DEFS = {
    "2015Q1-2019Q4": dict(
        quarters=qrange(2015, 1, 2019, 4),
        period_label="2015-19",             # cross-check key into netbuyers_periods_2026Q2.csv
        decomp_years=["2015", "2016", "2017", "2018", "2019"],
        final_year="2019",
    ),
    "2024Q1-2026Q2": dict(
        quarters=qrange(2024, 1, 2026, 2),
        period_label="2024-latest",
        decomp_years=["2024", "2025", "2026_YTD"],
        final_year="2026_YTD",              # 2026 is not a complete year -- YTD row used, flagged here
    ),
}


def load_quarterly():
    rows = []
    with open(NETBUYERS_Q, newline="") as f:
        for row in csv.DictReader(f):
            row["flow_bn"] = float(row["flow_bn"])
            row["level_bn"] = float(row["level_bn"])
            row["reval_bn"] = float(row["reval_bn"])
            rows.append(row)
    return rows


def load_periods():
    rows = []
    with open(NETBUYERS_P, newline="") as f:
        for row in csv.DictReader(f):
            for k in ("quarters_n", "sum_flow_bn", "start_level_bn", "end_level_bn",
                      "delta_level_bn", "sum_reval_bn"):
                if row.get(k, "") not in ("", None):
                    row[k] = float(row[k])
            rows.append(row)
    return rows


def load_decomp_annual():
    rows = {}
    with open(DECOMP_A, newline="") as f:
        for row in csv.DictReader(f):
            rows[row["year"]] = row
    return rows


def sum_flow(rows, quarters, sector, role):
    qs = set(quarters)
    return sum(r["flow_bn"] for r in rows if r["quarter"] in qs and r["sector"] == sector and r["role"] == role)


def sum_reval(rows, quarters, sector, role):
    qs = set(quarters)
    return sum(r["reval_bn"] for r in rows if r["quarter"] in qs and r["sector"] == sector and r["role"] == role)


def periods_row(prows, period, sector, role):
    for r in prows:
        if r["period"] == period and r["sector"] == sector and r["role"] == role:
            return r
    return None


def compute_objects(qrows, quarters):
    """
    Object definitions (choice made, and why -- see stdout log for the alternative):
      A = flow_bn summed for sector='All sectors', role='total'.
          This is the Z.1 identity total: total net issuance of corporate equities across all
          issuer sectors equals total net purchases across all holder sectors (Rest-of-world
          appears on both sides, closing the identity), so this one row IS "the whole market's
          net flow" the brief asks for.
      B = flow_bn summed for sector='Nonfinancial corporate business', role='issuer'.
          Directly labelled in the source data; negative = buybacks/retirements > new issuance.
      C = (ETF holder flow) - (mutual-fund holder flow), i.e. sector='Exchange-traded funds',
          role='holder' minus sector='Mutual funds', role='holder'.
          CHOICE: 'holder' role, not ETFs' 'issuer_detail' role. 'issuer_detail' for ETFs is the
          creation of new ETF shares (a liability of the ETF vehicle); 'holder' is the ETF
          vehicle's own net purchases of the underlying corporate-equities instrument -- the
          side that is actually comparable to "mutual funds, holder" (mutual-fund shares are a
          different Z.1 instrument entirely and never appear as an issuer of corporate equities,
          which is why no 'Mutual funds, issuer' row exists in this file). The P3 doc's own
          numbers for 2024-26 ("ETFs +$2.46trn against mutual funds -$2.01trn") match the
          holder-role flows computed here, confirming this is the intended construction.
          ALTERNATIVE (shown, not used): ETF 'issuer_detail' minus MF 'holder' -- material,
          logged below.
    """
    A = sum_flow(qrows, quarters, "All sectors", "total")
    B = sum_flow(qrows, quarters, "Nonfinancial corporate business", "issuer")
    etf_holder = sum_flow(qrows, quarters, "Exchange-traded funds", "holder")
    mf_holder = sum_flow(qrows, quarters, "Mutual funds", "holder")
    etf_issuer_detail = sum_flow(qrows, quarters, "Exchange-traded funds", "issuer_detail")
    C = etf_holder - mf_holder
    C_alt = etf_issuer_detail - mf_holder
    return dict(A=A, B=B, C=C, etf_holder=etf_holder, mf_holder=mf_holder,
                etf_issuer_detail=etf_issuer_detail, C_alt_issuer_detail_minus_mf_holder=C_alt)


def level_bounds(qrows, quarters):
    """
    end_level  = level_bn at the window's last quarter (sector='All sectors', role='total').
    start_level = level_bn at the window's first quarter, backed out to the level just BEFORE
                  that quarter's flow+revaluation were applied:
                      start_level = level_bn(first_q) - flow_bn(first_q) - reval_bn(first_q)
                  This is necessary because the quarterly file starts at 2015:Q1, so there is no
                  explicit 2014:Q4 row to read a start level from directly; deriving it this way
                  needs only the quarterly file itself and is verified below against the
                  independently-built netbuyers_periods_2026Q2.csv start_level_bn column.
    """
    first_q, last_q = quarters[0], quarters[-1]
    end_row = next(r for r in qrows if r["quarter"] == last_q and r["sector"] == "All sectors" and r["role"] == "total")
    first_row = next(r for r in qrows if r["quarter"] == first_q and r["sector"] == "All sectors" and r["role"] == "total")
    end_level = end_row["level_bn"]
    start_level = first_row["level_bn"] - first_row["flow_bn"] - first_row["reval_bn"]
    return start_level, end_level


def compute_B1_B2(qrows, quarters):
    start_level, end_level = level_bounds(qrows, quarters)
    B1 = end_level - start_level
    B2 = sum_reval(qrows, quarters, "All sectors", "total")
    flow_sum = sum_flow(qrows, quarters, "All sectors", "total")
    # identity check: level change must equal flow + revaluation, exactly (to float tolerance)
    assert abs((flow_sum + B2) - B1) < 1e-6, f"flow+reval != delta level: {flow_sum}+{B2} != {B1}"
    return B1, B2, start_level, end_level, flow_sum


def compute_B3(decomp, year_list, B2):
    """
    B3 = multiple expansion's share of the window's LOG price change, applied to B2 ($bn).
    Per the brief: compound the annual (simple) figures in decomp_annual.csv across the years
    in the window -- because each year's start row chains exactly to the prior year's end row
    (P_start(y) == P_end(y-1), verified below), compounding the annual multiplicative factors is
    arithmetically identical to taking the direct ratio of the window's first P_start/E_start to
    its last P_end/E_end. That ratio is then converted to logs (log space is what makes the
    price/EPS/P-E decomposition exactly additive, with no cross term -- see decomp_cumulative.csv,
    reproduced by this same method as a sanity check during development).
    For a window ending in 2026, year_list's last entry is '2026_YTD' (partial year, Jan-Jun 2026)
    -- flagged explicitly here and in the output.
    """
    first, last = decomp[year_list[0]], decomp[year_list[-1]]
    P_start, P_end = float(first["P_start"]), float(last["P_end"])
    E_start, E_end = float(first["E_start"]), float(last["E_end"])
    PE_start, PE_end = float(first["PE_start"]), float(last["PE_end"])

    # chaining check: confirm consecutive annual rows in the window connect start-to-end exactly
    for a, b in zip(year_list, year_list[1:]):
        end_a, start_b = float(decomp[a]["P_end"]), float(decomp[b]["P_start"])
        assert abs(end_a - start_b) < 1e-6, f"decomp_annual rows do not chain: {a}.P_end={end_a} vs {b}.P_start={start_b}"

    log_price = math.log(P_end / P_start)
    log_eps = math.log(E_end / E_start)
    log_pe = log_price - log_eps
    log_pe_direct = math.log(PE_end / PE_start)
    assert abs(log_pe - log_pe_direct) < 1e-9, "log P/E decomposition inconsistent with direct P/E ratio"

    share_pe = log_pe / log_price
    share_eps = log_eps / log_price
    B3 = share_pe * B2
    return dict(P_start=P_start, P_end=P_end, E_start=E_start, E_end=E_end,
                PE_start=PE_start, PE_end=PE_end,
                log_price=log_price, log_eps=log_eps, log_pe=log_pe,
                share_pe_pct=share_pe * 100.0, share_eps_pct=share_eps * 100.0,
                years_used="+".join(year_list), B3=B3,
                is_ytd_final="2026_YTD" in year_list)


def compute_B4(decomp, baseline_years, window_years, final_year_label, end_level):
    """
    Constant-risk-premium counterfactual:
      1. erp_baseline = simple mean of erp_pct over 2015-2019 (fixed anchor, both windows).
         CHOICE: simple (unweighted) mean of the 5 annual figures, since all five are
         full 12-month periods (249-251 trading days each) -- weighting would change this
         negligibly. Not re-shown as an alternative because it is not material.
      2. window_avg_tips: mean of tips_yield_avg_pct over the window's decomp_annual rows,
         WEIGHTED by n_days_tips (the exact day-count each row's average was built from).
         CHOICE, logged as material: the 2024-2026Q2 window mixes two full years (~250 days
         each) with one half-year YTD row (173 days); an unweighted mean of the three row
         averages is shown alongside as the alternative.
      3. counterfactual_earnings_yield = erp_baseline + window_avg_tips; counterfactual_PE =
         100 / counterfactual_earnings_yield.
      4. actual_avg_PE (final year) = 100 / earnings_yield_avg_pct(final_year_label) -- i.e. the
         SAME inversion is applied to the actual period-average earnings yield as to the
         counterfactual one, for a like-for-like comparison ("average P/E", not a point-in-time
         P/E). CHOICE, logged as material: using PE_end (point-in-time, end-of-year) of the
         final year instead is shown alongside as the alternative.
      5. gap_PE = actual_avg_PE - counterfactual_PE; gap as a fraction of market value =
         gap_PE / actual_avg_PE (holding earnings E fixed, this is exactly
         (actual_price - counterfactual_price) / actual_price); B4 = that fraction * end_level.
    """
    erp_baseline = sum(float(decomp[y]["erp_pct"]) for y in baseline_years) / len(baseline_years)

    weighted_num = sum(float(decomp[y]["tips_yield_avg_pct"]) * float(decomp[y]["n_days_tips"]) for y in window_years)
    weighted_den = sum(float(decomp[y]["n_days_tips"]) for y in window_years)
    tips_avg_weighted = weighted_num / weighted_den
    tips_avg_simple = sum(float(decomp[y]["tips_yield_avg_pct"]) for y in window_years) / len(window_years)

    counterfactual_ey = erp_baseline + tips_avg_weighted
    counterfactual_PE = 100.0 / counterfactual_ey

    actual_ey_final = float(decomp[final_year_label]["earnings_yield_avg_pct"])
    actual_PE_final = 100.0 / actual_ey_final

    gap_PE = actual_PE_final - counterfactual_PE
    gap_pct_of_market_value = gap_PE / actual_PE_final
    B4 = gap_pct_of_market_value * end_level

    # --- alternatives, computed and logged, not used for the primary B4 ---
    counterfactual_ey_simple_tips = erp_baseline + tips_avg_simple
    counterfactual_PE_simple_tips = 100.0 / counterfactual_ey_simple_tips
    gap_PE_simple_tips = actual_PE_final - counterfactual_PE_simple_tips
    B4_alt_simple_tips = (gap_PE_simple_tips / actual_PE_final) * end_level

    PE_end_final_point = float(decomp[final_year_label]["PE_end"])
    gap_PE_pointintime = PE_end_final_point - counterfactual_PE
    B4_alt_pointintime = (gap_PE_pointintime / PE_end_final_point) * end_level

    return dict(
        erp_baseline_pct=erp_baseline,
        tips_avg_weighted_pct=tips_avg_weighted, tips_avg_simple_pct=tips_avg_simple,
        counterfactual_ey_pct=counterfactual_ey, counterfactual_PE=counterfactual_PE,
        final_year_label=final_year_label,
        actual_ey_final_pct=actual_ey_final, actual_PE_final=actual_PE_final,
        gap_PE=gap_PE, gap_pct_of_market_value=gap_pct_of_market_value, B4=B4,
        B4_alt_simple_tips=B4_alt_simple_tips,
        PE_end_final_point=PE_end_final_point, B4_alt_pointintime=B4_alt_pointintime,
    )


def chk(label, mine, theirs, tol, mismatches):
    if theirs is None:
        print(f"  [SKIP] {label}: no matching row in periods CSV")
        return
    ok = abs(mine - theirs) <= tol
    flag = "OK" if ok else "MISMATCH"
    print(f"  [{flag}] {label}: computed={mine:.4f}  periods_csv={theirs:.4f}  diff={mine-theirs:.6f}")
    if not ok:
        mismatches.append((label, mine, theirs))


def main():
    qrows = load_quarterly()
    prows = load_periods()
    decomp = load_decomp_annual()

    benchmark_rows = []
    attribution_rows = []
    all_mismatches = []

    for wname, wd in WINDOW_DEFS.items():
        quarters = wd["quarters"]
        print(f"\n=== {wname}  ({quarters[0]} .. {quarters[-1]}, {len(quarters)} quarters) ===")

        objs = compute_objects(qrows, quarters)
        B1, B2, start_level, end_level, flow_sum = compute_B1_B2(qrows, quarters)
        b3 = compute_B3(decomp, wd["decomp_years"], B2)
        b4 = compute_B4(decomp, BASELINE_ERP_YEARS, wd["decomp_years"], wd["final_year"], end_level)

        print(f"  object A (total net issuance, All sectors/total):            {objs['A']:.3f} bn")
        print(f"  object B (nonfinancial-corporate net issuance, issuer):      {objs['B']:.3f} bn")
        print(f"  object C (ETF holder - MF holder):                          {objs['C']:.3f} bn"
              f"   [ETF holder={objs['etf_holder']:.3f}, MF holder={objs['mf_holder']:.3f}]")
        print(f"    ALT object C (ETF issuer_detail - MF holder), not used:   {objs['C_alt_issuer_detail_minus_mf_holder']:.3f} bn"
              f"   [ETF issuer_detail={objs['etf_issuer_detail']:.3f}]  -- material vs primary C, logged only")

        print(f"  B1 change in market value (end-start level):  {B1:.3f} bn  (start={start_level:.3f}, end={end_level:.3f})")
        print(f"  B2 revaluation component:                     {B2:.3f} bn  (flow component={flow_sum:.3f} bn)")
        print(f"  B3 multiple-expansion share of B2:             {b3['B3']:.3f} bn"
              f"   [share_pe={b3['share_pe_pct']:.3f}% of log price change; years={b3['years_used']}"
              f"{'  (2026 = YTD through June)' if b3['is_ytd_final'] else ''}]")
        print(f"  B4 constant-risk-premium gap x end level:      {b4['B4']:.3f} bn"
              f"   [erp_baseline(2015-19)={b4['erp_baseline_pct']:.4f}%, "
              f"window_avg_tips(weighted)={b4['tips_avg_weighted_pct']:.4f}%, "
              f"counterfactual_PE={b4['counterfactual_PE']:.3f}, "
              f"actual_avg_PE({b4['final_year_label']})={b4['actual_PE_final']:.3f}]")
        print(f"    ALT B4 using simple (unweighted) tips average, not used:  {b4['B4_alt_simple_tips']:.3f} bn"
              f"   [tips_avg_simple={b4['tips_avg_simple_pct']:.4f}%]")
        print(f"    ALT B4 using point-in-time PE_end instead of avg-yield inversion, not used: "
              f"{b4['B4_alt_pointintime']:.3f} bn   [PE_end({b4['final_year_label']})={b4['PE_end_final_point']:.3f}]")

        # --- cross-checks against the independently-aggregated periods CSV ---
        print("  cross-checks vs netbuyers_periods_2026Q2.csv:")
        pl = wd["period_label"]
        prow_A = periods_row(prows, pl, "All sectors", "total")
        prow_B = periods_row(prows, pl, "Nonfinancial corporate business", "issuer")
        prow_etf = periods_row(prows, pl, "Exchange-traded funds", "holder")
        prow_mf = periods_row(prows, pl, "Mutual funds", "holder")
        chk("A flow sum", objs["A"], prow_A["sum_flow_bn"] if prow_A else None, 0.02, all_mismatches)
        chk("B flow sum", objs["B"], prow_B["sum_flow_bn"] if prow_B else None, 0.02, all_mismatches)
        chk("ETF holder flow sum", objs["etf_holder"], prow_etf["sum_flow_bn"] if prow_etf else None, 0.02, all_mismatches)
        chk("MF holder flow sum", objs["mf_holder"], prow_mf["sum_flow_bn"] if prow_mf else None, 0.02, all_mismatches)
        chk("start level", start_level, prow_A["start_level_bn"] if prow_A else None, 0.02, all_mismatches)
        chk("end level", end_level, prow_A["end_level_bn"] if prow_A else None, 0.02, all_mismatches)
        chk("B1 (delta level)", B1, prow_A["delta_level_bn"] if prow_A else None, 0.02, all_mismatches)
        chk("B2 (sum reval)", B2, prow_A["sum_reval_bn"] if prow_A else None, 0.02, all_mismatches)

        benchmark_rows.append({
            "window": wname,
            "quarters_used": f"{quarters[0]}..{quarters[-1]} (n={len(quarters)})",
            "B1_change_in_market_value_bn": round(B1, 3),
            "B2_revaluation_bn": round(B2, 3),
            "B3_multiple_expansion_share_of_reval_bn": round(b3["B3"], 3),
            "B4_constant_risk_premium_gap_bn": round(b4["B4"], 3),
            "start_level_bn": round(start_level, 3),
            "end_level_bn": round(end_level, 3),
            "flow_sum_all_sectors_bn": round(flow_sum, 3),
            "B3_decomp_years_used": b3["years_used"],
            "B3_2026_is_YTD_through_June": b3["is_ytd_final"],
            "B3_P_start": b3["P_start"], "B3_P_end": b3["P_end"],
            "B3_E_start": b3["E_start"], "B3_E_end": b3["E_end"],
            "B3_PE_start": round(b3["PE_start"], 6), "B3_PE_end": round(b3["PE_end"], 6),
            "B3_log_price_change": round(b3["log_price"], 6),
            "B3_log_eps_growth": round(b3["log_eps"], 6),
            "B3_log_pe_change": round(b3["log_pe"], 6),
            "B3_share_pe_pct_of_log_price": round(b3["share_pe_pct"], 4),
            "B3_share_eps_pct_of_log_price": round(b3["share_eps_pct"], 4),
            "B4_baseline_years_fixed": "+".join(BASELINE_ERP_YEARS),
            "B4_erp_baseline_pct": round(b4["erp_baseline_pct"], 6),
            "B4_final_year_used": b4["final_year_label"],
            "B4_window_avg_tips_pct_weighted_by_days": round(b4["tips_avg_weighted_pct"], 6),
            "B4_window_avg_tips_pct_simple_ALT": round(b4["tips_avg_simple_pct"], 6),
            "B4_counterfactual_earnings_yield_pct": round(b4["counterfactual_ey_pct"], 6),
            "B4_counterfactual_PE": round(b4["counterfactual_PE"], 6),
            "B4_actual_avg_earnings_yield_final_year_pct": round(b4["actual_ey_final_pct"], 6),
            "B4_actual_avg_PE_final_year": round(b4["actual_PE_final"], 6),
            "B4_gap_PE": round(b4["gap_PE"], 6),
            "B4_gap_pct_of_market_value": round(b4["gap_pct_of_market_value"], 6),
            "B4_ALT_using_simple_tips_avg_bn": round(b4["B4_alt_simple_tips"], 3),
            "B4_ALT_using_pointintime_PE_end_bn": round(b4["B4_alt_pointintime"], 3),
            "B4_ALT_PE_end_final_year_pointintime": round(b4["PE_end_final_point"], 6),
            "objectC_ALT_etf_issuer_detail_minus_mf_holder_bn": round(objs["C_alt_issuer_detail_minus_mf_holder"], 3),
        })

        object_list = [
            ("A_total_net_issuance", objs["A"]),
            ("B_nonfinancial_corporate_net_issuance", objs["B"]),
            ("C_etf_minus_mutualfund_holder_flow", objs["C"]),
        ]
        for obj_name, obj_val in object_list:
            for M in M_VALUES:
                predicted = M * obj_val
                attribution_rows.append({
                    "window": wname,
                    "object": obj_name,
                    "object_value_bn": round(obj_val, 3),
                    "M": M,
                    "predicted_bn": round(predicted, 3),
                    "ratio_to_B1": round(predicted / B1, 6) if B1 else "",
                    "ratio_to_B2": round(predicted / B2, 6) if B2 else "",
                    "ratio_to_B3": round(predicted / b3["B3"], 6) if b3["B3"] else "",
                    "ratio_to_B4": round(predicted / b4["B4"], 6) if b4["B4"] else "",
                })

    attribution_path = os.path.join(OUT_DIR, "attribution_v0.csv")
    with open(attribution_path, "w", newline="") as f:
        fieldnames = ["window", "object", "object_value_bn", "M", "predicted_bn",
                      "ratio_to_B1", "ratio_to_B2", "ratio_to_B3", "ratio_to_B4"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(attribution_rows)

    benchmarks_path = os.path.join(OUT_DIR, "benchmarks.csv")
    with open(benchmarks_path, "w", newline="") as f:
        fieldnames = list(benchmark_rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(benchmark_rows)

    print(f"\nWrote {len(attribution_rows)} rows to {attribution_path}")
    print(f"Wrote {len(benchmark_rows)} rows to {benchmarks_path}")
    if all_mismatches:
        print(f"\n*** {len(all_mismatches)} CROSS-CHECK MISMATCH(ES) -- see above ***")
    else:
        print("\nAll cross-checks against netbuyers_periods_2026Q2.csv passed within tolerance.")


if __name__ == "__main__":
    main()
