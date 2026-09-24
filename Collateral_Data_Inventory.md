# Data and source inventory

Last updated: 2026-08-21

No institution publishes a "collateral-channel money creation" index. What exists is
a handful of people computing a collateral multiplier or reuse rate, plus stock data
you can build a series from. This file is the map.

---

## 1. People computing the multiplier

### Manmohan Singh (IMF) — originator
Method: source collateral × velocity. Source collateral comes from the
"collateral received permitted to be repledged/sold" footnote in the top ~15–20
dealer-bank annual reports. Velocity ~3.0 pre-2008, ~1.8–2.2 post.

- $9.4tn pledged collateral across the 18 largest dealer-banks at end-2020, up 50%+.
- Position as of 2026: velocity stuck for two to three years on Basel III balance
  sheet constraints.
- Latest commentary: *Collateral velocity is disappearing behind a digital curtain*,
  Risk.net / Central Banking, January 2026 — argues tokenisation could raise reuse
  rates while making them harder to observe.
- Link hub: sites.google.com/view/msinghdc

**Replicable:** yes, annually, from public dealer annual reports.

### Sebastian Infante, Charles Press, Zack Saravay (Federal Reserve Board)
Coined "collateral multiplier" in the precise sense: the ratio between a dealer's
total secured funding and their outright holdings financed through secured funding.

- Treasury collateral multiplier ≈ 10 across all contracts; fell to 5.5 in the second
  week of March 2020.
- Rehypothecated outgoing collateral $1.8–2.3tn against $2.0–2.4tn encumbered incoming.
- Papers: *The Ins and Outs of Collateral Re-use* (FEDS Notes, 2018);
  AEA Papers & Proceedings 2020; *What Drives U.S. Treasury Re-use?* (FEDS 2020-103);
  COVID-period FEDS Note, December 2020.

**Replicable:** no — uses confidential FR 2052a. Published series shape is usable.

### "Shadow Banks and the Collateral Multiplier" (Eastern Economic Journal, 2022)
Defines the collateral multiplier as dealer banks' matched book repo relative to
their trading book, estimated from the **public** NY Fed Primary Dealer Statistics.

**Replicable:** yes, weekly, free. This is the DIY series to build first.

### ECB — Rodrigues-Gomes et al., WP 3147 (Nov 2025)
*Repo collateral reuse and liquidity windfalls*, using SFTDS. ~15m transactions
July 2020–Feb 2025. Finds ~11.6% of European repo volume relies on reused
securities, ~€49bn/day, and rejects the liquidity windfall hypothesis. Free SUERF
policy brief summary available.

---

## 2. Stock and flow data infrastructure

| Source | What it gives | Frequency | Cost |
|---|---|---|---|
| NY Fed Primary Dealer Statistics (FR2004) | Matched book repo, trading book — the DIY multiplier | Weekly | Free |
| OFR Short-term Funding Monitor + US Repo Markets Data Release | US repo rates and volumes. ~$12.6tn daily exposures Q3 2025, ~$700bn above prior estimates. **No reuse field in NCCBR.** | Daily | Free |
| OFR Brief 24-07, *Repo Market Intermediation* | Traces reuse across segments: $109bn DVP, $212bn NCCBR reused | One-off | Free |
| ESMA SFT market report (SFTR data) | EU SFT outstanding €9.8tn Sept 2023, repo €6.7tn, sec lending €2.3tn | Annual | Free |
| ICMA — SFTR public data + ERCC European Repo Survey | European repo outstanding | Semi-annual | Free |
| FSB Global Monitoring Report on NBFI + dashboards | NBFI $256.8tn 2024, 51% of global financial assets; narrow measure $76.3tn (+12%); NBFI growth 9.4% vs ~half that for banks | Annual | Free |
| FSB (2017) *Non-Cash Collateral Re-Use: Measures and Metrics* + *Re-hypothecation and collateral re-use* | The standardised reuse metric definitions authorities collect against | One-off | Free |
| ISLA Securities Lending Market Report | On-loan balances, collateral, reinvestment (Pillar A) | Semi-annual | Free |
| S&P Global Securities Finance / DataLend (EquiLend) | Daily lendable and on-loan values | Daily | Paid |

---

## 3. FX swap / missing dollar debt

