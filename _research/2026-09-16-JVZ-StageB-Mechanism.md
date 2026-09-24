# 6c Stage B — JVZ mega-firm passive amplification: MECHANISM TEST (16 Sep 2026)

**Status:** STAGE B COMPLETE on free data (E-005).
**machineId:** `56a83289-aaaa-453d-a7c7-aa768bd566bb`
**Gate:** Stage A CLEARED — `_research/2026-09-16-JVZ-MDE-Gate.md` / Spec.
**Paper:** Jiang, Vayanos & Zheng, *Passive Investing and the Rise of Mega-Firms*, RFS 2025.

> Mechanism test only. **No scalar M.** No 2024–26 revaluation attribution.
> P5(iii) quarter-collapsed correlations are **not** findings and are not quoted as such below.

---

## 0. Critical gate (within-quarter variation)

**Passive intensity varies within quarter across firms — GATE DOES NOT COLLAPSE.**

| check | value | denominator |
|---|---:|---|
| Mean within-quarter SD of IWB `pctVal` | **0.559** | 23 quarters in regression sample |
| Share of quarters with within-Q SD > 0 | **1.00** | 23/23 |
| Share of identifying variation (within-Q SS / total SS of `pctVal`) | **0.9997** | ANOVA decomposition on 3,936 firm-quarters |
| Unique `pctVal` values per quarter | = n firms in Q (all distinct) | see §2 |

If intensity had been constant within Q, effective n would snap to ~23 and this report would stop with **GATE COLLAPSES**. It does not.

---

## 1. Sample construction

### Panel shape (longest free overlap actually used)

| quantity | value | denominator / note |
|---|---:|---|
| Firms | **181** | Yahoo-cached tickers from Stage A residual rebuild that name-match to ≥1 IWB equity holding |
| Quarters | **23** | 2020Q4–2026Q2 continuous (N-PORT IWB span after Sep/Dec pull) |
| Firm-quarters | **3,936** | inner join of residuals ∩ IWB intensity ∩ Z.1 ETF holder flow |
| Spec target | 2015Q1–2026Q2 | **not reached**: free IWB N-PORT on disk+pull starts 2020-12-31; Stage A residuals exist from 2015Q1 but intensity does not |

**Brief vs delivered:** Spec asked 2015Q1–2026Q2. Free N-PORT for IWB series `S000004347` was extended from on-disk Mar/Jun 2022–26 to **all quarter-ends 2020Q4–2026Q2** (13 new primary_doc.xml pulls, UA `ThirdDerivativeResearch/1.0`). Pre-2020Q4 free IWB holdings were not on disk and were not fabricated. Overlap = N-PORT ∩ residuals ∩ Z.1.

### LHS (firm-quarter)

From Stage A rebuild `data/stage_a/firm_quarter_residuals.csv` (method unchanged):

- **Idiosyncratic vol (ann. %):** market-model residual SD vs `^GSPC` daily × √252 × 100; min 40 daily obs.
- **Excess return (%):** compounded ticker quarterly return − compounded `^GSPC` over the same days.

### RHS — passive intensity (within-quarter-varying)

- **Source:** iShares Russell 1000 ETF (IWB) N-PORT-P equity holdings (`assetCat=EC`), field `pctVal` = position as **percent of ETF NAV**.
- **On disk:** `data/p4/iwb_iwm_holdings.csv` (Mar/Jun 2022–2026).
- **Pulled this run:** Sep/Dec + 2021 + 2020-12 via seriesId `S000004347` (accessions verified `seriesName=iShares Russell 1000 ETF`); parsed to `data/stage_b/iwb_holdings_extended.csv`.
- **Firm map:** holding `name`/`title` → Yahoo `shortName`/`longName` on Stage A price cache (unique normalized match only). 181 residual tickers matched; 6 residual tickers unmatched (AIV, APC, BBT, BEN, CAM, CNX).
- **Aggregation:** sum `pctVal` if multiple matched rows per ticker-period (share classes).

### RHS — aggregate equity-ETF flow

- **Source:** `data/z1_equity_netbuyers/netbuyers_quarterly_2026Q2.csv`
- **Definition:** sector `Exchange-traded funds`, role **`holder`**, field `flow_bn` (same construction P5 used for its flow column — industry-wide ETF equity holdings flow, **not** JVZ’s S&P500-index-fund-specific `PassiveFlowSP500`).
- **Standardization:** z-score to mean 0 / SD 1 over the **23 regression sample quarters**.
  - mean = **180.25 $bn**/quarter (n=23)
  - SD = **98.81 $bn** (n=23)
