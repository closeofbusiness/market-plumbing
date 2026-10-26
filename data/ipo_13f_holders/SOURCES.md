# Sources and method: 13F holders of the 2026 IPOs

Specification: `_research/2026-10-26-IPO-13F-Holders-Spec.md` (committed at 7306996, with its supervisor rulings, rounds 1 to 5; where rounds differ the latest round is applied). Script: `bin/ipo_13f_holders.py`. Vintage `13f_to_2026-08-31`. Guard: `bin/check.sh` M24.

## Disclosure of what was seen before the build

Observed means seen by the spec author on 26 Oct 2026 between 05:43 and 05:46 UTC with the non-SEC User-Agent, one request per URL, no redirect followed; no sec.gov or data.sec.gov host was contacted by the spec author. Seen of the answer before any build: eleven hand-read 13F rows in `data/i2_ipo_allocation/i2_13F_sample_holdings.csv`; i2's 13G/13D rows; and, in the rulings, the SpaceX listed-class count at the first 10-Q (about 7.70bn) and third-party aggregate 13F sums for SPCX and CBRS at 30 Jun 2026. SPCX is therefore not blind. The builder computed nothing before the selftest passed.

## Requests

The builder made none. The supervisor fetched the files on 26 Oct 2026 and copied them into the gitignored cache; the supervisor's fetch log holds each status and is not in this repository. The URLs the spec lists (2.6):

- https://www.sec.gov/files/datastandardsinnovation/data/form-13f-data-sets/01jun2026-31aug2026_form13f.zip
- https://www.sec.gov/files/structureddata/data/form-13f-data-sets/01mar2026-31may2026_form13f.zip
- https://www.sec.gov/files/form_13f_readme.pdf
- the five 424B4s and the five first 10-Qs for the period ended 30 Jun 2026 from the EDGAR filing index (SPCX, CBRS, QNT, FRVO, INIO)
- the SEC Official List of Section 13(f) Securities for the quarter ended 30 Jun 2026 (the first-quarter list was also supplied)

The spec author's own requests (2.7): `catalog.data.gov/dataset/form-13f-data-sets` 200 (281,068 bytes); `www.cusip.com` `/terms-of-use.html`, `/about/license-fees.html`, `/robots.txt` each 303 to `/index.html` (not followed); `/index.html` 200 (94,800); `/services/license-fees.html` 200 (111,955); `experience.cusip.com/license-fees-faq` 200 (924 bytes, a shell).

## The 13F readme as read (R11)

- `VALUE`: Market value. Starting on January 3, 2023, market value is reported rounded to the nearest dollar. Previously, market value was reported in thousands. -> whole US dollars; never rescaled.
- `SECFILENUMBER`: "SEC File Number (if applicable)", a separate field from `FORM13FFILENUMBER` ("FORM 13F file number") -> reg_category.csv is produced (round 5, R3-6). The prefix meanings 801-, 802-, 8- are relayed, not defined by the readme.
- `AMENDMENTTYPE`: "Amendment type is a restatement or adds new holdings"; values found in the data: RESTATEMENT, NEW HOLDINGS (an unknown value is a FAIL listing all).
- Dates: DD-MON-YYYY; submission types listed: 13F-HR, 13F-HR/A, 13F-NT, 13F-NT/A.

## Deal patterns (literal, case-insensitive)

| Ticker | Pattern |
|---|---|
| SPCX | `SPACE\s*EXPLORATION|SPACEX` |
| CBRS | `CEREBRAS` |
| QNT | `QUANTINUUM` |
| FRVO | `FERVO` |
| INIO | `INNIO` |
| SKHY | `SK\s*HYNIX` |
| JMKE | `JERSEY\s*MIKE` |
| BSP | `BENDING\s*SPOONS` |

## Gates and reviews

