# Grok batch g7, 18 Oct 2026: spec attacks on the next six builds

Six parcels through orchestrator_cursor (Grok 4.7, 256k, extra-high; fenced to read + web), 14-20 minutes each. All six SUCCESS: no
breaches, nothing blocked, no unexpected tools, Cursor default model restored. Several returns cite download URLs Grok's fetch tool
could not open (listed as not fetched by the wrapper). **Grok's text is input, not result.**

## Supervisor check

- **All six verdicts: BUILD WITH CHANGES.** The changes are mostly inference hygiene: changes not levels, overlap judged on
  non-overlapping counts, one pre-registered primary test per build, release timing, sample choices not cut around the result.
- **Grok's download "FAILS" were its own fetch tool.** The supervisor downloaded each on 18 Oct with the project's neutral
  User-Agent: JODI `primaryyear2026.csv` (HTTP 200, 5.5MB, 134,400 rows, latest month 2026-07; units CONVBBL, KBBL, KBD, KL, KTONS),
  the World Bank `CMO-Historical-Data-Monthly.xlsx` (200, 586KB), the Bank of England `glcnominalddata.zip` (200, 39MB), MoF
  `jgbcme_all.csv` (200, from 1974). Bundesbank's daily 10-year (BBSIS API) is current to 16 Oct 2026, not 3 Aug as Grok said (it
  read a different URL).
- **Overruled:** parcel 1's change 9 (do not script ICE). The principal ruled on that (THE_ASK.md E-025); the Brent ledger stands
  under its conditions.
- **Licences, under existing rules (no new ruling needed):** JODI reserves all rights and asks for acknowledgement; the World Bank's
  gold column has unclear reuse terms; the Bank of England's curves allow personal or internal non-commercial use. In each build the
  raw files stay in a local cache outside the repository and only derived statistics are committed, with the source cited.
- **Next rung:** specs written by Opus authors with the accepted changes and these rulings, then a second review, then builders in
  clones, an independent verifier and a pre-publication audit.

## Grok return 1: Full-sample COT horizons (WTI, Brent)

I'll review the design from the files on disk first, then check the live sources and the literature those tables depend on.The design, the two lead-lag tables, and the Brent ledger notes are in hand. Next I’ll check each named source live and pull the papers that actually ran this test.The source pages are up. I’m checking the actual series, fields, and the two papers’ methods next.**VERDICT: BUILD WITH CHANGES.** It sinks if a Newey-West lag equal to the horizon, and a block bootstrap of that same length, is treated as a valid 5% test of overlapping multi-week leads and of the level of positioning.

The full public WTI book is real and countable. Code `067651` has 1,062 futures-only weeks and 1,062 combined weeks, from 13 June 2006 through 13 October 2026, with no key. The design as written would still not test the claim.

**Overlapping horizons.** The spec’s own power bar treats overlapping weeks as `n/h` independent draws: at 875 weeks that is 0.066, 0.132, 0.24 and 0.34 at 1, 4, 13 and 26 weeks. The estimator then uses Bartlett Newey-West with lag equal to the horizon. With that kernel the weight on lag `h−1` is `2/(h+1)`. At 26 weeks the lag that carries the overlap gets weight about 0.07, so the standard error does not cover the overlap the horizon creates. The printed `nw_se` will clear 5% inside the spec’s own `n/h` bar. The bootstrap stores the 5th and 95th percentiles, a 90% interval. Calling that a 5% test is a 10% test. At horizon 1 the block length is 1, an iid bootstrap. One bandwidth is applied to a weekly change, a slow level, and trailing 1-, 3-, 6- and 12-month returns.

**Levels.** Local projections at 1, 2, 4, 8, 13 and 26 weeks put an h-week price outcome on the left and include the lagged level of net as a percent of open interest. Büyükşahin and Harris find the crude price non-stationary and run Granger tests on price changes. A level-on-level regression of two trending series is the spurious regression. A return on the lagged level is a persistent-regressor regression whose innovation is the same-week position change. In the tables already built, that same-week correlation is +0.376 to +0.660. That regression is biased toward “a large net position predicts the opposite move,” and the tapered standard error will call it a lead.

**Look-ahead and vintage.** The report is released Friday at 3:30 p.m. Eastern and contains the previous Tuesday. The October 2026 Fridays are 2, 9, 16, 23 and 30. A Tuesday-to-Tuesday “next week” return starts at the measurement timestamp and includes Wednesday–Friday before the number is public. That is a post-measurement association. It is not a lead a reader of the report could have used. History back to 13 June 2006 was filled in October 2009 by backcasting later trader classifications. The API is the revised file. The notes say large classification errors are corrected and republished. There is no as-of vintage.

**Multiple testing.** As written, for oil alone: 2 contracts × 2 report types × 6 horizons × 6 regressors = 144 regressions, each with a 5% claim and no Bonferroni, Holm, or false-discovery adjustment. About 7 would clear 5% if nothing were there. The user’s four horizons still leave 96. Gold and copper are in the spec and are not reproducible from a public price. There is no country panel. The multiplicity is benchmarks, report types, horizons, and regressors.

**Sample.** The only correlations already computed are 2 January 2024–13 October 2026, n = 146 and 145, not the spec’s assert of n = 145 and 144 through 6 October. Same-week correlations clear ±0.162. Next-week correlations (−0.084 to +0.015) do not. That window is the one already written up. The design then starts the “full” sample on 5 January 2010 (875 weeks through 6 October 2026) and drops 186 weeks from 13 June 2006. Hamilton and Wu find that the oil predictability people cite is the 2007–2009 recession and breaks afterward. Starting in 2010 deletes that episode from the only sample. Event windows since 26 December 2023 and 30 December 2025 are narrative cuts.

**Denominators.** Futures-only managed-money net on 8 September 2026 is 218,960 − 107,229 = 111,731, and on 6 October is 178,353 − 124,755 = 53,598, a 52% cut. Combined on 6 October is 198,618 − 94,127 = 104,491. The spec’s combined book over those four weeks is a 25% cut, and the twelve-week change flips sign between the two books. Percent of open interest puts open interest in the denominator: futures-only open interest was 1,044,276 on 13 June 2006 and 1,900,179 on 13 October 2026, so a constant fund book shrinks as a share when hedging open interest rises. Dollars (net × 1,000 × price) move with the price even when the position does not. Combined figures are option-adjusted futures equivalents. Spreading is correctly out of the net and still inside open interest. The price in the design is the EIA spot, not the futures curve the position is on. September 2026 monthly spot is $97.31 WTI and $114.16 Brent.

**Horizons and honest bars.** For all 1,062 WTI weeks, a two-sided 5% test that refuses to treat overlap as extra observations sees a correlation only if it exceeds `1.96/√floor(1062/h)`:

| Horizon | Independent windows | Minimum detectable \|r\| | \|r\| with about 80% power |
|---|---:|---:|---:|
| 1 week | 1,062 | 0.060 | 0.086 |
| 4 weeks | 265 | 0.120 | 0.172 |
| 13 weeks | 81 | 0.218 | 0.311 |
| 26 weeks | 40 | 0.310 | 0.443 |

If weekly innovations are white noise and only the mechanical overlap is corrected, the bars fall to about 0.100, 0.178 and 0.254 at 4, 13 and 26 weeks. That is the optimistic bound. Serial correlation in position changes, and a large same-week correlation, push the lead’s standard error back up. Twenty-six weeks is not worth running as a test. A true correlation of 0.15 has a z-statistic of about 0.95 on 40 windows. A miss is the expected result. A hit is a handful of oil cycles. Thirteen weeks is the same kind of result, and it is the horizon at which a searched window has already produced a published oil “lead” that did not survive the next two years.

## REQUIRED CHANGES

1. Pre-register one correlation: WTI futures-only, weekly change in managed-money net contracts, against the next week’s percent futures return, on all 1,062 weeks.
   The written grid is 144 tests, and the only result in hand is the 2024–26 same-week correlation. https://www.cftc.gov/sites/default/files/idc/groups/public/@swaps/documents/file/plstudy_19_cftc.pdf

2. Use position changes and price changes. Leave the level of net, and the level of price, out of the decision test.
   The crude price is non-stationary, and the same-week change correlation is already +0.38 to +0.66, which is what biases a regression on the lagged level. https://www.cftc.gov/sites/default/files/idc/groups/public/@swaps/documents/file/plstudy_19_cftc.pdf

3. For 4, 13 and 26 weeks, keep the one-week return on the left, or use non-overlapping blocks, and judge them with `1.96/√floor(T/h)`, not with Newey-West lag = horizon and not with the 5th–95th bootstrap percentiles.
   Bartlett tapering does not cover the overlap, and those percentiles are a 90% interval. Hamilton and Wu left the weekly futures return on the left even when the position change was 13 weeks long. https://www.nber.org/system/files/working_papers/w19892/w19892.pdf

4. Do not use 26 weeks as a test. A plot with the 0.310 band is optional.
   Forty windows detect a correlation of about 0.44 with 80% power, so a miss is uninformative and a hit is a few cycles. https://www.nber.org/system/files/working_papers/w19892/w19892.pdf

5. Date the return from after Friday 3:30 p.m. Eastern if the sentence is about the public report. Label a Tuesday-to-Tuesday return as post-measurement.
   The release is Friday at 3:30 p.m. Eastern and contains the previous Tuesday. https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm

6. Run the decision sample from 13 June 2006 through the latest Tuesday, and show 2006–2009 only as a pre-registered split, not by deleting it.
   Those weeks are the backcast classifications, and they are the recession window that produced the oil result which then broke. https://www.cftc.gov/MarketReports/CommitmentsofTraders/DisaggregatedExplanatoryNotes/index.htm and https://www.nber.org/system/files/working_papers/w19892/w19892.pdf

7. Decide on net contracts, and report futures-only and combined as two books.
   The same September–October 2026 cut is 52% in futures-only and 25% in the combined book in the design, and percent of open interest mixes the 2006 open interest of 1,044,276 with the October 2026 open interest of 1,900,179. https://publicreporting.cftc.gov/resource/72hh-3qpy.json?cftc_contract_market_code=067651&$select=count(report_date_as_yyyy_mm_dd)

8. Price the test with the futures contract the position is in. Keep the EIA spot out of the decision correlation.
   September 2026 monthly spot is $97.31 Cushing WTI and $114.16 Brent, and the named daily workbooks return HTTP 500. https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=RWTC&f=M and https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=RBRTE&f=M

9. Do not script the ICE files and do not commit a Brent ledger that rebuilds the book. A hand download, if someone accepts the personal licence, is a replication with its own bar, not a second 5% draw.
   The licence is personal and non-commercial and “does not include use of any data mining, robots,” and it bars systematic retrieval into a database. https://www.ice.com/privacy-security-center/terms-of-use

## SOURCES

- CFTC futures-only disaggregated API, https://publicreporting.cftc.gov/resource/72hh-3qpy.json?cftc_contract_market_code=067651&$select=count(report_date_as_yyyy_mm_dd) — WORKS — public domain, no key; code 067651; 1,062 weeks; fields `m_money_positions_long_all` and `m_money_positions_short_all`; name is “CRUDE OIL, LIGHT SWEET” on 13 June 2006 and “WTI-PHYSICAL” from 8 February 2022.
- CFTC combined API, https://publicreporting.cftc.gov/resource/kh3c-gbw2.json?cftc_contract_market_code=067651&$select=count(report_date_as_yyyy_mm_dd) — WORKS — same public-domain terms; 1,062 weeks; 6 October 2026 combined net 104,491.
- CFTC web policy, https://www.cftc.gov/WebPolicy/index.htm — WORKS — “Government information at the CFTC website is in the public domain.”
- CFTC disaggregated notes, https://www.cftc.gov/MarketReports/CommitmentsofTraders/DisaggregatedExplanatoryNotes/index.htm — WORKS — history from 13 June 2006 is backcast; corrections are republished.
- CFTC release schedule, https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm — WORKS — Friday 3:30 p.m. Eastern, previous Tuesday.
- EIA copyright, https://www.eia.gov/about/copyrights_reuse.php — WORKS — public domain; redistribution allowed with a dated acknowledgement.
- EIA Cushing WTI monthly page, https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=RWTC&f=M — WORKS — series RWTC, free, no login; September 2026 = 97.31; October blank on the 15 October 2026 release.
- EIA Brent monthly page, https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=RBRTE&f=M — WORKS — series RBRTE; September 2026 = 114.16; October blank.
- EIA daily workbook named in the design, https://www.eia.gov/dnav/pet/hist_xls/RWTCd.xls — FAILS — HTTP 500. The Brent twin https://www.eia.gov/dnav/pet/hist_xls/RBRTEd.xls also returned HTTP 500. The HTML series pages are the live free source.
- ICE COT index, https://www.ice.com/cot-report-links — WORKS — no login; yearly CSV links for 2011 through 2026.
- ICE 2026 history file, https://www.ice.com/publicdocs/futures/COTHist2026.csv — CHANGED — no login and the columns match (`CFTC_Commodity_Code` B, `FutOnly_or_Combined`, `M_Money_Positions_Long_All`, `M_Money_Positions_Short_All`, 1,000 barrels); 31 March 2026 Brent combined net is 429,853 and futures-only net is 382,072; terms forbid the scripted database the build wants. Rows after 31 March were past the returned slice.
- ICE terms, https://www.ice.com/privacy-security-center/terms-of-use — WORKS as a terms page — personal non-commercial use; no robots; no derivative database.

