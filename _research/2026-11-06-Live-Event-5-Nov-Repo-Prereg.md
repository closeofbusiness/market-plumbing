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
