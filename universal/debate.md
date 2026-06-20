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
- **`THE_END`** is the adjourn sentinel and the ONLY thing that stops an SA. Whilst the board does NOT contain `THE_END`, no SA may consider the task done; SAs never self-terminate on a turn count.
- The only MA-authored entries are the `## Observer` block and the `THE_END` line —— both visually distinct from the Debaters' `## Debater [X]` blocks, so SAs recognise them on sight.
- MA appends `THE_END` only when it judges the debate saturated (no materially new insight is surfacing) —— or immediately on a user `STOP` (see § User Interventions).

## SA Operation —— the Bounded Poll-Wait Loop

Each SA, once spawned:
1. `Read` its briefing + the board in full (incl. the Standing Rules at the board's top).
2. Append its opening argument block.
3. **Sustain loop —— repeat until `THE_END`:**
   - `Read` the board FRESH —— always re-read immediately before you decide or compose; never act on a stale read. This is what keeps the forum genuinely responsive.
   - **`THE_END` present** → stop at once, go idle, return a one-line final ack to MA. Done. (`THE_END` is the only terminator —— never quit on a self-imposed count.)
   - **A `## User` block present** → the human moderator (highest authority); fold its steer (e.g. a new angle) into your next block. You still stop only on `THE_END`.
   - **New opposing block since your last post** → compose a block that DIRECTLY engages the freshest opposing argument(s) —— name the debater and the exact point you are answering. Then re-read ONCE more to confirm nothing newer landed; if it did, fold it in or re-target; then append. Every non-opening block MUST be a response, never a blind monologue.
   - **Nothing new since your last post** → poll-wait (reliable wait; see below) and re-check. Do NOT fill the silence with a fresh block unless you have first answered all current opposing points AND are genuinely adding a new, non-repetitive angle. After several idle polls with no new material and no `THE_END`, report "idle —— awaiting new material or `THE_END`" to MA and keep polling at a slower cadence. Never exit.
- **Forum discipline:** address others by their Debater letter; build on the freshest blocks; prefer answering over racing ahead.

**Wait mechanism (important).** Do NOT idle on a raw foreground `sleep` —— it is unreliable for SAs (the agent can be treated as finished and die prematurely). Use a reliable wait instead: a `Monitor` until-loop over the board's mtime (the harness-blessed condition-wait), or simply keep the SA productively busy (compose → append → re-read) so it never goes idle. This active polling is the most expensive but most reliable wait —— acceptable here, as a debate runs minutes, not hours.

## MA Operation —— Orchestrate, Observe, Adjourn

1. Decide topic framing, stances, roles, SA count, and SA model on the spot.
2. Create the board (header + topic + Standing Rules) and declare it at once (see § Declaration).
3. Spawn one SA per role with `run_in_background=True`, using the briefing template below.
4. **Observe** the growing board —— wake on board changes via a `Monitor` file-watch, re-reading new blocks. Assess: are arguments still novel, or repeating/converging? Watch also for any `## User` block (see § User Interventions).
5. **Adjourn** when saturated → append `THE_END` to the board. Then CONFIRM each SA actually stops because it read `THE_END` (re-read for their final acks / idle) —— the stop must come from `THE_END`, not from an SA finishing on its own.
6. **Observer block:** MA itself (NOT a separate SA —— the whole board is already in MA's context) appends the final `## Observer` block to the board: objective assessment, winner(s)/loser(s), score(s) if apt, takeaway.
7. **Surface to the user:** MA then distils into `response_[TS].md` —— the insights gained and what they imply for the ongoing session's work/decision —— WITHOUT heavily repeating the Observer block. The board is the audit trail; the `response_` is the takeaway.
8. **Resilience:** if an SA dies/compacts mid-debate, re-spawn it —— the board is its durable memory, so the new SA reads the board and resumes. SAs naturally expire at compaction; MA retires and, if the debate is unfinished, re-spawns.

## User Interventions (highest authority)

The user may append their own block to the board at any time —— a block whose first line begins `## User` (via the copy-paste template at the very bottom of this file). The user outranks MA and every SA.
- **MA, on seeing a `## User` block:**
  - If it contains `STOP` (the all-caps token) → adjourn GRACEFULLY; do NOT hard-kill the run or end the turn abruptly. Append `THE_END`, confirm the SAs stop, append the `## Observer` block, and write the `response_` summary. (Closing it properly is exactly why the user posted `STOP` here instead of killing the background tasks themselves.)
  - Otherwise (a moderation/steer, e.g. a new angle to explore) → treat it as authoritative direction: let the SAs continue along it and adjust your own observation accordingly.
- **SAs, on seeing a `## User` block:** treat it as the highest-authority steer —— fold it into your next block. You still terminate only on `THE_END`.

## Declaration (overrides root CLAUDE.md §3.1.5)

- Declare the board (`➡️ `[folder]/debate_[start_TS].md``) IMMEDIATELY after creating it —— not batched at turn-end —— so the user can watch it grow live.
- The final `response_` is declared as usual.

## Standing Rules (paste into the board header —— so SAs need no per-SA re-briefing)

- Read-only via `Read`; add only via `>>`; NEVER `Edit`/`Write` this board.
- One block per append, in a single `>>` write; keep blocks concise.
- Re-read the board FRESH before every block; each non-opening block must DIRECTLY engage the freshest opposing (or `## User`) content —— name what you answer. Never rebut from a stale read; no monologues.
- Stop ONLY when `THE_END` appears —— never self-terminate on a turn count.
- A `## User` block is the human moderator (highest authority) —— fold its steer into your next block.
- Use the Debater block format (see § Example Outputs); be #numbered, 100% factual (no fabrication).
- Your outputs go to MA only (never user-visible); narrate to MA freely.

## SA Briefing Template (fill brackets only)

> You are Debater [X] in a `#debate` on: [TOPIC/DECISION]. Your role: [ROLE one-liner]. You SUPPORT [STANCE] and OPPOSE [STANCE(S)]. Board: [BOARD_PATH] —— first `Read` it in full, including the Standing Rules at its top, and obey them. Append your opening argument as one block (Debater block format). Then run the sustain loop until you see `THE_END`: re-read the board FRESH every cycle; if `THE_END` is present, stop and report done; if a new opposing block (or a `## User` block) has appeared since your last post, append a block that DIRECTLY engages it —— name the debater/point you answer —— re-reading once more right before appending so you respond to the very latest; if nothing new, poll-wait (a reliable wait —— never a raw `sleep`) and re-check. Never rebut from a stale read, never monologue, and never self-terminate on a turn count —— only `THE_END` ends you. Stay factual and concise; report each append to me in one line; never write to the user.

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

---

## User Intervention Template —— ONLY for the user (MA & SAs: ignore this entire section)

- MA and SAs never read, act on, or quote this section.
- This is purely a copy-paste helper for the human user, who outranks everyone.
- If you want to steer or stop a live debate without waiting for MA (who may be mid-run and unresponsive until closure):
  - Copy the block below
  - Edit `MSG`
  - Run in terminal
- It appends a highest-authority `## User` block to the live board.
- Include the all-caps word `STOP` in `MSG` to make MA adjourn gracefully (`THE_END` + Observer + `response_`); omit it to act as a moderator and add a new angle.

---

```bash
# Auto-pick the newest debate board (or set BOARD="/abs/path/to/debate_[TS].md" to override):
BOARD="$(ls -t "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/sessions"/*/*/debate_*.md | head -1)"

# Edit your message:
MSG="STOP —— wrap up now and give me the Observer verdict."

# Moderator example (no stop): MSG="New angle —— evaluate this for a 3-person startup."

# Append (append-only; safe alongside MA/SAs):
printf '\n## User · %s\n%s\n\n---\n' "$(TZ='Australia/Sydney' date +%H%M)" "$MSG" >> "$BOARD"
echo "Posted to: $BOARD"
```