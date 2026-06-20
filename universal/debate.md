# Role-Playing Debate

## Activate

- Trigger: `#debate`.
- If told which roles/stances → follow. Otherwise MA judges and assigns.
- Goals:
  - Pre-empt counter-arguments (from stakeholders in context, if applicable).
  - Surface multidimensional pros & cons; eliminate blindspots.
  - Ultimately assist in wisely making critical decisions.

## Architecture

- **One board** —— `debate_[start_TS].md` —— a shared, append-only file that grows live (the "forum" the user reads). Same folder as `response_`; CP-prefixed if a CP session.
- **MA** = Orchestrator + Observer: creates the board, spawns SAs, observes, adjourns, writes the verdict.
- **SAs** = Debaters, one per role, each spawned `run_in_background=True` (so MA is never blocked and can append `THE_END` whilst they run). Each free-runs —— reads, appends, rebuts —— until it sees `THE_END`.
- Role/stance count and SA model (Sonnet/Opus) are MA's on-the-spot call, not hardcoded. `#debate` is rare and run with intent —— reliability over economy; the user watches usage and intervenes if needed.

## Roles & Stances

- Play multiple roles concurrently (one SA each): supporting each stance, AND opposing the single opposite OR the rest (MA judges).
- Every argument: eloquent British spoken-style; 100% factual (no fabrication); well-grounded; concise.

## The Board —— Read/Append-Only (CRITICAL)

- **Create:** MA only, once (`Write`/heredoc is fine for the initial board: header + topic + Standing Rules).
- **Thereafter add ONLY via a Bash append (`>>`); read via the `Read` tool.** Never `Edit`/`Write` the board —— both overwrite and corrupt concurrent appends.
- Append each block in ONE concise `>>` write. `O_APPEND` lands every write at end-of-file, so parallel SAs never clobber each other —— no temp files; a whole debate is just two files, the board and the final `response_`.

## Lifecycle & the Adjourn Signal

- The board is both source of truth and control channel —— no separate control file.
- **`THE_END`** is the sole stop signal. Until it appears, no SA stops; SAs never self-terminate on a turn count.
- Only MA writes the two MA-authored entries —— `THE_END` and the `## Observer` block —— both visually distinct from `## Debater [X]` blocks.

## SA Operation —— Sustain Loop

Each SA, once spawned:
1. `Read` its briefing + the board in full (Standing Rules included).
2. Append its opening block.
3. Loop until `THE_END`:
   - `Read` the board FRESH (never act on a stale read).
   - `THE_END` present → stop, return a one-line ack. (Only `THE_END` ends you.)
   - New opposing block (or a `## User` block) since your last post → append ONE block that DIRECTLY answers the freshest point by its label (`Re B3:`); re-read once more right before appending so you answer the very latest.
   - Nothing new → run the foreground watch-wait (below), then re-read. Don't post just to fill silence.
- Address others by letter; answer rather than monologue.

**Watch-wait (keeps the SA alive; FOREGROUND only).** When nothing is new, block on this as a normal Bash call (`timeout: 45000`), never `run_in_background` (backgrounding makes the SA come to rest and it cannot be resumed):

```
B='[board]'; t=$(stat -f %m "$B"); for i in $(seq 1 10); do sleep 3; [ "$(stat -f %m "$B")" != "$t" ] && break; done
```

It returns within `~`3 s of any board change (new block, `## User`, or `THE_END`), else after `~`30 s —— the cap is only a fallback for a change that lands in the gap before the baseline `stat`. (macOS `stat -f %m`.)

## MA Operation —— Orchestrate, Observe, Adjourn

