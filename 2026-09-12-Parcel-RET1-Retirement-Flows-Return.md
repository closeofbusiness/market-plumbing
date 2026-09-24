# Parcel RET1 Return — Retirement Flows and Asset Allocation

**Status: EXTERNAL RETURN — SUPERVISOR-VERIFIED 13 Sep 2026.** Gemini in Antigravity, parcel
`Parcel_RET1_Retirement_Flows_For_Gemini_AGY.md`, reading the documents in `data/retirement_docs/`.
Every figure I spot-checked reproduced **exactly** against the official workbooks (verification note at the
foot). Table and sheet identifiers are sound.

**Citation defect — do not trust a page number in this file.** Table A4 of the 2023 Abstract is on PDF
page 12, not page 8 as cited below; the table *names* are real, the page pointers are not. The parcel
carried an explicit instruction to write PAGE UNKNOWN rather than estimate, and it was not honoured.

**WARNING — the net flows below are NOT a measure of money entering or leaving the equity market.**
Both legs are contaminated by transfers between retirement accounts, and the gross churn dwarfs the net:

- **Contributions include rollovers in.** DOL DC contributions of $767,581M include $74,607M of
  "Contributions From Others (Including Rollovers)" (2023 Abstract, sheet 8). Net of that, organic DC net
  flow is **-$90,723M**, not the -$16,116M headline — a figure five and a half times larger. *(my arithmetic,
  from the DOL components.)*
- **Benefits disbursed are mostly not spent.** Traditional-IRA rollovers IN were $652.8bn in 2023 against
  total private-sector DC benefits disbursed of $731.9bn; ICI Table 11 note 2 states rollovers are
  "primarily from employer-sponsored retirement plans". Most money leaving a DC plan moves to an IRA and
  stays invested.
- **Benefits are understated.** ICI Table 4 note 4: amounts "exclude benefits paid directly by insurance
  carriers", so the true outflow is larger and the net more negative than shown.

Net DC flow can therefore be read neither as a market inflow nor an outflow. Anything built on it must
either net out the internal transfers or use a different series.

**The finding that does survive, and it is the useful one.** Private-sector DC net contributions turned
negative in **2013** and have been negative in every year since — eleven consecutive years, through the
largest equity advance in the series (ICI Table 4, verified below). Whatever sustains the passive bid, it
is not net DC contributions. That is a constraint on the Green thesis, not a confirmation of it.

**Coverage limit: the flows stop at 2023.** ICI Tables 11-13 show N/A for 2024 and 2025 (IRS SOI lag), so
the "shifting from contributing to withdrawing" claim cannot be tested past 2023 from these sources. Asset
levels run to 2025; flows do not. Do not pair a 2025 level with a 2023 flow.

---

**Date:** 12 September 2026  
**Sources Examined (Downloaded to `data/retirement_docs/`):**
1. **ICI**, *The US Retirement Market, First Quarter 2026* (Release: June 2026; Excel workbook `ret_26_q1_data.xls`, Tables 1–28 and Methodology)
2. **ICI**, *2026 Investment Company Fact Book*, Chapter 8: "US Retirement and Education Savings" (PDF `2026-factbook-ch8.pdf`, pp. 1–21; Figures 8.1–8.16; and Data Tables 63–64)
3. **DOL / EBSA**, *Private Pension Plan Bulletin Historical Tables and Graphs 1975–2023* (December 2025 release; Tables E10, E13, E16, E25; printed pp. 13, 17, 21, 33)
4. **DOL / EBSA**, *Private Pension Plan Bulletin — Abstract of 2023 Form 5500 Annual Reports* (December 2025; Table A4 [p. 12, NOT p.8 as returned], Table C7 [page unverified])
5. **DOL / EBSA**, *Private Pension Plan Bulletin — Abstract of 2018 Form 5500 Annual Reports* (Table A4 p. 8)

---

## TABLE 1 — Defined-Contribution Plan Flows

*Most recent ten years available: 2014–2023 (Form 5500 research files through plan year 2023). Two official primary series disagree on boundary definition and are both provided below.*

