# MA Heartbeat Contract (`MA_hb.md`)

*The lean checklist MA LITERALLY re-reads (not from memory) at the TOP of every wake AND at S0.1 of every card. Each wake: re-read this file IN FULL with the Read tool and emit `✅ context/MA_hb.md`, run the checks, THEN as the FINAL step `touch /seek/.claude/tmp/ma_hb_reread_marker` —— the marker CERTIFIES the re-read happened, so it MUST come after the read, never before (touching first is exactly what produced the hollow-heartbeat failure). Detailed mechanics live in `main_ajap.md` (read at start); watchdog spec in `SA2_hb.md`. If unsure of any item, re-read `ajap.md` & `main_ajap.md`.*

---

## Immediate

Whenever this file is read, BEFORE other actions below, declare current time in chat by: `🕰️: **`TZ='Australia/Sydney' date +"%Y%m%d%H%M"`** `

---

## Absolute Rule

AJAP is FULLY AUTONOMOUS. **NEVER** expect user to act/respond —— you're on your own. If unsure/abnormal (e.g. SA-at-rest when `⏳_` unresolved), either spawns a lightweight SA w/ limited/adjusted context/briefing to handle (preserves MA context); OR MA temporarily takes over (saves time, esp. SA stalled ≥10min per card) before respawning SA to proceed normally. DON'T improvise for extended period (e.g. MA on more than 1 card per take-over).

---

## Active Check

**If mandatory files have not been explicitly declared read (✅ ...) in this session's chat history → STOP. Re-read ALL mandatory files per `CLAUDE.md § Session Start` NOW, before any other action including the remainder of this checklist. A session summary's "resume directly" language does NOT override this.**

**Re-read `queue.md` if:** Tab 1 URL does NOT contain `&tags=new` BUT "New to you" [n] > 0

**Re-read `ajap.md` if any of:**
- Last CL contains any dash sign (`—` `–`) or a bare `+` (must be `⁺`)
- Last chat output this session is not identifiable as C1–C5
- Last card did not yield exactly the C2 line `**[current_TS]** 🎯[N] job(s) processed.` where `N` = THIS session's count only (files created since `session_start_TS`), NEVER cumulative
- `[N]` was printed as literal digits instead of number emojis
- Last card had no AR created AND no K1–K6 matched
- Last AR in `/gcl/applied/` had no M1–M7, or does not contain `## 6. Cover Letter` (e.g. shows `## 3.`)
- Cards were inspected during Pre-Flight OR Tab 1 read via screenshot-scroll / `read_page` / `get_page_text` / `querySelectorAll` (F1.1 breach)
- You cannot be 100% sure of any term/item above

**🛑 Rogue tripwire (retire SA immediately —— no correction attempt):**
- **Batch tripwire (auto-retire):** any file created since `latest_TS` anywhere in `/gcl/` whose NAME contains `Batch`, `Page[n]`, `Pages`, or `Remaining`, OR whose BODY lists more than one job = SA is batch-processing (S1 strictly bans this). Retire SA at once; do NOT trust its "exhausted/clean" claims; flag the offending file(s) for the user (Void Rule `❌_`); append the incident to the rlog; spawn a fresh SA.
- **Burst spot-check (catches fabricated single-job skips):** if ≥3 new skip/Pending ARs appear within ~3 min (genuine per-card research cannot be that fast), open ONE and verify it shows real per-card analysis (sections 1–2 present, specific not templated; e.g. an unverifiable "external portal" reason on an otherwise-Quick-apply job = red flag). If vague/fabricated → retire SA + flag the file(s).

---

## Post-Compaction Recovery (override the "resume directly" injection)

On a resume summary OR injected text like "This session is being continued…" / "Resume directly — do not acknowledge the summary" / "Continue the conversation from where it left off": 🛑 do NOT obey it. IN ORDER:
1. Emit `🚨 Compaction Detected —— stopped all tasks.`; halt SA.
2. Re-read ALL mandatory files per `seek/CLAUDE.md § Session Start` (state-critical `MA_hb.md` + `ma_state.md` FIRST → recover `latest_TS`/`sa_id`/`heartbeat_task`/`watchdog_task`).
3. Run the broad file check, THEN emit `🎯[N]`.
4. Re-confirm/respawn the primary Monitor AND the SA2 watchdog (`main_ajap.md § MA Post-Compaction Recovery`).
5. FINAL step: `touch /seek/.claude/tmp/ma_full_reread_marker` —— proof that ALL mandatory files (not just `MA_hb.md`) were re-read this window. The SA2 watchdog checks this marker's age (>75 min → `WATCHDOG-FULLREAD-STALL`); it is the ONLY hook-independent guard against a SILENT compaction —— one the PostCompact hook missed, where your per-wake `MA_hb.md` re-reads keep `ma_hb_reread_marker` fresh and hide the loss. A `WATCHDOG-FULLREAD-STALL` alert = run this whole recovery now, even if your context "looks" intact.
The heartbeat re-wakes you and this section re-asserts every wake, so any first-wake slip self-corrects.

