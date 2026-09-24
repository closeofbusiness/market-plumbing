# P4 — Russell reconstitution elasticity pilot (15 September 2026)

> **[C-086]** The first stage of this design fails on free data. Do not quote a P4 multiplier, a P4 LATE, or a reconstitution-window return as a price-impact coefficient, and do not rescale any of these estimates to the market (C-077, C-080). IWB/IWM holdings are not the official Russell lists.

**Status: RESULT.** Ranked item 4 (= Tier B B3). Spec `_research/2026-09-12-P4-Flow-Elasticity-Spec.md`. The spec's own null clause is the finding: no discontinuity distinguishable from zero once local-linear slope, placebos and the window grid are applied. Grid in `data/p4/rd_grid.csv`. Panel `data/p4/panel.csv`; CARs `data/p4/car_panel.csv`.

Serves goal row **channel (d)** — market-structure flows such as the passive bid and ETF creation. Stock-level LATE does not answer the market-level money-to-price question even if it had been identified (B0; C-077/C-080).

## What was estimated

Fuzzy RD at the Russell 1000/2000 cutoff, June reconstitutions **2022–2026** pooled with year fixed effects. Local linear in rank, HC1 standard errors. Pre-registered objects: assignment, Δ13F ownership (first stage), market-model CAR around the last Friday of June (reduced form), 2SLS only if the first stage survives. Kill switch: first-stage *F* below 10. Bandwidth grid *h* ∈ {100, 200, 300} around rank 1000. CAR windows [0,0], [−1,+1], [−5,+5], [−20,+5], [−60,0], [+1,+20] (Chinco–Sammon sensitivity). Placebos at cutoffs 700 and 1300.

Effective dates used: 2022-06-24, 2023-06-23, 2024-06-28, 2025-06-27, 2026-06-26.

## Free-data substitutes (named, because they bind)

Official May float-adjusted Russell ranks and the reconstitution membership lists are not free (S&P DJI / FTSE Russell 403 to scripted access; no CRSP). Three substitutes were used; each is a hypothesis about how the cutoff is written down, not the cutoff itself.

**Membership.** Quarter-end N-PORT holdings of iShares Russell 1000 ETF (IWB, series S000004347) and iShares Russell 2000 ETF (IWM, S000004344), iShares Trust CIK 0001100663. Twenty filings, Mar/Jun 2022–2026. Accessions in `data/p4/nport_accessions.json`. IWB 2026-06-30 is accession `0001004726-26-007016`; IWM `0002071691-26-019749`. Equity CUSIPs only (`assetCat=EC`). IWB is a **sampling** ETF: name counts 965–1024, not a 1,000-name replica. N-PORT public files are **quarter-end** (31 Mar / 30 Jun), not the May rank date.

**Running variable.** March 13F long-stock dollar-holdings rank (largest = 1) among CUSIPs that appear in IWB ∪ IWM that year. SEC bulk Form 13F data sets, Mar and Jun windows 2022–2026 (`VALUE` in thousands; `PUTCALL` empty = long stock; `SSHPRNAMTTYPE=SH`). Combined 13F+N-PORT ownership share is not constructable: N-PORT here is the two ETFs, not the fund universe.

**Returns.** Yahoo v8 daily closes 2022-05-01 → 2026-07-31, CUSIP→ticker via OpenFIGI then Yahoo search; SPY market model estimated on trading days [−120, −21] before the effective date. 749 tickers priced of 860 unique in ranks 800–1200; CAR defined for **1,325** of 2,005 year-stock cells in that band (the rest lack a usable price path). No CRSP delisting adjustment.

**Artifacts retained.** The raw SEC bulk 13F zips (ten quarters) and the CUSIP→ticker map were **not** kept. Retained: `data/p4/13f_by_cusip.csv` (35,490 rows; all ten windows present, 3,454–3,594 CUSIPs each — re-checked 15 Sep), `panel.csv`, `car_panel.csv`, `rd_grid.csv`, and the two N-PORT XMLs in `data/vintages/p4_2026-09-15/`. Re-running from raw means re-downloading the bulk 13F data sets at the windows named above. OpenFIGI coverage on the full IWB∪IWM CUSIP union was reported as 3,691 of 4,143 (89.1%) — UNVERIFIED: the map was not retained and cannot now be re-checked. The band figure above (749 of 860 priced in ranks 800–1,200) is the one the grid uses and is reproducible from `car_panel.csv`.

## Assignment

P(in IWB at 30 Jun) falls smoothly with rank. Pooled:

| rank band | n | P(IWB Jun) |
|---:|---:|---:|
| 1–200 | 1,000 | 0.998 |
| 201–400 | 1,000 | 0.988 |
| 401–600 | 1,000 | 0.970 |
| 601–800 | 1,000 | 0.826 |
| 801–1,000 | 1,000 | 0.568 |
| 1,001–1,200 | 1,000 | 0.323 |
| 1,201–1,500 | 1,500 | 0.117 |
| 1,501–2,000 | 2,500 | 0.043 |

