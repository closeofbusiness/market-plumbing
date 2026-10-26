#!/bin/bash
# Warn (never block) if a draft restates a claim killed in CORRECTIONS.md.
# Usage:  bin/check.sh FILE [FILE...]   |   bin/check.sh --all
#         --goal | --latest | --todo | --handover [write <claude|grok>]
# Exit 0 always. A blocking gate gets reworded around; a warning leaves a trail.
# UTF-8 locale pinned 8 Oct 2026: under the C locale '.' matches one byte, so patterns spanning an en dash or
# a curly quote silently missed (found by a sweep agent; this shell has no LANG set).
export LC_ALL=en_US.UTF-8
# bash 3.2 compatible (macOS default) — no mapfile, no associative arrays.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 0
[ -f CORRECTIONS.md ] || exit 0

# --- GOAL DRIFT CHECK -------------------------------------------------------
# Runs on EVERY invocation, before anything else. On 22 Aug 2026 this project
# served the wrong goal for a day while every document agreed with every other
# document -- nothing was lost, the record was simply wrong. Internal consistency
# cannot detect that. What this check CAN detect is the goal being reworded in one
# place and not another, which is how a corrupted goal starts looking plausible.
# THE_ASK.md is the only source; the other two files must carry it verbatim.
goal_check() {
  [ -f THE_ASK.md ] || { echo "✗ THE_ASK.md missing — the goal has no source of truth."; return 1; }
  local g rc=0
  g=$(awk '/^```goal$/{f=1;next} /^```$/{f=0} f' THE_ASK.md | sed '/^[[:space:]]*$/d')
  if [ -z "$g" ]; then
    echo "✗ THE_ASK.md has no \`\`\`goal block — cannot verify the goal."; return 1
  fi
  if [ "$(printf '%s\n' "$g" | wc -l | tr -d ' ')" != "1" ]; then
    echo "✗ the goal block must be ONE unwrapped line (it is grepped verbatim)."; rc=1
  fi
  for f in CLAUDE.md RESEARCH_STATE.md; do
    [ -f "$f" ] || continue
    if ! grep -qF "$g" "$f"; then
      echo "✗ GOAL DRIFT: $f does not carry the canonical goal string verbatim."
      rc=1
    fi
  done
  if [ "$rc" = 0 ]; then
    echo "✓ goal intact and identical in THE_ASK.md, CLAUDE.md, RESEARCH_STATE.md:"
    printf '    %s\n' "$g"
  else
    echo "  → Fix by copying the \`\`\`goal block from THE_ASK.md verbatim. Do NOT reword it."
    echo "  → If the goal genuinely changed, it needs a new verbatim entry in THE_ASK.md first."
  fi
  return $rc
}

# --- M5: ORPHAN CHECK --------------------------------------------------------
# A top-level doc or subfolder that never appears as a row in CLAUDE.md's read
# table is invisible to every role column -- an agent has no instruction to
# read it at all. Excludes CLAUDE.md itself (it never names itself -- would
# otherwise be a permanent false positive) and checks the READ TABLE
# specifically, not the separate File Structure table (glob patterns, not a
# read order). Folders are checked at folder granularity: one row anywhere
# mentioning the folder is enough -- individual files inside are not enumerated.
orphan_check() {
  echo "-- M5: orphan check (top-level docs/folders absent from CLAUDE.md's read table) --"
  [ -f CLAUDE.md ] || { echo "  ✗ CLAUDE.md missing -- cannot check."; return; }
  local region f d base hits=0
  region=$(awk '/^\| File \| ~tok \|/{f=1} /^A \*\*synthesist\*\*/{f=0} f' CLAUDE.md)
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    base="${f#./}"
    [ "$base" = "CLAUDE.md" ] && continue
    if ! printf '%s\n' "$region" | grep -qF "$base"; then
      echo "  ✗ ORPHAN (file):   $base -- no row in the read table"
      hits=$((hits+1))
    fi
  done <<< "$(find . -mindepth 1 -maxdepth 1 -name '*.md' | sort)"
  while IFS= read -r d; do
    [ -z "$d" ] && continue
    base="${d#./}"
    if ! printf '%s\n' "$region" | grep -qF "$base"; then
      echo "  ✗ ORPHAN (folder): $base/ -- no row in the read table"
      hits=$((hits+1))
    fi
  done <<< "$(find . -mindepth 1 -maxdepth 1 -type d -not -name '.*' | sort)"
  [ "$hits" -eq 0 ] && echo "  ✓ no orphans -- every top-level doc and folder has a read-table row."
}