## LITERATURE

- Büyükşahin and Harris, “The Role of Speculators in the Crude Oil Futures Market,” CFTC working paper (SSRN 1435042; later Energy Journal, 2011). Fetched https://www.cftc.gov/sites/default/files/idc/groups/public/@swaps/documents/file/plstudy_19_cftc.pdf. They use confidential daily large-trader positions and NYMEX futures prices, Granger-test price changes against position changes at 1–5 day intervals, and find the lead runs from price to positions. Quote: “price changes do precede their position changes.”
- Hamilton and Wu, “Effects of Index-Fund Investing on Commodity Futures Prices,” NBER Working Paper 19892, February 2014. Fetched https://www.nber.org/system/files/working_papers/w19892/w19892.pdf. The left-hand side is the weekly near-futures return; the 13-week object is a change in notional on the right; the oil fit is the recession and dies out of sample, and the same imputed holdings also fit the S&P 500 over that window. Quote: “driven by some of the dramatic features of the 2007-2009 recession.”

## DECISION RULE

Descriptive association only. A coefficient is not a statement that funds moved the price.

**Supports.** On all 1,062 WTI futures-only weeks, the correlation between the weekly change in managed-money net contracts and the following week’s percent futures return has absolute value at least 0.060, and that absolute value is larger than the reverse correlation (the previous week’s return with this week’s position change). The combined book, same definition, has the same sign and absolute value at least 0.060. Horizons 4, 13 and 26 are not required.

**Against.** The forward one-week absolute correlation is below 0.060, or the reverse absolute correlation is larger and itself at least 0.060. A four-week forward absolute correlation below 0.120 counts against a multi-week lead. The 2024–26 same-week correlations of 0.376, 0.410, 0.580 and 0.660 do not support a lead.

**Inconclusive.** A result that appears only at 13 weeks (bar 0.218) or 26 weeks (bar 0.310); only in the level or in percent of open interest; only in 2010–2026 or in 2024–26; only in one report type; or only in Brent. A 26-week correlation that clears 0.310 is still inconclusive: 80% power at that horizon needs about 0.44, and there are 40 windows.

## SUCCESS CRITERIA

- The count query above returns 1,062 for futures-only and 1,062 for combined, code `067651`.
- Futures-only 8 September 2026: long 218,960, short 107,229, net 111,731, open interest 1,939,911. Futures-only 6 October 2026: long 178,353, short 124,755, net 53,598, open interest 1,889,422.
- Combined 6 October 2026: long 198,618, short 94,127, net 104,491, open interest 2,533,937.
- Before any coefficient is read, the builder prints the bars 0.060 (n = 1,062), 0.120 (n = 265), 0.218 (n = 81) and 0.310 (n = 40), using `1.96/√floor(1062/h)`.
- The decision correlation uses the 1,062-week futures-only change in net contracts. It is marked only if its absolute value is at least 0.060 and larger than the reverse correlation on the same rows.
- Rebuilding the 2024 window through 13 October 2026 reproduces the file in this folder: WTI futures-only same-week Pearson 0.376 (n = 146), next-week −0.084 (n = 145), band 0.162. The spec’s assert of n = 145 and 144 is already one week behind that file.
- Brent, if computed at all, is not in the decision. The 31 March 2026 check is combined net 470,101 − 40,248 = 429,853 and futures-only 432,381 − 50,309 = 382,072, from the 2026 CSV.
- No public output contains a gold or copper price.

## UNCERTAIN

- The 2026 ICE file’s weeks after 31 March 2026 were past the returned slice. Whether 30 June, 8 September and 6 October 2026 are in it now would be settled by reading those dates in `COTHist2026.csv`.
- The 2011 double-underscore header was not re-read. The 2026 header uses a single underscore, `Swap_Positions_Short_All`.
- Daily EIA prints after 1 October 2026, including the flagged Brent levels and the 8 September WTI price of $94.21, were not re-read. Both named `.xls` URLs returned HTTP 500, and the October 2026 monthly cells are blank on the 15 October release. A later daily page, or a workbook that actually downloads, would settle the spot gap.
- Brent’s week count was not counted from ICE. The index starts at 2011. The WTI count of 1,062 was fetched. Matching 1,062 to every Tuesday from 13 June 2006 through 13 October 2026 is calendar arithmetic; a date list would confirm there is no holiday gap inside that count.
- Filtering on the string “WTI-PHYSICAL” would start on 8 February 2022. The code, not the name, is what makes the 1,062 weeks one series.
- The sign of the bias on the lagged level is inferred from the positive same-week correlations in the two CSVs, not from a fitted full-sample coefficient.
- Whether a committed aggregate ICE ledger is lawful is a reading of the terms page, not a determination ICE has published on the COT files.

## Grok return 2: Yen and euro against rate gaps

I'll review the FX design as written, then check each data source and the matching literature on the live web before writing a decision rule.The spec is a weekly change regression on two yield gaps across three windows, with standard errors and a cumulative residual left undefined. I’ll fetch each named source and the papers that actually run this test.The yen print matches the spec, and the euro yield is an AAA continuous spot, not a par yield. Next I’ll check the Treasury and Ministry of Finance files, the release lag, and the papers that run this regression.VERDICT: BUILD WITH CHANGES — it sinks if a same-week Treasury-par minus foreign-yield gap, summed inside windows chosen after the path was known, is treated as the rate differential that accounts for the spot move.

Built as written, the regression can print coefficients and still be the wrong object. The horizon is one non-overlapping week, so overlapping-window standard errors are not the fix, and the standard-error columns name no estimator. The three windows do not overlap. W1 is week-ending Fridays from 2018-01-05 through 2021-12-31, W2 from 2022-01-07 through 2023-12-29, W3 from 2024-01-05 through 2026-09-18. Hansen-Hodrick order k−1 is 0 at a one-week horizon. A long-horizon Newey-West or a Valkanov 1/√m rescaling belongs to a different regression and would distort this one. What the file actually leaves blank is heteroskedasticity: intervention weeks and policy weeks are outliers, and ordinary least squares standard errors ignore that.

The cumulative residual is not a test of an unexplained move. With an intercept, residuals sum to zero, so the window-end cumulative residual is zero. Without an intercept, that endpoint mixes drift into the slopes. The memo already sets no residual-share cutoff, so the headline result has no pass mark.

The euro gap subtracts an ECB AAA continuous Svensson spot from a Treasury semiannual par yield. The ECB technical notes say Friday’s curve is fit to the previous business day’s prices, compounded continuously, and that a par curve is a separate object. Treasury’s par yields are bond-equivalent yields from quotes near 3:30 pm New York, usually posted by 6:00 pm. BIS recent daily rates follow the ECB 13:15 GMT fix or the Fed 17:00 GMT rate, and an increase is a depreciation against the dollar. MoF constant-maturity yields are the 3:00 pm Tokyo semiannual compound rate, released at 9:30 the next business day. Same-calendar-Friday changes are not the same information set.

There are 2 pairs × 3 windows × 2 slopes = 12 slope tests, plus event weeks, plus an uncoded policy-rate family. The 14 Oct 2026 write-up already uses data through 18 Sep 2026 and already reports that the 2024 stretch and the 2025 stretch have different gap and FX signs. W3 is that episode. W3 also contains the 19 March 2024 end of yield-curve control and the 2026 intervention block. The 10-year JGB is not one market gap across 2018–2026.

Levels of the spot on levels of the gap would be a unit-root regression. Weekly log changes are the regression to run. The cumulative path is an accounting sum of those changes, not a second levels regression.

## REQUIRED CHANGES

1. Estimate weekly log-spot changes on weekly gap changes with an intercept, and define the rate contribution as the sum of the fitted slope terms only. The window-end cumulative residual is zero once a constant is included, and the spot level is a unit-root series that has to be differenced. https://faculty.washington.edu/yuchin/Papers/CT1v3.pdf

2. Use heteroskedasticity-robust (HC3) standard errors as the primary estimator, set the Hansen-Hodrick lag to 0, and run Newey-West with lag 4 only as a check. Overlapping multi-month returns are an MA(k−1) problem; this file’s horizon is one week, and Newey-West on persistent overlapping regressions over-rejects. https://www.nber.org/system/files/working_papers/w11077/w11077.pdf

3. Declare one primary test, the post-21 March 2024 yen slope, at 5 percent. Treat the two pairs, three windows, and event weeks as description. If all 12 slopes are tested as confirmatory, the cutoff is 0.05/12 = 0.00417. Short windows move R² around, and these windows were dated after the path was already tabulated. https://www.nber.org/system/files/working_papers/w26046/w26046.pdf

4. Quote both pairs as foreign currency per dollar, and keep the gap as the US yield minus the foreign yield. On the BIS scale an increase is a depreciation against the dollar, so the design’s dollars-per-euro log change has the opposite dollar sign from yen per dollar. https://data.bis.org/topics/XRU

5. Build the euro gap from nominal par yields on a semiannual bond-equivalent basis, or convert both legs to continuous zeros before subtracting. The series `SR_2Y` and `SR_10Y` are AAA continuous spots, the price input is the previous close, and Treasury does not publish a daily zero curve. https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_area_yield_curves/shared/pdf/technical_notes.pdf

6. For the yen, regress the change in the nominal slope gap, (US 10-year − Japan 10-year) − (US 2-year − Japan 2-year), on the sample of week-ends after 21 March 2024, and run the 2-year gap change only as a separate regression. Yield-curve control is the framework the Bank of Japan said had ended on 19 March 2024, with the short rate as the policy tool and JGB buying continued; the fetched yen result that is about the curve is the relative slope, not two raw maturity gaps. https://www.boj.or.jp/en/mopo/mpmdeci/state_2024/k240319a.htm

7. Leave official intervention amounts off the right-hand side. Drop every week that intersects a non-zero official operation, using the full monthly list from 1991 through 2026, and drop the whole 30 Jul–26 Aug 2026 block because it has no day split. The 27 Aug–28 Sep 2026 total is ¥0, so those weeks stay in. Report the slope with the dropped weeks restored; do not write that the flow caused the price. https://www.mof.go.jp/english/policy/international_policy/reference/feio/monthly/index.html

8. Publish the full-sample 2018-01-05 through 2026-09-18 descriptive regression next to any window split. The 6 Dec 2021 Treasury curve-method change shifts constant-maturity rates by tenths of a basis point and does not justify a new window; the peeked 2024–26 split does. https://home.treasury.gov/policy-issues/financing-the-government/yield-curve-methodology-change-information-sheet

## SOURCES

