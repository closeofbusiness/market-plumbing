# Japan's 10-year yield: term premium and expected rates

This folder splits the change in Japan's 10-year government bond yield from December 2023 to September 2026 into a term premium and an expected path of short-term rates, using one researcher's published model. This is one model's split of the yield change. Other models split it differently, and it does not show why yields rose.

## The result

**Registered reading** (monthly file, 10-year, full window December 2023 to September 2026). The monthly-average 10-year constant-maturity yield changed by 2.3061 percentage points over the window. The model's term premium is 0.5356 of that change (denominator: the 2.3061-point change in the monthly-average 10-year yield), which is +8.2 basis points of yield change from an even split (distance = (share - 0.5) x change in yield x 100). Classification under the rule fixed before the data run: **close to even (a share from 0.40 to 0.60 names no larger part)**. "Registered" means that the rule, the full window and this row were written down before any data were run.

**The four tenors, monthly file, full window.** Each share is the term premium's part of that tenor's own change in the monthly-average constant-maturity yield.

| tenor | change in yield (pp) | change in term premium (pp) | change in expected rates (pp) | term-premium share of the change | distance from an even split (bp) | classification |
|---|---:|---:|---:|---:|---:|---|
| 2Y | 1.8168 | 0.6532 | 1.1636 | 0.3595 | -25.5 | expected rates larger |
| 5Y | 2.0422 | 0.9036 | 1.1386 | 0.4425 | -11.8 | close to even |
| 10Y | 2.3061 | 1.2351 | 1.0710 | 0.5356 | +8.2 | close to even |
| 20Y | 2.3969 | 1.4743 | 0.9226 | 0.6151 | +27.6 | term premium larger |

The four tenors fall on both sides of one half: the share runs from 0.3595 at 2Y to 0.6151 at 20Y.

**The monthly file and the daily file side by side, full window** (the daily file is a separate estimate by the same author, averaged by month here; it never enters the registered classification). Each share is the term premium's part of that file's own change in the yield at that tenor.

| tenor | monthly-file share | monthly-file class | daily-file share | daily-file class |
|---|---:|---|---:|---|
| 2Y | 0.3595 | expected rates larger | 0.2975 | expected rates larger |
| 5Y | 0.4425 | close to even | 0.3605 | expected rates larger |
| 10Y | 0.5356 | close to even | 0.4445 | close to even |
| 20Y | 0.6151 | term premium larger | 0.5032 | close to even |

**Headline reading at 10 years: close to even in both of the author's files, and dependent on the model.** The author's monthly file gives 0.5356 and his daily file 0.4445 (a separate estimate by the same author; why the two differ is not established); JMA's own model gives 0.2899; and the other tenors fall on both sides of one half. This is one model's split, and a different model can move it.

**Sub-windows and the path.** Each cell is the term premium's share of that window's own change in the yield at that tenor (monthly file); the last column is the 10-year change in points. A bridge window is never classified. The path windows split the full window in two at December 2024.

| window | 2Y | 5Y | 10Y | 20Y | 10-year change (pp) |
|---|---:|---:|---:|---:|---:|
| window A, December 2023 to July 2024 | 0.1545 | 0.2188 | 0.3929 | 0.5848 | 0.3828 |
| bridge, July 2024 to August 2024 (never classified) | bridge | bridge | bridge | bridge | -0.1677 |
| window B, August 2024 to September 2026 | 0.3873 | 0.4998 | 0.5808 | 0.6327 | 2.0910 |
| BoJ-matched window, August 2024 to June 2026 | 0.4168 | 0.5646 | 0.6432 | 0.6847 | 1.7529 |
| first path window, December 2023 to December 2024 | 0.2115 | 0.0773 | 0.0554 | 0.3356 | 0.3969 |
| second path window, December 2024 to September 2026 | 0.4214 | 0.5454 | 0.6354 | 0.6794 | 1.9092 |

The share moves a lot between windows: at 10 years it is 0.0554 in the first path window and 0.6354 in the second, so the full-window figure combines two stretches that look very different.

