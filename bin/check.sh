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
