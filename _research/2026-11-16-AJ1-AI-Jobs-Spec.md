# AJ1: does AI create more jobs than it displaces? Registered blind, 16 November 2026 (version 1)

**Status: registered before any employment or job-openings figure by industry was read by the supervisor or any agent for this
test.** The hash of this file is pinned at landing; a builder must refuse to score if it changes. Amendments after an attack are
allowed while still blind and are recorded as a new version.

**What the supervisor already knows, declared.** From general reporting, not from this data: employment in information and in
computer systems design has been described as soft since 2023, and the February 2026 CES benchmark revised payrolls down for the
year to March 2025. No industry series has been opened. This prior knowledge is why the labels are mechanical and fixed here.

## Why this exists

Thesis T5 in [`dossiers/ai-theses.md`](../dossiers/ai-theses.md): "AI creates more jobs than it displaces". It comes from the
Apollo note the principal cited (E-028), and the principal chose it as the next test (E-030). The free data cannot count jobs
created and destroyed by AI. It can answer a narrower question: **since 2023, have industries that use more AI gained or lost
employment and job openings, compared with other industries and with their own 2017-19 trend?** Displacement predicts that
AI-heavy industries fall behind; creation predicts that they keep up or pull ahead.

## Data (free)

- **AI use**: Census BTOS, `AI Core Questions.xlsx` (sha256 `e058a098…3da3ce`, already held), sheet "Subsector Estimates",
  question 7 ("use AI in producing goods or services"), answer "Yes", mean over the 46 cycles of 2024-2025. A subsector is kept
  only if all 46 cycles are published (no suppressed cycle). Read on 16 Nov 2026 (AI input only, no outcome data): 23 subsectors
  pass, plus a row coded `XXX` (dropped, not an industry): 238, 423, 424, 441, 454, 511, 512, 518, 519, 522, 523, 524, 531, 541,
  561, 611, 621, 624, 711, 713, 722, 811, 812. For sector-level statements the CV1-P6 sector means are used (imported code path,
  as in AF1).
- **Employment**: BLS Current Employment Statistics (CES), all employees, not seasonally adjusted (data type 01), at the
  three-digit NAICS level, through the public BLS API version 1 (no key, no registration, no contact details). On 16 Nov 2026
  `download.bls.gov` refused a script (HTTP 403) and is not used. The vintage is the one current at build; the raw JSON is
  cached, hashed and gitignored.
- **Job openings**: BLS JOLTS, job openings rate, not seasonally adjusted, by JOLTS industry, through the same API.
- If the API refuses (HTTP 403 or 429, or a daily-limit message), the script stops; the decision goes to the principal.

## Matching

CES uses NAICS 2022; BTOS subsectors are NAICS 2017. Rules, fixed now: 454 (nonstore retailers) was abolished in 2022 and is
dropped. 511 is matched to 513 (publishing industries) and 519 to 519; both are flagged, and a robustness run drops them. Any
other subsector that CES does not publish at three digits is dropped and listed. 541 is the whole professional-services sector.
The kept list and its count are written before any statistic.

JOLTS industries are coarser. Each is given the BTOS sector AI mean of the sector it covers; where one JOLTS industry covers two
BTOS sectors (professional and business services = 54 + 55 + 56), the AI means are weighted by each sector's CES employment, mean
of 2019, and 55 is dropped if BTOS does not publish it. Durable and nondurable manufacturing both take sector 31-33's mean. JOLTS
government is dropped (not in BTOS).

## Windows

Annual means of monthly NSA levels (all twelve months). g_post = ln(mean 2025) - ln(mean 2023); g_pre = ln(mean 2019) -
ln(mean 2017). Grok-style alternative reported, not labelled: g_post on 2024 to 2025, and the latest twelve months available
against the same months of 2023.

## Statements

| id | statement | statistic | SUPPORT | AGAINST |
|---|---|---|---|---|
| AJ1-P1 | Employment grew at least as much after 2023 in subsectors that use more AI | Spearman, subsector AI use vs g_post (CES employment) | permutation p ≤ 0.05 (positive) and all leave-one-out rho > 0 | permutation p ≤ 0.05 (negative) |
| AJ1-P2 | ...and against their own 2017-19 growth | Spearman, AI use vs g_post - g_pre | same rule | same rule |
| AJ1-P3 | Job openings held up better since 2019 where AI use is higher | Spearman across JOLTS industries, AI use vs (mean openings rate 2025 - mean 2019), percentage points | same rule | same rule |

