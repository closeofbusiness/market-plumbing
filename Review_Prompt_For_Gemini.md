# External review parcel — for Gemini

*Written 22 August 2026. Supersedes `Review_Prompt_For_Grok.md`, which stays on file verbatim
as sent and must not be reused — its opening question has since been withdrawn (C-030).*

**What changed, and why this parcel is shaped differently.** One external review has already
run. Its factual corrections are incorporated below, so Gemini is not asked to rediscover
them. Its **judgement calls are deliberately withheld** — under this project's own
anti-pattern #2, pasting one reviewer's conclusions into the next reviewer's prompt and then
calling the second independent is a leak. Gemini is therefore asked to reach its own verdict
on the one call I accepted fastest, without seeing the argument that produced it.

**The centre of gravity has moved.** The first review verified what it could and left five
load-bearing numbers it could not verify from published tables. Those five are now the binding
constraint on what can be published, so they are the primary task here rather than an
afterthought.

---

```
You are the second external reviewer of a research programme heading for publication. I want
you adversarial. Assume I am wrong somewhere and find it.

Today is 22 August 2026. Use search and go to primary sources. Where I give a number, I want
it checked against the issuing table, not reasoned about.

## STATUS: ONE REVIEW HAS ALREADY RUN

Its factual corrections are already folded into what follows, so do not spend effort
rediscovering them. Its judgement calls are deliberately NOT reproduced, because I want yours
to be independent rather than a vote on someone else's. Where I say "withdrawn" or "dead"
below, that is the current state of my belief — you are explicitly invited to tell me the
withdrawal was wrong.

## WHAT THIS PROJECT IS

A study of how the 2023–26 US capex and valuation boom is financed, and of whether any part
of it rests on claims that conventional aggregates cannot see. It has killed 30 of its own
claims in the course of getting here; the register is deliberately larger than the findings.

## THE FRAMING I HAVE WITHDRAWN — AND YOUR FIRST TASK IS TO JUDGE THE WITHDRAWAL

I opened this work with: *a boom is being funded while the US household saving rate falls, so
where is the money coming from?* I have since withdrawn that question as badly posed, on the
grounds that falling household saving is one of the terms that mechanically produces the
corporate profits doing the funding — it enters the Kalecki profit identity with a minus sign
— and that gross private saving rose from $4,815bn (2019) to $6,384bn (2025) regardless, so
there was never an aggregate shortfall to explain.

I also withdrew the thesis that framing supported: *"the wealth is not real and will not
survive being tested."*

**Judge both withdrawals independently.**
(a) Is the identity objection correct as I have stated it? Check the Kalecki decomposition and
    the saving figures yourself.
(b) Did I over-correct? A question can be badly posed and still have a real phenomenon behind
    it. Is there a defensible residual — a version of "this valuation cannot be realised in
    aggregate, and that matters" — that survives the accounting objection? Or is the honest
    position that the intuition was simply wrong?
(c) I accepted this kill within minutes of receiving it. Accepting a kill fast is its own
    failure mode. Tell me if I capitulated to a confident reviewer rather than to an argument.

## YOUR PRIMARY TASK: FIVE NUMBERS NOBODY HAS VERIFIED

These are load-bearing and the first review could not confirm any of them from published
tables. Each is retrievable in principle. For each: confirm, correct, or state precisely which
table would carry it and why it is not obtainable.

1. **BIS locational banking statistics.** Banks outside the US grew USD claims +$2,040bn
   against USD liabilities +$1,650bn over the four quarters to 2026Q1, leaving a $391bn
   residual with no dollar liability behind it. Japan is claimed as 47% of that residual,
   Japan plus China 89%. Series family: LBS, flow measure, break- and FX-adjusted, USD as a
   foreign currency. The claim that most needs checking is the JAPAN SHARE, because the
   nationality and currency-type dimensions may not intersect in the published cube — if they
   do not, the 47% cannot be derived from public data at all and I need to know that.

2. **The safe-asset share at 27.5%** of total US assets at 2026Q1, described as the minimum of
   297 quarters. This is a Gorton–Lewellen–Metrick style ratio rebuilt on current Z.1 data:
   a safe-asset numerator over "all sectors, total liabilities and equity" (Z.1 series
   FL894194005). Rebuild it or tell me the reconstruction is underdetermined.

3. **Form PF hedge-fund figures.** Repo borrowing +$882bn over Q4-2024 → Q4-2025, and
   relative-value strategy borrowing +70.7% over the same window. Source claimed as the OFR
   Hedge Fund Monitor. Verify both, and tell me whether Form PF repo and the Fed Financial
   Stability Report repo line are even the same measurement basis — I have used them side by
   side and I am not confident they are comparable.

4. **83.7% of the 2023–25 household net-worth gain being "equity-linked."** The parent figure —
   $31.40trn of net holding gains out of a $39.16trn rise, on the 11 June 2026 Z.1 vintage — is
   confirmed. The 83.7% split within it is not. Which Z.1 table decomposes holding gains by
   instrument, and does it support that split?

5. **$36.6trn of cumulative personal saving plus corporate retained earnings since 1995**,
   set against a $152.9trn rise in net worth. Verify the sum and, more importantly, tell me
   whether adding a saving FLOW cumulated over 30 years to compare against a net-worth STOCK
   change is a legitimate operation or a category error.

## WHAT I CURRENTLY BELIEVE — ATTACK ANY OF IT

- **No aggregate external funding gap.** US non-financial corporates fund 100% of capex from
  internal funds. The Z.1 financing gap has been negative four consecutive quarters. 72.1% of
  internal funds is consumption of fixed capital (2026Q1, SAAR). Between 2023Q4 and 2026Q1,
  gross fixed investment rose 13.1% while net fixed investment rose 5.8% — ~90% of the increase
  absorbed by depreciation. CAVEAT ALREADY ATTACHED: the surplus sits at firms that are not
  doing the capex; Alphabet's FCF turned negative in Q2 2026.
- **The wealth is overwhelmingly revaluation.** $31.40trn of the $39.16trn 2023–25 net-worth
  rise was net holding gains (80.2%), on the 11 June 2026 vintage.
- **Neither monetary nor a discount-rate artefact.** The collateral-circuit account fails on
  three observables. The discount-rate account fails on SIGN: 10-year TIPS went from −1.04% to
  +2.35% (+339bp) Dec-2021 to Aug-2026 while equity valuation did not revert — equity/profits
  +7.9%, equity/gross value added flat to three decimals, Tobin's q +6.9%, with 2025Q3 the
  highest of 304 quarters since 1945.
- **Money-like liabilities.** Fed FSR Table 4.1 puts runnable money-like liabilities at
  $27,033bn, +12.0% y/y against a 5.4% long-run average, with repo the largest contributor at
  +19.1%. I suspect a large share of that repo growth is Treasury basis-trade leverage rather
  than money demand. (See task 3 — I cannot currently size it.)
- **An unrecorded lease obligation, not created money — and not a guarantee either.** Updated
  22 Aug after summing the filings directly. ASC 842 leases **signed but not yet commenced**,
  six filers on one standard at/near 30 Jun 2026: Microsoft $329.1bn, Meta $278.99bn, Oracle
  $260bn, Amazon $137.2bn, Alphabet $85.2bn, NVIDIA $32.4bn — **$1,122.9bn**, against ~$417.4bn
  of prior-period equivalents. Disclosed by 6 of 6 filers and **XBRL-tagged by none**. The
  guarantee stack alongside it is far smaller: $86.2bn live, $228.3bn contracted, including
  Alphabet's $43.785bn of data-centre payment backstops which were **$0 at 31 Dec 2024**. At
  Hut 8's Beacon Point the notes are *expressly unguaranteed* and a bare lease covenant earns
  Baa2 on its own.
  THREE THINGS I GOT WRONG HERE AND HAVE SINCE KILLED, so do not repeat them back to me: the
  claim that such a guarantee "roughly halves" financing cost is false (best-controlled
  same-sponsor pair shows **6.3bp**, and the widest observed reduction anywhere is 38%);
  Nvidia is **not** named as the Hut 8 tenant in any filing (Hut 8 says only "rated AA- or
  higher"); and the "~100bp over Nvidia's own 30-year paper" comparison is not reproducible —
  Nvidia has issued no bond since 2020.
- **Singh does not carry the collateral-velocity story.** Across his five core IMF collateral
  papers, "asset price", "equity price" and "stock price" appear zero times; his model puts
  collateral efficiency in the LM curve, acting on output. His measured velocity FELL from 3.0
  (2007) to 1.8 (2016) while the S&P rose 52%.

## KNOWN BROKEN — DO NOT SPEND EFFORT HERE

- One quantity has three conflicting values from three of my own passes: margin debt as a share
  of non-financial corporate equity at 2026Q1, variously 0.90%, 1.756% and 1.84%, with opposite
  conclusions. Unresolved. I know.
- Two reconstructions disagree by ~21pp on what fraction of the safe-asset denominator is
  market-valued, and on the sign of its long-run change.
- The footnote-summing pass has now COMPLETED and its results are in the bullet above. Do not
  redo the collection. **Do** tell me two things about it: (a) whether summing ASC 842
  "not yet commenced" across six filers with vintages spanning eight months is a legitimate
  operation or whether I have built another category error; and (b) what a footnote-summing
  exercise systematically misses — my own suspicion is everything held by non-filers, since
  ~90% of the guarantee beneficiaries turned out not to be SEC registrants.

## WHAT I WANT FROM YOU

1. **The two withdrawal judgements above.** That is the most valuable thing you can give me.

2. **The five unverified numbers.** Confirmed, corrected, or shown to be underivable from
   public data. "Underivable, and here is why" is a complete answer and I would rather have it
   than a guess.

3. **HUNT MY SIGNATURE ERROR.** This project has made the same mistake four times: reading a
   NORMALISED statistic as if it measured a QUANTITY. A ratio read as a level. A *net*
   regression coefficient read as gross. A regression intercept's standard error read as the
   dispersion of the series. A *rate* read as a quantity. Find the fifth instance. I am
   confident it is in there.

4. **The channel I have missed.** I have covered bank credit, offshore dollars, repo and
   collateral reuse, money-like liabilities, private credit, securitisation, the insurance and
   annuity layer, FX swaps, stablecoins, margin and prime brokerage, and contingent guarantees.
   What is materially moving in 2025–26 that is not on that list?

5. **What should the essay be now?** If the original question was badly posed and the thesis it
   supported is dead, one legitimate outcome is that the piece becomes a negative result — *I
   went looking for hidden money creation and there is none; here is the accounting, and here
   is the one thing I found instead.* Is that the right piece, is the guarantee layer strong
   enough to carry a piece on its own, or is there a third framing I am not seeing?

## HOW TO ANSWER

Lead with your strongest objection. Name the claim, name the defect, give the correct version.
Where you check a number, say what you checked it against and what you got. Where you cannot
verify, say "cannot verify" — a confident wrong number is worse to me than an admitted gap.

Do not summarise my work back to me and do not open by telling me it is thorough. I have run
five rounds of adversarial review and the useful output every time was the disagreement.
```
