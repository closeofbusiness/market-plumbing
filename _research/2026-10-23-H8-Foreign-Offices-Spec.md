# Spec: foreign banks' US offices, "net due to related foreign offices", weekly (Fed H.8) (spec author, 23 Oct 2026; rewritten after rounds 2 and 3)

*Candidate X2 of `_research/2026-10-19-CGFS65-Dollar-Funding-Reading.md`; dossier `dossiers/cross-border-and-fx.md`. House style follows
`_research/2026-10-19-UK-Gold-Exports-China-HK-Spec.md` and `_research/2026-10-19-FX-Hedged-Treasury-Yield-Spec.md`. Script
`bin/h8_foreign_offices.py`, outputs `data/h8_foreign_offices/`, check.sh guard **M21**.*

*"Observed" means seen by the spec author on 23 Oct 2026 between 12:02 and 12:10 UTC, with the CLAUDE.md non-SEC User-Agent and one
request per URL: 16 requests, all HTTP 200, none refused (section 2.6). The H.8 release current then was dated 16 Oct 2026 (data to
Wednesday 7 Oct). "Relayed" means taken from a project file or a review and not re-read at source. The rewrite made no new request: every
re-derived pin comes from the spec author's cached copy of the 16 Oct vintage. The rulings at the end are the record. This body applies
them, and where round 3 differs from round 2, round 3 is applied. The spec author computed no quarter-end change and no headline
statistic. On real data it checked units, signs, identities and the levels on the named endpoint Wednesdays (section 8).*

## 0. Goal, and what the result can and cannot say

- **Record** the weekly level of H.8 line 38, "Net due to related foreign offices", for foreign-related institutions: US branches and
  agencies of foreign banks plus Edge Act and agreement corporations (US subsidiaries chartered to do international banking). The levels
  are Wednesday close-of-business values, not seasonally adjusted, from June 2004.
- **Beside it, record** the same line for domestically chartered banks and for all commercial banks.
- **Answer** five descriptive questions fixed in section 4 (Q1-Q4 and Q6; Q5 was dropped by R3-7). The paths are split at every
  published break (R3-3). Multi-year changes run between named ordinary Wednesdays (R3-4). Quarter-ends are observed only where the
  quarter-end day is itself a Wednesday (R3-1).

**It can say** what the net position of these US offices toward their related offices was at each Wednesday close, and how it changed
between named ordinary Wednesdays within a break-free segment. It can also say how it changed across the five quarter-ends from 2019 to
2026 that fell on a Wednesday. The levels are MEASURED: the Fed's estimates, benchmarked to quarterly reports. The sums, the sign test and
the binding test are IDENTITY.

**It cannot say** why the position changed, who moved money, or whether any of it relates to a price, a basis or a yield. It cannot show
any position that was held on a quarter-end day and gone by the next Wednesday close. A change in the line is a change in a net stock, not
a measured flow. The line moves with unremitted profits, capital-equivalent and reserve accounts, allowances for credit losses (inside it
for foreign-related institutions since 6 April 2022), panel changes and benchmark revisions, as well as with lending between offices
(section 2.2). **Required README sentence 3** (the first sentence after the two-sentence opening): "It records balances at Wednesday
closes only; it does not show why they changed, and a change in a balance is not a measure of money moved."

## 1. Hard requirements

- **R1. Free public data only (E-005).** The script's host allowlist is `www.federalreserve.gov` and nothing else. No FRED or ALFRED: no
  `stlouisfed.org` host and no FRED series id in any request. No sec.gov, no API key. Every other host is refused before the request.
- **R2. User-Agent** exactly `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)`. The script asserts that it
  holds no `@`, and M10 stays clean. Never send an email address, a name, `SEC_UA` or `CLAUDE_CODE_USER_EMAIL`.
- **R3. Polite, refusal-safe fetches.** GET only, sequential, at least 3 s apart, at most 6 requests a run (XML 1, DDP 4, notes 1), no
  redirect followed.
- **R3a. STOP latches (R3-8).** Any status other than 200, or a body that fails its content test (R3b), writes
  `data/vintages/h8_foreign_offices/STOP_xml`, `STOP_ddp` or `STOP_notes` and ends that source's fetch. There is no retry and no route
  around it. The file is created exclusively and holds five `name: value` lines: `status`, `utc_time`, `url_path`, `retry_after` and
  `body_head` (the first 300 bytes, escaped). **Only a person deletes a STOP file. No agent deletes, renames or overwrites one, the builder
  included.** With a latch present, that source makes no request and the run prints `STOP present: <file>`.
  - With `STOP_xml` and a DDP fetch that passes R3b, the build runs from the DDP packages: `route` = `ddp_fallback`, and C10 = `WARN
    xml_unavailable`.
  - When no route is left (`STOP_xml` together with `STOP_ddp`, or no cached DDP for the run), the script exits 2.
  - `STOP_notes` does not block a build; the newest cached notes page is used, and C11 says so.
- **R3b. Content tests.**
  - XML zip: it opens; it holds `H8_data.xml` and `H8_struct.xml`; `message:Prepared` parses as a date; the 20 series of 2.1 are present
    with the attributes listed there.
  - DDP CSV: the first six lines carry `Series Description`, `Unit:`, `Multiplier:`, `Currency:`, `Unique Identifier:` and `Time Period`;
    the wanted identifiers are present; `Multiplier:` is 1000000 for each.
  - Notes page: it holds the heading text "Notes on Data" and at least one dated note.
- **R4. Cache.** Raw files go to `data/vintages/h8_foreign_offices/`, which is gitignored (the builder adds the rule). They are kept for size,
  not for licence reasons. Keep:
  - `xml/FRB_h8_xml_<prepared-date>.zip`, newest only, pruned by exact file name and never by a glob over the cache root (R2-10), with
    every zip's sha256 kept in `vintages.csv`;
  - `subset/h8_<vintage>.csv`, the 20 series of 2.1 for each vintage, kept forever: this is the revision record;
  - `ddp/<package>_<vintage>.csv`;
  - `notes/h8notes_<utc-date>.htm`.
  The vintage key is the XML's `message:Prepared` date, or `fetch-<utc-date>` on the DDP fallback.
