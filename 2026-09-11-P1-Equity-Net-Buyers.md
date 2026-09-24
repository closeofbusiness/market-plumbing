# P1 — who bought US corporate equities, net, 2015Q1-2026Q2 (Fed Z.1, release of 11 Sep 2026)

**Status: DATA (first cut), channel-neutral.** Ranked item 1 in RESEARCH_STATE section 5. Script
`bin/z1_equity_netbuyers.py current|YYYYMMDD`; tables `data/z1_equity_netbuyers/*_2026Q2.csv`; source CSVs
`data/vintages/z1_equities_2026Q2/`.
**Supervisor verification (11 Sep):** the parse uses the same series codes as the earlier pipeline
(FU103164105.Q, FU263064105.Q, FU153064105.Q); 2025 annual sums vs the Q1-vintage values in
`data/series.tsv`: rest of world 646.7 vs 643.7; NFC net issuance -348.2 vs -304; households 824.0 vs 863.5 —
the size and offsetting direction of a normal June-to-September revision (households are the Z.1 residual).
**Read with these caveats (supervisor):**
- The identity check passes by construction (the household line is the plug); it proves the parse captured
  every line, not the data.
- The instrument is ALL US corporate equity plus foreign shares held by US residents, public and closely
  held (level $123.7trn at 2026Q2) — not listed market cap. "93% revaluation" is a statement about that
  whole stock.
- Hedge funds have their own line in this vintage; the household residual no longer contains them.
- Table numbering changed on 11 Jun 2026: corporate equities is F51.1.t (flows) / F51.1.s (stocks), not
  F.223/L.223. The script finds the table by title.

---

## Equity Net-Buyer Table — Z.1, 2026:Q2 Release

**Release used:** Federal Reserve Z.1 "Financial Accounts of the United States," release date **September 11, 2026**, data vintage **2026:Q2** — confirmed live from `https://www.federalreserve.gov/releases/z1/` (no fallback to Q1 needed). Source files pulled from `https://www.federalreserve.gov/releases/z1/current/` (release page, `z1_table_mapping.csv`, and the single bulk `z1_csv_files.zip`) — 3 HTTP requests total, correct User-Agent, no email in any request.

**Contradicts the brief — table numbers are stale.** The brief asked for F.223/L.223. In this release, old-style **F.223/L.223 is "Direct investment intercompany debt,"** not equities. Corporate equities is old-style **F.224/L.224**, and under the Fed's current table-naming scheme, flow and level share one root code, distinguished by suffix: **F51.1.t** (flow) and **F51.1.s** (level). I did not hardcode either the brief's number or my own discovery — the script resolves the table each run by matching the *title* "Corporate equities" in that release's own `z1_table_mapping.csv`, so it self-corrects if the Fed renumbers again. Within the flow table I used the `_tu` companion series (`FU`-prefixed, e.g. `F51_1_t_tu.csv`) — confirmed by direct comparison that the `FA` (SAAR) series ≈ 4× the `FU` series in the same quarter, so `FU` is already true single-quarter, not annualized; only millions→billions conversion was applied.

### Identity check (item 3) — PASS, exact

Per quarter, 2015:Q1–2026:Q2 (46 quarters): **max |Σholder net purchases − total net issuance| = $0.0000bn**, and separately **max |Σ(3 top-level issuers) − total| = $0.0000bn**. Both hold to the reporting precision of the source data ($1 million) with no exceptions in any quarter — this did not fail, so no stop was triggered. As an internal cross-check, the 12 issuer sub-lines (bank/insurer/fund/REIT/etc. own-share issuance) also sum exactly to the "Domestic financial sectors" aggregate (max gap $0.0000bn).

**Household-sector residual, verified numerically:** total flow minus the sum of the other 21 holder lines equals the published household line exactly every quarter (max gap $0.0000bn) — households *is* the Z.1 plug, as the brief states. One correction: in this vintage, **hedge funds have their own separately modeled line** ("Hedge funds (domestic)," not commingled with "Households and nonprofit organizations"), so the brief's parenthetical "(it includes hedge funds…)" no longer holds for 2026:Q2 data — only the "and nonprofits" half still does (no separate nonprofit line exists).

