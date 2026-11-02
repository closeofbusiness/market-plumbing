# Grok attack on the g16 spec draft (2 Nov 2026)

*Grok 4.7 (256k, extra-high), fenced, read and web only. SUCCESS; no breach, no blocked or unexpected tool; every cited URL fetched. Metadata and methodology only; no timeseries call. Verbatim.*

I'll review the design against its sources only: first the spec and scoping notes, then the OFR methodology and the FOMC calendar, without reading any rate or volume series.The spec’s spanning rule and the OFR tenor definitions are the load-bearing parts. I’ll check those pages, the series metadata, and the FOMC dates next—methodology and calendars only, no rate series.The registration does not identify a charge for spanning 31 Dec 2026. The calendar arithmetic that builds the day sets is mostly right; the economic reading of those days is not.

1. FINDING: On two of the three registered crossing days, the 2–7 day bucket mixes loans that end on or before T with loans that end after T, so the published mean is not a price for spanning the quarter-end. The methodology puts a trade in that bucket when its tenor is more than one business day and at most seven calendar days. Under the spec’s own rule that a trade ending on T does not span T, the December book is:
- Mon 28 Dec: loans ending Wed 30 Dec and Thu 31 Dec end on or before T; only a loan ending Mon 4 Jan (seven calendar days) ends after T.
- Tue 29 Dec: a loan ending Thu 31 Dec is inside the bucket and ends on T; loans ending 4 Jan or 5 Jan end after T.
- Wed 30 Dec: the next business day is 31 Dec, so that start is overnight, and every 2–7 day loan (ending 4, 5, or 6 Jan) ends after T.
The idea in the spec, that a 2–7 day loan starting on these days is still open on the quarter-end, holds on the 30th only. OPEN-3 names the mix and the registered statistic still averages the three days with equal weight. The share of the 28 Dec and 29 Dec prints that is the long slice is UNCERTAIN; the release does not split the bucket by maturity day, and only the microdata would settle it.

E large, with no year-end charge. The 2–7 day rate is flat through December. On 28–30 Dec the same-day overnight/open rate is 10 bp lower than on control days, because overnight borrowing has already been pulled and the open book still prints. Crossing spreads are +10 bp, the control median spread is 0, and E = 10. The term rate did not pay anything to be outstanding on the 31st.

A real charge, with E near zero. Only loans with an end date after 31 Dec pay charge C. The 28 Dec and 29 Dec prints are dominated by loans ending on or before the 31st, so those spreads are about 0. The 30 Dec cell is null (no spanning trades, or a disclosure edit) and is dropped. The mean over the two remaining days is 0, the control median is about 0, and E is about 0, while |C| = 2 so the test is still assessed. If the 30 Dec spread instead prints C and the other two days print 0, the registered mean is C/3; a control median on the order of that third, which finding 4 says is plausible, leaves E inside the 1 bp band.

SEVERITY: BLOCKER

CHANGE: Do not register the three-day mean. If a term spread is kept at all, register only the last business day before T, require that day to be non-null, and state in the page sentence that this is the only start date on which every fixed 2–7 day loan ends after T.

SOURCE: https://www.financialresearch.gov/data/files/2025-08-Methodology-TPR.pdf — “7 or fewer calendar days but more than one business day”

2. FINDING: For this particular year-end the loan that bridges 31 Dec is classified as overnight and is excluded from E. Thu 31 Dec 2026 is a business day; Fri 1 Jan 2027 is a holiday; the next business day is Mon 4 Jan. Weekends and U.S. holidays are dropped when deciding whether a repo is overnight, so a Thu–Mon loan is one business day and sits in the overnight/open bucket. SIFMA recommends an early close that day, not a shutdown, so the turn can print, on a short session. T is in neither set. Variant V2 does not recover it: a 2–7 day loan starting on the 31st ends on 5, 6, or 7 Jan and contains that same Thu–Mon interval, so B27(T) − OO(T) subtracts a pure turn spike out of both legs.

SEVERITY: BLOCKER

CHANGE: The registered object on this file, if there is one, is the ex-Fed overnight/open rate and volume on T, set against other days of the same weekday. Leave S(T) out of the registered label.

SOURCE: https://www.financialresearch.gov/data/files/2025-08-Methodology-TPR.pdf — “weekends and U.S. holidays are excluded”
Also https://www.sifma.org/resources/guides-playbooks/holiday-schedule — “Early Close (2:00 p.m. Eastern Time): Thursday, December 31, 2026”