- `etf1/quarterly.csv` covers only 2024+ and was **not** used as the primary flow (too short).

### Regressor

$$
\text{intensity\_x\_flow}_{i,t} = \underbrace{\mathrm{pctVal}_{i,t}}_{\text{IWB weight \% NAV}} \times \underbrace{\mathrm{flow\_z}_{t}}_{\text{Z.1 ETF holder flow, 1 SD}}
$$

### FE and clustering (declared = done)

- **Firm FE + quarter FE** (`linearmodels.PanelOLS`, `entity_effects=True`, `time_effects=True`).
- **SEs:** two-way clustered by **firm and quarter** (`cov_type='clustered'`, `cluster_entity=True`, `cluster_time=True`).
- Flow main effect absorbed by quarter FE; slow-moving intensity largely absorbed by firm FE; identifying variation is demeaned interaction (and §0 shows almost all raw intensity variation is within-Q).

---

## 2. Within-quarter variation check

| quarter | n firms | mean pctVal | SD pctVal | n unique |
|---|---:|---:|---:|---:|
| 2020Q4 | 153 | 0.214 | 0.598 | 153 |
| 2021Q1 | 153 | 0.204 | 0.526 | 153 |
| 2021Q2 | 154 | 0.200 | 0.530 | 154 |
| 2021Q3 | 155 | 0.202 | 0.537 | 155 |
| 2021Q4 | 156 | 0.205 | 0.578 | 156 |
| 2022Q1 | 159 | 0.215 | 0.603 | 159 |
| 2022Q2 | 161 | 0.204 | 0.538 | 161 |
| 2022Q3 | 174 | 0.204 | 0.560 | 174 |
| 2022Q4 | 174 | 0.195 | 0.473 | 174 |
| 2023Q1 | 176 | 0.199 | 0.548 | 176 |
| 2023Q2 | 176 | 0.199 | 0.596 | 176 |
| 2023Q3 | 177 | 0.198 | 0.560 | 177 |
| 2023Q4 | 177 | 0.198 | 0.564 | 177 |
| 2024Q1 | 177 | 0.188 | 0.492 | 177 |
| 2024Q2 | 177 | 0.189 | 0.557 | 177 |
| 2024Q3 | 179 | 0.189 | 0.566 | 179 |
| 2024Q4 | 180 | 0.193 | 0.611 | 180 |
| 2025Q1 | 180 | 0.190 | 0.573 | 180 |
| 2025Q2 | 180 | 0.182 | 0.527 | 180 |
| 2025Q3 | 180 | 0.183 | 0.572 | 180 |
| 2025Q4 | 180 | 0.186 | 0.594 | 180 |
| 2026Q1 | 180 | 0.184 | 0.569 | 180 |
| 2026Q2 | 178 | 0.184 | 0.578 | 178 |

Mean within-Q SD = **0.559**; within-Q share of SS = **99.97%**. Dead-design collapse (n→~23) **rejected**.

Largest mean IWB weights in sample (denom = matched tickers): AAPL 6.04, AMZN 3.25, TSLA 1.60, BRK-B 1.46, AVGO 1.21. **Missing from Stage A Yahoo cache (hence from panel):** MSFT, NVDA, META, GOOGL/GOOG, JPM, V, MA, UNH, XOM, JNJ — exactly the mega-firm left tail JVZ emphasizes.

---

## 3. Main results

Specification: $y_{it} = \alpha_i + \gamma_t + \beta\,(\mathrm{pctVal}_{it}\times\mathrm{flow\_z}_t) + \varepsilon_{it}$.

| LHS | β̂ | SE (firm+Q cluster) | t | p | N |
|---|---:|---:|---:|---:|---:|
| Quarterly excess return vs ^GSPC (%) | **+0.504** | 0.811 | 0.62 | 0.53 | 3,936 |
| Idio vol ann. (%) | **−0.051** | 0.216 | −0.24 | 0.81 | 3,936 |
| log(idio vol) | **+0.00014** | 0.00596 | 0.02 | 0.98 | 3,936 |

**FE:** firm + quarter. **Cluster:** firm + quarter (declared above).

**Reading:** A one-unit increase in IWB `pctVal` (e.g. 0→1 percentage point of ETF NAV) times a +1 SD Z.1 ETF holder flow is associated with ~+0.5 pp quarterly excess return — **insignificant**. Idio channel is a **wrong-signed null** relative to JVZ Table 6.3 (paper: passive flow raises mega-firm idio vol).

