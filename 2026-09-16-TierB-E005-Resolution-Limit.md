# Tier B / E-005 — resolution limit on the money→price bridge (16 September 2026)

> **[C-092 + Gate Rerun] JVZ is UNINFORMATIVE underpower, not a rejection.** Prior Stage B / sharpen are **UNINFORMATIVE**, not NOT SUPPORTED (C-092). Stage A's gate used **2σ/√N on 3,936 firm-quarters** (MDE 0.451pp) when the realised two-way-clustered SE gives **1.622pp** — effective n was **304**. Corrected placebo gate (`_research/2026-09-16-JVZ-Gate-Rerun.md`): **FAIL** — medSE_ret=0.548 → MDE_ret=1.097pp (0.48× vs 0.528); medSE_idio=0.239 → MDE_idio=0.478pp (0.90× vs 0.43); SD_with=0.579; **26** time clusters bind; **no real-flow regression**. Principal cleared permanent close on that FAIL. Do **not** say JVZ was not supported / refuted / mechanism false.

**Status: PERMANENTLY CLOSED 16 Sep under E-005.** Principal cleared on corrected JVZ gate FAIL. Not an unfinished todo. Sub-project Tier B
(frame `2026-09-13-B0-The-Bridge-Frame.md`; design ranking `_research/BR2_return_2026-09-15.md`).
**machineId:** `56a83289-aaaa-453d-a7c7-aa768bd566bb`

> Free paraphrase only. No scalar **M**. No 2024–26 attribution from these IVs.
> Failure modes distinguished per **C-091** (arithmetic ≠ data access ≠ mechanism rejection) and **C-092** (uninformative ≠ not supported).

---

## 1. One-sentence finding (E-005)

**Every free aggregate route for the bridge is closed — B5/P4 on data, B6 on arithmetic (C-091), and JVZ on demonstrated underpower (corrected placebo MDE; time clusters bind; C-092 / Gate Rerun FAIL) — not because JVZ was "not supported" or the mechanism was refuted.**

---

## 2. What Tier B was asking

B0 states the question so it can be answered:

> How much does a dollar of net buying, by investors who are not responding to price, move the aggregate value of US equities?

Call that object **M**. The bridge is **aggregate causal money→price**, not a description of who bought what. Description work (P1, ETF1, LIT1, N4) can and did proceed without M; attribution that multiplies a flow by M cannot (`2026-09-12-ATT0-First-Attribution.md`; C-077).

BR2 (`_research/BR2_return_2026-09-15.md`) ranked what remained after B5’s first stage and P4’s free Russell fail: a **days-horizon dividend payment-day IV** (primary) and a **JVZ mega-firm cross-section** (second-best mechanism test). Explicitly **not** a scalar on the Z.1 household residual, and **not** a multi-year explanation of the 2024–26 +$43.7trn revaluation.

---

## 3. Closed design ledger

