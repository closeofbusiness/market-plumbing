# Spec: on the last business day before a quarter-end, does a tri-party loan that must run past the date stand further above overnight than at an ordinary month-end? (supervisor, 2 Nov 2026; g16)

*Page context: `docs/index.html` §09 "Quarter-end funding stress" and §10 "December quarter-end" (prints only, due 4 Jan). Every print the page uses is overnight or a stock. Chosen in
[`_research/2026-11-01-Grok-G16-Term-Repo-Scoping.md`](2026-11-01-Grok-G16-Term-Repo-Scoping.md); rulings R0-1 to R0-6 there bind this spec. Attacked in
[`_research/2026-11-02-Grok-G16-Term-Repo-Attack.md`](2026-11-02-Grok-G16-Term-Repo-Attack.md) and by a second review (its findings are in the rulings below). Script `bin/term_repo_turns.py`, outputs
`data/term_repo_turns/`, vintages `data/vintages/ofr_repo/`, check.sh guard **M30**. This body applies round 1. Where the body and a ruling differ, the ruling wins.*

*"Supervisor fact" means read by the supervisor on 1 or 2 Nov 2026 from the source named.* ***Blind:*** *no value of any 2-7 day or overnight ex-Fed series has been read. The only values seen from this source are three
retired-bucket rates from 8-12 Aug 2025 (a recorded slip, in the scoping file), which enter nothing. Series coverage below came from a call that printed dates and null counts and discarded the values.*

## 0. Goal, and what the result can and cannot say

**The idea.** Take the last business day before a month-end T. A tri-party loan starting that day in the 2-7 day bucket has a tenor of more than one business day, so it cannot end, and its first exit option cannot fall, before the business day after T. Every one of them is open on T. An
overnight loan starting the same day ends on T. So on that one start date the two buckets differ in exactly the respect at issue. No other start date has this property: on earlier days the 2-7 day bucket mixes loans ending before T with loans ending after it, and the file does not split them.

- **Measure** E(T): the 2-7 day rate minus the overnight/open rate on T−1, minus the median of that spread on ordinary days of the same month. Tri-party, excluding Federal Reserve trades, preliminary vintage.
- **Register** one statement, for T = 31 Dec 2026 (T−1 = Wed 30 Dec): is E above, inside or below the range of E across eight ordinary month-ends?
- **Describe** (not registered): E at the five quarter-ends already passed (Sep 2025 to Sep 2026); each leg separately; the overnight/open print on T itself; the variants in 4.3.

**It can say** whether, on 30 Dec 2026, this one spread stood further above its ordinary December level than it did at the eight comparison month-ends.

**It cannot say:**
- **why, or whether lenders charged for the date.** A wider spread can come from the overnight leg falling as well as the term leg rising (the legs are always printed), from a shift in collateral (both series pool all classes), or from which dealers borrowed. The series has no counterparty detail. It is not called a charge or a premium anywhere;
- **anything comparing with SOFR or the other reference rates.** OFR says these means do "not allow for direct comparisons with those rates";
- **anything about the overnight leg being a pure overnight rate.** It includes open repo, which can be closed before T;
- **anything about the turn on T itself as a term spread.** The loan that spans this year-end most directly, Thu 31 Dec to Mon 4 Jan, is one business day and sits in the overnight/open bucket. That is why OO(T) is reported separately, and why the 4 Jan prints stay;
- **anything before 13 Aug 2025** (R0-1), about other repo (cleared, bilateral), or about year-ends in general (n = 1, and none of the eight comparison months is a year-end);
- **"no stress".** INSIDE means inside a range of eight, in one spread, on one day. A lender who declines to lend across the date leaves no print.

## 1. Hard requirements

