# CV1: did AI-driven managerial confidence move firms outside the AI complex to commit idle cash to capex? Registered statements P1 to P6 (build of 13 Nov 2026)

This folder holds the one-time scoring of statements CV1-P1 to CV1-P6 of the registration `_research/2026-11-13-CV1-Confidence-Velocity-Spec.md` (version 2, registered blind on 13 Nov 2026; sha256 `26672bd1f1632ddab839780b219724773cab83f63dae082c87e838cc1a7a6104`). `registered.csv` was written by the build before any statistic was computed, from that file; the build refuses to score if the file's hash differs from the one pinned in `bin/cv1_confidence_velocity.py`. P7 is not scored (its inputs do not exist yet). The numbers are derived from public US government data (BEA, Federal Reserve Board, Census Bureau, SEC); the raw files are not redistributed and sit in a gitignored cache.

What a label means. The labels are asymmetric by registration. AGAINST on P1 to P3 refutes the stage-4 leg (committed capital outside the AI complex accelerated; liquidity was drawn down) on this free data. SUPPORT says only that the numbers are consistent with that leg. It is never evidence that AI lowered managers' uncertainty, because no statistic here identifies a fall in uncertainty. INCONCLUSIVE means neither condition was met. The treatment window (2022 to 2025) also contains the CHIPS 25% credit, the clean-energy credits, restored 100% bonus depreciation, power and factory construction and acquisition arithmetic; none is separated out.

Capex in P2 to P5 is worldwide consolidated capex of US-GAAP USD filers; GDP is domestic. This is a known limit and applies to every number below.

## Result

| statement | label | statistic | value | denominators |
|---|---|---|---|---|
| CV1-P1 | AGAINST | nominal_gap_variant_A | -0.0503 pp per year | national accounts, no firm counts; nominal residual share of GDP Q4 2025 = 8.00%, Q4 2022 = 8.08%, Q4 2019 = 8.27%, Q4 2015 = 8.18% |
| CV1-P2 | AGAINST | median_gap | -7.2735 pp per year | firms T=788 P=716; share of 2025 ex-AI capex covered T=0.4105 P=0.3805; share of headline-class capex T=0.6511 P=0.6035 |
| CV1-P3 | AGAINST | difference_in_change | 0.7870 pp (Q4-to-Q4 change, treatment minus placebo, not annualised) | four Z.1 series, one sector (nonfinancial corporate business), 2 windows of Q4 values; GDP = Table 1.1.5 Q4 SAAR |
| CV1-P4 | AGAINST | difference_in_top_minus_bottom | -10.0617 pp per year | firms with cash and assets T=768 P=637 (of 788 and 716 in the P2 sets); 2-digit SIC groups used T=49 P=45; firms in groups of fewer than 3 dropped T=9 P=16; share of 2025 ex-AI capex covered T=0.4038 P=0.3629 |
| CV1-P5 | AGAINST | trimmed_gap | -5.2533 pp per year | firms T: high untrimmed=566 trimmed=537 (removed 29) low=200; P: high untrimmed=517 trimmed=491 (removed 26) low=182; high+low firms outside the two bins (SIC 1500-1799 and 4900+, 6000+, 9000+) are not used |
| CV1-P6 | NOT BUILT | - | -  | none |
| CV1-P7 | NOT SCORED | - | -  | none |

Full statistics for each statement are in `scores.csv` (one row per statement); every supporting number is a row of `detail.csv`.

## What each statement computes, exactly

### P1: business investment outside the AI build-out and the subsidised factory and power build, share of GDP

Source: BEA NIPA Tables 5.3.5 (nominal) and 5.3.6 (chained 2017 dollars) from `Section5All_xls.xlsx` (published October 29, 2026), and Tables 1.1.5 and 1.1.6 from `Section1All_xls.xlsx` (published October 29, 2026). Quarterly, seasonally adjusted annual rates. Residual = nonresidential fixed investment (A008RC) less the subtracted lines; share = residual over GDP (A191RC), in percent. Annualised pp change = (share at the end quarter minus share at the start quarter) divided by the years (3 for 2022Q4 to 2025Q4, 4 for 2015Q4 to 2019Q4). Statistic = treatment change minus placebo change. The real version is the same arithmetic on chained dollars (A008RX less the same lines over A191RX); chained dollars are not additive, so it is approximate. SUPPORT if both gaps are at least +0.15 pp per year, AGAINST if both are at most 0, otherwise INCONCLUSIVE.