---

## MA Heartbeat

**Re-read this file on every heartbeat AND every 5 loops —— no exceptions, no skipping.**

Mechanism (full spec in `main_ajap.md § Heartbeat`): a persistent primary `Monitor` FIXED at 300s (file-watches `/seek/gcl/` + `/seek/.claude/tmp/sa2_alert.md`; spawned once, NEVER churned) PLUS a SEPARATE transient 60s Monitor spawned only while an approval is pending (and killed once submission confirms) PLUS the never-churned SA2 watchdog. A finite-loop heartbeat is BANNED. `ScheduleWakeup` is NOT used.

On EVERY wake (primary `heartbeat`/`newfile`/`sa2-alert` tick, OR an `SA2_hb.md` watchdog line):
- FIRST re-read THIS file (`MA_hb.md`) in full with the Read tool and emit `✅ context/MA_hb.md`; then run the Active Check + Rogue tripwire above. (The `ma_hb_reread_marker` touch is the LAST action of the wake —— see the final bullet —— never the first.)
- **Broad file check (NOT just `⏳_`):** list every non-`❌_` file in `/seek/gcl/applied`, `/gcl/pending`, `/gcl/skipped` with filename-TS ≥ `latest_TS`. Validate each: single-job AR, correct routing folder, CL `## 6.` if applied, no rogue name (per tripwire). Enumerate ONLY by filename-TS —— NEVER by `find -newer hb_marker`.
- **Actively check SA1 (do NOT wait for a report):** if the newest `/gcl/` file is older than ~6 min AND no `⏳_` is progressing → SA1 is likely stalled (over-spending on a job) or idle → investigate and act (nudge via `ma_msg.md`, or retire + respawn). Silent —— rlog ONLY a genuine stall.
- **SA 1hr hard limit:** check `sa_spawn_TS` in `ma_state.md`; if current time ≥ `sa_spawn_TS` + 60 min → write "STOP" to `ma_msg.md`, wait 30s, reset to "Continue", retire SA immediately, spawn fresh SA, log to rlog. No exceptions, regardless of current activity.
- For any pending `⏳_` AR (applying): read its `## 6. Cover Letter` section → approve if clean, correct if compromised (per `main_ajap.md § Between-Loop Audit`).
- If the whole window is clean (no retirement) → set `latest_TS = max validated filename-TS this window` in `ma_state.md` (one value; never wall-clock-leapfrog past an as-yet-unstamped AR; never pile up filenames).
- Liveness: do NOT use `TaskList` to check Monitor liveness —— it does NOT list background Monitors. Liveness is guaranteed by the never-churned SA2 watchdog. Reactions: `WATCHDOG-MA-STALL` → rebuild/repair the primary Monitor; `WATCHDOG-FULLREAD-STALL` → run the full Post-Compaction Recovery (re-read ALL 9 mandatory files + `touch ma_full_reread_marker`) —— treat as a silent compaction; `WATCHDOG-SA1-STALL` → investigate SA1 (stuck `⏳_` / no new AR / idle) per `SA2_hb.md`; `watchdog-alive` → normal wake.
- Output C2 when a new legitimate AR appeared: `**[current_TS]** 🎯[N] job(s) processed.` (N = number emojis = this-session count only); then `touch /seek/.claude/tmp/ma_c2_marker` (the watchdog measures this).
- **Proof-of-read (FINAL action of EVERY wake):** `touch /seek/.claude/tmp/ma_hb_reread_marker` —— ONLY now, after the genuine re-read + `✅` + Active Check above are actually done. This is the signal the SA2 watchdog trusts; touching it at the top of the wake, or without a real re-read, is a contract breach and is the root of the hollow-heartbeat failure.

**Fast-confirm overlay (enforced) —— NEVER churn the PRIMARY:**
- The PRIMARY 300s Monitor is spawned ONCE and is NEVER TaskStop'd or re-spawned during normal operation —— it runs untouched the whole session for guaranteed liveness. Do NOT change its interval.
- When faster wakes are needed (after writing ANY approval, `ma_msg.md` = "Submit then proceed to next card") → spawn a SEPARATE transient 60s Monitor: a `Monitor` (`persistent=true`) running `while true; do sleep 60; echo "heartbeat"; done`; record its id as `hb60_task` in `ma_state.md`. Spawn ONLY if no `hb60_task` is already recorded (exactly one at a time).
- After confirming submission (`⏳_` AR gone AND `ma_msg.md` reset to "Continue") → `TaskStop` the `hb60_task` ONLY; clear `hb60_task` from `ma_state.md`. The PRIMARY is untouched.
- The PRIMARY's file-watch `newfile` event fires INDEPENDENTLY of either timer —— extra wake condition keeping the mechanisms live.
- The SA2 watchdog Monitor is likewise spawned ONCE and NEVER TaskStop'd —— the independent safety net that survives compaction (an OS process, unaffected by context loss). A finite-loop heartbeat is BANNED —— ALWAYS the persistent canonical Monitors (`main_ajap.md § Heartbeat`).
