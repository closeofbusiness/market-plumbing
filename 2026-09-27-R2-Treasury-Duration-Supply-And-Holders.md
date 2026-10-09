# R2 — How much Treasury duration the public had to absorb, and who bought (27 Sep 2026)

**Status: FINDING, corrected after outside review. Supervisor, 27 Sep.** This is the second rates pass: the charter's question 2
(money, as measurement) for US Treasuries. It follows R1 ([`2026-09-27-R1-Treasury-10y-Decomposition.md`](2026-09-27-R1-Treasury-10y-Decomposition.md)).
- **Corrected 27 Sep** after Grok's adversarial review (R12R). The headline survived: about 36% more rate risk at constant
  yields. Three framings did not:
  - whether duration grew faster than face value depends on the weighting (C-122);
  - the Fed's share is a range, not 4% (C-123);
  - the buyer table counted state and local pension funds twice, and placed offshore hedge funds in the wrong row (C-124).
  The adjudication is at the end of [`_research/2026-09-27-R12R-Rates-Review-Return.md`](_research/2026-09-27-R12R-Rates-Review-Return.md).
- **Script:** [`bin/r2_duration_supply.py`](bin/r2_duration_supply.py), written by a build agent to the supervisor's spec. The
  supervisor added the fixed-curve, par-weighted and DV01 measures.
- **Tables:** [`data/r2_rates/`](data/r2_rates/). The 52 checks in `checks.csv` all pass. They test par totals, bills and the
  Fed's holdings against MSPD Table 1 and the H.4.1. They do not test any duration figure, because no published series was found
  to test those against.
- **Inputs, supply:** the Treasury's security-level Monthly Statement of the Public Debt (Table 3), the New York Fed's
  security-level holdings for the Fed (SOMA), and the Treasury par curves.
- **Inputs, buyers:** the Fed's Financial Accounts (Z.1, 11 Sep 2026 vintage), taken from
  [`2026-09-12-N2c-Closure-Refresh-2026Q2.md`](2026-09-12-N2c-Closure-Refresh-2026Q2.md).

## Why duration, not dollars

A dollar of bills adds almost no interest-rate risk to the market; a dollar of 30-year bonds adds a lot. Supply is therefore
measured in duration. How duration is weighted changes the answer (C-122), so three weightings are reported:
- **10-year equivalents:** each security's market value times its duration, divided by the duration of a 10-year bond. That puts
  the stock in units of "10-year bonds' worth of rate risk". It is measured two ways:
  - **at market prices,** the risk actually held on each date;
  - **at constant end-2023 prices,** each date's securities priced on the end-2023 curve. This isolates quantity (issuance,
    runoff, ageing) from the price effect of yield moves.
- **Par-weighted duration:** face value times modified duration, the New York Fed's convention for the Fed's own portfolio. It
  ignores a bond's premium or discount to par.
- **DV01 at market prices:** the dollar loss from a one-basis-point rise in yields.

## The answer

1. **The public had to absorb about 36% more rate risk at constant yields.** Held outside the Fed, 10-year equivalents rose from
   $9.5trn to $12.9trn at constant end-2023 prices between end-2023 and 31 Aug 2026: +$3.4trn. At market prices the rise is
   +$2.4trn (+25%), because higher yields cut market values and durations; DV01 rose 20%. *MEASURED; derived with a pricing
   model. Grok's tests of other curves put the constant-price rise at 35.7–36.3%.*
   - **Per face dollar, the debt did not get longer.** Face value held by the public rose 26%. Weighted by par, the public's
     duration rose 25% on the fixed curve and 21% on each date's own curve. Its average modified duration per face dollar fell
     from 4.22 to 4.05 years.
   - The constant-price measure rose faster than face value because new issues carry higher coupons. On a fixed low curve a
     high-coupon bond is priced above par, and market-value weighting counts that premium as extra rate risk.
