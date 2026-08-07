# Hook Guide

## 0. Preamble

- 0.1. WSM worst-case hook latency: **`~`0.39 s** per interactive round trip.
  - 0.1.1. Re-measured 202608071235 after the stdin guards, mlint SHAPE C and PreCompact.
  - 0.1.2. Basis = largest `.md` in `sessions/` (109 KB) + largest transcript (50 MB).
  - 0.1.3. Round trip = one prompt, one `.md` write, one Bash call, one turn-end.
  - 0.1.4. Per event, medians of 5 on worst-case payloads:
    - 0.1.4.1. Stop 184 ms · PostToolUse 106 ms · PreToolUse-write 45 ms
    - 0.1.4.2. PreToolUse-Bash 33 ms · UserPromptSubmit 27 ms
  - 0.1.5. Each EXTRA `.md` write adds `~`0.15 s (45 + 106 per §0.1.4):
    - 0.1.5.1. An earlier `~`0.11 s counted PostToolUse alone and never reconciled
    - 0.1.5.2. Each extra Bash call adds `~`0.03 s
  - 0.1.6. Comfortably inside the 1 s budget (§12.4) —— `~`39%, with Stop now dominant.
  - 0.1.7. WSM only, interactive only —— SA/background work and OTGM are not counted.
  - 0.1.8. PreCompact + PostCompact EXCLUDED —— neither fires on an interactive round trip
  - 0.1.9. Re-measure and rewrite 0.1 EVERY time a hook is added, edited, or removed.
- 0.2. This file is the definitive, self-contained reference for CC hooks in this repo.
- 0.3. Read it BEFORE creating, editing, registering, debugging, or trusting any hook.
- 0.4. Everything needed is here —— no conversation or comms file is required or cited.
- 0.5. Lives in `ccsim/` because CCSIM owns the hook system.
- 0.6. `cscpt/README.md` describes each lint; this file describes the MACHINERY.

---

## 1. The Rule

- 1.1. Register EVERY hook in the USER settings file `~/.claude/settings.json`.
- 1.2. Hooks registered in the PROJECT file `.claude/settings.json` are a SILENT no-op in the Claude Desktop app.
- 1.3. "Silent" is literal —— no error, no warning, no log line, no chat notice; the app behaves exactly as if no hook existed.
- 1.4. The CLI does honour project-level hooks; the Desktop app is the daily driver here, so user-level is the only registration that works in practice.
- 1.5. NEVER register the same hook in both files —— a future Desktop fix would then double-fire everything.
- 1.6. `~/.claude/settings.json` is OUTSIDE this repo, so it is NOT under version control and NOT restored by a clone (recovery: §9).
- 1.7. Paths in the registration are ABSOLUTE, so a repo relocation silently kills every hook until they are re-pointed.
- 1.8. Because of 1.6, an edit to `~/.claude/settings.json` is only HALF done when it works —— the registration exists on one untracked drive and nowhere else. Mirror it in the same turn (§10), or the next drive failure takes every hook with it.

---

## 2. Why the Rule Exists

*History, stated honestly, because the diagnosis is more instructive than the fix.*

- 2.1. Five lint hooks (clint, dlint, hlint, nlint, tlint) were built across several sessions and registered in the PROJECT `.claude/settings.json`. Not one ever executed, and nobody noticed for weeks.
- 2.2. Each script was individually CORRECT —— piping a payload in by hand produced the right exit code every time.
- 2.3. That correctness is exactly WHY it went unnoticed: manual verification was repeatedly mistaken for evidence that the SYSTEM was wired.
- 2.4. "The script works" and "the harness invokes the script" are two independent claims; only the second one delivers any value, and only the second one was never tested.
- 2.5. The diagnosis was then over-generalised twice:
  - 2.5.1. First to "no hook fires in the Desktop app" —— false; user-level hooks fire fine.
  - 2.5.2. Then to "not fixable from inside the repo" —— false; the fix is a one-file merge into `~/.claude/settings.json`.
- 2.6. The proposed remedy —— switch to the CLI —— was the REAL error:
  - 2.6.1. Not because the CLI does not work; it does.
  - 2.6.2. But because it was an unsustainable workaround for a problem that had not actually been root-caused.
  - 2.6.3. The owner will not migrate to the CLI, so a fix predicated on that was worthless from the moment it was proposed.
- 2.7. The actual cause is narrow: the Desktop app ignores project-level hook registration and executes user-level registration. Nothing else was wrong.
- 2.8. Standing lessons:
  - 2.8.1. A workaround that changes the user's tooling is not a root cause —— keep digging until the defect is one sentence long.
  - 2.8.2. Never widen a negative finding ("X did not fire") into a universal ("X can never fire") without testing the narrower hypothesis first.
  - 2.8.3. A component that has never been exercised END-TO-END is not done, however well unit-tested (`universal/coding.md` § Testing).

---

## 3. Registered Hooks

*Intended live state. Restore-of-record is `.claude/hooks_user_settings.reference.json` (inert documentation; nothing loads it).*

