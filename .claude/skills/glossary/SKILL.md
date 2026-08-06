---
name: glossary
description: Use when a term, abbreviation or acronym in the user's message or a project file is unfamiliar, ambiguous, or only half-remembered — before acting on a guess. Covers project shorthand such as qb, fof, sic, CIIW, sesL, pcmd, QMM, OTG. Loads the project glossary lookup procedure.
---

Look the term up in `universal/glossary.md` by ESCALATION —— cheapest step first, and stop as soon as the term is settled.

1. Extract and read ONLY that term's line, plus its sub-items if it has any (a sub-item is an indented line beneath it; read on until the next line starting with `- ` or `---` at the term's own indent level). One term costs a few lines, not a file.
2. If still unsure, re-read `universal/glossary.md` in full AND emit the §3.2.6 sentinel from the root `CLAUDE.md`. Rationale: the glossary is an Unconditional, already read at session start —— so needing a FULL re-read is evidence that context was lost, which is exactly what that sentinel exists to declare. Do not skip it because the re-read felt routine.
3. If the term is still unclear after the full re-read, STOP and alert the user. Never proceed on a guessed meaning: this shorthand encodes protocol decisions, so a wrong guess silently executes the wrong protocol.

Never infer a term from resemblance to a common English word or a similar-looking abbreviation elsewhere in the repo.