3. FINDING: The subtractor is the overnight/open mean, and open repo is in that bucket by name and by tenor rule. Open and other cancellable trades are tenored to the first date either side can close, which is one business day, so they never enter the 2–7 day bucket even when they are left outstanding over the 31st. Their rate is the rate on a loan that can be closed before the turn. A charge that is paid inside that open book, or avoided by closing it, moves OO and can shrink, erase, or reverse S. Collateral is pooled in both mnemonics (metadata subsetting is “Tenor”), so a shift from Treasury overnight to non-Treasury term produces the same gap.

SEVERITY: BLOCKER

CHANGE: Stop calling S a term-over-overnight turn charge. If a spread remains in a described table, use a Treasury-only pair if the release’s collateral split has one, and say the overnight leg contains open repo. UNCERTAIN what share of the overnight/open bucket is open; a volume share was not read, and reading the series would violate the blind. The metadata name is enough to show the pool exists.

SOURCE: https://data.financialresearch.gov/v1/metadata/query?mnemonic=REPO-TRIV1_AR_OO-P — “overnight and open repurchase agreements”
Also the methodology PDF — “first date at which the dealer or the lender first has the option”

4. FINDING: December 2026 control days number 13 under the written rule, and that set is a poor ordinary-day baseline. T is Thu 31 Dec. Business days on or before 24 Dec are 1, 2, 3, 4, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 21, 22, 23, 24 Dec (18). The effective date 10 Dec falls in (t, t+7] for 3, 4, 7, 8, and 9 Dec only. The 10th stays, because the interval is open at t. Left in K: 1, 2, 10, 11, 14, 15, 16, 17, 18, 21, 22, 23, 24 Dec. Christmas does not reduce this count: 25 Dec is a full close and, if it were open, would be a crossing day (six calendar days before T), not a control. The gate |K| ≥ 5 is passed. Composition is the problem. The FOMC screen deletes the early-December cluster and leaves the median to be set by the rest. Of the 13, the spec’s own Tuesday/Thursday bill flag hits 1, 10, 15, 17, 22, and 24 Dec. The 15th is also the corporate estimated-tax installment and the spec’s coupon date. The 21st–24th are the Christmas week, and the 24th is an early close whose settlements still occur. V3 drops the coupon flag and removes the 15th only. A charge that also lifts mid-month and pre-Christmas spreads is subtracted away in the median, which is the second way a real charge leaves E near zero.

Crossing sets, re-derived. T = 2026-12-31: business days t with t < T and T − t < 7 are 28, 29, and 30 Dec. The 24th is exactly seven calendar days earlier and is out. The 25th is a full close; the 26th and 27th are the weekend. That matches the hardcoded target. T = 2026-11-30 (Monday): the same inequality keeps Tuesday 24 Nov (six days), Wednesday 25 Nov (five), and Friday 27 Nov (three). Thursday 26 Nov is Thanksgiving, a full close. Monday 23 Nov is exactly seven days out. Friday 27 Nov is an early close, not a shutdown, so it stays in the set if OFR publishes early-close sessions. UNCERTAIN only on that publication practice: the documentation withholds “market holidays,” not early closes. The date index would settle it; it was not read.

SEVERITY: BLOCKER

CHANGE: For the December registration, drop from K the 15th, each bill-settlement day, and every business day from the 15th through the 24th. If fewer than five days remain, label December NOT_ASSESSED rather than compare with a baseline taken inside the tax and holiday fortnight.

SOURCE: https://www.law.cornell.edu/uscode/text/26/6655 — “4th | December 15.”
Also https://www.sifma.org/resources/guides-playbooks/holiday-schedule — “Early Close (2:00 p.m. Eastern Time): Thursday, December 24, 2026”

5. FINDING: The eleven non-quarter month-ends are not an exchangeable yardstick, and section 4.1’s reason for keeping the five FOMC months does not follow. The meeting list matches the spec’s effective dates under the day-after rule. One implementation note confirms that rule for the December 2025 meeting (“effective December 11, 2025,” the day after the 9–10 Dec meeting). The five overlaps are real: 30 Oct 2025 against T = 31 Oct; 29 Jan 2026 against T = 30 Jan; 30 Apr 2026, which is T itself; 30 Jul 2026 against T = 31 Jul; 29 Oct 2026 against T = 30 Oct. No other placebo month has an effective date inside its crossing window. An expected cut lowers the term rate relative to same-day overnight and pushes E down; a hike pushes E up. Adding lower values extends the minimum. The maximum, which is what ABOVE has to clear, moves only if some of the five push E up. The calendar page does not show the sign of those five decisions; the signs were not read. “Widens the range and makes ABOVE harder” is therefore not a consequence of keeping them. What keeping them does do is shove the label toward INSIDE. The six “clean” months still include August 2025. Glossary text discontinues the old bucket after 13 Aug 2025, and the B27 metadata `start_date` is 2025-08-15, so that placebo month is the break month. UNCERTAIN whether the first printed B27 day is 13 or 15 Aug; settling it would mean a dates-only timeseries call, which this review does not make. November’s crossing window also contains Thanksgiving and an early-close Friday, so its maturity mix is a different object from December’s.

