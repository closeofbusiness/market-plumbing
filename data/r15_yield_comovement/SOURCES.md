# Sources: four-country 10-year yield comovement (R15)

Spec: `_research/2026-10-18-Yield-Comovement-Four-Country-Spec.md` (section 12, the amendments, overrides the earlier sections). Builder: `bin/r15_yield_comovement.py`.

**Nothing in this folder is a yield level or a weekly change.** The raw files are downloaded into `~/r15_yield_cache/` (outside the repository; the script refuses a cache inside it) and are read from there. What is committed is derived: shares, correlations, standard deviations, intervals, counts, dates of weeks, and a few single-value verification checkpoints in `checks.csv` (at most five per series, quoted as checkpoints, not a series). This project's CC BY 4.0 licence covers only the computation, not the issuers' data.

Source: Deutsche Bundesbank.

## The series (different objects; only correlations are used)

| Short name | Issuer, exact series | What it is | Compounding / timing |
|---|---|---|---|
| `us_nom` | US Treasury daily par yield curve, column `10 Yr` | 10-year par yield, semiannual bond-equivalent | end of day New York |
| `us_real` | US Treasury daily par real yield curve, column `10 YR` | 10-year TIPS par real yield (descriptive set only) | end of day New York |
| `bund_nom` | Bundesbank BBSIS `D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A` | Svensson fitted zero-coupon (spot) yield, listed Federal securities, 10.0 years residual maturity | percent; the compounding convention is not stated in the file (spec OPEN-3). It does not matter for a correlation. Basis of the daily value (midday or close) is not settled (spec OPEN-1) |
| `gilt_nom` | Bank of England nominal curve, sheet `4. spot curve` (`4. nominal spot curve` before 2005), the column whose maturity header is 10 | 10-year continuously compounded spot yield, fitted | London close; the workbook's `info` sheet names Bloomberg Finance L.P., Tradeweb and Bank calculations as sources, and records past revisions |
| `jgb_nom` | Ministry of Finance Japan JGB interest rate, column `10Y` | 10-year semiannual constant-maturity yield | 3pm Tokyo close, about a trading day before the other three |
| `ea_aaa` | ECB `YC` `B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y` | euro-area AAA Svensson spot yield. Not the Bund (robustness set only) | percent per annum |

No unit conversion is applied: a convention change rescales a weekly change by about 1/(1+y), and a correlation does not depend on scale. No covariance or variance share is computed, and no breakeven series exists in this build.

## URLs (all GET, https, no redirect followed, neutral User-Agent with no address, at least 3 seconds apart)

- Treasury: `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{Y}/all?type=daily_treasury_yield_curve&field_tdr_date_value={Y}&page&_format=csv` for Y = 1997 to the current year; the same with `type=daily_treasury_real_yield_curve` for 2017 to the current year.
- Bundesbank: `https://api.statistiken.bundesbank.de/rest/data/BBSIS/D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A?format=csv`
- MoF Japan: `https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv` and `.../interest_rate/jgbcme.csv`
- Bank of England: `https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/glcnominalddata.zip` (the archive, 39 MB, fetched only with `fetch --archive`) and `.../latest-yield-curve-data.zip` (the current month)
- ECB: `https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y?format=csvdata&detail=dataonly&startPeriod=2017-12-01`

A full fetch is 46 requests. Every request is one row of `fetch_log.csv` (UTC time, host, path, status, bytes, sha256 of the body, Last-Modified). Any status other than 200, a redirect, or a body that fails its content test writes `~/r15_yield_cache/STOP` and ends the run; only a person deletes it.

## Licence lines (each checked on 18 Oct 2026, one request each)

| Issuer | Terms seen | Handling |
|---|---|---|
| US Treasury | US Government work, 17 USC 105 | Redistributable; cached outside the repository anyway, so one rule covers all |
| Deutsche Bundesbank | Website conditions (`https://www.bundesbank.de/en/homepage/user-information/conditions-for-the-general-use-of-the-website-764706`): "free to save, forward or reproduce ... for your personal or professional use"; the content must "not be altered"; cite "Source: Deutsche Bundesbank" | Not clearly redistributable under CC BY 4.0, which permits alteration. Cache only; commit derived statistics; cite. Whether publishing derived statistics is compatible with "must not be altered" is the principal's ruling (spec OPEN-5) |
| Bank of England | `https://www.bankofengland.co.uk/legal`: resources are for personal or internal non-commercial use; reuse of third-party material needs that party's approval; the workbook names Bloomberg and Tradeweb | Cache only; commit derived statistics (supervisor ruling) |
| MoF Japan | `https://www.mof.go.jp/about_mof/notice/index.html`: PDL1.0 applies unless marked otherwise. That PDL1.0 allows commercial reuse is relayed by Grok, not re-read | Redistributable; cached outside the repository anyway |
| ECB | Not re-read; relayed: the data must be accurate and the ECB must be cited | Cache only; robustness use only |

## Dates, vintages, seams

The as-of date is the UTC date of the newest successful row in `fetch_log.csv`, never the clock. A week counts only if its Friday is on or before it. Each refetch keeps the previous file as `<name>.<sha8>.prev` in the cache, and `build` writes the revisions against it to `checks.csv` (K20). The Bank of England revises. The two seams (BoE archive to latest month, MoF `_all` to current) share no dates, are recorded as `no_overlap` with a continuity check, and are never reported as agreement.