- CUSIP_MAP_SHA256: match
- FILER_REVIEW_SHA256: match
- DEAL_INPUTS_SHA256: match
- cache stamp: match
- `CUSIP_MAP_SHA256 = d939fb8ec9cd919bd16377c2620e68495b6416656e6cd9b7c9953af288b01714`: the identifier map, reviewed and set by the supervisor on 26 Oct 2026 (stage 2); the cache's scans are stamped with it.
- `FILER_REVIEW_SHA256 = d2c369334679d441792dd4b148c70cad68b37ec175cef5696e17d0bcf6828f70`: the filer table (public names, kinds, pre-listing flags, 13D/13G and cornerstone matches), reviewed and accepted by the supervisor on 26 Oct 2026.
- `DEAL_INPUTS_SHA256 = d1b2471102068e62f59aeb697352463b03fee9265840e07fb8d645f3a027ffc8`: the transcribed `deal_inputs.csv`, checked and set by the supervisor on 26 Oct 2026 (stage 2), with the first trading days and the three September-quarter pricing dates entered from the supervisor's reply.
- Header allowlist: `SPEC_ALLOW_SHA256 = ee8cb56e1611e5586421bc59d7b2a87766937889bfb386d862f89a69323c8b65` (also held in `bin/check.sh`).

## Licence

SEC catalogue licence `https://www.usa.gov/government-copyright` (observed). CUSIP Global Services' licence-fee FAQ (observed, `https://www.cusip.com/services/license-fees.html`) allows collecting its data from public sources for "non-commercial use, provided that the source of such information permitted the reproduction and use of such information". The repository's CC BY 4.0 would let others reuse a committed CUSIP commercially, hence none is committed (R4, O-1). The reference figures of C19 are a third party's published aggregates used as two expected values only.

## Pricing and first trading dates against the deal master

| Ticker | Pricing date (prospectus) | First trading day (supervisor) | First quarter-end | Deal master ipo_date |
|---|---|---|---|---|
| SPCX | 2026-06-11 | 2026-06-12 | 2026-06-30 | same |
| CBRS | 2026-05-13 | 2026-05-14 | 2026-06-30 | same |
| QNT | 2026-06-03 | 2026-06-04 | 2026-06-30 | master 2026-06-04 |
| FRVO | 2026-05-12 | 2026-05-13 | 2026-06-30 | master 2026-05-13 |
| INIO | 2026-06-03 | 2026-06-04 | 2026-06-30 | same |
| BSP | 2026-06-30 | 2026-07-01 | 2026-09-30 | same |
| SKHY | 2026-07-09 | 2026-07-10 | 2026-09-30 | same |
| JMKE | 2026-07-29 | 2026-07-30 | 2026-09-30 | master 2026-07-31 |

## Pinned checks and the lists behind the acceptable warnings

