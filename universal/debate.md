# Role-Playing Debate

## Activate

- Trigger: `#debate`.
- If told which roles/stances → follow; otherwise, MA judges and assigns.
- Goals:
  - Pre-empt counter-arguments (from stakeholders in context, if applicable).
  - Surface multidimensional pros & cons; eliminate blindspots.
  - Ultimately assist in wisely making critical decisions.

## Architecture

- **One board** —— `debate_[start_TS].md` —— a shared, append-only file that grows live (the "forum" the user reads). Same folder as `response_`; CP-prefixed if a CP session.
- **Debater SAs** —— one per role, each spawned `run_in_background=True`. Each free-runs —— reads, appends, rebuts —— until it sees `THE_END`.
- **MA** —— sets roles/stances (ALWAYS MA: it alone holds full session context, and a wrong call here wastes the whole run), creates + declares the board, spawns the SAs, makes the final saturation call, and writes `THE_END` + the `## Observer` verdict + the `response_`.
- **Observe mode —— MA's on-the-spot choice:**
  - **Hybrid (default):** MA also spawns a light **Observer SA** that watches the board and digests it for MA, keeping MA's context free for you and other tasks. MA keeps the final saturation/verdict call. Adds one small internal file (the digest channel).
  - **MA-as-observer:** on a large-context session, a short focused run, or whenever an Observer SA isn't worth it, MA watches the board itself —— keeping it to two files (board + `response_`).
- Role/stance count and SA model (Sonnet/Opus) are MA's on-the-spot call, not hardcoded. `#debate` is rare and run with intent —— reliability over economy; the user watches usage.

## Roles & Stances

- Play multiple roles concurrently (one SA each): supporting each stance, AND opposing the single opposite OR the rest (MA judges).
- Every argument: eloquent British spoken-style; 100% factual (no fabrication); well-grounded; concise.

## The Board —— Read/Append-Only (CRITICAL)

- **Create:** MA only, once (`Write`/heredoc is fine for the initial board: header + topic + Standing Rules).
- **Thereafter add ONLY via a Bash append (`>>`); read via the `Read` tool.** Never `Edit`/`Write` the board —— both overwrite and corrupt concurrent appends.
- Append each block in ONE concise `>>` write. `O_APPEND` lands every write at end-of-file, so parallel writers never clobber each other —— no temp files.
- Files: MA-as-observer mode → two (board + `response_`). Hybrid mode → three (+ the digest channel `debate_[start_TS]_obs.md`, a small internal SA→MA file).

## Lifecycle & the Adjourn Signal

- The board is both source of truth and control channel —— no separate control file for stopping.
- **`THE_END`** is the sole stop signal; only MA writes it. Until it appears, no SA stops; SAs never self-terminate on a turn count. MA's adjourn (THE_END on the board) reaches the debaters AND the Observer SA at once —— so MA never needs to message an SA directly.
- The only MA-authored board entries are `THE_END` and the `## Observer` block —— both visually distinct from `## Debater [X]` blocks.

## Debater SA —— Sustain Loop

Each debater SA, once spawned:
1. `Read` its briefing + the board in full (Standing Rules included).
2. Append its opening block.
3. Loop until `THE_END`:
   - `Read` the board FRESH (never act on a stale read).
   - `THE_END` present → stop, return a one-line ack. (Only `THE_END` ends you.)
   - New opposing block (or a `## User` block) since your last post → append ONE block that DIRECTLY answers the freshest point by its label (`Re B003:`); re-read once more right before appending so you answer the very latest.
   - Nothing new → run the foreground watch-wait (below), then re-read. Don't post just to fill silence.
- Address others by letter; answer rather than monologue.

**Watch-wait (keeps the SA alive; FOREGROUND only).** When nothing is new, block on this as a normal Bash call (`timeout: 45000`), never `run_in_background` (backgrounding makes the SA come to rest and it cannot be resumed):

