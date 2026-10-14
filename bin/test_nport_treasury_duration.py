#!/usr/bin/env python3
"""Tests for bin/nport_treasury_duration.py. stdlib unittest, synthetic data only.

  python3 bin/test_nport_treasury_duration.py

Every zip is built under a temporary directory with the real header lines of the SEC bulk N-PORT tables hard-coded below
(SUBMISSION 7 columns, REGISTRANT 12, FUND_REPORTED_INFO 47, FUND_REPORTED_HOLDING 22, DEBT_SECURITY 9, INTEREST_RATE_RISK 13).
No real holding row is used. The tests call the script's functions, not its command line. The script runs this file as
pre-flight before it builds anything (spec N11).
"""
import datetime as dt
import hashlib
import os
import sys
import tempfile
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import nport_treasury_duration as ntd

D = dt.date

SUB_H = "ACCESSION_NUMBER FILING_DATE FILE_NUM SUB_TYPE REPORT_ENDING_PERIOD REPORT_DATE IS_LAST_FILING".split()
REG_H = "ACCESSION_NUMBER CIK REGISTRANT_NAME FILE_NUM LEI ADDRESS1 ADDRESS2 CITY STATE COUNTRY ZIP PHONE".split()
INFO_H = ("ACCESSION_NUMBER SERIES_NAME SERIES_ID SERIES_LEI TOTAL_ASSETS TOTAL_LIABILITIES NET_ASSETS ASSETS_ATTRBT_TO_MISC_SECURITY "
          "ASSETS_INVESTED BORROWING_PAY_WITHIN_1YR CTRLD_COMPANIES_PAY_WITHIN_1YR OTHER_AFFILIA_PAY_WITHIN_1YR OTHER_PAY_WITHIN_1YR "
          "BORROWING_PAY_AFTER_1YR CTRLD_COMPANIES_PAY_AFTER_1YR OTHER_AFFILIA_PAY_AFTER_1YR OTHER_PAY_AFTER_1YR DELAYED_DELIVERY "
          "STANDBY_COMMITMENT LIQUIDATION_PREFERENCE CASH_NOT_RPTD_IN_C_OR_D CREDIT_SPREAD_3MON_INVEST CREDIT_SPREAD_1YR_INVEST "
          "CREDIT_SPREAD_5YR_INVEST CREDIT_SPREAD_10YR_INVEST CREDIT_SPREAD_30YR_INVEST CREDIT_SPREAD_3MON_NONINVEST "
          "CREDIT_SPREAD_1YR_NONINVEST CREDIT_SPREAD_5YR_NONINVEST CREDIT_SPREAD_10YR_NONINVEST CREDIT_SPREAD_30YR_NONINVEST "
          "IS_NON_CASH_COLLATERAL NET_REALIZE_GAIN_NONDERIV_MON1 NET_UNREALIZE_AP_NONDERIV_MON1 NET_REALIZE_GAIN_NONDERIV_MON2 "
          "NET_UNREALIZE_AP_NONDERIV_MON2 NET_REALIZE_GAIN_NONDERIV_MON3 NET_UNREALIZE_AP_NONDERIV_MON3 SALES_FLOW_MON1 "
          "REINVESTMENT_FLOW_MON1 REDEMPTION_FLOW_MON1 SALES_FLOW_MON2 REINVESTMENT_FLOW_MON2 REDEMPTION_FLOW_MON2 SALES_FLOW_MON3 "
          "REINVESTMENT_FLOW_MON3 REDEMPTION_FLOW_MON3").split()
HOLD_H = ("ACCESSION_NUMBER HOLDING_ID ISSUER_NAME ISSUER_LEI ISSUER_TITLE ISSUER_CUSIP BALANCE UNIT OTHER_UNIT_DESC CURRENCY_CODE "
          "CURRENCY_VALUE EXCHANGE_RATE PERCENTAGE PAYOFF_PROFILE ASSET_CAT OTHER_ASSET ISSUER_TYPE OTHER_ISSUER INVESTMENT_COUNTRY "
          "IS_RESTRICTED_SECURITY FAIR_VALUE_LEVEL DERIVATIVE_CAT").split()
DEBT_H = ("HOLDING_ID MATURITY_DATE COUPON_TYPE ANNUALIZED_RATE IS_DEFAULT ARE_ANY_INTEREST_PAYMENT IS_ANY_PORTION_INTEREST_PAID "
          "IS_CONVTIBLE_MANDATORY IS_CONVTIBLE_CONTINGENT").split()
IRR_H = ("ACCESSION_NUMBER INTEREST_RATE_RISK_ID CURRENCY_CODE INTRST_RATE_CHANGE_3MON_DV01 INTRST_RATE_CHANGE_1YR_DV01 "
         "INTRST_RATE_CHANGE_5YR_DV01 INTRST_RATE_CHANGE_10YR_DV01 INTRST_RATE_CHANGE_30YR_DV01 INTRST_RATE_CHANGE_3MON_DV100 "
         "INTRST_RATE_CHANGE_1YR_DV100 INTRST_RATE_CHANGE_5YR_DV100 INTRST_RATE_CHANGE_10YR_DV100 INTRST_RATE_CHANGE_30YR_DV100").split()
