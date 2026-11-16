# AJ1: Grok attack on version 1 (16 November 2026)

Grok 4.7 (Cursor, fenced: read and web only, blind rule in the parcel). Status SUCCESS; no breaches, no blocked tools, no cited URL
left unfetched. It fetched only documentation (BLS developer pages, CES and JOLTS code lists, CES NAICS 2022 page, Census BTOS
methodology and question-wording PDF, Census NAICS pages). It reported seeing a search snippet of a data page and a chart of
BTOS AI shares and said it used neither; it reported no employment or openings figure. The supervisor's rulings are in version 2
of the spec. Return verbatim below.

---

I'll read the pre-registration and check its data claims against BLS and Census documentation only, without pulling any employment, openings, or AI-use figures.The API limits and the NAICS break are documented; next I’ll confirm series-ID construction and which industries are actually published, without using any data values.The test sinks if the rank of BTOS AI use is correlated with any non-AI shock that hit these industries in 2023–25 and was not already in 2017–19 growth. The spec names the shocks — interest rates, the end of the post-pandemic hiring boom, and software-sector cycles — and then still lets a one-sided Spearman print SUPPORT or AGAINST.

A search snippet showed a `data.bls.gov` timeseries page and old CES benchmark tables, and the BTOS wording PDF contains a chart of AI-use shares. Those figures are not used below. The Census concordance workbook returned HTTP 500; the CES NAICS 2022 page is the source for the match.

**F1. fatal.** Claim: a significant Spearman means creation or displacement. Reason: P1 and P2 partial out only 2017–19 growth, so any 2023–25 shock that lines up with AI use (rates, the hiring-boom reversal, the software cycle) is labelled as AI. Source: none (the spec’s asymmetry paragraph).

**F2. fatal.** Claim: AJ1-P1 says employment “grew at least as much,” and SUPPORT is a significantly positive Spearman with every leave-one-out rho above zero. Reason: “at least as much” includes equal growth, which this rule labels INCONCLUSIVE, while AGAINST needs only a negative p≤0.05 and does not require leave-one-out rhos to stay negative, so the registered label is easier to land on displacement. Source: none (the statements table).

**F3. fatal.** Claim: P3 measures whether “job openings held up,” using the openings rate in 2025 minus 2019. Reason: the rate’s denominator is employment plus openings, so industries that added jobs record a lower rate even if openings did not fall, and the 2019–25 gap includes the pandemic rather than the post-2023 window used for employment. Source: https://www.bls.gov/opub/hom/jlt/calculation.htm Quote: “The job openings rate is computed by dividing the number of job openings by the sum of employment and job openings and multiplying that quotient by 100.”

**F4. fatal.** Claim: each JOLTS industry is one observation, with durable and nondurable manufacturing both taking the 31–33 AI mean. Reason: the published list is nested (manufacturing and its two parts, financial activities and its two parts, education and health and its two parts, leisure and its two parts, trade-transport-utilities and its three parts), the spec never selects a non-overlapping partition, and two manufacturing rows share one AI value. Source: https://download.bls.gov/pub/time.series/jt/jt.industry Quote: “300000 Manufacturing” and “320000 Durable goods manufacturing” and “340000 Nondurable goods manufacturing” and “510099 Financial activities” and “540099 Professional and business services”.

**F5. fatal.** Claim: 511 matches to 513, and 519 matches to 519. Reason: 2022 publishing is the old publishing industries plus part of old internet publishing, and old 519 was split across publishing, broadcasting and content providers, and a remainder that kept the code 519. Source: https://www.bls.gov/ces/naics/naics-2022.htm Quote: “New NAICS 2022 newspaper publishers (50-513110) combined a portion of internet publishing and broadcasting and web search portals (50-519130) and all of newspaper publishers (50-511110).” Also: “Other information services … CEU5051900001” to “Web search portals, libraries, archives, and other information services(1)(2) … CEU5051900001”.

**F6. major.** Claim: dropping 454 removes the NAICS 2022 break from the employment sample. Reason: 454’s own series was discontinued with no successor, and part of electronic shopping was moved into motor-vehicle dealers, which stays in the labelled sample as 441. Source: https://www.bls.gov/ces/naics/naics-2022.htm Quote: “Nonstore retailers split into many different industries and has no closest equivalent.” And: “A portion of electronic shopping and mail-order houses (42-454100) moved into NAICS 2022 motorcycle, boat, and other motor vehicle dealers (42-441220).”

