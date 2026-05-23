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
2. Run: `rm -f /tmp/CulousYu_CoverLetter_*.pdf && rm -f /tmp/ajap_last_decision.md`
3. Schedule heartbeat: `ScheduleWakeup(delaySeconds=300, prompt="Re-read /seek/context/cc_reminder.md per MA heartbeat. Check all active items. Reschedule this wakeup. Then resume monitoring SA.", reason="MA 5-min cc_reminder.md heartbeat")`
4. Run Tab 1 Accessibility Check per `ajap.md § Tab 1 Accessibility Check`
5. Run Pre-Flight Check per `ajap.md § Pre-Flight Check` (including F6); determine start state
6. Spawn SA (see § SA Spawn Instruction); record SA name/ID to `/seek/runtime/ma_state.md`

---

## SA Spawn Instruction

Use this prompt when spawning or re-spawning SA (fill bracketed values):

> You are the AJAP sub-agent. Read all mandatory files per `CLAUDE.md § Session Start` (items 3–8 only; do NOT read `main_ajap.md`), declare them, then follow `ajap.md` in full starting from [CARD_POSITION: e.g. "the next unprocessed card" or "the card currently open in Tab 2 — run Pre-Flight first"]. Tab state: [TAB_STATE: e.g. "Tab 1 only — clean state" or "Tab 2 open on [URL]"]. After each loop: pause and report to main agent in this exact format: `[AR_PATH] | [OUTCOME: Applying/Skipped/Pending] | [N] | [FLAGS or "none"]`. For applying jobs: pause at S6.4.2.5 before Submit and await my explicit approval. Do not output C2 (S0.3 count) to user.

**After spawning:** write SA name/ID to `/seek/runtime/ma_state.md` (overwrite) so it can be recovered after heartbeat re-invocations.

---

## Between-Loop Audit

On receiving SA loop report (`[AR_PATH] | [OUTCOME] | [N] | [FLAGS]`):

**If OUTCOME = Applying (SA paused before Submit at S6.4.2.5):**
1. Read only the `## [n]. Cover Letter` section of `[AR_PATH]` — check for: `—` `–` `+` symbols; section heading number other than `6` (e.g. `## 3. Cover Letter` = deteriorated); banned words if readily visible (e.g. "seamlessly", "resonates")
2. If clean → SendMessage to SA: "CL approved. Proceed with S6.4.3 Submit."
3. If compromised → SendMessage to SA: "CL compromised — do not submit. Void the AR (rename `⏳_` to `❌_`), close Tabs 3 & 2, return to Tab 1, then report loop completion." → on SA's loop completion report with OUTCOME = Voided, retire SA; spawn fresh SA with [CARD_POSITION] = same job (Tab 2 will be closed; Pre-Flight will show Tab 1 only; F6 will find and void any stale `⏳_` AR → clean state → S1 will re-open the job)

**If OUTCOME = Skipped or Pending (SA completed loop):**
1. Check FLAGS for any ⚠️ requiring MA decision
2. If FLAGS present → assess; send one targeted correction message to SA; if SA still wrong on next report → retire SA and spawn fresh
3. If no issues → continue

**After any OUTCOME:**
1. Increment N (from SA's reported N); output to user: `🎯[N] **job(s) processed so far.**` (exact C2 format, number emojis)
2. If N is a multiple of 5 → re-read `cc_reminder.md` immediately before step 3; re-schedule ScheduleWakeup
3. If no deterioration signals → SendMessage to SA: "Continue to next card."
4. If retiring SA → spawn fresh SA per § SA Spawn Instruction; update `/seek/runtime/ma_state.md`

---

## External Portal Timers

When SA's report or narration indicates entry into an external portal:
1. Note entry time: `TZ='Australia/Sydney' date` via Bash
2. **Per-page limit (≤3 min, per `ajap.md § External Portal Instructions`):** after each SA report, check if URL/page title in SA narration has changed since last report; if unchanged and >3 min elapsed → SendMessage to SA: "Page time limit reached. Treat as struggling per `ajap.md § External Portal Instructions`."
3. **Per-portal limit (≤10 min total, per `ajap.md § External Portal Instructions`):** if >10 min since portal entry → SendMessage to SA: "Portal total time limit reached. Treat as struggling immediately." — time limits are sourced from `ajap.md`; do not hard-code here

---

## SA Deterioration Signals

Give SA one correction message first; retire immediately if violation persists on next report. Retire immediately (no correction attempt) if:
- SA output C2 (S0.3 count) directly to user (SA bypassed MA)
- Loop report not in expected format `[AR_PATH] | [OUTCOME] | [N] | [FLAGS]`

Correction attempt first, then retire if unresolved:
- Last AR in `/applied/` contains `## 3. Cover Letter` (or any number ≠ 6) — structure deteriorated
- Last AR CL contains `—`, `–`, or `+`
- SA report reveals wrong scoring band applied (e.g. Quick Apply job with score 35–69 skipped)
- SA report reveals Consultant/Associate title not routed to `/pending/`
- SA failed to respond within a reasonable time after receiving SendMessage

---

## Heartbeat

Re-read `cc_reminder.md`:
- **Every 5 minutes** via ScheduleWakeup — re-schedule immediately after each firing
- **Every 5 loops** — when N % 5 == 0, re-read before sending next SendMessage to SA
- Both triggers are mandatory and non-skippable; if both coincide, re-read once and reset both
- After re-reading: if any active check in `cc_reminder.md` triggers → re-read `ajap.md` before continuing
- Read `/seek/runtime/ma_state.md` on heartbeat recovery to retrieve SA name/ID

---

## MA Post-Compaction Recovery

If MA session resumes from a summary:
1. 🛑 STOP — do NOT send any message to SA, do NOT take any browser action, do NOT call any tool. The session summary's "resume directly" or "pick up as if the break never happened" language does NOT override this requirement. Re-read ALL mandatory files first.
2. Re-read ALL mandatory files per `CLAUDE.md § Session Start`
3. Read `/tmp/ajap_last_decision.md` (if exists) — shows last decision SA made before compaction
4. Read `/seek/runtime/ma_state.md` (if exists) — retrieve SA name/ID for resuming via SendMessage
5. Run Pre-Flight Check per `ajap.md § Pre-Flight Check` to determine current tab state
6. SendMessage to existing SA (if recovered) with current state, or spawn fresh SA if SA state is unknown