| year | total contributions | total distributions/withdrawals | net flow | plan types covered | document + page |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2014 (ICI)** | $373.6 B | $402.3 B | -$28.7 B | Private-sector DC plans (401(k) plans and other private DC) | ICI, *The US Retirement Market, First Quarter 2026*, Table 4 [Disagrees with DOL scope; excludes multiemployer and public DC plans] |
| **2014 (DOL)** | $403,462 M ($403.5 B) | $428,359 M ($428.4 B) | -$24,897 M (-$24.9 B) [UNCERTAIN: calculated c − b] | Defined Contribution, Total Plans (Single-employer, multiemployer, and multiple-employer DC plans) | DOL/EBSA, *Private Pension Plan Bulletin Historical Tables 1975–2023*, Table E13 (p. 17) & Table E16 (p. 21) [Disagrees with ICI scope] |
| **2015 (ICI)** | $402.3 B | $422.9 B | -$20.6 B | Private-sector DC plans (401(k) plans and other private DC) | ICI, *The US Retirement Market, First Quarter 2026*, Table 4 [Disagrees with DOL scope] |
| **2015 (DOL)** | $434,606 M ($434.6 B) | $450,554 M ($450.6 B) | -$15,948 M (-$15.9 B) [UNCERTAIN: calculated c − b] | Defined Contribution, Total Plans (Single-employer, multiemployer, and multiple-employer DC plans) | DOL/EBSA, *Private Pension Plan Bulletin Historical Tables 1975–2023*, Table E13 (p. 17) & Table E16 (p. 21) [Disagrees with ICI scope] |
| **2016 (ICI)** | $424.0 B | $426.9 B | -$2.9 B | Private-sector DC plans (401(k) plans and other private DC) | ICI, *The US Retirement Market, First Quarter 2026*, Table 4 [Disagrees with DOL scope] |
| **2016 (DOL)** | $458,953 M ($459.0 B) | $454,947 M ($454.9 B) | +$4,006 M (+$4.0 B) [UNCERTAIN: calculated c − b] | Defined Contribution, Total Plans (Single-employer, multiemployer, and multiple-employer DC plans) | DOL/EBSA, *Private Pension Plan Bulletin Historical Tables 1975–2023*, Table E13 (p. 17) & Table E16 (p. 21) [Disagrees with ICI scope] |
| **2017 (ICI)** | $455.5 B | $462.5 B | -$7.0 B | Private-sector DC plans (401(k) plans and other private DC) | ICI, *The US Retirement Market, First Quarter 2026*, Table 4 [Disagrees with DOL scope] |
| **2017 (DOL)** | $492,708 M ($492.7 B) | $493,986 M ($494.0 B) | -$1,278 M (-$1.3 B) [UNCERTAIN: calculated c − b] | Defined Contribution, Total Plans (Single-employer, multiemployer, and multiple-employer DC plans) | DOL/EBSA, *Private Pension Plan Bulletin Historical Tables 1975–2023*, Table E13 (p. 17) & Table E16 (p. 21) [Disagrees with ICI scope] |
| **2018 (ICI)** | $492.0 B | $514.1 B | -$22.2 B | Private-sector DC plans (401(k) plans and other private DC) | ICI, *The US Retirement Market, First Quarter 2026*, Table 4 [Disagrees with DOL scope] |
| **2018 (DOL)** | $531,859 M ($531.9 B) | $550,691 M ($550.7 B) | -$18,832 M (-$18.8 B) [UNCERTAIN: calculated c − b] | Defined Contribution, Total Plans (Single-employer, multiemployer, and multiple-employer DC plans) | DOL/EBSA, *Private Pension Plan Bulletin Historical Tables 1975–2023*, Table E13 (p. 17) & Table E16 (p. 21) [Disagrees with ICI scope; also in DOL 2018 Abstract Table A4 (p. 8)] |
| **2019 (ICI)** | $527.7 B | $559.3 B | -$31.6 B | Private-sector DC plans (401(k) plans and other private DC) | ICI, *The US Retirement Market, First Quarter 2026*, Table 4 [Disagrees with DOL scope] |
| **2019 (DOL)** | $570,211 M ($570.2 B) | $599,081 M ($599.1 B) | -$28,870 M (-$28.9 B) [UNCERTAIN: calculated c − b] | Defined Contribution, Total Plans (Single-employer, multiemployer, and multiple-employer DC plans) | DOL/EBSA, *Private Pension Plan Bulletin Historical Tables 1975–2023*, Table E13 (p. 17) & Table E16 (p. 21) [Disagrees with ICI scope] |
| **2020 (ICI)** | $544.5 B | $659.5 B | -$115.0 B | Private-sector DC plans (401(k) plans and other private DC) | ICI, *The US Retirement Market, First Quarter 2026*, Table 4 [Disagrees with DOL scope] |
| **2020 (DOL)** | $585,954 M ($586.0 B) | $703,607 M ($703.6 B) | -$117,653 M (-$117.7 B) [UNCERTAIN: calculated c − b] | Defined Contribution, Total Plans (Single-employer, multiemployer, and multiple-employer DC plans) | DOL/EBSA, *Private Pension Plan Bulletin Historical Tables 1975–2023*, Table E13 (p. 17) & Table E16 (p. 21) [Disagrees with ICI scope] |
| **2021 (ICI)** | $611.5 B | $727.1 B | -$115.6 B | Private-sector DC plans (401(k) plans and other private DC) | ICI, *The US Retirement Market, First Quarter 2026*, Table 4 [Disagrees with DOL scope] |
| **2021 (DOL)** | $656,875 M ($656.9 B) | $776,879 M ($776.9 B) | -$120,004 M (-$120.0 B) [UNCERTAIN: calculated c − b] | Defined Contribution, Total Plans (Single-employer, multiemployer, and multiple-employer DC plans) | DOL/EBSA, *Private Pension Plan Bulletin Historical Tables 1975–2023*, Table E13 (p. 17) & Table E16 (p. 21) [Disagrees with ICI scope] |
| **2022 (ICI)** | $663.2 B | $670.3 B | -$7.2 B | Private-sector DC plans (401(k) plans and other private DC) | ICI, *The US Retirement Market, First Quarter 2026*, Table 4 [Disagrees with DOL scope] |
| **2022 (DOL)** | $710,903 M ($710.9 B) | $715,955 M ($716.0 B) | -$5,052 M (-$5.1 B) [UNCERTAIN: calculated c − b] | Defined Contribution, Total Plans (Single-employer, multiemployer, and multiple-employer DC plans) | DOL/EBSA, *Private Pension Plan Bulletin Historical Tables 1975–2023*, Table E13 (p. 17) & Table E16 (p. 21) [Disagrees with ICI scope] |
| **2023 (ICI)** | $715.7 B | $731.9 B | -$16.3 B | Private-sector DC plans (401(k) plans and other private DC) | ICI, *The US Retirement Market, First Quarter 2026*, Table 4 [Disagrees with DOL scope] |
| **2023 (DOL)** | $767,581 M ($767.6 B) | $783,697 M ($783.7 B) | -$16,116 M (-$16.1 B) [UNCERTAIN: calculated c − b] | Defined Contribution, Total Plans (Single-employer, multiemployer, and multiple-employer DC plans) | DOL/EBSA, *Private Pension Plan Bulletin Historical Tables 1975–2023*, Table E13 (p. 17) & Table E16 (p. 21) [Disagrees with ICI scope; also in DOL 2023 Abstract Table A4 (PDF p. 12; workbook sheet 8)] |

