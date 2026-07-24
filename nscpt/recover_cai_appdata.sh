#!/bin/bash
# ============================================================================
# recover_cai_appdata.sh  —  RECOVER the Claude desktop app (CAI) after its
#   FURY-migrated data dir got knocked back to a broken/split-brain state.
# ============================================================================
# WHEN SOMETHING BREAKS, THE WHOLE WORKFLOW IS JUST:
#     1. Cmd-Q CAI (quit the Claude desktop app completely).
#     2. Run THIS script in a plain Terminal.
#     3. Follow the terminal output — it tells you exactly what to do next
#        (relaunch as normal, or, only if a database is actually corrupt,
#         do a targeted Time Machine restore).
#   The output below is self-guiding: you do not need to remember anything.
#
# THIS IS ALSO THE RECOVERY SCRIPT IF THE MIGRATION ITSELF FAILED:
#   If the migration script that symlinked ~/Library/Application Support/Claude
#   onto FURY (migrate_cai_to_fury_202607242011.sh) went wrong — you lost
#   sessions, CAI won't start, data looks split — THIS is the script to run to
#   recover. It only ever re-points the path at the intact FURY data and
#   renames strays aside; it never migrates and never deletes.
# ----------------------------------------------------------------------------
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
#   This script cleanly quits CAI, checks the FURY databases are healthy, then
#   re-points the path at the intact FURY data (renaming any stray local folder
#   aside — never deleting). It NEVER destroys.
#
# ANSWER to "can it save a corrupted (B) case?": Yes, in almost all cases.
#   - It restores the symlink so CAI reads the FURY data again.
#   - CAI/SQLite/LevelDB self-heal a half-written tail on next launch (journal/WAL
#     rollback); at worst you lose only the single most-recent unsynced action.
#   - Your sessions are also cloud-synced, so the account copy is a further backup.
#   - The new SQLite integrity scan (below) tells you up-front whether the FURY
#     copy is genuinely healthy or whether you actually need a Time Machine
#     restore — so you never guess.
#   - If the FURY copy is badly corrupt, fall back to the internal
#     `*.premigrate-backup-*` (kept by the migration script) or a Time Machine
#     snapshot from before the event.
#
# HOW TO RUN:
#   1. In a new CCSIM session, tell CC the situation (which mishap, A or B).
#   2. Ensure FURY 2TB is mounted (Disk Utility).
#   3. Quit CAI (Cmd-Q) and this session; then in a PLAIN Terminal:
#        bash "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/nscpt/recover_cai_appdata.sh"
#   4. Relaunch CAI (FURY mounted). Expect a one-time sign-in.
# ----------------------------------------------------------------------------
set -u
LOC="$HOME/Library/Application Support/Claude"
FURY="/Volumes/FURY 2TB/Library/Application Support/Claude"
TS="$(TZ='Australia/Sydney' date +%Y%m%d%H%M)"

say(){ printf '%s\n' "$*"; }

# Integrity verdict, set by step 3, consumed by final_guidance() ------------
INTEGRITY="skip"      # skip (no sqlite3) | ok | warn | fail
SCANNED=0
FAILED_DBS=""         # comma-list of DBs that failed integrity_check (real corruption)
WARN_DBS=""           # comma-list of DBs that could not be verified (e.g. locked)

# final_guidance — the self-guiding closing message. Called from BOTH the
# "already correctly linked" early exit and the normal end, so the health
# verdict is always reported no matter which repair path ran.
final_guidance(){
  say ""
  say "----------------------------------------------------------------------"
  case "$INTEGRITY" in
    ok)
      say "✅ DATABASE INTEGRITY: OK — all $SCANNED SQLite databases passed."
      say "   NO Time Machine restore needed. The FURY data is healthy."
      say "   Just relaunch CAI (FURY mounted). That's it — you're done."
      ;;
    skip)
      say "ℹ️  DATABASE INTEGRITY: not scanned ('sqlite3' not found on this Mac)."
      say "   The path was still repaired. Relaunch CAI (FURY mounted); if a"
      say "   session looks truncated, cloud-sync should reconcile it."
      ;;
    warn)
      say "⚠️  DATABASE INTEGRITY: could not verify $WARN_DBS."
      say "   This is usually a still-open/locked DB, NOT corruption. Make sure"
      say "   CAI is fully quit, then re-run this script. All other databases"
      say "   scanned OK. Relaunching CAI is likely fine."
      ;;
    fail)
      say ""
      say "  ####################################################################"
      say "  ##                                                                ##"
      say "  ##   🚨  DATABASE CORRUPTION DETECTED — TIME MACHINE RESTORE      ##"
      say "  ##       NEEDED. Do NOT rely on relaunching CAI alone.            ##"
      say "  ##                                                                ##"
      say "  ####################################################################"
      say ""
      say "  Corrupt database(s): $FAILED_DBS"
      say ""
      say "  RESTORE — do EXACTLY this, nothing more:"
      say "    1. Keep FURY 2TB mounted."
      say "    2. Open Time Machine."
      say "    3. Restore ONLY this ONE folder (NOT your whole Mac, NOT the"
      say "       whole disk):"
      say "           ~/Library/Application Support/Claude"
      say "    4. Pick the LATEST snapshot you are SURE was good (before the"
      say "       crash/unmount that caused this)."
      say "    5. Let it overwrite, then relaunch CAI (FURY mounted)."
      say ""
      say "  Note: 'Cookies' / 'Trust Tokens' / 'DIPS' are Chromium infra DBs —"
      say "  if ONLY those are listed, CAI usually just rebuilds them and asks"
      say "  you to sign in again, so a restore may be unnecessary. A restore"
      say "  matters most when a session/state DB is named above."
      ;;
  esac
  say "----------------------------------------------------------------------"
  say ""
  say "Keep any .stray-* / *.premigrate-backup-* folder until CAI runs cleanly"
  say "for a day, then delete to reclaim space."
}

