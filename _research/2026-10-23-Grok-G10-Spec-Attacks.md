# Grok attacks on the three g10 specs, 23 Oct 2026

Grok 4.7 (extra-high effort) via Cursor, fenced to read and web only; each parcel held one spec and asked for the strongest case against it. No breaches or blocked attempts. The returns are input: each section says what the supervisor checked, and the rulings are in the committed spec.

## Fed H.8 net due to related foreign offices

Spec: [`2026-10-23-H8-Foreign-Offices-Spec.md`](2026-10-23-H8-Foreign-Offices-Spec.md). Wall time 981 s; 13 pages fetched.

**Supervisor check: Grok's 7 Oct 2026 levels (836.9 / −483.6 / 353.3 $bn) equal the second reviewer's pins and the release table. Its Wednesday-close point was taken over the second reviewer's window fix (round 3, R3-1).**

Cited but not fetched in this call: https://www.federalreserve.gov/releases/h8/data/FRB_h8_xml.zip.

### Return

I'll review the spec as written, then check each data source and the papers behind the method against the live web.The spec is a weekly H.8 balance with a quarter-end comparison. I'll check the Fed's own definitions, the reporting form, and whether the quarter-end rule matches how those Wednesdays are dated.The level series matches a FRED print, but the quarter-end rule may be scoring the wrong week. I'll read the release notes, the reporting form, and the calendar the Fed actually uses.The release table matches the spec’s 7 October level and the liability identity. The quarter-end rule still needs a check against the calendar, and the download links need a live response.The Wednesday levels match the release. The quarter-end comparison does not measure the quarter-end date.

**VERDICT: BUILD WITH CHANGES.**

Load-bearing assumption: the Wednesday nearest the quarter’s last calendar day is the quarter-end observation. It is not. H.8 weekly levels are close-of-business Wednesday only. A position that is on the books on the quarter-end date and gone before the next Wednesday never appears in any Wednesday level.

That breaks the registered check. 7 Oct 2026 is a Wednesday in the 16 Oct release, and twelve Wednesdays later is 30 Dec 2026, so 31 Dec 2026 is a Thursday. Section 4.7 scores the change from 23 Dec to 30 Dec, on the 8 Jan 2027 release. The release lag is nine days (16 Oct covers 7 Oct), so that release stops on 30 Dec. Year-end is the next day, and it is not in the scored week. The first Wednesday after it is 6 Jan 2027, published 15 Jan. By then the 31 Dec position can already have left the book. No H.8 Wednesday is the year-end.

The same rule is the Q3 average. In 2019Q1–2026Q3 only five quarter-ends are themselves Wednesdays: 30 Sep 2020, 31 Mar 2021, 30 Jun 2021, 31 Dec 2025, and 30 Sep 2026. The other twenty-six “QE Wednesdays” are one to three days off. For a negative offset, the quarter-end date falls after the scored week, inside the following change. For a positive offset, the quarter-end date and the days after it sit inside one Wednesday-to-Wednesday change. Pooling those with the five on-date weeks pulls the mean toward zero. “Notable” against the placebo minimum detectable difference of about $15bn can then be a false negative, or a difference driven by the mix of offsets. The 30 Sep 2026 case, which is on a Wednesday and which the spec already records, fell from 877.9 to 855.7 to 836.9. One clean week is not the pooled mean.

Two of those mis-dated weeks are also breaks. Notes on Data for the week ending 2 Oct 2019, a Wednesday, records “net due to related foreign offices, −$3.0 billion” at foreign-related institutions. 30 Sep 2019 was the Monday before, so that week is W(2019Q3) and its −$3bn is inside Δin. Footnote 20 puts foreign-related allowances into line 38 beginning 6 Apr 2022. 31 Mar 2022 was a Thursday, so 6 Apr is the following Wednesday and is inside Δout(2022Q1). The amount is not published. The mean uses both weeks.

