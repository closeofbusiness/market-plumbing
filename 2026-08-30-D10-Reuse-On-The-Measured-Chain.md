# D10: re-use on the measured chain — the dealer node, instrumented
**Date: 2026-08-30. Status: BUILT v1, then ADVERSARIALLY REVIEWED same day (D10R, Grok — 13/13 of its evidence checks verified in-house). Strikes marked [C-066]/[C-067]; §6 carries the amendments.**
**Everything in-house and free: NY Fed Primary Dealer statistics API + SEC EDGAR 10-Q/10-K.**

## 0. The question

The cash-pool → FICC → hedge-fund chain is measured at all three joints (N-MFP3, DTCC/FR2004,
Form PF). D10 asks what RE-USE happens on that chain: where collateral can be re-pledged, where
it cannot, and what the measured intensity is at the one node where re-use is possible — the
dealer. Two instruments, both new to the workspace today.

## 1. Instrument one: the NY Fed primary-dealer venue split (weekly, $bn, UST ex-TIPS)

The SBN2024 series break of the Primary Dealer statistics (FR 2004 successor) splits dealer
Treasury financing BY VENUE — including the FICC sponsored legs separately. Pulled via
`bin/pull_series.py --only nyfed_pd` (new source; histories in `data/history/pd_ust_*.csv`).
Week of 2026-08-19, gross outstanding, primary dealers only:

| venue                                | repo OUT (collateral delivered) | reverse IN (collateral received) |
|--------------------------------------|-------:|-------:|
| Cleared bilateral, general            |   99.9 |  136.7 |
| Cleared bilateral, specified          |  530.0 |  513.1 |
| **Cleared bilateral, SPONSORED**      |  120.0 |  478.7 |
| GCF                                   |   20.9 |   37.9 |
| Triparty (ex-GCF), general collateral |  875.5 |   18.2 |
| Triparty, sponsored GC                |  239.5 |    0.0 |
| Uncleared bilateral, general          |  149.0 |  298.0 |
| Uncleared bilateral, specified        |  974.2 |1,261.0 |
| **TOTAL**                             |3,008.8 |2,743.6 |

The chain is legible in the venue signs. Collateral comes IN from leverage takers: uncleared
bilateral 1,559.0 (the off-FICC hedge-fund leg — the venue OFR's NCCBR work associates with
zero/low haircuts) plus sponsored DVP 478.7 (the on-FICC hedge-fund leg). It goes OUT to cash
pools: triparty GC 875.5 + sponsored triparty GC 239.5 + sponsored DVP 120.0 — the MMF-facing
legs. OUT exceeds IN by 265.2, the dealers' own-inventory financing floor. History (from 2022)
shows sponsored DVP reverse IN peaked near 690 in Dec-2025 and sits at 479 now; uncleared
bilateral IN has been ~1.4–1.6trn throughout — ~~the basis-trade collateral mostly enters the dealer off-FICC and exits on-FICC/triparty~~ **[C-066: the exit half is wrong — MMF-facing OUT is 41.0% (1,235.0) vs uncleared bilateral OUT 37.3% (1,123.2); only the entry half stands (uncleared = 56.8% of IN). And venue is not counterparty: OFR Brief 26-03 (entity-typed, H2-2025) shows primary dealers themselves net-borrow 986.4 — a slice of the OUT side finances dealer inventory (net UST position 436.4 the same week, PDPOSGST-TOT), not pass-through.]**

Joint-comparison caveat, stated not forced: DTCC's SponsoredVolume.csv (ficc_sponsored_dvp_bn
1,556.5 on 20 Aug) is activity across ALL sponsoring members and both directions; FR2004 is
primary dealers' own outstanding positions. 478.7 + 120.0 ≈ 600 of the DTCC 1,556 is the
PD-attributable part; the two series measure different objects and are not reconciled here.

## 2. Instrument two: the six banks' repledge stocks (10-Q, all collateral classes)

Fair value of collateral RECEIVED with the right to sell/repledge, and the amount actually
re-used. All figures verified verbatim against the filings by me (grep on the fetched HTML);
accessions in `data/series.tsv`.

