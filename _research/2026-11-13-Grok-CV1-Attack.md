# Grok attack on the CV1 registration (13 Nov 2026; fenced, web documentation only, blind rule held; 25 of 26 fetches succeeded; 1,193 s)

I'll review the registered tests in `spec.md` only, and check public documentation for definitions and methodology without looking up any of the outcome series.The registration is on disk. Next I’ll check official definitions for the BEA, Census, Z.1, XBRL, and BTOS pieces, and the 2022–2025 policy events that could move them, without reading any outcome series.The series descriptions are enough to test the design. I’ll pull methodology pages next—what each line includes, how frames are built, and which 2022–2025 policies hit investment—and leave the outcome numbers alone.Each of CV1-P1 through P7 can read SUPPORT while the hypothesis is false, or AGAINST while it is true. None of the seven statements survives as registered. The statistics were not computed, and no post-2015 outcome of those series is reported below.

The registration can still be a useful description of some investment and balance-sheet aggregates. It cannot, as written, tell whether managers committed capital because epistemic uncertainty fell.

## CV1-P1

**FLAW.** The residual is not “business investment outside the AI build-out.”

- Census classifies a data center as a building that stores, processes, and transmits digital information, and it excludes “racks or servers in data centers” from construction. Power plants, substations, and transmission lines are a separate Power category. Office buildings at manufacturing sites are classified as manufacturing. Subtracting only the private data-center row leaves the AI power build-out and factory-site digital buildings inside the residual. A rise in those categories produces SUPPORT while the hypothesis (old-economy investment, not the AI build-out) is false.
- BEA information-processing equipment, the line P1 subtracts in full, includes medical equipment and instruments, nonmedical instruments, photocopying equipment, and office machinery, as well as computers and communications equipment. A hospital-equipment boom that is removed from the residual produces AGAINST while non-AI investment rose.
- Own-account software R&D sits in research and development, which P1 does not subtract. AI development booked as R&D stays in the residual and can produce SUPPORT.
- The CHIPS advanced manufacturing credit is 25 percent of qualified investment in facilities whose primary purpose is manufacturing semiconductors or semiconductor manufacturing equipment, for property placed in service after 31 December 2022. Those factory structures are inside BEA nonresidential investment and are not in the subtracted lines. SUPPORT can be the credit, with managerial uncertainty unchanged. The same window contains the Inflation Reduction Act’s clean-energy credits (the IRS page groups IRA and CHIPS in one registration tool) and, after 19 January 2025, a restored 100 percent additional first-year depreciation deduction for qualified property.
- The object is a nominal share of GDP. That removes a common price level. It does not remove a rise in the price of structures relative to the GDP deflator. The share can rise with unchanged real volume.
- The placebo runs from 2015Q4 to 2019Q4, so it contains the post-27 September 2017 bonus-depreciation regime and stops before the pandemic. Projects started in the unscored gap (2020 through 2022Q3) and still being built in 2022–2025 count as treatment acceleration. “Latest quarter” is not locked, so the end date is a degree of freedom.
- A collapse in ordinary office and warehouse construction can offset a real rise in other non-AI categories, producing AGAINST while the hypothesis is true for those other categories. The statistic is one net residual.

**SEVERITY.** Fatal.

**AMENDMENT.** Replace the P1 statistic with: “From BEA NIPA Table 5.3.5, nominal private nonresidential fixed investment minus computers and peripheral equipment, minus communication equipment, minus software, minus manufacturing structures, minus power and communication structures, minus mining exploration, shafts and wells, divided by Table 1.1.5 nominal GDP. Annualised percentage-point change from 2022Q4 to 2025Q4, minus the same from 2015Q4 to 2019Q4. Compute the same object in chained dollars with Tables 5.3.6 and 1.1.6. SUPPORT only if both gaps are ≥ +0.15 pp per year. Census private data-center construction is a memo, not a subtraction, unless both endpoints are non-missing and the builder documents the BEA–Census bridge in the code; a blank is not a zero. If the gap changes sign once manufacturing, power, and mining structures are removed, the score is INCONCLUSIVE. The sentence is descriptive. It does not identify a change in managerial uncertainty.”

## CV1-P2

**FLAW.** “Listed firms outside the AI complex accelerated capex” is not what the panel measures.

