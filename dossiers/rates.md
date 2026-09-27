# Rates — US Treasuries, JGBs, euro-area government bonds

## Hypothesis

The same three questions apply. First the price: carry, roll, the expected path of policy and inflation, versus term premium. Then who bought, against net supply, after wrappers. Then each channel, including fiscal supply, QT/QE, and cross-currency basis regimes.

## Status

**US 10-year: first pass done (R1, 27 Sep 2026). JGBs and euro-area bonds: open.** The price side is decomposed in [`2026-09-27-R1-Treasury-10y-Decomposition.md`](../2026-09-27-R1-Treasury-10y-Decomposition.md). Real yields and the long end did the work. The split between term premium and expected rates is not measurable on free data, because two models and a survey disagree (HYPOTHESIS). Who bought, against what duration supply, is next (R2). Do not treat Treasury holdings or Fed purchases as a yield result.

## Evidence

What exists is measurement, not the decomposition:

- Treasury net issuance in the monitor is about **$1,930bn** for 2025, with a 2026:Q1 fragment in the note on that row. Source: Z.1, key `treasury_net_issuance_bn`.
- Fed purchases and money-fund sales in 2026 are in the official-plumbing dossier.
- Foreign official, Japan, and China holdings through July 2026 are in the TIC note. They move. The source does not say they caused a curve move.
- A synthesis of who buys Treasuries exists: [`2026-09-11-Who-Buys-Treasuries-Synthesis.md`](../2026-09-11-Who-Buys-Treasuries-Synthesis.md). Bill supply versus shadow money is an earlier test ([`2026-08-22-D1-Bill-Supply-vs-Shadow-Money.md`](../2026-08-22-D1-Bill-Supply-vs-Shadow-Money.md)): bill supply does not, on that test, shrink private shadow money. That is not a term-premium result.
- Dealer and sponsored-repo stocks are large and are collateral and clearing facts. FICC sponsored total was about **$2.3trn** on 20 August 2026, down from the year-end 2025 reading cited on the calendar. Whether that is migration out of sponsored clearing is an open calendar question, not a curve attribution.

**Not in the source, stated in the programme brief:** a net-supply identity for JGBs and for euro-area government bonds; a carry/roll/term-premium split for JGBs and euro-area bonds (the US 10-year now has one, R1); a cross-currency basis regime used as a cause of yields.

## What would change the conclusion

Running step 1 of the update cycle on a stated window for each market, with bands, and only then placing official, dealer, and foreign demand on the same denominator.

## Data used

Z.1 Treasury flows, FiscalData bill supply, TIC Table 5, SOMA, FICC and primary-dealer repo. No JGB or EGB series is carried in the monitor extract because none was identified as a worked series in the notes read.
