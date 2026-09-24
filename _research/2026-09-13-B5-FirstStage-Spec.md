# B5 — first-stage specification, PRE-REGISTERED before the data arrived (13 Sep 2026)

**Written deliberately before any of the three data agents returned.** The point is to fix the test before
seeing the numbers, because the failure mode here is obvious: with a free hand after the fact I would
try band widths, lags and sub-samples until something crossed F=10, and the result would mean nothing.
Anything I change after seeing data gets recorded below as a deviation, with the reason.

## What the first stage has to establish

Does a **published rebalancing rule** move **observable purchases of US equities**? If it does not, there is
no instrument, and Tier B's sovereign-mandate design is dead regardless of how good the theory is.

## The instrument

For fund k (NBIM, GPIF) in period t:

```
Z[k,t] = ( 1{band hit}[k,t] * (target - weight)[k,t-1]  +  inflow[k,t] * w_equity[k] )
         * AUM[k,t-1] * w_US[k,t-1]
```

Two terms, and **the second matters more than I first credited.** Band hits are rare by construction. But
Norway transfers petroleum revenue into the fund continuously, and that money is allocated at strategic
weights — which is forced, price-insensitive equity buying every period, not only at thresholds. **If the
bands almost never trigger, the design does not necessarily die; it degenerates to an inflow instrument.**
That is a weaker but still real design and it should be reported as the fallback rather than a failure.

## The dependent variables — two, deliberately

1. **TIC net purchases of US equities**, Norway and Japan lines, monthly.
2. **Norges Bank 13F total reported value**, differenced, quarterly.

Two because the first has a specific, known weakness: **TIC records the counterparty's country, not the
beneficial owner.** If NBIM trades through London or a custodian, its purchases land on the UK line, not
Norway's, and the first stage fails for a measurement reason rather than an economic one. The 13F series has
no such problem — it is the filer's own holdings — but it is quarterly, long-only, US-listed, and its value
changes mix price moves with trades. Neither is clean; they fail differently, which is why both are run.

## The regression

```
Flow[k,t] = a + b * Z[k,t] + c1*r_US[t-1] + c2*r_exUS[t-1] + c3*VIX[t-1] + e[k,t]
```

Controls are required, not optional: the band is a nonlinear function of lagged global equity returns and
therefore of lagged US returns, so without them the instrument is partly just past returns.

**Frequency:** NBIM/TIC monthly; GPIF quarterly. Run each fund separately first, then pooled at quarterly
frequency with fund fixed effects. Do not pool at monthly frequency by interpolating GPIF — that would
manufacture variation.

**Units:** AUM in NOK and JPY, TIC in USD millions. Convert with period-average FX, stated per row.

**Sample:** NBIM from the effective date of the 70% target (to be verified, claimed 1 May 2019) to Jun 2026.
GPIF from the current policy mix (claimed April 2020) to the latest published quarter. **Exclude GPIF's
October 2014 policy change** — it is confounded by concurrent Japanese monetary and fiscal policy.

## Decision rule, fixed in advance

| outcome | what we do |
|---|---|
| F >= 10 on either flow measure | proceed to the reduced form |
| F >= 10 on 13F only, not TIC | proceed, 13F only, quarterly — and record that TIC country attribution is the likely reason |
| F < 10 on both, bands never bind | fall back to the inflow-only instrument and re-test once |
| F < 10 on both, inflow-only also fails | **the design is dead. Report it as dead.** Tier B then has the days-horizon dividend design and the Jiang-Vayanos-Zheng cross-sectional test, and nothing else on free data |

**F = 10 is the conventional weak-instrument threshold and is being fixed here so it cannot be renegotiated
downward later.** If the result is F = 7 I will report a failed first stage, not "suggestive evidence".

## What this first stage does NOT establish, whatever it returns

It identifies a **LATE for official and pension mandate flow** — not a multiplier for the household sector,
which is 44.6% of gross buying in 2024Q1-2026Q2 and is a Z.1 residual anyway. It is not a scalar for Z.1
sector lines (C-077). It cannot fill a valuation-level hole (C-078). And per van Binsbergen, David & Opp, a
persistent instrumented price shift identifies a shifter-process elasticity rather than a structural one —
so even a clean result is an estimate of a specific object, and the object must be named every time.