2. **Treasury issuance supplied most of it. The Fed's share is 4% to about 13%, depending on the measure.**
   - **Counting only the Fed's own holdings:** at constant prices its 10-year equivalents fell $0.14trn over the window, about 4%
     of the public's +$3.4trn. They fell $0.20trn in 2024 and rose $0.06trn in 2025–26. Runoff ended on 1 Dec 2025. In 2025,
     reinvested maturing coupons offset ageing; the Fed's bill purchases began in mid-December 2025.
   - **Counting what Treasury had to refinance:** the Fed's Treasury holdings fell $601bn from 27 Dec 2023 to their trough on
     3 Dec 2025, $575bn of it coupon securities. Refinanced in the coupon mix of those months, that runoff put about
     $0.32–0.43trn of 10-year equivalents on the public, 9–13% (Grok's calculation, R12R). Refinanced with bills, it added almost
     none. Which Treasury did is not established here.
   - At market prices the Fed's holdings fell $0.43trn, mostly because their value fell. Its 2026 purchases added face value
     (+$0.32trn from end-2025 to August), mostly bills, but almost no duration.
   - *MEASURED (the 4%); BOUNDED (a ceiling of about 13%).*
3. **Bills rose as a share of all marketable debt, but not of the public's holdings.** Bills rose from 21.5% to 22.8% of
   marketable debt. The public's bill share fell from 25.3% to 24.6%, because the Fed's bills rose from $222bn to $542bn.
   Nominal coupon securities with more than 10 years to run grew 29%, from $4.2trn to $5.4trn. The average coupon on the stock
   rose from 2.4% to 3.3%, as higher-coupon issues replaced low-coupon 2020–21 bonds. *MEASURED.*
4. **Who bought, in dollars (Z.1 flows, 2024:Q1–2026:Q2, the equity window):**

   | Buyer | Net purchases |
   |---|---|
   | Rest of the world | $1.33trn |
   | Money-market funds | $1.01trn: bills, floating-rate notes and coupon securities within 397 days of maturity. Z.1 splits it: bills +$451.6bn (45%), other Treasuries +$560.5bn (55%) (FU633061110 / FU633061120, 9 Oct) |
   | Mutual funds, ETFs and closed-end funds | $0.64trn |
   | Banks | $0.49trn |
   | Households and nonprofits: a Z.1 residual, plus the new domestic hedge-fund sector (see item 5) | $0.46trn |
   | State and local governments, GSEs, corporates | $0.42trn |
   | Insurers and pensions, including state and local pension funds | $0.41trn |
   | Broker-dealers | $0.23trn |
   | The Fed | −$0.34trn |

   Net issuance was $4.65trn. The nine rows sum to $4.64trn, $12bn short, which is the table's own diagnostic. **[9 Oct: the $12bn is one omitted sector, nonfinancial noncorporate business (Z.1 FU113061003, +$12.3bn over the window; re-derived by an agent and checked by the supervisor against the 11 Sep Z.1 file). With it the rows close to within $0.4bn.]** An earlier
   version counted state and local pension funds twice, and its rows exceeded issuance by $132bn (C-124). *MEASURED, dollar flows
   at the stated vintage (large revisions happen; see the N2c refresh).*
5. **Which buyers took the duration is not measured.** Z.1 gives dollars, not maturities. Rule 2a-7 caps the maturities money
   funds may hold, so they took little of the duration, and nearly all of it went to the other buyers. How it split among them is
   not measured on free data. *HYPOTHESIS.*
   - **The household row is likely to be largely offshore hedge funds.** Offshore funds belong to the rest of the world. But TIC,
     the source for the rest of the world, misses most of their Treasuries: Fed staff put the shortfall at about $1.4trn at
     end-2024 (FEDS Notes, 15 Oct 2025). Z.1 computes households as a residual, so the missed holdings land in the household row.
     The Z.1's new table for foreign hedge funds puts their Treasuries, net of short sales, at $1.30trn at end-2023 and $1.81trn
     in 2026Q1, and the September 2026 release did not move them into the rest of the world (C-124). This is inferred, not
     measured.
   - Domestic hedge funds have been a separate Z.1 sector since the September 2026 release, holding about $0.1trn of Treasuries
     net of short sales. N2c adds them to the household row (+$21bn over the window).
   - Fed staff put the cash–futures basis trade at about $0.83trn in September 2025.

   So part of the duration went to levered, repo-financed buyers. That is where this question meets the programme's
   collateral and shadow-money channels.
6. **The link to R1 is timing, not cause.** The public absorbed about 36% more rate risk at constant yields over the same months
   in which the curve steepened by 60bp and both models' term premium rose. That fits a supply-and-premium story, but it is not a
   test of one. R1 shows the premium split rests on the models' long-horizon expectations, which the surveys dispute. And the
   charter forbids claiming that flows or official buying caused a yield move. *HYPOTHESIS.*

## The supply tables

**10-year equivalents, in $bn, and face value:**

| date | public, market prices | public, constant prices | Fed, market prices | Fed, constant prices | public face value | public average maturity (years) |
|---|---:|---:|---:|---:|---:|---:|
| 2023-12-31 | 9,539 | 9,539 | 3,320 | 3,320 | 21,576 | 5.32 |
| 2024-12-31 | 10,491 | 11,004 | 2,942 | 3,121 | 23,985 | 5.37 |
| 2025-12-31 | 11,627 | 12,201 | 2,952 | 3,126 | 26,039 | 5.38 |
| 2026-06-30 | 12,033 | 12,757 | 2,954 | 3,162 | 26,594 | 5.47 |
| 2026-08-31 | 11,936 | 12,943 | 2,893 | 3,178 | 27,278 | 5.39 |

| period | public, constant prices | Fed, constant prices | public face value |
|---|---:|---:|---:|
| 2024 | +1,465 | −199 | +2,409 |
| 2025 | +1,198 | +5 | +2,054 |
| 2026 to 30 Jun | +556 | +37 | +555 |
| 30 Jun to 31 Aug | +186 | +16 | +684 |
| end-2023 to 31 Aug 2026 | **+3,404** | **−142** | **+5,703** |

**The public's duration under the other two weightings:**

| date | par-weighted, own curve ($bn-years) | par-weighted, end-2023 curve ($bn-years) | DV01 at market prices ($mn per bp) |
|---|---:|---:|---:|
| 2023-12-31 | 91,043 | 91,043 | 7,844 |
| 2024-12-31 | 99,334 | 101,090 | 8,342 |
| 2025-12-31 | 107,288 | 108,914 | 9,424 |
| 2026-06-30 | 110,353 | 112,490 | 9,633 |
| 2026-08-31 | 110,448 | 113,563 | 9,414 |
| **change, end-2023 to 31 Aug 2026** | **+21.3%** | **+24.7%** | **+20.0%** |

Against these, the public's face value rose 26.4% and its 10-year equivalents 35.7% at constant prices and 25.1% at market
prices. Grok's review got a par-weighted rise of 24.9% on fixed curves and 26.5% on own curves; the own-curve gap is unresolved **[9 Oct: an independent engine reproduces our +21.3% on own curves and gets +24.8% on fixed curves; Grok's 26.5% does not reproduce on any curve, and lies on the wrong side, since rising yields shorten own-curve duration]**,
and on either figure par-weighted duration grew no faster than face value.

