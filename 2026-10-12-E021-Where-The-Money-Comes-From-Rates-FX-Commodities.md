# Where the money comes from in rates, FX and commodities — a first measurement map (E-021)

*12 October 2026. First pass, asked for by the principal (THE_ASK E-021: "same principle, where is the money coming from. Is money
flowing in or out? What can we measure? how can we measure change? What is research on the topic saying"). Two independent lanes
ran on each market: an in-house Sonnet agent, and Gemini (`gemini-3.1-pro-high` through agy) as an additional online-research
lane. The in-house returns are kept verbatim in `_research/2026-10-12-E021-{rates,fx,commodities}-inhouse-return.md`. Gemini's
returns and the citation check are in `_research/2026-10-12-E021-gemini-returns.json`. Grades follow the charter (E-007):
MEASURED, BOUNDED, HYPOTHESIS. Nothing here has had outside review yet.*

**Verified by the supervisor, one load-bearing number per market, re-fetched or re-summed at source:**
- **Rates:** the Z.1 absorption split below.
- **FX:** TIC July net purchases of $40.6bn (holdings $38.82trn), and Japan's Q2 intervention of ¥11.73trn.
- **Commodities:** COMEX gold managed-money net long, 110,987 contracts on 6 Oct.

---

## The answers in one paragraph each

**Rates — money is still flowing in, but the buyer has changed.** US net Treasury issuance rose from $1,615bn (2024Q3–2025Q2) to
$2,360bn (2025Q3–2026Q2). The rest of the world's share fell from $709bn (44%) to $294bn (12%). Money-market funds took $668bn
(28%, from $164bn), and the Fed went from −$266bn to +$264bn as it began buying bills. Mutual funds and ETFs took $378bn (from
$176bn). *MEASURED, Z.1 dollars, re-summed by the supervisor from the 11 Sep release.*
- **Funding changed too.** The ON RRP drain that funded money funds in 2024–25 is exhausted ($969bn in Dec 2023, $7bn in Jun
  2026). In July–August 2026 money funds added $415bn of Treasuries by cutting Treasury repo lending ($221bn) and from new assets
  (OFR N-MFP).
- **Foreign official holders are leaving Treasuries.** TIC official holdings fell $236bn from Feb to Jul 2026: net sales of $103bn
  (bills $99bn), valuation −$107bn, residual −$27bn.
- **Japan and the euro area.** Japan's residents turned net sellers of foreign bonds in 2026 (−¥4.5trn to 3 Oct, against +¥12.1trn
  in 2025). In the euro area, banks' buying of government debt slowed from €164bn (Jan–Apr) to €36bn (May–Aug) as the Eurosystem
  kept shrinking.

**FX — money is still flowing into US securities, but less, and official money is leaving the dollar at the margin.**
- **Private buyers:** foreign private net purchases of US long-term securities were $1,600bn over Aug 2025–Jul 2026 (equities $802bn).
- **Net inflow:** the all-instrument net inflow shrank from $1,677bn to $1,311bn year on year.
- **US buyers abroad:** US residents' purchases of foreign securities rose to $478bn (from $286bn).
- **Japan:** the MoF sold about $172bn of dollars for yen in 2026 (Apr–May ¥11.73trn; 30 Jul–26 Aug ¥15.40trn).
- **Reserves:** the dollar's share of allocated reserves is 56.7% (2026Q2). At constant exchange rates it fell 0.94pp in four
  quarters.
- **Euro area:** net portfolio inflow of €341bn over 12 months, against an outflow of €47bn a year earlier.
- **Off-balance-sheet dollar debt:** FX swaps and forwards, the dollar leg, reached $113.5trn (end-2025, +15.5% y/y), still rising.
- **No dollar-funding stress:** Fed swap lines $207mn.

*MEASURED flows. Attribution by country BOUNDED (custodial). Hedging as the driver of the 2025 dollar weakness is the BIS's
reading and HYPOTHESIS here.*

**Commodities — gold's money came from official and household buyers and global ETFs, not from futures; oil's price is a physical
shock.**
- **Gold futures:** managed-money net long on COMEX is 110,987 contracts (6 Oct 2026), about where it was at end-2023 (106,454).
  Gold roughly doubled over the same period, and fund length peaked at 219,029 in Sep 2024.
