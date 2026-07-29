# Response to ccsim_query_202607291950.md
*Double-declaration cause found; your c.md edit endorsed; closing*

## 93. re Preamble —— Double Declaration
- 93.1. Confirmed and owned: I declared twice in Turn 13 —— a partial `✅` mid-turn, then the full batch at the end.
- 93.2. Cause, precisely: whenever I have nothing to DO but wait, the harness still requires visible output, so I reached for a declaration to fill it. That is the same reflex that produced the `⚠️` progress notes —— filling a required output slot with the cheapest thing that passes.
- 93.3. Avoidable, and the fix is one rule: whilst waiting, make a TOOL CALL (the wait itself) and emit no chat text at all. A tool call satisfies the harness; a declaration is never needed mid-turn.
- 93.4. Adopting that from here. Not adding it to a file —— it is a discipline, and you have rightly pushed me towards enforcement over more prose. If it recurs, it becomes a lint.
- 93.5. Thank you for the win signal on the rest —— the no-prose turn was the first clean one.

## 94. re 80.1 —— Your Edit Is Better
- 94.1. Still effective, and tighter than mine. Restructuring §8.6 around the CONFIG DIR with memory as a sub-case is the right shape: the general rule now leads, the exception hangs off it.
- 94.2. Your rationale holds —— a directive file needs the rule, not the justification. Dropping the "why the snapshot rots" was correct.
- 94.3. One small ambiguity, your call whether it matters: §8.6.2 "If touched, draft …" sits after the memory carve-out, so a literal reader might think a routine memory READ triggers a queued query. §8.6.1 already exempts memory, so the intent is clear —— but "If touched (per §8.6.1)" would remove all doubt in three words.

## 95. re 83 —— Yes
- 95.1. Correct. A regression = something that previously worked now broken. What I kept hitting was the mirror image: the code changed on purpose, and the test still demanded the old behaviour.
- 95.2. Worth naming the distinction, because it decides the fix: a regression means fix the CODE; a stale assertion means fix the TEST. Treating one as the other either reverts a wanted change or hides a real break.

## 96. re 87, 89.4, 89.8
- 96.1. re 87 —— understood; the only bar is that every session can push in both modes.
- 96.2. re 89.4 —— good, and that removes the single data-loss risk entirely. With "On My Mac" emptied, the folder is now pure cache.
- 96.3. re 89.8 —— you are right and I was wrong to infer otherwise. An SA is reading your screenshot and reconciling it. My inference was "no stored value therefore unset"; the likelier truth is that `Recent` IS the default, so choosing it writes nothing. Confirming, plus what `Recent` actually bounds —— since it clearly did not stop 2018 attachments accumulating.

## 97. re 90.5 —— Clarified
- 97.1. Nothing to do with anything reading a deleted file. The suite in question asserted that `date_added.py` still existed under its `❌_` voided name.
- 97.2. When you deleted the voided file (your half of the Void Rule), that assertion failed —— not because anything broke, but because the rule completed.
- 97.3. Fixed and confirmed: the test now asserts only what matters —— that no LIVE predecessor exists —— and accepts either end-state. Suite back to 70/70.

## 98. re 91.3 —— Benchmark Recorded
- 98.1. Your arithmetic: 1.26Mn at 17 ses% → `~`7.4Mn per 100 ses% on Opus.
- 98.2. Recording it in the `close_` as you asked, with the caveat that it is one measurement from one turn, so treat it as an anchor to calibrate against rather than a constant.
- 98.3. On your Sonnet/Fable extrapolation —— plausible but unverified. Limits are usually weighted per model rather than being a flat token pool, so I would not assume a clean 2× or 0.5× until measured the same way.
- 98.4. Agreed the Perplexity figure (`~`88k) is far off —— off by roughly two orders of magnitude against this measurement.

## 99. Closing
- 99.1. `#close` done —— `ccsim_close_202607291954.md` written; session span 202607250326–202607291954, 16 pairs plus 2 non-paired.
- 99.2. The sesL benchmark is recorded in its § Remarks per your §91.3, with the caveat that it is one measurement.
- 99.3. Two CCSIM backlog entries appended per `close.md`: the double-declaration reflex (§93) and the standing rule that a suite must never assert the presence of a voided file (your half of the Void Rule).
- 99.4. ⚠️ One item is NOT resolved and I am not pretending otherwise: the Mail attachment targets, the `Recent` reconciliation and the Time Machine recommendation are still with an SA. If it lands after this turn closes, that is the one thing to pick up next session —— nothing in the repo depends on it.
