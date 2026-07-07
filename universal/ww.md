# #ww —— Word-Wrapping

*Trigger: `#ww`.*
*ONE-OFF —— acts only on files in the immediately preceding turn; never affects later turns.*

- Objective: display last turn's outputs cleanly on OTGD
- Targets: the file(s) CC just created/edited in the immediately preceding turn (chiefly `response_`) —— OR, if the user names specific file(s) in the `#ww` prompt, those instead
- Display each target via a plain Bash `cat` (e.g. `cat "[path]"`), NEVER the `Read` tool
- Why this works: on `/remote-control`, the app's Bash-tool Output panel soft-wraps prose text to fit the phone screen automatically