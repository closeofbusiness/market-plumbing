# Who buys US Treasuries now — four downloaded sources set against Green (11 Sep 2026)

**Status: CLAIMS, not data** — except where a row cites a project series, which is data. Serves channels
(a), (c), (d) and (e); the term premium feeds the discount rate in every P attribution.

**Sources.** Martin's downloads of the last two weeks, triaged: Japan Macro Advisors, "Yen Repatriation
Starts with the Whale" (10 Sep 2026, GPIF); Grant Williams podcast Ep 129 (Marvin Barth, 13 Aug), Ep 131
(Andrew McDermott, 21 Aug) and "Shifts Happen" Ep 13 (Luke Gromen, 5 Aug). Excluded after a scan: Kaos
Theory Ep 13 (Michael Every, geopolitics) and Ep 14 (Lakshmi Sreekumar, oil; one passing Treasury remark).
Set against Green's four bond posts (2, 16, 19, 23 Aug) and his Ep 61 bond claims. Paid material: paraphrase,
quotes of 15 words or fewer. Cards: `_research/2026-09-11-Treasury-Japan-Cards/`. Text below is the
synthesis agent's (Sonnet), unedited apart from HTML entities.

**Supervisor verification (11 Sep).** Re-read in the source texts: the JMA weights (25% today, a rule-implied
50%) and its ¥32trn (at 35%) to ¥80trn (at 50%) range; Gromen naming Cayman Islands hedge funds as the buyers;
McDermott's "rent balance sheet" framing. The four project series the synthesis cites match
`data/series.tsv` exactly (`fed_treasury_purchases_flow_bn` +156bn in 2026Q1 after -741/-515/-83bn in
2023-25; `hf_long/short_treasury_exposure_bn` 2,348/1,567bn at 2026-03-31; `tic_mfh_cayman_ust_bn` 453.1bn
Jun 2026; `barth_cayman_hf_ust_trn` 1.85trn end-2024).

**Read with these caveats (supervisor):**
- The strongest finding is the project's own: the Fed turned net Treasury buyer in 2026Q1 (Z.1). None of
  the outside sources notices it. Whether that is bills only (RMPs) needs the H.4.1 split — item A1.
- `barth_cayman_hf_ust_trn` is Daniel Barth et al. (Fed staff, FEDS Note), NOT Marvin Barth (Ep 129).
- European pension funds: no source here covers them (Martin expected some). Now scouting item E1.

---

# US Treasury Demand and the Term Premium — Synthesis

Source legend used throughout: **[JMA]** = Japan Macro Advisors, "Yen Repatriation Starts with the Whale," 2026‑09‑10. **[Barth]** = Grant Williams Podcast Ep.129 w/ Marvin Barth, 2026‑08‑13. **[McDermott]** = Grant Williams Podcast Ep.131 w/ Andrew McDermott, 2026‑08‑21. **[Gromen]** = "Shifts Happen" Ep.013 w/ Luke Gromen, 2026‑08‑05. **[Green 8/2]**, **[Green 8/16]**, **[Green 8/19]**, **[Green 8/23]** = Michael Green Substack essays by date. **[Green Ep61]** = "The End Game" #61 official-transcript reconciliation, taped ~2026‑09‑07/08.

## 0. Sources

Read in full: the JMA note and Barth transcript [D/cards_jma_barth.md]; the McDermott and Gromen transcripts [D/cards_mcdermott_shifts.md]. From the two Green Substack-card files (11 cards total), used only the four in scope of this brief — "Maid in Japan" (8/2), "Anchors Aweigh, My Boys" (8/16), "Sometimes, You Get What You Need" (8/19), "Great, Scott..." (8/23) — and excluded the other seven (equity-passive-flow essay, a content-free video notice, a semiconductor-ETF essay, a firm-launch announcement, a hacked-account notice, an inflation-distribution essay, an AI/fraud essay), none of which bear on Treasury demand or the term premium. From the Ep61 reconciliation, used only the bond-market claims (buybacks, synthetic shorts, passive bond flows, the unused bank-HTM-swap lever), excluding its equity/semiconductor/AI/housing content. Grepped P/data/series.tsv for existing series. Not read, per the brief's own upstream triage: Kaos Theory Ep.13 (Michael Every) and Ep.14 (Lakshmi Sreekumar) — I did not independently verify that exclusion.

