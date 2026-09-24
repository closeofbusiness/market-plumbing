# N2a: the offshore-dollar leg — v1 (build note)
**Date: 2026-08-30. Status: BUILT v1 COMPLETE, then ADVERSARIALLY REVIEWED same evening (N2aR, Grok — ~19/20 of its checks confirmed, 1 refuted by re-measurement). Strikes marked [C-069]; §7 carries the rebuild. All five ledgers measured: deposits (BIS),
holdings (TIC), self-reported positions (CPIS/PIP), offshore MMFs (CBI+CSSF), FX-swap layer (OTC derivatives). All sources free and in-house; agent-retrieved
figures spot-checked before entry (one C-068 correction registered against my own earlier
spot-check en route).**

## 0. What N2a asks

Where do offshore US-dollar cash pools sit, in which vehicles, and what do the official
ledgers see of them? The onshore side is instrumented (N-MFP, Form PF via OFR, FR 2004, Z.1);
this note builds the offshore counterpart from four ledgers: BIS LBS (bank balance sheets),
TIC (securities holdings), CBI (Irish MMFs), and the issuer/lender pages read in-browser.

## 1. The deposit leg (BIS LBS, USD, cross-border, 2026-Q1, $bn)

Banks' USD liabilities to non-banks, by counterparty residence (series keys and reproduce-URLs
in `data/series.tsv`; 2026-Q1 carries a BIS break flag but OBS_PRE_BREAK differs by only
$0.15bn on Cayman — negligible):

| counterparty | to non-banks | of which NBFI | 2019Q4 (non-banks) | 2022Q4 |
|---|---:|---:|---:|---:|
| Cayman Islands | **1,025.0** | 882.4 | 617.3 | 687.5 |
| United Kingdom | 1,012.7 | 890.6 | 523.5 | 865.0 |
| Luxembourg | 220.3 | 163.3 | 177.5 | 190.1 |
| Bermuda | 71.4 | 46.6 | 49.6 | 60.8 |
| **All countries** | **7,644.2** | 5,047.3 | 4,810.7 | 5,875.4 |

Cayman non-bank USD deposits +49% since end-2022. The mirror leg is bigger and faster:
**banks' USD claims ON Cayman NBFIs = $1,309.3bn, ×2.0 since 2022Q4 ($654.0bn)** — the
bank-credit financing of the Cayman fund complex has doubled in thirteen quarters.

## 2. The holdings ledger — what TIC sees, and what it measures

Live MFH (slt_table5 — NOT the frozen Publish/mfh.txt, see C-068): Cayman UST holdings
$440.9bn (Jun-2025) → $453.1bn (Jun-2026), against a $9,299.0bn all-country total. ~~+2.8%
y/y and barely moved~~ **[C-069: stacked windows — on the window MATCHED to §1's financing
series, TIC Cayman went 283.7 (Dec-2022, table3b) → 460.1 (Mar-2026) = +62%. And TIC-visible
is not holdings: Barth et al. (Fed FEDS Note, 15 Oct 2025) measure real Cayman hedge-fund UST
holdings at $1.85trn end-2024, +$1trn since 2022, with TIC undercounting by ~$1.4trn.]** The SHL 2025 benchmark agrees with MFH at the survey date (Cayman total UST $440.4bn =
$286.3 long-term + $154.1 short-term; Cayman is 4.9% of all foreign UST but 5.5% of foreign
TIPS). Cayman ALL US securities (SHL A1): $3,180bn — the pool is mostly equities and credit,
not Treasuries.

## 3. ~~The divergence~~ → the measured repo hole [rebuilt post-N2aR, C-069]

