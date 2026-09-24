# The Third Derivative — Concept Map

**Status:** Complete. Two research rounds, 30 agents, three adversarial verifiers, one completeness
critic. Round 1 was returned `materially_flawed` by all three verifiers; round 2 was commissioned
against the named gaps. Evidence in `_research/`.
**Compiled:** 2 August 2026.

---

## 1. What the concept is

A primary innovation or shock does not create most of its economic value directly. It first forces a
**reorganisation** or builds an **overcapacity** — often looking like waste while it happens. That
residue is what enables a later generation of businesses, which capture most of the value.

The operator's two illustrations (electricity → shop-floor reorganisation → mass production;
internet → dot-com and fibre bubbles → cloud and streaming) were offered to *identify* the pattern,
not to defend. Both contain inaccuracies, corrected in §7. The evidentiary weight of this work sits
on the case library, not on them.

---

## 2. What it is already called

The concept is not new. It is a re-description of four established literatures, each of which has
already fought the battles this framework is about to lose. Ranked by fit:

| Rank | Name | Origin | What it names | Where it falls short |
|---|---|---|---|---|
| 1 | **Installation → frenzy → turning point → deployment** | Carlota Perez, *Technological Revolutions and Financial Capital* (2002); building on Freeman & Perez | The whole arc, including the claim that the bubble is functionally necessary because it over-builds the infrastructure deployment then exploits | Periodisation is contested; Perez herself distinguishes technology bubbles from easy-money bubbles — a distinction the operator's framing collapses |
| 2 | **The productive bubble** | William Janeway, *Doing Capitalism in the Innovation Economy* (2012) | The precise mechanism: malinvestment leaves a usable residue | Carries a restriction the operator relies on implicitly — it applies to general-purpose *network* infrastructure, not to bubbles generally |
| 3 | **General Purpose Technology + co-invention** | Bresnahan & Trajtenberg (1995); Helpman (1998) | Layer 1, and why its value requires downstream complementary invention | Models coordination failure, not overcapacity or malinvestment |
| 4 | **Complementary organisational capital / the dynamo-and-computer lag** | Paul David (1990); Warren Devine, "From Shafts to Wires" (1983); Brynjolfsson & Hitt | Layer 2 as reorganisation — and this is literally the source of the operator's electricity example | Firm-level; the same firms capture the payoff, so it does not carry the value-migration claim |
| 5 | **Complementary and cospecialised assets** | Teece (1986), "Profiting from Technological Innovation" | *Why* the originator fails to capture value — the best-established support for the value-migration feature | Explains distribution within one wave, not across waves |
| 6 | **The productivity J-curve** | Brynjolfsson, Rock & Syverson (2021) | Makes the lag measurable: apparent waste, then payoff | Within-firm intangible investment; same firms capture |
| 7 | **Fordism / Régulation School** | Aglietta, Boyer, Lipietz; Gramsci (1929–30); Piore & Sabel (1984) | The established name for the operator's example (a) third order | Inverts the causality — see §7 |

**Also relevant:** combinatorial innovation (Weitzman 1998; Arthur 2009) and the adjacent possible
(Kauffman) for unpredictability; generativity (Zittrain 2008) for why a substrate yields
unanticipated applications; absorptive capacity (Cohen & Levinthal 1990) for why only some actors
can exploit a residue; Hirschman (1958) on infrastructure built ahead of demand as a forcing
function.

**Counter-literature that must be engaged, not ignored:** Rosenberg & Frischtak (1984), *Long
Waves: A Critical Appraisal* — the canonical demolition, and the framework as originally stated
fails all four of their requirements. Goldfarb & Kirsch, *Bubbles and Crashes* (2019). Klepper &
Simons on industry shakeouts. Eisfeldt & Rampini on procyclical capital reallocation.

**On the name itself.** "Third derivative" carries a false mathematical promise — a third derivative
is a well-defined quantity computed with respect to a specified variable, and nothing here is. The
term is retained as the house label because it communicates, but it should never be presented as
though the ordinal were measured.

---

## 3. Three retractions

These are not negotiable; the evidence forced them.

