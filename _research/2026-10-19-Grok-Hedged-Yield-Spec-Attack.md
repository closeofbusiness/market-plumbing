# Grok spec attack on the FX-hedged Treasury yield build, 19 Oct 2026 (orchestrator_cursor, fenced read + web; SUCCESS, no breaches, guard equal)

Input, not result. The supervisor accepted the headline change (locked 3-month forward), the plain-subtraction and 1-year variants, the release-timing point and the tighter validation gate; rejected a per-start-date basis as infeasible (only 3 yen days reach n >= 10) and kept the DTCC 3-month basis in the headline with a cross-currency-swap label. Rulings are in _research/2026-10-19-FX-Hedged-Treasury-Yield-Spec.md.

I'll review the spec as written, then check the named reference points and the free-data sources against the live web.The spec is loaded. Next I will test its arithmetic against the market conventions, then fetch the named reference points and the SOFR, €STR, and TONA terms.**VERDICT: BUILD WITH CHANGES.** The load-bearing assumption is that compounding today’s overnight rate for three months, then adding a monthly median of US-reported three-month cross-currency swaps, equals the yield locked by a rolled three-month FX forward.

The section 3.2 algebra is internally consistent. On the yen fixture (Treasury 4.50, SOFR 4.30, TONA 0.50, basis −20bp, 92 days) it produces h = 0.39124. With home currency per dollar, a lower home rate makes the forward below spot, so the hedged yield falls. A negative basis on the home leg lowers it further, which matches the Banque de France statement that a more negative basis makes the dollar hedge more expensive. Weekend-versus-business-day compounding is under 0.1bp a year. Those pieces can stay.

What the headline measures is a different contract from the one the references price.

A three-month FX swap locks the forward. The Bank for International Settlements describes that forward premium as the hedging cost, with the cross-currency basis a residual around it. Construction A instead freezes today’s overnight rate for every day of the horizon. Construction B is the realised overnight path, which is what a floating cross-currency swap pays after the fact. Construction C, the three-month overnight-index swap, is the rate the forward uses, and the spec parks it as a check from October 2024. The committed euro rows are A0, B0 and the EFFR variant: overnight gap, basis omitted.

That proxy is biased whenever policy is expected to move inside the window. The error is roughly the priced change in the US three-month rate minus the priced change in the yen or euro three-month rate. Cuts priced in dollars make A too low a hedged yield; hikes priced at the Bank of Japan do the same. On 6 August 2024 Tradeweb showed the effective fed funds fixing at 5.33 and the 18 September meeting rate at 4.89. A hedge from 6 August to 6 November is 92 days, with about 43 days at 5.33 and 49 days at 4.89, so the three-month average is about 5.10. **The dollar leg alone is about 23bp richer than spot.** A 25bp move fully priced for the days just ahead is worth most of that 25bp on the three-month rate; a 50bp move is worth more. The two legs add when the Fed is expected to ease and the Bank of Japan to tighten. On the BlackRock date itself, 8 September 2026, markets were fully pricing a Bank of Japan hike that month, while a Fed hike was still described as uncertain. Spot TONA misses that hike. The spec’s own “notable” bar is 25bp, and the V1 band is about ±50bp around a whole-percent quote, so this bias passes validation. The same frozen overnight also spreads a one-day SOFR spike across all 92 days; the monthly mean dilutes it, the daily print does not.

Their own fixture shows a second, smaller wedge versus the subtraction publishers use. Naive yield minus rate gap plus basis is 0.50; formula h is 0.391. About 5bp of the 11bp is ACT/360 money-market accrual restated with a 365-day log year (3.80 × 365/360). The rest is daily compounding and the semiannual bond-basis round trip. TD Economics’ hedged yield is exactly the naive form, US 10-year minus (US 3-month minus Japan 3-month), with no basis.

