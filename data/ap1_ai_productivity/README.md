# AP1: is AI raising productivity and profit margins where it is used? (build of 16 Nov 2026)

## What was asked

Since 2023, have industries that use more AI seen faster growth in output per worker and a larger rise in the gross operating surplus share of value added, compared with other industries and with their own 2017-19 change? Registered blind before any industry figure was read (`_research/2026-11-16-AP1-AI-Productivity-Spec.md`, version 2, sha256 `822c7c8a7eac38dadabbb1860eb0eaf0972709c6eb8487a237ce8398b5a8866d`).

## Result table

| statement | label | n | rank correlation | p (positive) | p (negative) | leave-one-out range |
|---|---|---|---|---|---|---|
| AP1-P1 (P1: AI use vs real VA per FTE growth 2023-25) | INCONCLUSIVE | 13 | 0.4396 | 0.06846 | 0.93457 | 0.2867 to 0.6224 |
| AP1-P2 (P2: AI use vs real VA per FTE growth 2023-25 minus 2017-19) | INCONCLUSIVE | 13 | 0.0604 | 0.42265 | 0.58435 | -0.1538 to 0.1888 |
| AP1-P3 (P3: AI use vs GOS share change 2023-25 (pp)) | SUPPORT | 15 | 0.6607 | 0.00471 | 0.99549 | 0.6044 to 0.8066 |
| AP1-P4 (P4: AI use vs GOS share change 2023-25 minus 2017-19 (pp)) | SUPPORT | 15 | 0.8786 | 0.00006 | 0.99995 | 0.8505 to 0.8945 |

Rule (version 2): SUPPORT if one-sided permutation p <= 0.05 (positive) and outside two Monte Carlo standard errors of 0.05, and every leave-one-out rho > 0; AGAINST if one-sided permutation p <= 0.05 (negative) and outside two Monte Carlo standard errors of 0.05, and every leave-one-out rho < 0; otherwise INCONCLUSIVE. 100000 permutations of the AI values, seed 20261116, p = (1 + k) / (100000 + 1).

## Asymmetry and limits

- **Version-2 asymmetry.** Neither label identifies AI as the cause: SUPPORT says the pattern T4 predicts is present (industries that use more AI gained more in output per worker or in gross-operating-surplus share), and does not show AI as the cause: rates, prices, post-pandemic recovery, or fast-growing firms adopting AI because they are growing can rank industries similarly. AGAINST says the pattern is absent or reversed on this data (a significant negative correlation; near zero is INCONCLUSIVE).
- **P3 and P4 are gross-operating-surplus shares, not profit margins (ruling 2).** P3 and P4 measure the gross operating surplus share of value added (`GOS / VA`), not profit margins: gross operating surplus includes depreciation (so heavier software and data-centre investment raises it), proprietors' income, net interest, and own-account software investment, and BEA revises this component most.
- **Definitions (ruling 10).** The two BEA files share the 2017 NAICS rows; the surplus is an establishment-basis residual built partly from company tax data; BTOS is a separate survey of employer firms.
- **Revision re-score (ruling 6).** Because 2023 and 2025 remain open to BEA revision, this build records each sheet's file vintage; a calendar row re-runs AP1 after BEA's 2027 annual update and reports any label change.
- **BTOS series and coverage.** The BTOS series is the original wording (`AI Core Questions (Original)`), cycles 2024-2025 (46 cycles ending before 17 Nov 2025). BTOS measures AI use by existing employers, firm-weighted. FTE counts employees, not the self-employed.
- **Multiplicity.** Four statements are scored with no multiplicity adjustment.
- **BEA release/vintage text:** TVA105-A: not stated; TVA106-A: not stated; TVA113-A: not stated.

## Denominators and national benchmark

- **P1/P2 kept industries (n=13):** 441, 511, 512, 523, 524, 541, 561, 621, 713, 722, 23, 31-33, 42.
- **P3/P4 kept industries (n=15):** 441, 511, 512, 523, 524, 541, 561, 611, 621, 624, 713, 722, 23, 31-33, 42.
- **Dropped for 46-cycle AI rule (n=0):** none.
- **Dropped from P1/P2 for non-positive real VA (n=0):** none.
- **National private industries (`Private industries`, FTE `A4303C`):** g_post (2023-25) = 0.0483, g_pre (2017-19) = 0.0239, diff = 0.0244.
- **Weighted Pearson (2019 nominal VA weights):** P1=0.2653 (n=13), P2=-0.0114 (n=13), P3=0.5483 (n=15), P4=0.5816 (n=15).

## Files

`registered.csv` (written before any statistic), `scores.csv`, `detail.csv`, `vintages.csv`, `README.md`. Raw downloads stay in `data/vintages/ap1` (gitignored).

