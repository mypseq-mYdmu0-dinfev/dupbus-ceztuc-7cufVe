#!/bin/bash
# PostToolUse fast-path wrapper for dlint_hook.py.
#
# Rationale: the hook fires on EVERY Edit/Write/MultiEdit (Claude Code matchers
# are tool-name only, no path filter). To keep the common non-response_ edit
# near-free, this bash shim reads the payload and exits 0 IMMEDIATELY unless the
# payload even mentions `response_` —— so Python is spawned ONLY when a response_
# file is plausibly involved. The Python hook then does the rigorous file_path
# check and runs `dlint.py --quick` (blocking on RED). Run, not read.
#
# Token cost either way is ZERO unless it blocks (exit-0 output never enters
# context); this shim only trims wall-time (a Python start per edit).

payload=$(cat)

case "$payload" in
  *response_*|*close_*|*wrap_*) ;;   # might involve a CC comms file -> verify in Python
  *) exit 0 ;;                        # definitely not -> do nothing, no Python spawned
esac

printf '%s' "$payload" | python3 "$(dirname "$0")/dlint_hook.py"
exit $?