- BIS yen `D.JP.JPY.A`, https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/D.JP.JPY.A?startPeriod=2026-09-18&endPeriod=2026-09-18&format=csv — WORKS — free, no key; 2026-09-18 = 157.888307; title says daily average; cite BIS.
- BIS euro `D.XM.EUR.A`, https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/D.XM.EUR.A?startPeriod=2026-09-18&endPeriod=2026-09-18&format=csv — WORKS — same terms; 2026-09-18 = 0.8726 euro per dollar.
- BIS yen 2023-12-29 and 2026-07-28/30, same API with those dates — WORKS — 141.475113, 163.913082, 162.940049.
- BIS end-of-period key `D.JP.JPY.E`, same host — FAILS — HTTP 404.
- BIS terms, https://data.bis.org/help/legal — WORKS — unrestricted if BIS is cited; API is as-is and may be throttled; no extra charge to users.
- BIS exchange-rate notes, https://data.bis.org/topics/XRU — WORKS — dollar value of one USD; ECB 13:15 GMT and Fed 17:00 GMT; weekly release.
- Treasury 2026 par CSV, https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_yield_curve&field_tdr_date_value=2026&page&_format=csv — WORKS — no login; headers `2 Yr` and `10 Yr`; 2026-09-18 is 4.76 and 5.01; 2026-09-24 is 4.87 and 5.18.
- Treasury methodology, https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/treasury-yield-curve-methodology — WORKS — par curve from quotes near 3:30 pm; monotone convex since 6 Dec 2021; usually posted by 6:00 pm.
- Treasury FAQ, https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/interest-rates-frequently-asked-questions — WORKS — semiannual bond-equivalent yields; Treasury does not publish a daily zero curve.
- Treasury archives, https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rate-archives — WORKS — public par-yield CSV and XML feeds. License page not obtained.
- Data.gov catalog for this dataset — FAILS — page timed out twice, so CC0 is not confirmed.
- MoF `jgbcme_all.csv`, https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv — WORKS — no login; row 2 headers include `2Y` and `10Y`; unit percent; missing as `-`. The body returned here starts in 1974 and does not show 2023–26.
- MoF directory, https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/ — WORKS — file present, 1.1M, dated 2026-10-02.
- MoF yield definition, https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/qa.htm — WORKS — semiannual compound constant maturity at 3:00 pm; released 9:30 the next business day.
- MoF copyright notice, https://www.mof.go.jp/english/about_mof/notice/index.html — WORKS — PDL 1.0 unless other rights are indicated.
- Japan PDL 1.0, https://www.digital.go.jp/en/resources/open_data/public_data_license_v1.0 — WORKS — free copying, commercial use allowed; numerical data are outside the licence; content may change without notice.
- MoF intervention Q2 2026, https://www.mof.go.jp/english/policy/international_policy/reference/feio/quarter/2026_2Qe.html — WORKS — released 7 Aug 2026; 30 Apr ¥6,278.7bn, 4 May ¥780.2bn, 6 May ¥4,675.9bn; page total ¥11,734.9bn.
- MoF intervention 30 Jul–26 Aug 2026, https://www.mof.go.jp/english/policy/international_policy/reference/feio/monthly/20260828e.html — WORKS — released 28 Aug 2026; ¥15,399.3bn; no days.
- MoF intervention 27 Aug–28 Sep 2026, https://www.mof.go.jp/english/policy/international_policy/reference/feio/monthly/20260930e.html — WORKS — released 30 Sep 2026; total ¥0. Absent from the written input list.
- MoF monthly index, https://www.mof.go.jp/english/policy/international_policy/reference/feio/monthly/index.html — CHANGED — monthly windows from 2023 through Sep 2026 are listed, plus “April 1991–June 2026” historical data. The design treated pre-2026 daily history as unavailable.
- ECB yield API, https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y+SR_2Y?startPeriod=2026-09-18&endPeriod=2026-09-18&format=csvdata — WORKS — no key; 2026-09-18 `SR_2Y` 3.2152124072 and `SR_10Y` 3.529753074; 2023-12-29 is 2.4363455063 and 2.0808856999.
- ECB reuse policy, https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html — WORKS — free reuse if “Source: ECB statistics” is cited and the published statistics are not modified; series can be revised.
- ECB yield-curve notes, https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_area_yield_curves/shared/pdf/technical_notes.pdf — WORKS — continuous compounding; previous-business-day prices; AAA and all-issuer curves; a par curve is also derived.
- Fed, BoJ, and ECB policy-rate codes — FAILS — the design names no series and rules out FRED, so that leg has no fetchable field.

## LITERATURE

- Lilley, Maggiori, Neiman, and Schreger, NBER w26046 (July 2019, revised December 2019), https://www.nber.org/system/files/working_papers/w26046/w26046.pdf — Quarterly log change in an equal-weighted G10 dollar basket on a constant and the lagged level of a 3-month nominal deposit or Treasury-bill differential. Pre-crisis fit is about 5 percent. Standard errors allow for heteroskedasticity. The yen’s risk comovement is muted. Bond flows are not treated as the cause. Quote: “interest differential explaining only 5 percent of the variation.”

- Chinn and Meredith, NBER w11077 (January 2005), https://www.nber.org/system/files/working_papers/w11077/w11077.pdf — Future exchange-rate change over the maturity on the level of a nominal differential. Yen evidence in this file is 3-, 6-, and 12-month eurocurrency rates. The long-horizon government-bond results shown are 5-year constant-maturity yields for Germany, the UK, and Canada. Overlapping horizons use Hansen-Hodrick GMM with MA order k−1. Quote: “moving average serial correlation of order k-1.”

- Chen and Tsang (June 2011), https://faculty.washington.edu/yuchin/Papers/CT1v3.pdf — Monthly forecasts of future dollar-per-foreign log changes from Nelson-Siegel level, slope, and curvature of nominal continuous zero-coupon curves, 3 months to 10 years, for Canada, Japan, and the UK. For the yen, the relative slope is the factor with a significant role. They difference the spot. For overlapping horizons they discard plain Newey-West and rescale the t statistic by 1/√m. Quote: “the Newey-West adjustment suffers from serious size distortion.”

## DECISION RULE

Run this before any sentence about the yen. Sample P is week-ends after 2024-03-22 through 2026-09-18, excluding weeks that intersect a non-zero official intervention day or an undated non-zero block. Quote yen per dollar. Gap is nominal and same-convention. Primary equation is Δln_t = α + β_s Δslope_t + e_t, with slope = (US 10-year − Japan 10-year) − (US 2-year − Japan 2-year), in percentage points. A second equation replaces Δslope with the 2-year gap change. S is the sum of Δln over P. F is the sum of β_s Δslope, intercept excluded. φ = F/S. Treat S as the realized cumulative move. The 95 percent interval for φ is the HC3 interval for β_s multiplied by (sum of Δslope) / S. Primary test: HC3 test of β_s = 0 at 5 percent. Newey-West lag 4 must give the same 5 percent call.

- Supports the idea: the HC3 test does not reject β_s = 0 at 5 percent, |φ| < 0.25, the 95 percent interval for φ lies entirely below 0.50, and the 2-year-only regression meets the same |φ| < 0.25 and interval test.
- Against the idea: the HC3 test rejects β_s = 0 at 5 percent, β_s > 0, φ > 0.50, the 95 percent interval for φ lies entirely above 0.25, and those four statements remain true when the dropped intervention weeks are put back.
- Inconclusive: |S| ≤ 0.01, or the interval for φ contains both 0.25 and 0.50, or HC3 and Newey-West lag 4 disagree on the 5 percent call, or restoring intervention weeks moves φ by 0.25 or more or flips the 5 percent call, or the sign-aligned euro regression on a same-convention nominal gap reaches the other verdict.

A lag, a lead, or an intervention amount is a description. It is not a cause. The 0.25 and 0.50 share marks and the lag of 4 are pre-commitments of this rule, not estimates from the papers.

## SUCCESS CRITERIA

1. `D.JP.JPY.A` equals 141.475113 on 2023-12-29, 157.888307 on 2026-09-18, 163.913082 on 2026-07-28, and 162.940049 on 2026-07-30, from the BIS CSV URL with those `startPeriod` and `endPeriod` values.
2. `D.XM.EUR.A` equals 0.8726 on 2026-09-18. The log change of dollars per euro equals the negative of the log change of euros per dollar within 1e-12.
3. The 2026 Treasury CSV has `2 Yr` 4.76 and `10 Yr` 5.01 on 2026-09-18, and `2 Yr` 4.87 and `10 Yr` 5.18 on 2026-09-24.
4. ECB `SR_2Y` and `SR_10Y` equal 2.4363455063 and 2.0808856999 on 2023-12-29, and 3.2152124072 and 3.529753074 on 2026-09-18. The output labels them AAA continuous spots.
5. MoF Q2 2026 days are 2026-04-30, 2026-05-04, and 2026-05-06 at 6278.7, 780.2, and 4675.9 billion yen. The page total is 11734.9 and the day sum is 11734.8. The 30 Jul–26 Aug 2026 total is 15399.3 with no days. The 27 Aug–28 Sep 2026 total is 0.
6. No regressor is a lead. With an intercept, the sum of residuals in each fitted sample is 0 within 1e-8.
7. The printed Hansen-Hodrick lag is 0. Primary standard errors are labeled HC3. The check is labeled Newey-West lag 4. The output prints n, the HC3 p-value for β_s = 0, φ, and the φ interval for sample P, then applies the decision rule above.
8. MoF `2Y` and `10Y` on 2023-12-29 and 2026-09-24 are read from `jgbcme_all.csv`. The design’s 0.048, 0.647, 1.912, and 3.073 pass only if they match that file to three decimals.
9. A request for `D.JP.JPY.E` returns 404 and is not replaced with a made-up key.
10. The builder confirms whether 163.913082 is the maximum of `D.JP.JPY.A` from 2026-01-02 through 2026-09-18. This review did not download that full span.

## UNCERTAIN

- The 2023–26 MoF rows were not in the truncated CSV, so 0.048, 0.647, 1.912, and 3.073 are unchecked. Reading those two dates in `jgbcme_all.csv` settles it.
- Whether 163.913082 is the maximum through 18 Sep 2026 is unchecked. The full 2026 BIS pull settles it.
- Treasury on 2023-12-29 was not in the file fetched here. The 2023 CSV settles the design’s 4.23 and 3.88.
- The BIS row is titled “Average of observations through period,” while the dataset note describes 13:15 GMT and 17:00 GMT fixings. Which fix is inside `D.JP.JPY.A` for 2026 is not on the row. The BIS source-by-currency note would settle it.
- Treasury reuse terms: the data.gov catalog timed out. The CSV and XML feeds are public. CC0 is not confirmed.
- MoF yields use JSDA reference prices. PDL 1.0 puts numerical data outside copyright and warns that third-party rights can remain. A JSDA terms page was not fetched.
- ECB policy says published statistics are not modified and may be revised. The API returned the series with no key. Whether a full-history script would be throttled under the “other users” clause is not stated.
- Monthly intervention pages other than the three 2026 releases were not opened. The index lists them, and the historical-file URL was not in the extracted text. Opening “April 1991–June 2026” settles which weeks to drop.
- Policy-rate gaps have no named series.
- The 0.25 / 0.50 share rule, the variance-inflation cutoff of 10 if both raw gaps are still estimated, and Newey-West lag 4 are pre-commitments, not figures from the fetched papers.
- How often Bank of Japan JGB purchases capped the 10-year yield after 21 March 2024 was not fetched. The operation schedules would settle whether the post-exit 10-year gap is a market rate.

Changes, not levels. The fetched tests use nominal yields: 3-month deposit or bill rates for the G10 basket, 5-year nominal government yields for the Deutschemark, sterling, and the Canadian dollar, and the slope of a nominal continuous zero curve for the yen. None of those yen or euro regressions uses a real yield, a 2-year gap and a 10-year gap together, or the ECB AAA continuous spot. For USD/JPY the slope of the nominal curve is the object the Japan table supports, and only after yield-curve control. For EUR/USD the matched objects are a short nominal rate or a 5-year nominal government par yield. On intervention weeks, drop the week from the slope regression when the official amount is positive or the days are unpublished, keep the week when the official total is zero, and leave the yen amount out of the regression.

## Grok return 3: Gold against real yields, break date

