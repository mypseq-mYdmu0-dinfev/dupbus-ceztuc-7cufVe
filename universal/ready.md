# Ready —— Session Pre-Conditioning

If user msg contains `#ready`, pre-condition the session by ONLY doing below, so the next turn (likely Opus/Fable) directly takes actions rather than wasting tokens on reading:

1. Read `CLAUDE.md`s & "Unconditionals" (directed files) of ALL working directories
2. No `response_` for this turn (one-off)
3. No chat text except TEA3
4. If msg contains `#ready + [filename(s)]`
- 4.1. Read the additional files after Unconditionals (`find` is allowed)
- 4.2. If any directed readings exist, read them as well
- 4.3. No actions exc. readings; do nothing else
5. FYI: User's actual `query_` in next turn