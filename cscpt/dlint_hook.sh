#!/bin/bash
# PostToolUse fast-path wrapper for dlint_quick.py.
#
# === NON-CCSIM —— start of all you need to RUN it ===
# WHAT: the registered PostToolUse hook fronting `dlint_quick.py` —— the harness
# invokes THIS file, not the .py. It exits 0 instantly unless the write mentions
# a `.md` or `.txt` path; otherwise the lint runs and its exit code passes
# through unchanged (2 = 🔴 RED found, or a deliverable still owes a FULL dlint,
# reason fed back on stderr for you to fix and rewrite; 0 = nothing to do).
# === NON-CCSIM —— end of all you need to RUN it ===
#
# CCSIM (only if you EDIT it) —— registered PostToolUse (Edit|Write|MultiEdit)
# in the USER-level ~/.claude/settings.json (the Claude Desktop app executes
# user-level hooks and silently ignores project-level ones). It fires on EVERY
# Edit/Write/MultiEdit (matchers are tool-name only, no path filter), so the
# common code/config edit must not pay a Python start.
#
# WHY THE GATE IS THIS LOOSE. `dlint_quick.py` now covers EVERY `.md`/`.txt`
# write in this repo, not the three comms filename roles it once matched, and
# it also carries the deliverable-escape gate that `elint_hook.sh` used to
# front. A single extension test is a cheap SUPERSET of both jobs whilst still
# skipping every `.py`, `.sh`, `.json` and notebook write. It matches the
# extension anywhere in the payload rather than only in `file_path`, because
# the JSON is scanned as one flat string here —— deliberately, since
# over-firing costs one silent Python start that then decides rigorously,
# whereas under-firing loses the enforcement entirely. Every rigorous check
# (repo scope, target extension, carve-outs, classification, receipts) lives in
# the .py and must stay there.
#
# Naming: `_hook` marks the file settings.json invokes; the `.py` is the lint
# body. Every `.sh` here carries `_hook`, no `.py` does —— don't "tidy" it.

payload=$(cat)

case "$payload" in
  *.md*|*.txt*) ;;   # might involve a prose file -> verify in Python
  *) exit 0 ;;       # definitely not -> do nothing, no Python spawned
esac

printf '%s' "$payload" | python3 "$(dirname "$0")/dlint_quick.py"
exit $?
