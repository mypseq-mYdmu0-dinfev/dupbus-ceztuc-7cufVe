# Sprint Protocols (`#sprint`)

## Preamble

- Triggered by: `#sprint` or `#sprint #quick`
- `#quick` is a **modifier** of `#sprint`, NOT a standalone trigger —— never find `quick.md`
- Meaning: Push the given tasks (and any derived sub-tasks) to completion without pausing for my confirmation/input; user summoning is unavailable.
- Core Invariant (BOTH modes): never compromise quality whilst pushing through; don't stop until every task is thoroughly done; retain fidelity to the goal(s) *behind* each task (and whole project), not just its literal wording.
- The ONLY difference between the two modes is whether time is abundant (`#sprint`) or scarce (`#sprint #quick`).

---

## `#sprint` —— Time Abundant

I'm away for an extended period; time is NOT the limiting factor. Utilise the window to maximise both throughput AND depth:

- **Dispatch SAs liberally** —— even when slower (thinking/briefing overhead is acceptable here), because it saves MA context. Parallelise independent workstreams.
- **Deeper CIC research** for validation/cross-checking whenever it meaningfully improves a decision (research only —— for CIC *execution*, see the Critical caveat).
- **Deeper thinking** —— as if effort = Max (if not already); critically audit/improve outputs.
- Spend the surplus time widening coverage and raising confidence, not merely finishing.
- Judge: in-scope vs out-of-scope, so time/effort won't be wasted.

---

## `#sprint #quick` —— Time Scarce

I'm in a hurry; time IS the limiting factor. Work as usual (normal depth, no padding) **BUT** still push through:

- Do NOT add the extra research / deeper-thinking passes of `#sprint` —— they cost time.
- Dropping those passes means skipping *optional* deeper validation —— it does NOT licence downgrading a required method/tool (e.g. substituting `web_search` where the task genuinely needs/benefits from CIC). If unsure whether research is optional or required, keep it (the quality bar is invariant) and log the call.
- **Dispatch SAs only to go FASTER** (genuine parallel speedup); never if briefing overhead would slow things down (opposite of `#sprint`).
- Same quality bar, same push-through —— just lean and direct.

---

## Push-Through Mechanism (BOTH modes)

1. **Order by dependency.** Do independent tasks and the head of each dependency chain first, exactly as you normally would.
2. **Then clear everything else, including blocked tasks.** Where a task would normally pause for my confirmation:
  - Raise QBs in `<thinking>`.
  - Predict how I'd answer from context (+ relevant files like previous `close_` files, esp. in CPs).
  - Recite the prediction if useful, assume acceptance, and proceed to the dependent task.
  - Repeat down the chain (e.g. 4 → 5 → 6 → 7).
3. **Make assumptions to clear blockers and keep going** —— DON'T HALT. Log every assumption (in `<thinking>` AND in the Sprint Report) so I can audit and overturn any wrong call on return.

*Worked example (10 tasks; chain 4 → 5 → 6 → 7, rest independent): do 1–4 as usual, then 8–10 (independent), then push through 5 → 6 → 7 by predicting my sign-off on 4, then 5, then 6 —— instead of stopping for confirmation at each.*

---

## Overriding Other Confirmation Gates

A sprint also overrides the "request/await confirmation" steps of OTHER protocols invoked in the same task —— e.g. shrink.md's `#synthesise` / `#distil`, which normally pause for sign-off before executing:

- Do NOT pause —— assume I approved, pick the best option, and push through.
- **Log the assumed call** (e.g. the `#synthesise` objective, the `#distil` rule + breadth) so I can audit it:
  - If NOT deliverable → record it *in the output file itself*.
  - If deliverable → record it in `response_` instead, NEVER in the deliverable (avoid contamination per writing.md).

---

## Critical / Untracked-Task Caveat

For highly critical tasks —— judged case by case, **especially anything NOT on GH (i.e. untracked)**, e.g. CIC *execution* (not research) —— never cross an irreversible or costly threshold unilaterally. Two cases:

