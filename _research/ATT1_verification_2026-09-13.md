# ATT1 — Grok's attack on the premium-compression finding, and my verification

**Returned 13 Sep 2026** (Grok in Cursor, parcel `Parcel_ATT1_Premium_Attack_For_Grok_Cursor.md`).
Preserved verbatim below under a correction banner. **Outcome: [C-078].**

**Supervisor verification, 13 Sep — five structural claims re-derived by me, independently of Grok:**

| claim | my check | result |
|---|---|---|
| P/E path 24.35 → 28.60 → 25.22 | P2c monthly series | 24.3468 / 28.6002 / 28.4790 (Dec-25) / 25.2212 — CONFIRMED |
| corr(real yield, residual) = −0.70 | n=282, 2003-01..2026-09 | **−0.6991** — CONFIRMED |
| baseline band 28.4 / 43.1 / 16.5 / 10.9 | recomputed all five baselines | 28.37 / 43.07 / 16.50 / 10.92, ours 35.37 — ALL CONFIRMED |
| Damodaran growth 8.7% → 13.7% | `ERPbymonth.xlsx` fetched 13 Sep | **8.74% → 13.69%** — CONFIRMED |
| Damodaran ERP 4.60% → 4.20% | same file | **4.60% → 4.20%** — CONFIRMED |
| FII30 1.95% → 2.72% | FRED refuses scripted requests | **UNVERIFIED** — not relied on |

Vintage of the external evidence: `data/vintages/damodaran_erp_2026-09-13/ERPbymonth.xlsx`
(sha256 762bee96…). Damodaran's file is overwritten monthly; this copy is the one the finding rests on.

**The fact that separates us from Grok, since both positions are locally right.** Grok reads the 40bp ERP
fall as evidence the residual is contaminated by growth. It is — for the *level*. But a 40bp fall in a
construction that *carries* an explicit growth term, over the same months our growth-free residual falls
49bp, is corroboration of the *change*. Grok concedes this in its own closing line. So the window
compression survives on two independent measures; the level claim does not survive at all.

**Where this lands:** P5 test (ii) — growth versus risk — is no longer a refinement. It is the load-bearing
test, and it now has a specific target: reconcile a −49bp trailing residual with a −40bp growth-adjusted ERP
and a +495bp move in the growth input.

---

## Grok's return, verbatim

Recomputed from `data/vintages/shiller_2026-09-02/` (Shiller `ie_data.xls` + FRED DFII10/DGS10) with the
script's Shapley, not by trusting the write-up. "Today" is June 2026, last month with trailing E.

| # | number recomputed | reproduces? | your value | note |
|---|---|---|---|---|
| 1 | rate effect −2.14 P/E pts | yes | −2.1359 | Shapley on P/E=100/(r+p), Dec-2023→Jun-2026 trailing E; rounds to −2.14 |
| 2 | premium effect +3.01 | yes | +3.0103 | same split; (1)+(2)=ΔP/E +0.8744 **by construction** (identity, not evidence) |
| 3 | multiple +3.6% | yes | +3.591% | P/E 24.3468→25.2212; path is +4.25 (2024), −0.12 (2025), −3.26 (H1-2026) |
| 4 | counterfactual multiple 16.3 | yes | 16.301 | 100/(2.1790+3.9555); 2015-01..2019-12 mean residual, Jun-2026 DFII10 |
| 5 | 54.7% above that counterfactual | yes | 54.722% | 25.221/16.301 − 1; **same gap as #6, different denominator** |
| 6 | 35.4% of today's valuation | yes | 35.368% | (25.221−16.301)/25.221. ATT0 B4 was 35.70% on 2026-YTD *average* E/P. Baseline band: 28.4% (2005-07) to 43.1% (2010-19); 16.5% if baseline=2023; 10.9% if baseline=window-start |
| 7 | 52.2% on CAPE | yes | 52.246% | CAPE 40.150 vs cf 19.173. CAPE residual → ~0 by Sep-2026 (not in headline) |
| 8 | H1-2026 trailing E +22.75% | yes | +22.754% | E 240.63→295.39; **widens** trailing residual in H1, so it *shrinks* #6 vs a Dec-2025 cut |

ATTACK: The −2.14/+3.01 split is an identity, not a finding: E/P := r + residual, and Shapley of 1/(r+p)
sums to ΔP/E by construction. That residual has no growth term, so it is ERP − g, not a risk premium.
Damodaran's own expected-growth input rose from 8.7% (start-Jan-2024) to 13.7% (start-Jul-2026) while his
growth-adjusted ERP (T12m) only fell 4.60%→4.20%. The 16.3× glues a low-g, low-r 2015-19 residual (analyst
g 4–7%) to today's 2.18% real yield — a pairing off the historical (r, residual) manifold (corr −0.70).
Endpoints hide the path: trailing P/E 24.35→28.60 in 2024, then back to 25.22 as earnings jumped. The 35.4%
(level vs 2015-19) and +3.01 (window change) are different objects. Treating the residual as the hole
"money" must fill confuses a price identity with a flow (valuation ≠ money). 30y TIPS rose *more* than 10y
(FII30 1.95%→2.72%) — duration does not save this.

SURVIVES?: partly — the arithmetic and a historically low trailing residual survive; calling it a risk
premium, quoting 35.4% as constant-premium mispricing, and using it as the money-shaped hole do not.

LOAD-BEARING ASSUMPTION: E/P minus 10y TIPS isolates risk pricing rather than expected growth, and the
2015-19 residual is the right ceteris-paribus baseline.

WHAT WOULD SETTLE IT: Damodaran/Fed implied ERP *and* its growth input, month-matched Dec-2023 to Jun-2026
— if ERP is flat after g, the trailing 35.4% is omitted-g (on today's files ERP still fell ~40bp while g
rose ~5pp, so the *window* compression is not fully an artefact; the *level* claim mostly is).

**Sources cited by Grok, resolved by me 13 Sep:** Damodaran histimpl page and `ERPbymonth.xlsx`
(pages.stern.nyu.edu) — BOTH RESOLVE, figures confirmed. FRED FII30 — could not resolve from a script.