The 2024–26 endpoints are the same calendar. Under the spec’s own rule, 3 Jan 2024 and 1 Jan 2025 are the nearest Wednesdays to the prior year-ends, and 7 Jan 2026 is the Wednesday after a Wednesday year-end. The multi-year change differences those weeks.

What is sound is the level ledger. On the 16 Oct 2026 release, Table 11 (foreign-related, not seasonally adjusted) prints line 38 for the week ending 7 Oct as 836.9. Table 5 prints the domestically chartered line as −483.6. Table 3 prints all commercial banks as 353.3. In billions, 836.9 + (−483.6) = 353.3. Table 11’s 7 Oct lines 34, 37, 38, 39, and 40 are 1,612.0, 981.6, 836.9, 211.7, and 3,642.2, and 1,612.0 + 981.6 + 836.9 + 211.7 = 3,642.2. The spec’s millions (836,860 and the components) are those prints before rounding to 0.1 billion. Positive is a net liability; footnote 24 puts the due-from position into line 38, which is how the domestic line is negative. Not seasonally adjusted is the right choice: the About page says foreign-related seasonal adjustment is a residual. Keep the XML-first route, the identities, the vintage file, and the ban on reading a stock change as money moved or as the cause of a price.

**REQUIRED CHANGES**

1. Define a quarter-end observation only when the quarter-end date is that Wednesday. List those weeks. Do not average nearest-Wednesday changes, and do not mark the average notable. Reason: Wednesday levels miss any position that is not held at Wednesday close. Source: https://www.federalreserve.gov/releases/h8/about.htm and Table 11 at https://www.federalreserve.gov/releases/h8/current/default.htm.

2. Drop the 8 Jan 2027 magnitude and sign hit. 30 Dec 2026 is the day before year-end, and that release stops there. Record the week as an ordinary Wednesday with its offset. Same sources as change 1.

3. Split every path and average at 6 Apr 2022 and at any Notes week that names the line, including 2 Oct 2019. Do not take a 2019–2026 minimum or maximum across the allowance break. The allowance amount is unpublished. Sources: footnote 20 on the release above, and https://www.federalreserve.gov/releases/h8/h8notes.htm.

4. Do not use 3 Jan 2024, 1 Jan 2025, or 7 Jan 2026 as ordinary start points. Each is a quarter-end Wednesday or the Wednesday after one under this calendar. Same sources as change 1.

5. Rewrite the locked opening sentence. The panel is US branches and agencies plus Edge Act and agreement corporations (release footnote 1). For a branch, FR 2644 item 9.a is one net against its own foreign offices, Edge and agreement subsidiaries, IBFs, head office, and other related US depository institutions, and it includes unremitted profits, capital requirements, reserve accounts, and allowances. Sources: the release above and https://www.federalreserve.gov/apps/reportingforms/Download/DownloadAttachment?guid=386cbedb-80c8-4cce-a618-a7f3e943b747.

6. Do not fail the build if the foreign-related line turns negative. The About page names this series as one that may be negative. A negative print is a possible level, not a failed group binding. Source: https://www.federalreserve.gov/releases/h8/about.htm.

A practitioner would keep the not-seasonally-adjusted Wednesday ledger, the sign box, the identities, and the revision log, and would delete the pooled quarter-end test, the year-end hit, and the basis file from this package. Twenty-four monthly averages placed beside a basis invite a reading the spec forbids, and the monthly figure is a day-weighted average that borrows the next month’s first Wednesday (Technical Q&A).

**SOURCES**

