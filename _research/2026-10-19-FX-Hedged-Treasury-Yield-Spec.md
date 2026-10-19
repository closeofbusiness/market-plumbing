# Spec: rolling-hedge carry on the 10-year Treasury for yen and euro investors (spec author, 19 Oct 2026; rewritten after two reviews)

*Candidate X1 of `_research/2026-10-19-CGFS65-Dollar-Funding-Reading.md`. It completes the hedging cost that ST1
(`2026-10-15-ST1-Swap-Spreads-Inflation-Gap-And-Basis.md`) left half-measured: ST1 has the basis but not the short-rate gap. House style
follows `_research/2026-10-18-FX-Rate-Gap-Weekly-Spec.md` and `_research/2026-10-15-ICE-Brent-COT-Spec.md`.*

*This text folds in the supervisor's eleven rulings on Grok's attack and on a second Sonnet review. The log at the end lists each
change; the body is authoritative. "Observed" means seen on 19 Oct 2026, with one request per URL and the CLAUDE.md non-SEC User-Agent:
41 requests in all, the redirect hops and two 403s included. "Relayed" means taken from a review or a search result and not re-read here.
Real-data values marked "reviewer" are the second reviewer's re-derivations; the builder reproduces them as pins. The spec author
computed no carry series on real data.*

## 0. Goal, and what the result can and cannot say

- **Measure** the rolling 3-month carry of a currency-hedged 10-year Treasury for a yen-based and a euro-based investor. That is the
  Treasury yield plus the annualised gain or loss of a 3-month currency hedge that is rolled. **Compare** it with the home 10-year
  government yield: the JGB for yen, and the ECB AAA curve for euro (3.1). **Decompose** it as Treasury yield + rate-gap term + basis term.
- **Headline:** the locked 3-month forward, built from 3-month OIS rates and the 3-month cross-currency basis, monthly. OIS is the
  overnight-index swap (fixed rate against the compounded overnight rate). The euro headline starts Oct 2024. The yen headline starts
  in the first month with a published median (3.5).
- Beside it: the plain-subtraction form that publishers use; a 1-year-hedge variant; and three diagnostics. Of those, spot overnight
  (A) is the only series with long history (yen from Apr 2018, euro from Oct 2019).
- **Label everywhere:** "rolling 3-month carry" (or "rolling 1-year carry"). Never "the yield an investor earns" over ten years.

**It can say:** the hedged carry and the pickup over the home yield by month, in each form and construction; how much of the hedge
cost is the rate gap and how much is the basis; and how close the build comes to published figures. The carry is IDENTITY given its
inputs, the inputs are MEASURED, and agreement with references is MEASURED.

**It cannot say** that the pickup caused, drove or explains any purchase, sale, hedge ratio, flow or price. It cannot give the return
from holding a hedged bond to maturity, which depends on ten years of future short rates (CFR, 18 Mar 2024). Nor can it give any
investor's own hedge cost. The required sentence: **"This measures an incentive. It does not show what led any investor to buy, sell
or hedge."**

## 1. Hard requirements

- **R1. Free public data only (E-005). No FRED, Bloomberg or sec.gov.**
  - The host allowlist for `bin/hedged_ust_yield.py`: `home.treasury.gov`, `www.mof.go.jp`, `data-api.ecb.europa.eu`,
    `markets.newyorkfed.org`, `www.stat-search.boj.or.jp`, `jschreger.s3.us-east-2.amazonaws.com`, `api.statistiken.bundesbank.de`.
    Any other host is refused before the request is made.
  - This script never reads DTCC files. It reads only the ledger's committed monthly output (R6, 3.5).
- **R2. User-Agent** exactly `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)`. Assert there is no `@`
  and that M10 is clean. Never send an email address, a name, `SEC_UA` or `CLAUDE_CODE_USER_EMAIL`.
- **R3. Polite, refusal-safe fetches** (the fx_rate_gap R3 rules).
  - GET only, sequential, at least 2 s apart, at most 30 per run (about 20 expected), and no redirect followed.
  - Any status other than 200 (206 for the DKS probe), or a body that fails its content test, writes
    `data/vintages/hedged_ust_yield/STOP` and ends the run. Only a person deletes it, and nothing retries.
  - `fetch_log.csv` records `utc_time, host, path, status, bytes, sha256`.
- **R4. Cache.** Raw files and every daily or yen-monthly series go to `data/vintages/hedged_ust_yield/` (gitignored). Committed files
  follow section 7.
- **R5. No causal language** (G14). The required sentence of section 0 is the one exemption.
- **R6. Code ownership.** `bin/hedged_ust_yield.py` is new and stdlib only. It imports `bin/fx_rate_gap.py` parsers read-only.
  `bin/swap_tape_ledger.py` gains a **monthly stage** (3.5). That is the only change to an existing script, and it runs under E-024.
- **R7. Staleness.** Each input has a maximum age (C12). A stale input ends its series at its last date with a WARN. Nothing is
  forward-filled.
- **R8. Validation gate.** Section 5. A miss beyond the gate is a FAILED build: outputs go to `data/hedged_ust_yield/_FAILED/` and
  the exit code is 1.

## 2. Data

