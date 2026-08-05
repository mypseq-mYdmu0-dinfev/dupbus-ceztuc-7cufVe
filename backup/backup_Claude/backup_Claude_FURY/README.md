# Backup FURY

*Overrides `backup/README.md`'s no-edit rule.*

## What
- This folder mirrors the handful of irreplaceable files in `/Volumes/FURY 2TB/.claude/` —— the folder `~/.claude` is a symlink to, and which no repo tracks
- It re-checks and repairs itself at every CCSIM session start, and again the moment CCSIM edits a live file (both triggers: see § Session-Start Check), rather than relying on anyone remembering to update it
- Every mirrored copy carries a `backup_` prefix and ends in `.md`, so nothing in the harness can ever load or act on one by accident

### Naming Rule (exact, and the only rule there is)
- Take the source path relative to `.claude/`, prefix `backup_`, and append `.md` unless the source already ends `.md` —— never `.md.md`, because the extension exists only to neutralise a non-`.md` file
- e.g. `/Volumes/FURY 2TB/.claude/settings.json` → `backup_settings.json.md`
- Where two projects hold same-named files, the project tag goes in the name —— e.g. `backup_memory_dupbus_MEMORY.md` vs `backup_memory_ajap_MEMORY.md`
- The enumerated, machine-readable form of this mapping is the `MAP` block at the top of `mirror.sh`, which is what the check actually reads —— it is the single source of truth, so add an entry THERE first and let the table below follow

### The Three Files Here That Are NOT Backups
- `README.md` —— this file
- `mirror.sh` —— the check/repair tool (§ Session-Start Check)
- `mirror_test.sh` —— its regression test; runs entirely on temp fixtures and never touches the real `.claude` folder

## Why
- Great efforts were spent on harness engineering, including hooks
- The target folder is outside GitHub repos & hence untracked
- In a doomsday scenario (`cp/ccsim/doomsday.md`), it'll be lost
- Backing up critical files here pushes them onto the cloud with every repo push

## Selection Test
- A file belongs here only if it is IRREPLACEABLE **and** UNTRACKED **and** SMALL —— all three
- Irreplaceable: nothing in git, in the cloud, or on the internal disk can reproduce it
- Small: it must stay a hand-maintainable mirror, not a sync job; the whole folder is a few dozen KB

## What Is Covered

| Backup File(s) | Source Under `.claude/` | Why It Qualifies |
|---|---|---|
| `backup_settings.json.md` | `settings.json` | The ONLY live registration of every hook. Registered at USER level because the Claude Desktop app silently ignores project-level hooks, so no repo holds it and a clone restores none of it |
| `backup_memory_dupbus_*.md` (10) | `projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-dupbus-ceztuc-7cufVe/memory/` | Persistent auto-memory —— corrections CC carries across sessions. Written locally only; not cloud-synced, not in git |
| `backup_memory_ajap_*.md` (3) | `projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-AJAP-repo/memory/` | Same, for the AJAP project |
| `backup_scheduled-tasks_ajap-auto-resume_SKILL.md` | `scheduled-tasks/ajap-auto-resume/SKILL.md` | Hand-written Routine logic (the guard that stops a second AJAP MA starting); exists nowhere else |

## What Is Deliberately Excluded
- `projects/*/*.jsonl` (~1 GB of session transcripts) —— fails the SMALL test outright; the durable record of what was decided lives in `sessions/` comms files, which are already in git
- `backups/.claude.json.backup.*` —— rolling copies of `~/.claude.json`, which sits in HOME on the INTERNAL disk and therefore survives a FURY loss untouched
- `session-env/`, `shell-snapshots/`, `sessions/*.json`, `ide/*.lock`, `tasks/`, `debug/`, `.last-cleanup` —— per-run scratch, regenerated on the next launch
- `plugins/blocklist.json`, `policy-limits.json`, `remote-settings.json` —— server-fetched or server-pushed; they come back on sign-in
- `scheduled-tasks/ma-heartbeat-cc-reminder/SKILL.md` —— its own text declares it deprecated and safe to delete
- ANY credential, token, or key —— excluded on a rule that OVERRIDES the selection test even when a file is irreplaceable, untracked, and small. This folder is pushed to GitHub; a secret mirrored here is a secret published. macOS keeps CC's credentials in the Keychain, so none is present today —— if one ever appears under `.claude/`, it stays out, permanently
- The bulk exclusions above are one judgement, stated once: transcripts, caches, scratch, and server-pushed files are all REGENERABLE. Losing them costs nothing that a fresh sign-in or the next launch does not rebuild, and mirroring them would turn a hand-checkable folder into a sync job nobody audits

*Coverage was re-audited against the live tree when this check was built: the four sources in the table above are the complete set that passes the test. `mirror.sh` re-runs that audit every time it runs —— it walks every `projects/*/memory/` and `scheduled-tasks/*/SKILL.md` and reports anything it finds that this README does not list.*

## Session-Start Check

