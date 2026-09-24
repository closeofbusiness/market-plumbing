# Market Plumbing

What moves asset prices, and where the money comes from.

This is a public research record. It is seeded from an ongoing programme that began with the Pozsar–Singh nonbank–bank nexus (collateral and shadow-money creation) and was widened, on 11 September 2026, to a simpler question: asset prices have run up, large sums are funding an AI build-out and an IPO boom, and both the price move and the money have to be accounted for.

Equities are ahead of the other markets. Rates, FX, and commodities are in scope and are updated on the same cycle. Where that work has not been done, the file says so.

## How to read it

1. [CHARTER.md](CHARTER.md) — the three questions, the markets in scope, and the rules.
2. [2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md](2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md) — the current answer, and the authority for what we believe. Every claim there carries a grade; the default is hypothesis.
3. [dossiers/](dossiers/) — one file per channel: hypothesis, status, evidence, what would change it, data used.
4. [CORRECTIONS.md](CORRECTIONS.md) — every claim the programme has killed, with machine-enforced bans on its phrasing. The designs that closed, including the limit on turning “money was present” into a causal price impact, are in the answer’s §4.
5. [monitor/DATA.md](monitor/DATA.md) — free series the live claims actually use, and when they print next. It is an extract: the live sources are `data/series.tsv` and `CALENDAR.tsv`.

Since 24 September 2026 the source programme’s full research record lives in this repository, and its answer note is the authority for “what we believe”. Third-party copyrighted or paywalled documents are summarised and cited, not copied; US federal public-domain documents are kept under `_research/primary_sources/` so the work can be reproduced.

## Update cycle

Keep this order. Do not start from a favourite channel.

1. **Prices.** Decompose the move. Equities: earnings versus the multiple, and whether valuation is cheaper money or a premium holding up against real yields and funding costs. Rates: carry, roll, the expected path of policy and inflation, versus term premium. Commodities: physical balance, inventory, curve shape, versus risk premium.
2. **Money, as measurement.** Who bought, against what net supply, after wrappers are classified — equities, duration, and commodity paper. Same denominators across sectors and cross-border legs, so a dollar, yen, or euro of hedged demand is not counted twice.
3. **Channels.** Size every path, including the ones that fail. New paths the evidence opens get added. Failures stay in the record.

Named stress cases rotate through the same three questions. They are not a separate encyclopaedia: AI funding and IPOs (equity); fiscal supply, QT/QE, and cross-currency basis regimes (rates and FX); inventory shocks, OPEC+ and metals supply, and commodity index or ETP demand waves (commodities).

## Rules that bind every file

Free data only. Rough bands over false precision. Every claim stays a hypothesis until tested. Attributions add up. Every purchase has a seller. Negatives stay first-class. Nothing is settled merely because it survived last month. Do not claim that FX, official buying, or financial commodity flows caused a yield or curve move. The attempt to turn “money present” into a causal aggregate equity-price impact closed on free data; that limit stays open in the corrections register until a better design exists.

## What this repository is not

Public visibility is not a copyright waiver. The programme’s own write-ups are under Creative Commons Attribution 4.0 International (see LICENSE). Third-party and paywalled documents are summarised and cited, not copied. The programme’s own write-ups are the text committed here.

The scripts are in `bin/`, and the gate is `bash bin/check.sh --all`. The monitor is `data/series.tsv` plus `CALENDAR.tsv`; [monitor/DATA.md](monitor/DATA.md) is an extract. Keys and material that must not be public are kept outside this repository.