- **R5. Wording (G11).** No causal, flow or motive wording, except in the one README denial sentence (5.3). Flows and positions are never
  written as the cause of a price.
- **R6. Code ownership.** `bin/h8_foreign_offices.py` is new and uses the standard library only. It reads no other project data file
  (R3-7 removed the swap-tape read). No existing script changes, apart from a new warn-only `bin/check.sh` guard M21.
- **R7. Post-registration fixes** are logged in SOURCES.md "Builder decisions" with the old value kept beside the new, never in the README.
- **R8. Denominators.** Every number names its unit and base. Levels and changes are millions of US dollars (`usd_mn`). A share is a
  percentage of the same group's H.8 total liabilities (line 40) on the same Wednesday.

## 2. Data

### 2.1 The series (observed 23 Oct 2026, release of 16 Oct 2026)

| Role | DDP identifier | XML attributes | First week | 7 Oct 2026, $mn |
|---|---|---|---|---|
| **Headline:** foreign-related (FRI), NSA, weekly | `H8/H8/B1100NFRD` | `BG="FR" SA="NSA" CATEGORY="L" ITEM="1100" FREQ="19"` | 1973-01-03 | **836,860.0** |
| Domestically chartered (DOM), NSA, weekly | `H8/H8/B1100NDMD` | `BG="DM" SA="NSA"` | 2004-06-02 | **−483,558.0** |
| All commercial banks (ALL), NSA, weekly | `H8/H8/B1100NCBD` | `BG="CB" SA="NSA"` | 2004-06-02 | **353,302.0** |
| Foreign-related, SA, weekly (context only) | `H8/H8/B1100NFRA` | `BG="FR" SA="SA"` | 1973-01-03 | 869,123.5 |
| Components, per group (suffix `NFRD`, `NDMD`, `NCBD`, `NFRA`) | `B1152` total liabilities (line 40), `B1058` deposits (34), `B3094` borrowings (37), `B3095` other liabilities (39) | | | FRI: 3,642,173; 1,612,007; 981,596; 211,710 |

That is **20 series**: four line-38 series, plus four components for each of FRI NSA, DOM NSA, ALL NSA and FRI SA. The monthly series
`B1100NFRDM` is no longer used, since R3-7 dropped the monthly comparison.

- **Exact suffixes (R2-3).** Identifiers are matched on the whole string. `D` at the end means NSA weekly, `A` means SA weekly, and `DM`
  means NSA monthly. A substring match such as `NFRD` inside `NFRDM` is a FAIL (G4).
- **Units.** DDP `Unit: Currency`, `Multiplier: 1000000`, `Currency: USD`; XML `UNIT_MULT="1000000"`. Values are millions of dollars, and
  those since 2004 all end in `.0`. Release Table 11 prints 836.9 ($bn) for 7 Oct.
- **Weekly levels are Wednesday close-of-business values** (release footnote 1). At the 16 Oct vintage the FRI series had 2,806 weekly
  rows, all Wednesdays, with no gaps. `OBS_STATUS` is `A` on every row of the four line-38 series.
- **Choice: not seasonally adjusted (NSA) Wednesday levels.** Seasonal adjustment would remove part of any quarter-end pattern. The About
  page says FRI seasonally adjusted data "are derived as residuals". Table 11 (NSA) is the table read on 19 Oct. SA is a context row so
  that readers can match Table 10, and it enters no question.

### 2.2 What the line is, its sign, and its breaks

- **Liability side.** In the XML codelist `CL_CATEGORY`, L means "Liabilities"; `CL_ITEM` 1100 is "(38) Net due to related foreign
  offices". Release footnote 24 says: "Excludes the due-from position with related foreign offices which is included in line 38."
- **Accounting test (observed, exact).** Line 38 = line 40 − (34 + 37 + 39). On 7 Oct 2026, FRI: 3,642,173 − (1,612,007 + 981,596 +
  211,710) = **836,860**. DOM: 19,900,577 − (18,130,689 + 1,374,822 + 878,624) = **−483,558**. The gap is 0 on all 2,806 FRI weeks and
  all 1,167 DOM weeks. ALL = DOM + FRI, with a gap of 0 on every week.
- **Sign convention.** **Positive: the US offices owe their related foreign offices, net. Negative: they are owed, net.** Monthly FRI
  averages from Sep 2025 to Sep 2026 ran from **776.4 $bn (Oct 2025) to 897.5 $bn (Apr 2026)** (R2-12, re-derived from the cached
  monthly package). DOM was −483.6 $bn on 7 Oct. **The negative values read on 19 Oct were the DOM line.**
- **Binding is by identity, not by sign (R3-6).** FRI was negative on 755 weeks, the last on 2011-06-15, and the About page allows
  negative levels. A negative FRI value is therefore a WARN. Groups are bound by three checks:
  - each group's own components satisfy that group's sign identity;
  - DOM line 40 exceeds FRI line 40 on every week (the smallest ratio observed since 2004 is 4.0);
  - ALL = DOM + FRI.
  The last check is symmetric in DOM and FRI and cannot catch a swap on its own. **The FRI-versus-ALL limit (R2-4):** "FRI ≤ ALL" is not
  a valid check, because DOM is negative (on 7 Oct, FRI 836,860 > ALL 353,302), so no such bound is used.
- **What reporters put in it** (FR 2644 instructions, item 9.a, page LI-7, footer "April 2024"; observed). A branch or agency reports
  one net position against its own foreign offices, Edge and agreement subsidiaries, IBFs (international banking facilities, which
  H.8 treats as foreign offices), own head office and other related depository institutions in the US. The position includes "unremitted
  profits, any statutory or regulatory capital requirement, any reserve accounts, and any allowance for credit losses". A net due-from
  position is filed as an asset (item 5.a), and H.8 carries it into line 38 as a negative. **Line 38 is not pure interoffice lending.**
