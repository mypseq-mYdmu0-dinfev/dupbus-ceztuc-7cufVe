#!/bin/bash
# PostToolUse fast-path wrapper for nlint_hook.py.
#
# Rationale: the hook fires on EVERY Edit/Write/MultiEdit (Claude Code matchers
# are tool-name only, no path filter). nlint only ever acts on a `response_`
# file, so this bash shim reads the payload and exits 0 IMMEDIATELY unless the
# payload even mentions `response_` —— sparing a Python spawn on the common edit.
# The Python hook then does the rigorous basename check (CP-prefix + response_ +
# 12 digits + .md), scans for a numbering RESET, and blocks (exit 2) only on a
# confirmed continuity breach. Run, not read.
#
# Narrower than dlint_hook.sh on purpose: dlint also lints close_/wrap_, but a
# numbering-continuity reset is meaningful for a response_ alone.
#
# Token cost is ZERO unless it blocks (exit-0 output never enters context); this
# shim only trims wall-time (a Python start per edit).

payload=$(cat)

case "$payload" in
  *response_*) ;;   # might involve a response_ file -> verify in Python
  *) exit 0 ;;       # definitely not -> do nothing, no Python spawned
esac

printf '%s' "$payload" | python3 "$(dirname "$0")/nlint_hook.py"
exit $?