- The exclusion windows miss industries that are inside the AI supply chain or inside a subsidised capex boom. OSHA’s SIC 3559 list includes “Semiconductor manufacturing machinery,” and 3559 is outside 3570–3579 and 3670–3679. Those firms are eligible for the CHIPS credit above and sit in the ex-AI panel. SIC 4813 is telephone transmission, including leased optical fiber, and it is outside the exclusion list. SIC 4911, electric generation, transmission, and distribution, is inside the blanket 4900–4991 exclusion, as is the rest of major group 49 (the OSHA header is “Electric, Gas, and Sanitary Services”). Water, gas, and sanitary utilities leave the “old economy” sample. SIC 6798 is every real estate investment trust, including mortgage trusts, not data-center landlords only. SIC 7370–7379 drops the whole software and data-processing industry. Amazon and Tesla are removed as entire CIKs, so their non-AI segments go with them. A parent whose primary SIC is outside the list keeps every subsidiary. UNCERTAIN for any named filer’s current SIC; the code-level holes do not depend on that.
- A panel balanced only on the two end years of each window is not a common-firm panel. A target that files in the base year and is acquired before the end year drops out. The acquirer’s end-year capex includes the acquired operations. Aggregate growth rises because of consolidation. The hypothesis itself predicts more acquisitions, so this channel manufactures SUPPORT on the capex test.
- The tag is a cash outflow for property, plant, and equipment, including self-constructed assets, on the consolidated filing. That is worldwide capex. Nominal GDP is domestic. Foreign plant spending by US filers produces SUPPORT for a claim about the US economy while domestic ex-AI investment is unchanged.
- SEC annual frames keep one fact per firm: the last filed fact whose duration is 365 days plus or minus 30. A nine-month year-to-date total does not meet that duration screen, so the classic 10-Q year-to-date error is avoided only if the builder actually uses `CY####` frames. The frame still mixes fiscal calendars (“different reporting start and end dates”), and the last-filed fact can be a later amendment or a non-10-K. Custom taxonomy extensions never enter the frame. IFRS filers are not in the `us-gaap` frame. The population is “US-GAAP filers who used this tag,” not “listed firms.”
- Firms that stop investing and omit the tag fall out of the balanced panel. Decelerators disappear. Aggregate growth is dominated by the largest remaining filers, so one subsidised plant program clears +2 pp per year.
- The placebo again contains the TCJA depreciation regime. Treatment growth minus placebo growth can be the 2025 depreciation restoration, aircraft and equipment deliveries delayed out of the gap years, or energy and defense capacity, with uncertainty unchanged. It can also be ≤ 0, and read AGAINST, when ex-AI firms did accelerate but nominal GDP growth was high enough to wipe out a +2 pp gap.

**SEVERITY.** Fatal.

**AMENDMENT.** Replace the P2 rule with: “Universe: `us-gaap` / USD frames `CY2016`, `CY2019`, `CY2022`, and `CY2025` for `PaymentsToAcquirePropertyPlantAndEquipment`. Keep a fact only if the joined submission form is 10-K or 10-K/A, the reported value is positive, and the fiscal year-end month is November, December, or January. The scored panel is the intersection present in all four years. Growth is the median of firm-level annualised growth, minus annualised nominal GDP growth from Table 1.1.5 over the matching calendar window. Drop a firm from a window if ending PPE exceeds beginning PPE by more than 25 percent because of a business combination. Add SIC 3559, 3661, 3663, 3669, 4812, and 4813 to the exclusion list. Remove the blanket exclusions of 4900–4991, 6798, and 7370–7379, and report those three groups as separate strata. Classify by the SIC on the filing, not the SIC current at download. SUPPORT only if the common-firm median gap is ≥ +2 pp per year and the capex-weighted gap has the same sign. Otherwise INCONCLUSIVE.”

## CV1-P3

**FLAW.** The four series are not idle liquidity, and a fall in the ratio is not a drawdown spent on capex.