Local linear jump in IWB June membership on *Z* = 1{rank ≤ 1,000}:

| *h* | n | τ | se | *t* |
|---:|---:|---:|---:|---:|
| 100 | 1,005 | −0.033 | 0.061 | −0.54 |
| 200 | 2,005 | 0.070 | 0.043 | 1.61 |
| 300 | 3,005 | 0.046 | 0.035 | 1.32 |

Primary bandwidth *h*=200: *t*=1.61, *F*≈2.6, below the kill switch. By year at *h*=200 the same *t* is 1.66 (2022), −0.21 (2023), −0.41 (2024), 0.73 (2025), 1.84 (2026) — no year carries the cutoff. Placebos at *h*=200: cutoff 700 *t*=1.27; cutoff 1,300 *t*=−1.02. IWB **March** membership on the same *Z* is *t*=1.18 at *h*=200 — no jump the quarter before either.

McCrary density of rank is not a test: we assigned ranks 1…*N* by construction, so the density is mechanically flat.

## Why the substitute smears the cutoff

IWB holdings barely move through the 2024 reconstitution. Jaccard of IWB equity CUSIPs, 31 Mar vs 30 Jun:

| year | Jaccard | adds | drops | IWB Jun *n* |
|---:|---:|---:|---:|---:|
| 2022 | 0.902 | 52 | 48 | 969 |
| 2023 | 0.934 | 35 | 34 | 1,008 |
| 2024 | **0.992** | **4** | **4** | 1,005 |
| 2025 | 0.934 | 39 | 30 | 1,015 |
| 2026 | 0.891 | 68 | 49 | 1,024 |

CUSIPs that switch IWM→IWB / IWB→IWM (Mar origin, Jun destination, not already in the destination): 2022 21/34, 2023 22/25, **2024 0/0**, 2025 17/23, 2026 40/35. A sampling ETF that does not rebalance at the cutoff cannot assign treatment. Wide-bin correlation between 13F rank and IWB membership is real; the local jump the design needs is not.

## First stage (Δ13F) and reduced form (CAR)

Δ13F = (June long shares / March long shares) − 1, same 13F bulk files.

| object | *h* | n | τ | se | *t* |
|---|---:|---:|---:|---:|---:|
| Δ13F share | 100 | 1,005 | −0.013 | 0.015 | −0.87 |
| Δ13F share | 200 | 2,004 | 0.012 | 0.016 | 0.78 |
| Δ13F share | 300 | 3,003 | 0.012 | 0.017 | 0.69 |
| CAR[0,0] | 200 | 1,325 | −0.0031 | 0.0020 | −1.51 |
| CAR[−1,+1] | 200 | 1,325 | −0.0001 | 0.0041 | −0.02 |
| CAR[−5,+5] | 200 | 1,325 | 0.0144 | 0.0093 | 1.55 |
| CAR[−20,+5] | 200 | 1,325 | 0.0109 | 0.0151 | 0.72 |
| CAR[−60,0] | 200 | 1,325 | 0.0030 | 0.0177 | 0.17 |
| CAR[+1,+20] | 200 | 1,325 | 0.0029 | 0.0132 | 0.22 |

No cell in the grid has |*t*| ≥ 2. CAR *h*=100 is the same sign and still |*t*|<1 except [−5,+5] *t*=0.91. By year, CAR[−5,+5] at *h*=200: 2022 unusable (price coverage below the *n*=30 floor), 2023 *t*=−1.66, 2024 *t*=0.18, 2025 *t*=1.46, 2026 *t*=1.79. The Chinco–Sammon window that moved their estimate from −39 to −1 does not move ours: every window is noise around zero.

**2SLS is not reported.** Dividing a zero reduced form by a zero first stage is not an elasticity.

## What this is and is not

This is a **failed identification on the free substitutes**, reported as a result under E-005 (direction plus band: the local jump is 7pp with a standard error of 4pp, consistent with zero; the CAR[−5,+5] ITT is 1.4pp with se 0.9pp). Confidence is **high** that *this* design on *these* files does not recover a first stage. Confidence is only **medium** that the index effect itself is gone in 2022–26: official May ranks plus full-replication membership could still jump, and this pass cannot see them. Paying for those files is closed (E-005).

It is **not** a market-level multiplier, **not** a replacement for the borrowed *M* that ATT0/P3R killed, and **not** a reason to treat the reduced-form CAR as if it were δ. The spec already forbade rescaling a stock-level LATE by market weight; there is no LATE to rescale.

The remaining free designs in the spec are (c) mandated/mechanical flows (leveraged-ETF rebalancing is the untested Green remainder) and (a) a Koijen–Yogo demand system, which is months not an agent-week. Neither is opened by this pass.

## Do not say

- Any P4 multiplier, P4 LATE, or δ/β from these files.
- That IWB/IWM holdings *are* the Russell reconstitution.
- That 13F rank *is* May float-adjusted cap.
- That a null ITT CAR is evidence the passive bid does not move prices. The design never assigned the bid.
