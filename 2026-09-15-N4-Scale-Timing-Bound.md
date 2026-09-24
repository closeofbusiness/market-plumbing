# N4 — scale, timing and an upper bound: nonbank money and collateral vs the 2024 compression (15 September 2026)

> **[C-085]** The ceilings in this document are not a funded share of purchases. 2024 private-repo growth is the ON RRP handoff, not new cash in the money-fund complex. The six-bank permitted step (+19.3%) is H1 2026, not the 2024 compression year.

**Status: RESULT.** Ranked item 3. Supervisor arithmetic on series already built and
adversarially reviewed: `z_k` (`2026-08-31-N2b-zk-The-Wholesale-Share.md` §8), the offshore
leg (`2026-08-30-N2a-Offshore-Dollar-Leg.md`), the Singh numerator
(`2026-08-31-N3v4-Singh-Reconciliation.md`), dealer re-use (`2026-08-30-D10-Reuse-On-The-Measured-Chain.md`),
Treasury absorption (`2026-09-12-N2c-Closure-Refresh-2026Q2.md`). Path from
`_research/n2b_v2/zk_v2.csv`. Computed tables in `data/n4/`.

The frame is `_research/2026-09-14-N4-Frame.md`. **No percentage of purchases "ran through"
nonbank money or collateral.** That number would be manufactured: the purchases were ETF-wrapper
purchases (ETF1, C-083) and the household mix inside the plug is still unsized (LIT1, C-084).
N4 answers the three questions the frame left standing. It does not convert a collateral stock
into a price move (C-077, C-080).

Window **2024:Q1–2026:Q2**, matching the rest of the attribution. The thing to explain is the
**2024** premium compression (P2c: −0.86pp in 2024 alone; P/E path 24.35 → 28.60 → 28.48 → 25.22;
P5i: 2024 accrued as drift). Wrapper issuance over the full window is **+$3,243.1bn**; household
purchases of that instrument **+$3,069.4bn**. Operating companies retired.

## N4a — did it expand?

**Wholesale non-M2 funding of banks/dealers: yes, then it plateaued.** `z_k` on the private
measure (W1 = private money-fund repo + H.8 large time deposits, over W1+M2 — `z_W1_D1_pct`) went 9.75% (2022-12) →
15.94% (2023-12) → 17.63% (2024-12) → 19.24% (2026-03) → 19.42% (2026-06). The wider perimeter
W2 (adds Form PF hedge-fund reverse repo) is the same shape, higher and shallower: 13.37% →
19.33% → 20.98% → 23.07% (2026-03, last quarter with the hedge-fund leg). Full path in
`data/n4/wholesale_path.csv`. This is C-070's rebuilt finding, not two endpoints. The v1 LTD vintage of the same share (S-N2b) is 9.09% (2021-12) → 19.45% (2026-06); same shape, ~0.03pp higher at the last print. Both perimeters named (C-067).

Dollar stocks, same file:

| | W1 $bn | W2 $bn | ON RRP (MMF repo with Fed) $bn | private MMF repo $bn |
|---|---:|---:|---:|---:|
| 2022-12 | 2,300.5 | 3,286.5 | 2,339.6 | 637.1 |
| 2023-12 | 3,940.8 | 4,980.8 | 968.7 | 1,697.2 |
| 2024-12 | 4,598.3 | 5,703.3 | 382.4 | 2,237.8 |
| 2026-03 | 5,402.7 | 6,801.7 | 6.4 | 2,925.6 |
| 2026-06 | 5,582.0 | — | 6.8 | 3,067.8 |

Most of the rise is the ON RRP handoff: money-fund cash leaving the Fed for private dealers.
From 2023-12 to 2024-12, private MMF repo grew **+$540.6bn** while MMF repo with the Fed fell
**−$586.3bn**. Net of the drain, private repo **fell $45.7bn**. The 2024 "expansion" of the
measured wholesale-repo leg is a **counterparty switch**, not new cash in the money-fund
complex. (The same cash did not leave MMFs — N2bR already had this; the quarterly path now
dates it to the compression year.)

**Collateral re-use intensity: no.** Mechanism-signed velocity remains **≈1.3–1.5** against
Singh's ≈2.0 (C-061 range; the point estimate "1.5 and falling" is dead). Six-bank permitted-stock
utilization was **83.2%** at Jun-2026 — nearly saturated on the measured hop (D10R). The
growth in the pledged pool is more *source* collateral, not faster reuse (N3). The US-five
permitted stock is 2.23× its 2017 filing level ($3,351bn → $7,460bn) — that is an eight-year
stock comparison, not a 2024 flow.

**Collateral stock, inside the window: the documented step-change is H1 2026.** Six-bank
permitted **+19.3%** / repledged **+21.5%** Dec-2025 → Jun-2026 (D10R). We do not have a
five-name permitted total at Dec-2023 on disk, so this pass does not invent a 2024 collateral
flow. What is dated is the jump we did measure, and it is **2026**.

**Offshore dollar claims: larger, and a different object.** Cayman NBFI USD bank credit
doubled 2022:Q4–2026:Q1 (N2a, C-069 matched windows). FX-swap non-bank USD obligations
$26.0trn (2022-S1) → $35.9trn (2025-S2). Those are stocks of dollar *claims*, not measured
funding of US equity purchases. They sit in the scale picture as capacity elsewhere in the
system; they are not added to W.

