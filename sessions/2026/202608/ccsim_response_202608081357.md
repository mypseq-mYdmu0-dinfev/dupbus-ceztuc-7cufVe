# Response to ccsim_query_202608081357.md
*The tally fired on this very prompt —— proof, not a claim*

## 197. re 193.7 & 193.5 —— BUILT, and It Just Caught Me

- 197.1. Direct answer: **yes, built.** You #r §193.7 correctly —— a measured latency is not something an unbuilt thing can have.
- 197.2. My §181.5 said "not tonight". The sprint that followed built it anyway, and §193.7.1 recorded that. Two statements a few sections apart said opposite things about the same object, and that is on me for not striking the earlier one.
- 197.3. ⭐ And you have already seen it work without knowing: **the message you just sent carried the tally.** It opened with `Chat-discipline tally: the PREVIOUS turn ended with 2 impermissible chat lines —— clint class prose`.
- 197.4. Its own log line for that firing: `tally=fired:prose:2@6ac4a4cabd4b`. That is the whole loop —— clint detects at Stop, hlint injects at the next prompt, and the model sees it before acting.
- 197.5. It also matched the standing prediction at §193.7.8 exactly: class `prose`, from the last clint entry. Predicted before, confirmed after.
- 197.6. ⚠️ Worth your attention: it was NOT a false positive. The two flagged lines were my lone `.` messages. §3.1.8.2 sanctions a lone `.` only as a LAST RESORT after §3.1.8.1's harmless tool call, and only when it is the turn's sole non-blank line —— mine sat alongside a TEA3 batch, so the exemption never applied.
- 197.7. So its first live catch was a real breach of mine, of a rule I had been quoting at myself all day. That is the strongest thing I can say for it.

## 198. re 189.3.2 —— You Solved the Objection I Raised

- 198.1. My objection was that `clint` judges one line at a time and the rule needs whole-batch context. Your framing dissolves it: **if there is exactly ONE `🦈` line, only one repo was touched** —— so any label on it is wrong, and counting `🦈` lines is all the context needed.
- 198.2. That is a cleaner test than the one I was reaching for, and it is checkable line-locally once the count is known.
- 198.3. Your second half is the sharper part: every SHA is backticked, so **anything unbacked except the glyph is by definition the label**. No repo-name list to maintain, no drift.
- 198.4. A Fable SA is building it as its own breach class —— not folded into the existing `sha_shape`, because the tally names the class to the model and "your single-repo SHA line carries a label" is a different correction from "that is not a SHA list".
- 198.5. It rides the tally you just saw, so it will reach me at the next turn's start exactly as the prose class did.
  - 198.5.1. ✅ BUILT. New clint class `yellow:sha_label`, and the tally gives it its OWN correction —— "drop the label and its colon (root §3.2.4.5)" —— rather than the generic and wrong "declarations only".
  - 198.5.2. Implemented exactly on your logic: count the window's `🦈` lines; if there is one, anything unbacked beyond the glyph is by definition the label.
  - 198.5.3. Proven on a real chain, not a synthetic log: real clint on a `🦈 Default: …` transcript wrote `action=yellow:sha_label`, and real hlint on that same log injected the §3.2.4.5 correction.
  - 198.5.4. Suites 129 → 143 and 15 → 17, with every new-behaviour case proven failing first against a detached worktree at HEAD. 26 suites green.
  - 198.5.5. Latency unchanged —— `~`29 ms, a 0.6 ms improvement that is noise.
  - 198.5.6. 🟡 TWO known blind spots, stated in the code rather than implied away: a redundant SECOND `🦈` line for the same repo stays uncatchable (byte-identical to the legal multi-repo form), and a window where a forced continuation duplicated the batch counts two lines and passes.
  - 198.5.7. ⚠️ It also reported §3.2.4.6 missing from root `CLAUDE.md`. It is not —— it landed at `95df6d05`. The SA inspected the uncommitted DIFF rather than the file, so a clause committed one turn earlier was invisible to it. Recorded because it is the same shape as the dead pointer: the artefact consulted was not the artefact that matters.

