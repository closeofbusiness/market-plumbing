# 6c Stage B SHARPEN — JVZ mega-firm passive amplification (16 Sep 2026)

**Status:** SHARPEN COMPLETE on free data (E-005).
**machineId:** `56a83289-aaaa-453d-a7c7-aa768bd566bb`
**Prior:** `_research/2026-09-16-JVZ-StageB-Mechanism.md` (INCONCLUSIVE; IWB + incomplete megas).
**Gate:** Stage A CLEARED — `_research/2026-09-16-JVZ-MDE-Gate.md`.

> Mechanism test only. **No scalar M.** No 2024–26 revaluation attribution.
> P5(iii) correlations are not findings.

---

## What changed vs Stage B

| hole in Stage B | sharpen action |
|---|---|
| Missing MSFT/NVDA/META/GOOGL/… in residuals | Yahoo chart pull + market-model rebuild for **37** mega/S&P names (all succeeded; 46Q each) |
| IWB (Russell 1000) intensity ≠ S&P500 | **Primary: SPY** N-PORT equity `pctVal` (SPDR S&P 500 ETF Trust, CIK 884394); IVV parallel |
| Incomplete left-tail weights | CUSIP overrides for GOOGL/GOOG/XOM (+ name match); top weights now AAPL/MSFT/AMZN/NVDA/GOOGL/META |

---

## 1. Sample construction

### Extended residuals

| quantity | value | denominator |
|---|---:|---|
| Prior Stage A firms | 186 | `data/stage_a/firm_quarter_residuals.csv` |
| **Mega-caps newly added** | **37** | listed below |
| Extended firms | **223** | union |
| Extended firm-quarters | **9,985** | 2015Q1–2026Q2 where min 40 daily obs |

**Mega-caps added (37/37 OK):** MSFT, NVDA, META, GOOGL, GOOG, JPM, V, MA, UNH, XOM, JNJ, LLY, WMT, ORCL, HD, PG, NFLX, KO, PEP, MRK, TMO, LIN, MCD, WFC, TXN, INTU, QCOM, GE, IBM, NOW, ISRG, T, VZ, PFE, MS, GS, SCHW.

Method unchanged: OLS daily returns on `^GSPC`; residual SD × √252 × 100; excess = compounded ticker − compounded `^GSPC`; min 40 days. Cache: `data/prices/*.json`. Panel: `data/stage_b/firm_quarter_residuals_extended.csv`.

### Intensity — **primary SPY** (IVV also pulled)

| fund | source | span | quarter-ends |
|---|---|---|---:|
| **SPY (primary)** | N-PORT-P `primary_doc.xml`, CIK 0000884394 | **2020Q1–2026Q2** | **26** |
| IVV (parallel) | N-PORT-P series `S000004310`, CIK 0001100663 | 2020Q1–2026Q2 | 26 |

- Intensity = equity (`assetCat=EC`) holding **`pctVal`** (% of fund NAV).
- Firm map: Yahoo name match + CUSIP overrides (Alphabet Class A/C, XOM).
- Holdings file: `data/stage_b/spy_ivv_holdings.csv`.

**Why SPY primary:** SPY filings are single-trust and clean; brief said prefer IVV only if SPY is harder. IVV results are nearly identical (reported below).

### Flow (unchanged)

Z.1 `Exchange-traded funds` / role=`holder` / `flow_bn`, z-scored on regression sample quarters.
Still **not** JVZ `PassiveFlowSP500` (no freer closer free proxy found).

### Spec vs delivered

Spec target overlap through 2026Q2: **met** for intensity (2020Q1–2026Q2). Pre-2020 N-PORT exists for SPY from 2019H2 but sharpen regression starts 2020Q1 with full mega residual overlap. 2015–2019 intensity still absent free for continuous S&P500 ETF holdings in this run’s download window choice (2020+).

---

## 2. Within-quarter variation check (SPY)

**PASS — GATE DOES NOT COLLAPSE.**

| check | value | denom |
|---|---:|---|
| Mean within-Q SD of SPY `pctVal` | **0.818** | 26 quarters |
| Share quarters with SD > 0 | **1.00** | 26/26 |
| Within-Q SS / total SS | **≈0.9999** | ANOVA on regression panel |

Regression panel after joins: **208 firms × 26 quarters = 5,010 firm-quarters**.

Top mean SPY weights in panel (denom = matched tickers): AAPL 6.58, MSFT 6.07, AMZN 3.68, NVDA 3.60, GOOGL 2.11, META 2.05, GOOG 1.84, TSLA 1.76, BRK-B 1.60, JPM 1.26.

---

## 3. Main results (primary: SPY × flow_z)

$y_{it}=\alpha_i+\gamma_t+\beta(\mathrm{pctVal}^{SPY}_{it}\times\mathrm{flow\_z}_t)+\varepsilon_{it}$