# --- M6: SECOND-HOME CHECK ---------------------------------------------------
# A numbered list item in RESEARCH_STATE.md section 5 that sits OUTSIDE the
# ```ranked fence is a second hand-written home for ranked status -- exactly
# the drift this project's diagnosis names. Scoped to the ranked-work portion
# of section 5 (from the "## 5." heading to "### Tier O") so Tier O's own,
# unrelated numbered list (a different, pre-existing, legitimate structure,
# out of this run's scope) is not swept in; Tier N's bold **N2. headers never
# match the digit-list pattern, which is what proves the check discriminates
# rather than being vacuously scoped past everything.
secondhome_check() {
  echo "-- M6: second-home check (numbered items in RESEARCH_STATE.md section 5, outside the ranked fence) --"
  [ -f RESEARCH_STATE.md ] || { echo "  ✗ RESEARCH_STATE.md missing -- cannot check."; return; }
  local hits
  hits=$(awk '
    /^## 5\. /{sec=1}
    /^### Tier O/{sec=0}
    /^```/{fence=!fence; next}
    sec && !fence && /^[0-9]+\. / {print "  ✗ RESEARCH_STATE.md:"NR"  "substr($0,1,110)}
  ' RESEARCH_STATE.md)
  if [ -z "$hits" ]; then
    echo "  ✓ no numbered list items found outside the ranked fence."
  else
    printf '%s\n' "$hits"
    echo "  -> fold into the ranked fence or delete; a second hand-written home is how status drifts."
  fi
}

# --- M7: UNREGISTERED-CORRECTION CHECK ---------------------------------------
# A [C-NNN] banner struck into a findings doc but never given a "## C-NNN"
# heading in CORRECTIONS.md is a correction applied and then invisible to the
# ban list forever -- the five-to-six-bank error (C-075) sat exactly like this
# before this run. Limit, stated plainly: this can only catch a banner that
# exists; it cannot catch a correction that was folded in with no banner at all.
unregistered_correction_check() {
  echo "-- M7: unregistered-correction check ([C-NNN] banners absent from CORRECTIONS.md) --"
  [ -f CORRECTIONS.md ] || { echo "  ✗ CORRECTIONS.md missing -- cannot check."; return; }
  local f ln id hits=0
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    while IFS=: read -r ln id; do
      [ -z "${ln:-}" ] && continue
      id="${id#\[}"
      if ! grep -qE "^## ${id}([^0-9]|\$)" CORRECTIONS.md; then
        echo "  ✗ ${f#./}:${ln}  banner [$id] has no matching heading in CORRECTIONS.md"
        hits=$((hits+1))
      fi
    done <<< "$(grep -noE '\[C-[0-9]+' "$f" 2>/dev/null)"
  done <<< "$FILELIST"
  [ "$hits" -eq 0 ] && echo "  ✓ every [C-NNN] banner found has a matching CORRECTIONS.md heading."
}

# --- M8: DUPLICATE CORRECTION-NUMBER CHECK -----------------------------------
# Two agents work this folder now (E-006), never at the same time, but with no
# version control between them. M7 asks whether a banner has a heading; it never
# asks whether that heading is UNIQUE. Two agents minting C-087 for different
# things both pass M7, the register quietly holds two claims under one id, and
# the ban list then enforces whichever one grep reaches first.
duplicate_correction_check() {
  echo "-- M8: duplicate correction-number check (two headings sharing one C-NNN) --"
  [ -f CORRECTIONS.md ] || { echo "  ✗ CORRECTIONS.md missing -- cannot check."; return; }
  local dupes
  dupes=$(grep -oE '^## C-[0-9]+' CORRECTIONS.md | sort | uniq -d)
  if [ -n "$dupes" ]; then
    printf '%s\n' "$dupes" | sed 's/^## /  ✗ /;s/$/ appears more than once -- renumber the later one and fix its banners./'
  else
    echo "  ✓ every correction number is used once."
  fi
}

# --- M9: SWAP-TAPE LEAK GUARD (warn only) -----------------------------------
# data/swap_tape/ may hold only statistics derived from DTCC's public price dissemination, never a DTCC record (THE_ASK.md E-024:
# "no raw DTCC file or row is committed or redistributed"). Two things would break that, and neither is visible to M5-M8:
#   1. an output field that is a whole string of 8-19 digits -- a Dissemination Identifier (19 digits; the legacy ids had 8-18);
#      the anchors make the digits a whole CSV field, so a date, a count or a hash does not match;
#   2. a DTCC zip or CSV (CFTC_CUMULATIVE_*, *.zip) among the files of the folder. `git ls-files -co` lists tracked AND untracked
#      files (-o without --exclude-standard also lists ignored ones), so a zip dropped in before `git add` is caught too.
# The script's own writers refuse such fields; this is the second, independent look. It warns and never blocks (header doctrine).
swaptape_leak_check() {
  echo "-- M9: swap-tape leak guard (DTCC identifiers or zips under data/swap_tape/) --"
  [ -d data/swap_tape ] || { echo "  ✓ data/swap_tape/ is absent -- nothing to leak."; return; }
  local ids files
  ids=$(grep -rEn '(^|,)[0-9]{8,19}(,|$)' data/swap_tape/ 2>/dev/null | cut -c1-110)
  files=$( { git ls-files -co data/swap_tape 2>/dev/null || find data/swap_tape -type f; } | grep -iE 'CFTC_CUMULATIVE|\.zip$' )
  if [ -z "$ids" ] && [ -z "$files" ]; then
    echo "  ✓ no 8-19 digit field and no CFTC_CUMULATIVE or .zip file under data/swap_tape/."
  else
    [ -n "$ids" ] && printf '%s\n' "$ids" | sed 's/^/  ✗ digit field (a Dissemination Identifier?): /'
    [ -n "$files" ] && printf '%s\n' "$files" | sed 's/^/  ✗ DTCC file or zip: /'
    echo "  -> a DTCC record must never be committed (E-024). Remove it before any commit; if it already left this folder, tell the principal."
  fi
}

# --- M10: USER-AGENT CHECK (warn only) ---------------------------------------
# CLAUDE.md (ruled 12 Sep): sec.gov hosts get the declared contact, read from the SEC_UA environment variable and
# never written into a file; every other host gets ONE neutral string with no address. On 15 Oct bin/ was found
# sending four other neutral strings beside it (pull_series.py had also sent SEC_UA to every host until 8 Oct), and
# nothing in M5-M9 could see either drift. This takes every line of bin/*.py holding a User-Agent literal -- a string
# set as a User-Agent header, assigned to a *UA / USER_AGENT name, or carrying a browser or tool token -- and warns on
#   1. a literal that is not the canonical string. Lines reading SEC_UA from os.environ are the one exemption;
#   2. any '@' on a line that touches a User-Agent, the SEC_UA lines included. Addresses at example.com, .org and
#      .net are reserved for documentation (RFC 2606) and pass: the SEC_UA error messages quote one as the format
#      to follow. A flagged line is located (file:line) and its text is never printed.
# The canonical string is copied from CLAUDE.md, so the first test is that CLAUDE.md still carries it verbatim.
# Limit, stated plainly: grep sees literals only. A request sent with no User-Agent at all (urllib then sends
# Python-urllib) or with a string built at run time is invisible here.
ua_check() {
  echo "-- M10: user-agent check (bin/*.py: CLAUDE.md's neutral string off sec.gov, SEC_UA on it, no address) --"
  local canon='Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)'
  local q="[\"']" rx crx bad addr
  rx="Mozilla/[0-9]|ThirdDerivativeResearch|AppleWebKit|Chrome/[0-9]|Firefox/[0-9]|curl/[0-9]|Wget/|python-requests|Python-urllib|--user-agent"
  rx="$rx|[Uu]ser-[Aa]gent${q}?[[:space:]]*[:,][[:space:]]*[rbuRBU]?${q}"
  rx="$rx|(^|[^A-Za-z0-9_])([A-Z_]*UA|ua|USER_AGENT[A-Z_]*|user_agent)[[:space:]]*=[[:space:]]*[(]?[[:space:]]*[rbuRBU]?${q}"
  crx=$(printf '%s' "$canon" | sed 's/[.()]/\\&/g')
  grep -qF "$canon" CLAUDE.md 2>/dev/null \
    || echo "  ✗ CLAUDE.md no longer carries the string this check enforces -- copy CLAUDE.md's into ua_check(); do not reword it."
  # 1. drop the SEC_UA lines, blank out the canonical string and its quotes; whatever still matches is another literal
  bad=$(grep -nE -e "$rx" bin/*.py 2>/dev/null | grep -vE 'SEC_UA.*os[.]environ|os[.]environ.*SEC_UA' \
        | sed -E "s#${q}?${crx}${q}?#CANON#g" | grep -E -e "$rx" \
        | sed -E "s#[^[:space:]\"']+@[^[:space:]\"']+#<address>#g" | sort -t: -k1,1 -k2,2n | cut -c1-140)
  # 2. every line that matched above or names a User-Agent or SEC_UA; documentation addresses removed first
  addr=$(grep -nE -e "$rx|[Uu]ser[-_][Aa]gent|USER_AGENT|SEC_UA" bin/*.py 2>/dev/null \
        | sed -E 's/[A-Za-z0-9._%+-]+@example[.](com|org|net)//g' | grep -F '@' | cut -d: -f1,2 | sort -t: -k1,1 -k2,2n)
  if [ -z "$bad" ] && [ -z "$addr" ]; then
    echo "  ✓ every User-Agent literal in bin/*.py is the CLAUDE.md string or reads SEC_UA; no '@' on any User-Agent line."
  else
    [ -n "$bad" ] && printf '%s\n' "$bad" | sed 's/^/  ✗ not the CLAUDE.md string: /'
    [ -n "$addr" ] && printf '%s\n' "$addr" | sed "s/^/  ✗ '@' on a User-Agent line (text not printed): /"
    echo "  -> non-sec.gov hosts get CLAUDE.md's string, defined once per script; sec.gov reads os.environ[\"SEC_UA\"]; no address in any file."
  fi
}

# --- M11: ICE BRENT LEAK GUARD (warn only) ----------------------------------
# data/ice_brent/ may hold only statistics derived from ICE Futures Europe's Brent Commitments-of-Traders files, never an ICE file or a gross
# position column (THE_ASK.md E-025, which extends E-024: "no raw ICE file or row is committed or redistributed"). Three things would break that,
# and none is visible to M5-M9:
#   1. a COTHist* file anywhere in the repository, in any letter case (COTHist2026.csv, cothist2026.csv, COTHIST2026.CSV). `git ls-files -co`
#      lists tracked AND untracked files (-o without --exclude-standard also lists ignored ones), so a file dropped in before `git add`, or one
#      the .gitignore rule hides, is caught too;
#   2. ICE's header line, Market_and_Exchange_Names,As_of_Date_In_Form_YYMMDD, inside any tracked or untracked file outside bin/ and _research/
#      (a COTHist file renamed, saved as .txt or pasted into a note). bin/ holds this script and the ICE parser, and _research/ the spec; both
#      name the columns, so they are left out;
#   3. a header cell in a data/ice_brent/*.csv (and, since the COT horizons build, data/cot_horizons/*.csv, top level only) that names a gross column: the word long, short, spread, spreading or gross, the string
#      open_interest, or the word oi outside pct_oi. bin/pull_ice_brent_cot.py refuses any header that is not on its exact allowlist; this is
#      the second, independent look, and it reads the files as committed.
# It warns and never blocks (header doctrine). (Numbered M11 because another session landed an M10, the User-Agent check, upstream.)
icebrent_leak_check() {
  echo "-- M11: ICE Brent leak guard (COTHist files in any letter case; ICE's header line outside bin/ and _research/; gross column names in data/ice_brent/ and data/cot_horizons/ headers) --"
  local files sig sigfiles names f hit
  files=$( { git ls-files -co 2>/dev/null || find . -type f | sed 's|^\./||'; } | grep -Ei '(^|/)cothist[^/]*$' )
  sig='Market_and_Exchange_Names,As_of_Date_In_Form_YYMMDD'
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    sigfiles=$(git grep -I --untracked -l -F -e "$sig" -- . ':(exclude)bin' ':(exclude)_research' 2>/dev/null)
  else
    sigfiles=$(grep -rIlF -e "$sig" --exclude-dir=.git --exclude-dir=bin --exclude-dir=_research . 2>/dev/null | sed 's|^\./||')
  fi
  names=""
  # data/cot_horizons/ (bin/cot_horizons.py) carries Brent figures too, so its top-level tables get the same header look (top level only, warn-only)
  for f in data/ice_brent/*.csv data/cot_horizons/*.csv; do
    [ -f "$f" ] || continue
    hit=$(grep -v '^#' "$f" | head -1 | tr -d '\r' | awk -F, '{ n = split(tolower($0), h, ",");
      for (i = 1; i <= n; i++) { c = h[i];
        if (c ~ /(^|_)(long|short|spread|spreading|gross)(_|$)/ || c ~ /open_interest/ || (c ~ /(^|_)oi(_|$)/ && c !~ /pct_oi/)) print c } }')
    [ -n "$hit" ] && names="${names}${f}: $(printf '%s' "$hit" | tr '\n' ' ')
"
  done
  # data/cot_horizons/ may hold only the published files (bin/cot_horizons.py, guard G24), and no csv there may have a header cell containing "fut"
  # (the local weekly futures panel must never be copied in)
  local stray="" futh="" rel
  if [ -d data/cot_horizons ]; then
    while IFS= read -r f; do
      rel=${f#data/cot_horizons/}
      case "$rel" in
        primary.csv|descriptive.csv|plot26.csv|weekly_panel.csv|release_dates.csv|roll_calendar.csv|checks.csv|fetch_log.csv|README.md|SOURCES.md) ;;
        raw/cftc_disagg_futonly_72hh-3qpy_067651.json|raw/cftc_disagg_combined_kh3c-gbw2_067651.json|raw/cftc_release_schedule.html) ;;
        raw/cftc_special_announcements.html|raw/cftc_press_release_7864-19.html|raw/gov_uk_bank_holidays.json) ;;
        *) stray="${stray}${f}
" ;;
      esac
      case "$f" in
        *.csv) grep -v '^#' "$f" | head -1 | tr -d '\r' | tr 'A-Z' 'a-z' | grep -q 'fut' && futh="${futh}${f}
" ;;
      esac
    done <<EOF
$(find data/cot_horizons -type f ! -name '.DS_Store' | sort)
EOF
  fi
  if [ -z "$files" ] && [ -z "$sigfiles" ] && [ -z "$names" ] && [ -z "$stray" ] && [ -z "$futh" ]; then
    echo "  ✓ no COTHist file in the repository (any letter case), no ICE header line outside bin/ and _research/, no gross column name in a data/ice_brent/ or data/cot_horizons/ header, nothing unexpected in data/cot_horizons/."
  else
    [ -n "$files" ] && printf '%s\n' "$files" | sed 's/^/  ✗ ICE file in the repository: /'
    [ -n "$sigfiles" ] && printf '%s\n' "$sigfiles" | sed 's/^/  ✗ ICE header line in a file (a COTHist file renamed or pasted?): /'
    [ -n "$names" ] && printf '%s' "$names" | sed 's/^/  ✗ gross column name in header: /'
    [ -n "$stray" ] && printf '%s' "$stray" | sed 's/^/  ✗ unexpected file in data\/cot_horizons: /'
    [ -n "$futh" ] && printf '%s' "$futh" | sed 's/^/  ✗ header containing "fut" (a futures panel copied in?): /'
    echo "  -> an ICE record must never be committed (E-025). Remove it before any commit; if it already left this folder, tell the principal."
  fi
}

# --- M12: R15 YIELD-COMOVEMENT LEAK GUARD (warn only) -----------------------
# data/r15_yield_comovement/ may hold only statistics derived from the US Treasury, Bundesbank, Bank of England, MoF Japan and ECB yield files
# (spec _research/2026-10-18-Yield-Comovement-Four-Country-Spec.md, 8.9). The Bundesbank's and the Bank of England's terms do not allow redistributing
# their series, so the raw files live in ~/r15_yield_cache/, outside the repository. Two things would break that, and none is visible to M5-M11:
#   1. a raw source file anywhere in the repository, in any letter case: glc*.zip (the BoE archive), latest-yield-curve-data.zip, jgbcme*.csv
#      (MoF) or anything with BBSIS in its name (Bundesbank). `git ls-files -co` lists tracked AND untracked files (and ignored ones, since -o is
#      used without --exclude-standard), so a file dropped in before `git add`, or one the .gitignore pattern hides, is caught too;
#   2. a header line in a data/r15_yield_comovement/*.csv that is not that file's exact column allowlist (a weekly panel, or a level column,
#      would show up as a different header). bin/r15_yield_comovement.py refuses to write such a header and runs the same test (leak_guard).
# The allowlists below are a second, independent copy of the script's ALLOW table (that is the point). It warns and never blocks (header doctrine).
r15_leak_check() {
  echo "-- M12: R15 yield-comovement leak guard (raw BoE/MoF/Bundesbank files in any letter case; every data/r15_yield_comovement CSV header equals its allowlist) --"
  local files badhdr f name hdr allow
  files=$( { git ls-files -co 2>/dev/null || find . -type f | sed 's|^\./||'; } | grep -Ei '(^|/)(glc[^/]*\.zip|latest-yield-curve-data\.zip|jgbcme[^/]*\.csv|[^/]*BBSIS[^/]*)$' | grep -v '^data/vintages/r3/' )
  # data/vintages/r3/jgbcme*.csv were committed by the R3 build (27 Sep); MoF publishes them under PDL1.0, which allows
  # redistribution with attribution, so they are exempt. The r15 build keeps its own copies in ~/r15_yield_cache/ all the same.
  badhdr=""
  for f in data/r15_yield_comovement/*.csv; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    hdr=$(grep -v '^#' "$f" | head -1 | tr -d '\r')
    case "$name" in
    windows.csv) allow='window,series_set,k,asof,first_week,last_week,weeks_calendar,weeks_used,dropped_gap,dropped_missing,lambda1,lambda1_share,rho_mean,rho_min,rho_max,share_ci95_lo,share_ci95_hi,block_len,boot_draws,status' ;;
    pairs.csv) allow='window,series_set,pair,n,rho,ci95_lo,ci95_hi' ;;
    shift_test.csv) allow='comparison,role,statistic,series_set,window_from,window_to,value_from,value_to,delta,boot_sd,placebo_sd,placebo_layouts,boot_sd_used,calibration,inflation_k,ci95_lo,ci95_hi,ci90_lo,ci90_hi,block_len,boot_draws,verdict,downgrade_reasons' ;;
    series_stats.csv) allow='window,series,n_changes,sd_bp,dropped_gap,missing_weeks' ;;
    freshness.csv) allow='source,series,last_obs,asof,lag_bdays,max_lag_bdays,status,seam,seam_status' ;;
    checks.csv) allow='check_id,description,pin_date,expected,observed,status' ;;
    fetch_log.csv) allow='utc,host,path,status,bytes,sha256,note' ;;
    *) allow='' ;;
    esac
    [ "$hdr" = "$allow" ] || badhdr="${badhdr}${f}
"
  done
  if [ -z "$files" ] && [ -z "$badhdr" ]; then
    echo "  ✓ no raw BoE, MoF or Bundesbank file in the repository; every data/r15_yield_comovement CSV header is its exact allowlist."
  else
    [ -n "$files" ] && printf '%s\n' "$files" | sed 's/^/  ✗ raw source file in the repository: /'
    [ -n "$badhdr" ] && printf '%s' "$badhdr" | sed 's/^/  ✗ header outside the allowlist: /'
    echo "  -> raw yield files stay in ~/r15_yield_cache/ and are never committed (R1). Remove it before any commit; if it already left this folder, tell the principal."
  fi
}

# --- M13: GOLD REAL-YIELD LEAK GUARD (warn only) -----------------------------
# data/gold_real_yield/ may hold derived statistics only: the World Bank Pink Sheet gold price is never redistributed (E-021 item 5; spec R1).
# bin/gold_real_yield_break.py enforces this when it writes (exact column allowlists, K08), and refuses a cache inside the repository; this is the
# second, independent look, and it reads the files as committed. It warns on
#   1. a World Bank workbook (CMO-Historical-Data-Monthly*, any case) anywhere in the repository (tracked, untracked or ignored), or any
#      .xlsx/.xls/.zip under data/gold_real_yield/;
#   2. a file under data/gold_real_yield/ that is not one of the thirteen allowed names (the eleven outputs, README.md, SOURCES.md);
#   3. a CSV whose header line is not exactly that file's allowlist, or whose header names gold, ln_g, dln, fitted, price or resid_ (the three
#      exempt names resid_sd_in_sample, resid_var_regime1 and resid_var_regime2 apart);
#   4. a rolling36.csv beta_ry, boot_lo or boot_hi cell with more than two decimals (the one per-month exception, published at 2 dp).
# It warns and never blocks (header doctrine).
goldry_leak_check() {
  echo "-- M13: gold real-yield leak guard (no CMO workbook or spreadsheet; file and header allowlists; rolling36.csv at most 2 decimals) --"
  local d=data/gold_real_yield out="" f b want hdr bad
  local cmo
  cmo=$( { git ls-files -co 2>/dev/null || find . -type f | sed 's|^\./||'; } | grep -Ei '(^|/)cmo-historical[^/]*$' )
  [ -n "$cmo" ] && out="${out}$(printf '%s\n' "$cmo" | sed 's/^/  ✗ World Bank workbook in the repository: /')
"
  if [ -d "$d" ]; then
    for f in "$d"/* "$d"/.[!.]*; do
      [ -e "$f" ] || continue
      b=$(basename "$f")
      case "$b" in
        monthly_inputs.csv|results.csv|cointegration.csv|break.csv|chow_known_dates.csv|rolling36.csv|rolling36.svg|levels_summary.csv|checks.csv|vintages.csv|fetch_log.csv|README.md|SOURCES.md) ;;
        *) out="${out}  ✗ file not on the allowlist: $f
" ;;
      esac
      case "$b" in *.xlsx|*.xls|*.zip|*.XLSX|*.XLS|*.ZIP) out="${out}  ✗ spreadsheet or zip under $d: $f
" ;; esac
      case "$b" in
      monthly_inputs.csv) want='month,tips10_avg_pct_mc,tips10_avg_pct_official,tips10_days,tips10_mc_day_share,usd_broad_2006jan100,seam_flag' ;;
      results.csv) want='object_id,role,sample_start,sample_end,n,regressors,coef_name,coef,coef_unit,pct_approx,pct_exact,se_classical,se_hac,hac_lag,hac_lag_rule,crit_value,crit_basis,ci_level,ci_low,ci_high,r2,mde80,flag,verdict' ;;
      cointegration.csv) want='test_id,role,sample_start,sample_end,T,adf_lags,adf_stat,cv_5pct,reject_5pct,levels_printed' ;;
      break.csv) want='trim,dummy_spec,first_candidate,last_candidate,n_candidates,sup_wald,p_value_boot,boot_draws,boot_mean_block,andrews_cv10,andrews_cv5,andrews_cv1,break_month_ssr,break_month_supwald,bai_ci_low,bai_ci_high,bai_halfwidth_months,ci_clipped,s_min_h4,s_min_h6,s_min_h8,s_min_h12,s_min_h18,resid_var_regime1,resid_var_regime2,hac_lag' ;;
      chow_known_dates.csv) want='regime2_start,wald_hac,df,p_chi2,hac_lag,role' ;;
      rolling36.csv) want='end_month,n,beta_ry,boot_lo,boot_hi,block_len,draws,seed' ;;
      levels_summary.csv) want='object_id,fit_start,fit_end,coef_name,coef,ci_low,ci_high,hac_lag,resid_sd_in_sample,residual_label,status' ;;
      checks.csv) want='check_id,description,expected,observed,status' ;;
      vintages.csv) want='source,file,retrieved_utc,sha256,bytes,published_updated_on,last_obs' ;;
      fetch_log.csv) want='utc,host,path,status,bytes,sha256,outcome' ;;
      *) want="" ;;
      esac
      [ -f "$f" ] || continue
      case "$b" in
      *.csv)
        hdr=$(grep -v '^#' "$f" | head -1 | tr -d '\r')
        [ -n "$want" ] && [ "$hdr" != "$want" ] && out="${out}  ✗ header differs from the allowlist: $f
"
        bad=$(printf '%s' "$hdr" | tr ',' '\n' | grep -Ei 'gold|ln_g|dln|fitted|price|^resid_' | grep -vxE 'resid_sd_in_sample|resid_var_regime1|resid_var_regime2')
        [ -n "$bad" ] && out="${out}  ✗ banned name in header of $f: $(printf '%s' "$bad" | tr '\n' ' ')
"
        ;;
      esac
    done
    if [ -f "$d/rolling36.csv" ]; then
      bad=$(grep -v '^#' "$d/rolling36.csv" | tail -n +2 | awk -F, '{ for (i = 3; i <= 5; i++) if ($i ~ /\.[0-9][0-9][0-9]/) { print NR ": " $i; break } }' | head -3)
      [ -n "$bad" ] && out="${out}  ✗ rolling36.csv has more than 2 decimals (row: value): $(printf '%s' "$bad" | tr '\n' ' ')
"
    fi
  fi
  if [ -z "$out" ]; then
    echo "  ✓ no World Bank workbook or spreadsheet; only the thirteen allowed files, each CSV on its exact header; rolling36.csv at most 2 decimals."
  else
    printf '%s' "$out"
    echo "  -> the gold price must never be committed (World Bank terms; spec R1). Remove it before any commit."
  fi
}

# --- M14: JODI LEAK GUARD (warn only) ---------------------------------------
# data/jodi_oil/ may hold only statistics derived from the JODI-Oil World Database, never a JODI file or a table that lets a reader rebuild JODI's
# country-by-month table (JODI: "All such rights are reserved"; spec _research/2026-10-18-JODI-World-Oil-Ledger-Spec.md, R1 and R6). Three things
# would break that, and none is visible to M5-M11:
#   1. a JODI annual file anywhere in the repository, by name: jodi_primary_*, primaryyear* or secondaryyear*, in any letter case. `git ls-files -co`
#      lists tracked AND untracked files (-o without --exclude-standard also lists ignored ones), so a file dropped in before `git add`, or one the
#      .gitignore rule hides, is caught too;
#   2. a file whose FIRST line is JODI's CSV header (REF_AREA, TIME_PERIOD, ENERGY_PRODUCT, ...) -- a JODI file renamed or saved as .txt. bin/ and _research/
#      name the header in the script and the spec, so they are left out;
#   3. a header cell set in a data/jodi_oil/*.csv (other than checkpoints.csv, whose rows are the fixed list of at most 30) that has ref_area together with
#      month, period, time_period or date as a whole word. bin/build_jodi_oil_ledger.py refuses any header that is not on its exact allowlist; this is
#      the second, independent look, and it reads the files as committed. (months_usable and months_in_window are not the word month.)
# It warns and never blocks (header doctrine).
jodi_leak_check() {
  echo "-- M14: JODI leak guard (JODI annual files by name; JODI's header as a first line outside bin/ and _research/; ref_area beside a time column in data/jodi_oil/ headers) --"
  local files sigfiles hits names f hit hdr
  hdr='REF_AREA,TIME_PERIOD,ENERGY_PRODUCT,FLOW_BREAKDOWN,UNIT_MEASURE,OBS_VALUE,ASSESSMENT_CODE'
  files=$( { git ls-files -co 2>/dev/null || find . -type f | sed 's|^\./||'; } | grep -Ei '(^|/)(jodi_primary_|primaryyear|secondaryyear)[^/]*$' )
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    sigfiles=$(git grep -I --untracked -l -F -e "$hdr" -- . ':(exclude)bin' ':(exclude)_research' 2>/dev/null)
  else
    sigfiles=$(grep -rIlF -e "$hdr" --exclude-dir=.git --exclude-dir=bin --exclude-dir=_research . 2>/dev/null | sed 's|^\./||')
  fi
  hits=""
  for f in $sigfiles; do
    [ "$(head -1 "$f" 2>/dev/null | tr -d '\r')" = "$hdr" ] && hits="${hits}${f}
"
  done
  names=""
  if [ -d data/jodi_oil ]; then
    for f in data/jodi_oil/*.csv; do
      [ -f "$f" ] || continue
      [ "$(basename "$f")" = "checkpoints.csv" ] && continue
      hit=$(grep -v '^#' "$f" | head -1 | tr -d '\r' | awk -F, '{ n = split(tolower($0), h, ","); a = 0; t = 0; w = "";
        for (i = 1; i <= n; i++) { c = h[i];
          if (c ~ /(^|_)ref_area(_|$)/) a = 1;
          if (c ~ /(^|_)(month|period|time_period|date)(_|$)/) { t = 1; w = w " " c } }
        if (a && t) print "ref_area with" w }')
      [ -n "$hit" ] && names="${names}${f}: ${hit}
"
    done
  fi
  if [ -z "$files" ] && [ -z "$hits" ] && [ -z "$names" ]; then
    echo "  ✓ no JODI annual file in the repository (by name), no file starting with JODI's header outside bin/ and _research/, no ref_area-plus-time header in data/jodi_oil/."
  else
    [ -n "$files" ] && printf '%s\n' "$files" | sed 's/^/  ✗ JODI file in the repository: /'
    [ -n "$hits" ] && printf '%s' "$hits" | sed 's/^/  ✗ file whose first line is JODI'"'"'s header: /'
    [ -n "$names" ] && printf '%s' "$names" | sed 's/^/  ✗ country-by-time header: /'
    echo "  -> a JODI file or a rebuildable country table must never be committed (JODI reserves all rights). Remove it before any commit; if it already left this folder, tell the principal."
  fi
}

# --- M15: FX-HEDGED TREASURY YIELD LEAK GUARD (warn only) ---------------------
# data/hedged_ust_yield/ may hold only derived statistics. The Bank of Japan's terms keep monthly yen figures out (spec
# _research/2026-10-19-FX-Hedged-Treasury-Yield-Spec.md, section 7 and ruling O-1), and the raw downloads, the daily panel and the yen monthly rows
# stay in the gitignored cache data/vintages/hedged_ust_yield/. Four things would break that, and none is visible to M5-M14:
#   1. a yen row in monthly.csv (the committed monthly file is euro only);
#   2. yen_summary.csv with more than 8 values for one (variant, statistic) -- annual means and two anchor months are the accepted granularity;
#   3. a header line in one of the committed CSVs that is not that file's exact column allowlist (the spec's lists, typed here a second time);
#   4. a file in the folder that is not one of the nine committed names: a raw input (tsy_*, mof_*, nyfed_*, ecb_*, boj_*, dks*, bbk_*), the daily
#      panel or the full monthly table. The _FAILED folder is gitignored and is not scanned.
# bin/hedged_ust_yield.py refuses the same things when it writes (leak_guard); this is the second, independent look. HEDGED_DIR overrides the folder
# (used to show that the guard fires on a planted row). It warns and never blocks (header doctrine).
hedged_leak_check() {
  echo "-- M15: hedged-yield leak guard (data/hedged_ust_yield/: no yen row in monthly.csv, yen_summary.csv within its cap, exact headers, no raw input file) --"
  local dir="${HEDGED_DIR:-data/hedged_ust_yield}" f name want got bad="" extra yen cap
  [ -d "$dir" ] || { echo "  ✓ $dir is absent -- nothing to leak."; return; }
  for name in monthly.csv yen_summary.csv summary.csv references.csv checks.csv pins.csv fetch_log.csv; do
    f="$dir/$name"
    [ -f "$f" ] || continue
    case "$name" in
      monthly.csv) want='month,pair,variant,role,n_days,partial,qe_turn_early,ust10_pct,home10_pct,rate_gap_term_pp,basis_term_pp,hedged_carry_pct,pickup_pp,form_gap_bp,basis_tenor,hedge_days_mean,n_ois_us,n_ois_home,n_basis' ;;
      yen_summary.csv) want='period,variant,statistic,value,credit' ;;
      summary.csv) want='run_label,L,question,pair,variant,statistic,value,notable' ;;
      references.csv) want='ref_id,source,ref_date,pair,form,tenor,published,rounding_bp,build_value,gap_bp,tolerance,status,note' ;;
      checks.csv) want='check_id,description,expected,observed,status' ;;
      pins.csv) want='source,series,pin_date,value,unit' ;;
      fetch_log.csv) want='utc_time,host,path,status,bytes,sha256' ;;
    esac
    got=$(grep -v '^#' "$f" | head -1 | tr -d '\r')
    [ "$got" = "$want" ] || bad="${bad}  ✗ header of $name is not its exact allowlist
"
  done
  if [ -f "$dir/monthly.csv" ]; then
    yen=$(grep -v '^#' "$dir/monthly.csv" | awk -F, 'NR > 1 && $2 == "yen" { n++ } END { if (n) print n }')
    [ -n "$yen" ] && bad="${bad}  ✗ monthly.csv holds $yen yen row(s)
"
  fi
  if [ -f "$dir/yen_summary.csv" ]; then
    cap=$(grep -v '^#' "$dir/yen_summary.csv" | awk -F, 'NR > 1 { k = $2 "|" $3; n[k]++ } END { for (k in n) if (n[k] > 8) print k " = " n[k] }')
    [ -n "$cap" ] && bad="${bad}$(printf '%s\n' "$cap" | sed 's/^/  ✗ yen_summary.csv has more than 8 values for /')
"
  fi
  extra=$(find "$dir" -maxdepth 1 -type f ! -name '.DS_Store' ! -name README.md ! -name SOURCES.md ! -name monthly.csv ! -name yen_summary.csv ! -name summary.csv \
            ! -name references.csv ! -name checks.csv ! -name pins.csv ! -name fetch_log.csv | sort)
  [ -n "$extra" ] && bad="${bad}$(printf '%s\n' "$extra" | sed 's/^/  ✗ file that is not one of the nine committed names: /')
"
  if [ -z "$bad" ]; then
    echo "  ✓ no yen row in monthly.csv, yen_summary.csv within 8 values per variant and statistic, every header its exact allowlist, no raw input file in $dir."
  else
    printf '%s' "$bad"
    echo "  -> Bank of Japan terms: no monthly yen series may be committed; raw inputs and the daily panel stay in data/vintages/hedged_ust_yield/. Remove it before any commit."
  fi
}

# --- M18: JAPANESE LIFE-INSURER FOREIGN-BOND LEAK GUARD (warn only) -----------
# data/jp_life_foreign_bonds/ may hold only the derived tables and the two generated texts (spec _research/2026-10-19-JP-Life-Insurers-Foreign-Bonds-Spec.md,
# sections 2.6 and 6; named M16 there, M18 here because parallel builds took M16 and M17). The raw MoF files and the Bank of Japan PDFs stay in the
# gitignored cache data/vintages/jp_life_foreign_bonds/. Four things would break that, and none is visible to M5-M15:
#   1. a file in the folder that is not one of the 12 committed names -- a raw monthb1-b4.csv (its second line is a MoF title), a PDF, a scratch file;
#   2. a committed CSV whose header (the first line that does not start with #) is not that file's exact column allowlist (the spec's lists, typed here
#      a third time, after ALLOW and SPEC_ALLOW in bin/jp_life_foreign_bonds.py);
#   3. a committed file with a MoF title as its second line (a raw file under a committed name) or a PDF signature;
#   4. a local path (/Users/ or /private/tmp) or an at sign in any committed file.
# bin/jp_life_foreign_bonds.py refuses the same things when it writes (G17); this is the second, independent look. JPLIFE_DIR overrides the folder (used
# to show that the guard fires on planted files). It warns and never blocks (header doctrine).
jp_life_leak_check() {
  echo "-- M18: Japanese life-insurer bond leak guard (data/jp_life_foreign_bonds/: 12 committed names, exact headers, no raw MoF file or PDF, no local path, no at sign) --"
  local dir="${JPLIFE_DIR:-data/jp_life_foreign_bonds}" f name want got bad="" committed raw
  [ -d "$dir" ] || { echo "  ✓ $dir is absent -- nothing to leak."; return; }
  committed=" README.md SOURCES.md monthly.csv annual.csv boj_dates.csv questions.csv forecast_score.csv vintages.csv revisions.csv checks.csv pins.csv fetch_log.csv "
  for f in "$dir"/*; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    raw=""
    case "$name" in *.csv) sed -n 2p "$f" | grep -qF 'Purchases and Sales of Foreign Securities' && raw=1 ;; esac
    head -c 4 "$f" | grep -qF '%PDF' && raw=pdf
    if [ -n "$raw" ]; then
      bad="${bad}  ✗ raw input file ($name): a MoF CSV or a PDF must stay in the cache
"
    elif [ "${committed#* $name }" = "$committed" ]; then
      bad="${bad}  ✗ file that is not one of the 12 committed names: $name
"
    fi
    grep -qE '/Users/|/private/tmp' "$f" && bad="${bad}  ✗ $name contains a local path (/Users/ or /private/tmp)
"
    grep -qF '@' "$f" && bad="${bad}  ✗ $name contains an at sign
"
    want=""
    case "$name" in
      monthly.csv) want='month,instrument,sector,acquisition_100m_yen,disposal_100m_yen,net_100m_yen,basis' ;;
      annual.csv) want='period_type,period,basis,instrument,sector,months,acquisition_100m_yen,disposal_100m_yen,net_100m_yen,file_total_net_100m_yen,diff_100m_yen' ;;
      boj_dates.csv) want='decision_date,effective_date,month,action,phrase,url,sha256' ;;
      questions.csv) want='run_label,question,window,instrument,sector,statistic,value,unit,denominator,notable' ;;
      forecast_score.csv) want='registered_on,target_month,vintage_final_update,vintage_sha256,point_100m_yen,low_100m_yen,high_100m_yen,print_100m_yen,status,of_record,band_recomputed_low,band_recomputed_point,band_recomputed_high,note' ;;
      vintages.csv) want='file,final_update,retrieved_utc,bytes,sha256,months_published,last_month' ;;
      revisions.csv) want='file,vintage_from,vintage_to,row_label,sector,field,old_value,new_value,kind' ;;
      checks.csv) want='check_id,description,expected,observed,status' ;;
      pins.csv) want='source,series,pin_date,value,unit' ;;
      fetch_log.csv) want='utc_time,host,path,status,bytes,sha256' ;;
    esac
    if [ -n "$want" ] && [ -z "$raw" ]; then
      got=$(grep -v '^#' "$f" | head -1 | tr -d '\r')
      [ "$got" = "$want" ] || bad="${bad}  ✗ header of $name is not its exact allowlist
"
    fi
  done
  if [ -z "$bad" ]; then
    echo "  ✓ only the 12 committed names, every header its exact allowlist, no raw MoF file or PDF, no local path, no at sign in $dir."
  else
    printf '%s' "$bad"
    echo "  -> raw MoF files and Bank of Japan PDFs stay in data/vintages/jp_life_foreign_bonds/ (gitignored). Remove the file before any commit."
  fi
}

# --- M17: JAPAN TERM-PREMIUM LEAK GUARD (warn only) --------------------------
# data/japan_term_premium/ may hold only derived statistics of Jouchi Nakajima's decomposition (spec
# _research/2026-10-19-Japan-Term-Premium-Spec.md, section 6), numbered M17 to avoid a clash with parallel builds. His repository
# states no licence, so his files are never committed in any form or under any name; the raw downloads stay in ~/jgb_term_premium_cache/. Four things
# would break that, and none is visible to M5-M15:
#   1. a file in the folder that is not one of the ten committed names (a copy of yield_M.csv or yield_D.csv, or the same bytes renamed);
#   2. Nakajima's quoted header line ("YYYYMM","ShadowRate",... or "YYYYMMDD","ShadowRate",...) at the start of a line in any file of the folder, or in
#      any tracked or untracked-but-not-ignored file of the repository outside bin/ and _research/ (the script and the spec quote it in prose);
#   3. pins.csv beyond its caps: more than 4 pins for one Nakajima monthly vintage, any pin for the April vintage or for a daily-file vintage, more than 4
#      for the Ministry of Finance or 3 for JMA, or a pin in a month outside the seven listed;
#   4. a month or a daily date in a committed file that is not one of 202312, 202407, 202408, 202412, 202603, 202606, 202609 (the fetch log's bytes and
#      sha256 columns are not read).
# Each file with a problem prints ONE ✗ line with all its reasons. bin/japan_term_premium.py refuses the same things when it writes (leak_guard); this is the
# second, independent look. JTP_DIR overrides the folder (used to show that the guard fires on a planted scratch copy). It warns and never blocks.
japan_tp_leak_check() {
  echo "-- M17: Japan term-premium leak guard (data/japan_term_premium/: only the ten committed names; no Nakajima header line; pins within caps; months within the list) --"
  local dir="${JTP_DIR:-data/japan_term_premium}" f name why bad="" pinbad want got toks t months hits
  local files="decomposition.csv verdict.csv vintage_revisions.csv fitted_check.csv vintages.csv pins.csv checks.csv fetch_log.csv README.md SOURCES.md"
  months="202312 202407 202408 202412 202603 202606 202609"
  local hdr_rx='^[[:space:]]*"YYYYMM(DD)?"[[:space:]]*,[[:space:]]*"ShadowRate"'
  [ -d "$dir" ] || { echo "  ✓ $dir is absent -- nothing to leak."; return; }
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    name=$(basename "$f")
    why=""
    case " $files " in *" $name "*) ;; *) why="${why}not on the list of ten committed names; " ;; esac
    grep -Eq "$hdr_rx" "$f" 2>/dev/null && why="${why}holds Nakajima's quoted header line; "
    case "$name" in
      decomposition.csv) want='vintage_id,variant,tenor,window_id,start_month,end_month,d_yield_pp,d_tp_pp,d_er_pp,tp_share,distance_bp,classification,opposite_signs,role' ;;
      verdict.csv) want='verdict_id,vintage_id,tenor,d_yield_pp,tp_share,distance_bp,classification,tp_share_2y,tp_share_5y,tp_share_10y,tp_share_20y,d_variant_tp_share,d_variant_classification,headline_reading,jma_tp_share,jma_label,jma_arms_fired,boj_match_tp_share,status,superseded_by,vintage_retrieved_utc' ;;
      vintage_revisions.csv) want='window_id,start_month,end_month,vintage_id,d_yield_pp,d_tp_pp,d_er_pp,tp_share,classification' ;;
      fitted_check.csv) want='vintage_id,file,tenor,scope,basis,n_periods,max_abs_gap_pp,median_abs_gap_pp,n_over_tol,status' ;;
      vintages.csv) want='vintage_id,source,file,commit_sha,commit_utc,blob_sha,sha256,first_period,last_period,n_rows,stated_update,retrieved_utc,role' ;;
      pins.csv) want='vintage_id,source,series,period,value,unit' ;;
      checks.csv) want='check_id,description,expected,observed,status' ;;
      fetch_log.csv) want='utc_time,host,path,status,bytes,sha256' ;;
      *) want='' ;;
    esac
    if [ -n "$want" ]; then
      got=$(grep -v '^#' "$f" | head -1 | tr -d '\r')
      [ "$got" = "$want" ] || why="${why}header is not its exact allowlist; "
    fi
    if [ "$name" = "pins.csv" ]; then
      pinbad=$(grep -v '^#' "$f" | tr -d '\r' | awk -F, -v months="$months" '
        BEGIN { n = split(months, ml, " "); for (i = 1; i <= n; i++) ok[ml[i]] = 1 }
        NR > 1 { c[$1 "|" $2]++
                 if ($2 == "nakajima_daily") bad = bad "a pin for a daily-file vintage; "
                 if ($2 == "nakajima_monthly" && index($1, "2026-04-20_8f940a0141ee") == 1) bad = bad "a pin for the April vintage; "
                 if (!($4 in ok)) bad = bad "a pin in a month outside the list; " }
        END { for (k in c) { split(k, p, "|"); s = p[2]
                cap = (s == "nakajima_monthly") ? 4 : (s == "mof") ? 4 : (s == "jma") ? 3 : (s == "nakajima_daily") ? -1 : 0
                if (cap >= 0 && c[k] > cap) bad = bad c[k] " pins for " s " " p[1] " (cap " cap "); " }
              print bad }')
      [ -n "$pinbad" ] && why="${why}${pinbad}"
    fi
    case "$name" in
      fetch_log.csv) toks=$(grep -v '^#' "$f" | cut -d, -f1-4 | tr -cs '0-9A-Za-z_.' '\n') ;;
      *) toks=$(grep -v '^#' "$f" 2>/dev/null | tr -cs '0-9A-Za-z_.' '\n') ;;
    esac
    hits=$(printf '%s\n' "$toks" | grep -E '^(19|20)[0-9]{2}(0[1-9]|1[0-2])([0-2][0-9]|3[01])?$' | awk -v months="$months" 'BEGIN { n = split(months, ml, " "); for (i = 1; i <= n; i++) ok[ml[i]] = 1 } !($1 in ok) { k++; if (k <= 4) s = s $1 " " } END { if (k) print k " token(s), first " s }')
    [ -n "$hits" ] && why="${why}month or date outside the list (${hits% }); "
    [ -n "$why" ] && bad="${bad}  ✗ $name: ${why%; }
"
  done < <(find "$dir" -maxdepth 1 -type f ! -name '.DS_Store' | sort)
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    t=$(git grep -I --untracked -l -E "$hdr_rx" -- . ':(exclude)bin' ':(exclude)_research' 2>/dev/null)
    [ -n "$t" ] && bad="${bad}$(printf '%s\n' "$t" | sed 's/^/  ✗ tracked or untracked file that starts a line with Nakajima'"'"'s quoted header: /')
"
  fi
  if [ -z "$bad" ]; then
    echo "  ✓ $dir holds only the ten committed names, no file starts a line with Nakajima's header, pins are within their caps, and every month is one of the seven listed."
  else
    printf '%s' "$bad"
    echo "  -> Nakajima's repository states no licence: his files are never committed, in any form or under any name; raw files stay in ~/jgb_term_premium_cache/. Remove the file before any commit."
  fi
}

# --- M16: UK GOLD EXPORTS LEAK AND WORDING GUARD (warn only) ------------------
# data/uk_gold_exports/ holds HMRC-derived kilograms (Open Government Licence) and, for completed years only, Swiss totals from UN Comtrade, whose terms keep
# monthly values out (spec _research/2026-10-19-UK-Gold-Exports-China-HK-Spec.md, sections 5 and 6). Raw replies, the Swiss monthly values and the STOP
# latches stay in the gitignored cache data/vintages/uk_gold_exports/. Four things would break that or the spec's wording rules, and none is visible to M5-M15:
#   1. a file in the folder that is not one of the ten names (eight CSVs, README.md, SOURCES.md), and a raw .json file in particular;
#   2. a header line (skipping every "# source:" line) that is not that file's exact column allowlist (the spec's canonical text, typed here a second time);
#   3. a Swiss monthly netWgt (kg, or tonnes to 3 decimals) anywhere in the folder unless it equals a completed-year total: in a cell of swiss_mirror_annual.csv or
#      of the Swiss column of context.csv, in any plain-number cell of the other committed files, or written with a unit in README.md or SOURCES.md; and a filled
#      Swiss cell for the current year. The three tables of HMRC kilograms and the request log are not read for this, since a coincidence there is not a disclosure;
#   4. a bound word (ceiling, cap, capped, bound, bounded) anywhere in the folder except the one README sentence that denies it.
# bin/uk_gold_exports.py refuses the same things when it writes; this is the second, independent look. UKGOLD_DIR and UKGOLD_CACHE override the folders
# (used to show that the guard fires on a planted value). It warns and never blocks (header doctrine). Numbered M16 to avoid a clash with parallel builds.
ukgold_leak_check() {
  echo "-- M16: UK gold exports guard (data/uk_gold_exports/: the ten names, exact headers, no raw file, no Swiss monthly value in any committed file, no bound word outside the denial sentence) --"
  local dir="${UKGOLD_DIR:-data/uk_gold_exports}" cache="${UKGOLD_CACHE:-data/vintages/uk_gold_exports}" name want got bad="" f extra kg
  local denial="From May 2016 warehouse and free-zone movements are outside the figures, so this series is not an upper bound, ceiling or cap on metal leaving the UK."
  [ -d "$dir" ] || { echo "  ✓ $dir is absent -- nothing to leak."; return; }
  for name in monthly.csv annual.csv swiss_mirror_annual.csv context.csv revisions.csv summary.csv checks.csv fetch_log.csv; do
    f="$dir/$name"
    if [ ! -f "$f" ]; then bad="${bad}  ✗ missing: $name
"; continue; fi
    case "$name" in
      monthly.csv) want='month,partner,series,net_mass_kg,supp_unit_div_1000,rows_n,status,trade_system,provisional,vintage' ;;
      annual.csv) want='year,partner,series,net_mass_kg,net_mass_kg_known_months,months_n,months_blank,trade_system,provisional_months,vintage' ;;
      swiss_mirror_annual.csv) want='year,partner,hs6,net_mass_kg,net_mass_kg_known_months,months_n,months_blank,net_wgt_estimated_months,status,comtrade_annual_kg,monthly_sum_minus_annual_kg' ;;
      context.csv) want='window,months,months_blank,trade_system,uk_71081310_cn_hk_t,uk_71081310_cn_t,uk_71081310_hk_t,swiss_710812_cn_hk_t,safe_reported_change_t,wgc_central_banks_t,wgc_minus_imf_gap_t,note' ;;
      revisions.csv) want='vintage_prev,vintage_new,month,partner,series,kg_prev,kg_new,change_kg,provisional_at_prev' ;;
      summary.csv) want='question,window,partner,series,statistic,value,blind,notable' ;;
      checks.csv) want='check_id,description,expected,observed,status' ;;
      fetch_log.csv) want='utc_time,host,path_and_query,status,bytes,sha256' ;;
    esac
    got=$(grep -v '^# source:' "$f" | head -1 | tr -d '\r')
    [ "$got" = "$want" ] || bad="${bad}  ✗ header of $name is not its exact allowlist
"
  done
  for name in README.md SOURCES.md; do
    [ -f "$dir/$name" ] || bad="${bad}  ✗ missing: $name
"
  done
  extra=$(find "$dir" -maxdepth 1 -type f -name '*.json' | sort)
  [ -n "$extra" ] && bad="${bad}$(printf '%s\n' "$extra" | sed 's/^/  ✗ raw file in the committed folder: /')
"
  extra=$(find "$dir" -maxdepth 1 -type f ! -name '*.json' ! -name '.DS_Store' ! -name README.md ! -name SOURCES.md ! -name monthly.csv ! -name annual.csv \
            ! -name swiss_mirror_annual.csv ! -name context.csv ! -name revisions.csv ! -name summary.csv ! -name checks.csv ! -name fetch_log.csv | sort)
  [ -n "$extra" ] && bad="${bad}$(printf '%s\n' "$extra" | sed 's/^/  ✗ file that is not one of the ten committed names: /')
"
  # Swiss monthly values: every monthly Comtrade reply in the cache (YYYYMM.json) gives netWgt values, as kg and as tonnes to 3 decimals
  kg=$(ls "$cache"/comtrade/[0-9][0-9][0-9][0-9][0-9][0-9].json 2>/dev/null | while read -r f; do grep -o '"netWgt": *[0-9.]*' "$f" | sed 's/.*: *//'; done | awk '{ printf "%d\n", $1 + 0.5 }' | sort -u)
  if [ -n "$kg" ] && [ -f "$dir/swiss_mirror_annual.csv" ] && [ -f "$dir/context.csv" ]; then
    local asof leak
    asof=$(grep -v '^#' "$dir/monthly.csv" 2>/dev/null | awk -F, 'NR == 2 { print substr($10, 1, 4) }')
    leak=$(printf '%s\n' "$kg" | awk -v asof="${asof:-9999}" -v sfile="$dir/swiss_mirror_annual.csv" -v cfile="$dir/context.csv" '
      { k[$1] = 1; t[sprintf("%.3f", $1 / 1000)] = 1 }
      END {
        while ((getline line < sfile) > 0) {
          if (line ~ /^#/) continue
          n = split(line, c, ","); if (c[1] == "year") continue
          if (c[9] == "complete" && c[4] != "") { tot[c[4]] = 1; tott[sprintf("%.3f", c[4] / 1000)] = 1 }
          rows[++r] = line
        }
        for (i = 1; i <= r; i++) {
          n = split(rows[i], c, ",")
          for (j = 4; j <= 11; j++) { if (j == 6 || j == 7 || j == 8 || j == 9) continue
            v = c[j]; if (v ~ /^[0-9]+$/ && v != "0" && (v in k) && !(v in tot)) print "a Swiss monthly kg value sits in swiss_mirror_annual.csv (" v ")" }
          if (c[1] + 0 >= asof + 0 && (c[4] != "" || c[5] != "" || c[10] != "" || c[11] != "")) print "a current-year Swiss cell is filled in swiss_mirror_annual.csv (" c[1] ")"
        }
        while ((getline line < cfile) > 0) {
          if (line ~ /^#/) continue
          n = split(line, c, ","); if (c[1] == "window") continue
          v = c[8]; if (v == "" || v == "0.000") continue
          if ((v in t) && !(v in tott)) print "a Swiss monthly value in tonnes sits in context.csv (" v ")"
          if (c[1] !~ /^[0-9][0-9][0-9][0-9]$/ || c[1] + 0 >= asof + 0) print "a current-year Swiss cell is filled in context.csv (" c[1] ")"
        }
      }')
    [ -n "$leak" ] && bad="${bad}$(printf '%s\n' "$leak" | sort -u | sed 's/^/  ✗ /')
"
  fi
  # the same Swiss monthly values in every other committed file: plain-number cells (an integer of 1,000 or more that is not a year, or a 3-decimal tonnes figure)
  # and any number written with a unit; completed-year totals are exempt
  if [ -n "$kg" ] && [ -f "$dir/swiss_mirror_annual.csv" ]; then
    local tots prose
    tots=$(grep -v '^#' "$dir/swiss_mirror_annual.csv" | awk -F, 'NR > 1 && $9 == "complete" && $4 != "" { print $4 }')
    prose=$(for f in "$dir"/README.md "$dir"/SOURCES.md "$dir"/summary.csv "$dir"/checks.csv; do
      [ -f "$f" ] || continue
      KGS="$kg" TOTS="$tots" awk -v name="$(basename "$f")" -v md="$([ "${f##*.}" = md ] && echo 1 || echo 0)" '
        BEGIN { n = split(ENVIRON["KGS"], a, "\n"); for (i = 1; i <= n; i++) if (a[i] != "") { k[a[i] + 0] = 1; t[sprintf("%.3f", a[i] / 1000)] = 1 }
                n = split(ENVIRON["TOTS"], b, "\n"); for (i = 1; i <= n; i++) if (b[i] != "") { tot[b[i] + 0] = 1; tott[sprintf("%.3f", b[i] / 1000)] = 1 } }
        /^#/ && md == 0 { next }
        { line = $0
          if (md == 1) { m = (line ~ /^[|]/) ? split(line, c, "|") : 0 } else { m = split(line, c, ",") }
          for (j = 1; j <= m; j++) { v = c[j]; gsub(/^[ \t"]+|[ \t"]+$/, "", v)
            if (v ~ /^[0-9]+$/ && v + 0 >= 1000 && !(v + 0 >= 1990 && v + 0 <= 2100) && ((v + 0) in k) && !((v + 0) in tot)) hit[v] = 1
            else if (v ~ /^[0-9]+[.][0-9][0-9][0-9]$/ && (v in t) && !(v in tott)) hit[v] = 1 }
          s = line
          while (match(s, /[0-9][0-9,]*([.][0-9]+)?[ \t]*(kg|kilograms?|tonnes?)([^A-Za-z]|$)/)) {
            tok = substr(s, RSTART, RLENGTH); s = substr(s, RSTART + RLENGTH)
            unit = tok; gsub(/[0-9,. \t]/, "", unit); sub(/[^A-Za-z]+$/, "", unit)
            num = tok; sub(/[ \t]*[A-Za-z].*$/, "", num); gsub(/,/, "", num)
            if (unit ~ /^(kg|kilograms?)$/ && num ~ /^[0-9]+$/ && ((num + 0) in k) && !((num + 0) in tot)) hit[num] = 1
            if (unit ~ /^tonnes?$/ && num ~ /^[0-9]+[.][0-9][0-9][0-9]$/ && (num in t) && !(num in tott)) hit[num] = 1 } }
        END { for (h in hit) print "a Swiss monthly value (" h ") sits in " name }' "$f"
    done)
    [ -n "$prose" ] && bad="${bad}$(printf '%s\n' "$prose" | sort -u | sed 's/^/  ✗ /')
"
  fi
  # bound words anywhere in the folder, except the one README sentence that denies them (removed once, from the first line that holds it)
  local words
  words=$(for f in "$dir"/*.csv "$dir"/README.md "$dir"/SOURCES.md; do
    [ -f "$f" ] || continue
    awk -v den="$denial" -v readme="$([ "$(basename "$f")" = README.md ] && echo 1 || echo 0)" -v name="$(basename "$f")" '
      { line = $0
        if (readme == 1 && !gone) { i = index(line, den); if (i > 0) { line = substr(line, 1, i - 1) substr(line, i + length(den)); gone = 1 } }
        l = tolower(line)
        if (l ~ /(^|[^a-z0-9_])(ceiling|caps?|capped|(upper[ \t]+)?bounds?|bounded)([^a-z0-9_]|$)/) print "  ✗ a bound word in " name " line " NR }' "$f"
  done)
  [ -n "$words" ] && bad="${bad}${words}
"
  if [ -z "$bad" ]; then
    echo "  ✓ ten names, every header its exact allowlist, no raw file, no Swiss monthly value in any committed file, no bound word outside the one denial sentence in $dir."
  else
    printf '%s' "$bad"
    echo "  -> UN Comtrade terms: monthly values stay in data/vintages/uk_gold_exports/; the spec bans bound words except in the one README sentence that denies them. Remove it before any commit."
  fi
}

# --- M19: FUND FUTURES AND INDEX SPLIT LEAK GUARD (warn only) -----------------
# data/nport/fut_*.csv and idx_*.csv are derived aggregates of the SEC bulk N-PORT and Form N-CEN files (spec
# _research/2026-10-19-Fund-Futures-And-Index-Split-Spec.md, requirements R5 and R23-16). Five things would break that, and none is visible to M5-M18:
#   1. a header that is not that file's row of data/nport/fut_idx_columns.tsv (the one committed allowlist; this guard keeps no copy of it);
#   2. a header holding CUSIP, HOLDING_ID, ACCESSION_NUMBER, SERIES_ID, SERIES_NAME, REGISTRANT_NAME, LEI or CIK, or a file above 2,000 rows;
#   3. a count below five (series_n or funds_n) on any row that is not the merged other_small row, or an other_small row of fewer than five with amounts;
#   4. a fut_*/idx_* file that fut_idx_columns.tsv does not list, or fut_idx_columns.tsv differing from the table of section 5 of the spec;
#   5. causal wording in the README, the sources file or the verdict files, or a verdict file whose first key is not required_sentence.
# bin/nport_futures_index.py checks the same things when it writes (C-X4); this is the second, independent look. FUTIDX_DIR and FUTIDX_SPEC override the
# folder and the spec path (used to show that the guard fires on a planted row). It warns and never blocks (header doctrine).
futidx_leak_check() {
  echo "-- M19: fund-futures / index-split leak guard (data/nport/fut_*, idx_*: headers = fut_idx_columns.tsv = spec section 5, no identifier column, small cells merged, no causal wording) --"
  local dir="${FUTIDX_DIR:-data/nport}" spec="${FUTIDX_SPEC:-_research/2026-10-19-Fund-Futures-And-Index-Split-Spec.md}"
  if ! ls "$dir"/fut_*.csv "$dir"/idx_*.csv >/dev/null 2>&1 && [ ! -f "$dir/fut_idx_columns.tsv" ]; then
    echo "  ✓ $dir holds no fund-futures or index-split file -- nothing to leak."; return
  fi
  local out py
  read -r -d '' py <<'PY' || true
import csv, glob, os, re, sys
d, spec = sys.argv[1], sys.argv[2]
bad = []
tsv = os.path.join(d, "fut_idx_columns.tsv")
cols = {}
if not os.path.exists(tsv):
    bad.append("fut_idx_columns.tsv is missing")
else:
    for ln in open(tsv, encoding="utf-8").read().splitlines()[1:]:
        if ln.strip():
            f, c = ln.split("\t")
            cols[f] = c.split("|")
if os.path.exists(spec) and cols:
    sec = open(spec, encoding="utf-8").read()
    a = sec.find("## 5. Outputs")
    b = sec.find("**Small cells", a)
    want = {}
    for ln in sec[a:b].splitlines():
        if ln.startswith("| `"):
            cells = [x.strip() for x in ln.strip().strip("|").split("|")]
            for f in re.findall(r"`([^`]+)`", cells[0]):
                want[f] = [x.strip() for x in re.search(r"`([^`]+)`", cells[2]).group(1).split(",")]
    if want != cols:
        bad.append("fut_idx_columns.tsv differs from the table of section 5 of the spec: " + ", ".join(sorted(set(want) ^ set(cols)) or [k for k in want if want[k] != cols.get(k)]))
forbid = ("CUSIP", "HOLDING_ID", "ACCESSION_NUMBER", "SERIES_ID", "SERIES_NAME", "REGISTRANT_NAME", "LEI", "CIK")
cellfiles = {"fut_contracts.csv": ("funds_n", "contract"), "fut_split.csv": ("funds_n", "group"), "idx_split.csv": ("series_n", "group"),
             "idx_coverage.csv": ("series_n", "flag"), "idx_crosstab.csv": ("series_n", "arm")}
for p in sorted(glob.glob(os.path.join(d, "fut_*.csv")) + glob.glob(os.path.join(d, "idx_*.csv"))):
    n = os.path.basename(p)
    rows = list(csv.reader(open(p, encoding="utf-8", newline="")))
    hdr = rows[0] if rows else []
    if n not in cols:
        bad.append(n + " is not listed in fut_idx_columns.tsv"); continue
    if hdr != cols[n]:
        bad.append(n + ": header is not its row of fut_idx_columns.tsv")
    if any(t in h.upper() for h in hdr for t in forbid):
        bad.append(n + ": a header holds an identifier token")
    if len(rows) - 1 > 2000:
        bad.append(n + ": %d rows, above 2,000" % (len(rows) - 1))
    if n in cellfiles and not (cellfiles[n][0] in hdr and cellfiles[n][1] in hdr):
        bad.append("%s: the count column %s or the label column %s is missing from the header (renamed?), so the small-cell test cannot run" % ((n,) + cellfiles[n]))
    elif n in cellfiles:
        nc, lc = cellfiles[n]
        for i, r in enumerate(rows[1:], start=2):
            row = dict(zip(hdr, r))
            try:
                k = int(float(row[nc]))
            except ValueError:
                continue
            if row[lc] != "other_small" and k < 5:
                bad.append("%s row %d: count %d is below five" % (n, i, k))
            if row[lc] == "other_small" and k < 5 and any(v for c, v in row.items() if c not in (nc, lc, "period", "window") and v != ""):
                bad.append("%s row %d: an other_small cell of %d shows amounts" % (n, i, k))
    if n in ("fut_verdict.csv", "idx_verdict.csv") and (len(rows) < 2 or rows[1][0] != "required_sentence"):
        bad.append(n + ": the first key is not required_sentence")
causal = re.compile(r"\b(caus(e|ed|es|ing)|drove|driv(e|es|en|ing)|led\s+to|pushed|because\s+of|in\s+response\s+to|moved\s+yields)\b", re.I)
req = "These are holdings measurements. They do not show what moved Treasury yields."
for p in sorted(glob.glob(os.path.join(d, "fut_idx_*.md")) + glob.glob(os.path.join(d, "fut_verdict.csv")) + glob.glob(os.path.join(d, "idx_verdict.csv"))):
    t = open(p, encoding="utf-8").read().replace(req, "")
    for m in causal.finditer(t):
        bad.append(os.path.basename(p) + ": causal wording '" + m.group(0) + "'")
print("\n".join("  ✗ " + b for b in bad) if bad else "OK")
PY
  out=$(python3 -c "$py" "$dir" "$spec")
  if [ "$out" = "OK" ]; then
    echo "  ✓ every fut_*/idx_* header is its row of fut_idx_columns.tsv (= spec section 5), no identifier column, at most 2,000 rows, no count below five outside other_small, no causal wording."
  else
    printf '%s\n' "$out"
    echo "  -> derived aggregates only: no identifier, fund or registrant name, and no cell under five series may be committed. Remove or re-run before any commit."
  fi
}

# --- M22: QUARTER-END BASIS LEAK AND WORDING GUARD (warn only) ----------------
# data/quarter_end_basis/ may hold only derived statistics of the swap-tape ledger's own derived files (spec _research/2026-10-23-Quarter-End-Basis-Spec.md,
# sections 6 and 7; E-024: nothing raw from DTCC is ever committed). Six things would break that or the spec's wording rules, and none is visible to M5-M19:
#   1. a file in the folder that is not one of the ten committed names, or a committed name that is missing;
#   2. the spec's fenced allowlist block not hashing to the pinned sha256 (typed here a third time, after SPEC_ALLOW_SHA256 in bin/quarter_end_basis.py and
#      the hash the spec prints), or columns.tsv or a CSV header (the first line that does not start with #) differing from that block;
#   3. a file named CFTC_CUMULATIVE_*, a .zip, or a header holding Dissemination Identifier, Event timestamp, UPI FISN or Notional currency-Leg 1;
#   4. a field that is a whole string of 8 to 19 digits (an identifier), or /Users/, /private/tmp or an at sign in any committed file;
#   5. a row of anchors.csv, anchors_tenor.csv or questions.csv whose status is not complete (or whose n_window is under 25) that carries a median, D or rank;
#   6. causal or attribution wording, or verdict or significance wording, in README.md, SOURCES.md or a note, outside the exemptions of the spec's R5.
# Each breach prints one line tagged [1] to [6]. bin/quarter_end_basis.py refuses the same things when it writes; this is the second, independent look.
# QEB_DIR and QEB_SPEC override the folder and the spec path (used to show that the guard fires on planted copies). It warns and never blocks.
qeb_leak_check() {
  echo "-- M22: quarter-end basis guard (data/quarter_end_basis/: the ten names, allowlist hash and exact headers, no raw DTCC file or identifier, no thin-row value, no verdict or causal wording) --"
  local dir="${QEB_DIR:-data/quarter_end_basis}" spec="${QEB_SPEC:-_research/2026-10-23-Quarter-End-Basis-Spec.md}" out py
  [ -d "$dir" ] || { echo "  ✓ $dir is absent -- nothing to leak."; return; }
  read -r -d '' py <<'PY' || true
import csv, hashlib, os, re, sys
d, spec = sys.argv[1], sys.argv[2]
PIN = "3f54fbeb17c65e257af8acd41c1f2b0b2398b432ca18b3bed4f60c1c5e2445e4"
NAMES = ["README.md", "SOURCES.md", "anchors.csv", "anchors_tenor.csv", "band.csv", "questions.csv", "short_tenor_availability.csv", "inputs.csv", "checks.csv", "columns.tsv"]
REQ = ("These are medians of reported 1-5-year cross-currency swap prices around quarter-ends. A difference at a quarter-end does not show who "
       "borrowed dollars, why, or that any flow moved a price.")
NEI = "Neither identifies the counterparties or the reason."
CAUSAL = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because|due\s+to|in\s+response\s+to|led\s+to|prompted|pushed|"
                    r"as\s+a\s+result\s+of|reflect(?:s|ed|ing)?|amid|owing\s+to|on\s+the\s+back\s+of|window[- ]dress(?:ed|es|ing)?|borrowed|"
                    r"borrowing\s+by|demand\s+for\s+dollars|hedging\s+demand)\b", re.I)
VERDICT = re.compile(r"\b(SUPPORTS|AGAINST|INCONCLUSIVE|PENDING)\b|(?i:\b(statistically\s+significant|significance|p-value|reject(?:s|ed)?\s+the\s+null)\b)")
files = sorted(os.listdir(d))
def text(n):
    with open(os.path.join(d, n), encoding="utf-8", errors="replace") as f:
        return f.read()
def table(n):
    lines = [l for l in text(n).splitlines() if not l.startswith("#")]
    if not lines:
        return [], []
    if n.endswith(".tsv"):
        rows = [l.split("\t") for l in lines]
    else:
        rows = list(csv.reader(lines))
    return rows[0], rows[1:]
def block():
    try:
        with open(spec, encoding="utf-8") as f:
            t = f.read()
    except OSError:
        return None, None
    i = t.find("**Header allowlist, canonical text.**")
    j = t.find("```\n", i)
    k = t.find("\n```", j + 4)
    if i < 0 or j < 0 or k < 0:
        return None, None
    m = re.search(r"sha256 of that text \([0-9,]+ bytes\): `([0-9a-f]{64})`", t)
    return t[j + 4:k] + "\n", (m.group(1) if m else None)
def r1():
    out = ["[1] file that is not one of the ten committed names: " + n for n in files if n not in NAMES]
    return out + ["[1] committed name missing: " + n for n in NAMES if n not in files]
def r2():
    blk, printed = block()
    if blk is None:
        return ["[2] the spec's fenced allowlist block cannot be read from " + spec]
    out = []
    if hashlib.sha256(blk.encode()).hexdigest() != PIN:
        out.append("[2] the spec's allowlist block does not hash to the pinned sha256")
    if printed != PIN:
        out.append("[2] the sha256 the spec prints for its allowlist block is not the pinned one")
    want = {}
    for ln in blk.splitlines():
        n, c = ln.split(":", 1)
        want[n] = c.split(",")
    for n in files:
        if n in want:
            h, rows = table(n)
            if h != want[n]:
                out.append("[2] header of %s is not its allowlist" % n)
            if n == "columns.tsv":
                got = {r[0]: r[1].split("|") for r in rows if len(r) == 2}
                if got != want:
                    out.append("[2] columns.tsv differs from the allowlist block")
    return out
def r3():
    out = []
    for n in files:
        if re.match(r"CFTC_CUMULATIVE_", n, re.I) or n.lower().endswith(".zip"):
            out.append("[3] raw DTCC file or archive by name: " + n)
        if n.endswith((".csv", ".tsv")):
            first = [l for l in text(n).splitlines() if not l.startswith("#")][:1]
            if first and re.search(r"Dissemination Identifier|Event timestamp|UPI FISN|Notional currency-Leg 1", first[0]):
                out.append("[3] raw DTCC header in " + n)
    return out
def r4a():
    out = []
    for n in files:
        if n.endswith((".csv", ".tsv")):
            h, rows = table(n)
            for i, r in enumerate(rows, 2):
                for c in r:
                    if re.fullmatch(r"\d{8,19}", c):
                        out.append("[4] %s row %d: a field that is a whole string of %d digits" % (n, i, len(c)))
    return out
def r4b():
    out = []
    for n in files:
        t = text(n)
        for tok in ("/Users/", "/private/tmp", "@"):
            if tok in t:
                out.append("[4] %s contains %s" % (n, "an at sign" if tok == "@" else tok))
    return out
NUMCOLS = ["med_window_bp", "med_pre_bp", "med_post_bp", "d_bp", "rank_band", "rank_ref", "mean_tenor_window_y", "mean_tenor_ctrl_y", "d_mean_tenor_y"]
def anchors():
    if "anchors.csv" not in files:
        return {}
    h, rows = table("anchors.csv")
    return {(r[0], r[1], r[2]): dict(zip(h, r)) for r in rows if len(r) == len(h)}
def thin(a):
    try:
        return a["status"] != "complete" or (a["n_window"] != "" and int(a["n_window"]) < 25)
    except (KeyError, ValueError):
        return True
def r5a():
    out = []
    for k, a in anchors().items():
        if thin(a) and any(a.get(c, "") != "" for c in NUMCOLS):
            out.append("[5] anchors.csv %s %s %s: status %s (n_window %s) carries a median, D or rank" % (k + (a["status"], a["n_window"])))
    return out
def r5t():
    out = []
    if "anchors_tenor.csv" in files:
        h, rows = table("anchors_tenor.csv")
        for r in rows:
            a = dict(zip(h, r))
            if a.get("status") != "complete" and any(a.get(c, "") != "" for c in ("med_window_bp", "med_pre_bp", "med_post_bp", "d_bp")):
                out.append("[5] anchors_tenor.csv %s %s %s tenor %s: status %s carries a median or D" % (a["pair"], a["anchor_date"], a["anchor_type"], a["tenor_y"], a["status"]))
    return out
def r5q():
    out = []
    if "questions.csv" not in files:
        return out
    an = anchors()
    tn = {}
    if "anchors_tenor.csv" in files:
        h, rows = table("anchors_tenor.csv")
        for r in rows:
            a = dict(zip(h, r))
            tn[(a["pair"], a["anchor_date"], a["anchor_type"], a["tenor_y"])] = a["status"]
    h, rows = table("questions.csv")
    for r in rows:
        q = dict(zip(h, r))
        if not re.match(r"(d_bp|rank_|d_mean_tenor_y|d_tenor_|med_|mean_tenor)", q["statistic"]) or q["value"] == "" or q["anchor_date"] == "":
            continue
        key = (q["pair"], q["anchor_date"], q["anchor_type"])
        a = an.get(key)
        if a is not None and thin(a):
            out.append("[5] questions.csv %s %s %s: %s is printed for an anchor whose status is %s" % (key + (q["statistic"], a["status"])))
        m = re.match(r"d_tenor_(\d)y_bp", q["statistic"])
        if m and tn.get(key + (m.group(1),)) != "complete":
            out.append("[5] questions.csv %s %s %s: %s is printed for a tenor cell that is not complete" % (key + (q["statistic"],)))
    return out
def strip(n, t):
    t = t.replace(REQ, "").replace(NEI, "")
    if n == "SOURCES.md":
        t = "\n".join("" if (re.search(r"CGFS", l) and re.search(r"\bpp?\s?\d", l)) else l for l in t.split("\n"))
    return t
def scan(label, n, t):
    out = []
    for m in CAUSAL.finditer(strip(n, t)):
        out.append("[6] %s: causal or attribution wording %r" % (label, m.group(0)))
    return out
def r6a():
    out = []
    for n in ("README.md", "SOURCES.md"):
        if n in files:
            out += scan(n, n, text(n))
    if "questions.csv" in files:
        h, rows = table("questions.csv")
        if "note" in h:
            i = h.index("note")
            for r in rows:
                if len(r) > i:
                    out += scan("questions.csv note", "questions.csv", r[i])
    return out
def r6b():
    out = []
    for n in ("README.md", "SOURCES.md"):
        if n in files:
            out += ["[6] %s: verdict or significance wording %r" % (n, m.group(0)) for m in VERDICT.finditer(text(n))]
    if "questions.csv" in files:
        h, rows = table("questions.csv")
        if "note" in h:
            i = h.index("note")
            for r in rows:
                if len(r) > i:
                    out += ["[6] questions.csv note: verdict or significance wording %r" % m.group(0) for m in VERDICT.finditer(r[i])]
    return out
bad = []
bad += r1()
bad += r2()
bad += r3()
bad += r4a()
bad += r4b()
bad += r5a()
bad += r5t()
bad += r5q()
bad += r6a()
bad += r6b()
print("\n".join("  ✗ " + b for b in bad) if bad else "OK")
PY
  out=$(python3 -c "$py" "$dir" "$spec")
  if [ "$out" = "OK" ]; then
    echo "  ✓ only the ten committed names, the allowlist block hashes to the pinned sha256 and every header is it, no raw DTCC file or identifier, no local path or at sign, no value on a thin row, no verdict or causal wording in $dir."
  else
    printf '%s\n' "$out"
    echo "  -> derived statistics only (E-024): no DTCC file, row or identifier, no value on a row that is not complete, no verdict or causal wording. Remove or re-run before any commit."
  fi
}