| Leg | Request | Field, units, day count | Timing | Observed |
|---|---|---|---|---|
| US 10y | Treasury CSV, fx_rate_gap `TSY_PATH`, Y = 2018–2026 (9 requests) | `10 Yr` **by name** (the 2025–26 files add `1.5 Month`); % par, semiannual | ~15:30 New York (relayed) | 10/15/2026 5.10 (reviewer) |
| JGB 10y | `www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv` and `.../interest_rate/jgbcme.csv` (2) | `10Y`, % semiannual; `-` is missing; footer note lines skipped | 15:00 Tokyo, published the next business day (relayed) | current month 200, 1,349 bytes, 2026/10/1 3.092; curve starts at 1Y |
| Euro 10y | fx_rate_gap `YC_PATH`, `startPeriod=2018-01-01` (1) | AAA Svensson parameters; 10y par **recomputed semiannual** (`fx_rate_gap.ea_semiannual`), so it is labelled derived | `TIME_PERIOD` acts as the price date | relayed: 2026-09-18 3.533452 |
| SOFR, EFFR | `markets.newyorkfed.org/api/rates/secured/sofr/search.csv?startDate=2018-04-01&endDate={today}` and `.../unsecured/effr/search.csv?startDate=2018-01-01&endDate={today}` (2) | `Rate (%)` by header, ACT/360, newest row first, `MM/DD/YYYY` | the rate for D is published the next business morning (latest at 05:33 ET Mon 19 Oct: 10/15) | 2018-04-02 1.80; 2026-10-15 3.89; EFFR 3.88 |
| SOFR Index | `.../api/rates/secured/sofrai/search.json?startDate=2020-03-02&endDate={today}` (1) | `index` | the index dated D uses SOFR up to D−1 | 2026-10-16 1.26303308 |
| €STR | `data-api.ecb.europa.eu/service/data/EST/B.EU000A2X2A25+EU000A2QQF08.WT+CI?format=csvdata&startPeriod=2019-10-01` (1) | `.WT` %, ACT/360; `.CI` compounded index (1 Oct 2019 = 100) | trade date T, published T+1 08:00 CET | 2019-10-01 −0.549; 2026-10-16 2.441; CI 2026-10-19 110.03236357 |
| TONA | `www.stat-search.boj.or.jp/api/v1/getDataCode?format=csv&lang=en&db=FM01&code=STRDCLUCON&startDate=201801` (1) | % p.a., ACT/365. The header block reads `STATUS,200`, `MESSAGEID,M181000I`, `NEXTPOSITION,`. The series name is a quoted field with a comma. `null` on non-business days | final rate the next business day (relayed); the API lags further (O-8) | 20180104 −0.047; 20261015 1.228; 16–19 Oct null at 18:33 JST |
| 3m and 1y OIS, xccy basis | `data/swap_tape/monthly_short_tenor.csv` (committed by the ledger's monthly stage, 3.5) | % for OIS medians, bp for basis, with n and status | month of execution (UTC) | the file does not exist yet |
| Check: all-in carry (DKS) | `jschreger.s3.us-east-2.amazonaws.com/cip_dataset_v4.csv`: probe = a ranged GET of bytes 0–65535 (206), every fetch. The 118,471,039-byte body only if `dks_3m_1y.csv` is missing from the cache, or with `--dks-full` | Du-Keerati-Schreger panel, header `group,currency,tenor,date,diff_y,rho,cip_govt,cip_govt_break_date,rho_ibor,rho_sofr,cip_govt_ibor,cip_govt_sofr`; dates `08feb2007` | daily to June 2025 (relayed) | 206; Last-Modified 31 Oct 2025; ETag `eb058f21fd563d35e00644bdb42120a1-7` |
| Check: Bund 10y | fx_rate_gap `BBK_PATH` (1) | Bundesbank Svensson 10y | basis and time OPEN (fx_rate_gap O-1) | relayed |

**Not used.**
- *Term bills.* Japan has no free 3-month government point, and bills trade at a spread to OIS.
- *TIBOR, Euribor, Term SOFR, TORF, QUICK TONA averages.* Licensed benchmarks.
- *EONIA and pre-€STR.* Not in the ECB EST dataflow; EONIA was not checked (O-6).
- *Bloomberg forward points.* Paid.
- *Per-start-date basis.* Not feasible: only 3 yen days reach n ≥ 10 (reviewer).

**Licences (read 19 Oct unless marked).**
- **Treasury.** US government work (relayed).
- **MoF.** PDL 1.0 per the notice page. Commercial use is allowed with attribution, and numerical data are outside copyright
  (Digital Agency text, relayed).
- **ECB.** Free use if the ECB is cited and the data appear accurately; modifications must be stated. The ESCB reuse policy (relayed
  by Grok) asks for statistics to be left unmodified, so the recomputed AAA par is labelled "derived from ECB statistics (recomputed
  on a semiannual basis)". The €STR page says the ECB "does not charge for the €STR or license its use" (relayed).
- **NY Fed.** `/privacy/termsofuse`: use and distribution are allowed with the fixed reference-rate notice (section 6), modified
  content must be labelled, and distributed content carries the same terms.
- **BoJ.**
  - Site copyright page: copying is allowed with the Bank credited, but commercial copying is excluded.
  - API notice (`stat-search.boj.or.jp/info/api_notice_en.pdf`, 200): a user who "releases a service which uses the API" should
    notify the Research and Statistics Department by email, and show the credit "This service uses the API provided by the "Bank of
    Japan Time-Series Data Search." The Bank of Japan does not guarantee the content of the service." (O-1b)
- **Bundesbank.** Index page only; terms relayed. A check only.
- **DKS.** The data page asks for three citations; redistribution is not stated, so the panel is restricted and stays in the cache.
- **DTCC.** E-024: non-commercial, derived statistics only, DTCC cited, raw files outside the repository. The monthly stage extends
  the ledger itself (ruling 4).

## 3. Method

### 3.1 Definitions and sign convention (the README carries these)

- **Hedging cost.** What a rolled currency hedge costs per year: the gap between the dollar and the home short rate over the hedge
  tenor, plus any premium that dollar borrowers pay on top of it. The rate-gap term and the basis term below are minus that cost.
- **Cross-currency basis (b), labelled "US-reported cross-currency swap median".** The spread on the yen or euro overnight-rate leg of
  a swap against flat SOFR, in bp, as on the DTCC tape and in ST1. **Negative b means a premium to borrow dollars, and it lowers the
  carry.**
  - It is a median of currency-swap prints. It is **not** FX-swap forward points, which dominate turnover: in April 2025, FX swaps
    were $4,015bn a day against $164bn for currency swaps (BIS, relayed by Grok).
- **Hedged carry (h).** The Treasury yield plus the annualised forward gain or loss of the rolled hedge. **Pickup = h − home 10-year
  yield.**
- **Euro benchmark: ECB AAA, not the Bund.** Its licence was read, its compounding and timing are documented (fx_rate_gap), the
  Bundesbank series' basis is open, and the Bundesbank terms could not be read. The Bund is a check (C13).

### 3.2 Arithmetic: two forms

