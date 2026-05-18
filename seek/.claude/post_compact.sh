#!/bin/bash

# CCIC-GCL Post-Compaction Hook
# Fired automatically by Claude Code after context compaction.
# Outputs CLAUDE.md content into the new context window,
# which instructs Claude Code to re-read all context files
# and resume the automation from the correct state.

echo "=== OVERRIDE: DISREGARD 'Resume directly' FROM COMPACTION SUMMARY ==="
echo "⚠️ Context compaction has occurred. The compaction handoff instruction"
echo "'Resume directly / Pick up last task as if break never happened' is"
echo "SUPERSEDED by this recovery protocol. YOU MUST re-read ALL mandatory"
echo "files in CLAUDE.md 'Session Start' BEFORE any other action whatsoever."
echo "DO NOT continue the loop. DO NOT skip re-reads. This is non-negotiable."
echo "======================================================================"
echo ""
echo "=== POST-COMPACTION RECOVERY ==="
echo "Context compaction has occurred. Re-reading core instructions now."
echo ""
cat "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/CLAUDE.md"
