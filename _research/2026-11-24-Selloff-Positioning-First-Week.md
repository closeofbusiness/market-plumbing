# The November 2026 sell-off in the futures data: the first week (10 to 17 November)

24 November 2026. This scores the secondary-window lines of the pre-registration
([version 2](2026-11-24-Selloff-Positioning-Preregistration.md), committed before the data was pulled). Script:
`bin/selloff_positioning.py`; outputs in `data/selloff_positioning/`. The supervisor re-read the S&P 500 and VIX rows
from the CFTC API, and they matched. The primary window (10 to 24 November) is scored on 30 November.

## What the futures data shows for the first week

The first week covers the start of the fall, not its worst days (18 to 20 November).

| line | change, contracts | rank since 2018 | prediction | result |
|---|---|---|---|---|
| P1s Leveraged Funds, E-mini S&P 500 net | **+68,082** (short cut from −303,060 to −234,978) | 91st percentile, High | sold (Low) | **wrong**: they bought |
| P3s Leveraged Funds, E-mini Nasdaq-100 net | **−24,895** | 1st percentile, Low | sold (Low) | **right** |
| P4 Leveraged Funds, VIX futures gross short | **+30,886** (96,310 to 127,196) | the largest one-week rise since 2018 (no-expiry weeks) | short cut (Low) | **wrong**: they added short volatility |

**Who sold, and who bought, in the first week:**
- **Nasdaq-100.** Leveraged Funds sold; Asset Managers (+10,115, 93rd percentile) and Non-Reportables (94th) bought.
- **S&P 500.** The broad index went the other way. Leveraged Funds bought back part of their short. Dealers (−52,087) and
  Asset Managers (−19,081) cut, neither unusually.
- **Pattern.** Selling the technology index while covering the broad one is the shape of a trade against AI stocks
  specifically, not a general cut in equity risk.
- **The VIX.** Leveraged Funds sold volatility as the VIX rose: their net position went from −34,762 to −72,916 (0.2nd
  percentile). Dealers and Asset Managers bought it from them (99th and 93rd percentiles).
  - That leaves a large short-volatility position in place going into the spike to 40 on 20 November.
  - Whether it was then covered is not visible yet. The November VIX contract settled on 18 November, inside the
    primary window, so the pre-registration bars a P4 verdict there.

**Treasuries (no verdict for this window).** Leveraged Funds *added* to their Treasury shorts in the first week:
- 10-year note: gross short +134,007 contracts, 98th percentile.
- Ultra bond: gross short +54,928, above the 99th percentile.

The short behind the basis trade grew into the sell-off; it was not unwound.

**Yen.** Nothing unusual:
- Leveraged Funds' yen net: −6,935, 20th percentile.
- The H.10 yen rate: 158.76 per dollar on 10 November, 159.27 on 17 November, 158.76 again on 20 November. Through
  20 November the yen did not strengthen, which is what a yen-funded unwind would need. P5a is scored on the 24 November
  rate.

**Japan's weekly flows (Ministry of Finance, descriptive).** In the week of 8 to 14 November, Japanese residents:
- were small net buyers of foreign equity (¥363bn);
- were small net sellers of foreign long-term bonds (¥441bn).

This is no sign of repatriation. The week of 15 to 21 November publishes on 26 November.

## What this changes

- **The equity seller in futures is not the broad "leveraged amplifier" first proposed (P1s wrong).** In the first week,
  Leveraged Funds:
  - sold the Nasdaq-100;
  - covered S&P 500 shorts;
  - sold volatility.

  The futures market priced a fall in AI stocks, not a general de-risking.
- **The short-volatility build-up is the new finding.** It is a plausible amplifier of 19 to 20 November, if those shorts
  had to be bought back. It is untested until the 24 November report, and then only around the expiry.
- **Every line reads futures only, by trader class.** Positions in cash shares, ETFs and options are not seen.

## Next

On 30 November, after the CFTC release (3:30 p.m. ET) and the H.10 (4:15 p.m. ET): run `fetch`, then `build`, and score
P1, P2, P3, P5a, P5b, P6 and the seller rule. A primary-window miss is INCONCLUSIVE, as pre-registered.