I'll review the gold regression design as written, then check each data source and the matching literature on the live web before deciding whether it should be built.The spec is a levels regression of log gold on the 10-year real yield, with Newey–West errors, a Quandt–Andrews break date, and a post-2021 residual. I’ll fetch each source it names and the papers that actually ran this test.The design’s named predecessor treats the gold–real-yield link as a fragile correlation, and a later paper splits a level break from the daily slope. I’ll fetch those papers and the live data pages before judging the spec.The literature split is already sharp: Erb and Harvey treat the levels correlation as fragile, and Torul puts Newey–West on daily changes and dates the level break separately. Next I’ll confirm the live files, licenses, and the break-date interval method.VERDICT: BUILD WITH CHANGES — the long-sample result is interpretable only if log gold and the 10-year real yield are cointegrated or weakly dependent; if they are persistent and not cointegrated, the HAC interval, the break date, and the post-2021 residual are spurious.

The monthly regression itself does not use overlapping returns. Each month is one average. The written standard errors are still the wrong precision statement. The lag is `floor(4*(n/100)^(2/9))`, a Bartlett Newey–West lag that depends only on sample size. At about 249 months that lag is 4. At the 9-month 2026 window it is 2. The spec already says the 2026 residuals come in blocks, so the classical interval (−33% to −7%) is the wrong precision statement. A 2-lag or 4-lag HAC does not repair that, and it does not repair a levels regression whose residuals behave like a near unit root. The 36-month bands are the overlapping object: about 214 windows, each sharing 35 months with the next, with a percentile bootstrap whose block length is never stated. Counting how many of those intervals exclude zero is hundreds of correlated tests.

The post-2021 file is a same-month residual, not a forecast. September’s gold average and September’s yield average are published together (Pink Sheet dated 2 Oct 2026; H.10 dated 1 Oct 2026). Treasury says the pre-6 Dec 2021 prints stay official, so the yield history is a splice, not a rewrite. December 2021, the imposed estimation end, is the month of that splice, so the month-average mixes pre-spline and post-spline days. The October 2026 H.10 page is one vintage of the whole dollar history; whether pre-2022 dollar levels were revised is not stated on that page.

Log gold and the real yield are the kind of persistent levels that produce a spurious regression. The design’s own seven-quarter levels fit already has R² 0.0005 while gold went from $2,863 to $4,268 and the real yield went from about 2.07% to 2.46%. There is no unit-root test, no cointegration test, no time trend, and no error-correction term. A short HAC lag does not supply those.

The test count, if every stored column is estimated, is levels and changes, with and without the dollar, month-average and month-end yield, the 2026 window, the seven-quarter window, the pre-2022 fit, the full sample, about 214 rolling windows, and about 174 break dates at a 15% trim, times however many trims are written into `trim`. One country, the United States. No Bonferroni, Holm, or Romano–Wolf correction is specified. The sup-F critical value pays for the date search only when Andrews/Hansen critical values are used. The spec never names those critical values. It defines `ci_low`/`ci_high` as “the dates not rejected at 5%.”

The sample is already chosen around the result. January 2006 is the dollar index’s start, which drops 2003–2005 and pushes the 1 Dec 2008 TIPS knot outside a 15% trim. December 2021 is the split written down after this same document had already measured the post-2021 rise. The nine-month 2026 levels slope is the window in which sensitivity was said to have “come back.” On a sample of 249 months (January 2006–September 2026), a 15% trim searches only from about February 2009 through July 2023. A 25% trim searches only from about March 2011 through June 2021. A 5% trim still ends in August 2025. A break in 2026 cannot be the estimated date under any of those trims. That part of the hypothesis is untestable as a break date.

Denominators: the yield is in percent, so 2.88 means 2.88 percentage points, and the stored beta −0.202 is log points per percentage point. Calling it −20.2% uses the log approximation; `100*(exp(−0.202)−1)` is about −18.3%. Gold is an average of daily rates; the yield is a business-day mean. Quarterly gold on the Pink Sheet is an equal-weight average of three months; the hand quarterly yield is day-weighted. The dollar coefficient in logs is an elasticity. Official tonnes stay out of the price regression in the spec, which is the right call: the Aug 2026 minus Dec 2025 reporter stock is 36,516.811 − 36,180.150 = 336.661 t, and the Sep 2026 ledger row is provisional with 16 of 142 reporters fresh. A stock change is not a cause of the price.

## REQUIRED CHANGES

1. Do not run the 2006–2021 half until `CMO-Historical-Data-Monthly.xlsx` returns a body with a gold row. The URL still returns HTTP 500, so the long gold sample cannot be built. https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx

2. Make the one confirmatory slope monthly Δ log gold on Δ real yield and Δ log dollar, and print a levels slope only if an Engle–Granger test rejects no-cointegration at 5%. Torul refuses a levels regression of persistent series when cointegration fails, and Erb finds a time trend fits the US chart better than the real yield. https://web.bogazici.edu.tr/torul/gold.pdf

3. Set the Bartlett Newey–West lag to at least 12 on the monthly sample and print `floor(4*(n/100)^(2/9))` beside it. That rule equals 4 at n≈249, and Torul applies Newey–West (1987) to daily changes, where the change beta is −7.8% per percentage point. https://web.bogazici.edu.tr/torul/gold.pdf

4. Keep the 36-month bands as a plot: state the block length, and do not count windows whose interval excludes zero. About 214 windows overlap by 35 months, and serially correlated errors make the classical interval the wrong precision statement. https://cacoleman16.github.io/tsecon/reference/model-cards/structural-breaks/

5. Store Bai (1997) 95% bounds in `ci_low`/`ci_high`, and use Andrews sup-F with Hansen p-values on the differenced regression. Chow belongs at the known dates 2008-12-01 and 2021-12-06; Bai–Perron belongs only if more than one break is allowed. The spec’s “dates not rejected at 5%” is a pointwise rejection set, and the fixed-date chi-square is the wrong reference for a searched date. https://cacoleman16.github.io/tsecon/reference/model-cards/structural-breaks/

6. Write the break month at trims 0.05, 0.15, and 0.25. At T=249, 15% trim hides December 2008 and everything after about July 2023, 25% trim hides all of 2022, and even 5% trim ends in August 2025, so 2026 cannot be the estimated break. https://cacoleman16.github.io/tsecon/reference/model-cards/structural-breaks/

7. Label the post-2021 path a same-month residual, and add a dummy for months from December 2021 before dating a break. Treasury switched to the monotone convex spline on 12/6/2021 and kept the earlier prints official, so December 2021’s average mixes the two methods. https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_real_yield_curve&field_tdr_date_value=2026

8. Treat the 2026 n=9 levels slope, the seven-quarter levels slope, and the rolling bands as checksums or plots. Erb’s longer UK sample cuts the same correlation from −0.82 to −0.31, which is what a second window is for. https://www.nber.org/system/files/working_papers/w18706/w18706.pdf

9. Leave `official_change_cf_t` out of the price regression. The project rule is that stocks and flows are not the cause of a price; Torul also finds the official flow too small to account for the post-2021 price gap. https://web.bogazici.edu.tr/torul/gold.pdf

10. Do not republish the Pink Sheet gold column as a derived public file until derivative-use consent is confirmed. Remainder terms allow non-commercial use and require prior written consent for a derivative or commercial use. https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets

## SOURCES

- Treasury 2026 real yield CSV, https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_real_yield_curve&field_tdr_date_value=2026&page&_format=csv, WORKS, no key; columns include `10 YR`; 2026-10-13 = 2.88, 2026-09-30 = 2.93; no licence line on the page.
- Treasury 2026 rate page, https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_real_yield_curve&field_tdr_date_value=2026, WORKS, free; R-CMT percent; spline break 2021-12-06 and TIPS knot break 2008-12-01, earlier prints kept official.
- Treasury 2003–2023 archive CSV, https://home.treasury.gov/system/files/276/par-real-yield-curve-rates-2003-2023.csv, WORKS, no key; columns `Date,5 YR,7 YR,10 YR,20 YR,30 YR`; 2023-12-29 `10 YR` = 1.72; no licence line.
- Treasury archives index, https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rate-archives, WORKS, free; lists `par-real-yield-curve-rates-2003-2023.csv`.
- FRED DFII10 text, https://fred.stlouisfed.org/data/DFII10.txt, WORKS, no key; series DFII10, percent, 2003-01-02 through 2026-10-15; 2026-10-13 = 2.88. The graph CSV `fredgraph.csv?id=DFII10` returned HTTP 500.
- FRED series page, https://fred.stlouisfed.org/series/DFII10, WORKS, no login; H.15 via Board of Governors; 2026-10-09 = 2.91, 2026-10-15 = 2.78, matching Treasury those days.
- FRED terms, https://fred.stlouisfed.org/legal/terms/, WORKS; research use allowed; disruptive scraping prohibited; cite FRED and the Board; API needs a key.
- World Bank monthly workbook, https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx, FAILS, HTTP 500.
- Pink Sheet October 2026 PDF, https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Pink-Sheet-October-2026.pdf, WORKS, no login; gold row `$/toz`, “spot average of daily rates”; Sep 2026 = 4,319; quarters 3,459, 4,152, 4,876, 4,512, 4,268.
- World Bank commodity markets, https://www.worldbank.org/en/research/commodity-markets, WORKS, free; latest prices dated 10/02/2026; the fetched page did not itself deliver the workbook.
- World Bank dataset terms, https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets, WORKS; non-commercial use; derivative or commercial use needs written consent.
- Fed H.10 nominal broad dollar, https://www.federalreserve.gov/releases/h10/summary/jrxwtfb_nm.htm, WORKS, no login; Jan 2006 = 100, Dec 2021 = 115.8045, Sep 2026 = 119.2152; release 1 Oct 2026.
- Fed disclaimer, https://www.federalreserve.gov/disclaimer.htm, WORKS; public domain; copy with citation to the Board.
- Gold ledger, https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/gold/ledger_monthly.csv, WORKS, public raw file; columns `official_reporters_cf_t` and `official_change_cf_t` present; no licence line in the file.

## LITERATURE

- Erb, Claude B., and Campbell R. Harvey, “The Golden Dilemma,” NBER Working Paper 18706, January 2013. https://www.nber.org/system/files/working_papers/w18706/w18706.pdf. They report a −0.82 correlation of the real gold price with the month-end 10-year TIPS yield for 1997–2012, and −0.31 on a longer UK sample, with time-trend correlations of about −0.90 and +0.87. They publish no HAC t-stat and no break date. Quote: “a time trend seems to explain the real price of gold.”
- Torul, Orhan, “Gold’s Missing Anchor: The Real-Rate Decoupling and the Reserve-Safety Premium,” 1 July 2026. https://web.bogazici.edu.tr/torul/gold.pdf. He estimates the levels anchor through 2021-12-31 at β = −0.21 (R² = 0.66), then tests daily changes with Newey–West HAC (−7.8% per percentage point, post-2022 interaction +1.7). Andrews sup-Wald dates the level break to mid-2020; a sequential Bai–Perron-style test dates the residual’s trend breaks to mid-2021 and early 2022. He drops a levels regression when Engle–Granger fails. Quote: “The break is in the level, not the mechanics.”

## DECISION RULE

Checksums already in the spec (the 2026 levels beta −0.202, the changes beta −0.319, the seven-quarter beta −0.021) are reproduction checks. They do not support or reject the claim.

Primary test, one regression, monthly and non-overlapping, February 2006–September 2026 once gold history exists: Δ log gold on Δ 10-year real yield in percentage points and Δ log broad dollar. Bartlett HAC lag = max(12, the printed rule-of-thumb lag). Report 100 times the yield coefficient as approximate percent per percentage point.

- Supports: that coefficient is −5% or more negative per percentage point, and the HAC 95% interval lies entirely below 0.
- Against: the point estimate is zero or positive, or the HAC 95% interval covers 0.
- Inconclusive: the point estimate is negative and the interval covers 0.

Levels slope, levels HAC interval, levels sup-F date, and the post-2021 levels residual are confirmatory only if Engle–Granger rejects no-cointegration at 5% and the yield coefficient stays negative after a linear time trend. Otherwise those four objects are inconclusive regardless of the t-stat.

Break, on the differenced regression:

