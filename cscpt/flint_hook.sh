#!/bin/sh
# PreToolUse fast-path wrapper for flint.py (the filename linter).
#
# === NON-CCSIM —— start of all you need to RUN it ===
# WHAT: the registered PreToolUse hook fronting `flint.py` —— the harness
# invokes THIS file, not the .py. It exits 0 instantly unless the payload
# carries a 12-digit timestamp starting "20"; otherwise flint runs and its exit
# code passes straight through. Exit 2 means the write was BLOCKED for a
# stray-space filename; the message on stderr names the correct name.
# === NON-CCSIM —— end of all you need to RUN it ===
#
# CCSIM (only if you EDIT it) —— registered PreToolUse
# (Edit|Write|MultiEdit|NotebookEdit|Read) in the USER-level
# ~/.claude/settings.json (the Claude Desktop app executes user-level hooks and
# silently ignores project-level ones). PreToolUse on Read+Write is the
# highest-frequency event set in this repo, so the shim is what keeps a Python
# spawn off every code/pcmd read (hook_guide.md §3.2); a TS-less payload cannot
# possibly hold the defect, since the defect is defined relative to a TS.
#
# WHY THE GATE IS "HAS A TS" AND NOT "LOOKS LIKE THE DEFECT": a defect-shaped
# grep would have to reproduce the whitespace class through JSON encoding —— a
# tab arrives as the two characters \t, and a non-breaking space depends on the
# locale's idea of [[:blank:]]. Any of those mismatches would silently drop a
# real hit, which is the one failure mode a gate must never have. Matching on
# the TS alone leaves ZERO detection gap: every decision that can be got wrong
# is made in Python, where the whitespace class is exact.
#
# The exit code is deliberately NOT swallowed —— unlike the warn-only shims
# beside it, this one's whole purpose is to propagate a 2. POSIX `/bin/sh`
# suffices. `_hook` marks the file settings.json invokes —— every `.sh` here has
# it, no `.py` does.
payload="$(cat)"
printf '%s' "$payload" | grep -qE '20[0-9]{10}' || exit 0
printf '%s' "$payload" | python3 "$(dirname "$0")/flint.py"
