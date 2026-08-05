# Monthly Wrapping Protocols

## Preamble

- Triggered by: `#wrap` | Current_TS: `TZ='Australia/Sydney' date +"%Y%m%d%H%M"`
- Editing `wrap_` file: NEVER edit TS in filename, so user can track diff
- Context gate: `#wrap` reads a whole month of `close_` (heavy); if the user reports the session is >50% context-full, advise running it in a FRESH session first
- Prefix: `wrap_` always stays unprefixed; never `[CP]_wrap_`
- Reminder: if this is a CCSIM session, remember your own CLAUDE.md's §6 (Backlog Sweep)
- `#wrap` session runs DATS at its own `#close`, not during `#wrap`
so a `wrap_` is never left un-DATS'd. (You always #wrap the PRIOR month, so this session's own `close_` belongs to the NEXT #wrap, not this one.)
- `#wrap` session must have its own `#close` (in current month folder; belonging to next `#wrap`)

---

*Wrap with 1 file*

Filename: `wrap_[TS].md`
Location: `/sessions/[YYYY]/[YYYYMM]/` —— one per month
Format: all #numbered; reference last month's `wrap_` (if applicable) to avoid repetition

---

## Template

```markdown
# Monthly Wrap: [YYYYMM]
*[Heading max 15w]*


## 1. Themes
- 1.1. [Key themes only; e.g. cross-session issues/patterns, user preferences, recurring decisions, ongoing work threads; all #numbered (same for all below sections)]
- 1.2. ...
[skip 1 line]

## 2. Decisions
- 2.1. [Key decisions made in this month; include reasoning if non-obvious]
- 2.2. ...
[skip 1 line]

## 3. Issues
- 3.1. [Todos or unresolved items with priority tag: 🔴 blocking / 🟡 important / 🟢 nice-to-have]
- 3.2. ...
[skip 1 line]


## 4. Sessions ([close_file_count])
- 4.1. `[YYYYMM]/close_[TS].md` —— [max. 15w descr]
- 4.2. `[YYYYMM]/[CP_folder]_close_[TS].md` —— [ditto]
- 4.3. ... [all `close_` files of the month, in chronological order]
[skip 1 line]

## 5. Notable Files ([file_count]) [only meaningful/major]
- 5.1. Created:
  - 5.1.1. `enclosing_folder/file.py` [1 line each; same for below]
  - 5.1.2. `enclosing_folder/file.html`
  - 5.1.3. ...
- 5.2. Modified:
  - 5.2.1. ...
[If none, input `N/A`]
[skip 1 line]

## 6. Remarks
- 6.1. [Standing context that next month's sessions should know; ONLY what's not in sections above; optional]
- 6.2. ...
```

---

## Wrap Rules

- #sprint with fullest FOF; start w/ Sonnet, then escalate to Opus if needed
- #SA read ALL `close_` files (incl. CP-prefixed) in the target month's folder
  - DON'T miss any, even if TS ≠ target month
  - i.e. Encompassing all sessions STARTED in target month (per root c.md §3.4.5)
- You or SAs may individually consider escalating to read non-`close_` comms files if valuable
- Synthesise —— don't just copy; `wrap_` must be easier to read than all `close_` files combined
- If a `wrap_` already exists for the target month, STOP & alert user