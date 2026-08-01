#!/bin/bash
# PreToolUse fast-path wrapper for alint.py —— the TEA1 in-flight gate.
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

payload=$(cat)

case "$payload" in
  *git*|*ALINT_PROBE*) ;;   # might be a commit/push -> decide in Python
  *) exit 0 ;;              # definitely not -> do nothing, no Python spawned
esac

printf '%s' "$payload" | python3 "$(dirname "$0")/alint.py"
exit $?
