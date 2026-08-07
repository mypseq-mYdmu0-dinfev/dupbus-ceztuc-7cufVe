# Response to ccsim_query_202608071454.md
*Litter untracked; nine fixes applied; clint under investigation*

## 174. re sesL —— Nothing Compromised, Checked Rather Than Assumed

- 174.1. All five SAs had RETURNED before the limit hit. None died mid-flight, so §9.02.4's redo rule does not bite this time.
- 174.2. Verified, not assumed: 25 of 25 suites green, and the tree holds only my own comms files —— every SA's transient ablation was restored.
- 174.3. One thing DID move whilst I was out: AJAP consumed my reply `#qq`, moved it to her `inv/` and answered it.
- 174.4. ⚠️ And she caught a real defect in it: my §5.1 pointed her at `cp/ccsim/sandbox/ajap_feedback_evidence.md`, which I had never COMMITTED. A dead pointer —— evidence she could not fetch. Committed now.

## 175. The Litter —— Fixed, and the Class Closed

- 175.1. Untracked, not deleted: `❌_hdaudit_nog/`, `❌_hdaudit_symlink`, `cscpt/❌_plint_state/`. The disk copies still sit there awaiting YOUR delete, per §8.2.3.
- 175.2. `.gitignore` now carries `❌_*`, so `git add -A` can never sweep voided litter again. That is the mechanical fix, not a resolution to be careful.
- 175.3. The edge case was PROVEN before relying on it: `git mv tracked.md ❌_tracked.md` still stages the rename even when the target name is ignored —— so voiding a tracked file keeps working and keeps its history.

## 176. Nine Fixes From the Audits, Applied

- 176.1. ⚠️ D1, the one that mattered: `mlint`'s blocked-turn message taught the OLD §5.8. It would have handed a post-compaction model the superseded rule at the exact moment its context was weakest. Now matches.
- 176.2. D2 —— `hook_guide.md` §0.1.5's write figure corrected `~`0.11 s → `~`0.15 s, with the arithmetic shown and the old figure named as the mistake it was.
- 176.3. D3 —— four stale `§5.1.4` pointers in the post-compact suite re-aimed at §5.1.6.
- 176.4. D4`~`D6 —— `pre_compact` added to the liveness inventory; the hard-wrapped lines broken into sub-points as `coding.md` requires; §12.7 marked SUPERSEDED rather than left to contradict §0.1.
- 176.5. D7 —— `cscpt/README.md` said mlint was the one unguarded hook body. It was guarded in the same commit. That sentence would have invited a future editor to re-break the only blocking hook.
- 176.6. §5.5.1 —— rewritten and EXTENDED. It now says root `CLAUDE.md` is injected only when cwd is this repo or a child, and that a session with the repo merely ADDED must re-read it, because compaction evicts one-off reads.
- 176.7. ⭐ And the pre-compact fail-open, which was mine and genuinely dangerous: it now LOGS on every branch but emits the payload ONLY when the cwd is proven to be this repo.
- 176.8. Why that asymmetry is right: every other hook here fails open because a lint breaking a turn is worse than one missing a turn. This is the only hook whose output reaches a MODEL —— failing open there meant injecting a HALT-and-await mandate into whatever project happened to be compacting, including an unattended cockpit.
- 176.9. Pinned with a negative control: reverting to blanket fail-open turns the suite red. 75/75, and 25 of 25 suites green overall.

## 177. re clint —— Dispatched, and Your Doubt Is Well Placed

- 177.1. A Fable SA is on it, briefed to settle the CHANNEL question FIRST because everything else depends on it.
- 177.2. ⚠️ Your instinct may be sharper than my belief. I have asserted that clint's exit-0 output reaches YOU but not me. You say you see nothing either. If BOTH are true, clint has been shouting into a void since its demotion —— worse than either of us thought.
- 177.3. It has your `CIIW` and is told to hunt the comms record for the real demotion reason rather than accept my recollection or yours.
- 177.4. It also has your clarification verbatim: multiple turns are acceptable NOW provided the TEAs and chapter markers stay 100% accurate, and the ROI test is "chat prose reduced whilst markers still right".
- 177.5. Your hard constraint is in its brief: **do not re-arm the red-flag block.** It must find something strictly better whilst staying warn-only, or return a design and change nothing.
- 177.6. On your model/domain hypothesis —— it is told that "unknowable from here" is a valid answer, so it cannot manufacture a plausible story from insufficient data.

## 178. ⭐ You Were Right About clint —— and It Is Worse Than Either of Us Said