### Revaluation check (item 4) — gaps are real, not rounding

> **[C-119, 23 Sep] RESOLVED — these gaps are the other-volume-changes term this check omitted, not non-reconciliation.**
> Z.1: change in level = flow + revaluation + other volume changes. The check below had no OVC term. Where the Fed
> publishes OVC (sector net worth) the identity closes to $1 million over 299 quarters; for rest of the world, sector
> OVC in 2024:Q2 is $319.4bn against a $318.5bn equity gap. OVC is published per sector only, so the equity-level match
> is strongly supported rather than exact. Households carry it because their line is a residual that absorbs other
> sectors' reclassifications. The table stands as arithmetic; the "genuine non-reconciliation" reading below does not.

Z.1 has no single revaluation table for equities; quarterly FR series exist only for four sector aggregates, scattered across four separate per-sector files. Max |implied revaluation (Δlevel − flow) − published FR|, $bn:

| Sector | Max gap | Quarter | Note |
|---|---:|---|---|
| Nonfinancial corp. business (as holder) | ~0.0 | — | clean 1:1 match |
| Households and nonprofits | 318.2 | 2021:Q4 | clean 1:1 match |
| Rest of world (as holder) | 322.1 | 2021:Q4 | clean 1:1 match |
| Domestic financial sectors (aggregate) | 496.3 | 2026:Q2 | **approximate** — my own best-effort grouping of ~14 subsector lines, not an official Fed crosswalk |

Gaps are irregular in sign and size every quarter (roughly $2bn–$300bn), not a one-time break — I checked for a hedge-fund-carveout discontinuity around 2021Q4/2022Q1 specifically and found none in the level series, so this reflects genuine non-reconciliation between independently-estimated Level/Flow/Revaluation components at the individual-sector level (only the whole-economy total ties out exactly, per the item-3 check above). Central bank, foreign banking offices, and "other financial business" hold ~$0 corporate equity throughout and use non-market-value level series by Fed convention, so revaluation there is definitionally near-zero.

### Period summaries

All $ figures are nominal USD billions, not inflation-adjusted, cumulative sums of quarterly `FU` flows over the period.

**2015:Q1–2019:Q4 (20 quarters)**
Top 5 net buyers: ETFs $1,076.6bn · Households $216.5bn · Private debt funds $30.9bn · Property-casualty insurers $29.5bn · BDCs $4.1bn
All net sellers (12): Foreign banking offices −$0.0bn · US depositories −$3.6bn · Federal govt pension −$25.7bn · State/local govts −$35.1bn · Life insurers −$51.2bn · Brokers-dealers −$66.5bn · Hedge funds −$67.0bn · NFC (as holder) −$95.5bn · State/local govt pension −$136.4bn · Private pension funds −$357.8bn · Rest of world (as holder) −$393.4bn · Mutual funds −$527.5bn
NFC net issuance (buybacks net): **−$2,243.96bn** (negative = net retirement exceeded new issuance)
Total equity market value: $37,131.6bn → $53,325.5bn (Δ = +$16,193.9bn) — net flow −$396.3bn (−2.4% of Δ), revaluation +$16,590.3bn (102.4% of Δ)

**2020:Q1–2021:Q4 (8 quarters)**
Top 5: Households $2,033.4bn · ETFs $991.8bn · Rest of world $537.9bn · Private debt funds $32.4bn · Closed-end funds $9.7bn
All sellers (10): Federal govt pension −$13.7bn · P&C insurers −$20.1bn · State/local govts −$53.2bn · Life insurers −$80.0bn · Brokers-dealers −$99.1bn · Hedge funds −$101.3bn · State/local govt pension −$214.9bn · NFC (holder) −$237.4bn · Private pension −$301.1bn · Mutual funds −$795.9bn
NFC net issuance: **−$128.22bn**
Market value: $53,325.5bn → $79,604.4bn (Δ = +$26,278.9bn) — flow +$1,700.8bn (6.5%), revaluation +$24,578.1bn (93.5%)