1. Free public data only; no key, no contact in the User-Agent, GET only, at least 3 seconds apart; a refusal, bot check or 403 stops the fetch with STOP and is not routed around.
2. `selftest` runs on synthetic data, no network, and every guard applies its own mutant (`M(name)`/`mutant()`, as `bin/collateral_reuse.py`); an uncaught mutant fails the selftest.
3. **The gate is 2027-01-05T20:00Z.** Before it, `fetch` sends `end_date=2026-12-23` and refuses to write a response holding any later date, so no file before the gate can hold a target-window print. Time is UTC; `fetch` compares the machine clock with the response's HTTP `Date` and refuses at more than one hour's difference.
4. `register` refuses before the gate; refuses a vintage whose `MANIFEST.csv` has any `fetched_at` before the gate; refuses unless the script's embedded block hashes to `SPEC_PREREG_SHA256`; creates `registered.csv` with `O_EXCL` and also refuses if `git log --all -- data/term_repo_turns/registered.csv` shows any earlier version.
5. The prereg block is embedded in the script verbatim as one string; the constants are parsed from it, never restated.
6. Spreads are never written as causes in any README or page sentence.

## 2. Data

### 2.1 Series (supervisor facts, 2 Nov 2026; `https://data.financialresearch.gov/v1/series/timeseries?mnemonic=M&start_date=2025-08-01[&end_date=...]`, public, no token; response is a JSON list of `[date, value]`, value may be null)

| use | mnemonic | dates returned | nulls |
|---|---|---|---:|
| term rate | `REPO-TRIV1_AR_B27-P` | 302, 2025-08-13 to 2026-10-28 | 0 |
| overnight rate | `REPO-TRIV1_AR_OO-P` | 310, 2025-08-01 to 2026-10-28 | 0 |
| term volume | `REPO-TRIV1_TV_B27-P` | 302, same span | 0 |
| overnight volume | `REPO-TRIV1_TV_OO-P` | 310, same span | 0 |
| 8-30 day rate (described) | `REPO-TRIV1_AR_B830-P` | 302 | 21 |
| finals, revision read | the first four with `-F` | to 2026-06-30 | 0 |

Rates are volume-weighted means in percent, metadata precision 2, so S is expected on a 1 bp grid (`pre` reports the actual decimals). Volume unit is "USD", magnitude 0. **Volumes include affiliate repo and rates do not** (methodology: "volume series still include affiliate repo"), so a volume is context, not the sample behind the rate, and is never used as a weight. A null means no trading or a disclosure edit (metadata); it is never zero and never evidence about activity. Preliminary prints lag two business days. The `rights` field is empty; the note says the rates are "not intended to be referenced in contracts".

### 2.2 Definitions from the OFR tri-party methodology (`2025-08-Methodology-TPR.pdf`, read 2 Nov)

Overnight/open: "a minimum contractual maturity of one business day". 2-7 days: "a minimum contractual maturity of 7 or fewer calendar days but more than one business day". Weekends and US holidays are excluded when deciding whether a repo is overnight. Open and cancellable trades are tenored to the first option date. Rate and volume are of trades starting that day. Collateral pooled.

### 2.3 Fixed dates (supervisor facts)

**T:** 2025: 08-29, 09-30, 10-31, 11-28, 12-31; 2026: 01-30, 02-27, 03-31, 04-30, 05-29, 06-30, 07-31, 08-31, 09-30, 10-30, 11-30, 12-31. **T−1** is the previous date in the overnight series, and must equal the fence's list where it names one.

**Three month-ends are out of the registered comparison and described only:** 2025-08-29 (the month the bucket began; glossary and metadata disagree by two days on when), 2026-04-30 (T−1 = 29 Apr, and the decision takes effect 30 Apr, inside the loan; in the other four meeting months, T−1 is itself the effective date, so both legs start at the new rate), 2026-11-30 (T−1 = Fri 27 Nov, a 2 p.m. early close). That leaves eight.

**FOMC effective dates (day after the second meeting day; federalreserve.gov/monetarypolicy/fomccalendars.htm; the 11 Dec 2025 implementation note confirms the rule):** in the fence. Reconfirmed in `dry`; a difference warns.

**US early closes** (SIFMA holiday schedule, read 2 Nov, 2026 table; the two 2025 dates in the fence are from memory of the pattern, UNCERTAIN, and the 2025 table would settle it; neither affects a registered month): in the fence. Good Friday 3 Apr 2026 is listed as a 12:00 close; the second review found one weekday absent from both series against a federal-holiday calendar, and `pre` prints which.

### 2.4 Traps, and the rule that meets each