- **Bond-basis form (H).** For a tenor of D days:
  - R = (G_home + (b/10000)·D/B_home) / G_us, with B_us = 360 (SOFR, EFFR) and B_home = 365 (TONA) or 360 (€STR);
  - c = 100·ln(R)·365/D;
  - y_c = 200·ln(1 + y_us/200);
  - **H = 200·(exp((y_c + c)/200) − 1)**, a semiannual rate like y_us and the home yields.
  - Exact decomposition: with h0 = H at b = 0, `rate_gap_term` = h0 − y_us and `basis_term` = H − h0.
- **Plain-subtraction form (P)**, as TD Economics defines it ("US-10 year – (US 3 month – Japan 3 month)", observed) and as Ginnie Mae
  uses it (10-year yield minus the 1-year hedge cost, observed): `rate_gap_term` = −(o_us − o_home), with rates as quoted and no
  day-count change, and `basis_term` = b/100, **shown separately**.
- **Both forms.** h = y_us + rate_gap_term + basis_term, and pickup = h − y_home. `form_gap_bp` = 100·(H − P) is reported for every
  month that has both.
- **Fixtures** (3-month OIS construction, D = 92, y_us 4.50, SOFR-OIS 4.30):
  - yen: TONA-OIS 0.50, b −20 → H 0.4144953188, rate_gap_term −3.8851920011, basis_term −0.2003126801; P 0.50; form gap −8.55bp;
  - euro: €STR-OIS 2.00, b −5 → H 2.0972732816 and P 2.15;
  - 1-year (D = 365, SOFR 4.00): yen TONA 0.80, b −15 → H 1.1256986972 and P 1.15; euro €STR 2.10, b −3 → H 2.5680226188 and
    P 2.57.

### 3.3 Headline: the locked forward (C), 3-month and 1-year

- For each month m: G = 1 + o_m·D/(100·B), where o_m is the month's published OIS median for the tenor. These are single-payment
  swaps, so simple interest. b_m is the month's basis median for the same tenor.
- **D = `hedge_days_mean`**, the mean over the month's New York business days of the days from d to the same day 3 (or 12) months
  later, clipped to the month end. Examples: 2025-11-30→2026-02-28 = 90; 2026-01-31→2026-04-30 = 89; 2024-02-29→2024-05-29 = 90.
- y_us and y_home are the month's means of daily values.
- **H3 and P3** (3-month) are the headline. **H12 and P12** (1-year) are for comparison with Ginnie Mae.
- A form exists for a month only if all three of its cells (o_us, o_home and b) are published (n ≥ 10). There is no carrying
  forward and no mixing of tenors.

### 3.4 Diagnostics (labelled; never the headline)

- **A, spot overnight.** G = (1 + r/(100·B))^D, with D for 3 months. This is the only long-history series.
  - Label: "**spot-rate proxy, biased when rate moves are priced inside the hedge window**".
  - Grok's example: on 6 Aug 2024 the fed funds fixing was 5.33 and the September-meeting rate 4.89 (Tradeweb, relayed). A 92-day
    hedge then averages about 5.10, so the dollar leg alone is about 23bp richer than spot. That is arithmetic on meeting rates, not
    an OIS print.
  - **A_rt (ex-ante):** the last rate already published at the 15:30 New York snapshot on d. That is SOFR and €STR of the previous
    business day, and TONA of the previous Tokyo business day (relayed release time; O-8).
  - **A_hist (final history):** the rate dated d, labelled "dated rate, not known at the time".
  - **A_effr:** A_hist with EFFR in place of SOFR, which shows SOFR's quarter-end spikes.
- **B, realised.** G = Π(1 + r_i·n_i/(100·B)) over the business days i in [d, d+D), the ARRC/ISDA convention. n_i runs to the next
  business day but is **clipped at d+D**. B is what a floating cross-currency swap paid after the fact.
  - Verified on the SOFR Index: every ratio from 2026-10-01 to 2026-10-16 matched within 6e-9. Compounding weekend days one by one
    misses by 3–7e-8.
  - B is blank unless both currencies cover the whole window. A gap of more than 4 calendar days between published rates is a WARN
    unless the dates are in `KNOWN_CLOSURES` (Tokyo New Year 31 Dec–3 Jan, Golden Week; TARGET Easter, 1 May, 25–26 Dec).
- **A and B are computed without a basis.** basis_term = 0, `basis_tenor` = `none`, and the label says so.

### 3.5 The basis and OIS cells: the ledger's monthly stage (E-024, ruling 4)

**What changes in `bin/swap_tape_ledger.py`.** A new subcommand
`monthly --start-month 2024-10 --end-month YYYY-MM`. It is offline, reads the cached zips in `~/dtcc_ppd/`, and leaves the STOP latch
logic and `fetch` untouched. It writes two **new** files:
- `data/swap_tape/monthly_short_tenor.csv`: `month, series, tenor, n, median, q1, q3, iqr, status, n_days_with_trades`;
- `data/swap_tape/monthly_short_tenor_funnel.csv`: `month, series, tenor, step, n_after`.

`series` ∈ {`sofr_ois`, `estr_ois`, `tona_ois`} (percent) or {`xccy_jpyusd`, `xccy_eurusd`} (bp); `tenor` ∈ {`3m`, `1y`}.

**Rules.**
1. **`XCCY_TENORS` is not touched.** Adding 0.25 would change `pool1to5`.
2. **Bucket:** |expiry − add_months(effective, k)| ≤ 7 days, with k = 3 or 12. `add_months` clips to the month end. With
   k = 3 the accepted span runs from 82 days (start 31 Jan) to 99 days (start 15 Jul).
