# N2a-S return — Gemini, received 2026-08-30 as chat paste (no file landed on the share root this time)
# Preserved verbatim below. Verification: see N2aS_verification_2026-08-30.md

Q1: BIS Locational Banking Statistics (LBS)
  PUBLISHER/TABLE: Bank for International Settlements (BIS) / Table A6.2 ("Cross-border positions, by residence and sector of counterparty") and BIS Data Portal dataset WS_LBS_D_PUB
  URL: https://data.bis.org/topics/LBS (Bulk download: https://data.bis.org/bulkdownload)
  FREQUENCY: Quarterly (approx. one-quarter publication lag)
  VARIABLES: Measure: Liabilities (L); Position type: Cross-border (C); Currency: US Dollar (USD); Sector of counterparty: Non-bank financial institutions (N) and Non-financial sector (P); Residence of counterparty: Counterparty country code (e.g., KY, BM, GB, LU); Reporting country: All reporting countries (5A).
  CAVEAT: Captures residence of the immediate booking counterparty without look-through to the beneficial owner or parent entity, and excludes non-reporting offshore banking centers.

Q2: IMF Coordinated Portfolio Investment Survey (CPIS) — Cayman Islands Reporter Series
  PUBLISHER/TABLE: International Monetary Fund (IMF) & Cayman Islands Monetary Authority (CIMA) / CPIS Table 1 ("Portfolio Investment Assets: Reporting Economy: Cayman Islands; Counterparty Economy: United States")
  URL: https://data.imf.org/?sk=B98782E4-F080-424B-9EA2-B92A44B08688 (IMF CPIS Portal) / CIMA release page: https://www.cima.ky/investments-statistics-digest
  FREQUENCY: Semi-annual (end-June and end-December; approx. 9-month lag)
  VARIABLES: Portfolio investment assets by instrument: Equity and investment fund shares, Long-term debt securities (US Treasuries, corporate bonds), Short-term debt securities (Treasury bills, commercial paper) issued by US residents.
  CAVEAT: Records the legal residence of the fund vehicle (Cayman Islands) rather than the location of the investment manager or ultimate beneficial investors (look-through unavailable).

Q3: IMMFA IRIS Statistics & Central Bank of Ireland Money Market Fund Balance Sheet Statistics
  PUBLISHER/TABLE: Institutional Money Market Funds Association (IMMFA) / IRIS Money Fund Report; Central Bank of Ireland (CBI) / Table B.4.1 ("Money Market Funds Balance Sheet by Currency Denomination: USD")
  URL: https://www.immfa.org/information/statistics.html (IMMFA) and https://www.centralbank.ie/statistics/data-and-analysis/funds-statistics/money-market-funds (CBI)
  FREQUENCY: Weekly for IMMFA (2–3 day lag); Monthly and Quarterly for Central Bank of Ireland (approx. 1-month lag)
  VARIABLES: USD Net Asset Value / AUM by fund type (LVNAV, Public Debt CNAV, VNAV); Asset composition breakdown: Certificates of Deposit, Commercial Paper, US Treasury/Sovereign Bills, Repurchase Agreements (Repo), Bank Deposits; WAM, WAL, and Weekly Liquid Assets (% WLA).
  CAVEAT: IMMFA is a voluntary industry association limited to member European funds (primarily Dublin/Luxembourg-domiciled UCITS/AIFs), while official EU MMFR Article 37 supervisory data is published only in periodic aggregate reports rather than granular public time series tables.

