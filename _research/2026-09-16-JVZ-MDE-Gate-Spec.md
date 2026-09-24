# 6c — JVZ mega-firm passive amplification: MDE GATE SPEC (16 Sep 2026)

**Author:** Claude (supervisor). **For:** whichever agent picks up ranked item 6c.
**Status:** GATE ONLY. Stage A is the deliverable. Stage B does not start until Stage A is reported and cleared.

> **Read `CLAUDE.md`'s MDE rule before starting (C-090, C-091).** Two parcels were already spent on a design
> that could not have detected its own hypothesis. This spec exists so that does not happen a third time.

---

## Why this is gated

Ranked item 6c is the last live Tier B design. Three have already failed: B5 sovereign mandate, P4 Russell RD
(C-086), B6 payment-day (C-090/C-091). B6 failed on **arithmetic, not data** — the predicted effect was 2.51bp
against 111bp of daily noise, needing ~386 years. That was computable before any pull, and was not computed.

**So: compute the minimum detectable effect FIRST, report it, and stop.**

## The design flaw this spec exists to fix

`2026-09-13-P5iii-Concentration-And-JVZ.md` already ran a version of this and returned a "weak-negative flow
link". **That result is uninformative and must not be quoted as evidence either way.** It collapsed the
cross-section into a single top10-minus-rest gap per quarter, leaving n = 10–30 quarters:

| effective n | detectable \|r\| at t=2 |
|---:|---:|
| 10 | 0.577 |
| 20 | 0.426 |
| 30 | 0.354 |
| 42 | 0.302 |
| 370 | 0.104 |
| 15,540 | 0.016 |

Observed in `data/p5_concentration/07_flow_correlation_tests.csv`: +0.050, −0.737, −0.546, +0.426, −0.465.
**The signs flip across windows.** That is the signature of an underpowered short series, not a finding.

**The trap to avoid, stated plainly.** A firm-quarter panel is 370 firms × 42 quarters ≈ **15,540 rows**, but
if the flow regressor varies **only by quarter** (as `etf_flow_bn` does), then clustering standard errors by
quarter returns the effective n to **42**, and the extra rows buy nothing. Power arrives only if the treatment
**varies within quarter, across firms** — e.g. each firm's passive/ETF ownership share, interacted with
aggregate flow. Do not skip this; it is the whole difference between a JVZ test and a repeat of P5(iii).

## Stage A — the gate (this is the deliverable)

Report, before pulling anything new:

1. **The predicted effect size, sourced from the paper, with a page or section reference.** Jiang, Vayanos &
   Zheng, *Passive Investing and the Rise of Mega-Firms*, RFS 2025 — `https://personal.lse.ac.uk/vayanos/Papers/PIRMF_RFSf.pdf`
   (**URL verified live 16 Sep 2026: HTTP 200, application/pdf, 801,643 bytes**). Do not guess a magnitude; if
   the paper gives a range or an elasticity rather than a point, report it in the paper's own units and say so.
   If you cannot find a usable magnitude, **say that** — an unnamed effect size is itself a gate failure.
2. **The noise term**, computed from data on disk: residual sd of firm-quarter idiosyncratic vol and of
   firm-quarter returns, from the per-ticker panel (see Data below).
3. **The effective n**, stated with the clustering you intend, and an explicit sentence on whether the
   treatment varies within quarter.
4. **The minimum detectable effect at t=2**, in the same units as (1), and the verdict:
   **does the predicted effect exceed the MDE?**

**Then stop and hand back.** Do not run the regression. Do not pull N-PORT. A cleared gate is a supervisor
decision, not yours.

## Stage B — only on a cleared gate

Firm-quarter panel, 2015Q1–2026Q2. LHS: idiosyncratic vol and excess return per firm-quarter. RHS: a
**within-quarter-varying** passive-intensity measure interacted with aggregate equity-ETF flow, with firm and
quarter fixed effects, SEs clustered as declared in Stage A. Report the placebo where passive intensity is
replaced by a size rank unrelated to index membership.

## Data already on disk — do not re-pull

- `data/p5_concentration/04_idio_vol_by_quarter_and_group.csv` — 84 rows, **group means only**. The per-ticker
  residuals were computed to build it (market model vs `^GSPC`, min 40 daily obs) but **were not saved**. The
  per-ticker-quarter panel must be rebuilt; the method is in the file's `source` column.
- `data/p5_concentration/06_flow_vs_concentration_quarterly.csv` — 42 quarters, gaps + ETF/MF flows.
- `data/p5_concentration/07_flow_correlation_tests.csv` — the underpowered tests. Use for the MDE arithmetic;
  do not quote as a result.
- `data/etf1/quarterly.csv` — ETF share issuance (C-083; the wrapper).
- `data/p4/iwb_iwm_holdings.csv`, `data/p4/nport_accessions.json` — N-PORT holdings, IWB/IWM, 2022–2026.
- `data/z1_equity_netbuyers/netbuyers_quarterly_2026Q2.csv` — Z.1 sector flows.

## Do not say

- Any scalar multiplier **M** for the household residual, or any rescaling of a firm-level estimate to the
  market (C-077, C-080, C-086, C-090, C-091).
- That P5(iii)'s weak-negative flow link is evidence the passive bid does not move prices.
- That JVZ "explains" the 2024–26 revaluation. This is a **mechanism** test, not an attribution.

## Rules

- **Run every command in the FOREGROUND and block on it.** No `nohup`, no trailing `&`, no detached worker,
  no "I'll wait to be notified" — completion notifications do not reach a subagent. If a command exceeds the
  tool timeout, split it into slices and run them in sequence, still in the foreground. Report only output you
  actually observed; a predicted result is a fabricated one.
- **State the denominator on every number**, including n and what population it came from.
- **If your finding contradicts this brief, say so explicitly.** A brief built on a wrong assumption is the
  most valuable thing you can send back — this spec is the third attempt at Tier B and may itself be wrong.
- **Never route around a refusal.** If something is blocked, say which part and why, and do the rest.
- **No summary or report files.** Findings go in the findings doc and the handover row.
- **We never pay for data (E-005).** Free sources only; a rough estimate with a band is a result.
- Hand over when you stop: `bin/check.sh --handover write <agent> 6c-mde-gate <done|paused|blocked> "<next>"`.