| Event | Registered Command | Purpose |
|---|---|---|
| PreToolUse | `cscpt/DADC.py hook-capture` | Capture Date Added + Date Created before a write |
| PreToolUse | `cscpt/alint_hook.sh` | TEA1 in-flight gate (BLOCKS a commit/push whilst an SA or workflow runs) |
| PreToolUse | `cscpt/tlint_hook.sh` pre | Time-integrity: clock read without `TZ='Australia/Sydney'` (advisory) |
| PreToolUse | `cscpt/flint_hook.sh` pre | Filename gate (BLOCKS a stray-space comms filename) |
| PreToolUse | `cscpt/plint.py` | Protocol-read reminder before a write/read (advisory) |
| PostToolUse | `cscpt/DADC.py hook-restore` | Restore Date Added + Date Created after a write |
| PostToolUse | `cscpt/dlint_hook.sh` | Prose lint on every `.md` + deliverable gate (blocking) |
| PostToolUse | `cscpt/nlint_hook.sh` | Numbering-continuity lint (advisory) |
| PostToolUse | `cscpt/flint_hook.sh` post | Filename lint: timestamp clash + stray-space alert (warn-only) |
| PostToolUse | `cscpt/tlint_hook.sh` post | Time-integrity: drifted/unclocked comms timestamp + US dates (advisory) |
| UserPromptSubmit | `cscpt/hlint.py` | `#trigger` read-reminder (advisory) |
| Stop | `cscpt/clint.py` | No-chat-prose lint (WARN-only; never blocks) |
| Stop | `cscpt/mlint.py` | Owed-output gate (BLOCKS): the `#m2` interim declaration stopped AT or never emitted, or a compaction-opened turn missing root §5's `🚨` sentinel |
| PreCompact | `.claude/pre_compact.sh` | Plant root §5's sentinel demand INSIDE the summary being written (§13) |
| PostCompact | `.claude/post_compact.sh` | Alert the USER that a compaction happened (it CANNOT reach the model —— §6.9) |

- 3.1. Naming convention: a `*_hook.sh` IS the file the harness launches; the `.py` beside it is the lint body. Every `.sh` in `cscpt/` carries `_hook`, no `.py` does.
- 3.2. A lint gets a `.sh` gate exactly when its EVENT is high-frequency: the PostToolUse lints fire on every Edit/Write, and `alint` fires on every Bash call, so each shim spares a needless Python spawn on the overwhelmingly common irrelevant payload.
- 3.3. `clint.py` + `mlint.py` (Stop) and `hlint.py` (UserPromptSubmit) fire once per turn/prompt, so they are registered directly and correctly have no `.sh`. `plint.py` fires on writes and reads without one —— it needs the payload parsed either way, so a shim would buy nothing.
- 3.4. Registration entry shape matters: an event's array holds `{"matcher": …, "hooks": [{"type":"command","command":…}]}` objects. A bare `{"type":"command", …}` placed directly in the event array is the wrong shape —— check it against the live file before trusting any hand-written entry.
- 3.5. Matchers are TOOL-NAME only —— there is no path filter, which is precisely why each PostToolUse lint must do its own file-path check.
- 3.6. Every addition to this table costs latency on its event —— estimate it against §12 before registering, and alert the user if that event's worst case would exceed 1 s.

---

## 4. Global Reach & Self-Scoping

- 4.1. A user-level hook fires in EVERY project on this Mac, not just this repo —— that is the price of §1.
- 4.2. Mitigation: each repo-specific lint self-scopes via `_in_scope(data)` before doing anything else.
- 4.3. Scope signal order:
  - 4.3.1. Payload `cwd` (absolute path) —— in scope if it equals the repo root or is a sub-path of it, compared separator-bounded after `os.path.realpath` (a naive `startswith` would wrongly match a `…-sibling` directory).
  - 4.3.2. Fallback: the `transcript_path` project slug —— transcripts live at `~/.claude/projects/<slug>/<uuid>.jsonl`, where `<slug>` is the project directory with every `/` and ` ` replaced by `-`.
  - 4.3.3. Neither usable → FAIL OPEN, i.e. run the lint anyway.
- 4.4. Fail OPEN, never closed —— an unscopeable payload is not evidence of a different project, it is merely a shape that cannot be read, and a silently disabled lint is the EXACT failure this whole guide exists to prevent.
- 4.5. Anchoring:
  - 4.5.1. The repo root is always derived from the script's own `__file__`, never hard-coded, so the repo stays relocatable.
  - 4.5.2. Because a global lint routinely runs from OTHER repos, every path it resolves must be anchored on its own repo root, never on the process cwd —— nothing may reintroduce a cwd-relative path.
- 4.6. Which lints are scoped, and why the split is deliberate:

| Lint | Reach | Rationale |
|---|---|---|
| alint | Repo-scoped | BLOCKS a commit/push; enforces this repo's own TEA ordering |
| clint | Repo-scoped | Blocks a Stop; enforces this repo's bespoke no-chat-prose rule |
| dlint | Repo-scoped | Blocks on RED and blocks a comms write; enforces this repo's prose guide, deliverable rule and territory map |
| flint | Block: repo-scoped<br>Warn: GLOBAL | One file, two behaviours. Its PreToolUse block is scoped (out of scope it downgrades to an advisory rather than going quiet); its whole PostToolUse half is global, because a missed TS clash is silent and expensive and once cost real work in AJAP |
| nlint | Repo-scoped | Enforces this repo's numbering-continuity convention |
| hlint | GLOBAL | Advisory-only; a missed `#trigger` has already cost real work elsewhere |
| plint | GLOBAL | Advisory-only; always exits 0 and can never gate a write |
| tlint | GLOBAL | Advisory-only, never exits 2. Its drift checks are STRUCTURALLY scoped (they fire only inside dupbus `sessions/` or AJAP `inv/`); the clock-read and US-date checks are global on purpose, because root §2.1.7's Sydney mandate is a USER-level convention |
| mlint | Repo-scoped | BLOCKS a Stop; enforces this repo's `#m2` sequence and root §5's post-compaction sentinel |

- 4.7. The asymmetry is intentional, not an oversight —— the test rule is: a lint that can BLOCK must be repo-scoped, a lint that can only advise may be global.
  - 4.7.1. Never "tidy" a scope guard onto hlint, plint, or flint's PostToolUse half.
  - 4.7.3. The test is per-BEHAVIOUR, not per-FILE. `flint` proves it: `_in_scope()` guards its exit-2 and nothing else, so ONE script honours §4.7 twice over. Hoisting that guard to the top of its `main()` would silently delete AJAP coverage —— T8a–d in its suite fail if anyone does.
  - 4.7.2. Never remove one from clint, dlint, or nlint.
