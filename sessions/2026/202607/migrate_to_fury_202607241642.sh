#!/bin/bash
# Migrate Claude's write-heavy home trees to the external SSD (FURY 2TB) to cut
# internal-SSD wear. Moves TWO trees, each independently and SAFELY (copy first,
# verify file counts, only THEN delete the source, then symlink):
#   1. ~/.claude                              -> /Volumes/FURY 2TB/.claude
#        Claude CODE / CLI: session transcripts (projects/), settings, hooks,
#        and any future skills. This is the whole family kept together on FURY.
#   2. ~/Library/Application Support/Claude    -> /Volumes/FURY 2TB/Library/Application Support/Claude
#        Claude DESKTOP app (CAI), ~13 GB, very high churn (~10 writes/min even idle).
# ~/.claude.json (the auth token, which lives in HOME, NOT inside ~/.claude) is
# left untouched on the internal SSD.
#
# RUN ONLY WITH EVERY CLAUDE WINDOW CLOSED — Claude Code CLI, the Claude desktop
# app (CAI), and this very session. Both trees hold the live state of any running
# Claude, so they can only move safely when nothing Claude is running. In a plain
# Terminal (Bypass not needed, it's your own shell):
#     bash "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/sessions/2026/202607/migrate_to_fury_202607241642.sh"
# Safe to re-run. Any mismatch or open file aborts THAT tree with its source intact.
# Revert commands: cp/ccsim/ssd_migration_guide.md and the revert-log.
set -u

migrate () {  # $1=source  $2=dest  $3=label
  local SRC="$1" DST="$2" LABEL="$3" SZ s d
  echo "== $LABEL =="
  if [ -L "$SRC" ]; then echo "  already a symlink -> $(readlink "$SRC"); skipping"; return 0; fi
  [ -e "$SRC" ] || { echo "  $SRC not found; skipping"; return 0; }
  if lsof +D "$SRC" >/dev/null 2>&1; then
    echo "  ABORT: files under $SRC are open — quit all Claude apps first; skipping this tree."; return 1; fi
  SZ="$(du -sh "$SRC" | cut -f1)"
  echo "  copying $SZ (ditto, metadata-preserving)..."
  mkdir -p "$(dirname "$DST")"
  ditto "$SRC" "$DST" || { echo "  ABORT: ditto failed; source intact."; return 1; }
  s="$(find "$SRC" -type f ! -name .DS_Store | wc -l | tr -d ' ')"
  d="$(find "$DST" -type f ! -name .DS_Store | wc -l | tr -d ' ')"
  echo "  verify: src=$s dst=$d"
  [ "$s" -eq "$d" ] || { echo "  ABORT: file-count mismatch — source intact, nothing deleted."; return 1; }
  rm -rf "$SRC" && ln -s "$DST" "$SRC"
  echo "  DONE: $SRC -> $(readlink "$SRC")"
}

[ -d "/Volumes/FURY 2TB" ] || { echo "ABORT: '/Volumes/FURY 2TB' not mounted."; exit 1; }
if pgrep -x claude >/dev/null 2>&1 || pgrep -x Claude >/dev/null 2>&1; then
  echo "ABORT: a Claude process is running. Quit ALL Claude Code / Claude-app windows, then re-run."; exit 1; fi

migrate "$HOME/.claude" "/Volumes/FURY 2TB/.claude" "Claude Code  (~/.claude)"
migrate "$HOME/Library/Application Support/Claude" "/Volumes/FURY 2TB/Library/Application Support/Claude" "Claude desktop app  (CAI, ~13GB)"

echo ""
echo "Relaunch Claude / CAI (with FURY mounted) and confirm past sessions + the app load normally."
echo "NEVER launch Claude while FURY is unmounted — a dangling symlink can spawn a fresh empty"
echo "local dir (split-brain). Recovery + the standing APFS-reformat plan: cp/ccsim/ssd_migration_guide.md"
