# FERC EL26-67..72: the six informational reports, read
**Date: 2026-08-30. Status: SETTLED — the 25 Aug calendar item, closed.**
**Sources: all primary, pulled in-house from FERC eLibrary (C-048 exclusion honoured — nothing left the house). Raw PDFs preserved in `_research/primary_sources/ferc_el26_reports/`.**

## 0. What was pulled

All six RTOs filed 30-day informational reports on 20 Jul 2026 under the 18 Jun show-cause
orders: PJM 20260720-5203 (EL26-67), SPP -5205 (EL26-68), NYISO -5217 (EL26-69), MISO -5204
(EL26-70), CAISO -5202 (EL26-71), ISO-NE -5216 (EL26-72). Also read: NGSA comments
20260810-5108 (all six dockets), Sparkfund 20260812-5036 and OMS 20260814-5198 (EL26-70),
and the CAISO order 196 FERC ¶ 61,131 (20260814-3061). Extraction: three Sonnet agents with
quote-anchored schemas; every load-bearing figure below spot-checked by me against the raw
text (grep on the pdftotext output).

## 1. The headline: the grid operators did not size the load

The single most striking fact is an absence. **No RTO reported an aggregate GW figure for
pending large-load interconnection requests.** PJM — the epicentre of the data-centre
buildout — filed a report that does not contain the words "data center" or "co-location"
at all (grep count 0 on both), and whose only large number is generic: 829 Cycle-1
applications totalling ~212,000 MW of *generation* under review. The demand side that is
driving the D9 financing stack ($146.2bn of hyperscaler bonds, sized 24 Aug) has no
official aggregate on the physical side in these filings. What exists instead is
fragments:

- **CAISO** (only report quoting a data-centre forecast): CEC forecasts data-centre load
  +1.8 GW by 2030, +4.9 GW by 2040; total CA load +15 GW by 2035 / +20 GW by 2040 needing
  +74 GW / +107 GW installed capacity.
- **NYISO**: statewide resource-adequacy criterion violation first in 2033, deficiency
  >1,800 MW by 2036 "when accounting for forecasted large load growth"; NYC needs from 2031.
- **SPP**: 2–3 GW accredited-capacity shortfall by 2030; 36 active ERAS requests ≈13.3 GW
  of generation.
- **MISO**: LSE load-forecast CAGR 3.1–5.1% over five years; claims the region "will
  continue to be resource adequate."
- **ISO-NE**: large loads "have yet to materialize in New England" — zero current figures.

This is the same shape as the FWTW gap in N2c: the financial system sizes the buildout in
dollars; the official demand-side ledger cannot (or in these filings, does not) size it in
GW. Flagged as a measurement-gap parallel, not folded anywhere.

## 2. Co-location — the original A2 hook — has nearly vanished from the record

Grep counts for "co-locat" across the six reports: PJM 0, SPP 0, NYISO 0, CAISO 0.
Only **MISO** addresses it: the zero-injection GIA (ZGIA) for generation co-located with
load, §205 filing "on, or about July 31, 2026", plus a Large Load Parallel Study Process
(load ≥250 MW, generation capped at 150% of load need, ~end-Sep filing) explicitly built
so pairing does NOT require co-location. ISO-NE discusses co-location only
generator-to-generator (surplus interconnection headroom). The show-cause orders asked
about co-located loads; five of six RTOs answered about resource adequacy instead.

## 3. But a distinct large-load service class IS emerging — the transferability watch

The Nov panel question (does a transferable/flexible large-load service class appear?) got
real signal:

- **SPP CHILLS**: conditional, curtailable, non-firm service for high-impact large loads,
  capped at a seven-year term — explicitly a bridge, already in tariff.
- **ISO-NE says it will copy CHILLS**, and goes further: a "bring your own (new)
  generation" requirement for new large loads, plus **excluding large loads from the
  Installed Capacity Requirement** — i.e. removing them from the socialized capacity
  construct entirely. Detailed rules pushed to 2027.
- **NYISO** is "considering assigning the responsibility for addressing that resource
  deficiency, including the addition of resources, to the large load(s)."
- **Cost allocation**: SPP has the cleanest rule — provisional-load network upgrades are
  100% directly assigned to the customer until firm service. States hold the rest (OMS:
  Minn. Stat. §216B.1622 assigns all costs to the very-large-customer class; Michigan
  special contracts).
- **Private layer**: Sparkfund documents Google's Pine Island MN ESA paying $50M into
  Xcel's Capacity*Connect distributed-battery portfolio for matched capacity credits —
  the load literally buying its own capacity, outside FERC jurisdiction.

Direction of travel: large loads are being pushed OUT of the mutualized firm-service
construct into bespoke, self-provisioned, curtailable classes. That is the opposite of
transferability-as-commodity; it is bilateralization.

## 4. Procedure: everything now waits for mid-November

All six proceedings went into abeyance on 14 Aug 2026 (letter orders; CAISO by full order
196 FERC ¶ 61,131, which also rescinded the show-cause against Six Cities and WAPA as
non-jurisdictional). §205 filings / show-cause responses now due **16 Nov 2026** (CAISO +
its PTOs explicitly; CAISO board approval 28 Oct), SPP until 20 Nov, others 90 days from
14 Aug. Notices of denial of rehearing by operation of law issued 20 Aug across dockets.
Interim filings to watch (already due or filed): MISO ZGIA §205 ~31 Jul; PJM RBP ~31 Jul
and insufficiency-framework ~7 Aug; MISO parallel-study §205 ~end Sep; SPP PAL/PALS by
16 Nov.

## 5. Claimed-not-verified items (kept separate)

- NGSA (20260810-5108): PJM queue gas generation up 1,458% in two years, ~6,800 MW →
  106,000 MW, now 48% of queue volume; MISO ERAS 75% gas. **NGSA's figures, not checked
  against PJM queue data.**
- Sparkfund cites a "16 GW nationwide VPP" (Tesla/Sunrun/Renew Home) — promoter figure.
- NYISO cites an NYPSC proceeding for 5 GW of nuclear — state-level, not verified.

## 6. What this changes for the programme

Nothing in the money/collateral mechanism map moves. Two things get sharper: (a) the D9
demand-side has no official aggregate GW — the financing is measurable, the load is not,
and that asymmetry is itself a finding; (b) the November panel question now has a
pre-read: the emerging service classes are bilateral and curtailable, not transferable.
Next dated action on this thread: 2026-11-12/16 filings.
