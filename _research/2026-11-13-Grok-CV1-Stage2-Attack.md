# Grok attack on the CV1 stage-2 registration (13 Nov 2026; fenced, documentation only, blind rule held; 14 of 16 fetches succeeded; 1,070 s)

I'll review the registered tests in `stage2spec.md` only, then check public methodology for the named series so the critique stays about design, not outcomes.The registration is the six aggregate proxies in that file. I’ll check how those measures are built and what they actually capture, without pulling any post-2015 readings.None of the labelled statements can be left as written. S1–S4 can each read SUPPORT while managers’ epistemic uncertainty is unchanged or higher, or AGAINST while it is lower. S5 and S6 have no label and can still be read as a cross-check that the hypothesis failed or held.

This registration does not contain an AI-firm exclusion list, an XBRL panel, nominal-GDP netting, a Z.1 liquid-asset series, a SIC-to-NAICS map, a P7 window, or a 2016–2019 placebo. Those cannot be what breaks these tests. The analogues that are in the file are the S2 stem list, the SBU and Dallas panels, nominal sales revenue, the EPU/VIX residual, and the baselines actually specified: January 2015–December 2019 for S1, S2, and S4; January 2018–December 2019 for S3; January 2017–December 2019 for S5.

Two features apply to every labelled statement. The controls are fit by OLS of the proxy on a constant, log daily EPU, and log 30-day VIX, pooling baseline and treatment and omitting a window indicator. The gap in residual means is then

`(mean Y_T − mean Y_B) − b̂₁(mean log EPU_T − mean log EPU_B) − b̂₂(mean log VIX_T − mean log VIX_B)`,

with `b̂` from that omitted-indicator regression. The window effect in the regression that includes a treatment indicator uses the within-window slopes instead. Those slopes and `b̂` coincide only if the controls have the same window means or the window effect is zero. The registration itself says the tariff episode moved policy uncertainty and that a calm market must not count as success, so the control means are not supposed to match. The statistic is not the partial effect the text describes. The introduction also says one AGAINST refutes stage 2 in the aggregate, and it never defines a vote across S1–S4. Any one false AGAINST kills the stage.

Baker, Bloom, and Davis’s daily index, which is the file named in the spec, is the wrong long-horizon control. They write that papers enter and exit the Newsbank archive, so “compositional shifts potentially distort the longer-term behavior of the daily EPU index,” and they use the stable 10-paper monthly index for longer comparisons. The VIX is 30-day S&P 500 implied volatility. S1 and the Bank of England measure are 12-month own-firm sales uncertainty. A twist in the volatility term structure moves the control when 12-month managerial uncertainty does not.

## CV1-S1

**FLAW**

- Inflation uncertainty is inside nominal sales revenue and outside the controls. The SBU asks for sales revenue, converts scenario growth rates to a symmetric growth rate, and publishes the activity-weighted mean of firm-level subjective standard deviations. A common inflation component widens every firm’s nominal distribution and then drops out of that average as price paths become easier to forecast. Log daily EPU does not contain the Survey of Professional Forecasters inflation-disagreement term that the same project uses in its other US index. Log 30-day VIX does not measure 12-month price uncertainty. Scenario: real-demand uncertainty and knowledge of firm facts are unchanged, nominal subjective uncertainty falls with inflation uncertainty, the residual effect size is ≤ −0.5. SUPPORT while the hypothesis is false.
- The same residual can do the opposite. Scenario: epistemic uncertainty falls, and that fall lines up with lower VIX. The pooled slope, fit partly on the treatment window, subtracts the decline. The residual gap is ≥ 0. AGAINST while the hypothesis is true. A slope shift does it without a level shift: firms react less to newspaper policy coverage in 2023–2025, EPU is higher, a single pooled slope over-predicts treatment uncertainty, and the residual mean falls through −0.5 while the intercept shift is zero.
- The baseline is not one measurement. Sales questions were modified in September 2016. The old instrument asks for future sales levels; the later one asks for scenario growth rates. Before September 2016 there are about 50 responses per topic per month and the published uncertainty smoother is a nine-month lagged moving average; from December 2016 to May 2019 it is a two-month lagged moving average; from June 2019 it is three months, which still covers the last seven months of the baseline. From September 2020 the uncertainty smoother is again two months. The spec splices a “Historical Data for Research” sheet through November 2016 to the smoothed sheet from December 2016 and gives no rule when the overlap disagrees. Scenario: the research segment sits higher because of the old instrument and the small sample, the treatment segment is the post-2016 smoother, and the effect size is ≤ −0.5 with no change in the underlying answers.
- The August 2026 revision extends the winsorization thresholds through December 2025, the last treatment month, and the annual clean of extreme forecast errors and unit mistakes rewrites the published index. Caps and deletions are functions of the treatment sample, including inflation-era unit errors (extra zeros, annual figures entered as quarterly). Scenario: cleaning drops messy high-uncertainty responses in 2023–2025 and loosens or tightens the cap using the treatment tail. Either threshold can be crossed.
- The panel is a recruited, non-probability panel with response rates that differ by sector. Weights are current and expected sales, winsorized at the 1st and 80th percentiles, so firms that expect higher sales get more weight. A June 2024 third panel on prices and costs begins inside the treatment window. The public landing page still describes a two-group sales/employment rotation. Whether sales-sample membership changed is UNCERTAIN. Scenario: high-uncertainty firms attrit, or the weight shifts toward large firms with tight forecasts, and the weighted mean falls through −0.5 while a fixed set of firms is unchanged.
- The two-month smoother exists “to reflect the split panel.” Consecutive months are different rotation groups, so the January 2023 smoothed point uses December 2022. UNCERTAIN only the exact weights. The excluded pandemic window enters the first treatment observation. A backward average does not pull 2026 into December 2025.