# --- M23: US MONEY FUNDS' CLAIMS ON NON-US BANKS GUARD (warn only) -----------
# data/mmf_nonus_banks/ holds statistics derived from the OFR money-fund monitor and nothing raw (spec _research/2026-10-25-MMF-NonUS-Banks-Spec.md, sections 5, 6
# and 9.5; build bin/mmf_nonus_banks.py). The monitor's JSON stays in the gitignored cache data/vintages/mmf_nonus_banks/. Six things would break that or the
# spec's rules, and none is visible to M5-M22:
#   1. a file that is not one of the twelve committed names (ten CSVs, README.md, SOURCES.md), a raw file (.json, .zip, .html, .pdf) or a node JSON under any
#      name, and a missing name;
#   2. a header line (skipping every "# source:" line) that is not that file's exact column allowlist -- the spec's ten canonical lines, typed here a second
#      time: this guard never reads them from the script;
#   3. a local path (/Users/, /private/, a tilde) or an at sign in any committed file;
#   4. causal, flow or motive wording (the spec's two patterns, pasted) in README.md anywhere but the one denial sentence;
#   5. a duplicate key in any file;
#   6. on every month, measure and lineage of levels_group.csv, the nine groups EA, JP, CA, UK, CH, NORDIC, AUNZ, OTHER_ASIA and OTHER not summing to ALL_NONUS.
# The script refuses the same things when it writes; this is the second, independent look. MMFNB_DIR overrides the folder (used to show that the guard fires on
# a planted copy). It warns and never blocks (header doctrine).
mmfnb_leak_check() {
  echo "-- M23: money-fund non-US banks guard (data/mmf_nonus_banks/: the twelve names, exact headers, no raw file, local path or at sign, no causal/flow/motive wording outside the denial sentence, no duplicate key, the nine groups sum to ALL_NONUS on every month, measure and lineage) --"
  local dir="${MMFNB_DIR:-data/mmf_nonus_banks}" out py
  [ -d "$dir" ] || { echo "  ✓ $dir is absent -- nothing to leak."; return; }
  read -r -d '' py <<'PY' || true
import csv, os, re, sys
from decimal import Decimal
d = sys.argv[1]
CANON = """levels_country.csv:month_end,country,country_group,instrument_group,usd_mn,pct_of_mmf_total,pct_of_nonus_fi,vintage
levels_group.csv:month_end,country_group,fund_lineage,measure,usd_mn,pct_of_mmf_total,pct_of_lineage_total,vintage
quarter_ends.csv:quarter,qe_month,basis,stat_kind,country_group,measure,level_prev_usd_mn,level_qe_usd_mn,level_next_usd_mn,chg_in_pct,chg_out_pct,below_nbrs_pct,below_nbrs_usd_mn,window,frozen_set,primary,blind,vintage
qe_summary.csv:basis,stat_kind,window,country_group,measure,n_quarters,n_blank,mean_below_nbrs_pct,median_below_nbrs_pct,n_negative,sd_below_nbrs_pct,se_mean_below_nbrs_pct,noise_clean_sd_pct,noise_n,pattern,paired_n_vs_aunz,paired_mean_diff_vs_aunz_pct,paired_se_vs_aunz_pct,primary,blind,vintage
parents.csv:parent,country,country_group,kind,first_month,last_month,usd_mn_latest,vintage
summary.csv:question,window,country_group,measure,from_month,to_month,statistic,value,unit,primary,blind
revisions.csv:vintage_prev,vintage_new,month_end,country,instrument_group,usd_mn_prev,usd_mn_new,change_usd_mn
vintages.csv:vintage,ofr_updated,ofr_asof,requests,nodes,manifest_sha256,api_total_check,kind_table_sha256
checks.csv:check_id,description,expected,observed,status
fetch_log.csv:utc_time,host,path,status,bytes,sha256
"""
want = dict(l.split(":", 1) for l in CANON.strip().split("\n"))
keys = {
 "levels_country.csv": ("month_end", "country", "instrument_group"),
 "levels_group.csv": ("month_end", "country_group", "fund_lineage", "measure"),
 "quarter_ends.csv": ("quarter", "basis", "country_group", "measure"),
 "qe_summary.csv": ("basis", "window", "country_group", "measure"),
 "parents.csv": ("parent", "country"),
 "summary.csv": ("question", "window", "country_group", "measure", "from_month", "to_month", "statistic"),
 "revisions.csv": ("vintage_prev", "vintage_new", "month_end", "country", "instrument_group"),
 "vintages.csv": ("vintage",),
 "checks.csv": ("check_id",),
}
names = set(want) | {"README.md", "SOURCES.md"}
CAUSAL = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b", re.I)
EXTRA = re.compile(r"\b(?:in|out)?flows?\b|window[- ]dressing|\b(?:head\s+offices?|parents?)\s+(?:fund|funds|funded|funding|push|pushes|pushed|pull|pulls|pulled|drain|drains|drained)\b|\b(?:dollar\s+)?(?:shortage|squeeze)\b|\bpull(?:ed|ing|s)?\s+(?:back|out)\b|\bretreat(?:ed|ing|s)?\b|\bruns?\s+on\b|\bflight\b|\blog[- ]points?\b|\bdips?\b", re.I)
DENIAL = "These month-end changes are not flows of funds, and the table does not test window dressing or any other motive."
bad = []
here = set()
texts = {}
for n in sorted(os.listdir(d)):
    p = os.path.join(d, n)
    if not os.path.isfile(p) or n == ".DS_Store":
        continue
    here.add(n)
    t = open(p, encoding="utf-8", errors="replace", newline="").read()
    texts[n] = t
    body = [l for l in t.split("\n") if not l.startswith("# source:") and l.strip()]
    first = body[0].lstrip() if body else ""
    if n.lower().endswith((".json", ".zip", ".html", ".pdf")) or first.startswith('{"datatable"') or first.startswith('{"highcharts"') or (first.startswith("{") and ('"datatable"' in t[:3000] or '"highcharts"' in t[:3000])):
        bad.append("raw file in the committed folder (a node JSON, zip, page or PDF): " + n)
        continue
    if n not in names:
        bad.append("file that is not one of the twelve committed names: " + n)
        continue
    if re.search(r"/Users/|/private/|~", t):
        bad.append(n + " contains a local path (/Users/, /private/ or a tilde)")
    if "@" in t:
        bad.append(n + " contains an at sign")
    if n in want:
        hdr = (body[0] if body else "").rstrip("\r")
        if hdr != want[n]:
            bad.append("header of " + n + " is not its exact allowlist")
        elif n in keys:
            rows = list(csv.reader(body))
            head = rows[0]
            idx = [head.index(k) for k in keys[n]]
            seen, dup = set(), []
            for r in rows[1:]:
                k = tuple(r[i] for i in idx if i < len(r))
                if k in seen:
                    dup.append(k)
                seen.add(k)
            if dup:
                bad.append("duplicate key in " + n + ": " + "|".join(dup[0]) + " (" + str(len(dup)) + " duplicate row(s))")
    if n == "README.md":
        t2 = t.replace(DENIAL, "", 1)
        hits = sorted({re.sub(r"\s+", " ", m.group(0).lower()) for rx in (CAUSAL, EXTRA) for m in rx.finditer(t2)})
        if hits:
            bad.append("README.md holds banned wording (spec R5): " + ", ".join(hits[:6]))
for n in sorted(names - here):
    bad.append("missing: " + n)
NINE = ("EA", "JP", "CA", "UK", "CH", "NORDIC", "AUNZ", "OTHER_ASIA", "OTHER")
t = texts.get("levels_group.csv")
if t:
    body = [l for l in t.split("\n") if not l.startswith("# source:") and l.strip()]
    rows = list(csv.reader(body))
    if rows and ",".join(rows[0]) == want["levels_group.csv"]:
        head = rows[0]
        im, ig, il, imeas, iv = (head.index(c) for c in ("month_end", "country_group", "fund_lineage", "measure", "usd_mn"))
        tot, parts = {}, {}
        for r in rows[1:]:
            if len(r) <= iv or r[iv] == "":
                continue
            k = (r[im], r[il], r[imeas])
            if r[ig] == "ALL_NONUS":
                tot[k] = Decimal(r[iv])
            elif r[ig] in NINE:
                parts[k] = parts.get(k, Decimal(0)) + Decimal(r[iv])
        off = [k for k in sorted(set(tot) | set(parts)) if abs(tot.get(k, Decimal(0)) - parts.get(k, Decimal(0))) > Decimal("0.5")]
        if off:
            k = off[0]
            bad.append("levels_group.csv: the nine groups do not sum to ALL_NONUS in " + str(len(off)) + " month-measure-lineage cell(s), first " + "/".join(k) + " (nine groups " + str(parts.get(k, Decimal(0))) + ", ALL_NONUS " + str(tot.get(k, Decimal(0))) + ")")
for b in bad:
    print("BAD " + b)
PY
  out=$(python3 -c "$py" "$dir" 2>&1)
  if [ -z "$(printf '%s' "$out" | tr -d '\n ')" ]; then
    echo "  ✓ twelve names, every header its exact allowlist, no raw file, local path or at sign, no duplicate key, no banned wording outside the denial sentence, and the nine groups sum to ALL_NONUS on every month, measure and lineage of levels_group.csv in $dir."
  else
    printf '%s\n' "$out" | grep '^BAD ' | sed 's/^BAD /  ✗ /'
    printf '%s\n' "$out" | grep -v '^BAD \|^$' | sed 's/^/  ✗ guard error: /'
    echo "  -> raw OFR files stay in data/vintages/mmf_nonus_banks/ (gitignored); fix the build, do not edit the committed tables by hand."
  fi
}

