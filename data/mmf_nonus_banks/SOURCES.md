# Sources, access record and builder decisions: US money funds' claims on non-US financial institutions

Specification: `_research/2026-10-25-MMF-NonUS-Banks-Spec.md (committed at da6f335, supervisor rulings rounds 1 to 4)`. Build script: `bin/mmf_nonus_banks.py`. Vintage: OFR release updated 2026-10-15, data as of 2026-09-30, retrieved 2026-10-25.

## 1. Source and licence

Office of Financial Research, OFR U.S. Money Market Fund Monitor, built from SEC Form N-MFP, refreshed monthly: https://www.financialresearch.gov/money-market-funds/ . The data are read from the monitor's chart files (`/money-market-funds/data/credit_risks_country/.../data.json`), crawled politely under the principal's ruling E-027 (requests at least 2 s apart, the neutral User-Agent, a STOP latch on any 403, 429 or other non-200, no retry), and from four series of the OFR API (`MMF-MMF_TOT-M`, `MMF-MMF_RP_wFFI-M`, `MMF-MMF_RP_wFICC-M`, `MMF-MMF_RP_wDFI-M`). The complete-dataset zip is never requested.

OFR Legal Notices (observed 25 Oct 2026): "No copyright may be claimed for any work on this website that was created by a federal employee in the course of his or her duties. However, credit is requested". The monitor footnote says the parent and country mapping draws on "regulatory filings, company disclosures and commercial data", so raw JSON stays in the gitignored cache and committed files are derived aggregates and the OFR's parent names with countries. Citation: Office of Financial Research, "OFR Money Market Fund Monitor", refreshed monthly, https://www.financialresearch.gov/money-market-funds/. `robots.txt` (observed) does not disallow `/money-market-funds/` or `/assets/`.

## 2. Requests

- Spec author, 25 Oct 2026, 14:06-14:25 UTC, the CLAUDE.md non-SEC User-Agent, one request per URL: 32 requests, 31 returning 200 and one 403.
- `www.financialresearch.gov` (27 requests): `/money-market-funds/`, its three chart pages, `/robots.txt`, `/about/policies/`, `/legal-notices/`, `/short-term-funding-monitor/datasets/mmf/`, three `/assets/js/mmf/` scripts, `asof.json`, `updated.json` and 13 node files (two of them the encoding tests): all 200.
- `/money-market-funds/data/mmf_data.zip`: **403 `AccessDenied`** (CloudFront/S3, 111 bytes), not retried. It is never requested by this build.
- `data.financialresearch.gov` (3 requests): the mnemonic list, `MMF-MMF_TOT-M`, `MMF-MMF_RP_wFFI-M`: all 200.
- `www.bis.org`: the CGFS Paper 65 PDF, 200. `catalog.data.gov/dataset/form-n-mfp-data-sets`: 200.
- This build's crawl: 1007 requests for vintage 2026-10-15 (budget 3000), 996 chart files plus `asof.json`, `updated.json` and the four API series; the full record is `fetch_log.csv`.

## 3. Drill levels and literal maps

Drill levels (monitor metadata): Category (MFS002), Region (MFS019), Country (MFS009), Sector (MFS006), Credit, i.e. ultimate parent (MFS008), Asset Type (MFS005). Measure MFS015, assets under management, USD. A path segment is the child's display name, lower-cased, whitespace replaced by `_`, percent-encoded as JavaScript's `encodeURIComponent`.

