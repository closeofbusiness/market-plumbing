# AF1: is AI raising company formation? Registered blind, 15 November 2026 (version 1)

**Status: registered before any sector-level business-application figure was read.** The national weekly series has been seen
(as a published chart, below); nothing broken down by industry has. The hash of this file is pinned at landing; a builder must
refuse to score if it changes. Amendments after an attack are allowed while still blind and are recorded as a new version.

## Why this exists

The principal added AI adoption and "the thesis that AI is raising business investment and the formation of new companies" to
the mission on 15 Nov 2026 (THE_ASK E-028), citing a published note (Apollo, "The AI Entrepreneurship Boom", Daily Spark,
15 Nov 2026). The note shows three charts, read by the supervisor and independently by Gemini 4 Hydrogen:

1. US business applications, weekly, seasonally adjusted, 4-week average, 2005 to 2026, rising to about 120,000-130,000 in 2026,
   with an arrow labelled "AI". No series in the chart measures AI.
2. The share of adults starting or managing a business up to 42 months old, by age group, 2015 against 2025 (for example 10% to
   24% at ages 18-24). No source line is printed on the image; the 42-month definition is the Global Entrepreneurship Monitor's
   (inference, unverified).
3. Revenue and employment expectations (diffusion indexes) of AI adopters against non-adopters (48 against 21, and 33 against
   15); the note's text sources it to the Federal Reserve Bank of New York. It compares firms at one time and does not separate
   firms that adopt AI because they are already growing.

None of the three shows that AI caused the rise. The rise in applications began in mid-2020, two years before generative AI
was widely available. AF1 asks the one question the free data can answer: **did industries that use more AI see more new
companies, compared with what those same industries did before AI?** It is a comparison across industries, so it is
descriptive evidence, not proof of cause. A rise in applications that is the same everywhere is not evidence for the thesis.

## Data (free, Census Bureau)

- **Business Formation Statistics (BFS)**, monthly, seasonally adjusted, by two-digit NAICS sector: business applications (BA)
  and high-propensity business applications (HBA, the applications Census judges likely to become employers). The vintage
  current at build is used and recorded with its release date and the file's sha256.
- **BTOS AI use by sector**: the CV1-P6 input (`AI Core Questions.xlsx`, sha256 `e058a098…3da3ce`), question 7 ("use AI in
  producing goods or services", "Yes"), mean over the unsuppressed cycles of 2024-2025, exactly as CV1-P6 computes it.
- If a Census host refuses a script (HTTP 403 or 429), the script stops; the files are then downloaded through the desktop
  browser with the principal's approval (as for CV1-P6) and hash-pinned. No contact address in any request.

## Sectors

The BTOS sectors (two-digit NAICS, with 31-33, 44-45 and 48-49 each grouped as one) that also appear in BFS. Sectors whose
BTOS AI mean uses fewer than 20 of the 46 cycles (heavy suppression) are dropped and listed. Sector 55 (management of
companies) is dropped if BFS does not publish it. The kept sectors are listed with their counts before any statistic.

## Statements

| id | statement | statistic | SUPPORT | AGAINST |
|---|---|---|---|---|
| AF1-P1 | Applications rose more in sectors that use more AI | Spearman rank correlation across the kept sectors between AI use and the growth of HBA: log(mean monthly HBA in 2025) minus log(mean monthly HBA in 2022) | rho ≥ +0.40 | rho ≤ 0 |
| AF1-P2 | ...and by more than the same sectors did before AI | rho(P1) minus rho of AI use against HBA growth from 2016 to 2019 (same formula, years 2016 and 2019) | difference ≥ +0.30 and rho(P1) ≥ +0.40 | difference ≤ 0 |
| AF1-P3 | The national rise is not just the post-2020 level shift | National HBA, mean monthly 2025 over mean monthly 2022, against mean monthly 2022 over mean monthly 2021 | 2022-25 growth, annualised, ≥ 2021-22 growth + 2 pp | 2022-25 annualised growth ≤ 0 |

Between the SUPPORT and AGAINST thresholds the label is INCONCLUSIVE.

**Asymmetry.** AGAINST on P1 or P2 refutes the industry pattern the thesis predicts, on this data. SUPPORT says only that the
pattern is consistent with the thesis: industries that use more AI (information, professional services, finance) may also
attract more new firms for other reasons, and P2's comparison with 2016-2019 removes only reasons that were already there
before. P3 is a national time series and cannot identify AI at all; it records whether there is anything left to explain
after the 2020 jump.

**Robustness, reported, not used for labels:** P1 and P2 recomputed on all business applications (BA) instead of HBA; leave-
one-sector-out range of rho(P1); P1 without sectors 51 and 54 (the two largest AI users, where AI firms themselves are formed).

**Not tested here, and why.** Chart 2's adult entrepreneurship shares need survey microdata this project has not located for
free. Chart 3 is a single cross-section of expectations; the New York Fed survey behind it is not tested. Whether new
companies *use* AI is not measured by any free series found so far (BTOS asks existing firms).

## Build

`bin/af1_ai_formation.py` with `selftest`, `fetch` (or a documented local-file path when a host refuses scripts) and `build`;
outputs in `data/af1_ai_formation/` (`registered.csv` written before any statistic, `scores.csv`, `detail.csv`, README). The
BTOS sector means come from the same code path as CV1-P6 (imported, not copied). A gate is registered in `bin/check.sh` at
landing. Every statistic carries its denominator (sectors kept and dropped, months used).