| trap | rule |
|---|---|
| Fed decision inside a control-day loan | K excludes any t with an effective date in (t, t+7] |
| Coupon settlement and the 15 Dec corporate tax date | K excludes the 15th, or the first business day after it when the 15th is not one. Flag column; V3 restores them |
| Early close | K excludes it. V3 restores |
| Christmas week in the December baseline | Kept, and a median of eleven tolerates it; V4 shows K limited to the 14th and earlier. Grok's proposal to drop bill days and 15-24 Dec is overruled: it leaves at most three days and would void the test by construction (R1-5) |
| Bill settlement | A column only: Tuesday and Thursday are 40% of days |
| One day, one print | Printed with volume, with both legs, and with `tick_sensitive` (does the label change if the control median moves one published tick either way?) |
| Preliminary prints revise | The January fetch governs target and placebo alike; `revisions.csv` shows November against January E and finals against preliminary; never re-scored |
| The Aug 2025 join | Earlier bucket not fetched |

### 2.5 What was known before the build

The page's overnight facts for June and September (other series) and the literature in the scoping file, which says the adjustment is mainly in overnight quantities. Nothing from 2.1 except dates and null counts. Reviewers worked from metadata and methodology only; Grok's fetch list holds no timeseries call (checked).

## 3. Method

Business days are dates present and non-null in both B27 and OO (a date in one only, or null, drops the day). `S(t) = 100 × (B27(t) − OO(t))`, in bp, from the file's strings as `fractions.Fraction`; comparisons exact; rounding only in print; an even-count median is the mean of the middle two.

**Control days K(T):** business days in T's calendar month with (T − t) ≥ 7 calendar days, no FOMC effective date in (t, t+7 calendar days], not coupon-flagged, not an early close.

**E(T) = S(T−1) − median(S over K(T)).** Needs T−1 defined and |K| ≥ 5, else NOT_ASSESSED. Dates after the data's last date leave E PENDING, never computed on what is there.

**Legs (always printed):** `dB = 100 × (B27(T−1) − median B27 over K)`, `dO = 100 × (OO(T−1) − median OO over K)`. Because a median of differences is not a difference of medians, dB − dO need not equal E; the README says so. **OT:** `100 × (OO(T) − median OO over K)`.

## 4. Questions, fixed in advance

### 4.1 Why these eight

Four months with no Fed decision near T (Nov 2025, Feb, May and Aug 2026) and four where T−1 is the decision's effective date, so both legs start at the new rate (Oct 2025, Jan, Jul and Oct 2026). All have an ordinary, full-session T−1. Under exchangeability December above all eight has probability 1/9; the months are not independent, so this is a guide. It goes in the README, not on the page.

### 4.2 Registered statement (`SPEC_PREREG_SHA256` is the sha256 of the interior of this fence, UTF-8, LF, final LF)

```
DEF|S(t)=100*(REPO-TRIV1_AR_B27-P(t)-REPO-TRIV1_AR_OO-P(t))|unit=basis_points|arithmetic=exact_fractions_from_file_strings|even_median=mean_of_middle_two|business_day=date_present_and_non-null_in_both_series
CONTROL|K(T)=business_days_in_month_of_T_with_(T-t)>=7_calendar_days,no_FOMC_effective_date_in_(t,t+7_calendar_days],not_coupon,not_early_close|coupon=the_15th_or_else_the_next_date_after_it_that_is_a_business_day_as_defined_in_DEF
STAT|E(T)=S(T-1)-median(S_over_K(T))|needs_T-1_defined_and_at_least_5_K_days_else_NOT_ASSESSED
PLACEBO|T-1=2025-10-30,2025-11-26,2026-01-29,2026-02-26,2026-05-28,2026-07-30,2026-08-28,2026-10-29|T=2025-10-31,2025-11-28,2026-01-30,2026-02-27,2026-05-29,2026-07-31,2026-08-31,2026-10-30|needs_at_least_7_assessed_else_VOID
FOMC|effective=2025-09-18,2025-10-30,2025-12-11,2026-01-29,2026-03-19,2026-04-30,2026-06-18,2026-07-30,2026-09-17,2026-10-29,2026-12-10
EARLY|close=2025-11-28,2025-12-24,2026-04-03,2026-05-22,2026-07-02,2026-11-27,2026-12-24
TARGET|T=2026-12-31|T-1=2026-12-30|missing_or_null_T-1_is_PENDING_no_write_retry_next_business_day_until_2027-01-29_then_NOT_ASSESSED
LABEL|ABOVE_if_E>max(placebo)_and_E>0;BELOW_if_E<min(placebo)_and_E<0;INSIDE_otherwise;NOT_ASSESSED_or_VOID_as_above
VINTAGE|preliminary|first_fetch_on_or_after_2027-01-05T20:00Z_supplies_target_and_placebo|finals_recorded_later_never_rescored
USE|label_E_range_and_both_legs_go_on_the_page_in_the_fixed_sentence|never_called_a_charge_or_premium|no_comparison_with_reference_rates|n=1
```

