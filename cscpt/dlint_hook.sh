#!/bin/bash
# dlint_quick.py Fast-Path Wrapper (PostToolUse hook)
#
# === NON-CCSIM —— start of all you need to RUN it ===
# WHAT: the registered PostToolUse hook fronting `dlint_quick.py` —— the harness
# invokes THIS file, not the .py. It exits 0 instantly unless the write mentions
# a `.md` or `.txt` path; otherwise the lint runs and its exit code passes
# through unchanged (2 = 🔴 RED found, or a deliverable still owes a FULL dlint,
# reason fed back on stderr for you to fix and rewrite; 0 = nothing to do).
# === NON-CCSIM —— end of all you need to RUN it ===
#
# CCSIM (only if you EDIT it) —— registered PostToolUse (Edit|Write|MultiEdit)
# in the USER-level ~/.claude/settings.json (the Claude Desktop app executes
# user-level hooks and silently ignores project-level ones). It fires on EVERY
# Edit/Write/MultiEdit (matchers are tool-name only, no path filter), so the
# common code/config edit must not pay a Python start.
#
# WHY THE GATE IS THIS LOOSE. `dlint_quick.py` now covers EVERY `.md`/`.txt`
# write in this repo, not the three comms filename roles it once matched, and
# it also carries the deliverable-escape gate that `elint_hook.sh` used to
# front. A single extension test is a cheap SUPERSET of both jobs whilst still
# skipping every `.py`, `.sh`, `.json` and notebook write. It matches the
# extension anywhere in the payload rather than only in `file_path`, because
# the JSON is scanned as one flat string here —— deliberately, since
# over-firing costs one silent Python start that then decides rigorously,
# whereas under-firing loses the enforcement entirely. Every rigorous check
# (repo scope, target extension, carve-outs, classification, receipts) lives in
# the .py and must stay there.
#
# Naming: `_hook` marks the file settings.json invokes; the `.py` is the lint
# body. Every `.sh` here carries `_hook`, no `.py` does —— don't "tidy" it.

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
    "dlint_hook.sh is a hook shim: it reads its JSON payload on stdin." \
    "Nothing was checked —— do not read this silence as a pass." \
    "Run it by hand from the repo root with:" \
    "  printf '%s' '{\"hook_event_name\":\"PostToolUse\",\"tool_name\":\"Write\"," \
    "\"tool_input\":{\"file_path\":\"/abs/file.md\"}}' | bash cscpt/dlint_hook.sh" >&2
  exit 3
fi
payload=$(cat)
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
    "dlint_hook.sh: stdin delivered NO payload (/dev/null, a closed descriptor, or a" \
    "pipe already at EOF). Nothing was checked —— do not read this silence" \
    "as a pass. Pipe a real payload in, or let the harness call this." >&2
  exit 3
fi

case "$payload" in
  *.md*|*.txt*) ;;   # might involve a prose file -> verify in Python
  *) exit 0 ;;       # definitely not -> do nothing, no Python spawned
esac

printf '%s' "$payload" | python3 "$(dirname "$0")/dlint_quick.py"
exit $?