Permutation: 10,000 random permutations of the AI ranking, growth held fixed, seed fixed and recorded; one-sided p-values. Between
the SUPPORT and AGAINST rules the label is INCONCLUSIVE.

**Asymmetry, stated with every result.** AGAINST says AI-heavy industries fell behind: the pattern displacement predicts, not
proof that AI caused it (rates, the end of the post-pandemic hiring boom and software-sector cycles rank industries similarly).
SUPPORT says the displacement pattern is absent in this data. **Neither label measures the economy-wide net**: jobs AI creates in
other industries (data-centre construction, power, chips) and displaced workers hired elsewhere are outside an industry
cross-section. BTOS measures AI use by existing employers.

**Reported, not labelled:** P1 and P2 without 511, 519 and 541 (the subsectors where AI suppliers themselves sit), and without 511
and 519 (the matching flags); leave-one-out range of each rho; a Pearson correlation weighted by 2019 employment; the alternative
windows; national CES private employment growth 2023-25 against 2017-19 (not about AI).

**Not tested here, and why.** Occupation-level exposure (OEWS by occupation against a published AI-exposure score) needs an
exposure index whose free availability is not yet checked; it is a candidate AJ2. Young graduates' unemployment needs CPS
microdata. BTOS's own questions on AI's effect on a firm's headcount are not in the file held.

## Build

`bin/aj1_ai_jobs.py` with `selftest`, `fetch` and `build`; outputs in `data/aj1_ai_jobs/` (`registered.csv` written before any
statistic, `scores.csv`, `detail.csv`, README). The BTOS sector means come from the CV1-P6 code path (imported). A gate is
registered in `bin/check.sh` at landing. Every statistic carries its denominator (subsectors kept and dropped, months used).

## Version 2 — amended after the attack, still blind (16 November 2026)

Grok (Cursor, read and web, blind rule) attacked version 1, fetched only documentation and reported no employment or openings
figure; its return is filed as `_research/2026-11-16-AJ1-Grok-Attack.md`. The supervisor re-read, in the desktop browser (scripts
get HTTP 403 from www.bls.gov), its quotes on the CES NAICS 2022 page (the 513 and 454 sentences, the sector-54 and sector-61 series
IDs, the history rebuilt on NAICS 2022) and on the CES published-series page (722, 811, 812 published from 1990; the 523 series
titled "Securities, commodity contracts, funds, trusts, and other financial vehicles"). Note: Grok read `download.bls.gov` from
Cursor's servers, so that host's 403 is a refusal of this machine's requests, not an outage; it is still not used.
**This section replaces the Matching, Windows and Statements sections of version 1. Where the two disagree, this section governs.**

**Rulings.**
1. *F1, "fatal": a 2023-25 shock that ranks industries like AI use is labelled as AI.* Accepted as the binding limit, not fatal (as
   in AF1). Labels name the pattern, never the cause. Partialling out a hand-picked "rate-sensitive" list (Grok's amendment 12) is
   **overruled**: the list would be the supervisor's choice and would decide the result; it is not added.
2. *F2: asymmetric rules.* Accepted. Both sides need one-sided permutation p ≤ 0.05 **and** every leave-one-out rho of that sign.
   P1 now reads "grew more".
3. *F3: the openings rate has employment in its denominator, and 2019-25 includes the pandemic.* Accepted. P3 uses the log of the
   openings **level** (series ending `JOL`), on the same windows as employment.
4. *F4, F14: JOLTS nesting.* Accepted: the 15 non-overlapping private child industries listed in the attack, parents and government
   dropped. Professional and business services (54 + 55 + 56) is **kept** (it is where AI use is highest): its AI value is the 2019
   CES-employment-weighted mean of 54 and 56, and the share of 55 in that industry's 2019 employment is printed; P3 is also reported
   without it. Transportation, warehousing and utilities takes sector 48-49's mean (utilities, 22, has no BTOS mean; its 2019 share
   is printed). Durable and nondurable manufacturing share one value; ties take average ranks.
5. *F5, F6, F15: NAICS 2022 matching.* CES rebuilt its history on NAICS 2022, so each CES series is consistent over time; the
   mismatch is only between the BTOS 2017 subsector and the CES 2022 series. **Labelled sample: drop 511→513 and 519** (their
   scope changed materially) and 454. 441 and 518 (minor changes) stay, flagged. 541 is sector 54 exactly (CEU6054000001) and stays.
   Reported: without 441 and 518; without 518 and 541 (the AI suppliers).