- C01a PASS: expected 111941660492 usd over 8 deals; observed 111941660492 usd over 8 deals.
- C01b PASS: expected 84119999925 usd; 75.146 pct of 111941660492; observed 84119999925 usd; 75.146 pct of 111941660492; deals CBRS,FRVO,INIO,QNT,SPCX.
- C01c PASS: expected 9120000000 usd; 24.688 pct of 36941660567; observed 9120000000 usd; 24.688 pct of 36941660567.
- C01d PASS: expected {"all": {"CBRS": "6.598", "FRVO": "2.247", "INIO": "0.000", "QNT": "1.997", "SPCX": "89.158"}, "ex_spcx": {"CBRS": "60.855", "FRVO": "20.724", "INIO": "0.000", "QNT": "18.421"}}; observed {"all": {"CBRS": "6.598", "FRVO": "2.247", "INIO": "0.000", "QNT": "1.997", "SPCX": "89.158"}, "ex_spcx": {"CBRS": "60.855", "FRVO": "20.724", "INIO": "0.000", "QNT": "18.421"}}.
- C02-r1 PASS: expected shares 171826745, VALUE 29358317651; observed shares 171826745, VALUE 29358317651, puts 0, put VALUE 0, calls 0.
- C02-r2 PASS: expected shares 120801820, VALUE 20640198965; observed shares 120801820, VALUE 20640198965, puts 0, put VALUE 0, calls 0.
- C02-r3 PASS: expected shares 7011028; observed shares 7011028, VALUE 1549437188, puts 0, put VALUE 0, calls 0.
- C02-r4 PASS: expected shares 0, puts 145700, put VALUE 16340805; observed shares 0, VALUE 0, puts 145700, put VALUE 16340805, calls 0.
- C02-r5 PASS: expected shares 3110086, VALUE 687329006, calls 700000; observed shares 3110086, VALUE 687329006, puts 0, put VALUE 0, calls 700000.
- C02-r6 PASS: expected shares 794467, VALUE 175577207; observed shares 794467, VALUE 175577207, puts 0, put VALUE 0, calls 0.
- C02-r8 PASS: expected shares 150000; observed shares 150000, VALUE 12261000, puts 0, put VALUE 0, calls 0.
- C02-r9 PASS: expected shares 20000, VALUE 584600; observed shares 20000, VALUE 584600, puts 0, put VALUE 0, calls 0.
- C03a PASS: expected 170.86; observed 170.86.
- C03b PASS: expected all five within bounds; observed SPCX 1.266 x; CBRS 1.195 x; QNT 1.362 x; FRVO 1.083 x; INIO 1.465 x.
- C03c WARN: expected listed; observed SPCX 134 of 1744 filers, CBRS 36 of 412 filers, QNT 13 of 174 filers, FRVO 14 of 183 filers, INIO 9 of 148 filers.
- C04 WARN: expected listed; observed CBRS 1 rows / 1 filers / 1040 shares, FRVO 0 rows / 0 filers / 0 shares, INIO 0 rows / 0 filers / 0 shares, QNT 0 rows / 0 filers / 0 shares, SPCX 1 rows / 1 filers / 4082 shares.
- C05a WARN: expected listed; observed CBRS 2, FRVO 0, INIO 0, QNT 0, SPCX 39.
- C05b PASS: expected none above 1 pct; observed none above 1 pct.
- C06 PASS: expected all valid; observed 5 mapped, 0 invalid.
- C07 PASS: expected none above 100; observed none above 100.
- C08 INFO: expected count only; observed no identifier mapped for BSP.
- C09 WARN: expected listed; observed SPCX 10 group(s), CBRS 5 group(s), QNT 5 group(s), FRVO 7 group(s), INIO 5 group(s).
- C10 WARN: expected listed; observed 13F-HR whose cover page says amendment 1, amendments with an unknown AMENDMENTTYPE, all periods read (a filing at a measured quarter-end would refuse the build, R6-1) 8, duplicate amendments 0, new-holdings amendments repeating an identifier 7, new-holdings amendments superseded by a restatement 1, orphan amendments 0, restatements not later than the original 0, several originals 0.
- C11 PASS: expected none; observed none.
- C12 PASS: expected identical; observed identical.
- C13 PASS: expected all three match; observed CUSIP_MAP_SHA256 ok; FILER_REVIEW_SHA256 ok; DEAL_INPUTS_SHA256 ok; cache stamp ok.
- C14 PASS: expected none missing; observed none missing.
- C15 INFO: expected info; observed 2026-03-31 01jun2026-31aug2026_form13f: 130 HR filers; 2026-06-30 01jun2026-31aug2026_form13f: 8857 HR filers; 2025-12-31 01mar2026-31may2026_form13f: 207 HR filers; 2026-03-31 01mar2026-31may2026_form13f: 8741 HR filers.
- C16 PASS: expected hold; observed hold.
- C17 INFO: expected info; observed SPCX: PRN 10, calls 116, puts 130, blank VALUE 0, non-integral 0, other type 0, other PUTCALL 0, of the call and put rows 36 rows / 26251563 shares underlying sit under the Official List's option identifiers (counted in sh_calls and sh_puts, never in sh_13f), option rows under unlisted identifier variants (not counted) 2 rows / 8500 shares underlying; CBRS: PRN 1, calls 36, puts 27, blank VALUE 0, non-integral 0, other type 0, other PUTCALL 0, of the call and put rows 15 rows / 1915600 shares underlying sit under the Official List's option identifiers (counted in sh_calls and sh_puts, never in sh_13f), option rows under unlisted identifier variants (not counted) 1 rows / 5400 shares underlying; QNT: PRN 0, calls 8, puts 6, blank VALUE 0, non-integral 0, other type 0, other PUTCALL 0, of the call and put rows 7 rows / 112902 shares underlying sit under the Official List's option identifiers (counted in sh_calls and sh_puts, never in sh_13f), option rows under unlisted identifier variants (not counted) 0 rows / 0 shares underlying; FRVO: PRN 0, calls 10, puts 6, blank VALUE 0, non-integral 0, other type 0, other PUTCALL 0, of the call and put rows 6 rows / 182300 shares underlying sit under the Official List's option identifiers (counted in sh_calls and sh_puts, never in sh_13f), option rows under unlisted identifier variants (not counted) 0 rows / 0 shares underlying; INIO: PRN 0, calls 0, puts 0, blank VALUE 0, non-integral 0, other type 0, other PUTCALL 0, of the call and put rows 0 rows / 0 shares underlying sit under the Official List's option identifiers (counted in sh_calls and sh_puts, never in sh_13f), option rows under unlisted identifier variants (not counted) 0 rows / 0 shares underlying.
- C18 WARN: expected listed; observed CBRS: 10-Q 103,220,568 against prospectus 30,000,000 (244.1 pct).
- C19 PASS: expected within 2 pct; observed SPCX 3,668,807,223 against 3,685,578,550 (-0.46 pct); CBRS 88,739,770 against 88,744,964 (-0.01 pct).
- C20 INFO: expected count and tickers; observed 0: none.
- C21 PASS: expected official_list_2026q2; observed SPCX official_list_2026q2, CBRS official_list_2026q2, QNT official_list_2026q2, FRVO official_list_2026q2, INIO official_list_2026q2.