- Re-derived from the Financial Accounts Guide. `FL103020005` is checkable deposits and currency of nonfinancial corporates plus the same asset of equity REITs (`FL103020000` + `FL123020003`). `FL103020000` is a QFR “cash and demand deposits” indicator, scaled by an SOI-to-QFR ratio, minus money-market fund shares. After the latest SOI year the benchmark ratio is frozen. `FL103030003`, time and savings deposits, is the remainder of a broader SOI/QFR cash total after subtracting checkable deposits, money-market fund shares, and foreign deposits. `FL103034000`, money-market fund shares, is an annual ICI figure; non-year-end quarters are a fixed ratio, not a measured quarterly stock. `FL102051003`, repo, is a percentage allocation of “other short-term financial investments,” not a reported repo stock. Unidentified miscellaneous assets of the sector are calculated residually, so error in these lines is absorbed there rather than shown as a discrepancy.
- The sector is domestic nonfinancial corporations only. It includes S corporations, corporate farms, and equity REITs (moved into this sector in the 7 December 2023 release). It excludes financial holding companies and the foreign subsidiaries of US corporations. Hyperscalers that are nonfinancial corporations stay in. Offshore cash, the stock the hypothesis means by a corporate hoard, is outside the numerator. Spending that cash produces AGAINST while the hypothesis is true. A shift from domestic deposits into Treasury bills produces SUPPORT while nothing was spent: the Fed’s own core liquid-asset series, `FL104001105`, is foreign deposits plus checkable deposits plus time and savings deposits plus money-market fund shares. P3 swaps the foreign deposits for imputed repo and still omits Treasury securities, agency securities, and commercial paper, which sit in the broader liquid-asset sum `FL104001005`. GAAP cash, the concept P4 uses, includes those short-term liquid investments. The same treasury operation can make P3 say “drawn down” and P4 say “still cash-rich.”
- The statistic is a change in a ratio to nominal GDP, from 2022Q4 to an unlocked “latest” quarter, with no placebo and no requirement that the dollar stock fall. Flat nominal balances and a higher price level produce ≤ −0.5 pp and SUPPORT. The levels are not seasonally adjusted. A Q4-to-Q2 comparison mixes a seasonal pattern into the change. The AI complex is not removed, so a hyperscaler deposit movement scores the “corporate” hypothesis by itself.

**SEVERITY.** Fatal.

**AMENDMENT.** Replace P3 with: “Q4 to Q4 only. Numerator = `FL104001105` + `FL103061103` + `FL103061703` + `FL103069100`. Do not use `FL102051003`. Divide by Table 1.1.5 nominal GDP. Statistic = change from 2022Q4 to 2025Q4 minus change from 2015Q4 to 2019Q4. SUPPORT only if that difference is ≤ −0.5 pp and the nominal dollar numerator falls. If the latest SOI benchmark year ends before 2025Q4, INCONCLUSIVE. The readout must state that the sector includes equity REITs and nonfinancial AI filers, excludes financial holding companies and foreign subsidiaries, and that time-and-savings deposits are a remainder.”

## CV1-P4

**FLAW.** A tercile of the cash ratio is not “cash-rich firms led.”

- `CashAndCashEquivalentsAtCarryingValue` is an instant fact. It will not appear in a `CY####` duration frame. Taken literally, the split cannot be built from the annual frames P2 uses.
- The concept includes short-term highly liquid investments. Terciles formed on it do not match the deposit stock in P3. “At the window start” is undefined. Using the end of the base year sorts firms on a stock already inside the treatment window.
- Aggregate growth of the top ratio tercile is often the growth of small high-ratio filers, so +3 pp per year is a noisy tripwire. The bottom tercile is where a 2022–2023 interest-rate shock binds. The differential can be ≥ +3 pp, and read SUPPORT, when cash-rich firms did not accelerate and constrained firms cut. It can also be ≥ +3 when both terciles have negative growth. Industry mix (pharma versus retail) sits inside the cash ratio. The specified tag’s parent list includes a broader restricted-cash concept, so filers who report only the broader tag disappear from the split.

**SEVERITY.** Fatal for the funding claim. The accounting mismatch is serious on its own and fatal in this rate cycle.

**AMENDMENT.** Replace the P4 rule with: “Cash and assets come from instant frames `CY####Q4I` at the fiscal year-end immediately before each window’s base year. If `CashAndCashEquivalentsAtCarryingValue` is absent, use `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents` and not both. Drop SIC 6000–6799. Form terciles within 2-digit SIC. Weight the tercile growth by beginning capex. Net of nominal GDP growth, the top tercile’s own treatment growth must be > 0. SUPPORT only if (top − bottom) in treatment minus (top − bottom) in placebo is ≥ +3 pp per year and that own-growth gate holds.”

## CV1-P5

**FLAW.** The SIC bins are not irreversibility.