| Design | Object | Free-data result | Failure mode | Citation |
|---|---|---|---|---|
| **B5** sovereign-mandate IV (NBIM/GPIF) | LATE for official/pension mandate flow into US equities | Band instruments dead (GPIF never bound in 25Q; NBIM monthly trigger unobservable). Inflow fallback: slope **+1.078**, corr **+0.57**, first-stage F=**3.41**, **n=9** — WEAK RESULT under E-005; mandate IV **DEAD** after B5+P4 | **data** (publication frequency / unobservability — not "no economic effect") | `_research/2026-09-13-B5-FirstStage-Spec.md`; RESEARCH_STATE Tier B / 6 |
| **P4** Russell reconstitution RD (= Tier B B3) | Stock-level reconstitution LATE (does not rescale to market even if identified) | Assignment t=1.61 (h=200); Δ13F t=0.78; CAR[−5,+5] t=1.55; IWB 2024 Jaccard **0.992**. First stage fails. 2SLS not reported | **data** (free substitutes are not official May ranks / full-replication lists; C-086) | `2026-09-15-P4-Russell-Elasticity-Pilot.md`; C-086 |
| **B6** dividend payment-day IV (BR2 primary) | Days-horizon temporary price-pressure LATE / mechanism presence | Kill switch trips on calendar-true dates (controlled top dummy t≈0.01). Imputed full-universe t≈1.37 **not** promoted. NYSE pay-date scout: **VERIFIED NO** free at-scale source — but that is **not** the binding limit | **arithmetic / power** (C-090, **C-091**): signal a few bp vs ~111bp daily SPY noise; true dates do not widen the yield spread | `2026-09-15-B6-Phase1-Payment-Day-Mechanism.md`; `_research/2026-09-16-NYSE-Payment-Date-Scout.md`; C-090; C-091 |
| **JVZ Stage A** MDE gate | Power gate for mega-firm passive amplification test | **UNINFORMATIVE (C-092).** Original "CLEARS GATE" used wrong **2σ/√N** on 3,936 firm-quarters (MDE 0.451pp); realised two-way-clustered SE ⇒ MDE **1.622pp**, effective n **304**. Dead quarter-collapsed design (n≈42) still fails — same trap as early P5(iii) | **underpower / bad gate formula** (C-092) — not a cleared path | `_research/2026-09-16-JVZ-MDE-Gate.md`; C-092 |
| **JVZ Stage B** mechanism | Free test: IWB intensity × Z.1 ETF holder flow | **UNINFORMATIVE (C-092).** Within-Q variation real (mean SD 0.559; n=3,936). Return β=+0.504 (t=0.62); idio wrong-signed null. Mega left-tail missing; intensity Russell-1000 not S&P500. Predicted÷realised MDE: ret **0.32×**, idio **1.01×** | **underpower** (uninformative null — not a rejection) | `_research/2026-09-16-JVZ-StageB-Mechanism.md`; C-092 |
| **JVZ Stage B sharpen** | Same object after mega + SPY holes closed | **UNINFORMATIVE (C-092)** — prior "NOT SUPPORTED" overstated. +37 megas; primary SPY `pctVal` (IVV agrees); within-Q SD 0.818; N=5,010 / 208 firms / 26Q. Excess ret β=**−0.336** (t=**−0.62**); idio β=+0.066 (t=0.22). Predicted÷realised MDE: ret **0.49×**, idio **0.72×** | **underpower** (uninformative — not "not supported" / mechanism false). Soft caveat only: Z.1 ETF holder flow ≠ paper’s `PassiveFlowSP500` — **stated, not used to reopen** | `_research/2026-09-16-JVZ-StageB-Sharpen.md`; C-092 |
| **JVZ Gate Rerun** corrected placebo MDE | Binding free-data power check after C-092 | **FAIL.** Coverage 540/587; top-40 megas 40/40; SD_with=**0.579** (26Q); N=10,729 FQ / 439 firms / **26** time clusters. Placebo 200 draws: medSE_ret=**0.548** → MDE_ret=**1.097pp** (**0.48×** vs 0.528); medSE_idio=**0.239** → MDE_idio=**0.478pp** (**0.90×** vs 0.43). Quarter clustering binds. **No real-flow regression.** Principal cleared permanent Tier B close on this FAIL | **demonstrated underpower** (time clusters bind; free N-PORT span cannot resolve predicted effect) | `_research/2026-09-16-JVZ-Gate-Rerun.md`; `_research/2026-09-16-JVZ-Gate-Rerun-Spec.md` |

**Count:** seven ledger rows (four identification designs + original MDE gate + Stage B intermediate + corrected Gate Rerun). Designs that could have delivered an aggregate causal estimate under free data: **B5, P4, B6, JVZ** — all closed for bridge purposes.

### Re-derive (one load-bearing number)

From C-091 / RESEARCH_STATE 6a figures already on disk:

- Full-universe top−bottom payment-yield spread = **1.32 bp** of mcap; SPY daily sd = **111 bp**.
- Predicted return gap at Hartzmark–Solomon M≈1.9: **1.9 × 1.32 = 2.508 bp**.
- Days per quintile for t≈2 on a top−bottom contrast:  
  \(n_q = 2(\sigma / (\widehat{\Delta}/2))^2 = 2(111 / 1.254)^2 \approx \mathbf{15{,}670}\)  
  (C-091 quotes 15,632 — same arithmetic).
- With ~80% of trading days carrying positive payment yield (B6 full-universe window), total trading days ≈ \(15{,}670 \times 5 / 0.80 \approx 98{,}000\) ≈ **~390 years** (C-091: **386 years** at their rounded 97,300). At envelope top M=9.4 the same algebra needs ~16 years; the sample has 11.7. **True NYSE pay dates remove timing noise; they do not widen 1.32 bp.** Hence C-091: arithmetic, not data access.

JVZ Gate Rerun cross-check (authoritative for power): MDE_ret = 2 × 0.548 = **1.097 pp** vs predicted **0.528 pp** → **0.48×**; MDE_idio = 2 × 0.239 = **0.478 pp** vs **0.43 pp** → **0.90×**. Sharpen ret t = −0.336 / 0.544 = **−0.618** remains an uninformative point estimate (C-092), not a rejection.

---

## 4. What we can still say (positive residue)

Only what the sources actually support:

