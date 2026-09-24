# S1 — the supply decomposition: which leg moved (13 Sep 2026)

> **[C-081] CORRECTED 15 Sep 2026 — READ THIS BEFORE THE NUMBERS BELOW.** Z.1's "corporate equities"
> instrument **includes ETF shares as a wrapper layer on top of operating-company equity**
> (`FA564090005.Q` is column 9 of the Fed's own F51.1.t table). Over 2024:Q1–2026:Q2 **ETFs created
> $3,603.8bn of shares while nonfinancial corporates RETIRED $540.7bn net.** So any statement in this
> document that the equity base grew, or that households absorbed net new *corporate* equity, describes
> **growth of the ETF wrapper — which households bought, part of it bond exposure — not issuance by
> operating companies.** The accounting is internally consistent (the Fed confirms no double count); the
> error was interpretation, and it was mine. See C-081.



**Status: RESULT for the nonfinancial-corporate universe through 2026:Q1. Supervisor-verified.**
Ranked item 1, Martin's instruction of 13 Sep. Data `data/supply_decomp/`.

## The source we did not know existed

The Fed publishes the gross decomposition we assumed was unavailable. **Enhanced Financial Accounts,
"Equity Issuance and Retirement"** — `federalreserve.gov/releases/efa/efa-project-equity-issuance-retirement.htm`
— a quarterly series 1996:Q4 to 2026:Q1 with Gross Issuance, Gross Retirement, Retirements-Repurchases and
Retirements-M&A, plus a monthly file splitting part of gross issuance into IPO and SEO. Downloaded to
`data/supply_decomp/fed_efa/`. Scope: **domestic nonfinancial corporations, excluding eREITs.**

## The answer: issuance moved, buybacks did not

| $bn, quarterly rate | 2025:Q1 | 2025:Q2 | 2025:Q3 | 2025:Q4 | **2026:Q1** |
|---|---:|---:|---:|---:|---:|
| Net issuance | −127.83 | −33.36 | −94.94 | −53.05 | **+25.20** |
| Gross issuance | 183.89 | 223.66 | 210.88 | 221.46 | **361.45** |
| Retirements — repurchases | 221.22 | 180.19 | 176.14 | 195.73 | **176.10** |
| Retirements — M&A | 90.49 | 76.83 | 129.68 | 78.78 | **160.15** |

**Gross issuance of $361.45bn in 2026:Q1 is the highest quarter in the series' 118-quarter history**, and not
narrowly: the previous record was $251.82bn (2021:Q2), so this is **43.5% above it**. I re-sorted the full
series to confirm. Repurchases at $176.10bn are *below* their own top five (2022:Q1 $222.35bn is the peak)
and fell both quarter-on-quarter (−10.0%) and year-on-year (−20.4%).

**So the net turned positive because companies issued more, not because they bought back less.**

## The finding inside the finding: the issuance is PRIVATE, not public

The Fed's monthly companion file splits out public offerings. For 2026:Q1: **IPO $6.29bn + SEO $31.88bn =
$38.17bn — 10.6% of the $361.45bn total.** I summed the three monthly rows myself; it reproduces exactly.

The other ~$323bn is the component the Fed aggregates but does not itemise: venture capital, private-equity
investment and other private placements (per the Fed's own FEDS Note methodology). **The record equity
issuance is overwhelmingly private-market issuance, not new listed float.**

This matters for three separate threads and should be carried into all of them:
- **The passive-bid question.** If the supply being created is largely unlisted, it is not supply the index
  bid has to absorb, and the "float grew" reading of net issuance overstates the listed float's growth.
- **The AI build-out (F1/I2).** A record private-issuance quarter is consistent with the large private AI
  rounds, and is the first aggregate measure of them we have. NOT asserted as causal — the Fed does not
  itemise the component, so attribution to AI is unproven.
- **Tier B.** Z.1's corporate equity stock includes closely-held equity while price indices are listed
  (already noted in C-077). This makes that mismatch quantitative rather than rhetorical.

## What is NOT settled — read before quoting

1. **2026:Q2 is not covered.** The EFA series ends at 2026:Q1; the headline Z.1 already has Q2. So the
   +$204.5bn H1-2026 NFC net figure **cannot yet be decomposed into quarters from any source reached.**
2. **The two Fed series do not reconcile, and I have not resolved it.** EFA net is defined as
   `FA103164155.Q ÷ 4` (seasonally adjusted, quarterly rate, excluding eREITs). Our N2c figure of +$51.3bn
   for 2026:Q1 is `FU103164105.Q` (unadjusted, quarterly). EFA gives +$25.20bn for the same quarter. The
   difference is some combination of seasonal adjustment, the eREIT exclusion and a different series
   concept — **verified that FA103164155.Q is not in our pulled vintage, so this is an open reconciliation,
   not a discrepancy either side can claim to win.** Do not mix the two series in one table.
3. **The SEC XBRL bottom-up build has a severe coverage artefact and must not be used for trend.** Because
   10-Q cash-flow statements report year-to-date, the frames API's Q2–Q4 buckets capture only the ~130–190
   filers who redundantly tag a standalone quarter, against ~1,360–1,620 in Q1. Illustration: S&P's real
   2025:Q2 buyback figure is $234.6bn; the frames "Q2 2025" sum is $19.7bn from 152 filers. **Q1-to-Q1
   comparisons are the only valid ones** from that source.
4. **Three tagging errors are live in the raw CSV**, left as reported and named here so they can be excluded:
   Brainstorm Cell Therapeutics $182.0bn issuance in 2025Q1 (a nano-cap; 71.5% of that quarter's total);
   Relmada Therapeutics $10,241.6bn in 2021Q3; Fannie Mae an identical $70.00bn every year 2020–2025.
   SPDR Gold Trust and other trusts/SPACs also contaminate the issuance concepts ($51.4bn in 2025 alone).
5. **S&P Dow Jones buyback data stops at 2025:Q3** for the cross-check — spglobal.com returns 403 to
   scripted and tool fetches alike, and the agent correctly declined to spoof a browser identity.
6. An SEC-filer-universe bottom-up shows buybacks **rising** +15.9% Q1-on-Q1, against the Fed's NFC series
   showing them falling. The likely reconciliation is sector scope — the SEC sum includes banks (JPMorgan,
   Bank of America, Goldman all in its Q1-2026 top ten) and REITs that the Fed's nonfinancial definition
   excludes. **Not resolved; the Fed series is the authoritative one for the nonfinancial question asked.**


## The third leg: equity retired through M&A — it is in the same Fed series

The second agent reached the same EFA source independently, which is the strongest form of corroboration
available here, and it carries the retirement leg we thought unmeasurable. Annual, $bn, nonfinancial
corporations (I re-summed all of these from the quarterly file — five years checked, five exact):

| year | retired via M&A | retired via repurchase |
|---|---:|---:|
| 2015 | 427.18 | 445.39 |
| 2020 | 287.17 | 427.89 |
| 2023 | 427.54 | 658.49 |
| 2024 | 322.07 | 728.35 |
| 2025 | 375.78 | 773.28 |
| 2026 Q1 only | 160.15 | 176.10 |

**So all three legs are measured, for nonfinancial corporates, 1996:Q4–2026:Q1.** Note the shape: buybacks
grew steadily (445 → 773 over the decade) while M&A retirement did not trend. The float-shrinking machine
of the last decade was buybacks, not take-privates.

**Scope, and it is not the going-private concept.** The Fed's M&A column covers any cash-financed M&A by a
domestic acquirer plus cash-or-stock M&A by a foreign acquirer, of **both public and private** nonfinancial
targets. It is broader than "listed equity taken private". It is also built from LSEG SDC Platinum, which is
paywalled — **we can use the Fed's output but cannot rebuild or independently verify it.** Label it as the
Fed's number, never as ours.

## Going-private filing counts — solid, and deliberately not summed

Counted from EDGAR's own quarterly full-index feed, every filing of every form type, bucketed by **filing
date** (not transaction date). **I re-counted 2015 myself from ~995,000 index rows: SC 13E3 33, SC 13E3/A
103, Form 25 76, Form 25-NSE 1,268 — four for four against the agent.**

| year | SC 13E3 | SC 13E3/A | Form 25 | Form 25-NSE |
|---|---:|---:|---:|---:|
| 2015 | 33 | 103 | 76 | 1,268 |
| 2020 | 56 | 165 | 137 | 1,790 |
| 2023 | 55 | 187 | 128 | 2,282 |
| 2024 | 54 | 210 | 123 | 1,694 |
| 2025 | 37 | 134 | 132 | 1,768 |
| 2026 (to 12 Sep, PARTIAL) | 21 | 75 | 77 | 1,262 |

**DO NOT SUM THESE COLUMNS.** They are not mutually exclusive populations. SC 13E-3 is filed only when an
*affiliate* takes the company private — an arm's-length cash acquisition of an unrelated public company
never files one. One deal can generate an SC 13E-3 plus a merger proxy *or* a tender offer, plus eventually
a Form 25 or 25-NSE. And Form 25-NSE, filed by the exchange, captures delistings for bond redemptions, ADR
terminations and listing-standard failures — it is not an "acquired" signal.

**A dollar aggregate for going-private cannot be built from these filings, and the reason is specific.**
Twelve filings were read at source, one per year, taking the figure verbatim from each filing's own fee
table. The "Transaction Valuation" is **not computed on a consistent basis**: AmTrust (2018), Tallgrass
(2020) and Continental Resources (2022) report only the *public float* being cashed out, excluding the
controlling holder's rollover — Continental's stated $4.31bn against roughly $26.6bn of total equity — while
Inovalon (2021) and Select Medical (2026) include everything. Reading all ~30–80 filings a year would still
not give a comparable aggregate without modelling each cap table.

**A method lesson worth keeping: EDGAR full-text search hit counts are NOT filing counts.** It indexes each
*document* inside a filing separately. Verified example: a January-2015 SC 13E3 query returned 15 hits
against 8 unique accessions, because one filing carried 7 exhibits. Scaled to the year that inflated 136
real filings to 200 "hits". Count from `full-index/{year}/QTR{n}/form.idx`, never from search hit counts.

## Supervisor verification, 13 Sep

| claim | check | result |
|---|---|---|
| EFA 2026:Q1 net +25.20, gross 361.45, repurchases 176.10, M&A 160.15 | read the downloaded CSV | REPRODUCES exactly |
| 361.45 is a series record | re-sorted all 118 quarters | CONFIRMED; prior record 251.82 (2021:Q2) |
| Repurchases fell QoQ and YoY | series arithmetic | CONFIRMED; and below their own top five |
| Public IPO+SEO = $38.2bn of Q1 | summed the three monthly rows | CONFIRMED, 38.17 = 10.6% |
| M&A retirement 160.15 is a record | re-sorted | **NO** — 2007:Q4 (221.48) and 2023:Q4 (218.17) are higher. The agent claimed only a QoQ rise, which is right |
| FA103164155.Q is our series | searched the pulled vintage | NOT PRESENT — reconciliation genuinely open |
| EFA annual M&A and repurchase sums (5 years) | re-summed from the quarterly file | ALL FIVE EXACT |
| 2015 filing counts, 4 form types | re-counted from EDGAR full-index, ~995k rows | ALL FOUR EXACT |
| A free dollar aggregate for M&A retirement exists | read the EFA series and its scope note | YES — contradicts the brief I wrote, correctly |
