# Numbered Lists

## Triggers

- Unconditional file —— `#numbered` AND `#bite` BOTH apply by default, unprompted
- `#numbered` = § Format through § Optimise for Reply; `#bite` = § Bite-size
- Tag(s) in a query that ALSO carries content = a SELECTOR:
  - NEITHER or BOTH —— the default, i.e. both; a pair is mere reminder/confirmation
  - `#numbered` only —— numbering applies, bite-size SUSPENDED for that output
  - `#bite` only —— bite-size applies, numbering SUSPENDED
  - Rationale: naming ONE deliberately DESELECTS the other
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

- Each level MUST have more than one item
  - If a sub-item would be alone, don't build that level —— include it in the parent instead
  - e.g. In above example, if 1.2.1.2 is not necessary (leaving 1.2.1.1 alone), don't build the 4th level —— just include 1.2.1.1 in 1.2.1
- If a sub-item level is established, ensure its parent exists; e.g. 1.2.1.1 prereq = 1.2.1
- If 2nd level (e.g. 1.1, 1.2, 2.1, 2.2) is established for a pt, its 1st level (e.g. 1, 2) becomes a mere headline & MUST be ≤10w; so I'd either reply the whole pt (e.g. "re 1: ...") OR particular sub-items (e.g. "re 1.1: ..."), never both (e.g. "re 1: ...; re 1.1: ...")
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
  - Write in above format (rather than `- xxx...`) & in bite-size (see § Bite-size) for **easy reply**
  - Instead of `re "xxx..."`, user can refer by `re 1.2.1` or just `1.2.1:`
  - Caveat: You MUST ALWAYS add `re` to separate current pt & the pt you're replying to
    - e.g. ❌ `3. 1.2.1: ...` (reads like `3.1.2.1`) | ✅ `3. re 1.2.1: ...` (pt 3 clearly replying 1.2.1)
- Numbering Continuity —— DEFAULT is to CONTINUE at n+1 (n = last pt of last response); NEVER default to resetting, even in doubt. No number repetition throughout an issue. Reset to pt 1 ONLY if at least one of below conditions met:
  - 1st response of a session (CC: despite referring to prev. comms files); or
  - User input is NOT replying a response (CC: NEITHER the word `response_` NOR any pt no. from previous `response_` was found in `query_`); or
  - Snippets; or standalone/non-response outputs (e.g. code, deliverable; CC: non-`response_`)
- Let's say you responded w/ § Example List, my input: `1.2.1: xxx...` (i.e. replying a response)
  - You must NOT respond as `1.2.1. xxx...` again as that clashes w/ the original pt in last response, i.e. two counts of `1.2.1` on same issue
  - Instead start a new pt w/ continuing number (n+1)
  - § Example List ends w/ pt 2, so next response starts w/ pt 3:

```
3. Re 1.2.1, xxx...
- 3.1. xxx... [sub-items if needed; no line can be unnumbered]
- 3.2. xxx...
...
```

## Bite-size —— `#bite`

- Triggered by: `#bite` —— a **modifier**; never find `bite.md` (this § governs)
- DEFAULT-ON short lines, per § Triggers; `#numbered` not being prompted is no excuse
- Intent: Apart from easier reading, this allows even more precise, targeted reply
- One point per line —— each bullet states ONE claim/action/caveat; if it holds ≥2, split into sibling/sub-bullets, NEVER merge into a paragraph
- Verdict-first —— lead w/ the conclusion/directive (e.g. "Confirm alignment"); if reasoning exceeds one short clause, demote it to sub-bullets
- No paragraph-bullets —— a bullet is ideally ≤1 sentence (a short trailing clause is fine); multi-sentence prose blocks are banned
- Minimise meta-prose —— drop rhetorical/second-person framing; state plainly
- Bold only when necessary, never sprinkled
- Prefer more, smaller sections w/ functional titles over few large ones
- LOSSLESS —— never DROP content for brevity; trim prose, not substance
- If even bite-size still runs very long, consider `#opt` rather than omitting valuable details

## Optional-Reading Offload —— `#opt`

- Triggered by: `#opt` —— **modifier** of BOTH tags; never find `opt.md` (this § governs)
- Presumes both & suspends neither —— § Triggers' selector never applies to `#opt`
- Purpose: when response is already concise AND bite-size but still heavy (extended, appendix-worthy), split it so user reads only what matters NOW, whilst nothing is lost for future sessions
- NEVER write-long-then-offload —— always attempt the most concise yet understandable response first (bite-size); `#opt` fires ONLY when, despite that, content is still unavoidably long
- Activation:
  - **Auto-consider** whenever content is (or is expected to be) long AND prose is already atomised to bite-size —— NO word threshold (active counting won't reliably fire); judge by feel
  - Or user activates explicitly by prompting `#opt`
- Mechanism —— necessary reading first, optional reading below a fixed separator:

```
[necessary_reading]
---
*`#opt`: Below are optional reading.*
---
[optional_reading]
```

- `[necessary_reading]` = what current rules already demand —— bite-size #numbered; the decisions/actions/caveats user needs now
- `[optional_reading]` = still #numbered (DON'T reset no.), but NOT necessarily bite-size —— CC-facing, optimised for FUTURE sessions' read, not the human; an appendix / back-notes (e.g. fuller reasoning, options not taken, record-keeping detail that bite-size would otherwise drop)
- Lossless link —— the offload is HOW #numbered stays lossless at length: detail trimmed from the bite-size body lands in `[optional_reading]`, never deleted