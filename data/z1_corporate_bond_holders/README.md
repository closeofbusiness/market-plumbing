# US corporate and foreign bonds: which holders took the net increase, 2024Q1-2026Q2 (Federal Reserve Z.1, table F3.5)

This folder shows which kinds of holders took the net increase in US corporate and foreign bonds from 2024Q1 to 2026Q2, in the Federal Reserve's financial accounts (Z.1 table F3.5, release 20260911). US insurers (life and property-casualty) took 33.26% of the all-sector net, $741.3bn of $2,228.4bn (unadjusted basis, 2024Q1-2026Q2), ranking third of seven holder groups, behind registered funds and the rest of the world.

These are flows for the whole US corporate and foreign bond market; Z.1 has no line for the AI companies' bonds, so nothing here shows who holds AI debt or who bought any deal, and a net acquisition is purchases minus sales and redemptions, not purchases.

The wave-window shares were seen during review, before this spec was committed, so they are reported, not tested. Three statements about how the shares move when the next release arrives are registered in advance: the insurer, registered-fund and rest-of-the-world shares of the 2024Q1-2026Q2 net each move by less than 2.0 percentage points between the 11 Sep 2026 and the 10 Dec 2026 releases. They are scored on the 10 Dec 2026 release and read PENDING until it is cached; see "Revisions and the registered statements" below.

## What the net was made of, before any holder

Net issuance is new bonds issued minus redemptions. Over 2024Q1-2026Q2 (10 quarters, unadjusted), by issuer sector; the denominator of every share is the all-sector net of $2,228.4bn (line 1 of the table).

| Issuer sector | Net issuance | Per-quarter average | Share of the net |
| --- | --- | --- | --- |
| All issuers (line 1) | $2,228.4bn | $222.8bn | 100.00% |
| Nonfinancial corporate business | $765.9bn | $76.6bn | 34.37% |
| Domestic financial sectors | $819.9bn | $82.0bn | 36.79% |
| of which US-chartered depository institutions | -$10.2bn | -$1.0bn | -0.46% |
| of which issuers of asset-backed securities | $338.0bn | $33.8bn | 15.17% |
| of which finance companies | $60.4bn | $6.0bn | 2.71% |
| of which mortgage REITs | $33.4bn | $3.3bn | 1.50% |
| of which business development companies | $48.0bn | $4.8bn | 2.16% |
| of which security brokers and dealers | $204.0bn | $20.4bn | 9.15% |
| of which holding companies | $146.3bn | $14.6bn | 6.57% |
| of which other financial business | $0.0bn | $0.0bn | 0.00% |
| Rest of the world (foreign bonds US residents acquired) | $642.6bn | $64.3bn | 28.84% |

The instrument is all corporate and foreign bonds: investment grade and high yield, financial issuers, private-label ABS and MBS, and foreign bonds held by US residents. Z.1 has no line for the AI issuers, so this table cannot say who took their bonds. For context only, the BIS Quarterly Review of 16 March 2026 reports that hyperscalers' gross bond issuance was "topping $100 billion in 2025"; that is gross issuance by five firms, so it is not comparable with a net figure and no ratio is computed here.

## The holders, 2024Q1-2026Q2

Net acquisition is purchases minus sales and redemptions over the period. The denominator of the share of the net is the all-sector net of $2,228.4bn (line 13); the denominator of the share of the positive flows is $3,077.1bn, the sum of the positive net acquisitions of the nine groups. The offset ratio (the all-sector net divided by the sum of the absolute net acquisitions of the 28 holder lines) is 0.5598, so the stability flag is "ok".