**R1 — The ordinal is not repairable as a count of technology generations.** Across the assembled
corpus, *every* third order is some other case's first order. The assembly line is L3 of
electrification and L1 of mass production. Semiconductors are L3 of Apollo procurement and L1 of the
PC. Worse than indexical: David and Wright describe electrification as a **confluence of parallel
converging trajectories**, and note explicitly that automated materials handling did not require
electrification. In a lattice, "which layer is this" has no answer even in principle.

**R2 — "The bubble made the capacity cheap" is largely wrong.** Kermani & Ma (2020): cyclical
conditions move liquidation recovery rates by only 5–10 percentage points, while fixed physical
attributes — mobility, durability, customisation — explain roughly 40% of cross-industry variation.
**Specificity sets the price; the cycle does not.** The bubble's causal role downgrades from
"creates the discount" to "creates the asset in irrational quantity, and supplies the cessation
event that dislodges it."

**R3 — "Usually different people" is false as a general claim.** Klepper & Simons: 4 out of 4
industries where post-shakeout leaders are early entrants, adjacent diversifiers, or spinoffs of the
best early entrants. In US autos the 1895–1904 cohort's annual exit hazard was 76% below the
1910–66 cohort's at age 15. Chandy & Tellis put ~74% of post-1945 radical innovations with
incumbents. And in the operator's own example: AWS, Google and Netflix are bubble-era firms run by
bubble-era people; Salesforce was founded inside the frenzy (1999); Illumina 1998; DJI and Anker
during the shanzhai boom; Tesla in 2003, before Cleantech 1.0.

---

## 4. The repair — the Input-Price Frame

Stop counting technologies. **Count claims on one metered capacity.**

Before any layer assignment, register four things in writing, timestamped:

1. **The metered input.** A specific, quotable unit price `P(t)` for a physical or legal capacity —
   $/Mbps-month of IP transit, $/satellite voice-minute, $/kW-year of dispatchable capacity,
   $/GPU-hour of a named accelerator class, $/MW-year of energised interconnected datacentre
   capacity. It must be a published or contractible series, **not a narrative**.
2. **The build-justifying price `P*`.** The price the layer-2 capital's own pro formas required to
   return cost of capital. This is a *historical fact*, recoverable from prospectuses,
   project-finance models, auction bids, rate cases, take-or-pay terms and filed depreciation
   schedules. Fixing `P*` from documents rather than from judgement is what makes the frame
   non-indexical.
3. **The threshold business class.** A named downstream class at a stated NAICS/SIC level, with a
   customer set distinct from the builders', whose gross margin is negative at `P*` and positive at
   some `P` below it. **Named before the outcome.**
4. **The condition scorecard.** PASS/FAIL on C1–C9 (§5), recorded before the outcome window opens.

Then the ordinal is defined by enumerating **the balance sheets that have owned the economics of
that one capacity**:

- **First order** — the builder, who underwrote at `P*`
- **Second order** — the claimant who takes the write-down: bondholders, receiver, acquiring
  creditor, or the state where losses are forced administratively
- **Third order** — the operator or consumer whose business exists only because `P` is now below `P*`

"Third order" therefore means **the third claim on a single named capacity**, not the third
generation of a technology. Claims on an asset are enumerable and finite; technologies are not.

**This gives the endogenous stopping rule the framework lacked.** You may run the frame again on a
different metered input, but not on the same one — once capacity is held at written-down basis by an
operator whose business works, there is no further write-down to harvest. The number of write-downs
on a given asset is finite and typically one. That comes from the accounting, not from a judgement
about when generativity decays.

> **The repair costs the operator example (a) outright.** There is no single metered input whose
> price collapse the assembly line consumed. Under the repaired frame it is not third order of
> anything — which is exactly how David and Wright classify it. That a repair excludes the flagship
> example is evidence it is doing work rather than accommodating.

---

## 5. The discriminating test

**In one sentence:** a second-order overbuild produces a third order if and only if the written-down
capacity is (i) legally dislodgeable into the operating control of an agent with no sunk commitment
to the build, (ii) a general-purpose input to a downstream industry *other than* the product market
the builders were competing in, and (iii) facing surviving physical output demand at the moment the
revenue model dies — and the advantage is durable only if (iv) the substrate fraction is large and
(v) its real replacement cost is not deflating faster than the cost-basis gap can be amortised.

