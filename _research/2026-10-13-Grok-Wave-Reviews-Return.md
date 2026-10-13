# Grok (Cursor CLI) wave, 13 Oct 2026: ten parcels, verbatim returns and the supervisor's adjudication

*Ten parcels sent by the supervisor through `orchestrator_cursor` to Grok 4.7 (256k, extra-high), each in a fresh stage behind the read-and-web-only fence, in two parallel waves of five. Every call ended SUCCESS, with no fence breaches, no blocked attempts, no unexpected tools and no stage changes. URLs cited without a fetch in this call are listed per parcel and are not relied on. The returns are claims until checked; the adjudication is at the end.*

*Quotes in the returns longer than 15 words were cut to their first twelve words by the supervisor (the repository's quotation rule); the full text is at each cited URL.*

| Parcel | Topic | Wall time (s) | Searches | Fetches | URLs cited but not fetched |
|---|---|---:|---:|---:|---:|
| J1 | Headline equity findings (judge) | 919 | 13 | 31 | 0 |
| J2 | Rates and FX flow map (judge) | 1033 | 13 | 37 | 1 |
| J3 | AI build-out financing (judge) | 693 | 11 | 16 | 0 |
| J4 | Collateral velocity, the Singh argument (judge) | 974 | 18 | 35 | 0 |
| R1 | Hyperscaler 2026 bond issuance (find) | 555 | 32 | 32 | 0 |
| R2 | Free term-premium series outside the US (find) | 760 | 41 | 43 | 0 |
| R3 | Derivatives as a market-structure flow (find) | 584 | 19 | 39 | 9 |
| R4 | Hedge ratios of foreign holders of US assets (find) | 476 | 27 | 19 | 0 |
| R5 | Bounding unreported central-bank gold (find) | 469 | 27 | 38 | 5 |
| R6 | Three data questions: corporate net interest, MOVE methodology, cross-currency basis (find) | 560 | 24 | 24 | 0 |


---

## J1 — Headline equity findings (judge)

I'll review the project's claims against its own notes and primary sources. First I'm reading the claims file and the public method notes.The notes disagree with several headline wordings on window, universe, and what was actually measured. I’ll pull the source notes and primary series next and recompute the figures that decide the verdicts.The 71–82% earnings split and the “two-thirds SpaceX” line look window- and sample-sensitive. I’m pulling the Fed, Shiller, and IPO pages so the verdicts rest on recomputed figures.The earnings endpoints match Shiller’s series. The issuance and premium claims still need the Fed tables and the rate data, which I’m fetching now.The claims are scoped to end-2023 through mid-2026. Two figures below were rebuilt from outside data: the earnings share of the price gain, and the nonfinancial corporate tax rate.

CLAIM: H1
VERDICT: FALLS
REASON: On Shiller monthly-average prices and trailing as-reported earnings, December 2023 to June 2026 is a log price gain of 0.464 against a log earnings gain of 0.429, so earnings are 92.4% of that price gain (4,685.05 to 7,450.03; earnings 192.43 to 295.39). The 71.0% and 82.3% figures reproduce only for December 2014–December 2025 and December 2014–June 2026, the same GAAP series at two long-window endpoints.
SOURCE URL: https://www.multpl.com/s-p-500-historical-prices/table/by-month
QUOTE: "all prices are monthly average closing prices."
UNCERTAIN: Operating EPS for this short window was not re-derived. S&P’s own operating series would settle whether any earnings measure puts the short window inside 71–82%.

CLAIM: H2
VERDICT: WEAKENED
REASON: Treasury 10-year par real yields average 1.92% in December 2023 and 2.18% in June 2026, a 26bp rise. With the earnings yield falling 14bp (4.11% to 3.97%), the defined premium compresses about 40bp and the rate leg is about 65% of it. The 36–60% band is the project’s own basis range on the whole residual, and that note says a consistent extrapolation can put growth above the entire compression.
SOURCE URL: https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_real_yield_curve&field_tdr_date_value_month=202606
QUOTE: "These par real yields are calculated from indicative secondary market quotations"
UNCERTAIN: Their 34bp real-yield rise was not recovered from these daily curves (month-end is +48bp). Their DFII10 monthly-mean file would settle the 8bp December gap. Damodaran’s monthly growth path 8.74% to 13.69% was not on the annual page fetched here (that page stops at January 2026 and shows 2023–25 smoothed growth of 3.68% to 4.61%).

CLAIM: H3
VERDICT: WEAKENED
REASON: On the 11 September 2026 Z.1, ETF net share issues over 2024Q1–2026Q2 are about $3,652bn and all-sector net equity issues about $3,269bn, while nonfinancial corporate equity issues are −$541bn. That is ETF creation against a shrinking nonfinancial line. The line is public and closely held together, and bond-fund ETF issuance on the same table is about $1,065bn, roughly 29% of the wrapper.
SOURCE URL: https://www.federalreserve.gov/releases/z1/20260911/html/f51_1_t.htm
QUOTE: "Includes shares of closed-end funds, exchange-traded funds"
UNCERTAIN: The published seasonally adjusted table implies 2026H1 ETF issuance of about $1,039bn. Their $3,603.8bn total was not reproduced. The unadjusted transactions file would settle the $48bn gap.

CLAIM: H4
VERDICT: FALLS
REASON: M&A of about $1,045bn against net retirement of about $552bn makes M&A larger than the net only because gross issuance is netted off first. The Fed defines retirement as repurchases plus cash M&A, and the project’s own annual table for this file had 2024–25 repurchases of $728bn and $773bn against M&A of $322bn and $376bn. Net issuance then turned positive in 2026 (+$45bn, +$152bn on their later reading), which shrinks the net and inflates M&A’s share of it.
SOURCE URL: https://www.federalreserve.gov/releases/efa/efa-project-equity-issuance-retirement.htm
QUOTE: "Equity retirements occur through share repurchases or mergers and acquisitions."
UNCERTAIN: The quarterly CSV returned only the dictionary and a guessed CSV URL 404’d, so $1,045bn and $552bn were not re-summed here, and the September/October revision may have changed the buyback totals. Summing Retirements, Repurchases against Retirements, Mergers and Acquisitions for 2024Q1–2026Q2 would settle it. M&A also covers private as well as public targets.

CLAIM: H5
VERDICT: WEAKENED
REASON: The 7–13% band is four ways of aggregating diluted-share decline as a share of the log price gain since 2015, and the project says survivorship pushes every one of them up. Their own share index falls from 1.00 in 2015 to 0.894 in 2023 and only to 0.872 in 2025, so most of the accretion sits before this window. Share-count decline also mixes buybacks with M&A removals and stock-based pay.
SOURCE URL: https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-18-EPS-Split.md
QUOTE: "overstate buyback intensity (survivors are the buyers)."
UNCERTAIN: No independent constituent share panel was rebuilt. A 2023–2026 back-dated S&P divisor, or S&P’s buyback series, would settle the in-window ceiling.

CLAIM: H6
VERDICT: FALLS
REASON: The statutory rate was already 21% at both ends of end-2023 to mid-2026. On Z.1, nonfinancial corporate taxes over profits before tax rise from 18.0% in 2023 (486.9/2,704.1) to 20.7% in 2026Q2 (737.9/3,561.2), so the tax wedge reduced the after-tax share of pretax profit. The “about a tenth” result is the project’s 2015–2025 effective-rate decline (27.4% to 19.6%), which brackets 2018 and which that note says foreign mix can inflate.
SOURCE URL: https://www.federalreserve.gov/releases/z1/20260911/html/s11_1_t.htm
QUOTE: "Taxes on corporate income"
UNCERTAIN: Z.1 profits are NIPA nonfinancial corporations, not S&P 500 EPS. A constituent effective-tax panel for FY2023 versus FY2025 would settle the index itself.

CLAIM: H7
VERDICT: WEAKENED
REASON: Z.1 money-fund repurchase agreements fall from $2,665.9bn at end-2023 to $2,620.2bn at end-2024, −$45.7bn, which is the −$46bn. Over the same year money-fund assets rise $886bn and Treasury holdings rise $725bn. The New York Fed has December 2023 ON RRP averaging $807.7bn and ending the year at $1.02tn, so a quarter-end comparison loads a year-end spike into the drain.
SOURCE URL: https://www.newyorkfed.org/medialibrary/media/markets/omo/omo2023-pdf
QUOTE: "ending the year at $1.02 trillion."
UNCERTAIN: The private-versus-Fed split inside the $2,665.9bn was not read off a Fed table this session; it only adds up to that total. Month-average MMF repo with the Fed for 2024 would settle how much of the −$46bn is the December 2023 spike.

CLAIM: H8
VERDICT: WEAKENED
REASON: SpaceX’s filing records 638.9 million shares at $135 including the full shoe, and net proceeds of $85,675 million, against a $75bn base. Renaissance’s 8 September 2026 preview has 2026 IPO proceeds at $146bn, $71bn excluding SpaceX, so the base deal is about half of that census. Two-thirds is $75bn over the project’s nine-prospectus sum of about $112bn.
SOURCE URL: https://www.renaissancecapital.com/review/US_Fall_Preview_2026_Public.pdf
QUOTE: "raised a record $146 billion ($71 billion ex-SpaceX)"
UNCERTAIN: Whether Renaissance’s $146bn matches the project’s universe (operating-company primary proceeds, no SPACs, no small deals) was not stated on the page. A full SEC count of 2026 primary proceeds would settle it. Renaissance is a vendor census.

CLAIM: H9
VERDICT: WEAKENED
REASON: On the same Z.1 flow table, ETF purchases of corporate equities are about $2,509bn and mutual-fund transactions about −$2,049bn, an offset of 81.6%, with about $460bn of ETF equity buying left over. Sector totals cannot show that those dollars are the same money moving wrapper.
SOURCE URL: https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-15-ETF1-Identity-Net-Of-ETF.md
QUOTE: "most of the equity-wrapper, not all of it."
UNCERTAIN: Account-level rotation is what the project already calls unsettled on free data. Linked shareholder or transfer-agent records would settle it.

The claim most likely to be wrong is H6. The tenth is a 2015-to-2025 effective-rate arithmetic that straddles the 2018 statutory cut. On the window named in the claims file, the Fed’s nonfinancial tax rate moves from 18.0% to 20.7%, so tax takes a larger share of pretax profit rather than explaining a tenth of the earnings gain.

---

## J2 — Rates and FX flow map (judge)

**Cited but not fetched in this call (not relied on):** https://alfred.stlouisfed.org/series?seid=RRPONTTLD

I'll review each claim against the project's notes and primary sources, starting with the claims file and the pages that document the method.The notes give the method behind each claim. Next I’ll check those figures against the Fed, Treasury, IMF, BIS and the other primary releases they cite.The Z.1 flow table is in hand, and the TIC totals match the press release. I’ll re-sum the quarterly rates and check the yield, reserves, and derivatives figures at the source.CLAIM: R1
VERDICT: WEAKENED
REASON: On the 11 Sep 2026 Z.1 table F.3.2, quarterly flows are annual rates (the 2025 average of the four quarters equals the annual column). Dividing by four, 2025Q3–2026Q2 net issuance is $2,362bn and the book-value rise is $2,360bn (30,878.3 minus 28,518.3). The Fed’s $264bn matches the seasonally adjusted flow ($264.3bn). The rest-of-world figure of about $294bn matches coupons only, $294.5bn, while all Treasuries are $289.5bn; money funds’ $668bn matches the book-value rise ($3,281.6bn minus $2,614.0bn), not the $671bn adjusted flow. The 12% share still rounds either way. The prior-window $709bn and 44% are not on the published quarter columns.
SOURCE URL: https://www.federalreserve.gov/releases/z1/20260911/html/F3_2_t.htm
QUOTE: "Marketable Treasury securities (net of premiums and discounts)"
UNCERTAIN: That $294bn was taken from the coupon row rather than an unadjusted all-Treasury file. The 2024Q3–2024Q4 columns of this same vintage would settle the $1,615bn and $709bn.

CLAIM: R2
VERDICT: STANDS
REASON: TIC Table 5 shows foreign official holdings fell from $4,009.6bn in February 2026 to $3,773.1bn in July, or $236.5bn. Bills fell from $453.3bn to $354.4bn, or $98.9bn. March–July long-term official net transactions sum to −$3.7bn, so sales are about $103bn, and the valuation series sums to −$106.7bn. The plug is −$27bn. Long-term notes were barely sold; the price effect is the large piece, and the claim already says so.
SOURCE URL: https://ticdata.treasury.gov/Publish/slt_table5.html
QUOTE: "may not provide a precise accounting of"
UNCERTAIN: Bill stock changes are treated as transactions. Treasury’s own custody warning, and the project’s roughly $100bn-a-year official residual, mean the $27bn plug is an error bar. A full SLT closure file for March–July would show whether any of the $99bn of bills is a custody shift.

CLAIM: R3
VERDICT: WEAKENED
REASON: The overnight reverse repo is an asset: the New York Fed sells a security to the counterparty, so the runoff is an asset swap by money funds, not a funding source that paid for their Treasury buying. The only balance fetched was $0.300bn on 9 Oct 2026, which shows the facility is drained by then. The $415bn, −$221bn, $969bn and $7bn were not on the OFR or New York Fed pages opened here. Those two asset changes also do not by themselves fund $415bn.
SOURCE URL: https://alfred.stlouisfed.org/series?seid=RRPONTTLD
QUOTE: "sells a security to an eligible counterparty"
UNCERTAIN: The December 2023 and June 2026 levels, and the July–August N-MFP Treasury and Treasury-repo stocks. OFR series MMF-MMF_T_TOT-M and MMF-MMF_RP_T_TOT-M for June–August 2026, plus the New York Fed print for 29 Dec 2023 and 30 Jun 2026, would settle them.

CLAIM: R4
VERDICT: UNTESTABLE
REASON: The Ministry of Finance weekly file is the designated-major-investor report, in units of ¥100 million, and the claim is explicitly that partial series through 3 Oct against the full year 2025. The file fetched here begins in 2005 and was cut off before any 2026 week, so −¥4.5trn and +¥12.1trn were not re-summed.
SOURCE URL: https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/week.csv
QUOTE: "based on reports from designated major investors"
UNCERTAIN: The year-to-date sum itself, and whether it is long-term debt only or long-term plus short-term. A complete sum of the 2026 “Long-term debt securities / Net” column through the week of 3 Oct, against the 2025 total of the same column, would settle it.

CLAIM: R5
VERDICT: WEAKENED
REASON: The 16 Sep 2026 TIC release does show private net purchases of long-term securities of $1,599.6bn in the twelve months to July 2026, and line 30 falling from $1,676.6bn to $1,311.1bn. That $366bn drop is mostly banks’ own dollar liabilities, from +$162.9bn to −$138.3bn. Foreigners’ purchases of long-term US securities rose from $1,468.7bn to $1,754.4bn. Of the $1,599.6bn, equities are $802.3bn.
SOURCE URL: https://home.treasury.gov/news/press-releases/sb0631
QUOTE: "Change in Banks' Own Net Dollar-Denominated Liabilities"
UNCERTAIN: How much of line 29 is a reporting revision rather than a real banking outflow. The August release and the banking-liabilities revision page would settle that.

CLAIM: R6
VERDICT: WEAKENED
REASON: The IMF’s 30 Sep 2026 brief says the dollar’s share of global reserves was 56.70% in 2026Q2, down from 57.18% in Q1, with exchange-rate moves inside about ±2% and valuation effects limited. The 0.94 percentage-point constant-exchange-rate decline over four quarters is not in that brief. It is an in-house adjustment, and the same brief says “other currencies” were still above 6% of reserves, the bucket the project says it left unadjusted.
SOURCE URL: https://data.imf.org/en/news/imf%20data%20brief%20september%2030
QUOTE: "exchange-rate valuation effects were limited"
UNCERTAIN: The four-quarter constant-exchange-rate change. Quarter-end amounts by currency and the IMF’s own valuation split for 2025Q2–2026Q2 would settle it.

CLAIM: R7
VERDICT: STANDS
REASON: The BIS series the project names, summed across the two instrument codes, is $74.023trn plus $39.474trn at 2025-S2, or $113.50trn, against $65.127trn plus $33.174trn at 2024-S2, or $98.30trn, which is +15.5%. The half-on-half jump into 2025-S1 is $113.87trn minus $98.30trn, or $15.57trn, and the stock then eased to $113.50trn by 2025-S2. That is the seasonal pattern the claim describes. Notional is still a gross stock.
SOURCE URL: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_OTC_DERIV2/1.0/H.A.D.B.5J.A.5J.A.USD.TO1.A.A.3.C?startPeriod=2024-S2&endPeriod=2025-S2&format=csv
QUOTE: "Comparisons of amounts outstanding between periods can be significantly affected"
UNCERTAIN: The instrument names behind codes D and I, inferred as forwards and swaps because the sum matches the claim. The BIS codelist, and whether any pre-2025 half-on-half percent exceeded 2025, would settle the “not a record” half.

CLAIM: R8
VERDICT: FALLS
REASON: BIS Bulletin 105 says hedging “appears to have made an important contribution” to the dollar’s weakness in April and May 2025, and that the largest declines were in Asian hours. It does not say hedging best explains the move, and the key takeaways do not say the episode was not an exit. The claim upgrades a contributory, hedged finding into a ranked explanation.
SOURCE URL: https://www.bis.org/publ/bisbull105.htm
QUOTE: "appears to have made an important contribution"
UNCERTAIN: Whether the bulletin body, which did not extract beyond the key takeaways, somewhere ranks hedging above other causes or rules out selling. The PDF body text would settle that.

CLAIM: R9
VERDICT: WEAKENED
REASON: Treasury par yields show the 10-year at 3.88% on 29 Dec 2023 and 5.01% on 18 Sep 2026, a rise of 113bp, with the 10-year real yield from 1.72% to 2.68%, or 96bp, so breakevens are 17bp. From the 19 Oct 2023 peak the same 10-year went from 4.98% to 5.01%, or +3bp, and the real yield from 2.49% to 2.68%, or +19bp. The BoJ’s “around 10 basis points” is the stock effect only (about 25bp once the flow effect is included); the BoE’s 15–25bp is cumulative gilt QT since 2022; the ECB’s about 35bp per €1trn is what analysts expected, and the blog says that survey cannot measure the exact effects.
SOURCE URL: https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202609
QUOTE: "10 Yr"
UNCERTAIN: Nothing material on the 113bp and 96bp, which match the Treasury curves. A common numeraire for the BoJ, BoE and ECB estimates would be needed before they can be read as one range.

The claim most likely to be wrong is R8. The bulletin’s own takeaway is that hedging appears to have been an important contribution, concentrated in Asian hours. The claim turns that into the best explanation and adds “not an exit,” which those takeaways do not say.

---

## J3 — AI build-out financing (judge)

I'll review each claim against the project's own notes and primary sources, starting with the claims file and the funding notes.The notes are in. Next I’ll check the cash-flow, lease, bond, and bank-exposure figures against filings and the Chicago Fed piece.CLAIM: A1
VERDICT: FALLS
REASON: Amazon's Q2 2026 earnings exhibit shows trailing operating cash flow of $161.403bn against purchases of property and equipment of $173.028bn, a shortfall of $11.6bn and free cash flow of −$7.6bn, so the shortfall is not confined to Oracle. Oracle's own quarterly bridge gives trailing operating cash flow to 31 Aug 2026 of $46.940bn ($31.977bn − $8.140bn + $23.103bn) against capital expenditure of $75.660bn ($55.663bn − $8.502bn + $28.499bn), a gap of $28.7bn; the ~$35bn matches the project's separate "internal cash" residual of $40.8bn.
SOURCE URL: https://www.sec.gov/Archives/edgar/data/1018724/000101872426000024/amzn-20260630xex991.htm
QUOTE: "Free cash flow decreased to an outflow of $7.6 billion"
UNCERTAIN: What the project subtracts to turn Oracle's $46.9bn of operating cash flow into $40.8bn of "internal cash" was inferred from the gap. The funding-table CSV definition would settle it. Alphabet, Meta and NVIDIA were not re-derived; Amazon alone breaks five of six.

CLAIM: A2
VERDICT: WEAKENED
REASON: Microsoft's 10-K discloses $329.1bn of additional leases, primarily datacenters, not yet commenced, and Oracle's 10-K discloses $260bn of additional data-center lease commitments, so those two pieces of the $1,122.9bn are in the filings and $1,122.9bn / $228.3bn is 4.9. The ratio sets undiscounted future rents, some conditional, against maximum guarantee ceilings: Microsoft's commenced finance leases are $89.686bn of payments against a $66.594bn recognized liability.
SOURCE URL: https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/R23.htm
QUOTE: "with some arrangements subject to certain contractual conditions being met"
UNCERTAIN: Meta, Amazon, Alphabet and NVIDIA lease lines, and the $228.3bn guarantee total, were not re-read from the filings here. An unconditional, present-value cut of all six footnotes would settle whether 4.9x still holds.

CLAIM: A3
VERDICT: WEAKENED
REASON: Amazon did raise $81.925bn of long-term-debt proceeds in the twelve months to 30 Jun 2026, so that piece of the ~$272bn is a real trailing proceeds figure. The ~$750bn in the notes fetched here is 2026 cash flow or capex (UBP: about $750bn of operating cash flow; S&P via The DESK and TwentyFour: about $750bn of capex), while the bond figures on those pages are about $212bn of debt in the first half and, on Goldman's page, $194bn issued so far in 2026 with a full-year hyperscaler forecast around $250bn. Oracle's FY2026 release says it raised $43bn of debt financing; the cash-flow line is $46.093bn of senior notes, term loans and other borrowings.
SOURCE URL: https://www.ubp.com/files/live/sites/ubp/files/documents/investment/headlines/20260916_ubp-headlines-financing-ai-build-out.pdf
QUOTE: "USD 750 billion of cash flow this year"
UNCERTAIN: No fetched page was found that forecasts $750bn of hyperscaler bonds. A calendar-2026 face-value deal list would settle the $272bn.

CLAIM: A4
VERDICT: WEAKENED
REASON: The same N-PORT note that supplies ~$9.7bn says the one-report-per-fund totals are $9.73bn and $9.72bn, while its single report-date cut is $8.76bn at 31 Mar 2026 and $8.73bn at 30 Jun 2026, about 32% of $27bn. Its 2026Q2 file is filings submitted April–June for periods ending around 31 March, so the claim's quarter labels are filing quarters. CoreWeave's like-for-like move from $2.73bn to $5.08bn is the project's figure behind ~$5.1bn.
SOURCE URL: https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-08-22-D2-Who-Holds-The-AI-Paper.md
QUOTE: "Beignet is $8.76bn and $8.73bn"
UNCERTAIN: The SEC bulk holding file was not re-summed here. A price for CUSIP 076912AA2, and the closed-end and fund-of-funds share inside "once per fund," would settle the 36%.

CLAIM: A5
VERDICT: WEAKENED
REASON: The ~$4bn is the project's July 2026 N-MFP name search, about $0.26bn held directly and about $3.99bn as repo collateral, and that collateral funds dealer inventories. The same note calls the census a floor because subsidiaries and SPVs can miss the name strings, and the list includes Apple, which that note sets aside as not an AI capex firm, so the claim states a ceiling the method does not deliver.
SOURCE URL: https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-08-22-D2-Who-Holds-The-AI-Paper.md
QUOTE: "the census is a floor"
UNCERTAIN: The N-MFP filings were not re-parsed. A collateral-issuer sweep for Beignet, Sopaipilla and other SPVs would settle whether the miss is large.

CLAIM: A6
VERDICT: WEAKENED
REASON: The Chicago Fed does put large-bank C&I commitments to its AI-adjacent industry set at about $250bn in 2015 and about $450bn in late 2025, with about $150bn outstanding. That set is software, electric and gas utilities, and semiconductor manufacturing; the article puts energy plus semiconductors at about $275bn, software at $191bn in late 2025 against $150bn in early 2022, and says energy companies are not that exposed to AI. The 2015 figure is an earlier level of this broad book, so the build-out residual stays unmeasured.
SOURCE URL: https://www.chicagofed.org/publications/chicago-fed-insights/2026/ai-tail-risk-for-banks
QUOTE: "not all companies in these industries have exposure to AI"
UNCERTAIN: The $450bn and $250bn were not rebuilt from FR Y-14Q loan-level data. A purpose split for data-center construction, CRE and loans to AI operators would settle the residual.

The claim most likely to be wrong is A1. Amazon's filing puts trailing operating cash flow below cash capex by $11.6bn, and Oracle's re-derived operating-cash gap is $28.7bn, so both the five-of-six count and the $35bn are off on primary cash-flow statements.

---

## J4 — Collateral velocity, the Singh argument (judge)

I'll review each claim against the project's notes and primary sources, starting with the claims file and the two public notes.The notes define velocity as pledged collateral received divided by primary sources. Next I’ll check the IMF paper, Form PF definitions, and the bank filings those ratios rest on.CLAIM: V1
VERDICT: STANDS
REASON: WP/19/106’s end-2017 stock of about $7.5 trillion is collateral received “that could be onward re-pledged,” and Figure 3 is sourced to bank annual reports. On the filing vintage available for Singh’s January 2026 “around $1.8 trillion,” JPMorgan’s permitted line was $1,829.9 billion and the amount already sold or repledged was $1,439.9 billion. The permitted line is still wider than pure repledge: the same footnote includes collateral “delivered, or otherwise used,” taken under resale, prime-brokerage, and derivative agreements.
SOURCE URL: https://www.imf.org/-/media/files/publications/wp/2019/wpiea2019106.pdf
QUOTE: "could be onward re-pledged in their own name"
UNCERTAIN: The PDF text does not give Figure 3’s bar values, so the 2017 US bars were not matched number-for-number to the footnotes. A digitized Figure 3 would settle that.

CLAIM: V2
VERDICT: WEAKENED
REASON: SEC XBRL matches three of the five permitted stocks exactly: JPMorgan $968.8 billion (2017) to $2,181.4 billion (30 June 2026), 2.25×; Goldman $763.984 billion to $1,431.870 billion, 1.87×; Citi $457.5 billion (2017) to $1,064.0 billion (31 December 2025), 2.33×. JPMorgan’s repledged share did not rise: $775.3 / $968.8 = 80.0% in 2017 and $1,741.8 / $2,181.4 = 79.8% at 30 June 2026. The five-name total of about $3,351 billion to $7,460 billion, and the four-bank move from about 80% to 84%, still depend on Morgan Stanley and Bank of America, which do not report this US-GAAP concept, and on Citi’s year-end print against June filings for the others.
SOURCE URL: https://www.sec.gov/Archives/edgar/data/19617/000162828026054343/R57.htm
QUOTE: "Collateral sold, repledged, delivered or otherwise used"
UNCERTAIN: Morgan Stanley’s $599.2 billion and $1,382.7 billion, and Bank of America’s $561.9 billion and roughly $1,400 billion, were not read from filings here. Those two footnotes would close the panel and the 84% ratio.

CLAIM: V3
VERDICT: FALLS
REASON: The size comparison is real and was re-derived from the OFR series: qualifying-hedge-fund repo borrowing was $3.249 trillion against cash collateral posted of $2.940 trillion on 31 March 2026, and $3.382 trillion against $3.137 trillion on 30 June 2026. That inequality cannot show the cash bucket is mostly reusable Treasuries. Repo borrowing is cash borrowed; the OFR’s own chart says funds post securities to borrow cash, and the current Form PF repo lines split cash from “government securities and other securities.” A bucket smaller than the repo book cannot contain that repo collateral. In the OFR’s H2 2025 transaction data, hedge funds borrowed $2.812 trillion gross and $1.805 trillion net, so Form PF gross repo is also a different stock from collateral sitting in dealers’ repledgeable footnotes.
SOURCE URL: https://www.financialresearch.gov/hedge-fund-monitor/categories/leverage/chart-34/
QUOTE: "post securities collateral when they want to borrow cash"
UNCERTAIN: The OFR chart page still defines cash collateral as including Treasuries and agencies, while the April 2025 Form PF separates them, and the published series has no break at the June 2025 compliance date. An OFR crosswalk for post-amendment question 43 would settle whether the 2026 “cash” print still contains Treasuries.

CLAIM: V4
VERDICT: FALLS
REASON: $13 / ($7.3 + $2.7) = 1.30 and $13 / ($7.3 + $1.6) = 1.46 only if about $7.3 trillion of hedge-fund “source” is accepted. Re-derived 31 March 2026 Form PF prints are securities $4.956 trillion, cash $2.940 trillion, and other $0.369 trillion. Securities alone plus a $1.6 trillion lending leg is $6.56 trillion, and $13 / $6.56 = 1.98, which is Singh’s stated “near 2.0” on a roughly $13 trillion pool (implied sources $6.5 trillion). The drop to 1.30–1.46 comes from treating about three-quarters of the non-securities residual as extra source collateral, using wedges that include a $500 billion cash allowance and a $300 billion CCP ceiling. The same January numerator against a June Form PF leg is what produces the mixed-date 1.18–1.31; JPMorgan’s permitted stock alone went from $1,829.9 billion at 30 September 2025 to $2,181.4 billion at 30 June 2026.
SOURCE URL: https://www.risk.net/comment/7962922/collateral-velocity-is-vanishing-behind-a-digital-curtain
QUOTE: "the collateral velocity has remained near 2.0"
UNCERTAIN: The $1.6–2.7 trillion lending leg was not re-derived. ISLA’s page shows €3.9 trillion on loan at 31 March 2026, but the client-type shares are in a chart the HTML did not carry. The overlap between that on-loan stock and Form PF collateral posted is inferred. The DataLend client-type series, and Singh’s own gross-versus-net rule, would settle the denominator.

CLAIM: V5
VERDICT: WEAKENED
REASON: Table 2’s hedge-fund column does go 1.85, 1.9, 2.0, 2.1, 2.2. The annual steps are 2.7%, 5.3%, 5.0%, and 4.8%: mean 4.4%, not about 5%, with a population standard deviation of 1.01 percentage points. Form PF all-collateral posted, re-derived as securities plus cash plus other, steps 10.3%, 0.6%, 5.3%, and 19.1%, standard deviation 6.84 percentage points. Four steps on a series printed to the nearest $0.05–0.10 trillion will look smooth even if measured. What does support an estimate is an earlier paper: the end-2012 hedge-fund source is built as AUM times a leverage and long/short formula, and that table is sourced to “IMF staff estimates.” The 2019 source line instead cites the Risk Management Association, Singh (2011), and Canadian-bank updates.
SOURCE URL: https://www.imf.org/external/pubs/ft/wp/2013/wp13186.pdf
QUOTE: "US$2.4 trillion x leverage of 1.5 x 33 percent"
UNCERTAIN: It is inferred that the 2012 AUM formula was still the 2013–17 method. Singh’s worksheet, or a statement of whether those five prints are rounded measurements, would settle it.

The claim most likely to be wrong is V4. V1 matches the paper’s “could be re-pledged” wording and JPMorgan’s two footnote lines. V3’s repo-versus-cash comparison is true and was re-derived, but it does not identify extra source collateral. V4 turns that step into 1.30–1.46. On the March 2026 securities print alone, $4.956 trillion plus a $1.6 trillion lending leg is $6.56 trillion, and $13 trillion divided by that is 1.98.

---

## R1 — Hyperscaler 2026 bond issuance (find)

I'll measure 2026 hyperscaler bond issuance from primary filings and IR pages, then trace the $750bn figure. First I'll load the web-search tools and start from company and SEC sources.Search hits show several large 2026 deals. I'll fetch the SEC filings and check for later issues, non-USD deals, and project vehicles that the first pass may have missed.Several non-dollar deals and the $750bn figure still need primary pages. I'll pull the SEC filings and the Goldman and S&P sources next.EDGAR lists the parent 8-Ks. I'll read those filings, plus the Swiss-franc, Australian-dollar, and project-vehicle deals that did not show up as ordinary 8-Ks.Parent-company bonds priced or closed from 1 January through the latest filings visible on 13 October 2026 come to **$157 billion of US-dollar face**, plus large euro, sterling, Canadian-dollar, Swiss-franc, yen and Australian-dollar issues. That is not about $750 billion of new debt. The $750 billion figure, in the sources below, is a **2026 capital-expenditure forecast**. Goldman Sachs’ own bond forecast for these five companies is about **$250 billion** of direct investment-grade issuance, project finance excluded.

Dates below are **pricing dates** when a term sheet or prospectus states one, otherwise the **closing date** in the filing. Amounts are **face (aggregate principal)**, not proceeds. All five issuers below are the parent unless the vehicle column says otherwise.

## Deals

| Date | Issuer | Vehicle | Currency | Face | Tenors | Source | Quote |
|---|---|---|---|---|---|---|---|
| 9 Feb 2026 (settled 13 Feb) | Alphabet Inc. | Parent | USD | $20 billion | 3.700% 2029 $2.5bn; 4.100% 2031 $3bn; 4.400% 2033 $3bn; 4.800% 2036 $4.25bn; 5.500% 2046 $1.5bn; 5.650% 2056 $4bn; 5.750% 2066 $1.75bn. Maturities 15 Feb of each year. | https://www.sec.gov/Archives/edgar/data/1652044/000119312526043127/d297481dfwp.htm | “Trade Date: February 9, 2026” and “2029 Notes: $2,500,000,000 … 2066 Notes: $1,750,000,000” |
| 10 Feb 2026 (settled 13 Feb) | Alphabet Inc. | Parent | GBP | £5.5 billion | 4.125% 13 Feb 2029 £750m; 4.625% 13 Nov 2032 £1.25bn; 5.500% 13 Nov 2041 £1.25bn; 5.875% 13 Feb 2058 £1.25bn; 6.125% 13 Feb 2126 £1bn | https://www.sec.gov/Archives/edgar/data/1652044/000119312526044473/d37599dfwp.htm | “Trade Date: February 10, 2026” and “2126 Notes: £1,000,000,000” |
| On or around 3 Mar 2026 (counsel note dated 10 Feb) | Alphabet Inc. | Parent | CHF | CHF 3.055 billion | 0.4270% 2029 CHF 905m; 0.8900% 2032 CHF 700m; 1.2525% 2036 CHF 575m; 1.5823% 2041 CHF 455m; 1.8675% 2051 CHF 420m | https://www.clearygottlieb.com/news-and-insights/news-listing/alphabet-in-record-inaugural-5-5-billion-and-chf-3-055-billion-bonds-issuances | “unregistered offering of CHF 3.055 billion … scheduled to close on or …” |
| 5 May 2026 (settled 11 May) | Alphabet Inc. | Parent | EUR | €9 billion | 3.200% 11 May 2030 €1.5bn; 3.450% 2032 €1.75bn; 3.625% 2034 €1.5bn; 4.100% 2039 €1.75bn; 4.500% 2045 €1.25bn; 4.800% 2063 €1.25bn | https://www.sec.gov/Archives/edgar/data/1652044/000119312526216986/d109021d8k.htm | “closed its concurrent underwritten public offerings of €9 billion aggregate principal amount …” |
| 5 May 2026 (settled 11 May) | Alphabet Inc. | Parent | CAD | C$8.5 billion | 3.650% 15 May 2031 C$1.5bn; 4.000% 2033 C$2bn; 4.350% 2036 C$2.25bn; 5.000% 2056 C$2.75bn | https://www.sec.gov/Archives/edgar/data/1652044/000119312526212222/d325417d424b2.htm | “C$8,500,000,000 … The date of this prospectus supplement is May 5, 2026.” |
| 21 May 2026 close (priced 15 May per the free-writing prospectus) | Alphabet Inc. | Parent | JPY | ¥576.5 billion on the tranche list | 1.965% 2029 ¥135.5bn; 2.412% 2031 ¥200.5bn; 2.822% 2033 ¥123.2bn; 3.189% 2036 ¥64.9bn; 3.713% 2041 ¥19.1bn; 4.395% 2056 ¥9.3bn; 4.599% 2066 ¥24.0bn | https://www.sec.gov/Archives/edgar/data/1652044/000119312526234488/d144566d8k.htm | “¥135,500,000,000 aggregate principal amount of 1.965% notes due 2029 … ¥24,000,000,000 aggregate …” |
| 6 Aug 2026 prospectus date; closed 10 Aug | Alphabet Inc. | Parent | USD | $25 billion | FRN 2028 $750m (SOFR+0.44%); 4.500% 2028 $1.25bn; FRN 2029 $500m (SOFR+0.60%); 4.625% 2029 $2bn; 4.875% 2031 $3.5bn; 5.200% 2033 $2.5bn; 5.450% 2036 $4.5bn; 6.250% 2046 $3bn; 6.375% 2056 $4.5bn; 6.500% 2066 $2.5bn | https://www.sec.gov/Archives/edgar/data/1652044/000119312526342390/d171253d8k.htm | “closed its underwritten public offering of $25 billion aggregate principal amount of …” |
| 27 Aug 2026 close | Alphabet Inc. | Parent | AUD | A$5.5 billion | 5.20% 2029 A$500m; FRN 2029 A$750m; 5.50% 2031 A$750m; FRN 2031 A$1.5bn; 6.25% 2036 A$1bn; 6.90% 2046 A$1bn | https://www.clearygottlieb.com/news-and-insights/news-listing/alphabet-in-inaugural-a-5-5-billion-aud-denominated-bonds-offering | “inaugural unregistered offering of A$5.5 billion … The offering closed on August 27, 2026.” |
| 10 Mar 2026 underwriting agreement; closed 13 Mar | Amazon.com, Inc. | Parent | USD | $37 billion face (public offering price $36.898 billion) | FRN 2028 $1.75bn; FRN 2029 $1bn; 3.850% 2028 $2.25bn; 4.000% 2029 $3bn; 4.250% 2031 $5bn; 4.550% 2033 $4bn; 4.875% 2036 $6bn; 5.650% 2046 $2.5bn; 5.800% 2056 $5.5bn; 5.950% 2066 $3bn; 6.050% 2076 $3bn | https://www.sec.gov/Archives/edgar/data/1018724/000110465926027729/tm266670d8_8k.htm | “closed the sale of $1,750,000,000 aggregate principal amount of its floating rate …” |
| 11 Mar 2026 underwriting agreement; closed 16 Mar | Amazon.com, Inc. | Parent | EUR | €14.5 billion face (public offering price €14.473 billion) | FRN 2028 €1.75bn; 2.800% 2028 €1.25bn; 3.100% 2030 €2bn; 3.350% 2032 €2.25bn; 3.700% 2035 €2.5bn; 4.050% 2039 €2.25bn; 4.450% 2045 €1.25bn; 4.850% 2064 €1.25bn | https://www.sec.gov/Archives/edgar/data/1018724/000110465926028556/tm266670d9_8k.htm | “closed the sale of €1,750,000,000 aggregate principal amount of its floating rate …” |
| 28 May 2026 issue date | Amazon.com, Inc. | Parent | CHF | CHF 2.82 billion | 0.8350% 2029 CHF 900m; 1.200% 2032 CHF 585m; 1.4475% 2035 CHF 475m; 1.6750% 2038 CHF 390m; 1.9389% 2044 CHF 245m; 2.0825% 2051 CHF 225m | https://homburger.ch/en/news/homburger-advises-amazon-on-its-issuance-of-chf-2-82-bn-in-inaugural-six-tranche-chf-offering | “On May 28, 2026, Amazon.com, Inc. issued bonds in Switzerland in the …” |
| 8 Jun 2026 underwriting agreement; closed 12 Jun | Amazon.com, Inc. | Parent | CAD | C$14 billion face (public offering price C$13.967 billion) | 3.400% 2029 C$1.25bn; 3.700% 2031 C$2.5bn; 4.000% 2033 C$2bn; 4.350% 2036 C$3.5bn; 5.000% 2056 C$4.75bn | https://www.sec.gov/Archives/edgar/data/1018724/000110465926073562/tm2613616d5_8k.htm | “closed the sale of C$1,250,000,000 aggregate principal amount of its 3.400% notes …” |
| 7 Jul 2026 (settled 9 Jul) | Amazon.com, Inc. | Parent | USD | $25 billion | FRN 9 Jul 2029 $750m (SOFR+0.58%); 4.600% 2029 $3.5bn; 4.800% 2031 $4.25bn; 5.100% 2033 $3bn; 5.300% 2036 $4.5bn; 6.000% 2046 $2.75bn; 6.100% 2056 $4bn; 6.250% 2066 $2.25bn. Fixed maturities 9 Jul. | https://www.sec.gov/Archives/edgar/data/1018724/000110465926081334/tm2619352d3_fwp.htm | “Trade Date: July 7, 2026” and “2029 Notes: $3,500,000,000 … 2066 Notes: $2,250,000,000” |
| 9 Sep 2026 underwriting agreement; closed 14 Sep | Amazon.com, Inc. | Parent | GBP | £4.25 billion face (public offering price £4.242 billion) | 5.200% 2029 £1.25bn; 5.550% 2032 £1bn; 6.250% 2038 £1bn; 6.650% 2045 £1bn | https://www.sec.gov/Archives/edgar/data/1018724/000110465926107526/tm2624614d5_8k.htm | “closed the sale of £1,250,000,000 aggregate principal amount of its 5.200% notes …” |
| 30 Apr 2026 (settled 4 May) | Meta Platforms, Inc. | Parent | USD | $25 billion | 4.550% 15 May 2031 $3bn; 4.875% 2033 $2bn; 5.250% 2036 $6bn; 6.200% 2046 $4bn; 6.300% 2056 $6bn; 6.450% 2066 $4bn | https://www.sec.gov/Archives/edgar/data/1326801/000119312526204128/d134616d8k.htm | “completed an offering of $3,000,000,000 aggregate principal amount of its 4.550% Senior …” |
| 28 Jul 2026 announcement; close described as still ahead | Meta Platforms, Inc. with BlackRock | JV (80% BlackRock funds / 20% Meta). Issuer legal name not in the release. | USD | $12.5 billion debt financing | Not stated. Meta lease: 4-year initial term plus four extensions, up to 20 years. RVG threshold about $13 billion. | https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Announces-New-Strategic-Venture-with-BlackRock-to-Develop-Data-Center-in-El-Paso/default.aspx | “A portion of BlackRock's investment will be funded with proceeds from a …” |
| 2 Feb 2026 (settled 4 Feb) | Oracle Corporation | Parent | USD | $25 billion | FRN 4 Feb 2029 $500m (SOFR+1.11%); 4.550% 2029 $3bn; 4.950% 2031 $3.5bn; 5.350% 4 May 2033 $3bn; 5.700% 2036 $5bn; 6.550% 2046 $2.25bn; 6.700% 2056 $5bn; 6.850% 2066 $2.75bn | https://www.sec.gov/Archives/edgar/data/1341439/000119312526033882/d44245dfwp.htm | “Trade Date: February 2, 2026” and “$2,750,000,000 of 6.850% Notes due 2066” |
| None found | Microsoft Corporation | Parent | — | — | — | https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=8-K&dateb=20261014&datea=20260101&owner=include&count=40 | EDGAR 8-K list from 1 Jan 2026 through the 2 Sep 2026 filing: earnings, directors, and Regulation FD. No notes offering. |

Microsoft has no row because that EDGAR list contains no 2026 notes offering.

## Totals

Parent face, by currency. Not converted to dollars.

| Company | Parent | Other (JV / project vehicle) |
|---|---|---|
| Alphabet | $45bn; £5.5bn; €9bn; C$8.5bn; ¥576.5bn; CHF 3.055bn; A$5.5bn | None found |
| Amazon | $62bn; €14.5bn; C$14bn; £4.25bn; CHF 2.82bn | None found |
| Meta | $25bn | $12.5bn debt financing for the El Paso JV (press release; not Meta’s own notes) |
| Microsoft | None found | None found |
| Oracle | $25bn | None found |
| **Five parents, USD only** | **$157 billion** | **$12.5 billion** stated for the Meta/BlackRock financing |

Dollar-denominated parent face is $45bn Alphabet + $62bn Amazon + $25bn Meta + $25bn Oracle. Adding the other currencies at any plausible exchange rate still leaves the total well short of $750 billion, and in the neighborhood of the roughly $250 billion full-year bond forecast below. A single dollar total is not stated here because the filings do not publish one set of exchange rates for every deal.

## The $750 billion and $2 trillion figures

**$750 billion is a capex forecast, not a borrowing forecast.**

Yahoo Finance, 28 July 2026, reporting a Goldman Sachs credit note led by Amanda Lynam: “By year end for 2026, that figure is expected to reach $750 …” The same article says the debt piece is separate: “expected to reach roughly $250 billion in debt issuance, or roughly 33% of capex.” It also says those bond figures leave out off-balance-sheet debt, leases (about $1.2 trillion disclosed, of which $725 billion not yet begun), and about $412 billion of 2026 AI-linked debt outside the hyperscalers. https://finance.yahoo.com/markets/article/big-tech-will-fund-more-than-a-third-of-its-ai-investments-with-debt-in-2027-goldman-sachs-predicts-145136150.html

Goldman Sachs’ own Exchanges page, recorded 3 August 2026, says the same split in Goldman’s voice: “we’re bracing for something like $250 billion of direct supply from the …” Hyperscalers had issued $194 billion so far in 2026 against $108 billion in all of 2025. https://www.goldmansachs.com/insights/goldman-sachs-exchanges/how-ai-debt-is-reshaping-the-credit-market

S&P is also talking about spending. The DESK, 27 May 2026, citing an S&P report: “In 2026, S&P Global predicts that the five largest cloud service providers …” The same piece says direct debt issuance from US hyperscalers was $115 billion in the first quarter of 2026, versus $70 billion in all of 2025. https://www.fi-desk.com/ratings-analysis-hyperscaler-spending-rings-credit-alarm-bells/

S&P’s 27 August 2026 press release does not repeat $750 billion. It says combined hyperscaler capex, for Alphabet, Amazon, Microsoft, Meta, Oracle **and SpaceX**, is “projected to exceed $1.3 trillion by 2027,” and that debt, leases, guarantees and joint ventures are part of the funding. https://press.spglobal.com/2026-08-27-AI-Infrastructure-Investment-To-Exceed-1-3-Trillion-By-2027,-S-P-Global-Ratings-Says

**$2 trillion is debt capacity, or a multi-year AI funding stack, not 2026 hyperscaler bonds.**

On the same Goldman Exchanges page, Lynam’s leverage exercise is: “That implies around the ballpark of $2 trillion of incremental debt capacity.” That is how much debt the hyperscalers could add and remain around two times net leverage or three times gross leverage. The Yahoo write-up of the research note puts the four names excluding Oracle at $1.3–1.4 trillion of capacity at two times net leverage. Neither number is a 2026 issuance plan.

J.P. Morgan Asset Management, 20 August 2026, uses $2.1 trillion for a different object: “Investment-grade bonds are expected to be the largest source of external capital …” against cumulative AI-related investment of $5.5 trillion by 2030, plus $700 billion from high-yield, leveraged loans and securitisation. The near-term hyperscaler line in that note is “USD 300 billion in investment-grade bonds over the next year,” and year-to-date issuance of $219 billion, of which $62 billion equivalent was non-dollar. https://am.jpmorgan.com/dk/en/asset-management/liq/insights/market-insights/market-updates/on-the-minds-of-investors/hyperscaler-debt-issuance-ai-buildout/

## UNCERTAIN

- **Alphabet Canadian-dollar total.** The 11 May 8-K says “C$9.5 billion,” but the four tranches in that same 8-K sum to C$8.5 billion, the prospectus supplement is titled C$8,500,000,000, and Cleary says C$8.5 billion. The table uses C$8.5 billion. A fifth tranche, if it exists, is not in the exhibits.
- **Alphabet yen total.** The 21 May 8-K says “¥576.9 billion,” but the seven tranches in that 8-K sum to ¥576.5 billion, which is also Cleary’s figure. The table uses the tranche sum.
- **Alphabet Swiss francs and Australian dollars** are counsel announcements (Cleary; Homburger was used for Amazon, not for Alphabet’s close). The sterling term sheet confirms a concurrent Swiss-franc offering was launched. Neither deal appears as its own 8-K in the Alphabet EDGAR list fetched through 14 October 2026. The latest Alphabet 8-K on that list is 10 August, before the 27 August Australian-dollar close. Reading the first-quarter and third-quarter 10-Q debt footnotes would confirm both closes and the exact Swiss-franc pricing date.
- **Amazon Swiss-franc pricing date.** Homburger states the issue date, 28 May 2026, not the trade date.
- **El Paso / Sopaipilla.** Meta’s release states a $12.5 billion debt financing, an 80/20 BlackRock/Meta venture, and leases. It does not name the issuer, the coupon, or the maturity, and it says the transaction was still expected to close. Trade-press figures (issuer name Sopaipilla Investor LLC, about $12.547 billion, 7.534%, due 30 November 2048, priced 27 July) were not confirmed from a filing fetched in this session. A prospectus, 144A offering memorandum, or rating report would settle the bond terms. This amount is kept out of parent debt.
- **Beignet / Hyperion.** No 2026 Meta 8-K or prospectus for that vehicle turned up. Secondary accounts place the roughly $27.3 billion Beignet bond in October 2025, outside this window. A 2025 offering document would settle the exclusion.
- **Amazon 10 June 2026 8-K** (items 1.01, 2.03 and 9.01) is on the EDGAR list and was not opened. Item 2.03 can be a loan or a bond. Opening accession 0001104659-26-072140 would settle it.
- **Microsoft.** No parent notes 8-K or 424B appeared. An unregistered private placement that was not filed, or a financing subsidiary that does not file under Microsoft’s CIK, would not show on that list. The fiscal-2026 Form 10-K long-term-debt note would settle parent issuance through 30 June 2026.
- **Landlord and loan paper** (QTS bonds with Microsoft, Meta or Oracle as tenants; reported Oracle project loans) is not the hyperscaler’s own bond and is not in the table.
- **Oracle’s February 2026 mandatory convertible preferred** is equity, not a bond, and is excluded.
- **Exchange rates.** Company filings give face in the issue currency. A single dollar sum of the non-dollar deals was not computed.

---

## R2 — Free term-premium series outside the US (find)

I'll look up free official term-premium series for Japan, the euro area, the UK, and the two US benchmarks, using primary publishers only.The first pass found the two US series and several yield curves, but not downloadable non-US term premia. I’ll fetch the official pages and search the central-bank publishers more narrowly.The US files look real; the non-US hits are mostly charts. I’ll open the publisher pages and a few academic downloads to see which ones are actual time series.The project’s R3 note still holds for an official, maintained file: no central bank publishes a free, updated term-premium time series for JGBs, Bunds, the euro-area AAA curve, or gilts. One researcher-maintained Japan file is free and current. The two US series are live and free. Assumption: “most useful” means a free file that splits a non-US long government yield into expected short rates and a term premium, and that is still being updated.

**ACM 10-year Treasury term premium, monthly chart file**
PUBLISHER: Federal Reserve Bank of New York, Research and Statistics / Applied Macroeconomics and Econometrics Center.
METHOD: Five-factor no-arbitrage model of Adrian, Crump and Moench (2013), fitted to Gürkaynak–Sack–Wright zero-coupon yields. The term premium is yield minus the expected average short rate.
FREQUENCY: The file that was read is monthly, month-end. The current data index says the release is updated daily. The authors’ 12 May 2014 post said the full download was updated weekly.
COVERAGE: 30 June 1961 through 30 September 2026 in the file that was read. On 30 September 2026 the term-premium column is about 0.89 and the fitted yield about 5.26, against a GSW yield of about 5.28. The 2014 post says the daily estimates run from 14 June 1961.
DOWNLOAD URL (fetched): https://www.newyorkfed.org/medialibrary/media/research/data_indicators/acmPlot_data.csv — index https://www.newyorkfed.org/research/data_indicators — method post https://libertystreeteconomics.newyorkfed.org/2014/05/treasury-term-premia-1961-present/
FORMAT: CSV. Header read: `RunDates,TERMYld,ACMFITYld,GSWYld`. The header does not name the maturity. The 2014 post identifies this chart as the ten-year ACM yield against the ten-year GSW yield.
TERMS: General New York Fed website licence, fetched at https://www.newyorkfed.org/privacy/termsofuse.html. Term premia are not in the extra restricted-content list. Use requires the New York Fed attribution. Not public domain.
QUOTE: “Treasury Term Premia (Updated: Daily)”

**Kim–Wright Treasury term premium (THREEFYTP10 and the full 1–10 year set)**
PUBLISHER: Board of Governors of the Federal Reserve System. Staff research product.
METHOD: Three-factor affine Gaussian no-arbitrage model, as in Kim and Wright (FEDS 2005-33), using Kim and Orphanides survey augmentation. Survey forecasts of the three-month T-bill are a noisy proxy. Term premium equals yield minus the expected average short rate, and includes the convexity premium. Parameters are rarely re-estimated; this file uses the re-estimate that includes effective-lower-bound years, not the pre-crisis parameters. The old file location moved on 5 November 2019.
FREQUENCY: Daily observations. The Board says it generally posts once a week, typically Tuesday, through the previous Friday.
COVERAGE: The paper and the current model page start in 1990. The HTML table fetched now is reverse-chronological and its newest row is 2 October 2026. On that date `THREEFYTP1000.B`, the ten-year zero-coupon term premium, is 1.0847. An earlier fetch in this session of FRED series THREEFYTP10 showed 2 January 1990 through 2 October 2026, updated 6 October 2026. A repeat fetch of that FRED page timed out, so that FRED end date was not re-read.
DOWNLOAD URL (fetched): model page https://www.federalreserve.gov/data/three-factor-nominal-term-structure-model.htm — HTML table https://www.federalreserve.gov/data/yield-curve-tables/feds200533_1.html — move note https://www.federalreserve.gov/pubs/feds/2005/200533/200533abs.html — FRED mirror https://fred.stlouisfed.org/series/THREEFYTP10
FORMAT: The model page offers CSV and HTML. The HTML tables were read (forwards, forward premia, fitted yields, and yield premia, 1–10 years, percentage points). The CSV bytes were not read. FRED carries only the ten-year yield term premium, not the other 39 columns. ACM is not that FRED series: ACMTP10 returned HTTP 404 earlier in this session.
TERMS: https://www.federalreserve.gov/disclaimer.htm — Board website material is in the public domain unless indicated otherwise; cite the Board. The model page adds that this is not an official statistical release and may be delayed or revised without notice. The FRB/US model disclaimer on the same page does not mention this term-structure file.
QUOTE: “not an official Federal Reserve statistical release”

**Nakajima shadow rate, term premiums and expected rates, Japan**
PUBLISHER: Jouchi Nakajima, on his own site and on the Japan’s Monetary Policy Database. Grant-in-Aid 23H00050 (MEXT). Explicitly not the Bank of Japan.
METHOD: Term-structure model with an effective lower bound. The page cites Ichiue and Ueno, Bank of Japan Working Paper 13-E-8 (2013), and Nakajima, Hitotsubashi Discussion Paper A.760 (2025). The 2013 paper, fetched at https://www.boj.or.jp/en/research/wps_rev/wps_2013/wp13e08.htm, estimates an affine model and a shadow-rate model for Japan, the US and the UK through March 2013 and offers a PDF only, not a data file.
FREQUENCY: Daily and monthly files. Updated every quarter. Past figures are revised.
COVERAGE: January 1995 through September 2026, updated October 2026, on both pages fetched now. A web-search snippet still said June or July 2026; the fetched pages supersede that.
DOWNLOAD URL (fetched): https://sites.google.com/site/jnakajimaweb/yield and https://sites.google.com/view/jpmpdata/ — the pages name `yield_M.csv` and `yield_D.csv`. A guessed direct URL for `yield_M.csv` returned HTTP 404, so the file bytes were not read.
FORMAT: CSV, as named on the page. Column layout, maturities and units were not read.
TERMS: Cite the papers. Not the official view of the Bank of Japan. Use at the user’s own risk. No standard open-data licence was stated.
QUOTE: “not the official view of the Bank of Japan”

**Wright international forward term premiums (Japan, Germany, United Kingdom, and seven other countries)**
PUBLISHER: Jonathan H. Wright. The estimates are in FEDS 2008-25 and *American Economic Review*, June 2011. This is an academic replication dataset, not a central-bank data product.
METHOD: Two decompositions of the five-to-ten-year forward rate: a homoskedastic affine model with three yield principal components, and a survey method that maps Consensus long-horizon inflation and growth forecasts into expected short rates using a US Blue Chip regression.
FREQUENCY: Monthly, end-of-month, in the paper.
COVERAGE: Yield curves from January 1990 to December 2007. Japan, Germany and the United Kingdom are in the ten-country panel. The sample is frozen. It does not cover the 2023–26 window in R3.
DOWNLOAD URL (fetched): paper text https://www.federalreserve.gov/pubs/feds/2008/200825/index.html — faculty page listing “Excel Data” https://econ.jhu.edu/directory/jonathan-wright/ — article page https://www.aeaweb.org/articles?id=10.1257/aer.101.4.1514 — openICPSR record https://www.openicpsr.org/openicpsr/project/112438/view stopped at a bot check, so the workbook was not opened. The Excel href on the faculty page was not recovered.
FORMAT: Excel, as labelled on the faculty page. Bytes not read.
TERMS: Not read. The openICPSR download was not completed.
QUOTE: “January 1990 to December 2007 for ten industrialized countries”

**Euro area: ECB staff decomposition of the ten-year OIS rate — chart, not a file**
PUBLISHER: Philip R. Lane, ECB Executive Board, speech of 11 June 2025. Personal views, not the Governing Council.
METHOD: Two affine models, with and without surveys, following Joslin, Singleton and Zhu (2011), plus a lower-bound model following Geiger and Schupp, Bundesbank Discussion Paper 27/2018. This decomposes the euro-area risk-free OIS rate, not the Bund yield and not the ECB AAA curve.
FREQUENCY: Not a published series. Chart observations through 10 June 2025.
COVERAGE: The speech discusses the euro period through that date. No start date for a downloadable file, because there is no file.
DOWNLOAD URL (fetched): https://www.ecb.europa.eu/press/key/date/2025/html/ecb.sp250611_1~cd38594925.en.html — no spreadsheet link.
FORMAT: HTML speech and charts.
TERMS: “Reproduction is permitted provided that the source is acknowledged.”
QUOTE: “The latest observations are for 10 June 2025.”

**Germany: Bundesbank term structure — yields, not a term premium**
PUBLISHER: Deutsche Bundesbank.
METHOD: Estimated default-free zero-coupon curve from observed coupon-bond yields. That is a fitted yield curve.
FREQUENCY: The fetched page does not state it; it is the statistical term-structure release.
COVERAGE: Not a premium series.
DOWNLOAD URL (fetched): https://www.bundesbank.de/en/statistics/money-and-capital-markets/interest-rates-and-yields/term-structure-of-interest-rates/term-structure-of-interest-rates-793592 — no term-premium file on that page.
FORMAT: The page points to statistical tables. No premium file was linked.
TERMS: Not read on that page.
QUOTE: “estimated values calculated on the basis of observed yields”

**United Kingdom: Bank of England gilt decomposition — chart, not a file**
PUBLISHER: Bank of England staff, Bank Insights, 23 January 2026 (Panigrahi and Sidhu).
METHOD: Internal term-structure models, named as Malik and Meldrum (2016), Vlieghe (2016) and Andreasen and Meldrum (2015), plus an inflation-risk-premium model adapted from Joslin, Singleton and Zhu (2011) and Kim and Orphanides (2012). Chart 4 is the change in the five-year, five-year-forward gilt yield since January 2025, not a level history.
FREQUENCY: Not a published series. Chart data updated to 18 December 2025.
COVERAGE: Changes over 2025 only, in the chart that was described.
DOWNLOAD URL (fetched): https://www.bankofengland.co.uk/bank-insights/2026/what-were-the-drivers-of-uk-long-term-interest-rates-in-2025 — sources named as Bloomberg, Consensus Economics, ONS, Tradeweb and Bank calculations. No spreadsheet.
FORMAT: HTML article and charts.
TERMS: Not separately stated on the fetched page.
QUOTE: “Data updated to 18 December 2025.”

**BIS euro-area and US estimates, September 2018 — article, not a file**
PUBLISHER: BIS Quarterly Review, Cohen, Hördahl and Xia, 23 September 2018. Authors’ views, not necessarily the BIS.
METHOD: Comparison of ACM, Kim–Wright, and Hördahl–Tristani (2014). For the euro area, the ACM-style estimate uses the German ten-year, Hördahl–Tristani uses the French ten-year, and a Banque de France model uses ten-year EONIA OIS.
FREQUENCY: One article. Charts, not an updated file.
COVERAGE: The text discusses the sample through about mid-2018. No end date of a downloadable series, because none is linked.
DOWNLOAD URL (fetched): https://www.bis.org/publ/qtrpdf/r_qt1809h.htm — no data file.
FORMAT: HTML article and graphs.
TERMS: Authors’ views, not necessarily those of the BIS.
QUOTE: “estimate term premia on US and euro area bonds”

**Ranked shortlist**

1. Nakajima’s Japan shadow-rate file. It is the only free, still-updated split of a JGB curve into expected rates and a term premium that turned up. It is not an official BoJ series, and history is revised each quarter.
2. Wright’s 1990–2007 panel, if the Excel on his faculty page or the AEA replication package can be opened. It is the only free decomposition found that covers Japan, Germany and the UK together. It stops in 2007, so it cannot measure the rise R3 is studying.
3. There is no third series. ECB, Bundesbank, Bank of England and BIS publish decompositions as charts or as a one-off article. The Bundesbank Svensson curve, the ECB AAA curve and the Bank of England gilt curve are yields, which R3 already uses. They are not term premia. ACM and Kim–Wright remain the live US benchmarks R1 already pulls; they do not fill the JGB, Bund or gilt hole.

NIESR’s quarterly Term Premium Tracker (Q3 2026 PDF fetched as a lead) estimates UK, US and some European premia with an ACM-style model through 30 September, but it is a PDF, not a time-series file, it is not a central bank, and its European yields are from Datastream.

**UNCERTAIN**

- The New York Fed multi-maturity daily workbook. The index says “Updated: Daily”; the 2014 post says the 1–10 year daily file, including fitted yields and expected short rates, was updated weekly. A fetch of `ACMTermPremium.xls` returned HTTP 500, so that filename was not confirmed. The tabs page at https://www.newyorkfed.org/research/data_indicators/term-premia-tabs did not render its download links. Opening that page in a browser would settle the filename, the maturity labels, and the latest daily date.
- The ACM chart CSV header does not say “10-year”. The maturity is inferred because the 2014 post describes that chart as the ten-year comparison and the columns match it.
- The Kim–Wright CSV filename. The model page says “Data: CSV | HTML”, but the link target was stripped in the fetch. A guessed `feds200533.csv` path returned HTTP 500 earlier in this session. The HTML tables are the copy that was actually read.
- Whether the Board has posted a Kim–Wright update since 2 October 2026. Today is Tuesday 13 October 2026, which is the usual posting day for data through Friday 9 October. The HTML fetched now still ends on 2 October 2026.
- Nakajima’s column names, maturities and units. Both landing pages name the CSVs; the file itself was not read. A direct download from the Google Sites link, opened in a browser, would settle that.
- Wright’s Excel URL, the last date inside the file, and whether the AEA or openICPSR package downloads without a login. The paper’s yield sample ends in December 2007. openICPSR stopped at a bot check and was not bypassed.
- Whether a BoE, ECB, Bundesbank or BIS spreadsheet exists on a page that these searches did not find. The pages that were fetched contain charts or yield curves, not a premium file.

---

## R3 — Derivatives as a market-structure flow (find)

**Cited but not fetched in this call (not relied on):** https://marketdata.theocc.com/daily-open-interest?...&action=download&format=csv; https://marketdata.theocc.com/daily-volume-statistics?reportDate=YYYYMMDD&format=csv; https://marketdata.theocc.com/exchange-volume?...&instrumentType=options&format=txt; https://marketdata.theocc.com/monthly-volume-reports?reportDate=YYYYMMDD&reportType=options&reportClass=equity&format=csv; https://marketdata.theocc.com/onn-volume-search?productKind=options&underlying=ibm&reportType=D&reportDate=YYYYMMDD&reportFormat=percent&reportView=raw; https://marketdata.theocc.com/volume-query?...&format=csv; https://www.cmegroup.com/market-data/browse-data/exchange-volume.html; https://www.cmegroup.com/market-data/volume-open-interest.html; https://www.direxion.com/holdings/{TICKER}.csv

I'll look up free official sources for equity-options volume, open interest, zero-day share, dealer gamma, and leveraged-ETF flows, plus 2023–2026 regulator research on whether those flows move the underlying. First I'll check the project repo and the primary publisher pages.The project can measure listed-options volume from free OCC and Cboe files, and leveraged-ETF exposure from issuer holdings files. It cannot download a free official series of zero-days-to-expiry (0DTE) share, dealer gamma, or options volume divided by share volume. CME’s pages did not load. Assumption: a usable source is a public file with no login, and a commercial-use ban still counts against the project’s free-data standard.

## DATA

**SOURCE:** OCC volume query (industry cleared volume, by symbol)  
**MEASURES:** Cleared contract volume. Parameters on the page: `volumeQueryType` O or F; `symbolType` ALL/O/U; `reportType` D/W/M; `accountType` ALL/C/F/M (customer, firm, market maker); `productKind` ALL/ODBT/OIND/OSTK (debt, index, equity); `porc` BOTH/C/P; `contractDt` yyyymmdd.  
**FREQUENCY/HISTORY:** Daily, weekly, or monthly file per query. Documented example dates include 2016–2019. Archive start is not stated. A live CSV in this session returned HTTP 500, so the header was not read.  
**URL fetched:** https://www.theocc.com/market-data/market-data-reports/other-market-data-info/batch-processing/volume-query-batch-processing  
**ACCESS:** No login or key on the page. Documented route: `https://marketdata.theocc.com/volume-query?...&format=csv`.  
**TERMS:** Site terms, updated 5 February 2025, ban commercial copying and robots. The batch page tells users to script the same URLs. See UNCERTAIN.  
**QUOTE:** “The Services and the Data may not be reproduced, duplicated, copied, sold …” And: “you will not … use or launch any automated system, including ‘robots,’ …” Terms page: https://www.theocc.com/specialpages/legal/terms-and-conditions

**SOURCE:** OCC daily volume statistics, exchange volume, and monthly/weekly volume by class  
**MEASURES:** Aggregate daily volume; exchange volume for `instrumentType=options`; monthly and weekly volume with `reportClass` debt, equity, etf, or index, and `reportType` options or futures.  
**FREQUENCY/HISTORY:** Daily and monthly. Example `reportDate=20190531`. Start date not stated. Live daily-volume CSV returned HTTP 500.  
**URL fetched:** https://www.theocc.com/market-data/market-data-reports/other-market-data-info/batch-processing and https://www.theocc.com/market-data/market-data-reports/other-market-data-info/batch-processing/volume-statistics-monthly-batch-processing and https://www.theocc.com/specialpages/batch-processing-changes  
**ACCESS:** No login. Routes documented: `https://marketdata.theocc.com/daily-volume-statistics?reportDate=YYYYMMDD&format=csv`; `https://marketdata.theocc.com/monthly-volume-reports?reportDate=YYYYMMDD&reportType=options&reportClass=equity&format=csv`; `https://marketdata.theocc.com/exchange-volume?...&instrumentType=options&format=txt`.  
**TERMS:** Same OCC terms as above.  
**QUOTE:** “Please refer to the URLs and parameters listed below to set up your scripts.” Monthly parameters: `reportClass: debt equity etf index`.

**SOURCE:** OCC daily open interest  
**MEASURES:** Open interest for a report date. The page does not say whether the file is aggregate or series-level.  
**FREQUENCY/HISTORY:** Daily. The documented example uses 27 January 2026. Start date not stated.  
**URL fetched:** https://www.theocc.com/market-data/market-data-reports/other-market-data-info/batch-processing/daily-open-interest  
**ACCESS:** No login. `https://marketdata.theocc.com/daily-open-interest?...&action=download&format=csv`. The parameter table says `dailyDate`; the example URL uses `reportDate`.  
**TERMS:** Same OCC terms.  
**QUOTE:** The page documents `action=download` and `format=csv` for a dated open-interest file.

**SOURCE:** OCC volume by account type (ONN)  
**MEASURES:** Options volume split by account type for one underlying, as raw counts or percent. This is volume, not inventory and not gamma.  
**FREQUENCY/HISTORY:** Daily (`reportType=D`).  
**URL fetched:** https://www.theocc.com/specialpages/batch-processing-changes  
**ACCESS:** No login. `https://marketdata.theocc.com/onn-volume-search?productKind=options&underlying=ibm&reportType=D&reportDate=YYYYMMDD&reportFormat=percent&reportView=raw`.  
**TERMS:** Same OCC terms.  
**QUOTE:** The migration page lists that ONN URL among the public batch routes.

**SOURCE:** Cboe daily market statistics  
**MEASURES:** Cboe-exchange volume and open interest, not OCC industry totals, by class: sum, index, ETP, equity, VIX, SPX+SPXW.  
**FREQUENCY/HISTORY:** A current snapshot. The fetched text has no trade date.  
**URL fetched:** https://www.cboe.com/markets/us/options/market-statistics/daily/  
**ACCESS:** No login. No history file on this page.  
**TERMS:** Cboe terms, last updated 16 November 2022: one copy for personal non-commercial use. The statistics page adds a no-accuracy-responsibility disclaimer.  
**QUOTE:** Fetched snapshot, undated in the extract: SUM volume 10,823,025 and open interest 676,696,344; INDEX 4,515,320 / 45,260,962; ETP 2,736,940 / 194,088,858; EQUITY 3,570,765 / 437,346,524; VIX 469,102 / 14,395,728; SPX+SPXW 3,719,155 / 23,622,151. Terms: “You may view, print and download one copy of the Materials for …” https://www.cboe.com/terms/

**SOURCE:** Cboe equity put/call CSV  
**MEASURES:** Cboe equity-option call volume, put volume, total, and put/call ratio. After 11 June 2012, equity volume excludes exchange-traded products. After 31 May 2012 the file is preliminary reported volume, not cleared volume.  
**FREQUENCY/HISTORY:** Daily. First row read: 11/1/2006. The fetch was truncated; the last row was not read.  
**URL fetched:** https://cdn.cboe.com/resources/options/volume_and_call_put_ratios/equitypc.csv and the archive pointer https://www.cboe.com/us/options/market_statistics/historical_data/  
**ACCESS:** No login. Direct CSV. The historical page says that from September 2019, equity-option volume history is on the Historical Options Data download page, and it lists monthly `.xls` files for January–August 2019 in the portion that rendered.  
**TERMS:** Cboe website terms above. The CSV carries its own volume-definition note.  
**QUOTE:** “As of June 11 2012 Equity Volume includes only the volume of …”

**SOURCE:** Cboe 0DTE product page  
**MEASURES:** A marketing snapshot of the share of SPX and XSP volume that traded 0DTE, and a growth figure since 2016. Not a downloadable series.  
**FREQUENCY/HISTORY:** One undated snapshot.  
**URL fetched:** https://www.cboe.com/en/tradable-products/0dte/  
**ACCESS:** No login.  
**TERMS:** Cboe website terms.  
**QUOTE:** “59% of SPX volume traded 0DTE”; “54% annual increase in SPX 0DTE volume since 2016”; “48% of XSP volume traded 0DTE.”

**SOURCE:** Cboe DataShop Open-Close Volume Summary  
**MEASURES:** Volume by customer, professional customer, broker-dealer, and market maker, and by buy/sell and open/close. This is the file academics use for dealer positioning. It is not gamma.  
**FREQUENCY/HISTORY:** C1 end-of-day from 2005-01-03; C1 10-minute from 2011-01-03.  
**URL fetched:** https://datashop.cboe.com/cboe-options-open-close-volume-summary  
**ACCESS:** Paid. SEC-filed LiveVol fees. Not a free source.  
**TERMS:** Internal use; redistribution of raw data is not allowed.  
**QUOTE:** “Raw data is licensed for internal use only and may not be …”

**SOURCE:** Nasdaq PHLX public statistics  
**MEASURES:** Previous-day PHLX equity-option call, put, and total volume; intraday totals; end-of-day volume and open interest for PHLX sector-index options. PHLX only, not industry-wide.  
**FREQUENCY/HISTORY:** Previous day and intraday. No historical file on the page.  
**URL fetched:** https://www.nasdaqtrader.com/trader.aspx?id=PHLXStatistics  
**ACCESS:** No login stated.  
**TERMS:** No terms sentence was in the extract.  
**QUOTE:** The page is a public previous-day and intraday statistics view, not a downloadable history.

**SOURCE:** ProShares daily holdings  
**MEASURES:** Fund-level holdings: ticker, shares or contracts, exposure value (notional plus gain/loss), and market value, including swaps and futures for leveraged funds. This is end-of-day exposure, not the rebalance trade.  
**FREQUENCY/HISTORY:** One file, “AS OF 10/12/2026”. The downloads page also links Historical NAVs, Split History, and Performance History as `.csv`. Those files were not opened.  
**URL fetched:** https://accounts.profunds.com/etfdata/psdlyhld.csv and https://www.proshares.com/resources/data-downloads  
**ACCESS:** No login.  
**TERMS:** Not stated on the CSV. ProShares’ website terms were not fetched.  
**QUOTE:** Header date “AS OF 10/12/2026”. Columns include “Shares/Contracts” and “Exposure Value (Notional + G/L)”.

**SOURCE:** Direxion daily holdings, example SPXL  
**MEASURES:** Shares outstanding, and line-level shares, price, market value, and weight, including cash, stocks, and “SPX SWAP ASSET LEG” rows. Current file, not an archive. The project’s 15 September 2026 note already used this URL pattern.  
**FREQUENCY/HISTORY:** TradeDate in the fetched file: “10/13/2026 12:00:00 AM”.  
**URL fetched:** https://www.direxion.com/holdings/SPXL.csv  
**ACCESS:** No login. Pattern `https://www.direxion.com/holdings/{TICKER}.csv`.  
**TERMS:** Direxion’s terms page was not fetched.  
**QUOTE:** “Direxion Daily S&P 500 Bull 3X ETF, SPXL, Shares Outstanding: 24750001.”

**CME:** Not a data block. https://www.cmegroup.com/market-data/volume-open-interest.html, the daily-bulletin page, the equity-index Section 01C PDF, and https://www.cmegroup.com/market-data/browse-data/exchange-volume.html each returned HTTP 500. No measure, history, or terms were read.

## RESEARCH

**FINDING:** Nearly half of S&P 500 options volume was 0DTE, versus a 15 percent share before the pandemic. Retail was about 10 percent of 0DTE volume. Dealers’ delta hedging can raise intraday volatility. In the first quarter of 2023, participants reported more days on which the S&P 500 moved more than 1 percent intraday around CPI, the jobs report, and Fed meetings. No price-impact coefficient.  
**AUTHORS, YEAR:** IMF staff, Global Financial Stability Report, Chapter 1, April 2023.  
**URL fetched:** https://www.imf.org/-/media/files/publications/gfsr/2023/april/english/ch1.pdf.md  
**QUOTE:** “nearly half the options trading volume on the S&P 500 is now …” “The share of retail investors amounts to about 10 percent of the …”

**FINDING:** Year-to-date through August 2023, US SPX 0DTE was more than 50 percent of that index’s option volume (source given as Cboe, 8 September 2023). Short 0DTE sellers may buy as prices rise and sell as prices fall. The box is a stylised simulation of a €1 million EURO STOXX 50 option hedge, not a US stock-price coefficient. Eurex added daily EURO STOXX 50 weeklies on 28 August 2023. Tuesday and Thursday SPX expiries are dated 18 April and 11 May 2022.  
**AUTHORS, YEAR:** Andrzej Sowiński, ECB Financial Stability Review box, November 2023.  
**URL fetched:** https://www.ecb.europa.eu/press/financial-stability-publications/fsr/focus/2023/html/ecb.fsrbox202311_02~0cf2c71d00.en.html  
**QUOTE:** The box states that US SPX 0DTE recently accounted for more than 50 percent of total option volumes for the index.

**FINDING:** 0DTE was about half of trading volume in S&P 500 index options and options on some index-linked ETFs. Of 21 dealers, 10 said institutional clients actively trade 0DTE, and all of those said these clients are a small fraction of equity-options clients. Half put 0DTE under 5 percent of those clients’ option premium; one-fifth said 10–20 percent; one-fifth said over 50 percent. Three-fifths collect intraday margin on 0DTE only when volatility is elevated; two-fifths do not. No price impact is estimated. Survey window 14–28 August 2023.  
**AUTHORS, YEAR:** Valery Polkovnichenko, Federal Reserve Senior Credit Officer Opinion Survey, September 2023.  
**URL fetched:** https://www.federalreserve.gov/data/scoos/scoos-202309.htm  
**QUOTE:** 0DTE options “now account for about half of all trading volume of S&P 500 …”

**FINDING:** SPX 0DTE was more than 50 percent of SPX options volume in August 2023, up from 5 percent in 2016. Leverage ratios can exceed 400. Average annualised 0DTE returns were −32,000 percent, with rare maxima up to 79,000 percent; one-month options averaged −550 percent annualised, with a maximum of 2,500 percent. 0DTE did not, on net, pull activity out of one-month options, so the authors judge it unlikely to be the main cause of the 2023 VIX decline. Their alternative is that dealers hedging yield-enhancing structured products buy when the index falls and sell when it rises, which dampens the underlying.  
**AUTHORS, YEAR:** Karamfil Todorov and Grigory Vilkov, BIS Quarterly Review, 4 March 2024.  
**URL fetched:** https://www.bis.org/publ/qtrpdf/r_qt2403x.htm  
**QUOTE:** The box reports SPX 0DTE above 50 percent of SPX options volume in August 2023, from 5 percent in 2016, and leverage ratios that can reach above 400.

**FINDING:** Exchange research, not a regulator. SPX 0DTE rose from 5 percent of SPX volume in 2016 to over 40 percent after Tuesday and Thursday expiries, averaging 50 percent in August 2023. The 2023 average was over 1.23 million contracts and $500 billion notional a day. Market-maker net gamma ran from $170 million to $670 million, equal to 0.04 percent to 0.17 percent of about $400 billion of daily S&P futures volume. Median net gamma at 3:30 p.m. was +$173 million; the 25th–75th range was −$1.1 billion to +$2.4 billion. On 15 August 2023 a 4440 put traded more than 100,000 contracts while market makers were short only about 3,000. Year-to-date, the spread between close-to-close and intraday volatility was 2.7 vol points, equal to the 10-year average.  
**AUTHORS, YEAR:** Mandy Xu, Cboe, 8 September 2023.  
**URL fetched:** https://www.cboe.com/insights/posts/volatility-insights-evaluating-the-market-impact-of-spx-0-dte-options/  
**QUOTE:** 0DTE averaged 50 percent of SPX volume in August 2023, and market-maker net gamma was 0.04 percent to 0.17 percent of daily S&P futures volume.

**FINDING:** July 2020–June 2023, using proprietary Cboe SPX/SPXW trades. 0DTE was 34.771 percent of SPX+SPXW volume on the average day. Customer-versus-market-maker was 68.717 percent of volume. Mean impact of options-market-maker gamma was to reduce daily annualised volatility by about 0.19 percentage points (median −0.08). The maximum impact raised daily annualised realised volatility by 3.3 percentage points and 30-minute annualised volatility by 6.4 percentage points. The authors say 3.3 points is small next to a 4.5-point standard deviation of daily changes. Mean of daily mean gamma was 341.2 × 10^9. Gamma was more often negative after May 2022. The underlying trades are not a free file.  
**AUTHORS, YEAR:** Diego Amaya, Peter Garcia-Ares, Neil D. Pearson, and Aurelio Vasquez, 25 January 2025.  
**URL fetched:** https://cdn.cboe.com/resources/education/research_publications/gammasqueezes.pdf  
**QUOTE:** The maximum estimated impact is an increase of 3.3 percentage points in daily annualised realised volatility and 6.4 percentage points in 30-minute annualised volatility.

**FINDING:** Staff views, from CAT and OPRA, which are not public downloads. The 0DTE share of traded contracts rose from 19.6 percent at the beginning of 2022 to 28 percent by 2025. Individual-customer 0DTE dollar volume exceeded $30 billion in peak months. Market-maker monthly 0DTE quantities surpassed 190 million contracts and notional exceeded $38 billion. In December 2025, excluding market makers, individual customers were 73.5 percent of expiration-day contract volume versus 54.3 percent on other days; institutional customers were 6.8 percent versus 21.8 percent. Unique underliers rose from 3,452 (2012) to 8,439 (2025). The note does not estimate a price impact on the underlying.  
**AUTHORS, YEAR:** SEC staff, Office of Analytics and Research, Division of Trading and Markets, 9 April 2026.  
**URL fetched:** https://www.sec.gov/files/roundtable-options-market-structure.pdf  
**QUOTE:** The 0DTE share of traded contracts went from 19.6 percent at the beginning of 2022 to 28 percent by 2025.

**FINDING:** For the four most liquid equity indices and ETFs, option notional was close to 80 percent of underlying cash volume, 60 percentage points higher than a decade earlier. 0DTE was around 60 percent of S&P 500 options volume, up from about 40 percent two years earlier; on some days up to 80 percent of volume was zero- to one-day expiry. Dynamic-volatility strategy assets were around $600 billion on a survey median. Stocks with greater leveraged-ETF exposure had higher intraday volatility; after market returns and betas, that link shows up mainly on stressed days (absolute market return at or above the 90th percentile), sample 2020–25, for single-stock leveraged ETFs on a named list of large US stocks. The chapter does not print the regression coefficient. The annex with that regression was not fetched.  
**AUTHORS, YEAR:** IMF staff, Global Financial Stability Report, Chapter 1, April 2026.  
**URL fetched:** https://www.imf.org/-/media/files/publications/gfsr/2026/april/english/ch1.pdf  
**QUOTE:** “Equity price declines could accelerate, with potential deleveraging in option and leveraged …” 0DTE was “around 60 percent of S&P 500 options volume, up from approximately 40 …”

**FINDING:** On 0DTE expiration days, 10-minute S&P 500 realised volatility was lower by 61 annualised basis points, about 7 percent of the sample mean of 9.10 percent (1 January 2018–19 May 2022). Market-maker hedging needs averaged about 1 percent of S&P 500 shares and were 0.15 percentage points higher when 0DTEs were present. A 2SLS multiplier of about −4 means 1 basis point more net gamma lined up with about 4 basis points lower realised volatility. One-standard-deviation 0DTE net gamma cut next-10-minute volatility by about 23 annualised basis points. After May 2022, average net gamma was 1.424 percent of S&P 500 capitalisation and 0DTE net gamma was 0.542 percent; net gamma was positive in 88 percent of 10-minute intervals. In 2024, more than 3 million SPX contracts traded a day and 0DTEs were nearly half. Built from paid Cboe Open-Close, OPRA, and futures feeds, not a free series. Views are not the Bank of Canada’s.  
**AUTHORS, YEAR:** Greg Adams, Chukwuma Dim, Bjorn Eraker, Jean-Sébastien Fontaine, Chayawat Ornthanalai, and Grigory Vilkov, draft 15 July 2026.  
**URL fetched:** https://www.jean-sebastienfontaine.com/papers/0dte-options-volatility.pdf  
**QUOTE:** On days when 0DTEs expire, 10-minute S&P 500 realised volatility is lower by 61 annualised basis points, about 7 percent of the sample mean of 9.10 percent.

## Three measurements

1. OCC daily equity, ETF, and index volume, split customer / firm / market maker, is the free industry-wide options-flow series; equity contracts times 100, divided by a free official share-volume series, is the options-versus-shares ratio, and that denominator was not confirmed here.  
2. There is no free 0DTE history file; the usable official levels are the SEC staff’s 19.6 percent to 28 percent of all contracts (2022–2025) and the IMF’s about 60 percent of SPX volume (April 2026), with an OCC `contractDt` filter still untested as a same-day-expiry cut.  
3. Direxion `{TICKER}.csv` and ProShares `psdlyhld.csv` already give the swap and futures notionals the project used on 15 September 2026; the missing piece is a dated AUM path so mechanical rebalance can be computed as leverage × (leverage − 1) × assets × that day’s index return.

## UNCERTAIN

- OCC CSV downloads returned HTTP 500 (`daily-volume-statistics` for 20261009 and 20190531, and an IBM volume query for 20241015). A browser or identified-user GET of a documented URL on a known trading day, plus the header row, would settle whether the files are actually public.  
- OCC terms ban robots and commercial copying, while the batch pages tell users to script those URLs. Which clause controls a research pull is not settled by the pages.  
- How far back OCC files go is not stated. Examples include 1 December 2016, 3 January 2017, and 31 May 2019.  
- `contractDt` is documented as yyyymmdd. The page does not say that setting it equal to the trade date isolates 0DTE. The volume-query record layout would settle that.  
- Daily open interest granularity is not defined on the page, and the parameter name differs between the table (`dailyDate`) and the example (`reportDate`).  
- Cboe daily statistics had no trade date in the extract, so the class totals above are an undated snapshot.  
- The Cboe 0DTE page had no as-of date.  
- `equitypc.csv` starts 1 November 2006. The fetch stopped around 24 June 2016 and also said only a few lines were truncated, so the end date was not read.  
- CME was not readable (HTTP 500 on four URLs). A successful fetch of the Daily Bulletin PG 01C would settle equity-index futures and options volume and open interest.  
- No free official series that already pairs single-stock option volume with share volume was found. The ratio has to be built.  
- Nasdaq’s paid PHOTO / Data Link products were not opened, so their price and licence are unknown. The public PHLX page has no history file.  
- ProShares and Direxion legal terms were not fetched. The holdings files are a single current day. ProShares’ historical NAV link was not opened, so it is unknown whether that file is a long AUM path or a short performance table.  
- There is no free official daily dealer-gamma series. OCC account type is volume. Large-options-position reports are not public. Rebuilding gamma requires Cboe Open-Close or an equivalent, which is paid and non-redistributable.  
- The IMF April 2026 leveraged-ETF result is an association on stressed days. The coefficient sits in Online Annex 1.3, which was not fetched. The April 2023 0DTE sentences were read from the chapter’s markdown rendering, so the wording may differ from the PDF box.

---

## R4 — Hedge ratios of foreign holders of US assets (find)

I’ll look up published hedge ratios for non-US holders of US assets from 2023–2026, starting with primary sources from central banks, supervisors, and company disclosures.Primary sources are turning up for Japan, Taiwan, Denmark, the Netherlands, Australia, and the BIS. I’ll fetch those pages and look for Finland, Norway, Canada, and Korea next.Published hedge ratios for 2023–2026 are sector-specific and are not one number. Official series exist for Denmark, the Netherlands (a quarterly loss offset, not a stock ratio), Australia, the Bank of Japan’s life-insurer chart, and Korea’s policy ceiling. Taiwan’s year-end ratios are in a wire report of a Financial Supervisory Commission briefing. Canada has no fetched official ratio.

| Holder group | Country | Hedge ratio or change | Date | Source type | URL fetched | Verbatim quote (≤15 words) |
|---|---|---|---|---|---|---|
| Insurance and pension sector, US-dollar book | Denmark | 61.8% to 73.5% of dollar investments | Start-2025 to end-May 2025 | Official statistic | https://www.nationalbanken.dk/en/news-and-knowledge/data-and-statistics/insurance-and-pension/20250703-insurance-companies-and-pension-funds-hedge-more-against-dollar-decline | “from 61.8 per cent to 73.5 per cent” |
| Same sector | Denmark | 70.7% in November to 72.2% | End-2025 | Official statistic | https://www.nationalbanken.dk/en/news-and-knowledge/data-and-statistics/insurance-and-pension/20260202-this-years-pension-return-driven-by-equities-and-currency-hedging | “from 70.7 per cent in November to 72.2 per cent” |
| Same sector | Denmark | About 70% of dollar exposure hedged; table shows kr 998.3bn hedged of kr 1,555.4bn | March 2024 | Official statistic | https://www.nationalbanken.dk/en/news-and-knowledge/data-and-statistics/insurance-and-pension/20240502-extended-statistic-on-currency-exposure-and-hedging | “about 70 per cent of the dollar exposure is hedged” |
| Pension funds | Netherlands | Derivatives gain of €11bn offset about 40% of FX losses. USD investments €551bn. Bonds mainly hedged; equities little hedged | Q1 2025 | Official statistic | https://www.dnb.nl/en/general-news/statistical-news/2025/weaker-us-dollar-hits-pension-funds-harder-than-falling-stock-prices/ | “offsetting some 40% of their foreign exchange losses” |
| Nine major life insurers, foreign bonds | Japan | BIS reading of the BoJ chart: roughly 60% to 40%. BoJ text says hedged foreign-bond holdings were reduced | 2021 to 2024; chart through end-September 2024, in the April 2025 Financial System Report | Study, citing the central bank | https://www.bis.org/publ/qtrpdf/r_qt2512b.htm and https://www.boj.or.jp/en/research/brp/fsr/data/fsr250423a.pdf | “reduced hedging rates from roughly 60% to 40%” |
| Life insurers, regulatory hedge ratio | Taiwan | 66.39% to 50.23%. Foreign investments NT$22.8tn; exposure excluding foreign-currency policies NT$15.4tn | End-2024 to end-2025 | Press, citing the regulator | https://www.cna.com.tw/news/afe/202601270363.aspx | “2025年底避險比率為50.23%” |
| Superannuation, overseas listed equity | Australia | Around one-fifth. June-quarter 2025 rise described as small. Hedge book on the order of A$½ trillion | Speech, 16 September 2025 | Central bank | https://www.rba.gov.au/speeches/2025/sp-dg-2025-09-16.html | “hedge only around one-fifth of the value of its overseas listed equity” |
| Superannuation, by asset | Australia | About 25% of international equity; about 70% of international debt and unlisted infrastructure | Survey date 31 March 2022, published March 2023 | Official statistic, via the RBA | https://www.rba.gov.au/publications/bulletin/2023/mar/foreign-currency-exposure-and-hedging-in-australia.html | “only around 25 per cent of their international equity investments” |
| Other financial corporations | Australia | Just over one-third of foreign-currency assets | 31 March 2022 | Official statistic | same RBA Bulletin URL | “hedge just over one-third of their foreign currency assets” |
| National Pension Service, strategic hedge | Korea | Standing target 0% since the 2015 decision. Temporary ceiling of up to 10%, plus a tactical band of ±5% of FX exposure. Ceiling period extended through end-2025 | Policy page current; extension decided 19 December 2024 | Official (fund policy and ministry) | https://fund.nps.or.kr/oprtplcy/astaprtplcy/getOHEC0007M0.do and https://www.mohw.go.kr/board.es?act=view&bid=0027&list_no=1483987&mid=a10503010100&nPage=1&tag= | “0%에서 시장상황에 따라 최대 10%까지” |
| Varma (pension insurer) | Finland | Open currency position 29.4% of investment market value | 31 December 2025 | Company disclosure | https://www.varma.fi/globalassets/tama-on-varma/varman-tilinpaatoksen-2025-esitysmateriaali.pdf | “Avoin valuuttapositio on 29,4 % sijoitusten markkina-arvosta.” |
| Government Pension Fund Global | Norway | No hedge ratio in the 2025 report. US assets 52.9% of the fund (NOK 21,268bn). Returns measured in a 34-currency basket; the krone effect is a separate value change | End-2025 | Official (manager) | https://www.nbim.no/en/news-and-insights/reports/2025/annual-report-2025/web-report-annual-report-2025/ | “Returns are generally measured in international currency” |
| Non-US investors, April 2025 | Cross-country | BIS: low hedge ratios into April, then higher hedge ratios and forward dollar sales, alongside a surge in spot and forwards | April 2025; article 8 December 2025 | Study | https://www.bis.org/publ/qtrpdf/r_qt2512b.htm | “increased their currency hedge ratios and sold dollars forward” |

The BIS bulletin on the April–May 2025 dollar slide was fetched, but the converter returned only the key takeaways: hedging by non-US holders of dollar securities contributed to dollar weakness, after high hedging costs had discouraged hedging, with the largest April declines in Asian hours. https://www.bis.org/publ/bisbull105.htm

## Synthesis

A single aggregate hedge ratio is not what these sources support. The defensible range for the holders that publish a ratio is about **20% to about 75%**, and it splits by asset and mandate.

- **Dollar or foreign-bond books with a hedging mandate** sit in the upper half. Denmark’s dollar hedge ratio, the cleanest official series, went from **61.8% at the start of 2025 to 73.5% at end-May and 72.2% at end-2025**, on a dollar book the central bank put at about kr 1,431 billion at end-May 2025 (its “30 percent of their investments”; the dot is the Danish thousands separator, so this is kr 1,431 billion, in line with the March 2024 dollar exposure of kr 1,555 billion). Taiwanese life insurers’ regulatory ratio, as briefed to the press, fell from **66% to 50%** over 2025. The BIS, using the Bank of Japan chart, puts major Japanese life insurers at **roughly 60% in 2021 and 40% in 2024**.
- **Equity-heavy pensions** sit near the bottom. Australian superannuation hedged **about one-fifth** of overseas listed equity in 2025, after a decline from about 30% toward 20%. The 2022 survey still had about **70%** on international debt. Dutch funds in Q1 2025 offset **about 40%** of FX losses with derivatives and, on De Nederlandsche Bank’s description, hedge bonds and leave equities largely open. Korea’s strategic target remains **0%**, with permission to go to **10%**.
- **April–May 2025.** The only fetched official increase is Denmark’s jump into May. The BIS describes a wider rush to raise hedge ratios with forwards rather than by selling the US assets. The Reserve Bank of Australia says the Australian equity-hedge increase that quarter was small.

**Coverage.** These ratios attach to identifiable books, not to all foreign holdings of US assets. Fetched stocks include Denmark’s dollar book (kr 1,431 billion, end-May 2025), Dutch USD investments (**€551 billion**, of which **€450 billion** in the United States, end-Q1 2025), Taiwanese life-insurer exposure excluding foreign-currency policies (**NT$15.4 trillion**, end-2025), and the Norwegian fund’s **52.9%** US weight. No total of foreign holdings of US assets was fetched in this session, so the share of that total is not computed here. The published ratios cover the main hedging institutions in Denmark, the Netherlands, Japan’s large life insurers, Taiwan’s life insurers, and Australian superannuation, and they leave official reserves, most mutual funds, and Canadian pensions outside the measured set.

## UNCERTAIN

- **Japanese 40% and 60%.** The April 2025 Bank of Japan report draws “Currency hedge ratios among life insurance companies” for nine majors through September 2024, and the text says currency-hedged foreign bonds were reduced. The percentages are the BIS reading of that chart. The chart’s printed ratio was not in the extracted text. The Life Insurance Association of Japan fact book was not fetched as a hedge-ratio source. A company-level filing with the ratio would settle it. Japan Times pages with a 44% figure did not load past a bot check.
- **Dutch 30% to 25%, and Danish 55% to 50%, in the December 2025 BIS Quarterly Review.** Those sentences cite the Dutch and Danish releases fetched here. The Dutch release gives the **40%** quarterly offset, not 30% or 25%. The Danish releases show a **rise** in 2025, not a fall to 50%. Treat 30-to-25 and 55-to-50 as unresolved until the underlying central-bank series are read directly.
- **Taiwan 50.23% and 66.39%.** They come from Central News Agency’s account of a Financial Supervisory Commission briefing, including the official’s name. Monthly FSC releases that were found report FX and hedging gains and losses, not the ratio. The FSC statistical table would settle it.
- **Korea’s executed ratio.** The fetched pages set the target and the ceiling. They do not say how much of the 0–10% band was used in 2025. A fund-committee implementation report would settle it. A December 2025 extension into 2026 appeared only in press search hits and was not fetched.
- **Finland.** Varma’s **29.4%** is the open currency position as a share of all investments, using the Finnish Pension Alliance’s net-of-hedges definition. It is not a hedge ratio on US assets. The sector table of open positions was located and not downloaded.
- **Norway.** The 2025 report measures the fund in the currency basket and shows the krone as a separate value change, with the United States at **52.9%**. It does not state a hedge ratio. Reading that as a zero hedge of dollar exposure is an inference. An explicit “not hedged” sentence showed up in search excerpts of 2012 reports, which were not fetched.
- **Canada.** No official pension hedge ratio was fetched.
- **Euro-area fund ratios in April 2025.** BIS Bulletin 123 was fetched, and only the summary came back: bond funds’ hedge ratios are high and stable; equity funds’ are volatile; the pattern flipped after Liberation Day. A search excerpt of the same PDF says equity funds’ de facto hedge ratio jumped from about 0.5 to almost a full hedge. That number was not in the fetched text.
- **Du and Huber, and the IMF’s 44% / 35% / 21% insurer, pension, and mutual-fund ratios,** are June 2020 estimates. The papers were not fetched, so they are not used above.
- **Share of all foreign holdings of US assets** needs a fetched TIC or IMF stock for the same date as these books.

---

## R5 — Bounding unreported central-bank gold (find)

**Cited but not fetched in this call (not relied on):** https://api.uktradeinfo.com; https://data.tuik.gov.tr/Bulten/Index?p=Foreign-Trade-Statistics-February-2025-53909&dil=2; https://ticaret.gov.tr/data/5bb71aa113b87613d802b783/TU%C4%B0K%20D%C4%B1%C5%9F%20Ticaret%20Verisi%20Edinme%20Rehberi_2023.pdf; https://tradeidds.censtatd.gov.hk/api/get; https://www.bazg.admin.ch/en/swiss-foreign-trade-statistics-database-opendata

I'll look up the research workflow first, then pull official trade and customs pages plus published methods that infer unreported official gold buying.The research skill file isn’t readable from here, so I’ll go straight to official statistics offices and published methods on unreported central-bank gold buying.Search hits point to official portals and WGC notes. I’ll open those pages and look for China customs, Comtrade, and the published inference methods.WGC’s 2024–26 figures are on the pages. Next I’ll open the customs portals, terms pages, and the later revision that cut the Q1 2026 central-bank total.Assumption: “unreported official buying” means gold that changes official ownership without showing up in IMF reserve statistics. Customs series measure declared non-monetary shipments, so they can only bound that gap.

## DATA

**SOURCE** | HM Revenue & Customs, UK Trade Info, Overseas Trade Statistics  
**MEASURES** | UK imports and exports of goods by HS/CN code, partner, and port. For this use: HS 7108, especially CN8 unwrought non-monetary gold, exports to Switzerland and other partners. Suppressed country or quantity detail is published only at a higher level.  
**UNIT** | Value in pounds sterling. Net mass in kilograms.  
**FREQUENCY** | Monthly, from 2000.  
**URL fetched** | https://www.uktradeinfo.com/trade-data/help-with-data-tables ; https://www.uktradeinfo.com/api-documentation ; https://www.uktradeinfo.com/terms-and-conditions/ ; https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/  
**ACCESS** | No login. Custom table: CSV up to 30,000 rows, export up to 150,000 rows; larger pulls via the API at `https://api.uktradeinfo.com`. The API is open access and does not need an Authorisation header. Rate limit 60 requests per minute; responses paginate at 40,000 rows.  
**TERMS** | Crown copyright, Open Government Licence v3.0: copy, publish, adapt, and commercial use, with attribution. Non-endorsement. No warranty.  
**QUOTE** | “Select the Net mass checkbox to show data for the net mass …”

**SOURCE** | Swiss Federal Office for Customs and Border Security (FOCBS), foreign-trade statistics / SwissImpex  
**MEASURES** | Swiss imports and exports of gold in raw form, including bars, under tariff heading 7108.1200, by country. From 2012 to 2020, mined and refined gold are not split. From 1 January 2021, imports are split into mined gold (key 911), refined gold of at least 99.5 percent (912/913), and refined gold below 99.5 percent (914). Headline “business cycle” trade totals exclude gold bars and other precious metals. The bulk open-data file found here is gold imports by country, not exports.  
**UNIT** | The gold page and SwissImpex manual describe quantity and value. The kilogram-versus-tonne unit is not stated on the pages fetched.  
**FREQUENCY** | Monthly by country from 2012 in SwissImpex. The open import file is monthly from 2021. September 2026 data were published on 20 October 2026.  
**URL fetched** | https://www.bazg.admin.ch/en/swiss-foreign-trade-statistics-gold-silver-and-coins ; https://www.bazg.admin.ch/en/swiss-foreign-trade-statistics-database-opendata ; https://www.bazg.admin.ch/en/swiss-foreign-trade-statistics-current-data ; https://opendata.swiss/en/dataset/waren-aussenhandel-goldimporte-nach-landern ; https://www.bazg.admin.ch/en/swiss-foreign-trade-statistics-the-terms-of-use-for-datasets  
**ACCESS** | SwissImpex is free and does not require registration. Results download as CSV or XLSX. Import CSV, about 299 MB, is on opendata.swiss with no key.  
**TERMS** | “You may use this dataset for non-commercial purposes. You may use this …”  
**QUOTE** | “Data relating to gold in raw form (e.g. bars) are recorded under …”

**SOURCE** | Hong Kong Census and Statistics Department, external merchandise trade / Trade-IDDS  
**MEASURES** | Declarations of imports, domestic exports, and re-exports, including trade with the Chinese Mainland. Ordinary merchandise tables omit SITC Rev. 4 Division 97, non-monetary gold excluding ores, and Division 98, monetary gold and coin. Those flows are recorded separately. Partner is country of consignment, not necessarily origin or final destination. Transit on a through bill of lading is excluded.  
**UNIT** | Value in HK$ ’000 in the API example. Quantity is a separate series (`QCm` / `QCy`); the unit is returned in the JSON `unit` field. A gold quantity call was refused, so the kilogram unit was not confirmed.  
**FREQUENCY** | Monthly. A month’s figures include declarations lodged up to the 14th of the next month. Annual and year-to-date series also exist.  
**URL fetched** | https://data.gov.hk/en-data/dataset/hk-censtatd-trade-idds-trade/resource/173a8d40-24ff-4e8e-b9f2-456b20208fa4 ; https://tradeidds.censtatd.gov.hk/MetadataLink/ApiSpec/API_eng.pdf ; https://www.censtatd.gov.hk/wbr/B1020005/B10200052025MM12/att/en/104/Explanatory%20note_202509_2.pdf ; https://www.censtatd.gov.hk/en/page_31.html ; https://tradeidds.censtatd.gov.hk/api/get?lang=EN&sv=QCy&freq=A&period=2024,2024&ttype=3&ccclass=C&cc=CN&codeclass=SITC2&code=97  
**ACCESS** | No API key in the specification. GET `https://tradeidds.censtatd.gov.hk/api/get`. The call above returned “Access denied” and asked for cookie consent or said too many calls were sent at once. Usage limits can change without notice.  
**TERMS** | C&SD statistical information may be downloaded, adapted, and distributed free of charge for commercial and non-commercial use, with acknowledgement of the C&SD site and of the Government as rights owner, and with modifications marked.  
**QUOTE** | “In this report, unless the “Trade in Gold and Specie”. All other tables refer to “merchandise trade” only, and do not include SITC Rev. 4 Division 97 “Gold, non-monetary (excluding gold ores and concentrates)” and Division 98 “Gold, monetary; gold coin and current coin”.”

**SOURCE** | General Administration of Customs of China, English monthly statistics  
**MEASURES** | The index fetched lists China’s total trade, trade by mode, trade by country, and major exports by quantity and value, in yuan and US dollars, through August 2026. It does not present an HS 7108 gold series. A separate fetch of a “major import commodities” table timed out, and search excerpts of those tables showed diamonds in kilograms under chapter 71, not a gold row.  
**UNIT** | Value in the tables that were listed. Gold quantity was not retrieved.  
**FREQUENCY** | Monthly.  
**URL fetched** | http://english.customs.gov.cn/Statistics/Statistics?ColumnId=1  
**ACCESS** | The English bulletin index is public, with no key. The detailed customs query system was not opened.  
**TERMS** | Not stated on the index page fetched.  
**QUOTE** | The fetched index is a list of aggregate releases, including “(5) China's Major Exports by Quantity and Value, Aug 2026 (in USD)”. No gold line was on that page.

**SOURCE** | UN Comtrade (UN Statistics Division), as the free compiled route for China’s reported gold trade and for mirror checks  
**MEASURES** | Annual and monthly merchandise trade by reporter, partner, and HS code. Non-monetary gold is in 7108.11, 7108.12, and 7108.13. Monetary gold, 7108.20, is not in the database.  
**UNIT** | Values in US dollars. Net weight in kilograms in the bulk-file layout (`netWgt (kg)`).  
**FREQUENCY** | Annual and monthly, as reported by each country.  
**URL fetched** | https://uncomtrade.org/docs/non-monetary-gold-in-trade-classifications-sitc-hs/ ; https://uncomtrade.org/docs/policy-on-comtrade-data-use/ ; https://comtradeplus.un.org/Subscriptions  
**ACCESS** | Preview without an account is described as available. A free registered account is required for fuller download and for an API key. Free tier: 500 API calls a day, 1 call a second, up to 100,000 records a call. Bulk files are premium.  
**TERMS** | UN copyright. Free data are for internal use. Re-dissemination needs UNSD permission, with a stated exemption for a small amount. Cite as “UN Comtrade”. Scraping the interface to dodge the quota can lead to suspension.  
**QUOTE** | “In UN Comtrade, there is no data under 7108.20 or 7118.90.”

**SOURCE** | Directorate General of Commercial Intelligence and Statistics (DGCI&S), India, and the public TradeStat help text  
**MEASURES** | India’s gold imports, quantity and value, from DGCI&S monthly data. The CI Division note aggregates them for FY 2022-23 to FY 2024-25. Country shares name Switzerland, the UAE, and South Africa as the top sources.  
**UNIT** | Metric tonnes and million US dollars in the note. TradeStat says the commodity unit is available only at 8-digit HS and can change, including between kilograms and tonnes.  
**FREQUENCY** | The note uses monthly data. The TradeStat help page fetched describes annual April–March figures. A monthly TradeStat screen was not fetched.  
**URL fetched** | https://www.dgciskol.gov.in/writereaddata/Downloads/20251128172849Navigating%20India%E2%80%99s%20Gold%20Import%20Trends.pdf ; https://tradestat.commerce.gov.in/eidb/help  
**ACCESS** | The PDF is a direct download. The help page does not mention a login or a key.  
**TERMS** | No reuse licence is stated on the help page fetched.  
**QUOTE** | “The quantity of imports has been witnessed to have increased from 678.3 …”

**SOURCE** | US Census Bureau merchandise trade, with the Bureau of Economic Analysis gold adjustment  
**MEASURES** | Physical movement of merchandise into and out of the US customs territory. Monetary gold is excluded from the merchandise trade balance. Census nonmonetary gold is end-use 12260 (exports) and 14270 (imports): unwrought or semi-manufactured, not finished manufactures. BEA adds a balance-of-payments adjustment for gold bought or sold by foreign official agencies that stays at the Federal Reserve Bank of New York and never crosses the customs line.  
**UNIT** | Census values in US dollars. Quantity is in the unit specified for that HTS or Schedule B code; the guide does not state a single gold unit. The BEA adjustment described in the FAQ is a value adjustment. Shipping weight is kilograms, vessel and air only, and includes packaging.  
**FREQUENCY** | Monthly. Prior-month revisions; annual redistribution of late records.  
**URL fetched** | https://www.census.gov/data/developers/data-sets/international-trade.html ; https://www.census.gov/foreign-trade/guide/sec2.html ; https://www.census.gov/data/developers/about/terms-of-service.html ; https://www.bea.gov/help/faq/1477  
**ACCESS** | Census API from January 2010. “All data queries to the Census Data API now require an API key.” A free key is requested from Census.  
**TERMS** | API use requires the notice “This product uses the Census Bureau Data API but is not endorsed …” Users must not identify a respondent. The API is “as is”.  
**QUOTE** | “Gold that is purchased by foreign official agencies, such as a foreign …”

**SOURCE** | Turkish Statistical Institute (TurkStat)  
**MEASURES** | Not documented from a page read in this session. The bulletin and the Ministry of Trade download guide both failed to load.  
**UNIT** | Not read.  
**FREQUENCY** | Not read.  
**URL fetched** | None. Attempted: https://data.tuik.gov.tr/Bulten/Index?p=Foreign-Trade-Statistics-February-2025-53909&dil=2 (timeout) and https://ticaret.gov.tr/data/5bb71aa113b87613d802b783/TU%C4%B0K%20D%C4%B1%C5%9F%20Ticaret%20Verisi%20Edinme%20Rehberi_2023.pdf (504).  
**ACCESS** | Not read.  
**TERMS** | Not read.  
**QUOTE** | None.

## METHODS/FINDINGS

**WHO** | World Gold Council, using Metals Focus. Gold Demand Trends, full year 2024, published 5 February 2025.  
**METHOD** | Official-sector demand is net purchases by central banks and other official institutions, including sovereign funds where applicable. Metals Focus estimates use IMF International Financial Statistics, international trade data, and other sources. The published total adds an estimate of unreported buying. Swaps are excluded. Monthly WGC reserve files are reported changes only.  
**FINDING with tonnes** | 1,044.6 tonnes in 2024, later revised. IMF IFS “only reflects 34% of our total official sector demand estimate for 2024”. Applied to 1,044.6 tonnes, that ratio leaves about 690 tonnes outside IFS. That tonne split is arithmetic from the published ratio, not a figure WGC printed. Reported buying named in the same article includes Poland 90 tonnes, Turkey’s official sector 75 tonnes, the Reserve Bank of India 73 tonnes, and the People’s Bank of China 44 tonnes.  
**URL fetched** | https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-full-year-2024/central-banks ; https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-q1-2024/18704 ; https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-full-year-2025/notes-definitions  
**QUOTE** | “Our quarterly central bank demand data is sourced from Metals Focus, whose …”

**WHO** | World Gold Council / Metals Focus, full year 2025, published 29 January 2026.  
**METHOD** | Same definition. Unreported buying is the gap between the Metals Focus estimate and officially reported data.  
**FINDING with tonnes** | 863.3 tonnes in 2025, down from a revised 1,092.4 tonnes in 2024. “Unreported buying remained a significant feature of the market in 2025 … …” Applied to 863.3 tonnes, 57 percent is about 492 tonnes. Again, that tonne figure is arithmetic. Reported additions include Poland 102 tonnes, Kazakhstan 57 tonnes, and the People’s Bank of China 27 tonnes, to 2,306 tonnes.  
**URL fetched** | https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-full-year-2025/central-banks  
**QUOTE** | “the gap between Metals Focus’ estimates and officially reported data continues to …”

**WHO** | World Gold Council / Metals Focus, first half of 2026.  
**METHOD** | Same residual. The Q1 2026 page says unreported buying is “the residual between estimated demand and reported purchases.” The next release reclassified part of Q1 from central banks to over-the-counter demand.  
**FINDING with tonnes** | Q1 2026 was first published as 243.7 tonnes on 29 April 2026, then revised to 57 tonnes. Q2 2026 is 288.9 tonnes. First-half 2026 is 345 tonnes, the lowest first half since 2022. Q2 says unreported buying “was again elevated” and gives no tonne split. Reported People’s Bank of China additions were 7 tonnes in Q1 and 33 tonnes in Q2, to 2,346 tonnes at end-June.  
**URL fetched** | https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-q1-2026/central-banks ; https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-q2-2026/central-banks  
**QUOTE** | “New data and analysis led to a sizable revision to our Q1 …”

**WHO** | IMF staff, “The Global Financial Safety Net—A Stocktaking”, October 2025, Box 2. The chart of official gold tonnes is sourced to the World Gold Council and IMF staff.  
**METHOD** | Compare gross central-bank purchases with the change in official reserve holdings.  
**FINDING with tonnes** | No unreported tonne total is printed in the box. Since 2022, central banks “accounted for just under a quarter of the total gold purchases”, versus a 10 percent market share in 2010–21. “Despite large purchases, net additions to official reserves have been modest, as …” Gold’s share of global reserves was nearly 18 percent at end-2024, mostly from the price rise.  
**URL fetched** | https://www.imf.org/-/media/files/publications/pp/2025/english/ppea2025035.pdf  
**QUOTE** | “some central banks appear to be holding the newly acquired gold outside their reserves.”

**WHO** | Jan Nieuwenhuijs, analyst article, April 2025. Press, not an official or peer-reviewed source. He attributes a three-source WGC description to the World Gold Council; that paragraph was not on the Gold.org pages fetched in this session. The Gold.org footnote above is the primary method statement.  
**METHOD** | Treat 80 percent of the WGC-minus-IMF gap as unreported Chinese buying. Separately, treat UK exports of London 400-ounce bars to China as People’s Bank of China metal, because the Shanghai Gold Exchange’s private market uses 1-kilogram bars, and because those exports continued when Shanghai traded at a discount to London.  
**FINDING with tonnes** | “In 2024, the Chinese central bank covertly bought 570 tonnes.” “China’s central bank has surreptitiously bought 1,800 tonnes from Q3 2022 through …” His stock estimate is 5,065 tonnes at end-2024, against reported holdings of 2,280 tonnes in the WGC 2024 article.  
**URL fetched** | https://www.thegoldobserver.com/p/chinas-gold-reserves-going-through  
**QUOTE** | “any gold moving directly from the U.K. to China is destined for …”

## Proposed bounding method

Use the WGC/Metals Focus total minus IMF-reported reserve changes as the global envelope: about 690 tonnes outside IFS on the February 2025 reading of 2024, and about 57 percent of the 863.3 tonnes in 2025. Treat it as an envelope only. The cut of Q1 2026 from 244 tonnes to 57 tonnes shows the residual moves between “official” and “over-the-counter”.

Cap one visible channel with HMRC net mass of CN8 7108.12 exports from the UK to China. That is an upper bound on London 400-ounce bars that left Britain for China, not proof of the buyer.

From SwissImpex exports of 7108.1200 by destination, subtract private sinks that are measured in tonnes: India, 669.3 tonnes of gold imports in FY 2024-25, and, once a TurkStat quantity file is actually downloaded, Turkish non-monetary gold imports. What remains can still be private investment, stocks, or official buying.

Cross-check Hong Kong re-exports to the Chinese Mainland, SITC 97 or HS 7108, with China’s reported non-monetary imports in UN Comtrade. Monetary gold, HS 7108.20, is absent there, so a mirror gap cannot be read as hidden reserve gold.

Keep US Census tonnes as a physical-crossing series only. Foreign-official purchases that stay at the New York Fed are in the BEA value adjustment, and the IMF’s 2025 note says some purchased gold never enters reported reserves at all.

## UNCERTAIN

SwissImpex quantity is described, but the pages fetched do not say whether it is kilograms or tonnes. A one-row export download for 7108.1200 would settle the unit. The open CSV on opendata.swiss is imports only; whether a matching export file exists outside the dashboard was not settled.

Hong Kong’s quantity unit was not confirmed. The API returns it in `unitEN`, and the 2024 re-export query for SITC 97 to the Chinese Mainland was denied. Repeating that call in a normal browser session would settle both the unit and the 2024 tonnage.

China’s own HS gold kilograms were not retrieved. The English GACC index fetched has no 7108 series, and the commodity table fetch timed out. A successful open of the Chinese customs query, or a China-as-reporter Comtrade pull for 710812, would settle what China publishes and whether it is value only.

Turkey was not read. Both attempted pages failed, so frequency, unit, login, and terms for TurkStat gold imports are unknown. A successful open of the TurkStat foreign-trade database for HS 7108 would settle them.

The India note’s later “2142.9 MT” for FY 2024-25 matches the sum of the three fiscal years 678.3, 795.2, and 669.3, so it reads as a running total from April 2022 rather than a second annual figure. That reading is inference from the arithmetic. The HS codes inside the 669.3 tonnes are not stated in the sentences fetched.

No peer-reviewed 2024–2026 paper that converts these customs flows into unreported official tonnes was fetched. The Nieuwenhuijs tonne figures are his, and they conflict with the older view that monetary-gold shipments are omitted from customs. The IMF sentence that some gold is held outside reserves does not identify the countries or the tonnes.

---

## R6 — Three data questions: corporate net interest, MOVE methodology, cross-currency basis (find)

I'll look up the official series and methodology pages for the three data questions, starting with the BEA, Fed, and ICE sources.The first hits point to NIPA Table 1.14 and Z.1 interest paid versus received. I’ll open those primary pages and the ICE and BIS sources next, because the preview numbers look incomplete.Monetary interest received is still well below interest paid in the BEA series. I’ll pull the 2024–2026 levels and the Z.1 and ICE pages so the sign is tied to the official tables.**Q1. ANSWER.** No. On the latest BEA figures, US nonfinancial corporations still pay more interest than they receive in 2024, 2025, and through 2026:Q2. “Net interest” in the NIPAs is interest paid minus interest received, so a positive NIPA number is a net payment, not net interest income.

**EVIDENCE.** BEA NIPA Table 7.11, updated with the 30 September 2026 GDP release. Monetary interest paid, nonfinancial corporate business, BEA code **B1101C** (FRED `B1101C1A027NBEA`), billions of dollars, annual: 2024 **952.984**, 2025 **992.240**. Monetary interest received, code **B1135C** (FRED `B1135C1A027NBEA`): 2024 **478.427**, 2025 **476.268**. Received minus paid: 2024 **−474.6**, 2025 **−516.0**. Table 7.11 line 7 is nonfinancial monetary interest paid; line 29 is nonfinancial monetary interest received. There is no 2026 annual observation.

NIPA Table 1.14, line 25, net interest and miscellaneous payments of nonfinancial corporate business, BEA code **B471RC**. Annual, not seasonally adjusted (FRED `B471RC1A027NBEA`): 2024 **319.911**, 2025 **346.271**. Quarterly, seasonally adjusted annual rate (FRED `B471RC1Q027SBEA`): 2025:Q2 **344.753**, 2025:Q3 **350.432**, 2025:Q4 **353.470**, 2026:Q1 **363.219**, 2026:Q2 **364.119**. Still a large positive payment.

Fed Z.1, 11 September 2026 release, Integrated Macroeconomic Accounts table S.11.1.i.a, billions of dollars. Nonfinancial corporate interest received **FA106130101**: 2024 **471.9**. Interest paid **FA106130001**: 2024 **639.4**. Received minus paid in 2024: **−167.5**. The annual table stops at 2024. The Financial Accounts Guide builds paid from Table 7.11 lines 7+49+80 and received from lines 29+58, then spreads the annual total evenly across the four quarters. FRED’s quarterly prints through 2026:Q2 (`BOGZ1FA106130001Q` **639,356** and `BOGZ1FA106130101Q` **471,894**, millions, SAAR) match that 2024 annual level. They are not a separate 2025–2026 estimate. The next Z.1 release is 10 December 2026, so this Z.1 vintage predates the 30 September 2026 BEA annual update. The Z.1 paid total is not equal to monetary interest paid; it includes the imputed-interest lines.

**URL fetched.** https://fred.stlouisfed.org/series/B1101C1A027NBEA ; https://fred.stlouisfed.org/series/B1135C1A027NBEA ; https://fred.stlouisfed.org/series/B471RC1A027NBEA ; https://fred.stlouisfed.org/series/B471RC1Q027SBEA ; https://fred.stlouisfed.org/release/tables?rid=53&eid=17676 ; https://www.bea.gov/news/2026/gdp-third-estimate-industries-corporate-profits-state-gdp-and-state-personal-income-2nd ; https://www.bea.gov/resources/methodologies/nipa-handbook/pdf/chapter-14.pdf ; https://www.federalreserve.gov/releases/z1/20260911/html/S11_1_i_a.htm ; https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FA106130001&t= ; https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FA106130101&t= ; https://fred.stlouisfed.org/series/BOGZ1FA106130001Q ; https://fred.stlouisfed.org/series/BOGZ1FA106130101Q

**QUOTE.** "aggregate interest paid, less the aggregate interest received"

**UNCERTAIN.** Whether 2024 monetary interest is final IRS Statistics of Income or still an extrapolation. The handbook says the most recent year is extrapolated, and 2025 is that year in this release. What would settle the 2026 Z.1 comparison is the 10 December 2026 Z.1 after it absorbs the 30 September BEA update.

**Q2. ANSWER.** ICE’s own pages disagree, and no ICE methodology document found here states the weights. The 16 October 2019 ICE release defines MOVE as one-month OTC options on 2-, 5-, 10-, and 30-year Treasuries, and treats swap-market versions as separate indices. ICE’s current catalogue page instead says options on US interest-rate swaps. The commonly cited 20/20/40/20 weights were not on any ice.com page fetched. They appear in a licensee catalogue that reprints an ICE BofA description.

**EVIDENCE.** ICE investor release, 16 October 2019: MOVE “measures the implied yield volatility of a basket of one-month over-the-counter options …” The same release says other indices in the family “measure volatility in the U.S. interest rate swap market,” and that inputs are “mid-implied volatilities for at-the-money bond options and swaptions.” The family listed there separates the bond-market MOVE from the swap-market SMOVE indices.

ICE Developer Portal catalogue, current page: “It measures U.S. bond market yield volatility by tracking a basket of …” No tenors, no expiry, no weights.

PNC’s ICE index catalogue, which carries an ICE Data Indices disclaimer and says the descriptions are used with permission, still says at-the-money one-month options on the current 2-, 5-, 10-, and 30-year Treasuries, “where the 10-year option is given a 40% weight and the other …” That is 20/20/40/20. It is not an ice.com methodology page. No post-2019 ICE rulebook or change notice was found that says the underlying was switched from Treasury options to swaptions.

**URL fetched.** https://ir.theice.com/press/news-details/2019/Intercontinental-Exchange-Completes-Acquisition-of-the-Merrill-Lynch-Option-Volatility-Estimate-MOVE-Index-from-Bank-of-America-Merrill-Lynch/default.aspx ; https://developer.ice.com/fixed-income-data-services/catalog/ice-data-indices-move-index ; https://www.pnc.com/content/dam/pnc-com/pdf/corporateandinstitutional/institutional/index-catalogue/ice-indices.pdf

**QUOTE.** "one-month over-the-counter options on 2-year, 5-year, 10-year and 30-year Treasuries"

**UNCERTAIN.** Whether the underlying actually changed after 2019, or the catalogue page is conflating MOVE with SMOVE. An ICE Data Indices rule document dated after 2019, stating the basket and the weights, would settle it.

**Q3. ANSWER.** No free official daily or weekly USD/JPY or EUR/USD cross-currency-basis series from the BIS, Fed, ECB, or BoJ turned up. The free series that does exist is an author-posted academic CIP dataset, Du, Keerati, and Schreger, updated October 2025 (V4), described in NBER Working Paper 35000. It covers Germany-for-euro and yen, daily, through June 2025. It is not a central-bank statistical release, and it is not the Du–Tepper–Verdelhan Libor basis file.

**EVIDENCE.** Download route: https://jesseschreger.com/data and the same posting at https://sites.google.com/view/jschreger/CIP. Files listed: Stata, CSV, an Excel supplement of Bloomberg and Datastream tickers, and a data appendix. The page says the file was updated October 2025 (V4).

NBER Working Paper 35000 (March 2026) says the dataset extends the Du–Im–Schreger Treasury-premium series through June 2025 and adds government-bond CIP deviations and their components under both IBOR and the post-LIBOR benchmark rates. Coverage stated in the paper: G10 currencies and 19 emerging-market currencies, nine tenors from 3 months to 30 years. The euro is Germany only. Yen is in the G10 tables. Figure notes use 13-day moving averages, and the 5-year samples are on the order of 6,500–7,000 observations, which is a business-daily panel. The paper’s CIP deviation is signed the opposite way from Du, Tepper, and Verdelhan (2018): positive means the synthetic dollar rate is above the cash dollar rate.

Terms, from the paper and the data page: the constructed series and the ticker list are “fully available for researchers.” Required citations are Du, Keerati, and Schreger (2025), “Decoupling Dollar and Treasury Privilege”; Du, Im, and Schreger (2018); and Du and Schreger (2016). Raw Bloomberg, Datastream, and Markit series are not reposted. No BIS, Fed, ECB, or BoJ statistical-release download of the basis itself was found; BIS material checked in this search is exchange rates or paper charts, not a maintained basis series.

**URL fetched.** https://jesseschreger.com/data ; https://sites.google.com/view/jschreger/CIP ; https://www.nber.org/system/files/working_papers/w35000/w35000.pdf

**QUOTE.** "fully available for researchers"

**UNCERTAIN.** The CSV was not opened here, so column names, the exact last date, and whether the link downloads without a Google login are unverified. Redistribution rights beyond “for researchers” are not stated. Opening the CSV from the Schreger page would settle frequency, currency columns, and the end date.


---

## Supervisor notes on the research parcels (R1–R6)

What each return changed is recorded where it belongs: R1 in `dossiers/ai-funding.md` and the Bassman note (claim 9); R6's Q1 and
Q2 in the Bassman note (claim 13 and the MOVE weights); R2–R5 and R6's Q3 in the E-021 map, section "Grok's source hunt". One figure
per return was checked at source by the supervisor:

| Parcel | Figure checked | At source | Result |
|---|---|---|---|
| R1 | Grok's deal list summed in dollars (ECB reference rates on each pricing date) | Goldman Exchanges page: $194bn issued "so far" (early Aug), $108bn in 2025, ~$250bn expected | **match:** $194.2bn to 3 Aug; $219.2bn to 20 Aug with $62.2bn non-dollar, against JPMorgan's $219bn and $62bn (JPM page relayed, not opened) |
| R2 | (no single figure; the finding is an absence) | — | consistent with the R3 note's own search |
| R3 | (research summaries; no figure carried into our notes) | — | not checked; relayed |
| R4 | Danish dollar hedge ratio 61.8% to 73.5% | Nationalbanken release, 3 Jul 2025 | **match** |
| R5 | WGC Q1 2026 central-bank demand revised 244t to 57t | gold.org, Gold Demand Trends Q2 2026 | **match** |
| R6 Q1 | Nonfinancial corporate monetary interest paid / received, 2025 | BEA bulk annual file `NipaDataA.txt`: B1101C 992,240; B1135C 476,268; B471RC 346,271 ($mn) | **match** |
| R6 Q2 | 20/20/40/20 in PNC's ICE catalogue | download failed (no connection) | **not verified**; relayed |
| R5 (J2) | TIC banks' own dollar liabilities +162.9 to −138.3 | Treasury press release sb0631, line 29 | **match** |

Not acted on: R1's Meta/BlackRock El Paso $12.5bn (a venture's debt, not Meta's bond) and the Alphabet 8-K headline/tranche
mismatches (C$9.5bn vs C$8.5bn; ¥576.9bn vs ¥576.5bn), left for the Q3 10-Q read.

## Supervisor adjudication of the judging parcels (J1–J4)

**Corrections registered from this wave:** C-133 (the M&A framing of net retirement), C-134 (four of six, not five), C-135 (the
velocity range is unsigned, about 1.3–2.0) and C-136 (the BIS on hedging).
While landing it, two more: C-137 (J1 showed the Bassman note gave the earnings share the wrong window) and C-138 (the
pre-publish page audit found the money-fund ~$4bn presented as a ceiling in W2 and as "at least" on the page; it is a name-search
floor that includes Apple). The same audit narrowed C-134 to three of the five large spenders.

**J1, headline equity findings.**
- **H1 and H6 were mis-framed by the supervisor's claims file, which put them in the wrong window.** The ANSWER's 71.0–82.3% earnings
  share and the tax-cut "tenth" are measured since 2015, not over end-2023 to mid-2026; the page's chart says "since 2015". Grok's
  in-window re-derivation, earnings about 92% of the Dec 2023–Jun 2026 log price gain (Shiller via multpl.com), is relayed
  unverified; the supervisor has no local Shiller copy. The ANSWER needs its windows stated where the numbers appear.
- **H4: FALLS, accepted.** This is C-133. The supervisor re-summed the live EFA file: gross retirement $2,979.4bn, 65% buybacks;
  gross issuance $2,427.4bn.
- **H8: WEAKENED, accepted.** The IPO share is half (Renaissance census, $146bn) to two-thirds (our eight 2026-priced deals among ten prospectuses read, $112bn; the page audit corrected "ten"). Reworded.
- **H2, H3, H5, H7, H9: WEAKENED, noted.**
  - Most per-share accretion predates the window (H5).
  - The December 2023 ON RRP spike loads the 2024 drain (H7).
  - The ETF/mutual-fund offset is 81.6%, not complete (H9).
  - The premium split is basis-sensitive, as the note already says (H2).
  - The wrapper's bond-ETF share of about 29% matches (H3).
  No wording on the page states more than these allow.

**J2, the rates and FX map.**
- **R8: FALLS, accepted.** This is C-136.
- **R5: WEAKENED, accepted.** The fall in the all-instrument net inflow is mostly banks' own dollar liabilities (+$162.9bn to
  −$138.3bn); foreign purchases of long-term US securities *rose* ($1,468.7bn to $1,754.4bn). The map is reworded.