- **Breaks (R3-3, R2-2).**
  - Release footnote 20: from **6 April 2022**, FRI allowances are included in line 38. No size is published.
  - Notes on Data entries naming line 38 for FRI, since 2004 (observed): **2 Oct 2019 (−$3.0bn), 29 Nov 2017 (+$5.2bn), 31 Mar 2010
    (−$12.0bn), 2 Apr 2008 (−$18.6bn), 6 Feb 2008 (+$12.0bn)**. The 31 Mar 2010 amount sits in an undated second paragraph of the entry
    (FAS 166/167, foreign-related institutions).
  - Notes for DOM: 4 Apr 2018 (+$2.0bn), 2 Mar 2016 (−$3.1bn), 5 Jan 2011 (+$5.7bn), 20 Aug 2008 (−$8.6bn), 7 Mar 2007 (−$3.2bn), 4 Oct
    2006 (−$10.0bn), 29 Dec 2004 (+$2.0bn).
  - Parse rules: an undated paragraph belongs to the dated entry before it. The group is read per paragraph, not per entry; the
    6 Feb 2008 entry has an FRI paragraph followed by two DOM paragraphs. The page's leading index line, a run of dates, is not an entry.
  - ALL takes the union of both groups' breaks.
- **Revisions (relayed example).** For the week of 5 Aug 2026, `_research/offshore_moneylike_lenses.md` line 310 records $834.4bn from the
  14 Aug 2026 release; the 16 Oct vintage has 839,732 $mn. The week of 6 Aug 2025 was 954.3 then and is 954,274 now.

### 2.3 Release, revisions, vintages

- **Release:** Fridays, "generally at 4:15 p.m." Eastern; on Thursday when Friday is a federal holiday. Data run to the Wednesday nine days
  earlier. Observed: the zip's `Last-Modified` was Fri, 16 Oct 2026 20:15:04 GMT, and `message:Prepared` was 2026-10-16T10:00:00.
- **Revisions:** weekly figures use weights carried forward from the latest Call Reports (the quarterly bank balance sheets). When new
  Call Report data arrive, the weights are updated; the Fed calls this benchmarking, and the change is interpolated over the previous
  quarter (Technical Q&A). Seasonal factors are updated once a year and affect SA only. Structure events are announced in Notes on Data.
- **Vintages (R2-9).** The DDP and the XML serve only the current release. Each run saves the 20-series subset (R4). `revisions.csv` is
  **regenerated deterministically on every build from all adjacent pairs of cached subsets**, in vintage order. It is never read from or
  appended to committed files, and never computed from `weekly.csv`. Two cached zips with the same `Prepared` date and different sha256
  are a FAIL. A vintage whose latest week is earlier than the one before it is a FAIL.
- **Spec author's copy of the 16 Oct vintage:** `…/scratchpad/g10/h8raw/` (temporary; use it if present). sha256: zip
  `2ce2d425cdc21fe7fe3623aec6fe0dc273438e6887cdea813a69e188344c222b`; DDP FRI NSA weekly `450307fe…cad6`; DOM NSA weekly `48841904…f894d`;
  ALL NSA weekly `6bbba727…a8559`; FRI SA weekly `f5a446aa…98e0`. The builder may seed the cache with it as vintage `2026-10-16` after
  checking the hashes, and records that in Builder decisions.

### 2.4 Access routes (R3-8; first ruling O-1)

- **Primary: the release-page XML zip**, `https://www.federalreserve.gov/releases/h8/data/FRB_h8_xml.zip`. The spec author got 8,438,469
  bytes on 23 Oct, holding `H8_data.xml` (SDMX-ML 1.0 compact, 79 MB unzipped), `H8_struct.xml`, `H8_H8.xsd` and `frb_common.xsd`. Parse
  with `xml.etree.ElementTree.iterparse`; never with a regex. **Grok's fetcher got HTTP 500 from the same URL the same day (R3-8)**, so a
  non-200 is expected sometimes, and it latches (R3a).
- **Cross-check, and fallback while it lasts: the DDP preformatted packages**,
  `https://www.federalreserve.gov/datadownload/Output.aspx?rel=H8&series=<id>&lastobs=&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package`.
  Weekly packages: FRI NSA `0e569516edadaa66168c115e5016ff16`, DOM NSA `18461c27aa45d43aa804016497d92ece`, ALL NSA
  `c8dfa96ef1d2db40ce57121ffdddf59d`, FRI SA `53b903ce661b8534202a6d5e36db960d`. Each holds 41 series, including every component of 2.1,
  so the fallback can build everything.
- **The DDP is being retired.** The Board's DDP-FRED page (notice of 16 Jul 2026) plans to remove "Build Your Package" in the week of
  9 Nov 2026, and later in 2026 and 2027 the preformatted packages and the DDP itself. The notice says XML files on release pages remain.
  FRED is off limits. When a DDP package fails while the XML is fine, C10 = `WARN ddp_unavailable` and the build goes on.

### 2.5 (Removed by R3-7: the swap-tape basis is no longer read.)

### 2.6 Licence, and the requests made

- **Licence.** The Board's website policy (`/disclaimer.htm`, observed): "Unless otherwise indicated, information on Board's website is in
  the public domain and may be copied and distributed without permission. Please cite to the Board as the source." Derived tables are
  committed with that citation; raw files stay in the cache for size (R4).
- **Requests on 23 Oct 2026, all 200:**
  - `releases/h8/current/default.htm`, `releases/h8/h8notes.htm`, `releases/h8/about.htm`, `releases/h8/h8_technical_qa.html` and
    `releases/h8/default.htm`;
  - `datadownload/Choose.aspx?rel=H8`, the four weekly packages and the FRI monthly package;
  - `releases/h8/data/FRB_h8_xml.zip`, `data/data-download-fred-information.htm` and `disclaimer.htm`;
  - `apps/reportingforms/Report/Index/FR_2644` and the FR 2644 instructions PDF
    (`DownloadAttachment?guid=386cbedb-80c8-4cce-a618-a7f3e943b747`).

## 3. Method

1. **Fetch** (mode `fetch`): the XML zip, the four DDP weekly packages, then the notes page; at most 6 requests, each logged with its
   sha256.