The registration names communication equipment as a subtraction. In this vintage the quarterly Tables 5.3.5 and 5.3.6 no longer show it as a line: it sits inside `Other` information processing equipment together with medical equipment and instruments, nonmedical instruments, photocopy and office equipment. Three variants were computed and all three are in `scores.csv`:

- Variant A (the primary, which sets the label): subtract the whole Information processing equipment line (Y034) with software (B985), manufacturing structures (C307), power and communication structures (W003) and mining exploration, shafts and wells (E318). It removes communication equipment as registered, and also medical equipment and instruments and the other small lines.
- Variant B: subtract computers and peripheral equipment (B935) only, with the same four other lines. Communication equipment stays in the residual.
- Variant C: the exact registered list (B935, communication equipment C275 from Tables 5.5.5 and 5.5.6, B985, C307, W003, E318) on annual data (Tables 5.3.5-A, 5.3.6-A, 5.5.5-A, 5.5.6-A, 1.1.5-A, 1.1.6-A, calendar years 2022 to 2025 and 2015 to 2019), because Tables 5.5.5 and 5.5.6 are annual only.

| variant | nominal gap | real gap | label if it were primary |
|---|---|---|---|
| A | -0.0503 | -0.0785 | AGAINST |
| B | 0.0009 | -0.0964 | INCONCLUSIVE |
| C | -0.0042 | -0.0330 | AGAINST |

Gaps are in pp per year. Census C30 private "Data center" construction (monthly, millions of dollars at a seasonally adjusted annual rate, `privsatime.xlsx`) is a memo only: December of 2015, 2019, 2022 and 2025 are in `detail.csv` with a blank kept as blank; it is not subtracted. Denominator: national accounts, no firm counts.

### P2: listed firms outside the AI complex accelerated capex

Panel: SEC frames `CY2016`, `CY2019`, `CY2022`, `CY2025` of `us-gaap` `PaymentsToAcquirePropertyPlantAndEquipment` in USD. A firm is common if in each of the four frames its fact is positive, its fact's period ends in November, December or January, and the fact's accession number resolves to a 10-K or 10-K/A in the SEC submissions data (main file plus the older pages it lists). The 7 named CIKs (Amazon, Alphabet, Meta, Microsoft, Oracle, Nvidia, Tesla) are removed first; then SIC (from the submissions file, fetched 2026-11-13) sorts firms: AI complex SICs 3559, 3570-3579, 3661, 3663, 3669, 3670-3679, 4812, 4813, 7370-7379 out; finance SIC 6000-6799 out (this includes REITs, SIC 6798); utilities SIC 4900-4991 reported as a separate stratum; firms with no SIC out. A firm is dropped from a window if PPE (`PropertyPlantAndEquipmentNet`) rose more than 25% in any year of that window with `PaymentsToAcquireBusinessesNetOfCashAcquired` above zero in that year. Firm growth = (capex at the end year over capex at the base year) to the power 1/3, minus 1. Statistic: the median of firm growth minus nominal GDP growth over the same years (Table 1.1.5 annual, calendar years: 2022 to 2025 and 2016 to 2019, 3 years each), treatment minus placebo, in pp per year; and the same difference for the capex-weighted mean of firm growth (weights = base-year capex). The aggregate growth of summed capex is also reported. SUPPORT if the median gap is at least +2 and the weighted gap is above 0; AGAINST if both are at most 0; otherwise INCONCLUSIVE.

Denominators (firms): frame facts in CY2016, CY2019, CY2022, CY2025 = 2016: 4324, 2019: 4347, 2022: 4415, 2025: 3578; candidates present in all four years with positive capex and a November, December or January period end (7 named CIKs out) = 1464; dropped because a fact was not from a 10-K or 10-K/A = 107 (accession not found in any submissions page = 0); common firms with 10-K facts = 1357, of which AI complex SIC 162, finance (excluding REITs) 292, REITs 8, utilities 57, headline class 838. Headline windows: treatment 788 firms (dropped by the acquisition rule 50), placebo 716 firms (dropped 122). Share of 2025 ex-AI capex covered by the headline panel: 0.4105 (treatment set) and 0.3805 (placebo set), where ex-AI capex is the sum of positive CY2025 frame facts of all firms outside the AI complex with a SIC, any form and any year-end; against the headline-class capex alone (also excluding finance, utilities and REITs) the shares are 0.6511 and 0.6035.