| Holder group | Net acquisition | Per-quarter average | Share of the net | Share of the positive flows |
| --- | --- | --- | --- | --- |
| **All holders (line 13)** | $2,228.4bn | $222.8bn | 100.00% | - |
| **US insurers (life and property-casualty)** | $741.3bn | $74.1bn | 33.26% | 24.09% |
| Life insurers | $567.6bn | $56.8bn | 25.47% | 18.44% |
| of which life insurers' general accounts | $423.5bn | $42.4bn | 19.01% | 13.76% |
| of which life insurers' separate accounts | $144.0bn | $14.4bn | 6.46% | 4.68% |
| Property-casualty insurers | $173.7bn | $17.4bn | 7.79% | 5.64% |
| **Pension funds** | $99.3bn | $9.9bn | 4.45% | 3.23% |
| Private pension funds | $19.9bn | $2.0bn | 0.89% | 0.65% |
| Federal government pension funds | $2.2bn | $0.2bn | 0.10% | 0.07% |
| State and local pension funds | $77.2bn | $7.7bn | 3.46% | 2.51% |
| **Registered funds** | $1,081.2bn | $108.1bn | 48.52% | 35.14% |
| Mutual funds | $423.5bn | $42.4bn | 19.00% | 13.76% |
| Closed-end funds | $0.9bn | $0.1bn | 0.04% | 0.03% |
| Exchange-traded funds | $644.4bn | $64.4bn | 28.92% | 20.94% |
| Interval and tender-offer funds | $12.3bn | $1.2bn | 0.55% | 0.40% |
| **Rest of the world** | $934.2bn | $93.4bn | 41.92% | 30.36% |
| **Banks and credit unions** | $90.3bn | $9.0bn | 4.05% | 2.93% |
| **Households and nonprofits (residual)** | -$848.6bn | -$84.9bn | -38.08% | - |
| **Hedge funds and private debt funds** | $52.3bn | $5.2bn | 2.35% | 1.70% |
| Hedge funds (domestic) | $55.4bn | $5.5bn | 2.48% | 1.80% |
| Private debt funds | -$3.1bn | -$0.3bn | -0.14% | - |
| Households plus hedge funds plus private debt funds (derived) | -$796.3bn | -$79.6bn | -35.74% | - |
| **Government-sponsored enterprises and security brokers and dealers** | $14.7bn | $1.5bn | 0.66% | 0.48% |
| **Other holders** | $63.8bn | $6.4bn | 2.86% | 2.07% |

A share can be below zero or above 100% because the total is a net: groups that reduced their holdings count as negative, so the rest add to more than 100%.

Ranked by net acquisition among the seven groups (insurers, pension funds, registered funds, rest of the world, banks, households, hedge funds and private debt funds): 1 Registered funds; 2 Rest of the world; 3 US insurers; 4 Pension funds; 5 Banks and credit unions; 6 Hedge funds and private debt funds; 7 Households and nonprofits.

## Against 2017-2019, and the yearly path

Each cell is the group's share of the all-sector net for that window, with the net acquisition in $bn in brackets; unadjusted basis. The rows between the two windows are in the same table; no sentence here compares two windows.