2. **Select series by exact identifier and attribute, never by column position.** In the XML, select on `SERIES_NAME` and assert `BG`,
   `SA` and `CATEGORY`. In the DDP, select on `Unique Identifier:` and assert that the `Series Description` names the group
   ("foreign-related institutions", "domestically chartered commercial banks" or "all commercial banks") and the basis ("not seasonally
   adjusted" or "seasonally adjusted"). A mismatch is a FAIL (G1).
3. **Weekly ledger** from 2004-06-02 to the latest Wednesday L. There are rows for (week, FRI|DOM|ALL, NSA) and (week, FRI, SA).
   `change_usd_mn` is the level minus the previous Wednesday's level. `pct_of_total_liabilities` = 100 × line 38 / line 40 for the same
   group, basis and week, to 2 decimals.
4. **Identities and binding on every week:** line 38 = 40 − 34 − 37 − 39 for each group and basis (tolerance 0.5 $mn; observed gap 0);
   ALL = DOM + FRI (NSA); DOM line 40 > FRI line 40. Any breach is a FAIL. A negative FRI level is a WARN, listed by week (R3-6).
5. **Breaks and segments (R3-3).** The break weeks for a group are its Notes on Data weeks (method 6) plus, for FRI and ALL, 2022-04-06.
   A segment runs from one break week to the Wednesday before the next. The break week opens the new segment, and the change ending at
   a break week belongs to no segment. `segment_start` in `weekly.csv` is the first week of the row's segment, or 2004-06-02 before the
   first break. **No change, minimum or maximum is ever taken across a segment boundary.**
6. **Notes (R2-2).** Parse every dated entry together with the undated paragraphs that follow it. For each paragraph that names "net
   due to related foreign offices", record the week, the group of that paragraph, the signed amount ("-$3.0 billion" becomes −3000.0) and
   `paragraph_index`. Footnote 20 is added as kind `footnote`, week 2022-04-06, with the amount blank.
7. **Quarter-ends (R2-1 as amended by R3-1).** For quarter q with last day D(q), W(q) is the Wednesday nearest D(q), with an offset of
   −3 to +3 days. `qe_role` is `qe` on W(q), `after_qe` on W(q)+7 and `none` otherwise. Then:
   - `delta_qe_wed` = L(W) − L(W−7) and `delta_next` = L(W+7) − L(W), for FRI and DOM, NSA;
   - `on_date` = yes when the offset is 0, i.e. D(q) is a Wednesday;
   - `qe_day_in_window` = yes when the offset is ≥ 0, meaning `delta_qe_wed` spans D(q); when the offset is negative, D(q) falls in
     `delta_next`;
   - `straddles_break` = yes when either change ends on a break week of that group;
   - `frozen_set` = yes for the 31 quarters 2019Q1-2026Q3 (R2-7). Later quarters are appended as rows with `frozen_set` = no.
8. **Cross-check (C10).** On every common week, DDP equals XML exactly for the four line-38 series.
9. **Revisions:** regenerated from all adjacent cached pairs (2.3).

## 4. Questions, fixed in advance (answers go to `summary.csv` and `quarter_ends.csv`)

**4.0 No test, so no MDE.** R3-1 removed every comparison between quarter-end and other weeks, and the placebo with it. Nothing here
is a test, so the MDE rules (C-090, C-092) bind nothing. The spec author's pre-sample figure (standard deviation of FRI NSA weekly changes,
2010-18, $40.3bn) stays in this spec as scale context and goes into no output.

**Named ordinary Wednesdays (R3-4).** Multi-year changes start and end on the Wednesday between the 8th and the 14th of February (or of
August), each at least 39 days from any quarter-end day. **For 2024-26: 2024-02-14, 2025-02-12, 2026-02-11 and 2026-08-12.** Q1's yearly
levels use 2019-02-13, 2020-02-12, 2021-02-10, 2022-02-09, 2023-02-08, 2024-02-14, 2025-02-12 and 2026-02-11. `Lo` (the latest ordinary
Wednesday) is the latest Wednesday at least 7 days from every quarter-end day that is not a break week; it is printed but never used
as a fixed endpoint. **README reason:** the weeks around quarter-ends swing, so an endpoint on such a week would put a quarter-end move
into a multi-year change.

**`blind`:** `no` on every Q1, Q2 and Q4 row (the spec author saw the endpoint levels), on the 2026Q3 rows of `quarter_ends.csv` (Table 11
showed 877.9, 855.7 and 836.9 for 23 Sep, 30 Sep and 7 Oct), and on Q6. `yes` on every other row.

- **Q1. Path since 2019, by segment.** For FRI NSA from 2019-01-02 to L, the segments start on 2019-01-02, 2019-10-02 and 2022-04-06 (DOM
  and ALL use their own break weeks). For each segment: the first and last level, the minimum and maximum with their dates, and the
  level on each named February Wednesday inside it; `pct_of_total_liabilities` on the same dates. The same for DOM.
- **Q2. Change over 2024-26.** For FRI, DOM and ALL (NSA): the changes 2024-02-14 → 2025-02-12, 2025-02-12 → 2026-02-11 and 2026-02-11 →
  2026-08-12. Each is given in $mn and as a share of the group's line 40 on the starting Wednesday, with the minimum and maximum inside
  the window and their dates. A window that crosses a break week is not computed; the row says `crosses_break` (none expected for
  2024-26). Also print `Lo`, and the level on it.
- **Q3. Quarter-ends (R3-1). Part A, observations:** the five quarter-ends in the frozen set whose last day is a Wednesday: **2020-09-30,
  2021-03-31, 2021-06-30, 2025-12-31 and 2026-09-30**. For each, FRI and DOM: the level, `delta_qe_wed` and `delta_next`, as single rows.
  There is **no average, count, test or "notable" flag**. The change ending 7 Oct 2026 is inside the frozen set, as 2026Q3's `delta_next`
  (R2-7). **Part B, descriptive table:** for the other 26 frozen quarters, the change containing the quarter-end day, with the other window
  beside it and `straddles_break` shown (2019Q3 and 2022Q1 straddle; C13). It is printed under the sentence "Wednesday levels cannot show a
  position that is not held at a Wednesday close". No statistic is taken across rows. Quarters after 2026Q3 are appended as rows only;
  the next Wednesday quarter-end is 2027-03-31.
- **Q4. Domestic beside foreign-related.** For the Q2 windows: the FRI change and the DOM change in separate rows, and the ALL = DOM + FRI
  identity row. No ratio between groups.
- **Q5.** Dropped (R3-7).
- **Q6. Revisions.** At each vintage pair: the number of cells changed, the largest absolute change ($mn) with its week, and whether any
  week more than 26 weeks old changed (`old_week_revised`, yes or no), with no flag.