- **Central banks, reported:** IMF data show +262 tonnes (2024), +306 t (2025), +337 t (Dec 2025–Aug 2026). China reports 2,410 t,
  +106 t in 12 months.
- **Central banks, estimated:** the World Gold Council puts purchases at 1,092 t and 863 t for 2024 and 2025. The 2.5–4× gap includes the WGC's estimate of
  unreported buying; why the two differ by that much is not established here.
- **US gold ETFs:** of the $119bn rise in GLD and IAU assets since end-2023, 77% is price and 23% is flows.
- **Crude:** managed money left WTI over the last four weeks (−58 mb). The Strategic Petroleum Reserve fell 130 mb since end-2025
  while the price went from $60 to about $97. The drivers are physical (supply disruption, stock draws), not financial inflow.
- **Copper:** a record price with LME stocks drawing and managed money flat over 12 weeks.

*MEASURED positions, stocks and reported reserves. WGC estimates BOUNDED. The cause of the oil price is HYPOTHESIS.*

## What can be measured on free data, and how to measure change

| Market | Free series | What it measures | How to measure change |
|---|---|---|---|
| Rates | Z.1 F.210 by holder; TIC SLT Tables 1, 3, 4, 5; H.4.1; H.8; Treasury investor-class allotments; OFR N-MFP and Form PF; CFTC TFF; BoJ Flow of Funds; MoF weekly securities; ECB APP/PEPP, SHSS, BSI; ONS HEWD | Holdings and transactions by buyer, foreign official and private, primary allotments, levered positions | Change in holdings = net purchases + valuation + residual. TIC does not close on its own columns (official residual about ±$100bn a year), so publish the residual. Net is 0.5% of gross. H.4.1 custody is not ownership (custody −$401bn while TIC official −$23bn, Dec 2023–2026). |
| FX | TIC; IMF COFER; BIS GLI, LBS, OTC derivatives, Triennial; MoF intervention and reserves; MoF weekly; Eurostat BoP; SAFE; CFTC TFF currencies; H.4.1 swaps | Portfolio, official, bank and hedging flows; reserve shares; off-balance-sheet dollar debt | Separate flows from FX valuation (constant-FX COFER). Compare the FX-swap notional only across the same half-year, because the series is seasonal (C-132). Futures positions are tiny against $9.5trn of daily turnover. |
| Commodities | CFTC disaggregated COT; GLD/IAU holdings; IMF official gold; SAFE; LBMA vaults; EIA stocks, SPR and STEO; LME stocks (mirror); World Bank prices | Futures positioning by class, ETF tonnes, official tonnes, physical inventories | Split every dollar change into volume × price. A futures long funds nothing physical: only margin moves, and the class nets sum to zero. Weekly managed-money changes move with the same week's price but do not predict the next week (n=148). |

**What cannot be measured for free:**
- the cross-currency basis (hedging cost), and with it whether foreign demand is funded hedged or unhedged;
- ICI's weekly fund flows (blocked to scripts);
- commodity index investment (discontinued by the CFTC in 2015);
- the WTI futures curve (EIA's series ends in Apr 2024);
- unreported central-bank gold buying.

## What the research says (opened sources only; full tables in the raw records)

- **Rates.** QT raises yields and term premia, though by less than QE lowered them.
  - Estimates: about 10bp for the BoJ's purchase cuts (stock effect), 15–25bp for BoE QT, about 35bp per €1trn for the ECB, and
    about 3bp on the 5-year per $100bn of US supply. These measure different things, so the range is HYPOTHESIS for us.
  - Absorption has shifted to more price-sensitive private buyers: non-banks, offshore hedge funds via the basis trade, and
    non-residents in gilts.
  - TIC records holdings by the custodian's residence and undercounts Cayman hedge funds by about $1.4trn.
  - Sources: Du, Forbes and Luzzetti 2024; Beltran and Li 2026; Barth et al. 2025; Judson and Kim 2026; Fang, Hardy and Lewis
    2023; BoJ 2026; BoE MPR 2025; Akkaya et al. 2024.
- **FX.** Hedging, not an exit, is the best-supported reading of the April–May 2025 dollar fall (BIS Bulletin 105). The
  off-balance-sheet swap debt is of the order of the on-balance-sheet dollar debt (Borio, McCauley and McGuire 2022). Reserve
  diversification is real but slow, and gold's reserve share rose mostly through price (Arslanalp, Eichengreen and Simpson-Bell
  2022, 2025; Bertaut et al. 2025).
