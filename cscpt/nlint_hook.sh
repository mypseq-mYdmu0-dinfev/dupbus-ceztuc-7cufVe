#!/bin/bash
# PostToolUse fast-path wrapper for nlint.py.
#
# === NON-CCSIM —— start of all you need to RUN it ===
# WHAT: the registered PostToolUse hook fronting `nlint.py` —— the harness
# invokes THIS file, not the .py. It exits 0 instantly unless the payload could
# interest one of nlint's two checks; otherwise nlint runs. The exit code is
# always 0 either way: nlint advises, never blocks.
# === NON-CCSIM —— end of all you need to RUN it ===
#
# CCSIM (only if you EDIT it) —— registered PostToolUse (Edit|Write|MultiEdit)
# in the USER-level ~/.claude/settings.json (the Claude Desktop app executes
# user-level hooks and silently ignores project-level ones). It fires on EVERY
# Edit/Write/MultiEdit (matchers are tool-name only, no path filter), so the
# common edit must not pay a Python start; the rigorous basename check,
# repo-scope guard and both analyses all live in nlint.py. Token cost is ZERO in
# the common case; when nlint DOES flag, it exits 0 with structured JSON
# (`hookSpecificOutput.additionalContext`) —— the one PostToolUse channel
# reaching the model without blocking, as plain exit-0 stdout/stderr text
# reaches it not at all. Blocking-vs-advisory is decided entirely in the .py.
# `_hook` marks the file settings.json invokes —— every `.sh` here has it, no
# `.py` does; don't "tidy" it away.
#
# WHY TWO GATE PATTERNS. nlint's two checks have different scopes, so one gate
# cannot serve both:
#   * Numbering RESET is `response_`-only, so the FILENAME in the payload is a
#     complete and near-free gate (this was the original sole pattern).
#   * TENTH SIBLING (`- [n].10.`) applies to ANY file, so a filename gate would
#     have suppressed it everywhere except responses —— the exact failure this
#     second pattern exists to prevent. It gates on the WRITTEN TEXT instead:
#     every Edit/Write/MultiEdit payload carries the new text inline
#     (`content`/`new_string`), so "a bullet followed by a digit" plus a `.10`
#     somewhere in the same payload is a cheap SUPERSET of every shape nlint.py
#     can flag (`- 3.10.`, `- 12.10.`, `- 1.2.10.`). Deliberately loose:
#     over-firing costs one silent Python start (the .py then decides
#     rigorously), whilst under-firing loses the warning entirely.
# Both patterns are pure bash builtins —— no fork, no subshell, so the common
# edit still spawns nothing at all.
#
# TRADE-OFF ACCEPTED (payload text, not the file on disk). The gate can only see
# what this write CONTAINS, whereas nlint.py reads the finished file. Net
# effect: the tenth-sibling advisory fires when `.10` is INTRODUCED (or when the
# file is rewritten wholesale), not on every later unrelated edit of a file that
# already holds it. That is the point of the gate AND a useful anti-nag
# property. Known gap in the harmless direction: an edit that adds ONLY
# `- 3.11.` to a file already holding `- 3.10.` does not re-warn —— the reminder
# was already delivered when `.10` went in.

payload=$(cat)

case "$payload" in
  *response_*) ;;         # might involve a response_ file -> verify in Python
  *"- "[0-9]*".10"*) ;;   # might carry a level's 10th sibling -> ditto
  *) exit 0 ;;            # neither -> do nothing, no Python spawned
esac

printf '%s' "$payload" | python3 "$(dirname "$0")/nlint.py"
exit $?
