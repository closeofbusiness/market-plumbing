# AF1: did industries that use more AI see more new business applications? (build of 15 Nov 2026)

## What was asked

A published note argues that AI is raising the formation of new companies. Its charts show US business applications rising, but nothing in them measures AI. This test asks the one question free Census data can answer: **after 2023, did the industries whose existing firms use more AI see a bigger rise in new business applications than the industries that use less, and was that bigger than the same ranking showed before AI (2017 to 2019)?** It is a comparison across industries. It was registered before any industry-level application count was read (`_research/2026-11-15-AF1-AI-Company-Formation-Spec.md`, version 2, sha256 `5f4a4dd08c08015ebb83e0c76bca531f18f3a6dfaddf5eb36be83e2730f75969`).

## The answer

- **Growth after 2023 against AI use (P1, business applications):** INCONCLUSIVE - the data do not decide. Spearman rank correlation 0.3978 across 14 sectors; one-sided permutation p for a positive value 0.0812.
- **The change against 2017-19 (P2):** SUPPORT - the predicted pattern is present. Rank correlation 0.4989; p for a positive value 0.0337.
- **The same two on applications with planned wages (P1w, P2w):** INCONCLUSIVE and INCONCLUSIVE.
- **National applications still rising (P3):** SUPPORT. Mean monthly applications in January to November 2025 were 7.3% above January to November 2024 (478,332 against 445,842).

- **How much weight the labelled result bears:** of the four labelled industry tests, SUPPORT 1, INCONCLUSIVE 3, AGAINST 0. Without sectors 51 and 54 (reported, not labelled), P1 is 0.1538 (p 0.3161) and P2 is 0.3007 (p 0.1693); with the 14-sector sample the label can change when one or two sectors move.

SUPPORT here means only that the cross-industry pattern the AI thesis predicts is present; AGAINST means it is absent or reversed. Neither label identifies AI as the cause (see the limits below).

## Result table

Denominators: 14 sectors kept (of 19 BTOS sectors with an AI row; 5 dropped, listed below); months used = January to November, 11 months, in each of 2017, 2019, 2023 and 2025; 10000 random permutations of the AI ranking, seed 20261115.

| statement | label | rank correlation | p (positive) | p (negative) | leave-one-sector-out range |
|---|---|---|---|---|---|
| P1: AI use vs growth 2023 to 2025, business applications | INCONCLUSIVE | 0.3978 | 0.0812 | 0.9212 | 0.2967 to 0.5659 |
| P2: AI use vs that growth minus 2017-19 growth, business applications | SUPPORT | 0.4989 | 0.0337 | 0.9681 | 0.3736 to 0.6319 |
| P1w: as P1, applications with planned wages | INCONCLUSIVE | 0.3099 | 0.1420 | 0.8619 | 0.1758 to 0.4396 |
| P2w: as P2, applications with planned wages | INCONCLUSIVE | 0.3758 | 0.0921 | 0.9099 | 0.2473 to 0.5000 |
| P3: national applications, Jan-Nov 2025 vs Jan-Nov 2024 | SUPPORT | +7.29% | | | |

Rule (registered): SUPPORT if the one-sided permutation p-value for a positive correlation is at most 0.05 **and** every leave-one-sector-out correlation is positive; AGAINST if the one-sided p-value for a negative correlation is at most 0.05; otherwise INCONCLUSIVE. P3 is SUPPORT if 2025 is higher, AGAINST if equal or lower.

## The sectors

Mean monthly business applications (not seasonally adjusted, January to November) and growth in log points (0.10 is about 10.5%).

| sector | AI use, mean % of firms | 2017 | 2019 | 2023 | 2025 | g_pre (2017 to 2019) | g_post (2023 to 2025) |
|---|---|---|---|---|---|---|---|
| 23 Construction | 2.38 | 29,080 | 32,694 | 47,039 | 44,314 | 0.117 | -0.060 |
| 31 Manufacturing (31-33) | 3.34 | 5,691 | 5,719 | 7,879 | 8,366 | 0.005 | 0.060 |
| 42 Wholesale trade | 3.85 | 8,648 | 8,571 | 10,893 | 10,173 | -0.009 | -0.068 |
| 44 Retail trade (44-45) | 4.19 | 38,329 | 44,282 | 82,826 | 99,144 | 0.144 | 0.180 |
| 48 Transportation and warehousing (48-49) | 2.08 | 17,109 | 20,243 | 33,945 | 30,655 | 0.168 | -0.102 |
| 51 Information | 20.90 | 6,206 | 6,234 | 8,737 | 9,427 | 0.005 | 0.076 |
| 53 Real estate and rental | 9.44 | 17,743 | 19,016 | 25,090 | 22,059 | 0.069 | -0.129 |
| 54 Professional, scientific and technical services | 16.25 | 36,061 | 38,619 | 57,717 | 61,900 | 0.069 | 0.070 |
| 56 Administrative and waste services | 6.08 | 18,512 | 20,359 | 35,230 | 31,723 | 0.095 | -0.105 |
| 61 Educational services | 12.23 | 4,522 | 5,053 | 6,919 | 7,597 | 0.111 | 0.093 |
| 62 Health care and social assistance | 7.05 | 17,391 | 19,130 | 27,908 | 29,226 | 0.095 | 0.046 |
| 71 Arts, entertainment and recreation | 6.47 | 9,604 | 9,827 | 13,728 | 13,270 | 0.023 | -0.034 |
| 72 Accommodation and food services | 1.88 | 14,516 | 15,662 | 25,984 | 25,085 | 0.076 | -0.035 |
| 81 Other services | 3.10 | 24,460 | 27,860 | 45,054 | 44,166 | 0.130 | -0.020 |

