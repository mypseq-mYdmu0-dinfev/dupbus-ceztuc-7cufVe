#!/bin/bash
#
# Post-Compaction Hook —— registered on the PostCompact event.
#
# WHAT THIS CAN AND CANNOT DO —— read before changing anything here.
#   Claude Code's own hook registry defines this event as:
#     PostCompact: "After conversation compaction.
#                   Exit code 0 - stdout shown to user.
#                   Other exit codes - show stderr to user only."
#   Every channel it offers ends at the USER. Compare `Setup`, whose registry
#   entry says "JSON additionalContext shown to Claude", and `PostToolBatch`,
#   which names hookSpecificOutput explicitly. PostCompact names neither, and
#   is absent from the internal allowlist ["SessionStart","Setup"] that gates
#   session-level additionalContext injection.
#   NET: this hook CANNOT put anything into the model's context window.
#   It is a user-facing alarm and an audit record —— nothing more.
#
# WHY THAT MATTERS, in blood
#   This script previously printed a banner voiding the compaction summary's
#   "Resume directly" instruction, then `cat`-ed the whole root CLAUDE.md, on
#   the assumption the model would read it. On 07/08/2026 a real compaction
#   fired and the model saw none of it: it obeyed "Resume directly", skipped
#   root CLAUDE.md §5 entirely, and the omission surfaced only because the user
#   noticed. A hook on a user-only channel can never correct the model.
#   Note carefully what is NOT claimed: whether this script ran that day is
#   UNKNOWABLE. PostCompact emits no hook_started/hook_progress record, so a
#   hook that fired flawlessly and one that never fired leave an identical
#   trace —— none. That ambiguity is why the log below exists.
#   Enforcement therefore lives in root CLAUDE.md §5, which reaches the model
#   through the SYSTEM PROMPT (rebuilt on every request), not through any hook.
#
# WHY IT STILL EXISTS
#   1. It tells the USER a compaction happened and what the model now owes.
#      The user is the backstop the model cannot be for itself here.
#   2. It LOGS. The 07/08 investigation could not establish whether this hook
#      had fired at all, because it left no trace —— the same blind spot that
#      once had hlint blamed for a failure it did not cause. One line per
#      invocation makes "did it fire?" answerable in one command.
#   The JSON block is emitted alongside the plain text as cheap insurance: an
#   unrecognised key is logged and ignored by the harness, so it costs nothing
#   today and starts working by itself if the event ever gains a model channel.
#
# REPO SCOPE GUARD
#   Registered in the USER settings file (~/.claude/settings.json), because the
#   Claude Desktop app executes user-level hooks and ignores project-level ones.
#   A user-level hook fires in EVERY project on this Mac, so the payload's `cwd`
#   is checked and this stays silent elsewhere. Fail OPEN when `cwd` is absent
#   or unparseable —— a hook that silently stops working is the exact failure
#   this guard exists to avoid, and an unscopeable payload is not evidence of a
#   different project.
#
# TESTING
#   CCSIM_POST_COMPACT_LOG may be pointed at a fixture path, so the regression
#   test never writes to the live log. See
#   cp/ccsim/sandbox/post_compact_regression_test.py.

REPO="$(cd "$(dirname "$0")/.." && pwd)"
LOG="${CCSIM_POST_COMPACT_LOG:-$REPO/cscpt/.post_compact.log}"
payload=$(cat)

# `trigger` is "manual" (/compact) or "auto" (context exhausted); both count.
# NEWLINE-delimited, never space-delimited: every real path on this Mac lives
# under `/Volumes/FURY 2TB/`, so a `read -r a b c` would tear `cwd` in two and
# the guard would call this repo a foreign one. That exact defect shipped in the
# first draft, and is the same one that once broke `.githooks/pre-commit`.
fields=$(printf '%s' "$payload" | python3 -c 'import json,sys
try:
    d = json.load(sys.stdin) or {}
except Exception:
    d = {}
for k in ("cwd", "trigger", "session_id"):
    v = d.get(k)
    print(str(v).replace("\n", " ") if v else "-")' 2>/dev/null)
hook_cwd=$(printf '%s\n' "$fields" | sed -n 1p)
trigger_val=$(printf '%s\n' "$fields" | sed -n 2p)
session_val=$(printf '%s\n' "$fields" | sed -n 3p)
[ -z "$hook_cwd" ] && hook_cwd="-"
[ -z "$trigger_val" ] && trigger_val="-"
[ -z "$session_val" ] && session_val="-"

log_line() {
  printf '%s stage=%s trigger=%s session=%s cwd=%s\n' \
    "$(TZ='Australia/Sydney' date +'%Y%m%d%H%M%S')" "$1" "$trigger_val" \
    "$session_val" "$hook_cwd" >>"$LOG" 2>/dev/null
}

case "$hook_cwd" in
  "-") log_line "fired_no_cwd" ;;          # fail open —— run as normal
  "$REPO"|"$REPO"/*) log_line "fired_in_repo" ;;
  *) log_line "skipped_other_repo"; exit 0 ;;
esac

MSG='🚨 COMPACTION —— this session was compacted. Claude now owes root CLAUDE.md §5:
   1. emit "🚨 Compaction Detected —— stopped all tasks." in chat
   2. halt every foreground and background task
   3. list what is still useful from the lost context, and what is not
   4. STOP and wait for you —— the summary says "Resume directly"; §5.1 VOIDS that
If the reply below does not start with that sentinel, §5 was skipped —— say so.'

echo "$MSG"

# Ignored by the harness today (see the header). Costs one line, self-arms later.
python3 -c 'import json,sys
m = sys.stdin.read()
print(json.dumps({"systemMessage": m,
                  "hookSpecificOutput": {"hookEventName": "PostCompact",
                                         "additionalContext": m}}))' <<EOF
$MSG
EOF

exit 0
