# CC Migration Revert-Log (202607241642)
*CC-facing only. Continues `ccsim_migration_revertlog_202607241459.md`. Exact state + revert for this turn's actions. See also `cp/ccsim/ssd_migration_guide.md`.*

---

## B1 — ~/Library/Application Support/Code → FURY  [DONE by CC]
- State: symlink `~/Library/Application Support/Code` → `/Volumes/FURY 2TB/Library/Application Support/Code` (1.4G, 5838 files, ditto+count-verified 5838=5838; VS Code quit, 0 open fds). Clean, no incident.
- REVERT: `rm "$HOME/Library/Application Support/Code" && mv "/Volumes/FURY 2TB/Library/Application Support/Code" "$HOME/Library/Application Support/Code"`

## B2 — ~/.codex robust guard  [DONE by CC]
- Context: user had already `rm -rf ~/.codex` (succeeded; not respawning). Pre-created a symlink so any FUTURE codex write lands on FURY, never internal.
- State: `~/.codex` → `/Volumes/FURY 2TB/.codex` (empty dir).
- REVERT: `rm ~/.codex` (leaves the empty FURY dir; delete it too if wanted).

## B3 — ~/.mcp (jobspy)  [NOT migrated]
- Aborted: the jobspy MCP server was RUNNING (spawned by Claude; config path in `~/.claude.json`). Also it's static `node_modules` (0 churn) → space-only 117M, not a wear win. Recommend leaving it, or migrate via a script when Claude is closed.
- If later migrated: symlink `~/.mcp` → `/Volumes/FURY 2TB/.mcp`; the absolute path in `~/.claude.json` resolves through the symlink. REVERT = `rm ~/.mcp && mv '/Volumes/FURY 2TB/.mcp' ~/.mcp`.

## B4 — Scripts created for the USER to run (not run by CC)
- `migrate_to_fury_202607241642.sh` — moves whole `~/.claude` + CAI `~/Library/Application Support/Claude` after all Claude quit (ditto+verify+delete+symlink each). REVERT per tree: `rm <symlink> && mv '/Volumes/FURY 2TB/<name>' <original>`.
- `setup_cc_tmpdir_202607241642.sh` — installs mount-guarded LaunchAgent setting `CLAUDE_CODE_TMPDIR=/Volumes/FURY 2TB/cctmp`. REVERT: `launchctl unload ~/Library/LaunchAgents/com.culous.cc-tmpdir.plist; rm -f ~/Library/LaunchAgents/com.culous.cc-tmpdir.plist ~/bin/cc-tmpdir.sh; launchctl unsetenv CLAUDE_CODE_TMPDIR`.
- Superseded + voided: `❌_migrate_cc_projects_202607241459.sh` (projects-only; replaced by migrate_to_fury which does whole ~/.claude).

## B5 — 16.4 pre-mount race check
- No user LaunchAgent/Daemon references any migrated path; VS Code + Claude apps are not Login Items. So nothing auto-writes a migrated path pre-mount → the split-brain race only fires on a MANUAL launch before FURY mounts. User discipline covers it. (Guide §3.)
