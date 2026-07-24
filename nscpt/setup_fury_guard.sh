#!/bin/bash
# ============================================================================
# setup_fury_guard.sh  —  install a lightweight watcher that pops a CRITICAL
#   alert whenever the external SSD "FURY 2TB" is NOT mounted.
# ============================================================================
# WHY: apps/dirs migrated to FURY (Claude Code ~/.claude, VS Code, Chrome, etc.,
#   and soon CAI) become dangling symlinks if FURY is unmounted. Opening any of
#   them then risks a split-brain / blank state. This guard gives you a loud
#   visual STOP so you don't run anything except Disk Utility until FURY is back.
#
# HOW IT WORKS: a per-login LaunchAgent watches /Volumes; on any mount change it
#   runs a tiny guard. If FURY is absent it shows ONE critical alert (debounced —
#   it won't re-nag until FURY comes back and goes away again). The guard script
#   and its state flag live on the INTERNAL disk (NOT on FURY), so it still works
#   precisely when FURY is gone.
#
# HOW TO RUN (once), in a plain Terminal:
#   bash "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/nscpt/setup_fury_guard.sh"
# Revert: launchctl unload ~/Library/LaunchAgents/com.culous.fury-guard.plist;
#         rm -f ~/Library/LaunchAgents/com.culous.fury-guard.plist ~/bin/fury_guard.sh /tmp/.fury_absent_warned
# ----------------------------------------------------------------------------
set -e
GUARD="$HOME/bin/fury_guard.sh"
PLIST="$HOME/Library/LaunchAgents/com.culous.fury-guard.plist"
mkdir -p "$HOME/bin" "$(dirname "$PLIST")"

cat > "$GUARD" <<'SH'
#!/bin/sh
# Lives on the INTERNAL disk so it runs even when FURY is gone.
VOL="/Volumes/FURY 2TB"; FLAG="/tmp/.fury_absent_warned"
if /sbin/mount | /usr/bin/grep -q "on $VOL ("; then
  /bin/rm -f "$FLAG"                       # mounted -> reset the debounce
else
  if [ ! -f "$FLAG" ]; then               # newly absent -> warn ONCE
    /usr/bin/touch "$FLAG"
    /usr/bin/osascript -e 'display alert "FURY 2TB is UNMOUNTED" message "Migrated apps (Claude / CAI, VS Code, Chrome, etc.) now live on FURY. Do NOT open or run anything except Disk Utility until FURY is remounted — launching them now risks data split-brain." as critical' >/dev/null 2>&1 || true
  fi
fi
SH
chmod +x "$GUARD"

cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.culous.fury-guard</string>
  <key>ProgramArguments</key><array><string>/bin/sh</string><string>$GUARD</string></array>
  <key>RunAtLoad</key><true/>
  <key>WatchPaths</key><array><string>/Volumes</string></array>
</dict>
</plist>
PL

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "Installed + loaded. It will alert whenever FURY 2TB goes missing."
echo "Test it: eject FURY in Finder -> you should get a critical alert. Re-mount to reset."
