# #sync —— OTG SHA-permalink refresh

*Trigger: `#sync [scope]` (default `universal`). CC-only ops doc.*

## What it solves
- CWI/OTGC caches raw-GitHub URLs (Claude web-fetch `~`15 min + GH CDN), so a `/main/` URL is served stale (the original "v01" bug).
- A commit-SHA permalink is a unique, immutable URL → never stale. `#sync` pins every file URL in `index_otg.md` to that file's last-commit SHA, and pins `index_otg.md`'s own permalink inside `preferences.md`.

## Precondition (Option B)
- Content edits are committed + pushed by the USER (GH Desktop) BEFORE running `#sync`.
- `#sync` commits + pushes ONLY the scope's `index_otg.md` + `preferences.md`.
- If any in-scope file has uncommitted changes, the script aborts and asks the user to commit first (prevents publishing a stale SHA).

## Run
1. `python3 .sync/sync.py [scope]`
2. Hand the printed `=== paste into userPref ===` block to the user → they paste into userPref (works in OTGC too).

## Guarantees
- Per-file SHA: only files whose content actually changed get a new URL → minimal edits, minimal tokens.
- Reads git history only —— never opens, edits, or `touch`es any file's content/mtime.
- Auto-push restricted to the 2 control files by three independent layers:
  - 3.1. permission rule auto-approves ONLY `python3 .sync/sync.py` (general `git push`/`commit` stay gated);
  - 3.2. the script stages only those 2 paths (never `git add -A`);
  - 3.3. `.githooks/pre-commit` rejects any other path whilst the `.git/SYNC_ACTIVE` marker is set (active only when you've run `git config core.hooksPath .githooks`).

## Scopes
- `universal` → `universal/index_otg.md` + `universal/preferences.md`.
- Add CPs to `SCOPES` in `.sync/sync.py`. For `career`, list `seek/context/*` deps inside `career/index_otg.md` (no `otg/` folder, no `seek/` contamination).
