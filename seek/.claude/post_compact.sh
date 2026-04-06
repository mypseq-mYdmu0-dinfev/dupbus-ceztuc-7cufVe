#!/bin/bash

# CCIC-GCL Post-Compaction Hook
# Fired automatically by Claude Code after context compaction.
# Outputs CLAUDE.md content into the new context window,
# which instructs Claude Code to re-read all context files
# and resume the automation from the correct state.

echo "=== POST-COMPACTION RECOVERY ==="
echo "Context compaction has occurred. Re-reading core instructions now."
echo ""
cat "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/CLAUDE.md"