C03c SPCX:
- JPMORGAN CHASE & CO: 15563576 shares, implied price 164.19 against median 170.86
- PRICE T ROWE ASSOCIATES INC /MD/: 10709016 shares, implied price 0.17 against median 170.86
- MASSACHUSETTS FINANCIAL SERVICES CO /MA/: 7062255 shares, implied price 173.16 against median 170.86
- filer outside the review: 3444426 shares, implied price 0.17 against median 170.86
- filer outside the review: 874732 shares, implied price 0.17 against median 170.86
- Penserra Capital Management LLC: 584662 shares, implied price 0.17 against median 170.86
- filer outside the review: 519560 shares, implied price 0.17 against median 170.86
- filer outside the review: 470422 shares, implied price 153.23 against median 170.86
- filer outside the review: 347770 shares, implied price 0.00 against median 170.86
- Defiance ETFs, LLC: 328595 shares, implied price 157.54 against median 170.86
- filer outside the review: 258235 shares, implied price 0.17 against median 170.86
- filer outside the review: 225370 shares, implied price 0.17 against median 170.86

C03c CBRS:
- JPMORGAN CHASE & CO: 3100806 shares, implied price 216.16 against median 221.00
- PRICE T ROWE ASSOCIATES INC /MD/: 2044623 shares, implied price 0.22 against median 221.00
- filer outside the review: 425000 shares, implied price 10.98 against median 221.00
- T. Rowe Price Investment Management, Inc.: 340920 shares, implied price 0.22 against median 221.00
- filer outside the review: 81008 shares, implied price 0.22 against median 221.00
- filer outside the review: 61508 shares, implied price 193.30 against median 221.00
- filer outside the review: 20084 shares, implied price 0.22 against median 221.00
- filer outside the review: 20000 shares, implied price 0.00 against median 221.00
- filer outside the review: 20000 shares, implied price 216.16 against median 221.00
- filer outside the review: 19366 shares, implied price 0.22 against median 221.00
- filer outside the review: 18620 shares, implied price 214.65 against median 221.00
- LORD, ABBETT & CO. LLC: 12950 shares, implied price 0.22 against median 221.00

