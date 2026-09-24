# B0 — The Bridge: stating the question we have to cross (13 Sep 2026)

**Status: FRAME. Supervisor, not delegated.** Opens **Tier B**, a standing sub-project by Martin's
instruction of 13 Sep: *"let's also dig into the 'bridge we cannot cross'... We should be able to cross
it, we just have not figure out how. Make this a core sub-project."*

## The question, stated so it can be answered

> **How much does a dollar of net buying, by investors who are not responding to price, move the
> aggregate value of US equities?**

Call it M. Everything in this programme that wants to say "money drove prices" needs M, and we do not
have it. We carried M = 5, and retracted it on 12 Sep when the specification behind it turned out to be
rejected by its own authors' J-test (C-077). The published envelope is roughly **1.5 to 9.4** — a six-fold
range, which is not a measurement.

## What we can already say without resolving M — a bound

Over **2024:Q1–2026:Q2** (Z.1, all corporate equity held): total change **+$46,919.4bn**, of which net
flow **+$3,243.1bn** and revaluation **+$43,676.3bn**.

If flows explained the entire repricing, the implied multiplier would be **13.47**. **No published
estimate reaches that.** So on the published envelope:

| M | revaluation explained | share of revaluation | share of the total rise |
|---|---|---|---|
| 1.5 | $4,864.6bn | 11.1% | 10.4% |
| 2 | $6,486.2bn | 14.9% | 13.8% |
| 5 | $16,215.5bn | 37.1% | 34.6% |
| 9 | $29,187.9bn | 66.8% | 62.2% |
| 9.4 | $30,485.1bn | 69.8% | 65.0% |

**The finding: flows cannot be the whole story on any published number.** Their contribution is bounded
to 11%–70% of the repricing. That is still a six-fold range and therefore still not an answer — but it
does kill the strong form of the passive-bid thesis as applied to this window, and it means earnings and
genuine repricing must carry at least 30%.

**[C-080] AMENDED 13 Sep, SAME DAY, after the BR2 challenge — the bound is much weaker than stated above.**
Grok attacked the denominator and I verified its arithmetic against our own file: **gross net-purchases by
the buying sectors over the same period were $6,886.8bn** (Grok said 6,887; households 44.6% of it, Grok
said 45%). On that denominator the implied multiplier is **43,676.3 / 6,886.8 = 6.34 — comfortably inside
the published envelope**, not above it. The table above therefore does not travel:

| denominator | what it is | implied M if flows explain all | envelope 1.5–9.4 explains |
|---|---|---|---|
| net issuance $3,243.1bn | equilibrium net new supply | 13.47 | 11% – 70% of revaluation |
| gross buying $6,886.8bn | what buying sectors actually bought | **6.34** | 24% – **148%** |

**On the second denominator the envelope covers the entire repricing, so "flows cannot be the whole story"
is not established.** Grok's deeper point is right and neither number is the answer: **both are equilibrium
quantities, not the demand shift M is defined on.** Gabaix–Koijen define M on a portfolio shift into
equities; Z.1's net flow is what the market cleared at. If issuance is itself inelastic, revaluation ÷
issuance is an artefact.

**What survives: an issuance-only ceiling.** If the relevant price-insensitive flow is bounded by net new
supply, then 9.4 × $3,243.1bn covers 70% of the repricing. That is a conditional ceiling, and the condition
must be stated every time. **A second mismatch also stands: Z.1's $123.7trn stock is public plus closely-held,
while every published M is estimated on listed markets** — and S1 has now shown 89% of record 2026:Q1 issuance
was private, which makes that mismatch large rather than technical.

**THE ORIGINAL LOAD-BEARING ASSUMPTION, now confirmed wrong as stated.** The bound treats Z.1's aggregate net flow as the
external money entering equities. At the whole-market level that flow *is* net issuance, because every
secondary purchase has a seller and the two net out. But an investor who sells bonds to buy equities from
another investor has moved external money into the asset class while contributing **zero** to Z.1's
aggregate net flow. If the relevant flow is sector-level rather than market-level, the denominator changes
and so does the bound. **This is exactly the aggregation problem below, and it must be settled before the
bound is quoted.**

## Why the estimates disagree — the hypothesis Tier B tests

They are probably not estimating the same object. They differ in horizon (days to years), in flow
definition (fund flows, index demand, sector purchases, issuance), in segment (single stocks versus the
market), and in identification (GIV, reconstitution discontinuities, fire sales, demand systems). **If the
dispersion is explicable by those differences, then a specific subset applies to our question and the
bridge is crossable.** That is the bet Tier B makes.