| Window | All-sector net ($bn) | Insurers | Pensions | Registered funds | Rest of the world | Banks | Households (residual) | Hedge and private debt funds | GSEs and dealers | Other |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2017Q1-2019Q4 | 1,329.6 | 34.4% (456.9) | -1.8% (-23.6) | 40.0% (531.6) | 31.2% (415.3) | -2.4% (-31.9) | -5.4% (-71.2) | 2.5% (33.1) | -2.0% (-27.2) | 3.5% (46.7) |
| 2017 | 620.8 | 15.4% (95.5) | 5.4% (33.8) | 37.1% (230.1) | 51.8% (321.5) | -2.8% (-17.5) | -10.1% (-62.5) | 0.8% (5.0) | -1.5% (-9.0) | 3.9% (23.9) |
| 2018 | 326.0 | 57.1% (186.2) | 9.3% (30.3) | 48.0% (156.4) | -19.1% (-62.2) | -6.0% (-19.5) | 6.2% (20.4) | -1.2% (-4.1) | -3.5% (-11.5) | 9.2% (30.2) |
| 2019 | 382.8 | 45.8% (175.2) | -22.9% (-87.6) | 37.9% (145.2) | 40.8% (156.0) | 1.3% (5.1) | -7.6% (-29.1) | 8.4% (32.2) | -1.8% (-6.7) | -1.9% (-7.4) |
| 2020 | 1,063.4 | 23.5% (250.0) | 11.1% (118.3) | 39.3% (417.5) | 20.1% (213.4) | 2.0% (21.5) | 12.4% (132.1) | -2.5% (-26.7) | -2.0% (-21.6) | -3.9% (-41.2) |
| 2021 | 851.9 | 31.2% (265.7) | 15.8% (134.3) | 46.3% (394.2) | 8.5% (72.7) | 24.7% (210.3) | -31.5% (-268.2) | -3.7% (-31.8) | 5.9% (50.0) | 2.9% (24.8) |
| 2022 (offsetting) | 394.9 | 63.5% (250.8) | 14.7% (58.2) | -2.1% (-8.3) | 26.7% (105.6) | 39.3% (155.1) | -69.1% (-272.9) | 11.8% (46.6) | 1.9% (7.5) | 13.2% (52.2) |
| 2023 | 521.7 | 24.3% (126.7) | -1.7% (-8.8) | 15.5% (81.0) | 57.5% (299.8) | -16.4% (-85.5) | 15.3% (79.7) | 8.0% (42.0) | 2.6% (13.7) | -5.2% (-26.9) |
| 2024 | 794.5 | 37.1% (294.9) | 5.5% (43.6) | 44.1% (350.0) | 37.6% (298.8) | -3.0% (-24.0) | -19.1% (-151.4) | -1.7% (-13.5) | -0.3% (-2.7) | -0.2% (-1.2) |
| 2025 | 805.4 | 35.7% (287.3) | 1.9% (15.4) | 45.2% (364.2) | 47.9% (386.2) | -0.3% (-2.1) | -33.4% (-268.9) | -1.2% (-10.1) | 0.3% (2.3) | 3.9% (31.1) |
| 2026H1 (offsetting) | 628.5 | 25.3% (159.0) | 6.4% (40.3) | 58.4% (366.9) | 39.7% (249.3) | 18.5% (116.4) | -68.1% (-428.3) | 12.1% (75.9) | 2.4% (15.2) | 5.4% (33.9) |
| 2024Q1-2026Q2 | 2,228.4 | 33.3% (741.3) | 4.5% (99.3) | 48.5% (1,081.2) | 41.9% (934.2) | 4.1% (90.3) | -38.1% (-848.6) | 2.3% (52.3) | 0.7% (14.7) | 2.9% (63.8) |

A window marked offsetting (2022, 2026H1) has an offset ratio below 0.5: groups adding and groups reducing holdings largely cancel, so a small change in any line moves every share in that row a lot.

## The insurer line and reinsurance

Only uncollateralised coinsurance moves the bonds to the reinsurer, which is in the rest of the world if it is offshore. Under funds withheld and modified coinsurance the US insurer keeps investing the assets, and US captives are brought into the life sector (Board FEDS Note, 12 Oct 2018). The size of each structure is unknown, so the insurer line may be understated by an unknown amount. Bonds held through funds sit in the fund sectors.

## The household line is a residual

Households and nonprofits are what is left of the table after the other 27 holder lines: any error in those lines, and any holder the Fed cannot place, lands in this line, so it is the least secure number in every table. Domestic hedge funds and private debt funds are separate lines. Over 2024Q1-2026Q2 (unadjusted; the denominator of each share is the all-sector net of $2,228.4bn):

| Line | Net acquisition | Share of the net |
| --- | --- | --- |
| Households and nonprofits (residual) | -$848.6bn | -38.08% |
| Hedge funds (domestic) | $55.4bn | 2.48% |
| Private debt funds | -$3.1bn | -0.14% |
| Hedge funds and private debt funds | $52.3bn | 2.35% |
| Households plus hedge funds plus private debt funds (derived) | -$796.3bn | -35.74% |