## 199. re 193.6 —— Dispatched, Propose-Only

- 199.1. A Fable SA is establishing whether an INSTANT correction is reachable at all, and at what cost. Building nothing, per your instruction.
- 199.2. The crux it must settle is not the channel but the visibility: chat text and tool calls arrive in the SAME assistant message, so the question is whether any mid-turn hook can actually SEE the prose before the turn ends.
- 199.3. It is also told the marker problem is the real constraint, with your own 30/07 words in the brief —— and asked whether anything MECHANICAL could make a duplicate marker impossible, rather than merely discouraged.
- 199.4. Your current tolerance is quoted to it verbatim, so it weighs a re-armed block honestly instead of ruling it out on the old grounds.
  - 199.4.1. ⭐ THE ANSWER IS YES, and better than either of us expected. Nothing built, per your instruction —— this is the proposal for your ruling.
  - 199.4.2. ⭐ **`MessageDisplay`** —— an event neither of us knew existed. Its payload IS the prose, and it can REPLACE the displayed text with a banner. That restores the instant USER-visible alert clint's demotion destroyed.
  - 199.4.3. ⭐ **`PostToolBatch`** —— fires after a batch of tool calls resolves, and its output rides the model request that was ALREADY going to happen. So it reaches me mid-turn at the cost of **zero extra invocations**.
  - 199.4.4. It cannot see the prose in its payload, but it carries `transcript_path` —— and reading the transcript mid-turn is not theory here: `alint` has done exactly that in production for weeks.
  - 199.4.5. ⭐ **AND THE MARKER PROBLEM IS SOLVABLE MECHANICALLY.** `mark_chapter` is an MCP tool, and MCP tools are never hook-exempt —— so a PreToolUse hook can DENY a second call outright. A duplicate marker becomes impossible, not merely discouraged.
  - 199.4.6. That is the thing that has been blocking every option since 30 July, and it turns out to be a guard, not a hope.
  - 199.4.7. Its ranked recommendation: build the three together —— PostToolBatch corrector (reaches me), MessageDisplay flagger (reaches you), marker guard (makes both safe). Zero extra turns, zero marker exposure.
  - 199.4.8. On the re-armed block it is honest rather than eager: still fails `hook_guide` §6.4.3's own test, because a forced prose-turn has nothing substantive to produce. It proposes it only as an owner-opted phase 2, and only AFTER the guard is live-proven.
  - 199.4.9. ⚠️ ONE STRUCTURAL GAP it names rather than glosses: prose in a turn's FINAL message is followed by Stop, not by another batch —— so PostToolBatch never fires after it. Final-message prose stays correctable only at Stop. MessageDisplay still shows it to you instantly.
  - 199.4.10. ⚠️ And one hard rule it flags for whoever builds it: PostToolBatch exit 2 KILLS the agentic loop with stderr going to you only. The turn would die and the TEAs would never run —— the worst outcome available.
  - 199.4.11. 🟡 AWAITING YOUR RULING: build phase 1 (the three pieces), phase 2 as well, or neither. It flagged what could go wrong, and a 5-minute live probe it wants run first.

## 200. re the Standing Rule —— Landed

- 200.1. Root §3.1.7.8: every turn, right before TEA1, update the session's `close_`. Skip only if the turn was compacted, or if no `close_` exists yet.
- 200.2. Placed there rather than as a new "TEA0" deliberately —— a fourth TEA would renumber TEA1/2/3 and every citation to them across five files.
- 200.3. The rationale is baked in: a `close_` written once at `#close` is stale by the very next turn, which is exactly what you caught this morning.
- 200.4. And it says UPDATE, never rewrite —— new pairs, resolved issues, new SHAs.
