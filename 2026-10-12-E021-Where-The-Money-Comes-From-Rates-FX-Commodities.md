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
- **Funding changed too.** Money funds' ON RRP balance, which they ran down in 2024–25 to buy bills (an asset swap inside their
  own balance sheets, not new funding), is exhausted ($969bn in Dec 2023, $7bn in Jun 2026). In July–August 2026 money funds added $415bn of Treasuries by cutting Treasury repo lending ($221bn) and from new assets
  (OFR N-MFP).
- **Foreign official holders are leaving Treasuries.** TIC official holdings fell $236bn from Feb to Jul 2026: net sales of $103bn
  (bills $99bn), valuation −$107bn, residual −$27bn.
- **Japan and the euro area.** Japan's residents turned net sellers of foreign bonds in 2026 (−¥4.5trn to 3 Oct, against +¥12.1trn
  in 2025). In the euro area, banks' buying of government debt slowed from €164bn (Jan–Apr) to €36bn (May–Aug) as the Eurosystem
  kept shrinking.

**FX — money is still flowing into US securities, but less, and official money is leaving the dollar at the margin.**
- **Private buyers:** foreign private net purchases of US long-term securities were $1,600bn over Aug 2025–Jul 2026 (equities $802bn).
- **Net inflow:** the all-instrument net inflow shrank from $1,677bn to $1,311bn year on year. The fall is mostly banks' own
  dollar liabilities (+$162.9bn to −$138.3bn, TIC line 29); foreign net purchases of long-term US securities *rose*, to
  $1,754.4bn (J2, Grok, 13 Oct; line 29 re-read by the supervisor at Treasury).
- **US buyers abroad:** US residents' purchases of foreign securities rose to $478bn (from $286bn).
- **Japan:** the MoF sold about $172bn of dollars for yen in 2026 (Apr–May ¥11.73trn; 30 Jul–26 Aug ¥15.40trn).
  The 16 Oct TIC release was scored on 17 Oct against the pre-registration. Japan's holdings fell from $1,103.9bn to $1,068.3bn
  in August: −$35.6bn raw, or −$40.4bn after the $4.8bn valuation.
  - The wide range (−$190bn to +$60bn) held.
  - The sharper guess, a raw fall of $50–100bn, missed.
  - That is 0.41–0.43 dollars of adjusted sales per dollar of intervention, inside the earlier months' spread.
  - It is an accounting comparison, not evidence that the intervention was paid for by selling Treasuries.
- **Reserves:** the dollar's share of allocated reserves is 56.7% (2026Q2). At constant exchange rates it fell 0.94pp in four
  quarters.
- **Euro area:** net portfolio inflow of €341bn over 12 months, against an outflow of €47bn a year earlier.
- **Off-balance-sheet dollar debt:** FX swaps and forwards, the dollar leg, reached $113.5trn (end-2025, +15.5% y/y), still rising.
- **No dollar-funding stress:** Fed swap lines $207mn.

*MEASURED flows. Attribution by country BOUNDED (custodial). Hedging as the driver of the 2025 dollar weakness is the BIS's
reading and HYPOTHESIS here.*

