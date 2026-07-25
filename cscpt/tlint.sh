#!/bin/sh
# Fast-path shim for tlint (timestamp linter): spawn Python ONLY when the tool
# payload carries a 12-digit TS (starting 20). Mirrors dlint_hook.sh / nlint.sh
# so a TS-less Write/Edit costs no Python spawn. Non-blocking either way.
payload="$(cat)"
printf '%s' "$payload" | grep -qE '20[0-9]{10}' || exit 0
printf '%s' "$payload" | python3 "$(dirname "$0")/tlint.py"
