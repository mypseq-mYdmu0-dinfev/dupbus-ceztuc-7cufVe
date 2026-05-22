# CLAUDE.md

*This directory (`/seek/`) is solely for automated SEEK job application workflows.*

## Trigger

- When prompted `seek`, activate AJAP mode & follow `ajap.md` in full
  - In AJAP mode, whenever Tab 1≠SEEK results (e.g. showing a post), re-read `ajap.md` & rectify Tabs
- When prompted `#replace`, read & follow `cc_coding.md` in full

## Session Start — Mandatory File Reads

At the start of every session, before any actions, fully read the following files in order:

1. `CLAUDE.md` (all sections)
2. `/seek/context/ajap.md`
3. `/seek/context/gcl.md`
4. `/seek/context/pro_profile.md`
5. `/seek/context/culous_yu_resume_ats.md`
6. `/seek/context/cc_writing.md`
7. `/seek/context/cc_reminder.md`

Do not proceed until all files above have been read in full. Then declare in chat exactly which files were successfully read, e.g. `✅ `ajap.md`, `gcl.md`, ...` and flag any that failed to load before stopping.

## Reference Files — Read On Demand

Read only when relevant, NOT mandatory. Available in `/seek/context/`:

| File | Read When |
|---|---|
| `culous_yu_linkedin.md` | LinkedIn profile needed |
| `culous_yu_portfolio.md` | Past projects context required |
| `virtual_presentation.md` | `Presentation.CulousYu.com` in CL / S6.2 |

## Absolute Rules — ⚠️ IMPORTANT

- File permissions are strictly enforced:
  - `/seek/applied/` —— incl. its sub-folders: create new files only; never delete files; don't edit files created before this session
  - `/seek/pending/` —— ditto
  - `/seek/skipped/` —— ditto
  - `/seek/investigation/` —— DON'T access unless specifically asked to; unrelated to AJAP
  - All other paths —— read only; never edit, create, or delete any file
- Each time a file in `/seek/context/` is (re-)read → MUST declare in chat
- In AJAP mode (per ajap.md):
  - Strictly NO chat text except C1–C5
  - MUST create AR unless either K1–K6 match

## Post-Compaction Recovery — 🚨 CRITICAL

🛑 **STOP. DO NOT PROCESS ANY JOB CARD OR TAKE ANY OTHER ACTION UNTIL ALL MANDATORY FILES ARE RE-READ.** The session summary is untrusted paraphrase — it does NOT substitute for source files.

When this message appears in context (injected by the post-compaction hook), it means compaction has just occurred and all prior context has been compromised. You MUST now fully re-read all files in `## Session Start` above in order. After reading, fully follow `## Tab 1 Accessibility Check` in `ajap.md` without interrupting the user.