- 4.8. `.claude/post_compact.sh` carries the same guard in bash form, for the same reason.

---

## 5. Verified Payload Shapes

*Top-level keys observed live. `cwd` is present on real payloads but is the one field whose absence the guards must tolerate.*

- 5.1. All three events share: `session_id`, `transcript_path`, `prompt_id`, `permission_mode`, `hook_event_name`, and (normally) `cwd`.
- 5.2. PostToolUse adds: `effort`, `tool_name`, `tool_input`, `tool_response`, `tool_use_id`, `duration_ms`.
- 5.3. Stop adds: `effort`, `stop_hook_active`, `last_assistant_message`, `background_tasks`, `session_crons`.
- 5.4. UserPromptSubmit adds: `prompt`, `session_title`.
- 5.5. Fields that actually matter:

| Field | Where | Why It Matters |
|---|---|---|
| `cwd` | All | Primary repo-scope signal (§4.3.1) |
| `transcript_path` | All | Scope fallback; also the JSONL clint parses |
| `tool_input` | PostToolUse | Holds `file_path` + `content`; the only reliable target of a lint |
| `stop_hook_active` | Stop | True once Claude is continuing from a prior Stop-block —— the loop guard |
| `prompt` | UserPromptSubmit | The raw text to scan |
| `prompt_id` | All | Keys "have I already fired for this prompt?" ledgers |
| `last_assistant_message` | Stop | Convenience copy of the turn's final text |

- 5.6. `tool_response.filePath` mirrors `tool_input.file_path`, but prefer `tool_input` —— it is present on every tool variant.
- 5.6.1. SUB-AGENT vs MAIN AGENT (PreToolUse, live-captured across 8 real payloads from two concurrent SAs and the main agent): a SUB-agent's payload carries `agent_id` and `agent_type`; the main agent's carries neither. That pair is the ONLY reliable discriminator.
- 5.6.2. It is NOT the transcript path, however plausible that looks. A sub-agent's transcript RECORDS do live in `<session>/subagents/agent-<id>.jsonl` and never appear in the main session file —— yet its PAYLOAD still hands over the MAIN session `transcript_path`. Anything scoping on the path alone will read every sub-agent as the main agent.
- 5.6.3. AGENT DISPATCH IS NOT AGENT COMPLETION, and this trap sinks the obvious design for anything that waits on an SA. The Agent tool's `tool_result` lands within ~200ms of the call saying `toolUseResult.status: "async_launched"` —— it is an ACK. Completion arrives later and separately, as a `<task-notification>` carrying `<task-id>` and `<status>` (completed | killed | failed). Measured across 368 historical dispatches: every one acked instantly; 363 later notified.
- 5.6.4. That notification appears in THREE record shapes (`attachment`, `queue-operation`, `user` —— 233/431/270 historically), so match the RAW `<task-notification>` substring, never one named field. A WORKFLOW rests by the very same notification, carrying its `taskId` as the `<task-id>`, so one parser serves both. `cscpt/alint.py` is the worked implementation.
- 5.6.5. THREE async shapes, and the boundaries are measured, not assumed: an AGENT is `toolUseResult.isAsync` + `agentId` (368 records); a WORKFLOW is `taskId` + `taskType`, with `transcriptDir` and NO `isAsync`/`agentId` (40 records); BACKGROUND BASH is `backgroundTaskId`. Agents AND workflows are gated; background bash is excluded on purpose (root `CLAUDE.md` §9.05's Monitor loop would block every commit). ⚠️ `taskType` is MANDATORY when matching a workflow —— a bare `taskId` also appears on 110 TodoWrite ticks and on the Monitor loop's own record, so keying on it alone bricks every commit. A workflow must be gated in its own right: its child agents do NOT appear in the main transcript at all (0 of 14 on the verified run), so nothing else covers them. It ages by the newest mtime across its `transcriptDir` AND that directory's entries —— entries because appending to a file never touches its parent's mtime.
- 5.7. Never assume a key exists. Every lint must parse defensively and exit 0 on any missing field.
- 5.8. Payload shapes are harness-owned and can change without notice —— re-verify from a captured payload rather than from memory of this table.

---

## 6. Which Channel Reaches the Model

*The single most misunderstood point in the whole system. Writing to the wrong channel produces a lint that appears to work and changes nothing.*

| Event | Exit 0, Plain Text | Exit 0, `additionalContext` | Exit 2, stderr |
|---|---|---|---|
| PostToolUse | User only | Reaches the MODEL, no block | Reaches the MODEL as an error; write is NOT undone |
| PreToolUse | User only | Reaches the MODEL, no block | Reaches the MODEL and BLOCKS the tool call |
| UserPromptSubmit | Added to context | Reaches the MODEL, no block | Reaches the MODEL; avoid —— see 6.6 |
| Stop | NOWHERE (see §6.1) | Reaches the MODEL —— but WAKES it (§6.1.3) | Reaches the MODEL and BLOCKS the stop |
| PostCompact | User only | Not a supported channel | User only —— NOTHING reaches the model |
| PreCompact | Appended to the SUMMARISER's prompt (§13) | Not a supported channel | Exit 2 BLOCKS compaction —— never use |

- 6.1. ⚠️ CORRECTED 202608071530 —— the previous wording here was wrong in BOTH directions:
  - 6.1.1. Exit-0 plain stdout goes NOWHERE. The registry says "stdout/stderr not shown".
  - 6.1.2. Exit-0 `systemMessage` becomes a `hook_system_message` attachment: written to the transcript, mapped to the model as `()=>[]` (never seen), and rendered ONLY by the terminal UI —— the Desktop app carries no renderer for it, so in CCD it reaches NOBODY. 142 such records carrying clint's warnings sit unseen in this project's transcripts.
  - 6.1.3. Exit-0 `hookSpecificOutput.additionalContext` IS supported at Stop and DOES reach the model —— but it RE-INVOKES the model on the same continuation path as a block, capped by `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` (default 8). It is a block wearing a softer name.
  - 6.1.4. NET: at Stop there is no non-waking model channel, BY CONSTRUCTION —— the model has stopped, so reaching it means starting it again.
- 6.2. Consequence: a non-blocking Stop warning can NEVER make the agent self-correct —— its turn has already ended and it never sees the note.
- 6.3. Cost of a Stop block: exactly ONE extra model turn —— a full round trip, billed and consuming context. Spend it deliberately, at most once per prompt.
- 6.4. clint is WARN-ONLY —— every verdict exits 0 and nothing blocks. It once blocked (first RED per prompt, later ones logged), but forcing an extra turn each time cascaded into worse turn-end behaviour than the breaches themselves, so the owner demoted it.
- 6.4.1. ⚠️ The price, and it is worse than first recorded: a warn-only Stop hook reaches NEITHER the model NOR the user in CCD (§6.1.2). clint is a LOG and an invisible transcript record —— nothing more. Enforcement rests entirely on root `CLAUDE.md` §3.1.6's TEAs. To make a chat-discipline lint actually correct CC without forcing a turn, the channel must move OFF Stop —— UserPromptSubmit (next turn's opening context) or PostToolBatch (mid-turn, non-blocking) are the two that reach the model without waking it.
- 6.4.2. Breach classes survive in the log with a `yellow:` prefix (`yellow:prose`, `yellow:reader`, …); a lone `.` is CLEAN in both modes (`clean:dot` / `clean:dot_reader`).
  - 6.4.3. clint is not the only Stop hook: `mlint.py` DOES block, and the two are not in tension. clint enforces chat SHAPE, where a block forces a turn with nothing left to do —— the deadlock that got it demoted. mlint enforces `#m2` COMPLETION, where the forced turn IS the missing sprint, so the vacuum that produced the cascade cannot form. The test that separates them: does the blocked agent have real work to spend the extra turn on? Only block when the answer is yes, at most once per prompt, and name the escape (a lone `.`) inside the message. mlint blocks in THREE shapes. For the missing declaration the forced turn is ONE line —— small, but not empty in clint's sense: clint's content had already reached the `response_`, whereas this line reached nowhere. For the missing post-compaction sentinel (root §5) the forced turn carries the sentinel, the halt, and both §5.3/§5.4 lists —— the only record the user ever gets of what his session lost, and one that lands in no file later. The test still holds —— block only when the forced turn delivers something the user does not otherwise get.
