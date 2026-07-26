#!/bin/bash
# ============================================================================
# fury_unmounted.sh  —  DIAGNOSE and REPAIR ~/.claude after a FURY-unmounted
#   event (Claude Code started, or kept running, while FURY 2TB was absent).
# ============================================================================
# HOW TO RUN — in a PLAIN Terminal (quit Claude first if a repair is needed;
# the script tells you and refuses to touch anything while Claude is running):
#   bash "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/nscpt/fury_unmounted.sh"
# Safe to run any time, as often as you like: it is read-only unless it finds
# something broken, and it NEVER deletes anything.
# ----------------------------------------------------------------------------
# WHY THIS SCRIPT EXISTS
#   ~/.claude is a SYMLINK to /Volumes/FURY 2TB/.claude. Everything Claude Code
#   is configured with physically lives on the external FURY drive:
#     - settings.json      the ONLY live registration of the lint hooks (clint,
#                          dlint, hlint, nlint, tlint + the date-restore and
#                          post-compact hooks). They are registered at USER
#                          level because the Claude Desktop app silently ignores
#                          project-level hook registration, so this file is not
#                          in any git repo and a clone does NOT restore it.
#     - projects/*/memory/ the persistent auto-memory — user corrections that
#                          nothing else on the machine or in the cloud holds.
#     - projects/*/*.jsonl every session transcript.
#   If FURY is absent, that symlink dangles and Claude Code comes up with NO
#   user settings at all. Nothing errors: every lint is simply, silently dead —
#   which is the exact failure mode the whole hook system was built to prevent.
#
# WHAT ACTUALLY HAPPENS WHEN FURY IS UNMOUNTED (probed on this Mac, 202607)
#   (1) THE COMMON CASE — the mount point vanishes with the volume, so
#       ~/.claude is a DANGLING symlink. Nothing silently replaces it: both
#       `mkdir -p` and Node's recursive mkdir refuse to create through a
#       dangling symlink (ENOENT), and the `claude` CLI launched against such a
#       HOME left the symlink untouched and just ran config-less. So the damage
#       is "no config, no hooks, no memory", NOT data loss.
#   (2) THE DANGEROUS CASE — a surprise unmount can leave the mount-point
#       DIRECTORY /Volumes/FURY 2TB behind as an ordinary, empty folder on the
#       INTERNAL disk. Then ~/.claude resolves perfectly well to a real path,
#       and Claude Code creates a fresh, empty .claude tree inside it. Two
#       things follow, both silent: every lint is dead (a brand-new settings.json
#       has no hooks), and when FURY is plugged back in macOS finds the name
#       taken and mounts it as "/Volumes/FURY 2TB 1" — so every symlink on the
#       machine keeps pointing at the decoy on the internal disk. This script
#       detects that and tells you exactly what to do; it will not act blind.
#   (3) THE THIRD CASE — anything that removes the dangling symlink (a manual
#       "fix", a reinstall) lets a REAL ~/.claude directory be created in its
#       place, shadowing the intact FURY copy. This script repairs that.
#
# THE REPAIR DISCIPLINE (the house rule, and why)
#   VERIFY, then RENAME ASIDE, then LINK — never delete before linking. A prior
#   migration on this Mac ran `rm -rf SRC && ln -s DST SRC`, the `rm` failed
#   half-way because the app was still writing, the `&&` therefore skipped the
#   `ln -s`, and the result was a gutted folder with no symlink at all. So: this
#   script only ever renames a stray directory to a timestamped name beside it,
#   creates the symlink, and reports where the stray went. It runs no `rm` on
#   any directory, ever. (Removing a dangling or wrong SYMLINK is not a
#   deletion — a symlink holds no data — and is the only unlink performed.)
#
# WHAT IT WILL NOT DO
#   It will not create a symlink to a missing target and call that fixed. If
#   FURY is not mounted, it says so and stops: mount FURY, then re-run.
# ----------------------------------------------------------------------------
set -u