- Fund categories and lineages: Prime = prime; Prime Institutional = prime; Prime Retail = prime; Government = government; Government (No Fees & Gates) = government; Government (Fees & Gates) = government; Tax Exempt = tax_exempt; Tax Exempt Institutional = tax_exempt; Tax Exempt Retail = tax_exempt
- Regions in the literal table: Asia, Australia, Europe, North America, South America, Supranational, Africa. Sectors: Financial Institution, Government, Non-Financial Corporate, Municipal, Other.
- Country labels in the literal table: Austria, Belgium, Bulgaria, Croatia, Cyprus, Estonia, Finland, France, Germany, Greece, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Netherlands, Portugal, Slovakia, Slovenia, Spain, Sweden, Norway, Denmark, UK, Switzerland, Japan, Canada, USA, China, India, Israel, Singapore, South Korea, Australia, New Zealand, Chile, Venezuela, Mexico, Tunisia, Ukraine, Jordan, Kuwait, Malaysia, Philippines, Qatar, Saudi Arabia, Taiwan, Turkey, United Arab Emirates.
- Euro area (2026 membership, every date): Austria, Belgium, Bulgaria, Croatia, Cyprus, Estonia, Finland, France, Germany, Greece, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Netherlands, Portugal, Slovakia, Slovenia, Spain. NORDIC: Sweden, Norway, Denmark. AUNZ: every country under region Australia. OTHER_ASIA: every other country under region Asia. Region Supranational is excluded from every non-US total.
- Asset types seen: Treasury Repurchase Agreement -> repo_treasury; Government Agency Repurchase Agreement -> repo_agency; Other Repurchase Agreement -> repo_other; Certificate of Deposit -> cd; Financial Company Commercial Paper -> fin_cp; Asset Backed Commercial Paper -> abcp; Other Note -> other_note; Other Instrument -> other_note; Non-Financial Company Commercial Paper -> misc; U.S. Treasury Debt -> misc; Government Agency Debt -> misc.
- Relayed asset-type labels (N-MFP investment categories, not seen in OFR JSON when the spec was written; mapped as listed and flagged by C13b if seen): Non-Negotiable Time Deposit -> time_deposit; Variable Rate Demand Note -> misc; Other Municipal Security -> misc; Tender Option Bond -> misc; Insurance Company Funding Agreement -> misc; Investment Company -> misc; Other Asset Backed Securities -> misc; Non-U.S. Sovereign, Sub-Sovereign and Supra-National Debt -> misc; Non-U.S. Sovereign, Sub-Sovereign and Supra-National debt -> misc.

## 4. CGFS Paper 65 (BIS, June 2020), quotes with printed page numbers

- p 20: "now obtain less funding from US MMFs"
- p 35: "some non-US banks significantly reduce their matched book repo activity at quarter-ends"
- p 67: "mainly via overnight repos from US MMFs"
- pp 67-68: "have become the most important repo counterparties to French banks"
- p 73: "are not subject to the quarter- or year-end balance sheet constraints"
- p 27: "has shortened considerably"
- The paper does not single out Japanese and Canadian banks as money-fund dependent. Its money-fund charts (Graph 14, p 28) use Crane Data, which is not free.

## 5. Disclosure

What was seen of the answer before any build: the spec author saw the pinned node levels and, from the OFR API, the aggregate "repo with foreign financial institutions" series (MMF-MMF_RP_wFFI-M), including its 2011-16 noise and its 2017Q1-2026Q2 dip spread. The second reviewer computed that aggregate's calendar and Canadian-fiscal dips and the history of statement S1 on it (9 of 9). No country-group statistic had been computed. The `blind` marks follow from this: every ALL_NONUS `secured` and `headline` row is marked not blind.

## 6. Builder decisions

