# W3 — how much of the earnings story is the 2017 tax act? (+ one attack) — for Grok in Cursor

**Author:** Claude (supervisor). **Routed to Grok by the principal, 20 Sep 2026.**
**Two tasks. Task 1 is the parcel; task 2 is short and is an attack on a claim I made today.**

> **Read C-095 first.** This parcel was nearly written against the wrong target. SYN1 named SBC,
> operating-vs-GAAP and R&D capitalisation as untested inflators of the earnings claim. **They cannot inflate
> it:** the headline rests on Shiller's **as-reported (GAAP)** series, which already expenses SBC (ASC 718)
> and already expenses R&D. What survives as live is **the 2017 tax act** and revenue-recognition timing.

---

## Task 1 — the tax decomposition

**The question.** "Earnings explain 70–80% of the S&P 500's price gain since 2015" rests on *after-tax*
reported profit. The 2017 act cut the federal statutory rate **35% → 21% from 2018**, which lifts after-tax
profit with **no change in pre-tax profit**. Nobody has asked how much of the earnings contribution is that.

**The identity** — this is an accounting decomposition, not a statistical test. **No MDE applies; do not
compute one.** Per share:

`Δlog EPS = Δlog(pre-tax profit) + Δlog(1 − effective tax rate) − Δlog(diluted shares)`

The third term is already measured (C-093: −0.1726, carry it, do not recompute). **The new term is the
middle one.**

**Method.**
1. **Universe and weights: reuse the EPS-split panel** (`data/eps_split/`, S&P 500 constituents, 2015 mcap
   weights). Same universe means the three terms compose; a different universe means they do not.
2. **Per firm, FY2015 and FY2025**, from SEC companyfacts (`data.sec.gov`, no key; the project User-Agent
   with the contact address goes to **sec.gov hosts only**):
   `us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest`
   (accept the documented variants) and `us-gaap:IncomeTaxExpenseBenefit`.
3. **THE TAG TRAP — this one will silently produce nonsense.** Several filers carry
   `...BeforeIncomeTaxesDomestic` and `...BeforeIncomeTaxesForeign` **alongside** the consolidated tag.
   Microsoft has all four. Taking the first match that resolves lands on a **component**, and dividing the
   *consolidated* tax expense by a *component* pre-tax gives an effective rate of **85.8%** and an after-tax
   multiplier of ×4.8 — obvious nonsense only because it is extreme. Select the consolidated tag explicitly,
   never fall through to Domestic or Foreign, and **where both components exist, check they sum to the
   consolidated total.** Report how many firms resolved on each tag.
4. **Aggregate before dividing.** Effective rate = **Σ tax ÷ Σ pre-tax**, not the mean of firm ratios. State
   that denominator explicitly wherever the rate appears.
5. **Report**: aggregate ETR in 2015 and 2025; `Δlog(1 − ETR)`; its share of `Δlog EPS` (1.0613); and the
   restatement — **what is 2025 EPS at the 2015 effective rate**, and what does that do to the 70–80%?

**A prior, so you can tell if your aggregate is wildly off** (supervisor, two firms, 20 Sep — a sanity
check, NOT a result): Apple's effective rate went **26.4% → 15.6%**, multiplying after-tax profit by
**×1.146**; Microsoft's **34.1% → 17.6%**, ×**1.250**. Both are heavily international and will sit at the
high end. An aggregate multiplier far outside roughly ×1.05–×1.25 deserves a second look before you report it.

**Threats to name in the result, each with a direction.**
- **Loss-makers.** Negative pre-tax income makes a firm-level rate meaningless. Aggregating first mostly
  handles it; say how many firms had negative pre-tax income in either year and what you did with them.
- **2017–18 is contaminated.** The act's transition tax produced one-off charges that spike ETRs in those
  years. That is why the endpoints are FY2015 and FY2025; do not use 2017 or 2018 as a base.
- **Foreign mix.** The aggregate ETR blends US and foreign rates; a shift in foreign earnings share moves it
  without any policy change. Flag it — you are not being asked to separate it.
- **Survivorship**, same as the EPS split: current constituents were the survivors. State the direction.
- **Coverage**: n of 500 with usable data in both years, and name any missing megas (the JVZ lesson).

**Do not say:** that the tax effect is "not real earnings" — it is real after-tax profit and it really
accrues to shareholders. The claim under test is narrower: **how much of the growth is a one-time change in
the tax rate rather than in the business.** And no causal statement about prices (C-077).

---

## Task 2 — attack a claim I made today (short)

`2026-09-20-W1-The-Leak-Objection.md` concludes that the contractual pension-and-insurance channel is
**$938.4bn**, and calls it a **ceiling**. The named weakness is this: **a pension selling equities may be
rebalancing into bonds, not paying benefits** — in which case the cash never leaves the asset circuit and
the ceiling is too high.

Z.1 carries those five sectors' flows in debt instruments over the same window (2024:Q1–2026:Q2). **Pair
them.** For each of the five, report net acquisition of debt securities against its equity sales, and say
what share of the $938.4bn is plausibly rebalancing rather than payout. If that share is large, **say so
plainly — it would take the number down, and the doc says so itself.**

Also say whether anything else in W1 is wrong. It was written in one pass today.

---

## Rules

- **Run every command in the FOREGROUND and block on it.** No `nohup`, no `&`, no detached worker. Long
  companyfacts pulls go in sequential slices, still in the foreground, paced against rate limits — Yahoo
  429s cost us a whole panel once. Report only output you actually observed.
- **State the denominator on every number**, including coverage and the ETR.
- **If your finding contradicts this brief, say so explicitly.** The brief has already been wrong once this
  week about which inflators apply.
- **Never route around a refusal. No summary files.** We never pay for data (E-005).
- Hand over when you stop, **note in SINGLE quotes** (a `$` figure in double quotes expands):
  `bin/check.sh --handover write grok w3-tax-decomposition done 'ETR 2015 x% -> 2025 y%; tax is z% of EPS growth'`
