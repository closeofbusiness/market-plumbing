# RESEARCH STATE

**The live argument, what holds it up, and what would bring it down.**
Read §0 first — it is what was *asked*. Then this file after `CORRECTIONS.md` and `CALENDAR.tsv`. It is the only file that tells you what
we currently *believe*, as opposed to what we have *written*.

**Maintenance rule:** the orchestrating agent updates §2–§5 whenever a claim's status changes.
If you finish a research pass and this file still says what it said before, you have not
finished. Last updated **2026-09-11** (**GOAL AMENDED by the principal — `THE_ASK.md` E-003; §0.0 rewritten; §5 RE-PLANNED on the channel map and the Green corpus dossier**; step-ladder re-entry repair, then housekeeping: S-N2b settled row added; S4's gross-saving pair marked CONTESTED per C-047; §1.0 and Tier-N statuses turned into pointers; corrections registered since 3 Sep are C-066 to C-075 — read them with `bin/check.sh --latest`, not from this line). Previous update **2026-09-03** (housekeeping: C-047 marker finally placed; C-053 Beignet census; D1–D3 settled as S-D1/S-D2/S-D3; data layer + `bin/pull_series.py`; §5 statuses reconciled. **Afternoon:** Gemini's D3 file found on the share root and adjudicated — C-054; hedge-fund leg of D3 measured from the OFR Hedge Fund Monitor API, D3 v1.1 §8; D10 flagged. **Evening:** Gemini's N3 return verified by a 14-agent fan-out — C-055, and C-056 for my own FIA claim; margin leg of D3 measured (FIA API), FICC sponsored daily series (DTCC CSV), Singh & Goel WP/19/106 Table 2 read at source; `2026-08-23-Parcel-N3-Collateral-Return.md`).

---

## 0. The ask, and its lineage

**Recorded because a research programme drifts by forgetting what it was asked, not by
getting an answer wrong.** Every agent reads this before §1. If a piece of work does not
serve a row in this table, it is a tangent — which is allowed, but should be known.

### 0.0 THE MISSION — the standing goal (`THE_ASK.md` E-015, 25 Sep 2026; consolidates E-003, E-004, E-005 and E-007)

> Establish, in numbers with ranges rather than false precision, what is driving asset prices and where the money is coming from: above all the run-up in US equities and the funding of the AI build-out and the IPO boom, and also rates, FX and commodities. Test every channel against fundamentals (earnings, interest rates and risk premia) as the benchmark — direct money creation, shadow banking and shadow money, the collateral channel, market structure such as the passive bid and ETF creation, and any other driver the evidence reveals — and record a channel that turns out not to matter as a result. For every flow, name the buyer, the seller and the funding; treat every claim as a hypothesis until it is tested; use free data only; and publish the work openly.
>
> *The mission statement, verbatim from `THE_ASK.md` (E-015; the principal confirmed the wording on 26 Sep, E-016).
> `bin/check.sh --goal` enforces it here, in `CLAUDE.md` and in `THE_ASK.md`. Do not reword it: corruption enters
> through paraphrase. The rest of this section is the mission's working detail, not a second goal. The principal's own
> words are E-003, E-004, E-005, E-007 and E-015.*

**The question, plainly.** Asset prices have run up to records — the S&P 500 is at an all-time
high — and very large sums are funding the AI build-out and an IPO boom. What is driving prices
up, and where is the money coming from?

**What is being explained** — each measured, never assumed:
- **P · asset prices** — US equities first (level and valuation), then the other assets at records.
- **F · the AI build-out's funding** — the capex and how it is paid for: internal cash, bonds,
  loans, private credit, off-balance-sheet vehicles, leases, vendor finance.
- **I · the IPO boom** — who supplies the money that buys the new issues.

**The candidate drivers** — each a hypothesis to be sized; none is assumed to matter:
- **(a) Direct money creation** — bank credit creating deposits; the central bank's balance sheet
  (QE/QT, reserves, reverse repo, bill purchases); fiscal deficits and how they are financed.
- **(b) Shadow banking and shadow money creation** — nonbank credit (private credit, conduits,
  SPVs) and money-like claims created outside the banks (money funds, repo, ABCP, stablecoins,
  offshore dollars): the Pozsar–Singh nonbank–bank nexus. *This was the whole goal under E-002;
  that work carries over.*
- **(c) The collateral channel** — collateral re-use and velocity, and the leverage built on it
  (basis trades, prime brokerage, securities lending, margin): Singh's line of work.
- **(d) Market structure and flows** — the passive bid (index and ETF flows that buy regardless of
  price, as argued by Michael Green; the principal is supplying material), ETF creation and
  redemption, retirement-plan auto-contributions, corporate buybacks, leveraged and options
  products, foreign inflows.
- **(e) Fundamentals, as the benchmark** — earnings growth, interest rates, risk premia. A money or
  flow explanation counts only for what it adds beyond these. *(Agent's addition, not the
  principal's words; CONFIRMED by the principal 11 Sep, E-004: it stops a liquidity story from winning by default.)*
- **(f) Anything else the evidence surfaces** — flagged and investigated, not ignored.

**What makes it answerable by agents:**
1. **Every purchase has a seller.** Money does not flow "into" a market in aggregate; prices move
   when net demand meets net supply. So every answer names who is a net buyer (by sector), with
   what funding, against what net supply (issuance minus buybacks), and how far a dollar of net
   demand moves the price. *(Agent's operationalisation; CONFIRMED by the principal 11 Sep, E-004.)*
2. **Mechanism, magnitude, evidence** for every channel: how it works; its size with a range, a
   denominator and a vintage; the primary source behind it.
3. **Attributions add up.** A dollar is counted once — not as money creation and again as a
   passive flow. The unexplained residual is stated, not hidden.
4. **Each channel carries its falsifier** — the observation that would show it does not matter.

**Done looks like:** a dossier per channel (mechanism, measured size and trend, sources,
falsifier); an attribution table for P, F and I (each channel's contribution with ranges, and the
residual); the monitor (`data/series.tsv`, `CALENDAR.tsv`) carrying the signals that would show
each driver strengthening or reversing; pre-registered predictions and the corrections register.
**The goal is met when a hostile, competent reader can take any dollar of the run-up or of the
AI and IPO financing and see which channel supplied it, how we know, and how sure we are.**

**Outcome, not goal:** a Substack piece — a side condition for a later date (E-003; E-002 said the
same). It sets no priority. Ideas worth their own investigation are *flagged as such* (§5, N5).

**Test to apply before starting any pass:** *does this help explain what is driving asset prices,
or where the money behind them — the AI build-out and the IPO boom included — comes from?* If the
only defence of a task is that an essay needs it, it is not a priority.

**History.** From 21 to 22 August this file, `CLAUDE.md` and the whole of §5 ranked work by *what
the essay needed*; the principal corrected that to the nexus goal (E-002, C-041). On 11 September
the principal widened it to the question above (E-003) — an amendment by the principal, not a
correction of agent error. The nexus work is now channels (b) and (c).

| # | What was asked | Status |
|---|---|---|
| A1 | Get up to speed with the `Work` folder and the build-out of `31 - Claude Cowork` | **Done** |
| A2 | Build reusable persona primers for four finance paragons (Burry, Soros, Griffin, Druckenmiller) via subagents and the step-ladder, **so they can be fed forward-thinker input and map third-derivative impact in industry** | **Built and validated once** (panel pass). **STANDING CAPABILITY — see §0.1. Currently idle.** |
| A3 | Map the "third derivative" concept itself; find its real names and more cases; document it | **Done** — concept map, 24-case library |
| A4 | Report it all McKinsey-style, in clickable HTML | **Done** — `Report/` |
| A5 | Fold the collateral-multiplier project in; it is "all part of the same coin" | **Done** — `Where_The_Two_Workstreams_Meet.md` |
| A6 | Widen beyond AI to **all** shadow debt currently being created | **In progress** — nine-channel map done; attribution open |
| A7 | Answer from first principles how the boom is funded when saving rates are not up, testing whether the **old masters** see more than the modern consensus | **Done** — `Funding_Identity_First_Principles.md` |
| A8 | **"How can we derive numbers"** — explicitly rated the higher-value half | **Done** — measurement handbook, build order, gap register. *Tier-1 six not yet built.* |
| A9 | Organise the workstream so it survives; specify how new agents are initialised | **Done** — this file, `CORRECTIONS.md`, `CALENDAR.tsv`, `bin/check.sh`, role read-table |
| A10 | Dig into Singh; explain KVJ | **In flight** / KVJ done (resolved negative, C-018) |
| A11 | Produce serious insights fit for **an initial high-value Substack post** | **Open — this is the OUTPUT, downstream of A12. Reclassified 22 Aug (C-041); it was recorded as "the output target", which was read as the goal.** |
| A12 | **Comprehensively understand the nonbank–bank nexus** — all shadow-banking collateral and money-creation mechanisms, on the Pozsar–Singh frame in which collateral does the work of base money | **The goal from 22 Aug to 11 Sep; now channels (b) and (c) of A13.** Open. Collateral leg covered (negatively); money leg BUILT (N2a, N2b); the interlock (N4) open |
| A13 | **Understand what is driving asset prices higher and where the money is coming from** — the AI build-out and the IPO boom included — across direct money creation, shadow banking, the collateral channel, and market-structure flows such as the passive bid and ETF creation (Michael Green) | **THE ULTIMATE GOAL since 11 Sep (E-003). Open. See §0.0.** Re-planned 11 Sep (§5) on the channel map and the Green corpus dossier; any further Green material from the principal feeds item D-G |
| A14 | **Summarise the goal into one clear mission statement that is the standing goal**, rather than separate thoughts (E-015) | **Done**: the mission above. The principal confirmed the wording on 26 Sep (E-016) |

### 0.1 The standing capability that is currently idle

A2 was not a one-off deliverable. The personas exist **to be run**: fed forward-thinker input,
and asked to map where third-derivative impact is forming. They have been run once, on
40 forward-thinker theses, producing four different *signs* on the same question and six live
disagreements with named resolution dates (`Analysis/`).

**They have not been run on any of the shadow-debt, funding-identity or collateral material.**
That is the most obvious unexploited asset in the project. Before the essay is written, the
four lenses should be run over the funding identity and the money-like stack — a Burry-lens
read of the FSR Table 4.1 reconciliation failure, or a Griffin-lens read of who is paid to
absorb the basis trade, would very likely surface something the generic passes did not.

---

## 1. What we are trying to establish

### 1.0 The frame — read this before the rest of §1

**Since 11 Sep (E-003) the nexus is channels (b) and (c) of a wider goal (§0.0)**; this section frames
those two channels only — the others have no §1 framing yet. Pozsar and Singh's mechanism has two
legs, and *the nexus is that the same entities sit on both*:

| Leg | What it is | Our coverage |
|---|---|---|
| **Money** | Asset managers and institutional cash pools are the dominant source of demand for **non-M2 money** — the money-like claims that never enter M1–M3 | **BUILT and joined 15 Sep (N4).** Measured as the offshore dollar leg (N2a) and `z_k` (N2b; §2 S-N2b). 2024 private-repo growth was the ON RRP handoff, not new cash (C-085). `2026-09-15-N4-Scale-Timing-Bound.md` |
| **Collateral** | The same asset managers are the source collateral **"mines"**; banks fund themselves by **re-using pledged collateral mined from them** | **Covered, negatively.** Reuse flat, multiplier −36% from 2023 peak, "permissive condition, not proximate source" *(21 Aug summary, not re-verified since D10 and N3v4 measured the leg; current state in §2 S-N3 and `2026-08-30-D10-Reuse-On-The-Measured-Chain.md`, `2026-08-31-N3v4-Singh-Reconciliation.md`)* |
| **The interlock** | These are not two mechanisms. The nonbank supplies the funding *and* the collateral; the bank supplies the money-like claim *and* consumes the collateral | **RESULT 15 Sep (N4), mixed on 2024.** Both legs moved (wholesale share up, source collateral up, velocity not up). The 2024 expansion of measured private repo was the RRP handoff; the dated collateral-stock step is 2026. No funded-share percentage (C-085). `2026-09-15-N4-Scale-Timing-Bound.md` |

**Their 2011 numbers, for calibration:** collateral mined from asset managers **$3.3trn
(YE2007)** and **$2.4trn (YE2010)** — split $1.6/$1.3trn hedge funds, $1.7/$1.1trn real money —
which took their estimate of US shadow banking to **up to $25trn (YE2007)** and **$18trn
(YE2010)**, above the then-standard estimates.

> **The most important structural finding of the 22 Aug goal correction.** That $3.3trn
> *is the denominator of Singh's velocity ratio* — the one our channel map reconstructed and
> flagged in its own words as *"the weak link"* because it "has to be estimated separately".
> We built the numerator to five significant figures (US-six source collateral $6,907bn FY2025)
> and left the denominator estimated. **The denominator is the nonbank side of the nexus.** We
> have been computing a ratio whose denominator is the actual object of the research, and
> recording it as a data-quality problem.

**Where the interlock is hiding in our own corpus:** the channel map is nine silos, each asked
*"is it money creation?"* and given a verdict. The interlock appears only in each channel's
**"Double-counting risk"** section — i.e. as a nuisance to net out. Those sections are
unharvested findings.

> **Amended later the same day, after reading Pozsar 2014 (C-042).** The first version of this
> paragraph said a security collateralising three channels at once *"is not double-counting — it
> is the phenomenon."* **Half right, stated as wholly right.** It depends entirely on what is
> being measured: for **reuse, velocity, chain length** (Singh's object) the repetition *is* the
> phenomenon and netting destroys it; for the **stock of money claims** (Pozsar's object) the
> repetition is precisely the inflation he nets out by construction. **Net for stocks, never for
> velocity, and never report one number as serving both.** See
> `2026-08-22-Nexus-Primary-Sources.md` §5.

**What is below in §1 is one sub-investigation within this frame**, not the frame itself: the
2023–26 capex-and-valuation episode, run hard as a worked case. Its conclusions stand. Its
*scope* is one episode, and the negative results in it are results about that episode, not
about the nexus.

---

### 1.1 The 2023–26 episode — the worked case

> **⚠ RESTATED 22 AUGUST 2026 AFTER EXTERNAL REVIEW (C-030). The original framing was not a
> hard question answered — it was a badly posed one, and it has been withdrawn.**

**The question we started with, and why it fails.** *A boom is being funded while the
household saving rate falls — where does the money come from?* There is no puzzle here.
Falling household saving is **how corporate internal funds are produced**: in the Kalecki
identity this project has carried since its first round, household saving enters with a
**minus sign**. And the statistic was wrong anyway — the household *rate* fell while **gross
private saving rose from $4,815bn (2019) to $6,384bn (2025)**, up ~$1.57trn ⚠ **[C-047: this pair is CONTESTED — a second reviewer gives $5,066bn → $6,153bn from BEA Table 5.1 line 20; neither verified by us; the kill rests on the *rise*, which both show]**. Two sides of an
identity, read as a tension.

**The thesis is narrower than it was, but I over-conceded it on 22 Aug and it is partly
reinstated.** A second external review found that I extended a correct kill beyond its reach:
*flow equilibrium does not imply stock robustness.* That US corporates fund 100% of capex from
internal funds says nothing about whether ~$180trn of household wealth is robust to an attempt
to realise it. Grok killed the **funding** question, correctly. I wrongly treated that as
killing the **fragility** question too, which is a separate object.

**Two residuals survive the accounting objection, and the second is the strong one.**

1. *Inelastic-market liquidity.* Market capitalisation is a marginal price times an
   inframarginal stock. An attempt to realise $31.4trn of holding gains does not meet a saving
   shortage — it meets price inelasticity. **Cite with the C-026 caveat**: the $1-to-$5
   multiplier is one paper, aggregate-only, and there is still no separate symmetry result.

2. *The reflexive profit loop* — and note where it comes from. In the same Kalecki identity
   that killed the funding question, corporate profits depend mechanically on investment and
   on the fiscal deficit. **So the capex that validates the multiple is funded by the profits
   that the capex itself creates.** A pause in capex, or a fiscal consolidation, cuts profits
   economy-wide without anyone selling anything. The trigger need not be a redemption.
   *The identity that killed one claim supports the other; that is not a reversal, it is the
   same accounting read correctly in both directions.*

**What is dead and stays dead:** the funding puzzle, and any framing in which the fragility is
a *hidden money-creation* story. **What is alive:** an operating-leverage and reflexivity
story, in which the exposure is contractual rather than monetary.

**THE ESSAY FRAMING, as at 22 Aug 2026.** Second review's verdict, which I accept: do not
publish a defensive negative result, and do not hang the argument on the $86bn guarantee stack.
Three pillars —
*(i) The flow reality as proof of mechanism.* Macro aggregates show no capex bubble precisely
because corporates funded it internally; 72.1% of internal funds is depreciation, and ~90% of
the gross-investment increase was absorbed by depreciation on short-lived silicon.
*(ii) The $1,122.9bn off-balance-sheet lease stack* — disclosed in prose by 6 of 6 filers,
XBRL-tagged by none, which is the mechanical cause of the ghost figures.
*(iii) Credit-rating arbitrage as the real fragility* — hyperscalers renting AA/AAA covenants
to unrated developers, a bare lease earning Baa2 with zero parent debt recognition.
**The vulnerability is an operating-leverage trap, not a banking run:** if monetisation lags,
the commitments convert flexible cost structures into rigid, bond-like overheads.

**What the question becomes.** The accounting is settled and boring. What is neither settled
nor boring is the **guarantee layer**: an unpledged investment-grade balance sheet doing
collateral work that appears in no balance sheet, no credit aggregate and no flow-of-funds
line, because a contingent guarantee is not a financial instrument until it is drawn (S10).
**Is the AI capex cycle underwritten by a stock of contingent obligations nobody has summed —
and can it be summed?** Meta has already printed the template: the residual-value-guarantee
sentence plus **$45.99bn of maximum VIE exposure**, both in the filings, both confirmed by
external review.

**THE CHARGE IS NOW PARTLY ANSWERED (22 Aug 2026).** *Quantum: yes* — the stack is measurable
and measured, 6 of 6 filers determinate, nothing retreats to the unmeasurable on size. *Value:
only at 9.5% coverage* — Alphabet discloses $43.785bn of data-centre payment backstops (from
**$0 at 31 Dec 2024**, via $16.94bn at 31 Dec 2025) and names no counterparty; only **$8.183bn**
of Google-backstopped project debt is traceable on EDGAR, because ~90% of the beneficiaries are
not SEC filers. *And the price is disclosed only by the party paying it*: TeraWulf $515.5m plus
Cipher $544.5m = **$1.060bn** of penny-warrant consideration to Google against $4.933bn of
backstopped debt (21.5% of principal), while the guarantor records approximately nil on both
sides of its own books. **Caveat: those are two instances of one counterparty's standard terms,
not two independent price discoveries**, and Hut 8 has the identical backstop and discloses no
consideration at all.

**What the beneficiaries are actually buying.** Not basis points — Cipher paid $544.5m for a
backstop worth ~$87m of interest over the note life, **six times the coupon saving**. They are
buying *the existence of the financing*. That is the one place in this project where the
mechanism is measured rather than asserted.

**The residual charge.** External review put it directly:
are we *retreating to the unmeasurable because the measurable did not cooperate?* That charge
**stands** until a pass sums the 10-K and 10-Q footnotes across the named issuers. Only after
that number exists — or is shown not to exist — may the argument move on to securities-based
lending, NAV loans and internalised synthetic prime. **Measure the disclosed thing first.**

**A SCOPE CORRECTION THE ESSAY MUST CARRY (21 Aug 2026).** The premise "financial assets
inflate while goods prices do not" is **false for 2021–2026**: US CPI peaked at 9.1% in June
2022 and core goods are +16.2% since Dec-2019 against roughly flat 1995–2019. The puzzle is
real for **2009–2019** — where the collateral circuit ran *backwards*, pledged collateral −39%
and velocity −40% while the S&P rose 52% — and arguably for 2023–2026. **Date the explanandum,
or a critic kills the piece in the first paragraph.**

**The sub-question now in play.** Does a *financial-circuit* mechanism — credit and collateral
that circulate among financial claims without entering goods markets — explain asset-price
inflation without goods-price inflation?

**Where the illusion question currently stands.** Formalised as a ten-link chain in
`Funding_Identity_First_Principles.md` §4, with each link marked established / contested /
inference. The operator's sentence was made testable as: *conditional on X% of the relevant
market capitalisation pledged at haircut H, a Y% price decline forces Z dollars of sales into
a market of elasticity E, producing a further decline of Z/E.* **The load-bearing unknown is
X** — what fraction of market cap has actually been pledged.

> ⚠ **C-024 — UNRESOLVED. The margin-debt ratio below is one of THREE conflicting figures for
> the same quantity** (0.90%, 1.756%, 1.84%), produced by three passes of this project, all
> claiming FINRA margin debt ÷ Z.1 NCBEILQ027S for 2026Q1, and disagreeing on the *sign of the
> conclusion*. Name the denominator and recompute once before using it. What is NOT in dispute:
> 12-month margin-debt growth hit **+53.7% into May 2026**, a top-ten expansion in a 355-month
> record whose other members are all bubble peaks — and it turned in July.

**X IS NOW PARTLY ANSWERED, AND THE ANSWER IS DEFLATING (21 Aug 2026, C-021).** Identified
credit against securities — FINRA margin debt plus H.8 "loans for purchasing or carrying
securities" — as a share of Z.1 nonfinancial corporate equity market value: **5.241% (2015Q4)
→ 4.544% (2019Q2) → 3.534% (2021Q4) → 3.495% (2026Q1)**, ranking **36th of 45 quarters**.
Margin debt alone sits at the **median of 117 quarters since 1997**, below both June 2007
(2.348%) and March 2000 (1.844%). The pledged fraction is *near the bottom of its own range*,
and the +38.6% y/y margin-debt growth is catching up, not leading — the ratio *fell* from
1.677% (2021Q4) to 1.325% (2024Q3) straight through the 2023–24 rally.

**What this does to the animating question.** The fragility cannot be a
*leverage-against-listed-equities* story on the identified data. If the wealth is fragile, the
fragility is elsewhere — and the remaining candidates are the genuinely dark ones:
securities-based lending, NAV loans against model-marked private assets, portfolio margin, and
internalised synthetic prime. **That is where the operator's own desk sees more than public
data does, and it is now the sharpest place to look.**

**Grok external review, 22 Aug 2026 (`2026-08-22-Grok-External-Review.md`).** The first
objection a cold-reading economist makes is not the pledged-fraction result. It is that
falling household saving is not a funding puzzle: in Kalecki–Levy and in BEA Table 5.1 it is
a source of corporate internal funds. Gross private saving rose 2019–25. The essay premise
still opens as if S4 had not been written. On the animating sentence itself the review's
verdict is that **"the wealth is not real and will not survive being tested" is not
supportable as stated.** Holding gains are how Z.1 measures wealth; "if a large fraction
were sold, prices would fall" is Gabaix–Koijen and was true in 2019. Identified leverage
against listed equity is a negative result and should remain one. Retreating from that
negative to SBL / NAV loans / synthetic prime *without first summing the 10-K footnote
stack that is public* (Meta VIE max exposure $45.99bn at 31 Mar 2026) is the unmeasurable
retreat the review was asked to name. The defendable sentence is narrower: most of the
recent net-worth rise is revaluation; identified listed-equity leverage is not the 2000/2007
story; the new credit-like object is rented IG creditworthiness in lease, offtake and
RVG footnotes; whether that object is large enough to be the test is a summing exercise
that has not been done.

**Output target (set 21 Aug 2026): a publishable essay.** Not an internal memo. That raises
the bar on two things specifically — every load-bearing number must be independently
checkable by a hostile reader, and every claim must survive a competent economist's first
objection. Findings that only work if the reader is friendly do not ship.

---

## 2. What is settled

Ordered by how much weight the argument puts on it. Confidence is mine, not an agent's.

| # | Finding | Confidence | Evidence |
|---|---|---|---|
| S1 | **The capex flow needs no monetary explanation.** US non-financial corporates fund 100% of capex from internal funds and lend the surplus onward; financing gap negative four of five recent quarters | **High** — identity re-derived from Z.1 S11.1.t, closes to the dollar every quarter 2019Q4–2026Q1 | `Funding_Identity_First_Principles.md` §1 |
| S2 | **72% of internal funds is depreciation** (2026Q1 SAAR: CFC $2,459.8bn / internal funds $3,410.0bn). ~90% of the rise in gross capex **2023Q4→2026Q1** was absorbed by faster depreciation. Net fixed investment rose 5.8% on that window (gross +13.1%). C-029: do not ship the percentages without the two dates | **High** — own computation from Z.1 | ibid. §2.1 |
| S3 | **The wealth is revaluation, not saving.** 80.2% of the $39.16trn rise in US household net worth 2023–25 was net holding gains (**Z.1 11 Jun 2026 vintage**; the 19 Mar 2026 HTML revises to $40.36trn / $32.66trn / 80.9% — same direction, ~$1.2trn vintage gap). Since 1995: saving + retained earnings $36.6trn against a $152.9trn net-worth rise (24%) — Grok pass did not re-sum the 30-year series | **High** on 2023–25 share; 1995–onwards un-reverified this session | ibid. §3(d) |
| S4 | **The saving composition changed, not the level.** Household saving rate 6.2% (Dec-19) → 2.7% (Jun-26). **C-028: 2.7% is not "lowest since 2005"** (June 2022 was 2.2%; July 2005 was 1.4%). BEA gross private saving rose $4,815bn (2019) → $6,384bn (2025) **[C-047: CONTESTED — a second reviewer gives $5,066bn → $6,153bn from BEA Table 5.1 line 20; neither verified by us]**; domestic business saving $3,023bn → $4,423bn (+46% on that series). The "+68%" corporate-gross-saving figure was not reproduced on the BEA annual in the Grok pass | **High** on the rate; **CONTESTED (C-047), not High,** on the $4,815bn→$6,384bn gross-private-saving pair specifically (both reviewers agree it rose); composition-not-level otherwise holds; +68% unverified against BEA annual | ibid. §3, Number 2 |
| S5 | **Bank lending to non-banks is the fastest-growing credit aggregate** — $546bn (Jul-19) → $2,006bn (Jul-26), +19.75% y/y vs total bank credit +6.21%. Excluded from the BIS credit-to-GDP gap. **It is private-credit and warehouse funding, NOT credit to buy securities — margin loans are excluded by the Fed's own footnote (C-020), and 28.3% of the rise is reclassification** | **Medium-high**, narrowed — FRED H.8 line 26 | `Shadow_Debt_Measurement_Handbook.md` §3 |
| S6 | **The marginal offshore dollar goes to non-bank financials, not the real economy.** Q1 2026: USD cross-border credit +$793bn; +$651bn of the +$1.1trn to non-banks went to NBFIs in the US, UK, Cayman, Japan | **High** — BIS LBS | `2026-08-21-Offshore-Dollar-And-Money-Like.md` |
| S7 | **Japan carries the offshore dollar funding gap.** Of a $391bn unfunded residual, Japan is 47%; Japan+China 89%. Japan-located net dollar position +$1,752bn against rest-of-world-ex-US at $947bn. BoJ FSR Apr-2026 fn16 states the yen-swap mechanism outright | **High** — BIS SDMX re-pulled in-session | ibid. |
| S8 | **A non-US bank does not need funding to *write* a dollar loan — it needs it to *keep* the loan after the borrower spends.** 41% of the expansion is a claim on a US resident | **High** — mechanically derived, four LBS cases tabulated | ibid. §1.1–1.2 |
| S10 | **The mechanism is an UNRECORDED LEASE OBLIGATION, not a guarantee** *(reframed 22 Aug after summing the filings — C-034)*. ASC 842 leases **signed but not yet commenced**, six filers, one standard, at/near 30 Jun 2026: Microsoft $329.1bn + Meta $278.99bn + Oracle $260bn + Amazon $137.2bn + Alphabet $85.2bn + NVIDIA $32.4bn = **$1,122.9bn**, versus ~$417.4bn prior-period (~2.7×, vintages span 8 months). **Disclosed by 6 of 6; XBRL-tagged by 0 of 6** — which is *why* the unsourced $662bn/$970bn ghosts could circulate. The guarantee stack is the visible minority: **$86.2bn live / $228.3bn contracted**, 6/6 determinate. At Hut 8's Beacon Point the notes are **expressly unguaranteed** and a bare lease covenant earns Baa2. Of $16.58bn of IG-covenant project debt, **$8.40bn rests on an unguaranteed lease, $8.18bn on a guarantee.** | **High on the quantum** — every figure read in a filing with an accession number. **Low on the value** — see below | `2026-08-22-Guarantee-Stack.md` |
| S9 | **Repo, not money funds, drives the money-like stack** — +19.1% y/y, 3.91pp of the +12.0%. And ~$749bn of the apparent rise is a *restatement*, not growth | **Medium-high** — Fed FSR, published-to-published comparison | ibid. |

---

**S-D1 (settled 22 Aug 2026, v1, our own pulls).** *Bill supply does not shrink private shadow
money — at least not in 2023–26, and not over 2013–25.* Jun-2023→Jul-2026: bills **+$2.52trn**;
ON RRP **−$2.03trn to $0.2bn**; MMF Treasuries **+$2.21trn**, MMF repo with the Fed **−$1.90trn**;
uninsured deposits +$1.04trn, large time deposits +$0.58trn, ABCP +$0.20trn, financial CP flat.
Issuer-side private stack $10.2trn→$12.0trn. 2013→2025: bills +$5.0trn, private stack +$5.0trn.
**H1 confirmed; Pozsar's macroprudential-bills prediction rejected on this evidence; Nagel's
rate-level account fits.** Caveats in `2026-08-22-D1-Bill-Supply-vs-Shadow-Money.md` §6 — foreign-
official netting not done, uninsured is total not demand, dealer repo by collateral ends 2021.
*Load-bearing; re-pull quarterly.* **Amended 23 Aug: the Fed's SOMA bill holdings rose $304bn YTD 2026 (reserve management purchases) — the 2023–25 window is clean, the 2026 window must net SOMA purchases; and ABCP's growth is equity-margin conduit funding (FT/JPM, partly verified).**

**S-D2 (settled 22 Aug 2026, v1, our own pulls).** *The AI debt stack is long-money funded; the
money-like leg barely touches it; bank credit is the one literal money-creation channel.* Z.1
2026Q1: MMFs hold **$22bn of $17.2trn** corporate & foreign bonds (0.13%); life insurers $3.9trn,
mutual funds $2.6trn, pensions $1.6trn, ROW $4.9trn. N-MFP3 census (Jul-2026, every filing naming
an AI issuer): **$0.26bn direct CP, ~$4.0bn as repo collateral** — CoreWeave's 2032 convert sits as
collateral in a BlackRock money fund's repo. Beignet/Hyperion $27bn: **1,497 NPORT-P filings name
it; **AMENDED 23 Aug (C-053): the full SEC bulk N-PORT census shows registered funds hold $9.81bn (36%) — PIMCO Funds alone $6.23bn — so the daily-redeemable share is a material minority, not small; the earlier "$0.70bn / 96% in SMAs" was a sampling artefact.** Large-bank
AI-adjacent C&I **~$450bn committed / ~$150bn outstanding** (Chicago Fed, late 2025; industry exposure, ~$250bn of it already in 2015 — C-115) vs ~$1.2trn
AI-company debt (JPMorgan analysts' estimate, relayed). **The six AI capex firms hold ~$630bn of liquid assets (+$240bn in two years) —
they are Pozsar's category-2 cash pools.** Fragility is duration/operating leverage, not a run —
the essay framing reached independently from the holder side. `2026-08-22-D2-Who-Holds-The-AI-Paper.md`.

**S-D6 (settled 29 Aug 2026, from statute + TBAC/FSOC/OFR primary docs + live on-chain data; C-062 for the
return's defects).** *Stablecoins ARE a fifth cash-pool category — but the pool is the ISSUER, not the coin.*
The GENIUS Act (PL 119-27, verified) writes Pozsar's "do not lose" mandate into law: reserves restricted to
≤93-day Treasuries, overnight repo, government MMFs, Fed balances and insured deposits; **no interest or yield
to holders**; monthly published reserve composition. Holders are money-users (par redemption institutional-only;
retail bears depeg risk — USDC 0.87 in Mar-23). **Engine 5 of N2c closed: outstanding $130bn (Dec-23) →
$207bn (Dec-24) → $308bn (Dec-25) → $309bn (Aug-26) — flows +76/+101/+2bn: real bill demand (~4–5% of net
issuance in 2024–25, TBAC ">$120bn" held; OFR: $92bn bills + $29bn repo at Jun-24) that STALLED in 2026,
completing the pattern of every private engine plateauing the year the Fed returned.** No official aggregate
exists (rules still proposed-only; OFR AR-2025 has zero stablecoin mentions); the only continuous series is
on-chain (`bin/pull_series.py --only llama`). TBAC scenario on record: ~$1.0tn issuer bill holdings 2028E
(~$900bn incremental) — one official scenario, not a range. Yield-bearing synthetic dollars (Ethena-type) are
a collateral-leg object — flagged, not folded. `2026-08-29-D6-Stablecoins-Fifth-Cash-Pool.md`.

**S-N2b (settled 31 Aug 2026, v2 — three adversarial lenses; v1's headline struck, C-070).** *`z_k`, the wholesale non-M2 share of nonbank funding of the US banking/dealer system, more than doubled and has plateaued — it did not stay flat.* v1's headline — the Fed-inclusive "no change" reading (wording in CORRECTIONS.md C-070, not repeated here) — was **STRUCK (C-070)**: an endpoint artefact (the Fed-inclusive ratio ranges over ~4.7pp across nine dates; the two chosen dates both happened to sit at 19.05%) plus a category error (the Fed is not a bank, so it cannot be a `z_k` lender). **The corrected private measure: 9.09% (2021-12) → 19.45% (2026-06)**, monotonic, now plateaued because the ON RRP is empty and there is nothing left to hand back. **v2's perimeter test** widens the numerator to add hedge-fund reverse repo and holds across all twelve perimeter × denominator combinations; on the strictest bank-funding denominator, H.8 deposits less large time deposits, it runs **16.42% (2021-12) → 29.22% (2026-03)**. **Passed three adversarial lenses** (endpoint artefact, denominator, double-count) and **was carried by N4 on 15 Sep** (`2026-09-15-N4-Scale-Timing-Bound.md`). Caveats: the level is perimeter-sensitive by about a point (Form PF's global hedge-fund population vs. the US-only census moves 2025-12 from 23.07% to 22.19%), and `W` is a floor — money-fund bank commercial paper is excluded from the numerator. `2026-08-31-N2b-zk-The-Wholesale-Share.md` §§7–8.

**S-N4 (settled 15 Sep 2026 — supervisor arithmetic on reviewed series; C-085).** *Wholesale non-M2 funding of banks/dealers expanded as a share, mostly by taking back the ON RRP; that is not new cash in the compression year, and the dated collateral-stock step is the wrong year.* `z_k` (W1 over W1+M2, H.8 LTD) 9.75% (2022-12) → 15.94% (2023-12) → 17.63% (2024-12) → 19.42% (2026-06); W2 same shape, 23.07% at 2026-03. 2024 private MMF repo **+$540.6bn** against ON RRP **−$586.3bn** (net **−$45.7bn**). Handoff-adjusted ceiling **$136.2bn** vs **$1,404.9bn** 2024 household purchases of the wrapper; full window to 2026-03 **$858.6bn** vs **$3,069.4bn**. Re-use intensity 1.3–1.5 (C-061); six-bank permitted/repledged **+19.3% / +21.5%** is H1 2026. Existing wholesale stocks can still rearrange — different claim, rate did not rise. Do not convert the ceilings into a funded share. `2026-09-15-N4-Scale-Timing-Bound.md`. Path: `data/n4/`.

**S-N2c (v2, 30 Aug 2026 — v1 heavily revised after the N2cR adversarial review returned 25-for-25 verified
and broke four of five conclusions; C-063/C-064/C-065; full adjudication N2c doc §7).** *What survives:* the
absorption TABLE (Fed's own data, reproduces), the plateau observations as series, the $2.0trn NDFI stock, and
the question. *Corrected findings:* **(1)** Fed bill-buying ratio on matched endpoints: **63.6% (Dec-31→Jul)
falling to 44.4% (→26 Aug)** as August's wave was privately absorbed; ~$160bn of ~$250bn was RMP, the rest
reinvestment; Jefferson verbatim: RMPs are stance-neutral, not QE. Q1's Fed +$156bn stands as the quarter's
largest single buyer; "re-monetized" is retracted. **(2)** Bank→NDFI: **$400.8bn of 2025's +$625bn was H.8
reclassification** (five dated notes, verified line-by-line); organic ≤~$224bn — **a steady ~$100–220bn/yr
engine on a real $2.0trn stock**, 57% credit intermediaries, 24% capital-call PE, **$987bn of commitments
undrawn**. **(3)** Equities, from F51.1.t reproduced exactly: biggest net purchasers were households (the Z.1
residual, incl. domestic hedge funds) +$985/+$864bn, ETFs +$840/+$959bn, and the **rest of world +$644bn in
2025 — the under-weighted row**; corporates were net sellers as holders while retiring −$304 to −$611bn of
issuance. Buybacks are a debt-funded structural bid, not "the only buyer"; the identity does not set prices.
**(4)** The regime/causal narrative is retracted on the Fed's own FWTW statement (core accounts "not designed
to reveal" who funds whom) — the engines are accounting layers that can double-count one financed position;
the FWTW gap is itself the finding. Competing verified narrative now in the record: **IMF Fiscal Monitor —
private domestic investors absorbed ~$5trn of US public debt since 2022**; BIS — the swap-spread trade (upper
bound $631bn) drove hedge-fund Treasury growth after the basis trade stalled in early 2024. Sharpest live
questions: persistence of the foreign equity bid; what draws the $987bn of undrawn NDFI revolvers.
`2026-08-29-N2c-The-Funding-Closure.md` §7.

**S-N3 (v3, 29 Aug 2026 — v2's symmetric range overturned by the principal's first-principles challenge; C-061 addendum; N3 doc §8).** *Corrected verdict: **velocity ≈1.3–1.5**, mechanism-signed (bracket-position floor 0.73: repo borrowing alone exceeds the cash-like bucket; downward wedges ≤$0.88trn sized from FICC PQD + ISDA); Singh's 2.0 is a conflicting direct measurement with a named ~$2.5–3trn reconciliation gap — askable of the author on LinkedIn.* Superseded v2 text follows: *The collateral leg grows by MORE
SOURCE COLLATERAL, not faster re-use — and that mechanism claim survived external attack under every reading,
including the reviewer's own alternative.* Velocity itself is now stated as a **range, not a point**: Singh
(Risk.net, 12 Jan 2026 — **free**, read in full, archived; the Central Banking twin we had logged as paywalled)
says *"almost constant at around 2.0"* for a decade on his hand-collected top-20-bank data; our Form PF-bracket
reconstruction gives 1.55 at the 2013–17-fitted position and ≈2.0 at the securities-only floor — the bracket
position is **unidentified in 2026**, so **[≈1.5, ≈2.0], Singh's 2.0 primary**. Sources grew in every reading:
+76% since 2017 on Singh's own implied split; ×2.7 on our securities-only floor; ≈×3 at the fitted position.
Hedge-fund leg still brackets cleanly (Singh strictly inside Form PF Q43 bounds all five overlap years).
Singh's 2026 method statement, from the article: denominator = collateral sourced via reverse repos,
securities lending, prime brokerage and **uncleared** derivatives; perimeter **top 20 banks** (ours is US-six —
half of it). **N3b DONE 29 Aug (§7): the ISLA client-type chart read via browser — real-money set = 61% of on-loan
(pensions 21 / gov-SWF 17 / insurers 3 / CIVs 20; banks 16 excluded; undisclosed 23) → leg ≈ USD 2.7trn upper
bound (×1.8 vs Singh's 2017). Velocity band tightens to [≈1.4, ≈2.0]; open-data readings now sit below
Singh's 2.0, with exactly two unidentified quantities left: the Form PF bracket position and the dealer-share/
churn haircut. By-product: the D5 cash-reinvestment pool is sized — €1.24trn (33% of collateral received).**
Settling test: a Form PF collateral-by-counterparty split, which OFR does not publish. Review
citations 13-for-13 verified (dealer footnotes tie to our $6,907bn to the decimal; WFC $469.2bn was the
reviewer's missing sixth). `2026-08-25-N3-Singhs-Denominator-Reconciled.md` §6; C-060 terminology note stands.
**Adversarial review RETURNED and adjudicated 28 Aug — the strongest external return to date; it materially
changed the finding. Process note: run in Grok-in-Cursor against hermes-core, landed as draft PR
closeofbusiness/hermes-core#557; content retrieved from the PR branch to `_research/N3R_Velocity_Review_Return.md`;
recommended to the principal that #557 be closed unmerged.**

**S-D9 (settled 24 Aug 2026, from the six firms' own filings).** *The AI complex's cash pools are large
corporate-bond investors; whether they hold each other's paper is not publicly knowable.* Corporate debt
securities held, fair value, latest filing each: **Amazon $59.4bn, Meta $33.1bn, Alphabet $26.2bn, NVIDIA
$15.1bn, Microsoft $12.4bn, Oracle none disclosed — $146.2bn total**, against **$22bn** held by the entire US
money-fund industry (S-D2). **No filing discloses issuer names, industry breakdown or a quantified
concentration** — verified by full-text search of all six, not inferred; corporate treasuries file neither
N-PORT nor Schedule D, and much of the money runs in SMAs, so the reflexivity question has no public route at
issuer level. **The finding is a sized measurement gap, not a null.** Flagged (N5): Microsoft's $1.7bn of
**Level 3** corporate notes and bonds; **$94.1bn of restricted SpaceX shares inside Alphabet's "marketable
securities"** (~92% of its marketable equity); Oracle's all-money-market pool as a leverage tell.
`2026-08-24-D9-Does-The-AI-Complex-Fund-Itself.md`.

**S-D3 (settled 23 Aug 2026, v1, our own pulls).** *Reverse maturity transformation explains the
level of institutional cash demand and the 2013–21 trend; it does not explain 2021–26.* Z.1:
asset-management complex (mutual funds, ETFs, CEFs, pensions, life, P&C) **+66% 2013→21 vs MMFs
+71% / institutional MMFs +80%**; **+16% 2021→26Q1 vs MMFs +59% (retail +122%, institutional +37%)**.
NFC liquid assets a stable **22–24%** of NFC financial assets throughout. Holding the 2013–21
MMF/complex ratio (6.70%) gives structural MMF assets of **$5.66trn vs $8.29trn actual** at 2026Q1;
institutional excess ~$1.3trn over the post-2023 deposit-flight window. **D1 and D3 agree: the
post-2021 cash surge is rate-driven, not structural.** Pre-registered: a material rate cut should
pull MMF assets toward ~$5.7–6trn. CCP-margin and sec-lending legs unmeasured (SLATE public data
29 Mar 2027, verified). `2026-08-23-D3-Cash-Pools-vs-Asset-Management-Structure.md`.
**Amended 23 Aug pm (v1.1, §8 — OFR Hedge Fund Monitor API, Form PF aggregates, qualifying hedge
funds):** the third institutional cash holder is measured and is not a driver either — hedge-fund
**unencumbered cash ~$0.7trn** (8% of MMF assets), **+4% 2013→21, +$180bn 2021→26Q1**, ratio to
NAV *down* from 21% to 14%. What doubled is the **collateral leg**: collateral posted **$4.4trn
(YE2021) → $8.2trn (2026Q1)**, tracking secured borrowing one-for-one (repo borrowing ×2.8 to
$3.2trn; prime-brokerage ×1.6 to $3.2trn; the margin-like residual ~$1trn). **All three of Pozsar's
institutional cash holders have now been measured against the 2021–26 surge and none scales with
it; the same institutions' collateral did.** The hedge-fund end of D8's FICC pipe is thereby
measured (D10). Gemini's D3 return adjudicated (C-054): one row changed what we know (the OFR
monitor pointer), nine constructed identifiers, all dollar values destroyed in transit.
**Amended 23 Aug evening (v1.2, §9 — FIA CCP Tracker API, C-056):** CCP initial margin across 15 derivatives
CCPs **$757bn (YE2021) → $1,071bn (2026Q1), +41%** — faster than the complex (+16%), but a $314bn increment
against MMFs' $3.1trn, and ~42% of CME's held margin is Treasuries, ~44% cash. **Margin is a real second
structural driver and is an order of magnitude too small to be the surge.** Only the sec-lending leg (SLATE)
remains. `2026-08-23-Parcel-N3-Collateral-Return.md` §2.1.

## 3. What is contested, and by whom

**These are live disagreements inside our own corpus. Do not quote one side as settled.**

| # | Question | Position A | Position B | How it resolves |
|---|---|---|---|---|
| K1 | **RESOLVED — NEITHER.** Was: is the illusion monetary or a discount-rate artefact? | Prior answer: a discount-rate artefact | Rival: a financial-circuit mechanism | **Both fail.** The circuit fails on three independent observables. The discount-rate account fails **on sign**: 10y TIPS +339bp Dec-2021→Aug-2026 while equity valuation did *not* revert on any of three denominators — equity/profits +7.9%, equity/GVA flat to three decimals, Tobin's q +6.9% with 2025Q3 the highest of 304 quarters since 1945. "A discount-rate artefact, not a monetary one" becomes **"nor a discount-rate one either."** What does the work: factor-share reallocation to shareholders (Greenwald–Lettau–Ludvigson: 40.2% of the 1989–2017 real equity rise, vs 14.3% for interest rates), float retirement (−$1.90trn net equity issuance 2022Q1–2025Q4), and Gabaix–Koijen as amplifier |
| K1b | *(superseded by K1)* **Is the illusion monetary or a discount-rate artefact?** | The funding-identity synthesis concluded it is *a discount-rate artefact, not a monetary one*, and that this is the *harder* problem | S5–S6 show a large, fast-growing intra-financial credit channel that no goods-price index would ever see | **The open Singh / two-circuits pass.** This is the single most important unresolved question in the project |
| K2 | **What is collateral velocity actually doing?** | The inherited claim was "flat 2–3 years on Basel III" — **killed as unsourced, C-015** | FICC sponsored repo +150% in two years to $2.856trn; NCCBR revealed at ~$5.0trn. Reuse may have migrated into CCP netting, which no velocity metric captures | Same pass. If the measured series falls while the phenomenon grows, that is the project's most important measurement finding |
| K4 | **RESOLVED — the null fails, but not by the proposed mechanism.** Does safe-asset supply drive valuation? | Operator: the constant share is a ratio, so it is no null on quantity — and if supply drives the denominator the constancy is mechanical | Rival: wealth drives safe-asset demand | **Operator right on the inference, wrong on the mechanism (C-022, C-023).** Numerator grew **177.8×**, denominator 239.1× — anyone using GLM as a quantity null is misusing it. But "drives" needs a *unit elasticity* and the realised one is **0.946**; and rising valuation pushes the share **down**, so it breaks the constancy rather than manufacturing it. **What replaces it is stronger and publishable:** revaluation as a share of the denominator's change went **18.1%** (GLM window) → **49.2%** (2011–26) → **66.6%** (2022Q4–2025Q4). *The constancy held while the denominator behaved like a quantity and failed once it began behaving like a valuation.* |
| K4b | *(superseded)* **Does safe-asset supply drive valuation, or does wealth drive safe-asset demand?** *(raised by the operator, 21 Aug, correcting a project error — see C-017)* | **Wealth-driven demand:** investors hold a stable share of wealth in safe form, so a constant GLM ratio follows mechanically from any source of wealth growth. Safe assets are an *effect*. Closest to GLM's own reading | **Collateral-driven supply:** safe assets are the raw material for leverage — more Treasuries → more collateral → more repo → more capacity to hold risk assets → higher valuations. Safe assets are a *cause*. Geanakoplos's leverage cycle in GLM's accounting | **In flight.** The two predict the *same* correlation and *opposite* causality. Requires an identification strategy — candidates are debt-ceiling episodes, wartime finance, the 2023 bill deluge, and QE (which removes collateral while adding reserves). Without one there is no publishable claim |
| K5 | **Was the KVJ sign-inversion claim publishable?** | We asserted it was a novel finding | It is KVJ's own Predictions 3 and 4, resting on a category error and a debt-ceiling-trough base effect | **RESOLVED — NO. C-018.** Do not publish in any form. A measurement critique survives: *a net measure that nets to zero the most run-prone part of the money-like stack cannot be the right summary statistic for fragility.* Makes no claim about any coefficient's sign |
| K3 | **Is the offshore dollar expansion money creation?** | Original framing: "unambiguously money creation, +$1.90trn" — **killed, C-014** | Three numbers on three perimeters: $2,040bn gross, $1,650bn liability-matched, $754bn owed to an identified non-bank | Cannot be resolved further: `L_CP_SECTOR` is suppressed on the foreign-currency cut, so genuine creation and interbank recycling have an identical signature |
| K6 | **Does the essay still open on a category error?** Raised by Grok external review, 22 Aug 2026 | The Grok prompt, and therefore the essay premise, still treats falling household saving as a funding mystery for the capex boom | S4 already says composition-not-level; Kalecki in `Funding_Identity_First_Principles.md` already dissolves it; BEA 5.1 shows gross private saving *rising* 2019–25 | **Not resolved until the opening sentence is rewritten.** Measure BEA Table 5.1 (household vs business vs government) and put the identity in paragraph one, or a cold-reading economist stops. `2026-08-22-Grok-External-Review.md` §1 |

---

## 4. The load-bearing assumptions

**If one of these breaks, everything in the right-hand column dies with it.** This is the
dependency map — check it before celebrating a new finding.

| Assumption | Status | What dies if it breaks |
|---|---|---|
| Z.1 sector accounts capture AI-related capex where it actually happens | **Strained.** SPV/JV capex classified to a financial sector never enters NFC capex at all. Magnitude unknown; bias direction known (understates external funding) | S1, S2 — the entire "no funding gap" conclusion |
| The flow-of-funds discrepancy floor is ~$0.7trn/yr | Holding | Any claimed channel smaller than that is unidentifiable. Disqualifies most proposed mechanisms |
| Depreciation schedules approximate economic life | **Strained.** 4–6 year stated lives against an annual product cadence; ~$1trn swing in cumulative 2026–31 depreciation between a 5-year and 3-year life | S2, and the "boom is barely visible in net terms" claim |
| BIS LBS suppressions do not hide a large offsetting flow | Holding, with a stated floor: $690bn (3.9%) unallocated by location; Singapore, Malaysia, Indonesia, Saudi all NaN | S6, S7 |
| The leak from asset purchases into goods demand is small | **QUANTIFIED 20 Sep (W1, C-094).** Ceiling is the $3,643.7bn seller-side flow, not the $6,886.8bn of buying; the mutual-fund leg is a wrapper rotation covered 122% by ETF buying; the contractual pension+insurance channel is $938.4bn. A CEILING, not a measured leak — rebalancing and MPC untested | **Nothing live.** K1 was already resolved as NEITHER in §3; this row had not caught up |

---

## 5. Open questions, ranked by value

*Reconciled 22 Aug 2026. Dependencies are stated, not implied by ordering. Every deferred
item has a date or a trigger; an item with neither is a decision nobody has made yet.*

> **EVERY ITEM IN §5 MUST NAME THE GOAL ROW IT SERVES.** `A12` = the nexus, the goal.
> `A11` = the Substack outcome, downstream. `A2` = the standing persona capability. **`TANGENT`**
> = serves none of them, which is *allowed and sometimes valuable* — but it must be labelled, and
> it lives in tier T below, never inside tier N or O. An unlabelled item is how the essay quietly
> became the goal: work accumulates, nobody re-asks what it is for, and the pile becomes the
> priority. **If you add an item and cannot name its row, that is the finding — say so.**
>
> **RE-RANKED 22 Aug 2026 after the goal correction (C-041).** The previous ordering ranked by
> *what the essay needed*. Under the actual goal (§0.0) that is the wrong criterion, and the
> items that serve the goal directly were **not on the list at all**. They are now tier N, above
> everything. The former "blocking the essay" tier is real work but it is **outcome-side**, and
> it is ranked accordingly. Nothing was deleted; things moved.

### Closed this pass, with evidence

- **0b — size the guarantee stack. DONE.** `2026-08-22-Guarantee-Stack.md`; nine filers, 43
  accession references. $86.2bn live / $228.3bn contracted, 6 of 6 determinate. **It also
  answered the retreat charge (quantum yes, value at 9.5% coverage) and reframed S10 — the
  guarantee is the minority case; the $1,122.9bn lease stack is 13× larger.**
- **3 — replace the velocity claim. DONE.** C-015 amended: the claim was traceable to Singh on
  Mercatus *Macro Musings*, 30 May 2022, and was mis-dated rather than unsourced. Superseded by
  his January 2026 statement. *Residual: the "velocity is X" phrasing is still live in three
  documents and must become "Singh estimates" — folded into item 7 below.*

### RANKED OPEN WORK (re-set 3 Sep housekeeping). Dependencies explicit; every item has a trigger

```ranked
RE-PLANNED 11 Sep under E-003 (THE_ASK.md; the charter is section 0.0).

STATE OF THE ARGUMENT, 17 Sep — **DO NOT READ IT FROM HERE. Read `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md`,
which is the single authoritative statement of what we believe. It deliberately restates no numbers — each claim points at its findings doc, because copying figures into a second place is what caused C-081, C-089 and C-092.**
This block used to restate the argument and went stale within a day; it is now a pointer by design.

Three things a cold reader needs before anything else:
  * THE PRICE SIDE HOLDS. Earnings did most of the work. That survived its disconfirming test (E2).
  * THE MONEY SIDE: issuance rebuilt 15 Sep (ETF1, C-081/C-083). Z.1 counts ETF SHARES as corporate equity.
    Operating companies retired over the window; the aggregate's growth is ETF share creation, three-tenths
    of it bond ETFs. The household plug was recategorized by tax status, not sized by legal entity
    (LIT1, C-084). N4 (C-085): 2024 wholesale-repo growth was the ON RRP handoff, not new cash;
    the dated collateral-stock step is H1 2026. P4 (C-086): free-data Russell RD first stage fails.
    Read `2026-09-15-ETF1-Identity-Net-Of-ETF.md`,
    `2026-09-15-LIT1-Residual-Literature.md`, `2026-09-15-N4-Scale-Timing-Bound.md` and
    `2026-09-15-P4-Russell-Elasticity-Pilot.md`, not this block.
  * EVERY CORRECTION THIS FORTNIGHT CAME FROM OUTSIDE. C-077, C-078, C-080 and C-081 were all caught by
    adversarial review, never by internal reading. Internal consistency is not evidence here. Run
    `bin/check.sh --latest` before trusting any document.

The standard of evidence is E-005: a rough understanding with bands, not proof to the last cent. We never pay
for data. Neither relaxes verification against source.

THIS FENCE IS THE CURRENT WAVE ONLY — AN EMPTY FENCE DOES NOT MEAN THE PROGRAMME IS DONE (added 20 Sep,
after the supervisor read the fence, found items 1-8 closed, and told the principal there was "no open work").
Open work also sits in: Tier N (N2c engine 5; N3's sec-lending and pre-Form-PF legs); the flagged D-series
directions below, of which D5 and D7 were never started; the numbered lists "Next" (items 2-7) and "Standing"
(items 9-11; item 8, the leak objection, was answered 20 Sep - C-094); section 7's reviewing-agent checks; and
CALENDAR.tsv, which carries 39 rows not yet done. Check all of those before reporting the list exhausted.

OPEN-ITEM INVENTORY — complete, enumerated 20 Sep at the principal's request, and RANKED BY HIM.
Every item below already lives in a tier section of this file; this is an INDEX, not a second copy.
Do not restate findings here. Status and detail stay in the home section named on each line.

  SEQUENCING — what gates what, and what DECAYS (24 Sep; items 1 and 3 updated 25 Sep). Dates live in CALENDAR.tsv, not here.
   1  QE sentiment RUN 1 ....... 25 Sep, GROK. DECAYS TO IMPOSSIBLE: a read of expectations BEFORE the
                                 quarter-end turn. Miss it and run 2 (1 Oct) has nothing to score against.
                                 24 Sep attempt BLOCKED (X sign-in wall in Cursor, C-121): its calls are placeholders.
                                 25 Sep: switched to public web sources (E-015). DONE 25 Sep: four SIMILAR calls, LOW weight
                                 (1 usable item of 62); supervisor-checked 26 Sep. RUN 2 on 1 Oct; the design decision on 2 Oct.
   2  Goal read-back ........... 25 Sep, THE PRINCIPAL'S. The only check that has ever caught goal
                                 corruption; an agent restating the goal cannot detect it (E-000).
   3  Panel asks (C-097, d3) ... DONE 24 Sep. Grok landed data/w3_tax/firm_tax_panel.csv and data/eps_split/panel/;
                                 the supervisor re-derived both exactly (W3: 412 firms, ETR 27.351% and 19.615%;
                                 EPS split: 366 firms reproduce the published bounds, a ceiling of ~7-13% of the price
                                 gain, C-101). The optional Z.1 debt pulls did not land.
   4  30 Sep quarter-end ....... point-in-time observations that cannot be made up afterwards; they also
                                 score RUN 1.
   5  Revolver-drawdown parcel . 1 Oct. Its gate was "only after the synthesis names the fragility question
                                 precisely". W2 (23 Sep) now names it: ~$300bn of committed-but-undrawn bank
                                 lines to AI-adjacent industries, plus N2c §7's undrawn NDFI commitments. The gate
                                 is arguably met — routing is the principal's call.
                                 APPROVED 25 Sep (E-015). Brief ready 26 Sep: Parcel_RV1_Revolver_Drawdown_For_Grok_Cursor.md.
   6  10 Oct N-MFP3 census ..... the trigger check for item 7 (D4). Nothing else waits on it.
  DONE and off this list: W1 (20 Sep), W3 (21 Sep), W2 (23 Sep) — see the wave block below.

  THE PRINCIPAL'S CURRENT WAVE (ranked by him, 20 Sep) — these three run now:
   W1  Meet the leak objection ........ DONE 20 Sep -> 2026-09-20-W1-The-Leak-Objection.md (C-094)
   W2  Is the AI complex's debt funded by money-like ... DONE 23 Sep -> 2026-09-22-W2-AI-Paper-Composition.md
       claims or by long money?                           (Grok drafted; supervisor revised and adjudicated — E-008, C-115)
   W3  Earnings quality: THE 2017 TAX ACT ............ DONE 21 Sep (Grok) -> 2026-09-21-W3-Tax-Decomposition.md
       (+ revenue-recognition timing)                  Findings live THERE and in the ANSWER §6 item 1. NOT restated here:
                                                       this is an index, and restating is what caused C-081/C-089/C-092.
                                                       Supervisor review 21 Sep: every scalar reproduces; Task 2's verdict
                                                       rescoped (C-096 — a tighter ceiling, not an estimate); the firm
                                                       panel and raw Z.1 pulls did not land (C-097).
                                                       Spec: _research/2026-09-20-W3-Tax-Decomposition-Spec.md (C-095).

   D5   Securities lenders' cash-collateral reinvestment ... flagged directions; "sharpest test of the nexus"
   D7a  Goldsmith layering ratio (Z.1) ..................... flagged directions
   D7b  From-whom-to-whom pilot on repo alone .............. flagged directions
   --   Derivatives / options as a market-structure flow ... NO home section yet; goal names this channel
   --   Who funds the ~89% private share of record issuance  S1 / I1b raise it; nobody has taken it
   --   The persona capability, idle since 22 Aug .......... section 0.1; pending a decision (Tier A2)
   --   The missing-channel question .................... flagged directions, after N5; asked twice, no answer

  STANDING, WITH TRIGGERS
   9    Decompose bank lending to NBFIs ($2,006bn) ........ "Standing" item 9; Call Report RC-C
   10   Test the SPV/JV capex hole ........................ "Standing" item 10; largest known bias in S1
   11   Build the Tier-1 six .............................. "Standing" item 11
   D4   Re-cut the channel map dealer-first ............... item 7 below; trigger is the 10 Oct census

  OPEN LEGS ON FINISHED WORK
   D1 foreign-official TIC netting / uninsured split / FR 2004 post-2021 ...... D1 block
   D2 full N-PORT census / insurer Schedule D / hyperscaler cash .............. D2 block
   D3 sec-lending leg (data starts Mar 2027) / fund-buffer leg ................ D3 block
   D8 $13.3bn ABCP unattributed across five issuers .......................... D8 block
   D10 second leg ............................................................ D10 block
   N2c engine 5 · N3/Singh sec-lending leg and pre-Form-PF years ............. Tier N
   Holder-side split of the household residual (C-084) ....................... no free route found

  NUMBERED ITEMS FROM THE EARLIER PLAN (2-7)
   2 essay opening vs BEA 5.1 (outcome-side) · 3 verify the five numbers Grok could not ·
   4 name the q series (C-036) · 5 repo-attribution instrument (C-038) · 6 GLL out of sample (C-037) ·
   7 triage the unpromoted caveats (C-040) — only 3 of 17 done

  KNOWN DEFECTS — found in housekeeping 21 Sep, NOT yet fixed, listed so they are not rediscovered
   d1  Four docs cite scratchpad deliverables that are GONE with no vault copy: Shadow_Debt_Channel_Map.md
       (collateral_multiplier.csv), _research/measurement_infrastructure_reviews.md (4, incl fwtw_data.csv),
       _research/funding_identity_adversarial_reviews.md, _research/paragon_burry_dossier.md (3).
       Severity: no live claim in the current answer rests on them, and the underlying sources (EDGAR
       filings, Z.1) are re-fetchable. Triage before quoting any of those four.
   d2  Thirteen more docs carry a dead scratchpad citation ALONGSIDE a durable one. Cosmetic; the durable
       path is what a reader should use. Bulk-fix only if someone is editing those docs anyway.
   d3  `data/eps_split/panel/` is an EMPTY DIRECTORY (22 Sep). The 385-firm diluted-share panel behind
       C-093 and every accretion figure is not on disk, so none of it is locally reproducible. Same class as
       C-097. Ask Grok for it on the next contact, bundled with the W3 panel.
   d4  THE GATE'S BAN SCAN SKIPS `_research/` AND `CALENDAR.tsv`, by design (`bin/check.sh` line 306:
       `-not -path './_research/*'`, *.md only). A killed ratio (C-116) survived in
       `_research/2026-09-11-Channel-Map-Gaps.md` and was found only by a Python sweep for the reasoning, 23 Sep.
       Rule: a finding cited from the ANSWER lives at top level where the gate sees it (W2 promoted 23 Sep); when a
       claim is killed, sweep `_research/` and the calendar in Python. Widening the scan is a design choice, not taken.

  STANDING QUALITY CHECKS ................................................... section 7
   S1 vs the SPV hole · attack the leak objection · re-derive "own computation" numbers ·
   look for false consensus · confirm corrections propagated

  DATED ....................................................... CALENDAR.tsv, 39 rows not done
  THE PRINCIPAL'S ............................................. Singh briefing · goal read-back · hermes-core

1. ETF1 - identity net of ETF shares        DONE 15 Sep -> 2026-09-15-ETF1-Identity-Net-Of-ETF.md (C-083).
                                            Issuance net of the wrapper is a retirement; bond ETFs are three-tenths of the
                                            wrapper; listed/closely-held mix is flat.

2. LIT1 leads to verify                     DONE 15 Sep -> 2026-09-15-LIT1-Residual-Literature.md (C-084).
                                            Tax-status recoding is real (taxable ~27%, foreign ~42% of Rosenthal-Mucciolo's
                                            look-through total in 2022). Legal-entity mix inside the F51 household line is
                                            not sized: PE funds and personal trusts remain in it; domestic hedge-fund equity
                                            does not (F51 line from 2012:Q4). The 2024 Burke citation was a merge with a
                                            section heading.

3. N4 — the interlock synthesis (b+c)       DONE 15 Sep -> 2026-09-15-N4-Scale-Timing-Bound.md (C-085).
                                            2024 private-repo growth was the ON RRP handoff (net -$45.7bn). Handoff-adjusted
                                            ceiling $136.2bn vs $1,404.9bn 2024 household purchases of the wrapper. Collateral
                                            re-use intensity did not rise; the dated six-bank stock step is H1 2026. No
                                            funded-share percentage. 1 Oct revolver parcel stays on the calendar (fragility, not this).

4. P4 — the elasticity pilot (= Tier B B3)   DONE 15 Sep -> 2026-09-15-P4-Russell-Elasticity-Pilot.md (C-086).
                                            Assignment t=1.61 (h=200); Δ13F t=0.78; CAR[-5,+5] t=1.55. IWB 2024 Jaccard 0.992.
                                            First stage fails. Does not rescale. 2SLS not reported.

5. D-G remainder — Green's untested numbers DONE 15 Sep -> 2026-09-15-DG-Remainder-Leveraged-ETF-Flows.md.
                                            G-008 supported (2x->$2; 3x->$3). G-012 $3B MU peak FOUND order-of-magnitude (~$1.3-2.9B via MUU+SOXL);
                                            $300M/day + G-013 50% BLOCKED-ON-PROPRIETARY. G-014 mechanism yes; ~150%/yr NOT reproduced
                                            (2026YTD SOX σ≈49% => μ_be≈24%). G-001 own-model remainder blocked-on-proprietary.
                                            First batch + RET1 remain the prior legs.

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


6a. B6 dividend payment-day IV             CLOSED 16 Sep. NOT A REFUTATION; NOT BLOCKED ON DATA ACCESS (C-090, C-091).
                                            Doc 2026-09-15-B6-Phase1-Payment-Day-Mechanism.md; pay-date scout
                                            _research/2026-09-16-NYSE-Payment-Date-Scout.md (VERIFIED NO free NYSE pay dates
                                            at scale - a good negative that answered the wrong question).
                                            THE REAL LIMIT IS ARITHMETIC. SPY daily sd = 111bp. Top-minus-bottom payment-yield
                                            spread = 1.32bp on a sample that ALREADY contains every S&P500 payer via imputed
                                            dates. At M=1.9 the predicted gap is 2.51bp against 111bp of noise -> 15,632 days
                                            per quintile = ~97,300 trading days = 386 YEARS. At M=9.4 it needs 16 years; we
                                            have 11.7. True pay dates remove timing noise, they do not widen the spread.
                                            DO NOT re-run B6, do not widen tickers, do not run the Nasdaq-only subsample -
                                            fewer payers is a SMALLER spread and strictly less power than the run that failed.
                                            SCREENING RULE THIS GENERALISES TO (now in CLAUDE.md): any design whose effect is
                                            a few bp against daily equity noise is unresolvable on a decade of daily data,
                                            whatever the source. Compute the MDE in the brief, before commissioning.

6c. JVZ mega-firm passive amplification    GATE RERUN FAIL 16 Sep -> _research/2026-09-16-JVZ-Gate-Rerun.md
    (principal clearance)                   Principal CLEARED permanent Tier B close on this FAIL (C-092).
                                            No real-flow regression. Coverage 540/587=0.920; top-40 megas 40/40.
                                            Within-Q SD SPY pctVal WITH megas **0.579** (26Q) — did NOT rise to
                                            ~1.6 (without megas 0.106). N=10,729 FQ / 439 firms / 26 time clusters.
                                            Placebo 200 draws (two-way cluster): median SE ret **0.548** → MDE
                                            **1.097pp** (pred÷MDE **0.48×** vs 0.528); idio SE **0.239** → MDE
                                            **0.478pp** (**0.90×** vs 0.43). Quarter clustering binds. 26 free
                                            N-PORT quarters cannot see 0.528pp under two-way cluster.
                                            RE-OPEN TRIGGER AS A NUMBER, NOT A WORD (added 16 Sep): if the only thing
                                            that changes is elapsed time, SE scales ~1/sqrt(clusters), so parity
                                            (pred÷MDE = 1.0) needs ~113 quarters — about 2048. At 40 quarters (2030)
                                            it is still only 0.60x. 'Permanent' is therefore fair; do not reopen on a
                                            hunch, and do not reopen on firm coverage — that is already 40/40 megas.
                                            SUPERVISOR'S BRIEF WAS WRONG AND THE AGENT SAID SO: I predicted megas would
                                            push within-Q SD to ~1.6+; it measured 0.579, BELOW the mega-heavy 208-firm
                                            sample's 0.818, because adding ~330 small names adds mass near zero and
                                            LOWERS the SD. The 26-cluster constraint was the half I got right. Prior Stage A /
                                            Stage B / sharpen remain UNINFORMATIVE (C-092), not NOT SUPPORTED.
                                            Spec: _research/2026-09-16-JVZ-Gate-Rerun-Spec.md.


6b. Holder-side split of the plug           SCOUTING CLOSED on the PE-bound route. Scout: `_research/2026-09-15-PFS-Scout-Corporate-Equity-Line.md`.
    (the C-084 gap)                         VERIFIED YES for Qualifying Hedge Funds only (Tables 8.16/8.17 Listed/Unlisted
                                            Equities, Form PF Q26/Q30). VERIFIED NO PE equity-holdings line — Section 10 is
                                            GAV/NAV, CPC industry %, CPC D/E only. Cannot bound PE inside F51 from PFS.
                                            Do not open measurement on this route. Remaining free scouts (ICI/SOI tax
                                            look-through) stay optional and separate.

8. EPS SPLIT — is 'earnings' partly buybacks?  DONE 18 Sep (Grok) -> 2026-09-18-EPS-Split.md. REVIEWED 19 Sep (C-093).
   (goal row: the PRICE SIDE, and the join       Method VERIFIED: AAPL re-derived exactly from SEC. RESULT, AS A BAND: per-share
   between its price and money halves)           accretion ~7-13% of the price gain since 2015; profit + index composition ~69-75%;
                                                 multiple ~18%. Lead claim SURVIVES - mostly real profit. The doc's point figure is
                                                 the top of its own 7.1-13.4% weighting band and survivorship pushes it up; 'profit'
                                                 is a residual that absorbs composition. Missing megas bias both ways (GOOGL buyer;
                                                 TSLA/AVGO issuers). data/eps_split/panel/ is EMPTY - per-firm panel not saved.

7. D4 — re-cut channel map dealer-first     HOLD. Trigger is the conduit channel stopping; it has not (re-checked 11 Sep on
                                            the 31 Aug N-MFP3 census). Folds C-066 when it runs. NEXT CHECK: the 10 Oct
                                            N-MFP3 census (30 Sep quarter-end) in CALENDAR.tsv. Full definition in Tier D below.
                                            RESTORED 19 Sep: this entry was deleted by accident on 18 Sep when item 8 was
                                            rewritten, which left the 10 Oct census with no ranked item to route its result to.



MARTIN'S, NOT MINE: the Singh briefing, pushed to 30 Sep by E-005 ("we don't have anything interesting to
tell him yet"); the hermes-core fixes task.

OUTSIDE PARCELS (orchestrator_outside):
  Parcel_ATT1_Premium_Attack_For_Grok_Cursor.md   - RETURNED 13 Sep, VERIFIED 13 Sep -> C-078. Grok reproduced all
      eight headline numbers exactly, then refuted the interpretation. I re-checked its structural claims myself: the
      P/E path (24.35->28.60->28.48->25.22), corr(real yield, residual) = -0.6991 (n=282), the baseline band
      (10.9%/16.5%/28.4%/35.4%/43.1%), and Damodaran's growth 8.74%->13.69% with ERP 4.60%->4.20% from
      ERPbymonth.xlsx. Five for five, plus the external file. The WINDOW compression survives and is corroborated;
      the LEVEL claim is dead. Its 30y TIPS point (FII30) is UNVERIFIED - FRED refuses scripted requests.
  Parcel_SYN1_Attack_The_Synthesis_For_Grok_Cursor.md - RETURNED 15 Sep -> _research/SYN1_return_2026-09-15.md.
      Earnings survives-amended; risk/growth split FAILS (C-082); unattributable FAILS (C-083); money-scale FAILS.
      Load-bearing: Z.1 equities = mostly ETF wrapper not operating-company demand. Rebuild money side from ETF1/A1.
  Parcel_BR2_Cross_The_Bridge_For_Grok_Cursor.md   - RETURNED 15 Sep -> _research/BR2_return_2026-09-15.md.
      Bound FAIL (C-080 restated). Aggregate M only-for-a-subset: dividend payment-day IV (Hartzmark–Solomon);
      second-best JVZ mega-firm passive mechanism. Sovereign-mandate IV not revived (B5/P4 dead).
  Parcel_RET1_Retirement_Flows_For_Gemini_AGY.md  - RETURNED 12 Sep, VERIFIED 13 Sep ->
      2026-09-12-Parcel-RET1-Retirement-Flows-Return.md. Four spot checks against the issuing workbooks, four
      exact. Result: private-sector DC net contributions turned negative in 2013 and have been negative in all
      11 years since (ICI Table 4) - so the passive bid is NOT net DC contributions. But the net is NOT a market
      flow either: DOL DC contributions include $74.6bn of rollovers IN, and $652.8bn of DC/DB outflow rolls into
      traditional IRAs and stays invested. Organic DC net 2023 = -$90.7bn, not the -$16.1bn headline. Flows stop
      at 2023 (IRS SOI lag); do not pair a 2025 level with a 2023 flow. Gemini's page numbers were wrong (its
      table names were right) - see the doc header.
  (already scheduled: the quarter-end sentiment parcel to Grok, 25 Sep - CALENDAR)

Infrastructure repair (step-ladder, 11 Sep) — DONE. Spec + both reviews + rung-5 overrules:
  _research/SPEC_reentry_infrastructure_2026-09-11.md. New guards in bin/check.sh: --todo reads the ```ranked
  fence (warns if missing), --latest (newest corrections), orphan check, second-home check, unregistered-
  correction check. Cold-read 10 tool calls vs 24 baseline; top priority + latest correction now PRESCRIBED.
  Spec items CLOSED 11 Sep (diff vs _research/snapshot_2026-09-11b/): S3 gross-saving S4 row marked CONTESTED;
  S5 read-table rows stripped of findings (7 rows); Tier-N + section 1.0 status clauses -> pointers; S-N2b
  settled row added. DEFERRED with trigger: move Parcel_*.md into Parcels/ (every Parcel file already has a
  read-table row, so a cold reader can find them; the move breaks every inbound link. Do it only if a
  cold-read test shows a reader wasting calls on them). data/status.tsv (build it for a class the next
  time one status fact is found in two places with different values).
  Rollback snapshot: _research/snapshot_2026-09-11/ (MD5SUMS.txt).
Closed 31 Aug - 15 Sep, with evidence — do NOT restate findings here, read the doc:
  P4 Russell RD         2026-09-15-P4-Russell-Elasticity-Pilot.md           | first stage fails; C-086
  LIT1 residual literature  2026-09-15-LIT1-Residual-Literature.md         | tax recoding not entity census; C-084
  ETF1 identity net of ETF  2026-09-15-ETF1-Identity-Net-Of-ETF.md         | wrapper was the issuance; bond ETFs 30% of it; C-083
  P5(ii) risk vs growth 2026-09-13-P5ii-Growth-Versus-Risk.md            | ran, did NOT resolve; 60% is a ceiling not a finding
  P5(iii) concentration 2026-09-13-P5iii-Concentration-And-JVZ.md        | gap 4x, idio-vol 0.686->1.042; flow link weak-negative
  P5(iv) third measure  2026-09-14-P5iv-Third-Premium-Measure.md         | survey ERP found; its SPLIT retracted (C-082) - the bond leg drove it
  P5(i) event study     2026-09-14-P5i-Event-Study-Result.md             | 2024 accrued as DRIFT; FOMC beats earnings head-to-head
  E2 earnings quality   2026-09-13-E2-Earnings-Quality-Useful-Lives.md   | 5-12%; main finding SURVIVES; Amazon reversed
  E1 European pensions  2026-09-14-E1-European-Pensions-Scout.md         | Wtp is a RELABELLING not a sale; thesis refuted
  S1 supply decomp    2026-09-13-S1-Supply-Decomposition.md                 | issuance moved not buybacks; 89% of record Q1 issuance is PRIVATE
  Tier B first stage  _research/2026-09-13-B5-FirstStage-Spec.md            | WEAK RESULT under E-005: slope +1.078, corr +0.57, n=9; limited by publication frequency
  Channel map         _research/2026-09-11-Channel-Map-Gaps.md              | the re-plan's input
  Green corpus pull   2026-09-11-Green-Passive-Bid-Corpus-Dossier.md        | 38 claims; 5 quotes re-verified
  Green Substack+Ep61 2026-09-11-Green-Substack-And-Ep61-Synthesis.md      | 17 posts + Ep 61; 3 figures re-read in source
  Treasury demand     2026-09-11-Who-Buys-Treasuries-Synthesis.md          | 4 downloads vs Green; 3 claims + 4 series re-checked
  P1 net buyers       2026-09-11-P1-Equity-Net-Buyers.md                     | Z.1 2026Q2; identity holds; 93% of the rise is revaluation
  P2a benchmark       2026-09-11-P2a-Return-Decomposition.md                 | 70-80% earnings since 2015; ERP 4pp -> 1.7pp
  P2b top-10 test     2026-09-12-P2b-Top10-Earnings-vs-Weight.md             | earnings LED value to 2019; 4.3pp gap only in 2025
  P2c rates vs premium 2026-09-12-P2c-Rates-vs-Risk-Premium.md               | rates a DRAG; the premium did the work
  P3 + ATT0           2026-09-12-ATT0-First-Attribution.md                   | the multiplier approach refuted (C-077)
  NYSE pay-date scout 2026-09-16-NYSE-Payment-Date-Scout.md | VERIFIED NO; E-005 limit
  B6 Phase 1         2026-09-15-B6-Phase1-Payment-Day-Mechanism.md           | uninformative null; C-090/C-091 - 386yr sample needed; no M
  D-G remainder      2026-09-15-DG-Remainder-Leveraged-ETF-Flows.md          | G-008 yes; $3B MU band; 150% no; Tier1 blocked
  D-G first batch     2026-09-11-DG-Green-Numbers-Checked.md                 | Alphabet DIFFERENT; passive shares by denominator
  IPO boom            2026-09-12-I1b-IPO-Prospectus-Facts.md                 | ~$112bn primary in 2026; cornerstones in 3 of 10
  AI funding          2026-09-12-F1-Funding-Table.md                         | NVIDIA guarantees $105bn of an OpenAI affiliate's leases
  Oracle Q1 FY27      2026-09-12-Oracle-RPO-And-Financing.md                 | $664bn backlog; $288bn of leases off balance sheet
  Z.1 closure refresh 2026-09-12-N2c-Closure-Refresh-2026Q2.md               | Fed still buying; NFC net equity issuance positive
  Singh back-test     2026-08-31-N3v4-Singh-Reconciliation.md section 6     | C-074; open: sec-lending leg, pre-Form-PF years
  N2b v2 (3 lenses)   2026-08-31-N2b-zk-The-Wholesale-Share.md section 8   | z_k ready to carry N4
  N3 v4 (Singh panel) 2026-08-31-N3v4-Singh-Reconciliation.md              | numerator independent, x2.23
  ZK2 return (Gemini) _research/ZK2_verification_2026-08-31.md             | stands-with-amendment
  SB1 return (Grok)   _research/SB1_verification_2026-08-31.md             | 56/62; C-072, C-073
  Model routing       CLAUDE.md working rules + ~/.claude/skills/orchestrator_outside/SKILL.md
Martin's, not mine: the Singh send (v5 ready, due 16 Sep); the 25 Sep goal read-back (E-003 + E-004); the two
outside parcels above; the hermes-core fixes task.
Scripted/dated — CALENDAR.tsv is authoritative, query it, never copy it here:
  awk -F'\t' '$NF=="OPEN"' CALENDAR.tsv | sort | head
```

*Dated items run on the calendar regardless — query it, do not copy it: `bin/check.sh --todo`.*

### Tier N — the nexus itself (**serves A12 — since 11 Sep, channels (b)+(c) of the goal, A13**). The least-served part of the project

**N1. Get the primary sources into the corpus. — SUBSTANTIALLY DONE 22 Aug.** Pozsar & Singh WP/11/289 (Dec 2011) is the
frame for the whole programme and **has never been read into this project** — "nonbank-bank
nexus" returns zero hits corpus-wide. Also unread: Pozsar, *Shadow Banking: The Money View*,
OFR WP 2014-04 (in `Collateral_Data_Inventory.md:105` as a bibliography line only);
*Institutional Cash Pools and the Triffin Dilemma*; Adrian–Ashcraft–Boesky–Pozsar,
*Shadow Banking*, NY Fed Staff Report 458.
*Blocks: N2, N3, N4 — all of them. Everything below is downstream of reading the frame.*
**Known obstacle:** `imf.org` and `rba.gov.au` PDFs both returned **HTTP 403** to our fetcher on
22 Aug. The OFR paper at `financialresearch.gov` was not tried. Needs a retrieval route that
works before this can start — that is the first concrete task, not the reading.
*Status (11 Sep): obstacle solved 22 Aug — `elibrary.imf.org` serves the IMF papers `imf.org` blocks (route in `2026-08-22-Nexus-WP11289-Read.md`); all four sources above are in `_research/primary_sources/` as PDF and text.*

**N2. Build the money leg — institutional cash pools and non-M2 money demand.** Half the nexus. Our own text concedes the gap this item exists to close: institutional cash pools are *"the actual marginal demanders in the Pozsar account"* and *"were not measured by anyone here"* (`2026-08-21-Safe-Asset-Share-Reexamined.md:179`). *Status: no longer blocked by N1, and no longer "nothing" — its two identified subcomponents are BUILT and adversarially reviewed: N2a (`2026-08-30-N2a-Offshore-Dollar-Leg.md`) and N2b (`2026-08-31-N2b-zk-The-Wholesale-Share.md` §8, ready to carry the N4 synthesis).*

**N3. Build Singh's denominator — primary source collateral.** We reconstructed the *numerator*
to five significant figures (US-six source collateral $6,907bn FY2025) and left the denominator
an estimate we ourselves called *"the weak link"* (`Shadow_Debt_Channel_Map.md:1196`). **That
denominator is the nonbank side of the nexus.** Pozsar–Singh give the benchmark to extend:
**$3.3trn (YE2007)**, **$2.4trn (YE2010)** — $1.6/$1.3trn hedge funds, $1.7/$1.1trn real money.
*Blocked by: N1 for method. Partially independent — the Form PF and ISLA inputs are already
identified in the channel map's build recipe.* **23 Aug pm: hedge-fund end measured from Form PF
aggregates (D3 §8 / D10). Scouting parcel for the rest of the collateral leg written —
`Parcel_N3_CollateralLeg_Scouting_For_Gemini.md` (sources by type, official re-use measures, per-CCP
PQD files, re-use literature) — awaiting the principal's hand-off to Gemini; return expected at the
Dropbox share root as `N3_Collateral_Scouting_Return.md`, to be filed under `_research/` and
adjudicated under C-054 rules (identifiers deleted unread).** **RETURNED 19:27 and verified the same evening (C-055) — `2026-08-23-Parcel-N3-Collateral-Return.md`. What it opened: Singh & Goel WP/19/106 **Table 2** read at source — sources $3.4trn (2007) / 2.4 (2010) / **3.7 (2017: hedge funds 2.2, sec lending 1.5)**, pledged $10.0 / 6.0 / 7.5trn, velocity 3.0 / 2.5 / 2.0; no later Singh table exists (Jan 2026 Central Banking: "roughly $13trn", velocity ~2, paywalled). Fund-side hedge-fund source = Form PF Q43 collateral posted (tracks Singh to ~15% 2013–16, diverges 2017, $8.2trn 2026Q1); sec-lending source = ISLA €3.9tn on loan (31 Mar 2026, client-type split on the market-data page). **N3 is no longer blocked on method: the build is the concept reconciliation between Form PF Q43 / ISLA on-loan and Singh's Table 2, then the 2026 row.** No official re-use aggregate exists anywhere (FSB/BIS/ESMA confirmed; FSB Feb 2026 repo report cites third-party 50–90% / 65% / 85% rates).** *Status (11 Sep): the reconciliation is BUILT — `2026-08-31-N3v4-Singh-Reconciliation.md` (panel rebuilt from the 2017 filings; §6 back-test 4 Sep, C-074). What remains on this thread is ranked-block item 0.*

**N4. Harvest the interlock from material we already own.** *Status: RESULT 15 Sep — `2026-09-15-N4-Scale-Timing-Bound.md` (C-085). Ranked item 3 closed.* Each of the nine channels has a
**"Double-counting risk"** section written to net the interlock *out*. Under Pozsar–Singh a
security collateralising three channels at once is not double-counting — it is the object.
The restated questions (did it expand; was the expansion large enough as a ceiling; did the timing match 2024) are answered. The nine-channel re-read remains a method note.
*Blocked by: nothing. Closed.*

**N4a. Gemini omnibus retrieval parcel — RETURNED and folded 22 Aug (C-043/044/045). DONE.** *(serves A12.)*
`Review_Prompt_For_Gemini_Retrieval.md`, written 22 Aug — a **retrieval** commission, not a
review, sent for search capacity. Its Group A is the highest-value question in the project right
now: **has anyone already extended Pozsar's shadow-money aggregate past 2013, built any of his
three satellite accounts, or updated the $6trn institutional-cash-pool figure?** A positive
answer to any of those changes what N2 and N3 are — from build-from-scratch to extend-and-check.
*Blocks: nothing formally, but running it BEFORE N2/N3 could save months. Do not start N2 until
Group A is answered.*
*Delivery risk, stated: the previous Gemini parcel was written, delivered and then sat unrun for
a day while work continued around it. This one has the same failure mode and no mechanism
prevents it — it needs the principal to actually run it.*

**N2a. Re-read the offshore-dollar and money-like work as asset-manager-to-bank, not bank-to-bank.** *(serves A12.)* WP/11/289 states it directly: *"banks' funding through non-M2 instruments are asset manager-to-bank claims and not bank-to-bank claims as it is widely assumed"* — aimed explicitly at the Shin interbank reading. If a material share of what we have read as interbank wholesale funding is asset-manager-to-bank, the counterparty question becomes first-order in every channel, and our channel map does not systematically ask it. *Status: BUILT and adversarially reviewed 30 Aug — see `2026-08-30-N2a-Offshore-Dollar-Leg.md` §7 (N2aR, Grok: ~19/20 checks confirmed, one re-measured under C-069). Folded into N2's build target.* See `2026-08-22-Nexus-WP11289-Read.md` §2.

**N2b. Build `z_k`.** *(serves A12.)* The paper decomposes Shin's funding share into `z_h` (M2 funding from households) and **`z_k` (non-M2 funding from other nonbanks)** — the whole nexus lives in `z_k`, and it is the closest thing to an estimable object the framework offers. *Status: BUILT and reviewed — see `2026-08-31-N2b-zk-The-Wholesale-Share.md` §8; z_k passed three adversarial lenses and was carried by N4 on 15 Sep.*

**N4b. Parcel A — the interlock — RETURNED and adjudicated 22 Aug (`2026-08-22-Parcel-A-Interlock-Return.md`). DONE; follow-ups (Avdjiev 30–45%, layering ratio, from-whom-to-whom) carried under D7/N4.** *(serves A12.)*
`Parcel_A_Interlock_For_Gemini.md`. The external half of N4: netting conventions per publisher
(Z.1, FSB, BIS LBS, OFR repo, IMF GFSR), who has written about double-counting as an object, the
term of art, documented per-channel overlaps, and whether any consolidated unduplicated measure
exists. **N4's internal re-read does not wait on this** — the two halves are independent.

### Flagged candidate directions — raised 22 Aug under N5, none started

*These are research QUESTIONS, where N1–N4 are construction tasks. Recorded per the standing
instruction to flag rather than fold. All serve A12. Ranked; the first two are the strong ones.*

**D1. Bill supply versus cash-pool demand — the Triffin test, run forwards.** **BUILT, v1, 22 Aug — `2026-08-22-D1-Bill-Supply-vs-Shadow-Money.md`; result promoted to §2 S-D1. Remaining: foreign-official TIC netting, demand-only uninsured split, FR 2004 post-2021. Scouting adjudicated at `2026-08-22-Parcel-D1-Scouting-Return.md`. Publishers/tables usable; IDs ~50% wrong; 2022–26 literature unlocated (C-050). Two real advances, both ours: Pozsar's own table shows the shortage closing $1.5trn→~0 in 2008–09 as bill supply surged (the template), and FRED shows ON RRP at $0.2bn on 21 Aug 2026 (the buffer is gone). H1 **TESTED 31 Aug by N2b, and the first answer was WRONG — see C-070.** Corrected (`2026-08-31-N2b-zk-The-Wholesale-Share.md` §7): the wholesale share z_k **more than doubled**, 9.09% (2021-12) -> 19.45% (2026-06), monotonic; it did not stay flat. The RRP cash did not leave the money-fund complex — but its destination is NOT pinned by the drain arithmetic: MMF Treasury holdings rose +$1,183.1bn over the same window, more than the entire $961.9bn drain. So H1's 'displaced ON RRP, not private money' survives in its negative half (no new household money was needed), while the positive half — where the cash went — is split between private repo and bills and remains unattributed. Original framing: 'the 2023–24 bill surge displaced ON RRP, not private money'. NEXT: re-pull S6/S7/S8/S12/S13/S14 and extend the shortage table to 2026. Ours to do.** WP/11/190's whole
argument is that shadow banking arose *because institutional cash pools outgrew the supply of
government safe assets*, and its policy conclusion is literally **supply management of Treasury
bills as a macroprudential tool**. Since 2023 the US has issued bills at enormous scale. **The
framework therefore predicts private shadow money should have SHRUNK.** Test it. Either result is
publishable: if private shadow money contracted, the "shadow debt explosion" narrative is wrong in
an interesting and specific way; if it grew *despite* the bill deluge, demand growth is larger
than anyone has measured. *Testable from public data. Connects directly to the safe-asset share
work. Strongest single candidate.*

**D2. Who actually holds the AI paper? — BUILT v1, 22 Aug; result in §2 S-D2. Remaining: full N-PORT census (background), insurer Schedule D, hyperscaler cash composition (D9).** The bridge between the subject matter that started this
project and the frame that now governs it. Under the nexus, the question about hyperscaler IG
bonds, data-centre ABS and neocloud debt is not *how much* but **whether it is funded by
money-like claims or by long money.** If it sits in MMFs and cash-pool vehicles it is a nexus
story with run risk; if pensions and insurers absorb it, it is a duration story with no run.
**Nobody has asked.** Form N-MFP gives MMF holdings issuer by issuer, so the money-like side is
constructible. *This is how A11's subject matter re-enters legitimately, through A12's frame.*

**D3. Is shadow-money demand explained by asset-management industry structure? — BUILT v1.2, 23 Aug; result in §2 S-D3 (amended twice). Margin leg MEASURED 23 Aug evening from FIA's free CCP-tracker API (C-056 killed my 'member dashboard' claim): 15-CCP initial margin $757bn (YE2021) → $1,071bn (2026Q1), +41% vs complex +16% — faster than AUM, too small and too securities-heavy to be the cash surge; `2026-08-23-Parcel-N3-Collateral-Return.md` §2.1, D3 §9. Remaining: sec-lending leg (SLATE 29 Mar 2027), fund-buffer leg (ICI liquid-asset ratio, SEC Registered Fund Statistics). Scouting parcel returned and adjudicated (C-054).** Reverse maturity
transformation makes money demand a **by-product of managing long money** — so it should scale
with AUM, with derivatives-overlay use, and with securities lending, all of which have grown
enormously since 2013. If cash-pool growth tracks AUM growth, shadow money is structurally driven
and grows regardless of monetary policy. Simple, strong, and directly downstream of §1 of
`2026-08-22-Nexus-WP11289-Read.md`.

**D4. Re-cut the channel map dealer-first.** Our nine channels are organised by *instrument*.
Pozsar puts the **dealer at the pivot** — cash pools on one side, levered investors on the other,
dealer balance sheet between. A dealer-centric cut makes both legs of the nexus visible at once
and promotes dealer *capacity* (SLR-constrained, per Duffie) to the binding variable. Cheaper
than the from-whom-to-whom re-architecture and reuses the ASC 860-30-50 footnote data we already
collected.

**D5. Securities lenders' cash-collateral reinvestment accounts.** Simultaneously cash-pool
category 4 **and** a collateral source — the nexus inside a single institution type. If the
interlock is real anywhere, it is here, and being one institution type makes it tractable.
*Sharpest available test case for N4.*

**D6. Are stablecoins a fifth cash-pool category? — SETTLED 29 Aug; result in §2 S-D6.** Answer: yes, and
the pool is the **issuer**, by statutory construction (GENIUS reserve restrictions + interest ban); the coin
itself is a money-instrument, not a pool. Engine 5 of N2c closed with it. Original framing: the "do not lose"
discriminator — which the statute answered for us.

**D8. CONDUITS as the nexus channel — FICC-sponsored repo AND alternative ABCP. (Broadened 23 Aug after the FT harvest.)** *(serves A12; raised by D1.)*
MMF repo cleared at FICC rose **$335bn (Jun-23) → $1,298bn (Dec-25)**, +$741bn to Jul-26, while
the Fed facility drained — cash pools funding the dealer–hedge-fund complex through one cleared
conduit, the money leg and collateral leg touching in a single instrument. **Not on our nine-channel
list as a channel. Strongest candidate yet for the E2 "missing channel".** Flagged, not folded.
*23 Aug pm: the far end of the pipe is now measured — qualifying hedge funds' repo borrowing $1.2trn
(YE2021) → $3.2trn (2026Q1), OFR Hedge Fund Monitor, D3 §8.2. D8 has both ends; the middle (dealer
matched book, FICC sponsored volumes — `FICC-SPONSORED_REPO_VOL` is on the same API) is what remains.*
*23 Aug evening: the middle is measured too — DTCC's daily sponsored CSV: sponsored repo (hedge funds borrowing)
$171bn (Dec-21) → $1,384bn (Dec-25) → $1,031bn (20 Aug 26); sponsored reverse repo (MMFs lending) $245bn →
$1,576bn → $1,265bn. ~40% of hedge-fund repo borrowing is sponsored. **And a new question: total sponsored is
down $664bn from the Dec-25 peak** — OFR's 20 Aug 2026 blog says clearing "plateaued in Q1 2026". Is the D8
conduit shrinking or migrating (to bilateral / NCCBR)? `2026-08-23-Parcel-N3-Collateral-Return.md` §2.2.*
*Scouting parcel written 23 Aug evening — `Parcel_D8_TreasuryClearing_Scouting_For_Gemini.md` (mandate dates as amended;
CME/ICE Treasury-clearing volume pages; FICC agent-clearing stats; 2025–26 transition publications). Return expected
at the share root as `D8_Clearing_Scouting_Return.md`; file under `_research/`, verify by fan-out (C-055), then D8 session.*
**RETURNED 20:33, verified by seven agents, adjudicated — C-057; `2026-08-23-Parcel-D8-Clearing-Return.md`. THE QUESTION IS
ANSWERED: neither migration nor retreat. On monthly averages the sponsored pipe plateaued at ~$2.5trn after a $2.67trn
December (−12% to August; hedge-fund side −17%, MMF side −8%; +12% y/y). OFR (20 Aug 2026, own collections): cleared share
53% → 46% (in-scope 72% → 62%), the drop concentrated in G-SIBs (55% → 45%, back to Sept-25; surcharge measured at year-end)
while non-G-SIBs rose 40% → 55%; FICC "the only Treasury repo CCA currently operating". CME Securities Clearing had no
members or users as of 6 Aug 2026 (its own SEC filings); ICE repo is Q4 2026; no volume exists at either. ISDA-Actrix
(monthly since Jun 2026): cleared ADV $6.5trn, sponsored $2.5trn = 38.6%, YTD sponsored −6% / direct −1%, y/y +23% / +9%.
Mandate unchanged: cash 31 Dec 2026, repo 30 Jun 2027. New series: DTCC GSD monthly (2001→), Actrix monthly; both in
`data/series.tsv`. D8's remaining work is the OTHER conduit — alternative ABCP funding equity leverage — and the FR 2004
venue split; the Treasury pipe is instrumented end to end.**
*Scouting parcel for the ABCP half written 23 Aug late evening, for **Grok** (live-search shaped: sponsor→programme
mapping, rating-agency ABCP publications, AXW product data, 2025–26 commentary) — `Parcel_D8b_Conduits_For_Grok.md`.
Self-contained (Grok reads none of our files); grounding table in the parcel header maps every inline fact to its
source file. Return comes back as one fenced block → save to share root as `D8b_Conduit_Scouting_Return.md` → C-055
fan-out before anything is read as a finding. X-post section fenced as colour-not-sources (R7); C-045 anti-confirmation
rule stated as R8.*
**RETURNED 24 Aug 06:24 and verified by four agents the same morning — the FIRST external return with no constructed
identifiers found (`2026-08-24-Parcel-D8b-Conduit-Return.md`). Sponsor→programme map verified at primary/archived sources
(Northcross roster verbatim; Regatta=Nearwater; JPM→Chariot/Falcon; RBC→Thunder Bay/Old Line/Bedford Row; TD→Cabot
Trail/GTA; BNP→Matchpoint/Starbird; CA→Atlantic/La Fayette/LMA; SG→Antalis/Barton; Mountcliff→20 Gates; Bennington
Stark: sponsor Liberty Hampshire, admin Guggenheim Treasury; BSN = Chesham's investment adviser). The map fed a full-census effort that took **three passes** to get right (C-059): a name-map and then a
category filter each proved incomplete, producing a **false correction (C-058, RETRACTED — the 23-Aug $9.4bn
three-name figure was right to three decimals)**. Definitive, from all 44,512 positions in the 325 August
filings with no name or category filter (`bin/census_nmfp3_all_positions.py`): at 31 Jul 2026 money funds held
**$101.2bn of ABCP across 139 issuers**; the named conduit families total **$56.7bn**, of which **$41.8bn is
non-bank-sponsored**, $7.9bn has no determinable sponsor in any free source, and $7.0bn is newly-found
bank-sponsored. **Ionic ($5.21bn), sponsored by Capitolis, is a total-return-swap vehicle over listed equities
— the FT's money-fund→conduit→equity mechanism, and it was on no sponsor list the press used.** Chesham $7.16bn;
Verto $5.57bn and HQLA $3.62bn have unknown sponsors. **D8c RETURNED and verified 24 Aug (`_research/D8c_Sponsor_Identification_Return.md`; independent
re-read of the two Fitch actions and Capitolis's own broker-dealer statements). RESULT — CAPITOLIS IS THE
CHANNEL. Fitch, verbatim, on **HQLA Funding** (Champlain/Tahoe 27 Sep 2024; Huron 2 Dec 2024): *"Capitolis
Administrator LLC (Capitolis) is the program's sponsor and administrator"*; HQLA funds **US Treasuries** via
Dynamic Funding Markets repo. Separately **Ionic Funding LLC is a wholly-owned subsidiary of Capitolis Inc.**
and lends into **Capitolis Liquid Global Markets**, whose book is **TRS referencing equity securities** plus
securities lending. Money funds held **$8.83bn** of the two at 31 Jul 2026 (Ionic 5.21 + HQLA 3.62) — **more
than Chesham's $7.16bn, so the largest non-bank ABCP sponsor in US money-fund portfolios, running Treasuries
and equities through one shop.** **New free semi-annual series:** CLGM's Statement of Financial Condition
(31 Jan / 31 Jul, `capitolis.com/regulatory-disclosures`, all five archived) — total assets **$4.97bn (Jan-24)
→ $19.70bn (Jan-26), ×4.0**, of which affiliate revolving loans from Ionic and HQLA **$4.88bn → $18.09bn**.
That is the FT's money-fund→conduit→equity chain measured at the vehicle, with a two-year history.
**Still unattributed: $13.3bn** (Verto 5.57, Overwatch 2.70, Washington Morgan 1.98, Intrepid 1.37, Mackinac
0.87, Alinghi 0.81). Not verified: Capitolis Administrator LLC as *Ionic's* sponsor (only the Capitolis Inc.
ownership is); Drexel Hamilton sponsors *"Overwatch Funding Company"*, which is not evidence about Overwatch
Alpha/Bravo LLC — not merged. `2026-08-24-Parcel-D8b-Conduit-Return.md` §2.2.**
**25 Aug, both months re-run definitively (§2.1b):** MMF-held ABCP **$104.47bn (30 Jun) → $101.22bn (31 Jul),
−3.1%**; the eight named families **−6.2%**, Capitolis −16.0%, Northcross −30.7%, Nearwater −27.8%, while
Chesham **+13.5%**. **Total ABCP outstanding ROSE over the same window (Fed CP $421bn Dec-25 → $488bn Aug-26)
— so money funds are not the marginal buyer of the conduits' 2026 growth.** Two points, not a trend; the
September census settles it. The 24-Aug June figures were name-map derived and are WITHDRAWN in
`data/series.tsv`. CME AIR TRF has FREE daily files via DataMine (the equity-financing-cost series). Remaining for total channel
size: gated S&P sponsor tables or paid DTCC feed — flagged.**

**D9. Does the AI complex fund itself? — BUILT and CLOSED 24 Aug; result in §2 S-D9.** *(serves A12; raised
by D2.)* Answered from all six firms' own filings: **$146.2bn of corporate debt securities held** (Amazon 59.4,
Meta 33.1, Alphabet 26.2, NVIDIA 15.1, Microsoft 12.4, Oracle none), **6.6× the entire money-fund industry's
$22bn**. **No issuer detail is disclosed by any of the six**, and corporate treasuries file no holdings
schedule, so the reflexive question is unanswerable from public disclosure — a sized measurement gap.
Remaining threads are the three N5 flags in S-D9, not the main question.
`2026-08-24-D9-Does-The-AI-Complex-Fund-Itself.md`.

**D10. Hedge funds as the collateral mine — the one chain measurable at both ends.** *(serves A12;
raised by D3 §8, 23 Aug.)* Qualifying hedge funds posted **$8.2trn of collateral at 2026Q1, $3.8trn
more than at YE2021**, tracking secured borrowing one-for-one (repo ×2.8, prime brokerage ×1.6); MMFs
lend $1.3trn into FICC sponsored repo (D8). Cash pools → FICC → dealers → hedge funds → Treasuries
posted back: Pozsar–Singh's money leg and collateral leg in a single instance, each end an open
series. Questions: (i) how much of the hedge-fund repo book is FICC-sponsored (OFR `FICC-SPONSORED_*`
series vs Form PF repo borrowing); (ii) re-use — Singh's collateral velocity on this chain from
dealer 10-Q "collateral received that may be repledged"; (iii) whether the ~$1trn collateral-minus-
borrowing residual is CCP margin (PQD 6.1 for CME/FICC) — which would also close the D3 margin leg.
One session from open data. **Flagged, not folded.** *23 Aug evening: (i) is answerable now — DTCC sponsored repo
$1,384bn vs Form PF repo borrowing $3,379bn at YE2025 ≈ 41% sponsored; (iii) the PQD files for all eleven CCPs are on disk
(`data/vintages/ccp_pqd_2026Q1/`), FICC GSD 6.1.1 = $66.5bn; the 15-CCP IM series is in `data/series.tsv`. Remaining: (ii)
re-use on this chain, and the concept reconciliation in N3.*

**N2c. THE FUNDING CLOSURE — BUILT v1 same day, 29 Aug; result in §2 S-N2c.** Remaining: engine 5
(stablecoins → D6 parcel), NDFI loan composition, household-cell split, RoW composition, the 2026Q1 equity
issuance sign-flip (watch at Z.1 Q2, ~11 Sep). Original framing: *(flagged 29 Aug at the principal's prompt.)* The programme has mapped pipes but never closed the
sources-and-uses: 2023–2026 gross absorption (Treasury net issuance + corporate/data-centre debt + net equity
demand at rising valuations) against the only five things that can pay for it: **(1) bank money creation** —
H.8 bank credit and specifically **loans to nondepository financial institutions**, the bank→private-credit/PE
pipe, the largest money-creation channel still unmeasured in our map; **(2) the central bank** — Fed RMPs
(ratio corrected 30 Aug, C-063: 63.6%→44.4% matched-endpoint, falling); **(3) foreign inflow** — TIC, corrected for the
~$1.4trn Cayman hedge-fund undercount (Barth et al., FEDS 15 Oct 2025, verified); **(4) new money-like
instruments** — stablecoins (D6); **(5) reallocation + leverage of existing money** — the MMF/deposit rotation
(D1/D3, settled) and the collateral chains (N3: sources ×3, velocity ~1.3–1.5). Note the reflexive loop the
closure would make visible: deficits CREATE the collateral that the leverage stands on, and the leverage buys
the deficits — Treasuries as both the financed object and the financing instrument. Includes the buyback line:
Z.1 net corporate equity issuance is deeply negative — a debt-funded structural buyback bid (C-065: the
"only net buyer" reading was later broken; see S-N2c v2). All free data (Z.1, H.8, H.4.1, TIC, attestations). ~One to two
sessions. **Flagged, not folded.**

**D7. Two cheap methodological builds.** (a) The **Goldsmith layering ratio** — intra-financial
assets over total financial assets — looks constructible from Z.1 and directly measures the claim
multiplication we keep circling. (b) A **from-whom-to-whom pilot on repo alone**, where OFR
collections now exist, rather than re-architecting everything at once.

> **Still unanswered after two attempts: the missing-channel question (E2).** Both external passes
> returned channels already on our list. Treat "what is materially moving that we do not have"
> as open, and do not assume the absence of an answer means there is nothing there.

**N5. Flag, do not fold.** Per the principal's instruction, ideas surfacing from N1–N4 that
merit their own investigation get **flagged as such** in this file. Do not silently absorb them
into an essay outline.

### Tier O — outcome-side (**serves A11**). Real, but downstream of the goal

*Formerly "blocking the essay — nothing ships until these clear". Still true as stated; it is
the ranking that changed, not the content. Do these when the nexus work is blocked on
retrieval, or when the essay is actually being drafted — not before.*


#### Blocking the essay specifically (tier O)

**O0. Parcel B — RETURNED 22 Aug; C-024 closed, C-046/C-047 opened (`2026-08-22-Parcel-B-Numbers-Return.md`). DONE.** *(serves A11.)* `Parcel_B_Essay_Numbers_For_Gemini.md` covers items 1
and 2 below plus the 83.7% split. **Built so the margin-debt figure is derived independently
before our three conflicting values are shown** — asking "which of these is right" would have
produced agreement with one of them, which is worth nothing (C-045).

1. ~~**Reconcile the margin-debt ratio (C-024).**~~ **CLOSED 22 Aug — three (vintage × denominator) combinations, all arithmetically right; the level is conceptually unsound (numerator covers ETFs/ADRs/bonds), use the flow. Conduit-financed PB lending may sit outside FINRA margin debt (FT harvest 23 Aug).** Three figures for one quantity, opposite
   conclusions, and it is the number designated load-bearing. Name the denominator, fix the
   vintage, compute once. Then use the **flow**, which is not in dispute.
   *Blocks: any fragility claim. Independent. ~1 hour.*
2. **Rewrite the essay opening against BEA Table 5.1 (K6) — now also the C-047 lookup: two reviewers, two values for gross private saving, neither ours.** Household vs business vs government
   gross saving, 2019–2026Q2. This is the first objection both reviewers raised.
   *Blocks: the entire draft. Independent. ~30 min, public data.*
3. **Verify the five numbers Grok could not.** BIS residual (global $390.6bn now confirmed by
   Gemini; **the Japan 47% must be restated as residence-based — C-039**), safe-asset 27.5%,
   Form PF prints, the 83.7% split, the $36.6trn sum. Gemini confirmed four of five; the
   remaining exposure is *methodological*, not arithmetic.
   *Blocks: publication of any of those figures. Partly done — see §3.*

### Next, and each has a named dependency

4. **Name the q series and settle it (0d, C-036).** Z.1 equity q is a post-1945 high;
   replacement-cost q reportedly is not (~1.94 vs ~2.15 in 2000Q1 — **unverified**). One series,
   one sentence, or the claim dies in the first referee report.
   *Blocks: pillar (iii) of the essay. Independent. Verify the counter-figures first.*
5. **Find an instrument for repo attribution (0c, restated after C-038).** The Form PF / FSR
   comparison is a **category error** — opposite sides of the trade — so the basis-trade
   hypothesis is currently *unevidenced*, not merely unquantified. The task is no longer
   "attribute the growth" but "find a measurement that can".
   *Blocked by: nothing. But do not reuse the old comparison.*
6. **GLL out of sample, 2018–2026 (0e, C-037).** Do not import 1989–2017 variance shares into a
   2023–25 paragraph. If a clean decomposition is not possible, drop GLL from that paragraph.
   *Blocks: the discount-rate paragraph, which is now half-withdrawn under C-035.*
7. **Triage the unpromoted caveats (C-040).** Only 3 of 17 items from the 21 Aug do-not-say list
   reached the register; one of the remainder reached an external reviewer as a load-bearing
   claim. Highest-value unpromoted: velocity phrasing, Damodaran's near-circular 266bp, Bezemer
   et al. used to characterise 2026 on a sample ending 2005.
   *Blocks: nothing directly — but it is the mechanism by which the next C-036 happens.*

### Standing, with triggers rather than dates

8. **Meet the leak objection.** Money spent on an existing asset reaches a seller who can spend
   it on goods. Candidates: low MPC at the top (Mian–Straub–Sufi), non-consuming buyers, credit
   extinguished on resale. Nobody has quantified it. *Trigger: before the fragility section is
   drafted.*
9. **Decompose bank lending to NBFIs.** $2,006bn, unsplit by borrower type. Call Report RC-C
   M.10.a–e gives five buckets from 2025Q2. Honest current answer: we do not know how much is AI.
   *Trigger: only if the essay makes a claim about that series. It currently does not.*
10. **Test the SPV/JV capex hole**, the largest known bias in S1 — now live as 2025–26
    project-finance issuance, not only a known unknown. *Trigger: Q3 10-Qs, 15 Nov (calendar).*
11. **Build the Tier-1 six** from the measurement handbook. Free, 30 min–2 hrs each.
    *Trigger: when a specific figure is needed; do not build speculatively.*

### Tier A2 — the persona capability, pending a decision

**A2a. Parcel C — RETURNED and then OVERTURNED 22 Aug (C-048): the 17 Aug filings do not exist; PJM and MISO obtained 90-day abeyances on 14 Aug. Three panel positions cannot resolve until ~12 Nov (calendar). The 30-day informational reports ARE real and unread (calendar 25 Aug).** *(serves A2.)*
`Parcel_C_FERC_Dockets_For_Gemini.md`. **This is the overdue 17 Aug calendar item.** Asks, per
RTO: does a *transferable* flexible-load service class appear, or do the RTOs defend
firm-service-only tariffs — the two branches three pre-registered panel positions turn on. Also
asks the parcel to correct our own unverified basics (the "six" RTOs, the docket numbers, whether
ERCOT is in scope).
*Written so the answer is worth having even if A2 is parked: whether a transferable flexible-load
right now exists is a real fact about how compute demand gets financed, independent of the panel.*

### Tier T — tangents. Labelled, not hidden, not ranked against the goal

*Nothing here yet. This section exists so that the next interesting thing that serves no goal
row has somewhere honest to go. Work that arrives without a row and gets filed under tier N or
O is exactly how the 21–22 Aug inversion happened — the pile set the priority because nobody
re-asked what it was for. A tangent recorded here is fine. A tangent wearing a tier-N badge is
not.*

### Resolved and closed earlier — do not reopen without new evidence

K1 (neither monetary nor discount-rate — **discount-rate half withdrawn, C-035**), K4 (the GLM
null fails, but not by the proposed mechanism), K5 (the KVJ sign-inversion is unpublishable).

---

## 6. What we tried that did not work

Recorded so nobody repeats it.

- **Round 1 of the cascade research** was returned `materially_flawed` by all three verifiers — a third duplicated, one fabricated citation, a shale-gas figure wrong by an order of magnitude. The fix was a second round targeted at a completeness critique, not a rewrite.
- **Nine economic traditions** collapsed to roughly four findings on inspection; six cited the same 2011 BIS paper. Treat apparent convergence as suspect by default.
- **Analysis of Competing Hypotheses** was investigated as a research-management method and rejected on the evidence (C-011).
- **A SQLite claim/measurement database** was designed and rejected on measurement — the folder is an SMB mount and WAL silently refuses (C-012).
- **Prediction scoring** was specced and cut: ~24% detection power at N=6, needs N≈50–80. Predictions are registered for registration-time hygiene only.

---

## 7. For a reviewing agent

If you have been asked to **review** rather than extend this work, the highest-yield attacks,
in order:

1. **Check S1 against the SPV hole.** It is the assumption most likely to be wrong and it
   carries the most weight. If material capex sits in vehicles classified outside the NFC
   sector, the headline conclusion inverts.
2. **Attack W1's ceiling** (`2026-09-20-W1-The-Leak-Objection.md`). The $938.4bn is a CEILING: test whether the pension sectors were funding benefits or rebalancing into bonds. Z.1 carries their bond flows; the pairing was not done.
3. **Re-derive any number marked "own computation."** They were computed by one agent each.
4. **Look for false consensus.** Three occurrences so far. When you see N sources agreeing,
   check whether they are N sources.
5. **Check whether `CORRECTIONS.md` entries have actually propagated** — run `bin/check.sh --all`.
   The register exists because a refutation once sat in one file while the claim stood in three.

Do **not** re-derive anything in §2 without a specific reason; it has been verified once and
re-verification without cause is how context budget disappears.