- Supports a datable shift only if all of these hold: Andrews sup-F at 15% trim rejects at 5% under Hansen’s approximation; the Bai (1997) 95% interval is no wider than 18 months; that interval still excludes a pure no-break after a December 2021 spline dummy; and the break month at trims 0.05 and 0.25 lies within 12 months of the 15% date.
- Against: sup-F at 15% trim does not reject at 5%.
- Inconclusive: it rejects, and the Bai interval is wider than 18 months, or the date moves by more than 12 months across those three trims, or the date is December 2021 and drops out once the spline dummy is included.

A 2026 “return” is not a break date this sample can estimate. It would support the return story only if the 2022–2023 changes interval covers 0 and a separate 2024–2026 changes interval lies entirely below 0. Otherwise that story is inconclusive. Rolling windows add nothing to this rule. The post-2021 residual, and only if cointegration holds, supports “the pre-2022 fit leaves the later price high” when the September 2026 log residual exceeds +2 in-sample residual standard deviations; it counts against that description when the absolute residual is under 1 standard deviation; between 1 and 2 it is inconclusive. The residual is a same-month association. Official tonnes do not explain it.

## SUCCESS CRITERIA

1. 2026 Treasury CSV: `10 YR` on 2026-10-13 equals 2.88 and on 2026-09-30 equals 2.93. The 21 September 2026 `10 YR` values sum to 55.40.
2. DFII10 text file: 2026-10-09 = 2.91, 2026-10-13 = 2.88, 2026-10-15 = 2.78. Archive CSV: 2023-12-29 `10 YR` = 1.72.
3. October 2026 Pink Sheet gold row: annual 1,943, 2,388, 3,442; quarters 3,459, 4,152, 4,876, 4,512, 4,268; July, August, September 4,073, 4,411, 4,319.
4. H.10 `jrxwtfb_nm`: January 2006 = 100.0000, December 2021 = 115.8045, September 2026 = 119.2152.
5. If the nine 2026 months are rebuilt, the levels beta is −0.202, the changes beta is −0.319, and the 2025Q1–2026Q3 levels beta is −0.021, each within 0.01. Those are checksums.
6. The results file prints the HAC lag. On the long sample it also prints a lag of at least 12 next to the rule-of-thumb lag.
7. `real_yield_break.csv` contains rows for trims 0.05, 0.15, and 0.25, and `ci_low`/`ci_high` are Bai (1997) bounds. The sup-F is compared with the Hansen 5% approximation, not a chi-square 5% line.
8. A cointegration p-value is printed before any levels t-stat. The price regression has no ledger column. Ledger checksum if kept separate: December 2025 `official_reporters_cf_t` = 36180.150 and August 2026 = 36516.811.
9. The long sample is skipped while the monthly workbook returns HTTP 500.

## UNCERTAIN

The gold vendor is not named. The October PDF says only “Gold, spot average of daily rates,” while silver on the same page is the London afternoon fixing, and the source list includes Bloomberg and S&P Global without tying them to gold. The Description tab is inside the workbook that returns HTTP 500. That tab, or a World Bank source note that names the gold series, would settle whether the row is a Refinitiv or LBMA series.

Whether a regression CSV that repeats the gold column is a “derivative work” under the World Bank remainder terms is an inference. A written answer from the Bank, or a catalog licence attached to the Pink Sheet, would settle it. No CC BY grant was on the pages fetched.

Whether the Fed rewrites pre-2022 broad-dollar levels inside the 1 Oct 2026 H.10 page is not stated on that page. Two archived vintages of the same month would settle it. Treasury does say the pre-spline and pre-2008-knot prints remain official.

DFII10 matched Treasury `10 YR` on 9, 13, and 15 Oct 2026. Day-by-day identity back to 2003, including across the 2008 and 2021 method breaks, was not checked.

Jan–Jun 2026 monthly gold prints were not re-fetched. The October PDF’s 2026Q1 = 4,876 and 2026Q2 = 4,512 match the spec’s quarter averages of those months. The April and July PDFs would settle the individual months.

IMF terms for the ledger were not on the GitHub file and were not fetched. The break-test sample is inferred as the ~249-month span from the runtime sentence “about 250 months.” The output spec never names the sample. The script header, once written, would settle it.

Bai’s 1997 PDF timed out on fetch. The interval recipe used here is the one stated on the fetched structural-break card: homogeneous-case anchors `P(|ξ| ≤ 7.7) ≈ 0.90` and `P(|ξ| ≤ 11.03) ≈ 0.95`, with the warning that unequal error variance across regimes makes those bounds approximate.

## Grok return 4: Four-country 10-year yield comovement

I'll review the design as written, then check the named data sources and the literature against the live web. First I'll read the spec and open the pages it depends on.The spec is in hand. Next I will fetch every source it names and locate papers that ran this kind of comovement test.The Treasury and Japan month files are live. I still need the Japan history file, the UK archive zip, the other vendors’ terms, and the papers themselves.The four-country factor share and the break-date intervals, built as written, would describe persistence and a two-series identity, not comovement.

Weekly last-print changes do not overlap, and the spec names no standard error, kernel, or bandwidth for them. The only 95% objects in the script are Bai–Perron intervals on the weekly level. Diebold, Li, and Yue, on these same four markets, find average first-order autocorrelation above 0.95, so an interval that treats the level as weakly dependent is far too narrow. Holiday weeks in the spec (Good Friday, 1 May, Juneteenth, Independence Day) already have unequal spacing.

The panel stores levels. The script runs Bai–Perron on the weekly level and never differences the panel before the factor share. On monthly levels for Germany, Japan, the UK, and the US, their first principal component explains more than ninety percent of level variation, and they find that principal component and their global factor are not the same object. A level share near 90%, and break dates in those levels, are what persistent yields produce.

The output schema reports at least 36 objects and names no multiplicity adjustment: 3 windows × 6 pairwise correlations = 18, 3 windows × 2 shares (correlation and covariance) = 6, and up to 3 breaks × 4 countries = 12 intervals. The title’s low-frequency test has no horizon, so it is untestable. The input years are 2018, 2019, 2022, 2023, 2024, 2025, and 2026, so 2020 and 2021 are absent. One change across that gap can dominate the sums of squares. The 2024 window ends at the latest common week. The Bund file’s last update is still 2026-08-03, value 3.21. US `10 Yr` was 4.70 that day and 5.09 on 2026-10-16, so 39 basis points of the US move sit outside the common sample.

The 88% share is `(1+0.76)/2`. The denominator is the trace of a 2×2 correlation matrix, which equals 2. With zero correlation that share is 0.50. For four series the same formula is `[1+3ρ]/4`, and zero correlation gives 0.25. The covariance share divides by the sum of variances, so the noisiest series sets it. `us_bei` is nominal minus real, so entering all three makes a singular correlation matrix while eigenvalues can still sum to 3. US `10 Yr` is a semiannual par yield. The Ministry of Finance 10-year is a semiannual constant-maturity yield from the 3pm close, released at 9:30 the next business day. The Bank of England 10-year is a continuously compounded zero-coupon spot, and the Bank revises the archive (the 2017 real-yield rewrite covered 2015–16). The Bund header says percent and does not state compounding. ECB `SR_10Y` on 2026-10-01 is 3.5921733451, against the Bund’s last print of 3.21 on 2026-08-03.

VERDICT: BUILD WITH CHANGES — it sinks if weekly yield levels are persistent enough that a principal-component share and Bai–Perron intervals on those levels are comovement.