# Real values. FURY_VOL and HOME are honoured as-is so the detection logic can
# be exercised against a sandbox instead of the live configuration; the repair
# is separately gated on the TARGET existing, so no override can make the script
# link to nothing. FURY_SELFTEST=1 is the ONE test seam (see its uses below);
# it is set only by cp/ccsim/sandbox/fury_unmounted_regression_test.py.
VOL="${FURY_VOL:-/Volumes/FURY 2TB}"
LINK="$HOME/.claude"
TARGET="$VOL/.claude"
REPO="/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
PROBE="cp/ccsim/sandbox/hook_probe_response_.md"
TS="$(TZ='Australia/Sydney' date +%Y%m%d%H%M 2>/dev/null || date +%Y%m%d%H%M)"

say(){ printf '%s\n' "$*"; }
rule(){ say "----------------------------------------------------------------------"; }

[ -n "${HOME:-}" ] || { say "ABORT: HOME is not set."; exit 1; }

say "fury_unmounted.sh — checking Claude Code's configuration link."
say "  volume : $VOL"
say "  link   : $LINK"
rule

# --- 1. Is FURY mounted, and mounted where it should be? --------------------
# Under FURY_SELFTEST the answer comes from FURY_TEST_MOUNTED instead, because a
# regression test cannot mount a real volume. This cannot cause harm: the repair
# is separately gated on $TARGET existing.
MOUNTED=no
if [ "${FURY_SELFTEST:-}" = "1" ]; then
  [ "${FURY_TEST_MOUNTED:-no}" = "yes" ] && MOUNTED=yes
elif /sbin/mount | /usr/bin/grep -q "on $VOL ("; then
  MOUNTED=yes
fi

# A collided mount ("FURY 2TB 1", "FURY 2TB 2", ...) means the real name was
# occupied by a leftover directory when the drive was reattached.
COLLIDED="$(/sbin/mount 2>/dev/null | /usr/bin/grep -oE "on ${VOL} [0-9]+ " | /usr/bin/sed 's/^on //; s/ $//' | /usr/bin/head -1)"

if [ "$MOUNTED" = "no" ]; then
  say "FURY: NOT MOUNTED."
  if [ -n "$COLLIDED" ]; then
    say ""
    say "  🚨 BUT THE DRIVE IS MOUNTED UNDER THE WRONG NAME: '$COLLIDED'"
    say "     macOS did that because '$VOL' was already taken by a leftover"
    say "     folder on the INTERNAL disk. Every symlink on this Mac still"
    say "     points at that leftover, so nothing sees the real drive."
    say "     FIX (in Finder / Terminal, with Claude quit):"
    say "       1. Eject the drive."
    say "       2. Rename the leftover aside — it is on the internal disk:"
    say "            mv '$VOL' '${VOL}.stale-${TS}'"
    say "          (rename, do NOT delete: it may hold data written while the"
    say "           real drive was away.)"
    say "       3. Re-attach the drive; it will mount as '$VOL' again."
    say "       4. Re-run this script."
  elif [ -d "$VOL" ]; then
    say ""
    say "  🚨 A LEFTOVER '$VOL' FOLDER EXISTS ON THE INTERNAL DISK."
    say "     The drive is gone but its mount point survived, so anything"
    say "     following ~/.claude is now reading and writing a decoy on the"
    say "     internal disk instead of failing loudly."
    if [ -e "$TARGET" ]; then
      n="$(find "$TARGET" -type f ! -name .DS_Store 2>/dev/null | wc -l | tr -d ' ')"
      say "     A decoy .claude ALREADY EXISTS there ($n files) — it is NOT your"
      say "     real configuration; your real one is on the drive."
    fi
    say "     FIX: quit Claude, then rename the leftover aside (never delete):"
    say "            mv '$VOL' '${VOL}.stale-${TS}'"
    say "          then re-attach FURY and re-run this script."
  else
    say ""
    say "  The drive is simply not attached. Nothing is broken and nothing"
    say "  needs repairing — Claude Code just has no configuration while it is"
    say "  away, so every lint hook is inactive."
  fi
  rule
  say "VERDICT: STOPPED — no repair attempted (a symlink to a missing drive"
  say "         would be a fake fix). Mount FURY 2TB, then re-run this script."
  exit 1
fi

say "FURY: mounted at $VOL ✅"
[ -n "$COLLIDED" ] && say "  NOTE: the drive is ALSO mounted at '$COLLIDED' — eject the duplicate."