Separate strata, not in the headline (same computation, utilities with 56 and 56 firms in the treatment and placebo windows, REITs with 8 and 8): utilities median gap 3.5472 and weighted gap 7.3383; REITs median gap -16.2881 and weighted gap -8.2784 (pp per year).

### P3: corporate liquidity was drawn down

Source: Fed Z.1 `FRB_Z1_csv.zip` (the release of 11 Sep 2026; its last quarter in these series is 2026Q2). Series, with the description in the file (each confirmed against the spec's meaning before scoring; a mismatch stops the build): FL103069100 = "Nonfinancial corporate business; commercial paper; asset"; FL103061703 = "Nonfinancial corporate business; agency- and GSE-backed securities; asset"; FL103061103 = "Nonfinancial corporate business; Treasury securities; asset"; FL104001105 = "Nonfinancial corporate business; liquid assets (core measure) (FSIs)". Sum of the four, millions of dollars, not seasonally adjusted, Q4 values; divided by Table 1.1.5 nominal GDP (Q4, seasonally adjusted annual rate), in percent. Statistic = (ratio at 2025Q4 minus ratio at 2022Q4) minus (ratio at 2019Q4 minus ratio at 2015Q4), in pp; the changes are not annualised. SUPPORT if the difference is at most -0.5 pp and the nominal dollar stock fell from 2022Q4 to 2025Q4; AGAINST if the difference is at least 0 or the stock rose by more than nominal GDP over the same quarters; otherwise INCONCLUSIVE. Denominator: one sector, four series, four Q4 dates.

Required statements for this readout: the sector is domestic nonfinancial corporate business; it includes equity REITs (moved into the sector on 7 Dec 2023, as the attack note quotes the Fed's table description; not re-read here) and the nonfinancial AI filers; it excludes financial holding companies and the foreign subsidiaries of US corporations; time and savings deposits within the core liquid assets series are a remainder. The SOI benchmark year is not named in the Z.1 file or in the series page for FL103020000 (the page says only that after the most recent SOI year the benchmark ratio is fixed); it is recorded as not determined, and the spec's ruling is that this does not make P3 unscorable. The quarterly movement in these stocks rests on the Census QFR, which this build does not read.

### P4: cash-rich firms led the ex-AI capex change

Panel: the P2 headline window sets. Cash = `CashAndCashEquivalentsAtCarryingValue` (else `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents`, never both) over `Assets`, from instant frames `CY2015Q4I` (placebo) and `CY2021Q4I` (treatment), each fact a 10-K or 10-K/A fact. Within each window the firms are sorted by cash over assets inside their 2-digit SIC; the i-th of n firms (i from 0) goes to tercile min(2, floor(3i/n)), bottom = 0, top = 2; a 2-digit group of fewer than 3 firms cannot be split and is dropped. Tercile growth = the mean of firm annualised capex growth weighted by base-year capex, pooled across 2-digit groups. Statistic = (top minus bottom) in the treatment window minus (top minus bottom) in the placebo window, pp per year. SUPPORT if at least +3 and the top tercile's own treatment growth net of annualised nominal GDP growth is above 0; AGAINST if at most 0; otherwise INCONCLUSIVE.

Denominators (firms): treatment window 768 firms with cash and assets of 788 in the P2 set (top 237, middle 254, bottom 268; 2-digit groups used 49; 9 firms in groups below 3); placebo window 637 of 716 (top 193, middle 208, bottom 220; groups 45; 16 dropped). Share of 2025 ex-AI capex covered: 0.4038 (treatment) and 0.3629 (placebo).

### P5: manufacturing, mining and non-utility transport capex growth exceeded trade and services (not an irreversibility test)

Panel: the P2 headline window sets. High = SIC 1000-1499, 2000-3999, 4000-4899; low = SIC 5000-5999, 7000-8999 (SIC 7370-7379 is already out as AI complex). Trimmed high removes SIC 1311, 1381, 1382, 1389, 2911, 3711 and 3721 (3559, 4812 and 4813 are already out); the removed firms are reported separately. Statistic = (median growth of high minus median growth of low) in the treatment window minus the same in the placebo window, pp per year, for the trimmed and the untrimmed high group. SUPPORT if the trimmed gap is at least +2 (if only the untrimmed gap clears +2: INCONCLUSIVE); AGAINST if the trimmed gap is at most 0; otherwise INCONCLUSIVE.

Denominators (firms): treatment high 566 (trimmed 537, removed 29), low 200; placebo high 517 (trimmed 491, removed 26), low 182. Firms with SIC 1500-1799, 4900 and above 5999 (other than the low bin) or 9000 and above are in neither bin.

### P6: sector AI use against sector capex change (descriptive, no label)

NOT BUILT. The one request for the Census BTOS downloads index (https://www.census.gov/hfp/btos/downloads/, sent with the neutral User-Agent, after a first request without the trailing slash answered 301) came back HTTP 403. The rule was applied: the STOP latch `STOP_www_census_gov` is in the cache, no further request went to www.census.gov, and nothing was fetched from any other host in its place. Without the AI Core Questions (Original) table and the 1987-SIC-to-2002-NAICS concordance (also on www.census.gov), no sector AI-use share and no SIC-to-NAICS map exist, so the Spearman and the leave-one-sector-out range were not computed. The Spearman function exists and is exercised on synthetic data in the selftest. The C30 workbook had been fetched from the same host before the block.

### P7: not scored

The inputs are not available: P7 needs `GoodwillImpairmentLoss` facts for CY2026, CY2027 and CY2028 10-Ks (the last are filed from about February 2029) and the acquisition-spend and goodwill facts for CY2024 and CY2025 and for the baseline cohorts 2012 to 2015. The spec dates its first scoring to about April 2029. No P7 number is computed or implied.

## Implementation choices (where the spec is silent or cannot be followed as written)

1. Raw cache. `data/vintages/cv1/` is not covered by `.gitignore`, and the build task could not edit it, so raw downloads sit in `data/vintages/cv1/raw/`, a folder `.gitignore` already ignores whole. Move them if `data/vintages/cv1/` is later added to `.gitignore`.
2. P1 communication equipment: see the three variants above; variant A sets the label. The label is the same under all three variants: NO, it is variant-dependent (A AGAINST, B INCONCLUSIVE, C AGAINST).
3. P2 capex tag: `PaymentsToAcquirePropertyPlantAndEquipment` (the tag the attack's amendment names). Facts must be positive. Fiscal year-end is taken from the month of each fact's period end (November, December or January), not from the current `fiscalYearEnd` of the submissions file.
4. Form join: a frame fact is matched to its form through its accession number in the submissions data: the `recent` block and every older page listed in the file's `files` array that could hold the accession number (chosen by the filing year inside the number; 319 older pages were fetched). Facts from any other form are dropped and counted.
5. The same 10-K filter is applied to the PPE, acquisition, cash and assets facts that P2 and P4 use. A missing or non-10-K fact never triggers the acquisition drop; a year with an acquisition above zero and no usable PPE pair is counted as untestable (treatment headline: 252 firm-years, placebo: 51).
6. The acquisition rule is applied year by year inside each window (PPE of year y against year y-1 for each year after the base year), using frames for every year in the two windows. The base year of a window is not itself tested.
7. SIC is the current SIC in the submissions file at the fetch date, not the SIC on the filing (the spec accepts this limit). A firm with no SIC is out of the headline and out of the coverage denominators.
8. Capex-weighted growth is the mean of firm annualised growth weighted by base-year capex (the same weighting P4 uses); the growth of summed capex is reported beside it as the aggregate.
9. GDP growth for P2 and P4 uses annual nominal GDP (Table 1.1.5 annual, calendar years) over 2022 to 2025 and 2016 to 2019. P1 and P3 use Q4 quarterly values; their placebo spans 4 years, the panel placebo 3.
10. Ties and groups in P4: firms sorted by cash ratio then CIK; groups below 3 firms dropped; terciles formed separately in each window, so the same firm can sit in different terciles in the two windows.
11. P5: when the untrimmed gap is at least +2 and the trimmed gap is below +2 the label is INCONCLUSIVE even if the trimmed gap is at most 0 (the INCONCLUSIVE clause is applied before AGAINST).
12. Thresholds. The spec's inequalities are inclusive where it writes at least or at most, so a value exactly on such a threshold takes the SUPPORT or AGAINST label; where it writes above or more than (P2 weighted gap, P4 own growth, P3 stock against GDP), a value exactly on the threshold fails the condition and the label is INCONCLUSIVE unless the other side holds. Comparisons use values rounded to 9 decimals. If both SUPPORT and AGAINST conditions held the label would be INCONCLUSIVE; none did.
13. Coverage. Share of 2025 ex-AI capex = sum of the panel's CY2025 capex over the sum of all positive CY2025 `PaymentsToAcquirePropertyPlantAndEquipment` facts of firms that are neither in the AI complex nor without a SIC (any form, any year-end; SIC for all 3511 CIKs was fetched). Two denominators are given: all ex-AI classes, and the headline class alone.
14. P3 uses Q4 values not seasonally adjusted for the Z.1 stocks and the seasonally adjusted annual rate for GDP.

## Sources and vintages

| source | url | fetched (UTC) | bytes | sha256 |
|---|---|---|---|---|
| bea1 | https://apps.bea.gov/national/Release/XLS/Survey/Section1All_xls.xlsx | 2026-11-13T14:28:19Z | 4067847 | a920921a004910f9 |
| bea5 | https://apps.bea.gov/national/Release/XLS/Survey/Section5All_xls.xlsx | 2026-11-13T14:28:20Z | 1820904 | 12f0fd7993b53245 |
| z1 | https://www.federalreserve.gov/releases/z1/data/FRB_Z1_csv.zip | 2026-11-13T14:28:27Z | 64219006 | 83b8eded0bc7f9b7 |
| c30 | https://www.census.gov/construction/c30/xlsx/privsatime.xlsx | 2026-11-13T14:30:43Z | 197163 | e11e6cd8c5a66b2e |
| fed-series-page | https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FL103020000&t= | 2026-11-13T14:41:50Z | 93032 | 2fd842595980eb17 |
| sec-submissions | https://data.sec.gov/submissions/ | 2026-11-13T14:32:03Z .. 2026-11-13T14:52:11Z | 385886651 | 4e3bbb048ec44f52 |
| sec-submissions-older-pages | https://data.sec.gov/submissions/ | 2026-11-13T14:38:37Z .. 2026-11-13T14:41:44Z | 79668729 | 57b4497a89c94b42 |
| census-btos | https://www.census.gov/hfp/btos/downloads/ | 2026-11-13T14:31:01Z | 0 | - |

The 24 SEC frames (tags Assets, CashAndCashEquivalentsAtCarryingValue, CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents, PaymentsToAcquireBusinessesNetOfCashAcquired, PaymentsToAcquirePropertyPlantAndEquipment, PropertyPlantAndEquipmentNet; periods CY2016, CY2019, CY2022, CY2025, and the PPE, acquisition, cash and assets periods named in the code) are listed one per row in `vintages.csv` with their fetch time, size and sha256. BEA files: published October 29, 2026 (Section 5) and published October 29, 2026 (Section 1). Z.1 release: Fed Board file dated 11 Sep 2026. C30: file dated 2 Nov 2026, latest month Sep-26. SIC history is not reconstructed. All requests to data.sec.gov carried the declared tool name only and ran at most 4 a second; no request went to www.sec.gov or FRED. The first four rows' fetch times are the files' modification times, because they were downloaded by a first probe before the fetch log existed.

## Reproduce

```
python3 bin/cv1_confidence_velocity.py selftest
python3 bin/cv1_confidence_velocity.py fetch --what bea|z1|census|frames|submissions|submissions-all [--max-requests N] [--budget-seconds S]
python3 bin/cv1_confidence_velocity.py build
```

`fetch` is resumable (files already in the cache are skipped); `build` is offline and reads only the cache. Checking the work: `bash bin/check.sh --all` runs gate M31 over this folder.
