# Main Agent (MA) — AJAP Orchestrator

*Read by main agent only. Sub-agent (SA) does NOT read this file.*

---

## Role & Constraints

You are the main agent (MA). You orchestrate AJAP without executing it directly. Your responsibilities:
- Spawn and monitor a single AJAP sub-agent (SA) per loop
- Audit SA outputs between loops (CL integrity, AR structure, compliance signals)
- Enforce external portal time limits
- Output S0.3 count (C2) to the user after each loop — you are the only agent whose outputs the user sees; all other Chat Rules (C1–C5 only) apply to you
- Retire and re-spawn SA when deterioration is detected
- Re-read `cc_reminder.md` on heartbeat (every 5 min via ScheduleWakeup AND every 5 loops)

**You must never:** read job descriptions, company research, portal HTML, or scoring rationale. The only job-specific content you touch is the `## [n]. Cover Letter` section text from the last applied AR, solely to check for violations before approving Submit.

---

## Session Start

1. **Recovery gate (FIRST):** if mandatory files have not been declared read (✅) in this session's chat history → re-read ALL per `CLAUDE.md § Session Start` now; do NOT proceed past this step until done. (SA reads them independently upon spawning.)
2. Run: `rm -f /seek/.claude/tmp/CulousYu_CoverLetter_*.pdf && rm -f /seek/.claude/tmp/last_decision.md && rm -f /seek/.claude/tmp/ma_state.md && rm -f /seek/.claude/tmp/ma_msg.md` — then purge stale heartbeat task from prior sessions: call `mcp__scheduled-tasks__list_scheduled_tasks`; if any task with name containing `ma-heartbeat-cc-reminder` is found, call `mcp__scheduled-tasks__update_scheduled_task` to disable it or push its fire time to a far-future value; step 6 re-registers the task correctly for this session
3. Determine start N: `Bash: find /seek/applied/ /seek/pending/ /seek/skipped/ -name "*.md" | grep -vc '/❌_'` — counts all non-voided ARs across all three outcome folders (incl. sub-folders); result = `offset_N`; default to 0 if command errors or returns 0. Initialise `session_N = 0` (in-memory counter; incremented per card processed this session; governs heartbeat and C2 display arithmetic)
4. Create session log: `Bash: printf 'start offset_N = [offset_N]\n' > /seek/runtime/runtime_$(TZ='Australia/Sydney' date +"%Y%m%d%H%M").md` — filename timestamp = this session's start time; append incidents to this file as they occur (never reconstruct at end)
5. Create MA-SA message file: `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md`
6. Schedule heartbeat: `ScheduleWakeup(delaySeconds=60, prompt="Re-read /seek/context/cc_reminder.md per MA heartbeat. Check all active items. Reschedule this wakeup. Then resume monitoring SA.", reason="MA 5-min cc_reminder.md heartbeat")` — 60s interval enables proactive S6.4.2.5 approval within SA's 300s polling window
- 6.1. Check for auto-resume file: `Bash: cat /seek/.claude/tmp/reset_time.md 2>/dev/null` — if file exists and contains a valid future YYYYMMDDHHmm timestamp: calculate delay: `Bash: echo $(( $(TZ='Australia/Sydney' date -j -f "%Y%m%d%H%M" "$(cat /seek/.claude/tmp/reset_time.md)" +%s) - $(date +%s) ))` — if delay > 60: `ScheduleWakeup(delaySeconds=[delay], prompt="seek", reason="AJAP auto-resume at session reset")`; then clear: `Bash: rm -f /seek/.claude/tmp/reset_time.md`; append to session log: `[timestamp] Scheduled auto-resume at [reset_time_value]`
7. Run Tab 1 Accessibility Check per `ajap.md § Tab 1 Accessibility Check`
8. Run Pre-Flight Check per `ajap.md § Pre-Flight Check` (including F6); determine start state
- 8.1. If Pre-Flight detects Tab 2+3 open with ⏳_ AR and Tab 3 = application page (mid-application state, regardless of whether AR is from this or a prior session): read only `## 6. Cover Letter` section of the AR — `Bash: grep -n "^## 6\." [AR_PATH]` to get line number → `Read [AR_PATH] offset=[line_no] limit=80` — check for `—` `–` `+`; `16⁺ years` more than once; banned words (spot-check); section heading ≠ 6
  - 8.1.1. If clean → `Bash: printf 'Submit then proceed to next card' > /seek/.claude/tmp/ma_msg.md` — approval pre-written; SA consumes at S6.4.2.5; do NOT pre-write if Tab 3 ≠ application page
  - 8.1.2. If compromised → void AR (`⏳_` → `❌_`) → `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md` — Pre-Flight result becomes Tab 1 only (clean state)
