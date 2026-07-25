#!/bin/bash
# PostToolUse fast-path wrapper for nlint.py.
#
# NON-CCSIM (to RUN) —— THIS file is the registered hook: PostToolUse
# (Edit|Write|MultiEdit) in the USER-level ~/.claude/settings.json; the harness
# invokes it, not the .py. It reads the tool payload on stdin and exits 0
# IMMEDIATELY unless that payload mentions `response_`; otherwise it pipes the
# payload to nlint.py and returns that exit code —— always 0, since nlint
# advises and never blocks. Run, not read —— see README.
#
# CCSIM (only if you EDIT it) —— the hook fires on EVERY Edit/Write/MultiEdit
# (matchers are tool-name only, no path filter), so the common edit must not pay
# a Python start; the rigorous basename check, repo-scope guard and reset
# analysis all live in nlint.py. NARROWER than dlint_hook.sh on purpose: dlint
# also lints `close_`/`wrap_`, but numbering continuity is meaningful for a
# `response_` alone. Token cost is ZERO in the common case; when nlint DOES
# flag, it exits 0 with structured JSON (`hookSpecificOutput.additionalContext`)
# —— the one PostToolUse channel reaching the model without blocking, as plain
# exit-0 stdout/stderr text reaches it not at all. Blocking-vs-advisory is
# decided entirely in the .py. `_hook` marks the file settings.json invokes ——
# every `.sh` here has it, no `.py` does; don't "tidy" it away.

payload=$(cat)

case "$payload" in
  *response_*) ;;   # might involve a response_ file -> verify in Python
  *) exit 0 ;;       # definitely not -> do nothing, no Python spawned
esac

printf '%s' "$payload" | python3 "$(dirname "$0")/nlint.py"
exit $?
