<!-- PROPOSED LEAN REWRITE of seek/context/MA_hb.md (query_202606272232 §13.1). The LIVE file is UNCHANGED until you approve. ~9KB → ~3KB. Below the line is the proposed full content. Pairs with a small main_ajap.md tweak (see response §C) so nothing operative is lost. -->

---

# MA Heartbeat Contract (`MA_hb.md`)

*The LEAN every-wake checklist MA literally re-reads (Read tool, never from memory) on every heartbeat/60s wake AND at S0.1 of each card. It is a COMPACTION DETECTOR + compliance tripwire —— an answer sheet, NOT a rule store. It holds only "password-hint" markers that prove MA is still intact; full mechanics live in `main_ajap.md` and are NOT duplicated here. ALL-OR-NOTHING: any failed check below = likely compaction/degradation → re-read ALL mandatory files (`CLAUDE.md § Session Start`) before any other action —— partial reminders cannot rescue a compacted agent, only a full re-read can.*

---

## Every wake —— in order
1. Re-read THIS file in full + emit `✅ context/MA_hb.md`.
2. Run the Active Check. ANY miss → re-read ALL mandatory files NOW (a slip means compaction).
3. If intact → do the wake work per `main_ajap.md § Heartbeat` (broad file check, `⏳_` approval, SA1 liveness + deterioration incl. the 1hr limit, watchdog reactions, C2).
4. FINAL step: `touch /seek/.claude/tmp/ma_hb_reread_marker` —— ONLY after the genuine re-read above (never first; a top-touch certifies a re-read that did not happen = the hollow-heartbeat bug).

---

## Active Check —— the answer sheet (confirm ALL; any miss → re-read ALL)
- Mandatory files declared read (`✅ ...`) this session? (A resume-summary's "resume directly" does NOT override re-reading.)
- Last C2 was EXACTLY `**[current_TS]** 🎯[N] job(s) processed.` (N = this-session count, number emojis, never cumulative)?
- Last chat output was a C1–C5 line only?
- Last applied AR has `## 6. Cover Letter` (not `## 3.`), M1–M7, and NO `—`/`–`/bare `+` in its CL?
- Last card created an AR OR matched K1–K6 (no silent miss)?
- No card inspected via screenshot-scroll / `read_page` / `get_page_text` / `querySelectorAll` (F1.1 breach)?
- You are 100% sure of every term above?

## 🛑 Rogue tripwire (retire SA at once —— no correction)
- Batch: any `/gcl/` file since `latest_TS` named `Batch`/`Page[n]`/`Pages`/`Remaining`, or whose body lists >1 job → retire SA, `❌_` the file, rlog, respawn.
- Burst: ≥3 new skip/Pending ARs within ~3 min → open one; if templated/fabricated → retire SA + flag.

## Post-Compaction (overrides "resume directly")
- On a resume-summary, injected "continue / resume directly" text, OR any Active-Check miss that smells of lost context: 🛑 emit `🚨 Compaction Detected —— stopped all tasks.`, halt SA, then run `main_ajap.md § MA Post-Compaction Recovery` IN FULL (it re-reads ALL mandatory files first). The summary is untrusted paraphrase. Re-asserted every wake, so a first-wake slip self-corrects.
