#!/bin/sh
# PreToolUse + PostToolUse fast-path wrapper for flint.py (the filename linter).
#
# === NON-CCSIM —— start of all you need to RUN it ===
# WHAT: the registered hook fronting `flint.py` —— the harness invokes THIS
# file, not the .py, on BOTH events. It exits 0 instantly unless the payload
# carries a 12-digit timestamp starting "20"; otherwise flint runs and its exit
# code passes straight through. Exit 2 means a write was BLOCKED for a
# stray-space filename; the message on stderr names the correct name. The
# PostToolUse half never exits 2 —— it only warns.
# === NON-CCSIM —— end of all you need to RUN it ===
#
# CCSIM (only if you EDIT it) —— TWO registrations in the USER-level
# ~/.claude/settings.json (the Claude Desktop app executes user-level hooks and
# silently ignores project-level ones):
#   PreToolUse  (Edit|Write|MultiEdit|NotebookEdit|Read) ... flint_hook.sh pre
#   PostToolUse (Edit|Write|MultiEdit)                   ... flint_hook.sh post
# ONE shim serves both because both events need the identical decision —— "is
# there a TS in this payload at all?" —— so a second file would be a byte-for-
# byte copy differing only in an argument. PreToolUse on Read+Write is the
# highest-frequency event set in this repo and PostToolUse fires on every
# Edit/Write, so the shim is what keeps a Python spawn off every code/pcmd read
# and every code write (hook_guide.md §3.2); a TS-less payload cannot possibly
# hold either defect, since both are defined relative to a TS.
#
# THE ARGUMENT IS LOAD-BEARING: flint.py is registered on TWO events and selects
# its mode from argv, falling back to the payload's `hook_event_name` only when
# argv is missing. Do not drop it. `${1:-}` (not `$1`) so the file is safe to
# source or run under `set -u`, and so an argument-less invocation reaches
# Python as an empty string rather than a syntax surprise.
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
# beside it, this one's whole purpose is to propagate a 2 on the PreToolUse
# half. POSIX `/bin/sh` suffices. `_hook` marks the file settings.json invokes
# —— every `.sh` here has it, no `.py` does.
payload="$(cat)"
printf '%s' "$payload" | grep -qE '20[0-9]{10}' || exit 0
printf '%s' "$payload" | python3 "$(dirname "$0")/flint.py" "${1:-}"
