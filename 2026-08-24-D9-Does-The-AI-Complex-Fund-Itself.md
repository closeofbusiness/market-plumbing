# D9 — Does the AI complex fund itself? The hyperscalers' cash pools as corporate-bond investors

*24 August 2026. Built from the six firms' own SEC filings, read note-by-note (four Sonnet extraction agents,
one to two firms each; every figure quoted verbatim with accession number, and two of the six independently
re-read from the filing HTML by the orchestrator before entry). Serves **A12**; raised by D2. Result promoted
to RESEARCH_STATE §2 as **S-D9**.*

---

## 1. Result in one paragraph

**The AI complex's cash pools are large corporate-bond investors — about $146bn between six firms — but no
filing discloses a single issuer, so the reflexivity question cannot be answered from public corporate
disclosure.** That is not a null result: it is a **measurement gap with a size attached**. For scale, D2
established that *all* US money-market funds together hold **$22bn** of corporate bonds (0.13% of the market).
**These six corporate treasuries hold 6.6× what the entire money-fund industry holds.** Whether any of it is
each other's paper — Beignet, the Hyperion notes, hyperscaler bonds — is undisclosed and, on the evidence
below, undiscoverable from filings alone.

## 2. The table — corporate debt securities held, fair value, each firm's own filing

| Firm | Filing | Period end | Corporate debt securities | Where it sits | Portfolio context |
|---|---|---|---:|---|---|
| **Amazon** | 10-Q, acc. 0001018724-26-000026 | 30 Jun 2026 | **$59,431m** | Level 2, "Corporate debt securities" | of $125,702m total cash+equivalents+marketable (fair value) |
| **Meta** | 10-Q, acc. 0001628280-26-050705 | 30 Jun 2026 | **$33,074m** | $28,591m in marketable securities + $4,483m in cash equivalents | of $74,798m marketable + $12,133m cash equivalents |
| **Alphabet** | 10-Q, acc. 0001652044-26-000071 | 30 Jun 2026 | **$26,166m** | $26,157m marketable + $9m cash equivalents | of $186,563m marketable securities |
| **NVIDIA** | 10-Q, acc. 0001045810-26-000052 | 26 Apr 2026 | **$15,132m** | $13,599m marketable + $1,533m cash equivalents | second to $21,918m of Treasuries |
| **Microsoft** | 10-K, acc. 0001193125-26-323660 | 30 Jun 2026 | **$12,398m** | "Corporate notes and bonds": $10,660m Level 2 + **$1,738m Level 3** | of $71,084m total debt investments |
| **Oracle** | 10-K, acc. 0001193125-26-277521 | 31 May 2026 | **none disclosed** | portfolio is $23,387m money-market funds + $739m time deposits, nothing else | — |
| **Total** | | | **$146,201m** | | |

*Amazon's and Microsoft's figures were re-read from the filing HTML by the orchestrator and match to the
dollar. Period ends differ (NVIDIA's fiscal calendar, Oracle's May year-end); this is a stack of latest
filings, not a synchronised cross-section.*

## 3. Four things worth keeping

**3.1 Oracle is the outlier, and it is the most levered of the six.** Oracle's entire disclosed cash-pool
composition is money-market funds and time deposits — **no corporate debt, no government securities, no
commercial paper held**. The only commercial paper in Oracle's filing is its own $1.5bn outstanding as a
*liability*. A firm funding heavily in the AI capex cycle holds its cash in the most liquid form available,
while less-levered peers reach for corporate credit. Consistent with the Sept-2026 calendar item on Oracle's
RPO composition and the ASC 460 guarantee maturing 30 Sep.

**3.2 Microsoft holds $1,738m of Level 3 corporate notes and bonds.** Level 3 means unobservable inputs —
marked to model, no quoted market. That is 14% of Microsoft's corporate-bond book and it is the only Level 3
corporate debt anywhere in the six filings. Worth knowing what it is; the filing does not say. **Flagged (N5).**

**3.3 Alphabet's "marketable securities" line contains $94.1bn of restricted SpaceX shares.** Per the note's
own footnotes: $80.0bn of SpaceX subject to short-term sale restrictions inside the $87,063m marketable
equity line, plus $14.1bn subject to long-term restrictions (through Q3 2027) in other non-current assets.
So **~92% of Alphabet's marketable *equity* securities is a single restricted private holding.** For the A11
question — is the wealth real, what happens if it is tested — a "marketable securities" balance that is
mostly one unlistable stake is exactly the kind of thing that reads as liquid until it is tested.
**Flagged (N5), not folded.**

**3.4 A discrepancy in Alphabet's note that we should not paper over.** The fair-value-hierarchy table gives
corporate debt securities at $26,157m; a second table in the same note (adjusted cost / unrealised /
fair value, AFS debt with changes in AOCI) gives $22,936m. The extraction agent offered an explanation —
that the second table combines classifications — but that would make it *larger*, not $3.2bn smaller, so the
explanation does not hold. **The gap is unexplained; we use the hierarchy table's $26,157m and record the
discrepancy.** Candidate cause to check: corporate debt not classified AFS (fair-value option / trading).

## 4. The negative, stated precisely — and it is the finding

**No filing among the six discloses issuer names, an industry or sector breakdown, or a quantified
concentration statement for its corporate-bond holdings.** Verified by full-text search of each document, not
inference: Microsoft's Note 4 contains no instance of "issuer", "industry", "sector" or "concentration";
Alphabet's only "concentration" hits are XBRL geographic-revenue tags and its only "issuer" hits are a
corporate-history sentence and a non-marketable-equity remeasurement clause; Amazon's 10-Q has zero
"concentrat" hits in the relevant note. Three firms carry a generic sentence instead — Meta's "our investment
holdings are in diversified highly rated securities", NVIDIA's "highly rated, diversified investment types
and credit exposures with shorter maturities", Oracle's "limit the amount of credit exposure to any one
issuer". None attaches a number.

**Why this closes the question rather than deferring it.** Registered funds file N-PORT holdings (that is how
D2 measured the Beignet notes) and insurers file Schedule D. **Corporate treasuries file neither.** Much of
this money is run in separately managed accounts by external managers, which are outside N-PORT as well
(the C-053 lesson from PIMCO's SMAs, in a different guise). So the chain "does the AI complex hold its own
paper" has no public route at issuer level. **D9's answer: they hold corporate bonds in size; whether they
hold each other's is not publicly knowable.** The honest downstream use is the aggregate — $146bn of
corporate credit demand from six treasuries, 6.6× the money-fund industry's holdings — not a claim about
reflexivity in either direction.

## 5. What this does to the record

- **S-D9 settled** — RESEARCH_STATE §2. The stale hypothesis figures in §5 ("Alphabet $187bn, Amazon $45bn,
  Meta $75bn" — those were XBRL `MarketableSecuritiesCurrent`, a different and narrower measure) are replaced
  by the table above.
- **D2's circle closes on the demand side.** D2 asked who holds the AI paper; the holders it could measure
  were funds and MMFs. The corporate-treasury bid is now sized in aggregate and shown to be opaque at issuer
  level — a gap to state in any published account, not a hole to hide.
- **Six vintage rows** in `data/series.tsv` (`*_corporate_debt_securities_bn`), each carrying its accession
  number; hand-read from notes, so re-read at the next annual filing rather than re-pulled by script.
- **Flagged, not folded (N5):** Microsoft's Level 3 corporate debt; Alphabet's SpaceX concentration inside
  "marketable securities"; Oracle's all-MMF pool as a leverage tell.
