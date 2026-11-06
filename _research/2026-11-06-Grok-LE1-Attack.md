# Grok attack on LE1 (6 Nov 2026)

*Grok 4.7 (256k, extra-high), fenced read + web through cursor_dispatch.py; 11 fetches, no breach, no URL cited unfetched. Blind rule: no repo or money-market value dated 5 Nov or later. Verbatim below. The supervisor checked the 5 Nov bill settlement on Treasury's schedule and the bill-day pass-through on pre-event data; the outcome is amendment LE1-A in [the registration](2026-11-06-Live-Event-5-Nov-Repo-Prereg.md).*

## 1. Control days

**VERDICT: FATAL**

Two of the ten dates have no Treasury auction or settlement on the schedule: Friday 13 November and Friday 20 November. The other eight are operation days, and 20 November fails the registration’s own “can cross a turn” rule. Monday 2 November settles the 2-year, 5-year, 7-year and 2-year FRN, because 31 October is a Saturday, and it also auctions the 13-week and 26-week bills. Monday 9 November auctions the 3-year note and the 6-, 13- and 26-week bills. Tuesday 10 November settles the 4-week and 8-week bills auctioned on the event day, auctions the 10-year note, and is the session before the SIFMA full close, so the overnight leg has to bridge Veterans Day. Thursday 12 November settles the 6-, 13- and 26-week bills, auctions the 30-year bond, and is the reopen after that close. Tuesday 17 November settles the 4-, 8- and 17-week bills. Wednesday 18 November auctions the 20-year bond. Thursday 19 November settles the 6-, 13- and 26-week bills, auctions the 10-year TIPS, and a 7-calendar-day loan started that day ends on Thanksgiving. Monday 23 November auctions the 2-year note, and a loan in the 2–7 day bucket can span Thanksgiving and reach Monday 30 November. The mid-month agency payment that falls on a non-business 15th moves to Monday 16 November, which is already excluded, and there is no quarterly estimated-tax date in November. There is no FOMC meeting between 28 October and 8 December, so that exclusion survives. After the settlement, auction and holiday-bridge dates are removed, fewer than seven days remain, which is the block’s own NO READING floor.

**Amendment:** Strike the label. Rebuild C with the exclusions already used for coupons, bills, auctions, holiday bridges and turns, and record that the surviving count is under 7.

- https://home.treasury.gov/system/files/221/TentativeAuctionScheduleQ32026.pdf — "Monday, November 02, 2026 | Thursday, November 05, 2026"
- https://www.sifma.org/resources/guides-playbooks/holiday-schedule — "Early Close (2:00 p.m. Eastern Time): Friday, November 27, 2026"
- https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm — "October 27-28" and "December 8-9"
- https://www.federalreserve.gov/econres/feds/files/2021028pap.pdf — "upward pressure on the repo rate of about 6 basis points"
- https://capitalmarkets.freddiemac.com/mbs/products/giants — "payment will be made on the next business day"
- https://www.irs.gov/publications/p509 — "15th day of the 4th, 6th, 9th, and 12th months"

## 2. The event day

**VERDICT: FATAL**

Thursday 5 November settles the 13-week and 26-week bills auctioned on Monday 2 November and the 6-week bill auctioned on Tuesday 3 November, and it is also the auction day for the 4-week and 8-week bills that settle on Tuesday 10 November, a control day. It is the session after the Wednesday 4 November refunding announcement. The control list does contain the same Thursday bill cycle, on 12 November and 19 November. Each of those days adds a coupon auction and a holiday problem, and the registered median treats them as two of ten mixed days. The bill-settlement-only control is described, not registered, so it cannot rescue the label. Anbil, Anderson and Senyuz estimate the settlement effect on the overnight repo level, about 6 basis points at mid-month and 15 at month-end. Whether that level effect passes through to the 2–7 day minus overnight spread is UNCERTAIN. A study of this spread on settlement days would settle it.

**Amendment:** Withdraw the equity label. A re-registered control would have to be other 6-/13-/26-week settlement Thursdays with no coupon auction and no holiday bridge. None exists in this window.

- https://home.treasury.gov/system/files/221/TentativeAuctionScheduleQ32026.pdf — "13-Week BILL | Thursday, October 29, 2026 | Monday, November 02, 2026 | Thursday, November 05, 2026"
- https://www.cmegroup.com/education/events/econoday/693000 — "Issue [Settlement] Date | 2026-11-05"
- https://www.federalreserve.gov/econres/feds/files/2021028pap.pdf — "On Treasury coupon settlement days, we typically see upward pressure on repo rates"

## 3. Leave-one-out band

**VERDICT: AMEND**