| Source | What it gives | URL |
|---|---|---|
| Borio, McCauley & McGuire, *Dollar debt in FX swaps and forwards: huge, missing and growing*, BIS QR Dec 2022 | The $80tn+ estimate, sectoral split | https://www.bis.org/publ/qtrpdf/r_qt2212h.htm |
| Borio, McCauley & McGuire, *FX swaps and forwards: missing global debt?*, BIS QR Sept 2017 | Original framing | https://bis.org/publ/qtrpdf/r_qt1709e.htm |
| McGuire (2022), *FX swaps and forwards in global dollar debt: "known knowns" and "known unknowns"*, Japan and the World Economy vol 64 | **The methodology paper.** Documents exactly which collections (OTCD, IBS, IIP, CPIS) combine and where they break — use this to rebuild and roll forward the estimate | https://ideas.repec.org/a/eee/japwor/v64y2022ics0922142522000457.html |
| BIS OTC derivatives statistics | FX notional outstanding by instrument, counterparty sector, maturity, currency. End-June / end-Dec. **The stock series.** | https://data.bis.org/topics/DER |
| BIS derivatives research hub | Curated papers using the statistics | https://bis.org/statistics/derivatives/ra.htm |
| 2025 Triennial — FX turnover | $9.6tn/day total; FX swaps $4tn/day (+5%), share 51%→42% | https://www.bis.org/statistics/rpfx25_fx.htm |
| BIS QR December 2025 (Triennial special edition) | *Global FX markets when hedging takes centre stage*; foreword *Shifting currents in FX and interest rate derivatives* | https://www.bis.org/publ/qtrpdf/r_qt2512.htm |
| BIS Global Liquidity Indicators | Quarterly dollar credit to non-banks outside the US. Pair with the off-balance-sheet estimate; the ratio is the leverage proxy | data.bis.org |
| CLS | Higher-frequency FX swap volumes between Triennials. CLS shows FX swap volumes $1.4tn→$1.8tn/day across the same window — a different read from BIS's +5%, itself informative about sample coverage | cls-group.com |
| Rime, Schrimpf & Syrstad, *Covered Interest Parity Arbitrage* (RFS) | Cross-currency basis as the price of the balance sheet constraint | — |

**Counter-argument to address:** ICMA Centre (Richard Comotto) argues BIS conflates
currency swaps with FX swaps and that the "misclassified as derivatives" premise is
flawed. Cite and answer it rather than omitting it.

---

## 4. Macro context series

| Series | Detail | Source |
|---|---|---|
| M2 (M2SL) | ~$23.2tn June 2026, +5.5% y/y, +2.1% over three months | https://fred.stlouisfed.org/series/M2SL |
| H.6 Money Stock Measures | Note: as of the 28 July 2026 release the Fed discontinued netting IRA/Keogh balances from small time deposits and retail MMF components; they are now a separate M2 component netted directly. Applies backward through the series — **rebase any pre-July-2026 comparison** | https://www.federalreserve.gov/releases/h6/current/default.htm |
| WGC Gold Demand Trends | Quarterly central bank purchases, ETF flows, bar and coin. Watch for Metals Focus revisions | https://www.gold.org/goldhub/research/gold-demand-trends |
| Triennial Survey archive | All vintages back to 1986 | https://www.bis.org/stats_triennial_surveys/index.htm |

---

## 5. Conceptual framing (no live series maintained by any of these)

- Pozsar, *Shadow Banking: The Money View*, OFR WP 2014-04 — the money-matrix taxonomy.
- Gabor & Vestergaard, *Towards a Theory of Shadow Money* (INET) — shadow money as
  repo liabilities backed by tradable collateral.
- Mehrling — the money view / dealer-of-last-resort framing.
- Ricks, *The Money Problem* — legal-institutional definition of money.
- Gabaix & Koijen — inelastic markets hypothesis; the ~5x flow-to-capitalisation
  multiplier. Central to the valuation half of the argument.
- Kalecki profit equation — links fiscal deficits to corporate profit, and therefore
  to self-funded AI capex.

---

## Build order

1. Weekly collateral multiplier from NY Fed Primary Dealer Statistics (EEJ 2022 method).
2. Annual source-collateral level from dealer annual report footnotes (Singh method).
3. FX swap stock series from BIS OTC derivatives statistics, sectoral split.
4. Roll forward the missing-dollar-debt estimate using McGuire (2022) methodology.
5. Overlay cross-currency basis as the constraint price.
6. Pillar A securities lending on-loan balances from ISLA.
7. Leave Pillar C unquantified and say so explicitly — do not estimate it.
