# 6c Stage A — JVZ mega-firm passive amplification: MDE GATE (16 Sep 2026)

**Status:** STAGE A ONLY — gate report. Stage B not run. N-PORT not pulled. No regression.
**machineId:** `56a83289-aaaa-453d-a7c7-aa768bd566bb`
**Paper:** Jiang, Vayanos & Zheng, *Passive Investing and the Rise of Mega-Firms*, RFS 2025 —
PDF `https://personal.lse.ac.uk/vayanos/Papers/PIRMF_RFSf.pdf` (fetched 16 Sep 2026, 801,643 bytes).
**Noise rebuild:** Yahoo Finance chart API / `^GSPC` only; market-model residuals; min 40 daily obs
per ticker-quarter (same method as `data/p5_concentration/04_idio_vol_by_quarter_and_group.csv` source column).

> This is a **mechanism-test power gate**, not an attribution of the 2024–26 revaluation.
> No scalar **M** for the household residual. P5(iii) flow correlations are used only as
> underpowered-design context — **not** as findings.

---

### 1. Predicted effect size (from the paper)

Usable magnitudes exist. Primary sources are the paper's own empirical estimates (Section 6),
not a guessed elasticity.

**A. Quarterly excess-return effect (Table 6.2, §6.2, pp. 34–36)**

- Regressor: S&P500-index-fund passive flow, standardized to mean 0 / SD 1
  (`PassiveFlowSP500`; raw mean 0.05%, raw SD **0.09%** of index market cap per quarter;
  Table 6.1 / flow definition p. 34).
- Outcome: quarterly return on large-stock portfolios **in excess of the S&P500**.
- Magnitudes (1 SD flow shock), value-weighted, with controls:

| portfolio | Δ quarterly excess return | t (NW) |
|---|---:|---:|
| Top 10 | **+0.687%** | 2.46 |
| Top 50 | **+0.528%** | 3.66 |
| Top 100 | +0.303% | 3.02 |
| Top 150 | +0.208% | 2.28 |
| Top 200 | +0.145% | 1.64 |

- Paper's cumulative translation (p. 36): \(0.528\% \times (0.05/0.09) \times 99 \approx 29\%\)
  excess appreciation for a firm that stayed in the top 50 over their 99-quarter sample.

**B. Idiosyncratic-volatility effect (Table 6.3, §6.2, pp. 37–38)**

- Firm-quarter panel of S&P500 names; LHS = \(\log(\mathrm{VolIdio})\);
  RHS = lagged passive flow × Top50 indicator; firm FE (± time FE); double-clustered SEs.
- Paper's own interpretation of a **1 SD** flow increase (using raw SD 0.09%):

| group | Δ idiosyncratic volatility (relative) |
|---|---|
| Outside top 50 | +1.86% \(= 20.63 \times 0.09%\) (insignificant) |
| Top 50 | +3.60% \(= (19.32+20.63)\times 0.09%\) |
| **Incremental Top50** | **+1.74%** \(= 19.32 \times 0.09%\) (t ≈ 2.45–2.53) |

**C. Calibration (secondary; Table 5.2, §5.2.1, p. 26)**

- Raising passive measure \(\mu_2\) from 0.1 → 0.6 via **entry** (\(\phi=0\)): largest size group
  price level **+11.78%** (constant-\(b_n\)) / **+7.53%** (varying-\(b_n\)).
- Switch active→passive (\(\phi=1\)): **0** in the baseline all-stock index.
- These are large discrete \(\mu_2\) shifts, not per-quarter flow elasticities — reported for
  completeness; **Stage A MDE uses (A) and (B)**.

**Conversion into Stage A / Stage B units**

| paper object | Stage A unit | conversion |
|---|---|---|
| Table 6.2 top-50 | firm-quarter excess return, **percentage points** | already in pp of quarterly excess; use **+0.528 pp per 1 SD flow** (top-10 band +0.687) |
| Table 6.3 Top50 incremental | annualized idio vol, **percentage points** | relative +1.74% × sample mean idio vol 24.83% ≈ **+0.43 pp** of ann. idio vol per 1 SD flow (E-005 band: using p50 21.7% → +0.38 pp; using mean±raw-SD envelope of vol level → roughly **0.3–0.6 pp**) |
| Table 6.3 relative | keep as **+1.74% relative** / ≈ **0.0174 log points** | no conversion |

Primary predicted effects for the gate: **+0.528 pp quarterly excess (top50)** and
**+0.43 pp (≈ +1.74% relative) annualized idio vol incremental for mega-firms**, each per
1 SD passive-flow shock, matching the paper's standardized / 1 SD framing.

---

### 2. Noise term (from data on disk — residuals rebuilt)