- 6.5. On PostToolUse the structured `hookSpecificOutput.additionalContext` field is the one channel that is BOTH non-blocking AND model-visible —— use it for any advisory that must actually be read.
- 6.6. On UserPromptSubmit, NEVER emit `decision:"block"` —— it ERASES the user's prompt.
- 6.7. PostToolUse cannot undo the write regardless of exit code (the tool already ran); exit 2 there buys model visibility with error framing, not a rollback.
- 6.8. Output mechanics:
  - 6.8.1. At exit 0, emit `{"hookSpecificOutput": {"hookEventName": "<Event>", "additionalContext": "<text>"}}` on stdout.
  - 6.8.2. At exit 2 the harness ignores stdout and JSON entirely —— write to STDERR or the message is lost.
- 6.9. PostCompact has NO model channel at all —— the costliest lesson in this file:
  - 6.9.1. Its dispatch returns a user-display string only; no `additionalContext`, no yield
  - 6.9.2. Contrast `Setup` ("JSON additionalContext shown to Claude") and `PostToolBatch`
  - 6.9.3. So a compaction protocol CANNOT be delivered by this hook. It never once was
  - 6.9.4. It ran dead 70 days: project-level (silent no-op) 29/05–25/07, then channel-blind
  - 6.9.5. Nothing observable changed at the 25/07 fix, so the second defect looked like success
  - 6.9.6. The protocol lives in root `CLAUDE.md` §5, which the harness re-injects itself
  - 6.9.7. Pinned by `sandbox/post_compact_regression_test.py`, which asserts the channel
  - 6.9.8. That test FAILS if the event ever gains a model channel —— an alarm to act on
  - 6.9.9. §5 was still skipped in full on 202608070423 —— the summary's own "resume directly, do not acknowledge" sits in the prompt, beating prose from turns earlier. ENFORCEMENT therefore moved to a Stop hook (`mlint.py` SHAPE C, §6.4.3): the only event that can force the owed output back into the same turn. PostCompact remains a user-facing banner and nothing more

---

## 7. Verifying a Hook Is Alive

*The anti-self-deception protocol. The most valuable section in this file.*

- 7.1. Two claims, never conflate them:
  - 7.1.1. "The script works when I pipe it a payload" —— tests the SCRIPT.
  - 7.1.2. "The harness actually invokes it" —— tests the WIRING.
  - 7.1.3. §2 happened because 7.1.1 was passed repeatedly and 7.1.2 was never tested once.
- 7.2. The one-step live probe (PostToolUse chain):
  - 7.2.1. Edit `cp/ccsim/sandbox/hook_probe_response_.md` with the Edit or Write tool.
  - 7.2.2. It deliberately contains RED flags (6 Americanisms on one line).
  - 7.2.3. BLOCKED with a dlint RED report → hooks are ALIVE.
  - 7.2.4. Write succeeds SILENTLY → hooks are DEAD. There is no third outcome.
  - 7.2.5. The `response_` in the probe's filename is still load-bearing, for a NARROWER reason than before. `dlint_hook.sh` now spawns Python on any `.md`, so the name no longer decides whether the lint RUNS —— it decides whether the WHOLE FILE is judged. Off the comms names a verdict is scoped to the text the write produced, so an Edit whose new text is clean would pass and the probe would prove nothing. Keep the name.
- 7.3. Per-event liveness test:

