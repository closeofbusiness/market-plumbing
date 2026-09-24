# E2 — how much of the earnings growth is a depreciation assumption? (13 Sep 2026)

**Status: CLOSED. The answer is 5-12%, and the main finding SURVIVES.** Ranked item 3. Data
`data/e2_useful_lives/`. Supervisor-verified 13 Sep.

## Why this was run

Every conclusion this programme has reached rests on REPORTED earnings, and the large technology companies
have repeatedly extended the assumed useful lives of their servers — which raises reported profit without
changing a dollar of cash. If a large share of "earnings explain 70-80% of the price rise" were an accounting
assumption, the main result would move. This was the cheapest test that could have overturned it.

## The answer

**Roughly 5-12% of these six companies' aggregate net income growth from FY2019 to FY2025/26 is attributable
to useful-life extensions rather than operations** — $21bn to $46bn depending on method.

| | each company's latest FY | aligned FY2019→FY2025 |
|---|---|---|
| reported net income growth, six companies | $422.32bn | $338.57bn |
| of which useful-life effect, conservative | $20.94bn | $20.75bn |
| of which useful-life effect, upper bound | $45.54bn | $39.13bn |
| **share** | **5.0% – 10.8%** | **6.1% – 11.6%** |

Denominator on every share: aggregate **reported** net income growth of the six named companies (Alphabet,
Amazon, Meta, Microsoft, Oracle, NVIDIA) from each company's own FY2019.

**Real, worth knowing, and not remotely large enough to overturn the earnings finding.** A modest secondary
factor, not the dominant one.

## The denominator caveat, which matters for how this is used

The 70-80% finding is about the **S&P 500**; this test covers **six companies**. These six are a large share
of the index but not all of it, and the useful-life issue is concentrated precisely in them — so this bounds
the effect where it actually lives, which is the right target. **It does not translate one-for-one into an
index-level correction, and must not be quoted as though it does.**

## A finding inside the finding: Amazon reversed

**Amazon SHORTENED the life of a subset of servers in FY2025, from six years back to five**, increasing
depreciation by $1.4bn and *reducing* net income by $1.0bn — disclosed by the company. The useful-life story
is therefore **not monotonically earnings-inflating**: at least one of the six has started unwinding it,
which is consistent with faster AI-era hardware turnover. Anyone arguing the extensions are a one-way
earnings-management ratchet has to deal with this.

## Verification I did myself

- **Alphabet FY2023 checked at source.** I fetched the 10-K (accession 0001652044-24-000022) and read the
  sentence: *"The effect of this change was a reduction in depreciation expense of $3.9 billion for the year
  ended December 31, 2023."* Matches the agent's figure exactly.
- **The FY2019 base reconciles.** The reported sum of $118.88bn ties to the six companies' individually known
  FY2019 net income to within rounding.
- **The share arithmetic reproduces** on both bases from the reported and restated growth figures.

## Method and its weak points, stated

Where a company disclosed its own first-year dollar effect it was used directly — **five of six do**, which
makes most of this sourced rather than modelled. Effects are chained across years and carried forward flat in
nominal terms, which **understates** later-year effects because the affected asset base keeps growing; a
scaled variant gives the upper bound. Both are in the CSV.

Two genuine weak points:
1. **Oracle discloses nothing.** Its one change (5→6 years, FY2025) carries no quantified effect in any of
   eight filings read, so its contribution is modelled, not sourced. A calibration check against Alphabet's
   disclosed figure showed this style of proxy understates by roughly half — so **Oracle's number is a floor.**
2. **Amazon's gap years** rely on carrying its own disclosed figures forward rather than a fresh estimate.

The agent found and fixed two sign-convention bugs mid-run and then validated the corrected model against
every company's own disclosed figures — reproducing Meta FY2021 at +$0.52bn against a disclosed +$0.516bn,
and Microsoft FY2021 at +$2.33bn against a disclosed +$2.3bn. That self-validation is why the output is
trustworthy; it is also a reminder that the first version of it was wrong.

## Consequence

**E2 is closed and the earnings leg of the argument stands.** Reported earnings for the megacaps are
inflated by an assumption change, by a measurable and modest amount. The finding that earnings — not
multiple expansion — did most of the work in the price rise is **not** overturned by it.
