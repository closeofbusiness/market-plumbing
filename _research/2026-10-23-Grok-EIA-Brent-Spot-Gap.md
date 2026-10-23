# EIA's Brent spot against ICE Brent futures, 1-22 October 2026 (Grok g10, 23 Oct 2026)

Grok 4.7 via Cursor, fenced to read and web only; no breaches, nothing blocked, every cited URL fetched in the call (32 pages, 323 s).

**Supervisor check (23 Oct):** the Rigzone/Bloomberg sentence of 19 October was re-fetched and found verbatim (Dated Brent near $117; December Brent settled $109.55). Reading: EIA's daily Brent spot (a Refinitiv spot series) has not returned to the futures price; it moves with press-reported Dated Brent, whose premium over futures narrowed from about $20-33 (2-15 Oct) to about $6-9 (16-21 Oct). No EIA notice or correction was found. The `eia_spot_gap_unverified` flag in `bin/pull_ice_brent_cot.py` now runs to 21 Oct; the gap is a reported physical premium, not a confirmed data error, and the prints are not excluded.

## Return

I'll check the local Brent series against exchange and EIA pages for 1–22 October 2026, then look for any EIA notice and Dated Brent reporting that would explain the gap.The local series runs through 20 October and stays well above the futures prints in the search hits. I’ll fetch the exchange and wire pages, plus EIA notices and Dated Brent reporting, so each price is tied to a page.Investing.com’s ICE Brent history lines up with the Dow Jones settlements already found. I’ll fetch those wire notes, the EIA definitions and notice pages, and the Dated Brent write-ups so the gap and the physical premium rest on pages read here.The gap has not closed. On every trading day in the file, EIA Europe Brent spot stayed at least $6.43 above the ICE Brent December settlement. The smallest gap is 20 October. No later EIA print that was fetched is within $3 of futures either.

Front month is the December 2026 contract on each of these days. Every Dow Jones note below says “for Dec. delivery.” Gap is the file’s EIA Brent spot minus that settlement. Weekends (3–4, 10–11, 17–18 October) had no settlement and are not in the file.

| Date | ICE Brent futures, Dec 2026 ($/bbl) | Source | EIA Brent spot, from the file ($/bbl) | Gap ($/bbl) |
| --- | --- | --- | --- | --- |
| 2026-10-01 | 102.31 | https://uk.investing.com/commodities/brent-oil-historical-data | 114.82 | 12.51 |
| 2026-10-02 | 102.25 | https://www.morningstar.com/news/dow-jones/202610025482/front-month-ice-brent-crude-rose-494-this-week-to-settle-at-10225-data-talk | 135.51 | 33.26 |
| 2026-10-05 | 100.32 | https://www.morningstar.com/news/dow-jones/202610056411/front-month-ice-brent-crude-fell-189-to-settle-at-10032-data-talk | 125.51 | 25.19 |
| 2026-10-06 | 100.58 | https://www.morningstar.com/news/dow-jones/202610066921/front-month-ice-brent-crude-rose-026-to-settle-at-10058-data-talk | 125.44 | 24.86 |
| 2026-10-07 | 100.20 | https://www.morningstar.com/news/dow-jones/202610076568/front-month-ice-brent-crude-fell-038-to-settle-at-10020-data-talk | 126.00 | 25.80 |
| 2026-10-08 | 104.28 | https://www.morningstar.com/news/dow-jones/202610087648/front-month-ice-brent-crude-rose-407-to-settle-at-10428-data-talk | 130.18 | 25.90 |
| 2026-10-09 | 104.72 | https://www.morningstar.com/news/dow-jones/202610096010/front-month-ice-brent-crude-rose-242-this-week-to-settle-at-10472-data-talk | 130.03 | 25.31 |
| 2026-10-12 | 106.65 | https://www.morningstar.com/news/dow-jones/202610125991/front-month-ice-brent-crude-rose-184-to-settle-at-10665-data-talk | 129.95 | 23.30 |
| 2026-10-13 | 105.69 | https://uk.investing.com/commodities/brent-oil-historical-data | 125.78 | 20.09 |
| 2026-10-14 | 106.06 | https://www.morningstar.com/news/dow-jones/202610147085/front-month-ice-brent-crude-rose-035-to-settle-at-10606-data-talk | 126.55 | 20.49 |
| 2026-10-15 | 105.92 | https://www.morningstar.com/news/dow-jones/202610157107/front-month-ice-brent-crude-fell-013-to-settle-at-10592-data-talk | 126.35 | 20.43 |
| 2026-10-16 | 109.86 | https://www.morningstar.com/news/dow-jones/202610165355/front-month-ice-brent-crude-rose-491-this-week-to-settle-at-10986-data-talk | 119.33 | 9.47 |
| 2026-10-19 | 109.55 | https://www.morningstar.com/news/dow-jones/202610195990/front-month-ice-brent-crude-fell-028-to-settle-at-10955-data-talk | 118.82 | 9.27 |
| 2026-10-20 | 108.79 | https://www.morningstar.com/news/dow-jones/202610207154/front-month-ice-brent-crude-fell-069-to-settle-at-10879-data-talk | 115.22 | 6.43 |
| 2026-10-21 | 108.82 | https://uk.investing.com/commodities/brent-oil-historical-data | not in file | — |
| 2026-10-22 | 113.17 | https://www.morningstar.com/news/dow-jones/2026102210027/front-month-ice-brent-crude-rose-400-to-settle-at-11317-data-talk | not in file | — |

