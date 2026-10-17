# Grok batch g6, 17 Oct 2026: page attack and four pre-registrations

Nine parcels through orchestrator_cursor (Grok 4.7, 256k, extra-high effort; fenced to read + web). All nine returned SUCCESS:
no breaches, nothing blocked, no URL cited without a fetch, Cursor default model restored. Grok's text is kept below as a dated
record. **It is input, not result.** Each section is headed by what the supervisor checked.

## Supervisor check: page attack (parcels A to E)

Grok judged 61 page claims: 5 STANDS, 39 WEAKENED, 14 FALLS (A 10/2, B 1/8/3, C 8/2, D 1/8/3, E 3/5/4 as stands/weakened/falls).
An independent Sonnet verifier checked the eight load-bearing FALLS against the project's files and primary sources; the
supervisor re-read the deciding source for each. Outcome:

- **Confirmed and corrected:** Gabaix–Koijen's "15" is the microstructure literature's figure, not theirs (C-147; the verifier's
  and Grok's further claim that 10.9 appears only in a column the authors do not recommend was itself an overreach: the one-factor
  column gives 10.85); the ETF census check is not independent (C-148); the retirement figure's "real exit" and "organic net"
  labels (C-149).
- **Partly confirmed and corrected:** the expected-rate fall is a net that hides its dating (C-150); "re-use intensity did not
  rise" was undefined and the banks' re-pledged share did edge up in H1 2026, and "did not carry" was causal wording (C-152);
  the 36–60% growth range is two bases, not bounds (C-153).
- **Also corrected from the WEAKENED list, after the supervisor re-read the path:** "the earnings yield barely moved" hid a
  −61bp/+45bp round trip (C-151); the lead figure's alt text spliced Z.1 with S&P 500 boxes (C-154).
- **Rejected:** the wholesale-share "plateau" (Grok read a stale file; `_research/n2b_v2/zk_v2.csv` gives 23.07% and 22.96%); the
  household row (the Fed note's $1.4trn is a stock gap, 59% of the $2.37trn end-2024 household stock, so "largely" holds for
  the stock); Japan's "0.4 dollars" (the pre-registration defined the adjustment as R1's full holding return, and raw and
  adjusted ratios both round to about 0.4); the 113bp window start (the window is the project's fixed one and is labelled).

## Supervisor check: pre-registrations (parcels 1 to 4)

An independent Sonnet verifier re-fetched every non-SEC input (GPIF flashes, MoF yields, Fed Z.1 bulk files, OFR money-fund
series) and found all of them matching, and re-ran the arithmetic: SAFE TO REGISTER. The supervisor fetched the SEC-only figures
with the approved contact: Meta $58.14bn (30 Sep 2025) and $182.88bn (31 Mar 2026), NVIDIA $25bn + $20bn (26 Jul 2026), Oracle
$248bn, $261bn and $288bn, Alphabet $75.6bn, Amazon $75.021bn: all match. Small fixes carried into CALENDAR.tsv: pp_1's
six filer points sum to $1,369bn, not $1,370bn; pp_4's next Z.1 release is 10 Dec (the Fed's release page), and the calendar's
11 Dec row was re-dated. Scored on the rows dated 2026-11-06, 2026-11-15, 2026-12-10 and 2026-12-15 in CALENDAR.tsv.

## Grok return: page attack, parcel A

I'll review the page section against the project's own evidence note and the data files those claims rest on. First I'll read the local materials and pull the cited findings notes.The page mixes an accounting split of prices with a money-side story. I’ll check the numbers that carry that argument against the findings notes that own them.The Treasury curve confirms the US starting point. Next I’ll check the path inside the window and the project’s own monthly series.The page’s lead story is an endpoint reading of two different markets. Several of those endpoints are real. The sentences that turn them into one explanation of 2024–26 are not.

1. **CLAIM:** "the earnings yield barely moved while real yields rose"  
   **VERDICT:** WEAKENED  
   **REASON:** On the project’s own monthly means, the trailing earnings yield fell 61bp in 2024 (4.11% to 3.50%) and rose 45bp in the first half of 2026, so the net is −14bp. The trailing price-earnings ratio went 24.35 to 28.60 and back to 25.22. The real yield’s +0.34 point is the change in the monthly average of the Treasury 10-year real par yield, from 1.836% in December 2023 to 2.179% in June 2026. Month-end to month-end that yield rose 48bp, from 1.72% on 29 Dec 2023 to 2.20% on 30 Jun 2026. On the cyclically adjusted yield the multiple rose 8.7 points, from 31.45 to 40.15.  
   **SOURCE:** `_research/2026-09-12-P2c-decomposition_annual.csv`, rows 2024 and 2026_YTD trailing_E; Treasury real-yield CSVs for 202312 and 202606.  
   **QUOTE:** "rose 17.5% in 2024 and gave it back"  
   **UNCERTAIN:** The earnings-yield path uses the project’s Shiller series. The Yale file was not re-read here.

2. **CLAIM:** "Revaluation splits into earnings growth and a net multiple change"  
   **VERDICT:** FALLS  
   **REASON:** The $46,919bn rise is the Z.1 stock of corporate equities from 2023:Q4 to 2026:Q2 ($76,768bn to $123,687bn). The +0.87 price-earnings point is the S&P 500 trailing multiple from Dec 2023 to Jun 2026, equal to about 3.6% of the Dec 2023 index level. Those are not two parts of one $43.7tn residual. The rate leg (−2.14) and premium leg (+3.01) sum to +0.87 by construction, and 2.14/3.01 = 71% of the premium leg repeats the rate move.  
   **SOURCE:** `2026-09-11-P1-Equity-Net-Buyers.md`, 2024:Q1–2026:Q2 block; `_research/2026-09-12-P2c-decomposition_windows.csv`, trailing_E row 2024-2026.  
   **QUOTE:** "not listed market cap"  
   **UNCERTAIN:** Nothing material. The splice is in the figure alt text. The prose underneath keeps the two identities apart.

3. **CLAIM:** "6.9% is shares that did not exist before"  
   **VERDICT:** WEAKENED  
   **REASON:** $3,243bn / $46,919bn is 6.9%, and that ratio is an identity: change in level minus net issuance. ETF share creation was $3,604bn, larger than the whole net issuance, and $1,065bn of it (29.6% of the wrapper, 2.3 percentage points of the 6.9) was bond ETFs. Closely held equity rose $5.9tn, 12.6% of the $46.9tn, and foreign equity held by US residents rose $4.9tn, 10.4%.  
   **SOURCE:** `2026-09-15-ETF1-Identity-Net-Of-ETF.md`, issuer table and ICI-type table; P1 period block.  
   **QUOTE:** "Almost thirty cents of every dollar"  
   **UNCERTAIN:** The dollar levels are the project’s parse of the 11 Sep 2026 Z.1. The Fed bulk file was not re-downloaded here. Other-volume changes for the whole instrument are unpublished.

4. **CLAIM:** "Prices rose mostly because earnings rose"  
   **VERDICT:** WEAKENED  
   **REASON:** Log price equals log earnings plus log multiple. From the project’s Dec 2014 and Jun 2026 anchors, earnings are 82.3% of the log price gain (1.060 / 1.288). The same split is 71.0% if it stops at Dec 2025. The opening sentence does not name that window. "Because" states the identity as a cause. Restating 2025 earnings at the 2015 effective tax rate, 27.4% to 19.6% on 412 firms, moves the 82.3% to 74.5%.  
   **SOURCE:** `2026-09-11-P2a-Return-Decomposition.md`, cumulative table; `2026-09-21-W3-Tax-Decomposition.md`, restated-EPS table.  
   **QUOTE:** "the upper end is tax-assisted"  
   **UNCERTAIN:** Shiller’s file was not re-opened. The 82.3% is the arithmetic of the anchors P2a says were checked.

5. **CLAIM:** "Profit plus index composition is at least 69 to 75 percent"  
   **VERDICT:** WEAKENED  
   **REASON:** Profit is not a measured total. It is Shiller earnings growth minus a share-count decline, so index composition sits inside it. The 7–13% accretion band is four weightings on current S&P members, 385 of 500 firms, and survivorship pushes every weighting up. "At least 69 to 75" is the complement of that band inside a fixed 82.3% (100 − 17.7 − accretion). A non-specialist cannot see that the two hatched bands are one split.  
   **SOURCE:** `2026-09-18-EPS-Split.md`, C-093 banner and weighting band.  
   **QUOTE:** "aggregate profit is a residual that absorbs index composition"  
   **UNCERTAIN:** The missing-mega correction (Alphabet, Berkshire, Tesla, Broadcom) is unsigned. Apple’s share-count endpoints were not re-pulled from SEC companyfacts.

6. **CLAIM:** "In 2024 it arrived as drift rather than on news"  
   **VERDICT:** WEAKENED  
   **REASON:** The object is the 2024 change in trailing price-earnings, +3.20 points on daily closes, and quarter-end earnings steps of −2.83 points sit inside it. At the [−1, +1] window, FOMC days are 9.5% of sessions and +25.6% of the change. Stripping shared days, they are 40% of the change. Ordinary days dominate only because the event sets are sparse and the earnings window is net negative.  
   **SOURCE:** `2026-09-14-P5i-Event-Study-Result.md`, head-to-head table.  
   **QUOTE:** "FOMC beats earnings, robustly"  
   **UNCERTAIN:** Nothing on the arithmetic. Whether a wider news calendar would shrink the residual was not tested.

7. **CLAIM:** "the money arriving met a shrinking float"  
   **VERDICT:** WEAKENED  
   **REASON:** Nonfinancial corporate net issuance was −$541bn over 2024:Q1–2026:Q2, public and closely held together. The project cannot split that flow into listed and closely held, so it is not a measured float. Stripping only ETF shares leaves −$361bn, and that line still mixes in foreign issuers (+$382bn). In 2026:Q2 nonfinancials issued +$153bn. Gross retirement was 65% repurchases and 35% M&A.  
   **SOURCE:** `2026-09-15-ETF1-Identity-Net-Of-ETF.md`, issuer table and quarterly-path section; answer note §2.  
   **QUOTE:** "not an operating-company figure"  
   **UNCERTAIN:** The quarterly +$153bn is the project’s Z.1 read, not a fresh Fed pull.

8. **CLAIM:** "The collateral channel did not carry this repricing"  
   **VERDICT:** FALLS  
   **REASON:** This says a money channel did not move the price. The project’s own ban is that no flow share of the price is measured. What was measured is smaller: in 2024, private repo net of the Fed’s reverse repo fell $46bn, and the handoff-adjusted wholesale increase was about $136bn against $1,405bn of household purchases of the wrapper. The dated collateral-stock step, +19% at six banks, is the first half of 2026, while the multiple was falling from 28.48 to 25.22. "Shadow money did not in 2024" is the same causal sentence.  
   **SOURCE:** `2026-09-15-N4-Scale-Timing-Bound.md`, N4b table and C-085 banner.  
   **QUOTE:** "No percentage of purchases ran through"  
   **UNCERTAIN:** Nothing on the sign of the 2024 handoff. Existing wholesale stocks, as distinct from their growth, are explicitly untested.

9. **CLAIM:** "The 10-year yield rose 113bp" and "almost all of it was real"  
   **VERDICT:** WEAKENED  
   **REASON:** From 3.88% on 29 Dec 2023 to 5.01% on 18 Sep 2026 is 113bp, and the real par yield rose from 1.72% to 2.68%, which is 96bp. From the 19 Oct 2023 peak of 4.98%, the 18 Sep 2026 level is +3bp. Only +16bp of the 113 accrued by 13 Feb 2026 (the yield was 4.04%); 97bp came after that. End-2025 was 4.18%, so 2025 had given back the earlier rise. By 30 Sep 2026 the nominal yield was 5.29%, 141bp above 3.88%. The page, dated 17 Oct, still says 113bp and does not name the end date.  
   **SOURCE:** Treasury nominal CSVs for 202310, 202312, 202512, 202602, 202606, 202609, and the real-yield CSVs for 202312 and 202609.  
   **QUOTE:** "Measured from that October peak, the rise"  
   **UNCERTAIN:** Germany’s 156bp and Japan’s 243bp were not re-read from the Bundesbank or the Ministry of Finance. The ECB AAA 10-year spot rate on 29 Dec 2023 was 2.08%, matching R3’s start. The 2026 endpoints of those two series were not in the portion returned. R1’s note that a Cleveland Fed real rate rose about 57bp was not re-fetched.

10. **CLAIM:** "JGB rate risk grew 11–25%"  
    **VERDICT:** WEAKENED  
    **REASON:** The 11–25% band is the project’s own range across two formulas and two start dates, and the top end uses an estimated end-2023 stock. At each date’s own yields the same public 10-year-equivalent stock fell 6.5%, from ¥558tn to ¥522tn. The page’s "grew" does not say the quantity is held at constant yields.  
    **SOURCE:** `2026-09-27-R3-JGB-And-Euro-Area-Bonds.md`, 8 Oct duration follow-up.  
    **QUOTE:** "10-year equivalents fell 6.5%"  
    **UNCERTAIN:** The ¥ figures were not re-derived from the Bank of Japan’s by-issue file.

11. **CLAIM:** "The AI build-out is funded mostly from operating cash flow"  
    **VERDICT:** WEAKENED  
    **REASON:** Over mixed trailing twelve months, operating cash flow at the five large spenders was about $707bn against capex of about $586bn. Amazon’s operating cash flow was $11.6bn short of capex and Oracle’s was $28.8bn short. Alphabet’s purchase commitments alone are $811bn, and the project’s later lease total for commitments not yet commenced is $1,123bn. Trailing cash covering trailing capex is a different stock from those signed obligations.  
    **SOURCE:** `2026-09-12-F1-Funding-Table.md`, compact table; answer note §3a for the $1,122.9bn.  
    **QUOTE:** "The biggest commitments are not on any balance sheet"  
    **UNCERTAIN:** The cash-flow cells were not re-read from the 10-Qs. Fiscal year-ends differ across the six firms.

12. **CLAIM:** "The IPO boom is between half and two-thirds a single deal"  
    **VERDICT:** WEAKENED  
    **REASON:** SpaceX at $75.0bn is 67% of the $112bn in eight 2026 operating-company deals the project read, and about half of a $146bn Renaissance total the project says it did not verify. The $112bn census checked 26 of 212 non-SPAC filings and stops at 12 Sep 2026. The page is dated 17 Oct and does not say so.  
    **SOURCE:** `2026-09-12-I1b-IPO-Prospectus-Facts.md`, deal table and caveats.  
    **QUOTE:** "Discovery is not exhaustive"  
    **UNCERTAIN:** Deals after 12 Sep 2026 were not checked against a later full census. The $75bn share count was not re-read from EDGAR.

## The single weakest claim

The weakest line is the figure’s claim that the $46.9tn rise "splits" into new shares and a revaluation which then "splits" into earnings growth and a +0.87 price-earnings-point change. The 6.9/93.1 split is an identity on all US corporate equity plus foreign shares held here, a stock of $124tn that includes closely held firms and bond ETFs. The +0.87 points are the S&P 500 trailing multiple, and 71% of the +3.01 "premium" leg is the rate leg restated. A reader who does not already know Shapley arithmetic, or the sentence about dividing by an equilibrium quantity rather than a demand shift, cannot tell that this picture is two calculations joined by a dashed arrow. What survives on its own denominator: earnings are 71% of the S&P log price gain to Dec 2025 and 82% to Jun 2026; net issuance is 6.9% of the Z.1 level change; ETF creation is larger than that net issuance; the US 10-year did rise 113bp from 29 Dec 2023 to 18 Sep 2026, 96bp of it in the real par yield; and the page is right that no measured share of the price has been attributed to a flow.

## Not done

Shiller’s workbook, the Fed’s Z.1 bulk file, SEC companyfacts, Damodaran’s monthly ERP file, the Bundesbank Bund yield, and the 2023–26 rows of the Ministry of Finance JGB file were not re-read. FRED’s CSV endpoint returned an error. The Treasury par and real curves were used instead, and their December 2023 and June 2026 monthly averages match the project’s real-yield inputs exactly.

## Grok return: page attack, parcel B

I'll review the page section against the project's own evidence, starting with the local files and then the findings notes they cite.The page’s load-bearing numbers sit in a handful of findings notes. I’ll pull those and the data files they name, then check the figures that can be re-derived.The notes disagree with the page in a few places already. Next I’ll check the funding, IPO, and collateral write-ups, and the Fed series those numbers come from.The load-bearing identity in §03 re-sums. The sentences that rank channels, turn a 2015–25 ratio into the 2024–26 story, or say what carried the repricing do not.

Assumption: “the price rise” is the project’s Shiller composite from December 2023 to June 2026, and “2024–26” means 2024:Q1–2026:Q2 unless a sentence names another window. EFA figures are the project’s 18 September 2026 file, the vintage the page names. The live Fed CSV was not re-downloaded.

1. **CLAIM:** “ETF share creation +$3,603.8bn and operating companies −$540.7bn”  
   **VERDICT:** STANDS  
   **REASON:** Over 2024:Q1–2026:Q2, `etf_share_issuance_bn` sums to $3,603.8bn and `nfc_issuance_bn` to −$540.7bn, on total net issuance of $3,243.1bn. The hard sentence is “issuance net of the wrapper … understates … by about a third”: −$360.7bn versus −$540.7bn is (540.7−360.7)/540.7 = 33%, a different aggregate, not a corrected NFC print. ETF1’s own 2025 ICI-versus-Z.1 totals differ by $0.2bn, so “under $0.1bn” is tight.  
   **SOURCE:** `data/etf1/issuer_identity.csv` rows `FU564090005.Q`, `FU103164105.Q`; `data/etf1/quarterly.csv`  
   **QUOTE:** “ETF share issuance … 3603.814”  
   **UNCERTAIN:** Z.1 was not re-pulled from the Fed this session. A post-11 September 2026 vintage would settle it. The ICI workbook returned an error.

2. **CLAIM:** “Net new equity, mostly ETF share creation, was … 905 in 2024”  
   **VERDICT:** WEAKENED  
   **REASON:** The bars are all-issuer net issuance: $905bn, $1,164bn, and $1,174bn. ETF share creation was $1,145bn, $1,468bn, and $991bn. In 2024 creation exceeded the bar by $240bn; in 2026:H1 it was 84% of the bar ($991bn of $1,174bn) because ex-ETF issuance was +$183bn.  
   **SOURCE:** `data/etf1/quarterly.csv`, columns `total_issuance_bn` and `etf_share_issuance_bn`  
   **QUOTE:** “2024:Q1,96.300,226.474” through “2026:Q2,730.548,543.408”  
   **UNCERTAIN:** 2023’s $33.5bn bar is outside this file.

