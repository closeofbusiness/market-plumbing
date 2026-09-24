# HR — the household residual: we cannot say who bought the equity (14 Sep 2026)

> **[C-081] [C-083] CORRECTED 15 Sep 2026 — READ THIS BEFORE THE NUMBERS BELOW.** Z.1's "corporate
> equities" instrument **includes ETF shares as a wrapper layer on top of operating-company equity**.
> Over 2024:Q1–2026:Q2 **ETFs created $3,603.8bn of shares while nonfinancial corporates RETIRED
> $540.7bn net.** Issuance net of ETF shares is **−$360.7bn**. Of the wrapper, **bond ETFs were
> $1,065.0bn (29.6%)**. So any statement in this document that the equity base grew, that households
> absorbed net new *corporate* equity, or that the buying cannot be attributed, describes the ETF
> wrapper — not issuance by operating companies. Rebuild: `2026-09-15-ETF1-Identity-Net-Of-ETF.md`.
> See C-081 and C-083.
>
> **[C-084] LIT1, 15 Sep.** The literature recodes this plug by tax status (Rosenthal–Mucciolo:
> taxable ~27% / foreign ~42% of *their* look-through total in 2022) and subtracts nonprofits
> (Holmquist). It does not size PE funds vs personal trusts vs persons inside F51. Domestic
> hedge-fund equity is already a named F51 holder from 2012:Q4. Rebuild:
> `2026-09-15-LIT1-Residual-Literature.md`.



**Status: SUPERVISOR ARITHMETIC.** LIT1 returned 15 Sep. Ranked item 1 is closed.
Derived from `data/z1_equity_netbuyers/netbuyers_periods_2026Q2.csv`, no new fetching.

## The identity, and it closes exactly

Over **2024:Q1–2026:Q2**, holder side, Z.1 corporate equity:

| | $bn |
|---|---:|
| Households and nonprofit organizations | **+3,069.4** |
| Every other holding sector, combined | **+173.7** |
| **sum** | **+3,243.1** |
| net new equity issued, all sectors (issuer side) | **+3,243.1** |
| **identity gap** | **0.0** |

**It closes to zero because households is the residual.** The Fed computes the sector as what is left when
every measurable holder is subtracted from net issuance. That is not a criticism of the accounts — it is how
they are built — but it means the largest line in our attribution is a subtraction, not a measurement, and
it absorbs every measurement error in every other sector.

## The framing that matters, and it is starker than "44.6% of gross buying"

I have been describing this as 44.6% of *gross* buying ($3,069.4bn of $6,886.8bn). On a **net** basis it is
much worse:

> **Households absorbed 94.6% of all net new equity issued over 2024:Q1–2026:Q2.
> Every other holding sector combined absorbed 5.4%.**

So the honest statement of where this project stands on its own central question is: **we do not know who
bought essentially any of the net new equity.** Everything else we have measured — the passive bid, foreign
buying, pensions, insurers — nets out to almost nothing against issuance.

## Why the measurable sectors net to nearly zero

The large gross flows cancel:

| holder | $bn |
|---|---:|
| Exchange-traded funds | +2,460.9 |
| Mutual funds | −2,009.0 |
| Rest of the world | +1,213.9 |
| Nonfinancial corporate business | −582.7 |
| State & local DB pensions | −463.9 |
| Life insurers | −194.0 |
| Property-casualty insurers | −185.0 |
| Federal government pensions | −67.8 |
| State & local governments | −52.4 |
| Hedge funds (domestic) | −51.2 |

The passive bid (ETFs +2,460.9) is 82% cancelled by mutual fund selling. Foreign buying (+1,213.9) is more
than cancelled by the combined selling of corporates, pensions and insurers (−1,545.8). **What is left for
the residual to absorb is the entire issuance.**

## What this does and does not mean

- **It does not mean the Fed is wrong.** A residual is a legitimate construction and the accounts balance.
- **It does mean our attribution has a hole the size of the question.** Any statement of the form "X bought
  the market" has to survive the fact that the largest buyer is defined as everyone we could not measure.
- **It also means measurement error concentrates here.** If ETF or foreign flows are mismeasured, the error
  lands in this line, magnified.
- **Hedge funds were recently carved out** and are separately measured at −$51.2bn. Each such carve-out
  shrinks the plug and is evidence about what used to hide in it — worth tracking which came when.

## Open, and with two agents on it

1. **What is actually inside the sector** — the Fed's own construction, the nonprofit share, what has been
   carved out and when, and the Distributional Financial Accounts breakdown by wealth group. *If the top
   few per cent hold and are buying nearly all of it, the "retail investor" story is wrong.*
2. **An independent bottom-up retail estimate** from the public filings of the brokers who custody retail
   accounts — Schwab, Interactive Brokers, Robinhood, LPL and others. Worth having precisely because it does
   not share the Fed's method.