**Kept (14):** 23 Construction, 31 Manufacturing (31-33), 42 Wholesale trade, 44 Retail trade (44-45), 48 Transportation and warehousing (48-49), 51 Information, 53 Real estate and rental, 54 Professional, scientific and technical services, 56 Administrative and waste services, 61 Educational services, 62 Health care and social assistance, 71 Arts, entertainment and recreation, 72 Accommodation and food services, 81 Other services.

**Dropped (5):**

- 11 Agriculture, forestry, fishing: AI share published in 2 of 46 cycles (suppressed in 44).
- 21 Mining: AI share published in 3 of 46 cycles (suppressed in 43).
- 22 Utilities: AI share published in 4 of 46 cycles (suppressed in 42).
- 52 Finance and insurance: BTOS excludes NAICS 525 but BFS includes it (spec ruling 7).
- 55 Management of companies: AI share published in 7 of 46 cycles (suppressed in 39).

A sector is kept only if its AI share is published in all 46 survey cycles of 2024-2025, so no sector's average is built from a censored subset, and it is a sector in the Census application series. The kept sectors hold 91.4% of national applications in January to November 2025 (the rest: dropped sectors and applications with no industry code).

## Reported, not labelled

Each is a one-off robustness item; none sets a label. Denominators as stated in each line.

- **Without sectors 51 (information) and 54 (professional services), the two largest AI users** (12 sectors; one-sided p for a positive value in brackets): business applications P1 0.1538 (0.3161), P2 0.3007 (0.1693); planned wages P1w 0.1329 (0.3359), P2w 0.1538 (0.3085).
- **Weighted correlation** (Pearson on the raw AI share and the raw growth, each of the 14 sectors weighted by its mean monthly applications in January to November 2019, weights summing to 273,270): AI use against g_post 0.2399; against g_post minus g_pre 0.4525.
- **Grok's shorter post window (2024 to 2025, 14 sectors):** AI use against log(mean 2025) minus log(mean 2024): rank correlation 0.4857, p positive 0.0415, leave-one-out range 0.3956 to 0.5934 (business applications); 0.3231, p 0.1287 (planned wages). Against that growth minus 2018-to-2019 growth, a matched one-year pre-period: 0.6088, p 0.0124 (business applications); 0.6088, p 0.0128 (planned wages). Against that growth minus the registered 2017-to-2019 growth: 0.3846, p 0.0870 (business applications).
- **Applications with no industry code, share of the national January-November total** (11 months in each year): 2017: 1.02% of business applications, 0.64% of planned-wage applications; 2018: 1.22% of business applications, 0.60% of planned-wage applications; 2019: 1.32% of business applications, 0.56% of planned-wage applications; 2023: 2.10% of business applications, 0.95% of planned-wage applications; 2024: 2.03% of business applications, 0.50% of planned-wage applications; 2025: 2.14% of business applications, 0.46% of planned-wage applications. They belong to no sector, so they are outside every statistic above.

## Method

