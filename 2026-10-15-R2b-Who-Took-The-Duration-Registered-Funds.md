# R2b: How much of the new Treasury duration registered funds took, from their own filings (15 Oct 2026)

**Status: FINDING. Supervisor, 15 Oct.** This follows R2
([`2026-09-27-R2-Treasury-Duration-Supply-And-Holders.md`](2026-09-27-R2-Treasury-Duration-Supply-And-Holders.md)). R2 measured
how much rate risk the public absorbed but could not say who took it, because the Fed's Z.1 accounts give holders in dollars, not
maturities. This note answers that for one holder group: registered funds (mutual funds, ETFs, closed-end and interval funds). It
uses the SEC's free Form N-PORT files, which list every fund's holdings line by line, with maturities.

- **How it was built.**
  - Grok batch g4, item 7, set the question and the verdict lines on 14 Oct, before any measurement.
  - Three investigation lenses, a spec, and two adversarial reviews (correctness and practicality).
  - The supervisor re-specified it after the reviews; then a builder agent built it.
  - An independent verifier reproduced every headline number with its own code, to within a millionth of a billion dollars.
  - The spec, with the reviews' amendments as section 10:
    [`_research/2026-10-14-NPORT-Treasury-Duration-Spec.md`](_research/2026-10-14-NPORT-Treasury-Duration-Spec.md).
- **Script:** [`bin/nport_treasury_duration.py`](bin/nport_treasury_duration.py). Its tests are in
  [`bin/test_nport_treasury_duration.py`](bin/test_nport_treasury_duration.py) and run before every build. The Z.1 inputs come
  from [`bin/nport_fetch_z1.py`](bin/nport_fetch_z1.py).
- **Tables:** `data/nport/tsy_*.csv`. `tsy_checks.csv` is the build's own gate: 0 failures.
- **Inputs:**
  - the SEC's quarterly N-PORT data sets, 2024Q1 to 2026Q3: eleven zips, sha256 in `tsy_file_stats.csv`, kept outside the
    repository;
  - R2's cached Treasury security master and end-2023 curve;
  - the Fed's Z.1 tables S.124.1 to S.124.3 (11 Sep 2026 release).

## The verdict lines, set before measurement

- ΔP is the public's added rate risk: R2's +$3,218.3bn of 10-year equivalents at constant end-2023 prices, from end-2023 to
  30 Jun 2026. The last N-PORT report date is 30 Jun, not 31 Aug, so the end point is 30 Jun.
- ΔS is registered funds' change on the same basis. It is computed from the funds' own lines, valued on R2's security master and
  curve.
- **First-order duration sink** if ΔS ≥ $460bn, one-seventh of ΔP. The item's rounder "$0.5trn" is printed beside it.
- **Bystander** if ΔS < $100bn.
- **Participant** in between.
- The verdict is computed for two arms:
  - **Measured:** the funds' N-PORT lines.
  - **Z.1-scaled:** the same holdings rescaled to the Fed's three-row total for mutual funds, ETFs and closed-end funds.
- If the arms disagree, the verdict is "not established".
- The spec's author and one reviewer saw provisional numbers before the build. The lines predate both. The spec author's own
  relative rule was withdrawn for that reason (spec section 10, N1).

## The answer

**Verdict: NOT ESTABLISHED. The two arms straddle the first-order line.** *The measured arm is MEASURED. The Z.1-scaled arm is
HYPOTHESIS: it is a population scaling. The label is the pre-registered rule applied to both.*

| | Measured arm | Z.1-scaled arm |
|---|---:|---:|
| ΔS, end-2023 to 30 Jun 2026 | **$549.2bn** | **$449.7bn** |
| Share of the public's +$3,218.3bn (r) | 17.1% | 14.0% |
| Funds' starting share of the stock (s₀) | 14.5% | 15.2% |
| Excess over pro-rata | +2.5pp (+$81bn) | −1.3pp (−$41bn) |
| Label | first-order sink | participant ($10.3bn short of the line) |

- **The measured arm clears the line.** On the funds' own filings, registered funds took about a sixth of the new duration, a
  little more than their share. It still clears the line on a matched filing vintage ($568.3bn) and on the 2026-06-30 curve
  instead of end-2023 ($517.1bn).
