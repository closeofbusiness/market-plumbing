# AP1: is AI raising productivity and profit margins where it is used? Registered blind, 16 November 2026 (version 1)

**Status: registered before any value added, employment or operating-surplus figure by industry was read by the supervisor or any
agent for this test.** The supervisor has opened the two BEA files only to list sheet titles, row labels, series codes and the
first and last period of each series. The hash of this file is pinned at landing; a builder must refuse to score if it changes.
Amendments after an attack are allowed while still blind and are recorded as a new version.

**What the supervisor already knows, declared.** From general reporting, not from this data: US labour productivity growth was
described as strong in 2023-25, and large technology firms reported rising margins. No industry series in either file has been
opened. This prior knowledge is why the labels are mechanical and fixed here.

## Why this exists

Thesis T4 in [`dossiers/ai-theses.md`](../dossiers/ai-theses.md): "AI is raising productivity and profit margins in the industries
that use it" (proposed E-029, confirmed E-030; the principal chose it as the next test on 16 Nov 2026). The free data cannot show
that AI caused a change. It can answer a narrower question: **since 2023, have industries that use more AI seen faster growth in
output per worker and a larger rise in the operating-surplus share of their value added, compared with other industries and with
their own 2017-19 change?** The thesis predicts yes on both.

## Data (free, no key, no registration, no contact details)

