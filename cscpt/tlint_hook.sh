#!/bin/sh
# tlint.py Fast-Path Wrapper —— the time-integrity linter (PreToolUse + PostToolUse hook)
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
# HOOK-BODY STDIN GUARD —— the `cat` below reads the harness payload, and on a
# terminal it waits for one that is never coming, so a hand run hangs instead of
# reporting anything. Silence from a hang is indistinguishable from silence from
# a clean pass, so that hang does not merely waste time: it manufactures a
# verification nobody performed. Refuse loudly and non-zero instead; a quiet
# exit 0 would be the same false pass in a different hat. Under the harness
# stdin is a pipe, never a tty, so this costs nothing on the real path.
#
# KNOWN RESIDUAL, left deliberately: a caller that holds an EMPTY pipe open
# is not a tty, so `cat` still waits on it here. Bounding that wait means
# replacing `cat` with `read -t`, which is a bashism in a file documented as
# POSIX sh AND does not reproduce `$(cat)` byte for byte —— too much risk to
# a gate that BLOCKS writes, for a path only a hand-invoker reaches. The .py
# this shim fronts bounds its own wait, so the linting side is covered; what
# is uncovered is hand-running the SHIM from something other than a terminal.
if [ -t 0 ]; then
  printf '%s\n' \
    "tlint_hook.sh is a hook shim: it reads its JSON payload on stdin." \
    "Nothing was checked —— do not read this silence as a pass." \
    "Run it by hand from the repo root with:" \
    "  printf '%s' '{\"hook_event_name\":\"PostToolUse\",\"tool_name\":\"Write\"," \
    "\"tool_input\":{\"file_path\":\"/abs/file.md\"}}' | sh cscpt/tlint_hook.sh post" >&2
  exit 3
fi
payload="$(cat)"
# READINESS IS NOT ARRIVAL. `/dev/null`, a closed descriptor and a pipe already
# at EOF all satisfy `cat` instantly and hand back nothing, and none of them is
# a tty, so the guard above waves every one of them through. The `case` below
# then matches nothing and the shim exits 0 without a word —— which is the
# false pass this whole guard exists to stop, reached by a shorter route than
# the hang. An agent shell runs its commands with stdin on `/dev/null`, so that
# was the ORDINARY hand invocation, not an exotic one.
#
# An EMPTY PIPE is left alone on purpose —— that is the harness sending
# nothing, and every lint here fails OPEN on it, a contract the suites pin
# (tlint F1, alint J4, and siblings). Only emptiness on a NON-pipe is a hand
# invocation. Where /dev/stdin cannot be inspected at all, nothing is refused:
# an odd environment may only ever fail towards leaving the gate armed.
#
# Exit 3, never 2: only a 2 blocks a tool call, so this can shout without ever
# being able to stop anything —— including on the PreToolUse half, where this
# shim otherwise propagates its lint's status.
if [ -z "$payload" ] && [ -e /dev/stdin ] && [ ! -p /dev/stdin ]; then
  printf '%s\n' \
    "tlint_hook.sh: stdin delivered NO payload (/dev/null, a closed descriptor, or a" \
    "pipe already at EOF). Nothing was checked —— do not read this silence" \
    "as a pass. Pipe a real payload in, or let the harness call this." >&2
  exit 3
fi
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
