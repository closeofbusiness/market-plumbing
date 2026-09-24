# NYSE / Exchange-Agnostic Dividend Payment-Date Scout

**Status: VERIFIED NO** (no free *at-scale* payment-date source for NYSE / all-US equities 2015–2026)

**Date:** 2026-09-16 (Europe/Berlin)  
**Scout only** — do not rebuild B6; do not invent an M; no handover write.  
**machineId:** 56a83289-aaaa-453d-a7c7-aa768bd566bb  
**Question:** Does a free NYSE (or exchange-agnostic) dividend **payment-date** source exist at scale for US listed equities (ideally S&P 500 / NYSE names 2015–2026), usable without paid CRSP/Compustat?

**At-scale bar (this note):** historical 2015–2026; NYSE or all-US in bulk/API/download (not one-ticker manual pages); free / no paid login; no bot-detection defeat; field must be **payment date** (not only ex/record).

---

## Verdict (one-liner)

**VERIFIED NO** — after checking the candidate list plus search, no free source clears the at-scale bar for calendar-true NYSE payment dates 2015–2026; Tier B resolution limit remains under **E-005**.

---

## Context (why this matters)

B6 Phase 1 (`2026-09-15-B6-Phase1-Payment-Day-Mechanism.md`) **FAILS kill switch** on calendar-true Nasdaq payment dates. ~78% of S&P500 events lacked true payment dates because the free Nasdaq calendar mostly covers Nasdaq-listed names; NYSE used lag imputation. A free NYSE/payment-date source at scale would allow a proper re-run; absence names the resolution limit.

---

## Candidate scorecard

