# Grok scoping of the next free-data measurements, 26 Oct 2026 (g11)

Grok 4.7 via Cursor, fenced to read and web only; it read the page (docs/index.html at 9b245ba) and fetched 19 pages. No breaches or blocked attempts; every cited URL fetched in the call.

**Supervisor's choice (26 Oct):** take forward (2) who held the 2026 IPOs at their first quarter-end, from SEC Form 13F data sets (the supervisor fetches the SEC files), and (3) public-pension contributions and benefits after 2023, from the Census Annual Survey of Public Pensions. Not now: (1) the ECB Survey of Monetary Analysts, because its PDF bars copying without written consent and it would only bound the German term premium; (4) the Livingston Survey, a panel of about a dozen forecasters; (5) primary-dealer collateral, a different population from the large-bank measure already scored. The candidates are Grok's; the supervisor has not yet re-read each source.

## Return

I'll read the project overview first, then look up free public sources for the gaps it still names.The overview leaves a short list of gaps that are still open. I’ll look for free official series that could measure those, and that the page does not already use.The page’s open holes are these. Inside the Fed’s household line, the holder is still a residual. Revenue-recognition timing is the last earnings-quality piece. The multiple’s residual still needs a third series that does not share a bond leg. The lease tests, the December funding prints, the Treasury refunding test, and the BIS dollar-forward notional are already queued. The US term premium is a disagreement between models and a survey on years five to ten. Germany has no free series, and the page says that was not re-searched. Japan’s split depends on the model. Retirement flows stop at 2023. IPO buyers are unknown. The flow-to-price bridge failed four times on free data. How much foreign Treasury demand is hedged is unmeasured, as is central-bank gold that is not reported, and the swap tape has no one-week to three-month series.

Assumption: a source counts as already used only if this page names it. Form 5500, EDGAR XBRL, N-PORT, Z.1, ICI, Bundesbank yields, and the DTCC tape are already in use. Nothing below is a claim that a flow or a position moved a price.

## 1. German survey residual on the 10-year Bund

**Open question:** “no free series found (not re-searched)”

