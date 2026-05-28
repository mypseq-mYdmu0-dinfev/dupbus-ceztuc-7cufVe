# Monthly Wrapping Protocols

*Triggered by: `#wrap` | Current_TS: `TZ='Australia/Sydney' date +"%Y%m%d%H%M"`*

---

*Wrap with 1 file*

Filename: `wrap_[TS].md`
Location: `/sessions/[YYYY]/[YYYYMM]/` —— one per month
Format: all #numbered; reference last month's `wrap_` (if exists)

---

## Template

```markdown
# Monthly Wrap: [YYYYMM]
*[Heading max 15w]*

## Sessions
- `[YYYYMM]/close_[TS].md` —— [max. 15w descr]
- `[YYYYMM]/[CP_folder]_close_[TS].md` —— [ditto]
[... all `close_` files of the month, in chronological order]

## Key Themes
[e.g. Cross-session issues/patterns, user preferences, recurring decisions, ongoing work threads]

## Key Decisions
[Noteworthy decisions made in this month]

## Carried Forward
[Open items from `close_` files not yet resolved; tagged 🔴/🟡/🟢]

## Notable Files
[Non-sessions files created or meaningfully modified this month; enclosing_folder/filename]

## Remarks
[Standing context that next month's sessions should know; ONLY what's not in sections above; optional]
```

---

## Wrap Rules

- Read ALL `close_` files (incl. CP-prefixed) in the target month's folder before writing
- Synthesise —— don't just copy; `wrap_` must be faster to read than all `close_` files combined
- If a `wrap_` already exists for the target month, STOP & alert user