- **Applications.** Census Business Formation Statistics, monthly file, **not seasonally adjusted**, United States, by sector: business applications (BA) and applications with planned wages (WBA). Results speak of applications, not companies. The Census data dictionary labels the grouped codes only as Manufacturing, Retail Trade, and Transportation and Warehousing; they are read here as NAICS 31-33, 44-45 and 48-49. Vintage: the November 12, 2026 release, file `bfs_monthly.csv` (sha256 `47975a1c7bca0aad7e8206bc40cbf4545c84b4cf5cc44aa9aeb8380b1b57b0cf`).
- **Growth.** For each sector and year, the mean monthly applications over January to November (the same eleven months every year, which keeps the broken December 2025 and seasonality out). g_post = log(mean 2025) minus log(mean 2023); g_pre = log(mean 2019) minus log(mean 2017). P1 correlates AI use with g_post; P2 with g_post minus g_pre.
- **AI use.** Census Business Trends and Outlook Survey, question 7 ("use AI in producing goods or services"), share answering Yes, mean over the 46 cycles of 2024-2025 that end before 17 Nov 2025, per sector, computed by the CV1-P6 code (`bin/cv1_confidence_velocity.py`, imported, not copied).
- **Sector codes.** BFS already publishes manufacturing (31-33), retail trade (44-45) and transportation and warehousing (48-49) as grouped codes (NAICSMNF, NAICSRET, NAICSTW); these are mapped to BTOS sectors 31, 44 and 48. The script's grouping function would sum separate two-digit codes if they were published (it is tested), but here no summing was needed.
- **Label by permutation.** The AI values are shuffled across sectors 10000 times (fixed seed 20261115), growth held fixed; the one-sided p-value is (1 + number of shuffles at least as extreme) / (10000 + 1).
- **Leave-one-out.** For SUPPORT every one of the 14 correlations computed without one sector must be positive.
- **Requests to census.gov:** 6 in all (three discovery requests by hand before the script existed: the data page, the release page and the data file; then the 3 the `fetch` command makes), GET only, one neutral user-agent string, no contact details, 3 seconds apart; no refusal.

## Limits

- **The test cannot identify AI as the cause.** Anything that ranked industries the way AI use does after 2019 (remote work, venture funding, interest-rate exposure, the shift from goods to services, reopening) would give the same result. Subtracting 2017-19 growth removes only reasons that were already there before. SUPPORT is never evidence that AI raised company formation, and AGAINST says only that the predicted pattern is missing.
- **BTOS measures AI use by existing employers, not by new applicants.** Whether the new applicants use AI is not measured by any free series found.
- **Applications are not companies.** An application is a request for an employer identification number, not a firm that exists or hires; applications with planned wages (WBA) are the subset that report planned wages, a closer proxy for employer firms, and are reported as a second labelled pass.
- **14 sectors is a small sample:** a rank correlation across 14 points moves a lot when one sector moves, which is why SUPPORT also requires every leave-one-out correlation to stay positive.
- Sector coverage: the 14 kept sectors have all 46 survey cycles; the dropped ones (including finance, mining, agriculture, utilities and management of companies) are not tested at all.

## Choices where the spec was silent

- **Permutation p-value convention:** (1 + count) / (10,000 + 1), so a p-value is never exactly zero; a shuffle that ties the observed correlation counts as at least as extreme (compared after rounding to 9 decimals).
- **Seed:** 20261115 (the registration date); every test re-seeds from it, so each is reproducible alone.
- **Spearman** is the CV1-P6 function (average ranks for ties), also used for the leave-one-out values. A leave-one-out value that is undefined counts as not positive.
- **National total (P3):** BFS's own TOTAL row (all sectors plus applications with no NAICS code), not the sum of kept sectors, so that it is the published national number. The comparison is of the two means, equivalent to comparing the 11-month sums.
- **Weighted Pearson:** computed on the raw AI percent and the raw growth (not ranks), for both g_post and g_post minus g_pre, business applications; weights are each kept sector's 2019 January-November mean monthly BA. No p-value.
- **No 51 and 54** is computed for business applications and for planned-wage applications, with the same permutation method on the remaining sectors; the label it would carry is stored in detail.csv but is not used.
- **The 2024-25 window** is log(mean 2025) minus log(mean 2024). The spec names only the post window, so the pre-period for its P2 version is shown two ways: Grok's matched one-year 2018-to-2019 growth (the main reported line) and the registered 2017-to-2019 growth (two years, so its duration differs).
- **Data-quality stops:** the build stops if any kept sector has a missing month in January to November of 2017, 2018, 2019, 2023, 2024 or 2025, or a non-positive mean. 2018 and 2024 are read only for the reported 2024-25 window.
- **The sector list** is fixed by BTOS cycle counts and BFS membership alone, before any BFS statistic is computed. Sectors suppressed in most cycles (11, 21, 22, 55) drop on the 46-cycle rule; sector 52 drops by the spec's ruling 7.
- **Pinned BFS file:** the build refuses to score if `bfs_monthly.csv` does not hash to the 12 Nov 2026 file; a later vintage needs a reviewed new pin.
- **Imported CV1 reader:** the CV1-P6 input reader also hash-checks the SIC-NAICS concordance workbook; it is required to load but not used here.
- **The BTOS cycle cutoff (before 17 Nov 2025) and the three cycles missing from the workbook** are inherited unchanged from the CV1-P6 code.

## Files

`registered.csv` (written before any statistic), `scores.csv` (one row per statement), `detail.csv` (every supporting number, including each leave-one-out value and the sector table for both outcomes), `vintages.csv` (what was downloaded, when, and its sha256). Raw downloads stay in `data/vintages/af1` (gitignored). Re-run: `python3 bin/af1_ai_formation.py fetch` then `build`; `selftest` needs no network.

