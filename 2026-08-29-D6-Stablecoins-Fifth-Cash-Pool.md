# D6 — Stablecoins: the fifth cash pool is the issuer, and engine 5 has stalled

*29 August 2026, v1. Built from the Gemini D6 parcel return (pasted; preserved at
`_research/D6_Stablecoin_Scouting_Return_gemini_pasted.md`) after full verification by three agents — every
load-bearing regulatory and data claim re-read at the primary source (statute text, both TBAC decks, FSOC/OFR
annual reports, issuer pages, the live DeFiLlama API). Register: **C-062** (the return's defects). Primary
PDFs archived `_research/primary_sources/stablecoins/`. Serves A12 (taxonomy) and closes **engine 5 of the
N2c funding closure**. Result promoted as **S-D6**.*

---

## 1. The taxonomy answer: the ISSUER is the fifth cash pool — by statute

Pozsar's discriminator was the "do not lose" mandate: cash pools rank proximity-to-government first, yield
second. The GENIUS Act (**Public Law 119-27, 18 July 2025** — verified at govinfo) writes that mandate into
law for stablecoin issuers: reserves restricted to currency, Fed balances, insured deposits, **Treasuries of
≤93 days remaining maturity**, overnight (reverse) repo backed by them, and government MMF shares; and — the
sharpest clause — *"no permitted payment stablecoin issuer … shall pay the holder … any form of interest or
yield."* Zero yield, government-proximate assets only, monthly published reserve composition with CEO/CFO
certification. **A stablecoin issuer is an institutional cash pool by legal construction** — the purest "do
not lose" balance sheet in the taxonomy. The *holder* is a money-user, not a cash pool: par redemption with
the issuer is institutional-only (Tether: USD 100k minimum, fee the greater of USD 1,000 or 0.1% — verified
on the live fees page); retail bears secondary-market depeg risk (USDC to ~0.87 in March 2023). So D6
resolves cleanly: **add a fifth category — stablecoin issuer reserves — sitting between institutional MMFs
and the govt-only funds; do not classify the coins themselves as a cash pool.** The Act's interest ban also
creates the predicted bifurcation (return §5, consistent with the statute): yield goes offshore into
synthetic-dollar vehicles (basis-trade-backed), which belong with the *collateral* leg, not here.

## 2. Engine 5, sized and closed — and it stalled in 2026

| | Dec-23 | Dec-24 | Dec-25 | 29 Aug 26 |
|---|---:|---:|---:|---:|
| Total USD stablecoins outstanding ($bn, DeFiLlama, pulled directly) | 130.3 | 206.5 | 307.5 | **309.4** |
| Annual flow | | **+76** | **+101** | **+2 YTD** |

Reserve composition is bill/repo-dominated (statute-bound going forward; historically: **TBAC, Oct 2024 —
">$120bn … directly invested in Treasuries"; OFR AR 2024 — USDC+Tether held ~$92bn of bills + $29bn of
overnight repo at June 2024** — both read from the PDFs, archived). So engine 5 supplied roughly
**$70–100bn/yr of new bill demand in 2024–25 — real, about 4–5% of net issuance — and has added ~nothing in
2026.** That completes the N2c 2026 picture: *every private absorption engine plateaued in the same year* —
MMFs net sellers, sponsored repo flat, stablecoins flat — which is exactly when the Fed returned as the
marginal buyer. Forward scenario on record (not ours): TBAC's April 2025 deck charts **~$1.0tn of issuer
bill holdings by 2028E, ~$900bn incremental** — a single official scenario, not a range.

**No official series exists.** Verified: the GENIUS reporting regime is still in notice-and-comment
(Treasury's latest proposed rule 18 Aug 2026, docket TREAS-DO-2026-0496); no federal register or aggregate;
OFR's 2025 annual report contains **zero** stablecoin mentions. The only continuous aggregate is on-chain
indexing (DeFiLlama; now in `bin/pull_series.py --only llama`). The monthly-report regime, once rules
finalise, becomes the official series — calendar-worthy when a final rule lands.

## 3. Scorecard on the return (C-062)

Spine real, five substantive errors, and the worst literature section of the nine parcels. **Verified:**
PL 119-27 and date; reserve restrictions and interest ban (quoted); rulemaking status; TBAC documents exist
and say ">$120bn"; issuer portals real; Tether redemption terms exact; Cantor custody (openable source);
Circle Reserve Fund real — **USD 60.7bn at 31 Jul 2026** (factsheet), double the return's stale figure.
**Wrong:** (1) headline market size "USD 168bn / USDT 69%" is a **pre-2024 training-data snapshot** — live:
$311bn / 59% — despite search being on, i.e. partial-search answers happen even when the toggle is set;
(2) reserve reporting "weekly and quarterly" — the statute says **monthly** (zero hits for weekly/quarterly
in the text; FSOC 2025 corroborates); (3) TBAC "120–135bn" and "500–900bn" — **fabricated precision**; the
documents say ">$120bn" and "~$900bn", full stop; (4) NYDFS register "lists Paxos and Gemini" — Gemini yes,
**Paxos absent** as fetched (FSOC 2024: of the top five coins only Circle is NYDFS-licensed); (5) Paxos
custodian "State Street" — the confirmable partner is **Standard Chartered** (their own Dec 2024 release).
**T2 official literature: 4/5 constructed** — real Fed/BIS/ECB stablecoin authors welded into trios that
never co-published, under invented titles. L1: 2/6 verified, 3 partly (fabricated titles/co-authors on real
papers), 1 constructed. The real literature, recovered by the audit: **Ahmed & Aldasoro, "Stablecoins and
Safe Asset Prices," BIS WP 1270 (2025, rev. Jun 2026)**; Carapella–Lubis–Vardoulakis, "Stablecoins in 2025,"
FEDS Notes (Apr 2026); Ma–Zeng–Zhang, "Stablecoin Runs and the Centralization of Arbitrage," NBER 33882
(2025); Anadu et al., "Runs on Stablecoins," Liberty Street (2023); Barthelemy–Gardin–Nguyen, JIMF
(~Feb 2026); Gorton & Zhang, "Taming Wildcat Stablecoins," U. Chicago L. Rev. (2023); Lyons–Viswanath-Natraj,
JIMF (2023); d'Avernas–Maurin–Vandeweyer, "Can Stablecoins Be Stable?", Mgmt Sci (2026).

## 4. Open

Issuer-level bill holdings as a *series* (Tether's figures are JS-rendered quarterly attestations — a
browser read, not a fetch); the Paxos NYDFS puzzle; whether the plateau is crypto-cycle or GENIUS-transition;
the yield-bearing synthetic-dollar complex (Ethena etc.) as a *collateral-leg* object — flagged, not folded.