# --- M25: CENSUS PUBLIC-PENSION TOTALS LEAK AND WORDING GUARD (warn only) ------
# data/census_public_pensions/ holds national statistics derived from the Census Bureau's Annual Survey of Public Pensions and nothing raw (spec
# _research/2026-10-26-Census-Public-Pensions-Spec.md, sections 5, 6 and 9.6; build bin/census_public_pensions.py). The unit files and summary workbooks stay in the
# gitignored cache data/vintages/census_public_pensions/. Seven things would break that or the spec's rules, and none is visible to M5-M23:
#   1. a file that is not one of the nine committed names (seven CSVs, README.md, SOURCES.md), a raw file (.dsv, .xlsx, .txt, .pdf, .html, .zip) under any name, and a
#      header line (skipping every "# source:" line) that is not that file's exact column allowlist -- the spec's seven canonical lines, typed here a second time: this
#      guard never reads them from bin/census_public_pensions.py;
#   2. a local path (/Users/, /private/, a tilde), an at sign, a SAMPLE_YEAR line, or a raw unit-file row (the spec's quote-aware pattern, no start-of-line anchor) in any
#      committed file;
#   3. causal, flow, sale or motive wording (the spec's two patterns, pasted) in README.md anywhere but the one denial sentence;
#   4. a national.csv row where employee + government is not total contributions, or net cash is not contributions - benefits - withdrawals (within 0.002 $mn);
#   5. a summary.csv change row inside the old years (2013-2016) or spanning 2016/2017;
#   6. a summary.csv pattern outside above_band, below_band, within_band and n_a;
#   7. a duplicate key in any CSV.
# The script refuses the same things when it writes; this is the second, independent look. CPP_DIR overrides the folder (used to show that the guard fires on a planted
# copy). It warns and never blocks (header doctrine).
cpp_leak_check() {
  echo "-- M25: Census public-pension guard (data/census_public_pensions/: the nine names, exact headers, no raw file, local path, at sign or unit-file row, no causal/flow/sale wording outside the denial sentence, employee + government = total and the net-cash identity on every national row, no change row in the old years or across 2016/2017, four pattern values, no duplicate key) --"
  local dir="${CPP_DIR:-data/census_public_pensions}" f name want got bad="" raw committed out py
  [ -d "$dir" ] || { echo "  ✓ $dir is absent -- nothing to leak."; return; }
  committed=" README.md SOURCES.md national.csv ratios.csv summary.csv revisions.csv checks.csv vintages.csv fetch_log.csv "
  for name in ${committed}; do
    [ -f "$dir/$name" ] || bad="${bad}  ✗ missing: $name
"
  done
  for f in "$dir"/*; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    [ "$name" = ".DS_Store" ] && continue
    raw=""
    case "$name" in *.dsv|*.xlsx|*.xls|*.txt|*.pdf|*.html|*.htm|*.zip|*.gz) raw=1 ;; esac
    [ "$(head -c 2 "$f" | tr -d '\0')" = "PK" ] && raw=1
    head -c 4 "$f" | grep -qF '%PDF' && raw=1
    if [ -n "$raw" ]; then
      bad="${bad}  ✗ raw file in the committed folder (a unit file, workbook, PDF, page or archive): $name
"
      continue
    fi
    if [ "${committed#* $name }" = "$committed" ]; then
      bad="${bad}  ✗ file that is not one of the nine committed names: $name
"
      continue
    fi
    grep -qE '/Users/|/private/|~' "$f" && bad="${bad}  ✗ $name contains a local path (/Users/, /private/ or a tilde)
"
    grep -qF '@' "$f" && bad="${bad}  ✗ $name contains an at sign
"
    want=""
    case "$name" in
      national.csv) want='survey_year,schema,year_kind,contrib_employee_usd_mn,contrib_government_usd_mn,contrib_total_usd_mn,benefits_usd_mn,withdrawals_usd_mn,net_cash_usd_mn,earnings_ex_gains_usd_mn,earnings_old_schema_usd_mn,gains_losses_usd_mn,expenses_admin_invest_usd_mn,assets_end_usd_mn,systems_published,cv_contrib_total,cv_benefits,cv_assets,summary_file_date,source_kind,source_file_date,vintage' ;;
      ratios.csv) want='survey_year,schema,benefits_per_contrib_usd,benefits_withdrawals_per_contrib_usd,net_cash_pct_of_assets_start,net_cash_pct_of_assets_end,income_per_net_cash_gap_usd,income_per_gap_after_expenses_usd,ratio_cv_bound_pct,vintage' ;;
      summary.csv) want='question,segment,from_year,to_year,statistic,value,unit,pattern,primary,vintage' ;;
      revisions.csv) want='survey_year,item,source_prev,date_prev,value_prev_usd_mn,source_new,date_new,value_new_usd_mn,change_usd_mn,change_pct' ;;
      checks.csv) want='check_id,description,expected,observed,status' ;;
      vintages.csv) want='vintage,newest_unit_file,newest_unit_file_date,files,requests,manifest_sha256' ;;
      fetch_log.csv) want='utc_time,host,path,status,bytes,sha256,last_modified' ;;
    esac
    if [ -n "$want" ]; then
      got=$(grep -v '^# source:' "$f" | head -1 | tr -d '\r')
      [ "$got" = "$want" ] || bad="${bad}  ✗ header of $name is not its exact allowlist
"
    fi
  done
  read -r -d '' py <<'PY' || true
import csv, os, re, sys
from decimal import Decimal, InvalidOperation
d = sys.argv[1]
CAUSAL = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b", re.I)
EXTRA = re.compile(r"\b(?:in|out)flows?\b|\bflows?\s+(?:into|out\s+of|from|to)\b|\bnet\s+(?:sell|buy)(?:ers?|ing)\b|\b(?:sell|sells|sold|selling|sale|sales|buy|buys|bought|buying|purchas(?:e|es|ed|ing))\s+(?:of\s+)?(?:equit(?:y|ies)|stocks?|shares|bonds|assets)\b|\bforced\s+(?:sell|sale)\w*|\bliquidat\w*|\bsell[- ]?off\b|\bbid\b|\bdrain\w*|\bdeplet\w*|\bunderfunded\b|\binsolven\w*|\bcrisis\b|\brunning\s+out\b|\bretirement\s+flows?\b", re.I)
RAWROW = re.compile(r'(?<!\d)\d{4}(?:\|[^|\n]*\||,(?:"[^"]*"|[^,"\n]*),)\d{6}[|,][A-Z]{2}[|,]\d[|,]R[XZJP]\d\d[|,]')
DENIAL = "It records the pension systems' own accounts only: a benefit payment is not a sale of equities, a contribution is not a purchase of them, and nothing here shows what the systems bought or sold in markets."
KEYS = {
 "national.csv": ("survey_year",),
 "ratios.csv": ("survey_year",),
 "summary.csv": ("question", "segment", "from_year", "to_year", "statistic"),
 "revisions.csv": ("survey_year", "item", "date_prev", "date_new"),
 "checks.csv": ("check_id",),
 "vintages.csv": ("vintage",),
 "fetch_log.csv": ("utc_time", "path"),
 }
HEADS = {
 "national.csv": "survey_year,schema,year_kind,contrib_employee_usd_mn,contrib_government_usd_mn,contrib_total_usd_mn,benefits_usd_mn,withdrawals_usd_mn,net_cash_usd_mn,earnings_ex_gains_usd_mn,earnings_old_schema_usd_mn,gains_losses_usd_mn,expenses_admin_invest_usd_mn,assets_end_usd_mn,systems_published,cv_contrib_total,cv_benefits,cv_assets,summary_file_date,source_kind,source_file_date,vintage".split(","),
 "summary.csv": "question,segment,from_year,to_year,statistic,value,unit,pattern,primary,vintage".split(","),
 }
PATTERNS = ("above_band", "below_band", "within_band", "n_a")
bad = []
def body(t):
    return [l for l in t.split("\n") if not l.startswith("# source:") and l.strip()]
for n in sorted(os.listdir(d)):
    p = os.path.join(d, n)
    if not os.path.isfile(p) or n == ".DS_Store":
        continue
    t = open(p, encoding="utf-8", errors="replace", newline="").read()
    if n.lower().endswith((".dsv", ".xlsx", ".xls", ".txt", ".pdf", ".html", ".htm", ".zip", ".gz")) or t[:2] == "PK" or t[:4] == "%PDF":
        continue
    if RAWROW.search(t):
        bad.append(n + " holds a raw unit-file row (the spec's quote-aware pattern)")
    if "SAMPLE_YEAR" in t:
        bad.append(n + " holds a unit-file header line (SAMPLE_YEAR)")
    if n == "README.md":
        t2 = t.replace(DENIAL, "", 1)
        hits = sorted({re.sub(r"\s+", " ", m.group(0).lower()) for rx in (CAUSAL, EXTRA) for m in rx.finditer(t2)})
        if hits:
            bad.append("README.md holds banned wording (spec R6): " + ", ".join(hits[:6]))
    if n in KEYS:
        lines = body(t)
        rows = list(csv.reader(lines))
        if not rows:
            continue
        head = rows[0]
        if n in HEADS and head != HEADS[n]:
            continue
        try:
            idx = [head.index(k) for k in KEYS[n]]
        except ValueError:
            continue
        seen, dup = set(), 0
        for r in rows[1:]:
            k = tuple(r[i] if i < len(r) else "" for i in idx)
            if k in seen:
                dup += 1
            seen.add(k)
        if dup:
            bad.append("duplicate key in " + n + " (" + str(dup) + " duplicate row(s))")
        if n == "national.csv" and head == HEADS[n]:
            for r in rows[1:]:
                x = dict(zip(head, r))
                try:
                    e, g, tot = (Decimal(x[k]) for k in ("contrib_employee_usd_mn", "contrib_government_usd_mn", "contrib_total_usd_mn"))
                    b, w, nc = (Decimal(x[k]) for k in ("benefits_usd_mn", "withdrawals_usd_mn", "net_cash_usd_mn"))
                except (InvalidOperation, KeyError):
                    bad.append("national.csv survey year " + x.get("survey_year", "?") + ": a money cell is not a number")
                    continue
                if abs(e + g - tot) > Decimal("0.002"):
                    bad.append("national.csv survey year " + x["survey_year"] + ": employee + government is not total contributions")
                if abs(nc - (tot - b - w)) > Decimal("0.002"):
                    bad.append("national.csv survey year " + x["survey_year"] + ": net cash is not contributions minus benefits minus withdrawals")
        if n == "summary.csv" and head == HEADS[n]:
            for r in rows[1:]:
                x = dict(zip(head, r))
                if x["pattern"] not in PATTERNS:
                    bad.append("summary.csv pattern " + repr(x["pattern"]) + " is not one of the four allowed values")
                if x["statistic"].startswith("change_") and x["from_year"]:
                    a, z = int(x["from_year"]), int(x["to_year"])
                    if a <= 2016 and z <= 2016:
                        bad.append("summary.csv has a change row inside the old schema (" + str(a) + " to " + str(z) + ")")
                    elif a <= 2016 < z:
                        bad.append("summary.csv has a change row spanning 2016/2017 (" + str(a) + " to " + str(z) + ")")
for b in bad:
    print("BAD " + b)
PY
  out=$(python3 -c "$py" "$dir" 2>&1)
  bad="${bad}$(printf '%s\n' "$out" | grep '^BAD ' | sed 's/^BAD /  ✗ /')"
  if [ -z "$(printf '%s' "$bad" | tr -d '\n ')" ]; then
    echo "  ✓ nine names, every header its exact allowlist, no raw file, local path, at sign or unit-file row, no banned wording outside the denial sentence, employee + government = total and the net-cash identity on every national row, no change row in the old years or across 2016/2017, four pattern values and no duplicate key in $dir."
  else
    printf '%s\n' "$bad" | sed '/^$/d'
    echo "  -> raw Census files stay in data/vintages/census_public_pensions/ (gitignored); fix the build, do not edit the committed tables by hand."
  fi
  printf '%s\n' "$out" | grep -v '^BAD \|^$' | sed 's/^/  ✗ guard error: /'
}

# --- M21: H.8 NET DUE TO RELATED FOREIGN OFFICES GUARD (warn only) -----------
# data/h8_foreign_offices/ holds Federal Reserve Board tables (public domain, cited to the Board) and nothing raw (spec
# _research/2026-10-23-H8-Foreign-Offices-Spec.md, sections 5, 6 and 9.5). The raw zip, the DDP packages and the notes page stay in the gitignored cache
# data/vintages/h8_foreign_offices/. Four things would break that or the spec's rules, and none is visible to M5-M19:
#   1. a file that is not one of the ten committed names, a raw file (zip, xml, page, pdf) or a DDP package under any name, and a header line (skipping every
#      "# source:" line) that is not that file's exact column allowlist -- the spec's eight canonical lines, typed here a second time (R2-5): this guard
#      never reads them from bin/h8_foreign_offices.py;
#   2. a local path (/Users/, /private/, a tilde) or an at sign in any committed file;
#   3. causal, flow or motive wording (the spec's two patterns, pasted) anywhere in the folder except the one README denial sentence;
#   4. binding on the latest week of weekly.csv: FRI + DOM = ALL (NSA, usd_mn) and FRI total liabilities below DOM's are errors. By R3-6 the groups are bound
#      by identities and never by sign: a negative FRI level from 2019-01-02 on is a warning, not an error.
# bin/h8_foreign_offices.py refuses the same things when it writes; this is the second, independent look. H8FO_DIR overrides the folder (used to show that
# the guard fires on a planted copy). It warns and never blocks (header doctrine).
h8fo_leak_check() {
  echo "-- M21: H.8 foreign-offices guard (data/h8_foreign_offices/: the ten names, exact headers, no raw file, local path or at sign, no causal/flow/motive wording outside the denial sentence, FRI + DOM = ALL on the latest week; a negative FRI level only warns) --"
  local dir="${H8FO_DIR:-data/h8_foreign_offices}" f name want got bad="" raw committed out py
  [ -d "$dir" ] || { echo "  ✓ $dir is absent -- nothing to leak."; return; }
  committed=" README.md SOURCES.md weekly.csv quarter_ends.csv notes.csv revisions.csv vintages.csv summary.csv checks.csv fetch_log.csv "
  for name in ${committed}; do
    [ -f "$dir/$name" ] || bad="${bad}  ✗ missing: $name
"
  done
  for f in "$dir"/*; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    [ "$name" = ".DS_Store" ] && continue
    raw=""
    case "$name" in *.zip|*.xml|*.htm|*.html|*.pdf|*.xsd|*.gz) raw=1 ;; esac
    [ "$(head -c 2 "$f" | tr -d '\0')" = "PK" ] && raw=1
    head -c 4 "$f" | grep -qF '%PDF' && raw=1
    case "$name" in *.csv) grep -v '^# source:' "$f" | head -1 | grep -q '^"Series Description"' && raw=1 ;; esac
    if [ -n "$raw" ]; then
      bad="${bad}  ✗ raw file in the committed folder (a zip, XML, page, PDF or DDP package): $name
"
      continue
    fi
    if [ "${committed#* $name }" = "$committed" ]; then
      bad="${bad}  ✗ file that is not one of the ten committed names: $name
"
      continue
    fi
    grep -qE '/Users/|/private/|~' "$f" && bad="${bad}  ✗ $name contains a local path (/Users/, /private/ or a tilde)
"
    grep -qF '@' "$f" && bad="${bad}  ✗ $name contains an at sign
"
    want=""
    case "$name" in
      weekly.csv) want='week_wed,group,sa,series_id,usd_mn,change_usd_mn,total_liabilities_usd_mn,pct_of_total_liabilities,qe_quarter,qe_role,qe_offset_days,segment_start,note_flag,vintage' ;;
      quarter_ends.csv) want='quarter,qe_date,qe_wed,offset_days,on_date,group,level_qe_wed_usd_mn,delta_qe_wed_usd_mn,delta_next_usd_mn,qe_day_in_window,straddles_break,frozen_set,blind,vintage' ;;
      notes.csv) want='note_week,group,line38_effect_usd_mn,kind,paragraph_index,text_head' ;;
      revisions.csv) want='vintage_prev,vintage_new,series_id,week_wed,usd_mn_prev,usd_mn_new,change_usd_mn' ;;
      vintages.csv) want='vintage,route,xml_prepared,xml_last_modified,xml_sha256,ddp_status,latest_week,rows_fri_nsa' ;;
      summary.csv) want='question,window,group,statistic,value,unit,blind' ;;
      checks.csv) want='check_id,description,expected,observed,status' ;;
      fetch_log.csv) want='utc_time,host,path_and_query,status,bytes,sha256' ;;
    esac
    if [ -n "$want" ]; then
      got=$(grep -v '^# source:' "$f" | head -1 | tr -d '\r')
      [ "$got" = "$want" ] || bad="${bad}  ✗ header of $name is not its exact allowlist
"
    fi
  done
  read -r -d '' py <<'PY' || true
import csv, os, re, sys
d = sys.argv[1]
CAUSAL = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b", re.I)
EXTRA = re.compile(r"\b(?:in|out)?flows?\b|window[- ]dressing|\b(?:head\s+offices?|parents?)\s+(?:fund|funds|funded|funding|push|pushes|pushed|pull|pulls|pulled|drain|drains|drained)\b|\b(?:dollar\s+)?(?:shortage|squeeze)\b", re.I)
DENIAL = "These weekly changes are not flows of funds, and the table does not test window dressing or any other motive."
HEAD = "week_wed,group,sa,series_id,usd_mn,change_usd_mn,total_liabilities_usd_mn,pct_of_total_liabilities,qe_quarter,qe_role,qe_offset_days,segment_start,note_flag,vintage".split(",")
bad, warn = [], []
for name in ("README.md", "SOURCES.md", "weekly.csv", "quarter_ends.csv", "notes.csv", "revisions.csv", "vintages.csv", "summary.csv", "checks.csv", "fetch_log.csv"):
    p = os.path.join(d, name)
    if not os.path.isfile(p):
        continue
    t = open(p, encoding="utf-8", errors="replace").read()
    if name == "README.md":
        t = t.replace(DENIAL, "", 1)
    hits = sorted({re.sub(r"\s+", " ", m.group(0).lower()) for rx in (CAUSAL, EXTRA) for m in rx.finditer(t)})
    if hits:
        bad.append("%s holds banned wording (spec R5): %s" % (name, ", ".join(hits[:4])))
p = os.path.join(d, "weekly.csv")
if os.path.isfile(p):
    lines = [l for l in open(p, encoding="utf-8", errors="replace").read().splitlines() if not l.startswith("# source:")]
    rows = list(csv.reader(lines))
    if rows and rows[0] == HEAD and len(rows) > 1:
        rows = [dict(zip(HEAD, r)) for r in rows[1:]]
        last = max(r["week_wed"] for r in rows)
        cur = {}
        for r in rows:
            if r["week_wed"] == last and r["sa"] == "NSA":
                cur.setdefault(r["group"], []).append(r)
        if sorted(cur) != ["ALL", "DOM", "FRI"] or any(len(v) != 1 for v in cur.values()):
            bad.append("weekly.csv, latest week %s: expected one NSA row each for FRI, DOM and ALL, found %s" % (last, {g: len(v) for g, v in sorted(cur.items())}))
        else:
            f, m, a = (float(cur[g][0]["usd_mn"]) for g in ("FRI", "DOM", "ALL"))
            ft, mt = float(cur["FRI"][0]["total_liabilities_usd_mn"]), float(cur["DOM"][0]["total_liabilities_usd_mn"])
            if abs(f + m - a) > 0.5:
                bad.append("weekly.csv, latest week %s: FRI + DOM = %.1f but ALL = %.1f" % (last, f + m, a))
            elif not ft < mt:
                bad.append("weekly.csv, latest week %s: FRI total liabilities %.1f is not below DOM's %.1f (groups mislabelled?)" % (last, ft, mt))
        neg = sorted(r["week_wed"] for r in rows if r["group"] == "FRI" and r["sa"] == "NSA" and r["week_wed"] >= "2019-01-02" and float(r["usd_mn"]) < 0)
        if neg:
            warn.append("FRI NSA is negative on %d week(s) from 2019-01-02 (%s...): a warning only, groups are bound by identities not sign" % (len(neg), neg[0]))
for b in bad:
    print("BAD " + b)
for w in warn:
    print("WARN " + w)
PY
  out=$(python3 -c "$py" "$dir" 2>&1)
  bad="${bad}$(printf '%s\n' "$out" | grep '^BAD ' | sed 's/^BAD /  ✗ /')"
  if [ -z "$(printf '%s' "$bad" | tr -d '\n ')" ]; then
    echo "  ✓ ten names, every header its exact allowlist, no raw file, local path or at sign, no banned wording outside the denial sentence, FRI + DOM = ALL and FRI total liabilities below DOM's on the latest week of weekly.csv in $dir."
  else
    printf '%s\n' "$bad" | sed '/^$/d'
    echo "  -> raw Board files stay in data/vintages/h8_foreign_offices/ (gitignored); fix the build, do not edit the committed tables by hand."
  fi
  printf '%s\n' "$out" | grep '^WARN ' | sed 's/^WARN /  ⚠ /'
  printf '%s\n' "$out" | grep -v '^BAD \|^WARN \|^$' | sed 's/^/  ✗ guard error: /'
}

# --- M20: BIS INTERNATIONAL DEBT SECURITIES (US DOLLARS) LEAK AND WORDING GUARD (warn only) ----------------------------------------------------------
# data/bis_ids_dollar/ holds BIS-derived quarterly aggregates and statistics derived from them, never the raw SDMX replies (spec
# _research/2026-10-23-BIS-IDS-Dollar-Spec.md, sections 5 and 6; build bin/bis_ids_dollar.py). The raw replies stay in the gitignored cache
# data/vintages/bis_ids_dollar/. Five things would break that, and none is visible to M5-M19:
#   1. a file in the folder that is not one of the 11 names (nine CSVs, README.md, SOURCES.md), and a missing one;
#   2. a header line (skipping every "# source:" line) that is not that file's exact column allowlist (the spec's canonical text, typed here a third time,
#      after ALLOW and SPEC_ALLOW_TEXT in the script);
#   3. a raw SDMX file: ANY line beginning FREQ,ISSUER_RES or FREQ,L_MEASURE, or a body holding "dataStructures" (a "# source:" line in front does not hide it),
#      in the folder or, for a JSON body or a line-start header, anywhere else the repository would commit (the gitignored cache is not looked at);
#   4. an at sign, or a local path (/Users/, /private/, /tmp/, ~/), in any file of the folder;
#   5. a match of the spec's literal causal pattern (6.3) in the README.
# bin/bis_ids_dollar.py refuses the same things when it writes (G11, G12, G16); this is the second, independent look. BISIDS_DIR and BISIDS_ROOT override the
# folder and the repository root (used to show that the guard fires on planted files). It warns and never blocks (header doctrine).
bisids_leak_check() {
  echo "-- M20: BIS IDS dollar guard (data/bis_ids_dollar/: the 11 names, exact headers, no raw SDMX file outside the cache, no at sign, no local path, no causal wording in the README) --"
  local dir="${BISIDS_DIR:-data/bis_ids_dollar}" root="${BISIDS_ROOT:-.}" py out
  [ -d "$dir" ] || { echo "  ✓ $dir is absent -- nothing to leak."; return; }
  read -r -d '' py <<'PY' || true
import os, re, subprocess, sys
d, root = sys.argv[1], sys.argv[2]
want = {
 "quarterly.csv": "quarter,basis,issuer_group,sector,outstanding_usd_m,net_issues_usd_m,change_in_outstanding_usd_m,other_change_usd_m,status,derived,vintage,ids_release",
 "shares.csv": "quarter,issuer_group,sector,share_pct,numerator_usd_m,denominator_usd_m,denominator",
 "net_issues_windows.csv": "window,first_quarter,last_quarter,issuer_group,sector,quarters_n,quarters_blank,net_issues_usd_m,change_in_outstanding_usd_m,other_change_usd_m,share_of_group_net_issues_pct,denominator",
 "cgfs_check.csv": "variant,plain_name,definition,first_quarter,last_quarter,ids_change_usd_m,lbs_change_usd_m,lbs_measure,lbs_flow_sum_usd_m,lbs_break_sum_usd_m,lbs_break_quarters,ids_share_of_increase_pct,denominator,reading,note",
 "summary.csv": "question,window,issuer_group,sector,statistic,value,denominator,blind",
 "revisions.csv": "vintage_prev,vintage_new,quarter,basis,issuer_group,sector,measure,value_prev_usd_m,value_new_usd_m,change_usd_m,change_pct",
 "registration_score.csv": "registered_on,scored_on,vintage_prev,vintage_new,latest_quarter_new,cells_checked,largest_abs_change_pct,largest_cell,threshold_pct,result,note",
 "checks.csv": "check_id,description,expected,observed,status",
 "fetch_log.csv": "utc_time,host,path_and_query,status,bytes,sha256",
}
names = set(want) | {"README.md", "SOURCES.md"}
raw_rx = re.compile(r"^FREQ,(ISSUER_RES|L_MEASURE)", re.M)
path_rx = re.compile(r"/Users/|/private/|/tmp/|~/")
causal = re.compile(r"\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of|fuell?ed)\b", re.I)
bad = []
here = set()
for n in sorted(os.listdir(d)):
    p = os.path.join(d, n)
    if not os.path.isfile(p) or n == ".DS_Store":
        continue
    here.add(n)
    t = open(p, encoding="utf-8", errors="replace", newline="").read()
    raw = bool(raw_rx.search(t)) or '"dataStructures"' in t
    if raw:
        bad.append("raw SDMX file in the committed folder: " + n)
    elif n not in names:
        bad.append("file that is not one of the 11 committed names: " + n)
    if path_rx.search(t):
        bad.append(n + " contains a local path (/Users/, /private/, /tmp/ or ~/)")
    if "@" in t:
        bad.append(n + " contains an at sign")
    if n in want and not raw:
        hdr = next((l.rstrip("\r") for l in t.split("\n") if not l.startswith("# source:")), "")
        if hdr != want[n]:
            bad.append("header of " + n + " is not its exact allowlist")
    if n == "README.md":
        for m in sorted({re.sub(r"\s+", " ", x.group(0).lower()) for x in causal.finditer(t)}):
            bad.append("causal wording in README.md: '" + m + "'")
for n in sorted(names - here):
    bad.append("missing: " + n)
# the rest of the repository: files git would commit (tracked, or untracked and not ignored), outside the folder itself
try:
    r = subprocess.run(["git", "-C", root, "ls-files", "-co", "--exclude-standard", "-z"], capture_output=True, timeout=120)
    files = [os.path.join(root, x) for x in r.stdout.decode("utf-8", "replace").split("\0") if x] if r.returncode == 0 else None
except Exception:
    files = None
if files is None:
    files = [os.path.join(dp, f) for dp, dn, fn in os.walk(root) if ".git" not in dp.split(os.sep) for f in fn]
dreal = os.path.realpath(d)
for p in files:
    rp = os.path.realpath(p)
    if rp.startswith(dreal + os.sep) or not os.path.isfile(p) or os.path.islink(p):
        continue
    try:
        if os.path.getsize(p) > 200 * 1024 * 1024:
            continue
        b = open(p, "rb").read()
    except OSError:
        continue
    if b"FREQ,ISSUER_RES" not in b and b"FREQ,L_MEASURE" not in b and b'"dataStructures"' not in b:
        continue
    t = b.decode("utf-8", "replace")
    if raw_rx.search(t) or (t.lstrip().startswith("{") and '"dataStructures"' in t):
        bad.append("raw SDMX file outside the cache: " + os.path.relpath(p, root))
print("\n".join("  ✗ " + x for x in bad) if bad else "OK")
PY
  out=$(python3 -c "$py" "$dir" "$root")
  if [ "$out" = "OK" ]; then
    echo "  ✓ the 11 committed names, every header its exact allowlist, no raw SDMX file anywhere the repository would commit, no at sign or local path, no causal wording in the README ($dir)."
  else
    printf '%s\n' "$out"
    echo "  -> BIS terms: only selected quarterly aggregates and statistics derived from them may be committed; raw replies stay in data/vintages/bis_ids_dollar/. Remove the file before any commit."
  fi
}

# --- HANDOVER ----------------------------------------------------------------
# Two agents work this folder (E-006), never at the same time, routed by whichever
# token budget the principal has. A handover is written after EVERY work parcel,
# not once a session.
#
# Two things this must do, and a third it must NOT do:
#   1. INTEGRITY. The principal never runs us simultaneously -- but Dropbox does not
#      know that. This is an SMB mount with asynchronous sync: an agent opening it
#      mid-sync reads a TORN tree, some files new and some old, and every other guard
#      here passes, because each file is individually valid and only the SET is wrong.
#      That is this project's signature failure -- internally consistent and untrue
#      (E-000, C-081). So the departing agent stamps counts; the arriving one re-derives.
#   2. DELTA, NOT STATE. The arriving agent must not have to read CORRECTIONS.md (1.4k
#      lines), RESEARCH_STATE.md (over the Read cap) or 100 findings docs to start. It
#      needs what CHANGED since the last stamp. That is a query, and it is ~20 lines.
#   3. NOT a database. SQLite was considered and rejected twice: it is a binary file on
#      a syncing share (Dropbox conflict-copies it, and POSIX advisory locks are not
#      reliable over SMB), and a derived store is a second home for facts the text files
#      already own -- the exact drift M5/M6/M7 exist to stop. At this size (86
#      corrections, 359 series rows, ~101 docs) grep answers in milliseconds. Revisit
#      only if a query needs a real join across files, or series.tsv passes ~50k rows;
#      then build it READ-ONLY and DERIVED, rebuilt from the text on demand, never the
#      source of truth.
#
TODAY="${CHECK_TODAY:-$(date +%F)}"

# HANDOVER.tsv columns: stamped_at  agent  parcel  status  fields  next
handover_fields() {
  local corr maxc ask series docs cal
  corr=$(grep -cE '^## C-[0-9]+' CORRECTIONS.md 2>/dev/null || echo 0)
  maxc=$(grep -oE '^## C-[0-9]+' CORRECTIONS.md 2>/dev/null | sed 's/.*C-//' | sort -n | tail -1)
  maxc=$((10#${maxc:-0}))
  ask=$(grep -cE '^## E-0[0-9]+' THE_ASK.md 2>/dev/null || echo 0)
  series=$(( $(wc -l < data/series.tsv 2>/dev/null || echo 1) - 1 ))
  docs=$(find . -mindepth 1 -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')
  # Data rows (5 tab-separated fields), not newlines: CALENDAR.tsv has a blank line 56 and no trailing newline, so
  # wc -l - 1 was right only by coincidence and would flip to 56 the day an editor added the final newline.
  cal=$(awk -F'\t' 'NR>1 && NF>=5' CALENDAR.tsv 2>/dev/null | wc -l | tr -d ' ')
  printf 'corrections=%s max=C-%03d ask=%s series=%s docs=%s calendar=%s' \
    "$corr" "$maxc" "$ask" "$series" "$docs" "$cal"
}

if [ "${1:-}" = "--handover" ]; then
  CUR=$(handover_fields)
  if [ "${2:-}" = "write" ]; then
    WHO="${3:-unknown}"; PARCEL="${4:-unnamed}"; STATUS="${5:-done}"; shift 5 2>/dev/null || shift $#
    NEXT="$*"; [ -z "$NEXT" ] && NEXT="(none stated)"
    # A newline or tab in a note splits the TSV row (18 Sep: a $1 inside double quotes expanded to a
    # 25-line script). Collapse both to spaces and cap the length, so a bad call degrades, not corrupts.
    NEXT=$(printf '%s' "$NEXT" | tr '\n\t' '  ' | cut -c1-400)
    PARCEL=$(printf '%s' "$PARCEL" | tr '\n\t' '  ' | cut -c1-60)
    [ -f HANDOVER.tsv ] || printf 'stamped_at\tagent\tparcel\tstatus\tfields\tnext\n' > HANDOVER.tsv
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$(date +%FT%T)" "$WHO" "$PARCEL" "$STATUS" "$CUR" "$NEXT" >> HANDOVER.tsv
    echo "== handover written =="
    echo "  $WHO / $PARCEL / $STATUS"
    echo "  next: $NEXT"
    echo "  $CUR"
    exit 0
  fi
  if [ ! -f HANDOVER.tsv ] || [ "$(wc -l < HANDOVER.tsv | tr -d ' ')" -le 1 ]; then
    echo "== HANDOVER == (no stamp yet -- first parcel)"
    echo "  now: $CUR"
    echo "  write one when you stop:  bin/check.sh --handover write <claude|grok> <parcel> <done|paused|blocked> <next step>"
    exit 0
  fi
  BAD=$(awk -F'\t' 'NF!=6' HANDOVER.tsv | wc -l | tr -d ' ')
  if [ "$BAD" -gt 0 ]; then
    echo "  ✗ HANDOVER.tsv HAS $BAD MALFORMED LINE(S) (not 6 tab-separated fields). A note containing"
    echo "    a newline or tab has split a row. Most likely cause: a \$ figure inside DOUBLE quotes, e.g."
    echo "    \"debit \$1,453.8bn\" expands \$1. Single-quote the next-step text. Lines:"
    awk -F'\t' 'NF!=6{printf "      %d\n", NR}' HANDOVER.tsv | head -5
  fi
  LAST=$(tail -1 HANDOVER.tsv)
  LWHEN=$(printf '%s' "$LAST" | cut -f1); LWHO=$(printf '%s' "$LAST" | cut -f2)
  LFIELDS=$(printf '%s' "$LAST" | cut -f5)
  echo "== HANDOVER =="
  if [ "$CUR" = "$LFIELDS" ]; then
    echo "  ✓ integrity: tree matches the stamp $LWHO left at $LWHEN -- safe to read."
  else
    echo "  ✗ integrity: MISMATCH against $LWHO's stamp at $LWHEN."
    echo "      stamped: $LFIELDS"
    echo "      now:     $CUR"
    echo "    Either Dropbox has not finished syncing, or the last agent edited after"
    echo "    stamping. STOP -- wait, re-run; if it still differs ask the principal who"
    echo "    wrote last. A torn tree passes EVERY other guard in this script."
  fi
  echo
  echo "-- last 3 parcels --"
  # Last 3 DISTINCT parcels, not last 3 rows. Agents stamp more than once per parcel --
  # observed on 8 of them, from both agents, one three times -- so a row-based tail wastes
  # the history window on repeats. Keep the LAST row for each (agent, parcel) and show three
  # of those. The log stays append-only; only the reader dedupes.
  tail -n +2 HANDOVER.tsv \
    | awk -F'\t' '{k=$2"|"$3; line[k]=$0; seq[k]=NR} END{for(k in line) print seq[k]"\t"line[k]}' \
    | sort -n | cut -f2- | tail -3 \
    | awk -F'\t' '{printf "  %s  %-6s %-22s %-8s next: %s\n",substr($1,1,16),$2,substr($3,1,22),$4,substr($6,1,70)}'
  echo
  echo "-- changed since that stamp (names only; read only what you need) --"
  CH=$(find . -mindepth 1 -maxdepth 2 \( -name '*.md' -o -name '*.tsv' -o -name '*.sh' -o -name '*.py' \) \
         -newer HANDOVER.tsv -not -path './_research/snapshot_*' 2>/dev/null | sed 's|^\./|  |' | sort | head -20)
  [ -z "$CH" ] && echo "  (nothing)" || printf '%s\n' "$CH"
  LMAX=$(printf '%s' "$LFIELDS" | sed 's/.*max=C-\([0-9]*\).*/\1/')
  NEWC=$(grep -oE '^## C-[0-9]+.*' CORRECTIONS.md 2>/dev/null | awk -v m="$((10#${LMAX:-0}))" \
         '{n=$2; gsub(/[^0-9]/,"",n); if (n+0 > m) print "  "substr($0,4,100)}' | head -10)
  echo
  echo "-- corrections registered since that stamp --"
  [ -z "$NEWC" ] && echo "  (none)" || printf '%s\n' "$NEWC"
  echo
  echo "-- due now --"
  # A row is FINISHED when its status BEGINS with "done" in any case: "done", "DONE", "DONE 3 Oct",
  # "DONE 4 Oct (unverified by supervisor)". The old filter (tolower($5)!="done") listed every annotated DONE row as
  # due, so 8 of 9 lines on 8 Oct were finished work, and head -10 would have cut off a real overdue row.
  # A row needs a date in column 1 and 5 fields: the blank line 56 of CALENDAR.tsv printed an empty "DUE" line.
  # The count is printed from the same pass, so it is the true number, not the number that fit under the cap.
  # CHECK_TODAY=YYYY-MM-DD overrides today's date (testing: "what would be due on the 16th?").
  awk -F'\t' -v d="$TODAY" -v cap=15 '
    NR>1 && NF>=5 && $1 ~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/ {
      rows++
      if (tolower($5) !~ /^[ ]*done/) {
        open++
        if ($1<=d) { due++; if (due<=cap) print "  DUE "$1"  "substr($2,1,80) }
      }
    }
    END {
      if (due>cap) printf "  ... %d more due, not shown (see bin/check.sh --todo)\n", due-cap
      printf "  (%d due now; %d of %d calendar rows are not done)\n", due, open, rows
    }' CALENDAR.tsv 2>/dev/null
  echo
  echo "  (then: bin/check.sh --todo for the ranked list. Write a handover after EVERY parcel.)"
  exit 0
fi

if [ "${1:-}" = "--goal" ]; then goal_check; exit 0; fi
if [ "${1:-}" = "--todo" ]; then
  # M1 (rung-5 amended) -- a VIEW over RESEARCH_STATE.md's fenced ranked block (opening
  # fence ```ranked), same awk shape as goal_check. Missing fence -> loud WARN, not silence
  # (the pre-amendment bug: this command used to show nothing wrong while section 5 held
  # zero current-priority markers). Empty fence -> neutral note, not a failure. Exit 0
  # always either way -- see header doctrine ("a blocking gate gets reworded around").
  echo "== RESEARCH_STATE.md section 5 -- ranked block (query, not a copy) =="
  if ! grep -q '^```ranked$' RESEARCH_STATE.md 2>/dev/null; then
    echo "  ✗ RANKED FENCE MISSING from RESEARCH_STATE.md -- expected an opening fence line of"
    echo "    three backticks followed by the word ranked. Cannot show ranked items."
    echo "    Fix the fence name -- do not silence this line."
  else
    RANKED=$(awk '/^```ranked$/{f=1;next} /^```$/{f=0} f' RESEARCH_STATE.md)
    if [ -z "$(printf '%s' "$RANKED" | sed '/^[[:space:]]*$/d')" ]; then
      echo "  (fence present, no ranked items -- caught up, or not yet ranked?)"
    else
      printf '%s\n' "$RANKED"
    fi
  fi
  echo; echo "== CALENDAR.tsv -- next 45 days =="
  # Same status rule as the handover's due-now list: "done"/"DONE"/"DONE 3 Oct" are finished (this used a case-sensitive
  # $5!="done", so every annotated DONE row listed as upcoming); blank lines are not rows; the count is the true one.
  E45=$(date -j -v+45d -f %F "$TODAY" +%F 2>/dev/null || date -d "$TODAY +45 days" +%F)
  awk -F'\t' -v e="$E45" '
    NR>1 && NF>=5 && $1 ~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/ && tolower($5) !~ /^[ ]*done/ {
      open++
      if ($1<=e) { n++; print "  "$1"  "substr($2,1,100) | "sort" }
    }
    END { close("sort"); printf "  (%d rows due within 45 days; %d rows not done in all)\n", n, open }' CALENDAR.tsv
  echo; echo "== data/series.tsv -- latest vintage per series =="
  [ -f data/series.tsv ] && awk -F'\t' 'NR>1{last[$2]=$1"  as_of "$3"  "$4" "$5} END{for(k in last) printf "  %-42s %s\n",k,last[k]}' data/series.tsv | sort || echo "  (no data/series.tsv yet -- run bin/pull_series.py)"
  exit 0
fi
if [ "${1:-}" = "--latest" ]; then
  # M2 -- newest corrections first. Was: cat CORRECTIONS.md | head -40 in CLAUDE.md's
  # first-action block, which always surfaces C-001..003 and never the newest entries.
  echo "== CORRECTIONS.md -- newest corrections (query, not a copy) =="
  # Sort by NUMBER, not by file position. This used to be "| tail -5", which assumed
  # entries are appended at the end. They are not: from C-077 on they are inserted
  # newest-FIRST, so tail -5 returned the five OLDEST of that block and C-082..C-086
  # were invisible here -- in the first-action path both agents run. Found 15 Sep 2026
  # while picking up a handover; the 14 Sep cold-start test ran this command and missed it.
  grep -E '^## C-[0-9]+' CORRECTIONS.md \
    | awk '{n=$2; gsub(/[^0-9]/,"",n); print n"\t"$0}' | sort -n | tail -5 | cut -f2-
  exit 0
fi
goal_check
echo

BANNED=$(awk '/^```banned$/{f=1;next} /^```$/{f=0} f' CORRECTIONS.md)
ALLOW=$(awk '/^```allow$/{f=1;next} /^```$/{f=0} f' CORRECTIONS.md)
[ -z "$BANNED" ] && exit 0

TARGET="${1:---all}"
if [ "$TARGET" = "--all" ]; then
  FILELIST=$(find . -maxdepth 2 -name '*.md' -not -path './_research/*' -not -name 'CORRECTIONS.md')
  orphan_check
  echo
  secondhome_check
  echo
  unregistered_correction_check
  echo
  duplicate_correction_check
  echo
  swaptape_leak_check
  echo
  ua_check
  icebrent_leak_check
  r15_leak_check
  echo
  goldry_leak_check
  echo
  jodi_leak_check
  echo
  hedged_leak_check
  echo
  jp_life_leak_check
  echo
  japan_tp_leak_check
  echo
  ukgold_leak_check
  echo
  futidx_leak_check
  echo
  qeb_leak_check
  echo
  h8fo_leak_check
  echo
  bisids_leak_check
  echo
  mmfnb_leak_check
  echo
  cpp_leak_check
  echo
else
  FILELIST=$(printf '%s\n' "$@")
fi
[ -z "$FILELIST" ] && exit 0

# --- Validate every pattern BEFORE using it. ---------------------------------
# Both greps below pass the pattern with -e. Without it, any pattern BEGINNING
# WITH '-' is consumed by grep as an option bundle: it matches nothing, raises no
# error, and the validator above passes it as 'usable'. Found 15 Sep 2026 while
# registering C-088, whose first pattern was '-52\.0%' and enforced nothing.
# ugrep rejects >1 bounded repeat combined with an alternation ("exceeds complexity
# limits"). The old loop sent stderr to /dev/null, so an invalid pattern matched
# nothing, reported nothing, and the run still printed the all-clear. C-017, C-020
# and C-030 were dead that way for a day; C-030 had never been enforced at all.
# A ban list that cannot be trusted to run is worse than none: it grants false
# confidence. This block makes an unusable pattern loud and non-silent.
badpat=0
while IFS=$'\t' read -r id rx; do
  [ -z "${rx:-}" ] && continue
  if err=$(printf 'x\n' | grep -nEi -e "$rx" 2>&1 >/dev/null); [ -n "$err" ]; then
    printf '  ✗ UNUSABLE PATTERN  [%s]  %s\n' "$id" "$(printf '%s' "$rx" | cut -c1-70)"
    printf '      engine says: %s\n' "$(printf '%s' "$err" | head -1 | cut -c1-90)"
    badpat=$((badpat+1))
  fi
done <<< "$BANNED"
if [ "$badpat" -gt 0 ]; then
  printf '\n⚠  %d ban pattern(s) CANNOT RUN and are enforcing nothing.\n' "$badpat"
  echo '   Split each into several same-id lines with one bounded repeat each.'
  echo '   See the ENGINE CONSTRAINT note in CORRECTIONS.md. Fix before trusting any result below.'
  echo
fi

# Speed (9 Oct 2026). This loop was pattern x file: 237 x 136 = 32,232 pairs, each spawning an allow-list grep and a scan
# grep (~6 ms a pair, about 195 s of the 197 s a full --all run took; the structural checks and the page check take
# under 3 s together). Now ONE grep -l per pattern over every file names the few files that match at all; the per-file
# allow test and line scan below are unchanged and run only for those, so output, order and attribution are identical.
# Files that do not exist are dropped up front (the old loop skipped them with [ -f ]).
FILES=()
while IFS= read -r f; do
  [ -f "$f" ] && FILES+=("$f")
done <<< "$FILELIST"

hits=0
while IFS=$'\t' read -r id rx; do
  [ -z "${rx:-}" ] && continue
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    base="${f##*/}"
    if printf '%s\n' "$ALLOW" | grep -qE "^${id}[[:space:]]+${base}([[:space:]]|$)"; then continue; fi
    while IFS=: read -r ln text; do
      [ -z "${ln:-}" ] && continue
      printf '  [%s] %s:%s  %s\n' "$id" "${f#./}" "$ln" "$(printf '%s' "$text" | cut -c1-86)"
      hits=$((hits+1))
    done < <(grep -nEi -e "$rx" "$f" 2>/dev/null | grep -vE '^[0-9]+:[[:space:]]*>' || true)
  done < <(grep -lEi -e "$rx" ${FILES[@]+"${FILES[@]}"} 2>/dev/null || true)
done <<< "$BANNED"

echo
if [ "$hits" -gt 0 ]; then
  printf '⚠  %d occurrence(s) of claims killed in CORRECTIONS.md.\n' "$hits"
  echo '   Check each against the correct position before shipping. Warning, not a block.'
elif [ "$badpat" -gt 0 ]; then
  echo '✗ no killed claims found among the patterns that RUN — but some do not run. See above.'
else
  echo '✓ no killed claims found, and all ban patterns are valid.'
fi

# -- page check (23 Sep) --------------------------------------------------------
# The published page is a rendering OUTSIDE the *.md scan above. It went stale twice (C-083 for four days;
# C-106/C-116/C-117 later) because claims were killed AFTER it was published and nothing re-scanned it.
# Its durable source lives at docs/index.html (moved 24 Sep, E-012, so GitHub can serve it) and is checked on every --all run. check_page.py strips tags per
# line, so it catches phrases an HTML tag splits -- C-116's "13x the <span>$86.2bn</span>" slipped past
# the raw scan above when it was pointed at the page.
if [ "$TARGET" = "--all" ]; then
  echo
  echo "-- page check: docs/index.html (source of the published page) --"
  if [ -f docs/index.html ]; then python3 bin/check_page.py docs/index.html
  else echo "  ✗ docs/index.html missing -- the published page has no checked source."; fi
fi
exit 0
