# Grok scoping of the next free-data measurements, 28 Oct 2026 (g13)

**Parcel:** `page.html` (docs/index.html at 029860c), Grok 4.7 256K Extra High through the fenced Cursor lane, 892 s, 17 searches,
19 fetches, no blocked or unexpected tool, no URL cited without a fetch. The parcel named gaps (a) to (h) from "The gaps that remain"
and the currencies-and-commodities section, listed what is built or declined, and forbade computing any result from the data found.

**Supervisor's rulings (28 Oct):**
- **Take forward (1), revenue-recognition timing**, from SEC XBRL on data.sec.gov (the frames API rather than the notes ZIPs, which
  repeat totals inside timing buckets). It is the last open piece of earnings quality on the page. Coverage was checked by the
  supervisor on 28 Oct (entity counts only, no values summed): `ContractWithCustomerLiability` 1,366 filers at CY2023Q4I and 960 at
  CY2026Q2I; `ContractWithCustomerAssetNetCurrent` 571 and 464; `RevenueRemainingPerformanceObligation` 798 and 674;
  `ContractWithCustomerLiabilityCurrent` 2,064 and 1,573. Year-end instants carry fuller note disclosure than quarter-ends.
- **(2) Defined-contribution flows for 2024: not from the raw Form 5500 data sets.** The page's 2013-2023 run comes from the
  Labor Department's published Private Pension Plan Bulletin, whose filters a raw aggregate would not reproduce. The 2023 Abstract
  was published in December 2025, so the 2024 Abstract is expected around December 2026; a CALENDAR row reads it then. dol.gov
  returned 403 to the supervisor's script on 28 Oct, so that read goes through a fenced Grok fetch, not a workaround.
- **(3) SPF corporate-profit forecasts (CPROF): not now.** It is a short-horizon forecast of national-accounts profits, a reading of
  the growth leg, not the premium series without a bond leg that the gap asks for.
- **(4) SPF BILL10: already used.** `bin/r1_treasury_decomposition.py` builds the years-five-to-ten survey leg from BILL10 (C-125,
  C-150); Grok's UNCERTAIN line is resolved.
- **(5) Japanese life insurers' hedge ratios: not now.** Semiannual PDFs per insurer, one holder class, foreign securities rather
  than Treasuries.
- **Germany's term premium was searched again** (four sources fetched; none publishes a premium series). The page line "not
  re-searched" is updated with the next page edit. The World Gold Council's terms bar publishing derived data, as before.

The candidates are Grok's. Apart from the coverage counts and the BILL10 check above, the supervisor has not re-read each source.

## Return

I'll read the project's overview first, then search free public sources for each open gap and confirm what each source actually contains.The overview leaves eight open measurements. I’ll look for a free, scriptable source for each one that the page does not already use.The page’s open list is narrower than it first looks. Two gaps have a free, scriptable file the project has not measured. Two more are the same survey, used for different objects. Germany and unreported official gold still have no series the project can publish.

Assumption: “SEC EDGAR XBRL” in the footer is the face-statement work already done. The notes extract below is the unused layer. The February 2024 and August 2026 dates match the Survey of Professional Forecasters calendar, so that survey is treated as the rate survey already in the page. No share, correlation, or premium was computed.

## GAP MAP

(a) **SEC Financial Statement and Notes Data Sets**, January 2009–September 2026, monthly ZIPs (older quarters rolled up). https://www.sec.gov/data-research/sec-markets-data/financial-statement-notes-data-sets — `ContractWithCustomerLiability` confirmed on the company-concept API (https://data.sec.gov/api/xbrl/companyconcept/CIK0000789019/us-gaap/ContractWithCustomerLiability.json). Apple’s `RevenueRemainingPerformanceObligation` URL returned 404.

(b) **Philadelphia Fed SPF, corporate profits after tax (CPROF)**, including the published annualized percent change of the median. https://www.philadelphiafed.org/surveys-and-data/cprof

