# SSD-Wear Migration Guide (WSM)
*Standing reference. Goal: cut internal-SSD wear on the WSM (Mac Mini M2 Pro, internal SSD health 94%) by relocating write-heavy home paths to the external SSD `/Volumes/FURY 2TB`. Origin: `ccsim_query_202607060438.md` (Fable audit) → executed across the 202607 CCSIM sessions. Future CC: read this to guide the user without digging old `response_` files.*

---

## 1. Mechanism
- 1.1. Relocation = move the dir to `/Volumes/FURY 2TB/<same-name>` then symlink the original path back to it. The owning app follows the symlink, so its reads/writes physically land on FURY; the internal SSD keeps only a tiny symlink inode.
- 1.2. `npm` is the exception: no symlink —— its cache is repointed by config (`npm config set cache '/Volumes/FURY 2TB/npm-cache'`).
- 1.3. Safe move method (ALWAYS): `ditto` copy → verify file counts match → only then `rm -rf` source → `ln -s`. NEVER cross-volume `mv` (its copy-then-delete can half-finish on a Finder `.DS_Store` regeneration race —— that scare happened once, recovered, 0 data lost).

## 2. Current state (as of 202607242011)
- 2.1. DONE (symlink → FURY): `~/.claude` (WHOLE dir —— user ran the script; transcripts + settings + hooks + future skills), `~/.vscode`, `~/Library/Application Support/Code`, `~/.codex` (guard —— codex respawned but now writes to FURY), `~/.ajap` (AJAP session), `~/Library/Caches/Google` (Chrome cache), `~/Library/Application Support/Google/Chrome/Default` (Chrome profile), `~/Library/Caches/ai.perplexity.macv3` (Perplexity cache), `~/Library/Application Support/TradingView`. `npm` cache repointed. Deletable caches purged (`brew cleanup`, pip).
- 2.2. CAI (`~/Library/Application Support/Claude`, ~12 GB, highest churn) —— NOT yet migrated. The first attempt FAILED (see §7) and was rolled back to internal by `rescue_cai_appdata_202607241900.sh`; CAI runs on internal now. Re-attempt via the HARDENED `sessions/2026/202607/migrate_cai_to_fury_202607242011.sh` (user runs after quitting ALL Claude). Recovery if it ever breaks post-migration: `nscpt/recover_cai_appdata.sh`.
- 2.3. NOT migrated (left local): `~/.mcp` (jobspy —— static node_modules + in-use; AJAP's call, see the AJAP note); Spotify (dir actively shrinks on quit —— its big cache already redirected in-app; low value); Perplexity APP dir (its `perplexityd` LaunchAgent respawns after kill —— can't cleanly quit; only its cache migrated); Signal + Google Drive (user: too fragile, high loss risk); Adobe (aggressive respawn); Raycast (`com.raycast.macos` —— user keeps local, accepts wear); keys (`~/.ssh`), `~/.Trash`, small static dotdirs.
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
  - 5.3.0. QUIESCE FURY FIRST (critical): the backup must be a consistent snapshot, so NOTHING may write to `/Volumes/FURY 2TB` whilst it copies —— not CAI, VS Code, Chrome, and NOT Google Drive (it silently syncs). Two ways: (i) quit every app that reads/writes FURY (all migrated apps + Google Drive via its menubar → Quit, plus `launchctl` the mount-guard off), then run the backup; OR (ii) simplest + safest —— boot into **Safe Mode** (hold ⇧ Shift at boot), which disables login items + third-party daemons so nothing touches FURY, then do the `ditto`/`rsync` backup, then reboot normally. Safe Mode is the recommended guarantee.
  - 5.3.1. (a) Back up: `ditto "/Volumes/FURY 2TB" "/Volumes/<backup-ssd>/FURY 2TB"` (or `rsync -aXE --info=progress2`) —— a metadata-preserving copy (xattrs, ACLs, Finder "Date Added"). Plain `cp` is NOT enough. Include hidden files (`.ajap`, `.claude`, `.vscode`, `.codex`, `.mcp`, etc.).
  - 5.3.2. (b) Reformat FURY → APFS, **case-INSENSITIVE** (matches today's HFS+; case-sensitive would break apps), and name the volume EXACTLY `FURY 2TB`.
  - 5.3.3. (c) Copy back: `ditto "/Volumes/<backup-ssd>/FURY 2TB" "/Volumes/FURY 2TB"`.
  - 5.3.4. Because the volume name (hence `/Volumes/FURY 2TB/...`) is unchanged, all symlinks (`~/.ajap`, `~/.vscode`, `~/.codex`, `~/Library/Application Support/Code`, and the scripted `~/.claude` + CAI) resolve exactly as before. Spotlight will reindex; re-add FURY paths to any backup tool.
- 5.4. Verify after: each symlink still resolves (`readlink` each), apps launch, and Finder "Date Added" survived on a sample.

## 6. Revert (undo any single migration)
- 6.1. Per-item exact revert commands live in the session revert-logs (`ccsim_migration_revertlog_202607241459.md`, `..._202607241642.md`, `..._202607242011.md`). General form: `rm <symlink> && mv '/Volumes/FURY 2TB/<name>' <original path>` (or `ditto` back); for npm: `npm config delete cache`. Live app migrations also keep a `*.migbak-*` / `*.premigrate-backup-*` aside copy for instant rollback.

## 7. THE MIGRATION FAILURE + THE SAFE PATTERN (mandatory reading before any app-dir move)
- 7.1. What happened (24 Jul, CAI): the first script did `rm -rf SRC && ln -s DST SRC`. `ditto` had already copied CAI to FURY, but `rm -rf` FAILED ("Directory not empty") because CAI's `Claude Helper` children were still alive and re-writing the folder. The `&&` then skipped `ln -s` —— so NO symlink was made AND the partial `rm` had already GUTTED ~34,500 of 35,584 files. CAI, still running, rebuilt a blank state → signed out, sessions/pins/settings gone. Data was safe on FURY; the live app was wrecked. The user was severely distressed.
- 7.2. Two root faults: (a) the process guard only did `pgrep -x Claude`, MISSING the `Claude Helper` processes; (b) a long DESTRUCTIVE `rm` ran on the LIVE path with no symlink yet.
- 7.3. THE SAFE PATTERN (use for EVERY live app-dir migration —— never deviate):
  - 7.3.1. Force-quit the app AND all helpers (`pkill -x App`, `pkill -f 'App Helper'`, then `-9`); WAIT; re-check; ABORT if any process survives (some, e.g. Perplexity's `perplexityd` or Adobe, respawn via LaunchAgent —— SKIP those, don't race them).
  - 7.3.2. `lsof +D` the dir right before touching it (TOCTOU guard).
  - 7.3.3. Rename any STALE FURY copy aside first (else `ditto` MERGES and the count-verify won't match live data).
  - 7.3.4. `ditto` SRC → FURY; verify file counts (excl `.DS_Store`) match EXACTLY; abort on mismatch (source intact).
  - 7.3.5. RENAME the source aside atomically (`mv SRC SRC.migbak-TS`) —— NEVER `rm` it. THEN `ln -s`. A failed step can never leave a gutted dir with no link, because the source is preserved and the symlink is created before any delete.
  - 7.3.6. KEEP the aside backup until the app runs cleanly for ~a day; then delete to reclaim space. Rollback = `rm <symlink> && mv <aside> <path>`.
- 7.4. Reference implementation of the safe pattern: `sessions/2026/202607/migrate_cai_to_fury_202607242011.sh` (CAI). (A general per-app migrator, `migrate_apps_to_fury_202607242011.sh`, was run once then voided to `❌_`-prefix —— the pattern itself lives in §7.3, so no live general script is kept.)
- 7.5. Ongoing (not migration-time) residual for CAI-on-FURY: a SURPRISE FURY unmount while CAI runs live can corrupt its SQLite/LevelDB. Mitigations: never unmount FURY with CAI open; CAI sessions are cloud-synced; `nscpt/recover_cai_appdata.sh` re-links + CAI self-heals; the APFS reformat (§5) removes the HFS+ corruption-proneness. This residual is inherent to a live DB on a removable volume —— it is NOT a script bug and cannot be scripted away, only reduced.