3. **CLAIM:** “Passive bid / ETF creation Dominant … an 82% offset”  
   **VERDICT:** WEAKENED  
   **REASON:** ETFs’ equity-holdings flow is $2,460.9bn and mutual funds’ equity flow is −$2,009.0bn, so 2,009/2,461 = 82%, and the net equity bid is $452bn. One quarter does the work: 2025:Q3 mutual funds −$521.5bn against ETF equity purchases of $223.9bn. Drop that quarter and the offset is 66%. Bond-fund creation was $1,065bn, 29.6% of the $3,603.8bn wrapper. “Dominant” is the issuance identity restated as where the money came from. The same-dollar rotation is graded unsettled.  
   **SOURCE:** `data/etf1/quarterly.csv` row 2025:Q3; `2026-09-15-ETF1-Identity-Net-Of-ETF.md`  
   **QUOTE:** “Consistent with rotation; not a measurement of it”  
   **UNCERTAIN:** How much of the $2,460.9bn was in-kind. Z.1 other-volume changes for 2025:Q3 would show whether that quarter was a conversion wave.

4. **CLAIM:** “Against those, buybacks were 5.3 times larger.”  
   **VERDICT:** WEAKENED  
   **REASON:** On the 18 September file, 2015–2025 repurchases are $6,228bn and IPO+SEO are $1,172bn, so 6,228/1,172 = 5.3×, and public offerings are 18.2% of gross issuance. The section’s own window, 2024:Q1–2026:Q2, is $1,935bn of repurchases over $473bn of IPO+SEO, which is 4.1×. Inside it, 2026:Q2 is $216.4bn of repurchases over $188.4bn of public offerings, 1.15×. The Fed calls IPO and SEO “select components” of gross issuance.  
   **SOURCE:** `data/vintages/efa/2026-09-18-equity-issuance-retirement-quarterly-historical.csv`; monthly file, 2015-01 through 2026-06; https://www.federalreserve.gov/releases/efa/efa-project-equity-issuance-retirement.htm  
   **QUOTE:** “select components of gross issuance, initial public offerings (IPO) and seasoned equity offerings (SEO)”  
   **UNCERTAIN:** Whether stock compensation and merger stock sit in the residual. The FEDS note’s methodology section would settle that.

5. **CLAIM:** “the rest was venture, private equity and private placements, which never become listed float”  
   **VERDICT:** WEAKENED  
   **REASON:** The shares are real on this vintage: 2026:Q1 public offerings are $38.98bn of $424.55bn gross, 9.2%, and 2026:Q2 is $188.44bn of $501.85bn, 37.5%. “Never” does not follow. The residual is whatever IPO+SEO do not itemise, and a private placement into a company that later lists, or a PIPE, can become listed float.  
   **SOURCE:** `data/vintages/efa/2026-09-18-equity-issuance-retirement-monthly-historical.csv`, 2026-01 through 2026-06; quarterly file rows 2026:Q1 and 2026:Q2  
   **QUOTE:** “2026:Q1, 45.35, 424.55” and June IPO “80.95”  
   **UNCERTAIN:** The share of the 91% residual that is a PIPE or a pre-IPO round. The Fed does not itemise it.

6. **CLAIM:** “Mostly self-funded … leases … $1,122.9bn, about 4.9×”  
   **VERDICT:** WEAKENED  
   **REASON:** On the funding table, Amazon’s operating-cash gap is $173.0bn − $161.4bn = $11.6bn and Oracle’s is $75.7bn − $46.9bn = $28.8bn, so three of five clear capex, and the five’s combined shortfall is $40bn on $586bn of capex. The same table shows about $297bn of new bonds. The $1,122.9bn sums leases not yet commenced, and Oracle’s leg in that sum is $260bn at 31 May 2026; the 31 August 10-Q, already read in the project, says $288bn. Replacing that leg makes $1,151bn, and 1,122.9/228.3 = 4.9× only on the older total. Those leases had not started, so they did not fund this window’s capex.  
   **SOURCE:** `2026-09-12-F1-Funding-Table.md` table; `2026-08-22-Guarantee-Stack.md`; `2026-09-12-Oracle-RPO-And-Financing.md`  
   **QUOTE:** “$288 billion … vs. $260 billion”  
   **UNCERTAIN:** Amazon’s $11.6bn and Microsoft’s $329bn lease were not re-read from the filings here. The 10-Qs would settle them.

7. **CLAIM:** “about $250bn of those commitments were already there in 2015”  
   **VERDICT:** WEAKENED  
   **REASON:** The Chicago Fed’s late-2025 figure is about $450bn committed and $150bn outstanding, and the 2015 level of the same buckets is about $250bn (9% of commitments then, 13% later). Those buckets are software, electric power, natural-gas distribution, and all semiconductor manufacturing. The article says there is no flag for which firms do AI. Software commitments went from $150bn in early 2022 to $191bn in late 2025. The same article puts data-center bank lending at $14.9bn over the year through 2025:Q3. “Already there” reads as the same loans; it is an industry total a decade earlier.  
   **SOURCE:** https://www.chicagofed.org/publications/chicago-fed-insights/2026/ai-tail-risk-for-banks  
   **QUOTE:** “not all companies in these industries have exposure to AI”  
   **UNCERTAIN:** None on the published article. The Y-14 microdata are not public.

8. **CLAIM:** “About $112bn of new company money in 2026 … about half” of “$146bn”  
   **VERDICT:** WEAKENED  
   **REASON:** The eight 2026-priced operating-company prospectuses sum to $111.9bn of primary proceeds, and SpaceX is $75.0bn, two-thirds of that sample. The note says 26 of 212 non-SPAC candidates were checked. Renaissance’s $146bn was not on a page fetched here, so “about half” (75/146) has an unstated denominator. June’s EFA IPO print is $80.95bn, above the $75bn base offer.  
   **SOURCE:** `2026-09-12-I1b-IPO-Prospectus-Facts.md`, deal table; monthly EFA row 2026-06-30  
   **QUOTE:** “Strictly 2026-priced only … $111.9bn”  
   **UNCERTAIN:** Renaissance’s universe, date, and whether the SpaceX greenshoe was exercised. The vendor page and an 8-K would settle it.

9. **CLAIM:** “even net of the handoff about a quarter of them”  
   **VERDICT:** WEAKENED  
   **REASON:** Handoff-adjusted wholesale growth from 2023-12 to 2026-03 is $858.6bn, and $858.6bn / $3,069.4bn of household wrapper purchases is 28%. The owning note says that ratio is a capacity ceiling through 2026:Q1, the last quarter with the hedge-fund leg, and says not to read it as a fraction of purchases funded. The 2024 repo handoff does stand: private money-fund repo +$540.6bn against the Fed reverse-repo facility −$586.3bn.  
   **SOURCE:** `data/n4/window_deltas.csv` row `N4_to_2026Q1`; `2026-09-15-N4-Scale-Timing-Bound.md`  
   **QUOTE:** “Do not read either ratio as a fraction of purchases funded.”  
   **UNCERTAIN:** None on the 28% arithmetic. The hedge-fund leg after March 2026 is unpublished.

10. **CLAIM:** “23.07% … in March 2026 and 22.96% in June, a plateau”  
    **VERDICT:** FALLS  
    **REASON:** March’s 23.074% is `z_W2_D1_pct`, wholesale funding over wholesale funding plus M2. The June W2 cell is blank because the hedge-fund leg is missing. The series that does print in June, W1, rose from 19.24% in March to 19.42% in June. “Stopped rising” is the opposite of the observed June print. A non-specialist cannot tell that “23.07% of wholesale funding plus M2” means W/(W+M2).  
    **SOURCE:** `data/n4/wholesale_path.csv` rows 2026-03 and 2026-06  
    **QUOTE:** “2026-06,5582.000,,19.4243,,”  
    **UNCERTAIN:** Whether correction C-130 reconstructs 22.96% and the $145bn M2 test. `CORRECTIONS.md` was not retrieved. That note, plus June M2, would settle it.

11. **CLAIM:** “Collateral re-use intensity did not rise.”  
    **VERDICT:** FALLS  
    **REASON:** Six-bank collateral permitted to be repledged, over the amount actually repledged, went from 81.7% at December 2025 (5,061.8/6,192.0) to 83.2% at June 2026 (6,149.6/7,389.7). The stock step is real: permitted collateral +19.3% in that half, and it is six banks, not large banks as a class. The timing clause is the part that holds: 78% of the Shiller rise from December 2023 ($4,685) to June 2026 ($7,450) was already in by December 2025 ($6,853). The index still rose 8.7% in the half of the step.  
    **SOURCE:** `2026-08-30-D10-Reuse-On-The-Measured-Chain.md` §2 and §6; `data/p2a_decomposition/decomp_annual.csv` rows 2023, 2025, 2026_YTD  
    **QUOTE:** “Six-bank Jun-26 utilization: 83.2% (6,149.6 / 7,389.7)”  
    **UNCERTAIN:** December 2025’s 81.7% is the sum of the note’s five-bank total and Wells Fargo. A single six-bank table in the 10-Qs would settle it. Singh velocity is a different, unsigned series.

12. **CLAIM:** “they are not what carried this repricing”  
    **VERDICT:** FALLS  
    **REASON:** That sentence says these flows carried, or did not carry, the price. The project’s own rule bars a flow-causes-price claim, including this negative one. The deposit stock at 6.3× household wrapper purchases ($19,384bn / $3,069bn) is a capacity. The association behind “small positive” is r = 0.263, R² = 6.9%, and the note says it misses ordinary significance. The rotation the paragraph treats as the money is the offset in claim 3, which the project marks unmeasurable.  
    **SOURCE:** `page_B.txt` §04 closing; `2026-09-14-A1-Money-Creation-Link.md`; `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md` §5  
    **QUOTE:** “Any scalar M; any statement that flows caused a specific share of the repricing”  
    **UNCERTAIN:** None on the wording. The deposit stock was not re-read from H.8 here.

## The single weakest claim

The weakest sentence is the closing one: the money that bought equities “was mostly already inside the system” and these channels “are not what carried this repricing.” It is easy to read, and it is the sentence that turns the section into an explanation of the price. The measurements will not carry that explanation. After mutual-fund sales, the equity bid from ETFs is $452bn, and 2025:Q3 alone (−$522bn of mutual-fund equity against $224bn of ETF equity purchases) produces the 82% offset. Bond ETFs are $1,065bn of the wrapper. The shadow-money figure of about a quarter is $859bn of capacity through March 2026 divided by $3,069bn of household purchases of the wrapper, and the owning note says that ratio is not a funded share. The deposit multiple, 6.3×, says existing balances were large enough. It does not say they were the money that bought the shares. A reader who stops at “Dominant,” “mostly self-funded,” and “not what carried this repricing” leaves with a causal ranking the page’s own files do not support.

## NOT DONE

The live Federal Reserve EFA CSV was not re-downloaded; the sums use the project’s 18 September 2026 copy, and the Fed’s project page was fetched only for the series definition. The ICI Fact Book workbook returned an error, so the $0.2bn 2025 gap is ETF1’s table. Correction C-130 was not opened, so 22.96% and the $145bn M2 test are unchecked against that note. Renaissance Capital’s $146bn page was not fetched. Amazon, Microsoft, Meta, and Alphabet lease footnotes, and the Beignet N-PORT, were not re-read. The 2023 bars in the figure ($33.5bn, $400bn, −$603bn) are outside `quarterly.csv`. FRED’s S&P file returned an error; the price path is the project’s Shiller file. The in-kind share of the $2.46trn ETF equity flow is not in the files. Two EFA nets for the same window both re-sum and differ: EFA net retirement $552.1bn versus Z.1 nonfinancial −$540.7bn, an $11.3bn gap the page states only for 2026:Q1 ($45.4bn versus $51.3bn).

## Grok return: page attack, parcel C

I'll review the page section against the project's own evidence, starting with the two files in this folder and then the findings notes they name.The rates section hangs on a handful of findings notes. I'll pull those next and check the numbers they actually own.The notes already flag several soft spots. Next I’ll re-derive the sharpest figures from the project’s data files and from official series.The rates section’s sharpest problem is a window problem. Several headline moves are real endpoint-to-endpoint, and several of those endpoints hide a round trip, a later sample, or a different denominator.

## 1. Claims

**CLAIM:** "expected rates for the next four years fell"  
**VERDICT:** FALLS  
**REASON:** That agreement is the 2024Q1–2026Q1 surveys, when the 10-year par yield fell 4bp and the SPF’s four-year bill rate fell 54bp. From the 2026Q1 survey to the 2026Q3 survey that bill rate rose 35bp, against a 65bp rise in the 10-year (ACM’s four-year expected rate +58bp, Kim-Wright +47bp). On 27 Feb 2026 the 10-year was 3.97%, 9bp above the 3.88% start, so nearly all of the +113bp sits in the stretch where the four-year expectations rose. R1 grades this split HYPOTHESIS; the page states it as what moved the yield.  
**SOURCE:** `data/r1_rates/survey_changes.csv` (rows 2024Q1–2026Q1 and 2026Q1–2026Q3); `data/swap_tape/ust_used.csv` row 2026-02-27  
**QUOTE:** "the SPF's four-year average rose 35bp"  
**UNCERTAIN:** The arithmetic is in the files. The page never names the survey dates, so tying the sentence to the +113bp is a reading of where it sits. Printing the two survey windows on the page would settle that reading.

**CLAIM:** "3.88% → 5.01%, +113bp to 18 Sep"  
**VERDICT:** WEAKENED  
**REASON:** The endpoints match the project’s curve: 5.01% and a 2.68% real yield on 18 Sep 2026, and 5.01% / 4.76% / 4.86% / 5.34% match a Treasury-cited report for that day. Inside the window the 10-year was 3.97% on 27 Feb 2026 and the 10-year real yield was 1.72%, the same as 29 Dec 2023, so the entire TIPS +96bp is the next seven months. 2025 alone was −40bp.  
**SOURCE:** `data/r1_rates/levels.csv`; `data/swap_tape/ust_used.csv` rows 2026-02-27 and 2026-09-18; https://statisticsoftheworld.com/news/2026-09-18  
**QUOTE:** "closed at 5.01% on 18 September 2026"  
**UNCERTAIN:** 29 Dec 2023 (3.88% and real 1.72%) was not re-read from treasury.gov this session. FRED returned an error.

**CLAIM:** "about 36% more rate risk at constant yields"  
**VERDICT:** WEAKENED  
**REASON:** Constant-price 10-year equivalents held by the public rose from $9,539bn to $12,943bn, +$3,404bn, which is 35.7%. On the same securities, DV01 rose 20.0% and par-weighted duration 21.3% on each date’s curve and 24.7% on the end-2023 curve, against a 26.4% rise in face value. Modified duration per face dollar fell from 4.22 years to 4.05 years. The 36% is the project’s own high weighting: on the low end-2023 curve, new high-coupon bonds are priced above par.  
**SOURCE:** `data/r2_rates/duration_supply.csv` rows 2023-12-31 and 2026-08-31; `2026-09-27-R2-Treasury-Duration-Supply-And-Holders.md`  
**QUOTE:** "counts that premium as extra rate risk"  
**UNCERTAIN:** No published duration series exists to check the 35.7% against. The project’s `checks.csv` tests par and Fed holdings, not duration.

**CLAIM:** "Fed's share is 4% to at most about 13%"  
**VERDICT:** WEAKENED  
**REASON:** The Fed’s own constant-price 10-year equivalents fell $142bn, 4.2% of the public’s +$3,404bn. The 13% is a different object: $0.32–0.43trn if the Fed’s runoff had been refinanced in the coupon mix of those months. The project’s own follow-up says Treasury does not publish those replacement maturities, so the 13% "stays a counterfactual about total issuance, not a datum." The 4% also nets a 2024 decline of $199bn against later increases.  
**SOURCE:** `data/r2_rates/duration_supply_changes.csv`, row end-2023 to 31 Aug 2026; R2 follow-up of 8 Oct 2026  
**QUOTE:** "a counterfactual about total issuance, not a datum"  
**UNCERTAIN:** The refunding statements were not re-read here. The 9–13% range is Grok’s calculation inside R2, not a row in `duration_supply.csv`.

**CLAIM:** "in the US a household line that is likely to be largely offshore hedge funds"  
**VERDICT:** FALLS  
**REASON:** On the project’s Z.1 flows for 2024–2026Q2, households bought $459bn of $4,652bn of net issuance, while the rest of the world bought $1,325bn and money funds $1,012bn. The Fed’s $1.4trn is the end-2024 stock gap between Form PF and TIC for Cayman funds, which Z.1 then drops into the household residual. That stock wedge is a different denominator from the $459bn flow, and the household flow was −$14bn in 2026Q1.  
**SOURCE:** `2026-09-12-N2c-Closure-Refresh-2026Q2.md`, Treasury absorption table; https://www.federalreserve.gov/econres/notes/feds-notes/the-cross-border-trail-of-the-treasury-basis-trade-20251015.html  
**QUOTE:** "$1.4 trillion at the end of 2024"  
**UNCERTAIN:** The FEDS note does not print the published household Treasury stock, so whether $1.4trn is most of that stock is open. Figure 4a’s level would settle "largely."

**CLAIM:** "¥138trn of 10-year equivalents, about 1.7 times"  
**VERDICT:** WEAKENED  
**REASON:** Public fixed-curve 10-year equivalents rose from ¥558.0trn to ¥696.5trn, +¥138.5trn, and total supply rose ¥82.8trn, so 138.5/82.8 = 1.67. The end-2023 stock is marked ESTIMATED. On each date’s own curve the public’s 10-year equivalents fell 6.5%, from ¥558.0trn to ¥521.8trn. The page’s 16% and 25% are the Oct 2024 start and the end-2023 start, two windows on the curve that most inflates long bonds.  
**SOURCE:** `data/r3_rates/jgb_duration_changes.csv`, headline row and observed-only row  
**QUOTE:** "public's 10-year equivalents fell 6.5%"  
**UNCERTAIN:** The unpriced 11–18% was not recomputed from `jgb_duration_issues.csv` in this pass.

