# ETF1 — the issuance identity net of ETF shares (15 September 2026)

**Status: RESULT. Supervisor arithmetic, two independent censuses.** Ranked item 1, opened by C-081.
Data `data/etf1/` and `data/vintages/z1_etf1_2026Q2/`. ICI Fact Book tables 11 and 13 saved at
`data/vintages/ici_etf_2026/`. Window **2024:Q1–2026:Q2**, Z.1 release of 11 September 2026.

This is the rebuild C-081 asked for. It supersedes the "unattributable" headline (C-083).

## The identity, stripped

Z.1's corporate-equities instrument counts ETF shares as a liability of the ETF sector. Strip that
line out of issuance and the rest of the identity is a *retirement*:

| issuer, 2024:Q1–2026:Q2 | $bn |
|---|---:|
| ETF share issuance (`FU564090005.Q`) | **+3,603.8** |
| Nonfinancial corporate business | **−540.7** |
| Rest of the world (foreign shares held by US residents) | +382.2 |
| Pass-through funds other than ETFs (interval + closed-end) | +90.0 |
| Other domestic financial issuers | **−292.3** |
| **total net issuance** | **+3,243.1** |
| **total net of ETF shares** | **−360.7** |

> **[C-106, 22 Sep]** The row-sum below **cannot fail** — Z.1's "all sectors" total is *constructed* as the sum of the
> issuer lines — so it is not corroboration of anything. The genuine three-line Fed identity is **NFC (−$540.713bn) +
> Domestic financial sectors (+$3,401.586bn) + RoW (+$382.240bn) = $3,243.113bn**, and that middle line, which contains
> the ETF series, is not named in this document's narrative table. **The real corroboration of the ETF figure is ICI Fact
> Book Table 13**, matching Z.1 to under $0.1bn on both years.

The three top-level issuer lines still sum to the total ($0.000bn). So do the
twelve domestic-financial sub-lines. Nothing was dropped; the ETF line was classified.

**Operating companies retired equity on net.** The −$540.7bn is `FU103164105.Q`, public and
closely-held together. Other domestic financials excluding pass-through funds retired another
$292.3bn (holding companies −$343.8bn, life −$68.8bn, P&C −$35.1bn, partly offset by BDCs
+$133.9bn). Foreign shares bought by US residents added $382.2bn. **The only large positive
issuance in the Z.1 corporate-equities identity is the ETF wrapper.**

## The wrapper, by fund type — and it is ICI's census

The Fed's own ETF-sector table (S124.3, old L.124) already splits that wrapper by ICI investment
objective. The levels at 2026:Q2 match ICI's June 2026 monthly release to a tenth of a billion
dollars — domestic equity $10,152.3bn both sides, world equity $2,627.6bn, bond $2,553.0bn,
commodity $311.8bn, hybrid $57.6bn, total $15,702.3bn. Year-end 2023/24/25 match Fact Book Table 11
the same way. **S124.3 is the ICI census, sitting inside Z.1.**

Flows over the window, `S124.3.t_tu`, $bn:

| ICI type | share issuance | share of wrapper |
|---|---:|---:|
| Domestic equity funds | 1,892.5 | 52.5% |
| World equity funds | 563.9 | 15.6% |
| **Equity funds** | **2,456.5** | **68.2%** |
| Taxable bond funds | 967.3 | 26.8% |
| Municipal bond funds | 97.7 | 2.7% |
| **Bond funds** | **1,065.0** | **29.6%** |
| Commodity funds | 60.1 | 1.7% |
| Hybrid funds | 22.3 | 0.6% |
| **All ETF shares** | **3,603.8** | 100% |

**Almost thirty cents of every dollar of "new corporate equity" in Z.1 was a bond ETF.** The Fed's
Technical Q&A (the C-081 source) says this outright: some ETF shares are based on underlying debt
securities, and data limitations force those shares into the corporate-equities instrument.

Independent check, ICI Fact Book Table 13 (annual, millions, downloaded 15 Sep 2026 from
`icifactbook.org/xls/26-fb-table-13.xlsx`):

