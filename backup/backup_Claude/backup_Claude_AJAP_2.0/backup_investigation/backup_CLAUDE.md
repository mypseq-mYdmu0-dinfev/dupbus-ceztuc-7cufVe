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

- Read anything in `/seek/` as needed but NEVER delete
  - DON'T follow programmatically (they're for AJAP) but review/analyse
- For edits, unless explicitly told to execute, create `changes_[TS].md` for approval first
- If necessary, read pervious `close_` `changes_` files in `/investigation/`
  - If insufficient or if I explicitly instruct, read other files

## Files Naming

In addition to root CLAUDE.md §3.3:
- `audit_[current_TS].md` = audit report; creation triggered by #audit
- `changes_[current_TS].md` = #replace changes w/ optional explainers (read `coding.md` first)
- `rchat_[copy_TS].txt` = copied chat history of an AJAP session; stored in `/runtime/` (NOT in this folder); copy_TS = time of copying, not session end. (Legacy `session_*` and `runtime_chat_*` names retired in favour of `rchat_`.)
- Runtime logs are named `rlog_[session_start_TS].md` (legacy `runtime_*` retired) and live in `/runtime/`