| bank | permitted ($bn) | repledged ($bn) | utilization | period |
|------|------:|------:|-----:|--------|
| JPM  | 2,181.4 | 1,741.8 | 79.9% | Jun-26 |
| GS   | 1,431.9 | 1,265.7 | 88.4% | Jun-26 |
| MS   | 1,382.7 | 1,062.2 | 76.8% | Jun-26 |
| BAC  | ~1,400  | ~1,300  | ~93% (1-digit rounding) | Jun-26 |
| BNY  |   394   |   331   | 84.0% | Jun-26 |
| Citi | 1,064   | not quantified ("a substantial portion") | — | **Dec-25 (10-K only)** |
| Five-bank Jun-26 [C-075: WFC omitted; six-bank = 83.2%, §6] | 6,789.4 | 5,700.7 | 84.0% | |
| Six-bank (mixed dates) | 7,853.4 | — | | |

Two findings inside the table:

**(a) ~~The stock re-use rate at the US dealer complex is ~84%.~~** **[C-075: this five-bank figure
omitted Wells Fargo. The six-bank rate is 83.2% (6,149.6/7,389.7) — see §6. The five-bank arithmetic
below is correct for those five names; it is not the complex-wide rate.]** Of every dollar of collateral
the five banks may re-use, 84 cents is re-used. This is the measured stock counterpart of the
flow pass-through in §1.

**(b) H1 2026 was a step-change.** **[C-075: five-bank; the six-bank growth including WFC is
+19.3% permitted / +21.5% repledged — §6.]** Five-bank like-for-like Dec-25 → Jun-26: permitted
5,722.8 → 6,789.4 (**+18.6% in six months**); repledged 4,752.5 → 5,700.7 (**+19.9%**).
JPM alone +410.4 permitted. The re-usable collateral pool at US dealers grew by over a trillion
dollars in two quarters — the balance-sheet signature of the same H1-2026 expansion the
sponsored and uncleared repo series show. (Caveat: these stocks span ALL collateral classes —
equity PB collateral included — not just Treasuries.)

## 3. Where re-use is possible on the chain, mechanism-signed

- **Hedge fund → dealer**: the fund's UST passes with full re-use rights (title transfer in
  repo). Both venues (uncleared bilateral, sponsored DVP) deliver re-usable collateral IN.
- **Dealer node**: ~~the ONE re-use point~~ [C-066 — the one re-use point *on this two-leg chain*; the market has others: hedge funds lend $1,007.0bn of cash (OFR 26-03) and therefore hold repledgeable collateral themselves, and uncleared repo OUT ($1,123.2bn) carries dealer-to-dealer and dealer-to-HF hops]. Measured: 84% stock utilization; flow OUT/IN 1.10.
- **FICC**: novation, not a re-use hop. Margin (clearing-fund deposits) is a re-use SINK
  (N3 §8 wedge, 0.08trn).
- **Dealer → cash pool**: terminal. MMF collateral sits in a BNY triparty shell; SEC rules and
  MMF practice mean money funds do not re-pledge repo collateral. BNY's own 10-Q separates its
  principal book (394/331) from the agent book, and dealer 10-Qs disclose segregation carve-outs
  (GS $47.06bn segregated securities; MS $28.1bn; JPM $14.2bn segregated for customers).

So the measured chain supports EXACTLY ONE re-use hop: HF → dealer → MMF, length two, and the
84% utilization says that hop is nearly saturated. A chain-level velocity materially above ~2 on THIS chain is mechanically impossible (true as scoped, but near-tautological — D10R correctly caps its evidential weight: the Singh gap lives exactly in the chains this scoping excludes — inter-dealer, dealer-to-HF, cross-border, derivatives margin). ~~New input for the Singh gap: the US-six permitted stock alone is now ~7.9trn — the size of Singh's entire GLOBAL pledged pool at end-2017. The bank-side numerator has roughly doubled-plus since his baseline on US banks alone.~~ **[C-067 — wrong perimeter: Table 2's $7.5trn is GLOBAL (US + Europe + Canada/Japan). Corrected like-for-like (D10R, re-verified): WP/19/106 Figure 3 US panel — **now rebuilt from the 2017 10-Ks themselves, superseding this visual read: $3,351.4bn (2017) → $7,460.0bn = ×2.23; see `2026-08-31-N3v4-Singh-Reconciliation.md`.** The original visual estimate (JPM ~970 + GS ~770 + MS ~600 + Merrill/BoA ~560 + Citi ~460 ≈ $3.4trn) proved accurate to +0.3% but is not citable. Figure 3 is on printed **p.14** (C-072; p.15 was the PDF viewer page). Global: 7.5 → ~13trn (Singh, Risk.net, 12 Jan 2026) = +73%; the US five-name share went 44.7% → 57.4%, CONSISTENT WITH (not an independent reproduction of) Singh's "over half" — the share uses his global pool as denominator (C-073). Cross-validation [vintage-corrected, C-071]: Singh's Jan-2026 article predates the Dec-2025 disclosures; the figure available to him was JPM's **Sep-2025 permitted $1,829.9bn**, which **rounds to** his "around $1.8 trillion" (the percentage gap is 1.7% — an earlier "0.5%" here was wrong arithmetic, C-072). And the numerator OBJECT is now settled from the source: WP/19/106 p.14 defines the pool as collateral "that could be onward re-pledged" — the PERMITTED stock. Feeds N3 v4 and removes one of the three Singh-ask questions.]**

