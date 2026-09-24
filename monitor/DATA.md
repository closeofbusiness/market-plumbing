# Data monitor

> **An extract.** The live sources are [`data/series.tsv`](../data/series.tsv) and [`CALENDAR.tsv`](../CALENDAR.tsv); where this file and they differ, they win.

Only series identified in the source and used by a claim this repository carries. Latest row is the last observation in [`data/series.tsv`](../data/series.tsv) (parent of the [`_research`](../_research) folder; file modified 21 September 2026; 463 rows, 387 keys). Frequency is taken from that file’s note when it says so, otherwise from the release the source names. Next print is from [`CALENDAR.tsv`](../CALENDAR.tsv) when a row exists. If the next print is unknown, the cell says so.

This is not the full monitor. The 11 September channel map counted 175 series and is stale against the file.

Values are hypotheses about the world even when the pull is exact. Bands are used where the source itself used a band.

## Prices and earnings

| Series | Free source | Frequency | Last observation | Next print | Used by |
|---|---|---|---|---|---|
| Earnings share of the US equity move | Decomposition in [`2026-09-11-P2a-Return-Decomposition.md`](../2026-09-11-P2a-Return-Decomposition.md) | Window, not a ticker | 71.0% to Dec 2025; 82.3% to Jun 2026 | Re-run when the next earnings window is built | [`answer/LIVE.md`](../answer/LIVE.md), fundamentals dossier |
| Tax-restated earnings share | [`2026-09-21-W3-Tax-Decomposition.md`](../2026-09-21-W3-Tax-Decomposition.md); keys `w3_etr_2015`, `w3_etr_2025`, `w3_eps_share_of_price_restated` | Annual window | Effective rate 27.4% (2015) to 19.6% (2025); restated share 74.5% | Unknown | fundamentals dossier |
| EPS split | [`2026-09-18-EPS-Split.md`](../2026-09-18-EPS-Split.md); keys `eps_split_*` | Window through Dec 2025 | Carried claim is the one-sided tenth-to-sixth band. The key `eps_split_accretion_share_of_price` is 0.134 and is the top of a weighting range, not the figure to quote | Firm panel still missing on disk upstream (C-097) | fundamentals dossier |
| Real-yield versus earnings-yield window | [`2026-09-12-P2c-Rates-vs-Risk-Premium.md`](../2026-09-12-P2c-Rates-vs-Risk-Premium.md) | Dec 2023–Jun 2026 | Real yields +0.34pt; earnings yield −0.14 | Unknown | fundamentals dossier |
| Trailing S&P PE | key `sp500_trailing_pe` | As pulled | 25.22 at 2026-06-01 | Unknown | context only; the answer does not rest on this point |

## Equity money and wrappers

| Series | Free source | Frequency | Last observation | Next print | Used by |
|---|---|---|---|---|---|
| `z1_etf_share_issuance_bn` | Z.1, 2026-09-11 vintage | 2024:Q1–2026:Q2 sum | +3,603.8 | Z.1 2026:Q3 on the calendar for 2026-12-11 | passive dossier, live answer |
| `z1_nfc_net_equity_issuance_issuer_bn` | Z.1 | same window | −540.7 | same | live answer |
| `z1_etf_bond_fund_issuance_bn` | Z.1 | same window | +1,065.0 | same | passive dossier |
| `z1_etf_commodity_fund_issuance_bn` | Z.1 | same window | +60.1 | same | commodities dossier |
| `z1_etf_equity_purchases_bn` | Z.1 | same window | +2,460.9 | same | passive dossier |
| `z1_mutualfund_equity_purchases_bn` | Z.1 | same window | −2,009.0 | same | passive dossier |
| `z1_pension_equity_purchases_bn` | Z.1 | same window | −559.4 | same | long-money dossier |
| `efa_nfc_ma_retirement_bn` | Enhanced Financial Accounts, 2025 annual in the key | Annual / quarterly keys also exist | 375.78 for 2025; quarterly key 160.15 at 2026:Q1 | Unknown as a named calendar row | live answer (M&A retirement) |
| `nfc_net_equity_issuance_q_bn` | Z.1 | Quarterly | +153.2 at 2026-06-30 | 2026-12-11 vintage | Do not confuse with the negative window total |

## Plumbing, shadow money, collateral

