# #sync —— OTG SHA-permalink refresh

*Trigger: `#sync [scope]` (default `universal`). CC-only ops doc.*

## What it solves
- CWI/OTGC caches raw-GitHub URLs (Claude web-fetch `~`15 min + GH CDN), so a `/main/` URL is served stale (the original "v01" bug).
- A commit-SHA permalink is a unique, immutable URL → never stale. `#sync` pins every file URL in `index_otg.md` to that file's last-commit SHA, and pins `index_otg.md`'s own permalink inside `preferences.md`.

## Precondition
- Content edits are committed + pushed by the USER (GH Desktop) BEFORE running `#sync`.
- `#sync` commits + pushes ONLY the scope's 2 control files (the index + the prefs/instr file).
- If any file listed in the index has uncommitted changes, the script aborts and leaves everything untouched (no stash, no loss) and asks the user to commit first —— this prevents publishing a stale SHA.

## Run
1. `python3 .sync/sync.py [scope]`
2. Give the user the printed `=== index URL for userPref ===` value (or the full prefs block) → they paste it into userPref (works in OTGC too).

## Guarantees
- Per-file SHA: only files whose content actually changed get a new URL → minimal edits, minimal tokens.
- MANDATE —— reads the CONTENT of only the 2 control files (the index + prefs/instr). For every file the index lists, it uses git metadata only (`git log`/`git status`), NEVER opening the file. So large listed files cost nothing and are never read.
- Never opens, edits, or `touch`es any content file's body/mtime.
- Auto-push restricted to the scope's 2 control files by three independent layers:
  - permission rule auto-approves ONLY `python3 .sync/sync.py` (general `git push`/`commit` stay gated);
  - the script stages only those 2 paths (never `git add -A`, which would stage the whole repo);
  - `.githooks/pre-commit` rejects any other staged path whilst the `.git/SYNC_ACTIVE` marker is set (active only after the user runs `git config core.hooksPath .githooks`).

## Scopes (no hard-coding)
- No arg → `universal` → `universal/index_otg.md` + `universal/preferences.md`.
- `#sync <cp>` → `<cp>/CP_index_otg.md` + `<cp>/CP_instr.md`.
- The file list is read from the index itself, so a CP index may legitimately list files OUTSIDE its folder (e.g. `seek/context/*`); those get pinned too, with no `otg/` folder and no `seek/` contamination.
