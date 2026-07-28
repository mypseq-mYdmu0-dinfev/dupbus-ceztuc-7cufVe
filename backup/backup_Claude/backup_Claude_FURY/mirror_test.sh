#!/bin/bash
#
# mirror_test.sh —— regression test for mirror.sh.
#
# WHAT IT PINS
#   The defect mirror.sh exists to kill: a live file under ~/.claude changes and the
#   snapshot in this folder silently stays stale, so a restore quietly reinstates an
#   old configuration. Test 2 encodes exactly that scenario; test 3 proves the repair.
#   The remaining tests pin the three conditions a static file list would MISS —— a new
#   live file nobody mirrored, a backup whose source is unknown, and a source that has
#   been deleted upstream.
#
# SAFETY
#   Runs entirely against fixtures in a temp dir via the CLAUDE_HOME and BACKUP_DIR
#   overrides. It never reads, writes, or even resolves the real /Volumes/FURY 2TB/
#   .claude folder, so it is safe to run at any time.
#
# USAGE
#   ./mirror_test.sh          exit 0 = all pass; exit 1 = a failure is printed

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
SUT="$HERE/mirror.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT   # guaranteed cleanup on the exception path too

pass=0
fail=0

ok()   { pass=$((pass + 1)); echo "  pass  $1"; }
bad()  { fail=$((fail + 1)); echo "  FAIL  $1"; }

# Assert a run's exit code and that its output does (or does not) contain a marker.
# Usage: expect <label> <want_exit> <want_substr|-> <not_substr|-> <mode>
expect() {
  local label="$1" want="$2" yes="$3" no="$4" mode="$5" out rc
  out="$(CLAUDE_HOME="$TMP/home" BACKUP_DIR="$TMP/bak" "$SUT" "$mode" 2>&1)"; rc=$?
  if [ "$rc" -ne "$want" ]; then
    bad "$label —— exit $rc, wanted $want"; printf '%s\n' "$out" | sed 's/^/        /'; return
  fi
  if [ "$yes" != "-" ] && ! printf '%s\n' "$out" | grep -q "$yes"; then
    bad "$label —— output missing '$yes'"; printf '%s\n' "$out" | sed 's/^/        /'; return
  fi
  if [ "$no" != "-" ] && printf '%s\n' "$out" | grep -q "$no"; then
    bad "$label —— output unexpectedly contains '$no'"; printf '%s\n' "$out" | sed 's/^/        /'; return
  fi
  ok "$label"
}

# Rebuild a clean, fully in-sync fixture pair from mirror.sh's own MAP block, so the
# fixture tracks the real mapping automatically as files are added to it.
build_fixture() {
  rm -rf "$TMP/home" "$TMP/bak"
  mkdir -p "$TMP/home" "$TMP/bak"
  while IFS='|' read -r src bak; do
    [ -z "$src" ] && continue
    mkdir -p "$TMP/home/$(dirname "$src")"
    printf 'content of %s\n' "$src" > "$TMP/home/$src"
    cp "$TMP/home/$src" "$TMP/bak/$bak"
  done <<EOF
$(awk "/^MAP=\\\$\(cat <<'EOF'\$/{f=1;next} f&&/^EOF\$/{exit} f" "$SUT")
EOF
  # An excluded live file must never be flagged; create it so that is actually tested.
  mkdir -p "$TMP/home/scheduled-tasks/ma-heartbeat-cc-reminder"
  printf 'deprecated\n' > "$TMP/home/scheduled-tasks/ma-heartbeat-cc-reminder/SKILL.md"
}

echo "mirror_test.sh —— fixtures in $TMP"
echo

# --- 0. The fixture builder itself must have found the mapping ---------------
build_fixture
n="$(ls "$TMP/bak" | wc -l | tr -d ' ')"
if [ "$n" -ge 13 ]; then ok "0. MAP parsed from mirror.sh ($n entries)"
else bad "0. MAP parse produced only $n entries —— heredoc markers changed?"; fi

# --- 1. Clean snapshot reports clean, and the EXCLUDE entry stays quiet ------
expect "1. in-sync snapshot -> exit 0, no UNMIRRORED for the excluded file" \
       0 "RESULT: snapshot in sync" "UNMIRRORED" check

# --- 2. THE PINNED DEFECT: live file edited, backup left behind -------------
build_fixture
printf 'a hook was added by hand\n' >> "$TMP/home/settings.json"
expect "2. edited live settings.json -> DRIFT, exit 1" \
       1 "DRIFT      backup_settings.json.md" - check

# --- 3. THE REPAIR: sync re-mirrors and the pair becomes byte-identical ------
CLAUDE_HOME="$TMP/home" BACKUP_DIR="$TMP/bak" "$SUT" sync >/dev/null 2>&1
if cmp -s "$TMP/home/settings.json" "$TMP/bak/backup_settings.json.md"; then
  ok "3. sync re-mirrored the stale copy byte-for-byte"
else
  bad "3. sync did NOT make the pair identical"
fi
expect "3b. re-check after sync -> clean, exit 0" 0 "RESULT: snapshot in sync" "DRIFT" check

# --- 4. A brand-new live memory file nothing mirrors -------------------------
build_fixture
printf 'new lesson\n' \
  > "$TMP/home/projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-dupbus-ceztuc-7cufVe/memory/feedback_brand_new.md"
expect "4. unmirrored new live file -> UNMIRRORED, exit 2" 2 "UNMIRRORED" - check
expect "4b. sync does NOT silently invent a name for it" 2 "UNMIRRORED" - sync

# --- 5. A backup file whose source is unknown --------------------------------
build_fixture
printf 'mystery\n' > "$TMP/bak/backup_something_unexplained.md"
expect "5. unmapped backup file -> ORPHAN, exit 2" 2 "ORPHAN" - check

# --- 6. A mapped source deleted upstream -------------------------------------
build_fixture
rm "$TMP/home/settings.json"
expect "6. vanished mapped source -> MISSING, exit 2" 2 "MISSING    settings.json" - check

# --- 7. A backup that was never made at all ----------------------------------
build_fixture
rm "$TMP/bak/backup_settings.json.md"
expect "7. never-mirrored file -> ABSENT, exit 1" 1 "ABSENT     backup_settings.json.md" - check
CLAUDE_HOME="$TMP/home" BACKUP_DIR="$TMP/bak" "$SUT" sync >/dev/null 2>&1
if cmp -s "$TMP/home/settings.json" "$TMP/bak/backup_settings.json.md"; then
  ok "7b. sync created the missing first copy"
else
  bad "7b. sync failed to create the missing copy"
fi

# --- 8. restore-plan prints commands and writes nothing ----------------------
build_fixture
before="$(ls -R "$TMP/home" "$TMP/bak")"
out="$(CLAUDE_HOME="$TMP/home" BACKUP_DIR="$TMP/bak" "$SUT" restore-plan 2>&1)"; rc=$?
after="$(ls -R "$TMP/home" "$TMP/bak")"
if [ "$rc" -eq 0 ] \
   && printf '%s\n' "$out" | grep -q 'cp "'"$TMP"'/bak/backup_settings.json.md"' \
   && [ "$before" = "$after" ]; then
  ok "8. restore-plan emits backup->live cp commands and mutates nothing"
else
  bad "8. restore-plan misbehaved (exit $rc, or it wrote to disk)"
fi

# --- 9. An unknown mode is rejected rather than silently treated as check -----
expect "9. unknown mode -> usage, exit 2" 2 "usage:" - bogus-mode

echo
echo "passed $pass, failed $fail"
[ "$fail" -eq 0 ] || exit 1