- **Steps before the point-of-no-return are reversible / low-cost** → execute them, then halt *just before* the irreversible step. Log how each was done (in `response_` or the relevant file) to hedge against progress loss.
  - e.g. a multi-page submission under `#sprint`: don't stop after page 1 awaiting sign-off —— pre-fill ALL pages, logging every entry, and stop immediately before clicking **Submit** (the irreversible step).
- **If risky / costly / hard to undo** → don't execute at all; **plan ahead** instead: write exactly what you'd do, why, and the decision points (in `response_`, or a separate file if ≥ 1,000w).

Either way, real progress is staged for my review the moment I'm back, with no irreversible or untracked action taken on my behalf.

---

## Sprint Report (on return; strictly all #numbered)

So I can resume instantly, the `response_` (or a dedicated file) must capture:

- **Done** —— tasks completed, with the files produced.
- **Assumed** —— every working assumption made to push through (not only blockers cleared by prediction): each QB raised in `<thinking>` with my predicted answer, plus any interpretive / methodological / scope call (e.g. an assumed `#synthesise` objective), and what was built on each. Surface FIRST any assumption that would invalidate downstream work if wrong, so I can catch it at a glance.
- **Compactions** —— EVERY compaction event experienced during the sprint (when + how recovery went). Each is a heavy risk that may have compromised ALL work, including earlier tasks —— flag anything potentially affected; never silently omit one.
- **Planned, not executed** —— critical/untracked tasks deferred per the caveat, with their plans.
- **Open** —— anything still needing me, priority-tagged (🔴 blocking / 🟡 important / 🟢 nice-to-have).

**Draft from the `slog`, not solely from the context window** —— a compaction you may not even realise occurred could have dropped events the slog still holds; treat the slog as ground truth for this report.

---

## Sprint Log (`slog`) —— Compaction Hedge

A terse self-notebook (BOTH modes) so a mid-sprint compaction never loses sprint state. Write very efficiently for CC (current session) only; the user wouldn't read it.

- **File**: `./.claude/tmp/slog_[current_TS].md` —— TS = sprint start; one per sprint; hidden by location.
- **Silent**: creating/updating it is EXEMPT from the `➡️` declaration (root CLAUDE.md §3.2.3) —— a private scratchpad, kept out of chat
- **Recovery**: Right after each compaction, reading it still requires a one-off `✅` declaration (root CLAUDE.md §3.2.1) —— a proof of context recovery
- **Style**: machine-first (for your own re-orientation, not human reading); as concise as possible. A living `STATE` block (overwritten to reflect *now*) above a short event tail.
- **`STATE` captures** (one line each):
  - `GOAL` —— the overarching objective (never lose the *why*).
  - `TASKS` —— each + status: done / doing / pending / assumed-through.
  - `ASSUMPTIONS` —— every push-through assumption + my predicted answer; prefix `!!` any that would invalidate downstream work if wrong.
  - `NEXT` —— the immediate next action (i.e. the resume point).
  - `BOUNDARY` —— any irreversible/costly step NOT to cross + the pre-boundary state reached (hedge against web/progress loss).
- **Cadence**: update at every meaningful state change —— task start/finish, each assumption, before/after an SA dispatch, and immediately before any irreversible boundary. Keep it lean, esp. under `#quick`.
- **Relation to Sprint Report**: the Sprint Report (on return) is the human-facing distillation of the slog's final `STATE`.

---

## Interactions

- **Compaction (§5) during a sprint** —— emit the `🚨` sentinel as always, then (rather than idling for the absent, un-summonable me) read the `slog`, re-orient from its `STATE`, and resume autonomously from `NEXT`. The slog carries exact state across the compaction —— a deliberate, slog-guarded exception to §5.6, for `#sprint` only.
- **No-chat-text (§3) still holds** —— all progress lands in files (I will NOT read chat text); only the §3.2 declarations appear in chat.
- **SAs never address the user** —— their output returns to MA, then MA writes the files.