- 178.1. **clint's warnings reach NEITHER of us.** Not you, not me. Since the demotion it has been shouting into a void.
- 178.2. Mechanism, from the binary: an exit-0 `systemMessage` becomes a transcript attachment whose model mapping is literally `()=>[]`, and it is rendered ONLY by the terminal UI. The Desktop app has NO renderer for it —— zero occurrences in its resources.
- 178.3. Evidence, not inference: **142 real records** carrying clint's exact warning text sit in this project's transcripts, structurally parsed, none of them contamination. You have seen none of them because there is nothing to see them with.
- 178.4. So my §150.6 was wrong in your favour. I told you clint reached you and not me; it reaches neither. Corrected in `hook_guide.md` §6.1, which had the same error.
- 178.5. ⚠️ A second correction to my own doctrine: exit-0 `additionalContext` IS supported at Stop and DOES reach the model —— `hook_guide.md` said "not a supported channel". But it RE-INVOKES the model on the same path as a block. It is a block wearing a softer name.
- 178.6. Which yields the real constraint, now written into §6.1.4: at Stop there is **no non-waking model channel, by construction** —— the model has stopped, so reaching it means starting it again.

## 179. Your `CIIW` —— Confirmed and Refined

- 179.1. Your recollection was right, and incomplete in your favour. The demotion order is your own, 30 Jul: the block "has FAILED to block you at all … AND it possibly made you emitted even more errors, like batch-declaring THRICE and painful failure of marking the chapter JUST ONCE".
- 179.2. So there were TWO reasons, not the one you remembered: the phantom markers (two markers over one real turn, Turn 15 never marked —— your words, "DECEIVING ME"), AND that it was not stopping the prose anyway.
- 179.3. That second reason matters for your ROI test: re-arming the block would buy back a mechanism that had already failed at its own job.

## 180. Model vs Domain —— Honestly Unresolvable

- 180.1. Your perception is CORRECT in shape: Opus breaches are multi-line narration paragraphs; Sonnet's are 1`~`2-line slips (a misplaced lone dot, a short status note). Sonnet is not clean, but its breaches are qualitatively tiny.
- 180.2. ⚠️ But model and domain are PERFECTLY correlated in the available sample —— Opus ran the CCSIM and agent-heavy sessions, Sonnet ran career and task sessions. The two cannot be separated from here.
- 180.3. What IS supported: breaches concentrate at multi-agent dispatch and waiting moments, and at session-limit failures —— wherever those happen. That matches exactly where mine occurred today.

## 181. What Was Fixed, and the One Thing I Am NOT Rushing

- 181.1. ✅ FIXED: clint was flagging the §5 compaction lists —— the very output `mlint` BLOCKS until it exists. Two Stop hooks of one suite were mandating and forbidding the same lines. Suite 118 → 129, three cases proven failing against HEAD first.
- 181.2. ✅ `hook_guide.md` §6 corrected in three places; its channel table was the single most load-bearing wrong thing in the repo's own documentation.
- 181.3. 🟡 NOT BUILT, and this is the one I want your word on: the SA's best idea is a **UserPromptSubmit tally** —— inject "N chat-discipline breaches last turn" into the START of my next turn.
- 181.4. Why it fits your ROI test exactly: model-visible, ZERO extra turns, ZERO marker risk. It corrects me where I can act, without the block you ruled out.
- 181.5. Why I have not built it tonight: it is new wiring on a live event at the end of a very long turn, and §8.5 is explicit that a rushed gate is how this repo keeps paying. Say the word and it is one focused turn.
- 181.6. 🟢 Also on the table, not recommended: `PostToolBatch` —— the only MID-turn non-blocking model-visible correction point, so it could catch narration before the turn ends. Bigger change, more risk.

## 182. 🟡 One Thing I Cannot Resolve Alone —— Turn Boundaries

- 182.1. Every message since `12672c86` arrived whilst I was mid-flight with agents running. By §3.1.7.6.1 that makes them all mid-turn messages of ONE practical turn.
- 182.2. But each carried `QMM`, and I gave each its own `query_` AND its own `response_` —— three pairs. §3.1.7.7.3 says a mid-turn message stays in the CURRENT `response_`, so on the strict reading I created two more than I should have.
- 182.3. I have marked ONE chapter for the whole stretch, which is the reading that keeps your navigation intact —— your stated priority.
- 182.4. Your ruling needed: does `QMM` on a mid-turn message create a new pair, or only a new `query_` answered inside the existing `response_`? Precedent says the latter (`ccsim_close_202607291954.md` §6.19), and I departed from it.
- 182.5. Flagging rather than quietly renumbering, because the `#close` inventory counts pairs and I would rather you decide than inherit my guess.

## 183. YELLOW Justifications

- 183.1. Across this turn's three `response_` files, every surviving bare `read` is a NOUN ("a one-off read", "an active read") or future tense ("before you read the rest"). No `#r` owed; the past-tense ones were silently corrected.
