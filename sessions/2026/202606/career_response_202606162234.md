# Response to career_query_202606162234.md
*Memory unlocked in §8.6; why not to migrate c.md*

56. Re 51.7 —— done.
- 56.1. Edited CLAUDE.md §8.6: the memory store is now READ-free; create/edit/delete only on explicit `override`; and CC MAY SUGGEST (await approval, never execute unprompted) a memory write when it detects something of lasting value or critical to know about you. Reworded for fit —— see §8.6.
- 56.2. I will hold to "suggest, not execute" by default, so expect me to occasionally flag "worth remembering?" rather than silently writing.

57. Side Question —— yes, memory is system-surfaced rather than actively read; and most of CLAUDE.md should NOT move into it.
- 57.1. Mechanics: MEMORY.md (the index) is auto-loaded into context every session, and the individual files are RECALLED by the system into `<system-reminder>` blocks when their description matches what is relevant. So they "smartly surface" by relevance —— I do not Read them with the tool, which is exactly why no ✅ appeared and why past sessions (including the false one) acted on them silently. You read the behaviour correctly.
- 57.2. They arrive as background context, not active reads, and are point-in-time —— advisory, and able to go stale (the false path-depth memory is the proof). That staleness is itself an argument against putting hard rules in memory.
- 57.3. Migration is mostly inadvisable, for two structural reasons:
  - 57.3.1. Determinism: CLAUDE.md is ALWAYS in full context, every turn; memory only PROBABLY surfaces when judged relevant. Hard protocol (initiation, comms discipline, file rules) must stay deterministic —— if it lived only in memory it could silently fail to surface.
  - 57.3.2. Portability: memory is machine-local (this WSM only, `~/.claude`). CLAUDE.md lives in the repo and travels to every machine and surface —— OTGM, OTGD, cloud, CWI, CAI. Anything needed off this Mac MUST stay in the repo.
- 57.4. On your §9 example —— it is the wrong direction. §9.1 calls `cscpt/set_dates.py`, a repo tool runnable from any machine, and §8.8.4 literally branches on WSM versus OTGM. Those are cross-machine, so they belong in the repo, not in a WSM-only store.
- 57.5. Net: keep CLAUDE.md as the constitution (deterministic, versioned, cross-machine) and let memory be field notes (evolving personal facts, preferences, feedback), which is already what it holds. Little to nothing in CLAUDE.md is both WSM-only AND safe to make merely-recalled, so I would not migrate.
