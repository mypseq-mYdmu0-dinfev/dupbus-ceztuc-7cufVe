# Session Closing Protocols

## Preamble

- Triggered by: `#close` | Current_TS: `TZ='Australia/Sydney' date +"%Y%m%d%H%M"`
- Editing `close_` file:
  - Also update end-of-range TS on Line 1 (`# Session Closing...`) w/ [current_TS]
  - NEVER edit TS in filename, so user can track diff
- Sprint Log —— if a `#sprint` ran this session, record its `slog_[TS].md` as a created non-comms file (§ Other Files; or § Coverage for Addendum) for future retrospection if needed.

---

## Non-CC Sessions

If you're not CC, follow below structure with these adaptations:
- Generate in artefact instead (no filename/location needed)
- Skip all TS (timestamp; user manually input)
- §4./AD[XX].4. Session Files lists/counts artefact no. (#) instead
- §5. Other Files lists/counts deliverables/codes generated (ref artefact #; if any)

---

## DevPlan

- If DevPlan.md was declared in chat history OR in `CP_index_*.md`, follow § DevPlan Sessions
- Non-CC: If `CP_index_*.md` not injected by system = no DevPlan
- CC: If `CP_index_*.md` not in one of working directories AND not in context = no DevPlan
- No DevPlan = follow § Non-DevPlan Sessions

---

## Non-DevPlan Sessions

*Close with 1 file*

Filename: `close_[TS].md` (CC: If CP, prefix `[CP_folder]_` like other comms files)
Location: same folder as the session's query_/response_ files

### Non-DevPlan Template

```markdown
# Session Closing ([1st_query_TS]–[current_TS])
*[Heading max 8w]*

## 1. Coverage
- 1.1. [List of issues/tasks addressed; all #numbered (same for all below sections)]
- 1.2. ...
[skip 1 line]

## 2. Decisions
- 2.1. [Key decisions made in this session; include reasoning if non-obvious]
- 2.2. ...
[skip 1 line]

## 3. Issues
- 3.1. [Todos or unresolved items with priority tag: 🔴 blocking / 🟡 important / 🟢 nice-to-have]
- 3.2. ...
[skip 1 line]

## 4. Session Files ([file_count])
- 4.1. `[YYYYMM]/query_[TS].md` —— [max. 8w descr]
- 4.2. `[YYYYMM]/response_[TS].md` —— [ditto]
- 4.3. ... [all `query_`/`response_` pairs (comms files) created this session, in chronological order]
[skip 1 line]

## 5. Other Files ([file_count])
- 5.1. Created:
  - 5.1.1. `enclosing_folder/file.py` [1 line each; same for below]
  - 5.1.2. `enclosing_folder/file.html`
  - 5.1.3. ... [all non-comms files in any format created this session, in chronological order]
- 5.2. Modified:
  - 5.2.1. ... [ditto]
- 5.3. Moved/Voided/Deleted:
  - 5.3.1. ... [ditto]
[If none, input `N/A`]
[skip 1 line]

## 6. Remarks
- 6.1. [What the next session (if applicable) must know immediately; ONLY what is not already captured in above sections; optional]
- 6.2. ...
```

---

## DevPlan Sessions

*Close with 2 files*

1. Handoff
Filename: `[CP_folder]_close_[TS].md`
Location: same folder as the session's query_/response_ files
Usage: to be kept for record & sent at next chat start; MUST be MECE with addendum

2. Addendum
Filename: `[CP_folder]_response_[TS].md` (a distinct response_ file, NOT directly appended to DevPlan.md; user reviews first)
Location: same folder as the session's query_/response_ files
Usage: to be deleted after user appended it to DevPlan (actively read by ALL future sessions)

### Handoff Template

```markdown
# [CP_Name/Alias] Session Closing ([1st_query_TS]–[current_TS])
*Chat [Z]: [Heading max 8w]*

## Status
[Last & next issues; use P[no.]/AD[no.] if applicable; max 20w; all #numbered (same for below)]
[skip 1 line]

## Remarks
[Next-session-only, temporary, but noteworthy; absent from DevPlan/Addenda; optional]
[skip 1 line]

## Session Files ([file_count])
- `[YYYYMM]/[CP_folder]_query_[TS].md` —— [max. 8w descr]
- `[YYYYMM]/[CP_folder]_response_[TS].md` —— [ditto]
[... all `query_`/`response_` pairs created this session, in chronological order]
```

### Addendum Template

```markdown
### AD[XX]. P[Y.Y] (Chat [Z]) —— [Heading max 8w]

*Note: `###` level for appending under `## PART C` of DevPlan.md; XX = last addendum no. + 1 in 2 digits; Y.Y = phase(s) worked on; Z = this chat's number (last +1 unless told otherwise)*

- AD[XX].1. Coverage
  - AD[XX].1.1. [What was accomplished/done; e.g. list of issues/tasks addressed, any non-comms files created/edited/deleted; if none AND 0% DevPlan progress, input N/A]
  - AD[XX].1.2. ...
[skip 1 line]

- AD[XX].2. Decisions
  - AD[XX].2.1. [Key decisions with lasting relevance]
  - AD[XX].2.2. ...
[skip 1 line]

- AD[XX].3. Deviations
  - AD[XX].3.1. [Any drift from DevPlan.md, even if already resolved]
  - AD[XX].3.2. ...
[skip 1 line]

- AD[XX].4. Session Files ([file_count])
  - AD[XX].4.1. `[YYYYMM]/query_[TS].md` —— [max. 8w descr]
  - AD[XX].4.2. `[YYYYMM]/response_[TS].md` —— [ditto]
[... all `query_`/`response_` pairs created this session, in chronological order]
[skip 1 line]

- AD[XX].5. Remarks [replace with more subsections as needed; don't cramp into this]
  - AD[XX].5.1. [What the next session (if applicable) must know immediately (e.g. todos/unresolved issues; ONLY what is not already captured in above sections; optional]
  - AD[XX].5.2. ...
[skip 1 line]
```

### Addendum Rules

- MUST be #numbered & formatted as above:
  - 2nd level (AD[XX].n) uses bullet `- ` (NOT a heading)
  - 3rd level uses sub-bullet `  - `
- No separator `---` within addendum
- MECE (Mutually Exclusive, Collectively Exhaustive):
  - Handoff = only applicable to immediate next chat
  - Addendum = persists for & valuable to all future chats
- Focus on discrepancies and special notes only
- DON'T describe general progress (P[Y.Y] already indicates that)