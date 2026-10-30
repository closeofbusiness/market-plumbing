#!/usr/bin/env python3
"""The fair-value share of collateral re-used at JPMorgan Chase and Goldman Sachs, quarterly from end-2009 to mid-2026 (SEC XBRL companyconcept on data.sec.gov). Python 3 standard library only.

  python3 bin/collateral_reuse.py fetch-concepts --vintage YYYYMMDD [--max-requests N] [--cache DIR] [--out DIR]     # network; SEC_UA required; supervisor only; 8 requests
  python3 bin/collateral_reuse.py build --vintage YYYYMMDD --stage pre [--cache DIR] [--out DIR]                    # offline; counts and dates only, no value is read
  python3 bin/collateral_reuse.py build --vintage YYYYMMDD --stage dry --out SCRATCH [--cache DIR]                  # offline; writes only status counts and checks, outside the committed folder
  python3 bin/collateral_reuse.py build --vintage YYYYMMDD --stage full [--supersede] [--cache DIR] [--out DIR]     # offline; the registering build; supervisor only; byte-identical on re-run
  python3 bin/collateral_reuse.py selftest [--no-mutants] [--mutant NAME]                                          # synthetic data only; no network; under 30 s

Specification: _research/2026-10-30-Collateral-Reuse-History-Spec.md (committed at ccacee1, with the supervisor's rulings of rounds 1 and 2; the latest round wins).
Outputs: data/collateral_reuse/ (twelve CSVs, README.md, SOURCES.md) and, per vintage, data/vintages/collateral_reuse/<YYYYMMDD>/concept_extract.csv (the raw JSON bodies sit in its raw/
folder, which git ignores).

WHAT TOUCHES THE NETWORK. Only fetch-concepts, only data.sec.gov (companyconcept), GET only, at least 1.0 s after the previous reply, no redirect followed, no retry of any kind, timeout 300 s,
at most 20 requests a run (8 are needed). The contact string is read from the SEC_UA environment variable, the fetch refuses to run without it (exit 2), and its value is never written to
any file, log or output. A 404 on a companyconcept path is `absent` (expected for a Wells Fargo tag; a failure, C01, for a primary bank). Any 403 or 429, any other non-200 status
(3xx included), and a 200 body that is empty, a web page, not JSON or not the document asked for writes STOP_cru in data/vintages/collateral_reuse/ and ends with exit 2. A timeout
prints FAIL network, ends with exit 3 and latches nothing. With the latch present no request is made. This script never deletes, renames over or truncates a STOP file; only a person
deletes one. The fetch is resumable: a body already in raw/ whose sha256 matches its vintages.csv row is not requested again. vintages.csv is written by the fetch mode only.

STAGES (blind order). `pre` reads the period-end, accession, form, filing date, fy and fp of every fact and never its value. `dry` computes everything and writes only status counts and
checks. `full` is the registering build: it writes everything and registered.csv, which is written once and never re-scored (a later vintage rewrites every other output).

WHAT IT RECORDS. For two banks, the fair value of collateral they report having sold or repledged and the fair value they were permitted to, as first reported in the original 10-Q or
10-K of each period, and the share of one in the other. It records no price and no flow of money, and it passes no judgement on any bank.

BUILDER DECISIONS (the spec leaves these open; the choice follows the hashed blocks; the list is BUILDER_DECISIONS below and is printed in SOURCES.md):
see BUILDER_DECISIONS.
"""
import argparse
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
    """SEC_UA is not set: the fetch refuses to run (exit 2)."""


class DataError(Exception):
    """A hard problem with the data or with an output (exit 2)."""


class SliceEnd(Exception):
    """The run's request cap (or --max-requests) is reached with work left (exit 4)."""


# ------------------------------------------------------------------------------------------------------------------------
# constants
# ------------------------------------------------------------------------------------------------------------------------
OUT_DEFAULT = os.path.join(ROOT, "data", "collateral_reuse")
CACHE_DEFAULT = os.path.join(ROOT, "data", "vintages", "collateral_reuse")
STOP_DIR = CACHE_DEFAULT                      # fixed, whatever --cache says: a latch cannot be dodged by pointing the cache elsewhere
STOP_NAME = "STOP_cru"
PIN_NAME = "captions_pin.csv"
SPEC_COMMIT = "ccacee1"
SPEC_FILE = "_research/2026-10-30-Collateral-Reuse-History-Spec.md"

HOST = "data.sec.gov"
BLOCKED_HOSTS = ("sec.gov", "www.sec.gov", "efts.sec.gov", "fred.stlouisfed.org", "alfred.stlouisfed.org", "api.stlouisfed.org")
MIN_GAP = 1.0                                 # seconds between the end of one reply and the next request (R3; G16 treats 0.9 as a violation)
TIMEOUT = 300
BODY_CAP = 256 * 1024 * 1024
ERR_CAP = 4096
FETCH_CAP = 20                                # per run (R3): 8 are needed

TAG_N = "FairValueOfSecuritiesReceivedAsCollateralThatHaveBeenResoldOrRepledged"
TAG_D = "FairValueOfSecuritiesReceivedAsCollateralThatCanBeResoldOrRepledged"
TAGS = (("N", TAG_N), ("D", TAG_D))
TAG_NAME = dict(TAGS)
JPM, GS, STT, WFC = "0000019617", "0000886982", "0000093751", "0000072971"
BANK_TABLE = ((JPM, "JPM", "primary"), (GS, "GS", "primary"), (STT, "STT", "sens_stt"), (WFC, "WFC", "probe"))
TICKER = {c: t for c, t, _ in BANK_TABLE}
PRIMARY = (JPM, GS)
CONCEPT_RX = re.compile(r"^/api/xbrl/companyconcept/CIK(\d{10})/us-gaap/(%s|%s)\.json$" % (TAG_N, TAG_D))
VINTAGE_RX = re.compile(r"^\d{8}$")

# the numbers of 4.6 and 4.7. The canonical texts are rebuilt from these, so editing one changes a hash and the build refuses (G10).
SIGN_TH = Decimal("0.1")                       # points
Y_FIRST, Y_LAST = "2011-12-31", "2019-12-31"
YR_FIRST = "2013-12-31"
YL_FIRST, YL_LAST = "2017-03-31", "2019-12-31"
Y_NOM, Y_EXP, Y_MIN = 33, 23, 20
YR_NOM, YR_EXP, YR_MIN = 25, 17, 14
YL_NOM, YL_MIN = 12, 10
CAP_FIRST = "2017-03-31"                       # JPM numerator: first quarter in the wider caption class (2.6)
CAP_LAST_BEFORE = "2016-12-31"
CAP_SPAN_LAST = "2018-12-31"
S3_START, S3_END = "2021-12-31", "2023-12-31"
S1_START, S1_END = "2023-12-31", "2025-12-31"
S2_DATE, S2_CMP = "2023-12-31", "2019-12-31"
MAX_DAYS = 100
UNIT_LO, UNIT_HI = Decimal("1e9"), Decimal("1e13")
RECAST_TH = Decimal("0.01")
JUMP_TH = Decimal("0.30")
WFC_FIRST, WFC_LAST, WFC_DATES = "2013-12-31", "2026-06-30", 51
SENS_MIN_N = 10
GRID_START = "2009-12-31"
LAST_PINNED = "2026-06-30"                     # the primary banks' last quarter-end in this vintage's span (C01, C02)
STT_LAST_PINNED = "2026-09-30"
N_PERIOD_ENDS, N_OWN = 66, 65

# ------------------------------------------------------------------------------------------------------------------------
# the specification's canonical texts. 4.6 and 4.7 are rebuilt from the constants above; 5 is pasted. Their hashes are checked at run time (C07, G10).
# ------------------------------------------------------------------------------------------------------------------------
PREREG_LINES = (
    'DEF|S_q=sum_b(N_b,q)/sum_b(D_b,q)|N=us-gaap:FairValueOfSecuritiesReceivedAsCollateralThatHaveBeenResoldOrRepledged|D=us-gaap:FairValueOfSecuritiesReceivedAsCollateralThatCanBeResoldOrRepledged|banks=JPM_CIK0000019617+GS_CIK0000886982|every_bank_must_have_both_values_at_q_with_N<=D|value=first_reported_in_the_original_10-K_or_10-Q_of_that_period|unit=USD|share_in_percent|D8_q=S_q-S_(q-8)_in_percentage_points|q-8_is_exactly_eight_calendar_quarters_before_q',
    'M|w_b=D_b/sum_b(D_b)|s_b=N_b/D_b|total=within+mix|within=sum_b(((w_b,0+w_b,1)/2)*(s_b,1-s_b,0))|mix=sum_b(((w_b,1-w_b,0)/2)*(s_b,0+s_b,1))|exact_Shapley_split_of_(w1*s1-w0*s0)|mix_dominates=mix_and_within_nonzero_and_sign(mix)==sign(total)_and_abs(mix)>abs(within)|applies_to=S1,S3',
    'Y|series=D8_q|sample=primary|basis=own_filing|end_quarters=<<y_range>>_inclusive|n_nominal=<<y_nom>>|exclude=any_window_spanning_a_pinned_caption_change_at_a_primary_bank(start<=last_quarter_before_the_change_and_end>=first_quarter_of_the_change)|caption_change=JPM_numerator_first_quarter_<<cap_first>>(spanning_ends_<<cap_first>>..<<cap_span_last>>)|members=those_with_S_defined_at_q_and_q-8_and_not_excluded|expected_members=<<y_exp>>|min_n=<<y_min>>|no_date_after_<<y_last>>_enters|compare=unrounded_decimal_prec28',
    "YR|robustness_yardstick=Y_restricted_to_end_quarters_<<yr_range>>|n_nominal=<<yr_nom>>|expected_members=<<yr_exp>>|min_n=<<yr_min>>|use=for_S1_and_S3_the_range_label_is_recomputed_against_YR|a_different_range_label_from_Y's=VOID_(yardstick_disagrees)|YR_thinner_than_min_n=VOID_(thin_yardstick)",
    'YL|series=S_q|sample=primary|basis=own_filing|quarters=<<yl_range>>_inclusive|n_nominal=<<yl_nom>>|members=those_with_S_defined|min_n=<<yl_min>>|no_date_after_<<y_last>>_enters|compare=unrounded_decimal_prec28',
    'SIGN|change=RISE_if_stat>=<<sign>>_point;FALL_if_stat<=-<<sign>>_point;ZERO_if_abs(stat)<<<sign>>_point|level=sign_of_(S_<<s2_date>>-median(YL))_by_the_same_<<sign>>_point_rule|registered_beside_and_apart_from_the_range_label|the_range_label_means_unusual_against_the_yardstick_and_never_rose_or_not',
    'S1|window=<<s1_range>>|sample=primary|basis=own_filing|vintage=first_full_build|stat=D8_<<s1_end>>|blind=partial|order=VOID,sign,labels|VOID_order=endpoint_undefined,thin_yardstick,endpoint_recast,caption_change,mix_dominates,yardstick_disagrees|endpoint_undefined=S_undefined_at_an_endpoint_or_a_bank-quarter_there_excluded_(incl_ratio_gt_1)|thin_yardstick=n_Y<<<y_min>>_or_n_YR<<<yr_min>>|endpoint_recast=any_bank_tag_flagged_recast_at_either_endpoint|caption_change=pinned_caption_class_differs_between_the_endpoints_for_either_line_of_either_bank|RISE_OUTSIDE_RANGE=stat>max(Y)|FALL_OUTSIDE_RANGE=stat<min(Y)|WITHIN_RANGE=min(Y)<=stat<=max(Y)|rank=position_of_stat_among_Y_and_stat_reported_not_scored|compare=unrounded_decimal_prec28',
    'S2|window=level_at_<<s2_date>>|sample=primary|basis=own_filing|vintage=first_full_build|stat=S_<<s2_date>>|blind=partial|order=VOID,sign,labels|VOID_order=endpoint_undefined,thin_yardstick,caption_change|endpoint_undefined=as_S1_at_<<s2_date>>|thin_yardstick=n_YL<<<yl_min>>|caption_change=pinned_class_at_<<s2_date>>_differs_from_<<s2_cmp>>|LEVEL_ABOVE_RANGE=stat>max(YL)|LEVEL_BELOW_RANGE=stat<min(YL)|LEVEL_WITHIN_RANGE=min(YL)<=stat<=max(YL)|rank=as_S1|compare=unrounded_decimal_prec28',
    'S3|window=<<s3_range>>|sample=primary|basis=own_filing|vintage=first_full_build|stat=D8_<<s3_end>>|blind=full|mandatory=yes|order=VOID,sign,labels|VOID_order=as_S1|labels=as_S1_against_the_same_Y|rank=as_S1|compare=unrounded_decimal_prec28',
)
POP_LINES = (
    'P1|primary=JPM_CIK0000019617;GS_CIK0000886982|why=the_only_banks_with_both_standard_tags_at_every_quarter_end(supervisor_count_66_each,_30_Oct_2026,_metadata_only:_own_filing_at_every_quarter_end_2010-06-30..2026-06-30,_2010-03-31_absent,_2009-12-31_comparative_only)|no_bank_enters_or_leaves_primary_after_any_value_is_read',
    'P2|sens_stt=JPM+GS+STT_CIK0000093751|only_calendar_quarter_ends_where_all_three_have_both_values|yardstick_members=those_of_Y_with_all_three_defined_at_q_and_q-8',
    'P3|sens_wfc=sens_stt+WFC_CIK0000072971|built_iff_the_count_probe_shows_both_tags_at_every_calendar_quarter_end_2013-12-31..2026-06-30(<<wfc_dates>>_dates)|else_not_built_and_the_counts_are_printed',
    'P4|four_bank_sample,_fetch-instances_and_the_Morgan_Stanley,_Bank_of_America,_BNY_and_Citigroup_probes=deferred_to_g14b|nothing_in_this_build_reads_or_fetches_them',
    'P5|probes=WFC_CIK0000072971_only|counts_of_period_ends_and_dates_only|no_value_is_written_for_it',
    'P6|calendar_quarter_end=end_is_exactly_Mar-31,Jun-30,Sep-30_or_Dec-31|any_other_end_is_counted_as_off_calendar_and_never_used',
    'P7|source=data.sec.gov/api/xbrl/companyconcept/CIK##########/us-gaap/<tag>.json|unit_key=USD_only|fact_keys_within={accn,end,val,fy,fp,form,filed,frame,start}_else_refuse|dimensioned_facts_are_not_served',
    "P8|own_filing=the_filing_(form_exactly_10-K_or_10-Q)_in_which_all_three_hold:end==implied_end_of_(fy,fp)_(Q1=Mar-31,Q2=Jun-30,Q3=Sep-30,FY_or_Q4=Dec-31_of_fy);0<=filed-end<=<<max_days>>_days;end==the_latest_end_among_that_accession's_facts_for_the_tag|N_and_D_both_facts_of_that_accession_else_quarter_missing_in_primary|two_such_accessions=ambiguous_and_excluded",
    'P9|amended=10-K/A,10-Q/A,10-KT_never_define_the_primary_value|sens_latest=latest_filed_among_all_forms,ties_to_largest_accn,N_and_D_from_the_same_accession_else_missing',
    'P10|conflict=two_different_val_for_one_tag,end,accn=>quarter_excluded_and_check_fails',
    'P11|unit_bounds=<<unit_lo>><=val<=<<unit_hi>>_else_unit_odd_and_excluded',
    'P12|flags=recast:abs(latest/first-1)><<recast>>_on_either_tag;jump:abs(q/q_change)><<jump>>_on_either_tag_between_adjacent_calendar_quarters|flags_exclude_nothing_in_primary|recast_at_an_endpoint_voids_S1_and_S3',
    'P13|sens_noflag=primary_with_every_quarter_flagged_recast_or_jump_for_any_bank_removed|removal_by_flag_only,_never_by_value_or_outcome',
    'P14|sens_eqw=S_q=mean_over_banks_of(N_b,q/D_b,q)|sens_jpm_and_sens_gs=one_bank_alone',
    'P15|no_imputation:missing_is_never_zero,_never_interpolated,_never_replaced_by_a_nearby_quarter|a_bank_missing_at_q_removes_q_from_the_sample',
    'P16|ratio_gt_1=N>D_for_a_bank-quarter|that_bank-quarter_is_excluded_from_every_sample|an_endpoint_so_excluded_voids_its_statement',
    "P17|captions=the_supervisor-pinned_class_of_each_bank's_wording_for_each_line_at_2011-12-31,2013-12-31,2019-12-31,2021-12-31,2023-12-31,2025-12-31(table_2.6)|different_class_at_the_two_endpoints_of_a_statement=VOID_(caption_change)|a_yardstick_window_spanning_a_class_change_at_a_primary_bank_is_excluded_(Y)|JPM_numerator_class_changes_at_2017-03-31;JPM_denominator_and_Goldman_both_lines_do_not_change|yardstick_end_captions_are_otherwise_described_only",
    'P18|sensitivities=labels_reported_with_n_shown|a_sensitivity_is_VOID_only_if_n<10|never_registered',
    'P19|supersede=a_bug_found_after_registration:the_old_registered_row_is_kept_and_marked_superseded,_the_corrected_row_is_added_with_the_next_version,_both_appear_in_the_README|only_the_supervisor_runs_a_registering_build',
)
SPEC_PREREG_SHA256 = "4ca76d72f2e6050e5e6f11aea432195b170405d2391783de3cca3b90641cd55b"
SPEC_POP_SHA256 = "6492ea1015b05b54cff27267e6228eb480e68ec7aa3f4533573c62b146b096fe"
SPEC_ALLOW_TEXT = (
    'banks.csv:cik10,ticker,entity_name,role,tag,n_period_ends,n_calendar,n_off_calendar,n_own_filing,first_end,last_end\n'
    'quarters.csv:cik10,ticker,end,basis,accession,form,filing_date,n_usd,d_usd,share_pct,flags,status\n'
    'samples.csv:sample,basis,end,n_banks,n_usd,d_usd,share_pct,flags\n'
    'changes.csv:sample,basis,kind,start_end,end_end,share_start_pct,share_end_pct,change_pp,role\n'
    'registered.csv:statement_id,version,superseded,sample,basis,vintage,n_dist,dist_min,dist_max,stat,unit,gap_to_extreme,rank,rank_of,sign,label,blind,void_reason,prereg_sha256,population_sha256\n'
    'decomposition.csv:window,sample,bank,weight_start_pct,weight_end_pct,share_start_pct,share_end_pct,within_pp,mix_pp,total_pp\n'
    'revisions.csv:cik10,ticker,end,tag,first_usd,latest_usd,rel_diff_pct,first_accession,latest_accession,flag\n'
    'probes.csv:cik10,ticker,tag,n_period_ends,n_calendar,first_end,last_end,n_both_tags,verdict\n'
    'headline.csv:vintage,sample,basis,statistic,value,unit,n\n'
    'checks.csv:check_id,description,expected,observed,status\n'
    'vintages.csv:vintage,host,url_path,status,bytes,sha256,retrieved_utc,elapsed_s\n'
    'captions_pin.csv:cik10,ticker,end,line,accession,class,caption_wording\n'
    'concept_extract.csv:vintage,cik10,tag,accn,form,filed,fy,fp,end,val\n'
)
SPEC_ALLOW_SHA256 = "f7540ed76e484978fc26f00f7841d7eb9cfde08d3a15b2519861ff517802f876"
SPEC_CAPTION_SHA256 = "2cfe524cc2257ce2951445f4d759784dd776a71a4910528b050e1c319695c6aa"
ALLOW_ORDER = tuple(l.split(":", 1)[0] for l in SPEC_ALLOW_TEXT.splitlines())
ALLOW = {l.split(":", 1)[0]: l.split(":", 1)[1].split(",") for l in SPEC_ALLOW_TEXT.splitlines()}
OUT_CSVS = ALLOW_ORDER[:12]
COMMITTED = tuple(OUT_CSVS) + ("README.md", "SOURCES.md")
PRE_FILES = ("banks.csv", "probes.csv", "quarters.csv", "checks.csv")
DRY_FILES = ("headline.csv", "checks.csv")
KEYS = {
    "banks.csv": ("cik10", "role", "tag"),
    "quarters.csv": ("cik10", "end", "basis"),
    "samples.csv": ("sample", "basis", "end"),
    "changes.csv": ("sample", "basis", "kind", "start_end", "end_end"),
    "registered.csv": ("statement_id", "version"),
    "decomposition.csv": ("window", "sample", "bank"),
    "revisions.csv": ("cik10", "end", "tag"),
    "probes.csv": ("cik10", "tag"),
    "headline.csv": ("vintage", "sample", "basis", "statistic"),
    "vintages.csv": ("vintage", "url_path"),
    "captions_pin.csv": ("cik10", "end", "line"),
}
CAUSAL_RX = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b", re.I)
EXTRA_RX = re.compile('\\b(?:in|out)flows?\\b|\\bflow(?:s|ed|ing)?\\s+(?:into|out\\s+of|from|to)\\b|\\bmanipulat\\w*|\\bmanag(?:e|ed|es|ing)\\s+(?:earnings|results|revenue)\\b|\\bearnings\\s+management\\b|\\baggressive\\w*|\\bfraud\\w*|\\bmisstat\\w*|\\binflat(?:e|ed|es|ing)\\b|\\bboost(?:s|ed|ing)?\\b|\\bpadd(?:ed|ing)\\b|\\blow[- ]quality\\b|\\bfake\\b|\\b(?:prices?|valuations?|multiples?|stocks?|shares)\\s+(?:rose|fell|rallied|moved|jumped|dropped)\\b|\\bmaterial\\w*|\\boverstat\\w*|\\bpulled\\s+forward\\b|\\bflatter\\w*|\\bwindow[- ]dressing\\b|\\bred\\s+flags?\\b|\\bvelocity\\b|\\bintensity\\b|\\bmultiplier\\b|\\bleverag\\w*|\\bfuel(?:l?ed|s|ing)?\\b|\\bsupport(?:ed|s|ing)?\\s+(?:the\\s+)?(?:rally|prices?|valuations?)\\b|\\bsignifican\\w*|\\bpermissive\\b|\\bpropell\\w*|\\bpow(?:er|ered)\\s+(?:the\\s+)?(?:rally|rise)\\b|\\bproves?\\b|\\bproven\\b', re.I)
DENIAL_SENTENCE = ("A bank's re-pledged share is the part of the collateral it may re-use that it reports having re-used: it is a share at a date, not a speed, and nothing here says it moved "
                   "any price or any flow of money.")
CAPTION_LINE = "JPMorgan's numerator caption widened in the first quarter of 2017; windows that span that change are excluded from the yardstick."
AFTER_SENTENCE = "This is a share at a date for two banks, not a speed (C-135), and says nothing about prices or money."
VERDICT_RX = re.compile(r"HELD|FALSIFIED|PROVEN|CAUSED|REFUTED|MATERIAL")        # section 5: no output carries a verdict word

ALLOWED_VALUES = {
    "role_banks": ("primary", "sens_stt", "sens_wfc", "probe"),
    "tag": ("N", "D"),
    "basis": ("own_filing", "latest_filed"),
    "status": ("ok", "missing_n", "missing_d", "own_filing_lacks_tags", "ambiguous", "conflict", "unit_odd", "off_calendar", "ratio_gt_1"),
    "flags": ("recast", "jump", "amended"),
    "sample": ("primary", "sens_stt", "sens_wfc", "sens_jpm", "sens_gs", "sens_eqw", "sens_noflag"),
    "kind": ("q8", "level"),
    "role_changes": ("yardstick", "registered", "described"),
    "statement_id": ("S1", "S2", "S3"),
    "superseded": ("no", "yes"),
    "unit": ("pp", "pct"),
    "sign": ("RISE", "FALL", "ZERO"),
    "blind": ("full", "partial"),
    "label": ("RISE_OUTSIDE_RANGE", "WITHIN_RANGE", "FALL_OUTSIDE_RANGE", "LEVEL_ABOVE_RANGE", "LEVEL_WITHIN_RANGE", "LEVEL_BELOW_RANGE", "VOID"),
    "void_reason": ("none", "endpoint_undefined", "thin_yardstick", "endpoint_recast", "caption_change", "mix_dominates", "yardstick_disagrees"),
    "line": ("N", "D"),
    "class": ("JN1", "JN2", "JD1", "GN1", "GD1"),
    "verdict": ("enters", "does_not_enter", "counts_only"),
    "check_status": ("PASS", "WARN", "FAIL", "INFO"),
}
COLUMN_RULES = {
    "banks.csv": {"role": "role_banks", "tag": "tag"},
    "quarters.csv": {"basis": "basis", "status": "status", "flags": "flags*"},
    "samples.csv": {"sample": "sample", "basis": "basis", "flags": "flags*"},
    "changes.csv": {"sample": "sample", "basis": "basis", "kind": "kind", "role": "role_changes"},
    "registered.csv": {"statement_id": "statement_id", "superseded": "superseded", "sample": "sample", "basis": "basis", "unit": "unit", "sign": "sign", "blind": "blind", "label": "label",
                       "void_reason": "void_reason"},
    "decomposition.csv": {"sample": "sample"},
    "revisions.csv": {"tag": "tag"},
    "probes.csv": {"tag": "tag", "verdict": "verdict"},
    "checks.csv": {"status": "check_status"},
    "captions_pin.csv": {"line": "line", "class": "class"},
}

# the nine KNOWN bank-date pairs of 2.5 (billions of dollars as printed; the tolerance is half the unit of the last printed digit). They are tie-out pins only (R10, C03).
PINS = (
    (JPM, "2017-12-31", "775.3", "968.8"), (JPM, "2024-12-31", "1,210.7", "1,544.0"), (JPM, "2025-09-30", "1,439.9", "1,829.9"), (JPM, "2025-12-31", "1,426.4", "1,771.0"),
    (JPM, "2026-06-30", "1,741.8", "2,181.4"), (GS, "2017-12-31", "599.6", "764.0"), (GS, "2024-12-31", "912.863", "1,038.740"), (GS, "2025-12-31", "1,119.825", "1,312.079"),
    (GS, "2026-06-30", "1,265.704", "1,431.870"),
)
PIN_DATES = ("2011-12-31", "2013-12-31", "2019-12-31", "2021-12-31", "2023-12-31", "2025-12-31")      # P17: the six pinned year-ends

# which bank's caption class changes, and when (2.6): JPM's numerator, at 2017-03-31; the build treats every earlier JPM quarter as JN1 (O-4, resolved in round 2)
CAPTION_RULE = {(JPM, "N"): (("JN1", None), ("JN2", CAP_FIRST)), (JPM, "D"): (("JD1", None),), (GS, "N"): (("GN1", None),), (GS, "D"): (("GD1", None),)}


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
    """A money amount in whole dollars, half-even (R8). The per-bank cells are quantized once, when the row is made; every aggregate is the sum of the written cells."""
    if v is None:
        return None
    return Decimal(v).quantize(Decimal(1), rounding=decimal.ROUND_HALF_EVEN)


def usd(v):
    return fdec(v, 0)


def pct3(v):
    return fdec(v, 3)


def r6(v):
    return fdec(v, 6)


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


# ---- the contact string (SEC_UA): its value is never written, logged or printed (R2) ----
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
    if M("g16_scrub_off"):
        return text
    for s in _SECRETS:
        text = text.replace(s, "[contact]")
    return text


def write_text(path, text):
    """Atomic write via a temporary sibling. Refuses any path whose name starts with STOP (this script never writes over a latch) and any text that holds the contact string."""
    if os.path.basename(path).upper().startswith("STOP"):
        raise Refused("write_text never touches a STOP file")
    if has_secret(text) and not M("g16_secret_written"):
        raise Refused("the contact string would be written to a file (not printed)")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


def write_bytes(path, data):
    if os.path.basename(path).upper().startswith("STOP"):
        raise Refused("write_bytes never touches a STOP file")
    if has_secret(data) and not M("g16_secret_written"):
        raise Refused("the contact string would be written to a file (not printed)")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.replace(tmp, path)


def read_csv_rows(path):
    """(header, rows) of a csv with comment lines (# ...) skipped; ([], []) if absent."""
    if not os.path.exists(path):
        return [], []
    with open(path, encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh.read().splitlines(True) if not ln.startswith("#")]
    rd = list(csv.reader(io.StringIO("".join(lines))))
    return (rd[0], rd[1:]) if rd else ([], [])


# ---- dates and quarter indexes ----
DATE_RX = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
CAL_MD = ((3, 31), (6, 30), (9, 30), (12, 31))
QEND_DAY = {3: 31, 6: 30, 9: 30, 12: 31}


def parse_date(s):
    """A strict YYYY-MM-DD as a date; None for anything else (a blank or odd date is missing, never guessed)."""
    m = DATE_RX.match(s or "")
    if not m:
        return None
    try:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def days_between(a, b):
    da, db = parse_date(a), parse_date(b)
    if da is None or db is None:
        return None
    return (db - da).days


def is_cal(end):
    """P6: `end` is exactly 31 Mar, 30 Jun, 30 Sep or 31 Dec. The mutants: any day of a quarter-end month; any date at all (it would be moved to its quarter) (G2)."""
    d = parse_date(end)
    if d is None:
        return False
    if M("g2_snap"):
        return True
    if M("g2_month_only"):
        return d.month in (3, 6, 9, 12)
    return (d.month, d.day) in CAL_MD


def qi(end):
    """The calendar quarter index of a date (year * 4 + quarter - 1); only meaningful for a calendar quarter-end."""
    d = parse_date(end)
    return None if d is None else d.year * 4 + (d.month - 1) // 3


def qd(i):
    y, r = divmod(i, 4)
    m = (r + 1) * 3
    return "%04d-%02d-%02d" % (y, m, QEND_DAY[m])


def utc_ms(t):
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


def cik10(x):
    s = str(x).strip() if x is not None else ""
    if not s.isdigit() or int(s) <= 0 or len(s) > 10:
        return None
    return "%010d" % int(s)


def title_name(s):
    """SEC registrant names are upper case; written in title case so that no output cell holds a banned verdict token by accident."""
    return " ".join(w.capitalize() for w in (s or "").split())


def fnum(x):
    """A constant as the text the canonical blocks print (0.1, 0.30, 33, 1e9)."""
    return x if isinstance(x, str) else format(Decimal(x), "f")


# ------------------------------------------------------------------------------------------------------------------------
# the canonical texts
# ------------------------------------------------------------------------------------------------------------------------
def tpl_values():
    sign = "0.2" if M("g10_prereg_edit") else fnum(SIGN_TH)
    return dict(y_range="%s..%s" % (Y_FIRST, Y_LAST), yr_range="%s..%s" % (YR_FIRST, Y_LAST), yl_range="%s..%s" % (YL_FIRST, YL_LAST), s1_range="%s..%s" % (S1_START, S1_END),
                s3_range="%s..%s" % (S3_START, S3_END), y_nom=str(Y_NOM), y_exp=str(Y_EXP), y_min=str(Y_MIN), yr_nom=str(YR_NOM), yr_exp=str(YR_EXP), yr_min=str(YR_MIN), yl_nom=str(YL_NOM),
                yl_min=str(YL_MIN), sign=sign, cap_first=CAP_FIRST, cap_span_last=CAP_SPAN_LAST, s2_date=S2_DATE, s1_end=S1_END, s3_end=S3_END, s2_cmp=S2_CMP, y_last=Y_LAST,
                unit_lo="1e9", unit_hi="10000000000000" if M("g10_pop_edit") else "1e13", recast="0.01", jump="0.30", max_days=str(MAX_DAYS), wfc_dates=str(WFC_DATES))


def fill(line):
    for k, v in tpl_values().items():
        line = line.replace("<<%s>>" % k, v)
    return line


