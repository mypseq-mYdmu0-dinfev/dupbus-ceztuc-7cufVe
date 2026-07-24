#!/bin/bash
# ============================================================================
# RESCUE (v2): restore the CC sessions / pins / settings lost when the CAI
#              app-data migration half-failed — AND put CAI back on a safe footing.
#              (throwaway — delete after use)
# ============================================================================
# WHAT HAPPENED (baked-in rationale; do not rely on chat history):
#   migrate_to_fury_202607241642.sh ran at ~18:25 (the "1642" is only the script's
#   filename). It copied ~/Library/Application Support/Claude to
#   /Volumes/FURY 2TB/Library/Application Support/Claude (35584 files, a COMPLETE,
#   VERIFIED, still-intact snapshot) and then ran `rm -rf SRC && ln -s DST SRC`.
#   The `rm -rf` FAILED ("Directory not empty") because the CAI desktop app was
#   still running and re-writing the folder — so the `&&` short-circuited and NO
#   symlink was ever made. The partial `rm` had already destroyed ~34500 files, so
#   the LOCAL folder is now gutted; the still-running CAI rebuilt a blank state in
#   it — THAT is why sessions/pins/dark-mode vanished and you were signed out.
#   Your real data is SAFE in the FURY copy. CC transcripts (~/.claude/projects)
#   were never touched.
#
# WHY v2 IS DIFFERENT (answers your two concerns):
#   1. CLEAN SHUTDOWN IS NOW ENFORCED. The original migrate script only checked
#      `pgrep -x Claude`, which MISSES the "Claude Helper" processes — so it ran
#      while CAI was actually alive and raced it. This script force-quits EVERY
#      Claude/CAI process, VERIFIES zero remain, and ABORTS (pointing you to
#      Activity Monitor) if any survive — before it touches anything.
#   2. SAFER TARGET. By default it restores CAI to the INTERNAL disk, not the
#      external symlink. CAI on the HFS+ "noowners" external volume is untested and
#      more corruption-prone; keeping CAI internal until the planned Dec-2026 APFS
#      reformat is the low-risk choice. To complete the original FURY symlink
#      instead, set MODE="external" below.
#
#   It NEVER deletes: it renames the broken folder aside and keeps the FURY copy.
#
# HOW TO RUN:
#   1. Quit EVERY Claude window — the CAI app (Cmd-Q), any Claude Code CLI, AND the
#      rescue session you are reading this from. (The script also force-quits
#      stragglers, but quit the app yourself first so it flushes cleanly.)
#   2. Make sure FURY 2TB is mounted.
#   3. In a PLAIN Terminal (your own shell):
#        bash "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/sessions/2026/202607/rescue_cai_appdata_202607241900.sh"
#   4. Relaunch the CAI app (FURY mounted).
# ----------------------------------------------------------------------------
set -u
MODE="internal"   # "internal" (recommended) = restore CAI to the internal SSD.
                  # "external"               = complete the original symlink to FURY.

FURY="/Volumes/FURY 2TB/Library/Application Support/Claude"
LOC="$HOME/Library/Application Support/Claude"
TS="$(TZ='Australia/Sydney' date +%Y%m%d%H%M)"
BK=""

# 1. Guards: FURY mounted + intact copy present -----------------------------
[ -d "/Volumes/FURY 2TB" ] || { echo "ABORT: FURY 2TB not mounted."; exit 1; }
[ -d "$FURY" ]            || { echo "ABORT: intact FURY copy missing: $FURY"; exit 1; }

# 2. ENFORCE CLEAN SHUTDOWN (the fix to your question) ----------------------
echo "Closing any lingering Claude / CAI processes (pkill never launches anything)..."
pkill -x Claude 2>/dev/null || true
pkill -x claude 2>/dev/null || true
pkill -f 'Claude Helper' 2>/dev/null || true
sleep 2
pkill -9 -x Claude 2>/dev/null || true          # force-kill any survivor
pkill -9 -x claude 2>/dev/null || true
pkill -9 -f 'Claude Helper' 2>/dev/null || true
sleep 2
REMAIN="$( { pgrep -x Claude; pgrep -x claude; pgrep -f 'Claude Helper'; } 2>/dev/null | sort -u )"
if [ -n "$REMAIN" ]; then
  echo "ABORT: Claude processes STILL running (PIDs: $(echo $REMAIN | tr '\n' ' '))."
  echo "       Open Activity Monitor -> search 'Claude' -> Force-Quit every 'Claude' and"
  echo "       'Claude Helper' row -> then re-run this script."
  exit 1
fi
echo "Confirmed: zero Claude processes running."

# 3. Sanity: the FURY copy must be substantial (expected ~35584 files) ------
fcount="$(find "$FURY" -type f ! -name .DS_Store | wc -l | tr -d ' ')"
echo "FURY copy file count: $fcount  (expected ~35584)"
[ "$fcount" -ge 20000 ] || { echo "ABORT: FURY copy looks incomplete ($fcount files); STOP and investigate."; exit 1; }

# 4. Move the broken local folder aside (rename, NEVER delete) --------------
if [ -e "$LOC" ] || [ -L "$LOC" ]; then
  BK="${LOC}.broken-backup-${TS}"
  mv "$LOC" "$BK" || { echo "ABORT: could not move the broken local folder aside."; exit 1; }
  echo "Broken local folder preserved at:"
  echo "  $BK"
fi

# 5. Restore ----------------------------------------------------------------
if [ "$MODE" = "internal" ]; then
  echo "Restoring CAI to the INTERNAL disk (copying ~13 GB from FURY; takes a few minutes)..."
  ditto "$FURY" "$LOC" || { echo "ABORT: ditto restore failed."; [ -n "$BK" ] && mv "$BK" "$LOC"; exit 1; }
  rc="$(find "$LOC" -type f ! -name .DS_Store | wc -l | tr -d ' ')"
  echo "verify: restored=$rc  source=$fcount"
  [ "$rc" -eq "$fcount" ] || echo "WARNING: count mismatch ($rc vs $fcount) — inspect before launching CAI."
  echo "DONE (internal). The intact FURY copy is kept as a backup at:"
  echo "  $FURY"
elif [ "$MODE" = "external" ]; then
  echo "Backing up the FURY copy first (so the live app is never pointed at the only copy)..."
  ditto "$FURY" "${FURY}.backup-${TS}" || { echo "ABORT: FURY backup failed."; [ -n "$BK" ] && mv "$BK" "$LOC"; exit 1; }
  ln -s "$FURY" "$LOC" || { echo "ABORT: symlink failed; restoring broken folder."; [ -n "$BK" ] && mv "$BK" "$LOC"; exit 1; }
  echo "DONE (external). Symlink created:"
  echo "  $LOC -> $(readlink "$LOC")"
  echo "REMEMBER: never launch Claude while FURY is unmounted (a dangling symlink -> split-brain)."
else
  echo "ABORT: MODE must be 'internal' or 'external' (got '$MODE')."
  [ -n "$BK" ] && mv "$BK" "$LOC"
  exit 1
fi

echo
echo "Next: relaunch the CAI app. You should get back your sessions (through the 24th),"
echo "your pins, and your dark-mode / scale settings. Notes:"
echo "  - You may be asked to sign in once (expected)."
echo "  - ~41 OLD May/June sessions may still say 'Couldn't read this file' — their transcripts"
echo "    aged out months ago; that is pre-existing, NOT caused by this incident."
echo "  - Keep the .broken-backup-* folder (and the 17:52 Time Machine snapshot) until CAI"
echo "    has run cleanly for a day. Then you may delete the backup to reclaim space."