| Series | Free source | Frequency | Last observation | Next print | Used by |
|---|---|---|---|---|---|
| `fed_on_rrp_bn` | FRED RRPONTSYD | Daily | 0.2 on 2026-08-21 | Quarter-end cluster 2026-09-30 | official plumbing, shadow money |
| `n4_private_repo_net_of_rrp_2024_bn` | N4 arithmetic on reviewed series | 2024 | −45.7 | Recompute after the next OFR print | shadow money |
| `n4_handoff_adj_2024_bn` | same | 2024 | 136.2 | same | shadow money |
| `zk_v2_W2_M2_pct` | N2b v2 | Quarterly | 23.07 at 2026-03 | Gated on OFR Q2, still unpublished at 2026-09-24; next check 2026-10-01 | shadow money |
| `m2_h6_sa_bn` | H.6 | Monthly | 23,218 in 2026-07 | Unknown | direct money |
| `reserve_balances_bn` | FRED WRESBAL | Weekly | 2,935.3 on 2026-08-19 | Unknown | direct money |
| `bank_loans_to_nondepository_fis_bn` | H.8 | Monthly | Level 2,005.0 at 2026-07-31; 2025 flow annotated contaminated | Unknown | direct money |
| `finra_margin_debit_balances_bn` | FINRA margin workbook | Monthly | 1,453.8 in 2026-08 | Next month’s edition; source file is overwritten, so the vintage copy matters | collateral |
| `ficc_sponsored_total_bn` | DTCC sponsored volume CSV | Daily | 2,295.6 on 2026-08-20 | 2026-09-30 quarter-end pull | rates dossier, collateral |
| `ccp_im_required_15ccp_fia_bn` | FIA CCP tracker | Quarterly | 1,071.0 at 2026-03-31 | Recheck 2026-10-06 | collateral |
| `hf_collateral_posted_securities_bn` | Form PF via OFR | Quarterly | 4,924 at 2026-03-31 | Q2 still unpublished 2026-09-24 | collateral |
| `abcp_outstanding_bn` | FRED ABCOMP | Weekly | 488.4 on 2026-08-19 | Quarter-end row 2026-09-30 | shadow money |
| `stablecoin_total_outstanding_bn` | DeFiLlama free API | As pulled | 309.4 on 2026-08-29 | GENIUS rulemaking watch 2026-10-15 | shadow money |
| `collateral_velocity_range` | N3v4 | Range, not a date | 1.3–1.5 | No official aggregate; FINRA SLATE public data 2027-03-29 | collateral |

## Rates and cross-border measurements

| Series | Free source | Frequency | Last observation | Next print | Used by |
|---|---|---|---|---|---|
| `treasury_net_issuance_bn` | Z.1 | Annual | 1,930 for 2025 | 2026-12-11 | rates dossier |
| `bills_outstanding_total_bn` | FiscalData MSPD | Month-end | 6,988.9 at 2026-07-31 | Unknown | rates dossier |
| `fed_treasury_purchases_flow_bn` | Z.1 | Quarterly | +97.8 at 2026-06-30 | 2026-12-11 | official plumbing |
| `mmf_treasury_flow_bn` | Z.1 / OFR context in the note | Quarterly | −144.9 at 2026-06-30 | same | official plumbing |
| `tic_table5_foreign_official_ust_bn` | TIC Table 5 | Monthly | 3,773.1 at 2026-07 | Next TIC; July was pulled 17 Sep | official plumbing |
| `tic_table5_japan_ust_bn` | TIC Table 5 | Monthly | 1,103.9 at 2026-07 (−12.8 on the month, per the note) | same | official plumbing |
| `tic_table5_china_ust_bn` | TIC Table 5 | Monthly | 618.0 at 2026-07 | same | official plumbing |
| `tic_cslt_foreign_net_us_equity_bn` | TIC CSLT | Monthly | 2.778 at 2026-07 | same | cross-border |
| `fx_usd_leg_total_trn` | BIS, as recorded in N2a | Semiannual | 113.5 in 2025-S2 | BIS LBS row on the calendar is 2027-01-18 for a different series | cross-border |
| `bis_usd_liab_cayman_nonbank_bn` | BIS | Quarterly | 1,025.0 in 2026-Q1 | Unknown | cross-border |
| `gpif_aum_jpy_trn` | GPIF | Quarterly | 320.4 at 2026-06-30 | Jul–Sep results about early Nov 2026 | cross-border; not a JGB-buying result |

## AI funding and IPOs

| Series | Free source | Frequency | Last observation | Next print | Used by |
|---|---|---|---|---|---|
| Lease stack versus guarantees | Hand-read 10-Ks, [`2026-08-22-Guarantee-Stack.md`](../2026-08-22-Guarantee-Stack.md) | Quarterly hand-read | 1,122.9 versus 228.3 contracted; 86.2 live at 22 Aug | 2026-11-15 for the lease note; 2026-09-30 for two guarantee maturities | AI dossier |
| `oracle_internal_cash_vs_capex_gap_bn` | Oracle filing | Quarterly | −34.9 at 2026-08-31 | Next 10-Q | AI dossier |
| `oracle_rpo_bn` | Oracle filing | Quarterly | 664 at 2026-08-31 | same | AI dossier |
| `oracle_offbs_lease_commitments_bn` | Oracle filing | Quarterly | 288 at 2026-08-31 | same | AI dossier |
| `amazon_delayed_draw_term_loan_bn` | Amazon filing | Point | 17.5 undrawn at 2026-06-30 | Window 2026-09-30; 10-Q is later | AI dossier |
| `spacex_ipo_primary_bn` | Prospectus fact table | Deal | 75.0 on 2026-06-11 | Unknown | IPO dossier |

## Explicitly absent

No series in this extract for JGB net supply, euro-area government-bond net supply, a cross-currency basis, commodity inventories, producer hedges, or managed-money futures positions. They are not omitted by accident. They were not identified as worked series in the notes this monitor is drawn from.