- WORKS. H.8 release, 16 Oct 2026, Table 11 and footnotes 1, 20, and 24. https://www.federalreserve.gov/releases/h8/current/default.htm. Free. Public domain if cited: https://www.federalreserve.gov/disclaimer.htm.
- WORKS. About page: Wednesday levels, residual seasonal adjustment, negative levels allowed, release at 4:15 p.m. Eastern. https://www.federalreserve.gov/releases/h8/about.htm.
- WORKS. Technical Q&A: Call Report weights carried forward, then interpolated over the previous quarter; pro rata months. https://www.federalreserve.gov/releases/h8/h8_technical_qa.html.
- WORKS. Notes on Data, including the 2 Oct 2019 line. https://www.federalreserve.gov/releases/h8/h8notes.htm. The converted body did not show the heading “Notes on Data”; the release page’s navigation does.
- WORKS. DDP retirement notice, 16 Jul 2026: “Build Your Package” goes the week of 9 Nov 2026; preformatted packages and the DDP later. XML remains. https://www.federalreserve.gov/data/data-download-fred-information.htm. FRED’s bulk API needs a key, so leaving FRED out of the script is right.
- WORKS. DDP choose page, release of 16 Oct 2026, offering an SDMX/ZIP labeled 75.5 MB. https://www.federalreserve.gov/datadownload/Choose.aspx?rel=H8.
- FAILS this session. Direct GET of https://www.federalreserve.gov/releases/h8/data/FRB_h8_xml.zip returned HTTP 500. The choose page still advertises the file. UNCERTAIN whether the origin or the fetch layer returned 500. The 75.5 MB label does not match the spec’s 8,438,469-byte zip.
- UNCERTAIN. The four package URLs returned no readable CSV here. A deleted package id comes back as HTML saying the package definition changed, sometimes with status 200. The spec’s header test would already stop that route and continue on the XML.
- WORKS. FR 2644 instructions at the spec’s guid. Cover says effective April 2025; the item 9.a page still says April 2024. Item 9.a matches the spec. The new monthly option is for FFIEC 051 domestic banks under $5bn, and item 9.a is not their line, so it does not break this series. Same instructions URL as change 5.
- Not a spec host. FRED republishes the Board series, free to read, citation requested. https://fred.stlouisfed.org/series/NDFFRIW027NBOG and https://fred.stlouisfed.org/series/NDFFRIM027NBOG.

**REFERENCE POINTS**

Both are the Board’s H.8, so on the 16 Oct 2026 vintage the build should match to the million, not merely be close.

- Week ending 7 Oct 2026, foreign-related, not seasonally adjusted, line 38. FRED: “2026-10-07: 836.8600”, “Billions of U.S. Dollars, Not Seasonally Adjusted.” That is 836,860 million. Table 11 prints “836.9”, which is that figure to 0.1 billion. https://fred.stlouisfed.org/series/NDFFRIW027NBOG and the release URL above.
- September 2026 monthly, same concept. FRED: “Sep 2026: 859.9365”, updated 9 Oct 2026. That is the spec’s 859,936.5 million. Table 11 prints “859.9”. https://fred.stlouisfed.org/series/NDFFRIM027NBOG.

Table 5’s “−483.6” for 7 Oct is the spec’s −483,558 million rounded to 0.1 billion. Do not check this build against BIS locational interoffice totals. Those are a different population and a different net.

**UNCERTAIN**

- Whether the zip server is down or only this fetch of a binary failed, and whether 75.5 MB is a new zip or a label for the uncompressed XML.
- Whether the live package ids still return the six DDP header lines. The fail-open covers a miss. It does not cover a 200 HTML page if the content test is skipped.
- Size of the 6 Apr 2022 allowance inside the line. Footnote 20 gives none.
- Whether positions between two foreign-related offices of one parent cancel in the aggregate. The H.8 does not say. The instructions say each branch reports one net against related US depositories.
- DTCC reuse terms for the medians copied into the basis file. Not fetched.
- The relayed 5 Aug 2026 revision from 834.4 to 839,732. The weeks printed in Table 11 start at 16 Sep.
- The hand list of foreign-related notes omits 31 Mar 2010, which the notes page does name. The parser, if it follows section 3.6, still picks it up. It is outside 2019–2026.
- Guard id M2x in the body versus M21 in the ruling. Bookkeeping, not the estimate.