### 4.3 Described, computed for every complete T (never registered)

V1 mean of S on all days with t < T and T−t < 7 calendar days, minus the control median (labelled as a mix of loans that do and do not span T); V2 S(T) minus the control median (both legs carry the spanning loan on this date; labelled so); V3 K with coupon and early-close days restored; V4 K limited to the 14th and earlier; V5 no FOMC exclusion in K; V6 the 8-30 day spread on the E rule, where defined; V7 the placebo range with the three excluded months added. Volumes on T−1 and mean over K, term and overnight, labelled as including affiliates. `tick_sensitive`.

**The passed quarter-ends:** five E beside the eight-month range, as a count above the maximum and nothing more; no test, by R0-3. Today 14 of the 17 T are complete on data ending 28 Oct; Oct 2026 needs the 29 Oct print, published about 2 Nov; `describe` shows the rest PENDING. Nov 2026 enters only V7.

## 5. Outputs (`data/term_repo_turns/`)

- `daily.csv`: date, b27, oo, tv_b27, tv_oo, b830, s_bp, coupon, bill, early, fomc_in_7d.
- `turns.csv`: t, t_minus_1, kind (quarter, placebo, described, target), status (OK, PENDING, NOT_ASSESSED), n_k, s_t1, control_median, e, db, do, ot, v1..v7 fields, tv_b27_t1, tv_b27_k_mean, tv_oo_t1, tv_oo_k_mean, tick_sensitive. The target row has status PENDING and empty values before the gate.
- `registered.csv` (January; one row): prereg_sha256, vintage, fetched_at, t, t_minus_1, s_t1, control_median, e, db, do, ot, placebo_min, placebo_max, n_placebo, label, tick_sensitive.
- `checks.csv`: id, status (PASS, WARN, FAIL, INFO), detail. `revisions.csv`: t, field, vintage_a, vintage_b, a, b.
- `README.md`: leads with what the numbers show, then limits, then how to rerun.
- `data/vintages/ofr_repo/<YYYYMMDD>/` raw JSON and `MANIFEST.csv` (url, sha256, bytes, fetched_at), committed (US government data; about 10 small files). Commit only the vintages actually used: the November describe, the first post-gate. A second fetch on one day refuses unless `--replace`.

Subcommands: `fetch`; `build --vintage V --stage pre|dry|describe|register`; `selftest`. **pre:** layout, coverage, decimals, one volume's order of magnitude, calendar-minus-data dates; prints no rate and no spread. **dry:** rule engine over the real dates with values hidden (|K| per T, T−1 match), FOMC page recheck, `register` shown to refuse. **describe:** writes everything but `registered.csv`. **register:** 1.4; exit 6 on PENDING with no write.

## 6. Selftests

Synthetic only. At least: T−1 across a weekend and a holiday; K edges (T−t = 7 and 6; FOMC date at t, at calendar t+7 (excluded) and at calendar t+8 (kept); coupon when the 15th is a weekend and when the next weekday is also absent (15 Feb 2026 is a Sunday, 16 Feb a holiday, so 17 Feb is excluded); early close); NOT_ASSESSED at |K| = 4; VOID at 6 placebos; PENDING for an incomplete T and for a null T−1 on target; each LABEL edge (E equal to max is INSIDE; E above max but negative is INSIDE; the same below); Fractions on an even median; prereg hash; clock gate with an injected clock; end_date cap with a response holding a later date; pre-gate vintage refused by `register`; O_EXCL; clock against `Date`; null and one-series dates; refusal stops the fetch; no address in the User-Agent; `pre` output holds no rate. A mutant for each.

## 7. Pinned checks and M30