(c) **NONE FOUND.** Fetched: Bundesbank term structure (yields only; the page already uses Bundesbank files), https://www.bundesbank.de/en/statistics/money-and-capital-markets/interest-rates-and-yields/term-structure-of-interest-rates/term-structure-of-interest-rates-793592 ; ECB yield-curve CSVs (spot, forward, par; not a premium), https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_area_yield_curves/html/index.en.html ; ECB Survey of Professional Forecasters (inflation, GDP, unemployment only), https://www.ecb.europa.eu/stats/ecb_surveys/survey_of_professional_forecasters/html/index.en.html ; Bocconi write-up of German estimates with no data file, https://iep.unibocconi.eu/publications/term-premia-euro-area-and-transmission-mechanism-monetary-policy-0

(d) **Philadelphia Fed SPF, BILL10** (10-year average bill return, first-quarter surveys only). https://www.philadelphiafed.org/surveys-and-data/bill10

(e) **DOL Form 5500 datasets, form years 2024 and 2025**, Schedule H / I and Form 5500-SF, posted beside the 2023 file and refreshed about monthly. https://www.dol.gov/agencies/ebsa/about-ebsa/our-activities/public-disclosure/foia/form-5500-datasets

(f) **The nine major Japanese life insurers’ own accounts.** The Bank of Japan’s Financial System Report index lists semiannual PDFs and no CSV. https://www.boj.or.jp/en/research/brp/fsr/

(g) **NONE FOUND** for a series the project can publish. World Gold Council Gold Demand Trends is free to download and is the usual estimate of official-sector buying, including buying that never reaches the IMF. Its terms allow personal, non-commercial saving and otherwise require written permission before publishing or making a derivative work. https://www.gold.org/terms-and-conditions

(h) **Household-line split: NONE FOUND.** The OFR Hedge Fund Monitor shows size, leverage, counterparties, and liquidity. https://www.financialresearch.gov/hedge-fund-monitor/ The lease-stack tests are already queued on filings.

## Five measurements

**1. Revenue-recognition stocks**

The open question: “Revenue-recognition timing is what remains.”

