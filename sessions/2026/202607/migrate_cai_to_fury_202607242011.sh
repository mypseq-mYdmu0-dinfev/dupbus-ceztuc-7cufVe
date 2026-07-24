#!/bin/bash
# ============================================================================
# HARDENED (v2) migration of the Claude desktop app (CAI) data dir to FURY.
#   ~/Library/Application Support/Claude  ->  symlink to
#   /Volumes/FURY 2TB/Library/Application Support/Claude
# v2 folds in an adversarial 3-reviewer audit (#debate). See cp/ccsim/ssd_migration_guide.md §7.
# ============================================================================
# WHAT WENT WRONG BEFORE (baked-in; do not rely on chat):
#   The first script did `rm -rf SRC && ln -s DST SRC`. `rm -rf` FAILED
#   ("Directory not empty") because CAI's "Claude Helper" children were still
#   running; `&&` skipped `ln -s` (no symlink) and the partial rm GUTTED the live
#   folder -> blank, signed-out CAI. Data was safe on FURY; the app was wrecked.
#
# WHY v2 IS SAFE (the audit's fixes):
#   - Never deletes the source: RENAME ASIDE (mv, atomic) THEN symlink. A failure
#     can't leave a gutted dir with no link.
#   - RE-VERIFIES zero Claude processes + no open files IMMEDIATELY before the mv
#     (closes the multi-minute copy window where CAI could relaunch -> split-brain).
#   - Broad process guard (Claude, claude, Claude Helper*, the app bundle, crashpad),
#     a clean `quit` first, polled re-check, force-kill only stragglers.
#   - Proves FURY is a REAL mountpoint (not a leftover dir), rejects a duplicate
#     "FURY 2TB 1" mount, refuses to run from inside Claude, single-instance lock.
#   - Verifies BOTH file count AND byte size; aborts on an implausibly small source.
#   - Signal-protected mv+ln; a mid-flight interruption is detected + healable on re-run.
#   - The FURY copy is your LIVE data and is labelled DO-NOT-DELETE; only the
#     internal aside (and any old stale snapshot) are ever called deletable.
#
# HOW TO RUN:
#   1. Cmd-Q the CAI app, and quit any Claude Code CLI + this session.
#   2. Confirm FURY 2TB is mounted (Disk Utility).
#   3. In a PLAIN Terminal (NOT inside Claude):
#        bash "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/sessions/2026/202607/migrate_cai_to_fury_202607242011.sh"
#   4. Relaunch CAI (FURY mounted). GOOD = your named sessions + pins + dark-mode
#      are back. A forced sign-in with EMPTY sessions = STOP, don't delete backups.
# ----------------------------------------------------------------------------
set -uo pipefail
LOC="$HOME/Library/Application Support/Claude"
VOL="/Volumes/FURY 2TB"
FURY="$VOL/Library/Application Support/Claude"
TS="$(TZ='Australia/Sydney' date +%Y%m%d%H%M%S)"          # seconds: no same-minute collision
ASIDE="${LOC}.premigrate-backup-${TS}"
STALE=""
LOCK="/tmp/migrate_cai_to_fury.lock"
say(){ printf '%s\n' "$*"; }
# Match ONLY Claude/CAI processes (the rescue script's proven-working set). Do NOT
# match `chrome_crashpad_handler` —— EVERY Electron app (Chrome, VS Code, Slack, …)
# runs one and instantly respawns it when killed, so that broad match never clears
# and the script false-aborts "Claude STILL running" (changing PID each run). Nor a
# bare app-bundle path. rename-aside + the lsof guard cover any lingering CAI FD.
claude_procs(){ { pgrep -x Claude; pgrep -x claude; pgrep -f 'Claude Helper'; } 2>/dev/null | sort -u; }
open_under(){ [ -n "$(lsof +D "$1" 2>/dev/null)" ]; }       # 0 = something open (best-effort)