| Event | Live Test | Alive Looks Like |
|---|---|---|
| PostToolUse | Edit the probe file (§7.2) | Edit blocked, RED report returned |
| PostToolUse | End a turn, then check `cscpt/.dlint.log` | A new line per `.md` write that turn |
| PreToolUse | Run `date +%Y%m%d%H%M` through the Bash tool (no TZ prefix) | A `[tlint] Clock read without a timezone` note; a `clock_warn` line in `cscpt/.tlint.log` |
| PreToolUse | Run `echo ALINT_PROBE` through the Bash tool | An `alint` ALIVE note comes back; a new `action=probe` line in `cscpt/.alint.log` |
| PreToolUse | Write `cp/ccsim/sandbox/flintprobe_ 202608011299.md` | The write is BLOCKED, stderr naming `flintprobe_202608011299.md` |
| PostToolUse | Bash-`touch` a `probe_close_ 202608011299.md` in `sandbox/`, then Write `probe_202608011298.md` beside it | A `[flint] Stray-space filename(s)` note comes back as context |
| Stop | End a turn, then check `cscpt/.clint.log` | A new line appended for that turn |
| UserPromptSubmit | Submit a prompt containing a real `#trigger` | Reminder line appears in context |
| UserPromptSubmit | End a turn, then check `cscpt/.hlint.log` | A new line per prompt: `fired` with trigger names, or `silent` |
| Stop | End an `#m2` turn on the interim declaration alone | The stop is BLOCKED, stderr naming the unrun sprint; a `block` line in `cscpt/.mlint.log` |
| Stop | End an `#m2` turn having written a `response_` and declared nothing | The stop is BLOCKED, stderr naming the missing `➡️`; a `block_nodeclare` line in `cscpt/.mlint.log` |
| Stop | End a compaction-opened turn without root §5's `🚨` sentinel (cannot be staged on demand —— wait for a real compaction, or read the `compact=` field on any `.mlint.log` line) | The stop is BLOCKED, stderr naming the sentinel, the halt, and the §5.3/§5.4 lists; a `block_nosentinel` line in `cscpt/.mlint.log` |
| PostCompact | Occurs naturally on compaction | A new line in `cscpt/.post_compact.log` (the banner reaches the USER, never the model —— §6.9) |

- 7.4. The manual pipe test —— useful, but know exactly what it proves:

```bash
cd "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
printf '%s' '{"tool_name":"Write","cwd":"/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe","tool_input":{"file_path":"cp/ccsim/sandbox/hook_probe_response_.md"}}' | bash cscpt/dlint_hook.sh; echo "exit=$?"
```

- 7.5. Exit 2 plus a RED report means the SCRIPT CHAIN works. It says NOTHING about whether the harness ever calls it.
- 7.6. Also verify every registered command still RESOLVES —— a hook pointing at a renamed or moved file exits 127 and the harness carries on in silence. This audits all of them at once and prints `DEAD` for any whose target is missing:

```bash
python3 -c "
import json,os,shlex
d=json.load(open(os.path.expanduser('~/.claude/settings.json'))).get('hooks',{})
for ev,groups in d.items():
    for g in groups:
        for h in (g.get('hooks') or [g]):
            c=h.get('command','')
            paths=[t for t in shlex.split(c) if '/' in t]
            bad=[p for p in paths if not os.path.exists(p)]
            print(('DEAD ' if bad else 'ok   '), ev, '->', c if bad else os.path.basename(paths[-1] if paths else c))
"
```


- 7.7. Per-invocation LOGGING is what makes "never fired" distinguishable from "fired and found nothing":
  - 7.7.1. A log written only on a breach cannot tell those two apart —— an empty log is consistent with BOTH, which is exactly how the dead wiring survived so long.
  - 7.7.2. clint therefore logs EVERY invocation to `cscpt/.clint.log` (git-ignored), tagged by the stage reached: `no_stdin`, `out_of_scope`, `no_transcript`, `unreadable_transcript`, `empty_transcript`, `clean` (+ `clean:dot`/`clean:dot_reader`), `message_failed`, one `exempt:` per exemption, and one `yellow:` per breach class (`prose`, `io_shape`, `sha_shape`, `sentinel`, `warn_*`, `sic_overrun`, `reader`). The retired always-RED tags (`block`, `block_failed`, `yellow:spent`, `yellow:active`) no longer exist —— §6.4.
  - 7.7.3. A non-growing clint log across real turns is now UNAMBIGUOUS: the harness is not calling that command.
  - 7.7.4. clint, alint, dlint_quick, hlint, tlint, post_compact and pre_compact each keep a stage log. flint now has §7.3 probe rows on BOTH its events but still no stage log; DADC, plint and nlint keep NEITHER a log nor a probe row —— so for those five there is currently no liveness evidence at all, which is a real gap, not an omission from this sentence. A stage log is the cheap fix; a probe row is the cheaper one.
- 7.8. After ANY change to a hook script, its filename, its path, or the settings file:
  - 7.8.1. Run the resolvability audit (§7.6) —— the cheapest guard against §8.6.2, and the check whose absence lets a renamed lint sit dead and unnoticed.
  - 7.8.2. Re-run the live probe (§7.2). A passing unit test is not a substitute.
  - 7.8.3. Do both in the SAME turn as the change —— a wiring break has no diff and no error message, so it will not resurface on its own.
- 7.9. ⚠️ A REGISTRATION CHANGE TAKES MINUTES TO GO LIVE, so an early probe LIES. Measured: a newly-added entry did not fire when tested twice within a few minutes, then fired unaided ~15 minutes later, in the SAME session, whilst every other hook ran normally throughout.
  - 7.9.1. The app therefore DOES re-read `~/.claude/settings.json` without a restart —— it is simply not prompt about it. Nothing here needs an app restart to take effect; it needs patience.
  - 7.9.2. Consequence for §8's failure signature: "the new hook did not fire" is NOT evidence of dead wiring until the delay has passed. Retest before concluding, or a correct registration gets "fixed" into a broken one.
  - 7.9.3. Consequence for a REMOVAL: the stale registration keeps running for those same minutes, which is why §8.6.2's delete-order rule exists.

