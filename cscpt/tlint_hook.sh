#!/bin/sh
# PostToolUse fast-path wrapper for tlint.py (the timestamp linter).
#
# === NON-CCSIM —— start of all you need to RUN it ===
# WHAT: the registered PostToolUse hook fronting `tlint.py` —— the harness
# invokes THIS file, not the .py. It exits 0 instantly unless the payload
# carries a 12-digit TS starting "20"; otherwise tlint runs. The exit code is
# always 0 either way: tlint warns, never blocks.
# === NON-CCSIM —— end of all you need to RUN it ===
#
# CCSIM (only if you EDIT it) —— registered PostToolUse (Edit|Write|MultiEdit)
# in the USER-level ~/.claude/settings.json (the Claude Desktop app executes
# user-level hooks and silently ignores project-level ones). Mirrors
# dlint_hook.sh / nlint_hook.sh so a TS-less write costs no Python spawn. The
# grep is deliberately loose: it only decides whether Python is worth spawning;
# the real TS/pairing rules live in tlint.py. POSIX `/bin/sh` suffices. `_hook`
# marks the file settings.json invokes —— every `.sh` here has it, no `.py` does.
payload="$(cat)"
printf '%s' "$payload" | grep -qE '20[0-9]{10}' || exit 0
printf '%s' "$payload" | python3 "$(dirname "$0")/tlint.py"