Q4: US Treasury International Capital (TIC) System: Major Foreign Holders (MFH) & Form SHL Benchmarks
  PUBLISHER/TABLE: U.S. Department of the Treasury / Table MFH ("Major Foreign Holders of Treasury Securities", file: mfh.txt) and Annual Survey Form SHL/SHLA ("Foreign Portfolio Holdings of U.S. Securities")
  URL: https://ticdata.treasury.gov/Publish/mfh.txt and https://www.treasury.gov/resource-center/data-chart-center/tic/Pages/fpis.aspx
  FREQUENCY: Monthly for MFH (approx. 45-day lag); Annual for SHL benchmark surveys (as of June 30)
  VARIABLES: Country-level holdings of US Treasury bills, bonds, and notes by foreign residents (separate lines for Cayman Islands, Belgium, United Kingdom, Luxembourg, Switzerland).
  CAVEAT: TIC tables record holdings based on the immediate foreign custodian and do NOT separate custodial bias; NO official regularly updated custodial-bias-corrected statistical series is published by Treasury/Fed (corrections exist only as ad-hoc Federal Reserve research papers).

Q5: SEC Private Funds Statistics
  PUBLISHER/TABLE: U.S. Securities and Exchange Commission (SEC), Division of Investment Management, Analytics Office / Table 3.1 ("Fund Domicile (Percent of Aggregate NAV)") and Table 3.2 ("Fund Domicile (Percent of Aggregate Gross Asset Value)")
  URL: https://www.sec.gov/divisions/investment/private-funds-statistics [Search path: sec.gov -> "Private Fund Statistics"]
  FREQUENCY: Quarterly (approx. 6-to-8-month lag)
  VARIABLES: Percentage of Aggregate Net Asset Value (NAV) and Gross Asset Value (GAV) by jurisdiction of domicile (United States, Cayman Islands, Bermuda, Ireland, Luxembourg, Other) across fund types (Hedge Funds, Qualifying Hedge Funds, Private Equity).
  CAVEAT: Measures only SEC-registered investment advisers meeting Form PF filing thresholds and reflects legal incorporation domicile rather than the operational location of the adviser.

Q6: BIS Global Liquidity Indicators (GLI) & Federal Reserve H.8 Statistical Release
  PUBLISHER/TABLE: Bank for International Settlements (BIS) / Table E2.1 ("US dollar credit to non-bank borrowers outside the United States", data structure WS_GLI); Board of Governors of the Federal Reserve System / Release H.8 ("Assets and Liabilities of Commercial Banks in the United States", Foreign-Related Institutions)
  URL: https://data.bis.org/topics/GLI and https://www.federalreserve.gov/releases/h8/current/default.htm
  FREQUENCY: Quarterly for BIS GLI (approx. 1-quarter lag); Weekly for Fed H.8 (released every Friday)
  VARIABLES: BIS GLI: Total US dollar credit to non-bank borrowers outside the US, disaggregated into Bank Loans and International Debt Securities; Fed H.8: "Foreign-Related Institutions in the U.S." line items: "Net due to related foreign offices" (onshore conduit funding), "Deposits", and "Borrowings".
  CAVEAT: GLI captures on-balance-sheet loans and bonds to non-banks but omits off-balance-sheet FX swap/forward commitments, while Fed H.8 measures onshore US branch positions rather than the offshore stock.

Q7: BIS Locational Banking Statistics by Nationality (USD Funding Gap Estimates)
  PUBLISHER/TABLE: Bank for International Settlements (BIS) / Table A4 ("Cross-border positions by nationality of reporting bank and sector of counterparty") & BIS Quarterly Review / BIS Bulletin No. 27
  URL: https://data.bis.org/topics/LBS (Data structure: WS_LBS_D_PUB); Analytical releases: https://www.bis.org/publ/bisbull27.htm and https://www.bis.org/publ/qtrpdf/r_qt2212h.htm
  FREQUENCY: Underlying LBS nationality data is Quarterly; synthesized USD funding gap releases are periodic/ad-hoc analytical editions in the BIS Quarterly Review and BIS Bulletin series (no automated recurring daily/monthly single-indicator release exists).
  VARIABLES: On-balance-sheet US dollar assets minus US dollar liabilities by banking nationality (Eurozone, Japanese, UK, Swiss, Canadian banks); estimated net USD borrowing via FX swaps/forwards; cross-currency basis spreads.
  CAVEAT: The USD funding gap is not a standardized reported balance-sheet line item; it is an econometric residual derived from BIS LBS nationality data under the assumption of balanced total currency positions.
