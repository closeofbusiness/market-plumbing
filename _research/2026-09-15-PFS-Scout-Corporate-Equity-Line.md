# PFS Scout: Corporate-Equity / Equity-Securities Holdings Line

**Status: VERIFIED YES** (Qualifying Hedge Funds only — not PE)

**Date:** 2026-09-15  
**Scout only** — no Z.1 F51 household-plug measurement.  
**Rule context:** Martin ruled 6b SCOUTING NOT ESTABLISHED; this note only verifies whether PFS publishes a usable equity-holdings line.

---

## Verdict (one-liner)

**VERIFIED YES** — PFS Table 8.16 / 8.17 publish QHF **Listed / Unlisted Equities** notional-exposure lines; **no PE equivalent** — cannot bound PE inside F51 from these lines.

---

## Current PFS URLs

| Role | URL | HTTP |
|------|-----|------|
| IM landing (report list) | https://www.sec.gov/data-research/investment-management-data/division-investment-management-private-fund-statistics | 200 |
| Viz landing | https://www.sec.gov/data-research/statistics-data-visualizations/private-fund-statistics | 200 |
| QHF Investment Types viz | https://www.sec.gov/data-research/data-visualizations/private-fund-statistics/private-funds-qualifying-hedge-fund-investment-types | 200 |
| **Latest PDF (2025Q4)** | https://www.sec.gov/files/investment/private-fund-statistics-2025-q4.pdf | 200 |
| **Latest Excel supporting data (2025Q4)** | https://www.sec.gov/files/investment/private-funds-statistics-2025-q4-supporting-data.xlsx | 200 |
| Prior PDF (2025Q3, linked on landing) | https://www.sec.gov/files/investment/private-funds-statistics-2025-q3.pdf | 200 |

Notes:
- Landing page (as of scout) still lists archive links through **2025 Q3**; the **2025Q4** PDF/Excel are live on `/files/investment/` (PDF filename uses singular `private-fund-statistics-2025-q4.pdf`).
- Landing/viz pages have **no equity breakdown on-page**; equity lines live in linked PDF/Excel (Tables 8.16–8.17 / Tab.8.16–8.17).
- SEC fetches used User-Agent: `ThirdDerivativeResearch/1.0`.

---

## YES — equity securities lines (Qualifying Hedge Funds)

**Table name:** Table 8.16 — *Aggregate Qualifying Hedge Fund Long Notional Exposure, by Investment Type ($ Billions)*  
**Companion:** Table 8.17 — *Aggregate Qualifying Hedge Fund Short Notional Exposure, by Investment Type ($ Billions)*  
**Source questions:** Form PF, Questions 26 and 30  
**Period verified:** Dec 2024 – Dec 2025 monthly columns in 2025Q4 report (Excel Tab.8.16 historical back to 2013-01)  
**Excel sheets:** `Tab.8.16`, `Tab.8.17` in supporting-data workbook

### Exact line labels (equity / equity securities)

| Exact line label | Role |
|------------------|------|
| **Non-Financial Listed Equities** | Listed corporate/equity securities (non-financial issuers) |
| **Financial Listed Equities** | Listed equity securities (financial issuers) |
| **Non-Financial Unlisted Equities** | Unlisted equity |
| **Financial Unlisted Equities** | Unlisted equity (financial) |
| Non-Financial Equity Derivatives | Derivatives (not cash equity) |
| Financial Equity Derivatives | Derivatives (not cash equity) |

Illustrative Long values (Table 8.16, **Dec 2025**, $ billions): Non-Financial Listed Equities **2,422**; Financial Listed Equities **362**; Non-Financial Unlisted Equities **696**; Financial Unlisted Equities **46**.

### Units / frequency / coverage

- **Units:** USD billions of **notional exposure** (long and short separately), not book holdings / NAV-marked portfolio weights alone.
- **Frequency:** **Monthly** for Qualifying Hedge Funds (QHF) in Tables 8.16–8.17; report itself is published on a ~quarterly cadence.
- **Geography:** Investment-type equity lines are **not** split US vs non-US (no “US corporate equity” subline). Regional/country exposure is separate (Tables 7.12–7.15) for large HF advisers — not an equity-securities holdings line.
- **PE vs HF split:** Equity investment-type lines are **Qualifying Hedge Fund only**. There is **no** parallel investment-type / corporate-equity holdings table for Private Equity / Section 4 funds.

### Could these bound the F51 household plug for PE?

**No.** QHF listed/unlisted equity notionals do not measure PE fund corporate-equity holdings and cannot bound PE inside Z.1 F51. Do not treat Table 8.16 as a PE equity bound. (Scout only — no plug arithmetic performed.)

---

## PE (Section 4): what PFS publishes instead

Section 10 — *Section 4 Private Equity Fund Specific Information* — has **no** corporate-equity / equity-securities holdings line.

Published instead (2025Q4):

- Aggregate **GAV / NAV** by fund type (Tables 2.1–2.6), including Private Equity Fund and Section 4 PE splits
- **Borrowings**, fair-value hierarchy, beneficial ownership (incl. Tables 4.7–4.8 for Section 4 PE)
- Table 10.1: Gross Assets by **Portfolio Company Industry** (% of Section 4 PE GAV) — industry mix of CPCs, not securities holdings
- Tables 10.2–10.6: CPC counts, current liabilities ratios, PIK borrowings, **CPC debt-to-equity** ratios / CPC gross assets by D/E bucket
- Footnote: PE **region/country exposure removed** beginning 2024Q2 (Form PF revisions effective June 11, 2024)

---

## Landing-page caveat (why earlier routes failed)

- IM landing and viz pages resolve **200** but show aggregates (fund counts, GAV, NAV) and links — **no equity breakdown on the landing HTML**.
- Equity lines appear only after opening the **quarterly PDF** or **supporting-data Excel** (Tables/Tabs 8.16–8.17) or the QHF Investment Types visualization page (charts; same Form PF Q26/Q30 basis).

---

## Bottom line for 6b / F51 PE bound

| Question | Answer |
|----------|--------|
| Does PFS publish corporate equity / equity securities holdings lines? | **YES** — QHF Listed/Unlisted Equities in Tables 8.16–8.17 |
| US-only equity line? | **NO** |
| PE fund equity-holdings line? | **NO** |
| Usable to bound PE inside F51 household plug? | **NO** (wrong sector/fund type; notionals ≠ PE holdings) |

**Recommendation:** Keep 6b as **SCOUTING NOT ESTABLISHED** for a *PE* equity bound from PFS. QHF equity lines are real but out-of-scope for bounding PE in F51.
