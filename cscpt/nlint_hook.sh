#!/bin/bash
# nlint.py Fast-Path Wrapper (PostToolUse hook)
#
# === NON-CCSIM —— start of all you need to RUN it ===
# WHAT: the registered PostToolUse hook fronting `nlint.py` —— the harness
# invokes THIS file, not the .py. It exits 0 instantly unless the payload could
# interest one of nlint's three checks; otherwise nlint runs and ITS exit code
# passes through: 0 for the two advisories, 2 when the label check BLOCKS.
# === NON-CCSIM —— end of all you need to RUN it ===
#
# CCSIM (only if you EDIT it) —— registered PostToolUse (Edit|Write|MultiEdit)
# in the USER-level ~/.claude/settings.json (the Claude Desktop app executes
# user-level hooks and silently ignores project-level ones). It fires on EVERY
# Edit/Write/MultiEdit (matchers are tool-name only, no path filter), so the
# common edit must not pay a Python start; the rigorous basename check,
# repo-scope guard and all three analyses live in nlint.py. Token cost is ZERO
# in the common case; when nlint ADVISES it exits 0 with structured JSON
# (`hookSpecificOutput.additionalContext`) —— the one PostToolUse channel
# reaching the model without blocking, as plain exit-0 stdout/stderr text
# reaches it not at all —— and when it BLOCKS it exits 2 with stderr text. Both
# pass straight through this shim (`exit $?`); which tier applies is decided
# entirely in the .py. `_hook` marks the file settings.json invokes —— every
# `.sh` here has it, no `.py` does; don't "tidy" it away.
#
# WHY SEVERAL GATE PATTERNS. nlint's three checks have different scopes, so one
# gate cannot serve them all:
#   * Numbering RESET is `response_`-only, so the FILENAME in the payload is a
#     complete and near-free gate (this was the original sole pattern).
#   * TENTH SIBLING (`- [n].10.`) applies to ANY file, so a filename gate would
#     have suppressed it everywhere except responses —— the exact failure this
#     second pattern exists to prevent. It gates on the WRITTEN TEXT instead:
#     every Edit/Write/MultiEdit payload carries the new text inline
#     (`content`/`new_string`), so "a bullet followed by a digit" plus a `.10`
#     somewhere in the same payload is a cheap SUPERSET of every shape nlint.py
#     can flag (`- 3.10.`, `- 12.10.`, `- 1.2.10.`). Deliberately loose:
#     over-firing costs one silent Python start (the .py then decides
#     rigorously), whilst under-firing loses the warning entirely.
#   * QB LABEL applies to EVERY file with no carve-out at all, so it likewise
#     gates on the written text: an uppercase QB followed by a digit, or by a
#     colon. Both are supersets of what the .py refuses —— the digit class also
#     admits an already-fine `QB` inside a longer token, and the colon pattern
#     also admits a backticked mention the .py deliberately acquits. Same
#     trade-off as above, and the same reason: this check BLOCKS, so a gate
#     that under-fires would silently disarm the only blocking check there is.
# All patterns are pure bash builtins —— no fork, no subshell, so the common
# edit still spawns nothing at all.
#
# TRADE-OFF ACCEPTED (payload text, not the file on disk). The gate can only see
# what this write CONTAINS, whereas nlint.py reads the finished file. Net
# effect: the tenth-sibling advisory fires when `.10` is INTRODUCED (or when the
# file is rewritten wholesale), not on every later unrelated edit of a file that
# already holds it. That is the point of the gate AND a useful anti-nag
# property. Known gap in the harmless direction: an edit that adds ONLY
# `- 3.11.` to a file already holding `- 3.10.` does not re-warn —— the reminder
# was already delivered when `.10` went in. The QB check inherits exactly the
# same property: it fires on the write that INTRODUCES the bad label (which is
# the write whose author can still fix it cheaply), not on every later edit of
# a file that already carries one. An edit REMOVING the label still passes the
# gate, since `old_string` carries the text too —— but the .py then reads the
# corrected file and stays silent, so the fix is never punished.

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
    "nlint_hook.sh is a hook shim: it reads its JSON payload on stdin." \
    "Nothing was checked —— do not read this silence as a pass." \
    "Run it by hand from the repo root with:" \
    "  printf '%s' '{\"hook_event_name\":\"PostToolUse\",\"tool_name\":\"Write\"," \
    "\"tool_input\":{\"file_path\":\"/abs/file.md\"}}' | bash cscpt/nlint_hook.sh" >&2
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
    "nlint_hook.sh: stdin delivered NO payload (/dev/null, a closed descriptor, or a" \
    "pipe already at EOF). Nothing was checked —— do not read this silence" \
    "as a pass. Pipe a real payload in, or let the harness call this." >&2
  exit 3
fi

case "$payload" in
  *response_*) ;;         # might involve a response_ file -> verify in Python
  *"- "[0-9]*".10"*) ;;   # might carry a level's 10th sibling -> ditto
  *QB[0-9]*) ;;           # might carry a merged question/blocker label -> ditto
  *"QB:"*) ;;             # ditto, the unnumbered form CC must never emit
  *) exit 0 ;;            # none of them -> do nothing, no Python spawned
esac

printf '%s' "$payload" | python3 "$(dirname "$0")/nlint.py"
exit $?
