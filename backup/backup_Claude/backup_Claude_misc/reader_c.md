# OTG Reader Instruction

## Purpose
- All sessions started from this directory ALONE has one sole job —— `#ww` files sent by user
- If your working directory is NOT ONLY `GitHub/`, entirely disregard this file

## Operations
- At session start (once per session, unless compacted), read `GitHub/dupbus-ceztuc-7cufVe/universal/ww.md` to learn how to `#ww`
- When user sends `*_[TS].md` (TS = 12-digit Timestamp in `YYYYMMDDHHmm`):
  - DON'T use `find`
  - Extract `YYYYMM` from the TS & construct the path `[YYYY]/[YYYYMM]/`
  - Locate file in either `dupbus-ceztuc-7cufVe/sessions/` OR `AJAP_repo/inv/` (both in `GitHub/`)
  - e.g. `response_202607092157.md` in `dupbus-ceztuc-7cufVe/sessions/2026/202607/`
  - Once found, `#ww` it
- When user sends a filename w/o TS, `find` it across `GitHub/`
- If user's msg only has a single `.` (1 char; no other text):
  - Respond w/ a `.` only in chat
  - No other chat text or any other actions

## Limitation
- DON'T directly read any files except `ww.md` (only `cat` it as instructed)
- DON'T emit ANY chat text NO MATTER WHAT
- DON'T create/edit/move/delete any files