say "WORKFLOW: Cmd-Q CAI  ->  run this script  ->  follow the output below."
say ""

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

# 3. SQLite integrity scan of the FURY copy ---------------------------------
#   Runs now — after step 2 guarantees NO Claude process is writing — so the
#   databases are quiescent and the verdict is trustworthy.
#   CAI is an Electron/Chromium app: its SQLite DBs carry NO .db/.sqlite/.sqlite3
#   extension (they are named Cookies, DIPS, Trust Tokens, SharedStorage, ...),
#   so a filename glob would find ZERO databases and falsely report "OK".
#   We therefore detect real databases by the on-disk magic header
#   "SQLite format 3" (which also catches any literal *.db/*.sqlite/*.sqlite3),
#   AND run the check on any such file. LevelDB stores (Local Storage, IndexedDB,
#   Session Storage, ...) are DIRECTORIES sqlite3 cannot read, so the -type f
#   header test skips them automatically.
#   The prune list below (node_modules, bundled extensions, binary caches) is a
#   SPEED optimisation only — those trees provably never hold profile SQLite
#   state. The magic-header test, not the prune list, decides what gets scanned,
#   so a missed prune only costs a little time, never correctness.
#   The check opens each DB read-write on purpose: that lets SQLite replay any
#   half-written WAL/journal tail (exactly what CAI does on next launch) and give
#   the TRUE health verdict. A WAL checkpoint preserves all committed data — it
#   is normal DB maintenance, not destruction.
if command -v sqlite3 >/dev/null 2>&1; then
  say ""
  say "Scanning FURY copy's SQLite databases (PRAGMA integrity_check)..."
  while IFS= read -r -d '' db; do
    # Confirm it is really SQLite (extension-less DBs included) before scanning.
    hdr="$(head -c 16 "$db" 2>/dev/null | tr -d '\000')"
    if [ "$hdr" != "SQLite format 3" ]; then
      case "$db" in *.db|*.sqlite|*.sqlite3) : ;; *) continue ;; esac
    fi
    SCANNED=$((SCANNED+1))
    rel="${db#"$FURY"/}"
    out="$(sqlite3 "$db" 'PRAGMA integrity_check;' 2>&1)"
    if [ "$out" = "ok" ]; then
      say "  OK    : $rel"
    elif printf '%s' "$out" | grep -qiE 'unable to open|is locked|database is busy|disk i/o error'; then
      # Could not verify (e.g. still-locked DB) — NOT proof of corruption.
      say "  WARN  : $rel  ->  $(printf '%s' "$out" | head -1)"
      WARN_DBS="${WARN_DBS}${WARN_DBS:+, }$rel"
    else
      # integrity_check ran and reported structural problems, or the file is
      # malformed / not a database => genuine corruption.
      say "  FAIL  : $rel  ->  $(printf '%s' "$out" | head -1)"
      FAILED_DBS="${FAILED_DBS}${FAILED_DBS:+, }$rel"
    fi
  done < <(find "$FURY" -type f \
      ! -path '*/node_modules/*' ! -path '*/Claude Extensions/*' \
      ! -path '*/GPUCache/*' ! -path '*/Code Cache/*' ! -path '*/Dawn*Cache/*' \
      ! -path '*/Cache/*' ! -path '*/Crashpad/*' ! -path '*/blob_storage/*' \
      ! -name '*.js' ! -name '*.ts' ! -name '*.mjs' ! -name '*.cjs' ! -name '*.cts' ! -name '*.mts' \
      ! -name '*.json' ! -name '*.md' ! -name '*.map' \
      -print0 2>/dev/null)
  say "Scanned $SCANNED SQLite database(s)."
  if [ -n "$FAILED_DBS" ]; then INTEGRITY="fail"
  elif [ -n "$WARN_DBS" ]; then INTEGRITY="warn"
  elif [ "$SCANNED" -gt 0 ]; then INTEGRITY="ok"
  else INTEGRITY="warn"; WARN_DBS="(no SQLite databases found to scan)"; fi
else
  say ""
  say "NOTE: 'sqlite3' not found — skipping the database integrity scan."
  INTEGRITY="skip"
fi

# 4. Fix the path -----------------------------------------------------------
if [ -L "$LOC" ]; then
  if [ "$(readlink "$LOC")" = "$FURY" ]; then
    say ""
    say "Path is already a correct symlink -> FURY. Nothing to repair (a remount alone fixed it)."
    final_guidance
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

final_guidance