## BIS international debt securities in US dollars

Spec: [`2026-10-23-BIS-IDS-Dollar-Spec.md`](2026-10-23-BIS-IDS-Dollar-Spec.md). Wall time 864 s; 15 pages fetched.

**Supervisor check: Grok's comparison values (P1 75.56%, P2 91.78%, gap about $0.66trn) equal the second reviewer's to the unit; the reading rule was tightened (R3-1, disclosed).**

Cited but not fetched in this call: https://data.bis.org/topics/LBS.

### Return

I'll review the spec as written, then check each data source and the papers behind the method against the live documentation.The spec is loaded. Next I’ll check the BIS definitions, the CGFS paper’s own wording, and whether the live series still match the keys it names.The live keys match the pins. I’ll check the 2014–19 window, the latest quarter, and the release calendar against the paper’s loan definition.**VERDICT: BUILD WITH CHANGES**

The load-bearing assumption is that the change in published locational-banking stocks, across a window in which every quarter is break-flagged, is the paper’s “increase” in bank lending, and that this comparison alone may be marked `consistent`.

The international-debt-securities (IDS) panel is sound: US-dollar amounts outstanding and net issues, in millions, face value, issuer residence, with `3P` as the world total. The comparison that receives the only pass/fail reading is not. On the current vintage, 2014-Q4 to 2019-Q4:

- IDS stocks: 8,778,278 to 11,586,704. Change = **2,808,426**. Sum of net issues, 2015-Q1 through 2019-Q4 = **2,808,425**.
- Locational banking statistics (LBS) stocks, US-dollar cross-border loans and deposits, all sectors, all countries: 9,975,340.668 to 10,883,514.581. Change = **908,174**. Every quarter from 2014-Q4 through 2019-Q4 is `OBS_STATUS` `B`.
- Sum of break-adjusted flows `F` over 2015-Q1 through 2019-Q4 = **251,397**.

P1, the verdict row, is 2,808,426 / (2,808,426 + 908,174) = **75.56%**, inside 65–85, so the build will print `consistent`. P2, which the spec computes and then forbids a reading, is 2,808,425 / (2,808,425 + 251,397) = **91.78%**. About **$0.66 trillion** of the loan-stock increase is the gap between the stock change and the break-adjusted flow. The band accepts the break-inclusive share and rejects the flow share. BIS defines those adjusted changes as the measure that approximates underlying flows.

A second false sentence is already specified. Q4 calls the US-nationality minus US-residence gap “a definition, not an estimate” of offshore issuance by US parents. Residence is where the issuer is incorporated. Nationality is where the parent is headquartered. The gap is the net of US-parent issuers outside the United States and foreign-parent issuers inside it.

The $22.6 trillion level check is the right LBS concept: IDS 11,586,704 plus loans 10,883,514.581 = **$22.47 trillion**, 0.6% under the paper. Dropping related offices produces about $18.15 trillion. Graph 10 includes interoffice loans. Graph 1’s footnote excludes them. P1 should keep interoffice positions.

## REQUIRED CHANGES

