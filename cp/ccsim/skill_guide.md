# Skill Guide —— House Style for Skill Descriptions

*Read before creating, editing, or auditing any `.claude/skills/*/SKILL.md`. Self-contained: every rule carries its own rationale, so no conversation or comms file is needed (or permitted) to explain it.*

> **Standing convention —— guide files in `cp/ccsim/` are named `*_guide.md`.** Any document in this folder whose job is to GUIDE how something is written or built takes that suffix: `skill_guide.md` (this file) for skill descriptions, `hook_guide.md` for hooks, `ssd_migration_guide.md` for the SSD migration procedure. Name every future guide the same way. The point is that the folder stays self-describing —— a reader can tell a guide apart from an index, a log, a playbook, or a backlog by filename alone, without opening anything. A merely clever name tells a newcomer nothing; the shared suffix is what makes the set legible at a glance.

---

## 1. Why the Description Is the Only Thing That Costs

- A skill has two halves with two very different price tags: the **frontmatter** (`name` + `description`) is injected into the SYSTEM PROMPT on EVERY turn of EVERY session; the **body** is loaded only when the skill is actually invoked.
- So the description is the ONLY standing cost. The body is free until used —— which is why depth belongs in the pcmd the body points to, never in the description.
- The skill listing is budget-capped at roughly **1% of the context window** (~2,000 tokens on a 200k window), and that cap is shared by project skills, plugin skills, and built-ins alike. Descriptions therefore COMPETE: every token one spends is a token another cannot have, and an over-budget listing gets truncated rather than negotiated.
- **The cap is a per-turn CEILING, not a running total.** The listing is assembled once into the system prompt, so it costs the same on turn 50 as on turn 1 —— it does NOT accumulate as a session lengthens. The sting is the other half of that sentence: you pay it on EVERY turn of EVERY session, including the majority in which no skill fires at all.
- **Over budget, the harness shortens rather than asks.** Two limits bite independently: `skillListingMaxDescChars` (default 1,536 characters) truncates any single over-long description, whilst `skillListingBudgetFraction` (default `0.01`) governs the shared 1% —— once the total exceeds it, descriptions are mechanically shortened to fit, and in the worst case skills drop out of the listing altogether. Both are raisable in `settings.json`, but raising them only relocates the cost onto every turn; it never removes it.
- That loss is SILENT —— exactly like the YAML `#` truncation of §4.3, the file still looks perfect on screen whilst the model sees a stub, and a description that arrives shortened is a skill that cannot reliably fire. So treat description length as a **shared, finite resource**: every character you spend is one a sibling cannot have, and brevity is a courtesy owed to every other skill in the listing —— including the built-ins you cannot edit and the ones you did not write.
- Measure, don't guess: concatenate every `name: description` line into one file and run `token-count --file <path>` (word count doesn't gate context budget, tokens do). Measured at the time of writing: 16 project skills = 991 tokens, roughly HALF the cap, before a single plugin or built-in skill is counted. There is no slack to be casual with.
- Working target: **≤300 characters (~65 tokens)** per description. Past ~400 you are crowding a sibling out, so spend the extra length only where it demonstrably buys matchability (see §3).

## 2. Skills Do NOT Replace the §7.2 Table

- Root `CLAUDE.md` §7.2 (conditional-read table) is a GUARANTEED read: a stated condition is met, the file is read, full stop. A skill match is PROBABILISTIC —— the model decides, and it can decide wrong.
- The two are belt-and-braces. Never delete a §7.2 row because a skill now exists, and never assume the skill will fire in place of the table.
- The `hlint` hook (UserPromptSubmit) already scans every prompt for literal `#trigger` tokens and injects a reminder to read the matching pcmd. So the manual path is covered three ways over.
- The skill's real job is the **unprompted** case: the user never types the trigger, never names the file, and just describes a task. Write the description for that user.

## 3. The Hybrid Shape (Mandatory)

Every description is three parts, in this order:

```
Use when <concrete task-shape> — <short tail of concrete trigger words in the user's own vocabulary>. Loads <what the body pulls in>.
```

- **Use-when clause** —— the gate. Supplies the WHEN, so the skill doesn't fire on a passing mention.
- **Concrete tail** —— the match surface. Supplies the WHAT-IT-LOOKS-LIKE, so the skill fires at all.
- **Payload clause** —— tells the model what it gains by paying the body's cost, so a borderline call resolves on evidence rather than on the name alone.
- Why hybrid and not either extreme: a pure keyword list has no WHEN, so it over-fires on any incidental mention (cost = a wasted body read plus a derailed turn); pure abstract prose has no match surface, so it never fires at all (cost = the entire skill, silently). One failure is noisy, the other is invisible —— which makes the abstract one worse.
- Write the tail in the **user's** vocabulary, not the system's. The description is matched against what the user actually typed, and users say "which laptop should I get", never "I am engaging in a spending activity".
- Add a **negative clause** when over-firing is likely or expensive: e.g. "not routine or low-stakes questions", "not the lint hooks (they run themselves)". One clause of exclusion is cheaper than a wrong invocation.
- Add a **boundary clause** when a sibling skill is nearby: e.g. "use career-bg for career work". This is what keeps §4.4 from happening.
- Punctuation: descriptions use a single spaced `—`, not the house doubled ` —— ` of root §2.4. Descriptions are machine-facing match text, the doubled dash costs standing budget on every turn and buys nothing in matching, and all existing SKILL.md files already read this way. Prose in a skill BODY follows the normal house style.