| # | Condition | Type | Observe it by |
|---|---|---|---|
| **C1** | **Alienable operating control at a cost-based price.** Control must be able to move to an agent with no sunk commitment — via liquidating sale, reorganisation that extinguishes equity, mandated third-party access at cost-based prices, or forced write-down without insolvency. The variable is *forced recognition of loss plus transferable control* — not bankruptcy, and not legal title. | necessary | Read the licence (does it transfer in insolvency, or lapse?); the security documents (what fraction of L2 capital is in mark-to-market hands?); the access regime |
| **C2** | **Output-demand survival.** Physical demand for the capacity's output must survive and preferably grow through the cessation. What dies is the revenue model, not the demand. | necessary | Compound growth in *physical units* — bits, satellite-minutes, MWh, seat-miles — peak to peak+5yr. Deliberately not revenue |
| **C3** | **Cross-market input, not same-market output capacity.** The residue must be a general-purpose input to a *different* downstream industry. | necessary | Name the industry ex ante at a stated NAICS level with a demonstrably distinct customer set |
| **C4** | **High substrate-to-overlay ratio.** Durable, immobile, low-customisation fraction (civil works, rights-of-way, conduit, spectrum, interconnection) large relative to short-lived vintage-specific fraction (electronics, tooling, chemistry). | contributory | Decompose L2 capex into 20–40yr near-zero-obsolescence assets vs 3–7yr high-customisation assets |
| **C5** | **Reset persistence.** Real replacement cost must not be deflating faster than the basis advantage can amortise. Working threshold: **>5%/yr real decline = FAIL**. | contributory | Ten-year trend in real *build* cost per unit — the build curve, not the output-price curve |
| **C6** | **Aggregability, and pricing as a metered service.** Re-assemblable by one or few buyers, *and* purchasable downstream as a metered unit priced off the written-down basis — not only as lumpy title. | contributory | Count separable parcels; then ask whether a downstream firm can buy a metered unit without buying the asset |
| **C7** | **Recombination permission in the labour market.** Where the residue is human, the jurisdiction's law and norms must permit recombination. | contributory | Non-compete enforceability, inevitable-disclosure doctrine, spinoff equity norms, local early-stage capital density — all published years ahead |
| **C8** | **Physical completion before cessation.** Announced, permitted or partially built capacity has nothing to dislodge. | necessary | Commissioned units vs announced units. Trivially observable and routinely ignored |
| **C9** | **Shared-asset incompatibility.** The only defensible version of "different people": incumbents fail to capture *iff* the third-order business requires shared use of a firm-level asset on incompatible terms — a price book, tariff, channel, depreciation schedule or cannibalised revenue line. **Name it before the outcome.** | contributory | Write down the specific asset and the specific incompatibility in one sentence. If you cannot, predict incumbent capture |

C1–C3 and C8 are jointly necessary; C1–C3 are jointly sufficient across this corpus for a third
order to *appear*. C4–C5 separate a durable third order from a two-year arbitrage. C9 determines
*who* captures, not *whether*.

**Yield: roughly 6–8 passes out of ~30 candidate episodes.** The failures distribute across
different conditions rather than piling onto one — the property a multi-condition test needs in
order not to be a single variable in disguise.

### The exclusion is the most valuable part

If the candidate overbuild is **competing output capacity in the market it was built to serve** —
more solar modules, more airline seats, more radio receivers, more merchant megawatts, more of the
same tokens sold to the same buyers — **the framework does not apply.** In that region Klepper and
the Capital Cycle are correct: the cull is endogenous, driven by returns to process R&D scaling with
output, it requires no bubble at all, and the winners are survivors with a lineage. Forecast
consolidation, not succession.

The framework's entire domain is the complement: overbuilds whose residue is an **input to somebody
else's industry**. That is the only reason "different people" appears at all — not because busts
create new cohorts, but because the incumbents are, by construction, in the wrong industry to be the
buyers.

---

## 6. Who actually captures the value

Three findings, the third uncomfortable and the most useful.