3. **Filters F0–F6, named.**
   - F0: series match. OIS: FISN `NA/Swap OIS {CCY}`, both notional currencies equal to CCY, and an underlier containing `OIS` and
     SOFR / EUROSTR / TONA. xccy: `xccy_match`.
   - F1: executed on the file date (UTC).
   - F2: spot start, 0–5 days.
   - F3: no upfront payment.
   - F4: not post-priced and not non-standard.
   - F4s: no strike price.
   - F5: OIS has exactly one fixed leg; xccy has no fixed leg and the currency pair is right.
   - F6:
     - OIS day count A004 for SOFR and €STR, A005 for TONA (via `conv`, reading the other leg when one is blank);
     - payment frequency accepted only when it is a **single payment at maturity**: EXPI/1; MNTH/3 at k = 3; YEAR/1 and MNTH/12
       at k = 3 or 12 (MNTH/12 is YEAR/1, as the ledger's existing `OIS_FREQ` already treats it);
     - DAIL, WEEK and every other code are dropped, and the drops are counted per code in the funnel as `F6f_<code>`;
     - xccy notation and cap as in `run_xccy`;
     - the OIS plausibility cut: a fixed rate (decimal) above 0.25 is dropped, as F6u.
4. **Month assignment** is the month of the UTC execution date (`_xd`), never the effective date.
5. **Floor: single-tenor cells publish only at n ≥ 10** (`FLOOR_TENOR_XCCY`), with status `ok`. Otherwise the status is
   `count_only` and only n is shown. No 5–9 tier, and never a minimum, a maximum or a notional-weighted value.
6. **Byte identity.**
   - Before the change, record the sha256 of every committed file in `data/swap_tape/`.
   - After it, run `build` over all 524 dates; every one of those files must be byte-identical, `SOURCES.md` included.
     `SOURCES_TEXT` is not edited.
   - The README gains an appended section only.

**Feasibility (rough, from the spec author and reviewer passes over 524 files; the builder pins its own):**
- 3-month xccy: yen 3–47 trades a month, at least 10 in 20 of 25 months; the first such month is about Feb 2025. Euro reaches 10 in
  22 months.
- 3-month OIS a month: SOFR 39–174, €STR 45–243, TONA 6–63. TONA paid EXPI in 641 of 697 trades and DAIL in 25 (reviewer).
- Day-count and frequency tally, 3-month OIS, the spec author's filters:
  - USD: A004 EXPI/1 9,258, YEAR/1 436, MNTH/1 152 (dropped), MNTH/3 64;
  - EUR: EXPI/1 3,698, MNTH/12 543;
  - JPY: A005 EXPI/1 677, DAIL/1 25.
- 1-year xccy: 1,769 yen and 1,861 euro trades.

`bin/hedged_ust_yield.py` reads **only** `monthly_short_tenor.csv`. It re-asserts the floor on read: a row with n < 10 and a median is
a FAIL. Months whose `status` is `count_only` have no form for that pair and tenor.

### 3.6 Timing and alignment (daily diagnostics)

- **Key:** one row per New York Treasury business date d.
- **Legs**, each the latest dated ≤ d:
  - SOFR and EFFR on d;
  - TONA and the JGB on the last Tokyo date ≤ d (Tokyo closes about 14 hours before the Treasury snapshot);
  - €STR and the AAA curve on the last TARGET date ≤ d.
  - A_rt then applies the publication lags of 3.4.
- **Stale legs:** a leg more than 5 calendar days older than d drops the row (`stale_leg`).
- **Expected triples** (d / Tokyo / TARGET), from calendar logic; the builder confirms each or explains (C11):
  - 2025-01-02 / 2024-12-30 / 2025-01-02;
  - 2025-04-21 / 2025-04-21 / 2025-04-17;
  - 2025-12-26 / 2025-12-26 / 2025-12-24;
  - 2026-05-06 / 2026-05-01 / 2026-05-06.

### 3.7 Monthly aggregation, quarter ends, and L

- **Diagnostics:** the mean of the daily values over kept days. Every term is averaged, so the identity holds in the means.
- **Headline:** built at monthly level (3.3).
- **Partial months:** a month is `partial` if its last business day is missing for any leg; section 4 uses complete months only.
- **Quarter ends.** Every 3-month window contains exactly one quarter end, and every 1-year window contains four. So "does the window
  contain a quarter end" would flag every month. The flag `qe_turn_early` marks months whose hedge windows put the quarter end in their
  first 30 days: start months March, June, September and December (O-7).
- **L.** L is the latest complete month at the first build. It is stored as the `L` row of `summary.csv`. Later builds read it and
  never change it; a missing row is written once. Mutant in G18.

### 3.8 Variant table

| Variant | Construction | Basis | Window | Role |
|---|---|---|---|---|
| H3 | bond-basis, 3m OIS | 3m xccy | EUR 2024-10 →; JPY first published month → | **HEADLINE** |
| P3 | plain subtraction, 3m OIS | 3m xccy, shown separately | as H3 | MAIN (scored) |
| H12, P12 | as above, 1-year | 1y xccy | from the first published month | MAIN (Ginnie Mae comparison) |
| A_rt, A_hist | spot overnight | none | JPY 2018-04 →; EUR 2019-10 → | DIAGNOSTIC |
| A_effr | spot overnight with EFFR | none | as A | DIAGNOSTIC |
| B | realised overnight | none | as A, ending about 3 months before the latest date | DIAGNOSTIC |
| DKS | forward premium `rho` (3m) | inside rho | to 2025-06 | CHECK, cache only |

## 4. Pre-registered descriptive questions (spec only; not in the README)

No hypothesis is tested. The questions, anchors and marks are fixed before any carry series was computed.

**Anchors:**
- euro headline: 2024-10;
- yen headline: the **first month with a published median** for all of TONA-OIS 3m, SOFR-OIS 3m and xccy_jpyusd 3m;
- diagnostics: 2023-01;
- L (3.7).

Every answer reports the full monthly path with its minimum and maximum months (C-070). Yen paths are computed in the cache only.
Committed yen numbers appear only in `yen_summary.csv` (section 7).

- **Q1. Yen pickup sign (H3), from the anchor to L.**
  - Notable: any month with H3 pickup > 0.
  - Expected now: negative. BlackRock gives about −1pp in September 2026.
- **Q2. Euro pickup sign (H3 from 2024-10; A_hist from 2023-01).** Notable: a change of sign.
- **Q3. Where the change came from, anchor to L (H3).** Δpickup = Δust10 + Δrate_gap_term + Δbasis_term − Δhome10 (IDENTITY; all
  terms reported). Notable: a term other than rate_gap_term with the largest absolute change.
- **Q4. Basis share (H3).** Share = |basis_term| / |rate_gap_term + basis_term|. Notable: a median above 10%, or any month above 20%.
- **Q5. Construction and form wedges.**
  - Median |H3 − A_rt|, |H3 − A_hist|, |H3 − B| and |form_gap_bp| per pair.
  - The count of months where the pickup signs disagree.
  - Notable: a median above 25bp, or sign disagreement in more than 10% of months.
- **Q6. Tenor.** Median |H3 − H12| per pair. Notable: above 25bp.
- **Q7. DKS agreement** (V5).

## 5. Validation and the gate

| Ref | Source (read 19 Oct) | Quote | Rounding | Build value | Role |
|---|---|---|---|---|---|
| V1 | BlackRock weekly commentary, 8 Sep 2026 (PDF 200). Note: "Bloomberg's estimate of a three-month USD-JPY hedging cost is subtracted" | JGB about 3% "versus 2% on a 10-year Treasury after hedging", rolling 3-month forwards | whole percent (±50bp) | yen H3 and P3, Sep 2026 | **GATE, 3m** |
| V2 | TD Economics, published 31 Mar 2026 (200); formula "US-10 year – (US 3 month – Japan 3 month)" | "closer to 1.3% on a fully hedged U.S. Treasury", against about 2.3% at home | one decimal (±5bp) | yen H3 and P3, Mar 2026; P without basis as like-for-like (INFO) | **GATE, 3m** |
| V3 | Ginnie Mae Global Markets Analysis (Bloomberg data; "subtracting the 1 yr hedge cost"; rounded to the hundredth). Issues of Jun 2025, Dec 2025 and Jul 2026 (200) | month-end yen / euro: Apr 2025 0.77 / 2.14 (from the stated monthly changes), May 2025 0.77 / 2.13, Nov 2025 1.14 / 2.44, Jun 2026 1.56 / 2.92 | ±0.5bp | H12 and P12, using that month's 1y cells with the **month-end** Treasury yield | **GATE, 1y** |
| V3-info | Ginnie Mae, Oct 2024 issue | Sep 2024 0.09 / 2.48; Aug 2024 −0.18 / 2.50 (implied) | ±0.5bp | before the tape starts | INFO |
| V4 | Banque de France blog 444, 13 Apr 2026, Chart 3 note | 3-month yen premium 35bp on 9 Apr 2025; 15–20bp at the start of 2026 | — | xccy_jpyusd 3m, Apr 2025 and Jan 2026 (reviewer −33, −16) | CHECK, **non-independent**: these windows were set after a rough look |
| V5 | DKS 3m `rho` (cache only) | all-in forward premium | — | H3 against h_dks on the overlap; A_hist against h_dks, 2018–2025 | CHECK |
| V6 | CFR, 18 Mar 2024 | short rates 5.5%, 10-year 4.0–4.5%, JGB about 75bp | — | A_hist and B, Mar 2024: carry < 0.5% and pickup < 0 | sign only |

**The gate (FAILED build if missed).** For each form F ∈ {H, P} and each tenor group (3m: V1 and V2; 1y: V3, eight points), compute
|F − published| in bp over the group's points. **A median above 25bp is a FAILED build.**
- `references.csv` prints each point's gap and its quote rounding. A point that misses by 25bp but lies within 25bp plus the rounding
  half-width is noted "within quote rounding". It still counts at its raw gap.
- Before the build, the reasons a miss can happen are stated:
  - V1 rounds to a whole percent and its exact date is not given;
  - the TD data date is not given, and its 3-month rates are unnamed (bills or OIS);
  - Ginnie Mae values are month-end, against monthly-median cells;
  - Bloomberg forwards are FX-swap prices, not currency-swap prints.
- V5 statuses: PASS ≤ 10bp median absolute monthly difference, WARN 10–15, FAIL above 15. A correlation verdict needs n ≥ 8
  overlapping months, otherwise INFO. The expected overlaps are Oct 2024–Jun 2025 (9) for euro and about 5 for yen (INFO).
- **Not used as evidence.** Bloomberg 24 Dec 2024 ("0.28%"; record −1.1% in 2023) reached the spec author only as search snippets;
  the BNN page redirected home. TwentyFour 27 Jun 2019 (euro −1.29%, 1-month hedge, before €STR). Both are INFO and unscored.

## 6. Outputs

**Script `bin/hedged_ust_yield.py`.** Modes: `fetch`, `build` (offline, byte-identical on re-run) and `selftest` (synthetic data, no
network, under 20 s). Committed files sit in `data/hedged_ust_yield/` and open with `# source:`. Each file has an **exact allowlist**
held as `SPEC_ALLOW` (sha256) and as `ALLOW` (G13). Values are % or pp to 6 decimals, and bp to 3.

- **`data/vintages/hedged_ust_yield/daily_panel.csv` (cache):**
  `date, pair, tokyo_or_target_date, ust10, home10, r_us, r_us_rt, r_us_effr, r_home, r_home_rt, D_days, h_A_rt, h_A_hist, h_A_effr,
  h_B, gap_A_rt, gap_A_hist, gap_B, h_dks, qe_turn_early, drop_reason`.
- **`data/vintages/hedged_ust_yield/monthly_all.csv` (cache: both pairs, the full monthly paths)**, with the same columns as
  `monthly.csv`.
- **`monthly.csv` (committed; euro rows only, G10e):**
  `month, pair, variant, role, n_days, partial, qe_turn_early, ust10_pct, home10_pct, rate_gap_term_pp, basis_term_pp,
  hedged_carry_pct, pickup_pp, form_gap_bp, basis_tenor, hedge_days_mean, n_ois_us, n_ois_home, n_basis`.
  - IDENTITY: hedged_carry = ust10 + rate_gap_term + basis_term and pickup = hedged_carry − home10. Tolerance 2e-6 on the committed,
    rounded file and 1e-9 unrounded in the cache.
- **`yen_summary.csv` (committed): `period, variant, statistic, value, credit`.**
  - `period` ∈ {`2023`, `2024`, `2025`, `2026_ytd`, `anchor_<YYYY-MM>`, `L_<YYYY-MM>`}.
  - `variant` ∈ {H3, P3, H12, A_hist, B}.
  - `statistic` ∈ {`hedged_carry_mean`, `pickup_mean`, `rate_gap_term_mean`, `basis_term_mean`, `n_months`}.
  - **At most 8 values per (variant, statistic).** Years before a variant exists are absent.
  - `credit` carries the BoJ credit text.
- **`summary.csv`:** `run_label, L, question, pair, variant, statistic, value, notable`. Yen rows carry `notable` with `value` blank;
  the first L's rows are kept.
- **`references.csv`:** `ref_id, source, ref_date, pair, form, tenor, published, rounding_bp, build_value, gap_bp, tolerance, status,
  note`. Yen rows have `build_value` and `gap_bp` blank, but status and tolerance filled. The gate lines are `ref_id = GATE_<form>_<tenor>`.
- **Also committed:**
  - `checks.csv`: `check_id, description, expected, observed, status`;
  - `pins.csv`: `source, series, pin_date, value, unit`, at most 5 per source, BoJ TONA pins included;
  - `fetch_log.csv`.
- **`README.md`** (generated, so G14 can scan it):
  1. Two opening sentences: what the series is (rolling 3-month carry of a hedged 10-year Treasury against the home 10-year yield),
     and the required sentence of section 0.
  2. The latest result, euro month by month and yen as annual figures.
  3. A column dictionary.
  4. Why yen appears only as annual figures (BoJ terms).
  5. Defined terms: hedging cost, basis, pickup, OIS, rolling carry, plain against bond-basis form.
  6. One real worked row: a euro month, from the committed columns.
  7. Provenance at the end, with the NY Fed notice, the BoJ API credit, the ECB "derived" label and the E-024 statement in full.
  The questions of section 4 are **not** in the README.
- **`SOURCES.md`:** each source with URL, licence and citation, and the column provenance used by G10.

## 7. Licence and leak rules

1. Committed date columns are `YYYY-MM` or calendar periods; daily values appear only in `pins.csv`.
2. **No committed column is a raw input series, or its monthly mean.** Exceptions: `ust10_pct` (US government), `home10_pct` for
   euro (ECB, labelled derived) and the DTCC cells, which live in the ledger's files. G10d checks every committed numeric column against
   the cache means of every raw input, rounded to the committed decimals, at 1e-6.
3. **Yen (O-1, ruled by the supervisor).** No yen monthly row is committed. The arithmetic: `rate_gap_term` plus the public SOFR
   recovers a mean TONA to about 1bp at the published granularity. Annual means, plus at most two anchor months, are the accepted
   granularity. TONA pins count against the five-per-source cap.
4. **The DKS panel never reaches a committed file**, except as V5 overlap statistics: n, median absolute difference, median signed
   difference, and correlation if n ≥ 8.
5. **DTCC cells** are committed only by the ledger's monthly stage (3.5), at n ≥ 10. This script copies their n and the derived terms,
   never a median at n < 10.

## 8. Pinned checks (`checks.csv`)

- **C01 Treasury 10y**, by name: 2024-03-21 4.27 and 2026-09-18 5.01 (relayed); 2026-10-15 5.10 (reviewer).
- **C02 MoF 10Y:** 2024-03-22 0.762 and 2026-09-18 2.981 (relayed); 2026-10-01 3.092. The two files agree on their overlap.
- **C03 NY Fed:** SOFR 2018-04-02 1.80 and 2026-10-15 3.89; EFFR 2026-10-15 3.88.
- **C04 SOFR Index (FAIL)**, from 2020-03-02. Each consecutive pair: Index(b)/Index(a) = 1 + SOFR(a)·(b−a)/36000 within 2e-8. Plus a
  window test: for every 3-month window starting on the first business day of a month, B's compounding of SOFR must equal the index
  ratio within 2e-8. Pin: 2026-10-16 1.26303308.
- **C05 €STR (FAIL):** 2019-10-01 −0.549; 2026-10-16 2.441; CI 2026-10-19 110.03236357. The CI ratios match B's compounding within
  1e-9, pairwise and on the window test.
- **C06 TONA:** 2018-01-04 −0.047 and 2026-10-15 1.228. `null` is missing. The header block is as in section 2. A non-empty
  `NEXTPOSITION` means the next page is fetched, at most 3 pages.
- **C07 ECB AAA:** `ea10_sa` 2026-09-18 3.533452 within 1e-5, with fx_rate_gap builder decision 12's quarantine dates.
- **C08 DKS.**
  - The probe returns 206 with header, size and ETag as observed. A different ETag is a WARN (a new vintage) and does not latch.
  - `dks_3m_1y.csv` holds the JPY and EUR `3m` and `1y` rows. The full body is deleted after extraction, and its sha256 is logged.
- **C09 Ledger cells.**
  - `monthly_short_tenor.csv` exists and is no older than 14 days.
  - Every row with a median has n ≥ 10.
  - The yen anchor month is recorded.
  - The euro 3m cells exist for 2024-10.
- **C10 Real-data pins (reviewer; reproduce within 1e-6 or explain).** A_hist on 2026-10-15 with D = 92:
  - yen: gap −2.766265, h 2.333735;
  - euro: gap −1.501968, h 3.598032.
- **C11 Alignment triples (3.6).** FAIL on a mismatch, unless a written explanation is given.
- **C12 Staleness (WARN):** SOFR, EFFR, €STR, TONA, Treasury, MoF current month and ECB YC no older than 7 days; the ledger monthly
  file 14; DKS none.
- **C13 Bund (INFO):** the monthly median of (AAA − Bund 10y). Statistic only.
- **C14 Fixed output:** a second `build` leaves every sha256 unchanged.

## 9. Selftests (synthetic only; each guard applies its mutant itself, and an uncaught mutant fails)

**`bin/hedged_ust_yield.py selftest`**

| Guard | Protects | Mutant that must be caught |
|---|---|---|
| G1 basis sign | b < 0 lowers h | sign flipped (yen H3 becomes 0.8152199118 against 0.4144953188); basis added to the USD leg |
| G2 gap direction | o_us > o_home gives a negative gap | home and US rates swapped |
| G3 day count | 360 / 365 / 360 | TONA on 360 (H3 0.4186674875); SOFR on 365 |
| G4 bond-basis form | 3.2 exactly | H computed as P (0.50 against 0.4144953188); P computed with a day-count change |
| G5 tenor D | D = actual days, clipped to month end; `hedge_days_mean` in C | D = 90 in H3 (0.4139834352, a miss of 5.1e-4); a quarter of a year in place of D/B. D also sets B's window (G7); A's annualisation cancels D to about 1e-6, so A's tolerance is ≤ 1e-7 |
| G6 alignment | legs dated ≤ d; A_rt uses only published rates | the next-day TONA leg; A_rt using the dated SOFR; stale rule removed (Golden Week fixture with a 10-day gap kept); the triples of 3.6 on a fixture calendar |
| G7 B window | [d, d+D), complete windows, clipping | window includes d+D; backward window; B at the sample end with missing days; no clipping (fixture Mon 5–Sat 10 Jan 2026, SOFR 4.30–4.33 then Fri 4.40: G 1.000601811483 clipped, against 1.000846373146 unclipped) |
| G8 B compounding | ARRC | weekend compounded daily (fixture Mon 5–Mon 12: 1.000846373146 against 1.000846417984); simple sum (1.000846111111); index rule of C04 on a fixture |
| G9 decomposition | basis_term = H − h0 | basis_term = b/100 inside H (identity fails by 3.1e-4 on the yen fixture) |
| G10 licence and leak | section 7 | (a) a daily date column; (b) a DKS-tagged column in any committed file; (c) a ledger row with a median at n = 9 is accepted on read; (d) a `tona_pct` or `sofr_pct` column, caught by the rounded comparison at 1e-6; (e) **`monthly.csv` has a yen row**; (f) `yen_summary.csv` with a 9th value per variant and statistic; (g) a yen `build_value` in `references.csv` |
| G11 staleness | R7 | a TONA file 20 days old passes silently; a stale ledger file forward-filled |
| G12 no carry-forward | each month's own cells | last month's basis used for a `count_only` month; a 1y cell used in H3 |
| G13 allowlists | exact headers | an extra or renamed column; `ALLOW` drifting from `SPEC_ALLOW` |
| G14 no causal text | R5 | "caused", "drove", "driven", "because of", "led to", "prompted", "pushed" or "in response to" in the README or printout (`fx_rate_gap.CAUSAL_RX` extended); the required sentence must pass, and the same sentence with "led to" added must fail |
| G15 fetch safety | R1–R3 | non-200 latches (the DKS probe's 206 does not); a redirect latches; FRED, sec.gov or DTCC hosts allowed; `@` in the UA; pacing under 2 s; 31 requests |
| G16 parsers | section 2 | BoJ `null` read as 0; the BoJ header read as data; a BoJ row with the quoted comma split wrongly; NY Fed read by position or as oldest-first; ECB CI read as a rate; Treasury `10 Yr` by position (the 2025 `1.5 Month` layout); MoF footer read as data; DKS `08feb2007` misparsed |
| G17 DKS sign | rho in the 3.2 convention | sign flipped: on a fixture with the home rate below the dollar rate, `rho_signed` < 0. On real data a negative overlap correlation with H3 is a FAIL naming O-4 |
| G18 months and L | complete months only; L frozen | a partial month counted in section 4; L recomputed on a later build |
| G19 gate | section 5 | the median over the group's points replaced by the minimum; a FAILED gate writing to the committed folder; the rounding note changing the status |

**`bin/swap_tape_ledger.py selftest`, new checks for the monthly stage** (fixture dates in 2030):

| Guard | Mutant that must be caught |
|---|---|
| M1 tenor edges | start 2030-01-31: 82 days in, 81 out; start 2030-07-15: 99 days in, 100 out; the same pattern at k = 12 |
| M2 floor | n = 9 publishes a median; n = 10 does not publish one |
| M3 month assignment | a trade executed 2030-03-31 23:30 UTC with effective date 2030-04-02 assigned to April |
| M4 `pool1to5` untouched | 0.25 added to `XCCY_TENORS` changes the fixture's `pool1to5` |
| M5 day count | TONA accepted with A004; SOFR accepted with A005 |
| M6 frequency | DAIL/1 or WEEK/13 kept; drop counts missing from the funnel |
| M7 F1 | a trade executed the previous day counted |
| M8 no extremes | a min, max or weighted column added |

## 10. Success criteria (exact)

1. `python3 bin/swap_tape_ledger.py selftest` passes every existing check plus M1–M8, with each mutant caught.
   `python3 bin/hedged_ust_yield.py selftest` prints G1–G19 with each mutant caught, and exits 0.
2. Byte identity (3.5 rule 6): the sha256 of every committed file in `data/swap_tape/` is the same before and after the ledger change,
   after `build --start 2024-10-14 --end <last cached date>`.
3. `python3 bin/swap_tape_ledger.py monthly --start-month 2024-10 --end-month <last complete month>` writes the two files, and C09
   holds.
4. `python3 bin/hedged_ust_yield.py fetch` makes at most 30 requests, logged, with no STOP. The DKS probe returns 206.
5. `python3 bin/hedged_ust_yield.py build`:
   - C01–C09, C11 and C14 PASS; C10 reproduced or explained; C12 PASS or WARN; C13 INFO;
   - both gate groups printed, with no FAILED gate;
   - V4–V6 statuses;
   - the section 4 summary with `notable` flags;
   - G10e holds (no yen rows in `monthly.csv`).
6. A second `build` leaves every sha256 unchanged.
7. `bin/check.sh --all`: five ✓ guard lines, `✓ no killed claims found`, `✓ page clean`, and M10 clean. Read the ✓ lines.
8. A verifier re-derives one number by hand: the euro H3 for 2024-10 from the committed ledger cells and the cached yields, or C10.
9. **README cold-reader test:** two fresh agents with no context, a non-specialist trustee and a rates practitioner, read only the
   README. Each states what the series is and is not. The supervisor checks their statements against section 0. A reader who comes
   away believing "the yield an investor earns" or a causal claim fails the README.

**Landing (builder):**
- a `.gitignore` rule for `data/vintages/hedged_ust_yield/` and `data/hedged_ust_yield/_FAILED/`;
- the ledger README section for the monthly files;
- a REPRODUCE.md paragraph;
- a CALENDAR.tsv row: "monthly: ledger `monthly`, then `fetch` and `build`; DKS V5 check";
- a HANDOVER row.
The builder commits nothing. The supervisor verifies and writes any findings text.

## 11. OPEN questions

- **O-1 RULED (supervisor): no yen monthly rows.** Annual and anchor values only (section 7.3).
- **O-1b OPEN, for the principal:** the BoJ API notice asks anyone who releases a service using the API to notify the Bank by email.
  Does a public repository with this script count as a "service"? The credit is shown either way. Sending the email is the
  principal's decision; no agent sends it.
- **O-2 RULED (supervisor): the ledger gains the monthly stage under E-024** (3.5).
- **O-3 OPEN: the A-proxy error before 2024.** Only V5 (to 2025-06) measures it.
- **O-4 OPEN: DKS conventions.** The sign and units of `rho`, `rho_ibor` against `rho_sofr` at 3m, and whether the `3m` rows exist
  for JPY and EUR (relayed). *Settles:* the DKS data appendix, then G17.
- **O-5 OPEN: no euro 3-month reference level.** The euro gate rests on Ginnie Mae's 1-year figures only. *Settles:* an ECB Financial
  Stability Review chart with values, or a Grok source hunt.
- **O-6 OPEN: euro before Oct 2019** (EONIA not checked).
- **O-7 OPEN (interpretation of ruling 6): the quarter-end flag.** Every 3-month window spans one quarter end, so the flag marks
  quarter-end-early starts (3.7). The supervisor confirms or replaces it.
- **O-8 OPEN: TONA availability.** BoJ's final rate is relayed as the next business day; the API showed 15 Oct as the latest at 18:33
  JST on 19 Oct. This affects A_rt's lag and C12.
- **O-9 OPEN: whole-percent references and the 25bp gate.** V1 can miss by up to 50bp on rounding alone. With two 3-month points, one
  rounding miss can fail the 3m gate. The rule stands as ruled, and the risk is stated here before the run.

## Amendments, 19 Oct (reviews)

Sources: Grok's attack (`grok_out.json`), the second Sonnet review, and the supervisor's rulings 1–11. Each item is folded into the
body; new web facts were observed 19 Oct (Ginnie Mae issues of Oct 2024, Jun 2025, Dec 2025 and Jul 2026; TD Economics; the BoJ API
notice; two guessed Ginnie Mae paths returned 403 and were not pursued).

1. **Headline** changed from spot overnight (A) to the locked 3-month forward from tape OIS plus the 3-month basis (H3). A and B are
   diagnostics, with Grok's 23bp example. A_rt uses only published rates; A_hist is labelled as dated. (Ruling 1; 0, 3.3, 3.4, 3.8)
2. **Plain-subtraction form P** added and scored; `form_gap_bp` reported; fixtures added. (Ruling 2; 3.2, 5)
3. **1-year variant** H12/P12 added. Ginnie Mae gives four in-window month-ends per currency; Sep and Aug 2024 are INFO. (Ruling 3; 5)
4. **Ledger monthly stage** specified: separate subcommand, new files, add_months bucket, F0–F6 named, A004/A005, single-payment
   frequencies (MNTH/12 accepted as YEAR/1, an interpretation flagged here), drop counts, byte identity, M1–M8. This script no longer
   reads zips. (Ruling 4; R1, R6, 3.5, 9)
5. **Floor** n ≥ 10 only. (Ruling 5; 3.5, G10c, M2)
6. **Basis label** "US-reported cross-currency swap median". BdF is non-independent. Per-start-date basis is not feasible. The
   quarter-end flag is reinterpreted (O-7). (Ruling 6; 3.1, 3.7, 5)
7. **Gate:** 25bp median per form and tenor group, FAILED build otherwise; rounding stated; V5 needs n ≥ 8; CFR is sign-only.
   (Ruling 7; R8, 5, G19)
8. **Yen:** no monthly rows; `yen_summary.csv` with a cap of 8 values; references with build_value blank; TONA pins in the cap.
   (Ruling 8; 6, 7, G10e–g)
9. **Second review, the 16 fixes:**
   - (1) folded into the body;
   - (2) the ledger spec;
   - (5) F1 and the OIS filters named;
   - (7) SPEC_ALLOW covers `yen_summary.csv`;
   - (8) the rounded leak test;
   - (9) G14 against the required sentence;
   - (10) identity tolerances of 2e-6 and 1e-9;
   - (11) C04 from 2020-03-02 with a window test, and C05 at 1e-9;
   - (12) B gaps, clipping, Golden Week, and D's role in G5;
   - (13) V5 thresholds and the n rule;
   - (14) the G16 mutants and the DKS probe;
   - (15) `hedge_days_mean` and the L rule;
   - (16) named guards, the real-data pins C10 and the cold-reader test.
   Fixes 3, 4, 6 and 7 are settled by rulings 1, 4, 6 and 8. (Ruling 9)
10. **README** structure and the required sentence; the questions moved to the spec only. (Ruling 10; 0, 6)
11. **Label** "rolling 3-month carry" throughout; the column is `hedged_carry_pct`. (Ruling 11)
12. **Dropped:** the A3, B3 and A5 variants (the basis now sits on the forward-based forms only), and the `_HELD/` mechanism (O-1 and
    O-2 are ruled).

## Supervisor rulings on the remaining items, 19 Oct 2026 (before any data run)

- Interpretations confirmed: MNTH/12 is accepted as YEAR/1; the quarter-end flag marks months whose hedge windows put the
  quarter-end in their first 30 days; a gate point beyond 25bp counts at its raw gap even when inside its quote's rounding, EXCEPT:
- **O-9 ruled:** a whole-percent quote (BlackRock 8 Sep 2026, "about 2%") is scored against its rounding interval [q − 0.5, q + 0.5]:
  its gap is the build value's distance to that interval (zero inside it). Quotes given to a tenth (TD 31 Mar 2026, "closer to 1.3%")
  and Ginnie Mae's two-decimal figures are scored at their printed value. The 25bp median-gap gate is otherwise unchanged.
- **O-1b** (the Bank of Japan API notice about notifying the Bank when a service uses the API) is referred to the principal. The
  build may use the API for this research run; nothing is sent to the Bank without the principal's decision.
