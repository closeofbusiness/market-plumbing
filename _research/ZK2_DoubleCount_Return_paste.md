# ZK2 return — Gemini in Antigravity (read-only, search off), received 2026-08-31 as chat paste
# Preserved verbatim. Adjudication: ZK2_verification_2026-08-31.md

VERDICT: stands-with-amendment

Q1 LENDER DOUBLE-COUNT: No double-count found. The two components measure disjoint reporting institutions entering direct repo lending agreements. Form PF Qualifying Hedge Funds (_research/n2b_v2/formpf.csv row 106, $1,335.0bn at 2025-12-31) report under the Investment Advisers Act; registered MMFs (_research/n2b_v2/zk_v2.csv row 18, private repo $2,921.8bn at 2025-12) report on Form N-MFP under the Investment Company Act. If a hedge fund holds cash in a money market fund, that holding is reported on Form PF as cash equivalents or fund shares (Question 33), not as a reverse repurchase agreement (FPF-ASSETCLASS_REPO_REVERSEREPO_SUM). Conversely, money market funds do not borrow cash in repo (OFR Brief 26-03 Figure 1, cited in 2026-08-30-D10-Reuse-On-The-Measured-Chain.md:129-132: MMF borrowing is $0.0bn; terminal cash lenders), so hedge funds cannot lend to MMFs via reverse repo. Finally, any bilateral reverse repo between hedge funds or with non-banks is outside Form N-MFP by construction and cannot appear in private MMF repo.

Q2 PERIMETER MIX: At 2025-12, with M2 D1 = $22,355.3bn and W1 = $5,369.7bn (H.8 LTD $2,447.9bn + private MMF repo $2,921.8bn):
- As built with Form PF ($1,335.0bn): W2 = $6,704.7bn, z_k(W2,D1) = 23.07% (23.0719%). (With v1 LTD $2,428.8bn: W2 = $6,685.6bn, z_k = 23.02%).
- Rescaled to OFR Brief 26-03 US census ($1,007.0bn): W2 = $6,376.7bn, z_k(W2,D1) = 22.19% (22.1937%). (With v1 LTD: W2 = $6,357.6bn, z_k = 22.14%).
- Level change: -0.88pp (a ~3.8% shift in ratio).
- Direction unchanged? yes. The series rises monotonically from 2021-12 (13.10% unscaled, 12.16% scaled) through 2023-12 (19.33% unscaled, 18.53% scaled) to 2025-12 (22.19% scaled), rising by +9.09pp to +10.03pp.

Q3 NOT-A-BANK: Every leg of W2 constitutes funding of banks and broker-dealers:
1. Large time deposits ($2,447.9bn at 2025-12) are direct liabilities of US commercial banks.
2. Private MMF repo ($2,921.8bn at 2025-12) excludes the Fed leg ($72.6bn) and is restricted by Rule 2a-7 to regulated broker-dealers, banks, and FICC-cleared trades.
3. Hedge-fund reverse repo ($1,335.0bn at 2025-12): in FICC sponsored clearing, the hedge fund faces FICC backed by an unconditional guarantee from its bank/dealer Sponsoring Member; in uncleared bilateral/NCCBR, hedge funds face primary and non-primary broker-dealers. Hedge funds are ineligible for the Fed ON RRP, and direct peer-to-peer repo between hedge funds or with non-financial non-banks without dealer intermediation is non-existent. No material part faces a non-bank.

Q4 LTD vs MMF BANK PAPER: The construction in build_zk.py:108-109 sets W1 = private repo + H.8 LTD, adding zero MMF bank-related assets under the assumption that all MMF bank paper sits inside large time deposits. This is strictly conservative: MMF bank-related assets comprise bank CDs (which sit inside H.8 large time deposits) and bank commercial paper/unsecured notes (which do not sit inside deposits). Assuming 100% of MMF bank paper is CDs prevents double-counting CDs, but omits (over-subtracts) the bank CP portion. The maximum possible over-subtraction is the full amount of mmf_bank_related_assets_bn:
- 2021-12: $301.6bn
- 2023-12: $483.5bn
- 2025-12: $451.8bn
W is therefore understated (and z_k a lower bound) by the bank CP share of those amounts.

Q5 RECOMPUTE: Recomputed from raw files (mmf_treasury_repo_bn.csv, mmf_agency_repo_bn.csv, mmf_repo_other_collateral_bn.csv, mmf_repo_with_fed_bn.csv, _research/n2b_v2/h8.csv, _research/n2b_v2/formpf.csv, data/vintages/alfred/alf_M2SL_2026-08-15.csv):

  2021-12: private repo 756.0, LTD 1,407.5, Form PF 1,078.0, W1 2,163.5, W2 3,241.5, M2 21,502.0, z_k(W1,D1) 9.1420%, z_k(W2,D1) 13.1004%
  2023-12: private repo 1,697.2, LTD 2,243.6, Form PF 1,040.0, W1 3,940.8, W2 4,980.8, M2 20,779.9, z_k(W1,D1) 15.9413%, z_k(W2,D1) 19.3349%
  2025-12: private repo 2,921.8, LTD 2,447.9, Form PF 1,335.0, W1 5,369.7, W2 6,704.7, M2 22,355.3, z_k(W1,D1) 19.3677%, z_k(W2,D1) 23.0719%

(Note: with v1 LTD from data/history/large_time_deposits_bn.csv — $1,394.3bn, $2,225.1bn, $2,428.8bn — z_k(W1,D1) recomputes to 9.0913%, 15.8783%, and 19.3121%, exactly matching z_W1v1ltd_D1_pct in zk_v2.csv).

Cells differing from zk_v2.csv by >0.05pp: NONE (maximum absolute discrepancy across all cells is 0.000043pp, attributable solely to float display rounding).

WHAT WOULD SETTLE IT: Publication by the OFR or Federal Reserve of an ongoing quarterly time series from the NCCBR collection isolating US-domiciled qualifying hedge funds' cash lending facing US primary dealers and bank entities, replacing the global Form PF proxy with a perimeter-matched domestic census series.

UNCERTAIN:
1. The exact breakdown of MMF bank-related assets between bank CDs (inside large time deposits) and bank commercial paper (outside large time deposits) is not disaggregated in mmf_bank_related_assets_bn.csv.
2. Whether the ratio of US-domiciled hedge fund lending to global qualifying hedge fund lending (~75.4%, 1,007 / 1,335) remained constant at earlier dates (2021-2024) is inferred from the H2-2025 OFR Brief 26-03 benchmark.
