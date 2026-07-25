# Response to ccsim_query_202607252223.md
*Thoughts on all pts; sprint to follow*

## 37. Answers —— `ccsim_response_202607251750.md`

### 37.1. re 11 —— nlint Yellow
- 37.1.1. Accepted, already the shipped behaviour. No further change.

### 37.2. re 12.2.1 —— §7.2 vs Skills
- 37.2.1. My call: KEEP §7.2, don't migrate. Reason —— they fail differently, so the redundancy is real cover, not duplication.
- 37.2.2. §7.2 is deterministic-ish (I read it every session, it never mis-matches); a skill descr is probabilistic (a matcher decides).
- 37.2.3. Migrating would trade a guaranteed read for a probabilistic one —— strictly worse for the exact files that already under-trigger.
- 37.2.4. Your `profile.md` observation is the real signal: NEVER triggered means its descr is too abstract ("user's PERSONAL background needed") —— nobody phrases a request that way.
- 37.2.5. So the fix is descr quality, not relocation: an SA reads each pcmd and writes descrs from CONCRETE situations, not abstract categories.
- 37.2.6. Doing this in the sprint, `profile` first as the worked example.

### 37.3. re 12.2.2 —— Context Accumulation (important)
- 37.3.1. Short answer: NO accumulation. Your concern does not materialise.
- 37.3.2. The skill listing sits in the SYSTEM PROMPT —— re-sent each turn, but it REPLACES itself; it never stacks.
- 37.3.3. It is also hard-capped: the harness reserves `~`1% of the context window for the whole listing (a real setting, `skillListingBudgetFraction`), and shortens descrs to fit rather than overflowing.
- 37.3.4. So 15 skills vs 5 costs a fixed, bounded sliver —— it does NOT grow as a session lengthens.
- 37.3.5. What DOES accumulate is the one-off system notice when a NEW skill appears mid-session (we saw those). Trivial, and only when creating skills.
- 37.3.6. Net: your 100%-context sessions are not threatened by skill count. Descr QUALITY is the only real cost lever.

### 37.4. re 12.3 —— OTG
- 37.4.1. Noted, treated as a non-factor from here.

### 37.5. re 12.6 —— `skiller.md`
- 37.5.1. Agreed, and I like the loop framing. Creating `cp/ccsim/skiller.md` —— the house style for writing a skill descr (hybrid = task-shape clause + concrete keyword tail), plus the anti-patterns we already learnt (abstract categories, restating the manual trigger, duplicating hlint).
- 37.5.2. Name: keeping `skiller.md` —— it is unambiguous and matches `hook_guide.md` as a sibling.

### 37.6. re 14 —— Chrome
- 37.6.1. SA is reading your 3 screenshots to confirm Mandatory/Machine actually landed before I give a verdict.
- 37.6.2. Provisional: hours elapsed, Chrome relaunched, folder did NOT return —— that is the behaviour we wanted.
- 37.6.3. On removing the `.mobileconfig`: the INSTALLED profile must stay (it IS the policy). The FILE in `sessions/` is just the installer —— safe to delete, but I would keep it: it is your re-install kit after a wipe, and doomsday cover. Verdict after the SA confirms.

### 37.7. re 15 —— Rename Logic (partly disagree)
- 37.7.1. You are RIGHT on the big one: `dlint_hook.py` only ever calls `dlint.py --quick`, so `dlint_quick.py` is the honest name. Doing it.
- 37.7.2. You are right that `.sh` files are the actual registered hooks.
- 37.7.3. But the tidy "5 pairs" story does NOT hold, and I would rather correct it than build a false symmetry.
- 37.7.4. The `.sh` shims exist for ONE reason: PostToolUse fires on EVERY edit, so a bash gate avoids spawning Python needlessly. That is dlint, nlint, tlint only.
- 37.7.5. clint fires once per TURN (Stop); hlint once per PROMPT. There is nothing to save —— a shim there would add a process, not remove one.
- 37.7.6. So the true story: 5 lints; 3 are high-frequency and carry a `_hook.sh` gate; 2 are low-frequency and are registered directly. I will state exactly this in `hook_guide.md`.
- 37.7.7. Naming still gets consistent: `dlint_hook.sh` → stays, `nlint.sh` → `nlint_hook.sh`, `tlint.sh` → `tlint_hook.sh`. So every `.sh` carries `_hook`, and no `.py` does.