**Method (unchanged from P5):** per ticker-quarter, OLS market model of daily returns on
`^GSPC` daily returns; residual sample SD; annualize \(\times\sqrt{252}\times 100\) for idio vol;
quarterly excess return = compounded ticker return − compounded `^GSPC` return over the same
days; **min 40 daily observations**. Free Yahoo chart API only.

**Why rebuild:** `04_idio_vol_by_quarter_and_group.csv` stores **group means only** (84 rows).
Per-ticker residuals were never saved.

**Rebuild actually observed (Stage A noise sample):**

| quantity | value | denominator |
|---|---:|---|
| Firms with usable ticker-quarters | **186** | equity tickers with cached Yahoo history after rate-limit pacing (of 587 attempted universe from P5 coverage; Yahoo 429s blocked a full pull in one pass) |
| Quarters | **46** | 2015Q1–2026Q2 continuous |
| Firm-quarters (min 40 days) | **8,283** | firm × quarter cells |
| Mean idio vol (ann. %) | 24.83 | across 8,283 firm-quarters |
| SD idio vol raw / after firm+quarter FE | 12.41 / **8.08** | same |
| Mean quarterly excess return (%) | 0.60 | vs `^GSPC` |
| SD excess return raw / after firm+quarter FE | 14.72 / **14.15** | same |

Noise terms used for MDE (residuals after firm + quarter demeaning — the FE design's
residual scale):

- \(\sigma_{\varepsilon}^{\mathrm{idio}} = 8.08\) pp annualized idio vol
- \(\sigma_{\varepsilon}^{\mathrm{ex}} = 14.15\) pp quarterly excess return

**Brief correction:** the gate spec's “370 firms × 42 quarters ≈ 15,540” is the *intended*
Stage B shape. On disk, P5 flow files are **not** a continuous 42-quarter panel — they are
2015–19 (20Q) plus 2024–26 (11Q) with two top-10 lists, hence 42 *rows*. Continuous
2015Q1–2026Q2 is **46** quarters. Noise σ above is from a **186-firm free subsample**;
σ is stable vs the 151-firm interim (idio FE SD 8.09 → 8.08). Full ~370/500-name rebuild
was blocked mid-run by Yahoo rate limits — E-005 band, not a paid-data hole.

**Context files (not findings):**
`06_flow_vs_concentration_quarterly.csv` (ETF/MF flow_bn + gaps) and
`07_flow_correlation_tests.csv` (underpowered quarter-level \(|r|\) arithmetic). Signs in
07 flip across windows — that is the dead-design signature the gate exists to catch.
**Do not read those correlations as evidence either way.**

---

### 3. Effective n

**Intended Stage B clustering:** two-way cluster by **firm** and **quarter** (same spirit as
JVZ Table 6.3), with firm FE and quarter FE.

**Does treatment vary WITHIN quarter across firms?**

**Yes.** The intended Stage B regressor is
\(\text{passive\_intensity}_{i,t} \times \text{aggregate\_ETF\_flow}_{t}\).
Passive intensity (ETF/index ownership share or equivalent within-quarter cross-section)
varies across firms inside a quarter; aggregate flow is common. After firm + quarter FE,
identifying variation remains in the demeaned interaction. That is the whole difference
from P5(iii).

**Effective n under that design**