1. **"Different people" conflates three things with very different base rates.** *Different cost
   basis* — high base rate, and this is the real mechanism; it does not require a new firm (Cogent,
   NTL→Virgin Media and the recapitalised Japanese banks achieved it as the *same* firms with
   extinguished claims). *Different legal entity* — medium, largely an artefact of insolvency law.
   *Different lineage* — low. Klepper is right. Claim the first, retract the third.

2. **Klepper and the operator describe complementary regions, not contradictory ones.** Every
   Klepper industry concerns same-market output capacity, where the only asset is market position,
   which cannot change hands cheaply because nobody outside the market wants it.

3. **In the best-documented qualifying cases, value does not accrue to the buyer of the asset
   either.** Cogent, Level 3 and Zayo bought the fibre and earn utility returns. Netflix and
   Cloudflare bought *metered services* priced off written-down assets and captured the equity
   value. The general statement is Teece (1986): **value accrues to whoever holds the cospecialised
   complement that remains scarce after the input price collapses.** In fibre that was content
   rights, subscriber relationships and the last mile. In post-WWI aviation it was the airmail
   contract — a *statutory* complement supplying ~95% of early carrier revenue, without which
   surplus Jennys at $50–100 apiece would have produced barnstormers and nothing else.

This has direct prospective bite: after inference prices collapse, value goes to holders of scarce
complements — proprietary distribution, regulated data, workflow lock-in, firm power and
interconnection — not to whoever buys distressed accelerators, and not to a new cohort of model labs.

---

## 7. The two illustrations, corrected

**Example (a) — electricity.** Breaks at three of four joints, and the blow comes from the
framework's own authorities. Highland Park in 1913 ran on electric **group drive** — overhead line
shafts each turned by a large motor, the shallow no-payoff configuration. Unit drive and
single-storey linear layout reached Ford in the 1920s. The line sat *between* two phases of the
reorganisation and helped pull the second. The WWII tail must be cut outright: Field measures
manufacturing TFP *falling* at −5.1%/yr 1941–45, and the capacity was federally financed via the
Defense Plant Corporation and mostly not retained by the firms that operated it.

What survives is narrower and cleaner: L1 practical electric power 1880s–1900s; L2 a twenty-year
no-payoff group-drive retrofit 1899–1919 **plus a utility holding-company frenzy c.1922–1932**
(Insull — the genuinely missing middle, whose collapse produced PUHCA 1935, the TVA and rural
electrification); L3 the 1919–29 reorganisation on unit drive and single-storey layout, delivering
industrial TFP near 5–6%/yr against roughly 1% before.

**Example (b) — the internet.** Must be **split**. The video/CDN chain survives and is
quantifiable. The cloud/SaaS chain is falsified by the ASP-to-SaaS natural experiment: bandwidth was
under 1% of ASP revenue even at peak-1998 transit prices, so a 100× fall in a line item that small
cannot bind. Salesforce was founded March 1999 — inside the frenzy, on input prices identical to
Corio and USinternetworking — and survived on **multi-tenancy**, an architectural choice. AWS's
documented 2003 origin contains no bandwidth reasoning at all, and Werner Vogels has called the
excess-capacity story a myth.

**AWS and Azure come off the list. Cloudflare (2009) is the only well-chosen name on it.** Two
statistics must be struck: the "2.7% dark fibre" figure (a misquoted single-city datapoint) and any
telecom *skills* claim — no public tracing of WorldCom, Global Crossing or 360networks engineers
exists, and carrier employment never recovered.

The strongest datum in the framework's favour is not a percentage of dark fibre. It is that **no new
US national long-haul network was built from the late 1990s until roughly 2015–17.**

---

## 8. Falsification

Three separable claims with different standing. Anything scored *after* an outcome is inadmissible
as evidence *for* the framework, though always admissible against it.

- **F1 — Emergence (live).** Register the frame at `T0`, the date `P` first crosses below `P*` and
  stays. Falsified by insufficiency if a case passing C1–C3 shows the capacity scrapped, mothballed
  or below 20% utilisation ten years on. Falsified by loss of necessity if a case failing C1, C2 or
  C3 nonetheless produces the business class at scale. Falsified as a reset if `P` recovers to `P*`
  within five years without a new-build cycle — that is an inventory cycle in a technological
  costume.