# --- 2. Is the real configuration present on FURY? --------------------------
if [ ! -d "$TARGET" ]; then
  say "  ⚠️  $TARGET does not exist on the mounted drive."
  rule
  say "VERDICT: STOPPED — the drive is mounted but carries no .claude folder."
  say "         Do NOT link to it. Check you mounted the right drive; if it is"
  say "         genuinely gone, this is the FURY-LOST case — see"
  say "         cp/ccsim/doomsday.md § Scenario B."
  exit 1
fi
if [ ! -f "$TARGET/settings.json" ]; then
  say "  ⚠️  $TARGET exists but has NO settings.json — that file is the only"
  say "      live hook registration, so this copy looks incomplete."
  say "      Continuing (the link is still the right thing), but read the"
  say "      recovery note printed at the end."
fi
say "Configuration on FURY: present ✅"

# --- 3. What state is ~/.claude in? -----------------------------------------
# A symlink carrying the right target necessarily RESOLVES by this point —
# steps 1 and 2 already exited if the volume or its .claude were missing — so
# "dangling" is not a state that can survive to here; it is reported earlier,
# and more usefully, as "FURY not mounted".
STATE=""
if [ -L "$LINK" ]; then
  CUR="$(readlink "$LINK")"
  if [ "$CUR" = "$TARGET" ]; then STATE="ok"; else STATE="wrong-target"; fi
elif [ -d "$LINK" ]; then
  STATE="stray-dir"
elif [ -e "$LINK" ]; then
  STATE="stray-file"
else
  STATE="missing"
fi

case "$STATE" in
  ok)           say "~/.claude: correct symlink -> $TARGET ✅" ;;
  wrong-target) say "~/.claude: symlink points at the WRONG target ($CUR)." ;;
  stray-dir)    say "~/.claude: a REAL FOLDER has taken the symlink's place (split-brain)." ;;
  stray-file)   say "~/.claude: a real FILE sits where the symlink should be." ;;
  missing)      say "~/.claude: missing entirely." ;;
esac

# --- 4. Repair (only if needed) ---------------------------------------------
REPAIRED=no
STRAY=""
if [ "$STATE" != "ok" ]; then
  # A running Claude holds open handles on the wrong path and would keep
  # writing there behind the new symlink. Refuse rather than race it.
  # (Under FURY_SELFTEST this guard is skipped: the regression test drives a
  # sandbox HOME that no running Claude can possibly be using.)
  if [ "${FURY_SELFTEST:-}" = "1" ]; then
    RUNNING=""
  else
    RUNNING="$( { pgrep -x Claude; pgrep -x claude; pgrep -f 'Claude Helper'; } 2>/dev/null | sort -u )"
  fi
  if [ -n "$RUNNING" ]; then
    rule
    say "VERDICT: REPAIR NEEDED, BUT CLAUDE IS RUNNING (PIDs $(echo $RUNNING | tr '\n' ' '))."
    say "         Quit Claude completely (⌘Q; Force Quit any 'Claude Helper' in"
    say "         Activity Monitor), then run this script again from a plain"
    say "         Terminal. Nothing has been changed."
    exit 1
  fi

  case "$STATE" in
    stray-dir|stray-file)
      # Show the user what is in the stray BEFORE moving it, so they can judge
      # whether anything written while FURY was away is worth merging back.
      if [ -d "$LINK" ]; then
        n="$(find "$LINK" -type f ! -name .DS_Store 2>/dev/null | wc -l | tr -d ' ')"
        say "  Stray contents: $n file(s)."
        find "$LINK" -maxdepth 3 -type d -name memory 2>/dev/null | while IFS= read -r m; do
          say "  ⚠️  the stray contains auto-memory: $m — review before discarding."
        done
      fi
      STRAY="${LINK}.stray-${TS}"
      mv "$LINK" "$STRAY" || { say "ABORT: could not rename the stray aside. Nothing changed."; exit 1; }
      say "  Stray preserved (NOT deleted) at: $STRAY"
      ;;
    dangling|wrong-target)
      # Unlinking a symlink destroys no data — it is a pointer, not a folder.
      rm "$LINK" || { say "ABORT: could not remove the old symlink. Nothing changed."; exit 1; }
      say "  Old symlink removed (no data involved)."
      ;;
  esac
  ln -s "$TARGET" "$LINK" || { say "ABORT: could not create the symlink."; exit 1; }
  REPAIRED=yes
  say "  Symlink restored: $LINK -> $(readlink "$LINK")"
fi