def prereg_text():
    """The canonical text of 4.6, rebuilt from this script's own constants. Its sha256 must equal SPEC_PREREG_SHA256 (C07)."""
    return "".join(fill(l) + "\n" for l in PREREG_LINES)


def pop_text():
    return "".join(fill(l) + "\n" for l in POP_LINES)


def prereg_ok():
    return sha256_of(prereg_text().encode("utf-8")) == SPEC_PREREG_SHA256


def pop_ok():
    return sha256_of(pop_text().encode("utf-8")) == SPEC_POP_SHA256


def prereg_sha_out():
    """The hash written to registered.csv's prereg_sha256 column; M28 holds its own literal copy. The mutant writes the hash of an edited text."""
    if M("g10_prereg_drift"):
        return sha256_of((prereg_text() + " ").encode("utf-8"))
    return SPEC_PREREG_SHA256


def pin_sha_expected():
    return "0" * 64 if M("g10_caption_hash") else SPEC_CAPTION_SHA256


# ---- csv rendering with the allowlist (G18) ----
def allowlist(name):
    cols = list(ALLOW[name])
    if M("g18_renamed") and name == "headline.csv":
        cols[cols.index("statistic")] = "stat"
    if M("g18_extra_col") and name == "samples.csv":
        cols.append("note")
    return cols


def allow_text():
    return "".join("%s:%s\n" % (n, ",".join(allowlist(n))) for n in ALLOW_ORDER)


def allow_hash_ok():
    return sha256_of(allow_text().encode("utf-8")) == SPEC_ALLOW_SHA256


def check_header(name, header):
    allow = allowlist(name)
    if M("g18_extra_col_ok"):
        ok = list(header[:len(allow)]) == allow
    elif M("g18_renamed_ok"):
        ok = len(header) == len(allow)
    else:
        ok = list(header) == allow
    if not ok:
        raise DataError("%s: header %r is not the exact column allowlist" % (name, list(header)))


def csv_body(text):
    """(header, rows) of a committed csv text, skipping every `# source:` line (the mutant reads the source line as the header)."""
    lines = text.splitlines()
    if not M("g18_source_as_header"):
        lines = [l for l in lines if not l.startswith("# source:")]
    rd = list(csv.reader(lines))
    return (rd[0], rd[1:]) if rd else ([], [])


def strip_exempt(text, readme=True):
    """Remove the one denial sentence, once (README; the same sentence is allowed nowhere else)."""
    if not readme:
        return text
    if M("g14_denial_all"):
        return re.sub(r"[^.;]*\bnothing here says\b[^.]*\.", "", text)
    if M("g14_denial_loose"):
        return text.replace(DENIAL_SENTENCE, "")
    return text.replace(DENIAL_SENTENCE, "", 1)


def wording_problems(name, text):
    t = strip_exempt(text, readme=name == "README.md")
    out = []
    if not M("g14_causal_off"):
        out += ["causal wording %r" % re.sub(r"\s+", " ", m.group(0).lower()) for m in CAUSAL_RX.finditer(t)]
    if not M("g14_extra_off"):
        out += ["price, speed or misconduct wording %r" % re.sub(r"\s+", " ", m.group(0).lower()) for m in EXTRA_RX.finditer(t)]
    return out


def verdict_problems(files):
    out = []
    for n in sorted(files):
        t = files[n] if isinstance(files[n], str) else files[n].decode("utf-8", errors="replace")
        if VERDICT_RX.search(t):
            out.append("%s holds a verdict word" % n)
    return out


def readme_problems(text):
    """G14: banned wording (the denial sentence excepted) and the lines the README must carry."""
    out = wording_problems("README.md", text)
    for need, why in ((CAPTION_LINE, "the 2017 caption-change line"), (DENIAL_SENTENCE, "the denial sentence"), ("fair-value share", "the words fair-value share"), ("blind", "the blind column")):
        if need not in text and not M("g14_readme_lax"):
            out.append("README lacks %s" % why)
    if "if the share moved at random with no change in behaviour" not in text and not M("g14_readme_lax"):
        out.append("README lacks the simulation sentence")
    return out


def guard_text(name, text):
    """What the build refuses to write: a verdict word anywhere, banned wording in the README or SOURCES (the denial sentence excepted), an absolute home path."""
    probs = wording_problems(name, text) if name in ("README.md", "SOURCES.md") else []
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


SOURCE_TXT = "US Securities and Exchange Commission, EDGAR XBRL API (companyconcept) on data.sec.gov, vintage %s"


def source_line(vintage, what):
    return "# source: " + SOURCE_TXT % vintage + "; caption pins from the company label linkbase of the filing; " + what


# ------------------------------------------------------------------------------------------------------------------------
# JSON, facts and the P8 own-filing rule
# ------------------------------------------------------------------------------------------------------------------------
FACT_KEYS = ("accn", "end", "val", "fy", "fp", "form", "filed", "frame", "start")
OWN_FORMS = ("10-K", "10-Q")
AMEND_FORMS = ("10-K/A", "10-Q/A", "10-KT")
FP_END = {"Q1": "03-31", "Q2": "06-30", "Q3": "09-30", "FY": "12-31", "Q4": "12-31"}


def _text_of(v):
    """A JSON scalar as text: Decimals and floats as plain digits, None as ''."""
    if v is None:
        return ""
    if isinstance(v, Decimal):
        return format(v, "f")
    if isinstance(v, float):
        return format(Decimal(repr(v)), "f")
    return str(v)


def _keep_strings(s):
    return s


def _no_val(pairs):
    return dict(p for p in pairs if p[0] != "val")


def parse_concept(raw, stage="full"):
    """A companyconcept body as (facts, entity name, cik). Stage `pre` reads no `val`: the pairs hook drops the key before any dict is built and the number hooks keep the text, so no value is
    ever converted (C11). Every other stage reads JSON with Decimal numbers (R8): a value above 2^53 or a fractional value never passes through a binary float (G1). A body whose unit keys
    are not exactly USD, or whose facts carry a key outside the P7 list, is refused."""
    text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw
    pre = stage == "pre" and not M("g17_pre_reads_val")
    if pre:
        doc = json.loads(text, object_pairs_hook=_no_val, parse_float=_keep_strings, parse_int=_keep_strings)
    elif M("g1_float_parse"):
        doc = json.loads(text, parse_float=float, parse_int=float)
    else:
        doc = json.loads(text, parse_float=Decimal, parse_int=Decimal)
    if not isinstance(doc, dict) or not isinstance(doc.get("units"), dict):
        raise DataError("a companyconcept body without a units object")
    units = doc["units"]
    keys = list(units)
    if M("g1_nonusd_ok") or M("g6_usdm_ok"):
        ok = len(keys) >= 1
    elif M("g6_two_units_ok"):
        ok = "USD" in keys
    else:
        ok = keys == ["USD"]
    if not ok:
        raise DataError("unit keys %r are not exactly USD (P7)" % keys[:3])
    facts = []
    for f in units["USD" if "USD" in units else keys[0]]:
        if not isinstance(f, dict):
            raise DataError("a fact that is not an object")
        if not set(f) <= set(FACT_KEYS) and not M("g5_extra_key_ok"):
            raise DataError("a fact carries a key outside the P7 list: %s" % ",".join(sorted(set(f) - set(FACT_KEYS))[:3]))
        d = dict(end=_text_of(f.get("end")), accn=_text_of(f.get("accn")), form=_text_of(f.get("form")), filed=_text_of(f.get("filed")), fy=_text_of(f.get("fy")), fp=_text_of(f.get("fp")))
        if not pre:
            v = f.get("val")
            if v is None:
                if not M("g1_missing_zero"):
                    continue                                  # a fact without a value is absent, never zero (R8, P15)
                v = Decimal(0)
            if isinstance(v, bool) or not isinstance(v, (Decimal, float, int)):
                raise DataError("a fact value that is not a number")
            d["val"] = v if isinstance(v, Decimal) else Decimal(repr(v))
        facts.append(d)
    c = doc.get("cik")
    return facts, title_name(_text_of(doc.get("entityName"))), cik10(_text_of(c)) if c is not None else None


def implied_end(fy, fp):
    """The end implied by a filing's own fiscal year and period: Q1 = 31 Mar, Q2 = 30 Jun, Q3 = 30 Sep, FY or Q4 = 31 Dec of fy (P8). The mutant leaves Q4 unmapped."""
    if not re.match(r"^\d{4}$", fy or ""):
        return None
    md = FP_END.get(fp)
    if M("g3_q4_unmapped") and fp == "Q4":
        md = None
    return None if md is None else "%s-%s" % (fy, md)


class Concept(object):
    """The facts of one bank and one tag, with the indexes P8 needs."""

    def __init__(self, facts):
        self.facts = facts
        self.by_end = collections.defaultdict(list)
        self.last_end = {}
        for f in facts:
            self.by_end[f["end"]].append(f)
            if f["end"] > self.last_end.get(f["accn"], ""):
                self.last_end[f["accn"]] = f["end"]

    def period_ends(self):
        """Distinct ends of any 10-K or 10-Q fact."""
        return sorted({f["end"] for f in self.facts if f["form"] in OWN_FORMS})

    def has(self, end):
        return bool(self.by_end.get(end))

    def own_fact_ok(self, f):
        forms = OWN_FORMS + (AMEND_FORMS if M("g3_amend_defines") else ())
        if f["form"] not in forms:
            return False
        if not M("g3_fy_fp_ignored") and implied_end(f["fy"], f["fp"]) != f["end"]:
            return False
        if not M("g3_comparative_ok"):
            dd = days_between(f["end"], f["filed"])
            lim = MAX_DAYS + 1 if M("g3_days_101") else (MAX_DAYS - 1 if M("g3_days_99") else MAX_DAYS)
            if dd is None or dd < 0 or dd > lim:
                return False
            if f["end"] != self.last_end.get(f["accn"]):
                return False
        return True

    def own_accns(self, end):
        """The accessions that qualify as the original filing of `end` (P8, all three conditions)."""
        return sorted({f["accn"] for f in self.by_end.get(end, ()) if self.own_fact_ok(f)})

    def latest_accn(self, end):
        """P9: the accession of the fact with the latest `filed` among all forms; ties to the largest accn (mutants: the earliest; ties to the smallest)."""
        best = None
        for f in self.by_end.get(end, ()):
            if not f["filed"]:
                continue
            key = (f["filed"], f["accn"])
            if M("g4_latest_uses_first"):
                key = (_neg(f["filed"]), f["accn"])
            elif M("g4_tie_smallest_accn"):
                key = (f["filed"], _neg(f["accn"]))
            if best is None or key > best[0]:
                best = (key, f["accn"])
        return None if best is None else best[1]

    def facts_of(self, end, accn):
        return [f for f in self.by_end.get(end, ()) if f["accn"] == accn]

    def values_at(self, end, accn):
        """The distinct values of the accession's facts at `end` (P10: more than one is a conflict). The mutant reads only the first."""
        vals = []
        for f in self.facts_of(end, accn):
            if "val" in f and f["val"] not in vals:
                vals.append(f["val"])
        if M("g5_conflict_ok"):
            return vals[:1]
        return vals

    def forms_at(self, end):
        return {f["form"] for f in self.by_end.get(end, ())}


def _neg(s):
    """An order-reversing key for a string (so max picks the smallest)."""
    return tuple(-ord(ch) for ch in s)


class Bank(object):
    def __init__(self, cik, ticker, role, n=None, d=None, name=""):
        self.cik, self.ticker, self.role, self.name = cik, ticker, role, name
        self.conc = {"N": n, "D": d}                # a Concept, or None when companyconcept had no facts (404)

    def any_conc(self):
        return [c for c in self.conc.values() if c is not None]


# ------------------------------------------------------------------------------------------------------------------------
# bank-quarter rows (P6-P12, P15, P16)
# ------------------------------------------------------------------------------------------------------------------------
def blank_row(bank, end, basis):
    return dict(cik10=bank.cik, ticker=bank.ticker, end=end, basis=basis, accession="", form="", filing_date="", n=None, d=None, share=None, flags=set(), status="")


def in_bounds(v):
    """P11: 1e9 <= val <= 1e13 (a millions-for-dollars slip in either direction falls outside). The mutants move each edge by one unit or make it exclusive (G6)."""
    lo, hi = UNIT_LO, UNIT_HI
    if M("g6_lo_lt"):
        return lo - 1 <= v <= hi
    if M("g6_lo_excl"):
        return lo < v <= hi
    if M("g6_hi_excl"):
        return lo <= v < hi
    if M("g6_hi_lax"):
        return lo <= v <= hi + 1
    return lo <= v <= hi


def ratio_bad(n, d):
    """P16: N > D. The mutants exclude N = D, or let N = D + 1 USD through (G5)."""
    if M("g5_eq_excluded"):
        return n >= d
    if M("g5_ratio_lax"):
        return n > d + 1
    return n > d


def finish_values(r, bank, end, an, ad, stage):
    cN, cD = bank.conc["N"], bank.conc["D"]
    f = cN.facts_of(end, an)[0]
    r["accession"], r["form"], r["filing_date"] = an, f["form"], f["filed"]
    if stage == "pre":
        r["status"] = "ok"                                    # structurally present in one filing; the value statuses are assigned from the dry stage on (builder decision 1)
        return
    vn, vd = cN.values_at(end, an), cD.values_at(end, ad)
    if len(vn) != 1 or len(vd) != 1:
        r["status"] = "conflict"                              # P10: two different val for one accn, tag and end
        return
    nraw, draw = vn[0], vd[0]
    r["n"], r["d"] = q0(nraw), q0(draw)
    if not (in_bounds(nraw) and in_bounds(draw)):
        r["status"] = "unit_odd"
        return
    if ratio_bad(r["n"], r["d"]):
        r["status"] = "ratio_gt_1"
        return
    r["status"] = "ok"
    r["share"] = Decimal(100) * r["n"] / r["d"]


def own_row(bank, end, stage):
    """The primary basis (P8): numerator and denominator are facts of the original filing of that period, and of the same accession."""
    r = blank_row(bank, end, "own_filing")
    if not is_cal(end):
        r["status"] = "off_calendar"
        return r
    cN, cD = bank.conc["N"], bank.conc["D"]
    if cN is None or not cN.has(end):
        r["status"] = "missing_n"
        return r
    if cD is None or not cD.has(end):
        r["status"] = "missing_d"
        return r
    an, ad = cN.own_accns(end), cD.own_accns(end)
    filled = False
    if M("g3_two_not_ambiguous"):
        an, ad = an[:1], ad[:1]
    elif len(an) > 1 or len(ad) > 1:
        r["status"] = "ambiguous"                             # two accessions that both qualify: excluded
        return r
    if not ad and M("g3_fill_later") and cD.latest_accn(end):
        ad, filled = [cD.latest_accn(end)], True              # the mutant: a missing denominator filled from a later filing
    if not an or not ad or (an[0] != ad[0] and not M("g3_two_accn") and not filled):
        r["status"] = "own_filing_lacks_tags"
        return r
    finish_values(r, bank, end, an[0], ad[0], stage)
    return r


def latest_row(bank, end, stage):
    """sens_latest (P9): the fact with the latest `filed` among all forms (ties to the largest accn), numerator and denominator from the same accession."""
    r = blank_row(bank, end, "latest_filed")
    if not is_cal(end):
        r["status"] = "off_calendar"
        return r
    cN, cD = bank.conc["N"], bank.conc["D"]
    if cN is None or not cN.has(end):
        r["status"] = "missing_n"
        return r
    if cD is None or not cD.has(end):
        r["status"] = "missing_d"
        return r
    an, ad = cN.latest_accn(end), cD.latest_accn(end)
    if an is None or ad is None or an != ad:
        r["status"] = "own_filing_lacks_tags"                 # the latest filing lacks a tag (builder decision 9)
        return r
    finish_values(r, bank, end, an, ad, stage)
    return r


def bank_grid(bank):
    """(calendar quarter-end dates from the bank's first to its last, off-calendar ends): a missing quarter-end inside the span gets a row with its status; none is ever filled (P15)."""
    ends = set()
    for c in bank.any_conc():
        ends.update(c.period_ends())
    cal = sorted(qi(e) for e in ends if is_cal(e))
    off = sorted(e for e in ends if not is_cal(e))
    dates = [qd(i) for i in range(cal[0], cal[-1] + 1)] if cal else []
    return dates, off


def first_latest(bank, tag, end):
    """((first value, accession) or None, (latest value, accession) or None) of one tag at one end, for revisions.csv and the recast flag."""
    c = bank.conc[tag]
    if c is None or not c.has(end):
        return None, None
    first = latest = None
    ao = c.own_accns(end)
    if len(ao) == 1:
        v = c.values_at(end, ao[0])
        if len(v) == 1:
            first = (v[0], ao[0])
    la = c.latest_accn(end)
    if la is not None:
        v = c.values_at(end, la)
        if len(v) == 1:
            latest = (v[0], la)
    return first, latest


def rel_change(first, latest):
    if first is None or latest is None or first[0] == 0:
        return None
    return latest[0] / first[0] - Decimal(1)


def is_recast(rel):
    """P12: abs(latest / first - 1) > 0.01 on either tag. The mutants flag exactly 1.0000%, or leave 1.0001% unflagged (G4)."""
    if rel is None:
        return False
    if M("g4_recast_ge"):
        return abs(rel) >= RECAST_TH
    if M("g4_recast_hi"):
        return abs(rel) > Decimal("0.02")
    return abs(rel) > RECAST_TH


def is_jump(v, pv):
    """P12: abs(q/q change) > 0.30 on either tag between adjacent calendar quarter-ends. Mutants: >= and > 0.31 (G5)."""
    if pv is None or v is None or pv == 0:
        return False
    x = abs(v / pv - Decimal(1))
    if M("g5_jump_ge"):
        return x >= JUMP_TH
    if M("g5_jump_hi"):
        return x > Decimal("0.31")
    return x > JUMP_TH


def bank_rows(bank, stage):
    """{basis: {end: row}} for one bank, with the flags: amended (structural), recast and jump (values; not in the pre stage)."""
    dates, off = bank_grid(bank)
    rows = {"own_filing": collections.OrderedDict(), "latest_filed": collections.OrderedDict()}
    for e in dates + off:
        rows["own_filing"][e] = own_row(bank, e, stage)
        rows["latest_filed"][e] = latest_row(bank, e, stage)
    for e in dates:
        am = any(f["form"] in AMEND_FORMS for c in bank.any_conc() for f in c.by_end.get(e, ()))
        rc = False
        if stage != "pre":
            rc = any(is_recast(rel_change(*first_latest(bank, t, e))) for t in ("N", "D"))
        for basis in rows:
            r = rows[basis][e]
            if am:
                r["flags"].add("amended")
            if rc:
                r["flags"].add("recast")
    if stage != "pre":
        for basis, rs in rows.items():
            for e in dates:
                r = rs[e]
                p = rs.get(qd(qi(e) - 1))
                if r["status"] == "ok" and p is not None and p["status"] == "ok" and (is_jump(r["n"], p["n"]) or is_jump(r["d"], p["d"])):
                    r["flags"].add("jump")
    return rows


def flag_text(flags):
    return "|".join(f for f in ALLOWED_VALUES["flags"] if f in flags)


def usable(r):
    """A bank-quarter that may enter a sample: status ok (the mutants also take a ratio above one, or drop every flagged quarter)."""
    if r is None:
        return False
    ok = r["status"] == "ok" or (M("g5_ratio_in_sample") and r["status"] == "ratio_gt_1")
    if ok and M("g5_flag_excludes") and (r["flags"] & {"recast", "jump"}):
        return False
    return ok


# ------------------------------------------------------------------------------------------------------------------------
# samples, series, yardsticks, labels (3.5-3.9, 4.6)
# ------------------------------------------------------------------------------------------------------------------------
SAMPLE_DEFS = (("primary", PRIMARY), ("sens_stt", PRIMARY + (STT,)), ("sens_wfc", PRIMARY + (STT, WFC)), ("sens_jpm", (JPM,)), ("sens_gs", (GS,)), ("sens_eqw", PRIMARY), ("sens_noflag", PRIMARY))
SAMPLE_BANKS = dict(SAMPLE_DEFS)
CHANGE_FIRST = {JPM: qi(CAP_FIRST)}              # the bank whose pinned caption class changes, and the first quarter-end in the new class (2.6)


def sample_points(rows, sample, basis):
    """{quarter index: point} where point holds n, d, nb, share and flags. S_q = sum N / sum D over the banks of the sample, only where every bank is usable (P15). The mutants: a sum over the
    banks that are present, a missing bank as zero, as the previous quarter, as the mean of its neighbours, and the mean of the banks' ratios for `primary` (G1, G7)."""
    ciks = SAMPLE_BANKS[sample]
    idxs = sorted({qi(e) for c in ciks for e, r in rows.get(c, {}).get(basis, {}).items() if is_cal(e)})
    out = collections.OrderedDict()
    for i in idxs:
        e = qd(i)
        got = [(c, rows[c][basis].get(e)) for c in ciks if c in rows]
        ok = [(c, r) for c, r in got if usable(r)]
        if len(ok) < len(ciks) or len(got) < len(ciks):
            if M("g7_one_bank") and ok:
                pass
            elif M("g7_missing_zero") and ok:
                pass
            elif M("g7_prev_quarter") and ok:
                for c, r in got:
                    if not usable(r):
                        p = rows[c][basis].get(qd(i - 1))
                        if usable(p):
                            ok.append((c, p))
            elif M("g7_interpolate") and ok:
                for c, r in got:
                    if not usable(r):
                        a, b = rows[c][basis].get(qd(i - 1)), rows[c][basis].get(qd(i + 1))
                        if usable(a) and usable(b):
                            ok.append((c, dict(a, n=(a["n"] + b["n"]) / 2, d=(a["d"] + b["d"]) / 2)))
            else:
                continue
        if not ok:
            continue
        rs = [r for _, r in ok]
        n, d = dsum([r["n"] for r in rs]), dsum([r["d"] for r in rs])
        if d == 0:
            continue
        if sample == "sens_eqw" or (M("g1_mean_ratios") and sample == "primary"):
            share = dsum([Decimal(100) * r["n"] / r["d"] for r in rs]) / len(rs)
        else:
            share = Decimal(100) * n / d
        fl = set()
        for r in rs:
            fl |= r["flags"]
        out[i] = dict(n=n, d=d, nb=len(rs), share=share, flags=fl, ratios=[Decimal(100) * r["n"] / r["d"] for r in rs])
    if sample == "sens_noflag":
        for i in list(out):
            e = qd(i)
            if any(rows[c][basis].get(e) is not None and (rows[c][basis][e]["flags"] & {"recast", "jump"}) for c in ciks):
                del out[i]
    return out


def d8_pairs(series):
    """[(q, q-8)] for every q with S defined at both: q-8 is eight calendar quarters earlier, found by quarter index, never by row position (G8)."""
    keys = sorted(series)
    if M("g8_row_pos"):
        return [(keys[i], keys[i - 8]) for i in range(8, len(keys))]
    return [(q, q - 8) for q in keys if (q - 8) in series]


def span_excluded(start, end, change_idxs):
    """The caption rule (R1-12): a window whose start is on or before the last quarter before a change and whose end is on or after the first quarter of the change is excluded. The mutants
    move each edge by one quarter (G21)."""
    for c in change_idxs:
        if M("g21_start_2016_kept"):
            hit = start < c - 1 and end >= c
        elif M("g21_end_2016_excluded"):
            hit = start <= c - 1 and end >= c - 1
        elif M("g21_start_2017_excluded"):
            hit = start <= c and end >= c
        elif M("g21_end_2017_kept"):
            hit = start <= c - 1 and end > c
        else:
            hit = start <= c - 1 and end >= c
        if hit:
            return True
    return False


def change_idxs_of(sample):
    """The first quarter of each caption change among the banks of the sample: JPM's, so every sample that holds JPM; Goldman alone has none (no exclusion, G21)."""
    if M("g21_gs_excluded"):
        return [qi(CAP_FIRST)]
    return [CHANGE_FIRST[c] for c in SAMPLE_BANKS[sample] if c in CHANGE_FIRST]


def yardstick(series, change_idxs, unrestricted=False):
    """Y and YR (4.6): the eight-quarter changes ending 2011-12-31 to 2019-12-31 with S defined at both dates and the window not spanning a caption change. Returns the nominal count, the
    defined windows, the members of Y and of YR."""
    lo, hi = qi(Y_FIRST), qi(Y_LAST)
    if M("g8_y_lo_in"):
        lo = qi("2011-09-30")
    if M("g8_y_lo_out"):
        lo = qi(Y_FIRST) + 1
    if M("g8_y_hi_out"):
        hi = qi(Y_LAST) - 1
    if M("g8_y_hi_in"):
        hi = qi("2020-03-31")
    if M("g8_2026_in"):
        hi = qi("2026-06-30")
    if M("g10_s3_in_y"):
        hi = qi(S3_END)
    defined, members, excluded = [], [], []
    for q, p in d8_pairs(series):
        if lo <= q <= hi:
            d8 = series[q] - series[p]
            defined.append((q, d8))
            if span_excluded(p, q, change_idxs) and not unrestricted:
                excluded.append((q, d8))
            else:
                members.append((q, d8))
    yr_lo = qi(YR_FIRST)
    base = defined if M("g21_yr_noexcl") else members
    yr = [(q, v) for q, v in base if q >= yr_lo]
    return dict(nominal=hi - lo + 1, nominal_yr=hi - yr_lo + 1, defined=defined, members=members, excluded=excluded, yr=yr)


def level_yardstick(series):
    """YL (4.6): the levels at the twelve quarter-ends 2017-03-31 to 2019-12-31 where S is defined."""
    lo, hi = qi(YL_FIRST), qi(YL_LAST)
    if M("g8_yl_lo_in"):
        lo = qi("2016-12-31")
    if M("g8_yl_lo_out"):
        lo = qi("2017-06-30")
    if M("g8_yl_hi_out"):
        hi = qi("2019-09-30")
    if M("g8_yl_hi_in"):
        hi = qi("2020-03-31")
    if M("g8_2026_in"):
        hi = qi("2026-06-30")
    return dict(nominal=hi - lo + 1, members=[(q, series[q]) for q in range(lo, hi + 1) if q in series])


def sign_of(x):
    """RISE if the change is at least +0.1 point, FALL if at most -0.1, else ZERO (R1-1); the unrounded Decimal is compared. Mutants: strict inequalities; a 0.09 threshold (G9)."""
    th = Decimal("0.09") if M("g9_sign_wide") else SIGN_TH
    if M("g9_sign_strict"):
        return "RISE" if x > th else ("FALL" if x < -th else "ZERO")
    return "RISE" if x >= th else ("FALL" if x <= -th else "ZERO")


def _cmp(x):
    return x.quantize(Decimal("0.001")) if M("g9_rounded_compare") else x


def range_label(stat, vals):
    """RISE_OUTSIDE_RANGE if stat > max, FALL_OUTSIDE_RANGE if stat < min, else WITHIN_RANGE (ties with an extreme are WITHIN). The mutants: stat = max is a rise; a 1e-8 tolerance; rounded values (G9)."""
    hi, lo = max(vals), min(vals)
    s = _cmp(stat)
    if M("g9_max_rise"):
        return "RISE_OUTSIDE_RANGE" if s >= _cmp(hi) else ("FALL_OUTSIDE_RANGE" if s < _cmp(lo) else "WITHIN_RANGE")
    eps = Decimal("1e-8") if M("g9_eps") else Decimal(0)
    if s > _cmp(hi) + eps:
        return "RISE_OUTSIDE_RANGE"
    if s < _cmp(lo) - eps:
        return "FALL_OUTSIDE_RANGE"
    return "WITHIN_RANGE"


def level_label(stat, vals):
    return {"RISE_OUTSIDE_RANGE": "LEVEL_ABOVE_RANGE", "FALL_OUTSIDE_RANGE": "LEVEL_BELOW_RANGE", "WITHIN_RANGE": "LEVEL_WITHIN_RANGE"}[range_label(stat, vals)]


def median(vals):
    s = sorted(vals)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def rank_of(stat, vals):
    """The position of the statistic among the yardstick members and itself, largest = 1 (reported, never scored)."""
    return 1 + sum(1 for v in vals if v > stat), len(vals) + 1


# ---- the Shapley split (3.8) ----
def decompose(rows, ciks, start, end):
    """Weights w_b = D_b / sum D, shares s_b = N_b / D_b at the start (0) and end (1); within_b = ((w0 + w1) / 2)(s1 - s0), mix_b = ((w1 - w0) / 2)(s0 + s1). They sum to the total
    exactly. None when a bank-quarter is not usable at an endpoint."""
    r0 = [rows.get(c, {}).get("own_filing", {}).get(start) for c in ciks]
    r1 = [rows.get(c, {}).get("own_filing", {}).get(end) for c in ciks]
    if not all(usable(r) for r in r0 + r1):
        return None
    d0, d1 = dsum([r["d"] for r in r0]), dsum([r["d"] for r in r1])
    if M("g13_weights_90"):
        d0, d1 = d0 * Decimal("1.1"), d1 * Decimal("1.1")
    out = []
    for c, a, b in zip(ciks, r0, r1):
        w0, w1 = a["d"] / d0, b["d"] / d1
        s0, s1 = a["n"] / a["d"], b["n"] / b["d"]
        if M("g13_simple"):
            within, mix = w0 * (s1 - s0), (w1 - w0) * s1
        else:
            within, mix = ((w0 + w1) / 2) * (s1 - s0), ((w1 - w0) / 2) * (s0 + s1)
        if M("g13_sum_off"):
            mix = mix * Decimal("1.01")
        out.append(dict(cik=c, w0=w0 * 100, w1=w1 * 100, s0=s0 * 100, s1=s1 * 100, within=within * 100, mix=mix * 100))
    within, mix = dsum([x["within"] for x in out]), dsum([x["mix"] for x in out])
    S0 = dsum([r["n"] for r in r0]) / dsum([r["d"] for r in r0]) * 100
    S1 = dsum([r["n"] for r in r1]) / dsum([r["d"] for r in r1]) * 100
    return dict(banks=out, within=within, mix=mix, total=S1 - S0, s_start=S0, s_end=S1)


def sgn(x):
    return (x > 0) - (x < 0)


def mix_dominates(dec):
    """mix_and_within_nonzero_and_sign(mix) == sign(total) and abs(mix) > abs(within) (4.6, round-2 ruling O-1). The mutants: never, always, the narrower direction, the opposite sign (G13)."""
    mix, within, total = dec["mix"], dec["within"], dec["total"]
    if M("g13_void_never"):
        return False
    if M("g13_void_always"):
        return True
    if M("g13_void_smaller"):
        return mix != 0 and within != 0 and sgn(mix) == sgn(total) and abs(mix) < abs(within)
    if M("g13_void_vs_within_sign"):
        return mix != 0 and within != 0 and sgn(mix) == sgn(within) and abs(mix) > abs(within)
    return mix != 0 and within != 0 and sgn(mix) == sgn(total) and abs(mix) > abs(within)


# ---- caption classes (2.6, P17) ----
def pin_map(pin_rows):
    return {(r[0], r[2], r[3]): r[5] for r in pin_rows}


def caption_class(pins, cik, line, end):
    """The pinned class of a bank's line at a date; for a date that is not pinned, the rule of 2.6 (JPM's numerator is JN1 before 2017-03-31 and JN2 from it; the other lines never change)."""
    c = pins.get((cik, end, line))
    if c is not None:
        return c
    cur = None
    for cls, since in CAPTION_RULE[(cik, line)]:
        if since is None or end >= since:
            cur = cls
    return cur


def caption_differs(pins, ciks, a, b):
    return any(caption_class(pins, c, ln, a) != caption_class(pins, c, ln, b) for c in ciks for ln in ("N", "D"))