**Source:** ECB Survey of Monetary Analysts, [release list](https://www.ecb.europa.eu/stats/ecb_surveys/sma/html/all-releases.en.html) and the [September 2026 results](https://www.ecb.europa.eu/stats/ecb_surveys/sma/shared/pdf/ecb.smar260911_september.en.pdf). Free to view, no login. Aggregates are PDF from June 2021 and CSV from June 2022, back to June 2021. About eight rounds a year. The September 2026 round (69 respondents) has the median €STR path by quarter through 2029Q4, a long-run anchor, and the German 10-year only at 12 and 24 months ahead. The PDF says copying needs the ECB’s prior written consent. The [site disclaimer](https://www.ecb.europa.eu/services/disclaimer/html/index.en.html) does not grant a reuse licence.

**Design:** Measure the last 2023 round and the September 2026 round: the median €STR at each dated quarter, and the long-run median. Set each beside the 10-year Bund yield on those dates. Unit: percentage points. Denominator: the change in that Bund yield. Test, fixed in advance: the long-run anchor’s change as a share of the yield change; report the dated path’s change separately. The remainder is an upper bound on everything else in the yield, including the term premium. Main trap: most of a ten-year average is the single long-run number, because the dated path ends in 2029.

**Trap:** This is a survey bound. It is the same kind of object the page already refuses to call a measurement for Japan. The PDF licence may also bar republishing the medians.

## 2. Who held the 2026 IPOs at the first quarter-end

**Open question:** “Who was allocated the shares is not recoverable on free data”

**Source:** SEC Form 13F data sets, [bulk page](https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets). Free quarterly ZIPs, July 2013 through August 2026. [SEC FAQ](https://www.sec.gov/about/webmaster-frequently-asked-questions): government-created content and EDGAR filings are free to access and reuse. The official list of which securities belong on Form 13F is PDF-only because of the CUSIP licence. Scripted access is capped at 10 requests a second.

**Design:** For each 2026 operating-company deal, sum shares reported by 13F managers at the first quarter-end on or after listing. Unit: that sum divided by shares outstanding in the prospectus. Test: the share, deal by deal and weighted by the page’s new-money total, plus the concentration in the largest filers. Descriptive. The allocation book stays unread. Main trap: the August 2026 ZIP is filings through August, so it covers quarter-ends through 30 June 2026. Later listings wait for the next ZIP.

**Trap:** Managers under $100 million are absent, confidential treatments drop names, and adding N-PORT on top would double-count funds. Listing dates are not in the page, so how much of the $112bn is inside the June window is unknown.

## 3. Public-pension contributions and benefits after 2023

**Open question:** “Retirement flows after 2023”

**Source:** Census Annual Survey of Public Pensions, [2025 release](https://www.census.gov/newsroom/press-releases/2026/2025-aspp.html), [tables](https://www.census.gov/data/tables/2025/econ/aspp/aspp-historical-tables.html), and the [2025 publication](https://www.census.gov/library/publications/2026/econ/aspp-2025.html). Free CSV. Annual since 1957. A census in years ending in 2 or 7; other years are a sample whose national totals stand for the universe. The 2025 release reports $315.02bn of contributions and $418.25bn of benefit payments, against $6.49trn of assets. No fee is stated. The open-data policy page did not load.

**Design:** Measure employee plus government contributions, and benefit payments, for 2024 and 2025. Unit: benefit payments per dollar of contributions, and per dollar of same-survey assets. Test: those ratios against the same survey’s 2013–2023 run, using 2022 as the last census year. Descriptive cash accounts for state and local defined-benefit plans. Main trap: a benefit payment is not a sale of equities, and a contribution is not an equity purchase.

**Trap:** This does not extend the private defined-contribution series in §07. That extension is the 2024 Form 5500 file of a source the page already uses.

## 4. Expected profit growth with no bond in the formula

**Open question:** “A third premium series that does not share a bond leg”

**Source:** Philadelphia Fed Livingston Survey, [historical workbooks](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/livingston-historical-data) (page updated 24 June 2026) and the [June 2026 release](https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/livingston-survey/2026/livjun26.pdf). Free. Twice a year. The June 2026 panel has 17 forecasters; 12 answered corporate profits after taxes, 11 the S&P 500. The pre-1990 stock-price file is discontinued and is not part of the official set. No separate reuse licence is printed on these pages.

**Design:** Measure the median forecast for the growth of corporate profits after taxes in the December 2023 survey and the June 2026 survey. Unit: annualized percent. Denominator: the December 2023 forecast, so the result is a revision in expected profit growth. Test: the sign and size of that revision. Leave the 10-year bond forecast in its own column and do not subtract it. Main trap: NIPA profits are not S&P earnings, and the panel is a dozen people.

**Trap:** A higher profit forecast does not, by itself, assign a share of the 49bp. The page already says the 2015–19 growth sensitivity is not a finding. The S&P level in the same file mixes cash-flow news and discount-rate news, so it is the wrong column for this question.

## 5. Dealer collateral before the equity window

**Open question:** “earlier shares are not measured”

**Source:** New York Fed primary dealer statistics, [data tool](https://www.newyorkfed.org/markets/counterparties/primary-dealers-statistics) and the [release page](https://www.newyorkfed.org/markets/primarydealers). Weekly CSV, XML, and JSON. The tool covers 28 January 1998 to the present, split where the form changed, updated Thursdays. [FR 2004C](https://www.newyorkfed.org/banking/reportingforms/FR_2004A_B_C) collects repo, reverse repo, securities borrowed or lent, and collateralized loans. The Bank does not audit the figures. The [terms page](https://www.newyorkfed.org/terms-of-use) returned no licence text.

**Design:** Measure securities lent per dollar of securities borrowed plus securities lent, weekly, and only inside one published form structure. Unit: a share. Denominator: borrowed plus lent, from FR 2004C. Test, fixed in advance: whether that share in the last complete pre-2024 structure sits above or below its 2024–25 counterpart inside the same structure. Descriptive timing. Main trap: these are primary dealers, a different population from the large-bank re-pledge ratio already scored.

**Trap:** A higher dealer ratio would reopen the timing question. It would still leave the price link unmeasured, which is the failure already recorded in §06.

## REJECTED

- **Private defined-contribution flows after 2023, via a new source.** The [Form 5500 datasets](https://www.dol.gov/agencies/ebsa/about-ebsa/our-activities/public-disclosure/foia/form-5500-datasets) already include a 2024 file and a 2025 “latest” file, refreshed about monthly. That is the source the page already uses. The 2025 file is an incomplete vintage.
- **The flow-to-price bridge.** The page marks it closed on free data. No new free file found here assigns the treatment the four failed designs lacked.
- **Dollar FX forwards, and the one-week to three-month basis.** The BIS notional test is already written down for 16 November. [CME settlement history](https://www.cmegroup.com/articles/faqs/access-to-cme-group-settlement-data-faq.html) that could proxy short forwards is DataMine, from about $105 a month. The website view after midnight is free to look at and is not a scriptable history.
- **Another US term-premium model.** The page already has models and a survey that part on years five to ten. A third model would restate that disagreement.
- **Splitting the household residual by legal entity.** The page says the last free route closed. A wealth split is a different object, and the page says it would not bet on one.
- **Insurer-level AI bond holdings, Japanese life-insurer hedge ratios, and dividend futures.** No free bulk file with a clear reuse licence was confirmed for any of the three. Without that, they cannot carry a denominator for “most of the AI debt,” “how much foreign demand is hedged,” or the growth side of the 49bp.
- **Revenue-recognition timing.** The structured filings are EDGAR XBRL, already in the footer. The hole is an unbuilt measurement, not a missing source.
- **Lease draws, December funding prints, and the refunding-day yield test.** Already queued on sources the page has.

## UNCERTAIN

- Whether the SMA CSV, as distinct from the September 2026 PDF, may be reused. The PDF forbids copying without written consent. The HTML page publishes the CSV and does not repeat that sentence.
- The €STR horizon in the last 2023 SMA round was not opened. If that round’s dated path is shorter than September 2026’s, the two rounds are not the same object.
- How many of the eight IPOs, and how much of the $112bn, listed on or before 30 June 2026.
- The unnamed survey that fell 19bp is probably not Livingston. Livingston publishes profit growth and an index level. That identification is an inference.
- Written reuse terms for Census, Livingston, and the New York Fed dealer files were not on the pages that loaded. Access is free and there is no login. The Census policy page timed out. The New York Fed terms page returned no licence text.
- Dealer form-break dates were not read from the definition file. The comparison has to stay inside one structure the file itself labels.
