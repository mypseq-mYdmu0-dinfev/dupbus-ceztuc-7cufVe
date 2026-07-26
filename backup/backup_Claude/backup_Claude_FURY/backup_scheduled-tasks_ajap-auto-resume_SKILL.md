---
name: ajap-auto-resume
description: AJAP auto-resume after session limit (guard-and-resume; PAUSED until user activates)
---

AJAP auto-resume guard. You run as your OWN new session; the user is not present. GOAL: only restart AJAP if the prior AJAP session has DIED (e.g. hit its 5-hour limit). NEVER start a second AJAP while one is alive (that would create two MAs driving one Chrome).

Steps:
1. Read `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/.claude/tmp/ma_state.md`. Find `latest_TS` (format YYYYMMDDHHmm, Australia/Sydney).
2. Compute minutes since `latest_TS`: `echo $(( ( $(TZ='Australia/Sydney' date +%s) - $(TZ='Australia/Sydney' date -j -f "%Y%m%d%H%M" "<latest_TS>" +%s) ) / 60 ))`.
3. ALSO check for any AR file modified in the last 20 min: `find "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/gcl" -type f -mmin -20 2>/dev/null | head -1`.
4. If `latest_TS` is within 20 minutes OR a recent AR was found → an AJAP session is ALIVE → DO NOTHING. Output "AJAP active — no resume" and STOP.
5. If `latest_TS` is older than 20 minutes AND no recent AR AND `ma_msg.md` is absent/stale → the prior AJAP likely died → resume: read `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/CLAUDE.md` and perform the `seek` trigger as MA (full Session Start). 
6. On ANY uncertainty, default to NO action (safer to skip one hour than to spawn a conflicting session).

LIMITATION (known): you cannot inject a message into an existing interactive AJAP window — you can only resume a dead session as a fresh MA. The user monitors via /remote-control.