---

## 8. Failure Signature

*Recognise this fast; it is what §2 looked like from the inside for weeks.*

- 8.1. Every lint silently passing, forever.
- 8.2. No log lines being appended (`cscpt/.clint.log` frozen at an old timestamp, or absent).
- 8.3. Deliberately non-compliant files being written with no complaint —— chat prose never blocked, Americanisms in a `response_` never flagged, a numbering reset never queried.
- 8.4. Every script still passing when piped a payload by hand.
- 8.5. The combination of 8.1–8.4 is diagnostic: the scripts are fine and the WIRING is dead. Go straight to `~/.claude/settings.json`.
- 8.6. Near-miss variants that produce the same silence:
  - 8.6.1. Hooks registered project-level (§1) —— the original defect.
  - 8.6.2. A registered path that no longer exists after a rename or move. NOT always silent, and the difference matters: at PostToolUse the command fails and the harness carries on, but at PreToolUse the harness reports a hook error and BLOCKS the tool call. Observed live —— deleting a still-registered script made every Bash call fail until the file was put back. So delete the FILE only after the live settings stop naming it, never the other way round.
  - 8.6.3. An absolute path stale after the repo was relocated.
  - 8.6.4. A wrongly-shaped registration entry (§3.4).
  - 8.6.5. A scope guard that fails CLOSED on an unreadable payload —— never write one.
- 8.7. Renaming a hook script is a WIRING change, not a refactor: `~/.claude/settings.json` is outside the repo, so `git mv` cannot update it and no diff will ever show the breakage. Re-point the live settings and re-probe in the same turn.

---

## 9. Recovery

- 9.1. `~/.claude/settings.json` is OUTSIDE the repo —— a `git clone` on a new machine restores every script and ZERO registrations.
- 9.2. Restore-of-record: `.claude/hooks_user_settings.reference.json` (inert; nothing loads it; it lives in `.claude/` rather than `cscpt/` because `cscpt/` holds runnable scripts only).
- 9.3. Restore steps:
  - 9.3.1. Open `.claude/hooks_user_settings.reference.json` and `~/.claude/settings.json` side by side.
  - 9.3.2. Merge the reference's `hooks` object into the user file —— MERGE, never overwrite; the user file also holds unrelated preferences.
  - 9.3.3. Rewrite every absolute path to the repo's location on the new machine.
  - 9.3.4. Confirm each command resolves (§7.6) —— no exit 127.
  - 9.3.5. Run the live probe (§7.2); a blocked edit is the acceptance criterion.
  - 9.3.6. Run `cp/ccsim/sandbox/repo_scope_guard_regression_test.py` to confirm the scope guards still behave (in-scope, out-of-scope, and fail-open branches).
  - 9.3.7. Run `cp/ccsim/sandbox/alint_regression_test.py` —— it pins the TEA1 gate, which is the only hook here that can block a COMMIT, so a silent break there is felt as either a lost turn-end discipline or an unexplainably stuck repo.
  - 9.3.5.1. This checklist covers the BLOCKING hooks only —— a silent break in one of those is felt as a stuck repo or an escaped deliverable. The advisory lints have suites too (`cp/ccsim/sandbox/`), worth running but not recovery-critical.
  - 9.3.8. Run `cp/ccsim/sandbox/dlint_gate_regression_test.py` —— it pins the only lint that blocks on content, and the deliverable gate folded into it.
  - 9.3.9. Run `cp/ccsim/sandbox/flint_filename_gate_regression_test.py` —— it pins the filename gate, and its live-repo sweep fails if the detection rule ever broadens.
  - 9.3.11. Run `cp/ccsim/sandbox/mlint_m2_sprint_gate_regression_test.py` —— it pins the only Stop hook that can BLOCK, replaying the real stall from a transcript fixture; its last check reads the LIVE settings file, so an unregistered hook fails the suite rather than sitting silent.
  - 9.3.12. Run `cp/ccsim/sandbox/tlint_time_integrity_regression_test.py` —— its last two checks read the LIVE settings file, so an unregistered tlint fails the suite rather than sitting silent.
  - 9.3.10. Run `cp/ccsim/sandbox/pairing_lint_regression_test.py` —— it pins both arms of the query/response pairing enforcement (root `CLAUDE.md` §3.5.3).
- 9.4. Keep the reference file in step with the live file whenever a hook is added, renamed, or re-pointed —— a stale reference is a recovery that silently restores dead wiring.
- 9.5. The reference file is documentation, so it may legitimately run AHEAD of the live file during a change; whichever is ahead, close the gap before the turn ends.

---

## 10. Backup Mirror Discipline

*§9 restores the hook REGISTRATIONS from a reference file inside the repo. This section covers the wider problem: `~/.claude` is a symlink to `/Volumes/FURY 2TB/.claude`, so if that drive is lost, every hand-made configuration on it goes with it. `backup/backup_Claude/backup_Claude_FURY/` is the repo's copy of the handful of files that no clone, no cloud account, and no internal disk can reproduce. A backup nobody updates is worse than none, so the rule below is a MANDATE, not a suggestion.*

- 10.1. THE MANDATE: run this at EVERY CCSIM SESSION START. It diffs every mirrored pair and overwrites any backup that no longer matches its live file:

```bash
"/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/backup/backup_Claude/backup_Claude_FURY/mirror.sh" sync
```