Tenor. The panel compares a 10-year par yield with a three-month hedge. Setser’s point on 18 March 2024 is that a hold to maturity depends on the path of short rates over ten years. Section 0 says the series cannot give that return; the opening sentence still says the yield an investor earns. Ginnie Mae’s public “10yr Total Return Hedged” subtracts a **one-year** hedge cost. BlackRock, the Banque de France and TD use three months. A three-month forward can be the headline only for rolling three-month carry, and it will miss the Ginnie Mae level by the three-month versus one-year forward gap.

Calendar alignment is sound: Tokyo’s close is before the New York Treasury snapshot, and the holiday triples are the right last open dates. The series is still not knowable at that snapshot. SOFR for a date is published the next business morning (the API’s latest print on this Monday is still 15 October, 3.89). €STR for 16 October was published 19 October at 08:00. TONA’s 16–19 October fields are still null at 18:58 JST on 19 October. Final revised history can use the rate dated that day. A same-day ex-ante quote has to use the last rate already released.

The basis sample is the wrong market and a thin one. In April 2025, BIS turnover was $4,015 billion a day in FX swaps and $164 billion in currency swaps. Treasury’s 16 November 2012 determination treats FX swaps and forwards as separate from currency swaps. This build reads cross-currency swaps in the rates zip: 424 yen trades in about 25 months, three of them in October 2024. One monthly median is then written onto every day, mixing starts that cross quarter-end with starts that do not. The formula’s sign is tested. The tape’s sign is tested only by V2, which compares that monthly median with one Bloomberg day inside a band about 20bp wide. V3 cannot catch a flipped basis: with short rates at 5.5% and the 10-year at 4.0–4.5%, the rate gap alone keeps the hedged carry negative.

## REQUIRED CHANGES

1. Make the locked three-month forward the only headline (C, or the Du–Keerati–Schreger all-in forward premium where it exists); keep A and B as diagnostics of the expectations wedge and of a floating swap.
   The forward is the hedge that is priced and rolled. https://www.bis.org/publications/global-fx-markets-when-hedging-takes-centre-stage.pdf

2. Score the headline against forward-based prints, and treat a median gap above 25bp as a failed build.
   On 8 September 2026 a Bank of Japan hike was fully priced, so spot overnight is not that forward; the current ±50bp band lets the bias through. https://www.blackrock.com/us/individual/literature/market-commentary/weekly-investment-commentary-en-us-20260908-why-japan-matters-for-us-bond-market-investors.pdf

3. Publish the plain subtraction (Treasury yield minus three-month rate gap, basis shown separately) as a scored series next to the bond-basis formula.
   Public hedged yields use that subtraction; the fixture differs by 11bp. https://economics.td.com/gbl-what-happens-in-japan-may-not-stay-in-japan

4. Report the DTCC three-month cell as a US-reported currency-swap median, and keep it out of the headline until it tracks FX-swap forward points.
   Currency-swap turnover was $164 billion a day against $4,015 billion in FX swaps in April 2025. https://www.bis.org/publications/global-fx-markets-when-hedging-takes-centre-stage.pdf and https://home.treasury.gov/news/press-releases/tg1773

5. Give each start date its own three-month basis, and separate windows that contain a quarter-end.
   The premium was 35bp on 9 April 2025 and 15–20bp at the start of 2026; a monthly median cannot be both. https://www.banque-france.fr/en/publications-and-statistics/publications/are-foreign-investors-more-cautious-over-us-dollar

6. Label the result as rolling three-month carry, and add a one-year forward variant before any comparison with Ginnie Mae or with hold-to-maturity language.
   Ginnie Mae subtracts a one-year hedge; Setser ties maturity value to the ten-year path of short rates. https://www.ginniemae.gov/s3/sites/default/files/listing_pdfs/global_market_analysis_oct24.pdf and https://www.cfr.org/articles/japanese-bid-foreign-bonds-after-end-yield-curve-control

7. Keep yen month-by-month rows uncommitted, and label any euro derivative as derived.
   Bank of Japan site terms exclude commercial copying; ESCB reuse allows free use if the source is cited and the statistics are left unmodified. https://www.boj.or.jp/en/about/copyright.htm and https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html