Window B (August 2024 to September 2026) straddles the two path windows (December 2023 to December 2024, and December 2024 to September 2026): it starts inside the first and runs to the end of the second. The full window equals window A plus the bridge plus window B exactly, and equals the two path windows added, in changes of the term premium, of expected rates and of the yield (checked to 1e-9; `checks.csv` row C12).

## What was fixed in advance

The rule, the full window, the tenors and the 0.40 to 0.60 band were written down before this build ran on any data (the band was amended once, before the build, so that no larger part is named inside it). Two things were not independent of the data:

The full-window result was read before this build. The sub-windows and the BoJ-matched window were chosen after looking at the data.

## Definitions

- **Term premium** (here): the part of the yield that Nakajima's model does not attribute to its expected path of short rates. Nakajima (2025), appendix, defines it simply as the yield minus the expected rate, and the data match: the two add to the Ministry of Finance monthly-average yield (see the fitted-yield section).
- **Expected rates**: the model's expected average short rate over the bond's life, under the real-world (not the risk-neutral) measure, as published.
- **Residual**: the change in the term premium is the change in the yield minus the change in expected rates, so every error in the model's expected path lands in it. It is not a measurement.
- **Monthly average**: the mean of the month's daily values, not the month-end value.
- **Constant-maturity yield**: the Ministry of Finance series (semiannual compounding, percent), read for the 10-year and the other tenors.
- **Vintage**: one dated upload of the author's file (a GitHub commit). Every row names its vintage (the commit date and the first 12 characters of its code); no statistic mixes two.
- **Tenor**: the bond's maturity; 2Y is a 2-year bond. A **basis point** (bp) is one hundredth of a percentage point (pp).
- **Abbreviations**: JGB is a Japanese government bond, the Bank is the Bank of Japan (BoJ), MoF is Japan's Ministry of Finance, JMA is Japan Macro Advisors. Nakajima's published files estimate the Ichiue–Ueno shadow-rate model, so the two names refer to one model.

## The model caveat (a property of the cited model, not a finding)

The Ichiue–Ueno model holds the long-run short rate constant, so a rise in long-run expected rates can be recorded as term premium. Japan Macro Advisors makes this criticism of the standard model; it states that standard models "significantly overestimate the premium".

In plain terms: the model expects the short-term interest rate to drift back, over the long run, toward one fixed level. If the true long-run level has moved up, the model can record such a rise as term premium.

Reading of the papers (a manual step outside the script; one request per file): Ichiue and Ueno (2013), pages 8 to 9: checked. The short rate is a constant, written rho and carrying no time index, plus two zero-mean Gaussian factors, and the paper calls rho the long-run level of the short rate (equation 1, printed page 7, which is page 8 of the PDF; the shadow-rate model repeats it on printed page 11). The long-run level is one estimated number for the whole sample. Nakajima (2025): the same constant is kept. The appendix (printed page 10, page 11 of the PDF) writes the shadow rate as rho plus a linear function of the factors, following Ichiue and Ueno (2013), with rho again a single parameter with no time index; only the lower bound on the short rate is set to vary by date. The paper defines the term premium simply as the yield minus the expected rate (printed page 11).

## What it cannot say

It cannot say why yields rose, or that purchases, flows or positions moved any price. It does not test the project's breakeven split (C-126), which divides the nominal yield into inflation compensation and the real yield. This split cuts across it: expected inflation sits inside expected nominal rates, and an inflation risk premium sits inside the term premium. The term premium here is one model's residual; the author's own monthly and daily files already differ.

**Japan Macro Advisors (JMA), cross-check.** JMA's own model gives a 10-year full-window share of 0.2899 (denominator: JMA's 2.3923-point change in its own 10-year yield), against 0.5356 in the monthly file. JMA's label: **model_sensitive** (arms fired: share+side). The label is model_sensitive if any of three arms fires: ratio (JMA's change in term premium is under half or over twice the monthly file's), share (the two shares differ by more than 0.15) or side (the two shares sit on opposite sides of one half). JMA's yield is a spot (zero-coupon) yield, probably a month-end value rather than a monthly average, and it benchmarks its premia to their 2004 to 2012 averages, so it is not on the same basis. Its model is proprietary, and its updated estimates are for paid users; its files are free to use and reproduce with attribution to Japan Macro Advisors. Raw JMA files stay in the local cache.

