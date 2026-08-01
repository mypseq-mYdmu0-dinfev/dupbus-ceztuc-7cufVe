#!/bin/bash
# PostToolUse fast-path wrapper for elint.py.
#
# === NON-CCSIM —— start of all you need to RUN it ===
# WHAT: the registered PostToolUse hook fronting `elint.py` —— the harness
# invokes THIS file, not the .py. It exits 0 instantly unless the payload
# mentions a `.md` or `.txt` path; otherwise elint runs and ITS exit code
# passes through: 0 for an advisory, 2 when a deliverable is still un-linted
# and a comms file is being written.
# === NON-CCSIM —— end of all you need to RUN it ===
#
# CCSIM (only if you EDIT it) —— registered PostToolUse (Edit|Write|MultiEdit)
# in the USER-level ~/.claude/settings.json (the Claude Desktop app executes
# user-level hooks and silently ignores project-level ones). It fires on EVERY
# Edit/Write/MultiEdit, since matchers are tool-name only with no path filter,
# so a code or config write must not pay a Python start. The `stop`
# registration has NO shim and calls `elint.py stop` directly —— a Stop hook
# fires once per turn, so a shim would save nothing (same reason clint and
# hlint have none).
#
# WHY THE GATE IS THIS LOOSE. elint has to see two different payload shapes:
# the write of a DELIVERABLE (`.md`/`.txt` outside comms territory) and the
# write of a COMMS file that hands it over (`response_`/`close_`/`wrap_`,
# always `.md`). A single extension test is a cheap SUPERSET of both, whilst
# still skipping every `.py`, `.sh`, `.json` and notebook write. It matches
# the extension anywhere in the payload rather than only in `file_path`,
# because the JSON is scanned as one flat string here —— deliberately, since
# over-firing costs one silent Python start that then decides rigorously,
# whereas under-firing loses the enforcement entirely. All rigorous checks
# (repo scope, classification, receipts) live in the .py and must stay there.
#
# The argument `post` is load-bearing: elint.py is registered on TWO events
# and selects its tier from argv, falling back to `hook_event_name` only if
# argv is missing. Do not drop it.
#
# Naming: `_hook` marks the file settings.json invokes —— every `.sh` here
# carries it and no `.py` does; don't "tidy" it away.

payload=$(cat)

case "$payload" in
  *.md*|*.txt*) ;;   # might involve a prose file -> verify in Python
  *) exit 0 ;;       # definitely not -> do nothing, no Python spawned
esac

printf '%s' "$payload" | python3 "$(dirname "$0")/elint.py" post
exit $?
