#!/bin/bash
# PostToolUse fast-path wrapper for dlint_quick.py.
#
# NON-CCSIM (to RUN) —— THIS file is the registered hook: PostToolUse
# (Edit|Write|MultiEdit) in the USER-level ~/.claude/settings.json; the harness
# invokes it, not the .py. It reads the tool payload on stdin and exits 0
# IMMEDIATELY unless that payload mentions `response_`, `close_` or `wrap_`;
# otherwise it pipes the payload to dlint_quick.py and returns that exit code
# unchanged (2 = RED flags found and fed back to CC, 0 = nothing to do).
# Run, not read —— see README.
#
# CCSIM (only if you EDIT it) —— the hook fires on EVERY Edit/Write/MultiEdit
# (matchers are tool-name only, no path filter), so the common non-comms edit
# must not pay a Python start. The substring test is deliberately loose: it only
# decides whether Python is worth spawning —— the rigorous file_path and
# repo-scope checks live in dlint_quick.py and must stay there. Token cost is
# ZERO unless it blocks (exit-0 output never enters context); this shim trims
# wall-time only. Naming: `_hook` marks the file settings.json invokes; the `.py`
# is a single-purpose lint runner (`dlint.py --quick` + block on RED), hence
# `_quick`. Every `.sh` here carries `_hook`, no `.py` does —— don't "tidy" it.

payload=$(cat)

case "$payload" in
  *response_*|*close_*|*wrap_*) ;;   # might involve a CC comms file -> verify in Python
  *) exit 0 ;;                        # definitely not -> do nothing, no Python spawned
esac

printf '%s' "$payload" | python3 "$(dirname "$0")/dlint_quick.py"
exit $?
