# Doomsday & Resilience Playbook (WSM)
*What to do when hardware fails. Much of the WSM setup is HIGHLY LOCAL —— it does NOT travel by just cloning the repos to another Mac. This file is the recovery map for each failure. When a failure happens, the user starts a CCSIM session and states which scenario; CC reads the relevant §. Companion: `cp/ccsim/ssd_migration_guide.md`.*

---

## 1. What is portable vs WSM-local (read first)
- 1.1. PORTABLE (survives losing the Mac): the two git repos on GitHub (`dupbus-ceztuc-7cufVe`, `AJAP_repo`); cloud-synced Claude/ChatGPT sessions + memories (account-side); anything committed + pushed.
- 1.2. ON FURY (lost if FURY dies, unless backed up): all migrated app data —— CAI (`~/Library/Application Support/Claude`), VS Code state (`~/Library/Application Support/Code`), Chrome profile + caches, TradingView, Perplexity cache, `~/.claude` (CC transcripts + `settings.json`, which holds the ONLY live hook registrations —— §5.2.7), `~/.vscode`, `~/.codex`, `~/.mcp`(local), npm cache, `~/.ajap`.
- 1.3. WSM-LOCAL, NOT in git or cloud (must be RE-CREATED on a new Mac): the symlinks themselves (`~/.claude`, `~/.vscode`, `~/.codex`, `~/Library/.../Code`, `~/Library/.../Claude` → FURY); the LaunchAgents (`com.culous.fury-guard`, `com.culous.cc-tmpdir`) + their `~/bin` scripts; `npm config` cache path; `git config core.hooksPath`; macOS Automation/permissions grants; Finder "Date Added" metadata; credentials (`.claude/cic_login.local.md`, `seek/.claude/ajap_login.local.md` —— git-ignored by design); CAI's local settings (fonts/pins —— sessions are cloud, these local prefs are not).
- 1.4. RULE OF THUMB: git has the CODE + PROTOCOLS; cloud has the SESSIONS; FURY has the APP DATA; the WSM has the WIRING. A new Mac needs the wiring rebuilt by hand (re-run the setup scripts per §5.2 + re-grant permissions).