- 10.2. THE SPECIFIC MISTAKE THIS PREVENTS: editing `~/.claude/settings.json` —— adding a hook, re-pointing a path, changing a matcher —— and not mirroring it. The edit works, every test passes, nothing complains, and the only copy of the new registration is sitting on an untracked drive. Run `mirror.sh sync` in the SAME turn as any `settings.json` edit; do not wait for the next session start.
  - 10.2.1. The same applies to any other live change (a new auto-memory entry, a Routine reworded), but `settings.json` is the one that costs the whole hook system.
- 10.3. To INSPECT without writing anything, drop the argument —— same report, no changes. Useful during a hook audit alongside §7.6:

```bash
"/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/backup/backup_Claude/backup_Claude_FURY/mirror.sh"
```

- 10.4. Read it by exit code: `0` all identical; `1` drift (check mode only —— `sync` repairs and returns `0`); `2` a human decision is needed, and the line says which —— `UNMIRRORED` (live file nothing backs up), `ORPHAN` (backup whose source is unknown), `MISSING` (mapped source deleted upstream), `ABSENT` (mirror never made). `ABSENT` and `UNMIRRORED` are the gaps this check exists to surface, so they are reported loudly rather than assumed benign.
- 10.5. `mirror.sh` DISCOVERS the live memory folders instead of trusting a fixed list, so a brand-new auto-memory file —— or a whole new project's `memory/` —— is flagged `UNMIRRORED` the first time the check runs after it appears. It never invents a backup name for one; that needs a naming decision, so it stops and says so.
- 10.6. Overwriting the backup is intended and safe —— that folder is tracked by git, so prior contents stay recoverable from history. The live file is the truth; the copy is the follower.
- 10.7. ACCEPTED RISK, recorded honestly: the check is session-START, so a live file changed MID-session is unprotected until the next session begins. Per-turn mirroring was considered and REJECTED —— it taxes every turn of every session to close a window of minutes, for files that change a few times a month. §10.2's same-turn habit for `settings.json` is what narrows the gap that matters; the session-start run is the safety net behind it.
- 10.8. The obvious upgrade —— a `SessionStart` hook running `mirror.sh sync` automatically —— is deliberately NOT in place: it would itself require a `settings.json` edit, which must then be mirrored, and an unattended writer touching the backup folder is a bigger change than the problem warrants. Revisit only if the session-start run is observed being skipped.
- 10.9. After editing `mirror.sh`, run `mirror_test.sh` beside it —— temp fixtures only, never touching the real `.claude`; exit 0 means the checker still catches drift.

---

## 11. Backup Mirror —— Scope & Restore

