# D10R verification — 2026-08-30. Grok adversarial review of the D10 construct
**Return preserved verbatim: `_research/D10R_Reuse_Review_Return_paste.md`. Every checkable
figure re-measured in-house before accepting a verdict. Outcome: 2 claims fall (C-066, C-067),
2 stand with amendments (folded), 1 falls-as-market-description / stands-as-scoped.**

## What I re-verified (all CONFIRMED)
- OFR Brief 26-03 Figure-1 table, from the on-disk PDF: money funds lend 2,927.5 / borrow 0.0
  (100% lending); G-SIBs net −472.4; primary dealers lend 2,832.2 / borrow 3,818.6 / net −986.4;
  hedge funds lend 1,007.0 / borrow 2,811.6 / net −1,804.7 ($bn, H2-2025). Exact.
- NY Fed PD API: PDPOSGST-TOT (net UST position) 2026-08-19 = 436,406 $mn = 436.4bn. Exact.
- Uncleared repo OUT 1,123.2 = my own venue table (149.0 + 974.2) — Grok used my numbers
  against my gloss, correctly.
- DTCC 19 Aug sponsored DVP 1,590.3 — matches data/history vintage. Exact.
- WFC 10-Q (acc 0000072971-26-000302, fetched): permitted 600.3 / repledged 448.9 at Jun-26;
  469.2 / 309.3 at Dec-25. Verbatim. A real omission from D10 v1.
- XBRL frames census (Grok's settle-it step, executed): us-gaap:FairValueOfSecuritiesReceived
  AsCollateralThatCanBeResoldOrRepledged, CY2026Q2I: 17 filers; JPM 2,181.4 / GS 1,431.9 /
  WFC 600.3 confirm the hand-pulls; MS, BAC, BNY, Citi do not tag the concept (custom tags).
  Mid-tier adds: Schwab 228.2, Jefferies 72.0, StoneX 38.3, FNMA 37.2, State Street 20.1.
- Singh Risk.net (on-disk txt): "over half of the roughly $13 trillion global market";
  "JP Morgan and Barclays ... each offering around $1.8 trillion". Verbatim.
- WP/19/106 (on-disk PDF): p.14 text "pledged collateral received by the major banks that
  could be onward re-pledged in their own name was around US$7.5 trillion" — numerator object
  = PERMITTED stock, settled from the source. Figure 3 read visually by me (p.15 of the PDF):
  2017 bars US panel ≈ JPM 970 / GS 770 / MS 600 / Merrill-BoA 560 / Citi 460 ≈ $3.4trn —
  Grok's UNCERTAIN visual reads confirmed within reading error.

## Verdicts as adjudicated
- CLAIM 1 (venue gloss): **falls in half** → C-066. "Enters mostly off-FICC" stands (56.8% of
  IN). "Exits on-FICC/triparty" is wrong (MMF-facing 41.0% vs uncleared OUT 37.3%), and venue
  is not counterparty — OFR's entity typing shows dealers net-borrow 986.4 for inventory.
- CLAIM 2 (84%): **stands amended**. WFC folded: six-bank Jun-26 utilization 83.2%
  (6,149.6 / 7,389.7). Heterogeneity caveat promoted from footnote to text: JPM includes
  derivatives + PB receivables; BNY includes custody agreements; BAC includes loans; MS
  excludes 15c3-3 segregated. This is a group-wide re-use aggregate, NOT UST-repo utilization.
- CLAIM 3 (+19% H1): **stands amended**. With WFC: permitted +19.3%, repledged +21.5%
  (6,192.0→7,389.7 / 5,061.8→6,149.6). Ex-BAC (rounding artifact risk): +17.6% / +19.4%.
  Both observation dates are quarter-ends; a composition shift is not excluded.
- CLAIM 4 (one hop): **falls as market description** → C-066; stands as scoped (near-tautology,
  weight reduced). New map facts folded: HFs lend $1,007.0bn (re-use-capable node); uncleared
  repo OUT $1,123.2bn carries dealer-to-dealer / dealer-to-HF hops.
- CLAIM 5 (Singh comparison): **falls** → C-067. Correct like-for-like: Figure 3 US five-name
  panel ~3.4trn (2017) → same names ~7.5trn (Jun-26, Citi Dec-25) = ×2.2; global 7.5 → 13trn
  = +73%; US share 45% → ~57% (matches "over half"). JPM ≈ Singh's "~$1.8trn" is a [C-071 31 Aug: the right vintage is Sep-2025, $1,829.9bn — his Jan-2026 article predates the Dec-2025 disclosure] 
  direct cross-validation that his numerator = the permitted stock.

## Grok errors: none found in its evidence layer. 13/13 checkable assertions verified.
(Its "BAC Note 9" vs my agent's note-location description differ; immaterial, figures identical.)
