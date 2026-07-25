# Response to ccsim_query_202607252305.md
*Auto-purge disabled; 90-day sweep wired into CCSIM*

## 50. Your Reading —— Correct, With One Correction
- 50.1. Yes, auto-purge was live. But it is 30 days since LAST ACTIVITY (mtime), not since creation —— so an old session you still touch never expires, whilst a dormant one does.
- 50.2. That distinction matters for your Reader session: reverting keeps touching it, so it was probably never actually at risk. The rule you asked for protects it explicitly anyway.
- 50.3. It only ever deleted TRANSCRIPTS —— never `memory/`. So the 8 memory files were never on that clock.

## 51. Disabled —— Confirmed
- 51.1. Set `cleanupPeriodDays: 36500` (100 years) in `~/.claude/settings.json`. Verified: valid JSON, value reads back correctly.
- 51.2. Why not a literal "off": the setting has no disable value —— its floor is 1 day, and a large number is the documented way to mean "keep indefinitely". So this IS the off switch.
- 51.3. Trade-off, stated plainly: nothing self-cleans now. That directory only grows —— which is exactly why you asked for the sweep, and why I wired it rather than leaving it to memory.

## 52. Sweep Wired —— `cp/ccsim/CLAUDE.md` §2.6
- 52.1. Runs at EVERY CCSIM session start, alongside the existing close-index and SSD-health checks.
- 52.2. Flags a dir only when BOTH hold: newest activity ≥90 days old AND the project is no longer in use.
- 52.3. PROPOSE only —— never delete without your approval. Sizes included so you can judge at a glance.
- 52.4. `-Volumes-FURY-2TB-Fury-Documents-GitHub` is permanently EXEMPT, with your reason recorded (Reader session, kept alive by reverting, so age is meaningless for it).
- 52.5. I added a guard you did not ask for and should know about: before proposing ANY dir, check its `memory/`. A populated one holds auto-memory nothing in the repo can restore —— excluded from proposals regardless of age. Say the word if you want that relaxed.

## 53. Note
- 53.1. Your 413MB from §48 is still pending —— unaffected by this change, still yours to run.
