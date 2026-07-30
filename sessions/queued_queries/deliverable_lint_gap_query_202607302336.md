# Deliverable Lint Has No Enforcement Outside Comms Files

## Context (pointer only, NOT truth —— verify everything yourself)
- Root CLAUDE.md §3.7.3: "ANY deliverable: MUST follow `writing.md` & run `dlint.py` before output to user."
- `writing.md`'s Deliverable Lint section: separate-file deliverables get FULL-mode `python3 cscpt/dlint.py <path>`.
- This is a written rule with (as far as this session found) no mechanical backstop for the specific case below.

## What Happened
- Career CP session built `temp/temp_int/20260625_Alltech/output/CHEATSHEET_Stage3.md` —— a genuine deliverable (sent to the user via `SendUserFile`, meant to be read verbatim before a real interview).
- It was drafted, debated twice (`#debate`, content-quality only), rewritten, and sent —— without ever running FULL `dlint.py` on it.
- User caught this later and asked for it to be fully linted retroactively. Running it found 18 RED flags (em dashes, mid-sentence colons needing full restructure) plus 20⁺ YELLOW flags —— i.e. real, load-bearing writing-rule breaches, not a formality.
- Root cause, checked directly: the two hooks that exist don't cover this file.
  - `dlint_quick.py` (PostToolUse) only fires "on a CC-authored comms write" (per `cscpt/README.md`) —— the 5 types in root §3.3 (`query_`/`response_`/`close_`/`wrap_`/`artefact_`). A cheat sheet in `temp/*/output/` is none of those, so it never fired.
  - `plint.py` (PreToolUse) is meant to remind CC to read a governing protocol before writing "a script, pcmd or letter-like file" —— it fired (misfiringly) on plain data files elsewhere this session (the AR, `CP_notes.md`, `backlog.md`) but never fired at all on this cheat sheet, so its file-type detection doesn't catch this category either.
- Net: for this exact shape of file (a genuine prose deliverable, non-comms, sitting under `temp/`), the ONLY enforcement of §3.7.3 is CC's own memory of an explicit written rule, with zero mechanical surfacing at the moment of the write. Per `cp/ccsim/CLAUDE.md` §8.7's own diagnostic framework, this is a NOT-NOTICED gap (an enforcement gap), not a misapplied rule —— restating the words in root CLAUDE.md again would not have prevented this; the rule was already there, clearly, and still didn't fire at the point of action.

## Why This Is Worth Fixing (not just this one file)
- Any future non-comms deliverable (a cheat sheet, a one-pager, a script for a call, anything written FOR a third party or for the user's own verbatim use) shares this exact blind spot.
- CCSIM's own Operating Posture (§8.1) states the house rule directly: "prefer a lint, hook, or default that makes the wrong move hard over an instruction that asks for the right one" —— this case is precisely that principle unmet.

## Candidate Fix Directions (for the receiving session to weigh, not decided here)
1. Extend `dlint_quick.py` (or a new lightweight hook) to also fire FULL-mode on any Write/Edit whose target isn't a comms file but matches an "output deliverable" shape —— e.g. under `temp/*/output/`, or a filename pattern like `CHEATSHEET_*`/similar known deliverable conventions. Risk: false positives on genuinely-internal working files that happen to sit in similar folders; would need a clear allow/deny shape.
2. A cheaper, less precise option: a PreToolUse advisory (like `plint.py`, non-blocking) that fires on ANY Write under `temp/*/output/` reminding CC to run `dlint.py` FULL before it's sent anywhere —— lower engineering cost, keeps a human/CC judgement call rather than a hard gate.
3. If neither is wanted: at minimum, log this as a known blind spot somewhere CC re-reads regularly (e.g. `writing.md` itself, right next to §3.7.3), since the current phrasing alone evidently isn't enough to survive a busy multi-task turn.

## Reminders
- Not fixed by this file —— it exists to hand the investigation/fix to a session with the right context/tools for hook changes, per `cscpt/README.md`'s ownership rule (CCSIM by default; another CC may fix small things in passing but must record it here regardless).
- The cheat sheet itself has since been fully linted (RED=0) and re-sent; this query is about the process gap, not that specific file's content.
