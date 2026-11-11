# Measurement-infrastructure checks: rebuild of the Z.1 figures in the research note

Source note: `_research/measurement_infrastructure_reviews.md` (not edited; its source files were lost). Handbook
lines 83, 171, 289, 345-346 (`Shadow_Debt_Measurement_Handbook.md`, not edited by the build) quote it and are covered too.

## What was rebuilt, from which release
- Z.1 release **2026-06-11, data through 2026:Q1**, the release the note names (line 6). Package:
  `data/vintages/funding_identity_checks/20261111/z1_csv_files.zip` (kept by bin/funding_identity_checks.py).
  Same release, so a DIFFERS is not revision noise unless a row says so.
- One reading of the debt/GDP rows uses BEA `NipaDataQ.txt` from the same folder (fetched 2026-11-11, a later vintage).
- `bin/measurement_infra_checks.py build` is offline (no network code), stdlib only, byte-identical on re-run.

## Result (reconciliation.csv, 516 rows = 469 figures; 40 figures have one row per reading)
- 449 rows MATCH within rounding, 39 DIFFERS, 24 NOT FOUND, 4 NOT Z.1. Tolerance: half a unit of the last quoted digit.
- By figure: 430 of 469 match under at least one reading, 11 differ under every reading, 24 NOT FOUND, 4 NOT Z.1.
- 24 NOT FOUND: z1_code_changes.txt and the crosswalk CSV (not in the zip), and FWTW holder cells and file
  facts (a different Fed release, the Enhanced Financial Accounts file of 2026-06-18, not in the zip). Where a FWTW
  number also sits in the package as a Z.1 series (3 cells), the row matches by value and says so.
- 4 NOT Z.1: Fed Financial Stability Report runnables figures that cite Z.1 codes as inputs.

## What did not reproduce
- "$12.1trn residual larger than the entire $14.45trn measured debt stock" (note 797, Handbook 83): 12,101.9 < 14,454.
- Household equity revaluation "-$1.8tn" (-1.39 equities, -1.68 with funds, -1.85 all financial assets).
- Government (federal + S&L) 2025 "-$1,116bn": -2,293.5; no subset of the six sectors gives it. "-$1,908bn": -1,979.2.
- Broker-dealer loans 2025:Q4 "$541.8bn, +53.5%": 542.1, +53.6 (possible revision if the note used the 2026-03-19 release).
- NFC debt/GDP 51.2 and 45.4: the BEA reading is within 0.1; the Z.1 GDP readings are 1 to 2 points off.
- "1,536 asset / 745 liability series": 1,541 / 743 nine-digit cores. "Eight straight quarters of net retirement":
  the run is 18 quarters (the 2024:Q1-2025:Q4 window holds exactly 8). 2021 sector sum and a few quarterly residuals: off by 1.
- Mislabelled in the note: "Finance companies 706,410" is the asset line; the 635,014 of lines 323/793 is FL103169535.
  Commercial mortgages 1,202,775 is FL103165505, not FL103165005 (1,475,560).

Supervisor, 11 Nov 2026: the "$12.1trn larger than the debt stock" claim is registered as C-157 and fixed at Handbook line 83 (about 84%); the note keeps its wording with a C-157 marker. The other rows that did not reproduce are rounding, labelling or construction differences inside a research note that no live claim on the page or in the ANSWER rests on.