**The Bank's Review, side by side.** Bank of Japan Review 2026-E-10, from summer 2024: both factors "contributed to roughly the same degree". The monthly file's share over the matched window (August 2024 to June 2026, the Review's end point) is 0.6432 (denominator: the 1.7529-point change in the 10-year yield over that window). The two are set next to each other and no verdict is given. Reading "roughly the same degree" as a share from 0.40 to 0.60 is this spec's convention, not the Bank's. The Bank used a different model (Imakubo and Nakajima 2015, anchored on Consensus Forecasts) and a window that had already been read before this build. The data are as of end-June 2026 in its chart.

## Why the yield change here differs from the project's earlier JGB note's +243bp

The project's earlier JGB note reports +243bp for the 10-year JGB from 29 December 2023 to 24 September 2026 on daily values. This folder uses monthly averages (the December 2023 average to the September 2026 average, which holds 19 days), and the change is 2.3061 points. Different end points, a different averaging; neither is wrong.

## The fitted-yield check

Over the window, the monthly file's term premium plus expected rate equals the Ministry of Finance monthly-average constant-maturity yield to within 0.00010 percentage points at six tenors (204 comparisons; tolerance 0.00015); the daily file against the MoF value on each common date, within 0.00000 (4134 comparisons). Against the month's last value instead, the 10-year gap is larger (maximum 0.12290 over the window; `fitted_check.csv`). This shows the basis (percent, monthly average) and that the term premium is, in effect, the observed yield minus the model's expected path. It cannot test the model's fit: the sum matches whatever the model's expected path is.

## Vintage and revisions

The monthly file used is the vintage `2026-10-06_33118433fe95`; the daily file `2026-10-06_33118433fe95`; JMA `jma_2026-10_23d7c109d5d8`. The registered row is the first successful build and is never rewritten; a later vintage adds rows and a changed classification would be stated with both. 

**How far a revision moves the share.** On the two revision windows below, which end earlier than the full window and so move more for the same revision, the 10-year share moved by at most 0.0285 between vintages. The registered share (0.5356) lies 0.0644 below the band's upper edge (0.60) and 0.1356 above its lower edge (0.40); as term premium that is 0.149 and 0.313 percentage points. A revision of the size seen would not by itself carry it out of the band. A change of model moves it further: the daily file reads 0.4445 (inside the band) and JMA 0.2899 (below it).

| revision window (10-year) | vintage | change in yield (pp) | term-premium share of that change | class |
|---|---|---:|---:|---|
| December 2023 to March 2026 | 2026-04-20_8f940a0141ee | 1.5569 | 0.5022 | close to even |
| December 2023 to March 2026 | 2026-07-06_80f7108a1637 | 1.5570 | 0.5270 | close to even |
| December 2023 to March 2026 | 2026-10-06_33118433fe95 | 1.5570 | 0.5307 | close to even |
| December 2023 to June 2026 | 2026-07-06_80f7108a1637 | 1.9680 | 0.5743 | close to even |
| December 2023 to June 2026 | 2026-10-06_33118433fe95 | 1.9680 | 0.5834 | close to even |

## Provenance

- Model: Ichiue, H., and Y. Ueno (2013), "Estimating term premia at the zero bound: An analysis of Japanese, US, and UK yields", Bank of Japan Working Paper 13-E-8; Nakajima, J. (2025), "Impact of US monetary policy spillovers and yield curve control policy", Discussion Paper A.760, Institute of Economic Research, Hitotsubashi University. Data: Jouchi Nakajima's published files (the page says "Cite the below articles when using this dataset"), estimated and released within his research activity, not the official view of the Bank of Japan, used at the user's own risk.
- Nakajima's repository states no licence. This repository's own CC BY 4.0 licence does not extend to his files, which are therefore never committed here, in any form; only changes over listed windows, shares, and at most four level points per vintage (`pins.csv`) are.
- JMA: free to use and reproduce with attribution to Japan Macro Advisors. Ministry of Finance Japan JGB yields: Public Data License 1.0.
- Every URL, commit and licence text is in `SOURCES.md`.
- Build decisions, including two text fixes made after the first build, are listed in [SOURCES.md](SOURCES.md).
