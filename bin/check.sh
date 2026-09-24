#!/bin/bash
# Warn (never block) if a draft restates a claim killed in CORRECTIONS.md.
# Usage:  bin/check.sh FILE [FILE...]   |   bin/check.sh --all
#         --goal | --latest | --todo | --handover [write <claude|grok>]
# Exit 0 always. A blocking gate gets reworded around; a warning leaves a trail.
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
# HANDOVER.tsv columns: stamped_at  agent  parcel  status  fields  next
handover_fields() {
  local corr maxc ask series docs cal
  corr=$(grep -cE '^## C-[0-9]+' CORRECTIONS.md 2>/dev/null || echo 0)
  maxc=$(grep -oE '^## C-[0-9]+' CORRECTIONS.md 2>/dev/null | sed 's/.*C-//' | sort -n | tail -1)
  maxc=$((10#${maxc:-0}))
  ask=$(grep -cE '^## E-0[0-9]+' THE_ASK.md 2>/dev/null || echo 0)
  series=$(( $(wc -l < data/series.tsv 2>/dev/null || echo 1) - 1 ))
  docs=$(find . -mindepth 1 -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')
  cal=$(( $(wc -l < CALENDAR.tsv 2>/dev/null || echo 1) - 1 ))
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
  awk -F'\t' -v d=$(date +%F) 'NR>1 && $1<=d && tolower($5)!="done" {print "  DUE "$1"  "substr($2,1,80)}' CALENDAR.tsv 2>/dev/null | head -10
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
  awk -F'\t' -v d=$(date +%F) -v e=$(date -v+45d +%F 2>/dev/null || date -d "+45 days" +%F) 'NR>1 && $5!="done" && $1<=e {print "  "$1"  "substr($2,1,100)}' CALENDAR.tsv | sort
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
  done <<< "$FILELIST"
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
# Its durable source lives in the vault and is checked on every --all run. check_page.py strips tags per
# line, so it catches phrases an HTML tag splits -- C-116's "13x the <span>$86.2bn</span>" slipped past
# the raw scan above when it was pointed at the page.
if [ "$TARGET" = "--all" ] && [ -f _research/artifact/state-of-play.html ]; then
  echo
  echo "-- page check: _research/artifact/state-of-play.html (source of the published page) --"
  python3 bin/check_page.py _research/artifact/state-of-play.html
fi
exit 0
