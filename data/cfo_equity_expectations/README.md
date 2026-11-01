# The CFO Survey's expected S&P 500 return, Q1 2024 to Q1 2026

Credit: The CFO Survey (Duke Fuqua School of Business, Federal Reserve Banks of Richmond and Atlanta). The numbers below are derived from the Richmond Fed's revised historical workbook, vintage 1 November 2026 (sha256 1b4e215c5626b741182b8a647c7a66d5c6d448616942d27138f18d37acec6bca).

This build measures the change in the CFO Survey's mean expected S&P 500 return, on a 10-year and a 12-month horizon, between 2024Q1 and 2026Q1 in the 1 November 2026 vintage of the survey's revised historical file, and whether the change has the sign of the Philadelphia Fed forecasters' survey.
For the 10-year horizon (E1) the mean expected return (the series whose recent values the results pages give for firms that closely follow the stock market; see What is not known) was 9.12% in 2024Q1 and 9.25% in 2026Q1: it rose by 0.14 point (sign RISE). The forecasters' survey (STOCK10, CORRECTIONS.md C-082) rose by 0.15 point (+0.1543) over the same quarters, so spf_direction is SAME. Blind: full.

This build measures one leg only, the expected return on the S&P 500 from a panel of financial decision-makers at US firms who say they follow the stock market; it builds no equity premium and subtracts no Treasury yield.

Expectations of 12-month returns in this survey have been found to follow past returns (Greenwood and Shleifer 2014); for the 10-year horizon the evidence is weaker, so a change in either is not evidence about the discount rate.

The survey changed in 2020 (new sponsors, different question wording and outlier treatment), so levels are never compared across 2020; only changes within each series are.

The respondents are financial decision-makers at firms (chief financial officers and others), not investors; the figures are stated expectations, not market prices.

For the 12-month horizon (E2, shown here only) the mean expected return was 6.74% in 2024Q1 and 6.58% in 2026Q1: it fell by 0.16 point (sign FALL); no forecasters' figure is held for this horizon, so spf_direction is na.
The 10-year sign (RISE) and the 12-month sign (FALL) differ; they are two horizons and are not merged.

## What the zone means

