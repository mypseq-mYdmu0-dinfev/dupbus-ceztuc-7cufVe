# AJAP Investigation CP

## Purpose

This CP ("AJAP Investigation") is for optimising AJAP (Agentic Job Application Programme).

## Absolute Protocols

- Root CLAUDE.md governs: (re-)read `dupbus-ceztuc-7cufVe/CLAUDE.md` in full
- Ignore "If working directory is `/seek/`, skip all sections below"
- All protocols apply EXCEPT:
  - Comms files are in `/investigation/[YYYY]/[YYYYMM]`, NOT `/sessions/`
  - Don't add `[CP_folder]_` prefix; all comms files herein are in this CP
- Re root CLAUDE.md §3.2.1.5, `audit_` `changes_` are also considered comms files in this CP
- Ensure no chat text per root CLAUDE.md §3

## Context

- When prompted `
- Read anything in `/seek/` (incl. `investigation/`) as needed but NEVER delete
  - DON'T follow programmatically (they're for AJAP) but review/analyse
- For edits, unless explicitly told to execute, create `changes_[TS].md` for approval first
- Actively read the concerned session's `rlog_`
- If necessary, read pervious `close_` `audit_` `changes_` files in `/investigation/`
  - If insufficient or if I explicitly instruct, read other files

## Files Naming

In addition to root CLAUDE.md §3.3:
- `audit_[current_TS].md` = audit report; creation triggered by #audit
- `changes_[current_TS].md` = #replace w/ optional explainers (read `replace.md` first)
- `rlog_[session_start_TS].md` = runtime logs; live in `seek/runtime/`
- `rchat_[copy_TS].txt` = copied chat history of an AJAP session; stored in `/runtime/` (NOT in this folder); copy_TS = time of copying, not session end; live in `seek/runtime/`