**SEVERITY:** fatal

**AMENDMENT:** Replace S1 with: “Use one frozen workbook, hash recorded in the registration. Use the unsmoothed sales-revenue subjective-SD index for every month from December 2016 through December 2025. Drop January 2015–November 2016. Winsorize firm SDs at percentiles computed on December 2016–December 2019 only. Fit `Y = a + b1 log(monthly 10-paper EPU) + b2 log(VIX) + b3 log(SPF CPI-forecast dispersion) + d Treatment + e` on December 2016–December 2019 and January 2023–December 2025. Effect size = `d` divided by the baseline residual standard deviation from that regression. SUPPORT if effect size ≤ −0.5. AGAINST if effect size ≥ 0. Otherwise no label. S1 alone cannot refute stage 2.”

## CV1-S2

**FLAW**

- The exclusion rule is a substring test. As specified, `war` matches toward, warning, warned, warehouse, and award. `rates` matches moderates, which is standard Beige Book diction, and also wage rates and freight rates. `trade` matches retail trade and wholesale trade. `conflict` matches conflicting reports. `shutdown` matches a plant shutdown. Scenario: ordinary “retail trade contacts were uncertain as growth moderates” sentences are dropped. In 2023–2025 more uncertainty sentences also contain rates, trade, or toward. The kept count falls by more than 0.5 baseline residual standard deviations. SUPPORT while managers are not more certain.
- Inflation, prices, banks, credit, insurance, strikes, and hurricanes are not stems. Bank failures, commercial real estate, and price uncertainty in 2023–2025 stay in the numerator. Tariff and trade sentences in the 2018–2019 part of the baseline are removed by `tariff` and `trade`. Scenario: the kept rate is higher in treatment. Effect size ≥ 0. AGAINST while own-firm epistemic uncertainty fell.
- The first redesigned Beige Book is 18 January 2017, inside the baseline. Each District report was rebuilt around overall activity, employment and wages, and prices, and the book was made more concise. The labelled rate is per 1,000 sentences, split on `.?!` plus whitespace. That splitter breaks on “U.S.” and “St. Louis” and drops bullets that have no terminal punctuation. A shorter book or a new bullet style changes the rate with no change in contact language. District text is written by Reserve Bank staff from businesses and community organizations, so an editorial change is enough to cross either threshold.
- Eight editions a year, with sticky phrasing, are treated as independent monthly observations when the residual standard deviation is computed. A few repeated sentences can clear −0.5 or 0.

**SEVERITY:** fatal

**AMENDMENT:** Replace the S2 label rule with: “S2 carries no label. Publish, per edition, uncertainty sentences per 1,000 sentences under two dictionaries only: a word-boundary match to uncertain/uncertainty/uncertainties, and the same match excluding a sentence only if it has a whole word from {tariff, election, shutdown, regulation, tax, fiscal, geopolitics, sanction, immigration, pandemic, covid, brexit, congress, legislation} or the phrases {federal reserve, interest rate, debt ceiling, stock market, financial market}. Do not use the stems war, trade, rates, conflict, polic, volatil, administration, or government. Map each edition to its release month. Do not residualize this series, and do not let it refute or support stage 2.”