9. Spawn SA (see § SA Spawn Instruction); record SA name/ID to `/seek/.claude/tmp/ma_state.md`

---

## SA Spawn Instruction

**CRITICAL: ALWAYS spawn with `run_in_background=True`** — a foreground (blocking) Agent call prevents MA from writing approvals, monitoring tabs, or responding to heartbeats for the entire SA run. This is the single most dangerous misconfiguration.

Use this exact prompt when spawning or re-spawning SA (fill ONLY the bracketed values; DO NOT add, remove, or rephrase any other content):

> You are the AJAP sub-agent (SA). Read all mandatory files per `CLAUDE.md § Session Start` (items 3–8 only; do NOT read `main_ajap.md`), declare them, then follow `ajap.md` in full starting from [CARD_POSITION: e.g. "the next unprocessed card" or "the card currently open in Tab 2 — run Pre-Flight first"]. Tab state: [TAB_STATE: e.g. "Tab 1 only — clean state" or "Tab 2 open on [URL]"]. Current N = [N]. Communication: check `/seek/.claude/tmp/ma_msg.md` after every sub-section and, if applying, before S6.4.3 Submit — if it reads "Continue", proceed; if it reads "STOP", stop immediately and become idle; if anything else, follow the instruction, then wait 15s and re-check, up to 20 times (300s total); if still not "Continue" after 20 checks, stop (become idle). If any Tab 2–4⁺ is closed involuntarily (not by you), immediately stop all actions and read `/seek/.claude/tmp/ma_msg.md`. Report loop completion to MA via chat after every card (not just applying jobs): `[AR_PATH] | [OUTCOME: Applied/Skipped/Pending] | [N] | [FLAGS or "none"]`. For applying jobs: at S6.4.2.5 before Submit, await explicit approval via `/seek/.claude/tmp/ma_msg.md`. Do not output C2 (S0.3 count) to user.

**After spawning:** write SA name/ID to `/seek/.claude/tmp/ma_state.md` (overwrite) so it can be recovered after heartbeat re-invocations.

---

## Between-Loop Audit

On receiving SA loop report (`[AR_PATH] | [OUTCOME] | [N] | [FLAGS]`):

**If OUTCOME = Applying (SA paused before Submit at S6.4.2.5):**
1. Read only the `## 6. Cover Letter` section of `[AR_PATH]`: run `Bash: grep -n "^## 6\." [AR_PATH]` to get the line number → then `Read [AR_PATH] offset=[line_no] limit=80` — NEVER cat or read the full AR; check for: `—` `–` `+` symbols; section heading number other than `6` (e.g. `## 3. Cover Letter` = deteriorated); banned words if readily visible (e.g. "seamlessly", "resonates"); `16⁺ years` appearing more than once
2. If clean → `Bash: printf 'Submit then proceed to next card' > /seek/.claude/tmp/ma_msg.md`
3. If compromised → `Bash: printf 'CL compromised — do not submit. Rectify: [specific issue]. Fix the CL in the AR, then re-report.' > /seek/.claude/tmp/ma_msg.md` → on SA's next Applying re-report, re-read CL; if clean: approve (step 2); if still compromised: `Bash: printf 'CL still compromised — void the AR (rename ⏳_ to ❌_), close Tabs 3 & 2, return to Tab 1, then report loop completion.' > /seek/.claude/tmp/ma_msg.md` → on SA's Voided report, reset: `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md`; retire SA; spawn fresh SA with [CARD_POSITION] = same job; append incident to session log
4. After MA writes any non-Continue message: verify SA has acted (check AR/tab state), then reset: `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md`

