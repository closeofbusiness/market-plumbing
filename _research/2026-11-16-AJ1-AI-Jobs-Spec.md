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
