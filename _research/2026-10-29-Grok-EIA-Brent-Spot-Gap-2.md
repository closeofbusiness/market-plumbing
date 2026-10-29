# EIA's Brent spot against ICE Brent futures and Dated Brent, 22-28 October 2026 (Grok, 29 Oct 2026)

Grok 4.7 via Cursor, fenced to read and web only; no breaches, nothing blocked, every cited URL fetched in the call (33 fetch calls, 518 s). One page (Morningstar) answered 403 and was not used.

**Supervisor check (29 Oct):** the Xinhua dispatch of 23 October was re-fetched and both settlements found verbatim (December Brent $113.17, December WTI $99.47, 22 Oct). Reading: on 22-27 October EIA's daily Brent spot stood about $9-12 above the December ICE Brent settlement ($125.39 against $113.17 on 22 Oct) and within about $1.6-3.0 of Trend's Dated Brent on 22-23 October; Dated Brent's premium over futures was about $9-10 on 22-23 October and $5.3 on 28 October. The spread of EIA's Brent spot over EIA's WTI spot, $18-23 on 22-27 October, mixes that premium with a Brent-WTI futures gap of about $14 ($113.17 against $99.47). As on 23 October, the gap is a reported physical premium, not a confirmed data error; the prints are not excluded and the `eia_spot_gap_unverified` flag in `bin/pull_ice_brent_cot.py` now runs to 27 October, the last EIA print.

## Return

Trading days in that window are 22, 23, 26, 27 and 28 October 2026. The 24th and 25th were Saturday and Sunday. On every session below, the named front month is December 2026. A Morningstar page returned 403 and was not used.

2026-10-22, ICE Brent, $113.17, December 2026, https://english.news.cn/20261023/33f3f9abc83240e28dcfbe90ed12a33a/c.html, "to settle at 113.17 dollars a barrel"
2026-10-22, Dated Brent, $122.44, —, https://www.trend.az/azerbaijan/4238658.html, Dated Brent row under 22.10.2026, "$122.44"
2026-10-22, WTI futures, $99.47, December 2026, https://english.news.cn/20261023/33f3f9abc83240e28dcfbe90ed12a33a/c.html, "to settle at 99.47 dollars a barrel"
2026-10-23, ICE Brent, $116.72, December 2026, https://english.news.cn/20261024/d8154c319da74087afbf5f97ae9974f5/c.html, "to settle at 116.72 dollars a barrel"
2026-10-23, Dated Brent, $126.69, —, https://www.trend.az/azerbaijan/4238658.html, Dated Brent row under 23.10.2026, "$126.69"
2026-10-23, WTI futures, $103.27, December 2026, https://english.news.cn/20261024/d8154c319da74087afbf5f97ae9974f5/c.html, "to settle at 103.27 dollars a barrel"
2026-10-26, ICE Brent, $115.81, December 2026, https://www.nampa.org/text/23050011, "to settle at 115.81 dollars a barrel"
2026-10-26, Dated Brent, $128.3, —, https://dan-bunkering.com/insight-weekly-market-report/market-report-27102026/, "assessed at USD 128.3/bbl on Monday"
2026-10-26, WTI futures, $101.76, December 2026, https://www.nampa.org/text/23050011, "to settle at 101.76 U.S. dollars a barrel"
2026-10-27, ICE Brent, $113.88, December 2026, https://english.news.cn/20261028/0f1d4e9353ab426d8dc006c1491c7322/c.html, "to settle at 113.88 dollars a barrel"
2026-10-27, Dated Brent, NOT FOUND, —, —, —
2026-10-27, WTI futures, $99.9, December 2026, https://english.news.cn/20261028/0f1d4e9353ab426d8dc006c1491c7322/c.html, "to settle at 99.9 U.S. dollars a barrel"
2026-10-28, ICE Brent, $115.32, December 2026, https://english.news.cn/20261029/279ec84332204907a8e9ddfe97bc8124/c.html, "to settle at 115.32 dollars a barrel"
2026-10-28, Dated Brent, $120.61, —, https://commodityscope.com/prices/dated-brent-crude-oil, "on 28 Oct 2026, to $120.61/bbl"
2026-10-28, WTI futures, $102.78, December 2026, https://english.news.cn/20261029/279ec84332204907a8e9ddfe97bc8124/c.html, "to settle at 102.78 U.S. dollars a barrel"

Assumptions: Dan-Bunkering’s “Monday” is 26 October, the day of the Tehran talks in that report. Trend’s 29 October note prints the same $120.61 and the same $1.09 rise without naming the assessment date; the 28 October date is taken from the commodityscope page. Reuters prints WTI on 27 October as $99.90. The same Reuters dispatches match the Brent settlements on 23, 26 and 27 October. Gaps below are the difference of two fetched prices, not a separate quoted assessment.

VERDICT
NARROWED. On Trend’s Dated Brent series the gap over the December ICE settlement was $10.97 on 21 October ($119.79 versus $108.82), $9.27 on 22 October, $9.97 on 23 October, and $5.29 on 28 October ($120.61 versus $115.32); 26–27 October have no print in that same series, and the Monday $128.3 figure would show a wider gap only if it is the same assessment.
NEITHER. FRED’s EIA Europe Brent spot series prints $125.39, $128.30, $128.12 and $123.10 for 22, 23, 26 and 27 October (https://fred.stlouisfed.org/series/DCOILBRENTEU; 28 October was not on that page), which is $1.61–$2.95 from Trend’s Dated Brent on 22–23 October and $9.22–$12.31 above December ICE Brent, and EIA’s spot-price note names Refinitiv as the source (https://www.eia.gov/dnav/pet/TblDefs/pet_pri_spt_tbldef2.asp). A Platts Dated Brent (PCAAS00) print for these dates would settle whether any other physical assessment matches EIA exactly.