- **F2 — Identity ("different people").** *Already returned negative.* The honest move is
  retraction, not further testing.
- **F3 — Mechanism.** The framework and Shleifer–Vishny predict the **same observable** — assets
  exiting the incumbent class in a bust — with **opposite welfare signs**. Two tests separate them:
  post-transfer *utilisation must rise* (Iridium passes: switched off 2000, profitable by 2005;
  Ebone passes: dark network relit, $2.3bn exit in 2018; aerospace 1988–95 fails), and the
  insider-premium sign must be negative in claimed cases. If outsiders always pay less, the
  framework cannot be distinguished from ordinary fire-sale value destruction and should be
  abandoned as a mechanism claim.

**Highest-priority live falsifier: China post-2015.** Solar, EV, battery, fibre and property
overbuild produced dominant downstream firms with essentially no loss recognition and no title
transfer. If confirmed, C1 must be restated at the level of *realised input price* rather than legal
alienability — which weakens the framework toward tautology and should be resisted unless the
evidence compels it.

---

## 9. What this framework cannot do

1. **It cannot pick the third order.** Farmer–Lafond forecasts the unit cost of an *already-named*
   artefact — and works precisely because cost curves are smooth random walks with drift, i.e. the
   *absence* of the discontinuous jump a cascade requires. Product space is worse: relatedness
   predicts where industries *are*, not where they *grow*. **Claim exclusion power; never claim
   selection power.**
2. **It cannot claim the bubble is necessary.** Four hyperscale third orders here were built with no
   bust: Alibaba/Tencent cloud, India Stack, M-PESA, Brazil Pix. Add Unit 8200 and the German dye
   labs. This is a theory of *one route*, and not the most common one.
3. **It cannot claim the bubble is even characteristic.** Goldfarb, Kirsch & Miller find *too little*
   entry in the dot-com era, not overbuild — five-year survival approached 50%.
4. **It cannot date anything, and the "decades" claim is false.** Observed lags run from 2 years
   (Iridium) to 30–40 (electrification), with Nokia→Supercell at 3 and arguably negative.
   Gort–Klepper Stage I duration fell from 23.1 years pre-1930 to 4.9 post-1940. **The lag carries
   no information and must not be used as a screen.**
5. **It has no slot for a mandatory non-bubble intermediate layer.** Streaming was impossible
   without DOCSIS 3.0 and FiOS at roughly $23bn of incumbent cash flow, plus H.264, Silverlight,
   Roku and the Xbox. None of that is malinvestment residue.
6. **On the mechanism question it is retrospective by necessity** — post-transfer utilisation data
   does not exist until years after the transfer.
7. **"Nobody forecasts the third order" is dead as a defence.** Gilder, HP's 1998 Utility Computing
   Division, Sun Grid at $1/CPU-hour in 2006, and Hastings naming Netflix in 1997 were all ex ante
   and right in kind. They were destroyed anyway — which is *good* for the mechanism (foresight is
   not the scarce input) and fatal to any claim that this framework confers unique foresight.

**At the ceiling of the evidence,** given a named metered input, a documented `P*` and a named
candidate downstream business, it can: exclude infeasible adjacencies with meaningful precision;
bound the cost trajectory of an already-named artefact; predict which parts of an overbuild transfer
and appreciate versus which are scrapped (the substrate/overlay split); and score whether a price
reset will persist beyond one asset replacement cycle.

It cannot name the winner. It cannot date the win. It cannot tell you a bubble is coming or
required. On this corpus, the full phenomenon occurs **roughly once in ten candidate episodes.**

---

## 10. Live application

A pre-registered forward register — six current capacity events scored against C1–C9 with dated
falsification windows and verified anchor prices as at 2 August 2026 — is in
`Analysis/Forward_Prediction_Register.md`. Headline: accelerator fleets **fail** C3/C4/C5 (forecast
consolidation, not succession); power, interconnection and shells are the only durable residue but
predict **incumbent** capture; and the best-scoring case in the register is not AI at all.
