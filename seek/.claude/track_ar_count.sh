#!/bin/bash

# CCIC-GCL AR Counter & S0.4 Re-Read Enforcer
# PostToolUse hook (matcher: Write) — fires after every Write tool call.
# Tracks AR file creation in applied/pending/skipped; injects ccic_gcl.md
# into context at every multiple of 5 (enforcing S0.4 compliance).

COUNTER_FILE="/tmp/seek_job_count"
SEEK_DIR="/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek"

# Parse tool input from stdin
TOOL_DATA=$(cat 2>/dev/null)
if [[ -z "$TOOL_DATA" ]]; then exit 0; fi

FILE_PATH=$(echo "$TOOL_DATA" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    inp = d.get('tool_input', d.get('input', {}))
    if isinstance(inp, dict):
        print(inp.get('file_path', ''))
except:
    pass
" 2>/dev/null)

if [[ -z "$FILE_PATH" ]]; then exit 0; fi

# Only count writes to AR paths
IS_AR=0
for P in "/seek/applied/" "/seek/pending/" "/seek/skipped/"; do
    if [[ "$FILE_PATH" == *"$P"* ]]; then IS_AR=1; break; fi
done
if [[ "$IS_AR" -eq 0 ]]; then exit 0; fi

# Skip DEL_ files (Move Rule artifacts)
BASENAME=$(basename "$FILE_PATH")
if [[ "$BASENAME" == DEL_* ]]; then exit 0; fi

# Increment counter
COUNT=0
if [[ -f "$COUNTER_FILE" ]]; then COUNT=$(cat "$COUNTER_FILE" 2>/dev/null || echo 0); fi
NEW_COUNT=$((COUNT + 1))
echo "$NEW_COUNT" > "$COUNTER_FILE"

# Inject ccic_gcl.md at every multiple of 5 (S0.4)
if [[ $((NEW_COUNT % 5)) -eq 0 ]]; then
    echo ""
    echo "==================================================================="
    echo "MANDATORY RE-READ — S0.4 TRIGGERED (N=${NEW_COUNT})"
    echo "Per ccic_gcl.md S0.4: re-read ccic_gcl.md in full before next card."
    echo "Declare in chat: ✅ ccic_gcl.md — then proceed with strict compliance."
    echo "==================================================================="
    echo ""
    cat "$SEEK_DIR/context/ccic_gcl.md"
    echo ""
    echo "==================================================================="
    echo "END RE-READ. N=${NEW_COUNT}. Proceed."
    echo "==================================================================="
fi

exit 0