---

## What is actually inside the sector — answered, and one correction to me

**A CORRECTION TO WHAT I TOLD THE PRINCIPAL TODAY.** I said domestic hedge funds were "recently" carved out
of this sector. **They were carved out in 2012:Q3 — fourteen years ago.** Verified verbatim in the Fed's own
footnote to table S1M.b, fetched at source: *"Sector includes domestic hedge funds (through 2012q3), private
equity funds, and personal trusts."* The Technical Q&A explaining it is dated 2020, which is when the Fed
documented the change, not when it happened. Every quarter in our window is safely after the cutover, so no
number moves — but the framing "recent carve-out, more to come" was wrong.

**And the same footnote carries the bigger fact: PRIVATE EQUITY FUNDS ARE STILL INSIDE.** They have no
carve-out date and no separate holder line anywhere in the current corporate-equities table. **Private
equity funds' holdings of corporate equity are counted as "household" holdings today.** Personal trusts too,
named verbatim.

**It is a residual, and this is now established three ways:** my own arithmetic (the identity closes to
0.0bn, above); two Fed FEDS Notes describing the construction in prose; and the Financial Accounts Guide's
Series Analyzer, which returns the literal formula — total corporate equities minus eleven named sectors.
**The Series Analyzer URL does not reproduce for me** (it returns "Invalid URL" by two separate fetch
paths), so that third citation is **relayed unverified**. The conclusion does not depend on it.

**Nonprofits are 5.5%–8% of the combined household+nonprofit total** (2010–2025; 5.53% in 2025), from the
Fed's annual supplementary tables built on IRS Form 990 data. That is a parallel annual estimate for a
broader concept, not a split of this instrument — so roughly **$170–185bn of the $3,069.4bn is plausibly
nonprofit rather than household**, stated as a rough cross-concept figure.

## Who holds it — extreme concentration, unchanged for a decade

Distributional Financial Accounts, corporate equities and mutual fund shares, share of the household total.
**Recomputed by me from the pulled data; within 0.3pp of the agent's figures.**

| | 2015:Q1 | 2019:Q4 | 2023:Q4 | 2026:Q1 |
|---|---:|---:|---:|---:|
| Top 0.1% | 23.5% | 21.9% | 23.5% | 24.2% |
| Next 0.9% | 26.9% | 30.1% | 26.0% | 25.9% |
| Next 9% | 36.1% | 36.2% | 37.4% | 37.2% |
| Next 40% | 12.7% | 11.1% | 12.1% | 11.6% |
| Bottom 50% | 0.8% | 0.6% | 1.0% | 1.1% |
| **Top 1%** | **50.4%** | 52.0% | 49.5% | **50.1%** |
| **Top 10%** | **86.5%** | 88.2% | 86.9% | **87.3%** |

**The top 10% hold 87% of it and the bottom half hold 1%.** That is the distribution of the largest buyer
in the market.

## The nuance that stops this being an answer — and it is the important part

**Stable shares do not tell you who was BUYING.** The DFA publishes levels only, with no flow-versus-
valuation split by wealth group. And over 2023:Q4 → 2026:Q1 the DFA total rose $14,629bn while the
aggregate flow was $2,718.9bn — **so 81% of the level change is revaluation, not purchases.**

A flat ~50%/87% share is therefore equally consistent with two opposite stories: that the top 1% did nearly
all the buying, or that everybody held roughly steady proportions while the whole market re-priced. **The
data cannot distinguish them**, and anyone quoting the concentration shares as evidence about the marginal
buyer is over-reading them. This qualifies my own framing of the brief.

## The rough answer, with its assumption stated

Under E-005's standard — an estimate with a band beats withholding one — the best available apportionment
of the $3,069.4bn flow is by each group's average holding share. **This distributes an assumption about
behaviour, not a measurement:**

| group | rough share of the flow | $bn |
|---|---:|---:|
| Top 1% | ~50% | ~1,357 |
| Next 9% | ~37% | ~1,013 |
| Next 40% | ~12% | ~320 |
| Bottom 50% | ~1% | ~29 |

The assumption is that each group bought in proportion to what it already held. It is untested and it is the
weakest link here; treat the split as indicative of scale, not as a finding.

## Where this lands

**The residual's size is now well bounded and its two named contaminants are dated. Its composition beyond
broad wealth bands is genuinely unattributable with free data.** Concretely:

- ~$170–185bn is plausibly nonprofit.
- The remaining ~$2,885–2,900bn is households, personal trusts and **private equity funds**, in unknown
  proportions, distributed across wealth bands only by assumption.
- **Essentially none of it can be pinned to a named buyer type**, and the Fed's own documentation says
  private equity funds and personal trusts live in there.

