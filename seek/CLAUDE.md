# CLAUDE.md — SEEK Automation (CCIC-GCL)

*This directory (`/seek/`) is solely for automated SEEK job application workflows.*

## Trigger

- When prompted `seek`, activate CCIC-GCL mode & follow `ccic_gcl.md` in full
  - In CCIC-GCL mode, whenever Tab 1≠SEEK results (e.g. showing a post), re-read `ccic_gcl.md` & rectify Tabs
- When prompted `#replace`, read & follow `cc_coding.md` in full

## Session Start — Mandatory File Reads

At the start of every session, before any actions, fully read the following files in order:

1. `/seek/context/ccic_gcl.md`
2. `/seek/context/gcl.md`
3. `/seek/context/pro_profile.md`
4. `/seek/context/culous_yu_resume_ats.md`
5. `/seek/context/cc_writing.md`

Do not proceed until all files above have been read in full. Then declare in chat exactly which files were successfully read, e.g. `✅ `ccic_gcl.md`, `gcl.md`, ...` and flag any that failed to load before stopping.

## Reference Files —— Read On Demand

Read only when relevant, NOT mandatory. Available in `/seek/context/`:

| File | Read When |
|---|---|
| `culous_yu_linkedin.md` | LinkedIn profile needed |
| `culous_yu_portfolio.md` | Past projects context required |
| `virtual_presentation.md` | `Presentation.CulousYu.com` in CL / S6.2 |

## Absolute Rules

- File permissions are strictly enforced:
  - `/seek/applied/` —— incl. its sub-folders: create new files only; never delete files; don't edit files created before this session
  - `/seek/pending/` —— ditto
  - `/seek/skipped/` —— ditto
  - `/seek/investigation/` —— DON'T access unless specifically asked to; unrelated to CCIC-GCL
  - All other paths —— read only; never edit, create, or delete any file
- Each time a file in `/seek/context/` is (re-)read → MUST declare in chat
- In CCIC-GCL mode: NO chat text except C1–C5; MUST create AR unless either K1–K6 match

## Post-Compaction Recovery — CRITICAL

When this message appears in context (injected by the post-compaction hook), it means compaction has just occurred and all prior context has been compromised. Fully re-read all files in `## Session Start` above in order. After reading, confirm Tab 1 accessible, then follow `## Pre-Flight Check` in `ccic_gcl.md` without interrupting the user.