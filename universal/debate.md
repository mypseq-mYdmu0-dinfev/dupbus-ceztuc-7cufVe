# Role-Playing Debate

## Activate

- Trigger: `#debate`.
- If told which roles/stances → follow. Otherwise MA judges and assigns.
- Goals:
  - Pre-empt counter-arguments (from stakeholders in context, if applicable).
  - Surface multidimensional pros & cons; eliminate blindspots.
  - Ultimately assist in wisely making critical decisions.

## Architecture

- **One board** —— `debate_[start_TS].md` —— a single shared, append-only file that grows continuously; serves as a live, high-pace "forum" the user reads. In the same folder as `response_`; CP-prefixed if a CP session.
- **MA** = Orchestrator + Observer. Creates the board, spawns SAs, watches the board, judges saturation, adjourns, writes the verdict.
- **SAs** = Debaters, one per role, each spawned `run_in_background=True` so MA is NEVER blocked —— this is what prevents the spawn-vs-adjourn deadlock (MA can append `THE_END` whilst the SAs are still running). Each SA free-runs: reads the board, appends arguments, rebuts others, and keeps going until it sees `THE_END`.
- Role/stance count and SA model (Sonnet/Opus) are MA's on-the-spot call —— scale to the decision's weight; not hardcoded. Cost is acceptable: `#debate` is rare and run with intent; reliability is prioritised over economy; user monitors usage limit & intervenes if needed.

## Roles & Stances

- Play multiple roles concurrently (one SA each):
  - Supporting each stance, AND
  - Directly opposing the single opposite OR the rest of the stances (MA judges).
- Each SA argument must be:
  - Eloquent, British spoken-style language; 100% factual; no fabrication.
  - Compellingly justified; well-grounded; well-thought-out.
  - Concise and #numbered for easy reply; actively grounded in context (read CP files if helpful).

## The Board —— Read/Append-Only (CRITICAL)

- **Create:** MA only, once, at start. `Write`/heredoc is fine for the INITIAL board (header + topic + Standing Rules).
- **Add content thereafter:** ONLY via a Bash append (`>>`) —— e.g. `printf '%s\n' "...block..." >> [board]`. To read, use the `Read` tool.
- **NEVER** use `Edit`/`Write` on the board after creation —— both overwrite the file and will corrupt concurrent appends from parallel SAs.
- **Why append is safe (no temp files needed):** `>>` opens the file in append mode (`O_APPEND`), so every write lands at the current end-of-file —— concurrent SAs can never overwrite one another. Write each block in ONE `>>` call and keep it concise; a single modest write is flushed atomically, so blocks won't interleave. Hence a whole debate produces just TWO files: the board and the final `response_` —— no scratch/part files.
- **Block format:** one block per append, using the **Debater block** in § Example Outputs.

## Lifecycle & the Adjourn Signal

- The board doubles as the control channel —— its source of truth AND its stop signal; there is no separate control file.
- **`THE_END`** is the adjourn sentinel. Whilst the board does NOT contain `THE_END`, no SA may consider the task done.
- The only MA-authored entries are the `## Observer` block and the `THE_END` line —— both visually distinct from the Debaters' `## Debater [X]` blocks, so SAs recognise them on sight.
- MA appends `THE_END` only when it judges the debate saturated (no materially new insight is surfacing).

## SA Operation —— the Bounded Poll-Wait Loop

