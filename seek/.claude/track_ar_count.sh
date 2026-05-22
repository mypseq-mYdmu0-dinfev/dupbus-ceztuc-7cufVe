#!/bin/bash

# AJAP AR Counter
# PostToolUse hook (matcher: Write) — fires after every Write tool call.
# Tracks AR file creation in applied/pending/skipped.

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

# Skip ❌_ files (Move Rule artifacts)
BASENAME=$(basename "$FILE_PATH")
if [[ "$BASENAME" == ❌_* ]]; then exit 0; fi

# Increment counter
COUNT=0
if [[ -f "$COUNTER_FILE" ]]; then COUNT=$(cat "$COUNTER_FILE" 2>/dev/null || echo 0); fi
NEW_COUNT=$((COUNT + 1))
echo "$NEW_COUNT" > "$COUNTER_FILE"

exit 0
