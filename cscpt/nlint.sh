#!/bin/bash
# PostToolUse fast-path wrapper for nlint.py.
#
# Rationale: the hook fires on EVERY Edit/Write/MultiEdit (Claude Code matchers
# are tool-name only, no path filter). nlint only ever acts on a `response_`
# file, so this bash shim reads the payload and exits 0 IMMEDIATELY unless the
# payload even mentions `response_` —— sparing a Python spawn on the common edit.
# The Python hook then does the rigorous basename check (CP-prefix + response_ +
# 12 digits + .md), scans for a numbering RESET, and —— only when no
# numbered.md condition excuses it —— ADVISES (never hard-blocks; PostToolUse
# cannot block anyway, the write already happened). Run, not read.
#
# Narrower than dlint_hook.sh on purpose: dlint also lints close_/wrap_, but a
# numbering-continuity reset is meaningful for a response_ alone.
#
# Token cost is ZERO unless nlint.py actually flags: a plain exit-0 with
# no stdout (the overwhelming common case —— no reset, or a reset numbered.md
# already excuses) never enters context. When it DOES flag, it exits 0 with
# structured JSON (`hookSpecificOutput.additionalContext`) —— the one
# PostToolUse channel that reaches the model WITHOUT blocking (plain exit-0
# stdout/stderr text does NOT reach the model; only exit-2 stderr or
# structured exit-0 JSON do — see nlint.py's own docstring). This shim's
# OWN job is unchanged: trim wall-time (spare a Python start per edit), not
# decide blocking vs advisory —— that decision lives entirely in the .py.

payload=$(cat)

case "$payload" in
  *response_*) ;;   # might involve a response_ file -> verify in Python
  *) exit 0 ;;       # definitely not -> do nothing, no Python spawned
esac

printf '%s' "$payload" | python3 "$(dirname "$0")/nlint.py"
exit $?
