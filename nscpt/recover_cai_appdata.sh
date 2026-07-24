#!/bin/bash
# ============================================================================
# recover_cai_appdata.sh  —  RECOVER the Claude desktop app (CAI) after its
#   FURY-migrated data dir got knocked back to a broken/split-brain state.
# ============================================================================
# WHAT THIS IS / WHEN TO USE IT:
#   Once CAI's data dir is migrated (~/Library/Application Support/Claude is a
#   symlink -> /Volumes/FURY 2TB/Library/Application Support/Claude), two mishaps
#   can break it:
#     (A) You launched CAI while FURY was UNMOUNTED. The symlink was dangling, so
#         the OS/app created a fresh REAL local folder in its place (split-brain);
#         your real data still sits intact on FURY, just unlinked.
#     (B) FURY UNMOUNTED while CAI was open and writing. CAI's writes to the
#         vanished target failed; a stray local folder may have been made, and the
#         FURY copy's SQLite/LevelDB may have a half-written (recoverable) tail.
#   This script cleanly quits CAI, then re-points the path at the intact FURY data
#   (renaming any stray local folder aside — never deleting). It NEVER destroys.
#
# ANSWER to "can it save a corrupted (B) case?": Yes, in almost all cases.
#   - It restores the symlink so CAI reads the FURY data again.
#   - CAI/SQLite/LevelDB self-heal a half-written tail on next launch (journal/WAL
#     rollback); at worst you lose only the single most-recent unsynced action.
#   - Your sessions are also cloud-synced, so the account copy is a further backup.
#   - If the FURY copy is badly corrupt, fall back to the internal
#     `*.premigrate-backup-*` (kept by the migration script) or a Time Machine
#     snapshot from before the event.
#
# HOW TO RUN:
#   1. In a new CCSIM session, tell CC the situation (which mishap, A or B).
#   2. Ensure FURY 2TB is mounted (Disk Utility).
#   3. Quit CAI and this session; then in a PLAIN Terminal:
#        bash "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/nscpt/recover_cai_appdata.sh"
#   4. Relaunch CAI (FURY mounted). Expect a one-time sign-in.
# ----------------------------------------------------------------------------
set -u
LOC="$HOME/Library/Application Support/Claude"
FURY="/Volumes/FURY 2TB/Library/Application Support/Claude"
TS="$(TZ='Australia/Sydney' date +%Y%m%d%H%M)"

say(){ printf '%s\n' "$*"; }

# 1. FURY + intact copy must be present -------------------------------------
[ -d "/Volumes/FURY 2TB" ] || { say "ABORT: FURY 2TB not mounted. Mount it first."; exit 1; }
[ -d "$FURY" ] || { say "ABORT: FURY copy missing ($FURY). Do NOT proceed — use a Time Machine restore instead."; exit 1; }
fc="$(find "$FURY" -type f ! -name .DS_Store | wc -l | tr -d ' ')"
say "FURY copy file count: $fc"
[ "$fc" -ge 5000 ] || { say "ABORT: FURY copy looks too small ($fc files) — STOP, investigate, consider Time Machine."; exit 1; }

# 2. Force-quit every Claude/CAI process, verify zero -----------------------
say "Closing every Claude / CAI process (pkill never launches anything)..."
pkill -x Claude 2>/dev/null||true; pkill -x claude 2>/dev/null||true; pkill -f 'Claude Helper' 2>/dev/null||true
sleep 2
pkill -9 -x Claude 2>/dev/null||true; pkill -9 -x claude 2>/dev/null||true; pkill -9 -f 'Claude Helper' 2>/dev/null||true
sleep 2
REMAIN="$( { pgrep -x Claude; pgrep -x claude; pgrep -f 'Claude Helper'; } 2>/dev/null | sort -u )"
[ -n "$REMAIN" ] && { say "ABORT: Claude still running (PIDs $(echo $REMAIN|tr '\n' ' ')). Force-Quit all 'Claude'/'Claude Helper' in Activity Monitor, re-run."; exit 1; }
say "Confirmed: zero Claude processes running."

# 3. Fix the path -----------------------------------------------------------
if [ -L "$LOC" ]; then
  if [ "$(readlink "$LOC")" = "$FURY" ]; then
    say "Path is already a correct symlink -> FURY. Nothing to repair (a remount alone fixed it)."
    exit 0
  fi
  say "Path is a symlink to the WRONG target ($(readlink "$LOC")); replacing with the FURY link."
  rm "$LOC"
elif [ -e "$LOC" ]; then
  # a stray REAL folder (split-brain). Preserve it, never delete.
  mv "$LOC" "${LOC}.stray-${TS}" || { say "ABORT: could not move the stray local folder aside."; exit 1; }
  say "Stray local folder preserved at: ${LOC}.stray-${TS}"
fi
ln -s "$FURY" "$LOC" || { say "ABORT: could not create the symlink."; exit 1; }
say "DONE: $LOC -> $(readlink "$LOC")"

say ""
say "Relaunch CAI (FURY mounted). If a session looks truncated, CAI/cloud-sync should"
say "reconcile it. Keep any .stray-* / *.premigrate-backup-* folder until CAI runs"
say "cleanly for a day, then delete to reclaim space."
