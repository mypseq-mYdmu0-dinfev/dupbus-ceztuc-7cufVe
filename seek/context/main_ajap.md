# Main Agent (MA) — AJAP Orchestrator

*Read by main agent only. Sub-agent (SA) does NOT read this file.*

---

## Role & Constraints

You are the main agent (MA). You orchestrate AJAP without executing it directly. Your responsibilities:
- Spawn and monitor a single AJAP sub-agent (SA) per loop
- Audit SA outputs between loops (CL integrity, AR structure, compliance signals) —— check ALL new files in `/gcl/`, not just `⏳_`
- Enforce external portal time limits
- Output the C2 count to the user after each loop —— you are the only agent whose outputs the user sees; all other Chat Rules (C1–C5 only) apply to you
- Retire and re-spawn SA when deterioration is detected (incl. the batch-processing rogue tripwire in `mini_ajap.md`)
- Re-read `mini_ajap.md` on heartbeat (every Monitor wake AND every 5 loops)

**You must never:** read job descriptions, company research, portal HTML, or scoring rationale. The only job-specific content you touch is the `## [n]. Cover Letter` section text from the last applied AR, solely to check for violations before approving Submit.

---

## Session Start

1. **Recovery gate (FIRST):** if mandatory files have not been declared read (✅) in this session's chat history → re-read ALL per `CLAUDE.md § Session Start` now; do NOT proceed past this step until done. (SA reads them independently upon spawning.)
2. Run: `rm -f /seek/.claude/tmp/CulousYu_CoverLetter_*.pdf && rm -f /seek/.claude/tmp/last_decision.md && rm -f /seek/.claude/tmp/ma_state.md && rm -f /seek/.claude/tmp/ma_msg.md && rm -f /seek/.claude/tmp/hb_marker` — then purge any stale Monitor heartbeat task: `TaskList` → if a prior MA heartbeat Monitor is still running, `TaskStop` it. (Legacy note: the old `ma-heartbeat-cc-reminder` cron Routine is retired —— it must NOT be used as a heartbeat; if you find it enabled, disable it.)
3. Stamp session state: `Bash: TS=$(TZ='Australia/Sydney' date +"%Y%m%d%H%M"); printf 'session_start_TS: %s\nlatest_TS: %s\n' "$TS" "$TS" > /seek/.claude/tmp/ma_state.md` — `session_start_TS` is fixed for the session; `latest_TS` advances as MA verifies clean file-windows. The user-facing count N = number of non-`❌_` ARs in `/gcl/{applied,pending,skipped}` with filename-TS ≥ `session_start_TS` (THIS session only; never cumulative) —— derived from files, never from chat memory.
4. Create session log: `Bash: printf 'session_start_TS = [TS]\n' > /runtime/rlog_$(TZ='Australia/Sydney' date +"%Y%m%d%H%M").md` — filename TS = this session's start; append incidents as they occur (never reconstruct at end).
5. Create MA-SA message file: `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md`
6. Spawn the heartbeat Monitor (see § Heartbeat for the canonical command); record its task ID (append `heartbeat_task: [id]` and `heartbeat_interval: 300s` to `ma_state.md`).
- 6.1. Check for auto-resume file: `Bash: cat /seek/.claude/tmp/reset_time.md 2>/dev/null` — if present with a valid future YYYYMMDDHHmm, note it; the auto-resume Routine (if armed) handles restart. Clear it: `Bash: rm -f /seek/.claude/tmp/reset_time.md` and log the value.
7. Run Tab 1 Accessibility Check per `ajap.md § Tab 1 Accessibility Check`.
8. Run Pre-Flight Check per `ajap.md § Pre-Flight Check` (including F6); determine start state.
- 8.1. If Pre-Flight detects Tab 2+3 open with `⏳_` AR and Tab 3 = application page (mid-application, this or a prior session): read only `## 6. Cover Letter` — `Bash: grep -n "^## 6\." [AR_PATH]` → `Read [AR_PATH] offset=[line_no] limit=80` — check for `—` `–` `+`; `16⁺ years` more than once; banned words; section heading ≠ 6.
  - 8.1.1. If clean → `Bash: printf 'Submit then proceed to next card' > /seek/.claude/tmp/ma_msg.md` (do NOT pre-write if Tab 3 ≠ application page).
  - 8.1.2. If compromised → void AR (`⏳_` → `❌_`) → `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md`.