assert (len(SUB_H), len(REG_H), len(INFO_H), len(HOLD_H), len(DEBT_H), len(IRR_H)) == (7, 12, 47, 22, 9, 13)


def tsv(header, rows):
    lines = ["\t".join(header)]
    for r in rows:
        lines.append("\t".join(str(r.get(c, "")) for c in header))
    return "\n".join(lines) + "\n"


def make_zip(path, subs, regs, infos, holds, debts=(), irrs=()):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("SUBMISSION.tsv", tsv(SUB_H, subs))
        z.writestr("REGISTRANT.tsv", tsv(REG_H, regs))
        z.writestr("FUND_REPORTED_INFO.tsv", tsv(INFO_H, infos))
        z.writestr("FUND_REPORTED_HOLDING.tsv", tsv(HOLD_H, holds))
        z.writestr("DEBT_SECURITY.tsv", tsv(DEBT_H, debts))
        z.writestr("INTEREST_RATE_RISK.tsv", tsv(IRR_H, irrs))


def filing(acc, sub_type, filed, reported, sid, cik, nav="1000000", name="Test Fund"):
    """One filing as the three metadata rows (SUBMISSION, REGISTRANT, FUND_REPORTED_INFO)."""
    return (dict(ACCESSION_NUMBER=acc, FILING_DATE=filed, SUB_TYPE=sub_type, REPORT_DATE=reported),
            dict(ACCESSION_NUMBER=acc, CIK=cik, REGISTRANT_NAME="Test Trust"),
            dict(ACCESSION_NUMBER=acc, SERIES_ID=sid, SERIES_NAME=name, NET_ASSETS=nav))


def hold(acc, hid, cusip, cat="DBT", itype="UST", bal="1000", val="990", ccy="USD", payoff="Long", unit="PA", pct="", title="", name="UNITED STATES TREAS"):
    return dict(ACCESSION_NUMBER=acc, HOLDING_ID=hid, ISSUER_NAME=name, ISSUER_TITLE=title, ISSUER_CUSIP=cusip, BALANCE=bal, UNIT=unit,
                CURRENCY_CODE=ccy, CURRENCY_VALUE=val, PERCENTAGE=pct, PAYOFF_PROFILE=payoff, ASSET_CAT=cat, ISSUER_TYPE=itype)


def flat_r2_setup(r2, y=4.0, real=1.0):
    """A flat 4% nominal and 1% real curve dated 2023-12-29, in the shape r2.load_curve returns."""
    nom = {k: y for k in ("1 Mo", "1.5 Month", "2 Mo", "3 Mo", "4 Mo", "6 Mo", "1 Yr", "2 Yr", "3 Yr", "5 Yr", "7 Yr", "10 Yr", "20 Yr", "30 Yr")}
    rl = {k: real for k in ("5 YR", "7 YR", "10 YR", "20 YR", "30 YR")}
    return {D(2023, 12, 29): nom}, {D(2023, 12, 29): rl}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = self.tmp.name

    def zip_path(self, name):
        return os.path.join(self.dir, name)

    def filings_from(self, name, zipi, specs, holds=(), debts=(), irrs=()):
        """Build a zip from filing specs [(acc, sub_type, filed, reported, sid, cik, nav)] and load it as the script does."""
        parts = [filing(*s) for s in specs]
        path = self.zip_path(name)
        make_zip(path, [p[0] for p in parts], [p[1] for p in parts], [p[2] for p in parts], list(holds), list(debts), list(irrs))
        z = zipfile.ZipFile(path)
        fl = ntd.load_zip_filings(z, zipi)
        ntd.scan_zip_holdings(z, fl)
        return z, fl


