# Role-Playing Debate

## Activate

- Trigger: `#debate`.
- If told which roles/stances → follow; otherwise, MA judges and assigns.
- Goals:
  - Pre-empt counter-arguments (from stakeholders in context, if applicable).
  - Surface multidimensional pros & cons; eliminate blindspots.
  - Ultimately assist in wisely making critical decisions.

## Architecture (Director / Manager / debaters)

- **Board** —— `debate_board_[start_TS].md` —— a shared, append-only file that grows live (the "forum" the user reads). Same folder as `response_`; CP-prefixed if a CP session.
- **Debater SAs** —— one per role, spawned `run_in_background=True`; each free-runs (reads, appends, rebuts) until `THE_END`. They NEVER self-stop or self-declare saturation.
- **MA = Director.** Sets roles/stances (only it holds full session context; a wrong call wastes the run), creates + declares the board (and, hybrid, the digest), spawns the SAs, keeps OVERSIGHT throughout, and writes the `## Observer` verdict + `response_`.
- **Observe mode (MA's on-the-spot choice):**
  - **Default Mode (MA-as-observer) —— the DEFAULT:** MA is both Director and Manager —— watches the board itself by DELTA (cost stays linear), judges saturation + the token cap, closes (`THE_END`), and verdicts. No Observer SA, no digest —— just board + `response_`. Simplest, cheapest, most reliable (no digest to degrade). Use this unless you need Hybrid.
  - **Hybrid Mode (+ Observer SA) —— for CONCURRENT work, esp. `#sprint`:** MA also spawns a light **Observer SA = Manager** that watches the board, digests it to `debate_digest_[start_TS].md`, judges saturation, and CLOSES it (`THE_END`). This keeps MA's context lean DURING the debate so MA can do other work; the cost is an extra SA + a digest that can degrade (MA's full-board read at close still grounds the verdict, so a degraded digest at worst mistimes the close, never corrupts the verdict). MA keeps oversight via the digest and may itself judge/close.