**Commodities — gold rose alongside official buying, bar-and-coin demand and ETF inflows, while fund futures length ended where it
began; oil's rise ran with large physical stock draws, and funds' futures length rose over 2026 in swings, not one climb (C-141, C-142,
C-146; Grok's K1 review, 13 Oct, and g5 review, 17 Oct).**
- **Gold futures:** managed-money net long on COMEX is 110,987 contracts (6 Oct 2026), about where it was at end-2023 (106,454).
  Gold roughly doubled over the same period, and fund length peaked at 219,029 in Sep 2024. Across all COMEX groups, swap dealers'
  net short deepened by 37,694 contracts (about 117 t), so other futures holders added net length (producers covered 25,512). The
  COT covers US reportable positions only; Shanghai, OTC forwards and Asian ETFs are outside it (C-141).
- **Central banks, reported:** IMF data show +262 tonnes (2024), +306 t (2025), +337 t (Dec 2025–Aug 2026) for all reporters, and
  305/328 t for countries only. The WGC's own reported-share statements imply about 355/371 t. The reported floor is about 260–370 t
  a year, depending on the definition (Grok check, 13 Oct). China reports 2,410 t,
  +106 t in 12 months.
- **Central banks, estimated:** the World Gold Council puts purchases at 1,092 t and 863 t for 2024 and 2025. [Gold ledger, 12 Oct: the gap is
  volatile, not a stable signature of unreported buying. By quarter it runs from −67 t to +276 t. The WGC revises its own quarterly
  figure by up to 187 t between vintages (Q1 2026: 244 t to 57 t). BIS swings move the IMF total. Russia (2,327 t) has not
  reported since Nov 2025. Treat the WGC figure as an estimate with a wide band.]
- **US gold ETFs:** of the $119bn rise in GLD and IAU assets since end-2023, 77% is price and 23% is flows.
- **Crude, NYMEX WTI:** managed money left WTI over the four weeks to 6 Oct (−58 mb, futures only). Over 2026 its net long moved in swings: 15,743
  contracts on 30 Dec 2025 ($57.79), 96,371 on 17 Mar, 73,347 on 31 Mar, 64,041 on 7 Jul, 111,731 on 8 Sep ($94.21), then 53,598
  on 6 Oct (futures only; C-142, C-146). The Strategic Petroleum Reserve fell 130 mb since
  end-2025 while the WTI price went from $60 to about $97. The stock draws are measured; how the rise splits between supply
  disruption and financial demand is not.
- **Crude, ICE Brent.** Measured since 15 Oct by [`bin/pull_ice_brent_cot.py`](bin/pull_ice_brent_cot.py) into `data/ice_brent/`,
  under E-025. Only derived statistics are published (nets, their changes and one share of open interest), and ICE is cited.
  - **Managed money's futures-only net long moved in two legs.**
    - 126,906 contracts on 30 Dec 2025;
    - 382,072 on 31 Mar 2026, the 2026 high;
    - 96,437 on 7 Jul. That is below its end-2025 level, while the EIA Brent spot was 15% above its own;
    - 259,481 on 8 Sep;
    - 275,879 on 15 Sep;
    - 186,288 on 6 Oct.
  - **The last four weeks.** From 8 Sep to 6 Oct it fell 28%, after rising in the first week; from the 15 Sep high it fell
    32.5%. With options it went from 265,753 to 201,052, a fall of 24% (28.9% from the 15 Sep high of 282,657).
  - **Swings, not one climb** (C-146, in the weekly series). 300,712 of the length was on by 24 Feb, with the spot at $71.21; the
    week the spot first jumped $12 (3 Mar) funds cut 54,198 contracts; the net then rose through the March surge to the 31 Mar peak;
    it was cut from 7 Apr to early July and rebuilt from 7 Jul to 15 Sep (+179,442 as the spot rose 82%) before the latest cut.
  - **Outside checks (17 Oct).** ING (11 Aug: 240,748), John Kemp (78 million barrels bought in the week to 17 Mar) and two reports
    for 6 Oct (201,052) match the futures-and-options figures, to rounding. *RELAYED; not re-read.*
  - **The same week.** Weekly changes in the managed-money net long move with the same week's percentage change in the spot price
    (EIA Brent spot for Brent, EIA Cushing spot for WTI).
    - Pooled over 2024–26 (145 weeks), futures only: ICE Brent r = 0.58, NYMEX WTI 0.38.
    - In 2026's 40 weeks alone: Brent 0.60, WTI 0.04.
  - **No lead is detected** in the next week's price change.
    - Futures only, over 144 weeks: −0.01 (ICE Brent) and −0.08 (NYMEX WTI).
    - Both are inside the ±0.16 band, the smallest correlation this sample can tell from zero.
    - The Brent figures include the two flagged EIA prints (6 and 13 Oct); without them the same-week r is 0.59.
    - *MEASURED in sample; coincident, no lead detected.*
- **Copper:** about $14,800 a tonne (12 Oct; whether this is a record was not verified). LME stocks fell over the last month but are
  up 93.6 kt on the year (139,475 t on 9 Oct 2025 to 233,025 t on 9 Oct 2026, Cochilco weekly report, re-read by the supervisor 14 Oct;
  +87.7 kt since 2 Jan). COMEX held 70.9% of the three-exchange visible stock on 9 Oct 2026, against 56.5% a year earlier (both re-read) and 19.7%
  at end-2024 (relayed; Grok g4 item 5). That is where exchange-visible metal sits, not a share of world stocks; Cochilco's printed weekly
  year-on-year column uses a frozen base and should not be quoted. Managed money was flat end to end over 12 weeks (60,185 to 61,134 contracts) after
  peaking at 82,522 on 22 Sep.

*MEASURED positions, stocks and reported reserves. WGC estimates BOUNDED. The causes of the oil and gold moves are HYPOTHESIS.*

## What can be measured on free data, and how to measure change

| Market | Free series | What it measures | How to measure change |
|---|---|---|---|
| Rates | Z.1 F.210 by holder; TIC SLT Tables 1, 3, 4, 5; H.4.1; H.8; Treasury investor-class allotments; OFR N-MFP and Form PF; CFTC TFF; BoJ Flow of Funds; MoF weekly securities; ECB APP/PEPP, SHSS, BSI; ONS HEWD | Holdings and transactions by buyer, foreign official and private, primary allotments, levered positions | Change in holdings = net purchases + valuation + residual. TIC does not close on its own columns (official residual about ±$100bn a year), so publish the residual. Net is 0.5% of gross. H.4.1 custody is not ownership (custody −$401bn while TIC official −$23bn, Dec 2023–2026). |
| FX | TIC; IMF COFER; BIS GLI, LBS, OTC derivatives, Triennial; MoF intervention and reserves; MoF weekly; Eurostat BoP; SAFE; CFTC TFF currencies; H.4.1 swaps | Portfolio, official, bank and hedging flows; reserve shares; off-balance-sheet dollar debt | Separate flows from FX valuation (constant-FX COFER). Compare the FX-swap notional only across the same half-year, because the series is seasonal (C-132). Futures positions are tiny against $9.5trn of daily turnover. |
| Commodities | CFTC disaggregated COT; GLD/IAU holdings; IMF official gold; SAFE; LBMA vaults; EIA stocks, SPR and STEO; LME stocks (mirror); World Bank prices | Futures positioning by class, ETF tonnes, official tonnes, physical inventories | Split every dollar change into volume × price. A futures long funds nothing physical: only margin moves, and the class nets sum to zero. Weekly managed-money changes move with the same week's price but do not predict the next week (WTI, 2 Jan 2024 to 6 Oct 2026: 145 same-week and 144 next-week pairs; the n=148 printed here until 14 Oct did not match `data/cftc_cot/leadlag.csv`, Grok g4 item 2). |

**What cannot be measured for free:**
- whether foreign demand is funded hedged or unhedged. The cross-currency basis, one part of the hedging cost, has been measured
  since 15 Oct from the public swap tape (DTCC; [`2026-10-15-ST1-Swap-Spreads-Inflation-Gap-And-Basis.md`](2026-10-15-ST1-Swap-Spreads-Inflation-Gap-And-Basis.md)):
  the JPY/USD basis went from about −48bp to −22bp in two years, and EUR/USD and GBP/USD sit near zero. That gives the premium,
  not the hedge ratio;
- ICI's weekly fund flows (blocked to scripts);
- commodity index investment (discontinued by the CFTC in 2015). Nor can the COT swap-dealer line stand in for it: on the
  33 monthly changes of the 2013–15 archive, its correlation with index investment is at most 0.42 (WTI swap longs), and about
  zero for gold and copper, against a pass mark of 0.50 fixed in advance (Grok g4 item 8; re-derived by the supervisor 14 Oct).
  So the gold swap-dealer short above cannot be read as index or passive supply;
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
- **FX.** Hedging appears to have made an important contribution to the April–May 2025 dollar fall (BIS Bulletin 105; an earlier line here called it the best-supported reading and "not an exit", which overstated the BIS: C-136). The
  off-balance-sheet swap debt is of the order of the on-balance-sheet dollar debt (Borio, McCauley and McGuire 2022). Reserve
  diversification is real but slow, and gold's reserve share rose mostly through price (Arslanalp, Eichengreen and Simpson-Bell
  2022, 2025; Bertaut et al. 2025).
