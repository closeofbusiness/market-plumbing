# Migration record, 24 September 2026

Vault copied into https://github.com/closeofbusiness/market-plumbing from the live tree. The Dropbox vault was not modified. This file is the exclusion list. It does not restate findings.

## Assumptions

- CC BY 4.0 was already on `LICENSE`. No second license was added. `LICENSE` was not edited.
- The federal exception was applied as Fed Board, SEC, and Treasury only. FDIC, the Department of Labor, FERC, the New York Fed, the Chicago Fed, and raw ALFRED/FRED downloads were excluded. That reading of the parenthetical is an assumption. Marked UNCERTAIN where the file is a US government work outside those three.
- OFR files were committed as Treasury. OFR is a bureau of the Treasury. Assumption, from the agency's status, not from a terms page read this session.
- FSOC annual reports were committed as US government works. Assumption.
- `shl2025r.pdf` and its appendix were committed. The first page names the Treasury, the New York Fed, and the Board together. Treated as a Treasury publication.
- `data/history` CSVs whose `series.tsv` source is FiscalData, OFR, H.8, or a FRED id the pull script labels as a mirror of a Fed release were committed as our two-column caches of those series. Raw FRED and ALFRED files under `data/vintages/` were not. The FRED terms page was not read this session; the committed files are the script's cache, and the series identity is the Board or Treasury series named in `pull_series.py`.
- `SEC_UA` is the User-Agent header value. Scripts that had the address hardcoded now read `os.environ["SEC_UA"]`. Nothing in the repo supplies a default.
- The new commit uses the author already on `main` (`MartinS <289195898+martinukphd-art@users.noreply.github.com>`). The local git identity is the gmail address. It was not used for this commit, so the address is not added to a new commit object.

## Counts against the 24 Sep stamp

Stamp: corrections=119 max=C-119 ask=9 series=463 docs=115 calendar=49.

In this tree, after the copy: corrections=119, max=C-119, ask=9, series=463 (`wc -l data/series.tsv` is 464, minus the header), calendar=49 (`wc -l CALENDAR.tsv` is 50, minus the header).

docs=117. The stamp counts top-level `*.md`. The vault has 115. This repo already had `README.md` and `CHARTER.md`. No vault top-level markdown file was excluded.

## Scrub

The address was removed from the 15 files that were committed. Two files were not scrubbed and were not committed: `_research/inbox_harvest_lenses.md` and `_research/inbox_harvest_raw.json`. Removing the address there would rewrite which mailbox was searched. Those files also contain other personal and employer mailbox addresses.

Scripts now read `SEC_UA`: `bin/pull_series.py`, `bin/census_abcp_all.py`, `bin/census_nmfp3.py`, `bin/census_nmfp3_all_positions.py`, `bin/top10_earnings_vs_weight.py`.

The `ua` field was dropped from `data/w3_tax/results.json`. The `user_agent_sec` row was dropped from `data/p5i_event_study/00_methodology_and_sources.csv`.

No `api_key`, `Bearer`, or `sk-` secret was found. `bin/pull_series.py` still contains `FIA_KEY`, sent as an `Authorization` header. The script's own comment says it is the page-embedded key every browser sends. It was left in place. Removing it would rewrite the fetch. Reported, not fixed.

`pull_series.py` still sends one User-Agent to every host, including hosts that are not sec.gov. That was already true. Not changed.

`bin/top10_earnings_vs_weight.py` docstring still says the User-Agent is the Mozilla string with no email, while `USER_AGENT_SEC` is now `SEC_UA`. The docstring did not contain the address. Not rewritten.

## Paid and press quote test

Committed unchanged, as already checked: `2026-08-23-FT-Harvest-ABCP-Conduits-And-Equity-Repo.md`, `2026-09-11-Green-Substack-And-Ep61-Synthesis.md`, `2026-09-11-Green-Passive-Bid-Corpus-Dossier.md`, `_research/2026-09-11-Green-Ep61-Official-Claims.md`.

Green Substack cards and the Treasury-Japan cards were tested here. Every anchor quote counted at or under 15 words. They were committed. Same-line spans over 15 words in those files were citation lists broken across a quotation mark, not a continuous quotation.

`_research/SB1_Briefing_Verify_Return_paste.md` contains an ellipsis quotation from IMF WP/19/106 of about 18 words. That source is a free working paper, not paid or press. The file was committed. UNCERTAIN if the 15-word rule was meant to cover it.

