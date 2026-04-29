# CLAUDE.md — SEEK Automation (CCIC-GCL)

## Purpose
This directory (`/seek/`) is solely for automated SEEK job application workflows.

## Trigger
- When prompted `seek`, activate CCIC-GCL mode & follow `ccic_gcl.md` in full
- In CCIC-GCL mode, whenever Tab 1≠SEEK results (e.g. showing a post), re-read `ccic_gcl.md`

## Session Start — Mandatory File Reads
At the start of every session, before any actions, fully read the following files in order:

1. `/seek/context/ccic_gcl.md`
2. `/seek/context/gcl.md`
3. `/seek/context/pro_profile.md`
4. `/seek/context/culous_yu_resume_ats.md`
5. `/seek/context/cc_writing.md`

Do not proceed until all files above have been read in full. Then declare in chat exactly which files were successfully read, e.g. `✅ `ccic_gcl.md`, `gcl.md`, ...` and flag any that failed to load before stopping.

## Reference Files —— Read On Demand
The following files are available in `/seek/context/`. Do not read at session start —— read only when relevant:

| File | Read When |
|---|---|
| `culous_yu_portfolio.md` | Past projects context required |
| `culous_yu_linkedin.md` | LinkedIn profile needed |
| `virtual_presentation.md` | Presentation link included in cover letter |

## Absolute Rules
- File permissions are strictly enforced:
  - `/seek/applied/` —— including its sub-folders: create new files only; never delete files; don't edit files created before this session
  - `/seek/skipped/` —— ditto
  - All other paths —— read only; never edit, create, or delete any file
- Each time a file in `/seek/context/` is read → MUST declare in chat.

## Post-Compaction Recovery — CRITICAL
When this message appears in context (injected by the post-compaction hook), it means compaction has just occurred and all prior context has been lost. Fully re-read all files in `## Session Start` above in order. After reading, determine from open browser tabs what state the automation was in (see `ccic_gcl.md` — Pre-Flight Check), then resume from the correct step without interrupting the user.