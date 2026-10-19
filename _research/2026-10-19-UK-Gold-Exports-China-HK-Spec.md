# Spec: UK customs declarations of semi-manufactured gold (CN 71081310) to China and Hong Kong (spec author, 19 Oct 2026; rewritten after rounds 2 and 3)

*CALENDAR.tsv row 2026-10-27, as REVISED 19 Oct (Grok g8 parcel 3, `_research/2026-10-19-Grok-G8-Returns.md`; the supervisor's check at
the top of that file outranks Grok). House style follows `_research/2026-10-19-FX-Hedged-Treasury-Yield-Spec.md`. Modelled on
`bin/build_gold_ledger.py` and `data/gold/`, which this build reads but never edits. The title follows R2-1 with R3-3's rule that the
code is named by its tariff text, never as bare "bars".*

*"Observed" means seen by the spec author on 19 Oct 2026 with the CLAUDE.md non-SEC User-Agent, one request per URL (about 40
requests, including one 403, one 500, one 429 and three 404s, each recorded below and none retried around). "Relayed" means taken
from Grok, the second review or the supervisor and not re-read here. The rulings at the end are the record; this body applies them, and
where round 3 differs from round 2, round 3 is applied. No comparison against SAFE or the WGC was computed by the spec author.*

## 0. Goal, and what the result can and cannot say

- **Measure** the net mass (kg) of non-monetary gold that UK customs export declarations send to China and to Hong Kong each month,
  from HMRC's Overseas Trade Statistics (OTS). Main series: **CN 71081310** (semi-manufactured gold: bars, rods, wire, sections, plates,
  sheets and strips over 0.15 mm). Beside it: 71081200 + 71081380 (other unwrought and semi-manufactured), and powder (71081100) as its
  own row. From May 2016 the series is **declared special-trade net mass**; before it, **general-trade net mass** (R3-2).
- **Print beside it, as separate magnitudes and never as ratios** (R3-1): Switzerland's exports of HS 710812 (unwrought) to the same
  partners for completed years; China's reported reserve change (SAFE); the World Gold Council's central-bank total.
- **It is a physical-movement series**, not the ONS change-of-ownership series, and not an upper bound on metal leaving the UK.

**It can say:** how many kilograms left the UK for China and for Hong Kong under an export declaration each month, and what the other
magnitudes were in the same windows. Everything is MEASURED (customs records) or IDENTITY (sums over ports, codes and months).

**It cannot say** who bought the gold, whether a central bank bought any of it, how much the People's Bank of China bought, or
anything about the gold price. It cannot be compared with SAFE or the WGC by ratio: HMRC records gross physical declarations, the WGC
net purchases including an estimate of unreported buying, and Hong Kong is not the PBoC's reserve account (R3-1). Gold reaches China
from Chinese mines, Switzerland and elsewhere, or changes owner in a London vault by book entry, which customs never sees. **Required
sentence (README sentence 2):** "It counts declared shipments, not buyers, and it is not a measure of central-bank buying."

## 1. Hard requirements

- **R1. Free public data only (E-005).** Script host allowlist: `api.uktradeinfo.com`, `comtradeapi.un.org`. Any other host is refused
  before the request. No FRED, no sec.gov, no API key (the Comtrade route is the keyless public preview). The one HMRC help page quoted
  for the May 2016 date (R3-2) is fetched once by the builder by hand, not by the script, and logged in Builder decisions.
- **R2. User-Agent** exactly `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)`. Assert no `@`; M10 clean.
  Never send an email address, a name, `SEC_UA` or `CLAUDE_CODE_USER_EMAIL`.
- **R3. Polite, refusal-safe fetches.** GET only, sequential, no redirect followed. HMRC at least 2 s apart, at most 12 requests a run.
  Comtrade at least 6 s apart, at most 200 a run (`--comtrade-max`). Any status other than 200, or a body that fails its content test
  (R3a), writes `data/vintages/uk_gold_exports/STOP_hmrc` or `STOP_comtrade` and ends that source's fetch. **No retry, no route around
  it. Only a person deletes a STOP file; no agent deletes one, the builder included.** With a latch present that source makes no
  request; the run prints `STOP present: <file>` and exits 2. The STOP file holds, one per line: `status`, `utc_time`, `url_path`,
  `retry_after` (the header, or blank) and `body_head` (the first 300 bytes of the body, escaped) (R2-7).
- **R3a. Content tests** (R2-7; the second review's exact wording was not in the spec author's context, so these are the spec author's
  rendering and the supervisor confirms them):
  - HMRC `/OTS`: JSON parses; `@odata.context` ends `#OTS`; `value` is a list; `@odata.count` is an integer; after pagination rows =
    count; every row has the ten fields of 2.1; every `FlowTypeId` = 4; every `MonthId` is a valid YYYYMM from 200501 to the current month.
  - HMRC lookups: FlowType 4 description (stripped) = "Non-EU Exports"; Country 720/740/39/977 present with alpha CN/HK/CH/blank; the
    7108 Commodity list = the five codes of 2.1.
  - Comtrade: JSON parses; `error` empty; `data` is a list (**an empty list is a valid reply**, recorded as no record); every record has
    `reporterCode` = the requested reporter, `flowCode` = `X`, the requested `cmdCode` and `period`, and `partnerCode` in the request.
- **R4. Never use `$orderby`** (403 on 19 Oct; not a documented option), and no `or`-chains on `CommoditySitcId` (a 500).
  `fetch_log.csv`: `utc_time, host, path_and_query, status, bytes, sha256`.