class TestSurvivors(Base):
    def test_1_guard_fails_on_a_hand_built_duplicate_map(self):
        # (C2) one (fund, report month) selected twice must be reported as a FAIL; a clean map as a PASS.
        dup = [(("S", "S1"), (2023, 12), "A1"), (("S", "S1"), (2023, 12), "A2"), (("S", "S2"), (2023, 12), "B1")]
        clean = [(("S", "S1"), (2023, 12), "A1"), (("S", "S1"), (2024, 1), "A2"), (("S", "S2"), (2023, 12), "B1")]
        self.assertEqual(ntd.check_unique_survivors(dup), "FAIL", "the guard passed a duplicated selection: it is worthless")
        self.assertEqual(ntd.check_unique_survivors(clean), "PASS")

    def test_1b_summed_once_guard_fails_on_a_double_sum_and_on_two_windows(self):
        # (C2, second assertion) on the accessions Ctx.add actually summed: once into one window, as many lines as pass A counted
        tsy = {"A1": 3, "B1": 2, "A2": 1}
        clean = {("base", 0): {"A1": 3, "B1": 2}, ("base", 1): {"A2": 1}, ("matched", 0): {"A1": 3}}
        self.assertEqual(ntd.check_summed_once(clean, tsy), "PASS")
        twice = {("base", 0): {"A1": 6, "B1": 2}, ("base", 1): {"A2": 1}}
        self.assertEqual(ntd.check_summed_once(twice, tsy), "FAIL", "an accession whose lines were added twice into one window passed")
        two_windows = {("base", 0): {"A1": 3, "B1": 2}, ("base", 1): {"A1": 3, "A2": 1}}
        self.assertEqual(ntd.check_summed_once(two_windows, tsy), "FAIL", "an accession summed into two windows passed")
        self.assertEqual(ntd.check_summed_once({("base", 0): {"ZZ": 1}}, tsy), "FAIL", "an accession pass A never counted passed")
        # the wiring: Ctx.add records one count per line and vintage, so adding the same line twice is caught
        r2 = ntd.load_by_path("r2_for_test_c2", os.path.join(HERE, "r2_duration_supply.py"))
        nom, real = flat_r2_setup(r2)
        fixed = ntd.r2_fixed_curve(r2, nom, real, "2023-12-31")
        w = ntd.Window(0, 2024, 1)
        _, fl = self.filings_from("2024q1_nport.zip", 0, [("Q1", "NPORT-P", "10-FEB-2024", "29-DEC-2023", "S1", "100")])
        f = fl[0]
        ctx = ntd.Ctx(r2, ntd.Pricer(r2, nom, real, fixed, fixed), {}, {}, [w], {"Q1": f})
        L = ntd.Line("Q1", "1", "912810", 1e9, 9.8e8, "", "", False)
        ctx.add("T", L, f, 0, 3, "unpriced", 6, 3.0, None)
        self.assertEqual({k: dict(v) for k, v in ctx.summed.items()}, {("base", 0): {"Q1": 1}, ("matched", 0): {"Q1": 1}})
        self.assertEqual(ntd.check_summed_once(ctx.summed, {"Q1": 1}), "PASS")
        ctx.add("T", L, f, 0, 3, "unpriced", 6, 3.0, None)
        self.assertEqual(ntd.check_summed_once(ctx.summed, {"Q1": 1}), "FAIL")

    def test_2_amendment_dedup_leaves_one_survivor_carrying_the_amendment(self):
        h0 = [hold("A1", "1", "912797AA1", cat="STIV")] * 3
        h1 = [hold("A2", "9", "912797AA1", cat="STIV")] * 3
        _, f0 = self.filings_from("2024q1_nport.zip", 0, [("A1", "NPORT-P", "10-FEB-2024", "31-DEC-2023", "S1", "100")], h0)
        _, f1 = self.filings_from("2024q2_nport.zip", 1, [("A2", "NPORT-P/A", "20-FEB-2024", "31-DEC-2023", "S1", "100")], h1)
        chosen, info = ntd.pick_survivors(f0 + f1)
        self.assertEqual([f.acc for f in chosen], ["A2"], "one survivor carrying the amendment's accession")
        self.assertEqual(ntd.check_unique_survivors(chosen), "PASS")
        self.assertEqual(info["superseded_filings"], 1)

    def test_3_wrong_zip_makes_c1_fail(self):
        # a synthetic file named 2026q3_nport.zip cannot carry the pinned sha256
        path = self.zip_path("2026q3_nport.zip")
        make_zip(path, [], [], [], [])
        sha = ntd.file_sha256(path)
        with open(path, "rb") as fh:
            self.assertEqual(sha, hashlib.sha256(fh.read()).hexdigest())
        anchors = {("2026q3", "zip_sha256"): ("2f5ee059234d2e28f16d0451d9fcb405aab3dad5d92cded74c8ea9ffc4b66c38", "exact")}
        res, bad, _ = ntd.check_c1({"2026q3_nport.zip": sha}, anchors, {})
        self.assertEqual((res, bad), ("FAIL", ["2026q3_nport.zip"]))
        res, bad, n = ntd.check_c1({"2026q3_nport.zip": sha}, {("2026q3", "zip_sha256"): (sha, "exact")}, {"2026q3_nport.zip": sha})
        self.assertEqual((res, bad, n), ("PASS", [], 2))
        res, _, _ = ntd.check_c1({"2026q3_nport.zip": sha}, {}, {"2026q3_nport.zip": "0" * 64})       # previous stats disagree
        self.assertEqual(res, "FAIL")
        res, _, n = ntd.check_c1({"2024q2_nport.zip": sha}, {("2024q2", "zip_sha256"): (ntd.NO_ANCHOR, "")}, {})
        self.assertEqual((res, n), ("PASS", 0))

    def test_4_month_keying_and_window_fallback(self):
        w = ntd.Window(0, 2024, 1)                       # the 2024q1 zip's window is 2023-12
        self.assertEqual((w.label, w.qend, w.months), ("2023Q4", D(2023, 12, 31), ["2023-11", "2023-12", "2024-01"]))
        specs = [("A1", "NPORT-P", "20-FEB-2024", "29-DEC-2023", "S1", "100"),     # 2023-12-29 keeps its fund in the Dec window
                 ("B1", "NPORT-P", "20-FEB-2024", "30-NOV-2023", "S2", "200"),     # S2 has m-1 and m+1 but no m0
                 ("B2", "NPORT-P", "20-FEB-2024", "31-JAN-2024", "S2", "200")]
        _, fl = self.filings_from("2024q1_nport.zip", 0, specs)
        chosen, _ = ntd.pick_survivors(ntd.eligible_filings(fl, [w], "matched"))
        got = {f.fund[1]: tag for f, tag in ntd.assign_windows(chosen, [w])[0]}
        self.assertEqual(got, {"S1": "m0", "S2": "m-1"})

    def test_5_cross_zip_same_day_stub_and_content_duplicates(self):
        full = [hold("X1", str(i), "912797AA1", cat="STIV") for i in range(3)]
        _, f0 = self.filings_from("2024q1_nport.zip", 0, [("X1", "NPORT-P", "10-FEB-2024", "31-DEC-2023", "S1", "100")], full)
        _, f1 = self.filings_from("2024q2_nport.zip", 1, [("X2", "NPORT-P/A", "10-FEB-2024", "31-DEC-2023", "S1", "100")],
                                  [hold("X2", "9" + str(i), "912797AA1", cat="STIV") for i in range(3)])
        chosen, _ = ntd.pick_survivors(f0 + f1)
        self.assertEqual([f.acc for f in chosen], ["X2"], "a same-day P/A beats the P")
        # a zero-line P/A filed later never replaces a non-empty original
        _, f2 = self.filings_from("2024q3_nport.zip", 2, [("X3", "NPORT-P/A", "30-MAR-2024", "31-DEC-2023", "S1", "100")], [])
        chosen, info = ntd.pick_survivors(f0 + f2)
        self.assertEqual([f.acc for f in chosen], ["X1"])
        self.assertEqual(info["stubs_ignored"], 1)
        # if every candidate is a stub the latest still wins
        chosen, _ = ntd.pick_survivors(f2)
        self.assertEqual([f.acc for f in chosen], ["X3"])
        # an amendment with under half the lines is counted as partial
        _, f4 = self.filings_from("2024q4_nport.zip", 3, [("X4", "NPORT-P/A", "30-MAR-2024", "31-DEC-2023", "S1", "100")],
                                  [hold("X4", "77", "912797AA1", cat="STIV")])
        _, info = ntd.pick_survivors(f0 + f4)
        self.assertEqual(info["partial_amendments"], 1)
        # content duplicates: same CIK, REPORT_DATE, NET_ASSETS and Treasury line count under two fund keys
        two = [("D1", "NPORT-P", "10-FEB-2024", "31-DEC-2023", "S1", "100", "5000000"),
               ("D2", "NPORT-P", "15-FEB-2024", "31-DEC-2023", "S9", "100", "5000000"),
               ("D3", "NPORT-P", "15-FEB-2024", "31-DEC-2023", "S5", "100", "7000000")]
        _, fl = self.filings_from("2024q1b_nport.zip", 0, two,
                                  [hold(a, a + str(i), "912797AA1", cat="STIV") for a in ("D1", "D2", "D3") for i in range(2)])
        chosen, _ = ntd.pick_survivors(fl)
        kept, dropped = ntd.drop_content_duplicates(chosen)
        self.assertEqual(sorted(f.acc for f in kept), ["D2", "D3"])
        self.assertEqual([f.acc for f in dropped], ["D1"])

    def test_5b_base_vintage_lag_cut_keeps_62_days_and_drops_63(self):
        # (N2) a filing counts in the base vintage only if FILING_DATE <= REPORT_DATE + 62 days; the matched vintage has no lag cut
        self.assertEqual(ntd.LAG_DAYS, 62)
        rep = D(2023, 12, 31)
        d62, d63 = rep + dt.timedelta(days=62), rep + dt.timedelta(days=63)
        ds = lambda d: d.strftime("%d-%b-%Y").upper()
        self.assertEqual((ds(d62), ds(d63)), ("02-MAR-2024", "03-MAR-2024"))
        w = ntd.Window(0, 2024, 1)
        _, fl = self.filings_from("2024q1_nport.zip", 0, [("LAG62", "NPORT-P/A", ds(d62), "31-DEC-2023", "S62", "100"),
                                                          ("LAG63", "NPORT-P/A", ds(d63), "31-DEC-2023", "S63", "200")])
        self.assertEqual([(f.acc, (f.fdate - f.rdate).days) for f in fl], [("LAG62", 62), ("LAG63", 63)])
        self.assertEqual([f.acc for f in ntd.eligible_filings(fl, [w], "base")], ["LAG62"], "62 days is in, 63 is out")
        self.assertEqual(sorted(f.acc for f in ntd.eligible_filings(fl, [w], "matched")), ["LAG62", "LAG63"],
                         "the matched vintage has no lag cut")
        sel = ntd.select_vintage(fl, [w], "base")
        self.assertEqual(([f.acc for f in sel["chosen"]], [f.acc for f in sel["kept"]]), (["LAG62"], ["LAG62"]))
        self.assertEqual([[f.acc for f, _ in lst] for lst in sel["assign"].values()], [["LAG62"]])

    def test_5c_matched_vintage_home_zip_cut_drops_filings_in_later_zips(self):
        # (M1) matched vintage = zips up to the window's home zip (the following calendar quarter's); a filing in a later zip is out
        w0, w1 = ntd.Window(0, 2024, 1), ntd.Window(1, 2024, 2)
        self.assertEqual((w0.home_zipi, w1.home_zipi), (0, 1))
        _, f0 = self.filings_from("2024q1_nport.zip", 0, [("HOME", "NPORT-P", "20-FEB-2024", "29-DEC-2023", "S1", "100")])
        _, f1 = self.filings_from("2024q2_nport.zip", 1, [("LATE", "NPORT-P/A", "20-FEB-2024", "29-DEC-2023", "S2", "200"),
                                                          ("NEXT", "NPORT-P", "20-MAY-2024", "28-MAR-2024", "S3", "300")])
        fl = f0 + f1
        # LATE reports the 2023-12 window but sits in the 2024q2 zip, one past that window's home zip; NEXT sits in w1's own home zip
        self.assertEqual(sorted(f.acc for f in ntd.eligible_filings(fl, [w0, w1], "matched")), ["HOME", "NEXT"])
        self.assertEqual(sorted(f.acc for f in ntd.eligible_filings(fl, [w0, w1], "base")), ["HOME", "LATE", "NEXT"],
                         "all three are inside the 62-day lag, so only the home-zip cut separates the vintages")
        got = {v: {wi: [f.acc for f, _ in lst] for wi, lst in ntd.select_vintage(fl, [w0, w1], v)["assign"].items()}
               for v in ("matched", "base")}
        self.assertEqual(got["matched"], {0: ["HOME"], 1: ["NEXT"]})
        self.assertEqual(got["base"], {0: ["HOME", "LATE"], 1: ["NEXT"]})