SEVERITY: CHANGE

CHANGE: Registered placebo = the FOMC-clean month-ends after dropping 2025-08-29 (November 2025, February, May, August, and November 2026). Keep the contaminated months in the described table only. Delete the sentence that contamination makes ABOVE harder. Raise the “at least nine” rule to the size of whatever registered set remains, or VOID is automatic.

SOURCE: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm — “April 28-29” and “December 8-9”
Also https://www.federalreserve.gov/newsevents/pressreleases/monetary20251210a1.htm — “effective December 11, 2025”
Also https://www.financialresearch.gov/short-term-funding-monitor/mnemonics/ — “series discontinued after August 13, 2025”

6. FINDING: The 1.0 bp floor is one published tick of the control median, so it does not do the job OPEN-1 claims for it. Both rate series are percent with precision 2, so each daily S lies on a 1 bp grid. K for December has 13 days, an odd count, so the median is one of those daily prints. Moving that one cell by a published tick moves E by 1.0 bp, which is the whole floor. The three-day mean can sit on thirds, and a one-tick change in a single crossing day moves the mean by about 0.33 bp. OPEN-1 treats the thirds as the reason the floor is fine. The binding grain is the median. When the placebo maximum is already several basis points, the floor never binds. When the placebo range is tight, ABOVE flips on one rounded tick.

SEVERITY: CHANGE

CHANGE: Remove the 1.0 bp clause from the label and let the clean-month range be the only gate. If a deadband stays, require the label to be unchanged when the control median is shifted by 0.01 percentage point.

SOURCE: https://data.financialresearch.gov/v1/metadata/query?mnemonic=REPO-TRIV1_AR_B27-P — `"precision": 2`

7. FINDING: The volume printed beside E is not the sample behind the rate. From July 2024, affiliate repo is taken out of tri-party rates and left in tri-party volumes. A large volume can sit beside a rate computed on a smaller book, and V4’s volume weights follow the larger book. A disclosure edit can also blank the rate when the volume looks ordinary. The spec’s reassurance that volume will show a thin print is not reliable on these series.

SEVERITY: CHANGE

CHANGE: Drop V4. In the side table, describe volume as including affiliate trades the rate excludes, and treat a null rate as “missing,” not as a zero spread and not as evidence the day was busy.

SOURCE: https://www.financialresearch.gov/data/files/2025-08-Methodology-TPR.pdf — “volume series still include affiliate repo”

8. FINDING: The page will over-read the label, and the same free release supports a smaller design. Section 9 puts the label on the quarter-end page next to a sentence about June and September “showing it.” ABOVE will be read as year-end stress, INSIDE as the December analogue of “neither June nor September showed it,” and the 1/12 exchangeability line as a probability. The release itself says these volume-weighted means are not to be compared with the New York Fed reference rates the page already uses. A cheaper design on this API: do not add E. The 4 Jan item already queues SOFR, reverse repo, sponsored repo, and commercial paper. If one OFR print is added, make it the ex-Fed overnight/open rate and volume on T, which is the contract that spans this turn, plus the ex-Fed 2–7 day volume on the prior business day. Keep any term-minus-overnight gap in an appendix, last business day only, against the five clean month-ends, with the maturity-mix sentence in the same line as the number.

SEVERITY: CHANGE

CHANGE: Strike the registered ABOVE / INSIDE / BELOW label from §09 and §10. Queue the overnight/open ex-Fed print on 31 Dec 2026 instead.

SOURCE: https://www.financialresearch.gov/short-term-funding-monitor/datasets/repo/ — “does not allow for direct comparisons with those rates”

9. FINDING: Several checks the spec needs do hold, and they should not be “fixed” into something else. The quoted tenor bullets match the August 2025 methodology PDF, including overnight as one business day and 2–7 days as more than one business day and at most seven calendar days. The API line “starting on a given day and maturing in 7 or fewer days” matches the spec’s start-date reading; the PDF assigns both the rate and the forward-start volume to the start date. The inequality t < T and T − t < 7 is exactly the set of start dates from which a loan of at most seven calendar days can end after T, including the edge the spec states for 24 Dec (a seven-day loan ends on T). It also holds at T−1 across a weekend: Fri 27 Nov 2026 is three calendar days before Mon 30 Nov, the Fri–Mon loan is overnight, and every longer loan inside seven calendar days ends after the 30th. The same is true across the New Year holiday for Wed 30 Dec. The fixed last-business-day list matches the 2025–26 weekday calendar. None of the 2026 T dates falls on a SIFMA full close in the schedule that was fetched. The 2026 Friday after Thanksgiving is an early close, which supports T = 28 Nov 2025 as a business day; that specific 2025 recommendation was not on the page fetched. UNCERTAIN, and the 2025 SIFMA table would settle it. The 8–30 day bullet uses a maximum maturity while the 2–7 day bullet uses a minimum. UNCERTAIN whether a cancellable trade can satisfy both; the PDF never says the buckets are exclusive. That ambiguity hits described V6, not the registered 2–7 day series, as long as fixed-term trades are tenored start to end.