| year | ICI total | Z.1 four-quarter sum | ICI bond | Z.1 bond funds |
|---|---:|---:|---:|---:|
| 2024 | 1,144.8 | 1,144.8 | 295.4 | 295.3 |
| 2025 | 1,468.2 | 1,468.0 | 443.4 | 443.5 |

The two censuses agree. 2026:H1 is Z.1 only (Fact Book stops at 2025): $991.0bn of ETF issuance, of
which $326.2bn bond funds. ICI's June 2026 monthly release puts year-to-date net issuance at
$991.6bn — sixty basis points of a trillion apart.

The bond share of ETF issuance is not a one-window coincidence (C-074). Quarter by quarter it ran
**18–39%**, window 29.6%. Lowest 2024:Q4 (17.8%), highest 2026:Q1 (39.1%). Path in
`data/etf1/quarterly.csv`.

## What the ETFs bought — the instrument lens

Same table, same flows, by what the funds *hold* rather than by what they *are*:

| ETF asset flow, 2024:Q1–2026:Q2 | $bn |
|---|---:|
| Corporate equities | **+2,460.9** |
| Debt securities | **+1,059.1** |
| of which Treasuries | +318.1 |
| of which corporate and foreign bonds | +644.4 |
| of which municipals | +96.6 |
| Money-market fund shares | +30.8 |
| Unidentified miscellaneous | +53.0 |
| **= ETF share issuance** | **+3,603.8** |

The $1,142.9bn gap between ETF *share* issuance and ETF *equity* purchases is the bond/commodity
wrapper, not a residual: debt + MMF + miscellaneous = $1,142.9bn exactly. Equity-fund issuance
($2,456.5bn) and equity-holdings flow ($2,460.9bn) differ by $4.4bn because equity funds hold some
cash and bond funds are not 100% bonds. Two lenses, same $3,603.8bn, agreement to a few billion.

Mutual funds sold $2,009.0bn of corporate equity over the same window. Equity-fund issuance
exceeded that sale by $447bn — the rotation from mutual funds into equity ETFs is most of the
equity-wrapper, not all of it. The bond wrapper has no such offset inside this instrument.

## The quarterly path — do not average 2026:Q2 into the rest (C-070)

Issuance *net of ETF shares* is negative in **nine of ten quarters**. The exception is 2026:Q2
(+187.1bn), when nonfinancial corporates themselves issued +153.2bn. 2026:Q1, the EFA record
gross-issuance quarter, is −3.9bn in this identity once ETF shares are out. A two-endpoint
comparison of 2023:Q4 against 2026:Q2 would hide that the stripped identity is a retirement in
almost every quarter of the window.

## Listed versus closely-held — a stock split, and it did not move