class TestLines(Base):
    def test_6_filter_keeps_and_excludes(self):
        h = [hold("L1", "1", "912797AA1", cat="STIV"),                                         # STIV bill: kept
             hold("L1", "2", "91282CAA1", cat="SN", title="TREAS INFLATION INDEXED NOTE"),     # SN TIPS: kept
             hold("L1", "3", "91282CAB9", cat="DBT", itype="USGA"),                            # USGA with a 912 CUSIP: kept
             hold("L1", "4", "999999AA9", cat="STIV", itype="UST", name="A MONEY FUND"),        # fund share typed UST, not 912: excluded
             hold("L1", "5", "912810AA6", cat="DIR", itype="UST"),                             # derivative: excluded
             hold("L1", "6", "912828AA8", cat="RA", itype="UST"),                              # repo: excluded
             hold("L1", "7", "38141GAA2", cat="DBT", itype="UST"),                             # non-912 UST: excluded
             hold("L1", "8", "912828AB6", cat="DBT", val=""),                                  # blank value: excluded
             hold("L1", "9", "912828AC4", cat="DBT", payoff="Short", bal="500", val="-480"),   # short: kept, negative par
             hold("L1", "10", "912828AD2", cat="DBT", ccy="EUR"),                              # non-USD: excluded
             hold("L1", "11", "31359MAA1", cat="DBT", itype="USGA"),                           # agency paper: ignored
             hold("L1", "12", "912828AE0", cat="DBT", itype="CORP")]                           # 912 typed CORP: excluded
        z, fl = self.filings_from("2024q1_nport.zip", 0, [("L1", "NPORT-P", "10-FEB-2024", "31-DEC-2023", "S1", "100")], h)
        st, sfl = ntd.scan_zip_holdings(z, fl)
        self.assertEqual(st["holding_rows"], 12)
        self.assertEqual(st["tsy_lines_kept"], 4)
        self.assertEqual([st[f"excl_lines_{r}"] for r in ("non912_ust", "derivative", "repo", "blank_value_or_balance", "non_usd", "912_not_ust_type")],
                         [2, 1, 1, 1, 1, 1])
        self.assertEqual(st["usga_non912_lines_ignored"], 1)
        self.assertEqual((fl[0].total_lines, fl[0].tsy_lines), (12, 4))
        self.assertEqual(st["short_lines"], 1)
        lines = ntd.stream_survivor_lines(z, {"L1"})
        self.assertEqual([L.hid for L in lines], ["1", "2", "3", "9"])
        self.assertEqual(lines[-1].par, -500.0)
        self.assertEqual(ntd.stream_survivor_lines(z, {"nope"}), [])

    def test_6b_debt_and_dv01_joins(self):
        debts = [dict(HOLDING_ID="1", MATURITY_DATE="15-MAY-2030", COUPON_TYPE="Fixed", ANNUALIZED_RATE="0.02125")]
        irrs = [dict(ACCESSION_NUMBER="L1", INTEREST_RATE_RISK_ID="1", CURRENCY_CODE="USD", INTRST_RATE_CHANGE_3MON_DV01="1", INTRST_RATE_CHANGE_1YR_DV01="2",
                     INTRST_RATE_CHANGE_5YR_DV01="3", INTRST_RATE_CHANGE_10YR_DV01="4", INTRST_RATE_CHANGE_30YR_DV01="5"),
                dict(ACCESSION_NUMBER="L1", INTEREST_RATE_RISK_ID="2", CURRENCY_CODE="EUR", INTRST_RATE_CHANGE_3MON_DV01="100")]
        z, _ = self.filings_from("2024q1_nport.zip", 0, [("L1", "NPORT-P", "10-FEB-2024", "31-DEC-2023", "S1", "100")],
                                 [hold("L1", "1", "912828AA8")], debts, irrs)
        d = ntd.read_debt(z, {"1", "2"})
        self.assertEqual(d["1"], (D(2030, 5, 15), "Fixed", "0.02125"))
        self.assertEqual(ntd.read_dv01(z, {"L1"}), {"L1": 15.0}, "the five USD key-rate DV01s, the EUR row ignored")

    def test_7_pricing_matches_r2_and_par_bond_factor_is_one(self):
        r2 = ntd.load_by_path("r2_for_test", os.path.join(HERE, "r2_duration_supply.py"))
        nom, real = flat_r2_setup(r2)
        fixed = ntd.r2_fixed_curve(r2, nom, real, "2023-12-31")
        self.assertEqual(fixed[3], D(2023, 12, 29))
        pr = ntd.Pricer(r2, nom, real, fixed, fixed)
        rd, mat = D(2023, 12, 29), D(2033, 6, 30)
        T, fx, _, own, d10o = pr.price("coupons", 3.5, mat, rd)
        want = r2.price_one("coupons", 3.5, (mat - rd).days / 365.25, fixed[0], fixed[1])
        self.assertAlmostEqual(T, (mat - rd).days / 365.25, places=12)
        self.assertEqual(fx, want, "the script's price is r2.price_one called directly")
        self.assertEqual(own, want)
        self.assertAlmostEqual(ntd.par_bond_factor(r2, fixed, 10), 1.0, places=9)
        # a strip is a semiannual zero: modified duration T / (1 + y/2)
        price, dur = pr._pd("strips", 0.0, 5.0, fixed[0], fixed[1])
        self.assertAlmostEqual(dur, 5.0 / (1 + 0.04 / 2), places=9)
        self.assertAlmostEqual(price, 100.0 * (1 + 0.04 / 2) ** -10, places=9)

    def test_8_coupon_normalisation_and_kind_rules(self):
        self.assertEqual(ntd.decide_coupon("912828ZZ9", {}, "0.02125"), (2.125, "rate_x100"))
        self.assertEqual(ntd.decide_coupon("912828ZZ9", {}, "2.125"), (2.125, "rate"))
        self.assertEqual(ntd.decide_coupon("912828ZZ9", {}, ""), (None, "none"))
        m = {"912828AA8": ntd.Mspd("coupons", D(2030, 5, 15), 1.75)}
        self.assertEqual(ntd.decide_coupon("912828AA8", m, "0.5"), (1.75, "mspd"))
        self.assertEqual(ntd.decide_kind("912828AA8", "", "", "", m), ("coupons", 1))
        self.assertEqual(ntd.decide_kind("912796XX1", "", "", "", {}), ("bills", 2))
        self.assertEqual(ntd.decide_kind("912803AB1", "", "", "", {}), ("strips", 3))
        self.assertEqual(ntd.decide_kind("912828QQ1", "US TREAS STRIPS", "", "", {}), ("strips", 3))
        self.assertEqual(ntd.decide_kind("912828QQ1", "", "", "Floating", {}), ("frn", 4))
        self.assertEqual(ntd.decide_kind("912828QQ1", "TIPS 0.125", "", "Fixed", {}), ("tips", 5))
        self.assertEqual(ntd.decide_kind("912828QQ1", "T NOTE", "", "Fixed", {}), ("coupons", 6))

    def test_9_tips_index_ratio_and_original_face_rule(self):
        rows = [dict(security_class1_desc="Inflation-Protected Securities", security_class2_desc="912828X", issued_amt="1000", inflation_adj_amt="250", redeemed_amt="0"),
                dict(security_class1_desc="Inflation-Protected Securities", security_class2_desc="912828X", issued_amt="500", inflation_adj_amt="100", redeemed_amt="*"),
                dict(security_class1_desc="Inflation-Protected Securities", security_class2_desc="Total Treasury Inflation-Protected", issued_amt="9", inflation_adj_amt="9", redeemed_amt="0")]
        r2 = ntd.load_by_path("r2_for_test2", os.path.join(HERE, "r2_duration_supply.py"))
        self.assertAlmostEqual(ntd.tips_ratios_from_rows(rows, r2.num)["912828X"], (1500 + 350) / 1500, places=12)
        self.assertEqual(list(ntd.tips_ratios_from_rows(rows, r2.num)), ["912828X"])
        # BALANCE 1000, model price 95: adjusted reading is worth 950, original-face reading (ratio 1.30) 1,235
        self.assertTrue(ntd.tips_original_face(1230.0, 1000.0, 1.30, 95.0))
        self.assertFalse(ntd.tips_original_face(955.0, 1000.0, 1.30, 95.0))
        self.assertFalse(ntd.tips_original_face(1052.0, 1000.0, 1.02, 95.0), "below the 1.05 threshold the readings cannot be told apart")
        self.assertFalse(ntd.tips_original_face(1230.0, 1000.0, None, 95.0))
        series = [(D(2024, 1, 1), 1.0), (D(2024, 1, 11), 1.1)]
        self.assertAlmostEqual(ntd.tips_ratio_at(series, D(2024, 1, 6)), 1.05)
        self.assertEqual(ntd.tips_ratio_at(series, D(2023, 1, 1)), 1.0)
        self.assertEqual(ntd.tips_ratio_at(series, D(2025, 1, 1)), 1.1)
        self.assertIsNone(ntd.tips_ratio_at(None, D(2025, 1, 1)))

    def test_10_buckets_sum_to_total_and_dv01_ratio_uses_magnitudes(self):
        r2 = ntd.load_by_path("r2_for_test3", os.path.join(HERE, "r2_duration_supply.py"))
        nom, real = flat_r2_setup(r2)
        fixed = ntd.r2_fixed_curve(r2, nom, real, "2023-12-31")
        w = ntd.Window(0, 2024, 1)
        _, fl = self.filings_from("2024q1_nport.zip", 0, [("Q1", "NPORT-P", "10-FEB-2024", "29-DEC-2023", "S1", "100")])
        f = fl[0]
        ctx = ntd.Ctx(r2, ntd.Pricer(r2, nom, real, fixed, fixed), {}, {}, [w], {"Q1": f})
        rd = D(2023, 12, 29)
        for i, (kind, mat, par) in enumerate([("bills", D(2024, 3, 1), 1e9), ("coupons", D(2026, 5, 15), 2e9), ("coupons", D(2033, 8, 15), 3e9),
                                              ("coupons", D(2053, 2, 15), 4e9), ("frn", D(2025, 1, 31), 5e8)]):
            L = ntd.Line("Q1", str(i), f"91282{i}", par, par * 0.98, "", "", False)
            ctx.add("T", L, f, 0, 1, kind, 1, 3.0, mat)
        ctx.add("T", ntd.Line("Q1", "99", "912829", 1e9, 9.7e8, "", "", False), f, 0, 1, "unpriced", 6, 3.0, None)
        ag = ctx.agg[("base", 0)]
        self.assertEqual(ag.lines, 6)
        self.assertEqual(ag.unpriced_lines, 1)
        self.assertAlmostEqual(sum(b[1].value() for b in ag.buckets.values()), ag.val("value"), places=12)
        self.assertAlmostEqual(sum(b[2].value() for b in ag.buckets.values()), ag.val("par"), places=12)
        self.assertAlmostEqual(sum(b[3].value() for b in ag.buckets.values()), ag.val("tenyeq_fixed"), places=12)
        self.assertEqual(ctx.agg[("matched", 0)].lines, 0, "mask 1 is the base vintage only")
        self.assertEqual(ntd.dv01_ratio(-1000.0, 900.0), ntd.dv01_ratio(1000.0, 900.0))
        self.assertEqual(ntd.dv01_ratio(-1000.0, -900.0), ntd.dv01_ratio(1000.0, 900.0))
        self.assertEqual(ntd.bucket_of(0.5), "0-1")
        self.assertEqual(ntd.bucket_of(10.0), "10-20")
        self.assertEqual(ntd.bucket_of(25.0), "20+")

    def test_10b_tips_original_face_line_has_par_tenyeq_and_counts_scaled_by_the_index_ratio(self):
        # (N4) Ctx.add: a TIPS line detected as original face has its par scaled by the MSPD index ratio, so its 10-year
        # equivalent follows, and the tips_orig_* figures and counters record what was added; an adjusted-face line is untouched
        r2 = ntd.load_by_path("r2_for_test4", os.path.join(HERE, "r2_duration_supply.py"))
        nom, real = flat_r2_setup(r2)
        fixed = ntd.r2_fixed_curve(r2, nom, real, "2023-12-31")
        w = ntd.Window(0, 2024, 1)
        _, fl = self.filings_from("2024q1_nport.zip", 0, [("Q1", "NPORT-P", "10-FEB-2024", "29-DEC-2023", "S1", "100")])
        f = fl[0]
        pricer = ntd.Pricer(r2, nom, real, fixed, fixed)
        mat, coupon, ratio, par = D(2033, 7, 15), 0.125, 1.30, 1e9
        ratios = {"91282TP01": [(D(2023, 12, 1), ratio), (D(2024, 1, 1), ratio)]}
        _, (price_f, dur_f), _, (price_own, _), _ = pricer.price("tips", coupon, mat, f.rdate)

        def run(value):
            ctx = ntd.Ctx(r2, pricer, {}, ratios, [w], {"Q1": f})
            ctx.add("T", ntd.Line("Q1", "1", "91282TP01", par, value, "", "", False), f, 0, 1, "tips", 1, coupon, mat)
            return ctx, ctx.agg[("base", 0)]

        # BALANCE is the original face: the value is par x ratio x model price
        value = par * ratio * price_own / 100.0
        self.assertTrue(ntd.tips_original_face(value, par, ratio, price_own))
        ctx, ag = run(value)
        added = par * (ratio - 1.0) / 1e9                                      # 0.30bn of par
        per_par = price_f / 100.0 * dur_f / ctx.d10f                           # 10-year equivalent per $1 of par
        self.assertAlmostEqual(ag.val("par"), par * ratio / 1e9, places=9)     # 1.30bn, not 1.00bn
        self.assertAlmostEqual(ag.val("tenyeq_fixed"), par * ratio / 1e9 * per_par, places=9)
        self.assertAlmostEqual(sum(b[2].value() for b in ag.buckets.values()), par * ratio / 1e9, places=9)
        self.assertAlmostEqual(sum(b[3].value() for b in ag.buckets.values()), ag.val("tenyeq_fixed"), places=12)
        self.assertAlmostEqual(ctx.fund_agg[(0, f.fund)].tenyeq.value(), ag.val("tenyeq_fixed"), places=12)
        self.assertEqual(ag.tips_orig_lines, 1)
        self.assertAlmostEqual(ag.val("tips_orig_par_added"), added, places=9)
        self.assertAlmostEqual(ag.val("tips_orig_tenyeq_fixed"), added * per_par, places=9)
        self.assertEqual(ctx.zstats["T"]["tips_original_face_lines"], 1)
        self.assertAlmostEqual(ctx.zfl["T"]["tips_original_face_par_added_bn"], added, places=9)
        self.assertAlmostEqual(ag.val("value"), value / 1e9, places=12, msg="the $ value is the filed value, never scaled")
        # BALANCE is the adjusted face: the value is par x model price, and nothing is added
        value = par * price_own / 100.0
        self.assertFalse(ntd.tips_original_face(value, par, ratio, price_own))
        ctx, ag = run(value)
        self.assertAlmostEqual(ag.val("par"), par / 1e9, places=12)
        self.assertAlmostEqual(ag.val("tenyeq_fixed"), par / 1e9 * per_par, places=9)
        self.assertEqual((ag.tips_orig_lines, ag.val("tips_orig_par_added"), ag.val("tips_orig_tenyeq_fixed")), (0, 0.0, 0.0))
        self.assertEqual(ctx.zstats["T"]["tips_original_face_lines"], 0)