- **Commodities.** Financialization raised co-movement among indexed commodities (Tang and Xiong). The evidence that index flows
  move prices is weak outside 2007–09 (Hamilton and Wu; Sanders and Irwin), against Singleton. The 2003–08 oil surge was demand,
  not speculation (Kilian and Murphy). The 2024–26 rise in gold's reserve value was price-driven and private demand jumped in late
  2024 (Weiss, FEDS Note, Sep 2026). Gold's sensitivity to real yields collapsed in 2024–25 and came back in 2026 (in-house
  regression; HYPOTHESIS, window-dependent).

## The two lanes compared

| | Gemini (agy, Pro-high) | In-house Sonnet |
|---|---|---|
| **Citations** | 37 sources: 27 quotes found verbatim on the page, 5 near-verbatim (pages load; high word overlap), 5 blocked by the host (mainly imf.org), none fabricated. Many are data portals, not findings. | Every cited source opened. In rates, 37 quotes were re-checked against saved text. |
| **Numbers** | Mostly from secondary pages. No series fetched. | Pulled the latest data from each issuer and gave 4- and 12-period directions. |
| **Where they disagreed** | "Managed-money gold longs expanded to multi-year highs in 2024–2026"; "central banks >1,000 t a year" (WGC figure, stated as fact) | Fund length peaked in Sep 2024 and is back at end-2023 levels; IMF-reported buying is 262–337 t a year, and the WGC figure includes estimates |
| **Cost** | About 22% of the 5-hour quota and 4% of the weekly per market; 17–20 minutes each | Subagent tokens |

Gemini was a useful map of the literature and the series catalogue, and its citations held up far better than its chat surfaces'
record. On numbers, it repeated a headline estimate as fact where the in-house lane measured the reported floor. Use it to find
what to read, and verify every number it gives.

## Corrections this pass found in our own records

- **C-131:** TIC July 2026 equities. The dossier's "+$2.8bn vs −$10.6bn" is a difference of scope (all countries against
  non-official only), not two competing measures. They reconcile exactly.
- **C-132:** the FX-swap notional's "+$15.57trn in H1 2025, the largest in the series" is a half-on-half change in a seasonal
  series. Year on year it is +15.5%, an acceleration from +8.0%. "Largest" holds only in absolute dollars.

## What to build next, in order

1. **A TIC closure ledger** (rates and FX): monthly change in holdings = net + valuation + residual for official, private and the
   five custody centres. Anchor it to the annual survey and H.4.1, with the Cayman overlay as a range. **First test: the August TIC
   release on 16 Oct.** HYPOTHESIS: Japan's Treasury holdings fall by roughly $50–100bn after the Jul–Aug intervention.
2. **Weekly COT ledger for gold, WTI and copper: BUILT 12 Oct** (`bin/pull_cftc_cot.py`; `data/cftc_cot/`). Weekly from 2010, futures-only
   and combined, five classes. The long = short identity holds on all 5,250 rows (exact for futures-only, within rounding for
   combined). Positions and physical units are public; WTI dollars are public (EIA). Gold and copper dollar splits are local only
   (sponsor price licences). Positions move with the same week's price but do not predict the next week (n=145): gold +0.30/−0.01,
   WTI +0.38/−0.08, copper +0.60/−0.07. Since end-2023, almost all of the rise in managed money's gold exposure came from price on
   contracts already held, not new buying.
3. **Gold tonnes ledger:** IMF reported official buying, SAFE, GLD and IAU, and LBMA vaults, against the WGC aggregates. Report
   the unexplained residual.
4. **Primary-market duration by investor class** (rates): R2's pricing applied to Treasury's investor-class allotments, to get
   10-year equivalents taken at auction per class.
5. **A like-for-like FX-swap dollar-debt tracker:** the same half-year each year. The end-June 2026 BIS print is due in November.
6. **A funding ledger for the levered Treasury bid:** CFTC short, dealer positions, money-fund repo and bills, and Form PF. Run a
   lead-lag test with bootstrap ranges.

Open questions carried forward:
- In 2026 the CFTC leveraged short fell while Form PF's net long rose. Why?
- Did Japan's intervention fund the official bill sales?
- How large is unreported central-bank gold buying?
- What is the hedged share of foreign demand?
