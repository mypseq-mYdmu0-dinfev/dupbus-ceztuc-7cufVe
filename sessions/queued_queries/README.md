# Queued Queries

## Organisation
If a file in this folder was directly sent in chat, do sequentially:
- Rename as `[CP_folder]_query_[TS].md` (drop the prefix if the addressing session isn't a CP) —— keep the file's OWN 12-digit TS whenever its name already carries one:
  - It dates when the query was written for record keeping
  - Stamping the current TS instead would collide with the live turn's own `query_`/`response_`
  - Exception: Use `[current_TS]` ONLY when the filename carries no TS
- Move to `sessions/[YYYY]/[YYYYMM]/` (current month, NOT the TS' month) per root Move Rule
- Briefly note you've followed these in `response_`
- Address it as usual
- Ensure the file AND this README.md join the batch as usual per root CLAUDE.md §3.2.1

## FYI
- A `❌_`-prefixed file here is an already-moved original awaiting the user's manual delete
- Filenames might be temporarily showing unstructured issues/CP names