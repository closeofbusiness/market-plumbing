# Cross-border and FX-funded demand

## Hypothesis

Official and private cross-border demand, FX hedges, the basis, and reserve recycling funded sovereign bonds or equities, and that funding is visible once hedged and unhedged legs share a denominator.

## Status

**Open.** Stocks and some bilateral holdings are measured. A hedged-versus-unhedged demand table is not. **No claim is made that FX flows, the basis, or official buying caused a yield or equity move.**

## Evidence

Offshore-dollar and Cayman reconciliation series are in the monitor, from [`2026-08-30-N2a-Offshore-Dollar-Leg.md`](../2026-08-30-N2a-Offshore-Dollar-Leg.md). Examples, latest row only: BIS USD liabilities to Cayman nonbanks about **$1,025bn** in 2026:Q1; FX USD leg notional about **$113.5trn** in 2025:S2 on the key `fx_usd_leg_total_trn`. These are stocks and notionals. They are not an attribution.

TIC July 2026 foreign net purchases of US equities were **+$2.8bn** for all countries, made of **−$10.6bn** by private (non-official) investors and **+$14.3bn** by official ones (SLT Table 1; the two figures differ in scope, not method, C-131). Source: [`_research/2026-09-17-TIC-July-2026.md`](../_research/2026-09-17-TIC-July-2026.md).

A European pensions scout exists ([`2026-09-14-E1-European-Pensions-Scout.md`](../2026-09-14-E1-European-Pensions-Scout.md)). Dutch pension asset stocks are in the monitor. They are not an EGB curve result. GPIF assets are in the monitor (about **¥320trn** at 30 June 2026). A claim that GPIF will buy a stated amount of JGBs is someone else’s call on the calendar; it is not a result of this programme.

JGB and euro-area government-bond holders by sector and the yield decompositions are in R3 ([`2026-09-27-R3-JGB-And-Euro-Area-Bonds.md`](../2026-09-27-R3-JGB-And-Euro-Area-Bonds.md), tables in `data/r3_rates/`). The cross-currency basis is now measured from the public DTCC swap tape (1-5-year JPY/USD premium about halved in two years; EUR and GBP near zero), in [`2026-10-15-ST1-Swap-Spreads-Inflation-Gap-And-Basis.md`](../2026-10-15-ST1-Swap-Spreads-Inflation-Gap-And-Basis.md). That is the premium, not the hedge ratio, and not a price driver.

A primary-source HTML note on the cross-border Treasury basis trade sits in the Dropbox tree and was not copied. The programme’s own N2a note is the citation.

## What would change the conclusion

One denominator for hedged and unhedged official and private demand, beside net UST, JGB, and EGB supply, with the price decomposition done first. Until that exists, these series stay measurements.

## Data used

TIC, BIS locational banking and GLI, CPIS, Irish and Luxembourg USD money funds, OCC bank FX notionals, GPIF and Dutch pension keys. See the monitor.

**First measurement map, 12 Oct 2026 (E-021):** `2026-10-12-E021-Where-The-Money-Comes-From-Rates-FX-Commodities.md`, with the FX agent's full tables in `_research/2026-10-12-E021-fx-inhouse-return.md`.

**Candidates from BIS CGFS Papers No 65 (read 19 Oct 2026):** the full hedging cost and FX-hedged Treasury yield; foreign banks' US offices' net due to related foreign offices (Fed H.8); US money funds' lending to non-US banks by nationality and quarter-end; the quarter-end effect in the basis; the BoJ's dollar stability gap and life insurers' hedge ratio as series; dollar debt securities by issuer sector (BIS IDS). Candidate 1 (the hedged Treasury yield) is BUILT, 19 Oct: [`data/hedged_ust_yield/`](../data/hedged_ust_yield/README.md) (spec `_research/2026-10-19-FX-Hedged-Treasury-Yield-Spec.md`). The others, 23-25 Oct: X2 H.8 foreign offices [`data/h8_foreign_offices/`](../data/h8_foreign_offices/README.md); X3 money funds' holdings with non-US institutions by parent country [`data/mmf_nonus_banks/`](../data/mmf_nonus_banks/README.md) (OFR monitor, E-027); X4 quarter-end basis, descriptive [`data/quarter_end_basis/`](../data/quarter_end_basis/README.md); X6 BIS dollar international debt securities [`data/bis_ids_dollar/`](../data/bis_ids_dollar/README.md); X5 closed as a note (below). All six CGFS 65 candidates are now built or closed. Details and the free sources checked: [`_research/2026-10-19-CGFS65-Dollar-Funding-Reading.md`](../_research/2026-10-19-CGFS65-Dollar-Funding-Reading.md).

**Bank of Japan Financial System Report, October 2026 (published 23 Oct; read for candidate X5 by Gemini through orchestrator_gemini, quotes checked by the supervisor against the PDF).** Life insurers "somewhat expanded their foreign bond positions overall" to end-June 2026, staying cautious on unhedged bonds while some added hedged foreign bonds as yields after hedging costs improved (p. 23; April 2026 report: holdings "more or less unchanged" to end-September 2025). This sits beside the MoF monthly flows (`data/jp_life_foreign_bonds/`, net disposition in 2026), which count redemptions and cover all life insurers reporting to MoF, while the BoJ text describes positions of the major insurers' general accounts. For major banks, "relatively stable funding exceeds their loans" in foreign currency (p. 46, Chart IV-3-15, data to 2026 Q2), and dollar funding premiums were "generally at low levels" (p. 13). The loan-to-funding gap and the hedge ratio are published only as charts, and ruling E-026 bars committing a file that rebuilds a BoJ series, so **X5 is closed as a dossier note, not a build**; the semi-annual report is re-read each April and October.