- High is mining (1000–1499), all manufacturing (2000–3999), and transport and communications (4000–4899). That puts oil and gas, semiconductor-equipment makers (3559), aircraft and autos, and telephone carriers (4813) in the “hard to reverse” group. Low is wholesale, retail, and services. A retailer building a warehouse is low. A manufacturer buying resaleable vehicles is high. Utilities, the longest-lived structures, are removed by the P2 exclusion before the split. Construction (1500–1799) and finance (6000–6799) are in neither bin, so the acceleration can sit in the omitted codes while high-minus-low still clears +2 pp.
- The 2022–2025 high group is where the CHIPS credit, clean-energy manufacturing credits, energy-price capex, fiber and telecom spending, and aircraft deliveries land. SUPPORT can be those payoffs. AGAINST can be a services capex response to AI, which the hypothesis allows and the bin codes as reversible.

**SEVERITY.** Fatal.

**AMENDMENT.** Replace the statement with: “Manufacturing, mining, and non-utility transport capex growth exceeded wholesale, retail, and services.” Delete “irreversibility.” Before scoring, remove SIC 1311, 1381, 1382, 1389, 2911, 3559, 3711, 3721, 4812, and 4813 from the high group and report them separately. Keep the common-firm rule from the amended P2. SUPPORT only if the trimmed high-minus-low gap, treatment minus placebo, is ≥ +2 pp per year. If the untrimmed gap clears +2 and the trimmed gap does not, INCONCLUSIVE.”

## CV1-P6

**FLAW.** The sector correlation does not measure “sectors that use more AI accelerated capex more.”

- BTOS is a proportional sample of employer businesses (“the same percentage of businesses is selected from each stratum”). The published figure is a weighted share of businesses responding, not a share of employment or of capex. The original question, which is the 2024–2025 series, asks about AI “in producing goods or services” in the last two weeks. Census changed the stem because respondents using AI for hiring, project management, accounting, R&D, or software workflows answered “no.” That omitted use is the decision-making channel the hypothesis is about. A sector can adopt managerial AI, accelerate commitment, and rank as a low user on this question, producing AGAINST while the hypothesis is true. Production AI plus subsidised factory capex in manufacturing produces SUPPORT while uncertainty did not change.
- Census split the series on purpose. The new stem starts with collection on 17 November 2025, and the new time series starts with the 4 December 2025 release. A mean of “2024–2025 cycles” that ignores the stem crosses that break. Collection is also missing for 6 October through 16 November 2025. Multi-establishment firms that operate in more than one NAICS sector are excluded from sector totals, so the firms that dominate XBRL capex are structurally out of the AI rank. Railroads (NAICS 482) are out of scope for BTOS and inside the XBRL transport sector.
- The official concordance page offers 1987 SIC to 2002 NAICS, not to the 2022 NAICS used by BTOS. The crosswalk is many-to-many, and the spec leaves the table to the builder. Software filers in SIC 7370–7379 are removed from the capex side and left inside the BTOS sector rate. Spearman ≥ +0.30 on the remaining handful of sectors is a one-sector result. Subtracting national GDP growth shifts every sector by a constant and does not change ranks.

**SEVERITY.** Fatal as a test. As a descriptive correlation it is still serious until the series break and the crosswalk are fixed.

**AMENDMENT.** Replace the P6 rule with: “Descriptive only. No SUPPORT or AGAINST label. AI-use is the ‘Yes’ share whose stem is ‘in producing goods or services,’ taken from the AI Core Questions (Original) table, averaged over unsuppressed 2024–2025 cycles that end before 17 November 2025. Do not fill the shutdown periods 202521–202523, and do not pool any release from 4 December 2025 onward. Match sectors with the Census 1987-SIC-to-2002-NAICS concordance, chained to 2022 NAICS, weights written down and hashed before the build. Drop sectors with fewer than 20 common-firm filers. Publish the Spearman and the leave-one-sector-out range. The prose may not say that AI use caused the capex gap.”

## CV1-P7

**FLAW.** The ratio is not “acquisitions made in the boom are written down faster.”