## 2. Scenario A —— FURY unmounted whilst CAI open, or CAI opened whilst FURY unmounted
- 2.1. Symptom: CAI blank/signed-out, or a stray real `~/Library/Application Support/Claude` folder appears (should be a symlink).
- 2.2. Fix: `⌘Q` CAI (and this CC session) → in a plain Terminal run `bash "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/nscpt/recover_cai_appdata.sh"` → follow its output. It force-quits CAI, SCANS the FURY databases for corruption, re-links the path to FURY, and renames any stray internal folder aside (never deletes).
- 2.3. If it reports SQLite corruption (only a surprise-unmount-mid-write can cause it —— the WSM's UPS + FURY's rarity make this very unlikely): the script states exactly whether/how to Time Machine restore (only the CAI folder). SQLite/LevelDB also self-heal a half-written tail on next launch, and sessions are cloud-synced —— worst case loses only the last unsynced action.
- 2.4. The mount-guard (`nscpt/setup_fury_guard.sh`, installed) pops a critical alert whenever FURY is missing —— heed it: touch nothing but Disk Utility until FURY is back.
- 2.5. SAME EVENT, OTHER VICTIM —— `~/.claude` (CC's own config: `settings.json`, the ONLY live hook registrations, plus `projects/*/memory/`). Symptom: no symptom —— every lint just silently stops firing. Fix: ⌘Q Claude → plain Terminal → `bash "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/nscpt/fury_unmounted.sh"`. It detects the link's state (correct / wrong target / stray real folder / missing), renames any stray aside (never deletes), restores the symlink, then verifies `settings.json` and every registered hook path resolves. If FURY isn't mounted it refuses to act rather than fake a fix.
- 2.6. The nastier variant that script also catches: a surprise unmount can leave the mount-point FOLDER `/Volumes/FURY 2TB` behind on the INTERNAL disk. Everything then silently reads a decoy there, and re-attaching FURY mounts it as `FURY 2TB 1` (name taken), so every symlink keeps pointing at the decoy. Remedy: rename the leftover aside (never delete), re-attach, re-run the script.

## 3. Scenario B —— FURY LOST (no access to FURY data; WSM + internal data intact)
- 3.1. What's gone: everything on FURY (§1.2) —— CAI data, VS Code state, Chrome profile, `~/.claude` transcripts, etc. The symlinks now dangle.
- 3.2. What survives: the git repos (GitHub); cloud CAI/ChatGPT sessions; and any INTERNAL backups still present (`*.migbak-*`, `*.premigrate-backup-*` —— only if not yet deleted). Time Machine helps ONLY for paths that were on the internal disk or if FURY had been added to TM (external volumes are excluded by default).
- 3.3. Recovery onto a NEW drive: name the new volume EXACTLY `FURY 2TB` (then every surviving symlink + LaunchAgent resolves unchanged —— the WSM wiring itself is intact in this scenario), OR rename it and re-point the symlinks. Then repopulate the FURY data: restore the FURY backup if one was made, else re-run the app migrations fresh (`sessions/2026/202607/migrate_cai_to_fury_202607242011.sh` for CAI, plus the per-app migration for the rest) from whatever internal `*.migbak-*`/`*.premigrate-backup-*` copies remain, and let CAI re-sync sessions from cloud. Re-clone both repos from GitHub if needed. Verify after: each symlink resolves (`readlink`), apps launch, and the hooks fire (§5.2.8) —— `~/.claude/settings.json` lived on FURY, so the lint registrations died with it and re-cloning the repo does NOT bring them back BY ITSELF —— you must copy them in by hand, either from `backup/backup_Claude/backup_Claude_FURY/backup_settings.json.md` (the whole file) or by merging `.claude/hooks_user_settings.reference.json` (hooks only); §5.2.7.
- 3.4. LESSON for prevention: keep an independent FURY backup (Time Machine that INCLUDES FURY, or a periodic `ditto` to a second drive) —— once the `*.migbak`/`*.premigrate` copies are deleted, FURY becomes the SOLE copy of that app data.

## 4. Scenario C —— FURY being REPLACED (the WSM + current FURY data are BOTH still available) *[HIGHLY LIKELY, ~1 year out]*
- 4.1. Context: the user plans to replace FURY (2TB PCIe 4.0) with a larger drive (e.g. FURY 4TB PCIe 5.0), so this WILL happen —— not soon, but treat it as expected.
- 4.2. The clean path (timing is user-controlled): follow `ssd_migration_guide.md` §5.3.0 —— QUIESCE FURY (Safe Mode boot, or quit every FURY-writer incl. Google Drive), then `ditto`/`rsync` a metadata-preserving copy of all of `/Volumes/FURY 2TB` to the new drive.
- 4.3. Name the new drive EXACTLY `FURY 2TB` → all symlinks + LaunchAgents resolve with zero changes. (If renamed, update every symlink target, the two LaunchAgent scripts, and the absolute hook command paths inside `~/.claude/settings.json` —— a rename breaks those paths silently, leaving every lint dead with no error; §5.2.7.)
- 4.4. This is also the opportunity to switch FURY to APFS (removes the HFS+ corruption-proneness) —— see `ssd_migration_guide.md` §5.
- 4.5. Verify after: each symlink resolves (`readlink`), apps launch, Finder "Date Added" survived on a sample, hooks still fire (§5.2.8).

## 5. Scenario D —— WSM being REPLACED (both the current WSM + FURY data are still available)
- 5.1. Move FURY to the new Mac (its app data comes with it). Clone both repos from GitHub.
- 5.2. RE-CREATE the WSM-local wiring (§1.3) —— this is the part cloning does NOT do:
  - 5.2.1. Re-create the symlinks: `~/.claude`, `~/.vscode`, `~/.codex`, `~/.mcp`(if migrated), `~/Library/Application Support/Code`, `~/Library/Application Support/Claude` → their FURY targets. (`~/.ajap` too.) Exact `ln -s` form: `ssd_migration_guide.md` §3.4.
  - 5.2.2. Re-run the setup scripts: `nscpt/setup_fury_guard.sh`, `sessions/2026/202607/setup_cc_tmpdir_202607241642.sh`.
  - 5.2.3. `npm config set cache '/Volumes/FURY 2TB/npm-cache'`; `git config core.hooksPath .githooks` (per repo).
  - 5.2.4. Re-supply credentials (`.claude/cic_login.local.md` etc. —— they're git-ignored, so copy them from the user's own secure store).
  - 5.2.5. Re-grant macOS permissions (Automation for the usage/keystroke scripts, Full Disk if needed).
  - 5.2.6. CAI: sign in → sessions re-sync from cloud; re-set local prefs (fonts/pins) —— those are local, not cloud.
  - 5.2.7. RE-REGISTER THE HOOKS —— the registrations are not in git: they live in `~/.claude/settings.json` (USER level), because the Claude Desktop app executes user-level hooks and silently ignores project-level ones, so user level is the only thing that runs —— a necessity, not a preference (each lint self-scopes to this repo, so global registration is safe). A clean GitHub restore therefore brings back every lint SCRIPT and registers NONE of them: the machine comes up with all 5 lints silently dead. Restore by merging the `hooks` object from `.claude/hooks_user_settings.reference.json` (an inert reference copy kept in the repo for exactly this) into `~/.claude/settings.json`, then correcting every absolute path inside it if the repo or the volume no longer sits where it did. If FURY travelled with the machine, `settings.json` came along —— still correct the paths, then verify.
  - 5.2.8. VERIFY, never assume: Edit `cp/ccsim/sandbox/hook_probe_response_.md` with the Edit/Write tool —— it deliberately carries RED flags, so a live chain BLOCKS the write with a dlint report; a silent success means the hooks are still dead. Piping a payload into a lint by hand proves only that the SCRIPT works, NEVER that the harness invokes it —— that exact gap is how the lints once sat dead for weeks unnoticed. Full rationale: `cp/ccsim/hook_guide.md`.
- 5.3. Keep a short "new-Mac checklist" handy —— this §5.2 IS it.

## 6. Scenario E —— FURY + WSM BOTH lost (true doomsday)
- 6.1. What survives: ONLY the cloud + GitHub —— both repos (code + protocols + comms history), and cloud-side Claude/ChatGPT sessions + memories.
- 6.2. What's permanently lost: all FURY app data not otherwise backed up; all WSM-local wiring, credentials, permissions, CAI local settings; anything committed-but-never-pushed or never-committed.
- 6.3. Rebuild: new Mac + new external drive → clone both repos → follow §5.2 to rebuild the wiring from scratch → sign into Claude/ChatGPT (sessions re-sync) → re-enter credentials from the user's own secure store.
- 6.4. Prevention that makes doomsday survivable: (a) push often (nothing lives only in the working tree); (b) an OFF-SITE backup of FURY + the credential store (the one thing neither git nor cloud holds); (c) periodically export/verify the credential files exist somewhere other than the WSM.

## 7. CAI settings note
- 7.1. CAI SESSIONS + memories = cloud (survive everything except account loss). CAI LOCAL settings (font, scale, dark-mode, window position, pins) live in `config.json` inside the app-data folder —— on FURY after migration, so they follow FURY, and are lost only in Scenario B/E. Re-set them by hand there.
- 7.2. The user's "Active Sessions" list (Settings ▸ Account) is cloud-side (survives all scenarios).

## 8. Standing prevention checklist
- 8.1. Keep an independent backup of FURY (TM-including-FURY or a periodic `ditto` to a 2nd drive) —— the single most important gap.
- 8.2. Never delete the `*.migbak-*` / `*.premigrate-backup-*` copies until a migrated app has run cleanly for a while.
- 8.3. Back up the credential store (`*.local.md`) off the WSM —— git + cloud both intentionally exclude it.
- 8.4. Push both repos regularly.
- 8.5. Re-probe the hooks (§5.2.8) after ANY volume rename, repo move, or machine change —— they fail SILENTLY, so nothing tells you they stopped.
- 8.6. The harness-critical SLICE of FURY is already mirrored in-repo at `backup/backup_Claude/backup_Claude_FURY/` (`settings.json`, both projects' auto-memory, the AJAP Routine) —— tiny, so it rides to GitHub with every push. It does NOT replace §8.1 (it covers a few dozen KB of a 754 GB drive), but it is what makes §5.2.7 a copy rather than a rebuild. Mandate: mirror any change to those live files in the SAME turn —— `cp/ccsim/hook_guide.md` §10, which also carries the drift check.
