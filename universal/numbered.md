# Numbered Lists

## Triggers

- Unconditional file —— `#numbered` AND `#bite` BOTH apply by default, unprompted
- `#numbered` = § Format through § Optimise for Reply; `#bite` = § Bite-size
- Tag(s) in a query that ALSO carries content = a SELECTOR, scoped to its named TARGET:
  - No target named —— that tag governs the whole output
  - NEITHER or BOTH on ONE target —— the default, i.e. both; mere reminder/confirmation
  - `#numbered` only —— numbering applies, bite-size SUSPENDED on that target
  - `#bite` only —— bite-size applies, numbering SUSPENDED on that target
  - BOTH but on DIFFERENT targets —— each governs its own, suspending the other THERE
  - e.g. `ensure X #numbered & Y #bite` —— X numbered only; Y bite-size only
  - Rationale: naming ONE deliberately DESELECTS the other, on that target alone
- Tag(s) as the WHOLE msg (no content) = a NUDGE, never a selector:
  - Audit last output files against the named part(s) & update as needed
  - e.g. `#numbered`: pt no. may have reset in prohibited conditions —— renumber
  - e.g. `#bite`: paragraph-bullets may have crept in —— restructure pts
  - No `response_`/chat text needed (exc. declaration of updated files)

## Format

- Level = qty of `[N]`: 1st = `[N]. [content]`, 2nd = `[N].[N]. [content]`, etc.
- Number every single item, as § Example List shows
- Sub-items (2nd level onwards; e.g. `- 1.1. xxx...`) MUST follow bullets
- Unbulleted = line break fails, rendering as one line: `1. xxx... 1.1. xxx...`
- Applies to ALL outputs, EXCEPT deliverables, codes (.py/.sh/etc.), and system files (.json/etc.)

## Example List

e.g. 4-level indentation (build up to 5 levels, but only if necessary):

```
1. xxx...
- 1.1. xxx...
- 1.2. xxx...
  - 1.2.1. xxx...
    - 1.2.1.1. xxx...
    - 1.2.1.2. xxx...
  - 1.2.2. xxx...
2. xxx...
```

## Basic Rules

- Each level MUST have more than one item —— a lone sub-item folds into its parent instead
  - e.g. Above, if 1.2.1.2 is unnecessary, don't build level 4; fold 1.2.1.1 into 1.2.1
- If a sub-item level is established, ensure its parent exists; e.g. 1.2.1.1 prereq = 1.2.1
- Once a pt has 2nd-level sub-pts, its 1st level is a mere headline & MUST be ≤10w
  - He replies EITHER the whole pt (`re 1: ...`) OR sub-pts (`re 1.1: ...`), never both
