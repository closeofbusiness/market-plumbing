# BIS CGFS Papers No 65, "US dollar funding: an international perspective" (June 2020): what it adds to the FX list

*Read 19 Oct 2026 by a Sonnet reader (whole paper, page-referenced) and mapped against the project's FX list by a second agent;
compared and checked by the supervisor. Source: https://www.bis.org/publications/cgfs-paper-65-us-dollar-funding-international-perspective.pdf
(87 pages; fetched 19 Oct 2026, HTTP 200). The paper's numbers are 2019-2020 and are used here for method, not as current values.
Page numbers are the paper's printed pages.*

## What the paper is

A CGFS working-group report mapping who borrows and lends dollars outside the US, through which instruments, and where the
vulnerabilities sit: short wholesale funding of non-US banks; non-bank investors (Asian insurers and pension funds, European funds)
funding or hedging long dollar assets with short FX swaps (about three quarters of a sample of Asian insurers' and pensions' forwards
mature within three months, p 32); concentration in a few global banks; reliance on US money funds (prime funds lost about $1trn
after the 2016 reform, p 27); quarter-end window-dressing spilling into FX swaps (pp 27-28); and data opacity (pp 41-43). It names the
March 2020 stress and the effect of the Fed swap lines (pp 46-52).

## Already on the FX list (no change needed)

BIS LBS/GLI dollar credit (F11, F21); FX-swap dollar debt from the BIS OTC statistics (F7, F8); the cross-currency basis (F5, from the
DTCC tape, which the paper treats as a funding-pressure barometer, pp 63-64); Fed swap-line usage (F18); foreign-holder hedge ratios
(F9; the paper's Japanese life insurers figure, about 60% hedged in FY2019, p 32, fits the project's panel: about 60% in 2021 and 40% in
2024); Cayman and TIC (F13).

The paper also supports, qualitatively, the project's caveat on F8: UK trade-repository data (EMIR, confidential) showed insurers,
pension funds and investment funds net short dollar forwards in 2019 (pp 14-15) - consistent with hedging, but still not a measured
hedging share of the free BIS series.

It confirms an earlier unvetted lens claim (`_research/offshore_moneylike_lenses.md`): Japanese banks moved from short FX swaps
towards longer cross-currency swaps, client deposits and bonds (pp 65-66).

## Candidates to add (free data checked by the supervisor, 19 Oct)

| # | Candidate | What it adds | Free data (checked) | Size |
|---|---|---|---|---|
| X1 | **Full hedging cost and the FX-hedged Treasury yield** for yen and euro investors | The project's basis ledger gives only the basis; the larger part of hedging cost is the short-rate gap, which the ledger lacks (ST1). Hedged 10-year Treasury yield vs JGB and Bund yields is the incentive the paper describes (p 9, Annex B) | SOFR (NY Fed API, 200), €STR (ECB data API, 200), BoJ TONA (stat-search, 200); basis from `data/swap_tape/`; yields already cached | small build |
| X2 | **Foreign banks' US offices: net due to related foreign offices** (weekly) | The paper's intermediation model: dollars moving between US branches and head offices. A live, free flow series the list lacks | Fed H.8, "Net due to related foreign offices" (in the current release, checked) | small pull |
| X3 | **US money funds' lending to non-US banks by bank nationality and tenor, with quarter-end dips** | The paper's MMF dependence and window-dressing points; the project has OFR aggregates and an N-MFP3 census, but no nationality or quarter-end cut | SEC N-MFP3 (project scripts `bin/census_nmfp3*.py`), OFR MMF Monitor | medium |
| X4 | **Quarter-end effect in the cross-currency basis** | Tests the paper's quarter-end spillover on the project's own daily tape | `data/swap_tape/` (no new data) | small |
| X5 | **Japanese banks' dollar "stability gap" and life insurers' hedge ratio as series** | Extends F9/F12 with the BoJ's own measures (the paper reports a record-low gap of 2.5% at end-Nov 2019, pp 31, 65-66) | BoJ Financial System Report (semi-annual), BoJ / Life Insurance Association releases | small, manual |
| X6 | **Dollar international debt securities by issuer sector** (BIS IDS) | The paper finds securities were about three quarters of the five-year rise in dollar funding (p 22); the project uses LBS and GLI but not IDS by sector | BIS IDS (free) | small |

Not candidates: the paper's FX-swap-implied basis by currency and hedged-yield charts (Bloomberg), Crane MMF data, EMIR positions,
ECB survival periods and Refinitiv firm accounts are not free. EME and Chinese corporate dollar debt (Annex G) is outside the goal's
current scope unless it is asked for.

All are open candidates, not results; none says that a flow caused a price.