- **R5. Cache.** Raw responses go to `data/vintages/uk_gold_exports/` (gitignored), one dated file per pull.
- **R6. No causal, buyer or bound language** (G12).
- **R7. Code ownership.** `bin/uk_gold_exports.py` is new, standard library only. It reads `data/gold/ledger_annual_reconciliation.csv`
  and `data/gold/ledger_monthly.csv` read-only. No existing script changes, except a new warn-only `bin/check.sh` guard M16.
- **R8. Post-registration fixes** are logged in "Builder decisions" with the old values kept beside the new.

## 2. Data

### 2.1 HMRC Overseas Trade Statistics API (the series)

| Item | Observed 19 Oct 2026 |
|---|---|
| Base, terms | `https://api.uktradeinfo.com`, no key. Site footer: "All content is available under the Open Government Licence v3.0, except where otherwise stated". Documentation `https://www.uktradeinfo.com/api-documentation/` (200): 60 requests a minute; 40,000-item pages with `@odata.nextLink` or `$skip`; options `$select, $expand, $filter, $top, $apply, $count, $format` |
| Entity | `GET /OTS`. Fields (`/$metadata`, 200): `MonthId` (YYYYMM), `FlowTypeId`, `SuppressionIndex`, `CommodityId` (= CN8 as an integer), `CommoditySitcId`, `CountryId`, `PortId`, `Value` (£), `NetMass` (kg), `SuppUnit` |
| Flow types | 1 EU Imports, 2 EU Exports, 3 Non-EU Imports, **4 Non-EU Exports** (space-padded; strip) |
| Partners | 720 `CN` China; 740 `HK` Hong Kong; 39 `CH` Switzerland; 977 "Confidential Country" |
| Codes | 71081100 powder; 71081200 unwrought excl. powder; 71081310 semi-manufactured (bars, rods, wire, sections, plates, sheets, strips > 0.15 mm); 71081380 other semi-manufactured; 71082000 monetary gold (suppressed by HMRC, never in these figures) |
| Rows | One row per month, flow, code, partner and **port**; sum over `PortId` (2024-01 China 71081310: port 428 25,046 kg + port 434 0 kg; Grok's live read matches) |
| Units | `NetMass` whole kg (a small shipment shows 0.0). `SuppUnit` is the supplementary quantity (grams under the CN); it is not reconciled to net mass: the second review found 13% of rows with `NetMass` ≥ 100 kg disagree (R3-5). Implied price 2024-01 China: £1,306,665,011 / 25,046 kg = £52,171 per kg, about £1,623 per troy ounce |
| Coverage | First month for any 7108 row: **2005-01** (nothing earlier). Latest: **2026-08** |
| Suppression | Five documented kinds. Country-suppressed rows are **moved to CountryId 977, port 987** (seen for other goods, 2024-08), so a suppressed China row would vanish rather than carry a flag. Whole history: 7108 rows with `SuppressionIndex ne 0`: **0**; under CountryId ≥ 950: **0** |
| EU flows | 9,004 EU-export rows (FlowTypeId 2) for 7108; **0** with China or Hong Kong, by construction. Not pulled beyond one count |
| Size | 7108, FlowTypeId 4, all partners, all months: 9,667 rows, one page |
| Release | Release calendar (200): September 2026 on **12 Nov 2026**, October on 11 Dec, November on 15 Jan 2027. Provisional for up to 18 months after first publication (relayed). The API serves only the current vintage |
| Trade system | From May 2016 non-EU figures moved from general to special trade; warehouse and free-zone movements are outside special trade (relayed by Grok, who fetched HMRC's "help with using our data" page; the builder quotes it, R3-2). Before 2016-05 = `general` |

**Query forms tested on 19 Oct (all three worked here, unlike the supervisor's earlier attempt):** (1) the build's form,
`GET /OTS?$filter=CommodityId ge 71080000 and CommodityId le 71089999 and FlowTypeId eq 4&$count=true`: with `CountryId eq 720` and 2024
months it returned 11 rows summing to 382,786 kg; parentheses around `or` work. (2) `$apply=filter(...)/groupby((MonthId),aggregate(NetMass
with sum as kg))`: the same monthly sums; cross-check C05. (3) `Commodity/Cn8Code eq '71081310' and Country/CountryCodeAlpha eq 'CN'`:
2024-12 44,904 kg; not used. Form 1 returns raw rows, so ports, suppression and confidential rows stay visible.

### 2.2 Swiss mirror: UN Comtrade public preview (keyless)

- **Why this route.** FOCBS's tariff-by-country export file on opendata.swiss is 690,385,243 bytes compressed (HEAD 200, Last-Modified
  17 Sep 2026) holding **one** CSV member of over 4 GB (ranged central-directory read, 206); the gold-by-country file is imports only
  (313 MB); SwissImpex's base URL returned 404; all BAZG resources carry `terms_by_ask`. No small scriptable FOCBS route exists, so the
  mirror is "Switzerland, as reported to UN Comtrade" (O-2).
- **Request:** `GET https://comtradeapi.un.org/public/v1/preview/C/M/HS?reporterCode=757&period=YYYYMM&partnerCode=156,344&cmdCode=710812&flowCode=X`;
  one period per call (observed 400 for three). Annual check: `.../C/A/HS?...&period=YYYY`. Fields kept: `period`, `reporterCode`,
  `partnerCode`, `cmdCode`, `flowCode`, **`netWgt`** (kg), **`isNetWgtEstimated`** (stored), `primaryValue` (cache only), `isReported`,
  `isAggregate`. A record is **never dropped for `isReported` = false** (R3-6); no claim is made that `netWgt` equals `qty`.
- **Observed** (2024 and earlier are the pin months): 2024-01 China 77,807 kg, HK 44,573; 2014-01 China 12,000, HK 84,628; 2013-12 China
  11,000, HK 67,826; annual 2024 China 336,327, HK 90,145 (Grok's re-read matches). A fourth call inside 10 s returned **429**.
- **Coverage and blanks:** the first month with a record is found fetching forward from 2012-01; earlier months are `not_published`.
  Comtrade publishes no zeros and is a reporter-submitted mirror, so **a missing record is blank, never zero** (the asymmetry with HMRC
  in 3.4 is deliberate and named in the README, R2-6).
- **Revisions:** each monthly run re-fetches the latest 18 months; the first backfill (about 176 calls, about 18 minutes at 6 s) may end
  on a 429, in which case the build ships UK-only and says so (R2-12).
- **UK cross-check call (R3-8):** one annual call, `reporterCode=826&partnerCode=156&cmdCode=710813&flowCode=X&period=2024`, for C12.
- **Terms (observed):** UN Comtrade data are "for internal use only and may not be re-disseminated in any form without UNSD's
  permission", except "Publication of limited amounts of UN Comtrade data in a few tables". So **only completed-year totals per partner
  are committed** (R2-4); monthly values never leave the cache.
- **Different codes.** UK 71081310 (semi-manufactured) and Swiss HS 710812 (unwrought) are different headings. Switzerland records
  imports by origin, so Swiss imports "from the UK" are not a mirror of UK exports to Switzerland. **No UK figure is ever added to, divided
  by or compared by flag with a Swiss figure** (R3-3).

### 2.3 Context magnitudes (read from the committed gold ledger; no fetch)

- `data/gold/ledger_annual_reconciliation.csv`: `china_change_t` (SAFE-based: 2019 95.799, 2020 0.000, 2021 0.000, 2022 62.207, 2023 224.878,
  2024 44.167, 2025 26.749); `wgc_central_banks_fy_published_t` (2022 1,081.9, 2023 1,050.8, 2024 1,092.4, 2025 863.3);
  `gap_wgc_fy_published_minus_imf_t` (2024 830.336, 2025 557.257; the ledger: "not a measure of unreported buying").
- `data/gold/ledger_monthly.csv`: `china_change_t` by month, for the current-year window.
- Cited as the ledger cites them: SAFE "Official Reserve Assets"; WGC Gold Demand Trends.

## 3. Method

1. **Pull** all 7108 rows, FlowTypeId 4, every partner, every month; follow `@odata.nextLink`; FAIL if rows ≠ `@odata.count`.
2. **Code groups** (`series`): `cn71081310` = {71081310}; `other` = {71081200, 71081380}; `powder` = {71081100}, printed as its own row
   and in no other series (O-5). 71082000 is counted in `checks.csv`. Any other 7108 code is a FAIL that a person classifies.
3. **Partner-month sum** over ports and codes: `net_mass_kg` = Σ `NetMass`, and `supp_unit_div_1000` = Σ `SuppUnit` / 1,000, over rows with
   `SuppressionIndex` = 0. Partners `CN`, `HK`, `CH` (an upstream refining leg) and `ALL_NON_EU` (every partner). `CN_HK` = CN + HK.
   `supp_unit_div_1000` never enters a summary, context column or README result (R3-5).
4. **Status of a partner-month**, in order (O-1 ruling, R2-6):
   - `suppressed`: a row for that partner, series and month has `SuppressionIndex` ≠ 0 → blank.
   - `unattributable`: any 7108 FlowTypeId 4 row that month sits under CountryId ≥ 950 or has `SuppressionIndex` ≠ 0 → CN, HK, CN_HK
     **and ALL_NON_EU** blank for that series.
   - `no_rows`: no row and neither of the above → 0. This rests on HMRC's observed behaviour (OTS publishes every non-zero partner-month
     and no gold row has ever been suppressed or confidential), not on an HMRC statement; README and SOURCES say so.
   - `ok`: otherwise (including a row whose `NetMass` is 0, such as 2024-08 China).
   - `CN_HK` is blank if either part is blank, with the worse status.
5. **Trade system:** monthly `general` before 2016-05, `special` from 2016-05. Annual and window rows carry `general`, `special` or
   `mixed` (2016) (R2-8). No summary spans the break without this column (R3-2).
6. **Provisional (R3-4):** a month is provisional until 18 months after its first publication. First publication = the `vintage` date of
   the first cached pull that contains the month; for months already present in the first pull, the HMRC release date if known, otherwise
   the month's end plus 2 months (stated as an approximation in SOURCES). On the 19 Oct 2026 vintage that makes 2025-03 onward provisional
   and 2024 final.
7. **Vintages and revisions (R2-5).** Each pull is cached as `hmrc/ots_7108_f4_<YYYY-MM-DD>.json`. The previous vintage is read from the
   newest earlier dated cache file, never from the committed `monthly.csv`. Every changed partner-month cell is **appended** to
   `revisions.csv`, keyed on (vintage_prev, vintage_new, month, partner, series); existing rows are never rewritten or reordered, and a
   key already present is not written twice. With no earlier cache file, one marker row is appended with `vintage_prev` = `baseline` and
   the other cells blank. A new vintage whose latest month is earlier than the previous one is a FAIL.
8. **Annual rows:** `net_mass_kg` is the sum over the year's months; **blank when `months_blank` > 0**, with `net_mass_kg_known_months`
   (sum over the known months) beside it (R2-6). The current year is a year-to-date row with `months_n` < 12.
9. **Swiss mirror:** monthly sums per partner in the cache; committed for **completed calendar years only** (R2-4). A completed year with a
   blank month is `partial`: `net_mass_kg` blank, `net_mass_kg_known_months` filled, and `comtrade_annual_kg` and
   `monthly_sum_minus_annual_kg` blank (otherwise their difference would reveal the missing month). Current-year Swiss cells are blank.
10. **Context windows:** calendar years 2019–2025 from the ledger's annual file, and `2026_to_<L>`, L = the latest month in both the UK
    series and the ledger's monthly `china_change_t`, summed from the monthly file over the same months. Tonnes = kg / 1,000. Each
    magnitude sits in its own column; **no ratio, multiple, share or "exceeds" flag is computed anywhere** (R3-1). A UK magnitude is blank,
    with a note, when any month in the window is blank. The Swiss column is blank for 2026.
11. **`Value`** is used only for C07 (implied price); no committed column holds sterling values.

## 4. Pre-registered descriptive questions (spec only; answers go to `summary.csv`)

No hypothesis is tested, and no question compares two sources by ratio or flag. Every answer gives the full monthly or annual path with
its minimum and maximum (C-070). **`blind`** (R2-9, R3-7) is `no` for every 2024 row, every 2025 row (the second review computed 2025
figures; the spec author does not know which, so all are marked), every Q1 row, and every Q4 row (the reviewer computed the year pairs);
otherwise `yes`.

- **Q1. Path.** Monthly `cn71081310` CN, HK and CN_HK from 2005-01, with `trade_system`: minimum and maximum months; zero months per
  year 2019–2026. Notable: three or more consecutive zero months for CN after 2019 (set after the 2024 path was seen, so `blind = no`).
- **Q2. SAFE beside it.** For each year 2019–2025 and `2026_to_<L>`: `cn71081310` CN_HK and CN in tonnes, and SAFE's reported change in
  tonnes, as separate rows. No notable mark. The README's demand sentence (R2-1) gives the reader the context: Chinese jewellery, bar
  demand and mine output far exceed SAFE's reported additions, so the UK figures are expected to be larger than SAFE's.
- **Q3. WGC beside it.** 2022–2025: `cn71081310` CN_HK in tonnes, the WGC central-bank total and the ledger gap, as separate rows. No
  notable mark.
- **Q4. Destinations.** `cn71081310` CN_HK and ALL_NON_EU per year 2005–2026 with `trade_system`, as separate rows. No share and no marker
  (the earlier 20-point marker was weak, firing in about 5 of 14 year pairs on reviewer data, and is dropped with the shares).
- **Q5. The other codes.** Per year: `other` CN_HK and `powder` CN_HK beside `cn71081310` CN_HK, as separate rows. No notable mark.
- **Q6. Switzerland beside the UK.** Per completed year from the first Swiss year: Swiss HS 710812 CN_HK and UK CN 71081310 CN_HK, each
  labelled with its code. No ratio and no "UK exceeds Switzerland" flag (R3-3).
- **Q7. Revisions.** At each new vintage: cells changed, largest absolute change (kg), and any change to a month that was no longer
  provisional at the previous vintage. Notable: any such change.
- **Q8. The 2016 break.** `cn71081310` CN_HK for 2015 (`general`), 2016 (`mixed`) and 2017 (`special`), and the January–April 2016
  months. The 2015-to-2017 fall straddles the change of recording system and is probably not like-for-like; the earlier fall in January
  to April 2016 is described, not explained (R2-8, R3-2).

## 5. Outputs

**Script `bin/uk_gold_exports.py`.** Modes `fetch`, `build` (offline, byte-identical on re-run) and `selftest` (synthetic, no network,
under 20 s). Committed files sit in `data/uk_gold_exports/` and begin with one `# source:` line.

**Header allowlist (R2-10), canonical text.** One line per file, `<name>:<headers comma-joined, no spaces>`, each line ending in LF
(including the last), in this order. The script holds `SPEC_ALLOW_SHA256`; G11 and M16 skip the `# source:` line and compare.

```
monthly.csv:month,partner,series,net_mass_kg,supp_unit_div_1000,rows_n,status,trade_system,provisional,vintage
annual.csv:year,partner,series,net_mass_kg,net_mass_kg_known_months,months_n,months_blank,trade_system,provisional_months,vintage
swiss_mirror_annual.csv:year,partner,hs6,net_mass_kg,net_mass_kg_known_months,months_n,months_blank,net_wgt_estimated_months,status,comtrade_annual_kg,monthly_sum_minus_annual_kg
context.csv:window,months,months_blank,trade_system,uk_71081310_cn_hk_t,uk_71081310_cn_t,uk_71081310_hk_t,swiss_710812_cn_hk_t,safe_reported_change_t,wgc_central_banks_t,wgc_minus_imf_gap_t,note
revisions.csv:vintage_prev,vintage_new,month,partner,series,kg_prev,kg_new,change_kg,provisional_at_prev
summary.csv:question,window,partner,series,statistic,value,blind,notable
checks.csv:check_id,description,expected,observed,status
fetch_log.csv:utc_time,host,path_and_query,status,bytes,sha256
```

**sha256 of that text (913 bytes): `966c81ab0f63f5dc04100f57f83ae3af9df4cb80e4e4dcd2d9376f214be65796`** (computed by the spec author).

Values: `partner` ∈ {CN, HK, CN_HK, CH, ALL_NON_EU}; `series` ∈ {cn71081310, other, powder}; `status` (monthly) ∈ {ok, no_rows,
suppressed, unattributable}; `trade_system` ∈ {general, special, mixed}; `provisional` ∈ {yes, no}; `vintage` = pull date; kg as
integers, tonnes to 3 decimals, `supp_unit_div_1000` to 3 decimals. Swiss `partner` ∈ {CN, HK, CN_HK}, `status` ∈ {complete, partial}.

- **`README.md`** (generated, so G12 scans it), in this order, each term defined at its first use (R2-12):
  1. Two opening sentences: "This table counts the kilograms of gold that UK customs export declarations sent to China and Hong Kong
     each month, from HMRC trade statistics. It counts declared shipments, not buyers, and it is not a measure of central-bank buying."
  2. **What it leaves out:** London vault transfers (book entry, never a customs record; this is a physical-movement series, not the ONS
     change-of-ownership series); **the May 2016 break**: from then on warehouse and free-zone movements are outside the figures, so it
     is not an upper bound, ceiling or cap on metal leaving the UK, and earlier months are general trade and not like-for-like (with
     HMRC's quoted sentence, or "date relayed, not verified"); monetary gold (suppressed by HMRC, never here); other routes into China;
     onward movement from Hong Kong.
  3. Why the figures are not compared with SAFE or the WGC by ratio (R3-1's three reasons), and the demand sentence (R2-1).
  4. The latest result: annual tonnes 2019 to date with `trade_system`; Swiss completed years and the context magnitudes in separate tables.
  5. Blank months: HMRC absence is zero under the observed-behaviour rule; Comtrade absence is blank (the named asymmetry).
  6. Column dictionary, with CN 71081310 by its tariff text; `supp_unit_div_1000` labelled "supplementary quantity ÷ 1,000 (grams under
     the CN), not reconciled to net mass"; a note that WITS-published quantities are supplementary quantities and differ from net mass
     by kilograms (China 2024: 382,802 against 382,786 kg, relayed by Grok).
  7. One worked row: 2024-01 China CN 71081310 from its two port rows.
  8. Provenance last: OGL v3.0 attribution (HMRC); "UN Comtrade" with the limited-amounts basis and the first-backfill note; SAFE and WGC
     as the gold ledger cites them.
  The questions of section 4 are not in the README.
- **`SOURCES.md`:** each source, URL, licence, access date, the columns it feeds, the O-1 basis and the first-publication approximation.

**Cache (gitignored, `data/vintages/uk_gold_exports/`):** `hmrc/*.json`, `comtrade/<YYYYMM>.json` and annual files, `swiss_monthly.csv`
(`month, partner, net_wgt_kg, is_net_wgt_estimated, primary_value_usd`), the STOP files.

## 6. Licence and leak rules

1. HMRC-derived kilograms are committed (OGL v3.0, attribution in README and SOURCES).
2. **Swiss-derived values** live only in `swiss_mirror_annual.csv` and the `swiss_710812_cn_hk_t` column of `context.csv`, for completed
   years only. G10 checks those two places (R2-3): no cell there may equal a cached Swiss monthly `netWgt` (as kg, or as tonnes to 3
   decimals) unless it also equals that partner's completed-year total, and no current-year Swiss cell may be filled.
3. No raw response, `primaryValue` or sterling `Value` in the committed folder; only the eight CSVs, README and SOURCES (G11, M16).
4. The context magnitudes are copied from committed ledger files only.

## 7. Pinned checks (`checks.csv`)

Pins are **one-vintage checks** (R3-4): on a vintage pulled before HMRC's next release (12 Nov 2026) a mismatch is FAIL; on a later
vintage it is WARN plus the `revisions.csv` rows that explain it (HMRC's unscheduled corrections can rewrite old years).

- **C01 2024 `cn71081310`:** CN 382,786 kg; CH 305,087; HK 26,044.
- **C02 2024 by code:** 71081200 CN `no_rows`, CH 3,000, HK 17; 71081380 CN 1, HK 14, CH 63; so `other` CN 1, HK 31; `powder` HK 1.
- **C03 2024 China `cn71081310` by month:** 01 25,046; 02 20,017; 03 41,750; 04 35,634; 05 50,194; 06 `no_rows`; 07 `no_rows`; 08 0 (`ok`);
  09 60,595; 10 54,715; 11 49,931; 12 44,904.
- **C04 Coverage:** first month 2005-01; nothing earlier; latest month ≥ 2026-08; row count ≥ 9,667 (WARN if lower).
- **C05 Cross-check:** the `$apply` groupby for 2024 China equals C03.
- **C06 Suppression census:** 7108 rows with `SuppressionIndex` ≠ 0 and under CountryId ≥ 950, printed (0 and 0 on 19 Oct); every
  `unattributable` month listed.
- **C07 Implied price only (R2-2):** rows from 2016-05 with `NetMass` ≥ 100: `Value / NetMass / 32.1507466` in [150, 6,000] £ per troy
  ounce; WARN per outlier, FAIL above 1% of such rows. 2024-01 China: £1,623 per ounce.
- **C07s SuppUnit census (WARN only):** the count and share of rows with `NetMass` ≥ 100 whose `SuppUnit / NetMass` lies outside
  [990, 1,010]. Expected about 13% (second review). Never a FAIL, never a headline.
- **C08 Lookups:** as R3a.
- **C09 Swiss pins (R2-3): PASS/FAIL only; `expected` and `observed` left blank** (the values are Comtrade monthly data). Months 2024-01,
  2014-01 and 2013-12, and annual 2024, as listed in 2.2; `flowCode` X. Completed-year monthly sum minus annual record is in
  `swiss_mirror_annual.csv`.
- **C10 Context pins:** ledger `china_change_t` 2024 44.167, 2025 26.749; WGC 2024 1,092.4, 2025 863.3; monthly `china_change_t` summed
  over each calendar year equals the annual figure within 0.01 t.
- **C11 Fixed output:** a second `build` leaves every sha256 unchanged, `revisions.csv` included (no row appended twice).
- **C12 UK against Comtrade's UK record (R3-8), INFO:** 2024 UK net mass to China, 71081310 + 71081380 (382,787 kg), against Comtrade's
  reporter-826 `netWgt` for HS 710813, partner 156; INFO, with the gap in kg, flagged if over 2 kg.

## 8. Selftests (synthetic only; each guard applies its own mutant, and an uncaught mutant fails the selftest)

| Guard | Protects | Mutant that must be caught |
|---|---|---|
| G1 port sum | Σ over ports | first row per partner-month kept (fixture: 25,046 + 0, and a three-port month) |
| G2 blank rules | 3.4, 3.8–3.10, 2.2 | HMRC absence written blank; a month with a 977 gold row written 0 for CN; ALL_NON_EU filled in an `unattributable` month; a `NetMass` 0 row given `no_rows`; an annual `net_mass_kg` filled with `months_blank` > 0; a context UK magnitude filled over a blank month; a missing Comtrade month written 0 |
| G3 suppression | `SuppressionIndex` 0 only | a CN row with index 5 kept |
| G4 code groups | 3.2 | 71082000 in `cn71081310`; `powder` added to `other`; unknown 71081390 silently dropped |
| G5 flow sign | FlowTypeId 4, `flowCode` X | FlowTypeId 3 or 2 admitted; a lookup labelling 4 "Non-EU Imports" accepted; Comtrade `M` admitted |
| G6 partners | 720/740/39 | 39 mapped to CN; CN_HK filled with HK blank |
| G7 no cross-route sum | 2.2 | a committed number equal to UK CH + Swiss CN, or UK CN_HK + Swiss CN_HK (unique fixture sums) |
| G8 units, no ratios | kg, t = kg/1,000; R3-1 | `NetMass` read as tonnes; t = kg/1,000,000; any committed column whose name contains `multiple`, `ratio`, `share`, `_over_`, `pct` or `exceed`, or any value equal to a quotient of two committed magnitudes (fixture chosen so quotients are unique) |
| G9 vintages, provisional | 3.6, 3.7 | an existing `revisions.csv` row rewritten or reordered; a key appended twice; `kg_prev` lost; previous vintage read from `monthly.csv`; no `baseline` row on the first vintage; provisional measured from the newest month instead of first publication (fixture: a month first published 2026-11-12 is provisional on 2028-05-11 and final on 2028-05-13); an earlier latest month accepted |
| G10 Swiss leak | 6.2 only | a Swiss monthly kg in `swiss_mirror_annual.csv`; the same as tonnes in `context.csv`; a current-year Swiss cell filled; a partial year with `comtrade_annual_kg` filled. **Run on a planted bad folder (must report each) and on the clean folder (must pass)** |
| G11 allowlists, folder | 5, 6.3 | an extra or renamed column; `SPEC_ALLOW_SHA256` ≠ sha256 of the canonical text; a raw `.json` or an eleventh file in the folder; the `# source:` line compared as a header |
| G12 wording | R6 | causal words ("caused", "drove", "driven", "because of", "led to", "pushed", "in response to"; `bin/hedged_ust_yield.py`'s `CAUSAL_RX` copied, not imported); buyer phrases (`(unreported\|hidden\|secret\|undisclosed\|covert)\s+(central[- ]bank\s+\|official\s+\|PBoC\s+)?(buying\|purchases\|demand)`, `(PBoC\|central[- ]bank)s?\s+(bought\|buying\|purchases)`); bound words (`\bceiling\b`, `\bcaps?\b`, `\bcapped\b`, `\b(upper\s+)?bound(s\|ed)?\b`) anywhere except the one README sentence of 5.2 that denies them. Bare "bars" as a series label. The two opening sentences must pass; with "is a measure of central-bank buying" they must fail; a second "ceiling" sentence must fail |
| G13 fetch safety | R1–R4 | a non-allowlisted host; `@` in the UA; `$orderby`; a redirect followed; HMRC under 2 s or Comtrade under 6 s; a 429 retried; a 13th HMRC request; an empty Comtrade `data` list treated as a failure |
| G14 STOP latch | R3 | static: the script contains `os.remove`, `os.unlink`, `os.replace`, `os.rename`, `shutil.rmtree`, `shutil.move`, `Path.unlink` or `Path.rename` applied to a STOP path. **Runtime (R2-11):** with a planted `STOP_comtrade`, `fetch` makes no Comtrade request, exits 2, and the STOP file is byte-identical (sha256) afterwards; a STOP written by a fixture 503 carries the five fields of R3 |
| G15 pagination | 3.1 | `@odata.nextLink` ignored; rows ≠ count accepted |
| G16 windows | 3.10 | SAFE Jan–Sep against UK Jan–Aug; a 2026 Swiss cell filled |
| G17 break | 3.5 | `general` missing for 2016-04; 2016 annual not `mixed`; a Q8 or Q4 row without `trade_system` |
| G18 blind | section 4 | a 2024 row, a 2025 row, a Q1 row or a Q4 row marked `blind = yes` |

## 9. Success criteria

1. `python3 bin/uk_gold_exports.py selftest` prints G1–G18, every mutant caught, exit 0.
2. `fetch` makes at most 12 HMRC requests and at most `--comtrade-max` Comtrade requests, all logged, with no STOP written. If a STOP is
   written, the builder stops that source and tells the supervisor; the UK series still builds.
3. `build`: C01–C06, C08–C11 PASS; C12 INFO. **Acceptable WARNs** (R2-12): C04 if the row count is lower with a reason; C07 outliers under
   1%; C07s always; any pin on a vintage after 12 Nov 2026 (with its `revisions.csv` rows). Every other WARN is reported to the supervisor.
   A `summary.csv` row for every question of section 4, with `blind` filled.
4. A verifier re-derives one number by hand from the cache: 2024 CN_HK `cn71081310` = 408,830 kg (382,786 + 26,044).
5. `bin/check.sh --all`: the existing ✓ lines plus warn-only **M16** (`data/uk_gold_exports/`: the ten names, headers against the canonical
   text skipping `# source:`, no Swiss monthly value in the two Swiss places, no raw file, none of G12's bound words outside the denial
   sentence). On a scratch copy with a planted Swiss monthly value, a planted `.json` and a renamed header it prints three ✗ lines; on the
   clean folder ✓.
6. **README cold-reader test:** two fresh agents, a non-specialist and a precious-metals practitioner, read only the README. A reader who
   comes away believing it measures central-bank buying, bounds Chinese buying or metal leaving the UK, or compares with SAFE as a share,
   fails the README.

**Landing (builder):** `.gitignore` rule for `data/vintages/uk_gold_exports/`; REPRODUCE.md paragraph; CALENDAR row 2026-10-27 re-dated to
a monthly row without the word "ceiling" (after each HMRC release, next 12 Nov 2026: `fetch`, `build`, read `revisions.csv`); HANDOVER row.
The builder commits nothing; the supervisor verifies and writes any findings text.

## 10. OPEN questions

- **O-1 RULED:** absence is zero only when no gold row that month is suppressed or confidential; otherwise blank. Basis stated in README.
- **O-2 OPEN: Swiss primary source.** Comtrade re-publishes the Swiss submission; a one-off check of two months against SwissImpex
  (manual) or the 690 MB FOCBS file (once, outside the repository) would confirm it.
- **O-3 OPEN: Comtrade quota.** Undocumented; a 429 after four calls in 10 s. If the preview refuses, the UK series ships alone.
- **O-4 OPEN: the 18-month rule** is relayed; Q7 measures it on real vintages.
- **O-5 RULED:** powder stays out of both series and is printed as its own row.
- **O-6 OPEN:** Hong Kong onward flows (C&SD) and China Customs gold imports are out of scope.
- **O-7 OPEN:** 2024 Swiss exports to China imply about $2,166 per troy ounce, below the year's market average; unused here, unexplained.
- **O-8 CLOSED by the supervisor, 19 Oct: R3a stands as written (it is stricter than the second review's tests and keeps an empty Comtrade `data` list valid); every 2025 row is `blind = no`.** Original text: The second review's wording for the content tests (R2-7) and its list of
  computed 2025 rows (R2-9) were not in the spec author's context; R3a and section 4 are renderings the supervisor confirms.

## Supervisor rulings, 19 Oct 2026 (before any data run)

- **O-1:** a missing partner-month counts as zero only when no gold row that month is suppressed or under a confidential country; otherwise
  the month is blank. This rests on HMRC's observed behaviour (no gold row has ever been suppressed or confidential), not on an HMRC
  statement, and the README and SOURCES say so; the guard that blanks the month stays.
- **O-5:** gold powder (71081100) stays out of both series and is printed beside them as its own row.
## Supervisor rulings, round 2 (second review), 19 Oct 2026 — before any data run

All twelve required fixes from the second review are accepted, with these rulings:

- **R2-1 "ceiling" is dropped everywhere.** Title becomes "UK customs declarations of gold bars to China and Hong Kong". The spec file is renamed `UK-Gold-Exports-China-HK-Spec.md`. No column or file name says ceiling, cap or bound; G12 bans those words outside one README sentence that denies them. Q2's notable is replaced by the reviewer's wording ("not a contradiction, reported without comment"). The README carries the demand sentence (Chinese jewellery, bar demand and mine output far exceed SAFE's reported additions, so UK figures are expected to exceed SAFE's).
- **R2-2 C07** becomes the £/oz test only (rows from 2016-05, NetMass ≥ 100, range 150 to 6,000); SuppUnit is a WARN-only ratio census and is not called grams.
- **R2-3 C09 commits PASS/FAIL only**, pins only months outside the revision window (2024 or earlier). G10 is scoped to Swiss-derived files and columns.
- **R2-4 Swiss figures are committed for completed calendar years only.** Current-year Swiss cells are blank. No Swiss monthly path anywhere.
- **R2-5 `revisions.csv` is append-only**, keyed on (vintage_prev, vintage_new, month, partner, series); previous vintage read from the dated cache file; absent = `baseline`.
- **R2-6 Blank months:** `net_mass_kg` blank when months_blank > 0, with `net_mass_kg_known_months` beside it; context multiples blank with a note when any month in the window is blank; the same rule for Swiss partial years. `ALL_NON_EU` in an unattributable month is blank. The UK/Comtrade asymmetry stays and is named in the README: a missing HMRC partner-month is zero under O-1 (HMRC publishes every non-zero partner-month and never suppressed gold); a missing Comtrade record is blank, because Comtrade is a reporter-submitted mirror and absence there is not evidence of zero.
- **R2-7 Content tests** as the reviewer wrote them; empty Comtrade `data` is a valid reply. The STOP file records status, time, Retry-After and the first 300 bytes; no retry.
- **R2-8 The 2016 break:** the builder cites an HMRC page for the date if one is found by fetching gov.uk; otherwise the README says "date relayed, not verified". `annual.csv` gains `trade_system` (`general`, `special`, `mixed`). Q8 says the 2015-to-2017 fall straddles the change and is probably not like-for-like.
- **R2-9 `blind` column** in `summary.csv`: `no` for every 2024 row (the author and reviewer saw them) and for 2025 rows the reviewer computed; Q4's 20-point marker is described as weak (fires in about 5 of 14 year pairs on reviewer data).
- **R2-10 Header allowlist:** one line per file, `<name>:<comma-joined headers, no spaces>`, LF, section-5 order; sha256 printed in the spec by its author; G11/M16 skip the `# source:` line.
- **R2-11 G14** adds os.replace, shutil.rmtree, Path.rename/unlink and a runtime test (STOP file byte-identical after `fetch`).
- **R2-12 Minor points** accepted; 9.3 names the acceptable WARNs; the README says the first Comtrade backfill (~18 minutes) may end on a 429 and ship UK-only.
- **CALENDAR row 2026-10-27** is reworded to drop "ceiling" when the spec is committed.
## Supervisor rulings, round 3 (Grok attack, g9), 19 Oct 2026 — before any data run

Grok's live January 2024 China row (port 428, 25,046 kg; port 434, 0 kg) and the 2024 Swiss Comtrade pins match the spec and the second review. Where Grok and the second review differ, the stronger rule is taken:

- **R3-1 No ratios.** `uk_bars_cn_hk_over_safe_multiple`, `uk_bars_cn_hk_share_of_wgc_pct` and every "exceeds" or "share above 100%" flag are dropped (this supersedes R2-1's kept multiples). SAFE's reported change and the WGC official-sector total are printed as separate magnitudes for the same years, in their own columns, with no ratio. Reasons, from HMRC's and the WGC's own definitions: HMRC records gross physical declarations, the WGC net purchases including an estimate of unreported buying, and Hong Kong is not the PBoC's reserve account. R2-1's README demand sentence stays.
- **R3-2 Name and trade system.** The series is "declared special-trade net mass of CN 71081310" (from May 2016) and "general-trade net mass" before. The README says that from May 2016 warehouse and free-zone movements are out, so it is not an upper bound on metal leaving the UK, and that it is a physical-movement series, not the ONS change-of-ownership series. The builder quotes HMRC's "help with using our data" page for the May 2016 date (Grok fetched it); this resolves R2-8 if the quote is found, and the data's earlier fall (Jan to Apr 2016) is described, not explained. No long series is summarised across the break without the `trade_system` column.
- **R3-3 Goods codes.** CN 71081310 is labelled by its tariff text (semi-manufactured: bars, rods, wire, sections, plates), never bare "bars". Q6 prints UK 71081310 and Swiss HS 710812 (unwrought) as separate magnitudes with their codes; no UK/Swiss ratio and no "UK exceeds Switzerland" flag.
- **R3-4 Provisional months.** A month is provisional until 18 months after its first publication (not 18 months before the newest month). Pins are one-vintage checks: on the pinned vintage a mismatch is FAIL; on a later vintage it is WARN plus a `revisions.csv` row (HMRC's unscheduled corrections can rewrite old years).
- **R3-5 Supplementary units.** `monthly.csv` carries `supp_unit_div_1000` beside `net_mass_kg`, labelled "supplementary quantity ÷ 1,000 (grams under the CN), not reconciled to net mass" (the second review found 13% of rows with net mass ≥ 100 kg disagree). It never enters a headline.
- **R3-6 Comtrade fields.** Keep `netWgt`, store `isNetWgtEstimated`, never drop a row for `isReported = false`; no claim that `netWgt` equals `qty`.
- **R3-7 The Q1 three-zero-month notable** was set after the 2024 path was seen: `blind = no` on every Q1 row.
- **R3-8 README notes:** monetary gold (71082000) is suppressed by HMRC and never in these figures; WITS-published quantities are supplementary quantities and differ from net mass by kilograms (Grok's reference: 382,802 vs 382,786 kg, China 2024). A cross-check row compares UK net mass (bars plus 71081380) with Comtrade's UK `netWgt` for 2024 within 2 kg, as INFO.