### 37.8. re 17.2 —— Good Now?
- 37.8.1. Yes. Three of five are confirmed firing live this session (dlint blocked me twice, clint blocked me once, hlint injected reminders in your last three prompts). nlint/tlint are same-mechanism and registered.

### 37.9. re 17.3 —— Doomsday (you spotted a real hole)
- 37.9.1. Correct, and important: `~/.claude/settings.json` is OUTSIDE the repo, so GH does NOT restore it. A clean restore would come back with ALL hooks silently dead —— exactly the failure we just spent two sessions on.
- 37.9.2. Updating `doomsday.md` with the re-registration step, pointing at the reference JSON, plus the one-edit probe verification.

### 37.10. re 17.4/17.5 —— Covered
- 37.10.1. Agreed —— `hook_guide.md` supersedes the memory suggestion (a file beats a memory here: versioned, reviewable, CCSIM-owned).

### 37.11. re 17.6 —— Reminder Hooks
- 37.11.1. coding.md hook: doing it (rule is mechanical —— target is `.py`/`.sh`/pcmd).
- 37.11.2. writing.md: your keyword heuristic is the right shape. Implementing as a YELLOW nudge on `hello`/`dear`/`greetings`/`regards`, plus a few I would add (`sincerely`, `best wishes`, `to whom it may concern`, `yours`), and it will also suggest CONSIDERING `## Stylisation`.
- 37.11.3. Deliberately non-blocking —— a deliverable false-positive that blocks a write would be worse than a missed nudge.

### 37.12. re 17.7 —— Skill Descrs
- 37.12.1. Yes, doing all of them, governed by the new `skiller.md`.

## 38. Answers —— `ccsim_response_202607251917.md`

### 38.1. re 25 —— Harness Engineering
- 38.1.1. Yes, precisely that, and it is worth naming. We are not writing content —— we are engineering the environment that makes correct behaviour automatic rather than remembered.
- 38.1.2. That IS what CCSIM is for, and it is why this session's finding is worth more than any single deliverable.

### 38.2. re 27 —— Covered
- 38.2.1. The user-level vs project-level rule is the CENTRAL fact of `hook_guide.md`.

### 38.3. re 28 —— Chat Prose This Turn
- 38.3.1. I will report honestly in the Sprint Report, including whether clint fired.
- 38.3.2. Caveat for fairness: you granted an explicit override for the ≤15w chat reply two turns ago, and clint correctly fired on it (mechanically right, contextually expected). Overrides are the one class where a clint hit is not a defect.

### 38.4. re 30.1 —— Why User-Level
- 38.4.1. Technically necessary, not preference: Desktop ignores project-level hooks entirely. Repo-level registration is a no-op there —— that is the whole bug.
- 38.4.2. And yes, this confirms your 17.3 suspicion exactly. Mitigations: the reference JSON is tracked in-repo, and doomsday.md will carry the restore step.

### 38.5. re 30.2 —— Compaction + date_added
- 38.5.1. post_compact is now registered and repo-scoped; I hand-tested all five branches. It has not yet fired for real (needs an actual compaction) —— I will not claim victory until it does.
- 38.5.2. `date_added.py` reminder: it preserves a file's macOS "Date Added" across your edits. Without it, every time I edit a file under `sessions/` or `AJAP_repo/inv/`, that file jumps to the top of a Date-Added sort and your chronological ordering silently rots.
- 38.5.3. Verdict: still useful, keep. It is also why DATS behaves. Re-registered.

### 38.6. re 30.3 —— Widening Scope (agreed, good call)
- 38.6.1. Agreed and doing it: hlint and tlint lose the repo guard (all repos), clint/dlint/nlint stay dupbus-only.
- 38.6.2. Rationale check that makes me confident: hlint is pure advisory (never blocks), tlint is warn-only —— both safe everywhere. clint enforces a dupbus-specific chat rule and dlint/nlint enforce dupbus comms conventions —— those would be wrong elsewhere.
- 38.6.3. Your §33.4 point is the clincher: an AJAP `#name` silently not firing cost you 100⁺ hours. A global hlint is the cheapest possible insurance against a repeat.