## 4. Anti-Patterns

Each fails for a specific reason. Learn the reason, not just the shape.

- **4.1. Abstract category description.** e.g. "Use when the user's PERSONAL background is needed". This NEVER fires: nobody phrases a request that way, so the model must first infer that an invisible thing "is needed" before it can match —— an inference it has no cue to make. Write the SITUATIONS instead: asking for a recommendation, anything that turns on his home, devices, location, or constraints.
- **4.2. Restating the pcmd's own manual trigger.** e.g. "or when the user asks to review `ftv.md`", "when `#buy` is prompted". If the user typed the trigger or named the file, the file is already being read —— by §7.2, by `hlint`, or simply because it was named. The clause adds nothing and bills the whole context window for it, every turn.
- **4.3. Writing `#name` inside a description.** Two independent reasons, either one fatal:
  - Redundancy —— `hlint` already catches every literal `#trigger` and points at the pcmd, so the clause is dead weight (§4.2).
  - MECHANICAL TRUNCATION —— in YAML, a ` #` inside an unquoted scalar starts a COMMENT. Everything from the `#` to end of line is silently discarded before the model ever sees it. The `google` skill lost 51% of its description this way (134 chars authored, 65 surviving: the listing read "…or calendar operations, or when" and simply stopped), and nothing warns you —— the file looks perfect on screen.
  - If a `#` is ever genuinely unavoidable, the entire description must be wrapped in quotes. Prefer removing it.
- **4.4. Two skills claiming the same job.** Either both fire (two body reads, two protocols competing for the same turn) or the model picks the wrong one and the right one never runs. Give the more specific skill ownership and give the other an explicit boundary clause (e.g. `personal-bg` says "use career-bg for career work").
  - COMPLEMENTARY skills are not this defect: `buy` supplies the research protocol and `personal-bg` supplies who the buyer is, so both firing on "which laptop should I get" is correct. The test is whether they offer the SAME payload for the same request, not whether they co-occur.
- **4.5. Padding the description with what belongs in the body.** Procedure, caveats, and rules cost nothing in the body and cost every turn in the description. If a sentence does not help the model DECIDE, it goes in the pcmd.

## 5. Body Rules (Thin Pointer)

- The body is a POINTER, not a copy: `Read <path> in full and follow it for the current task.` Duplicating the pcmd's rules guarantees drift, and drift means two sources of truth and no way to tell which is stale.
- Every body must name its target file by path, and that path must be verified to exist whenever the skill is touched (§6). A skill whose target has moved fails at the worst moment: mid-task, after the model has already committed to using it.
- **Propose-first.** If the skill starts a LARGE or hard-to-reverse operation —— multi-agent runs, sustained behavioural commitments, bulk rewrites, recursive file operations, anything driving the user's GUI —— the body MUST instruct proposing it to the user (what it entails plus rough cost) and awaiting explicit approval, instead of auto-running. The description's job is to make the skill FIRE; the body's job is to stop a correct firing from becoming an unwanted action.
- Keep the standing note that the manual `#trigger` / §7.2 path still applies, so nobody later "tidies up" the guaranteed read on the assumption the skill replaced it (§2).

## 6. Before Saving —— Validate

- [ ] Frontmatter parses: `---` fence, `name` + `description`, nothing else.
- [ ] The description SURVIVES parsing intact —— verify by parsing, never by eyeballing (§4.3).
- [ ] `name` equals the folder name; lower-case, hyphens only.
- [ ] Shape check: Use-when clause / concrete tail / payload clause, ≤300 chars where it can be.
- [ ] The tail's distinctive words appear in no other skill's tail (§4.4).
- [ ] The target file exists at the stated path.
- [ ] Propose-first clause present if the operation is large or hard to reverse.

Boxes 1–3 and 6 are mechanical, so a script enforces them rather than your eyes (a deterministic check beats hoping an instruction is obeyed). Run it after ANY skill edit:

```zsh
cd "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
python3 cp/ccsim/sandbox/skill_desc_regression_test.py
```

It fails loudly on an unquoted ` #` truncation, a `name` that doesn't match its folder, and a body pointing at a file that no longer exists; it is dependency-free, because PyYAML is not installed system-wide on this Mac. Then price the whole listing (`name: description`, one line each, concatenated into a file) with `token-count --file` and compare against §1's budget.

## 7. Changing a Description Is a Behavioural Change

- A description edit changes when the skill fires in every future session, and the effect is not visible from reading the file —— only from running it.
- `cp/ccsim/CLAUDE.md` §4 (Change Simulation QA) therefore applies: actively propose blind A/B sub-agents on the SAME scenario, one fed the new description and one the old, neither told of the change, then improve from what actually happened.
- A description that has never fired in practice is a BUG report, not a matter of taste —— diagnose it against §4 before rewriting, so the rewrite fixes the cause rather than reshuffling the words.
