# Sources, rulings, guards and open items: full-sample COT horizons

Specification: `_research/2026-10-18-COT-Full-Sample-Horizons-Spec.md` (with its amendments, the OPEN-6 ruling and the "Builder decisions" section). Script: `bin/cot_horizons.py`. Status at build: built and not frozen. `primary.csv` carries no `frozen_on` date until the supervisor runs `freeze`, which needs the section 8.6 independent re-derivation recorded as PASS (check V01 in `checks.csv`, PENDING). An independent verifier has already reproduced both primaries (WTI n=731 r=-0.01076; Brent n=819 r=+0.0303); recording V01 is the supervisor's step.

## Sources and terms

| Source | Used for | Terms |
|---|---|---|
| CFTC Disaggregated Commitments of Traders, contract code 067651, futures only (`72hh-3qpy`) and combined (`kh3c-gbw2`), publicreporting.cftc.gov | Managed-money long and short, WTI | Public domain (CFTC web policy). One query per book, `$limit=5000`, ordered by report date. The API serves revised history and has no as-of vintage; `fetch_log.csv` holds the pull time and checksum, and the rows are committed under `raw/`. |
| CFTC release schedule and historical special announcements, cftc.gov | Release dates: the 2026 schedule (52 dates), the 9 Dec 2025 shutdown table, the 2023 ION re-issue notices, 13 Jan 2025, 30 Dec 2014, 4 Jul 2014, the 5 Dec 2018 closure | Public domain. Saved under `raw/`. |
| CFTC press release 7864-19 (29 Jan 2019) | The 2018-19 shutdown schedule | Public domain. Saved under `raw/`. It states that the last report before the lapse was published on 21 Dec 2018 and that the report dated 24 Dec 2018 would be published on 1 Feb 2019; later dates are "expected" only. |
| EIA NYMEX crude futures contracts 1 and 2 (`RCLC1d.xls`, `RCLC2d.xls`), eia.gov | WTI futures returns, 2006 to 5 Apr 2024 | EIA reuse policy: public domain. The licence of these historical NYMEX files is OPEN-3. Kept local (`data/vintages/cot_horizons/`); no raw print and no weekly futures return is committed. |
| EIA Cushing WTI spot (`RWTCd.xls`) and Europe Brent spot (`RBRTEd.xls`) | Spot returns | Public domain. Read from the files the sister scripts commit (`data/cftc_cot/raw/`, `data/ice_brent/raw/`); never fetched here. |
| gov.uk bank holidays (`bank-holidays.json`, England and Wales) | ICE release timing | Open Government Licence. Used for 2019-2028; earlier years are computed (Easter, fixed days, substitutes, proclaimed one-offs) and the computed set is cross-checked against the file for every year the file covers. |
| ICE Futures Europe Brent Commitments of Traders, as `data/ice_brent/brent_ledger.csv` | Brent managed-money net and its change | E-025: derived statistics only; ICE is cited in every file with a Brent figure; the ICE `COTHist` files stay in `~/ice_cot/`. This script makes no request to ICE and never opens a `COTHist*` file or touches `~/ice_cot/` or its STOP latch (guard G17). Release timing is from ICE's CoT notes (Friday 18:30 London; read by the spec author, not fetched here). |

## E-025 conditions, as they bind this build

- Raw ICE files stay in `~/ice_cot/`. Nothing here reads them.
- Only derived statistics are published, and every file with a Brent figure carries the ICE citation in its `# source:` line.
- The STOP latch is never deleted. To refresh Brent, run the sister script per its CALENDAR clause; if it prints STOP, do not retry or route around it.
- Brent non-reportable positions are a balancing figure in ICE's own notes; no non-reportable figure is used here.

## Rulings applied

| # | Earlier design | This build | Source |
|---|---|---|---|
| R1 | 144 regressions, no correction | Two primary correlations (WTI, Brent; futures-only; next-week post-release return), Holm across the two; everything else descriptive | supervisor; Grok 1 |
| R2 | levels of net % OI and of price | changes only: change in net contracts against percent return | Grok 2 |
| R3 | Newey-West lag = h; bootstrap percentiles | one-week returns on the left, or non-overlapping h-week blocks, judged against 1.96 over the square root of the block count; no Newey-West or bootstrap column anywhere | Grok 3 |
| R4 | 26 weeks tested | 26 weeks is plot data with its band and no verdict | Grok 4 |
| R5 | Tuesday-to-Tuesday "next week" | the return starts at the first price strictly after the release date; Tuesday-to-Tuesday is `post_measurement`, descriptive | Grok 5 |
| R6 | sample from 2010 | WTI primary from 2009-09-08 (OPEN-6 ruling: every change uses two positions that were public in real time); the pooled 2006-2024 sample and the 2006-2009 split are descriptive | Grok 6; supervisor |
| R7 | % of OI regressors | net contracts; futures-only is the primary book, combined is descriptive | Grok 7 |
| R8 | EIA spot | WTI: NYMEX futures (EIA RCLC1/RCLC2), roll-consistent, to 5 Apr 2024; Brent: EIA spot, a proxy | Grok 8; supervisor |
| R9 | "do not script ICE" | OVERRULED (E-025) for the committed derived ledger; this build makes no ICE request | supervisor |

