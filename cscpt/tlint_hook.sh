#!/bin/sh
# PreToolUse + PostToolUse fast-path wrapper for tlint.py (the time-integrity
# linter).
#
# === NON-CCSIM —— start of all you need to RUN it ===
# WHAT: the registered hook fronting `tlint.py` —— the harness invokes THIS
# file, not the .py, on BOTH events. It exits 0 instantly unless the payload
# could carry a time defect; otherwise tlint runs. Every path exits 0: this
# lint only ever advises, and its notes reach the model as context, never as
# an error. Stage log: `cscpt/.tlint.log`.
# === NON-CCSIM —— end of all you need to RUN it ===
#
# CCSIM (only if you EDIT it) —— TWO registrations in the USER-level
# ~/.claude/settings.json (the Claude Desktop app executes user-level hooks and
# silently ignores project-level ones):
#   PreToolUse  (Bash)                 ... tlint_hook.sh pre
#   PostToolUse (Edit|Write|MultiEdit) ... tlint_hook.sh post
# ONE shim serves both, as `flint_hook.sh` does, because a second file would
# differ only in its gate. The gates DIFFER by event, which is why this one
# branches on the argument where flint's does not: the two events look for
# entirely different evidence.
#
# THE ARGUMENT IS LOAD-BEARING: tlint.py selects its mode from argv, falling
# back to the payload's `hook_event_name` only when argv is missing. Do not
# drop it. `${1:-}` (not `$1`) so the file is safe under `set -u`.
#
# WHY THE SHIM EXISTS AT ALL: PreToolUse-Bash and PostToolUse-write are two of
# the highest-frequency events in this repo, and a Python spawn costs ~26 ms
# against a shell exit of ~5 ms (`hook_guide.md` §3.2/§12.7). Measured on 4630
# real Bash calls from this repo's transcripts, the `pre` gate lets ~9% through.
#
# WHY EACH GATE IS BROADER THAN THE DEFECT IT GUARDS:
#  * `pre` matches the word `date` anywhere in the payload, not a
#    command-position `date` lacking a TZ. Reproducing that decision in grep
#    would mean reproducing shell-separator and env-assignment parsing through
#    JSON escaping, and any mismatch would silently DROP a real hit —— the one
#    failure a gate must never have. The precise call is made in Python.
#    Only `[A-Za-z0-9_-]` bounds the word: `/` and `.` are NOT excluded, so
#    `/usr/bin/date` still matches. That is not fussiness —— the first draft
#    excluded `/` and dropped exactly that spelling, which the suite caught.
#    Measured over 4641 real Bash calls from this repo's transcripts, this
#    gate lets ~16% through against ~20% for a plain substring search.
#  * `post` matches a 12-digit timestamp, OR a numeric `D/M/YYYY`, OR a
#    month-name-then-year shape. All three are plain ASCII, so JSON escaping
#    cannot distort them. A payload with none of the three cannot hold any
#    defect this lint knows about.
#  * NO ARGUMENT means a settings edit has not gone live yet (`hook_guide.md`
#    §7.9), so the event is unknown and EITHER gate must be able to admit the
#    payload —— narrowing to one of them would silently disable half the lint
#    for those minutes.
#
# The exit code is deliberately swallowed to 0: nothing in tlint blocks, and a
# stray non-zero on PreToolUse would BLOCK the tool call (`hook_guide.md` §6).
# POSIX `/bin/sh` suffices. `_hook` marks the file settings.json invokes ——
# every `.sh` here has it, no `.py` does.
payload="$(cat)"
arg="${1:-}"

CLOCK='(^|[^A-Za-z0-9_-])date([^A-Za-z0-9_-]|$)'
# STAMP exceeds the 130-char guide unavoidably: it is ONE alternation passed to
# a single `grep -qE`, and splitting a regex across shell string joins is how a
# gate acquires a silent hole. Read it as three arms: 12-digit TS | numeric
# D/M/YYYY | month-name then day then year.
STAMP='20[0-9]{10}|[0-9]{1,2}/[0-9]{1,2}/(19|20)[0-9]{2}|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?[[:space:]]+[0-9]{1,2}(st|nd|rd|th)?,[[:space:]]*(19|20)[0-9]{2}'

case "$arg" in
  pre)  gate="$CLOCK" ;;
  post) gate="$STAMP" ;;
  *)    gate="$CLOCK|$STAMP" ;;
esac

printf '%s' "$payload" | grep -qE "$gate" || exit 0
printf '%s' "$payload" | python3 "$(dirname "$0")/tlint.py" "$arg"
exit 0