1. **Crawl set (reading of 2.3).** The frontier is one function, `needed()`, used by `fetch` and by `build`: the root; each category with a nonzero month; each region with a nonzero month; each country with a nonzero month, USA included (its file lists the sectors); the `Financial Institution` file of every non-US country with a nonzero financial-institution month; the asset-type file of every non-US parent with a nonzero month except a child named exactly "Aggregated small issuers"; and, for FICC, the USA `Financial Institution` file of a category only where the chain category, region, USA, Financial Institution is nonzero in the files already read (so no file the OFR may not serve is requested). The region `Supranational` is fetched as a region file but its countries are not drilled (it is outside every total). No US parent and no non-financial sector is drilled.
2. **Latches.** Any STOP file in the cache stops the whole fetch before a request, not only that source's: the strict reading. The budget counts every request of the vintage across resumed runs, both `updated.json` fetches included; the 3,001st attempt writes `STOP_budget`.
3. **Slices.** `fetch --max-requests N --max-seconds S` ends a run in an orderly way (exit 3) so the crawl fits a tool timeout; the next run resumes from the manifest. A socket fault is logged with status `socket_fault`, nothing is latched (exit 4). Exit codes: 0 complete, 2 STOP or release changed or data error, 3 slice ended, 4 socket fault, 5 refused.
4. **Cache and log layout.** Each vintage folder holds its files (named by the sha256 of the URL path), `manifest.csv`, `requests.txt` and its own `fetch_log.csv`; requests outside any vintage (an `updated.json` read when the vintage was already complete, a removed partial crawl) go to `fetch_log_other.csv`. The committed `fetch_log.csv` is the concatenation of all of them. The retrieval date in each `# source:` line is the latest date in the vintage's own log. `manifest_sha256` is the sha256 of the manifest lines sorted by URL path, so it does not depend on the order files landed.
5. **Headline and unallocated.** The headline is the `Financial Institution` series of the non-US country's own file; the instrument groups come from the parent files; `unallocated` is the "Aggregated small issuers" child. C16 compares the two routes, so it is not an identity by construction.
6. **Stable pins and revisions.** A stable pin that differs from the spec's value WARNs if the same cell differs between this vintage and the previous complete vintage (a revision), else FAILs; the comparison is made on the node cell itself because `revisions.csv` holds country-level cells, not node cells. A recent pin FAILs on vintage 2026-10-15 and WARNs on later ones. C07 follows the recent-pin rule.
7. **Quarter-end implementation.** (a) AUNZ rows are also written on the jp_march, jp_other and ca_fiscal bases so that the paired difference is computed on the same basis and months from rows in the file. (b) `qe_summary.csv` covers the windows `post_reform` and `pre_reform`; `transition` is in no summary (F8) and `after_freeze` has no computed fall. (c) When a standard error is zero and the mean is zero, `pattern` is `neither`. (d) `frozen_set` is `yes` for quarters up to 2026Q2 (all windows but `after_freeze`). (e) `quarter_ends.csv` carries the four measures of Q3 (headline, bank_only, secured, unsecured); MEMO_FICC has headline only. (f) The literal `blind` rule marks any row containing a 2026-06 or later month-end `no`, so every calendar and jp_other summary whose window includes 2026Q2 is `no`. (g) The noise reference of a basis row is that of the group and window (it does not depend on the basis's months).
8. **summary.csv.** Q1 and Q2 are for fund lineage `all`: the grammar has no lineage column, and `levels_group.csv` holds every lineage in every month. For lineage `all`, `pct_of_lineage_total` equals `pct_of_mmf_total`. Q6 rows carry the two vintage dates in `from_month` and `to_month`; the month and country of the largest change are found in `revisions.csv`. Q7 is the hit rate as a share of the 9 year-ends, 2017-2025 (the count is in `checks.csv`, row S1).
9. **levels_group.csv** holds every group, lineage, measure and month, zeros included, so that the nine-groups-sum-to-ALL_NONUS test sees every cell.
10. **Extra checks.** `checks.csv` also holds C01c to C01e (the API comparison), C13b, C17 (node identities), C18 (category lineages), C19 (nine groups, shares), C20 (vintage order), C21 (the neighbour rule) and S1. Pin ids carry letters.
11. **Kind table.** Keyed by (parent, country); the sha256 is taken over the lines `parent|country|kind\n`. 138 parents are classified; the table and its review date follow. Reviewed by the supervisor: 25 Oct 2026. `KIND_TABLE_SHA256` in the script: `372706934150e78332604721c1efde76cdd0b07b09015d4ed8159eec6e6c491b`; the table in this build hashes to `372706934150e78332604721c1efde76cdd0b07b09015d4ed8159eec6e6c491b`.
12. **Labels added after the first vintage (O-10, round 4).** region Africa (seen in the 2026-10-15 vintage: holds Tunisia only; its countries fall under OTHER); sector Municipal (seen in the 2026-10-15 vintage under the USA only; the USA is outside every non-US total and only its Financial Institution file is read); sector Other (seen in the 2026-10-15 vintage under the USA only; the USA is outside every non-US total and only its Financial Institution file is read); country Chile (seen in the 2026-10-15 vintage under South America; OTHER); country Jordan (seen in the 2026-10-15 vintage under Asia; OTHER_ASIA); country Kuwait (seen in the 2026-10-15 vintage under Asia; OTHER_ASIA); country Malaysia (seen in the 2026-10-15 vintage under Asia; OTHER_ASIA); country Mexico (seen in the 2026-10-15 vintage under North America; OTHER); country Philippines (seen in the 2026-10-15 vintage under Asia; OTHER_ASIA); country Qatar (seen in the 2026-10-15 vintage under Asia; OTHER_ASIA); country Saudi Arabia (seen in the 2026-10-15 vintage under Asia; OTHER_ASIA); country Taiwan (seen in the 2026-10-15 vintage under Asia; OTHER_ASIA); country Tunisia (seen in the 2026-10-15 vintage under the new region Africa; OTHER); country Turkey (seen in the 2026-10-15 vintage under Asia (the OFR's region, not a geographic choice of ours); OTHER_ASIA); country Ukraine (seen in the 2026-10-15 vintage under Europe; OTHER (not euro area, not NORDIC)); country United Arab Emirates (seen in the 2026-10-15 vintage under Asia; OTHER_ASIA); country Venezuela (seen in the 2026-10-15 vintage under South America; OTHER)
13. **Supervisor rulings after stage 1 (25 Oct 2026), applied.** (1) Kind rule: every public development, agency or export-credit lender is `other_fin`, whether or not it holds a banking licence, because it takes no deposits from the public (Bank Nederlandse Gemeenten, Nederlandse Waterschapbank, NRW.Bank, Oesterreicheische Kontrollbank, KfW, Kommunalbanken, Japan Finance Corp, Eksportfinans, Swedish Export Finance). Macquarie (its group includes the deposit-taking Macquarie Bank), Natexis + Natixis and Sumitomo Trust stay `bank`; Nomura, Daiwa, the asset-backed commercial paper conduits (Albion, Northcross, Zephyr) and Suncorp stay `other_fin`. Every judgement call is marked in the Note column of the kind table below. (2) The exact serialization hashed for `KIND_TABLE_SHA256`: one line per classified parent, `parent|country|kind` followed by one line feed, UTF-8, the rows sorted by (parent, country) in Unicode code-point order, no header and no final blank line; the sha256 of that byte string. (3) The unknown labels were accepted and mapped as listed under "Labels added" (by region: Africa, the 14 countries, the USA sectors Municipal and Other; the lower-case "Supra-National debt" asset type to `misc`). (4) The six readings of this list (the crawl set, the whole-fetch latch, the pin revision test, summary.csv for lineage `all`, the literal blind rule, AUNZ rows on every basis) were accepted.
14. **Edits to the script after the first vintage was fetched (25 Oct 2026, before any `build`).** (a) The builder-added labels above and the kind table (the report of `kinds` was the first sight of them). (b) The spelling variant "...Supra-National debt" of a relayed asset-type label, mapped to `misc` as the spec lists the label and flagged by C13b. (c) A faster number-formatting routine (`qfix`, `dstr`) with identical output, re-proved by the selftest. (d) `S1_N_FROZEN` set to the first build's value, 6.215782929260888, as spec 4.5 requires (old value `None`; the build had printed N = 6.2158, the spec author's proxy 6.22). No rule, threshold, window or spec label was changed. Before the fetch: `parse_node` was made to turn any malformed-body error into a content failure (a STOP latch) rather than an exception.
15. **S1.** N, the clean-month sd of ALL_NONUS `secured` in `post_reform` (before dividing by the square root of 2), is frozen in the script (S1_N_FROZEN) at 6.2158. Historical hit rate: 9 of 9 year-ends.
16. **Honesty note on S1 (spec 4.5).** At 9 of 9 on the proxy a HELD is near-certain, so S1 checks that a known pattern persists and carries little information.

### Kind table

The kinds rest on the builder's knowledge of each institution (relayed, not an OFR field); a note marks each judgement call.

| Parent | Country | Kind | Note |
|---|---|---|---|
| ABB Ltd. | Switzerland | other_fin |  |
| ABN AMRO | Netherlands | bank |  |
| Abu Dhabi International Bank I | United Arab Emirates | bank | name read as a bank; no further information in the OFR file |
| Agricultural Bank of China | China | bank |  |
| Albion Capital | Australia | other_fin | name and instrument mix (asset-backed commercial paper) read as a funding vehicle; counted other_fin |
| Allianz | Germany | insurer |  |
| Alternative Bank Switzerland AG | Switzerland | bank |  |
| Asian Development Bank | Philippines | other_fin | multilateral lender, not a bank under any national law; counted other_fin |
| Australia & New Zealand Banking Group | Australia | bank |  |
| Axa SA | France | insurer |  |
| Axis | India | bank |  |
| BNP Paribas | France | bank |  |
| Banco Bilbao Vizcaya Argentaria | Spain | bank |  |
| Banco Santander | Spain | bank |  |
| Banco de Credito e Inversiones | Chile | bank |  |
| Banco del Estado de Chile | Chile | bank |  |
| Banesco | Venezuela | bank |  |
| Bank Baroda | India | bank |  |
| Bank Hapoalim | Israel | bank |  |
| Bank Leumi | Israel | bank |  |
| Bank Nederlandse Gemeenten | Netherlands | other_fin | public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence) |
| Bank of Australia | Australia | bank | name read as a bank; no further information in the OFR file |
| Bank of China | China | bank |  |
| Bank of India | India | bank |  |
| Bank of Ireland | Ireland | bank |  |
| Bank of Montreal | Canada | bank |  |
| Bank of New Zealand | New Zealand | bank |  |
| Bank of Nova Scotia | Canada | bank |  |
| Bank of Tokyo-Mitsubishi | Japan | bank |  |
| Banque et Caisse | Luxembourg | bank |  |
| Barclays | UK | bank |  |
| Bayerische Hypo Vereinsbank | Germany | bank |  |
| Bayerische Landesbank | Germany | bank |  |
| Brookfield Holdings Canada Inc. | Canada | other_fin |  |
| Caisse Centrale Des Jardins | Canada | bank |  |
| Canadian Imperial Bancorp | Canada | bank |  |
| Canadian Pacer Auto Recievables Trust | Canada | other_fin |  |
| Chiba Bank | Japan | bank |  |
| China Construction Bank | China | bank |  |
| Cic Eurosecurities, Inc. | France | other_fin | US broker-dealer subsidiary that the OFR maps as its own parent; counted other_fin |
| Commerzbank | Germany | bank |  |
| Commonwealth Bank of Australia | Australia | bank |  |
| Credit Agricole | France | bank |  |
| Credit Industriel | France | bank |  |
| Credit Mutuel | France | bank |  |
| Credit Suisse | Switzerland | bank |  |
| DBS Bank | Singapore | bank |  |
| DNB | Norway | bank |  |
| DZ Bank AG | Germany | bank |  |
| Daiwa Securities Group Inc | Japan | other_fin |  |
| Danske Bank | Denmark | bank |  |
| Depfa Bank | Germany | bank |  |
| Deutsche Bank | Germany | bank |  |
| Dexia | Belgium | bank |  |
| Eaton Capital UnLtd Co | Ireland | other_fin |  |
| Eksportfinans | Norway | other_fin | public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence) |
| Erste Bank | Austria | bank |  |
| Experian Finance PLC | UK | other_fin |  |
| Firstmac Mortgage | Australia | other_fin |  |
| Glencore | Switzerland | other_fin |  |
| Global Lending Services LLC | Japan | other_fin | non-bank lender; counted other_fin |
| Groupe BPCE | France | bank |  |
| HSBC | UK | bank |  |
| Hana Financial Group | South Korea | bank |  |
| Helaba | Germany | bank |  |
| ING Groep Nv | Netherlands | bank |  |
| ITOCHU Corporation | Japan | other_fin |  |
| Icici Bank Limited | India | bank |  |
| Industrial & Commercial Bank of China Ltd. | China | bank |  |
| Intesa | Italy | bank |  |
| Israel Discount Bank of New York | Israel | bank |  |
| Japan Finance Corp | Japan | other_fin | public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence) |
| KBC Groep Nv | Belgium | bank |  |
| KFW | Germany | other_fin | public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence) |
| Kommunalbanken | Norway | other_fin | public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence) |
| Kookmin Bank | South Korea | bank |  |
| LA BANQUE POSTALE | France | bank |  |
| Landesbank Baden-wuerttemberg | Germany | bank |  |
| Lloyds | UK | bank |  |
| London Stock Exchange Group | UK | other_fin |  |
| London Stock Exchange Group plc | UK | other_fin |  |
| Louis Dreyfus | Netherlands | other_fin |  |
| Macquarie | Australia | bank | the group includes the deposit-taking Macquarie Bank; kept as a bank by supervisor ruling |
| Maybank | Malaysia | bank |  |
| Mirae Asset Financial Group | South Korea | other_fin |  |
| Mizuho | Japan | bank |  |
| NRW.Bank | Germany | other_fin | public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence) |
| NatWest Group | UK | bank |  |
| Natexis + Natixis | France | bank | the BPCE group's corporate and investment bank, a licensed French credit institution; kept as a bank by supervisor ruling |
| National Australia Bank | Australia | bank |  |
| National Bank of Abu Dhabi | United Arab Emirates | bank |  |
| National Bank of Canada | Canada | bank |  |
| National Bank of Kuwait | Kuwait | bank |  |
| Nationwide Building Society | UK | bank |  |
| Nederlandse Waterschapbank | Netherlands | other_fin | public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence) |
| Nomura Securities | Japan | other_fin |  |
| Norddeutsche Landesbank | Germany | bank |  |
| Nordea | Sweden | bank |  |
| Norinchukin Bank | Japan | bank |  |
| Northcross Capital | UK | other_fin | same: funding vehicle; counted other_fin |
| Novo Holdings A/S | Denmark | other_fin |  |
| OMERS Finance Trust | Canada | other_fin |  |
| OP Financial Group | Finland | bank |  |
| Oesterreicheische Kontrollbank Ag | Austria | other_fin | public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence) |
| Oversea Chinese Banking | Singapore | bank |  |
| Pepper Group | UK | other_fin |  |
| Prudential Plc | UK | insurer |  |
| RWE AG | Germany | other_fin |  |
| Rabobank | Netherlands | bank |  |
| Reckitt Benckiser | UK | other_fin |  |
| Resimac | Australia | other_fin |  |
| Roche Holdings | Switzerland | other_fin |  |
| Royal Bank of Canada | Canada | bank |  |
| Royal Bank of Scotland | UK | bank |  |
| SBAB Bank AB | Sweden | bank |  |
| Shinhan Bank | South Korea | bank |  |
| Shizuoka Bank | Japan | bank |  |
| Skandinaviska Enskilda Banken | Sweden | bank |  |
| Societe Generale | France | bank |  |
| Standard Chartered Bank | UK | bank |  |
| State Bank Financial | India | bank | name read as a bank; no further information in the OFR file |
| State Bank of India | India | bank |  |
| Sumitomo Mitsui Bank | Japan | bank |  |
| Sumitomo Trust | Japan | bank | trust bank (deposit-taking); kept as a bank by supervisor ruling |
| Suncorp | Australia | other_fin | financial conglomerate (insurance and, until a sale, a bank); neither bank nor insurer fits every date, so other_fin (relayed knowledge, not checked at source) |
| Svenska Handelsbanken | Sweden | bank |  |
| Swedbank | Sweden | bank |  |
| Swedish Export Finance | Sweden | other_fin | public development, agency or export-credit lender; other_fin by supervisor ruling (it takes no deposits from the public, whatever its licence) |
| TP ICAP | UK | other_fin |  |
| The Commercial Bank of Qatar | Qatar | bank |  |
| Toronto Dominion | Canada | bank |  |
| UBS | Switzerland | bank |  |
| Unicredit | Italy | bank |  |
| United Overseas Bank | Singapore | bank |  |
| Westpac | Australia | bank |  |
| Wintek Ltd | China | other_fin | non-financial company; counted other_fin |
| Zephyr Financiere Inc. | Canada | other_fin | same: funding vehicle; counted other_fin |
| Zurich Cantonal Bank | Switzerland | bank |  |