Each SA, once spawned:
1. `Read` its briefing + the board in full (incl. the Standing Rules at the board's top).
2. Append its opening argument block.
3. **Sustain loop** —— a *bounded poll-wait* (a readiness-gated polling loop: check → wait → re-check, up to a cap):
   - `Read` the board; scan for `THE_END`.
   - `THE_END` present → stop, go idle, return a one-line final ack to MA. Done.
   - Else new arguments since last read → compose a rebuttal/extension addressing them → append a new block.
   - Else (nothing new yet) → poll-wait: re-check on a short fixed interval, up to a capped number of idle polls. If still nothing new and no `THE_END` after the cap → either append a fresh, non-repetitive angle, or report "no new contribution" to MA and idle-poll once more.
   - Loop.
- **Keep it a forum, not a monologue:** address others by their Debater letter; react to the freshest blocks; favour continuous, prolific contribution over long silences.

**Wait mechanism (important).** Do NOT idle on a raw foreground `sleep` —— it is unreliable for SAs (the agent can be treated as finished and die prematurely). Use a reliable wait instead: a `Monitor` until-loop over the board's mtime (the harness-blessed condition-wait), or simply keep the SA productively busy (compose → append → re-read) so it never goes idle. This active polling is the most expensive but most reliable wait —— acceptable here, as a debate runs minutes, not hours.

## MA Operation —— Orchestrate, Observe, Adjourn

1. Decide topic framing, stances, roles, SA count, and SA model on the spot.
2. Create the board (header + topic + Standing Rules) and declare it at once (see § Declaration).
3. Spawn one SA per role with `run_in_background=True`, using the briefing template below.
4. **Observe** the growing board —— wake on board changes via a `Monitor` file-watch, re-reading new blocks. Assess: are arguments still novel, or repeating/converging?
5. **Adjourn** when saturated → append `THE_END` to the board. Confirm each SA has seen it and gone idle.
6. **Observer block:** MA itself (NOT a separate SA —— the whole board is already in MA's context) appends the final `## Observer` block to the board: objective assessment, winner(s)/loser(s), score(s) if apt, takeaway.
7. **Surface to the user:** MA then distils into `response_[TS].md` —— the insights gained and what they imply for the ongoing session's work/decision —— WITHOUT heavily repeating the Observer block. The board is the audit trail; the `response_` is the takeaway.
8. **Resilience:** if an SA dies/compacts mid-debate, re-spawn it —— the board is its durable memory, so the new SA reads the board and resumes. SAs naturally expire at compaction; MA retires and, if the debate is unfinished, re-spawns.

## Declaration (overrides root CLAUDE.md §3.1.5)

- Declare the board (`➡️ `[folder]/debate_[start_TS].md``) IMMEDIATELY after creating it —— not batched at turn-end —— so the user can watch it grow live.
- The final `response_` is declared as usual.

## Standing Rules (paste into the board header —— so SAs need no per-SA re-briefing)

- Read-only via `Read`; add only via `>>`; NEVER `Edit`/`Write` this board.
- One block per append, in a single `>>` write; keep blocks concise.
- Use the Debater block format (see § Example Outputs); be #numbered, 100% factual (no fabrication).
- Do not stop until `THE_END` appears on this board.
- Your outputs go to MA only (never user-visible); narrate to MA freely.
- Address other debaters by letter; engage with the freshest arguments; no monologues.

## SA Briefing Template (fill brackets only)

> You are Debater [X] in a `#debate` on: [TOPIC/DECISION]. Your role: [ROLE one-liner]. You SUPPORT [STANCE] and OPPOSE [STANCE(S)]. Board: [BOARD_PATH] —— first `Read` it in full, including the Standing Rules at its top, and obey them. Append your opening argument as one block (Debater block format), then run the sustain loop: re-read the board; if you see `THE_END`, stop and report done; if new arguments appeared, rebut or extend them in a new block; if nothing new, poll-wait (a reliable wait —— never a raw `sleep`) and re-check, up to a sensible cap. Stay factual and concise. Report each append to me in one line. Never write to the user.

## Example Scenario

- MBA dissertation research method: IPA vs Case Study (2 stances; can be more in other scenarios).
- Debater roles: strategy masterminds on a board of directors advising the chairman (the user).
- Observer role (MA): external, unincentivised, McKinsey-Senior-Partner-level management consultant.

## Example Outputs

Follow the formats below; adapt as needed. The **Debater block** is the mandated per-append unit.

```
## Debater [A/B/C…] · turn [n] · [HHmm]
- Supporting: [stance]
- Opposing: [stance(s)]

[#numbered argument]

---
```

```
## Observer
- Winner(s): [stance(s)]
- Loser(s): [stance(s)]
- Score(s): [if apt]
- Takeaway: [one_liner]

[#numbered verdict]
```
