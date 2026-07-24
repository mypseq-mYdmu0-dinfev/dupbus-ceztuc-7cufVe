# CC Migration Revert-Log (202607241459)
*CC-facing only (per user 4.2.4). Exact state + revert commands for the SSD-wear migrations. NOT for the response_. Append-only; newest actions at bottom.*

---

## A1 — npm cache repointed to FURY  [DONE by CC, 202607241459]
- Action: `npm config set cache '/Volumes/FURY 2TB/npm-cache'` (created that dir). Was default `~/.npm`.
- Verify: `npm config get cache` → `/Volumes/FURY 2TB/npm-cache` ✅
- Old `~/.npm` (282M) left in place = now a stale disposable cache; user may reclaim: `rm -rf ~/.npm`.
- REVERT: `npm config delete cache`  (npm reverts to default `~/.npm`, recreated on next use).
- Risk: nil — npm cache is pure download cache; worst case a re-download.

## A2 — VS Code ~/.vscode moved to FURY + symlink  [DONE by CC, 202607241459]
- Final state: `~/.vscode` is a symlink → `/Volumes/FURY 2TB/.vscode` (1.2G, 18064 files, 23 extensions). VS Code was quit.
- INCIDENT + recovery (for the record): the cross-volume `mv` copied fully to FURY but its source-delete was blocked by Finder-regenerated `.DS_Store` files ("Directory not empty") on the `openai.chatgpt` extension dir; a stray `~/.vscode/.vscode` symlink was also created by the botched `ln -s` into the surviving dir. Recovery: removed stray symlink → `find ~/.vscode -name .DS_Store -delete` → confirmed 0 real files remained (all real content already on FURY) → `rm -rf ~/.vscode` → `ln -s '/Volumes/FURY 2TB/.vscode' ~/.vscode`. NO extension data lost (FURY copy verified complete BEFORE removing the empty leftover).
- REVERT: `rm ~/.vscode && mv '/Volumes/FURY 2TB/.vscode' ~/.vscode`
- Lesson: for the next big move (projects), use `ditto` + count-verify + then delete — NOT cross-volume `mv` (avoids the partial-delete race). Encoded in A3's script.

## A3 — Claude Code ~/.claude/projects → FURY  [SCRIPTED for USER; NOT run by CC]
- Script: `sessions/2026/202607/migrate_cc_projects_202607241459.sh` — user runs after quitting ALL Claude sessions (incl. CAI). Copies via `ditto`, verifies file counts, only then deletes source, then symlinks `~/.claude/projects` → `/Volumes/FURY 2TB/.claude/projects`.
- Why not CC: `~/.claude/projects` holds the LIVE transcript of every running session incl. the one advising; can only move with zero Claude sessions running.
- Post-run REVERT: `rm ~/.claude/projects && ditto '/Volumes/FURY 2TB/.claude/projects' ~/.claude/projects` (then optionally remove the FURY copy).
- Scope note: moves ONLY `projects/` (the churn, ~1.4G); settings/hooks/skills/`cic_login.local.md` stay local (keeps creds off noowners FURY).

## Pending / NOT actioned (investigation only)
- `~/.codex` — NOT deleted. Appears to be OpenAI-Codex agent data (schema: approval_mode, app_server_client_name, websocket_url, account_id + skills/memories/goals/state), actively written today; writer not caught by lsof (intermittent), plausibly the running `ChatGPTHelper` (OpenAI ChatGPT app). Stop-writer = quit ChatGPT app + remove from Login Items; THEN user deletes `rm -rf ~/.codex`. Held pending user confirm (their delete instruction was conditioned on identity/unused).
- Harness scratch `/private/tmp/claude-501/...` — SA investigating relocation.
- BIGGER wear sources found (outside dotfolder scope, flagged, NOT touched): `~/Library/Application Support/Claude/` (7.9G, ~323 writes/day — Claude DESKTOP/CAI app, likely the single biggest wear source), `~/Library/Application Support/Code/` (1.4G, ~111/day — VS Code real state, distinct from ~/.vscode).