- **AI use**: Census BTOS, `AI Core Questions.xlsx` (sha256 `e058a098…3da3ce`, already held), question 7 ("use AI in producing goods
  or services"), answer "Yes", mean over the 46 cycles of 2024-2025, a subsector or sector kept only if all 46 cycles are published.
  Subsector and sector means come from the AJ1 code path (`bin/aj1_ai_jobs.py`, `load_btos_inputs`, imported, not copied).
- **Real value added and its components by industry**: BEA GDP by Industry, `https://apps.bea.gov/industry/Release/XLS/GDPxInd/ValueAdded.xlsx`
  (served to a script on 16 Nov 2026, HTTP 200). Sheet `TVA106-A` (real value added, millions of 2017 chained dollars, annual
  1997-2025), `TVA105-A` (value added, millions of current dollars), `TVA113-A` (compensation of employees; taxes on production
  and imports less subsidies; gross operating surplus; millions of current dollars, annual 1997-2025).
- **Full-time-equivalent employees by industry**: BEA NIPA Table 6.5D, from the flat file
  `https://apps.bea.gov/national/Release/TXT/NipaDataA.txt` with `SeriesRegister.txt` (both HTTP 200 on 16 Nov 2026; annual
  1998-2025). BEA uses the same industry definitions in both files and codes industries on NAICS 2017, as BTOS does.
- Both files are cached, hashed and gitignored (`data/vintages/ap1/raw/`); the release date is taken from each file's own text, or
  "not stated". On HTTP 403 or 429, or a body that is not the expected file, the script stops; the decision goes to the principal.

## Industries

Each BEA row is matched to one AI value. Rows that correspond to a single published BTOS subsector take its mean; rows for which BEA
publishes nothing finer than the sector take the BTOS sector mean. No BEA row overlaps another.

| BEA row (TVA106-A label) | FTE series (Table 6.5D) | AI value | flag |
|---|---|---|---|
| Motor vehicle and parts dealers | N4339C | subsector 441 | |
| Publishing industries, except internet (includes software) | N4353C | 511 | AI supplier |
| Motion picture and sound recording industries | N4354C | 512 | |
| Data processing, internet publishing, and other information services | N4356C | simple mean of 518 and 519 | two subsectors; AI supplier |
| Federal Reserve banks, credit intermediation, and related activities | N4358C | 522 | includes 521 (the Fed) |
| Securities, commodity contracts, and investments | N4359C | 523 | finance |
| Insurance carriers and related activities | N4360C | 524 | finance |
| Professional, scientific, and technical services | N4365C | 541 | AI supplier (includes computer systems design) |
| Administrative and support services | N4371C | 561 | |
| Educational services | N4373C | 611 | |
| Ambulatory health care services | N4375C | 621 | |
| Social assistance | N4392C | 624 | |
| Performing arts, spectator sports, museums, and related activities | N4394C | 711 | includes 712 |
| Amusements, gambling, and recreation industries | N4395C | 713 | |
| Food services and drinking places | N4398C | 722 | |
| Construction | N4312C | sector 23 | sector-level AI |
| Manufacturing | N4313C | sector 31-33 | sector-level AI |
| Wholesale trade | N4335C | sector 42 | sector-level AI |
| Transportation and warehousing | N4343C | sector 48-49 | sector-level AI |
| Other services, except government | N4399C | sector 81 | sector-level AI |

20 industries. Not tested, and why: real estate (BEA's real estate includes the imputed rent of owner-occupied housing, which no
firm produces, and Table 6.5D has no housing split); the other retail rows, accommodation, hospitals, nursing care, broadcasting and
telecommunications, rental and leasing, management of companies, waste management, mining, utilities and agriculture (no BTOS
subsector or sector mean with all 46 cycles that matches the row); government. If any listed AI value fails the 46-cycle rule, the
row is dropped and listed before any statistic.

## Measures

- **Productivity**: real value added per full-time-equivalent employee, `q = TVA106-A / FTE`. g_post = ln q(2025) - ln q(2023);
  g_pre = ln q(2019) - ln q(2017).
- **Margin**: gross operating surplus as a share of value added, `s = GOS / VA` (both current dollars, TVA113-A and TVA105-A).
  d_post = s(2025) - s(2023); d_pre = s(2019) - s(2017), in percentage points.

## Statements

| id | statement | statistic | SUPPORT | AGAINST |
|---|---|---|---|---|
| AP1-P1 | Output per worker grew more after 2023 in industries that use more AI | Spearman, AI use vs g_post, 20 industries | one-sided permutation p ≤ 0.05 (positive) and every leave-one-out rho > 0 | one-sided permutation p ≤ 0.05 (negative) and every leave-one-out rho < 0 |
| AP1-P2 | ...relative to their own 2017-19 growth | Spearman, AI use vs g_post - g_pre | same rule | same rule |
| AP1-P3 | The operating-surplus share rose more after 2023 where AI use is higher | Spearman, AI use vs d_post | same rule | same rule |
| AP1-P4 | ...relative to its own 2017-19 change | Spearman, AI use vs d_post - d_pre | same rule | same rule |

Otherwise INCONCLUSIVE. Permutation: seed 20261116, 100,000 permutations of the AI values with the outcome held fixed, p = (1 + k) /
100,001, ties take average ranks; a p within two Monte Carlo standard errors of 0.05 is INCONCLUSIVE. Four statements, no
multiplicity adjustment; this is said in the README.

**Asymmetry, stated with every result.** SUPPORT says the pattern T4 predicts is present: industries that use more AI gained more in
output per worker or in margin. It does not show that AI caused it: industries that use more AI (information, professional services,
finance) may also have gained from rates, prices or the post-pandemic recovery, and fast-growing firms may adopt AI because they are
growing. AGAINST says the pattern is absent or reversed on this data. Gross operating surplus is not profit: it includes depreciation
(so heavier software and data-centre investment raises it), proprietors' income and net interest. Real value added in finance and
education is partly measured from inputs, which weakens productivity there. FTE counts employees, not the self-employed. BTOS
measures AI use by existing employers, firm-weighted.

**Reported, not labelled:** leave-one-out range of each rho; a Pearson correlation weighted by each industry's 2019 nominal value
added; the 15 subsector-matched rows only; without the AI-supplier rows (511, 518-519, 541); without finance (522, 523, 524); the
2024-25 window; the 2019-23 change beside each result; the same tests on the mean of the 2023 cycles (202319-202326) where all 8
are published; national private-industry real value added per FTE, 2023-25 against 2017-19 (not about AI).

**Not tested here, and why.** BLS labour productivity by detailed industry (download.bls.gov refuses this machine; a candidate if the
API serves it). Corporate profits by industry (NIPA Table 6.16D) are published only for broad groups. Firm-level margins of AI
adopters need company data (T6's benchmark).

## Build

`bin/ap1_ai_productivity.py` with `selftest`, `fetch` and `build`; outputs in `data/ap1_ai_productivity/` (`registered.csv` written
before any statistic, `scores.csv`, `detail.csv`, README). Rows are found by exact label and FTE series code; a missing row, a
duplicate label, a non-positive value or a missing year (2017, 2019, 2023, 2024, 2025) stops the build. A gate is registered in
`bin/check.sh` at landing. Every statistic carries its denominator (industries kept and dropped, years used).
