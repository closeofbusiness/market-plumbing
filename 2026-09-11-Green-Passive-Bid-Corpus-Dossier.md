# Michael Green and the passive bid — what he has argued, from the podcast corpus (11 Sep 2026)

**Status: CLAIMS, not data.** Every number below is Green's (or a cited source's, as he relays it),
anchored to an episode. None is verified against a primary source yet — that is ranked item D-G in
`RESEARCH_STATE.md` section 5. Channel (d) of the goal (section 0.0); feeds explananda P and I.

**Provenance.** Extracted 11 Sep 2026 by a Sonnet agent from Martin's private Hermes podcast corpus,
read-only. Claim table: `_research/2026-09-11-Green-Claims.tsv` (38 claims, G-001..G-038). Raw
transcripts are deliberately NOT in this folder (external models read it); re-fetch by episode id.
The access recipe is kept outside this folder too.

**Supervisor verification (11 Sep):** five anchor quotes (G-001, G-009, G-012, G-013, G-019) re-read
verbatim at the cited lines, spoken by the cited label; the rosters of ep 2994 (SPEAKER_02 = Mike
Green, conf 1.00) and ep 4555 (SPEAKER_00 = Mike Green, conf 0.83) re-fetched — both carry the same
voice id (#1526), which corroborates the binding; G-013's "Tier 1 Alpha's models" checked at ep 4555
line 41, where Green says he left Simplify about a month earlier to launch Tier 1 Alpha Asset
Management. **So as of September 2026 Green is at Tier 1 Alpha, not Simplify** — older docs here that
say "Simplify" were right when written.

**Entry point since 11 Sep: `2026-09-11-Green-Substack-And-Ep61-Synthesis.md`**, which merges this dossier with his
17 Substack posts and the official Ep 61 transcript (the latter confirms all 10 ep-4555 claims verbatim).

**Relation to the earlier summary.** `Analysis/Input_Substrate_Forward_Thinkers.md` (section on Green,
as at 2 Aug) states his thesis, its testable pieces and the counter-arguments, with the
Gabaix-Koijen multiplier. This dossier is the episode-anchored layer under it. The passive-share
figures do not yet reconcile and must not be quoted as one number: ~45-47% "of the market" (G-001,
his estimate), ~65% of equity fund assets (G-004, his relay of Morningstar), ~55% of US fund assets
(the substrate). Three different denominators; resolving them is part of D-G.

---

# Mike Green / passive-bid extraction — dossier

Scope: Hermes podcast corpus, via its two read-only channels (the library dashboard and the frozen search CLI). Read-only extraction; no judgment on whether Green is right.

## (a) Denominators

**Path A candidate searches** (`GET /library?q=...`), each parsed for (date, show, title,
episode id, has_transcript):

| query | dashboard-reported matches | rows parsed |
|---|---|---|
| "Mike Green" | 28 | 28 |
| "Michael Green" | 78 | 78 |
| "Michael W. Green" | 69 | 69 |
| "Simplify Asset Management" | 43 | 43 |

Total rows across the 4 searches: 218. **Unique episodes after de-duplication by id: 141.**

Classification of the 141 unique episodes:

| class | count | notes |
|---|---|---|
| BILLED | 6 | 4555, 419, 445, 2994 (all confirmed with transcripts); 3126, 3128 (the "ATOMIQ LEVEL Live" event, no transcript for either) |
| SUBSTACK | 27 | his Substack RSS feed; listed in (g), not fetched, per instruction |
| FALSE-POSITIVE | 14 | fetched and grepped; "green" either absent or present but not referring to Michael/Mike Green |
| MENTION | 94 | of which **7 confirmed genuine** (fetched + verified), **87 unverified** (86 have a transcript but were not examined; 1 has no transcript at all) |

Transcripts fetched and saved: 4 BILLED (`transcripts/{4555,419,445,2994}.md`) + 21 MENTION
candidates (`mention_raw/*.md`: the 15-newest-first sweep + 6 confirmed via Path B). BILLED
episode pages (roster) fetched for all 6 BILLED ids, including the 2 without a transcript.
Total Path A HTTP requests this run: 35 (4 searches + 6 episode pages + 4 BILLED transcripts +
15 + 6 MENTION transcripts), each ≥1.5s apart. Total CLI calls: 4 (`search` for "passive
bid", "Mike Green", "Michael Green", "Simplify Asset Management"), each ≥3s apart.

**Mid-task correction, and how it changed the method.** The supervisor corrected the brief
mid-run: `/library?q=` full-text hits are single-word matches, not phrase matches, so a hit on
"Mike Green" can be a transcript that merely contains "Mike" and, separately, "green" — e.g. as
a chart color ("flip green"), a place-name substring ("Greensboro"), or unrelated biology
("red and green in every cell"). This was confirmed directly: of the first 15 MENTION
candidates fetched (newest-first), 7 had no occurrence of "green" at all, and a further 7 had
the word but not about a person named Green — leaving only 1 genuine mention in that batch of
15. Per the correction, the method changed to: (i) never call a row MENTION until its transcript
is fetched and grepped for "green"; (ii) use Path B's literal-phrase search (which marks
`>>phrase<<` in returned excerpts, with genuine hits scoring roughly 8.6-14.3 versus ~0.65-0.78
for semantic noise with no phrase match at all) for topical discovery. That second step
recovered 6 more genuine MENTION episodes (2992, 2993, 136, 2991, 2971, 2969) that were real but
outside the newest-15 window, none of which were newer than the cap would have reached on its
own. The remaining 87 MENTION candidates were not examined and are reported, not guessed at, in
`candidates.tsv`.

**Contradiction vs. the supervisor's pre-verified facts, flagged per the rules:** the brief
states `/library?q=Michael+Green` returns "~100 rows." A fresh fetch this run returned **78
matches**, parsed as 78 rows, not ~100. I re-ran the query once (no caching); the discrepancy is
reported as observed, not resolved — it may reflect corpus drift since this morning's
verification or an imprecision in the original "~100."

## (b) Green's passive-bid argument, reconstructed (in these words, not his)

Green's starting claim is that a large and growing share of demand for equities and bonds is
mechanical rather than price-sensitive. He puts the passive share of the market at roughly
45-47% by his own estimate (G-001), a number he sets against Morningstar data showing under a
third of mutual-fund/ETF assets are actively managed, with passive running about 65% on the
equity side and approaching 40% on fixed income (G-004). His mechanism is that a fund is a
"liquidity concentration vehicle": it pools contributions — a 401k paycheck, a target-date
rebalance, a retirement default — that carry no view on whether now is a good time to buy, then
discharges that pooled liquidity into individual securities in proportion to index weight
(G-011, G-021). Because that flow doesn't discriminate between securities the way a
valuation-driven buyer would, he argues it mechanically explains things usually credited to the
Fed, including the persistent rally and the widening gap between mega-caps and everything else
(G-002). He attributes mega-cap outperformance specifically to exposure to this passive bid — a
mechanism distinct from, though correlated with, the academic "size factor" — citing outside
work on market-making and substitutability in very large names (G-005, G-030). He extends the
same logic to bonds, estimating 25-35% of incremental bond-market flow is now passive and
price-insensitive (G-016), and to post-drawdown rebounds via target-date rebalancing (G-022,
G-025). On the other side of the trade, he cites outside research concluding the main sellers to
passive buyers are corporate insiders (G-009). He ties the mechanism to demographics: the shift
from defined-benefit to defined-contribution plans forces individuals to over-accumulate against
unknown lifespan risk (G-025), and typical retirement withdrawal rates have fallen from about 4%
to about 2%, both of which he says support prices now but will reverse as the retiring
population becomes a net seller (G-026). Leverage compounds it — 2x/3x and single-stock ETFs
reintroduce fund-level leverage last seen in the 1920s (G-008) — and, at the extreme, rebalancing
inside such products can itself dominate a stock's daily move: he estimates roughly half of the
daily price movement in 2026's semiconductor melt-up names came from mechanical ETF flow, against
a "normal" passive bid he sizes at about $300 million/day for the largest stocks (G-012, G-013).
He treats the unwind this could cause as a real but still-unproven hypothesis (G-003), pointing
to 2022 — when rising mega-cap correlation flipped the effect into reverse and the largest names
fell hardest — as the nearest precedent (G-007). His recurring illustration for why the marginal
buyer won't simply refuse to pay up is that a mandated allocator who "cannot hold cash" has no
price at which they stop buying (G-019, echoed at G-036 by his colleague Harley Bassman
independently endorsing the framework).

## (c) Numbers he uses

| number | what it measures | as-of (episode date) | his stated source | claim_id |
|---|---|---|---|---|
| ~45-47% | passive share of the market | 2025-01-27 | his own estimate/models | G-001 |
| <33% | share of mutual fund/ETF assets actively managed | 2025-01-27 (citing YE-2024 data) | Morningstar analysis | G-004 |
| ~65% | passive share, equity mutual funds/ETFs | 2025-01-27 (citing YE-2024 data) | Morningstar analysis | G-004 |
| ~40% | passive share, fixed-income mutual funds/ETFs | 2025-01-27 (citing YE-2024 data) | Morningstar analysis | G-004 |
| ~40% | mutual funds + ETFs as share of all managed assets | 2025-01-27 (citing YE-2024 data) | Morningstar analysis | G-004 |
| $1 in -> ~$2 invested | leverage multiplier inside levered ETFs | 2025-01-27 | his own characterization, uncited | G-008 |
| ~$300 million/day | "normal" passive bid, largest-cap stocks | 2026-09-08 | Tier 1 Alpha's own model | G-012 |
| ~$3 billion/day | peak single-stock (Micron) inflow, 2026 melt-up | 2026-09-08 (describing 2026) | Tier 1 Alpha's own model | G-012 |
| ~50% | share of daily price move from mechanical flow (melt-up names) | 2026-09-08 | Tier 1 Alpha's own model | G-013 |
| ~150%/year | required index return for 3x-ETF breakeven at observed volatility | 2026-09-08 | his own calculation | G-014 |
| $2bn/mo -> $4bn/mo | US Treasury debt buyback program size | 2026-09-08 | his own account of a Treasury announcement, uncited | G-015 |
| 25-35% | passive share of incremental bond-market flow | 2026-09-08 | his own ("Tier 1") work, uncited | G-016 |
| ~3,500 | ETFs tracked in his firm's database | 2026-09-08 | Tier 1 Alpha's own database | G-020 |
| ~1,200-1,300 bps/yr* | "passive factor" excess performance vs. valuation benchmark | 2025-11-13 | "my math" — his own model, uncited | G-029 |
| up to 2x | benchmark volatility permitted under the SEC "derivative rule" | 2025-11-13 (describing Sept 2020 rule) | his own description of the rule, no document cited | G-031 |
| up to $10,000 (hypothetical) | gold price absent Bitcoin-related retail diversification | 2025-11-13 | "my calculation" — his own, uncited | G-033 |
| $70bn net cash -> ~$30-40bn net debt | Meta balance-sheet swing | 2025-11-13 | none given; his own "rough estimate" | G-034 |

\* Heard/transcribed as "12 to 1300"; almost certainly an ASR rendering of "1,200 to 1,300" — flagged, not silently corrected, in claims.tsv.

No claim above carries a source beyond Green's own models/estimates except the Morningstar
citation (G-004) and the unnamed academic papers he references by author only (Valentin Haddad,
G-005; a 2025 paper by "Coimbra" in the Financial Analysts Journal, cited in claims.tsv as
context for G-025; and a paper he calls "Who Clears the Market When Passive Trades?", G-009) —
none of which were independently retrieved or checked in this task.

## (d) ETF creation/redemption, AI funding, IPOs

**ETF creation/redemption:** Green does not, in the material examined, describe the
authorized-participant creation/redemption arbitrage mechanism itself. What he does discuss is
adjacent: the 2019 "ETF rule" and September-2020 "derivative rule" that he says enabled the boom
in active and 2x/3x-leveraged ETFs (G-031); leveraged ETFs' need to rebalance daily, which forces
buying/selling with no new investor money ("endogenous liquidity") (G-014); and a "multiplier"
effect he attributes to the ongoing conversion of end-of-day-settled mutual funds into
continuously-traded ETFs (G-017).

**AI capex funding:** no direct claim about how AI-related capital spending is financed
(debt vs. equity vs. off-balance-sheet) was found. The closest adjacent material is (i) a
balance-sheet observation about Meta swinging from ~$70bn net cash to an estimated ~$30-40bn net
debt (G-034, episode 445) and (ii) a psychological analogy in episode 4555 comparing "total
addressable market for AI" reasoning to prior bubble narratives ("it's different this time"),
which is rhetorical framing rather than a testable funding-mechanism claim and was not made into
a numbered claim.

**IPOs:** covered directly — Green argues passive vehicles cannot bid on a name until it joins an
index, which he says is why private equity cannot get portfolio companies to a conventional IPO
and why direct listings/SPACs have grown as workarounds, widening the gap between public and
private valuations (G-006).

## (e) Counter-arguments and other reactions

No genuine rebuttal of Green's thesis was found in the material examined. Hosts across all four
BILLED transcripts treat the passive-bid framework as established and press for elaboration or
boundary conditions rather than disputing it. The closest to pushback is Bill Fleckenstein
(SPEAKER_01, roster-confirmed, conf 0.97) in episode 2994 asking whether the market could grow
large enough that "the passive bid wasn't enough to hold it up" — a question about the theory's
limits, not a challenge to it.

Among MENTION episodes (third-party statements about Green, not his own claims — see G-035 to
G-038): a Forward Guidance speaker credits the concentration thesis as vindicated ("Mike Green's
been right," G-035); Green's Simplify colleague Harley Bassman independently endorses the
framework's relevance to bond markets (G-036); a Grant Williams Podcast speaker frames Green's
recent conversations as being about "index kings" plus private-equity concentration, drawing a
parallel to 1980s Japanese bank valuations (G-037); and, notably, one speaker explicitly
distinguishes their own broader "flywheel reversal" speculation from Green's argument by noting
it "doesn't necessarily have to be passive" (G-038) — useful as a boundary marker on what Green's
argument specifically is (a passive-flow mechanism) versus is not (any capital-appreciation
reversal generally).

## (f) Attribution caveats

- Of the 4 BILLED episodes with a transcript, only **2994** and **4555** have inline `[Speaker
  NN]` tags in the saved transcript file that can be bound to the episode-page roster
  (SPEAKER_02 = Mike Green, conf 1.00, in 2994; SPEAKER_00 = Mike Green, conf 0.83, in 4555).
  Claims from these two are attributed to "Mike Green" directly.
- **419** and **445** are different: the episode page for 419 reports a normal roster
  (SPEAKER_02 = Mike Green, conf 0.78), but the *downloadable transcript.md file itself carries
  no `[Speaker]` tags at all* — so there is no line-level label to bind that name to. 445 has no
  diarization at all ("0 speakers" on the episode page) and its transcript.md is one unlabeled
  block of text. Per the non-negotiable attribution rule, every claim sourced from 419 or 445 is
  attributed to "unnamed speaker in episode {id}," with a note that the content directly follows
  the host's on-air question to the billed guest and is phrased in the first person — a strong
  contextual signal, but explicitly not turned into an attribution.
- **3126** and **3128** (the "ATOMIQ LEVEL Live" event, billed by title, catalogued respectively
  under Green's own Substack feed and under Marvin Barth's show) have no transcript at all; no
  claims could be extracted.
- For the 7 confirmed genuine MENTION episodes, step 3 of the brief calls for fetching the
  transcript only, not the episode page — so no roster exists to confirm even the *other* named
  speakers (e.g., "Harley Bassman" in 2969 is an in-dialogue self-introduction, not a
  roster-bound identification).
- "12 to 1300 basis points" (G-029) is reported as heard; it is very likely an ASR
  mis-transcription of "1,200 to 1,300."

## (g) Substack rows (titles only, not fetched)

16 essay rows (of 27 catalogued) from the show "Michael W. Green (Yes, I give a fig... thoughts on markets from Michael
Green)". The other 11 rows are account notifications (verification codes, billing and subscription notices, a welcome email), EXCLUDED as personal data. Also excluded: 3126, the live-video event catalogued under the same feed but classified
BILLED — see section (f)):

| id | date | title |
|---|---|---|
| 4476 | 2026-09-06 | The Quiet Turning |
| 4236 | 2026-08-30 | The Vibecession Was Real |
| 3963 | 2026-08-23 | Great, Scott... |
| 3855 | 2026-08-19 | And Get What You Deserve |
| 3857 | 2026-08-19 | Sometimes, You Get What You Need |
| 3755 | 2026-08-16 | Anchors Aweigh, My Boys |
| 3526 | 2026-08-09 | It's Time to Complicate |
| 3587 | 2026-08-02 | Maid in Japan |
| 3247 | 2026-07-26 | A Semi-Theory of Almost Everything |
| 2773 | 2026-07-12 | You Can Lead a Horse to Water |
| 2530 | 2026-07-05 | The Verb |
| 2294 | 2026-06-28 | A Token China Shock |
| 1998 | 2026-06-21 | Rinse, Warsh, Repeat |
| 1537 | 2026-06-14 | Size Does Matter |
| 1963 | 2026-06-07 | xAIr Supply |
| 350 | 2026-05-31 | Probably not... |