### 38.7. re 30.5 —— Move the Reference
- 38.7.1. Agreed —— `cscpt/` is for runnable scripts; a JSON reference is not one. Moving to `.claude/`.

### 38.8. re 32.2 —— clint Firing Model
- 38.8.1. Yes: a block costs one extra turn, because exit-2 stderr is the ONLY channel that reaches me on Stop.
- 38.8.2. Frequency: once per STOP-CYCLE, re-armed by each genuine user message. So practically once per your message, never once per session, and it cannot loop.
- 38.8.3. On demoting: a pure yellow would be useless —— a non-blocking Stop message reaches only YOU, never me. That was the original bug.
- 38.8.4. So your HYBRID is the correct design and I am implementing it: RED block on the first breach of a user turn, then YELLOW (log-only) for the rest of that turn. One split maximum, nudging preserved, no repeat splits.

### 38.9. re 32.4 / 33.1 / 33.2 —— Noted for `#close`
- 38.9.1. Recording both: the prose-breach history, and the attitude lesson.
- 38.9.2. On the attitude point, plainly: twice I stated a conclusion more broadly than my evidence supported ("no hook has ever fired", "not fixable from inside the repo"), and both times your pushback —— not my own checking —— caught it. The specific failure was treating MY OWN manual verification as evidence the SYSTEM worked. I have taken the concrete lesson, not just the apology: the probe file now exists so that claim can never again rest on my say-so.

### 38.10. re 33.3 / 33.4 —— Covered / Yes
- 38.10.1. All answered above; nothing missed as far as I can see.
- 38.10.2. AJAP widening confirmed for hlint + tlint (§38.6).

## 39. Housekeeping A & B —— Agreed in Full
- 39.1. Housekeeping A (top comments of the 5 lints + `cscpt/README.md` accuracy) runs FIRST, as you sequenced.
- 39.2. Suggestion 1 —— `cp/ccsim/hook_guide.md`, keeping your name. It will record the UNDERLYING logic, and I will state the failure honestly as you framed it: the error was not recommending the CLI, it was proposing an unsustainable workaround instead of finding the real cause.
- 39.3. Suggestion 2 —— hook content migrates out of `cscpt/README.md` into it.
- 39.4. Suggestion 3 —— NON-CCSIM / CCSIM split in every `cscpt/` script's top comment. Using Opus SAs as you suggest.
- 39.5. Suggestion 4 —— every script descr trimmed to ≤30w.
- 39.6. Suggestion 5 —— the funnel mandate goes above § Scripts, including the escalation step (alert user, request approval, append to `backlog.md`) when the ≤30w line and the NON-CCSIM block both fail. That escalation is the feedback loop that keeps the docs honest.
- 39.7. Suggestion 6 —— CCSIM-by-default editing rule, with the queued-query path for large edits and the mandatory backlog entry for self-serve edits.
- 39.8. New skill `cscpt` —— agreed, scoped to "about to run a `cscpt/` script", explicitly NOT the 5 lints (mechanical now). Checking that `writing` genuinely covers dlint FULL mode and adjusting if not.
- 39.9. Caveat —— no hard-coded script names in `README.md` (except `dark_mode.html`). Noted as a standing rule; I will phrase entries so the list can change without the prose rotting.

## 40. On the Analogy
- 40.1. It lands, and it changed how I will write the docs, so it did its job.
- 40.2. The part I will actually encode: a general fixing rust on the spot STILL reports it. That is the `backlog.md` entry after a self-serve edit —— the rule that stops silent drift.
- 40.3. The deeper point I take: my client is the OTHER CC, and my job is that she achieves her goal reading as little as possible. That reframes `README.md` from "documentation" to "an interface with a token budget".
- 40.4. Recording it in `close_` per your note; extracting only the rules above into the files.

## 41. Sprint
- 41.1. `#sprint` starting now; `slog_` created. Sprint Report will be appended here as new pts, per your update rules.