The decision rule (AGAINST takes precedence; SUPPORTS needs Holm rejection and a Spearman of the same sign above its band; a WTI futures/spot sign disagreement downgrades a SUPPORTS only) is in the specification, section 5, and was written before any position data was run.

## Guards (all 24 run in `selftest`, each with the mutant that must trip it)

G1 regressor is the first difference, not a level. G2 every post-release window starts strictly after the release date. G3 consecutive windows share an end date and blocks do not overlap. G4 the bar is 1.96 over the square root of the block count, with blocks at most floor(T/h). G5 exact column allowlists, no banned estimator column. G6 the CFTC release rule reproduces all 52 dates of the saved 2026 schedule. G7 the stated overrides and the two shutdown blocks. G8 ICE timing (no print on the release day; a Good Friday release moves to Tuesday). G9 roll consistency (same contract at both ends, at most one expiry per window, positive prices). G10 roll calendar (2020-04-21 is an expiry; weekday, Saturday and Sunday cases; holiday-set prints ignored; the expiry test uses the dates actually used). G11 no futures window ends after the last print. G12 real-time start and backcast separation. G13 flagged Brent prints excluded and counted. G14 Holm order, alphas and stopping. G15 freeze and unfreeze. G16 placebo scale and pinned random stream. G17 E-025 isolation. G18 fetch hygiene. G19 seam with `wti_ledger.csv`. G20 reproduction of the legacy lead-lag files at commit 768a26f. G21 Brent net check. G22 one report per ISO week. G23 week pairing. G24 no futures leak.

## Post-registration correction (18 Oct 2026)

The independent verifier found that `fut_expiries` stopped at the March 2024 delivery month, so the 2024-03-20 expiry was missing and the window of the 2024-03-12 report (2024-03-18 to 2024-03-25) was priced RCLC2 to RCLC2 (-0.949%) instead of RCLC2 to RCLC1 (-0.256%). The calendar now runs to the May 2024 delivery month, using weekdays minus the holiday set past the last EIA print, and guard G09 fails if any window ends after the last expiry in the calendar (its mutant is the truncated span). Before: WTI r -0.01066, z -0.288, p 0.7731. After: r -0.010763, z -0.291, p 0.7711. Verdict unchanged (AGAINST). The pre-fix values are also kept in check X02.

## Open items

- **OPEN-1 (supervisor): WTI after March 2024.** EIA's futures series ends 5 Apr 2024. Default kept: futures primary to 2024-03-19; later weeks are a spot extension (132 pairs before exclusions, 120 after the 2025 shutdown weeks).
- **OPEN-2 (supervisor): Brent's price.** No free scriptable Brent futures series. Default kept: Brent stays in the Holm family on EIA spot, labelled a proxy.
- **OPEN-3: licence of EIA's historical NYMEX files.** Default kept: raw files and futures returns stay local.
- **OPEN-4: ICE holiday releases.** The English bank-holiday rule is assumed, with the later date when ambiguous; the 47 affected pairs are excluded in one descriptive row.
- **OPEN-5: shutdown release dates.** Both blocks stay excluded. New fact from press release 7864-19: the release of the report dated 2018-12-18 is verified (Friday 21 Dec 2018, the last report before the lapse), so the window of the report dated 2018-12-11 ends at a verified release and could be re-admitted through a CORRECTIONS entry. The report dated 2018-12-18 starts at a verified release but ends at the release of the 2018-12-24 report, which is "expected" for 1 Feb 2019 only; every later date is "expected" too. The 2013 block still has no source.
- **OPEN-6: resolved** by the supervisor's ruling (start at 2009-09-08); the 2009-09-01 pair is a descriptive backcast row.
- **OPEN-7 (supervisor, new): the expiry calendar.** The specification's trading-day calendar (EIA prints minus the holiday set) treats the 16 weekdays that are not holidays but on which EIA has no print (most are the day after Thanksgiving, Columbus Day or Veterans Day) as non-business days. That moves the expiry of three delivery months (December 2006, 2016 and 2017) by one trading day (check X01). The registered build follows the specification; X01 records the 6 futures windows whose returns would change and the largest change. A calendar of weekdays minus the holiday set would fix it.
- **OPEN-8: CME holiday notices.** `NYMEX_HOLIDAYS` is generated from the standard rule and evidenced by absence from both EIA files (163 entries) or by an EIA carried-forward print (11). No CME Group notice was read, so check F07 is a WARN.
