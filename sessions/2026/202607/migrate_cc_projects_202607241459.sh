#!/bin/bash
# Migrate Claude Code session transcripts (~/.claude/projects) to the external
# SSD to cut internal-SSD write wear. Moves ONLY projects/ (the heavy, high-churn
# transcript store, ~1.4G); settings/hooks/skills/credentials in ~/.claude stay
# local. A symlink at ~/.claude/projects points to the FURY copy, so Claude Code
# keeps reading/writing transcripts there transparently.
#
# WHY a script you run (not the assistant): ~/.claude/projects holds the LIVE
# transcript of every open Claude Code session — including the one that wrote
# this. It can only be moved safely when NO Claude session is running. Quit ALL
# Claude Code / Claude-app (CAI) windows first, then run this in a plain Terminal:
#
#     bash "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/sessions/2026/202607/migrate_cc_projects_202607241459.sh"
#
# It is safe to re-run: it copies first, verifies file counts, and ONLY then
# deletes the source. On any mismatch or open file it aborts leaving the source
# untouched. To revert, see ccsim_migration_revertlog_202607241459.md.
set -euo pipefail

SRC="$HOME/.claude/projects"
DST="/Volumes/FURY 2TB/.claude/projects"

echo "== Claude Code projects -> FURY migration =="

[ -d "/Volumes/FURY 2TB" ] || { echo "ABORT: '/Volumes/FURY 2TB' not mounted."; exit 1; }
[ -e "$SRC" ]            || { echo "ABORT: $SRC not found."; exit 1; }
if [ -L "$SRC" ]; then echo "Already a symlink -> $(readlink "$SRC"). Nothing to do."; exit 0; fi

# Transcripts must be quiescent: no Claude process, no open files under projects/.
if pgrep -x claude >/dev/null 2>&1 || pgrep -x Claude >/dev/null 2>&1; then
  echo "ABORT: a Claude process is still running. Quit ALL Claude Code / Claude-app windows, then re-run."
  exit 1
fi
if lsof +D "$SRC" >/dev/null 2>&1; then
  echo "ABORT: files under $SRC are open. Close every Claude session, then re-run."
  exit 1
fi

SZ="$(du -sh "$SRC" | cut -f1)"
echo "Copying $SZ to FURY (ditto, metadata-preserving)..."
mkdir -p "/Volumes/FURY 2TB/.claude"
ditto "$SRC" "$DST"

s="$(find "$SRC" -type f | wc -l | tr -d ' ')"
d="$(find "$DST" -type f | wc -l | tr -d ' ')"
echo "Verify: source=$s files, dest=$d files."
if [ "$s" -ne "$d" ]; then
  echo "ABORT: file-count mismatch. Source left INTACT; nothing deleted. Investigate before retrying."
  exit 1
fi

echo "Counts match. Removing source and creating symlink..."
rm -rf "$SRC"
ln -s "$DST" "$SRC"
echo "DONE: $SRC -> $(readlink "$SRC")"
echo "Relaunch Claude / CAI and confirm your past sessions still load."
echo "IMPORTANT: never launch Claude while '/Volumes/FURY 2TB' is unmounted, or a"
echo "dangling symlink could make Claude start a fresh empty projects dir (split-brain)."
