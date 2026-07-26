# Backup FURY

## What
- This folder stores manual backup of contents in `Volumes/FURY 2TB/.claude/`
- All prefixed `backup_` + converted as `.md` to eliminate interference
- e.g. `Volumes/FURY 2TB/.claude/settings.json` → `backup_settings.json.md`

## Why
- Great efforts were spent on harness engineering, including hooks
- The target folder is outside GitHub repos & hence untracked
- In doomsday scenario (`ccsim/doomsday.md`), it'll be lost
- Backing up critical files here push them onto cloud