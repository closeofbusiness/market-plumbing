# Parcel N2aR — adversarial review of the offshore-dollar leg (for Grok, chat window)

Copy everything below the line into grok.com. Do NOT run in Cursor — judging parcel, no repo
access needed or wanted.

---

You are an adversarial reviewer of empirical work on offshore dollar intermediation. Your job
is to break the claims below, not improve them. Everything needed is in this message or public.

MATERIAL — five claims from a research note dated 30 Aug 2026, with their evidence:

CLAIM 1 (the divergence). BIS LBS (stats.bis.org API, series key
Q.S.C.A.USD.A.5J.A.5A.F.KY.N): banks' cross-border USD claims on Cayman NON-BANK FINANCIAL
institutions were 654.0bn dollars at 2022-Q4 and 1,309.3bn at 2026-Q1 — x2.0 in 13 quarters.
Meanwhile TIC (live MFH table, slt_table5.txt on ticdata.treasury.gov — NOT the frozen
Publish/mfh.txt): Cayman holdings of US Treasuries went 440.9bn (Jun-2025) to 453.1bn
(Jun-2026), +2.8%. Inference OFFERED (not asserted): bank financing of the Cayman fund
complex doubled while its visible Treasury holdings stood still.

CLAIM 2 (repo invisibility as candidate mechanism). Treasury's own SHL 2025 methodology
(shl2025r.pdf §4.2.4) says custodians "may not always be able to distinguish" repo transfers
from sales, and in the under-reporting case the custodian "would not report the security as
foreign held." The note holds this as a DOCUMENTED CANDIDATE mechanism for Claim 1's
divergence, explicitly not asserted as the reconciliation.

CLAIM 3 (CPIS attribution wedge). IMF PIP (formerly CPIS; api.imf.org, key
CYM.A.P_TOTINV_P_USD.S1.S1.USA.A): Cayman self-reports 4.51trn dollars of US securities at
end-2024 (debt 2.38, equity 2.13). The US custodian-based SHL survey attributes 3.18trn to
Cayman at end-June 2025. The note claims a >=1.3trn attribution wedge "with the self-reported
side larger," while carrying the caveat that CIMA's fund-census expansion makes pre-2023 CPIS
non-comparable (2022: 1.97trn -> 2023: 3.86trn).

CLAIM 4 (FX-swap layer update). Replicating Borio–McCauley–McGuire (BIS QR Dec-2022,
r_qt2212h) on current BIS OTC derivatives data (WS_OTC_DERIV2, instruments D = outright
forwards + FX swaps and I = currency swaps, FX risk, USD leg, semiannual): total USD-leg
113.5trn at 2025-S2; non-bank obligations by the paper's method ((other-financial +
non-financial)/2) = 35.9trn, vs 26.0trn at 2022-S1 — and the replication reproduces the
paper's own 85trn and 26trn at 2022-S1 exactly. On-balance-sheet comparator (BIS GLI,
Q.USD.3P.N.A.I.B.USD): 14.7trn at 2026-Q1. Claimed ratio: off-BS/on-BS 2.0x (mid-2022) ->
2.4x (now).

CLAIM 5 (offshore USD MMF pool). Irish MMFs 451.2bn EUR of USD-denominated assets (CBI
MMF.2, 30 Jun 2026, gross assets) + Luxembourg 334bn EUR USD-denominated NAV (CSSF MMF
Reporting Dashboard 2025, 31 Dec 2025, 53% of 631bn NAV) = a "~785bn EUR two-domicile
offshore USD MMF pool," with the NAV-vs-gross-assets and date mismatches flagged.

TASK
1. Verify every figure you can reach (BIS, IMF api.imf.org, TIC, CSSF PDF are public). Per
   figure: CONFIRMED / CONTRADICTED (with correct value) / UNREACHABLE.
2. For each claim, argue the strongest case it is WRONG. Specific angles to attack:
   - Claim 1: is the BIS claims series really "financing of funds" — what else is in it
     (intragroup? securities held as claims? valuation effects from the 2026-Q1 break)?
   - Claim 3: could the entire wedge be timing (end-Dec vs end-Jun), valuation, or CIMA
     coverage rather than attribution? What would separate those?
   - Claim 4: does the /2 halving still hold in 2025 data (has the net USD direction of
     non-bank positions changed)? Is including ALL currency-swap notional right when the
     paper's own number was anchored to a USD leg share?
   - Claim 5: double-counting risk — do Irish/Lux USD MMF assets overlap the BIS LBS
     deposit figures (MMF deposits AT banks are bank liabilities to non-banks)?
3. Name any PUBLIC data source that would improve the construct that the note does not use.

RETURN EXACTLY THIS
For each claim 1–5, four labelled lines:
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