- **Commodities.** Financialization raised co-movement among indexed commodities (Tang and Xiong). The evidence that index flows
  move prices is weak outside 2007–09 (Hamilton and Wu; Sanders and Irwin), against Singleton. The 2003–08 oil surge was demand,
  not speculation (Kilian and Murphy). The 2024–26 rise in gold's reserve value was price-driven and private demand jumped in late
  2024 (Weiss, FEDS Note, Sep 2026). Gold's sensitivity to real yields collapsed in 2024–25 and came back in 2026 (in-house
  regression; HYPOTHESIS, window-dependent). On public monthly data the return is not established (Grok g4 item 9, inputs
  re-derived by the supervisor 14 Oct): across Jan–Sep 2026 the levels slope is −20% per percentage point of the 10y real yield (R²
  0.66, with residuals in blocks), but on monthly changes the 95% interval runs from −75% to +11%, and across 2025Q1–2026Q3 the
  quarterly slope is about zero.

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
   (sponsor price licences). Positions move with the same week's price and show no detectable one-week lead (n=145): gold +0.30/−0.01,
   WTI +0.38/−0.08, copper +0.60/−0.07. The test can detect correlations above about 0.16; the report is as of Tuesday and
   published Friday, so a longer-horizon regression is the proper test (Grok K1). On the end-points, almost all of the rise in
   managed money's gold exposure came from price on contracts already held; in between, funds built and sold about 113k contracts.