The file’s EIA prints match FRED’s EIA series through 20 October, including “2026-10-20: 115.22” (https://fred.stlouisfed.org/series/DCOILBRENTEU). The 2 October jump is in the spot series, not in futures: the spot went from 114.82 to 135.51 while December Brent settled 102.25, down 6 cents on the day.

**CLOSED_ON: NOT CLOSED.** The narrowest gap in the file is $6.43 on 20 October. EIA’s daily-prices page, dated 22 October 2026, still shows a 21 October Brent close of 117.37, which is $8.55 above that day’s 108.82 settlement. No 22 October EIA Brent spot was on the pages fetched. FRED’s next release is listed as 28 October.

Quote, 22 October settlement: “Front Month ICE Brent Crude for Dec. delivery gained $4.35 per barrel, or 4.00% to $113.17 today” (Dow Jones via Morningstar). CNBC’s same-day story: “Brent crude futures gained 4% to close at $113.17 per barrel” (https://www.cnbc.com/2026/10/22/oil-prices-today-wti-brent-saudi-arabia.html). Investing.com’s ICE Dec 2026 history matches every Dow Jones settlement above to the cent. For 1, 13 and 21 October the price is the Investing.com row; the next session’s Dow Jones change lands on the same figure (2 October “down 6.00 cents” from a $102.25 settlement; 14 October “gained 37 cents” to $106.06; 22 October “gained $4.35” to $113.17).

**EIA_NOTICE: NONE FOUND.** Nothing fetched is a correction, revision, or explanation of the October 2026 daily Brent spot series.

Pages checked:

- Spot-price table, release date 10/21/2026, next release 10/28/2026. The only note is the averaging rule: “Weekly, monthly, and annual prices are calculated by EIA from daily data by taking an unweighted average of the daily closing spot prices” (https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm).
- Definitions page. Source line is only “Refinitiv, an LSEG business.” No October errata (https://www.eia.gov/dnav/pet/TblDefs/pet_pri_spt_tbldef2.asp).
- Today in Energy daily prices, page dated 22 October 2026. It republishes Refinitiv spots and shows Brent at 117.37 for the 10/21/26 close, with no correction text (https://www.eia.gov/todayinEnergy/prices.php).
- This Week in Petroleum. “We no longer publish This Week in Petroleum (TWIP).” The archive on that page runs through 2025 and has no October 2026 Brent note (https://www.eia.gov/petroleum/weekly/).
- Weekly Petroleum Status Report page. Tables only; no Brent-spot notice (https://www.eia.gov/petroleum/supply/weekly/).
- Short-Term Energy Outlook, 6 October 2026. It raises the forecast. It does not retract the daily series: “We now forecast the Brent crude oil spot price will average $105 per barrel (b) in 4Q26, $14/b higher than in last month’s STEO” (https://www.eia.gov/outlooks/steo/).
- FRED DCOILBRENTEU, sourced to EIA, last observation 115.22 on 20 October, updated 21 October, next release 28 October. No revision note on the page.

A site search for an EIA RBRTE correction or errata for October 2026 returned the ordinary history pages, not a notice.

**PHYSICAL_PREMIUM:** Press reporting describes a real Dated Brent premium of the same order as the EIA gap. It narrowed from the mid-October extremes and was still several dollars on 19–22 October, not about $3.

Bloomberg, carried by Rigzone on 19 October: “The Dated Brent benchmark, which underpins prices in Europe, traded near $117 on Monday, down almost $16 from a week prior.” The same piece: “Brent for December settlement fell 0.3% to settle at $109.55 a barrel” (https://www.rigzone.com/news/wire/oil_prices_hover_near_fivemonth_high-19-oct-2026-184878-article/). Near $117 against a $109.55 settlement is about $7.50. “Down almost $16” from near $117 puts the level a week earlier near $133. That is the same neighborhood as the file’s EIA prints on 8–12 October (130.18, 130.03, 129.95), and far above futures, which settled $104.28 to $106.65 those days. EIA on 19 October is 118.82, about $2 above Bloomberg’s “near $117,” so the two series are close and not identical.

Bloomberg, carried by BusinessMirror on 22 October: “Yet there has been a plunge in Dated Brent… It’s near $120, down roughly $15 in less than two weeks.” And: “While Dated’s premium has fallen significantly recently, it remains much higher than it would be in normal times relative to futures” (https://businessmirror.com.ph/2026/10/22/price-of-physical-oil-barrels-slides-just-as-futures-rally/). Futures that day settled at $113.17, so a Dated price near $120 is still about $7 over the screen.

That pattern matches the file: the EIA-minus-futures gap peaked at $33.26 on 2 October, was still about $20–26 through 15 October, then fell to $9.47, $9.27 and $6.43 on 16, 19 and 20 October. It did not fall to about $3. The EIA series is moving with reported physical Brent, not snapping back to the futures price.

Two limits. EIA’s definition page calls the series a Refinitiv Brent spot and does not name it Platts Dated Brent, so the comparison is to the press description of Dated Brent, not to a Platts assessment page. A secondary write-up says Bloomberg had Dated Brent at $130 on 15 October against the $105.92 settlement (https://oilauthority.com/news/dated-brent-130-ice-futures-24-dollar-physical-premium-hormuz). That page says the $24.08 premium is its own calculation, and the underlying Bloomberg wire for 15 October was not fetched. The file’s EIA print that day is 126.35, still about $20 above futures.