The Fed's holdings are the New York Fed's weekly figures on the Wednesday on or before each month-end.

**Checks:**
- The Treasury's totals and bills match MSPD Table 1 to within 0.02%. The small gap is the Federal Financing Bank, which is
  intragovernmental.
- The Fed's holdings match the H.4.1 to within 0.06% (exactly on four of the five dates).
- Bills on 31 Jul 2026 match the monitor's figure.
- None of these tests a duration figure.

**Method notes:**
- Bills use the money-market approximation.
- Floating-rate notes are given a duration of 0.02 years.
- TIPS are priced on the real curve and treated as comparable to nominal duration.
- The curve is interpolated linearly and extrapolated flat, so TIPS with under five years to run take the 5-year real yield.
- Clean prices are used; accrued interest is ignored.
- Matured but unpresented notes are counted at par with no duration.
- Par-weighted duration is face value times modified duration. DV01 is market value times modified duration times 0.0001.

All of these are in the script's docstring.

## What this does and does not establish

- **It establishes how much rate risk the public had to absorb at constant yields, and that Treasury issuance supplied most of
  it.** The Fed's share is between 4% and about 13%, depending on the measure.
- **It does not establish who took the duration,** or that absorbing it raised term premia.
- **It covers the US only.** JGBs and euro-area government bonds are next (R3).

## Next

- **Split the rest of the world** into official and private for the same window. TIC holdings by country give the official
  line, but windows must be matched (C-069).