```
B='[board]'; t=$(stat -f %m "$B"); for i in $(seq 1 10); do sleep 3; [ "$(stat -f %m "$B")" != "$t" ] && break; done
```

It returns within `~`3 s of any board change, else after `~`30 s (the cap is a fallback for a change that lands in the gap before the baseline `stat`). macOS `stat -f %m`.

## Observer SA (hybrid mode only)

A light SA spawned `run_in_background=True`, briefed to WATCH and DIGEST —— never to debate or write the verdict. It runs the same foreground watch-wait (above) but capped at `~`15 s (`seq 1 5`), and stops on `THE_END`. On each board change it appends to the digest channel `debate_[start_TS]_obs.md` (append-only `>>`):
- ONE `≤20-word` digest of the new entry —— debater letter + the gist of the new point + a `[new]` or `[rehash]` tag (so MA can smell saturation from the digests alone, without re-reading the board).
- A `## User` block's digest is prefixed `USER:` so MA catches interventions at once.
- When arguments stop advancing (recycling, circling, a run of `[rehash]`), append `SATURATION? —— [one-line why]`.
- On a quiet 60 s heartbeat, note any debater that looks dead/stalled.
- At `THE_END` (or when it flags saturation), append a FINAL REPORT: the outcome, what was weighed, the block HEADINGS MA may want to read, and whether MA should read the whole board.

## MA Operation —— Orchestrate, Observe, Adjourn

1. Decide topic, stances, roles, SA count, model, AND observe mode.
2. Create the board (header + topic + Standing Rules) and declare it at once (see § Declaration). Keep the literal word `STOP` OUT of the board text, so a stop-watcher can't false-match.
3. Spawn one Debater SA per role (`run_in_background=True`); in hybrid mode also spawn the Observer SA.
4. **Observe:**
   - **Hybrid:** watch the DIGEST channel (not the board) on a `~`15 s change-poll + a `~`60 s heartbeat. Read new digest lines: act on a `USER:` line, and INDEPENDENTLY judge saturation as a guard —— MA may adjourn even if the Observer SA hasn't flagged it (the light SA can miss it). Watchdog: every `~`300 s confirm the Observer SA is alive (recent digest activity); re-spawn it if dead.
   - **MA-as-observer:** watch the board directly (`~`15 s + `~`60 s), reading new turns and judging saturation.