# ---- the statements (4.6) ----
def statement(sid, ctx):
    """One registered statement (S1, S2 or S3) of the primary sample on the own_filing basis, in the order of the hashed text: VOID reasons in their order, then the sign, then the range label."""
    series = ctx["series"]
    out = dict(sid=sid, stat=None, n_dist=None, dmin=None, dmax=None, rank=None, rank_of=None, gap=None, sign="", label="VOID", void="none", unit="pp")
    if sid == "S2":
        out["unit"] = "pct"
        e = S2_DATE
        yl = ctx["yl"]
        vals = [v for _, v in yl["members"]]
        out["stat"] = series.get(qi(e))
        out["n_dist"] = len(vals)
        if vals:
            out["dmin"], out["dmax"] = min(vals), max(vals)
        rec = M("g9_s2_recast_void") and ctx["recast_at"](e)                 # the mutant: S2 voided for a recast (it is exempt, round-2 ruling)
        for reason, hit in (("endpoint_undefined", out["stat"] is None), ("thin_yardstick", len(vals) < YL_MIN), ("endpoint_recast", rec),
                            ("caption_change", caption_differs(ctx["pins"], PRIMARY, e, S2_CMP))):
            if hit and out["void"] == "none":
                out["void"] = reason
        if out["stat"] is not None and vals:
            out["rank"], out["rank_of"] = rank_of(out["stat"], vals)
            out["gap"] = min(out["stat"] - out["dmin"], out["dmax"] - out["stat"])
        if out["void"] == "none":
            out["sign"] = sign_of(out["stat"] - median(vals))
            out["label"] = level_label(out["stat"], vals)
        return out
    start, end = (S3_START, S3_END) if sid == "S3" else (S1_START, S1_END)
    s0, s1 = series.get(qi(start)), series.get(qi(end))
    y, vals = ctx["y"], [v for _, v in ctx["y"]["members"]]
    yrv = [v for _, v in ctx["y"]["yr"]]
    out["n_dist"] = len(vals)
    if vals:
        out["dmin"], out["dmax"] = min(vals), max(vals)
    if s0 is not None and s1 is not None:
        out["stat"] = s1 - s0
        if vals:
            out["rank"], out["rank_of"] = rank_of(out["stat"], vals)
            out["gap"] = min(out["stat"] - out["dmin"], out["dmax"] - out["stat"])
    dec = ctx["decompose"](start, end)
    lab_y = range_label(out["stat"], vals) if out["stat"] is not None and vals else None
    lab_yr = range_label(out["stat"], yrv) if out["stat"] is not None and yrv else None
    recast = ctx["recast_at"](start) or ctx["recast_at"](end)
    cap = caption_differs(ctx["pins"], PRIMARY, start, end)
    tests = [("endpoint_undefined", s0 is None or s1 is None), ("thin_yardstick", len(vals) < Y_MIN or len(yrv) < YR_MIN),
             ("endpoint_recast", recast and not M("g9_recast_label_written")), ("caption_change", cap and not M("g9_caption_label_written")),
             ("mix_dominates", dec is not None and mix_dominates(dec)), ("yardstick_disagrees", lab_y != lab_yr if not M("g21_disagree_ok") else False)]
    if M("g9_void_order"):
        tests[2], tests[3] = tests[3], tests[2]
    if M("g21_disagree_void_same"):
        tests[5] = ("yardstick_disagrees", True)
    for reason, hit in tests:
        if hit:
            out["void"] = reason
            return out
    out["sign"] = sign_of(out["stat"])
    out["label"] = lab_y
    if M("g9_within_zero_sign") and lab_y == "WITHIN_RANGE":
        out["sign"] = "ZERO"
    return out


def light_statements(series, change_idxs):
    """The same three statements for a sensitivity or a variant: sign and range label against the sample's own yardstick, n shown, VOID only when the endpoints are undefined or n < 10 (P18)."""
    y = yardstick(series, change_idxs)
    yl = level_yardstick(series)
    vals = [v for _, v in y["members"]]
    out = collections.OrderedDict()
    for sid, (a, b) in (("S3", (S3_START, S3_END)), ("S1", (S1_START, S1_END))):
        s0, s1 = series.get(qi(a)), series.get(qi(b))
        st = dict(stat=None if s0 is None or s1 is None else s1 - s0, n=len(vals), lo=min(vals) if vals else None, hi=max(vals) if vals else None, unit="pp", sign="", label="VOID")
        if st["stat"] is not None and len(vals) >= SENS_MIN_N:
            st["sign"], st["label"] = sign_of(st["stat"]), range_label(st["stat"], vals)
        out[sid] = st
    lv = [v for _, v in yl["members"]]
    s2 = series.get(qi(S2_DATE))
    st = dict(stat=s2, n=len(lv), lo=min(lv) if lv else None, hi=max(lv) if lv else None, unit="pct", sign="", label="VOID")
    if s2 is not None and len(lv) >= SENS_MIN_N:
        st["sign"], st["label"] = sign_of(s2 - median(lv)), level_label(s2, lv)
    out["S2"] = st
    return out, y, yl



# ------------------------------------------------------------------------------------------------------------------------
# the whole computation, in memory
# ------------------------------------------------------------------------------------------------------------------------
BANK_ORDER = (JPM, GS, STT, WFC)


def probe_of(bank):
    """P3, P5: Wells Fargo's counts and dates only. It enters the State Street sensitivity iff both tags have a period-end at every calendar quarter-end 2013-12-31..2026-06-30 (51 dates)."""
    dates = [qd(i) for i in range(qi(WFC_FIRST), qi(WFC_LAST) + 1)]
    ends = {}
    for t in ("N", "D"):
        c = bank.conc[t]
        ends[t] = set(c.period_ends()) if c is not None else set()
    n_both = sum(1 for d in dates if d in ends["N"] and d in ends["D"])
    absent = bank.conc["N"] is None and bank.conc["D"] is None
    verdict = "counts_only" if absent else ("enters" if n_both == len(dates) == WFC_DATES else "does_not_enter")
    return dict(n_both=n_both, verdict=verdict, dates=len(dates))


def compute(banks, stage, vintage, pin_rows):
    """Everything the outputs need, from the parsed banks. In the pre stage no value exists: rows hold structure only, and nothing else is computed."""
    ctx = dict(stage=stage, vintage=vintage, banks=[b for b in sorted(banks, key=lambda b: BANK_ORDER.index(b.cik))], pin_rows=pin_rows, pins=pin_map(pin_rows))
    ctx["by_cik"] = {b.cik: b for b in ctx["banks"]}
    wfc = ctx["by_cik"].get(WFC)
    ctx["probe"] = probe_of(wfc) if wfc is not None else dict(n_both=0, verdict="counts_only", dates=0)
    if wfc is not None:
        wfc.role = "sens_wfc" if ctx["probe"]["verdict"] == "enters" else "probe"
    ctx["rows"] = {b.cik: bank_rows(b, stage) for b in ctx["banks"]}
    if stage == "pre":
        return ctx
    rows = ctx["rows"]
    samples = collections.OrderedDict()
    for name, ciks in SAMPLE_DEFS:
        if name == "sens_wfc" and ctx["probe"]["verdict"] != "enters":
            continue
        if not all(c in rows for c in ciks):
            continue
        for basis in (("own_filing", "latest_filed") if name == "primary" else ("own_filing",)):
            samples[(name, basis)] = sample_points(rows, name, basis)
    ctx["samples"] = samples
    series = collections.OrderedDict((k, collections.OrderedDict((i, p["share"]) for i, p in pts.items())) for k, pts in samples.items())
    ctx["series"] = series
    prim = series[("primary", "own_filing")]
    ctx["y"] = yardstick(prim, change_idxs_of("primary"))
    ctx["yl"] = level_yardstick(prim)
    own = rows

    def recast_at(e):
        return any("recast" in own[c]["own_filing"][e]["flags"] for c in PRIMARY if c in own and e in own[c]["own_filing"])

    ctx["recast_at"] = recast_at
    ctx["decompose"] = lambda a, b: decompose(own, PRIMARY, a, b)
    sctx = dict(series=prim, y=ctx["y"], yl=ctx["yl"], pins=ctx["pins"], recast_at=recast_at, decompose=ctx["decompose"])
    ctx["stmts"] = collections.OrderedDict((sid, statement(sid, sctx)) for sid in ("S3", "S1", "S2"))
    ctx["decomp"] = collections.OrderedDict((sid, ctx["decompose"](a, b)) for sid, a, b in (("S3", S3_START, S3_END), ("S1", S1_START, S1_END)))
    ctx["light"] = collections.OrderedDict()
    for (name, basis), ser in series.items():
        ctx["light"][(name, basis)] = light_statements(ser, change_idxs_of(name))
    ctx["sctx"] = sctx
    return ctx


# ------------------------------------------------------------------------------------------------------------------------
# tables
# ------------------------------------------------------------------------------------------------------------------------
def rows_banks(ctx):
    out = []
    for b in ctx["banks"]:
        for t, _ in TAGS:
            c = b.conc[t]
            if c is None:
                out.append([b.cik, b.ticker, b.name, b.role, t, "0", "0", "0", "0", "", ""])
                continue
            ends = c.period_ends()
            cal = [e for e in ends if is_cal(e)]
            own = sum(1 for e in cal if c.own_accns(e))
            out.append([b.cik, b.ticker, b.name, b.role, t, str(len(ends)), str(len(cal)), str(len(ends) - len(cal)), str(own), ends[0] if ends else "", ends[-1] if ends else ""])
    return out


def rows_probes(ctx):
    b = ctx["by_cik"].get(WFC)
    if b is None:
        return []
    out = []
    for t, _ in TAGS:
        c = b.conc[t]
        ends = c.period_ends() if c is not None else []
        cal = [e for e in ends if is_cal(e)]
        out.append([b.cik, b.ticker, t, str(len(ends)), str(len(cal)), ends[0] if ends else "", ends[-1] if ends else "", str(ctx["probe"]["n_both"]), ctx["probe"]["verdict"]])
    return out


def rows_quarters(ctx):
    out = []
    for b in ctx["banks"]:
        for basis in ("own_filing", "latest_filed"):
            for e in sorted(ctx["rows"][b.cik][basis]):
                r = ctx["rows"][b.cik][basis][e]
                has_v = r["status"] in ("ok", "ratio_gt_1", "unit_odd")
                out.append([r["cik10"], r["ticker"], e, basis, r["accession"], r["form"], r["filing_date"], usd(r["n"]) if has_v else "", usd(r["d"]) if has_v else "",
                            pct3(r["share"]) if r["status"] == "ok" else "", flag_text(r["flags"]), r["status"]])
    return out


def rows_samples(ctx):
    out = []
    for (name, basis), pts in ctx["samples"].items():
        for i, p in pts.items():
            out.append([name, basis, qd(i), str(p["nb"]), usd(p["n"]), usd(p["d"]), pct3(p["share"]), flag_text(p["flags"])])
    return out


def rows_changes(ctx):
    out = []
    for (name, basis), ser in ctx["series"].items():
        y = ctx["light"][(name, basis)][1]
        members = {q for q, _ in y["members"]}
        for q, p in d8_pairs(ser):
            role = "yardstick" if q in members else "described"
            if name == "primary" and basis == "own_filing" and qd(q) in (S1_END, S3_END):
                role = "registered"
            out.append([name, basis, "q8", qd(p), qd(q), pct3(ser[p]), pct3(ser[q]), pct3(ser[q] - ser[p]), role])
        for q in sorted(ser):
            if qi(YL_FIRST) <= q <= qi(YL_LAST):
                out.append([name, basis, "level", "", qd(q), "", pct3(ser[q]), "", "yardstick"])
            elif qd(q) == S2_DATE:
                out.append([name, basis, "level", "", qd(q), "", pct3(ser[q]), "", "registered" if (name, basis) == ("primary", "own_filing") else "described"])
    return out


def rows_decomposition(ctx):
    out = []
    for sid, a, b in (("S3", S3_START, S3_END), ("S1", S1_START, S1_END)):
        dec = ctx["decomp"][sid]
        if dec is None:
            continue
        win = "%s..%s" % (a, b)
        for x in dec["banks"]:
            out.append([win, "primary", TICKER[x["cik"]], pct3(x["w0"]), pct3(x["w1"]), pct3(x["s0"]), pct3(x["s1"]), pct3(x["within"]), pct3(x["mix"]), pct3(x["within"] + x["mix"])])
        out.append([win, "primary", "ALL", pct3(dsum([x["w0"] for x in dec["banks"]])), pct3(dsum([x["w1"] for x in dec["banks"]])), pct3(dec["s_start"]), pct3(dec["s_end"]), pct3(dec["within"]),
                    pct3(dec["mix"]), pct3(dec["total"])])
    return out


def rows_revisions(ctx):
    """Per bank, quarter and tag: the first-reported and the latest-filed value and their relative difference. Regenerated on every build, never appended (G4)."""
    out = []
    for b in ctx["banks"]:
        if b.role == "probe":
            continue
        dates, _ = bank_grid(b)
        for e in dates:
            for t, _ in TAGS:
                first, latest = first_latest(b, t, e)
                if first is None and latest is None:
                    continue
                rel = rel_change(first, latest)
                out.append([b.cik, b.ticker, e, t, usd(q0(first[0])) if first else "", usd(q0(latest[0])) if latest else "", pct3(rel * 100) if rel is not None else "",
                            first[1] if first else "", latest[1] if latest else "", "recast" if is_recast(rel) else ""])
    return out


def count_rows(ctx):
    """Status counts and yardstick member counts: the only statistics the dry stage writes (3.3). Each row is [statistic, value, n]."""
    out = []
    for b in ctx["banks"]:
        for basis in ("own_filing", "latest_filed"):
            cnt = collections.Counter(r["status"] for r in ctx["rows"][b.cik][basis].values())
            for s in ALLOWED_VALUES["status"]:
                if cnt.get(s):
                    out.append((basis, "count_status_%s_%s" % (b.ticker, s), cnt[s]))
            if basis == "own_filing":
                for f in ALLOWED_VALUES["flags"]:
                    k = sum(1 for r in ctx["rows"][b.cik][basis].values() if f in r["flags"])
                    if k:
                        out.append((basis, "count_flag_%s_%s" % (b.ticker, f), k))
    if "y" in ctx:
        y, yl = ctx["y"], ctx["yl"]
        for nm, v in (("count_Y_nominal", y["nominal"]), ("count_Y_defined", len(y["defined"])), ("count_Y_excluded_caption", len(y["excluded"])), ("count_Y_members", len(y["members"])),
                      ("count_YR_nominal", y["nominal_yr"]), ("count_YR_members", len(y["yr"])), ("count_YL_nominal", yl["nominal"]), ("count_YL_members", len(yl["members"])),
                      ("count_primary_quarters", len(ctx["series"][("primary", "own_filing")]))):
            out.append(("own_filing", nm, v))
    return out


def _hl(ctx, sample, basis, stat, value, unit, n=""):
    return [ctx["vintage"], sample, basis, stat, value, unit, str(n)]


def rows_headline(ctx, counts_only=False):
    out = [_hl(ctx, "primary", basis, stat, str(v), "count", v) for basis, stat, v in count_rows(ctx)]
    if counts_only:
        return out
    for (name, basis), (light, y, yl) in ctx["light"].items():
        for sid in ("S3", "S1", "S2"):
            st = light[sid]
            out.append(_hl(ctx, name, basis, sid + "_stat", pct3(st["stat"]), st["unit"], st["n"]))
            out.append(_hl(ctx, name, basis, sid + "_dist_min", pct3(st["lo"]), st["unit"], st["n"]))
            out.append(_hl(ctx, name, basis, sid + "_dist_max", pct3(st["hi"]), st["unit"], st["n"]))
            out.append(_hl(ctx, name, basis, sid + "_sign", st["sign"], "label", st["n"]))
            out.append(_hl(ctx, name, basis, sid + "_label", st["label"], "label", st["n"]))
    ser = ctx["series"][("primary", "own_filing")]
    ch = change_idxs_of("primary")
    # (a) the unrestricted 2011-start yardstick: keeps the windows that span the caption change
    ya = yardstick(ser, ch, unrestricted=True)
    va = [v for _, v in ya["members"]]
    out.append(_hl(ctx, "primary", "own_filing", "variant_a_n", str(len(va)), "count", len(va)))
    if va:
        out.append(_hl(ctx, "primary", "own_filing", "variant_a_min", pct3(min(va)), "pp", len(va)))
        out.append(_hl(ctx, "primary", "own_filing", "variant_a_max", pct3(max(va)), "pp", len(va)))
    for sid in ("S3", "S1"):
        st = ctx["light"][("primary", "own_filing")][0][sid]
        lab = range_label(st["stat"], va) if st["stat"] is not None and va else "VOID"
        out.append(_hl(ctx, "primary", "own_filing", "variant_a_%s_label" % sid, lab, "label", len(va)))
        out.append(_hl(ctx, "primary", "own_filing", "variant_a_%s_differs_from_Y" % sid, "yes" if lab != st["label"] else "no", "flag", len(va)))
    # (b) the non-overlapping spans of the December phase (the span ending 2011-12-31 on the latest_filed basis only, flagged: its start is a comparative)
    usable_spans = 0
    for e in ("2011-12-31", "2013-12-31", "2015-12-31", "2017-12-31", "2019-12-31"):
        q = qi(e)
        src = ctx["series"][("primary", "latest_filed")] if e == "2011-12-31" else ser
        basis = "latest_filed" if e == "2011-12-31" else "own_filing"
        if q in src and (q - 8) in src and (e == "2011-12-31" or not span_excluded(q - 8, q, ch)):
            out.append(_hl(ctx, "primary", basis, "variant_b_span_%s" % e, pct3(src[q] - src[q - 8]), "pp", 1))
            if e != "2011-12-31":
                usable_spans += 1
        else:
            out.append(_hl(ctx, "primary", basis, "variant_b_span_%s" % e, "", "pp", 0))
    out.append(_hl(ctx, "primary", "own_filing", "variant_b_usable_december_spans", str(usable_spans), "count", usable_spans))
    # (c) a December-only subset of Y
    vc = [v for q, v in ctx["y"]["members"] if qd(q).endswith("-12-31")]
    out.append(_hl(ctx, "primary", "own_filing", "variant_c_n", str(len(vc)), "count", len(vc)))
    if vc:
        out.append(_hl(ctx, "primary", "own_filing", "variant_c_min", pct3(min(vc)), "pp", len(vc)))
        out.append(_hl(ctx, "primary", "own_filing", "variant_c_max", pct3(max(vc)), "pp", len(vc)))
    for sid in ("S3", "S1"):
        st = ctx["light"][("primary", "own_filing")][0][sid]
        out.append(_hl(ctx, "primary", "own_filing", "variant_c_%s_label" % sid, range_label(st["stat"], vc) if st["stat"] is not None and vc else "VOID", "label", len(vc)))
    # (d) a Goldman-only yardstick (no caption change, so no exclusion)
    if ("sens_gs", "own_filing") in ctx["light"]:
        yd = ctx["light"][("sens_gs", "own_filing")][1]
        vd = [v for _, v in yd["members"]]
        out.append(_hl(ctx, "sens_gs", "own_filing", "variant_d_n", str(len(vd)), "count", len(vd)))
        if vd:
            out.append(_hl(ctx, "sens_gs", "own_filing", "variant_d_min", pct3(min(vd)), "pp", len(vd)))
            out.append(_hl(ctx, "sens_gs", "own_filing", "variant_d_max", pct3(max(vd)), "pp", len(vd)))
    # the recast flag at 2016-12-31, per bank (the date JPMorgan's numerator caption was about to change)
    for c in PRIMARY:
        r = ctx["rows"].get(c, {}).get("own_filing", {}).get("2016-12-31")
        out.append(_hl(ctx, "primary", "own_filing", "recast_2016-12-31_%s" % TICKER[c], "undefined" if r is None else ("yes" if "recast" in r["flags"] else "no"), "flag", ""))
    return out


BLIND = {"S3": "full", "S1": "partial", "S2": "partial"}


def rows_registered_new(ctx):
    out = []
    for sid in ("S3", "S1", "S2"):
        s = ctx["stmts"][sid]
        out.append([sid, "1", "no", "primary", "own_filing", ctx["vintage"], str(s["n_dist"]), pct3(s["dmin"]), pct3(s["dmax"]), pct3(s["stat"]), s["unit"], r6(s["gap"]),
                    "" if s["rank"] is None else str(s["rank"]), "" if s["rank_of"] is None else str(s["rank_of"]), s["sign"], s["label"], BLIND[sid], s["void"], prereg_sha_out(), SPEC_POP_SHA256])
    return out


def supersede_rows(old, new):
    """P19: the old registered rows are kept and marked superseded = yes; the corrected rows are added with the next version number (G17)."""
    h = ALLOW["registered.csv"]
    iv, isup, isid = h.index("version"), h.index("superseded"), h.index("statement_id")
    out = []
    if not M("g17_supersede_deletes"):
        for r in old:
            r = list(r)
            r[isup] = "yes"
            out.append(r)
    for r in new:
        r = list(r)
        prev = [int(x[iv]) for x in old if x[isid] == r[isid]]
        r[iv] = "1" if M("g17_supersede_noversion") else str((max(prev) if prev else 0) + 1)
        out.append(r)
    return sorted(out, key=lambda r: (("S3", "S1", "S2").index(r[isid]), int(r[iv])))


def rows_extract(ctx):
    out = []
    for b in ctx["banks"]:
        for t, tag in TAGS:
            c = b.conc[t]
            if c is None:
                continue
            for f in sorted(c.facts, key=lambda f: (f["end"], f["accn"], f["form"], f["filed"], f["fy"], f["fp"], f["val"])):
                if f["end"] < GRID_START:
                    continue
                out.append([ctx["vintage"], b.cik, tag, f["accn"], f["form"], f["filed"], f["fy"], f["fp"], f["end"], usd(f["val"]) if f["val"] == f["val"].to_integral_value() else format(f["val"], "f")])
    return out


# ------------------------------------------------------------------------------------------------------------------------
# checks (section 8): operate on the rendered texts, so the committed files are tested, not the in-memory objects
# ------------------------------------------------------------------------------------------------------------------------
def table(files, name):
    """The rows of a rendered csv as dicts, or None when the file is absent or its header is not the allowlist."""
    if name not in files:
        return None
    h, rows = csv_body(files[name])
    if list(h) != ALLOW[name]:
        return None
    return [dict(zip(h, r)) for r in rows]


def _dec(s):
    try:
        return Decimal(s)
    except (decimal.InvalidOperation, TypeError, ValueError):
        return None


def share_from_quarters(qmap, sample, basis, end):
    """(n, d, nb, share) of a sample at a quarter-end, recomputed from the bank rows of quarters.csv alone; None when a bank is not `ok` there."""
    ciks = SAMPLE_BANKS[sample]
    parts = [qmap.get((c, basis, end)) for c in ciks]
    if any(p is None or p["status"] != "ok" for p in parts):
        return None
    ns, ds = [Decimal(p["n_usd"]) for p in parts], [Decimal(p["d_usd"]) for p in parts]
    n, d = sum(ns), sum(ds)
    if sample == "sens_eqw":
        share = sum(Decimal(100) * a / b for a, b in zip(ns, ds)) / len(ns)
    else:
        share = Decimal(100) * n / d
    return n, d, len(parts), share


def qmap_of(files):
    q = table(files, "quarters.csv")
    return None if q is None else {(r["cik10"], r["basis"], r["end"]): r for r in q}


def c05_problems(files):
    """C05: samples.csv n_usd and d_usd equal the sums of the banks' quarters.csv rows; share_pct recomputes to 3 decimals."""
    if M("g18_c05_off"):
        return []
    qm, srows = qmap_of(files), table(files, "samples.csv")
    if qm is None or srows is None:
        return []
    out = []
    for r in srows:
        if r["sample"] not in SAMPLE_BANKS:
            out.append("samples.csv holds an unknown sample %s" % r["sample"])
            continue
        got = share_from_quarters(qm, r["sample"], r["basis"], r["end"])
        if got is None:
            out.append("samples.csv %s %s %s: a bank row is missing or not ok in quarters.csv" % (r["sample"], r["basis"], r["end"]))
            continue
        n, d, nb, share = got
        if _dec(r["n_usd"]) != n or _dec(r["d_usd"]) != d or r["n_banks"] != str(nb):
            out.append("samples.csv %s %s %s: n_usd/d_usd do not equal the sums of the bank rows" % (r["sample"], r["basis"], r["end"]))
        elif pct3(share) != r["share_pct"]:
            out.append("samples.csv %s %s %s: share_pct does not recompute to three decimals" % (r["sample"], r["basis"], r["end"]))
    return out


def c08_problems(files):
    """C08: changes.csv D8 is recomputed at full precision from the USD sums in quarters.csv (not from the rounded shares) and equals the written value to three decimals; each registered row
    recomputes from them. After a second vintage only the vintage named in registered.csv is recomputed (the vintage in headline.csv is the one quarters.csv holds)."""
    if M("g18_c08_off"):
        return []
    qm, crows = qmap_of(files), table(files, "changes.csv")
    if qm is None or crows is None:
        return []
    out = []
    S = {}

    def s_at(sample, basis, end):
        k = (sample, basis, end)
        if k not in S:
            g = share_from_quarters(qm, sample, basis, end) if sample in SAMPLE_BANKS else None
            S[k] = None if g is None else g[3]
        return S[k]

    for r in crows:
        e = s_at(r["sample"], r["basis"], r["end_end"])
        if e is None:
            out.append("changes.csv %s %s %s: the end share cannot be recomputed from quarters.csv" % (r["sample"], r["basis"], r["end_end"]))
            continue
        if r["kind"] == "level":
            if pct3(e) != r["share_end_pct"]:
                out.append("changes.csv %s %s level %s: share does not recompute" % (r["sample"], r["basis"], r["end_end"]))
            continue
        s = s_at(r["sample"], r["basis"], r["start_end"])
        if s is None or pct3(e - s) != r["change_pp"] or pct3(s) != r["share_start_pct"] or pct3(e) != r["share_end_pct"]:
            out.append("changes.csv %s %s %s..%s: D8 does not recompute from the USD sums of quarters.csv" % (r["sample"], r["basis"], r["start_end"], r["end_end"]))
    reg, head = table(files, "registered.csv"), table(files, "headline.csv")
    if reg and head:
        hv = {r["vintage"] for r in head}
        yard = [r for r in crows if r["sample"] == "primary" and r["basis"] == "own_filing" and r["role"] == "yardstick"]
        for r in reg:
            if r["superseded"] == "yes" or r["vintage"] not in hv:
                continue
            sid = r["statement_id"]
            if sid == "S2":
                dist = [_dec(x["share_end_pct"]) for x in yard if x["kind"] == "level"]
                reg_stat = [x["share_end_pct"] for x in crows if x["sample"] == "primary" and x["basis"] == "own_filing" and x["kind"] == "level" and x["end_end"] == S2_DATE]
            else:
                dist = [_dec(x["change_pp"]) for x in yard if x["kind"] == "q8"]
                end = S3_END if sid == "S3" else S1_END
                reg_stat = [x["change_pp"] for x in crows if x["sample"] == "primary" and x["basis"] == "own_filing" and x["kind"] == "q8" and x["end_end"] == end]
            if r["stat"] != (reg_stat[0] if reg_stat else ""):
                out.append("registered.csv %s: stat does not recompute from changes.csv" % sid)
            if r["label"] == "VOID" and r["void_reason"] == "endpoint_undefined":
                continue
            if dist and sid != "S2" and (r["dist_min"] != pct3(min(dist)) or r["dist_max"] != pct3(max(dist))):
                out.append("registered.csv %s: dist_min or dist_max does not recompute from the yardstick rows of changes.csv" % sid)
    return out


def pin_usd(text):
    """(value in USD, tolerance in USD) of a pin printed in billions: the tolerance is half the unit of the last printed digit (0.05bn for $0.1bn, 0.5mn for $0.001bn)."""
    t = text.replace(",", "")
    dec = Decimal(t)
    unit = Decimal(1).scaleb(dec.as_tuple().exponent)
    tol = unit / 2
    if M("g20_one_unit"):
        tol = unit
    if M("g20_wide"):
        tol = unit * Decimal("0.7")
    return dec * Decimal(10) ** 9, tol * Decimal(10) ** 9


def pin_ok(diff, tol):
    return abs(diff) < tol if M("g20_strict") else abs(diff) <= tol


def c03_report(ctx, dry=False):
    """C03: for the nine KNOWN bank-date pairs, the primary N and D equal the filing-note value within half the unit of the pin's last digit. A pin for a date the series lacks is reported."""
    bad, gaps = [], []
    for cik, end, nb, db in PINS:
        r = ctx["rows"].get(cik, {}).get("own_filing", {}).get(end)
        for tag, txt, key in (("N", nb, "n"), ("D", db, "d")):
            label = "%s %s %s" % (TICKER[cik], end, tag)
            if r is None or r["status"] != "ok":
                if not M("g20_absent_pass"):
                    bad.append("%s: no usable value" % label)
                continue
            v, tol = pin_usd(txt)
            diff = r[key] - v
            gaps.append(diff)
            if not pin_ok(diff, tol):
                bad.append("%s: off by %s USD" % (label, usd(diff)) if not dry else "%s: outside the tolerance" % label)
    return bad, gaps


def counts_checks(ctx, add):
    exp_n, exp_own = N_PERIOD_ENDS, N_OWN
    if M("g12_c01_65"):
        exp_n, exp_own = 65, 65
    if M("g12_c01_67"):
        exp_n, exp_own = 67, 65
    for b in ctx["banks"]:
        for t, _ in TAGS:
            c = b.conc[t]
            last = STT_LAST_PINNED if b.cik == STT else LAST_PINNED
            ends = [e for e in (c.period_ends() if c else []) if e <= last]
            cal = [e for e in ends if is_cal(e)]
            own = sum(1 for e in cal if c.own_accns(e))
            off = len(ends) - len(cal)
            obs = "period_ends=%d own_filing=%d off_calendar=%d" % (len(ends), own, off)
            if b.cik in PRIMARY:
                ok = len(ends) == exp_n and own == exp_own and (off == 0 or M("g12_offcal_pass"))
                add("C01", "%s %s counts (period-ends in 2009-12-31..%s, own filing, off-calendar)" % (b.ticker, t, last), "%d %d 0" % (exp_n, exp_own), obs, ok)
            elif b.cik == STT:
                ok = len(ends) == 52 and own == 51 and off == 0     # supervisor, 30 Oct: 2013-12-31 is comparative-only (pre-stage metadata)
                add("C01", "%s %s counts (period-ends in 2013-12-31..%s, own filing, off-calendar)" % (b.ticker, t, last), "52 51 0", obs, ok, warn=True)
            else:
                add("C01", "%s %s counts, printed for P3" % (b.ticker, t), "none pinned", obs, True, info=True)
    for b in ctx["banks"]:
        if b.cik not in PRIMARY and b.cik != STT:
            continue
        for t, _ in TAGS:
            c = b.conc[t]
            probs = []
            if c is None:
                probs.append("no facts")
            elif b.cik in PRIMARY:
                for i in range(qi("2010-06-30"), qi(LAST_PINNED) + 1):
                    e = qd(i)
                    if not c.own_accns(e) and not M("g12_c02_missing_pass"):
                        probs.append("%s not in own filing" % e)
                if c.has("2010-03-31") and not M("g12_c02_2010q1"):
                    probs.append("2010-03-31 is present")
                if not c.has("2009-12-31") or (c.own_accns("2009-12-31") and not M("g12_c02_2009_own")):
                    probs.append("2009-12-31 is not comparative-only")
            else:
                for i in range(qi("2014-03-31"), qi(STT_LAST_PINNED) + 1):
                    if not c.own_accns(qd(i)):
                        probs.append("%s not in own filing" % qd(i))
                if not c.has("2013-12-31") or c.own_accns("2013-12-31"):
                    probs.append("2013-12-31 is not comparative-only")
            add("C02", "%s %s expected dates" % (b.ticker, t), "every quarter-end in own filing; 2010-03-31 absent; 2009-12-31 comparative-only (JPM, GS)", "ok" if not probs else "; ".join(probs[:3]), not probs)


