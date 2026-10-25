# Sources

## Federal Reserve Board, H.8 release: XML file (primary source)

- URL: `https://www.federalreserve.gov/releases/h8/data/FRB_h8_xml.zip`, fetched by `bin/h8_foreign_offices.py fetch`. The zip holds `H8_data.xml` (SDMX-ML compact), `H8_struct.xml` and two schema files; the script streams `H8_data.xml` with `iterparse` and never reads it with a regular expression. Vintages so far, with the time each was retrieved (UTC) and the XML `Prepared` timestamp: 2026-10-16 (xml, retrieved 2026-10-23T12:05:34Z, prepared 2026-10-16T10:00:00); 2026-10-23 (xml, retrieved 2026-10-25T14:02:58Z, prepared 2026-10-23T10:00:00).
- Series: matched on the whole `SERIES_NAME`, never on a substring or a column position (`NFRD` is weekly NSA, `NFRDM` monthly NSA, `NFRA` weekly SA). The script asserts, for each of the 20 series: `BG`, `SA`, `CATEGORY` = `L`, `ITEM`, `FREQ` = `19`, `UNIT_MULT` = `1000000`. `CL_CATEGORY` L is "Liabilities" and `CL_ITEM` 1100 is "(38) Net due to related foreign offices".

| series | group | basis | BG | ITEM | line |
|---|---|---|---|---|---|
| `B1100NFRD` | FRI | NSA | FR | 1100 | (38) Net due to related foreign offices |
| `B1152NFRD` | FRI | NSA | FR | 1152 | (40) Total liabilities |
| `B1058NFRD` | FRI | NSA | FR | 1058 | (34) Deposits |
| `B3094NFRD` | FRI | NSA | FR | 3094 | (37) Borrowings |
| `B3095NFRD` | FRI | NSA | FR | 3095 | (39) Other liabilities including trading liabilities |
| `B1100NDMD` | DOM | NSA | DM | 1100 | (38) Net due to related foreign offices |
| `B1152NDMD` | DOM | NSA | DM | 1152 | (40) Total liabilities |
| `B1058NDMD` | DOM | NSA | DM | 1058 | (34) Deposits |
| `B3094NDMD` | DOM | NSA | DM | 3094 | (37) Borrowings |
| `B3095NDMD` | DOM | NSA | DM | 3095 | (39) Other liabilities including trading liabilities |
| `B1100NCBD` | ALL | NSA | CB | 1100 | (38) Net due to related foreign offices |
| `B1152NCBD` | ALL | NSA | CB | 1152 | (40) Total liabilities |
| `B1058NCBD` | ALL | NSA | CB | 1058 | (34) Deposits |
| `B3094NCBD` | ALL | NSA | CB | 3094 | (37) Borrowings |
| `B3095NCBD` | ALL | NSA | CB | 3095 | (39) Other liabilities including trading liabilities |
| `B1100NFRA` | FRI | SA | FR | 1100 | (38) Net due to related foreign offices |
| `B1152NFRA` | FRI | SA | FR | 1152 | (40) Total liabilities |
| `B1058NFRA` | FRI | SA | FR | 1058 | (34) Deposits |
| `B3094NFRA` | FRI | SA | FR | 3094 | (37) Borrowings |
| `B3095NFRA` | FRI | SA | FR | 3095 | (39) Other liabilities including trading liabilities |

- Units: millions of US dollars (`UNIT_MULT` 1000000; DDP `Multiplier:` 1000000). Weekly levels are Wednesday close-of-business values.
- Breaks and notes: footnote 20 of the release ("Beginning April 6, 2022, foreign-related institutions no longer report the allowance for loan and lease losses separately (currently, the allowance for credit losses on loans and leases). Any such allowances are included in net due to related foreign offices (line 38).") and footnote 24 ("Excludes the due-from position with related foreign offices which is included in line 38."). The Board's About page says the seasonally adjusted foreign-related data "derived as residuals" from other groups.
- Licence: the Board's website policy (https://www.federalreserve.gov/disclaimer.htm, read by hand on 23 Oct 2026): "Unless otherwise indicated, information on Board's website is in the public domain and may be copied and distributed without permission. Please cite to the Board as the source of the information." Derived tables are committed with that citation; raw files stay in the git-ignored cache for size.