C03c QNT:
- Defiance ETFs, LLC: 1215283 shares, implied price 78.41 against median 81.74
- Penserra Capital Management LLC: 1200176 shares, implied price 0.08 against median 81.74
- LORD, ABBETT & CO. LLC: 99756 shares, implied price 0.08 against median 81.74
- T. Rowe Price Investment Management, Inc.: 73551 shares, implied price 0.08 against median 81.74
- filer outside the review: 10000 shares, implied price 0.08 against median 81.74
- PRICE T ROWE ASSOCIATES INC /MD/: 9383 shares, implied price 0.08 against median 81.74
- filer outside the review: 7500 shares, implied price 80.88 against median 81.74
- filer outside the review: 6555 shares, implied price 0.08 against median 81.74
- filer outside the review: 2800 shares, implied price 0.08 against median 81.74
- JPMORGAN CHASE & CO: 1814 shares, implied price 72.84 against median 81.74
- filer outside the review: 778 shares, implied price 75.57 against median 81.74
- filer outside the review: 50 shares, implied price 78.42 against median 81.74

C03c FRVO:
- JPMORGAN CHASE & CO: 7566646 shares, implied price 31.77 against median 29.23
- T. Rowe Price Investment Management, Inc.: 3996908 shares, implied price 0.03 against median 29.23
- PRICE T ROWE ASSOCIATES INC /MD/: 2658721 shares, implied price 0.03 against median 29.23
- ALLIANCEBERNSTEIN L.P.: 1769587 shares, implied price 29.52 against median 29.23
- filer outside the review: 1362734 shares, implied price 24.66 against median 29.23
- filer outside the review: 699288 shares, implied price 0.03 against median 29.23
- filer outside the review: 294575 shares, implied price 0.03 against median 29.23
- filer outside the review: 19659 shares, implied price 0.03 against median 29.23
- filer outside the review: 18715 shares, implied price 0.03 against median 29.23
- filer outside the review: 16992 shares, implied price 32.48 against median 29.23
- filer outside the review: 16311 shares, implied price 0.03 against median 29.23
- filer outside the review: 10000 shares, implied price 29.75 against median 29.23

C03c INIO:
- JPMORGAN CHASE & CO: 12353527 shares, implied price 38.32 against median 39.55
- Aspex Management (HK) Ltd: 6851716 shares, implied price 0.04 against median 39.55
- PRICE T ROWE ASSOCIATES INC /MD/: 5894653 shares, implied price 0.04 against median 39.55
- LORD, ABBETT & CO. LLC: 1374366 shares, implied price 0.04 against median 39.55
- filer outside the review: 113343 shares, implied price 0.04 against median 39.55
- filer outside the review: 55543 shares, implied price 0.04 against median 39.55
- filer outside the review: 27281 shares, implied price 37.29 against median 39.55
- filer outside the review: 27000 shares, implied price 0.04 against median 39.55
- filer outside the review: 13430 shares, implied price 33.41 against median 39.55

C05a:
- CBRS: 2 row(s) under other issuer names, e.g. CEVEBRAS SYSTEMS INC.; Canadian National Railroad
- SPCX: 39 row(s) under other issuer names, e.g. #N/A; SPAC and New Issue ETF; SPACE EX TECH CL A; SPACE EXPL; SPACE EXPL TECHNOLOGIES

C09 SPCX:
- 8000000 shares reported identically by ranks 43, 44
- 100000 shares reported identically by ranks 271, 272, 273
- 75000 shares reported identically by ranks 296, 297
- 57241 shares reported identically by ranks 319, 320
- 50000 shares reported identically by ranks 337, 338
- 40000 shares reported identically by ranks 366, 367, 368
- 36185 shares reported identically by ranks 380, 381
- 35000 shares reported identically by ranks 385, 386
- 20000 shares reported identically by ranks 470, 471, 472
- 10000 shares reported identically by ranks 599, 600, 601, 602, 603

C09 CBRS:
- 150000 shares reported identically by ranks 75, 76, 77
- 30000 shares reported identically by ranks 133, 134
- 20000 shares reported identically by ranks 152, 153
- 11000 shares reported identically by ranks 173, 174
- 10000 shares reported identically by ranks 180, 181, 182, 183

