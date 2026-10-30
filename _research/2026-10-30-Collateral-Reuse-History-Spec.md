# Spec: the fair-value share of collateral re-used at JPMorgan Chase and Goldman Sachs, quarterly from end-2009 to mid-2026, from SEC XBRL on data.sec.gov (spec author, 30 Oct 2026; amended to apply the supervisor's round 1, R1-1 to R1-12)

*Page context: `docs/index.html` §00 verdict, §04 table and §11, and `dossiers/collateral-reuse.md` line 13: "No measure shows collateral re-use rising
before the price rise ... earlier shares are not measured" (correction C-152 in `CORRECTIONS.md`). Chosen in
[`_research/2026-10-30-Grok-G14-Scoping.md`](2026-10-30-Grok-G14-Scoping.md) (candidate 1, ruled "take forward as g14"). Attacked in
[`_research/2026-10-30-Grok-G14-Collateral-Reuse-Attack.md`](2026-10-30-Grok-G14-Collateral-Reuse-Attack.md). Lands as
`_research/2026-10-30-Collateral-Reuse-History-Spec.md`. House style follows `_research/2026-10-28-Revenue-Recognition-Timing-Spec.md`.
Script `bin/collateral_reuse.py`, outputs `data/collateral_reuse/`, vintages `data/vintages/collateral_reuse/`, check.sh guard **M28**.
Repository read at `efbcba8`. The rulings at the end are the record; this body applies round 1 (R1-1 to R1-12). Where the body and a ruling differ,
the ruling wins.*

*"Observed" means seen by the spec author on 30 Oct 2026 in the repository. **This spec was written with no network access: the author made no request
to any host, so no fact about SEC data below is "observed" at source.** "Supervisor count" and "supervisor fact" mean metadata the supervisor read on
data.sec.gov or in filings on 30 Oct 2026, no value read: period-end counts (the g14 brief and the scoping file); that for JPM and GS, both tags, every
quarter-end from 2010-06-30 appears in its own original 10-Q or 10-K under the test of P8, 2009-12-31 exists only as a comparative in later filings,
2010-03-31 is absent, there are no off-calendar period-ends, and State Street has all 52 quarter-ends 2013-12-31 to 2026-09-30; and the caption wording
of 2.6. "Relayed" means taken from a ruling, a project file or general knowledge and not re-read at source. **Blind:** the author computed no share and
no sum or ratio of any value of the two tags for any date, and read no XBRL value of them. The author did read the filing-note values that already sit
in the repository; 2.5 lists every one of them as KNOWN, including some the brief did not list.*

## 0. Goal, and what the result can and cannot say

- **Measure** the aggregate **fair-value share** S_q = Σ fair value of collateral resold or repledged / Σ fair value of collateral that could be resold
  or repledged, over JPMorgan Chase and Goldman Sachs, at every calendar quarter-end q from 31 Dec 2009 to 30 Jun 2026, each value as first reported in
  the original 10-Q or 10-K of that period, from the two standard us-gaap tags
  `FairValueOfSecuritiesReceivedAsCollateralThatHaveBeenResoldOrRepledged` (N, the numerator) and
  `FairValueOfSecuritiesReceivedAsCollateralThatCanBeResoldOrRepledged` (D, the denominator). Per-bank shares are reported beside it. Both legs are fair
  values, so a price move in the collateral can move the ratio with no new re-use; the README and every allowed sentence say "fair-value share" for that reason.
- **Register** (4.6) three statements, each with a **sign** (RISE, FALL or ZERO) and a **range label** that are separate: **S3**, mandatory, the change in S
  from 31 Dec 2021 to 31 Dec 2023, the statement for "before the price rise"; **S1**, the change from 31 Dec 2023 to 31 Dec 2025, the price-rise window
  itself, ending before the first-half-2026 step already on the page; **S2**, the 31 Dec 2023 level against the range of levels at the 2017-2019
  quarter-ends. The range label compares a change with a yardstick of earlier eight-quarter changes (4.6); it says whether the change was **unusual
  against the yardstick**, and never whether the share rose.
- **Describe**: the whole quarterly path; per-bank shares; the within-bank and weight-shift split of every registered change (also a VOID test); the
  variants of the yardstick; sensitivities (State Street added, equal weights, each bank alone, latest-filed values, flagged quarters removed, Wells Fargo
  if its counts qualify), each with its label and n shown.

**It can say** how the fair-value share of collateral that the two largest dealer banks may re-use and report having re-used changed between two dates,
with the sign stated, and whether that change was unusual against the range of its eight-quarter changes in 2011-2019. **The perimeter is two banks**
(C-067: name the panel before the ratio). The page's 81.7% (Dec 2025) and 83.2% (Jun 2026) are the six-bank share of JPMorgan, Goldman, Morgan
Stanley, Bank of America, BNY and Wells Fargo (5,061.8/6,192.0 and 6,149.6/7,389.7 $bn; `2026-08-30-D10-Reuse-On-The-Measured-Chain.md` §6 and C-152);
**the six-bank share before 2025 stays unmeasured**, and this two-bank history is a separate object that the page reports in a separate sentence (R1-11).

**It cannot say:**
- **anything about a speed or a chain length.** A fair-value share is utilisation of a stock at a date (C-135); the project's velocity range stays
  unsigned and is not touched;