## Deviations from this spec

**13 Sep — ADDITION (not a change to the test): a cross-measure diagnostic run before the first stage.**
The spec names two dependent variables *because they fail differently*, and the specific worry was that TIC
attributes a trade to the counterparty's country, so NBIM trading through London would land on the UK line.
That worry is now largely answered, and it was cheap to answer.

Method: from Norges Bank's 13F total value I formed implied net trades as
`dValue - lagged_value * (S&P price return over the quarter)`, and compared them with TIC's Norway line
summed over the same three months.

- **Correlation +0.6152 over 45 quarters (2015:Q2 - 2026:Q2).**
- Means are the same order: 13F-implied $3,590mn/quarter, TIC Norway $4,309mn/quarter.

**Reading: TIC's Norway line does carry NBIM's US equity trading.** Custodial attribution degrades it but
does not destroy it. Both dependent variables stay in the design.

**What this diagnostic is NOT.** The proxy uses the S&P price return as a stand-in for NBIM's actual US
portfolio return — no dividends, no composition, no non-S&P US holdings — so the residual is partly my
approximation rather than partly trading. And TIC "Norway" is every Norwegian entity, not NBIM alone. A
correlation of 0.62 between two crude measures of the same underlying quantity is encouraging, not a
validation. It does not license dropping either measure.



**13 Sep — RESULT, GPIF leg: the band-hit instrument is DEAD for Japan, and the reason matters.**

Verified by recomputing headroom from the raw quarterly allocations, independent of the agent's own gap file:
**the foreign-equity band has never bound in 25 quarters.** Minimum headroom 4.51pp, and that in
2020:Q2 — the transition quarter immediately after the new policy mix took effect, so it is a regime-change
artefact rather than drift. Every other quarter sits 5.7-7.0pp clear of the edge.

**A correction to the BR2 parcel, which I had passed on unchecked.** Grok stated a +/-6pp foreign-equity band
from April 2020. The verified primary source gives **+/-7pp for FY2020-FY2024, and +/-6pp only from
1 April 2025.** Three years wrong, and it applies to a narrower risk regime than the one governing most of
the sample. Anyone rebuilding this must use 7pp before 2025:Q2.

**What the allocation series actually reveals, and it is more interesting than the negative.** Excluding the
transition quarter, the deviation from the 25% target has a standard deviation of about 0.6pp and never
exceeds ~1.1pp. **GPIF is not drifting toward a band and waiting — it is rebalancing continuously to hold the
target.** So forced, price-insensitive flow from GPIF is real and sizeable; it simply is not
threshold-triggered, and a band-crossing instrument cannot see it.

**But this does NOT rescue the design, and I want to be careful not to spin a negative into a positive.**
The obvious replacement — instrument with the rebalancing trade implied by holding weight constant as
relative returns move it — is a *smooth function of lagged relative returns*. That is precisely the
endogeneity Grok named as the main threat, and the threshold nonlinearity was the thing that gave the band
design its identifying power. **Losing the threshold makes identification harder, not easier.** A continuous
rebalancing instrument is a weaker design than the one we set out to test, not a lateral move.

**Consequence for the remaining leg.** The only clean source of identification left in this family is a flow
that is large, mandated, and *not* a function of equity returns at all. NBIM's petroleum-revenue inflow is
exactly that shape — government transfers are driven by oil and gas revenue, not by US equity prices. If the
Norwegian leg also fails, the pre-registered decision rule sends this design to "dead", and Tier B falls back
to the dividend-timing design and the Jiang-Vayanos-Zheng cross-sectional test.

**Directional note for when the first stage runs:** the 13F-implied series is noisier than TIC
(sd $18,511mn against $12,069mn), which is consistent with my return proxy adding variance. Expect a weaker
first stage on the 13F leg for that reason alone, and do not read it as economics.


---

# EXECUTED RESULT — 13 Sep 2026. The design is DEAD by the pre-registered rule.

## Leg 1, GPIF band: dead on no variation
Never bound in 25 quarters; minimum headroom 4.51pp, in the transition quarter. Recorded above.

