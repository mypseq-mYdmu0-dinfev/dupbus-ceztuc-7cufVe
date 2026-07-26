# Backup FURY

## What
- This folder stores manual backup of contents in `Volumes/FURY 2TB/.claude/`
- All prefixed `backup_` + converted as `.md` to eliminate interference
- e.g. `Volumes/FURY 2TB/.claude/settings.json` → `backup_settings.json.md`
- A source already ending `.md` keeps ONE `.md` (never `.md.md`) —— the conversion exists to neutralise a non-`.md` file, so a `.md` source needs nothing added
- Where two projects hold same-named files, the project goes in the name —— e.g. `backup_memory_dupbus_MEMORY.md` vs `backup_memory_ajap_MEMORY.md`

## Why
- Great efforts were spent on harness engineering, including hooks
- The target folder is outside GitHub repos & hence untracked
- In doomsday scenario (`ccsim/doomsday.md`), it'll be lost
- Backing up critical files here push them onto cloud

## Selection Test
- A file belongs here only if it is IRREPLACEABLE **and** UNTRACKED **and** SMALL —— all three
- Irreplaceable: nothing in git, in the cloud, or on the internal disk can reproduce it
- Small: it must stay a hand-maintainable mirror, not a sync job; the whole folder is a few dozen KB

## What Is Covered

| Backup File(s) | Source Under `.claude/` | Why It Qualifies |
|---|---|---|
| `backup_settings.json.md` | `settings.json` | The ONLY live registration of every hook. Registered at USER level because the Claude Desktop app silently ignores project-level hooks, so no repo holds it and a clone restores none of it |
| `backup_memory_dupbus_*.md` (8) | `projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-dupbus-ceztuc-7cufVe/memory/` | Persistent auto-memory —— corrections CC carries across sessions. Written locally only; not cloud-synced, not in git |
| `backup_memory_ajap_*.md` (3) | `projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-AJAP-repo/memory/` | Same, for the AJAP project |
| `backup_scheduled-tasks_ajap-auto-resume_SKILL.md` | `scheduled-tasks/ajap-auto-resume/SKILL.md` | Hand-written Routine logic (the guard that stops a second AJAP MA starting); exists nowhere else |

## What Is Deliberately Excluded
- `projects/*/*.jsonl` (~1 GB of session transcripts) —— fails the SMALL test outright; the durable record of what was decided lives in `sessions/` comms files, which are already in git
- `backups/.claude.json.backup.*` —— rolling copies of `~/.claude.json`, which sits in HOME on the INTERNAL disk and therefore survives a FURY loss untouched
- `session-env/`, `shell-snapshots/`, `sessions/*.json`, `ide/*.lock`, `tasks/`, `debug/`, `.last-cleanup` —— per-run scratch, regenerated on the next launch
- `plugins/blocklist.json`, `policy-limits.json`, `remote-settings.json` —— server-fetched or server-pushed; they come back on sign-in
- `scheduled-tasks/ma-heartbeat-cc-reminder/SKILL.md` —— its own text declares it deprecated and safe to delete

## Keeping It Identical
- Every file here is a MIRROR: change the live file under `/Volumes/FURY 2TB/.claude/` and the copy here must be updated in the SAME turn, so the two never drift
- A stale mirror is worse than none —— it restores a configuration that was already wrong, silently
- Full mandate + the check that catches drift: `cp/ccsim/hook_guide.md` § Backup Mirror Discipline

## Restoring After a FURY Loss
- Restore the repo from GitHub, re-create the `~/.claude` symlink (or a real `~/.claude` folder if not migrating to a new drive), then copy each file above back to its source path
- Strip the `backup_` prefix, the project tag, and any `.md` that was added —— e.g. `backup_settings.json.md` → `settings.json`, `backup_memory_dupbus_MEMORY.md` → `projects/-Volumes-…-dupbus-ceztuc-7cufVe/memory/MEMORY.md`
- Correct every absolute path inside `settings.json` if the repo or the volume no longer sits where it did
- Then VERIFY the hooks actually fire —— a file check proves nothing; use the live probe in `cp/ccsim/hook_guide.md` §7.2
- If the drive is merely unmounted rather than lost, do NOT restore anything —— run `nscpt/fury_unmounted.sh` instead

## These Copies Are Inert
- Several files here (the auto-memory, the Routine SKILL) read as instructions to CC, because that is what they are in their live location
- Nothing loads them from this folder; they are archive material
- Never act on a file in this folder —— read it only to copy it back