The sign uses a zone of 0.10 point: RISE at +0.10 or more, FALL at -0.10 or less, ZERO inside. The zone is a convention equal to the one-decimal resolution of the published pages, fixed before any value was read; it is not a noise bound. Sampling noise is not published for these means (N is about 340-370 per quarter, from the pages' figures for 2026Q2 and 2026Q3), so nothing here says whether a change is large or small against noise. The signed change is always printed to two decimals beside the forecasters' 0.15, so a move of the same direction under 0.10 shows as a number.

## For scale: the described ranges

These are described, never registered or tested, and carry no rank and no label. The Duke-era survey (question form and treatment differ from 2020) had eight-quarter changes with end quarters 2004Q1 to 2020Q1 (2002-2020): for the 10-year return from -1.70 to 1.24 points (n = 63 of 65 windows; at most eight disjoint spans), and for the 12-month return from -4.86 to 3.97 points (n = 63 of 65). The variant inside the current series has end quarters 2022Q3 to 2026Q3 without the registered window: 10-year -0.44 to 1.28 points (n = 16 of 17), 12-month -3.74 to 4.31 points (n = 16 of 17); at most three disjoint spans, and they overlap each other.

## What was known before the build

The only numbers known to the authors were the forecasters' result (STOCK10 7.1513% in Q1 2024 to 7.3056% in Q1 2026, CORRECTIONS.md C-082) and four values from the Q3 2026 results page for firms that closely follow the stock market: 12-month 7.8% (2026Q2) and 7.9% (2026Q3), 10-year 9.7% (2026Q2) and 9.6% (2026Q3). No cell of the window or of the Duke-era series had been seen by anyone writing or briefing the build. The two pinned quarters sit after the window, so the pins do not reach the window values; and the Bank revises the historical file each year (a March 2026 page said data from Q2 2020 to Q4 2025 were revised, which includes 2024Q1). The pins compared as: match.

## What is not known

- Winsorisation: the methods document says S&P 500 expectations are winsorized at 2.5 and 97.5 percent; the Q3 2026 results page says winsorized at 5%. Both are recorded here and neither is resolved.
- The population: the results page gives its figures for firms that closely follow the stock market, unweighted. The workbook does not state whether its _2 columns carry the same filter.

## Dates

CFO Survey field dates: 2024Q1 2024-02-20 to 2024-03-08; 2026Q1 2026-02-17 to 2026-03-05. The forecasters' survey responses were due 6 Feb 2024 and 2 Mar 2026 (the 2026 date was delayed by a government shutdown). The quarter labels are not the same days in the two surveys.

## Dictionary text, verbatim (each line clipped to 15 words)

- through_Q1_2020_dictionary: sp_10_low | low estimate S&P return over the next 10 years | average
- through_Q1_2020_dictionary: sp_10_exp | expected S&P return over the next 10 years
- through_Q1_2020_dictionary: sp_10_high | high estimate S&P return over the next 10 years
- through_Q1_2020_dictionary: sp_1_low | low estimate S&P return over the next year
- through_Q1_2020_dictionary: sp_1_exp | expected S&P return over the next year
- through_Q1_2020_dictionary: sp_1_high | high estimate S&P return over the next year
- from_Q2_2020on_dictionary: sp_12moexp_1 | 10% chance S&P return over the next 12 months will be less than
- from_Q2_2020on_dictionary: sp_12moexp_2 | expectation for S&P return over the next 12 months
- from_Q2_2020on_dictionary: sp_12moexp_3 | 10% chance over the next 12 months S&P return will be greater than
- from_Q2_2020on_dictionary: sp_10yrexp_1 | 10% chance S&P return over the next 10 years will be less than
- from_Q2_2020on_dictionary: sp_10yrexp_2 | expectation for S&P return over the next 10 years
- from_Q2_2020on_dictionary: sp_10yrexp_3 | 10% chance over the next 10 years S&P return will be greater than [...]

## Coverage

- Duke sheet: 74 quarters, 2001Q4 to 2020Q1; sp_10_exp is numeric at 72 and not at 2019Q1(empty), 2020Q1(empty); sp_1_exp is numeric at 72 and not at 2019Q1(empty), 2020Q1(empty).
- Current sheet: 25 quarters, 2020Q3 to 2026Q3 (2020Q2 absent); sp_10yrexp_2 is numeric at 25 and not at none; sp_12moexp_2 is numeric at 25 and not at none.

## Superseded rows

No row has been superseded.

## Column dictionary

- expected return: the answer to the survey's question about the S&P 500 return over the stated horizon, in percent a year.
- mean: the survey's mean of the answers for the quarter (the median columns are not used).
- percentage point (pp): the difference of two percentages; 7.3 percent less 7.1 percent is 0.2 point.
- vintage: the date of the copy of the revised historical file the numbers come from.
- winsorized: extreme answers are replaced by the value at a set percentile before the mean is taken.
- sign: RISE, FALL or ZERO from the exact difference of the two rounded cells and the 0.10-point zone.
- spf_direction: SAME, OPPOSITE or FLAT from the sign beside the forecasters' rise; none for a void row, na for the 12-month horizon. It describes and decides nothing.
- void_reason: none, endpoint_undefined (an endpoint quarter is absent, empty or not a number) or unit_odd (a cell outside -20 to 40).
- pins: match or near, the comparison of four published values with the workbook; never used in a statistic.

## Builder decisions

- The quarter key is the first column whose every cell parses as a quarter label (or year and quarter columns); the survey dates sheet's open and close columns are found by header words.
- A pin whose workbook cell is not a number counts as near; a text cell in a path.csv series is written as status empty.
- unit_odd tests the stored value, not the rounded one. Dictionary lines are clipped to 15 words and are subject to the wording guard like the rest of this file.

## Sources

- Workbook: https://www.richmondfed.org/-/media/RichmondFedOrg/research/national_economy/cfo_survey/current_historical_cfo_data.xlsx (retrieved or supplied, vintage 1 November 2026). The CFO Survey (Duke Fuqua School of Business, Federal Reserve Banks of Richmond and Atlanta)
- Forecasters' survey figure: CORRECTIONS.md C-082 in this repository (Federal Reserve Bank of Philadelphia, Survey of Professional Forecasters).
- Greenwood and Shleifer (2014), Expectations of Returns and Expected Returns, Review of Financial Studies (relayed in the spec; not read by the build).
