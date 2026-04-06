# CLAUDE.md — SEEK Automation (CCIC-GCL)

## Working Directory Purpose
This directory (`/seek/`) is solely for automated SEEK job application workflows. No other tasks are performed here.

## Session Start — Mandatory File Reads
At the start of every session, before responding to any message, read all of the following files in full:

1. `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/ccic_gcl.md`
2. `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/pro_profile.md`
3. `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/gcl.md`
4. `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/writing.md`
5. `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/cc.md`
6. `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/glossary.md`
7. `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/notes.md`

Do not respond until all files above have been read in full.

## Trigger
When the user sends `seek` as their message, activate CCIC-GCL automation mode and follow `ccic_gcl.md` in full.

## Post-Compaction Recovery — CRITICAL
When this message appears in context (injected by the post-compaction hook), it means compaction has just occurred and all prior context has been lost. Execute the following immediately, in order, before any other action:

1. Read `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/ccic_gcl.md` in full
2. Read `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/pro_profile.md` in full
3. Read `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/gcl.md` in full
4. Read `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/writing.md` in full
5. Read `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/cc.md` in full
6. Read `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/glossary.md` in full
7. Read `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/context/notes.md` in full

After reading all files, determine from open browser tabs what state the automation was in (see `ccic_gcl.md` — Pre-Flight Check), then resume from the correct step without interrupting the user.

## Absolute Rule
`Culous_Yu_Resume_Consulting.pdf` must never be selected or submitted under any circumstance in this workflow.