Units are **not** directly JVZ Table 6.2’s “Top50 × 1 SD PassiveFlowSP500” (+0.528 pp). Here intensity is continuous IWB weight × industry ETF flow z-score. Rough translation: +1 within-Q SD of intensity (≈0.56 pctVal) × 1 SD flow → ≈0.28 pp excess (still well inside SE).

Working files: `data/stage_b/firm_quarter_panel.csv`, `data/stage_b/regression_results.json`.

---

## 4. Placebo

**Placebo intensity:** within-quarter percentile of end-of-quarter Yahoo **adjclose** among Stage A residual-panel firms that quarter (universe **not** conditioned on IWB membership). Intent: a size-ish rank that does not use index membership to define who enters the ranking. **Limitation:** price ≠ market cap; corr(pctVal, size_pctile) = **0.183** on the sample.

| LHS | β̂ placebo | SE | t | p | N |
|---|---:|---:|---:|---:|---:|
| Excess return (%) | −0.200 | 1.891 | −0.11 | 0.92 | 3,936 |
| Idio vol ann. (%) | +0.412 | 0.618 | 0.67 | 0.50 | 3,936 |
| log(idio) | +0.026 | 0.019 | 1.33 | 0.18 | 3,936 |

Placebo is also null. Does **not** rescue a false positive (there was none). Does **not** separately identify “size vs passive intensity” given the main null.

---

## 5. Verdict

### **INCONCLUSIVE** on free data

**Why not SUPPORTED:** main return and idio interactions are statistically zero; idio point estimate has the wrong sign vs JVZ Table 6.3.

**Why not NOT SUPPORTED (clean rejection):** the free-data design is live on within-Q variation (gate passed; n=3,936) but is still a blunt proxy for the paper’s object:

1. Flow is **Z.1 industry ETF holder flow**, not S&P500-index-fund `PassiveFlowSP500`.
2. Intensity is **IWB (Russell 1000) weight**, not S&P500 passive ownership share.
3. Stage A Yahoo coverage **omits MSFT/NVDA/META/GOOG(L)/…** — the mega-firm left tail that should dominate the JVZ cross-section.
4. N-PORT span is **2020Q4–2026Q2** (23Q), not 2015–2026; quarter-cluster dimension remains thin (23 clusters).
5. Placebo size rank uses **price**, not market cap.

So: the P5(iii) dead design was fixed (within-Q variation is real; n is not ~42). On that live free-data design, **we do not find support** for the mechanism — but free-data holes are large enough that this is **not** a refutation of JVZ the paper. **INCONCLUSIVE.**

Explicitly **not** claimed: any household residual **M**; any 2024–26 attribution; any P5(iii) correlation as evidence.

---

## 6. Limitations

| limitation | effect on interpretation |
|---|---|
| Yahoo Stage A cache incomplete (rate limits) | Mega-caps missing → attenuation / selection against the hypothesis’s strongest cells |
| N-PORT free span 2020Q4–2026Q2 | Shorter than Stage A residual panel; 23 time clusters |
| Z.1 ETF holder flow ≠ index-fund flow | Dose is industry-wide, not PassiveFlowSP500 |
| IWB weight ≠ S&P500 passive ownership | Cap-weighted Russell 1000 ETF weight is a cousin, not the paper’s measure |
| Name-match ticker map | Unmatched / ambiguous names dropped; no CUSIP→ticker master |
| Placebo = price percentile | Not market-cap rank; only weakly correlated with intensity |
| Two-way cluster with G_time=23 | Conservative SEs; still the declared design |
| `etf1/quarterly.csv` unused as primary flow | Only 2024+ rows; too short for 23Q panel |

---

## Blockers / notes for parent

1. Deliverable path: `_research/2026-09-16-JVZ-StageB-Mechanism.md` (this file).
2. Do **not** run `bin/check.sh --handover write` here — parent will.
3. Vintage append left as clean TSV under `data/vintages/` for parent merge into `data/series.tsv`.
4. New N-PORT XMLs on box: `data/p4/nport_xml/IWB_*.xml` (13 files); extended holdings CSV in `data/stage_b/`.
5. If supervisor wants a sharper test: (a) finish Yahoo mega-cap residual panel, (b) CUSIP map, (c) S&P500-index ETF holdings (e.g. IVV/SPY) as intensity — still free, still E-005.