Row counts at least those in 2.1; every complete T in OO; first B27 date 2025-08-13; fence T−1 list equals the computed list; finals and preliminary cover the same dates up to 2026-06-30; one E re-derived by a second code path.
**M30** (`term_repo_check`, beside M29 in `--all`). ✗: the script's prereg constant differs from check.sh's literal; a target value in `turns.csv` before the gate; `registered.csv` exists before the gate; its sha differs from check.sh's literal once present (the literal lands in the same commit as the file). Warn: `registered.csv` absent after 2027-01-29.

## 8. Success criteria

- `python3 bin/term_repo_turns.py selftest` exits 0 and every mutant is caught.
- `bash bin/check.sh --all` shows 0 ✗ with M30 present; a wrong literal shows ✗ when tried.
- An independent verifier re-derives E and both legs for at least two complete T from the raw JSON with its own code and matches to the printed precision.
- Today `register` refuses; on or after 5 Jan 2027 it writes one row with the prereg hash, and a second run exits 5.

## 9. Page

**Now:** §10 gains one plain sentence on the five passed turns as a count with both legs named, and the December statement as queued. §09's "Neither June nor September showed it" is about overnight prints and stays true of them either way; a term reading sits beside it and does not replace it.
**January, fixed sentence, filling numbers only:** "On 30 December 2026, the tri-party rate on loans of 2-7 days, all of which ran past the year-end, was [x] basis points [above/below] the overnight rate. On ordinary December days the same gap had a median of [m], so the day differed from ordinary by [E] (the term rate by [y], the overnight rate by [z]; these need not add up, and the overnight rate includes open repo that can be closed before the date). At eight ordinary month-ends the same difference ranged from [a] to [b]. Against that range, set before the data was read, December is [ABOVE / INSIDE / BELOW]. One day and one spread; it does not say why." If the label is INSIDE while E lies outside the range (E above the maximum but not positive, or the mirror), the sentence adds "outside the range, but with the wrong sign to count". CALENDAR: the 2027-01-04 row stays; a new 2027-01-05 row runs `fetch` and `register`.

## 10. OPEN questions

None need a ruling before the build. `pre` settles the decimals and the absent weekday.

## Supervisor rulings

### Round 1 (supervisor, 2 Nov 2026), after Grok's attack and the Sonnet second review

The first draft registered a mean over the three days before T. **The attack sank it and I accept that.** Grok's verdict on the draft was "does not survive". I checked its core claim against the methodology's tenor bullets and it holds: on 28 and 29 Dec the bucket mixes loans ending on or before T with loans ending after it.

- **R1-1. Register T−1 only (Grok 1, accepted).** This is a better test and not only a repair: it is the one start date on which every trade in the bucket is open on T and the overnight trade starting the same day is not. The three-day mean survives as described V1.
- **R1-2. The bridging overnight (Grok 2, accepted as description).** OO(T) is reported as OT, not registered; the 4 Jan prints keep the turn itself. V2 stays, labelled.
- **R1-3. Not a charge (Grok 3, accepted).** Nothing is called a charge or premium, the overnight leg's open repo is stated, and both legs are always printed. The split also follows the g13 lesson on naming a net measure. Grok's Treasury-only pair is not taken: the metadata's subsetting for these series is tenor alone, and no tenor-by-collateral mnemonic is known.
- **R1-4. Grok's second scenario** (a real charge with the term print null) now gives PENDING, then NOT_ASSESSED, not a false reading.
- **R1-5. December controls: Grok 4 partly overruled.** The 15th and early closes are out of K, for every month. Dropping every bill day and all of 15-24 Dec, as proposed, leaves at most 2, 11 and 14 Dec, so December would be NOT_ASSESSED by construction; that is a design that cannot return a result. K for December is 1, 2, 10, 11, 14, 16, 17, 18, 21, 22, 23 Dec (eleven). V4 shows the earlier-month baseline.
- **R1-6. Placebo (Grok 5 and Sonnet 5, accepted; my error).** My sentence in the draft's 4.1, that contaminated months make ABOVE harder, was wrong: cuts extend only the minimum. It is deleted. Moving to T−1 cleans four of the five FOMC months because T−1 is then the effective date. Grok's list of five is replaced by eight: April 2026 is out, plus Aug 2025 (the break) and Nov 2026 (early close on T−1). Once T−1 is the only crossing day, I do not need to throw away four good months, and a range of eight is better than five.
- **R1-7. Floor (Grok 6, accepted).** The 1.0 bp floor is one tick. Replaced by E > 0 for ABOVE and E < 0 for BELOW, and `tick_sensitive` reported.
- **R1-8. Volumes (Grok 7, accepted; quote checked in the PDF).** No volume weighting. Labelled as including affiliates.
- **R1-9. Grok 8, overruled in part.** It would strike the label and queue only the overnight print. A registered reading on the one clean start date is worth having and costs little; the risk it names, over-reading, is met by the fixed sentence in section 9, no probability on the page and no reference-rate comparison.
- **R1-10. Sonnet 1, 2, 3, 4, 6, 7, 8, 9, 10 and 11 accepted.** Pre-gate fetch cap and vintage check; PENDING; O_EXCL and git-history check; clock against `Date`; completeness (14 of 17 today); dates defined on presence in both series; M30 ✗ and warn split; Fractions; fence embedded verbatim; January fetch governs, with a revision diff; schemas and stage semantics written; wording of section 0.
- **R1-11. The attack cost 20 minutes and one tool error.** The wrapper recorded one malformed MCP call as errored, not denied, with no effect.

