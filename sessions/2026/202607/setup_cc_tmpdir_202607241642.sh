#!/bin/bash
# Relocate Claude Code's EPHEMERAL scratch/temp root (default /private/tmp/claude-501,
# where sub-agent .output files + scratchpads live) to FURY, via the supported env var
# CLAUDE_CODE_TMPDIR, applied by a MOUNT-GUARDED login LaunchAgent: if FURY isn't
# mounted it safely unsets the var (falls back to internal /tmp), avoiding a stray dir.
# NOTE: this is a genuine wear win despite the small size — the harness scratch is
# rewritten constantly during agent-fleet use. (The bulk of transcript bytes live in
# ~/.claude/projects, already relocated by migrate_to_fury_...sh.)
# This script only writes a LaunchAgent + a helper + sets an env var — it touches NO
# live app data dir, so the rename-aside migration discipline does not apply here; it
# is safe to run with apps open, and fully reversible (revert line printed at the end).
# HOW TO RUN — FURY mounted, in a PLAIN Terminal:
#   bash "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/sessions/2026/202607/setup_cc_tmpdir_202607241642.sh"
# Then QUIT + RELAUNCH Claude so it inherits the var.
set -e
DIR="/Volumes/FURY 2TB/cctmp"    # 23 bytes — under the ~30-byte AF_UNIX socket-path limit
BIN="$HOME/bin/cc-tmpdir.sh"
PLIST="$HOME/Library/LaunchAgents/com.culous.cc-tmpdir.plist"

mkdir -p "$HOME/bin" "$(dirname "$PLIST")" "$DIR"

cat > "$BIN" <<'SH'
#!/bin/sh
VOL="/Volumes/FURY 2TB"; DIR="$VOL/cctmp"
if /sbin/mount | /usr/bin/grep -q "on $VOL "; then
  /bin/mkdir -p "$DIR"
  /bin/launchctl setenv CLAUDE_CODE_TMPDIR "$DIR"
else
  /bin/launchctl unsetenv CLAUDE_CODE_TMPDIR   # FURY absent -> safe internal /tmp fallback
fi
SH
chmod +x "$BIN"

cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.culous.cc-tmpdir</string>
  <key>ProgramArguments</key>
  <array><string>/bin/sh</string><string>$BIN</string></array>
  <key>RunAtLoad</key><true/>
  <key>WatchPaths</key><array><string>/Volumes</string></array>
</dict>
</plist>
PL

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "Installed + loaded. Now: CLAUDE_CODE_TMPDIR=$(launchctl getenv CLAUDE_CODE_TMPDIR)"
echo "QUIT + RELAUNCH Claude (with FURY mounted); a new session's scratch should sit under $DIR."
echo "Revert: launchctl unload '$PLIST'; rm -f '$PLIST' '$BIN'; launchctl unsetenv CLAUDE_CODE_TMPDIR"