## 5. Outputs

**Script `bin/h8_foreign_offices.py`.** Modes: `fetch`; `build` (offline and byte-identical on re-run); `selftest` (synthetic data, no
network, under 20 s). Committed files sit in `data/h8_foreign_offices/`. Each CSV begins with one `# source:` line naming the Board, the
H.8 release date, the retrieval date and the route.

**Header allowlist, canonical text.** One line per file, `<name>:<headers comma-joined, no spaces>`, each ending in LF (the last one too),
in this order. The script holds `SPEC_ALLOW_SHA256`. **`bin/check.sh` holds its own literal copy of these eight lines (R2-5)** and never
reads them from the script. G9 and M21 skip the `# source:` line and compare.

```
weekly.csv:week_wed,group,sa,series_id,usd_mn,change_usd_mn,total_liabilities_usd_mn,pct_of_total_liabilities,qe_quarter,qe_role,qe_offset_days,segment_start,note_flag,vintage
quarter_ends.csv:quarter,qe_date,qe_wed,offset_days,on_date,group,level_qe_wed_usd_mn,delta_qe_wed_usd_mn,delta_next_usd_mn,qe_day_in_window,straddles_break,frozen_set,blind,vintage
notes.csv:note_week,group,line38_effect_usd_mn,kind,paragraph_index,text_head
revisions.csv:vintage_prev,vintage_new,series_id,week_wed,usd_mn_prev,usd_mn_new,change_usd_mn
vintages.csv:vintage,route,xml_prepared,xml_last_modified,xml_sha256,ddp_status,latest_week,rows_fri_nsa
summary.csv:question,window,group,statistic,value,unit,blind
checks.csv:check_id,description,expected,observed,status
fetch_log.csv:utc_time,host,path_and_query,status,bytes,sha256
```

**sha256 of that text (817 bytes): `4ad6cc43d2befbae6df06998a362d818827b0f43cd6b30eed8d65868bf030d59`** (computed by the spec author;
superseded hash `f060ebf9b9d7372f0c5e2918a0398da4c50fdd0eced7916325efe0993a3080d7`). The hash is anchored here, outside the code. A builder
who needs a column changes this text and its hash first, logs it in Builder decisions, and tells the supervisor.

Allowed values: `group` ∈ {FRI, DOM, ALL}; `sa` ∈ {NSA, SA}, with SA only for FRI; `qe_role` ∈ {qe, after_qe, none}; `on_date`,
`qe_day_in_window`, `straddles_break`, `frozen_set` and `blind` ∈ {yes, no}; `route` ∈ {xml, ddp_fallback}; `kind` ∈ {note, footnote};
`unit` ∈ {usd_mn, pct, count, date, yes_no}. Money is in $mn to 1 decimal. `summary.csv` has no `notable` column (R3-1).

- **`README.md`** (generated, so G11 scans it), in this order, with every term defined at first use: NSA, Edge Act corporation, IBF,
  benchmark, Call Report, H.8.
  1. **Opening, two sentences (R3-5, R2-12):** "This table shows, at each Wednesday close, the net amount that US branches and agencies of
     foreign banks, with Edge Act and agreement corporations, owe to their own offices abroad and to related institutions in the US,
     from the Federal Reserve's H.8 release. The figure nets those positions and includes unremitted profits, capital and reserve
     accounts and, from April 2022, allowances for credit losses."
  2. Sentence 3, from section 0: "It records balances at Wednesday closes only; it does not show why they changed, and a change in a
     balance is not a measure of money moved."
  3. **The sign, with the trap:** positive = owed by the US offices; negative = owed to them. The domestically chartered line is negative
     and is not the foreign banks' line. The foreign banks' line itself was negative until 2011. Quote footnote 24 and give the 7 Oct 2026
     accounting example.
  4. **What the line contains** (FR 2644 item 9.a), then the one denial sentence: "These weekly changes are not flows of funds, and the
     table does not test window dressing or any other motive."
  5. **Breaks:** why paths are split (6 Apr 2022 and the Notes on Data weeks), and that no change or extreme is taken across one.
  6. **Endpoints:** the named February and August Wednesdays and the reason (section 4).
  7. **Quarter-ends:** the five Wednesday quarter-ends as single rows. Then the caveat sentence, "Wednesday levels cannot show a position
     that is not held at a Wednesday close". Then a note that the quarter-end day sometimes falls in the next week's change (R2-12). Then
     the descriptive table.
  8. Latest levels at L and the Q2 changes, in plain tables.
  9. Not seasonally adjusted, and why. Revisions and vintages: benchmarking, the 5 Aug 2026 example, and the DDP fallback.
  10. Column dictionary. Provenance last: the Board citation and public-domain statement, and the DDP retirement notice.
  The questions of section 4 do not appear in the README.
- **`SOURCES.md`:** each URL, its access date, the identifiers, the asserted attributes, the licence text, the quoted notes and footnotes,
  the FR 2644 page, and **Builder decisions** (every build choice and every post-registration fix with old and new values).

## 6. Leak and integrity rules

1. Committed: only the eight CSVs, README.md and SOURCES.md. No `.zip`, `.xml`, `.htm`, `.pdf`, no DDP package (a first line starting
   `"Series Description"`), no local path (`/Users/`, `/private/`, `~`), no `@`.
2. No file outside `data/h8_foreign_offices/` and the gitignored cache is written, apart from the `.gitignore` rule and the REPRODUCE.md
   paragraph (landing).

## 7. Selftests (synthetic only; each guard applies its own mutant, and an uncaught mutant fails the selftest)

**G11's literal patterns (R2-6), both compiled with `re.I`.** `CAUSAL_RX` is the hedged-yield pattern expanded and pasted, not imported:

```
\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b
```

`EXTRA_RX`:

```
\b(?:in|out)?flows?\b|window[- ]dressing|\b(?:head\s+offices?|parents?)\s+(?:fund|funds|funded|funding|push|pushes|pushed|pull|pulls|pulled|drain|drains|drained)\b|\b(?:dollar\s+)?(?:shortage|squeeze)\b
```

"due to" is not banned, because it is the series name.