## 1. Holder by holder

**Foreign official (China; Japan MoF).** Green cites TIC data: aggregate foreign official UST holdings down $233bn from the Feb-2026 peak, Japan's official holdings down $123bn from an all-time high of $1.239trn, China down a further $61bn, all Feb–June 2026, while foreign *private* holdings rose $43bn over the same window [Green 8/23]. A separate Green essay puts Japan's holdings at ~$1.1trn (largest of any foreign holder) and reports a $66.7bn May-2026 decline, the largest since 2022 (~$60bn bills, ~$7bn bonds) [Green 8/2] — the two essays don't reconcile their monthly path against each other. Gromen asserts flatly that China has stopped buying, and that Japan, Germany, Korea and the UK are now borrowing for defense rather than recycling surpluses into Treasuries [Gromen]. McDermott and Barth push back in emphasis, not fact: McDermott calls the "Japan will dump Treasuries" narrative real but incomplete [McDermott]; Barth argues the US retains a durable "foreign bid" and that a Japan-driven shock hits France/Spain first [Barth]. No source gives a currently-dated figure for Japan MoF's reserve holdings specifically, as distinct from Japan's mixed aggregate TIC total.

**Japanese public pensions (GPIF + sister funds).** JMA's entire subject (detailed in §3); no other source names GPIF as a current actor — Gromen and Grant Williams raise GPIF repatriation only as an explicit future hypothetical, not a present claim [Gromen]. McDermott only relays Grant Williams' unquantified concern about pension unrealized losses, which McDermott himself redirects to banks and mortgage borrowers [McDermott].

**Japanese life insurers.** Carried entirely by Green: insurers are one of two return-insensitive buyers stepping back (with central banks), because domestic JGB yields now clear yen liabilities without hedging cost, not because hedging got costlier [Green 8/2]. His numbers: "roughly half" of Japan's ten largest life insurers reportedly cutting foreign-bond holdings (no primary source named), and a ¥1.35trn JGB-holdings cut dated "three months through March 2025" — about a year earlier than the rest of the piece's 2026 narrative, a dating inconsistency flagged in the source itself. JMA explicitly states no life insurer is mentioned in its note; McDermott names only Tokio Marine, and only via Buffett's equity stake, with no bond claim. This entire holder category is thus uncorroborated within this note set.

**European pension funds.** No source covers this at all — see §8.

**US pensions and insurers.** Carried entirely by Green [Green 8/16], who surveys three pools as candidates to replace Japan's exiting bid and finds none available: corporate pensions de-risked into bonds in 2022–23 and are largely done; public pensions (~$6trn vs. ~$3trn corporate) discount liabilities at ~6.8% rather than market yields, so higher rates create no rebalancing incentive, and are additionally locked into illiquid private assets; the insurance/reinsurance complex is increasingly PE-owned, funds annuities with private credit, and cedes risk offshore (~$1.5trn affiliated reinsurance exposure vs. $657bn total US life-insurance surplus, per analyst Nick Nemeth). JMA explicitly notes the US is not discussed as a pension/insurer market; Barth, McDermott and Gromen are silent.