### Round 2 (supervisor, 2 Nov 2026), after Grok's second pass on the amended spec

Grok's first attempt at this pass hit the 30-minute limit with no answer; a resumed turn wrote up what it had read (no further fetch; the two URLs the wrapper lists as unfetched in that turn were fetched in the session's first turn). Its return is appended to the attack file. **It confirms the central claim** at Fri 28 Aug into Mon 31 Aug 2026 and Wed 26 Nov into Fri 28 Nov 2025, cancellable trades included, and agrees that T−1 being the effective date justifies keeping the four months. R1-5 stands.

- **R2-1. Calendar days in the fence (accepted).** The window now says so, with a selftest at t+7 and t+8.
- **R2-2. The page sentence (accepted in substance, my wording).** "Further above" could describe a rate still below overnight, and INSIDE covers a value outside the range with the wrong sign. The sentence now gives the gap, the ordinary gap, the difference, the legs and the range, and says when the sign case arises. R1-9's claim that the earlier sentence contained the over-read was wrong.
- **R2-3. The coupon date (accepted).** Defined on the data's business days; 17 Feb 2026 is the selftest case.
- **R2-4. Left open, recorded.** Trades on an effective date may have been agreed before the announcement the previous afternoon; only trade-level timestamps would settle it. This goes in the README's limits.
- **R2-5. Spec closed.** Next: commit, then the builder, working on synthetic data only.

## Rulings round 3 (supervisor, 3 Nov 2026, after the first build and the independent verification)

- **R3-1. The API refuses a future `end_date`** (HTTP 400, "Date must be between 1900-01-01 and" today, seen 2 Nov). The spec's cap was my error. Before the gate `fetch` now sends the earlier of today and 2026-12-23, with a selftest and a mutant. The fetch wrote a STOP on this; it was our own malformed request, not a refusal, so I cleared it in the clone.
- **R3-2. The verifier matched every number:** 286 cells of `turns.csv`, 60 volume cells, 1,555 of `daily.csv`, all 33 revision values, and December and October 2025 by hand; zero differences. I reran its script on the landed vintage. Its Date-header point and `--out` route need deliberate tampering; recorded, not changed.
- **R3-3. Four README fixes from the verifier.** A recommended early close was written as a past event. My sentence on Fed moves was wrong for most of the eight, and now says what it means. My explanation of the top of the range (rates adjusting at a different pace) was untested and rested on one month, so it is cut: the README now says that October 2025 alone sets the top (+8, next highest +1) and that one month sets the bar for ABOVE. "Both legs start at the new rate" becomes "no decision falls inside the loan".
- **R3-4. The range is not changed after seeing it.** It is registered; October 2025 stays in.
- **R3-5. The T−1 check stays a hard stop** (builder's question): a placebo T−1 that moves means the calendar or the data has changed, and a person should look, in January above all.
- **R3-6. The FOMC recheck reads a saved page** (`dry --fomc-page`), as the script makes no request to the Board: the parser was fixed against the real page, and the page and the fence agree on 11 effective dates.

