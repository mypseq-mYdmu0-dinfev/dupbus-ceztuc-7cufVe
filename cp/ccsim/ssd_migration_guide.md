# SSD-Wear Migration Guide (WSM)
*Standing reference. Goal: cut internal-SSD wear on the WSM (Mac Mini M2 Pro, internal SSD health 94%) by relocating write-heavy home paths to the external SSD `/Volumes/FURY 2TB`. Origin: `ccsim_query_202607060438.md` (Fable audit) → executed across the 202607 CCSIM sessions. Future CC: read this to guide the user without digging old `response_` files.*

---

## 1. Mechanism
- 1.1. Relocation = move the dir to `/Volumes/FURY 2TB/<same-name>` then symlink the original path back to it. The owning app follows the symlink, so its reads/writes physically land on FURY; the internal SSD keeps only a tiny symlink inode.
- 1.2. `npm` is the exception: no symlink —— its cache is repointed by config (`npm config set cache '/Volumes/FURY 2TB/npm-cache'`).
- 1.3. Safe move method (ALWAYS): `ditto` copy → verify file counts match → only then `rm -rf` source → `ln -s`. NEVER cross-volume `mv` (its copy-then-delete can half-finish on a Finder `.DS_Store` regeneration race —— that scare happened once, recovered, 0 data lost).

## 2. Current state (as of 202607241642)
- 2.1. DONE by CC (symlink → FURY): `~/.vscode`, `~/Library/Application Support/Code`, `~/.codex` (guard: was deleted by user; symlink pre-created so any future write lands on FURY), `~/.ajap` (done earlier by the AJAP Fable session). `npm` cache repointed.
- 2.2. SCRIPTED for the user to run after quitting ALL Claude (`sessions/2026/202607/migrate_to_fury_202607241642.sh`): `~/.claude` (whole dir —— transcripts + settings + hooks + future skills) and `~/Library/Application Support/Claude` (CAI desktop app, ~13 GB, ~10 writes/min).
- 2.3. NOT migrated: `~/.mcp` (jobspy) —— it is static `node_modules` (0 churn; jobspy's runtime writes go elsewhere, not here), and it was in use (MCP server running); space-only 117 MB win, not worth it. `~/.config/raycast` + `~/Library/Application Support/com.raycast.macos` —— KEPT LOCAL by user choice (Raycast replaced Spotlight; user accepts its wear). Keys (`~/.ssh`), `~/.Trash`, small static dotdirs —— stay local.
- 2.4. `~/.claude.json` (auth token) lives in HOME, NOT inside `~/.claude` —— never moved (stays on internal, off the noowners volume).

## 3. Mount-race — the ONE hazard, and recovery
- 3.1. FURY hosts the whole GitHub repo already, so an unmounted FURY breaks everything regardless —— migrating adds no NEW practical risk. The single new failure mode: launching an app that uses a migrated path BEFORE FURY is mounted.
- 3.2. If that happens, the symlink dangles and the app may create a fresh REAL dir at that path on the internal SSD (split-brain: new local data shadows the FURY copy).
- 3.3. GOOD NEWS (verified 202607241642): none of the migrated-path apps auto-fire at boot —— VS Code and the Claude apps are NOT in Login Items, and no LaunchAgent/Daemon writes to a migrated path. So the race only occurs if the user MANUALLY opens such an app before FURY mounts. The user's own discipline (check Disk Utility → only use the WSM once FURY is mounted) fully covers it.
- 3.4. Recovery if a stray real dir appears (e.g. `~/.claude` shows as a real folder, not a symlink `-> /Volumes/FURY 2TB/...`):
  - 3.4.1. Quit the app. Mount FURY.
  - 3.4.2. If the stray local dir has NEW data you care about (e.g. a session written while unmounted), copy it into the FURY copy first: `ditto ~/.claude /Volumes/FURY\ 2TB/.claude` (review first).
  - 3.4.3. Remove the stray + recreate the symlink: `rm -rf ~/.claude && ln -s '/Volumes/FURY 2TB/.claude' ~/.claude`.
  - 3.4.4. It does NOT auto-heal —— the symlink must be recreated by hand (or re-run the migrate script, which detects the symlink and skips if already correct).
- 3.5. Optional hardening (not built): a login LaunchDaemon that blocks until FURY is mounted before anything touches the symlinked paths. Offered; deferred as unnecessary given §3.3.

## 4. SQLite-corruption note
- 4.1. HFS+ (current FURY format) is more prone to SQLite corruption on a SURPRISE unmount than APFS. This only bites if FURY unmounts MID-write. Since the user never works until FURY is mounted and doesn't unmount mid-session, the practical risk is low. Resolved fully by the APFS reformat (§5).

## 5. STANDING PENDING TASK — reformat FURY to APFS (target: December 2026)
- 5.1. Why: HFS+ `noowners` can't enforce POSIX perms (some apps demand it) and is slower + more corruption-prone than APFS. The user plans this but it needs a full back-up + wipe (~754 GB, a multi-day job), so it waits until AFTER the MBA dissertation (due November 2026) —— expected **December 2026**.
- 5.2. Goal: everything snaps back in place afterwards with zero re-linking, because every symlink points at `/Volumes/FURY 2TB/...` and that mount path is preserved.
- 5.3. Procedure (the a/b/c):
  - 5.3.1. (a) Back up: `ditto "/Volumes/FURY 2TB" "/Volumes/<backup-ssd>/FURY 2TB"` (or `rsync -aXE --info=progress2`) —— a metadata-preserving copy (xattrs, ACLs, Finder "Date Added"). Plain `cp` is NOT enough. Include hidden files (`.ajap`, `.claude`, `.vscode`, `.codex`, `.mcp`, etc.).
  - 5.3.2. (b) Reformat FURY → APFS, **case-INSENSITIVE** (matches today's HFS+; case-sensitive would break apps), and name the volume EXACTLY `FURY 2TB`.
  - 5.3.3. (c) Copy back: `ditto "/Volumes/<backup-ssd>/FURY 2TB" "/Volumes/FURY 2TB"`.
  - 5.3.4. Because the volume name (hence `/Volumes/FURY 2TB/...`) is unchanged, all symlinks (`~/.ajap`, `~/.vscode`, `~/.codex`, `~/Library/Application Support/Code`, and the scripted `~/.claude` + CAI) resolve exactly as before. Spotlight will reindex; re-add FURY paths to any backup tool.
- 5.4. Verify after: each symlink still resolves (`readlink` each), apps launch, and Finder "Date Added" survived on a sample.

## 6. Revert (undo any single migration)
- 6.1. Per-item exact revert commands live in the session revert-logs (`ccsim_migration_revertlog_202607241459.md`, `..._202607241642.md`). General form: `rm <symlink> && mv '/Volumes/FURY 2TB/<name>' <original path>` (or `ditto` back); for npm: `npm config delete cache`.