Source: notes ZIPs above. Free download. The EDGAR access page says anyone may download, with a declared user-agent and a cap of 10 requests a second (https://www.sec.gov/os/accessing-edgar-data). Monthly, then quarterly; history from 2009; ASC 606 tags start later. Direct ZIP links. A copyright-disclaimer URL returned 404, so the formal license sentence was not confirmed.

Design: Sum contract liabilities, contract assets, and remaining performance obligations for a CIK list frozen from the 2023 revenue extract before the later ratios are opened. Dollars of each stock, divided by those same firms’ trailing-four-quarter revenue. Descriptive ratios from end-2023 to the latest quarter, plus a threshold for the change in net contract liability over revenue, written down before the extract is opened. The main trap is double counting: the notes file repeats a total inside timing buckets and custom tags, and the company-concept API drops extensions. An S&P 500 membership list is a licensed index; the denominator is the frozen filer set.

**2. Defined-contribution cash, form year 2024**

The open question: “Official flow data stops there; only levels run to 2025.”

Source: the DOL page above. Public FOIA ZIPs; no reuse restriction is stated on that page. Annual form year, file refreshed about monthly, back to 2009 in this layout. Script the ZIPs. Use the set labeled Latest.

Design: Employer contributions plus participant contributions, minus benefits, for defined-contribution pension plans on Schedule H, Schedule I, and Form 5500-SF. Dollars, divided by beginning-of-year assets of the same plans. Whether that 2024 ratio has the same sign as the 2013–2023 run, scored only if a coverage bar written in advance is met. The trap is the one the page already names: “other contributions” are mostly rollovers, and benefits are mostly rollovers out. Keep those lines separate. Do not pair the flows with ICI levels. The 2025 file is still arriving after the October 2026 extension date.

**3. Expected profit growth with no bond in the formula**

The open question: “A third premium series that does not share a bond leg would settle it.”

Source: CPROF page above. Quarterly Excel for the median, the mean, and the annualized percent change of the median. Page stamp 14 August 2026, so the August 2026 survey is in the file. The survey began in 1968; this variable page does not restate its own first date. No reuse restriction appears on the pages fetched.

Design: The published annualized percent change of the median after-tax corporate-profit forecast. Percent. The unit is already a growth rate; nothing is subtracted from an earnings yield or a Treasury yield. Over the same months as the page’s 49bp comparison, whether that growth rate moved by more than a threshold written down before the growth file is opened. This is a reading of the growth leg. It does not assign a share of the 49bp. The trap: these are NIPA profits, with IVA and CCAdj from 2006, not S&P earnings per share. The published growth rate is the slope of the forecast path. A note on the survey page says a 2026 Q3 PDF erratum did not change the Excel projections.

**4. The survey’s own years-five-to-ten bill average**

The open question: “models and surveys disagree on years five to ten.”

Source: BILL10 page above. Same survey, same free Excel, same August 2026 stamp. First-quarter surveys only. The fetched page does not give the first observation date.

Design: BILL10 is the annual-average bill return “over the current and next nine years.” Subtract the same survey’s near-term bill path, aligned to that wording, and the residual is the average for the rest of the ten-year window. Percentage points. At the 2024 Q1 and 2026 Q1 surveys, whether that residual and the Treasury five-year/five-year forward move in the same direction, with the tolerance written down first. August 2026 is not a BILL10 date. The trap: the file is labeled a return, the window starts in the current year, and this may already be how the page built the years-five-to-ten survey leg.

**5. Japanese life insurers’ currency-hedge ratio**

The open question: “How much foreign demand is hedged is still not measured.”

Source: insurer accounts. The BoJ index above lists the semiannual Financial System Reports as PDFs and does not link a CSV. No keyless bulk API was confirmed.

Design: The hedge ratio stated in the general accounts of the nine major life insurers. Percent of their foreign securities. Descriptive change from end-2023 to the latest common fiscal date, after the hedge definition is copied from the accounts. The trap: foreign securities are not Treasuries; the BoJ’s own notes on this chart treat bonds earmarked for foreign-currency insurance as unhedged; swaps and forwards differ; the general account omits separate accounts. This bounds one holder class. It does not say what led anyone to hedge.

## REJECTED

World Gold Council demand tables: the download is free, and the terms bar open publication of a derivative without written consent, the same failure as the declined ECB Survey of Monetary Analysts.

Bundesbank and ECB yield curves: forwards still mix expected short rates and premia. The page already uses Bundesbank prices.

ECB Survey of Professional Forecasters: no interest-rate question, so it cannot produce a Bund premium. This is not the declined Survey of Monetary Analysts.

Bocconi’s German term-premium page: a 2023–24 description that uses consensus forecasts and posts no file. A new affine model would repeat the Japan result that the split depends on the model.

OFR Hedge Fund Monitor: no field, on the page fetched, for the hedged share of Treasury holdings or for the Z.1 household equity residual. The private-fund scout is already closed.

BIS dollar forwards and swaps: already in the project, and the notional is not a share of Treasury holdings.

## UNCERTAIN

Whether the page’s rate survey is the SPF, and whether BILL10 is already inside the years-five-to-ten split. Whether the unnamed equity survey is an SPF stock-return file; CPROF is profits, so it is a different series either way. The current SPF panel size is not stated on the pages fetched. How complete the 2024 Form 5500 Latest file is. Whether Apple’s 404 means that filer omits `RevenueRemainingPerformanceObligation` or uses only a dimensional tag. The SEC copyright sentence, because the disclaimer URL failed. EDINET keyless bulk access was not confirmed, so item 5 is a filing extract.