## CV1-S3

**FLAW**

- The form asks: “How has uncertainty regarding your company’s outlook changed in the current month vs. prior month?” Answers are Increase, No Change, Decrease. `uncr` is the percent reporting an increase minus the percent reporting a decrease. Responses are not weighted. The registered contrast compares average monthly changes in 2023–2025 with average monthly changes in 2018–2019. The sum of monthly changes over the treatment window telescopes to the level at December 2025 minus the level at December 2022. December 2022 is inside the excluded window. Neither the mean nor the sum equals the 2023–2025 level minus the 2018–2019 level.
- Scenario, SUPPORT while false: uncertainty rises in 2020–2022, then falls every month in 2023–2025 and finishes still above 2018–2019. Treatment `Uncr` is negative, the baseline mean is about zero, the residual effect size is ≤ −0.5. The level hypothesis is false.
- Scenario, AGAINST while true: uncertainty falls during the excluded years onto a plateau below the 2018–2019 level, then the monthly change is about zero in 2023–2025. Effect size ≥ 0. AGAINST while the level hypothesis is true.
- Regressing that change index on the level of log EPU and log VIX subtracts a level from a flow. A higher EPU level in the treatment window pulls the residual down whenever the fitted slope is positive, which can manufacture ≤ −0.5 while the change index itself is flat.
- Both surveys are Texas-only, voluntary, and subject to exit, including firms that go out of business. An equal average of manufacturing and services gives manufacturing half the statistic. The Dallas Fed describes private services as the bulk of the Texas economy. Energy, the border, and a state-specific shock can move the average while national epistemic uncertainty does not. In January each year, seasonal factors are recalculated and history is rewritten for indexes that show seasonality. Whether `uncr` is in that set is UNCERTAIN. The baseline has 24 months.

**SEVERITY:** fatal

**AMENDMENT:** Delete the S3 label. Replace the paragraph with: “S3 is descriptive and cannot support or refute stage 2. Report the not-seasonally-adjusted balance `uncri − uncrd` for TMOS and for TSSOS separately, from the vintage frozen at the build, and state in the table that a negative reading means more respondents said uncertainty decreased this month than said it increased. Do not average the two surveys, do not residualize them on EPU or VIX, and do not compare their means with 2018–2019 as a test of the level.”

## CV1-S4

**FLAW**

- The numerator is within-firm uncertainty about the next four quarters of nominal sales. The denominator is the activity-weighted gap between the 90th and 10th percentiles of sales growth over the past year. A shock that adds the same amount to every firm’s nominal growth leaves that cross-sectional gap unchanged and raises every firm’s subjective standard deviation. When common inflation uncertainty recedes, the numerator falls and the denominator does not. Scenario: the treatment ratio is ≤ 0.9 times the baseline ratio, SUPPORT, with no change in real or epistemic uncertainty. The first twelve treatment months have a denominator whose lookback year is mostly 2022, which the registration excluded.
- The denominator also moves for reasons that have nothing to do with a firm’s own aleatory risk. It includes permanent differences across firms. Tariff exposure, a shift in which industries respond, and the sales weights change p90−p10. Scenario: subjective uncertainty is unchanged, realized growth fans out across firms, the ratio falls through the 0.9 line. SUPPORT while the hypothesis is false. The reverse, a more homogeneous respondent set, compresses the gap, the ratio rises to the baseline or above, and the label is AGAINST while subjective uncertainty fell.
- “Window means compared” is undefined between the mean of monthly ratios and the ratio of window means. Those two numbers sit on opposite sides of the 0.9 line when a few months have a very wide realized gap. The numerator is winsorized. The percentile gap is not, so a fatter realized tail lowers the ratio by itself.

**SEVERITY:** fatal

**AMENDMENT:** Replace S4 with: “For each month, numerator = unsmoothed activity-weighted mean subjective SD of nominal sales growth. Denominator = activity-weighted p90 minus p10 of realized nominal sales growth over the past four quarters, observed rows only. Drop any month whose realization window overlaps 2020–2022, which removes January 2023–December 2023. Let R be the ratio of the mean numerator to the mean denominator within a window. SUPPORT if R_treatment ≤ 0.9 × R_baseline. AGAINST if R_treatment ≥ R_baseline. No label in between. Publish the two means beside R. S4 cannot refute stage 2 unless amended S1 is also AGAINST.”