## What was not copied

227 vault paths were not committed. 204 were excluded on the first pass. 23 more series files were removed from the index before the first push of vault content, so they are not in published history. `data/THIRD_PARTY_MANIFEST.tsv` has 184 data rows: path, source URL, fetch date, sha256, size, and reason. It includes the third-party files and the three gitignored XML files. Persona files are not in that manifest.

### UNCERTAIN or third-party raw file; terms not a named federal exception (76)

- `data/retirement_docs/dol_abstract_2018.pdf`
- `data/retirement_docs/dol_abstract_2018.xlsm`
- `data/retirement_docs/dol_abstract_2023.pdf`
- `data/retirement_docs/dol_abstract_2023.xlsx`
- `data/retirement_docs/dol_historical_tables_and_graphs.pdf`
- `data/retirement_docs/dol_historical_tables_and_graphs.xlsx`
- `data/retirement_docs/ici_factbook_2026_ch8.pdf`
- `data/retirement_docs/ici_factbook_2026_data_ch8.zip`
- `data/retirement_docs/ici_factbook_data_ch8/8.1.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/8.10.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/8.11.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/8.12.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/8.13.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/8.14.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/8.15.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/8.16.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/8.2.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/8.3.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/8.4.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/8.5.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/8.6.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/8.7.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/8.8.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/8.9.xlsx`
- `data/retirement_docs/ici_factbook_data_ch8/data_methods_and_assumptions.txt`
- `data/retirement_docs/ici_factbook_table_63.xlsx`
- `data/retirement_docs/ici_factbook_table_64.xlsx`
- `data/retirement_docs/ici_retirement_market_2026_q1_data.xls`
- `data/vintages/alfred/alf_M2SL_2026-07-01.csv`
- `data/vintages/alfred/alf_M2SL_2026-08-15.csv`
- `data/vintages/alfred/alf_MDLM_2026-07-01.csv`
- `data/vintages/alfred/alf_MDLM_2026-08-15.csv`
- `data/vintages/alfred/alf_RMFSL_2026-07-01.csv`
- `data/vintages/alfred/alf_RMFSL_2026-08-15.csv`
- `data/vintages/alfred/alf_STDSL_2026-07-01.csv`
- `data/vintages/alfred/alf_STDSL_2026-08-15.csv`
- `data/vintages/alfred/alf_WRMFSL_2026-07-01.csv`
- `data/vintages/alfred/alf_WRMFSL_2026-08-15.csv`
- `data/vintages/alfred/alf_WSAVNS_2026-07-01.csv`
- `data/vintages/alfred/alf_WSAVNS_2026-08-15.csv`
- `data/vintages/capitolis/CLGM_SoFC_2024-01-31.pdf`
- `data/vintages/capitolis/CLGM_SoFC_2024-07-31.pdf`
- `data/vintages/capitolis/CLGM_SoFC_2025-01-31.pdf`
- `data/vintages/capitolis/CLGM_SoFC_2025-07-31.pdf`
- `data/vintages/capitolis/CLGM_SoFC_2026-01-31.pdf`
- `data/vintages/ccp_pqd_2026Q1/CCPG_PQD_NF_25Q1.pdf`
- `data/vintages/ccp_pqd_2026Q1/CCPG_PQD_QTR_Q1_2026.pdf`
- `data/vintages/ccp_pqd_2026Q1/CME_DataFile_2026Q1.zip`
- `data/vintages/ccp_pqd_2026Q1/DTCC-PQD-026Q1.xlsx`
- `data/vintages/ccp_pqd_2026Q1/ECAG_PQD_2026Q1.xlsx`
- `data/vintages/ccp_pqd_2026Q1/ICC_QuantitativeDisclosures_2026Q1.zip`
- `data/vintages/ccp_pqd_2026Q1/ICEU_QuantitativeDisclosures_2026Q1.zip`
- `data/vintages/ccp_pqd_2026Q1/ICUS_QuantitativeDisclosures_2026Q1.zip`
- `data/vintages/ccp_pqd_2026Q1/JSCC_PQD_2026Q1.xlsx`
- `data/vintages/ccp_pqd_2026Q1/OCC_PQD_2026Q1.xlsx`
- `data/vintages/ccp_pqd_2026Q1/ltd-ccp12-pqd-q1-2026.xlsx`
- `data/vintages/ccp_pqd_2026Q1/sa-ccp12-pqd-q1-2026.xlsx`
- `data/vintages/damodaran_erp_2026-09-13/ERPbymonth.xlsx`
- `data/vintages/dtcc/SponsoredVolume_pulled_2026-08-23.csv`
- `data/vintages/dtcc/dtcc_gcfindex_pulled_2026-08-23.csv`
- `data/vintages/dtcc/dtcc_gsd_monthly_volume_2001-2026_scraped_2026-08-23.csv`
- `data/vintages/fia/fia_ccp_initial_margin_2015Q3-2026Q1_pulled_2026-08-23.csv`
- `data/vintages/finra/finra_margin_statistics_2026-08-21.xlsx`
- `data/vintages/finra/finra_margin_statistics_2026-08-24.xlsx`
- `data/vintages/finra/finra_margin_statistics_2026-08-30.xlsx`
- `data/vintages/finra/finra_margin_statistics_2026-08-31.xlsx`
- `data/vintages/finra/finra_margin_statistics_2026-09-18.xlsx`
- `data/vintages/ici_etf_2026/26-fb-table-11.xlsx`
- `data/vintages/ici_etf_2026/26-fb-table-13.xlsx`
- `data/vintages/isda_actrix/ISDA_Actrix_June2026.pdf`
- `data/vintages/isda_actrix/ISDA_Actrix_June2026.txt`
- `data/vintages/isla/isla_market_data_2026-03-31_read_2026-08-29.json`
- `data/vintages/shiller_2026-09-02/FRED_DFII10.csv`
- `data/vintages/shiller_2026-09-02/FRED_DGS10.csv`
- `data/vintages/shiller_2026-09-02/ie_data.xls`
- `data/vintages/stablecoins/defillama_total_daily_pulled_2026-08-29.csv`