| # | Candidate | URL | Free? | Historical 2015–2026? | NYSE coverage? | Bulk method | Pay-date field? | Verdict |
|---|-----------|-----|-------|----------------------|----------------|-------------|-----------------|--------|
| 1 | Nasdaq dividend calendar API | `https://api.nasdaq.com/api/calendar/dividends?date=YYYY-MM-DD` | Yes (no key) | Yes — day queries return rows back to at least 2015 (probed) | **No / thin** — see below | Day-by-day JSON | Yes (`payment_Date`) | **FAIL** for NYSE unblock |
| 1b | Nasdaq per-symbol dividend history | `https://api.nasdaq.com/api/quote/{SYM}/dividends?assetclass=stocks` | Yes | Nasdaq-listed history deep | **Explicitly no** for non-Nasdaq | Per ticker | Yes (`paymentDate`) when available | **FAIL** |
| 2 | NYSE / ICE Corporate Actions of NYSE Group Listings | Product: https://www.nyse.com/data-products/catalog/corporate-actions-for-nyse-group-listings ; samples: https://ftp.nyse.com/Corporate%20Actions%20Data%20Samples/CORPORATE%20ACTIONS%20OF%20NYSE%20GROUP%20LISTINGS/ ; spec PDF | **Samples only free**; full product is paid client (SFTP/S3/email; `sftp.nyse.com` archives) | Paid archives yes | Yes (NYSE, American, Arca, Texas) | Paid SFTP/HTTP client feed | Yes (sample row has declare/record/ex/pay date fields; e.g. pay `06/10/2024` for CLCO) | **FAIL** (not free at scale) |
| 2b | NYSE Market Event Feed (MEF) API | Factsheet / `datasales@nyse.com` | Paid / sales contact | Limited historical window on product sheet | NYSE Group | API (subscriber) | Corporate actions incl. dividends | **FAIL** |
| 3 | SEC EDGAR XBRL payment-date tags | Taxonomy: `us-gaap:DividendPayableDateToBePaidDayMonthAndYear` (+ record/declared siblings); Notes bulk: https://www.sec.gov/data-research/sec-markets-data/financial-statement-notes-data-sets ; Companyfacts per CIK | Yes (public; UA required) | Tags exist in Notes back through XBRL era | Exchange-agnostic *when tagged* | Quarterly Notes ZIPs (`txt.tsv`) | Yes when filer tags it | **FAIL** for scale (sparse voluntary tagging) |
| 4 | OpenFIGI | https://www.openfigi.com/api/documentation | Free mapping tier | N/A | ID mapping only | Mapping API | **No** dividends | **FAIL** |
| 5 | Yahoo Finance | Chart `events=div`; quoteSummary (crumb-gated) | Free chart | Ex-date history deep | All US | Per ticker chart JSON | Chart events: **ex-date + amount only** (`date`,`amount`) — no pay date | **FAIL** |
| 5b | Stooq | https://stooq.com | Free pages | Prices | US symbols | CSV prices | No payment-date corporate-actions feed found; JS/bot wall on probe | **FAIL** |
| 6 | Dividend.com / Seeking Alpha / Nasdaq.com web | Various | Page views free; no free bulk API; scraping against ToS / partner data | Per-ticker pages | Mixed | Manual / scrape (disallowed here) | Pages may show pay dates | **FAIL** (no free bulk; do not scrape) |
| 7 | Federal Reserve / FRED | e.g. aggregate dividend series | Yes | Macro aggregates | Not security-level | FRED CSV/API | No per-equity pay dates | **FAIL** |
| 8 | GitHub open dividend datasets | e.g. `userFRM/divkit`, `chonito7919/DivScout`, Yahoo scrapers | Often open license | Amounts / period dates | US SEC filers | Parquet/CSV | **Explicitly no pay/ex/record** in SEC-XBRL kits; Yahoo kits = ex-dates | **FAIL** |
| — | Alpha Vantage `DIVIDENDS` | https://www.alphavantage.co/query?function=DIVIDENDS&symbol=IBM&apikey=… | Free key (≤~25 req/day) | Demo IBM shows multi-year `payment_date` | NYSE works in paid/full key path (IBM) | Per-ticker JSON | Yes | **FAIL at-scale** (rate limit; key signup; not bulk download) |
| — | BusinessQuant Dividends API | https://businessquant.com/docs/api/dividends | Free plan (docs: ~30 calls/day) | Docs claim 14+ years + `payment_date` | Docs claim stocks generally | Per-ticker JSON | Yes (`payment_date`) | **FAIL at-scale** (free rate limit) |
| — | EODHD `/api/div/` | https://eodhd.com/financial-apis/api-splits-dividends | Free plan **1 year history only**; paid for 30y | Free fails 2015–2026 | Major US JSON includes `paymentDate` (demo AAPL) | Per-ticker / paid bulk | Yes on major US (JSON) | **FAIL** (free history cap) |
| — | Finnhub stock dividends | Finnhub docs | Dividends marked **Premium** | N/A free | — | — | paymentDate on premium | **FAIL** |
| — | Barchart / Benzinga calendars | Vendor APIs | Paid keys | Vendor-dependent | Explicit NYSE filters on some | Paid API | payable dates on paid products | **FAIL** (paid) |

---

## Evidence notes (probes this scout)

### 1. Nasdaq calendar — NYSE hole confirmed

- Day calendar schema includes `payment_Date`, `record_Date`, `dividend_Ex_Date`, `symbol`, … (probed `2024-06-03`, 107 rows).
- Exchange sample on that day (Yahoo `fullExchangeName` on ~25 symbols): **only NasdaqGM/GS/CM** — zero NYSE in sample.
- On Yahoo ex-dates for **JPM** (2024–2025) and **KO** (2025), Nasdaq calendar rows for those symbols were **empty**.
- May 2024 scan: **JPM/KO/XOM/IBM = 0** calendar hits; **AAPL/MSFT/WMT = 1** each (sporadic; not reliable NYSE coverage).
- Per-symbol API for **JPM**: message **"Dividend History for Non-Nasdaq symbols is not available"**; all fields N/A.
- Nasdaq.com JPM dividend-history HTML: **"Please note Dividend History is only available for Nasdaq-listed symbols"** / "Dividends are currently not available."

→ Confirms B6’s ~78% true-pay-date gap for S&P500 (NYSE-heavy).

### 2. NYSE / ICE — right fields, wrong license