6. *F7: CES 523 includes NAICS 525, which BTOS excludes.* Accepted: 523 dropped (the AF1 rule for sector 52).
7. *F9, F10: which BTOS series.* Overruled in part, as in AF1: the file held is "AI Core Questions (Original)", whose codes (454,
   511) are NAICS 2017; its last cycle is 202520, so no new-wording cycle is in it.
8. *F12: AI use measured inside the outcome window.* Noted, not adopted for the label: the 2024-25 mean is kept for comparability
   with AF1 and CV1-P6. Reported: the same tests on the mean of the 2023 cycles (202319-202326) for subsectors with all 8 published.
   The asymmetry statement adds that fast-growing industries may adopt AI because they are growing.
9. *F13: the 2019-23 change sits in neither window.* Reported, not labelled: ln(mean 2023) - ln(mean 2019) beside each result.
10. *F11, amendment 15.* Accepted into the asymmetry statement: a rank association among firm-weighted AI rates in a
    suppression-selected set of industries.
11. *F16-F18: fetch and permutation details.* Accepted: POST bodies of at most 25 series, startyear 2017, endyear 2026, period M13
    dropped, stop on "series does not exist" or any non-success status; the raw JSON is hashed and not refetched; the CES and JOLTS
    release dates are recorded from the response's own messages or footnotes, or "not stated". Seed 20261116; 100,000 permutations
    of the AI values; p = (1 + k) / 100,001; a p within two Monte Carlo standard errors of 0.05 is labelled INCONCLUSIVE. Three
    statements, no multiplicity adjustment; this is said in the README.

**Series (version 2).** CES all employees, NSA: 238 CEU2023800001; 423 CEU4142300001; 424 CEU4142400001; 441 CEU4244100001;
512 CEU5051200001; 518 CEU5051800001; 522 CEU5552200001; 524 CEU5552400001; 531 CEU5553100001; 541 CEU6054000001;
561 CEU6056100001; 611 CEU6561000001; 621 CEU6562100001; 624 CEU6562400001; 711 CEU7071100001; 713 CEU7071300001;
722 CEU7072200001; 811 CEU8081100001; 812 CEU8081200001 (19 labelled subsectors). Reported only: 513 CEU5051300001,
519 CEU5051900001, 523 CEU5552300001. Weights and national: CEU0500000001 (total private), CEU6055000001 (55),
CEU6056000001 (56). JOLTS openings level, NSA, the 15 child industries: JTU{code}000000000JOL for codes 230000, 320000, 340000,
420000, 440000, 480099, 510000, 520000, 530000, 540099, 610000, 620000, 710000, 720000, 810000, with each industry's AI value
from its BTOS sector (31-33, 42, 44-45, 48-49, 51, 52, 53, 54+56, 61, 62, 71, 72, 81, 23). Sector 52 (finance and insurance)
takes the CV1-P6 sector-52 mean, flagged because BTOS excludes 525; P3 is also reported without it.

**Windows (version 2).** Annual means of the twelve monthly NSA values. g_post = ln(mean 2025) - ln(mean 2023); g_pre = ln(mean
2019) - ln(mean 2017). Reported: 2024-25; the latest twelve months available against the same months of 2023; 2019-23.

**Statements (version 2).**

| id | statement | statistic | SUPPORT | AGAINST |
|---|---|---|---|---|
| AJ1-P1 | Employment grew more after 2023 in subsectors that use more AI | Spearman, AI use vs g_post (CES), 19 subsectors | permutation p ≤ 0.05 (positive) and all leave-one-out rho > 0 | permutation p ≤ 0.05 (negative) and all leave-one-out rho < 0 |
| AJ1-P2 | ...relative to their own 2017-19 growth | Spearman, AI use vs g_post - g_pre | same rule | same rule |
| AJ1-P3 | Job openings fell less after 2023 where AI use is higher | Spearman across the 15 JOLTS industries, AI use vs ln(mean openings 2025) - ln(mean 2023) | same rule | same rule |

Otherwise INCONCLUSIVE. SUPPORT means the displacement pattern is absent and the industries that use more AI kept up or pulled
ahead; AGAINST means they fell behind. Neither identifies AI as the cause or measures the economy-wide net.
