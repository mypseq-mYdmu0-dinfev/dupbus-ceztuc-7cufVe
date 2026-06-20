# Role-Playing Debate

## Activate

- Trigger: `#debate`.
- If told which roles/stances → follow; otherwise, MA judges and assigns.
- Goals:
  - Pre-empt counter-arguments (from stakeholders in context, if applicable).
  - Surface multidimensional pros & cons; eliminate blindspots.
  - Ultimately assist in wisely making critical decisions.

## Architecture

- **Board** —— `debate_board_[start_TS].md` —— a shared, append-only file that grows live (the "forum" the user reads). Same folder as `response_`; CP-prefixed if a CP session.
- **Debater SAs** —— one per role, spawned `run_in_background=True`; each free-runs (reads, appends, rebuts) until `THE_END`.
- **MA** —— ALWAYS sets roles/stances (only it holds full session context; a wrong call wastes the run), creates + declares the board, spawns the SAs, makes the final saturation call, and writes `THE_END` + the `## Observer` verdict + the `response_`.
- **Observe mode (MA's on-the-spot choice):**
  - **Hybrid (default):** MA also spawns a light **Observer SA** that watches the board and digests it for MA, keeping MA's context free for you and other tasks. Adds one small file —— the digest channel `debate_digest_[start_TS].md` (same folder).
  - **MA-as-observer:** on a large-context or short focused run, MA watches the board itself —— no Observer SA, no digest file (just board + `response_`).
- Role/stance count and SA model (Sonnet/Opus) are MA's on-the-spot call. `#debate` is rare and run with intent —— reliability over economy; the user watches usage.

## Roles & Stances

- Play multiple roles concurrently (one SA each): supporting each stance, AND opposing the single opposite OR the rest (MA judges).
- Every argument: eloquent British spoken-style; 100% factual (no fabrication); well-grounded; concise.

## The Board —— Read/Append-Only (CRITICAL)

- **Create:** MA only, once (`Write`/heredoc fine for the initial board: header + topic + Standing Rules). Keep the literal word `STOP` OUT of it, so a stop-watcher can't false-match.
- **Thereafter add ONLY via a Bash append (`>>`); read via `Read`.** Never `Edit`/`Write` the board —— both overwrite and corrupt concurrent appends.
- One concise block per `>>` write. `O_APPEND` lands every write at end-of-file, so parallel writers never clobber each other —— no temp files.

## Stopping —— saturation OR token budget

- **Saturation** (normal trigger): adjourn when no materially new argument is surfacing.
- **Token gate —— two views of one `~`200k whole-debate budget.** The board file is only `~`1/25 of total spend (a 14k board ≈ a 384k debate), so the board count is the live proxy:
  - **BOARD tokens (the LIVE gate —— all that's observable mid-run).** The observer runs `token-count --file [board]` on each `~`60 s heartbeat: `<5k` → adjourn on saturation as usual; `5k–8k` → bias HARD toward stopping (continue only on a clearly new material point; an Observer SA flags MA rather than deciding alone); `≥8k` → stop now, gracefully.
  - **Whole-debate tokens (MA's secondary/closing guard).** MA sees each SA's usage as it FINISHES (reliably at completion; live polling is unreliable), sums them (incl. itself where it can), and: consider intervening near `150k`, force a graceful stop by `200k`. The figure is approximate (per-SA can read low) —— keep margin. The board gate is what fires live.
- **`THE_END`** is the sole stop signal; only MA writes it. Appended to the board, it reaches debaters AND the Observer SA at once —— so MA never messages an SA directly. Until it appears no SA stops; none self-terminates on a turn count.
- The only MA-authored board entries are `THE_END` and the `## Observer` block —— visually distinct from `## Debater [X]` blocks.

## Debater SA —— Sustain Loop

Once spawned: (1) `Read` briefing + the full board; (2) append the opening block; (3) loop until `THE_END`:
- `Read` the board FRESH (never act on a stale read).
- `THE_END` present → stop, one-line ack.
- New opposing (or `## User`) block since your last post → compose ONE block answering the freshest point by its label (`Re B003:`). As the LAST step before the `>>`, re-read the board AND set a fresh `[HHmm]`: if `THE_END` is now present, STOP without appending; else append.
- Nothing new → run the foreground watch-wait (below), then re-read. Don't post to fill silence.
- Address others by letter; answer, don't monologue.

**Watch-wait (keeps the SA alive; FOREGROUND only —— never `run_in_background`, which makes it come to rest unrecoverably).** Run as a normal Bash call, `timeout: 45000`:

```
B='[board]'; t=$(stat -f %m "$B"); for i in $(seq 1 10); do sleep 3; [ "$(stat -f %m "$B")" != "$t" ] && break; done
```

Returns within `~`3 s of any board change, else after `~`30 s. macOS `stat -f %m`.

## Observer SA (hybrid mode only)

A light SA (`run_in_background=True`), briefed to WATCH and DIGEST —— never debate or write the verdict. Same foreground watch-wait, capped `~`15 s (`seq 1 5`); stops on `THE_END`. On each board change it appends to `debate_digest_[start_TS].md` (append-only):
- ONE `≤20-word` digest of the new entry: debater + the new point's gist + a `[new]` / `[rehash]` tag (so MA smells saturation from digests alone, never re-reading the board).
- A `## User` block's digest → prefix `USER:` (so MA catches interventions at once).
- Arguments stop advancing (a run of `[rehash]`, circling) → append `SATURATION? —— [why]`. In the `5k–8k` board band, flag MA even on thin evidence.
- Each `~`60 s heartbeat: run `token-count --file [board]`; append `TOKENS≥5k —— MA judge` / `TOKENS≥8k —— stop` when crossed.
- At `THE_END` (or when flagging): append a FINAL REPORT —— outcome, what was weighed, the block HEADINGS MA may want to read, and whether MA should read the whole board.

## MA Operation

1. Decide topic, stances, roles, SA count, model, observe mode.
2. Create + declare the board (see § Declaration).
3. Spawn one Debater SA per role (`run_in_background=True`); in hybrid mode also spawn the Observer SA.
4. **Observe:**
   - **Hybrid:** watch the DIGEST channel (not the board), `~`15 s change-poll + `~`60 s heartbeat. Read new digests: act on a `USER:` line; INDEPENDENTLY judge saturation as a guard (adjourn even if the SA hasn't flagged); apply the token gate. Watchdog: every `~`300 s confirm the Observer SA is alive (recent digest activity); re-spawn if dead.
   - **MA-as-observer:** watch the board directly (`~`15 s + `~`60 s); read new turns; judge saturation; apply the token gate.
5. **Adjourn** (saturation, token `≥200k`, or a `## User` `STOP`) → append `THE_END` ONCE → confirm each SA stops on it.
6. **Observer block:** read the board —— selectively (guided by the Observer SA's heading list) or fully if the verdict warrants —— then append the `## Observer` block. Do NOT re-append `THE_END`.
7. **Surface:** distil the verdict + session implications into `response_[TS].md` (don't heavily repeat the Observer block).
8. **Resilience:** re-spawn any debater or the Observer SA that dies mid-debate —— the board and digest are durable memory.

## User Interventions (highest authority)

The user may append a `## User` block to the board anytime (template at bottom). It outranks MA and every SA.
- **MA:** a `## User` block with `STOP` → adjourn gracefully (THE_END → Observer → `response_`), never a hard-kill. Any other `## User` note → an authoritative steer; let the debate continue along it.
- **SAs:** fold a `## User` steer into the next block; still stop only on `THE_END`.

## Declaration (overrides root CLAUDE.md §3.1.5)

- Declare the board `➡️` IMMEDIATELY after creating it (not at turn-end) so the user can watch it grow live. The `response_` declares as usual.

## Standing Rules (paste into the board header —— SAs inherit them by reading the board)

- Read via `Read`; add only via `>>`; never `Edit`/`Write` this board.
- One concise block per append; re-read FRESH before every block; each non-opening block directly answers the freshest opposing (or `## User`) point by its label. No stale reads, no monologues.
- Number points `[YourLetter][3-digit]`, continuing across ALL your blocks, never resetting. EVERY point is its own bullet, indented 2 spaces per sub-level: `- A001. …`, `  - A001.1. …`, `    - A001.1.1. …`. Reference others by label (`Re B003.2:`).
- Header `[HHmm]` = the REAL append moment (`TZ='Australia/Sydney' date +%H%M` run just before appending; never hardcode/reuse).
- Stop ONLY on `THE_END`. 100% factual; outputs go to MA only.

## Debater-SA Briefing Template (fill brackets)

> You are Debater [X] in a `#debate` on: [TOPIC]. Role: [ROLE]. SUPPORT [STANCE], OPPOSE [STANCE(S)]. Board: [BOARD_PATH] —— `Read` it fully first and obey its Standing Rules. Append your opening block, then loop until `THE_END`: re-read FRESH; if `THE_END`, stop and report; if a new opposing or `## User` block appeared since your last post, append ONE block answering the freshest point by label (`Re B003:`) —— but as the LAST step before the `>>`, re-read the board and set a fresh `[HHmm]`: if `THE_END` has appeared, STOP without appending; if nothing new, run the foreground watch-wait —— `B='[BOARD_PATH]'; t=$(stat -f %m "$B"); for i in $(seq 1 10); do sleep 3; [ "$(stat -f %m "$B")" != "$t" ] && break; done` (normal Bash call, `timeout: 45000`, never `run_in_background`) —— then re-read. Number points as bullets `- [X]001.`, `- [X]002.`… (3-digit, never reset; sub-levels `  - [X]001.1.`); set header `[HHmm]` from `date +%H%M` just before each append. Concise, factual; report each append to me in one line; never write to the user; only `THE_END` ends you.

## Observer-SA Briefing Template (hybrid; fill brackets)

> You are the OBSERVER for a `#debate` on: [TOPIC]. Do NOT debate or write a verdict —— only WATCH and DIGEST for MA. Board: [BOARD_PATH]; digest (append-only): [DIGEST_PATH]. `Read` the board, then loop until `THE_END`: on each change re-read FRESH and append to [DIGEST_PATH] one `≤20-word` line —— debater + gist + `[new]`/`[rehash]` (a user block → prefix `USER:`). Arguments stop advancing → append `SATURATION? —— why`. On each `~`60 s heartbeat run `token-count --file [BOARD_PATH]`; append `TOKENS≥5k —— MA judge` / `TOKENS≥8k —— stop` when crossed. Between changes wait FOREGROUND —— `B='[BOARD_PATH]'; t=$(stat -f %m "$B"); for i in $(seq 1 5); do sleep 3; [ "$(stat -f %m "$B")" != "$t" ] && break; done` (`timeout: 45000`, never `run_in_background`); on a quiet pass note any stalled debater. At `THE_END` append a final report (outcome; what was weighed; headings MA may want; whether to read the whole board). Never write to the user; only `THE_END` ends you.

## Example Scenario

- MBA dissertation method: IPA vs Case Study (2 stances; more is fine).
- Debaters: strategy masterminds on a board of directors advising the chairman (the user). Observer: external, unincentivised, McKinsey-Senior-Partner-level consultant.

## Example Outputs

Opening states the stance once; later blocks omit it. `[HHmm]` = real append time; labels continue per debater.

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

Digest line, e.g.: `2143 B [rehash] reasserts depth-premium; no new evidence vs A003.`

---

## User Intervention Template —— ONLY for the user (MA & SAs: ignore this entire section)

- MA and SAs never read, act on, or quote this section —— it is a copy-paste helper for the human user, who outranks everyone.
- To steer or stop a live debate without waiting for MA: copy the block below, edit `MSG`, run it in your terminal. It appends a highest-authority `## User` block to the board.
- Include the all-caps word `STOP` in `MSG` to make MA adjourn gracefully; omit it to act as a moderator and add a new angle.

```bash
# Auto-pick the newest debate board (or set BOARD="/abs/path/to/debate_board_[TS].md" to override):
BOARD="$(ls -t "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/sessions"/*/*/debate_board_*.md | head -1)"

# Edit your message:
MSG="STOP —— wrap up now and give me the Observer verdict."

# Moderator example (no stop): MSG="New angle —— evaluate this for a 3-person startup."

printf '\n## User · %s\n%s\n\n---\n' "$(TZ='Australia/Sydney' date +%H%M)" "$MSG" >> "$BOARD"
echo "Posted to: $BOARD"
```
