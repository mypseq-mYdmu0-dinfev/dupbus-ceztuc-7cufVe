# #br —— wrap last turn's outputs for narrow OTG screen

*Trigger: `#br`.*
*ONE-OFF —— acts only on files in the immediately preceding turn; never affects later turns.*

- For each file CC just created/edited (the `➡️` files, chiefly `response_`), make a copy in the SAME folder with a `temp_` prefix (e.g. `temp_response_[TS].md`).
- In each copy, WORD-WRAP every line to ≤33 characters: break only at spaces, never mid-word (hard-break only a single token longer than 33). Keep the numbering/bullets; wrapped continuation lines are fine. Restructure into short ≤33-char bullets where it reads better.
- Why: on `/remote-control`, OTGD reader doesn't wrap (lines run off-screen, needing L/R scroll)
- After creating the copies, read each `temp_` file back so it surfaces for OTG viewing.
- `temp_` = disposable (§8.3.2); remind user to delete if still exists when `#close`.