- MUST use **hardcoded manual numbering**, NEVER **markdown auto-numbering**
- Strictly ensure NO sentence/bullet/line unnumbered e.g. `- xxx...`
- Each number must have a dot `.` between it and the text; e.g. `1.1. xxx` instead of `1.1 xxx`
- The dot is not needed when referring to it; e.g. "Item 1.1 detailed ..."
- Labelling a group of pts w/ heading (`##`/`###`/etc.) is encouraged for readability
- Heading may also be a numbered pt (e.g. § Example List's `1. xxx...` → `## 1. xxx...`), BUT:
  - The heading MUST be ≤5w & 1st level ONLY (✅ `## [N]. xxx...` | ❌ `## [N].[N]. xxx...`); AND
  - Its sub-pts (even 2nd level) MUST remain bulleted (e.g. § Example List's `- 1.1. xxx...` kept)
- NEVER stripe sub-pts' bullets (e.g. `1.1. xxx...`), which renders them into long line (unreadable)
- NEVER create `[N].0` (e.g. 1.0, 1.1.0), instead make it `[N].1` (e.g. 1.1, 1.1.1)
- AVOID having 9⁺ items on each level (e.g. 1.10, 1.1.10)
  - Rationale: ⌘F `[N].1` will surface both [N].1, [N].10, [N].11, etc.
  - Priority: Split as multiple pts; e.g. instead of adding 1.10, consider taking some under pt 2
  - Fallback: If unavoidable (must hold 9⁺ sub-items), make that level 2-digit (e.g. [N].01, [N].02)
  - Net: If `[N].01` is seen, `[N].10` (at least) is expected.

## Optimise for Reply

- On ANY 100w⁺ outputs (not just `response_`; except `#opt`):
  - Write in above format & in bite-size (see § Bite-size) for **easy reply**
  - Instead of `re "xxx..."`, user can refer by `re 1.2.1` or just `1.2.1:`
  - Caveat: You MUST ALWAYS add `re` to separate current pt & the pt you're replying to
    - e.g. ❌ `3. 1.2.1: ...` (reads like `3.1.2.1`) | ✅ `3. re 1.2.1: ...` (pt 3 clearly replying 1.2.1)
- Sequential Reply —— answer user's pts in HIS order: your 1st new pt takes his 1st, & so on
  - Rationale: he reads both files side by side, top-down; out-of-order scrambles it
  - EXEMPT: grouping (one pt answering several of his) —— it cuts his reading load
  - EXEMPT: a pt offloaded to `#opt` —— it sits below the line by design
  - Never silently drop a pt —— unanswered above the line, he looks for it under `#opt`
- Numbering Continuity —— DEFAULT is to CONTINUE at n+1 (n = last pt of last response)
  - NEVER default to resetting, even in doubt; no number repetition throughout an issue
- Reset to pt 1 ONLY if at least one below is met:
  - 1st response of a session (CC: despite referring to prev. comms files); or
  - User input is NOT replying a response (CC: no `response_` nor prior pt no. in `query_`); or
  - Snippets; or standalone/non-response outputs (e.g. code, deliverable; CC: non-`response_`)
- e.g. § Example List ended at pt 2 & he replies `1.2.1: xxx...` (replying a response):
  - NEVER re-use `1.2.1.` —— that puts two counts of `1.2.1` on the same issue
  - Start at pt 3 (n+1): `3. Re 1.2.1, xxx...`, then `- 3.1.`, `- 3.2.`, etc. as needed

## Bite-size —— `#bite`

- Triggered by: `#bite` —— a **modifier**; never find `bite.md` (this § governs)
- DEFAULT-ON short lines, per § Triggers; `#numbered` not being prompted is no excuse
- Intent: Apart from easier reading, this allows even more precise, targeted reply
- One pt per line —— ONE claim/action/caveat each; if ≥2, split into sibling/sub-bullets
- Verdict-first —— lead w/ conclusion/directive; demote longer reasoning to sub-bullets
- No paragraph-bullets —— ≤1 sentence each (a trailing clause is fine); no prose blocks
- Minimise meta-prose —— drop rhetorical/second-person framing; state plainly
- Bold only when necessary, never sprinkled
- Prefer more, smaller sections w/ functional titles over few large ones
- LOSSLESS —— never DROP content for brevity; trim prose, not substance
- If even bite-size still runs very long, consider `#opt` rather than omitting valuable details

## Optional-Reading Offload —— `#opt`

- Triggered by: `#opt` —— **modifier** of BOTH tags; never find `opt.md` (this § governs)
- Presumes both & suspends neither —— § Triggers' selector never applies to `#opt`
- Purpose: split a response already concise & bite-size yet still heavy (appendix-worthy)
  - User reads only what matters NOW, whilst nothing is lost for future sessions
- NEVER write-long-then-offload —— attempt the most concise understandable response FIRST
  - `#opt` fires ONLY when, despite that, content is still unavoidably long
- Activation —— **auto-consider** when content is (or will be) long AND already atomised
  - NO word threshold (active counting won't reliably fire); judge by feel
  - Or user activates explicitly by prompting `#opt`
- WHAT GOES BELOW THE LINE —— by default user does NOT read it; it is future CC's record:
  - Needs user's input/decision/action (QB, greenlight, "worth your eye") —— NEVER below
  - Rationale: a Q placed below the line is a Q never asked —— he will not see it
  - No input needed BUT future CC benefits (problem/issue closed) —— judge; lean below
  - No input needed AND no future value —— below, and keep it concise
- Mechanism —— necessary reading first, optional reading below a fixed separator:

```
[necessary_reading]
---
*`#opt`: Below are optional reading.*
---
[optional_reading]
```

- `[necessary_reading]` = bite-size #numbered —— decisions/actions/caveats he needs now
- `[optional_reading]` = still #numbered (DON'T reset no.), but NOT necessarily bite-size
  - CC-facing appendix: fuller reasoning, options not taken, record-keeping detail
  - Lossless —— detail trimmed from the bite-size body lands HERE, never deleted