- **The Z.1-scaled arm falls just short.** Rescaled to the Fed's totals, the funds took a little less than their share. It stays
  short in every variant the verifier tried: $443bn to $450bn.
- **The two arms differ because the two sources grew differently.** The funds' N-PORT Treasury value grew by $788bn, Z.1's by
  $657bn. The ratio went from 95.5% at end-2023 to 101.8% at 2026Q2. The +$131bn gap is unexplained, and it alone decides the
  label (spec, OPEN 1).
- **The excess over pro-rata has no established sign,** because the two arms give opposite signs.

**The time path is the firmer result: the funds' share of the added risk rose through the window.** *The measured arm is
MEASURED and the scaled arm HYPOTHESIS. Both agree on the direction.*

| Period | ΔS, measured | r, measured | r, Z.1-scaled | Funds' share at the start |
|---|---:|---:|---:|---:|
| 2024 | $203.2bn | 13.9% | 10.3% | 14.5% |
| 2025 | $184.0bn | 15.4% | 14.4% | 14.5% |
| 2026, first half | $162.1bn | **29.2%** | **22.6%** | 14.5% |

In the first half of 2026 registered funds took between a fifth and three-tenths of the added rate risk, well above their share
on either arm. That half-year accounts for most of the whole-window excess on the measured arm.

**Where it sat: mostly beyond ten years.** *MEASURED.*
- Coupon securities over 20 years: up from $475.9bn to $655.3bn of 10-year equivalents.
- Coupon securities of 10–20 years: up from $246.9bn to $358.1bn.
- Together these are about 53% of ΔS. That is close to their 52% share of the funds' starting stock, so it largely reflects the
  funds' existing maturity mix.
- The full maturity table at both end points is in `tsy_buckets.csv`. It splits bills, coupons, TIPS, FRNs and STRIPS, and gives
  the public's figure for each bucket.

## Checks that would fail if it were wrong

- **R2's own totals.** The build rebuilds the public's 10-year equivalents with R2's functions at all four R2 dates. All are
  within $0.05bn of `duration_supply.csv`.
- **N-PORT against Z.1.** The funds' Treasury value is 95.5% and 101.8% of Z.1's three-row total at the two end points, inside
  the ±10% band.
- **The funds' own interest-rate risk.** For 238 and 350 funds holding at least 90% of their assets in Treasuries, the median
  ratio of reported DV01 to computed DV01 is 0.998 and 0.999. Filers sign DV01 inconsistently, so this checks magnitude only.
- **Tests.** Twenty tests run before every build. Each guard was shown to fail on a broken copy of the code: amendment
  de-duplication off; the filing-lag cut inverted; the home-zip cut removed; the TIPS index ratio not applied.
- **Determinism.** Four runs were byte-identical.

**Sensitivities, from the verifier (not in a committed table).**
- Reading the TIPS rule literally, without a model price, moves ΔS by −$2.4bn.
- Removing the filing-lag cut moves it by −$0.002bn.
- Neither changes either label.

## What this does and does not establish

- **It covers cash Treasuries only.** Treasury futures held by funds are not measured in this landing. A lens estimated their
  10-year equivalents rose by roughly $120bn; that is relayed, not measured.
- **It is a holding share, not a price effect.** Nothing here says that fund buying moved yields. The charter forbids that
  reading.
- **Money-market funds are outside it.** They file Form N-MFP. R2 already places their purchases mainly in bills and short
  coupons. Every other holder is outside this measurement too.
- **It narrows R2's open question only for registered funds.** At about a sixth of the new duration on their own filings, about
  five-sixths sat with other holders. Among those, the offshore hedge funds in Z.1's household row are the leading candidate
  (C-124). That remains HYPOTHESIS.

## Observed vs inferred

- **Observed:** every ΔS, r and bucket figure, from the funds' filings on R2's basis.
- **Inferred:**
  - the population scaling in the Z.1 arm (HYPOTHESIS grade in the variant table);
  - that the unexplained N-PORT–Z.1 gap is a population or valuation difference rather than an error in either source.