~~Two official ledgers disagree: financing doubled while holdings rose 2.8%~~ — that framing
died in review (stacked windows, §2). The original §3 text (a "documented candidate
mechanism" reading of SHL §4.2.4) is superseded by the rebuilt picture, which COHERES across
four ledgers:

- **Financing**: bank loans/deposits to Cayman NBFIs 451.6 → 1,136.0 ($bn, 2022-Q4→2026-Q1,
  LBS instrument G) — ×2.5, real financing, not valuation.
- **Real holdings**: Cayman hedge-fund UST $1.85trn end-2024, +$1trn since 2022 (Barth et
  al., Fed FEDS Note 15 Oct 2025, Form PF-based — the basis-trade growth).
- **TIC-visible holdings**: +62% matched-window, to $460.1bn — with the gap to real holdings
  MEASURED by the Fed at ~$1.4trn end-2024: repo'd-out securities drop out exactly as the SHL
  §4.2.4 under-reporting case describes (Treasury's own text; §4.2.4 equally allows
  over-reporting and double-counting cases — the Fed's measurement is what signs the net
  direction, not the methodology text alone).
- **CPIS-vs-SHL** (§6): the gap decomposes to DEBT ONLY — equity matches to 1.4% (2.13 vs
  2.16trn) while debt gaps by 1.36trn ≈ the same $1.4trn hole, from the reporter side.

What was a "divergence with a candidate mechanism" this morning is, by evening, a
three-way-triangulated measurement of one object: **~$1.4trn of repo-financed Cayman UST
invisible to custodial statistics**. The Fed had measured it in Oct-2025; the review surfaced
the paper (lesson in C-069: search for the official measurement before declaring a puzzle).

## 4. The offshore cash-pool map so far (what z_k gets built from)

- Cayman NBFI deposits at banks: $882.4bn (2026-Q1)
- UK non-bank USD deposits: $1,012.7bn
- Irish MMFs, USD-denominated assets: **€451.2bn** (30 Jun 2026; 44.9% of the €1,005.7bn
  Irish MMF total; CBI MMF.2)
- Luxembourg MMFs, USD-denominated NAV: **€334bn** (31 Dec 2025; 53% of €631bn total NAV;
  CSSF MMFR dashboard — the ONLY source with a currency split: ECB BSI has none, verified,
  and BCL's currency tables died in 2020-Q2. Caveats: NAV not gross assets; annual only;
  dates differ from the Irish figure). **Two-domicile offshore USD MMF pool: ~€785bn** —
  z_k CONSTRUCTION RULE (N2aR): never ADD this pool to the BIS deposit ledger — the MMFs'
  bank deposits (Irish USD loans 155.4bn EUR alone) ARE part of LBS liabilities to IE/LU
  NBFIs; the pool and the deposit ledger overlap by the deposit/repo legs. EUR sums across
  dates are also FX-contaminated (CSSF notes 2025 USD-depreciation effects)
- Stablecoin issuers (the fifth pool, D6): Tether alone $187.75bn total assets, ~$115bn
  direct T-bills (30 Jun 2026, derived from the attestation page percentages)
- Securities-lending cash side (ISLA, 31 Mar 2026): €3.9tn on-loan globally, 61% from
  identified real-money lenders (pensions 21% + govt/SWF 17% + CIVs 20% + insurance 3%)

## 5. The FX-swap layer, measured (read + updated to current vintage, 30 Aug eve)

The Borio–McCauley–McGuire mechanism (BIS QR Dec-2022, on disk): FX swaps/forwards/currency
swaps are economically repos with currency as collateral, but their USD payment obligations
are OFF balance sheet and absent from all debt statistics. Their mid-2022 estimate: non-banks
outside the US owed $26trn this way — double their on-balance-sheet dollar debt ($13trn) —
and non-US banks $39trn.

**Replicated and updated from the BIS OTC derivatives statistics (WS_OTC_DERIV2), method
validated at the paper's own anchors** (my computation reproduces their $85trn total USD leg
and $26trn non-bank figure at 2022-S1 exactly; series keys in `data/series.tsv`):

| | 2016-S1 | 2022-S1 | 2025-S2 (latest) |
|---|---:|---:|---:|
| Total USD-leg outstanding (forwards + FX swaps + currency swaps) | 63.9 | 85.5 | **113.5** |
| vs other financial institutions (two-sided notional) | 29.4 | 43.0 | 60.2 |
| **Non-bank USD obligations (paper method: (OFI+NFC)/2)** | 18.3 | 26.0 | **35.9** |

