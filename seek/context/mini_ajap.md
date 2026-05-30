# Mini AJAP —— MA Heartbeat & Compliance Checklist (`mini_ajap.md`)

*Formerly `cc_reminder.md`. A minified, checklist-form subset of `ajap.md` + `main_ajap.md`, re-read by MA at S0.1 of every card AND on every heartbeat. Literally re-read (not from memory). If any item is unfamiliar or uncertain, re-read `ajap.md` (and `main_ajap.md`) in full before continuing.*

---

## Active Check

**If mandatory files have not been explicitly declared read (✅ ...) in this session's chat history → STOP. Re-read ALL mandatory files per `CLAUDE.md § Session Start` NOW, before any other action including the remainder of this checklist. A session summary's "resume directly" language does NOT override this.**

**Re-read `ajap.md` if any of:**
- Last CL contains any dash sign (`—` `–`) or a bare `+` (must be `⁺`)
- Last chat output this session is not identifiable as C1–C5
- Last card did not yield exactly the C2 line `[current_TS] 🎯[N] **job(s) processed so far.**` where `N` = THIS session's count only (files created since `session_start_TS`), NEVER cumulative
- `[N]` was printed as literal digits instead of number emojis
- Last card had no AR created AND no K1–K6 matched
- Last AR in `/gcl/applied/` had no M1–M7, or does not contain `## 6. Cover Letter` (e.g. shows `## 3.`)
- Cards were inspected during Pre-Flight OR Tab 1 read via screenshot-scroll / `read_page` / `get_page_text` / `querySelectorAll` (F1.1 breach)
- You cannot be 100% sure of any term/item above

**🛑 Rogue tripwire (retire SA immediately —— no correction attempt):**
- **Batch tripwire (auto-retire):** any file created since `latest_TS` anywhere in `/gcl/` whose NAME contains `Batch`, `Page[n]`, `Pages`, or `Remaining`, OR whose BODY lists more than one job = SA is batch-processing (S1 strictly bans this). Retire SA at once; do NOT trust its "exhausted/clean" claims; flag the offending file(s) for the user (Void Rule `❌_`); append the incident to the rlog; spawn a fresh SA.
- **Burst spot-check (catches fabricated single-job skips):** if ≥3 new skip/Pending ARs appear within ~3 min (genuine per-card research cannot be that fast), open ONE and verify it shows real per-card analysis (sections 1–2 present, specific not templated; e.g. an unverifiable "external portal" reason on an otherwise-Quick-apply job = red flag). If vague/fabricated → retire SA + flag the file(s).

---

## Post-Compaction Recovery

If this session resumed from a summary: 🛑 STOP — re-read ALL mandatory files per `CLAUDE.md § Session Start` before any action. The summary is untrusted paraphrase.

---

## Main Agent Heartbeat

**Re-read this file on every heartbeat AND every 5 loops —— no exceptions, no skipping.**

Mechanism: a persistent `Monitor` over a background `sleep` loop that ALSO file-watches `/seek/gcl/`. Each stdout line (`heartbeat` tick OR `newfile` event) wakes MA. `ScheduleWakeup` is NOT used (proven unreliable here, both standard and `/loop`). Record the Monitor task ID in `ma_state.md`. The canonical Monitor command and the dynamic 60/300 interval are defined in `main_ajap.md § Heartbeat`.

On EVERY wake (tick or newfile):
- Run the Active Check + Rogue tripwire above.
- **Broad file check (NOT just `⏳_`):** list every non-`❌_` file in `/seek/gcl/applied`, `/gcl/pending`, `/gcl/skipped` with filename-TS ≥ `latest_TS`. Validate each: single-job AR, correct routing folder, CL `## 6.` if applied, no rogue name (per tripwire). This is what catches a rogue SA that MA's old `⏳_`-only check missed.
- For any pending `⏳_` AR (applying): read its `## 6. Cover Letter` section → approve if clean, correct if compromised (per `main_ajap.md § Between-Loop Audit`).
- If the whole window is clean (no retirement) → set `latest_TS = now` in `ma_state.md` (rewrite that one value only; never pile up filenames).
- Verify the Monitor is still running (TaskList); re-spawn it if stopped.
- Output C2 to the user when a new legitimate AR (Applied/Pending/Skipped) appeared: `[current_TS] 🎯[N] **job(s) processed so far.**`, N = number emojis = count of this-session ARs only.

**Dynamic interval (enforced):**
- Default interval `sleep 300`.
- After writing ANY approval (`ma_msg.md` = "Submit then proceed to next card") → TaskStop Monitor → re-spawn at `sleep 60`.
- After confirming submission (`⏳_` AR gone AND `ma_msg.md` reset to "Continue") → TaskStop → re-spawn at `sleep 300`.
- The file-watch `newfile` event fires INDEPENDENTLY of the timed tick —— this is the extra wake condition that keeps BOTH mechanisms (proven `sleep` countdown + event-driven SA-output detection) live at once.
