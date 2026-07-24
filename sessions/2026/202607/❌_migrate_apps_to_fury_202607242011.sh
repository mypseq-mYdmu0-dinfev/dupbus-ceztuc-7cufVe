#!/bin/bash
# Migrate approved Library app dirs to FURY, using the AIRTIGHT pattern learned
# from the CAI failure: PER-APP force-quit + ALL helpers -> verify that app is
# truly dead (skip it if a daemon respawns) -> lsof guard -> ditto -> verify
# counts -> RENAME ASIDE (mv, never rm-before-symlink) -> symlink -> keep a
# rollback backup (caches auto-removed, profiles kept). A failure can never gut a
# live dir: the source is preserved by an atomic mv, the symlink made before any
# delete. Each app is guarded independently, so one that won't cleanly quit
# (e.g. Perplexity's respawning perplexityd LaunchAgent) is SKIPPED, not raced.
# HOW TO RUN: FURY mounted, then:
#   bash "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/sessions/2026/202607/migrate_apps_to_fury_202607242011.sh"
set -u
FTS="$(TZ='Australia/Sydney' date +%Y%m%d%H%M)"
LIB="$HOME/Library"; FURYLIB="/Volumes/FURY 2TB/Library"

quit_app(){ pkill -x "$1" 2>/dev/null||true; pkill -f "$1 Helper" 2>/dev/null||true; sleep 1
            pkill -9 -x "$1" 2>/dev/null||true; pkill -9 -f "$1 Helper" 2>/dev/null||true; sleep 1; }
running(){ pgrep -x "$1" >/dev/null 2>&1 || pgrep -f "$1 Helper" >/dev/null 2>&1; }

migrate_one(){ # $1 relpath  $2 keep(yes/no)  $3 app-name  $4 label
  local SRC="$LIB/$1" DST="$FURYLIB/$1"
  echo "== $4 : $1 =="
  [ -L "$SRC" ] && { echo "  already symlink; skip"; return 0; }
  [ -e "$SRC" ] || { echo "  absent; skip"; return 0; }
  quit_app "$3"
  running "$3" && { echo "  '$3' still alive after force-quit (respawning daemon?) -> SKIP (migrate manually)"; return 1; }
  lsof +D "$SRC" >/dev/null 2>&1 && { echo "  OPEN FILES -> SKIP"; return 1; }
  mkdir -p "$(dirname "$DST")"
  ditto "$SRC" "$DST" || { echo "  ditto failed; src intact"; return 1; }
  local s d; s="$(find "$SRC" -type f ! -name .DS_Store|wc -l|tr -d ' ')"; d="$(find "$DST" -type f ! -name .DS_Store|wc -l|tr -d ' ')"
  echo "  verify src=$s dst=$d"; [ "$s" -eq "$d" ] || { echo "  MISMATCH -> SKIP, src intact"; return 1; }
  local A="${SRC}.migbak-${FTS}"
  mv "$SRC" "$A" || { echo "  rename-aside failed; SKIP"; return 1; }
  ln -s "$DST" "$SRC" || { echo "  symlink failed -> rollback"; mv "$A" "$SRC"; return 1; }
  echo "  DONE -> $(readlink "$SRC")"
  [ "$2" = no ] && { rm -rf "$A" && echo "  (cache backup removed)"; } || echo "  backup kept: $A"
}

[ -d "/Volumes/FURY 2TB" ] || { echo "ABORT: FURY not mounted"; exit 1; }
migrate_one "Caches/Google" no "Google Chrome" "Chrome cache"
migrate_one "Application Support/Google/Chrome/Default" yes "Google Chrome" "Chrome profile"
migrate_one "Caches/ai.perplexity.macv3" no "Perplexity" "Perplexity cache"
migrate_one "Application Support/TradingView" yes "TradingView" "TradingView"
migrate_one "Application Support/Spotify" yes "Spotify" "Spotify"
echo ""
echo "Rollback any item:  rm <symlink> && mv <its .migbak-${FTS}> <original path>"
echo "Delete kept .migbak-* backups only after the apps run cleanly on FURY."