1. Decide topic, stances, roles, SA count, and model.
2. Create the board (+ declare it at once, see § Declaration).
3. Spawn one SA per role, `run_in_background=True`, via the briefing template.
4. **Observe:** re-read the board (or keep a lightweight background watch on it) for new blocks, saturation, and any `## User` block.
5. **Adjourn:** append `THE_END` ONCE → confirm each SA stops because it read `THE_END` (their acks).
6. **Observer:** append the `## Observer` block (MA is the observer —— the board is already in its context). Do NOT append `THE_END` again.
7. **Surface:** distil the verdict + what it implies for the session into `response_[TS].md` (don't heavily repeat the Observer block). Board = audit trail; `response_` = takeaway.
8. **Resilience:** if an SA dies/compacts mid-debate, re-spawn it —— the board is its memory.

## User Interventions (highest authority)

The user may append a `## User` block at any time (via the template at the bottom). It outranks MA and every SA.
- **MA:** a `## User` block containing `STOP` → adjourn gracefully (append `THE_END` → Observer → `response_`), never a hard-kill. Any other `## User` note → an authoritative steer (e.g. a new angle); let the debate continue along it.
- **SAs:** fold a `## User` steer into the next block; still stop only on `THE_END`.

## Declaration (overrides root CLAUDE.md §3.1.5)

- Declare the board `➡️` IMMEDIATELY after creating it (not at turn-end) so the user can watch it grow. The `response_` is declared as usual.

## Standing Rules (paste into the board header —— SAs inherit them by reading the board)

- Read via `Read`; add only via `>>`; never `Edit`/`Write` this board.
- One concise block per append.
- Re-read FRESH before every block; each non-opening block must directly answer the freshest opposing (or `## User`) point by its label. No stale reads, no monologues.
- Number your points `[YourLetter][n]`, continuing across ALL your blocks and never resetting (A1, A2, A3…); reference others by label (`Re B3:`). This is the debate's own scheme —— not `numbered.md`'s nested `1.1.` style.
- Header `[HHmm]` = the REAL append moment: set it from `TZ='Australia/Sydney' date +%H%M` run immediately before appending; never hardcode or reuse an earlier value.
- Stop ONLY on `THE_END`; never self-terminate on a count.
- A `## User` block is the human moderator (highest authority).
- 100% factual; your outputs go to MA only (never user-visible).

## SA Briefing Template (fill brackets only)

> You are Debater [X] in a `#debate` on: [TOPIC]. Role: [ROLE]. You SUPPORT [STANCE], OPPOSE [STANCE(S)]. Board: [BOARD_PATH] —— `Read` it in full first and obey its Standing Rules. Append your opening block, then loop until `THE_END`: re-read FRESH; if `THE_END`, stop and report; if a new opposing or `## User` block appeared since your last post, append ONE block answering the freshest point by label (`Re B3:`), re-reading once more right before appending; if nothing new, run the foreground watch-wait —— `B='[BOARD_PATH]'; t=$(stat -f %m "$B"); for i in $(seq 1 10); do sleep 3; [ "$(stat -f %m "$B")" != "$t" ] && break; done` as a normal Bash call (`timeout: 45000`, never `run_in_background`) —— then re-read. Number your points [X]1, [X]2… continuing across blocks (never reset); set the header `[HHmm]` from `date +%H%M` immediately before each append. Concise and factual; report each append to me in one line; never write to the user; only `THE_END` ends you.

## Example Scenario

- MBA dissertation method: IPA vs Case Study (2 stances; more is fine).
- Debaters: strategy masterminds on a board of directors advising the chairman (the user).
- Observer (MA): external, unincentivised, McKinsey-Senior-Partner-level consultant.

## Example Outputs

Opening states the stance once; later blocks omit it. `[HHmm]` = real append time; point labels continue per debater.

```
## Debater A · turn 1 · [HHmm]
- A: [stance] (opposing [stance(s)])

A1. [point]
A2. [point]

---
```

```
## Debater A · turn 2 · [HHmm]
A3. Re B2: [direct counter]
A4. [point]

---
```

```
## Observer
- Winner(s): [stance(s)] · Loser(s): [stance(s)] · Score(s): [if apt]
- Takeaway: [one_liner]

1. [verdict point]
2. [verdict point]
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
