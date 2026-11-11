# Pre-registration LE1: the 5 Nov 2026 equity sell-off in tri-party term repo (supervisor, 6 Nov 2026)

*Written and pushed before any OFR print dated after 4 Nov 2026 was read. Prints lag two business days, so the 5 Nov print is due about 9 Nov. Machinery and series as in g16 ([spec](2026-11-02-Term-Repo-Turns-Spec.md)); a builder script follows before the gate, also blind.*

## Why this event, and why this measure

On Thu 5 Nov 2026 the S&P 500 closed at 7,353.73, down 334.89 points or 4.36%. The supervisor checked this on the Fox Business market page, fetched 6 Nov. Grok's scout (fenced, read and web only) puts it as the worst day since 4 Apr 2025 (CNBC). It is a one-day stress event that came before the data recording it.

Of the programme's measures, a daily tri-party spread fits the event best:
- it is daily;
- it is free;
- its machinery already exists and has been checked independently (g16);
- its 5 Nov print is not yet public.

The other candidates were weighed with Gemini 3.8 Flash High (publication map) and Grok (literature). The list is at the end of this note.

**Selection is stated, not hidden.** The event was chosen because it was large. The repo response is unseen, and no direction is predicted.

## The registered statement

Its SHA-256 is `fcdd50cc04817ddcb8b990bb3b06986e0db821b4db6205a698a3dcd7d34c070e` (1237 bytes, LF line ends, final newline). The block below is verbatim:

```
LE1|live event: the US equity sell-off of Thu 5 Nov 2026 (S&P 500 -4.36% close to close)
SERIES|OFR tri-party, Fed trades excluded, preliminary: REPO-TRIV1_AR_B27-P (2-7 day) and REPO-TRIV1_AR_OO-P (overnight/open)
S|S(t)=100*(B27(t)-OO(t)) in basis points, start date t
EVENT|t*=2026-11-05
CONTROL|C=2026-11-02,2026-11-09,2026-11-10,2026-11-12,2026-11-13,2026-11-17,2026-11-18,2026-11-19,2026-11-20,2026-11-23; any date in C without both prints is dropped and named; fewer than 7 left means NO READING
EXCLUDED|11-03 election day; 11-04 refunding statement; 11-05 and 11-06 event; 11-11 holiday; 11-16 coupon and refunding settlement; 11-24 onward (a 2-7 day loan can cross the 30 Nov month-end)
E|E=S(t*)-median(S over C)
BAND|for each c in C: e(c)=S(c)-median(S over C without c); lo=min e(c), hi=max e(c)
LABEL|ABOVE if E>hi and E>0; BELOW if E<lo and E<0; else INSIDE; two-sided, no direction predicted
GATE|2026-11-27T20:00Z; before it no print dated after 2026-11-04 is read
DESCRIBED|each leg on t* and on 2026-11-06; E for 2026-11-06 against the same band; tri-party volumes; a bill-settlement-day-only control
CANNOT|why; whether lenders charged for risk; anything about the election, the refunding or other repo segments; n=1
```

## What it cannot say

- **Why.** A wider or narrower spread can come from either leg, from collateral mix or from which dealers borrowed.
- **Anything about the election (3 Nov) or the refunding (4 Nov).** Both fall in the same week, and their days are excluded from the comparison days, not controlled for.
- **"No stress."** INSIDE means inside the range of ten ordinary November days, in one spread, on one day.

## Considered and not registered

| measure | 5 Nov data public | why not registered |
|---|---|---|
| SOFR, TGCR, Fed reverse repo, sponsored repo | already, 6 Nov | read before any statement could be written; described only |
| 10y and 30y yields, swap spreads | already | same |
| CFTC futures positions (week to Tue 10 Nov) | 13 Nov | the week also holds the 9, 10 and 12 Nov auctions; no clean comparison weeks |
| H.8 bank lending to nonbanks (Wed 11 Nov) | 20 Nov | a week-average stock that also holds the election and the refunding |
| money-fund repo lending (OFR monitor) | month-end holdings | the November month-end file mixes the whole month |
| cross-currency basis (swap tape) | 13 Nov | the tape has no daily one-week to three-month tenor; the page calls its quarter-end table descriptive |

The 4 Nov refunding pre-registration (CALENDAR) scored separately:
- the 10y moved −5 bp and the 30y −4 bp, both inside ±8;
- that is no supply-effect reading, and the session was declared unclean in advance.

## Amendment LE1-A (6 Nov 2026, same day, still blind)

