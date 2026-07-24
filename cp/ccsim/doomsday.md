# Doomsday & Resilience Playbook (WSM)
*What to do when hardware fails. Much of the WSM setup is HIGHLY LOCAL —— it does NOT travel by just cloning the repos to another Mac. This file is the recovery map for each failure. Read the relevant § when it happens; start a CCSIM session and tell CC which scenario. Companion: `cp/ccsim/ssd_migration_guide.md`.*

---

## 1. What is portable vs WSM-local (read this first)
- 1.1. PORTABLE (survives losing the Mac): the two git repos on GitHub (`dupbus-ceztuc-7cufVe`, `AJAP_repo`); cloud-synced Claude/ChatGPT sessions + memories (account-side); anything committed + pushed.
- 1.2. ON FURY (lost if FURY dies, unless backed up): all migrated app data —— CAI (`~/Library/Application Support/Claude`), VS Code state (`~/Library/Application Support/Code`), Chrome profile + caches, TradingView, Perplexity cache, `~/.claude` (CC transcripts), `~/.vscode`, `~/.codex`, `~/.mcp`(local), npm cache, `~/.ajap`.
- 1.3. WSM-LOCAL, NOT in git or cloud (must be RE-CREATED on a new Mac): the symlinks themselves (`~/.claude`, `~/.vscode`, `~/.codex`, `~/Library/.../Code`, `~/Library/.../Claude` → FURY); the LaunchAgents (`com.culous.fury-guard`, `com.culous.cc-tmpdir`) + their `~/bin` scripts; `npm config` cache path; `git config core.hooksPath`; macOS Automation/permissions grants; Finder "Date Added" metadata; credentials (`.claude/cic_login.local.md`, `seek/.claude/ajap_login.local.md` —— git-ignored by design); CAI's local settings (fonts/pins —— sessions are cloud, these local prefs are not).
- 1.4. RULE OF THUMB: git has the CODE + PROTOCOLS; cloud has the SESSIONS; FURY has the APP DATA; the WSM has the WIRING. A new Mac needs the wiring rebuilt by hand (re-run this session's setup scripts + re-grant permissions).

## 2. Scenario A —— FURY unmounted whilst CAI open, or CAI opened whilst FURY unmounted
- 2.1. Symptom: CAI blank/signed-out, or a stray real `~/Library/Application Support/Claude` folder appears (should be a symlink).
- 2.2. Fix: `⌘Q` CAI → in a plain Terminal run `nscpt/recover_cai_appdata.sh` → follow its output. It force-quits CAI, SCANS the FURY databases for corruption, re-links the path to FURY, and renames any stray internal folder aside (never deletes).
- 2.3. If it reports SQLite corruption (only a surprise-unmount-mid-write can cause it —— your UPS + FURY's rarity make this very unlikely): the script tells you exactly whether/how to Time Machine restore (only the CAI folder). SQLite/LevelDB also self-heal a half-written tail on next launch, and sessions are cloud-synced —— worst case you lose only the last unsynced action. (This is the peace-of-mind answer to your §50.2.)
- 2.4. The mount-guard (`nscpt/setup_fury_guard.sh`, installed) pops a critical alert whenever FURY is missing —— heed it: touch nothing but Disk Utility until FURY is back.

## 3. Scenario B —— FURY LOST (no access to FURY data; WSM + internal data intact) *[HIGHLY LIKELY, ~1 year out]*
- 3.1. Context: you plan to replace FURY (2TB PCIe 4.0) with a larger drive (e.g. FURY 4TB PCIe 5.0), so this WILL happen —— not soon, but treat it as expected.
- 3.2. What's gone: everything on FURY (§1.2) —— CAI data, VS Code state, Chrome profile, `~/.claude` transcripts, etc. The symlinks now dangle.
- 3.3. What survives: the git repos (GitHub); cloud CAI/ChatGPT sessions; and any INTERNAL backups still present (`*.migbak-*`, `*.premigrate-backup-*` —— only if you hadn't deleted them). Time Machine helps ONLY for paths that were on the internal disk or if you'd added FURY to TM (external volumes are excluded by default).
- 3.4. Recovery onto a NEW drive: name the new volume EXACTLY `FURY 2TB` (then every symlink resolves unchanged), OR rename it and re-point the symlinks. Then either restore the FURY backup (if you made one) or re-run the migrations fresh from whatever internal copies remain + let CAI re-sync sessions from cloud. Re-clone both repos from GitHub if needed.
- 3.5. LESSON for prevention: keep an independent FURY backup (Time Machine that INCLUDES FURY, or a periodic `ditto` to a second drive) —— once you delete the `*.migbak`/`*.premigrate` copies, FURY becomes the SOLE copy of that app data.

## 4. Scenario C —— FURY being REPLACED (you still have BOTH WSM + current FURY data)
- 4.1. The clean path (you control the timing): follow `ssd_migration_guide.md` §5.3.0 —— QUIESCE FURY (Safe Mode boot, or quit every FURY-writer incl. Google Drive), then `ditto`/`rsync` a metadata-preserving copy of all of `/Volumes/FURY 2TB` to the new drive.
- 4.2. Name the new drive EXACTLY `FURY 2TB` → all symlinks + LaunchAgents resolve with zero changes. (If you rename it, update every symlink target + the two LaunchAgent scripts.)
- 4.3. This is also your chance to switch FURY to APFS (removes the HFS+ corruption-proneness) —— see `ssd_migration_guide.md` §5.
- 4.4. Verify after: each symlink resolves (`readlink`), apps launch, Finder "Date Added" survived on a sample.

## 5. Scenario D —— WSM being REPLACED (you still have BOTH WSM + FURY data)
- 5.1. Move FURY to the new Mac (its app data comes with it). Clone both repos from GitHub.
- 5.2. RE-CREATE the WSM-local wiring (§1.3) —— this is the part cloning does NOT do:
  - 5.2.1. Re-create the symlinks: `~/.claude`, `~/.vscode`, `~/.codex`, `~/.mcp`(if migrated), `~/Library/Application Support/Code`, `~/Library/Application Support/Claude` → their FURY targets. (`~/.ajap` too.)
  - 5.2.2. Re-run the setup scripts: `setup_fury_guard.sh`, `setup_cc_tmpdir_202607241642.sh`.
  - 5.2.3. `npm config set cache '/Volumes/FURY 2TB/npm-cache'`; `git config core.hooksPath .githooks` (per repo).
  - 5.2.4. Re-supply credentials (`.claude/cic_login.local.md` etc. —— they're git-ignored, so copy them from your own secure store).
  - 5.2.5. Re-grant macOS permissions (Automation for the usage/keystroke scripts, Full Disk if needed).
  - 5.2.6. CAI: sign in → sessions re-sync from cloud; re-set local prefs (fonts/pins) —— those are local, not cloud.
- 5.3. Keep a short "new-Mac checklist" handy —— this §5.2 IS it.

## 6. Scenario E —— FURY + WSM BOTH lost (true doomsday)
- 6.1. What survives: ONLY the cloud + GitHub —— both repos (code + protocols + comms history), and cloud-side Claude/ChatGPT sessions + memories.
- 6.2. What's permanently lost: all FURY app data not otherwise backed up; all WSM-local wiring, credentials, permissions, CAI local settings; anything committed-but-never-pushed or never-committed.
- 6.3. Rebuild: new Mac + new external drive → clone both repos → follow §5.2 to rebuild the wiring from scratch → sign into Claude/ChatGPT (sessions re-sync) → re-enter credentials from your own secure store.
- 6.4. Prevention that makes doomsday survivable: (a) push often (nothing lives only in the working tree); (b) an OFF-SITE backup of FURY + the credential store (the one thing neither git nor cloud holds); (c) periodically export/verify the credential files exist somewhere other than the WSM.

## 7. CAI settings note
- 7.1. CAI SESSIONS + memories = cloud (survive everything except account loss). CAI LOCAL settings (font, scale, dark-mode, window position, pins) live in `config.json` inside the app-data folder —— on FURY after migration, so they follow FURY, and are lost only in Scenario B/E. Re-set them by hand there. Your "Active Sessions" list (Settings ▸ Account) is cloud-side.

## 8. Standing prevention checklist
- 8.1. Keep an independent backup of FURY (TM-including-FURY or a periodic `ditto` to a 2nd drive) —— the single most important gap.
- 8.2. Never delete the `*.migbak-*` / `*.premigrate-backup-*` copies until a migrated app has run cleanly for a while.
- 8.3. Back up the credential store (`*.local.md`) off the WSM —— git + cloud both intentionally exclude it.
- 8.4. Push both repos regularly.