| Guard | Protects | Mutant that must be caught |
|---|---|---|
| G1 group binding (the 19 Oct trap; R3-6) | 3.2, 3.4 | FRI and DOM line-38 columns swapped with labels kept (caught by the per-group identity); whole groups swapped, every column (caught by DOM line 40 > FRI line 40); `BG` read as FR for a DM series; selection by column index; **a binding check that FAILs on a negative FRI fixture** (it must WARN) |
| G2 sign identity | 3.4 | line 38 negated on read; taken from the asset side; lines 35 + 36 added to 34 (double count); a one-week 1 $mn breach not reported |
| G3 group identity | 3.4 | ALL built from DOM NSA + FRI SA; ALL ≠ DOM + FRI by 2 $mn accepted; a check of "FRI ≤ ALL" present (it is invalid, 2.2) |
| G4 NSA and exact suffix (R2-3) | 2.1 | any statistic computed from SA; selection by substring (`NFRD` matching `NFRDM`, or `B1100NFR` matching `NFRA`) |
| G5 units | 2.1 | multiplier ignored; values read as thousands; $bn written into a `_usd_mn` column |
| G6 quarter-ends (R3-1, R2-1) | 3.7 | the "last Wednesday on or before" rule; the "first on or after" rule; W(q)+7 marked `qe`; a non-Wednesday quarter-end given `on_date` = yes; `qe_day_in_window` = yes at a negative offset; an average, count or flag over quarters written anywhere; a post-2026Q3 row with `frozen_set` = yes. Fixture pins: the five on-date dates, and offsets 2026-06-30 → 2026-07-01 (+1), 2026-12-31 → 2026-12-30 (−1), 2024-03-31 → 2024-04-03 (+3) |
| G7 routes (R3-8) | 2.4, 3.8 | a 1 $mn XML/DDP difference passes; a DDP 404 aborts a build whose XML is fine; an XML 500 with a good DDP refuses to build (it must fall back with `route` = `ddp_fallback`); both routes failed yet a build is written (it must exit 2) |
| G8 vintages and revisions (R2-9) | 2.3 | **"build after two fetches"**: a `revisions.csv` built incrementally across two fetches differs from the one regenerated from all cached pairs; same `Prepared` date with a different zip sha256 accepted; previous vintage read from `weekly.csv`; an earlier latest week accepted; an XML-route vintage keyed by fetch date |
| G9 allowlists (R2-5) | 5 | an extra or renamed column; `SPEC_ALLOW_SHA256` ≠ sha256 of the canonical text; `# source:` compared as a header; an 11th file; **check.sh reading the header lines from the script** instead of holding its own copy |
| G10 leak guard | 6 | **on a planted bad folder** containing a raw `.zip`, a DDP package renamed `.csv` and a `/Users/` path in SOURCES, each must be reported. **On the clean folder it must pass** |
| G11 wording | R5 | the two patterns above, applied everywhere except the one denial sentence of 5.4. The opening and sentence 3 must pass; adding "because of quarter-end window dressing" must fail; a second sentence with "flows" must fail; "head offices funded the branches" must fail |
| G12 STOP latch (R2-10) | R3a | **AST scan**: a STOP path reached by `os.remove`, `os.unlink`, `os.replace`, `os.rename`, `shutil.rmtree`, `shutil.move`, `Path.unlink`, `Path.rename`, `Path.write_text`, `Path.write_bytes` or `open` in mode w, a or x. Pruning old zips by exact name is not flagged; **pruning by a glob over the cache root is flagged**. Runtime: with planted `STOP_xml` and `STOP_ddp`, `fetch` makes no request, exits 2, and both sha256 are unchanged. A fixture 500 on the XML writes `STOP_xml` with the five fields, and the build falls back to the DDP |
| G13 fetch safety | R1-R3 | a non-allowlisted host (`fred.stlouisfed.org`); `@` in the UA; a redirect followed; requests under 3 s apart; a 7th request; a retry after a 429 or 500 |
| G14 breaks and segments (R3-3) | 3.5 | a minimum, maximum or change taken across 2022-04-06 or 2019-10-02; the change ending at a break week placed in a segment; footnote 20 missing from the break list; a DOM note used as an FRI break |
| G15 notes parse (R2-2) | 3.6 | the sign of "-$3.0 billion" lost; **an undated paragraph dropped** (the 31 Mar 2010 FRI −12.0 lost); the group taken per entry, not per paragraph (the 6 Feb 2008 DOM paragraphs tagged FRI); the date-index line parsed as a note |
| G16 blind marks | 4 | a Q1, Q2, Q4, Q6 or 2026Q3 row marked `blind = yes` |
| G17 endpoints (R3-4) | 4 | an endpoint within 7 days of a quarter-end accepted; the first Wednesday of the year used; an endpoint on a break week; `Lo` used as a fixed endpoint |

## 8. Pinned checks (`checks.csv`)

**Pin rules.**
- **Recent pins** are weeks within 52 weeks of the vintage's latest week. They are FAIL on the 16 Oct 2026 vintage. On later vintages
  they are WARN, with the `revisions.csv` rows that explain them.
- **Stable pins** are older weeks (R2-8). They are WARN if `revisions.csv` has a row for that week in this vintage pair, and FAIL
  otherwise.
- All values in $mn, re-derived from the cached 16 Oct vintage.

- **C01 FRI NSA (B1100NFRD).** Stable: 2019-01-02 241,674.0; 2020-03-25 341,831.0; 2024-02-14 704,646.0; 2025-02-12 849,074.0; 2025-08-06
  954,274.0. Recent: 2026-02-11 809,580.0; 2026-08-05 839,732.0; 2026-08-12 798,035.0; 2026-09-30 855,694.0; 2026-10-07 836,860.0.
- **C02 DOM NSA (B1100NDMD).** Stable: 2004-06-02 209,549.0 (first week); 2019-01-02 −154,927.0; 2024-02-14 −360,685.0; 2025-02-12
  −400,102.0. Recent: 2026-02-11 −417,299.0; 2026-08-12 −466,101.0; 2026-09-30 −502,585.0; 2026-10-07 −483,558.0.