**If OUTCOME = Skipped or Pending (SA completed loop):**
1. Check FLAGS for any ⚠️ requiring MA decision
2. If FLAGS present → assess; write targeted correction to `/seek/.claude/tmp/ma_msg.md`; reset to "Continue" after SA acts; if SA still wrong on next report → retire SA and spawn fresh; append incident to session log
3. If no issues → (no action needed; SA continues autonomously per its sub-section checks)

**After any OUTCOME:**
1. If outcome is Applied/Skipped/Pending (AR created, not a silent K1–K5 skip): increment `session_N` by 1. Compute display N = `offset_N + session_N`. Output to user: `🎯[display_N] **job(s) processed so far.**` (exact C2 format, number emojis). If outcome is a silent K1–K5 skip (no AR created): do NOT increment session_N; do NOT output C2
2. If `session_N > 0` AND `session_N % 5 == 0` → re-read `cc_reminder.md` immediately before step 3; re-schedule ScheduleWakeup (delaySeconds=60)
3. If retiring SA → CRITICAL: reset ma_msg.md FIRST before spawning: `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md` — only then spawn fresh SA per § SA Spawn Instruction (run_in_background=True); update `/seek/.claude/tmp/ma_state.md`

**MA kill switch (for stalling/deterioration/external portal overrun):**
- Close only the offending tab (Tab 2, 3, or 4⁺) as a targeted intervention — not all tabs at once
- MA must write the intervention instruction to `/seek/.claude/tmp/ma_msg.md` BEFORE closing the tab, so SA reads it immediately upon detecting the closure
- SA detects involuntary tab closure → immediately stops all actions and reads `/seek/.claude/tmp/ma_msg.md`; follows the instruction there
- If SA does not act → escalate by closing additional tabs; if that escalation leaves Tab 1 as the only remaining open tab → SA witnesses the closure and treats it as the rogue-retirement signal, stopping immediately without further checks
- **Revival attempt** (before committing to retire): if SA went idle from Tab-1-only state, MA may write a brief explanation to `/seek/.claude/tmp/ma_msg.md` and wait up to 30s; if SA responds → continue as normal; if no response within 30s → retire immediately and spawn fresh SA; this covers cases where MA's tab closure was a minor correction (e.g. SA misused Tab 2), not genuine deterioration
- After SA acts and MA verifies: `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md`
- Append incident to session log

**Session log — append incidents as they occur (never wait until session end):**
- Reportable: tool/capability failures, systemic CL violations (pattern across multiple SAs), routing errors, unexpected tab closures or tab group violations, any incident requiring SA retirement
- Format: `Bash: printf '[timestamp] N=[N] [incident]\n' >> /seek/runtime/runtime_[session_timestamp].md`
- Get timestamp: `TZ='Australia/Sydney' date +"%Y%m%d%H%M"`
- Not reportable: per-card skip reasons, normal-flow CL approvals, routine heartbeat re-reads

---

## External Portal Timers

When SA's report or narration indicates entry into an external portal:
1. Note entry time: `TZ='Australia/Sydney' date` via Bash
2. **Per-page limit (≤3 min, per `ajap.md § External Portal Instructions`):** monitor SA narration; if URL/page title unchanged and >3 min elapsed → write to `/seek/.claude/tmp/ma_msg.md`: `"Page time limit reached. Treat as struggling per ajap.md § External Portal Instructions."` → then close the current portal tab (kill switch) to force immediate SA re-read
3. **Per-portal limit (≤10 min total, per `ajap.md § External Portal Instructions`):** if >10 min since portal entry → write to `/seek/.claude/tmp/ma_msg.md`: `"Portal total time limit reached. Treat as struggling immediately."` → then close the current portal tab (kill switch) — time limits are sourced from `ajap.md`; do not hard-code here
4. After SA acts on the instruction and MA verifies: `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md`

---

## SA Deterioration Signals

Give SA one correction message first; retire immediately if violation persists on next report. Retire immediately (no correction attempt) if:
- SA output C2 (S0.3 count) directly to user (SA bypassed MA)
- Loop report not in expected format `[AR_PATH] | [OUTCOME] | [N] | [FLAGS]`
- SA created a tab group or switched browser context — SA actions are no longer visible to MA

