# W1 — the leak objection, quantified (20 September 2026)

**Status: RESULT.** Principal's wave item W1. The objection had stood as *"UNTESTED — and it is the
load-bearing objection to the whole circuit thesis"* (§4) and *"Nobody has quantified it"* (§5 standing
item 8) since 22 August. Data: `data/z1_equity_netbuyers/netbuyers_periods_2026Q2.csv`, period `2024-latest`.

> **ATTACKED 21 Sep and the ceiling TIGHTENED — `2026-09-21-W3-Tax-Decomposition.md` Task 2.** Pairing these five
> sectors' equity sales against their Z.1 debt-security acquisitions over the same window bounds bond rebalancing at
> **$680.5bn of the $938.4bn (72.5%)**, tightening the ceiling to **~$258bn**. Read it as the interval narrowing, not as
> this document being 3–4× too big: `min(sale, purchase)` bounds one recycling route and measures none of it, and
> **no floor has been established** (C-096). The caution below — *ceiling, not a measured leak* — still governs both numbers.

## The objection, as the file states it

> Money spent on an existing asset reaches a seller who can spend it on goods. Candidates: low MPC at the
> top (Mian–Straub–Sufi), non-consuming buyers, credit extinguished on resale.

## First: its target is already dead, and §4 had not caught up

§4 listed what dies if the leak turns out large: **"K1, and any essay built on the two-circuits idea."**
But §3 records **K1 as RESOLVED — NEITHER**, with the circuit account failing on three independent
observables. The objection was still being carried as load-bearing for a thesis the project had already
retired. That inconsistency is corrected in §4 and §7; the quantification below is worth having anyway,
because the leak bears on any future fragility section and because it was never done.

## The arithmetic ceiling — most of the buying could never leak

Over 2024:Q1–2026:Q2 the buying sectors paid **$6,886.8bn**. That money went to two different places:

| destination | $bn | can it leak to goods? |
|---|---:|---|
| **Sellers of existing shares** | **3,643.7** | Yes — this is the whole of what the objection can touch |
| Issuers of new shares | 3,243.1 | No — this is new equity, not a sale by a holder. Per ETF1 it is mostly the ETF wrapper |
| **total** | **6,886.8** | ties to C-080: 6,886.8 − 3,643.7 = 3,243.1 |

**So 47% of the purchase flow cannot leak by construction.** Any leak estimate that starts from the
purchase flow rather than the seller-side flow is too big before behaviour is considered at all.

## Second: most of the seller side is a wrapper switch, not cash leaving

| net seller, holder side | $bn |
|---|---:|
| Mutual funds | 2,009.0 |
| Nonfinancial corporate business | 582.7 |
| State and local government employee DB pensions | 463.9 |
| Life insurance companies | 194.0 |
| Property-casualty insurance companies | 185.0 |
| Federal government pension funds | 67.8 |
| State and local governments | 52.4 |
| Hedge funds (domestic) | 51.2 |
| Private pension funds, including 403(b) | 27.7 |
| Security brokers and dealers | 9.5 |
| Closed-end funds | 0.5 |
| **total paid to sellers** | **3,643.7** |

**Mutual funds are 55% of the seller side on their own — and ETFs bought $2,460.9bn over the same window,
122% of the mutual-fund leg.** That is the rotation already established in S1, seen from the sell side: a
household switching from a mutual fund to an ETF shows up here as a $1 sale and a $1 purchase, and no cash
leaves the market. Treating the mutual-fund line as a withdrawal would double-count the rotation.

## What is left is the retirement and insurance system

| | $bn | share of seller side | share of all buying |
|---|---:|---:|---:|
| **Pension + insurance block** | **938.4** | **25.8%** | **13.6%** |
| annualised over ten quarters | **375 / yr** | | |
| residual (corporates, governments, hedge funds, dealers) | 696.3 | 19.1% | 10.1% |

These five sectors are the only net sellers whose outflows are **contractual payments to households**. They
are the identifiable leak channel, and they are the mirror of RET1: the retirement system stopped being a
net contributor in 2013, and here it is on the other side of the trade — **the marginal seller of US equity
over this window is the retirement and insurance complex, and the marginal buyer is the household sector
directly.**

## Verdict

**The objection is answered at the level it was posed, and it does not threaten the current answer.** The
leak has an arithmetic ceiling of 53% of the buying flow, most of that ceiling is a fund-wrapper rotation
rather than cash leaving, and the identifiable contractual channel is **$938.4bn, about a quarter of the
seller side**. Of the three defences the file named, this pass supports the second — **non-consuming
sellers** — and tests neither of the others.

## What this does NOT establish, and must travel with the number

1. **$938.4bn is a ceiling on that channel, not a measured leak.** A pension selling equities may be
   **rebalancing into bonds**, in which case the cash never leaves the asset circuit at all. Z.1 carries the
   pension sectors' bond flows; pairing them is the obvious next step and was not done here.
2. **No MPC is applied.** We hold no marginal-propensity estimate, so nothing here converts the ceiling into
   consumption.
3. **No consumption denominator.** `data/series.tsv` holds no PCE, GDP or income series, so the leak is
   stated against flows we measured and **not** as a share of goods demand. Do not quote it as one.
4. Low MPC at the top, and credit extinguished on resale, remain untested.

## Do not say

- That the leak objection is untested, or load-bearing for the circuit thesis (C-094).
- That $938.4bn leaked into consumption. It is a ceiling on one channel, before rebalancing and before MPC.
- Any leak figure computed on the $6,886.8bn purchase flow rather than the $3,643.7bn seller-side flow.