## CV1-S5

**FLAW**

- There is no SUPPORT or AGAINST line, so this statement cannot misfire a label. It can still be read as the cross-check the heading promises. UK sales uncertainty is the standard deviation from five self-chosen sales-growth scenarios. Regular sales questions start in August 2016, and each firm is asked them on a three-month rotation. The software carries forward previous scenario values. The baseline January 2017–December 2019 is the Brexit negotiation period; the survey’s own design note says the special questions had mostly concerned Brexit. The treatment window is the aftermath of the European energy shock and a different UK policy path. Scenario: the UK three-month average is lower in 2023–2025 because Brexit uncertainty left the distribution, and the figure is placed beside a lower US residual. A reader treats that as replication. The US epistemic hypothesis can be false. The opposite UK path, a higher reading because of UK-specific policy, looks like a failed replication while the US hypothesis is true.
- The January 2023 three-month average includes November and December 2022. Units are not the US residual’s units. It is UNCERTAIN whether the free monthly workbook even contains this constructed standard deviation: the data page posts aggregate workbooks and does not name the column, and the microdata are in the ONS Secure Research Service.

**SEVERITY:** serious

**AMENDMENT:** Replace S5 with: “S5 is not a cross-check and cannot corroborate or weaken S1. If, and only if, the Bank of England monthly aggregate workbook contains a column that is the average subjective standard deviation of year-ahead nominal sales growth, report the ratio of the January 2023–December 2025 mean to the January 2017–December 2019 mean, name the sheet and column, and print beside it: this comparison mixes Brexit, the UK energy shock, and carry-forward of old scenario answers, and it is not in US residual units. If that column is absent, write ‘not in the free monthly file’ and stop. Do not reconstruct it from microdata.”

## CV1-S6

**FLAW**

- On the instrument in force at registration, Content Year 5 Cycle 2, fielded 19 October 2026 through 17 January 2027, question 7 is the change in supplier delivery time and question 20 is expected inventories six months ahead. Forecast difficulty is question 16. Current “Super Intelligence (formerly Artificial Intelligence)” use is question 24. A literal build of “Q20 beside Q7” plots inventories against delivery times and calls them forecast difficulty and AI use.
- The forecast item is a five-way rating of how hard overall performance is to forecast, not a subjective variance, and it has no pre-2023 baseline. The AI wording was broadened to “any of its business functions,” and Census created a new time series beginning with the 4 December 2025 release because of a level shift. The 19 October 2026 instrument renames the object Super Intelligence. Scenario: the spliced “AI use” share jumps at those breaks while forecast difficulty is unchanged. The side-by-side chart shows co-movement produced by the questionnaire. The 2025 tariff episode can also make performance harder to forecast while adoption is high, which reads as AI failing. Both readings are available to anyone who treats S6 as evidence. The series are national biweekly aggregates, so they do not link AI-using firms to firms that find forecasting hard.

**SEVERITY:** fatal for a literal build; serious as description

**AMENDMENT:** Replace S6 with: “S6 carries no label and is not evidence about stage 2. Plot the share answering ‘Difficult to forecast future performance’ or ‘Very difficult to forecast future performance’ to the question whose text begins ‘Thinking about the future performance of this business.’ Plot Census’s original AI series and its post-4 December 2025 series as two separate lines, and start a third line on 19 October 2026 for the Super Intelligence wording. Do not splice them. Do not correlate them. Do not refer to these items as Q7 or Q20.”

## SURVIVORS

Five choices survive. SUPPORT is defined as “consistent, not attributed,” so a decline would not establish that AI caused it. The pandemic years are kept out of both windows. S5 and S6 are given no label. EDGAR full-text search is rejected because it returns documents rather than filings and silently ignores SIC filters. S1 is aimed at the right kind of object: the activity-weighted mean of firm-level subjective standard deviations from a five-point distribution.

The thresholds −0.5, 0, and 0.9 do not survive. Neither do the pooled residual, the daily EPU control, the S2 stem list, the S3 level test, the S4 cross-sectional denominator, or the S6 question numbers.

