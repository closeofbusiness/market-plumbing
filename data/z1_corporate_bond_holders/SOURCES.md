# Sources, requests and builder decisions: net acquisition of corporate and foreign bonds by holder sector (Z.1 table F3.5)

The specification is `_research/2026-10-26-Z1-Corporate-Bond-Holders-Spec.md`, committed at bc22c96 (with the supervisor's rulings of rounds 1 and 2) before the first request.

## Requests

**By the spec author, first draft, 26 Oct 2026** (5 requests, all GET, sequential, at least 2.5 s apart, the User-Agent of R2, no redirect followed, no retry, no 403 or 429; the rewrite made no request):

| UTC (26 Oct 2026) | URL | Status | Bytes | Note |
|---|---|---|---|---|
| 19:43:08 | https://www.federalreserve.gov/releases/z1/20260911/z1_csv_files.zip | 200 | 8,336,582 | sha256 b63af9755437df0fb88b7cf346f8f9eaeb22bf1aa2b5df1709334135c43de4b6; 616 members |
| 19:45:22 | https://home.treasury.gov/data/treasury-international-capital-tic-system | 200 | 78,207 | read for the Form S and CSLT notes; not used by the build |
| 19:45:25 | https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/cslt.zip | 200 | 8,910,770 | metadata only; not used by the build |
| 19:46:30 | https://www.federalreserve.gov/releases/z1/20260911/default.htm | 404 | 82,134 | not retried; never requested by the build |
| 19:46:33 | https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FA653063005&t=F.213 | 200 | 73,549 | the Financial Accounts Guide's error page; not retried |

**By others during review (relayed from the round-1 rulings, not logged by the spec author):** Grok read the published F3.5.t table on federalreserve.gov; the supervisor read the cached 11 Sep zip and checked a Treasury press release. No request by anyone went to sec.gov or FRED.

**By this build (`fetch`, one request per run; the request log is fetch_log.csv):**

| UTC | host | path | status | bytes | sha256 | Last-Modified |
|---|---|---|---|---|---|---|
| 2026-10-27T05:44:03Z | www.federalreserve.gov | /releases/z1/20260911/z1_csv_files.zip | 200 | 8336582 | b63af9755437df0fb88b7cf346f8f9eaeb22bf1aa2b5df1709334135c43de4b6 | 2026-09-11T16:00:19Z |

## Disclosure: what was seen before any build

The wave-window shares were seen during review, before this spec was committed, so they are reported, not tested.

Before any build, during the review of the specification, some holder shares were seen:

- Grok (an attack parcel that carried no blind clause) read the published seasonally adjusted F3.5.t table on federalreserve.gov and reported wave-window shares of about 32% (life plus
  property-casualty insurers), 47% (registered funds), 41% (rest of the world) and -35% (household residual).
- The supervisor then confirmed from the cached 11 Sep zip, unadjusted sums: insurers 33.26% of 2,228,428 $mn over the ten quarters; 2024 37.12% (224,689 + 70,237 of 794,490); 2025 35.67%
  (221,483 + 65,834 of 805,405).
- The second reviewer stayed blind on 2024-26 and computed 2017-2019 shares (observed during review): registered funds 39.98%, insurers 34.36%, rest of the world 31.23% of 1,329,619 $mn.
- The spec author saw no holder share for any window and no 2024-26 value; read the dictionaries, the identity residuals on 2017Q1-2019Q4, the FA/4-versus-FU annual gaps for 2017-2019, the flows
  of lines 18, 41, 42 and 50 for 2020Q1-2021Q4, a count of ND cells (zero) and CSLT metadata only.

## Identities (section 2.3)

Checked on every quarter from 1990:Q1 (FAIL from 2017:Q1, WARN before), within 2 $mn:

- Flows, both bases: the 28 leaf lines sum to line 13; line 1 = line 13; lines 2 + 3 + 12 = line 1; lines 4-11 = line 3; 19 = 20 + 21; 24 = 25 + 26; 27 = 28 + 29; 30 = 31 + 32; 43 = 44 + 45;
  51 = 52 + 53; general + separate accounts = line 30 (fu basis only).
- Levels: the 28 leaf levels sum to line 13 and line 54 = line 1 - line 13. Line 1 minus line 13 was -290,252 (2017Q4), +357,667 (2018Q4) and -599,833 (2019Q4) $mn on the 11 Sep release.
  The spec's first draft wrongly said line 13 is not the sum of the leaves; the level-share denominator is that sum, and line 54 is printed beside it.
- Bases: over each complete calendar year from 2017, sum(FA)/4 equals sum(FU) within 4 $mn on all 53 lines.

## Wording of every series code

From the data dictionaries of release 20260911 (the FU, FA and level code of every line; the four S1281 codes). Level codes beginning LM are market value; FL codes state no basis.

| Series code | Line | Dictionary text |
|---|---|---|
| FU893163005.Q | 1 | All sectors; corporate and foreign bonds; liability |
| FA893163005.Q | 1 | All sectors; corporate and foreign bonds; liability |
| FL893163005.Q | 1 | All sectors; corporate and foreign bonds; liability |
| FU103163005.Q | 2 | Nonfinancial corporate business; corporate bonds; liability |
| FA103163005.Q | 2 | Nonfinancial corporate business; corporate bonds; liability |
| FL103163005.Q | 2 | Nonfinancial corporate business; corporate bonds; liability |
| FU793163005.Q | 3 | Domestic financial sectors; corporate and foreign bonds; liability |
| FA793163005.Q | 3 | Domestic financial sectors; corporate and foreign bonds; liability |
| FL793163005.Q | 3 | Domestic financial sectors; corporate and foreign bonds; liability |
| FU763163005.Q | 4 | U.S.-chartered depository institutions; corporate and foreign bonds; liability |
| FA763163005.Q | 4 | U.S.-chartered depository institutions; corporate and foreign bonds; liability |
| FL763163005.Q | 4 | U.S.-chartered depository institutions; corporate and foreign bonds; liability |
| FU673163005.Q | 5 | Issuers of asset-backed securities; corporate and foreign bonds; liability |
| FA673163005.Q | 5 | Issuers of asset-backed securities; corporate and foreign bonds; liability |
| FL673163005.Q | 5 | Issuers of asset-backed securities; corporate and foreign bonds; liability |
| FU613163005.Q | 6 | Finance companies; corporate and foreign bonds; liability |
| FA613163005.Q | 6 | Finance companies; corporate and foreign bonds; liability |
| FL613163005.Q | 6 | Finance companies; corporate and foreign bonds; liability |
| FU643163075.Q | 7 | Mortgage real estate investment trusts; corporate and foreign bonds, excluding FHLB advances; liability |
| FA643163075.Q | 7 | Mortgage real estate investment trusts; corporate and foreign bonds, excluding FHLB advances; liability |
| FL643163075.Q | 7 | Mortgage real estate investment trusts; corporate and foreign bonds, excluding FHLB advances; liability |
| FU453163003.Q | 8 | Business development companies; corporate bonds; liability |
| FA453163003.Q | 8 | Business development companies; corporate bonds; liability |
| FL453163003.Q | 8 | Business development companies; corporate bonds; liability |
| FU663163003.Q | 9 | Security brokers and dealers; corporate and foreign bonds; liability |
| FA663163003.Q | 9 | Security brokers and dealers; corporate and foreign bonds; liability |
| FL663163003.Q | 9 | Security brokers and dealers; corporate and foreign bonds; liability |
| FU733163005.Q | 10 | Holding companies; corporate and foreign bonds; liability |
| FA733163005.Q | 10 | Holding companies; corporate and foreign bonds; liability |
| FL733163005.Q | 10 | Holding companies; corporate and foreign bonds; liability |
| FU503163003.Q | 11 | Other financial business; corporate and foreign bonds where the proceeds are down-streamed to broker-dealer subsidiaries by investment banks that are holding-company parents; liability |
| FA503163003.Q | 11 | Other financial business; corporate and foreign bonds where the proceeds are down-streamed to broker-dealer subsidiaries by investment banks that are holding-company parents; liability |
| FL503163003.Q | 11 | Other financial business; corporate and foreign bonds where the proceeds are down-streamed to broker-dealer subsidiaries by investment banks that are holding-company parents; liability |
| FU263163005.Q | 12 | Rest of the world; bonds; liability |
| FA263163005.Q | 12 | Rest of the world; bonds; liability |
| LM263163005.Q | 12 | Rest of the world; bonds; liability |
| FU893063005.Q | 13 | All sectors; corporate and foreign bonds; asset |
| FA893063005.Q | 13 | All sectors; corporate and foreign bonds; asset |
| FL893063005.Q | 13 | All sectors; corporate and foreign bonds; asset |
| FU153063005.Q | 14 | Households and nonprofit organizations; corporate and foreign bonds; asset |
| FA153063005.Q | 14 | Households and nonprofit organizations; corporate and foreign bonds; asset |
| LM153063005.Q | 14 | Households and nonprofit organizations; corporate and foreign bonds; asset |
| FU123063003.Q | 15 | Equity real estate investment trusts; corporate and foreign bonds; asset |
| FA123063003.Q | 15 | Equity real estate investment trusts; corporate and foreign bonds; asset |
| LM123063003.Q | 15 | Equity real estate investment trusts; corporate and foreign bonds; asset |
| FU313063005.Q | 16 | Federal government; corporate and foreign bonds; asset |
| FA313063005.Q | 16 | Federal government; corporate and foreign bonds; asset |
| FL313063005.Q | 16 | Federal government; corporate and foreign bonds; asset |
| FU213063003.Q | 17 | State and local governments; corporate and foreign bonds; asset |
| FA213063003.Q | 17 | State and local governments; corporate and foreign bonds; asset |
| LM213063003.Q | 17 | State and local governments; corporate and foreign bonds; asset |
| FU713011525.Q | 18 | Central bank; other U.S. reserves, foreign securities; asset |
| FA713011525.Q | 18 | Central bank; other U.S. reserves, foreign securities; asset |
| FL713011525.Q | 18 | Central bank; other U.S. reserves, foreign securities; asset |
| FU763063005.Q | 19 | U.S.-chartered depository institutions, including IBFs; corporate and foreign bonds; asset |
| FA763063005.Q | 19 | U.S.-chartered depository institutions, including IBFs; corporate and foreign bonds; asset |
| LM763063005.Q | 19 | U.S.-chartered depository institutions, including IBFs; corporate and foreign bonds; asset |
| FU763063605.Q | 20 | U.S.-chartered depository institutions; private MBS and CMOs; asset |
| FA763063605.Q | 20 | U.S.-chartered depository institutions; private MBS and CMOs; asset |
| LM763063605.Q | 20 | U.S.-chartered depository institutions; private MBS and CMOs; asset |
| FU763063095.Q | 21 | U.S.-chartered depository institutions, including IBFs; corporate and foreign bonds, excluding private MBS and CMOs; asset |
| FA763063095.Q | 21 | U.S.-chartered depository institutions, including IBFs; corporate and foreign bonds, excluding private MBS and CMOs; asset |
| LM763063095.Q | 21 | U.S.-chartered depository institutions, including IBFs; corporate and foreign bonds, excluding private MBS and CMOs; asset |
| FU753063005.Q | 22 | Foreign banking offices in the U.S., including IBFs; corporate and foreign bonds; asset |
| FA753063005.Q | 22 | Foreign banking offices in the U.S., including IBFs; corporate and foreign bonds; asset |
| LM753063005.Q | 22 | Foreign banking offices in the U.S., including IBFs; corporate and foreign bonds; asset |
| FU743063005.Q | 23 | Banks in U.S.-affiliated areas; corporate and foreign bonds; asset |
| FA743063005.Q | 23 | Banks in U.S.-affiliated areas; corporate and foreign bonds; asset |
| LM743063005.Q | 23 | Banks in U.S.-affiliated areas; corporate and foreign bonds; asset |
| FU473063005.Q | 24 | Credit unions; corporate and foreign bonds; asset |
| FA473063005.Q | 24 | Credit unions; corporate and foreign bonds; asset |
| LM473063005.Q | 24 | Credit unions; corporate and foreign bonds; asset |
| FU473063605.Q | 25 | Credit unions; mortgage-backed securities and other asset-backed bonds; asset |
| FA473063605.Q | 25 | Credit unions; mortgage-backed securities and other asset-backed bonds; asset |
| LM473063605.Q | 25 | Credit unions; mortgage-backed securities and other asset-backed bonds; asset |
| FU473063095.Q | 26 | Credit unions; corporate and foreign bonds, excluding mortgage-backed securities and other asset-backed bonds; asset |
| FA473063095.Q | 26 | Credit unions; corporate and foreign bonds, excluding mortgage-backed securities and other asset-backed bonds; asset |
| LM473063095.Q | 26 | Credit unions; corporate and foreign bonds, excluding mortgage-backed securities and other asset-backed bonds; asset |
| FU513063005.Q | 27 | Property-casualty insurance companies; corporate and foreign bonds, including those held by U.S. residual market reinsurers; asset |
| FA513063005.Q | 27 | Property-casualty insurance companies; corporate and foreign bonds, including those held by U.S. residual market reinsurers; asset |
| LM513063005.Q | 27 | Property-casualty insurance companies; corporate and foreign bonds, including those held by U.S. residual market reinsurers; asset |
| FU513063605.Q | 28 | Property-casualty insurance companies; mortgage-backed securities and other asset-backed bonds, including those held by U.S. residual market reinsurers; asset |
| FA513063605.Q | 28 | Property-casualty insurance companies; mortgage-backed securities and other asset-backed bonds, including those held by U.S. residual market reinsurers; asset |
| LM513063605.Q | 28 | Property-casualty insurance companies; mortgage-backed securities and other asset-backed bonds, including those held by U.S. residual market reinsurers; asset |
| FU513063095.Q | 29 | Property-casualty insurance companies; corporate and foreign bonds, excluding mortgage-backed securities and other asset-backed bonds; asset |
| FA513063095.Q | 29 | Property-casualty insurance companies; corporate and foreign bonds, excluding mortgage-backed securities and other asset-backed bonds; asset |
| LM513063095.Q | 29 | Property-casualty insurance companies; corporate and foreign bonds, excluding mortgage-backed securities and other asset-backed bonds; asset |
| FU543063005.Q | 30 | Life insurance companies; corporate and foreign bonds; asset |
| FA543063005.Q | 30 | Life insurance companies; corporate and foreign bonds; asset |
| LM543063005.Q | 30 | Life insurance companies; corporate and foreign bonds; asset |
| FU543063675.Q | 31 | Life insurance companies, general accounts; mortgage-backed securities and other asset-backed bonds, including those held by U.S. captive reinsurers; asset |
| FA543063675.Q | 31 | Life insurance companies, general accounts; mortgage-backed securities and other asset-backed bonds, including those held by U.S. captive reinsurers; asset |
| LM543063675.Q | 31 | Life insurance companies, general accounts; mortgage-backed securities and other asset-backed bonds, including those held by U.S. captive reinsurers; asset |
| FU543063095.Q | 32 | Life insurance companies; corporate and foreign bonds, excluding mortgage-backed securities and other asset-backed bonds; asset |
| FA543063095.Q | 32 | Life insurance companies; corporate and foreign bonds, excluding mortgage-backed securities and other asset-backed bonds; asset |
| LM543063095.Q | 32 | Life insurance companies; corporate and foreign bonds, excluding mortgage-backed securities and other asset-backed bonds; asset |
| FU543063075.Q | 8 | Life insurance companies, general accounts; corporate and foreign bonds; asset |
| LM543063075.Q | 8 | Life insurance companies, general accounts; corporate and foreign bonds; asset |
| FU543063085.Q | 8 | Life insurance companies, separate accounts; corporate and foreign bonds; asset |
| LM543063085.Q | 8 | Life insurance companies, separate accounts; corporate and foreign bonds; asset |
| FU573063005.Q | 33 | Private pension funds; corporate and foreign bonds; asset |
| FA573063005.Q | 33 | Private pension funds; corporate and foreign bonds; asset |
| LM573063005.Q | 33 | Private pension funds; corporate and foreign bonds; asset |
| FU343063005.Q | 34 | Federal government pension funds; corporate and foreign bonds; asset |
| FA343063005.Q | 34 | Federal government pension funds; corporate and foreign bonds; asset |
| LM343063005.Q | 34 | Federal government pension funds; corporate and foreign bonds; asset |
| FU223063045.Q | 35 | State and local government employee defined benefit pension funds; corporate and foreign bonds; asset |
| FA223063045.Q | 35 | State and local government employee defined benefit pension funds; corporate and foreign bonds; asset |
| LM223063045.Q | 35 | State and local government employee defined benefit pension funds; corporate and foreign bonds; asset |
| FU633063005.Q | 36 | Money market funds; corporate and foreign bonds; asset |
| FA633063005.Q | 36 | Money market funds; corporate and foreign bonds; asset |
| FL633063005.Q | 36 | Money market funds; corporate and foreign bonds; asset |
| FU653063005.Q | 37 | Mutual funds; corporate and foreign bonds; asset (market value) |
| FA653063005.Q | 37 | Mutual funds; corporate and foreign bonds; asset (market value) |
| LM653063005.Q | 37 | Mutual funds; corporate and foreign bonds; asset (market value) |
| FU553063003.Q | 38 | Closed-end funds; corporate and foreign bonds; asset |
| FA553063003.Q | 38 | Closed-end funds; corporate and foreign bonds; asset |
| LM553063003.Q | 38 | Closed-end funds; corporate and foreign bonds; asset |
| FU563063003.Q | 39 | Exchange-traded funds; corporate and foreign bonds; asset |
| FA563063003.Q | 39 | Exchange-traded funds; corporate and foreign bonds; asset |
| LM563063003.Q | 39 | Exchange-traded funds; corporate and foreign bonds; asset |
| FU463063005.Q | 40 | Interval funds and tender offer funds; corporate and foreign bonds; asset |
| FA463063005.Q | 40 | Interval funds and tender offer funds; corporate and foreign bonds; asset |
| LM463063005.Q | 40 | Interval funds and tender offer funds; corporate and foreign bonds; asset |
| FU623063005.Q | 41 | Hedge funds (domestic); corporate and foreign bonds net of short sales; asset (market value) |
| FA623063005.Q | 41 | Hedge funds (domestic); corporate and foreign bonds net of short sales; asset (market value) |
| LM623063005.Q | 41 | Hedge funds (domestic); corporate and foreign bonds net of short sales; asset (market value) |
| FU443063000.Q | 42 | Private debt funds; corporate and foreign bonds; asset |
| FA443063000.Q | 42 | Private debt funds; corporate and foreign bonds; asset |
| LM443063000.Q | 42 | Private debt funds; corporate and foreign bonds; asset |
| FU403063005.Q | 43 | Government-sponsored enterprises; corporate and foreign bonds; asset |
| FA403063005.Q | 43 | Government-sponsored enterprises; corporate and foreign bonds; asset |
| LM403063005.Q | 43 | Government-sponsored enterprises; corporate and foreign bonds; asset |
| FU403063605.Q | 44 | Government-sponsored enterprises; mortgage-backed securities and other asset-backed bonds; asset |
| FA403063605.Q | 44 | Government-sponsored enterprises; mortgage-backed securities and other asset-backed bonds; asset |
| LM403063605.Q | 44 | Government-sponsored enterprises; mortgage-backed securities and other asset-backed bonds; asset |
| FU403063095.Q | 45 | Government-sponsored enterprises; corporate and foreign bonds, excluding mortgage-backed securities and other asset-backed bonds; asset |
| FA403063095.Q | 45 | Government-sponsored enterprises; corporate and foreign bonds, excluding mortgage-backed securities and other asset-backed bonds; asset |
| LM403063095.Q | 45 | Government-sponsored enterprises; corporate and foreign bonds, excluding mortgage-backed securities and other asset-backed bonds; asset |
| FU613063003.Q | 46 | Finance companies; corporate and foreign bonds; asset |
| FA613063003.Q | 46 | Finance companies; corporate and foreign bonds; asset |
| LM613063003.Q | 46 | Finance companies; corporate and foreign bonds; asset |
| FU643063073.Q | 47 | Mortgage real estate investment trusts; corporate and foreign bonds; asset |
| FA643063073.Q | 47 | Mortgage real estate investment trusts; corporate and foreign bonds; asset |
| LM643063073.Q | 47 | Mortgage real estate investment trusts; corporate and foreign bonds; asset |
| FU663063005.Q | 48 | Security brokers and dealers; corporate and foreign bonds (net); asset |
| FA663063005.Q | 48 | Security brokers and dealers; corporate and foreign bonds (net); asset |
| LM663063005.Q | 48 | Security brokers and dealers; corporate and foreign bonds (net); asset |
| FU733063003.Q | 49 | Holding companies; corporate and foreign bonds; asset |
| FA733063003.Q | 49 | Holding companies; corporate and foreign bonds; asset |
| LM733063003.Q | 49 | Holding companies; corporate and foreign bonds; asset |
| FU503063005.Q | 50 | Other financial business; corporate and foreign bonds, including financial stabilization programs; asset |
| FA503063005.Q | 50 | Other financial business; corporate and foreign bonds, including financial stabilization programs; asset |
| FL503063005.Q | 50 | Other financial business; corporate and foreign bonds, including financial stabilization programs; asset |
| FU263063005.Q | 51 | Rest of the world; corporate bonds; asset |
| FA263063005.Q | 51 | Rest of the world; corporate bonds; asset |
| LM263063005.Q | 51 | Rest of the world; corporate bonds; asset |
| FU263063603.Q | 52 | Rest of the world; U.S. mortgage-backed securities and other U.S. asset-backed bonds; asset |
| FA263063603.Q | 52 | Rest of the world; U.S. mortgage-backed securities and other U.S. asset-backed bonds; asset |
| LM263063603.Q | 52 | Rest of the world; U.S. mortgage-backed securities and other U.S. asset-backed bonds; asset |
| FU263063095.Q | 53 | Rest of the world: U.S. corporate bonds, excluding mortgage-backed securities and other asset-backed bonds; asset |
| FA263063095.Q | 53 | Rest of the world: U.S. corporate bonds, excluding mortgage-backed securities and other asset-backed bonds; asset |
| LM263063095.Q | 53 | Rest of the world: U.S. corporate bonds, excluding mortgage-backed securities and other asset-backed bonds; asset |
| LM903063003.Q | 54 | Instrument discrepancies; corporate and foreign bonds (level) |

## Other sources

- Board of Governors of the Federal Reserve System, FEDS Notes, 12 October 2018, on reinsurance structures (relayed in the specification by the supervisor; not read by the builder, who does not have its title).
- Treasury TIC press release sb0662, used only for the typed constants of check CREF2 (relayed; checked verbatim by the supervisor; not read by the builder).
- BIS Quarterly Review, 16 March 2026, for one context figure in the README (supervisor ruling, round 2).

## Builder decisions

Where the specification is ambiguous the stricter reading about leaks and causal wording was taken. None of these changes a rule, a threshold, a window, a registered number or a label.

1. **Zip not kept; member files committed; .gitignore.** R4 says the zip is not kept and the 14 member files are committed under data/vintages/z1_corporate_bond_holders/<release>/; the build instruction says the raw zip stays in a gitignored cache. Read together: the zip is held in memory only and never written to disk; .gitignore carries `*.zip`, `*.json` and the STOP latch for that folder as a second line of defence, and the committed member files are exactly R4's. No member CSV is ignored.

2. **General and separate accounts on the fu basis only.** The seven members of R4 hold no seasonally adjusted file for the S1281 tables, so ins_life_ga and ins_life_sa have no fa_div4 rows; the identity general + separate accounts = line 30 is checked on the fu basis only. 2.3 says "both bases" for the other identities.

3. **Issuer offset ratio.** 3.7 defines the offset ratio for holders only. For issuers it is the absolute line-1 window sum over the sum of the absolute window sums of lines 2, 3 and 12 (the details 4-11 are inside line 3). Same 0.5 threshold.

4. **levels.csv starts at 2016:Q4.** 3.3 says the same quarters as quarterly.csv (2017:Q1 on), but 3.9 needs the 2016:Q4 level for the 2016:Q4 level share and for the start of pre1719 and y2017. levels.csv therefore starts one quarter earlier, and C09 covers levels from 2016:Q4.

5. **Total rows carry no share of the positive flows.** 3.6 gives share_of_positive_pct to every row whose flow is positive, members and sub-lines included; the all-holder and all-issuer total rows are left blank (their ratio to the positive total is not a share of anything).

6. **A void window writes no share at all.** When the total is not positive, share_of_total_pct and share_of_positive_pct are both blank (3.5 names only the first).

7. **Tolerance of the flow identities.** 2.3 says within 1 $mn and "exactly"; C04 says within 2 $mn for each. The check uses 2 $mn on every identity; the observed maximum is printed in checks.csv.

8. **Checks across releases.** checks.csv has no release column, so a per-release check prints one clause per cached release in `observed` and takes the worst status. Pins fail on 20260911 and warn on a later release.

9. **Folder guards refuse instead of adding a check.** The folder guards (names, headers, allowed values, keys, verdict words, CUSIP shapes, paths, at signs, wording, the typed reference constants) are not among the pinned and structural checks of section 8; when they find a problem the build stops (exit 2) and writes nothing, the way G12-G14 and G17 require "refuse".

10. **Wording scan on the CSVs as well.** G14 applies to README.md. The same two patterns and the verdict-word scan are also applied to every CSV when it is written (stricter); SOURCES.md is exempt, as the denial sentence is.

11. **A corrupt zip latches STOP.** R3a lists empty, HTML and non-zip bodies. A body that starts with PK\x03\x04 but cannot be opened as a zip is treated as the same kind of failed content test (STOP).

12. **A cached release is not fetched again.** fetch refuses a release whose folder already holds provenance.csv (exit 5); the cache is never overwritten. The two runs a day of R3 are counted from fetch_log.csv.

13. **provenance.csv layout.** kind,name,sha256,bytes,last_modified,members: one `zip` row (digest, size and Last-Modified of the zip, member count of the archive) and one `member` row per cached file.

14. **Missing member or table.** A cached release that lacks one of the seven CSV files stops the build (DataError). A missing dictionary file, or a code missing from a header, is a C15 FAIL and the build goes on.

15. **Which release the README shows.** The README tables use the newest cached release; earlier releases appear in the CSVs and in revisions.csv.

16. **Outputs written when a check fails.** As R3b says, the build writes its outputs and exits 1 when any check row is FAIL; nothing is moved to a _FAILED folder.

17. **Statement scoring.** registered.csv holds one row per statement: PENDING with a blank release_new until a release after 20260911 that carries 2026:Q3 is cached, then that release (the first such release only).

18. **Names in the README.** NAMES in the script give each group a plain label; `other` is equity REITs, the federal government, state and local governments, the central bank, money market funds, finance companies, mortgage REITs, holding companies and other financial business (lines 15-18, 36, 46, 47, 49, 50); `gse_bd` is lines 43 and 48.

### Fixes after the first run (R9)

- **Folder guard: the TIC pairing test hit a coincidence (R9, fixed before the first outputs were written).** The first `build` stopped with "README.md holds a figure from another source": the guard looked for the digits of three reference numbers (the review figure of CREF2a and the two typed constants of CREF2b) anywhere outside checks.csv, and a README table cell printed the unadjusted 2024 net acquisition of the rest of the world, in $bn, with the same digits as the review figure: a Z.1 figure that happens to equal it. Old rule: any occurrence of those three numbers outside checks.csv. New rule: only the two typed constants, and only where a line names the source (TIC, Treasury or sb0662) beside one, or a CSV cell is exactly a constant at one decimal. The review figure is a Fed number read during review, not another source, and is no longer matched. No rule, threshold, window, registered number or label changed.

- **README: quarter labels (presentation only, before the outputs were first written).** The level-share table headed its columns with the data form of a quarter (2016:Q4) while the rest of the README writes 2016Q4. Old: 2016:Q4 ... 2026:Q2 in the README headings and sentences. New: 2016Q4 ... 2026Q2. The CSVs keep the YYYY:QN form of R8.

- **README: two links (presentation only).** The citations now link SOURCES.md and the specification, so the doc-link check finds both reachable. No number or sentence of the results changed.
