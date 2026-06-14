# PSL (Process Single Loop)

*Read prompt-matching section; e.g. on `psl`, read § `psl`.*

## Shared Rules
- If creating new AR, do in `/gcl/applied/` (Outcome: Applying) as usual
- If NOT creating (AR complete; nothing to improve), move (per Move Rule) from current directory (e.g. `/pending/`) to `/applied/` → edit as `Outcome: Applying`
- For both creating/editing: DON'T prefix `⏳_` (unclickable) but `PSL_` instead → declare `➡️`
- Before starting next AR, remind user (in chat) to delete any copies voided in this session
- `apply` = finish the loop (S6); STOP right before "Submit", "Submit application", or similar
- `done` = edit as `Outcome: Applied`; remove `⏳_` from filename; proceed to next AR
- `next` = don't touch current AR; proceed to next AR
- `parallel AJAP` = an AJAP session is running in parallel —— minimise disturbance by:
  - Except for "batch verify URLs..." below, avoid file changes in `/seek/` (notice if unavoidable)
  - For both creating/editing: duplicate to `dupbus-ceztuc-7cufVe/temp/temp_seek/` → remark at top where it was from (e.g. "Dup From: `gcl/pending/`") → execute the intended creation/editing → if moving is needed: DON'T; instead remark where it should go (e.g. "Go To: `gcl/applied/`") right below "Dup From"
  - This overrides other directory-related instructions (e.g. "create AR in `/ccl/`")

## `psl`

- Enter AJAP mode but process ONE single loop only, stopping at S5 completion
- A5's "SEEK results" become "any application"
- DON'T spawn SA1 (run solo), skip any (ignore Save & Skip/K1–6), or interact w/ job page (opened by user) except screenshot/scrolling as needed; stop to ask anything if necessary
- Skip A1; at A6 (waited 3 cycles), alert then STOP; DON'T proceed to Qi

## `psl [AR_filename(s)]`

- Perform `psl` on the AR(s) (sequentially if multiple)
- Read the file(s) (stop if not found) but never edit them
- If it's complete (w/ P.S. line), re-validate (S3/S4) then create new AR(s) (S5) if results differ
- If it's incomplete, create new AR(s)
- For each, open its URL like ajap.md's Tab 2 for reading, since there's no Tab 1 (single loop)

## `psl pending`

- Perform `psl [AR_filename(s)]` on `/gcl/pending/` ARs starting from oldest
- Right before reading the full file, bash extract its SEEK URL → open it
- If 404/closed/expired, use SAs to batch verify URLs of all pending ARs (w/o fully reading ARs) → void all unavailable ARs (no "Apply" button) → concisely tell amount of voided & remained
- Otherwise (still available) or when done (told amount in chat), proceed (from oldest available)

## `ccl`

- Read `/context/ccl.md`
- Perform `psl`
- Instead of `/gcl/applied/`, create AR in `/ccl/`
- Reference ARs in `/ccl/` & `/ccl/ccl_archive/` for quality & style; adapt to current firm