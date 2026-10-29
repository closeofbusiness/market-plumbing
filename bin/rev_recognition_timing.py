#!/usr/bin/env python3
"""Revenue-recognition timing in the net-income growth of the W3 firm set, fiscal 2023 to fiscal 2025 (SEC XBRL on data.sec.gov). Python 3 standard library only.

  python3 bin/rev_recognition_timing.py fetch-submissions --vintage YYYYMMDD [--max-requests N] [--cache DIR] [--out DIR]   # network; SEC_UA required; supervisor only
  python3 bin/rev_recognition_timing.py fetch-companyfacts --vintage YYYYMMDD [--max-requests N] [--cache DIR] [--out DIR]  # network; needs the submissions extract first
  python3 bin/rev_recognition_timing.py fetch-frames --vintage YYYYMMDD [--max-requests N] [--cache DIR] [--out DIR]        # network; coverage and checks only
  python3 bin/rev_recognition_timing.py build --vintage YYYYMMDD --stage pre|full [--cache DIR] [--out DIR] [--panel PATH]  # offline; byte-identical on re-run
  python3 bin/rev_recognition_timing.py selftest [--no-mutants] [--mutant NAME]                                            # synthetic data only; no network

Specification: _research/2026-10-28-Revenue-Recognition-Timing-Spec.md (committed at 2cd528f, with the supervisor's rulings of rounds 1 and 2; the latest round wins).
Outputs: data/rev_recognition_timing/ (fifteen CSVs, README.md, SOURCES.md) and, per vintage, data/vintages/rev_recognition_timing/<YYYYMMDD>/ (three extract CSVs; the raw JSON
bodies sit in its raw/ folder, which git ignores).

WHAT TOUCHES THE NETWORK. Only the three fetch modes, only data.sec.gov, GET only, at least 1.0 s after the previous reply, no redirect followed, no retry of any kind, timeout 300 s,
at most 1,000 (submissions), 600 (companyfacts) or 250 (frames) requests a run. The contact string is read from the SEC_UA environment variable, a fetch refuses to run without it
(exit 2), and its value is never written to any file, log or output. A 404 on a frame is `absent`; a 404 on a submissions or companyfacts file marks the firm no_sec_record. Any 403 or
429, any other status, and a 200 body that is empty, a web page, not JSON or not the document asked for writes STOP_rrt in data/vintages/rev_recognition_timing/ and ends with exit 2.
A timeout ends with exit 3 and latches nothing. With the latch present no request is made. This script never deletes, renames over or truncates a STOP file; only a person deletes one.
Each fetch is resumable: a body already in raw/ whose sha256 matches its vintages.csv row is not requested again.

WHAT IT RECORDS. Contract assets, contract liabilities, revenue and net income as the firms first reported them in their own 10-Ks (XBRL company facts), and from them the excess accrual
and the timing contribution T of the tagged contract balances to the change in net income. It records no price and no flow of money, and it passes no judgement on any firm.
"""
import argparse
import ast
import collections
import contextlib
import csv
import datetime as dt
import decimal
import hashlib
import http.client
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from decimal import Decimal
from urllib.parse import urlsplit

decimal.getcontext().prec = 28

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------------------------------------------------------------------------
# mutants: deliberately broken variants, switched on only by the selftest, in this process
# ------------------------------------------------------------------------------------------------------------------------
_ACTIVE = set()


def M(name):
    return name in _ACTIVE


@contextlib.contextmanager
def mutant(name):
    added = name not in _ACTIVE
    _ACTIVE.add(name)
    try:
        yield
    finally:
        if added:
            _ACTIVE.discard(name)


class Refused(Exception):
    """A request, path, argument or setting this script will not honour (exit 5)."""


class Latched(Exception):
    """A technical refusal: STOP was written (or already exists); the fetch ends (exit 2)."""


class SocketFault(Exception):
    """Timeout, reset or TLS error: the invocation ends with exit 3, without latching."""


class NoContact(Exception):
    """SEC_UA is not set: a fetch refuses to run (exit 2)."""


class DataError(Exception):
    """A hard problem with the data or with an output (exit 2)."""


# ------------------------------------------------------------------------------------------------------------------------
# constants
# ------------------------------------------------------------------------------------------------------------------------
OUT_DEFAULT = os.path.join(ROOT, "data", "rev_recognition_timing")
CACHE_DEFAULT = os.path.join(ROOT, "data", "vintages", "rev_recognition_timing")
STOP_DIR = CACHE_DEFAULT                      # fixed, whatever --cache says: a latch cannot be dodged by pointing the cache elsewhere
STOP_NAME = "STOP_rrt"

HOST = "data.sec.gov"
BLOCKED_HOSTS = ("sec.gov", "www.sec.gov", "efts.sec.gov", "fred.stlouisfed.org", "alfred.stlouisfed.org", "api.stlouisfed.org")
MIN_GAP = 1.0                                 # seconds between the end of one reply and the next request (R3; G15 treats 0.9 as a violation)
TIMEOUT = 300
BODY_CAP = 256 * 1024 * 1024
ERR_CAP = 4096
CAPS = collections.OrderedDict([("submissions", 1000), ("companyfacts", 600), ("frames", 250)])    # per run (R1-18)

SUB_RX = re.compile(r"^/submissions/CIK(\d{10})\.json$")
SUBPAGE_RX = re.compile(r"^/submissions/CIK(\d{10})-submissions-(\d{3})\.json$")
CF_RX = re.compile(r"^/api/xbrl/companyfacts/CIK(\d{10})\.json$")
FRAME_RX = re.compile(r"^/api/xbrl/frames/us-gaap/([A-Za-z0-9]+)/USD/(CY(\d{4})(?:Q[1-4]I?)?)\.json$")
VINTAGE_RX = re.compile(r"^\d{8}$")

PANEL_REL = "data/w3_tax/firm_tax_panel.csv"
PANEL_PIN = {"sha256": "7b65abda3aed6b0acf7cf2614a14ae1d74a7aa8991880716f69aa5b25e11966b", "bytes": 343641, "rows": 503, "ciks": 500,
             "shared": collections.OrderedDict([("0001652044", ("GOOGL", "GOOG")), ("0001754301", ("FOXA", "FOX")), ("0001564708", ("NWSA", "NWS"))])}
MEGA = ("0001652044", "0001018724", "0001326801", "0000789019", "0001341439", "0001045810", "0000320193", "0001730168", "0001318605")   # 2.1: E2's six + Apple, Broadcom, Tesla

# the numbers of 4.6 and 4.7. The canonical texts are rebuilt from these, so editing one changes a hash and the build refuses (G10).
TH_LO = Decimal("10")
TH_HI = Decimal("25")
VOID_FRAC = Decimal("0.02")
THIN_PCT = Decimal("70")
S2_DATE = "2027-05-01"                        # no CY2026 frame, no fact after D_2025 and no S2 score before this date (R1-9, R1-10)
THIN_DATE = "2027-08-01"
S2_LO, S2_HI = "2026-11-30", "2027-02-15"     # D_2026 of an S2-eligible firm
FYE_A, FYE_B, FYE_C, FYE_D = "1130", "1231", "0101", "0215"
FY_START, FY_END = "04-01", "03-31"           # D_Y: a 10-K with reportDate in [Y-04-01, (Y+1)-03-31]
DUR_MIN, DUR_MAX = 350, 380
NEAR_DAYS = 7
REV_FLOOR = Decimal(100000000)
SIC_LO, SIC_HI = 6000, 6799
N_CIK = 500
DAYS_YEAR = Decimal(365)

# ------------------------------------------------------------------------------------------------------------------------
# the specification's canonical texts. 4.6 and 4.7 are rebuilt from the constants above; 5 is pasted. The three hashes are checked at run time (C11).
# ------------------------------------------------------------------------------------------------------------------------
PREREG_LINES = (
    'S1|window=FY2023..FY2025|sample=primary|vintage=first_full_build|N=CA-CL|r_t=N_t/Rev_t|AA_t=N_t-r_(t-1)*Rev_t|T_i=AA_i,2025-AA_i,2023|T=sum_i(T_i)|dNI=sum_i(NI_i,2025-NI_i,2023)|order=VOID,labels|VOID=sum_i(NI_i,2023)<=0_or_dNI<{void}*sum_i(NI_i,2023)|share=T/dNI|test=abs(share)|SHARE_BELOW_10=abs(share)<{lo}%|SHARE_10_TO_25={lo}%<=abs(share)<={hi}%|SHARE_ABOVE_25=abs(share)>{hi}%|direction=with_growth_if_T>0;against_growth_if_T<0;zero_if_T=0|qualifier=within_pre_window_range_if_abs(T)/sum_i(Rev_i,2025)<=NB2_else_outside_pre_window_range|compare=unrounded_decimal_prec28',
    'S1P|window=FY2023..FY2025|sample=primary|vintage=first_full_build|T_i=as_S1|dNI=as_S1|order=VOID,labels|VOID=as_S1|share_pos=sum_i(max(T_i,0))/dNI|test=share_pos|SHARE_BELOW_10=share_pos<{lo}%|SHARE_10_TO_25={lo}%<=share_pos<={hi}%|SHARE_ABOVE_25=share_pos>{hi}%|direction=as_S1|qualifier=as_S1|compare=unrounded_decimal_prec28',
    'S2|window=FY2025..FY2026|sample=s2_eligible|vintage=first_full_build_on_or_after_{s2date}|N=CA-CL|r_t=N_t/Rev_t|AA_t=N_t-r_(t-1)*Rev_t|T_i=AA_i,2026-AA_i,2025|T=sum_i(T_i)|dNI=sum_i(NI_i,2026-NI_i,2025)|order=PENDING,PENDING_THIN,VOID_thin,VOID,labels|PENDING=no_full_build_on_or_after_{s2date}|PENDING_THIN=fewer_than_{thin}%_of_firms_S2_eligible_and_in_scope_at_FY2025_have_a_FY2026_10-K|VOID_thin=still_PENDING_THIN_on_or_after_{thindate}|VOID=sum_i(NI_i,2025)<=0_or_dNI<{void}*sum_i(NI_i,2025)|share=T/dNI|test=abs(share)|labels=as_S1|direction=as_S1|qualifier=within_pre_window_range_if_abs(T)/sum_i(Rev_i,2026)<=NB1_frozen_else_outside_pre_window_range|late_filers=counted|reported_beside=s2_subset|compare=unrounded_decimal_prec28',
    'S2P|window=FY2025..FY2026|sample=s2_eligible|vintage=as_S2|T_i=as_S2|dNI=as_S2|order=as_S2|PENDING=as_S2|PENDING_THIN=as_S2|VOID_thin=as_S2|VOID=as_S2|share_pos=sum_i(max(T_i,0))/dNI|test=share_pos|labels=as_S1P|direction=as_S2|qualifier=as_S2|compare=unrounded_decimal_prec28',
    "NB|statistic=T_as_S1_on_each_window|windows=FY2020..FY2022(two-year,inputs_FY2019..FY2022);FY2020..FY2021(one-year,inputs_FY2019..FY2021);FY2021..FY2022(one-year,inputs_FY2020..FY2022)|firm_set=in_scope_on_the_window's_own_years_by_the_population_block|includes_fy2020=yes_if_FY2020_is_an_endpoint|NB1=max_abs(T)/sum_i(Rev_i,e)_over_one-year_windows_without_FY2020_as_an_endpoint|NB2=abs(T)/sum_i(Rev_i,e)_of_the_two-year_window|medians=reported_beside_the_maxima|frozen=first_full_vintage|S2_uses=frozen_NB1",
)
POP_LINES = (
    'P1|panel=data/w3_tax/firm_tax_panel.csv|sha256={panel_sha}|unit=distinct_cik10|n={n_cik}',
    'P2|exclude=sic_{sic_lo}..{sic_hi}_inclusive|sic_from=data.sec.gov_submissions|missing_sic=excluded',
    'P3|D_Y=reportDate_of_the_original_form_10-K_with_reportDate_in_[Y-{fy_start},(Y+1)-{fy_end}]|none=year_gap|two_or_more=fy_ambiguous|10-K/A_or_10-KT=never_defines_D_Y',
    'P4|source=companyfacts_for_every_firm|primary_basis=own_10k:the_fact_whose_accn_is_the_year_Y_original_10-K_accession|sens_latest=latest_filed,ties_to_largest_accn|unit=USD|select_by=end_and_start,never_fy_or_fp',
    'P5|instant=end==D_Y|duration=end==D_Y_and_{dur_min}<=days(end-start)<={dur_max}|no_exact_but_abs(end-D_Y)<={near}_days=end_mismatch',
    'P6|CA=ContractWithCustomerAssetNet_if_total>=Current(+Noncurrent_where_tagged)_at_every_needed_year;else_parts=ContractWithCustomerAssetNetCurrent+ContractWithCustomerAssetNetNoncurrent|flag=total_gt_parts|sensitivity=sens_parts',
    'P7|CL=ContractWithCustomerLiability_if_total>=Current(+Noncurrent_where_tagged)_at_every_needed_year;else_parts=ContractWithCustomerLiabilityCurrent+ContractWithCustomerLiabilityNoncurrent|fallback=DeferredRevenueCurrent+DeferredRevenueNoncurrent_only_if_no_ContractWithCustomerLiability*_tag_at_any_needed_year|never_a_total_with_its_parts',
    'P8|N=CA-CL|receivables_not_in_N|no_contract_balance_tag_at_any_needed_year=N_is_0_every_year_and_in_scope|a_tag_at_some_needed_years_only=year_gap(gap_n);sens_gap0_sets_the_missing_side_to_0',
    'P9|Rev=R2:RevenueFromContractWithCustomerExcludingAssessedTax;then_R3:RevenueFromContractWithCustomerIncludingAssessedTax;then_Revenues_only_if_neither_R2_nor_R3_at_every_needed_year(flag_rev_fallback)|one_tag_per_window|sens_r2only=drop_rev_fallback',
    'P10|NI=NetIncomeLoss|no_fallback',
    "P11|needed_years=S1:FY2022..FY2025;S2:FY2024..FY2026;placebo:each_window's_inputs|year_gap=N_or_Rev_or_NI_or_D_Y_missing_at_a_needed_year|floor=Rev>={floor}_USD_at_every_needed_year_else_tiny_revenue",
    'P12|status_order=no_sec_record,financial_sic,no_sic,fy_ambiguous,end_mismatch,year_gap,tiny_revenue,in_scope',
    'P13|S2_eligible=in_scope_for_S2_and_D_2026_in_[{s2_lo},{s2_hi}]|S2_eligible_at_FY2025=fiscalYearEnd_MMDD_in_[{fye_a},{fye_b}]or[{fye_c},{fye_d}]_and_in_scope_on_FY2024..FY2025',
)
SPEC_PREREG_SHA256 = "6d113eb3905efff2447989c1de31475b7398e1d44def1cdec43cdd7eb80fc43e"
SPEC_POP_SHA256 = "6a68f3d883929120d55f490bb799280a81e661c13773acdc8251905167d7c769"
SPEC_ALLOW_TEXT = (
    'firms.csv:cik10,tickers,entity_name,sic,fye_mmdd,status,flags\n'
    'firm_years.csv:cik10,fiscal_year,period_end,accession,filing_date\n'
    'firm_tags.csv:window,cik10,component,structure,tags\n'
    'panel.csv:window,basis,cik10,fiscal_year,period_end,revenue_tag,revenue_usd,ni_usd,ca_usd,cl_usd,n_usd,r,ar_usd,contract_cost_usd\n'
    'contributions.csv:window,sample,cik10,ticker,aa_base_usd,aa_end_usd,t_usd,dni_usd,rev_end_usd,flags\n'
    'headline.csv:vintage,window,sample,statistic,value,unit,n_firms\n'
    'registered.csv:statement_id,window,sample,vintage,n_firms,numerator_usd,t_usd,dni_usd,ni_base_usd,share_pct,t_pct_rev,t_days_rev,noise_band_pct_rev,qualifier,direction,label,void_reason,prereg_sha256,population_sha256\n'
    'contributors.csv:window,side,rank,cik10,ticker,entity_name,t_usd,share_of_side_pct,flags\n'
    'placebo.csv:window,years,includes_fy2020,n_firms,t_usd,t_pos_usd,rev_end_usd,t_pct_rev,dni_usd,share_pct\n'
    'receivables.csv:window,row_type,fiscal_year,measure,n_firms,ar_usd,rev_usd,ar_days,t_ar_usd,t_ar_days_rev\n'
    'coverage.csv:tag,period,role,n_cik_all500,n_cik_in_scope\n'
    'checks.csv:check_id,description,expected,observed,status\n'
    'vintages.csv:vintage,url_path,status,bytes,sha256,retrieved_utc\n'
    'fetch_log.csv:utc_time,vintage,host,path,status,bytes,sha256,elapsed_s\n'
    'revisions.csv:vintage_prev,vintage_new,window,sample,statistic,value_prev,value_new\n'
    'frames_extract.csv:vintage,tag,period,cik10,accn,start,end,val\n'
    'cf_extract.csv:vintage,cik10,tag,start,end,val,accn,form,fp,fy,filed\n'
    'submissions_extract.csv:vintage,cik10,sic,fye_mmdd,form,report_date,filing_date,accession\n'
)
SPEC_ALLOW_SHA256 = "99e8e8f929139485e37cec69c3e1afd6623d33a40d8cbc854ad0c05e75e55376"
ALLOW_ORDER = tuple(l.split(":", 1)[0] for l in SPEC_ALLOW_TEXT.splitlines())
ALLOW = {l.split(":", 1)[0]: l.split(":", 1)[1].split(",") for l in SPEC_ALLOW_TEXT.splitlines()}
OUT_CSVS = ALLOW_ORDER[:15]
EXTRACT_CSVS = ALLOW_ORDER[15:]
COMMITTED = tuple(OUT_CSVS) + ("README.md", "SOURCES.md")
KEYS = {
    "firms.csv": ("cik10",),
    "firm_years.csv": ("cik10", "fiscal_year"),
    "firm_tags.csv": ("window", "cik10", "component"),
    "panel.csv": ("window", "basis", "cik10", "fiscal_year"),
    "contributions.csv": ("window", "sample", "cik10"),
    "headline.csv": ("vintage", "window", "sample", "statistic"),
    "registered.csv": ("statement_id", "vintage"),
    "contributors.csv": ("window", "side", "rank"),
    "placebo.csv": ("window",),
    "receivables.csv": ("window", "row_type", "fiscal_year"),
}

# G13's literal patterns (pasted from section 7, not imported), both compiled with re.I
CAUSAL_RX = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b", re.I)
EXTRA_RX = re.compile(r"\b(?:in|out)flows?\b|\bflow(?:s|ed|ing)?\s+(?:into|out\s+of|from|to)\b|\bmanipulat\w*|\bmanag(?:e|ed|es|ing)\s+(?:earnings|results|revenue)\b|\bearnings\s+management\b|\baggressive\w*|\bfraud\w*|\bmisstat\w*|\binflat(?:e|ed|es|ing)\b|\bboost(?:s|ed|ing)?\b|\bpadd(?:ed|ing)\b|\bchannel[- ]stuff\w*|\blow[- ]quality\b|\bfake\b|\billusory\b|\bnot\s+real\b|\b(?:prices?|valuations?|multiples?|stocks?|shares)\s+(?:rose|fell|rallied|moved|jumped|dropped)\b|\bmaterial\w*|\boverstat\w*|\bpulled\s+forward\b|\bflatter\w*|\bprematur\w*|\bwindow[- ]dressing\b|\bred\s+flags?\b|\bfictitious\b|\bsmooth(?:ed|ing)\b|\babnormal\w*", re.I)
DENIAL_SENTENCE = ("A change in contract assets or contract liabilities relative to revenue is a balance-sheet accrual: it shows when revenue was booked against billing, not why, "
                   "and nothing here says it moved any price or any flow of money.")
CEILING_PHRASE = "the share is a ceiling on size for the tagged balances, not an estimate of the effect"
CONTRIBUTOR_SENTENCE = "A large contributor is not a finding about that firm."
VERDICT_RX = re.compile(r"HELD|FALSIFIED|PROVEN|CAUSED|REFUTED|MATERIAL")          # 5 and criterion 4: no output carries a verdict word (NOT_HELD and NOT_MATERIAL contain two of them)

ALLOWED_VALUES = {
    "status_firm": {"in_scope", "no_sec_record", "financial_sic", "no_sic", "fy_ambiguous", "end_mismatch", "year_gap", "tiny_revenue"},
    "flags": {"acq2", "disc_ops", "rev_fallback", "total_gt_parts", "extreme_r", "near_end", "gap_10k", "gap_n", "gap_rev", "gap_ni", "gap0_imputed", "unbilled_added"},
    "component": {"ca", "cl", "rev", "ni", "ar", "contract_cost"},
    "structure": {"single", "total", "parts", "deferred_revenue", "absent_everywhere", "gap"},
    "basis": {"own_10k", "latest_filed"},
    "window": {"fy2023_fy2025", "fy2025_fy2026", "fy2020_fy2022", "fy2020_fy2021", "fy2021_fy2022"},
    "includes_fy2020": {"yes", "no"},
    "sample": {"primary", "mega", "s2_subset", "s2_eligible", "sens_gap0", "sens_acq", "sens_disc", "sens_trim", "sens_unbilled", "sens_r2only", "sens_parts", "sens_latest", "sens_leave1", "sens_samefiling"},
    "unit": {"usd", "pct", "days", "count", "ratio", "label"},
    "side": {"positive", "negative"},
    "row_type": {"level", "window_t"},
    "measure": {"collection_not_recognition"},
    "role": {"component", "revenue", "net_income", "receivable", "contract_cost", "descriptive", "flag"},
    "statement_id": {"S1", "S1P", "S2", "S2P"},
    "label": {"SHARE_BELOW_10", "SHARE_10_TO_25", "SHARE_ABOVE_25", "VOID", "PENDING", "PENDING_THIN"},
    "void_reason": {"none", "base_not_positive", "dni_small", "thin_coverage"},
    "direction": {"with_growth", "against_growth", "zero"},
    "qualifier": {"within_pre_window_range", "outside_pre_window_range", "none"},
    "status_check": {"PASS", "WARN", "FAIL", "INFO"},
}
FLAG_ORDER = ("acq2", "disc_ops", "rev_fallback", "total_gt_parts", "extreme_r", "near_end", "gap_10k", "gap_n", "gap_rev", "gap_ni", "gap0_imputed", "unbilled_added")
STATUS_ORDER = ("no_sec_record", "financial_sic", "no_sic", "fy_ambiguous", "end_mismatch", "year_gap", "tiny_revenue", "in_scope")

# ---- the windows (section 3, R1-6): years of the base and end, and the inputs they need ----
WINDOWS = collections.OrderedDict([
    ("fy2023_fy2025", {"b": 2023, "e": 2025, "years": (2022, 2023, 2024, 2025), "includes_fy2020": "no"}),
    ("fy2025_fy2026", {"b": 2025, "e": 2026, "years": (2024, 2025, 2026), "includes_fy2020": "no"}),
    ("fy2020_fy2022", {"b": 2020, "e": 2022, "years": (2019, 2020, 2021, 2022), "includes_fy2020": "yes"}),
    ("fy2020_fy2021", {"b": 2020, "e": 2021, "years": (2019, 2020, 2021), "includes_fy2020": "yes"}),
    ("fy2021_fy2022", {"b": 2021, "e": 2022, "years": (2020, 2021, 2022), "includes_fy2020": "no"}),
])
PLACEBO_WINDOWS = ("fy2020_fy2022", "fy2020_fy2021", "fy2021_fy2022")
SAMPLES_S1 = ("primary", "mega", "s2_subset", "sens_gap0", "sens_acq", "sens_disc", "sens_trim", "sens_unbilled", "sens_r2only", "sens_parts", "sens_latest", "sens_leave1", "sens_samefiling")
PRE_LAST_YEAR = 2022
PRE_DATE_LIMIT = "2023-03-31"                 # the end of FY2022's date window: the pre stage reads no 10-K row reported after it
ALL_YEARS = tuple(range(2019, 2027))

# ---- tags (2.4) ----
CA_T, CA_C, CA_N = "ContractWithCustomerAssetNet", "ContractWithCustomerAssetNetCurrent", "ContractWithCustomerAssetNetNoncurrent"
CL_T, CL_C, CL_N = "ContractWithCustomerLiability", "ContractWithCustomerLiabilityCurrent", "ContractWithCustomerLiabilityNoncurrent"
DEF_C, DEF_N = "DeferredRevenueCurrent", "DeferredRevenueNoncurrent"
REV_R2 = "RevenueFromContractWithCustomerExcludingAssessedTax"
REV_R3 = "RevenueFromContractWithCustomerIncludingAssessedTax"
REV_ANY = "Revenues"
NI_TAG = "NetIncomeLoss"
AR_A1 = "AccountsReceivableNetCurrent"
AR_A2 = "AccountsNotesAndLoansReceivableNetCurrent"
AR_A3 = "ReceivablesNetCurrent"
CC_TAG = "CapitalizedContractCostNet"
RPO_TAG = "RevenueRemainingPerformanceObligation"
UNB_TAG = "UnbilledContractsReceivable"
CF_CA, CF_CL, CF_AR = "IncreaseDecreaseInContractWithCustomerAsset", "IncreaseDecreaseInContractWithCustomerLiability", "IncreaseDecreaseInAccountsReceivable"
ACQ_TAG = "PaymentsToAcquireBusinessesNetOfCashAcquired"
DISC_TAG = "IncomeLossFromDiscontinuedOperationsNetOfTax"
DURATION_TAGS = frozenset([REV_R2, REV_R3, REV_ANY, NI_TAG, CF_CA, CF_CL, CF_AR, ACQ_TAG, DISC_TAG])
INSTANT_TAGS = frozenset([CA_T, CA_C, CA_N, CL_T, CL_C, CL_N, DEF_C, DEF_N, AR_A1, CC_TAG, RPO_TAG, UNB_TAG])
CF_TAGS = tuple(sorted(DURATION_TAGS | INSTANT_TAGS))                       # the tags extracted from companyfacts (A2 and A3 are not trade receivables, so they are not extracted)
# the frames fetched for coverage and checks (about 70 requests): (tag, role); instants at CY2019Q4I, CY2023Q4I, CY2025Q4I and durations at CY2019, CY2023, CY2025
FRAME_INSTANTS = ((CL_T, "component"), (CL_C, "component"), (CL_N, "component"), (CA_T, "component"), (CA_C, "component"), (CA_N, "component"), (DEF_C, "component"),
                  (AR_A1, "receivable"), (AR_A2, "receivable"), (AR_A3, "receivable"), (RPO_TAG, "descriptive"), (UNB_TAG, "descriptive"), (CC_TAG, "contract_cost"))
FRAME_DURATIONS = ((REV_ANY, "revenue"), (REV_R2, "revenue"), (REV_R3, "revenue"), (NI_TAG, "net_income"), (CF_AR, "descriptive"), (CF_CL, "descriptive"), (CF_CA, "descriptive"),
                   (ACQ_TAG, "flag"), (DISC_TAG, "flag"))
FRAME_ROLE = dict(list(FRAME_INSTANTS) + list(FRAME_DURATIONS))
FRAME_YEARS = (2019, 2023, 2025)

# ------------------------------------------------------------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------------------------------------------------------------
def tilde(p):
    home = os.path.expanduser("~")
    return str(p).replace(home, "~") if home and home != "~" else str(p)


def sha256_of(b):
    return hashlib.sha256(b).hexdigest()


def fdec(v, nd):
    """Fixed-decimal text of a Decimal, '' for None, no negative zero. Rounding is half-even and happens only here, at write time (R8)."""
    if v is None:
        return ""
    q = Decimal(1).scaleb(-nd)
    s = format(Decimal(v).quantize(q, rounding=decimal.ROUND_HALF_EVEN), "f")
    if s.startswith("-") and Decimal(s) == 0:
        s = s[1:]
    return s


def q0(v):
    """A money amount in whole dollars, half-even (R8). The per-firm cells are quantized once, when the record is made, and every aggregate is the sum of the written cells."""
    if v is None:
        return None
    return Decimal(v).quantize(Decimal(1), rounding=decimal.ROUND_HALF_EVEN)


def usd(v):
    return fdec(v, 0)


def r6(v):
    return fdec(v, 6)


def pct3(v):
    return fdec(v, 3)


def days3(v):
    return fdec(v, 3)


def dsum(values):
    """Exact Decimal sum (R8). The mutant sums as binary floating point (G1)."""
    if M("g1_float_sum"):
        f = 0.0
        for v in values:
            f += float(v)
        return Decimal(repr(f))
    t = Decimal(0)
    for v in values:
        t += v
    return t


def read_file(path, mode="rb"):
    with open(path, mode) as fh:
        return fh.read()


# ---- the contact string (SEC_UA): its value is never written, logged or printed (R2, R1-17) ----
_SECRETS = []


def register_secret(value):
    if value and value not in _SECRETS:
        _SECRETS.append(value)


def forget_secrets():
    del _SECRETS[:]


def has_secret(data):
    if not _SECRETS:
        return False
    text = data if isinstance(data, str) else bytes(data).decode("latin-1")
    return any(s in text for s in _SECRETS)


def scrub(text):
    """Remove the contact string from a text that is about to be stored (a reply that echoes it)."""
    if M("g15_scrub_off"):
        return text
    for s in _SECRETS:
        text = text.replace(s, "[contact]")
    return text


def write_text(path, text):
    """Atomic write via a temporary sibling. Refuses any path whose name starts with STOP (this script never writes over a latch) and any text that holds the contact string."""
    if os.path.basename(path).upper().startswith("STOP"):
        raise Refused("write_text never touches a STOP file")
    if has_secret(text) and not M("g15_secret_ok"):
        raise Refused("the contact string would be written to a file (not printed)")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


def write_bytes(path, data):
    if os.path.basename(path).upper().startswith("STOP"):
        raise Refused("write_bytes never touches a STOP file")
    if has_secret(data) and not M("g15_secret_ok"):
        raise Refused("the contact string would be written to a file (not printed)")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.replace(tmp, path)


def write_text_if_changed(path, text):
    """Write only when the bytes differ, so a file the stage order depends on (placebo.csv, criterion 9) keeps its age on an identical re-run."""
    if os.path.isfile(path) and read_file(path, "rb") == text.encode("utf-8"):
        return False
    write_text(path, text)
    return True


def read_csv_rows(path):
    """(header, rows) of a csv with comment lines (# ...) skipped; ([], []) if absent."""
    if not os.path.exists(path):
        return [], []
    with open(path, encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh.read().splitlines(True) if not ln.startswith("#")]
    rd = list(csv.reader(io.StringIO("".join(lines))))
    return (rd[0], rd[1:]) if rd else ([], [])


# ---- dates ----
DATE_RX = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")


def parse_date(s):
    """A strict YYYY-MM-DD as a date; None for anything else (a blank or odd date is missing, never guessed)."""
    m = DATE_RX.match(s or "")
    if not m:
        return None
    try:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def iso(d):
    return d.isoformat()


def add_days(s, n):
    return iso(parse_date(s) + dt.timedelta(days=n))


def days_between(a, b):
    """b minus a, in days, for two ISO dates; None when either is not a date."""
    da, db = parse_date(a), parse_date(b)
    if da is None or db is None:
        return None
    return (db - da).days


def utc_ms(t):
    """A UTC time with milliseconds, never local time."""
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (t.microsecond // 1000)


def parse_utc_ms(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=dt.timezone.utc)


def vintage_ok(v):
    if not VINTAGE_RX.match(v or ""):
        return False
    try:
        dt.datetime.strptime(v, "%Y%m%d")
    except ValueError:
        return False
    return True


def vint_date(v):
    return "%s-%s-%s" % (v[:4], v[4:6], v[6:8])


def s2_open(vintage):
    """True from the S2 date on: only then may a FY2026 value be read or a CY2026 frame be fetched (R1-9, R1-10; G8)."""
    if M("g8_gate_off"):
        return True
    return vint_date(vintage) >= S2_DATE


def thin_void_open(vintage):
    return vint_date(vintage) >= THIN_DATE


# ---- JSON and numbers (R8, G1) ----
def parse_json(raw):
    """JSON read with parse_float and parse_int as Decimal: a value above 2^53 or a fractional value never passes through a binary float. The mutant reads every number through a binary float."""
    text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw
    if M("g1_float_parse"):
        return json.loads(text, parse_float=float, parse_int=float)
    return json.loads(text, parse_float=Decimal, parse_int=Decimal)


def to_dec(s):
    """A cell as a Decimal; a blank is missing (None), never zero (R8). The mutant reads a blank as 0."""
    if s is None or str(s).strip() == "":
        return Decimal(0) if M("g1_missing_zero") else None
    try:
        v = Decimal(str(s).strip())
    except decimal.InvalidOperation:
        raise DataError("a value cell is not a number: %r" % str(s)[:20])
    if not v.is_finite():
        raise DataError("a value cell is not finite: %r" % str(s)[:20])
    return v


def num_text(v):
    """The canonical text of a parsed number (a Decimal; never exponent notation); '' when the value is not a number."""
    if isinstance(v, bool) or v is None:
        return ""
    if isinstance(v, (int, float)) and not isinstance(v, Decimal):
        v = Decimal(repr(v))
    if not isinstance(v, Decimal) or not v.is_finite():
        return ""
    return format(v, "f")


def cik10(x):
    """A ten-digit CIK from a number or a string; None when it is not one."""
    s = num_text(x) if not isinstance(x, str) else x.strip()
    if not s.isdigit() or int(s) <= 0 or len(s) > 10:
        return None
    return "%010d" % int(s)


def title_name(s):
    """SEC registrant names are upper case; written in title case so that no output cell holds a banned verdict token by accident (VULCAN MATERIALS CO would)."""
    return " ".join(w.capitalize() for w in (s or "").split())


# ---- csv rendering with the allowlist (G12) ----
def allowlist(name):
    cols = list(ALLOW[name])
    if M("g12_allow_drift") and name == "headline.csv":
        cols[cols.index("statistic")] = "stat"
    if M("g12_extra_col") and name == "placebo.csv":
        cols.append("note")
    return cols


def allow_text():
    return "".join("%s:%s\n" % (n, ",".join(allowlist(n))) for n in ALLOW_ORDER)


def allow_hash_ok():
    return sha256_of(allow_text().encode("utf-8")) == SPEC_ALLOW_SHA256


def check_header(name, header):
    allow = allowlist(name)
    if M("g12_extra_col_ok"):
        ok = list(header[:len(allow)]) == allow
    elif M("g12_renamed_ok"):
        ok = len(header) == len(allow)
    else:
        ok = list(header) == allow
    if not ok:
        raise DataError("%s: header %r is not the exact column allowlist" % (name, list(header)))


def csv_body(text):
    """(header, rows) of a committed csv text, skipping every `# source:` line (the mutant reads the source line as the header)."""
    lines = text.splitlines()
    if not M("g12_source_as_header"):
        lines = [l for l in lines if not l.startswith("# source:")]
    rd = list(csv.reader(lines))
    return (rd[0], rd[1:]) if rd else ([], [])


def strip_exempt(text, readme=True):
    """Remove the one denial sentence (README only), once."""
    if not readme:
        return text
    if M("g13_denial_all"):
        return re.sub(r"[^.;]*\bnothing here says\b[^.]*\.", "", text)
    if M("g13_denial_loose"):
        return text.replace(DENIAL_SENTENCE, "")
    return text.replace(DENIAL_SENTENCE, "", 1)


def wording_problems(name, text):
    t = strip_exempt(text, readme=name == "README.md")
    out = []
    if not M("g13_causal_off"):
        out += ["causal wording %r" % re.sub(r"\s+", " ", m.group(0).lower()) for m in CAUSAL_RX.finditer(t)]
    if not M("g13_extra_off"):
        out += ["price, motive or misconduct wording %r" % re.sub(r"\s+", " ", m.group(0).lower()) for m in EXTRA_RX.finditer(t)]
    return out


def verdict_problems(files):
    out = []
    for n in sorted(files):
        t = files[n] if isinstance(files[n], str) else files[n].decode("utf-8", errors="replace")
        if VERDICT_RX.search(t):
            out.append("%s holds a verdict word" % n)
    return out


def guard_text(name, text):
    """What the build refuses to write: a verdict word anywhere, banned wording in the README (the one denial sentence excepted), an absolute home path."""
    probs = wording_problems(name, text) if name == "README.md" else []
    probs += ["verdict word %s" % m for m in sorted(set(VERDICT_RX.findall(text)))]
    if probs:
        raise DataError("%s: %s" % (name, "; ".join(sorted(set(probs))[:4])))
    home = os.path.expanduser("~")
    if home != "~" and home in text:
        raise DataError("%s: an absolute home path would be published" % name)


def render_csv(name, rows, source, header=None):
    header = allowlist(name) if header is None else header
    check_header(name, header)
    out = io.StringIO()
    out.write(source + "\n")
    w = csv.writer(out, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        cells = [r[h] for h in header] if isinstance(r, dict) else list(r)
        if len(cells) != len(header):
            raise DataError("%s: a row has %d cells, the header %d" % (name, len(cells), len(header)))
        w.writerow(cells)
    text = out.getvalue()
    if not text.startswith("# source:"):
        raise DataError("%s: the first line is not a `# source:` line" % name)
    guard_text(name, text)
    return text


# ---- the three canonical texts (C11, G10) ----
def prereg_text():
    """The canonical text of 4.6, rebuilt from this script's own constants. The sha256 of this text must equal SPEC_PREREG_SHA256 (C11)."""
    lo = "11" if M("g10_prereg_edit") else fnum(TH_LO)
    f = dict(lo=lo, hi=fnum(TH_HI), void=fnum(VOID_FRAC), thin=fnum(THIN_PCT), s2date=S2_DATE, thindate=THIN_DATE)
    return "".join(l.format(**f) + "\n" for l in PREREG_LINES)


def pop_text():
    """The canonical text of 4.7, rebuilt from the constants the code uses."""
    floor = "99999999" if M("g10_pop_edit") else fnum(REV_FLOOR)
    f = dict(panel_sha=PANEL_PIN["sha256"], n_cik=N_CIK, sic_lo=SIC_LO, sic_hi=SIC_HI, fy_start=FY_START, fy_end=FY_END, dur_min=DUR_MIN, dur_max=DUR_MAX, near=NEAR_DAYS,
             floor=floor, fye_a=FYE_A, fye_b=FYE_B, fye_c=FYE_C, fye_d=FYE_D, s2_lo=S2_LO, s2_hi=S2_HI)
    return "".join(l.format(**f) + "\n" for l in POP_LINES)


def fnum(x):
    """A constant as the text the canonical blocks print (10, 25, 0.02, 70, 100000000)."""
    s = format(Decimal(x), "f")
    return s.rstrip("0").rstrip(".") if "." in s else s


def prereg_ok():
    return sha256_of(prereg_text().encode("utf-8")) == SPEC_PREREG_SHA256


def pop_ok():
    return sha256_of(pop_text().encode("utf-8")) == SPEC_POP_SHA256


def prereg_sha_out():
    """The hash written to registered.csv's prereg_sha256 column; M27 holds its own literal copy. The mutant writes the hash of an edited text."""
    if M("g10_prereg_drift"):
        return sha256_of((prereg_text() + " ").encode("utf-8"))
    return SPEC_PREREG_SHA256


# ------------------------------------------------------------------------------------------------------------------------
# fiscal years (2.2, P3): a date rule, never the fy label
# ------------------------------------------------------------------------------------------------------------------------
TENK_FORMS = ("10-K", "10-K/A", "10-KT", "10-KT/A")
SUB_FIRST_DATE = "%d-%s" % (min(ALL_YEARS), FY_START)       # 2019-04-01: the earliest report date any needed year can have


def fy_of(report_date):
    """The fiscal year Y whose date window [Y-04-01, (Y+1)-03-31] holds a report date (G2). The mutants: the calendar year of the date (the fy-label error: a retailer with
    reportDate 2026-02-01 would land in FY2026), and each window edge off by a day."""
    if parse_date(report_date) is None:
        return None
    y, md = int(report_date[:4]), report_date[5:]
    if M("g2_fy_label"):
        return y
    if M("g2_edge_end"):
        return y if md >= "03-31" else y - 1               # 03-31 wrongly opens the next window
    if M("g2_edge_start"):
        return y if md > FY_START else y - 1               # 04-01 wrongly stays in the previous window
    return y if md >= FY_START else y - 1


def tenk_form_ok(form):
    """Only the original form 10-K defines D_Y; a 10-K/A or 10-KT never does (G2)."""
    if M("g2_amend_defines"):
        return form in TENK_FORMS
    return form == "10-K"


def year_map(filings):
    """{Y: [(report_date, accession, filing_date), ...]} from (form, report_date, filing_date, accession) rows; one entry per accession, ordered."""
    out = {}
    seen = set()
    for form, rd, fd, acc in filings:
        if not tenk_form_ok(form):
            continue
        y = fy_of(rd)
        if y is None or (y, acc) in seen:
            continue
        seen.add((y, acc))
        out.setdefault(y, []).append((rd, acc, fd))
    for y in out:
        out[y].sort()
    return out


def year_info(ymap, y):
    """(kind, D_Y, accession, filing_date): kind is 'one' for exactly one original 10-K in the window, 'many' for two or more (fy_ambiguous), 'none' for no 10-K (year_gap)."""
    xs = ymap.get(y, [])
    if len(xs) == 1:
        return "one", xs[0][0], xs[0][1], xs[0][2]
    if len(xs) >= 2:
        if M("g2_two_not_ambiguous"):
            return "one", xs[0][0], xs[0][1], xs[0][2]
        return "many", None, None, None
    return "none", None, None, None


# ------------------------------------------------------------------------------------------------------------------------
# documents to extract rows (the fetch modes, section 3 steps 1 to 3)
# ------------------------------------------------------------------------------------------------------------------------
def doc_cik(doc):
    return cik10(doc.get("cik")) if isinstance(doc, dict) else None


def sub_block_rows(block):
    """(form, report_date, filing_date, accession) rows of a submissions arrays block, for the 10-K family from 2019-04-01 on."""
    cols = [block.get(k) for k in ("form", "reportDate", "filingDate", "accessionNumber")]
    if not all(isinstance(c, list) for c in cols) or len({len(c) for c in cols}) != 1:
        raise DataError("a submissions block is not four parallel arrays")
    out = []
    for form, rd, fd, acc in zip(*cols):
        if form in TENK_FORMS and isinstance(rd, str) and parse_date(rd) is not None and rd >= SUB_FIRST_DATE and isinstance(acc, str) and acc:
            out.append((form, rd, fd if isinstance(fd, str) else "", acc))
    return out


def older_pages(cik, main):
    """The older submissions pages that can hold a 10-K reported on or after 2019-04-01: those whose filingTo is on or after it (or unstated). Names are checked, never built from the reply."""
    out = []
    files = (main.get("filings") or {}).get("files") or []
    for f in files:
        name = f.get("name") if isinstance(f, dict) else None
        if not isinstance(name, str) or not SUBPAGE_RX.match("/submissions/" + name) or SUBPAGE_RX.match("/submissions/" + name).group(1) != cik:
            continue
        to = f.get("filingTo")
        if to is None or not isinstance(to, str) or to >= SUB_FIRST_DATE:
            out.append(name)
    return sorted(set(out))


def submissions_rows(vintage, cik, main, pages):
    """The submissions_extract rows of one firm: the 10-K family rows of the main file and its older pages, firm-level sic and fiscalYearEnd on each row; one row with blank filing
    columns when there is none, so that sic and the year end are kept."""
    sic = main.get("sic")
    sic = str(sic).strip() if isinstance(sic, (str, int)) and not isinstance(sic, bool) else ""
    fye = main.get("fiscalYearEnd")
    fye = fye.strip() if isinstance(fye, str) else ""
    rows = set(sub_block_rows((main.get("filings") or {}).get("recent") or {}))
    for p in pages:
        rows |= set(sub_block_rows(p))
    out = [[vintage, cik, sic, fye, f, rd, fd, acc] for f, rd, fd, acc in sorted(rows, key=lambda r: (r[1], r[2], r[3], r[0]))]
    return out or [[vintage, cik, sic, fye, "", "", "", ""]]


def wanted_ends(dmap, vintage):
    """(set of end dates within 7 days of a needed D_Y, cut): the facts to extract and the last end date allowed. Before S2's date there is no fact with end after D_2025 (or after
    2026-03-31 where the firm has no D_2025): R1-10, C10."""
    last = 2026 if s2_open(vintage) else 2025
    cut = None if s2_open(vintage) else (dmap.get(2025) or "2026-03-31")
    ends = set()
    for y in range(min(ALL_YEARS), last + 1):
        d = dmap.get(y)
        if not d:
            continue
        for off in range(-NEAR_DAYS, NEAR_DAYS + 1):
            e = add_days(d, off)
            if M("g8_extract_all") or cut is None or e <= cut:
                ends.add(e)
    return ends, cut


def companyfacts_rows(vintage, cik, doc, dmap):
    """Every candidate USD fact for the tags of 2.4 whose end is within 7 days of a needed D_Y (and not after the cut), with filed, form, accn. Only the us-gaap USD unit; the mutant
    takes any unit."""
    ends, cut = wanted_ends(dmap, vintage)
    gaap = ((doc.get("facts") or {}).get("us-gaap")) or {}
    out = []
    for tag in CF_TAGS:
        td = gaap.get(tag)
        if not isinstance(td, dict):
            continue
        units = td.get("units") or {}
        lst = units.get("USD")
        if lst is None and M("g1_nonusd_ok") and units:
            lst = units[sorted(units)[0]]
        for e in lst or []:
            end = e.get("end")
            if end not in ends:
                continue
            vt = num_text(e.get("val"))
            if vt == "":
                raise DataError("a used fact is not a number (%s, %s)" % (tag, end))
            fy = num_text(e.get("fy")) if e.get("fy") is not None else ""
            out.append([vintage, cik, tag, e.get("start") or "", end, vt, e.get("accn") or "", e.get("form") or "", e.get("fp") or "", fy, e.get("filed") or ""])
    out.sort(key=lambda r: (r[2], r[4], r[3], r[10], r[6], r[5]))
    return out


def frame_rows(vintage, tag, period, doc, panel_ciks):
    """The rows of one frame for the 500 CIKs only. pts is the number of filers in the whole frame and is never a count of the 500 (G1)."""
    out = []
    for e in doc.get("data") or []:
        c = cik10(e.get("cik"))
        if c in panel_ciks:
            vt = num_text(e.get("val"))
            if vt == "":
                raise DataError("a frame value is not a number (%s, %s)" % (tag, period))
            out.append([vintage, tag, period, c, e.get("accn") or "", e.get("start") or "", e.get("end") or "", vt])
    out.sort(key=lambda r: (r[3], r[6], r[5], r[4], r[7]))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# the extract files (committed, per vintage) and their loaders; the loaders are stage-aware (R1-19, C10)
# ------------------------------------------------------------------------------------------------------------------------
def source_line_vintage(vintage, what=""):
    return ("# source: US Securities and Exchange Commission, EDGAR XBRL APIs (companyfacts, submissions, frames) on data.sec.gov, vintage %s%s" % (vintage, ("; " + what) if what else ""))


READ_LOG = []                     # (cik10, end) of every fact value the loaders converted; C10 and G11 read it


def mixed(row_vintage, vintage, name):
    """A build reads one vintage: a row stamped with another vintage stops it (R4, G16)."""
    if row_vintage != vintage and not M("g16_mixed_ok"):
        raise DataError("%s holds a row of vintage %s in a build of vintage %s: a build never mixes vintages" % (name, row_vintage, vintage))


def load_submissions(path, stage, vintage):
    """{cik: {'sic','fye','filings':[(form, report_date, filing_date, accession)]}} from the submissions extract. The pre stage reads no 10-K row reported after the FY2022 window."""
    h, rows = read_csv_rows(path)
    if h != ALLOW["submissions_extract.csv"]:
        raise DataError("submissions_extract.csv: header is not the exact column allowlist")
    ix = {c: i for i, c in enumerate(h)}
    out = {}
    for r in rows:
        mixed(r[ix["vintage"]], vintage, "submissions_extract.csv")
        c = r[ix["cik10"]]
        d = out.setdefault(c, {"sic": r[ix["sic"]], "fye": r[ix["fye_mmdd"]], "filings": []})
        rd = r[ix["report_date"]]
        if not r[ix["form"]]:
            continue
        if stage == "pre" and rd > PRE_DATE_LIMIT and not M("g11_pre_reads_all"):
            continue
        d["filings"].append((r[ix["form"]], rd, r[ix["filing_date"]], r[ix["accession"]]))
    return out


def pre_cut(ymap):
    """The last end date the pre stage may read for a firm: D_2022 + 7 days, or the end of FY2022's window where the firm has no unique D_2022."""
    kind, d, _, _ = year_info(ymap, PRE_LAST_YEAR)
    return add_days(d, NEAR_DAYS) if kind == "one" else PRE_DATE_LIMIT


def full_cut(ymap, vintage):
    """The last end date a full-stage build may read before S2's date: D_2025 (or 2026-03-31 without one). None from S2's date on."""
    if s2_open(vintage):
        return None
    kind, d, _, _ = year_info(ymap, 2025)
    return d if kind == "one" else "2026-03-31"


def load_cf(path, cuts, stage, vintage):
    """{cik: {tag: [(start, end, val, accn, form, fp, fy, filed)]}}. A row whose end is after the firm's cut is skipped on its end date alone: its val is never converted (the pre stage's
    blindness, G11). Returns (facts, n_skipped, n_beyond): n_beyond counts rows after the cut that a full-stage extract should not hold at all (C10)."""
    h, rows = read_csv_rows(path)
    if h != ALLOW["cf_extract.csv"]:
        raise DataError("cf_extract.csv: header is not the exact column allowlist")
    ix = {c: i for i, c in enumerate(h)}
    out, skipped = {}, 0
    for r in rows:
        mixed(r[ix["vintage"]], vintage, "cf_extract.csv")
        c, end = r[ix["cik10"]], r[ix["end"]]
        cut = cuts.get(c)
        if cut is not None and end > cut and not M("g11_pre_reads_all"):
            skipped += 1
            continue
        v = to_dec(r[ix["val"]])
        READ_LOG.append((c, end))
        out.setdefault(c, {}).setdefault(r[ix["tag"]], []).append((r[ix["start"]], end, v, r[ix["accn"]], r[ix["form"]], r[ix["fp"]], r[ix["fy"]], r[ix["filed"]]))
    return out, skipped


def load_frames(path, stage, vintage):
    """{(tag, period): {cik: [(accn, start, end, val)]}}. The pre stage reads the CY2019 periods only, decided on the period column before any value is converted."""
    h, rows = read_csv_rows(path)
    if h != ALLOW["frames_extract.csv"]:
        raise DataError("frames_extract.csv: header is not the exact column allowlist")
    ix = {c: i for i, c in enumerate(h)}
    out = {}
    for r in rows:
        mixed(r[ix["vintage"]], vintage, "frames_extract.csv")
        period = r[ix["period"]]
        if stage == "pre" and frame_year(period) > 2019 and not M("g11_pre_reads_all"):
            continue
        out.setdefault((r[ix["tag"]], period), {}).setdefault(r[ix["cik10"]], []).append((r[ix["accn"]], r[ix["start"]], r[ix["end"]], to_dec(r[ix["val"]])))
    return out


def frame_year(period):
    m = re.match(r"^CY(\d{4})", period or "")
    return int(m.group(1)) if m else 0


def frame_period_ok(period, vintage):
    """No frame for a calendar year of 2026 or later is fetched before S2's date (R1-10, G8). Stricter than the spec's CY2026Q2I-and-later: any 2026 period is held back."""
    if not re.match(r"^CY\d{4}(?:Q[1-4]I?)?$", period or ""):
        return False
    if frame_year(period) >= 2026 and not s2_open(vintage):
        return False
    return True


def frame_plan(vintage):
    """[(tag, period)] to fetch: the tags of 2.4 at CY2019Q4I, CY2023Q4I, CY2025Q4I (instants) and CY2019, CY2023, CY2025 (durations), plus CY2026Q4I and CY2026 from S2's date on."""
    years = list(FRAME_YEARS) + ([2026] if s2_open(vintage) else [])
    plan = []
    for tag, _ in FRAME_INSTANTS:
        plan += [(tag, "CY%dQ4I" % y) for y in years]
    for tag, _ in FRAME_DURATIONS:
        plan += [(tag, "CY%d" % y) for y in years]
    return plan


def frame_path(tag, period):
    return "/api/xbrl/frames/us-gaap/%s/USD/%s.json" % (tag, period)


def raw_name(path):
    """The cache file (below raw/) for a request path; None for a path that is not one of the three kinds."""
    m = SUB_RX.match(path) or SUBPAGE_RX.match(path)
    if m:
        return "submissions/" + path.rsplit("/", 1)[1]
    m = CF_RX.match(path)
    if m:
        return "companyfacts/" + path.rsplit("/", 1)[1]
    m = FRAME_RX.match(path)
    if m:
        return "frames/%s__%s.json" % (m.group(1), m.group(2))
    return None


def kind_of(path):
    if SUB_RX.match(path) or SUBPAGE_RX.match(path):
        return "submissions"
    if CF_RX.match(path):
        return "companyfacts"
    if FRAME_RX.match(path):
        return "frames"
    return None


# ------------------------------------------------------------------------------------------------------------------------
# firms, fact selection (2.3, P4, P5) and structure (2.4, P6-P10)
# ------------------------------------------------------------------------------------------------------------------------
NONE3 = ("none", None, None)
CONFLICTS = []                    # (cik10, tag, fiscal year) where one filing states two different values for the same context: treated as missing


class Firm(object):
    """One CIK: its filings (the submissions extract), its facts (the companyfacts extract) and the panel's tickers. Facts are (start, end, val, accn, form, fp, fy, filed)."""

    def __init__(self, cik, tickers, name="", sic="", fye="", no_record=False, filings=(), facts=None):
        self.cik, self.tickers, self.name, self.sic, self.fye = cik, tuple(tickers), name, sic, fye
        self.no_record = no_record
        self.filings = list(filings)
        self.facts = facts or {}
        self._ymap = None
        self._idx = None
        self._ends = {}

    def ymap(self):
        if self._ymap is None:
            self._ymap = year_map(self.filings)
        return self._ymap

    def info(self, y):
        return year_info(self.ymap(), y)

    def idx(self):
        if self._idx is None:
            self._idx = {}
            for tag, lst in self.facts.items():
                d = self._idx.setdefault(tag, {})
                for f in lst:
                    d.setdefault(f[1], []).append(f)
        return self._idx

    def ends(self, y):
        """[(offset, end date)] for the days D_Y-7 .. D_Y+7 of year y."""
        if y not in self._ends:
            kind, d, _, _ = self.info(y)
            self._ends[y] = [(off, add_days(d, off)) for off in range(-NEAR_DAYS, NEAR_DAYS + 1)] if kind == "one" else []
        return self._ends[y]

    def ticker(self):
        return "|".join(self.tickers)


def _span_ok(start, end, duration):
    """A duration fact is an annual one when 350 <= days(end - start) <= 380 (P5, G3). The mutants move each edge by a day."""
    if not duration:
        return True
    n = days_between(start, end)
    if n is None:
        return False
    lo = DUR_MIN - 1 if M("g3_lo_349") else (DUR_MIN + 1 if M("g3_lo_351") else DUR_MIN)
    hi = DUR_MAX + 1 if M("g3_hi_381") else (DUR_MAX - 1 if M("g3_hi_379") else DUR_MAX)
    return lo <= n <= hi


def _latest(facts):
    """The facts with the greatest (filed, accn): the latest-filed fact, ties to the largest accn (P4). The mutant takes the first-reported."""
    key = (lambda f: (f[7], f[3]))
    k = min(map(key, facts)) if M("g3_latest_first") else max(map(key, facts))
    return [f for f in facts if key(f) == k]


def _value(firm, tag, y, facts):
    vals = {f[2] for f in facts}
    if len(vals) == 1:
        return ("exact", facts[0][2], facts[0][3])
    CONFLICTS.append((firm.cik, tag, y))
    return NONE3


def cell(firm, tag, y, basis):
    """What the firm states for one tag at fiscal year y: ('exact', val, accn), ('near', None, None) when only a fact within 7 days of D_Y exists in the year's own 10-K, or ('none', ...).
    Selection is by end (and start for durations) and never by fy or fp. basis own_10k takes the fact whose accn is the year's original 10-K; latest_filed takes the latest-filed fact."""
    kind, D_, accn, _ = firm.info(y)
    if kind != "one":
        return NONE3
    byend = firm.idx().get(tag)
    if not byend:
        return NONE3
    duration = tag in DURATION_TAGS
    exact, near = [], []
    for off, e in firm.ends(y):
        for f in byend.get(e, ()):
            if not _span_ok(f[0], f[1], duration):
                continue
            if M("g3_use_fy") and f[6] != str(y):
                continue
            (exact if off == 0 or M("g3_near_used") else near).append(f)
    if basis == "own_10k":
        own = _latest(exact) if (M("g3_own_latest") and exact) else [f for f in exact if f[3] == accn]
        if own:
            return _value(firm, tag, y, own)
        if [f for f in near if f[3] == accn]:
            return ("near", None, None)
        return NONE3
    if exact:
        return _value(firm, tag, y, _latest(exact))
    return NONE3


def cell_in_filing(firm, tag, y, filing_year):
    """What the original 10-K of filing_year states for tag at fiscal year y (a comparative column when filing_year is later than y): the fact with end exactly D_y (and, for a duration, 350 to 380 days)
    whose accn is that 10-K's accession. ('exact', val, accn) or ('none', None, None). The same-filing basis of R3-1 uses it."""
    kind, D_, _, _ = firm.info(y)
    fkind, _, faccn, _ = firm.info(filing_year)
    if kind != "one" or fkind != "one":
        return NONE3
    if M("g3_sf_latest"):
        return cell(firm, tag, y, "latest_filed")                      # the mutant: the latest-filed fact, whatever filing it sits in
    duration = tag in DURATION_TAGS
    facts = [f for f in (firm.idx().get(tag) or {}).get(D_, ()) if _span_ok(f[0], f[1], duration) and f[3] == faccn]
    return _value(firm, tag, y, facts) if facts else NONE3


def sf_prev(firm, struct, y, filing_year):
    """(N, revenue) of fiscal year y as the 10-K of filing_year reports them, or None when that filing does not tag all of them (the caller then falls back to the first-reported values). The tags are
    those of the firm's primary structure; a contract-balance family with no tag anywhere is zero."""
    n = {}
    for comp in ("ca", "cl"):
        st, tags = struct[comp]
        if st == "absent_everywhere":
            n[comp] = Decimal(0)
            continue
        if st in ("gap", "gap0") or not tags:
            return None
        tot = Decimal(0)
        for t in tags:
            got, v, _ = cell_in_filing(firm, t, y, filing_year)
            if got != "exact":
                return None
            tot += v
        n[comp] = tot
    rtags = struct["rev"][1]
    if not rtags:
        return None
    got, rev, _ = cell_in_filing(firm, rtags[0], y, filing_year)
    if got != "exact":
        return None
    return n["ca"] - n["cl"], rev


def sf_restated(firm, struct, y, filing_year):
    """True when the 10-K of filing_year states, for any tag of the firm's primary structure (contract balances and revenue), a value for year y that differs from the first-reported one (a restated
    comparative)."""
    tags = [t for comp in ("ca", "cl") if struct[comp][0] not in ("absent_everywhere", "gap", "gap0") for t in struct[comp][1]] + list(struct["rev"][1][:1])
    for t in tags:
        a, b = cell_in_filing(firm, t, y, filing_year), cell(firm, t, y, "own_10k")
        if a[0] == "exact" and b[0] == "exact" and a[1] != b[1]:
            return True
    return False


def samefiling_calc(firm, wname, struct, wc):
    """R3-1, added after the result was seen: AA_t = N_t - r_(t-1) x Rev_t for the base and end year, with r_(t-1) from the year-t original 10-K's own comparative column (N and revenue of year t-1 as
    reported in the SAME accession as year t) and, where that filing does not tag the comparative, from the first-reported values (the primary's r). N_t and Rev_t are the primary's. Returns
    (a copy of wc with the new excess accrual and T, whether any fallback was used, whether any comparative was restated), or (None, True, False) in the mutant that drops a firm without the
    comparative."""
    w = WINDOWS[wname]
    b, e = w["b"], w["e"]
    aa, fallback, restated = {}, False, False
    for y in (b, e):
        restated = restated or sf_restated(firm, struct, y - 1, y)
        pair = None if M("g3_sf_first_reported") else sf_prev(firm, struct, y - 1, y)
        if pair is None or pair[1] == 0:
            if M("g3_sf_no_fallback"):
                return None, True, False
            rprev = wc["r"][y - 1]
            fallback = True
        else:
            rprev = pair[0] / pair[1]
        aa[y] = wc["n"][y] - rprev * wc["rev"][y]
    out = dict(wc)
    out["aa_b"], out["aa_e"], out["t"] = aa[b], aa[e], aa[e] - aa[b]
    return out, fallback, restated


def sic_int(s):
    s = (s or "").strip()
    return int(s) if s.isdigit() else None


def sic_financial(sic):
    """SIC 6000-6799 inclusive is excluded (P2, G7). The mutants: both ends kept, and both neighbours excluded."""
    if M("g7_sic_exclusive"):
        return SIC_LO < sic < SIC_HI
    if M("g7_sic_wide"):
        return SIC_LO - 1 <= sic <= SIC_HI + 1
    return SIC_LO <= sic <= SIC_HI


def below_floor(rev):
    """Revenue below 100,000,000 USD at a needed year is tiny_revenue; exactly 100,000,000 is not (P11, G7)."""
    if M("g7_floor_off_by_one"):
        return rev < REV_FLOOR - 1
    return rev < REV_FLOOR


def resolve_balance(avail, Ys, T, C, N):
    """(structure, tags, total_gt_parts, parts) for a total/current/noncurrent family (P6, P7, R1-14). avail: {tag: {year: value}}. The total is used when it is at least its parts at
    every year (the parts being those tagged at that year), else the parts; a tag present at some years only is a gap (P8)."""
    allY = set(Ys)
    has = {t: set(avail[t]) for t in (T, C, N)}
    if not any(has.values()):
        return "absent_everywhere", [], False, []
    P = [t for t in (C, N) if has[t]]
    parts_ok = bool(P) and all(has[t] == allY for t in P)
    if has[T] == allY:
        if not P:
            return "total", [T], False, []
        ge, gt = True, False
        for y in Ys:
            ps = sum((avail[t][y] for t in P if y in avail[t]), Decimal(0))
            if avail[T][y] < ps:
                ge = False
            if avail[T][y] > ps:
                gt = True
        if M("g4_parts_when_total_ok") and parts_ok:
            return "parts", P, False, P
        if ge or M("g4_total_when_lt"):
            return "total", ([T] + P if M("g4_add_total_parts") else [T]), gt, (P if parts_ok else [])
        if parts_ok:
            return "parts", P, False, P
        return "gap", [], False, []
    if parts_ok:
        return "parts", P, False, P
    return "gap", [], False, []


def resolve_cl(avail, Ys):
    st, tags, gt, parts = resolve_balance(avail, Ys, CL_T, CL_C, CL_N)
    if st == "absent_everywhere":
        allY = set(Ys)
        P = [t for t in (DEF_C, DEF_N) if avail[t]]
        if not P:
            return st, tags, gt, parts
        if all(set(avail[t]) == allY for t in P):
            return "deferred_revenue", P, False, []
        return "gap", [], False, []
    if M("g4_deferred_beside") and st in ("total", "parts") and avail[DEF_C]:
        tags = tags + [DEF_C]
    return st, tags, gt, parts


def resolve_rev(avail, Ys):
    """R2 if at every needed year, else R3, else Revenues (rev_fallback); one tag per window (P9, R1-3)."""
    allY = set(Ys)
    order = [REV_R2, REV_R3, REV_ANY]
    if M("g4_revenues_over_r2"):
        order = [REV_ANY, REV_R2, REV_R3]
    if M("g4_skip_r3"):
        order = [REV_R2, REV_ANY]
    for t in order:
        if allY and set(avail[t]) == allY:
            return "single", [t]
    if M("g4_rev_switch") and allY and all(any(y in avail[t] for t in order) for y in Ys):
        return "single", order
    return "gap", []


def resolve_single(avail, Ys, tag):
    allY = set(Ys)
    if allY and set(avail[tag]) == allY:
        return "single", [tag]
    if not avail[tag]:
        return "absent_everywhere", []
    return "gap", []


FAMILY_TAGS = {"rev": (REV_R2, REV_R3, REV_ANY), "ni": (NI_TAG,), "ca": (CA_T, CA_C, CA_N), "cl": (CL_T, CL_C, CL_N, DEF_C, DEF_N)}
ALL_FAMILY_TAGS = tuple(sorted({t for ts in FAMILY_TAGS.values() for t in ts} | {AR_A1, CC_TAG}))


def window_years(wname):
    ys = tuple(WINDOWS[wname]["years"])
    if M("g5_fy2022_ok") and wname == "fy2023_fy2025":
        ys = ys[1:]                                  # the mutant forgets FY2022 as an input year
    return ys


def classify(firm, years):
    """Status, flags and the tag structure of one firm for the needed years of a window, on the own_10k basis (P2-P12). Returns a dict: status, flags, years, info {y: year_info}, struct
    {component: (structure, tags)}, parts {ca|cl: tags usable as parts}, avail {tag: {year: value}}."""
    res = {"status": None, "flags": set(), "years": tuple(years), "info": {}, "struct": {}, "parts": {}, "avail": {}, "alt": {}}
    if firm.no_record:
        res["status"] = "no_sec_record"
        return res
    sic = sic_int(firm.sic)
    if sic is not None and sic_financial(sic):
        res["status"] = "financial_sic"
        return res
    if sic is None:
        res["status"] = "no_sic"
        return res
    res["info"] = {y: firm.info(y) for y in years}
    if any(res["info"][y][0] == "many" for y in years):
        res["status"] = "fy_ambiguous"
        return res
    Ys = [y for y in years if res["info"][y][0] == "one"]
    flags = res["flags"]
    if len(Ys) < len(years):
        flags.add("gap_10k")
    avail, near = {}, {}
    for tag in ALL_FAMILY_TAGS + (UNB_TAG,):
        avail[tag], near[tag] = {}, set()
        for y in Ys:
            st, v, _ = cell(firm, tag, y, "own_10k")
            if st == "exact":
                avail[tag][y] = v
            elif st == "near":
                near[tag].add(y)
    res["avail"] = avail
    mismatch = False
    for fam in FAMILY_TAGS.values():
        for y in Ys:
            if not any(y in avail[t] for t in fam) and any(y in near[t] for t in fam):
                mismatch = True
    if any(near[t] for t in ALL_FAMILY_TAGS):
        flags.add("near_end")
    if M("g3_near_no_mismatch"):
        mismatch = False
    st_rev, tags_rev = resolve_rev(avail, Ys)
    st_ni, tags_ni = resolve_single(avail, Ys, NI_TAG)
    st_ca, tags_ca, gt_ca, parts_ca = resolve_balance(avail, Ys, CA_T, CA_C, CA_N)
    st_cl, tags_cl, gt_cl, parts_cl = resolve_cl(avail, Ys)
    st_ar, tags_ar = resolve_single(avail, Ys, AR_A1)
    st_cc, tags_cc = resolve_single(avail, Ys, CC_TAG)
    if st_rev == "single" and tags_rev[:1] == [REV_ANY]:
        flags.add("rev_fallback")
    if gt_ca or gt_cl:
        flags.add("total_gt_parts")
    if st_rev == "gap":
        flags.add("gap_rev")
    if st_ni != "single":
        flags.add("gap_ni")
    if (st_ca == "gap" or st_cl == "gap") and not M("g5_partial_in_primary"):
        flags.add("gap_n")
    res["struct"] = {"ca": (st_ca, tags_ca), "cl": (st_cl, tags_cl), "rev": (st_rev, tags_rev), "ni": ("single" if st_ni == "single" else "gap", tags_ni),
                     "ar": (st_ar, tags_ar), "contract_cost": (st_cc, tags_cc)}
    res["parts"] = {"ca": parts_ca, "cl": parts_cl}
    res["alt"] = {"unbilled_all": set(avail[UNB_TAG]) == set(Ys) and bool(Ys)}
    if M("g5_absent_excluded") and st_ca == "absent_everywhere" and st_cl == "absent_everywhere":
        flags.add("gap_n")
    if mismatch:
        res["status"] = "end_mismatch"
        return res
    if flags & {"gap_10k", "gap_n", "gap_rev", "gap_ni"}:
        res["status"] = "year_gap"
        return res
    rev = series(firm, tags_rev, Ys, "own_10k", rev_mode=True)
    if rev is None or any(below_floor(v) for v in rev.values()):
        res["status"] = "tiny_revenue"
        return res
    res["status"] = "in_scope"
    if M("g5_old_status") and st_ar == "absent_everywhere":
        res["status"] = "no_receivable"
    return res


def series(firm, tags, years, basis, zero_missing=False, rev_mode=False, acc=None, comp=""):
    """{year: sum of the tags' values} or None when a tag is missing at a year. A tag missing is never zero, except where zero_missing says so (sens_gap0). The mutant for revenue
    takes, year by year, the first tag that has a value (a tag switching between years, G4)."""
    out = {}
    for y in years:
        tot = Decimal(0)
        if rev_mode and len(tags) > 1:
            got = None
            for t in tags:
                st, v, a = cell(firm, t, y, basis)
                if st == "exact":
                    got = (v, a)
                    break
            if got is None:
                return None
            tot = got[0]
            if acc is not None:
                acc.append((firm.cik, comp, y, got[1]))
        else:
            for t in tags:
                st, v, a = cell(firm, t, y, basis)
                if st == "exact":
                    tot += v
                    if acc is not None:
                        acc.append((firm.cik, comp, y, a))
                elif not zero_missing:
                    return None
        out[y] = tot
    return out


def bal_series(firm, struct, years, basis, acc=None, comp=""):
    """A contract-balance component under a structure: zero every year when no tag exists anywhere (P8); the imputed 'gap0' structure fills a missing year with 0 (sens_gap0 only)."""
    st, tags = struct
    if st == "absent_everywhere":
        return {y: Decimal(0) for y in years}
    if st == "gap0":
        return series(firm, tags, years, basis, zero_missing=True, acc=acc, comp=comp)
    if st == "gap":
        if M("g5_partial_in_primary"):
            return series(firm, tags or [], years, basis, zero_missing=True)
        return None
    return series(firm, tags, years, basis, acc=acc, comp=comp)


def variant_struct(firm, cls, variant):
    """The structure of a sensitivity variant and the flags it adds: parts (sens_parts), unbilled (sens_unbilled), gap0 (sens_gap0). None where the variant does not apply."""
    base = dict(cls["struct"])
    flags = set()
    if variant == "primary" or variant == "latest":
        return base, flags
    if variant == "parts":
        for comp in ("ca", "cl"):
            if base[comp][0] == "total" and cls["parts"][comp]:
                base[comp] = ("parts", list(cls["parts"][comp]))
        return base, flags
    if variant == "unbilled":
        if base["ca"][0] == "absent_everywhere" and cls["alt"].get("unbilled_all"):
            base["ca"] = ("single", [UNB_TAG])
            flags.add("unbilled_added")
        return base, flags
    if variant == "gap0":
        if M("g5_gap0_off"):
            return None, flags
        avail = cls["avail"]
        did = False
        for comp, (T, C, N) in (("ca", (CA_T, CA_C, CA_N)), ("cl", (CL_T, CL_C, CL_N))):
            if base[comp][0] == "gap":
                if avail[T]:
                    tags = [T]
                else:
                    tags = [t for t in (C, N) if avail[t]]
                    if not tags and comp == "cl":
                        tags = [t for t in (DEF_C, DEF_N) if avail[t]]
                base[comp] = ("gap0", tags)
                did = True
        if not did:
            return None, flags
        flags.add("gap0_imputed")
        return base, flags
    raise DataError("unknown variant %r" % variant)


def window_calc(firm, wname, struct, basis="own_10k", acc=None, ar_in_n=False):
    """One firm in one window: the values, r, the excess accrual AA_t = N_t - r_(t-1) * Rev_t for each year after the first, T_i = AA_e - AA_b, and the change in net income.
    Returns a dict, or None when a value is missing. The mutants: AA with r_t (G6), EA as T (G6, G11), N and Rev from different filings (G3), receivables added to N (G4)."""
    w = WINDOWS[wname]
    years = window_years(wname)
    b, e = w["b"], w["e"]
    rev_basis = "latest_filed" if M("g3_mixed_accn") and basis == "own_10k" else basis
    rev = series(firm, struct["rev"][1], years, rev_basis, rev_mode=True, acc=acc, comp="rev")
    ni = series(firm, struct["ni"][1], years, basis, acc=acc, comp="ni")
    ca = bal_series(firm, struct["ca"], years, basis, acc=acc, comp="ca")
    cl = bal_series(firm, struct["cl"], years, basis, acc=acc, comp="cl")
    if rev is None or ni is None or ca is None or cl is None:
        return None
    n = {y: ca[y] - cl[y] for y in years}
    if M("g4_ar_in_n"):
        ar = series(firm, [AR_A1], years, basis)
        if ar:
            n = {y: n[y] + ar[y] for y in years}
    if M("g18_cc_in_n"):
        cc = series(firm, [CC_TAG], years, basis)
        if cc:
            n = {y: n[y] + cc[y] for y in years}
    if any(rev[y] == 0 for y in years):
        return None
    r = {y: n[y] / rev[y] for y in years}
    aa = {}
    for y in years[1:]:
        aa[y] = n[y] - (r[y] if M("g6_aa_rt") else r[y - 1]) * rev[y]
    ea = (r[e] - r[b]) * rev[e]
    t = ea if M("g6_t_is_ea") else aa[e] - aa[b]
    return {"years": years, "rev": rev, "ni": ni, "ca": ca, "cl": cl, "n": n, "r": r, "aa": aa, "t": t, "ea": ea, "dni": ni[e] - ni[b], "ni_b": ni[b], "rev_e": rev[e], "aa_b": aa[b], "aa_e": aa[e]}


# ------------------------------------------------------------------------------------------------------------------------
# records, samples and statistics (section 3, steps 6 to 14)
# ------------------------------------------------------------------------------------------------------------------------
ACQ_FRAC = Decimal("0.02")                    # R1-7: acquisitions over the window's years above 2% of base-year revenue
FULL_FLAG_WINDOWS = ("fy2023_fy2025", "fy2025_fy2026")


def placebo_windows():
    """The three placebo windows and no other (R1-6, G11). The mutant adds the S1 window, which needs FY2023-or-later values."""
    return PLACEBO_WINDOWS + (("fy2023_fy2025",) if M("g11_extra_window") else ())


def rec_flags(firm, cls, wc, wname, full):
    f = set(cls["flags"] & {"rev_fallback", "total_gt_parts", "near_end"})
    w = WINDOWS[wname]
    if any(abs(wc["r"][y]) > 1 for y in wc["years"]):
        f.add("extreme_r")
    if full:
        vals = [v for st, v, _ in (cell(firm, ACQ_TAG, y, "own_10k") for y in range(w["b"], w["e"] + 1)) if st == "exact"]
        if vals and dsum(vals) > ACQ_FRAC * wc["rev"][w["b"]]:
            f.add("acq2")
        if any(st == "exact" and v != 0 for st, v, _ in (cell(firm, DISC_TAG, y, "own_10k") for y in wc["years"])):
            f.add("disc_ops")
    return f


def make_rec(firm, wc, flags, placebo=False, struct=None):
    """One firm's row of one sample. Every USD cell is quantized once here (half-even, whole dollars); each aggregate is the sum of the cells that are written (C07, criterion 6)."""
    t = wc["ea"] if (M("g11_placebo_ea") and placebo) else wc["t"]
    return {"cik": firm.cik, "ticker": firm.ticker(), "name": firm.name, "aa_b": q0(wc["aa_b"]), "aa_e": q0(wc["aa_e"]), "t": q0(t), "dni": q0(wc["dni"]), "ni_b": q0(wc["ni_b"]),
            "rev_e": q0(wc["rev_e"]), "ea": wc["ea"], "flags": set(flags), "wc": wc, "struct": struct}


def build_primary(firms, order, clsw, wname, basis="own_10k", acc=None, placebo=False):
    full = wname in FULL_FLAG_WINDOWS
    recs = []
    for cik in order:
        cl = clsw[cik]
        if cl["status"] != "in_scope":
            continue
        firm = firms[cik]
        wc = window_calc(firm, wname, cl["struct"], basis, acc=acc)
        if wc is None:
            raise DataError("an in-scope firm has a missing value (%s, %s)" % (cik, wname))
        recs.append(make_rec(firm, wc, rec_flags(firm, cl, wc, wname, full), placebo=placebo, struct=cl["struct"]))
    return recs


def build_samples(firms, order, clsw, wname, s2set, acc=None):
    """The primary sample and the sensitivities of one window (3.8). Every sensitivity but sens_gap0 works on the primary firms; sens_gap0 adds the firms whose only gap is a contract-balance
    tag present at some years only."""
    prim = build_primary(firms, order, clsw, wname, acc=acc)
    pmap = {r["cik"]: r for r in prim}
    S = collections.OrderedDict()
    S["primary"] = prim
    S["mega"] = [r for r in prim if r["cik"] in MEGA]
    S["s2_subset"] = [r for r in prim if r["cik"] in s2set]
    S["sens_acq"] = [r for r in prim if "acq2" not in r["flags"]]
    S["sens_disc"] = [r for r in prim if "disc_ops" not in r["flags"]]
    S["sens_trim"] = [r for r in prim if "extreme_r" not in r["flags"]]
    S["sens_r2only"] = [r for r in prim if "rev_fallback" not in r["flags"]]
    pos = [r for r in prim if r["t"] > 0]
    top = max(pos, key=lambda r: (r["t"], r["cik"])) if pos else None
    S["sens_leave1"] = [r for r in prim if r is not top]
    for name, variant in (("sens_parts", "parts"), ("sens_unbilled", "unbilled"), ("sens_latest", "latest")):
        recs = []
        for r in prim:
            firm, cl = firms[r["cik"]], clsw[r["cik"]]
            struct, vf = variant_struct(firm, cl, variant)
            wc = window_calc(firm, wname, struct, "latest_filed" if variant == "latest" else "own_10k")
            if wc is None:
                raise DataError("a variant has a missing value (%s, %s)" % (r["cik"], variant))
            recs.append(make_rec(firm, wc, r["flags"] | vf, struct=struct))
        S[name] = recs
    g0 = []
    for cik in order:
        cl = clsw[cik]
        if cl["status"] == "in_scope":
            g0.append(pmap[cik])
        elif cl["status"] == "year_gap" and "gap_n" in cl["flags"] and not (cl["flags"] & {"gap_10k", "gap_rev", "gap_ni"}):
            firm = firms[cik]
            struct, vf = variant_struct(firm, cl, "gap0")
            if struct is None:
                continue
            wc = window_calc(firm, wname, struct)
            if wc is None or any(below_floor(v) for v in wc["rev"].values()):
                continue
            g0.append(make_rec(firm, wc, (cl["flags"] & {"gap_n", "near_end", "rev_fallback"}) | vf, struct=struct))
    S["sens_gap0"] = g0
    sf, sf_fb, sf_rs = [], [], []
    for r in prim:
        firm, cl = firms[r["cik"]], clsw[r["cik"]]
        wc2, fb, rs = samefiling_calc(firm, wname, cl["struct"], r["wc"])
        if wc2 is None:
            continue
        sf.append(make_rec(firm, wc2, r["flags"], struct=cl["struct"]))
        if fb:
            sf_fb.append(r["cik"])
        if rs:
            sf_rs.append(r["cik"])
    S["sens_samefiling"] = sf
    return S, {"samefiling_fallback": sf_fb, "samefiling_restated": sf_rs}


def leave_one_out(recs, nb_net, nb_gross):
    """Single-firm leave-one-out (R3-2; descriptive, not a registered statement): for each firm, S1's and S1P's scores on the sample without it. Returns [(rec, net score, gross score)]. The mutant
    leaves the firm in."""
    tot = calc_stats(recs)
    out = []
    for r in recs:
        d = {"t": r["t"], "tp": max(r["t"], 0), "tn": min(r["t"], 0), "dni": r["dni"], "ni_b": r["ni_b"], "rev": r["rev_e"], "ea": r["ea"]}
        if M("g9_loo_no_removal"):
            d = {k: Decimal(0) for k in d}
        st = {"n": tot["n"] - 1}
        st.update({k: tot[k] - d[k] for k in d})
        out.append((r, score_stat(st, nb_net), score_stat(st, nb_gross, gross=True)))
    return out


def fragility(recs, nb_net, nb_gross):
    """(S1 firms whose removal alone takes S1 below 10%: [(rec, share)], count of firms whose removal alone takes S1P below 25%). Counted only when the full sample is not already below the threshold."""
    full_net, full_gross = score_stat(calc_stats(recs), nb_net), score_stat(calc_stats(recs), nb_gross, gross=True)
    loo = leave_one_out(recs, nb_net, nb_gross)
    s1 = [(r, sc_["share"]) for r, sc_, _ in loo if full_net["label"] != "SHARE_BELOW_10" and sc_["label"] == "SHARE_BELOW_10"]
    low = ("SHARE_BELOW_10",) if M("g9_loo_s1p_threshold") else ("SHARE_BELOW_10", "SHARE_10_TO_25")
    n_s1p = sum(1 for r, _, sg in loo if full_gross["label"] == "SHARE_ABOVE_25" and sg["label"] in low)
    return s1, n_s1p


def calc_stats(recs):
    ts = [r["t"] for r in recs]
    t = dsum(ts)
    return {"n": len(recs), "t": t, "tp": t if M("g6_tpos_net") else dsum([x for x in ts if x > 0]), "tn": dsum([x for x in ts if x < 0]), "dni": dsum([r["dni"] for r in recs]),
            "ni_b": dsum([r["ni_b"] for r in recs]), "rev": dsum([r["rev_e"] for r in recs]), "ea": dsum([r["ea"] for r in recs])}


# ---- labels (3.7, 4.6) ----
def void_state(ni_b, dni):
    """VOID: base net income not positive, or the change below 2% of it (which covers every change at or below zero). The mutant tests only the sign of the change."""
    if M("g6_void_weak"):
        return "none" if dni > 0 else ("base_not_positive" if ni_b <= 0 else "dni_small")
    if ni_b <= 0:
        return "base_not_positive"
    if dni < VOID_FRAC * ni_b:
        return "dni_small"
    return "none"


def share_label(sh):
    """The label of a non-negative share in percent, on the unrounded Decimal: below 10, 10 to 25 inclusive, above 25 (G6). The mutants round first, or move an edge."""
    if M("g6_round_compare"):
        sh = sh.quantize(Decimal("0.001"), rounding=decimal.ROUND_HALF_EVEN)
    if (sh <= TH_LO) if M("g6_lo_inclusive") else (sh < TH_LO):
        return "SHARE_BELOW_10"
    if (sh < TH_HI) if M("g6_hi_exclusive") else (sh <= TH_HI):
        return "SHARE_10_TO_25"
    return "SHARE_ABOVE_25"


def direction_of(t):
    d = "with_growth" if t > 0 else ("against_growth" if t < 0 else "zero")
    if M("g6_dir_wrong"):
        d = {"with_growth": "against_growth", "against_growth": "with_growth"}.get(d, d)
    return d


def qualifier_of(t, rev, nb):
    """within_pre_window_range when |T| / sum Rev_e is at most the frozen band, else outside; none without a band (4.6)."""
    if nb is None or rev == 0:
        return "none"
    return "within_pre_window_range" if abs(t) / rev <= nb else "outside_pre_window_range"


def score_stat(st, nb, gross=False):
    """The statistic's label, void reason, share, direction and qualifier. VOID is tested first. gross scores share_pos (the sum of the positive T_i over the change in net income)."""
    ni_b, dni = st["ni_b"], st["dni"]
    num = st["tp"] if gross else st["t"]
    reason = void_state(ni_b, dni)
    if M("g6_void_last") and dni != 0:
        reason = "none"
    share = None
    if reason != "none":
        label = "VOID"
    else:
        share = num / dni * 100
        label = share_label(share if (gross or M("g6_label_signed")) else abs(share))
    out = {"label": label, "void_reason": reason, "share": share, "direction": direction_of(st["t"]), "qualifier": qualifier_of(st["t"], st["rev"], nb)}
    out["t_pct_rev"] = st["t"] / st["rev"] * 100 if st["rev"] != 0 else None
    out["t_days_rev"] = st["t"] / st["rev"] * DAYS_YEAR if st["rev"] != 0 else None
    return out


# ---- the placebo band (R1-6, R1-13, R2-1, R2-2) ----
def median(xs):
    xs = sorted(xs)
    if not xs:
        return None
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2


def placebo_table(recs_by_window):
    """(placebo.csv rows, band) from the three windows. band: nb1, nb2, med1, med2 as ratios of |T| to the sum of end-year revenue (None where undefined)."""
    rows, ratios = [], {}
    for w in placebo_windows():
        recs = recs_by_window[w]
        st = calc_stats(recs)
        wd = WINDOWS[w]
        sc = score_stat(st, None)
        yrs = wd["years"]
        rows.append([w, "FY%d..FY%d" % (min(yrs), max(yrs)), wd["includes_fy2020"], str(st["n"]), usd(st["t"]), usd(st["tp"]), usd(st["rev"]), pct3(sc["t_pct_rev"]), usd(st["dni"]),
                     pct3(sc["share"])])
        if st["rev"] != 0:
            ratios[w] = abs(st["t"]) / st["rev"]
    one_all = [w for w in placebo_windows() if WINDOWS[w]["e"] - WINDOWS[w]["b"] == 1 and w in ratios]
    one_no20 = [w for w in one_all if WINDOWS[w]["includes_fy2020"] == "no" or M("g11_nb1_with2020")]
    two = [w for w in placebo_windows() if WINDOWS[w]["e"] - WINDOWS[w]["b"] == 2 and w in ratios]
    band = {"nb1": max([ratios[w] for w in one_no20]) if one_no20 else None, "nb2": ratios[two[0]] if two else None,
            "med1": median([ratios[w] for w in one_all]), "med2": median([ratios[w] for w in two]), "windows": [w for w in placebo_windows() if w in ratios]}
    return rows, band


def frozen_band(current, existing):
    """The band S1 and S2 are scored against: the one frozen from the first full vintage (placebo.csv as it stands), never one recomputed from a later vintage (R1-13, G11)."""
    if existing is not None and not M("g11_band_recomputed"):
        return existing
    return current


def band_from_rows(rows):
    """The band back from placebo.csv's rows (window, years, includes_fy2020, n_firms, t_usd, t_pos_usd, rev_end_usd, ...): the ratios are rebuilt from the written cells."""
    ratios = {}
    for r in rows:
        t, rev = to_dec(r[4]), to_dec(r[6])
        if t is not None and rev not in (None, 0):
            ratios[r[0]] = abs(t) / rev
    one_all = [w for w in placebo_windows() if WINDOWS[w]["e"] - WINDOWS[w]["b"] == 1 and w in ratios]
    one_no20 = [w for w in one_all if WINDOWS[w]["includes_fy2020"] == "no"]
    two = [w for w in placebo_windows() if WINDOWS[w]["e"] - WINDOWS[w]["b"] == 2 and w in ratios]
    return {"nb1": max([ratios[w] for w in one_no20]) if one_no20 else None, "nb2": ratios[two[0]] if two else None,
            "med1": median([ratios[w] for w in one_all]), "med2": median([ratios[w] for w in two]), "windows": [w for w in placebo_windows() if w in ratios]}


def nb_for(statement, band):
    """S1 and S1P are measured against NB2 (the two-year window); S2 and S2P against the frozen NB1 (one year). The mutant gives S1 the NB1 (G10)."""
    if statement in ("S1", "S1P"):
        return band["nb1"] if M("g10_nb1_for_s1") else band["nb2"]
    return band["nb1"]


# ---- S2 (R1-9, R1-10, P13) ----
def fye_ok(fye):
    """S2_eligible_at_FY2025: a fiscalYearEnd (MMDD) in [1130, 1231] or [0101, 0215]."""
    return bool(re.match(r"^\d{4}$", fye or "")) and ((FYE_A <= fye <= FYE_B) or (FYE_C <= fye <= FYE_D))


def s2_date_ok(d):
    """D_2026 in [2026-11-30, 2027-02-15], both ends inside (G8). The mutants move each end by a day."""
    if parse_date(d) is None:
        return False
    lo = add_days(S2_LO, 1) if M("g8_edge_lo") else (add_days(S2_LO, -1) if M("g8_edge_lo_in") else S2_LO)
    hi = add_days(S2_HI, -1) if M("g8_edge_hi") else (add_days(S2_HI, 1) if M("g8_edge_hi_in") else S2_HI)
    return lo <= d <= hi


def thin_share(num, den):
    return (Decimal(num) / Decimal(den) * 100) if den else Decimal(0)


def is_thin(num, den):
    """Fewer than 70% of the eligible firms have a FY2026 10-K: 69.99% is thin, 70.00% is not (G8). The mutants move the edge."""
    sh = thin_share(num, den)
    if M("g8_thin_le"):
        return sh <= THIN_PCT
    if M("g8_thin_strict"):
        return sh < THIN_PCT - Decimal("0.01")
    return sh < THIN_PCT


def s2_phase(vintage, num, den):
    """PENDING before the S2 date, PENDING_THIN while thin, VOID (thin_coverage) once thin on or after 2027-08-01, else 'score' (4.6 order)."""
    if not s2_open(vintage) and not M("g8_score_early"):
        return "PENDING"
    if is_thin(num, den):
        if thin_void_open(vintage) and not M("g8_void_never"):
            return "VOID"
        return "PENDING_THIN"
    return "score"


def s2_fy2026_state(firm):
    """Where a firm's FY2026 original 10-K stands against the S2 year-end window [2026-11-30, 2027-02-15] (ruling S2-R1): 'in_window' (one 10-K whose period end is inside it), 'outside_window' (one
    10-K whose period end is outside it: the submissions fiscalYearEnd does not match the filing's period end; status end_mismatch for S2), 'ambiguous' (two or more original
    10-Ks: fy_ambiguous) or 'none' (not filed yet)."""
    kind, d, _, _ = firm.info(2026)
    if kind == "none":
        return "none"
    if kind == "many":
        return "ambiguous"
    return "in_window" if s2_date_ok(d) else "outside_window"


def s2_coverage(firms, elig):
    """The firms eligible at FY2025 sorted by their FY2026 10-K state. Only 'in_window' firms count in the numerator of the 70% test (S2-R1 b); the four lists add up to the denominator, which is
    unchanged (S2-R1 a). The mutant counts a firm whose 10-K ends outside the window."""
    out = {"in_window": [], "outside_window": [], "ambiguous": [], "none": []}
    for cik in elig:
        st = s2_fy2026_state(firms[cik])
        if st == "outside_window" and M("g8_outside_counted"):
            st = "in_window"
        out[st].append(cik)
    return out


def s2_scored_set(firms, order, cls_s2):
    """The firms S2 scores: in scope on FY2024-FY2026 and with a FY2026 10-K whose period end is inside the window. A firm whose 10-K ends outside it is excluded with status end_mismatch (S2-R1 c). The
    mutant scores it."""
    ok = ("in_window", "outside_window") if M("g8_outside_scored") else ("in_window",)
    return {cik for cik in order if cls_s2[cik]["status"] == "in_scope" and s2_fy2026_state(firms[cik]) in ok}


# ---- described tables: contributors, concentration, receivables, contract costs, remaining performance obligations, cash flows ----
def contributors(recs, k=10):
    """The ten largest T_i and the ten most negative of a sample (3.9): (positive rows, negative rows) of (rank, rec, share of the side's total in percent). The mutant keeps eleven."""
    kk = k + 1 if M("g9_eleven") else k
    pos = sorted([r for r in recs if r["t"] > 0], key=lambda r: (-r["t"], r["cik"]))[:kk]
    neg = sorted([r for r in recs if r["t"] < 0], key=lambda r: (r["t"], r["cik"]))[:kk]
    tp = dsum([r["t"] for r in recs if r["t"] > 0])
    tn = dsum([r["t"] for r in recs if r["t"] < 0])
    tt = dsum([r["t"] for r in recs])
    out_p = [(i + 1, r, (r["t"] / (tt if M("g9_share_over_t") else tp) * 100) if (tt if M("g9_share_over_t") else tp) != 0 else None) for i, r in enumerate(pos)]
    out_n = [(i + 1, r, (r["t"] / (tt if M("g9_share_over_t") else tn) * 100) if (tt if M("g9_share_over_t") else tn) != 0 else None) for i, r in enumerate(neg)]
    return out_p, out_n


def top5_shares(recs):
    """The five largest firms' shares of gross positive T and of gross negative T, in percent (R1-11). The mutant takes the five largest by absolute value across both sides."""
    ts = [r["t"] for r in recs]
    tp, tn = dsum([x for x in ts if x > 0]), dsum([x for x in ts if x < 0])
    if M("g9_top5_abs"):
        top = sorted(recs, key=lambda r: (-abs(r["t"]), r["cik"]))[:5]
        p5 = dsum([r["t"] for r in top if r["t"] > 0])
        n5 = dsum([r["t"] for r in top if r["t"] < 0])
    else:
        p5 = dsum(sorted([x for x in ts if x > 0], reverse=True)[:5])
        n5 = dsum(sorted([x for x in ts if x < 0])[:5])
    return (p5 / tp * 100 if tp != 0 else None), (n5 / tn * 100 if tn != 0 else None)


def cl_top5_share(recs, y):
    cls_ = sorted([q0(r["wc"]["cl"][y]) for r in recs], reverse=True)
    tot = dsum(cls_)
    return (dsum(cls_[:5]) / tot * 100) if tot != 0 else None


def ar_series(firm, years):
    """Trade receivables, AccountsReceivableNetCurrent (A1) only (R1-2). The mutant falls back to A2 or A3, which are not trade receivables (G4, G18)."""
    s = series(firm, [AR_A1], years, "own_10k")
    if s is None and M("g4_ar_a2a3"):
        for t in (AR_A2, AR_A3):
            s = series(firm, [t], years, "own_10k")
            if s is not None:
                break
    return s


def receivables_table(firms, prim, wname):
    """receivables.csv: AR days per year and the same T construction on AR, marked collection, not recognition (3.11). Returns (rows, t_ar)."""
    years = window_years(wname)
    b, e = WINDOWS[wname]["b"], WINDOWS[wname]["e"]
    items = []
    for r in prim:
        ar = ar_series(firms[r["cik"]], years)
        if ar is not None:
            items.append((r, ar))
    measure = "" if M("g18_measure_missing") else "collection_not_recognition"
    rows = []
    for y in years:
        a = dsum([q0(ar[y]) for _, ar in items])
        v = dsum([q0(r["wc"]["rev"][y]) for r, _ in items])
        rows.append([wname, "level", str(y), measure, str(len(items)), usd(a), usd(v), days3(a / v * DAYS_YEAR) if v != 0 else "", "", ""])
    t_ar, rev_e = Decimal(0), Decimal(0)
    for r, ar in items:
        rev = r["wc"]["rev"]
        aa = {y: ar[y] - ar[y - 1] / rev[y - 1] * rev[y] for y in years[1:]}
        t_ar += q0(aa[e] - aa[b])
        rev_e += q0(rev[e])
    rows.append([wname, "window_t", str(e), measure, str(len(items)), "", "", "", usd(t_ar), days3(t_ar / rev_e * DAYS_YEAR) if rev_e != 0 else ""])
    return rows, t_ar


def descriptive_levels(firms, prim, wname, tag, mode=None):
    """Sum of a tag over the primary firms that state it at every year of the window: (n, {year: sum}, {year: sum of revenue}, {year: sum of N}). Used for contract costs and remaining
    performance obligations (3.12, 3.13)."""
    years = window_years(wname)
    items = []
    for r in prim:
        s = series(firms[r["cik"]], [tag], years, "own_10k")
        if s is not None:
            items.append((r, s))
    tot = {y: dsum([q0(s[y]) for _, s in items]) for y in years}
    rev = {y: dsum([q0(r["wc"]["rev"][y]) for r, _ in items]) for y in years}
    nn = {y: dsum([q0(r["wc"]["n"][y]) for r, _ in items]) for y in years}
    return len(items), tot, rev, nn


def cf_sign(firms, order, clsw):
    """The sign convention of each cash-flow change tag, set from FY2019-FY2022 for firms without acquisitions: +1 when the tag's sign matches the balance-sheet change in most firm-years,
    -1 when it opposes it (R1-7). Returns {'ca'|'cl'|'ar': (sign or None, n_same, n_opp)}. The mutant assumes +1 without looking."""
    spec = (("ca", CF_CA), ("cl", CF_CL), ("ar", CF_AR))
    out = {}
    for comp, tag in spec:
        same = opp = 0
        for cik in order:
            cl = clsw[cik]
            if cl["status"] != "in_scope":
                continue
            firm = firms[cik]
            years = cl["years"]
            if comp == "ar":
                bs = series(firm, [AR_A1], years, "own_10k")
            else:
                st = cl["struct"][comp]
                if st[0] in ("absent_everywhere", "gap"):
                    continue
                bs = bal_series(firm, st, years, "own_10k")
            if bs is None:
                continue
            for y in years[1:]:
                st_cf, v, _ = cell(firm, tag, y, "own_10k")
                if st_cf != "exact" or v == 0 or bs[y] == bs[y - 1]:
                    continue
                st_a, va, _ = cell(firm, ACQ_TAG, y, "own_10k")
                if st_a == "exact" and va != 0:
                    continue                                    # a firm-year with an acquisition is left out of the sign test
                if (v > 0) == (bs[y] - bs[y - 1] > 0):
                    same += 1
                else:
                    opp += 1
        sign = None if (same + opp) == 0 else (1 if same >= opp else -1)
        if M("g18_cf_sign_assumed"):
            sign = 1
        out[comp] = (sign, same, opp)
    return out


def cf_cross_check(firms, prim, wname, signs):
    """T with each year's change in N taken from the cash-flow change tags: AA_t = dN_t - r_(t-1) (Rev_t - Rev_(t-1)). Returns (n, T from cash flows, T from balances, sum of end revenue)
    over the primary firms that state the needed change tags (a firm whose family needs a tag with an undetermined sign is left out)."""
    w = WINDOWS[wname]
    b, e = w["b"], w["e"]
    n, tcf, tbs, rev_e = 0, Decimal(0), Decimal(0), Decimal(0)
    for r in prim:
        firm, wc = firms[r["cik"]], r["wc"]
        aa = {}
        ok = True
        if r["struct"]["ca"][0] == "absent_everywhere" and r["struct"]["cl"][0] == "absent_everywhere":
            continue
        for y in (b, e):
            dn = Decimal(0)
            for comp, tag, sg in (("ca", CF_CA, 1), ("cl", CF_CL, -1)):
                if r["struct"][comp][0] == "absent_everywhere":
                    continue
                st, v, _ = cell(firm, tag, y, "own_10k")
                if st != "exact" or signs[comp][0] is None:
                    ok = False
                    break
                dn += sg * signs[comp][0] * v
            if not ok:
                break
            aa[y] = dn - wc["r"][y - 1] * (wc["rev"][y] - wc["rev"][y - 1])
        if not ok:
            continue
        n += 1
        tcf += q0(aa[e] - aa[b])
        tbs += r["t"]
        rev_e += r["rev_e"]
    return n, tcf, tbs, rev_e


# ------------------------------------------------------------------------------------------------------------------------
# inputs: the panel, the vintage's extracts, vintages.csv and fetch_log.csv
# ------------------------------------------------------------------------------------------------------------------------
def read_panel(path):
    """The frozen population (R5): CIKs in order of first appearance, their tickers in file order, and the file's digest, size and row count."""
    raw = read_file(path, "rb")
    rd = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    order, tick, n = [], {}, 0
    for r in rd:
        n += 1
        c = (r.get("cik10") or "").strip()
        t = (r.get("ticker") or "").strip()
        if not re.match(r"^\d{10}$", c):
            raise DataError("the panel holds a cik10 that is not ten digits: %r" % c[:12])
        if c not in tick:
            order.append(c)
            tick[c] = []
        if t and t not in tick[c]:
            tick[c].append(t)
    return {"order": order, "tickers": tick, "sha": sha256_of(raw), "bytes": len(raw), "rows": n}


def vint_rows(out_dir):
    """All rows of vintages.csv as dicts."""
    h, rows = read_csv_rows(os.path.join(out_dir, "vintages.csv"))
    if rows and h != ALLOW["vintages.csv"]:
        raise DataError("vintages.csv: header is not the exact column allowlist")
    return [dict(zip(h, r)) for r in rows if r]


def fetch_rows(out_dir):
    h, rows = read_csv_rows(os.path.join(out_dir, "fetch_log.csv"))
    if rows and h != ALLOW["fetch_log.csv"]:
        raise DataError("fetch_log.csv: header is not the exact column allowlist")
    return [dict(zip(h, r)) for r in rows if r]


def read_names(raw_dir, order):
    """SEC registrant names from the cached submissions files (the only use of the raw cache besides C13); blank where a file is absent."""
    out = {}
    for c in order:
        p = os.path.join(raw_dir, "submissions", "CIK%s.json" % c)
        name = ""
        if os.path.isfile(p):
            try:
                doc = json.loads(read_file(p, "rb").decode("utf-8"))
                name = doc.get("name") if isinstance(doc, dict) and isinstance(doc.get("name"), str) else ""
            except ValueError:
                name = ""
        out[c] = title_name(name)
    return out


def load_inputs(cache, out_dir, vintage, stage, panel_path, pin=None, raw_dir=None, existing=True):
    """Everything a build reads, for one vintage and one stage. Refuses (DataError) when the fetch is incomplete: a CIK with neither a reply nor a recorded 404 is never read as absent."""
    if stage not in ("pre", "full"):
        raise Refused("--stage must be pre or full")
    if not vintage_ok(vintage):
        raise Refused("--vintage must be YYYYMMDD")
    vdir = os.path.join(cache, vintage)
    if not os.path.isdir(vdir):
        raise DataError("no vintage folder %s: run the fetch modes first" % tilde(vdir))
    del READ_LOG[:]
    pin = pin or PANEL_PIN
    panel = read_panel(panel_path)
    order = panel["order"]
    vr = [r for r in vint_rows(out_dir) if r["vintage"] == vintage]
    by_path = {r["url_path"]: r for r in vr}
    subs = load_submissions(os.path.join(vdir, "submissions_extract.csv"), stage, vintage)
    no_rec = set()
    for c in order:
        row = by_path.get("/submissions/CIK%s.json" % c)
        if row is None:
            raise DataError("vintages.csv has no submissions row for %s: the fetch is incomplete" % c)
        if row["status"] == "404":
            no_rec.add(c)
            continue
        cf = by_path.get("/api/xbrl/companyfacts/CIK%s.json" % c)
        if cf is None:
            raise DataError("vintages.csv has no companyfacts row for %s: the fetch is incomplete" % c)
        if cf["status"] == "404":
            no_rec.add(c)
    plan = [(t, p) for t, p in frame_plan(vintage) if stage == "full" or frame_year(p) <= 2019]
    fstat = {}
    for t, p in plan:
        row = by_path.get(frame_path(t, p))
        if row is None:
            raise DataError("vintages.csv has no row for the frame %s %s: the fetch is incomplete" % (t, p))
        fstat[(t, p)] = row["status"]
    firms = {}
    names = read_names(raw_dir or os.path.join(vdir, "raw"), order)
    for c in order:
        s = subs.get(c, {"sic": "", "fye": "", "filings": []})
        firms[c] = Firm(c, panel["tickers"][c], name=names.get(c, ""), sic=s["sic"], fye=s["fye"], no_record=c in no_rec, filings=s["filings"])
    cuts = {}
    for c in order:
        ym = firms[c].ymap()
        cuts[c] = pre_cut(ym) if stage == "pre" else full_cut(ym, vintage)
    facts, skipped = load_cf(os.path.join(vdir, "cf_extract.csv"), cuts, stage, vintage)
    for c, d in facts.items():
        if c in firms:
            firms[c].facts = d
    frames = load_frames(os.path.join(vdir, "frames_extract.csv"), stage, vintage)
    inp = {"stage": stage, "vintage": vintage, "panel": panel, "pin": pin, "order": order, "firms": firms, "vdir": vdir, "raw_dir": raw_dir or os.path.join(vdir, "raw"), "out_dir": out_dir,
           "vint_all": vint_rows(out_dir), "vint": vr, "fetch": fetch_rows(out_dir), "frame_status": fstat, "plan": plan, "frames": frames, "cf_skipped": skipped, "cuts": cuts,
           "read_log": list(READ_LOG), "no_rec": no_rec}
    inp["existing"] = load_existing(out_dir) if existing else {}
    return inp


def load_existing(out_dir):
    """The accumulating outputs as they stand: headline.csv, registered.csv and placebo.csv rows (the rest is regenerated)."""
    ex = {}
    for name, key in (("headline.csv", "headline"), ("registered.csv", "registered"), ("placebo.csv", "placebo")):
        p = os.path.join(out_dir, name)
        if os.path.isfile(p):
            h, rows = read_csv_rows(p)
            if h != ALLOW[name]:
                raise DataError("%s: header is not the exact column allowlist" % name)
            ex[key] = [r for r in rows if r]
    return ex


# ------------------------------------------------------------------------------------------------------------------------
# compute: classification, samples, statistics and the rows of every output
# ------------------------------------------------------------------------------------------------------------------------
def flag_text(flags):
    return "|".join(f for f in FLAG_ORDER if f in flags)


def hl(vintage, window, sample, statistic, value, unit, n=None):
    return [vintage, window, sample, statistic, value, unit, "" if n is None else str(n)]


def sample_headline(vintage, window, sample, st, sc, scg):
    """The headline rows of one sample: counts, sums, shares, labels, direction, qualifier, T in percent and in days of revenue (statistics, never registered, for the sensitivities)."""
    n = st["n"]
    rows = [hl(vintage, window, sample, "n_firms", str(n), "count", n)]
    for name, key in (("t_usd", "t"), ("t_pos_usd", "tp"), ("t_neg_usd", "tn"), ("dni_usd", "dni"), ("ni_base_usd", "ni_b"), ("rev_end_usd", "rev"), ("ea_usd", "ea")):
        rows.append(hl(vintage, window, sample, name, usd(st[key]), "usd", n))
    rows.append(hl(vintage, window, sample, "share_pct", pct3(sc["share"]), "pct", n))
    rows.append(hl(vintage, window, sample, "share_pos_pct", pct3(scg["share"]), "pct", n))
    rows.append(hl(vintage, window, sample, "label_net", sc["label"], "label", n))
    rows.append(hl(vintage, window, sample, "label_gross", scg["label"], "label", n))
    rows.append(hl(vintage, window, sample, "void_reason", sc["void_reason"], "label", n))
    rows.append(hl(vintage, window, sample, "direction", sc["direction"], "label", n))
    rows.append(hl(vintage, window, sample, "qualifier", sc["qualifier"], "label", n))
    rows.append(hl(vintage, window, sample, "t_pct_rev", pct3(sc["t_pct_rev"]), "pct", n))
    rows.append(hl(vintage, window, sample, "t_days_rev", days3(sc["t_days_rev"]), "days", n))
    return rows


def reg_row(sid, window, sample, vintage, n, num, st, sc, nb):
    return [sid, window, sample, vintage, str(n), usd(num), usd(st["t"]), usd(st["dni"]), usd(st["ni_b"]), pct3(sc["share"]), pct3(sc["t_pct_rev"]), days3(sc["t_days_rev"]),
            pct3(nb * 100) if nb is not None else "", sc["qualifier"], sc["direction"], sc["label"], sc["void_reason"], prereg_sha_out(), SPEC_POP_SHA256]


def pending_row(sid, window, sample, vintage, label, n="", reason="none"):
    return [sid, window, sample, vintage, str(n) if n != "" else "", "", "", "", "", "", "", "", "", "none", "", label, reason, prereg_sha_out(), SPEC_POP_SHA256]


def compute(inp):
    """All tables of one build as rows of strings (the committed text is rendered from them). Pure: no file is read or written here."""
    stage, vintage = inp["stage"], inp["vintage"]
    firms, order, pin = inp["firms"], inp["order"], inp["pin"]
    full = stage == "full"
    ex = inp.get("existing") or {}
    c = {"stage": stage, "vintage": vintage, "order": order, "firms": firms, "inp": inp, "acc": [], "rows": {}, "notes": []}
    del CONFLICTS[:]
    if full and not (prereg_ok() and pop_ok()):
        raise DataError("the statement constants do not reproduce the canonical texts of 4.6 and 4.7 (sha256 mismatch): registered.csv is not written")
    w1 = "fy2023_fy2025"
    w2 = "fy2025_fy2026"
    pw = list(placebo_windows())
    wnames = ([w1] if full else []) + pw
    cls = {w: {cik: classify(firms[cik], window_years(w)) for cik in order} for w in wnames}
    c["cls"] = cls
    cls25 = {cik: classify(firms[cik], (2024, 2025)) for cik in order} if full else {}
    elig25 = [cik for cik in order if full and fye_ok(firms[cik].fye) and cls25[cik]["status"] == "in_scope"]
    cov26 = s2_coverage(firms, elig25)
    have26 = cov26["in_window"]
    if sum(len(v) for v in cov26.values()) != len(elig25):
        raise DataError("the S2 coverage states do not add up to the eligible firms")
    phase = s2_phase(vintage, len(have26), len(elig25)) if full else None
    c["s2"] = {"phase": phase, "elig25": elig25, "have26": have26, "cov": cov26}
    s2scored = set()
    if phase == "score":
        cls[w2] = {cik: classify(firms[cik], window_years(w2)) for cik in order}
        s2scored = s2_scored_set(firms, order, cls[w2])
    s2set = s2scored if phase == "score" else set(elig25)
    prec = {w: build_primary(firms, order, cls[w], w, acc=c["acc"], placebo=True) for w in pw}
    c["prec"] = prec
    prow, band_now = placebo_table(prec)
    reg_old = ex.get("registered", [])
    s1_old = [r for r in reg_old if r[0] == "S1"]
    s1_vint = s1_old[0][3] if s1_old else None
    frozen = s1_vint is not None and s1_vint != vintage and not M("g16_rescore_s1")
    if frozen:
        if not ex.get("placebo"):
            raise DataError("S1 was scored on vintage %s but placebo.csv is missing: the frozen band cannot be read" % s1_vint)
        band = frozen_band(band_now, band_from_rows(ex["placebo"]))
        prow_out = ex["placebo"]
    else:
        band, prow_out = band_now, prow
    c["band"], c["band_now"], c["frozen"] = band, band_now, frozen
    c["placebo_rows"] = prow_out
    c["placebo_now"] = prow
    status_w = w1 if full else "fy2020_fy2022"
    signs = cf_sign(firms, order, cls["fy2020_fy2022"])
    c["signs"] = signs
    # --- firms.csv, firm_years.csv, firm_tags.csv
    S1 = None
    if full:
        S1, extras = build_samples(firms, order, cls[w1], w1, s2set, acc=c["acc"])
        c["extras"] = extras
        pm = {r["cik"]: r for r in S1["primary"]}
    else:
        pm = {r["cik"]: r for r in prec["fy2020_fy2022"]}
    c["S1"] = S1
    firm_rows = []
    for cik in order:
        f, cl = firms[cik], cls[status_w][cik]
        fl = set(cl["flags"]) | (pm[cik]["flags"] if cik in pm else set())
        firm_rows.append([cik, f.ticker(), f.name, f.sic, f.fye, cl["status"], flag_text(fl)])
    c["rows"]["firms.csv"] = firm_rows
    last_year = 2026 if s2_open(vintage) else 2025
    if not full:
        last_year = PRE_LAST_YEAR
    fy_rows = []
    for cik in order:
        for y in range(min(ALL_YEARS), last_year + 1):
            kind, d, acc_, fd = firms[cik].info(y)
            if kind == "one":
                fy_rows.append([cik, str(y), d, acc_, fd])
    c["rows"]["firm_years.csv"] = fy_rows
    comp_names = (("ca", "ca"), ("cl", "cl"), ("rev", "rev"), ("ni", "ni"), ("ar", "ar"), ("contract_cost", "contract_cost"))
    tag_rows = []
    main_windows = [w for w in cls if w != w2]
    for w in main_windows:
        for cik in order:
            st = cls[w][cik]["struct"]
            if not st:
                continue
            for comp, name in comp_names:
                tag_rows.append([w, cik, name, st[comp][0], "|".join(st[comp][1])])
    # --- panel.csv
    panel_rows = []
    for w in main_windows:
        for basis in (("own_10k", "latest_filed") if w == w1 else ("own_10k",)):
            for cik in order:
                cl = cls[w][cik]
                if cl["status"] != "in_scope":
                    continue
                f = firms[cik]
                wc = window_calc(f, w, cl["struct"], basis)
                if wc is None:
                    continue
                for y in wc["years"]:
                    ar = cell(f, AR_A1, y, basis)
                    cc = cell(f, CC_TAG, y, basis)
                    panel_rows.append([w, basis, cik, str(y), cl["info"][y][1], cl["struct"]["rev"][1][0], usd(wc["rev"][y]), usd(wc["ni"][y]), usd(wc["ca"][y]), usd(wc["cl"][y]), usd(wc["n"][y]),
                                       r6(wc["r"][y]), usd(ar[1]) if ar[0] == "exact" else "", usd(cc[1]) if cc[0] == "exact" else ""])
    # --- contributions.csv
    contrib = []
    sets = []
    if full:
        sets += [(w1, s, S1[s]) for s in SAMPLES_S1]
    sets += [(w, "primary", prec[w]) for w in pw]
    for w, s, recs in sets:
        for r in recs:
            contrib.append([w, s, r["cik"], r["ticker"], usd(r["aa_b"]), usd(r["aa_e"]), usd(r["t"]), usd(r["dni"]), usd(r["rev_e"]), flag_text(r["flags"])])
    c["sets"] = sets
    # --- the S2 sample, when scored
    s2recs = None
    if phase == "score":
        s2recs = [r for r in build_primary(firms, order, cls[w2], w2, acc=c["acc"]) if r["cik"] in s2scored]
        sets.append((w2, "s2_eligible", s2recs))
        for r in s2recs:
            contrib.append([w2, "s2_eligible", r["cik"], r["ticker"], usd(r["aa_b"]), usd(r["aa_e"]), usd(r["t"]), usd(r["dni"]), usd(r["rev_e"]), flag_text(r["flags"])])
            cl, f, wc = cls[w2][r["cik"]], firms[r["cik"]], r["wc"]
            for y in wc["years"]:
                ar = cell(f, AR_A1, y, "own_10k")
                cc = cell(f, CC_TAG, y, "own_10k")
                panel_rows.append([w2, "own_10k", r["cik"], str(y), cl["info"][y][1], cl["struct"]["rev"][1][0], usd(wc["rev"][y]), usd(wc["ni"][y]), usd(wc["ca"][y]), usd(wc["cl"][y]),
                                   usd(wc["n"][y]), r6(wc["r"][y]), usd(ar[1]) if ar[0] == "exact" else "", usd(cc[1]) if cc[0] == "exact" else ""])
        for cik in sorted(s2scored, key=order.index):
            st = cls[w2][cik]["struct"]
            for comp, name in comp_names:
                tag_rows.append([w2, cik, name, st[comp][0], "|".join(st[comp][1])])
    c["rows"]["panel.csv"] = panel_rows
    c["rows"]["firm_tags.csv"] = tag_rows
    c["rows"]["contributions.csv"] = contrib
    c["s2recs"] = s2recs
    c["placebo_out"] = prow_out
    # --- coverage.csv
    inscope = {cik for cik in order if cls[status_w][cik]["status"] == "in_scope"}
    cov = []
    for tag, period in inp["plan"]:
        st = inp["frame_status"][(tag, period)]
        ciks = set(inp["frames"].get((tag, period), {}))
        cov.append([tag, period, FRAME_ROLE[tag], str(len(ciks & set(order))) if st == "200" else "0", str(len(ciks & inscope)) if st == "200" else "0"])
    c["rows"]["coverage.csv"] = cov
    c["inscope"] = inscope
    if not full:
        return c
    # ---------------------------------------------------------------- full stage only
    prim = S1["primary"]
    rec_rows, t_ar = receivables_table(firms, prim, w1)
    stats = collections.OrderedDict((s, calc_stats(S1[s])) for s in S1)
    if M("g18_tar_in_t"):
        stats["primary"]["t"] = stats["primary"]["t"] + t_ar                 # the mutant adds the receivables T to T (G18)
    nb2 = nb_for("S1", band)
    nb1 = band["nb1"]
    sc = {s: score_stat(stats[s], nb2) for s in S1}
    scg = {s: score_stat(stats[s], nb_for("S1P", band), gross=True) for s in S1}
    c["stats"], c["sc"], c["scg"] = stats, sc, scg
    H = []
    for s in SAMPLES_S1:
        H += sample_headline(vintage, w1, s, stats[s], sc[s], scg[s])
    sf_fb = c["extras"]["samefiling_fallback"]
    H.append(hl(vintage, w1, "sens_samefiling", "n_samefiling_fallback", str(len(sf_fb)), "count", len(S1["sens_samefiling"])))
    c["sf_fallback"] = sf_fb
    sf_rs = c["extras"]["samefiling_restated"]
    c["sf_restated"] = sf_rs
    H.append(hl(vintage, w1, "sens_samefiling", "n_samefiling_restated", str(len(sf_rs)), "count", len(S1["sens_samefiling"])))
    fr_s1, fr_n_s1p = fragility(prim, nb2, nb_for("S1P", band))
    c["fragile_s1"], c["fragile_s1p_n"] = fr_s1, fr_n_s1p
    H.append(hl(vintage, w1, "primary", "n_leave1_s1_below_10", str(len(fr_s1)), "count", len(prim)))
    H.append(hl(vintage, w1, "primary", "n_leave1_s1p_below_25", str(fr_n_s1p), "count", len(prim)))
    for r_, sh_ in fr_s1:
        H.append(hl(vintage, w1, "primary", "leave1_s1_share_pct_" + re.sub(r"[^A-Za-z0-9]+", "_", r_["ticker"]), pct3(sh_), "pct", len(prim) - 1))
    differ = [smp for smp in SAMPLES_S1 if (sc[smp]["label"], scg[smp]["label"]) != (sc["primary"]["label"], scg["primary"]["label"])]
    c["label_differs"] = differ
    H.append(hl(vintage, w1, "primary", "n_samples_label_differs", str(len(differ)), "count", len(SAMPLES_S1)))
    # populations and weights
    cnt = collections.Counter(cls[w1][cik]["status"] for cik in order)
    for stt in STATUS_ORDER:
        H.append(hl(vintage, w1, "primary", "n_status_" + stt, str(cnt.get(stt, 0)), "count", cnt.get(stt, 0)))
    ni25 = {}
    for cik in order:
        st_, v, _ = cell(firms[cik], NI_TAG, 2025, "own_10k")
        if st_ == "exact":
            ni25[cik] = q0(v)
    prim_ni25 = dsum([q0(r["wc"]["ni"][2025]) for r in prim])
    all_ni25 = dsum(list(ni25.values()))
    H.append(hl(vintage, w1, "primary", "ni_2025_primary_usd", usd(prim_ni25), "usd", len(prim)))
    H.append(hl(vintage, w1, "primary", "ni_2025_all500_usd", usd(all_ni25), "usd", len(ni25)))
    H.append(hl(vintage, w1, "primary", "ni_2025_all500_missing", str(len(order) - len(ni25)), "count", len(order) - len(ni25)))
    miss_fin = sum(1 for cik in order if cik not in ni25 and cls[w1][cik]["status"] == "financial_sic")
    H.append(hl(vintage, w1, "primary", "ni_2025_missing_financial", str(miss_fin), "count", miss_fin))
    H.append(hl(vintage, w1, "primary", "ni_2025_missing_other", str(len(order) - len(ni25) - miss_fin), "count", len(order) - len(ni25) - miss_fin))
    H.append(hl(vintage, w1, "primary", "earnings_weight_pct", pct3(prim_ni25 / all_ni25 * 100 if all_ni25 != 0 else None), "pct", len(prim)))
    # concentration
    p5, n5 = top5_shares(prim)
    H.append(hl(vintage, w1, "primary", "top5_share_t_pos_pct", pct3(p5), "pct", len(prim)))
    H.append(hl(vintage, w1, "primary", "top5_share_t_neg_pct", pct3(n5), "pct", len(prim)))
    H.append(hl(vintage, w1, "primary", "top5_share_cl_fy2025_pct", pct3(cl_top5_share(prim, 2025)), "pct", len(prim)))
    # the placebo band, beside S1
    for name, key, unit in (("nb1_pct_rev", "nb1", "pct"), ("nb2_pct_rev", "nb2", "pct"), ("placebo_median_1y_pct_rev", "med1", "pct"), ("placebo_median_2y_pct_rev", "med2", "pct")):
        v = band[key]
        H.append(hl(vintage, w1, "primary", name, pct3(v * 100) if v is not None else "", unit))
    for w in pw:
        rs = calc_stats(prec[w])
        scw = score_stat(rs, None)
        H.append(hl(vintage, w, "primary", "t_usd", usd(rs["t"]), "usd", rs["n"]))
        H.append(hl(vintage, w, "primary", "t_pct_rev", pct3(scw["t_pct_rev"]), "pct", rs["n"]))
    # cash-flow sign convention, receivables, contract costs, remaining performance obligations, the cross-check
    for comp in ("ca", "cl", "ar"):
        sg, same, opp = signs[comp]
        H.append(hl(vintage, "fy2020_fy2022", "primary", "cf_sign_" + comp, "" if sg is None else str(sg), "ratio"))
        H.append(hl(vintage, "fy2020_fy2022", "primary", "cf_sign_%s_firm_years_same" % comp, str(same), "count", same))
        H.append(hl(vintage, "fy2020_fy2022", "primary", "cf_sign_%s_firm_years_opposite" % comp, str(opp), "count", opp))
    c["rows"]["receivables.csv"] = rec_rows
    n_cc, cc_tot, cc_rev, cc_n = descriptive_levels(firms, prim, w1, CC_TAG)
    for y in window_years(w1):
        if cc_rev[y] != 0:
            H.append(hl(vintage, w1, "primary", "contract_cost_days_fy%d" % y, days3(cc_tot[y] / cc_rev[y] * DAYS_YEAR), "days", n_cc))
            H.append(hl(vintage, w1, "primary", "n_days_same_firms_fy%d" % y, days3(cc_n[y] / cc_rev[y] * DAYS_YEAR), "days", n_cc))
    n_rpo, rpo_tot, rpo_rev, _ = descriptive_levels(firms, prim, w1, RPO_TAG)
    for y in window_years(w1):
        H.append(hl(vintage, w1, "primary", "rpo_usd_fy%d" % y, usd(rpo_tot[y]), "usd", n_rpo))
        if rpo_rev[y] != 0:
            H.append(hl(vintage, w1, "primary", "rpo_days_fy%d" % y, days3(rpo_tot[y] / rpo_rev[y] * DAYS_YEAR), "days", n_rpo))
    n_cf, tcf, tbs, rev_cf = c["cf"] = cf_cross_check(firms, prim, w1, signs)
    H.append(hl(vintage, w1, "primary", "t_cashflow_usd", usd(tcf) if n_cf else "", "usd", n_cf))
    H.append(hl(vintage, w1, "primary", "t_balance_same_firms_usd", usd(tbs) if n_cf else "", "usd", n_cf))
    H.append(hl(vintage, w1, "primary", "t_cashflow_days_rev", days3(tcf / rev_cf * DAYS_YEAR) if n_cf and rev_cf != 0 else "", "days", n_cf))
    # S2: the eligible set and its coverage; scored only from the S2 date on
    cov_pct = thin_share(len(have26), len(elig25))
    H.append(hl(vintage, w2, "s2_eligible", "n_eligible_fy2025", str(len(elig25)), "count", len(elig25)))
    H.append(hl(vintage, w2, "s2_eligible", "n_with_fy2026_10k", str(len(have26)), "count", len(have26)))
    H.append(hl(vintage, w2, "s2_eligible", "n_s2_end_mismatch", str(len(cov26["outside_window"])), "count", len(cov26["outside_window"])))
    H.append(hl(vintage, w2, "s2_eligible", "n_s2_fy_ambiguous", str(len(cov26["ambiguous"])), "count", len(cov26["ambiguous"])))
    H.append(hl(vintage, w2, "s2_eligible", "n_s2_no_fy2026_10k", str(len(cov26["none"])), "count", len(cov26["none"])))
    H.append(hl(vintage, w2, "s2_eligible", "coverage_pct", pct3(cov_pct), "pct", len(elig25)))
    if phase == "score":
        st2 = calc_stats(s2recs)
        sc2 = score_stat(st2, nb1)
        scg2 = score_stat(st2, nb1, gross=True)
        H += sample_headline(vintage, w2, "s2_eligible", st2, sc2, scg2)
        reg_s2 = [reg_row("S2", w2, "s2_eligible", vintage, st2["n"], st2["t"], st2, sc2, nb1), reg_row("S2P", w2, "s2_eligible", vintage, st2["n"], st2["tp"], st2, scg2, nb1)]
    elif phase == "VOID":
        reg_s2 = [pending_row("S2", w2, "s2_eligible", vintage, "VOID", len(elig25), "thin_coverage"), pending_row("S2P", w2, "s2_eligible", vintage, "VOID", len(elig25), "thin_coverage")]
    elif phase == "PENDING_THIN":
        reg_s2 = [pending_row("S2", w2, "s2_eligible", vintage, "PENDING_THIN", len(elig25)), pending_row("S2P", w2, "s2_eligible", vintage, "PENDING_THIN", len(elig25))]
    else:
        reg_s2 = [pending_row("S2", w2, "s2_eligible", vintage, "PENDING"), pending_row("S2P", w2, "s2_eligible", vintage, "PENDING")]
    # registered.csv: S1 and S1P stay as first scored; S2 and S2P stay once scored
    if frozen:
        reg_s1 = [r for r in reg_old if r[0] in ("S1", "S1P")]
    else:
        reg_s1 = [reg_row("S1", w1, "primary", vintage, stats["primary"]["n"], stats["primary"]["t"], stats["primary"], sc["primary"], nb2),
                  reg_row("S1P", w1, "primary", vintage, stats["primary"]["n"], stats["primary"]["tp"], stats["primary"], scg["primary"], nb_for("S1P", band))]
    s2_old = [r for r in reg_old if r[0] in ("S2", "S2P")]
    s2_final = any(r[15] not in ("PENDING", "PENDING_THIN") for r in s2_old if r[3] != vintage)
    keep = [r for r in s2_old if r[3] != vintage]
    reg = reg_s1 + keep + ([] if s2_final else reg_s2)
    reg.sort(key=lambda r: (["S1", "S1P", "S2", "S2P"].index(r[0]), r[3]))
    c["rows"]["registered.csv"] = reg
    c["s2_final"] = s2_final
    # contributors.csv
    cr = []
    pos, neg = contributors(prim)
    for side, lst in (("positive", pos), ("negative", neg)):
        for rank, r, sh in lst:
            cr.append([w1, side, str(rank), r["cik"], r["ticker"], r["name"], usd(r["t"]), pct3(sh), "" if M("g9_flags_missing") else flag_text(r["flags"])])
    c["rows"]["contributors.csv"] = cr
    c["contributors"] = (pos, neg)
    # headline.csv: earlier vintages stay; this vintage's rows are these
    old_h = [r for r in ex.get("headline", []) if r[0] != vintage]
    allh = old_h + H
    allh.sort(key=lambda r: r[0])                                   # stable: by vintage, then the order the rows were made
    c["rows"]["headline.csv"] = allh
    c["H"] = H
    c["rows"]["revisions.csv"] = revision_rows(allh)
    c["t_ar"] = t_ar
    return c


def revision_rows(headline):
    """revisions.csv, regenerated from headline.csv every time (never appended): for each pair of adjacent vintages, every statistic whose value differs."""
    by = collections.OrderedDict()
    for r in headline:
        by.setdefault(r[0], collections.OrderedDict())[(r[1], r[2], r[3])] = r[4]
    vs = sorted(by)
    out = []
    for a, b in zip(vs, vs[1:]):
        for k in by[b]:
            if k in by[a] and by[a][k] != by[b][k]:
                out.append([a, b, k[0], k[1], k[2], by[a][k], by[b][k]])
    if M("g16_revisions_append"):
        out = [[a, b, k[0], k[1], k[2], by[a][k], by[b][k]] for a, b in zip(vs, vs[1:]) for k in by[b] if k in by[a]]
    return out


# ------------------------------------------------------------------------------------------------------------------------
# pinned and structural checks (section 8)
# ------------------------------------------------------------------------------------------------------------------------
def chk(cid, desc, expected, observed, status):
    return [cid, desc, expected, observed, status]


CHECK_ORDER = ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14"]
PRE_CHECKS = ("C01", "C03", "C04", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14")

# 2.5: the count of the 500 with a fact in the frame, at CY2023Q4I and CY2025Q4I (None: not fetched on 28 Oct)
PINS_Q4I = collections.OrderedDict([(CL_T, (183, 176)), (CL_C, (217, 218)), (CL_N, (130, 131)), (CA_T, (83, 82)), (CA_C, (67, 67)), (CA_N, (31, 31)), (DEF_C, (42, 42)),
                                    (AR_A1, (311, 317)), (AR_A2, (18, 17)), (AR_A3, (70, 74)), (RPO_TAG, (132, 134)), (UNB_TAG, (32, None))])
PIN_TOL = 5
# 2.4: the fiscal-2019 presence and identity counts of the 500 (None: not stated)
PINS_STRUCT = collections.OrderedDict([
    ("liability: total, current and noncurrent all tagged", 59), ("liability, all three: total = current + noncurrent", 45), ("liability, all three: total = current", 1), ("liability, all three: neither", 13),
    ("liability: total and current without noncurrent", 36), ("liability, total and current: equal", 14), ("liability, total and current: total larger", 13), ("liability, total and current: total smaller", 9),
    ("liability: total only", 81), ("liability: current only", 51), ("liability: current and noncurrent", 49),
    ("asset: total, current and noncurrent all tagged", 9), ("asset, all three: total = parts", 8),
    ("asset: total and current without noncurrent", 7), ("asset, total and current: equal", 3), ("asset, total and current: total larger", 3), ("asset, total and current: total smaller", 1),
    ("asset: total only", 61), ("asset: current only", 28), ("asset: current and noncurrent", 13),
    ("revenue: Revenues and R2 both tagged", 104), ("revenue: equal", 49), ("revenue: Revenues larger", 50), ("revenue: Revenues smaller", 5)])
PINS_NI_CY2019 = (("0000789019", "2018-07-01", "2019-06-30"), ("0001341439", "2019-06-01", "2020-05-31"), ("0000320187", "2019-06-01", "2020-05-31"))     # Microsoft, Oracle, Nike
MSFT = "0000789019"


def fvals(inp, tag, period):
    d = inp["frames"].get((tag, period), {})
    return {k: v[0][3] for k, v in d.items() if k in inp["panel"]["tickers"]}


def near_eq(a, b):
    """Equal within 0.5% (the 2.4 identity comparisons)."""
    return a == b or abs(a - b) <= Decimal("0.005") * max(abs(a), abs(b))


def struct_counts(inp):
    out = collections.OrderedDict()
    P = "CY2019Q4I"
    for nm, (T, C, N) in (("liability", (CL_T, CL_C, CL_N)), ("asset", (CA_T, CA_C, CA_N))):
        t, cu, no = fvals(inp, T, P), fvals(inp, C, P), fvals(inp, N, P)
        keys = set(t) | set(cu) | set(no)
        a3 = [k for k in keys if k in t and k in cu and k in no]
        s_sum = sum(1 for k in a3 if near_eq(t[k], cu[k] + no[k]))
        s_cur = sum(1 for k in a3 if not near_eq(t[k], cu[k] + no[k]) and near_eq(t[k], cu[k]))
        out["%s: total, current and noncurrent all tagged" % nm] = len(a3)
        out["%s, all three: total = %s" % (nm, "current + noncurrent" if nm == "liability" else "parts")] = s_sum
        if nm == "liability":
            out["liability, all three: total = current"] = s_cur
            out["liability, all three: neither"] = len(a3) - s_sum - s_cur
        tc = [k for k in keys if k in t and k in cu and k not in no]
        out["%s: total and current without noncurrent" % nm] = len(tc)
        out["%s, total and current: equal" % nm] = sum(1 for k in tc if near_eq(t[k], cu[k]))
        out["%s, total and current: total larger" % nm] = sum(1 for k in tc if not near_eq(t[k], cu[k]) and t[k] > cu[k])
        out["%s, total and current: total smaller" % nm] = sum(1 for k in tc if not near_eq(t[k], cu[k]) and t[k] < cu[k])
        out["%s: total only" % nm] = sum(1 for k in keys if k in t and k not in cu and k not in no)
        out["%s: current only" % nm] = sum(1 for k in keys if k in cu and k not in t and k not in no)
        out["%s: current and noncurrent" % nm] = sum(1 for k in keys if k in cu and k in no and k not in t)
    rv, r2 = fvals(inp, REV_ANY, "CY2019"), fvals(inp, REV_R2, "CY2019")
    both = [k for k in rv if k in r2]
    out["revenue: Revenues and R2 both tagged"] = len(both)
    out["revenue: equal"] = sum(1 for k in both if near_eq(rv[k], r2[k]))
    out["revenue: Revenues larger"] = sum(1 for k in both if not near_eq(rv[k], r2[k]) and rv[k] > r2[k])
    out["revenue: Revenues smaller"] = sum(1 for k in both if not near_eq(rv[k], r2[k]) and rv[k] < r2[k])
    return out


def c01(c):
    inp = c["inp"]
    p, pin = inp["panel"], inp["pin"]
    shared_ok = all(sorted(p["tickers"].get(k, [])) == sorted(v) for k, v in pin["shared"].items())
    ok = p["sha"] == pin["sha256"] and p["bytes"] == pin["bytes"] and p["rows"] == pin["rows"] and len(p["order"]) == pin["ciks"] and shared_ok
    return chk("C01", "Frozen population: the panel file is the one pinned in 4.7 (R5)", "sha256 %s, %s bytes, %d rows, %d distinct cik10, three shared CIKs" % (pin["sha256"], "{:,}".format(pin["bytes"]), pin["rows"], pin["ciks"]),
               "sha256 %s, %s bytes, %d rows, %d distinct cik10, shared CIKs %s" % (p["sha"], "{:,}".format(p["bytes"]), p["rows"], len(p["order"]), "as pinned" if shared_ok else "differ"), "PASS" if ok else "FAIL")


def c02(c):
    inp = c["inp"]
    cov = {(r[0], r[1]): int(r[3]) for r in c["rows"]["coverage.csv"]}
    first = min([r["vintage"] for r in inp["vint_all"]] or [c["vintage"]]) == c["vintage"]
    bad, n = [], 0
    for tag, pins in PINS_Q4I.items():
        for per, pinv in zip(("CY2023Q4I", "CY2025Q4I"), pins):
            if pinv is None or (tag, per) not in cov:
                continue
            n += 1
            if abs(cov[(tag, per)] - pinv) > PIN_TOL:
                bad.append("%s %s: %d against %d" % (tag, per, cov[(tag, per)], pinv))
    st = "PASS" if not bad else "WARN"
    if not first:
        st = "INFO"
    return chk("C02", "Coverage pins: the 500 CIKs with a fact in the CY2023Q4I and CY2025Q4I frames (first vintage only)", "each count within %d of 2.5's count" % PIN_TOL,
               ("%d of %d counts within %d" % (n - len(bad), n, PIN_TOL)) + ("; " + "; ".join(bad[:6]) if bad else "") + ("" if first else "; not a first vintage, reported only"), st)


def c03(c):
    cnt = struct_counts(c["inp"])
    diff = ["%s: %d against %d" % (k, cnt[k], v) for k, v in PINS_STRUCT.items() if cnt[k] != v]
    return chk("C03", "Structure pins: fiscal-2019 presence and identity counts of 2.4, re-derived from the CY2019Q4I and CY2019 frames", "all %d counts as in 2.4" % len(PINS_STRUCT),
               "%d of %d reproduced" % (len(PINS_STRUCT) - len(diff), len(PINS_STRUCT)) + ("; " + "; ".join(diff[:5]) if diff else ""), "PASS" if not diff else "WARN")


def c04(c):
    d = c["inp"]["frames"].get((NI_TAG, "CY2019"), {})
    bad = []
    for cik, s, e in PINS_NI_CY2019:
        got = d.get(cik)
        if not got or (got[0][1], got[0][2]) != (s, e):
            bad.append("%s %s" % (cik, "absent" if not got else "%s to %s" % (got[0][1], got[0][2])))
    return chk("C04", "Alignment pins: NetIncomeLoss/CY2019 holds Microsoft's year to 2019-06-30 and Oracle's and Nike's to 2020-05-31", "3 of 3 dates as in 2.3", "%d of 3" % (3 - len(bad)) + ("; " + "; ".join(bad) if bad else ""),
               "PASS" if not bad else "WARN")


def c05(c):
    f = c["firms"].get(MSFT)
    want = ("2023-06-30", "2025-06-30", "2026-07-29")
    if f is None:
        return chk("C05", "Microsoft: D_2023, D_2025, the FY2026 10-K and S2 eligibility", "2023-06-30, 2025-06-30, filed 2026-07-29, not S2-eligible", "not in the panel", "FAIL")
    got = (f.info(2023)[1], f.info(2025)[1], f.info(2026)[3])
    ok = got == want and not fye_ok(f.fye)
    return chk("C05", "Microsoft: D_2023, D_2025, the FY2026 10-K and S2 eligibility", "D_2023 %s, D_2025 %s, FY2026 10-K filed %s, not S2-eligible" % want,
               "D_2023 %s, D_2025 %s, FY2026 10-K filed %s, fiscalYearEnd %s" % (got[0], got[1], got[2], f.fye or "blank"), "PASS" if ok else "FAIL")


def c06(c):
    inp = c["inp"]
    keys = (AR_A1, CL_C, REV_R2, NI_TAG)
    bad = [(t, p, inp["frame_status"][(t, p)]) for (t, p) in inp["plan"] if t in keys and inp["frame_status"][(t, p)] != "200"]
    return chk("C06", "Content: the frames for A1, ContractWithCustomerLiabilityCurrent, R2 and NetIncomeLoss returned 200 at every fetched period; every fact used is USD and numeric",
               "200 at every period; no non-numeric value", "%d of %d returned 200; every value read was numeric" % (sum(1 for (t, p) in inp["plan"] if t in keys) - len(bad), sum(1 for (t, p) in inp["plan"] if t in keys)) +
               ("; " + "; ".join("%s %s %s" % b for b in bad[:4]) if bad else ""), "PASS" if not bad else "FAIL")


def registered_closure_problems(reg, head):
    """registered.csv is the scored record, so it must close against the build: for every statement row that carries numbers, n_firms, t_usd, dni_usd, ni_base_usd and numerator_usd (t_usd for S1 and
    S2, t_pos_usd for S1P and S2P) equal the headline.csv values of the same vintage, window and sample, and share_pct recomputes from them to three decimals. reg and head are lists of rows of strings."""
    if M("g10_registered_unclosed"):
        return []
    hm = {(r[0], r[1], r[2], r[3]): r[4] for r in head}
    out = []
    for r in reg:
        if len(r) < 10 or r[6] == "":
            continue                                            # PENDING, PENDING_THIN and a thin VOID carry no number
        sid, w, smp, v = r[0], r[1], r[2], r[3]
        num_stat = "t_pos_usd" if sid.endswith("P") else "t_usd"
        pairs = (("n_firms", r[4], "n_firms"), ("numerator_usd", r[5], num_stat), ("t_usd", r[6], "t_usd"), ("dni_usd", r[7], "dni_usd"), ("ni_base_usd", r[8], "ni_base_usd"))
        bad = [name for name, cell_, stat_ in pairs if _dec(hm.get((v, w, smp, stat_), "")) is None or _dec(cell_) != _dec(hm.get((v, w, smp, stat_), ""))]
        if bad:
            out.append("registered.csv %s (vintage %s): %s differ from the headline.csv values" % (sid, v, ", ".join(bad)))
        num, dni = _dec(r[5]), _dec(r[7])
        if r[9] == "":
            if r[15] != "VOID":
                out.append("registered.csv %s (vintage %s): share_pct is blank on a row labelled %s" % (sid, v, r[15]))
        elif num is None or dni is None or dni == 0 or fdec(num / dni * 100, 3) != r[9]:
            out.append("registered.csv %s (vintage %s): share_pct %s does not recompute from numerator_usd and dni_usd" % (sid, v, r[9]))
    return out


def c07(c):
    rows = c["rows"]
    bad = []
    for r in rows["panel.csv"]:
        ca, cl_, n = to_dec(r[8]), to_dec(r[9]), to_dec(r[10])
        if None not in (ca, cl_, n) and abs(n - (ca - cl_)) > 1:
            bad.append("panel %s %s %s %s: N differs from CA - CL" % (r[0], r[1], r[2], r[3]))
    sums = collections.OrderedDict()
    for r in rows["contributions.csv"]:
        s = sums.setdefault((r[0], r[1]), [Decimal(0), Decimal(0), Decimal(0)])
        t = to_dec(r[6])
        s[0] += t
        s[1] += max(t, 0)
        s[2] += to_dec(r[7])
    head = {}
    if "headline.csv" in rows:
        for r in rows["headline.csv"]:
            if r[0] == c["vintage"]:
                head[(r[1], r[2], r[3])] = r[4]
    pl = {r[0]: r for r in c["placebo_now"]}
    for (w, s), (t, tp, dni) in sums.items():
        if w in PLACEBO_WINDOWS and s == "primary" and w in pl:
            want = (to_dec(pl[w][4]), to_dec(pl[w][5]), to_dec(pl[w][8]))
        else:
            want = tuple(to_dec(head.get((w, s, k), "")) for k in ("t_usd", "t_pos_usd", "dni_usd"))
        for nm, got, exp in zip(("T", "T_pos", "dNI"), (t, tp, dni), want):
            if exp is None or abs(got - exp) > 1:
                bad.append("%s %s: sum of contributions %s %s against %s" % (w, s, nm, usd(got), usd(exp) if exp is not None else "no headline row"))
    n = len(sums)
    closure = registered_closure_problems(rows["registered.csv"], rows["headline.csv"]) if "registered.csv" in rows and "headline.csv" in rows else []
    n_reg = len([r for r in rows.get("registered.csv", []) if r[6] != ""])
    bad += closure
    return chk("C07", "Tamper: per panel row N = CA - CL; per window and sample the sum of contributions equals T, T_pos and dNI; registered.csv's scored rows close against headline.csv (counts, sums, share)",
               "every difference within 1 USD; every registered cell equal to its headline value",
               "%d panel rows and %d window-sample sets checked; %d registered row(s) checked against headline.csv; %d difference(s)" % (len(rows["panel.csv"]), n, n_reg, len(bad)) + ("; " + "; ".join(bad[:3]) if bad else ""),
               "PASS" if not bad else "FAIL")


def c08(c):
    bad = 0
    for cik, comp, y, accn in c["acc"]:
        if c["firms"][cik].info(y)[2] != accn:
            bad += 1
    return chk("C08", "Same filing: every own_10k value comes from the fact whose accn is that firm-year's original 10-K accession (R1-8)", "0 values from another accession",
               "%d values checked; %d from another accession" % (len(c["acc"]), bad), "PASS" if bad == 0 and c["acc"] else ("FAIL" if bad else "INFO"))


def c09(c):
    inp = c["inp"]
    fy = {(r[0], int(r[1])): r for r in c["rows"]["firm_years.csv"]}
    bad, n = [], 0
    for w, cl in c["cls"].items():
        for cik, k in cl.items():
            if k["status"] != "in_scope":
                continue
            for y in k["years"]:
                n += 1
                r = fy.get((cik, y))
                f10 = [x for x in c["firms"][cik].filings if x[0] == "10-K" and x[1] == (r[2] if r else None) and x[3] == (r[3] if r else None)]
                lo, hi = "%d-%s" % (y, FY_START), "%d-%s" % (y + 1, FY_END)
                if r is None or not f10 or not (lo <= r[2] <= hi):
                    bad.append("%s %s FY%d" % (w, cik, y))
    return chk("C09", "Fiscal years: every in-scope firm's D_Y comes from a form-10-K reportDate inside its window (P3)", "0 firm-years without a 10-K inside [Y-04-01, (Y+1)-03-31]",
               "%d firm-years checked; %d outside" % (n, len(bad)) + ("; " + "; ".join(bad[:4]) if bad else ""), "PASS" if not bad else "FAIL")


def independent_cut(firm, stage, vintage):
    """The blind cut worked out a second way, from the filings alone (C10): the last end date a build of this stage and vintage may read for the firm."""
    def dy(y):
        lo, hi = "%d-%s" % (y, FY_START), "%d-%s" % (y + 1, FY_END)
        ds = sorted({x[3]: x[1] for x in firm.filings if x[0] == "10-K" and lo <= x[1] <= hi}.values())
        return ds[0] if len(ds) == 1 else None
    if stage == "pre":
        d = dy(PRE_LAST_YEAR)
        return add_days(d, NEAR_DAYS) if d else PRE_DATE_LIMIT
    if vint_date(vintage) >= S2_DATE:
        return None
    return dy(2025) or "2026-03-31"


def c10(c):
    inp = c["inp"]
    stage, vintage = c["stage"], c["vintage"]
    bad = []
    for cik, end in inp["read_log"]:
        cut = independent_cut(c["firms"][cik], stage, vintage)
        if cut is not None and end > cut:
            bad.append("%s %s" % (cik, end))
    frames_bad = [k for k in inp["frames"] if (frame_year(k[1]) >= 2026 and vint_date(vintage) < S2_DATE) or (stage == "pre" and frame_year(k[1]) > 2019)]
    urls_bad = [r["url_path"] for r in inp["vint"] if (FRAME_RX.match(r["url_path"]) and int(FRAME_RX.match(r["url_path"]).group(3)) >= 2026 and vint_date(vintage) < S2_DATE)]
    beyond = inp["cf_skipped"] if stage == "full" and vint_date(vintage) < S2_DATE else 0
    ok = not bad and not frames_bad and not urls_bad and beyond == 0
    return chk("C10", "Blind order: the code read no FY2023-or-later value in --stage pre, and before 2027-05-01 no CY2026 frame and no fact with end after D_2025 (R1-10, R1-19)",
               "0 values read beyond the cut, 0 rows beyond it in the extract, 0 later frames",
               "%d fact values read, %d beyond the cut; %d extract rows beyond it; %d frames or requests for 2026 or later" % (len(inp["read_log"]), len(bad), beyond, len(frames_bad) + len(urls_bad)) +
               ("; " + "; ".join(bad[:3]) if bad else ""), "PASS" if ok else "FAIL")


def c11(c):
    reg_ok = True
    if "registered.csv" in c["rows"]:
        reg_ok = all(r[17] == SPEC_PREREG_SHA256 and r[18] == SPEC_POP_SHA256 for r in c["rows"]["registered.csv"])
    pre, pop, al = prereg_ok(), pop_ok(), allow_hash_ok()
    ok = pre and pop and al and reg_ok
    return chk("C11", "Hashes: the constants reproduce the canonical texts of 4.6, 4.7 and 5; registered.csv carries the 4.6 and 4.7 hashes", "%s / %s / %s" % (SPEC_PREREG_SHA256[:12], SPEC_POP_SHA256[:12], SPEC_ALLOW_SHA256[:12]),
               "4.6 %s, 4.7 %s, 5 %s, registered.csv hash columns %s" % ("reproduced" if pre else "DIFFERS", "reproduced" if pop else "DIFFERS", "reproduced" if al else "DIFFERS", "as pinned" if reg_ok else "DIFFER"),
               "PASS" if ok else "FAIL")


def c12(c, t1, t2):
    same = {n: sha256_of(x.encode("utf-8")) for n, x in t1.items()} == {n: sha256_of(x.encode("utf-8")) for n, x in t2.items()}
    return chk("C12", "Fixed output: a second build from the same inputs leaves every output sha256 unchanged", "every output identical", "%d outputs compared; %s" % (len(t1), "identical" if same else "DIFFER"),
               "PASS" if same else "FAIL")


def c13(c):
    inp = c["inp"]
    bad, n = [], 0
    for r in inp["vint"]:
        if r["status"] != "200":
            continue
        n += 1
        rn = raw_name(r["url_path"])
        p = os.path.join(inp["raw_dir"], rn) if rn else None
        if not p or not os.path.isfile(p):
            bad.append("%s absent" % (rn or r["url_path"]))
            continue
        b = read_file(p, "rb")
        if sha256_of(b) != r["sha256"] or str(len(b)) != r["bytes"]:
            bad.append("%s differs" % rn)
    return chk("C13", "Cache integrity: each raw body's sha256 and size equal its vintages.csv row", "every body present and equal", "%d bodies checked; %d absent or different" % (n, len(bad)) +
               ("; " + "; ".join(bad[:3]) if bad else ""), "PASS" if not bad and n else "FAIL")


def c14(c):
    inp = c["inp"]
    cl = c["cls"]["fy2020_fy2022"]
    pick = [cik for cik in c["order"] if cl[cik]["status"] == "in_scope" and c["firms"][cik].fye == "1231"][:15]
    n, bad = 0, []
    for cik in pick:
        f = c["firms"][cik]
        for tag, per in ((AR_A1, "CY2019Q4I"), (CL_C, "CY2019Q4I"), (REV_R2, "CY2019"), (NI_TAG, "CY2019")):
            fr = inp["frames"].get((tag, per), {}).get(cik)
            if not fr:
                continue
            _, fs, fe, fv = fr[0]
            cands = [x for x in f.facts.get(tag, []) if x[1] == fe and (not (tag in DURATION_TAGS) or x[0] == fs)]
            if not cands:
                continue
            latest = _latest(cands)
            n += 1
            if abs(latest[0][2] - fv) > 1:
                bad.append("%s %s" % (cik, tag))
    return chk("C14", "Frames against companyfacts: for the first 15 in-scope December year-end CIKs the latest-filed companyfacts value equals the frame value (A1, ContractWithCustomerLiabilityCurrent, R2, NetIncomeLoss at CY2019Q4I and CY2019)",
               "every pair within 1 USD", "%d firms, %d pairs compared; %d differ" % (len(pick), n, len(bad)) + ("; " + "; ".join(bad[:3]) if bad else ""), "PASS" if not bad and n else ("FAIL" if bad else "WARN"))


def build_checks(c, t1, t2):
    fns = {"C01": c01, "C02": c02, "C03": c03, "C04": c04, "C05": c05, "C06": c06, "C07": c07, "C08": c08, "C09": c09, "C10": c10, "C11": c11, "C13": c13, "C14": c14}
    out = []
    for cid in CHECK_ORDER:
        if c["stage"] == "pre" and cid not in PRE_CHECKS:
            continue
        out.append(c12(c, t1, t2) if cid == "C12" else fns[cid](c))
    return out


# ------------------------------------------------------------------------------------------------------------------------
# folder guards (sections 5 and 6; G12, G13, G17): the second look at what is about to be committed
# ------------------------------------------------------------------------------------------------------------------------
COLUMN_RULES = {
    "firms.csv": {"status": "status_firm", "flags": "flags*"},
    "firm_tags.csv": {"window": "window", "component": "component", "structure": "structure"},
    "panel.csv": {"window": "window", "basis": "basis"},
    "contributions.csv": {"window": "window", "sample": "sample", "flags": "flags*"},
    "headline.csv": {"window": "window", "sample": "sample", "unit": "unit"},
    "registered.csv": {"statement_id": "statement_id", "window": "window", "sample": "sample", "qualifier": "qualifier", "direction": "direction", "label": "label", "void_reason": "void_reason"},
    "contributors.csv": {"window": "window", "side": "side", "flags": "flags*"},
    "placebo.csv": {"window": "window", "includes_fy2020": "includes_fy2020"},
    "receivables.csv": {"window": "window", "row_type": "row_type", "measure": "measure"},
    "coverage.csv": {"role": "role"},
    "checks.csv": {"status": "status_check"},
}


def leak_problems(files, full=True):
    """Section 6: only the seventeen committed names; no json, zip, html or STOP file; no local path; no at sign; not a byte of the contact string."""
    out = []
    for n in sorted(files):
        raw = files[n] if isinstance(files[n], bytes) else files[n].encode("utf-8")
        text = raw.decode("utf-8", errors="replace")
        low = n.lower()
        rawfile = low.endswith((".zip", ".html", ".htm", ".gz", ".pdf")) or raw[:2] == b"PK" or raw[:4] == b"%PDF" or n.upper().startswith("STOP")
        if low.endswith(".json") and not M("g17_json_ok"):
            rawfile = True
        if rawfile:
            out.append("raw or forbidden file in the committed folder: %s" % n)
            continue
        if n not in COMMITTED and n != ".DS_Store" and not M("g12_sixteenth_csv_ok"):
            out.append("file that is not one of the seventeen committed names: %s" % n)
        if not M("g17_path_ok") and any(p in text for p in ("/Users/", "/private/", "~/")):
            out.append("a local path in %s" % n)
        if not M("g17_at_ok") and "@" in text:
            out.append("an at sign in %s" % n)
        if has_secret(text):
            out.append("the contact string in %s" % n)
    if full:
        for n in sorted(set(COMMITTED) - set(files)):
            out.append("missing: %s" % n)
    return out


def header_problems(files):
    out = []
    for n in ALLOW_ORDER:
        if n in files:
            try:
                check_header(n, csv_body(files[n])[0])
            except DataError as e:
                out.append(str(e))
    return out


def dup_key_problems(files):
    out = []
    for n, ks in KEYS.items():
        if n not in files:
            continue
        h, rows = csv_body(files[n])
        if list(h) != ALLOW[n]:
            continue
        idx = [h.index(k) for k in ks]
        seen = set()
        for r in rows:
            k = tuple(r[i] for i in idx)
            if k in seen and not M("g12_dup_key_ok"):
                out.append("duplicate key in %s: %s" % (n, "|".join(k)))
            seen.add(k)
    return out


def value_problems(files):
    """Allowed values (section 5): every constrained column holds only its listed values."""
    out = []
    for n, rules in COLUMN_RULES.items():
        if n not in files:
            continue
        h, rows = csv_body(files[n])
        if list(h) != ALLOW[n]:
            continue
        for col, rule in rules.items():
            i = h.index(col)
            if rule.endswith("*"):
                allowed = ALLOWED_VALUES[rule[:-1]]
                bad = sorted({f for r in rows for f in r[i].split("|") if f and f not in allowed})
            else:
                allowed = ALLOWED_VALUES[rule]
                bad = sorted({r[i] for r in rows if r[i] not in allowed and r[i] != ""})
            if bad:
                out.append("%s: column %s holds %s" % (n, col, ", ".join(bad[:4])))
    return out


def _dec(s):
    try:
        return Decimal(s)
    except (decimal.InvalidOperation, TypeError):
        return None


def tamper_problems(files):
    """C07 on the committed text: per panel row N = CA - CL; per window and sample the sum of the contributions equals the headline T, T_pos and dNI (latest vintage in headline.csv) within 1 USD; and
    registered.csv closes against headline.csv (registered_closure_problems)."""
    out = []
    if "panel.csv" in files:
        h, rows = csv_body(files["panel.csv"])
        if list(h) == ALLOW["panel.csv"]:
            ix = {c: h.index(c) for c in h}
            for r in rows:
                ca, cl_, n = _dec(r[ix["ca_usd"]]), _dec(r[ix["cl_usd"]]), _dec(r[ix["n_usd"]])
                if None not in (ca, cl_, n) and abs(n - (ca - cl_)) > 1:
                    out.append("panel.csv %s %s %s %s: N is not CA - CL" % (r[ix["window"]], r[ix["basis"]], r[ix["cik10"]], r[ix["fiscal_year"]]))
    if "contributions.csv" in files and "headline.csv" in files:
        h, rows = csv_body(files["contributions.csv"])
        hh, hrows = csv_body(files["headline.csv"])
        if list(h) == ALLOW["contributions.csv"] and list(hh) == ALLOW["headline.csv"]:
            ix = {c: h.index(c) for c in h}
            jx = {c: hh.index(c) for c in hh}
            latest = max([r[jx["vintage"]] for r in hrows] or [""])
            head = {(r[jx["window"]], r[jx["sample"]], r[jx["statistic"]]): _dec(r[jx["value"]]) for r in hrows if r[jx["vintage"]] == latest}
            sums = collections.OrderedDict()
            for r in rows:
                s = sums.setdefault((r[ix["window"]], r[ix["sample"]]), [Decimal(0), Decimal(0), Decimal(0)])
                t = _dec(r[ix["t_usd"]])
                if t is None:
                    continue
                s[0] += t
                s[1] += max(t, 0)
                s[2] += _dec(r[ix["dni_usd"]]) or 0
            for (w, s), got in sums.items():
                for nm, g, key in zip(("T", "T_pos", "dNI"), got, ("t_usd", "t_pos_usd", "dni_usd")):
                    exp = head.get((w, s, key))
                    if exp is not None and abs(g - exp) > 1:
                        out.append("%s %s: the contributions sum to %s %s, the headline says %s" % (w, s, nm, usd(g), usd(exp)))
    if "registered.csv" in files and "headline.csv" in files:
        rh, rrows = csv_body(files["registered.csv"])
        hh, hrows = csv_body(files["headline.csv"])
        if list(rh) == ALLOW["registered.csv"] and list(hh) == ALLOW["headline.csv"]:
            out += registered_closure_problems(rrows, hrows)
    return out


def all_folder_problems(files, full=True):
    out = leak_problems(files, full) + header_problems(files) + dup_key_problems(files) + value_problems(files) + tamper_problems(files) + verdict_problems(files)
    for n, t in files.items():
        if n == "README.md" and isinstance(t, str):
            out += ["%s: %s" % (n, p) for p in sorted(set(wording_problems(n, t)))]
    return out


def checksh_problems(text):
    """G12: the M27 guard in bin/check.sh holds its own literal copy of the eighteen canonical lines and of the 4.6 hash, and never reads them from this script."""
    a = text.find("rrt_leak_check() {")
    if a < 0:
        return ["bin/check.sh has no rrt_leak_check function"]
    region = text[a:text.find("\n}\n", a) + 3]
    out = []
    for l in SPEC_ALLOW_TEXT.splitlines():
        name, hdr = l.split(":", 1)
        if ("%s) want='%s'" % (name, hdr)) not in region:
            out.append("check.sh does not hold the literal header of %s" % name)
    if SPEC_PREREG_SHA256 not in region:
        out.append("check.sh does not hold the literal 4.6 hash")
    if re.search(r"rev_recognition_timing\.py", region) and not M("g12_checksh_reads_script"):
        out.append("check.sh names the script inside the guard (it must not read the headers from it)")
    return out


# ------------------------------------------------------------------------------------------------------------------------
# the README and SOURCES.md
# ------------------------------------------------------------------------------------------------------------------------
DIRECTION_WORDS = {"with_growth": "above zero, so the timing added to reported growth", "against_growth": "below zero, so the timing subtracted from reported growth", "zero": "zero", "": "undefined"}
QUALIFIER_WORDS = {"within_pre_window_range": "inside the range of the placebo windows", "outside_pre_window_range": "outside the range of the placebo windows", "none": "no placebo band to compare with", "": "no placebo band to compare with"}
VOID_WORDS = {"base_not_positive": "the base-year net income is not positive", "dni_small": "the change in net income is below 2% of the base-year level", "thin_coverage": "too few firms have filed", "none": ""}
SAMPLE_WORDS = collections.OrderedDict([
    ("primary", "all non-financial firms with every needed number stated (status in_scope)"),
    ("mega", "the nine largest of the 500, %s, those of them in scope" % "Alphabet, Amazon, Meta, Microsoft, Oracle, NVIDIA, Apple, Broadcom and Tesla"),
    ("s2_subset", "primary firms that S2 will cover (fiscal year-end from 30 November to 15 February)"),
    ("sens_gap0", "adds firms that tag a contract balance in some years only, the missing years set to zero"),
    ("sens_acq", "drops firms whose cash paid for acquisitions over fiscal 2023-2025 exceeds 2% of fiscal 2023 revenue"),
    ("sens_disc", "drops firms with income from discontinued operations (for example a spin-off) in a needed year"),
    ("sens_trim", "drops firms whose N exceeds a year's revenue in size (|N / revenue| above 1) in a needed year"),
    ("sens_unbilled", "adds unbilled receivables to contract assets for firms with no contract-asset tag"),
    ("sens_r2only", "drops firms whose revenue comes from the broad Revenues tag (rev_fallback)"),
    ("sens_parts", "uses the tagged current plus noncurrent parts instead of a tagged total wherever the parts exist at every year"),
    ("sens_latest", "takes every value from the latest filing that reports it, so restated figures replace first-reported ones, instead of the year's own 10-K"),
    ("sens_leave1", "drops the single largest positive contributor"),
    ("sens_samefiling", "takes the prior year's ratio r from the same 10-K as the current year (its comparative column, restated where the firm recast it), falling back to first-reported values where that 10-K does not "
                        "tag the comparative. Added after the result was seen, by an independent check on 28 October 2026; it is not part of the rule set in advance")])


def money(v, nd=1):
    """A USD amount as $x.xbn from a billion up and $x.xm below it, with the sign in front."""
    if v is None:
        return "n/a"
    x = Decimal(v)
    unit, div = ("bn", Decimal(10) ** 9) if abs(x) >= Decimal(10) ** 9 else ("m", Decimal(10) ** 6)
    q = (x / div).quantize(Decimal(1).scaleb(-nd), rounding=decimal.ROUND_HALF_EVEN)
    s = "{:,.{}f}".format(abs(q), nd)
    return ("-$%s%s" % (s, unit)) if q < 0 else "$%s%s" % (s, unit)


def tick_text(t):
    return t.replace("|", " / ")


def pctx(v, nd=2):
    return "n/a" if v is None else "%s%%" % "{:,.{}f}".format(Decimal(v).quantize(Decimal(1).scaleb(-nd), rounding=decimal.ROUND_HALF_EVEN), nd)


def dayx(v, nd=2):
    return "n/a" if v is None else "{:,.{}f}".format(Decimal(v).quantize(Decimal(1).scaleb(-nd), rounding=decimal.ROUND_HALF_EVEN), nd)


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out) + "\n"


def share_words(sc):
    if sc["share"] is None:
        return "not scored (%s)" % VOID_WORDS.get(sc["void_reason"], "")
    return "%s of the change in net income (label %s)" % (pctx(sc["share"]), sc["label"])


def hmap(c):
    return {(r[1], r[2], r[3]): r[4] for r in c["H"] if r[0] == c["vintage"]}


STATUS_WORDS = collections.OrderedDict([
    ("no_sec_record", "the SEC has no submissions or company-facts file for the CIK"),
    ("financial_sic", "the SEC's industry code (SIC) is 6000 to 6799: banks, insurers, brokers and similar; excluded because ASC 606 does not cover their main income"),
    ("no_sic", "the SEC file carries no industry code, so the firm cannot be classed as financial or not"),
    ("fy_ambiguous", "two or more original 10-Ks fall in one fiscal-year window, so the year-end is not unique"),
    ("end_mismatch", "a needed number is stated only for a date 1 to 7 days from the 10-K's period end, not for the date itself"),
    ("year_gap", "a needed input (the 10-K, revenue, net income or a complete contract-balance tag set) is missing in some year; the firm is dropped because its excess accrual cannot be computed from reported "
                 "numbers, and filling a gap with zero would invent data (sens_gap0 shows that variant)"),
    ("tiny_revenue", "revenue below $100 million in a needed year, where ratios turn unstable"),
    ("in_scope", "every needed input is stated in every needed year: the primary sample")])
FLAG_WORDS = collections.OrderedDict([
    ("rev_fallback", "revenue comes from the broad Revenues tag because the contract-revenue tags are not stated in every year"),
    ("acq2", "cash paid for acquisitions over fiscal 2023-2025 exceeds 2% of fiscal 2023 revenue"),
    ("disc_ops", "the firm reports income from discontinued operations (a disposal such as a spin-off) in a needed year"),
    ("total_gt_parts", "the tagged total is larger than its tagged current and noncurrent parts in some year, so the total was used"),
    ("extreme_r", "N exceeds a year's revenue in size (|N / revenue| above 1) in a needed year"),
    ("near_end", "some figure is stated for a date 1 to 7 days from the 10-K's period end"),
    ("gap_n", "a contract balance is tagged in some needed years only"),
    ("gap_10k", "no single original 10-K for a needed year"),
    ("gap_rev", "no revenue tag is stated in every needed year"),
    ("gap_ni", "net income is not stated in every needed year"),
    ("gap0_imputed", "a missing contract balance was set to zero (sens_gap0 only)"),
    ("unbilled_added", "unbilled receivables were added to contract assets (sens_unbilled only)")])
WINDOW_WORDS = {"fy2020_fy2022": "fiscal 2020 to 2022", "fy2020_fy2021": "fiscal 2020 to 2021", "fy2021_fy2022": "fiscal 2021 to 2022"}


def longdate(d):
    p = parse_date(d)
    return "%d %s %d" % (p.day, p.strftime("%B"), p.year) if p else d


LABEL_GLOSS = {"SHARE_BELOW_10": "below 10%", "SHARE_10_TO_25": "10% to 25%", "SHARE_ABOVE_25": "above 25%", "VOID": "no score"}


def readme_name(firm):
    """A firm's name for the README, only when it passes the wording ban (a name such as Vulcan Materials would not); the ticker always stands."""
    if firm.name and not wording_problems("README.md", firm.name):
        return "%s (%s)" % (firm.name, tick_text(firm.ticker()))
    return tick_text(firm.ticker())


def join_and(items):
    items = list(items)
    return items[0] if len(items) == 1 else (", ".join(items[:-1]) + " and " + items[-1] if items else "")


def render_readme(c):
    v = c["vintage"]
    hm = hmap(c)
    st, sc, scg = c["stats"]["primary"], c["sc"]["primary"], c["scg"]["primary"]
    band = c["band"]
    firms = c["firms"]
    w1, w2 = "fy2023_fy2025", "fy2025_fy2026"
    reg = c["rows"]["registered.csv"]
    s1row = [r for r in reg if r[0] == "S1"][0]
    s1v, n_s1 = s1row[3], s1row[4]
    weight = to_dec(hm.get((w1, "primary", "earnings_weight_pct")))
    n_fin = sum(1 for k in c["order"] if c["cls"][w1][k]["status"] == "financial_sic")
    n_miss = int(hm.get((w1, "primary", "ni_2025_all500_missing"), "0"))
    n_ni = len(c["order"]) - n_miss
    miss_fin, miss_oth = int(hm.get((w1, "primary", "ni_2025_missing_financial"), "0")), int(hm.get((w1, "primary", "ni_2025_missing_other"), "0"))
    sf, sfs = c["stats"]["sens_samefiling"], c["sc"]["sens_samefiling"]
    n_fb = len(c["sf_fallback"])
    fr_s1 = c["fragile_s1"]
    n_diff = len(c["label_differs"])
    L = []
    A = L.append

    def atmost(score, gross=False):
        if score["share"] is None:
            return "cannot be scored (%s; label VOID)" % VOID_WORDS.get(score["void_reason"], "")
        return "at most %s of the change in their net income" % pctx(score["share"] if gross else abs(score["share"]))

    # ---------------------------------------------------------------- the opening (R3-3): the ceiling, the figures, the denial, one sentence on fragility
    A("# Revenue-recognition timing and the growth in S&P 500 net income, fiscal 2023 to fiscal 2025 (SEC XBRL data)\n")
    first = ("This is a ceiling for the tagged balances under assumption A1, not an estimate: if every dollar by which a firm's contract balances moved beyond what its revenue growth would give is counted "
             "as profit, with no cost and no tax, the timing of revenue against billing in those balances is %s for the %s non-financial firms (S1, label %s: %s), and %s if only the firms where the "
             "timing was positive are counted (S1P, label %s: %s)." % (atmost(sc), n_s1, sc["label"], LABEL_GLOSS.get(sc["label"], "no score"), atmost(scg, gross=True), scg["label"], LABEL_GLOSS.get(scg["label"], "no score")))
    if M("g13_readme_attribution"):
        first = "The change in these firms' net income came from revenue booked ahead of or behind billing: " + first
    names = [readme_name(firms[r["cik"]]) for r, _ in fr_s1]
    share_sf = pctx(sfs["share"]) if sfs["share"] is not None else "no score"
    if not names:
        frag = "No single firm's removal takes S1 below 10%%, %d of the 13 samples give a different label, and the same-filing basis (each prior year as restated in the later report), added after the result was seen, gives %s." % (n_diff, share_sf)
    else:
        frag = ("These labels rest on %s: removing %s takes S1 below 10%%, %d of the 13 samples give a different label, and the same-filing basis (each prior year as restated in the later report), added after the result was seen, gives %s." % (
            "a few firms" if len(names) > 1 else "one firm", ("any one of " + join_and(names)) if len(names) > 1 else names[0] + " alone", n_diff, share_sf))
    A(first + " " + DENIAL_SENTENCE + " " + frag + "\n")
    prov = ("The numbers come from the SEC's structured filing data on data.sec.gov (company facts, submissions and frames), vintage %s (the UTC date the download began). The rule (samples, tags and thresholds) "
            "was fixed in a specification committed on 28 October 2026 before any data were fetched." % v)
    if s1v == "20261028":
        prov += (" An independent check on 28 October 2026 recomputed all %s firms from the raw SEC files and matched them to the dollar; it also supplied the same-filing sample, after the result was seen." % n_s1)
    A(prov + "\n")
    # ---------------------------------------------------------------- what was measured
    A("## What was measured\n")
    A("**The firms.** The %d distinct SEC registrants behind the %d tickers of the S&P 500 as this project's earlier tax work (workstream W3) holds them in `data/w3_tax/firm_tax_panel.csv`: the 2026 members, so "
      "firms that left the index are absent. Each registrant is identified by its CIK, the SEC's ten-digit Central Index Key. %d are financial firms and are excluded; the primary sample is the %s non-financial "
      "firms with every needed number stated, and they hold %s of the 500 firms' fiscal 2025 net income (that denominator covers %d of the 500: %d state no fiscal 2025 NetIncomeLoss fact, %d of them financial "
      "firms and %d not).\n" % (len(c["order"]), c["inp"]["panel"]["rows"], n_fin, st["n"], pctx(weight, 1), n_ni, n_miss, miss_fin, miss_oth))
    A("**The measure.** A contract asset is revenue a firm has booked but cannot yet bill; a contract liability is billing or cash received before the revenue is booked (deferred revenue). N, the net contract "
      "position, is contract assets minus contract liabilities, and r is N divided by the year's revenue. If revenue grows, N would grow in step at last year's r; the excess accrual in a year is the part of the "
      "change in N beyond that: N this year minus last year's r times this year's revenue. A firm's T_i is its excess accrual in fiscal 2025 minus its excess accrual in fiscal 2023 (the base year), and T is the sum "
      "of the T_i over the firms. T in days is T divided by fiscal 2025 revenue times 365.\n")
    A("**S1 and S1P.** The change in net income is fiscal 2025 minus fiscal 2023, summed over the firms. S1 is the size of T as a share of that change; S1P is the sum of the positive T_i as a share of the same "
      "change, so no firm's offset is netted. A label sorts the share: SHARE_BELOW_10 (below 10%), SHARE_10_TO_25 (10% to 25% inclusive), SHARE_ABOVE_25 (above 25%), or VOID when fiscal 2023 net income is not "
      "positive or the change is below 2% of it. The thresholds, 10% and 25%, were fixed in advance by the project, are not calibrated, and were not moved after the placebo windows (earlier periods used as a yardstick, described below) were seen. Direction "
      "is reported beside the label: with_growth when T is above zero, against_growth when it is below.\n")
    A("**Fiscal years.** A firm's fiscal year Y is the year of its original 10-K whose report date lies from 1 April of Y to 31 March of Y+1, whatever label the firm gives it.\n")
    A("## What the number is\n")
    A("Two assumptions frame it. There is no A2: the first draft's second assumption, about the reference year, was dropped because that year's excess accrual is now measured. "
      "(A1) Every dollar of excess accrual is counted as profit, with no cost and no tax. Because booked revenue carries costs and tax in practice, only part of it reaches net income, so |T| is at least as large as "
      "the effect on net income and " + CEILING_PHRASE + ". "
      "(A3) Timing in balances that are not tagged is invisible here. The SEC's company-facts feed carries only numbers tagged with the standard US accounting labels and not split by segment, product or other "
      "dimension; a balance reported only by segment (a dimensioned one), or under a company-made label outside the standard list (an extension), is absent.\n")
    A("N moves for ordinary explanations: milestone billing, contract mix, a large contract near year-end. Stock-funded acquisitions, spin-offs and other disposals, and currency translation can also move N with no "
      "change in recognition, and are not screened (sensitivities drop firms with large acquisitions or with discontinued-operations income). A large T is a reason to look, not a finding.\n")
    A("## What is left out\n")
    A("- **Trade receivables** are billed consideration awaiting cash: they measure collection, not recognition, and sit outside N (reported apart below).\n"
      "- **Capitalized contract costs** can move profit with N unchanged; the measure ignores them (reported apart below).\n"
      "- **Stock-funded acquisitions, spin-offs and currency translation** are not screened (see above).\n"
      "- **Dimensioned and extension balances** are absent from the SEC's company-facts feed (A3).\n"
      "- **Financial firms** (SIC 6000 to 6799) and firms with no SIC code are excluded; see the coverage section.\n")
    # ---------------------------------------------------------------- the result
    A("## The result and the sensitivities\n")
    A("Under A1, T is %s (%s days of revenue). The direction is %s: T is %s. Its size relative to revenue is %s (the placebo windows, earlier periods used as a yardstick, are explained below).\n" % (
        money(st["t"]), dayx(sc["t_days_rev"]), sc["direction"], DIRECTION_WORDS[sc["direction"]], QUALIFIER_WORDS[sc["qualifier"]]))
    A("Each row recomputes S1 and S1P on another sample or definition. Every row but the first is a sensitivity: it changes one rule to see whether the label survives.\n")
    rows = []
    for s in SAMPLES_S1:
        a, b, d = c["stats"][s], c["sc"][s], c["scg"][s]
        rows.append([s, str(a["n"]), money(a["t"]), dayx(b["t_days_rev"]), pctx(b["share"]) if b["share"] is not None else "n/a", b["label"], pctx(d["share"]) if d["share"] is not None else "n/a", d["label"],
                     b["direction"], SAMPLE_WORDS[s]])
    A(md_table(["Sample", "Firms", "T", "T in days of revenue", "S1: T / change in net income", "S1 label", "S1P: positive T_i / change", "S1P label", "Direction", "What it is"], rows))
    changed = [s for s in SAMPLES_S1 if s in c["label_differs"]]
    A("Samples whose S1 or S1P label differs from the primary sample's: %s (%d of the 13 samples). On the same-filing basis T is %s and S1 is %s; the next 10-K restates a comparative of %d of the %d firms, and "
      "for %d firms it does not tag the comparative, so the first-reported value stands.\n" % (", ".join(changed) if changed else "none", n_diff, money(sf["t"]), pctx(sfs["share"]) if sfs["share"] is not None else "n/a",
                                                                                              len(c["sf_restated"]), sf["n"], n_fb))
    A("**Flags** appear on firms in the tables below and in contributions.csv:\n")
    A("\n".join("- `%s`: %s." % (k, FLAG_WORDS[k]) for k in FLAG_ORDER) + "\n")
    A("## How much rests on a few firms\n")
    A("A leave-one-out check removes one firm at a time from the primary sample and rescores (descriptive; it registers nothing). S1 falls below 10%% when any one of these %d of the %d firms is removed: %s. "
      "S1P falls below 25%% when any one of %d firms is removed.\n" % (len(fr_s1), st["n"], "; ".join("%s, with S1 at %s" % (readme_name(firms[r["cik"]]), pctx(sh, 2)) for r, sh in fr_s1) if fr_s1 else "none", c["fragile_s1p_n"]))
    # ---------------------------------------------------------------- contributors
    A("## Contributors\n")
    pos, neg = c["contributors"]
    for title, lst in (("Largest positive contributions (shares of gross positive T, the sum of the positive T_i)", pos), ("Largest negative contributions (shares of gross negative T)", neg)):
        A("**%s**, by ticker; names are in contributors.csv:\n" % title)
        if lst:
            A(md_table(["Rank", "Ticker", "T_i", "Share of the side", "Flags"], [[str(k), tick_text(r["ticker"]), money(r["t"], 2), pctx(sh), flag_text(r["flags"]) or "none"] for k, r, sh in lst]))
        else:
            A("No firm in the sample has a T_i on this side.\n")
    A(CONTRIBUTOR_SENTENCE + " Concentration, as statistics and not verdicts: the five largest firms hold %s of gross positive T, %s of gross negative T and %s of contract liabilities at fiscal 2025.\n" % (
        pctx(to_dec(hm.get((w1, "primary", "top5_share_t_pos_pct")))), pctx(to_dec(hm.get((w1, "primary", "top5_share_t_neg_pct")))), pctx(to_dec(hm.get((w1, "primary", "top5_share_cl_fy2025_pct"))))))
    # ---------------------------------------------------------------- the placebo windows
    A("## The placebo windows: an earlier yardstick\n")
    A("The same statistic T, computed for earlier periods that need no fiscal 2023-or-later number, shows what ordinary movement in these balances looks like. \"Placebo\" here means only that: earlier windows "
      "used as a yardstick, not a test of anything.\n")
    rows = [[WINDOW_WORDS.get(r[0], r[0]), r[1], r[3], money(to_dec(r[4]), 2), pctx(to_dec(r[7]), 3), r[2]] for r in c["placebo_rows"]]
    A(md_table(["Window", "Inputs", "Firms", "T", "T / end-year revenue", "Fiscal 2020 an endpoint"], rows))
    A("NB1 (noise band 1) is |T| over end-year revenue for the only one-year window that does not start from fiscal 2020, fiscal 2021 to 2022: %s. NB2 (noise band 2) is the same for the two-year window, fiscal "
      "2020 to 2022: %s. Medians over all windows of each length: %s (one year) and %s (two years). S1 and S1P read within_pre_window_range when |T| over fiscal 2025 revenue is at most NB2, and "
      "outside_pre_window_range otherwise; S2 and S2P are read against NB1. The band rests on three windows, two of them with fiscal 2020 as an endpoint, so it is thin. The fiscal 2021 to 2022 window uses fiscal "
      "2020 balances as the prior-year input to its fiscal 2021 excess accrual. The band is frozen from the first full vintage and is not recomputed.\n" % (
          pctx(band["nb1"] * 100 if band["nb1"] is not None else None, 3), pctx(band["nb2"] * 100 if band["nb2"] is not None else None, 3),
          pctx(band["med1"] * 100 if band["med1"] is not None else None, 3), pctx(band["med2"] * 100 if band["med2"] is not None else None, 3)))
    # ---------------------------------------------------------------- descriptive tables
    A("## Descriptive tables (not registered)\n")
    rr = c["rows"]["receivables.csv"]
    A("**Trade receivables, collection and not recognition (descriptive).** Receivable days are receivables divided by revenue times 365, from the AccountsReceivableNetCurrent tag only, over the primary firms that tag it "
      "at every year:\n")
    A(md_table(["Fiscal year", "Firms", "Receivables", "Revenue", "Receivable days"], [[r[2], r[4], money(to_dec(r[5])), money(to_dec(r[6])), dayx(to_dec(r[7]))] for r in rr if r[1] == "level"]))
    tr = [r for r in rr if r[1] == "window_t"][0]
    A("The same T construction on receivables gives %s (%s days of revenue) for %s firms; this is a collection measure and is not added to T.\n" % (money(to_dec(tr[8])), dayx(to_dec(tr[9])), tr[4]))
    cc = [(y, hm.get((w1, "primary", "contract_cost_days_fy%d" % y)), hm.get((w1, "primary", "n_days_same_firms_fy%d" % y))) for y in window_years(w1)]
    A("**Capitalized contract costs (descriptive).** \"Costs in days\" is the capitalized contract costs divided by revenue times 365; \"N in days\" is N divided by revenue times 365 (negative when contract liabilities "
      "exceed contract assets), over the firms that tag the costs at every year: %s.\n" % ("; ".join("fiscal %d: costs %s days, N %s days" % (y, dayx(to_dec(a)), dayx(to_dec(b))) for y, a, b in cc if a not in (None, "")) or "no firm tags them at every year"))
    rp = [(y, hm.get((w1, "primary", "rpo_usd_fy%d" % y)), hm.get((w1, "primary", "rpo_days_fy%d" % y))) for y in window_years(w1)]
    A("**Remaining performance obligations (descriptive).** Contracted revenue not yet recognised, billed or not, over the primary firms that report all four years: %s.\n" % (
        "; ".join("fiscal %d: %s, %s days of revenue" % (y, money(to_dec(a)), dayx(to_dec(b))) for y, a, b in rp if a not in (None, ""))))
    n_cf, tcf, tbs, rev_cf = c["cf"]
    A("**Cash-flow cross-check (descriptive).** It recomputes T with each year's change in N taken from the cash-flow statement's change items instead of the balance sheet (signs set on fiscal 2019 to 2022, see "
      "SOURCES.md). %d firms tag the needed items; T from them is %s, against %s from the balance sheets for the same firms. The balance-sheet figure for these %d firms differs from the headline %s "
      "because the other %d primary firms, which do not tag the items, net to %s; the cash-flow figure differs from the balance-sheet one because the statement's change items need not equal the "
      "difference between two balance-sheet dates.\n" % (n_cf, money(tcf) if n_cf else "n/a", money(tbs) if n_cf else "n/a", n_cf, money(st["t"]), st["n"] - n_cf, money(st["t"] - tbs) if n_cf else "n/a"))
    # ---------------------------------------------------------------- S2
    A("## S2 and S2P\n")
    s2rows = [r for r in reg if r[0] in ("S2", "S2P")]
    last = max(r[3] for r in s2rows)
    s2 = {r[0]: r for r in s2rows if r[3] == last}
    cov26 = c["s2"]["cov"]
    A("S2 and S2P repeat S1 and S1P on fiscal 2025 to 2026 for the firms whose fiscal 2026 year-end falls between 30 November 2026 and 15 February 2027, a period no one can have seen when the specification was "
      "committed. A firm is eligible when the fiscalYearEnd field of its SEC submissions file (the month and day its fiscal year ends, for example 1231) lies from 30 November to 15 February and it is in scope on "
      "fiscal 2024 and 2025. S2 and S2P are scored once, on the first full build on or after 1 May 2027, and read PENDING until then. If fewer than 70%% of the %s eligible firms have filed a fiscal 2026 10-K "
      "(%s have, counting only a 10-K whose period end lies inside the window), they read PENDING_THIN (pending: too few filers yet) and are run again each month, and VOID after 1 August 2027 if still thin. "
      "They are reported beside s2_subset, the S1 statistic on the same firms: T %s, %s. Status on vintage %s: S2 %s, S2P %s.\n" % (
          hm.get((w2, "s2_eligible", "n_eligible_fy2025"), "0"), hm.get((w2, "s2_eligible", "n_with_fy2026_10k"), "0"), money(c["stats"]["s2_subset"]["t"]), share_words(c["sc"]["s2_subset"]), last, s2["S2"][15], s2["S2P"][15]))
    A(md_table(["Status for S2", "Firms"], [["fiscal 2026 10-K with its period end inside the window (counted)", str(len(cov26["in_window"]))],
                                           ["fiscal 2026 10-K with its period end outside the window (end_mismatch: never counted, never scored)", str(len(cov26["outside_window"]))],
                                           ["two or more original 10-Ks in the fiscal 2026 window (fy_ambiguous: never counted, never scored)", str(len(cov26["ambiguous"]))],
                                           ["no fiscal 2026 10-K yet (stays in the denominator)", str(len(cov26["none"]))]]))
    for k in cov26["outside_window"]:
        f = firms[k]
        tt = [x for x in f.filings if x[0] in ("10-KT", "10-KT/A")]
        A("%s: the submissions file says fiscalYearEnd %s, but its latest original 10-K covers the year to %s and %s; the data do not show a completed change of year-end.\n" % (
            tick_text(f.ticker()), f.fye or "(blank)", longdate(f.info(2026)[1]), "a 10-KT (transition report) is on file" if tt else "no 10-KT (transition report) has been filed"))
    # ---------------------------------------------------------------- coverage
    A("## Coverage and exclusions\n")
    cnt = collections.Counter(c["cls"][w1][k]["status"] for k in c["order"])
    A(md_table(["Status", "CIKs", "Meaning"], [[s_, str(cnt.get(s_, 0)), STATUS_WORDS[s_]] for s_ in STATUS_ORDER]))
    A("Financial firms (SIC 6000 to 6799) are excluded; %d of the 500 CIKs are in that range. ASC 606 leaves financial instruments, leases and insurance contracts out of its scope, and a bank's receivables are loans. "
      "The SIC range is not the boundary of ASC 606: it also drops exchanges, brokers and insurance brokers, whose fees are under ASC 606, and keeps card networks and processors under other codes. A firm with no "
      "contract-balance tag at any needed year has N equal to zero at every year and stays in scope. `coverage.csv` counts the 500 CIKs with a fact in each frame; the frames are used for coverage and checks "
      "only.\n" % n_fin)
    A("## Words\n")
    A("- **Vintage**: the UTC date a set of downloads began. **Trade receivable**: billed consideration awaiting cash. **Remaining performance obligation**: contracted revenue not yet recognised.\n"
      "- **Operating cash flow**: cash generated by operations, the statement that reports the year's change in these balances. **ASC 606**: the US accounting standard for revenue from contracts with customers.\n"
      "- **Latest-filed values**: for each number, the figure in the most recent filing that reports it, so restatements replace first-reported figures.\n"
      "- Columns ending _usd are whole dollars, _pct percent, _days days of revenue. The aggregates in headline.csv and registered.csv are sums of the whole-dollar cells in contributions.csv.\n")
    A("The fifteen CSV files: firms, firm_years, firm_tags, panel, contributions, headline, registered, contributors, placebo, receivables, coverage, checks, vintages, fetch_log and revisions. SOURCES.md lists every "
      "request, the rules and the builder's decisions.\n")
    A("## Citations\n")
    A("US Securities and Exchange Commission, EDGAR XBRL APIs (companyfacts, submissions, frames) on data.sec.gov, vintage %s (US government works, 17 U.S.C. 105). The project's specification and its rulings are in "
      "[the spec](../../_research/2026-10-28-Revenue-Recognition-Timing-Spec.md). How the numbers were fetched, the checks and the builder's decisions are in [SOURCES.md](SOURCES.md).\n" % v)
    return "\n".join(L)


# the spec author's 57 requests of 28 Oct 2026 (2.8): (number, UTC, path, status, bytes, sha256 first 12)
AUTHOR_REQUESTS = (
    (1, '06:21:31', '/api/xbrl/frames/us-gaap/ContractWithCustomerLiability/USD/CY2019Q4I.json', 200, 170706, '6ae9cd741778'),
    (2, '06:21:33', '/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityCurrent/USD/CY2019Q4I.json', 200, 228064, '989bcca3c607'),
    (3, '06:21:34', '/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityNoncurrent/USD/CY2019Q4I.json', 200, 105398, '24a9375a313f'),
    (4, '06:21:35', '/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNet/USD/CY2019Q4I.json', 200, 79080, '08b9525c0817'),
    (5, '06:21:37', '/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNetCurrent/USD/CY2019Q4I.json', 200, 69195, '344a307d46bf'),
    (6, '06:21:38', '/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNetNoncurrent/USD/CY2019Q4I.json', 200, 23553, 'dbc2bc7dfcd5'),
    (7, '06:21:40', '/api/xbrl/frames/us-gaap/Revenues/USD/CY2019.json', 200, 435064, '112eb1b4349f'),
    (8, '06:21:41', '/api/xbrl/frames/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/USD/CY2019.json', 200, 467424, 'bb44dd228eb4'),
    (9, '06:21:42', '/api/xbrl/frames/us-gaap/NetIncomeLoss/USD/CY2019.json', 200, 946165, 'f15e595eca6b'),
    (10, '06:21:44', '/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityCurrent/USD/CY2019Q2I.json', 200, 174582, '67fb471fe612'),
    (11, '06:21:45', '/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityCurrent/USD/CY2019Q3I.json', 200, 178358, '9c1d503fdd5d'),
    (12, '06:21:47', '/submissions/CIK0000789019.json', 200, 185671, '6acb47292f97'),
    (13, '06:21:48', '/api/xbrl/companyfacts/CIK0000723531.json', 200, 3497237, 'c14cf3666260'),
    (14, '06:22:25', '/api/xbrl/frames/us-gaap/ContractWithCustomerLiability/USD/CY2023Q4I.json', 200, 177860, '9e4576f5040c'),
    (15, '06:22:26', '/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityCurrent/USD/CY2023Q4I.json', 200, 267855, '49d6c222fea4'),
    (16, '06:22:28', '/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityNoncurrent/USD/CY2023Q4I.json', 200, 110695, '663928642186'),
    (17, '06:22:29', '/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNet/USD/CY2023Q4I.json', 200, 79430, 'eb0d0814f431'),
    (18, '06:22:31', '/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNetCurrent/USD/CY2023Q4I.json', 200, 74624, 'db9080afdf8b'),
    (19, '06:22:32', '/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNetNoncurrent/USD/CY2023Q4I.json', 200, 23638, '5e73d816e127'),
    (20, '06:22:33', '/api/xbrl/frames/us-gaap/AccountsReceivableNetCurrent/USD/CY2023Q4I.json', 200, 442699, '85bc970e0e18'),
    (21, '06:22:35', '/api/xbrl/frames/us-gaap/ReceivablesNetCurrent/USD/CY2023Q4I.json', 200, 60780, '4358c0aa9a8b'),
    (22, '06:22:36', '/api/xbrl/frames/us-gaap/AccountsNotesAndLoansReceivableNetCurrent/USD/CY2023Q4I.json', 200, 14350, '904d3f03bc6b'),
    (23, '06:22:38', '/api/xbrl/frames/us-gaap/ContractWithCustomerReceivableAfterAllowanceForCreditLossCurrent/USD/CY2023Q4I.json', 200, 4824, '384bd988bcf5'),
    (24, '06:22:39', '/api/xbrl/frames/us-gaap/DeferredRevenueCurrent/USD/CY2023Q4I.json', 200, 80634, '60472c932ba4'),
    (25, '06:22:40', '/api/xbrl/frames/us-gaap/RevenueRemainingPerformanceObligation/USD/CY2023Q4I.json', 200, 104247, '8d373307e21c'),
    (26, '06:22:42', '/api/xbrl/frames/us-gaap/AccountsReceivableNetNoncurrent/USD/CY2023Q4I.json', 200, 11509, '73110e8df10d'),
    (27, '06:22:43', '/api/xbrl/frames/us-gaap/UnbilledContractsReceivable/USD/CY2023Q4I.json', 200, 20815, '5a6f0f729260'),
    (28, '06:22:44', '/api/xbrl/frames/us-gaap/ContractWithCustomerLiability/USD/CY2025Q4I.json', 200, 155939, '4916481b82d4'),
    (29, '06:22:46', '/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityCurrent/USD/CY2025Q4I.json', 200, 247125, '8cb8c0d85191'),
    (30, '06:22:47', '/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityNoncurrent/USD/CY2025Q4I.json', 200, 102336, '77466be9a3b9'),
    (31, '06:22:49', '/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNet/USD/CY2025Q4I.json', 200, 68029, 'b7cf577ed3bc'),
    (32, '06:22:50', '/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNetCurrent/USD/CY2025Q4I.json', 200, 72161, '85db54cf43b6'),
    (33, '06:22:52', '/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNetNoncurrent/USD/CY2025Q4I.json', 200, 21703, '5ca0a1f9ad65'),
    (34, '06:22:53', '/api/xbrl/frames/us-gaap/AccountsReceivableNetCurrent/USD/CY2025Q4I.json', 200, 407016, 'ec500eddb769'),
    (35, '06:22:54', '/api/xbrl/frames/us-gaap/ReceivablesNetCurrent/USD/CY2025Q4I.json', 200, 49720, 'c255dafc343b'),
    (36, '06:22:55', '/api/xbrl/frames/us-gaap/DeferredRevenueCurrent/USD/CY2025Q4I.json', 200, 63046, '4f1eefc2c4ee'),
    (37, '06:22:57', '/api/xbrl/frames/us-gaap/RevenueRemainingPerformanceObligation/USD/CY2025Q4I.json', 200, 97460, '82ae0957285e'),
    (38, '06:22:58', '/api/xbrl/frames/us-gaap/ContractWithCustomerLiability/USD/CY2026Q2I.json', 200, 125018, 'b5c0105dd845'),
    (39, '06:23:00', '/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityCurrent/USD/CY2026Q2I.json', 200, 204482, '679f55bb2777'),
    (40, '06:23:01', '/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNetCurrent/USD/CY2026Q2I.json', 200, 60650, '25be4564636f'),
    (41, '06:23:02', '/api/xbrl/frames/us-gaap/AccountsReceivableNetCurrent/USD/CY2026Q2I.json', 200, 344333, '31327d7f1981'),
    (42, '06:23:04', '/api/xbrl/frames/us-gaap/RevenueRemainingPerformanceObligation/USD/CY2026Q2I.json', 200, 87872, 'd17b561817e2'),
    (43, '06:23:17', '/api/xbrl/frames/us-gaap/Revenues/USD/CY2023.json', 200, 409960, 'fc7cf4e32d91'),
    (44, '06:23:18', '/api/xbrl/frames/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/USD/CY2023.json', 200, 480689, '13d3dd083fe1'),
    (45, '06:23:20', '/api/xbrl/frames/us-gaap/RevenueFromContractWithCustomerIncludingAssessedTax/USD/CY2023.json', 200, 119965, '81187c80bc89'),
    (46, '06:23:21', '/api/xbrl/frames/us-gaap/NetIncomeLoss/USD/CY2023.json', 200, 974484, '250bd2dd6e12'),
    (47, '06:23:22', '/api/xbrl/frames/us-gaap/Revenues/USD/CY2025.json', 200, 345804, 'ed2f734d3f98'),
    (48, '06:23:24', '/api/xbrl/frames/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/USD/CY2025.json', 200, 414741, 'a400a02d09ca'),
    (49, '06:23:25', '/api/xbrl/frames/us-gaap/RevenueFromContractWithCustomerIncludingAssessedTax/USD/CY2025.json', 200, 101372, '356cb1414f8d'),
    (50, '06:23:26', '/api/xbrl/frames/us-gaap/NetIncomeLoss/USD/CY2025.json', 200, 869214, 'e6434be0c524'),
    (51, '06:23:28', '/api/xbrl/frames/us-gaap/IncreaseDecreaseInAccountsReceivable/USD/CY2025.json', 200, 472718, '9409e31becf3'),
    (52, '06:23:29', '/api/xbrl/frames/us-gaap/IncreaseDecreaseInContractWithCustomerLiability/USD/CY2025.json', 200, 204315, '213ccd678323'),
    (53, '06:23:31', '/api/xbrl/frames/us-gaap/PaymentsToAcquireBusinessesNetOfCashAcquired/USD/CY2025.json', 200, 198735, '59ba5d240c0d'),
    (54, '06:25:30', '/api/xbrl/frames/us-gaap/AccountsReceivableAfterAllowanceForCreditLossCurrent/USD/CY2023Q4I.json', 404, 366, 'eb09525baa3d'),
    (55, '06:25:32', '/api/xbrl/frames/us-gaap/AccountsReceivableAfterAllowanceForCreditLossCurrent/USD/CY2025Q4I.json', 404, 386, 'c03b5fb89acd'),
    (56, '06:25:33', '/api/xbrl/frames/us-gaap/AccountsReceivableAfterAllowanceForCreditLossCurrent/USD/CY2026Q2I.json', 404, 366, 'cae5a74c1ed8'),
    (57, '06:26:01', '/api/xbrl/frames/us-gaap/AccountsNotesAndLoansReceivableNetCurrent/USD/CY2025Q4I.json', 200, 12771, '8ff0403f2815'),
)

DECISIONS = [
    ('Canonical texts rebuilt from constants', '4.6 and 4.7 are built in the script from the numbers the code itself uses (thresholds, floor, dates, tag names), so editing one changes its sha256 and the build refuses to write registered.csv; the allowlist of 5 is pasted. The three hashes are the ones the supervisor gave. They are checked at every build (C11) and by the selftest (G10, G12).'),
    ('Aggregates are sums of the written whole-dollar cells', "R8 rounds each USD cell to whole dollars at write time, but C07 and success criterion 6 ask the sum of contributions.csv to equal T, T_pos and the change in net income within 1 USD, and independent rounding would leave several dollars of gap over several hundred firms. Each firm's cells are therefore rounded half-even once, when its record is made, and every aggregate (T, T_pos, T_neg, the change in net income, the net income and revenue sums, and so every share and label) is computed from those cells on unrounded Decimals. The difference from summing unrounded values is under half a dollar a firm. Rounding to the printed decimals still happens only at write time."),
    ('Entity names in title case; the README names contributors by ticker', 'SEC registrant names are upper case, and a name such as Vulcan Materials Co would carry the banned verdict token for materiality (success criterion 4 greps case-sensitively, and the wording ban catches the word in the README). entity_name is therefore written in title case, the README lists contributors by ticker, and the names stay in contributors.csv and firms.csv. Names are read from the cached submissions files at build time, because no extract column holds them.'),
    ('README sentence 2 is the denial sentence', 'Section 0 makes the denial sentence the second README sentence; section 5 lists the results before it. The first sentence carries what was measured and the S1 and S1P results, the second is the denial sentence verbatim, and a paragraph with the thresholds follows. The README lists contributors by ticker, not by name.'),
    ('Extraction runs inside the fetch modes', "cf_extract.csv needs each firm's D_Y to pick the facts within 7 days of it, so fetch-companyfacts refuses to start (exit 5) until fetch-submissions has written submissions_extract.csv. A fetch mode writes its extract, from all cached bodies and sorted, once every planned body is cached or recorded as 404; a run that stops short prints what is missing and writes no extract. Firms whose submissions file is 404 get no companyfacts request (they are no_sec_record)."),
    ('Fetch mechanics', "--vintage is required and must be today's UTC date or an existing vintage folder, so the 2027-05-01 gate cannot be opened by naming a future vintage. Exit codes: 0 done, 2 STOP or no contact string or a data error, 3 network fault, 4 a run ended by its cap or by --max-requests with work left, 5 refused. The 1.0 s gap is measured from the end of the previous reply to the next request, timestamps in fetch_log.csv carry milliseconds, and a network fault is logged with status 0. A 404 recorded in vintages.csv is final for the vintage and is not requested again. A body in raw/ that does not match its vintages.csv row stops the run (exit 5) and is never fetched over. A 404 on an older submissions page, a reply for another CIK and a 200 that is valid JSON but not the document asked for latch STOP like the other content failures. The STOP file's body_head has the contact string replaced if a reply echoes it."),
    ('Frames plan', "13 balance-sheet tags at CY2019Q4I, CY2023Q4I and CY2025Q4I and 9 duration tags at CY2019, CY2023 and CY2025 (22 tags, 66 requests), plus CY2026Q4I and CY2026 from 2027-05-01 on (22 more). Any 2026 period is held back before that date, which is stricter than the specification's CY2026Q2I and later. The probe-only tags of 2.5 (AccountsReceivableNetNoncurrent, ContractWithCustomerReceivableAfterAllowanceForCreditLossCurrent, AccountsReceivableAfterAllowanceForCreditLossCurrent) are not fetched."),
    ('What cf_extract holds', "Every USD fact of the tags of 2.4 whose end is within 7 days of a needed D_Y (2019 to 2025, and 2026 from 2027-05-01), with filed, form and accn. Before the S2 date nothing after D_2025 (or after 2026-03-31 where there is no D_2025) is extracted, so FY2025's near-end diagnostic sees only facts up to D_2025 and not the 7 days after it: the hashed P5 reads plus or minus 7 days while R1-10 forbids later facts, and the stricter blind reading was taken. The file may be large (tens of megabytes); it is committed whole."),
    ('The pre stage', "build --stage pre reads only submissions rows reported up to 2023-03-31, only facts ending up to each firm's D_2022 plus 7 days (decided on the end date before any value is converted) and only the CY2019 frames. Besides placebo.csv (windows, NB1 and NB2, from which the medians follow) and coverage.csv (CY2019 periods only; n_cik_in_scope counts the fy2020_fy2022 scope), it writes the files that let the placebo be checked: firms.csv (status for the window fy2020_fy2022), firm_years.csv (FY2019-FY2022), firm_tags.csv, panel.csv and contributions.csv for the three placebo windows, and checks.csv (C01, C03, C04 and C06 to C14; C02 and C05 need later frames or filings and run in the full stage). The full stage rewrites these files whole and rewrites placebo.csv only if its bytes would change, so the stage-order test of criterion 9 can hold. A pre build is refused for a vintage whose S1 is already scored. The cash-flow sign convention is also set in this stage's data (fiscal 2019-2022) and written by the full stage."),
    ('Vintages and what accumulates', 'headline.csv, registered.csv, vintages.csv and fetch_log.csv accumulate over vintages (their keys carry the vintage); revisions.csv is regenerated from headline.csv on every build and lists the statistics that differ between adjacent vintages. The other files describe the last vintage built. S1 and S1P are written on the first full vintage and kept verbatim by later ones; placebo.csv is the band frozen on that vintage. S2 and S2P get a row per vintage until one is scored (VOID included) and are then kept verbatim.'),
    ('Required inputs and gaps', "R1-15 and P11 are read literally: N, revenue and net income must be stated at every needed year, FY2022 to FY2025 for S1, even though the change in net income uses only FY2023 and FY2025. A contract-balance family with a tag at some needed years only, and no complete set of parts, is a gap (gap_n); a Noncurrent tag alone, stated at every year, counts as parts. Two different values for one context in one filing are treated as missing, not resolved, and counted in the build's console output."),
    ('Near-end facts', "Near facts (end 1 to 7 days from D_Y) are looked for in the year's own 10-K only. A firm is end_mismatch when, at some needed year, no tag of revenue, net income, contract assets or contract liabilities (DeferredRevenue included) has an exact fact and one of them has a near fact. near_end is set when any such near fact exists."),
    ('Structure details', 'total_gt_parts is set when the total is used and exceeds the parts tagged at some year. sens_parts uses the parts wherever they are tagged at every year. DeferredRevenueNoncurrent is extracted with DeferredRevenueCurrent for the fallback. A firm with no contract tag at any needed year has N = 0 (structure absent_everywhere) and stays in scope.'),
    ('Sensitivity samples', 'Every sensitivity except sens_gap0 starts from the primary firm set: sens_acq, sens_disc, sens_trim, sens_r2only and sens_leave1 drop firms; sens_parts, sens_unbilled and sens_latest change values (sens_latest keeps the primary firms and their tags, with latest-filed values); sens_gap0 adds the firms whose only gap is gap_n, the missing side set to 0, with the revenue floor applied. acq2 sums PaymentsToAcquireBusinessesNetOfCashAcquired over FY2023-FY2025 against FY2023 revenue (R2-5); a firm that does not tag it is not flagged. s2_subset is the primary firms in the S2 set: before 2027-05-01 those whose fiscalYearEnd falls in 1130-1231 or 0101-0215 and that are in scope on FY2024-FY2025, afterwards the firms S2 actually scores.'),
    ('VOID and PENDING rows', 'A VOID row writes no share but keeps T, the change in net income, direction and qualifier, which do not depend on the sign of that change. PENDING and PENDING_THIN rows write no number except n_firms for PENDING_THIN (the firms eligible at fiscal 2025), with qualifier none and no direction; the coverage count is in headline.csv.'),
    ('Placebo and statistics details', "Medians are over all windows of each length (R2-2). NB1 and NB2 are ratios of |T| to end-year revenue, written as percents. placebo.csv's share_pct is blank where the VOID conditions hold. The ticker column of contributions.csv carries the joined tickers (GOOGL|GOOG). Contributors tie-break on the CIK. The window and sample enumerations of section 5 are the only ones written."),
    ('Checks', 'C02 is evaluated on the first vintage only and is INFO afterwards. C03 compares exact counts (a warning on any difference). C07 reads the written cells. C13 needs the raw cache (--raw overrides its place) and fails if it is absent. A population drift (C01 FAIL) stops the build before anything is written. C14 compares only pairs that exist in both sources.'),
    ('What the selftest reads', "R7 lets the script read the panel and its own folders only. The selftest also reads bin/check.sh (read-only) and nothing else outside them, because R1-25 asks G10 and G12 to be cross-checked against M27's literal copies of the 4.6 hash and the eighteen header lines. It builds its synthetic world in a temporary folder, makes no request and never reads SEC_UA from the environment."),
    ('Guard M27', 'In bin/check.sh, warn-only, appended after M26 and called after it in --all. It holds its own copy of the eighteen header lines and of the 4.6 hash, treats a folder with no README.md as the pre stage (missing names are then a warning), and prints one line per problem.'),
    ('Supervisor ruling S2-R1 (28 Oct 2026): S2 coverage and a fiscal year-end mismatch', "Dated 28 Oct 2026, from the supervisor, after the first full build of vintage 20261028. (a) The denominator of the 70% test is unchanged: the firms eligible by the FY2025 rule (a fiscalYearEnd in 1130-1231 or 0101-0215 in the submissions file, and in scope on FY2024-FY2025). (b) The numerator, n_with_fy2026_10k, counts a firm only when its FY2026 original 10-K's period end lies inside [2026-11-30, 2027-02-15]; a firm with two or more original 10-Ks in the FY2026 window is not counted either (it is fy_ambiguous). (c) A firm in the denominator whose FY2026 10-K ends outside the window is never counted and, at scoring, is excluded from S2 and S2P with the status end_mismatch. The first case is a firm whose submissions file says fiscalYearEnd 1231 while its FY2026 10-K ends on 2026-06-30 and was filed on 2026-08-14 (the data do not show that the year-end changed; no 10-KT has been filed). The status is stated in headline.csv (n_s2_end_mismatch, n_s2_fy_ambiguous and n_s2_no_fy2026_10k beside n_eligible_fy2025 and n_with_fy2026_10k; the four counts add up to the denominator), in the README's S2 section and in its table of S2 statuses. An existing status was used because a new one would have to be added to P12 in the hashed 4.7 block, which this ruling leaves alone; end_mismatch is read here as the period end not matching the S2 window, which is wider than P5's 7-day rule for facts. A dedicated status would also need the allowed-status lists of section 5 and of the script changed; the M27 guard checks no status value and would not change. No rule, threshold, label or hashed block changes, and S1 and S1P are not re-scored."),
    ('Supervisor ruling R3-1 (28 Oct 2026): the same-filing sensitivity, added after the result was seen', "An independent check on 28 Oct 2026 recomputed r_(t-1) from the year-t original 10-K's own comparative column (N and revenue of year t-1 as reported in the same accession as year t) instead of the first-reported figures of year t-1, and the ruling adds it as the sample sens_samefiling. It was added after the primary result was seen, by that check, and is not part of the rule set fixed in advance; the README's sensitivity table says so. The build computes it offline from the vintage's cf_extract.csv, which already holds every fact that ends within 7 days of a fiscal year-end whatever filing carries it (so the comparative columns of later 10-Ks are in it). N_t, revenue_t and the change in net income are the primary's; only r_(t-1) in the base-year and end-year excess accruals changes. The tags are those of the firm's primary structure for each of contract assets, contract liabilities and revenue. Where the year-t 10-K does not state every one of them for year t-1, r_(t-1) falls back to the first-reported value for that year; headline.csv states how many firms do that (n_samefiling_fallback). It also states how many firms' comparatives were restated, meaning any tag's comparative differs from the first-reported value (n_samefiling_restated). On vintage 20261028 the build gives T 23,698,570,553 USD, S1 9.992% and S1P 24.510%, the verifier's figures to the dollar; GE's T_i moves by -2,606,864,195.68 USD exactly (-2,606,864,196 between the two whole-dollar cells; the verifier's -2,606,864,195 is within 1 USD). The fallback count here is 6 firms (11 firm-years); the verifier's 20 equals the build's count of restated firms, so the verifier's wording 'on the fallback' is read as 'restated'. The primary sample, S1 and S1P are not changed and registered.csv is not touched."),
    ('Supervisor ruling R3-2 (28 Oct 2026): fragility counts', "Descriptive, not a new registered statement. For every firm in the primary sample the build removes it alone, rescores S1 and S1P on the other firms (same VOID rule, same thresholds, S1 against NB2 as ever) and counts the firms whose removal takes S1 below 10% and S1P below 25%; a count is zero when the full sample is already below the threshold. headline.csv holds n_leave1_s1_below_10, n_leave1_s1p_below_25 and, for each firm that takes S1 below 10%, leave1_s1_share_pct_<ticker>; the README names those firms. On vintage 20261028: 4 firms for S1 (BA 4.309%, DELL 8.197%, GE 8.761%, GD 9.732%) and 17 for S1P, as the verifier found. A removal that leaves S1P exactly at 25% would count as below; none does."),
    ('Supervisor ruling R3-3 (28 Oct 2026): the README opening', "The ruling overrides the specification's wording of item (1), 'came from revenue booked ahead of or behind billing', which reads as attribution. The opening now states, in this order, that the share is a ceiling for the tagged balances under assumption A1 and not an estimate ('at most'); the S1 and S1P figures with their labels; and, after the denial sentence, one sentence on fragility (the firms whose removal takes S1 below 10%, how many of the 13 samples give a different label, and the same-filing figure). The denial sentence stays verbatim and is still the second sentence of the opening paragraph, as section 0 of the specification requires, so it sits between the figures and the fragility sentence. The direction ('T is above zero, so the timing added to reported growth') appears only later, after the ceiling. A short provenance paragraph follows; its sentence on the independent check appears only for the vintage it describes (20261028)."),
    ('Supervisor ruling R3-4 (28 Oct 2026): the README for a cold reader', "Fixes made after a reader who knows accounting read the README cold: the 500 firms are described (S&P 500 registrants as workstream W3 holds them); CIK, T, T_i, the labels, S1 and S1P, the base year (fiscal 2023), vintage and the placebo windows are defined at first use; the thresholds are said to have been fixed in advance by the project; the assumptions keep the names A1 and A3 and the text says why there is no A2; the receivables tag is called by its name instead of A1; company facts, dimensioned balances and extensions are explained; the one-line argument for 'at least as large as the effect' is given; every flag and every status is defined, with the reason year_gap firms are dropped; the megacap firms are named; NB1 and NB2 are expanded; N in days, costs in days and receivable days are defined; the cash-flow cross-check says why its figure differs from the headline; fiscalYearEnd and PENDING_THIN are explained; and the earnings weight states its denominator (455 of the 500 CIKs on vintage 20261028: 45 state no fiscal 2025 NetIncomeLoss fact, 10 of them financial firms and 35 not). Only the denominator counts are new numbers (headline.csv: ni_2025_missing_financial and ni_2025_missing_other)."),
    ('Supervisor ruling R3-5 (28 Oct 2026): wording for a firm whose year-end does not match', "The data do not show a completed change of fiscal year-end for the end_mismatch firm: the submissions file says fiscalYearEnd 1231, the firm's latest original 10-K covers the year to 30 June 2026, and no 10-KT (transition report) has been filed. The README says exactly that, built from the data for each such firm (the fiscalYearEnd read, the period end of the latest original 10-K, and whether a 10-KT is on file), and does not say that the year-end changed.")
]


def render_sources(c):
    v = c["vintage"]
    L = []
    A = L.append
    A("# Sources, requests and builder decisions: revenue-recognition timing in the net-income growth of the W3 firm set\n")
    A("The specification is `_research/2026-10-28-Revenue-Recognition-Timing-Spec.md`, committed at 2cd528f (with the supervisor's rulings of rounds 1 and 2) before the first request. Every number comes from "
      "data.sec.gov (R10).\n")
    A("## Requests\n")
    A("**By the spec author, 28 Oct 2026** (57 requests, all GET to data.sec.gov, sequential, at least 1.0 s apart, 14,747,233 bytes; 54 x 200 and 3 x 404; no redirect followed, no retry, no 403 or 429). They used the neutral "
      "User-Agent of CLAUDE.md's working rules, with no address. The supervisor's 8 coverage requests of the same day used it too (their list is not in the specification).\n")
    A("| # | UTC (28 Oct) | Path | Status | Bytes | sha256, first 12 |\n|---|---|---|---|---|---|")
    for n, t, p, s_, b, h in AUTHOR_REQUESTS:
        A("| %d | %s | `%s` | %d | %s | `%s` |" % (n, t, p, s_, "{:,}".format(b), h))
    A("")
    A("**By this build** (the fetch modes; the supervisor runs them with the contact string in SEC_UA, which no file holds; every request is a row of fetch_log.csv and every kept body a row of vintages.csv):\n")
    kinds = collections.Counter()
    for r in c["inp"]["fetch"]:
        kinds[(kind_of(r["path"]) or "other", r["status"])] += 1
    A(md_table(["Kind", "Status", "Requests"], [[k, s_, str(n)] for (k, s_), n in sorted(kinds.items())]) if kinds else "No request is logged yet.\n")
    A("## Rules applied\n")
    A("- **Fiscal year Y** is the report date of the firm's original form 10-K with a report date from Y-04-01 to (Y+1)-03-31 (a 10-K/A or 10-KT never defines it); none is `year_gap`, two or more `fy_ambiguous`. "
      "The `fy` and `fp` labels are never used.\n"
      "- **Facts**: USD only; an instant has end equal to D_Y, a duration has end equal to D_Y and 350 to 380 days. Primary basis `own_10k`: the fact whose accn is that year's 10-K; sensitivity `sens_latest`: the "
      "latest-filed fact, ties to the largest accn. Facts within 7 days of D_Y are a diagnostic (`near_end`); a needed value with a near fact but no exact one makes the firm `end_mismatch`.\n"
      "- **Tags** (2.4): CA, CL (total, else current plus noncurrent, else DeferredRevenue), revenue R2, R3, Revenues, NetIncomeLoss; receivables, contract costs, remaining performance obligations, unbilled "
      "receivables and the cash-flow change tags are descriptive.\n"
      "- **Evidence behind the total rule**, observed on fiscal 2019 by the spec author (per-firm comparisons within 0.5%, no sums): liabilities at CY2019Q4I, all three tags 59 (total = current + noncurrent in 45, "
      "= current in 1, neither in 13); total and current without noncurrent 36 (equal 14, total larger 13, total smaller 9); total only 81; current only 51; current and noncurrent 49. Contract assets: all three 9 "
      "(total = parts in 8); total and current 7 (equal 3, larger 3, smaller 1); total only 61; current only 28; current and noncurrent 13. Revenue at CY2019: 104 firms tag both Revenues and R2 (equal 49, "
      "Revenues larger 50, smaller 5).\n")
    A("## What the spec author looked at before any build (the blind rule, 2.7)\n")
    A("Fiscal-2019 identity comparisons and end-date offsets; for the 2023-2026 frames only counts (how many of the 500 appear, end months, durations, set intersections), no value of any firm; one submissions file "
      "(filing metadata) and one companyfacts file (structure and filing dates of facts ending in 2018 and 2019). No T, EA, r or share, and no sum, average or ratio of any fiscal 2023-2026 value, was computed.\n")
    A("## Builder decisions\n")
    A("Where the specification is ambiguous the stricter reading about leaks, blindness and causal wording was taken. None of these changes a rule, a threshold, a window, a registered text, a label or a hashed block.\n")
    for i, (t, d) in enumerate(DECISIONS, 1):
        A("%d. **%s.** %s\n" % (i, t, d))
    sg = c.get("signs")
    if sg:
        A("%d. **Cash-flow sign convention, measured (R1-7).** Set on fiscal 2019-2022 for firms without acquisitions, as the sign that matches the balance-sheet change in most firm-years: contract assets %s "
          "(%d firm-years agree, %d oppose), contract liabilities %s (%d, %d), trade receivables %s (%d, %d). A sign of +1 means the tag is positive when the balance rises.\n" % (
              len(DECISIONS) + 1, sg["ca"][0] if sg["ca"][0] is not None else "undetermined", sg["ca"][1], sg["ca"][2], sg["cl"][0] if sg["cl"][0] is not None else "undetermined", sg["cl"][1], sg["cl"][2],
              sg["ar"][0] if sg["ar"][0] is not None else "undetermined", sg["ar"][1], sg["ar"][2]))
    A("### Fixes after the first run (R9)\n")
    A("None yet. A post-registration fix is listed here with its old and new value.\n")
    return "\n".join(L)


# ------------------------------------------------------------------------------------------------------------------------
# render, finish and the build command
# ------------------------------------------------------------------------------------------------------------------------
PRE_NAMES = ("firms.csv", "firm_years.csv", "firm_tags.csv", "panel.csv", "contributions.csv", "placebo.csv", "coverage.csv")
FULL_NAMES = PRE_NAMES + ("headline.csv", "registered.csv", "contributors.csv", "receivables.csv", "revisions.csv")


def render_all(c):
    """Every output of the stage but checks.csv, vintages.csv and fetch_log.csv (the two logs are written by the fetch modes and only read here)."""
    v, stage = c["vintage"], c["stage"]
    full = stage == "full"
    base = "stage %s; population %s" % (stage, PANEL_REL)
    note = {"firms.csv": "status is for window fy2023_fy2025 (S1)" if full else "status is for window fy2020_fy2022 (the pre stage reads no later year)",
            "placebo.csv": "the band frozen from the first full vintage" if c["frozen"] else "placebo windows, fiscal 2019-2022 inputs only",
            "coverage.csv": "n_cik_in_scope counts the S1 scope in the full stage and the fy2020_fy2022 scope in the pre stage", "headline.csv": "all vintages built so far", "registered.csv": "all vintages built so far; S1 and S1P are scored once", "revisions.csv": "regenerated on every build"}
    t = collections.OrderedDict()
    for name in (FULL_NAMES if full else PRE_NAMES):
        rows = c["placebo_rows"] if name == "placebo.csv" else c["rows"][name]
        src = source_line_vintage(v, ("population %s" % PANEL_REL) + ("; " + note[name] if name in note else "")) if name == "placebo.csv" else source_line_vintage(v, base + (("; " + note[name]) if name in note else ""))
        t[name] = render_csv(name, rows, src)
    if full:
        rd = render_readme(c)
        guard_text("README.md", rd)
        t["README.md"] = rd
        t["SOURCES.md"] = render_sources(c)
        guard_text("SOURCES.md", t["SOURCES.md"])
    return t


def finish(load):
    """Render twice from independently loaded inputs (C12), add the checks, run the folder guards. Returns (texts, failed check ids, the first computation)."""
    if not allow_hash_ok():
        raise DataError("the column allowlist in this script does not hash to SPEC_ALLOW_SHA256")
    inp1 = load()
    c1 = compute(inp1)
    t1 = render_all(c1)
    inp2 = load()
    c2 = compute(inp2)
    t2 = render_all(c2)
    if M("x_render_unstable"):
        t2["firms.csv"] += "x"
    checks = build_checks(c1, t1, t2)
    t1["checks.csv"] = render_csv("checks.csv", checks, source_line_vintage(c1["vintage"], "stage %s; population %s" % (c1["stage"], PANEL_REL)))
    if any(r[0] == "C01" and r[4] == "FAIL" for r in checks):
        raise DataError("the population drifted from the pinned panel (C01): nothing is written")
    files = dict(t1)
    out_dir = c1["inp"]["out_dir"]
    for nm in ("vintages.csv", "fetch_log.csv"):
        p = os.path.join(out_dir, nm)
        if os.path.isfile(p):
            files[nm] = read_file(p, "r")
    probs = all_folder_problems(files, full=c1["stage"] == "full")
    if probs:
        raise DataError("folder guards: " + "; ".join(probs[:5]))
    c1["checks"] = checks
    return t1, [r[0] for r in checks if r[4] == "FAIL"], c1


def write_outputs(texts, c, out_dir):
    for n, x in texts.items():
        if n == "placebo.csv":
            if not c["frozen"]:
                write_text_if_changed(os.path.join(out_dir, n), x)          # an identical re-run keeps the file's age (criterion 9)
            continue
        write_text(os.path.join(out_dir, n), x)


def check_cache(cache, root=ROOT, out_dir=None):
    """The cache may be outside the repository, or inside it only under data/vintages/ (never in the committed output folder)."""
    real = os.path.realpath(os.path.expanduser(cache))
    rroot = os.path.realpath(root)
    if real == rroot or real.startswith(rroot + os.sep):
        outd = os.path.realpath(out_dir or os.path.join(root, "data", "rev_recognition_timing"))
        if real == outd or real.startswith(outd + os.sep):
            raise Refused("the cache may not live in the committed output folder")
        rel = os.path.relpath(real, rroot).replace(os.sep, "/") + "/"
        if not rel.startswith("data/vintages/"):
            raise Refused("a cache inside the repository must be under data/vintages/")
    return real


def run_build(a):
    t0 = time.time()
    out_dir = a.out
    cache = check_cache(a.cache, out_dir=out_dir)
    panel_path = a.panel or os.path.join(ROOT, PANEL_REL)
    ex = load_existing(out_dir)
    if a.stage == "pre" and any(r[0] == "S1" and r[3] == a.vintage for r in ex.get("registered", [])):
        raise Refused("vintage %s already has its S1 scored: a pre build would overwrite the full outputs with the pre subset" % a.vintage)
    texts, failed, c = finish(lambda: load_inputs(cache, out_dir, a.vintage, a.stage, panel_path, raw_dir=a.raw))
    write_outputs(texts, c, out_dir)
    print("vintage %s, stage %s: %d firms in the panel (%d distinct CIKs)" % (a.vintage, a.stage, c["inp"]["panel"]["rows"], len(c["order"])))
    if c["stage"] == "full":
        st, sc, scg = c["stats"]["primary"], c["sc"]["primary"], c["scg"]["primary"]
        print("== S1 (window fy2023_fy2025, primary, %d in-scope firms): T = %s USD of a change in net income of %s USD; share %s%% (%s); direction %s; qualifier %s" % (
            st["n"], usd(st["t"]), usd(st["dni"]), pct3(sc["share"]) or "blank", sc["label"], sc["direction"], sc["qualifier"]))
        print("== S1P (same firms): positive T %s USD; share %s%% (%s)" % (usd(st["tp"]), pct3(scg["share"]) or "blank", scg["label"]))
        print("== S2 and S2P: %s" % c["s2"]["phase"])
    else:
        print("== placebo windows written: %s" % ", ".join("%s n=%s" % (r[0], r[3]) for r in c["placebo_rows"]))
    if CONFLICTS:
        print("note: %d (firm, tag, year) cells state two different values in one filing and were treated as missing" % len(CONFLICTS))
    print("== checks")
    for r in c["checks"]:
        print("   %-4s %-5s %s" % (r[0], r[4], r[3][:200]))
    print("failed: %s; wrote %d files to %s (%.1f s)" % (", ".join(failed) or "none", len(texts), tilde(out_dir), time.time() - t0))
    return 1 if failed else 0


# ------------------------------------------------------------------------------------------------------------------------
# requests: the URL check (R1), the content tests (R3a) and the fetcher (R2, R3, R4)
# ------------------------------------------------------------------------------------------------------------------------
class SliceEnd(Exception):
    """The run's request cap (or --max-requests) is reached with work left (exit 4)."""


def check_url(url):
    """Only a plain https GET to data.sec.gov for a submissions file, a companyfacts file or a frame. www.sec.gov, efts.sec.gov and the Financial Statement and Notes ZIPs are refused
    before the request. Returns (host, path)."""
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    if M("g15_allow_other_host"):
        return host, p.path
    if p.scheme != "https" or p.username or p.password or p.port not in (None, 443) or p.fragment or p.query:
        raise Refused("only plain https URLs without a query are allowed")
    if host != HOST:
        if any(host == b or host.endswith("." + b) for b in BLOCKED_HOSTS):
            raise Refused("host %s is never requested (only %s is)" % (host, HOST))
        raise Refused("host %s is not on the allowlist" % host)
    if not (SUB_RX.match(p.path) or SUBPAGE_RX.match(p.path) or CF_RX.match(p.path) or FRAME_RX.match(p.path)):
        raise Refused("only submissions, companyfacts and frames paths are requested")
    return host, p.path


def real_opener(host, target, headers, timeout, cap):
    """GET https://host/target. Returns (status, body, response headers). No redirect is followed (a 3xx comes back as a status and latches), no cookies, the only verb is GET.
    A non-200 body is read up to ERR_CAP bytes (its head goes into the STOP file). Socket faults raise SocketFault."""
    conn = http.client.HTTPSConnection(host, timeout=timeout)
    try:
        conn.request("GET", target, headers=dict(headers))
        resp = conn.getresponse()
        status = resp.status
        hdrs = {k.lower(): v for k, v in resp.getheaders()}
        if status != 200:
            return status, resp.read(ERR_CAP), hdrs
        chunks, total = [], 0
        while True:
            b = resp.read(1 << 16)
            if not b:
                break
            total += len(b)
            if total > cap:
                return status, None, hdrs
            chunks.append(b)
        return status, b"".join(chunks), hdrs
    except (OSError, EOFError, http.client.HTTPException) as e:
        raise SocketFault(type(e).__name__)
    finally:
        conn.close()


def esc_head(body, n=300):
    return scrub((body or b"")[:n].decode("latin-1").encode("unicode_escape").decode("ascii"))


STOP_FIELDS = ("status", "utc_time", "url_path", "retry_after", "body_head")


def stop_fields(status, utc_time, url_path, retry_after, body_head):
    lines = ["status: %s" % status, "utc_time: %s" % utc_time, "url_path: %s" % url_path]
    if not M("g14_stop_short"):
        lines.append("retry_after: %s" % retry_after)
    lines.append("body_head: %s" % body_head)
    return "\n".join(lines) + "\n"


def stop_text_ok(text):
    return [l.split(":", 1)[0] for l in text.splitlines()] == list(STOP_FIELDS)


def create_stop(path, text):
    """The one place a STOP file is created: exclusive create ("x"), so an existing latch is never overwritten. The AST scan (G14) allows nothing else."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "x", encoding="utf-8") as fh:
            fh.write(text)
    except FileExistsError:
        if M("g14_overwrite"):
            _clobber(path, text)                  # the mutant: what create_stop must never do; run-time test only


def _clobber(p, text):
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


def looks_like_page(body):
    return body.lstrip()[:15].lower().startswith((b"<!", b"<html"))


def body_check(kind, body, expect):
    """R3a: a 200 body that is empty, a web page, not JSON or not the document asked for is a content failure. Returns (problem, document); document is the parsed body (plain floats; it is
    only looked at here) when there is no problem. expect: the CIK (submissions, companyfacts) or (tag, period) for a frame."""
    if not body and not M("g14_empty_ok"):
        return "empty body", None
    if body and looks_like_page(body) and not M("g14_html_ok"):
        return "the body is a web page", None
    try:
        doc = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        if M("g14_nonjson_ok"):
            return "", None
        return "the body is not JSON", None
    if not isinstance(doc, dict):
        return "the JSON body is not an object", None
    if kind == "submissions":
        ok = isinstance(doc.get("filings"), dict) and doc_cik(doc) == expect
    elif kind == "submissions_page":
        ok = isinstance(doc.get("accessionNumber"), list)
    elif kind == "companyfacts":
        ok = isinstance(doc.get("facts"), dict) and doc_cik(doc) == expect
    else:
        ok = isinstance(doc.get("data"), list) and doc.get("uom", "USD") == "USD" and doc.get("tag", expect[0]) == expect[0] and doc.get("ccp", expect[1]) == expect[1]
    return ("", doc) if ok else ("the body is valid JSON but not the document asked for", None)


def frame_count(doc, panel_ciks):
    """How many of the 500 CIKs a frame holds. pts is the number of filers in the whole frame and is never this count (G1)."""
    if M("g1_pts_count"):
        return int(doc.get("pts") or 0)
    return len({cik10(e.get("cik")) for e in doc.get("data") or []} & set(panel_ciks))


def fetch_vintage_ok(vintage, cache, now):
    """A vintage is today's UTC date or an existing vintage folder: the S2 date's gate cannot be opened by naming a future vintage."""
    if not vintage_ok(vintage):
        return False
    return vintage == now.strftime("%Y%m%d") or os.path.isdir(os.path.join(cache, vintage))


class Fetcher(object):
    """One host, GET only. Opener, sleeper and clock are injectable so every rule is testable without a network. The contact string is held in memory only and is registered as a secret,
    so nothing that would write it gets written."""

    def __init__(self, cache, out_dir, vintage, contact, stop_dir=STOP_DIR, opener=real_opener, sleeper=time.sleep, now_utc=None, root=ROOT, cap=None, max_requests=None, panel_ciks=()):
        if not contact or re.search(r"[\x00-\x1f]", contact):
            raise NoContact("SEC_UA is not set (or holds a control character)")
        try:
            contact.encode("latin-1")
        except UnicodeEncodeError:
            raise Refused("SEC_UA holds a character an HTTP header cannot carry (the value is not printed)")
        register_secret(contact)
        self.out_dir = out_dir
        self.cache = check_cache(cache, root=root, out_dir=out_dir)
        self.vintage = vintage
        self.vdir = os.path.join(self.cache, vintage)
        self.raw = os.path.join(self.vdir, "raw")
        self.stop_dir = stop_dir
        self.headers = {"User-Agent": contact, "Accept-Encoding": "identity", "Accept": "application/json"}
        self.opener, self.sleeper = opener, sleeper
        self.now_utc = now_utc or (lambda: dt.datetime.now(dt.timezone.utc))
        self.cap = cap
        self.max_requests = max_requests
        self.requests = 0
        self.panel_ciks = tuple(panel_ciks)
        self.log_path = os.path.join(out_dir, "fetch_log.csv")
        self.vint_path = os.path.join(out_dir, "vintages.csv")
        self.log = [list(r.values()) for r in fetch_rows(out_dir)]
        self.vint_all = [list(r.values()) for r in vint_rows(out_dir)]
        self.vint = {r[1]: r for r in self.vint_all if r[0] == vintage}
        self.last_end = None
        if self.log:
            last = self.log[-1]
            try:
                self.last_end = parse_utc_ms(last[0]) + dt.timedelta(seconds=float(last[7] or 0))
            except ValueError:
                self.last_end = None

    def stop_path(self):
        return os.path.join(self.stop_dir, STOP_NAME)

    def check_stop(self):
        if os.path.exists(self.stop_path()) and not M("g14_stop_ignored"):
            raise Latched("STOP present: %s" % tilde(self.stop_path()))

    def limit(self):
        lim = [x for x in (self.cap, self.max_requests) if x is not None]
        return min(lim) if lim else None

    def _write_logs(self):
        write_text(self.log_path, render_csv("fetch_log.csv", self.log, "# source: request log of bin/rev_recognition_timing.py fetch modes against %s; one row per request" % HOST))
        write_text(self.vint_path, render_csv("vintages.csv", self.vint_all, "# source: replies kept by bin/rev_recognition_timing.py fetch modes against %s; one row per body kept or 404 recorded" % HOST))

    def _pace(self):
        gap = 0.9 if M("g15_gap_09") else MIN_GAP
        if self.last_end is not None:
            wait = gap - (self.now_utc() - self.last_end).total_seconds()
            if wait > 0:
                self.sleeper(wait)

    def _latch(self, status, path, retry_after, body, why):
        create_stop(self.stop_path(), stop_fields(status, utc_ms(self.now_utc()), path, retry_after or "", esc_head(body)))
        raise Latched("STOP written: %s (%s)" % (tilde(self.stop_path()), why))

    def _get(self, path):
        check_url("https://" + HOST + path)
        self._pace()
        started = self.now_utc()
        self.requests += 1
        try:
            status, body, hdrs = self.opener(HOST, path, dict(self.headers), TIMEOUT, BODY_CAP)
        except SocketFault:
            ended = self.now_utc()
            self.log.append([utc_ms(started), self.vintage, HOST, path, "0", "0", "", "%.3f" % (ended - started).total_seconds()])
            self.last_end = ended
            self._write_logs()
            if M("g14_stop_on_timeout"):
                create_stop(self.stop_path(), stop_fields("timeout", utc_ms(ended), path, "", ""))
            raise
        ended = self.now_utc()
        self.last_end = ended
        return status, body, hdrs, started, ended

    def _row(self, started, ended, path, status, body):
        n = len(body) if body is not None else 0
        self.log.append([utc_ms(started), self.vintage, HOST, path, str(status), str(n), sha256_of(body) if body else "", "%.3f" % (ended - started).total_seconds()])

    def obtain(self, path, kind, expect):
        """The body for a path: ('cached', body) when raw/ already holds it with its vintages.csv digest (no request), ('200', body) after a request, ('404', None) for an absent frame or a
        firm without a record. Everything else latches STOP. A body in raw/ that differs from its row is refused, never fetched over."""
        rn = raw_name(path)
        row = self.vint.get(path)
        if row is not None and not M("g15_recache"):
            if row[2] == "404":
                return "404", None
            p = os.path.join(self.raw, rn)
            if row[2] == "200" and os.path.isfile(p):
                b = read_file(p, "rb")
                if sha256_of(b) == row[4] and str(len(b)) == row[3]:
                    return "cached", b
                raise Refused("the cached body of %s does not match its vintages.csv row; nothing is fetched over it" % rn)
        self.check_stop()
        lim = self.limit()
        if lim is not None and self.requests >= lim and not M("g15_cap_off"):
            raise SliceEnd("the cap of %d requests is reached" % lim)
        status, body, hdrs, started, ended = self._get(path)
        if status in (429, 500) and M("g15_retry"):
            self._row(started, ended, path, status, body)
            status, body, hdrs, started, ended = self._get(path)
        if status == 404 and kind != "submissions_page" and not M("g14_404_latches"):
            self._row(started, ended, path, 404, body)
            self.vint_all = [r for r in self.vint_all if not (r[0] == self.vintage and r[1] == path)]
            row = [self.vintage, path, "404", str(len(body or b"")), sha256_of(body or b""), utc_ms(ended)]
            self.vint_all.append(row)
            self.vint[path] = row
            self._write_logs()
            return "404", None
        if status != 200:
            self._row(started, ended, path, status, body)
            self._write_logs()
            if status // 100 == 3 and M("g14_3xx_ignored"):
                return "404", None
            if status // 100 == 3 and M("g15_redirect_follow"):
                status, body, hdrs, started, ended = self._get(urlsplit(hdrs.get("location", path)).path or path)
            else:
                self._latch(status, path, hdrs.get("retry-after", ""), body, "HTTP %s" % status)
        if body is None:
            self._row(started, ended, path, status, body)
            self._write_logs()
            self._latch(status, path, "", b"", "body larger than the cap")
        self._row(started, ended, path, status, body)
        prob, _ = body_check(kind, body, expect)
        if prob:
            self._write_logs()
            self._latch(status, path, "", body, "content test: %s" % prob)
        write_bytes(os.path.join(self.raw, rn), body)
        self.vint_all = [r for r in self.vint_all if not (r[0] == self.vintage and r[1] == path)]
        row = [self.vintage, path, "200", str(len(body)), sha256_of(body), utc_ms(ended)]
        self.vint_all.append(row)
        self.vint[path] = row
        self._write_logs()
        return "200", body


# ---- the three fetch modes ----
def mode_submissions(fe, order, say):
    """The 500 submissions files plus the older pages that can hold a 10-K reported from 2019-04-01 on; then submissions_extract.csv."""
    for cik in order:
        st, body = fe.obtain("/submissions/CIK%s.json" % cik, "submissions", cik)
        if st == "404":
            continue
        for name in older_pages(cik, json.loads(body.decode("utf-8"))):
            fe.obtain("/submissions/" + name, "submissions_page", cik)
    rows = []
    for cik in order:
        row = fe.vint.get("/submissions/CIK%s.json" % cik)
        if row is None or row[2] == "404":
            continue
        main = parse_json(read_file(os.path.join(fe.raw, "submissions", "CIK%s.json" % cik), "rb"))
        pages = []
        for name in older_pages(cik, main):
            pages.append(parse_json(read_file(os.path.join(fe.raw, "submissions", name), "rb")))
        rows += submissions_rows(fe.vintage, cik, main, pages)
    write_text(os.path.join(fe.vdir, "submissions_extract.csv"), render_csv("submissions_extract.csv", rows, source_line_vintage(fe.vintage, "submissions extract: the original 10-K family from 2019-04-01, for the 500 CIKs only")))
    say("submissions_extract.csv: %d rows for %d CIKs" % (len(rows), len({r[1] for r in rows})))


def mode_companyfacts(fe, order, say):
    """The companyfacts file of every firm with a submissions record; then cf_extract.csv (needs the submissions extract for each firm's D_Y)."""
    path = os.path.join(fe.vdir, "submissions_extract.csv")
    if not os.path.isfile(path):
        raise Refused("submissions_extract.csv is missing: run fetch-submissions first")
    subs = load_submissions(path, "full", fe.vintage)
    for cik in order:
        srow = fe.vint.get("/submissions/CIK%s.json" % cik)
        if srow is None:
            raise Refused("vintages.csv has no submissions row for %s: run fetch-submissions to the end first" % cik)
        if srow[2] == "404":
            continue
        fe.obtain("/api/xbrl/companyfacts/CIK%s.json" % cik, "companyfacts", cik)
    rows = []
    for cik in order:
        row = fe.vint.get("/api/xbrl/companyfacts/CIK%s.json" % cik)
        if row is None or row[2] == "404":
            continue
        ym = year_map(subs.get(cik, {"filings": []})["filings"])
        dmap = {y: year_info(ym, y)[1] for y in ALL_YEARS if year_info(ym, y)[0] == "one"}
        doc = parse_json(read_file(os.path.join(fe.raw, "companyfacts", "CIK%s.json" % cik), "rb"))
        rows += companyfacts_rows(fe.vintage, cik, doc, dmap)
    write_text(os.path.join(fe.vdir, "cf_extract.csv"), render_csv("cf_extract.csv", rows, source_line_vintage(fe.vintage, "companyfacts extract: USD facts of the tags of 2.4 ending within 7 days of a needed D_Y")))
    say("cf_extract.csv: %d rows for %d CIKs" % (len(rows), len({r[1] for r in rows})))


def mode_frames(fe, order, say):
    """The frames of the plan, for coverage and checks only; then frames_extract.csv."""
    plan = frame_plan(fe.vintage)
    for tag, period in plan:
        if not frame_period_ok(period, fe.vintage):
            raise Refused("the frame %s is not fetched before %s" % (period, S2_DATE))
    pset = set(order)
    for tag, period in plan:
        st, body = fe.obtain(frame_path(tag, period), "frames", (tag, period))
        if st != "404" and body is not None:
            say("frame %s %s: %d of the 500 CIKs" % (tag, period, frame_count(json.loads(body.decode("utf-8")), pset)))
        else:
            say("frame %s %s: absent (404)" % (tag, period))
    rows = []
    for tag, period in plan:
        row = fe.vint.get(frame_path(tag, period))
        if row is None or row[2] == "404":
            continue
        doc = parse_json(read_file(os.path.join(fe.raw, "frames", "%s__%s.json" % (tag, period)), "rb"))
        rows += frame_rows(fe.vintage, tag, period, doc, pset)
    write_text(os.path.join(fe.vdir, "frames_extract.csv"), render_csv("frames_extract.csv", rows, source_line_vintage(fe.vintage, "frames extract: the facts of the 500 CIKs, for coverage and checks only")))
    say("frames_extract.csv: %d rows" % len(rows))


MODES = {"fetch-submissions": ("submissions", mode_submissions), "fetch-companyfacts": ("companyfacts", mode_companyfacts), "fetch-frames": ("frames", mode_frames)}


def run_fetch(a, environ=None, opener=real_opener, sleeper=time.sleep, now_utc=None, say=print, stop_dir=STOP_DIR):
    """Returns the exit code: 0 done, 2 STOP present or written (or no contact string), 3 network fault, 4 the cap or --max-requests reached with work left, 5 refused."""
    environ = os.environ if environ is None else environ
    contact = (environ.get("SEC_UA") or "").strip()
    if not contact and M("g15_no_contact_ok"):
        contact = "anonymous"                                    # the mutant: a fetch that runs without a declared contact
    if not contact:
        say("SEC_UA is not set: a fetch refuses to run (set it to the declared contact; its value is never printed or written)")
        return 2
    now = (now_utc or (lambda: dt.datetime.now(dt.timezone.utc)))()
    cache = check_cache(a.cache, out_dir=a.out)
    if not fetch_vintage_ok(a.vintage, cache, now):
        raise Refused("--vintage must be today's UTC date (%s) or an existing vintage folder" % now.strftime("%Y%m%d"))
    mode = a.cmd
    kind, fn = MODES[mode]
    panel = read_panel(a.panel or os.path.join(ROOT, PANEL_REL))
    fe = Fetcher(cache, a.out, a.vintage, contact, stop_dir=stop_dir, opener=opener, sleeper=sleeper, now_utc=now_utc, cap=CAPS[kind], max_requests=a.max_requests, panel_ciks=panel["order"])
    try:
        fe.check_stop()
        os.makedirs(a.out, exist_ok=True)
        fn(fe, panel["order"], say)
        say("%s: done; requests sent in this invocation: %d" % (mode, fe.requests))
        return 0
    except Latched as e:
        say(str(e))
        return 2
    except SliceEnd as e:
        say("%s: %s; run it again to resume (a body already kept is not requested again); requests sent: %d" % (mode, e, fe.requests))
        return 4
    except SocketFault:
        say("FAIL network: the run ends; nothing was latched and nothing is retried")
        return 3


# ------------------------------------------------------------------------------------------------------------------------
# static scans of this script's own source: the STOP latch (G14) and isolation (G19)
# ------------------------------------------------------------------------------------------------------------------------
REMOVERS = {"remove", "unlink", "rmtree", "rmdir"}
MUTATORS = {"replace", "rename", "move", "write_text", "write_bytes", "truncate", "copy", "copyfile", "copy2", "symlink", "link"}


def _mentions_stop(node, tainted):
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and ("stop" in n.id.lower() or n.id in tainted):
            return True
        if isinstance(n, ast.Attribute) and "stop" in n.attr.lower():
            return True
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and "stop" in n.value.lower():
            return True
    return False


def _fname(call):
    f = call.func
    return f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")


def _open_mode(call):
    """The mode of an open() call: the literal string, '' when absent (read), None when it is not a literal."""
    node = call.args[1] if len(call.args) > 1 else next((k.value for k in call.keywords if k.arg == "mode"), None)
    if node is None:
        return ""
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _scope_nodes(scope):
    """The nodes of one scope, not descending into nested functions (each function is scanned as its own scope)."""
    out, stack = [], [scope]
    while stack:
        n = stack.pop()
        out.append(n)
        for ch in ast.iter_child_nodes(n):
            if not isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                stack.append(ch)
    return out


def _taint(nodes, mentions):
    tainted = set()
    for _ in range(3):
        for n in nodes:
            tgt, val = None, None
            if isinstance(n, ast.Assign):
                tgt, val = n.targets, n.value
            elif isinstance(n, (ast.AnnAssign, ast.AugAssign)) and n.value is not None:
                tgt, val = [n.target], n.value
            elif isinstance(n, ast.For):
                tgt, val = [n.target], n.iter
            if val is not None and mentions(val, tainted):
                for t in tgt:
                    for x in ast.walk(t):
                        if isinstance(x, ast.Name):
                            tainted.add(x.id)
    return tainted


def stop_ast_problems(src):
    """G14: an AST scan. A STOP path may be reached only by create_stop, with open(path, "x"). No function removes, renames over or truncates anything that reaches a STOP path."""
    if M("g14_scan_off"):
        return []
    tree = ast.parse(src)
    problems = set()
    scopes = [(n.name, n) for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))] + [("<module>", tree)]
    for fname, scope in scopes:
        nodes = _scope_nodes(scope)
        tainted = _taint(nodes, _mentions_stop)
        for call in [n for n in nodes if isinstance(n, ast.Call)]:
            nm = _fname(call)
            where = "%s line %d" % (fname, call.lineno)
            if fname == "create_stop" and nm in ("open", "fdopen") and _open_mode(call) != "x" and not M("g14_ignore_open"):
                problems.add("%s: create_stop opens a file in mode %r (only exclusive create, \"x\", is allowed)" % (where, _open_mode(call)))
            reach = any(_mentions_stop(a, tainted) for a in list(call.args) + [k.value for k in call.keywords]) or (
                isinstance(call.func, ast.Attribute) and _mentions_stop(call.func.value, tainted))
            if nm in REMOVERS:
                problems.add("%s: %s (this script removes nothing)" % (where, nm))
            elif nm in MUTATORS and reach and not (nm == "replace" and M("g14_replace_ok")):
                problems.add("%s: %s reaches a STOP path" % (where, nm))
            elif nm in ("open", "fdopen") and reach and not M("g14_ignore_open"):
                mode = _open_mode(call)
                if not (fname == "create_stop" and mode == "x") and (mode is None or any(ch in mode for ch in "wax+")):
                    problems.add("%s: open in mode %r reaches a STOP path" % (where, mode))
    return sorted(problems)


FORBIDDEN_FRAGMENTS = ("series.tsv", "data/history", "calendar.tsv", "handover.tsv", "the_ask", "research_state", "dropbox", "secrets.env", "w3_tax/results", "keys/")
ALLOWED_DATA_PREFIXES = ("data/rev_recognition_timing", "data/vintages/rev_recognition_timing", PANEL_REL)
PATH_CALLS = {"open", "read_file", "read_csv_rows", "join", "exists", "listdir", "isdir", "isfile", "write_text", "write_bytes", "makedirs", "glob", "walk", "read_panel", "load_submissions", "load_cf", "load_frames"}


def isolation_problems(src):
    """G19: the script opens the panel and its own two folders only. No path call names another project file, an absolute path or a parent directory."""
    if M("g19_scan_off"):
        return []
    tree = ast.parse(src)
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _fname(node) in PATH_CALLS:
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Constant):
                continue                                  # "sep".join(...)
            for a in list(node.args) + [k.value for k in node.keywords]:
                for s in ast.walk(a):
                    if isinstance(s, ast.Constant) and isinstance(s.value, str):
                        v = s.value
                        low = v.lower()
                        if any(fr in low for fr in FORBIDDEN_FRAGMENTS):
                            out.add("line %d: %s(...) names %r" % (node.lineno, _fname(node), v))
                        elif "data/" in low and not any(low.startswith(p) for p in ALLOWED_DATA_PREFIXES) and not M("g19_prefix_ok"):
                            out.add("line %d: %s(...) names the project path %r" % (node.lineno, _fname(node), v))
                        elif _fname(node) in ("open", "read_file", "read_csv_rows") and (v.startswith("/") or ".." in v):
                            out.add("line %d: %s(...) opens the absolute or parent path %r" % (node.lineno, _fname(node), v))
    return sorted(out)


# ------------------------------------------------------------------------------------------------------------------------
# selftest: synthetic data only. Every guard G1-G19 of the spec's section 7 has a test; each mutant (a deliberately broken variant, switched on in this process only) must make its
# guard's test fail. A mutant that is not caught is a failure.
# ------------------------------------------------------------------------------------------------------------------------
class Checks(object):
    def __init__(self):
        self.items = []

    def ok(self, name, cond, detail=""):
        self.items.append((name, bool(cond), "" if cond else detail))

    def eq(self, name, got, want):
        self.ok(name, got == want, "got %r, want %r" % (got, want))

    def raises(self, name, exc, fn):
        try:
            fn()
        except exc:
            self.ok(name, True)
        except Exception as e:
            self.ok(name, False, "raised %s: %s" % (type(e).__name__, e))
        else:
            self.ok(name, False, "did not raise")

    def quiet(self, name, fn):
        try:
            fn()
        except Exception as e:
            self.ok(name, False, "raised %s: %s" % (type(e).__name__, e))
        else:
            self.ok(name, True)

    def failed(self):
        return [(n, d) for n, c, d in self.items if not c]


class FakeClock(object):
    """A clock that only moves when the code sleeps (so the pacing of the fetcher is testable)."""

    def __init__(self, t=1_800_000_000.0):                       # 2027-01-15 08:00:00 UTC
        self.t = t

    def sleep(self, s):
        self.t += s

    def now_utc(self):
        return dt.datetime.fromtimestamp(self.t, dt.timezone.utc)


FIXTURE_CONTACT = "Fixture Research Contact 7Q2X-91 (selftest)"        # a made-up contact string with no address; the tests look for it in every byte written


def Dm(x):
    return Decimal(x)


# ---- unit-test builders ----
def tfact(start, end, val, accn, filed="2024-02-20", fy="2023", form="10-K", fp="FY"):
    return (start, end, Decimal(val), accn, form, fp, fy, filed)


def dec_filings(years=range(2019, 2027)):
    """One original 10-K for each December fiscal year: reportDate Y-12-31, accession ACC-Y."""
    return [("10-K", "%d-12-31" % y, "%d-02-20" % (y + 1), "ACC-%d" % y) for y in years]


def own_instant(tag, y, val, accn=None, end=None):
    return tfact("", end or "%d-12-31" % y, val, accn or "ACC-%d" % y, filed="%d-02-20" % (y + 1), fy=str(y))


def own_duration(tag, y, val, accn=None, span=364, end=None):
    e = end or "%d-12-31" % y
    return tfact(add_days(e, -span), e, val, accn or "ACC-%d" % y, filed="%d-02-20" % (y + 1), fy=str(y))


def mkfirm(facts_by_tag, filings=None, cik="0000000001", sic="3571", fye="1231", name="Synth Corp", tickers=("SYN",), no_record=False):
    return Firm(cik, tickers, name, sic, fye, no_record, filings if filings is not None else dec_filings(), facts_by_tag)


def inst_series(tag, vals, years=range(2019, 2027)):
    return {tag: [own_instant(tag, y, v) for y, v in zip(years, vals) if v is not None]}


def dur_series(tag, vals, years=range(2019, 2027)):
    return {tag: [own_duration(tag, y, v) for y, v in zip(years, vals) if v is not None]}


def merge(*ds):
    out = {}
    for d in ds:
        out.update(d)
    return out


# ---- an independent reference for the arithmetic (Fractions, written a second time) ----
def ref_T(N, R, b, e):
    """T = AA_e - AA_b with AA_t = N_t - (N_(t-1) / R_(t-1)) * R_t, in exact fractions; N and R are dicts year -> number."""
    from fractions import Fraction as Fr
    def aa(t):
        return Fr(N[t]) - Fr(N[t - 1]) / Fr(R[t - 1]) * Fr(R[t])
    return aa(e) - aa(b)


def fr_to_dec(f):
    return Decimal(f.numerator) / Decimal(f.denominator)


# ---- the synthetic world: nineteen firms, one vintage, built through the production extraction code ----
M_ = 1000000


def lin(base, step_pct, n=8, bump=None):
    """Eight yearly values (2019..2026): base grown by step_pct a year, in whole dollars; bump {index: add}."""
    out = []
    for k in range(n):
        v = base * (100 + step_pct * k) // 100
        v += (bump or {}).get(k, 0)
        out.append(v)
    return out


def spec(cik, tickers, **kw):
    d = {"cik": cik, "tickers": list(tickers), "sic": "3571", "fye": "1231", "name": "SYNTH %s CORP" % cik[-4:], "ends": {y: "%d-12-31" % y for y in range(2019, 2026)}, "vals": {}, "later": {}, "drop": set(),
         "shift": {}, "extra_tenk": [], "no_record": False}
    d.update(kw)
    d["ends"] = dict(d["ends"])
    d.setdefault("later2", {})
    d.setdefault("no_comp", set())
    return d


def world_specs(fy2026=False):
    dec = {y: "%d-12-31" % y for y in range(2019, 2026)}
    if fy2026:
        dec[2026] = "2026-12-31"
    june = {y: "%d-06-30" % y for y in range(2019, 2027)}
    jan = {2019: "2020-02-01", 2020: "2021-01-30", 2021: "2022-01-29", 2022: "2023-01-28", 2023: "2024-02-03", 2024: "2025-02-01", 2025: "2026-01-31"}
    if fy2026:
        jan[2026] = "2027-01-30"
    S = []
    rev = lin(1000 * M_, 10)
    S.append(spec("0000789019", ["MSFT"], fye="0630", ends=june, filed_offset=29, vals={REV_R2: rev, NI_TAG: lin(100 * M_, 12), CL_T: lin(100 * M_, 14, bump={4: 30 * M_}), CL_C: lin(100 * M_, 14, bump={4: 30 * M_}),
                                                                        CA_T: lin(20 * M_, 15), AR_A1: [r * (20 + k) // 100 for k, r in enumerate(rev)], CC_TAG: [r // 20 for r in rev], RPO_TAG: [2 * r for r in rev]}))
    rev = lin(3000 * M_, 8)
    S.append(spec("0000320193", ["AAPL", "AAPX"], ends=dec, vals={REV_R3: rev, NI_TAG: lin(300 * M_, 7), CL_C: lin(200 * M_, 9), CL_N: lin(50 * M_, 6)}))
    rev = lin(2000 * M_, 9)
    S.append(spec("0001018724", ["AMZN"], ends=dec, no_comp={(DEF_C, 2024)}, vals={REV_R2: rev, NI_TAG: lin(150 * M_, 8), DEF_C: lin(80 * M_, 10), DEF_N: lin(10 * M_, 8)}))
    S.append(spec("0000100001", ["NOCT"], ends=dec, vals={REV_R2: lin(500 * M_, 5), NI_TAG: lin(50 * M_, 5)}))
    rtl_rev = lin(800 * M_, 4)
    S.append(spec("0000100002", ["RTL"], fye="0131", ends=jan, later={(REV_R2, 2022): rtl_rev[3] * 6 // 10}, later2={(REV_R2, 2022): rtl_rev[3] * 5 // 10},
                  vals={REV_R2: rtl_rev, NI_TAG: lin(40 * M_, 4), CL_T: lin(30 * M_, 9)}))
    S.append(spec("0000100003", ["BANK"], sic="6021", ends=dec, vals={REV_R2: lin(900 * M_, 4), NI_TAG: lin(90 * M_, 4)}))
    S.append(spec("0000100004", ["NOSIC"], sic="", ends=dec, vals={REV_R2: lin(900 * M_, 4), NI_TAG: lin(90 * M_, 4)}))
    S.append(spec("0000100005", ["GONE"], ends=dec, no_record=True))
    S.append(spec("0000100006", ["AMBI"], ends=dec, extra_tenk=[("10-K", "2021-12-15", "2022-01-30", "0000100006-22-900001")], vals={REV_R2: lin(700 * M_, 6), NI_TAG: lin(70 * M_, 6), CL_T: lin(40 * M_, 8)}))
    S.append(spec("0000100007", ["MISM"], ends=dec, shift={CL_T: 3}, vals={REV_R2: lin(700 * M_, 6), NI_TAG: lin(70 * M_, 6), CL_T: lin(40 * M_, 8)}))
    S.append(spec("0000100008", ["NOGN"], ends=dec, drop={(NI_TAG, 2022)}, vals={REV_R2: lin(700 * M_, 6), NI_TAG: lin(70 * M_, 6), CL_T: lin(40 * M_, 8)}))
    S.append(spec("0000100009", ["TINY"], ends=dec, vals={REV_R2: lin(50 * M_, 6), NI_TAG: lin(5 * M_, 6), CL_T: lin(4 * M_, 8)}))
    S.append(spec("0000100010", ["GAPN"], ends=dec, drop={(CL_T, y) for y in (2019, 2020, 2021, 2022)}, vals={REV_R2: lin(700 * M_, 6), NI_TAG: lin(70 * M_, 6), CL_T: lin(40 * M_, 8)}))
    S.append(spec("0000100011", ["RVFB"], ends=dec, vals={REV_ANY: lin(600 * M_, 6), NI_TAG: lin(60 * M_, 6), CL_T: lin(35 * M_, 8)}))
    rev = lin(1200 * M_, 6)
    S.append(spec("0000100012", ["ACQR"], ends=dec, vals={REV_R2: rev, NI_TAG: lin(120 * M_, 6), CL_T: lin(60 * M_, 8), ACQ_TAG: [r * 5 // 100 for r in rev]}))
    S.append(spec("0000100013", ["DISC"], ends=dec, vals={REV_R2: lin(650 * M_, 6), NI_TAG: lin(65 * M_, 6), CL_T: lin(30 * M_, 8), DISC_TAG: [0, 0, 0, 0, 0, 3 * M_, 0, 0]}))
    rev = lin(400 * M_, 5)
    S.append(spec("0000100014", ["XTRM"], ends=dec, vals={REV_R2: rev, NI_TAG: lin(40 * M_, 5), CL_T: [2 * r for r in rev]}))
    S.append(spec("0000100015", ["TGP"], ends=dec, vals={REV_R2: lin(900 * M_, 5), NI_TAG: lin(80 * M_, 5), CL_T: lin(100 * M_, 6), CL_C: lin(60 * M_, 6)}))
    S.append(spec("0000100016", ["TLP"], ends=dec, vals={REV_R2: lin(950 * M_, 5), NI_TAG: lin(85 * M_, 5), CL_T: lin(100 * M_, 6, bump={5: -30 * M_}), CL_C: lin(60 * M_, 6), CL_N: lin(40 * M_, 6)}))
    return S


def filed_of(sp, y):
    return add_days(sp["ends"][y], sp.get("filed_offset", 45))


def acc_of(cik, y):
    return "%s-%02d-000001" % (cik, y % 100)


def facts_doc(sp, vintage):
    """A companyfacts-shaped document for one synthetic firm: each value as the firm's own 10-K states it, and again (restated if sp['later'] says so) in the next year's 10-K."""
    gaap = {}
    for tag, vals in sp["vals"].items():
        for k, v in enumerate(vals):
            y = 2019 + k
            if y not in sp["ends"] or (tag, y) in sp["drop"]:
                continue
            srcs = [(y, v)]
            if (tag, y) not in sp["no_comp"]:
                srcs.append((y + 1, sp["later"].get((tag, y), v)))
            if (tag, y) in sp["later2"]:
                srcs.append((y + 2, sp["later2"][(tag, y)]))
            for src_y, val in srcs:
                if src_y not in sp["ends"]:
                    continue
                end = add_days(sp["ends"][y], sp["shift"].get(tag, 0))
                e = {"end": end, "val": Decimal(val), "accn": acc_of(sp["cik"], src_y), "fy": Decimal(src_y), "fp": "FY", "form": "10-K", "filed": filed_of(sp, src_y)}
                if tag in DURATION_TAGS:
                    e["start"] = add_days(sp["ends"][y], -364 + sp["shift"].get(tag, 0))
                gaap.setdefault(tag, {"units": {"USD": []}})["units"]["USD"].append(e)
    return {"cik": Decimal(int(sp["cik"])), "entityName": sp["name"], "facts": {"us-gaap": gaap}}


def subs_doc(sp):
    rows = [("10-K", sp["ends"][y], filed_of(sp, y), acc_of(sp["cik"], y)) for y in sorted(sp["ends"])] + list(sp["extra_tenk"])
    rows.append(("10-K/A", add_days(sp["ends"][2022], 0), "2023-09-01", "AMEND-%s" % sp["cik"]))
    rows.append(("8-K", "", "2023-09-02", "OTHER-%s" % sp["cik"]))
    block = {"form": [r[0] for r in rows], "reportDate": [r[1] for r in rows], "filingDate": [r[2] for r in rows], "accessionNumber": [r[3] for r in rows]}
    return {"cik": sp["cik"], "name": sp["name"], "sic": sp["sic"], "fiscalYearEnd": sp["fye"], "filings": {"recent": block, "files": []}}


def frames_docs(specs, vintage):
    """{(tag, period): document}: the synthetic firms' latest-filed values at CY2019, CY2023, CY2025 (and the plan's other tags)."""
    out = {}
    for tag, period in frame_plan(vintage):
        y = frame_year(period)
        data = []
        for sp in specs:
            if sp["no_record"] or tag not in sp["vals"] or y not in sp["ends"] or (tag, y) in sp["drop"]:
                continue
            v = sp["later"].get((tag, y), sp["vals"][tag][y - 2019])
            e = {"accn": acc_of(sp["cik"], y + 1 if y + 1 in sp["ends"] else y), "cik": Decimal(int(sp["cik"])), "entityName": sp["name"], "loc": "US-WA", "end": add_days(sp["ends"][y], sp["shift"].get(tag, 0)), "val": Decimal(v)}
            if tag in DURATION_TAGS:
                e["start"] = add_days(sp["ends"][y], -364)
            data.append(e)
        out[(tag, period)] = {"taxonomy": "us-gaap", "tag": tag, "ccp": period, "uom": "USD", "pts": Decimal(5000), "data": data}
    return out


def make_world(tmp, vintage="20261105", fy2026=False, tweak=None):
    """Write a complete synthetic cache and output folder (extracts made by the production extraction functions) and return the paths."""
    specs = world_specs(fy2026)
    if tweak:
        tweak(specs)
    cache, out = os.path.join(tmp, "cache"), os.path.join(tmp, "out")
    vdir = os.path.join(cache, vintage)
    raw = os.path.join(vdir, "raw")
    panel = os.path.join(tmp, "panel.csv")
    lines = ["ticker,cik10,status"] + ["%s,%s,ok" % (t, sp["cik"]) for sp in specs for t in sp["tickers"]]
    write_text(panel, "\n".join(lines) + "\n")
    pset = {sp["cik"] for sp in specs}
    srows, cfrows, vrows, frows = [], [], [], []
    now = "2026-11-05T09:00:00.000Z"

    def keep(path, body_obj):
        body = json.dumps(body_obj, default=str).encode("utf-8")
        write_bytes(os.path.join(raw, raw_name(path)), body)
        vrows.append([vintage, path, "200", str(len(body)), sha256_of(body), now])

    for sp in specs:
        spath = "/submissions/CIK%s.json" % sp["cik"]
        if sp["no_record"]:
            vrows.append([vintage, spath, "404", "366", sha256_of(b"nokey"), now])
            continue
        sd = subs_doc(sp)
        keep(spath, {"cik": sp["cik"], "name": sp["name"]})
        srows += submissions_rows(vintage, sp["cik"], sd, [])
        fd = facts_doc(sp, vintage)
        ym = year_map([(r[4], r[5], r[6], r[7]) for r in submissions_rows(vintage, sp["cik"], sd, []) if r[4]])
        dmap = {y: year_info(ym, y)[1] for y in ALL_YEARS if year_info(ym, y)[0] == "one"}
        cfrows += companyfacts_rows(vintage, sp["cik"], fd, dmap)
        keep("/api/xbrl/companyfacts/CIK%s.json" % sp["cik"], {"cik": sp["cik"], "facts": {}})
    for (tag, period), doc in frames_docs(specs, vintage).items():
        keep(frame_path(tag, period), {"tag": tag, "ccp": period, "uom": "USD", "data": []})
        frows += frame_rows(vintage, tag, period, doc, pset)
    os.makedirs(vdir, exist_ok=True)
    write_text(os.path.join(vdir, "submissions_extract.csv"), render_csv("submissions_extract.csv", srows, source_line_vintage(vintage, "test")))
    write_text(os.path.join(vdir, "cf_extract.csv"), render_csv("cf_extract.csv", cfrows, source_line_vintage(vintage, "test")))
    write_text(os.path.join(vdir, "frames_extract.csv"), render_csv("frames_extract.csv", frows, source_line_vintage(vintage, "test")))
    os.makedirs(out, exist_ok=True)
    write_text(os.path.join(out, "vintages.csv"), render_csv("vintages.csv", vrows, "# source: test"))
    lg = [["2026-11-05T08:00:00.000Z", vintage, HOST, r[1], r[2], r[3], r[4], "0.100"] for r in vrows[:3]]
    write_text(os.path.join(out, "fetch_log.csv"), render_csv("fetch_log.csv", lg, "# source: test"))
    pan = read_panel(panel)
    pin = {"sha256": pan["sha"], "bytes": pan["bytes"], "rows": pan["rows"], "ciks": len(pan["order"]), "shared": collections.OrderedDict([("0000320193", ("AAPL", "AAPX"))])}
    return {"cache": cache, "out": out, "vdir": vdir, "panel": panel, "pin": pin, "specs": specs, "vintage": vintage, "raw": raw, "tmp": tmp}


def world_loader(w, stage, vintage=None):
    return lambda: load_inputs(w["cache"], w["out"], vintage or w["vintage"], stage, w["panel"], pin=w["pin"], raw_dir=w["raw"])


def build_world(w, stage, vintage=None):
    """finish() then write: returns (texts, failed, c)."""
    texts, failed, c = finish(world_loader(w, stage, vintage))
    write_outputs(texts, c, w["out"])
    return texts, failed, c


_WORLD = {}


def get_world():
    """The default synthetic world, built once with no mutant active (a mutant changes how a build reads it, never the files)."""
    if "w" not in _WORLD:
        td = tempfile.TemporaryDirectory(prefix="rrt_world_", ignore_cleanup_errors=True)
        _WORLD["td"] = td
        _WORLD["w"] = make_world(td.name)
    return _WORLD["w"]


def new_dir(w, name):
    return tempfile.mkdtemp(prefix="w_%s_" % name, dir=_WORLD["td"].name)


def copy_world(w, name):
    """A fresh copy of the default world's files in its own folder (so a test can build into it)."""
    dst = new_dir(w, name)
    shutil.copytree(os.path.join(w["tmp"], "cache"), os.path.join(dst, "cache"))
    shutil.copytree(os.path.join(w["tmp"], "out"), os.path.join(dst, "out"))
    w2 = dict(w)
    w2.update({"cache": os.path.join(dst, "cache"), "out": os.path.join(dst, "out"), "vdir": os.path.join(dst, "cache", w["vintage"]), "raw": os.path.join(dst, "cache", w["vintage"], "raw"), "tmp": dst})
    return w2


# ---- G1 to G9: parsing, fiscal years, fact selection, structure, statuses, labels, exclusions, the S2 gate, contributors ----
def quick_firm(rev, ni, cl=None, ca=None, cl_later=None, rev_later=None, extra=None, filings=None, cik="0000000001", sic="3571"):
    """A December-year firm from eight yearly lists (2019..2026): revenue (R2), net income, contract liabilities (total), contract assets (total); a later-filed restatement for the rest."""
    f = {}
    f.update(dur_series(REV_R2, rev))
    f.update(dur_series(NI_TAG, ni))
    if cl is not None:
        f.update(inst_series(CL_T, cl))
    if ca is not None:
        f.update(inst_series(CA_T, ca))
    for tag, later in ((REV_R2, rev_later), (CL_T, cl_later)):
        if later:
            for y, v in later.items():
                f[tag].append(tfact(add_days("%d-12-31" % y, -364) if tag in DURATION_TAGS else "", "%d-12-31" % y, v, "ACC-%d" % (y + 1), filed="%d-02-20" % (y + 2), fy=str(y + 1)))
    f.update(extra or {})
    return mkfirm(f, filings=filings, cik=cik, sic=sic)


def t_g1(ck):
    v = parse_json('{"a": 9007199254740993, "b": 1234.5, "c": 0.1, "d": [1, 2.5]}')
    ck.ok("an integer above 2^53 is read exactly, as a Decimal", isinstance(v["a"], Decimal) and v["a"] == Decimal("9007199254740993"), repr(v["a"]))
    ck.ok("a fractional value is a Decimal, never a float", isinstance(v["b"], Decimal) and v["b"] == Decimal("1234.5") and isinstance(v["c"], Decimal) and v["c"] == Decimal("0.1"), repr(v["c"]))
    ck.ok("numbers inside arrays are Decimals too", all(isinstance(x, Decimal) for x in v["d"]), repr(v["d"]))
    ck.eq("a Decimal sum of values above 2^53 is exact", dsum([Decimal("9007199254740993"), Decimal(1), Decimal(1)]), Decimal("9007199254740995"))
    ck.eq("a blank cell is missing, not zero", to_dec(""), None)
    ck.eq("a zero cell is zero", to_dec("0"), Decimal(0))
    ck.eq("a number is written without an exponent", num_text(Decimal("1E+3")), "1000")
    gaap = {"facts": {"us-gaap": {NI_TAG: {"units": {"EUR": [{"start": "2023-01-01", "end": "2023-12-31", "val": Decimal(5), "accn": "A-1", "fy": Decimal(2023), "fp": "FY", "form": "10-K", "filed": "2024-02-01"}]}}}}}
    ck.eq("a fact in another unit is not extracted", companyfacts_rows("20261105", "0000000001", gaap, {2023: "2023-12-31"}), [])
    gaap["facts"]["us-gaap"][NI_TAG]["units"]["USD"] = gaap["facts"]["us-gaap"][NI_TAG]["units"].pop("EUR")
    ck.eq("the same fact in USD is", len(companyfacts_rows("20261105", "0000000001", gaap, {2023: "2023-12-31"})), 1)
    ck.eq("pts is the filers in the whole frame, never a count of the 500", frame_count({"pts": Decimal(5000), "data": [{"cik": Decimal(789019)}, {"cik": Decimal(1)}]}, {"0000789019", "0000000002"}), 1)
    ck.eq("a cik is ten digits", cik10(Decimal(789019)), "0000789019")


def t_g2(ck):
    retailer = [("10-K", "2026-02-01", "2026-03-20", "R-25"), ("10-K", "2025-02-01", "2025-03-20", "R-24")]
    ym = year_map(retailer)
    ck.eq("a retailer's reportDate 2026-02-01 is in FY2025, not FY2026", (year_info(ym, 2025)[1], year_info(ym, 2026)[0]), ("2026-02-01", "none"))
    for d, y in (("2026-03-31", 2025), ("2026-04-01", 2026), ("2025-03-31", 2024), ("2025-04-01", 2025), ("2026-12-31", 2026), ("2027-03-31", 2026)):
        ck.eq("the window edge: %s is FY%d" % (d, y), fy_of(d), y)
    ck.eq("a 10-K/A or 10-KT never defines D_Y", year_info(year_map([("10-K/A", "2024-12-31", "2025-03-01", "A"), ("10-KT", "2024-12-31", "2025-03-01", "B")]), 2024)[0], "none")
    ck.eq("an original 10-K beside its amendment is one filing", year_info(year_map([("10-K", "2024-12-31", "2025-02-20", "A"), ("10-K/A", "2024-12-31", "2025-03-01", "B")]), 2024)[:2], ("one", "2024-12-31"))
    ck.eq("two original 10-Ks in one window are many", year_info(year_map([("10-K", "2024-06-30", "2024-08-01", "A"), ("10-K", "2024-12-31", "2025-02-20", "B")]), 2024)[0], "many")
    f = mkfirm({}, filings=[("10-K", "%d-12-31" % y, "x", "ACC-%d" % y) for y in range(2019, 2026)] + [("10-K", "2022-10-31", "2022-12-01", "ACC-X")])
    ck.eq("two 10-Ks in a needed year make the firm fy_ambiguous", classify(f, (2022, 2023, 2024, 2025))["status"], "fy_ambiguous")


def firm_full(cl=None, ca=None, rev=None, ni=None, **kw):
    rev = rev or [1000 * M_ + k * 50 * M_ for k in range(8)]
    ni = ni or [100 * M_ + k * 5 * M_ for k in range(8)]
    return quick_firm(rev, ni, cl=cl, ca=ca, **kw)


def t_g3(ck):
    for span, want in ((349, "none"), (350, "exact"), (380, "exact"), (381, "none")):
        f = mkfirm({REV_R2: [own_duration(REV_R2, 2023, 1000, span=span)]})
        ck.eq("a duration of %d days is %s" % (span, "accepted" if want == "exact" else "refused"), cell(f, REV_R2, 2023, "own_10k")[0], want)
    f = mkfirm({CL_T: [own_instant(CL_T, 2023, 100, end="2024-01-03")]})
    ck.eq("a fact 3 days off D_Y is near, not exact", cell(f, CL_T, 2023, "own_10k")[0], "near")
    ys = (2022, 2023, 2024, 2025)
    f = quick_firm([1000 * M_ + k * 50 * M_ for k in range(8)], [100 * M_ + k * 5 * M_ for k in range(8)], cl=[100 * M_, 100 * M_, 100 * M_, 100 * M_, 100 * M_, 100 * M_, 100 * M_, 100 * M_])
    f.facts[CL_T] = [x for x in f.facts[CL_T] if x[1] != "2023-12-31"] + [own_instant(CL_T, 2023, 100 * M_, end="2024-01-03")]
    ck.eq("no exact match but a near one makes the firm end_mismatch", classify(f, ys)["status"], "end_mismatch")
    st0 = add_days("2023-12-31", -364)
    own, later = tfact(st0, "2023-12-31", 100, "ACC-2023", filed="2024-02-20", fy="2023"), tfact(st0, "2023-12-31", 105, "ACC-2024", filed="2025-02-20", fy="2024")
    f = mkfirm({NI_TAG: [own, later]})
    ck.eq("own_10k takes the year's own 10-K, not the latest", cell(f, NI_TAG, 2023, "own_10k")[1], Dm(100))
    ck.eq("latest_filed takes the latest-filed fact", cell(f, NI_TAG, 2023, "latest_filed")[1], Dm(105))
    f = mkfirm({NI_TAG: [tfact(st0, "2023-12-31", 1, "A-0009", filed="2025-02-20"), tfact(st0, "2023-12-31", 2, "A-0010", filed="2025-02-20")]})
    ck.eq("a tie in filing date goes to the largest accn", cell(f, NI_TAG, 2023, "latest_filed")[1], Dm(2))
    f = mkfirm({NI_TAG: [tfact(add_days("2023-12-31", -364), "2023-12-31", 77, "ACC-2023", fy="2024", fp="Q1")]})
    ck.eq("selection never uses fy or fp", cell(f, NI_TAG, 2023, "own_10k")[:2], ("exact", Dm(77)))
    rev = [1000 * M_ + k * 100 * M_ for k in range(8)]
    f = quick_firm(rev, [100 * M_] * 8, cl=[100 * M_ + k * 10 * M_ for k in range(8)], rev_later={2025: 1900 * M_})
    wc = window_calc(f, "fy2023_fy2025", classify(f, window_years("fy2023_fy2025"))["struct"], "own_10k")
    ck.eq("a year's N and revenue come from the same filing: FY2025 revenue is the 10-K's own", wc["rev"][2025], Dm(rev[6]))
    wl = window_calc(f, "fy2023_fy2025", classify(f, window_years("fy2023_fy2025"))["struct"], "latest_filed")
    ck.eq("sens_latest takes the latest-filed revenue", wl["rev"][2025], Dm(1900 * M_))
    # R3-1, the same-filing basis: a later 10-K that recasts the prior year
    from fractions import Fraction as Fr
    rev8 = [1000 * M_ + k * 100 * M_ for k in range(8)]
    cl8 = [100 * M_ + k * 10 * M_ for k in range(8)]
    R22 = 700 * M_
    third = tfact(add_days("2022-12-31", -364), "2022-12-31", 500 * M_, "ACC-2024", filed="2025-02-20", fy="2024")
    fa = quick_firm(rev8, [100 * M_] * 8, cl=cl8, rev_later={2022: R22, 2024: rev8[5]}, cl_later={2022: cl8[3], 2024: cl8[5]})
    fa.facts[REV_R2].append(third)
    stA = classify(fa, window_years("fy2023_fy2025"))["struct"]
    wcA = window_calc(fa, "fy2023_fy2025", stA)
    wcS, fbA, rsA = samefiling_calc(fa, "fy2023_fy2025", stA, wcA)
    N8 = {2019 + k: -cl8[k] for k in range(8)}
    want = fr_to_dec((Fr(N8[2025]) - Fr(N8[2024]) / Fr(rev8[5]) * Fr(rev8[6])) - (Fr(N8[2023]) - Fr(N8[2022]) / Fr(R22) * Fr(rev8[4])))
    ck.ok("a firm whose later 10-K recasts the prior year's revenue: T on the same-filing basis uses the recast ratio", wcS is not None and abs(wcS["t"] - want) < Decimal("0.000001"), "got %s, want %s" % (wcS and wcS["t"], want))
    ck.ok("...it differs from the first-reported T, uses no fallback and is flagged restated", wcS["t"] != wcA["t"] and (fbA, rsA) == (False, True), str((fbA, rsA)))
    fb_ = quick_firm(rev8, [100 * M_] * 8, cl=cl8)
    stB = classify(fb_, window_years("fy2023_fy2025"))["struct"]
    wcB = window_calc(fb_, "fy2023_fy2025", stB)
    wcBS, fbB, rsB = samefiling_calc(fb_, "fy2023_fy2025", stB, wcB)
    ck.ok("a firm whose later 10-Ks tag no comparative falls back to the first-reported ratio, stays in the sample and is not restated", wcBS is not None and wcBS["t"] == wcB["t"] and (fbB, rsB) == (True, False), str((fbB, rsB)))
    fc = quick_firm(rev8, [100 * M_] * 8, cl=cl8, rev_later={2022: R22}, cl_later={2022: cl8[3], 2024: cl8[5]})
    stC = classify(fc, window_years("fy2023_fy2025"))["struct"]
    wcC, fbC, rsC = samefiling_calc(fc, "fy2023_fy2025", stC, window_calc(fc, "fy2023_fy2025", stC))
    ck.ok("a firm with the recast but no FY2024 revenue comparative in the FY2025 10-K falls back for that year only", wcC is not None and abs(wcC["t"] - want) < Decimal("0.000001") and fbC, str((wcC and wcC["t"], fbC)))


def av(T=None, C=None, N=None, ys=(2022, 2023, 2024, 2025)):
    d = {}
    for tag, vals in (("T", T), ("C", C), ("N", N)):
        d[tag] = {y: Decimal(v) for y, v in zip(ys, vals)} if vals else {}
    return d


def t_g4(ck):
    ys = (2022, 2023, 2024, 2025)
    a = av(T=[100, 100, 100, 100], C=[60, 60, 60, 60], N=[40, 40, 40, 40])
    r = resolve_balance(a, ys, "T", "C", "N")
    ck.eq("the total is used where it is at least its parts at every year", (r[0], r[1], r[2]), ("total", ["T"], False))
    a = av(T=[100, 100, 100, 100], C=[60, 60, 60, 60])
    r = resolve_balance(a, ys, "T", "C", "N")
    ck.eq("a total above its tagged parts is flagged total_gt_parts", (r[0], r[2]), ("total", True))
    a = av(T=[100, 100, 90, 100], C=[60, 60, 60, 60], N=[40, 40, 40, 40])
    r = resolve_balance(a, ys, "T", "C", "N")
    ck.eq("a total below its parts in one year sends the firm to the parts", (r[0], r[1]), ("parts", ["C", "N"]))
    a = av(T=[100, 100, 100, 100], C=[60, 60, 60, 60], N=[40, 40, 40, 40])
    ck.eq("a total is never added to its parts", resolve_balance(a, ys, "T", "C", "N")[1], ["T"])
    cl = {CL_T: {y: Dm(100) for y in ys}, CL_C: {}, CL_N: {}, DEF_C: {y: Dm(50) for y in ys}, DEF_N: {}}
    ck.eq("DeferredRevenueCurrent is not used beside a ContractWithCustomerLiability tag", resolve_cl(cl, ys)[:2], ("total", [CL_T]))
    cl2 = {CL_T: {}, CL_C: {}, CL_N: {}, DEF_C: {y: Dm(50) for y in ys}, DEF_N: {}}
    ck.eq("with no ContractWithCustomerLiability tag the DeferredRevenue fallback is used", resolve_cl(cl2, ys)[:2], ("deferred_revenue", [DEF_C]))
    both = {REV_R2: {y: Dm(1) for y in ys}, REV_R3: {y: Dm(1) for y in ys}, REV_ANY: {y: Dm(1) for y in ys}}
    ck.eq("R2 is used where it exists at every year, though Revenues exists too", resolve_rev(both, ys)[1], [REV_R2])
    r3 = {REV_R2: {2022: Dm(1)}, REV_R3: {y: Dm(1) for y in ys}, REV_ANY: {y: Dm(1) for y in ys}}
    ck.eq("R3 is used before Revenues", resolve_rev(r3, ys)[1], [REV_R3])
    sw = {REV_R2: {2022: Dm(1), 2023: Dm(1)}, REV_R3: {2024: Dm(1), 2025: Dm(1)}, REV_ANY: {}}
    ck.eq("a revenue tag never switches between years: no single tag is a gap", resolve_rev(sw, ys)[0], "gap")
    f = mkfirm({AR_A2: [own_instant(AR_A2, y, 5) for y in range(2019, 2027)], AR_A3: [own_instant(AR_A3, y, 5) for y in range(2019, 2027)]})
    ck.eq("A2 and A3 are not trade receivables: no AR series without A1", ar_series(f, (2022, 2023, 2024, 2025)), None)
    fa = firm_full(cl=[100 * M_] * 8)
    fa.facts.update(inst_series(AR_A1, [10 * M_] * 8))
    wc = window_calc(fa, "fy2023_fy2025", classify(fa, window_years("fy2023_fy2025"))["struct"], "own_10k")
    ck.eq("receivables are not added to N", wc["n"][2023], Dm(-100 * M_))


def t_g5(ck):
    ys = (2022, 2023, 2024, 2025)
    f0 = firm_full()
    c0 = classify(f0, ys)
    ck.eq("a firm with no contract tag at any year is in scope with N = 0", (c0["status"], c0["struct"]["ca"][0], c0["struct"]["cl"][0]), ("in_scope", "absent_everywhere", "absent_everywhere"))
    ck.eq("...and its N is zero every year", window_calc(f0, "fy2023_fy2025", c0["struct"])["n"], {y: Dm(0) for y in ys})
    fg = firm_full(cl=[None, None, None, None, None, 100 * M_, 110 * M_, 120 * M_])
    cg = classify(fg, ys)
    ck.eq("a contract tag at some needed years only is year_gap with gap_n", (cg["status"], "gap_n" in cg["flags"]), ("year_gap", True))
    fy22 = firm_full(cl=[100 * M_] * 8)
    fy22.filings = [x for x in fy22.filings if x[1] != "2022-12-31"]
    fy22._ymap = None
    ck.eq("FY2022 missing is year_gap for S1 (gap_10k)", (classify(fy22, window_years("fy2023_fy2025"))["status"], "gap_10k" in classify(fy22, window_years("fy2023_fy2025"))["flags"]), ("year_gap", True))
    vs, flags = variant_struct(fg, cg, "gap0")
    ck.ok("sens_gap0 builds a structure with the missing side imputed", vs is not None and vs["cl"][0] == "gap0" and "gap0_imputed" in flags, str(vs))
    if vs is not None:
        wc = window_calc(fg, "fy2023_fy2025", vs)
        ck.eq("...and sets the missing years to 0", (wc["cl"][2022], wc["cl"][2024]) if wc else None, (Dm(0), Dm(100 * M_)))
    fn = firm_full(cl=[100 * M_] * 8)
    fn.facts.pop(NI_TAG)
    ck.eq("a missing net income is year_gap with gap_ni", ("gap_ni" in classify(fn, ys)["flags"], classify(fn, ys)["status"]), (True, "year_gap"))
    allowed = ALLOWED_VALUES["status_firm"]
    sts = {classify(x, ys)["status"] for x in (f0, fg, fn, mkfirm({}, no_record=True), mkfirm({}, sic=""), mkfirm({}, sic="6021"))}
    ck.ok("no_mid or no_receivable is never written: every status is one of the eight", sts <= allowed, str(sts - allowed))


def stat(t, tp=None, dni=1000000, ni_b=10000000, rev=100000000000):
    return {"n": 3, "t": Dm(t), "tp": Dm(t if tp is None else tp), "tn": Dm(0), "dni": Dm(dni), "ni_b": Dm(ni_b), "rev": Dm(rev), "ea": Dm(0)}


def t_g6(ck):
    for t, lab in ((99996, "SHARE_BELOW_10"), (100000, "SHARE_10_TO_25"), (100001, "SHARE_10_TO_25"), (250000, "SHARE_10_TO_25"), (250001, "SHARE_ABOVE_25")):
        sh = Dm(t) / Dm(1000000) * 100
        ck.eq("|share| %s is %s" % (sh.quantize(Decimal("0.0001")), lab), score_stat(stat(t), None)["label"], lab)
        ck.eq("share_pos %s is %s" % (sh.quantize(Decimal("0.0001")), lab), score_stat(stat(5, tp=t), None, gross=True)["label"], lab)
    ck.eq("a negative T scores on its absolute size", score_stat(stat(-300000), None)["label"], "SHARE_ABOVE_25")
    ck.eq("dNI / base net income 0.0199 is VOID", (score_stat(stat(5, dni=199, ni_b=10000), None)["label"], score_stat(stat(5, dni=199, ni_b=10000), None)["void_reason"]), ("VOID", "dni_small"))
    ck.ok("dNI / base net income 0.0201 is not VOID", score_stat(stat(5, dni=201, ni_b=10000), None)["label"] != "VOID", "")
    ck.ok("dNI / base net income exactly 0.02 is not VOID", score_stat(stat(5, dni=200, ni_b=10000), None)["label"] != "VOID", "")
    sc = score_stat(stat(5, dni=-100000, ni_b=10000000), None)
    ck.eq("a change at or below zero with |share| < 10 is VOID (VOID is tested first)", (sc["label"], sc["void_reason"]), ("VOID", "dni_small"))
    ck.eq("a base not positive is VOID with its own reason", score_stat(stat(5, dni=5, ni_b=0), None)["void_reason"], "base_not_positive")
    ck.eq("direction: T > 0 is with_growth, T < 0 against_growth, T = 0 zero", [score_stat(stat(x), None)["direction"] for x in (5, -5, 0)], ["with_growth", "against_growth", "zero"])
    ck.eq("qualifier: inside the band", qualifier_of(Dm(5), Dm(1000), Dm("0.01")), "within_pre_window_range")
    ck.eq("qualifier: outside the band", qualifier_of(Dm(11), Dm(1000), Dm("0.01")), "outside_pre_window_range")
    st = calc_stats([{"t": Dm(10), "dni": Dm(0), "ni_b": Dm(0), "rev_e": Dm(0), "ea": Dm(0)}, {"t": Dm(-4), "dni": Dm(0), "ni_b": Dm(0), "rev_e": Dm(0), "ea": Dm(0)}])
    ck.eq("T_pos does not net offsets: T 6, T_pos 10, T_neg -4", (st["t"], st["tp"], st["tn"]), (Dm(6), Dm(10), Dm(-4)))
    N = {2022: 100 * M_, 2023: 140 * M_, 2024: 150 * M_, 2025: 230 * M_}
    R = {2022: 1000 * M_, 2023: 1100 * M_, 2024: 1200 * M_, 2025: 1300 * M_}
    f = mkfirm(merge(dur_series(REV_R2, [900 * M_, 950 * M_, 980 * M_, R[2022], R[2023], R[2024], R[2025], 1400 * M_]), dur_series(NI_TAG, [90, 91, 92, 93, 94, 95, 96, 97]),
                     inst_series(CA_T, [0, 0, 0, N[2022], N[2023], N[2024], N[2025], 0])))
    wc = window_calc(f, "fy2023_fy2025", classify(f, window_years("fy2023_fy2025"))["struct"])
    want = fr_to_dec(ref_T(N, R, 2023, 2025))
    ck.ok("T = AA_2025 - AA_2023 with AA_t = N_t - r_(t-1) Rev_t, not the stock residual", wc is not None and abs(wc["t"] - want) < Decimal("0.000001"), "got %s, want %s" % (wc and wc["t"], want))
    ck.ok("EA is described separately and differs from T here", wc is not None and abs(wc["ea"] - wc["t"]) > 1, "")


def t_g7(ck):
    ys = (2022, 2023, 2024, 2025)
    for sic, want in (("6000", "financial_sic"), ("6799", "financial_sic"), ("5999", "in_scope"), ("6800", "in_scope"), ("", "no_sic"), ("6021", "financial_sic"), ("7372", "in_scope")):
        f = firm_full()
        f.sic = sic
        ck.eq("SIC %r is %s" % (sic, want), classify(f, ys)["status"], want)
    for rev, want in ((99999999, "tiny_revenue"), (100000000, "in_scope")):
        f = firm_full(rev=[1000 * M_] * 3 + [rev] + [1000 * M_] * 4)
        ck.eq("revenue of %s USD in one needed year is %s" % ("{:,}".format(rev), want), classify(f, ys)["status"], want)


def t_g8(ck):
    for d, want in (("2026-11-29", False), ("2026-11-30", True), ("2027-02-15", True), ("2027-02-16", False)):
        ck.eq("D_2026 %s is %s" % (d, "in" if want else "out"), s2_date_ok(d), want)
    sp = {"cik": "0000000001", "name": "X", "facts": {"us-gaap": {NI_TAG: {"units": {"USD": [
        {"start": "2024-01-01", "end": "2024-12-31", "val": Decimal(1), "accn": "A-1", "fy": Decimal(2024), "fp": "FY", "form": "10-K", "filed": "2025-02-01"},
        {"start": "2025-01-01", "end": "2025-12-31", "val": Decimal(2), "accn": "A-2", "fy": Decimal(2025), "fp": "FY", "form": "10-K", "filed": "2026-02-01"},
        {"start": "2026-01-01", "end": "2026-12-31", "val": Decimal(3), "accn": "A-3", "fy": Decimal(2026), "fp": "FY", "form": "10-K", "filed": "2027-02-01"},
        {"start": "2025-01-04", "end": "2026-01-03", "val": Decimal(9), "accn": "A-4", "fy": Decimal(2025), "fp": "FY", "form": "10-K", "filed": "2026-02-01"}]}}}}}
    dm = {2024: "2024-12-31", 2025: "2025-12-31", 2026: "2026-12-31"}
    ck.eq("before 2027-05-01 no fact with end after D_2025 is extracted, not even 3 days after it", [r[4] for r in companyfacts_rows("20261105", "0000000001", sp, dm)], ["2024-12-31", "2025-12-31"])
    ck.eq("from 2027-05-01 the FY2026 fact and the 3-day tail are extracted", [r[4] for r in companyfacts_rows("20270501", "0000000001", sp, dm)], ["2024-12-31", "2025-12-31", "2026-01-03", "2026-12-31"])
    ck.eq("without a D_2025 the cut is 2026-03-31", wanted_ends({2024: "2024-12-31"}, "20261105")[1], "2026-03-31")
    for p in ("CY2026Q2I", "CY2026Q4I", "CY2026", "CY2027Q1I"):
        ck.ok("%s is not fetched before 2027-05-01" % p, not frame_period_ok(p, "20261105") and frame_period_ok(p, "20270501"), "")
    ck.ok("the frame plan holds no 2026 period before the S2 date", all(frame_year(p) < 2026 for _, p in frame_plan("20261105")), "")
    ck.eq("the plan is 22 tags in three periods", len(frame_plan("20261105")), 66)
    ck.ok("from the S2 date the plan adds CY2026Q4I and CY2026", len(frame_plan("20270501")) == 88 and ("%s" % AR_A1, "CY2026Q4I") in frame_plan("20270501"), "")
    ck.eq("S2 scored before 2027-05-01 must be PENDING", s2_phase("20261105", 100, 100), "PENDING")
    ck.eq("69.99% coverage is PENDING_THIN", s2_phase("20270501", 6999, 10000), "PENDING_THIN")
    ck.eq("70.00% coverage is not thin", s2_phase("20270501", 7000, 10000), "score")
    ck.eq("still thin on 2027-08-01 is VOID", s2_phase("20270801", 6999, 10000), "VOID")
    ck.eq("thin on 2027-07-31 is still PENDING_THIN", s2_phase("20270731", 6999, 10000), "PENDING_THIN")
    ck.ok("fiscalYearEnd 1130 and 1231 and 0101 and 0215 are eligible, 1129 and 0216 are not", [fye_ok(x) for x in ("1130", "1231", "0101", "0215", "1129", "0216", "0630")] == [True, True, True, True, False, False, False], "")
    cut = full_cut(year_map([("10-K", "2025-12-31", "x", "A")]), "20261105")
    ck.eq("a full-stage build before the S2 date reads nothing after D_2025", cut, "2025-12-31")
    ck.eq("from the S2 date there is no cut", full_cut({}, "20270501"), None)

    # ruling S2-R1: a firm whose submissions fiscalYearEnd is 1231 but whose FY2026 10-K ends in June
    def f26(cik, rows):
        return Firm(cik, ("T",), "N", "3571", "1231", False, rows, {})
    dec_ = f26("0000000002", [("10-K", "2025-12-31", "2026-02-20", "D-25"), ("10-K", "2026-12-31", "2027-02-10", "D-26")])
    jun_ = f26("0000000001", [("10-K", "2025-12-31", "2026-02-20", "J-25"), ("10-K", "2026-06-30", "2026-08-14", "J-26")])
    amb_ = f26("0000000003", [("10-K", "2025-12-31", "2026-02-20", "A-25"), ("10-K", "2026-12-31", "2027-02-10", "A-26"), ("10-K", "2027-01-15", "2027-02-20", "A-26b")])
    non_ = f26("0000000004", [("10-K", "2025-12-31", "2026-02-20", "N-25")])
    fx = collections.OrderedDict((f.cik, f) for f in (dec_, jun_, amb_, non_))
    ck.eq("the FY2026 10-K states: inside, outside, two 10-Ks, none", [s2_fy2026_state(f) for f in fx.values()], ["in_window", "outside_window", "ambiguous", "none"])
    cov = s2_coverage(fx, list(fx))
    ck.eq("a firm with fiscalYearEnd 1231 and a June FY2026 10-K is not counted in have26", cov["in_window"], [dec_.cik])
    ck.eq("...it is the end_mismatch firm; a firm with two 10-Ks and one with none are counted apart", (cov["outside_window"], cov["ambiguous"], cov["none"]), ([jun_.cik], [amb_.cik], [non_.cik]))
    ck.eq("...and the four lists add up to the denominator, which is unchanged", sum(len(v) for v in cov.values()), 4)
    ck.eq("one of two eligible firms counted (the June firm is not) is 50%, thin", s2_phase("20270501", len(s2_coverage(fx, [dec_.cik, jun_.cik])["in_window"]), 2), "PENDING_THIN")
    scored = s2_scored_set(fx, list(fx), {k: {"status": "in_scope"} for k in fx})
    ck.eq("at scoring the June firm is excluded from S2 (status end_mismatch), as are the two-10-K and no-10-K firms", scored, {dec_.cik})
    ck.eq("a firm not in scope is not scored either", s2_scored_set(fx, list(fx), {k: {"status": "year_gap"} for k in fx}), set())


def t_g9(ck):
    def lrec(i, t):
        return {"cik": "%010d" % i, "ticker": "L%d" % i, "name": "N", "t": Dm(t), "dni": Dm(40), "ni_b": Dm(1000), "rev_e": Dm(10000), "ea": Dm(0), "flags": set()}
    lrecs = [lrec(1, 60)] + [lrec(i, 10) for i in range(2, 6)] + [lrec(6, -50)]
    f_s1, f_n = fragility(lrecs, None, None)
    ck.eq("leave-one-out: removing the one firm that carries the result takes S1 below 10% (20.83% to 5%)", [r["cik"] for r, _ in f_s1], ["0000000001"])
    ck.eq("...and takes S1P below 25% (41.67% to 20%); no other firm does either", f_n, 1)
    recs = [{"cik": "%010d" % i, "ticker": "T%d" % i, "name": "N", "t": Dm(i * 100), "flags": {"acq2"} if i == 12 else set()} for i in range(1, 13)]
    recs += [{"cik": "%010d" % (100 + i), "ticker": "N%d" % i, "name": "N", "t": Dm(-i * 50), "flags": set()} for i in range(1, 13)]
    pos, neg = contributors(recs)
    ck.eq("ten rows on each side, not eleven", (len(pos), len(neg)), (10, 10))
    tp = sum(r["t"] for r in recs if r["t"] > 0)
    tn = sum(r["t"] for r in recs if r["t"] < 0)
    ck.ok("the positive share is over gross positive T", abs(pos[0][2] - Dm(1200) / tp * 100) < Decimal("0.0000001"), str(pos[0][2]))
    ck.ok("the negative share is over gross negative T", abs(neg[0][2] - Dm(-600) / tn * 100) < Decimal("0.0000001"), str(neg[0][2]))
    ck.eq("the largest positive and the most negative lead their sides", (pos[0][1]["cik"], neg[0][1]["cik"]), ("0000000012", "0000000112"))
    p5, n5 = top5_shares(recs)
    ck.ok("top five of gross positive T", abs(p5 - sum(sorted([r["t"] for r in recs if r["t"] > 0], reverse=True)[:5]) / tp * 100) < Decimal("0.0000001"), str(p5))
    ck.ok("top five of gross negative T is taken on the negative side", abs(n5 - sum(sorted([r["t"] for r in recs if r["t"] < 0])[:5]) / tn * 100) < Decimal("0.0000001"), str(n5))
    w = get_world()
    w2 = copy_world(w, "g9")
    texts, failed, c = build_world(w2, "full")
    h, rows = csv_body(texts["contributors.csv"])
    cont = {(r[0], r[2]): r for r in csv_body(texts["contributions.csv"])[1] if r[1] == "primary"}
    flagged = [r for r in rows if cont[(r[0], r[3])][9]]
    ck.ok("the contributors carry their flags", bool(flagged) and all(r[8] == cont[(r[0], r[3])][9] for r in flagged), "no flagged contributor, or the flags are missing")


# ---- G10 to G19 ----
def checksh_text():
    return read_file(os.path.join(ROOT, "bin", "check.sh"), "r")


def checksh_region(text):
    a = text.find("rrt_leak_check() {")
    return text[a:text.find("\n}\n", a) + 3] if a >= 0 else ""


@contextlib.contextmanager
def patched(**kw):
    """Temporarily rebind module constants (the test of 'editing a constant changes the hash')."""
    g = globals()
    old = {k: g[k] for k in kw}
    g.update(kw)
    try:
        yield
    finally:
        g.update(old)


def t_g10(ck):
    ck.ok("the constants reproduce the 4.6 text", prereg_ok(), sha256_of(prereg_text().encode("utf-8")))
    ck.ok("the constants reproduce the 4.7 text", pop_ok(), sha256_of(pop_text().encode("utf-8")))
    ck.ok("4.6 has 5 lines and 2,409 bytes, 4.7 has 13 lines and 2,240 bytes", (len(prereg_text().splitlines()), len(prereg_text().encode("utf-8")), len(pop_text().splitlines()), len(pop_text().encode("utf-8"))) == (5, 2409, 13, 2240), "")
    with patched(TH_LO=Decimal("11")):
        ck.ok("editing a threshold changes the 4.6 hash", not prereg_ok(), "")
    with patched(REV_FLOOR=Decimal(99999999)):
        ck.ok("editing the revenue floor changes the 4.7 hash", not pop_ok(), "")
    w = get_world()
    inp = world_loader(w, "full")()
    ck.quiet("with both hashes holding the build writes registered.csv", lambda: compute(inp))
    region = checksh_region(checksh_text())
    m = re.search(r"PREREG_SHA='([0-9a-f]{64})'", region)
    ck.ok("prereg_sha256 in registered.csv equals M27's literal copy", bool(m) and m.group(1) == prereg_sha_out() == SPEC_PREREG_SHA256, "no literal in check.sh, or it differs")
    band = {"nb1": Dm("0.01"), "nb2": Dm("0.02")}
    ck.eq("S1 is measured against NB2, S2 against NB1", (nb_for("S1", band), nb_for("S1P", band), nb_for("S2", band), nb_for("S2P", band)), (Dm("0.02"), Dm("0.02"), Dm("0.01"), Dm("0.01")))
    # registered.csv closes against headline.csv (the scored record must match the build)
    w3 = copy_world(w, "g10c")
    texts, failed, c = build_world(w3, "full")
    reg, head = csv_body(texts["registered.csv"])[1], csv_body(texts["headline.csv"])[1]
    ck.eq("registered.csv closes against headline.csv on the clean build", registered_closure_problems(reg, head), [])
    ck.eq("...and so does the folder guard on the texts", tamper_problems({"registered.csv": texts["registered.csv"], "headline.csv": texts["headline.csv"]}), [])
    s1 = [r for r in reg if r[0] == "S1"][0]

    def planted(col_edits, only="S1"):
        out = []
        for r in reg:
            r = list(r)
            if r[0] == only:
                for col, val in col_edits.items():
                    r[col] = val
            out.append(r)
        return out

    n1 = str(int(s1[5]) + 1000)
    ck.ok("a registered S1 numerator and T both edited by 1,000 USD are reported", any("S1" in p for p in registered_closure_problems(planted({5: n1, 6: n1}), head)), "")
    ck.ok("a registered S1 n_firms edited is reported", bool(registered_closure_problems(planted({4: str(int(s1[4]) + 1)}), head)), "")
    ck.ok("a registered S1 dNI edited is reported", bool(registered_closure_problems(planted({7: str(int(s1[7]) + 1000)}), head)), "")
    ck.ok("a registered S1 share_pct edited is reported", bool(registered_closure_problems(planted({9: "99.999"}), head)), "")
    s1p = [r for r in reg if r[0] == "S1P"][0]
    ck.ok("a registered S1P numerator that is not the positive T is reported", bool(registered_closure_problems(planted({5: str(int(s1p[5]) + 5)}, only="S1P"), head)), "")
    ck.ok("a registered row with no headline row of its vintage is reported", bool(registered_closure_problems(planted({3: "19990101"}), head)), "")
    ptext = texts["registered.csv"].replace(",%s,%s," % (s1[5], s1[6]), ",%s,%s," % (n1, n1), 1)
    ck.ok("the folder guard reports the edited registered.csv text", ptext != texts["registered.csv"] and bool(tamper_problems({"registered.csv": ptext, "headline.csv": texts["headline.csv"]})), "")
    ck.eq("C07 passes on the clean build", c07(c)[4], "PASS")
    c["rows"]["registered.csv"] = planted({5: n1, 6: n1})
    ck.eq("C07 fails on an edited registered row", c07(c)[4], "FAIL")
    # M27 itself, run on the written folder
    w4 = copy_world(w, "g10m")
    build_world(w4, "full")
    ck.eq("M27 prints no problem on the clean build", m27_run(w4["out"], w4["cache"], m27_text()), [])
    rp = os.path.join(w4["out"], "registered.csv")
    clean = read_file(rp, "r")
    for label, edited in (("numerator and T edited", clean.replace(",%s,%s," % (s1[5], s1[6]), ",%s,%s," % (n1, n1), 1)), ("n_firms edited", clean.replace("S1,fy2023_fy2025,primary,%s,%s," % (s1[3], s1[4]), "S1,fy2023_fy2025,primary,%s,%s," % (s1[3], int(s1[4]) + 1), 1)),
                          ("share_pct edited", clean.replace(",%s,%s,%s,%s," % (s1[7], s1[8], s1[9], s1[10]), ",%s,%s,99.999,%s," % (s1[7], s1[8], s1[10]), 1))):
        write_text(rp, edited)
        lines = m27_run(w4["out"], w4["cache"], m27_text())
        ck.ok("M27 prints a problem line for the registered S1 row with its %s" % label, edited != clean and 1 <= len(lines) <= 2 and all("registered.csv S1 " in l for l in lines), str(lines))
    write_text(rp, clean)


def m27_text():
    """The M27 guard as it stands in bin/check.sh; the mutant cuts out its registered-closure block."""
    t = checksh_text()
    if M("g10_m27_closure_off"):
        t = re.sub(r"# registered-closure begin\n.*?# registered-closure end\n", "", t, flags=re.S)
    return t


def m27_run(out_dir, vint_dir, text):
    """Run M27 (the bash function of bin/check.sh) on a folder and a vintage root; returns its lines that carry a cross."""
    with tempfile.TemporaryDirectory(prefix="rrt_m27_", ignore_cleanup_errors=True) as tmp:
        script = os.path.join(tmp, "m27.sh")
        write_text(script, checksh_region(text) + '\nRRT_DIR="$1" RRT_VDIR="$2" rrt_leak_check\n')
        r = subprocess.run(["bash", script, out_dir, vint_dir], capture_output=True, text=True, timeout=120)
    return [l for l in r.stdout.splitlines() if "\u2717" in l]


def fake_rec(t, rev=1000, dni=10, ni_b=100):
    return {"t": Dm(t), "dni": Dm(dni), "ni_b": Dm(ni_b), "rev_e": Dm(rev), "ea": Dm(0)}


def t_g11(ck):
    ck.eq("exactly the three placebo windows", placebo_windows(), ("fy2020_fy2022", "fy2020_fy2021", "fy2021_fy2022"))
    f = mkfirm(merge(dur_series(REV_R2, [1000 * M_, 1100 * M_, 1200 * M_, 1300 * M_, 1400 * M_, 1500 * M_, 1600 * M_, 1700 * M_]), dur_series(NI_TAG, [100 * M_] * 8),
                     inst_series(CA_T, [10 * M_, 30 * M_, 25 * M_, 60 * M_, 0, 0, 0, 0])))
    cl = classify(f, window_years("fy2020_fy2022"))
    wc = window_calc(f, "fy2020_fy2022", cl["struct"])
    rec = make_rec(f, wc, set(), placebo=True)
    ck.eq("a placebo window's T is AA_e - AA_b, not EA", rec["t"], q0(wc["aa_e"] - wc["aa_b"]))
    ck.ok("...and EA differs here", abs(wc["ea"] - (wc["aa_e"] - wc["aa_b"])) > 1, "")
    rbw = {"fy2020_fy2022": [fake_rec(100)], "fy2020_fy2021": [fake_rec(500)], "fy2021_fy2022": [fake_rec(20)]}
    rows, band = placebo_table(rbw)
    ck.eq("NB1 is the one-year window without FY2020 as an endpoint; NB2 the two-year window", (band["nb1"], band["nb2"]), (Dm("0.02"), Dm("0.1")))
    ck.eq("medians are over all windows of each length", (band["med1"], band["med2"]), (Dm("0.26"), Dm("0.1")))
    ck.eq("placebo.csv rows carry includes_fy2020", [r[2] for r in rows], ["yes", "yes", "no"])
    ck.eq("the frozen band is not replaced by one from a later vintage", frozen_band({"nb1": 1}, {"nb1": 2}), {"nb1": 2})
    ck.eq("the band comes back from the written rows", band_from_rows(rows)["nb1"], Dm("0.02"))
    w = get_world()
    w1, w2 = copy_world(w, "g11a"), copy_world(w, "g11b")
    clean, _, c1 = build_world(w1, "pre")
    cfp = os.path.join(w2["vdir"], "cf_extract.csv")
    poison = "".join("20261105,0000789019,%s,%s,%s,POISON,ZZZ-1,10-K,FY,%d,2025-08-01\n" % (t, s, e, y) for t, s, e, y in (
        (NI_TAG, "2023-07-01", "2024-06-30", 2024), (CL_T, "", "2024-06-30", 2024), (REV_R2, "2024-07-01", "2025-06-30", 2025), (CL_T, "", "2025-06-30", 2025)))
    write_text(cfp, read_file(cfp, "r") + poison)
    dirty, failed, c2 = build_world(w2, "pre")
    ck.eq("the pre stage never converts a value dated after FY2022: poison rows change nothing", dirty["placebo.csv"], clean["placebo.csv"])
    c10 = [r for r in c2["checks"] if r[0] == "C10"][0]
    ck.eq("...and C10 passes", c10[4], "PASS")
    limit = [(cik, end) for cik, end in c2["inp"]["read_log"] if end > independent_cut(c2["firms"][cik], "pre", w2["vintage"])]
    ck.eq("...no value beyond the cut was read", limit, [])
    ck.eq("the pre stage writes the pre subset only", sorted(clean), sorted(PRE_NAMES + ("checks.csv",)))


def t_g12(ck):
    ck.ok("SPEC_ALLOW_SHA256 is the hash of the allowlist text", allow_hash_ok(), sha256_of(allow_text().encode("utf-8")))
    ck.eq("the allowlist has eighteen lines and 1,547 bytes", (len(SPEC_ALLOW_TEXT.splitlines()), len(SPEC_ALLOW_TEXT.encode("utf-8"))), (18, 1547))
    ck.raises("an extra column is refused", DataError, lambda: check_header("placebo.csv", ALLOW["placebo.csv"] + ["note"]))
    ck.raises("a renamed column is refused", DataError, lambda: check_header("headline.csv", ["vintage", "window", "sample", "stat", "value", "unit", "n_firms"]))
    ck.quiet("the exact header is accepted", lambda: check_header("headline.csv", ALLOW["headline.csv"]))
    txt = "# source: x\n" + ",".join(ALLOW["coverage.csv"]) + "\na,b,c,1,1\n"
    ck.eq("a # source: line is never read as the header", csv_body(txt)[0], ALLOW["coverage.csv"])
    clean = {n: "# source: x\n" + ",".join(ALLOW[n]) + "\n" for n in ALLOW_ORDER[:15]}
    clean["README.md"], clean["SOURCES.md"] = "A plain README.\n", "Plain sources.\n"
    ck.eq("on the clean folder the name check passes", leak_problems(clean), [])
    bad = dict(clean)
    bad["sixteenth.csv"] = "# source: x\na\n"
    ck.ok("a sixteenth CSV in the output folder is reported", any("sixteenth.csv" in p for p in leak_problems(bad)), str(leak_problems(bad)))
    dup = "# source: x\n" + ",".join(ALLOW["placebo.csv"]) + "\nfy2020_fy2022,a,yes,1,1,1,1,1,1,1\nfy2020_fy2022,b,yes,1,1,1,1,1,1,1\n"
    ck.ok("a duplicate key is reported", bool(dup_key_problems({"placebo.csv": dup})), "")
    ck.eq("a rename inside a committed file is reported", header_problems({"headline.csv": "# source: x\nvintage,window,sample,stat,value,unit,n_firms\n"}) != [], True)
    sh = checksh_text()
    ck.eq("bin/check.sh holds the literal header lines and the 4.6 hash", checksh_problems(sh), [])
    region = checksh_region(sh)
    got = "".join("%s:%s\n" % (n, m.group(1)) for n in ALLOW_ORDER for m in [re.search(r"\b%s\) want='([^']*)'" % re.escape(n), region)] if m)
    ck.ok("M27's copy of the allowlist hashes to SPEC_ALLOW_SHA256", sha256_of(got.encode("utf-8")) == SPEC_ALLOW_SHA256, sha256_of(got.encode("utf-8")))
    ck.ok("a check.sh with an altered literal header is reported", bool(checksh_problems(sh.replace("want='window,sample,cik10,ticker,", "want='window,sample,cik,ticker,"))), "")
    ck.ok("a check.sh that reads the headers from the script is reported", bool(checksh_problems(sh.replace("rrt_leak_check() {", "rrt_leak_check() {\n  python3 bin/rev_recognition_timing.py allow", 1))), "")


GOOD_README_SAMPLE = ("Plain words about excess accrual, booked ahead of billing, the timing contribution, ordinary explanations and operating cash flow. " + DENIAL_SENTENCE + " Nothing else.")


def t_g13(ck):
    w = get_world()
    texts, failed, c = build_world(copy_world(w, "g13"), "full")
    ck.eq("the generated README passes", wording_problems("README.md", texts["README.md"]), [])
    ck.ok("the README never says the change in net income came from timing", "came from" not in texts["README.md"], "")
    ck.eq("the sample sentence passes", wording_problems("README.md", GOOD_README_SAMPLE), [])
    ck.eq("the denial sentence is exempt, once", wording_problems("README.md", "Intro. " + DENIAL_SENTENCE + " Outro."), [])
    ck.eq("the exemption removes the denial sentence once: a second copy stays", strip_exempt(DENIAL_SENTENCE + "\n" + DENIAL_SENTENCE).count(DENIAL_SENTENCE), 1)
    ck.eq("the denial sentence is not exempt outside the README", strip_exempt(DENIAL_SENTENCE, readme=False), DENIAL_SENTENCE)
    ck.ok("a sentence that merely says 'nothing here says' is not exempt", bool(wording_problems("README.md", "Honestly nothing here says it is a flow into software. " + DENIAL_SENTENCE)), "")
    ck.ok("an altered denial sentence is not exempt", bool(wording_problems("README.md", DENIAL_SENTENCE.replace("booked", "pulled forward"))), "")
    for s in ("timing inflated earnings", "the firms boosted revenue", "revenue was pulled forward", "abnormal accruals", "a material share", "receivables drove the rally", "money flowed into software",
              "the firm managed earnings", "a premature booking", "window-dressing", "smoothed profits", "a red flag", "caused by the contract"):
        ck.ok("'%s' fails" % s, bool(wording_problems("README.md", s)), "passed")
    ck.ok("a verdict word fails the writer", all(_raises(DataError, lambda w_=w_: guard_text("checks.csv", "x %s y" % w_)) for w_ in ("MATERIAL", "HELD", "NOT_MATERIAL", "CAUSED", "PROVEN", "REFUTED", "FALSIFIED")), "")


def _raises(exc, fn):
    try:
        fn()
    except exc:
        return True
    except Exception:
        return False
    return False


def good_frame(target):
    m = FRAME_RX.match(target)
    return 200, json.dumps({"tag": m.group(1), "ccp": m.group(2), "uom": "USD", "data": []}).encode("utf-8"), {}


def fetch_rig(tmp, resp=good_frame, clock=None, mode="fetch-frames", max_requests=None, ciks=("0000000001", "0000000002", "0000000003")):
    clock = clock or FakeClock()
    panel = os.path.join(tmp, "panel.csv")
    if not os.path.isfile(panel):
        write_text(panel, "ticker,cik10\n" + "".join("T%d,%s\n" % (i, c) for i, c in enumerate(ciks)))
    calls = []
    cache, out = os.path.join(tmp, "cache"), os.path.join(tmp, "out")

    def opener(host, target, headers, timeout, cap):
        calls.append((host, target, dict(headers)))
        r = resp(target) if callable(resp) else resp
        if isinstance(r, Exception):
            raise r
        return r

    ns = argparse.Namespace(cmd=mode, vintage=clock.now_utc().strftime("%Y%m%d"), cache=cache, out=out, panel=panel, max_requests=max_requests)

    def go(environ=None, ns_=None):
        said = []
        code = run_fetch(ns_ or ns, environ={"SEC_UA": FIXTURE_CONTACT} if environ is None else environ, opener=opener, sleeper=clock.sleep, now_utc=clock.now_utc, say=said.append, stop_dir=cache)
        return code, said

    return go, calls, ns, clock


def jdump(obj):
    """JSON text of a document built with Decimals (numbers stay numbers)."""
    return json.dumps(obj, default=lambda o: int(o) if o == o.to_integral_value() else float(o)).encode("utf-8")


def bytes_of_tree(root):
    out = b""
    for d, _, fs in os.walk(root):
        for n in sorted(fs):
            out += read_file(os.path.join(d, n), "rb")
    return out


def t_g14(ck):
    forget_secrets()
    src = read_file(os.path.abspath(__file__), "r")
    ck.eq("the script's own source passes the STOP scan", stop_ast_problems(src), [])
    bad_sources = {
        "os.remove": "import os\ndef f(cache):\n    os.remove(os.path.join(cache, 'STOP_rrt'))\n",
        "os.unlink via a name": "import os\ndef f(cache):\n    sp = os.path.join(cache, 'STOP_rrt')\n    os.unlink(sp)\n",
        "os.replace": "import os\ndef f(tmp):\n    os.replace(tmp, STOP_PATH)\n",
        "os.rename": "import os\ndef f(a):\n    os.rename(a, stop_path)\n",
        "Path.unlink": "from pathlib import Path\ndef f(stop):\n    Path(stop).unlink()\n",
        "Path.write_text": "from pathlib import Path\ndef f(stop):\n    Path(stop).write_text('x')\n",
        "Path.write_bytes": "from pathlib import Path\ndef f(stop):\n    Path(stop).write_bytes(b'x')\n",
        "open w": "def f(stop):\n    open(stop, 'w').write('x')\n",
        "open a": "def f(stop):\n    open(stop, 'a').write('x')\n",
        "shutil.move": "import shutil\ndef f(stop):\n    shutil.move(stop, 'x')\n",
        "shutil.rmtree": "import shutil\ndef f(cache):\n    shutil.rmtree(cache)\n",
        "create_stop with a": "def create_stop(path, text):\n    open(path, 'a').write(text)\n",
    }
    for name, s in bad_sources.items():
        ck.ok("the scan reports: %s" % name, bool(stop_ast_problems(s)), "not reported")
    good = "import os\ndef create_stop(path, text):\n    with open(path, 'x') as fh:\n        fh.write(text)\ndef check(stop):\n    return os.path.exists(stop) and open(stop).read()\n"
    ck.eq("exclusive create and a read of the latch are allowed", stop_ast_problems(good), [])
    with tempfile.TemporaryDirectory(prefix="rrt_g14_", ignore_cleanup_errors=True) as tmp:
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "p"))
        stop = os.path.join(ns.cache, STOP_NAME)
        create_stop(stop, "status: 429\nutc_time: x\nurl_path: y\nretry_after: 5\nbody_head: z\n")
        before = sha256_of(read_file(stop))
        code, said = go()
        ck.eq("with a planted STOP_rrt a fetch makes no request and exits 2", (code, len(calls)), (2, 0))
        ck.eq("...the STOP file is unchanged", sha256_of(read_file(stop)), before)
        ck.ok("...and says STOP present", any(s.startswith("STOP present") for s in said), str(said))
        create_stop(stop, "something else\n")
        ck.eq("create_stop never overwrites an existing latch", sha256_of(read_file(stop)), before)
        cases = [("301", (301, b"", {"location": "/api/xbrl/frames/x"}), "HTTP 301"), ("403", (403, b"Forbidden", {}), "HTTP 403"), ("429", (429, b"slow down", {"retry-after": "60"}), "HTTP 429"),
                 ("500", (500, b"oops", {}), "HTTP 500"), ("an empty body", (200, b"", {}), "empty body"), ("an HTML body", (200, b"<html><body>blocked</body></html>", {}), "web page"),
                 ("an HTML body after a space", (200, b"  \n<!DOCTYPE html><html>", {}), "web page"), ("a non-JSON body", (200, b"hello there, not JSON at all", {}), "not JSON"),
                 ("JSON that is not the document", (200, b'{"message": "rate limited"}', {}), "not the document")]
        for i, (label, resp, msg) in enumerate(cases):
            go, calls, ns, clock = fetch_rig(os.path.join(tmp, "b%d" % i), resp)
            code, said = go()
            stp = os.path.join(ns.cache, STOP_NAME)
            has = os.path.exists(stp)
            ck.ok("...and says why (%s)" % msg, any(msg in s for s in said), str(said))
            ck.ok("a reply of %s writes STOP_rrt, ends the fetch (exit 2) after exactly one request" % label, has and code == 2 and len(calls) == 1 and len(fetch_rows(ns.out)) == 1, "exit %s, %d calls, stop %s" % (code, len(calls), has))
            if has:
                ck.ok("...with the five fields in order", stop_text_ok(read_file(stp, "r")), read_file(stp, "r")[:200])
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "n404"), (404, b"<?xml version='1.0'?><Error>NoSuchKey</Error>", {}), max_requests=3)
        code, said = go()
        ck.eq("a 404 on a frame is absent: no STOP, the slice ends by its limit (exit 4)", (code, os.path.exists(os.path.join(ns.cache, STOP_NAME)), len(calls)), (4, False, 3))
        ck.eq("...and each 404 is a vintages.csv row", [r["status"] for r in vint_rows(ns.out)], ["404"] * 3)
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "tmo"), SocketFault("TimeoutError"))
        code, said = go()
        ck.ok("a timeout exits 3, writes no STOP and retries nothing", code == 3 and not os.path.exists(os.path.join(ns.cache, STOP_NAME)) and len(calls) == 1 and any(s.startswith("FAIL network") for s in said), str((code, said)))
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "ok"), max_requests=2)
        code, said = go()
        ck.ok("good frames write no STOP", code == 4 and not os.path.exists(os.path.join(ns.cache, STOP_NAME)), str(code))
    forget_secrets()


def t_g15(ck):
    forget_secrets()
    for u in ("https://www.sec.gov/Archives/edgar/data/1/x.htm", "https://efts.sec.gov/LATEST/search-index?q=x", "https://www.sec.gov/files/dera/data/financial-statement-and-notes-data-sets/2026q1_notes.zip",
              "https://example.com/api/xbrl/frames/us-gaap/NetIncomeLoss/USD/CY2019.json", "http://data.sec.gov/submissions/CIK0000789019.json",
              "https://data.sec.gov/submissions/CIK0000789019.json?x=1", "https://data.sec.gov/files/x.json", "https://data.sec.gov:8443/submissions/CIK0000789019.json",
              "https://fred.stlouisfed.org/series/DGS10"):
        ck.raises("refused before any request: %s" % u[:70], Refused, lambda u=u: check_url(u))
    ck.eq("the allowed targets", [check_url(u)[1] for u in ("https://data.sec.gov/submissions/CIK0000789019.json", "https://data.sec.gov/api/xbrl/companyfacts/CIK0000789019.json",
                                                            "https://data.sec.gov/api/xbrl/frames/us-gaap/NetIncomeLoss/USD/CY2019.json", "https://data.sec.gov/submissions/CIK0000789019-submissions-001.json")],
          ["/submissions/CIK0000789019.json", "/api/xbrl/companyfacts/CIK0000789019.json", "/api/xbrl/frames/us-gaap/NetIncomeLoss/USD/CY2019.json", "/submissions/CIK0000789019-submissions-001.json"])
    with tempfile.TemporaryDirectory(prefix="rrt_g15_", ignore_cleanup_errors=True) as tmp:
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "nouser"))
        code, said = go(environ={})
        ck.eq("a fetch with SEC_UA unset exits 2 and makes no request", (code, len(calls)), (2, 0))
        ck.ok("...and prints no value", all(FIXTURE_CONTACT not in s for s in said), "")
        ck.raises("a contact string an HTTP header cannot carry is refused", Refused, lambda: fetch_rig(os.path.join(tmp, "lat"))[0](environ={"SEC_UA": "Fixture \u2019 contact"}))
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "a"), max_requests=3)
        code, said = go()
        ck.eq("a good slice sends exactly the requests allowed", (code, len(calls)), (4, 3))
        if calls:
            ck.eq("...to data.sec.gov with the contact string and identity encoding", (calls[0][0], calls[0][2].get("User-Agent"), calls[0][2].get("Accept-Encoding")), (HOST, FIXTURE_CONTACT, "identity"))
        ck.ok("...and the contact string is in no byte written", FIXTURE_CONTACT.encode("utf-8") not in bytes_of_tree(os.path.join(tmp, "a")), "")
        rows = fetch_rows(ns.out)
        gaps = []
        for r0, r1 in zip(rows, rows[1:]):
            end0 = parse_utc_ms(r0["utc_time"]) + dt.timedelta(seconds=float(r0["elapsed_s"]))
            gaps.append((parse_utc_ms(r1["utc_time"]) - end0).total_seconds())
        ck.ok("requests are at least 1.0 s apart (0.9 s is a violation)", bool(gaps) and min(gaps) >= 1.0 - 1e-9, str(gaps))
        ck.ok("every fetch_log row names data.sec.gov and no status is 403, 429 or 3xx", all(r["host"] == HOST and r["status"] not in ("403", "429") and not r["status"].startswith("3") for r in rows), "")
        code2, said2 = go()
        paths2 = [c[1] for c in calls[3:]]
        ck.ok("a resumed run does not request a body it already holds", len(set(c[1] for c in calls[:3]) & set(paths2)) == 0 and len(paths2) == 3, str(paths2))
        ck.ok("a second slice stops by its limit too", code2 == 4, str(code2))
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "echo"), lambda t: (403, ("Forbidden for %s" % FIXTURE_CONTACT).encode("utf-8"), {}))
        code, said = go()
        ck.eq("a 403 that echoes the contact string latches STOP", code, 2)
        ck.ok("...but no byte of the contact string is written, STOP included", FIXTURE_CONTACT.encode("utf-8") not in bytes_of_tree(os.path.join(tmp, "echo")) and os.path.exists(os.path.join(ns.cache, STOP_NAME)), "")
        ck.raises("a write that would hold the contact string is refused", Refused, lambda: write_text(os.path.join(tmp, "x.txt"), "x " + FIXTURE_CONTACT))
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "r301"), (301, b"", {"location": "/submissions/CIK0000000001.json"}))
        go()
        ck.eq("a redirect is not followed", len(calls), 1)
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "r429"), (429, b"x", {}))
        go()
        ck.eq("a 429 is never retried", len(calls), 1)
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "r500"), (500, b"x", {}))
        go()
        ck.eq("a 500 is never retried", len(calls), 1)
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "cap"))
        code, said = go(ns_=argparse.Namespace(**dict(vars(ns), max_requests=5)))
        ck.eq("--max-requests is a cap: five requests, then exit 4", (code, len(calls)), (4, 5))
    ck.eq("the per-run caps are 1,000, 600 and 250", dict(CAPS), {"submissions": 1000, "companyfacts": 600, "frames": 250})
    forget_secrets()


def clone_vintage(w, new, mutate=None):
    """A second vintage in the same cache: the first one's extracts re-stamped, one value changed by mutate(rows) on the companyfacts rows, and its vintages.csv rows copied."""
    old = w["vintage"]
    nd = os.path.join(w["cache"], new)
    shutil.copytree(w["vdir"], nd)
    for name in EXTRACT_CSVS:
        h, rows = read_csv_rows(os.path.join(nd, name))
        for r in rows:
            r[0] = new
        if name == "cf_extract.csv" and mutate:
            mutate(rows)
        write_text(os.path.join(nd, name), render_csv(name, rows, source_line_vintage(new, "test")))
    vp = os.path.join(w["out"], "vintages.csv")
    h, rows = read_csv_rows(vp)
    rows = rows + [[new] + r[1:] for r in rows if r[0] == old]
    write_text(vp, render_csv("vintages.csv", rows, "# source: test"))
    return new


def t_g16(ck):
    w = get_world()
    wa = copy_world(w, "g16a")
    p = os.path.join(wa["vdir"], "cf_extract.csv")
    h, rows = read_csv_rows(p)
    rows[0][0] = "20260101"
    write_text(p, render_csv("cf_extract.csv", rows, source_line_vintage(wa["vintage"], "test")))
    ck.raises("a row of another vintage stops the build", DataError, lambda: world_loader(wa, "full")())
    wb = copy_world(w, "g16b")
    t1, f1, c1 = build_world(wb, "full")
    placebo_before = read_file(os.path.join(wb["out"], "placebo.csv"), "r")
    s1_before = [r for r in csv_body(t1["registered.csv"])[1] if r[0] in ("S1", "S1P")]

    def bump(rows):
        for r in rows:
            if r[1] == "0000789019" and r[2] == CL_T and r[4] == "2025-06-30":
                r[5] = str(int(r[5]) + 77000000)

    v2 = clone_vintage(wb, "20261201", bump)
    t2, f2, c2 = build_world(wb, "full", vintage=v2)
    reg = csv_body(read_file(os.path.join(wb["out"], "registered.csv"), "r"))[1]
    s1_after = [r for r in reg if r[0] in ("S1", "S1P")]
    ck.eq("S1 and S1P are scored once: the later vintage leaves them as they were", s1_after, s1_before)
    ck.eq("S2 and S2P have a row for each vintage while pending", sorted((r[0], r[3], r[15]) for r in reg if r[0] in ("S2", "S2P")),
          [("S2", "20261105", "PENDING"), ("S2", "20261201", "PENDING"), ("S2P", "20261105", "PENDING"), ("S2P", "20261201", "PENDING")])
    ck.eq("the placebo band stays frozen", read_file(os.path.join(wb["out"], "placebo.csv"), "r"), placebo_before)
    rev = csv_body(t2["revisions.csv"])[1]
    ck.ok("revisions.csv lists what moved between the two vintages", bool(rev) and all(r[0] == "20261105" and r[1] == "20261201" for r in rev) and any(r[4] == "t_usd" and r[2] == "fy2023_fy2025" for r in rev), str(rev[:3]))
    t3, f3, c3 = build_world(wb, "full", vintage=v2)
    ck.eq("a second build of the same vintage is byte-identical", {n: sha256_of(x.encode("utf-8")) for n, x in t3.items()}, {n: sha256_of(x.encode("utf-8")) for n, x in t2.items()})
    h1 = [["v1", "w", "s", "t_usd", "5", "usd", "1"], ["v2", "w", "s", "t_usd", "5", "usd", "1"], ["v1", "w", "s", "n_firms", "3", "count", "1"], ["v2", "w", "s", "n_firms", "4", "count", "1"]]
    ck.eq("revisions are regenerated: only the statistic that differs is listed", revision_rows(h1), [["v1", "v2", "w", "s", "n_firms", "3", "4"]])


def t_g17(ck):
    clean = {n: "# source: x\n" + ",".join(ALLOW[n]) + "\n1,2,3\n" for n in ALLOW_ORDER[:15]}
    clean["README.md"], clean["SOURCES.md"] = "A plain README.\n", "Plain sources.\n"
    ck.eq("on the clean folder the leak guard passes", leak_problems(clean), [])
    for nm, body in (("data.json", "{}"), ("x.zip", b"PK\x03\x04junk"), ("STOP_rrt", "status: 403\n"), ("page.html", "<html>")):
        bad = dict(clean)
        bad[nm] = body
        ck.ok("%s is reported as a raw file" % nm, any("raw or forbidden" in p and nm in p for p in leak_problems(bad)), str(leak_problems(bad)))
    bad = dict(clean)
    bad["SOURCES.md"] = "see " + "/Us" + "ers/someone/file\n"
    ck.ok("a local path is reported", any("local path" in p for p in leak_problems(bad)), "")
    bad = dict(clean)
    bad["README.md"] = "write to a" + chr(64) + "b\n"
    ck.ok("an at sign is reported", any("at sign" in p for p in leak_problems(bad)), "")
    bad = dict(clean)
    bad["coverage.csv"] = clean["coverage.csv"] + "x,y,z,1,1,\n"
    ck.eq("a plain extra row is not a leak", leak_problems(bad), [])
    ck.ok("the verdict-word scan reports MATERIAL in a cell", bool(verdict_problems({"checks.csv": "C99,a,b,c,MATERIAL\n"})) and not verdict_problems({"firms.csv": "0001,Vulcan Materials Co\n"}), "")
    ck.ok("the value scan reports a label outside the allowed set", bool(value_problems({"registered.csv": "# source: x\n" + ",".join(ALLOW["registered.csv"]) + "\nS1,fy2023_fy2025,primary,v,1,1,1,1,1,1,1,1,1,none,with_growth,MATERIAL_SHARE,none,a,b\n"})), "")


def t_g18(ck):
    w = get_world()
    texts, failed, c = build_world(copy_world(w, "g18"), "full")
    rec = csv_body(texts["receivables.csv"])[1]
    ck.ok("every receivables row is marked collection, not recognition", bool(rec) and all(r[3] == "collection_not_recognition" for r in rec), str(rec[:2]))
    ck.eq("AR days use A1 only: a firm with A2 and A3 but no A1 has no receivables series", ar_series(mkfirm({AR_A2: [own_instant(AR_A2, y, 5) for y in range(2019, 2027)], AR_A3: [own_instant(AR_A3, y, 5) for y in range(2019, 2027)]}), (2022, 2023, 2024, 2025)), None)
    lv = [r for r in rec if r[1] == "level"]
    ck.ok("AR days are over receivables of A1 only: sum AR / sum revenue x 365", bool(lv) and abs(Dm(lv[0][7]) - Dm(lv[0][5]) / Dm(lv[0][6]) * 365) < Decimal("0.001"), str(lv[:1]))
    tw = [r for r in rec if r[1] == "window_t"]
    ck.ok("T on receivables is its own row and is not zero here", bool(tw) and tw[0][8] not in ("", "0"), str(tw))
    ck.ok("C07 passes: T is the sum of the contributions, T on receivables added to nothing", "C07" not in failed, str(failed))
    pan = csv_body(texts["panel.csv"])[1]
    ck.ok("N is contract assets minus contract liabilities in every panel row: contract costs are not in it", all(abs(Dm(r[10]) - (Dm(r[8]) - Dm(r[9]))) <= 1 for r in pan), "")
    hm = {(r[1], r[2], r[3]): r[4] for r in csv_body(texts["headline.csv"])[1]}
    ck.ok("contract costs and remaining performance obligations are described in days", (("fy2023_fy2025", "primary", "contract_cost_days_fy2025") in hm) and (("fy2023_fy2025", "primary", "rpo_days_fy2025") in hm), "")
    f = quick_firm([1000 * M_] * 8, [100 * M_] * 8, cl=[100 * M_ + k * 10 * M_ for k in range(8)])
    f.facts.update(inst_series(CL_T, [100 * M_ + k * 10 * M_ for k in range(8)]))
    f.facts[CF_CL] = [own_duration(CF_CL, y, -10 * M_) for y in range(2020, 2023)]
    cl = {f.cik: classify(f, (2019, 2020, 2021, 2022))}
    sg = cf_sign({f.cik: f}, [f.cik], cl)
    ck.eq("a cash-flow tag that opposes the balance-sheet change gets sign -1, set from the data", sg["cl"], (-1, 0, 3))
    g = quick_firm([1000 * M_] * 8, [100 * M_] * 8, cl=[100 * M_ + k * 10 * M_ for k in range(8)])
    g.facts[CF_CL] = [own_duration(CF_CL, y, 10 * M_) for y in range(2020, 2023)]
    cl2 = {g.cik: classify(g, (2019, 2020, 2021, 2022))}
    sg2 = cf_sign({g.cik: g}, [g.cik], cl2)
    ck.eq("...and one that agrees gets +1", sg2["cl"], (1, 3, 0))
    ck.eq("...and a family with no balance-sheet tag has no sign", sg2["ca"][0], None)


def t_g19(ck):
    src = read_file(os.path.abspath(__file__), "r")
    ck.eq("the script's own source passes the isolation scan", isolation_problems(src), [])
    ck.ok("a read of data/w3_tax/results.json is reported", bool(isolation_problems("def f():\n    open('data/w3_tax/results.json')\n")), "")
    ck.ok("a read of another project folder is reported", bool(isolation_problems("def f():\n    open('data/nport/nport_2026Q3.csv')\n")), "")
    ck.ok("a read of the series table is reported", bool(isolation_problems("def f():\n    read_file('data/series.tsv')\n")), "")
    ck.ok("a read of a secrets file is reported", bool(isolation_problems("def f():\n    open('keys/secrets.env')\n")), "")
    ck.ok("an absolute path is reported", bool(isolation_problems("def f():\n    open('/etc/passwd')\n")), "")
    ck.eq("the panel and the script's own folders are allowed", isolation_problems("def f(cache):\n    open('data/w3_tax/firm_tax_panel.csv')\n    read_file('data/vintages/rev_recognition_timing/x')\n    open(os.path.join(cache, 'cf_extract.csv'))\n"), [])


# ---- end to end ----
SET_S1 = ["0000789019", "0000320193", "0001018724", "0000100001", "0000100002", "0000100006", "0000100011", "0000100012", "0000100013", "0000100014", "0000100015", "0000100016"]
SET_P2 = ["0000789019", "0000320193", "0001018724", "0000100001", "0000100002", "0000100010", "0000100011", "0000100012", "0000100013", "0000100014", "0000100015", "0000100016"]
SET_P1A = SET_P2 + ["0000100008"]
SET_P1B = list(SET_P2)


def ref_series(sp, comp, y, window_years_):
    """The reference value (written a second time, by hand) of one component for one firm and year."""
    v = sp["vals"]
    def g(tag):
        if tag not in v or (tag, y) in sp["drop"]:
            return 0
        return v[tag][y - 2019]
    cik = sp["cik"]
    if comp == "rev":
        for t in (REV_R2, REV_R3, REV_ANY):
            if t in v:
                return v[t][y - 2019]
    if comp == "ni":
        return v[NI_TAG][y - 2019]
    if comp == "ca":
        return g(CA_T)
    if comp == "cl":
        if cik in ("0000320193", "0000100016"):
            return g(CL_C) + g(CL_N)
        if cik == "0001018724":
            return g(DEF_C) + g(DEF_N)
        return g(CL_T)


def ref_window(sp, b, e):
    from fractions import Fraction as Fr
    ys = range(b - 1, e + 1)
    N = {y: ref_series(sp, "ca", y, ys) - ref_series(sp, "cl", y, ys) for y in ys}
    R = {y: ref_series(sp, "rev", y, ys) for y in ys}
    return fr_to_dec(ref_T(N, R, b, e)), ref_series(sp, "ni", e, ys) - ref_series(sp, "ni", b, ys), ref_series(sp, "ni", b, ys), ref_series(sp, "rev", e, ys)


def t_x_build(ck):
    w = get_world()
    wc_ = copy_world(w, "x1")
    pre, failed_pre, cpre = build_world(wc_, "pre")
    ck.eq("the pre stage's checks have no FAIL", failed_pre, [])
    placebo_stat = os.stat(os.path.join(wc_["out"], "placebo.csv"))
    placebo_text = read_file(os.path.join(wc_["out"], "placebo.csv"), "r")
    full, failed, c = build_world(wc_, "full")
    ck.eq("the full stage's FAIL checks: none", failed, [])
    ck.eq("...placebo.csv is the pre stage's file, untouched (same bytes, same age)", (read_file(os.path.join(wc_["out"], "placebo.csv"), "r"), os.stat(os.path.join(wc_["out"], "placebo.csv")).st_mtime_ns), (placebo_text, placebo_stat.st_mtime_ns))
    names = sorted(n for n in os.listdir(wc_["out"]) if not n.startswith("."))
    ck.eq("the seventeen committed names", names, sorted(COMMITTED))
    files = {n: read_file(os.path.join(wc_["out"], n), "r") for n in names}
    ck.eq("the folder guards find nothing", all_folder_problems(files), [])
    st = {r[0]: r[4] for r in c["checks"]}
    ck.eq("C11, C12, C13, C14, C07, C08, C09, C10, C05 PASS", [st[k] for k in ("C11", "C12", "C13", "C14", "C07", "C08", "C09", "C10", "C05")], ["PASS"] * 9)
    ck.eq("C02, C03 and C04 warn on the synthetic counts (they are pins on the real data)", [st[k] for k in ("C02", "C03", "C04")], ["WARN"] * 3)
    ck.eq("C01 passes against the test's pinned panel", st["C01"], "PASS")
    firms = {r[0]: r for r in csv_body(files["firms.csv"])[1]}
    want = {"0000100003": "financial_sic", "0000100004": "no_sic", "0000100005": "no_sec_record", "0000100006": "in_scope", "0000100007": "end_mismatch", "0000100008": "year_gap",
            "0000100009": "tiny_revenue", "0000100010": "year_gap", "0000100001": "in_scope", "0000789019": "in_scope"}
    ck.eq("statuses on the S1 window", {k: firms[k][5] for k in want}, want)
    ck.eq("flags on the S1 window", {k: firms[k][6] for k in ("0000100011", "0000100012", "0000100013", "0000100014", "0000100015", "0000100010")},
          {"0000100011": "rev_fallback", "0000100012": "acq2", "0000100013": "disc_ops", "0000100014": "extreme_r", "0000100015": "total_gt_parts", "0000100010": "gap_n"})
    ck.eq("the title-cased names are written", firms["0000789019"][2], "Synth 9019 Corp")
    ck.eq("the shared CIK joins its tickers", firms["0000320193"][1], "AAPL|AAPX")
    contrib = csv_body(files["contributions.csv"])[1]
    specs = {sp["cik"]: sp for sp in w["specs"]}
    prim = {r[2]: r for r in contrib if r[0] == "fy2023_fy2025" and r[1] == "primary"}
    ck.eq("the primary sample is the twelve in-scope firms", sorted(prim), sorted(SET_S1))
    tsum, dsum_ = Decimal(0), Decimal(0)
    bad = []
    for cik in SET_S1:
        t, dni, ni_b, rev_e = ref_window(specs[cik], 2023, 2025)
        if prim[cik][6] != usd(q0(t)) or prim[cik][7] != str(dni):
            bad.append((cik, prim[cik][6], usd(q0(t))))
        tsum += q0(t)
        dsum_ += dni
    ck.eq("each firm's T_i and dNI equal the hand-worked reference (fractions)", bad, [])
    reg = {r[0]: r for r in csv_body(files["registered.csv"])[1]}
    ck.eq("S1's T and dNI are the sums of the cells", (reg["S1"][6], reg["S1"][7]), (usd(tsum), usd(dsum_)))
    share = tsum / dsum_ * 100
    ck.ok("S1's share is T / dNI in percent, to three decimals", reg["S1"][9] == pct3(share), "%s vs %s" % (reg["S1"][9], pct3(share)))
    lab = "SHARE_BELOW_10" if abs(share) < 10 else ("SHARE_10_TO_25" if abs(share) <= 25 else "SHARE_ABOVE_25")
    ck.eq("...its label and direction", (reg["S1"][15], reg["S1"][14]), (lab, "with_growth" if tsum > 0 else ("against_growth" if tsum < 0 else "zero")))
    ck.eq("S1P and S2P rows exist; S2 and S2P are PENDING; every row carries the two hashes", ([reg[k][15] for k in ("S2", "S2P")], {(r[17], r[18]) for r in reg.values()}),
          (["PENDING", "PENDING"], {(SPEC_PREREG_SHA256, SPEC_POP_SHA256)}))
    pl = {r[0]: r for r in csv_body(files["placebo.csv"])[1]}
    ck.eq("the placebo windows' firm counts", {k: pl[k][3] for k in pl}, {"fy2020_fy2022": "12", "fy2020_fy2021": "13", "fy2021_fy2022": "12"})
    for wname, (b, e), sset in (("fy2020_fy2022", (2020, 2022), SET_P2), ("fy2020_fy2021", (2020, 2021), SET_P1A), ("fy2021_fy2022", (2021, 2022), SET_P1B)):
        pc = sorted(r[2] for r in contrib if r[0] == wname and r[1] == "primary")
        ck.eq("placebo %s: the firm set" % wname, pc, sorted(sset))
        tt = sum(q0(ref_window(specs[k], b, e)[0]) for k in sset)
        ck.eq("placebo %s: T equals the reference sum" % wname, pl[wname][4], usd(tt))
    hm = {(r[1], r[2], r[3]): r[4] for r in csv_body(files["headline.csv"])[1]}
    ck.eq("sens_gap0 adds the one firm whose only gap is gap_n", (hm[("fy2023_fy2025", "sens_gap0", "n_firms")], hm[("fy2023_fy2025", "primary", "n_firms")]), ("13", "12"))
    ck.eq("sens_acq, sens_disc, sens_trim, sens_r2only, sens_leave1 each drop one firm", [hm[("fy2023_fy2025", s, "n_firms")] for s in ("sens_acq", "sens_disc", "sens_trim", "sens_r2only", "sens_leave1")], ["11"] * 5)
    ck.eq("the firms without a fiscal 2025 net income are counted, not imputed", hm[("fy2023_fy2025", "primary", "ni_2025_all500_missing")], "1")
    # R3-1: the same-filing sample against the hand-worked reference (RTL's FY2022 revenue is recast in its FY2023 10-K; AMZN's FY2025 10-K omits one FY2024 comparative)
    from fractions import Fraction as Fr
    def ref_sf(sp):
        t0, _, _, _ = ref_window(sp, 2023, 2025)
        if sp["cik"] != "0000100002":
            return t0
        ys = range(2022, 2026)
        N = {y: ref_series(sp, "ca", y, ys) - ref_series(sp, "cl", y, ys) for y in ys}
        R = {y: ref_series(sp, "rev", y, ys) for y in ys}
        R22 = sp["later"][(REV_R2, 2022)]
        return fr_to_dec((Fr(N[2025]) - Fr(N[2024]) / Fr(R[2024]) * Fr(R[2025])) - (Fr(N[2023]) - Fr(N[2022]) / Fr(R22) * Fr(R[2023])))
    sf_rows = [r for r in contrib if r[0] == "fy2023_fy2025" and r[1] == "sens_samefiling"]
    ck.eq("sens_samefiling: the twelve primary firms", sorted(r[2] for r in sf_rows), sorted(SET_S1))
    ck.eq("sens_samefiling: each firm's T_i equals the hand-worked reference", sorted((r[2], r[6]) for r in sf_rows), sorted((k, usd(q0(ref_sf(specs[k])))) for k in SET_S1))
    ck.eq("sens_samefiling: headline T is the sum of the cells", hm[("fy2023_fy2025", "sens_samefiling", "t_usd")], usd(sum(q0(ref_sf(specs[k])) for k in SET_S1)))
    ck.ok("sens_samefiling differs from the primary only through RTL", hm[("fy2023_fy2025", "sens_samefiling", "t_usd")] != hm[("fy2023_fy2025", "primary", "t_usd")] and
          sum(1 for r in sf_rows if r[6] != prim[r[2]][6]) == 1, "")
    ck.eq("sens_samefiling: one firm falls back (AMZN) and one firm's comparative is restated (RTL)", (hm[("fy2023_fy2025", "sens_samefiling", "n_samefiling_fallback")], hm[("fy2023_fy2025", "sens_samefiling", "n_samefiling_restated")]), ("1", "1"))
    # R3-2: leave-one-out against an independent recomputation
    cells = {k: (Fr(int(prim[k][6])), Fr(int(prim[k][7])), Fr(ref_window(specs[k], 2023, 2025)[2])) for k in SET_S1}
    Tt, Dd, NBb = (sum(cells[k][i] for k in cells) for i in range(3))
    TPp = sum(max(cells[k][0], 0) for k in cells)
    cross, n_p = [], 0
    for k, (t_, d_, nb_) in cells.items():
        nb2, d2 = NBb - nb_, Dd - d_
        if nb2 <= 0 or d2 < Fr(2, 100) * nb2:
            continue
        if abs(Tt - t_) / d2 * 100 < 10:
            cross.append(k)
        if (TPp - max(t_, 0)) / d2 * 100 <= 25 and TPp / Dd * 100 > 25:
            n_p += 1
    ck.eq("leave-one-out: the counts equal an independent recomputation", (hm[("fy2023_fy2025", "primary", "n_leave1_s1_below_10")], hm[("fy2023_fy2025", "primary", "n_leave1_s1p_below_25")]), (str(len(cross)), str(n_p)))
    ck.ok("...and the firms that take S1 below 10% are named in the README", bool(cross) and all(specs[k]["tickers"][0] in files["README.md"] for k in cross), str(cross))
    rd = files["README.md"]
    paras = rd.split("\n\n")
    ck.ok("README: the opening states the ceiling first, then the figures with labels, then the denial sentence, then one sentence on fragility", rd.count(DENIAL_SENTENCE) == 1 and
          paras[1].startswith("This is a ceiling for the tagged balances under assumption A1, not an estimate") and paras[1].index("at most") < paras[1].index("S1, label") < paras[1].index(DENIAL_SENTENCE)
          and paras[1].rstrip().endswith("gives %s." % pctx(Dm(hm[("fy2023_fy2025", "sens_samefiling", "share_pct")]))) and "These labels rest on" in paras[1].split(DENIAL_SENTENCE)[1], paras[1][-400:])
    ck.ok("README: nothing says the growth came from timing, and the direction wording comes after the ceiling", "came from" not in rd and rd.index("the timing added to reported growth") > rd.index("ceiling"), "")
    ck.ok("README: the sensitivity row says the same-filing sample was added after the result was seen", "sens_samefiling" in rd and "Added after the result was seen, by an independent check on 28 October 2026" in rd, "")
    ck.ok("README: every flag and every status is defined and the cold-read terms are explained", all("`%s`:" % f in rd for f in FLAG_ORDER) and all(("| %s |" % st_) in rd for st_ in STATUS_ORDER) and
          all(w_ in rd for w_ in ("Central Index Key", "fiscalYearEnd field", "PENDING_THIN (pending", "NB1 (noise band 1)", "NB2 (noise band 2)", "Alphabet, Amazon, Meta", "There is no A2", "an extension")) and
          not any(w_ in rd for w_ in ("W3 firm set", "the supervisor's", "megacap firms of 2.1")), "")
    ck.ok("README: the ceiling sentence and the contributor sentence appear", CEILING_PHRASE in rd and CONTRIBUTOR_SENTENCE in rd, "")
    named = sorted(k for k in SET_S1 if firms[k][2] and firms[k][2] in rd)
    ck.ok("README: no verdict word, and a firm is named only where R3-2 asks for it (the firms whose removal takes S1 below 10%)", not VERDICT_RX.search(rd) and named == sorted(cross), "%s vs %s" % (named, sorted(cross)))
    ck.ok("README: its links are reachable relative paths", "(../../_research/2026-10-28-Revenue-Recognition-Timing-Spec.md)" in rd and "(SOURCES.md)" in rd, "")
    ck.ok("SOURCES.md: the 57 author requests, the builder decisions, the measured signs", "| 57 |" in files["SOURCES.md"] and "## Builder decisions" in files["SOURCES.md"] and "Cash-flow sign convention, measured" in files["SOURCES.md"], "")
    ck.ok("no output holds a verdict word", not any(VERDICT_RX.search(x) for x in files.values()), "")
    ck.ok("the contact string is in no output", all(FIXTURE_CONTACT not in x for x in files.values()), "")
    d1 = {n: sha256_of(x.encode("utf-8")) for n, x in full.items()}
    full2, _, _ = build_world(wc_, "full")
    ck.eq("a second build over the same inputs is byte-identical", {n: sha256_of(x.encode("utf-8")) for n, x in full2.items()}, d1)
    ck.raises("a pre build is refused for a vintage already scored", Refused, lambda: run_build(argparse.Namespace(vintage=wc_["vintage"], stage="pre", cache=wc_["cache"], out=wc_["out"], panel=wc_["panel"], raw=wc_["raw"])))
    p = os.path.join(wc_["raw"], raw_name("/submissions/CIK0000789019.json"))
    write_bytes(p, read_file(p, "rb") + b" ")
    texts_t, failed_t, _ = build_world(wc_, "full")
    ck.ok("an edited raw body fails C13", "C13" in failed_t, str(failed_t))


def t_x_s2(ck):
    with tempfile.TemporaryDirectory(prefix="rrt_s2_", ignore_cleanup_errors=True) as tmp:
        w = make_world(tmp, vintage="20270501", fy2026=True)
        texts, failed, c = build_world(w, "full")
        reg = {r[0]: r for r in csv_body(texts["registered.csv"])[1]}
        ck.eq("S2 and S2P are scored from the S2 date (no PENDING)", (reg["S2"][15] in ("PENDING", "PENDING_THIN"), reg["S2P"][15] in ("PENDING", "PENDING_THIN")), (False, False))
        specs = {sp["cik"]: sp for sp in w["specs"]}
        s2set = ["0000320193", "0001018724", "0000100001", "0000100002", "0000100006", "0000100008", "0000100010", "0000100011", "0000100012", "0000100013", "0000100014", "0000100015", "0000100016"]
        got = sorted(r[2] for r in csv_body(texts["contributions.csv"])[1] if r[0] == "fy2025_fy2026" and r[1] == "s2_eligible")
        ck.eq("the S2 sample is the firms in scope whose D_2026 is in range (not the June-year firm)", got, sorted(s2set))
        tt = sum(q0(ref_window(specs[k], 2025, 2026)[0]) for k in s2set)
        ck.eq("S2's T equals the hand-worked reference sum", reg["S2"][6], usd(tt))
        ck.eq("S2 has n_firms", reg["S2"][4], str(len(s2set)))
        ck.eq("no FAIL check", failed, [])
        hm = {(r[1], r[2], r[3]): r[4] for r in csv_body(texts["headline.csv"])[1]}
        ck.eq("coverage of the eligible firms is 100%", hm[("fy2025_fy2026", "s2_eligible", "coverage_pct")], "100.000")
        for r in csv_body(texts["panel.csv"])[1]:
            if r[0] == "fy2025_fy2026":
                break
        else:
            ck.ok("the S2 window has panel rows", False, "")
    with tempfile.TemporaryDirectory(prefix="rrt_s2t_", ignore_cleanup_errors=True) as tmp:
        def drop26(specs):
            for sp in specs:
                if sp["cik"] not in ("0000100001", "0000100002"):
                    sp["ends"].pop(2026, None)
        w = make_world(tmp, vintage="20270601", fy2026=True, tweak=drop26)
        texts, failed, c = build_world(w, "full")
        reg = {r[0]: r for r in csv_body(texts["registered.csv"])[1]}
        ck.eq("with fewer than 70% of the eligible firms filed, S2 and S2P are PENDING_THIN", (reg["S2"][15], reg["S2P"][15]), ("PENDING_THIN", "PENDING_THIN"))
    with tempfile.TemporaryDirectory(prefix="rrt_s2v_", ignore_cleanup_errors=True) as tmp:
        def drop26b(specs):
            for sp in specs:
                if sp["cik"] not in ("0000100001", "0000100002"):
                    sp["ends"].pop(2026, None)
        w = make_world(tmp, vintage="20270801", fy2026=True, tweak=drop26b)
        texts, failed, c = build_world(w, "full")
        reg = {r[0]: r for r in csv_body(texts["registered.csv"])[1]}
        ck.eq("still thin on 2027-08-01: VOID with reason thin_coverage", (reg["S2"][15], reg["S2"][16]), ("VOID", "thin_coverage"))


def t_x_s2_changed_fy(ck):
    """Ruling S2-R1 end to end: one eligible December firm has a FY2026 10-K ending 2026-06-30."""
    with tempfile.TemporaryDirectory(prefix="rrt_s2c_", ignore_cleanup_errors=True) as tmp:
        def switch(specs):
            for sp in specs:
                if sp["cik"] == "0000100001":
                    sp["ends"][2026] = "2026-06-30"
        w = make_world(tmp, vintage="20270501", fy2026=True, tweak=switch)
        texts, failed, c = build_world(w, "full")
        hm = {(r[1], r[2], r[3]): r[4] for r in csv_body(texts["headline.csv"])[1]}
        g = lambda k: hm[("fy2025_fy2026", "s2_eligible", k)]
        ck.eq("the eligible firms and the four states add up: 13 = 12 + 1 + 0 + 0", (g("n_eligible_fy2025"), g("n_with_fy2026_10k"), g("n_s2_end_mismatch"), g("n_s2_fy_ambiguous"), g("n_s2_no_fy2026_10k")), ("13", "12", "1", "0", "0"))
        ck.eq("coverage is 12 of 13", g("coverage_pct"), "92.308")
        got = sorted(r[2] for r in csv_body(texts["contributions.csv"])[1] if r[0] == "fy2025_fy2026" and r[1] == "s2_eligible")
        ck.ok("the changed-year firm is not in the S2 sample", "0000100001" not in got and len(got) == 12, str(got))
        reg = {r[0]: r for r in csv_body(texts["registered.csv"])[1]}
        ck.eq("S2 is scored on 12 firms", (reg["S2"][4], reg["S2"][15] in ("PENDING", "PENDING_THIN")), ("12", False))
        ck.ok("the README states the status, the count and the ticker", "end_mismatch: never counted, never scored" in texts["README.md"] and "NOCT" in texts["README.md"], "")
        ck.ok("the README says what the data show, without asserting that the year-end changed (R3-5)", "NOCT: the submissions file says fiscalYearEnd 1231, but its latest original 10-K covers the year to 30 June 2026 and no 10-KT (transition report) has been "
              "filed; the data do not show a completed change of year-end." in texts["README.md"] and "year-end changed" not in texts["README.md"] and "usually because" not in texts["README.md"], "")
        ck.eq("no FAIL check", failed, [])
    with tempfile.TemporaryDirectory(prefix="rrt_s2d_", ignore_cleanup_errors=True) as tmp:
        def thin(specs):
            for sp in specs:
                if sp["cik"] in ("0000320193", "0001018724", "0000100006"):
                    sp["ends"].pop(2026, None)
                elif sp["cik"] == "0000100001":
                    sp["ends"][2026] = "2026-06-30"
        w = make_world(tmp, vintage="20270601", fy2026=True, tweak=thin)
        texts, failed, c = build_world(w, "full")
        hm = {(r[1], r[2], r[3]): r[4] for r in csv_body(texts["headline.csv"])[1]}
        g = lambda k: hm[("fy2025_fy2026", "s2_eligible", k)]
        ck.eq("9 of 13 filed inside the window, 1 outside it, 3 not at all", (g("n_with_fy2026_10k"), g("n_s2_end_mismatch"), g("n_s2_no_fy2026_10k"), g("coverage_pct")), ("9", "1", "3", "69.231"))
        ck.eq("a changed-year filer does not lift coverage over 70%: S2 reads PENDING_THIN", [r[15] for r in csv_body(texts["registered.csv"])[1] if r[0] == "S2"], ["PENDING_THIN"])


def t_x_fetch(ck):
    forget_secrets()
    with tempfile.TemporaryDirectory(prefix="rrt_xf_", ignore_cleanup_errors=True) as tmp:
        specs = world_specs()[:4]
        ciks = [sp["cik"] for sp in specs]
        sp_by = {sp["cik"]: sp for sp in specs}
        fdocs = frames_docs(specs, "20270115")

        def resp(target):
            m = SUB_RX.match(target)
            if m:
                return 200, jdump(subs_doc(sp_by[m.group(1)])), {}
            m = CF_RX.match(target)
            if m:
                return 200, jdump(facts_doc(sp_by[m.group(1)], "x")), {}
            m = FRAME_RX.match(target)
            return 200, jdump(fdocs[(m.group(1), m.group(2))]), {}

        go, calls, ns, clock = fetch_rig(tmp, resp, mode="fetch-companyfacts", ciks=ciks)
        ck.raises("fetch-companyfacts refuses to start without the submissions extract", Refused, lambda: go())
        ck.eq("...and makes no request", len(calls), 0)
        ns.cmd = "fetch-submissions"
        code, said = go()
        ck.eq("fetch-submissions: exit 0 and one request per CIK (no older pages here)", (code, len(calls)), (0, 4))
        ns.cmd = "fetch-companyfacts"
        code, said = go()
        ck.eq("fetch-companyfacts: exit 0 and one request per CIK", (code, len(calls)), (0, 8))
        ns.cmd = "fetch-frames"
        code, said = go()
        ck.eq("fetch-frames: exit 0 and 66 requests", (code, len(calls)), (0, 8 + 66))
        ns.cmd = "fetch-submissions"
        code, said = go()
        ck.eq("a second run requests nothing: every body is cached", (code, len(calls)), (0, 74))
        vd = os.path.join(ns.cache, ns.vintage)
        ck.eq("the three extracts exist", sorted(n for n in os.listdir(vd) if n.endswith(".csv")), ["cf_extract.csv", "frames_extract.csv", "submissions_extract.csv"])
        ck.ok("the extracts have the allowlisted headers and no row of another vintage", all(read_csv_rows(os.path.join(vd, n))[0] == ALLOW[n] and all(r[0] == ns.vintage for r in read_csv_rows(os.path.join(vd, n))[1]) for n in EXTRACT_CSVS), "")
        ck.ok("cf_extract holds no fact after D_2025 (the vintage is before 2027-05-01)", all(r[4] <= "2025-12-31" for r in read_csv_rows(os.path.join(vd, "cf_extract.csv"))[1] if r[1] == "0000320193"), "")
        ck.ok("no byte of the contact string is written anywhere", FIXTURE_CONTACT.encode("utf-8") not in bytes_of_tree(tmp), "")
        rows = fetch_rows(ns.out)
        ck.ok("every fetch_log row names data.sec.gov", all(r["host"] == HOST for r in rows) and len(rows) == 74, str(len(rows)))
        ck.ok("every kept body is a vintages.csv row with its digest", len(vint_rows(ns.out)) == 74 and all(sha256_of(read_file(os.path.join(vd, "raw", raw_name(r["url_path"])), "rb")) == r["sha256"] for r in vint_rows(ns.out)), "")
    forget_secrets()


# ---- the table of guards and the runner ----
GUARDS = [
    ("G1", "parsing (Decimal JSON, values above 2^53, fractions, missing is not zero, USD only, pts)", ["g1_float_sum", "g1_missing_zero", "g1_nonusd_ok", "g1_float_parse", "g1_pts_count"], t_g1),
    ("G2", "fiscal years (date rule, window edges, 10-K/A and 10-KT, fy label, ambiguity)", ["g2_amend_defines", "g2_fy_label", "g2_edge_end", "g2_edge_start", "g2_two_not_ambiguous"], t_g2),
    ("G3", "fact selection (350-380 days, near facts, own 10-K, latest filed, same filing, fy and fp)", ["g3_lo_349", "g3_lo_351", "g3_hi_379", "g3_hi_381", "g3_near_used", "g3_near_no_mismatch", "g3_own_latest",
                                                                                                         "g3_latest_first", "g3_mixed_accn", "g3_use_fy", "g3_sf_latest", "g3_sf_first_reported", "g3_sf_no_fallback"], t_g3),
    ("G4", "tags and structure (total or parts, deferred revenue, revenue tag, A2 and A3, receivables out of N)", ["g4_parts_when_total_ok", "g4_total_when_lt", "g4_add_total_parts", "g4_deferred_beside",
                                                                                                                   "g4_revenues_over_r2", "g4_skip_r3", "g4_rev_switch", "g4_ar_a2a3", "g4_ar_in_n"], t_g4),
    ("G5", "statuses and gaps (absent everywhere, partial tags, FY2022, sens_gap0, withdrawn statuses)", ["g5_absent_excluded", "g5_partial_in_primary", "g5_fy2022_ok", "g5_gap0_off", "g5_old_status"], t_g5),
    ("G6", "statistic and labels (T, AA, T_pos, VOID first, 10 and 25 edges, direction)", ["g6_t_is_ea", "g6_aa_rt", "g6_tpos_net", "g6_label_signed", "g6_void_last", "g6_void_weak", "g6_round_compare",
                                                                                         "g6_lo_inclusive", "g6_hi_exclusive", "g6_dir_wrong"], t_g6),
    ("G7", "exclusions (SIC 6000-6799 edges, the revenue floor)", ["g7_sic_exclusive", "g7_sic_wide", "g7_floor_off_by_one"], t_g7),
    ("G8", "S2 gate (year-end edges, extraction and frame gates, PENDING, 70% edge, VOID after 2027-08-01)", ["g8_edge_lo", "g8_edge_lo_in", "g8_edge_hi", "g8_edge_hi_in", "g8_extract_all", "g8_gate_off",
                                                                                                             "g8_score_early", "g8_thin_le", "g8_thin_strict", "g8_void_never", "g8_outside_counted", "g8_outside_scored"], t_g8),
    ("G9", "contributors and concentration (ten a side, flags, share over its side, top five per side)", ["g9_eleven", "g9_flags_missing", "g9_share_over_t", "g9_top5_abs", "g9_loo_no_removal", "g9_loo_s1p_threshold"], t_g9),
    ("G10", "registered texts (4.6 and 4.7 hashes, M27's copy, NB2 for S1)", ["g10_prereg_edit", "g10_pop_edit", "g10_prereg_drift", "g10_nb1_for_s1", "g10_registered_unclosed", "g10_m27_closure_off"], t_g10),
    ("G11", "placebo (pre stage reads nothing later, three windows, T not EA, NB1, frozen band)", ["g11_pre_reads_all", "g11_extra_window", "g11_placebo_ea", "g11_nb1_with2020", "g11_band_recomputed"], t_g11),
    ("G12", "allowlists (headers, hash, M27's copy, # source:, seventeen names, keys)", ["g12_allow_drift", "g12_extra_col", "g12_extra_col_ok", "g12_renamed_ok", "g12_source_as_header",
                                                                                         "g12_sixteenth_csv_ok", "g12_checksh_reads_script", "g12_dup_key_ok"], t_g12),
    ("G13", "wording (causal, price, motive and misconduct patterns; the one denial sentence)", ["g13_causal_off", "g13_extra_off", "g13_denial_loose", "g13_denial_all", "g13_readme_attribution"], t_g13),
    ("G14", "STOP latch (AST scan, statuses, bodies, 404 on a frame, timeout)", ["g14_scan_off", "g14_ignore_open", "g14_replace_ok", "g14_stop_ignored", "g14_overwrite", "g14_stop_short", "g14_html_ok",
                                                                                 "g14_empty_ok", "g14_nonjson_ok", "g14_3xx_ignored", "g14_404_latches", "g14_stop_on_timeout"], t_g14),
    ("G15", "fetch safety (hosts, SEC_UA, redirect, retry, 1.0 s gap, caps, cache, the contact string in no byte)", ["g15_allow_other_host", "g15_no_contact_ok", "g15_scrub_off", "g15_secret_ok", "g15_redirect_follow",
                                                                                                                      "g15_retry", "g15_gap_09", "g15_cap_off", "g15_recache"], t_g15),
    ("G16", "vintages (no mixing, S1 scored once, revisions regenerated)", ["g16_mixed_ok", "g16_rescore_s1", "g16_revisions_append"], t_g16),
    ("G17", "leak guard (json, zip, STOP, page, local path, at sign, verdict words, values)", ["g17_json_ok", "g17_path_ok", "g17_at_ok"], t_g17),
    ("G18", "descriptive tables (A1 only, T_AR apart, measure, contract costs out of N, cash-flow signs from the data)", ["g4_ar_a2a3", "g18_tar_in_t", "g18_measure_missing", "g18_cc_in_n", "g18_cf_sign_assumed"], t_g18),
    ("G19", "isolation (AST scan: the panel and the script's own folders only)", ["g19_scan_off", "g19_prefix_ok"], t_g19),
    ("X1", "end-to-end build on the synthetic world (pre then full, reference arithmetic, outputs, guards, fixed output)", ["x_render_unstable"], t_x_build),
    ("X2", "S2 scoring, PENDING_THIN and VOID on the synthetic world", [], t_x_s2),
    ("X2b", "ruling S2-R1: a December firm whose FY2026 10-K ends in June is neither counted nor scored", ["g8_outside_counted", "g8_outside_scored"], t_x_s2_changed_fy),
    ("X3", "the three fetch modes through a mock opener (counts, extracts, resume)", [], t_x_fetch),
]


def run_test(fn):
    ck = Checks()
    try:
        fn(ck)
    except Exception as e:                      # a test that crashes under a mutant has noticed it
        ck.ok("test ran to completion", False, "%s: %s" % (type(e).__name__, e))
    return ck


def selftest(mutants=True, only=None):
    t0 = time.time()
    get_world()                                  # built first, with no mutant active
    bad_total, n_checks, n_mut = 0, 0, 0
    try:
        if only:
            names = {m for _, _, ms, _ in GUARDS for m in ms}
            if only not in names:
                print("unknown mutant %r" % only)
                return 2
            with mutant(only):
                for gid, desc, muts, fn in GUARDS:
                    ck = run_test(fn)
                    bad = ck.failed()
                    print("%-4s %s: %d checks, %s" % (gid, desc, len(ck.items), "FAILED (%d)" % len(bad) if bad else "ok"))
                    for name, detail in bad[:3]:
                        print("       FAIL  %s   <- %s" % (name, detail[:140]))
                    bad_total += len(bad)
            print("selftest with mutant %s: %d failing check(s) -> %s" % (only, bad_total, "the selftest FAILS (mutant caught)" if bad_total else "the selftest PASSES (mutant NOT caught)"))
            return 1 if bad_total else 0
        for gid, desc, muts, fn in GUARDS:
            ck = run_test(fn)
            n_checks += len(ck.items)
            bad = ck.failed()
            bad_total += len(bad)
            print("%-4s %s: %d checks, %s" % (gid, desc, len(ck.items), "ok" if not bad else "FAILED"))
            for name, detail in bad:
                print("       FAIL  %s   <- %s" % (name, detail[:200]))
            if mutants:
                for m in muts:
                    with mutant(m):
                        mk = run_test(fn)
                    caught = bool(mk.failed())
                    n_mut += 1
                    bad_total += 0 if caught else 1
                    print("       mutant %-28s %s%s" % (m, "caught" if caught else "SURVIVED", "  (first failing check: %s)" % mk.failed()[0][0][:70] if caught else ""))
        print("selftest: %d guards, %d checks, %d mutants applied one at a time, %d failure(s), %.1f s" % (len(GUARDS), n_checks, n_mut, bad_total, time.time() - t0))
        return 0 if bad_total == 0 else 1
    finally:
        forget_secrets()
        if "td" in _WORLD:
            _WORLD.pop("td").cleanup()
            _WORLD.clear()


# ==== COMMAND LINE ====
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for mode, help_ in (("fetch-submissions", "the 500 submissions files and their older pages (network; SEC_UA required)"), ("fetch-companyfacts", "the companyfacts file of every firm (network; SEC_UA required)"),
                        ("fetch-frames", "the frames for coverage and checks (network; SEC_UA required)")):
        pf = sub.add_parser(mode, help=help_)
        pf.add_argument("--vintage", required=True, help="YYYYMMDD: today's UTC date, or an existing vintage folder to resume")
        pf.add_argument("--max-requests", type=int, default=None, help="end the run after this many requests (a slice); run again to resume")
        pf.add_argument("--cache", default=CACHE_DEFAULT)
        pf.add_argument("--out", default=OUT_DEFAULT)
        pf.add_argument("--panel", default=None)
    pb = sub.add_parser("build", help="offline: validate the cache and write the outputs of one stage")
    pb.add_argument("--vintage", required=True)
    pb.add_argument("--stage", required=True, choices=("pre", "full"))
    pb.add_argument("--cache", default=CACHE_DEFAULT)
    pb.add_argument("--out", default=OUT_DEFAULT)
    pb.add_argument("--panel", default=None)
    pb.add_argument("--raw", default=None, help="the folder of raw bodies, if not <cache>/<vintage>/raw")
    ps = sub.add_parser("selftest", help="synthetic data, mutants applied one at a time; no network")
    ps.add_argument("--no-mutants", action="store_true")
    ps.add_argument("--mutant", help="run every guard with this one mutant switched on; exit 1 (the selftest fails) when it is caught")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "selftest":
            return selftest(mutants=not a.no_mutants, only=a.mutant)
        if a.cmd == "build":
            return run_build(a)
        return run_fetch(a)
    except Refused as e:
        print("refused: %s" % e, file=sys.stderr)
        return 5
    except NoContact as e:
        print("refused: %s" % e, file=sys.stderr)
        return 2
    except DataError as e:
        print("STOP (data): %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