## Amounts outstanding, and level change minus net acquisition

Share of the holders' total of the amounts outstanding at the end of the quarter, with the level in $bn in brackets. The denominator is the sum of the 28 holder lines' levels ($18,115.7bn at 2026Q2); the instrument discrepancy (line 54) is printed beside it in level_shares.csv (-$410.6bn at 2026Q2).

| Holder group | 2016Q4 | 2019Q4 | 2021Q4 | 2023Q4 | 2026Q2 |
| --- | --- | --- | --- | --- | --- |
| US insurers (life and property-casualty) | 26.8% (3,126.7) | 27.9% (3,865.3) | 27.2% (4,313.6) | 27.2% (4,056.3) | 26.8% (4,850.2) |
| Pension funds | 10.2% (1,192.2) | 9.6% (1,334.1) | 10.0% (1,587.6) | 9.6% (1,429.4) | 8.5% (1,547.6) |
| Registered funds | 18.8% (2,193.4) | 20.6% (2,850.3) | 22.9% (3,629.1) | 21.2% (3,158.9) | 23.7% (4,301.5) |
| Rest of the world | 29.4% (3,429.8) | 28.8% (3,979.5) | 27.8% (4,401.6) | 28.8% (4,289.8) | 28.7% (5,195.7) |
| Banks and credit unions | 5.8% (682.5) | 4.7% (654.6) | 5.6% (888.0) | 6.1% (908.4) | 5.6% (1,018.3) |
| Households and nonprofits (residual) | 1.5% (178.1) | 1.5% (211.8) | 1.3% (210.2) | 1.3% (199.0) | 1.1% (192.0) |
| Hedge funds and private debt funds | 2.2% (260.9) | 2.2% (305.6) | 1.6% (248.8) | 2.0% (302.3) | 2.0% (360.1) |
| Government-sponsored enterprises and security brokers and dealers | 1.0% (113.4) | 0.6% (87.6) | 0.4% (68.8) | 0.6% (82.7) | 0.5% (99.2) |
| Other holders | 4.2% (490.6) | 4.0% (547.5) | 3.2% (513.5) | 3.2% (471.9) | 3.0% (551.3) |

Change in the amount outstanding over the window minus the window's net acquisition is, for most groups, mainly price changes and other changes in volume; for the household line it is not (see the note below the table). For 2024Q1-2026Q2, from the end of 2023Q4 to the end of 2026Q2, in $bn:

| Holder group | Level, start | Level, end | Net acquisition | Level change minus net acquisition |
| --- | --- | --- | --- | --- |
| All holders (sum of the 28 holder lines) | $14,898.7bn | $18,115.7bn | $2,228.4bn | $988.6bn |
| US insurers (life and property-casualty) | $4,056.3bn | $4,850.2bn | $741.3bn | $52.6bn |
| Pension funds | $1,429.4bn | $1,547.6bn | $99.3bn | $18.9bn |
| Registered funds | $3,158.9bn | $4,301.5bn | $1,081.2bn | $61.4bn |
| Rest of the world | $4,289.8bn | $5,195.7bn | $934.2bn | -$28.4bn |
| Banks and credit unions | $908.4bn | $1,018.3bn | $90.3bn | $19.7bn |
| Households and nonprofits (residual) | $199.0bn | $192.0bn | -$848.6bn | $841.7bn |
| Hedge funds and private debt funds | $302.3bn | $360.1bn | $52.3bn | $5.4bn |
| Government-sponsored enterprises and security brokers and dealers | $82.7bn | $99.2bn | $14.7bn | $1.7bn |
| Other holders | $471.9bn | $551.3bn | $63.8bn | $15.5bn |