**Banks.** Near-total gap. Green's Ep61 remarks note an unused Treasury lever — a swap to move underwater held-to-maturity securities off bank balance sheets — with "no indication" Bessent is pursuing it [Green Ep61, N‑24]. McDermott discusses *Japanese* banks' rate-normalization stress (citing Zentoshin's bankruptcy), not US banks as UST buyers [McDermott]. No source quantifies bank UST holdings or HQLA-driven demand.

**Money-market funds and bills.** A total gap. Gromen's card states explicitly that money-market funds are never mentioned as Treasury buyers [Gromen]; JMA, Barth, McDermott and the in-scope Green essays are likewise silent. This is despite the project's own series.tsv holding substantial MMF/bill data (below) — none of the five documents engages it.

**Hedge funds and the basis trade.** Gromen names leveraged, Cayman-domiciled basis-trade funds as *the* marginal Treasury buyer, prone to "degrossing" when volatility rises [Gromen]. Green offers parallel, more granular data: asset managers net long ~2.59mn vs. leveraged funds net short ~2.23mn 10-year note futures contracts (CFTC TFF, week of 8/18/26); ~$830bn cash-futures basis and ~$375bn steepener positions (Fed's June-2026 decomposition of Sept-2025 Form PF data); ~$1trn notional short Treasury-futures exposure that would need buying back if the buyback succeeds [Green 8/23; Green Ep61 N‑20]. The project's own series independently track a related but distinct cut of the same actor: `hf_long_treasury_exposure_bn` ($2,348bn) and `hf_short_treasury_exposure_bn` ($1,567bn), both OFR Form PF at 2026‑03‑31, plus `tic_mfh_cayman_ust_bn` ($453.1bn, Jun 2026) and `barth_cayman_hf_ust_trn` ($1.85trn, end‑2024, Fed FEDS Note) — **note this "Barth" is a Federal Reserve staff economist, not Marvin Barth of Thematic Markets who appears elsewhere in this synthesis; the shared surname is coincidental and a citation trap.**

**Passive bond funds.** Central to Green: market-value-weighted index funds mechanically under-buy exactly the cheapest, highest-duration bonds, since a bond's index weight shrinks as its price falls [Green 8/16]; mutual funds hold ~$1.7trn of Treasuries (5–6% of marketable debt, Fed Z.1), ETFs added an estimated $90–125bn of exposure in 2025, and passive demand covers roughly a quarter to a third of net coupon issuance [Green 8/23; Green Ep61 G‑016]. Gromen's transcript, by contrast, never mentions passive or money-market funds as UST buyers at all [Gromen] — his own answer to "who's left" is leverage alone, not passive flows. Green's Ep61 remarks explicitly link the two mechanisms (passive indices "neglect" beaten-down bonds, which is what the leveraged futures position fills) [Green Ep61, N‑19], so this is a difference in emphasis rather than a flat contradiction — but a reader of Gromen alone would not know passive flows play any role.

**The Fed (bills-only, reserve-management purchases).** Green: the Fed ended runoff 12/1/25 and grows its balance sheet only via bills, at a pace falling from $40bn/month to $10bn/month by Aug 2026 [Green 8/16]; Barth independently corroborates from the issuance side, stating Treasury itself has been "skewing more and more…to the front end" [Barth]. Gromen sits in tension with a strict bills-only reading: he describes Fed/Treasury swap lines to Japan as "a weak form of yield curve control" and floats a full long-end backstop if Japan sold aggressively [Gromen]. **None of the five sources reports what the project's own data shows**: `fed_treasury_purchases_flow_bn` (Fed Z.1 flow) has the Fed swinging from net Treasury *seller* (–$741bn 2023, –$515bn 2024, –$83bn 2025) to net *buyer* of +$156bn in 2026 Q1 alone — the project's own note calls this the largest single Treasury buyer at the margin that quarter. This doesn't necessarily contradict "bills-only" in composition (Z.1 doesn't split bills vs. coupons in that series), but it does contradict any implication that the Fed's net footprint is small or shrinking.

**Treasury buybacks.** Exclusively a Green thread. Buyback size doubling from ~$2bn to ≥$4bn per operation starting 9/9/26 [Green 8/23; Green Ep61 G‑015]; economics of retiring ~5% all-in paper (≈1.5pp of which is capital appreciation) with ~3.75%-yielding new issuance [Green Ep61, N‑22]; market reaction was hostile — "greeted by the bond markets as a heinous financial crime" [Green Ep61, N‑23] — which Green reads as evidence Treasury and bond traders are structural adversaries, not allies. JMA, Barth, McDermott and Gromen do not mention the buyback program.

## 2. The term premium — driver by source

**Barth**: central-bank *credibility*, not the policy rate — hawkish June-2026 FOMC read as lowering long yields, "capitulating" July-2026 FOMC read as raising them; preferred proxy is far-forward less medium-forward rates; "you are always going to have this foreign bid" for the US specifically [Barth]. **Green**: *buyer composition/scarcity* — the term premium is the price the marginal buyer charges to absorb the residual after Japan, the Fed, and passive formulas have done their part; evidence is the Kim-Wright 10yr term premium (FRED THREEFYTP10) rising ~32bp (≈0.52%→0.82–0.85%, mid-Feb–mid-Aug 2026) while 5y5y forward inflation (FRED T5YIFR) stayed in a ~20bp band (~2.13–2.34%) — a real-rate, not inflation, move [Green 8/23]. Green explicitly declines to fully choose among three rivals (post-QE normalization, fiscal sustainability, buyer-transition scarcity), saying "most likely it is some of all three." **Gromen**: *fiscal dominance* — his own "true interest expense" (interest + entitlements) nearing 95% of federal receipts, with a 2% real-10yr-yield historical trigger (cited to Calomiris, Fed 2023) [Gromen]. **JMA and McDermott never use the term "term premium"** — JMA's nearest analogue is GPIF's own real-return-vs-wage-growth optimizer, a distinct portfolio-allocation framework. All three named mechanisms are complementary rather than mutually exclusive in the notes, but none of the sources attempts to adjudicate between them.

## 3. GPIF — the JMA case in detail

Current target: 25% each of domestic bonds/equity, foreign equity/bonds (of total AUM, since 2020), down from 35% (2014) and 62% actual (end FY2012). JMA's author, replicating GPIF's own stated allocation rule at the current ~3% 10yr JGB yield, calculates the rule now implies ~50% domestic bonds. GPIF may already move within its existing ±6-point band (up to 31%) without a formal announcement, based on the 2014 precedent of moving first and disclosing after. Scale: ¥32trn of net domestic-bond buying if the target reaches 35%, ¥80trn if it reaches 50% (static, current-AUM estimates, excluding future fund growth). What funds it: foreign bonds, of which >50% are USD-denominated — the note connects this directly to US Treasuries, projecting Bessent would object to a public announcement of reduced GPIF UST purchases (paraphrased; not GPIF's own statement). Three sister funds run the identical 25/25/25/25 model — Pension Fund Association for Local Government Officials (¥35.5trn), the Federation of National Public Service Personnel Mutual Aid Associations (¥11.5trn), and the Promotion and Mutual Aid Corporation for Private Schools of Japan (¥4.9trn) — ¥87trn combined with legacy reserves on top of GPIF itself. The confirming/refuting report is GPIF's next quarterly disclosure, expected early November 2026. The ~50% figure is the author's own reconstruction of GPIF's rule, not a GPIF-published target — a checker should weight it accordingly.

## 4. Numbers

| Value | Measures | As‑of | Stated source | Doc (date) | Project series_key / primary source to check |
|---|---|---|---|---|---|
| $1.239trn (peak); –$123bn | Japan official UST holdings, level & decline | Feb–Jun 2026 | TIC | Green 8/23 | none found → TIC Table 5 |
| –$233bn | Foreign official UST holdings, decline | Feb–Jun 2026 | TIC | Green 8/23 | none found → TIC Table 5 |
| –$61bn | China official UST holdings, further decline | Feb–Jun 2026 | TIC | Green 8/23 | none found → TIC Table 5 |
| +$43bn | Foreign private UST holdings, increase | Feb–Jun 2026 | TIC | Green 8/23 | none found → TIC Table 5 |
| ~$1.1trn | Japan UST holdings, largest foreign holder | Aug 2026 | Treasury data (implied) | Green 8/2 | none found → TIC Table 5 |
| –$66.7bn (~$60bn bills+~$7bn bonds) | Japan UST holdings, monthly decline | May 2026 | presumably TIC | Green 8/2 | none found → TIC Table 5 |
| 25% (of AUM) | GPIF current domestic-bond target | since 2020 | GPIF disclosure | JMA | none found → GPIF quarterly/annual report |
| ~50% (of AUM) | GPIF implied domestic-bond weight | Sept 2026 | author's own model | JMA | none found → GPIF quarterly report (the actual test) |
| ¥32trn / ¥80trn | GPIF implied net domestic-bond buying at 35%/50% targets | static, current AUM | author's own calc | JMA | none found → GPIF quarterly report |
| >50% | GPIF foreign-bond book, USD share | current | none given | JMA | none found → GPIF asset-composition disclosure |
| ~3% (from ~0.9%) | 10yr JGB yield | Sept 2026 (vs. end-Sept-2024) | none given | JMA | none found → Japan MoF/BOJ JGB data |
| 0.52%→0.82‑0.85% (~32bp) | US 10yr Kim-Wright term premium | mid-Feb–mid-Aug 2026 | FRED THREEFYTP10 | Green 8/23 | none found → FRED THREEFYTP10 |
| ~2.13–2.34% | 5y5y forward inflation compensation | 2026 YTD–Aug 21 | FRED T5YIFR | Green 8/23 | none found → FRED T5YIFR |
| $40bn/mo→$10bn/mo | Fed Treasury-bill purchase pace | Dec 2025–Aug 2026 | his own, citing Fed ops | Green 8/16 | related: `fed_soma_tbills_bn`, `fed_bill_absorption_ratio_matched` (not identical metric) → Fed H.4.1/SOMA |
| –$741bn/–$515bn/–$83bn/+$156bn | Fed net Treasury purchases by year (2023–2026Q1) | through 2026Q1 | Fed Z.1 | not in read sources — project data | `fed_treasury_purchases_flow_bn` → Fed Z.1 |
| $2bn→≥$4bn/operation | Treasury buyback size | from 2026‑09‑09 | Treasury announcement/CNBC | Green 8/23; Ep61 | none found → Treasury buyback schedule, TreasuryDirect |
| 2.39x cover, 66.8% indirect, 5.216% | Aug‑13‑2026 30yr auction demand | 2026‑08‑13 | TreasuryDirect | Green 8/23 | none found → TreasuryDirect auction results |
| $1.504trn→$1.675trn (5–6% of debt) | Mutual-fund UST holdings, level & growth | Q4 2024–Q4 2025 | Fed Z.1 via FRED | Green 8/23 | none found → Fed Z.1 (FRED) |
| $90–125bn | ETF Treasury-exposure added | 2025 | etf.com/TD Sec./BlackRock 10-K | Green 8/23 | none found → ICI/etf.com flow data |
| ~25% (up to 25–35%) | Passive share of net coupon issuance | 2025–2026 | his own estimate | Green 8/23; Ep61 G‑016 | none found → bespoke build from Fed Z.1 + ICI |
| +2.59mn / –2.23mn contracts | 10yr note futures, asset managers vs. leveraged funds | week of 2026‑08‑18 | CFTC TFF | Green 8/23 | none found (project's Form PF series is a different universe) → CFTC Traders in Financial Futures |
| ~$830bn + ~$375bn | Basis-trade + steepener hedge-fund positions | Fed's Jun‑2026 decomposition of Sept‑2025 Form PF | Federal Reserve | Green 8/23 | related: `hf_long_treasury_exposure_bn` $2,348bn, `hf_short_treasury_exposure_bn` $1,567bn (2026‑03‑31, different vintage) → OFR Hedge Fund Monitor |
| $1.85trn (+$1trn since 2022) | Cayman-domiciled hedge fund UST holdings | end‑2024 | Fed FEDS Note | not in read sources — project data | `barth_cayman_hf_ust_trn` (Fed staff "Barth," distinct from Marvin Barth) → Fed FEDS Note 2025‑10‑15 |
| ~$1trn notional/OI | Synthetic short Treasury-futures exposure | Sept 2026 taping | his own account, no data source | Green Ep61 N‑20 | none found → CFTC Commitment of Traders |
| ≤75¢ ceiling / ~54¢ avg | 2020–21-vintage long Treasury prices | Sept 2026 | none given, self-qualified | Green Ep61 N‑21 | none found → current market bond pricing |

## 5. Predictions

| Date made | Prediction | Horizon | Conditions | Source | Check date |
|---|---|---|---|---|---|
| 2026‑09‑10 | GPIF raises domestic-bond target (or already has) | Sept 2026 quarter | none beyond the real-return case | JMA | ~early Nov 2026 report |
| 2026‑09‑10 | GPIF moves inside ±6pt band pre-announcement | near-term | 2014 precedent | JMA | early Nov 2026 report |
| 2026‑09‑10 | Shift scale ¥32trn or ¥80trn | undated | depends on GPIF's new target | JMA | whenever board resets target |
| 2026‑08‑13 | Term premium rises toward ≥1990s norms | ongoing | fiscal deterioration + non-credibility, "not just the US" | Barth | ongoing; THREEFYTP10 |
| 2026‑08‑13 | US funding crisis not imminent | "not particularly soon" | no alternative capital destination | Barth | open-ended |
| 2026‑08‑13 | Sovereign shock hits France/Spain before US | unspecified | Japan "repressing savings" | Barth | French/Spanish spreads |
| 2026‑08‑21 | Bessent's manufacturing-shift strategy succeeds or fails | ~10yr (~2036) | McDermott's own falsification test | McDermott | ~2036 |
| 2026‑08‑05 | Too-strong yen (142–153 JPY/USD) triggers mirror-image crisis | contingent | Gromen: "I don't know" the level | Gromen | USD/JPY approach |
| 2026‑08‑05 | Gold's reaction tests policy adequacy | immediate | absent a rally, "more" needed | Gromen | ongoing, gold price |
| 2026‑08‑02 | Companion essay on "who buys" as Japan/central banks retreat | "in two weeks" | none | Green 8/2 | fulfilled by Green 8/16 |
| 2026‑08‑02 | 5 falsifiable Japan-transmission tests; reversal in JGB foreign buying "kills" thesis | within quarters | as listed | Green 8/2 | ongoing |
| 2026‑08‑16 | Breakevens joining the move revives inflation-fear story; staying quiet favors term-premium story | ongoing | future breakeven/swap moves | Green 8/16 | ongoing; T5YIFR |
| 2026‑08‑16 | Long bonds do NOT rally on a Fed hike | next FOMC(s) | Fed actually hikes | Green 8/16 | after next hike, if any |
| 2026‑08‑19 | Fed cuts at "the next meeting," producing bull steepener | next FOMC | needed to continue the "turn" | Green 8/19 | next FOMC decision |
| 2026‑08‑23 | Warsh's Jackson Hole keynote | 2026‑08‑28 | scheduled | Green 8/23 | 2026‑08‑28 (past; verify outcome) |
| 2026‑08‑23 | Expanded buyback begins | 2026‑09‑09 | per Treasury announcement | Green 8/23 | 2026‑09‑09 (imminent; verify) |
| 2026‑08‑23 | 5-part falsification bundle (steepening, contained inflation forward, buyback-eligible outperformance, fewer large moves, no repo stress) | after 8/28–9/9 | Fed cuts + Treasury follows through | Green 8/23 | shortly after 2026‑09‑09 |
| ~2026‑09‑07/08 | Rate cut replicates carry trade across "every levered investor" | unspecified | contingent on a cut | Green Ep61 N‑25 | after next cut, via Form PF/CFTC TFF |

## 6. Contradictions

**Between sources.** Marginal buyer: Gromen names leveraged Cayman basis-trade funds and never mentions passive flows [Gromen]; Green treats passive index funds and leveraged basis funds as linked, not rival, mechanisms [Green Ep61 N‑19] — divergent emphasis, not a clean contradiction. "No buyer left" vs. persistent bid: Barth's "you are always going to have this foreign bid" for the US [Barth] sits against Green's finding that no named US domestic pool can replace Japan's exit [Green 8/16] — but these are different claims (aggregate foreign demand vs. specific domestic pools), not directly opposed. Dumping vs. renting: McDermott frames the August 2026 intervention as the US choosing to "rent balance sheet" rather than Japan selling [McDermott], while Gromen (recorded 16 days earlier, before that intervention) discusses a Japanese Treasury sale as a live future possibility [Gromen] — the sequencing (Gromen pre-, McDermott post-intervention) matters for reading this as evolution rather than disagreement. Fed posture: Green's bills-only, shrinking-pace Fed [Green 8/16] and Gromen's swap-line/full-backstop Fed [Gromen] are in tension on their own terms; both sit awkwardly against the project's own Z.1 series showing the Fed as the largest net Treasury buyer in 2026 Q1 (§1).

**Inside sources.** JMA's title calls the GPIF move "repatriation"; its own conclusion calls it "rebalancing, rather than a repatriation" — not the same claim, since repatriation implies capital physically returning while rebalancing does not [JMA]. Gromen states US debt-to-GDP as 132%, then 111%, then "still at 120%" within two consecutive sentences, unreconciled in the transcript [Gromen]. Green's ¥1.35trn Japanese-insurer JGB-cut figure is dated a year earlier than the rest of "Maid in Japan"'s narrative [Green 8/2]. Green's own three rival term-premium explanations are explicitly left unresolved — "most likely it is some of all three" [Green 8/23].

## 7. Implications for the project's channels (hypotheses, not conclusions)

**(a) Direct money creation.** Test whether the Fed's stated bills-only, decelerating reserve-management purchases [Green 8/16] and the much larger net-purchase swing in the project's own Z.1 series (§1) describe the same phenomenon at different resolutions, or genuinely different things (bills vs. total Treasury flow), and whether Treasury's own bill-heavy issuance [Barth] plus the September buyback materially reshapes maturity supply investors face.

**(c) Collateral, leverage, basis trades.** Test whether a Cayman-domiciled leveraged basis-trade complex [Gromen; Green 8/23] is growing fast enough, relative to departing official demand, to be *the* marginal buyer rather than *a* marginal buyer — using CFTC TFF, OFR Form PF (`hf_long_treasury_exposure_bn`/`hf_short_treasury_exposure_bn`), and the Cayman-specific series already in the project (`tic_mfh_cayman_ust_bn`, `barth_cayman_hf_ust_trn`) — and whether this financing structure is as fragile to volatility spikes as Gromen's "degrossing" claim implies.

**(d) Market structure and flows.** Test whether GPIF/sister-fund rebalancing [JMA], Japanese insurer non-reinvestment [Green 8/2], and mechanical market-value-weighted 401(k)/mutual-fund/ETF buying [Green 8/16, 8/23] jointly explain the observed term-premium rise better than they do individually — this is the channel where sources most directly disagree on which flow dominates (§6), so any test should be designed to distinguish passive-flow and leveraged-flow contributions rather than assume one.

**(e) Fundamentals incl. rates and term premia.** Test the three offered mechanisms — credibility [Barth], buyer-composition/scarcity [Green], fiscal-dominance threshold [Gromen] — against each other going forward using THREEFYTP10/T5YIFR (Green's proxy), Barth's own far-forward-less-medium-forward measure (not a named public series in these notes), and Gromen's proprietary interest-expense/receipts ratio (also not a named public series), noting Green's own data rules out a pure inflation-expectations story as currently configured without adjudicating between the other two.

## 8. The European-pension gap

No source in this set — JMA, Barth, McDermott, Gromen, or the four in-scope Green essays — discusses European pension funds' Treasury or bond-buying behavior; JMA explicitly flags Europe as unmentioned. Free primary sources that would address this, named as suggestions only (not retrieved): DNB (De Nederlandsche Bank) quarterly pension-fund investment statistics and the Dutch pension-system transition schedule (Wet toekomst pensioenen), given the Dutch system's size and its ongoing DB-to-DC shift's effect on long-duration hedging demand; EIOPA's IORP (pension fund) statistics; the ECB Statistical Data Warehouse's insurance-corporation/pension-fund balance-sheet series (by issuer residence and currency); and, for the UK, The Pensions Regulator and ONS series MQ5 on insurance/pension/trust investment, given LDI's known sensitivity to long-rate moves.