1. **Within-quarter passive intensity variation is real** — IWB Stage B mean within-Q SD of `pctVal` = 0.559 (23/23 quarters); SPY sharpen = 0.818 (26/26); Gate Rerun SD_with = 0.579 (26/26). Gate does not collapse to n≈42 (`_research/2026-09-16-JVZ-StageB-Mechanism.md` §0; Sharpen §2; Gate Rerun §2).
2. **Stage A MDE formula does not stand (C-092)** — its σ/√N overstated precision ~3.6×. Corrected Gate Rerun demonstrates the free design cannot see JVZ’s predicted return effect under two-way clustering. What also survives: the quarter-collapsed P5(iii) test was underpowered. Early P5(iii) weak-negatives are **not** evidence either way.
3. **No scalar M was invented** — ATT0/C-077 retraction stands; B6 and JVZ explicitly refuse household-residual / 2024–26 multipliers.
4. **B5 slope is a weak first-stage fact under E-005** — ~$1 of forced mandate buying ≈ $1.08 on TIC Norway (n=9, no usable controls) — directionally right, imprecise; **not** an identification strategy for reduced-form M until monthly mandate flows are published.
5. **B0/BR2 framing corrections stand** — Z.1 net issuance is not the demand-shift denominator (C-080); "only boundary-crossing flows matter" is too strong as a universal rule (JVZ mechanism paper cited in B0); stock-level elasticities do not rescale when the counterparty is another equity.
6. **Free NYSE payment-date coverage at S&P500 × 2015–2026 scale is absent** — scout finding kept (`_research/2026-09-16-NYSE-Payment-Date-Scout.md`); useful negative, not a reopen trigger (C-091).
7. **26 free N-PORT quarters cannot resolve a 0.528 pp predicted return effect under two-way cluster** — Gate Rerun FAIL; quarter clustering ≈ two-way SE; firm-only SE is much smaller. Precision is governed by shock periods, not firm-quarters.

---

## 5. What we cannot say / must not claim

| Ban | Why |
|---|---|
| Any household-residual **M**, or "flows explain X% of 2024–26 via multiplier Y" from these IVs | Object never identified; C-077 |
| **2024–26 attribution** from B5 / P4 / B6 / JVZ | Explicit non-objects in every parcel |
| "B6 **mechanism failed** / was refuted / tested and found absent" | C-090: uninformative null; underpowered |
| "B6 is **blocked on NYSE pay dates**" / reopen B6 for corporate-actions data | **C-091**: arithmetic; scout answered the wrong question |
| Quote **P5(iii)** flow correlations as findings | Underpowered dead design; Stage A / Gate Rerun exist to stop that reading |
| Paid-data unblocks that would only fix **B5/P4** (monthly mandate prints; official Russell lists) as if they also fix **B6** | B6’s limit is signal-to-noise, not missing dates |
| P4 multiplier / LATE / rescale to market | C-086; first stage never assigned treatment |
| Treat JVZ soft caveat (Z.1 ≠ PassiveFlowSP500) as reopening Tier B | Stated; **does not reopen** after Gate Rerun FAIL + principal clearance |
| "JVZ **not supported** / refuted / mechanism false" | **C-092**: Stage B/sharpen are UNINFORMATIVE; Gate Rerun shows underpower, not rejection |

---

## 6. Resolution limit named

**Free data cannot deliver a credible aggregate money→price multiplier / LATE for the bridge as B0 framed it. Every free aggregate route is closed.**

- Routes that needed **observability of treatment** failed on **data** (B5 frequency; P4 free substitutes).
- The route that had treatment timing (B6) failed on **arithmetic** (few-bp signal vs ~111 bp daily noise; C-091).
- The JVZ route failed on **demonstrated underpower**: corrected placebo MDE (Gate Rerun) shows predicted÷MDE **0.48×** (return) and **0.90×** (idio) with **26** free N-PORT quarters under two-way cluster — those quarters **cannot see** JVZ Table 6.2’s **0.528 pp**. Prior Stage A/B/sharpen are **UNINFORMATIVE (C-092)**, not "NOT SUPPORTED". Soft Z.1≠`PassiveFlowSP500` caveat is noted and **does not reopen** Tier B.

This is the standing finding under E-005. **PERMANENTLY CLOSED 16 Sep** after principal clearance on gate FAIL. Weigh it before a fifth free aggregate design.

---

## 7. Process lesson (brief)

**MDE-before-commission (C-090 / C-091 / C-092).** Arming a kill switch without a minimum-detectable-effect check produced an uninformative null, then a scout commissioned on a misdiagnosed cause. Screening rule now in CLAUDE.md / RESEARCH_STATE 6a: any design whose predicted effect is a few bp against daily equity noise is unresolvable on a decade of daily data — compute the MDE in the brief, before commissioning. C-092 / Gate Rerun add: do not clear a clustered panel with σ/√N on firm-quarters; placebo or cluster-aware MDE first.

---

## 8. Explicit bans (echo)