def build_checks(ctx, files, env):
    """The rows of checks.csv for the stage. env: pin_text, vint_rows (all vintages), raw_dir, dry, existing_reg (parsed rows of an earlier registered.csv or None)."""
    stage, dry = ctx["stage"], env.get("dry", False)
    rows = []

    def add(cid, desc, exp, obs, ok, warn=False, info=False):
        rows.append([cid, desc, exp, obs, "INFO" if info else ("PASS" if ok else ("WARN" if warn else "FAIL"))])

    counts_checks(ctx, add)
    add("C19", "captions_pin.csv equals SPEC_CAPTION_SHA256 and carries a class for each of the 24 bank-date-line cells", pin_sha_expected(),
        sha256_of(env["pin_text"].encode("utf-8")) if not dry else "checked", sha256_of(env["pin_text"].encode("utf-8")) == pin_sha_expected() and pin_cells_ok(ctx["pin_rows"]))
    cnt = collections.Counter()
    for b in ctx["banks"]:
        for basis in ("own_filing", "latest_filed"):
            cnt = collections.Counter(r["status"] for r in ctx["rows"][b.cik][basis].values())
            add("C12", "%s %s status counts" % (b.ticker, basis), "reported", " ".join("%s=%d" % (k, v) for k, v in sorted(cnt.items())), True, info=True)
    if stage == "pre":
        has_val = any("val" in f for b in ctx["banks"] for c in b.any_conc() for f in c.facts)
        add("C11", "--stage pre reads no val field", "no fact holds a val", "a fact holds a val" if has_val else "no fact holds a val", not has_val)
        return rows
    # C03
    bad, gaps = c03_report(ctx, dry)
    add("C03", "tie-outs against the nine KNOWN bank-date pairs (half the unit of the last printed digit)", "18 values within tolerance", "all within tolerance" if not bad and dry else
        ("%d values, largest unrounded gap %s USD" % (len(gaps), usd(max([abs(g) for g in gaps] or [Decimal(0)]))) if not bad else "; ".join(bad[:4])), not bad)
    # C04
    probs = []
    for c in PRIMARY:
        if c not in ctx["rows"]:
            continue
        b = ctx["by_cik"][c]
        for e, r in ctx["rows"][c]["own_filing"].items():
            if r["status"] == "ok" and not (b.conc["N"].facts_of(e, r["accession"]) and b.conc["D"].facts_of(e, r["accession"])):
                probs.append("%s %s" % (b.ticker, e))
    add("C04", "every primary quarter's N and D carry one accn", "0 quarters otherwise", "0" if not probs else "; ".join(probs[:3]), not probs)
    p5 = c05_problems(files)
    add("C05", "samples.csv closes against quarters.csv (sums, share to three decimals)", "0 problems", str(len(p5)) if not p5 else "; ".join(p5[:2]), not p5)
    pre_ok = prereg_ok() and pop_ok() and allow_hash_ok()
    reg_rows = env.get("existing_reg") or []
    reg_ok = all(r[ALLOW["registered.csv"].index("prereg_sha256")] == SPEC_PREREG_SHA256 and r[ALLOW["registered.csv"].index("population_sha256")] == SPEC_POP_SHA256 for r in reg_rows)
    add("C07", "the constants reproduce the hashes of 4.6, 4.7 and 5; registered.csv carries them", "4 hashes", "ok" if pre_ok and reg_ok else "a hash differs", pre_ok and reg_ok)
    p8 = c08_problems(files)
    add("C08", "changes.csv D8 and registered.csv recompute at full precision from quarters.csv", "0 problems", str(len(p8)) if not p8 else "; ".join(p8[:2]), not p8)
    vrows = [r for r in env.get("vint_rows", []) if r["vintage"] == ctx["vintage"]]
    probs = []
    for r in vrows:
        if r["status"] != "200":
            continue
        p = os.path.join(env.get("raw_dir") or "", raw_name(r["url_path"]) or "?")
        if not os.path.isfile(p):
            probs.append("%s missing" % r["url_path"][-40:])
        else:
            b = read_file(p, "rb")
            if sha256_of(b) != r["sha256"] or str(len(b)) != r["bytes"]:
                probs.append("%s differs from its row" % r["url_path"][-40:])
    add("C09", "each raw body's sha256 and size equal its vintages.csv row", "%d bodies" % sum(1 for r in vrows if r["status"] == "200"), "ok" if not probs else "; ".join(probs[:3]), not probs)
    if stage == "dry":
        names = sorted(env.get("dry_files", ()))
        ok = set(names) <= set(DRY_FILES) and all(r[3].startswith("count_") for r in env.get("dry_headline", []))
        add("C11", "--stage dry writes only status counts and checks", "headline.csv with count_ statistics, checks.csv", " ".join(names), ok)
    else:
        add("C11", "--stage full is the registering build; the pre stage read no val", "pre-stage reads no val field", "tested by the selftest (G17)", True, info=True)
    bad_status = [(b.ticker, r["end"], r["status"]) for c in PRIMARY if c in ctx["rows"] for b in [ctx["by_cik"][c]] for r in ctx["rows"][c]["own_filing"].values()
                  if r["status"] in ("unit_odd", "conflict", "ambiguous")]
    add("C14", "every unit key is USD; no primary quarter is unit_odd, conflict or ambiguous", "0 quarters", "0" if not bad_status else "; ".join("%s %s %s" % x for x in bad_status[:3]), not bad_status)
    y = ctx["y"]
    add("C20", "yardstick counts on the real data", "n_Y = %d, n_YR = %d" % (Y_EXP, YR_EXP), "n_Y = %d, n_YR = %d" % (len(y["members"]), len(y["yr"])), len(y["members"]) == Y_EXP and len(y["yr"]) == YR_EXP, warn=True)
    return rows


def pin_cells_ok(pin_rows):
    have = {(r[0], r[2], r[3]): r[5] for r in pin_rows if len(r) >= 6}
    for c in PRIMARY:
        for e in PIN_DATES:
            for ln in ("N", "D"):
                if have.get((c, e, ln)) not in ALLOWED_VALUES["class"]:
                    return False
    return True


def raw_name(path):
    m = CONCEPT_RX.match(path)
    return None if not m else "CIK%s__%s.json" % (m.group(1), m.group(2))


def concept_path(cik, tag):
    return "/api/xbrl/companyconcept/CIK%s/us-gaap/%s.json" % (cik, TAG_NAME[tag])


# ------------------------------------------------------------------------------------------------------------------------
# README.md and SOURCES.md
# ------------------------------------------------------------------------------------------------------------------------
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def longdate(e):
    return "%d %s %s" % (int(e[8:]), MONTHS[int(e[5:7]) - 1], e[:4])


def signed(x):
    s = pct3(x)
    return s if s.startswith("-") else "+" + s


VOID_WORDS = {
    "endpoint_undefined": "the share is undefined at one of the two dates (a bank-quarter is missing, was excluded, or reports more re-used than permitted)",
    "thin_yardstick": "the yardstick holds too few earlier changes",
    "endpoint_recast": "a value at one of the two dates was later restated by more than 1%",
    "caption_change": "the filers' wording for one of the lines changed class between the two dates",
    "mix_dominates": "the shift of weight between the two banks outweighs the change inside the banks",
    "yardstick_disagrees": "the narrower yardstick (from 2013) gives a different label from the full one",
}


def monthyear(e):
    return "%s %s" % (("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")[int(e[5:7]) - 1], e[:4])


def label_plain(label):
    return {"RISE_OUTSIDE_RANGE": "more than any two-year change in 2011-2019", "WITHIN_RANGE": "inside the range of 2011-2019 two-year changes", "FALL_OUTSIDE_RANGE": "less than any two-year change in 2011-2019",
            "LEVEL_ABOVE_RANGE": "above every level in 2017-2019, so unusual against that yardstick", "LEVEL_WITHIN_RANGE": "inside the 2017-2019 range, so not unusual against that yardstick",
            "LEVEL_BELOW_RANGE": "below every level in 2017-2019, so unusual against that yardstick"}[label]


def s2_clause(r, median):
    """The sign of S2, from the registered row and the median of the 2017-2019 levels: how far the level sits from the median, the sign, and what the range label says."""
    d = Decimal(r["stat"]) - median
    return "That is %s points %s the 2017-2019 median of %s%%, so the sign is %s; the range label says the level was %s." % (
        pct3(abs(d)), "above" if d >= 0 else "below", pct3(median), r["sign"], {"LEVEL_ABOVE_RANGE": "above every 2017-2019 level", "LEVEL_WITHIN_RANGE": "not unusual against 2017-2019",
                                                                               "LEVEL_BELOW_RANGE": "below every 2017-2019 level"}[r["label"]])


def plain_result(r, median):
    """One plain sentence per registered statement for the top of the README, from the registered row."""
    sid = r["statement_id"]
    if r["label"] == "VOID":
        return "%s could not be made for these two banks: %s." % (sid, VOID_WORDS.get(r["void_reason"], r["void_reason"]))
    if sid == "S2":
        d = Decimal(r["stat"]) - median
        return "On 31 December 2023 the level was %s%%, %s points %s the 2017-2019 median of %s%%, so the sign is %s; the range label says it was %s." % (
            r["stat"], pct3(abs(d)), "above" if d >= 0 else "below", pct3(median), r["sign"], label_plain(r["label"]))
    a, b = (S3_START, S3_END) if sid == "S3" else (S1_START, S1_END)
    mag = pct3(abs(Decimal(r["stat"])))
    verb = {"RISE": "rose %s points" % mag, "FALL": "fell %s points" % mag, "ZERO": "was unchanged to within 0.1 point (%s points)" % r["stat"]}[r["sign"]]
    return "Between %s and %s the share %s, %s." % (monthyear(a), monthyear(b), verb, label_plain(r["label"]))


def sentence(r, median=None):
    """The allowed sentence of 4, from a registered row (dict of text cells): sign and label together, the signed change always stated."""
    sid = r["statement_id"]
    if r["label"] == "VOID":
        return "The statement could not be made for these two banks: %s." % VOID_WORDS.get(r["void_reason"], r["void_reason"])
    if sid == "S2":
        rel = {"LEVEL_ABOVE_RANGE": "above", "LEVEL_WITHIN_RANGE": "inside", "LEVEL_BELOW_RANGE": "below"}[r["label"]]
        base = "On %s the fair-value share was %s%%, %s its 2017-2019 range (%s%% to %s%%)." % (longdate(S2_DATE), r["stat"], rel, r["dist_min"], r["dist_max"])
        return base + (" " + s2_clause(r, median) if median is not None else "")
    a, b = (S3_START, S3_END) if sid == "S3" else (S1_START, S1_END)
    verb = {"RISE": "rose", "FALL": "fell", "ZERO": "was unchanged to within 0.1 point"}[r["sign"]]
    chg = r["stat"] if r["stat"].startswith("-") else "+" + r["stat"]
    rel = {"RISE_OUTSIDE_RANGE": "more than every comparable two-year change in the 2011-2019 yardstick", "WITHIN_RANGE": "inside the range of the comparable two-year changes in the 2011-2019 yardstick",
           "FALL_OUTSIDE_RANGE": "less than every comparable two-year change in the 2011-2019 yardstick"}[r["label"]]
    return "From %s to %s the fair-value share of collateral re-used at JPMorgan Chase and Goldman Sachs %s, by %s points, %s (%s to %s points)." % (
        longdate(a), longdate(b), verb, chg, rel, r["dist_min"], r["dist_max"])


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def reg_dicts(rows):
    h = ALLOW["registered.csv"]
    return [dict(zip(h, r)) for r in rows]


def render_readme(ctx, reg_rows):
    v = ctx["vintage"]
    regs = reg_dicts(reg_rows)
    cur = {r["statement_id"]: r for r in regs if r["superseded"] == "no"}
    L = []
    A = L.append
    A("# The fair-value share of collateral re-used at JPMorgan Chase and Goldman Sachs")
    A("")
    A("This is the fair-value share of the collateral they may re-use that JPMorgan Chase and Goldman Sachs report having re-used, at every quarter-end from June 2010 to June 2026, as first "
      "reported in the original 10-Q or 10-K of each period (vintage %s)." % v)
    A("Three statements were registered before any value was read; each has a sign (RISE, FALL or ZERO, the zone being 0.1 point) and a range label that are separate, and the label only says "
      "whether the change was unusual against the yardstick of earlier eight-quarter changes, never whether the share rose.")
    A("")
    ylv = [v for _, v in ctx["yl"]["members"]]
    med = median(ylv) if ylv else None
    for sid in ("S3", "S1", "S2"):
        r = cur.get(sid)
        if r is not None:
            A("- %s" % plain_result(r, med))
    A("")
    A("How to read the table that follows:")
    A("")
    A("- **S3, S1, S2**: the three statements registered before any value was read. S3 is the change from December 2021 to December 2023, the years before the price rise (the 2024-26 rise in US equity prices, "
      "as the project overview at docs/index.html describes it); S1 is the change from December 2023 to December 2025; S2 is the level on 31 December 2023 against the levels of 2017-2019.")
    A("- **sign**: RISE if the change is at least 0.1 point up, FALL if at least 0.1 point down, otherwise ZERO; for S2 it is the sign of the level against the median of the 2017-2019 levels.")
    A("- **range label**: whether the change was unusual against the yardstick, the earlier two-year changes of 2011-2019. WITHIN_RANGE never means that the share did not rise.")
    A("- **rank**: the position of the statistic among the yardstick members plus itself; rank 1 is the largest, so 3 of 24 means two members are larger.")
    A("- **n in yardstick**: the number of earlier changes (for S2, earlier levels) the statistic is compared with.")
    A("- **blind**: full means no value for the dates involved was known to the author before the build; partial means some were (see What was known before the build).")
    A("- **VOID**: no statement can be made; the reason is given in the void reason column. recast, one of those reasons, means a bank later restated a value at one of the two dates by more than 1%.")
    A("- **C-135**: the project's correction C-135, in CORRECTIONS.md, which says a share at a date is not a speed.")
    A("")
    rows = []
    for sid in ("S3", "S1", "S2"):
        r = cur.get(sid)
        if r is None:
            continue
        win = {"S3": "31 Dec 2021 to 31 Dec 2023", "S1": "31 Dec 2023 to 31 Dec 2025", "S2": "level on 31 Dec 2023"}[sid]
        rows.append([sid, win, r["sign"] or "-", r["label"], (r["stat"] + (" points" if r["unit"] == "pp" else "%")) if r["stat"] else "-", "%s to %s" % (r["dist_min"], r["dist_max"]) if r["dist_min"] else "-",
                     ("%s of %s" % (r["rank"], r["rank_of"])) if r["rank"] else "-", r["n_dist"], r["blind"], r["void_reason"]])
    A(md_table(["statement", "window", "sign", "range label", "statistic", "yardstick lowest to highest", "rank", "n in yardstick", "blind", "void reason"], rows))
    A("")
    for sid in ("S3", "S1", "S2"):
        r = cur.get(sid)
        if r is not None:
            A("- **%s.** %s %s" % (sid, sentence(r, med), AFTER_SENTENCE))
    A("")
    A("S3 is the statement for the years before the price rise (blind: full). S1 covers the window of the price rise itself and ends before the first half of 2026 (blind: partial). S2 is a "
      "level against the 2017-2019 range (blind: partial). A WITHIN_RANGE label states the signed change and never means that the share did not rise.")
    A("")
    A("## What this is not")
    A("")
    A(DENIAL_SENTENCE)
    A("")
    A("The perimeter is two banks. The page (the project overview at docs/index.html) gives 81.7% (December 2025) and 83.2% (June 2026), which are the six-bank share of JPMorgan, Goldman, Morgan Stanley, Bank of America, BNY and Wells Fargo; the "
      "six-bank share before 2025 stays unmeasured, and this two-bank history is a separate object reported in a separate sentence.")
    A("")
    A("Left out: a speed or chain length; prices; money; intraday or off-quarter re-use (the quarter-end note does not show it); the Treasury repo alone (the lines cover every collateral class, "
      "derivatives and prime brokerage included); the other banks. Both legs are fair values, so a price move in the collateral can move the share with no new re-use; this is why the "
      "statistic is called a fair-value share.")
    A("")
    A("## The yardstick")
    A("")
    y = ctx["y"]
    A("The yardstick Y is the set of eight-quarter changes in the share (percentage points) that end between 31 Dec 2011 and 31 Dec 2019, with the share defined at both dates and the window not "
      "spanning the caption change below: %d nominal, %d defined, %d excluded for the caption change, %d members (%d expected; a statement is VOID below %d). The robustness yardstick YR (ends from "
      "31 Dec 2013) has %d members (%d expected; VOID below %d). The level yardstick YL is the share at the quarter-ends 31 Mar 2017 to 31 Dec 2019: %d of %d defined (VOID below %d)." % (
          y["nominal"], len(y["defined"]), len(y["excluded"]), len(y["members"]), Y_EXP, Y_MIN, len(y["yr"]), YR_EXP, YR_MIN, len(ctx["yl"]["members"]), ctx["yl"]["nominal"], YL_MIN))
    A("")
    A("The yardstick is thin: the usable levels run 2010-06-30 to 2016-12-31 (three disjoint spans) and 2017-03-31 to 2019-12-31 (one span), so it holds at most four independent draws. "
      "A simulation shows what chance alone would give: if the share moved at random with no change in behaviour (standard-normal quarterly increments, 200,000 replications, seed 14), a new change would exceed the yardstick's maximum about 11% of the time "
      "(roughly one in nine) and fall outside it on either side about 22% of the time; for the robustness yardstick the figures are 14% and 28%. A RISE_OUTSIDE_RANGE label would therefore "
      "still appear roughly one time in nine with no change in behaviour at all.")
    A("")
    if not M("g21_readme_no_2017"):
        A(CAPTION_LINE)
        A("")
    A("## The path of the share")
    A("")
    prim = ctx["series"][("primary", "own_filing")]
    path = []
    for i in sorted(prim):
        e = qd(i)
        if e.endswith("-12-31") or i == max(prim):
            cells = [e, pct3(prim[i])]
            for nm in ("sens_jpm", "sens_gs"):
                s = ctx["series"].get((nm, "own_filing"), {})
                cells.append(pct3(s[i]) if i in s else "-")
            path.append(cells)
    A(md_table(["quarter-end", "two-bank share (%)", "JPMorgan (%)", "Goldman Sachs (%)"], path))
    A("")
    A("Every quarter-end is in samples.csv and quarters.csv. The split of each registered change into a within-bank part and a weight-shift part is in decomposition.csv. The split is exact: each bank's within part is the change in its own share times the average of its start and end weights, and its weight-shift part is the change in its weight times the average of its start and end shares (a Shapley split); the weights are each bank's permitted collateral over the two banks' total.")
    A("")
    drows = []
    for sid in ("S3", "S1"):
        d = ctx["decomp"].get(sid)
        if d is not None:
            drows.append([sid, pct3(d["total"]), pct3(d["within"]), pct3(d["mix"]), "VOID (mix_dominates)" if mix_dominates(d) else "no"])
    A(md_table(["statement", "total (points)", "within banks", "weight shift", "weight shift dominates"], drows))
    A("")
    A("## Sensitivities and variants (never registered; n is the number of earlier changes in the sample's own yardstick)")
    A("")
    srows = []
    base = ctx["light"][("primary", "own_filing")][0]
    differ, thin = [], []
    for (name, basis), (light, yy, yl) in ctx["light"].items():
        cells = [name, basis]
        for sid in ("S3", "S1", "S2"):
            st = light[sid]
            cells.append("%s %s (n=%d)" % (st["sign"] or "-", st["label"], st["n"]))
            if (name, basis) != ("primary", "own_filing"):
                if st["label"] == "VOID":
                    thin.append("%s %s on %s" % (sid, name, basis))
                elif st["label"] != base[sid]["label"]:
                    differ.append("%s %s on %s" % (sid, name, basis))
        srows.append(cells)
    A(md_table(["sample", "basis", "S3", "S1", "S2"], srows))
    A("")
    A("A sensitivity gives a different label from the primary for: %s. A sensitivity is VOID (too few earlier changes, or an undefined endpoint) for: %s." % (", ".join(differ) if differ else "none", ", ".join(thin) if thin else "none"))
    A("")
    A("The names: **primary** is the two banks together (sum of re-used over sum of permitted); **sens_jpm** and **sens_gs** are one bank alone; **sens_eqw** gives the two banks equal weight (the mean of their shares); "
      "**sens_noflag** drops every quarter flagged recast or jump; **sens_stt** adds State Street; **sens_wfc** adds State Street and Wells Fargo if its counts qualify. **own_filing** takes each value from the original "
      "10-Q or 10-K of its period; **latest_filed** takes the latest filing that reports it.")
    A("")
    pooled = {sid: cur[sid]["sign"] for sid in ("S3", "S1") if sid in cur and cur[sid]["sign"]}
    names = {JPM: "JPMorgan's", GS: "Goldman's"}
    verbs = {"RISE": "rose", "FALL": "fell", "ZERO": "was unchanged"}
    clauses = []
    for sid, yrs in (("S3", "2021-2023"), ("S1", "2023-2025")):
        d = ctx["decomp"].get(sid)
        if d is None or sid not in pooled:
            continue
        per = [(x["cik"], sign_of(x["s1"] - x["s0"])) for x in d["banks"]]
        if any(sg != pooled[sid] for _, sg in per):
            clauses.append("over %s %s" % (yrs, " and ".join("%s own share %s" % (names[c], verbs[sg]) if i == 0 else "%s %s" % (names[c], verbs[sg]) for i, (c, sg) in enumerate(per))))
    if clauses:
        A("Where a bank's own change differs in sign from the pooled change: %s. The pooled change is not a statement about each bank." % "; ".join(clauses))
    else:
        A("In both windows each bank's own change has the sign of the pooled change; the pooled change is still not a statement about each bank.")
    A("")
    if ("sens_stt", "own_filing") in ctx["light"] and ctx["by_cik"].get(STT) is not None:
        lt = ctx["light"][("sens_stt", "own_filing")][0]
        qs = ctx["rows"][STT]["own_filing"]
        n_odd = sum(1 for r in qs.values() if r["status"] == "unit_odd")
        n_ok = sum(1 for r in qs.values() if r["status"] == "ok")
        n_own = sum(1 for r in qs.values() if r["accession"])
        if lt["S3"]["label"] == "VOID" or lt["S1"]["label"] == "VOID":
            A("Why sens_stt and sens_wfc are VOID for S3 and S1: State Street has %d own-filing quarters (its first year-end, 2013-12-31, exists only as a comparative in later filings, a supervisor decision), "
              "%d of them are usable and %d fall outside the unit band of 1e9 to 1e13 dollars and are excluded, so its shares start in 2014. After the eight windows that span JPMorgan's caption change are "
              "removed, %d earlier changes remain in their yardstick, fewer than the %d the spec requires." % (n_own, n_ok, n_odd, lt["S3"]["n"], SENS_MIN_N))
            A("")
    vh = {r[3]: r[4] for r in rows_headline(ctx)}
    A("The unrestricted 2011-start yardstick (it keeps the windows that span the caption change) holds %s windows; its S3 label is %s and its S1 label is %s. %s" % (
        vh.get("variant_a_n", "-"), vh.get("variant_a_S3_label", "-"), vh.get("variant_a_S1_label", "-"),
        "It gives a different range label from the registered yardstick for a registered statement." if "yes" in (vh.get("variant_a_S3_differs_from_Y"), vh.get("variant_a_S1_differs_from_Y"))
        else "It gives the same range labels as the registered yardstick."))
    A("")
    A("## Captions")
    A("")
    A("The caption classes are the filers' own wording of each line, read from the company label linkbase: JN1 is JPMorgan's numerator \"sold or repledged\", JN2 its wider numerator \"sold, repledged, delivered or "
      "otherwise used\"; JD1 is JPMorgan's denominator, \"permitted to be sold or repledged, delivered or otherwise used\"; GN1 is Goldman's numerator \"delivered or repledged\" and GD1 its denominator "
      "\"permitted to deliver or repledge\". A statement is VOID if a class differs between its two dates.")
    A("")
    A(md_table(["bank", "10-K for", "line", "class", "wording"], [[r[1], r[2][:4], r[3], r[5], r[6]] for r in ctx["pin_rows"]]))
    A("")
    A("The recast flag at 2016-12-31, per bank: %s." % ", ".join("%s %s" % (TICKER[c], vh.get("recast_2016-12-31_%s" % TICKER[c], "-")) for c in PRIMARY))
    A("")
    A("## What was known before the build")
    A("")
    A("The repository already held some filing-note values for these two banks (nine bank-date pairs, listed in SOURCES.md, and some shares). They shaped no choice of window, threshold, label or "
      "bank set, and they are used only as tie-out pins. The author also formed, without recording a figure, an impression that the two-bank share was in the low 80s percent at the end of 2024 "
      "and 2025. So S3 is blind in full, while S1 and S2 are blind in part: the `blind` column says which.")
    A("")
    A("## Later filings")
    A("")
    rev = rows_revisions(ctx)
    lrows = []
    for b in ctx["banks"]:
        if b.role == "probe":
            continue
        rr = [r for r in rev if r[0] == b.cik]
        lrows.append([b.ticker, len(rr), sum(1 for r in rr if r[9] == "recast"), sum(1 for r in rr if r[6] and r[6] not in ("0.000", "-0.000"))])
    A(md_table(["bank", "bank-quarter-tag rows", "flagged recast (more than 1% apart)", "rows with any difference"], lrows))
    A("")
    A("recast: the latest-filed value differs from the first-reported one by more than 1% on either tag (a recast at an end of S1 or S3 voids that statement). jump: either tag moved by more than "
      "30% from the previous quarter-end. amended: an amendment exists for the period. Flags are prompts to look; they remove nothing from the primary sample.")
    A("")
    A("## Coverage")
    A("")
    brows = rows_banks(ctx)
    odd = {b.ticker: sum(1 for r in ctx["rows"][b.cik]["own_filing"].values() if r["status"] == "unit_odd") for b in ctx["banks"]}
    A(md_table(["bank", "tag", "role", "period-ends", "calendar", "off calendar", "own filing", "first", "last", "quarters outside the unit band"], [[r[1], r[4], r[3], r[5], r[6], r[7], r[8], r[9], r[10], odd.get(r[1], 0)] for r in brows]))
    A("")
    A("Expected: 66 period-ends and 65 in own filing for each primary bank and tag (2010-06-30 to 2026-06-30), 2010-03-31 absent, 2009-12-31 only a comparative, none off calendar. For State Street: 52 period-ends and 51 in own filing (2013-12-31 only a comparative, a supervisor decision), from 2014-03-31 on. "
      "A quarter outside the unit band (a value below 1e9 or above 1e13 dollars) is excluded from every sample.")
    A("")
    sup = [r for r in regs if r["superseded"] == "yes"]
    if sup:
        A("## Superseded rows")
        A("")
        A(md_table(["statement", "version", "label", "statistic"], [[r["statement_id"], r["version"], r["label"], r["stat"]] for r in sup]))
        A("")
    A("## Columns")
    A("")
    A("- **fair-value share**: the fair value of collateral reported as re-used divided by the fair value of collateral permitted to be re-used, in percent, summed over the banks of the sample.")
    A("- **permitted to be re-used**: collateral received that the bank is allowed to sell or repledge.")
    A("- **re-pledged**: the part it has sold, repledged, delivered or otherwise used, as the filing words it.")
    A("- **first reported**: the value in the original 10-Q or 10-K of that period, not a later restated one.")
    A("- **quarter-end**: 31 March, 30 June, 30 September or 31 December.")
    A("- **yardstick**: the earlier eight-quarter changes (2011-2019) against which a change is compared.")
    A("- **percentage point**: a difference between two percentages.")
    A("- **vintage**: the date the SEC files were read.")
    A("")
    A("## Citation")
    A("")
    A(SOURCE_TXT % v + ". Caption pins: company label linkbase of the filing, read by the supervisor on 2026-10-30. Specification: %s (commit %s). See SOURCES.md." % (SPEC_FILE, SPEC_COMMIT))
    return "\n".join(L) + "\n"


BUILDER_DECISIONS = (
    "Supervisor decision, 30 Oct 2026, after the pre stage on vintage 20261030 (metadata only, no values): State Street's first year-end, 2013-12-31, is in later filings only (comparative-only), like JPM's and GS's 2009-12-31. C01 expects 52 period-ends with 51 in own filing, and C02 expects own filing from 2014-03-31 with 2013-12-31 comparative-only. This corrects the supervisor's own pin in ruling R1-10; it touches no hashed block, and sens_stt starts at 2014-03-31 under P8.",
    "In the pre stage a quarter is `ok` when it is present in one filing for both tags; conflict, unit_odd and ratio_gt_1 need values and are assigned from the dry stage on (R1-7, C11).",
    "quarters.csv has a row for every calendar quarter-end from a bank's first to its last, so the absent 2010-03-31 appears with status missing_n; an off-calendar end gets a row with status off_calendar; if both tags are absent the status is missing_n, if only the denominator is absent missing_d.",
    "Wells Fargo enters sens_wfc iff both tags have a 10-K or 10-Q period-end at every one of the 51 quarter-ends 2013-12-31..2026-06-30 (counts and dates only, P3); P8 then decides which dates are usable.",
    "C01 counts period-ends up to 2026-06-30 for JPM and GS (up to 2026-09-30 for State Street), so a later vintage with a Q3 2026 filing does not fail it. concept_extract.csv lists the facts that end on or after 2009-12-31.",
    "A VOID statement carries label VOID and a blank sign (the sign is tested after the VOID reasons); the statistic, the yardstick extremes, the rank and the gap are still written when defined.",
    "gap_to_extreme = min(stat - min, max - stat) of the yardstick, unrounded and written to 6 decimals: positive or zero when the label is WITHIN, negative when it is outside.",
    "rank = 1 + the number of yardstick members above the statistic; rank_of = members + 1; ties share the better rank.",
    "mix_dominates keeps the 'mix and within nonzero' words of the hashed 4.6 text on top of the same sign and larger size (round-2 ruling O-1).",
    "sens_latest takes, per tag, the fact with the latest filing date (ties to the largest accn); if the two tags' latest accessions differ the row's status is own_filing_lacks_tags (the nearest listed status).",
    "A timeout is logged in vintages.csv as a row with status 0 so that every request is one row; the next successful request of the same path replaces it. It writes no STOP.",
    "A q/q jump is judged only against the immediately preceding calendar quarter-end of the same basis when that row is ok; a missing neighbour gives no flag.",
    "The caption-change exclusion applies to every sample that holds JPMorgan Chase (primary and the State Street, Wells Fargo, JPM-only, equal-weight and no-flag samples); the Goldman-only sample has none (variant d).",
    "changes.csv writes level rows with an empty start_end and share_start_pct; role registered is used only for the primary sample on the own_filing basis; every sample and basis carries its own yardstick rows.",
    "samples.csv flags are the union of the banks' flags; sens_eqw's share is the mean of the banks' ratios, so C05 and C08 recompute it that way and the other samples as sum N over sum D.",
    "C08 recomputes registered rows only when the vintage in registered.csv is the vintage in headline.csv; a row from an earlier vintage is left alone (INFO).",
    "The dry stage writes headline.csv (count_ statistics only) and checks.csv, to the folder given by --out; the checks it writes carry no value (C03 reports only that the pins are within tolerance).",
    "SPEC_COMMIT is ccacee1, the commit that holds the spec, the rulings and captions_pin.csv.",
    "The decomposition file has one row per bank and one ALL row; its window column is the two dates joined by two dots.",
    "A fact without a val is treated as absent (never zero); a non-numeric val is a data error. Dollar values are quantized to whole dollars (half-even) when a bank-quarter row is made; the unit bounds are tested on the unrounded value.",
    "Any bank (including Wells Fargo) whose file has a unit key other than exactly USD, or a fact key outside the P7 list, stops the build with a data error.",
    "The tie-out pins use the primary own_filing rows; a pin for a date without a usable value is reported as a failure of C03.",
    "registered.csv is written once, by the first full build; it is kept byte-identical afterwards. `build --stage full --supersede` is the P19 route: old rows are marked superseded = yes and the corrected rows are added with the next version.",
    "--stage has no default; the stage must be named. The dry stage reads vintages.csv and registered.csv from the committed folder (--committed, default data/collateral_reuse) and writes only to --out, which may not be that folder.",
    "The headline.csv sample column holds the sample a statistic belongs to; count statistics sit under `primary`; variants a to c sit under `primary` and variant d under `sens_gs`.",
    "A full build in which any check FAILs writes checks.csv and nothing else (no registered.csv, no README), so a registered row can never come from a failed run; WARN and INFO rows do not block.",
    "The State Street and Wells Fargo samples start their yardsticks at 2015-12-31 (P2); the spec's exclusion of the eight caption-spanning windows then leaves 9 members, below the n = 10 floor of P18, so their S3 and S1 are VOID on any data. This is the spec's arithmetic, not a defect.",
    "The probes.csv verdict is counts_only when the file for both tags is absent (404), otherwise enters or does_not_enter, the same on both tag rows.",
)