## N4c — did the timing match 2024?

**Wholesale share: the steep climb is 2023; 2024 is the tail of the RRP drain; the plateau is
2025–26.** W2 rose **+$1,694.3bn in 2023** and **+$722.5bn in 2024**. Premium compression is
front-loaded into 2024 (P2c). So 2024 is not a blank on the wholesale series — `z_k` was still
rising — but the *large* move in the series is the year before the compression, and the 2024
increment is the handoff shown above.

**Dealer collateral stock: the wrong year.** The +19% H1-2026 step coincides with the
*giveback* of the multiple (P/E 28.48 → 25.22), not with 2024's rise (24.35 → 28.60). A stock
that jumps while the premium is reversing is not the explanation for the compression.

**Fed SOMA: the wrong sign in 2024.** Net Treasury flow **−$515.3bn in 2024**, then
−$82.8bn (2025), then **+$156.2bn / +$97.8bn** in 2026:Q1–Q2 (N2c). Direct central-bank
buying of duration was a drain in the compression year and a source only after it. A1 already
found the deposit–equity association weak; this is the same sign-pattern on the Fed's own book.

**P5i:** 2024's multiple expansion accrued as drift, not on earnings dates or FOMC dates. A
slow RRP handoff through the year is *compatible* with drift. Compatibility is not
identification.

## N4b — was the expansion large enough? Upper bound only

Against household purchases of the wrapper instrument, **$3,069.4bn** over 2024:Q1–2026:Q2
(issuance **$3,243.1bn**; both are the ETF-wrapper identity, not operating-company equity).

| | ΔW raw $bn | handoff-adjusted $bn | vs $3,069bn purchases |
|---|---:|---:|---:|
| 2024 calendar (the compression year) | W2 **+722.5** | **+136.2** (private repo net of RRP −45.7, + LTD 116.9, + HF 65.0) | 0.24 raw / **0.04** adjusted |
| Full window to 2026:Q1 (last HF print) | W2 **+1,820.9** | **+858.6** | 0.59 raw / 0.28 adjusted |

Handoff-adjusted = private MMF repo growth minus the ON RRP drain, plus the change in large
time deposits, plus the change in hedge-fund reverse repo. It is the part of ΔW that is not
the same money-fund dollar moving from the Fed to a dealer. **Stock ≠ flow:** these are
changes in wholesale *stocks*, used here only as a ceiling on new capacity.

**The 2024 bound is the one that bites.** Even the raw 2024 ΔW2 ($722.5bn) is about half of
2024 household purchases of the instrument ($1,404.9bn, N2c calendar year). Net of the RRP
handoff it is **~$136bn — an order of magnitude too small.** Under the frame's own rule, that
closes the 2024 question for *new* wholesale capacity. It does not close the possibility that
*existing* wholesale stocks were used (the A1 amendment applies equally here: a $5trn W2 stock
at end-2023 can rearrange without growing). Existing-stock reuse is a different claim, and
the measured reuse *rate* did not rise.

The full-window raw ΔW2 ($1.8trn vs $3.1trn) is the same order of magnitude, so it does **not**
fail the "order of magnitude too small" test. Strip the handoff and it is a quarter of
purchases — large enough to remain in the picture as a ceiling, not large enough to have been
the sole source. **Do not read either ratio as a fraction of purchases funded.** They are
capacity ceilings. No multiplier is applied.

## What this does to the argument

- **Channel (b), nonbank / wholesale money.** It expanded as a *share* of bank funding, mostly
  by taking back the ON RRP. In the year the premium compressed, new private-repo capacity net
  of that handoff was approximately zero. The channel is real. It is not the proximate source
  of 2024's compression on the expansion test the frame asked for.
- **Channel (c), collateral.** Intensity did not rise. The dated stock jump is 2026, during the
  reversal. Permissive condition, not proximate source — the inherited collateral-leg finding,
  now dated against the compression.
- **The interlock.** The same institutions sit on both legs, and both legs moved: wholesale
  share up, source collateral up, velocity not up. That is the Pozsar–Singh mechanism running.
  It does not, on free data, identify those moves as the 2024 premium event. Tracing a dollar
  to a named buyer remains closed (LIT1). Converting a stock to a price remains closed
  (C-077, C-080).
- **Limit of the programme, stated so it can close.** We cannot say what fraction of wrapper
  purchases, or of the compression, "ran through" nonbank money or collateral re-use. We can
  say the *expansion* of measured wholesale capacity in 2024 was the RRP handoff, that the
  handoff-adjusted ceiling is an order of magnitude below 2024 purchases, and that the
  collateral-stock step we did measure is in the wrong year. That is the answer N4 can give.
  The 1 October revolver-drawdown parcel stays on the calendar; it is a fragility question,
  not this one.

## Sources

- `z_k` path: `_research/n2b_v2/zk_v2.csv` (N2b v2, three lenses; W = W/(W+M2) despite the
  v2 table's "W/M2" header — W2 $6,801.7bn at 23.07% implies M2 ≈ $22.7trn).
- RRP / private repo / LTD: same file, OFR N-MFP and H.8 legs.
- Collateral: D10 / D10R / N3v4, filings already in `data/series.tsv`.
- Compression path: P2c (surviving window claim) and P5i.
- Wrapper identity: ETF1. Household purchases: HR / `data/etf1/`.
- Treasury flows: N2c, Z.1 2026:Q2 vintage.