## LOAD-BEARING ASSUMPTION

The registration stands or falls on this claim: after a straight-line adjustment for log daily EPU and log 30-day VIX, the gap between the 2023–2025 mean and the pre-2020 mean of these published series is a gap in the level of managers’ epistemic uncertainty.

That claim is already false for S3 on the wording of the question, and it fails for S1, S2, and S4 if inflation uncertainty, a survey break, panel composition, or the keyword rule can move the statistic across −0.5 or 0. If the assumption is wrong, stage 2 cannot be confirmed or refuted from this file, regardless of the numbers.

## PRACTICALITY

S1 and S4 can be built from the Atlanta Fed’s free workbook. The minimal fix is to freeze one hashed vintage, use the unsmoothed series from December 2016 only, and write the overlap rule down. It is UNCERTAIN whether the realized-distribution sheet has an explicit observed-versus-projected flag; if it does not, restrict the denominator to months at least twelve months before the vintage date.

S2 can be built from the Board’s public Beige Books. The minimal fix is the word-boundary dictionary above, plus a fixed list of District headings so the national summary stays out after the 2017 retitling.

S3 can be built. The codebook name `uncr` is real, and `uncri` minus `uncrd` is the unweighted, not-seasonally-adjusted balance. Use those components so a later January seasonal-factor revision cannot rewrite the result.

S5 is the free-data hole. Aggregate workbooks are public, and the microdata are not part of a free build. The minimal fix is the amendment above: a named column, or an explicit “not in the free file.”

S6 cannot be built as specified. Q7 and Q20 are the wrong questions on the instrument fielded from 19 October 2026. The minimal fix is to name question text and to keep Census’s split AI series apart.

The daily EPU file and CBOE `VIX_History.csv` are free. Substitute the 10-paper monthly EPU index for the daily Newsbank file. That is a one-file change, and it is the series the authors say is fit for a multi-year comparison.

## URLs

Quotes are twenty words or fewer. No post-2015 reading of the registered series is used.

- https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/research-and-data/surveys/business-uncertainty/survey-of-business-uncertainty-methodology.pdf — “we modified the sales-related questions in September 2016”
- Same PDF — “up to December 2025 (previously the period ended in December 2024)”
- Same PDF — “For months up to and including August 2016 we use a nine-month lagged moving average.”
- https://www.atlantafed.org/research-and-data/surveys/business-uncertainty — “rotate between the sales revenue and employment forms, responding to each questionnaire every other month”
- https://www.dallasfed.org/~/media/Documents/research/surveys/TMOS/documents/form.pdf — “How has uncertainty regarding your company's outlook changed in the current month vs. prior month?”
- https://www.dallasfed.org/research/surveys/tmos/definitions — “uncr | Outlook uncertainty - index”
- https://www.dallasfed.org/-/media/documents/research/papers/2025/wp2532.pdf — “Responses are not weighted in the calculation of diffusion indexes”
- Same PDF — “revises historical TSSOS data by recalculating the seasonal adjustment factors”
- https://www.federalreserve.gov/newsevents/pressreleases/other20161130a.htm — “The first Beige Book in the new format will be released on January 18, 2017.”
- https://policyuncertainty.com/media/EPU_BBD_Mar2016.pdf — “compositional shifts potentially distort the longer-term behavior of the daily EPU index”
- https://www.policyuncertainty.com/methodology.html — “dispersion between individual forecasters' predictions about future levels of the Consumer Price Index”
- https://www.cboe.com/tradable_products/vix/ — “market expectations of near-term volatility conveyed by S&P 500 Index option prices”
- https://decisionmakerpanel.co.uk/survey-design/ — “The software we use will carry forward the values given from previous surveys”
- https://decisionmakerpanel.co.uk/data/ — “Aggregated data from the survey are published each month”
- https://www.census.gov/hfp/btos/downloads/BTOS%20Content%20V5%20Core%20and%20SI%20Instrument%20-%20Cycle%202-Tagged.pdf — “Fielded 10/19/2026 – 01/17/2027”
- Same PDF — question 7, “time it takes for this business to receive deliveries from suppliers”
- Same PDF — question 16, “Difficult to forecast future performance”
- https://www.census.gov/hfp/btos/downloads/AI%20Question%20Wording%20Updates.pdf — “create a new time series for the AI questions, beginning with data released on December 4, 2025”