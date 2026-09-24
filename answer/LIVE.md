# Live answer

Status date: 23 September 2026 for the equity argument (the source answer note), with the series monitor pulled through 21 September and the print calendar touched 24 September. This file follows the charter’s update order. Grades are in [CHARTER.md](../CHARTER.md).

The default grade is **HYPOTHESIS**. A claim is stronger only where a grade is written next to it.

## 1. Prices

### Equities

**Earnings carried most of the recent US equity return. The multiple held while real yields rose.**

- Earnings share of the price move: **71.0% to December 2025, 82.3% to June 2026** [MEASURED; the two endpoints the decomposition actually computes]. The June figure is partly tax-assisted. Owner: `2026-09-11-P2a-Return-Decomposition.md`. Tax restatement: `2026-09-21-W3-Tax-Decomposition.md` — restating 2025 earnings at the 2015 effective rate moves the earnings share from 82.3% to **74.5%**.
- Of the earnings contribution, per-share accretion from a shrinking share count is **at most roughly a tenth to a sixth** of the price gain since 2015 [BOUNDED, one-sided, not a confidence interval]. Survivorship pushes the band up, so the truth sits below it. Owner: `2026-09-18-EPS-Split.md`.
- Depreciation-life extensions explain **5–11%** of six megacaps’ net-income growth. Owner: `2026-09-13-E2-Earnings-Quality-Useful-Lives.md`.
- December 2023 to June 2026, real yields **rose 0.34 points** while the earnings yield fell **0.14**. The multiple held. The “premium compressed” sentence is mostly the arithmetic mirror of that rate rise, not a second fact. The window compression stands; a level or constant-premium counterfactual does not. Owner: `2026-09-12-P2c-Rates-vs-Risk-Premium.md`.
- The move arrived as drift. Ordinary days carry the bulk. Owner: `2026-09-14-P5i-Event-Study-Result.md`.
- **Open inside this result:** whether what held the multiple up was cheaper risk or higher growth expectations. That split was withdrawn.

### Rates

**Open.** No carry / roll / expected-path / term-premium decomposition for US Treasuries, JGBs, or euro-area government bonds is in the source that this answer is taken from. Foreign official Treasury holdings are a measurement, recorded under money and under the cross-border dossier. They are not a yield decomposition, and they are not a claim that official buying moved the curve.

### FX

**Open as a price result.** There is no result here that an FX basis, a swap, or reserve recycling moved a yield or an equity multiple. Offshore-dollar stocks are a funding measurement. See the cross-border dossier.

### Commodities

**Open.** No physical-balance, inventory, or curve-shape decomposition for energy, metals, or softs is in the source. A commodity-ETF issuance line sits inside the US equity-instrument identity (about $60bn over 2024:Q1–2026:Q2 in the series monitor). That is a wrapper fact, not a commodity-market result.

## 2. Money, as measurement

### Equities

The line read as “corporate equity issuance” in the US Financial Accounts **counts ETF shares**. Over 2024:Q1–2026:Q2 the identity in the source answer is:

- ETF share creation **+$3,603.8bn**
- nonfinancial corporates **−$540.7bn** (this is the operating-company figure)
- total issuance **+$3,243.1bn**
- a derived “net of the wrapper” line **−$360.7bn**, which blends foreign and other financial issuers and is not itself the operating-company number

**Net new operating-company equity supply was negative.** Retirement on the window the enhanced accounts cover (2024:Q1–2026:Q1) was predominantly M&A: **M&A retirement $858.0bn against net retirement $679.1bn**. M&A more than accounts for the retirement. That is a published line, not a residual, and it is not “buybacks” by another name. A decade-long near-equality of repurchases and gross issuance was the wrong comparison: most of that gross issuance never touched the public float. Owners: `2026-09-15-ETF1-Identity-Net-Of-ETF.md`, `2026-09-13-S1-Supply-Decomposition.md`.

Roughly **three-tenths** of the wrapper is bond ETFs. An equity-instrument line is already pulling fixed-income plumbing into the equity measurement. Commodity ETPs are the same kind of wrapper problem; the commodity-fund issuance key in the monitor is the only figure carried, and it is small beside the equity and bond wrappers.

Who held the wrapper, same window [MEASURED, and not a proof of rotation]:

- ETFs **+$2,460.9bn**, mutual funds **−$2,009.0bn**. The offset is **81.6%**. Consistent with rotation. Not a measurement that the same dollars switched wrapper. That question is unsettled on free data.
- Pensions were net sellers on the directly reported lines (state and local defined benefit, federal, private).
- The household line is still a residual. No free split by legal entity.

