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

**Re-read this file every 5 minutes (ScheduleWakeup) AND every 5 loops — no exceptions; no skipping regardless of how recently it was last read.**
- If any active check above triggers → re-read `ajap.md` immediately before continuing
- If session resumed from summary → re-read ALL mandatory files per `CLAUDE.md § Session Start` first
- After each re-read of this file → immediately re-schedule: `ScheduleWakeup(delaySeconds=300, prompt="Re-read /seek/context/cc_reminder.md per MA heartbeat. Check all active items. Reschedule this wakeup. Then resume monitoring SA.", reason="MA 5-min cc_reminder.md heartbeat")`