**F7. major.** Claim: BTOS 523 matches the CES three-digit series for 523. Reason: that CES series also covers NAICS 525, and BTOS drops 525 from its target population, so the employment outcome contains an industry the AI rate excludes. Source: https://www.bls.gov/web/empsit/cesseriespub.htm and https://www2.census.gov/data/experimental-data-products/business-trends-and-outlook-survey/methodology.pdf Quote: “55-523000 | 523” and “55-523000 | 525”. And: “Funds, Trusts, and other financial vehicles (NAICS = 525)”.

**F8. major.** Claim: the series are three-digit NAICS, formed as CEU plus an 8-digit industry code plus 01, including 541 and 611. Reason: CES publishes sector 54 as CEU6054000001 and private educational services (sector 61) as CEU6561000001; padding 541 and 611 the way 238 is padded builds IDs that are not the published series. Source: https://www.bls.gov/ces/naics/naics-2022.htm Quote: “Professional and technical services | CEU6054000001” and “Educational services | CEU6561000001 … Private educational services | CEU6561000001”.

**F9. major.** Claim: the held file is NAICS 2017, so the 2017-to-2022 crosswalk is the right match. Reason: the October 2026 BTOS methodology and the BTOS program page describe the survey on 2022 NAICS, while 454 and 511 cannot be 2022 subsectors, so either the crosswalk double-converts a 2022 file or the file is an older 2017 extract. UNCERTAIN which, until the file’s code column is checked without reading the shares. Source: https://www2.census.gov/data/experimental-data-products/business-trends-and-outlook-survey/methodology.pdf Quote: “excluding the following 2022 North American Industry Classification System (NAICS) codes”.

**F10. major.** Claim: question 7, “use AI in producing goods or services,” averaged over 46 cycles of 2024–2025 in `AI Core Questions.xlsx`, is one exposure. Reason: Census replaced that wording, started a new series with the December 4, 2025 release, and says the Core Questions download is the new series while the old wording is “AI Core Questions (Original)”; collection also skipped October 6–November 16, 2025. Source: https://www.census.gov/hfp/btos/downloads/AI%20Question%20Wording%20Updates.pdf and the methodology PDF. Quote: “create a new time series for the AI questions, beginning with data released on December 4, 2025.” And: “The Core Questions downloads contain the new time series data.” The PDF also shows a chart of AI-use shares; those shares are not used.

**F11. major.** Claim: the subsector “Yes” mean is AI use in the same units as CES employment. Reason: a BTOS percentage is a nonresponse-adjusted weight across businesses, suppression drops any estimate with a relative standard error above 50 percent, and keeping only subsectors published in every cycle selects large, precisely measured industries. Source: https://www2.census.gov/data/experimental-data-products/business-trends-and-outlook-survey/methodology.pdf Quote: “the published percentage estimate for a particular response category is calculated as the sum of the nonresponse-adjusted weights for all responses in that particular response category, divided by the sum of the nonresponse-adjusted weights for each business responding to the question.” And: “BTOS suppresses estimates with relative standard errors greater than 50%.”

**F12. major.** Claim: AI use is predetermined for growth from 2023 to 2025. Reason: the exposure is the average of cycles inside 2024–2025, which is the outcome window, so industries that were already hiring or shrinking can adopt AI and the Spearman reads the reverse direction. Source: none (windows section plus the BTOS question dating from the PDF above).

**F13. major.** Claim: g_post and g_pre answer “since 2023” relative to the industry’s own pre-trend. Reason: both rates skip the change from 2019 to 2023, so a one-time level shift in the first year of widespread generative AI is in neither term, and P2 cannot see it. Source: none (windows section). CES itself does not have a classification break inside that gap: history was rebuilt on NAICS 2022. Source: https://www.bls.gov/ces/naics/naics-2022.htm Quote: “Forward ratios were held constant and applied to each monthly CES employment estimate for the entire history of the series, usually back to 1990”.

**F14. major.** Claim: where one JOLTS industry covers “two BTOS sectors (professional and business services = 54 + 55 + 56),” weight the AI means by 2019 CES employment, and drop 55 if BTOS does not publish it. Reason: that is three sectors, JOLTS professional and business services still contains 55 after it is dropped from the AI mean, and the weight is employment while the P3 outcome already has employment in the denominator. Source: https://download.bls.gov/pub/time.series/jt/jt.industry Quote: “540099 Professional and business services”.

**F15. major.** Claim: the supplier check drops 511, 519, and 541. Reason: 518 is the computing-infrastructure series and is marked affected by the NAICS 2022 update, and it stays in both the labelled sample and that check. Source: https://www.bls.gov/ces/naics/naics-2022.htm Quote: “Data processing, hosting and related services | CEU5051800001 … Computing infrastructure providers, data processing, web hosting, and related services(1) | CEU5051800001”.

