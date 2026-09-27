# R2 — How much Treasury duration the public had to absorb, and who bought (27 Sep 2026)

**Status: FINDING. Supervisor, 27 Sep.** This is the second rates pass: the charter's question 2 (money, as measurement) for US
Treasuries. It follows R1 ([`2026-09-27-R1-Treasury-10y-Decomposition.md`](2026-09-27-R1-Treasury-10y-Decomposition.md)).
- **Script:** [`bin/r2_duration_supply.py`](bin/r2_duration_supply.py), written by a build agent to the supervisor's spec. The
  supervisor added the fixed-curve measure.
- **Tables:** [`data/r2_rates/`](data/r2_rates/); all 52 checks pass (`checks.csv`).
- **Inputs, supply:** the Treasury's security-level Monthly Statement of the Public Debt (Table 3), the New York Fed's
  security-level holdings for the Fed (SOMA), and the Treasury par curves.
- **Inputs, buyers:** the Fed's Financial Accounts (Z.1, 11 Sep 2026 vintage), taken from
  [`2026-09-12-N2c-Closure-Refresh-2026Q2.md`](2026-09-12-N2c-Closure-Refresh-2026Q2.md).

## Why duration, not dollars

A dollar of bills adds almost no interest-rate risk to the market; a dollar of 30-year bonds adds a lot. Supply is therefore
measured here in **10-year equivalents**: each security's market value times its duration, divided by the duration of a 10-year
bond. That puts the whole stock in units of "10-year bonds' worth of rate risk". The stock is measured two ways:
- **At market prices:** the risk actually held on each date.
- **At constant end-2023 prices:** each date's securities priced on the end-2023 curve. This isolates quantity (issuance, runoff,
  ageing) from the price effect of yield moves.

## The answer

1. **The public had to absorb about 36% more duration.** Held outside the Fed, 10-year equivalents rose from $9.5trn to $12.9trn
   at constant prices between end-2023 and 31 Aug 2026: +$3.4trn. At market prices the rise is +$2.4trn (+25%), because higher
   yields cut market values and durations by about $1.0trn. Face value held by the public rose 26%, so **duration supply grew
   faster than face value**. *MEASURED; derived, and every check passes.*
2. **Treasury issuance supplied it, not the Fed's runoff.** At constant prices, the Fed's holdings fell $0.14trn of 10-year
   equivalents over the window: −$0.20trn in 2024, then +$0.06trn in 2025–26 as it resumed buying. So about 96% of the public's
   extra duration came from Treasury's net issuance. At market prices the Fed's holdings fell $0.43trn, mostly because their
   value fell. Its 2026 purchases added face value (+$0.32trn from end-2025 to August), mostly bills, but almost no duration.
   *MEASURED.*
3. **Issuance shifted toward bills, yet duration still outgrew face value.** Bills rose from 21.5% to 22.8% of marketable debt.
   Nominal coupon securities with more than 10 years to run grew faster still: 29%, from $4.2trn to $5.4trn. And the average
   coupon on the stock rose from 2.4% to 3.3%, as higher-coupon issues replaced low-coupon 2020–21 bonds, which at a fixed curve
   carry less rate risk per face dollar. *MEASURED.*
4. **Who bought, in dollars (Z.1 flows, 2024:Q1–2026:Q2, the equity window):**

   | Buyer | Net purchases |
   |---|---|
   | Rest of the world | $1.33trn |
   | Money-market funds | $1.01trn, bills and very short paper |
   | Mutual funds, ETFs and closed-end funds | $0.64trn |
   | Insurers and pensions | $0.55trn |
   | Banks | $0.49trn |
   | Households and nonprofits (a Z.1 residual that includes domestic hedge funds) | $0.46trn |
   | State and local governments, GSEs, corporates | $0.42trn |
   | Broker-dealers | $0.23trn |
   | The Fed | −$0.34trn |

   Net issuance was $4.65trn. The nine rows overlap slightly: their sum exceeds net issuance by $132bn, which is the table's own
   diagnostic. *MEASURED, dollar flows at the stated vintage (large revisions happen; see the N2c refresh).*
5. **Which buyers took the duration is not measured.** Z.1 gives dollars, not maturities. Money-market funds took bills, so
   nearly all the extra duration went to the other buyers. How it split among them is not measured on free data. *HYPOTHESIS.*
   - The rest of the world includes hedge funds domiciled offshore. TIC data undercount their Treasury holdings, and Fed staff
     put Cayman funds at $1.85trn at end-2024.
   - Domestic hedge funds sit inside the household residual.
   - Fed staff put the cash–futures basis trade at about $0.83trn in September 2025.

   So part of the duration went to levered, repo-financed buyers. That is where this question meets the programme's
   collateral and shadow-money channels.
6. **The link to R1 is timing, not cause.** The public absorbed about 36% more duration over the same months in which the curve
   steepened by 60bp and both models' term premium rose. That fits a supply-and-premium story, but it is not a test of one. R1
   shows the premium split itself cannot be measured, and the charter forbids claiming that flows or official buying caused a
   yield move. *HYPOTHESIS.*

## The supply tables, in $bn of 10-year equivalents unless stated

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

The Fed's holdings are the New York Fed's weekly figures on the Wednesday on or before each month-end.

**Checks:**
- The Treasury's totals and bills match MSPD Table 1 to within 0.02%. The small gap is the Federal Financing Bank, which is
  intragovernmental.
- The Fed's holdings match the H.4.1 to within 0.06% (exactly on four of the five dates).
- Bills on 31 Jul 2026 match the monitor's figure.

**Method notes:**
- Bills use the money-market approximation.
- Floating-rate notes are given a duration of 0.02 years.
- TIPS are priced on the real curve and treated as comparable to nominal duration.
- The curve is interpolated linearly and extrapolated flat, so TIPS with under five years to run take the 5-year real yield.
- Clean prices are used; accrued interest is ignored.
- Matured but unpresented notes are counted at par with no duration.

All of these are in the script's docstring.

## What this does and does not establish

- **It establishes how much duration the public had to absorb, and where it came from:** Treasury issuance, not the Fed's
  runoff.
- **It does not establish who took the duration,** or that absorbing it raised term premia.
- **It covers the US only.** JGBs and euro-area government bonds are next (R3).

## Next

- **Split the rest of the world** into official and private for the same window. TIC holdings by country give the official
  line, but windows must be matched (C-069).
- **Find free sources of maturity by holder.** Examples to check are insurers' Schedule D filings and banks' Call Report
  maturity buckets, which would give a partial duration split.
- **R3: JGBs and euro-area government bonds.**

## Observed vs inferred

**Observed:** security-level supply and Fed holdings, and Z.1 flows. **Inferred:** the pricing and duration approximations; the
split between quantity and valuation (the constant-price measure); and the reading that the extra duration went to buyers other
than money-market funds.