**CLAIM:** "Mostly real over the window"  
**VERDICT:** WEAKENED  
**REASON:** In 2026 the 6.6-year linker’s breakeven rose 48.5bp and the 19.6-year’s 34.2bp, against the Bund’s +68bp, while the 3.6-year linker rose 69.9bp, more than the nominal Bund. The page’s 34–49bp range leaves that bond out. The 2024–25 breakeven fell 21bp and then rose, and R3 marks the full-window real share as inferred because linker issuance stopped in 2024.  
**SOURCE:** `data/r3_rates/ea_linkers.csv`; `data/r3_rates/ea_levels.csv` (Bund 2.94 on 2025-12-31 to 3.62 on 2026-09-24)  
**QUOTE:** "the 3.6-year's rose 70bp"  
**UNCERTAIN:** The 2024–25 −21bp was not recomputed from the Bundesbank daily files here. It is the project’s 8 Oct measurement in R3.

**CLAIM:** "holdings fell €751bn; banks bought €725bn"  
**VERDICT:** WEAKENED  
**REASON:** The file shows Eurosystem −€750.9bn, banks +€725.1bn, and the rest of the world +€829.9bn, on face value from 2023Q4 to 2026Q2. The rest-of-world line is "total outstanding minus all euro-area holders." The Eurosystem share went from 3,419.6/10,984.7 = 31.1% to 2,668.8/12,634.5 = 21.1%. The Bund then rose from 2.93% on 30 Jun 2026 to 3.62% on 24 Sep, +69bp of the +156bp, after those stocks stop.  
**SOURCE:** `data/r3_rates/ea_holders.csv`; `data/r3_rates/ea_levels.csv`  
**QUOTE:** "total outstanding minus all euro-area holders"  
**UNCERTAIN:** None on the arithmetic. Whether face-value stock changes equal market purchases, after Bulgaria’s entry, is the project’s own bound of about €25bn.

**CLAIM:** "Holders lost against cash in all three"  
**VERDICT:** WEAKENED  
**REASON:** The full-window figures match the files: US +3.54% against three-month bills +12.91%, Germany −4.67% against one-year paper +6.87%, Japan −13.86% against +1.65%. In 2025 the US 10-year returned +8.30% against bills at +4.32%. Germany’s −4.67% is the last quarter (−4.84%); through 30 Jun 2026 the Bund was +0.17%. The US public’s modified duration was 4.05 years, not 10.  
**SOURCE:** `data/r1_rates/holder_return_periods.csv`; `data/r3_rates/ea_holder_return.csv`; `data/r3_rates/jp_holder_return.csv`; `data/r2_rates/duration_supply.csv`  
**QUOTE:** "2025 full revaluation +8.30 against bills +4.32"  
**UNCERTAIN:** These are rolled par bonds, not a published total-return index. Japan’s −13.9% was not checked against the NOMURA-BPI index here.

**CLAIM:** "about 25bp from its purchase cuts"  
**VERDICT:** WEAKENED  
**REASON:** Bank of Japan Review 2026-E-10 says expected rates and the term premium contributed "roughly the same degree" from summer 2024 through its sample, and that purchase cuts contributed about 25bp (about 10bp from the stock), which it calls relatively small and a simple regression to be read with latitude. Chart 3 is as of end-June 2026, when the 10-year was 2.69%, before the page’s move to 3.07%. This sentence says a purchase cut caused a yield change. The charter forbids that reading. The later line that supply has not been shown to move yields does not cancel it.  
**SOURCE:** https://www.boj.or.jp/en/research/wps_rev/rev_2026/data/rev26e10.pdf; `data/r3_rates/jp_levels.csv` row 2026-06-30  
**QUOTE:** "appears to be relatively small to date"  
**UNCERTAIN:** None on the 25bp sentence in the PDF. The equal split’s exact basis-point legs are in Chart 3, which the text conversion does not tabulate.

A non-specialist cannot follow "10-year equivalents," "the line set in advance for a first-order holder ($460bn…)," or "The Z.1 household row is likely to be largely offshore hedge funds that TIC misses," and the C-122 / R2b tags are internal codes.

## 2. The single weakest claim

The weakest sentence is the one that puts the +113bp on a fall in expected rates over the next four years, with the argument turning on years five to ten. That fall is real for one survey pair: from the February 2024 survey to the March 2026 survey, the SPF’s four-year bill rate fell 54bp, ACM’s four-year expected rate 118bp and Kim-Wright’s 72bp, and over those same dates the 10-year par yield fell 4bp. From the March 2026 survey to the August 2026 survey all three rose (SPF +35bp, ACM +58bp, Kim-Wright +47bp) while the 10-year rose 65bp, and years five to ten rose in both models (+39bp and +19bp). The project’s own Treasury curve puts the 10-year at 3.97% on 27 Feb 2026, with the real yield back at its 29 Dec 2023 level of 1.72%. What survives is narrower: over the full window ACM puts +97bp of its +107bp fitted move on the term premium and Kim-Wright +87bp of +109bp, and over 2024Q1–2026Q1 the surveys and the models disagree on years five to ten (SPF +61bp, ACM −56bp, Kim-Wright −8bp). Both of those are endpoint model results. R1 already marks the split HYPOTHESIS.

Elsewhere the dated levels stand: US 3.88% to 5.01% (+113bp) with TIPS +96bp and breakeven +17bp adding up; Japan 0.647% to 3.073% (+243bp); the Bund 2.06% to 3.62% (+156bp). The Fed’s own constant-price duration fell 4.2% of the public’s constant-price increase. The $1.4trn end-2024 TIC shortfall for Cayman funds is the Fed’s figure. Registered funds’ $549bn of $3,218bn (17.1%) versus $450bn scaled, and the "not established" verdict, match `tsy_verdict.csv`; in 2026H1 their share was 29.2% on filings and 22.6% scaled, against a starting share of about 15%. Japan’s Flow of Funds totals (−¥63.0trn, banks +¥54.7trn, public pensions +¥32.3trn, overseas +¥23.7trn) and the euro-area face-value changes match the files. The holder-return arithmetic matches. ST1’s −38.9bp and −65.2bp on 13 Oct 2026 are what the page rounds to 39bp and 65bp, and the Treasury borrowing advisers’ −53bp in July 2025 is the outside check the project recorded. The page’s own line that none of this shows supply moved yields is the part that fits the charter.

## 3. Not done

The 29 Dec 2023 Treasury curve was not re-read from treasury.gov; FRED returned HTTP 500. The refunding statements behind "auction sizes held constant" were not re-read. The Fed’s 9–13% coupon-refinance range was not rebuilt from SOMA files. The Cleveland Fed’s +25bp versus the TIPS breakeven’s +17bp is R1’s note, not a workbook pulled here. The JGB unpriced 11–18% was not recomputed from the issues file. Gross BoJ purchases versus outright sales were not split; the −¥63trn is a net transactions total. The ECB Economic Bulletin 6/2026 was not fetched, so "largely higher real term premia" was not checked against the ECB’s text. `data/swap_tape/summary.csv` counts 199 CMT dates and a 10-year day-to-day sample of 191, which does not match ST1’s 498 days and 469 pairs; the 13 Oct inflation gap (page 14bp, ST1’s early-October monthly median about +13bp) was not recomputed from `ledger_2026.csv`. The published Z.1 household Treasury stock, which would show whether the $1.4trn gap is most of that row, is not in the FEDS note text fetched here.

## Grok return: page attack, parcel D

I'll review the page section against the evidence note and the project's own data, starting with the files in this folder.The page and the evidence note disagree in a few places already. I'll pull the findings notes that own the sharpest numbers and check those against the data.The ledger mixes identities, ceilings, and window endpoints. I'll read the notes that own the retirement net, the 93 percent residual, the earnings share, and the bridge arithmetic.The retirement net and the 93 percent residual are the first places a denominator can lie. Next I’ll check the rates, supply, and earnings notes, and the primary series those numbers come from.The 113bp Treasury rise is real on the dates named, and it is measured from the bottom of the prior rally. The retirement “corrected” net and the Gabaix–Koijen 10.9 and 15 are in worse shape.

## 1. Claims

**CLAIM:** "The US 10-year rose 113bp, almost all of it in real yields"  
**VERDICT:** WEAKENED  
**REASON:** Treasury par yields go from 3.88% on 29 Dec 2023 to 5.01% on 18 Sep 2026, and the 10-year real yield from 1.72% to 2.68%, so +96bp real and +17bp breakeven do add to +113bp. The window starts at the bottom of a rally: on 19 Oct 2023 the 10-year was 4.98% and the real yield 2.49%, so from that peak the nominal rise is +3bp and the real rise is +19bp. Inside the window the yield fell from 4.58% at end-2024 to 4.18% at end-2025, and 97bp of the 113bp came after 13 Feb 2026, when it was 4.04%.  
**SOURCE:** Treasury daily nominal and real curves, 2023 and 2026 (https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2023/all?type=daily_treasury_yield_curve&field_tdr_date_value=2023&page&_format=csv and the 2026 nominal file, plus both real-curve files); project `data/r1_rates/levels.csv`.  
**QUOTE:** "Measured from that October peak, the rise is 3bp."  
**UNCERTAIN:** The Cleveland Fed’s roughly +57bp model real rate, versus TIPS +96bp, is taken from R1 and was not re-read from the Cleveland workbook.

**CLAIM:** "The earnings yield barely moved while real yields rose 34bp"  
**VERDICT:** WEAKENED  
**REASON:** On the project’s monthly series the earnings yield goes from 4.11% in Dec 2023 to 3.96% in Jun 2026, a net −14bp, while average 10-year TIPS go from 1.84% to 2.18%, +34bp. Inside that window the earnings yield fell 61bp in 2024 and rose 45bp in the first half of 2026; the premium compressed 86bp in 2024, then widened 20bp in 2025 and 17bp in the first half of 2026. The +34bp is a change in monthly averages. Treasury point prints over the same equity window rise 48bp, from 1.72% on 29 Dec 2023 to 2.20% on 30 Jun 2026, because December 2023’s average sits well above the 29 Dec print. The ledger’s “real-rate leg −2.14 P/E pts; premium leg +3.01” matches the trailing Shapley split; on cyclically adjusted earnings the premium leg is +13.44 points, not +3.01. “71% of the premium leg is the rate rise” is the definition premium = E/P − real yield (34bp of a 49bp compression), and a non-specialist cannot see that from the sentence.  
**SOURCE:** `_research/2026-09-12-P2c-decomposition_annual.csv` and `decomposition_windows.csv`; Treasury real curve, dates above.  
**QUOTE:** "The path was 24.35, 28.60, 28.48, 25.22. Quote the path."  
**UNCERTAIN:** The 1.84% and 2.18% figures are the project’s monthly means of FRED DFII10. The daily Treasury file confirms the path; the monthly average itself was not recomputed day by day.

**CLAIM:** "only the two highest aggregate specifications in Gabaix and Koijen reach (10.9 and 15"  
**VERDICT:** FALLS  
**REASON:** In the June 2021 NBER paper the authors say their estimates lie between $3 and $8, and they use about $5. Table 2’s granular-IV estimates are 7.1 and 5.3; the robustness range they report is 3.5 to 8. Table 3’s 10.93 is the column with only GDP as a control, which they say they do not recommend; with the factors they do recommend, the estimate is about 7.6 to 7.7. The 15 in that paper is the “prima facie” trade-level multiplier from Frazzini and Bouchaud, which they separate from their own macro estimate. At the headline of about 5, the page’s own scaling needs about 56 years, and none of the specifications the authors endorse clears M≈11 on 11.7 years. The 386-year figure at M≈1.9 is just that algebra: 1.9 × 1.32bp against 111bp of daily noise.  
**SOURCE:** Gabaix and Koijen, NBER w28967, June 2021, https://www.nber.org/system/files/working_papers/w28967/w28967.pdf, introduction, Table 2, Table 3, and the footnote on the microstructure 15; page section 06; `2026-09-16-TierB-E005-Resolution-Limit.md`.  
**QUOTE:** "our estimates are between $3 and $8"  
**UNCERTAIN:** A February 2023 revision was not opened. A later draft could contain a 15. The NBER PDF fetched here does not.

**CLAIM:** "IRA withdrawals of 475 billion are the real exit"  
**VERDICT:** FALLS  
**REASON:** $475.0bn is traditional-IRA withdrawals in 2023, not all IRA withdrawals and not money that necessarily left markets. The same table shows $652.8bn rolled into traditional IRAs that year, so withdrawals offset about three-quarters of the gross rollover, and $36.7bn of Roth conversions are inside the traditional account, not an exit from savings. Defined-contribution benefits that are spent rather than rolled are a second exit the $475bn does not include. ICI’s September 2026 release puts IRA assets at $19.9trn and defined-contribution assets at $15.0trn in June 2026.  
**SOURCE:** `2026-09-12-Parcel-RET1-Retirement-Flows-Return.md`, Table 2, traditional IRA 2023 row, supervisor check against ICI Table 11; https://www.ici.org/statistical-report/ret_26_q1.  
**QUOTE:** "Benefits disbursed are mostly not spent."  
**UNCERTAIN:** RET1’s $515.2bn for all IRA types is its own sum across tables and is marked uncertain there. The ICI workbook was not opened this session.

**CLAIM:** "headline net of minus 16.1 billion becomes minus 90.7"  
**VERDICT:** FALLS  
**REASON:** The subtraction is exact and one-sided. DOL defined-contribution contributions of $767,581m minus “Contributions From Others (Including Rollovers)” of $74,607m, minus benefits of $783,697m, equal −$90,723m. That removes a contaminated inflow and leaves the benefit line, which the same note says is mostly rollovers into IRAs, so the “correction” makes the net more negative. The $74.6bn line is “including rollovers,” not rollovers alone. Employer plus participant contributions are $691.3bn; the page’s “$693bn of genuinely new money” also picks up $1.7bn of noncash contributions.  
**SOURCE:** RET1, DOL 2023 Abstract components, supervisor-checked on `dol_abstract_2023.xlsx` sheet 8.  
**QUOTE:** "organic DC net flow is −$90,723M, not the −$16,116M headline"  
**UNCERTAIN:** How much of the $74.6bn is rollovers rather than other contributions is not separated in the table that was read.

**CLAIM:** "net DC contributions have been negative every year since 2013"  
**VERDICT:** WEAKENED  
**REASON:** On ICI’s private-sector defined-contribution table the nets shown for 2014–2023 are all negative, and 2023’s −$16.3bn was checked against the workbook. The broader DOL total was +$4.0bn in 2016. “After transfers” reads as if transfers were removed; RET1 says both legs are still contaminated and that the net is not a measure of money entering or leaving equities. The flow series stops in 2023, before the 2024–26 price window. Calling that streak “starker than the claim it was meant to test” puts the contaminated plan-level net back in the green ledger.  
**SOURCE:** RET1 Table 1, ICI versus DOL columns, and the warning at the top of that note.  
**QUOTE:** "NOT a measure of money entering or leaving the equity market."  
**UNCERTAIN:** 2013 itself is not in the table that was read, which starts in 2014. The 2016 DOL plus sign is RET1’s subtraction, not a re-read of the DOL PDF this session.

**CLAIM:** "Operating companies retired $541bn of equity net, 2024–26"  
**VERDICT:** WEAKENED  
**REASON:** Z.1 nonfinancial net issuance over 2024:Q1–2026:Q2 is −$540.7bn, on an instrument that mixes public and closely held firms. The Enhanced Financial Accounts net is a different series, −$552bn, and the page’s own unresolved row is +$45.4bn versus +$51.3bn for 2026:Q1. Inside the window the cumulative retirement shrinks: through 2025:Q4 net retirement was about $749bn, then 2026:Q1 net issuance was +$45.4bn and 2026:Q2 was +$151.95bn on the later vintage. Gross retirement of $2,979bn is about 65% repurchases ($1,935bn / $2,979bn), but that issuance leg includes private placements while repurchases are public firms, which is the mismatch already used to retract the “fully offset” line. Grading the combined gross line Measured hides that.  
**SOURCE:** `2026-09-15-ETF1-Identity-Net-Of-ETF.md`; `2026-09-13-S1-Supply-Decomposition.md`, 9 Oct and 11 Oct updates; the evidence note’s supply section.  
**QUOTE:** "Net issuance turned positive in 2026, so the window's net retirement is shrinking."  
**UNCERTAIN:** The $2,979bn, $2,427bn, and +$151.95bn were not re-summed from the Fed’s quarterly CSV this session.

**CLAIM:** "Three of the five large AI spenders out-earn their capex"  
**VERDICT:** WEAKENED  
**REASON:** On the funding table, operating cash exceeds capex for Alphabet ($185.7bn vs $132.4bn), Meta ($130.3bn vs $89.3bn), and Microsoft ($182.9bn vs $115.9bn). Amazon’s operating cash is $161.4bn against capex of $173.0bn, and Oracle’s is $46.9bn against $75.7bn. “Out-earn” names profit; the comparison is operating cash, which adds back depreciation. The $1,122.9bn of leases not yet commenced is Meta $279.0bn + Microsoft $329.1bn + Oracle $260bn + Amazon $137.2bn + Alphabet $85.2bn + NVIDIA $32.4bn, six ASC 842 footnotes on three different dates, and it is every such lease, not an AI-only subset. Alphabet’s own 2026 capex guide is $180–190bn against $132bn trailing.  
**SOURCE:** `2026-09-12-F1-Funding-Table.md`, compact table; `2026-08-22-Guarantee-Stack.md`, ASC 842 sum.  
**QUOTE:** "Only Oracle cannot fund its own capex from operations"  
**UNCERTAIN:** The six lease footnotes were not re-read at EDGAR. How much of Microsoft’s $329bn is data-center capacity would settle the AI share. F1’s own prose still says only Oracle fails, which its Amazon row contradicts; the page’s “three of five” matches the table, not that prose.

**CLAIM:** "2024's expansion arrived as drift, not on scheduled news"  
**VERDICT:** WEAKENED  
**REASON:** The object is the change in trailing P/E, +3.20 points, and quarter-boundary earnings steps summed to −2.83 points, so the price-driven move ex-artefact is +6.03 points. At the [−1,+1] window, FOMC days are 9.5% of days and +25.6% of the P/E change, while earnings days are −34.7%. At [−1,+5], earnings carry +42.4% and the FOMC +48.4%. “FOMC beats earnings head-to-head” is the tight window. Ordinary days do carry the bulk; that does not identify a flow.  
**SOURCE:** `2026-09-14-P5i-Event-Study-Result.md`, the head-to-head table.  
**QUOTE:** "ordinary days alone carry +183% of the total move."  
**UNCERTAIN:** The day shares were not recomputed from the daily file.