### UNCERTAIN: series cache from a source outside Fed Board, SEC, and Treasury (37)

- `data/history/capitolis_clgm_affiliate_revolver_bn.csv`
- `data/history/capitolis_clgm_total_assets_bn.csv`
- `data/history/ccp_im_asx_fia_bn.csv`
- `data/history/ccp_im_cme_fia_bn.csv`
- `data/history/ccp_im_eurex_fia_bn.csv`
- `data/history/ccp_im_hkex_fia_bn.csv`
- `data/history/ccp_im_ice_clear_credit_fia_bn.csv`
- `data/history/ccp_im_ice_clear_europe_fia_bn.csv`
- `data/history/ccp_im_ice_clear_us_fia_bn.csv`
- `data/history/ccp_im_jscc_fia_bn.csv`
- `data/history/ccp_im_lch_ltd_fia_bn.csv`
- `data/history/ccp_im_lch_sa_fia_bn.csv`
- `data/history/ccp_im_lme_fia_bn.csv`
- `data/history/ccp_im_nasdaq_clearing_fia_bn.csv`
- `data/history/ccp_im_nasdaq_fia_bn.csv`
- `data/history/ccp_im_occ_fia_bn.csv`
- `data/history/ccp_im_required_15ccp_fia_bn.csv`
- `data/history/ccp_im_sgx_fia_bn.csv`
- `data/history/ccp_im_tmx_fia_bn.csv`
- `data/history/ficc_gsd_monthly_net_obligations_trn.csv`
- `data/history/ficc_gsd_monthly_value_compared_trn.csv`
- `data/history/ficc_sponsored_dvp_bn.csv`
- `data/history/ficc_sponsored_gc_bn.csv`
- `data/history/ficc_sponsored_repo_bn.csv`
- `data/history/ficc_sponsored_reverse_repo_bn.csv`
- `data/history/ficc_sponsored_total_bn.csv`
- `data/history/finra_free_credit_cash_bn.csv`
- `data/history/finra_free_credit_margin_bn.csv`
- `data/history/finra_margin_debit_balances_bn.csv`
- `data/history/pd_ust_repo_out_bn.csv`
- `data/history/pd_ust_repo_sponsored_bn.csv`
- `data/history/pd_ust_repo_triparty_gc_bn.csv`
- `data/history/pd_ust_rev_sponsored_dvp_bn.csv`
- `data/history/pd_ust_rev_uncleared_bilateral_bn.csv`
- `data/history/pd_ust_reverse_in_bn.csv`
- `data/history/stablecoin_total_outstanding_bn.csv`
- `data/history/uninsured_deposits_all_insts_bn.csv`