3. **Gold tonnes ledger: BUILT 12 Oct** (`bin/build_gold_ledger.py`; `data/gold/`), monthly from 2019.
   - **Official sector:** IMF official gold for 142 reporters, carry-forward, with the IMF's own world change reproduced to
     under 0.01 t in 88 of 92 months. China per SAFE matches the IMF to the ounce.
   - **Reconciled each quarter:** against the WGC's free release tables.
   - **The first-pass framing is corrected:** the WGC-minus-IMF gap is volatile (see above).
   - **ETFs:** GLD+IAU's tonnage change is about 36% of the WGC's global ETF change on the ledger's basis, and no proxy quarter by
     quarter (in 2026, UK-listed funds out-gathered North America, WGC).
   - **Value:** about 96% of the rise in official gold's value since end-2023 is price, on IMF-reported tonnes. It excludes unreported
     buying, and the share depends on how the price-quantity cross term is assigned.
   - **What is public:** IMF and SAFE series plus per-quarter cited aggregates. Sponsor daily and monthly series are local only
     (licences; the WGC allows limited extracts with citation).
3b. **Crude physical ledger: BUILT 13 Oct** (`bin/build_crude_ledger.py`; `data/crude/`). US weekly since 2001 and world monthly (STEO).
   - **The weekly balance is asserted:** stock change = production + transfers + imports − exports + unaccounted − refinery input.
     Our parse reproduces EIA's table arithmetic within 11 thousand barrels on 508 of 509 weeks since 2017 (EIA added a transfers
     line in Nov 2023). EIA's adjustment line is its balancing item, so this checks our parsing, not the data (Grok K1).
   - **2026 to date (40 weeks):**
     - the Strategic Petroleum Reserve fell 130.2 mb, about $12.0bn at weekly WTI spot;
     - commercial stocks were roughly flat (+1.2 mb);
     - the world drew 424 mb (Jan–Sep, STEO), after building 688 mb in 2025.
     So the price rise ran with large stock draws, while funds' futures length swung (C-142, C-146); the attribution is HYPOTHESIS.
     Outside counts point the same way on the draw, not on its size: the IEA's observed global stocks fell 507 mb over Feb–Aug, while
     OPEC's OECD commercial stocks rose 36.6 mb in August, and IEA members released about 325 mb under the March collective action
     (all relayed by Grok, not re-read).
   - **No free futures curve:** EIA's NYMEX series ends Apr 2024.
   - **EIA's Brent print of 2 Oct is a data error, not a market price** (Grok check, 13 Oct). EIA showed $135.5, then about $125.5;
     ICE front-month Brent settled about $102, and Kalshi's weekly contract priced Brent near $100. Brent-priced ledger columns from
     2 Oct are unreliable until EIA revises.
4. **Primary-market duration by investor class** (rates): R2's pricing applied to Treasury's investor-class allotments, to get
   10-year equivalents taken at auction per class.
5. **A like-for-like FX-swap dollar-debt tracker:** the same half-year each year. The end-June 2026 BIS print is due in November.
6. **A funding ledger for the levered Treasury bid:** CFTC short, dealer positions, money-fund repo and bills, and Form PF. Run a
   lead-lag test with bootstrap ranges.

Open questions carried forward:
- ~~In 2026 the CFTC leveraged short fell while Form PF's net long rose. Why?~~ Mis-posed; resolved 13 Oct, see "The levered bid,
  re-read" below.
- Did Japan's intervention fund the official bill sales?
- How large is unreported central-bank gold buying?
- What is the hedged share of foreign demand?

## The levered bid, re-read (13 Oct)