- **R3: WEAKENED, accepted on wording.** The ON RRP is a money-fund asset; its run-down is an asset swap, not "funding". Reworded.
- **R1: WEAKENED on basis only.** The $294bn is on an unadjusted basis; it is $289.5bn on the seasonally adjusted all-Treasury flow.
  The 12% stands.
- **R2 and R7 stand. R4 is untestable (Grok's file fetch was truncated); our in-house sum stands. R6 is labelled in-house. R9 is noted.**

**J3, AI financing.**
- **A1: FALLS, accepted.** This is C-134.
- **A3: WEAKENED, informative.** The "$750bn" in the press is 2026 capex or operating cash flow, not bonds (UBP; S&P via The DESK).
  Goldman counts $194bn of hyperscaler bonds issued so far in 2026, with about $250bn forecast for the full year. That supports our
  ~$272bn trailing figure, and settles the Bassman comparison: his $750bn is capex, not borrowing.
- **A4: WEAKENED, labels.** The quarter labels are filing quarters; the single report-date cut gives 32%, the one-per-fund cut 36%.
  Noted.
- **A5: WEAKENED, accepted, then narrowed.** The census is a floor for the names searched, but it includes about $0.8bn of Apple.
  Under AI names it is about $3.4bn. The page audit rejected "at least about $4bn"; the page now gives $3.4bn (C-138).
- **A2 and A6: WEAKENED, noted.** The lease total sets undiscounted, partly conditional rents against guarantee ceilings, as the note
  says; the Chicago Fed's industry set is broad.

**J4, collateral velocity.**
- **V3 and V4: FALL, accepted after re-reading N3 §8.** This is C-135. The 16 Nov Singh note must ask, not assert.
- **V2: WEAKENED.** JPMorgan's repledged share is flat (80.0% to 79.8%); the four-bank 84% depends on the Morgan Stanley and Bank of
  America footnotes. To be re-read before the Singh note.
- **V5: WEAKENED.** Singh's 2012 source line was an AUM × leverage formula ("IMF staff estimates"). That supports "estimated" for
  2012; the 2013–17 method is inferred.
- **V1 stands.**


---

# Wave 3, 13 Oct 2026: six more parcels (K1–K6)

*Same lane, same fence, six calls in parallel. Every call ended SUCCESS with no breaches, no blocked attempts, no unexpected tools and no stage changes. Quotes over 15 words cut to twelve by the supervisor.*

| Parcel | Topic | Wall time (s) | Searches | Fetches | URLs cited but not fetched |
|---|---|---:|---:|---:|---:|
| K1 | Commodities claims C1–C10 (judge) | 1218 | 16 | 43 | 3 |
| K2 | The Bassman note's sixteen verdicts and the MOVE re-derivation (judge) | 742 | 27 | 26 | 0 |
| K3 | Bank collateral re-use, six banks, June 2025 and June 2026 (find) | 590 | 32 | 26 | 0 |
| K4 | Who bought the 2026 hyperscaler bonds (find) | 482 | 28 | 45 | 0 |
| K5 | Hedge-ratio citation gaps (find) | 409 | 26 | 18 | 1 |
| K6 | Why the CFTC short fell while Form PF's net long rose (find) | 638 | 9 | 17 | 0 |

---

## K1 — Commodities claims C1–C10 (judge)

**Cited but not fetched in this call (not relied on):** https://publicreporting.cftc.gov/resource/72hh-3qpy.json?%24where=cftc_contract_market_code%3D%27088691%27; https://www.iea.org/news/statement-by-iea-executive-director-on-meeting-of-iea-member-governments-on-7-october-2026; https://www.iea.org/reports/oil-market-report-october-2026

I'll review each commodities claim against the file and the public sources it names, then test the wording on C2, C4, and C8.The claims file is loaded. Next I’ll pull the named CFTC, EIA, STEO, and IMF series and check the wording on futures, prediction, and the oil-stock draw.The futures counts in C1, C7 and the US stock and WTI price prints in C8 match the public series. The sentences that turn those counts into a source of the gold bid, a test that positions “do not predict,” or “a physical squeeze, not financial inflow” do not.

Managed-money net is long minus short, futures-only. Gold is CFTC market 088691, WTI 067651, copper 085692. The oil window is the 40 weeks from the week ending 26 Dec 2025 through the week ending 2 Oct 2026.

C1 | STANDS | All three futures-only gold nets match the disaggregated report, and no later week has a higher net. | 6 Oct 2026: 127,101 − 16,114 = 110,987. 26 Dec 2023: 152,801 − 46,347 = 106,454. 24 Sep 2024: 256,435 − 37,406 = 219,029. | https://publicreporting.cftc.gov/resource/72hh-3qpy.json?%24where=cftc_contract_market_code%3D%27088691%27 | “published in futures-only formats as well as futures-and-options combined formats” | Whether a reader treats “peak” as the high since end-2023. On that window it is the high: the smallest short since 26 Dec 2023 is 8,310, so every week outside the largest-long set nets at most 214,227.

C2 | FALLS | “Not from futures” uses a flat managed-money endpoint to stand in for every futures book and for venues the COT does not cover. | Since 26 Dec 2023, managed-money net +4,533 contracts, but it first rose by 112,575 contracts (about 350 tonnes) to the Sep 2024 peak. Swap-dealer net short deepened by 37,694 contracts, to −225,026. Producer net short shrank by 25,512 contracts, which is futures buying. Non-reportable net long rose by 9,565. Open interest fell from 491,343 to 396,109. | https://www.cftc.gov/MarketReports/CommitmentsofTraders/DisaggregatedExplanatoryNotes/index.htm | “counterparties may be speculative traders, like hedge funds” | A full gold-flow identity would need LBMA OTC forwards, SHFE and SGE position data, Asian ETF creations, and bar-and-coin shipments. CFTC itself says reported positions are “70 to 90 percent of the total open interest,” on US reportable markets only. World Gold Council’s market primer, fetched this session, puts 2025 Shanghai Futures Exchange gold volume at about $51bn a day beside COMEX.

C3 | WEAKENED | The endpoint position rose only 4.3 percent, so a large price rise would make mark-to-market the bulk of the dollar change, but “contracts already held, not from new buying” describes a round trip that peaked at 219,029 contracts. | +4,533 contracts from 106,454 to 110,987. Front-month COMEX gold settled at $4,159.20 on 6 Oct 2026, 21.80 percent under the 29 Jan 2026 high of $5,318.40, and down 3.85 percent year to date. | https://www.morningstar.com/news/dow-jones/202610066572/comex-gold-settles-075-higher-at-415920-data-talk | “Off 21.80% from its record high of $5318.40” | The 26 Dec 2023 COMEX settlement was not retrieved, so the price-versus-quantity split was not recomputed. The settlement that day, plus a stated rule for the price-quantity cross term, would settle the percent.

C4 | WEAKENED | A near-zero one-week correlation fails to reject “no linear lead”; with 145 weeks it does not show that positions do not predict. | The window from 26 Dec 2023 to 6 Oct 2026 is 1,015 days, exactly 145 weeks. The correlation coefficients were not recomputed. For a true correlation of −0.08, the t-statistic is about −1.0, and a 95 percent interval is about −0.24 to +0.09. Effects smaller than about 0.16 are what this sample can detect at 5 percent. | https://www.cftc.gov/MarketReports/CommitmentsofTraders/DisaggregatedExplanatoryNotes/index.htm | “breakdown of each Tuesday's open interest” | Recompute Pearson, and a Newey-West regression of the return from Friday’s release on both the position change and the position level, at 1-, 4- and 8-week horizons. The report is as of Tuesday and is published Friday, so a “same-week” price change is contemporaneous with the position change, and part of the “next week” occurs before anyone can read the report.

C5 | WEAKENED | The warning that GLD and IAU are a poor stand-in for global ETF flows matches 2026 regional data; “are about 36 percent” does not match this year’s country flows, and the 77/23 split was not re-derived. | World Gold Council, published 7 Oct 2026: September global inflows $10bn and a record Q3 of $31bn; North America year to date $4.1bn; UK-listed funds $9.5bn year to date and ahead of China. US funds were $3.8bn of September’s $10bn. | https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2026/10 | “US$9.5bn of inflows y-t-d, UK-listed funds” | GLD and IAU shares outstanding and NAV at end-2023 and now. That filing pair would test the $119bn rise, the 77 percent price share, and whether 36 percent is a since-end-2023 cumulative rather than the current mix.

C6 | WEAKENED | Price can dominate the change in reserve value, but 96 percent requires only about a 2 percent rise in tonnes if the gold price doubled, and the Council’s own estimates show more buying than that, including metal not in the IMF file. | End-2025 official holdings about 38,600 tonnes. First-half 2026 central-bank and official-institution net demand 345 tonnes, the lowest first half since 2022, after Q1 was revised from 244 tonnes to 57 tonnes. | https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-q2-2026/central-banks | “H1 net demand of 345t was the lowest for a first half since 2022” | IMF IFS tonnes at end-2023 and the latest month, the LBMA price used to value them, and whether unreported buying is inside the stock. The Council’s line “was again elevated in Q2 and continued to be a notable feature” is the gap that moves 96 percent. The cross term in the value change also moves it by several points.

C7 | WEAKENED | The four-week cut and the end-2023 versus now contract counts are right; over that same span the net fell by half while the monthly WTI price rose, and during the 2026 rally the net rose. | 8 Sep 2026 net 111,731 contracts to 6 Oct 2026 net 53,598, a cut of 58,133 contracts, which is 58.1 million barrels. 26 Dec 2023 net 107,403, stated as 107k. 30 Dec 2025 net was 15,743, then at least 111,731 on 8 Sep 2026. EIA Cushing monthly spot: Dec 2023 $71.90, Jan 2026 $60.04, Sep 2026 $97.31. | https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?f=m&n=pet&s=rwtc | “unweighted average of the daily closing spot prices” | A test that weekly position changes lead weekly returns is the C4 regression. The level comparison already shows the net fell from end-2023 to now while the monthly price rose from $71.90 to $97.31.

C8 | WEAKENED | The US stock changes, the two WTI monthly averages, about $12bn, and a −424 mb Jan–Sep implied balance all re-derive; “a physical squeeze, not financial inflow” goes past what a residual, a policy release, and one futures category can show. | SPR 413,219 thousand barrels on 26 Dec 2025 to 282,983 on 2 Oct 2026, a fall of 130.236 mb over the 40 reported weeks. Commercial crude 422,888 to 424,134, a rise of 1.246 mb. Valuing each month’s SPR change at that month’s Cushing spot gives about $12.01bn. Jan–Sep 2026 supply minus demand, times days, is −424.2 mb. Of that, Jan–Jul is −243.6 mb and Aug–Sep, which the same table marks as projection, is −180.6 mb. | https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=WCSSTUS1&f=W | “an accounting residual, not a measured inventory figure” | Weekly WTI times each weekly SPR change, rather than the monthly proxy used here. The 2025 build of 688 mb was not on an EIA table that opened: Aug–Dec 2025 on the same monthly file is a build of about 489 mb, so 688 needs about 199 mb more in Jan–Jul 2025. Commercial crude was flat only at the ends; it reached 461,636 thousand barrels on 27 Mar 2026. NYMEX managed money rose from 15,743 contracts on 30 Dec 2025 to 111,731 on 8 Sep 2026 during the move from $60 to $97.

C9 | WEAKENED | Twelve-week managed-money net is almost unchanged at the ends and LME stocks have fallen over the last month, from a mid-range stock, while the position inside the twelve weeks was not flat. | COMEX copper managed-money net 60,185 on 14 Jul 2026 and 61,134 on 6 Oct 2026 (+949). The high inside the window was 82,522 on 22 Sep 2026. LME total stock 231.3 thousand tonnes on 12 Oct 2026, down 1.4 percent in 30 days. On 9 Oct the three-exchange total was LME 233,025 t, COMEX 713,771 t, Shanghai 58,744 t. | https://thevaultreport.com/lme/copper | “sits mid-range for its record, at the 47th percentile” | An official LME all-time price high. The page gives a 12 Oct cash price of $14,822 a tonne and does not call it a record. LME stocks are also up about 93 thousand tonnes over twelve months on that page, so “drawing” is the recent leg.

C10 | WEAKENED | Once “unaccounted” is inside the equation, the weekly balance meets itself by construction; 11 thousand barrels is a rounding band around that plug. | The 508-of-509 count was not recomputed. EIA defines the adjustment, formerly unaccounted-for crude oil, as disposition minus supply, and says the independent components rarely meet. The adjustment is typically under 2 percent of refinery inputs, which is hundreds of thousands of barrels a day, against 11 thousand barrels a week after the plug is inserted. | https://www.eia.gov/todayinenergy/detail.php?id=21472 | “Typically, the adjustment is less than 2% of refinery crude oil inputs.” | Recomputing reported stock change against 7 times (production + transfers + imports − exports + adjustment − refinery inputs) on all 509 weeks since 2017, and naming the one week outside 11 thousand barrels.

OUTSIDE ESTIMATES

| figure | value | source URL | agrees with ours? |
| --- | --- | --- | --- |
| STEO Jan–Sep 2026 implied world stock change, re-derived | −424.2 mb (−1.55 mb/d). 3Q26 is −1.87 mb/d | https://storagecurve.com/crude-oil/world/demand/ and https://www.eia.gov/pressroom/releases/press593.php | This is the claim’s 424 mb. EIA’s own line is “global inventories fell by 1.9 million barrels per day” in 3Q26. Aug–Sep in the monthly file are still marked as projection. |
| IEA observed global oil stocks, February through August 2026 | −507 mb, of which August −95 mb; August oil on water −65 mb; non-OECD −52 mb; OECD +23 mb | https://www.iea.org/reports/oil-market-report-september-2026 | Same direction as a large 2026 draw. It does not agree with −424 mb: shorter window, counted stocks including oil on water, and OECD tanks rose in August. August’s −95 mb is close to the STEO August residual of about −92 mb. |
| IEA member government releases | about 325 mb released under the March 2026 collective action | https://www.iea.org/news/statement-by-iea-executive-director-on-meeting-of-iea-member-governments-on-7-october-2026 | Not a world balance. It is large relative to the US SPR draw of 130.2 mb and to the 424 mb residual, and it is a policy supply release. |
| OPEC OECD commercial stocks, August 2026 | +36.6 mb on the month, to 2,808 mb; 8.8 mb under the five-year average and 57.5 mb under a year earlier | https://publications.opec.org/momr | No. The visible OECD commercial system built in August. |
| IEA Oil Market Report, October 2026 | page returned 404 | https://www.iea.org/reports/oil-market-report-october-2026 | No Jan–Sep 2026 IEA total was available. |
| STEO 2025 world build of 688 mb | not re-derived | EIA STEO text and table PDFs timed out | Unresolved. Aug–Dec 2025 on the monthly file used above is a build of about 489 mb. |

The October STEO narrative PDF timed out, so 424 mb is the sum of the monthly implied rates in the StorageCurve table of the 6 Oct 2026 STEO, checked against EIA’s 1.9 mb/d for the third quarter. TradingEconomics returned 403. GLD and IAU sponsor files, the IMF IFS tonne file, the 26 Dec 2023 gold settlement, and the weekly WTI series were not retrieved.

---

## K2 — The Bassman note's sixteen verdicts and the MOVE re-derivation (judge)

I'll review the note claim by claim against primary sources, starting with the file and the public data behind the CONTRADICTED and CONSISTENT verdicts.The note’s contested calls are the buyer mix, insurer and pension demand, corporate net interest, and the MOVE construction. I’ll check those against primary releases first.Primary pages are up. Next I’ll pull the Z.1 flows, auction buyer classes, corporate interest, and the yield series needed to recompute one MOVE row.The yield row is computable. I’m now opening the Z.1 sector tables, the Treasury demand charge, and the MOVE methodology pages.The note’s all-maturity buyer and nonfinancial-interest verdicts match the releases. The long-end reading is harsher than the bill-versus-coupon split supports, and one MOVE row matches only if the four volatilities are weighted, not if the daily changes are weighted first.

Assumptions: Z.1 quarterly flows are seasonally adjusted annual rates, so a year of dollars is the four-quarter sum divided by four. The year to 2026Q2 is 2025Q3–2026Q2. “Last 21 trading days” means 21 close-to-close changes ending 9 October 2026.

**1 | PARTLY | AGREE |** From 29 Dec 2023 to 18 Sep 2026 the 10-year rose 113bp, the real yield 96bp and the breakeven 17bp; BIS ties the later term-premium rise to fiscal pressure but says the drivers cannot be separated. | https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2023/202312?type=daily_treasury_yield_curve&field_tdr_date_value_month=202312&page&_format=csv | “12/29/2023 … 3.88” on the 10-year | UNCERTAIN: no free term-premium series was recomputed here.

**2 | CONSISTENT | AGREE |** The same dates give breakevens of 2.16% and 2.33%, a 17bp rise, which is the note’s “small, not flat” reading of “around 2.35%.” | https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/202609?type=daily_treasury_real_yield_curve&field_tdr_date_value_month=202609&page&_format=csv | “09/18/2026 … 2.68” on the 10-year real yield | UNCERTAIN: the four-year path between those dates was not re-read.

**3 | OPINION | AGREE |** Hedonic quality adjustment is a methodology dispute, and the note measures nothing against it. | — | — | UNCERTAIN: no BLS methods page was opened.

**4 | PARTLY | AGREE |** BIS says weighted-average maturity fell from about 6.3 years in early 2023 to 5.8, mostly because bill issuance rose, which is the front-end shift; the note’s “36% more rate risk” was not recomputed. | https://www.bis.org/publications/qr-202609/yields-climb-yet-risk-appetite-holds-firm | “ramping up the issuance of T-bills” | UNCERTAIN: the 36% duration figure and the “constant since February 2024” date.

**5 | CONTRADICTED | TOO HARSH |** The 12%, 28% and +$264bn figures match Z.1 for all Treasuries, but the Fed’s +$264bn was +$292bn of bills and −$27bn of notes, bonds and TIPS, and the Desk’s reserve-management buying is bills or, if needed, coupons of three years or less. | https://www.federalreserve.gov/releases/z1/20260911/html/F3_2_t.htm | “Treasury bills” and “Other Treasury notes, bonds, and TIPS” | UNCERTAIN: the prior-year 44%, 10% and −$266bn, because this table has no 2024Q3. Money funds also bought $268bn of non-bill Treasuries; whether those are short coupons is not stated.

**6 | CONTRADICTED (all maturities); UNTESTED (30-year) | TOO HARSH |** Life, property-casualty and pensions did buy about $205bn of Treasuries in the year to 2026Q2, but private defined-benefit plans were net sellers of about $2.7bn, life insurers’ non-bill buying was about $28bn, and the Bank of England says UK defined-benefit demand for long gilts has fallen. | https://www.federalreserve.gov/releases/z1/20260911/html/F3_2_t.htm | “Defined benefit plans” under private pension Treasury securities | UNCERTAIN: no 30-year split. The investor-class auction workbook did not come down as a file, and the prior-year $18bn was not recomputed. No NAIC or ACLI 2025–26 maturity table was opened.

**7 | CONSISTENT | AGREE |** Japan’s TIC holdings fell from $1,191.6bn in March 2026 to $1,103.9bn in July, about $88bn, and the Ministry of Finance’s September report shows residents net selling long-term foreign bonds. | https://ticdata.treasury.gov/Publish/slt_table5.html | “Japan | 1103.9 … 1191.6” | UNCERTAIN: the −¥4.5trn year-to-3-October figure and the $172bn intervention size. Holdings also move with valuation.

**8 | CONSISTENT | AGREE |** Mainland China held $618.0bn in July 2026, down $77.6bn from $695.6bn a year earlier. | https://ticdata.treasury.gov/Publish/slt_table5.html | “China, Mainland | 618.0 … 695.6” | UNCERTAIN: the 2013 peak was not on the page opened, so “far below its peak” was not re-checked from a primary history file.

**9 | CONTRADICTED on size | AGREE |** Reuters/LSEG, via CNA, counts about $194bn of bonds from Amazon, Alphabet, Meta and Oracle through 7 July 2026, and Goldman’s $750bn figure in that article is 2026 capital expenditure, with bond issuance expected near $250bn. | https://www.channelnewsasia.com/business/hyperscaler-debt-binge-pushes-yields-up-investor-demand-cools-6286196 | “capital expenditure to reach about $750 billion in 2026” | UNCERTAIN: the note’s $229bn sum to 13 October was not retotalled from the 8-Ks. Crowding-out remains untested.

**10 | CONSISTENT | AGREE |** BIS says gold fell from early-2026 peaks and rebounded when the 19 August buyback announcement revived fiscal worries, which fits “down on rates, still a fiscal hedge.” | https://www.bis.org/publications/qr-202609/yields-climb-yet-risk-appetite-holds-firm | “Gold extended its decline from early-year peaks” | UNCERTAIN: the $4,155 price, the 24k-contract cut, and the IMF tonne figures were not opened.

**11 | PARTLY | AGREE |** The earnings-share and residual-multiple arithmetic sits in the programme’s own files, which are not a public source, and nothing fetched overturns the split between earnings and an unmeasured flow. | — | — | UNCERTAIN: the 71–82% and 92% earnings shares.

**12 | PARTLY CONTRADICTED | AGREE |** H.8 shows loans to nondepository financial institutions at $2,079.4bn on 30 September 2026, the note’s figure, so bank credit does reach private-credit vehicles. | https://www.federalreserve.gov/releases/h8/current/default.htm | “Loans to nondepository financial institutions” | UNCERTAIN: the $1,090bn of unused commitments was not on this H.8 page.

**13 | CONTRADICTED for nonfinancial corporations | AGREE |** BEA shows nonfinancial corporations paid $992.240bn and received $476.268bn in 2025. All domestic corporate business received $4,023.897bn and paid $3,288.231bn, a net receipt of about $736bn, but that is the financial-sector margin and was already true in 2021. | https://fred.stlouisfed.org/series/B1135C1A027NBEA | “2025: 476.268” monetary interest received, nonfinancial | UNCERTAIN: no S&P 500 ex-financial aggregate of interest income versus expense was found. What would settle it is a published S&P 500 nonfinancial interest-income and interest-expense total.

**14 | UNTESTED | AGREE |** ICE’s own catalogue gives history since 1996 and does not publish a 1990s average or a free level near 100. | https://developer.ice.com/fixed-income-data-services/catalog/ice-data-indices-move-index | “History Since 1996” | UNCERTAIN: whether 100 equals the 1990s average.

**15 | CONSISTENT on cause | AGREE |** BIS treats the oil move in this window as a consequence of the Hormuz and Iran conflict, which is the note’s physical-shock reading; “transitory” is still a forecast. | https://www.bis.org/publications/qr-202609/yields-climb-yet-risk-appetite-holds-firm | “hostilities in the Strait of Hormuz” | UNCERTAIN: the SPR draw of 130 million barrels and the managed-money positioning.

**16 | PARTLY | AGREE |** In the twelve months through July 2026, private foreigners’ net purchases of long-term US securities were $1,599.6bn, while official net purchases of Treasury bonds and notes were −$16.8bn. | https://home.treasury.gov/news/press-releases/sb0631 | “Private, net” Treasury bonds and notes “263.4” over twelve months to July 2026 | UNCERTAIN: the 1-percentage-point reserve-share decline and the €341bn euro-area inflow.

## MOVE re-derivation

Window: 21 close-to-close changes, 11 September 2026 through 9 October 2026, from Treasury par yields (levels from 10 September).

Method that matches the note: population standard deviation of each tenor (divide by 21, not 20), annualise with √252, then weight 20/20/40/20. That gives a daily figure of 5.23bp, which rounds to the note’s 5.2bp, and 83.0bp annualised against the note’s 83bp. The 2-year and 30-year legs are 97bp and 70bp, against the note’s 97 / 70.

Method that does not match: standard deviation of the weighted daily change, same population divisor and √252. That annualises to about 78bp, not 83bp. The row is the volatility of a weighted basket of yields only if the weights are applied after the standard deviations.

## ICE methodology

No ICE-hosted page opened here states the 20/20/40/20 weights. The weights are in PNC’s index catalogue, which says ICE data are used with permission: the 10-year is weighted 40% and the other three tenors 20% each, on one-month at-the-money options on Treasury notes and bonds. https://www.pnc.com/content/dam/pnc-com/pdf/corporateandinstitutional/institutional/index-catalogue/ice-indices.pdf — “the 10-year option is given a 40% weight”.

ICE’s 16 October 2019 release says MOVE is one-month options on 2-, 5-, 10- and 30-year Treasuries, that a separate family measures the swap market, and that inputs are “mid-implied volatilities for at-the-money bond options and swaptions.” It states no weights. https://ir.theice.com/press/news-details/2019/Intercontinental-Exchange-Completes-Acquisition-of-the-Merrill-Lynch-Option-Volatility-Estimate-MOVE-Index-from-Bank-of-America-Merrill-Lynch/default.aspx

ICE’s current developer catalogue says the MOVE “tracks a basket of over the counter options on U.S. interest rate swaps,” and gives history since 1996, with no weights. https://developer.ice.com/fixed-income-data-services/catalog/ice-data-indices-move-index — “options on U.S. interest rate swaps”.

Whether the underlying was switched from Treasury options to swaptions after 2019 is not settled. The 2019 release keeps MOVE on Treasuries and SMOVE on swaps; the current catalogue page says swaps; the PNC reprint of an ICE description still says Treasury notes and bonds.

---

## K3 — Bank collateral re-use, six banks, June 2025 and June 2026 (find)

I'll pull the June 2025 and June 2026 collateral figures from the banks' own 10-Qs, starting with the SEC filing pages and the known JPMorgan and Goldman reference points.I'll look up each bank's June 2025 and June 2026 10-Q on EDGAR and pull the collateral footnote that states permitted re-use versus what was actually repledged.June 2026 figures for JPMorgan, Goldman, Morgan Stanley, and Wells Fargo are in the search hits. I’ll fetch those pages and the missing Bank of America, Citigroup, and June 2025 filings.Bank of America’s June 2026 note is rounded to the nearest tenth of a trillion, and Citigroup still needs a direct filing hit. I’ll fetch those pages and the June 2025 disclosures next.The June figures are in the notes. I’ll confirm the XBRL tags and whether Citigroup quantifies the repledged portion or only the amount it is allowed to re-use.The re-use share on received collateral is about 0.84 at 30 June 2026 and about 0.83 at 30 June 2025 for JPMorgan, Goldman Sachs, Morgan Stanley and Bank of America together. That is the filings’ (b)/(a). It is not a velocity of 2.

JPMorgan’s 30 June 2026 pair matches the reference exactly: $2,181.4bn permitted and $1,741.8bn repledged, 79.8%. Goldman’s permitted amount at that date is $1,431.870bn.

Amounts are fair value of collateral received that the firm may sell or repledge, and the part it had sold or repledged. They are not the firm’s own assets pledged to others.

| bank | date | permitted (a), $bn | repledged (b), $bn | share | filing and page or XBRL tag | SOURCE URL fetched | QUOTE (15 words or fewer) |
|---|---|---:|---:|---:|---|---|---|
| JPMorgan Chase | 30 Jun 2026 | 2,181.4 | 1,741.8 | 79.8% | 10-Q; `us-gaap:FairValueOfSecuritiesReceivedAsCollateralThatCanBeResoldOrRepledged` and `…ThatHaveBeenResoldOrRepledged` | https://www.sec.gov/Archives/edgar/data/19617/000162828026054343/R31.htm | “Collateral permitted to be sold or repledged, delivered, or otherwise used” |
| JPMorgan Chase | 30 Jun 2025 | 1,726.4 | 1,350.2 | 78.2% | same two tags; Q2 2025 10-Q | https://www.sec.gov/Archives/edgar/data/19617/000001961725000615/R31.htm | “fair value of collateral accepted” |
| Goldman Sachs | 30 Jun 2026 | 1,431.870 | 1,265.704 | 88.4% | 10-Q collateral table; (a) is `…ThatCanBeResoldOrRepledged` | https://www.sec.gov/Archives/edgar/data/886982/000088698226000297/R18.htm | “Collateral available to be delivered or repledged” |
| Goldman Sachs | 30 Jun 2025 | 1,196.882 | 1,019.781 | 85.2% | same table in the Q2 2025 10-Q | https://www.sec.gov/Archives/edgar/data/886982/000088698225000022/R46.htm | “were delivered or repledged” |
| Morgan Stanley | 30 Jun 2026 | 1,382.658 | 1,062.240 | 76.8% | 10-Q Note 8, p. 58; `CustomerSecuritiesForWhichEntityHasRightToSellOrRepledgeFairValue` and `…FairValueOfSecuritiesSoldOrRepledged` | https://www.sec.gov/Archives/edgar/data/895421/000089542126000212/R34.htm | “Collateral received with right to sell or repledge” |
| Morgan Stanley | 30 Jun 2025 | 1,120.277 | 876.305 | 78.2% | same two tags; Q2 2025 10-Q | https://www.sec.gov/Archives/edgar/data/895421/000089542125000440/R35.htm | “Does not include securities used to meet federal regulations for the Firm’s U.S. broker-dealers.” |
| Bank of America | 30 Jun 2026 | 1,400 | 1,300 | 92.9% | 10-Q securities-financing note; rounded to $0.1 trillion. Standard numeric tag is absent (404) | https://www.sec.gov/Archives/edgar/data/70858/000007085826000394/R16.htm | “permitted by contract or practice to sell or repledge” |
| Bank of America | 30 Jun 2025 | 1,100 | 1,000 | 90.9% | same note in the Q2 2025 10-Q; same rounding | https://www.sec.gov/Archives/edgar/data/70858/000007085825000268/R16.htm | “of which $1.0 trillion and $882.2 billion were sold or repledged” |
| Citigroup | 30 Jun 2026 | not disclosed | not disclosed | — | not in the Q2 2026 10-Q | https://data.sec.gov/api/xbrl/companyconcept/CIK0000831001/us-gaap/FairValueOfSecuritiesReceivedAsCollateralThatCanBeResoldOrRepledged.json | — |
| Citigroup | 30 Jun 2025 | not disclosed | not disclosed | — | not in the Q2 2025 series; tag history is year-end only | same companyconcept URL | — |
| Citigroup | 31 Dec 2025 | 1,064.0 | not disclosed | — | nearest 10-K, not a June date; (a) tag `…ThatCanBeResoldOrRepledged`. Repledged tag returns 404 | https://www.sec.gov/Archives/edgar/data/831001/000083100126000011/R196.htm | “Fair value of collateral received that may be resold or repledged” |
| Wells Fargo | 30 Jun 2026 | 600.3 | 448.9 | 74.8% | 10-Q Note 15; `…ThatHaveBeenResoldOrRepledged` | https://www.sec.gov/Archives/edgar/data/72971/000007297126000302/R22.htm | “right to sell or repledge was $600.3 billion” |
| Wells Fargo | 30 Jun 2025 | 311.2 | 216.1 | 69.4% | 10-Q Note 16; same tag | https://www.sec.gov/Archives/edgar/data/72971/000007297125000201/R23.htm | “of which $216.1 billion and $142.2 billion, respectively, were sold or repledged” |

Bank of America amounts in the table are the printed roundings ($1.4tn / $1.3tn and $1.1tn / $1.0tn), expressed in billions. The 30 June 2025 note gives December 31, 2024 more tightly, at $925.7bn and $882.2bn. Those are not the June figures.

**Four dealers (JPM, GS, MS, BAC)**

Using the figures as printed, including Bank of America’s rounded trillions:

| date | permitted (a), $bn | repledged (b), $bn | share |
|---|---:|---:|---:|
| 30 Jun 2026 | 6,395.928 | 5,369.744 | 84.0% |
| 30 Jun 2025 | 5,143.559 | 4,246.286 | 82.6% |

JPM + GS + MS alone, which are stated to the million or to $0.1bn, are 81.5% at 30 June 2026 ($4,995.928bn / $4,069.744bn) and 80.3% at 30 June 2025 ($4,043.559bn / $3,246.286bn).

**Reference checks**

- JPMorgan 30 June 2026, $2,181.4bn / $1,741.8bn / 79.8%, matches.
- Goldman permitted $1,431.870bn at 30 June 2026 matches. Repledged on the same line is $1,265.704bn.
- The $775.3bn repledged figure is the 31 December 2017 fact on `…ThatHaveBeenResoldOrRepledged`. The 30 June 2017 fact on that tag is $779.8bn. The $968.8bn permitted amount was not re-read in this session.

**UNCERTAIN**

- Bank of America prints June amounts only to the nearest $0.1 trillion. A figure shown as $1.4tn can sit anywhere from $1.35tn up to but not including $1.45tn, and $1.3tn from $1.25tn up to but not including $1.35tn. On that band the four-dealer share is about 82.5–85.4% at 30 June 2026 and about 80.8–84.3% at 30 June 2025. An unrounded XBRL fact, which this company does not file under the standard tag, would settle it.
- Bank of America says it accepts “securities and loans.” The primary source is securities borrowed or purchased under resale agreements. The loan piece is not split out.
- Morgan Stanley’s repledged line “does not include securities used to meet federal regulations for the Firm’s U.S. broker-dealers.” Segregated securities were $28.116bn at 30 June 2026 and $22.293bn at 30 June 2025, drawn from resale agreements and trading assets together. The filing does not say how much of that came from received collateral, so it cannot be added to (b).
- Goldman’s repledged dollars are in the note. The exhibit page stopped before the second element’s Name, so the tag name for (b) was not read. The permitted tag is confirmed because the companyconcept value equals $1,431,870,000,000.
- Citigroup does not report either June date. The nearest 10-K gives permitted collateral of $1,064.0bn at 31 December 2025 and $844.8bn at 31 December 2024, and no repledged amount. The $497.6bn line beside it is collateral Citi itself pledged that the counterparty may not sell or repledge. A sentence quantifying re-use, if it exists, would be in the narrative of that 10-K note; it was not in the details table fetched here.
- Wells Fargo is outside the four-dealer total. Its share is 74.8% and 69.4%.

---

## K4 — Who bought the 2026 hyperscaler bonds (find)

I'll start from the two dossiers, then look up each 2026 hyperscaler bond deal and any free holdings evidence that can test the "long money" claim.The dossiers put about $229bn of 2026 hyperscaler bonds with “long money.” I’ll look up each deal’s order book and any published buyer split, then the free holdings data.Order-book figures are showing up in the press; investor-type splits and the non-dollar deals still need primary pages. I’ll fetch those next.Press snippets give order books, but I still need the pages themselves, plus any buyer-type split and the free holdings series.Reuters returned 401, so I’ll use free syndications and primary filings instead of trying to get past that wall.The free record shows large, cooling order books and index inclusion. It does not show who was allocated the bonds. No fetched page gives a buyer split by insurer, pension, asset manager, hedge fund, bank, or central bank.

Issuer filings confirm sizes. Order books come from press accounts of lead-manager figures, not from the issuers. Reuters returned 401 on the original stories, so those figures are taken from free syndications. Bloomberg, IFR, and GlobalCapital were not used where the page was blocked, empty, or a paywall copy.

## Table 1. Deals

| Date | Issuer | Currency and size | Order book | Allocation by type or region | Source | Quote |
|---|---|---|---|---|---|---|
| 2 Feb 2026 | Oracle | USD $25bn, eight parts, 3s–40s plus a $500m floater | Peak about $129bn. A second fetched account says over $127bn | Not published. One account says the floater was aimed at bank and floating-rate buyers. That is a description of the structure, not an allocation | https://www.communicationstoday.co.in/oracles-25-billion-bond-sale-calms-ai-debt-concerns/ | “orders for more than $129 billion of Oracle bonds” |
| 9 Feb 2026 (closed 13 Feb) | Alphabet | USD $20bn, seven parts, 2029–2066. Size is the 8-K; the book is not | Peak $103bn. Another fetched account says more than $100bn | Not published | https://api.advisorperspectives.com/articles/2026/05/05/alphabet-returns-euro-debt-market-ai-megabond-deal | “orders that peaked at $103 billion” |
| 10 Feb 2026 (closed 13 Feb) | Alphabet | GBP £5.5bn: £0.75bn 2029, £1.25bn 2032, £1.25bn 2041, £1.25bn 2058, £1bn 2126 | Century tranche: £9.5bn of orders. Whole sterling book: about five times covered, per LSEG IFR as relayed later. A sterling total in pounds was not on a page that loaded | Not published. See UNCERTAIN on the UK pension and insurer inference | https://blog.twentyfouram.com/insights/how-hyperscaler-issuance-is-reshaping-the-treasury-curve | “drew £9.5bn of orders” |
| 10 Feb 2026 (CHF close about 3 Mar) | Alphabet | CHF 3.055bn, five parts, 2029–2051 | Not on any page that loaded | Not published | https://www.clearygottlieb.com/news-and-insights/news-listing/alphabet-in-record-inaugural-5-5-billion-and-chf-3-055-billion-bonds-issuances | “CHF 3.055 billion aggregate principal amount” |
| 10 Mar 2026 | Amazon | USD $37bn, 11 parts, 2028–2076 | About $126bn | Not published | https://www.ttnews.com/articles/amazon-bond-sale-37-billion | “drawn about $126 billion of orders” |
| 11 Mar 2026 | Amazon | EUR €14.5bn, eight parts, 2028–2064 | Peak more than €35bn. A later press compilation puts the book at €27.9bn | Not published | https://finance.yahoo.com/news/amazon-raises-54b-record-bond-144705950.html | “more than 35 billion of peak demand for the euro offering” |
| 30 Apr 2026 | Meta | USD $25bn, six parts, 2031–2066 | About $96bn at the peak | Not published | https://texxr.com/1168077/meta-raises-$25b-with-$96b-order-book | “Investors placed about $96 billion of orders” |
| 5 May 2026 | Alphabet | EUR €9bn, six parts. Launch reports said at least €9bn; a later note states €9bn issued | More than €25.2bn of bids at launch | Not published | https://api.advisorperspectives.com/articles/2026/05/05/alphabet-returns-euro-debt-market-ai-megabond-deal | “drawn more than €25.2 billion of bids” |
| Early May 2026 | Alphabet | CAD. A four-part sale was launched. Final size did not load (a secondary filing page timed out; Reuters returned 401) | Not obtained | Not published | https://api.advisorperspectives.com/articles/2026/05/05/alphabet-returns-euro-debt-market-ai-megabond-deal | “four-part Canadian dollar bond sale” |
| 15 May 2026 (settle 21 May) | Alphabet | JPY ¥576.5bn, seven parts, 2029–2066 | Not in the prospectus | Not published. Japan leg is a solicitation limited to qualified institutional investors, which is a legal limit, not a buyer split | https://www.sec.gov/Archives/edgar/data/1652044/000119312526228923/d137872d424b5.htm | “solicitation targeting QIIs” |
| 12 May 2026 (issued 28 May) | Amazon | CHF 2.82bn, six parts, 2029–2051 | Size was increased several times. No total book found | Not published | https://www.swissinfo.ch/eng/amazon-sells-swiss-franc-bond-offering-in-record-six-parts/91400508 | “raised 2.82 billion Swiss francs” |
| 8 Jun 2026 | Amazon | CAD C$14bn, from a compilation of Amazon’s pricing term sheet | That compilation says no book was reported | Not published | https://r40.io/news/amzn-done-borrowing-then-sold-425bn-sterling/ | “no book was reported for the franc, Canadian dollar” |
| 7 Jul 2026 | Amazon | USD $25bn, eight parts, 2029–2066 | Peak about $62bn, then about $41bn, about 1.6 times. A separate 30-year cover of 2.5 times is a different cut | Not published | https://www.marketbeat.com/articles/the-bond-market-just-sent-amazon-a-message-investors-shouldnt-ignore/ | “settling at about $41 billion” |
| 6 Aug 2026 | Alphabet | USD up to $25bn, 10 parts, about 2 to 40 years | About $115bn | Not published. The same piece only says the structure was built to appeal to short-end money managers and long-duration pensions | https://ng.investing.com/news/stock-market-news/alphabet-taps-bond-market-with-sweeping-10part-offering-to-fuel-ai-ambitions-2643353 | “drew about $115 billion of demand” |
| 19 Aug 2026 | Alphabet | AUD A$5.5bn, 3s, 5s, 10s, and 20s | Bids worth more than A$18bn | Not published. A local ETF manager said Australian institutions had depth. No percentages | https://ca.finance.yahoo.com/news/alphabet-raises-3-9-billion-084802381.html | “worth more than A$18 billion” |
| 9 Sep 2026 | Amazon | GBP £4.25bn: £1.25bn 3-year and £1bn each of 6-, 12-, and 19-year | Final book more than £10.65bn, after about £12bn before the spread was tightened. About 2.5 times | Not published | https://theedgemalaysia.com/node/817417 | “final demand of more than £10.65 billion” |

USD and sterling sizes for Alphabet’s February deals are also in the 13 February 8-K, which has no order book: https://www.sec.gov/Archives/edgar/data/1652044/000119312526051423/d946885d8k.htm. Quote: “$20 billion aggregate principal amount”.

## Table 2. Holdings evidence

| Source | What it shows | Value | URL | Quote |
|---|---|---|---|---|
| Treasury TIC, July 2026 release | Foreign net purchases of all US corporate bonds, not these issuers. “Corporate bonds” here include company bonds and municipal bonds. Private buyers dominate official buyers. Later releases revise earlier months | Private, 12 months through Jul 2026: $392.3bn, versus $305.4bn through Jul 2025. Official: $59.7bn versus $35.7bn. Latest monthly private / official, $bn: Feb 47.9 / 6.1; Mar 67.3 / 9.5; Apr 18.1 / 2.6; May 48.7 / 3.8; Jun 27.7 / 11.7; Jul 20.5 / 6.5. January 2026 was not in these three releases | https://home.treasury.gov/news/press-releases/sb0631 | “cannot attribute holdings of U.S. securities with complete accuracy” |
| Bank of England, July 2026 Financial Stability Report | The five hyperscalers’ share of US investment-grade debt. Issuance share, not a holder census. The report says the paper was absorbed and spreads stayed tight | 3% of outstanding US investment-grade debt at end-2025; over 15% of year-to-date US investment-grade issuance by early May 2026 | https://www.bankofengland.co.uk/financial-stability-report/2026/july-2026 | “just 3% of the stock of outstanding US IG debt” |
| CPRAM, 23 Sep 2026 | These bonds are inside the main investment-grade indices. Long end is heavier | Bloomberg US investment-grade corporate: close to 5% overall, 7.5% at 10 years and longer. Bloomberg Euro Corporate: about 1%, and 4% at the long end. 2026 issuance cited: $223bn, of which $132bn dollars, €23.5bn, CHF 5.9bn, £9.75bn | https://cpram.com/gbr/en/professional/publications/experts/article/what-impact-is-hyperscaler-bond-issuance-having-on-bond-markets | “close to 5% of the overall index” |
| J.P. Morgan Asset Management, 20 Aug 2026 | Single-name weights are still small. Passive funds must follow issuance. Combined weight was lower at the start of the year | Each hyperscaler 1.5% or less of the USD investment-grade index. Combined about 3.5% at the start of 2026. Year-to-date issuance $219bn, including $62bn equivalent outside the dollar | https://am.jpmorgan.com/gb/en/asset-management/institutional/insights/market-insights/market-updates/on-the-minds-of-investors/hyperscaler-debt-issuance-ai-buildout/ | “Individual hyperscaler weights are currently 1.5% or less” |
| TwentyFour, 3 Sep 2026 | ICE BofA US Corporate weight, and long-end primary demand versus the investment-grade average | About 4.5% of that index. 30-year cover: Oracle 4.5x, Meta 3.6x, Alphabet’s later deal 4.6x, Amazon’s July 30-year 2.5x, against a 2.98x year-to-date investment-grade average | https://blog.twentyfouram.com/insights/how-hyperscaler-issuance-is-reshaping-the-treasury-curve | “around 4.5% of the ICE BofA US Corporate Index” |
| ETF Daily, citing ETF Trends, 29 Sep 2026 | Technology sector inside bond ETFs. This is the whole sector, not the four issuers | Technology more than 10% of the Bloomberg US Corporate Bond Index. LQD, VCIT, and IGIB technology weight 13% or more, up about 300bp from about 9% in 2024 | https://www.theetfdaily.com/story/ai-infrastructure-debt-pushes-tech-past-banks-in-major-investment-grade-bond-ind | “Technology accounts for more than 10%” |
| NISA, 24 Aug 2026 | AA pension discount curves now contain a large hyperscaler share, so liability-driven managers have a reason to own Amazon, Alphabet, and Meta. Oracle is BBB and is outside those curves. The page does not give a holding percentage | Charts are described, not numbered in the text. The mechanism is pressure to hold the bond that is in the curve | https://www.nisa.com/perspectives/the-elephants-in-the-curve-hyperscalers-in-pension-discount-curves/ | “may feel pressure to hold it to track the liability” |
| NAIC public summaries | No issuer-level insurer holdings of these bonds were found. Industry bond totals do not name Alphabet, Amazon, Meta, or Oracle | Not a test of the claim | Search only; no issuer table loaded | — |
| SEC N-PORT | No free aggregate of registered-fund holdings of these 2026 CUSIPs was found. A hit in search was equity, not these bonds | Not a test of the claim | — | — |

Index-tracking demand, as far as free pages go: fixed-rate dollar investment-grade bonds of this size are in the Bloomberg US Corporate and ICE BofA US Corporate indices, because those sources already publish weights for these issuers. Euro bonds are in the Bloomberg Euro Corporate index at about 1%. Sterling, Swiss-franc, Canadian, yen, and Australian bonds are not in the US dollar indices. Floaters are a separate question: inclusion in the standard fixed-coupon indices was not stated on a page that loaded.

A weight near 5% means index funds hold about 5% of the index-eligible stock, in line with the benchmark. It does not say what share of each new deal those funds bought, and it does not say what share insurers or pensions hold on top of that. Turning 5% into a dollar bid needs tracker assets divided by the index’s market value. That ratio was not on a free page.

## VERDICT

**UNTESTABLE ON FREE DATA.**

The claim is that this debt is held mainly by insurers, pensions, and long-only funds. Nothing fetched allocates a deal, or the stock, by those classes. The books show that buyers existed in size early in the year, from about five times covered down to about 1.6 times on Amazon’s July dollar sale, and that the long end still covered above the investment-grade average. Books are indications of interest, they shrink when the spread is cut, and they mix every buyer type. Index weights and the Bank of England’s 3% stock figure show the bonds entered ordinary investment-grade portfolios, including passive ones, and NISA’s curve work shows pensions have a liability reason to own the AA names. That is consistent with a large long-only and liability-matching bid. It does not show that bid is the majority, and it does not show the opposite. TIC foreign buying of corporate bonds in 2026 is large and mostly private, but it is not these CUSIPs. No free NAIC or N-PORT total was found, so cash pools and leveraged holders are not measured either. The claim is not contradicted. It is not demonstrated.

What would settle it is a CUSIP census: N-PORT and N-MFP summed for registered funds and money funds; NAIC Schedule D summed for life, property, and health insurers; and, for the non-dollar tranches, the local equivalents plus euro UCITS holdings. A lead-manager allocation by investor type, if one is ever released free, would settle the new-issue question directly. Index weight times passive assets over index market value would settle only the passive slice.

## UNCERTAIN

- Sterling full-book pounds. Fetched pages support about five times covered and £9.5bn on the £1bn century bond. A £30bn book appeared only in search snippets of pages that were not opened.
- Alphabet’s Canadian deal. Launch is confirmed. Size and book did not load.
- Amazon’s Canadian C$14bn is from a secondary reading of the term sheet. No order book was reported there. A page that mentioned a larger book timed out.
- Swiss-franc books for both Alphabet and Amazon. Sizes are confirmed. Totals of orders are not.
- Alphabet’s yen book. The prospectus has the amount and a qualified-institutional-investor limit in Japan. A Reuters line on domestic and international demand returned 401.
- Alphabet’s August dollar book. Peak about $115bn is fetched. A later $108bn figure was not.
- Oracle’s book. Fetched pages say about $129bn and over $127bn. A higher figure in search was not fetched.
- Amazon’s July cover. About 1.6 times is the whole deal after the spread was cut. 2.5 times is the 30-year tranche in a different note. They should not be averaged.
- Amazon’s euro book. Peak above €35bn and a later €27.9bn are both press figures, not a filing.
- Whether the 4.5% ICE weight includes SpaceX. The sentence sits next to a list that includes SpaceX.
- Whether the floating-rate tranches sit in the main fixed-coupon indices.
- Mawer’s statement that the century bond was placed with UK pension funds and insurers. That is the author’s reading of who needs 100-year credit. No allocation was published.
- NISA’s chart percentages. The text does not state them.
- TIC official-versus-private split. Treasury says the split has a transaction bias, and custody does not equal the end holder.
- January 2026 TIC corporate-bond flow. Not in the May, June, or July releases that loaded.

---

## K5 — Hedge-ratio citation gaps (find)

**Cited but not fetched in this call (not relied on):** https://www.nissay.co.jp/global/news/pdf/20250523a.pdf

I'll pin down the published hedge-ratio figures from the BIS review and the official releases behind them, then check Japan, Taiwan, and any aggregate estimates. First I need the search and fetch tool schemas.The BIS sentence is in the December 2025 review. Next I’ll read the Dutch and Danish releases it cites, and look up Japan, Taiwan, and any official aggregate.The cited Dutch and Danish news items do not print 30–25% or 55–50%. I’ll check the charts and the other official series before treating those BIS figures as confirmed.The December 2025 BIS article does state the Dutch 30-to-25 and Danish 55-to-50 figures, but the central-bank releases it cites do not. Those releases print a different Danish dollar-hedge series, which rose in 2025. Company-level Japanese ratios for fiscal 2023–2025 were not in the filings opened here. Taiwan’s 66.39% and 50.23% appear in a news report of an FSC briefing, not in the FSC press release itself. No IMF, BIS, ECB, or Fed estimate of the hedged share of all foreign holdings of US securities for 2023–2026 was found.

| Holder | Country | Ratio and date | Definition (asset class, population) | Source type | URL fetched | QUOTE (≤15 words) |
| --- | --- | --- | --- | --- | --- | --- |
| Dutch pension funds | Netherlands | 30% to 25%, between 2022 and 2024, as stated by BIS | Not defined in the sentence. Cited source is the 17 June 2025 DNB note, which does not print these levels | BIS Quarterly Review article | https://www.bis.org/publ/qtrpdf/r_qt2512b.htm | "Dutch pension funds fell from 30% to 25%" |
| Dutch pension funds | Netherlands | Derivatives offset about 40% of FX losses, Q1 2025 | Flow result, not a stock hedge ratio. All pension-fund FX losses, not a dollar-only policy ratio. Look-through of Dutch investment funds | DNB statistical news, 17 June 2025 | https://www.dnb.nl/en/general-news/statistical-news/2025/weaker-us-dollar-hits-pension-funds-harder-than-falling-stock-prices/ | "offsetting some 40% of their foreign exchange losses" |
| Dutch pension funds | Netherlands | "some 50%" and, in the next paragraph, "some 40%", last five years | The page describes the equity–dollar correlation, and it also says fixed income is the main hedged book. The two percentages conflict | Same DNB note | same URL | "some 40% of the foreign exchange risk" |
| Danish insurers and pension funds | Denmark | "about 55% to 50%", between 2022 and 2024, as stated by BIS | Not defined. Cited source is the 3 July 2025 Nationalbanken note, which does not print 55% or 50% | BIS Quarterly Review article | https://www.bis.org/publ/qtrpdf/r_qt2512b.htm | "fell from about 55% to 50%" |
| Danish insurers and pension funds | Denmark | 61.8% at the start of 2025 to 73.5% at end-May 2025 | Share of dollar investments hedged. Insurance companies and pension funds. Dollar assets were about kr. 1,431 billion, 30% of investments | Nationalbanken statistical news, 3 July 2025 | https://www.nationalbanken.dk/en/news-and-knowledge/data-and-statistics/insurance-and-pension/20250703-insurance-companies-and-pension-funds-hedge-more-against-dollar-decline | "from 61.8 per cent to 73.5 per cent" |
| Danish insurers and pension funds | Denmark | 70.7% in November 2025 to 72.2% at end-2025 | Dollar hedging of the insurance and pension sector | Nationalbanken statistical news, 2 February 2026 | https://www.nationalbanken.dk/en/news-and-knowledge/data-and-statistics/insurance-and-pension/20260202-this-years-pension-return-driven-by-equities-and-currency-hedging | "from 70.7 per cent in November to 72.2 per cent" |
| Danish insurers and pension funds | Denmark | Prose: about 70% in March 2024. Table: hedged dollar exposure kr. 998.3 billion of kr. 1,555.4 billion, which is 64.2% | Hedged dollar exposure divided by total dollar exposure, including hedges to euro and to kroner. Sector reports to Nationalbanken; series DNFPVALE | Nationalbanken statistical news, 2 May 2024 | https://www.nationalbanken.dk/en/news-and-knowledge/data-and-statistics/insurance-and-pension/20240502-extended-statistic-on-currency-exposure-and-hedging | "Nearly 70 per cent of the dollar exposure is thus hedged" |
| Danish pension sector (same insurers and pensions) | Denmark | "around 70 per cent" in February 2024; a footnote says 67% | Hedged dollar exposure over total dollar exposure. US stocks are about 75% of dollar assets | Nationalbanken economic memo, 2 May 2024 | https://www.nationalbanken.dk/media/i5qlfplp/currency-hedging-and-the-danish-pension-sector.pdf | "hedge ratio of dollar exposures was 67 per cent" |
| Danish insurers and pension funds | Denmark | Euro hedge ratio "nearly 40 per cent" in March 2024; memo says it fell about six points from October 2022 to February 2024 | Euro exposure hedged to kroner, not the dollar hedge ratio. Table: kr. 676.2 billion hedged of kr. 1,773.7 billion | Same May 2024 statistic and memo | both Nationalbanken URLs above | "a hedge ratio of nearly 40 per cent" |
| Japanese life insurers, sector | Japan | BIS: "roughly 60% to 40%", between 2022 and 2024 | BIS attributes this to the Bank of Japan. The October 2025 Financial System Report charts the ratio but does not print 60 or 40 in the text | BIS article, citing the BOJ report | https://www.bis.org/publ/qtrpdf/r_qt2512b.htm | "reduced hedging rates from roughly 60% to 40%" |
| Nine major Japanese life insurers | Japan | Chart only; endpoints not printed in the text layer | General-account currency hedge ratio, estimated from company accounts. Unhedged includes foreign bonds backing foreign-currency policies. Hedge instruments shown: currency swaps and FX swaps | Bank of Japan Financial System Report, October 2025, Chart III-2-4 | https://www.boj.or.jp/en/research/brp/fsr/data/fsr251023a.pdf | "Currency hedge ratios among life insurance companies" |
| Nippon Life | Japan | "Approx. 20%" on a chart whose dates run through March 2023 | FX-hedged share of foreign-currency assets, including currency-swapped bonds. General account. This is end-FY2022, before the requested FY2023–FY2025 window. UNCERTAIN: the text layer jumbles the label and the date | Company investor presentation, January 2024 | https://www.nissay.co.jp/global/report/pdf/h1_fy2023_investor_presentation.pdf | "Approx. 20%" |
| Nippon Life, Dai-ichi Life, Meiji Yasuda, Sumitomo Life | Japan | No printed hedge ratio for FY2023, FY2024, or FY2025 in the filings opened | Sumitomo’s October 2025 slides give portfolio shares, including hedged foreign bonds at 8.6% of the general account at June 2025. That is a portfolio weight, not a hedge ratio | Company slides and results notes | https://www.sumitomolife.co.jp/about/pdf/company/ir/irlibrary/ir20251027.pdf ; https://www.nissay.co.jp/global/news/pdf/20250523a.pdf | "うち為替ヘッジ付外債" |
| Taiwan life insurers | Taiwan | 66.39% at end-2024; 50.23% at end-2025, as reported from the FSC briefing | Foreign investment after deducting foreign-currency policies: NT$15.6 trillion at end-2024 and NT$15.4 trillion at end-2025. Life insurers | Central News Agency report of the 27 January 2026 FSC briefing | https://www.cna.com.tw/news/afe/202601270363.aspx | "2025年底避險比率為50.23%" |
| Taiwan life insurers | Taiwan | Hedge ratio not printed | The FSC’s own 27 January 2026 release gives profits, hedging gains and losses, and the FX valuation reserve (NT$613.7 billion), not the ratio | FSC press release | https://www.fsc.gov.tw/ch/home.jsp?dataserno=202601270003&dtable=News&id=96&mcustomize=news_view.jsp&parentpath=0 | "外匯價格變動準備金之累積餘額為6,137億元" |
| Taiwan life insurers | Taiwan | Rule dated 29 August 2024, not 2025 | Optional new FX valuation reserve: extra provision/offset raised to 100%, fixed provision to 1.2%, traditional hedge-cost provision removed, and specified liability reserves may be transferred in | FSC press release | https://www.fsc.gov.tw/ch/home.jsp?dataserno=202408290002&dtable=News&id=96&mcustomize=news_view.jsp&parentpath=0 | "提高壽險業管理匯率風險之彈性" |
| Insurers, pension funds, and mutual funds worldwide | Several | About 44%, 35%, and 21% as of June 2020 | Share of dollar securities hedged, by sector. IMF cites Du and Huber; it does not recompute this for 2023–2026 | IMF GFSR, October 2025, Chapter 1 | https://www.imf.org/-/media/files/publications/gfsr/2025/october/english/ch1.pdf | "considerably less than 100 percent" |

**What can and cannot be said.** Published sector ratios exist, and they are not interchangeable. Nationalbanken’s dollar hedge ratio is hedged dollar exposure over total dollar exposure for insurers and pension funds, including hedges into euro as well as kroner. That series was about 64% on the March 2024 table, described in the same release as nearly 70%, 67% in February 2024 in the memo, 61.8% at the start of 2025, 73.5% at end-May 2025, and 72.2% at end-2025. The BIS 55-to-50 claim uses the same population and cites that July 2025 release, but the release’s printed movement is a 2025 rise from 61.8% to 73.5%, and no fetched Nationalbanken page contains 55% or 50%. The gap is therefore not only a later reversal of one series. A bond-only or kroner-only slice was not found; the March 2024 dollar book hedged straight into kroner was kr. 292.1 billion of kr. 1,555.4 billion. DNB’s cited note likewise does not say 30% or 25%. Its 40% is the share of Q1 2025 FX losses offset by derivative gains, and the same page gives both 40% and 50% for a five-year equity–dollar correlation. The Bank of Japan chart covers nine life insurers’ general accounts and is the series behind the BIS “roughly 60% to 40%,” but those endpoints are the BIS reading, not numbers printed in the report text. Nothing fetched supports one hedged share of all foreign holdings of US securities in 2023–2026. The IMF’s October 2025 chapter repeats June 2020 sector ratios and plots a volatility-minimizing hedge ratio, which is a benchmark, not the share actually hedged.

**UNCERTAIN.** The BIS 30/25 and 55/50 figures may be chart readings that the text extracts missed. Monthly DNFPVALE for 2022–2024, and the chart images on the DNB and July 2025 Nationalbanken pages, would settle that. Nippon Life’s “Approx. 20%” is on a chart through March 2023; the slide image would confirm the date. Printed hedge ratios for Nippon Life, Dai-ichi Life, Meiji Yasuda, and Sumitomo Life for fiscal 2023, 2024, and 2025 were not in the results files opened. The Japan Times page with a later industry compilation was blocked by a bot check. Taiwan’s 66.39% and 50.23% are in the CNA account of the briefing; the FSC release does not print them, and the CNA headline says 50.53% while the body says 50.23%. An FSC statistical table would settle the ratio. The December 2025 FSC accounting-rule page timed out, so that text was not read. The reserve reform that was read, and that was written to allow more flexible hedging, is the 29 August 2024 release.

---

## K6 — Why the CFTC short fell while Form PF's net long rose (find)

I'll start from the claims file and the official CFTC and OFR definitions, then check 2025–2026 official commentary before ranking explanations and a free-data test.The claims file contrasts a shrinking CFTC leveraged-fund futures short with a rising Form PF net long. Next I’ll pull the official definitions and the 2025–2026 commentary that could explain the split.The search results already point to a definitional split and a possible shift from basis trades into swap-spread trades. I’ll fetch the source pages so the quotes and timing details come from the documents themselves.The Fed’s June 2026 note stops in September 2025, and the OFR blog is still describing year-end 2025. I’ll look for 2026 official material on the futures short and for the Form PF measurement rules.The two 2026 prints are different objects on different dates. A smaller CFTC leveraged-fund futures short can sit next to a larger Form PF net long if hedge funds kept repo-financed cash Treasuries and hedged them by paying fixed on interest-rate swaps, because those swaps are not a Treasury short in Form PF. That mechanism is documented through late 2025. Nothing fetched here measures it through the 2026 futures decline, and the quoted windows do not even overlap.

Assumption: the moves to explain are the ones in `claims_cftc_formpf.md` — CFTC leveraged-fund net futures, six CBOT Treasury contracts, face value, from about −$1,154bn at end-2025 to −$774bn on 29 Sep 2026, and Form PF qualifying-hedge-fund net Treasury exposure from about +$791bn on 31 Mar 2026 to +$864bn on 30 Jun 2026. Those series were not re-downloaded.

## DEFINITIONS

| measure | what it includes | what it excludes | URL fetched | QUOTE |
|---|---|---|---|---|
| CFTC Traders in Financial Futures, Leveraged Funds | Reportable futures open interest as of Tuesday, released Friday. One category per trader for all financial contracts, from the predominant business purpose on Form 40. Leveraged funds are hedge funds, CTAs, CPOs, and unregistered funds. Hedge funds stay in this category whether or not they are registered. The claims figure is long minus short, futures only, six CBOT Treasury contracts, converted at contract face value. Calendar-spread offsets sit in a spreading column, so they drop out of that net. | Cash Treasuries, swaps, repo, and OTC forwards. Non-reportable accounts. Dealers, other reportables, and asset managers. A hedge fund whose predominant business is judged to be institutional asset management is classified with asset managers, so its futures never enter this net. CFTC staff have documented that some large basis traders are in Asset Managers on that rule. | https://www.cftc.gov/sites/default/files/idc/groups/public/@commitmentsoftraders/documents/file/tfmexplanatorynotes.pdf | "hedge funds are included in this category, regardless of whether they are registered." |
| CFTC classification rule | Predominant activity of the trader, not of each trade. The same category applies across financial commodities. A Form 40 change of business purpose moves the whole book between categories from one week to the next. Historical COT files are not revised. | Strategy labels. Staff do not observe why a position is held, so a CTA outright short and a basis short are added together. | https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm | "classified in the same category for all commodities." |
| Same rule, applied to basis funds | Some funds that CFTC economists treat as basis traders are nonetheless tagged Asset Manager. | Those futures shorts from the leveraged-fund total. | https://www.cftc.gov/sites/default/files/Basis_trade_Mixon_Orlov_ada.pdf | "Some entities that are categorized as Asset Managers in CoT reports." |
| OFR Form PF long and short Treasury (FPF-ASSETCLASS_LTREASURY_SUM / STREASURY_SUM) | Qualifying hedge funds only: net assets at least $500 million, adviser with at least $1.5 billion of hedge-fund assets. On the legacy form, questions 26 and 30, U.S. treasury securities, long and short, physical, synthetic, and derivative. That covers cash bonds, futures, forwards, and options. Cash is market value. Derivatives other than options are gross notional. Options are delta-adjusted notional. Longs and shorts are gross; the form says not to net inside the sub-asset class. A repo-financed bond stays in the Treasury long. The quoted "net long" is long minus short after OFR aggregates. | Interest-rate swaps, overnight index swaps, and forward rate agreements. OFR puts those in a separate interest-rate-derivatives class, on a 10-year equivalent basis. The repo loan itself is a separate repo line, not part of the Treasury long or short. Funds below the qualifying threshold. Parallel managed accounts, except when testing the threshold. | https://www.financialresearch.gov/hedge-fund-monitor/categories/size/chart-22/ | "include both cash securities and derivatives, such as Treasury futures" |
| Why the swap hedge is invisible | Long cash financed in repo is inside the Treasury long. The pay-fixed swap is not a Treasury short. | IRS from both the long and the short Treasury totals. | https://www.bis.org/publ/qtrpdf/r_qt2512y.htm | "the OFR does not classify IRS as UST exposures." |
| Who files, and when | Large hedge-fund advisers file quarterly within 60 days of quarter-end. Positions are as of the last calendar day of the month. Where the form is monthly, OFR keeps the third month of the fiscal quarter. The monitor's posted rule maps filings to a calendar quarter by report date, so the "30 Jun" bucket is not every fund's 30 Jun balance. Aggregates are revised for amendments and can be winsorized. Qualifying funds are about 85 percent of Form PF hedge-fund gross assets. | Smaller annual filers. Anything after the latest quarter OFR has released. | https://www.financialresearch.gov/hedge-fund-monitor/datasets/fpf/ | "within 60 days after the advisers' fiscal quarter-end." |
| Form in force for the 2026 prints | A quarterly filing submitted on or after 1 Oct 2025 uses the amended form. The Q1 and Q2 2026 reports are in that set. Old section 2a question 26 was deleted. The exposure grid moved. | A clean splice, on the pages fetched, between legacy questions 26/30 and the amended grid. OFR's dataset page still describes questions 26 and 30. | https://www.sec.gov/rules-regulations/staff-guidance/division-investment-management-frequently-asked-questions/form-pf-faq | "on or after October 1, 2025" |

Legacy valuation, which the Fed note used through September 2025: "for derivatives (other than options), value means gross notional value" and, for other investments, "value means market value" (https://www.sec.gov/files/formpf-legacy.pdf). The Treasury line also asks for duration, weighted-average tenor, or a 10-year equivalent as a separate field. The published dollar sums used by BIS for Q2 2025 ($2,379bn long) match the scale of the June 2026 long in the claims ($2,362bn), which is what a gross dollar exposure looks like.

## EXPLANATIONS

| rank | explanation | evidence for | evidence against | URL fetched | QUOTE |
|---|---|---|---|---|---|
| 1 | Shift from the cash-futures basis toward the swap-spread trade: stay long cash Treasuries financed in repo, pay fixed on an interest-rate swap, and buy back the futures. Futures shorts shrink in the CFTC category. Form PF net Treasury rises because the new hedge is not a Treasury short. | From 2024 through Q3 2025 the basis stayed the larger book but stopped growing, while the swap trade accounted for most of the growth in Treasury exposure and repo. BIS's upper bound, long Treasury minus all short Treasury, was $631bn in Q2 2025. The Fed's fund-level match was about $305bn of swap-spread trades and about $830bn of basis trades in September 2025. Dallas Fed: through year-end 2025, net repo kept rising while leveraged-fund futures shorts were roughly flat. BIS in September 2026 still describes basis growth as having moderated and swap trades as having risen from about $100bn to about $300bn. Repo borrowing on Form PF was already $3.0tn by September 2025, in line with the claims' $3.38tn in June 2026. | Those sizes stop in September 2025. The OFR's August 2026 blog, using year-end 2025, still puts short futures near $1.4tn and treats the basis as large. The claims' futures decline is from end-2025 to 29 Sep 2026, and the Form PF rise is only March to June 2026 (+$73bn), against a face-value futures move of about $380bn over a longer span. On 19 Aug 2026 Treasury buybacks compressed long-end swap spreads, which narrows the cheapness that draws the trade. No fetched paper decomposes 2026 positions. | https://www.bis.org/publ/qtrpdf/r_qt2512y.htm | "while remaining the largest, has largely stagnated" |
| 2 | The two "2026" changes are different intervals. Form PF is a quarter-end snapshot with up to a 60-day lag. The cited Form PF rise ends 30 Jun 2026. The cited futures decline runs through 29 Sep 2026. Q3 Form PF is not due until about 29 Nov 2026. | COT positions are Tuesday, released Friday, and are not revised. Form PF quarters on the monitor are built from report-date windows and can be revised. The July–August 2026 money-fund Treasury-repo cut in the claims sits after the Form PF date and inside the CFTC window. A Q3 futures cover tied to that funding pull would not yet appear in Form PF. | This is an explanation of the comparison, not a measured split of positions. It is unsettled until the same Tuesdays nearest 31 Mar and 30 Jun 2026 are computed. If the futures short already shrank in that quarter, timing does not account for the pair. | https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm | "from Tuesday and released Friday." |
| 3 | CTA and macro futures inside Leveraged Funds, plus basis funds parked in Asset Managers. A directional cover, or a reclassification, moves the CFTC net without a matching move in qualifying-hedge-fund cash Treasuries. | The category explicitly includes CTAs and CPOs. Classification follows predominant business, and a Form 40 rewrite moves the entire book. In December 2023, CFTC economists' basis-trader group was net short about $1.04tn, while other leveraged funds were net short about $160bn, so the label is not pure basis. Some of the basis group itself is tagged Asset Manager. | At the 2019 and 2023 peaks those basis funds were about three-quarters of leveraged-fund short futures, so CTAs were the minority. No 2026 classification notice was on the pages fetched. A one-third drop in the aggregate short is large relative to that 2023–24 residual. | https://www.cftc.gov/sites/default/files/Basis_trade_Mixon_Orlov_ada.pdf | "Some entities that are categorized as Asset Managers" |
| 4 | Cash relative-value and curve trades that never use futures: on-the-run versus off-the-run, and steepeners. A duration-neutral steepener is net long face amount, so Form PF net notional rises with no CFTC futures short. | March 2025 SCOOS: the trades dealers most often see against Treasury repo are on-the-run/off-the-run, curve or duration, and the basis. Fed, September 2025: maturity-matched trades about $395bn and steepener-like trades about $375bn of long Treasury exposure. BIS assigned about $688bn of short Treasury exposure in Q2 2025 to relative-value books other than the basis. | Matched long-and-short cash books raise gross exposure and leave net exposure small. They do not, by themselves, reduce an existing futures short. The Fed sizes are through September 2025. | https://www.federalreserve.gov/data/scoos/scoos-202503.htm | "on-the-run versus off-the-run arbitrage, yield curve or duration trades" |
| 5 | Sponsored and centrally cleared repo let funds hold more cash Treasuries per unit of dealer balance sheet. | February 2026 TBAC: repo clearing and sponsored repo support market functioning. March 2025 SCOOS: dealers expected the non-centrally-cleared bilateral share to fall and cleared repo to rise, for netting. Both the basis and the swap trade need that cash leg. | Sponsored repo finances the bond. It does not choose futures versus swaps. Dallas Fed ties money-market spreads to net repo, and treats cash-versus-cash relative value as roughly cash-neutral. No fetched series shows sponsored repo replacing futures hedges in 2026. | https://home.treasury.gov/system/files/221/TBACCharge2Q12026.pdf | "expansion of sponsored repo will assist market functionality." |
| 6 | Units. CFTC face value can fall while rate risk does not, if shorts move from the 2-year and 5-year contracts into the bond contracts. Form PF mixes market-value cash with notional futures. | OFR converts the same TFF contracts both at face value and to 10-year equivalents, because those are different numbers. From 1 Jun to 3 Sep 2026, U.S. 10-year yields rose 31bp. Higher yields mark cash market values down, so the Form PF dollar rise understates any increase in par amount. | A tenor shift does not create a Form PF net long. The yield move works in the wrong direction for a mark-to-market explanation of the Form PF increase. No fetched 2026 breakdown by contract was used. | https://www.financialresearch.gov/hedge-fund-monitor/datasets/tff/ | "multiplying the number of contracts held by their respective contract sizes." |

Supporting lines, same sources: Dallas Fed, 28 May 2026, "short futures positions have remained roughly flat" while net repo rose through year-end 2025 (https://www.dallasfed.org/research/economics/2026/0528). Fed, 22 Jun 2026, "repo cash borrowing has grown to $3.0 trillion as of September 2025" (https://www.federalreserve.gov/econres/notes/feds-notes/decomposing-hedge-funds-u-s-treasury-exposures-20260622.html). BIS, 14 Sep 2026, swap trades "risen from $100 billion to $300 billion in just the past year" (https://www.bis.org/publications/qr-202609/yields-climb-yet-risk-appetite-holds-firm). OFR, 19 Aug 2026, "short futures positions totaled $1.4 trillion" at the year-end 2025 measurement (https://www.financialresearch.gov/the-ofr-blog/2026/08/19/hedge-funds-cash-treasury-holdings/).

## TESTS

| explanation pair | series | expected sign under each | URL of the series |
|---|---|---|---|
| 1. Basis-to-swap substitution during the Form PF window. 2. The futures decline falls outside that window. | CFTC Traders in Financial Futures, futures only. Leveraged Funds long minus short, excluding the spreading column. Sum of CBOT 2-year, 5-year, 10-year, Ultra 10-year, Bond, and Ultra Bond, times contract face value ($200,000 for the 2-year, $100,000 for the others). Compare the Tuesday on or nearest 31 Mar 2026 with the Tuesday on or nearest 30 Jun 2026. | Under 1, the net short shrinks: the face-value net (long minus short) rises, alongside the Form PF net long. Under 2, that March-to-June change is about zero or the short grows; the drop from end-2025 to 29 Sep 2026 sits outside the Form PF dates. | https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm |

If that March-to-June futures short does shrink, the same free file separates substitution from a CTA cover. Asset Manager/Institutional net long in those six contracts should fall with the leveraged-fund short if asset managers are leaving the futures bid that the basis trade had been taking the other side of. It should stay put if the cover is CTA or macro flow and dealers, rather than asset managers, are the other side. The OFR Hedge Fund Monitor interest-rate-derivatives aggregate, which the dataset page defines as 10-year-equivalent swaps, options, overnight index swaps, and FRAs, should become more net pay-fixed under the swap trade and be little changed under a futures-only CTA cover (https://www.financialresearch.gov/hedge-fund-monitor/datasets/fpf/).

## UNCERTAIN

- Whether the 2026 API fields `FPF-ASSETCLASS_LTREASURY_SUM` and `STREASURY_SUM` are still gross dollars (market value for cash, notional for futures) or the amended form's 10-year-equivalent netted exposures. The June 2026 long is almost the same size as the pre-amendment Q2 2025 long, which points to gross dollars. The OFR methodology page still cites legacy questions 26 and 30. A current series note, or the monitor's data dictionary after the October 2025 form change, would settle it.
- Whether OFR's 2026 quarter dates are true calendar quarter-ends. The FAQ says large advisers move to calendar-quarter reporting for the quarter ending 31 Dec 2025. The monitor page still describes fiscal report-date windows. The monitor's own update would settle it.
- The March-to-June 2026 path of the futures short. That is the test above. It was not computed in this session.
- Any official split of hedge-fund Treasury exposure after September 2025. The swap-substitution account of the 2026 futures decline is an extrapolation from the 2024–25 pattern.
- How many 2026 basis funds are classified as asset managers. COT files do not name traders. A CFTC staff update, or a published classification notice, would settle it.
- Whether `FPF-BORROW_REPO_SUM` is gross repo borrowing or net of reverse repo. The claims' $3.38tn lines up with the Fed's $3.0tn gross borrowing in September 2025, and not with the Dallas Fed's $1.8tn net at year-end 2025. The series definition on the monitor would settle it. The repo chart page was not fetched.


---

## Supervisor adjudication of wave 3

**Corrections registered from wave 3:** C-139 (K4: long money graded Measured for AI names), C-140 (K2: Bassman claim 6), C-141 and
C-142 (K1: the gold and crude framings).

| Parcel | What the supervisor checked at source | Ruling |
|---|---|---|
| K1 | Our own COT ledgers: gold group nets (swap dealers −187,332 to −225,026; producers −45,013 to −19,501), WTI managed money 15,743 (30 Dec 2025) to 111,731 (8 Sep 2026) to 53,598 (6 Oct), copper 60,185 to 61,134 with an 82,522 peak | C2 **FALLS, accepted** (C-141). C7/C8 **WEAKENED, accepted as a correction** (C-142): the end-2023 comparison hid the 2026 build. C3, C4, C5, C6, C9, C10 **WEAKENED, reworded** in the E-021 map. C1 stands. The IEA/OPEC outside estimates are relayed, not re-read. |
| K2 | Z.1 F.3.2 (11 Sep), year to 2026Q2: Fed bills +291.8, coupons −27.5; life insurers' coupons +28.2; private DB −2.7; DC +61.3; state and local pensions +71.6; rest of the world's share of coupon issuance 35.0% (2024), 27.3% (2025), 20.3% | Claim 6 **too harsh, accepted** (C-140). Claim 5 **too harsh, rejected**: the buyer change holds in coupons too. MOVE row reproduced by Grok on the note's method; the method is now stated in the note. |
| K3 | Morgan Stanley's permitted collateral, XBRL: $1,382.658bn (Jun 2026), $1,120.277bn (Jun 2025) | Accepted. Four-dealer re-use share 84.0% (2026) against 82.6% (2025), recorded in the collateral dossier and the Singh calendar row. |
| K4 | Bank of England FSR, Jul 2026 ("just 3% of the stock of outstanding US IG debt"; over 15% of issuance by early May); CPRAM ("close to 5% of the overall index", 7.5% long end) | Accepted as evidence; the verdict "untestable on free data" is partly rejected (N-PORT counts registered funds by security). The page's grade is corrected (C-139). |
| K5 | BIS QR Dec 2025 text, verbatim: Japan roughly 60% to 40%, Dutch 30% to 25%, Danish about 55% to 50%, 2022–2024 | Accepted: the BIS sentences exist; the cited central-bank releases do not print them (Grok); the Danish release shows a 2025 rise (supervisor re-read earlier). Taiwan's reserve reform is dated 29 Aug 2024, which corrects the parcel's premise. |
| K6 | OFR chart notes ("Treasury exposures include both cash securities and derivatives, such as Treasury futures"); OFR API long/short by quarter; our CFTC file at 31 Mar and 30 Jun 2026 | Accepted in part. Explanation 2 (timing) **fails** on the test: the futures short shrank inside the Form PF window. The "conflict" is mis-posed; recorded in the E-021 map, "The levered bid, re-read". Swap substitution stays open with a named test. |