# 0. Single-instance lock --------------------------------------------------
mkdir "$LOCK" 2>/dev/null || { say "ABORT: another run in progress ($LOCK). Delete it if stale."; exit 1; }
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

# 1. Run from a plain Terminal, not inside Claude --------------------------
p="$PPID"
while [ "${p:-0}" -gt 1 ]; do
  c="$(ps -o comm= -p "$p" 2>/dev/null || true)"
  case "$c" in *Claude*|*claude*) say "ABORT: run from a PLAIN Terminal, not inside Claude ($c). NOTHING changed."; exit 1;; esac
  p="$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ' || true)"; [ -z "$p" ] && break
done

# 2. FURY must be a REAL mounted volume (not a leftover dir), no duplicate --
#    Uses diskutil (a direct volume query), NOT `mount | grep -q`: under
#    `set -o pipefail`, grep -q exits on first match and SIGPIPEs `mount`, so the
#    pipeline returns 141 and the check FALSE-ABORTS (v1's "not a mounted volume"
#    bug on a machine with many mounts). diskutil has no pipe and is authoritative.
diskutil info "$VOL" >/dev/null 2>&1 || { say "ABORT: '$VOL' is not a mounted volume (leftover dir?). NOTHING changed."; exit 1; }
[ -d "${VOL} 1" ] && { say "ABORT: a duplicate mount '${VOL} 1' exists — eject/rename it first."; exit 1; }

# 3. Heal a mid-flight interruption instead of re-breaking -----------------
if [ ! -e "$LOC" ] && [ ! -L "$LOC" ]; then
  cand="$(ls -d "${LOC}.premigrate-backup-"* 2>/dev/null | tail -1 || true)"
  if [ -d "$FURY" ]; then
    say "NOTICE: $LOC is missing but FURY data exists (a prior run was interrupted)."
    say "  FINISH the migration:  ln -s \"$FURY\" \"$LOC\""
    [ -n "$cand" ] && say "  or ROLL BACK to internal:  mv \"$cand\" \"$LOC\""
    exit 1
  fi
  say "ABORT: $LOC missing and no FURY data. Use nscpt/recover_cai_appdata.sh or Time Machine."; exit 1
fi

# 4. Validate an existing symlink (don't false-report success) -------------
if [ -L "$LOC" ]; then
  if [ "$(readlink "$LOC")" = "$FURY" ] && [ -d "$LOC/" ]; then say "Already correctly migrated -> $FURY. Nothing to do."; exit 0; fi
  say "ABORT: $LOC is a symlink to an unexpected/dead target ($(readlink "$LOC")). Fix manually; NOTHING changed."; exit 1
fi
[ -d "$LOC" ] || { say "ABORT: $LOC is not a directory. NOTHING changed."; exit 1; }

# 5. Clean quit, then force-quit stragglers, POLLED verify zero ------------
say "Asking CAI to quit cleanly (lets SQLite checkpoint)..."
osascript -e 'quit app "Claude"' 2>/dev/null || true; sleep 3
for _ in 1 2 3 4 5; do
  pkill -x Claude 2>/dev/null||true; pkill -x claude 2>/dev/null||true
  pkill -f 'Claude Helper' 2>/dev/null||true
  sleep 1
  pkill -9 -x Claude 2>/dev/null||true; pkill -9 -x claude 2>/dev/null||true; pkill -9 -f 'Claude Helper' 2>/dev/null||true
  sleep 2
  [ -z "$(claude_procs)" ] && break
done
R="$(claude_procs)"; [ -n "$R" ] && { say "ABORT: Claude STILL running (PIDs $(echo $R|tr '\n' ' ')). Force-Quit all 'Claude'/'Claude Helper' in Activity Monitor, re-run. NOTHING changed."; exit 1; }
open_under "$LOC" && { say "ABORT: files under $LOC still open. NOTHING changed."; exit 1; }
say "Confirmed: zero Claude processes, no open files."