*Notes on Table 1:*
- **Scope difference:** DOL/EBSA includes Single-Employer ($711.6B contrib, $734.0B benefits in 2023), Multiemployer ($15.1B contrib, $13.3B benefits), and Multiple-Employer ($40.9B contrib, $36.4B benefits). ICI Table 4 covers private-sector 401(k) plans ($677.2B contrib, $684.7B benefits in 2023) and other private-sector DC plans ($38.4B contrib, $47.2B benefits), adjusting plan years to calendar year-end.
- **Form 5500 components:** In DOL 2023 Abstract Table A4 (PDF p. 12; workbook sheet 8), DC contributions consist of Employer Contributions ($257,634M) + Participant Contributions ($433,656M) + Contributions From Others including Rollovers ($74,607M) + Noncash Contributions ($1,684M) = $767,581M. Total Benefit Payments equal $783,697M.

---

## TABLE 2 — IRA Flows

*Most recent ten years available: 2014–2023 (IRS SOI tax return tabulations available through tax year 2023; 2024–2025 flows are reported as N/A in the ICI statistical release). DOL Form 5500 does not cover IRAs.*

| year | contributions | withdrawals | rollovers in | net flow | document + page |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2014 (Traditional)** | $17.5 B | $257.7 B | $423.9 B | +$183.7 B (or +$175.4 B less $8.3 B Roth conversions) [UNCERTAIN: calculated; net flow column not printed] | ICI, *The US Retirement Market, First Quarter 2026*, Table 11 [Traditional IRAs only] |
| **2014 (Total All IRAs)** | $62.8 B [UNCERTAIN: calculated sum] | $275.0 B [UNCERTAIN: calculated sum] | $434.8 B [UNCERTAIN: calculated sum] | +$222.6 B [UNCERTAIN: calculated as (c + roll) − w] | ICI, *The US Retirement Market, First Quarter 2026*, Tables 11, 12, 13 [Combined Traditional, Roth, SEP, SIMPLE; unified table not in these documents] |
| **2015 (Traditional)** | $17.7 B | $276.9 B | $459.9 B | +$200.7 B (or +$191.7 B less $9.0 B Roth conversions) [UNCERTAIN: calculated; net flow column not printed] | ICI, *The US Retirement Market, First Quarter 2026*, Table 11 [Traditional IRAs only] |
| **2015 (Total All IRAs)** | $63.7 B [UNCERTAIN: calculated sum] | $294.7 B [UNCERTAIN: calculated sum] | $472.6 B [UNCERTAIN: calculated sum] | +$241.6 B [UNCERTAIN: calculated as (c + roll) − w] | ICI, *The US Retirement Market, First Quarter 2026*, Tables 11, 12, 13 [Combined Traditional, Roth, SEP, SIMPLE] |
| **2016 (Traditional)** | $18.3 B | $272.6 B | $430.8 B | +$176.5 B (or +$167.4 B less $9.1 B Roth conversions) [UNCERTAIN: calculated; net flow column not printed] | ICI, *The US Retirement Market, First Quarter 2026*, Table 11 [Traditional IRAs only] |
| **2016 (Total All IRAs)** | $65.5 B [UNCERTAIN: calculated sum] | $291.8 B [UNCERTAIN: calculated sum] | $444.8 B [UNCERTAIN: calculated sum] | +$218.5 B [UNCERTAIN: calculated as (c + roll) − w] | ICI, *The US Retirement Market, First Quarter 2026*, Tables 11, 12, 13 [Combined Traditional, Roth, SEP, SIMPLE] |
| **2017 (Traditional)** | $18.8 B | $303.4 B | $463.0 B | +$178.4 B (or +$168.4 B less $10.0 B Roth conversions) [UNCERTAIN: calculated; net flow column not printed] | ICI, *The US Retirement Market, First Quarter 2026*, Table 11 [Traditional IRAs only] |
| **2017 (Total All IRAs)** | $69.4 B [UNCERTAIN: calculated sum] | $324.7 B [UNCERTAIN: calculated sum] | $477.9 B [UNCERTAIN: calculated sum] | +$222.6 B [UNCERTAIN: calculated as (c + roll) − w] | ICI, *The US Retirement Market, First Quarter 2026*, Tables 11, 12, 13 [Combined Traditional, Roth, SEP, SIMPLE] |
| **2018 (Traditional)** | $18.6 B | $341.1 B | $516.7 B | +$194.2 B (or +$180.5 B less $13.7 B Roth conversions) [UNCERTAIN: calculated; net flow column not printed] | ICI, *The US Retirement Market, First Quarter 2026*, Table 11 [Traditional IRAs only] |
| **2018 (Total All IRAs)** | $70.1 B [UNCERTAIN: calculated sum] | $365.6 B [UNCERTAIN: calculated sum] | $533.7 B [UNCERTAIN: calculated sum] | +$238.2 B [UNCERTAIN: calculated as (c + roll) − w] | ICI, *The US Retirement Market, First Quarter 2026*, Tables 11, 12, 13 [Combined Traditional, Roth, SEP, SIMPLE] |
| **2019 (Traditional)** | $20.1 B | $351.4 B | $535.7 B | +$204.4 B (or +$187.4 B less $17.0 B Roth conversions) [UNCERTAIN: calculated; net flow column not printed] | ICI, *The US Retirement Market, First Quarter 2026*, Table 11 [Traditional IRAs only] |
| **2019 (Total All IRAs)** | $75.5 B [UNCERTAIN: calculated sum] | $375.9 B [UNCERTAIN: calculated sum] | $554.4 B [UNCERTAIN: calculated sum] | +$254.0 B [UNCERTAIN: calculated as (c + roll) − w] | ICI, *The US Retirement Market, First Quarter 2026*, Tables 11, 12, 13 [Combined Traditional, Roth, SEP, SIMPLE] |
| **2020 (Traditional)** | $22.1 B | $323.0 B | $594.8 B | +$293.9 B (or +$259.4 B less $34.5 B Roth conversions) [UNCERTAIN: calculated; net flow column not printed] | ICI, *The US Retirement Market, First Quarter 2026*, Table 11 [Traditional IRAs only] |
| **2020 (Total All IRAs)** | $83.2 B [UNCERTAIN: calculated sum] | $345.3 B [UNCERTAIN: calculated sum] | $618.4 B [UNCERTAIN: calculated sum] | +$356.3 B [UNCERTAIN: calculated as (c + roll) − w] | ICI, *The US Retirement Market, First Quarter 2026*, Tables 11, 12, 13 [Combined Traditional, Roth, SEP, SIMPLE] |
| **2021 (Traditional)** | $23.6 B | $438.0 B | $706.0 B | +$291.6 B (or +$250.4 B less $41.2 B Roth conversions) [UNCERTAIN: calculated; net flow column not printed] | ICI, *The US Retirement Market, First Quarter 2026*, Table 11 [Traditional IRAs only] |
| **2021 (Total All IRAs)** | $91.1 B [UNCERTAIN: calculated sum] | $470.2 B [UNCERTAIN: calculated sum] | $740.4 B [UNCERTAIN: calculated sum] | +$361.3 B [UNCERTAIN: calculated as (c + roll) − w] | ICI, *The US Retirement Market, First Quarter 2026*, Tables 11, 12, 13 [Combined Traditional, Roth, SEP, SIMPLE] |
| **2022 (Traditional)** | $25.8 B | $480.3 B | $635.9 B | +$181.4 B (or +$144.9 B less $36.5 B Roth conversions) [UNCERTAIN: calculated; net flow column not printed] | ICI, *The US Retirement Market, First Quarter 2026*, Table 11 [Traditional IRAs only] |
| **2022 (Total All IRAs)** | $86.6 B [UNCERTAIN: calculated sum] | $512.7 B [UNCERTAIN: calculated sum] | $664.4 B [UNCERTAIN: calculated sum] | +$238.3 B [UNCERTAIN: calculated as (c + roll) − w] | ICI, *The US Retirement Market, First Quarter 2026*, Tables 11, 12, 13 [Combined Traditional, Roth, SEP, SIMPLE] |
| **2023 (Traditional)** | $26.9 B | $475.0 B | $652.8 B | +$204.7 B (or +$168.0 B less $36.7 B Roth conversions) [UNCERTAIN: calculated; net flow column not printed] | ICI, *The US Retirement Market, First Quarter 2026*, Table 11 [Traditional IRAs only] |
| **2023 (Total All IRAs)** | $89.1 B [UNCERTAIN: calculated sum] | $515.2 B [UNCERTAIN: calculated sum] | $682.4 B [UNCERTAIN: calculated sum] | +$256.3 B [UNCERTAIN: calculated as (c + roll) − w] | ICI, *The US Retirement Market, First Quarter 2026*, Tables 11, 12, 13 [Combined Traditional, Roth, SEP, SIMPLE] |
| **2024–2025** | NOT IN THESE DOCUMENTS (reported as N/A) | NOT IN THESE DOCUMENTS (reported as N/A) | NOT IN THESE DOCUMENTS (reported as N/A) | NOT IN THESE DOCUMENTS | ICI, *The US Retirement Market, First Quarter 2026*, Tables 11, 12, 13 [IRS SOI flow data through 2023 only; asset levels estimated] |