## Data Download Program (DDP) packages: cross-check and fallback

- URL pattern: `https://www.federalreserve.gov/datadownload/Output.aspx?rel=H8&series=<package>&lastobs=&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package`; packages fri_nsa `0e569516edadaa66168c115e5016ff16`, dom_nsa `18461c27aa45d43aa804016497d92ece`, all_nsa `c8dfa96ef1d2db40ce57121ffdddf59d`, fri_sa `53b903ce661b8534202a6d5e36db960d`.
- The script selects on the `Unique Identifier:` row (`H8/H8/<series>`) and asserts that the series description names the group and the basis and that `Multiplier:` is 1000000. The Board's Data Download Program is being retired (notice of 16 Jul 2026; the "Build Your Package" feature is to go in the week of 9 Nov 2026); a package that fails leaves the XML route untouched, and C10 is then WARN.

## Notes on Data

- URL: `https://www.federalreserve.gov/releases/h8/h8notes.htm`, newest cached copy retrieved 2026-10-25. The leading index of dates is not an entry; an undated paragraph belongs to the dated entry before it; the group is read per paragraph.

Quoted clauses that carry the amounts (the Board's text, in the stated paragraph):

- 2004-12-29, DOM, paragraph 0: "net due to related foreign offices, $2.0 billion" (2000.0 usd_mn)
- 2006-10-04, DOM, paragraph 0: "net due to related foreign offices, -$10.0 billion" (-10000.0 usd_mn)
- 2007-03-07, DOM, paragraph 0: "net due to related foreign offices, -$3.2 billion" (-3200.0 usd_mn)
- 2008-02-06, FRI, paragraph 0: "net due to related foreign offices, $12.0 billion" (12000.0 usd_mn)
- 2008-04-02, FRI, paragraph 0: "net due to related foreign offices, -$18.6 billion" (-18600.0 usd_mn)
- 2008-08-20, DOM, paragraph 0: "net due to related foreign offices, -$8.6 billion" (-8600.0 usd_mn)
- 2010-03-31, FRI, paragraph 1: "net due to related foreign offices, -$12.0 billion" (-12000.0 usd_mn)
- 2011-01-05, DOM, paragraph 0: "net due to related foreign offices, $5.7 billion" (5700.0 usd_mn)
- 2016-03-02, DOM, paragraph 0: "net due to related foreign offices, -$3.1 billion" (-3100.0 usd_mn)
- 2017-11-29, FRI, paragraph 0: "net due to related foreign offices, $5.2 billion" (5200.0 usd_mn)
- 2018-04-04, DOM, paragraph 0: "net due to related foreign offices, $2.0 billion" (2000.0 usd_mn)
- 2019-10-02, FRI, paragraph 0: "net due to related foreign offices, -$3.0 billion" (-3000.0 usd_mn)

## Other pages read by hand (not fetched by the script)

- Read on 23 Oct 2026 between 12:02 and 12:10 UTC by the spec author with the CLAUDE.md User-Agent and one request per URL (16 requests, all HTTP 200), under `https://www.federalreserve.gov`: `/releases/h8/current/default.htm` (current release, footnotes 1, 20 and 24), `/releases/h8/about.htm`, `/releases/h8/h8_technical_qa.html`, `/releases/h8/default.htm`, `/datadownload/Choose.aspx?rel=H8`, `/data/data-download-fred-information.htm` (the DDP notice), `/disclaimer.htm` (the website policy), `/apps/reportingforms/Report/Index/FR_2644` and the FR 2644 instructions PDF (`/apps/reportingforms/Download/DownloadAttachment?guid=386cbedb-80c8-4cce-a618-a7f3e943b747`, footer "April 2024", item 9.a on page LI-7).
- FR 2644 instructions, item 9.a: the positions reported "should include unremitted profits, any statutory or regulatory capital requirement, any reserve accounts, and any allowance for credit losses"; a net due-from position is reported in item 5.a and a net due-to position in item 9.a.

## Builder decisions

- Seeding. The cache was seeded with the spec author's raw copies of the 16 Oct 2026 vintage (zip sha256 2ce2d425...222b and the four DDP weekly packages, hashes checked first), as the spec allows. They were put through the same ingest code as a fetch (`ingest_xml`), and the vintage is keyed 2026-10-16. Those requests were made by the spec author on 23 Oct 2026 and are not in `fetch_log.csv`.
- Changes that end on a break week. The spec defines `change_usd_mn` as the level minus the previous Wednesday's level, says no change is ever taken across a segment boundary (R3-3), and C13 words 2019Q3 and 2022Q1 as straddling. The supervisor ruled that R3-3 outranks C13's wording: the change ending on a break week is left blank in `weekly.csv` (with `note_flag`) and, in `quarter_ends.csv`, FRI 2019Q3 `delta_qe_wed` (ends on the 2 Oct 2019 note week) and FRI 2022Q1 `delta_next` (ends on 6 Apr 2022) are blank, with `straddles_break` = yes kept.
- Notes before the ledger. The page also names the line for domestically chartered banks on 21 Apr 2004; that week is before the first ledger week (2004-06-02) and is left out of `notes.csv`, so the seven DOM notes are the ones of spec 2.2.
- `text_head` in `notes.csv` is the item clause of the Board's paragraph that carries the amount ("net due to related foreign offices" and the signed amount), not the start of the paragraph: the Board's opening and reason clauses use words that the wording guard (R5) bans in this folder.
- Group of a note paragraph: whichever of the three group phrases (foreign-related institutions, domestically chartered commercial banks, all commercial banks) comes first in the paragraph. A paragraph that names the line and no group stops the build.
- Pins. Mismatches of a pinned week are WARN only when `revisions.csv` has a row for that series and week in some pair of cached vintages; a mismatch without such a row is FAIL, for recent and stable weeks alike. On the pin vintage 2026-10-16 every mismatch is FAIL. The 52-week rule only decides the label recent or stable in the text of the check.
- Q1 covers FRI and DOM, as the spec's closing sentence says ("the same for DOM"); the opening parenthesis also mentions ALL, and no ALL rows were added.
- Q6 is computed per group (FRI, DOM, ALL) over the NSA line-38 series, and a week counts as old when it is more than 26 weeks before the newer vintage's latest week.
- Q3 rows in `summary.csv` repeat the five Wednesday quarter-ends of `quarter_ends.csv`, one row per statistic; no statistic is taken across quarters.
- C15 compares two renderings made in one run; the on-disk comparison is a second `build` run, which leaves every sha256 unchanged. C16 and C17 are extra checks (folder guards on the rendering; the vintage ledger). The retired checks C06 and C12 are not rows.
- The STOP scan (G12) allows one creator, `create_stop`, which opens the file with mode "x" (exclusive create) because a latch has to be created; it flags every other call that reaches a STOP path, every removal outside `prune_old_zips`, and a removal in a function that lists or globs a directory.
- Stop rules at build: no cached vintage, or STOP_xml together with STOP_ddp, or STOP_xml present with a newest vintage that is not a DDP fallback, ends the build with exit 2 and no file written.
- The README defines H.8 in its title line and glosses the other terms in a "Terms" paragraph after the two required opening sentences and sentence 3, because those sentences are fixed text that already use H.8 and Edge Act.
- The mutant for "lines 35 + 36 added to 34" adds line 34 a second time, because lines 35 and 36 are not among the 20 series and are already inside line 34.
- A vintage is ordered by the date in its key (an XML vintage before a DDP fallback vintage of the same date). A cell that is in an older vintage and missing from the next is listed in `revisions.csv` with blank new value and change.
- `fetch` makes no request at all, and exits 2, when STOP_xml and STOP_ddp are both present at the start (no route is left; the notes page is not fetched either). With STOP_xml alone it goes on with the DDP and the notes page. It exits 0 when the XML vintage was saved or a DDP fallback vintage was made, and 2 otherwise; a socket fault exits 4 and latches nothing.
- The reader accepts a gzip-encoded reply (the request asks for identity encoding) so that a server that compresses anyway does not trip a content test.
- Lo is computed against the union of the break weeks of FRI, DOM and ALL. The Q2 and Q4 windows test a break against the group's own break weeks. Q4 prints, per window, the FRI and DOM changes and the gap ALL change - DOM change - FRI change.
- The XML content test asserts BG, SA, CATEGORY, ITEM, FREQ and UNIT_MULT on each of the 20 series (spec 2.1 and R3b); it does not assert the series descriptions, which only the DDP test reads (spec 3.2).
- First fetch by this script: 23 Oct 2026, 13:16:31 to 13:16:47 UTC, six requests (the XML zip, the four DDP packages, the notes page), all HTTP 200, no STOP file. The zip has the same sha256 as the seeded copy (Prepared 2026-10-16T10:00:00), so no new vintage was made, `revisions.csv` holds no row and the vintage stays 2026-10-16. The next H.8 release was due at 4:15 p.m. Eastern (20:15 UTC) that day, after this fetch; a later `fetch` brings the 23 Oct vintage.
- DDP hash slip in the spec: the spec quotes the hash of the ALL package as 6bbba727 ... a8559. The seeded and the fetched file are byte-identical and both are 6bbba7279a4bc51c...ad8559, so the first eight characters agree and the tail differs by one character; this is read as a typing slip in the spec, and C10 shows the package equals the XML on all 7,946 common weeks of the 16 Oct vintage.
- Post-registration fix after the first build on real data (23 Oct 2026): `text_head` in `notes.csv` changed from a window of up to 120 characters ending at the amount (starting after the first clause boundary) to the item clause only. One reason: the window cut some clauses in the middle (an unbalanced parenthesis, a leading "and"). No amount, group, week or paragraph index changed. The old values were not kept on disk; they were rebuilt by running the old rule on the cached notes page and agree with the first build's printed output. All 12 old and new values:
  - 2019-10-02 FRI paragraph 0: old "borrowings, -$1.6 billion; net due to related foreign offices, -$3.0 billion"; new "net due to related foreign offices, -$3.0 billion"
  - 2018-04-04 DOM paragraph 0: old "deposits, other deposits, $45.5 billion; borrowings, -$1.6 billion; net due to related foreign offices, $2.0 billion"; new "net due to related foreign offices, $2.0 billion"
  - 2017-11-29 FRI paragraph 0: old "borrowings, $23.3 billion (borrowings from others, $23.3 billion); net due to related foreign offices, $5.2 billion"; new "net due to related foreign offices, $5.2 billion"
  - 2016-03-02 DOM paragraph 0: old "borrowings, $4.5 billion (borrowings from others, $4.1 billion); net due to related foreign offices, -$3.1 billion"; new "net due to related foreign offices, -$3.1 billion"
  - 2011-01-05 DOM paragraph 0: old "borrowings, $3.0 billion (borrowings from others, $3.0 billion); net due to related foreign offices, $5.7 billion"; new "net due to related foreign offices, $5.7 billion"
  - 2010-03-31 FRI paragraph 1: old "borrowings, $21.0 billion (borrowings from others, $21.0 billion); net due to related foreign offices, -$12.0 billion"; new "net due to related foreign offices, -$12.0 billion"
  - 2008-08-20 DOM paragraph 0: old "The major liability items affected were the following: net due to related foreign offices, -$8.6 billion"; new "net due to related foreign offices, -$8.6 billion"
  - 2008-04-02 FRI paragraph 0: old "and net due to related foreign offices, -$18.6 billion"; new "net due to related foreign offices, -$18.6 billion"
  - 2008-02-06 FRI paragraph 0: old "The major liability item affected was the following: net due to related foreign offices, $12.0 billion"; new "net due to related foreign offices, $12.0 billion"
  - 2007-03-07 DOM paragraph 0: old "borrowings from others, -$0.7 billion); net due to related foreign offices, -$3.2 billion"; new "net due to related foreign offices, -$3.2 billion"
  - 2006-10-04 DOM paragraph 0: old "borrowings, $21.5 billion (borrowings from others, $21.5 billion); net due to related foreign offices, -$10.0 billion"; new "net due to related foreign offices, -$10.0 billion"
  - 2004-12-29 DOM paragraph 0: old "The major liability item affected was the following: net due to related foreign offices, $2.0 billion"; new "net due to related foreign offices, $2.0 billion"
- In the identity check the tolerance is 0.5 usd_mn on every table. FRI seasonally adjusted values carry half-units, and 1,089 of its weeks show a rounding gap of 0.1 or 0.2 usd_mn; the NSA tables show none.
