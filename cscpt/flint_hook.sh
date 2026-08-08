#!/bin/sh
# flint.py Fast-Path Wrapper —— the filename linter (PreToolUse + PostToolUse hook)
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
# HOOK-BODY STDIN GUARD —— the `cat` below reads the harness payload, and on a
# terminal it waits for one that is never coming, so a hand run hangs instead of
# reporting anything. Silence from a hang is indistinguishable from silence from
# a clean pass, so that hang does not merely waste time: it manufactures a
# verification nobody performed. Refuse loudly and non-zero instead; a quiet
# exit 0 would be the same false pass in a different hat. Under the harness
# stdin is a pipe, never a tty, so this costs nothing on the real path.
#
# KNOWN RESIDUAL, left deliberately: a caller that holds an EMPTY pipe open
# is not a tty, so `cat` still waits on it here. Bounding that wait means
# replacing `cat` with `read -t`, which is a bashism in a file documented as
# POSIX sh AND does not reproduce `$(cat)` byte for byte —— too much risk to
# a gate that BLOCKS writes, for a path only a hand-invoker reaches. The .py
# this shim fronts bounds its own wait, so the linting side is covered; what
# is uncovered is hand-running the SHIM from something other than a terminal.
if [ -t 0 ]; then
  printf '%s\n' \
    "flint_hook.sh is a hook shim: it reads its JSON payload on stdin." \
    "Nothing was checked —— do not read this silence as a pass." \
    "Run it by hand from the repo root with:" \
    "  printf '%s' '{\"hook_event_name\":\"PostToolUse\",\"tool_name\":\"Write\"," \
    "\"tool_input\":{\"file_path\":\"/abs/file.md\"}}' | sh cscpt/flint_hook.sh pre" >&2
  exit 3
fi
payload="$(cat)"
# READINESS IS NOT ARRIVAL. `/dev/null`, a closed descriptor and a pipe already
# at EOF all satisfy `cat` instantly and hand back nothing, and none of them is
# a tty, so the guard above waves every one of them through. The `case` below
# then matches nothing and the shim exits 0 without a word —— which is the
# false pass this whole guard exists to stop, reached by a shorter route than
# the hang. An agent shell runs its commands with stdin on `/dev/null`, so that
# was the ORDINARY hand invocation, not an exotic one.
#
# An EMPTY PIPE is left alone on purpose —— that is the harness sending
# nothing, and every lint here fails OPEN on it, a contract the suites pin
# (tlint F1, alint J4, and siblings). Only emptiness on a NON-pipe is a hand
# invocation. Where /dev/stdin cannot be inspected at all, nothing is refused:
# an odd environment may only ever fail towards leaving the gate armed.
#
# Exit 3, never 2: only a 2 blocks a tool call, so this can shout without ever
# being able to stop anything —— including on the PreToolUse half, where this
# shim otherwise propagates its lint's status.
if [ -z "$payload" ] && [ -e /dev/stdin ] && [ ! -p /dev/stdin ]; then
  printf '%s\n' \
    "flint_hook.sh: stdin delivered NO payload (/dev/null, a closed descriptor, or a" \
    "pipe already at EOF). Nothing was checked —— do not read this silence" \
    "as a pass. Pipe a real payload in, or let the harness call this." >&2
  exit 3
fi
printf '%s' "$payload" | grep -qE '20[0-9]{10}' || exit 0
printf '%s' "$payload" | python3 "$(dirname "$0")/flint.py" "${1:-}"
