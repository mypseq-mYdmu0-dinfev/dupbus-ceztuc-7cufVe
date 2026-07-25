#!/bin/sh
# PostToolUse fast-path wrapper for tlint.py (the timestamp linter).
#
# NON-CCSIM (to RUN) —— THIS file is the registered hook: PostToolUse
# (Edit|Write|MultiEdit) in the USER-level ~/.claude/settings.json; the harness
# invokes it, not the .py. It reads the tool payload on stdin and exits 0
# IMMEDIATELY unless that payload carries a 12-digit TS starting "20";
# otherwise it pipes the payload to tlint.py, whose exit code is always 0 ——
# tlint warns, never blocks. Run, not read —— see README.
#
# CCSIM (only if you EDIT it) —— mirrors dlint_hook.sh / nlint_hook.sh so a
# TS-less write costs no Python spawn. The grep is deliberately loose: it only
# decides whether Python is worth spawning; the real TS/pairing rules live in
# tlint.py. POSIX `/bin/sh` suffices. `_hook` marks the file settings.json
# invokes —— every `.sh` here has it, no `.py` does.
payload="$(cat)"
printf '%s' "$payload" | grep -qE '20[0-9]{10}' || exit 0
printf '%s' "$payload" | python3 "$(dirname "$0")/tlint.py"