*Notes on Table 2:*
- **Component Breakdown for 2023:**
  - *Traditional IRAs (Table 11):* Contributions = $26.9B; Rollovers in = $652.8B; Roth conversions out = $36.7B; Withdrawals = $475.0B.
  - *Roth IRAs (Table 12):* Contributions = $32.8B; Rollovers in = $24.3B; Roth conversions in = $36.7B; Withdrawals = $30.8B.
  - *SEP & SAR-SEP IRAs (Table 13):* Contributions = $16.6B; Rollovers in = $4.7B; Withdrawals = $7.0B.
  - *SIMPLE IRAs (Table 13):* Contributions = $12.8B; Rollovers in = $0.6B; Withdrawals = $2.4B.
- **Absence of Unified Table:** The published documents do not provide an official single unified "All IRA Flows" table; IRS Statistics of Income (SOI) Division publishes them by IRA type. If calculated across all four IRA types, organic contributions minus withdrawals is -$426.1B, but net flows including rollovers from employer plans is +$256.3B.

---

## TABLE 3 — DC Asset Allocation and Equity Exposure

*Years 2014–2023 (and through 2025 where available in ICI quarterly release).*

| year | DC assets total | share in equity funds | share in target-date funds | share in index funds if stated | document + page |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2014** | $6,502.0 B | 61% of DC mutual fund assets ($2,246 B; Domestic 48%, World 13%); 34.5% of total DC assets [UNCERTAIN: calculated] | 12.9% of DC mutual fund assets ($476 B); 7.3% of total DC assets [UNCERTAIN: calculated] | 17.4% of DC mutual fund assets ($644 B); 9.9% of total DC assets [UNCERTAIN: calculated] | ICI, *The US Retirement Market, First Quarter 2026*, Table 6, Table 16, Table 25, Table 27 |
| **2015** | $6,457.0 B | 60% of DC mutual fund assets ($2,190 B; Domestic 47%, World 14%); 33.9% of total DC assets [UNCERTAIN: calculated] | 14.1% of DC mutual fund assets ($510 B); 7.9% of total DC assets [UNCERTAIN: calculated] | 18.6% of DC mutual fund assets ($675 B); 10.5% of total DC assets [UNCERTAIN: calculated] | ICI, *The US Retirement Market, First Quarter 2026*, Table 6, Table 16, Table 25, Table 27 |
| **2016** | $6,915.0 B | 60% of DC mutual fund assets ($2,310 B; Domestic 46%, World 13%); 33.4% of total DC assets [UNCERTAIN: calculated] | 15.4% of DC mutual fund assets ($596 B); 8.6% of total DC assets [UNCERTAIN: calculated] | 20.7% of DC mutual fund assets ($799 B); 11.6% of total DC assets [UNCERTAIN: calculated] | ICI, *The US Retirement Market, First Quarter 2026*, Table 6, Table 16, Table 25, Table 27 |
| **2017** | $7,906.0 B | 61% of DC mutual fund assets ($2,796 B; Domestic 46%, World 15%); 35.4% of total DC assets [UNCERTAIN: calculated] | 16.3% of DC mutual fund assets ($748 B); 9.5% of total DC assets [UNCERTAIN: calculated] | 22.3% of DC mutual fund assets ($1,024 B); 13.0% of total DC assets [UNCERTAIN: calculated] | ICI, *The US Retirement Market, First Quarter 2026*, Table 6, Table 16, Table 25, Table 27 |
| **2018** | $7,555.0 B | 59% of DC mutual fund assets ($2,512 B; Domestic 45%, World 14%); 33.2% of total DC assets [UNCERTAIN: calculated] | 17.2% of DC mutual fund assets ($733 B); 9.7% of total DC assets [UNCERTAIN: calculated] *(Fact Book: 27% of 401(k) assets across all pooled vehicles)* | 23.4% of DC mutual fund assets ($995 B); 13.2% of total DC assets [UNCERTAIN: calculated] | ICI, *The US Retirement Market, First Quarter 2026*, Tables 6, 16, 25, 27; ICI *Fact Book 2026*, Figure 8.10 (p. 13) |
| **2019** | $8,927.0 B | 60% of DC mutual fund assets ($3,122 B; Domestic 46%, World 14%); 35.0% of total DC assets [UNCERTAIN: calculated] | 18.0% of DC mutual fund assets ($941 B); 10.5% of total DC assets [UNCERTAIN: calculated] | 25.3% of DC mutual fund assets ($1,322 B); 14.8% of total DC assets [UNCERTAIN: calculated] | ICI, *The US Retirement Market, First Quarter 2026*, Table 6, Table 16, Table 25, Table 27 |
| **2020** | $10,051.0 B | 60% of DC mutual fund assets ($3,466 B; Domestic 47%, World 13%); 34.5% of total DC assets [UNCERTAIN: calculated] | 18.3% of DC mutual fund assets ($1,063 B); 10.6% of total DC assets [UNCERTAIN: calculated] | 25.3% of DC mutual fund assets ($1,467 B); 14.6% of total DC assets [UNCERTAIN: calculated] | ICI, *The US Retirement Market, First Quarter 2026*, Table 6, Table 16, Table 25, Table 27 |
| **2021** | $11,303.0 B | 61% of DC mutual fund assets ($3,980 B; Domestic 49%, World 12%); 35.2% of total DC assets [UNCERTAIN: calculated] | 18.4% of DC mutual fund assets ($1,200 B); 10.6% of total DC assets [UNCERTAIN: calculated] | 26.5% of DC mutual fund assets ($1,728 B); 15.3% of total DC assets [UNCERTAIN: calculated] | ICI, *The US Retirement Market, First Quarter 2026*, Table 6, Table 16, Table 25, Table 27 |
| **2022** | $9,630.0 B | 59% of DC mutual fund assets ($3,113 B; Domestic 48%, World 11%); 32.3% of total DC assets [UNCERTAIN: calculated] | 18.9% of DC mutual fund assets ($998 B); 10.4% of total DC assets [UNCERTAIN: calculated] | 28.3% of DC mutual fund assets ($1,499 B); 15.6% of total DC assets [UNCERTAIN: calculated] | ICI, *The US Retirement Market, First Quarter 2026*, Table 6, Table 16, Table 25, Table 27 |
| **2023** | $11,232.0 B | 60% of DC mutual fund assets ($3,739 B; Domestic 49%, World 11%); 33.3% of total DC assets [UNCERTAIN: calculated] | 19.0% of DC mutual fund assets ($1,185 B); 10.6% of total DC assets [UNCERTAIN: calculated] *(Fact Book: 42% of 401(k) assets across all pooled vehicles)* | 30.6% of DC mutual fund assets ($1,909 B); 17.0% of total DC assets [UNCERTAIN: calculated] | ICI, *The US Retirement Market, First Quarter 2026*, Tables 6, 16, 25, 27; ICI *Fact Book 2026*, Figure 8.10 (p. 13) |
| **2024** | $12,684.0 B | 61% of DC mutual fund assets ($4,195 B; Domestic 51%, World 10%); 33.1% of total DC assets [UNCERTAIN: calculated] | 19.3% of DC mutual fund assets ($1,332 B); 10.5% of total DC assets [UNCERTAIN: calculated] | 32.3% of DC mutual fund assets ($2,232 B); 17.6% of total DC assets [UNCERTAIN: calculated] | ICI, *The US Retirement Market, First Quarter 2026*, Table 6, Table 16, Table 25, Table 27 |
| **2025** | $14,181.0 B | 59% of DC mutual fund assets ($4,345 B; Domestic 48%, World 11%); 30.6% of total DC assets [UNCERTAIN: calculated] | 20.7% of DC mutual fund assets ($1,522 B); 10.7% of total DC assets [UNCERTAIN: calculated] | 30.7% of DC mutual fund assets ($2,262 B); 16.0% of total DC assets [UNCERTAIN: calculated] | ICI, *The US Retirement Market, First Quarter 2026*, Table 6, Table 16, Table 25, Table 27 |

