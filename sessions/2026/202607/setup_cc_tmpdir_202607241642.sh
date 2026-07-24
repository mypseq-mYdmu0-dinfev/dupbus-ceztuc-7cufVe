#!/bin/bash
# Relocate Claude Code's EPHEMERAL scratch/temp root (default /private/tmp/claude-501,
# where sub-agent .output files + scratchpads live) to FURY, via the supported env var
# CLAUDE_CODE_TMPDIR, applied by a MOUNT-GUARDED login LaunchAgent: if FURY isn't
# mounted it safely unsets the var (falls back to internal /tmp), avoiding a stray dir.
# NOTE: this is only a MODEST wear win — the bulk of sub-agent write bytes are the
# transcripts under ~/.claude/projects (relocated by migrate_to_fury_...sh, whole ~/.claude).
# Run once in a plain Terminal, then QUIT + RELAUNCH Claude so it inherits the var.
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