- 11.1. Currently mirrored (the folder's own README carries the full table, the selection test, and the exclusions):
  - 11.1.1. `settings.json` —— the ONLY live hook registration; outside git by necessity (§1.6).
  - 11.1.2. `projects/*/memory/*.md` for both projects —— persistent auto-memory; written locally, never cloud-synced.
  - 11.1.3. `scheduled-tasks/ajap-auto-resume/SKILL.md` —— hand-written Routine logic that exists nowhere else.
- 11.2. `settings.json` is covered TWICE, deliberately, and the two are not interchangeable:
  - 11.2.1. `.claude/hooks_user_settings.reference.json` (§9.2) is a HOOKS-ONLY excerpt, shaped for merging into an existing user file.
  - 11.2.2. `backup_settings.json.md` is the WHOLE file, including the unrelated preferences a merge would not carry.
  - 11.2.3. A hook change must update BOTH in the same turn; updating one alone leaves a restore that is half-right, which reads as success.
- 11.3. Adding anything new to the backup folder: apply its README's selection test —— IRREPLACEABLE and UNTRACKED and SMALL, all three —— then add it to the `MAP` block in `mirror.sh` AND that README. Bulk transcripts, caches, `session-env/`, and server-pushed files fail the test and stay out. Credentials are barred outright regardless of the test, because that folder is pushed to GitHub.
- 11.4. THE NET EFFECT, stated plainly: if FURY is lost, restore the repo from GitHub FIRST (the backups live inside it), then copy these files into the new `~/.claude/`. `mirror.sh restore-plan` prints the exact `mkdir -p` + `cp` commands and writes nothing, so it reverses the naming rule for you rather than leaving it to be fumbled by hand. Without this folder, a clean GitHub restore brings back every lint SCRIPT and registers NONE of them, and the auto-memory is simply gone —— §5's failure signature, from a standing start.
- 11.5. If FURY is merely UNMOUNTED rather than lost, nothing here applies —— do NOT restore anything on top of an intact drive. Run `nscpt/fury_unmounted.sh`, which diagnoses the link, repairs it by renaming any stray aside (never deleting), and verifies every registered hook path still resolves.

---

## 12. Runtime Budget —— Worst-Case Latency

*Hooks sit between the user's action and the response, so their cost is felt directly. This § exists so the roster cannot grow into a perceptible delay one harmless-looking addition at a time.*

- 12.1. THE MANDATE: before registering ANY new hook, estimate the worst-case latency it adds to its EVENT, not to itself. Count every hook already on that event (§3, grouped by event) —— they all fire on the same trigger, so a hook is never billed alone.
- 12.2. WORST CASE means the payload that defeats every fast path: a RELEVANT file or command that makes each `*_hook.sh` shim spawn its Python and each lint do real work. The cheap path is the common case; it is never the budget.
- 12.3. Hooks on the SAME event run in PARALLEL, so an event costs the MAX of its hooks, not the SUM. Measured, not assumed —— two independent methods:
  - 12.3.1. WIRING: sampling `ps -axo pid=,ppid=,args=` at `~`12 ms whilst a real Edit fired the chain caught ALL the PostToolUse hooks alive in ONE frame —— consecutive PIDs, one child Python already spawned under each, all parented to the same harness process. The PreToolUse hooks on a write, and the Stop hooks, behaved identically.
  - 12.3.2. WALL-CLOCK: the same set driven concurrently by hand measured `~`75 ms, against a SUM of `~`226 ms and a MAX of `~`71 ms. The observation tracks the MAX.
  - 12.3.3. Parallelism is HARNESS-OWNED and can change without notice, exactly as §5.8 says of payload shapes. Re-establish it after a harness update rather than trusting this line —— a switch to sequential multiplies every figure below.
- 12.4. ALERT THE USER whenever an event's estimated worst case exceeds **1 SECOND**. Above that the delay is perceptible, and a hook the user can feel is a hook they will ask to remove. Name the event, the figure, and which hook dominates it.
- 12.5. The design rule parallelism implies: a new hook is effectively FREE unless it is SLOWER than the worst hook already on its event. The ceiling is therefore per-hook —— keep every single hook well under 1 s and no event can breach it. A tenth cheap lint costs nothing; one slow lint costs everything.
- 12.5.1. flint is the worked example: added to PreToolUse at `~`44 ms, it raised that event's worst case by ZERO, because DADC capture (`~`47 ms) already sat above it. A hook cheaper than the incumbent worst is genuinely free.
- 12.6. Baseline, re-measured 202608020004 (median of 9 runs, worst-case payloads):

| Event | Dominant Hook | Event Worst Case |
|---|---|---|
| PreToolUse (Edit/Write) | DADC capture `~`47 ms | `~`47 ms |
| PreToolUse (Read) | plint `~`43 ms | `~`43 ms |
| PreToolUse (Bash) | alint `~`41 ms —— `~`150 ms on the largest transcript on disk (53 MB) | `~`150 ms |
| PostToolUse | dlint `~`130 ms on the repo's largest `.md` (322 KB) | `~`130 ms |
| UserPromptSubmit | hlint `~`26 ms | `~`26 ms |
| Stop | clint `~`41 ms —— `~`184 ms on the largest transcript on disk (51 MB) | `~`184 ms |
| PostCompact | `~`31 ms | `~`31 ms |

- 12.7. ⚠️ SUPERSEDED by §0.1 (re-measured 202608071235: Stop dominant at 184 ms, round trip `~`0.39 s). The narrative below is the dlint-dominant era and is kept only for the per-hook scaling laws, which still hold. The worst event then spent `~`35% of the budget, up from `~`7% —— dlint alone accounts for the rise. TWO hooks are no longer FIXED costs and must be re-estimated against their INPUT, not against this table: dlint is `~`0.3 ms per KB of `.md` text judged atop a `~`30 ms floor (so `~`3 MB in a single write would breach 1 s; the repo's largest `.md` is 322 KB) —— it was `~`1 ms/KB until the Americanism lookup became a tokenise-and-intersect instead of one regex per listed word per line, and alint/clint scale with transcript size (`~`41 ms at 2.7 MB, `~`150/165 ms at 53 MB —— clint parses every line unbounded, alint pre-filters and caps at 64 MB). The floor is process spawn —— `~`26 ms for any Python hook, `~`5 ms for a shim that exits inside bash. That floor is why the shims exist (§3.2), and why a lint's own logic is almost never what costs. `mlint` joins Stop at `~`78 ms on that same 51 MB transcript —— it tail-reads a bounded 8 MB window instead of parsing unbounded, so it costs a FLAT amount where clint scales, and adds ZERO to the event (§12.5).
- 12.8. To re-measure: pipe a worst-case payload (§5's shapes) into each command on the event, time it, and take the MAX. That times the SCRIPTS (§7.1.1); confirming the harness still runs them in parallel needs the `ps` sample of §12.3.1 (§7.1.2). Neither substitutes for the other.
- 12.9. File mtimes are useless for this on FURY —— it is HFS+, so `st_mtime` has 1-SECOND resolution and every sub-second interval reads as zero. Time the processes, never the files they touch.

---

## 13. PreCompact —— the Only Hook That Reaches the Model

*Appended as a new § so nothing above renumbers. Reached from §3's roster row and §6's channel table.*

- 13.1. Registry, verbatim: exit 0 = "stdout appended as custom compact instructions".
- 13.2. Exit 2 = BLOCK compaction. NEVER exit 2 —— on `auto` that strands the session at the ceiling.
- 13.3. Extracted from the binary, not from docs: exit-0 stdout of every non-blocked PreCompact hook is trimmed, multi-hook outputs joined by blank lines, returned as `newCustomInstructions`.
- 13.4. Merged AFTER any user `/compact` text, then appended to the summariser prompt under the literal heading `Additional Instructions:`. It never REPLACES the summary spec.
- 13.5. Fires on BOTH triggers, incl. the background precompute path —— where the hook runs at PRECOMPUTE time and its result is reused at swap, so a log time can precede the visible compaction.
- 13.6. ⚠️ ADVISORY TWICE OVER, never a guarantee:
  - 13.6.1. It instructs the SUMMARISER, which may comply, paraphrase, or drop the ask.
  - 13.6.2. The fresh context ALWAYS ends with the hardcoded harness tail "Resume directly ... as if the break never happened" —— `suppressFollowUpQuestions`, hardcoded true on the reactive path.
  - 13.6.3. So the conflict with root `CLAUDE.md` §5 is STRUCTURAL and permanent, not incidental.
- 13.7. Root §5 therefore stays PRIMARY. This is the in-band second cue, and §5 must never be rewritten to lean on it.
- 13.8. Script rules for `.claude/pre_compact.sh`:
  - 13.8.1. stdout must never START with `{` —— it would parse as hook JSON, and a schema failure discards the instructions entirely.
  - 13.8.2. Target the ask INSIDE `<summary>`; `<analysis>` is stripped before the summary reaches the fresh context.
  - 13.8.3. No harness truncation on this path (the 10k cap belongs to the REPL pipeline); default hook timeout 600 s.
- 13.9. Pinned by `sandbox/pre_compact_regression_test.py`, which re-verifies the channel against the installed binary on every run and alarms if PostCompact ever gains a direct model channel —— which would supersede this two-hop design.