The two measures do not conflict. OFR's Form PF Treasury exposures "include both cash securities and derivatives, such as Treasury
futures" (OFR chart notes, re-read by the supervisor). So a smaller futures short *raises* Form PF's net long by construction.
Quarter by quarter, the supervisor's computation from the CFTC file on disk (six contracts, face value) and OFR's API:

| Date | CFTC leveraged-fund net | CFTC leveraged-fund short | CFTC asset-manager net | Form PF long | Form PF short | Form PF net |
|---|---:|---:|---:|---:|---:|---:|
| 30 Dec 2025 | −$1,154bn | $1,400bn | +$1,253bn | $2,465bn | $1,645bn | $820bn |
| 31 Mar 2026 | −$1,020bn | $1,234bn | +$1,231bn | $2,359bn | $1,568bn | $791bn |
| 30 Jun 2026 | −$918bn | $1,124bn | +$1,156bn | $2,362bn | $1,498bn | $864bn |
| 29 Sep 2026 | −$774bn | $1,079bn | +$1,087bn | (due about late Nov) | | |

- **Q1 2026:** both legs of the basis shrank. The Form PF long fell $106bn and its short $77bn, while the futures short fell $165bn.
- **Q2 2026:** the Form PF long held while its short fell $70bn, against $110bn on the CFTC. That is why its net rose.
- **The futures short shrank inside the Form PF window.** So "different dates" is not the explanation (Grok K6's explanation 2
  fails on this test).