So the FX-swap layer DWARFS every ledger in §1–§4: $35.9trn of non-bank off-balance-sheet dollar debt against $7.6trn of measured offshore non-bank USD deposits and $5.0trn of bank credit to NBFIs. The on-balance-sheet comparator, updated from GLI (2026-Q1, keys in series.tsv): USD credit to non-banks outside the US = $14.74trn ($6.68trn bank loans + $8.06trn debt securities; the GLI 2022Q4 value 12.8trn matches the paper's ~13trn — a third cross-validation). **Off-BS/on-BS ratio: 2.0x at mid-2022 (the paper's headline), 2.52x at MATCHED end-2025 windows (35.9 / GLI 2025-Q4 14.25 — my first pass mixed windows and got 2.4x; N2aR amendment)** — the missing ledger is growing faster than the visible one. Folded from review: the /2 halving is the paper's identifying assumption that banks run dollar-balanced FX books (Aldasoro et al. 2020, paper fn.4) — gross notionals cannot confirm it held in 2025 — and the OCC settle-step is now CLOSED AS UNTESTABLE (31 Aug): the OCC's Quarterly Report publishes US banks' FX notional gross only ($75.3trn at 1Q2026, up from $41.9trn at 2Q2022, all insured US banks), with zero net or directional FX disclosure — while publishing exactly that bought-vs-sold split for CREDIT derivatives, so the omission is a reporting-schedule choice, not a data limit. **The /2 halving is therefore a maintained assumption no public source can verify**, and the $35.9trn inherits that status; and the review's one factual error was here — it claimed NFC=7.72trn making (OFI+NFC)/2=34.0; re-measurement gives NFC=11.57trn with sectors summing to the total exactly, so 35.9 stands on both formulas. It grew +38% since mid-2022 — faster than the deposit pool (+30%). Caveats
carried: the /2 halving is the paper's assumption, not a measurement; "other financial
institutions" includes non-reporting banks; mostly short-maturity, so this is rollover-hungry
debt (the 2020 stress channel — Bulletin 27's swap-lines episode).

## 6. What remains before N2b closes

1. ~~FX-swap layer read~~ — DONE above.
2. ~~Luxembourg USD MMFs~~ — DONE: €334bn USD NAV (above). ECB/BCL routes confirmed dead
   ends; CSSF Art.-37 dashboard is the standing source (annual, ~Dec; watch for the 2026
   edition in spring 2027).
3. ~~CPIS cross-check~~ — DONE (30 Aug eve). The dataset survives as **PIP** ("Portfolio
   Investment Positions by Counterpart Economy, formerly CPIS") on api.imf.org, which curl CAN
   reach (the data.imf.org portal blocks; the api host does not — route recorded in series.tsv
   keys). Cayman-as-reporter, counterpart US, end-2024: **total $4.51trn** ($2.38trn debt of
   which $2.17trn long-term, $2.13trn equity). Against SHL's custodian-based attribution of
   $3.18trn (Jun-2025): a ≥$1.3trn gap — which the N2aR review sharpened decisively: it is a
   **DEBT-ONLY gap** (CPIS equity 2.13 vs SHL equity 2.16trn — matched within 1.4%; CPIS debt
   2.38 vs SHL debt 1.02trn = 1.36trn), the size of the Fed's measured $1.4trn Treasury-repo
   undercount. Not general mis-attribution; the repo hole seen from the reporter side. CIMA
   coverage caveat still carried for pre-2023 levels (and its incompleteness biases CPIS DOWN,
   so it cannot manufacture the gap).

   **SETTLED 31 Aug on a MATCHED date.** CIMA's own CPIS submission for 30 Jun 2025
   (377PI6_2025S1.xlsx, Table 1 row 246; figures re-read from the raw XML by me) against SHL
   at the same date, $bn:

   | instrument | CIMA (reporter) | SHL (US custodial) | gap |
   |---|---:|---:|---:|
   | Equity | 2,129.8 | 2,160.1 | **−30.2** (SHL larger; matched to 1.4%) |
   | Debt, long-term | 2,166.6 | 861.8 | +1,304.8 |
   | Debt, short-term | 216.9 | 158.5 | +58.4 |
   | **Debt, total** | **2,383.5** | **1,020.2** | **+1,363.3** |
   | Total US securities | 4,513.3 | 3,180.3 | +1,333.0 |

   **The timing objection is dead** — same date, same instruments, and the gap is entirely in
   debt while equity matches (and is marginally larger on the US side). $1,363.3bn ≈ the Fed's
   independently measured ~$1.4trn TIC Treasury undercount. Two further checks: CIMA's own
   Dec-2024 US total (4,509.8) reproduces the IMF PIP figure exactly, validating that route;
   and the file's internal cross-check rows sum to zero, with nothing withheld as confidential.
   **Limitation found:** Cayman files the CPIS issuer-sector template but leaves every sector
   column blank (Tables 5/5.1/5.2 and 6 — verified across both vintages), so US TREASURY debt
   cannot be isolated from other US debt on the reporter side. The identification that this
   gap is Treasuries rests on Barth et al., not on CPIS.
4. Then **N2b**: z_k weights over the pool map in §4.

## 7. Review outcome (N2aR, Grok chat window, returned and adjudicated 30 Aug eve)

Verdicts as adjudicated after re-measurement (`_research/N2aR_verification_2026-08-30.md`;
raw return preserved verbatim): Claim 1 (the divergence) FELL — C-069, stacked windows,
rebuilt in §3 as the triangulated repo hole; Claims 2, 3, 5 stand with amendments (folded
above); Claim 4's central arithmetic attack was REFUTED by re-measurement (its NFC figure was
a mis-pull — the judging lane's first material factual error in five reviews; the receipt
procedure caught it inside the sceptic's own return, the system working in both directions),
while its window-matching and identifying-assumption amendments were folded.

Settle-steps closed 31 Aug (both in-house): CIMA June-2025 CPIS (matched-date wedge, §6) and the
OCC report (/2 untestable, §5). New standing sources from the review: Barth et al. (Fed FEDS Note 15 Oct 2025) — now THE
anchor for the Cayman basis-trade holdings ledger (preserved in
`_research/primary_sources/offshore_dollar/`); TIC table3b (monthly by-country UST history);
CIMA's own CPIS June-2025 file (open settle-step for §6); OCC derivatives report (open
settle-step for the /2 assumption); BIS LBS instrument-G keys (in series.tsv).
