# Grok scoping of the next free-data measurements, 30 Oct 2026 (g14)

**Parcel:** `page.html` (docs/index.html at d0d59ef), Grok 4.7 256K Extra High through the fenced Cursor lane, 1041 s, 20 searches,
27 fetch calls, no blocked or unexpected tool. One URL in the answer (a CME legal-text file, candidate 5) was never fetched and is dropped.
The parcel listed what is built or declined and forbade computing any result from the data found.

**Supervisor's rulings (30 Oct):**
- **Take forward (1), the collateral re-use share before 2026, as g14.** It tests the page's collateral verdict ("No measure shows
  collateral re-use rising before the price rise") on a history the project has not measured: the repo holds the share only at June 2025
  and June 2026 (CALENDAR row 2026-11-16). Coverage checked by the supervisor on 30 Oct on data.sec.gov companyconcept (counts of 10-K/10-Q
  period-ends only, no values read): FairValueOfSecuritiesReceivedAsCollateralThatHaveBeenResoldOrRepledged and ...ThatCanBeResoldOrRepledged
  each have 66 period-ends from 2009-12-31 to 2026-06-30 for JPMorgan Chase and Goldman Sachs; State Street 52 each (2013-12-31 to 2026-09-30);
  BNY numerator 53 (from 2010) but denominator only to 2017-06-30; Citigroup denominator only (17 year-ends); Morgan Stanley and Bank of America
  are not on these standard tags (custom tags; the 5 Nov census row already hand-pulls them). A spec is written before any value is read.
