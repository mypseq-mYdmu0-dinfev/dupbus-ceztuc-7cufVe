# #br —— wrap last turn's outputs for narrow OTG screen

*Trigger: `#br`.*
*ONE-OFF —— acts only on files in the immediately preceding turn; never affects later turns.*

- Targets: the file(s) CC just created/edited in the immediately preceding turn (the `➡️` files, chiefly `response_`) —— OR, if the user names specific file(s) in the `#br` prompt, those instead.
- Wrap deterministically via the script, NEVER by hand-composing the wrapped text (costs zero generation tokens, always matches the spec): `python3 cscpt/br.py file1 [file2 ...]` —— for each target, writes a `temp_`-prefixed sibling copy in the SAME folder (e.g. `temp_response_[TS].md`), word-wrapped to ≤33 characters/line (breaks only at spaces, never mid-word; hard-break only a single token longer than 33).
- Why wrap: on `/remote-control`, OTGD reader doesn't wrap (lines run off-screen, needing L/R scroll).
- Display each `temp_` file via a plain Bash `cat` (e.g. `cat "[temp_path]"`), NEVER the `Read` tool —— `Read` prepends a `cat -n`-style line-number gutter that contaminates the OTG view (confirmed via screenshot). A Bash `cat` avoids that gutter overhead entirely; note it does NOT eliminate the write-then-display round-trip itself (content still re-enters context once to be shown) —— the saving vs `Read` is the gutter tax only, not the whole display cost.
- `temp_` = disposable (§8.3.2); remind user to delete if still exists when `#close`.