### third-party source text or UNCERTAIN terms; not Fed Board, SEC, or Treasury (34)

- `_research/primary_sources/AdrianAshcraftBoeskyPozsar_ShadowBanking_NYFed_SR458.pdf`
- `_research/primary_sources/AdrianAshcraftBoeskyPozsar_ShadowBanking_NYFed_SR458.txt`
- `_research/primary_sources/FSB_2026-02-04_Govt_Bond_Repo_Vulnerabilities.pdf`
- `_research/primary_sources/FSB_2026-02-04_Govt_Bond_Repo_Vulnerabilities.txt`
- `_research/primary_sources/IMF_WP19106_Singh_Goel_2019_Pledged_Collateral.pdf`
- `_research/primary_sources/IMF_WP19106_Singh_Goel_2019_Pledged_Collateral.txt`
- `_research/primary_sources/PozsarSingh_2011_IMF_WP11289_NonbankBankNexus.pdf`
- `_research/primary_sources/PozsarSingh_2011_IMF_WP11289_NonbankBankNexus.txt`
- `_research/primary_sources/Pozsar_2011_IMF_WP11190_InstitutionalCashPools.pdf`
- `_research/primary_sources/Pozsar_2011_IMF_WP11190_InstitutionalCashPools.txt`
- `_research/primary_sources/Singh_2026-01-12_Risknet_Collateral_Velocity_Digital_Curtain.txt`
- `_research/primary_sources/collateral_reuse/ccp_pqd_q4_2025.pdf`
- `_research/primary_sources/collateral_reuse/ecb_wp3147.pdf`
- `_research/primary_sources/collateral_reuse/isda_margin_survey_ye2025.pdf`
- `_research/primary_sources/ferc_el26_reports/CAISO_order.txt`
- `_research/primary_sources/ferc_el26_reports/CAISO_report_EL26-71.pdf`
- `_research/primary_sources/ferc_el26_reports/CAISO_rescission_abeyance_order.bin`
- `_research/primary_sources/ferc_el26_reports/ISONE_report_EL26-72.pdf`
- `_research/primary_sources/ferc_el26_reports/MISO_report_EL26-70.pdf`
- `_research/primary_sources/ferc_el26_reports/NGSA_comments_all.pdf`
- `_research/primary_sources/ferc_el26_reports/NYISO_report_EL26-69.pdf`
- `_research/primary_sources/ferc_el26_reports/OMS_comments_EL26-70.pdf`
- `_research/primary_sources/ferc_el26_reports/PJM_report_EL26-67.pdf`
- `_research/primary_sources/ferc_el26_reports/SPP_report_EL26-68.pdf`
- `_research/primary_sources/ferc_el26_reports/Sparkfund_comments_EL26-70.pdf`
- `_research/primary_sources/funding_closure/fdic_article.pdf`
- `_research/primary_sources/funding_closure/imf_execsum.pdf`
- `_research/primary_sources/offshore_dollar/CPIS_June2025_377PI6_2025S1.xlsx`
- `_research/primary_sources/offshore_dollar/bis_bulletin27_dollar_funding_swap_lines.pdf`
- `_research/primary_sources/offshore_dollar/bis_qt2212h_dollar_debt_fx_swaps.pdf`
- `_research/primary_sources/offshore_dollar/cbi_ie_mmf_all_series_2026-06.xlsx`
- `_research/primary_sources/offshore_dollar/cssf_mmf_dashboard_2025.pdf`
- `_research/primary_sources/offshore_dollar/q1-2026-derivatives-quarterly.pdf`
- `_research/primary_sources/treasury_clearing/TMPG-White-Paper-05222025.pdf`

### snapshot tree; git history replaces it (21)

