# Funding-identity checks: rebuild of the Z.1 and nominal-GDP figures

Source note: `_research/funding_identity_adversarial_reviews.md` (not edited). Its source files were lost.
This folder re-derives every figure in it that rests on Z.1 or on BEA nominal GDP.

## What was rebuilt, from which release
- Z.1: release **2026-06-11, data through 2026:Q1**, the exact release the note names. It was still archived at
  federalreserve.gov/releases/z1/20260611/z1_csv_files.zip (8,075,952 bytes). Nothing in data/ held it before.
  Revision noise is therefore not an issue for the Z.1 rows.
- BEA: NIPA flat files NipaDataQ/NipaDataA/SeriesRegister fetched 2026-11-11, **data through 2026Q3**. This is a
  LATER vintage than the note's (June to August 2026). Every figure that divides by GDP, and every BEA-coded
  level, can differ by revision. Those rows say so; no match was forced.
- Raw files: data/vintages/funding_identity_checks/20261111/ (54 MB, git-ignored; requests_log.csv lists the 4 requests).
- `bin/funding_identity_checks.py fetch` (4 GETs), then `build` (offline, byte-identical).

## Result (reconciliation.csv, 133 rows)
- 83 MATCH within rounding, 50 DIFFERS, 0 NOT FOUND. Status uses half a unit of the last quoted digit.
  Where a DIFFERS is inside one unit, the note says "would match if truncated".
- Figures with several rows have one per plausible construction ("construction a of n"); read all.
## What did not reproduce
- Financing gap "negative in five of the last six quarters": 4 of 6 (2024:Q4 and 2025:Q1 are positive).
- Identity "residual 0.000": true only when the sector discrepancy (FA107005005) is in the sum.
- General government gross saving -1,146: Z.1 gives -1,135 (two constructions), BEA now -1,125.
- Federal deficit 5.6% of GDP: federal current deficit is 5.66% (5.7 rounded); no 5.6 federal construction fits.
- 110.5%: only NFC gross saving / NFC capex over the trailing four quarters (110.56) is close; the note says 2026:Q1.
- Private domestic +3.7% of GDP: none of 7 constructions gives 3.7 (range 3.5 to 13.1; 2025:Q4 gives 3.57).
- Current account 4.1% in 2024 (4.02) and "down 0.8pp" (0.68). The 2026:Q1 $1,065bn and 3.3% do match.
- Info-processing + software +585 of +701 (83%): neither base period reproduces it (443/628 or 468/723).
- NIPA CFC "+36" in 2025:Q1: 23. Net investment 708 (709), +4.9% (5.0), "roughly 90%" (91): rounding-size.
- "$133-224bn per quarter" NFC capital vs financial gap: no window of recent quarters fits.
- Debt 9.24% annualised: 9.13 (the Wicksell section's own figure). Household mortgage debt 10,648 / 9,328 / -12.4%:
  10,650 / 9,301 / -12.7 in this release. MMF 3,120 is 3,120.5. IEEPA ~168 is 166.
- BEA revisions: GDP 31,865.7 / 31,422.5 now 31,906.3 / 31,462.5; W274RC 1,244.2 now 1,204.6; AD01RC -2,955.2 now
  -2,880.3; W020RC 807.9 now 812.5; GDP y/y 6.07 now 5.75.
## Not rebuilt
- M2 (out of scope; its values are taken from the note only as numerators for the M2/NGDP ratios).
- PSAVERT, FRED-only series, BIS quotes, and arguments (Kalecki 41%, the ~$82bn/yr wage bill).
## Notes
- Z.1 package names: NFC rows are in S11_1_*, combined nonfinancial business in S11_t; there is no file called S11_a.
- FU... series are quarterly NSA flows; the note's "economic CFC" is FU106300003.Q x 4. FA... series are SAAR.
## Supervisor notes (11 Nov 2026)
- 110.5%: the supervisor re-derived 110.56 (trailing four quarters to 2026:Q1) and 124.35 (2026:Q1 alone) from S11_1_t.csv. The note's other tables are trailing-four-quarter means, so "2026Q1" reads as "four quarters to 2026Q1"; not a defect.
- "Five of the last six": already corrected to four quarters in Funding_Identity_First_Principles.md (financing-gap paragraph).
- +3.7% of GDP: _research/old_masters_traditions.md takes sectoral balances from Z.1 table S.1.2 (four-quarter sums), which none of the seven constructions here uses. Untested, not refuted.
- None of the figures that did not reproduce reaches docs/index.html or the ANSWER (triage of 8 Oct).
