# Parcel N2bR — adversarial review of the z_k wholesale-share build (for Grok, chat window)

Copy everything below the line into grok.com. Do NOT run in Cursor — judging parcel, no repo
access needed or wanted.

---

You are an adversarial reviewer of empirical work on US bank and dealer funding. Your job is to
break the claims below, not improve them. Everything needed is in this message or public.

BACKGROUND (one paragraph). Pozsar & Singh (IMF WP/11/289) split a bank's funding share into
z_h — funding received from households as M2 — and z_k — funding received from OTHER NONBANKS
that is not M2. Their thesis is that the banking system can lever up with M2 stable via the
asset-management complex's portfolio choices. The note under review estimates z_k for the US.

MATERIAL — five claims with their evidence:

CLAIM 1 (construction). z_k = W / (W + M2), where M2 is the H.6 seasonally-adjusted money stock
and W is non-M2 nonbank wholesale funding measured LENDER-SIDE (to avoid counting a money
fund's repo lending and a dealer's repo borrowing twice). W has three components: private money
market fund repo (N-MFP3 via OFR: Treasury + agency + other-collateral repo, LESS repo with the
Federal Reserve), money funds' bank-related assets (bank CDs, bank CP, bank deposits), and
large time deposits at all commercial banks. Because money-fund CDs are themselves large time
deposits, two bounds are reported: W_low subtracts the bank-related line once, W_high adds gross.

CLAIM 2 (the levels). $bn. 2023-12: private MMF repo 1,697.2; MMF bank paper 483.5; large time
deposits 2,225.1; W_low 3,922.3; M2 20,779.9; z_k_low 15.88%. 2026-07: 2,918.4; 467.4; 2,537.6;
W_low 5,456.0; M2 23,218.0; z_k_low 19.03%. Intermediate points 2024-12 (17.57%) and 2025-12
(19.31%). Over the window M2 +11.7%, W_low +39.1%, private MMF repo +72.0%, z_k +3.15pp.

CLAIM 3 (the finding). The Fed's overnight reverse repo facility drained 961.9bn over the same
window (968.7 -> 6.8) while private MMF repo rose 1,221.2bn, so the drain accounts for 78.8% of
the private-repo growth. Counting the Fed as a wholesale borrower, z_k is 19.05% at BOTH dates
(-0.01pp). The note states plainly that the Fed term cancels algebraically in that second
measure, which reduces to (total MMF repo + large time deposits)/(that + M2) — and argues the
flatness is therefore a genuine near-equality of growth rates: that aggregate grew +11.69%
while M2 grew +11.73%. Conclusion drawn: the nexus did not expand as a share of money; the Fed
exited as the money funds' counterparty and dealers re-entered.

CLAIM 4 (cross-validation). The note's N-MFP3-derived private MMF repo at 2025-12 is 2,921.8bn;
OFR Brief 26-03's entity-typed repo census puts money-fund lending at 2,927.5bn for H2-2025 —
a 0.19% difference between independent sources.

CLAIM 5 (stated perimeter limits). W excludes: hedge funds' cash lending of 1,007.0bn and
non-primary broker-dealers' 1,086.8bn (both OFR 26-03, H2-2025); securities-lending cash
collateral reinvestment; offshore USD deposits from nonbanks (7.6trn, but a global-banks
perimeter); ABCP outside money-fund holdings; corporate and pension wholesale deposits beyond
the large-time-deposit line. The note says adding the two OFR segments would put W near 7.4trn
and z_k near 25% at 2025-12, but declines to report that as the number because those are
H2-2025 averages with no comparable series at the other dates.

TASK
1. Verify every figure you can reach (H.6, N-MFP/OFR money market fund statistics, large time
   deposits, OFR Brief 26-03, ON RRP are all public). Per figure: CONFIRMED / CONTRADICTED
   (with the correct value) / UNREACHABLE.
2. For each claim, argue the strongest case it is WRONG. Specific angles worth your effort:
   - CLAIM 3 is the one to attack hardest. Is the +11.69% vs +11.73% near-equality robust, or
     is it an artefact of the two endpoints chosen? Recompute on other start dates (2021, 2022,
     mid-2024) and say whether the flatness survives. If it does not, the conclusion falls.
   - Is attributing 78.8% of private-repo growth to the RRP drain a real attribution or just
     two numbers of similar size? What would distinguish them?
   - CLAIM 1: is M2 the right z_h base at all? M2 contains currency and retail money-fund
     shares, neither of which is bank funding. Does stripping them change the DIRECTION of the
     result, or only its level?
   - CLAIM 5: would including the hedge-fund and non-primary-dealer lending legs, if a time
     series exists for them, break the flatness? This is the note's own stated weak point.
   - Any double-count still present in W, or any non-M2 nonbank funding of US banks/dealers
     large enough to matter that the note omits entirely.
3. Name any PUBLIC source with a genuine TIME SERIES for the excluded legs.

RETURN EXACTLY THIS
For each claim 1-5, four labelled lines:
VERDICT: (stands / falls / stands-with-amendment)
STRONGEST ATTACK: one or two sentences.
EVIDENCE: link + date for every factual assertion you introduce.
WHAT WOULD SETTLE IT: one measurable step.
Then one final line: NEW SOURCES: list or "none".

RULES
- Do not ask clarifying questions; state any assumption and answer anyway.
- Mark anything inferred rather than verified as UNCERTAIN, and say what would settle it.
- If you cannot do part of this, say which part and why, and do the rest.
- Cite a link and date for every factual claim you introduce. Paywalled figures do not count.
- Market-size figures from training data are presumed stale; pull live or mark stale.
