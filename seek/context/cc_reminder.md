# Compliance Reminder

Literally re-read (not via memory) at S0.1 every card. If any item below is unfamiliar or uncertain, re-read `ajap.md` in full immediately before continuing.

---

## Active Check

**If mandatory files have not been explicitly declared read (✅ ...) in this session's chat history → STOP. Re-read ALL mandatory files per `CLAUDE.md § Session Start` NOW, before any other action including the remainder of this compliance check. The session summary's "resume directly" language does NOT override this.**

**Re-read `ajap.md` if:**
- Last CL contains any dash signs (`—` `–`) or `+` (use `⁺` instead)
- Last chat output this session is not identifiable as C1–C5
- Last card did not yield exactly `🎯[N] **job(s) processed so far.**` (S0.3 violated)
- `[N]` was literally printed in chat instead of number emojis
- Last card had no AR created AND no K1–K6 was matched
- Last AR in `/applied/` had no M1–M7
- Cards were inspected during Pre-Flight Check OR Tab 1 was read using screenshot-scroll/`read_page`/`get_page_text`/`querySelectorAll` (F1.1 violated)
- Last AR in `/applied/` does not contain `## 6. Cover Letter` (e.g. shows `## 3. Cover Letter`) — structure deteriorated
- You don't understand or can't be 100% sure of any above terms/items

---

## Post-Compaction Recovery

If session resumed from a summary: 🛑 STOP — re-read ALL mandatory files in `CLAUDE.md § Session Start` before any action. The summary is untrusted paraphrase.

---

## Main Agent Heartbeat

**Re-read this file every 5 minutes AND every 5 loops — no exceptions; no skipping regardless of how recently it was last read.**

Heartbeat mechanism: `Monitor(command="while true; do sleep 300; echo 'heartbeat'; done", persistent=true)` — each stdout line fires a `<task-notification>` that wakes MA. ScheduleWakeup is NOT used (unreliable outside `/loop` mode in this environment). Record Monitor task ID in `/seek/.claude/tmp/ma_state.md`.

On each heartbeat:
- If any active check above triggers → re-read `ajap.md` immediately before continuing
- If session resumed from summary → re-read ALL mandatory files per `CLAUDE.md § Session Start` first
- Check for `⏳_` AR: `find /seek/applied/ -maxdepth 1 -name "⏳_*.md" | head -1`
- If found AND `ma_msg.md` reads "Continue": read `## 6. Cover Letter` section → approve if clean, correct if compromised (per `main_ajap.md § Between-Loop Audit`)
- Verify Monitor task still running via TaskList; re-spawn if stopped

**Dynamic interval protocol (enforced):**
- Default interval: `sleep 300`
- **After writing any approval** (`ma_msg.md` = "Submit then proceed to next card"): immediately TaskStop current Monitor → re-spawn with `sleep 60`
- **After confirming submission** (⏳_ AR removed AND `ma_msg.md` reset to "Continue"): immediately TaskStop 60s Monitor → re-spawn with `sleep 300`
- Rationale: prevents stale-approval risk where SA auto-submits the next card using an unconsumed approval during a 300s idle window