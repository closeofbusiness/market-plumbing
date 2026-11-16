# AV1: are share prices ahead of AI earnings? (build of 16 Nov 2026)

## What was asked

Did the AI complex's pooled price-to-earnings multiple rise from January 2023 to January 2026, and by more than the rest of the US market's? Registered blind before any multiple, market value or earnings figure by industry was read (`_research/2026-11-16-AV1-AI-Valuation-Spec.md`, version 2, sha256 `c8b3f868d1ad9525aad9307934d29f480c5315e36f0cf8ec9f500559d4d526da`).

## Result table

| statement | label | K (AI) | n (other) | G (log pts) | delta_M AI | delta_M other | p (positive) | p (negative) | LOO G range |
|---|---|---|---|---|---|---|---|---|---|
| AV1-P1 (pooled multiple change Jan 2023 -> Jan 2026) | INCONCLUSIVE | 7 | 85 | 0.0346 | 0.4157 | 0.3811 | 0.39076 | 0.60906 | -0.1404 to 0.3036 |

Rule (version 2): SUPPORT if K >= 7, delta_M(AI pool) > 0, G > 0, one-sided permutation p <= 0.05 (outside two Monte Carlo standard errors of 0.05), and every leave-one-out with K - 1 meets the same three conditions; AGAINST if K >= 7, delta_M(AI pool) < 0, G < 0, one-sided permutation p <= 0.05 (outside two Monte Carlo standard errors of 0.05), and every leave-one-out meets the same three conditions; otherwise INCONCLUSIVE. 100000 permutations reassigning the AI label to K kept industries, seed 20261116, p = (1 + k) / (100000 + 1).

## Asymmetry, universe, and definitions

- **Asymmetry (version 2).** SUPPORT says prices of the AI complex rose faster than its earnings, relative to other industries: the pattern T6 predicts. It does not show the market is wrong; a higher multiple can be a correct forecast of earnings still to come, or a lower discount rate for those firms. AGAINST says the AI complex's earnings kept pace with or outran its prices over the window: the gains were being delivered, not only priced. Neither speaks to the level of the multiple, only to its change.
- **Seven named industries, not "AI firms" (ruling 3).** AV1 tests seven named industries (Semiconductor, Semiconductor Equip, Software (System & Application), Software (Internet), Computer Services, Computers/Peripherals, Telecom. Equipment), not "AI firms": industry buckets hold non-AI business and the AI firms are not all in them. A frozen firm list needs firm-level values and is AV2.
- **Universe (ruling 10).** Damodaran's frame: firms classified by country of incorporation (the US), all listed firms with a market price, no size cut-off.
- **Earnings definition (ruling 6).** Aggregate net income of all firms in the group (GAAP, including one-off items); Damodaran's documentation says trailing data run through the third quarter of the prior year.

## Reported, not labelled

- **Price and earnings legs (Jan 2023 -> Jan 2026):** AI pool dln(Mkt Cap) = 0.9526, dln(Net Income) = 0.5370; comparison pool dln(Mkt Cap) = 0.4447, dln(Net Income) = 0.0636.
- **Version 1 P1 (PE files, equal-weighted):** diff mean = 0.2547, diff median = 0.3336 (n_ai=6, n_other=76).
- **Version 1 P2 (PE files, delta_m_post - delta_m_pre):** diff mean = 0.1993, diff median = 0.0815 (n_ai=6, n_other=66).
- **January 2022 baseline (DollarUS21 -> current):** G = 0.0500; **January 2024 -> January 2026:** G = -0.1516.
- **Money-making-firms multiple (PE files):** diff mean = 0.1395, diff median = 0.2353.
- **AI build-out group (Power; Utility (General); Electrical Equipment; Engineering/Construction):** G = -0.2594 (n_group=4, n_other=88).
- **BTOS-sector Spearman (2024-25 46-cycle sector AI vs PE delta_m_post):** rho = 0.0267 (n=64).

## Files

`registered.csv` (written before any statistic), `scores.csv`, `detail.csv`, `vintages.csv`, `README.md`. Raw `.xls` files stay in `data/vintages/av1` (gitignored).