## The aggregation problem — the crux

A stock-level elasticity does **not** rescale to the market, and the reason is substitution. Buy stock A
and the money usually comes from stock B, so the market does not move: within-equity rotation has a
large stock-level impact and roughly zero aggregate impact. An aggregate multiplier requires flows that
do **not** substitute within equities — money entering or leaving the asset class.

This is the same error we caught in the retirement data on 13 Sep, one level up: a rollover from a 401(k)
to an IRA looks like a flow and is a transfer. **The general rule: before any flow is multiplied, show
that it crosses the boundary of the asset class.** ETF creations fail this test unless the money came from
outside equities; so do sector reallocations with an equity counterparty.

## Candidate flows that plausibly DO cross the boundary

- Net new equity supply (issuance less buybacks less retirements) — measured, and being decomposed now.
- Foreign net purchases of US equities — external by construction.
- Retirement contributions net of withdrawals — external, and **negative since 2013** (RET1, 13 Sep).
- Large forced reallocations by mandate: GPIF, NBIM, the Dutch Wtp transition.

## Tier B items

| # | item | who |
|---|---|---|
| B1 | Census of published aggregate estimates: number, identification, horizon, flow definition, segment | OUTSIDE — Gemini Deep Research, then every URL resolved |
| B2 | Adversarial case that the bridge IS crossable, and the specific design | OUTSIDE — Grok in Cursor |
| B3 | Our own stock-level elasticity (Russell reconstitution) | DONE 15 Sep — first stage fails (C-086); does not rescale |
| B4 | The aggregation problem: which flows cross the asset-class boundary, and how to measure them | SUPERVISOR |
| B5 | Natural experiments on free data: GPIF, NBIM, Dutch Wtp — large, forced, pre-announced | SONNET; connects to E1 |
| B6 | The demand-system route (13F holdings, Koijen–Yogo) | deferred — trigger is B1+B2 showing it is the only route |

## The design BR2 named, and the mechanism paper that reframes B4

**BR2 verdict (Grok in Cursor, 13 Sep): only-for-a-subset.** An aggregate M is identifiable for *mechanical
mixed-asset mandate flows*, not for the household plug and not as a scalar on Z.1 lines.

**The design: a sovereign-mandate rebalancing IV.** Instrument = published rebalancing rules forcing
bond-financed equity buys or sells — NBIM's 70% ±2pp band plus petroleum inflows at strategic weights, and
GPIF's 25% foreign-equity target with a ±6pp band — times lagged AUM times US weight. First stage runs to
Treasury TIC SLT foreign net purchases and Norges Bank 13F holdings changes, both free. Reduced form runs to
the listed-market return and our trailing residual, **not** to a C-078-style level gap. Threat: the band is a
nonlinear function of lagged global returns, so lagged US, global-ex-US and VIX must be controlled; the kill
switch is a first-stage F below 10. Falsification set: the instrument must move TIC and 13F; earnings
revisions must not jump the same month; bond-only rebalancing months must move Treasuries and not the equity
residual. **All nine of its URLs that I could reach resolve; the DNB page 403s to scripts.**

**B4 is reframed, and this is the important part.** Our rule "only boundary-crossing flows matter" is **too
strong**. Verified at source 13 Sep — **Jiang, Vayanos & Zheng, "Passive Investing and the Rise of
Mega-Firms"** (Michigan State / LSE / UC-Irvine, 19 Jun 2025,
`personal.lse.ac.uk/vayanos/Papers/PIRMF_RFSf.pdf`), abstract, quoted: flows into passive funds
*"disproportionately raise the stock prices of the economy's largest firms"*, and **"the aggregate market can
rise even when flows are entirely due to investors switching from active to passive funds."** Their mechanism:
passive flows raise the idiosyncratic risk of large in-demand firms, which discourages arbitrageurs from
correcting the price effect.

**So a flow that does NOT cross the asset-class boundary can still move the aggregate market.** That is
exactly Michael Green's mechanism, it is published, and it means our rotation finding (ETFs +$2,460.9bn
against mutual funds −$2,009.0bn, 2024Q1–2026Q2) does not refute the passive-bid thesis — it is what the
thesis predicts. Their cross-sectional prediction is also directly testable against our own P2b work: the
largest S&P 500 firms should show the biggest price and idiosyncratic-volatility rise after index inflows.

**DONE for Tier B** = a defensible number or range for M *that states which flows it applies to*, with an
identification strategy we can describe in one paragraph and defend against an adversarial reader.
