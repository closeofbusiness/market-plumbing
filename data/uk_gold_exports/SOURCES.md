# Sources

## HM Revenue and Customs (HMRC) Overseas Trade Statistics

- URL: `https://api.uktradeinfo.com` (entity `/OTS`, lookups `/FlowType`, `/Country`, `/Commodity`); documentation https://www.uktradeinfo.com/api-documentation/. Retrieved: 2026-10-19.
- Licence: Open Government Licence v3.0 ("All content is available under the Open Government Licence v3.0, except where otherwise stated"). Contains public sector information licensed under the Open Government Licence v3.0.
- Feeds: `monthly.csv`, `annual.csv`, `revisions.csv`, `summary.csv`, the UK columns of `context.csv`, and the checks.
- Filter: CN8 (eight-digit Combined Nomenclature) codes 71080000 to 71089999, FlowTypeId 4 (non-EU exports), every partner and month; `SuppressionIndex` 0 only; `Value` is used only for the implied-price check and no sterling value is committed.
- Blank-month basis (supervisor ruling): a missing partner-month is zero only when no gold row that month is suppressed or confidential. This rests on HMRC's observed behaviour on 19 Oct 2026 (no 7108 row has ever been suppressed or under a confidential country), not on an HMRC statement.
- Provisional months: a month is provisional until 18 months after its first publication (a rule taken from the project's specification and not checked against an HMRC statement; the revisions summary measures it on real pulls). For months already in the oldest pull the first publication is approximated as the first day of the month two after it.
- Release calendar: September 2026 on 12 Nov 2026, October on 11 Dec, November on 15 Jan 2027.

## UN Comtrade public preview (Swiss mirror)

- URL: `https://comtradeapi.un.org/public/v1/preview/C` (keyless preview), reporter 757, HS (Harmonized System) 710812, partners 156 and 344, flow X; UK cross-check reporter 826, HS 710813, partner 156, 2024. Retrieved: 2026-10-19.
- Terms: UN Comtrade data are for internal use only and may not be re-disseminated in any form without the permission of the United Nations Statistics Division (UNSD), except publication of limited amounts in a few tables. Only completed-year totals per partner are committed; monthly values stay in the ignored cache.
- Feeds: `swiss_mirror_annual.csv` and the Swiss column of `context.csv`. Fields kept: `netWgt`, `isNetWgtEstimated`; a record is never dropped for `isReported` false.
- Comtrade re-publishes the Swiss customs submission; no scriptable Swiss customs route exists (the tariff-by-country file is a 690 MB archive and its terms are by request).

## Context magnitudes

- `data/gold/ledger_annual_reconciliation.csv` and `data/gold/ledger_monthly.csv` in this repository (SAFE, the State Administration of Foreign Exchange, "Official Reserve Assets"; WGC, the World Gold Council, Gold Demand Trends), read-only. The figures are copied as the ledger carries them.

## HMRC help page

- https://www.uktradeinfo.com/trade-data/help-with-using-our-data, read once by hand on the date in the build decisions below; what it confirms is in the build decisions below.

## Build decisions

- A month is `unattributable` when any 7108 non-EU-export row of that month, in any code, sits under CountryId 950 or above or carries a suppression index; the spec's "that series" is read as applying the month-level trigger to each series (the stricter reading; no such row exists on the 19 Oct 2026 pull).
- First publication for a month already in the oldest pull is the first day of the month two after it (HMRC publishes month M in month M+2). The spec's "month's end plus 2 months" taken to the day gives a different 2025-02, and only the month-level reading reproduces the spec's own statement that 2025-03 onward is provisional and 2024 is final on the 19 Oct 2026 pull.
- Sums of `NetMass` are rounded to whole kilograms in the outputs; the count of rows with fractional kilograms is in `checks.csv`.
- `summary.csv` has no `trade_system` column, so every window label carries it in square brackets, and no window crosses May 2016 except 2016 itself (`mixed`).
- A Comtrade reply that breaks a partner down by transport mode, second partner or customs procedure is reduced to its total record (modes 0, partner2 0, customs C00 where those fields exist); two total records for one partner and month stop the Swiss section as a data error.
- In the Swiss leak scan a zero is not compared with a monthly value, since zero is not a disclosure.
- The HMRC lookups are the entity sets `/FlowType`, `/Country` and `/Commodity` (the last filtered on `Cn8Code`); the spec names the facts, not the paths, and a path that fails latches the HMRC source as the spec requires.
- The cross-check of the 2024 China sums against HMRC's own group-by reply is tested with the relaxed rule that the reply names the Overseas Trade Statistics in its context and that every row is a 2024 month with a numeric `kg`.
- A STOP file holds `status`, `utc_time`, `url_path`, `retry_after` and `body_head` as five `name: value` lines; the file is created exclusively and never rewritten.
- Every number in `summary.csv` for a window is the same figure as in `annual.csv` or `context.csv`; none is a new computation across sources.
- The pinned 2024 figures in `checks.csv` fail on a pull made before HMRC's next release (12 Nov 2026) and warn afterwards; the Swiss and context pins are pass or fail only.
- The Swiss section is built from a complete Comtrade cache (monthly replies from 2012-01 and annual replies for each completed year); the first backfill of 191 requests on 19 Oct 2026 ended without a refusal.
- Fix made after the first build: a Swiss known-months cell equal to a cached monthly value was blanked after the first build, because the licence rule forbids any Swiss cell equal to a cached monthly value unless it equals a completed-year total.
- Supervisor ruling after verification: `net_mass_kg_known_months` is left blank for every Swiss partial year and every partner, not only the clashing cell, because a monthly value could otherwise be recovered by adding and subtracting the China, Hong Kong and China-plus-Hong-Kong cells of one year, and a month filled in later would show as a rise between versions. The UK columns of the same name are unaffected, since the UK source carries an open licence. In this build the blank cells are: 2012 China; 2012 China plus Hong Kong; 2020 China; 2020 Hong Kong; 2020 China plus Hong Kong; 2021 China; 2021 China plus Hong Kong; 2024 China; 2024 China plus Hong Kong; 2025 China; 2025 China plus Hong Kong.
- Supervisor ruling after verification: the Swiss leak scan reads every committed file that can carry Swiss-derived numbers, including this file, the README and `summary.csv`, for any cached Swiss monthly value (in kilograms or tonnes); it skips only the three tables of HMRC kilograms and the request log, where a coincidence with a Swiss value would not be a disclosure (the two Swiss tables are scanned column by column).
- Comtrade may leave a month out when there was no trade; the spec still leaves such years blank.
- The May 2016 date was checked against HMRC's help page, fetched once by hand (not by the script) on 19 Oct 2026 at 13:18 UTC with the neutral user agent: HTTP 200, 77,391 bytes, no redirect followed. It confirms the move from general to special trade in May 2016 and the exclusion of goods in customs warehouses.
