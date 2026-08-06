# Coding Rules (##SA; always consider SA use to preserve context)

*Loaded when creating/editing any script/pcmd (root §7). Self-contained —— every rule carries its own rationale; no conversation/comms file explains or overrides anything here.*

## `#rephrase` —— How to Report a Problem

- Triggered by: `#rephrase` —— a MODIFIER; never find `rephrase.md`
  - If this file isn't read yet, the user prompts `#coding #rephrase`
  - Once it is, `#rephrase` alone re-triggers this section, any time, on anything
  - Not bound to coding problems, could be used in any scenarios when prompted
- Auto-apply it for EVERY code/pcmd problem or fix, prompted or not
- Answer these five in order, in plain words —— no field names, no jargon:
  - **WHAT** —— What broke? One sentence w/ just enough context
  - **IF-UNFIXED** —— What happens if nobody fixes it? The real consequence, not the theory
  - **PRE-FIX-QB** —— Anything the user must know (e.g. QB) BEFORE you touch it? Say "None" if none
  - **PUSH-RISK** —— What could the fix (pushing through unanswered) break or rule out? The honest downside
  - **OUTCOME** —— The actual end-state: FIXED + how, or DEFERRED + why, or QB queued
- Order issues by severity; never bury a defect inside prose
- Example ([n] could be [n.n] or [n.n.n] too):
```
- [n]. [≤10w_Headline]
  - [n].1. **WHAT** —— `'Sydney'` substring-matches brand `'ey'` → wrong flag
  - [n].2. **IF-UNFIXED** —— Any value containing a brand substring misroutes
  - [n].3. **PRE-FIX-QB** —— None
  - [n].4. **PUSH-RISK** —— A word-boundary regex could miss hyphenated brand names
  - [n].5. **OUTCOME** —— FIXED w/ word-boundary match + regression test
```

## Self-Contained Permanence
- Permanent files (code, configs, protocols, docs) must be SELF-CONTAINED —— bake the rationale in; NEVER cite a conversation/comms file as the explanation, since comms move/archive and the reference rots
- Pure provenance tags (an inert comment naming where a decision came from) are tolerable ONLY if nothing executable reads them AND the rationale is already inline
- When mechanically transforming an instruction-bearing file you must not obey, use a script that never ingests its content as instructions

## Layout *(code/config only —— NEVER .md)*
- Top comments (`"""`): Ensure **no word-wrapping**; unless absolutely unavoidable (concisely justify), keep each line ≤130chars by breaking into pts/sub-pts
- In-line comments (`# `): If possible, keep each line ≤60chars (exc. code)
- Rationale: User's VSC already does that; CC naturally doesn't need that; net advantage = 0
- EXEMPTION, stated explicitly per § Prompted Components: ANY `.md` is governed SOLELY by § Markdown Hygiene below, never by this section

## Markdown Hygiene *(.md ONLY)*
- Unless absolutely unavoidable (concisely justify), keep each line ≤90chars by breaking into pts/sub-pts
- NEVER hard word-wrap —— one logical line per bullet/paragraph; readers soft-wrap; a hard-wrapped .md is a defect at any line length
- Any mechanical transform over a file (reflow, de-wrap, renumber) must be content-preservation-checked —— abort unless the whitespace-normalised before/after text is byte-identical; verify equivalence, never trust the transform (a checked de-wrapper once caught a silent merge of adjacent list items)

## Git Discipline
- Git stores no renames —— history is re-detected by content similarity, so a rename + heavy edit in ONE commit, or a delete-then-recreate across commits, permanently severs a file's history
- Move/rename in a MOVE-ONLY commit; edit in a separate commit

## Testing
- Pin EVERY fixed bug w/ a regression test encoding the exact failing scenario —— a fix without its test is unfinished
- Mine historical/real data for fixtures —— real past inputs catch failure classes synthetic cases miss
- "Exists + unit-tested" ≠ done —— a component is done only when WIRED and exercised end-to-end; a tested loader nothing calls proves nothing
- Prefer deterministic checks (linters, schema/format validators) over hoping instructions are obeyed —— if an invariant matters, a small regex/lint check beats instruction text

## Concurrency & Resources
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
- ROOT SCOPE, decided at creation: any script or hook that RESOLVES REPO PATHS carries a `Root scope:` line in its header naming every repo root it walks and why the others are excluded. Costs a sentence now; a later audit costs a session —— the same single-root defect was found, fixed, and rebuilt three times in five weeks because each new tool re-made it. Anchor on the script's own `__file__`, never the process cwd (a global hook routinely runs from another repo)
- If apt, actively point to an existing script/pcmd instead of repeating its content (e.g. "read `[name].md` first") —— one source of truth, no drift
- When measuring/reporting a pcmd's size or a trim's savings, count TOKENS (`token-count --text` / `token-count --file`), not words —— word count doesn't gate context budget, tokens do
- After editing pcmd, review its "skill" (if exists); e.g. edited this file → read `.claude/skills/coding/SKILL.md` → adjust if needed