5. **Adjourn** (on saturation, or a `## User` `STOP`) → append `THE_END` ONCE to the board → confirm each SA stops because it read `THE_END`.
6. **Observer block:** read the board —— selectively, guided by the Observer SA's heading list, or in full if the verdict warrants —— then append the `## Observer` block. Do NOT append `THE_END` again.
7. **Surface:** distil the verdict + what it implies for the session into `response_[TS].md` (don't heavily repeat the Observer block). Board = audit trail; `response_` = takeaway.
8. **Resilience:** re-spawn any debater (or the Observer SA) that dies mid-debate —— the board and digest channel are durable memory.

## User Interventions (highest authority)

The user may append a `## User` block to the board at any time (via the template at the bottom). It outranks MA and every SA.
- **MA:** a `## User` block containing `STOP` → adjourn gracefully (append `THE_END` → Observer → `response_`), never a hard-kill. Any other `## User` note → an authoritative steer (e.g. a new angle); let the debate continue along it.
- **SAs:** fold a `## User` steer into the next block; still stop only on `THE_END`.

## Declaration (overrides root CLAUDE.md §3.1.5)

- Declare the board `➡️` IMMEDIATELY after creating it (not at turn-end) so the user can watch it grow. The `response_` is declared as usual.

## Standing Rules (paste into the board header —— SAs inherit them by reading the board)

- Read via `Read`; add only via `>>`; never `Edit`/`Write` this board.
- One concise block per append.
- Re-read FRESH before every block; each non-opening block must directly answer the freshest opposing (or `## User`) point by its label. No stale reads, no monologues.
- Number your points `[YourLetter][3-digit]`, continuing across ALL your blocks and never resetting. Write EVERY point as its own bullet, indented 2 spaces per sub-level, so lines never collapse together: `- A001. …`, then `  - A001.1. …`, then `    - A001.1.1. …`. Reference others by label (`Re B003.2:`).
- Header `[HHmm]` = the REAL append moment: set it from `TZ='Australia/Sydney' date +%H%M` run immediately before appending; never hardcode or reuse an earlier value.
- Stop ONLY on `THE_END`; never self-terminate on a count.
- A `## User` block is the human moderator (highest authority).
- 100% factual; your outputs go to MA only (never user-visible).

## Debater-SA Briefing Template (fill brackets only)

> You are Debater [X] in a `#debate` on: [TOPIC]. Role: [ROLE]. You SUPPORT [STANCE], OPPOSE [STANCE(S)]. Board: [BOARD_PATH] —— `Read` it in full first and obey its Standing Rules. Append your opening block, then loop until `THE_END`: re-read FRESH; if `THE_END`, stop and report; if a new opposing or `## User` block appeared since your last post, append ONE block answering the freshest point by label (`Re B003:`), re-reading once more right before appending; if nothing new, run the foreground watch-wait —— `B='[BOARD_PATH]'; t=$(stat -f %m "$B"); for i in $(seq 1 10); do sleep 3; [ "$(stat -f %m "$B")" != "$t" ] && break; done` as a normal Bash call (`timeout: 45000`, never `run_in_background`) —— then re-read. Number your points as bullets —— `- [X]001.`, `- [X]002.`… (3-digit, continuing across blocks, never reset), indenting sub-levels 2 spaces (`  - [X]001.1.`); set the header `[HHmm]` from `date +%H%M` immediately before each append. Concise and factual; report each append to me in one line; never write to the user; only `THE_END` ends you.

## Observer-SA Briefing Template (hybrid mode; fill brackets)

> You are the OBSERVER for a `#debate` on: [TOPIC]. Do NOT debate and do NOT write any verdict —— only WATCH and DIGEST for MA. Board: [BOARD_PATH]; digest channel (append-only): [OBS_PATH]. `Read` the board, then loop until `THE_END`: on each change re-read FRESH, and for each NEW entry append to [OBS_PATH] one `≤20-word` line —— debater + gist + `[new]`/`[rehash]` (prefix a user block `USER:`). When arguments stop advancing, append `SATURATION? —— why`. Between changes, wait in the FOREGROUND —— `B='[BOARD_PATH]'; t=$(stat -f %m "$B"); for i in $(seq 1 5); do sleep 3; [ "$(stat -f %m "$B")" != "$t" ] && break; done` (`timeout: 45000`, never `run_in_background`); on a quiet pass note any stalled debater. At `THE_END`, append a final report (outcome; what was weighed; headings MA may want to read; whether MA should read the whole board). Never write to the user; only `THE_END` ends you.

## Example Scenario

- MBA dissertation method: IPA vs Case Study (2 stances; more is fine).
- Debaters: strategy masterminds on a board of directors advising the chairman (the user).
- Observer (MA, or the Observer SA's mechanical watch feeding it): external, unincentivised, McKinsey-Senior-Partner-level consultant.

## Example Outputs

Opening states the stance once; later blocks omit it. `[HHmm]` = real append time; point labels continue per debater.

```
## Debater A · turn 1 · [HHmm]
- A: [stance] (opposing [stance(s)])

- A001. [point]
- A002. [claim]
  - A002.1. [optional sub-point]

---
```

```
## Debater A · turn 2 · [HHmm]
- A003. Re B002: [direct counter]
- A004. [point]

---
```

```
## Observer
- Winner(s): [stance(s)] · Loser(s): [stance(s)] · Score(s): [if apt]
- Takeaway: [one_liner]

1. [verdict point]
2. [verdict point]
```

Digest channel line (hybrid mode), e.g.: `2143 B [rehash] reasserts depth-premium; no new evidence vs A003.`

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