1. **No M** — no household residual multiplier; no invented bridge coefficient.
2. **No reopening B6 for NYSE dates** — C-091; arithmetic limit.
3. **No quoting P5(iii) correlations as findings** — underpowered; not evidence.
4. **No "JVZ not supported / mechanism false"** — C-092; Gate Rerun FAIL is underpower.

Tone of claim: E-005 rough understanding with bands. Denominators on numbers. Cite files, not memory.

---

## Sources (authoritative; this note invents nothing)

- Frame: `2026-09-13-B0-The-Bridge-Frame.md`
- Design ranking: `_research/BR2_return_2026-09-15.md`
- B5: `_research/2026-09-13-B5-FirstStage-Spec.md`
- P4 + C-086: `2026-09-15-P4-Russell-Elasticity-Pilot.md`; `CORRECTIONS.md`
- B6 + C-090 + C-091: `2026-09-15-B6-Phase1-Payment-Day-Mechanism.md`; `_research/2026-09-16-NYSE-Payment-Date-Scout.md`
- JVZ: `_research/2026-09-16-JVZ-MDE-Gate.md` (UNINFORMATIVE / C-092); `_research/2026-09-16-JVZ-StageB-Mechanism.md` (UNINFORMATIVE); `_research/2026-09-16-JVZ-StageB-Sharpen.md` (UNINFORMATIVE); `_research/2026-09-16-JVZ-Gate-Rerun.md` (**FAIL** — permanent close reason); `_research/2026-09-16-JVZ-Gate-Rerun-Spec.md`
- State blocks: `RESEARCH_STATE.md` Tier B / 6 / 6a / 6c
- Standard: `THE_ASK.md` E-005; `CLAUDE.md` working rules (rough understanding; never pay for data); C-092

**Pointer for RESEARCH_STATE:** cite this path —  
`2026-09-16-TierB-E005-Resolution-Limit.md` (project root).

---

## Appendix — RESEARCH_STATE replacement text (items 6 and 6c)

Parent should paste these into the ranked fence in `RESEARCH_STATE.md` (blocks clearly identifiable as item 6 / 6c). Sidecar copy: `_research/2026-09-16-RESEARCH_STATE-6-6c-REPLACEMENT.md`. Live RESEARCH_STATE was left unchanged here — full-file rewrite not applied safely via MCP create_file size path.

```
6. TIER B - the bridge (standing)            PERMANENTLY CLOSED 16 Sep -> 2026-09-16-TierB-E005-Resolution-Limit.md
                                            (E-005; principal cleared on corrected JVZ gate FAIL).
                                            Every free aggregate route closed: B5/P4 = data; B6 = arithmetic
                                            (C-090/C-091) — NOT "mechanism failed", NOT blocked on NYSE dates;
                                            JVZ = demonstrated underpower (C-092 + Gate Rerun FAIL) — NOT
                                            "not supported" / mechanism false. Frame B0; BR2 ranking.
                                            JVZ Stage A/B/sharpen = UNINFORMATIVE (C-092). Gate Rerun:
                                            medSE_ret=0.548 MDE_ret=1.097 (0.48×); medSE_idio=0.239
                                            MDE_idio=0.478 (0.90×); SD_with=0.579; 26 clusters bind; no
                                            real-flow regression. Soft Z.1≠PassiveFlowSP500 does not reopen.
                                            No M. No P5iii quotes. Weigh before any further free aggregate IV.
```

```
6c. JVZ mega-firm passive amplification    GATE RERUN FAIL 16 Sep -> _research/2026-09-16-JVZ-Gate-Rerun.md
    (principal clearance)                   Principal CLEARED permanent Tier B close on this FAIL (C-092).
                                            No real-flow regression. Coverage 540/587=0.920; top-40 megas 40/40.
                                            Within-Q SD SPY pctVal WITH megas **0.579** (26Q) — did NOT rise to
                                            ~1.6 (without megas 0.106). N=10,729 FQ / 439 firms / 26 time clusters.
                                            Placebo 200 draws (two-way cluster): median SE ret **0.548** → MDE
                                            **1.097pp** (pred÷MDE **0.48×** vs 0.528); idio SE **0.239** → MDE
                                            **0.478pp** (**0.90×** vs 0.43). Quarter clustering binds. 26 free
                                            N-PORT quarters cannot see 0.528pp under two-way cluster. Prior Stage A /
                                            Stage B / sharpen remain UNINFORMATIVE (C-092), not NOT SUPPORTED.
                                            Spec: _research/2026-09-16-JVZ-Gate-Rerun-Spec.md.
```

**Taxonomy note:** C-091 splits B6 to **arithmetic**, not data access; C-092 splits JVZ to **underpower / uninformative**, not mechanism rejection. This note uses that finer taxonomy.