## 4. Honest limits

1. FR2004: primary dealers only, UST only, gross, weekly Wednesdays; own-inventory vs re-pledged
   collateral in repo OUT is NOT separated — the 84% stock ratio is the best available proxy.
2. 10-Q stocks: all collateral classes, group-wide, quarter-end (window-dressed); BAC rounds to
   1 digit; Citi discloses only annually and never quantifies the repledged amount.
3. The two instruments have different perimeters (PD subsidiaries vs holding companies) and
   different collateral universes; ratios from one are not applied to the other anywhere above.

## 5. Registered

- New puller: `bin/pull_series.py --only nyfed_pd` (6 weekly venue series; add to the
  quarter-end calendar pulls).
- 17 new rows in `data/series.tsv` (6 venue + 11 bank).
- Raw filings and extracts preserved in the session scratchpad; accession numbers above are the
  durable pointers.

## 6. Review outcome (D10R, Grok chat window, returned and adjudicated 30 Aug 2026)

Verdicts as adjudicated after in-house re-measurement (`_research/D10R_verification_2026-08-30.md`;
raw return `_research/D10R_Reuse_Review_Return_paste.md`; 13/13 of the review's checkable
assertions verified — the strongest external return of the programme so far):

1. **Venue gloss: broken and struck** (C-066, above). Venue is not counterparty; OFR 26-03
   entity-typed is now the companion instrument to the FR2004 venue split.
2. **WFC was missing.** Verified and folded: permitted 600.3 / repledged 448.9 (Jun-26);
   469.2 / 309.3 (Dec-25). **Six-bank Jun-26 utilization: 83.2%** (6,149.6 / 7,389.7).
   Growth incl. WFC: permitted **+19.3%**, repledged **+21.5%** H1-2026; ex-BAC (rounding
   risk): +17.6% / +19.4%. Headline unchanged in kind: a step-change, robust to composition.
3. **The utilization number is a group-wide re-use aggregate, not UST-repo utilization** —
   JPM includes derivatives and PB receivables, BNY includes custody agreements, BAC includes
   loans, MS excludes 15c3-3 segregated securities. Promoted from caveat to the definition.
4. **XBRL census unlock** (Grok's suggestion, executed): the frames API returns all filers
   tagging `FairValueOfSecuritiesReceivedAsCollateralThatCanBeResoldOrRepledged` in one call —
   17 filers CY2026Q2I; confirms JPM/GS/WFC; adds Schwab 228.2, Jefferies 72.0, StoneX 38.3,
   FNMA 37.2, State Street 20.1. MS/BAC/BNY/Citi use custom tags (manual). Candidate for a
   quarterly `--only` puller at next 10-Q season.
5. **The Singh comparison: rebuilt** (C-067, above). US five-name panel ×2.2 since 2017;
   numerator object = permitted stock, settled from WP/19/106 p.14 itself.

New facts for the chain map from OFR 26-03 (H2-2025, verified from the on-disk PDF): money
funds lend 2,927.5 / borrow 0 (a pure terminal node — confirming §3's scoping); hedge funds
lend 1,007.0 as well as borrow 2,811.6 (NOT a terminal node — a re-use-capable intermediary
on some chains); primary dealers net-borrow 986.4; G-SIB banks net-borrow 472.4.