**CLAIM:** "Buybacks are at most ~7–13% of the gain"  
**VERDICT:** WEAKENED  
**REASON:** The 7.1–13.4% band is four weightings of current S&P 500 constituents, 385 of 500 usable, missing Alphabet, Berkshire, Tesla, and Broadcom. The 13.4% is the top of that band, and the findings note says survivorship pushes every weighting up, so the band is not a demonstrated ceiling. The share index rose in 2024, from 0.8938 to 0.9045, before falling to 0.8717 in 2025. “Profit + composition at least ~69–75%” is 100 minus the 17.7% multiple minus that same biased accretion band, not a second measurement.  
**SOURCE:** `2026-09-18-EPS-Split.md`, weighting band, share-index table, and the C-093 banner.  
**QUOTE:** "the 13.4% below is the top of the doc's own 7.1–13.4% weighting band"  
**UNCERTAIN:** The firm panel was not re-derived from SEC companyfacts this session. A back-dated 2015 constituent list would settle the survivorship gap.

**CLAIM:** "The US public absorbed ~36% more rate risk at constant yields"  
**VERDICT:** WEAKENED  
**REASON:** Public 10-year equivalents on the end-2023 curve go from $9,539bn to $12,943bn, which is +35.7%, from end-2023 to 31 Aug 2026. Face value rose 26.4%, from $21,576bn to $27,278bn. DV01 rose 20%, and par-weighted duration on each date’s own curve rose 21.3%. Modified duration per face dollar fell from 4.22 years to 4.05. The constant-price measure runs ahead of face value because higher-coupon new issues are priced above par on the old, lower curve. “36% more rate risk” is the top construction. The per-dollar caveat is on the page; the DV01 and the coupon premium are not.  
**SOURCE:** `2026-09-27-R2-Treasury-Duration-Supply-And-Holders.md`, the 10-year-equivalent and DV01 tables.  
**QUOTE:** "Per face dollar, the debt did not get longer."  
**UNCERTAIN:** No published duration series was found to check the 10-year equivalents against; R2 says its checks match face and bills, not duration.

**CLAIM:** "30-year TIPS rose more than 10-year"  
**VERDICT:** STANDS  
**REASON:** On the Treasury real curve the 30-year goes from 1.90% on 29 Dec 2023 to 3.09% on 18 Sep 2026, +119bp, and the 10-year from 1.72% to 2.68%, +96bp. From the 19 Oct 2023 peak the 30-year still rose more: 2.55% to 3.09% is +54bp, against +19bp for the 10-year. The comparison is not an artefact of starting at the December trough.  
**SOURCE:** Treasury daily real yield curve, 2023 and 2026 files cited above.  
**QUOTE:** "+119bp vs +96bp, end-2023 to 18 Sep 2026"  
**UNCERTAIN:** None on these two dates. The cross-check to H.15 named on the page was not fetched separately; the Treasury real curve is the primary file.

## 2. The single weakest claim

The weakest claim is the retirement correction: that stripping rollovers turns a −$16.1bn defined-contribution net into −$90.7bn, that $475bn of IRA withdrawals are “the real exit,” and that what survives is starker than the story under test because net defined-contribution contributions have been negative every year since 2013. The −$90.7bn deletes only the inflow labelled “Contributions From Others (Including Rollovers),” $74.6bn, and leaves $783.7bn of benefits in the outflow, even though the same note says most of that benefit line rolls into an IRA. The $475bn is one gross withdrawal line for traditional IRAs in 2023, set beside $652.8bn of rollovers into those same IRAs, and the $652.8bn is not a subset of the $731.9bn private-sector defined-contribution benefit figure it is compared with. The “every year since 2013” streak is an ICI private-sector sign count through 2023, while the DOL total was positive in 2016, the words “after transfers” suggest the transfers are gone, and the flow record stops before the 2024–26 window in which retirement assets were still rising. No live sentence in these three sections says a flow caused a price. Section 06 says the closed tests do not show that money failed to move prices either.

What still stands is narrower than the ledger’s green rows. The Dec 2023 to 18 Sep 2026 Treasury subtraction, 3.88% to 5.01%, with real +96bp and breakeven +17bp, is an identity on those dates, and the 30-year real yield did rise more than the 10-year. Z.1’s −$540.7bn for nonfinancials and +$3,603.8bn for ETF shares are the issuer lines; ICI matches 2024 to the dollar and 2025 to $0.2bn, which is not “under $0.1bn,” and 2026 is outside that annual match. The log earnings split, 71.0% to Dec 2025 and 82.3% to Jun 2026, follows from the Shiller endpoints the project cites, and it is an identity in price, earnings, and the multiple, not a separate cause. The Russell assignment t of 1.61 is an F of about 2.6. The return-power ratio of 0.48 is 1.097pp over a predicted 0.528pp; the idiosyncratic ratio in the same gate is 0.90, so “only 0.48” and “twice the size” describe the noisier specification.

## 3. Not done

The 2013 ICI row, the DOL historical PDF for 2016, and the ICI retirement workbook were not opened; the asset release at https://www.ici.org/statistical-report/ret_26_q1 has levels, not the 2023 flow rows. The Enhanced Financial Accounts quarterly file was not re-summed, so the $2,979bn, $2,427bn, and 2026:Q2 +$151.95bn rest on S1 and the evidence note. German linker and JGB breakeven levels were not re-read from the Bundesbank, the Finanzagentur, or the Ministry of Finance. The six lease footnotes and the EPS-split companyfacts panel were not re-read at the SEC. FRED returned an error; Treasury’s own curves were used instead. The February 2023 Gabaix–Koijen revision was not fetched. No sentence-by-sentence pass was made on sections outside 06–08.

## Grok return: page attack, parcel E

I'll review the page section against the evidence note and the project's own data, starting with the local files.The page’s sharpest numbers sit in the gaps, the queue, and the confidence grades. I’ll pull the findings notes that own them and check those figures against the sources.The root listing is long and the code search needs auth. I’ll pull the findings notes that own the page’s numbers, and the recent commits that added the October queue items.The Treasury file that came back stops in early 2023, so I’m checking whether the 2026 prints exist at the source and pulling the project tables that can be re-added.The 10-year yield was unchanged across August, so the Japan adjustment is the claim that fails. Eleven other sentences in sections 09–12 were checked against the findings notes and the primary prints that could be opened.

## 1.

**CLAIM:** “Of the 49bp, 36–60% is not explained by growth expectations”
**VERDICT:** FALLS
**REASON:** 17.4/48.59bp and 29.31/48.59bp are only two restatements of Damodaran’s equity-risk-premium change. The same note says a control-window sensitivity lets growth explain more than the whole 49bp, so 36% is not a floor. A non-specialist cannot tell 49bp of what.
**SOURCE:** [P5ii](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-13-P5ii-Growth-Versus-Risk.md), C-104 re-run
**QUOTE:** “cannot rule out mostly or entirely growth”
**UNCERTAIN:** No. The third premium series named on the page would be a new test, not a repair of this one.

**CLAIM:** “recorded holdings fell about 0.4 dollars per dollar”
**VERDICT:** FALLS
**REASON:** The 10-year par yield was 4.75% on both 31 July and 31 August 2026, so the price did not rise. Coupon on $1,103.9bn at 4.75% is about $4.4bn, not a $4.8bn mark-to-market gain; adding it turns −$35.6bn into −$40.4bn and produces the 0.41–0.43 ratio. The recorded ratio on the pre-registered $94.5–98.3bn intervention is about 0.36–0.38.
**SOURCE:** [Treasury August 2026](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202608) and [July 2026](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202607); [E-021](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-10-12-E021-Where-The-Money-Comes-From-Rates-FX-Commodities.md)
**QUOTE:** “0.41–0.43 dollars of adjusted sales”
**UNCERTAIN:** The raw $1,103.9bn and $1,068.3bn. `mfh.txt` still served a March 2023 vintage. The R1 code would show whether $4.8bn was meant as coupon.

**CLAIM:** “the ETF figure matched by an independent census”
**VERDICT:** FALLS
**REASON:** The findings note says the Fed ETF table is the ICI census inside Z.1. 2024 issuance matches at $1,144.8bn on both sides, and the 2026:Q2 stock matches at $15,702.3bn to $0.1bn. That is one source copied, on a $15.7trn denominator.
**SOURCE:** [ETF1](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-15-ETF1-Identity-Net-Of-ETF.md)
**QUOTE:** “S124.3 is the ICI census, sitting inside Z.1”
**UNCERTAIN:** The Fed guide page fetched does not itself say “source: ICI.” The Fed’s S124.3 table description would close that.

**CLAIM:** “Collateral did not carry this repricing, and shadow money did not”
**VERDICT:** FALLS
**REASON:** This says a channel did not cause the repricing. N4 refuses that sentence: 2024’s handoff-adjusted wholesale increase was $136bn against $1,405bn of wrapper purchases that year (about 4%), while the full-window ceiling is still about a quarter of the $3,069bn. “Did not” is stronger than either bound.
**SOURCE:** [N4](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-15-N4-Scale-Timing-Bound.md)
**QUOTE:** “No percentage of purchases ran through nonbank money”
**UNCERTAIN:** No, on the wording. The 2024 capacity ceiling survives as a bound.

**CLAIM:** “managed-money futures length ended where it began”
**VERDICT:** WEAKENED
**REASON:** Futures-only gold net length was 106,454 contracts on 26 Dec 2023 and 107,089 on 13 Oct 2026. It was 166,169 at end-2024, and the findings note puts the peak at 219,029 in Sep 2024. The endpoint hides a doubling and a full reversal.
**SOURCE:** [checkpoints.csv](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/cftc_cot/checkpoints.csv); [E-021](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-10-12-E021-Where-The-Money-Comes-From-Rates-FX-Commodities.md)
**QUOTE:** “peaked at 219,029 in Sep 2024”
**UNCERTAIN:** No for the endpoint. The 219,029 peak was not re-read from a CFTC file this session.

**CLAIM:** “fund positions moved with the price, more closely in Brent”
**VERDICT:** WEAKENED
**REASON:** Over 2 Jan 2024–13 Oct 2026 the same-week correlation is 0.58 for Brent and 0.38 for WTI (146 weeks). In 2026 alone the findings note has Brent at 0.60 and WTI at 0.04, inside a ±0.16 noise band. The paragraph is about 2026, and WTI did not move with the price that year.
**SOURCE:** [leadlag.csv](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/cftc_cot/leadlag.csv); [brent_leadlag.csv](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/ice_brent/brent_leadlag.csv); E-021
**QUOTE:** “In 2026’s 40 weeks alone: Brent 0.60, WTI 0.04”
**UNCERTAIN:** The 0.04 is the findings note’s split; the csv on disk is only the pooled window.

**CLAIM:** “the rest of the world’s share of net Treasury issuance fell from 44% to 12%”
**VERDICT:** WEAKENED
**REASON:** E-021’s own dollars are $709bn/$1,615bn (43.9%) then $294bn/$2,360bn (12.5%). Issuance rose 46%, so unchanged foreign buying would already have been 30%, not 44%. The Fed’s swing from −$266bn to +$264bn also changes the share. Z.1 still places offshore hedge funds in the household row, so 12% is not “foreigners.”
**SOURCE:** [E-021](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-10-12-E021-Where-The-Money-Comes-From-Rates-FX-Commodities.md)
**QUOTE:** “$709bn (44%) to $294bn (12%)”
**UNCERTAIN:** The Z.1 F.210 file itself. The 11 Sep 2026 table URL returned 404, so these dollars were not re-added from the Fed CSV.

**CLAIM:** “Operating companies retired equity on net while the ETF layer grew”
**VERDICT:** WEAKENED
**REASON:** Nonfinancial net issuance over 2024:Q1–2026:Q2 is −$540.7bn, and ETF share issuance is +$3,603.8bn. Inside that window, 2026:Q1 is +$51.3bn and 2026:Q2 is +$153.2bn, so 2026 to date is +$204.5bn of issuance after −$745bn through 2025:Q4.
**SOURCE:** [quarterly.csv](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/etf1/quarterly.csv)
**QUOTE:** “2026:Q2 … nfc_issuance_bn … 153.209”
**UNCERTAIN:** No for this file. It is the project’s Z.1 extract, not a fresh Fed download.

**CLAIM:** “the tax cut is about a tenth of earnings growth”
**VERDICT:** WEAKENED
**REASON:** 0.1012/1.0613 is 9.5% of 2015–2025 Δlog earnings per share (8.9% on the panel’s own 1.1341). That is the whole effective-rate decline, 27.35% to 19.62% of summed pre-tax income, not a measured Tax Cuts and Jobs Act share. The note says the foreign mix can over-attribute it, and the ratio spreads a 2018 level shift across a decade.
**SOURCE:** [W3](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-21-W3-Tax-Decomposition.md)
**QUOTE:** “tax is about a tenth of EPS growth either way”
**UNCERTAIN:** How much of the 7.7-point effective-rate drop is statutory rather than foreign mix. A domestic-only effective rate would settle it.

**CLAIM:** “Most of the measured compression is the rate rise restated”
**VERDICT:** STANDS
**REASON:** Premium is defined as earnings yield minus the real yield. Real yields rose 0.34 points and the earnings yield fell 0.14, so 0.34/0.48 of the 49bp is the rate leg by construction. It does not explain why the multiple held up. That multiple also round-tripped, 24.35 to 28.60 to 25.22.
**SOURCE:** [P2c](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-12-P2c-Rates-vs-Risk-Premium.md), C-102 banner
**QUOTE:** “most of its fall is the same rate rise, restated”
**UNCERTAIN:** No for the identity.

