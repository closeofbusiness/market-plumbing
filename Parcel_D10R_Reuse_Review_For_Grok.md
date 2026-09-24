# Parcel D10R — adversarial review of the dealer re-use construct (for Grok, chat window)

Copy everything below the line into grok.com. Do NOT run in Cursor — this is a judging
parcel, no repo access needed or wanted.

---

You are an adversarial reviewer of empirical work on US repo-market plumbing. Your job is to
break the claims below, not to improve them. Everything you need is in this message or on the
public web.

MATERIAL — five claims from a research note dated 30 Aug 2026, with their evidence:

CLAIM 1 (venue asymmetry). NY Fed Primary Dealer statistics (markets.newyorkfed.org/api/pd,
SBN2024 series break, UST ex-TIPS, week of 2026-08-19, gross outstanding, $bn): reverse repo
(collateral IN): uncleared bilateral 1,559.0, cleared-bilateral sponsored 478.7, total
2,743.6. Repo (collateral OUT): triparty general collateral ex-GCF 875.5, triparty sponsored
GC 239.5, cleared-bilateral sponsored 120.0, total 3,008.8. Inference drawn: hedge-fund
collateral mostly ENTERS the primary dealers off-FICC (uncleared bilateral) and EXITS
on-FICC/triparty toward money funds.

CLAIM 2 (stock utilization 84%). From Q2-2026 10-Qs (SEC EDGAR accessions:
GS 0000886982-26-000297 Note 11; MS 0000895421-26-000212 Note 8; JPM 0001628280-26-054343
Note 23; BAC 0000070858-26-000394; BNY 0001390777-26-000086): collateral received with right
to sell/repledge vs actually repledged, at 30 Jun 2026, $bn: GS 1,431.9/1,265.7;
MS 1,382.7/1,062.2; JPM 2,181.4/1,741.8; BAC ~1,400/~1,300 (1-digit rounding);
BNY 394/331. Five-bank ratio 5,700.7/6,789.4 = 84.0%. Citi: annual disclosure only,
$1,064bn permitted at Dec-2025, repledged amount not quantified.

CLAIM 3 (H1-2026 step change). Same filings, Dec-2025 columns: five-bank permitted
5,722.8 → 6,789.4 (+18.6% in six months); repledged 4,752.5 → 5,700.7 (+19.9%).

CLAIM 4 (one re-use hop). On the chain money-fund cash → dealer → hedge fund, re-use of the
collateral is possible at exactly one node, the dealer: repo passes title to the dealer with
re-use rights; FICC novation is not a re-use hop; money funds receiving collateral in BNY
triparty shells do not re-pledge it. Therefore chain length ≈ 2 and chain velocity cannot
materially exceed ~2 on THIS chain.

CLAIM 5 (Singh comparison). The five/six-bank "permitted to repledge" stock (~7.9tn dollars
including Citi at year-end) is compared against Singh and Goel (IMF WP/19/106) Table 2
"pledged collateral received by banks that can be re-used", 7.5tn dollars GLOBAL at end-2017,
to argue the bank-side numerator has more than doubled on US banks alone. The comparability
of "permitted-to-repledge" (10-Q disclosure) with Singh's "pledged collateral" is asserted,
not demonstrated. This is the weakest joint — attack it first.

TASK
1. Verify every figure you can reach: the NY Fed pd API series and the five EDGAR filings
   are public. Say for each: CONFIRMED / CONTRADICTED (with the correct value) / UNREACHABLE.
2. For each claim, argue the strongest case it is WRONG — measurement perimeter, double
   counting, netting conventions, window-dressing at quarter-end, own-inventory vs client
   collateral in repo OUT, anything real. No devil's-advocacy filler: if a claim survives,
   say so in one line.
3. Specifically on CLAIM 5: what exactly does Singh's numerator include that
   permitted-to-repledge excludes, or vice versa (derivatives margin received? custody
   collateral? European banks' IFRS disclosures being non-comparable?).
4. Name any PUBLIC data source that would improve the construct that the note does not use.

RETURN EXACTLY THIS
For each claim 1–5, a block of four labelled lines:
VERDICT: (stands / falls / stands-with-amendment)
STRONGEST ATTACK: one or two sentences.
EVIDENCE: link + date for every factual assertion you introduce.
WHAT WOULD SETTLE IT: one measurable step.
Then one final line: NEW SOURCES: list or "none".

RULES
- Do not ask clarifying questions; state any assumption you make and answer anyway.
- Mark anything inferred rather than verified as UNCERTAIN and say what would settle it.
- If you cannot do part of this, say which part and why, and do the rest.
- Cite a link and date for every factual claim you introduce. Figures behind paywalls do not
  count as evidence.
- Market-size figures from your training data are presumed stale; pull live or mark stale.
