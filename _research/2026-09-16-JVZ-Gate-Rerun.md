# 6c GATE RERUN — JVZ placebo MDE (16 Sep 2026)

**Status:** GATE COMPLETE. **Verdict: FAIL.**
**machineId:** `56a83289-aaaa-453d-a7c7-aa768bd566bb`
**Spec:** `_research/2026-09-16-JVZ-Gate-Rerun-Spec.md`
**C-092:** Prior Stage B / sharpen are **UNINFORMATIVE**, not rejections. This doc does **not** say NOT SUPPORTED / refuted.

> GATE ONLY. **No real-flow regression was run.** No scalar **M**. Clearing the gate is the principal's decision.

---

## Four numbers (handover)

| quantity | value | denom / definition |
|---|---:|---|
| Median placebo SE (excess return) | **0.548** | 200 quarter-permutations of `flow_z`; two-way clustered SE of β̂ |
| Median placebo SE (ann. idio vol) | **0.239** | same design, LHS = `idio_vol_ann_pct` |
| MDE return = 2 × median SE | **1.097 pp** | vs JVZ Table 6.2 top-50 **+0.528 pp** → predicted÷MDE = **0.48×** |
| MDE idio = 2 × median SE | **0.478 pp** | vs JVZ Table 6.3 **+0.43 pp** → predicted÷MDE = **0.90×** |

**PASS rule:** ratio > 1 on either channel. **Observed: both ≤ 1 → FAIL.**

---

## Step 1 — Coverage hole

Universe = `data/equity_tickers.txt` (**587** tickers; S&P500 / historical payer set used in Stage A).

| quantity | value | denominator |
|---|---:|---|
| Firms attempted | **587** | equity_tickers.txt |
| Firms with usable residuals | **540** | ≥1 firm-quarter with ≥40 daily OLS obs vs ^GSPC |
| Coverage | **540 ÷ 587 = 0.920** | retrieved ÷ attempted |
| Firm-quarters in residual panel | **24,074** | 2015Q1–2026Q2 |
| Top-40 megas by mean SPY `pctVal` | **40 / 40 present** | AAPL, MSFT, AMZN, NVDA, GOOGL, META, GOOG, TSLA, BRK-B, JPM, … |

**Still missing (47 / 587):** AET, ANDV, ARG, AVB, BBBY, BCR, BRCM, CCE, CFN, COL, COV, CVC, EA, EQR, ESRX, FDO, GAS, GGP, GMCR, HAR, HCBK, HOT, HSP, JOY, KORS, KRFT, LEG, LLTC, LO, LVLT, MJN, MWV, NFX, PCP, PETM, POM, RAI, SCG, SIAL, SNI, SPLS, STJ, SWY, TEG, TWC, TWX, WFM.

Almost all are delisted / acquired names Yahoo returns empty for. A few live names (AVB, EA, EQR, LEG) returned Yahoo “data doesn’t exist” under paced yfinance; not fabricated. Reused `data/prices/*.json` where present; new pulls written in the same chart-JSON cache shape.

Artifacts: `data/stage_b/firm_quarter_residuals_extended.csv`, `data/stage_b/gate_coverage.json`.

---

## Step 2 — Regressor spread

Regression panel = residuals ∩ SPY equity `pctVal` ∩ Z.1 ETF-holder `flow_bn`, quarters **2020Q1–2026Q2**.

| quantity | value | denominator |
|---|---:|---|
| N firm-quarters (SPY) | **10,729** | inner join |
| # firms | **439** | unique tickers in SPY panel |
| # time clusters | **26** | quarters 2020Q1–2026Q2 |
| Mean within-Q SD of SPY `pctVal` **with megas** | **0.579** | mean of 26 within-quarter SDs |
| Mean within-Q SD of SPY `pctVal` **without top-40 megas** | **0.106** | same after dropping top-40 by mean SPY weight |
| Delta (with − without) | **+0.473** | megas dominate cross-sectional spread |
| IVV cross-check (with megas) | **0.577** | 26 quarters; N FQ = 10,744 |

**Contradicts the brief’s arithmetic table.** Supervisor predicted that closing the mega hole would push within-Q SD toward **~1.6+** (live). Measured SD **with** megas on the fuller panel is **0.579** — *below* the sharpen incomplete-sample figure of **0.818** (208 firms). Top-208-by-weight within-Q SD on this panel is **0.778**, still well below 1.6. Adding the rest of the index adds mass near zero and **lowers** the empirical within-Q SD relative to a mega-heavy incomplete sample. The binding constraint remains **26 time clusters**, as the brief also predicted.

---

## Step 3 — Placebo MDE (200 perms)

**Design (unchanged vs Stage B/sharpen):** firm FE + quarter FE; two-way cluster (firm + quarter) via `linearmodels.PanelOLS`. LHS: (a) quarterly excess return vs ^GSPC (%); (b) annualised idio vol (%). Intensity = SPY `pctVal`. Treatment = `pctVal × flow_z`, where `flow_z` is Z.1 ETF-holder flow z-scored on the 26 sample quarters.

**Placebo:** randomly permute `flow_z` **across quarters** (preserve marginal), rebuild interaction, record SE(β̂). Repeat **200** times (seed 20260916).

| LHS | median SE | p10 | p90 | n perms |
|---|---:|---:|---:|---:|
| Excess return vs ^GSPC | **0.548** | 0.433 | 0.711 | 200 / 200 |
| Ann. idio vol | **0.239** | 0.146 | 0.407 | 200 / 200 |

**One-way bounds** (because # time clusters = 26 < 30):

| LHS | median SE firm-only | median SE quarter-only | largest |
|---|---:|---:|---|
| Excess return | 0.265 | **0.548** | **quarter** |
| Ann. idio vol | 0.122 | **0.234** | **quarter** |

Quarter clustering ≈ two-way; firm-only is much smaller. Precision is governed by **shock periods**, not firm-quarters (C-092).

---

## Step 4 — Verdict

| channel | predicted | MDE = 2 × median placebo SE | predicted ÷ MDE |
|---|---:|---:|---:|
| Return (JVZ Table 6.2 top-50) | +0.528 pp | **1.097 pp** | **0.48×** |
| Idio (JVZ Table 6.3) | +0.43 pp | **0.478 pp** | **0.90×** |

**FAIL** — neither channel has predicted ÷ MDE > 1.

Idio is close (0.90×) but does not clear. Return channel remains ~2× underpowered relative to JVZ’s predicted magnitude under this free-data design.

**Not claimed:** that JVZ is false; that Stage B/sharpen rejected the mechanism (they are uninformative per C-092); any household residual **M**; any 2024–26 attribution; that P5(iii) flow correlations are evidence either way.

**Not run:** real-flow regression (per spec — stop after gate).

---

## Artifacts

- Gate results JSON: `data/stage_b/gate_rerun_results.json`
- Residual panel: `data/stage_b/firm_quarter_residuals_extended.csv` (540 firms / 24,074 FQ)
- Regression panels: `data/stage_b/panel_SPY.csv`, `panel_IVV.csv`
- Coverage: `data/stage_b/gate_coverage.json`
- Price cache: `data/prices/*.json` (Yahoo chart JSON + yfinance-filled)

Handover row (parent runs `bin/check.sh`):  
`grok 6c-gate-rerun done "FAIL; medSE_ret=0.548 medSE_idio=0.239 MDE_ret=1.097 MDE_idio=0.478; ratios 0.48× / 0.90×; SD_with=0.579 SD_wo=0.106; cov 540/587"`