- **In Hybrid Mode, both the Observer SA and MA may append `THE_END`** (identical effect). The Observer is the primary closer (it sees the verbatim board in real time); MA is the higher-authority overseer who closes if the Observer misses it (MA's edge: the full session picture —— including WHY this debate was started —— though it sees only the digest mid-run, not the board).
- Role/stance count and SA model (Sonnet/Opus) are MA's on-the-spot call. `#debate` is rare and run with intent —— reliability over economy. The user watches usage and may intervene —— EXCEPT under `#sprint` (user away), where MA self-governs entirely: the auto-close + token cap need no live intervention, and MA judges every call (close / add-a-debater / void-restart) herself.

## Roles & Stances

- Play multiple roles concurrently (one SA each): supporting each stance, AND opposing the single opposite OR the rest (MA judges).
- Every argument: eloquent British spoken-style; 100% factual (no fabrication); well-grounded; concise.

## The Board —— Read/Append-Only (CRITICAL)

- **Create:** MA only, once (`Write`/heredoc fine for the initial board: header + topic + Standing Rules).
- **Thereafter add ONLY via a Bash append (`>>`); read via `Read`/`tail`.** Never `Edit`/`Write` the board —— both overwrite and corrupt concurrent appends.
- One concise block per `>>` write. `O_APPEND` lands every write at end-of-file, so parallel writers never clobber each other —— no temp files.
- **DELTA reads (the cost lever).** Read the FULL board once at start; thereafter NEVER re-read the whole board —— track the last line you've seen and read ONLY new lines (`tail -n +[lastline+1] "$B"`), then update your marker. Safe because the board is append-only: nothing before your marker ever changes, so a delta read can never miss anything (true for any number of debaters). Re-reading the whole growing board each cycle is what makes cost balloon; deltas keep each agent's context linear.
- **Header-safe signals.** Keep the literal tokens `THE_END`, `STOP`, and `FINAL REPORT` OUT of any header you write (board or digest), so a grep/watcher can't false-match the documentation. Closure is detected ONLY as a standalone `^THE_END$` line.

## Stopping —— saturation or a size-scaled board cap

- **Saturation** (normal trigger): close when no materially new argument is surfacing. In practice this almost always arrives first.
- **Board-token cap (live gate), scaled to debate size.** Cap = (number of DEBATERS) × 4k tokens (the Observer doesn't write to the board, so it isn't counted). The observer runs `token-count --file [board]` each `~`60 s:
  - `< 50%` of cap → close on saturation as usual.
  - `≥ 50%` of cap (debaters × 2k) → bias HARD towards closing (continue only on a clearly new material point); the Observer SA ALERTS MA via the digest.
  - `≥ 100%` of cap (debaters × 4k) → close now, gracefully.
- **`THE_END`** is the sole stop signal —— a standalone line, written by the Observer SA (hybrid) or MA. Appended to the board, it reaches every debater at once. Until it appears no debater stops.
- The `## Observer` verdict block is ALWAYS MA-authored (it needs session context); `THE_END` and the digest are the Observer SA's in hybrid mode.

## Debaters run dry ≠ saturation

- Debaters running out of things to say (going idle) is NOT itself saturation, and is NEVER theirs to call —— they only ever idle-wait until `THE_END`. Crucially they stay ALIVE in that watch-wait, so a newly-added debater's (or a `## User`) post re-stimulates them —— which is exactly why adding a stance (below) revives a stalled board; a debater that had truly quit could not be revived.
- When the board goes idle but it is NOT genuinely saturated (a fresh angle could still add value), do NOT close. Two responses, CHEAPEST FIRST: (a) NUDGE —— append a short steer to the board (`continue`, `consider X`, `elaborate Y`); the idle debaters' watch-wait wakes them and they resume, at a fraction of the cost; (b) ADD A DEBATER —— only if a genuinely new STANCE would add value (re-stimulation is then a free side-benefit, not the reason), spawned WITHOUT consulting the user; or restart with a better config. Spawning a debater purely to re-stimulate is wasteful —— prefer the nudge. (Hybrid: the Observer SUGGESTS via the digest; MA decides.) Close only when genuinely saturated (or the cap is hit).

## Debater SA —— Sustain Loop

Once spawned: (1) `Read` briefing + the FULL board once (record the last line); (2) append the opening block; (3) loop until `THE_END`:
- Read ONLY the new lines since your last read (delta —— `tail -n +[N]`); update your marker.
- A standalone `THE_END` present → stop, one-line ack.
- New opposing (or `## User`) block → compose ONE block answering the freshest point by its label (`Re B003:`). As the LAST step before the `>>`, run `grep -q '^THE_END$' [board]` (a FULL board check, not just your delta —— `THE_END` may sit anywhere) AND set a fresh `[HHmm]`: if `THE_END` is present, STOP without appending; else append.
- Nothing new → run the foreground watch-wait (below), then re-read the delta. Don't post to fill silence; if you have nothing new, keep idle-waiting (do NOT quit).
- Address others by letter; answer, don't monologue.

**Watch-wait (keeps the SA alive; FOREGROUND only —— never `run_in_background`, which makes it come to rest unrecoverably).** Run as a normal Bash call, `timeout: 45000`:

```
B='[board]'; t=$(stat -f %m "$B"); for i in $(seq 1 10); do sleep 3; [ "$(stat -f %m "$B")" != "$t" ] && break; done
```

Returns within `~`3 s of any board change, else after `~`30 s. macOS `stat -f %m`.

## Observer SA (hybrid mode only)

A light SA (`run_in_background=True`), briefed to WATCH, DIGEST, and CLOSE —— never to debate or write the verdict. Same foreground watch-wait, capped `~`15 s (`seq 1 5`). Reads the board by DELTA. On each board change it appends to the pre-created `debate_digest_[start_TS].md` (append-only):
- ONE `≤20-word` digest of each new entry, written in a SINGLE `printf` as ONE line (never fragmented across lines, even under fast churn): debater + the new point's gist + `[new]` / `[rehash]` (so MA, reading only the digest, has the whole picture). A `## User` block → prefix `USER:`.
- Each `~`60 s heartbeat: run `token-count --file [board]`; append `TOKENS=[n]` (proves the cap is polled live).
- ALERT MA (a digest line) at `≥ 50%` of the cap. SUGGEST MA add a debater ONLY after SEVERAL consecutive genuinely-empty deltas (a true lull) and you judge it not saturated —— never on a single quiet poll (a momentary gap whilst debaters compose is not idleness).
- **Close** when genuinely saturated, OR `≥ 100%` cap, OR a `## User` block contains `STOP`: append a standalone `THE_END` line to the BOARD, then a FINAL REPORT to the digest (outcome; what was weighed; the block HEADINGS MA should read; whether MA must read the whole board), then stop.

## MA Operation

1. Decide topic, stances, roles, debater count, model, observe mode.
2. Create + declare the board AND (hybrid) the digest at once (see § Declaration).
3. Spawn one Debater SA per role (`run_in_background=True`); hybrid → also spawn the Observer SA.
4. **Observe.** **Default Mode:** watch the board directly by DELTA (`~`15 s + `~`60 s heartbeat), judge saturation + the token cap, and close (`THE_END`) yourself. **Hybrid Mode:** watch the DIGEST instead (`~`15 s + `~`60 s) —— the Observer owns the close, but YOU retain oversight: act on a `USER:` / `ALERT` / `SUGGEST` line; judge saturation yourself from the digest + your session context; if you deem it saturated and the Observer hasn't closed, close it yourself. Watchdog: every `~`300 s confirm the Observer SA is alive (recent digest activity); re-spawn if dead.
5. **Verdict (MA, always) —— let the board SETTLE first.** After `THE_END` is down, do NOT verdict immediately: WAIT until every debater has actually stopped (their completion acks) —— a fast debater can append one or more blocks in its compose-window AFTER `THE_END`, so the board keeps growing for a beat. Only once it's settled, RE-READ the board's FINAL state afresh (NEVER verdict from an earlier oversight read —— the board moves fast and will have moved on) plus the digest's final report, THEN append the `## Observer` block. Skipping the wait/re-read produces a verdict that misses the last turns and a block stranded mid-board.
6. **Surface + cost/compaction check:** distil the verdict + session implications into `response_[TS].md` (don't heavily repeat the Observer block). Tally whole-debate token usage (sum of per-SA usages seen at completion) as a cost report. If that sum exceeds `~`200k —— noteworthy —— check EACH SA against its context window (Sonnet 200k, Opus 1M): any SA OVER its window COMPACTED and its content may be compromised → MA MUST flag it (in `response_` and/or the Observer block). **The Observer SA especially:** if IT compacted, the digest MA steered by may itself be wrong —— strongly consider voiding + restarting. If > 50% of SAs compacted (round up: 1 of 2, 2 of 3, 2 of 4) → consider VOIDING the result and restarting with an adjusted config. For a debate expected to run large, pre-empt all this by spawning an OPUS Observer (5× Sonnet's window). Under `#sprint`, MA makes these calls itself.
- 6.1. **Self-improvement (real debates refine this protocol).** After a NON-`#sprint` debate fully finishes, if you noticed any shortcoming or improvement to THIS protocol, SUGGEST it (do NOT act on it) at the END of the `response_` —— so practical runs, not just test runs, keep `debate.md` improving. Under `#sprint`, log it for the Sprint Report instead of pausing.
7. **Resilience:** re-spawn any debater or the Observer SA that dies mid-debate —— the board and digest are durable memory.

## User Interventions (highest authority)

The user may append a `## User` block to the board anytime (template at bottom). It outranks everyone.
- A `## User` block with `STOP` → the observer (Observer SA in hybrid, else MA) closes gracefully: `THE_END` → final report → MA verdict → `response_`. Never a hard-kill.
- Any other `## User` note → an authoritative steer (e.g. a new angle); the debate continues along it.
- Debater SAs fold a `## User` steer into the next block; they still stop only on `THE_END`.

## Declaration (overrides root CLAUDE.md §3.1.5)

- Declare the board `➡️` IMMEDIATELY after creating it; in hybrid mode declare the digest `➡️` at the same time (MA creates it). Declaring both lets the user click between them to force a live refresh. The `response_` declares as usual.

## Standing Rules (paste into the board header —— SAs inherit them by reading the board)

- Read via `Read`/`tail` (delta after the first read); add only via `>>`; never `Edit`/`Write` this board.
- One concise block per append; before every block, read the latest delta and answer the freshest opposing (or `## User`) point by its label. No stale reads, no monologues.
- Number points `[YourLetter][3-digit]`, continuing across ALL your blocks, never resetting. EVERY point is its own bullet, indented 2 spaces per sub-level: `- A001. …`, `  - A001.1. …`, `    - A001.1.1. …`. Reference others by label (`Re B003.2:`).
- Header `[HHmm]` = the REAL append moment (`TZ='Australia/Sydney' date +%H%M` just before appending; never hardcode/reuse).
- Stop ONLY on a standalone `THE_END` line —— never self-declare saturation or quit. 100% factual; outputs go to MA only.

## Debater-SA Briefing Template (fill brackets)

> You are Debater [X] in a `#debate` on: [TOPIC]. Role: [ROLE]. SUPPORT [STANCE], OPPOSE [STANCE(S)]. Board: [BOARD_PATH] —— `Read` it in full ONCE (note the last line number) and obey its Standing Rules. Append your opening block, then loop until `THE_END`: read only the NEW lines since last (`tail -n +[lastline+1] "[BOARD_PATH]"`), updating your marker; if a standalone `THE_END` is present, stop and report; if a new opposing or `## User` block appeared, compose ONE block answering the freshest point by label (`Re B003:`) —— then as the LAST step before the `>>`, run `grep -q '^THE_END$' "[BOARD_PATH]"` (FULL board check) and set a fresh `[HHmm]`: if `THE_END` is present, stop without appending, else append; if nothing new, run the foreground watch-wait —— `B='[BOARD_PATH]'; t=$(stat -f %m "$B"); for i in $(seq 1 10); do sleep 3; [ "$(stat -f %m "$B")" != "$t" ] && break; done` (normal Bash call, `timeout: 45000`, never `run_in_background`) —— then re-read the delta. Never quit on your own —— only `THE_END` ends you. Number points as bullets `- [X]001.`, `- [X]002.`… (3-digit, never reset; sub-levels `  - [X]001.1.`); set header `[HHmm]` from `date +%H%M` just before each append. Concise, factual; report each append to me in one line; never write to the user.

## Observer-SA Briefing Template (hybrid; fill brackets)

> You are the OBSERVER for a `#debate` on: [TOPIC] —— [N] debaters (board cap = N×4k tokens). WATCH, DIGEST, and CLOSE —— do NOT debate or write a verdict. Board (read-only, by delta): [BOARD_PATH]; digest (append-only, already created): [DIGEST_PATH]. `Read` the board once (note the last line), then loop: read only NEW lines (`tail -n +[lastline+1] "[BOARD_PATH]"`), update marker; for each new entry append to [DIGEST_PATH] one `≤20-word` line —— debater + gist + `[new]`/`[rehash]` (user block → prefix `USER:`). Each `~`60 s heartbeat run `token-count --file "[BOARD_PATH]"` and append `TOKENS=[n]`; append an `ALERT` line at ≥50% of cap. If the board idles but isn't genuinely saturated, append a `SUGGEST —— add a debater` line (don't close). CLOSE —— append a standalone `THE_END` line to the BOARD, then a `FINAL REPORT` line to the digest (outcome; what was weighed; headings MA should read; whether MA must read the whole board), then stop —— when genuinely saturated, OR board ≥100% cap, OR a `## User` block says `STOP`. Between changes wait FOREGROUND —— `B='[BOARD_PATH]'; t=$(stat -f %m "$B"); for i in $(seq 1 5); do sleep 3; [ "$(stat -f %m "$B")" != "$t" ] && break; done` (`timeout: 45000`, never `run_in_background`). Never write to the user.

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