The stock these flows sit against is the Financial Accounts equity instrument, not listed market cap. Revaluation in that identity is a residual (`change in level minus flow`) and includes other volume changes. Do not quote it as an independent price result.

### Rates, FX, and commodity paper

**Partial, and not a matched supply-demand table.**

- US bill supply, Treasury net issuance, Fed Treasury purchases, and money-fund Treasury flows are in the monitor. They are not yet a net-supply identity for notes and bonds beside official, dealer, and private demand, with one denominator.
- TIC July 2026 holdings (foreign official, Japan, China) are in the monitor. A holding change is not a cause of a yield move.
- JGB and euro-area government-bond net supply are **not in the source as a worked identity**. Stated in the programme brief, not yet tied to a source file.
- FX-hedged versus unhedged sovereign demand is likewise not a finished table. Offshore-dollar and FX-swap notionals exist as stocks in the monitor (`2026-08-30-N2a-Offshore-Dollar-Leg.md` and the series keys). They are not an attribution to a curve.
- Commodity paper versus physical supply is not built. Producer hedging, merchant books, managed-money, and index flows are named in the brief and are not yet tied to a source file, except the commodity-ETF issuance key above.

## 3. Channels

Sized, failed, or still open. Detail and the “what would change this” line live in [dossiers/](../dossiers/).

| Channel | Status on the equity window already studied | Owner |
|---|---|---|
| Fundamentals benchmark | Earnings did most of the work. Hypothesis, re-test on the next print. | P2a, P2c, EPS split, E2, W3 |
| Direct money creation | Weak positive association with equity buying. Not a funding ceiling. | `2026-09-14-A1-Money-Creation-Link.md` |
| Wholesale repo and shadow money | 2024 growth was a reverse-repo handoff, not new cash. Not ruled out as a ceiling over the full window. | `2026-09-15-N4-Scale-Timing-Bound.md` |
| Collateral re-use | Intensity did not rise. The dated step in the six-bank collateral stock is first half of 2026, after most of the price rise. | N4; `2026-08-30-D10-Reuse-On-The-Measured-Chain.md` |
| Passive and ETF structure | The wrapper is the issuance. The bid looks like rotation and is not measured as rotation. Causal price impact: closed. | ETF1; corrections register |
| Official-sector plumbing | The 2024 reverse-repo handoff into private repo is measured. | N4 |
| Cross-border and FX-funded demand | Holdings and offshore-dollar stocks measured. No causal yield or equity claim. | TIC note; N2a |
| Long-money holders | The AI debt that exists is held mainly by long money. | `2026-08-22-D2-Who-Holds-The-AI-Paper.md`; `2026-09-22-W2-AI-Paper-Composition.md` |
| AI funding | Mostly operating cash. The material financing innovation is off-balance-sheet leases. Oracle is the exception on cash versus capex. | F1; guarantee stack; W2 |
| IPO boom | Highly concentrated. About $112bn of new money in 2026 to the date of the note, about two-thirds one deal. | `2026-09-12-I1b-IPO-Prospectus-Facts.md` |
| Rates (UST, JGB, EGB) | Open as a price-and-money account. | — |
| Commodities | Open. | — |

Read together, the equity-window result is mostly negative on the original shadow-money and collateral hypothesis, and that negative is a result: the money that met the equity market was largely already inside the system. It does not say those channels never matter, and it does not zero them. N4 bounds them.

## What failed

Four free designs for an aggregate causal money-to-equity-price multiplier closed. They closed for different reasons: missing treatment data, arithmetic (a few basis points of signal inside about 111 basis points of daily noise), and demonstrated underpower. No scalar multiplier is carried. Full ledger: [corrections/REGISTER.md](../corrections/REGISTER.md).

## What is open

- Rates and commodities on the same three questions, including JGB and euro-area supply, cross-currency basis regimes, and commodity inventory and curve financing. These are stated as in-scope here. They are not yet tied to a finished source note.
- Whether the equity premium compression was risk or growth.
- A free split of the household equity residual.
- Revenue-recognition timing inside the earnings series.
- The lease stack as a fragility question, which is not the price question.
- Re-opening the causal equity bridge only on the numeric triggers already written down (not on a hunch). At the central borrowed multiplier the dividend-day design needs on the order of centuries of data; the mega-firm design needs on the order of a hundred more quarters. Neither is a rejection of the mechanism.