SEVERITY: NOTE

CHANGE: Leave the can-span inequality, the T list, and the FOMC date list as they are. Do not cite the API’s “7 or fewer days” sentence without the methodology’s “more than one business day” clause.

SOURCE: https://www.financialresearch.gov/data/files/2025-08-Methodology-TPR.pdf — “a start date on a given day”

VERDICT: The spec does not survive. Its day-count rule and its copied definitions are largely faithful to the sources, but the registered spread averages days that do not carry a quarter-end commitment and omits the Thursday-to-Monday overnight that does, so an ABOVE or an INSIDE on the page would both misstate the turn.

LOAD-BEARING ASSUMPTION: The 2–7 day volume-weighted mean on a start date less than seven calendar days before T, minus that day’s overnight/open mean, equals a charge lenders require in order to be outstanding on T. That assumption is already in conflict with the tenor rules above; if the 28 Dec and 29 Dec means are mostly loans ending on or before T, or if the bridging loan is the overnight that starts on T, E is not the object the page would be claiming to report.


---

## Second pass, on the amended spec (2 Nov; verbatim)

*First attempt timed out at 30 minutes with 12 pages fetched and no answer; this is a resumed turn with no further fetching. No breach, no blocked tool, no timeseries call in either.*

FINDING: The hashed control line leaves the FOMC window's unit unspecified (`no_FOMC_effective_date_in_(t,t+7]`). Read as seven business days, 1 Dec and 2 Dec drop out of the December set R1-5 lists, placebo medians move, and the label can change or the test can go VOID. The hash check does not test the unit. The selftest names t+7 and t+8 and does not say calendar days.

SEVERITY: BLOCKER

CHANGE: Write `no_FOMC_effective_date_in_(t,t+7_calendar_days]` in the fence, and add a selftest that keeps the day when the effective date falls on calendar t+8.

https://www.financialresearch.gov/data/files/2025-08-Methodology-TPR.pdf — "7 or fewer calendar days but more than one business day"

FINDING: R1-9 is wrong that the section 9 sentence contains the over-read. The sentence reports INSIDE as "inside that range." INSIDE also covers an E outside that range when the sign test fails. "Further above" covers a positive gap versus the median, including when the 2–7 day rate is still below overnight. "Closer to" covers a negative gap, including when the gap widens below zero. The parenthetical legs need not add to the gap. The label on this one start date can stand.

SEVERITY: CHANGE

CHANGE: Use: "On 30 December 2026, the 2–7 day tri-party rate minus overnight/open was [x] bp; the December control median was [m] bp (term leg [y], overnight leg [z]; the legs need not add to the gap; overnight/open includes open repo). Eight month-ends ranged from [a] to [b] bp. Registered label: [LABEL]. One day and one spread; it does not say why."

https://www.financialresearch.gov/data/files/2025-08-Methodology-TPR.pdf — "on that day, including open repo"

FINDING: 15 Feb 2026 is a Sunday and the next weekday, 16 Feb, is Washington's Birthday, a full close. The coupon exclusion is the next date present in both series, 17 Feb, which sits inside February's control window. A weekday reading of "first business day" leaves that settlement day in K and can move the placebo median.

SEVERITY: NOTE

CHANGE: Add a selftest in which the 15th is a Sunday, the next weekday is absent, and the exclusion falls on the next date present in both series.

https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/ — "Monday, February 16 | Washington's Birthday"

VERDICT: The section 0 claim holds for Friday 28 Aug 2026 into Monday 31 Aug and for Wednesday 26 Nov 2025 into Friday 28 Nov: Thanksgiving is a U.S. holiday and the weekend drops out, Friday 28 Nov is an early close whose settlements still occur, so the one-business-day loan is overnight and every 2–7 day loan, cancellable trades included, is still open on T. T−1 is the effective date in each of the four kept months, so both legs start that day, which justifies keeping them; the share agreed before the announcement is UNCERTAIN and trade-level timestamps would settle it, and R1-5 stands.