For households and nonprofits the $841.7bn is not a measured price effect: their net acquisition is the figure that closes the flow table, their amount outstanding is a separate series that moved only from $199.0bn to $192.0bn, and the two do not reconcile, so read this row, and the all-holder row that includes it, as a gap between two series.

## Revisions and the registered statements

Z.1 revises its history at every release. revisions.csv compares every window, group and basis between adjacent releases; 1 release cached so far, so it holds 0 rows. The window 2024Q1-2026Q2 stays fixed in every release; a later quarter enters only the extended window wave_ext.

Registered statements (scored on the first release that carries 2026Q3, expected 10 Dec 2026): each group's share of the 2024Q1-2026Q2 net on that release is compared with the same share on the 11 Sep 2026 release. STABLE means the two differ by less than 2.0 percentage points, MOVED means 2.0 or more, PENDING means no release with 2026Q3 is cached yet. The 2.0 is not calibrated against any earlier revision. A MOVED is a result, written beside the old value.

| Statement | Group | Share, release 20260911 | Share, new release | Absolute change (pp) | Label |
| --- | --- | --- | --- | --- | --- |
| SREV | US insurers (life and property-casualty) | 33.26% | - | - | PENDING |
| SREV-F | Registered funds | 48.52% | - | - | PENDING |
| SREV-R | Rest of the world | 41.92% | - | - | PENDING |

## Columns and words

- **Net acquisition**: purchases minus sales and redemptions over the period, by holders in a sector. **Net issuance**: new bonds issued minus redemptions, by issuers in a sector.
- **Share of the net**: 100 times the group's window sum divided by the all-sector window sum (line 13 for holders, line 1 for issuers); a ratio of sums, never a mean of quarterly shares.
- **Share of the positive flows**: 100 times the group's net acquisition divided by the sum of the positive net acquisitions of the nine groups (three issuer groups); blank when the group's figure is zero or negative.
- **Per-quarter average**: the window sum divided by the number of quarters in the window.
- **Offset ratio**: the absolute all-sector net divided by the sum of the absolute window sums of the 28 holder lines (lines 2, 3 and 12 for issuers); below 0.5 every share in the window is marked offsetting.
- **Residual**: a figure obtained by subtraction (the household line); every error in the other lines lands in it.
- **Seasonally adjusted**: the Fed's annual-rate series divided by 4 (basis fa_div4); the headline basis fu is the unadjusted quarterly figure.
- **pp**: percentage points. **Release**: a dated posting of the Z.1 data (the folder date of its zip). **Z.1**: the Fed's Financial Accounts of the United States.
- **Level**: the amount outstanding at the end of a quarter; LM codes are market value, FL codes state no valuation basis in the dictionary (valuation fl_unspecified).

The twelve CSV files: quarterly.csv (every flow code, 2017Q1 to the latest quarter, both bases), levels.csv (every level code from 2016Q4), windows.csv (window sums, shares, offset ratio and stability flag by side, group and basis), level_shares.csv and level_change.csv, headline.csv (the 2024Q1-2026Q2 shares and the ranks), comparisons.csv (2024Q1-2026Q2 minus each comparison window, in pp), revisions.csv, registered.csv, checks.csv, vintages.csv and fetch_log.csv. Column names ending _usd_mn are millions of dollars; _pct is percent; _pp is percentage points. SOURCES.md lists every request, the wording of every series code and the builder's decisions.

## Citations

Board of Governors of the Federal Reserve System, Financial Accounts of the United States (Z.1), release 20260911, tables F3.5 and S1281 (public domain, 17 U.S.C. 105). BIS Quarterly Review, 16 March 2026 (context figure only). Board of Governors FEDS Note of 12 October 2018 (reinsurance structures). The specification and the supervisor's rulings are in [the spec](../../_research/2026-10-26-Z1-Corporate-Bond-Holders-Spec.md). How the numbers were fetched, the checks and the builder's decisions are in [SOURCES.md](SOURCES.md).