Assume the ten control values are i.i.d. continuous uniform, and assume the g16 rule that an even-count median is the mean of the two middle values. The block never restates that rule. Order the controls X(1) < … < X(10). The leave-one-out median is X(6) when a bottom-half day is dropped and X(5) when a top-half day is dropped, so lo = X(1) − X(6) and hi = X(10) − X(5). A new draw Y falls outside the band only if it clears the sample maximum or minimum by half the gap between X(5) and X(6). For uniforms, the spacing calculation gives exactly 4/33, about 12.1 percent, two-sided. Merely falling outside the sample range, which is necessary but not sufficient, has probability 2/11 for any continuous i.i.d. law. The 4/33 figure is not distribution-free: bimodal data can make it near zero, and heavier tails push it up toward 2/11. These November days are also not i.i.d. What would settle the relevant frequency is the historical distribution of this spread on matched Thursdays. This review does not estimate that. On a 1 basis point grid, ties shrink the gap and the chance moves toward 2/11. Either way, an ordinary day is outside often enough that ABOVE or BELOW is not a rare-event finding.

**Amendment:** Write “under an i.i.d. uniform null this happens with probability 4/33, and for any continuous i.i.d. law with probability less than 2/11” into the label sentence, and restore g16’s one-tick sensitivity check.

## 4. Two-sided label

**VERDICT: AMEND**

The three-way label is a partition: the two tails cannot both fire, and equality stays INSIDE. The clauses E>0 and E<0 never change it. For any control size, the leave-one-out residual of the largest control value is at least zero, so hi ≥ 0, and the residual of the smallest is at most zero, so lo ≤ 0. Then E > hi already implies E > 0. Those clauses do work in g16, where the placebo deviations can all lie on one side of zero. They cannot do that work for a band built from deviations around a median. There is a second mismatch: E subtracts the median of all ten days, while each e(c) subtracts the median of the other nine. The event is not scored with the statistic that forms the band.

**Amendment:** Delete “and E>0” and “and E<0”. Score the event and the controls with the same function, deviations from one common median, and state the null frequency beside the label.

## 5. Literature

**VERDICT: AMEND**

The fetched literature does not estimate a tri-party 2–7 day minus overnight spread on equity stress days. What it does say cuts against reading this label as that effect. Aldasoro, Hördahl and Zhu find that money-market conditions co-move only loosely with the VIX, that the VIX drops out of their predictor of money-market stress beyond the coincident horizon, and that repo-OIS surged in the February 2018 VIX spike along with the crisis episodes, while their money-market index rose only moderately then and was otherwise subdued outside the financial crisis and Covid. The September 2024 FOMC minutes, covering the early-August 2024 equity break, say overnight secured rates were largely unchanged over that intermeeting period and that short-term funding stayed stable. That is a period average, not a day study. Anbil, Anderson and Senyuz’s measured repo moves are settlement and month-end effects on the overnight level. The August 2024 precedent is that a large equity day can leave overnight secured rates unmoved, while the precisely estimated repo moves are the calendar effects this registration leaves inside C and on the event day.

**Amendment:** Do not attach the label to an equity-stress channel. The object the literature actually varies is overnight repo against OIS, on days purged of settlement. This window cannot supply those days.

- https://www.bis.org/publications/under-pressure-market-conditions-and-stress.pdf — "co-move only loosely with the VIX"
- https://www.bis.org/publications/under-pressure-market-conditions-and-stress.pdf — "surged during the GFC, the US MMF reform, the VIX spike in early 2018"
- https://www.federalreserve.gov/monetarypolicy/fomcminutes20240918.htm — "Overnight secured rates were largely unchanged"
- https://www.federalreserve.gov/monetarypolicy/fomcminutes20240918.htm — "conditions in U.S. short-term funding markets remained stable"

## 6. Anything else

**VERDICT: AMEND**

Nine of the ten controls are after 5 November. A funding echo that lasts past the Thursday is pulled into the median and pushes the label toward INSIDE. The bills auctioned on the event day settle on a control day, so the baseline is not independent of the event’s Treasury operations. Monday 2 November is also already public under the registration’s own gate: the gate forbids prints dated after 4 November, and g16 says preliminary prints lag two business days, so the Monday 2 November print was due on Wednesday 4 November, before this statement was written on 6 November. Reaching back to earlier months for cleaner controls would use spreads the programme had already computed by 3 November. The series pools collateral and is cut only by tenor, so an equity-financing stress need not appear in it. The registered day is the equity-close day; the next session is excluded from the label and only described. There is no rule that a later revision cannot flip the label. Which of the Thursday’s repo trades printed before the equity move is UNCERTAIN. Trade times against the equity path would settle it.

**Amendment:** Drop 2 November from any rebuilt control because its print predates the statement. State that later control days are not a pre-event baseline. Import g16’s revision rule: one vintage, never rescore. Keep the legs in the registered sentence. Commit that the described bill-only control will not be used to qualify the label after the print arrives.

## SINGLE LOAD-BEARING ASSUMPTION

- The ten dates are exchangeable with 5 November as ordinary draws of this spread, so a label other than INSIDE is a property of the equity sell-off.