- `_research/snapshot_2026-09-11/2026-08-23-FT-Harvest-ABCP-Conduits-And-Equity-Repo.md`
- `_research/snapshot_2026-09-11/CLAUDE.md`
- `_research/snapshot_2026-09-11/CORRECTIONS.md`
- `_research/snapshot_2026-09-11/MD5SUMS.txt`
- `_research/snapshot_2026-09-11/RESEARCH_STATE.md`
- `_research/snapshot_2026-09-11/bin/check.sh`
- `_research/snapshot_2026-09-11b/CALENDAR.tsv`
- `_research/snapshot_2026-09-11b/CLAUDE.md`
- `_research/snapshot_2026-09-11b/MD5SUMS.txt`
- `_research/snapshot_2026-09-11b/RESEARCH_STATE.md`
- `_research/snapshot_2026-09-11b/census_nmfp3_all_positions.py.pre-fix`
- `_research/snapshot_2026-09-11c/CALENDAR.tsv`
- `_research/snapshot_2026-09-11c/CLAUDE.md`
- `_research/snapshot_2026-09-11c/MD5SUMS.txt`
- `_research/snapshot_2026-09-11c/RESEARCH_STATE.md`
- `_research/snapshot_2026-09-11c/THE_ASK.md`
- `_research/snapshot_2026-09-11d/CALENDAR.tsv`
- `_research/snapshot_2026-09-11d/CLAUDE.md`
- `_research/snapshot_2026-09-11d/MD5SUMS.txt`
- `_research/snapshot_2026-09-11d/RESEARCH_STATE.md`
- `_research/snapshot_2026-09-11d/THE_ASK.md`

### HOLD OUT pending the principal's ruling (12)

- `Analysis/Panel_Individual_Reads.md`
- `Analysis/Panel_Synthesis.md`
- `Personas/Persona_George_Soros.md`
- `Personas/Persona_Ken_Griffin.md`
- `Personas/Persona_Michael_Burry.md`
- `Personas/Persona_Stanley_Druckenmiller.md`
- `Personas/Persona_Usage_Guide.md`
- `_research/panel_raw.json`
- `_research/paragon_burry_dossier.md`
- `_research/paragon_druckenmiller_dossier.md`
- `_research/paragon_griffin_dossier.md`
- `_research/paragon_soros_dossier.md`

### third-party paper extract; not Fed Board/SEC/Treasury (9)

- `data/vintages/lit1_2026-09-15/crossref_holmquist.json`
- `data/vintages/lit1_2026-09-15/crossref_rosenthal_mucciolo.json`
- `data/vintages/lit1_2026-09-15/crossref_szz.json`
- `data/vintages/lit1_2026-09-15/rosenthal_burke_2020.txt`
- `data/vintages/lit1_2026-09-15/rosenthal_burke_2020_whos_left_to_tax.pdf`
- `data/vintages/lit1_2026-09-15/rosenthal_mucciolo_2024_taxnotes_html_extract.txt`
- `data/vintages/lit1_2026-09-15/rosenthal_mucciolo_2024_tpc_pdf_extract.txt`
- `data/vintages/lit1_2026-09-15/smith_zidar_zwick_2023.txt`
- `data/vintages/lit1_2026-09-15/smith_zidar_zwick_2023_top_wealth.pdf`

### generated or filesystem metadata (4)

- `.DS_Store`
- `_research/.DS_Store`
- `data/.DS_Store`
- `data/vintages/.DS_Store`

### Fed Board XML named for .gitignore; not copied (H41 120MB class, two H8 copies) (3)

- `data/a1_money_creation/H41_data.xml`
- `data/a1_money_creation/H8_data.xml`
- `data/a1_money_creation/h8_data/H8_data.xml`

### SMB delete residue, not a vault document (2)

- `.smbdeleteAAA82ca4.4`
- `.smbdeleteBAA82ca4.4`

### UNCERTAIN: Chicago Fed Insights is not a Board release; terms not read (2)

- `data/vintages/chicagofed_ai_tail_risk_2026-02/ai-tail-risk-for-banks_fetched_2026-09-23.html`
- `data/vintages/chicagofed_ai_tail_risk_2026-02/ai-tail-risk-for-banks_fetched_2026-09-23.txt`

### backup; git history replaces it (2)

- `_research/check.sh.pre-C100-fix-2026-09-22.bak`
- `_research/check.sh.pre-page-check-2026-09-23.bak`

### personal inboxes; removing the address would rewrite which mailbox was searched, and other personal addresses are in the file (2)

- `_research/inbox_harvest_lenses.md`
- `_research/inbox_harvest_raw.json`

### removed before the first push: full third-party series saved as CSV, not a calculated table (23)

