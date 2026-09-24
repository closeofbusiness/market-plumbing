<!-- Official transcript of The End Game Ep 61 (Martin's download, 11 Sep 2026); claims extracted and reconciled by a Sonnet agent. Quotes <=15 words. Index: 2026-09-11-Green-Substack-And-Ep61-Synthesis.md -->
# Ep 61 Official Transcript vs ASR Reconciliation — Mike Green, The End Game #61

Source: `The-End-Game_Transcript_0061_Mike_Green.pdf`, a local copy of the published transcript (third-party, not redistributed here) (20 pp., published Sept 07/08 2026), converted with `pdftotext -layout`. Page numbers below are the PDF's own printed page numbers (footer), verified to match the pdftotext page-split.
ASR file checked against: `2026-09-11-Green-Claims.tsv`, rows with episode_id 4555 (G-011 through G-020, 10 rows — confirmed by `awk` count, no other 4555 rows exist).

---

## 1. Speakers

Official transcript names three speakers, by full name at every turn:

| Name as given in transcript | Role (from context) | First line |
|---|---|---|
| Grant Williams | Host | p.2, "Before we get going..." |
| Bill Fleckenstein | Co-host | p.2, (00:47) |
| Michael Green | Guest | p.2, (01:29) — referred to verbally as "Mike"/"Mike Green" throughout |

**SPEAKER_00 = Michael Green: CONFIRMED.** Page 2: "**Michael Green** (01:39): It's been an interesting time period. For those who have not …" This is the exact identifying fact the ASR roster used to bind SPEAKER_00. I additionally checked all ten episode-4555 anchor quotes against the speaker tag immediately preceding each in the official text (see reconciliation table below) — every one falls inside a "Michael Green (mm:ss):" turn with no intervening speaker change. Attribution confidence: fully confirmed, not just the one identifying line.

Notes/artifacts in the official transcript itself (not ASR errors, just flagging):
- Title page (p.1) reads "Mike Green, **Tier One Alpha Capital**"; in-episode Green calls it "**Tier1 Alpha Asset Management**" (p.2) and gives the URL "**t1acapital.com**" (p.17). Three slightly different renderings of one firm name — a documented inconsistency in the source PDF, not something I'm resolving.
- p.9 has an orphaned timestamp "(26:12):" with no speaker name before a continuation of what is contextually Michael Green's Tickle-Me-Elmo question. Treated as a Green continuation, not a fourth speaker.

---

## 2. Reconciliation table — episode_id 4555 rows

**Result: all 10 rows CONFIRMED. Zero CORRECTED, zero MISATTRIBUTED, zero NOT FOUND.**

This is worth flagging explicitly since it runs against the base rate this project has otherwise found for ASR-derived claims (per prior sessions' notes on false "VERIFIED" tags): for this specific episode, every anchor quote in the file is a verbatim, correctly-attributed match to the official text, and every number checks out exactly. I re-verified each with `grep` against the pdftotext output plus a speaker-tag lookup, not by eye alone.

| claim_id | verdict | note |
|---|---|---|
| G-011 | CONFIRMED | Verbatim, Michael Green, p.4: "that fund is a liquidity concentration vehicle." Full mechanism (401k contributions arrive with no price judgment) matches. |
| G-012 | CONFIRMED | Verbatim, Michael Green, p.7. Both numbers exact: ~$300M/day baseline passive bid (largest caps) vs. ~$3B/day into Micron at the melt-up peak. |
| G-013 | CONFIRMED | Verbatim, Michael Green, p.7 (same paragraph as G-012, immediately following). "~50% of the daily price movement" exact. |
| G-014 | CONFIRMED | Verbatim, Michael Green, p.7. "~150% a year" breakeven figure exact. |
| G-015 | CONFIRMED | Verbatim, Michael Green, p.11. "$2bn/month → $4bn/month," "established under Yellen," "almost unlimited," off-the-run targeting — all exact. Only difference is typographic: PDF spells out "two billion"/"four billion," ASR file used numerals "$2 billion"/"$4 billion" — same value, not a factual error, not scored as CORRECTED. |
| G-016 | CONFIRMED | Verbatim, Michael Green, p.13. "25 to 35%" of incremental bond flow exact. |
| G-017 | CONFIRMED | Verbatim, Michael Green, p.9. "multiplier" mechanism and mutual-fund→ETF framing exact. |
| G-018 | CONFIRMED | Verbatim, Michael Green, p.8. "Trump accounts," "two choices, the S&P 500 or the Vanguard Total Market Index" exact. |
| G-019 | CONFIRMED | Verbatim, Michael Green, p.10. ASR anchor drops "hurriedly" (truncation for length), immaterial. Analogy and meaning match. |
| G-020 | CONFIRMED | Verbatim, Michael Green, p.5. "~3,500 ETFs" plus mutual/target-date funds, buybacks, insider activity — exact list match. |

---

## 3. New claims — present in the official transcript, absent from the TSV

Schema: page | paraphrase (≤2 sentences) | anchor quote (verbatim, ≤15 words) | number + his source | refuting observation. All quotes verified verbatim against `ep61_paged.txt` via grep; word counts checked ≤15.

### Passive bid — mechanism, sizing precedent, concentration

**N-01** (p.4–5). Tier1's research method: model each security's "response function" to incoming/outgoing fund flows — described as a camera taking a snapshot of the crowd (market participants in a given stock) before a liquidity "wave" (flow event) hits, so the firm can predict how that stock specifically will react.
Anchor: "built a high resolution camera that is taking a snapshot"
Number: none given (methodology description)
Refute: evidence a security's response to flows is better explained by public liquidity/float metrics than by Tier1's proprietary flow-signature database.

**N-02** (p.5). The market's capacity to arbitrage away passive's price-insensitive impulse depends on the size and direction of the active-manager community; Green singles out CTAs/managed futures as unusually important because trend-following rules make them predictable in aggregate even though no single CTA's move is knowable.
Anchor: "they are actually predictable in aggregate"
Number: none given
Refute: evidence CTA/managed-futures flows are not predictable in aggregate, or do not move with trend signals as described.

**N-03** (p.3). Green's precedent for how large a factor-based flow can become: after the 1992 Fama-French size/value paper, small-value strategies saw nearly 900 new fund launches over the next 7 years, and Dimensional Fund Advisors converted early-mover advantage into what Green estimates is worth $1.5–2 trillion in assets today from "a standing start."
Anchor: "somewhere in the neighborhood of about a trillion and a half to $2 trillion"
Number: nearly 900 funds (7-yr window from 1992); ~0.5% market-share gain for DFA; $1.5–2 trillion implied current AUM. Source: none given — his own estimate/recollection, no data cited.
Refute: Dimensional's actual reported AUM being far below $1.5–2 trillion, or independent fund-launch counts for small-value materially below ~900.

**N-04** (p.3). Second precedent: Rob Arnott's 2005 fundamental-indexing research was converted into $500 billion indexed to Research Affiliates' fundamental-index programs within 7 years.
Anchor: "within seven years there was half a trillion dollars"
Number: $500 billion within 7 years of 2005. Source: none given.
Refute: Research Affiliates/fundamental-index AUM data for that period showing a materially different figure.

**N-05** (p.3–4). The S&P 500 is roughly $70 trillion in total market cap, and Green says there is no genuine active-management competitor for the "center" of that portfolio anymore — legacy active funds (he names Fidelity Contrafund) are being slowly run off, not replaced, and nobody has made a real attempt at the S&P core in "well over a decade."
Anchor: "roughly $70 trillion in total market capitalization"
Number: ~$70 trillion S&P 500 market cap (as of taping, Sept 2026). Source: none given.
Refute: S&P 500 float-adjusted market-cap data materially different from ~$70T as of the relevant date, or evidence of new large active funds targeting the S&P core.

**N-06** (p.3–4, repeated p.8). Green cites roughly 900 academic papers now existing on the subject of passive investing, some citing him directly, some he collaborated on, some refuted and later reversed by their own authors.
Anchor: "900 academic papers related to the subject"
Number: ~900 papers. Source: none given.
Refute: a literature count materially below ~900 papers using a reasonable "related to passive" definition.

**N-07** (p.7–8). Once leveraged/thematic buying pushed semiconductor and AI-adjacent mega-caps to sufficient size, ordinary market-cap-weighted passive flows "picked them up" on their own and kept buying — meaning the concentration becomes self-sustaining. Green notes very few of the affected names gave back gains anywhere near the extent they'd realized them, which he reads as a structural (not temporary) change in S&P 500 weights.
Anchor: "structurally changed the weightings of the S&P 500"
Number: none given (qualitative "very few" gave back gains)
Refute: price data showing the affected names substantially round-tripped (gave back most gains) after the unwind rather than staying structurally elevated.

### Passive bid — demographics/retirement flows, unwind risk, dated prediction

**N-08** (p.9). Tier1 runs "full trackers" on 401k flows; Green reports these continue to show large net inflows, i.e. the payroll/retirement-driven bid into passive has not reversed as of taping.
Anchor: "they continue to be large inflows on net"
Number: none given (no rate/dollar figure, just "large")
Refute: DOL/ICI 401k flow data showing net outflows or stagnant flows over the relevant period.

**N-09** (p.13–14). In the bond-market context specifically, Green calls the passive bond investor "the Fool" (an inversion of Asimov's unmodelable "Mule") — a buyer he calls catastrophically unsophisticated because it is continuously re-funded by ordinary Americans' retirement contributions regardless of the price of what it's buying.
Anchor: "continuously funded by their retirement flows from the US population"
Number: none given
Refute: evidence retirement-plan bond allocations are price-sensitive, or are a minor (not dominant) funding source for passive bond flows.

**N-10** (p.8). **Dated prediction.** Given current efforts to extend how long people stay tied up in passive (e.g. Trump accounts), Green's model puts the passive-bid "endgame" at roughly one to two years out from the Sept-2026 taping — i.e., an implied window of roughly late 2027 to late 2028 — and he expects conditions to intensify, not calm, before it arrives.
Anchor: "my model suggests that we're still probably a year or two out"
Number: 1–2 years from Sept 2026 taping. Source: "my model" — his own (Tier1's), mechanism unspecified.
Refute: the described passive-bid dislocation failing to materialize by roughly late 2027/2028, or arriving on a materially different timetable than "gets crazier and crazier" in the interim.

**N-11** (p.8). Green analogizes the 2026 leveraged-semiconductor unwind to LTCM's 1998 blowup: after both, the prevailing narrative was "that's the end," yet markets reached new all-time highs within weeks — his point being that the passive bid's unwind risk keeps getting deferred rather than resolved.
Anchor: "new all time highs within weeks of the narrative"
Number: none given
Refute: an instance of a comparable deleveraging event followed by a sustained decline rather than a fast recovery to new highs.

**N-12** (p.9). Green declines to name a hard trigger threshold for the unwind, framing the timing as politically endogenous: with the American retirement system fused to equities, there is pressure — he draws a historical-dictator analogy for the mechanism, not as a claim about current US politics — to prevent a decline "on their watch," which becomes "a measure of national pride."
Anchor: "it becomes a measure of national pride"
Number: none given
Refute: not empirically falsifiable as stated (political/behavioral framing, not a data claim).

### Leveraged/sector ETFs and rebalancing

**N-13** (p.6). Green frames a 2026 episode — retail/thematic leveraged buying tied to an AI/semiconductor thesis he calls "the Leo Aschenbrenner experience," amplified by a new product launch ("DRAM, the ETF" concentrating in memory names) — as an exogenous shock that blew up 2x/3x leveraged semiconductor ETFs (SOXL named specifically) to unprecedented size.
Anchor: "the explosion of the 2X levered variants or 3X levered variants"
Number: none given (qualitative)
Refute: evidence SOXL/leveraged-semiconductor-ETF AUM did not reach unusual size in 2026, or that the buying was institutional rather than retail/thematic as described.

**N-14** (p.6–7). Mechanical walkthrough of leveraged-ETF "endogenous liquidity": a 3x fund that starts at $100→$300 exposure/$200 debt, after a 10% underlying rise, sits at $330 exposure on unchanged $200 debt (leverage now below 3x target), so the fund must mechanically buy an additional $60 of the underlying with zero new investor cash just to restore its stated leverage ratio.
Anchor: "you have to buy an additional 60 of the securities"
Number: illustrative worked example, not empirical. Source: his own mechanical walk-through.
Refute: evidence 3x-leveraged ETFs do not rebalance daily to a fixed target, or that such rebalancing does not measurably move the underlying's price.

**N-15** (p.7). **Distinct from the ~50% "daily price movement" figure already in the TSV (G-013).** In the subsequent unwind specifically, Green attributes roughly 50% of the overall price move to this same mechanical "product change" phenomenon, separate from ordinary discretionary/panic selling — this is a second, separate 50% estimate about a different phase of the episode.
Anchor: "50% of the overall move was caused by this phenomenon"
Number: ~50% of the unwind's overall move. Source: Tier1's models (implied, not explicitly named in this sentence).
Refute: evidence the unwind was driven predominantly by discretionary selling rather than mechanical/product-flow effects.

**N-16** (p.7). Retail behavior in SOXL-type products shifted mid-episode from the professional approach (shorting both long and short legs to harvest volatility decay) to naive dollar-cost-averaging buy-and-hold — which Green calls "a terrible strategy" given the leverage/volatility math (see N-related 150%/year breakeven, already in TSV as G-014).
Anchor: "give way to dollar cost averaging"
Number: none given
Refute: fund-flow/positioning data showing professional short-both-legs positioning stayed dominant rather than giving way to retail DCA buying.

**N-17** (p.8). The Mag 7's underperformance during this window is, per Green, a direct mechanical consequence of a spike in idiosyncratic (name-specific) realized volatility caused by the externally injected leveraged flow — not a fundamentals-driven rotation out of those names.
Anchor: "a direct result of this increase in idiosyncratic volatility"
Number: none given
Refute: evidence Mag 7 underperformance in the period correlates with earnings/guidance revisions rather than realized-volatility spikes.

### Bonds

**N-18** (p.12). Green says the bond market has crossed a "Costanza moment": the passive bid is now large enough there that the situation mirrors valuation-conscious small-cap-value managers in equities circa 2016 — people who correctly saw the market as overpriced but were structurally powerless against the mechanical bid for another decade.
Anchor: "we have crossed the Costanza moment"
Number: none given
Refute: not directly falsifiable as framed (analogy/thesis statement).

**N-19** (p.13). Because passive bond indices are built market-cap-weighted (i.e., weighted by amount of debt outstanding, not by valuation), a period of heavy low-coupon issuance followed by rate hikes causes those bonds to fall in price and be "neglected" by passive indices — which Green says is what produces the basis-trade / large levered futures positions seen in the market. This also means Fed cuts create a mechanical "bid for duration" and Fed hikes a mechanical "loss of bid," independent of fundamentals.
Anchor: "introduced a tremendous procyclicality to interest rate policy"
Number: none given
Refute: evidence Treasury basis-trade position sizes are uncorrelated with passive bond-index turnover/composition changes.

**N-20** (p.12, clarified p.14). Bond-market voices who argue the Treasury is "constrained" have themselves built up roughly a trillion dollars of synthetic short exposure via Treasury futures — confirmed by Green, when Bill asks if he means open interest, as "just the notional exposure." That exposure would need to be bought back, likely at a loss, if Bessent's buyback program succeeds.
Anchor: "issued somewhere around a trillion dollars of synthetic exposure"
Number: ~$1 trillion notional/OI in short Treasury-futures positioning (as of taping). Source: his own account, no data source cited.
Refute: CFTC Commitment-of-Traders data showing net commercial short notional in Treasury futures materially different from ~$1 trillion.

**N-21** (p.11). Pricing detail behind the buyback rationale: long-duration Treasuries issued 2020–2021 (original coupons roughly 0.5%–1.5%) are now trading at "75 cents and below" on the dollar, averaging roughly 54 cents for that vintage ("I think," his own qualifier).
Anchor: "trading in an average, I think right now of about 54 cents"
Number: ≤75 cents ceiling; ~54 cents average, both "on the dollar," for 2020–2021-vintage long bonds, as of taping. Source: none given, self-qualified as approximate ("I think").
Refute: current market pricing data for 2020–2021-issued long Treasuries showing average/ceiling prices materially different from ~54–75 cents.

**N-22** (p.11). Economics of the trade: retiring paper yielding roughly 5% all-in (of which only about 1.5 percentage points is price/capital appreciation, the rest coupon) funded by new issuance priced around 3.75% — Green's basis for calling it a "fair trade" that cuts debt face value without materially changing the interest bill.
Anchor: "issuing paper that is being issued at give or take 3.75"
Number: ~5% all-in yield retired (~1.5 pts of which = capital appreciation) vs. ~3.75% new-issue yield. Source: none given.
Refute: Treasury auction data showing new-issue yields materially above 3.75% or retired-paper all-in yields materially different from ~5% over the relevant window.

**N-23** (p.11–12). The bond market's reaction to Bessent's buyback announcement was hostile enough that Green calls it being "greeted... as a heinous financial crime" — which he uses to argue Treasury and bond traders are structurally adversaries (fighting over the rate the government pays), not allies, contrary to a common assumption.
Anchor: "greeted by the bond markets as a heinous financial crime"
Number: none given
Refute: not a quantifiable claim — characterization of market reaction/rhetoric.

### Fed, Treasury and liquidity (beyond buybacks)

**N-24** (p.15). A second Treasury lever Green says is available but not yet used: a swap with large banks to move underwater held-to-maturity securities off their balance sheets, relieving what he calls a "balance sheet recession" inside the banking system and freeing lending capacity into housing/autos/construction. He states plainly he sees no sign Bessent is heading that way.
Anchor: "no indication that's the direction he's heading yet"
Number: none given
Refute: trivially falsified if such a swap is later announced; until then, not testable.

**N-25** (p.15). If Fed chair candidate Warsh cuts rates, that creates conditions for a levered carry trade (borrow short, buy long duration) to become newly attractive — meaning the same trade Bessent is executing at the Treasury would then be replicated broadly by private leveraged investors once it clears their risk/return hurdle.
Anchor: "will be done by every levered investor out there"
Number: none given
Refute: absence of a pickup in leveraged duration-carry positioning following a rate cut, if one occurs.

**N-26** (p.15). Using new housing starts per capita as his indicator, Green characterizes the rate-sensitive part of the US economy as being in "full-blown depression" — i.e., current rates are too high for housing/autos/construction specifically, even if headline economic data look fine.
Anchor: "it is full-blown depression out there"
Number: none given — no housing-starts-per-capita figure or comparison period is actually supplied, only the qualitative label. Denominator (per capita, which population base, which vintage of starts data) is unstated.
Refute: Census Bureau new-housing-starts-per-capita data showing levels in line with historical norms rather than depression-era lows.

**N-27** (p.15). Conditional forecast: a rate cut would be "modestly inflationary" for real estate/autos, but Green expects currently-elevated short-term/transitory inflation drivers to be retreating over the same period, so his net call is that a cut "would not prove to be meaningfully inflationary overall."
Anchor: "would not prove to be meaningfully inflationary overall"
Number: none given — no percentage or timeframe attached, purely directional.
Refute: CPI/PCE prints after a Fed cut showing meaningfully accelerating inflation rather than a wash.

### Valuations / AI narrative (only tangentially covered — see gap note below)

**N-28** (p.10). Green questions whether single-day mega-cap market-cap gains like Microsoft or NVIDIA rising "$400 billion" are plausibly justified by ordinary earnings/guidance news, arguing the implied cash-flow assumptions would need to be extraordinary — his point being that mechanical/flow-based explanations fit the size of such moves better than fundamentals-based narratives.
Anchor: "rose by $400 billion in market capitalization"
Number: $400 billion, illustrative (no specific date/ticker-day named). Source: none given.
Refute: an event study tying a specific $400bn Microsoft/NVIDIA cap move cleanly to a proportionate, cash-flow-justified news item.

**N-29** (p.10–11). Green is skeptical of "expectations-based investing" that justifies today's valuations by defining AI's total addressable market as "all of human knowledge" — his stated preference is to "diagnose the mechanical properties of the system" (flow-based explanation) rather than adjudicate whether the AI cash-flow narrative is true or false.
Anchor: "diagnose the mechanical properties of the system"
Number: none given
Refute: not a testable empirical claim as stated — a methodological/epistemic preference.

### Explicit scope gap vs. the brief

**N-30** (p.17, plus absence elsewhere). At the close, Bill Fleckenstein states outright: "We didn't even get to talk to you about AI. We'll have to save …" and Green jokes "by the time we get there, our robot overlords will do it for us." I confirmed by full-text search that the transcript contains **no** occurrences of "IPO," "private market," "private equity," "data center," "capex," "hyperscaler," "single-stock," "single stock," "creation," "redemption," or "authorized participant." **AI build-out funding, IPOs, and private markets are not substantively addressed in this episode at all (beyond the tangential N-28/N-29 valuation-skepticism remarks and the semiconductor/SOXL episode, which is about a leveraged-ETF product, not AI capex financing). ETF creation/redemption mechanics (the technical AP/in-kind-basket process) and single-stock ETFs specifically are likewise never named** — the closest adjacent content is the general fund-flow/"liquidity concentration" framing and the SOXL leverage-rebalancing mechanics (a sector-leveraged ETF, not a single-stock one). This directly contradicts the brief's assumption that these are topics to extract claims on; flagging per the instruction to say so explicitly rather than force-fitting claims that aren't there.

One more direct contradiction-of-assumption to flag: Bill Fleckenstein's question on p.9 — "you never really talked about what the end game of it looks like when …" — is **Bill's own recollection/paraphrase of Green's past claims**, not a number Green restates or confirms in this transcript. Green's actual answer pivots straight to the Tickle Me Elmo analogy without repeating "55, 60%." I have not treated "55, 60%" as a Green claim in this episode; it's Fleckenstein's framing only.

---

## 4. Numbers table

State of denominator/basis given in the "measures" column; "as-of" is the point in time the number is claimed to hold, per Green's own words (not independently confirmed — no web access was used).

| number | measures | as-of | his source | page |
|---|---|---|---|---|
| ~$70 trillion | S&P 500 total market capitalization | at taping (Sept 2026), implied "today" | none given | 3–4 |
| nearly 900 | small-value funds launched in the 7 years after the 1992 Fama-French paper | 1992–~1999 window | none given | 3 |
| ~0.5% | Dimensional Fund Advisors' market-share gain attributable to the Fama-French/small-value trade | unspecified historical accumulation, "today" | none given | 3 |
| $1.5–2 trillion | implied current AUM value of that 0.5% share gain | today (Sept 2026), his estimate | his own estimate, no data cited | 3 |
| $500 billion | assets indexed to Research Affiliates' fundamental-indexing programs | ~2012 (7 yrs after Arnott's 2005 paper) | none given | 3 |
| ~900 | academic papers "related to the subject of passive" | today (Sept 2026) | none given | 3–4, 8 |
| ~1 terabyte | size of Tier1 Alpha's proprietary flow database, fully compressed | today | Tier1 Alpha (his own firm) | 5 |
| ~3,500 | ETFs tracked in Tier1's database (plus mutual/target-date funds, buybacks, insider activity) | today | Tier1 Alpha | 5 |
| ~$3 billion/day | peak single-security inflow into Micron during the 2026 leveraged-semiconductor melt-up | melt-up peak, date unspecified | Tier1's flow-tracking database/models | 7 |
| ~$300 million/day | baseline aggregate passive bid for the largest S&P companies | general/current, unspecified date | Tier1's models | 7 |
| ~50% | share of daily price movement (melt-up phase) attributed to mechanical leveraged-ETF flow | melt-up period | Tier1's models | 7 |
| ~150%/year | required SOX index return for a 3x SOXL-type product to break even, given realized volatility | melt-up-period volatility | his own calculation | 7 |
| ~50% | share of the *unwind's* overall move attributed to mechanical "product change" (distinct from the melt-up-phase 50% above) | unwind period | Tier1's models (implied) | 7 |
| $400 billion | illustrative single-day/single-event market-cap gain example (Microsoft or NVIDIA) | illustrative, no specific date given | none given | 10 |
| $2bn/month → $4bn/month | US Treasury debt-buyback program size, before/after Bessent's announced increase | as announced, 2026 | his own account of the (unnamed) Treasury announcement | 11 |
| ≤75 cents | trading price "on the dollar" ceiling for 2020–2021-vintage off-the-run long Treasuries | today (Sept 2026) | none given | 11 |
| ~54 cents | average trading price "on the dollar" for that same 2020–2021 vintage | "right now," self-qualified "I think" | none given | 11 |
| ~5% | approximate all-in yield of the paper being retired (coupon + price return combined) | at issuance / current, unspecified | none given | 11 |
| ~1.5 points | of that ~5%, the portion attributable to capital appreciation rather than coupon | same as above | none given | 11 |
| ~3.75% | approximate yield on new bills issued to fund the buyback | current, unspecified date | none given | 11 |
| ~$1 trillion | notional/open-interest short Treasury-futures exposure ("synthetic supply") held by bond-market participants betting the Treasury is constrained | today (Sept 2026) | his own account, no data source cited | 12, 14 |
| 25–35% | share of incremental bond-market flow now coming through price-insensitive passive vehicles | today/current | Tier1's own flow-tracking work | 13 |
| 1–2 years | Green's forecast horizon for the passive-bid "endgame" to arrive, from the Sept 2026 taping | forecast made Sept 2026 | "my model" (Tier1, mechanism unspecified) | 8 |

---

## Summary of method

- PDF → text via `pdftotext -layout` (20 pages, clean conversion; only cosmetic "Invalid Font Weight" warnings, no content loss).
- Page-split with a Python one-liner on form-feed characters; verified the resulting page numbers match the PDF's own printed footer numbers (spot-checked pp. 2, 17, 18).
- Every anchor quote above (TSV reconciliation and new claims alike) was located with `grep -n` against the page-split text and confirmed to fall inside the correct speaker's turn by checking the nearest preceding "Name (mm:ss):" tag — not eyeballed from a single read-through.
- No web access used; no independent verification of any number Green states — only transcript-to-transcript reconciliation, as scoped.