**2022:Q1–2023:Q4 (8 quarters)**
Top 5: Households $1,044.3bn · ETFs $816.2bn · Private debt funds $18.9bn · Interval funds $12.9bn · Brokers-dealers $11.5bn
All sellers (8): P&C insurers −$66.1bn · Rest of world −$75.8bn · Private pension −$88.2bn · Life insurers −$105.2bn · Hedge funds −$118.2bn · NFC (holder) −$223.3bn · State/local govt pension −$275.0bn · Mutual funds −$705.8bn
NFC net issuance: **−$1,155.67bn**
Market value: $79,604.4bn → $76,767.8bn (Δ = **−$2,836.6bn**, the only period of decline) — net flow was still positive at +$269.5bn; revaluation was −$3,106.1bn (a price decline larger than the total fall, partly offset by continued net buying). Percentages are arithmetically valid but read oddly against a negative denominator (flow = "−9.5%," reval = "109.5%" of Δ), so dollar figures are the clearer statement here.

**2024:Q1–2026:Q2 (10 quarters, latest available)**
Top 5: Households $3,069.4bn · ETFs $2,460.9bn · Rest of world $1,213.9bn · Private debt funds $48.9bn · Interval funds $47.1bn
All sellers (11): Closed-end funds −$0.5bn · Brokers-dealers −$9.5bn · Private pension −$27.7bn · Hedge funds −$51.2bn · State/local govts −$52.4bn · Federal govt pension −$67.8bn · P&C insurers −$185.0bn · Life insurers −$194.0bn · State/local govt pension −$463.9bn · NFC (holder) −$582.7bn · Mutual funds −$2,009.0bn
NFC net issuance: **−$540.71bn**
Market value: $76,767.8bn → $123,687.2bn (Δ = +$46,919.4bn) — flow +$3,243.1bn (6.9%), revaluation +$43,676.3bn (93.1%)

Note: this instrument covers *all* US corporate equity, public and closely-held, which is why levels ($37T→$124T) run well above headline listed-market-cap figures.

### Caveats
- Table numbers in the brief were stale (see above); resolved dynamically by title match, not trusted verbatim.
- No unified equity revaluation table exists; the four-sector FR cross-check is genuine but the "Domestic financial sectors" comparison is my own approximate grouping (flagged in code), not an official Fed aggregation.
- Revaluation gaps (up to $322bn on clean 1:1 matches) are real, unexplained-by-me non-reconciliation between independently estimated series — reported, not resolved. **[C-119, 23 Sep: resolved — the other-volume-changes term; see the item 4 banner.]**
- "Domestic financial sectors" is kept as one issuer line per the brief's own 3-way definition; its 12 components are in the CSVs as `role=issuer_detail`, excluded from the main identity check to avoid double-counting.
- No cause-level interpretation attempted, per the brief's scope instruction.

### Deliverables
All in `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave1/p1/`:
- `z1_equity_netbuyers.py` — reproducible, takes `current` or `YYYYMMDD`
- `netbuyers_quarterly.csv` (1,748 data rows: 46 quarters × 38 series)
- `netbuyers_periods.csv` (152 data rows: 4 periods × 38 series)
- `raw/` — release page HTML, table mapping, full bulk zip, and the extracted flow/level/revaluation CSVs + data dictionaries (`F51_1_t_tu.csv`/`F51_1_s.csv` = the corporate-equities flow/level tables; `S11_1_r.csv`, `S1M_r.csv`, `S12_i_q.csv`, `S2_i_q.csv` = revaluation sources)

One process note: my very first exploratory download went to `/tmp` before I'd set up the working directory — caught and deleted; nothing in the deliverables was affected.
