# Parcel ZK2 — the double-count lens on the z_k v2 build (Gemini in ANTIGRAVITY, read-only)

ROUTING: Gemini in Antigravity — needs to open the CSVs and the build script as they are and
recompute; a paste would strip the data. READ-ONLY.

HANDOFF:
1. Open Antigravity on the FOLDER
   `~/Dropbox/31 - Claude Cowork/Work/2026.08 - Third Derivative Research`
2. Turn web search OFF — everything needed is on disk; web numbers would contaminate the check.
3. Paste everything below the line. Decline any offer to edit or create files.
4. If the answer truncates, use "continue". Copy the full return back to me verbatim.

---

You are an adversarial reviewer with read access to a research folder. One lens only: is
anything in the wholesale-funding measure W2 COUNTED TWICE, or counted as nonbank funding of
banks when it is not? Default to REFUTED unless the construction survives your own recomputation.

CONTEXT (read in this order, then the data):
  2026-08-31-N2b-zk-The-Wholesale-Share.md   — sections 1, 6, 7: how z_k is built, what v2 must test, the C-070 correction
  _research/n2b_v2/build_zk.py               — the v2 build script
  _research/n2b_v2/zk_v2.csv                 — its output: one row per quarter-end 2021-12..2026-06, inputs and every z_k variant
  _research/n2b_v2/formpf.csv                — OFR Form PF: hedge-fund reverse repo (cash LENDING) and repo (cash BORROWING), raw USD, quarterly
  _research/n2b_v2/h8.csv                    — H.8 total deposits and large time deposits, $bn, monthly
  _research/n2b_v2/m2.csv                    — M2, currency, retail MMF, $bn, monthly
  _research/n2b_v2/z1.csv                    — Z.1 household deposits and FHLB advances, quarterly
  data/history/mmf_*.csv                     — OFR N-MFP money-fund repo by collateral type, repo with the Fed, bank-related assets, $bn, monthly

THE CONSTRUCTION UNDER ATTACK:
  W1 = private MMF repo (Treasury + agency + other-collateral repo, LESS repo with the Fed) + large time deposits
       (money funds' bank-related assets are treated as sitting INSIDE large time deposits and are not added again)
  W2 = W1 + Form PF hedge-fund reverse repo (hedge funds lending cash)
  z_k = W / (W + denominator), denominators D1..D4 as in the CSV column names

SPECIFIC QUESTIONS — answer each with numbers from the files:
1. LENDER DOUBLE-COUNT: can any dollar in Form PF reverse repo also be inside private MMF repo?
   (Same borrower counted from two different lenders is fine; the same LENDER's dollar counted
   twice is not.) Consider money funds that are themselves fed by hedge-fund cash, and hedge-fund
   reverse repo whose counterparty is another hedge fund or a non-bank rather than a dealer/bank.
2. PERIMETER MIX: Form PF covers a GLOBAL population of qualifying hedge funds; every other input
   is US-perimeter. The v1 note records OFR Brief 26-03 putting US hedge-fund cash lending at
   1,007bn (H2-2025) against Form PF's 1,335bn (end-2025). Quantify what W2 and z_k(W2,D1) at
   2025-12 become if the hedge-fund leg is scaled to the US census figure. Does the direction of
   the series change? Does the level change materially?
3. NOT-A-BANK: is every leg of W2 funding of BANKS/DEALERS? Hedge-fund reverse repo cleared via
   FICC sponsored service still faces a dealer sponsor; uncleared bilateral faces a dealer. Say
   whether any material part faces a non-bank and should be excluded.
4. LARGE TIME DEPOSITS vs MMF BANK PAPER: confirm from the files whether treating money funds'
   bank-related assets as inside large time deposits is conservative (it should be a subtraction
   of at most the CD portion); state the size of the possible over-subtraction.
5. Recompute z_k(W2,D1) and z_k(W1,D1) at 2021-12, 2023-12, 2025-12 from the raw inputs yourself
   (not from zk_v2.csv) and report any cell that differs from the CSV by more than 0.05pp.

OUT OF SCOPE: the endpoint/window lens and the denominator lens (already run); web data; editing files.

RETURN EXACTLY THIS:
VERDICT: stands / falls / stands-with-amendment
Q1 LENDER DOUBLE-COUNT: finding, with the numbers you used
Q2 PERIMETER MIX: W2 and z_k(W2,D1) at 2025-12 as built, and rescaled to the US census; direction unchanged? yes/no
Q3 NOT-A-BANK: finding
Q4 LTD vs MMF BANK PAPER: finding, size of possible over-subtraction
Q5 RECOMPUTE: your three-date table for z_k(W1,D1) and z_k(W2,D1), and any cell differing >0.05pp
WHAT WOULD SETTLE IT: one measurable step
UNCERTAIN: anything you inferred rather than read

RULES
- Do not ask clarifying questions; state any assumption and proceed.
- Every number you report must come from a file in the folder; name the file and the row.
- Units: formpf.csv is raw US dollars (divide by 1e9 for $bn); h8.csv, m2.csv, data/history are $bn already.
- If a file is unreadable, say which and continue. Do not modify, create, or save any file.
