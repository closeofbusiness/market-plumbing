# N2a-S verification — 2026-08-30, all 13 URLs curl-checked, load-bearing content spot-checked
**Return: `_research/N2aS_Offshore_Scouting_Return_paste.md` (verbatim). Verdict: SUBSTANCE GOOD,
URLS THE USUAL — 8/13 good, 4 constructed near-misses, 1 stale-but-redirects. Gemini marked
nothing UNVERIFIED despite the parcel requiring it; treat every identifier as unconfirmed until
used.**

## Per-question adjudication (corrected URLs are the ones to use)

Q1 BIS LBS — GOOD. data.bis.org/topics/LBS and /bulkdownload both live. Table A6.2 and
WS_LBS_D_PUB consistent with BIS conventions (identifiers not yet exercised — verify dimensions
on first pull). Caveat (immediate-counterparty residence, no look-through) is correct and is THE
known limitation.

Q2 CPIS/CIMA — SUBSTANCE RIGHT, BOTH URLS WRONG. IMF ?sk=GUID link is legacy and data.imf.org
403-blocks curl entirely (browser needed; portal migrated). CIMA link 404 — real pages are
https://www.cima.ky/investment-statistics and https://www.cima.ky/investments-statistical-digest
(Gemini's "/investments-statistics-digest" was a near-miss construction). CPIS semi-annual
cadence and vehicle-residence caveat: correct.

Q3 IMMFA/CBI — SUBSTANCE PLAUSIBLE, BOTH URLS WRONG. immfa.org alive but
/information/statistics.html 404s (whether public weekly stats still exist: UNVERIFIED). CBI
real path: https://www.centralbank.ie/statistics/data-and-analysis/other-financial-sector-statistics/money-market-funds
(200). "Table B.4.1" designation UNVERIFIED. MMFR Art. 37 caveat: correct.

Q4 TIC — ~~GOOD. mfh.txt live; Cayman line spot-checked (272.1 latest column, $bn)~~ **[C-068: mfh.txt is FROZEN at Mar-2023 (Treasury notice); it returns HTTP 200 with stale content, and the 272.1 I read as 'latest' was the oldest column (Jan-2022). Live MFH = slt_table5.txt; Cayman Jun-2026 = 453.1bn.]** Old
treasury.gov SHL link redirects to a TIC forms page on home.treasury.gov — usable. The caveat is
the valuable part and is right: NO official custodial-bias-corrected series exists; corrections
live in ad-hoc Fed research. NOTE for N2a: MFH Cayman ($453.1bn Jun-2026, live table) vs what SHL/CPIS attribute to
Cayman funds is itself the custodial-bias measurement.

Q5 SEC PFS — GOOD after redirect. Live page:
https://www.sec.gov/data-research/investment-management-data/division-investment-management-private-fund-statistics
(old /divisions/ URL 403s without UA, redirects with one). "Table 3.1/3.2" numbering UNVERIFIED
until a report is opened. Domicile-by-NAV/GAV content claim consistent with known PFS structure.

Q6 GLI/H.8 — GOOD. Both URLs live. H.8 "net due to related foreign offices" line: real (known
from N2c work). GLI FX-swap blind spot caveat: correct and important.

Q7 USD funding gap — EXCELLENT. Both analytical references verified as EXACT matches:
bisbull27 = "Global banks' dollar funding needs and central bank swap lines"; r_qt2212h =
"Dollar debt in FX swaps and forwards: huge, missing and growing" (the Borio/McCauley/McGuire
piece — directly relevant to N2a). "Econometric residual" caveat: correct.

## Lessons (repeat of C-050/C-054 pattern, no new correction entry)
Constructed-URL rate 4/13 despite an explicit do-not-construct rule and an UNVERIFIED-marking
rule, both ignored. The substance layer (dataset names, cadences, caveats) was near-perfect.
Continue using Gemini scouting for WHAT/WHERE, never trust the literal URL, always re-derive.
