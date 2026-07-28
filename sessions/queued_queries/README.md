# Queued Queries

## Organisation
If a file in this folder was directly sent in chat, do sequentially:
- Rename as `[CP_folder]_query_[TS].md` (drop the prefix if the addressing session isn't a CP) —— keep the file's OWN 12-digit TS whenever its name already carries one: it dates when the query was written, and stamping the current TS instead would collide with the live turn's own `query_`/`response_` pair. Use `[current_TS]` ONLY when the name carries no TS.
- Move to `sessions/[YYYY]/[YYYYMM]/` (derived from that TS) via the root Move Rule —— copy to the target, then void the original in place; never a bare `mv`, never a delete, so the breadcrumb survives until the user clears it
- Briefly note in chat
- Address it as usual

## FYI
- A `❌_`-prefixed file here is an already-moved original awaiting the user's manual delete —— it is NOT a queued query and does NOT count towards the folder being non-empty below
- If this folder isn't empty (except this file), it probably means either:
  - The user hasn't finished writing them; or
  - The user forgot to send them
- Filenames are temporarily showing unstructured issues/CP names
- Upon finishing writeup, user is supposed to:
  - Rename & move as told above
  - Send to the right session
  - Create Apple Reminder (optional):
    - When to prompt `continue`
    - Which session(s)