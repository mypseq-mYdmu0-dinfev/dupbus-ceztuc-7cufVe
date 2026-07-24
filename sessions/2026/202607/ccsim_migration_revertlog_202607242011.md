# CC Migration Revert-Log (202607242011)
*CC-facing. Continues `..._202607241642.md`. This turn's LIVE migrations used the SAFE rename-aside pattern (never rm-before-symlink); all reversible. See `cp/ccsim/ssd_migration_guide.md` §7.*

---

## C1 — Chrome cache → FURY  [DONE, live]
- `~/Library/Caches/Google` → symlink → `/Volumes/FURY 2TB/Library/Caches/Google` (14079 files verified). Cache backup auto-removed (regenerable). Chrome was force-quit + verified (0 procs).
- REVERT: `rm "$HOME/Library/Caches/Google" && ditto "/Volumes/FURY 2TB/Library/Caches/Google" "$HOME/Library/Caches/Google" && rm -rf "/Volumes/FURY 2TB/Library/Caches/Google"`

## C2 — Chrome profile → FURY  [DONE, live, backup kept]
- `~/Library/Application Support/Google/Chrome/Default` → symlink → FURY (11679 verified). Backup: `…/Default.migbak-202607242021`.
- REVERT: `rm "<Default symlink>" && mv "…/Default.migbak-202607242021" "<Default path>"`

## C3 — Perplexity cache → FURY  [DONE, live]
- `~/Library/Caches/ai.perplexity.macv3` → symlink → FURY (1442 verified). Cache backup auto-removed.
- CAVEAT: Perplexity's `perplexityd` LaunchAgent respawns + is a login agent → mount-race risk (could make a stray local cache pre-mount). Low harm (cache regenerates). REVERT like C1.

## C4 — TradingView → FURY  [DONE, live, backup kept]
- `~/Library/Application Support/TradingView` → symlink → FURY (9278 verified). Backup: `…/TradingView.migbak-202607242021`.
- REVERT: `rm "<TV symlink>" && mv "…/TradingView.migbak-202607242021" "<TV path>"`

## C5 — Spotify  [NOT migrated]
- Skipped: count mismatch (src 137 / a stale partial FURY copy 378 —— its dir shrinks on quit as it prunes cache). My stale FURY copy was removed; internal Spotify intact (144 files). Low value (big cache already redirected in-app by user). Leave local.

## C6 — Safe live deletes
- `brew cleanup -s` (freed ~449M); `pip3 cache purge` (empty). No revert needed (regenerable).

## C7 — Scripts created/updated this turn (user runs the migrations)
- `sessions/2026/202607/migrate_cai_to_fury_202607242011.sh` —— hardened CAI migration (force-quit-all-helpers, stale-copy-aside, rename-aside, symlink; keeps backups). Rollback line printed by the script.
- `sessions/2026/202607/migrate_apps_to_fury_202607242011.sh` —— general per-app safe migrator (already run for C1–C4; Perplexity-app/Spotify self-skipped).
- `nscpt/recover_cai_appdata.sh` —— permanent post-migration recovery (re-link to FURY after a bad launch/unmount; never deletes).
- `setup_cc_tmpdir_202607241642.sh` —— annotated with how-to-run (unchanged behaviour).

## C8 — Preserved backups (do NOT delete until confirmed)
- `~/Library/Application Support/Claude.broken-backup-202607241939` (from the rescue) + the FURY CAI copy —— keep until CAI migration re-done + verified.
- `*.migbak-202607242021` (Chrome profile, TradingView) —— keep until those apps verified on FURY.