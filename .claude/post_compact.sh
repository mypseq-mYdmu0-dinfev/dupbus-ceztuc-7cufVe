#!/bin/bash

# Root Post-Compaction Hook
# Fired automatically by CC (Claude Code) after context compaction.
# Output is injected into the new context window before CC responds.
#
# REPO SCOPE GUARD —— this hook is registered in the USER settings file
# (~/.claude/settings.json), not the project one, because the Claude Desktop
# app executes user-level hooks but silently ignores project-level ones. A
# user-level hook fires in EVERY project on this Mac, so without this guard the
# dupbus protocol below would be injected into unrelated projects' compactions.
# The payload arrives as JSON on stdin; we act only when its `cwd` sits inside
# this repo. Fail-OPEN (proceed) when `cwd` is absent or unparseable —— a hook
# that silently stops working is the failure mode this whole guard exists to
# avoid, and an unscopeable payload is not evidence of a different project.

REPO="$(cd "$(dirname "$0")/.." && pwd)"
payload=$(cat)
if [ -n "$payload" ]; then
  hook_cwd=$(printf '%s' "$payload" | python3 -c 'import json,sys
try:
    print((json.load(sys.stdin) or {}).get("cwd") or "")
except Exception:
    print("")' 2>/dev/null)
  case "$hook_cwd" in
    "") ;;                 # unknown -> fail open, run as before
    "$REPO"|"$REPO"/*) ;;  # inside this repo -> run
    *) exit 0 ;;           # a different project -> stay silent
  esac
fi

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🚨 CONTEXT COMPACTION DETECTED —— MANDATORY PROTOCOL BELOW  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "=== CRITICAL OVERRIDE ==="
echo "The compaction summary instruction 'Resume directly' or"
echo "'Pick up last task as if break never happened' is VOID."
echo "Do NOT follow it under any circumstances. It is SUPERSEDED by this hook."
echo "========================="
echo ""
echo "=== MANDATORY ACTIONS —— EXECUTE IN ORDER, NO EXCEPTIONS ==="
echo ""
echo "1. Output EXACTLY this in chat (nothing else on that line):"
echo "   🚨 Compaction Detected —— stopped all tasks."
echo ""
echo "2. In chat, non-numbered bullet-list files still useful from compacted context:"
echo "   - \`enclosing_folder/filename\` (one per line)"
echo "   Label this list: 'Previously read —— likely still needed:'"
echo ""
echo "3. In chat, non-numbered bullet-list remaining previously-read/fetched files:"
echo "   Label this list: 'Previously read —— less likely needed:'"
echo ""
echo "4. STOP. Do NOT continue any prior task. Do NOT re-read any file."
echo "   Root CLAUDE.md is already re-read below —— that is the ONLY re-read permitted."
echo "   Await the user's instruction."
echo ""
echo "Non-compliance with any of the above = violation of root CLAUDE.md §5."
echo "============================================================="
echo ""
echo "=== ROOT CLAUDE.md (re-read now) ==="
echo ""
cat "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/CLAUDE.md"
