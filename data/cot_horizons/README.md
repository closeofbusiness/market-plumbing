# Do funds' weekly oil positions predict the next week's price move?

We asked whether a change in hedge funds' net position in crude oil futures, as published each Friday by the US futures regulator (the CFTC), is followed by a price move in the week after the report is public. We tested it for US crude (WTI, the benchmark traded on the New York Mercantile Exchange, NYMEX; 731 weeks from 8 September 2009 to 19 March 2024) and for Brent (819 weeks from 11 January 2011 to 15 September 2026), counting only prices that came after each report was released. As built on 18 October 2026, no association was found in either market: the correlation is -0.011 for WTI and +0.030 for Brent, both well inside the range that chance alone produces with this many weeks. The test could have seen a correlation of about 0.10 about four times in five. No lead larger than about 0.083 (WTI) or 0.105 (Brent) was detected at 95%, and a smaller one would not show up. The numbers describe how the series moved together; they do not say that positions moved prices, or that they did not.

*Corrected on 18 October after independent verification: one WTI window (the report of 12 March 2024) was priced on the wrong contract because the contract-expiry calendar stopped one month too early. The WTI correlation moved from -0.01066 to -0.01076 (z from -0.288 to -0.291, p from 0.7731 to 0.7711); the verdict is unchanged. Brent is unaffected.*

*Status: the values are provisional until an independent re-derivation has been recorded in `checks.csv` (see `SOURCES.md`). Grade: MEASURED on the stated samples; "funds lead prices" stays HYPOTHESIS whatever the result.*

## Terms

- **CFTC**: the US Commodity Futures Trading Commission, which publishes the Commitments of Traders reports. **EIA**: the US Energy Information Administration, the source of the price series. **NYMEX**: the New York Mercantile Exchange, where WTI futures trade. **WTI**: West Texas Intermediate, the US crude benchmark; Brent is the North Sea benchmark traded on ICE Futures Europe.
- **Managed money**: the CFTC's and ICE's class for funds that trade on behalf of clients, such as hedge funds and commodity trading advisers.
- **Net position**: contracts held long minus contracts held short, in contracts of 1,000 barrels. Positions are as of Tuesday's close and published the following Friday (a federal or English bank holiday can delay the release).
- **Next-week return**: the percentage price change from the first price after the report is public to the first price after the following week's report is public. A price dated on the release day itself is never used.
- **Placebo standard error**: how much the correlation wanders by chance. We recompute it 2,000 times after giving each week's price move a random plus or minus sign; the larger of that spread and the textbook 1 over the square root of n is used.
- **Holm correction**: two correlations are tested at once, so the smaller p-value must pass 0.025 and only then may the other pass 0.05.

## What this cannot say

- **That funds moved prices, or did not.** The result is a correlation between a change in positions and a later price change.
- **"There is no lead."** A lead below the size the test can see (about 0.08 to 0.10 here) would not show up.
- **Anything about WTI after 5 April 2024.** The free futures price history ends there, so later weeks use the spot price and are described, not tested.
- **WTI weeks before 8 September 2009 as a real-time lead.** Managed-money positions for report dates before 2009-09-01 were first published on 2009-10-20; for those weeks no real-time lead is possible. The 1 September 2009 report was itself public on 4 September, but its weekly change is measured against the 25 August level, which was not public in real time, so the first tested week is 8 September. The earlier weeks appear only in the descriptive rows.
- **Brent at futures quality.** No free Brent futures series exists that scripts may read, so Brent uses the EIA Europe Brent spot price, a weaker proxy (`EIA_Europe_Brent_spot_FOB_proxy_not_futures`). Windows that touch the EIA prints dated 2 to 16 October 2026, which are unexplained, are left out.
- **Anything about levels of positioning, dollar exposure or percent of open interest.** None is tested.
- **The weeks the CFTC could not publish on time.** The two federal shutdown periods (2013, 2018-19) are left out because their release dates are not verified, and so are the weeks delayed more than seven days (the 2023 ION incident and the 2025 shutdown).

## The descriptive rows are not findings

`descriptive.csv` holds 70 rows (other windows, the combined futures-and-options book, 4-week and 13-week horizons, other samples). Each row says `role=descriptive (no verdict)` in its `note`, and `exceeds_own_bar=yes` or `no`. 20 of the 70 exceed their own 95% bar, including the Brent 13-week rows (r = -0.398 and -0.419 on 62 non-overlapping blocks, bar 0.249). With about 70 rows, some exceed their bar by chance. Under the decision rule these rows carry no verdict and are not a lead. The 13-week horizon is also where a searched oil "lead" has failed before. The same-week rows (r about 0.4 to 0.5) are prices and positions moving together within the week, not a lead.

## Files

| File | What it holds |
|---|---|
| `primary.csv` | The two pre-registered correlations, with the placebo-based standard error, the Holm correction and the verdict. |
| `descriptive.csv` | Everything else, with no verdict: other windows, the combined futures-and-options book, 4-week and 13-week horizons, the pooled and 2006-2009 samples, the spot extension, samples without Mar-Jun 2020. |
| `plot26.csv` | 26-week blocks for a plot, with their band. No verdict. |
| `weekly_panel.csv` | One row per report: change in net position, release date used, window dates, spot returns, exclusion reason. |
| `release_dates.csv` | The release date used for every report, the rule that produced it and its source. |
| `roll_calendar.csv` | The expiry date of every WTI contract delivery month, January 2006 to May 2024 (the last two months are there so that the final windows have an expiry to test against). |
| `checks.csv` | Every check, with its expected and observed value and a status (PASS, FAIL, WARN, INFO, PENDING). |
| `fetch_log.csv` | The eight requests made to CFTC, EIA and gov.uk, with time, status, size and checksum. |
| `raw/` | The CFTC rows for both books, the saved CFTC pages and the gov.uk bank-holiday file (all public). |
| `SOURCES.md` | Sources and terms, the rulings applied, the guards, and the open questions. |

Rebuild offline with `python3 bin/cot_horizons.py build`; the selftest is `python3 bin/cot_horizons.py selftest`. The EIA futures workbooks and the weekly futures returns stay local (`data/vintages/cot_horizons/`) and are never committed.