The memo lines on F51.1.s (`data/vintages/z1_equities_2026Q2/F51_1_s.csv`, labels from the same
release's data dictionary):

| | series | 2023:Q4 $bn | 2026:Q2 $bn | share of total, both dates |
|---|---|---:|---:|---|
| Public domestic | `LM883164115` | 57,440.9 | 93,607.7 | 74.8% → 75.7% |
| Closely held | `LM883164125` | 9,745.3 | 15,637.0 | 12.7% → 12.6% |
| of which S-corps | `LM883164133` | 7,382.4 | 12,069.7 | |
| of which C-corps | `LM883164135` | 2,362.9 | 3,567.2 | |
| Rest of the world | residual of the three | 9,581.7 | 14,442.5 | 12.5% → 11.7% |
| **Total** | `LM893064105` | 76,767.8 | 123,687.2 | |

`LM883164133 + LM883164135 = LM883164125` in every quarter of the window. `public + closely held +
RoW = total` in every quarter. The older HTML vintage's `LM883164123` for closely-held is not this
release; this release's code is **125**, and the dictionary names it.

**These are levels, not flows.** 93.1% of the $46,919bn rise in the Z.1 stock is revaluation
(P1). A $5.9trn rise in closely-held *value* is not $5.9trn of closely-held *issuance*. The mix
itself is flat — listed/closely/foreign at roughly 76/13/12 at both ends of the window. What did
move inside public is the ETF wrapper: ETF shares were 14.1% of public domestic at 2023:Q4 and
16.8% at 2026:Q2 (10.5% → 12.7% of the all-sectors stock).

Nonfinancial corporates are almost all of closely-held (95.1% at the start, 94.0% at the end). The
listed NFC stock (`LM103164115`) is $68,353bn at 2026:Q2. There is no flow series for the memo
lines, so this pass cannot split the −$540.7bn NFC *flow* into listed versus closely-held. The EFA
gross-issuance decomposition (S1) remains the source for that cut on nonfinancials, and it is a
different series.

## What households bought

The household line purchased **+$3,069.4bn** of the Z.1 corporate-equities *instrument*. That
instrument's net new supply was **+$3,243.1bn of which +$3,603.8bn was ETF shares and −$360.7bn
was everything else.** Households matched the wrapper. They did not match net new operating-company
equity, because operating companies were not supplying any.

Two statements that have to travel together, and neither requires naming a natural person:

1. **The residual is still a plug.** It is defined as total minus eleven measured sectors, and it
   still closes to $0.0bn. Private equity funds and personal trusts are still inside it. LIT1 is
   still the way to name those bodies.
2. **What the plug was matching is no longer a mystery.** The only large positive issuance was ETF
   shares, and 29.6% of those shares wrap bonds. Mutual funds sold $2,009bn of the underlying
   while equity ETFs issued $2,457bn of the wrapper — most of the equity-ETF line is a change of
   vehicle, not a new claim on a company.

We do not observe household holdings of ETF shares versus listed stocks versus closely-held/PE
inside this instrument, so this pass does **not** produce a household operating-company purchase
number. Any such number would be an assumption about who holds the wrapper. The bound that does
not need that assumption: the household plug is the only holder line large enough to absorb
$3,604bn of ETF shares. Every other measured holder combined purchased +$173.7bn of the wrapper
instrument, and that +$173.7bn *includes* the ETF sector's own +$2,460.9bn of underlying stocks.

## What this does to the argument

- **"The equity base grew about a trillion a year"** was C-081. Confirmed here by rebuilding the
  identity rather than by rereading the same issuer line: issuance net of ETF shares is
  **−$360.7bn**.
- **The household-share-of-issuance claim (C-081)** was a statement about the wrapper identity.
  It is not a statement about who bought operating companies.
- **The claim that buying cannot be attributed (C-083).** Issuance is attributable. It was ETF
  share creation. The residual's *internal* composition — persons versus PE funds versus trusts,
  and ETF shares versus direct stocks — is still not split on this instrument, and that is LIT1.
  Those are different claims. The first is closed.

The S1 EFA finding is untouched: 2026:Q1 nonfinancial gross issuance was a record, and 89% of it
was private. That series does not include ETF shares. It and this identity are answers to
different questions, both true.

## Sources

- Fed Z.1, 11 Sep 2026 vintage, 2026:Q2. F51.1.t_tu / F51.1.s from `data/vintages/z1_equities_2026Q2/`;
  S124.3.s / S124.3.t_tu and data dictionaries extracted from the same release's `z1_csv_files.zip`
  on 15 Sep 2026 into `data/vintages/z1_etf1_2026Q2/`.
- ICI 2026 Fact Book Tables 11 and 13, `https://www.icifactbook.org/xls/26-fb-table-11.xlsx` and
  `.../26-fb-table-13.xlsx`, fetched 15 Sep 2026. ICI monthly ETF release for June 2026 (published
  30 Jul 2026; July 2026 release of 28 Aug 2026 carries the June column used above).
- Series labels: `data/vintages/z1_etf1_2026Q2/F51_1_s.txt`, `S124_3_s.txt`, `S124_3_t_tu.txt`.
- Computed tables: `data/etf1/issuer_identity.csv`, `quarterly.csv`, `listed_vs_closely_held.csv`.