- **C03 ALL NSA (B1100NCBD).** 2024-02-14 343,961.0; 2025-02-12 448,972.0; 2026-02-11 392,281.0; 2026-08-12 331,934.0; 2026-09-30 353,109.0;
  2026-10-07 353,302.0. Each equals DOM + FRI.
- **C04 Sign identity** on every week for each group and basis, with the 7 Oct 2026 worked numbers in `observed`.
- **C05 FRI SA (B1100NFRA)** 2026-10-07 869,123.5 (context).
- **C06** Retired: the monthly series is no longer used. The monthly range 776.4 to 897.5 $bn is quoted in 2.2 only.
- **C07 Binding (R3-6), FAIL:** ALL = DOM + FRI on every week; DOM line 40 > FRI line 40 on every week (minimum ratio 4.0 at this vintage).
  **C07w, WARN:** FRI NSA < 0 on any week from 2019-01-02, listed by week (none expected; the last negative week was 2011-06-15).
- **C08 Coverage:** FRI first week 1973-01-03 (1,498.3); DOM and ALL first week 2004-06-02; all rows Wednesdays; no gaps; FRI rows ≥ 2,806.
- **C09 XML metadata:** the attributes of 2.1; `CL_CATEGORY` L = "Liabilities"; `CL_ITEM` 1100 = "(38) Net due to related foreign
  offices". On the DDP fallback: `N/A ddp_fallback`.
- **C10 Routes:** DDP = XML on every common week for the four line-38 series. `WARN ddp_unavailable` or `WARN xml_unavailable`
  when one route is missing.
- **C11 Notes (R2-2):** the five FRI notes of 2.2 with their signed amounts, including 31 Mar 2010 −12,000.0 from paragraph index 1; the
  seven DOM notes; footnote 20. A WARN when the notes page came from the cache (`STOP_notes`).
- **C12** Retired (R3-7).
- **C13 Quarter-end calendar:** 31 frozen quarters; `on_date` = yes for exactly 2020-09-30, 2021-03-31, 2021-06-30, 2025-12-31 and
  2026-09-30. W(2019Q3) = 2019-10-02 (+2): `delta_qe_wed` ends on the FRI note week, so it straddles a break. W(2022Q1) = 2022-03-30 (−1):
  `delta_next` ends on 2022-04-06 and straddles. W(2026Q3): `delta_next` ends 2026-10-07, inside the frozen set.
- **C14 Endpoints:** each named Wednesday of section 4 is a Wednesday, is at least 7 days from every quarter-end (observed minimum 39),
  and is not a break week.
- **C15 Fixed output:** a second `build` leaves every sha256 unchanged, `revisions.csv` included.

## 9. Success criteria

1. `python3 bin/h8_foreign_offices.py selftest` prints G1 to G17 with every mutant caught, and exits 0.
2. `fetch` makes at most 6 requests, all logged. If a STOP is written, the builder stops that source, tells the supervisor, and never
   deletes the file.
3. `build`: C01 to C05, C07 to C11 and C13 to C15 PASS. **Acceptable WARNs:** recent pins on a later vintage, with their revision rows;
   stable pins with a revision row; C07w; C10 `ddp_unavailable` or `xml_unavailable`; C11 from cache. Every other WARN goes to the
   supervisor. Every question has `summary.csv` rows with `blind` filled.