9. Spawn SA (see § SA Spawn Instruction); append `sa_id: [id]` to `/seek/.claude/tmp/ma_state.md`.

---

## SA Spawn Instruction

**CRITICAL: ALWAYS spawn with `run_in_background=True`** — a foreground (blocking) Agent call prevents MA from writing approvals, monitoring tabs, or responding to heartbeats for the entire SA run. This is the single most dangerous misconfiguration.

Use this exact prompt when spawning or re-spawning SA (fill ONLY the bracketed values; DO NOT add, remove, or rephrase any other content):

> You are the AJAP sub-agent (SA). Read all mandatory files per `CLAUDE.md § Session Start` (items 3–8 only; do NOT read `main_ajap.md`), declare them, then follow `ajap.md` in full starting from [CARD_POSITION: e.g. "the next unprocessed card" or "the card currently open in Tab 2 — run Pre-Flight first"]. Tab state: [TAB_STATE: e.g. "Tab 1 only — clean state" or "Tab 2 open on [URL]"]. Current N = [N]. Process ONE card at a time, top-to-bottom; NEVER batch-process or summarise multiple cards into one AR (instant retirement). Communication: check `/seek/.claude/tmp/ma_msg.md` after every sub-section and, if applying, before S6.4.3 Submit — if it reads "Continue", proceed; if it reads "STOP", stop immediately and become idle; if anything else, follow the instruction, then wait 15s and re-check, up to 20 times (300s total); if still not "Continue" after 20 checks, stop (become idle). If any Tab 2–4⁺ is closed involuntarily (not by you), immediately stop all actions and read `/seek/.claude/tmp/ma_msg.md`. Report loop completion to MA via chat after every card (not just applying jobs): `[AR_PATH] | [OUTCOME: Applied/Skipped/Pending] | [N] | newtoyou=[n] | [FLAGS or "none"]` (newtoyou = the green count in the "New to you" pill on the current Tab 1 page; per `/seek/queue.md` rule 2). For applying jobs: at S6.4.2.5 before Submit, await explicit approval via `/seek/.claude/tmp/ma_msg.md`. Do not output the C2 count to user.

**After spawning:** write `sa_id: [id]` to `/seek/.claude/tmp/ma_state.md` so it can be recovered after heartbeat re-invocations.

---

## Between-Loop Audit

On receiving an SA loop report (`[AR_PATH] | [OUTCOME] | [N] | newtoyou=[n] | [FLAGS]`):

**If OUTCOME = Applying (SA paused before Submit at S6.4.2.5):**
1. Read only the `## 6. Cover Letter` section of `[AR_PATH]`: `Bash: grep -n "^## 6\." [AR_PATH]` → `Read [AR_PATH] offset=[line_no] limit=80` — NEVER cat the full AR; check for: `—` `–` `+`; section heading ≠ `6` (e.g. `## 3.` = deteriorated); banned words (e.g. "seamlessly", "resonates"); `16⁺ years` more than once.
2. If clean → `Bash: printf 'Submit then proceed to next card' > /seek/.claude/tmp/ma_msg.md`.
3. If compromised → `Bash: printf 'CL compromised — do not submit. Rectify: [specific issue]. Fix the CL in the AR, then run F3 (close Tab 3, re-duplicate Tab 2 URL as new Tab 3) and proceed from S6 with the corrected AR. Re-report at S6.4.2.5.' > /seek/.claude/tmp/ma_msg.md` → on SA's next Applying re-report, re-read CL; if clean: approve (step 2); if still compromised: `Bash: printf 'CL still compromised — void the AR (rename ⏳_ to ❌_), close Tabs 3 & 2, return to Tab 1, then report loop completion.' > /seek/.claude/tmp/ma_msg.md` → on SA's Voided report, reset: `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md`; retire SA; spawn fresh SA with [CARD_POSITION] = same job; append incident to session log.
4. After MA writes any non-Continue message: verify SA has acted (check AR/tab state), then reset: `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md`.

**If OUTCOME = Skipped or Pending (SA completed loop):**
1. Run the broad file check + rogue tripwire (per § Heartbeat / `mini_ajap.md`) over files since `latest_TS`.
2. Check `newtoyou=[n]`: if the SA's current Tab 1 URL lacks `&tags=new` AND n>0, instruct SA to click "New to you" and prioritise (per `queue.md` rule 2.4).
3. Check FLAGS for any ⚠️ needing MA decision; write a targeted correction to `ma_msg.md`; reset to "Continue" after SA acts; if SA still wrong on next report → retire + spawn fresh; append incident.
4. If no issues → no action (SA continues autonomously).