**FE:** firm + quarter. **Cluster:** firm + quarter (`linearmodels` two-way).

| LHS | β̂ | SE | t | p | N |
|---|---:|---:|---:|---:|---:|
| Excess return vs ^GSPC (%) | **−0.336** | 0.544 | **−0.62** | 0.54 | 5,010 |
| Idio vol ann. (%) | **+0.066** | 0.293 | **0.22** | 0.82 | 5,010 |
| log(idio vol) | **+0.00011** | 0.0072 | **0.02** | 0.99 | 5,010 |

Return channel is a **wrong-signed null** vs JVZ Table 6.2 (paper: mega stocks *earn positive* excess when passive flows arrive). Idio channel is a **near-zero null** vs Table 6.3.

### Placebo (price percentile × flow_z; universe = extended residual panel, not conditioned on SPY membership)

| LHS | β̂ | SE | t | p |
|---|---:|---:|---:|---:|
| Excess return (%) | −1.60 | 2.64 | −0.61 | 0.54 |
| Idio vol ann. (%) | +2.52 | 1.23 | **2.05** | 0.04 |
| log(idio) | +0.060 | 0.026 | **2.30** | 0.02 |

Placebo **return** null (consistent with main). Placebo **idio** is significant — a size-ish rank × industry ETF flow correlates with idio vol even when SPY weight × flow does not. That undercuts reading any idio pattern as *index-membership passive intensity*; if anything it points at a generic size×flow association under a blunt flow proxy. Price ≠ market cap (limitation).

---

## 4. Comparison vs Stage B (IWB) and parallels

| design | intensity | N FQ | firms | Q | ret β (t) | idio β (t) |
|---|---|---:|---:|---:|---|---|
| Stage B original | IWB | 3,936 | 181 | 23 | +0.504 (0.62) | −0.051 (−0.24) |
| Sharpen IWB + megas | IWB | 4,665 | 214 | 23 | −0.293 (−0.46) | −0.285 (−1.36) |
| **Sharpen SPY + megas (primary)** | **SPY** | **5,010** | **208** | **26** | **−0.336 (−0.62)** | **+0.066 (0.22)** |
| Sharpen IVV + megas | IVV | 4,930 | 206 | 26 | −0.475 (−0.87) | +0.027 (0.10) |

Adding megas and switching to S&P500-ETF intensity **does not** produce JVZ-signed significant effects. IWB-on-extended is if anything more wrong-signed on idio.

---

## 5. Verdict

### **NOT SUPPORTED** on free data (sharpened design)

Stage B’s INCONCLUSIVE rested on missing megas and Russell-1000 intensity. Those holes are closed:

1. Within-Q variation remains live (gate passed; n≈5,010).
2. Mega-cap left tail is in the residual panel and in SPY weights.
3. Intensity is an **S&P500 ETF** (SPY; IVV agrees).

Under firm+quarter FE and two-way clustering, the interaction of SPY weight with Z.1 ETF holder flow is **insignificant** on excess returns (wrong sign) and **insignificant** on idiosyncratic vol. That is **not support** for the JVZ mega-firm passive-amplification mechanism on free data.

**Remaining non-refutation caveat (stated, not used to walk back the verdict):** flow is still industry-wide Z.1 ETF holder flow, not the paper’s S&P500-*index-fund* `PassiveFlowSP500`. A paid Morningstar/CRSP index-fund flow series could still differ. Within E-005 free data, this is the closest live design we can run.

Explicitly **not** claimed: household residual **M**; 2024–26 attribution; P5(iii) as evidence.

---

## 6. Limitations

| limitation | note |
|---|---|
| Z.1 ETF holder flow ≠ PassiveFlowSP500 | Binding free-data gap called out in Stage B / P5 |
| N-PORT from 2020Q1 (26Q) | Shorter than Stage A residual span; 26 time clusters |
| Placebo = EOP price percentile | Not market cap; idio placebo significant |
| Name/CUSIP map | Manual CUSIP overrides for Alphabet/XOM; residual mismatch risk elsewhere |
| Yahoo coverage | 37 new megas OK this run; full 500-name panel still incomplete |
| GOOG+GOOGL both in panel | Dual share classes; both carry SPY weights |

---

## Blockers / notes for parent

1. Path: `_research/2026-09-16-JVZ-StageB-Sharpen.md`
2. Do **not** run `bin/check.sh --handover write` — parent will.
3. Vintage TSV: `data/vintages/2026-09-16-jvz-stageb-sharpen-scalars.tsv`
4. Working artifacts: `data/stage_b/panel_SPY.csv`, `sharpen_results.json`, `firm_quarter_residuals_extended.csv`, `spy_ivv_holdings.csv`, `data/p4/nport_xml/SPY_*.xml` + `IVV_*.xml`
