# AJ1: does AI create more jobs than it displaces? (build of 16 Nov 2026)

## What was asked

Since 2023, have industries that use more AI gained or lost employment and job openings, compared with other industries and with their own 2017-19 trend? Registered blind before any employment or job-openings figure by industry was read (`_research/2026-11-16-AJ1-AI-Jobs-Spec.md`, version 2, sha256 `53b53f49a93d55910f03088a9b5bbbbfcbd46e0bf6617fce8238efc8c45571c1`).

## Result table

| statement | label | n | rank correlation | p (positive) | p (negative) | leave-one-out range |
|---|---|---|---|---|---|---|
| AJ1-P1 (P1: AI use vs CES employment growth 2023-25) | INCONCLUSIVE | 19 | -0.2263 | 0.82671 | 0.17518 | -0.3065 to -0.0960 |
| AJ1-P2 (P2: AI use vs CES growth 2023-25 minus 2017-19) | INCONCLUSIVE | 19 | -0.2579 | 0.86012 | 0.14174 | -0.3664 to -0.1290 |
| AJ1-P3 (P3: AI use vs JOLTS openings level growth 2023-25) | SUPPORT | 15 | 0.7954 | 0.00031 | 0.99970 | 0.7657 to 0.8405 |

Rule (version 2): SUPPORT if one-sided permutation p <= 0.05 (positive) and outside two Monte Carlo standard errors of 0.05, and every leave-one-out rho > 0; AGAINST if one-sided permutation p <= 0.05 (negative) and outside two Monte Carlo standard errors of 0.05, and every leave-one-out rho < 0; otherwise INCONCLUSIVE. 100000 permutations of the AI values, seed 20261116, p = (1 + k) / (100000 + 1).

## Asymmetry and limits

- **Neither label identifies AI as the cause.** Labels name the cross-industry pattern, never the cause: rates, the end of the post-pandemic hiring boom, software-sector cycles, or fast-growing industries adopting AI because they are growing can rank industries similarly.
- **Neither label measures the economy-wide net.** Jobs AI creates in other industries (data-centre construction, power, chips) and displaced workers hired elsewhere are outside an industry cross-section.
- **BTOS series and coverage.** The BTOS series is the original wording (`AI Core Questions (Original)`), cycles 2024-2025 (46 cycles ending before 17 Nov 2025). BTOS measures AI use by existing employers, and this test is a rank association among firm-weighted AI rates in a suppression-selected set of industries.
- **Multiplicity.** Three statements are scored with no multiplicity adjustment.
- **Release dates:** CES: preliminary; JOLTS: preliminary.

## Denominators and weights