*Every file here is a MIRROR of a live file. A stale mirror is worse than none —— it restores a configuration that was already wrong, and the restore looks like it succeeded. So the snapshot is not trusted; it is re-verified.*

- AT EVERY CCSIM SESSION START, run this one command. It diffs every mirrored pair and overwrites any backup that no longer matches its live file:

```bash
"/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/backup/backup_Claude/backup_Claude_FURY/mirror.sh" sync
```

- ALSO RE-MIRROR ON THE SPOT whenever CCSIM itself EDITS a file under `.claude/` —— same command, same turn as the edit. No diff sweep is needed to locate the drift: the agent that made the edit already knows which file it touched (`mirror.sh` has no per-file mode and needs none —— `sync` is idempotent and cheap)
- The two triggers are complementary, not redundant: the targeted one covers CCSIM's OWN edits at the instant they happen; the session-start sweep still catches whatever anyone or anything ELSE changed
- To inspect without changing anything (same report, no writes), drop the argument:

```bash
"/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/backup/backup_Claude/backup_Claude_FURY/mirror.sh"
```

- OVERWRITING IS CORRECT AND INTENDED —— this folder is tracked by git, so every prior version of a backup stays recoverable from repo history. The live file is always the truth; the copy here is always the follower. There is nothing to lose by re-mirroring and everything to lose by hesitating
- Read the result by its exit code, not by squinting at the lines:
  - `0` —— every pair identical, nothing to do
  - `1` —— drift found (check mode only; `sync` repairs it and returns `0`)
  - `2` —— a human decision is needed, and the offending line says which: `UNMIRRORED` (a live file nothing backs up), `ORPHAN` (a backup whose source is unknown), `MISSING` (a mapped source deleted upstream). Resolve it by editing the `MAP` or `EXCLUDE` block in `mirror.sh` and this README —— never by guessing a filename
- `UNMIRRORED` is the important one: `mirror.sh` DISCOVERS the live memory folders rather than trusting a fixed list, so a brand-new auto-memory file, or a whole new project's `memory/`, is flagged the first time the check runs after it appears
- After changing `mirror.sh`, run `./mirror_test.sh` —— temp fixtures only, exit 0 means the checker still catches drift

## The Accepted Risk (stated plainly, not buried)
- The sweep runs at SESSION START. A live file changed MID-session by anything OTHER than CCSIM is therefore unprotected until the next one (CCSIM's own edits are already covered by the same-turn trigger)
- If FURY dies inside that window, that one change is lost —— everything mirrored at the last session start survives
- Per-turn mirroring was considered and REJECTED: it would spend tokens on every turn of every session to close a window measured in minutes, for files that change a few times a month. Disproportionate
- The residual risk is narrowed, not eliminated, by the same-turn re-mirror trigger (§ Session-Start Check) —— which is precisely why that trigger exists. The session-start run is the safety net, not the only line of defence
- The honest summary: this design accepts losing at most one session's worth of change to a rarely-changed file, in exchange for a check cheap enough that it actually gets run

## Restoring After a Total Loss

*The order matters: the repo comes back from GitHub FIRST, because these backups live inside it. Until the clone exists there is nothing to restore FROM.*

1. Clone the repo from GitHub to its new location
2. Re-create `~/.claude` —— a symlink to the replacement drive, or a real folder if not migrating to one
3. Generate the exact copy commands, review them, then paste them into a fresh terminal:

```bash
"/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/backup/backup_Claude/backup_Claude_FURY/mirror.sh" restore-plan
```

   - This PRINTS a `mkdir -p` + `cp` pair per file and writes nothing itself, so it is safe to run just to look
   - It reverses the naming rule for you —— stripping the `backup_` prefix, the project tag, and any added `.md` —— which is the step most likely to be fumbled by hand
   - If the repo or the volume no longer sits where it did, edit the printed paths before pasting; the plan is built from this machine's paths, not the new one's
4. Correct every absolute path INSIDE the restored `settings.json` —— hook registrations are absolute, so a relocated repo leaves every hook pointing at nothing
5. VERIFY the hooks actually fire. A file-exists check proves nothing: use the live probe in `cp/ccsim/hook_guide.md` §7.2, where a blocked edit is the acceptance criterion
6. Run `mirror.sh` (no argument) —— a clean `exit 0` confirms the restored live tree now matches the snapshot

- IF THE DRIVE IS MERELY UNMOUNTED rather than lost, do NOT restore anything on top of an intact drive —— run `nscpt/fury_unmounted.sh` instead

## These Copies Are Inert
- Several `backup_*` files here (the auto-memory, the Routine SKILL) read as instructions to CC, because that is exactly what they are in their live location
- Nothing loads them from this folder; they are archive material
- Never act on a `backup_*` file in this folder —— read one only to copy it back
- EXPLICIT CARVE-OUT, so the two rules do not contradict each other: `mirror.sh` and `mirror_test.sh` are tooling, not backups. They carry no `backup_` prefix and are MEANT to be executed. The inertness rule applies to the mirrored copies alone