- Public FTP path is explicitly **“Corporate Actions Data Samples”**.
- Sample `EQY_US_NYSEGROUP_DISTRIBUTIONS_20240522_154500.txt` is pipe-delimited NYSE Group distributions with multiple date columns including a **payment date** (field index 15 on sample rows).
- Historical archive paths in the client spec (`/EQY_US_NYSEGROUP_DISTRIBUTIONS/...`) live on **authenticated** `sftp.nyse.com`, not the open samples folder (`https://ftp.nyse.com/EQY_US_NYSEGROUP_DISTRIBUTIONS/` → 404).
- Product page: commercial delivery (email/SFTP/website download for **clients**).

### 3. SEC XBRL — free but not bulk-usable for B6

- Companyfacts for **JPM, KO, IBM, AAPL**: **zero** `DividendPayableDateToBePaidDayMonthAndYear` / record / declared date tags.
- SEC Notes `2024q1_notes.zip` (UA: `ThirdDerivativeResearch/1.0`):
  - Tag present in `tag.tsv`.
  - `txt.tsv` raw count ≈ **1055** facts for `DividendPayableDateToBePaidDayMonthAndYear`.
  - **244 unique CIKs** that quarter; forms mostly 10-K.
  - Mega-cap set (JPM/KO/IBM/AAPL/…) **absent**; only a few large names (e.g. Microsoft, Disney) among taggers.
- Frames API for that concept returned 404 / non-JSON.
- Open-source SEC dividend kits (`divkit`, DivScout) document the same gap: amounts/period ends yes; **ex/record/pay dates not in structured SEC feeds at usable completeness**.

→ Free and bulk-downloadable Notes exist, but **tagging is voluntary and far too sparse** for S&P500 × ~10y payment-day panel.

### 5. Yahoo — ex-dates only (reconfirmed)

- `v8/finance/chart/JPM?...&events=div`: dividend event keys = `{date, amount}` only (ex-date semantics, as used in B6).

### Free keyed APIs that *look* close (still fail “at scale”)

- **Alpha Vantage `DIVIDENDS`**: fields include `payment_date`; IBM demo returns deep history. Free tier ≈ **25 calls/day** → ~500 S&P names need weeks of sequential pulls; not a free bulk dump; requires API key registration.
- **BusinessQuant**: documents `payment_date` + 14y history; free plan ≈ **30 calls/day** — same scale failure.
- **EODHD**: `paymentDate` on major US JSON (demo AAPL 2015–2026 visible with demo token) but **free plan limited to 1 year** of history — fails 2015–2026 without pay.

These are **not** treated as PASS/PARTIAL for unblocking B6 under the stated free at-scale bar.

---

## Overall status rationale

| If we needed… | Result |
|---------------|--------|
| Free Nasdaq payment dates for Nasdaq-listed names | Already have (B6 calendar-true sample) |
| Free NYSE / all-US payment dates 2015–2026 at S&P500 scale | **Not found** |
| Paid NYSE ICE distributions / CRSP / Compustat / EODHD paid / AV premium | Exist — out of scope |

Closest *commercial* free-tier teases (AV / BusinessQuant) still fail throughput and “no paid upgrade” longevity for a research-grade panel. Closest *public* structured source (SEC Notes pay-date tags) fails coverage completeness.

---

## Implication for B6

- **Do not re-run B6 Phase 1** expecting calendar-true NYSE payment dates from free data — the missing source was scouted and is **absent at scale**.
- **Stop** mechanism-claim extension; keep “do not invent an M”.
- Name Tier B’s resolution limit under **E-005**: free-data payment-date identification is **Nasdaq-calendar–bounded**; NYSE/S&P500-wide true pay dates require paid corporate-actions (e.g. NYSE Group Distributions / CRSP) or accepting lag imputation (already rejected as primary).

---

## Probe artifacts (box)

`/workspace/nyse-paydate-scout/` — Nasdaq/Yahoo JSON, NYSE sample TXT, SEC `2024q1_notes.zip` (local), HTML snippets.

SEC fetches used User-Agent: `ThirdDerivativeResearch/1.0`. No bot-detection defeat; no paid products purchased.