- **CES labelled subsectors (n=19):** 238, 423, 424, 441, 512, 518, 522, 524, 531, 541, 561, 611, 621, 624, 711, 713, 722, 811, 812.
- **CES dropped subsectors (n=64):** 113 (AI share published in 0 of 46 cycles (suppressed in 46)); 114 (AI share published in 0 of 46 cycles (suppressed in 46)); 115 (AI share published in 1 of 46 cycles (suppressed in 45)); 211 (AI share published in 0 of 46 cycles (suppressed in 46)); 212 (AI share published in 0 of 46 cycles (suppressed in 46)); 213 (AI share published in 0 of 46 cycles (suppressed in 46)); 221 (AI share published in 4 of 46 cycles (suppressed in 42)); 236 (AI share published in 45 of 46 cycles (suppressed in 1)); 237 (AI share published in 5 of 46 cycles (suppressed in 41)); 311 (AI share published in 17 of 46 cycles (suppressed in 29)); 312 (AI share published in 17 of 46 cycles (suppressed in 29)); 313 (AI share published in 0 of 46 cycles (suppressed in 46)); 314 (AI share published in 1 of 46 cycles (suppressed in 45)); 315 (AI share published in 2 of 46 cycles (suppressed in 44)); 316 (AI share published in 0 of 46 cycles (suppressed in 46)); 321 (AI share published in 3 of 46 cycles (suppressed in 43)); 322 (AI share published in 0 of 46 cycles (suppressed in 46)); 323 (AI share published in 35 of 46 cycles (suppressed in 11)); 324 (AI share published in 0 of 46 cycles (suppressed in 46)); 325 (AI share published in 9 of 46 cycles (suppressed in 37)); 326 (AI share published in 3 of 46 cycles (suppressed in 43)); 327 (AI share published in 1 of 46 cycles (suppressed in 45)); 331 (AI share published in 0 of 46 cycles (suppressed in 46)); 332 (AI share published in 37 of 46 cycles (suppressed in 9)); 333 (AI share published in 22 of 46 cycles (suppressed in 24)); 334 (AI share published in 22 of 46 cycles (suppressed in 24)); 335 (AI share published in 4 of 46 cycles (suppressed in 42)); 336 (AI share published in 3 of 46 cycles (suppressed in 43)); 337 (AI share published in 5 of 46 cycles (suppressed in 41)); 339 (AI share published in 33 of 46 cycles (suppressed in 13)); 425 (AI share published in 44 of 46 cycles (suppressed in 2)); 442 (AI share published in 17 of 46 cycles (suppressed in 29)); 443 (AI share published in 18 of 46 cycles (suppressed in 28)); 444 (AI share published in 13 of 46 cycles (suppressed in 33)); 445 (AI share published in 27 of 46 cycles (suppressed in 19)); 446 (AI share published in 35 of 46 cycles (suppressed in 11)); 447 (AI share published in 2 of 46 cycles (suppressed in 44)); 448 (AI share published in 40 of 46 cycles (suppressed in 6)); 451 (AI share published in 34 of 46 cycles (suppressed in 12)); 452 (AI share published in 0 of 46 cycles (suppressed in 46)); 453 (AI share published in 44 of 46 cycles (suppressed in 2)); 454 (abolished in NAICS 2022 (spec ruling 5)); 481 (AI share published in 0 of 46 cycles (suppressed in 46)); 483 (AI share published in 0 of 46 cycles (suppressed in 46)); 484 (AI share published in 32 of 46 cycles (suppressed in 14)); 485 (AI share published in 7 of 46 cycles (suppressed in 39)); 486 (AI share published in 0 of 46 cycles (suppressed in 46)); 487 (AI share published in 0 of 46 cycles (suppressed in 46)); 488 (AI share published in 19 of 46 cycles (suppressed in 27)); 492 (AI share published in 8 of 46 cycles (suppressed in 38)); 493 (AI share published in 1 of 46 cycles (suppressed in 45)); 511 (matched to CES 513, scope changed materially in NAICS 2022 (spec ruling 5; reported only)); 515 (AI share published in 20 of 46 cycles (suppressed in 26)); 517 (AI share published in 33 of 46 cycles (suppressed in 13)); 519 (scope changed materially in NAICS 2022 (spec ruling 5; reported only)); 523 (CES 523 includes NAICS 525, which BTOS excludes (spec ruling 6; reported only)); 532 (AI share published in 11 of 46 cycles (suppressed in 35)); 533 (AI share published in 6 of 46 cycles (suppressed in 40)); 551 (AI share published in 7 of 46 cycles (suppressed in 39)); 562 (AI share published in 11 of 46 cycles (suppressed in 35)); 622 (AI share published in 0 of 46 cycles (suppressed in 46)); 623 (AI share published in 20 of 46 cycles (suppressed in 26)); 712 (AI share published in 26 of 46 cycles (suppressed in 20)); 721 (AI share published in 36 of 46 cycles (suppressed in 10)).
- **JOLTS private child industries (n=15):** 230000, 320000, 340000, 420000, 440000, 480099, 510000, 520000, 530000, 540099, 610000, 620000, 710000, 720000, 810000.
- **Sector 55 share of 54+55+56 2019 CES employment:** 11.78%. **Utilities (22) 2019 share:** not fetched (no CES 22 or 48-49 series in spec's 40-series list).
- **National CES private employment (`CEU0500000001`):** g_post (2023-25) = 0.0140, g_pre (2017-19) = 0.0320, diff = -0.0180, g_1923 = 0.0366.
- **Weighted Pearson (2019 CES employment weights, n=19):** P1 = -0.0807, P2 = -0.2346.

## Files

`registered.csv` (written before any statistic), `scores.csv`, `detail.csv`, `vintages.csv`, `README.md`. Raw JSON replies stay in `data/vintages/aj1` (gitignored).