class TestInfrastructure(Base):
    def test_11_no_network_guard(self):
        guard = ntd.make_fetch_guard()
        present = os.path.join(self.dir, "mspd_table3_2026-06-30_p1.json")
        with open(present, "w") as fh:
            fh.write("{}")
        self.assertIsNone(guard("https://example.invalid/x", present), "a cached file is returned without any fetch")
        missing = os.path.join(self.dir, "soma_tsy_2026-06-24.json")
        with self.assertRaises(SystemExit) as cm:
            guard("https://example.invalid/x", missing)
        self.assertIn("soma_tsy_2026-06-24.json", str(cm.exception))
        self.assertIn("bin/r2_duration_supply.py", str(cm.exception))

    def test_12_cache_list_is_explicit_and_missing_files_are_named(self):
        names = [n for _, n, _ in ntd.expected_cache_files()]
        self.assertEqual(len(names), 8 + 6 + 5)
        self.assertEqual(len(set(names)), len(names))
        with self.assertRaises(SystemExit) as cm:
            ntd.check_caches(self.dir, self.dir)
        self.assertIn("mspd_table3_2023-12-31_p1.json", str(cm.exception))
        self.assertIn("python3 bin/r2_duration_supply.py", str(cm.exception))

    def test_13_verdict_rule(self):
        f, b = ntd.FIRST_ORDER_BN, ntd.BYSTANDER_BN
        self.assertEqual((f, b), (460.0, 100.0))
        self.assertEqual(ntd.verdict_label(459.0, f, b), "PARTICIPANT")
        self.assertEqual(ntd.verdict_label(460.0, f, b), "FIRST-ORDER SINK")
        self.assertEqual(ntd.verdict_label(99.0, f, b), "BYSTANDER")
        self.assertEqual(ntd.verdict_label(100.0, f, b), "PARTICIPANT")
        self.assertEqual(ntd.verdict_label((99.0, 461.0), f, b), "PARTICIPANT", "a band that straddles a line is a participant")
        self.assertEqual(ntd.verdict_label((470.0, 480.0), f, b), "FIRST-ORDER SINK")
        self.assertEqual(ntd.verdict_label((10.0, 99.0), f, b), "BYSTANDER")
        self.assertEqual(ntd.combine_verdicts("PARTICIPANT", "BYSTANDER"), "NOT ESTABLISHED")
        self.assertEqual(ntd.combine_verdicts("PARTICIPANT", "PARTICIPANT"), "PARTICIPANT")

    def test_14_zips_are_discovered_by_glob_and_gaps_refused(self):
        for n in ("2024q1_nport.zip", "2024q2_nport.zip", "2024q3_nport.zip", "notes.txt"):
            with open(os.path.join(self.dir, n), "w"):
                pass
        zips = ntd.discover_zips(self.dir)
        self.assertEqual([(y, q) for y, q, _ in zips], [(2024, 1), (2024, 2), (2024, 3)])
        self.assertEqual([w.label for w in ntd.make_windows(zips)], ["2023Q4", "2024Q1", "2024Q2"])
        os.remove(os.path.join(self.dir, "2024q2_nport.zip"))
        with self.assertRaises(SystemExit):
            ntd.discover_zips(self.dir)
        with tempfile.TemporaryDirectory() as empty:
            with self.assertRaises(SystemExit):
                ntd.discover_zips(empty)

    def test_15_exact_sums_and_hygiene(self):
        s = ntd.Fsum()
        for x in (1e16, 1.0, -1e16, 1.0):
            s.add(x)
        self.assertEqual(s.value(), 2.0, "a naive sum of these terms gives 0.0 or 1.0")
        files = {"a": (["rank_by", "value"], [{}]), "b": (["fund_key", "HOLDING_ID"], [{}])}
        c = ntd.hygiene_check(files)
        self.assertEqual(c["result"], "FAIL")
        files = {"a": (["rank_by", "value"], [{}] * 2000)}
        self.assertEqual(ntd.hygiene_check(files)["result"], "PASS")
        files = {"a": (["rank_by", "value"], [{}] * 2001)}
        self.assertEqual(ntd.hygiene_check(files)["result"], "FAIL")


if __name__ == "__main__":
    unittest.main(verbosity=2)