- The numerator is every `GoodwillImpairmentLoss` in the later window. Legacy goodwill from earlier deals is included. A small 2024 cash deal plus a large write-down of a 2016 acquisition produces a ratio ≥ 1.25× and SUPPORT while the boom deals were not written down.
- The denominator is “the cash outflow associated with the acquisition of a business, net of the cash acquired.” Stock-for-stock deals, which are where optimistic goodwill usually sits, never enter. Cash deals with little goodwill make the denominator large and the ratio small, producing AGAINST while the boom’s equity deals were impaired.
- The lag is the same for both cohorts, so the statistic measures a fraction at a fixed horizon, not speed. Impairments booked in 2026, before CY2027, miss the numerator and produce AGAINST for deals that were written down sooner.
- The baseline impairments are CY2018–2019. That window ends before 2020, so write-downs of the 2015–2016 cohort that landed in the 2020 stress year are outside the baseline. The comparison is a future window, which is allowed to be a downturn, against a late-expansion pair. UNCERTAIN, because the primary FASB PDF was not fetched: secondary summaries of ASU 2017-04 put the mandatory one-step impairment test in fiscal years beginning after 15 December 2019 for SEC filers, with early adoption allowed. If that date is right, the baseline is mostly the old two-step test and CY2027–2028 is the new test, which recognises impairment up to the full gap between carrying amount and fair value. The ratio can clear 1.25× because the rule changed.
- Filers who never tag the impairment concept are undefined in the spec. Treating them as missing and dropping them raises the ratio. Filers who go bankrupt and stop filing take their write-downs out of the frames and push the ratio down, producing AGAINST while the hypothesis is true.

**SEVERITY.** Fatal.

**AMENDMENT.** Replace P7 with: “Among ex-AI US-GAAP 10-K filers with `PaymentsToAcquireBusinessesNetOfCashAcquired` > 0 in CY2024 or CY2025, the numerator is the sum of `GoodwillImpairmentLoss` in CY2026, CY2027, and CY2028, with a missing tag stored as zero and only 10-K facts used. The denominator is the larger of cash acquisition spend and the increase in goodwill across CY2024–CY2025. Firms that stop filing are removed from both numerator and denominator, and the count is reported. The baseline is the median of the same ratio for the three cohorts 2012–13, 2013–14, and 2014–15, measured over the three fiscal years that start two years later. SUPPORT only if the treatment ratio is ≥ 1.25× that median and a same-accounting-rule comparison is shown. The claim’s verb is ‘a larger fraction within three years,’ not ‘faster.’ This remains a cohort association, not a link to specific deals.”

## SURVIVORS

None of P1–P7 survives in its current wording.

The preamble’s decision not to register the aggregate Atlanta Fed SBU series, and its correction of the “top motive” and “heavy capital deployment” readings of the two survey papers, should stand. Stage 2 at firm level remains untested, as the spec says.

After the amendments, two descriptive objects are worth computing and are not tests of the channel: the locked real BEA residual in the amended P1, and the common-firm median capex gap in the amended P2, reported with the strata and with no uncertainty label. P3–P7 should be rescored only under the rewritten rules, or left unscored.

## LOAD-BEARING ASSUMPTION

The 2022–2025 minus 2016–2019 gap in residual investment is a fall in managers’ epistemic uncertainty. If that gap is instead the CHIPS credit, clean-energy credits, the 2025 depreciation restoration, power and factory construction that the exclusion list leaves inside “ex-AI,” energy and defense and aircraft-delivery cycles, or acquisition arithmetic in a balanced panel, then a SUPPORT label on P1–P6 is the wrong answer about the hypothesis, and a high P7 ratio is the aftermath of whichever boom actually occurred. No other registered statistic identifies the channel. Debt capacity, new credit, inventory, and firm-level uncertainty are not in the design.

## PRACTICALITY

- P2, P4, P5, P6’s capex half, and P7 cannot be fetched as specified. SEC fair access requires a declared User-Agent with an organisation name and a contact address. The spec forbids any contact address and forbids touching `www.sec.gov`. Minimal change: allow a project mailbox in the `data.sec.gov` User-Agent header only, and do not write that address into the repo or the outputs. Keep the ban on `www.sec.gov` pages.
- Every GDP denominator is Table 1.1.5 in NIPA Section 1. The named BEA file is Section 5. Minimal change: add `Section1All_xls.xlsx`, and Tables 1.1.6, 5.3.4, and 5.3.6 if the real variant is adopted.
- P4’s cash and assets are instant concepts. Minimal change: request `CY####Q4I`, not `CY####`.
- P6’s “Sector.xlsx, question 7” is not a stable identifier. The methodology describes a 24-question core instrument; the original AI stem lives in the AI Core Questions (Original) table; the 4 December 2025 release is a new series. Minimal change: match the question stem and the original-series file, as in the P6 amendment.
- P1’s Census subtraction has no stated unit, sheet, or row, and a BEA billions series cannot be combined with a raw spreadsheet cell until the unit is fixed. UNCERTAIN whether the separate data-center row is populated at 2015Q4; this review did not open the construction release, because that release publishes the spending estimates. Minimal change: name the sheet, the row label “Data center,” the conversion to billions, and the blank-is-not-zero rule.
- P3 can be built from `FRB_Z1_csv.zip`. The four IDs resolve to the titles in the spec. The June 2026 renumbering changed table numbers, not these series IDs. The build failure is the definition, not the file.
- P7 is not scorable until the CY2028 10-Ks are in the frames, which the spec already says is about April 2029.

