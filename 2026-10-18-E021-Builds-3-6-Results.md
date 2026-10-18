# Four tests set in advance: oil positioning, the yen, gold and global yields (E-021 builds 3-6), 18 Oct 2026

**Status: RESULT for four builds; one more (the JODI world oil ledger) runs its test after JODI's 21 October update.**
Each test's design was attacked from outside (Grok batch g7), rewritten, reviewed a second time, and committed to this public
repository before its data were run. A builder ran it once. An independent verifier then rebuilt each headline number with its own
code (recorded in each build's commit message; the oil build's own check row V01 still reads PENDING until it is frozen). The FX
build's README notes that its primary regressor was chosen after looking at the yield series (not the yen), which it discloses. Every number below is descriptive: it says how two series moved together, not that one moved the other.

## What the four tests found

| Question | Answer, in one line | Verdict (rule fixed in advance) | Where |
|---|---|---|---|
| Does a change in funds' oil positions lead the next week's price? | No. WTI correlation −0.011 over 731 weeks (Sep 2009 to Mar 2024, futures prices); Brent +0.030 over 819 weeks (2011 to Sep 2026, spot prices as a proxy). No lead larger than a correlation of 0.083 (WTI) or 0.105 (Brent) was detected at 95%. | AGAINST, both | [`data/cot_horizons/`](data/cot_horizons/README.md) |
| Does the US-Japan two-year yield gap account for the yen's fall since March 2024? | No. Over 118 weeks from late March 2024 to mid-September 2026 (intervention weeks and two weeks with a stale quote left out) the yen fell about 13% in log terms while the gap narrowed by 0.9 points (both summed over the kept weeks; over all 130 weeks the net yen fall was about 4%, because it strengthened in the intervention weeks, and the gap narrowed 1.6 points). Week to week a narrower gap went with a stronger yen (slope 0.058 per point, p < 0.001), so the gap term points the other way; the fall sits in the constant term. | POINTS THE OTHER WAY | [`data/fx_rate_gap/`](data/fx_rate_gap/README.md) |
| Does gold move against US real yields? | On average, yes: over 2006 to 2026, in months when the 10-year real yield rose one point more, gold's monthly average price was about 7.7% lower, holding the dollar fixed (95% band 4.6% to 10.6%). Since December 2021 the association is weaker (−0.03 and −0.04 log points per point in two sub-periods chosen after the fact) and both bands include zero. | SUPPORTS (the band's upper end is just past the line) | [`data/gold_real_yield/`](data/gold_real_yield/README.md) |
| Do the four big 10-year yields move together more now than in 2018-19? | No reliable change found. One common factor accounted for 0.78 of the weekly variation of the US, German, UK and Japanese yields in 2018-19 and 0.71 in 2024-26; the test cannot tell that drop from zero, and it would need a change of about 0.19 to see one reliably. | INCONCLUSIVE | [`data/r15_yield_comovement/`](data/r15_yield_comovement/README.md) |

**What the results do not say.**
- The oil result says positions did not *lead* prices week by week. Positions and prices still moved together in the same week (over these samples, correlation about 0.45 for WTI and 0.42 for Brent; since January 2024 Brent's is the higher).
- The yen result does not say what moved the yen. It says the two-year gap, week to week, cannot account for it.
- The gold result's sub-periods since 2021 are short. "Weaker" is a description; the searched break test did not date a break.
- The yield test is weak on a change specific to Japan. Japan's average correlation with the other three fell from 0.65 to 0.52, but that interval is too wide to read.

## Tests that came out against a hypothesis are results

The oil test was the one most likely to find a lead if one existed: it uses every public week since the CFTC began publishing
these positions in real time. It found none. Of its 70 descriptive rows, 20 exceed their own threshold, including the Brent 13-week
blocks (r about −0.40 at 62 blocks). With that many rows some do so by chance, and the 13-week horizon is where a searched oil "lead"
has failed before. They carry no verdict.

## The fifth build: the JODI world oil ledger

Built on 18 October as a dry run on JODI's 22 September file. It finds that the countries reporting to JODI covered 97% of world
crude production in January 2015 (81% leaving out countries JODI flags for checking) and 59% in 2025, because many stopped reporting. China, Russia and most Gulf states report no
stocks at all. So it publishes only sums over fixed panels of countries, never world totals. Its one test compares a fixed panel's stock
changes (Saudi Arabia carries a little over half of their variation) with the line EIA uses to balance world stocks. The test is blind until JODI's 21 October update; see
the calendar row of that date. [`data/jodi_oil/`](data/jodi_oil/README.md)

## How these were built, and what went wrong on the way

- **Specs, committed before the data:** [`gold`](_research/2026-10-18-Gold-Real-Yield-Break-Spec.md),
  [`JODI`](_research/2026-10-18-JODI-World-Oil-Ledger-Spec.md), [`FX`](_research/2026-10-18-FX-Rate-Gap-Weekly-Spec.md),
  [`yields`](_research/2026-10-18-Yield-Comovement-Four-Country-Spec.md), [`oil positioning`](_research/2026-10-18-COT-Full-Sample-Horizons-Spec.md).
  The outside attack is in [`_research/2026-10-18-Grok-G7-Spec-Attacks.md`](_research/2026-10-18-Grok-G7-Spec-Attacks.md).
- **The second reviews changed the designs materially.** The gold break test rejected about two in five pure-noise samples as
  first written, so it became descriptive. The yield test's interval failed under persistent volatility, so it now takes its width from
  pre-2018 history. The FX review found the rule as first written could hardly return anything but "inconclusive"; its gate and labels were
  rewritten to describe the gap term, not "rates". 168 early oil weeks were never public in real time, so they left the primary sample.
- **One bug was fixed after the registered run.** The oil roll calendar missed the 20 March 2024 contract expiry, so one window was
  priced on the wrong contract. Correcting it moved the WTI correlation from −0.01066 to −0.01076; the verdict did not change.
- **Process lapses, disclosed.** The oil builder saw both correlations once in an unfinished development run before the registered
  run (no definition changed afterwards; the registered values are identical to three decimals), and it listed the folder of cached ICE files twice
  without opening a file. The yields builder started the full download into a scratch folder by mistake (34 of 46 requests, all
  answered normally), then moved that folder and finished the remaining 12; no URL was requested twice.
- **Licences.** Raw files from sources whose terms reserve rights or are unclear (JODI, the World Bank's gold price, the Bank of
  England's curves, ICE) stay in local caches outside the repository. Only derived statistics are published, with each source cited.