C09 QNT:
- 200000 shares reported identically by ranks 36, 37
- 150000 shares reported identically by ranks 47, 48
- 100000 shares reported identically by ranks 62, 63
- 40000 shares reported identically by ranks 73, 74
- 20000 shares reported identically by ranks 89, 90, 91

C09 FRVO:
- 500000 shares reported identically by ranks 56, 57
- 450000 shares reported identically by ranks 62, 63
- 175000 shares reported identically by ranks 83, 84
- 70000 shares reported identically by ranks 98, 99
- 25000 shares reported identically by ranks 116, 117
- 20000 shares reported identically by ranks 123, 124
- 10000 shares reported identically by ranks 138, 139

C09 INIO:
- 500000 shares reported identically by ranks 40, 41
- 400000 shares reported identically by ranks 51, 52
- 350000 shares reported identically by ranks 57, 58
- 80000 shares reported identically by ranks 88, 89
- 25000 shares reported identically by ranks 115, 116

## Builder decisions

1. **No network, no fetch step.** The spec lists a `fetch` step as optional ('if the spec has one'); it has none. The supervisor fetched every SEC file and the script makes no request and imports no network or process module (selftest G14). `verify` only re-hashes the cached zips against their stamps.
2. **Where the zip folder may sit (spec R2 against round 5).** R2 says the script refuses a `--zip-dir` inside the repository; round 5 puts the raw zips in the repository's gitignored `data/vintages/form13f_zips/`. The latest round governs, so exactly that folder is accepted, and only while `.gitignore` names it; any other folder inside the repository is refused. The cache (filtered rows, names, the two private reviewed tables) is refused anywhere inside the repository.
3. **The cache location.** The default `--cache` is the folder `ipo13f_cache` in the user's home folder, as the spec says. This build was run with a cache in the session's scratch folder outside the clone (the instruction to work only inside the clone, with R3's rule that the cache is outside the repository).
4. **The live latch is the file named exactly `STOP`.** A preserved record such as `STOP.<date>.<note>` is not a latch and does not stop a run.
5. **Pricing date means the prospectus date.** `pricing_date` is the date printed on the 424B4 cover ('Prospectus dated'); the 424B4 itself is filed a day later. The three deals that have no 424B4 in the supervisor's copies (BSP, SKHY, JMKE) take the issuer's pricing release date, relayed by the supervisor and marked `issuer_release_relayed` in `deal_inputs.csv` (R6).
6. **'First 10-Q' means the 10-Q for the first quarter-end.** CBRS and FRVO filed a 10-Q for the period ended 31 March 2026 after listing; that one covers a quarter-end before the offering. The denominator comes from the 10-Q for the period ended 30 June 2026, the first calendar quarter-end after pricing.
7. **Rounded share counts.** SpaceX's financial statements give shares in millions (7,607 and 5,569) and Fervo's in thousands (286,869 and 7,785). They are entered as stated, multiplied out, and the precision (plus or minus half a million, half a thousand) is in the row. Fervo's statement says 'issued'; there is no treasury stock at 30 June 2026, so issued equals outstanding.
8. **Identifier variants.** Shares are summed only for the mapped identifier after stripping white space and upper-casing (O-13). Rows under other identifier strings that match the deal's name are reported in `sh_name_match_other_cusip` and never added.
9. **Duplicates and repeated identifiers** (`n_amend_duplicates`, `n_new_holdings_repeat_cusip`) can only be judged on rows the scan kept, which are the deals' rows. Orphans and several-originals are judged over every filer.
10. **Reports 'filed after the due date'** counts 13F-HR originals (not amendments) filed after the 45th day, rolled to the next business day over weekends and federal holidays.
11. **`sh_13dg_holders_without_13f`** sums each reporting person's typed count (spec 3.7). Several persons in one filing may report the same shares; the column is labelled in the README as beneficial ownership that may include convertible, unlisted or repeated shares, and is never added to anything.
12. **Label numbering.** Where a name is withheld the output says `withheld #n` (`individual (withheld) #n` for an i2 reporting person of type IN), numbered within a ticker so that keys stay unique.
13. **`reg_category` follows round 5** (SECFILENUMBER is a separate field from FORM13FFILENUMBER). The prefix meanings 801-, 802-, 8- are relayed, not defined by the readme.
14. **A 13F-HR whose cover page says it is an amendment** (ISAMENDMENT Y, type NEW HOLDINGS) is kept as the base because its SUBMISSIONTYPE is 13F-HR, and is listed in C10.
15. **The second scan** keeps the rows of the mapped listed-class identifier and every row whose issuer name matches a deal pattern; rejected identifiers are not collected.
16. **Supervisor ruling R6-1 (unknown `AMENDMENTTYPE`).** `UNKNOWN_AMENDTYPE_SCOPE` is `measured_quarters_only`: a blank or unknown type refuses the build only for a filing whose period is a measured quarter-end (30 Jun 2026 now). The spec's literal reading, any period, is the value `all`. The eight blank-type 13F-HR/A filings in the Mar-May zip (periods 2023 to 2025, none with a row of any deal) are listed in C10.
17. **Supervisor ruling R6-2 (C02 pins).** The supervisor verified both in the zip. Row 5 (Atreides): shares rows 3,110,086, VALUE 687,329,006, calls 700,000; the relayed 3,810,086 was shares plus calls. Row 8 (Maplelane, QNT): shares rows 150,000 (23,597 + 4,929 + 58,377 + 63,097); the relayed 145,071 dropped the 4,929 sole-discretion row. Both pins are corrected, with the relayed values beside them in the checks.csv description.
18. **Supervisor ruling R6-3 (offer price).** `deal_inputs.csv` has an item `offer_price_usd`: the price sits in the `shares` column and the quote is the 424B4 cover phrase. The script-side price table is gone and `DEAL_INPUTS_SHA256` covers the prices. No header changes; the `item` allowed values gain one.
19. **Supervisor ruling R6-4 (zip folder).** The builder's reading is accepted: only the gitignored `data/vintages/form13f_zips/` may sit inside the repository; the cache may not.
20. **Supervisor ruling R6-5 (`pre_ipo_flag`).** A ; list of tickers per filer is accepted, so a flag for one issuer adds nothing to another issuer's `sh_pre_ipo_flagged`.
21. **Supervisor ruling R6-6 (option identifiers).** Rows under the Official List's CALL and PUT identifiers of a deal are options on that deal's listed class. The CUSIP map gives them the roles `option_call` and `option_put`; their rows are counted in `sh_calls` and `sh_puts` by PUTCALL, or by the identifier's role when PUTCALL is blank, together with option rows under the main identifier, and never in `sh_13f`. C17 reports them separately. Option rows under unlisted identifier variants are not counted and are reported in C17.
22. **Supervisor ruling R6-7 (rounded counts).** Accepted. The README says SpaceX's quarter-end count is stated in millions and Fervo's in thousands (issued, no treasury stock). Cerebras's primary denominator is its 30 Jun balance-sheet count of 103,220,568 (R3-1).
23. **Supervisor ruling R6-8 (i2 typed counts).** Accepted as labelled. The README says the 13D/13G column overlaps across the filings of one group and includes convertible Class B shares.
24. **Supervisor ruling R6-9 (13F-HR with ISAMENDMENT Y).** One 13F-HR whose cover page says it is a NEW HOLDINGS amendment is kept as the base by its SUBMISSIONTYPE and listed in C10.
25. **Supervisor ruling R6-10 (Official List).** `13flist2026q2` is treated as the list governing the June reports. Its title page reads "Second Quarter FY 2026" and prints no as-of date (C21).
26. **Filer review accepted by the supervisor** (80 organisations public, 15 individuals not named). Kinds remain hypotheses and appear only in `kind_hypothesis.csv`.
27. **First trading days are relayed.** CBRS comes from its own first 10-Q (read by the supervisor); BSP was verified verbatim by the supervisor; the other six were relayed from a web search with fetched pages and are not re-read by the builder: SPCX (cnbc.com live updates, 12 Jun 2026), QNT (conyers.com note), FRVO (ir.fervoenergy.com investor FAQs), INIO (Nasdaq opening-bell page of 4 Jun 2026; the pricing release said trading was expected on 4 June 2026), SKHY (Nasdaq Trader notice DTN2026-11; when-issued from 10 Jul 2026, regular way from 13 Jul), JMKE (the company's closing release). Each source string is in `first_trade_source`.
28. **Pricing dates of the three September-quarter deals are relayed from the issuers' releases** (marked `issuer_release_relayed`): BSP 2026-06-30, SKHY 2026-07-09, JMKE 2026-07-29. The deal master's 2026-07-31 for Jersey Mike's is the closing date. No first quarter-end changes.
29. **Supervisor ruling R6-11 (the 13D/13G column).** The Schedule 13D/13G column left the main README table and has its own small table after it, headed "Schedule 13D/13G shares, any class, holders with no 13F row (not comparable; can exceed the listed class)", with a sentence that the counts are not comparable and a gloss of Schedule 13D/13G at first use. No person is named. `holdings.csv` is unchanged.
30. **Supervisor ruling R6-12 (the prospectus count).** The README table no longer has the percentage against the count after the offering; `holdings.csv` keeps `pct_of_listed_prosp`. One sentence after the table says that the prospectus count is a different quantity (for Cerebras only the Class A shares sold) and that the percentage can exceed 100.
31. **Supervisor ruling R6-13 (the weighted mean, spec R3-3).** SpaceX's weight, INNIO's zero weight and the count of unmeasured deals now sit in the same sentence as the weighted mean, joined by a colon.
32. **Supervisor ruling R6-14 (denominator at its point of use).** A selftest check compares `pct_of_listed` in the written `holdings.csv` with 100 x `sh_13f` over the listed class's balance-sheet count read straight from `deal_inputs.csv`, for synthetic deals whose prospectus count differs. Two mutants now fail it: the prospectus count as primary, and `pct_of_listed` computed against the prospectus count at the point of use while `deals.csv` stays right.
33. **Supervisor ruling R6-15 (stale restatement).** A selftest case files a restatement before the original; it must lose and be listed as stale. The mutant that lets it win now fails.
34. **Supervisor ruling R6-16 (leak).** The selftest's planted ISIN and FIGI are shape-valid synthetic strings, not real identifiers; the script was searched for any other ISIN-shaped or BBG-shaped string.
35. **Supervisor ruling R6-17 (small items).** The column dictionary says a filer is counted only if its reported shares are positive. C01d's expected text now equals its observed text, INIO 0.000 included. `overlap_i2.csv` leaves `i2_shares`, `sh_13f_matched` and `gap_sh` blank on the row of a holder withheld as an individual, so that a withheld person cannot be re-identified by matching share counts against a named filer (a mutant that shows them fails the selftest).
36. **Status** is computed: a deal is `measured` when the cached zips hold 13F-HR filings for its first quarter-end, else `awaiting_next_zip`.
37. **Identifiers rejected from the CUSIP map, by reason (no identifier is committed):** CBRS: 1 x a different issuer's security on the Official List that one or more filers labelled with the deal's name; CBRS: 3 x not on the Official List; one-filer identifier variant of the deal's name (mis-keyed or an option-type variant); SKHY: 1 x Korean ordinary share (KRW 5000 par), not the Nasdaq ADS; SKHY: 1 x a sponsored ADR of SK hynix reported by one filer, not the Nasdaq ADS of the 2026 offering; SKHY: 3 x not on the Official List; SK hynix ordinary share or another instrument, not the Nasdaq ADS; SPCX: 3 x a different issuer's security on the Official List that one or more filers labelled with the deal's name; SPCX: 7 x a different security (an exchange-traded fund or product) whose name contains the issuer's name; SPCX: 4 x not on the Official List; one-filer identifier variant of the deal's name (mis-keyed or an option-type variant).