## URLs fetched

- https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FL103020005&t= — “Computed = + FL103020000 + FL123020003.”
- https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FL103020000&t= — “less money market fund shares”; “benchmark is fixed.”
- https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FL103030003&t= — “less: Checkable deposits and currency, Money market fund shares, and Foreign deposits.”
- https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FL103034000&t= — “Non-year-end data points are calculated as a fixed ratio.”
- https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FL102051003&t= — “plus a percentage of sum of lines Other short-term financial investments.”
- https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FL104001005&t= — Broad liquid assets add Treasury securities, commercial paper, and corporate equities.
- https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FL104001105&t= — Core liquid assets are foreign deposits, checkable deposits, time and savings deposits, and money-market fund shares.
- https://www.federalreserve.gov/releases/z1/current/z1_tables_description.pdf — “does not include the foreign subsidiaries of U.S. corporations.” Also: “Holding companies are considered financial businesses” and are excluded; equity REITs “were reclassified” on 7 December 2023; “Unidentified miscellaneous assets, which is calculated residually.”
- https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data — “Sample Company Name AdminContact@.com.”
- https://www.sec.gov/search-filings/edgar-application-programming-interfaces — “CY#### for annual data (duration 365 days +/- 30 days)”; “one fact for each reporting entity that is last filed”; “mindful different reporting start and end dates.”
- https://www.census.gov/econ_file/construction/c30/definitions.html — “Data center Includes buildings that contain the hardware”; construction excludes “racks or servers in data centers”; “Office buildings at manufacturing sites are classified as manufacturing”; Power includes “power plants” and “electrical substations.”
- https://www.bea.gov/help/faq/125 — “GDP current-dollar estimates are presented in table 1.1.5.”
- https://www.bls.gov/news.release/prod3.tn.htm — Information-processing equipment includes “medical equipment and related instruments”; R&D “includes own-account R&D for software which had previously been classified as software.”
- https://www.irs.gov/credits-deductions/advanced-manufacturing-investment-credit — “25% of the qualified investment”; a facility “manufacturing of semiconductors or semiconductor manufacturing equipment”; “Placed in service after Dec. 31, 2022.”
- https://www.irs.gov/newsroom/treasury-irs-issue-guidance-on-the-additional-first-year-depreciation-deduction-amended-as-part-of-the-one-big-beautiful-bill — “100 percent” additional first-year depreciation “for qualified property acquired … after Jan. 19, 2025.”
- https://www.osha.gov/sic-manual/3559 — “Semiconductor manufacturing machinery.”
- https://www.osha.gov/sic-manual/4813 — “leasing telephone lines” and “optical fiber lines.”
- https://www.osha.gov/sic-manual/4911 — “generation, transmission, and/or distribution of electric energy for sale.”
- https://www.osha.gov/sic-manual/6798 — “Mortgage investment trusts” and “Real estate investment trusts.”
- https://www.census.gov/naics/concordances/concordances.html — “1987 SIC to 2002 NAICS.”
- https://www.census.gov/hfp/btos/downloads/methodology/Business_Trends_and_Outlook_Survey_Methodology_V6.pdf — “the same percentage of businesses is selected from each stratum”; multi-sector firms are “excluded from sector-level totals”; railroads “NAICS = 482” are out of scope; no collection for “October 6 – November 16, 2025.”
- https://www.census.gov/hfp/btos/downloads/AI%20Question%20Wording%20Updates.pdf — original stem “in producing goods or services”; respondents were “using AI tools in the hiring process”; “a new time series” beginning with the “December 4, 2025” release.
- https://www.calcbench.com/element/CashAndCashEquivalentsAtCarryingValue — “short-term, highly liquid investments”; period type “instant.”
- https://www.calcbench.com/element/PaymentsToAcquireBusinessesNetOfCashAcquired — “The cash outflow associated with the acquisition of a business, net of the cash acquired.”
