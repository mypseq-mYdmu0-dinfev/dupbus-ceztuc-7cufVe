# Monthly Wrapping Protocols

## Preamble

- Triggered by: `#wrap` | Current_TS: `TZ='Australia/Sydney' date +"%Y%m%d%H%M"`
- Editing `wrap_` file: NEVER edit TS in filename, so user can track diff
- Context gate —— `#wrap` reads a whole month of `close_` (heavy). If the user reports the session is >50% context-full, advise running it in a FRESH session first (`cp/ccsim/CLAUDE.md` §6.2). `#wrap` is a CCSIM job; `wrap_` stays unprefixed.
- After creating & declaring the file, run `gscpt/DATS.py`
  - If `✅ Fixed [no.] file(s) ...`, simply tell in chat (override; exact): "DATS done. Fixed [no.] file(s)."
  - If any other results (e.g. `👀 [no.] file(s) ...`), stop (don't input `yes`) & concisely tell user.

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

## Issues
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

## CCSIM Backlog Sweep (do BEFORE writing the `wrap_`, so it's reflected in it)

- Surface `cp/ccsim/backlog.md`'s OPEN items (those without a `→ ✅ RESOLVED` line).
- Scan the month's `close_` for EMERGENT cross-session patterns worth a CCSIM fix that no single `close_` already logged; append any new one to `backlog.md` (format: `cp/ccsim/CLAUDE.md` §3). Per-session items are already self-registered by each `close_` (close.md), so hunt PATTERNS, not un-logged flags.
- For EACH open item, PROPOSE a concrete solution + rough effort —— this monthly sweep is what keeps the backlog from growing unbounded.
- Do NOT fix at wrap time (context cost); instead tee up a dedicated CCSIM session to action the proposals.
- Record the sweep in the `wrap_` § Issues: the open count + your proposals, referencing `backlog.md` (don't re-list its entries).

---

## Wrap Rules

- Read ALL `close_` files (incl. CP-prefixed) in the target month's folder
  - DON'T miss any, even if TS ≠ target month
  - i.e. Encompassing all sessions STARTED in target month (per root c.md §3.4.5)
- Synthesise —— don't just copy; `wrap_` must be easier to read than all `close_` files combined
- If a `wrap_` already exists for the target month, STOP & alert user