REQUIRED CHANGES:
1. Estimate the factor share only on non-overlapping week-ending changes, and drop Bai–Perron on weekly levels. Diebold, Li, and Yue record autocorrelation above 0.95 and a level-factor share above 90% for these four markets (https://www.nber.org/system/files/working_papers/w13588/w13588.pdf).
2. Pre-commit one statistic, λ1/4 on the four nominal weekly changes, and treat every other share, pair, and break interval as descriptive. The written outputs are at least 18 correlations, 6 shares, and 12 intervals with no correction (same paper: they report one variance share with a posterior interval).
3. Download 2020 and 2021, and drop any change whose previous print is more than 5 business days earlier. The year list skips those two years, so one pseudo-week can dominate the sums of squares (https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_yield_curve&field_tdr_date_value=2026&page&_format=csv).
4. If the Bund last update is more than 5 business days behind the run, write the lag and mark the 2024 window inconclusive. The live file still ends 2026-08-03 at 3.21 (https://www.bundesbank.de/statistic-rmi/StatisticDownload?tsId=BBSIS.D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A&mode=its&its_csvFormat=en&its_currency=default&its_dateFormat=default&its_from=2026-08&its_to=2026-10).
5. Keep the UK zip out of the build until a request returns a 10-year spot column, and store any opened file as a Bank Resource for personal or internal non-commercial use. Both unhashed archive URLs returned HTTP 500, and the curve uses Bloomberg, Reuters, and Tradeweb inputs (https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/glcnominalddata.zip; https://www.bankofengland.co.uk/legal).
6. Decide on the correlation share only, and keep US par, Bund Svensson, JGB semiannual constant-maturity, and UK continuous spot as different objects. Covariance shares move with units; the Bank’s spot is continuously compounded (https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/qa.htm; https://www.bankofengland.co.uk/statistics/yield-curves/terminology-and-concepts).
7. Leave `us_bei` out of any matrix that already contains `us_nom` and `us_real`. The breakeven is their difference, so the matrix is singular while the eigenvalue-sum check can still pass (Treasury par URL above).

SOURCES:
- US Treasury par CSV, https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_yield_curve&field_tdr_date_value=2026&page&_format=csv, WORKS, public-domain government work, no key; `10 Yr` present.
- 17 USC 105, https://www.govinfo.gov/content/pkg/USCODE-2023-title17/html/USCODE-2023-title17-chap1-sec105.htm, WORKS, no copyright in US Government works.
- US Treasury real curve, same path with `type=daily_treasury_real_yield_curve`, not fetched this session.
- Bundesbank StatisticDownload, URL in change 4, CHANGED, free to save and reproduce with attribution; last update 2026-08-03.
- Bundesbank REST, https://api.statistiken.bundesbank.de/rest/data/BBSIS/D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A?startPeriod=2026-09-01&format=csv, FAILS, HTTP 500.
- Bundesbank website terms, https://www.bundesbank.de/en/homepage/user-information/conditions-for-the-general-use-of-the-website-764706, WORKS, reproduce for personal or professional use, cite the Bank, do not alter.
- MoF `jgbcme.csv`, https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/jgbcme.csv, WORKS, no key; column `10Y`; 2026/10/13 = 3.019.
- MoF `jgbcme_all.csv`, https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv, CHANGED, file opens and the header has `10Y`, but `10Y` is “-” from 1974/9/24 through 1979/6/19; later rows were cut off.
- MoF PDL notice, https://www.mof.go.jp/about_mof/notice/index.html, WORKS, PDL1.0 where no other mark is shown.
- PDL1.0, https://www.digital.go.jp/resources/open_data/public_data_license_v1.0, WORKS, commercial use allowed; numerical data are outside copyright.
- MoF Q&A, https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/qa.htm, WORKS, semiannual constant maturity, 3pm close, released 9:30 the next business day.
- ECB `SR_10Y`, https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y?startPeriod=2026-10-01&endPeriod=2026-10-16&format=csvdata&detail=dataonly, WORKS, no key; 2026-10-01 = 3.5921733451.
- ECB disclaimer, https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.en.html, WORKS as a public page; the returned text has no reuse sentence.
- BoE yield-curve page, https://www.bankofengland.co.uk/statistics/yield-curves, WORKS, no login and no API; archive zips listed at 39.2MB nominal and 25.1MB real; data are revised.
- BoE nominal daily zip, https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/glcnominalddata.zip, FAILS, HTTP 500.
- BoE nominal monthly zip, https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/glcnominalmonthedata.zip, FAILS, HTTP 500.
- BoE legal, https://www.bankofengland.co.uk/legal, WORKS as terms, Resources are personal or internal non-commercial; Database is OGL; third-party copyright stays with the owner.
- BoE terminology, https://www.bankofengland.co.uk/statistics/yield-curves/terminology-and-concepts, WORKS, continuous spot; inputs from Bloomberg, Reuters, Tradeweb, and the DMO.
- UK OGL v3, https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/, WORKS, copy and commercial reuse of information the provider can license; third-party rights excluded.

LITERATURE:
- Diebold, Li, and Yue, NBER Working Paper 13588 (November 2007), https://www.nber.org/system/files/working_papers/w13588/w13588.pdf. Same four countries, monthly continuously compounded zeros from one Fama–Bliss build, second calendar day of the month, global factor separated from country factors, equal half-samples with posterior odds. “average first-order autocorrelation greater than 0.95”
- Sutton, BIS Working Paper 44 (July 1997), https://www.bis.org/publ/work44.pdf. Ten-year yields in the US, Japan, Germany, the UK, and Canada are judged excess only against the expectations theory; this design has no base model. The fetched text does not give frequency or standard errors. “excess comovement relative to the base model”

DECISION RULE:
Descriptive only. A flow or a position coefficient does not support the claim.
Supports: on listwise non-overlapping weekly changes in US, Bund, gilt, and JGB 10-year yields, full sample 2018 through a latest week whose every print is within 5 business days of the run, correlation-matrix λ1/4 ≥ 0.55, average of the six pairwise correlations ≥ 0.40, and a moving-block bootstrap 95% lower bound ≥ 0.40 (block length 8, 1000 draws, seed fixed). The same λ1/4 is at least 0.45 in each of 2018–19, 2020–21, 2022–23, and 2024–latest. Under equal correlations, λ1/4 = [1+3ρ]/4, so 0.55 matches average ρ of 0.40. Zero correlation gives 0.25.
Against: full-sample λ1/4 < 0.40, or average pairwise correlation < 0.20, or the bootstrap interval includes a value ≤ 0.30. Zero-correlation share 0.40 would match average ρ of 0.20.
Inconclusive: the share or the bound falls between those cuts; any window’s share differs from the full-sample share by more than 0.15; listwise deletion drops more than 10% of weeks; any series has weekly-change standard deviation below 1 bp; the Bund lag exceeds 5 business days; replacing the Bund with ECB `SR_10Y` moves λ1/4 by 0.05 or more; block lengths 4 and 12 put the lower bound on opposite sides of 0.40. A Bai–Perron date on weekly levels is inconclusive at any interval width.

SUCCESS CRITERIA:
- Treasury column `10 Yr`: 2026-01-02 = 4.19, 2026-07-31 = 4.75, 2026-09-18 = 5.01, from the 2026 par CSV above.
- From the 30 listed weekly triples, correlations 0.76, 0.88, and 0.72, and (1+0.76)/2 = 0.88 with denominator 2. A four-country share that equals 0.88 has used the wrong denominator.
- MoF `jgbcme.csv` column `10Y`: 2026/10/13 = 3.019.
- Bund download: last update 2026-08-03 and 2026-08-03 = 3.21. Writing an October Bund from this file fails the check.
- ECB `OBS_VALUE` 2026-10-01 = 3.5921733451, stored only as the robustness series.
- Eigenvalues of the 4×4 correlation matrix of weekly changes sum to 4 within 1e-8, and the reported share is λ1/4.
- No change is taken across a gap longer than 5 business days, and no yield is regressed on a flow.
- UK pass condition: the archive request returns a 10-year continuously compounded spot. The two zip URLs above returned HTTP 500, so that check fails today.

UNCERTAIN:
- The history file’s last date. This fetch showed 1974/9/24 through 1979/6/19, with `10Y` equal to “-”, then 10,070 lines cut by the fetcher. Reading the last row of `jgbcme_all.csv` would settle whether 2018–2026 `10Y` is in it. A line count is not that date.
- The Bank of England page’s real zip href. The markdown conversion dropped the link target; the unhashed daily and monthly URLs returned HTTP 500. The href on the yield-curve page would settle whether a hashed link opens.
- Bund compounding. The CSV says Prozent and gives no convention. The series note would settle it.
- ECB reuse wording and compounding. The English disclaimer fetch contained no reproduction sentence, and the CSV does not state continuous compounding.
- US real yields 1.72 on 2023-12-29 and 2.68 on 2026-09-18, and any Treasury revision policy. The real-yield CSV was not fetched. The nominal checks above were.
- Sutton’s frequency, regression, and how he computed standard errors. Only the abstract came back from the PDF and the HTML page.
- A formal Bai–Perron size result under a unit root. That paper was not fetched. What was read is the spec’s silence on kernel and bandwidth, plus Diebold’s autocorrelation above 0.95.

## Grok return 5: JODI world oil ledger

I'll review the planned oil ledger against the three files on disk, then check the live sources and the published method before writing a build decision.The calendar row is only a one-line build. I’ll read the live JODI and EIA pages it names, then compare that plan with how published inventory tests were actually run.The download page is live, but the plan never names the file, the unit, or the missing-country rule. I’ll open the CSV, the STEO balance table, and the inventory papers next.VERDICT: BUILD WITH CHANGES. The assumption that would sink it is that a sum of JODI country closing stocks, with blanks treated as zero, is a world inventory that should match the EIA STEO world balance.

The calendar row specifies a country crude file “through 2026-07,” a reconciliation to STEO’s world balance and OECD stocks, and a JODI attribution. It specifies no horizon, no HAC estimator, no bandwidth, no test count, no transformation, and no vintage. Built that way, the file is a misleading world total, and any later lead-lag read off it is untestable.

Overlapping windows. Nothing in the row says which window, so there is no standard error to be right or wrong. A 3-, 6-, or 12-month stock change stacked on monthly data reuses the same months. Ordinary least squares treats those overlaps as new observations and makes the tests look sharper than they are. The inventory papers below do not repair that with Newey-West. They do not run the overlapping regression.

Look-ahead. JODI is updated on or around the 20th, and the submission deadline is two months after the reference month, with many reporters later than that. A July 2026 stock was not public in July. The 20 October build falls on the update day, so the file can change while it is being saved. For OECD countries, JODI replaces every month except the latest with IEA Monthly Oil Statistics, which is a revised series. STEO for this comparison was frozen on 1 October 2026 and calls the third-quarter inventory change an estimate. Pairing the latest revised JODI month with the price in that month uses information that did not exist on the price date.

Spurious levels. Closing stocks and prices are persistent. The row stores levels. Kilian and Murphy difference inventories because the percent change in inventories is not covariance stationary, and they keep the price in a 24-lag VAR rather than regressing the price level on the stock level.

Multiple testing. The row names no test. JODI’s own pages say “more than 90” participating countries and also “around 80,” with about 70 submitting on an M-1 target. A later pass over 80 countries, 5 series, and 4 horizons is 1,600 comparisons. Nothing in the plan counts them or corrects them. One pre-specified aggregate is the only comparison this build can support.

Sample. “Through 2026-07” is the month that happened to be complete on 13 October, not a window chosen before the September price move. STEO puts the September Brent average at $114/b and a daily print of $131/b on 15 September, inside the third-quarter draw and outside a July file. Reporters with full stock histories are the countries that keep reporting. China, Russia, Indonesia, Singapore, and Vietnam are documented holes, so a complete-case sample is the selected sample.

Denominators. Primary-file crude closing stocks are thousand-barrel levels (KBBL). Production and trade are also published per day (KBD). STEO’s world balance is million barrels per day of all liquids, and its OECD stocks are million barrels of commercial crude and other liquids. Adding those, or dividing by the wrong thousand, manufactures a gap. STEO’s world stock change also contains a residual line, “other inventory draws and balance,” which is not a measured stock.

REQUIRED CHANGES:
1. Keep non-reported cells as missing and publish no world stock total. JODI states that it does not fill gaps, and the APEC assessment records China with no closing stocks or stock changes and Russia with no submission after March 2023. https://www.jodidata.org/about-jodi/faqs.aspx
2. Take crude only from the primary file: ENERGY_PRODUCT=CRUDEOIL and flows INDPROD, TOTIMPSB, TOTEXPSB, STOCKCH, CLOSTLV. The secondary file is refined products and has no crude production. https://www.jodidata.org/_resources/files/downloads/oil-data/jodi-oil-wdb-item-names-ver2017.pdf
3. Use KBBL for closing stocks and KBD for production and trade, convert both by dividing by 1,000, and keep a single UNIT_MEASURE per series. The same guide defines KBBL as thousand barrels and KBD as thousand barrels per day.
4. Reconcile production to STEO world crude, 79.00 mb/d in 2025 and 75.40 mb/d in 2026. World liquids are a different series, 106.29 and 101.09 mb/d, with other liquids of 27.29 and 25.69 mb/d. https://www.eia.gov/outlooks/steo/tables/pdf/3atab.pdf
5. Reconcile measured stocks only with STEO Table 3a OECD commercial crude-and-other-liquids levels, 2,832 million barrels at end-2025. Leave STEO’s world draw, about 424 million barrels for January–September 2026, unmatched: about 147 million barrels of it is the residual line.
6. Store ASSESSMENT_CODE 1, 2, 3, and 4 with the cell, and keep code 2 and code 4 out of any total that is described as comparable. The code list is blue, yellow, not assessed, and under verification; the FAQ’s green/amber/red labels are a different scheme. https://www.jodidata.org/oil/support/user-guide/assessments.aspx
7. Save the download timestamp and the maximum TIME_PERIOD, and lag any descriptive comparison by at least two months. The database updates around the 20th, OECD history except the latest month is IEA Monthly Oil Statistics, and STEO’s third-quarter draw is an estimate completed 1 October. https://www.jodidata.org/oil/support/user-guide.aspx
8. Run no price regression in this build. Flows and stock changes stay descriptive; a correlation is not a cause. https://www.frbsf.org/wp-content/uploads/Kilian_Role-of-Inventories-and-Speculative-Trading.pdf

SOURCES:
- JODI download page, https://www.jodidata.org/oil/database/data-downloads.aspx, WORKS, free CSV claimed, no login; scripted reuse not granted.
- JODI overview, https://www.jodidata.org/oil/database/overview.aspx, WORKS, free, “more than 90” countries, “one month-old.”
- JODI user guide, https://www.jodidata.org/oil/support/user-guide.aspx, WORKS, acknowledge JODI; the sentence after “cite the source as follows” did not render.
- JODI terms, https://www.jodidata.org/terms-of-use.aspx, WORKS, all rights reserved; no script or redistribution licence.
- JODI item-name guide, https://www.jodidata.org/_resources/files/downloads/oil-data/jodi-oil-wdb-item-names-ver2017.pdf, WORKS, field names, KBBL/KBD, codes 1–4.
- JODI oil FAQ, https://www.jodidata.org/oil/support/faqs.aspx, WORKS, official submissions only; stocks are end-month levels.
- JODI general FAQ, https://www.jodidata.org/about-jodi/faqs.aspx, WORKS, around 80 countries; does not fill gaps.
- JODI assessments, https://www.jodidata.org/oil/support/user-guide/assessments.aspx, WORKS, M-2 deadline; OECD history except M-1 is MOS.
- APEC JODI progress, 8–10 April 2026, https://aperc.or.jp/file/2026/4/21/5_Session_6-A_Progress_of_JODI_in_APEC.pdf, WORKS, China 56% complete and no stocks; Russia stopped.
- JODI forum file note, 20 February 2018, https://www.jodidata.org/forum/jodi-support/naming-convention-and-location-of-zip-and-csv-files, CHANGED, names world_Primary_CSV_NewFormat.csv; that zip URL now returns HTTP 500.
- Primary file https://www.jodidata.org/_resources/files/downloads/oil-data/annual-csv/primary/primaryyear2026.csv and https://www.jodidata.org/_resources/files/downloads/oil-data/world_primary_csv.zip, FAILS, HTTP 500 this session.
- Guessed annual path https://www.jodidata.org/_resources/files/downloads/oil-data/annual-csv/primary/2026.csv, FAILS, HTTP 404.
- JODI Oil Manual PDF, https://www.jodidata.org/_resources/files/downloads/manuals/jodi-oil-2nd-manual.pdf, FAILS, HTTP 500.
- EIA STEO tables, 6 October 2026, https://www.eia.gov/outlooks/steo/data.php?type=tables, WORKS, free, no login, no key.
- EIA STEO Table 3a PDF, https://www.eia.gov/outlooks/steo/tables/pdf/3atab.pdf, WORKS, world liquids balance and OECD stock levels.
- EIA global oil narrative, https://www.eia.gov/outlooks/steo/report/global_oil.php, WORKS, third-quarter draw described as an estimate.
- EIA copyright, https://www.eia.gov/about/copyrights_reuse.php, WORKS, public domain; distribute with a dated acknowledgment.

LITERATURE:
- Kilian and Murphy, 12 May 2011 draft, “The Role of Inventories and Speculative Trading in the Global Market for Crude Oil,” https://www.frbsf.org/wp-content/uploads/Kilian_Role-of-Inventories-and-Speculative-Trading.pdf. They build one world proxy by scaling US crude stocks by the OECD-to-US petroleum-stock ratio, about 2.23 to 2.59, put inventories in barrel changes, and identify shocks in a 24-lag structural VAR with Bayesian 16th/84th bands. A country sum of JODI levels has no scale factor and no identified shock. “Given the lack of data on crude oil inventories for other countries.”
- Baumeister and Kilian, Bank of Canada Working Paper 2011-16, August 2011, https://www.publications.gc.ca/collections/collection_2011/banque-bank-canada/FB3-2-111-16-eng.pdf. They keep a separate vintage for each month, state that a vintage of world crude production reaches only t−3, discard the last six months before calling data final, and score horizons of 1, 3, 6, 9, and 12 months by mean squared prediction error against a no-change forecast. They say standard significance tests do not apply to those real-time ratios. HAC standard errors appear only in the revision regression, with no kernel and no bandwidth. “Because the most recent data are still preliminary, we discarded the last six months.”

DECISION RULE:
Supports: all of the following. China crude closing stocks and stock changes for 2026 are blank or “-”, and Russia has no crude rows after 2023-03. The US crude closing stock in million barrels (KBBL divided by 1,000) falls in 339–509, around the project’s 13 October commercial crude print of 424.134, or in 566–848 if the SPR of 282.983 is inside the JODI US stock. The 2025 sum of reporter crude production is at or below 81 mb/d. No world total is published, and no price correlation is published.

Against: any one of the following. A world stock-change total for January–September 2026 lies within 20 million barrels of 424. A 2025 reporter crude-production sum exceeds 81 mb/d. The US crude closing stock falls within 10 percent of STEO’s US commercial crude-and-other-liquids level of 1,289 million barrels at end-2025, that is, inside 1,160–1,418. China or Russia is filled in, or “-” is summed as zero. Any price result is reported from this build.

Inconclusive: a 2025 reporter crude-production sum from 64.00 through 79.00 mb/d against STEO world crude of 79.00. A first-half 2026 reporter stock-change sum whose distance from the STEO first-half world draw of about 252 million barrels is anywhere from 60 million barrels up, short of the 20-million-barrel band around the wrong January–September target of 424. A stock-identity pass rate from 80 percent up to, and not including, 90 percent. Any single pre-specified descriptive correlation, which cannot support a cause under the project rule.

SUCCESS CRITERIA:
1. From Table 3a, reproduce world crude production of 79.00 mb/d in 2025 and 75.40 in 2026, other liquids of 27.29 and 25.69, the 2025 world inventory withdrawal of −1.89 mb/d, the residual line of −1.59 mb/d, OECD end-2025 stocks of 2,832 million barrels, and US end-2025 stocks of 1,289. Then reproduce the project’s 424 million barrel January–September 2026 draw as −0.79×90 + 3.55×91 + 1.87×92 = 423.99.
2. On primary-file rows with CRUDEOIL, UNIT_MEASURE=KBBL, and ASSESSMENT_CODE=1, at least 90 percent of country-months with all three fields satisfy |STOCKCH − (CLOSTLV(t) − CLOSTLV(t−1))| ≤ the larger of 1 percent of the change and 100 KBBL. Record whether the median signs match.
3. Apply the US band in the decision rule, using KBBL/1000, and print the month. A figure inside 1,160–1,418 fails.
4. Print the 2026 CRUDEOIL CLOSTLV cell for China and the last Russia crude month. Blanks pass. A filled China stock, or a Russia month after 2023-03, stops the build.
5. Print max(TIME_PERIOD) and the download time. The 13 October verification says 2026-07. If the 20 October file reads 2026-08, the output must say 2026-08.
6. The output contains a JODI acknowledgment and “Source: U.S. Energy Information Administration (Oct 2026),” and it contains no price series and no p-value.

JODI detail for the builder. Crude production, imports, exports, closing stocks, and stock changes are primary-file fields: CRUDEOIL with INDPROD, TOTIMPSB, TOTEXPSB, CLOSTLV, and STOCKCH. Closing stocks are end-month levels, so the level unit is KBBL (thousand barrels). Divide by 1,000 for million barrels. Production and trade used as rates are KBD (thousand barrels per day); divide by 1,000 for million barrels per day. The overview also lists tons and litres. The downloads page says the series run from January 2002 to “one month-old” and are updated around the 20th; the participation rule marks a submission as on time if it arrives within two months, and the APEC note shows China often at M-3 or later. JODI does not estimate missing cells. Codes on the cell are 1 reasonable comparability, 2 consult metadata, 3 not assessed, 4 under verification; “-” means not reported, and “x” means the unit does not apply. The April 2026 APEC assessment, covering submissions through December 2025, shows China at 56 percent completeness with no closing stocks and no stock changes, Indonesia with no crude closing stocks, Malaysia with no closing stocks or stock change, Singapore reporting trade only, Vietnam missing every flow except crude production after February 2023, and Russia at zero submissions since April 2023. The user guide asks for an acknowledgment of the Joint Organizations Data Initiative (JODI) in any derivative work. The terms reserve all intellectual property and do not mention scripted download.

Reconcile to STEO Table 3a of 6 October 2026, completed 1 October. Match crude production to the crude line, not to total liquids. Match stock levels, if at all, to OECD commercial crude and other liquids: 2,832 million barrels at end-2025, of which the United States is 1,289. STEO publishes no world stock level. Its world balance is production minus consumption, printed as inventory net withdrawals: a 1.89 mb/d build in 2025, of which 1.59 mb/d is “other inventory draws and balance,” and a 1.34 mb/d draw in 2026, of which 0.36 mb/d is that residual. For January–September 2026 the world withdrawal rates sum to about 424 million barrels, and the residual rates sum to about 147 million barrels. A gap of that order between a JODI reporter sum and the STEO world draw is the normal one. A gap near zero would mean the residual had been filled in. First-half 2026 is the window a July file can actually see: about 252 million barrels of world draw, of which about 60 million barrels is the residual.

UNCERTAIN:
- The live CSV’s last month and row count. Three file URLs returned HTTP 500 and one returned 404, while the download page still offers a free CSV. A browser save on 20 October settles whether the 500 is a bot wall and whether the file still ends at 2026-07.
- The current zip name. The 2018 forum post names world_Primary_CSV_NewFormat.csv; the downloads page now lists annual primary files and did not print that name.
- The exact attribution sentence. The user guide stops at “cite the source as follows.”
- The sign of STOCKCH. The manual PDF returned HTTP 500. The US identity check settles whether a positive stock change is a build.
- Whether the October 2026 file still matches the April 2026 APEC gaps for China and Russia.
- Whether US JODI closing stocks include the SPR. The 339–509 band and the 566–848 band separate those two readings.
- Which Table 3a columns are shaded as forecasts. The note says shading marks the break; the text extract did not show it. The narrative does call the third-quarter draw an estimate.
- The IEA licence for the OECD months that JODI says are Monthly Oil Statistics. That licence was not fetched again this session.
- Both papers are the 2011 working papers that were fetched, not the later journal PDFs.

## Grok return 6: N-PORT fund Treasury futures (R2b next build)

I'll review the cash-Treasury design and the N-PORT spec first, then check the live sources and the literature against that written plan.The cash build is specified; the futures leg is only a deferred sketch. I’ll check that sketch against the live N-PORT dictionary, the sources it names, and papers that actually measured fund derivatives.The futures table in the N-PORT readme has notional and expiry, but not the underlying contract. I’ll confirm that on the form instructions and check each source page the design names.**VERDICT: BUILD WITH CHANGES.** The assumption that would sink it is that `FUT_FWD_NONFOREIGNCUR_CONTRACT.NOTIONAL_AMOUNT`, times an analyst-chosen tenor, is a 10-year equivalent that can be added to cash ΔS and divided by public cash supply ΔP.

The deferred sketch in the spec (§4.6) is “DIR lines with `DERIVATIVE_CAT = FUT`, joined to `FUT_FWD_NONFOREIGNCUR_CONTRACT` on `HOLDING_ID`, contracts × face by tenor, 10-year equivalents at representative maturities.” Built that way, the number is the wrong object, and the cash verdict lines cannot test it.

**Why that build fails**

The futures table does not contain a contract count, a reference instrument, or an underlying tenor. Its fields are payoff (long/short), expiration date, notional amount, currency, and unrealized appreciation. The form defines the notional as the aggregate notional or contract value **on the trade date**, and it defines expiration as the contract’s expiry. Item C.11.d.ii puts the reference instrument in the same structure as Item C.11.c.iii, which the bulk files store in `DESC_REF_OTHER`, `DESC_REF_INDEX_BASKET`, and `DESC_REF_INDEX_COMPONENT`, plus free text in `ISSUER_TITLE`. The written join never reads those. “Representative maturity” is not a field.

Using expiry as the tenor assigns a few months of duration to a note future. Using one face for every contract mis-scales the 2-year contract, whose face is $200,000; every other Treasury contract on the CME page is $100,000. Holding-level `PAYOFF_PROFILE` is N/A for derivatives; the sign is on the futures table. `CURRENCY_VALUE` and `UNREALIZED_APPRECIATION` are the mark-to-market. Summing them measures variation margin and misses the exposure.

There is no standard error in the design, so there is nothing for a HAC estimator to get right. Each fund is placed in month m₀, else m₀−1, else m₀+1, so one filing can enter two adjacent quarterly stocks. The full-window change is the sum of 2024, 2025, and 2026H1, so those four figures are one identity. With 11 quarterly windows, a Newey–West lag of about 4×(T/100)^(2/9) is about 2 quarters, shorter than a four-quarter overlap, so an overlapping-horizon t-test is not identified. The cash landing already prints labels for six variants (M0, M1, M8, P1, P2, D6) across four periods, 24 labels, with no Bonferroni or Benjamini–Hochberg correction. The futures sentence in the findings note then asks whether a relayed $120bn would lift the scaled arm from $449.7bn across the $460bn line. That comparison was chosen after the cash result; the shortfall is $10.3bn, inside the unexplained $131bn N-PORT–Z.1 gap. The sample is the 11 zips already used for cash (2023Q4–2026Q2). That matches the R2 episode. It drops the 2020–2023 futures cycle the papers measure, and the one-seventh line ($459.8bn) sits next to the funds’ own starting share (about $468bn). One country is in scope. The multiple-testing problem is the variant-by-period grid, not a country grid.

A regression of futures levels on yield levels over this window would be a regression of two trends. The design never says “changes.” The fixed end-2023 curve is a constant-price quantity index for cash; it does not rescue a futures measure built from trade-date contract value.

Look-ahead and vintage: the position date is `REPORT_DATE`; the public file is the third month of the fund’s fiscal quarter, filed up to 60 days later, and a filing after 5:30pm ET on the quarter’s last business day waits for the next zip. Amendments inside the 62-day lag restate the whole form. The mutual-fund Treasury cell used as a scaler is `FL653061105` = `FL653061003` − `FL653061703`, and the guide still says the most recent quarter of `FL653061003` is estimated from price indexes plus estimated transactions. In the current release that quarter is 2026Q2. A CTD chosen from a later exchange page is a second look-ahead. The ETF cell `LM563061103` is ICI government-bond ETF total net assets, not the Treasuries held by all ETFs.

Futures are in zero net supply. The spec already says a share of ΔP built from them does not add across holders. Adding ΔF to ΔS and re-issuing the $460bn / $100bn labels treats a gross risk overlay as a holder of the cash stock.

**How to convert a Treasury future**

Map the reference text to a contract. Face is $200,000 for the 2-year and $100,000 otherwise. On the report date, take the cheapest-to-deliver note’s DV01 per contract face and divide by its conversion factor:

BPV of the contract = BPV of the CTD ÷ conversion factor.

The CME worked example is $42.45 / 0.8317 = $51.04 per 5-year contract. Signed contracts times that BPV, divided by the 10-year par DV01 on the fixed end-2023 curve (modified duration 8.2233), is the 10-year equivalent. A dated public CTD file was not on the page that states this formula. Until one is in hand, use a pre-registered tenor (2 / 5 / 7 / 10 / 20 / 25) inside the same `price_one` function, and treat the gap versus any later CTD calculation as a published sensitivity. Do not add expiry to the underlying maturity.

**Double-count and miss**

Cash Treasuries already in ΔS include securities posted as futures margin; add futures DV01 to cash DV01, and do not add futures notional to cash market value. Counting `BALANCE` × face and `NOTIONAL_AMOUNT` counts the same position twice. The futures table also holds non-currency forwards, including when-issued trades, which do not have a CME face. Options on futures live in `SWAPTION_OPTION_WARNT_DERIV` (delta is there). Swaps live in `NONFOREIGN_EXCHANGE_SWAP`. In the Choi–Kim–Randall fixed-income sample, interest-rate swaps are 54% of derivative position counts, so a futures-only total misses most of the interest-rate-derivative book. Keyword screens pick up gilts and JGBs and drop wordings that never say “10y”; Barth, Kahn, Monin, and Sokolinskiy exclude “EUREX,” “JPN,” and “gilt” and still spot-check. Master and feeder funds can both file. Part D miscellaneous securities, up to 5% of assets, are nonpublic. Only one month per fund fiscal quarter is public, so rolls between public dates are invisible.

## REQUIRED CHANGES

1. Join futures to `DESC_REF_OTHER`, `DESC_REF_INDEX_BASKET`, `DESC_REF_INDEX_COMPONENT`, `IDENTIFIERS`, and `ISSUER_TITLE`, and sign with `FUT_FWD.PAYOFF_PROFILE`.
   The futures table has no reference instrument; Item C.11.d.ii points at Item C.11.c.iii. https://www.sec.gov/files/formn-port.pdf

2. Measure contracts × the contract face ($200,000 for the 2-year, $100,000 otherwise), or the trade-date notional, never both, and never `CURRENCY_VALUE`.
   Item C.2.a is the contract count; Item C.11.d.iv is trade-date notional or contract value; unrealized appreciation is the mark. https://www.sec.gov/files/nport_readme.pdf

3. Convert with CTD DV01 ÷ conversion factor, or a pre-registered tenor map, and publish the gap between them.
   Contract BPV equals CTD BPV divided by the conversion factor. https://www.cmegroup.com/education/courses/introduction-to-treasuries/how-can-you-measure-risk-in-treasuries

4. Keep ΔF as its own risk exposure. Do not add it to ΔS, do not divide by ΔP, and do not re-use the $460bn line.
   Futures are zero net supply, so a share of cash supply does not add across holders. The ETF scaler is government-bond ETF assets, not Treasury holdings. https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=LM563061103&t=

5. Pre-register one magnitude test, |ΔF| against $100bn, and stop if the 2023Q4 anchors below fail.
   The Fed’s own book shows notional and DV01 diverge, and mutual-fund growth was in the 2-year and 5-year contracts. https://www.federalreserve.gov/econres/notes/feds-notes/why-do-mutual-funds-invest-in-treasury-futures-accessible-20240510.htm

6. Drop interest-rate swaps, options, and non-Treasury futures from this total, and print their notional beside it.
   Swaps dominate interest-rate-derivative counts in the N-PORT fixed-income sample, and a futures keyword screen is how the Treasury subset is identified. https://www.federalreserve.gov/econres/feds/files/2024039pap.pdf

7. Do not scale the futures result by the 11 Sep 2026 Z.1 mutual-fund cell.
   That Treasury series is government securities minus agencies, and the parent series says the latest quarter is estimated from price indexes. https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FL653061003&t=

## SOURCES

- SEC Form N-PORT data sets, https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets, WORKS, free, no login; 2019Q4–2026Q3 zips listed; scripted use needs a declared User-Agent, 10 requests/second.
- N-PORT readme (bulk dictionary), https://www.sec.gov/files/nport_readme.pdf, WORKS, same SEC terms; tab-delimited tables, as-filed.
- Form N-PORT (12/23), https://www.sec.gov/files/formn-port.pdf, WORKS, free form instructions.
- SEC webmaster FAQ, https://www.sec.gov/about/webmaster-frequently-asked-questions, WORKS, EDGAR content “free to access and reuse”; scripted download allowed with a declared User-Agent.
- Z.1 S.124.1 current, https://www.federalreserve.gov/releases/z1/current/html/S124_1_s.htm, WORKS, free page, no key; 2026Q2 `LM653061105` = 1,741.2.
- `FL653061105` analyzer, https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FL653061105&t=, WORKS, free; Treasury equals government securities minus agencies.
- `FL653061003` analyzer, https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FL653061003&t=, CHANGED, page is free, but the input is “ICI by subscription” and the latest quarter is an estimate from price indexes.
- `LM563061103` analyzer, https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=LM563061103&t=, CHANGED, free page; the series is ICI government-bond ETF total net assets, not all ETFs’ Treasuries.
- `LM553061103` analyzer, https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=LM553061103&t=, CHANGED, free page; ICI unpublished detail, capital gains from Bloomberg series G0A0.
- S.124.2 and S.124.3 level tables, https://www.federalreserve.gov/releases/z1/current/html/S124_2_s.htm and https://www.federalreserve.gov/releases/z1/20260911/html/S124_3_s.htm, WORKS, free; closed-end Treasury 2.0, ETF line 807.6 in 2026Q2.
- Daily Treasury par yields for 2026, https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2026, WORKS, free, no key; through 16 Oct 2026. The archive page stops at 2023, so 2024–2026 are this year page, not the old archive CSV.
- MSPD “detail” page, https://fiscaldata.treasury.gov/datasets/monthly-statement-public-debt/detail-of-treasury-securities-outstanding, CHANGED, API is open, but the fields shown are the summary, not CUSIP-level Table 3.
- Fiscal Data API license, https://fiscaldata.treasury.gov/api-documentation/, WORKS, “free, without restriction,” no token.
- NY Fed SOMA holdings, https://www.newyorkfed.org/markets/soma-holdings, WORKS, public download page; the export widget did not render, and https://www.newyorkfed.org/terms-of-use returned no license text.
- CME Treasury risk note, https://www.cmegroup.com/education/courses/introduction-to-treasuries/how-can-you-measure-risk-in-treasuries, WORKS, fetched with no login; formula and faces are there; a dated CTD history is not.
- FEDS note, https://www.federalreserve.gov/econres/notes/feds-notes/why-do-mutual-funds-invest-in-treasury-futures-20240510.html, WORKS, free; accessible numbers at the companion URL below.

## LITERATURE

- Iorio, Li, and Petrasek, FEDS Note, 10 May 2024, https://www.federalreserve.gov/econres/notes/feds-notes/why-do-mutual-funds-invest-in-treasury-futures-20240510.html. They separate notional from DV01 and find futures are a small share of portfolio DV01 because the book is short-tenor and partly offsetting. “futures contribute just 7 percent of the overall portfolio DV01.”
- Barth, Kahn, Monin, and Sokolinskiy, FEDS 2024-039, https://www.federalreserve.gov/econres/feds/files/2024039pap.pdf. They classify Treasury futures with keywords, not a tenor field, and take futures duration from J.P. Morgan Markets, which this project cannot use. “We use keywords to extract the Treasury futures positions from N-PORT.”
- Choi, Kim, and Randall, 10 December 2023, https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/news-and-events/events/2023/10/19/interest-rate-variability-and-the-financial-sector/Choi_Dec2023.pdf. They set futures duration equal to expiry plus the reference bond’s maturity, and their sample is dominated by swaps after a Morningstar match. “a 3-month future on a 10-year Treasury bond has a 10.25-year duration.”

## DECISION RULE

One comparison, set before the futures build runs. ΔF is the change in signed Treasury-futures 10-year equivalents from the 2023Q4 window to the 2026Q2 window, same survivors and 62-day lag as the cash build, fixed end-2023 curve. It is an exposure. It is not a cause of yields, and it is not a share of the public’s +$3,218.3bn.

- **Supports** “futures are large beside the cash result” only if |ΔF| ≥ $100bn, the 2023Q4 anchors below pass, the 62-day vintage and the matched vintage differ by at most $20bn, and a tenor-map ΔF and a CTD ΔF differ by at most $50bn.
- **Against:** |ΔF| < $100bn with those same anchors passing.
- **Inconclusive:** any anchor fails; unclassified USD futures notional exceeds 10%; the two vintages differ by more than $20bn; or the tenor-map and CTD figures differ by more than $50bn. A result that crosses $460bn only after adding ΔF to cash ΔS is inconclusive by rule. The relayed $120bn and the $10.3bn scaled-arm gap are not thresholds.

Half-years may be printed. They are not a second test. No t-statistic.

## SUCCESS CRITERIA

Reproduce these from the public N-PORT zips and the fixed end-2023 curve. The 2023Q4 universe is funds with more than 1% of net assets in Treasury securities or Treasury futures, matching the note’s “Treasury funds.”

1. Net Treasury-futures notional in that universe at 2023Q4 is between $250bn and $380bn. The accessible table prints $313.8bn (3.13779×10^11). Face is $200,000 for the 2-year and $100,000 otherwise; shorts are subtracted. Outside the band, stop.
2. Futures DV01 divided by notes-and-bonds DV01, same universe and date, is between 0.20 and 0.45. The printed center is 117,752,385 / 388,686,063 = 0.303. Above 0.45, the tenor map is too long.
3. Implied futures modified duration, futures DV01 / (net notional × 0.0001), is between 3.0 and 4.5 years. The center implied by those two printed figures is about 3.75 years. The unit label “Millions of $” on that table fights the arithmetic; the ratio does not depend on it.
4. Inside the cash build’s ≥90%-Treasury universe, futures 10-year equivalents are at most 15% of that universe’s cash 10-year equivalents at both endpoints. The cash DV01 median ratios were 0.998 and 0.999; a large futures book inside that universe would have broken that check.
5. A one-contract 2-year long maps to $200,000 face. A future expiring within 90 days whose text is a 10-year note future receives a tenor of 6–10 years, not the expiry.
6. |Unrealized appreciation| / |notional| on the kept futures lines is under 5%. A build that used `CURRENCY_VALUE` as the position fails this.
7. Unclassified USD `DERIVATIVE_CAT` future notional is at most 10% of USD futures notional. Swap and option notionals are printed and excluded.
8. |ΔF| under the 62-day vintage and under the matched vintage differs by at most $20bn, or the label is inconclusive. Two runs’ output hashes match. No verdict column equals ΔF / $3,218.3bn.

## UNCERTAIN

- The bulk codes `DIR` and `FUT` are what the cash spec read off the zips. The form’s words are “derivative-interest rate” and “future.” The readme does not list the codes. The XML technical specification v1.12 is a zip; it was not unpacked. Counting distinct `ASSET_CAT` and `DERIVATIVE_CAT` values in one zip would settle it.
- Whether futures `HOLDING_ID`s actually appear in `DESC_REF_OTHER` is inferred from the form’s cross-reference, not from a row count. A join count on one zip would settle it.
- The accessible DV01 table is headed “Millions of $,” but those figures only produce a plausible duration if they are dollars per basis point. The 0.303 ratio is safe; a dollar DV01 level is not. The figure’s original note in the PDF would settle the unit.
- The data-sets page lists the 2026Q3 zip and its size. The fetched markdown did not include the href. The href on that page would settle the URL pattern.
- A free dated CTD and conversion-factor file was not found. The CME page states the formula and an example. Contract rules plus MSPD CUSIPs plus the report-date curve would settle a CTD path; the machine-readable MSPD page that was fetched does not show CUSIP rows.
- `FL653061003`’s “most recent quarter is estimated” sentence was last edited 7 June 2016 and is still on the page. The December 2026 Z.1 release notes would show whether 2026Q2 was in fact the estimated quarter.
- The NY Fed terms page returned no readable license. The SOMA holdings page says history is downloadable; the column layout did not render.