## Leg 2, NBIM band: dead on unobservability, which is worse than a failed test
The rule is verified exactly at source — 70% strategic weight, 2pp band, assessed **on the last trading day
of each month**, effective 1 May 2019. But **NBIM publishes the metric the rule is defined on (equity share of
the *actual benchmark index*) only at YEAR-END.** Quarterly and half-year reports give a different,
fund-level figure on a wider denominator, and the two differ by 0.9-1.4pp — enough that at 31 Dec 2025 the
benchmark figure (72.20%) was past the 72.00% trigger while the fund figure (71.3%) was not. **We cannot
observe a monthly trigger from annual data.** Separately, there is exactly **one documented crossing in 7+
years** (March 2020, COVID: 65.8%, NBIM's own words "This triggered a rebalancing"), plus an apparent but
undocumented overshoot running 2024-2026. One event is not an instrument.

## Leg 3, NBIM inflow — the fallback the rule allowed, run once, FAILED

Instrument: annual net government inflow (NOK bn) x 0.70 strategic equity weight x US share of the equity
benchmark, converted at an FX rate implied by NBIM's own NOK and USD fund values. Dependent: TIC Norway net
purchases of US equities, summed to calendar years.

| | |
|---|---|
| n | **9 annual observations (2017-2025)** |
| correlation | +0.5723 |
| slope | **+1.078** — $1 of forced buying shows up as $1.08 on the TIC line |
| R-squared | 0.3275 |
| **first-stage F** | **3.41** |
| pre-registered threshold | **10** |
| **verdict** | **FAIL** |

**And this is the most favourable version that can be constructed.** The spec required three controls
(lagged US return, lagged global-ex-US return, VIX); nine observations cannot support them, and adding any
of them only reduces F. Quarterly inflows exist for just **nine non-consecutive quarters** (Q1 and Q3 only,
2022-2026), and the agent flagged them as its own interpretation of press-release wording rather than an
NBIM statement of single-quarter flow — so the quarterly route is not a rescue either.

## What this result IS and IS NOT

**It is not evidence that mandate flows do not move prices.** The slope is +1.08 with the right sign and a
plausible magnitude, and the correlation is +0.57. **The finding is that we cannot detect it** — nine
observations, no usable controls, and a dependent variable that also contains every other Norwegian entity.
Stating "no effect" here would be exactly the error of reading an underpowered null as a zero.

**What killed it was data frequency, not economics.** Both sovereign funds behave as the theory predicts:
GPIF rebalances continuously to target, NBIM rebalances gradually by design after its 2019 reform. Both
generate real forced flow. Neither *publishes* that flow at a frequency that supports identification. The
2019 NBIM reform is quietly fatal here — it replaced discrete, observable rebalancing events with gradual
execution precisely so no single dramatic trade occurs, which is good policy and destroys the experiment.

## Pre-registered consequence, honoured

> "F < 10 on both, inflow-only also fails → **the design is dead. Report it as dead.**"

**[E-005 RESTATEMENT, 14 Sep — the standard this was closed against no longer applies.]** The principal
ruled the same day that the bar is *"a rough understanding, not proof everything to the last cent"*, and
that a directionally-right estimate with a wide band is a result rather than a failure. Under that standard
**this is not a dead design, it is a weak result**: a slope of **+1.078** with correlation **+0.57** says a
dollar of forced mandate buying shows up as roughly a dollar of observed purchases — right sign, plausible
magnitude, imprecise at n=9. **Carry it as that, with the band, not as a null.** What genuinely limits it is
publication frequency, not the F-statistic, and that limit is unchanged.

**What survives from the original framing:** pre-registering the METHOD before seeing data — that is what
stopped the spec being tuned to a flattering answer, and it stays. What is retired is the kill-threshold: a
number that misses 10 no longer closes a line of work.

**The original verdict, superseded but preserved for the record:**

Tier B item B5 is **CLOSED, negative.** Do not revive it by loosening the threshold, adding a fourth
frequency, or splicing the two funds to buy observations. If it is ever reopened, the trigger is new data,
not a new specification: NBIM or GPIF publishing benchmark-basis weights or mandate flows at monthly
frequency.

**Tier B now rests on the two designs that survive:** the dividend-timing design (Hartzmark-Solomon, daily
free data, a days-horizon object) and the Jiang-Vayanos-Zheng cross-sectional test — the latter testable
against holdings data we already hold, which makes it the cheaper of the two to start.