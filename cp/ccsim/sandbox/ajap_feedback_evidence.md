# Evidence Pack —— the Two Claims AJAP Could Not Verify

<!-- dlint: skip —— verbatim binary extracts and command outputs; not prose -->

*Every command runs on this Mac as-is. `$B` = the Desktop build both sides already
agreed on:*
`~/Library/Application Support/Claude/claude-code/2.1.221/claude.app/Contents/MacOS/claude`

## 1. "No `hook_started`/`hook_progress` Transcript Record" —— CONFIRMED

The gate, from the binary (reproduce: `grep -aob '"hook_started"' "$B"` → first hit
242715029, then `dd` a window around it):

    function Jvo(e){if(lL_.includes(e))return!0;return RWu&&JB.includes(e)}
    function Xvo(e,t,r){if(!Jvo(r))return;Sv({type:"system",subtype:"hook_started",...})}
    lL_=["SessionStart","Setup"]

Every `hook_started`/`hook_progress`/`hook_response` emitter checks `Jvo(event)` first.
Default allowlist = `SessionStart` and `Setup` alone. `RWu` widens it only under
`--remote`/`CLAUDE_CODE_REMOTE` (`kWu(!0)`, offset 259568243). `PreCompact` and
`PostCompact` sit outside the gate —— they can never emit those records on this Mac.

Empirical cross-check over every transcript dir here (incl. ~4,700 AJAP files):

    grep -rlE '"subtype":"hook_(started|progress)"' /Users/culous/.claude/projects/<dir>/
    # → 0 matching files, in every project dir

## 2. "70 Days Dead" —— CONFIRMED as a Total, With an Honest Split

    cd <default repo> && git log --follow --format='%h %ad %s' \
      --date=format:'%Y-%m-%d' -- .claude/post_compact.sh
    # 3cf26df5 2026-08-07  root-caused and rebuilt
    # 8b3da0ad 2026-07-25  hooks live in CAI: user-level registration + repo-scope guards
    # 348b39c4 2026-05-29  first landed (renamed in from a same-morning draft)

Registration trail:

    git show 348b39c4:.claude/settings.json
    # → "PostCompact": [ { "type": "command", "command": ".../post_compact.sh" } ]
    git show 8b3da0ad:.claude/settings.json
    # → hooks: {} —— project-level entry REMOVED 25/07
    git show 6cfafe37:.claude/hooks_user_settings.reference.json
    # → PostCompact present at USER level from 2026-07-25 23:30 onwards

Arithmetic: 29/05→25/07 = 57 days registered project-level, which the Desktop app does
not execute —— never fired there. 25/07→07/08 = 13 days registered user-level, so
presumably firing, but on a user-only channel and (per §1 above) leaving no transcript
trace either. 57 + 13 = 70.

Verdict: "70 days dead" is CORRECT as first-landed→root-cause, reading "dead" as "never
once corrected the model". The strictly-never-executed span is the 57-day half.

Caveat, so the figure is not oversold: any pre-25/07 session run through the CLI (which
does read project-level hooks) could have fired it invisibly —— no log existed to say.