4. **A verifier re-derives by hand** from the cached subset: FRI NSA on 2026-10-07 = 3,642,173 − 1,612,007 − 981,596 − 211,710 = 836,860
   $mn (or the same vintage's revised components).
5. `bin/check.sh --all`: the existing ✓ lines plus warn-only **M21**, with its own copy of the canonical header lines (R2-5). M21 checks:
   - the ten names, the headers (skipping `# source:`), and no raw file, local path or `@`;
   - no G11 pattern outside the denial sentence;
   - binding on the latest week in `weekly.csv`: FRI + DOM = ALL, and FRI `total_liabilities_usd_mn` < DOM's (✗ if not);
   - a negative FRI level is ⚠, never ✗ (R3-6).
   On a scratch copy with a planted `.zip`, a renamed header and the DOM rows relabelled FRI, M21 prints three ✗ lines; on the clean
   folder it prints ✓. It is shown failing on the planted copy before it lands.
6. **README cold-reader test (R2-12).** Two fresh agents read only the README: a non-specialist and a bank-funding practitioner.
   - **Pass** only if each can state the population, the sign, that levels are Wednesday closes, and that the line includes non-lending
     items.
   - **Fail** if either believes the line measures money moved, that head offices "fund" branches as a finding, that quarter-end changes
     are window dressing, or that the negative domestic line belongs to foreign banks.

**Landing (builder):** the `.gitignore` rule for `data/vintages/h8_foreign_offices/`; a REPRODUCE.md paragraph; one proposed CALENDAR row,
given as text and not edited in: weekly, each Friday after 4:15 p.m. ET, run `fetch` and `build` and read `revisions.csv`. There is no
forecast row (R3-2). Also a HANDOVER row. The builder commits nothing; the supervisor verifies and writes any findings text.

## 10. OPEN questions

- **O-1 RULED:** the XML is primary, and the DDP is cross-check and fallback (first ruling, R3-8).
- **O-2, O-3, O-6 RULED:** no Table 11 scrape, no pre-2004 file, no split by offset.
- **O-7 CLOSED by R3-2:** the year-end check is dropped, because 31 Dec 2026 is a Thursday and no H.8 Wednesday observes it.
- **O-4 OPEN: the size of the April 2022 allowance move.** Footnote 20 gives none. FRI paths are split there (R3-3), so the size affects no
  number here, only what a reader can compare across the split.
- **O-5 OPEN: benchmark dates.** No machine-readable list was found; Q6 detects them from revisions after the fact.
- **O-8 OPEN: related US offices.** FR 2644 item 9.a includes related US depository institutions. Whether positions between two FRIs of
  one parent cancel in the aggregate is not stated by H.8.
- **O-9 OPEN: the fallback vintage key.** A DDP-fallback vintage has no `Prepared` date, so it is keyed `fetch-<utc-date>`. A later XML
  vintage of the same release will compare against it as a separate vintage, which may produce zero-change pairs. The supervisor
  should confirm that this is acceptable.
- **O-10 OPEN: review texts not in the spec author's context.** R2-4 refers to "M21 sign test as the reviewer wrote it", and R2-12 to
  "smaller points as listed". The spec author had only the ruling summaries. 9.5 and 2.2 are its rendering, binding by identity per
  R3-6, which supersedes any sign test as a FAIL. The supervisor should check them against the review.
- **O-11 OPEN: when both routes fail.** After the DDP's retirement, an XML 500 leaves no route and the build stops (exit 2). That is
  intended (no FRED), but the weekly CALENDAR row will then show gaps.

## Supervisor rulings, 23 Oct 2026 (before any data run)

- **O-1:** the release-page XML file is primary; the DDP packages are a cross-check while they last (a missing package is a WARN).
- **O-2 / O-3 / O-6:** no Table 11 scrape, no pre-2004 file, no split by days-from-quarter-end (it would multiply comparisons after the fact).
- **O-7:** the year-end 2026 row is kept, labelled a one-week forecast check, not a test.
- **Guard number:** **M21**.
## Supervisor rulings, round 2 (second review), 23 Oct 2026 — before any data run

All twelve fixes are accepted:
- **R2-1 Quarter-end window.** `delta_qe_wed` = L(W) − L(W−7) and `delta_next` = L(W+7) − L(W), plus `qe_day_in_window` (yes when the Wednesday is on or after the quarter-end). The window that contains the quarter-end day is the change ending at W if the offset is ≥ 0, else the change ending at W+7. Q3's means, counts, S and T use that window, and the other window is printed beside it. The year-end check is "the change ending Wednesday 6 Jan 2027, which contains 31 Dec 2026", scored on the 15 Jan 2027 release; CALENDAR row 2027-01-15. The placebo is drawn from non-quarter-end weeks and the README says quarter-end weeks are noisier (standard deviation of weekly changes about 48 against 36 $bn), so it understates the noise at the dates tested.
- **R2-2** Notes parse: undated paragraphs belong to the preceding dated entry; the five FRI notes are listed and pinned in C11; mutant "undated paragraph dropped".
- **R2-3** NSA/SA by exact suffix, with the substring mutant.
- **R2-4** M21 sign test as the reviewer wrote it; the FRI-versus-ALL limit is stated.
- **R2-5** check.sh holds its own copy of the header lines.
- **R2-6** The literal expanded causal pattern is pasted into the spec.
- **R2-7** Q3 uses a frozen set of 31 quarters; later quarters are added to `quarter_ends.csv` but never enter the frozen statistics; say whether the change ending 7 Oct 2026 is inside.
- **R2-8** Stable-pin rule: WARN if `revisions.csv` has a row for that week in this vintage, else FAIL.
- **R2-9** `revisions.csv` regenerated deterministically from all adjacent cached pairs; same `Prepared` date with a different sha256 is a FAIL; mutant "build after two fetches".
- **R2-10** AST scan on STOP paths with the extra write calls; zip pruning not flagged; mutant "pruning by glob over the cache root".
- **R2-11** Q5 part-window defined; blank months skipped to the next `ok` month; the 14 Oct 2024 start noted.
- **R2-12** Smaller points as listed; the monthly-average range is 776.4 to 897.5 $bn; README opening split into two sentences; jargon defined at first use; cold-reader test gains the positive criteria; the README says the quarter-end day sometimes falls in the next week's change.
## Supervisor rulings, round 3 (Grok attack, g10), 23 Oct 2026 — before any data run

Grok's level checks hold (7 Oct 2026: foreign-related 836.9, domestic −483.6, all banks 353.3 $bn, adding up; line 38 = total liabilities less lines 34, 37, 39). Where Grok and the second review differ, Grok's point is stronger and is taken:
- **R3-1 Quarter-ends (supersedes R2-1's averages).** H.8 levels are Wednesday close only, so a position held on a quarter-end date and gone by the next Wednesday never appears in any level. Q3 therefore lists, as individual observations with no average and no "notable" flag, only the quarter-ends that are themselves Wednesdays (2019Q1–2026Q3: 30 Sep 2020, 31 Mar 2021, 30 Jun 2021, 31 Dec 2025, 30 Sep 2026), with the change into and out of each. The change containing every other quarter-end day (R2-1's window) is printed as a descriptive table, under the sentence "Wednesday levels cannot show a position that is not held at a Wednesday close". The placebo minimum-detectable-difference and the counts of negative quarters are dropped.
- **R3-2 The year-end forecast check is dropped.** 31 Dec 2026 is a Thursday, so no H.8 Wednesday observes it. No CALENDAR row.
- **R3-3 Breaks.** Every path and multi-year change is split at 6 Apr 2022 (allowances moved into line 38, footnote 20; size unpublished) and at each Notes-on-Data week that names the line (including 2 Oct 2019, −$3.0bn, and the five listed in R2-2). No minimum or maximum is taken across a break.
- **R3-4 Endpoints.** Multi-year changes use ordinary Wednesdays at least 7 days from any quarter-end; the spec author names them (for 2024–26, a Wednesday in mid-January or mid-February of each year) and the README says why.
- **R3-5 Opening sentence** rewritten to name the population (US branches and agencies of foreign banks plus Edge Act and agreement corporations) and to say the line nets positions with the bank's own offices abroad and related US institutions, and includes unremitted profits, capital and reserve accounts and, from April 2022, allowances.
- **R3-6** A negative foreign-related value is a WARN, not a FAIL (the About page allows negative levels); group binding is checked by the identities, not by sign.
- **R3-7 The swap-tape comparison (Q5, `beside_basis.csv`) is dropped**: a monthly day-weighted average beside a basis median invites the reading the spec forbids, and the monthly figure borrows the next month's first Wednesday.
- **R3-8** The XML zip returned HTTP 500 to Grok's fetcher on 23 Oct (the second reviewer got HTTP 200, 8,438,469 bytes, the same day); the build treats a non-200 as a latch, and the DDP package is the fallback while it lasts.

## Supervisor rulings, round 4 (spec author's open items), 23 Oct 2026 — before any data run

- **O-9:** fallback vintages are keyed by fetch date, as written.
- **O-10:** the author's M21 rendering (binding by identities, R3-6) is accepted.
- **O-11:** once the packages are retired, a failed XML fetch writes STOP and the build stops; the supervisor decides. No third route is added.