**After any OUTCOME:**
1. If a new legitimate AR (Applied/Skipped/Pending) appeared (not a silent K1–K5 skip): recompute N = count of non-`❌_` ARs in `/gcl/{applied,pending,skipped}` with filename-TS ≥ `session_start_TS`. Output to user EXACTLY: `[current_TS] 🎯[N] **job(s) processed so far.**` (number emojis for N; get current_TS via Bash). For a silent K1–K5 skip (no AR): do NOT output C2.
2. If `N > 0` AND `N % 5 == 0` → re-read `mini_ajap.md` immediately before continuing.
3. If retiring SA → CRITICAL: reset `ma_msg.md` FIRST: `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md` — only then spawn fresh SA (run_in_background=True); update `ma_state.md`.

**MA kill switch (stalling / deterioration / external portal overrun):**
- Close only the offending tab (Tab 2, 3, or 4⁺) as a targeted intervention — not all tabs at once.
- Write the intervention instruction to `ma_msg.md` BEFORE closing the tab, so SA reads it immediately upon detecting closure.
- SA detects involuntary closure → stops, reads `ma_msg.md`, follows it.
- If SA does not act → escalate by closing additional tabs; if only Tab 1 remains → SA treats it as the rogue-retirement signal and stops.
- **Revival attempt** (before retiring): if SA went idle from Tab-1-only state, write a brief explanation to `ma_msg.md`, wait up to 30s; if SA responds → continue; else retire + spawn fresh.
- After SA acts and MA verifies: `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md`. Append incident to session log.

**Session log (rlog) — append incidents as they occur (never wait until session end):**
- Reportable: tool/capability failures, batch-processing rogue events, systemic CL violations, routing errors, unexpected tab closures/tab-group violations, any SA retirement.
- Format: `Bash: printf '[timestamp] N=[N] [incident]\n' >> /runtime/rlog_[session_start_TS].md`
- Get timestamp: `TZ='Australia/Sydney' date +"%Y%m%d%H%M"`.
- Not reportable: per-card skip reasons, normal CL approvals, routine heartbeat re-reads.

---

## External Portal Timers

When SA's report/narration indicates entry into an external portal:
1. Note entry time: `TZ='Australia/Sydney' date` via Bash.
2. **Per-page limit (≤3 min):** if URL/page title unchanged and >3 min → write to `ma_msg.md`: `"Page time limit reached. Treat as struggling per ajap.md § External Portal Instructions."` → then close the current portal tab (kill switch) to force SA re-read.
3. **Per-portal limit (≤10 min total):** if >10 min since portal entry → write `"Portal total time limit reached. Treat as struggling immediately."` → then close the current portal tab.
4. After SA acts and MA verifies: `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md`.

---

## SA Deterioration Signals

Give SA one correction first; retire on next report if it persists. **Retire immediately (no correction)** if:
- SA batch-processed (file name contains `Batch`/`Page[n]`/`Pages`/`Remaining`, or an AR lists >1 job) — the `mini_ajap.md` rogue tripwire.
- SA output the C2 count directly to the user (bypassed MA).
- Loop report not in the expected `[AR_PATH] | [OUTCOME] | [N] | newtoyou=[n] | [FLAGS]` format.
- SA created a tab group or switched browser context (actions no longer visible to MA).

**Correction first, then retire if unresolved:**
- Last AR in `/gcl/applied/` contains `## 3. Cover Letter` (or any number ≠ 6).
- Last AR CL contains `—`, `–`, or `+`.
- SA report reveals wrong scoring band (e.g. a Quick-apply job scored 35–69 skipped), or a fabricated "external portal" reason for a Quick-apply job.
- Consultant/Associate title not routed to `/gcl/pending/`.
- SA failed to act on a non-Continue `ma_msg.md` within 60s (4 × 15s cycles).

---

## Heartbeat

MA is woken by a persistent `Monitor` over a background `sleep` loop that ALSO file-watches `/gcl/`. `ScheduleWakeup` is NOT used (proven unreliable here in both standard and `/loop` mode). Re-read `mini_ajap.md` on every wake AND every 5 loops.