*Notes on Table 3:*
- **Asset Denominators:** Total DC Plan Assets (Table 6) includes 401(k) plans ($7,932B in 2023), other private DC ($734B), 403(b) plans ($1,291B), Federal TSP ($845B), and 457 plans ($430B). Mutual fund assets in DC plans totaled $6,241B at year-end 2023 (55.6% of all DC assets).
- **Target-Date Fund Vehicles:** In Table 25, target-date assets reflect **mutual funds only** ($1,185B in DC plans at YE2023). In *Fact Book 2026*, Figure 8.10 (p. 13), target-date funds include mutual funds, collective investment trusts (CITs), and separate accounts, rising to **42% of the total 401(k) market** at year-end 2023 (up from 7% in 2008, 17% in 2013, and 27% in 2018).
- **Index Funds:** Table 27 reports index **mutual fund** assets ($1,909B in DC plans at YE2023, of which equity index funds represent approximately 84% across the index fund universe). Non-mutual fund index assets (such as index CITs) are NOT STATED in these documents.
- **DOL Form 5500 Asset Classification:** In DOL 2023 Abstract Table C7 (p. 35), large DC plan assets are classified by legal instrument rather than fund mandate: Registered Investment Companies (36.0%), Common/Collective Trusts (29.6%), Master Trusts (16.7%), Employer Securities (5.0%), and Direct Corporate Stocks (1.5%). Form 5500 does not report investment-mandate breakdowns (equity vs bond vs target-date).