**F16. major.** Claim: version 1 with no key returns the CES and JOLTS history needed here. Reason: the limits are real (25 series, 10 years, 25 queries a day, and 50 requests per 10 seconds), registration is not required for v1, and a request with no years returns three years, so a default call never contains 2017; v1 also returns no series title, and the year-specified sample includes an M13 annual row that must be dropped before a twelve-month mean. One labelled query of the 22 subsectors fits; subsectors plus sector weights plus JOLTS does not. Source: https://www.bls.gov/developers/api_FAQs.htm and https://www.bls.gov/developers/api_signature.htm Quote: “Daily query limit … 25” and “Series per query limit … 25” and “Years per query limit … 10” for version 1.0 unregistered. And: “The Single Series and Multiple Series signatures will return a three-year period of data by default.” And: “version 1.0 of the BLS Public Data API only returns raw data from BLS surveys; it does not include metadata.”

**F17. minor.** Claim: NSA JOLTS is a fixed vintage once fetched. Reason: not-seasonally-adjusted JOLTS is aligned to CES and is recalculated for the most recent five years when seasonal factors change, so an unpinned release date changes P3. Source: https://www.bls.gov/opub/hom/jlt/calculation.htm Quote: “the data series that are not seasonally adjusted are also recalculated for the most-recent 5 years to reflect the effect of the updated seasonal adjustment factors on the alignment process.”

**F18. minor.** Claim: 10,000 permutations of “the AI ranking,” seed “fixed and recorded,” one-sided p≤0.05, decide three statements. Reason: the seed is not in the spec, permuting ranks rather than values breaks ties that P3 creates on purpose, three statements are unadjusted, and Monte Carlo error around 0.05 can flip the label. After dropping 454 the employment n is 22, and a one-sided 5 percent Spearman at that n is about 0.36, so one subsector moves the label. Source: none (permutation paragraph). The null critical value is a design fact, not a statistic from these series.

**F19. minor.** Claim: every listed three-digit subsector is published as all-employees NSA back through 2017. Reason: 238, 423, 424, 441, 512, 513, 518, 519, 522, 523, 524, 531, 54, 561, 61, 621, 624, 711, and 713 are on the published-series list with all-employees coverage and start years of 1990 or earlier. UNCERTAIN for 722, 811, and 812: the published-series page was truncated at 711, and those three are not in the title-change exhibit. Within-811 detail was recombined (exhaust and transmission repair into specialized automotive repair; computer repair into electronic and precision equipment repair), so the 811 boundary should be checked on that page. Source: https://www.bls.gov/web/empsit/cesseriespub.htm and https://www.bls.gov/ces/naics/naics-2022.htm Quote: “20-238000 | 238 | Specialty trade contractors” and “50-513000 | 513 | Publishing industries” and “Amusement, gambling, and recreation industries | CEU7071300001”.

## Series IDs

CES all-employees NSA is CE + U + the 8-digit CES industry code + 01. Confirmed from https://www.bls.gov/ces/naics/home.htm (“Positions 1-2 CE … 3 U … 4-11 Industry Code … 12-13 01”) and https://download.bls.gov/pub/time.series/ce/ce.txt (“All employees (01)”; “U=Unadjusted”).

| BTOS code | Series ID | Confirmed title | Source |
|---|---|---|---|
| 238 | CEU2023800001 | Specialty trade contractors | cesseriespub.htm |
| 423 | CEU4142300001 | Merchant wholesalers, durable goods | cesseriespub.htm and naics-2022.htm |
| 424 | CEU4142400001 | Merchant wholesalers, nondurable goods | cesseriespub.htm and naics-2022.htm |
| 441 | CEU4244100001 | Motor vehicle and parts dealers | cesseriespub.htm |
| 512 | CEU5051200001 | Motion picture and sound recording industries | cesseriespub.htm |
| 511→513 | CEU5051300001 | Publishing industries (replaces CEU5051100001) | naics-2022.htm |
| 518 | CEU5051800001 | Computing infrastructure providers, data processing, web hosting, and related services | naics-2022.htm |
| 519 | CEU5051900001 | Web search portals, libraries, archives, and other information services | naics-2022.htm |
| 522 | CEU5552200001 | Credit intermediation and related activities | cesseriespub.htm |
| 523 | CEU5552300001 | Securities and investments, and this same code also covers NAICS 525 | cesseriespub.htm |
| 524 | CEU5552400001 | Insurance carriers and related activities | cesseriespub.htm |
| 531 | CEU5553100001 | Real estate | cesseriespub.htm |
| 541 | CEU6054000001 | Professional, scientific, and technical services (sector 54) | naics-2022.htm |
| 561 | CEU6056100001 | Administrative and support services | cesseriespub.htm |
| 611 | CEU6561000001 | Private educational services (sector 61) | naics-2022.htm |
| 621 | CEU6562100001 | Ambulatory health care services | cesseriespub.htm |
| 624 | CEU6562400001 | Social assistance | cesseriespub.htm |
| 711 | CEU7071100001 | Performing arts, spectator sports, and related industries | naics-2022.htm |
| 713 | CEU7071300001 | Amusement, gambling, and recreation industries | naics-2022.htm |
| 722 | CEU7072200001 | UNCERTAIN | cesseriespub.htm truncated |
| 811 | CEU8081100001 | UNCERTAIN | cesseriespub.htm truncated |
| 812 | CEU8081200001 | UNCERTAIN | cesseriespub.htm truncated |