A practitioner would keep the identity, the day-count guards, the SOFR-index check, and the licence hold. They would drop A as “the” hedged yield, drop V3 as a level test, and add the one-year series and the plain subtraction so the build can hit the prints below.

## REFERENCE POINTS

- 8 Sep 2026, yen, hedged 10-year about 2% against a JGB about 3%, three-month forwards. https://www.blackrock.com/us/individual/literature/market-commentary/weekly-investment-commentary-en-us-20260908-why-japan-matters-for-us-bond-market-investors.pdf — “versus 2% on a 10-year Treasury after hedging”
- 13 Apr 2026, yen, three-month basis premium 35bp on 9 Apr 2025; 15–20bp in early 2026. https://www.banque-france.fr/en/publications-and-statistics/publications/are-foreign-investors-more-cautious-over-us-dollar — “pay a yield premium of 35 basis points”
- 18 Mar 2024, yen, US short rates 5.5%, Treasury 4.0–4.5%, JGB about 75bp. https://www.cfr.org/articles/japanese-bid-foreign-bonds-after-end-yield-curve-control — “isn’t the current difference in short-term interest rates”
- Month-end Sep 2024, yen hedged 10-year 0.09%; euro hedged 10-year 2.48%; one-year hedge. https://www.ginniemae.gov/s3/sites/default/files/listing_pdfs/global_market_analysis_oct24.pdf — “subtracting the 1 yr hedge cost for JPY and EUR”
- 31 Mar 2026, yen, hedged Treasury about 1.3% against a JGB about 2.3%. https://economics.td.com/gbl-what-happens-in-japan-may-not-stay-in-japan — “closer to 1.3% on a fully hedged U.S. Treasury”
- Jan–Dec 2022, yen and euro, three-month FX-swap forward premium from 0.3% to 5.5% (USDJPY) and 0.7% to 3.5% (EURUSD). https://www.bis.org/publications/global-fx-markets-when-hedging-takes-centre-stage.pdf — “forward premium increased from 0.3% to 5.5% for USDJPY”

## SOURCES

- SOFR, New York Fed API. Fetched https://markets.newyorkfed.org/api/rates/secured/sofr/last/1.json — **WORKS** (15 Oct 2026, 3.89, no key). Terms fetched https://www.newyorkfed.org/privacy/termsofuse — personal or business use, automated access allowed, fixed reference-rate notice, modifications labelled.
- €STR, ECB API. Fetched https://data-api.ecb.europa.eu/service/data/EST/B.EU000A2X2A25.WT?lastNObservations=1&format=csvdata — **WORKS** (16 Oct 2026, 2.441, no key). Product page https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_short-term_rate/html/index.en.html — “does not charge for the €STR or license its use.” Reuse policy: free, including commercial, source cited, statistics unmodified.
- TONA, Bank of Japan API. Fetched https://www.stat-search.boj.or.jp/api/v1/getDataCode?format=csv&lang=en&db=FM01&code=STRDCLUCON&startDate=202610&endDate=202610 — **WORKS** (keyless CSV, `STATUS,200`; 15 Oct 2026 = 1.228; 16–19 Oct null). Copyright page: credit required, commercial copying excluded. API notice https://www.stat-search.boj.or.jp/info/api_notice_en.pdf — notify the Bank if a service is released; prescribed credit; no fee stated.

## UNCERTAIN

The 23bp figure is an average built from the fetched 5.33 and 4.89 meeting rates, not a fetched three-month OIS print. The €STR page and the TONA row say “percent,” and the ACT/360 and ACT/365 labels were not on those responses. The Bank of Japan copyright page says linked sites are outside it; it does not say whether `stat-search.boj.or.jp` is included. Null TONA on 16 October is unpublished rather than a holiday only by the surrounding dates. The Du–Keerati–Schreger sign, the DTCC spread-leg field, and `ea_semiannual` were not opened; only this spec was read from disk.