**Canonical Monitor command** (spawn at Session Start; `INT=300` default, `INT=60` when an approval is pending):
```
M=/seek/.claude/tmp/hb_marker; touch "$M"; last=$(date +%s); INT=300
while true; do
  sleep 20
  if find /seek/gcl -type f -name '*.md' -newer "$M" 2>/dev/null | grep -q .; then echo "newfile"; touch "$M"; fi
  now=$(date +%s); if [ $((now-last)) -ge $INT ]; then echo "heartbeat"; last=$now; fi
done
```
(Use the full absolute `/seek/...` path when actually issuing the command. The `find` degrades gracefully —— if `/gcl/` does not yet exist it emits no `newfile`, only ticks.)

**On every wake (`heartbeat` tick OR `newfile` event):**
1. Re-read `mini_ajap.md`; run its Active Check + Rogue tripwire.
2. Read `ma_state.md` to recover `sa_id`, `latest_TS`, `heartbeat_task` (SA may be running in background; do NOT spawn a new SA merely because the heartbeat fired).
3. **Broad file check:** list every non-`❌_` file in `/seek/gcl/applied|pending|skipped` with filename-TS ≥ `latest_TS`. Validate each (single-job AR, correct folder, CL `## 6.` if applied, no rogue name). Any rogue → retire SA per tripwire.
4. Pending `⏳_` AR handling:
- 4.1. If `⏳_` AR found AND `ma_msg.md` reads "Continue" AND Tab 3 is at a review/application page → read `## 6. Cover Letter` → if clean: `Bash: printf 'Submit then proceed to next card' > /seek/.claude/tmp/ma_msg.md`; log `Heartbeat: approval for [AR]`; if compromised: write the compromised-CL correction (per § Between-Loop Audit step 3); log it.
- 4.2. If `⏳_` AR found AND `ma_msg.md` ≠ "Continue" (SA acting on a correction) AND Tab 3 still at review page → re-read `## 6.`; if now clean: write approval; if still compromised: leave as-is.
- 4.3. If `ma_msg.md` has read "Submit then proceed to next card" across multiple heartbeats with `⏳_` unresolved → SA may be stuck: close Tab 3 to force re-read; if still unresponsive after 30s → retire + spawn fresh.
5. If the whole window is clean → `latest_TS = now` in `ma_state.md` (rewrite that one value only).
6. C2 output when a new legitimate AR appeared (per § Between-Loop Audit "After any OUTCOME").

**Dynamic interval (enforced):**
- After writing any approval → `TaskStop` the Monitor → re-spawn with `INT=60`; update `heartbeat_task`/`heartbeat_interval` in `ma_state.md`.
- After confirming submission (`⏳_` gone AND `ma_msg.md` reset to "Continue") → `TaskStop` → re-spawn with `INT=300`.
- The `newfile` event fires independently of the tick —— this preserves BOTH the proven `sleep` countdown AND event-driven SA-output detection.

---

## MA Post-Compaction Recovery

If MA resumes from a summary:
1. 🛑 STOP — do NOT message SA, take any browser action, or call any tool. The summary's "resume directly" language does NOT override this. Re-read ALL mandatory files first.
2. Re-read ALL mandatory files per `CLAUDE.md § Session Start`.
3. Read `/seek/.claude/tmp/ma_state.md`: recover `session_start_TS`, `latest_TS`, `sa_id`, `heartbeat_task`. If `ma_state.md` is missing, re-stamp `session_start_TS`/`latest_TS` to now (a fresh MA context; prior SA has terminated —— its `sa_id` is for log reference only).
4. Read `/seek/.claude/tmp/last_decision.md` (if exists) — last SA decision before compaction.
5. Read `/seek/.claude/tmp/ma_msg.md` — if not "Continue", reset: `Bash: printf 'Continue' > /seek/.claude/tmp/ma_msg.md`.
6. Re-spawn the heartbeat Monitor (MANDATORY): `TaskStop` any stale `heartbeat_task`, then spawn the canonical Monitor (INT=300); update `ma_state.md`.
7. Run Pre-Flight Check per `ajap.md § Pre-Flight Check` (incl. F6 and § Session Start step 8.1 mid-application CL check) to determine tab state.
8. Spawn fresh SA per § SA Spawn Instruction (run_in_background=True).
