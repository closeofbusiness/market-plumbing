# Grok attack on the g15 spec (CFO Survey expected S&P 500 return), 1 Nov 2026

**Parcel:** `spec.md` (the spec author's draft, before rulings), `page.html` (docs/index.html at 19dacee), `c082.md`. Grok 4.7 256K Extra High
through the fenced Cursor lane, 691 s, 9 searches, 10 fetches, no blocked or unexpected tool, no unfetched URL in the answer. The parcel carried the blind
rule: no CFO workbook and no 2024 or 2026 results page fetched, no CFO value computed or reported. The supervisor re-fetched the methods PDF and found both
quoted passages. Rulings are in the spec's "Supervisor rulings", round 1.

## Return

ATTACKS

1. Verdict: fatal. A registered RISE and AGREES, very likely WITHIN_RANGE, would let the page say the CFO Survey rose over the same quarters by at least 0.10 point and sat inside a Duke-era range, while that cell can be a revised, winsorized mean for firms that closely follow the market, taken on different days from the SPF deadlines of 6 February 2024 and 2 March 2026; a registered FALL would force the page to qualify a sentence that is already true of the SPF mean alone (STOCK10 7.1513% to 7.3056%, +15.4bp in C-082). https://www.philadelphiafed.org/surveys-and-data/stock10 — “Annual average return over the current and next nine years.”

2. Verdict: needs change. The registered yardstick treats eight-quarter changes from the 2001–2020 repeated cross-section as the noise scale for a post-2020 US panel, and the page clause calls those changes “comparable,” while sponsors, sample design, the international cut, the familiarity filter, and outlier treatment all differ. https://www.richmondfed.org/research/national_economy/cfo_survey/research_and_commentary/2020/20200515_introducing_cfo_survey — “moved from a repeated cross-section to a panel data format”

3. Verdict: needs change. The ±0.10 point ZERO zone is 10bp against an SPF rise of 15.4bp, so a same-direction CFO move of 0.09 point is ZERO and the allowed sentence must call it unchanged to within 0.1 point; on full-precision cells that zone is an indifference band, not the resolution of the stored number. No external URL; the 15.4bp figure is C-082.

4. Verdict: needs change. The spec truthfully says the yardstick holds at most nine disjoint spans, but `rank` is still a count out of 64 windows stepped one quarter apart, so seven of the eight quarters are shared and 64 is not a sample size. No external URL; this is the spec’s own T8 and section 4.0. The 4.4% and 8.8% simulation figures were not recomputed here.

5. Verdict: fatal. Matching signs is a weak claim here: the SPF object is professional forecasters’ mean annual-average return over the current and next nine years, collected by a deadline (6 February 2024, and 2 March 2026 after a shutdown delay), while the CFO object is a cross-sectional mean of point forecasts from a filtered firm panel typically in the field in the quarter’s last month, and the rule ignores size. https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/spf-release-dates.txt — “The 2026Q1, 2019Q1, 2013Q4, and 1996Q1 surveys were all delayed”

6. Verdict: needs change. The S&P item is documented as keeping the Global Business Outlook’s exact language, so a blanket “different question wording” in 2020 does not describe this question; the ten-year form “average annual” is quoted for the Duke survey from 2002Q1, which leaves the 2001Q4 start of the yardstick on an earlier form. https://www.richmondfed.org/-/media/RichmondFedOrg/research/national_economy/cfo_survey/the_cfo_survey_methods.pdf — “exact language used in the Global Business Outlook Survey”

7. Verdict: needs change. The published stock table is an unweighted, winsorized mean (and a separate median) for firms that closely follow the market, the question is asked of everyone who does not say they do not follow, the methods table activity-weights macro expectations, and respondents include owner-operators, treasurers, controllers, and accountants, so “the CFO Survey’s mean” and R-A’s “chief financial officers” name a narrower panel than the survey. https://www.richmondfed.org/research/national_economy/cfo_survey/research_and_commentary/2022/20220330_research_commentary — “firms that indicated they closely follow the stock market”

8. Verdict: needs change. Each Q1 release rewrites the historical series, including late responses and a winsorization cutoff that since Q1 2022 uses the full sample through the prior year, so the stored 2024Q1-to-2026Q1 difference is a revised-file change, and C14 only watches vintages after registration. https://www.richmondfed.org/-/media/RichmondFedOrg/research/national_economy/cfo_survey/the_cfo_survey_methods.pdf — “annual revision process began in Q1 2022 and included all historical data”

9. Verdict: needs change. Greenwood and Shleifer’s extrapolation result uses the Graham-Harvey twelve-month CFO forecast, Graham and Harvey call the ten-year premium the stable object, and Ben-David, Graham and Harvey find the one-year point forecast insensitive to positive past returns, so R-B’s “a rise after strong returns is what extrapolation predicts” is not a result about the mandatory ten-year mean. https://www.nber.org/system/files/working_papers/w18686/w18686.pdf — “positively correlated with past stock market returns”

10. Verdict: fine. E1 leaves the §09 gap open, which is what that gap asks for: a third premium series with no shared bond leg. No external URL; the spec’s section 0 matches the page’s §09 wording.

UNCERTAIN. Figure 6 did not come through as text, so the live wording is inferred from “exact language” plus the Duke question; the figure image or a sample questionnaire would settle it. The spec’s “winsorized at 5%” on 2026 pages was not checked, because those results pages were not opened; the methods PDF and the 2022 note both say 2.5 and 97.5. Whether the Duke sheet is US-only, and the actual 2024Q1 and 2026Q1 open and close dates, are in the workbook, which was not opened. A pin match at two quarters after the window would not show that the window endpoints used the same trim and filter.

LOAD-BEARING ASSUMPTION. The sign of `sp_10yrexp_2` in 2026Q1 minus `sp_10yrexp_2` in 2024Q1, in the single current workbook, is the sign of the same expected-return object the §02 sentence reports for the SPF over that interval. If the cell is a rewritten, winsorized, closely-follow mean on different days, every AGREES, DISAGREES, and FLAT sentence tests a different claim.

REQUIRED CHANGES

1. Drop agreement as a verdict on the §02 sentence, and report the CFO change as its own series with the panel, the filter, the trim, and the vintage named in the same sentence.
2. Replace the ±0.10 sign rule with one that can record a rise smaller than 10bp, and print the CFO change next to the SPF’s 15.4bp instead of collapsing both to a sign.
3. Delete “comparable,” stop registering the Duke min/max as the noise test of the post-2020 series, and stop reporting a rank out of 64.
4. Close the open questions on the question text before any registering build: quote the full ten-year question, state that the figure is an annualized mean, and state whether the column is the closely-follow subset and which winsorization percent it uses.
5. Call the statistic the change in the revised historical file, and do not describe the stored 2024Q1 cell as the number first published for that quarter.
6. Rewrite R-A and R-D so the respondents are financial decision-makers at firms, and rewrite R-B so the extrapolation claim is tied to the twelve-month evidence.
7. Put the SPF deadlines (6 February 2024 and 2 March 2026) beside the CFO open and close dates whenever the quarter labels are treated as the same window.

SURVIVES? Yes with changes. The measurement of one revised mean, with the premium and the §09 gap kept out, is a coherent small build; the agreement rule and the Duke range, as registered, cannot test the sentence.