The honest headline stands: **the largest buyer of US equity over 2024–26 is, in the official accounts, the
set of holders nobody measures.**


---

## The bottom-up cross-check: it cannot corroborate the Fed number, and that is the finding

Seven brokers' own SEC filings, client assets at 2026:Q2 (verified by me — my six-broker sum of $29,325bn
plus LPL's $2,562.7bn gives **$31,888bn**, matching the agent's ~$31.9trn):

| broker | firm's own metric | $bn |
|---|---|---:|
| Charles Schwab | Total client assets | 13,084.9 |
| Morgan Stanley WM | Total client assets | 8,084.0 |
| Bank of America / Merrill | Total client balances | 4,934.4 |
| LPL Financial | Total client assets | 2,562.7 |
| Raymond James | Client assets under administration | 1,922.4 |
| Interactive Brokers | Customer Equity | 930.3 |
| Robinhood | Total Platform Assets | 369.0 |
| **total** | | **31,887.7** |

**This is a lower bound on a different quantity, not a comparable.** Three reasons, all disqualifying:

1. **Fidelity and Vanguard are structurally invisible.** Neither is an SEC equity filer — privately held and
   mutually owned respectively — so no 10-K exists. Both are plausibly comparable to Schwab or larger.
   Wells Fargo Advisors, UBS Americas, Ameriprise and Edward Jones are also uncovered. Coverage is
   **roughly 30–50% of US retail-facing custody**, as a judgement not a measurement.
2. **Units do not match.** The Fed figure is an equity-only FLOW. These are all-asset-type STOCKS — cash,
   bonds, equity, alternatives together. Only Schwab discloses anything asset-class-based at all
   ("equity and other securities", ~40% of its total, and explicitly a mixed category). The others publish
   an advisory-versus-brokerage split, which is a **billing channel, not an asset class**.
3. **Growth at the two biggest movers is partly acquisition mechanics.** Schwab jumped 52% in 2020:Q4
   (TD Ameritrade) and Morgan Stanley 40% in the same quarter (E*TRADE); LPL has at least four M&A step
   changes; Robinhood redefined its metric in 2025:Q1 to add ~$41bn of assets it does not custody. Flagged,
   not smoothed.

## The trap the agent found and refused to walk into

Summing five brokers' **net new assets** over the *same* ten quarters as the Fed window gives **$2,650bn —
86% of the Fed's $3,069.4bn.** It looks like striking corroboration. **It is worthless, and the agent said
so rather than reporting it as a match.** Two reasons:

- **Net new assets is asset-GATHERING, not buying.** A client moving an existing IRA from Fidelity to Schwab
  counts in full as Schwab's net new assets while contributing **exactly zero** net new equity at the system
  level. Transfers between brokers net to zero system-wide; the Fed number does not contain them at all.
- **It excludes two of the seven brokers and all of Fidelity and Vanguard.** A number that reaches 86% of
  the target with most of the market missing is evidence of a units error, not of agreement.

**Do not put this ratio in the synthesis as corroboration.** Registered here so a future session that
rediscovers the coincidence knows it was already examined and rejected.

## A correction to my own brief

I told the agent that `data.sec.gov` XBRL companyfacts was "the efficient route" for this data. **It is not:
none of the seven firms tags client assets as a structured XBRL fact**, in any namespace including their own
extensions. The metric exists only in narrative press-release exhibits, so every figure above came from
parsing EX-99 text. Worth knowing before anyone briefs this kind of pull again.

## HR — the conclusion

**The residual is real, large and irreducibly unattributable on free data.** Three things are now settled:

- **It is arithmetically a plug** — the identity closes to 0.0bn, and the Fed's own construction subtracts
  eleven measured sectors from the total.
- **Its named contents include private equity funds and personal trusts**, verbatim from the Fed, with
  domestic hedge funds carved out back in 2012:Q3 and nothing carved since.
- **It sits on top of a genuinely large retail balance sheet** — at least $31.9trn of client assets at seven
  named brokers, with the two largest custodians invisible to public filings. So the plug is not a phantom;
  it is a real population we cannot measure the *flow* from.

What cannot be established with free data, and I do not expect to establish later: **who bought the
$3,069.4bn.** Not by wealth group (no flow/valuation split exists), not by institution (the two biggest
custodians do not file), not by buyer type (private equity and trusts are commingled in by design).

**The usable statement for the synthesis:** the largest buyer of US equity over 2024–26 is, in the official
accounts, the set of holders nobody measures — a population that holds 87% of its equity in the top tenth of
the wealth distribution and includes private equity funds by construction. Anything stronger than that is
over-reading.

**Method note for both (now answered):** a level rising because prices rose is not buying. Every number in this file is a
FLOW over the stated window. Do not compare it to a stock.
