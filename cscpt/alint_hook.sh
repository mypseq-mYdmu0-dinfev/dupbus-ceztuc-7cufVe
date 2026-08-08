#!/bin/bash
# alint.py Fast-Path Wrapper —— the TEA1 in-flight gate (PreToolUse hook)
#
# === NON-CCSIM —— start of all you need to RUN it ===
# WHAT: the registered PreToolUse hook fronting `alint.py` —— the harness
# invokes THIS file, not the .py. It exits 0 instantly unless the Bash command
# mentions `git` (or the liveness probe token); otherwise the gate runs and its
# exit code passes through unchanged (2 = BLOCKED because a sub-agent is still
# in flight, reason on stderr; 0 = allowed).
# === NON-CCSIM —— end of all you need to RUN it ===
#
# CCSIM (only if you EDIT it) —— registered PreToolUse (matcher `Bash`) in the
# USER-level ~/.claude/settings.json; the Claude Desktop app executes user-level
# hooks and silently ignores project-level ones. Bash is the most frequent tool
# call there is and matchers are tool-name only, so the common non-git command
# must not pay a Python start. The substring test is deliberately loose: it only
# decides whether Python is worth spawning —— the rigorous command parsing,
# repo-scope and in-flight checks live in alint.py and must stay there.
# `GitHub` in a payload path does NOT match, because `case` is case-sensitive
# and the test is lowercase `git`; a false match would only cost a needless
# Python spawn, never a wrong verdict. `ALINT_PROBE` is passed through so the
# liveness probe works without performing a real commit. Naming: `_hook` marks
# the file settings.json invokes; every `.sh` here carries it, no `.py` does.

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
    "alint_hook.sh is a hook shim: it reads its JSON payload on stdin." \
    "Nothing was checked —— do not read this silence as a pass." \
    "Run it by hand from the repo root with:" \
    "  printf '%s' '{\"hook_event_name\":\"PostToolUse\",\"tool_name\":\"Write\"," \
    "\"tool_input\":{\"file_path\":\"/abs/file.md\"}}' | bash cscpt/alint_hook.sh" >&2
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
    "alint_hook.sh: stdin delivered NO payload (/dev/null, a closed descriptor, or a" \
    "pipe already at EOF). Nothing was checked —— do not read this silence" \
    "as a pass. Pipe a real payload in, or let the harness call this." >&2
  exit 3
fi

case "$payload" in
  *git*|*ALINT_PROBE*) ;;   # might be a commit/push -> decide in Python
  *) exit 0 ;;              # definitely not -> do nothing, no Python spawned
esac

printf '%s' "$payload" | python3 "$(dirname "$0")/alint.py"
exit $?
