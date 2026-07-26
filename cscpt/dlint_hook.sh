#!/bin/bash
# PostToolUse fast-path wrapper for dlint_quick.py.
#
# === NON-CCSIM —— start of all you need to RUN it ===
# WHAT: the registered PostToolUse hook fronting `dlint_quick.py` —— the harness
# invokes THIS file, not the .py. It exits 0 instantly unless the write mentions
# `response_`, `close_` or `wrap_`; otherwise the lint runs and its exit code
# passes through unchanged (2 = 🔴 RED found, flags fed back on stderr for you
# to fix and rewrite; 0 = nothing to do).
# === NON-CCSIM —— end of all you need to RUN it ===
#
# CCSIM (only if you EDIT it) —— registered PostToolUse (Edit|Write|MultiEdit)
# in the USER-level ~/.claude/settings.json (the Claude Desktop app executes
# user-level hooks and silently ignores project-level ones). It fires on EVERY
# Edit/Write/MultiEdit (matchers are tool-name only, no path filter), so the
# common non-comms edit must not pay a Python start. The substring test is
# deliberately loose: it only decides whether Python is worth spawning —— the
# rigorous file_path and repo-scope checks live in dlint_quick.py and must stay
# there. Token cost is ZERO unless it blocks (exit-0 output never enters
# context); this shim trims wall-time only. Naming: `_hook` marks the file
# settings.json invokes; the `.py` is a single-purpose lint runner (`dlint.py
# --quick` + block on RED), hence `_quick`. Every `.sh` here carries `_hook`, no
# `.py` does —— don't "tidy" it.

payload=$(cat)

case "$payload" in
  *response_*|*close_*|*wrap_*) ;;   # might involve a CC comms file -> verify in Python
  *) exit 0 ;;                        # definitely not -> do nothing, no Python spawned
esac

printf '%s' "$payload" | python3 "$(dirname "$0")/dlint_quick.py"
exit $?
