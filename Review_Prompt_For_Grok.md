# External review prompt — for Grok

*Written 21 August 2026. Self-contained: Grok cannot read the project files, so every claim it
is asked to attack is carried inline with its number and source. Paste the block below.*

**Why this shape.** The most useful thing an outside model can do here is what our own
adversarial verifiers have been doing — attack. This project has killed 27 of its own claims,
and the failure modes are known and repeatable: reading a normalised statistic as a quantity
(twice), category errors, and mistaking a citation cascade for independent confirmation (four
times). The prompt names those failure modes so Grok hunts for them specifically, and lists
what is *already known to be broken* so it does not spend effort rediscovering it.

---

```
You are reviewing a research programme before it becomes a published essay. I want you
adversarial, not helpful. Assume I am wrong somewhere and find it.

Today is 21 August 2026. You have live search; use it. Every number below is checkable and
I want you to check the ones that carry weight rather than reasoning about them.

## THE QUESTION THE ESSAY ANSWERS

A capex and valuation boom is being funded while the US aggregate household saving rate
FALLS (2.7% in June 2026, lowest since 2005). My starting intuition was that this is the
creation of an illusion of wealth: that if anyone actually tried to realise it, valuations
would collapse and trigger calls on collateral whose value had itself diminished.

So: is the wealth real, and what happens if it is tested?

## WHAT I NOW BELIEVE, WITH THE NUMBERS

Attack any of these. They are load-bearing.

1. THERE IS NO AGGREGATE EXTERNAL FUNDING GAP. US non-financial corporates fund 100% of
   capex from internal funds and lend the surplus onward (~$326bn/yr). The Z.1 financing gap
   has been negative in four consecutive quarters. 72% of internal funds is consumption of
   fixed capital — depreciation. ~90% of the RISE in gross capex was absorbed by faster
   depreciation, so net fixed investment rose only 5.8% while gross rose 13.1%.
   CAVEAT I HAVE ALREADY ATTACHED: the identity holds because the internal-funds surplus
   sits at firms that are NOT doing the capex. Alphabet's FCF turned negative in Q2 2026;
   six hyperscalers issued ~$182bn IG YTD against ~$690–800bn of 2026 capex.

2. THE WEALTH IS OVERWHELMINGLY REVALUATION, NOT SAVING. Of the $39.16trn rise in US
   household net worth 2023–25, $31.40trn (80.2%) was net holding gains, 83.7% equity-linked.
   Since 1995, personal saving plus corporate retained earnings total $36.6trn against a
   $152.9trn rise in net worth — 24%.

3. THE ILLUSION IS NEITHER MONETARY NOR A DISCOUNT-RATE ARTEFACT. Both explanations fail.
   The collateral-circuit account fails on three observables (reuse intensity flat; the ECB's
   transaction-level test for a "liquidity windfall" returns null; identified credit against
   securities has SHRUNK relative to the prices it should explain). The discount-rate account
   fails on SIGN: the 10-year TIPS yield rose from −1.04% to +2.35%, +339bp, Dec-2021 to
   Aug-2026, and equity valuation did NOT revert on any of three denominators — equity to
   profits +7.9%, equity to gross value added flat to three decimals, Tobin's q +6.9% with
   2025Q3 the highest of 304 quarters since 1945.
   What I think does the work instead: factor-share reallocation to shareholders
   (Greenwald–Lettau–Ludvigson put 40.2% of the 1989–2017 real equity rise there against
   14.3% for interest rates), float retirement (−$1.90trn net equity issuance 2022Q1–2025Q4),
   and inelastic-market amplification of any flow regardless of its funding source.

4. THE OFFSHORE DOLLAR IS THE ONE LARGE CHANNEL OUTSIDE THE AGGREGATES — BUT SMALLER THAN
   THE HEADLINE. Banks outside the US grew USD claims +$2,040bn against liabilities
   +$1,650bn; the $391bn residual has no dollar liability behind it. Japan is 47% of that
   residual alone, Japan plus China 89%. In Q1 2026 Japanese offices' entire dollar credit
   growth was funded with NO net new dollar liability. The BoJ's own Financial System Report
   (April 2026, footnote 16) states the yen-swap funding mechanism outright.
   Three numbers on three perimeters, never one: $2,040bn gross claim expansion, $1,650bn
   liability-matched, $754bn owed to an identified non-bank.

5. THE MONEY-LIKE STACK IS GROWING THROUGH REPO — AND THAT MAY BE LEVERAGE, NOT MONEY.
   Fed FSR "runnable money-like liabilities" $27,033bn, +12.0% y/y against a 5.4% long-run
   average. Repo is the largest contributor (+19.1%, 32.6% of the increase). BUT hedge-fund
   repo borrowing rose +$882bn over the same window — the same ORDER as the entire increase
   in the FSR repo line — with relative-value strategy borrowing +70.7% and leveraged-fund
   net short Treasury futures roughly 2.2–2.8× the pre-March-2020 peak. A hedge fund is the
   cash BORROWER; it issues no money-like claim to any saver.

6. THE MECHANISM I DID NOT EXPECT: CREATED CREDITWORTHINESS, NOT CREATED MONEY. Nvidia
   signed a 15-year, $19.6bn lease (renewals toward $50bn/30yr) on Hut 8's 1GW Texas site.
   Hut 8 then issued ~$4.3bn of bonds at 6.129%, rated investment grade by Moody's BECAUSE
   OF THE LEASE, priced ~100bp over Nvidia's own 30-year paper. Meta's filing language on
   residual value guarantees: payments are "not probable, and therefore no liability has
   been recorded to date." An unpledged IG balance sheet is doing collateral work that
   appears in no balance sheet, no credit aggregate and no flow-of-funds line — invisible by
   construction, because a contingent guarantee is not a financial instrument until drawn.

7. SINGH DOES NOT CARRY THE COLLATERAL-VELOCITY STORY. Across his five core IMF collateral
   papers the strings "asset price", "equity price" and "stock price" appear ZERO times; his
   formal model puts collateral efficiency in the LM curve, acting on OUTPUT. And in the ZIRP
   window his measured velocity FELL from 3.0 (2007) to 1.8 (2016) while the S&P rose 52%.

8. THE SAFE-ASSET SHARE IS NOT A NULL. The widely cited "33.2% of US assets, constant since
   1952" uses a standard error (0.003) that is a regression INTERCEPT's, not the dispersion
   of the share — which is ±2.2–2.4pp, a nine-point band. The share is at 27.5% now, the
   minimum of 297 quarters, outside the 95% band of the original paper's own regression. The
   safe-asset numerator grew 177.8× while the denominator grew 239.1×. Revaluation as a share
   of the denominator's change went 18.1% (original window) → 49.2% (2011–26) → 66.6%
   (2022Q4–2025Q4). My claim: the constancy held while the denominator behaved like a
   quantity and failed once it began behaving like a valuation.

## WHAT I ALREADY KNOW IS BROKEN — DO NOT SPEND EFFORT HERE

- One quantity has THREE conflicting values from three of my own passes: margin debt as a
  share of non-financial corporate equity market value at 2026Q1, variously 0.90%, 1.756%
  and 1.84%, with opposite conclusions. Unresolved; I know.
- Two reconstructions disagree by ~21pp on what fraction of the safe-asset denominator is
  market-valued, and on the SIGN of its long-run change.
- How much of repo growth is the Treasury basis trade rather than money demand is open.

## WHAT I WANT FROM YOU

1. THE HOSTILE ECONOMIST'S FIRST OBJECTION. You are a sceptical macro or financial economist
   reading this cold. What is the first thing you say? Not the most sophisticated objection —
   the first one, the one that makes you stop reading if it isn't answered.

2. CHECK THE NUMBERS THAT CARRY WEIGHT. Pick the five that most of the argument rests on and
   verify them against live sources. Tell me which are wrong, stale, measured from a
   convenient base, or defined differently from how I've used them. I would rather find out
   from you than from a reader. Pay attention to: base effects, mismatched observation
   windows, gross versus net, stock versus flow, and figures measured from a trough.

3. HUNT MY KNOWN FAILURE MODES SPECIFICALLY. This project has repeatedly made four errors:
   (a) reading a normalised statistic — a ratio, or a NET regression coefficient — as if it
       measured a quantity;
   (b) category errors, e.g. mixing a composition share, a growth-contribution share and an
       elasticity and treating them as the same object;
   (c) treating N sources that all cite one underlying paper as N independent confirmations;
   (d) letting a refuted figure survive in a downstream document.
   Find fresh instances above. I expect there are some.

4. IS THERE A LIVE MECHANISM I HAVE MISSED? I have covered: bank credit, offshore dollars,
   repo and collateral reuse, money-like liabilities, private credit, securitisation, the
   insurance and annuity layer, FX swaps, stablecoins, margin and prime brokerage, and
   contingent guarantees. What is the channel that is materially moving in 2025–26 that is
   not on that list?

5. THE HONEST VERDICT ON THE THESIS. Given all of the above, is "the wealth is not real and
   will not survive being tested" supportable? My current position is that the fragility is
   NOT a leverage-against-listed-equities story — identified credit against securities is
   near the bottom of its own range — and that if it exists it is in the dark corners:
   securities-based lending, NAV loans against model-marked private assets, portfolio margin,
   internalised synthetic prime, and now contingent guarantees. Is that right, or am I
   retreating to the unmeasurable because the measurable didn't cooperate? Say so if it's the
   latter. That is the criticism I am most worried about and least able to see.

6. WHAT WOULD YOU MEASURE NEXT, and is it obtainable from public data?

## HOW TO ANSWER

Lead with your strongest objection. Be specific: name the claim, name the defect, give the
correct version where you can. Where you check a number, say what you checked it against and
what you got. Where you can't verify something, say "can't verify" rather than reasoning
around it — a confident wrong number is worse to me than an admitted gap.

Do not summarise what I wrote back to me. Do not open by telling me the work is thorough.
Agreement is worth nothing here; I have had four rounds of adversarial review and the useful
output every time was the disagreement.
```