Weights and the national comparison, from the same published-series page: total private CEU0500000001; manufacturing CEU3000000001; durable goods CEU3100000001; nondurable goods CEU3200000001; management of companies CEU6055000001; administrative and waste services CEU6056000001.

JOLTS NSA openings rate, national, all size classes: JTU + 6-digit industry code + `00` + `00000` + `00` + `JOR`. Layout from https://www.bls.gov/jlt/jlt_series_changes.htm and https://download.bls.gov/pub/time.series/jt/jt.txt; `JO` is “Job openings” and `R` is “Rate” (https://download.bls.gov/pub/time.series/jt/jt.dataelement and jt.ratelevel). These strings were assembled from that layout. `jt.series` was not opened row by row.

Use only a non-overlapping private partition: JTU230000000000000JOR construction; JTU320000000000000JOR durable goods; JTU340000000000000JOR nondurable goods; JTU420000000000000JOR wholesale; JTU440000000000000JOR retail; JTU480099000000000JOR transportation, warehousing, and utilities; JTU510000000000000JOR information; JTU520000000000000JOR finance and insurance; JTU530000000000000JOR real estate and rental and leasing; JTU540099000000000JOR professional and business services; JTU610000000000000JOR private educational services; JTU620000000000000JOR health care and social assistance; JTU710000000000000JOR arts, entertainment, and recreation; JTU720000000000000JOR accommodation and food services; JTU810000000000000JOR other services. Drop parents 000000, 100000, 300000, 400000, 510099, 600000, and 700000, and drop government 900000, 910000, 920000, 923000, and 929000.

## Amendments

1. Write the series IDs above into the spec, including CEU6054000001 for 541 and CEU6561000001 for 611, and resolve 722, 811, and 812 from the published-series table before any fetch.
2. Label P1 and P2 only on the sample that drops 441, 513, 518, 519, and 541, and report the NAICS-flagged matches as unlabelled.
3. Drop 523 from the labelled employment test, because CEU5552300001 includes NAICS 525 and BTOS excludes 525.
4. Take AI use only from “AI Core Questions (Original),” list the cycle IDs in the spec, and exclude periods 202521–202523 and every period from 202524 onward.
5. Set the labelled exposure to cycles whose reference period ends before January 2024, and keep the 2024–2025 mean unlabelled.
6. Keep g_post as ln(mean of the twelve 2025 months) minus ln(mean of the twelve 2023 months), and report the 2019-to-2023 log change beside it so a one-time level shift cannot disappear between the two windows.
7. Define the labelled openings outcome as the 2025 mean level minus the 2023 mean level on series ending in `JOL`, and leave the rate unlabelled.
8. Pre-specify the JOLTS sample as the fifteen child industries above, drop transportation, and drop professional and business services from the labelled test because sector 55 has no BTOS mean and still sits inside JTU540099000000000JOR.
9. If a JOLTS industry is kept and covers more than one published BTOS sector, weight those sector means by 2019 CES employment and print the employment share of any missing sector in the denominator.
10. Require the same rule on both sides: one-sided permutation p≤0.05 and every leave-one-out rho of that sign, and rewrite P1’s sentence to “grew more,” with equal growth left INCONCLUSIVE.
11. Pin seed 20261116, draw 100,000 permutations of the AI values, set p = (1 + the number of permutations with Spearman greater than or equal to the observed) / 100001, and label INCONCLUSIVE when that p is within two Monte Carlo standard errors of 0.05.
12. Label only the residual Spearman of (g_post − g_pre) on AI use after partialling a 2020 log employment change and a rate-sensitive indicator fixed now as 238, 441, 522, and 531.
13. Fetch with POST bodies of at most 25 series, startyear 2017 and endyear 2025, drop period M13, and stop if any ID returns “series does not exist.”
14. Name the Employment Situation release and the JOLTS release in the spec before the first fetch, hash that JSON, and do not refetch.
15. State, next to every label, that the result is a rank association inside this suppression-selected set of firm-weighted AI rates, and that jobs created in other industries are outside the test.
