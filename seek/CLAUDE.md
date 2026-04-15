# CLAUDE.md — SEEK Automation (CCIC-GCL)

## Working Directory Purpose
This directory (`/seek/`) is solely for automated SEEK job application workflows. No other tasks are performed here.

## Session Start — Mandatory File Reads
At the start of every session, before responding to any message, read all of the following files in full:

1. `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/ccic_gcl.md`
2. `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/pro_profile.md`
3. `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/gcl.md`
4. `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/writing.md`

Do not proceed until all files above have been read in full. Then declare in chat exactly which files were successfully read, e.g. `✅ ccic_gcl.md, pro_profile.md, ...` and flag any that failed to load before stopping.

## Reference Files —— Read On Demand
The following files are available in `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/`. Do not read at session start —— read only when relevant:

| File | Read When |
|---|---|
| `Culous_Yu_Resume_Consulting.pdf` in `culous_yu_resume_ats.md` | STRICTLY COMPLETELY DISREGARD; DO NOT USE |
| `Culous_Yu_Resume_Marketing.pdf` in `culous_yu_resume_ats.md` | for marketing/branding/PR/social/content roles |
| `Culous_Yu_Resume_IxD.pdf` in `culous_yu_resume_ats.md` | for UX/UI/service design/product roles |
| `Culous_Yu_Resume_IT.pdf` in `culous_yu_resume_ats.md` | for IT/IS/data analytics/software roles |
| `Culous_Yu_Resume_General.pdf` in `culous_yu_resume_ats.md` | for all other roles |
| `culous_yu_portfolio.md` | Read when employer background or cover letter requires past projects context |
| `culous_yu_linkedin.md` | LinkedIn profile snapshot |
| `virtual_presentation.md` | Read when including presentation link in cover letter |

## Trigger
When the user sends `seek` as their message, activate CCIC-GCL automation mode and follow `ccic_gcl.md` in full.

## Post-Compaction Recovery — CRITICAL
When this message appears in context (injected by the post-compaction hook), it means compaction has just occurred and all prior context has been lost. Execute the following immediately, in order, before any other action:

1. Read `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/ccic_gcl.md` in full
2. Read `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/pro_profile.md` in full
3. Read `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/gcl.md` in full
4. Read `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/writing.md` in full

After reading all files, determine from open browser tabs what state the automation was in (see `ccic_gcl.md` — Pre-Flight Check), then resume from the correct step without interrupting the user.

## Absolute Rules
- `Culous_Yu_Resume_Consulting.pdf` must never be selected or submitted under any circumstance in this workflow.
- File permissions are strictly enforced:
  - `/seek/applied/` —— create new files only; never edit or delete existing files
  - All other paths —— read only; never edit, create, or delete any file