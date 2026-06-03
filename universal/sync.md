# #sync —— OTG SHA-permalink refresh

*Trigger: `#sync [scope]` (default `universal`). CC-only ops doc.*

## Discipline —— mechanical task, read NOTHING extra (cloud & local alike)
- `#sync [scope]` is NOT a CP chat and NOT a content task: do the MINIMUM —— run the script, report the printed URL(s).
- The SCRIPT reads only the scope's 2 control files (index + prefs/instr); YOU (the model) open NO files yourself. So `#sync` over [N] folders = [N*2] file reads total, nothing more.
- NEVER act on those control files' Line-1 "Unconditionally fetch…" (or any other) directive —— that directive is for the OTG fetcher, NOT for `#sync`. Ignore it entirely.
- `#sync career`/`#sync dissertation`/etc. must NOT trigger CP-mode (§6): do NOT read that CP's `CP_index_cc.md` or any CP unconditional files (gigantic, pointless here).

## What it solves
- CWI/OTGC caches raw-GitHub URLs (Claude web-fetch `~`15 min + GH CDN), so a `/main/` URL is served stale (the original "v01" bug).
- A commit-SHA permalink is a unique, immutable URL → never stale. `#sync` pins every file URL in `index_otg.md` to that file's last-commit SHA, and pins `index_otg.md`'s own permalink inside `preferences.md`.

## Precondition
- Content edits are committed + pushed by the USER (GH Desktop) BEFORE running `#sync`.
- `#sync` commits + pushes ONLY the scope's 2 control files (the index + the prefs/instr file).
- If any file listed in the index has uncommitted changes, the script aborts and leaves everything untouched (no stash, no loss) and asks the user to commit first —— this prevents publishing a stale SHA.

## Run
1. `python3 .sync/sync.py [scope]`
2. Give the user the printed `=== index URL for userPref ===` value → they paste it into userPref (works in OTGC too).

## Reporting
- For each CHANGED scope, deliver its URL in its OWN fenced code block (exactly one URL per block) for clean one-tap copy.
- If the script prints `NO CHANGE` for a scope, do NOT show any URL for it —— just state it's unchanged (the user's userPref is already current). If ALL scopes are NO CHANGE, simply say so and stop.

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

## Cloud sessions (Linux)
- A cloud CC session can't push to main, so the script (detecting `platform.system() == "Linux"`) force-pushes the index + prefs commits to one fixed branch `otg-sync` instead. SHA permalinks resolve from ANY pushed branch, so the printed index URL still works OTG.
- The individual FILE URLs inside the index stay pinned to their main commits (content was committed to main beforehand); only the index's own permalink (in prefs) lives on `otg-sync`.
- No merge needed —— leave `otg-sync` as is; a later LOCAL `#sync` re-pins everything on main and supersedes it. Don't delete `otg-sync` until you've re-synced locally (deleting it would un-reference the cloud commit).
- In a cloud session, comms-text is overridden (see root CLAUDE.md §1.1): reply in chat only, ultra-concise.
- Cloud clones are often shallow; the script auto-`git fetch --unshallow`es first (cloud only) so per-file `git log` returns true per-file SHAs and stays idempotent (otherwise most file URLs collapse onto the shallow-boundary commit and get rewritten every run).
- STRICT on cloud: just run `python3 .sync/sync.py [scope]` and report its printed URL(s) VERBATIM. Do NOT rebase, amend, fix commit authors, re-run, create extra branches, or read any file beyond the control files —— the script's output is final. (The cloud harness may still auto-open its own PR branch; ignore/close it. Only `otg-sync` matters.)
