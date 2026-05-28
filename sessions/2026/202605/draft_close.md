# Session Closing Protocols (Destination: `universal/close.md`)

*Triggered by: `#close` | Current_TS: `TZ='Australia/Sydney' date +"%Y%m%d%H%M"`*

---

## Non-CP Sessions

*Close with 1 file*

Filename: `close_[TS].md`
Location: same folder as the session's query_/response_ files

### Non-CP Template

```markdown
# Session Closing ([1st_query_TS]–[current_TS])
*[Heading max 8w]*

## What Was Covered
[List of topics/tasks addressed; all #numbered (same for below)]

## Key Decisions
[Decisions made; include reasoning if non-obvious]

## Unresolved / Todos
[Items with priority tag: 🔴 blocking / 🟡 important / 🟢 nice-to-have]

## Session Files
- `[YYYYMM]/query_[TS].md` —— [max. 8w descr]
- `[YYYYMM]/response_[TS].md` —— [ditto]
[... all `query_`/`response_` pairs created this session, in chronological order]

## Other Files
- Created: `enclosing_folder/file.py`, `enclosing_folder/file.html`, ...
- Modified: ...
- Moved/Voided/Deleted: ...

## Remarks
[What the next session (if applicable) must know immediately; ONLY what is not already captured in the sections above; optional]
```

---

## CP Sessions

*Close with 2 files*

1. Handoff
Filename: `[CP_folder]_close_[TS].md`
Location: same folder as the session's query_/response_ files
Usage: to be kept & sent at next chat start; MUST be MECE with addendum

2. Addendum
Filename: `[CP_folder]_response_[TS].md` (a distinct response_ file, NOT appended to DevPlan.md; user reviews before appending)
Location: same folder as the session's query_/response_ files
Usage: to be deleted after user manually reviewed & appended to DevPlan (for all CP sessions)

### CP Handoff Template

```markdown
# [CP_Name/Alias] Session Closing ([1st_query_TS]–[current_TS])
*Chat [Z]: [Heading max 8w]*

## Status
[Last & next issues; use P[no.]/AD[no.] if applicable; max 20w; all #numbered (same for below)]

## Remarks
[Next-session-only, temporary, but noteworthy; absent from DevPlan/Addenda; optional]

## Session Files
- `[YYYYMM]/[CP_folder]_query_[TS].md` —— [max. 8w descr]
- `[YYYYMM]/[CP_folder]_response_[TS].md` —— [ditto]
[... all `query_`/`response_` pairs created this session, in chronological order]
```

### CP Addendum Template

```markdown
### AD[XX]. P[Y.Y] (Chat [Z]) —— [Heading max 8w]

*Note: `###` level for appending under `## PART C` of DevPlan.md; XX = last addendum no. + 1 in 2 digits; Y.Y = phase(s) worked on; Z = this chat's number (last +1 unless told otherwise)*

- AD[XX].1. What Was Done
  - AD[XX].1.1. [e.g. Any non-`/sessions/` files created/edited/deleted; if none AND 0% DevPlan progress, input N/A]
  - AD[XX].1.2. ...
[skip 1 line]

- AD[XX].2. Key Decisions Made
  - AD[XX].2.1. [Decisions with lasting relevance]
  - AD[XX].2.2. ...
[skip 1 line]

- AD[XX].3. Deviation from Dev Plan
  - AD[XX].3.1. [Any drift from DevPlan.md, even if already resolved]
  - AD[XX].3.2. ...
[skip 1 line]

[Add more subsections as needed; don't cramp in a single `AD[XX].4. Notes` subsection]
```

### CP Addendum Rules

- MUST be #numbered & formatted as above:
  - 2nd level (AD[XX].n) uses bullet `- ` (NOT a heading)
  - 3rd level uses sub-bullet `  - `
- No separator `---` within addendum
- MECE (Mutually Exclusive, Collectively Exhaustive):
  - Handoff = only applicable to immediate next chat
  - Addendum = persists for & valuable to all future chats
- Focus on discrepancies and special notes only
- DON'T describe general progress (P[Y.Y] already indicates that)