def render_sources(ctx, env):
    v = ctx["vintage"]
    L = []
    A = L.append
    A("# Sources: collateral re-use history")
    A("")
    A("## Source")
    A("")
    A(SOURCE_TXT % v + ". US government works (17 U.S.C. 105). Caption pins: company label linkbase of the filing (wording only), read by the supervisor on 2026-10-30; the file is captions_pin.csv.")
    A("")
    A("## Requests (data.sec.gov, vintage %s)" % v)
    A("")
    vr = [r for r in env.get("vint_rows", []) if r["vintage"] == v]
    A(md_table(["URL", "date (UTC)", "HTTP status"], [["https://%s%s" % (r["host"], r["url_path"]), r["retrieved_utc"][:10], r["status"]] for r in vr]))
    A("")
    A("## Specification and rules")
    A("")
    A("The specification is `%s`, committed at %s with the supervisor's rulings of rounds 1 and 2 and the caption pins, before any value was read. The own-filing rule (P8): the primary value of a "
      "quarter-end is a fact of the original 10-K or 10-Q of that period, in which the end equals the end implied by the filing's own fiscal year and period, the filing date is 0 to 100 days after "
      "the end, and the end is the latest end among that filing's facts for the tag; the numerator and the denominator must be facts of the same accession. First reported means that value; a "
      "later restated value appears only in revisions.csv and in the latest_filed basis." % (SPEC_FILE, SPEC_COMMIT))
    A("")
    A("## What was known before the build")
    A("")
    A(md_table(["bank", "date", "re-pledged (bn)", "permitted (bn)"], [[TICKER[c], e, n, d] for c, e, n, d in PINS]))
    A("")
    A("Also known as shares: JPM 78.2% (Jun 2025) and 79.8% (Jun 2026), GS 85.2% and 88.4%; JPM 80.0% at 31 Dec 2017; the four-name share 80.4% at 31 Dec 2017; 77.8% at FY2019 and 79.2% at FY2025 "
      "for the four US dealers disclosing both legs; the four-bank 82.6% (Jun 2025) and 84.0% (Jun 2026); the six-bank 81.7% (Dec 2025) and 83.2% (Jun 2026). They enter the build only as tie-out pins.")
    A("")
    A("## Builder decisions")
    A("")
    for i, d in enumerate(BUILDER_DECISIONS, 1):
        A("%d. %s" % (i, d))
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------------------------------
# reading the cache and building (stages pre, dry, full)
# ------------------------------------------------------------------------------------------------------------------------

def vint_rows(out_dir):
    """The rows of vintages.csv as dicts ([] when absent). Only the fetch mode writes this file."""
    h, rows = read_csv_rows(os.path.join(out_dir, "vintages.csv"))
    return [dict(zip(h, r)) for r in rows] if list(h) == ALLOW["vintages.csv"] else []


def check_cache(cache, root=ROOT, out_dir=None):
    """The cache may be outside the repository, or inside it only under data/vintages/ (never in the committed output folder)."""
    real = os.path.realpath(os.path.expanduser(cache))
    rroot = os.path.realpath(root)
    if real == rroot or real.startswith(rroot + os.sep):
        outd = os.path.realpath(out_dir or os.path.join(root, "data", "collateral_reuse"))
        if real == outd or real.startswith(outd + os.sep):
            raise Refused("the cache may not live in the committed output folder")
        rel = os.path.relpath(real, rroot).replace(os.sep, "/") + "/"
        if not rel.startswith("data/vintages/"):
            raise Refused("a cache inside the repository must be under data/vintages/")
    return real


def load_pins(out_dir, pin_path=None):
    """(text, rows) of captions_pin.csv: an input, never written by this script. It is read from the committed folder."""
    p = pin_path or os.path.join(OUT_DEFAULT, PIN_NAME)
    if not os.path.isfile(p):
        raise DataError("captions_pin.csv is missing")
    text = read_file(p, "r")
    h, rows = read_csv_rows(p)
    if list(h) != ALLOW[PIN_NAME]:
        raise DataError("captions_pin.csv: header is not the allowlist")
    return text, rows


def load_banks(cache, out_dir, vintage, stage):
    """The four banks from the raw bodies of one vintage: a path's row in vintages.csv must belong to that vintage (the mutant takes any), a 404 row means absent."""
    rows = vint_rows(out_dir)
    raw_dir = os.path.join(cache, vintage, "raw")
    banks = []
    for cik, ticker, role in BANK_TABLE:
        conc, name = {}, ""
        for tag, _ in TAGS:
            path = concept_path(cik, tag)
            cand = [r for r in rows if r["url_path"] == path and (r["vintage"] == vintage or M("g17_mixed"))]
            if not cand:
                raise DataError("vintages.csv has no row for %s in vintage %s: run fetch-concepts first" % (path[-60:], vintage))
            row = cand[0]
            if row["status"] == "404":
                conc[tag] = None
                continue
            if row["status"] != "200":
                raise DataError("vintages.csv status %s for %s" % (row["status"], path[-60:]))
            p = os.path.join(raw_dir, raw_name(path))
            if not os.path.isfile(p):
                raise DataError("the raw body of %s is missing from the cache" % raw_name(path))
            facts, nm, cik_doc = parse_concept(read_file(p, "rb"), stage)
            if cik_doc is not None and cik_doc != cik:
                raise DataError("%s holds the facts of CIK %s" % (raw_name(path), cik_doc))
            conc[tag] = Concept(facts)
            name = name or nm
        banks.append(Bank(cik, ticker, role, conc["N"], conc["D"], name))
    return banks, rows, raw_dir


def make_texts(ctx, env):
    """Every output text of the stage, in memory, and the checks computed on them."""
    stage, v = ctx["stage"], ctx["vintage"]
    t = collections.OrderedDict()
    t["banks.csv"] = render_csv("banks.csv", rows_banks(ctx), source_line(v, "period-end counts per bank and tag"))
    t["probes.csv"] = render_csv("probes.csv", rows_probes(ctx), source_line(v, "Wells Fargo counts and dates only (P5), no value"))
    t["quarters.csv"] = render_csv("quarters.csv", rows_quarters(ctx), source_line(v, "one row per bank, quarter-end and basis; USD as reported, first reported on basis own_filing"))
    if stage != "pre":
        t["samples.csv"] = render_csv("samples.csv", rows_samples(ctx), source_line(v, "share = sum N / sum D over the banks of the sample, percent"))
        t["changes.csv"] = render_csv("changes.csv", rows_changes(ctx), source_line(v, "eight-quarter changes in percentage points and levels"))
        t["decomposition.csv"] = render_csv("decomposition.csv", rows_decomposition(ctx), source_line(v, "exact Shapley split of the S1 and S3 changes"))
        t["revisions.csv"] = render_csv("revisions.csv", rows_revisions(ctx), source_line(v, "first-reported against latest-filed values"))
        t["headline.csv"] = render_csv("headline.csv", rows_headline(ctx), source_line(v, "counts, sensitivities and variants; described, never registered"))
        new = rows_registered_new(ctx)
        old = env.get("existing_reg")
        if env.get("supersede"):
            if not old:
                raise Refused("--supersede needs an existing registered.csv")
            reg = supersede_rows(old, new)
        else:
            reg = old if old and not M("g17_rewrite_registered") else new
        env["existing_reg"] = reg
        t["registered.csv"] = render_csv("registered.csv", reg, source_line(v, "registered once, by the first full build; never re-scored (P19)"))
        t["README.md"] = render_readme(ctx, reg)
        t["SOURCES.md"] = render_sources(ctx, env)
        for n in ("README.md", "SOURCES.md"):
            guard_text(n, t[n])
    checks = build_checks(ctx, t, env)
    t["checks.csv"] = render_csv("checks.csv", checks, source_line(v, "the pinned checks of section 8 of the spec"))
    return t, checks


def run_build(a):
    t0 = time.time()
    stage = a.stage
    out_dir = os.path.abspath(a.out)
    # pre and full write into the committed folder and read their inputs there; the dry stage writes to a scratch folder and reads its inputs from the committed one (--committed)
    src = os.path.abspath(getattr(a, "committed", None) or OUT_DEFAULT) if stage == "dry" else out_dir
    if stage == "dry":
        if getattr(a, "out", None) is None or (os.path.realpath(out_dir) in (os.path.realpath(src), os.path.realpath(OUT_DEFAULT)) or os.path.realpath(out_dir).startswith(os.path.realpath(src) + os.sep)) and not M("g17_dry_committed"):
            raise Refused("the dry stage never writes into the committed folder: give --out a scratch folder")
    cache = check_cache(a.cache, out_dir=src)
    if not vintage_ok(a.vintage):
        raise Refused("--vintage must be a date YYYYMMDD")
    reg_path = os.path.join(src, "registered.csv")
    existing = None
    if os.path.isfile(reg_path):
        h, rows = read_csv_rows(reg_path)
        if list(h) == ALLOW["registered.csv"]:
            existing = rows
    if stage == "pre" and existing:
        raise Refused("registered.csv exists: a pre build would overwrite the full outputs with the pre subset")
    pin_text, pin_rows = load_pins(src, getattr(a, "pins", None))
    banks, vrows, raw_dir = load_banks(cache, src, a.vintage, stage if stage == "pre" else "full")
    ctx = compute(banks, stage, a.vintage, pin_rows)
    env = dict(pin_text=pin_text, vint_rows=vrows, raw_dir=raw_dir, dry=stage == "dry", existing_reg=existing, supersede=getattr(a, "supersede", False), out_dir=out_dir)
    if stage == "dry":
        env["dry_files"] = list(DRY_FILES) + (["registered.csv"] if M("g17_dry_writes_registered") else []) + (["quarters.csv"] if M("g17_dry_writes_values") else [])
        env["dry_headline"] = [[r[0], r[1], r[2], r[3]] for r in rows_headline(ctx, counts_only=True)]
    readme_only = getattr(a, "readme_only", False)
    if readme_only and (stage != "full" or not existing or env.get("supersede")):
        raise Refused("--readme-only needs --stage full, an existing registered.csv and no --supersede")
    texts, checks = make_texts(ctx, env)
    failed = [r[0] for r in checks if r[4] == "FAIL"]
    if readme_only:
        todo = {} if failed else {n: texts[n] for n in ("README.md", "SOURCES.md")}
        if M("g17_readme_only_writes_all"):
            todo = {n: x for n, x in texts.items() if n != "registered.csv"}
    elif stage == "pre":
        todo = {n: texts[n] for n in PRE_FILES}
    elif stage == "dry":
        todo = {"headline.csv": render_csv("headline.csv", rows_headline(ctx, counts_only=True), source_line(a.vintage, "dry stage: status counts only")), "checks.csv": texts["checks.csv"]}
        if M("g17_dry_writes_registered"):
            todo["registered.csv"] = texts["registered.csv"]
        if M("g17_dry_writes_values"):
            todo["quarters.csv"] = texts["quarters.csv"]
    else:
        todo = {n: x for n, x in texts.items() if not (n == "registered.csv" and existing and not env.get("supersede") and not M("g17_rewrite_registered"))}
        if failed:
            todo = {"checks.csv": texts["checks.csv"]}               # a failing check writes the checks and nothing else (see Builder decisions)
        else:
            problems = folder_problems(dict(texts), full=False)
            if problems:
                raise DataError("; ".join(problems[:3]))
    write_outputs(todo, out_dir)
    if stage == "full" and not failed and not readme_only:
        write_text(os.path.join(cache, a.vintage, "concept_extract.csv"), render_csv("concept_extract.csv", rows_extract(ctx), source_line(a.vintage, "facts of the two tags, as the SEC served them")))
    if M("g16_second_writer") and stage == "full":
        write_text(os.path.join(out_dir, "vintages.csv"), render_csv("vintages.csv", [list(r.values()) for r in reversed(vrows)], "# source: x"))
    print("vintage %s, stage %s: %d banks (%s)" % (a.vintage, stage, len(banks), ", ".join("%s %s" % (b.ticker, b.role) for b in ctx["banks"])))
    if stage != "pre":
        print("== status counts and yardstick members")
        for basis, stat, v in count_rows(ctx):
            if basis == "own_filing":
                print("   %s = %s" % (stat, v))
    if stage == "full" and not failed:
        for sid in ("S3", "S1", "S2"):
            s = ctx["stmts"][sid]
            print("== %s: stat %s %s, sign %s, label %s, void %s (n %s, yardstick %s to %s)" % (sid, pct3(s["stat"]) or "blank", s["unit"], s["sign"] or "-", s["label"], s["void"], s["n_dist"],
                                                                                                  pct3(s["dmin"]) or "-", pct3(s["dmax"]) or "-"))
    print("== checks")
    for r in checks:
        if r[4] != "PASS" or stage != "full":
            print("   %-4s %-5s %s" % (r[0], r[4], r[3][:160]))
    print("failed: %s; wrote %d file(s) to %s (%.1f s)" % (", ".join(sorted(set(failed))) or "none", len(todo), tilde(out_dir), time.time() - t0))
    return 1 if failed else 0


# ------------------------------------------------------------------------------------------------------------------------
# requests: the URL check (R1), the content tests (R3a) and the fetcher (R2, R3, R4)
# ------------------------------------------------------------------------------------------------------------------------
def check_url(url):
    """Only a plain https GET to data.sec.gov for a companyconcept file of one of the two tags. www.sec.gov, efts.sec.gov, the ZIPs and FRED are refused before the request. Returns (host, path)."""
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    if M("g16_other_host"):
        return host, p.path
    if p.scheme != "https" or p.username or p.password or p.port not in (None, 443) or p.fragment or p.query:
        raise Refused("only plain https URLs without a query are allowed")
    if host != HOST:
        if any(host == b or host.endswith("." + b) for b in BLOCKED_HOSTS):
            raise Refused("host %s is never requested (only %s is)" % (host, HOST))
        raise Refused("host %s is not on the allowlist" % host)
    if not CONCEPT_RX.match(p.path):
        raise Refused("only companyconcept paths of the two tags are requested")
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
    if not M("g15_stop_short"):
        lines.append("retry_after: %s" % retry_after)
    lines.append("body_head: %s" % body_head)
    return "\n".join(lines) + "\n"


def stop_text_ok(text):
    return [l.split(":", 1)[0] for l in text.splitlines()] == list(STOP_FIELDS)