Grok attacked the block above the same day. Its review, verbatim, is in [the attack note](2026-11-06-Grok-LE1-Attack.md). Its main points held when the supervisor checked them:
- **5 Nov is a bill-settlement Thursday.** Treasury's tentative auction schedule shows the 6-, 13- and 26-week bills settling that day.
- **The comparison days were a poor match.** They mix settlement, auction and holiday-bridge days, and nine of the ten fall after the event, so an after-effect of the event would end up in the baseline.
- **2 Nov had already printed.** Its print was due on 4 Nov, before LE1 was written.
- **The band is weak.** Even with no event effect, a day falls outside it about 12% of the time (4/33 under a uniform null).
- **The E>0 and E<0 clauses do nothing.**

**What the supervisor checked on pre-event data.** Do bill settlements move this spread? On the 155 mid-month days of the 20261103 vintage, the median S is 5bp on settlement days and 5bp on other days. LE1-A therefore compares 5 Nov with earlier bill-settlement Thursdays, chosen by the calendar rule below. Their spreads were already in the repository, and the supervisor saw them before writing this block. The 5 Nov value is still unread.

**LE1's label is withdrawn. LE1-A is the scored statement.** Its SHA-256 is `bc39ff240caa0eac796fbed12075ea68ae1f1dde30ee814a1ef884ec6011e1ca` (2014 bytes):

```
LE1-A|amendment of LE1 (block sha fcdd50cc), written 6 Nov 2026 before any OFR print dated after 2026-11-04 was read; LE1's label is withdrawn and LE1-A is the scored statement
SERIES|as LE1: OFR tri-party, Fed trades excluded, preliminary: REPO-TRIV1_AR_B27-P and REPO-TRIV1_AR_OO-P; S(t)=100*(B27(t)-OO(t)) bp
EVENT|t*=2026-11-05 (a Thursday settling the 6-, 13- and 26-week bills; the day after the refunding statement; two days after the election)
BASELINE|B = the 25 pre-event Thursdays from vintage 20261103 (data/term_repo_turns/daily.csv) with: day of month 5-24; bill settlement; no coupon settlement; no FOMC effective date in (t,t+7]; no early close; not within one calendar day of a federal holiday; not within three calendar days after an FOMC decision day. Dates: 2025-08-14,2025-08-21,2025-10-09,2025-10-16,2025-11-06,2025-11-13,2025-11-20,2025-12-18,2026-01-08,2026-02-05,2026-02-12,2026-02-19,2026-03-05,2026-04-09,2026-04-16,2026-05-07,2026-05-14,2026-05-21,2026-07-09,2026-07-16,2026-08-06,2026-08-13,2026-08-20,2026-09-24,2026-10-08
BAND|S over B runs from 3 to 9 bp (median 5); these values were read before this block was written
LABEL|ABOVE if S(t*)>9 (10 bp or more); BELOW if S(t*)<3 (2 bp or less); else INSIDE; two-sided; if t* were exchangeable with B the chance of a non-INSIDE label is at most 2/26
VINTAGE|score on the first fetched vintage holding 2026-11-05; never rescored on a later vintage; a null on either leg means NO READING
GATE|2026-11-10T20:00Z
DESCRIBED|each leg on t*; S on 2026-11-06; LE1's original median and band (withdrawn: its control days mix settlement, auction and holiday-bridge days, nine of ten fall after the event, and 2 Nov printed before LE1 was written; Grok review 6 Nov)
PRIOR|the literature found (BIS, FOMC minutes Sep 2024) points to INSIDE: secured overnight rates were largely unchanged around the August 2024 equity break
CANNOT|why; anything about the election or the refunding, which share the window; anything about other repo segments; n=1
```

## Result (scored 11 Nov 2026)

**LE1-A: INSIDE.** On 5 Nov the tri-party 2-7 day rate was 3.96% and the overnight rate 3.91%, so S was 5 bp. That is the baseline median and inside the registered 3 to 9 bp band, as the prior expected. The read used vintage 20261111, fetched at about 05:48 UTC on 11 Nov after the gate, which is the first fetched vintage holding 5 Nov (manifest sha256 03e19965c158...). `bin/le1a_score.py --vintage 20261111` printed the label, and the supervisor re-derived S from the raw JSON. The block above still hashes to bc39ff24 (2014 bytes).

Described, not scored: S was 6 bp on 4 Nov and on 6 Nov. LE1's withdrawn median and band need its control days, which run to 23 Nov, so they are described on a later read; that read never changes the label.

Independent check, 11 Nov: Gemini 3.8 Flash, given only the block, the two raw JSON files and the 20261103 daily file, returned the same values (S 6, 5 and 6 bp on 4, 5 and 6 Nov; baseline n 25, 3 to 9 bp, median 5; INSIDE). Before the 11 Nov fetch the vintage folder held only 20261103, so 20261111 is the first fetched vintage holding 5 Nov.

As registered, this says nothing about the election or the refunding, which share the window, and nothing about other repo segments. It is one day.
