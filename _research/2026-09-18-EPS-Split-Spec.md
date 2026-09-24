# EPS SPLIT — how much of "earnings did 70–80% of the work" is buybacks? (18 Sep 2026)

**Author:** Claude (supervisor). **Status:** SPEC, unrouted — the principal routes.
**Serves:** the canonical goal's price side, and the join between the answer's two halves.

## The question

`2026-09-11-P2a-Return-Decomposition.md` finds 70–80% of the S&P 500's price gain since 2015 is earnings growth.
It uses Shiller's **per-share** EPS (×2.89). Shrinking share counts raise EPS without raising profit. **No doc in
this project has split EPS growth into aggregate profit growth and per-share accretion** — P2a, E2 and P2b
contain no mention of share count, buybacks or stock-based compensation. That is the largest untested exposure
on the lead claim of `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md`.

In logs it is an identity: **Δlog EPS = Δlog aggregate earnings − Δlog shares outstanding.**

**This is an accounting decomposition, not a statistical test. No minimum-detectable-effect calculation applies**
(the CLAUDE.md MDE rule governs designs that estimate an effect against noise). Do not spend time on one.

## The trap — the data already on disk looks like it answers this, and it does not

`data/supply_decomp/fed_efa/equity-issuance-retirement-quarterly-historical.csv`, NFC, summed by calendar year
(checked by the supervisor 18 Sep):

| 2015 → 2026Q1 | $bn |
|---|---:|
| gross issuance | 6,623.3 |
| **repurchases** | **6,403.6** |
| M&A retirement | 4,748.4 |
| net | −4,528.6 |
| **repurchases − gross issuance** | **−219.7** |

**At the aggregate, buybacks are fully offset by issuance, and the whole net retirement is M&A** (57% of gross
retirement is repurchases, 43% M&A). **Do not read that as "buybacks did not inflate S&P EPS."** Gross issuance
is dominated by **private** placements — the record 2026:Q1 quarter was only 10.6% public — which never touch an
S&P 500 share count. The aggregate nets *public buybacks* against *private issuance*, and would show roughly zero
per-share accretion for the index when the true figure may be large. **Only constituent-level share counts
answer this.** (EFA's net column also does not reconcile with Z.1's `FU103164105.Q` — do not mix the two series.)

## Method

1. **Share counts, constituent-level, free.** SEC XBRL company facts for S&P 500 constituents:
   `us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding` (primary — it is what EPS divides by) and
   `dei:EntityCommonStockSharesOutstanding` (cross-check), annual 2015–2026. `data.sec.gov` needs no key; the
   User-Agent carrying the project address goes to **sec.gov hosts only** (CLAUDE.md working rules).
2. **Aggregate per-share accretion** = market-cap-weighted change in diluted shares across constituents,
   annualised and cumulated 2015 → 2026. Report it as a share of Δlog EPS (log 2.89 ≈ 1.061).
3. **Split gross buybacks from SBC dilution where XBRL allows:** `us-gaap:PaymentsForRepurchaseOfCommonStock`
   and `us-gaap:ShareBasedCompensation`. Gross buybacks that merely offset SBC do not shrink the count; state the
   offset explicitly.
4. **Headline in the answer's own terms:** "aggregate profit growth explains X% of the price gain; per-share
   accretion Y%", with a band.

## Threats — name each in the result

- **Survivorship:** current constituents over 2015–2026 overstate buyback intensity (survivors are the buyers).
  Report the bias direction even if it cannot be removed.
- **Index composition:** S&P EPS changes when constituents change, which is neither profit growth nor buybacks.
  Say how large it looks and do not fold it silently into either bucket.
- **Coverage:** report n constituents with usable share-count history ÷ 500, and name the megas if any are missing
  (the JVZ lesson: a panel missing the largest names is not a test of them).

## Do not say

- That buybacks did or did not inflate EPS **from the EFA aggregate** — see the trap above.
- Any scalar M, and any causal statement that buybacks *drove* prices (C-077, C-080). This splits an accounting
  identity; it attributes nothing.

## Rules

- **Run every command in the FOREGROUND and block on it.** No `nohup`, no `&`, no detached worker, no "I'll wait
  to be notified". A long XBRL pull goes in sequential slices, still in the foreground. Report only observed output.
- **State the denominator on every number.**
- **If your finding contradicts this brief, say so explicitly** — the supervisor's EFA reading above is itself an
  inference about public versus private issuance and could be wrong.
- **Never route around a refusal. No summary files.** We never pay for data (E-005).
- Hand over: `bin/check.sh --handover write <agent> eps-split <done|paused|blocked> "<X% profit / Y% per-share>"`