A first pass treated any CSV under `data/` that was not a known raw download as "our own derived CSV". These 23 are the publisher's series, reshaped. Terms were not read. They were deleted from the work tree and listed in the manifest before the content commit.

Yahoo Finance price series; terms UNCERTAIN (1):

- `data/p5i_event_study/03_daily_sp500_price_raw.csv`

Yale/Shiller confidence index, full series reshaped; terms not read (1):

- `data/p5_third_measure/yale_shiller_stock_market_confidence_indices.csv`

Philadelphia Fed SPF; not a Board release (1):

- `data/p5_third_measure/philly_fed_spf_stock10_bond10_bill10.csv`

New York Fed SCE series; not a Board release (1):

- `data/p5_third_measure/nyfed_sce_stock_price_expectations.csv`

Richmond Fed / Duke CFO survey; terms not read (1):

- `data/p5_third_measure/richmond_duke_cfo_survey_sp500_expected_return.csv`

GPIF published tables; terms not read (5):

- `data/bridge_firststage/gpif/gpif_allocation_quarterly.csv`
- `data/bridge_firststage/gpif/gpif_aum_quarterly.csv`
- `data/bridge_firststage/gpif/gpif_band_gap_summary.csv`
- `data/bridge_firststage/gpif/gpif_foreign_equity_us_share_annual.csv`
- `data/bridge_firststage/gpif/gpif_policy_asset_mix_bands.csv`

NBIM published tables; terms not read (6):

- `data/bridge_firststage/nbim/nbim_band_crossings.csv`
- `data/bridge_firststage/nbim/nbim_equity_share.csv`
- `data/bridge_firststage/nbim/nbim_fund_value.csv`
- `data/bridge_firststage/nbim/nbim_inflows.csv`
- `data/bridge_firststage/nbim/nbim_rebalancing_rule_history.csv`
- `data/bridge_firststage/nbim/nbim_us_share.csv`

DNB, EIOPA, ECB, or UK Purple Book table; terms not read (7):

- `data/e1_european_pensions/01_dnb_nl_system_size_and_transition.csv`
- `data/e1_european_pensions/02_wtp_statutory_schedule.csv`
- `data/e1_european_pensions/03_eiopa_nl_balance_sheet_by_scheme_type.csv`
- `data/e1_european_pensions/04_eiopa_eu_country_comparison.csv`
- `data/e1_european_pensions/05_ecb_pfbr_nl_key_series.csv`
- `data/e1_european_pensions/06_uk_purple_book_2025_summary.csv`
- `data/e1_european_pensions/07_cross_source_total_assets_reconciliation.csv`

Kept, and marked UNCERTAIN: `data/b6_phase1/daily_payment_yield.csv` is a regression panel whose header includes `spy_ret` and `gspc_ret`. The vendor terms for those return columns were not read. It was left in as a calculated panel. Not removed.

Kept: `data/e1_european_pensions/00_methodology_and_sources.csv`, `data/p5_third_measure/00_candidate_verdicts.csv`, and `data/bridge_firststage/tic/`. Those are methodology notes or Treasury TIC and SEC 13F extracts.

`_research/RESEARCH_STATE.md.bak-live-before-permanent-close-swap` and `_research/RESEARCH_STATE.md.bak-pre-tierb-permanent-close` were committed. The exclusion was `*.bak`. These names do not end in `.bak`.

## Committed references to excluded paths

Not edited. Line numbers are in this tree.