- **Find free sources of maturity by holder.** Examples to check are insurers' Schedule D filings, banks' Call Report maturity
  buckets and money funds' N-MFP holdings by security type, which would give a partial duration split.
- **Narrow the Fed's share.** Treasury's own attribution of issuance to Fed redemptions (the TBAC financing tables) would place
  it within the 4–13% range.
- **R3: JGBs and euro-area government bonds.**

## Observed vs inferred

**Observed:** security-level supply and Fed holdings, the Fed's runoff, and Z.1 flows.
**Derived by a stated method** (graded MEASURED, and dependent on the method): every duration measure, including the
constant-price measure.
**Inferred:** the refinancing range for the Fed's share; that the household row is largely offshore hedge funds; and that the extra
duration went to buyers other than money-market funds.

### Follow-up, 8 October 2026: does Treasury say how it refinanced the Fed's runoff?

**No.** This was the follow-up that might have narrowed the Fed's 4–13% share (C-123). Treasury publishes
the dollars, not the maturities. Its quarterly Sources and Uses tables carry a memo line of SOMA
redemptions. Its advisory committee (TBAC) defines privately-held borrowing as total borrowing plus those
redemptions. **Nothing it publishes says which maturities replaced them.** So the 13% upper bound stays a
counterfactual about total issuance, not a datum.

- **Redemptions, 2024Q1–2025Q4:** $621bn on Treasury's cash basis. The NY Fed shows a $601.4bn par
  decline in the Fed's Treasury holdings (27 Dec 2023 to 3 Dec 2025, $26.9bn of it bills). The gap is
  TIPS inflation compensation, about $20bn, which is an agent estimate. The supervisor re-derived the
  $601.4bn and the bills figure from the NY Fed's SOMA summary.
- **2026:** none. The Fed has rolled over all principal since 1 Dec 2025.
- **What was redeemed:** about $599bn coupons, TIPS and FRNs, and about $22bn bills. This comes from the
  gap between total and privately-held net issuance, which matches the memo in every quarter. It
  describes what the Fed redeemed, not what Treasury issued in its place.
- **Coupon auction sizes were held constant from February 2024** (refunding statements). Total net
  issuance over the eight quarters was about $872bn of bills and $3,194bn of coupons, FRNs and TIPS.
- **Sources** (gathered by a Sonnet agent; URLs in its working files, not committed):
  - Treasury marketable-borrowing press releases, jy1851 (30 Oct 2023) to sb0584 (3 Aug 2026);
  - the Sources and Uses tables and TBAC combined charts, 2023Q4 to 2026Q3;
  - the Quarterly Release Data xls (16 Jul 2026);
  - the NY Fed SOMA API.

The only thing that would settle the maturity question is a written answer from Treasury's Office of
Debt Management. That route is not taken.

### Follow-up, 9 October 2026: hedge funds' Treasury-futures positioning (CFTC)

The basis-trade test the programme prescribed now has data. `bin/pull_cftc_tff.py` pulls the CFTC's Traders in Financial Futures
(futures only, free) for the six CBOT Treasury contracts, weekly from 2018. Leveraged funds' aggregate net short:

| report date | contract face | 10-year equivalents (fixed CME DV01s) |
|---|---:|---:|
| 26 Dec 2023 | −$774bn | −$533bn |
| 30 Dec 2025 | −$1,154bn | −$711bn |
| 30 Jun 2026 | −$918bn | −$666bn |
| 29 Sep 2026 | −$774bn | −$599bn |

- **Pattern.** The short built through 2024–25 and has since unwound by about a third on face value (by a sixth in 10-year
  equivalents). On face value it is back to its end-2023 level.
- **Form PF.** Qualifying hedge funds' Treasury long-minus-short rose from $350bn to $864bn between end-2023 and 30 Jun 2026.
  Their repo borrowing rose from $2.0trn to $3.4trn.
- **Caveats.** The 10-year equivalents carry about ±25% from the DV01 source. They come second-hand from CME material, because
  cmegroup.com refused a scripted fetch. No causation is read from the comparison.
- **What it does not test.** C-124's inference, that the Z.1 household row is largely offshore hedge funds, needs holder-side data
  this series does not have.

An older ratio in the register did not reproduce on this data; it is C-129.

