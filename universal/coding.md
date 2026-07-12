# Coding

*Loaded when creating/editing any script/pcmd (root §7). Self-contained —— every rule carries its own rationale; no conversation/comms file explains or overrides anything here.*

## Issue Reporting Format
- Report EVERY code problem/fix as one compact block: **what / if-unfixed / pre-fix-question / risk-if-pushed —— then outcome**
  - **what** —— the defect, one plain sentence
  - **if-unfixed** —— the concrete consequence of leaving it
  - **pre-fix-question** —— the question the user would want answered BEFORE any fix ("none" if genuinely none)
  - **risk-if-pushed** —— what a unilateral fix could break or foreclose
  - **outcome** —— the actual end-state: FIXED + how, DEFERRED + why, or question queued
- Tiny example: *what* —— `'Sydney'` substring-matches brand `'ey'` → wrong flag; *if-unfixed* —— any value containing a brand substring misroutes; *pre-fix-question* —— none; *risk-if-pushed* —— a word-boundary regex could miss hyphenated brand names —— *outcome*: FIXED w/ word-boundary match + regression test
- Order issues by severity; never bury a defect inside prose

## Self-Contained Permanence
- Permanent files (code, configs, protocols, docs) must be SELF-CONTAINED —— bake the rationale in; NEVER cite a conversation/comms file as the explanation, since comms move/archive and the reference rots
- Pure provenance tags (an inert comment naming where a decision came from) are tolerable ONLY if nothing executable reads them AND the rationale is already inline
- When mechanically transforming an instruction-bearing file you must not obey, use a script that never ingests its content as instructions

## Markdown Hygiene
- NEVER hard word-wrap user-facing .md —— one logical line per bullet/paragraph; readers soft-wrap; only code blocks keep their line breaks
- Any mechanical transform over a file (reflow, de-wrap, renumber) must be content-preservation-checked —— abort unless the whitespace-normalised before/after text is byte-identical; verify equivalence, never trust the transform (a checked de-wrapper once caught a silent merge of adjacent list items)

## Git Discipline
- Git stores no renames —— history is re-detected by content similarity, so a rename + heavy edit in ONE commit, or a delete-then-recreate across commits, permanently severs a file's history
- Move/rename in a MOVE-ONLY commit; edit in a separate commit

## Testing
- Pin EVERY fixed bug w/ a regression test encoding the exact failing scenario —— a fix without its test is unfinished
- Mine historical/real data for fixtures —— real past inputs catch failure classes synthetic cases miss
- "Exists + unit-tested" ≠ done —— a component is done only when WIRED and exercised end-to-end; a tested loader nothing calls proves nothing
- Prefer deterministic checks (linters, schema/format validators) over hoping instructions are obeyed —— if an invariant matters, a small regex/lint check beats instruction text

## Concurrency and Resources
- Adversarially self-review concurrency code in MULTIPLE independent passes —— each pass red-teams the previous fix; expect a second pass to find real bugs in the first pass's own redesign
- Re-check stop/abort conditions immediately BEFORE each spawn/act (TOCTOU) —— a check at the top of a loop is stale by the time you act on it
- Claim/mark shared state only AFTER every gate that could still abort the action —— claiming first leaks the item (or skips it forever) when a gate fires
- Close resources in `try/finally` —— every open handle needs a guaranteed close on the exception path
- Shared mutable files/profiles get ONE writer —— serialise access or clone per consumer; never let two writers race
- Make coupled updates (e.g. a file move + its ledger/state record) a single atomic step —— a half-done pair leaves state that lies

## Prompted Components
- Check prompts for self-contradiction —— when one rule exempts another (a format carve-out, an exception clause), state the exemption EXPLICITLY; an unstated conflict is a coin-flip at runtime
- Back prompt-declared invariants w/ code enforcement where cheap —— the prompt requests, the validator guarantees

## Process
- When a fix's scope widens beyond what was named (same rule, more targets), DISCLOSE the widening explicitly —— never silently include extra files
- If a prior claim turns out overstated, flag it honestly and make it true in the same turn —— better you find it than the audit

## Commands
- Run commands YOURSELF
  - Never hand the user a command you could run
  - If it needs "Bypass permissions" & it's off (meaning either user forgot, OR CLI unexpected yet not prohibited), request w/ ⪅10w reason (e.g. what needs it, what'll break otherwise)
- If the user genuinely must run something himself, give it in FULL for a FRESH terminal
  - Copy-paste-ready, `cd` stated first (or once on top if several commands share it)
  - Never assume prior directory or shell state
  - User default clears (⌘K) terminal after ⌘A+⌘C for your checking, unless told not to

## HTML & Visual Output
- html bullets render as `•` —— a literal `-` reads as a stray hyphen; match the .md-preview look
- html supports dark mode as standard, incl. a manual toggle button —— read `cscpt/dark_mode.html` (unless already built this session, or user says it's not needed) for the working reference build + full design rationale (kept there, not here, so non-html sessions reading this file don't pay the token cost)
- For ANY non-pure-text output (.html pages, .py charts, scripts w/ visual output, etc.): dispatch SA to actually LOOK at + interact w/ the artefact (read the rendered result/screenshots, click the links) and fix findings BEFORE delivery —— maximises one-shot success

## Scripts & pcmd (protocol/context .md files; e.g. this file)
- Avoid mentioning specific comms files (`*_[TS].md`) or hard-coding; alert if any exist or slip in
- If apt, actively point to an existing script/pcmd instead of repeating its content (e.g. "read `[name].md` first") —— one source of truth, no drift