def create_stop(path, text):
    """The one place a STOP file is created: exclusive create ("x"), so an existing latch is never overwritten."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "x", encoding="utf-8") as fh:
            fh.write(text)
    except FileExistsError:
        if M("g15_overwrite"):
            _clobber(path, text)                  # the mutant: what create_stop must never do; run-time test only


def _clobber(p, text):
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


def looks_like_page(body):
    return body.lstrip()[:15].lower().startswith((b"<!", b"<html"))


def body_check(body, expect):
    """R3a: a 200 body that is empty, a web page, not JSON or not the document asked for is a content failure. expect: (cik10, tag)."""
    if not body and not M("g15_empty_ok"):
        return "empty body"
    if body and looks_like_page(body) and not M("g15_html_ok"):
        return "the body is a web page"
    try:
        doc = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return "" if M("g15_nonjson_ok") else "the body is not JSON"
    if not isinstance(doc, dict):
        return "the JSON body is not an object"
    ok = isinstance(doc.get("units"), dict) and cik10(doc.get("cik")) == expect[0] and doc.get("tag", TAG_NAME[expect[1]]) == TAG_NAME[expect[1]]
    return "" if ok else "the body is valid JSON but not the document asked for"


def fetch_vintage_ok(vintage, cache, now):
    if not vintage_ok(vintage):
        return False
    return vintage == now.strftime("%Y%m%d") or os.path.isdir(os.path.join(cache, vintage))


class Fetcher(object):
    """One host, GET only. Opener, sleeper and clock are injectable so every rule is testable without a network. The contact string is held in memory only and is registered as a secret,
    so nothing that would write it gets written."""

    def __init__(self, cache, out_dir, vintage, contact, stop_dir=STOP_DIR, opener=real_opener, sleeper=time.sleep, now_utc=None, root=ROOT, cap=None, max_requests=None):
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
        self.vint_path = os.path.join(out_dir, "vintages.csv")
        self.vint_all = [list(r.values()) for r in vint_rows(out_dir)]
        self.vint = {r[2]: r for r in self.vint_all if r[0] == vintage}
        self.last_end = None
        if self.vint_all:
            try:
                self.last_end = parse_utc_ms(self.vint_all[-1][6])
            except ValueError:
                self.last_end = None
        if M("g16_fetch_log"):
            write_text(os.path.join(out_dir, "fetch_log.csv"), "x\n")

    def stop_path(self):
        return os.path.join(self.stop_dir, STOP_NAME)

    def check_stop(self):
        if os.path.exists(self.stop_path()) and not M("g15_stop_ignored"):
            raise Latched("STOP present: %s" % tilde(self.stop_path()))

    def limit(self):
        lim = [x for x in (self.cap, self.max_requests) if x is not None]
        return min(lim) if lim else None

    def _write_vint(self):
        write_text(self.vint_path, render_csv("vintages.csv", self.vint_all, "# source: US Securities and Exchange Commission, EDGAR XBRL API (companyconcept) on data.sec.gov; one row per request "
                                              "made by bin/collateral_reuse.py fetch-concepts, which is the only writer of this file"))

    def _pace(self):
        gap = 0.9 if M("g16_gap09") else MIN_GAP
        if self.last_end is not None:
            wait = gap - (self.now_utc() - self.last_end).total_seconds()
            if wait > 0:
                self.sleeper(wait)

    def _latch(self, status, path, retry_after, body, why):
        create_stop(self.stop_path(), stop_fields(status, utc_ms(self.now_utc()), path, retry_after or "", esc_head(body)))
        raise Latched("STOP written: %s (%s)" % (tilde(self.stop_path()), why))

    def _get(self, path):
        check_url("https://" + HOST + path)
        self.last_path = path
        self._pace()
        started = self.now_utc()
        self.requests += 1
        try:
            status, body, hdrs = self.opener(HOST, path, dict(self.headers), TIMEOUT, BODY_CAP)
        except SocketFault:
            ended = self.now_utc()
            self._record(path, "0", b"", started, ended)
            self.last_end = ended
            if M("g15_stop_on_timeout"):
                create_stop(self.stop_path(), stop_fields("timeout", utc_ms(ended), path, "", ""))
            raise
        ended = self.now_utc()
        self.last_end = ended
        return status, body, hdrs, started, ended

    def _record(self, path, status, body, started, ended):
        row = [self.vintage, HOST, path, str(status), str(len(body or b"")), sha256_of(body) if body else "", utc_ms(ended), "%.3f" % (ended - started).total_seconds()]
        self.vint_all = [r for r in self.vint_all if not (r[0] == self.vintage and r[2] == path)]
        self.vint_all.append(row)
        self.vint[path] = row
        self._write_vint()

    def obtain(self, path, expect):
        """The body for a path: ('cached', body) when raw/ already holds it with its vintages.csv digest (no request), ('200', body) after a request, ('404', None) for a path with no facts.
        Everything else latches STOP. A body in raw/ that differs from its row is refused, never fetched over."""
        rn = raw_name(path)
        row = self.vint.get(path)
        if row is not None and not M("g16_recache"):
            if row[3] == "404":
                return "404", None
            p = os.path.join(self.raw, rn)
            if row[3] == "200" and os.path.isfile(p):
                b = read_file(p, "rb")
                if sha256_of(b) == row[5] and str(len(b)) == row[4]:
                    return "cached", b
                raise Refused("the cached body of %s does not match its vintages.csv row; nothing is fetched over it" % rn)
        self.check_stop()
        lim = self.limit()
        if lim is not None and self.requests >= lim and not M("g16_cap_off"):
            raise SliceEnd("the cap of %d requests is reached" % lim)
        status, body, hdrs, started, ended = self._get(path)
        if status in (429, 500) and M("g16_retry"):
            self._record(path, status, body, started, ended)
            status, body, hdrs, started, ended = self._get(path)
        if status == 404 and not M("g15_404_latches"):
            self._record(path, 404, body, started, ended)
            return "404", None
        if status in (403, 429) and M("g15_403_ignored"):
            self._record(path, status, body, started, ended)
            return "404", None
        if status != 200:
            self._record(path, status, body, started, ended)
            if status // 100 == 3 and M("g15_3xx_ignored"):
                return "404", None
            if status // 100 == 3 and M("g16_redirect"):
                status, body, hdrs, started, ended = self._get(urlsplit(hdrs.get("location", path)).path or path)
            else:
                self._latch(status, path, hdrs.get("retry-after", ""), body, "HTTP %s" % status)
        if body is None:
            self._record(path, status, b"", started, ended)
            self._latch(status, path, "", b"", "body larger than the cap")
        prob = body_check(body, expect)
        if prob:
            self._record(path, status, body, started, ended)
            self._latch(status, path, "", body, "content test: %s" % prob)
        write_bytes(os.path.join(self.raw, rn), body)
        self._record(path, 200, body, started, ended)
        return "200", body


def mode_concepts(fe, say):
    """The eight requests: the two tags for JPM, GS, State Street and Wells Fargo (a 404 on a Wells Fargo tag is expected if absent)."""
    for cik, ticker, _ in BANK_TABLE:
        for tag, _ in TAGS:
            st, _ = fe.obtain(concept_path(cik, tag), (cik, tag))
            say("%s %s: %s" % (ticker, tag, "absent (404)" if st == "404" else ("kept" if st == "200" else "already kept")))


def run_fetch(a, environ=None, opener=real_opener, sleeper=time.sleep, now_utc=None, say=print, stop_dir=STOP_DIR):
    """Returns the exit code: 0 done, 2 STOP present or written (or no contact string), 3 network fault, 4 the cap or --max-requests reached with work left, 5 refused."""
    environ = os.environ if environ is None else environ
    contact = (environ.get("SEC_UA") or "").strip()
    if not contact and M("g16_no_ua_ok"):
        contact = "anonymous"                                    # the mutant: a fetch that runs without a declared contact
    if not contact:
        say("SEC_UA is not set: the fetch refuses to run (set it to the declared contact; its value is never printed or written)")
        return 2
    now = (now_utc or (lambda: dt.datetime.now(dt.timezone.utc)))()
    cache = check_cache(a.cache, out_dir=a.out)
    if not fetch_vintage_ok(a.vintage, cache, now):
        raise Refused("--vintage must be today's UTC date (%s) or an existing vintage folder" % now.strftime("%Y%m%d"))
    fe = Fetcher(cache, a.out, a.vintage, contact, stop_dir=stop_dir, opener=opener, sleeper=sleeper, now_utc=now_utc, cap=FETCH_CAP, max_requests=a.max_requests)
    try:
        fe.check_stop()
        os.makedirs(a.out, exist_ok=True)
        mode_concepts(fe, say)
        say("fetch-concepts: done; requests sent in this invocation: %d" % fe.requests)
        return 0
    except Latched as e:
        say(str(e))
        return 2
    except SliceEnd as e:
        say("fetch-concepts: %s; run it again to resume (a body already kept is not requested again); requests sent: %d" % (e, fe.requests))
        return 4
    except SocketFault:
        say("FAIL network %s: the run ends; nothing was latched and nothing is retried" % getattr(fe, "last_path", ""))
        return 3


# ------------------------------------------------------------------------------------------------------------------------
# folder-level guards (6, G18): the same rules the build applies when it writes, and that M28 applies a second time
# ------------------------------------------------------------------------------------------------------------------------
def leak_problems(files, full=True):
    """Section 6: only the committed names; no json, xml, zip, html or STOP file; no local path; no at sign; not a byte of the contact string."""
    out = []
    for n in sorted(files):
        raw = files[n] if isinstance(files[n], bytes) else files[n].encode("utf-8")
        text = raw.decode("utf-8", errors="replace")
        low = n.lower()
        rawfile = low.endswith((".zip", ".html", ".htm", ".gz", ".pdf")) or raw[:2] == b"PK" or raw[:4] == b"%PDF" or n.upper().startswith("STOP")
        if low.endswith(".json") and not M("g18_json_ok"):
            rawfile = True
        if low.endswith(".xml") and not M("g18_xml_ok"):
            rawfile = True
        if rawfile:
            out.append("raw or forbidden file in the committed folder: %s" % n)
            continue
        if n not in COMMITTED and n != ".DS_Store" and not M("g18_thirteenth_ok") and not (M("g18_json_ok") and low.endswith(".json")) and not (M("g18_xml_ok") and low.endswith(".xml")):
            out.append("file that is not one of the committed names: %s" % n)
        if not M("g18_path_ok") and any(p in text for p in ("/Users/", "/private/", "~/")):
            out.append("a local path in %s" % n)
        if not M("g18_at_ok") and "@" in text:
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
            if k in seen and not M("g18_dup_ok"):
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


def folder_problems(files, full=True):
    out = leak_problems(files, full) + header_problems(files) + dup_key_problems(files) + value_problems(files) + verdict_problems(files) + c05_problems(files) + c08_problems(files)
    for n in ("README.md", "SOURCES.md"):
        if n in files and isinstance(files[n], str):
            out += ["%s: %s" % (n, p) for p in sorted(set(wording_problems(n, files[n])))]
    return out


def checksh_region(text):
    a = text.find("cru_leak_check() {")
    return text[a:text.find("\n}\n", a) + 3] if a >= 0 else ""


def checksh_problems(text):
    """G18: the M28 guard in bin/check.sh holds its own literal copy of the thirteen canonical header lines and of the 4.6 hash, and never reads them from this script."""
    if M("g18_checksh_lax"):
        return []
    region = checksh_region(text)
    if not region:
        return ["bin/check.sh has no cru_leak_check function"]
    out = []
    for l in SPEC_ALLOW_TEXT.splitlines():
        name, hdr = l.split(":", 1)
        if ("%s) want='%s'" % (name, hdr)) not in region:
            out.append("check.sh does not hold the literal header of %s" % name)
    if SPEC_PREREG_SHA256 not in region:
        out.append("check.sh does not hold the literal 4.6 hash")
    if re.search(r"collateral_reuse\.py", region):
        out.append("check.sh names the script inside the guard (it must not read the headers from it)")
    return out


def write_outputs(todo, out_dir):
    """The writer of the committed tables. Regenerates every file in full (revisions.csv is never appended to, G4); the mutant keeps the old rows and adds the new ones."""
    for n, x in todo.items():
        p = os.path.join(out_dir, n)
        if n == "revisions.csv" and M("g4_revisions_append") and os.path.isfile(p):
            x = read_file(p, "r") + "".join(l + "\n" for l in x.splitlines()[2:])
        write_text(p, x)


# ------------------------------------------------------------------------------------------------------------------------
# the command line
# ------------------------------------------------------------------------------------------------------------------------
def make_parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch-concepts", help="the eight companyconcept requests (network; SEC_UA required; supervisor only)")
    pf.add_argument("--vintage", required=True, help="YYYYMMDD: today's UTC date, or an existing vintage folder to resume")
    pf.add_argument("--max-requests", type=int, default=None, help="end the run after this many requests (a slice); run again to resume")
    pf.add_argument("--cache", default=CACHE_DEFAULT)
    pf.add_argument("--out", default=OUT_DEFAULT)
    pb = sub.add_parser("build", help="offline: validate the cache and write the outputs of one stage")
    pb.add_argument("--vintage", required=True)
    pb.add_argument("--stage", required=not M("g17_full_default"), default="full" if M("g17_full_default") else None, choices=("pre", "dry", "full"))
    pb.add_argument("--cache", default=CACHE_DEFAULT)
    pb.add_argument("--out", default=OUT_DEFAULT)
    pb.add_argument("--committed", default=None, help="dry stage only: the committed folder to read vintages.csv and registered.csv from (default: data/collateral_reuse)")
    pb.add_argument("--pins", default=None, help="captions_pin.csv, if not the committed one (tests)")
    pb.add_argument("--readme-only", action="store_true", help="full stage only: re-render README.md and SOURCES.md from the registered rows and the cache; writes nothing else")
    pb.add_argument("--supersede", action="store_true", help="P19: mark the registered rows superseded and add the corrected ones with the next version")
    ps = sub.add_parser("selftest", help="synthetic data, mutants applied one at a time; no network")
    ps.add_argument("--no-mutants", action="store_true")
    ps.add_argument("--mutant", help="run every guard with this one mutant switched on; exit 1 (the selftest fails) when it is caught")
    return ap


def main(argv=None):
    a = make_parser().parse_args(argv)
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


# ==============================================================================================================================
# SELFTEST: synthetic data only. Every guard applies its own mutants one at a time; an uncaught mutant fails the selftest.
# ==============================================================================================================================
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

    def failed(self):
        return [(n, d) for n, c, d in self.items if not c]


class FakeClock(object):
    """A clock that only moves when the code sleeps (so the pacing of the fetcher is testable)."""

    def __init__(self, t=1_793_523_200.0):                       # 2026-11-01 08:53:20 UTC
        self.t = t

    def sleep(self, s):
        self.t += s

    def now_utc(self):
        return dt.datetime.fromtimestamp(self.t, dt.timezone.utc)


FIXTURE_CONTACT = "Fixture Research Contact 7Q2X-91 (selftest)"        # a made-up contact string with no address; the tests look for it in every byte written
NAMES = {JPM: "JPMORGAN CHASE & CO", GS: "GOLDMAN SACHS GROUP INC", STT: "STATE STREET CORP", WFC: "WELLS FARGO & COMPANY"}


@contextlib.contextmanager
def patched(**kw):
    """Temporarily rebind module constants."""
    g = globals()
    old = {k: g[k] for k in kw}
    g.update(kw)
    try:
        yield
    finally:
        g.update(old)


def add_days(s, n):
    return (parse_date(s) + dt.timedelta(days=n)).isoformat()


# ---- the synthetic world: four banks, quarterly, with the traps of 2.3 built in (comparatives in later filings; 2009-12-31 comparative-only; 2010-03-31 absent) ----
I0 = qi("2009-12-31")
SHARE = {JPM: lambda k: Decimal(70) + Decimal(k) / 10 + Decimal(k % 4) / 20, GS: lambda k: Decimal(75) + Decimal(k) / 20 - Decimal(k % 3) / 25,
         STT: lambda k: Decimal(40) + Decimal(k % 7) / 2, WFC: lambda k: Decimal(60) + Decimal(k % 5)}
DENOM = {JPM: lambda k: 10 ** 12 + 2 * 10 ** 9 * k, GS: lambda k: 6 * 10 ** 11 + 15 * 10 ** 8 * k, STT: lambda k: 2 * 10 ** 10 + 10 ** 8 * k, WFC: lambda k: 5 * 10 ** 11 + 10 ** 9 * k}
SPAN = {JPM: (qi("2010-06-30"), qi("2026-06-30")), GS: (qi("2010-06-30"), qi("2026-06-30")), STT: (qi("2014-03-31"), qi("2026-09-30")), WFC: (qi("2013-12-31"), qi("2026-06-30"))}


def nd_of(cik, i):
    k = i - I0
    d = DENOM[cik](k)
    return int(Decimal(d) * SHARE[cik](k) / 100), d


def mfact(end, accn, form, filed, fy, fp, val):
    return dict(end=end, accn=accn, form=form, filed=filed, fy=str(fy), fp=fp, val=Decimal(val))


def filing_of(cik, i):
    e = qd(i)
    y, m = int(e[:4]), int(e[5:7])
    form, fp, lag = ("10-K", "FY", 55) if m == 12 else ("10-Q", "Q%d" % (m // 3), 40)
    return "%s-%02d-%06d" % (cik, y % 100, i), form, fp, y, add_days(e, lag)


def world_facts(cik, tag, drop=(), tweak=None, extra=()):
    lo, hi = SPAN[cik]
    first_comp = I0 if cik in PRIMARY else (qi("2013-12-31") if cik == STT else lo)      # State Street's 2013-12-31 exists only as a comparative (supervisor decision)
    out = []
    for i in range(lo, hi + 1):
        e = qd(i)
        if e in drop:
            continue
        accn, form, fp, fy, filed = filing_of(cik, i)
        v = nd_of(cik, i)[0 if tag == "N" else 1]
        if tweak and (cik, tag, e) in tweak:
            v = tweak[(cik, tag, e)]
        out.append(mfact(e, accn, form, filed, fy, fp, v))
        pd = (fy - 1) * 4 + 3
        if pd >= first_comp and pd != i:
            out.append(mfact(qd(pd), accn, form, filed, fy, fp, nd_of(cik, pd)[0 if tag == "N" else 1]))
    out += list(extra.get((cik, tag), ())) if isinstance(extra, dict) else list(extra)
    return out


def make_banks(drop=None, tweak=None, extra=None, ciks=(JPM, GS, STT, WFC), absent=()):
    banks = []
    for cik, ticker, role in BANK_TABLE:
        if cik not in ciks:
            continue
        conc = {}
        for t, _ in TAGS:
            if cik in absent:
                conc[t] = None
            else:
                conc[t] = Concept(world_facts(cik, t, (drop or {}).get(cik, ()), tweak, extra or {}))
        banks.append(Bank(cik, ticker, role, conc["N"], conc["D"], title_name(NAMES[cik])))
    return banks


_PIN_CACHE = {}


def real_pins():
    """The committed captions_pin.csv, read once (an input; the selftest never writes it)."""
    if "p" not in _PIN_CACHE:
        _PIN_CACHE["p"] = load_pins(OUT_DEFAULT)
    return _PIN_CACHE["p"]


def fresh_ctx(stage="full", banks=None, vintage="20261101"):
    return compute(banks if banks is not None else make_banks(), stage, vintage, real_pins()[1])


def okrow(cik, end, n, d, flags=(), status="ok", basis="own_filing"):
    return dict(cik10=cik, ticker=TICKER[cik], end=end, basis=basis, accession="A", form="10-Q", filing_date="x", n=Decimal(n), d=Decimal(d), share=Decimal(100) * Decimal(n) / Decimal(d),
                flags=set(flags), status=status)


def ref_share(ciks, i):
    n = sum(nd_of(c, i)[0] for c in ciks)
    d = sum(nd_of(c, i)[1] for c in ciks)
    return Decimal(100) * n / d


def pair(end, accn, nv=1_200_000_000_000, dv=1_500_000_000_000, form="10-Q", filed=None, fy=None, fp=None):
    d = parse_date(end)
    fp = fp or {3: "Q1", 6: "Q2", 9: "Q3", 12: "FY"}.get(d.month, "Q2")
    fy = str(fy if fy is not None else d.year)
    filed = filed or add_days(end, 40)
    return mfact(end, accn, form, filed, fy, fp, nv), mfact(end, accn, form, filed, fy, fp, dv)


def micro(pairs_n, pairs_d=None, cik=JPM):
    n = [p[0] if isinstance(p, tuple) else p for p in pairs_n]
    d = [p[1] if isinstance(p, tuple) else p for p in (pairs_d if pairs_d is not None else pairs_n)]
    return Bank(cik, TICKER[cik], "primary", Concept(n), Concept(d), "X")


def status_of(bank, end, basis="own_filing", stage="full"):
    r = (own_row if basis == "own_filing" else latest_row)(bank, end, stage)
    return r["status"], r


# ---- fixtures for the statement tests ----
def sctx(series=None, ymem=None, yrmem=None, ylmem=None, recast=(), pins=None, dec=None):
    s = {qi(S3_START): Decimal(70), qi(S3_END): Decimal("71.5"), qi(S1_START): Decimal("71.5"), qi(S1_END): Decimal(73), qi(S2_DATE): Decimal("71.5")}
    if series:
        s.update(series)
    ymem = ymem if ymem is not None else [Decimal(x) / 4 - 1 for x in range(Y_EXP)]               # -1.00 .. 4.50
    yrmem = yrmem if yrmem is not None else ymem[-YR_EXP:]
    ylmem = ylmem if ylmem is not None else [Decimal(68) + Decimal(x) / 4 for x in range(YL_NOM)]
    return dict(series=s, y=dict(members=[(1000 + i, v) for i, v in enumerate(ymem)], yr=[(1000 + i, v) for i, v in enumerate(yrmem)]), yl=dict(members=[(2000 + i, v) for i, v in enumerate(ylmem)]),
                pins=pins if pins is not None else pin_map(real_pins()[1]), recast_at=lambda e, r=tuple(recast): e in r, decompose=lambda a, b: dec)


# ==============================================================================================================================
# the guards
# ==============================================================================================================================
def t_g1(ck):
    big, frac = 9007199254740993, "1234567890123.45"
    raw = ('{"cik":19617,"entityName":"X","units":{"USD":[{"end":"2020-12-31","val":%d,"accn":"a","fy":2020,"fp":"FY","form":"10-K","filed":"2021-02-20"},'
           '{"end":"2020-09-30","val":%s,"accn":"b","fy":2020,"fp":"Q3","form":"10-Q","filed":"2020-11-02"}]}}' % (big, frac)).encode()
    facts = parse_concept(raw, "full")[0]
    ck.eq("a value above 2^53 is read exactly", facts[0]["val"], Decimal(big))
    ck.eq("a fractional value is read exactly", facts[1]["val"], Decimal(frac))
    ck.eq("a sum is exact (ten tenths)", dsum([Decimal("0.1")] * 10), Decimal("1.0"))
    ck.eq("a fact without a val is absent, not zero", parse_concept(b'{"cik":1,"units":{"USD":[{"end":"2020-12-31","accn":"a","fy":2020,"fp":"FY","form":"10-K","filed":"2021-02-20"}]}}')[0], [])
    d_only = Bank(JPM, "JPM", "primary", Concept([]), Concept([pair("2012-06-30", "A1")[1]]), "X")
    ck.eq("...so the quarter is missing, never a zero", status_of(d_only, "2012-06-30")[0], "missing_n")
    for label, units in (("a USDm unit key", '{"USDm":[]}'), ("two unit keys", '{"USD":[],"shares":[]}'), ("no unit key", "{}")):
        ck.raises("%s is refused" % label, DataError, lambda u=units: parse_concept(('{"cik":1,"units":%s}' % u).encode()))
    rows = {JPM: {"own_filing": {"2012-06-30": okrow(JPM, "2012-06-30", 80, 100)}}, GS: {"own_filing": {"2012-06-30": okrow(GS, "2012-06-30", 10, 200)}}}
    ck.eq("S = sum N / sum D, not a mean of ratios", sample_points(rows, "primary", "own_filing")[qi("2012-06-30")]["share"], Decimal(30))
    ck.eq("...while sens_eqw is the mean of the ratios", sample_points(rows, "sens_eqw", "own_filing")[qi("2012-06-30")]["share"], Decimal("42.5"))


def t_g2(ck):
    for e in ("2009-03-27", "2008-12-26", "2010-03-30", "2010-04-01", "2010-06-29", "bad"):
        ck.ok("%s is not a calendar quarter-end" % e, not is_cal(e), "")
    for e in ("2010-03-31", "2010-06-30", "2010-09-30", "2010-12-31", "2016-12-31"):
        ck.ok("%s is a calendar quarter-end" % e, is_cal(e), "")
    offs = ("2009-03-27", "2008-12-26", "2010-03-30", "2010-04-01")
    b = micro([pair(e, "OFF" + e) for e in offs] + [pair("2010-06-30", "A1")])
    ctx = dict(banks=[b])
    row = rows_banks(ctx)[0]
    ck.eq("n_off_calendar counts the four off-calendar ends", (row[5], row[6], row[7]), ("5", "1", "4"))
    qr = bank_rows(b, "full")["own_filing"]
    ck.eq("each off-calendar end has status off_calendar and no value", sorted((e, r["status"], r["n"]) for e, r in qr.items() if e in offs), [(e, "off_calendar", None) for e in sorted(offs)])
    ck.eq("an off-calendar end is not moved to a quarter-end", [e for e in qr if is_cal(e)], ["2010-06-30"])
    ck.eq("...and the calendar quarter-end next to it is ok on its own filing", qr["2010-06-30"]["status"], "ok")
    ctx = fresh_ctx("pre")
    r = ctx["rows"][JPM]["own_filing"]
    ck.eq("2010-03-31 is absent in the world: missing_n, never filled", (r["2010-03-31"]["status"], r["2010-03-31"]["n"]), ("missing_n", None))
    ck.eq("2009-12-31 is comparative-only: own_filing_lacks_tags", r["2009-12-31"]["status"], "own_filing_lacks_tags")
    ck.eq("the first ok quarter is 2010-06-30", [e for e in sorted(r) if r[e]["status"] == "ok"][0], "2010-06-30")


def t_g3(ck):
    A = lambda *a, **k: pair("2012-06-30", *a, **k)
    n, d = A("A1")
    ck.eq("a single original filing is the own filing", (status_of(micro([A("A1")]), "2012-06-30")[0], status_of(micro([A("A1")]), "2012-06-30")[1]["accession"]), ("ok", "A1"))
    late = A("A2", filed="2013-08-09", fy=2012, fp="Q2")
    ck.eq("a late-filed repeat of the period (a comparative column) cannot replace the original", status_of(micro([A("A1"), late]), "2012-06-30")[1]["accession"], "A1")
    n3, d3 = pair("2012-06-30", "A3")
    n3b, d3b = pair("2012-09-30", "A3", fy=2012, fp="Q3")
    ck.eq("an end that is not the latest end of its accession cannot define the value", status_of(micro([A("A1"), (n3, d3), (n3b, d3b)]), "2012-06-30")[1]["accession"], "A1")
    amend = [pair("2012-06-30", "AM", form="10-K/A"), pair("2012-06-30", "AN", form="10-Q/A")]
    ck.eq("a 10-K/A or 10-Q/A never defines the primary value", status_of(micro(amend), "2012-06-30")[0], "own_filing_lacks_tags")
    nn, dd = A("A1")[0], A("A2", filed=add_days("2012-06-30", 20))[1]
    ck.eq("numerator and denominator from two accessions: not ok", status_of(micro([nn], [dd]), "2012-06-30")[0], "own_filing_lacks_tags")
    ck.eq("a filing 100 days after the end is accepted", status_of(micro([A("A1", filed=add_days("2012-06-30", 100))]), "2012-06-30")[0], "ok")
    ck.eq("...and 101 days after is refused", status_of(micro([A("A1", filed=add_days("2012-06-30", 101))]), "2012-06-30")[0], "own_filing_lacks_tags")
    ck.eq("...a filing before the end is refused", status_of(micro([A("A1", filed=add_days("2012-06-30", -1))]), "2012-06-30")[0], "own_filing_lacks_tags")
    ck.eq("fy and fp that imply a different end are refused", status_of(micro([A("A1", fy=2013, fp="Q2")]), "2012-06-30")[0], "own_filing_lacks_tags")
    q4 = pair("2012-12-31", "A5", form="10-K", fp="Q4")
    ck.eq("fp = Q4 on a 10-K is 31 December", status_of(micro([q4]), "2012-12-31")[0], "ok")
    fy = pair("2012-12-31", "A5", form="10-K", fp="FY")
    ck.eq("fp = FY on a 10-K is 31 December", status_of(micro([fy]), "2012-12-31")[0], "ok")
    ck.eq("two qualifying accessions: ambiguous", status_of(micro([A("A1"), A("A6", filed=add_days("2012-06-30", 60))]), "2012-06-30")[0], "ambiguous")
    late_d = pair("2012-06-30", "A7", fy=2013, fp="Q2", filed=add_days("2012-06-30", 300))[1]
    ck.eq("a missing denominator is not filled from a later filing", status_of(micro([A("A1")[0]], [late_d]), "2012-06-30")[0], "own_filing_lacks_tags")
    both = pair("2012-06-30", "A7", fy=2013, fp="Q2", filed=add_days("2012-06-30", 300))
    ck.eq("sens_latest takes both legs from the one latest accession", (status_of(micro([A("A1"), both]), "2012-06-30", "latest_filed")[0], status_of(micro([A("A1"), both]), "2012-06-30", "latest_filed")[1]["accession"]), ("ok", "A7"))
    ck.eq("...and a latest accession that lacks a leg gives no latest value", status_of(micro([A("A1")[0], both[0]], [A("A1")[1]]), "2012-06-30", "latest_filed")[0], "own_filing_lacks_tags")


def t_g4(ck):
    A1 = pair("2012-06-30", "A1")
    A2 = pair("2012-06-30", "A2", nv=1_300_000_000_000, fy=2013, fp="FY", form="10-K", filed=add_days("2012-06-30", 400))
    b = micro([A1, A2])
    s1, r1 = status_of(b, "2012-06-30", "own_filing")
    s2, r2 = status_of(b, "2012-06-30", "latest_filed")
    ck.eq("the primary value is the first-reported one", (r1["accession"], r1["n"]), ("A1", Decimal(1_200_000_000_000)))
    ck.eq("sens_latest takes the latest filed value", (r2["accession"], r2["n"]), ("A2", Decimal(1_300_000_000_000)))
    t1, t2 = pair("2012-06-30", "B8", filed="2012-09-01"), pair("2012-06-30", "B9", filed="2012-09-01")
    ck.eq("a tie on the filing date goes to the largest accn", status_of(micro([t1, t2]), "2012-06-30", "latest_filed")[1]["accession"], "B9")
    first = (Decimal(1_000_000_000_000), "A1")
    ck.ok("a difference of exactly 1.0000% is not flagged", not is_recast(rel_change(first, (Decimal(1_010_000_000_000), "A2"))), "")
    ck.ok("a difference of 1.0001% is flagged", is_recast(rel_change(first, (Decimal(1_010_100_000_000), "A2"))), "")
    ck.ok("a difference of -1.0001% is flagged", is_recast(rel_change(first, (Decimal(989_900_000_000), "A2"))), "")
    rv = rows_revisions(dict(banks=[b]))
    ck.eq("revisions.csv lists the first and the latest value and the flag", [(r[3], r[4], r[5], r[6], r[9]) for r in rv if r[3] == "N"], [("N", "1200000000000", "1300000000000", "8.333", "recast")])
    ck.ok("the recast flag lands on the bank-quarter", "recast" in bank_rows(b, "full")["own_filing"]["2012-06-30"]["flags"], "")
    with tempfile.TemporaryDirectory(prefix="cru_g4_", ignore_cleanup_errors=True) as tmp:
        todo = {"revisions.csv": render_csv("revisions.csv", rv, "# source: test")}
        write_outputs(todo, tmp)
        first_bytes = read_file(os.path.join(tmp, "revisions.csv"))
        write_outputs(todo, tmp)
        ck.ok("revisions.csv is regenerated, not appended to", read_file(os.path.join(tmp, "revisions.csv")) == first_bytes, "")


def t_g5(ck):
    ck.raises("a fact with an extra key is refused", DataError, lambda: parse_concept(b'{"cik":1,"units":{"USD":[{"end":"2020-12-31","val":1,"accn":"a","fy":2020,"fp":"FY","form":"10-K","filed":"x","dim":"Seg"}]}}'))
    two = [mfact("2012-06-30", "A1", "10-Q", "2012-08-09", 2012, "Q2", 1_200_000_000_000), mfact("2012-06-30", "A1", "10-Q", "2012-08-09", 2012, "Q2", 1_199_999_999_999)]
    b = Bank(JPM, "JPM", "primary", Concept(two), Concept([pair("2012-06-30", "A1")[1]]), "X")
    ck.eq("two different values for one accn, tag and end: conflict", status_of(b, "2012-06-30")[0], "conflict")
    same = [two[0], dict(two[0])]
    b2 = Bank(JPM, "JPM", "primary", Concept(same), Concept([pair("2012-06-30", "A1")[1]]), "X")
    ck.eq("identical repeats are one fact", status_of(b2, "2012-06-30")[0], "ok")
    pv = Decimal(1_000_000_000_000)
    ck.ok("a q/q move of 30.0000% is not flagged", not is_jump(Decimal(1_300_000_000_000), pv), "")
    ck.ok("a q/q move of 30.0001% is flagged", is_jump(Decimal(1_300_100_000_000), pv), "")
    ck.ok("a q/q fall of 30.0001% is flagged", is_jump(Decimal(699_900_000_000), pv), "")
    D = 1_500_000_000_000
    ck.eq("N = D is accepted", status_of(micro([pair("2012-06-30", "A1", nv=D, dv=D)]), "2012-06-30")[0], "ok")
    ck.eq("N = D + 1 USD is excluded as ratio_gt_1", status_of(micro([pair("2012-06-30", "A1", nv=D + 1, dv=D)]), "2012-06-30")[0], "ratio_gt_1")
    rows = {JPM: {"own_filing": {"2012-06-30": okrow(JPM, "2012-06-30", 90, 100), "2012-09-30": okrow(JPM, "2012-09-30", 110, 100, status="ratio_gt_1")}},
            GS: {"own_filing": {"2012-06-30": okrow(GS, "2012-06-30", 90, 100), "2012-09-30": okrow(GS, "2012-09-30", 90, 100)}}}
    pts = sample_points(rows, "primary", "own_filing")
    ck.eq("a ratio_gt_1 bank-quarter keeps the quarter out of every sample", sorted(pts), [qi("2012-06-30")])
    rows2 = {JPM: {"own_filing": {"2012-06-30": okrow(JPM, "2012-06-30", 90, 100, flags=("jump", "recast", "amended"))}}, GS: {"own_filing": {"2012-06-30": okrow(GS, "2012-06-30", 90, 100)}}}
    ck.eq("a flagged quarter stays in the primary sample", sorted(sample_points(rows2, "primary", "own_filing")), [qi("2012-06-30")])
    ck.eq("...and sens_noflag removes a recast or jump quarter (not an amended one)", (sorted(sample_points(rows2, "sens_noflag", "own_filing")),
          sorted(sample_points({JPM: {"own_filing": {"2012-06-30": okrow(JPM, "2012-06-30", 90, 100, flags=("amended",))}}, GS: rows2[GS]}, "sens_noflag", "own_filing"))), ([], [qi("2012-06-30")]))
    sc = sctx()
    sc["series"].pop(qi(S3_END))
    ck.eq("an excluded endpoint voids its statement (endpoint_undefined)", statement("S3", sc)["void"], "endpoint_undefined")


def t_g6(ck):
    for v, want in ((999_999_999, False), (10 ** 9, True), (10 ** 13, True), (10 ** 13 + 1, False), (5 * 10 ** 11, True), (10 ** 8, False)):
        ck.eq("val %s is %s" % (v, "accepted" if want else "unit_odd"), in_bounds(Decimal(v)), want)
    ck.eq("a quarter with val 999,999,999 is unit_odd", status_of(micro([pair("2012-06-30", "A1", nv=999_999_999, dv=1_500_000_000_000)]), "2012-06-30")[0], "unit_odd")
    ck.eq("a quarter with val 1e13 + 1 on the denominator is unit_odd", status_of(micro([pair("2012-06-30", "A1", nv=1_200_000_000_000, dv=10 ** 13 + 1)]), "2012-06-30")[0], "unit_odd")
    ck.eq("a quarter at both edges is ok", status_of(micro([pair("2012-06-30", "A1", nv=10 ** 9, dv=10 ** 13)]), "2012-06-30")[0], "ok")
    ck.raises("a USDm unit key is refused", DataError, lambda: parse_concept(b'{"cik":1,"units":{"USDm":[{"end":"2020-12-31","val":1,"accn":"a","fy":2020,"fp":"FY","form":"10-K","filed":"x"}]}}'))
    ck.raises("a bank with two unit keys is refused", DataError, lambda: parse_concept(b'{"cik":1,"units":{"USD":[],"USDm":[]}}'))


def rows_dropping(rows, cik, end, status="missing_n"):
    out = {c: {b: dict(rs) for b, rs in v.items()} for c, v in rows.items()}
    r = dict(out[cik]["own_filing"][end])
    r.update(status=status, n=None, d=None, share=None)
    out[cik]["own_filing"][end] = r
    return out


def t_g7(ck):
    ctx = fresh_ctx("full")
    rows = ctx["rows"]
    gap = rows_dropping(rows, JPM, "2016-06-30")
    i = qi("2016-06-30")
    ck.ok("primary: a date one bank lacks is undefined (not a sum over the other)", i not in sample_points(gap, "primary", "own_filing"), "")
    ck.ok("sens_stt: a date JPM lacks is undefined", i not in sample_points(gap, "sens_stt", "own_filing"), "")
    ck.ok("sens_gs: Goldman alone still has the date", i in sample_points(gap, "sens_gs", "own_filing"), "")
    ck.ok("...and the neighbours are untouched", all(j in sample_points(gap, "primary", "own_filing") for j in (i - 1, i + 1)), "")
    stt = sample_points(rows, "sens_stt", "own_filing")
    ck.eq("sens_stt starts at 2014-03-31, the first date all three banks have in own filing (P8)", (min(stt), qd(min(stt))), (qi("2014-03-31"), "2014-03-31"))
    ck.ok("sens_stt never has a date before 2014-03-31 (2013-12-31 is comparative-only at State Street)", all(j >= qi("2014-03-31") for j in stt), "")
    prim = sample_points(rows, "primary", "own_filing")
    ck.eq("primary equals the reference sum N / sum D at every date", all(prim[j]["share"] == ref_share(PRIMARY, j) for j in prim) and len(prim) == 65, True)
    ck.eq("the missing quarter 2010-03-31 is not in the sample", qi("2010-03-31") in prim, False)


def full_series(lo="2009-03-31", hi="2026-06-30"):
    return {i: Decimal(50) + Decimal((i * 7) % 11) / 10 + Decimal(i - qi(lo)) / 20 for i in range(qi(lo), qi(hi) + 1)}


def t_g8(ck):
    ctx = fresh_ctx("full")
    y, yl = ctx["y"], ctx["yl"]
    ck.eq("Y on the synthetic world: 33 nominal, 31 defined, 23 members", (y["nominal"], len(y["defined"]), len(y["members"])), (33, 31, 23))
    ck.eq("YR: 25 nominal, 17 members", (y["nominal_yr"], len(y["yr"])), (25, 17))
    ck.eq("YL: 12 nominal, 12 defined", (yl["nominal"], len(yl["members"])), (12, 12))
    full = full_series()
    yf = yardstick(full, [qi(CAP_FIRST)])
    ends = [qd(q) for q, _ in yf["defined"]]
    ck.eq("on a full series Y spans exactly 2011-12-31 to 2019-12-31 (33 windows)", (ends[0], ends[-1], len(ends)), ("2011-12-31", "2019-12-31", 33))
    ck.ok("2011-09-30 and 2020-03-31 are out; 2011-12-31 and 2019-12-31 are in", "2011-09-30" not in ends and "2020-03-31" not in ends and "2011-12-31" in ends and "2019-12-31" in ends, "")
    ck.eq("...with 8 windows spanning the caption change excluded: 25 members", len(yf["members"]), 25)
    ck.ok("no 2026 date enters Y", all(q <= qi(Y_LAST) for q, _ in yf["defined"]), "")
    lv = level_yardstick(full)
    lends = [qd(q) for q, _ in lv["members"]]
    ck.eq("YL spans exactly 2017-03-31 to 2019-12-31", (lends[0], lends[-1], len(lends)), ("2017-03-31", "2019-12-31", 12))
    ck.ok("2016-12-31 and 2020-03-31 are not in YL", "2016-12-31" not in lends and "2020-03-31" not in lends, "")
    ck.ok("no 2026 date enters YL", all(q <= qi(YL_LAST) for q, _ in lv["members"]), "")
    gapped = {i: v for i, v in full.items() if i != qi("2014-06-30")}
    ck.eq("q-8 is found by quarter index across a missing quarter", sorted({q - p for q, p in d8_pairs(gapped)}), [8])
    ck.ok("...so the window ending 2016-06-30 is not defined", all(q != qi("2016-06-30") for q, p in d8_pairs(gapped)), "")
    D = {q: v for q, v in yf["defined"]}
    ck.eq("D8 is S_q - S_(q-8)", D[qi("2013-12-31")], full[qi("2013-12-31")] - full[qi("2011-12-31")])


def t_g9(ck):
    vals = [Decimal(x) for x in (-1, 0, 1, 2)]
    hi, lo = max(vals), min(vals)
    e = Decimal("1e-9")
    ck.eq("stat = max is WITHIN_RANGE", range_label(hi, vals), "WITHIN_RANGE")
    ck.eq("stat = min is WITHIN_RANGE", range_label(lo, vals), "WITHIN_RANGE")
    ck.eq("max + 1e-9 is a rise outside the range", range_label(hi + e, vals), "RISE_OUTSIDE_RANGE")
    ck.eq("min - 1e-9 is a fall outside the range", range_label(lo - e, vals), "FALL_OUTSIDE_RANGE")
    ck.eq("labels use the unrounded value (2.0004 against a maximum of 2.0000)", range_label(Decimal("2.0004"), vals), "RISE_OUTSIDE_RANGE")
    ck.eq("a level above, inside and below", (level_label(Decimal(3), vals), level_label(Decimal(1), vals), level_label(Decimal(-2), vals)), ("LEVEL_ABOVE_RANGE", "LEVEL_WITHIN_RANGE", "LEVEL_BELOW_RANGE"))
    ck.eq("sign at +0.0999, +0.1000, -0.0999, -0.1000 points", [sign_of(Decimal(x)) for x in ("0.0999", "0.1000", "-0.0999", "-0.1000")], ["ZERO", "RISE", "ZERO", "FALL"])
    s = statement("S3", sctx(ymem=[Decimal(x) / 2 - 3 for x in range(Y_EXP)]))
    ck.eq("a WITHIN_RANGE change of +1.5 carries sign RISE, not ZERO", (s["label"], s["sign"], s["void"]), ("WITHIN_RANGE", "RISE", "none"))
    ck.eq("...with the stat, extremes and rank written", (s["stat"], s["dmin"], s["dmax"], s["rank_of"]), (Decimal("1.5"), Decimal(-3), Decimal(8), Y_EXP + 1))
    for n, void in ((19, "thin_yardstick"), (20, "none")):
        s = statement("S3", sctx(ymem=[Decimal(x) / 4 - 1 for x in range(n)], yrmem=[Decimal(x) / 4 - 1 for x in range(n)][-YR_EXP:]))
        ck.eq("n_Y = %d is %s" % (n, "VOID" if void != "none" else "not VOID"), s["void"], void)
    for n, void in ((13, "thin_yardstick"), (14, "none")):
        s = statement("S3", sctx(yrmem=[Decimal(x) / 4 - 1 for x in range(n)]))
        ck.eq("n_YR = %d is %s" % (n, "VOID" if void != "none" else "not VOID"), s["void"], void)
    for n, void in ((9, "thin_yardstick"), (10, "none")):
        s = statement("S2", sctx(ylmem=[Decimal(68) + Decimal(x) / 4 for x in range(n)]))
        ck.eq("n_YL = %d is %s" % (n, "VOID" if void != "none" else "not VOID"), s["void"], void)
    pins = dict(pin_map(real_pins()[1]))
    pins[(JPM, S3_END, "N")] = "JN1"
    s = statement("S3", sctx(recast=(S3_END,), pins=pins))
    ck.eq("a recast endpoint and a caption change: endpoint_recast, with no label", (s["void"], s["label"], s["sign"]), ("endpoint_recast", "VOID", ""))
    s = statement("S3", sctx(pins=pins))
    ck.eq("a caption class that differs at the endpoints: caption_change, with no label", (s["void"], s["label"]), ("caption_change", "VOID"))
    s = statement("S3", sctx(recast=(S3_START,)))
    ck.eq("a recast at the start endpoint voids S3", s["void"], "endpoint_recast")
    s = statement("S1", sctx(recast=(S2_DATE,)))
    ck.eq("...and at the shared 2023-12-31 endpoint voids S1 too", s["void"], "endpoint_recast")
    s = statement("S2", sctx(recast=(S2_DATE,)))
    ck.eq("S2 is not voided by a recast", (s["void"], s["label"]), ("none", "LEVEL_ABOVE_RANGE"))
    s = statement("S3", sctx(ymem=[Decimal(x) / 4 - 1 for x in range(19)], recast=(S3_END,)))
    ck.eq("thin_yardstick is reported before endpoint_recast", s["void"], "thin_yardstick")
    s = statement("S2", sctx(series={qi(S2_DATE): Decimal(90)}))
    ck.eq("S2 above the 2017-2019 range: LEVEL_ABOVE_RANGE with sign RISE", (s["label"], s["sign"], s["rank"]), ("LEVEL_ABOVE_RANGE", "RISE", 1))
    s = statement("S2", sctx(series={qi(S2_DATE): Decimal(60)}))
    ck.eq("S2 below the range: LEVEL_BELOW_RANGE with sign FALL", (s["label"], s["sign"]), ("LEVEL_BELOW_RANGE", "FALL"))


def t_g10(ck):
    ck.ok("the constants reproduce the 4.6 text", prereg_ok(), sha256_of(prereg_text().encode("utf-8")))
    ck.ok("the constants reproduce the 4.7 text", pop_ok(), sha256_of(pop_text().encode("utf-8")))
    ck.ok("the allowlist text reproduces the section 5 hash", allow_hash_ok(), sha256_of(allow_text().encode("utf-8")))
    ck.eq("4.6 is 9 lines and 3463 bytes; 4.7 is 19 lines and 3401 bytes; 5 is 13 lines and 1220 bytes",
          (len(prereg_text().splitlines()), len(prereg_text().encode()), len(pop_text().splitlines()), len(pop_text().encode()), len(allow_text().splitlines()), len(allow_text().encode())),
          (9, 3463, 19, 3401, 13, 1220))
    for name, val in (("SIGN_TH", Decimal("0.2")), ("Y_MIN", 19), ("YR_MIN", 13), ("YL_MIN", 9), ("Y_NOM", 34), ("S3_START", "2021-09-30"), ("CAP_FIRST", "2017-06-30"), ("MAX_DAYS", 101)):
        with patched(**{name: val}):
            ck.ok("editing %s changes the 4.6 or 4.7 hash" % name, not (prereg_ok() and pop_ok()), "")
    txt = read_file(os.path.join(ROOT, "bin", "check.sh"), "r")
    m = re.search(r"PREREG_SHA='([0-9a-f]{64})'", checksh_region(txt))
    ck.ok("prereg_sha256 written to registered.csv equals M28's literal copy", bool(m) and m.group(1) == prereg_sha_out(), "")
    ck.eq("SPEC_CAPTION_SHA256 is the hash of captions_pin.csv", sha256_of(real_pins()[0].encode("utf-8")), pin_sha_expected())
    ctx = fresh_ctx("full")
    ck.ok("no yardstick holds the statistic's own window (S3 ends 2023-12-31)", all(q <= qi(Y_LAST) for q, _ in ctx["y"]["defined"]), "")
    row = rows_registered_new(ctx)[0]
    ck.eq("a registered row carries the 4.6 and 4.7 hashes", (row[-2], row[-1]), (SPEC_PREREG_SHA256, SPEC_POP_SHA256))


def edit_bank(bank, fn):
    """A copy of a bank with the facts of both tags passed through fn (a list of facts -> a list of facts)."""
    return Bank(bank.cik, bank.ticker, bank.role, Concept(fn([dict(f) for f in bank.conc["N"].facts])), Concept(fn([dict(f) for f in bank.conc["D"].facts])), bank.name)


def count_failures(banks):
    """(C01, C02) results of counts_checks on a pre-stage context: {(check id, ticker): ok}."""
    ctx = compute(banks, "pre", "20261101", real_pins()[1])
    out = {}

    def add(cid, desc, exp, obs, ok, warn=False, info=False):
        key = (cid, desc.split()[0])
        out[key] = out.get(key, True) and ok

    counts_checks(ctx, add)
    return out


def t_g12(ck):
    base = make_banks(ciks=(JPM, GS, STT))
    r = count_failures(base)
    ck.ok("the synthetic world passes C01 and C02 for JPM, GS and State Street", all(r.values()), str({k: v for k, v in r.items() if not v}))
    jpm = base[0]
    stt = base[2]
    ck.eq("State Street: 52 period-ends, 51 in own filing, 2013-12-31 comparative-only", (len(stt.conc["N"].period_ends()), sum(1 for e in stt.conc["N"].period_ends() if stt.conc["N"].own_accns(e)), stt.conc["N"].own_accns("2013-12-31"), stt.conc["N"].has("2013-12-31")), (52, 51, [], True))
    stt_own = edit_bank(stt, lambda fs: fs + [mfact("2013-12-31", "STT-OWN-13", "10-K", "2014-02-20", 2013, "FY", 20_000_000_000)])
    r = count_failures(base[:2] + [stt_own])
    ck.eq("State Street's 2013-12-31 in its own filing fails C02 (and C01: 52 with 52 in own filing)", (r[("C02", "STT")], r[("C01", "STT")]), (False, False))
    stt_no = edit_bank(stt, lambda fs: [f for f in fs if f["end"] != "2013-12-31"])
    r = count_failures(base[:2] + [stt_no])
    ck.eq("State Street without the 2013-12-31 comparative fails C02 and C01", (r[("C02", "STT")], r[("C01", "STT")]), (False, False))

    no2009 = edit_bank(jpm, lambda fs: [f for f in fs if f["end"] != "2009-12-31"])
    r = count_failures([no2009] + base[1:])
    ck.eq("65 period-ends fail C01 (66 are pinned)", r[("C01", "JPM")], False)
    ck.eq("...and C02 fails too: 2009-12-31 must be present as a comparative", r[("C02", "JPM")], False)
    sixty7 = edit_bank(jpm, lambda fs: fs + [mfact("2010-03-31", "LATE-1", "10-Q", "2011-08-01", 2011, "Q1", 1_000_000_000_000)])
    r = count_failures([sixty7] + base[1:])
    ck.eq("67 period-ends fail C01", r[("C01", "JPM")], False)
    ck.eq("2010-03-31 present fails C02", r[("C02", "JPM")], False)
    off = edit_bank(jpm, lambda fs: [f for f in fs if f["end"] != "2009-12-31"] + [mfact("2012-05-15", "OFF-1", "10-Q", "2012-06-20", 2012, "Q2", 1_000_000_000_000)])
    r = count_failures([off] + base[1:])
    ck.eq("66 period-ends with one off-calendar end still fail C01", r[("C01", "JPM")], False)
    own09 = edit_bank(jpm, lambda fs: fs + [mfact("2009-12-31", "OWN-09", "10-K", "2010-02-26", 2009, "FY", 1_000_000_000_000)])
    r = count_failures([own09] + base[1:])
    ck.eq("2009-12-31 in its own filing fails C02", r[("C02", "JPM")], False)
    gap = edit_bank(jpm, lambda fs: [f for f in fs if f["end"] != "2014-09-30"])
    r = count_failures([gap] + base[1:])
    ck.eq("a missing quarter-end among the 65 fails C02", r[("C02", "JPM")], False)
    nobank = [Bank(JPM, "JPM", "primary", None, None, "")] + base[1:]
    ck.eq("a primary bank with no facts fails C01 and C02", (count_failures(nobank)[("C01", "JPM")], count_failures(nobank)[("C02", "JPM")]), (False, False))


def t_g13(ck):
    ctx = fresh_ctx("full")
    for sid, a, b in (("S3", S3_START, S3_END), ("S1", S1_START, S1_END)):
        dec = decompose(ctx["rows"], PRIMARY, a, b)
        ck.ok("%s: within + mix = total to 1e-9 point" % sid, abs(dec["within"] + dec["mix"] - dec["total"]) < Decimal("1e-9"), str(dec["within"] + dec["mix"] - dec["total"]))
        ck.ok("%s: total = S_end - S_start" % sid, abs(dec["total"] - (ref_share(PRIMARY, qi(b)) - ref_share(PRIMARY, qi(a)))) < Decimal("1e-9"), "")
        d0 = sum(nd_of(c, qi(a))[1] for c in PRIMARY)
        d1 = sum(nd_of(c, qi(b))[1] for c in PRIMARY)
        for x in dec["banks"]:
            n0, dd0 = nd_of(x["cik"], qi(a))
            n1, dd1 = nd_of(x["cik"], qi(b))
            w0, w1, s0, s1 = Decimal(dd0) / d0, Decimal(dd1) / d1, Decimal(n0) / dd0, Decimal(n1) / dd1
            ref_within, ref_mix = ((w0 + w1) / 2) * (s1 - s0) * 100, ((w1 - w0) / 2) * (s0 + s1) * 100
            ck.ok("%s %s: the Shapley within and mix terms" % (sid, TICKER[x["cik"]]), abs(x["within"] - ref_within) < Decimal("1e-9") and abs(x["mix"] - ref_mix) < Decimal("1e-9"), "")
        ck.ok("%s: the weights sum to 100 at both ends" % sid, abs(sum(x["w0"] for x in dec["banks"]) - 100) < Decimal("1e-9") and abs(sum(x["w1"] for x in dec["banks"]) - 100) < Decimal("1e-9"), "")
    D = Decimal
    cases = [("mix of the total's sign and larger than within", dict(mix=D(2), within=D(1), total=D(3)), True), ("mix of the total's sign, larger, within opposite", dict(mix=D(3), within=D(-1), total=D(2)), True),
             ("negative mix larger than within", dict(mix=D(-3), within=D(1), total=D(-2)), True), ("mix smaller than within", dict(mix=D(1), within=D(2), total=D(3)), False),
             ("mix zero", dict(mix=D(0), within=D(2), total=D(2)), False), ("within zero", dict(mix=D(3), within=D(0), total=D(3)), False)]
    for label, dec, want in cases:
        ck.eq("mix_dominates: %s" % label, mix_dominates(dec), want)
        s = statement("S3", sctx(dec=dec))
        ck.eq("...so S3 is %s" % ("VOID mix_dominates" if want else "not VOID"), s["void"], "mix_dominates" if want else "none")
    ck.eq("the opposite sign of the total (impossible with a larger mix) is not VOID", mix_dominates(dict(mix=D(1), within=D(-3), total=D(-2))), False)


def t_g14(ck):
    ctx = fresh_ctx("full")
    reg = rows_registered_new(ctx)
    text = render_readme(ctx, reg)
    ck.eq("the README of the synthetic world passes", readme_problems(text), [])
    ck.eq("SOURCES.md of the synthetic world passes the wording scan", wording_problems("SOURCES.md", render_sources(ctx, dict(vint_rows=[]))), [])
    ck.ok("the denial sentence is in the README exactly as the spec words it", DENIAL_SENTENCE in text, "")
    top = text.split("How to read the table")[0]
    ck.ok("the three results are stated as sentences before the table, with sign, size and label", top.count("\n- ") == 3 and "Between December 2021 and December 2023 the share rose" in top and "so the sign is" in top, top[-400:])
    ck.ok("the S2 sentence gives its sign and the median, from the data", "points above the 2017-2019 median of" in text and "so the sign is RISE; the range label says" in text, "")
    ck.ok("rank is explained where it first appears, before the table", "rank 1 is the largest" in top + text.split("| statement |")[0] and text.index("rank 1 is the largest") < text.index("| statement |"), "")
    for needle in ("C-135**: the project's correction C-135, in CORRECTIONS.md", "docs/index.html", "2024-26 rise in US equity prices", "no statement can be made; the reason is given", "**sens_noflag**", "**latest_filed**",
                   "JN1 is JPMorgan's numerator", "recast, one of those reasons", "**blind**", "a Shapley split", "if the share moved at random with no change in behaviour", "State Street has 51 own-filing quarters",
                   "Why sens_stt and sens_wfc are VOID"):
        ck.ok("the README defines or states: %s" % needle[:50], needle in text, "")
    ck.ok("the old jargon is gone", "i.i.d." not in text, "")
    ck.ok("the coverage line explains State Street (52 and 51)", "52 period-ends and 51 in own filing" in text, "")
    import copy
    c2 = copy.copy(ctx)
    c2["decomp"] = {k: (None if v is None else dict(v, banks=[dict(x) for x in v["banks"]])) for k, v in ctx["decomp"].items()}
    for x in c2["decomp"]["S3"]["banks"]:
        x["s0"], x["s1"] = (Decimal(80), Decimal(79)) if x["cik"] == JPM else (Decimal(80), Decimal(81))
    t2 = render_readme(c2, reg)
    ck.ok("when the banks' own signs differ from the pooled one, the README says so", "over 2021-2023 JPMorgan's own share fell and Goldman's rose" in t2 and "not a statement about each bank" in t2, "")
    ck.eq("...and the generated sentences pass the wording scan", readme_problems(t2), [])
    ck.ok("when they agree it says so instead", "each bank's own change has the sign of the pooled change" in text or "Where a bank's own change differs" in text, "")
    bad = ["re-use velocity rose", "the share drove the rally", "intensity fell", "a significant rise", "banks fuelled the boom", "shares rose because of it", "shares rose by two points",
           "a multiplier of two", "the data is not material", "boosted re-use", "led to more re-use", "in response to the rally"]
    for p in bad:
        ck.ok("'%s' is flagged" % p, bool(wording_problems("README.md", text + "\n" + p + ".\n")), "")
    ck.eq("'the share rose by 1.2 points' passes", wording_problems("README.md", text + "\nIn the sample the share rose by 1.2 points.\n"), [])
    ck.ok("a sentence that borrows the denial wording does not escape the scan", bool(wording_problems("README.md", text + "\nBut nothing here says the share drove the rally.\n")), "")
    ck.ok("a README without the 2017 caption line fails", bool(readme_problems(text.replace(CAPTION_LINE, ""))), "")
    ck.ok("a README without the blind column fails", bool(readme_problems(text.replace("blind", "hidden"))), "")
    ck.ok("a README without 'fair-value share' fails", bool(readme_problems(text.replace("fair-value share", "ratio"))), "")
    ck.ok("a README without the denial sentence fails", bool(readme_problems(text.replace(DENIAL_SENTENCE, ""))), "")
    for sid, row in zip(("S3", "S1", "S2"), reg):
        ck.ok("the sentence of %s ends with the two-banks, not-a-speed line in the README" % sid, AFTER_SENTENCE in text, "")
    ck.ok("no output cell carries a verdict word", not verdict_problems({"README.md": text}), "")


def good_concept(target):
    m = CONCEPT_RX.match(target)
    return 200, json.dumps({"cik": int(m.group(1)), "taxonomy": "us-gaap", "tag": m.group(2), "units": {"USD": []}}).encode("utf-8"), {}


def fetch_rig(tmp, resp=good_concept, clock=None, max_requests=None):
    clock = clock or FakeClock()
    calls = []
    cache, out = os.path.join(tmp, "cache"), os.path.join(tmp, "out")

    def opener(host, target, headers, timeout, cap):
        calls.append((host, target, dict(headers)))
        r = resp(target) if callable(resp) else resp
        if isinstance(r, Exception):
            raise r
        return r

    ns = argparse.Namespace(cmd="fetch-concepts", vintage=clock.now_utc().strftime("%Y%m%d"), cache=cache, out=out, max_requests=max_requests)

    def go(environ=None, ns_=None):
        said = []
        code = run_fetch(ns_ or ns, environ={"SEC_UA": FIXTURE_CONTACT} if environ is None else environ, opener=opener, sleeper=clock.sleep, now_utc=clock.now_utc, say=said.append, stop_dir=cache)
        return code, said

    return go, calls, ns, clock


def bytes_of_tree(root):
    out = b""
    for d, _, fs in os.walk(root):
        for n in sorted(fs):
            out += read_file(os.path.join(d, n), "rb")
    return out


def t_g15(ck):
    forget_secrets()
    with tempfile.TemporaryDirectory(prefix="cru_g15_", ignore_cleanup_errors=True) as tmp:
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "p"))
        stop = os.path.join(ns.cache, STOP_NAME)
        create_stop(stop, "status: 429\nutc_time: x\nurl_path: y\nretry_after: 5\nbody_head: z\n")
        before = sha256_of(read_file(stop))
        code, said = go()
        ck.eq("with a planted STOP_cru a fetch makes no request and exits 2", (code, len(calls)), (2, 0))
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
            ck.ok("a reply of %s writes STOP_cru, ends the fetch (exit 2) after exactly one request" % label, has and code == 2 and len(calls) == 1 and len(vint_rows(ns.out)) == 1, "exit %s, %d calls, stop %s" % (code, len(calls), has))
            if has:
                ck.ok("...with the five fields in order", stop_text_ok(read_file(stp, "r")), read_file(stp, "r")[:200])
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "n404"), (404, b"<?xml version='1.0'?><Error>NoSuchKey</Error>", {}), max_requests=3)
        code, said = go()
        ck.eq("a 404 on a companyconcept path is absent: no STOP, the slice ends by its limit (exit 4)", (code, os.path.exists(os.path.join(ns.cache, STOP_NAME)), len(calls)), (4, False, 3))
        ck.eq("...and each 404 is a vintages.csv row", [r["status"] for r in vint_rows(ns.out)], ["404"] * 3)
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "tmo"), SocketFault("TimeoutError"))
        code, said = go()
        ck.ok("a timeout exits 3, writes no STOP and retries nothing", code == 3 and not os.path.exists(os.path.join(ns.cache, STOP_NAME)) and len(calls) == 1 and any(s.startswith("FAIL network /api/xbrl") for s in said), str((code, said)))
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "ok"), max_requests=2)
        code, said = go()
        ck.ok("good bodies write no STOP", code == 4 and not os.path.exists(os.path.join(ns.cache, STOP_NAME)), str(code))
    forget_secrets()


def t_g16(ck):
    forget_secrets()
    for u in ("https://www.sec.gov/Archives/edgar/data/1/x.htm", "https://efts.sec.gov/LATEST/search-index?q=x", "https://www.sec.gov/files/dera/data/financial-statement-and-notes-data-sets/2026q1_notes.zip",
              "https://example.com/api/xbrl/companyconcept/CIK0000019617/us-gaap/%s.json" % TAG_N, "http://data.sec.gov/api/xbrl/companyconcept/CIK0000019617/us-gaap/%s.json" % TAG_N,
              "https://data.sec.gov/api/xbrl/companyconcept/CIK0000019617/us-gaap/%s.json?x=1" % TAG_N, "https://data.sec.gov/api/xbrl/companyfacts/CIK0000019617.json",
              "https://data.sec.gov/submissions/CIK0000019617.json", "https://data.sec.gov/api/xbrl/frames/us-gaap/%s/USD/CY2019Q4I.json" % TAG_N,
              "https://data.sec.gov/api/xbrl/companyconcept/CIK0000019617/us-gaap/Assets.json", "https://data.sec.gov:8443/api/xbrl/companyconcept/CIK0000019617/us-gaap/%s.json" % TAG_N,
              "https://fred.stlouisfed.org/series/DGS10", "https://alfred.stlouisfed.org/series?seid=DGS10"):
        ck.raises("refused before any request: %s" % u[:70], Refused, lambda u=u: check_url(u))
    ck.eq("the allowed target", check_url("https://data.sec.gov/api/xbrl/companyconcept/CIK0000019617/us-gaap/%s.json" % TAG_N), (HOST, "/api/xbrl/companyconcept/CIK0000019617/us-gaap/%s.json" % TAG_N))
    with tempfile.TemporaryDirectory(prefix="cru_g16_", ignore_cleanup_errors=True) as tmp:
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "nouser"))
        code, said = go(environ={})
        ck.eq("a fetch with SEC_UA unset exits 2 and makes no request", (code, len(calls)), (2, 0))
        ck.ok("...and prints no value", all(FIXTURE_CONTACT not in s for s in said), "")
        ck.raises("a contact string an HTTP header cannot carry is refused", Refused, lambda: fetch_rig(os.path.join(tmp, "lat"))[0](environ={"SEC_UA": "Fixture ’ contact"}))
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "a"), max_requests=3)
        code, said = go()
        ck.eq("a good slice sends exactly the requests allowed", (code, len(calls)), (4, 3))
        if calls:
            ck.eq("...to data.sec.gov with the contact string and identity encoding", (calls[0][0], calls[0][2].get("User-Agent"), calls[0][2].get("Accept-Encoding")), (HOST, FIXTURE_CONTACT, "identity"))
        ck.ok("...and the contact string is in no byte written", FIXTURE_CONTACT.encode("utf-8") not in bytes_of_tree(os.path.join(tmp, "a")), "")
        rows = vint_rows(ns.out)
        gaps = [(parse_utc_ms(r1["retrieved_utc"]) - parse_utc_ms(r0["retrieved_utc"])).total_seconds() for r0, r1 in zip(rows, rows[1:])]
        ck.ok("requests are at least 1.0 s apart (0.9 s is a violation)", bool(gaps) and min(gaps) >= 1.0 - 1e-9, str(gaps))
        ck.ok("every vintages.csv row names data.sec.gov and no status is 403, 429 or 3xx", all(r["host"] == HOST and r["status"] not in ("403", "429") and not r["status"].startswith("3") for r in rows), "")
        code2, said2 = go()
        paths2 = [c[1] for c in calls[3:]]
        ck.ok("a resumed run does not request a body it already holds", len(set(c[1] for c in calls[:3]) & set(paths2)) == 0 and len(paths2) == 3, str(paths2))
        ck.eq("a second slice stops by its limit too", code2, 4)
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "full"))
        code, said = go()
        ck.eq("a full run is exactly eight requests", (code, len(calls)), (0, 8))
        ck.eq("...all on data.sec.gov, in the order JPM, GS, State Street, Wells Fargo (N then D)", [(c[0], c[1].split("/")[4]) for c in calls], [(HOST, "CIK" + b) for b in (JPM, JPM, GS, GS, STT, STT, WFC, WFC)])
        ck.ok("...with no fetch_log.csv", not os.path.exists(os.path.join(ns.out, "fetch_log.csv")), "")
        code, said = go()
        ck.eq("a second full run requests nothing: every body is cached", (code, len(calls)), (0, 8))
        ck.eq("...and vintages.csv holds eight rows", len(vint_rows(ns.out)), 8)
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "echo"), lambda t: (403, ("Forbidden for %s" % FIXTURE_CONTACT).encode("utf-8"), {}))
        code, said = go()
        ck.eq("a 403 that echoes the contact string latches STOP", code, 2)
        ck.ok("...but no byte of the contact string is written, STOP included", FIXTURE_CONTACT.encode("utf-8") not in bytes_of_tree(os.path.join(tmp, "echo")) and os.path.exists(os.path.join(ns.cache, STOP_NAME)), "")
        ck.raises("a write that would hold the contact string is refused", Refused, lambda: write_text(os.path.join(tmp, "x.txt"), "x " + FIXTURE_CONTACT))
        go, calls, ns, clock = fetch_rig(os.path.join(tmp, "r301"), (301, b"", {"location": "/api/xbrl/companyconcept/CIK0000019617/us-gaap/%s.json" % TAG_D}))
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
    ck.eq("the per-run cap is 20", FETCH_CAP, 20)
    forget_secrets()


# ---- an on-disk world: the fetch mode run against a mock opener, so every later test reads what the fetch wrote ----
def concept_body(cik, tag, tweak=None, drop=None):
    facts = world_facts(cik, tag, (drop or {}).get(cik, ()), tweak)
    units = [dict(end=f["end"], val=int(f["val"]), accn=f["accn"], fy=int(f["fy"]), fp=f["fp"], form=f["form"], filed=f["filed"]) for f in facts]
    return json.dumps(dict(cik=int(cik), taxonomy="us-gaap", tag=TAG_NAME[tag], label="x", description="x", entityName=NAMES[cik], units={"USD": units})).encode("utf-8")


def world_resp(tweak=None, wfc_absent=False, drop=None):
    def resp(target):
        m = CONCEPT_RX.match(target)
        cik, tag = m.group(1), "N" if m.group(2) == TAG_N else "D"
        if cik == WFC and wfc_absent:
            return 404, b'{"message":"not found"}', {}
        return 200, concept_body(cik, tag, tweak, drop), {}
    return resp


def disk_world(tmp, vintage_offset=0, tweak=None, wfc_absent=False, base=None):
    """Fetch the synthetic world into tmp (cache and committed-like folder) with a mock opener; returns (ns, vintage). A second call with the same tmp and another offset adds a second vintage."""
    clock = FakeClock(1_793_523_200.0 + 86400 * vintage_offset)
    go, calls, ns, clock = fetch_rig(tmp, world_resp(tweak, wfc_absent), clock)
    code, said = go()
    assert code == 0 and len(calls) == 8, (code, said)
    return ns


def synthetic_pins():
    pins = []
    for cik, end, nb, db in PINS:
        n, d = nd_of(cik, qi(end))
        pins.append((cik, end, format(Decimal(n) / Decimal(10 ** 9), ".3f"), format(Decimal(d) / Decimal(10 ** 9), ".3f")))
    return tuple(pins)


_DISK = {}


def base_disk():
    """The synthetic world fetched once (vintage 20261101: all four banks; vintage 20261102: Wells Fargo absent and JPM's numerator at 2023-12-31 moved)."""
    if "td" not in _DISK:
        td = tempfile.TemporaryDirectory(prefix="cru_world_", ignore_cleanup_errors=True)
        _DISK["td"] = td
        tmp = os.path.join(td.name, "w")
        ns1 = disk_world(tmp)
        ns2 = disk_world(tmp, vintage_offset=1, tweak={(JPM, "N", "2023-12-31"): nd_of(JPM, qi("2023-12-31"))[0] + 10 ** 10}, wfc_absent=True)
        _DISK["w"] = dict(root=tmp, cache=ns1.cache, out=ns1.out, v1=ns1.vintage, v2=ns2.vintage)
    return _DISK["w"]


def copy_world(name):
    w = base_disk()
    dst = os.path.join(_DISK["td"].name, name)
    shutil.copytree(w["root"], dst)
    return dict(root=dst, cache=os.path.join(dst, "cache"), out=os.path.join(dst, "out"), v1=w["v1"], v2=w["v2"])


def build_ns(w, stage, vintage=None, out=None, committed=None, **kw):
    return argparse.Namespace(cmd="build", vintage=vintage or w["v1"], stage=stage, cache=w["cache"], out=out or w["out"], pins=None, supersede=kw.get("supersede", False), committed=committed, readme_only=kw.get("readme_only", False))


def quiet_build(ns):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = run_build(ns)
    return code, buf.getvalue()


def read_dir(path):
    return {n: read_file(os.path.join(path, n), "r") for n in sorted(os.listdir(path)) if os.path.isfile(os.path.join(path, n))}


def tree_hash(path):
    h = hashlib.sha256()
    for d, _, fs in sorted(os.walk(path)):
        for n in sorted(fs):
            h.update(n.encode())
            h.update(read_file(os.path.join(d, n)))
    return h.hexdigest()


def t_g17_pre(ck):
    w = copy_world("g17pre")
    with patched(PINS=synthetic_pins()):
        code, out = quiet_build(build_ns(w, "pre"))
    files = read_dir(w["out"])
    ck.eq("--stage pre writes banks, probes, quarters and checks, and no registered.csv", sorted(n for n in files if n != "vintages.csv"), sorted(PRE_FILES))
    h, rows = csv_body(files["quarters.csv"])
    ci = {c: h.index(c) for c in h}
    ck.ok("...no n_usd, d_usd or share_pct cell holds anything", all(r[ci["n_usd"]] == "" and r[ci["d_usd"]] == "" and r[ci["share_pct"]] == "" for r in rows), "")
    ck.ok("...and the own-filing statuses are there (65 ok rows for JPM)", sum(1 for r in rows if r[ci["cik10"]] == JPM and r[ci["basis"]] == "own_filing" and r[ci["status"]] == "ok") == 65, "")
    ck.eq("...with no check failing", (code, [r for r in csv_body(files["checks.csv"])[1] if r[-1] == "FAIL"]), (0, []))
    ck.ok("...and C11 is among them", any(r[0] == "C11" for r in csv_body(files["checks.csv"])[1]), "")
    banks, vrows, raw_dir = load_banks(w["cache"], w["out"], w["v1"], "pre")
    ck.ok("the pre-stage loader holds no val in any fact", not any("val" in f for b in banks for c in b.any_conc() for f in c.facts), "")
    ck.eq("...and the run did not touch the raw bodies", tree_hash(os.path.join(w["cache"], w["v1"], "raw")), tree_hash(os.path.join(base_disk()["cache"], w["v1"], "raw")))
    first = read_dir(w["out"])
    with patched(PINS=synthetic_pins()):
        quiet_build(build_ns(w, "pre"))
    ck.eq("a second pre build is byte-identical", read_dir(w["out"]), first)


def t_g17_dry(ck):
    w = copy_world("g17dry")
    scratch = os.path.join(_DISK["td"].name, "g17dry_scratch")
    before = tree_hash(w["out"])
    with patched(PINS=synthetic_pins()):
        code, out = quiet_build(build_ns(w, "dry", out=scratch, committed=w["out"]))
    files = read_dir(scratch)
    ck.eq("--stage dry writes only headline.csv and checks.csv, outside the committed folder", sorted(files), ["checks.csv", "headline.csv"])
    ck.eq("...and the committed folder is untouched", tree_hash(w["out"]), before)
    h, rows = csv_body(files["headline.csv"])
    ck.ok("...headline.csv holds only count_ statistics", bool(rows) and all(r[h.index("statistic")].startswith("count_") for r in rows), "")
    blob = files["headline.csv"] + files["checks.csv"]
    ck.ok("...no share, sign, label or void reason appears in either file", not any(t in blob for t in ("RISE", "FALL", "ZERO", "WITHIN_RANGE", "OUTSIDE_RANGE", "LEVEL_", "VOID", "endpoint_", "thin_yardstick")), "")
    ck.ok("...no dollar value of the series appears in either file", not re.search(r"\d{10,}", blob), "")
    ck.ok("...no registered.csv in the scratch folder", not os.path.exists(os.path.join(scratch, "registered.csv")), "")
    ck.eq("...and no check fails on the synthetic world", (code, [r for r in csv_body(files["checks.csv"])[1] if r[-1] == "FAIL"]), (0, []))
    ck.ok("...the dry counts carry the Y member count (23)", any(r[h.index("statistic")] == "count_Y_members" and r[h.index("value")] == "23" for r in rows), "")
    ck.raises("the dry stage refuses the committed folder as --out", Refused, lambda: quiet_build(build_ns(w, "dry", out=w["out"], committed=w["out"])))
    ck.eq("...and wrote nothing there", tree_hash(w["out"]), before)


def t_g17_full(ck):
    w = copy_world("g17full")
    vint_before = read_file(os.path.join(w["out"], "vintages.csv"), "r")
    with patched(PINS=synthetic_pins()):
        code, out = quiet_build(build_ns(w, "full"))
        files = read_dir(w["out"])
        ck.eq("the first full build exits 0 and writes every committed file but the two inputs", (code, sorted(set(COMMITTED) - set(files))), (0, ["captions_pin.csv"]))
        reg1 = files["registered.csv"]
        ck.eq("the build never writes vintages.csv (the fetch mode is its only writer)", files["vintages.csv"], vint_before)
        ext = os.path.join(w["cache"], w["v1"], "concept_extract.csv")
        ck.ok("...and the vintage's concept_extract.csv", os.path.isfile(ext), "")
        snap = {n: x for n, x in files.items()}
        code, out = quiet_build(build_ns(w, "full"))
        again = read_dir(w["out"])
        ck.eq("a second build of the same vintage is byte-identical in every file", [n for n in again if again[n] != snap.get(n)], [])
        code, out = quiet_build(build_ns(w, "full", vintage=w["v2"]))
        after = read_dir(w["out"])
        ck.eq("a second vintage rewrites the other outputs but registered.csv is unchanged", (after["registered.csv"] == reg1, after["quarters.csv"] != snap["quarters.csv"]), (True, True))
        ck.eq("...and the S1 row is byte-identical, one row each", ([l for l in after["registered.csv"].splitlines() if l.startswith("S1,")] == [l for l in reg1.splitlines() if l.startswith("S1,")], after["registered.csv"].count("\nS1,")), (True, 1))
        ck.eq("...the second vintage has Wells Fargo absent (a 404 row), counts_only", [r for r in csv_body(after["probes.csv"])[1]][0][-1], "counts_only")
        ck.eq("...and its checks do not fail on the registered rows of the first vintage", [r for r in csv_body(after["checks.csv"])[1] if r[-1] == "FAIL"], [])


def t_g17_mixed(ck):
    w = copy_world("g17mix")
    with patched(PINS=synthetic_pins()):
        try:
            code, out = quiet_build(build_ns(w, "dry", vintage=w["v2"], out=os.path.join(_DISK["td"].name, "g17mix_s"), committed=w["out"]))
        except DataError as e:
            code = "DataError: %s" % str(e)[:80]
        ck.eq("a build of one vintage uses only that vintage's rows (Wells Fargo is absent in the second)", code, 0)
        banks = load_banks(w["cache"], w["out"], w["v2"], "full")[0]
        banks1 = load_banks(w["cache"], w["out"], w["v1"], "full")[0]
        ck.eq("...Wells Fargo has no facts in vintage two and has them in vintage one", ([b.conc["N"] is None for b in banks if b.cik == WFC], [b.conc["N"] is None for b in banks1 if b.cik == WFC]), ([True], [False]))


def t_g17_parser(ck):
    with contextlib.redirect_stderr(io.StringIO()):
        ck.raises("build without --stage is a usage error (no default stage)", SystemExit, lambda: make_parser().parse_args(["build", "--vintage", "20261101"]))
    ck.eq("--stage full is accepted when named", make_parser().parse_args(["build", "--vintage", "20261101", "--stage", "full"]).stage, "full")


def t_g17_supersede(ck):
    ctx = fresh_ctx("full")
    old = rows_registered_new(ctx)
    new = [list(r) for r in old]
    for r in new:
        r[ALLOW["registered.csv"].index("n_dist")] = "99"
    sup = supersede_rows(old, new)
    h = ALLOW["registered.csv"]
    ck.eq("supersede keeps the old rows, marked yes, and adds the next version", sorted((r[0], r[1], r[2]) for r in sup), sorted([(s, "1", "yes") for s in ("S1", "S2", "S3")] + [(s, "2", "no") for s in ("S1", "S2", "S3")]))
    ck.ok("...the old rows are otherwise unchanged", all([c for i, c in enumerate(r) if i not in (h.index("superseded"),)] == [c for i, c in enumerate(o) if i not in (h.index("superseded"),)] for r, o in zip([r for r in sup if r[1] == "1"], sorted(old, key=lambda r: ("S3", "S1", "S2").index(r[0])))), "")
    w = copy_world("g17sup")
    with patched(PINS=synthetic_pins()):
        quiet_build(build_ns(w, "full"))
        code, out = quiet_build(build_ns(w, "full", supersede=True))
        reg = csv_body(read_dir(w["out"])["registered.csv"])[1]
    ck.eq("a --supersede build writes six rows: three superseded, three at version 2", (code, sorted((r[0], r[1], r[2]) for r in reg)), (0, sorted([(s, "1", "yes") for s in ("S1", "S2", "S3")] + [(s, "2", "no") for s in ("S1", "S2", "S3")])))
    ck.ok("...and the README shows both", "Superseded rows" in read_dir(w["out"])["README.md"], "")
    w2 = copy_world("g17pre2")
    with patched(PINS=synthetic_pins()):
        quiet_build(build_ns(w2, "full"))
        ck.raises("a pre build is refused once registered.csv exists", Refused, lambda: quiet_build(build_ns(w2, "pre")))


def t_g17_readme_only(ck):
    w = copy_world("g17ro")
    with patched(PINS=synthetic_pins()):
        quiet_build(build_ns(w, "full"))
        before = read_dir(w["out"])
        ext = os.path.join(w["cache"], w["v1"], "concept_extract.csv")
        ext_before = read_file(ext)
        write_text(os.path.join(w["out"], "README.md"), "stale\n")
        write_text(os.path.join(w["out"], "SOURCES.md"), "stale\n")
        os.remove(ext)
        write_text(ext, "stale\n")
        code, out = quiet_build(build_ns(w, "full", readme_only=True))
        after = read_dir(w["out"])
        ck.eq("--readme-only re-renders README.md and SOURCES.md to what the full build wrote", (code, after["README.md"] == before["README.md"], after["SOURCES.md"] == before["SOURCES.md"]), (0, True, True))
        ck.eq("...and writes nothing else: every CSV is byte-identical, the extract is untouched", ([n for n in after if n not in ("README.md", "SOURCES.md") and after[n] != before[n]], read_file(ext)), ([], b"stale\n"))
        ck.raises("--readme-only is refused with --stage pre", Refused, lambda: quiet_build(build_ns(w, "pre", readme_only=True)))
    w2 = copy_world("g17ro2")
    with patched(PINS=synthetic_pins()):
        ck.raises("--readme-only is refused when there is no registered.csv", Refused, lambda: quiet_build(build_ns(w2, "full", readme_only=True)))


def t_g17(ck):
    for fn in (t_g17_pre, t_g17_dry, t_g17_full, t_g17_mixed, t_g17_parser, t_g17_supersede, t_g17_readme_only):
        fn(ck)


_TEXTS = {}


def base_texts():
    if "t" not in _TEXTS:
        ctx = fresh_ctx("full")
        with patched(PINS=synthetic_pins()):
            env = dict(pin_text=real_pins()[0], vint_rows=[], raw_dir=None, dry=False, existing_reg=None, supersede=False)
            t, checks = make_texts(ctx, env)
        _TEXTS["t"] = (dict(t), checks)
    return _TEXTS["t"]


def t_g18(ck):
    files, checks = base_texts()
    files = dict(files)
    ck.ok("the allowlist text reproduces the section 5 hash", allow_hash_ok(), "")
    ck.eq("every written header is exactly its allowlist line", [n for n in ALLOW_ORDER if n in files and csv_body(files[n])[0] != SPEC_ALLOW_TEXT.splitlines()[ALLOW_ORDER.index(n)].split(":", 1)[1].split(",")], [])
    ck.eq("the clean synthetic folder has no problem", folder_problems(files, full=False), [])
    ck.eq("...and no check fails on it except C03/C09 notes that need the real cache", [(r[0], r[3]) for r in checks if r[4] == "FAIL" and r[0] not in ("C09",)], [])
    for label, extra in (("a .json file", {"raw.json": "{}"}), ("an .xml file", {"x.xml": "<a/>"}), ("a thirteenth csv", {"extra.csv": "a,b\n1,2\n"}), ("a STOP file", {"STOP_cru": "x"}),
                         ("a zip", {"a.zip": "PK\x03\x04"})):
        ck.ok("a planted %s is reported" % label, bool(leak_problems(dict(files, **extra), full=False)), "")
    ck.ok("a local /Users/ path is reported", bool(leak_problems(dict(files, **{"README.md": files["README.md"] + "\n/Users/x/y\n"}), full=False)), "")
    ck.ok("a local /private/ path is reported", bool(leak_problems(dict(files, **{"README.md": files["README.md"] + "\n/private/tmp\n"}), full=False)), "")
    ck.ok("an at sign is reported", bool(leak_problems(dict(files, **{"SOURCES.md": files["SOURCES.md"] + "\na@b\n"}), full=False)), "")
    ck.ok("a missing committed file is reported on a full folder", bool(leak_problems(files, full=True)), "")
    swapped = files["banks.csv"].replace("entity_name", "name", 1)
    ck.ok("a renamed header is reported", bool(header_problems(dict(files, **{"banks.csv": swapped}))), "")
    extra = files["samples.csv"].replace("share_pct,flags", "share_pct,flags,note", 1)
    ck.ok("an extra column is reported", bool(header_problems(dict(files, **{"samples.csv": extra}))), "")
    src = files["banks.csv"].replace("# source:", "# sourc:", 1)
    ck.ok("a missing `# source:` line makes the first line a header, which is reported", bool(header_problems(dict(files, **{"banks.csv": src}))), "")
    ck.eq("`# source:` lines are skipped when the header is read", csv_body(files["banks.csv"])[0], ALLOW["banks.csv"])
    lines = files["banks.csv"].splitlines()
    ck.ok("a duplicate key is reported", bool(dup_key_problems(dict(files, **{"banks.csv": files["banks.csv"] + lines[-1] + "\n"}))), "")
    ck.ok("a verdict word is reported", bool(verdict_problems(dict(files, **{"banks.csv": files["banks.csv"].replace("Jpmorgan", "HELD", 1)}))), "")
    ck.ok("a value outside the lists is reported", bool(value_problems(dict(files, **{"quarters.csv": files["quarters.csv"].replace(",ok\n", ",fine\n", 1)}))), "")
    q = files["samples.csv"].splitlines()
    i = next(k for k, l in enumerate(q) if l.startswith("primary,own_filing,2015-12-31"))
    cells = q[i].split(",")
    cells[4] = str(int(cells[4]) + 1)
    bent = "\n".join(q[:i] + [",".join(cells)] + q[i + 1:]) + "\n"
    ck.ok("a samples.csv n_usd that is not the sum of its banks fails C05", bool(c05_problems(dict(files, **{"samples.csv": bent}))), "")
    c = files["changes.csv"].splitlines()
    j = next(k for k, l in enumerate(c) if l.startswith("primary,own_filing,q8") and ",2015-12-31," in l)
    cc = c[j].split(",")
    cc[7] = pct3(Decimal(cc[7]) + Decimal("0.001"))
    bent = "\n".join(c[:j] + [",".join(cc)] + c[j + 1:]) + "\n"
    ck.ok("a changes.csv D8 that moved by 0.001 fails C08", bool(c08_problems(dict(files, **{"changes.csv": bent}))), "")
    rg = files["registered.csv"].splitlines()
    k = next(n for n, l in enumerate(rg) if l.startswith("S3,"))
    rc = next(csv.reader([rg[k]]))
    rc[ALLOW["registered.csv"].index("stat")] = pct3(Decimal(rc[ALLOW["registered.csv"].index("stat")]) + 1)
    out = io.StringIO()
    csv.writer(out, lineterminator="\n").writerow(rc)
    bent = "\n".join(rg[:k] + [out.getvalue().rstrip("\n")] + rg[k + 1:]) + "\n"
    ck.ok("a registered.csv statistic that does not recompute fails C08", bool(c08_problems(dict(files, **{"registered.csv": bent}))), "")
    cs = read_file(os.path.join(ROOT, "bin", "check.sh"), "r")
    ck.eq("bin/check.sh holds its own literal copy of the thirteen lines and the 4.6 hash", checksh_problems(cs), [])
    broken = cs.replace("banks.csv) want='cik10,ticker", "banks.csv) want='cik10,tickerX", 1)
    ck.ok("a header line edited in check.sh is reported", bool(checksh_problems(broken)), "")
    ck.ok("an edited 4.6 hash in check.sh is reported", bool(checksh_problems(cs.replace(SPEC_PREREG_SHA256, "0" * 64))), "")
    ck.ok("a guard that names the script is reported", bool(checksh_problems(cs.replace("cru_leak_check() {", "cru_leak_check() {\n  python3 bin/collateral_reuse.py\n", 1))), "")


def pin_ctx(drop_date=None):
    ctx = fresh_ctx("full")
    if drop_date:
        ctx["rows"][JPM]["own_filing"][drop_date] = dict(ctx["rows"][JPM]["own_filing"][drop_date], status="missing_n")
    return ctx


def t_g20(ck):
    v, tol = pin_usd("775.3")
    ck.eq("a pin printed to $0.1bn: tolerance 0.05bn", (v, tol), (Decimal(775300000000), Decimal(50000000)))
    ck.eq("a pin printed to $0.001bn: tolerance 0.5mn", pin_usd("912.863")[1], Decimal(500000))
    ck.eq("a thousands separator is read", pin_usd("1,210.7")[0], Decimal(1210700000000))
    ck.ok("a value off by one unit of the last digit fails", not pin_ok(Decimal(100000000), tol), "")
    ck.ok("off by half a unit passes", pin_ok(Decimal(50000000), tol) and pin_ok(Decimal(-50000000), tol), "")
    ck.ok("off by 0.6 unit fails", not pin_ok(Decimal(60000000), tol) and not pin_ok(Decimal(-60000000), tol), "")
    ck.ok("exact passes", pin_ok(Decimal(0), tol), "")
    with patched(PINS=synthetic_pins()):
        bad, gaps = c03_report(pin_ctx())
        ck.eq("on the synthetic world every synthetic pin ties out", (bad, len(gaps)), ([], 18))
        bad, gaps = c03_report(pin_ctx("2017-12-31"))
        ck.ok("a pin for a date the series lacks is reported, not passed", any("no usable value" in b for b in bad), str(bad))
    ctx = pin_ctx()
    bad, gaps = c03_report(ctx)
    ck.ok("the real pins do not tie out to the synthetic series (the check is not vacuous)", len(bad) >= 9, str(len(bad)))


def t_g21(ck):
    full = full_series()
    ch = [qi(CAP_FIRST)]

    def kept(series, lo_end, hi_end, sample="primary"):
        y = yardstick(series, change_idxs_of(sample))
        return {qd(q) for q, _ in y["members"]}

    m = kept(full, "", "")
    ck.ok("a window starting 2016-12-31 and ending 2018-12-31 is excluded from Y", "2018-12-31" not in m, "")
    ck.ok("a window ending 2016-12-31 is kept", "2016-12-31" in m, "")
    ck.ok("a window starting 2017-03-31 (ending 2019-03-31) is kept", "2019-03-31" in m, "")
    ck.ok("a window ending 2017-03-31 is excluded", "2017-03-31" not in m, "")
    ck.ok("the eight windows ending 2017-03-31..2018-12-31 are all excluded", not any(e in m for e in ("2017-03-31", "2017-06-30", "2017-09-30", "2017-12-31", "2018-03-31", "2018-06-30", "2018-09-30", "2018-12-31")), "")
    ck.eq("Goldman alone has no exclusion", kept(full, "", "", "sens_gs") >= {"2017-03-31", "2018-12-31"}, True)
    ck.eq("...and every sample that holds JPMorgan has it", (kept(full, "", "", "sens_jpm") == m, kept(full, "", "", "sens_stt") == m), (True, True))
    y = yardstick(full, ch)
    ck.eq("YR is computed with the exclusion: 17 members on the world, 17 on a full series with ends from 2013-12-31 less the 8", len([1 for q, _ in y["yr"]]), 25 - 8)
    ctx = fresh_ctx("full")
    ck.eq("YR on the synthetic world: 17", len(ctx["y"]["yr"]), 17)
    wide = [Decimal(x) / 4 - 1 for x in range(Y_EXP)]
    narrow = wide[-YR_EXP:]
    s = statement("S3", sctx(series={qi(S3_END): Decimal("73")}, ymem=wide, yrmem=[Decimal(0), Decimal(1), Decimal(2)] * 5 + [Decimal(1), Decimal(1)]))
    ck.eq("a stat that is WITHIN against Y but a RISE against YR is VOID yardstick_disagrees", (s["void"], s["label"]), ("yardstick_disagrees", "VOID"))
    s = statement("S3", sctx(ymem=wide, yrmem=narrow))
    ck.eq("the same labels against Y and YR are not voided", s["void"], "none")
    ck.ok("the README carries the 2017 caption line", CAPTION_LINE in render_readme(ctx, rows_registered_new(ctx)), "")
    ck.eq("the caption classes of the six pinned year-ends are those of 2.6", [(caption_class(pin_map(real_pins()[1]), JPM, "N", e)) for e in PIN_DATES], ["JN1", "JN1", "JN2", "JN2", "JN2", "JN2"])
    ck.ok("a date that is not pinned follows the rule (JPM numerator: JN1 before 2017-03-31, JN2 from it)", (caption_class({}, JPM, "N", "2016-12-31"), caption_class({}, JPM, "N", "2017-03-31")) == ("JN1", "JN2"), "")


def t_x_build(ck):
    """The end-to-end build on the synthetic world: pre, dry, full, the reference arithmetic, the outputs and M28 on them."""
    w = copy_world("x1")
    scratch = os.path.join(_DISK["td"].name, "x1_scratch")
    with patched(PINS=synthetic_pins()):
        code_pre, _ = quiet_build(build_ns(w, "pre"))
        pre_files = read_dir(w["out"])
        code_dry, _ = quiet_build(build_ns(w, "dry", out=scratch, committed=w["out"]))
        code, out = quiet_build(build_ns(w, "full"))
        files = read_dir(w["out"])
    ck.eq("pre, dry and full exit 0", (code_pre, code_dry, code), (0, 0, 0))
    ck.eq("full writes every committed name except captions_pin.csv (an input)", sorted(set(COMMITTED) - set(files)), ["captions_pin.csv"])
    ck.ok("full replaces the pre-stage quarters.csv (values now present)", files["quarters.csv"] != pre_files["quarters.csv"] and re.search(r",\d{12,},\d{12,},", files["quarters.csv"]) is not None, "")
    chk = csv_body(files["checks.csv"])[1]
    ck.eq("checks.csv has no FAIL and no WARN", [r for r in chk if r[-1] in ("FAIL", "WARN")], [])
    ck.eq("all of C01 C02 C03 C04 C05 C07 C08 C09 C11 C12 C14 C19 C20 are present", sorted({r[0] for r in chk}), ["C01", "C02", "C03", "C04", "C05", "C07", "C08", "C09", "C11", "C12", "C14", "C19", "C20"])
    reg = {r[0]: r for r in csv_body(files["registered.csv"])[1]}
    h = ALLOW["registered.csv"]
    I = lambda c: h.index(c)
    ck.eq("registered.csv: one row each for S1, S2, S3, version 1, not superseded, with the hashes", sorted((r[0], r[1], r[2], r[I("prereg_sha256")], r[I("population_sha256")]) for r in reg.values()),
          sorted((s, "1", "no", SPEC_PREREG_SHA256, SPEC_POP_SHA256) for s in ("S1", "S2", "S3")))
    ck.eq("...blind: S3 full, S1 and S2 partial", {s: r[I("blind")] for s, r in reg.items()}, {"S3": "full", "S1": "partial", "S2": "partial"})
    # reference arithmetic, independent of the build's code path
    ref_lo = [qi("2011-12-31") + j for j in range(33)]
    members = [q for q in ref_lo if q - 8 >= qi("2010-06-30") and not (q - 8 <= qi(CAP_LAST_BEFORE) and q >= qi(CAP_FIRST))]
    vals = [ref_share(PRIMARY, q) - ref_share(PRIMARY, q - 8) for q in members]
    s3 = ref_share(PRIMARY, qi(S3_END)) - ref_share(PRIMARY, qi(S3_START))
    s1 = ref_share(PRIMARY, qi(S1_END)) - ref_share(PRIMARY, qi(S1_START))
    ck.eq("n in the yardstick is 23 and the extremes are the reference ones", (reg["S3"][I("n_dist")], reg["S3"][I("dist_min")], reg["S3"][I("dist_max")]), ("23", pct3(min(vals)), pct3(max(vals))))
    ck.eq("S3 and S1 statistics are the reference arithmetic", (reg["S3"][I("stat")], reg["S1"][I("stat")]), (pct3(s3), pct3(s1)))
    exp_label = lambda s: "RISE_OUTSIDE_RANGE" if s > max(vals) else ("FALL_OUTSIDE_RANGE" if s < min(vals) else "WITHIN_RANGE")
    ck.eq("...and so are their labels and signs", (reg["S3"][I("label")], reg["S1"][I("label")], reg["S3"][I("sign")]), (exp_label(s3), exp_label(s1), "RISE" if s3 >= Decimal("0.1") else ("FALL" if s3 <= Decimal("-0.1") else "ZERO")))
    lv = [ref_share(PRIMARY, q) for q in range(qi(YL_FIRST), qi(YL_LAST) + 1)]
    s2 = ref_share(PRIMARY, qi(S2_DATE))
    ck.eq("S2 is the reference level against the 2017-2019 levels", (reg["S2"][I("stat")], reg["S2"][I("dist_min")], reg["S2"][I("dist_max")], reg["S2"][I("n_dist")]), (pct3(s2), pct3(min(lv)), pct3(max(lv)), "12"))
    q = {(r[0], r[2], r[3]): r for r in csv_body(files["quarters.csv"])[1]}
    ck.ok("quarters.csv: an ok row for each primary bank at each of the 65 quarter-ends and none for 2010-03-31", all(q[(c, e, "own_filing")][-1] == "ok" for c in PRIMARY for e in [qd(i) for i in range(qi("2010-06-30"), qi("2026-06-30") + 1)]) and q[(JPM, "2010-03-31", "own_filing")][-1] == "missing_n", "")
    sm = [r for r in csv_body(files["samples.csv"])[1] if r[0] == "primary" and r[1] == "own_filing"]
    ck.eq("samples.csv (primary, own_filing) has 65 rows", len(sm), 65)
    ck.ok("...and its sums are exact to the dollar", all(Decimal(r[4]) == sum(Decimal(q[(c, r[2], "own_filing")][7]) for c in PRIMARY) and Decimal(r[5]) == sum(Decimal(q[(c, r[2], "own_filing")][8]) for c in PRIMARY) for r in sm), "")
    ck.eq("banks.csv: 66 period-ends and 65 in own filing for each primary bank and tag, 52 and 51 for State Street", sorted({(r[1], r[5], r[8], r[7]) for r in csv_body(files["banks.csv"])[1] if r[1] in ("JPM", "GS", "STT")}),
          [("GS", "66", "65", "0"), ("JPM", "66", "65", "0"), ("STT", "52", "51", "0")])
    ck.ok("the README states the results with the sign and the label together", "From 31 Dec 2021 to 31 Dec 2023" in files["README.md"] and "yardstick" in files["README.md"], "")
    ck.eq("README.md, SOURCES.md and the tables pass every folder rule", folder_problems(dict(files, **{"captions_pin.csv": real_pins()[0]}), full=True), [])
    ck.ok("SOURCES.md lists the eight requests", files["SOURCES.md"].count("https://data.sec.gov/api/xbrl/companyconcept/") == 8, "")
    ck.ok("no byte of any output holds an address, a local path or the contact string", all("@" not in x and "/Users/" not in x and FIXTURE_CONTACT not in x for x in files.values()), "")
    # M28 on the output: clean folder, then the four planted faults
    m28 = m28_run(w, files)
    ck.eq("M28 prints no cross on the clean folder", m28["clean"], [])
    ck.eq("M28 prints four crosses on the planted copy (a .json, a renamed header, a HELD cell, a changed n_usd)", len(m28["planted"]), 4)


def m28_run(w, files):
    """Run the M28 bash function of bin/check.sh on a copy of the output (clean, then with four planted faults); returns the lines that carry a cross."""
    text = read_file(os.path.join(ROOT, "bin", "check.sh"), "r")
    region = checksh_region(text)
    out = {}
    with tempfile.TemporaryDirectory(prefix="cru_m28_", ignore_cleanup_errors=True) as tmp:
        script = os.path.join(tmp, "m28.sh")
        write_text(script, region + '\nCRU_DIR="$1" CRU_VDIR="$2" cru_leak_check\n')
        for label in ("clean", "planted"):
            d, v = os.path.join(tmp, label, "out"), os.path.join(tmp, label, "vint")
            os.makedirs(d)
            os.makedirs(os.path.join(v, w["v1"]))
            for n, x in files.items():
                write_text(os.path.join(d, n), x)
            write_text(os.path.join(d, "captions_pin.csv"), real_pins()[0])
            write_text(os.path.join(v, w["v1"], "concept_extract.csv"), read_file(os.path.join(w["cache"], w["v1"], "concept_extract.csv"), "r"))
            if label == "planted":
                write_text(os.path.join(d, "raw.json"), "{}")
                write_text(os.path.join(d, "revisions.csv"), read_file(os.path.join(d, "revisions.csv"), "r").replace("rel_diff_pct", "rel_diff", 1))
                write_text(os.path.join(d, "banks.csv"), read_file(os.path.join(d, "banks.csv"), "r").replace("Jpmorgan", "HELD", 1))
                ls = read_file(os.path.join(d, "samples.csv"), "r").splitlines()
                i = next(k for k, l in enumerate(ls) if l.startswith("primary,own_filing,2015-12-31"))
                c = ls[i].split(",")
                c[4] = str(int(c[4]) + 1)
                ls[i] = ",".join(c)
                write_text(os.path.join(d, "samples.csv"), "\n".join(ls) + "\n")
            r = subprocess.run(["bash", script, d, v], capture_output=True, text=True, timeout=120)
            out[label] = [l for l in r.stdout.splitlines() if "✗" in l]
            if label == "clean" and r.stderr.strip():
                out[label].append("stderr: " + r.stderr[:200])
    return out


# ---- the table of guards and the runner ----
GUARDS = [
    ("G1", "parsing (Decimal JSON, values above 2^53, fractions, missing is not zero, USD only, sum not mean of ratios)", ["g1_float_sum", "g1_missing_zero", "g1_nonusd_ok", "g1_float_parse", "g1_mean_ratios"], t_g1),
    ("G2", "calendar quarter-ends (off-calendar ends, none moved, 2010-03-31 absent)", ["g2_month_only", "g2_snap"], t_g2),
    ("G3", "own filing (comparatives, amendments, same accession, 100 and 101 days, fy and fp, Q4, ambiguity, no fill from a later filing)",
     ["g3_comparative_ok", "g3_amend_defines", "g3_two_accn", "g3_days_101", "g3_days_99", "g3_fy_fp_ignored", "g3_q4_unmapped", "g3_two_not_ambiguous", "g3_fill_later"], t_g3),
    ("G4", "latest-filed and revisions (latest, ties, 1.0000% and 1.0001%, regenerated)", ["g4_latest_uses_first", "g4_tie_smallest_accn", "g4_recast_ge", "g4_recast_hi", "g4_revisions_append"], t_g4),
    ("G5", "facts, flags and exclusions (extra key, conflict, 30.0000% and 30.0001%, N = D and N = D + 1, ratio above one, flags exclude nothing)",
     ["g5_extra_key_ok", "g5_conflict_ok", "g5_jump_ge", "g5_jump_hi", "g5_eq_excluded", "g5_ratio_lax", "g5_ratio_in_sample", "g5_flag_excludes"], t_g5),
    ("G6", "units (999,999,999 and 1e9, 1e13 and 1e13 + 1, USDm, two unit keys)", ["g6_lo_lt", "g6_lo_excl", "g6_hi_excl", "g6_hi_lax", "g6_usdm_ok", "g6_two_units_ok"], t_g6),
    ("G7", "aggregation and gaps (one bank, zero, interpolation, previous quarter, State Street dates)", ["g7_one_bank", "g7_missing_zero", "g7_prev_quarter", "g7_interpolate"], t_g7),
    ("G8", "changes and yardstick (q-8 by index, edge quarters, counts 33/31/23 and 25/17, YL edges, no 2026)",
     ["g8_row_pos", "g8_y_lo_in", "g8_y_lo_out", "g8_y_hi_out", "g8_y_hi_in", "g8_yl_lo_in", "g8_yl_lo_out", "g8_yl_hi_out", "g8_yl_hi_in", "g8_2026_in"], t_g8),
    ("G9", "labels, sign and VOID (max and min ties, 1e-9, rounding, 0.0999/0.1000, thin edges, VOID order, S2 exempt)",
     ["g9_max_rise", "g9_eps", "g9_rounded_compare", "g9_sign_strict", "g9_sign_wide", "g9_within_zero_sign", "g9_void_order", "g9_recast_label_written", "g9_caption_label_written", "g9_s2_recast_void"], t_g9),
    ("G10", "registered texts and hashes (4.6, 4.7, 5, caption pin, M28's copy, S3 not in its own yardstick)", ["g10_prereg_edit", "g10_pop_edit", "g10_prereg_drift", "g10_caption_hash", "g10_s3_in_y"], t_g10),
    ("G12", "counts and expected dates (C01, C02)", ["g12_c01_65", "g12_c01_67", "g12_offcal_pass", "g12_c02_2010q1", "g12_c02_2009_own", "g12_c02_missing_pass"], t_g12),
    ("G13", "decomposition (Shapley, sums, weights, mix_dominates)", ["g13_simple", "g13_sum_off", "g13_weights_90", "g13_void_never", "g13_void_always", "g13_void_smaller", "g13_void_vs_within_sign"], t_g13),
    ("G14", "wording (causal, price, speed and misconduct patterns; the one denial sentence; the required README lines)", ["g14_causal_off", "g14_extra_off", "g14_denial_all", "g14_readme_lax"], t_g14),
    ("G15", "STOP latch (planted STOP, statuses, bodies, 404, timeout)", ["g15_stop_ignored", "g15_overwrite", "g15_stop_short", "g15_html_ok", "g15_empty_ok", "g15_nonjson_ok", "g15_3xx_ignored", "g15_404_latches",
                                                                          "g15_stop_on_timeout", "g15_403_ignored"], t_g15),
    ("G16", "fetch safety (hosts, SEC_UA, redirect, retry, 1.0 s gap, cap, cache, the contact string in no byte, one writer of vintages.csv, no fetch_log)",
     ["g16_other_host", "g16_no_ua_ok", "g16_scrub_off", "g16_secret_written", "g16_redirect", "g16_retry", "g16_gap09", "g16_cap_off", "g16_recache", "g16_fetch_log"], t_g16),
    ("G17", "vintages and stages (no mixing, registered once, pre reads no val, dry writes counts only, no default stage, supersede)",
     [("g17_mixed", t_g17_mixed), ("g17_rewrite_registered", t_g17_full), ("g17_pre_reads_val", t_g17_pre), ("g17_dry_writes_values", t_g17_dry), ("g17_dry_writes_registered", t_g17_dry), ("g17_dry_committed", t_g17_dry),
      ("g17_full_default", t_g17_parser), ("g17_supersede_deletes", t_g17_supersede), ("g17_supersede_noversion", t_g17_supersede), ("g16_second_writer", t_g17_full), ("g17_readme_only_writes_all", t_g17_readme_only)], t_g17),
    ("G18", "allowlists and leak (headers, hash, M28's copy, # source:, thirteenth file, keys, paths, tamper)",
     ["g18_extra_col", "g18_renamed", "g18_extra_col_ok", "g18_renamed_ok", "g18_source_as_header", "g18_thirteenth_ok", "g18_dup_ok", "g18_json_ok", "g18_xml_ok", "g18_path_ok", "g18_at_ok", "g18_c05_off", "g18_c08_off",
      "g18_checksh_lax"], t_g18),
    ("G20", "tie-outs (half a unit passes, one unit and 0.6 unit fail, an absent date is reported)", ["g20_one_unit", "g20_wide", "g20_strict", "g20_absent_pass"], t_g20),
    ("G21", "caption change (the window edges, Goldman alone, YR, yardstick_disagrees, the README line)",
     ["g21_start_2016_kept", "g21_end_2016_excluded", "g21_start_2017_excluded", "g21_end_2017_kept", "g21_gs_excluded", "g21_yr_noexcl", "g21_disagree_ok", "g21_disagree_void_same", "g21_readme_no_2017"], t_g21),
    ("X1", "end-to-end build on the synthetic world (fetch, pre, dry, full, reference arithmetic, outputs, M28 on a clean and a planted copy)", [], t_x_build),
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
    bad_total, n_checks, n_mut = 0, 0, 0
    try:
        real_pins()
        base_disk()
        base_texts()
        if only:
            names = {(m if isinstance(m, str) else m[0]) for _, _, ms, _ in GUARDS for m in ms}
            if only not in names:
                print("unknown mutant %r" % only)
                return 2
            with mutant(only):
                for gid, desc, muts, fn in GUARDS:
                    use = dict((m if not isinstance(m, str) else (m, fn)) for m in muts).get(only, fn)
                    ck = run_test(use)
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
            survived = 0
            if mutants:
                for m in muts:
                    name, mfn = (m, fn) if isinstance(m, str) else m
                    with mutant(name):
                        mk = run_test(mfn)
                    caught = bool(mk.failed())
                    n_mut += 1
                    bad_total += 0 if caught else 1
                    survived += 0 if caught else 1
                    print("       mutant %-28s %s%s" % (name, "caught" if caught else "SURVIVED", "  (first failing check: %s)" % mk.failed()[0][0][:70] if caught else ""))
            if not bad and not survived:
                print("       %s caught%s" % (gid, " (%d of %d mutants)" % (len(muts), len(muts)) if muts else " (no mutant: an end-to-end run)"))
        print("live guards: %s (G11 and G19 are withdrawn)" % " ".join(g[0] for g in GUARDS))
        print("selftest: %d guards, %d checks, %d mutants applied one at a time, %d failure(s), %.1f s" % (len(GUARDS), n_checks, n_mut, bad_total, time.time() - t0))
        return 0 if bad_total == 0 else 1
    finally:
        forget_secrets()
        if "td" in _DISK:
            _DISK.pop("td").cleanup()
            _DISK.clear()
        _TEXTS.clear()


if __name__ == "__main__":
    sys.exit(main())