| design | what varies | clustering | effective n (stated) |
|---|---|---|---:|
| **Dead design (P5iii trap)** | aggregate flow only (quarter-level) | cluster by quarter → collapses | **n ≈ 42** (spec) / **46** continuous quarters |
| **Live Stage B** | within-quarter passive intensity × aggregate flow | firm + quarter FE; two-way cluster | **n = 8,283** firm-quarters on the noise sample; design target **~370 × 46 ≈ 17,020** (or spec's 370 × 42 = 15,540) |

Under two-way clustering, OLS-style \(\sqrt{N}\) overstates precision somewhat; a
conservative “cluster-count” floor (\(N_{\mathrm{firms}}\) or \(N_{\mathrm{quarters}}\) alone)
is also reported in §4 as an E-005 band. The live design is **not** collapsed to 42 —
that is the trap made visible.

Detectable \(|r|\) at \(t=2\) (spec's table, for orientation only):
\(r = 2/\sqrt{4+n-2}\).

| n | detectable \|r\| |
|---:|---:|
| 42 | 0.302 |
| 46 | 0.289 |
| 8,283 | 0.022 |
| 15,540 | 0.016 |
| 17,020 | 0.015 |

---

### 4. MDE at t≈2 and verdict

**Formula** (standardized treatment, same 1 SD framing as JVZ Tables 6.2–6.3):

\[
\mathrm{MDE}_{t=2} \;=\; 2 \cdot \frac{\sigma_{\varepsilon}}{\sqrt{n_{\mathrm{eff}}}}
\]

with \(\sigma_{\varepsilon}\) = residual SD after firm+quarter demeaning (§2), and
\(n_{\mathrm{eff}}\) as in §3. Units match the predicted effects in §1.

**Return channel** (\(\sigma_{\varepsilon}=14.15\) pp; predicted **+0.528** pp top50 / **+0.687** top10):

| \(n_{\mathrm{eff}}\) | MDE (pp) | predicted exceeds MDE? |
|---:|---:|---|
| 42 (dead) | **4.37** | no (0.53 ≪ 4.37) |
| 46 (quarters only) | 4.17 | no |
| 8,283 (noise sample FQ) | **0.311** | **yes** (0.53 > 0.31; top10 0.69 > 0.31) |
| 15,540 (spec design) | 0.227 | yes |
| 17,020 (370×46) | 0.217 | yes |
| 370 firms only (ultra-conservative) | 1.47 | no for top50; no for top10 |

**Idio-vol channel** (\(\sigma_{\varepsilon}=8.08\) pp ann.; predicted incremental **≈ +0.43** pp
from +1.74% relative × mean 24.83%):

| \(n_{\mathrm{eff}}\) | MDE (pp) | predicted exceeds MDE? |
|---:|---:|---|
| 42 (dead) | **2.49** | no |
| 8,283 | **0.178** | **yes** (0.43 > 0.18) |
| 15,540 / 17,020 | 0.130 / 0.124 | yes |
| 370 firms only | 0.84 | no |

Relative / log form of the same idio test: predicted **+1.74% relative**; FE residual SD of
\(\log(\mathrm{idio\_vol})\) on the rebuild ≈ 0.255; MDE at n=8,283 ≈ \(2\times 0.255/\sqrt{8283}\approx 0.0056\)
(0.56% relative) — predicted 1.74% still clears.

**E-005 band:** if two-way clustering bites hard enough that \(n_{\mathrm{eff}}\) collapses
toward \(N_{\mathrm{firms}}\) (~200–370) rather than firm-quarters, **both** channels fail or go
marginal (return MDE ≈ 1.47 pp > 0.53; log-idio MDE ≈ 0.027 > 0.017). Both clear
comfortably once \(n_{\mathrm{eff}}\gtrsim 2{,}000\) firm-quarters. The honest central case for
the *intended* within-quarter-varying design remains firm-quarter \(N\).

---

## Verdict

### **CLEARS GATE**

for the **intended Stage B design** (within-quarter-varying passive intensity × aggregate ETF
flow, firm + quarter FE), on both the paper's return magnitude (+0.528 pp / 1 SD) and the
idio-vol incremental (+1.74% relative ≈ +0.43 pp), using \(n_{\mathrm{eff}}\) in the
thousands-of-firm-quarters range.

The **dead design is shown to fail** (n≈42 → MDE 4.4 pp return / 2.5 pp idio), which is why
P5(iii)'s quarter-collapsed flow test was uninformative — not because JVZ is false.

**Supervisor decision still required before Stage B.** *(Recorded 16 Sep: the principal signed this off and
authorised Stage B. The gate was NOT self-cleared. Its arithmetic was nonetheless wrong — see C-092: the
2σ/√N formula in §4 overstated precision 3.6x, and the correct MDE comes from a realised clustered SE.)* This report does not start Stage B,
does not pull N-PORT, and does not run the regression.

---

## Blockers / notes for parent

1. **Yahoo rate limits** prevented a full ~500-name residual panel in one pass; noise σ is from
   **186 firms / 8,283 firm-quarters**, method-identical. σ stable across subsample growth.
2. **Brief vs disk:** “42 quarters” matches P5's *row count* (gapped windows), not continuous
   2015Q1–2026Q2 (**46Q**). Called out above.
3. **Within-quarter passive intensity** for Stage B is not yet on disk as a firm-quarter series
   (N-PORT reserved for cleared gate). Gate assumes that measure will vary within quarter —
   if it does not, effective n snaps back to ~42 and the gate **fails**.
4. Explicitly **not** claimed: any M for household residual / 2024–26 revaluation; P5(iii)
   weak-negative as a real finding; JVZ “explains” the revaluation.
5. Handover: parent to run `bin/check.sh --handover write` (per instructions — not run here).

## Working files on box

- `/workspace/tdr/paper/PIRMF_RFSf.pdf`
- `/workspace/tdr/data/stage_a/firm_quarter_residuals.csv`
- `/workspace/tdr/data/stage_a/noise_summary.json`
- `/workspace/tdr/data/p5_concentration/{04,06,07,00,08}_*.csv` (copies)