- **Asset managers' net futures long fell with the leveraged short** ($1,253bn to $1,087bn), the pattern of a basis unwind rather than
  a trend-follower covering (K6's test).
- **Open:** whether the Q2 long held because funds swapped their futures hedge for a pay-fixed swap (the swap-spread trade, which
  Form PF does not count as a Treasury short; BIS, Dec 2025). The test is OFR's interest-rate-derivatives aggregate for the same
  quarters: it should turn more pay-fixed if so. The magnitudes differ because the populations differ: CFTC leveraged funds include
  trend-followers and exclude basis funds classed as asset managers, and Form PF covers qualifying hedge funds only.
- **Grade:** the alignment is MEASURED; the unwind reading and the swap substitution are HYPOTHESIS.

## Grok's source hunt, 13 Oct: what it adds

Six research parcels went to Grok in Cursor; the full returns and the URLs it fetched are in
[`_research/2026-10-13-Grok-Wave-Reviews-Return.md`](_research/2026-10-13-Grok-Wave-Reviews-Return.md). One figure from each was
checked at source by the supervisor, and all matched except the PNC catalogue, which would not download.

- **Hedge ratios: no single number exists.** The published ratios cover identifiable books, from about 20% to about 75%:
  - Danish insurers and pensions, dollar book: 61.8% at the start of 2025, 73.5% at end-May, 72.2% at end-2025 (Nationalbanken;
    the 61.8% to 73.5% re-read by the supervisor).
  - Taiwan's life insurers: 66% to 50% over 2025 (regulator, via press).
  - Japan's nine major life insurers: about 60% in 2021, 40% in 2024 (BIS reading of a BoJ chart).
  - Australian superannuation: about one-fifth of overseas listed equity.
  - Korea's NPS: a 0% target, with up to 10% allowed.

  The Danish rise fits the BIS account of hedging in April–May 2025 (C-136); the Taiwanese and Japanese falls do not. Grok also
  flags two BIS Quarterly Review figures (Dutch 30% to 25%, Danish 55% to 50%) that it could not match to the central-bank
  releases. They stay unresolved.
- **Unreported gold: the envelope moves.** The WGC's own residual (Metals Focus estimate minus IMF-reported buying) has the
  following points:
  - 2024: reported buying was 34% of total demand.
  - 2025: unreported buying was 57% of 863t.
  - Q1 2026: revised from 244t to 57t (re-read by the supervisor at gold.org).

  The IMF (Oct 2025) says some central banks appear to hold new gold outside reported reserves. Our own ledger's finding that
  the gap is volatile stands. A free cap on one channel exists:
  - **Source:** HMRC's trade data (Open Government Licence) gives UK exports of 400-ounce bars to China, CN8 7108.12, in kilograms.
  - **Status:** candidate build 7. A cap, not proof of the buyer.
- **Term premia outside the US: confirmed absent.** No central bank publishes a maintained free series for JGBs, Bunds or gilts.
  The ECB, BoE, Bundesbank and BIS publish charts or one-off articles. One researcher file exists for Japan: Nakajima's
  shadow-rate decomposition, Jan 1995 to Sep 2026, revised each quarter. It is not the BoJ, and no open licence is stated.
  - **Status:** candidate build 8, kept local; R3's "no free term premium" caveat stands for the euro area and the UK.
- **Cross-currency basis: one free academic panel.** Du, Keerati and Schreger (V4, Oct 2025) is a daily panel, for researchers,
  ending June 2025. There is no official basis series, so the FX lane can describe the basis to mid-2025 but not track it (superseded 15 Oct: the
  public swap tape now tracks it daily, ST1).
- **Derivatives as a flow: volume only.** OCC and Cboe publish options volume free; the OCC's site terms ban robots and
  commercial copying. There is no free dealer-gamma or 0DTE history. On average, the research finds 0DTE hedging dampens
  volatility rather than amplifying it:
  - Bank of Canada-affiliated authors (2026): volatility about 7% lower on 0DTE expiry days.
  - Cboe-published study (2025): small effects.

  The IMF (Apr 2026) links leveraged-ETF exposure to intraday volatility on stressed days only. The project's leveraged-ETF
  rebalance estimate (DG, 15 Sep) still needs a dated AUM path.

## The fifteen follow-up items, first tests (Grok batch g4, 14 Oct)

On 14 Oct the principal asked for every item on the ranked list of further rates, FX and commodities research to be started.
Each item went to Grok 4.7 through the fenced Cursor lane, with the instruction to run its first test on free public data. The
supervisor then re-fetched at least one figure per item at source with the neutral User-Agent, and re-derived the arithmetic
where the inputs allowed. All fifteen returns, verbatim apart from quotes cut to twelve words, with the supervisor's check at the
head of each, are in [`_research/2026-10-14-Grok-G4-Returns.md`](_research/2026-10-14-Grok-G4-Returns.md). These are first
tests. None of them makes a flow the cause of a price.

**What the first tests found**

| # | Item | First test | Checked at source |
|---:|---|---|---|
| 1 | Japan intervention funding | Across the seven completed intervention months, the change in Japan's Treasury holdings (after an R1 valuation) per dollar of intervention runs from 0.58 of a dollar of buying to 1.91 dollars of selling. There is no stable ratio. Sep 2022's −$79.6bn was 80% revaluation; May 2026's −$66.8bn was quantity. **Pre-registered** for the 16 Oct TIC print: August's adjusted change between −$190bn and +$60bn (`CALENDAR.tsv`, committed 14 Oct) | yes: every input, and the valuation recomputed with the R1 code |
| 2 | COT horizons, ICE Brent | The four-week halving of WTI fund length is futures-only (−52%); counting options it is −25%. The page now says so. On all 875 weeks the test could see a one-week correlation of about 0.07, against 0.16 on the 2024–26 sample, so "no detectable lead" is not yet tested at full size | yes: CFTC rows; E-021's n=148 corrected to 145/144 |
| 3 | Swap-tape ledger | Grok could not open the DTCC files. The supervisor can: the cumulative-rates archive starts 14 Oct 2024 (11 Oct 2024 is a 404) and the 13 Oct 2026 file is a 15 MB CSV. The build is unblocked. DTCC's reuse terms were still unread at the time (read 14 Oct; the principal's ruling is E-024), so only derived medians will be published | yes: Treasury rows; DTCC reached |
| 4 | Yen against rate gaps | The "1.3pp narrowing" mixes two end dates. On one date both tenors narrowed about 1.1–1.2pp. Inside the window the 10y gap and USD/JPY moved together in 2024–25 and apart in 2026. The weekly regression has not been run | yes: BIS yen prints |
| 5 | Copper visible stocks | Cochilco publishes LME, COMEX and SHFE stocks free in tonnes. COMEX held 70.9% of the three-exchange total on 9 Oct 2026, against 56.5% a year earlier. Cochilco's printed weekly year-on-year column uses a frozen base and is wrong | yes: both 9 Oct weeklies |
| 6 | R1 second opinions | The Cleveland Fed model's inflation compensation rose 25bp (October run; 27bp on the September run) against TIPS +17bp. That is inside the 10bp trigger, so the breakeven row stands. Added to R1 | yes: the Cleveland workbook and GSW |
| 7 | N-PORT duration holders | Not run: the bulk files are on sec.gov, which only the supervisor may fetch. Z.1's fund rows re-derive $640bn of net purchases (2024–2026Q2). That is enough at either end of the maturity range to make funds anything from bystanders to a first-order duration sink, so N-PORT is needed | yes: R2 rows, Z.1 ETF line |
| 8 | Index-investment proxy | **Negative.** On the 2013–15 CFTC archive, swap-dealer changes do not track index investment for gold, copper or WTI. The best is 0.42 (WTI), against a 0.50 pass mark fixed in advance. Gold's swap-dealer short cannot be read as passive supply | yes: all nine correlations, CFTC rows |
| 9 | Gold against real yields | In 2026 alone the levels slope is −20% per point, but on monthly changes the interval covers zero, and across 2025Q1–2026Q3 the slope is about zero. "Came back in 2026" is not established | yes: Treasury real yields, Pink Sheet, the regression |
| 10 | US external balance sheet | In 2026Q2, price changes were 81% of the $4.87trn rise in US liabilities; transactions were $979bn. "Money flowing in" describes the transactions slice, not the stock. The net position is −$22.42trn | yes: the BEA release |
| 11 | BIS pre-registration | **Pre-registered** for the BIS release due by 16 Nov: FX forwards and swaps dollar notional at 2026-S1 +11% to +18% June on June (last two: +8.2%, +14.5%). The +15.5% the calendar used to quote was December on December, and included currency swaps | yes: the BIS series |
| 12 | IMF currency composition | Germany's dollar share of its debt claims on non-residents fell from 14.6% (2019) to 12.9% (2026Q2) because its euro-denominated book grew faster. Within foreign-currency claims the dollar's share rose, from 59.1% to 60.3%. Across six reporters with a dollar line there is no common fall (Canada +7.3pp, Switzerland −1.7pp). The fall in the dollar's share of official reserves is not repeated in these private books, which say nothing about hedging | yes: the IMF Germany series |
| 13 | Dealer DV01, repo dispersion | Dealers' net Treasury book rose $176bn (fair value) from end-2023. Their over-7-year coupons on 30 Sep 2026 were 2.1× the 2022–23 maximum. On large cash days, SOFR dispersion was 3bp narrower after June 2026 than before, but the two sets of days are not matched, so that is not a test | yes: NY Fed dealer series, SOFR |
| 14 | Refunding event study | From Nov 2023 no clean refunding statement moved both the 10y and the 30y outside the Wednesday band (±8bp) in the direction of its supply news. The coupon increases all fell on FOMC days. The 19 Aug 2026 buyback doubling moved the 30y −9bp but the 10y only −6bp. **Pre-registered** for 4 Nov, already marked unclean because it is the day after the US election | yes: event-day yields, the Treasury buyback release |
| 15 | Global yield comovement | Jan–Jul 2026: weekly changes in the US 10y and the Bund correlate 0.76, while the US level rose 56bp against the Bund's 25bp. Only two countries and part of the window have been read, so the term-premium split is not yet set in a global-factor frame | yes: all 30 US weekly changes |