- **(2) SVIX (Martin's index premium): declined.** Built from OptionMetrics and CRSP through WRDS, so not re-derivable on free data; the
  documented sample ends August 2025; no licence stated.
- **(3) EFA against Z.1 non-financial net issuance: take as a small follow-up after g14.** It may close the ledger's "unresolved" row; the
  annual-rate versus quarterly-rate units trap is noted.
- **(4) EFA IPO series: not now.** Its 2017 note sources IPOs from Thomson Reuters SDC; at most a cross-check of the vendor universe later.
- **(5) LBMA London vault data: not now.** No stable file URL found and terms unchecked.

The candidates are Grok's. Apart from the coverage counts above, the supervisor has not re-read each source.

## Return

GAPS
- Who bought inside the household line: the holder side cannot be split by legal entity on free data.
- What the multiple’s resilience was made of: a third premium series that does not share a bond leg is still missing.
- Whether the off-balance-sheet lease stack is fragile: the September tests have not reported; they are queued in §10.
- Quarter-end funding stress: June and September did not show it; December is queued on the prints; the swap tape has no daily series for a week to three months.
- The term premium: US models and the survey split on years five to ten; no free German series; Japan’s split depends on the model.
- Private defined-contribution flows after 2023: Form 5500 tables stop in 2023, with the 2024 tables expected around December 2026.
- Two Fed series for non-financial net issuance differ, and the cause is not identified.
- Whether the corporate-bond holder mix holds most of the AI debt is not measured; free data count only two holder groups.
- Bank lending to the build-out itself is the unmeasured part of the industry exposure.
- How much foreign demand is hedged is still not measured.
- UK gold export declarations leave out customs-warehouse metal from May 2016, and unreported central-bank gold is not measurable on free data.
- Whether ETF buying and mutual-fund selling are the same money is not measurable on free data.
- IPO allocations are not recoverable, and the vendor total’s universe is not stated.
- Large-bank collateral re-pledge shares before the first half of 2026 are not measured.
- The JODI stock panel is not the world: China, Russia and most Gulf states do not report.
- FICC-cleared repo is booked under the US, so a country line can reappear there.
- Whether Treasury supply moved yields is not measured; the refunding-day test is queued for 4 November.
- The Fed’s share of duration supply still depends on a refinancing split the Treasury does not publish.
- Already queued, so not proposed: Amazon’s term loan, third-quarter filings, the 4 November refunding, the BIS dollar forwards-and-swaps print, the December Z.1 and Oracle guarantee, the 4 January quarter-end, and the fiscal-2026 revenue-recognition window.

CANDIDATE 1
- GAP: “earlier shares are not measured”
- SOURCE URL: https://data.sec.gov/api/xbrl/companyconcept/CIK0000019617/us-gaap/FairValueOfSecuritiesReceivedAsCollateralThatHaveBeenResoldOrRepledged.json
- QUOTE: “Fair Value of Securities Received as Collateral that Have Been Resold or Repledged”
- ACCESS: Direct JSON, no key, quarterly. The same filer’s companyconcept file for the denominator tag, FairValueOfSecuritiesReceivedAsCollateralThatCanBeResoldOrRepledged, was fetched too. Both files contain period-ends from 2009-12-31 through 2026-06-30. The 2019 10-K rendering names both lines: https://www.sec.gov/Archives/edgar/data/19617/000001961720000257/R200.htm
- TERMS: No licence statement on the JSON. These are public SEC exhibits. UNCERTAIN what a separate SEC developer-terms page would add.
- DESIGN: The population is the large banks already inside the page’s re-pledge share. This session read the two tags for JPMorgan Chase only. The statistic is collateral resold or repledged divided by collateral permitted to be resold or repledged, taking each quarter from the original 10-Q. The comparison window is year-ends from 2009 through 2025 against the first half of 2026 already on the page.
- TRAP: Revisions. The same period-end is repeated in later filings, so a later accession can replace the original print. Summing banks would also double-count collateral passed from one large bank to another. UNCERTAIN whether 81.7% to 83.2% uses this pair of lines; the overview does not name the form. The same tags at the other banks were not fetched.

CANDIDATE 2
- GAP: “A third premium series that does not share a bond leg”
- SOURCE URL: https://personal.lse.ac.uk/martiniw/oiret.html
- QUOTE: “svix_market_monthly.csv Monthly time series, 1996–2025.”
- ACCESS: Direct CSV, no key, month-end and daily. The readme, fetched at https://personal.lse.ac.uk/martiniw/readme.pdf, says the sample runs from 4 January 1996 to 29 August 2025 and defines the index premium as the gross risk-free return times SVIX squared. The download page’s “1996–2025” label is wider than that end date. UNCERTAIN which end date is in the CSV; the last date row was not opened.
- TERMS: No licence is stated on the data page or in the readme.
- DESIGN: The population is the S&P 500 index in the published index file, at the 365-day horizon. The statistic is that option-implied expected excess return, a lower bound built from option prices. The comparison window is December 2023 through August 2025, the overlap with the page’s premium window, set beside the page’s own premium.
- TRAP: A series that only looks free. The readme builds it from OptionMetrics and CRSP through WRDS, so it cannot be re-derived on free data. A zero-coupon rate multiplies the variance and sets the forward, so a short rate is inside the series. The documented sample ends in August 2025, before the page’s first-half 2026 giveback. A CBOE VIX series on FRED was fetched and not used: https://fred.stlouisfed.org/series/VIXCLS says “Copyright, 2016, Chicago Board Options Exchange, Inc. Reprinted with permission.”

CANDIDATE 3
- GAP: “the cause is not identified”
- SOURCE URL: https://www.federalreserve.gov/releases/efa/equity-issuance-retirement-quarterly-historical.txt
- QUOTE: “Equals series FA103164155.Q of the Financial Accounts of the United States … divided by 4.”
- ACCESS: Direct text file, no key. The matching Z.1 series page, fetched with no key, is https://fred.stlouisfed.org/series/BOGZ1FA103164155Q (quarterly, and the chart axis runs back to 1946). ALFRED’s page for the same id lists release dates and loaded with no key: https://alfred.stlouisfed.org/series?seid=BOGZ1FA103164155Q. A direct vintage CSV for 12 June 2026 returned HTTP 500, so scripted vintage download is UNCERTAIN.
- TERMS: No licence restriction is stated in the file header or on the FRED series page.
- DESIGN: The population is domestic nonfinancial corporate net equity issuance, excluding equity REITs, as both files define it. The statistic is the EFA quarterly-rate net beside the Z.1 series divided by four, vintage by vintage. The comparison window is 2024:Q1 through 2026:Q2, including the 13 September print the page already distinguishes from the current vintages.
- TRAP: Revisions, and a units trap. The EFA text file on that URL is the current file, not an archive of past EFA releases. Treating the annual rate as a quarterly rate would manufacture an offset. The 2017 methods note was fetched; it is not a current data dictionary.

CANDIDATE 4
- GAP: “a vendor figure; its universe is not stated”
- SOURCE URL: https://www.federalreserve.gov/releases/efa/equity-issuance-retirement-monthly-historical.txt
- QUOTE: “IPO (initial public offering) issuance includes new equity issuance by companies that were not previously publicly traded.”
- ACCESS: Direct text file, no key, monthly. The header fetched this session does not state the first or last month. A 2017 Fed note, fetched at https://www.federalreserve.gov/econres/notes/feds-notes/equity-issuance-and-retirement-by-nonfinancial-corporations-20170616.html, says the monthly download began in January 1994. UNCERTAIN whether the current file still starts then. The EFA index, fetched at https://www.federalreserve.gov/releases/efa/enhanced-financial-accounts.htm, says “Equity Issuance and Retirement Updated September 18, 2026.”
- TERMS: No licence statement in the file header.
- DESIGN: The population is the Fed’s nonfinancial first-time public offerings, not the eight prospectuses and not Renaissance’s list. The statistic is monthly funds raised, summed over the 2026 months the file actually contains. The comparison window is calendar 2026 against the same months in 2015–2019, and against the page’s prospectus total.
- TRAP: A series that only looks free. The 2017 note says “Nonfinancial IPO and SEO issuance are obtained from Thomson Reuter's SDC Platinum software.” UNCERTAIN whether the 18 September 2026 update still uses that paid source. The file can also omit a 2026 deal the prospectus count includes, or include deals that count does not.

CANDIDATE 5
- GAP: “metal held in customs warehouses is outside the figures”
- SOURCE URL: https://www.lbma.org.uk/prices-and-data/london-vault-data
- QUOTE: “Starts from July 2016, when the current set of custodians were established”
- ACCESS: Monthly, one month in arrears. The page titles a September 2026 release and describes a vault-holdings series; this fetch did not return the workbook’s href, so a stable direct-file URL is UNCERTAIN. The Bank of England custody series was fetched separately at https://www.bankofengland.co.uk/statistics/gold (“the weight of gold we have in our custody on the last business day of each month”) and https://www.bankofengland.co.uk/news/2020/september/increased-transparency-of-london-gold-holdings (one-month lag). The Bank file’s start date was not on those pages.
- TERMS: The October 2022 LBMA FAQ, fetched at https://www.lbma.org.uk/articles/monthly-faqs-october-2022, says “LBMA now freely publishes monthly vault holding data.” No formal licence page was fetched. No licence text was on the Bank’s gold page. UNCERTAIN whether either source bars a published derived comparison.
- DESIGN: The population is loco-London vault gold, commercial vaults plus Bank of England custody, inside the M25. The statistic is month-end ounces, with the Bank’s own custody file kept beside the LBMA total so the Bank is not added twice. The comparison window is July 2016 through the latest shared month, set beside the project’s monthly UK export declarations to China and Hong Kong.
- TRAP: Double counting if the LBMA total, which includes the Bank, is added to the Bank’s file. The series is a stock of metal in London. It does not fill in customs-warehouse shipments, and it does not identify unreported central-bank buying.

RANKING
1. Candidate 1. It is the only one that can change the collateral channel’s “not the source” line, because that line rests on re-use before the price rise being unmeasured, and the same two tags already run from 2009 through June 2026.
2. Candidate 2. The overview says this is the series that would settle the multiple, but the file cannot be rebuilt on free data and the readme stops in August 2025, so the page could add an option-implied premium only through that date.
3. Candidate 3. Naming the offset would let the supply section stop treating the two net-issuance series as unmixable; it would not change the finding that operating companies retired equity.
4. Candidate 4. A stated-universe IPO total would replace the vendor denominator in the “half to two-thirds” sentence; the eight-deal prospectus count would still stand on its own.
5. Candidate 5. It can sit beside the export caveat as the London stock from July 2016; it leaves unreported central-bank buying unmeasured.

NONE FOUND
- A published week-to-three-month FX-swap basis. The CME repository page was fetched and says FX transaction files exist as daily zip/csv (https://www.cmegroup.com/market-data/repository/data.html); a daily file was not opened, so the tenor is not shown. https://www.cmegroup.com/ftp/pub/sdr/fx/ftp-legal-verbiage.txt returned HTTP 400. The ECB exchange-rate methodology URL timed out twice and is not cited.
- A free scriptable third holder file for named AI bonds. NAIC’s financial-statement page was fetched (https://content.naic.org/prod_serv_financial_home.htm): individual statements are purchased, and bulk CSV requires a licence agreement and payment.
- FICC repo split by the dealer parent’s country. The OFR page was fetched (https://www.financialresearch.gov/hedge-fund-monitor/datasets/ficc/) and describes aggregate sponsored repo and reverse repo. It lists no parent-country series.
- A non-PDF official hedge ratio for Japanese life insurers. The Life Insurance Association of Japan monthly index was fetched (https://www.seiho.or.jp/english/statistics/summary/) and lists Excel files from fiscal 2019 through August 2026. The index does not name a hedge ratio. The workbooks were not opened, so a hedge column inside them is UNCERTAIN.