Digest lines, e.g.: `2143 B [rehash] reasserts depth-premium; no new evidence vs A003.` · `2144 TOKENS=3120` · `2150 ALERT —— 50% cap` · `2152 SUGGEST —— add a debater (idle, not saturated)`

---

## User Intervention Template —— ONLY for the user (MA & SAs: ignore this entire section)

- MA and SAs never read, act on, or quote this section —— it is a copy-paste helper for the human user, who outranks everyone.
- To steer or stop a live debate without waiting: copy the block below, edit `MSG`, run it in your terminal. It appends a highest-authority `## User` block to the board.
- Include the all-caps word `STOP` in `MSG` to close gracefully; omit it to act as a moderator and add a new angle.

```bash
# Auto-pick the newest debate board (or set BOARD="/abs/path/to/debate_board_[TS].md" to override):
BOARD="$(ls -t "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/sessions"/*/*/debate_board_*.md | head -1)"

# Edit your message:
MSG="STOP —— wrap up now and give me the Observer verdict."

# Moderator example (no stop): MSG="New angle —— evaluate this for a 3-person startup."

printf '\n## User · %s\n%s\n\n---\n' "$(TZ='Australia/Sydney' date +%H%M)" "$MSG" >> "$BOARD"
echo "Posted to: $BOARD"
```