**CLAIM:** “SOFR rose 2bp, the Fed’s reverse repo took $11.5bn”
**VERDICT:** STANDS
**REASON:** SOFR was 3.88% on 29 Sep 2026 and 3.90% on 30 Sep, then 3.87% on 1 Oct. Reverse repo accepted $11.539bn on 30 Sep, against $11.446bn the day before, so the level was not a spike. Sponsored repo’s $253bn was not re-read.
**SOURCE:** [NY Fed SOFR](https://markets.newyorkfed.org/api/rates/secured/sofr/search.json?startDate=2026-09-28&endDate=2026-10-02); [NY Fed reverse repo](https://markets.newyorkfed.org/api/rp/reverserepo/propositions/search.json?startDate=2026-09-29&endDate=2026-10-01)
**QUOTE:** “percentRate: 3.90” on 2026-09-30, and “totalAmtAccepted: 11539000000”
**UNCERTAIN:** The $253bn sponsored-repo jump. The OFR search returned 403.

**CLAIM:** “on 5 February 2025 both yields fell more than 8bp”
**VERDICT:** STANDS
**REASON:** Treasury par yields from 4 Feb to 5 Feb 2025: 10-year 4.52% to 4.43% (−9bp), 30-year 4.75% to 4.64% (−11bp). Both cleared 8bp, with auction sizes not re-checked here.
**SOURCE:** [Treasury February 2025](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202502)
**QUOTE:** “02/05/2025 … 4.43 … 4.64”
**UNCERTAIN:** That auction sizes were unchanged that day. The yield move itself is not uncertain.

## 2. The single weakest claim

The weakest sentence is the Japan result: recorded holdings “fell about 0.4 dollars per dollar of intervention.” The 10-year yield was 4.75% at both month-ends, so a 10-year’s clean price did not gain the $4.8bn that turns −$35.6bn into −$40.4bn and then into 0.41–0.43. One month of coupon on $1,103.9bn at 4.75% is about $4.4bn, and coupon cash is not a rise in the custodial stock. The raw decline, the wide pre-registered range, and the disclaimer that this is not proof the sales paid for the intervention all survive. The 0.4 ratio does not. A reader also cannot see which dollar is the numerator.

What else survives in the section: the compression line is an identity (about 70% of the 49bp is the 0.34-point real-yield rise); SOFR’s quarter-end move was 2bp and reverse repo was $11.5bn; 5 Feb 2025 really did move both long yields by more than 8bp; gold’s futures length did finish near its end-2023 level; operating companies are still net retirees over the full 2024:Q1–2026:Q2 window (−$540.7bn); and the tax term is still about a tenth of 2015–2025 log earnings-per-share growth. The 2024 wholesale-money ceiling (about 4% of that year’s wrapper purchases after the reverse-repo handoff) survives as a bound. It does not survive as “shadow money did not carry the repricing.”

## 3. NOT DONE

The current TIC major-foreign-holders file, the BIS $75.7trn June 2025 stock and the +8.2% and +14.5% June-on-June changes, the $253bn sponsored-repo print, Beignet’s $27bn deal size, the “93 to 119 corrections in four days” dating, and a fresh sum of Z.1 Table F.210. `mfh.txt` returned a March 2023 vintage, the BIS release URLs tried returned 404, the OFR search returned 403, and the 11 Sep 2026 F.210 page returned 404. Those sentences were not scored.

## Grok return: pre-registration 1, lease commitments not yet commenced

I'll read the local calendar and the September note first, then pull the repository files and primary sources they name so the pre-registrations rest on those figures.The calendar row names the guarantee-stack note and a $1,122.9bn mid-2026 total. I’ll pull that note and the AI-funding files it sits with.The mid-2026 total is six filers and $1,122.9bn, with vintages that do not line up. Next I’ll pull the per-filer history and the filings those figures came from.The project’s filer notes give two vintages, not a quarterly path. I’ll read the lease footnotes and the filings that updated Oracle and NVIDIA after that sum.The latest 10-Qs are still the mid-year filings; Q3 is not out. I’ll read the lease footnotes, including NVIDIA’s July quarter, which the $1,122.9bn total does not include.The six-filer lease stock to score is the next hand-read of leases signed but not yet commenced. The last readings already on file sum to about **$1,163.5bn**, and the base-rate point for the next round is **$1,370bn**, inside **$1,220bn–$1,570bn**. The project’s $1,122.9bn figure is the older stack (Oracle at 31 May, NVIDIA at 26 April). These registrations are dated 17 October 2026. No September-quarter 10-Q for these filers is in the EDGAR lists pulled today.

The quantity is one stock, not a flow, and it is not a claim about any price.

The six filers are the set in the guarantee-stack note and the AI-funding dossier: Alphabet, Amazon, Meta, Microsoft, Oracle, and NVIDIA. “Q3 2026” follows the calendar row. Four filers report a quarter ending 30 September. NVIDIA’s fiscal quarter ends about 25 October. Oracle’s next reading is the quarter ending 30 November. The six dates will not match. That is the same vintage practice as the $1,122.9bn stack.

**Scoring rule, locked now.** Undiscounted future payments on leases signed but not yet commenced, in billions of US dollars, from the ASC 842 lease footnote or from the commitments line the filer labels as leases not yet commenced if that is where the amount moved. Do not add purchase obligations, guarantees, remaining performance obligations, or residual-value caps. If a filer omits the line, record “not disclosed” and do not enter zero. The six-filer total is scored only when all six numbers are in, which waits on Oracle.

---

## 1. Six-filer total

**QUANTITY.** Sum of the six amounts defined above. There is no XBRL tag for this line in the project’s August reading (0 of 6). The figures below were taken from the HTML notes and commitment tables. Units: $bn, undiscounted. The total can be scored when Oracle’s Q2 FY2027 10-Q is filed, expected about **10–12 December 2026** (the Q2 filings were 11 Dec 2025, 10 Dec 2024, and 12 Dec 2023). Alphabet, Amazon, Meta, and Microsoft are expected about **28 October–2 November 2026**. NVIDIA is expected about **18–25 November 2026**.

**LAST OBSERVED VALUES.** Latest filed figure for each name, mixed dates:

| Filer | As of | $bn | Where read |
|---|---|---:|---|
| Meta | 30 Jun 2026 | 278.99 | Project filer note, 10-Q acc. 0001628280-26-050705 |
| Microsoft | 30 Jun 2026 | 329.1 | Project filer note, 10-K acc. 0001193125-26-323660 |
| Oracle | 31 Aug 2026 | 288 | Oracle facts file, 10-Q acc. 0001193125-26-389274 |
| Amazon | 30 Jun 2026 | 137.214 | Project filer note, 10-Q acc. 0001018724-26-000026 |
| Alphabet | 30 Jun 2026 | 85.2 | Project filer note, 10-Q acc. 0001652044-26-000071 |
| NVIDIA | 26 Jul 2026 | 45 | This session: 10-Q, $25bn + $20bn, both labeled leases not commenced |
| **Sum** | mixed | **1,163.5** | |

The project’s prior-period stack is about **$417.4bn** (Meta 103.77 at 31 Dec 2025, Alphabet 58.5 at 31 Dec 2025, Microsoft 92.7 at 30 Jun 2025, Oracle 43.4 at 31 May 2025, Amazon 96.4 at 31 Dec 2025, NVIDIA 22.7 at 25 Jan 2026). Those six dates span eight months. 1,122.9 / 417.4 is about 2.7×. That multiple is a year-scale description. It is the wrong base rate for one quarter.

Replacing Oracle 260 with 288 and NVIDIA 32.4 with 45 moves 1,122.9 to 1,163.5.

**PREDICTION.** Point **$1,370bn**. Range **$1,220bn–$1,570bn** (width $350bn).

The point is the sum of the six filer points below. Four of those points are the recent quarterly dollar change in that filer’s own series. Microsoft’s point spreads the only measured change, +$236.4bn over the year to 30 June 2026, into four equal quarters (+$59bn). Oracle’s last three quarters, after a step-up that was finished by 30 November 2025, moved by −$1bn, +$13bn, and +$28bn, so the total does not repeat the old 2.7×. The $350bn width is mostly Microsoft: its interim path was not read, so one quarter of a 3.55× year can sit anywhere from a pause to about half of that annual dollar increase. The other five histories are tighter, and they are what keep the total from being “anywhere.”

**FALSIFIED IF** the hand-sum of the six next readings is below $1,220bn or above $1,570bn. A missing line voids the total. It is not scored as zero.

**WHAT IT WOULD TELL THE PROJECT.** A print inside the range says the off-balance-sheet lease stock is still being added to, on the order of one recent quarter of signing, and that the mid-2026 level was not a peak. A print above $1,570bn says signing ran ahead of that quarterly pace. A print below $1,220bn says leases commenced onto the balance sheet faster than new ones were signed, or that signing paused. Either result sizes that stock. This paragraph does not say the stock caused a price.

**UNCERTAIN.** The $1,163.5bn sum mixes 30 June, 26 July, and 31 August. NVIDIA’s $45bn is two lines printed in whole billions. Microsoft’s quarterly path was not read. Exact filing days are inferred from the prior three years of the same quarter, not from a company calendar.

---

## 2. Meta Platforms

**QUANTITY.** Operating and finance leases not yet commenced, the single approximate dollar figure in the commitments note (Q1 2026: Note 8, “Leases and Contractual Commitments”). $bn. Quarter ending **30 September 2026**. Expected filing **about 29–31 October 2026** (filed 30 Oct 2025, 31 Oct 2024, 26 Oct 2023).

**LAST OBSERVED VALUES.** Read this session unless noted.

| As of | $bn | Change | Source |
|---|---:|---|---|
| 30 Sep 2025 | 58.14 | | [10-Q](https://www.sec.gov/Archives/edgar/data/1326801/000162828025047240/meta-20250930.htm), acc. 0001628280-25-047240 |
| 31 Dec 2025 | 103.77 | +45.6 | Project filer note; 10-K acc. 0001628280-26-003942 |
| 31 Mar 2026 | 182.88 | +79.1 | [10-Q](https://www.sec.gov/Archives/edgar/data/1326801/000162828026028526/meta-20260331.htm), acc. 0001628280-26-028526 |
| 30 Jun 2026 | 278.99 | +96.1 | Project filer note; 10-Q acc. 0001628280-26-050705 |

The June filing also reports about **$68bn** of further data-centre leases entered in July 2026, commencement expected in 2027 and 2028, and not included in the $278.99bn. Those leases should still be uncommenced at 30 September, so they sit inside the next stock.

**PREDICTION.** Point **$367bn**. Range **$340bn–$410bn** (width $70bn).

The three quarterly net additions are +$46bn, +$79bn, and +$96bn. The point uses the mean of the last two (+$88bn). The $68bn July signing is already inside that increment. It is not added on top of a full extra quarter. The $70bn width is a little wider than the $50bn span of those three additions, which is as tight as three observations of an accelerating series will bear.

**FALSIFIED IF** the 30 September 2026 figure is below $340bn or above $410bn.

**WHAT IT WOULD TELL THE PROJECT.** Meta is the fastest-rising large stock in the set. A print inside the range says that rise is still near the last two quarters, with the July leases absorbed rather than stacked on a new surge. Above $410bn, the quarterly addition has broken the recent pace. Below $340bn, commencement or a signing pause has offset the July leases. This sizes Meta’s uncommenced lease stock. It does not identify a cause of any price.

**UNCERTAIN.** The 31 December and 30 June figures, and the $68bn, were taken from the project filer note, not re-read in the HTML this session. Meta gives no maturity schedule, so the commenced piece of each quarterly change is not separated.

---

## 3. Alphabet

**QUANTITY.** Leases not yet commenced, primarily data centres, future lease payments not yet recorded, in the leases note (Q1 2026: Note 4). $bn. Quarter ending **30 September 2026**. Expected filing **about 29–30 October 2026** (filed 30 Oct 2025, 30 Oct 2024, 25 Oct 2023).

**LAST OBSERVED VALUES.**

| As of | $bn | Change | Source |
|---|---:|---|---|
| 31 Dec 2025 | 58.5 | | Project filer note: $5.8bn short-term + $52.7bn long-term; 10-K acc. 0001652044-26-000018 |
| 31 Mar 2026 | 75.6 | +17.1 | [10-Q](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000048/goog-20260331.htm), acc. 0001652044-26-000048 |
| 30 Jun 2026 | 85.2 | +9.6 | Project filer note; 10-Q acc. 0001652044-26-000071 |

**PREDICTION.** Point **$99bn**. Range **$90bn–$110bn** (width $20bn).

The only two quarterly additions are +$17.1bn and +$9.6bn, and the second is the smaller one. The point is their mean (+$13.4bn). The range runs from a bit under the slower quarter to a bit over the faster one. That is the width those two changes support. A further $5.8bn short-term lease the project lists as commencing in Q3, and as outside the $85.2bn, is left out of the stock.

**FALSIFIED IF** the 30 September 2026 figure is below $90bn or above $110bn.

**WHAT IT WOULD TELL THE PROJECT.** Alphabet is the slowest riser of the large lessees over the first half of 2026. A print inside the range says that slower pace held for another quarter. Outside it, Alphabet has either rejoined the faster signers or the uncommenced stock has started to roll onto the balance sheet. This is a stock size. It is not a price cause.

**UNCERTAIN.** The 31 December and 30 June amounts were not re-read in the HTML this session. The September 2025 quarter was not fetched, so the pre-2026 pace is unknown.

---

## 4. Amazon

**QUANTITY.** The commitments-table row “Leases not yet commenced.” $bn. Quarter ending **30 September 2026**. Expected filing **about 30 October–2 November 2026** (filed 31 Oct 2025, 1 Nov 2024, 27 Oct 2023).

**LAST OBSERVED VALUES.**

| As of | $bn | Change | Source |
|---|---:|---|---|
| 30 Sep 2025 | 75.021 | | [10-Q](https://www.sec.gov/Archives/edgar/data/1018724/000101872425000123/amzn-20250930.htm), acc. 0001018724-25-000123, commitments table total $75,021 million |
| 31 Dec 2025 | 96.373 | +21.4 | Project filer note; 10-K acc. 0001018724-26-000004 |
| 31 Mar 2026 | 106.347 | +10.0 | Project filer note; 10-Q acc. 0001018724-26-000014 |
| 30 Jun 2026 | 137.214 | +30.9 | Project filer note; 10-Q acc. 0001018724-26-000026 |

**PREDICTION.** Point **$158bn**. Range **$142bn–$180bn** (width $38bn).

Three quarterly net additions: +$21.4bn, +$10.0bn, +$30.9bn. The point is their mean (+$20.7bn). The range is wide enough to cover the smallest and the largest of those quarters with a few billion of room. That $38bn width is the history. A tighter band would pretend the three quarters agreed.

**FALSIFIED IF** the 30 September 2026 figure is below $142bn or above $180bn.

**WHAT IT WOULD TELL THE PROJECT.** Amazon is the one filer that publishes a maturity profile of this stock, so a later hand-read can separate commencement from new signing. The registered object is still the total. Inside the range, the lumpy quarterly adds have continued. Outside it, the lump has changed size. This does not say the leases caused a price.

**UNCERTAIN.** Only the September 2025 total was read in the HTML this session. The later three totals are the project filer note’s readings of the same row. The note’s H2 2026 commencement slice of $4,018 million was not re-read here.

---

## 5. Oracle

**QUANTITY.** Additional lease commitments that are off the balance sheet and off the lease-maturity table, substantially all data-centre arrangements. $bn, as printed (whole billions). This is not the calendar Q3 10-Q. It is the **Q2 FY2027** 10-Q, quarter ending **30 November 2026**, expected filing **about 10–12 December 2026**.

**LAST OBSERVED VALUES.**

| As of | $bn | Change | Source |
|---|---:|---|---|
| 31 May 2025 | 43.4 | | Project filer note; 10-K acc. 0000950170-25-087926 |
| 30 Nov 2025 | 248 | +205 over two quarters | [10-Q](https://www.sec.gov/Archives/edgar/data/1341439/000119312525315925/orcl-20251130.htm), acc. 0001193125-25-315925 |
| 28 Feb 2026 | 261 | +13 | [10-Q](https://www.sec.gov/Archives/edgar/data/1341439/000119312526101045/orcl-20260228.htm), acc. 0001193125-26-101045 |
| 31 May 2026 | 260 | −1 | Project filer note and Oracle facts file; 10-K acc. 0001193125-26-277521 |
| 31 Aug 2026 | 288 | +28 | Oracle facts file; 10-Q acc. 0001193125-26-389274 |

**PREDICTION.** Point **$301bn**. Range **$275bn–$330bn** (width $55bn).

The base rate is the last three quarters, +$13bn, −$1bn, and +$28bn, mean about +$13bn. The +$205bn between May and November 2025 is a completed step, not the one-quarter rate. The range covers another flat quarter through another quarter a bit larger than the +$28bn. The 6.0× annual multiple is the step plus the later drift. Using it as the next-quarter forecast would make the range useless.

**FALSIFIED IF** the 30 November 2026 figure is below $275bn or above $330bn.

**WHAT IT WOULD TELL THE PROJECT.** Oracle is the filer whose uncommenced stock jumped and then slowed. A print inside the range says the post-step regime is still a drift of tens of billions a quarter, not another step. Above $330bn, a second step has started. Below $275bn, commencement has overtaken new signing. The $3.3bn lessor-borrowing guarantee that was due in September 2026 is a different line and is not part of this score. None of this is a claim that the lease stock caused a price.

**UNCERTAIN.** The August 2025 quarter, inside the +$205bn step, was not fetched, so that step is not split. The November 2025 sentence says “data centers and cloud capacity arrangements.” The February 2026 sentence says “data center arrangements.” The dollar path is smooth across that wording change. A definition break large enough to move the score would have to be shown from the two notes side by side.

---

## 6. NVIDIA

**QUANTITY.** Sum of every line in the 10-Q that the filing itself labels as data-centre leases not commenced, whether in the lease note or the commitments note. Do not add the $3.5bn land-power-shell guarantee or the $105bn SB Energy cap. $bn. Fiscal Q3 ends about **25 October 2026** (Q2 ended 26 July; FY2027 Q2 was a 13-week quarter). Expected filing **about 18–25 November 2026** (Q1 was filed 24 days after quarter-end, Q2 was filed 31 days after, and the prior Q3 was filed 19 Nov 2025).

**LAST OBSERVED VALUES.**

| As of | $bn | Source |
|---|---:|---|
| 25 Jan 2026 | 22.7 | Project filer note; FY2026 10-K Note 17, acc. 0001045810-26-000021 |
| 26 Apr 2026 | 32.4 | Project filer note; Q1 FY2027 10-Q Note 14, acc. 0001045810-26-000052 |
| 26 Jul 2026 | 25 + 20 = **45** | [10-Q](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm), acc. 0001045810-26-000075, Note 10. Own-use line total 25. Third-party line total 20. Note 14 of that filing has no separate not-yet-commenced total. |

The 14 September project note read only the $20bn third-party line inside “Additional Commitments.” The same filing’s first commitments table has another $25bn line for NVIDIA’s own data-centre leases not commenced. Both are in the registered sum. The April $32.4bn was one lease-note figure, “primarily” data-centre leases. The July filing split the disclosure.

**PREDICTION.** Point **$56bn**. Range **$40bn–$70bn** (width $30bn).

Treating 22.7 → 32.4 → 45 as one series, the quarterly additions are +$9.7bn and +$12.6bn. The point repeats that pace (+$11bn). The range allows the third-party $20bn book to be reassigned and drop out, and allows another quarter like the last two on the remaining stock. The components are printed in whole billions, so the $45bn start is already rounded.

**FALSIFIED IF** the sum of the not-commenced data-centre lease lines in the Q3 FY2027 10-Q is below $40bn or above $70bn. If the filing returns to a single lease-note sentence, that sentence is the score.

**WHAT IT WOULD TELL THE PROJECT.** NVIDIA’s own uncommenced leases are small beside Meta, Microsoft, and Oracle. The new fact in the July filing is a $20bn book NVIDIA expects to reassign. A print inside the range says that book is still small in the six-filer sum. A drop through $40bn, with the third-party line gone, says those leases left NVIDIA’s disclosure. A print above $70bn says NVIDIA has become a large lessee in this stock, which the two prior quarters do not show. This is not a claim about a price.

**UNCERTAIN.** Whether the April $32.4bn already contained any of the July $20bn is not stated. Each July component is rounded to $1bn, so the true sum can differ by a few billion. The Q3 filing date inside 18–25 November is inferred.

---

## 7. Microsoft

**QUANTITY.** Leases signed but not yet commenced, the figure in the leases note (FY2026 10-K: Note 13). $bn. The next reading is **Q1 FY2027**, quarter ending **30 September 2026**. Expected filing **about 28–30 October 2026** (filed 29 Oct 2025, 30 Oct 2024, 24 Oct 2023).

**LAST OBSERVED VALUES.** Only two points were read, both from the project filer note, not from the interim HTML.

| As of | $bn | Source |
|---|---:|---|
| 30 Jun 2025 | 92.7 | 10-K acc. 0000950170-25-100235 |
| 30 Jun 2026 | 329.1 | 10-K acc. 0001193125-26-323660, Note 13 |

Change: **+$236.4bn in four quarters, 3.55×**. The September 2025, December 2025, and March 2026 10-Qs were not read. Their HTML files are about 7.5MB, and the lease sentence was not extracted.

**PREDICTION.** Point **$388bn**. Range **$330bn–$470bn** (width $140bn).

$388bn adds one-fourth of the only measured annual increase (+$59bn). A constant quarterly rate that compounds to 3.55× would put the next quarter near $450bn, and that number sits inside the range. It is not a second point estimate. The range runs from a pause at the June level to about half of the annual dollar increase arriving in this one quarter (+$141bn). That is as narrow as two annual observations can make one quarter. It is wider than the other five ranges because the quarterly path is missing. A result inside $330bn–$470bn will not distinguish a smooth year from a lumpy one.

**FALSIFIED IF** the 30 September 2026 figure is below $330bn or above $470bn.

**WHAT IT WOULD TELL THE PROJECT.** Microsoft is the largest single stock in the $1,163.5bn sum, so this one reading moves the total more than any other. Inside the range, the June level has not reversed and has not repeated a full year of additions in one quarter. Below $330bn, the largest stock has stalled or rolled on. Above $470bn, one quarter has done more than half of last year’s entire increase. That is a stock observation. It does not say Microsoft’s leases caused a price.

**UNCERTAIN.** The entire quarterly path from $92.7bn to $329.1bn. Reading the three interim 10-Qs would replace this range with one on the scale of Amazon’s or Alphabet’s. Until then, Microsoft is the soft joint in the six-filer total.

---

## NOT DONE

- Microsoft’s 10-Qs for the quarters ended 30 September 2025, 31 December 2025, and 31 March 2026. The lease sentence was not extracted. That is the largest hole in the six-filer range.
- Oracle’s 10-Q for the quarter ended 31 August 2025, so the +$205bn step between May and November 2025 is not split into two quarters.
- HTML re-reads of Meta at 31 December 2025 and 30 June 2026 (including the July $68bn sentence), Alphabet at 31 December 2025 and 30 June 2026, Amazon at 31 December 2025, 31 March 2026, and 30 June 2026, and Microsoft’s FY2026 10-K. Those amounts are the project filer note’s readings, with the accessions named above.
- Alphabet at 30 September 2025.
- A fresh XBRL companyfacts check. The July NVIDIA 10-Q still presents the lease totals in a commitments table in the HTML.
- Company-announced filing dates. The dates above are the prior three years of the same quarter, from the EDGAR atom feeds fetched today.
- No sentence here says a lease signing, a guarantee, or any other flow caused a price.

## Grok return: pre-registration 2, cash flow against capex, and 2026 bond face

I'll read the calendar and the September note first, then pull the source notes and filings those rows name so the pre-registrations rest on the published figures.The calendar ties both reads to the Q3 10-Qs and names the funding table, the AI-funding dossier, and the 13 October bond review. I'll pull those next.The dossier’s $229bn is the 13 October deal list converted at ECB rates, and the cash-flow table stops at June–August. I’ll pull the tag definitions, the quarterly history, and the expected filing dates before writing the ranges.The cash-flow comparison is trailing operating cash against capex, and the bond figure is a face sum converted at ECB rates. I’ll pull the quarterly filings and those rates so the ranges come from the history.Alphabet’s quarterly cash-flow history is in the XBRL, and no October earnings release is on file. I’ll pull the same series for the other five firms and the exchange rates behind the $229bn sum.Pre-registration, 17 October 2026. No third-quarter 10-Q for these firms is in the EDGAR feeds dated today. No sentence below treats a cash flow or a bond issue as a cause of a price.

Assumption: “the Q3 2026 10-Q” means the quarter ended 30 September 2026 for Alphabet, Amazon, Meta, and Microsoft (Microsoft’s first quarter of fiscal 2027). Oracle’s quarter ended 31 August 2026 is already filed. Oracle’s next 10-Q ends 30 November 2026. NVIDIA’s next quarter ends about 25 October 2026.

---

## 1. Trailing-twelve-month operating cash flow and capital expenditure

### QUANTITY

For each firm, two lines from the consolidated statement of cash flows in the Form 10-Q (Microsoft: the Q1 FY2027 10-Q; Oracle’s October reading: the 10-Q already filed), in billions of US dollars as reported:

- Operating cash flow: XBRL `NetCashProvidedByUsedInOperatingActivities`.
- Capital expenditure: `PaymentsToAcquirePropertyPlantAndEquipment` for Alphabet, Meta, Microsoft, and Oracle; `PaymentsToAcquireProductiveAssets` for Amazon and NVIDIA.

The trailing twelve months are each firm’s own fiscal window, not a common calendar year. The comparison the page states is the sign of trailing-twelve-month operating cash flow minus trailing-twelve-month capex. The scored gap is that difference. Oracle’s internal-cash residual (operating cash flow after dividends and buybacks) is a different last observation, about −$34.9bn, and is not the scored gap.

Filing dates, from each firm’s last three same-quarter 10-Qs. Today is Saturday 17 October 2026. The large-accelerated-filer deadline for a 30 September quarter is 9 November 2026.

| Firm | Period | Expected filing | Same-quarter filings |
| --- | --- | --- | --- |
| Alphabet | ended 30 Sep 2026 | 30 Oct 2026 | 30 Oct 2025, 30 Oct 2024, 25 Oct 2023 |
| Amazon | ended 30 Sep 2026 | 30 Oct 2026 | 31 Oct 2025, 1 Nov 2024, 27 Oct 2023 |
| Meta | ended 30 Sep 2026 | 29 Oct 2026 | 30 Oct 2025, 31 Oct 2024, 26 Oct 2023 |
| Microsoft | ended 30 Sep 2026 | 28 Oct 2026 | 29 Oct 2025, 30 Oct 2024, 24 Oct 2023 |
| Oracle, next | ended 30 Nov 2026 | 10–11 Dec 2026 | 11 Dec 2025, 10 Dec 2024, 12 Dec 2023 |
| NVIDIA | ended ~25 Oct 2026 | 18 Nov 2026 | 19 Nov 2025, 20 Nov 2024, 21 Nov 2023 |

Oracle’s quarter ended 31 August 2026 was filed 11 September 2026. That print is the Oracle input to an October score.

### LAST OBSERVED VALUE(S)

Trailing twelve months, USD billions, from the project’s sourced table, recomputed from the cash-flow facts below.

| Firm | Window | Capex | Operating cash flow | Gap |
| --- | ---: | ---: | ---: | ---: |
| Alphabet | to 30 Jun 2026 | 132.402 | 185.675 | +53.273 |
| Amazon | to 30 Jun 2026 | 173.028 | 161.403 | −11.625 |
| Meta | to 30 Jun 2026 | 89.325 | 130.301 | +40.976 |
| Microsoft | FY2026, to 30 Jun 2026 | 115.948 | 182.935 | +66.987 |
| Oracle | to 31 Aug 2026 | 75.660 | 46.940 | −28.720 |
| NVIDIA | to 26 Jul 2026 | 7.354 | 134.360 | +127.0 |

Sources: [funding table CSV](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/_research/2026-09-12-F1-funding_table.csv), [funding table note](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-12-F1-Funding-Table.md), [dossier](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/dossiers/ai-funding.md), [public page](https://closeofbusiness.github.io/market-plumbing/). The page’s “three of five” are Alphabet, Meta, and Microsoft. Amazon’s shortfall is about $12bn. Oracle’s operating-cash shortfall is about $29bn. NVIDIA’s capex is small beside its operating cash flow.

Quarterly operating cash flow and capex, latest vintage, USD millions. A quarter that is not filed as its own fact is the year-to-date minus the prior year-to-date. Surplus is operating cash flow minus capex.

Alphabet, Amazon, Meta, and Microsoft company facts: [Alphabet capex](https://data.sec.gov/api/xbrl/companyconcept/CIK0001652044/us-gaap/PaymentsToAcquirePropertyPlantAndEquipment.json), [Alphabet operating cash flow](https://data.sec.gov/api/xbrl/companyconcept/CIK0001652044/us-gaap/NetCashProvidedByUsedInOperatingActivities.json), [Amazon capex](https://data.sec.gov/api/xbrl/companyconcept/CIK0001018724/us-gaap/PaymentsToAcquireProductiveAssets.json), [Amazon operating cash flow](https://data.sec.gov/api/xbrl/companyconcept/CIK0001018724/us-gaap/NetCashProvidedByUsedInOperatingActivities.json), [Meta capex](https://data.sec.gov/api/xbrl/companyconcept/CIK0001326801/us-gaap/PaymentsToAcquirePropertyPlantAndEquipment.json), [Meta operating cash flow](https://data.sec.gov/api/xbrl/companyconcept/CIK0001326801/us-gaap/NetCashProvidedByUsedInOperatingActivities.json), [Microsoft capex](https://data.sec.gov/api/xbrl/companyconcept/CIK0000789019/us-gaap/PaymentsToAcquirePropertyPlantAndEquipment.json), [Microsoft operating cash flow](https://data.sec.gov/api/xbrl/companyconcept/CIK0000789019/us-gaap/NetCashProvidedByUsedInOperatingActivities.json).

Alphabet surplus, last eight quarters: +16.8, +13.5, +17.6, +24.8, +19.0, +5.3, +24.5, +24.6, +10.1, −5.9 ($bn, 2024 Q1 through 2026 Q2). Year-on-year change in the quarterly surplus, last four: +6.8, −0.3, −8.8, −11.2.

Amazon surplus, 2024 Q3 through 2026 Q2: +3.4, +17.8, −8.0, +0.3, +0.4, +14.9, −18.2, −8.8. Year-on-year changes, last four: −2.9, −2.9, −10.2, −9.2. The four quarters sum to the table totals 173.028 and 161.403.

Meta surplus, 2025 Q1 through 2026 Q2: +11.1, +9.0, +11.2, +14.8, +13.2, +1.7. Year-on-year changes, last four: −5.3, +1.3, +2.1, −7.3. The last four quarters sum to 89.325 and 130.301.

Microsoft fiscal quarters, surplus: FY2025 Q1 through Q4 +19.3, +6.5, +20.3, +25.6; FY2026 +25.7, +5.9, +15.8, +19.6. Year-on-year changes, last four: +6.4, −0.6, −4.5, −5.9. FY2026 quarters sum to 115.948 and 182.935.

Oracle and NVIDIA quarterly paths inside the year were not read from company-concept files. Oracle’s completed new-regime quarter (Q1 FY2027) is capex 28.499 and operating cash flow 23.103, surplus −5.4, against a year-ago surplus of −0.4. The other three quarters of FY2026 sum to a surplus of −23.3.

Filing lists confirming that these quarters are still the latest: [Alphabet 10-Q](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&type=10-Q&dateb=20261017&owner=include&count=12&output=atom), [Amazon 10-Q](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001018724&type=10-Q&dateb=20261017&owner=include&count=12&output=atom), [Meta 10-Q](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001326801&type=10-Q&dateb=20261017&owner=include&count=12&output=atom), [Microsoft 10-Q](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=10-Q&dateb=20261017&owner=include&count=12&output=atom), [Oracle 10-Q](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001341439&type=10-Q&dateb=20261017&owner=include&count=8&output=atom), [NVIDIA 10-Q](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001045810&type=10-Q&dateb=20261017&owner=include&count=8&output=atom).

### PREDICTION

The new trailing gap equals the old trailing gap, minus the surplus of the quarter that drops, plus the surplus of the new quarter. The new surplus equals the year-ago surplus plus the median of the last four year-on-year changes in that surplus. The range is the same year-ago surplus plus the smallest and the largest of those four changes. That width is the full span of four recent changes, not a band with tails beyond the sample. Capex and operating-cash-flow points use the median of the last four year-on-year ratios on the year-ago quarter. Those two lines move together, so the scored object for the page’s comparison is the surplus range.

On that rule the October filings keep the same three positive and two negative. Alphabet, Meta, and Microsoft would need a single quarter whose surplus is tens of billions below the worst recent year-on-year change before the trailing gap changes sign. Amazon’s entire range stays negative, and the top of that range is still about $14bn below zero, twice the width of the range itself. Oracle’s August gap is already −$28.7bn and does not update in October.

| Firm | TTM capex point (range) | TTM operating cash flow point (range) | TTM gap point (range) | Sign |
| --- | ---: | ---: | ---: | --- |
| Alphabet | 155.8 (152.4 to 158.1) | 203.8 (198.6 to 213.6) | +48.7 (+42.1 to +60.1) | positive |
| Amazon | 194.7 (187.8 to 199.9) | 175.0 (168.3 to 180.2) | −17.7 (−21.8 to −14.5) | negative |
| Meta | 101.6 (98.1 to 113.4) | 138.4 (136.7 to 140.5) | +39.0 (+33.7 to +43.1) | positive |
| Microsoft | 132.8 (121.8 to 137.2) | 196.9 (194.7 to 210.1) | +64.4 (+61.1 to +73.4) | positive |
| Oracle, October score | 75.7, already filed | 46.9, already filed | −28.7, already filed | negative |
| Five-firm count |  |  |  | 3 of 5 positive |

Gap widths the four-quarter history supports: Alphabet $18bn, Amazon $7bn, Meta $9bn, Microsoft $12bn. Meta’s capex line range is wider ($15bn) because one of the four ratios, 2.28, is 2025 Q3 against a low 2024 Q3 base. Microsoft’s capex line range is wider ($15bn) because the July–September quarter’s own prior ratio was 1.30 while the later three quarters were 1.84 to 2.10.

Oracle, December score, quarter ended 30 November 2026. Point gap −$26bn if the dropped quarter equals one-third of the unsplit FY2026 remainder (−$7.8bn) and the new quarter repeats Q1 FY2027 (−$5.4bn). Range −$34bn to −$11bn, the envelope from placing that −$23.3bn remainder anywhere in the three unsplit quarters and repeating the last quarter. Sign: negative. The December range is an envelope of an unread split, wider than the four-quarter method used above.

NVIDIA, filing expected 18 November 2026. Trailing operating cash flow remains above capex. A point gap near +$130bn to +$150bn requires an equal split of the half-years in the funding table, which was not read from the quarterly facts. The sharp call is the sign: capex would have to rise by on the order of $120bn in one quarter to close a +$127bn gap. Range used for scoring the sign only: gap still above +$100bn.

Sum of the five October gaps at the points: about +$106bn. Stacking every firm at the adverse end of its range, with Oracle held at −$28.7bn, still leaves the sum near +$86bn. This is the operating-cash-flow-minus-capex sum. It is not the Epoch AI aggregate free-cash-flow series named in the calendar row, which the project marks unverified.

### FALSIFIED IF

- Alphabet’s trailing gap is below +$42.1bn or above +$60.1bn, or the sign is negative.
- Amazon’s trailing gap is above −$14.5bn or below −$21.8bn, or the sign is positive.
- Meta’s trailing gap is below +$33.7bn or above +$43.1bn, or the sign is negative.
- Microsoft’s trailing gap is below +$61.1bn or above +$73.4bn, or the sign is negative.
- The October count of Alphabet, Amazon, Meta, Microsoft, and Oracle with trailing operating cash flow above trailing capex is anything other than three, or the three are not Alphabet, Meta, and Microsoft.
- Oracle’s December trailing gap is positive, or, on the envelope, outside −$34bn to −$11bn.
- NVIDIA’s November trailing capex exceeds trailing operating cash flow, or the gap is below +$100bn.
- A line item (capex or operating cash flow) outside its own range falsifies that line’s point. The comparison is scored on the gap range.

### WHAT IT WOULD TELL THE PROJECT

If the October count is still three of five, the dossier’s firm-level description survives one more reported quarter, and Oracle’s shortfall remains the August measurement until December. If Amazon’s gap turns positive, or Alphabet, Meta, or Microsoft turns negative, the count on the page changes and the self-funded sentence is stale. A December Oracle gap that is still negative extends that firm’s shortfall through the quarter ending 30 November. The calendar’s “aggregate free cash flow crossing zero” item, as an Epoch projection, stays untested by these figures. Either result revises a funding description. It is silent on prices.

### UNCERTAIN

- Oracle’s December point uses an equal split of Q2–Q4 FY2026. The Q2 FY2026 cash-flow statement would replace −$26bn with a bridge of the same kind as the other four firms.
- NVIDIA’s dollar point uses an equal split of each half-year. The Q3 FY2026 facts would settle the quarter that drops.
- Alphabet’s $180–190bn capex guide for 2026 was not re-read from the July earnings release. It was not used as the base rate.
- Microsoft’s July–September capex ratio may stay near last year’s 1.30 rather than the later-quarter ratios. That is why the capex line range is wider than the gap range; the gap range already includes the surplus outcome of that lower capex path.
- “Three of five” on the page was read as these five firms. Adding NVIDIA would make a sixth name whose gap stays largely positive.

---

## 2. Parent-company bond face issued in 2026 through 30 September

### QUANTITY

Sum of parent-company notes issued from 1 January 2026 through 30 September 2026 by Alphabet, Amazon, Meta, Microsoft, and Oracle. Principal in the issue currency, from the debt footnote of the 10-Q that covers 30 September (Oracle: the FY2026 10-K and the Q1 FY2027 10-Q already filed, plus the mid-December 10-Q if a September issue exists). Converted to US dollars at the ECB euro reference rate on the pricing date: US dollars per unit of foreign currency equals US dollars per euro divided by foreign currency per euro. Units: billions of US dollars. The project figure is about $229bn.

The scored sum is that face. Cash-flow proceeds tags are a different quantity. El Paso / joint-venture debt is outside the sum. NVIDIA’s notes are outside the sum. Filing dates are the same 10-Q dates as in section 1.

Date rule used here: the pricing or trade date when the deal list states one; otherwise the underwriting-agreement date. Alphabet’s Swiss franc uses 3 March (“on or around”). Alphabet’s Australian dollar uses the 27 August close, the date the note gives. Alphabet’s yen uses 15 May, the pricing date.

### LAST OBSERVED VALUE(S)

The dossier split is Alphabet $81bn, Amazon $98bn, Meta $25bn, Oracle $25bn, Microsoft none, summing to about $229bn. Deal face is from the fetched review note: [R1 deal list](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/_research/2026-10-13-Grok-Wave-Reviews-Return.md). The supervisor’s adjudication at the end of that file was past the truncated portion and was not read.

ECB rates fetched: [USD](https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?startPeriod=2026-02-02&endPeriod=2026-09-15&format=csvdata), [GBP](https://data-api.ecb.europa.eu/service/data/EXR/D.GBP.EUR.SP00.A?startPeriod=2026-02-09&endPeriod=2026-09-10&format=csvdata), [CHF](https://data-api.ecb.europa.eu/service/data/EXR/D.CHF.EUR.SP00.A?startPeriod=2026-02-27&endPeriod=2026-05-29&format=csvdata), [CAD](https://data-api.ecb.europa.eu/service/data/EXR/D.CAD.EUR.SP00.A?startPeriod=2026-05-04&endPeriod=2026-06-12&format=csvdata), [JPY](https://data-api.ecb.europa.eu/service/data/EXR/D.JPY.EUR.SP00.A?startPeriod=2026-05-14&endPeriod=2026-05-21&format=csvdata), [AUD](https://data-api.ecb.europa.eu/service/data/EXR/D.AUD.EUR.SP00.A?startPeriod=2026-08-20&endPeriod=2026-08-28&format=csvdata).

| Issue | Face | Date | ECB cross | USD bn |
| --- | ---: | --- | --- | ---: |
| Alphabet USD | $20bn | 9 Feb | — | 20.000 |
| Alphabet sterling | £5.5bn | 10 Feb | 1.3679 USD/GBP | 7.524 |
| Alphabet Swiss franc | CHF 3.055bn | 3 Mar | 1.2744 USD/CHF | 3.893 |
| Alphabet euro | €9bn | 5 May | 1.1686 | 10.517 |
| Alphabet Canadian | C$8.5bn | 5 May | 0.7345 USD/CAD | 6.243 |
| Alphabet yen | ¥576.5bn | 15 May | 0.006307 USD/JPY | 3.636 |
| Alphabet USD | $25bn | Aug | — | 25.000 |
| Alphabet Australian | A$5.5bn | 27 Aug | 0.7190 USD/AUD | 3.955 |
| Alphabet total |  |  |  | 80.77 |
| Amazon USD | $37bn | Mar | — | 37.000 |
| Amazon euro | €14.5bn | 11 Mar | 1.1581 | 16.792 |
| Amazon Swiss franc | CHF 2.82bn | 28 May | 1.2673 USD/CHF | 3.574 |
| Amazon Canadian | C$14bn | 8 Jun | 0.7175 USD/CAD | 10.045 |
| Amazon USD | $25bn | 7 Jul | — | 25.000 |
| Amazon sterling | £4.25bn | 9 Sep | 1.3565 USD/GBP | 5.765 |
| Amazon total |  |  |  | 98.18 |
| Meta USD | $25bn | 30 Apr | — | 25.00 |
| Oracle USD | $25bn | 2 Feb | — | 25.00 |
| Microsoft | none | through 30 Jun, and no Item 2.03 8-K from 1 Jul to 17 Oct | — | 0 |
| Five-name total |  |  |  | 228.9 |

The headline discrepancies in that review are small beside the total: Alphabet’s Canadian headline C$9.5bn would add about $0.73bn; the yen headline ¥576.9bn would add about $3m. Amazon’s euro on the 16 March close (1.1478) would subtract about $0.15bn. Alphabet’s Swiss franc and Australian dollar together are $7.85bn. Both are in the fetched deal list as counsel notes, with a close date only for the Australian dollar.

Checks that no later parent notes were filed as current reports: [Microsoft 8-Ks, 1 Jul–17 Oct](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=8-K&dateb=20261017&datea=20260701&owner=include&count=20&output=atom) (29 Jul results; 2 Sep Reg FD); [Oracle 8-Ks, 1 Sep–17 Oct](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001341439&type=8-K&dateb=20261017&datea=20260901&owner=include&count=15&output=atom) (10 Sep results; 14 Sep a cancelled stock-sale plan, [exhibit](https://www.sec.gov/Archives/edgar/data/1341439/000119312526389753/d20034dex991.htm)); [NVIDIA 8-Ks, 27 Jul–17 Oct](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001045810&type=8-K&dateb=20261017&datea=20260727&owner=include&count=15&output=atom). NVIDIA’s 17 August Item 2.03 is residual-value guarantees on leases, capped at $105bn of contingent obligation beginning in 2028, [8-K](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000069/nvda-20260817.htm). NVIDIA’s 3 September 8-K is an acquisition agreement, [8-K](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000078/nvda-20260902.htm). Neither is a parent note.

NVIDIA’s $24.9bn of proceeds through 26 July 2026 is already in its July 10-Q and is outside the $229bn.

### PREDICTION

Point: **$229bn**. Company points: Alphabet $80.8bn, Amazon $98.2bn, Meta $25bn, Oracle $25bn, Microsoft $0.

Range if the Swiss franc and Australian dollar deals closed: **$228bn to $230bn**. That width is the Canadian headline ($0.7bn), the Amazon euro date ($0.15bn), and rounding to the dossier’s $229bn. It is the width the fetched rates and the two headline gaps support.

The close of those two Alphabet currencies is the large unresolved item. If both are absent from the debt footnote, the sum falls to about **$221bn**. The prediction includes them, because the fetched record gives a scheduled close for the Swiss franc and a 27 August close for the Australian dollar, and no cancelling current report was in the filings read.

Specific principals the footnotes are predicted to show: Alphabet Canadian **C$8.5bn** (tranche sum), yen **¥576.5bn**, Swiss franc **CHF 3.055bn**, Australian dollar **A$5.5bn**. Microsoft: no parent notes in calendar 2026 through 30 September. Oracle: the $25bn February notes and no further parent notes through 30 September.

### FALSIFIED IF

- The five-name face sum, converted on the date rule above, is below $221bn or above $230bn.
- Alphabet’s footnote omits the Swiss franc issue or the Australian dollar issue.
- Alphabet’s Canadian principal is C$9.5bn rather than C$8.5bn, or the yen principal is materially off ¥576.5bn (a few tenths of a billion yen is inside the range).
- Microsoft’s Q1 FY2027 debt note records parent notes issued on or before 30 September 2026.
- Any of the five footnotes shows a parent note issued on or before 30 September 2026 that is not in the table above.
- Oracle’s December debt note shows parent notes issued in September 2026.

A USD carrying amount at the 30 September spot rate, or a cash-flow proceeds total, is a different quantity. It does not by itself falsify this face prediction.

### WHAT IT WOULD TELL THE PROJECT

If the footnotes convert to about $229bn and include both Alphabet currencies at the tranche amounts, the dossier figure is the issuers’ own principal through 30 September, and the Canadian and yen headlines lose to the tranche sums. If the Swiss franc or Australian dollar principal is absent, those amounts were counsel announcements that did not become parent debt, and the 2026 total was high by about $4bn or about $8bn. A Microsoft or Oracle note that is not in the table means the 13 October list was short. Either result settles the calendar row that asks for this confirmation. It is silent on prices.

### UNCERTAIN

- Alphabet’s Swiss franc pricing date is “on or around 3 March.” A few days either side moves the sum by a few hundredths of a billion. The 10 February counsel-note date was not in the Swiss franc series fetched.
- Amazon’s Swiss franc trade date was not stated; 28 May is the issue date used.
- Amazon’s dollar and euro dates are the underwriting dates, not a separately stated trade date.
- The end of the review file, where a supervisor may have locked the rate dates, was not read. This recomputation lands on $228.9bn, which matches the dossier’s $229bn at the rounding the page uses. The worksheet that first produced $81bn and $98bn was not opened.
- 30 September ECB rates were not fetched. They would matter only for a carrying-amount comparison, which is not the scored quantity.
- October current-report lists for Alphabet, Amazon, and Meta were read in the prior pass of this session as empty from 1 October. They were not re-fetched in this continuation.

---

## NOT DONE

- Oracle’s and NVIDIA’s quarterly company-concept files were not fetched, so those two December and November dollar points rest on unsplit year-to-date bridges.
- The supervisor adjudication at the end of the 13 October review was truncated and not read.
- Alphabet’s July capex guidance was not re-read.
- Individual note prospectuses were not opened; face amounts are as given in the fetched review.
- The lease stack and Amazon’s delayed-draw term loan are calendar items and were not scored. The term loan is bank debt, not the bond-face sum and not the operating-cash-flow comparison.
- Epoch AI’s aggregate free-cash-flow series was not fetched, so the calendar’s “crossing zero” projection was not given a number.

## Grok return: pre-registration 3, GPIF July–September 2026

I'll read the calendar and the September note first, then pull the Japan notes and GPIF primary sources they name so the pre-registration is dated to figures already published.The calendar pins the GPIF print to about 6 November and points at the Treasuries synthesis plus the Japan notes. I'll pull those files and the GPIF pages they rely on.The June print is on the GPIF site; the July–September flash is not. Next I’ll pull the quarterly PDFs, the policy-mix page, and the project’s pension-flow figures.The June weight is 25.59% against a 25% target. I’ll take the quarter-end history and the July–September market moves that are already public, so the range comes from rebalancing, not from a guess.Pre-registration, 17 October 2026. July–September 2026 is GPIF’s fiscal 2026 second quarter. The flash is not on the site yet. The weight below is the line the November print will actually carry. A pure JGB buy/sell line is not in that print.

## 1. Domestic-bond weight at 30 September 2026

**QUANTITY.** The domestic-bond share of pension reserves at 30 September 2026, in percent to the two decimals GPIF prints. Source: the fiscal-2026 second-quarter flash, section 2, table 「運用資産額・構成割合（年金積立金全体）」, row 国内債券, column 構成割合［4資産］. Same perimeter as the June flash: GPIF plus the Pension Special Account, trade-date basis, futures notionals included. Yen-hedged foreign bonds and yen short-term assets sit in this row. Policy target, from [the portfolio page](https://www.gpif.go.jp/gpif/portfolio.html), in force since 1 April 2025: 25%, deviation limit ±6% (allowed band 19% to 31%). Bond-versus-equity limit ±9%. Foreign bonds are ±5%.

Publication date: on or about **6 November 2026**. [MHLW’s log](https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/nenkin/nenkin/zaisei/tsumitate/info/index.html) shows the July–September flash on 1 November 2024 and 7 November 2025, both the first Friday of November. 6 November 2026 is that Friday. [GPIF’s 2026 topics page](https://www.gpif.go.jp/topics/2026/), read today, has no forward date. The latest performance item there is the 7 August 2026 first-quarter flash. The project’s calendar row is 2026-11-06.

**LAST OBSERVED VALUE(S).** Section-2 weights, domestic bonds:

| Quarter-end | Weight | Market value | Total reserves | Fetched from |
|---|---:|---:|---:|---|
| 31 Mar 2025 | 27.64% | ¥71.150 trillion | ¥257.418 trillion | [FY2024 review](https://www.gpif.go.jp/operation/32821257gpif/2024_4Q_0704_jp.pdf) |
| 30 Jun 2025 | 26.13% | ¥68.917 trillion | ¥263.763 trillion | [FY2025 Q1 flash](https://www.gpif.go.jp/en/performance/2025_1Q_0801-en.pdf) |
| 30 Sep 2025 | 26.29% | ¥74.276 trillion | ¥282.536 trillion | [FY2025 Q2 flash](https://www.gpif.go.jp/operation/92011372gpif/2025_2Q_1107_jp.pdf) |
| 31 Dec 2025 | 25.29% | ¥74.571 trillion | ¥294.837 trillion | [FY2025 Q3 flash](https://www.gpif.go.jp/en/performance/75943515gpif/2025_3Q_0206_en.pdf) |
| 31 Mar 2026 | 26.91% | ¥80.679 trillion | ¥299.825 trillion | [FY2025 summary](https://www.gpif.go.jp/en/performance/73509681gpif/gpifannual_report_summary_2025_en.pdf) |
| 30 Jun 2026 | **25.59%** | ¥81.998 trillion | ¥320.373 trillion | [FY2026 Q1 flash](https://www.gpif.go.jp/operation/38371785gpif/2026_1Q_0807_jp.pdf) and [the results page](https://www.gpif.go.jp/operation/the-latest-results.html) |

Quarter-to-quarter changes in the weight, in percentage points: −1.51, +0.16, −1.00, +1.62, −1.32. The largest move is 1.62 points. Every print is above 25% and inside 19–31%.

April–June 2026 portfolio returns in that flash: domestic bonds −1.11% (¥−0.848 trillion), foreign bonds +3.13%, domestic equities +14.48%, foreign equities +16.94%, total fund +8.20%. Applying those returns to the 31 March weights (26.91 / 24.48 / 23.81 / 24.80) gives an unrebalanced domestic-bond weight of about 24.6%. The flash printed 25.59%.

**PREDICTION.** **25.6%, range 24.0% to 27.2%.** Width 3.2 percentage points, equal to the last print plus or minus the largest quarter-to-quarter move in the table (1.62 points). The legal band of 19–31% is four times wider and would not test anything.

Six quarter-ends under the current 25% target have sat between 25.29% and 27.64%, and the fund has bought domestic bonds back toward 25% when equities ran ahead, as in April–June. Over July–September the Ministry of Finance 10-year constant-maturity yield went from 2.690% on 30 June (R3, checked to the Ministry file) to 3.073% on 24 September (same note) and **3.092% on 1 October** ([jgbcme.csv](https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/jgbcme.csv)). TOPIX, 3,994.76 in the June flash, closed at 4,108.65 on 30 September ([47NEWS/Fisco](https://www.47news.jp/15015395.html)), about +2.9% in price, against a +14.48% domestic-equity return the quarter before. That mix does not repeat the drift that took the unrebalanced weight to about 24.6%, so the point stays on the last print, 25.6%.

**FALSIFIED IF.** The section-2 domestic-bond 構成割合［4資産］ prints below 24.0% or above 27.2%.

**WHAT IT WOULD TELL THE PROJECT.** A print inside 24.0–27.2% leaves GPIF on the 25% target, inside the cluster already measured. That is the book behind R3’s public-pension line: Flow of Funds transactions, sector 424A, **+32.3 trillion yen** of JGBs from 2024Q1 through 2026Q2 ([jp_flows_periods.csv](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/r3_rates/jp_flows_periods.csv); quarterly path in [jp_flows_quarterly.csv](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/r3_rates/jp_flows_quarterly.csv)). R3 treats GPIF’s domestic-bond inflows, about ¥31 trillion over that window, as a proxy for that sector, and says the proxy is inferred. Japan Macro Advisors’ 10 September call, as recorded in [the Treasuries synthesis, section 3](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-11-Who-Buys-Treasuries-Synthesis.md), is a later move toward about 50%, or ¥32 trillion of buying at a 35% target and ¥80 trillion at 50%. A September weight near 25.6% means that move is not in this book. A print above 27.2%, and any print above 31%, is the weight leaving the rebalancing cluster. R3b, the duration follow-up inside [R3](https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-27-R3-JGB-And-Euro-Area-Bonds.md), is a by-issue stock through 31 August 2026. This flash has no by-issue holdings, so it does not rescore that 16–25% rise in public rate risk.

**UNCERTAIN.** The 30 September yield itself is not in the October Ministry file; 24 September (3.073%) and 1 October (3.092%) bracket it. The March composition note says futures notionals are excluded, while the quarterly flashes include them, so the 26.91% to 25.59% step mixes two bases. NOMURA-BPI, the foreign-bond index and the foreign-equity index for July–September were not fetched, so the 25.6% point is the rebalancing base rate, not a full four-asset drift. The 6 October committee PDFs listed on the topics page were not opened. A policy change already decided there would settle whether the inner ring in this flash is still 25% / ±6%.

## 2. Net allocation to domestic bonds, July–September 2026

**QUANTITY.** GPIF does not print a JGB purchase line in the quarterly flash. The first-quarter 2026 flash and the second-quarter 2025 flash have market value, weight, and 収益額, and no 配分・回収額. That allocation line is annual. FY2025, in the summary above: domestic bonds **+¥14.753 trillion**, foreign bonds +¥2.653 trillion, domestic equities −¥10.693 trillion, foreign equities −¥4.201 trillion. FY2024, in the review above: domestic bonds **+¥5.257 trillion**. Positive means allocation exceeds withdrawal.

The scored number is the quarterly reconstruction of that annual line, fixed now:

- D2 = section-2 domestic-bond 資産額, 億円
- T2 = section-2 合計
- T3 = section-3 運用資産額 at quarter-end (the total that excludes the special account)
- R = section-3(2) domestic-bond 収益額 for the second quarter only, 億円
- Special account at end = T2 − T3
- GPIF-managed domestic bonds at end = D2 − (T2 − T3)
- Start, 30 June 2026 = 819,976 − (3,203,732 − 3,177,596) = **793,840 億円**
- **Net allocation = GPIF-managed end − 793,840 − R**

Units: trillion yen. Positive is net allocation into the domestic-bond bucket. Summed over the four quarters of FY2025 this reconstruction is ¥14.704 trillion, against the published ¥14.753 trillion. The gap is ¥0.05 trillion.

This is not a JGB transaction. R3’s review puts direct JGB holdings at ¥62.1 trillion at 31 March 2026. Domestic bonds that day were ¥80.7 trillion, of which about ¥6.2 trillion was the special account, so JGBs were about four-fifths of the GPIF-managed domestic-bond book. Yen-hedged foreign bonds are inside the same bucket.

**LAST OBSERVED VALUE(S).** Reconstructed GPIF-managed net allocation into domestic bonds:

| Quarter | Net allocation |
|---|---:|
| Apr–Jun 2025 | +¥1.76 trillion |
| Jul–Sep 2025 | +¥5.08 trillion |
| Oct–Dec 2025 | +¥5.34 trillion |
| Jan–Mar 2026 | +¥2.52 trillion |
| Apr–Jun 2026 | +¥5.73 trillion |

All five are net buying. The sample runs from +¥1.76 trillion to +¥5.73 trillion. The mean is +¥4.1 trillion. Sector JGB transactions in the project’s quarterly file average about ¥3.2 trillion a quarter over the ten quarters to 2026Q2, and about ¥5.1 trillion over the latest four (5.96, 5.95, 2.39, 6.07). Same order of magnitude, not the same line: one is a fiscal-quarter domestic-bond allocation, the other is a calendar-quarter JGB transaction for all public pensions.

**PREDICTION.** **+¥4.0 trillion, range +¥1.5 trillion to +¥6.5 trillion.** Width ¥5.0 trillion. The five quarters occupy +1.76 to +5.73; the range is that sample with a small margin. A window wide enough to include a ¥32 trillion quarter would not test the release.

The point is the mean of those five quarters. April–June was the high end (+¥5.73 trillion) in a quarter when equities returned 14% and 17%. July–September does not have that equity move on the prices already public, and every quarter in the sample was still a net allocation, so the point stays at the mean rather than at zero or at the JMA scale.

**FALSIFIED IF.** The reconstructed net allocation is below +¥1.5 trillion or above +¥6.5 trillion. A negative figure, net withdrawal, is a miss. If the flash itself prints a quarterly 配分・回収額 for domestic bonds, that printed number replaces the reconstruction and the same bounds apply.

**WHAT IT WOULD TELL THE PROJECT.** A result inside +¥1.5 to +¥6.5 trillion extends the buying that makes up R3’s +¥32.3 trillion sector total, at the recent pace of a few trillion yen a quarter. It does not fund Japan Macro Advisors’ ¥32–80 trillion shift, and the FY2025 published split funded the domestic-bond allocation from equities, with foreign bonds also receiving money (+¥2.65 trillion), not supplying it. A quarter above +¥6.5 trillion would be faster than any of the five reconstructed quarters and would be the first print in this sample at an accelerated pace, still a fraction of ¥32 trillion. A net withdrawal would break the run of buying in that sample. R3b’s duration stock is unchanged by either result. The synthesis records the ¥32–80 trillion figure as static and undated, so one quarter inside this range retires “already in the September book” and leaves a later target change untested.

**UNCERTAIN.** The special-account stock is the gap between two totals; the flash’s prose note is rounded (“about”). Using T2 − T3, as above, is what matched the annual line. The ¥0.05 trillion FY2025 gap is the tolerance of the identity. Direct JGB holdings were not re-read from the holdings file this session; the ¥62.1 trillion figure is the one in the fetched R3 review. If the second-quarter flash adds a named JGB transaction line, that line is a different series and is not silently substituted.

## 3. Policy target printed in the same flash

**QUANTITY.** The domestic-bond policy weight and the per-asset deviation limit in the inner ring of the same section-2 chart (基本ポートフォリオ, 乖離許容幅).

**LAST OBSERVED VALUE(S).** 25% and ±6%, on the portfolio page, applied 1 April 2025, and printed in the June 2025, September 2025, December 2025 and June 2026 releases fetched above. The prior plan, through 31 March 2025, was 25% with ±7%.

**PREDICTION.** **25% and ±6%, unchanged.** Four flashes under the fifth plan have printed that pair, and the portfolio page still does.

**FALSIFIED IF.** The flash prints a domestic-bond target other than 25%, or a per-asset deviation limit other than ±6%.

**WHAT IT WOULD TELL THE PROJECT.** An unchanged ring means the September book was still run against 25% / ±6%, which is the policy R3’s pension proxy sits under. A different target is the event the synthesis says would scale Japan Macro Advisors’ ¥32 trillion or ¥80 trillion figures, and it would be the policy change the calendar row asks this release to check.

**UNCERTAIN.** The 6 October committee papers were not read. A decision already recorded there, and not yet on the portfolio page, would settle this before November.

## NOT DONE

The 6 October committee PDFs were not opened. The 30 September Ministry yield was not in the file that was fetched. July–September total returns for NOMURA-BPI, the FTSE world government index and MSCI ACWI were not fetched, so there is no full mechanical weight. The holdings-by-issue file was not re-opened. The three sister funds named in the calendar row were not given their own pre-registrations. Bank of Japan Flow of Funds for July–September 2026 is a later release than this flash. No sentence here treats a flow as the cause of a price.

## Grok return: pre-registration 4, Z.1 2026Q3 (holders, fund levels, financing gap)

I'll read the local calendar and the 17 September note first, then fetch the named source notes and the 11 September Z.1 tables so the pre-registrations rest on those base rates.The calendar points at the 11 December Z.1 row and the funding-identity note. I’ll pull those project files and the Fed’s release page next.The Fed’s page dates the 2026Q3 Z.1 for Thursday 10 December, not 11 December. Next I’ll pull the buyer-share note, the registered-fund note, and the 11 September series.The 2026Q3 Financial Accounts print is **Thursday 10 December 2026, at noon**, on the 11 September release page and on FRED. The project calendar row dated 11 December is one day later. Shares below are four-quarter sums of not-seasonally-adjusted flows. No sentence here says a flow moved a price.

The 11 September 2026 vintage is the current FRED vintage (updated 11 September 2026). It reproduces the page’s absorption split.

---

## 1. Who absorbed net Treasury issuance

**QUANTITY.** Two shares of net marketable Treasury issuance over the four quarters **2025Q4–2026Q3**, scored on the 10 December 2026 vintage.

- Numerator, rest of the world: `FU263061105` (bills plus other Treasuries).
- Numerator, money-market funds: `FU633061105` (bills plus other Treasuries).
- Denominator: `FU313161105`, federal government, total marketable Treasury securities, liability, transactions. Not seasonally adjusted, millions of dollars, quarterly. The same five quarters match `FU893061105` (all sectors, asset). E-021 calls this holder split table F.210. The series analyzer does not print a line number.
- Share = 100 × (sum of four quarterly flows) / (sum of four issuance flows), reported to one decimal.
- Source of the base rates: FRED series pages and full histories, last updated 11 September 2026, and the project’s re-sum in E-021.

**LAST OBSERVED.** Page rounding and the unrounded sums from the same vintage:

| Four quarters | Issuance | Rest of world | Money funds |
|---|---:|---:|---:|
| 2024Q3–2025Q2 | $1,615.210bn | $709.055bn, **43.9%** (page: 44%) | $164.128bn, **10.2%** |
| 2025Q3–2026Q2 | $2,359.942bn | $293.760bn, **12.4%** (page: 12%) | $667.526bn, **28.3%** (page: 28%) |

Quarterly flows, billions:

| Quarter | Issuance | Rest of world | Money funds |
|---|---:|---:|---:|
| 2025Q3 | 1,053.303 | 118.328 | 618.320 |
| 2025Q4 | 497.993 | 25.212 | 285.478 |
| 2026Q1 | 571.907 | 128.837 | −91.395 |
| 2026Q2 | 236.739 | 21.383 | −144.877 |

The three quarters that stay in the new window (2025Q4–2026Q2) are already **$1,306.639bn** of issuance, **$175.432bn** for the rest of the world (13.4% of that stub), and **$49.206bn** for money funds. The quarter that rolls off, 2025Q3, is an 11.2% foreign share and a 58.7% money-fund share of that quarter’s issuance.

Third-quarter issuance since 2023 was $858bn, $683bn, and $1,053bn. Third-quarter rest-of-world flows since 2017 ran from $62bn to $237bn; the median is $105bn.

Money funds are no longer a forecast for the quarter. OFR `MMF-MMF_T_TOT-M`, fetched this session, is $3,281.213bn on 30 June 2026, $3,696.649bn on 31 August, and **$3,483.974bn on 30 September**. July–August was +$415.4bn. September was **−$212.7bn**. The third-quarter stock change is **+$202.8bn**. On the quarters checked, that stock change and the Z.1 flow match to a few hundred million (2026Q2: OFR −$145.2bn, Z.1 −$144.877bn; 2025Q3 and 2024Q3 match the same way).

**PREDICTION.**

- Rest of the world: **13.0%**, range **8% to 21%**. Point uses a third-quarter foreign flow of $105bn (the median third quarter since 2017) and third-quarter issuance of $858bn (the middle of the three third quarters since 2023): four-quarter totals $280bn of $2,164bn. The low end of the range is a repeat of 2026Q2’s $21bn foreign flow with a repeat of 2025Q3’s $1,053bn issuance (8.3%). The high end is a repeat of 2024Q3, when foreigners took $237bn of $683bn (the four-quarter share would be 20.7%). That is a 13-point band. It leaves out the 28–45% shares that were normal from 2022 through mid-2025. Since 2022, a one-quarter move in this four-quarter share has usually been a few points and has reached about 14 points.
- Money funds: **11.6%**, range **10% to 13%**. The point adds the OFR third-quarter stock change of $202.8bn to the $49.2bn already in the window, and divides by the same $2,164bn. Across the three observed third-quarter issuance totals since 2023, that locked-in numerator is 10.7%, 11.6%, and 12.7%. The extra width allows issuance a little outside that trio. A four-quarter share near the current 28% would require third-quarter money-fund buying on the scale of the $618bn quarter that is rolling off. September’s print has already removed that path.

**FALSIFIED IF.** On the 10 December vintage, the rest-of-world share is below 8.0% or above 21.0%, or the money-fund share is below 10.0% or above 13.0%. Each share is scored on its own.

**WHAT IT WOULD TELL THE PROJECT.** The page’s measured shift, from a 44% foreign share over the year to 2025Q2 to 12% over the year to 2026Q2, either survives the roll-off of 2025Q3 or it was an artefact of that one quarter. Money funds’ 28% share was mostly 2025Q3 (+$618bn) plus 2025Q4. With September already in the OFR stock, their four-quarter share should fall back toward their 10% share of the prior year. That is a holder-table result. It does not say whether the mix moved yields.

**UNCERTAIN.** September OFR is a stock change. Z.1 has matched it to within about $0.3bn on recent quarters; a break in that match would settle the money-fund numerator. The foreign third quarter is not pinned by a monthly series fetched here. “F.210” is the project’s table name; the line numbers were not on the series-analyzer pages.

---

## 2. Mutual-fund and ETF Treasury levels, and the 2026Q2 revision

**QUANTITY.** Three levels, millions of dollars, market value, not seasonally adjusted, end of quarter, in the 10 December 2026 vintage.

1. Restatement of **2026Q2** `LM653061105`. Mutual funds, Treasury securities. S.124.1 line 4, and F.3.2 line 32. The 11 September figure is the latest-quarter estimate.
2. **2026Q3** `LM653061105`, which the Fed’s method will again publish as an estimate.
3. **2026Q3** `LM563061103`. Exchange-traded funds, Treasury securities. S.124.3 line 3, and F.3.2 line 36. The series analyzer describes this as ICI government-bond ETF total net assets, plus a hybrid-fund portion, minus an estimated money-fund holding inside fixed-income ETFs. It is not a sum of Treasuries held by every ETF.

The parent series of the mutual-fund line, `FL653061003`, says the most recent quarter is “estimated from price indexes” plus estimated transactions, and that earlier quarters are ICI. So 10 December should replace the 2026Q2 estimate with ICI and print 2026Q3 as a new estimate. The 11 September vintage already contains an ETF figure for 2026Q2, so the same lag is assumed for 2026Q3 ETFs.

Closed-end funds, `LM553061103`, are $2.014bn at 2026Q2. They do not move the three-row total at the precision below.

**LAST OBSERVED.** 11 September vintage, millions:

| Quarter | Mutual funds `LM653061105` | ETFs `LM563061103` |
|---|---:|---:|
| 2025Q2 | 1,541,358 | 635,739 |
| 2025Q3 | 1,641,230 | 674,936 |
| 2025Q4 | 1,685,159 | 705,991 |
| 2026Q1 | 1,733,658 | 780,095 |
| 2026Q2 | **1,741,237** (estimate) | **807,612** |

Mutual-fund level change in the estimate quarter was **+$7.579bn**. The estimated flow, `FU653061105`, was **+$14.059bn**, so the implied revaluation is about **−$6.5bn**. The three prior quarters, now on ICI, rose $99.9bn, $43.9bn, and $48.5bn. Their flows were +$86.0bn, +$43.6bn, and +$58.1bn.

ETF level changes from 2024Q2 through 2026Q2, billions: +18.8, +45.7, −13.0, +49.1, +30.8, +39.2, +31.1, +74.1, +27.5. Mean **+$33.7bn**. Seven of the nine lie between +$19bn and +$49bn.

R2b, on this vintage: N-PORT Treasury value grew $788bn from end-2023 to 30 June 2026, and the Z.1 three-row total grew $657bn. The ratio went from 95.5% to **101.8%**. The growth gap is **+$131bn**. The three-row stock at 2026Q2 is $1,741.237 + $807.612 + $2.014 = **$2,550.863bn**. At 101.8%, N-PORT is about **$46bn** above that stock. The $131bn is how far the gap widened over the window, not the end-point difference. R2b says that growth gap decides the scaled arm, which was $449.7bn, $10.3bn short of the $460bn line set in advance.

**PREDICTION.**

- **2026Q2 mutual funds, restated:** **$1,785bn** (revision **+$44bn**), range **$1,770bn to $1,815bn**. The point replaces the estimated +$14bn flow with the median of the last three ICI flows (+$58bn) and keeps the −$6bn revaluation. The range is those three ICI flows ($44bn, $58bn, $86bn) in place of the $14bn estimate. Width about $45bn. A vintage-to-vintage revision history was not available (below), so this width is the recent ICI flow span, not a measured revision-error distribution.
- **2026Q3 mutual funds, as printed (an estimate):** **$1,833bn**, range **$1,750bn to $1,910bn**. The point is the revised 2026Q2 figure plus the median ICI quarterly level change of those three quarters (+$48.5bn). The range stacks the revision band and a new-quarter change of about $0 to $100bn, which is the recent level-change span. Width about $160bn on a $1,741bn stock: one revision plus one quarter, not an open interval.
- **2026Q3 ETFs:** **$841bn**, range **$826bn to $857bn**. Last stock $807.612bn plus the mean quarterly change of +$33.7bn. The range is that stock plus the seven central changes (+$19bn to +$49bn). The 2024Q4 decline (−$13bn) and the 2026Q1 jump (+$74bn) sit outside on purpose. Width about $30bn.

**FALSIFIED IF.** On the 10 December vintage, the restated 2026Q2 mutual-fund level is outside $1,770bn–$1,815bn; or the printed 2026Q3 mutual-fund level is outside $1,750bn–$1,910bn; or the 2026Q3 ETF level is outside $826bn–$857bn. Each is scored on its own.

**WHAT IT WOULD TELL THE PROJECT.** A revision near +$44bn would lift the three-row total by about that amount and bring the end-point ratio from 101.8% to about 100%. The Q2 price-index estimate would then account for the end-point excess of N-PORT over Z.1. The older gap, N-PORT at 95.5% of Z.1 at end-2023, would remain, and so would the ETF definition (government-bond ETF assets, not every ETF’s Treasuries). The scaled arm was $10bn short of its line; a revision of this size is large enough that the script has to be re-run before the “not established” label is kept or dropped. A revision near zero would leave the end-point excess in place and mean the estimate was not the source. Either result is a measurement of the two sources. It is not a finding about yields.

**UNCERTAIN.** The FRED data page with `vintage_date=2026-06-11` returned the 11 September vintage, so the size of past estimate-to-ICI revisions was not measured. The revision range assumes the price-index piece of the Q2 print (−$6bn) was close and that the miss was the flow. The 2026Q3 mutual-fund print is an estimate built on whatever 2026Q2 becomes; the $1,750–$1,910bn band is wide because those two pieces stack. Whether ICI’s ETF table for September is inside the 10 December release is inferred from the 11 September release having contained June.

---

## 3. Nonfinancial corporate financing gap

**QUANTITY.** `FA105005305` and `FU105005305` for **2026Q3**, first print in the 10 December 2026 vintage.

- `FA105005305`: seasonally adjusted annual rate, millions of dollars. Series analyzer: S.11.1 transactions, **line 59**. It equals capital expenditure (`FA105050005`) minus gross saving less net capital transfers paid (`FA106000105`) plus foreign earnings retained abroad (`FA106006065`). FRED’s title is the financing gap.
- `FU105005305`: the same gap, not seasonally adjusted, quarterly dollars, not annualised. The analyzer lists it as the unadjusted form of that line.
- Assumption: the calendar’s “both bases” means these two published forms. A different second concept (for example, a gap that leaves foreign earnings inside saving) was not stated in the files read.

**LAST OBSERVED.** 11 September vintage. Billions:

| Quarter | FA, SAAR | FU, quarterly NSA |
|---|---:|---:|
| 2025Q2 | −249.844 | −95.514 |
| 2025Q3 | −252.822 | −42.361 |
| 2025Q4 | −164.438 | −79.771 |
| 2026Q1 | −734.256 | −152.188 |
| 2026Q2 | −249.632 | −83.489 |

Five consecutive negative SAAR quarters. The clean post-2025Q2 readings, leaving out 2026Q1, are −$253bn, −$164bn, and −$250bn. The funding-identity note, from the prior vintage, had 2026Q1 at −$634.9bn SAAR. The 11 September vintage revised that first print by about **−$99bn SAAR**. The four-quarter average through 2026Q2 is **−$350.3bn SAAR**.

Third-quarter NSA since 2019, billions: +11.6, −58.3, −19.4, +32.5, +40.8, +53.3, **−42.4**. In 2025, the only third quarter inside the current negative run, NSA was 0.67 of the SAAR divided by four. In 2022Q3 the SAAR was −$40bn and the NSA print was +$32bn, so a mildly negative SAAR quarter has printed positive before seasonal adjustment.

**PREDICTION.**

- **FA, 2026Q3: −$250bn SAAR**, range **−$350bn to −$150bn**. The point repeats 2026Q2 and 2025Q2–Q3. The width is about $200bn, the size of the 2025Q3-to-Q4 move (+$88bn) and of the one measured first-print revision (−$99bn). It covers the three clean post-break quarters. It does not stretch to 2026Q1’s −$734bn, which the funding-identity note ties to the one-quarter capital transfer. A later vintage is a different object: this scores the 10 December first print.
- **FU, 2026Q3: −$42bn**, range **−$60bn to −$25bn**. That applies the 2025Q3 seasonal ratio (NSA ≈ 0.67 × SAAR/4) to the SAAR band. One post-break third quarter is the whole seasonal sample.

Inside this SAAR band the four-quarter average stays near −$350bn. A single quarter would have to print above about +$1,150bn SAAR to make that average positive.

**FALSIFIED IF.** The 10 December first print of `FA105005305` for 2026Q3 is above −$150bn or below −$350bn SAAR, or `FU105005305` is above −$25bn or below −$60bn. A positive SAAR print falsifies the FA range. A positive NSA print falsifies the FU range even if the SAAR print stays negative.

**WHAT IT WOULD TELL THE PROJECT.** The tripwire in the calendar and in section 2 of the funding-identity note is whether external funding has opened: a positive gap. A print inside the band extends the negative run to six quarters on the adjusted basis and keeps the sector’s capital expenditure inside internal funds on that line. A positive SAAR print is the tripwire. A negative SAAR print with a positive NSA print would mean the two bases the calendar asked for disagree on the sign of the third quarter, which 2022Q3 shows is possible when the adjusted gap is only mildly negative. The sector discrepancy the funding-identity note puts near $0.7tn a year is unchanged by a print inside this band. This does not say what funded equity prices.

**UNCERTAIN.** “Both bases” is read as FA and FU. The seasonal translation of the NSA third quarter rests on 2025Q3 alone. The −$99bn revision of the 2026Q1 first print is one observation; the score here is the first print, not the following vintage.

---

## NOT DONE

- No prior vintage of `LM653061105` was retrieved. The FRED data page ignored `vintage_date=2026-06-11` and returned 11 September, so the mutual-fund revision band is inferred from recent ICI flows, not from measured estimate-to-ICI errors.
- F.210 line numbers were not on the series-analyzer pages. The share identity was checked by reproducing E-021’s $709bn, $294bn, $668bn, $1,615bn, and $2,360bn from `FU263061105`, `FU633061105`, and `FU313161105`.
- TIC for the third quarter of 2026 was not used. The foreign share is a Z.1 forecast.
- The calendar’s phrase “both bases” is not defined in the files read beyond the series code `FA105005305`. FU is the unadjusted form on the Fed’s series page.
- Nothing was written to disk.