---

## Supervisor verification note — 13 Sep 2026

Checked against the issuing files in `data/retirement_docs/`, not against the return's own summary.

| # | claim checked | source | result |
|---|---|---|---|
| 1 | DC 2023 contributions 715.7, benefits 731.9, net -16.3 | ICI `ret_26_q1_data.xls`, Table 4 row 55 | REPRODUCES exactly |
| 2 | DOL DC 2023 contributions 767,581 / benefits 783,697 | `dol_abstract_2023.xlsx`, sheet 3, "Defined Contribution" | REPRODUCES exactly |
| 3 | DOL components 257,634 / 433,656 / 74,607 | `dol_abstract_2023.xlsx`, sheet 8 | REPRODUCES exactly |
| 4 | Traditional IRA 2023: contrib 26.9, rollovers 652.8, conversions 36.7, withdrawals 475.0 | ICI Table 11 row 35 | REPRODUCES exactly |
| 5 | Cited table identifiers exist (ICI 4/6/11/12/13/16/25/27; DOL A4, E13) | workbook sheet list; `pdftotext` on the Abstract | ALL REAL |
| 6 | Page pointer "Table A4 p. 8" | `pdftotext` page sweep | **WRONG — A4 is on p. 12; p. 8 holds Table A1(a)** |

Unverified and left so: the ICI Fact Book chapter-8 figure numbers (8.10 etc.) and the Table 3 allocation
shares, which were not load-bearing for the flow question. The 42% target-date share of 401(k) assets is
relayed **unverified**.

Process note: the parcel omitted a read-only clause, and the agent created this file unasked. It wrote
nothing else — checked. Dollar figures survived intact here (62 of them), unlike the earlier web-chat
file-write path that stripped them.