**Builds, in order** (specs in the returns file; each commits its script and derived tables, never a licensed or Refinitiv-sourced
series):
1. **Swap-tape ledger** (item 3): DONE 15 Oct. The principal ruled to script it despite DTCC's terms (E-024). The result is in ST1.
   The ledger runs weekly from a CALENDAR row.
2. **N-PORT Treasury maturity buckets** (item 7): DONE 15 Oct. The result is in R2b
   ([`2026-10-15-R2b-Who-Took-The-Duration-Registered-Funds.md`](2026-10-15-R2b-Who-Took-The-Duration-Registered-Funds.md)).
   Registered funds took $549bn on their own filings and $450bn scaled to Z.1, so the first-order verdict is not established.
3. **Full-sample COT horizons** (item 2). The ICE Brent leg was BUILT on 15 Oct, after the principal extended E-024's terms to
   it (E-025). The multi-horizon regressions over the full sample are still to do, for WTI and Brent.
4. **Yen and euro against rate gaps, weekly regression** (item 4), the three windows pre-registered in the return.
5. **Gold against real yields with HAC errors and a break date** (item 9), once the World Bank monthly workbook downloads.
6. **Four-country comovement** (item 15), adding the UK and JGB legs.
7. **Copper ledger** (item 5), kept local (Refinitiv-sourced), with only the shares published.
