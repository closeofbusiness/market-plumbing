# 6c RERUN — JVZ gate, done correctly this time (16 Sep 2026)

**Author:** Claude (supervisor). **For:** the agent picking up 6c. **Principal has routed this to Grok.**
**Status:** GATE ONLY. The deliverable is four numbers and a verdict. **Do not run the real regression.**

> **Read C-092 first.** The previous gate cleared this design using `2σ/√N` on 3,936 firm-quarters (MDE
> 0.451pp). The realised two-way-clustered SE was 0.811 — a true MDE of **1.622pp**, and an effective n of
> **304, not 3,936**. Stage B and the sharpen run are therefore **uninformative, not rejections**, and
> `2026-09-16-TierB-E005-Resolution-Limit.md` is bannered to that effect. Do not cite either run as evidence
> about JVZ, and do not repeat "NOT SUPPORTED".

---

## The two things that were wrong, both fixable

**1. The megas were missing.** Stage A's Yahoo pull hit rate limits and returned 186 of 587 firms; the sharpen
added 37 but the panel still omits part of the mega-firm left tail. **A test of mega-firm amplification that
omits the largest mega-firms is not a test of the hypothesis.** This is a pacing problem, not a data wall, and
E-005 does not bite: Yahoo is free, it just needs to be pulled slowly.

**2. The MDE was declared, not demonstrated.** `σ/√N` is the wrong formula when the treatment is a
period-level shock interacted with a near-time-invariant cross-sectional characteristic. Precision is governed
by the number of **shock periods** and by the **cross-sectional spread of the characteristic**, and the only
honest way to know it is to measure the clustered SE the design actually produces.

## Why this is worth one parcel rather than a write-off

The gate turns on a single measurable quantity: **the within-quarter SD of passive intensity once the megas
are in.** Mega SPY weights are 5–7% against a sharpen-sample SD of 0.818, so including them could widen that
spread sharply — and `SE(β̂) ∝ σ / √(N · Var(X))`.

| within-Q SD of pctVal (with megas) | implied SE | MDE = 2·SE | predicted ÷ MDE |
|---:|---:|---:|---:|
| 0.818 (sharpen, megas missing) | 0.544 | 1.088 | 0.49× **fail** |
| 1.0 | 0.414 | 0.827 | 0.64× fail |
| 1.3 | 0.318 | 0.636 | 0.83× fail |
| **1.6** | 0.258 | 0.517 | **1.02× marginal pass** |
| 2.0 | 0.207 | 0.414 | 1.28× pass |
| 2.5 | 0.165 | 0.331 | 1.60× pass |

**Below ~1.6 this design is dead; above ~1.6 it is live.** The supervisor's prediction on record is that it
fails, because 23–26 time clusters are the binding constraint and adding firms does not add quarters. That
prediction may be wrong — the spread effect above is the mechanism that would overturn it. **Measure it; do
not defer to the prediction.**

## Task

**Step 1 — close the coverage hole.** Rebuild the firm-quarter panel with the full S&P 500 payer universe,
**megas included** (MSFT, NVDA, META, GOOGL/GOOG, AAPL, AMZN and the rest of the top 40 by index weight).
Pace the Yahoo pulls — sleep between requests, retry on 429, resume from cache — until coverage is complete.
Report coverage as **n firms retrieved ÷ n attempted**, and name any firm still missing.

**Step 2 — measure the regressor spread.** Report the **within-quarter SD of passive intensity** (SPY `pctVal`
primary, IVV cross-check), with and without the megas, so the delta is visible. Also report N firm-quarters
and the number of time clusters.

**Step 3 — demonstrate the MDE on placebo treatment.** Keep the panel, LHS, firm FE, quarter FE and two-way
clustering exactly as Stage B/sharpen. **Replace the flow series with a randomly permuted version across
quarters** (preserving its marginal distribution), re-run, and record `SE(β̂)`. Repeat **200 times**. Report
the **median and the 10th/90th percentile** of the placebo SE for both LHS variables (quarterly excess return
vs `^GSPC`; annualised idio vol). With fewer than 30 time clusters, also report firm-only and quarter-only
clustered SEs as a bound, and say which is largest.

**Step 4 — the verdict.** MDE = 2 × median placebo SE. Compare against **+0.528pp** (JVZ Table 6.2, top-50 per
1 SD flow) and **+0.43pp** (Table 6.3 incremental idio). State `predicted ÷ MDE` for each channel and give
one word: **PASS** (ratio > 1 on either channel) or **FAIL**.

**Then stop and hand back.** The placebo tells you nothing about the true effect, by construction — that is
the point. **Do not run the regression on real flow.** Clearing the gate is the principal's decision; he
signed off the last one and will sign off this one.

## Do not say

- That JVZ was not supported, refuted, or tested with its holes closed (C-092).
- Any scalar **M** for the household residual, or any 2024–26 attribution (C-077, C-080, C-086, C-090, C-091).
- That P5(iii)'s flow correlations are evidence either way.
- That Tier B is closed on all legs — B5/P4 (data) and B6 (arithmetic) are closed; this leg is reopened.

## Rules

- **Run every command in the FOREGROUND and block on it.** No `nohup`, no trailing `&`, no detached worker,
  no "I'll wait to be notified" — completion notifications do not reach a subagent. Step 1 is a long paced
  download: if it exceeds the tool timeout, split it into slices and run them in sequence, still in the
  foreground. Report only output you actually observed; a predicted result is a fabricated one.
- **State the denominator on every number**, including coverage, N, and cluster counts.
- **If your finding contradicts this brief, say so explicitly.** The supervisor's arithmetic above is itself a
  prediction and has been wrong twice this week.
- **Never route around a refusal.** If a step is blocked, say which and why, and do the rest.
- **No summary or report files.** Findings go in the gate doc and the handover row.
- **We never pay for data (E-005).** Yahoo rate limits are a pacing problem, not a reason to buy anything.
- Hand over when you stop:
  `bin/check.sh --handover write grok 6c-gate-rerun <done|paused|blocked> "<PASS or FAIL, and the four numbers>"`