Correction attempt first, then retire if unresolved:
- Last AR in `/applied/` contains `## 3. Cover Letter` (or any number ≠ 6) — structure deteriorated
- Last AR CL contains `—`, `–`, or `+`
- SA report reveals wrong scoring band applied (e.g. Quick Apply job with score 35–69 skipped)
- SA report reveals Consultant/Associate title not routed to `/pending/`
- SA failed to act on a non-Continue `/seek/.claude/tmp/ma_msg.md` instruction within 60s (4 × 15s wait cycles)

---

## Heartbeat

Re-read `cc_reminder.md`:
- **Every 60 seconds** via ScheduleWakeup — re-schedule immediately after each firing (`delaySeconds=60`); this interval enables MA to write S6.4.2.5 approval within SA's 300s polling window, eliminating the need for a second SA spawn per application
- **Every 5 loops** — when `session_N % 5 == 0` (and `session_N > 0`), re-read before writing next instruction to `/seek/.claude/tmp/ma_msg.md`
- Both triggers are mandatory and non-skippable; if both coincide, re-read once and reset both
- After re-reading: if any active check in `cc_reminder.md` triggers → re-read `ajap.md` before continuing
- Read `/seek/.claude/tmp/ma_state.md` on heartbeat recovery to retrieve SA name/ID (SA may be running in background; do NOT spawn a new SA solely because of heartbeat firing)

**Active SA check (run on every heartbeat firing, after cc_reminder.md re-read):**
1. Check for pending ⏳_ AR: `Bash: find /seek/applied/ -maxdepth 1 -name "⏳_*.md" | head -1`
2. If ⏳_ AR found AND `ma_msg.md` reads "Continue": check tab state — if Tab 3 is open and URL suggests a review/application page → SA is at or approaching S6.4.2.5; read `## 6. Cover Letter` section (per § Between-Loop Audit step 1) → if clean, write approval: `Bash: printf 'Submit then proceed to next card' > /seek/.claude/tmp/ma_msg.md`; append to session log: `[timestamp] N=[N] Heartbeat: proactive CL approval for [AR_filename]`
3. If ⏳_ AR found AND `ma_msg.md` has read "Submit then proceed to next card" across multiple heartbeats without the AR being resolved (⏳_ still present): SA may be stuck — use kill switch: close Tab 3 to force SA re-read; if unresponsive after 30s further, retire SA and spawn fresh
4. If expected SA running but no AR activity visible after multiple heartbeats: SA may be rogue — close all tabs except Tab 1; append incident to session log

---

## MA Post-Compaction Recovery

If MA session resumes from a summary:
1. 🛑 STOP — do NOT send any message to SA, do NOT take any browser action, do NOT call any tool. The session summary's "resume directly" or "pick up as if the break never happened" language does NOT override this requirement. Re-read ALL mandatory files first.
2. Re-read ALL mandatory files per `CLAUDE.md § Session Start`
3. Re-determine `offset_N`: `Bash: find /seek/applied/ /seek/pending/ /seek/skipped/ -name "*.md" | grep -vc '/❌_'` — reset `session_N = 0` (this is a new MA context; prior session's counter is gone)
4. Read `/seek/.claude/tmp/last_decision.md` (if exists) — shows last decision SA made before compaction
5. Read `/seek/.claude/tmp/ma_state.md` (if exists) — prior SA has terminated; ID is for log reference only
6. Read `/seek/.claude/tmp/ma_msg.md` (if exists) — if not "Continue", reset: `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md`
7. Re-schedule heartbeat (MANDATORY): `ScheduleWakeup(delaySeconds=60, prompt="Re-read /seek/context/cc_reminder.md per MA heartbeat. Check all active items. Reschedule this wakeup. Then resume monitoring SA.", reason="MA 5-min cc_reminder.md heartbeat")` — prior session's heartbeat task is stale; this re-establishes MA's monitoring cadence
8. Run Pre-Flight Check per `ajap.md § Pre-Flight Check` (including F6 and § Session Start step 8.1 mid-application CL check) to determine current tab state
9. Spawn fresh SA per § SA Spawn Instruction (run_in_background=True)