- **anything about prices or flows of money.** No sentence says a share moved a price or a quantity of money;
- **anything about the six-bank share before 2026**, which these two banks may not represent (Morgan Stanley's share was the lowest and Bank of
  America's the highest of the four on the page in June 2026, relayed from `dossiers/collateral-reuse.md` line 17);
- **anything about intraday or off-quarter re-use**, which the quarter-end footnote does not show (D10 §4 limit 2);
- **anything about the Treasury-repo chain**: the lines cover every collateral class, derivatives and prime-brokerage included (D10 §6 item 3);
- **a "did not rise" from a WITHIN_RANGE label.** WITHIN_RANGE means the change was not unusual against 2011-2019. A share can rise by a few points and
  be WITHIN_RANGE; the sign says which.

**Required README sentence 2 (the denial sentence, exempt from G14, verbatim):** "A bank's re-pledged share is the part of the collateral it may re-use
that it reports having re-used: it is a share at a date, not a speed, and nothing here says it moved any price or any flow of money."

## 1. Hard requirements

- **R1. Free public data, one host.** `data.sec.gov` only (companyconcept). Refused before the request: every other host, explicitly `www.sec.gov`,
  `efts.sec.gov`, the Financial Statement and Notes ZIPs, `fred.stlouisfed.org` and `alfred.stlouisfed.org`. No key. (`fetch-instances` and the
  submissions fetch are cut: R1-8.)
- **R2. User-Agent.** The fetch mode reads `SEC_UA` from the environment (the declared contact that CLAUDE.md, by the principal's ruling of 12 Sep,
  gives sec.gov hosts), refuses to run without it (exit 2), and never writes its value to any file, log or output; G16 tests that it is absent from
  every written byte. Header `Accept-Encoding: identity`. **Only the supervisor runs the fetch mode and the registering build.** The builder writes
  the code and the selftest and may run on real data only `selftest` and `build --stage pre|dry` (R1-7). The spec author read neither the variable nor
  any contact string.
- **R3. Crawl.** GET only; no redirect followed; **no retry of any kind**; timeout 300 s; at least 1.0 s between requests (G16 treats 0.9 s as a
  violation). Cap per run: `fetch-concepts` 20 (8 are needed). **Resumable:** a body already in `raw/` whose sha256 matches its `vintages.csv` row is not
  re-requested.
- **R3a. STOP latch.** A 404 on a companyconcept URL means "no facts for this tag at this filer": logged `absent`, no STOP; it is expected for a Wells
  Fargo tag if absent and is a FAIL (C01) for a primary bank. Any 403 or 429, any other non-200 (3xx included), or a 200 body that is empty, HTML or not
  JSON writes `data/vintages/collateral_reuse/STOP_cru`, created exclusively (`open(..., "x")`) with five lines `status`, `utc_time`, `url_path`,
  `retry_after`, `body_head`; with the latch present no request is made and the run exits 2. **Only a person deletes a STOP file.** A timeout prints
  `FAIL network <path>`, exits 3, writes no STOP and retries nothing. (Grok's point 10, on a retry after `Retry-After` and no latch on one 403, is not
  adopted by the rulings; O-3.)
- **R4. Vintages and one location.** Raw bodies go to `data/vintages/collateral_reuse/<YYYYMMDD>/raw/` (gitignored; key = UTC date the vintage began).
  Committed per vintage: `concept_extract.csv` only. **Every request is one row of `data/collateral_reuse/vintages.csv`** (vintage, host, path, status,
  bytes, sha256, UTC time, elapsed seconds); the fetch mode is its only writer, it holds the log that `fetch_log.csv` held, and no other file does.
  **`registered.csv` is written by the first registering build only** and never re-scored (G17); a later vintage rewrites every other output; the only
  later change to `registered.csv` is the supersede rule of P19.
- **R5. Frozen inputs.** The bank list, tag names, CIKs and caption pins are in P1-P19 and 2.6 and are not changed after any value is read.
- **R6. Wording (G14).** No causal, price, speed or misconduct wording in README.md or SOURCES.md except the denial sentence. Say "fair-value share",
  "permitted to be re-used", "first reported", "quarter-end", "ordinary explanations"; never "velocity", "intensity", "multiplier", "drove", "fuelled",
  "supported the rally", "significant" or "material". **The plural "shares" before a verb of movement ("shares rose", "shares fell") is banned**; the singular
  "the share rose by 1.2 points" is allowed and is how the signed change is stated (the patterns are in 7).
- **R7. Code ownership.** `bin/collateral_reuse.py` is new, standard library only, and reads no project file other than its own two folders and
  `bin/check.sh` (read-only, for the selftest's cross-check against M28's literal copies). No existing script changes, apart from a new warn-only
  guard M28 in `bin/check.sh`.
- **R8. Parsing and numbers.** JSON read with `parse_float=Decimal, parse_int=Decimal`; `decimal` precision 28. Missing is never zero, never
  interpolated, never replaced by a nearby quarter (P15). Every threshold comparison uses the unrounded Decimal; half-even rounding at write time
  only: `_usd` whole dollars, `_pct` and `_pp` 3 decimals, `gap_to_extreme` 6 decimals (the unrounded gap to the nearest extreme of the yardstick, so a label that
  turned on a hair is visible).
- **R9. Post-registration fixes** go in SOURCES.md "Builder decisions" with the old value beside the new, and, for a registered row, by the supersede
  rule of P19. No registered number changes otherwise.
- **R10. One source.** Every number comes from data.sec.gov companyconcept; no other source enters any output cell. The KNOWN values of 2.5 enter
  `checks.csv` as tie-out pins only, never a statistic.

## 2. Data

### 2.1 Population (supervisor count unless marked)

On data.sec.gov companyconcept, 10-K and 10-Q period-ends with values, for each of the two tags:

| Bank | CIK | Count per tag | Span | Role in this build |
|---|---|---|---|---|
| JPMorgan Chase | 0000019617 | 66 (65 in own filing: 2010-06-30 to 2026-06-30; 2010-03-31 absent; 2009-12-31 comparative-only) | 2009-12-31 to 2026-06-30 | primary |
| Goldman Sachs | 0000886982 | 66 (same pattern) | 2009-12-31 to 2026-06-30 | primary |
| State Street | 0000093751 | 52, all in own filing | 2013-12-31 to 2026-09-30 | sensitivity |
| Wells Fargo | 0000072971 | **not counted by the supervisor**; D10 §6 item 4 says the frames API returned it on the denominator tag at CY2026Q2I (relayed) | | conditional (P3); two requests |
| BNY | 0001390777 | numerator 53 from 2010-12-31; denominator to 2017-06-30 only | | not fetched (g14b) |
| Citigroup | 0000831001 | denominator only, 17 year-ends to 2025-12-31 | | not fetched (g14b) |
| Morgan Stanley | 0000895421 | not on these tags (numerator: 3 period-ends in 2009-10) | | not fetched (g14b) |
| Bank of America | 0000070858 | not on these tags | | not fetched (g14b) |

**The two arithmetic questions of the first draft are settled by the supervisor's facts.** There are 67 calendar quarter-ends from 2009-12-31 to
2026-06-30 inclusive; 2010-03-31 is the absent one, so the 66 counted include 2009-12-31, which is a comparative in later filings and fails P8 (it was
filed more than 100 days after the period-end). The own-filing quarter-ends are therefore the **65** from 2010-06-30 to 2026-06-30. State Street's Q3
2026 10-Q is filed, which is why its count runs to 2026-09-30; the primary sample does not depend on it, and the State Street sensitivity uses only the
dates it shares with JPM and Goldman.

**Why two banks, and why the rule is fixed now.** These are the only banks the supervisor found with both standard tags at every quarter-end of the
span. A bank enters or leaves the primary sample only by P1, which was written before any value was read. A bank whose counts qualify for a
sensitivity (P2, P3) enters by its count, never by its value. Morgan Stanley, Bank of America, BNY and Citigroup are deferred to a later build, g14b,
which would need the filings' instance documents; nothing here fetches them.

### 2.2 The series, and which value counts (P6-P12, P16)

- **Source.** `https://data.sec.gov/api/xbrl/companyconcept/CIK<10 digits>/us-gaap/<tag>.json`, one request per bank and tag (8 in all). Each file lists
  facts under `units` with key `USD` (a bank whose file has any other unit key, or none, is refused: P7). Each fact carries `accn`, `end`, `val`, `fy`,
  `fp`, `form`, `filed` and sometimes `frame` (fields relayed from the g13 spec's reading of companyfacts, same schema; not re-observed).
- **Calendar quarter-end (P6).** `end` is exactly 31 Mar, 30 Jun, 30 Sep or 31 Dec. Anything else is counted in `banks.csv` (`n_off_calendar`; pinned at
  0 in C01) and never used.
- **First reported, the primary basis `own_filing` (P8).** For each bank and calendar quarter-end q the primary value is taken from the **original
  filing of that period**: form exactly `10-K` or `10-Q`, in which (i) `end` equals the end implied by the filing's own `fy` and `fp` (Q1 = 31 Mar, Q2 =
  30 Jun, Q3 = 30 Sep, FY or Q4 = 31 Dec of `fy`); (ii) the filing date is 0 to 100 days after `end`; (iii) `end` is the latest `end` among that
  accession's facts for the tag. A comparative column in a later filing fails (ii) or (iii), so a period-end repeated in later filings cannot replace
  the original print. The numerator and the denominator must both be facts of **the same accession**; if the original filing lacks either, the quarter
  is missing in the primary (status `own_filing_lacks_tags`), and `sens_latest` shows what a later filing says. Two accessions that both qualify make the
  quarter `ambiguous` and excluded. (Calendar-year filers only; the rule is not used for a fiscal-year filer without a new spec line.)
- **Amendments and restatements (P9, P12).** `10-K/A`, `10-Q/A`, `10-KT` never define the primary value. **Latest-filed sensitivity `sens_latest`:**
  the fact with the latest `filed` among all forms, ties to the largest `accn`, numerator and denominator from the same accession. `revisions.csv` lists, per
  bank, quarter and tag, the first and the latest value and their relative difference; a difference above 1% on either tag flags the quarter `recast`.
  **A `recast` flag at an endpoint of S1 or S3 voids that statement** (R1-4). The flag at 2016-12-31 will show whether JPMorgan restated its prior-year
  numerator when its caption changed (2.6); it is reported and acted on only by the rules above.
- **Conflicts (P10).** The same `accn`, tag and `end` with two different `val` makes the quarter `conflict`, excluded, and C14 FAIL. Identical repeats
  are one fact.
- **Units (P11).** `val` is full US dollars. A `val` outside 1e9 to 1e13 is `unit_odd` and excluded (JPM's permitted line is a few trillion and State
  Street's a few tens of billions, so a millions-for-dollars slip in either direction falls outside).
- **Ratio above one (P16).** A bank-quarter with N > D is excluded from every sample (status `ratio_gt_1`); if that is an endpoint of a statement the
  statement is VOID `endpoint_undefined`.
- **Dimensioned facts (P7).** companyconcept serves facts without dimensions (relayed, as for companyfacts and frames in the g13 spec). The build
  refuses any fact that carries a key outside the list in P7, and C03 ties the primary values to nine bank-date pairs of the filing notes (2.5) so a
  total that is really a segment would fail.
- **Flags (P12).** `jump`: either tag moves by more than 30% from the previous calendar quarter-end of the same bank (a prompt to look, not a verdict).
  `amended`: an amendment exists for the period. Flags exclude nothing from the primary; `sens_noflag` removes the flagged quarters (P13).

### 2.3 Traps, and the rule that meets each

| Trap | Rule | Guard |
|---|---|---|
| Period-ends repeated in later filings | P8 own filing; `sens_latest`; `revisions.csv`; `recast` at an endpoint voids | G3, G4 |
| Amendments, restatements | P9, P12 | G4 |
| Dimensioned facts beside consolidated totals | P7 key check; C03 ties to note totals | G5 |
| USD or millions | P11 bounds; unit key `USD` only | G6 |
| A quarter where the bank changed its line definition | XBRL tag names do not change when the note's caption does. The supervisor pinned the captions (2.6): JPM's numerator widened at 2017-03-31. Statements whose endpoints differ in caption class are VOID; yardstick windows spanning the change are excluded (R1-12) | G8, G21 |
| Off-calendar period-ends | P6 | G2 |
| Numerator and denominator from different filings | P8 same accession | G3 |
| Missing quarter filled | P15 | G7 |
| Weights moving between banks | Shapley split; a weight-dominated change is VOID | G13 |
| Numerator above denominator | P16 exclusion | G5 |
| Collateral passed between the two banks counted in both | cannot be netted on free data; per-bank shares and `sens_jpm`, `sens_gs` beside S; a stated limit, not an open question | |
| Fair-value remeasurement | N and D are both fair values at the date, so a price move partly cancels in the ratio; it need not cancel exactly (different collateral mixes), and the spec does not claim it does; hence the name "fair-value share" | |
| Seasonality and quarter-end positioning | every registered change compares the same calendar quarter at both ends, which removes a fixed seasonal; it does not remove a changing one | |

### 2.4 Other banks

**Wells Fargo (P3).** D10 §6 says Wells Fargo is on the standard denominator tag and is one of the six banks behind 83.2%. The supervisor's facts do not
count it. It enters the State Street sensitivity as `sens_wfc` only if the count probe (two requests) shows both tags at **every** calendar quarter-end
from 2013-12-31 to 2026-06-30 (51 dates); otherwise it appears in `probes.csv` and nowhere else. The rule uses counts and dates, never values.
**Morgan Stanley, Bank of America, BNY and Citigroup** are not fetched, probed or sampled in this build (P4); the four-bank year-end sample, the
instance-document fetch and everything that existed only for them are deferred to g14b.

### 2.5 KNOWN values (the blind list)

The brief names three dates (June 2025, December 2025, June 2026) as known. **The repository holds more**, and the blind rule is only honest if all
of it is listed. These are KNOWN to the spec author, the supervisor and any reviewer; they were used for **no** design choice (window, threshold,
label, bank set), and they are used in the build only as the tie-out pins of C03. Tolerance of a pin: **half the unit of its last printed digit** (0.05bn
for a pin printed to $0.1bn, 0.5mn for a pin printed to $0.001bn).

| Bank | Date | Repledged N | Permitted D | Where in the repository |
|---|---|---:|---:|---|
| JPM | 2017-12-31 | $775.3bn | $968.8bn | `data/series.tsv` (singh_panel_jpm), FY2017 10-K acc 0000019617-18-000057 |
| JPM | 2024-12-31 | $1,210.7bn | $1,544.0bn | `Shadow_Debt_Channel_Map.md` line 1200 |
| JPM | 2025-09-30 | $1,439.9bn | $1,829.9bn | `data/series.tsv` (jpm_collateral_permitted_sep2025_bn); CORRECTIONS C-071, C-072 |
| JPM | 2025-12-31 | $1,426.4bn | $1,771.0bn | `Shadow_Debt_Channel_Map.md` line 1200 |
| JPM | 2026-06-30 | $1,741.8bn | $2,181.4bn | D10 §2; `data/series.tsv` lines 116-117 |
| GS | 2017-12-31 | $599.6bn | $764.0bn | `data/series.tsv` (singh_panel_gs); `_research/2026-10-13-Grok-Wave-Reviews-Return.md` line 224 |
| GS | 2024-12-31 | $912.863bn | $1,038.740bn | `Shadow_Debt_Channel_Map.md` line 1201 |
| GS | 2025-12-31 | $1,119.825bn | $1,312.079bn | `Shadow_Debt_Channel_Map.md` line 1201 |
| GS | 2026-06-30 | $1,265.704bn | $1,431.870bn | `_research/D10R_Reuse_Review_Return_paste.md` line 15 (10-Q acc 0000886982-26-000297); D10 §2 |

Also KNOWN, as shares: JPM 78.2% (Jun 2025) and 79.8% (Jun 2026), GS 85.2% and 88.4% (`dossiers/collateral-reuse.md` line 17); JPM 80.0% at
31 Dec 2017 (Wave-Reviews Return line 224); the four-name share 80.4% at 31 Dec 2017 (`data/series.tsv`, singh_panel_utilization_2017_pct) and, from a
different note, 77.8% at FY2019 and 79.2% at FY2025 for "the four US dealers disclosing both legs"
(`2026-08-21-Singh-And-The-Two-Circuits.md` line 29); the four-bank 82.6% (Jun 2025) and 84.0% (Jun 2026) and the six-bank 81.7% (Dec 2025) and 83.2%
(Jun 2026). Components for the other banks are in the same files and are KNOWN; none enters a statistic.

**What this means for the test, stated plainly (the `blind` column of `registered.csv` and the README print it).** Not blind: the 2025-12-31 endpoint of S1
(the author formed, from the components above and without recording a figure, the impression that the JPM+GS aggregate was in the low 80s percent at
2024-12-31 and 2025-12-31), JPM's 2017 share, and S2's 2023-12-31 level only through that impression of neighbouring years. Blind: the 2023-12-31 and
2021-12-31 levels, every value from 2018 to 2023 and from 2009 to 2016 (except JPM's and Goldman's 2017 year-end), and the whole yardstick. So **S3 is
`blind` = full; S1 and S2 are `partial`.**

*Repository defect noted for the supervisor (not an open question of this spec):* `2026-08-21-Singh-And-The-Two-Circuits.md` line 29 gives 79.2% for
the four dealers at FY2025, while the FY2025 components in `Shadow_Debt_Channel_Map.md` lines 1200-1203 give nearer 82-83% (the author's arithmetic on
Bank of America's rounded values; not a registered figure) and C-152 gives 81.7% for six banks at Dec 2025.

### 2.6 Caption pins (R1-6, R1-12)

The supervisor read, on 30 Oct 2026, the company label for each line from the **company label linkbase of the filing** (wording only, no values). The
pinned class is what the build uses; "caption change" in the statements means a change of class between two dates. The wording below is a filer's label
(quoted at under 15 words each).

| Bank | Filing (10-K for) | Accession | Numerator wording (class) | Denominator wording (class) |
|---|---|---|---|---|
| JPM | 2011 | 0000019617-12-000163 | "Assets accepted by the Firm as collateral that the Firm has sold or repledged" (**JN1**) | "...that it could sell or repledge, deliver or otherwise use at fair value" (**JD1**) |
| JPM | 2013 | 0000019617-14-000289 | as 2011 (**JN1**) | as 2011 (**JD1**) |
| JPM | 2019 | 0000019617-20-000257 | "Collateral sold, repledged, delivered or otherwise used" (**JN2**) | "Collateral permitted to be sold or repledged, delivered, or otherwise used" (**JD1**) |
| JPM | 2021 | 0000019617-22-000272 | as 2019 (**JN2**) | as 2019 (**JD1**) |
| JPM | 2023 | 0000019617-24-000225 | as 2019 (**JN2**) | as 2019 (**JD1**) |
| JPM | 2025 | 0001628280-26-008131 | as 2019 (**JN2**) | as 2019 (**JD1**) |
| GS | 2011 | 0001193125-12-085822 | "...received as collateral which the firm delivered or repledged" (**GN1**) | "...that it was permitted to deliver or repledge" (**GD1**) |
| GS | 2013 | 0001193125-14-073792 | as 2011 (**GN1**) | as 2011 (**GD1**) |
| GS | 2019 | 0001193125-20-043853 | as 2011 with "at fair value" added (**GN1**) | as 2011 (**GD1**) |
| GS | 2021 | 0001193125-22-052682 | as 2019 (**GN1**) | as 2011 (**GD1**) |
| GS | 2023 | 0000886982-24-000006 | "Collateral that was delivered or repledged" (**GN1**) | "Collateral available to be delivered or repledged" (**GD1**) |
| GS | 2025 | 0000886982-26-000091 | as 2023 (**GN1**) | as 2023 (**GD1**) |

Also read, without a pinned accession: the JPM 10-Ks for 2014, 2015 and 2016 carry the **JN1** wording (the 2012 10-K was not read); the
JPM 10-Qs of 2017-03-31, 2017-06-30 and 2017-09-30 and the 10-Ks of 2017 and 2018 carry **JN2** (the 10-Q wording of the denominator in 2017 is
"Collateral that could be sold or repledged, delivered, or otherwise used", class **JD1**). **Findings:** JPMorgan's denominator was already wide and did not change in
scope; **only its numerator widened, at 2017-03-31** (first quarter in JN2), from sold-or-repledged to sold, repledged, delivered or otherwise used.
Goldman's wording is treated as unchanged in scope (GN1, GD1 throughout). The 10-Qs before 2017-03-31 were not read; the build treats every JPM quarter
before 2017-03-31 as JN1, an assumption stated here (O-4).

**Consequences, fixed.** (a) S3 (2021, 2023) and S1 (2023, 2025) endpoints carry the same class at both banks, so neither is VOID on captions; S2's
2023-12-31 and 2019-12-31 classes also match. (b) Any yardstick window whose start is on or before 2016-12-31 and whose end is on or after 2017-03-31
is excluded from the registered yardstick (R1-12): for JPM, the eight ends 2017-03-31 to 2018-12-31. (c) The README says: "JPMorgan's numerator caption
widened in the first quarter of 2017; windows that span that change are excluded from the yardstick." A selftest guard (G21) enforces the exclusion.
(d) After the build, the captions at the quarters that set the yardstick's maximum and minimum are read by the supervisor as a described check; it changes
no label.

`data/collateral_reuse/captions_pin.csv` carries these pins (header in 5); `SPEC_CAPTION_SHA256` in the script is the sha256 of that file, taken by the
supervisor when the table is committed, and C19 FAILs if the file differs from it or lacks a class for any pinned bank-date-line.

### 2.7 Licence and citation

US government works (17 U.S.C. 105; relayed, not re-verified here). Every CSV's `# source:` line and the README cite: US Securities and Exchange
Commission, EDGAR XBRL API (companyconcept) on data.sec.gov, vintage <YYYYMMDD>; and the caption pins "company label linkbase of the filing".

### 2.8 What the spec author looked at

The repository files named in the brief and the lines of `data/series.tsv`, `Shadow_Debt_Channel_Map.md`, `dossiers/collateral-reuse.md`,
`2026-08-21-Singh-And-The-Two-Circuits.md`, the D10R return and the Wave-Reviews Return cited in 2.5; `CALENDAR.tsv` rows 2026-11-05 and 2026-11-16;
`bin/check.sh` M27; the head of `bin/rev_recognition_timing.py`; Grok's attack file. **No request was made, no XBRL value of the two tags was read, and
no share, sum or ratio of any value was computed or written down.** Two synthetic simulations (random numbers, no data) were run for 4.0; the
unrecorded impression of 2.5 is disclosed there.

## 3. Method

0. **Spec first.** This spec, with the rulings and the filled caption table, is committed under `_research/` before the first fetch (criterion 11).
   SOURCES.md cites that commit.
1. **`fetch-concepts`** (supervisor): 8 requests, the two tags for JPM, GS, State Street and Wells Fargo. Appends one row per request to
   `vintages.csv`; bodies to `raw/`. → `concept_extract.csv` (after `build`).
2. **`build --stage pre`** (builder or supervisor): reads only `end`, `accn`, `form`, `filed`, `fy`, `fp` of each fact (never `val`) and writes
   `banks.csv`, `probes.csv`, the own-filing status of every bank-quarter (`n_usd`, `d_usd`, `share_pct` empty), and checks C01, C02, C11, C12, C19. **No value
   is read or written.**
3. **`build --stage dry`** (the builder may run this on real data; R1-7): computes everything, including the statements, the yardsticks, the tie-outs and
   the decomposition, but writes **only status counts and checks**, to a scratch folder given by `--out` (refused if it is the committed folder). Status
   counts: quarters per bank and status, `recast` and `jump` counts, `ratio_gt_1` count, yardstick member counts n_Y and n_YR. No value, no share, no
   sign, no label, no VOID reason and no `registered.csv`. Its purpose is to show that the code runs end to end on the real files; the builder reads
   nothing else.
4. **`build --stage full`** (the **supervisor** only: the registering build): everything. The full series and `registered.csv` are written only here.
5. **Per bank-quarter** (P6-P12, P16) → `quarters.csv` (`basis` own_filing and latest_filed on separate rows); **per sample and quarter** →
   `samples.csv`: S_q = Σ N / Σ D over the banks of the sample, only where every bank has an `ok` status.
6. **Changes** → `changes.csv`: D8_q = S_q − S_(q−8) in percentage points for every calendar quarter-end q with both dates defined (q−8 is eight calendar
   quarters earlier, found by quarter index, never by row position); `role` = `yardstick` for the members of Y (4.6), `registered` for the S1 and S3
   windows, `described` otherwise (including windows spanning the caption change, which are excluded from Y but still written). `kind` = `level` rows
   carry S_q for the 2017-03-31 to 2019-12-31 quarter-ends (`yardstick`) and 2023-12-31 (`registered`).
7. **Statements** → `registered.csv` (4.6), from the primary sample and the `own_filing` basis only. Order of tests: VOID reasons in the order of the
   hashed text, then sign, then range label. Ties with an extreme of the distribution are WITHIN (min ≤ stat ≤ max); a label uses the unrounded
   Decimal and `gap_to_extreme` records the margin.
8. **Decomposition** → `decomposition.csv`, for the S1 and S3 windows. With w_b = D_b / Σ D and s_b = N_b / D_b at the start (0) and end (1), the exact
   (Shapley) split of Σ w_b,1 s_b,1 − Σ w_b,0 s_b,0 is within_b = ((w_b,0 + w_b,1) / 2)(s_b,1 − s_b,0) and mix_b = ((w_b,1 − w_b,0) / 2)(s_b,0 + s_b,1);
   the two sum to the total exactly. **A registered change is VOID `mix_dominates` when the summed mix term has the same sign as the total and is larger
   in size than the summed within term.** Per-bank shares are reported beside it.
9. **Samples** (each gets the same changes and, as a statistic, the same three range labels computed against its own yardstick members, with n shown and
   VOID only when n < 10; never registered): `primary`; `sens_stt` (P2; its members are those of Y for which all three banks are defined at q and q−8,
   so it starts at 2015-12-31); `sens_wfc` (P3, if built); `sens_jpm`, `sens_gs` (each bank alone); `sens_eqw` (P14); `sens_noflag` (P13); and
   `basis` = latest_filed for the primary bank set.
10. **Described variants of the yardstick** (`headline.csv`; never registered): (a) the unrestricted 2011-start yardstick, which keeps the 8 windows
    spanning the caption change (31 defined under P8); (b) the non-overlapping spans: five disjoint spans fit the nominal 2009Q4-2019Q4 frame, and the
    spans defined and not spanning the caption change are at most four (three within 2010-06-30 to 2016-12-31 and one within 2017-03-31 to
    2019-12-31; three in the December phase, ending 2013, 2015 and 2019); the span ending 2011-12-31 is reported on the `latest_filed` basis only, flagged,
    because its start is a comparative; (c) a December-only subset of Y (6 defined: December ends 2012-2016 and 2019); (d) a Goldman-only yardstick on
    Goldman's own share (no caption change, so no exclusion; 31 windows defined from 2012-06-30). **If the unrestricted 2011-start variant gives a
    different range label from Y for a registered statement, the README says so.** (The registered robustness test is YR, 4.6.)
11. **Tie-outs** (C03) against the nine KNOWN bank-date pairs of 2.5, and the **ranks**: the position of each registered statistic among the yardstick
    members and itself (largest = 1), reported and never scored. The recast flag at 2016-12-31 is reported as a headline row.
12. **Stages.** The raw bodies hold every year on disk, unread, before `pre`; C11 tests what the code reads, not what is on disk. Reading `raw/`, the
    extract or any `quarters.csv` value before the registering build has run once is a breach of the blind rule (6.3).

## 4. Questions, fixed in advance

**4.0 Noise and resolution.** Two banks form a census, so there is no sampling error; what limits a reading is identification (line definitions, weights,
collateral passed between the two) and the thinness of the yardstick. **Fence-post:** the nominal 2009Q4-2019Q4 frame is 40 quarter-steps, which is
five disjoint eight-quarter spans; the registered yardstick uses windows ending 2011-12-31 to 2019-12-31, of which **23 are defined and not excluded**
(33 nominal; minus 2 lost to P8 at the 2009-12-31 and 2010-03-31 starts; minus 8 that span JPM's 2017 caption change; the supervisor's 23 is re-derived
and correct). The usable levels run 2010-06-30 to 2016-12-31 (26 steps, three disjoint spans) and 2017-03-31 to 2019-12-31 (11 steps, one span), so the
yardstick holds **at most four** independent draws. The robustness yardstick YR (ends 2013-12-31 to 2019-12-31) has 25 nominal and **17 defined and not
excluded** members (the supervisor's 17 is re-derived and correct).
**Chance wording (a simulation, not a property of the data):** under an i.i.d.-increment null (standard-normal quarterly increments, the 23 windows
placed as above, one new independent eight-quarter change; 200,000 replications, seed 14), a new change exceeds the yardstick's maximum about 11% of the
time (roughly one in nine) and falls outside it on either side about 22% of the time (roughly one in 4.5); for YR the figures are 14% and 28%. So a
RISE_OUTSIDE_RANGE label would still appear roughly one time in nine with no change in behaviour at all. The README states this with the words "a
simulation under an i.i.d.-increment null". The 1-point unit is the README's; the resolution of the data is the rounding of the filings (JPM to $0.1bn,
Goldman to $1mn), far below 0.01 point.

- **Q1** Counts per bank and tag; the expected-dates table (`banks.csv`, C01, C02). **Q2** The path of S and the per-bank shares. **Q3** S3, S1, S2:
  sign, label, rank and gap, the yardstick extremes, blind (`registered.csv`). **Q4** The within-bank and weight-shift split. **Q5** Whether any
  sensitivity or variant changes a label. **Q6** What the later filings say: `revisions.csv`, `recast`. **Q7** After the 5 Nov census, the same series with
  2026-09-30 (described).
- **Not asked:** anything about prices, flows of money, speed or chain length; any judgement on a named bank; any reading of the six-bank figures as a
  history.

**What the page may say, fixed before data** (R1-1, R1-11). The six-bank sentence in C-152 stays as it is: the six-bank share before 2025 remains
unmeasured. The result is reported as a **separate two-bank sentence naming the banks**, built from the sign and the label together, with the signed change
always stated:

> "From D1 to D2 the fair-value share of collateral re-used at JPMorgan Chase and Goldman Sachs {rose | fell | was unchanged to within 0.1 point}, by {+X | −X}
> points, {more than every | inside the range of | less than every} comparable two-year change in the 2011-2019 yardstick ({lowest} to {highest})."

| Statement | Sign | Label | Notes |
|---|---|---|---|
| S3 (D1 = Dec 2021, D2 = Dec 2023) | RISE / FALL / ZERO | RISE_OUTSIDE_RANGE / WITHIN_RANGE / FALL_OUTSIDE_RANGE | This is the sentence for "before the price rise". |
| S1 (Dec 2023 to Dec 2025) | as above | as above | Said to cover the window of the price rise itself, not "before". |
| S2 (level on 31 Dec 2023) | RISE / FALL / ZERO against the 2017-2019 median | LEVEL_ABOVE_RANGE / LEVEL_WITHIN_RANGE / LEVEL_BELOW_RANGE | "On 31 Dec 2023 the fair-value share was X%, above / inside / below its 2017-2019 range (Y% to Z%)." |
| any VOID | | | No sentence of the above kind; the page says only that the statement could not be made for these two banks, with the reason. |

A WITHIN_RANGE sentence **states the signed change** and **never says or implies that the share did not rise**; the range label is described as "unusual
against the yardstick". Every sentence is followed by "This is a share at a date for two banks, not a speed (C-135), and says nothing about prices or
money." A correction to C-152 goes only through `CORRECTIONS.md`, by the supervisor.

### 4.6 Registered statements (the script holds `SPEC_PREREG_SHA256` and refuses to write `registered.csv` if its constants do not reproduce this text byte for byte; one line per statement, LF endings, final LF included)

```
DEF|S_q=sum_b(N_b,q)/sum_b(D_b,q)|N=us-gaap:FairValueOfSecuritiesReceivedAsCollateralThatHaveBeenResoldOrRepledged|D=us-gaap:FairValueOfSecuritiesReceivedAsCollateralThatCanBeResoldOrRepledged|banks=JPM_CIK0000019617+GS_CIK0000886982|every_bank_must_have_both_values_at_q_with_N<=D|value=first_reported_in_the_original_10-K_or_10-Q_of_that_period|unit=USD|share_in_percent|D8_q=S_q-S_(q-8)_in_percentage_points|q-8_is_exactly_eight_calendar_quarters_before_q
M|w_b=D_b/sum_b(D_b)|s_b=N_b/D_b|total=within+mix|within=sum_b(((w_b,0+w_b,1)/2)*(s_b,1-s_b,0))|mix=sum_b(((w_b,1-w_b,0)/2)*(s_b,0+s_b,1))|exact_Shapley_split_of_(w1*s1-w0*s0)|mix_dominates=mix_and_within_nonzero_and_sign(mix)==sign(total)_and_abs(mix)>abs(within)|applies_to=S1,S3
Y|series=D8_q|sample=primary|basis=own_filing|end_quarters=2011-12-31..2019-12-31_inclusive|n_nominal=33|exclude=any_window_spanning_a_pinned_caption_change_at_a_primary_bank(start<=last_quarter_before_the_change_and_end>=first_quarter_of_the_change)|caption_change=JPM_numerator_first_quarter_2017-03-31(spanning_ends_2017-03-31..2018-12-31)|members=those_with_S_defined_at_q_and_q-8_and_not_excluded|expected_members=23|min_n=20|no_date_after_2019-12-31_enters|compare=unrounded_decimal_prec28
YR|robustness_yardstick=Y_restricted_to_end_quarters_2013-12-31..2019-12-31|n_nominal=25|expected_members=17|min_n=14|use=for_S1_and_S3_the_range_label_is_recomputed_against_YR|a_different_range_label_from_Y's=VOID_(yardstick_disagrees)|YR_thinner_than_min_n=VOID_(thin_yardstick)
YL|series=S_q|sample=primary|basis=own_filing|quarters=2017-03-31..2019-12-31_inclusive|n_nominal=12|members=those_with_S_defined|min_n=10|no_date_after_2019-12-31_enters|compare=unrounded_decimal_prec28
SIGN|change=RISE_if_stat>=0.1_point;FALL_if_stat<=-0.1_point;ZERO_if_abs(stat)<0.1_point|level=sign_of_(S_2023-12-31-median(YL))_by_the_same_0.1_point_rule|registered_beside_and_apart_from_the_range_label|the_range_label_means_unusual_against_the_yardstick_and_never_rose_or_not
S1|window=2023-12-31..2025-12-31|sample=primary|basis=own_filing|vintage=first_full_build|stat=D8_2025-12-31|blind=partial|order=VOID,sign,labels|VOID_order=endpoint_undefined,thin_yardstick,endpoint_recast,caption_change,mix_dominates,yardstick_disagrees|endpoint_undefined=S_undefined_at_an_endpoint_or_a_bank-quarter_there_excluded_(incl_ratio_gt_1)|thin_yardstick=n_Y<20_or_n_YR<14|endpoint_recast=any_bank_tag_flagged_recast_at_either_endpoint|caption_change=pinned_caption_class_differs_between_the_endpoints_for_either_line_of_either_bank|RISE_OUTSIDE_RANGE=stat>max(Y)|FALL_OUTSIDE_RANGE=stat<min(Y)|WITHIN_RANGE=min(Y)<=stat<=max(Y)|rank=position_of_stat_among_Y_and_stat_reported_not_scored|compare=unrounded_decimal_prec28
S2|window=level_at_2023-12-31|sample=primary|basis=own_filing|vintage=first_full_build|stat=S_2023-12-31|blind=partial|order=VOID,sign,labels|VOID_order=endpoint_undefined,thin_yardstick,caption_change|endpoint_undefined=as_S1_at_2023-12-31|thin_yardstick=n_YL<10|caption_change=pinned_class_at_2023-12-31_differs_from_2019-12-31|LEVEL_ABOVE_RANGE=stat>max(YL)|LEVEL_BELOW_RANGE=stat<min(YL)|LEVEL_WITHIN_RANGE=min(YL)<=stat<=max(YL)|rank=as_S1|compare=unrounded_decimal_prec28
S3|window=2021-12-31..2023-12-31|sample=primary|basis=own_filing|vintage=first_full_build|stat=D8_2023-12-31|blind=full|mandatory=yes|order=VOID,sign,labels|VOID_order=as_S1|labels=as_S1_against_the_same_Y|rank=as_S1|compare=unrounded_decimal_prec28
```

**sha256 of that text: `4ca76d72f2e6050e5e6f11aea432195b170405d2391783de3cca3b90641cd55b`** (3463 bytes, 9 lines). `registered.csv` carries it in `prereg_sha256`, and M28 holds its own literal copy.

**In words.** **Y** is the set of eight-quarter changes of S (percentage points) whose end quarter lies from 31 Dec 2011 to 31 Dec 2019, with S defined at both
dates and the window not spanning the 2017-03-31 caption change at JPMorgan: 23 expected, statement VOID if fewer than 20. **YR** is Y restricted to ends from
31 Dec 2013: 17 expected, VOID if fewer than 14. **YL** is the set of levels at the twelve quarter-ends from 31 Mar 2017 to 31 Dec 2019 (VOID if fewer than 10).
**Sign** of a change: RISE if it is at least +0.1 point, FALL if at most −0.1 point, else ZERO; registered apart from the label. **S3, S1:** the range label
is `RISE_OUTSIDE_RANGE` if the change exceeds the largest member of Y, `FALL_OUTSIDE_RANGE` if it is below the smallest, else `WITHIN_RANGE`. **S2:** the level
on 31 Dec 2023 is `LEVEL_ABOVE_RANGE`, `LEVEL_BELOW_RANGE` or `LEVEL_WITHIN_RANGE` against YL. **VOID**, tested first and in this order, with its
`void_reason`: `endpoint_undefined` (S undefined at an endpoint, or an endpoint bank-quarter excluded, `ratio_gt_1` included), `thin_yardstick`,
`endpoint_recast` (S1, S3), `caption_change` (the pinned class differs between the endpoints, 2.6), `mix_dominates` (S1, S3: the weight term has the
sign of the total and is larger than the within term), `yardstick_disagrees` (S1, S3: the label against YR differs from the label against Y). No date after
2019-12-31 enters any yardstick, and no window that includes 2026 is a yardstick. **S3 is mandatory.** S2 is not subject to the recast, mix or YR tests.

### 4.7 Population rules (the script holds `SPEC_POP_SHA256`; same conventions)

```
P1|primary=JPM_CIK0000019617;GS_CIK0000886982|why=the_only_banks_with_both_standard_tags_at_every_quarter_end(supervisor_count_66_each,_30_Oct_2026,_metadata_only:_own_filing_at_every_quarter_end_2010-06-30..2026-06-30,_2010-03-31_absent,_2009-12-31_comparative_only)|no_bank_enters_or_leaves_primary_after_any_value_is_read
P2|sens_stt=JPM+GS+STT_CIK0000093751|only_calendar_quarter_ends_where_all_three_have_both_values|yardstick_members=those_of_Y_with_all_three_defined_at_q_and_q-8
P3|sens_wfc=sens_stt+WFC_CIK0000072971|built_iff_the_count_probe_shows_both_tags_at_every_calendar_quarter_end_2013-12-31..2026-06-30(51_dates)|else_not_built_and_the_counts_are_printed
P4|four_bank_sample,_fetch-instances_and_the_Morgan_Stanley,_Bank_of_America,_BNY_and_Citigroup_probes=deferred_to_g14b|nothing_in_this_build_reads_or_fetches_them
P5|probes=WFC_CIK0000072971_only|counts_of_period_ends_and_dates_only|no_value_is_written_for_it
P6|calendar_quarter_end=end_is_exactly_Mar-31,Jun-30,Sep-30_or_Dec-31|any_other_end_is_counted_as_off_calendar_and_never_used
P7|source=data.sec.gov/api/xbrl/companyconcept/CIK##########/us-gaap/<tag>.json|unit_key=USD_only|fact_keys_within={accn,end,val,fy,fp,form,filed,frame,start}_else_refuse|dimensioned_facts_are_not_served
P8|own_filing=the_filing_(form_exactly_10-K_or_10-Q)_in_which_all_three_hold:end==implied_end_of_(fy,fp)_(Q1=Mar-31,Q2=Jun-30,Q3=Sep-30,FY_or_Q4=Dec-31_of_fy);0<=filed-end<=100_days;end==the_latest_end_among_that_accession's_facts_for_the_tag|N_and_D_both_facts_of_that_accession_else_quarter_missing_in_primary|two_such_accessions=ambiguous_and_excluded
P9|amended=10-K/A,10-Q/A,10-KT_never_define_the_primary_value|sens_latest=latest_filed_among_all_forms,ties_to_largest_accn,N_and_D_from_the_same_accession_else_missing
P10|conflict=two_different_val_for_one_tag,end,accn=>quarter_excluded_and_check_fails
P11|unit_bounds=1e9<=val<=1e13_else_unit_odd_and_excluded
P12|flags=recast:abs(latest/first-1)>0.01_on_either_tag;jump:abs(q/q_change)>0.30_on_either_tag_between_adjacent_calendar_quarters|flags_exclude_nothing_in_primary|recast_at_an_endpoint_voids_S1_and_S3
P13|sens_noflag=primary_with_every_quarter_flagged_recast_or_jump_for_any_bank_removed|removal_by_flag_only,_never_by_value_or_outcome
P14|sens_eqw=S_q=mean_over_banks_of(N_b,q/D_b,q)|sens_jpm_and_sens_gs=one_bank_alone
P15|no_imputation:missing_is_never_zero,_never_interpolated,_never_replaced_by_a_nearby_quarter|a_bank_missing_at_q_removes_q_from_the_sample
P16|ratio_gt_1=N>D_for_a_bank-quarter|that_bank-quarter_is_excluded_from_every_sample|an_endpoint_so_excluded_voids_its_statement
P17|captions=the_supervisor-pinned_class_of_each_bank's_wording_for_each_line_at_2011-12-31,2013-12-31,2019-12-31,2021-12-31,2023-12-31,2025-12-31(table_2.6)|different_class_at_the_two_endpoints_of_a_statement=VOID_(caption_change)|a_yardstick_window_spanning_a_class_change_at_a_primary_bank_is_excluded_(Y)|JPM_numerator_class_changes_at_2017-03-31;JPM_denominator_and_Goldman_both_lines_do_not_change|yardstick_end_captions_are_otherwise_described_only
P18|sensitivities=labels_reported_with_n_shown|a_sensitivity_is_VOID_only_if_n<10|never_registered
P19|supersede=a_bug_found_after_registration:the_old_registered_row_is_kept_and_marked_superseded,_the_corrected_row_is_added_with_the_next_version,_both_appear_in_the_README|only_the_supervisor_runs_a_registering_build
```

**sha256 of that text: `6492ea1015b05b54cff27267e6228eb480e68ec7aa3f4533573c62b146b096fe`** (3401 bytes, 19 lines). `registered.csv` carries it in `population_sha256`.

## 5. Outputs

**Script `bin/collateral_reuse.py`.** Modes `fetch-concepts` (supervisor only, under R1-R3a), `build --vintage YYYYMMDD --stage pre|dry|full` (offline;
`full` is the supervisor's and is byte-identical on re-run), `selftest` (synthetic, no network, under 30 s). Committed files in `data/collateral_reuse/`
(the first twelve lines below) and `data/vintages/collateral_reuse/<YYYYMMDD>/` (the last line); each CSV begins with one `# source:` line.

**Header allowlist, canonical text.** One line per file, `<name>:<headers comma-joined, no spaces>`, LF endings, final LF included, in this order. The
script holds `SPEC_ALLOW_SHA256`; **`bin/check.sh` holds its own literal copy of these thirteen lines** and never reads them from the script. M28 skips the
`# source:` line.

```
banks.csv:cik10,ticker,entity_name,role,tag,n_period_ends,n_calendar,n_off_calendar,n_own_filing,first_end,last_end
quarters.csv:cik10,ticker,end,basis,accession,form,filing_date,n_usd,d_usd,share_pct,flags,status
samples.csv:sample,basis,end,n_banks,n_usd,d_usd,share_pct,flags
changes.csv:sample,basis,kind,start_end,end_end,share_start_pct,share_end_pct,change_pp,role
registered.csv:statement_id,version,superseded,sample,basis,vintage,n_dist,dist_min,dist_max,stat,unit,gap_to_extreme,rank,rank_of,sign,label,blind,void_reason,prereg_sha256,population_sha256
decomposition.csv:window,sample,bank,weight_start_pct,weight_end_pct,share_start_pct,share_end_pct,within_pp,mix_pp,total_pp
revisions.csv:cik10,ticker,end,tag,first_usd,latest_usd,rel_diff_pct,first_accession,latest_accession,flag
probes.csv:cik10,ticker,tag,n_period_ends,n_calendar,first_end,last_end,n_both_tags,verdict
headline.csv:vintage,sample,basis,statistic,value,unit,n
checks.csv:check_id,description,expected,observed,status
vintages.csv:vintage,host,url_path,status,bytes,sha256,retrieved_utc,elapsed_s
captions_pin.csv:cik10,ticker,end,line,accession,class,caption_wording
concept_extract.csv:vintage,cik10,tag,accn,form,filed,fy,fp,end,val
```

**sha256 of that text: `f7540ed76e484978fc26f00f7841d7eb9cfde08d3a15b2519861ff517802f876`** (1220 bytes, 13 lines). A builder who needs a column changes this text and its hash first, logs it in
Builder decisions, and tells the supervisor.

**Allowed values.** `role` (banks.csv) in {primary, sens_stt, sens_wfc, probe}; `tag` in {N, D}; `basis` in {own_filing, latest_filed}; `status`
(quarters.csv) in {ok, missing_n, missing_d, own_filing_lacks_tags, ambiguous, conflict, unit_odd, off_calendar, ratio_gt_1}; `flags` a `|`-joined subset of
{recast, jump, amended}; `sample` in {primary, sens_stt, sens_wfc, sens_jpm, sens_gs, sens_eqw, sens_noflag}; `kind` in {q8, level}; `role` (changes.csv) in
{yardstick, registered, described}; `statement_id` in {S1, S2, S3}; `version` a positive integer; `superseded` in {no, yes}; `unit` in {pp, pct}; `sign` in
{RISE, FALL, ZERO}; `blind` in {full, partial}; `label` in {RISE_OUTSIDE_RANGE, WITHIN_RANGE, FALL_OUTSIDE_RANGE, LEVEL_ABOVE_RANGE, LEVEL_WITHIN_RANGE,
LEVEL_BELOW_RANGE, VOID}; `void_reason` in {none, endpoint_undefined, thin_yardstick, endpoint_recast, caption_change, mix_dominates, yardstick_disagrees};
`line` (captions_pin.csv) in {N, D}; `class` in {JN1, JN2, JD1, GN1, GD1}; `verdict` (probes.csv) in {enters, does_not_enter, counts_only}; `status` in
`checks.csv` in {PASS, WARN, FAIL, INFO}; in `vintages.csv` it is the HTTP code. Keys unique: `banks.csv` (cik10, role, tag); `quarters.csv` (cik10, end,
basis); `samples.csv` (sample, basis, end); `changes.csv` (sample, basis, kind, start_end, end_end); `registered.csv` (statement_id, version);
`decomposition.csv` (window, sample, bank); `revisions.csv` (cik10, end, tag); `probes.csv` (cik10, tag); `headline.csv` (vintage, sample, basis,
statistic); `vintages.csv` (vintage, url_path); `captions_pin.csv` (cik10, end, line). **No output carries HELD, FALSIFIED, PROVEN, CAUSED, REFUTED or
MATERIAL.**

- **`README.md`** (generated; G14 scans it), plain words, in this order: (1) two opening sentences: what was measured ("the fair-value share of the
  collateral they may re-use that JPMorgan Chase and Goldman Sachs report having re-used, every quarter-end from June 2010 to June 2026, as first
  reported") and the S3, S1 and S2 results (sign, label, the signed change in points, the yardstick's extremes, the rank, the `blind` column); (2) the
  denial sentence; (3) the perimeter in one sentence: two banks, against the page's six, whose pre-2025 share stays unmeasured; (4) what is left out: a
  speed or chain length, prices, money, intraday re-use, Treasury repo alone, the other banks; (5) the yardstick, its thinness (at most four independent
  draws) and the simulation sentence of 4.0, and the line "JPMorgan's numerator caption widened in the first quarter of 2017; windows that span that
  change are excluded from the yardstick"; (6) the path of the share, per-bank shares, the within-bank and weight-shift split and any `mix_dominates`
  VOID; (7) the sensitivities and variants with n shown, and whether any changes a label, including the 2011-start unrestricted variant; (8) the caption
  table of 2.6 and the recast result at 2016-12-31; (9) what was known before the build (2.5, in plain words) and which statements are therefore less
  blind; (10) the later-filings table and what the flags mean; (11) coverage: counts and the expected-dates table; (12) any superseded row (P19) beside
  its replacement; (13) a column dictionary glossing "fair-value share", "permitted to be re-used" (collateral received that the bank is allowed to
  sell or repledge), "re-pledged" (the part it has sold, repledged, delivered or otherwise used, as the filing words it), "first reported", "quarter-end",
  "yardstick", "percentage point", "vintage"; (14) citations.
- **`SOURCES.md`:** every URL with date and status (404s included), the commit of this spec, the caption pins and their source, the own-filing and
  first-reported rules, the KNOWN list of 2.5, Builder decisions.

## 6. Leak and integrity rules

1. Committed: in `data/collateral_reuse/` only the twelve CSVs, README.md and SOURCES.md; in each vintage folder only `concept_extract.csv`; never a
   `.json`, `.xml`, `.zip`, `.html` or STOP file. The `raw/` cache is gitignored. The dry stage writes only outside these folders.
2. No local path (`/Users/`, `/private/`, `~/`), no `@`, no email address, no personal name, and **no byte of `SEC_UA`'s value** in any written file.
   Company names are SEC registrant names. The script writes nothing outside its two folders (and the scratch folder of the dry stage) except landing's
   `.gitignore` rule, REPRODUCE.md paragraph, CALENDAR rows and RESEARCH_STATE.md row.
3. **Blind order.** No human or agent opens `raw/`, the extract, or any `n_usd`, `d_usd` or `share_pct` cell for 2009-2025 before the registering build
   has run once. The extract is committed in the same commit as, or after, the full-stage outputs (criterion 10).
4. **Attack parcels carry the blind rule.** Any outside review of the results must forbid computing a result from a public table and any reading of
   the series before the labels are fixed (a reviewer with web access can compute a blind result from a public table).

## 7. Selftests (synthetic only; each guard applies its own mutant, and an uncaught mutant fails the selftest; fixtures are two-sided)

**G14's literal patterns, both compiled with `re.I`** (pasted, not imported). `CAUSAL_RX` (as in the g13 spec):

```
\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b
```

`EXTRA_RX` (the g13 list, with this build's additions; the denial sentence is exempt):

```
\b(?:in|out)flows?\b|\bflow(?:s|ed|ing)?\s+(?:into|out\s+of|from|to)\b|\bmanipulat\w*|\bmanag(?:e|ed|es|ing)\s+(?:earnings|results|revenue)\b|\bearnings\s+management\b|\baggressive\w*|\bfraud\w*|\bmisstat\w*|\binflat(?:e|ed|es|ing)\b|\bboost(?:s|ed|ing)?\b|\bpadd(?:ed|ing)\b|\blow[- ]quality\b|\bfake\b|\b(?:prices?|valuations?|multiples?|stocks?|shares)\s+(?:rose|fell|rallied|moved|jumped|dropped)\b|\bmaterial\w*|\boverstat\w*|\bpulled\s+forward\b|\bflatter\w*|\bwindow[- ]dressing\b|\bred\s+flags?\b|\bvelocity\b|\bintensity\b|\bmultiplier\b|\bleverag\w*|\bfuel(?:l?ed|s|ing)?\b|\bsupport(?:ed|s|ing)?\s+(?:the\s+)?(?:rally|prices?|valuations?)\b|\bsignifican\w*|\bpermissive\b|\bpropell\w*|\bpow(?:er|ered)\s+(?:the\s+)?(?:rally|rise)\b|\bproves?\b|\bproven\b
```

(The plural "shares" before a verb of movement is banned by the fifth alternative; the singular "the share rose by 1.2 points" is allowed and is how the
signed change is stated.)

Guard identifiers are stable; **G11 and G19 are withdrawn (R1-8).**

| Guard | Protects | Mutant that must be caught |
|---|---|---|
| G1 parsing | R8 | a float sum; a missing fact read as 0; a non-USD unit accepted; **a value above 2^53 and a fractional value** read through float; a share computed as a mean of ratios in `primary` |
| G2 calendar quarter-ends | P6 | ends **2009-03-27, 2008-12-26, 2010-03-30, 2010-04-01** used (must be `off_calendar`); 2010-03-31 refused; an off-calendar end silently moved to a quarter-end |
| G3 own filing | P8 | a comparative column of a later filing used; a `10-K/A` or `10-Q/A` defining the value; N and D from two accessions; **a filing 100 days after `end` accepted and 101 refused**; `fy`/`fp` implying a different end accepted; **`fp` = Q4 with form 10-K not mapped to 31 Dec**; two qualifying accessions not `ambiguous`; a missing denominator filled from a later filing in the primary |
| G4 latest-filed and revisions | P9, P12 | `sens_latest` using first-reported values; ties not to the largest `accn`; a difference of **1.0000% flagged and 1.0001% not**, or the reverse; `revisions.csv` appended instead of regenerated |
| G5 facts, flags and exclusions | P7, P10, P12, P16 | a fact with an extra key accepted; two different values for one accn, tag and end not `conflict`; **a q/q move of 30.0000% flagged and 30.0001% not**; **N = D accepted and N = D + 1 USD excluded as `ratio_gt_1`**; a `ratio_gt_1` quarter left in a sample or an endpoint so excluded not VOID; a flagged quarter excluded from `primary` |
| G6 units | P11 | **999,999,999 refused and 1e9 accepted, 1e13 accepted and 10,000,000,000,001 refused**; a `USDm` unit key accepted; a bank with two unit keys accepted |
| G7 aggregation and gaps | P15, 3.5 | S = ΣN/ΣD computed over one bank when the other is missing; a missing quarter treated as zero, interpolated or replaced by the previous quarter; State Street counted at a date JPM lacks; `sens_stt` using dates before 2013-12-31 |
| G8 changes and yardstick | 3.6, 4.6 | q−8 found by row position across a missing quarter; end quarters **2011-09-30 (out), 2011-12-31 (in nominal), 2019-12-31 (in), 2020-03-31 (out)**; on a full synthetic fixture n_nominal other than 33, defined other than 31, and not-excluded other than **23** for Y and **17** for YR; YL end dates **2016-12-31 (out), 2017-03-31 (in), 2019-12-31 (in), 2020-03-31 (out)**; a 2026 date in either set |
| G9 labels, sign and VOID | 4.6 | stat equal to max(Y) labelled RISE (must be WITHIN); max + 1e-9 not RISE; min − 1e-9 not FALL; labels on rounded values; **sign at +0.0999, +0.1000, −0.0999, −0.1000 points → ZERO, RISE, ZERO, FALL**; a WITHIN label with a positive change carrying sign ZERO; **n_Y = 19 VOID and 20 not; n_YR = 13 VOID and 14 not; n_YL = 9 VOID and 10 not**; VOID order other than the hashed one (a statement with a recast endpoint and a caption change must report `endpoint_recast`); an endpoint recast but a label written; a caption class differing at the endpoints but a label written; S2 voided for recast (it must not be) |
| G10 registered and hashes | 4.6, 4.7 | **a constant edited so any block's sha256 changes** (build refuses `registered.csv`); `prereg_sha256` differing from M28's literal copy; S3 scored against a yardstick that includes its own window; `SPEC_CAPTION_SHA256` not the hash of `captions_pin.csv` |
| G12 counts and expected dates | C01, C02 | 65 or 67 period-ends passing C01 for JPM or GS; `n_off_calendar` ≠ 0 passing; 2010-03-31 present, 2009-12-31 own-filing, or a missing quarter-end among the 65 passing C02 |
| G13 decomposition | 3.8 | within + mix ≠ total beyond 1e-9 point; the simple (non-Shapley) split; **mix of the total's sign and larger than within not VOID, and mix smaller than within VOID**; mix with the opposite sign VOID; the weights summing to other than 100 |
| G14 wording | R6 | the patterns above applied to README.md and SOURCES.md except the denial sentence; the README template passes; "re-use velocity rose", "the share drove the rally", "intensity fell", "a significant rise", "banks fuelled the boom", "shares rose because of it" and "shares rose by two points" each fail while "the share rose by 1.2 points" passes; a README template that lacks the 2017 caption-change line, the `blind` column or the words "fair-value share" fails |
| G15 STOP latch | R3a | a planted `STOP_cru` blocks every request (exit 2, file unchanged); 301, 403, 429, 500, empty, HTML and non-JSON bodies each write STOP with five fields; a companyconcept 404 writes no STOP; a timeout exits 3 |
| G16 fetch safety | R1-R3, R2 | a request to any host but data.sec.gov (`www.sec.gov`, `efts.sec.gov`, `fred.stlouisfed.org` each refused); a fetch with `SEC_UA` unset (must exit 2); **`SEC_UA`'s value in any written byte**; a redirect followed; a retry; **a 0.9 s gap**; a cap exceeded; a cached body re-requested; a second writer of `vintages.csv` |
| G17 vintages and stages | R4, 3.2-3.4, P19 | a build mixing two vintages; `registered.csv` rewritten by a second vintage; a `--stage pre` that reads a `val`; **`--stage dry` writing any value, share, sign, label or void reason, writing `registered.csv`, or writing into the committed folder**; a `--stage full` run by the builder's default; a supersede that deletes the old row instead of marking it `superseded = yes`, or that does not add the next `version` |
| G18 allowlists and leak | 5, 6 | an extra or renamed column; `SPEC_ALLOW_SHA256` not the hash of the canonical text, **or not equal to M28's literal copy**; `# source:` compared as a header; a thirteenth CSV in the output folder; a duplicate key; on a planted folder: a `.json`, an `.xml`, a `/Users/` path, an `@`, each reported; the clean folder passes |
| G20 tie-outs | C03 | a pin off by one unit of its last digit passing; a pin off by half a unit passing and by 0.6 unit failing; a pin for a date the series lacks passing instead of being reported |
| G21 caption change | 2.6, 4.6 | a window **starting 2016-12-31 and ending 2018-12-31** kept in Y; **ending 2016-12-31** excluded; **starting 2017-03-31 (ending 2019-03-31)** excluded; **ending 2017-03-31** kept; the exclusion applied to Goldman-only windows; YR computed without the exclusion; **a Y and YR that give different range labels not VOID `yardstick_disagrees`**, or the same labels voided; the 2017 caption line absent from the README |

## 8. Pinned checks (`checks.csv`)

Check identifiers are stable. **Withdrawn (R1-8): C02 (old), C06, C10, C13 (merged into C14), C15, C16, C17, C18.** The identifiers below are the live ones.

- **C01 Counts (FAIL for JPM and GS, WARN otherwise):** JPM and GS have **66** period-ends per tag (any 10-K or 10-Q fact, 2009-12-31 to 2026-06-30), **65** of
  them in own filing, and **`n_off_calendar` = 0**; State Street has 52, all in own filing; Wells Fargo's counts are printed for P3. A mismatch is
  reported, not repaired.
- **C02 Expected dates (FAIL):** for JPM and GS, both tags, every calendar quarter-end 2010-06-30 to 2026-06-30 is in own filing; 2010-03-31 is absent; 2009-12-31
  is comparative-only; for State Street, every quarter-end 2013-12-31 to 2026-09-30 is in own filing.
- **C03 Tie-outs (FAIL):** for the nine bank-date pairs of 2.5, the primary N and D equal the filing-note value within half the unit of the pin's last
  printed digit; the unrounded gap is written to `observed`.
- **C04 Same accession (FAIL):** every primary quarter's N and D carry one `accn`.
- **C05 Closure (FAIL):** `samples.csv` `n_usd` and `d_usd` equal the sums of the banks' `quarters.csv` rows; `share_pct` recomputes to 3 decimals.
- **C07 Hashes (FAIL):** the constants reproduce the three hashes of 4.6, 4.7 and 5 and `SPEC_CAPTION_SHA256`; `prereg_sha256` and `population_sha256` in
  `registered.csv` equal them.
- **C08 Tamper (FAIL):** `changes.csv` D8 is recomputed **at full precision from the USD sums in `quarters.csv`** (not from the rounded shares) and equals
  the written value to 3 decimals; each `registered.csv` row recomputes from them. After a second vintage, only the vintage named in `registered.csv`
  is recomputed.
- **C09 Cache integrity (FAIL):** each raw body's sha256 and size equal its `vintages.csv` row.
- **C11 Blind order (FAIL):** `--stage pre` reads no `val` field and the dry stage writes no value.
- **C12 Pre-stage coverage (INFO):** the status counts of every bank-quarter.
- **C14 Units and conflicts (FAIL):** every fact's unit key is `USD`; no primary quarter is `unit_odd`, `conflict` or `ambiguous`.
- **C19 Captions (FAIL):** `captions_pin.csv` equals `SPEC_CAPTION_SHA256` and carries a class for each of the 24 bank-date-line cells of 2.6.
- **C20 Yardstick counts (WARN):** n_Y = 23 and n_YR = 17 on the real data; a difference is reported (the thin rules still apply).

## 9. Success criteria (each with the command and the number that would disprove it)

1. `python3 -I bin/collateral_reuse.py selftest` prints G1 to G21 except the withdrawn G11 and G19, each `caught`, and exits 0. **Disproved by** any
   `SURVIVED`, a missing live G-number, or a non-zero exit.
2. **Supervisor's fetch:** `vintages.csv` has **8** rows for the vintage, all host `data.sec.gov`, status 200 except at most the two Wells Fargo
   requests (404 allowed there only), no 403, 429 or 3xx, no gap below 1.0 s between `retrieved_utc` values; no `fetch_log.csv` exists; and `grep -rlF
   "$SEC_UA" data/collateral_reuse data/vintages/collateral_reuse | wc -l` prints **0**. **Disproved by** another host, a STOP file, a shorter gap, a 404
   on a primary or State Street tag, or any file holding the UA.
3. **Safe order:** `build --stage pre` then `build --stage dry --out <scratch>` are run first (by the builder or the supervisor): `grep -c ',FAIL$'` on the
   dry `checks.csv` prints **0**, and the dry folder holds no `registered.csv` and no cell with a share, sign or label. Only then does the supervisor run
   `build --stage full`, after which `grep -c ',FAIL$' data/collateral_reuse/checks.csv` prints **0**. WARN rows are reported to the supervisor.
4. **Counts and dates:** `banks.csv` shows **66** period-ends and **65** in own filing for each of JPM and GS on each tag, `n_off_calendar` 0, and **52**
   for State Street; `quarters.csv` has an `ok` row for each primary bank at every quarter-end 2010-06-30 to 2026-06-30 (65) and none for 2010-03-31;
   `samples.csv` (primary, own_filing) has **65** rows (fewer only if a `ratio_gt_1` or other status is shown for a named quarter); `changes.csv` shows
   n_Y = 23 and n_YR = 17 (C20). **Disproved by** a different count without a named cause.
5. **Sums close:** `python3 -I -c` over `quarters.csv` reproduces every `samples.csv` `n_usd` and `d_usd` exactly (0 USD difference) and `share_pct` to 3
   decimals for the primary sample; the same over `changes.csv` reproduces `dist_min`, `dist_max` and `stat` in `registered.csv`. **Disproved by** a gap of
   1 USD or of 0.001 point.
6. **Byte-identical rebuild:** the sha256 of every file in `data/collateral_reuse/` other than `registered.csv` is unchanged by a second `build` of the same
   vintage (a command run by the verifier; the check C10 was withdrawn).
7. **Tie-out by a different method:** a verifier, for four bank-dates named by the supervisor after the build and drawn from outside 2.5, reads the two
   lines in the filing note on www.sec.gov and compares them with `quarters.csv`: equal within the note's rounding. **Disproved by** any difference above
   half the note's unit, which would mean a segment, a unit or a definition problem the tie-outs did not catch.
8. **M28** (warn-only, in `bin/check.sh --all`), with its own copies of the thirteen header lines and the 4.6 hash: names; headers (skipping `# source:`);
   no `.json`, `.xml`, `.zip` or STOP in git; no local path or `@`; no G14 pattern in README.md or SOURCES.md outside the denial sentence; no banned verdict
   word; labels, signs and void reasons only from 5; `prereg_sha256` equal to its copy; C05's and C08's sums; no duplicate key. **On a scratch copy** with a
   planted `.json`, a renamed header, a `HELD` cell and a `samples.csv` `n_usd` that no longer equals the sum of its banks, M28 prints **four** ✗ lines; on the
   clean folder, ✓. Shown failing on the planted copy before it lands.
9. **Supervisor hash step:** extract the three canonical blocks from this spec and take their sha256: they equal `SPEC_PREREG_SHA256`, `SPEC_POP_SHA256`,
   `SPEC_ALLOW_SHA256`, M28's literal copies, and `4ca76d72f2e6050e5e6f11aea432195b170405d2391783de3cca3b90641cd55b`, `6492ea1015b05b54cff27267e6228eb480e68ec7aa3f4533573c62b146b096fe`, `f7540ed76e484978fc26f00f7841d7eb9cfde08d3a15b2519861ff517802f876` (or the re-hashed values in a ruling); and the sha256
   of `captions_pin.csv` equals `SPEC_CAPTION_SHA256`.
10. **Stage order:** `git log --diff-filter=A` on `concept_extract.csv` is not earlier than on `quarters.csv`. **Disproved by** a value file committed first.
11. **Spec before data:** `git log --diff-filter=A --format=%cI -- _research/2026-10-30-Collateral-Reuse-History-Spec.md` is earlier than the first
    `retrieved_utc` in `vintages.csv`. **Disproved by** a later commit, or none.
12. **Registration:** `registered.csv` has exactly **one** row each for S1, S2 and S3 (`version` 1, `superseded` no) with the 4.6 and 4.7 hashes, a sign, a
    `blind` value (S3 full, S1 and S2 partial), and labels from the list in 5. After a second vintage `grep -c '^S1,' data/collateral_reuse/registered.csv`
    still prints **1** and the S1 row is byte-identical. **Disproved by** a second row without a stated supersede, a changed row, or a verdict word.
13. **README cold-reader test.** Three fresh agents read only the README: a non-specialist, a bank-regulatory accountant, and one told to report the
    signs, labels, signed changes and yardstick extremes. **Pass** only if the first two can say what "permitted to be re-used" and "re-pledged" mean,
    that this is two banks and not the page's six, that it is not a speed or a statement about prices or money, that the yardstick holds at most four
    independent draws and a "rise outside range" would appear roughly one time in nine by chance, that WITHIN_RANGE does not mean "did not rise", and
    which statements were less blind; and the third reports it all. **Fail** if any reader thinks the result is a speed, a cause of the price rise, a
    six-bank history, or that a WITHIN_RANGE label means no rise.
14. **Re-run with Q3 2026:** after the 5 Nov census row and the JPM and Goldman Q3 10-Qs, a new vintage adds 2026-09-30 for JPM, GS and State Street to
    `quarters.csv` and `samples.csv` as described rows; `registered.csv` is not re-scored; `revisions.csv` lists any first-reported value that moved; C08
    recomputes only the vintage named in `registered.csv`. **Disproved by** a changed registered row or a Q3 value used in a yardstick.
15. **Registration of the work (CLAUDE.md "four places"):** at landing, the CALENDAR rows below and a `RESEARCH_STATE.md` §5 row naming the goal row it
    serves (A13, the collateral channel; A12 channel (c)); no findings document and no read-table row until the labels exist. **Disproved by** a
    missing row.

**CALENDAR rows (text, for the builder to add at landing):** `2026-11-02`, "Collateral re-use history (g14): the supervisor runs python3
bin/collateral_reuse.py fetch-concepts (SEC_UA set), then the builder or supervisor runs build --stage pre and --stage dry (status counts only, no
value to be read); then the supervisor runs build --stage full; read registered.csv rows S3, S1, S2 (sign, label, blind, void reason) and decide the
two-bank sentence by the table in 4; do not re-score"; and `2026-11-09`, "Collateral re-use history (g14), Q3 2026: after the 5 Nov census row and the
JPM, GS and State Street Q3 10-Qs, fetch-concepts again into a new vintage and build; add 2026-09-30 as described rows; S1-S3 are not re-scored; compare
the XBRL Q3 values with the census hand-pull of CALENDAR row 2026-11-05". **RESEARCH_STATE §5 row:** "COLLATERAL RE-USE HISTORY: SPEC g14 ->
bin/collateral_reuse.py, data/collateral_reuse; serves A13 (the collateral channel: whether re-use rose before the price rise, C-152). Trigger: CALENDAR
2026-11-02; Q3 re-run 2026-11-09. Deferred: g14b, the four-bank year-end sample."

**Landing (builder):** `.gitignore` rule for `data/vintages/collateral_reuse/*/raw/`, REPRODUCE.md paragraph, the CALENDAR rows, the RESEARCH_STATE.md §5
row, M28, a HANDOVER row; commits nothing.

## 10. OPEN questions (only where a ruling is still needed)

Closed by the rulings and the supervisor's facts: the 66 against 67 and State Street's 2026-09-30 (2.1); Morgan Stanley and Bank of America, element
names and the four-bank statement (cut, g14b); Wells Fargo (P3 stands); own-filing identification by submissions pages (cut); line-definition changes
(captions pinned, 2.6); yardstick start, S3 and the second yardstick (R1-2, R1-12); first-build timing (dry stage, R1-7); collateral passed between
the two banks (a stated limit); the tag names against the line wording (captions pinned).

- **O-1 "Larger in size" in the mix test (R1-3).** I read it as: the summed weight term has the sign of the total and is larger than the summed
  within term (the weight term dominates). The narrower reading, larger than the *total* (so that the within term opposes the total), is contained in
  this one. *Option:* the narrower reading would VOID fewer statements.
- **O-2 The sign of S2, a level (R1-1).** A level has no change. I defined it as the sign of the 2023-12-31 level minus the median of the 2017-2019 levels,
  by the same 0.1-point rule. *Option:* drop the sign for S2 (leave the column `ZERO`/empty), or sign it against the 2019-12-31 level.
- **O-3 Transport hardening (Grok point 10, not in the rulings).** One retry after `Retry-After` with no latch on a single 403; `Accept-Encoding: gzip`;
  ignoring unknown JSON keys when the P8 fields are present. I applied only the `fp` = Q4 mapping (P8). The spec keeps R3 and R3a as they were.
- **O-4 JPM captions between pinned dates.** The supervisor read the 10-Ks of 2011-2016 and the 2017 10-Qs; the 10-Qs of 2010-2016 were not read. The build
  assumes JN1 for every JPM quarter before 2017-03-31. *Option:* the supervisor reads one 2016 10-Q label to confirm, or accepts the assumption.

## Supervisor rulings

*Appended here by the supervisor, newest last, before any data run; they override the body.*

### Supervisor rulings, round 1 (30 Oct 2026)

Applied in the body as follows (one line each; R1-12 was an addendum and supersedes the registered-yardstick part of R1-2):

- **R1-1 Statements.** S3 mandatory (for "before"); S1 and S2 stay; each carries a registered sign (RISE / FALL / ZERO, ZERO below 0.1 point) apart from the range
  label; allowed sentences follow sign and label together; WITHIN_RANGE states the signed change and never implies "did not rise"; the label is "unusual
  against the yardstick" (0, 4.6).
- **R1-2 Yardstick.** Registered 2013-12-31 to 2019-12-31 (25 nominal, min 22) was **superseded by R1-12**; the described variants (2011-start, non-overlapping
  spans, December-only), the chance wording (one-sided about one in nine, by simulation) and the fence-post (five nominal disjoint spans; at most four usable)
  are in 3.10 and 4.0.
- **R1-3 Mix.** Shapley split of each registered change; VOID `mix_dominates` when the weight term has the total's sign and is larger than the within term;
  per-bank shares beside (3.8, 4.6; O-1).
- **R1-4 Restatements.** S1 or S3 is VOID `endpoint_recast` when either endpoint is flagged `recast` (2.2, 4.6).
- **R1-5 Ratio above one.** Excluded from every sample; an excluded endpoint voids its statement (P16, G5).
- **R1-6 Definitions.** Caption table filled from the supervisor's reading (2.6); a statement with a different caption class at its endpoints is VOID
  `caption_change`; maximum and minimum quarters' captions read after the build as a described check; the statistic is named "fair-value share".
- **R1-7 Safe first build.** Stages pre, dry and full; the builder runs only selftest, pre and dry on real data; the supervisor runs the registering build;
  the supersede rule of P19 (3.3, 3.4, G17).
- **R1-8 Cuts.** Four-bank sample, `fetch-instances`, submissions and the BNY, Citigroup, Morgan Stanley and Bank of America probes cut (g14b); Wells Fargo's two
  requests kept; G11, G19, the AST-scan parts of G15 and G17, C02 (old), C06, C10, the mtime part of C11, C13 (into C14), C15-C18 withdrawn; sensitivities VOID only
  below n = 10; `fetch_log.csv` merged into `vintages.csv` in `data/collateral_reuse/` (R4, 6.1, M28); O-2, O-3 and O-13 removed.
- **R1-9 Blind column.** `registered.csv` carries `blind` (S3 full; S1 and S2 partial) and the README prints it (2.5).
- **R1-10 Small fixes.** README item 4 says "a speed or chain length"; the plural "shares" before a verb of movement is banned (R6); C08 recomputes at full
  precision from the USD sums and, after a second vintage, only the named vintage; C01 and C02 pin the expected-dates table and `n_off_calendar` = 0; criteria 4
  and 14 updated; the Goldman off-calendar narrative deleted (P6 and its mutants kept).
- **R1-11 Page wording.** The six-bank sentence stays; the two-bank result is a separate sentence naming the banks (4).
- **R1-12 Caption-spanning windows (addendum).** Registered Y = non-spanning overlapping eight-quarter changes ending 2011-12-31 to 2019-12-31: 33 nominal, 23
  defined (minus 2 lost to P8, minus 8 spanning), min 20; YR (ends from 2013-12-31: 25 nominal, 17 defined, min 14) is the registered robustness test, and a
  different range label is VOID `yardstick_disagrees`; the Goldman-only yardstick is described; the 2017 caption change is in the README and in G21; the recast flag
  at 2016-12-31 is reported. **The counts 23 and 17 were re-derived by the spec author and are correct.**

**Additions of the spec author, not in the rulings (strike if unwanted):** `fp` = Q4 maps to 31 December (P8; Grok point 10); the unit band tightened to
1e9-1e13 and the tie-out tolerance set at half the unit of the pin's last digit (Grok point 8); the column `gap_to_extreme`; a minimum of 14 for YR (the
rulings give none); the sign of S2 (O-2); the choice that S2 is not subject to the recast, mix or YR tests (the rulings name S1 and S3).

### Supervisor rulings, round 2 (30 Oct 2026)

- **O-1 (mix test):** the author's reading stands: VOID when the weight term has the same sign as the total and is larger in size than the within term.
- **O-2 (S2 sign):** keep S2's sign against the median of the 2017-2019 levels, by the 0.1-point rule.
- **O-3 (transport):** R3 and R3a stand unchanged. The project rule is to stop on any 403, 429 or bot check and never retry around it.
- **O-4 (JPM before 2017):** resolved. The supervisor read the 10-Q for 2016-09-30 (accession 0000019617-16-001150, company label linkbase): numerator "Collateral received that was sold or repledged" (JN1 scope), denominator "Fair value of financial assets accepted as collateral to sell or repledge, deliver or otherwise use" (JD1 scope). The JN1 assumption for quarters before 2017-03-31 is kept, now with one 10-Q read.
- **The author's added items** (fp = Q4 maps to 31 December; unit band 1e9 to 1e13; tie-out tolerance half the last printed digit; the `gap_to_extreme` column; withdrawn ids left as gaps; captions_pin.csv as a committed file) are accepted.
- **S2 exemptions:** S2 is exempt from the recast, mix and YR tests, as the author applied; it is VOID only on caption change, an undefined endpoint or a thin YL.
- **captions_pin.csv** is committed with this spec (24 rows, 2 banks x 6 year-ends x 2 lines). `SPEC_CAPTION_SHA256` = `2cfe524cc2257ce2951445f4d759784dd776a71a4910528b050e1c319695c6aa`.