# --- 5. Verify (never assume the repair worked) ------------------------------
rule
say "VERIFYING"
FAIL=0
if [ -L "$LINK" ] && [ "$(readlink "$LINK")" = "$TARGET" ]; then
  say "  ✅ ~/.claude is a symlink to $TARGET"
else
  say "  ❌ ~/.claude is still not the expected symlink"; FAIL=1
fi
if [ -d "$LINK/" ]; then
  say "  ✅ it resolves to a real folder"
else
  say "  ❌ it does not resolve"; FAIL=1
fi
if [ -r "$LINK/settings.json" ]; then
  say "  ✅ settings.json is readable through the link"
else
  say "  ❌ settings.json is NOT readable through the link"; FAIL=1
fi

# Hook registrations: present, well-shaped, and every referenced file existing.
# A hook whose command path no longer exists exits 127 and the harness carries
# on in total silence, so "registered" alone is not good enough.
if [ -r "$LINK/settings.json" ] && command -v python3 >/dev/null 2>&1; then
  HOOKOUT="$(python3 - "$LINK/settings.json" <<'PY'
import json,os,shlex,sys
try:
    hooks=json.load(open(sys.argv[1])).get('hooks',{})
except Exception as e:
    print("ERR unreadable settings.json: %s" % e); raise SystemExit
if not hooks:
    print("ERR no 'hooks' object registered"); raise SystemExit
total=dead=0
for ev,groups in hooks.items():
    for g in groups:
        for h in (g.get('hooks') or [g]):
            c=h.get('command','')
            if not c: continue
            total+=1
            paths=[t for t in shlex.split(c) if '/' in t]
            bad=[p for p in paths if not os.path.exists(p)]
            if bad:
                dead+=1
                print("DEAD %s -> %s" % (ev,c))
print("COUNT %d %d" % (total,dead))
PY
)"
  if printf '%s' "$HOOKOUT" | grep -q '^ERR'; then
    say "  ❌ hooks: $(printf '%s' "$HOOKOUT" | sed -n 's/^ERR //p')"; FAIL=1
  else
    printf '%s\n' "$HOOKOUT" | grep '^DEAD' | while IFS= read -r l; do say "  ❌ $l"; done
    tot="$(printf '%s' "$HOOKOUT" | sed -n 's/^COUNT \([0-9]*\) .*/\1/p')"
    dead="$(printf '%s' "$HOOKOUT" | sed -n 's/^COUNT [0-9]* \([0-9]*\)/\1/p')"
    if [ "${dead:-1}" = "0" ]; then
      say "  ✅ ${tot} hook command(s) registered, all resolving"
    else
      say "  ❌ ${dead} of ${tot} hook command(s) point at a missing file"; FAIL=1
    fi
  fi
else
  say "  ℹ️  hook registrations not checked (python3 unavailable)"
fi

# --- 6. Verdict + the one thing a file check can never prove ----------------
rule
if [ "$FAIL" -eq 0 ]; then
  if [ "$REPAIRED" = "yes" ]; then
    say "VERDICT: REPAIRED ✅  ~/.claude points at FURY again and the hook"
    say "         registrations are intact."
  else
    say "VERDICT: HEALTHY ✅  Nothing needed repairing."
  fi
else
  say "VERDICT: STILL BROKEN ❌  See the ❌ lines above."
  say "         If settings.json or its hooks are the problem, restore them by"
  say "         merging the 'hooks' object from"
  say "           $REPO/.claude/hooks_user_settings.reference.json"
  say "         into ~/.claude/settings.json (MERGE, never overwrite — the file"
  say "         also holds unrelated preferences), correcting every absolute"
  say "         path, then re-run this script."
fi
say ""
say "LAST STEP — the checks above prove the FILES are right; only this proves"
say "the hooks actually FIRE. Relaunch Claude, then ask it to edit this file"
say "with its Edit/Write tool:"
say "    $PROBE"
say "It deliberately contains errors, so a live hook chain BLOCKS the write"
say "with a dlint RED report. A silent success means the hooks are DEAD."
say ""
say "Keep any .stray-* folder until Claude has run cleanly for a day, then"
say "delete it yourself to reclaim space."
[ -n "$STRAY" ] && say "  This run's stray: $STRAY"
rule
[ "$FAIL" -eq 0 ] || exit 1
exit 0