- `CORRECTIONS.md:26` cites `Panel_Synthesis.md`
- `CORRECTIONS.md:845` cites `_research/check.sh.pre-C100-fix-2026-09-22.bak`
- `CORRECTIONS.md:1662` cites `Panel_Synthesis.md`
- `CORRECTIONS.md:1663` cites `Panel_Individual_Reads.md`
- `HANDOVER.tsv:50` cites `paragon_burry_dossier.md`
- `RESEARCH_STATE.md:613` cites `paragon_burry_dossier.md`
- `RESEARCH_STATE.md:764` cites `snapshot_2026-09-11`
- `RESEARCH_STATE.md:770` cites `snapshot_2026-09-11`
- `2026-09-12-Oracle-RPO-And-Financing.md:5` cites `Panel_Synthesis.md`
- `CALENDAR.tsv:7` cites `Panel_Synthesis.md`
- `CALENDAR.tsv:8` cites `Panel_Synthesis.md`
- `CALENDAR.tsv:9` cites `Panel_Synthesis.md`
- `CALENDAR.tsv:15` cites `Panel_Synthesis.md`
- `CALENDAR.tsv:20` cites `Panel_Individual_Reads.md`
- `CALENDAR.tsv:23` cites `Panel_Individual_Reads.md`
- `CALENDAR.tsv:27` cites `Panel_Individual_Reads.md`
- `CLAUDE.md:438` cites `Personas/`
- `CLAUDE.md:446` cites `Panel_Synthesis.md`
- `CLAUDE.md:448` cites `Panel_Individual_Reads.md`
- `CLAUDE.md:648` cites `Personas/`
- `_research/RESEARCH_STATE.md.bak-live-before-permanent-close-swap:651` cites `snapshot_2026-09-11`
- `_research/RESEARCH_STATE.md.bak-live-before-permanent-close-swap:657` cites `snapshot_2026-09-11`
- `_research/RESEARCH_STATE.md.bak-pre-tierb-permanent-close:651` cites `snapshot_2026-09-11`
- `_research/RESEARCH_STATE.md.bak-pre-tierb-permanent-close:657` cites `snapshot_2026-09-11`
- `_research/2026-09-11-Channel-Map-Gaps.md:22` cites `inbox_harvest_lenses.md`
- `_research/2026-09-11-Channel-Map-Gaps.md:25` cites `inbox_harvest_lenses.md`
- `_research/2026-09-11-Channel-Map-Gaps.md:31` cites `inbox_harvest_lenses.md`
- `_research/2026-09-11-Channel-Map-Gaps.md:37` cites `snapshot_2026-09-11`
- `_research/LADDER_reentry_repair_2026-09-11.md:115` cites `Personas/`
- `_research/LADDER_reentry_repair_2026-09-11.md:130` cites `snapshot_2026-09-11`
- `_research/LADDER_reentry_repair_2026-09-11.md:132` cites `snapshot_2026-09-11`
- `_research/LADDER_reentry_repair_2026-09-11.md:147` cites `Personas/`
- `_research/SPEC_reentry_infrastructure_2026-09-11.md:20` cites `snapshot_2026-09-11`
- `_research/SPEC_reentry_infrastructure_2026-09-11.md:46` cites `Personas/`
- `_research/2026-09-11-Channel-Map-Docs.tsv:95` cites `inbox_harvest_lenses.md`
- `_research/2026-09-11-Channel-Map-Docs.tsv:99` cites `paragon_burry_dossier.md`
- `_research/2026-09-11-Channel-Map-Docs.tsv:100` cites `paragon_druckenmiller_dossier.md`
- `_research/2026-09-11-Channel-Map-Docs.tsv:101` cites `paragon_griffin_dossier.md`
- `_research/2026-09-11-Channel-Map-Docs.tsv:102` cites `paragon_soros_dossier.md`
- `Report/Third_Derivative_Report.html:735` cites `Personas/`
- `data/series.tsv:292` cites `gpif_allocation_quarterly.csv`
- `data/p5_third_measure/00_candidate_verdicts.csv:3` cites `richmond_duke_cfo_survey_sp500_expected_return.csv`
- `data/p5_third_measure/00_candidate_verdicts.csv:4` cites `philly_fed_spf_stock10_bond10_bill10.csv`
- `data/p5_third_measure/00_candidate_verdicts.csv:5` cites `yale_shiller_stock_market_confidence_indices.csv`
- `data/p5_third_measure/00_candidate_verdicts.csv:6` cites `nyfed_sce_stock_price_expectations.csv`

## Resync

No vault file had a modification time after 2026-09-24 08:08:27 CEST at the check immediately before the content commit (08:29 CEST). Nothing was re-copied.

## Check, not fixed

`bin/check.sh --all` goal line matched. M6, M7, and M8 passed. The page check passed. The orphan check did not: `CHARTER.md`, `README.md`, `.git/`, `dossiers/`, and `monitor/` have no read-table row. `answer/` and `corrections/` were not flagged because the read table contains the substrings `answer` and `corrections` inside other rows. Three killed-claim hits are in programme files that were already on main: `answer/LIVE.md:16` [C-078], `corrections/REGISTER.md:35` [C-078], `dossiers/direct-money-creation.md:13` [C-089]. Not edited.