# 6. Fresh FURY copy (stale aside first), verify COUNT + BYTES -------------
if [ -e "$FURY" ] || [ -L "$FURY" ]; then
  STALE="${FURY}.stale-${TS}"
  mv "$FURY" "$STALE" || { say "ABORT: could not move stale FURY copy aside; NOTHING changed."; exit 1; }
  say "Old stale FURY copy renamed aside: $STALE"
fi
say "Copying ~12G to FURY (ditto, a few minutes)..."
ditto "$LOC" "$FURY" || { say "ABORT: ditto failed; NOTHING moved, source intact."; exit 1; }
s="$(find "$LOC"  -type f ! -name .DS_Store | wc -l | tr -d ' ')"
d="$(find "$FURY" -type f ! -name .DS_Store | wc -l | tr -d ' ')"
sb="$(du -sk "$LOC"  | cut -f1)"; db="$(du -sk "$FURY" | cut -f1)"
say "verify: count internal=$s FURY=$d ; KB internal=$sb FURY=$db"
[ "${s:-0}" -ge 5000 ] || { say "ABORT: source file count ($s) implausibly low — refusing to migrate a blank dir. NOTHING moved."; exit 1; }
[ "$s" -eq "$d" ] || { say "ABORT: file-count mismatch; NOTHING moved, source intact."; exit 1; }
lo=$(( sb - sb/100 - 1024 )); hi=$(( sb + sb/100 + 1024 ))
{ [ "$db" -ge "$lo" ] && [ "$db" -le "$hi" ]; } || { say "ABORT: byte-size mismatch ($sb vs $db KB, >1%); NOTHING moved, source intact."; exit 1; }

# 7. RE-VERIFY right before the destructive mv (close the copy-window TOCTOU)
R="$(claude_procs)"; [ -n "$R" ] && { say "ABORT: Claude RELAUNCHED during the copy (PIDs $(echo $R|tr '\n' ' ')). NOTHING moved."; exit 1; }
open_under "$LOC" && { say "ABORT: files under $LOC re-opened during the copy. NOTHING moved."; exit 1; }

# 8. Critical section: rename-aside THEN symlink, signal-protected ---------
trap '' HUP INT TERM
mv "$LOC" "$ASIDE" || { trap - HUP INT TERM; say "ABORT: rename-aside failed; NOTHING changed."; exit 1; }
if ! ln -s "$FURY" "$LOC"; then
  mv "$ASIDE" "$LOC"; trap - HUP INT TERM
  say "symlink failed -> rolled back; verifying $LOC restored: $([ -d "$LOC" ] && echo OK || echo CHECK-MANUALLY). NOTHING lost."; exit 1
fi
trap - HUP INT TERM
{ [ "$(readlink "$LOC")" = "$FURY" ] && [ -d "$LOC/" ]; } || say "WARNING: symlink made but does not resolve — check the FURY mount before launching CAI."

# 9. Report — $FURY is LIVE data, only the aside(s) are deletable ----------
say ""
say "DONE. $LOC -> $(readlink "$LOC")"
say ""
say "DELETABLE backups (remove ONLY after CAI runs cleanly for ~a day):"
say "  $ASIDE   (internal pre-migration copy)"
[ -n "$STALE" ] && say "  $STALE   (old stale FURY snapshot)"
say ""
say "DO NOT DELETE — this IS your live CAI data, NOT a backup:"
say "  $FURY"
say ""
say "Relaunch CAI (FURY mounted)."
say "  GOOD  = your named sessions + pins + dark-mode are all back."
say "  BAD   = forced sign-in with an EMPTY session list -> STOP, do NOT delete backups, run:"
say "          bash \"$VOL/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/nscpt/recover_cai_appdata.sh\""
say "ROLLBACK to internal anytime:  rm \"$LOC\" && mv \"$ASIDE\" \"$LOC\""
say "RULES: never launch Claude while FURY is unmounted; never unmount FURY while CAI is open"
say "       (live SQLite on a removable disk can corrupt on a surprise unmount)."