1. **Do not mark P1 `consistent` from the stock share alone.** Report P1 (75.56% on this vintage) as the change in published nominal stocks, report P2 (91.78%) as the break-adjusted flow, and withhold a single reading when they fall on opposite sides of 65–85. Give the break count in dollars as well as in quarters (here, 20 of 20 quarters, about $0.66 trillion). Reason: the pass/fail word attaches to the break-inclusive loan change. Sources: [LBS overview](https://data.bis.org/topics/LBS); [CGFS press release](https://www.bis.org/press/p200618.htm); live series `Q.S+F.C.G.USD.A.5J.A.5A.A.5J.N` and `Q.3P.3P.1.1.C.A.A.USD.A.A.A.A.A.I+G` on `stats.bis.org`.

2. **Rewrite Q4.** Publish the residence stock and the nationality stock as two totals. Describe the difference as that net of two classification gaps. Reason: the IDS glossary defines the two bases that way, and the subtraction is not itself a published population. Source: [IDS overview](https://data.bis.org/topics/IDS).

3. **Say face value, and state the market test.** Amounts outstanding are face value. “International” means listed, registered, or governed outside the issuer’s home country. Reason: “how many dollars borrowers owe” and “sold outside their home markets” are looser than the BIS definitions the cold-reader test is meant to protect. Sources: [IDS overview](https://data.bis.org/topics/IDS); [VoxEU, Pradhan et al.](https://cepr.org/voxeu/columns/dollarisation-waves-insights-bis-international-bond-database).

4. **Score the 7 December 2026 revision test only when 2026-Q3 is present in the file.** Keep the calendar date as a label. Reason: the calendar says data appear no later than the date, and `ids_release` is inferred from that date, so a pull on 7 December before the file updates can be marked held with no change. Source: [release calendar](https://data.bis.org/release-calendar).

## SOURCES

- **WORKS.** IDS data, `WS_DEBT_SEC2_PUB`, no key. Header matches the spec. 2019-Q4 outstanding `11,586,704`; 2026-Q1 `15,871,836`; 2026-Q2 `16,274,316`; 2019-Q4 net issues `147,756`. `ISSUE_CUR=USD` with `ISSUE_CUR_GROUP=A` is the dollar series. `TO1` in the same slot is all currencies. [2019-Q4 query](https://stats.bis.org/api/v2/data/dataflow/BIS/WS_DEBT_SEC2_PUB/1.0/Q.3P.3P.1.1.C.A.A.USD.A.A.A.A.A.I?startPeriod=2019-Q4&endPeriod=2019-Q4&format=csv).
- **WORKS.** LBS data, `WS_LBS_D_PUB`. Header matches. 2019-Q4 `S/A/5J` = `10,883,514.581`, status `B`, pre-break `10,834,001.584`. [2019-Q4 query](https://stats.bis.org/api/v2/data/dataflow/BIS/WS_LBS_D_PUB/1.0/Q.S.C.G.USD.A.5J.A.5A.A.5J.N?startPeriod=2019-Q4&endPeriod=2019-Q4&format=csv). Instrument “loans and deposits” includes repo cash legs and inter-office business ([LBS overview](https://data.bis.org/topics/LBS)).
- **WORKS.** Terms. Reproduction with citation is allowed; use must not imply endorsement; a commercial product may not add a charge for the statistics; the API itself may not be redistributed. Russia: no official data after 28 February 2022. [Legal](https://data.bis.org/help/legal).
- **WORKS.** Calendar, with one trap. The HTML calendar has International debt securities **2026-Q3** and an LBS **2026-Q2 revision** on 7 December 2026, and LBS **2026-Q2** on 30 October 2026. The JSON category `DSS` (“Debt securities statistics”) on that same December date is **2026-Q2**, a different release. The spec’s IDS dates follow the international line. [Calendar](https://data.bis.org/release-calendar); [JSON](https://data.bis.org/api/v0/releasecalendar).
- **WORKS.** CGFS Papers No 65, June 2020. [PDF](https://www.bis.org/publications/cgfs-paper-65-us-dollar-funding-international-perspective.pdf). [Press release, 18 June 2020](https://www.bis.org/press/p200618.htm).
- **FAILS.** `https://www.bis.org/statistics/secstats.htm` still returns 403. The script does not fetch it. The live methodology page is the IDS overview above.
- **UNCERTAIN.** Exact structure-file label strings were not re-read. A label change stops the run under the spec, so it does not silently publish a remapped series.

## REFERENCE POINTS

1. CGFS Paper 65, page 5, data as of Q4 2019: “is $22.6 trillion as of Q4 2019.” The build’s IDS plus all-sector cross-border US-dollar loans should be **$22.47 trillion**, within about **1%**. [PDF](https://www.bis.org/publications/cgfs-paper-65-us-dollar-funding-international-perspective.pdf).

2. BIS press release, 18 June 2020: “three-quarters of the increase in the nominal stock.” P1 should print **75.56%**, within **1 percentage point** of 75. The same paragraph in the paper says dollar IDS “now exceed bank loans”; 11.59 versus 10.88 trillion still exceeds, by about 6%. The break-adjusted share, **91.78%**, is a different quantity and should stay outside that quote. [Press release](https://www.bis.org/press/p200618.htm).

## UNCERTAIN

The paper never prints the start quarter. 2014-Q4 to 2019-Q4 is the five-year stock change that lands on 75.56% now; that is support for the window, and it was computed here, not taken from the spec.

Whether the June 2020 graph used pre-revision stocks is unknowable from the current API. The 75.56% figure is today’s nominal-stock share.

The 1.0% revision rule has no measured base rate, as the spec says. It can be kept only as a statement about revisions.

`3P` is labeled “All countries excluding residents” and is the world total BIS uses, including the United States. The spec’s subtraction for non-US residents matches that arithmetic. The single-country list behind check C04 is still unspecified; a bad list should fail the check rather than change non-US totals.

A practitioner would add face value, the listing/registration/governing-law test, the $0.66 trillion break gap next to both shares, and the nationality gap as a net. They would leave interoffice loans in the paper’s row. They would drop a one-word `consistent` flag, the “definition, not an estimate” sentence, and any relabeling of the IDS dates from the JSON `DSS` rows.

## Quarter-end effect in the cross-currency basis

Spec: [`2026-10-23-Quarter-End-Basis-Spec.md`](2026-10-23-Quarter-End-Basis-Spec.md). Wall time 953 s; 11 pages fetched.

**Supervisor check: the build was re-scoped to descriptive (R3-1) on Grok's term-structure argument; the two papers it cites are relayed, not re-read.**

Cited but not fetched in this call: none.

### Return

I'll review the spec as written, then check each data source and the method against the sources' own documentation.The spec is a registered test of the 1–5-year basis around quarter-ends. I’ll check that estimand against the paper and the live data definitions.**VERDICT: BUILD WITH CHANGES.**

The load-bearing assumption is that the last five liquid 1–5-year prints on or before 31 December 2026, even if that window ends about eight days earlier, are the year-end basis, and that a difference at or below the fifth percentile of overlapping placebos means that basis widened at the reporting date. Built as written, that assumption makes D a mid-December traded-spread contrast and then labels it as a reporting-date result.

## Why the number misleads

The registered window does not have to contain the reporting date. On the tape the author had already dated, the JPY windows for 31 Dec 2024 and 31 Dec 2025 run only to 23 December (gap 8). EUR 31 Dec 2024 has gap 12 and is `gap`. The registered tolerance is 10 calendar days, so the same holiday shape scores `complete`. Christmas sits inside the exclusion zone, so the placebo band has no holiday-matched windows. Section 3.4’s claim that the symmetric control removes a linear trend holds when the next liquid day is the next index. A year-end hole breaks that symmetry. Using the spec’s own drift, about −48 bp to −22 bp over two years, the extra post-window distance biases D by only a few tenths of a basis point. The larger error is the label: a complete December verdict is a mid-December print.

That print is the wrong contract. Du, Tepper, and Verdelhan measure the quarter-end price gap on the one-week contract in the week it begins to span the reporting date. A three-month contract, which spans a quarter-end whenever it is struck, “does not exhibit any particular dynamics.” A 1-year or 5-year swap always spans the date. The par spread can embed a short-dated spike only as a small annuity weight. A further 30–40 bp on a one-week contract is on the order of 1 bp in a 1-year par quote and a fraction of a basis point at 5 years (this scaling is arithmetic, not a published 1–5-year estimate). The design’s JPY detection edge is about 3.5–5 bp. **AGAINST** is what that term-structure fact predicts, and the verdict text will still be read as a statement about the year-end. **SUPPORTS** would be some other move in traded term spreads: tenor mix, package mix, or a holiday print.

`pool1to5` can manufacture several basis points without any tenor’s basis moving. The mix flag allows a mean-tenor shift up to 0.66 years (JPY) before the test is void. Per-tenor medians are rarely published. The flag does not remove a smaller shift.

The fifth percentile is not a 5 percent tail. The spec’s own screen uses 52 overlapping JPY windows from about eight stretches between quarter-ends, and nearest-rank P5 is the third of those 52. The meaning text (“wider than placebo windows almost ever show”) overclaims. Q2 then reports a binomial probability against 0.05×m. The independence caveat is attached only to the standard error.

The supervisor ruling adds 31 Mar 2027 as a second registered look. `REG_TEXT` and the change log do not. JPY and EUR at two dates are four nominal 5 percent looks. The log says there has been no post-registration change.

CFTC leg order for two floating legs is alphabetical by underlier name, not “foreign leg versus flat SOFR.” The public file carries `Spread-Leg 1`, `Spread-Leg 2`, and a notation code for each leg. Payer and receiver identifiers are not disseminated, so the median is a median of traded spreads, not a mid. Package fields exist; this design ignores `share_pkg`. Action types include corrections and errors, so a cumulative file can change after the week is first stored. Three October cells (JPY −21.875 bp, EUR −3.875 bp, GBP +2.438 bp) match a negative yen premium under the foreign-leg convention. They do not show that every earlier row was normalized the same way.

## Required changes

1. Score an anchor only when the anchor day is inside the window (`gap_days` = 0). Otherwise status `gap` and no verdict. Reason: tolerance 10 sits between gaps already measured (JPY year-ends 8, EUR 31 Dec 2024 12), and those windows were dated before the rule was frozen. A gapped December window is not the reporting date, and the control is no longer symmetric. Spec section 3.3 and check C06.

2. Publish D and its rank. Do not issue **SUPPORTS** or **AGAINST** as a test of quarter-end dollar funding. Reason: the published price gap is in short-dated contracts that cross the date; at five years the initiation-date effect is described as very small. CGFS 65, in the text retrieved here, places the reporting-date widening in repo and FX swaps, and its Table 1 puts FX swaps mainly under six months and cross-currency swaps over one year. Sources: https://www.nber.org/system/files/working_papers/w23170/w23170.pdf ; https://portal.northernfinanceassociation.org/viewp.php?n=2240217560 ; https://www.bis.org/publications/cgfs-paper-65-us-dollar-funding-international-perspective.pdf

3. Keep 1-year and 5-year out of one verdict median. Residualize on mean tenor, or leave a tenor `thin` when its own median is unpublished. Reason: a mix shift inside the 0.66-year JPY limit can move a pooled median by as much as the effect this rule can see.

4. Draw the reference distribution from non-overlapping anchors, one per stretch between quarter-ends. Attach the same dependence caveat to the Q2 binomial that the spec already puts on the standard error. Reason: about eight clusters, not 50 independent draws (spec section 3.5 and O-3).

5. Before any build, append the 31 Mar 2027 ruling to the change log and to `REG_TEXT`, or leave it out. Do not treat two dates and two pairs as separate discoveries. December stays unscored unless change 1 is met. March can be described once its window contains 31 March.

6. Define the stored spread as the foreign overnight leg after notation is converted to basis points, drop rows with the package indicator set, and re-read correction and error reports before the 27 Nov freeze. Reason: alphabetical two-float leg order, dual spreads, notation codes, and no disseminated side. https://www.cftc.gov/media/9921/Part43_45TechnicalSpecification12132023CLEAN/download (v3.3, 13 Dec 2023, §1.3.3) and the PPD field list at https://kgc0418-tdw-data-0.s3.amazonaws.com/gtr/static/gtr/docs/RT_PPD_quick_ref_guide.pdf

## Sources

- **DTCC public price dissemination — CHANGED.** Dashboard live 23 Oct 2026, with a Rates tab: https://pddata.dtcc.com/ . Guide v2.8 (May 2025) lists CFTC interest-rate cumulative zips and the fields named above; files are kept 366 days and online history starts 29 Dec 2023, so 2024 through about Oct 2025 cannot be re-downloaded from the cumulative module. https://kgc0418-tdw-data-0.s3.amazonaws.com/gtr/static/gtr/docs/RT_PPD_quick_ref_guide.pdf . Terms updated 11 Mar 2026 are a personal license and, on that page, bar scraping, redistribution, and compiling the content into a database without written permission: https://www.dtcc.com/terms.aspx . Statistics-only commitment matches that limit. “Free to copy” does not. This session did not download a rates zip (UNCERTAIN the file href); commodities slices on the same site were populating.
- **CGFS Papers No 65 (June 2020) — WORKS.** Free PDF: https://www.bis.org/publications/cgfs-paper-65-us-dollar-funding-international-perspective.pdf . “Brief excerpts may be reproduced or translated provided the source is stated.” The retrieved text matches the spec’s page-28 point: repo and FX-swap dollar costs widen around balance-sheet reporting dates. The spec’s page 35, 44, and 73 quotations were not in the retrieved text.
- **CFTC Parts 43/45 technical specification v3.3 — WORKS as the field dictionary, not a price file.** https://www.cftc.gov/media/9921/Part43_45TechnicalSpecification12132023CLEAN/download

The local ledger was not opened. The build reads committed cells only; the checks above are about what those cells are.

## Reference points

1. Du, Tepper, and Verdelhan, NBER Working Paper 23170, February 2017, §5.1.1: “the quarter-end weekly CIP deviation increases by another 30-40 basis points” since January 2015, absolute value, one-week contracts that cross the reporting date, sample through 2016. https://www.nber.org/system/files/working_papers/w23170/w23170.pdf . Their sign is the same foreign-leg convention: negative means the direct dollar rate is below the synthetic dollar rate. The build’s |D| on a 1–5-year pool should miss 30–40 bp by an order of magnitude.

2. Georgievska, Karner, and Syrstad, September 2026 (preliminary): “the basis widens by 4 to 5 basis points into quarter-ends” at three months, and “At five years, the corresponding initiation-date effects are very small.” Year-end contracts at three months are 9–11 bp in the same passage. https://portal.northernfinanceassociation.org/viewp.php?n=2240217560 . Pooled 1–5-year D should lie within about 2 bp of zero, with the five-year sentence, and short of both the 4–5 bp three-month figure and this design’s JPY P5 near −3.5 bp. A |D| beyond about 5 bp agrees with neither figure.

## What a practitioner would change

Add the `gap_days` = 0 gate, separate tenors, a non-overlapping reference set, package exclusion, and a corrections pass before the freeze. Remove the December **SUPPORTS** / **AGAINST** label, the uncaveated binomial probability, and the sentence that the control removes a linear trend at a gapped year-end. Keep the required sentence that a difference in these medians does not show who dealt or that any flow moved a price. March and June are worth a table. They should not be extra registered discoveries stacked on a December window that misses the turn.

## Uncertain

Exact CGFS wording on pages 35, 44, and 73. Whether every historical ledger row uses one notation and the foreign leg (only three days are pinned). How large a Christmas shift in the five-year quote is, beyond the few-tenths drift bias implied by the stated two-year move. Which currencies and estimator sit behind the Georgievska appendix sentence; the paper is preliminary. The eCFR page did not load. No rates zip was opened in this session.
