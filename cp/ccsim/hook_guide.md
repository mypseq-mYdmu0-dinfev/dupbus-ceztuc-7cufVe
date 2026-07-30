# Hook Guide

*The definitive, self-contained reference for CC hooks in this repo. Read this BEFORE creating, editing, registering, debugging, or trusting any hook. Everything needed is here —— no conversation, comms file, or session memory is required or cited. Lives in `ccsim/` because CCSIM owns the hook system; `cscpt/README.md` describes each individual lint, this file describes the MACHINERY they run on.*

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
| PostToolUse | `cscpt/DADC.py hook-restore` | Restore Date Added + Date Created after a write |
| PostToolUse | `cscpt/dlint_hook.sh` | Comms/deliverable prose lint (blocking on RED) |
| PostToolUse | `cscpt/nlint_hook.sh` | Numbering-continuity lint (advisory) |
| PostToolUse | `cscpt/tlint_hook.sh` | Timestamp-clash lint (warn-only) |
| UserPromptSubmit | `cscpt/hlint.py` | `#trigger` read-reminder (advisory) |
| Stop | `cscpt/clint.py` | No-chat-prose lint (WARN-only; never blocks) |
| PostCompact | `.claude/post_compact.sh` | Inject the post-compaction protocol |

- 3.1. Naming convention: a `*_hook.sh` IS the file the harness launches; the `.py` beside it is the lint body. Every `.sh` in `cscpt/` carries `_hook`, no `.py` does.
- 3.2. Only the three PostToolUse lints have a `.sh` gate —— they fire on EVERY Edit/Write, so the shim spares a needless Python spawn.
- 3.3. `clint.py` (Stop) and `hlint.py` (UserPromptSubmit) fire once per turn/prompt, so they are registered directly and correctly have no `.sh`.
- 3.4. Registration entry shape matters: an event's array holds `{"matcher": …, "hooks": [{"type":"command","command":…}]}` objects. A bare `{"type":"command", …}` placed directly in the event array is the wrong shape —— check it against the live file before trusting any hand-written entry.
- 3.5. Matchers are TOOL-NAME only —— there is no path filter, which is precisely why each PostToolUse lint must do its own file-path check.

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
| clint | Repo-scoped | Blocks a Stop; enforces this repo's bespoke no-chat-prose rule |
| dlint | Repo-scoped | Blocks on RED; enforces this repo's prose/style guide |
| nlint | Repo-scoped | Enforces this repo's numbering-continuity convention |
| hlint | GLOBAL | Advisory-only; a missed `#trigger` has already cost real work elsewhere |
| tlint | GLOBAL | Warn-only, always exit 0; a missed TS clash is silent and expensive |

- 4.7. The asymmetry is intentional, not an oversight —— the test rule is: a lint that can BLOCK must be repo-scoped, a lint that can only advise may be global.
  - 4.7.1. Never "tidy" a scope guard onto hlint or tlint.
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
| Stop | User only | Not a supported channel | Reaches the MODEL and BLOCKS the stop |

- 6.1. On Stop, ONLY a non-zero exit's stderr reaches the model. An exit-0 `systemMessage` or stdout reaches the user alone.
- 6.2. Consequence: a non-blocking Stop warning can NEVER make the agent self-correct —— its turn has already ended and it never sees the note.
- 6.3. Cost of a Stop block: exactly ONE extra model turn —— a full round trip, billed and consuming context. Spend it deliberately, at most once per prompt.
- 6.4. clint is WARN-ONLY —— every verdict exits 0 and nothing blocks. It once blocked (first RED per prompt, later ones logged), but forcing an extra turn each time cascaded into worse turn-end behaviour than the breaches themselves, so the owner demoted it.
- 6.4.1. ⚠️ The price, so nobody restores the block unaware: exit-0 output reaches ONLY the user, never the model. clint therefore cannot correct CC at all —— it is an audit trail, and enforcement rests on root `CLAUDE.md` §3.1.6's TEAs.
- 6.4.2. Breach classes survive in the log with a `yellow:` prefix (`yellow:prose`, `yellow:reader`, …); a lone `.` is CLEAN in both modes (`clean:dot` / `clean:dot_reader`).
- 6.5. On PostToolUse the structured `hookSpecificOutput.additionalContext` field is the one channel that is BOTH non-blocking AND model-visible —— use it for any advisory that must actually be read.
- 6.6. On UserPromptSubmit, NEVER emit `decision:"block"` —— it ERASES the user's prompt.
- 6.7. PostToolUse cannot undo the write regardless of exit code (the tool already ran); exit 2 there buys model visibility with error framing, not a rollback.
- 6.8. Output mechanics:
  - 6.8.1. At exit 0, emit `{"hookSpecificOutput": {"hookEventName": "<Event>", "additionalContext": "<text>"}}` on stdout.
  - 6.8.2. At exit 2 the harness ignores stdout and JSON entirely —— write to STDERR or the message is lost.

---

## 7. Verifying a Hook Is Alive

*The anti-self-deception protocol. The most valuable section in this file.*

- 7.1. Two claims, never conflate them:
  - 7.1.1. "The script works when I pipe it a payload" —— tests the SCRIPT.
  - 7.1.2. "The harness actually invokes it" —— tests the WIRING.
  - 7.1.3. §2 happened because 7.1.1 was passed repeatedly and 7.1.2 was never tested once.
- 7.2. The one-step live probe (PostToolUse chain):
  - 7.2.1. Edit `cp/ccsim/sandbox/hook_probe_response_.md` with the Edit or Write tool.
  - 7.2.2. It deliberately contains RED flags (5 Americanisms on one line).
  - 7.2.3. BLOCKED with a dlint RED report → hooks are ALIVE.
  - 7.2.4. Write succeeds SILENTLY → hooks are DEAD. There is no third outcome.
  - 7.2.5. The `response_` in the probe's filename is load-bearing —— `dlint_hook.sh` only spawns Python when the payload mentions `response_`/`close_`/`wrap_`, so a probe without it would prove nothing.
- 7.3. Per-event liveness test:

| Event | Live Test | Alive Looks Like |
|---|---|---|
| PostToolUse | Edit the probe file (§7.2) | Edit blocked, RED report returned |
| Stop | End a turn, then check `cscpt/.clint.log` | A new line appended for that turn |
| UserPromptSubmit | Submit a prompt containing a real `#trigger` | Reminder line appears in context |
| PostCompact | Occurs naturally on compaction | The `🚨` banner is injected |

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
  - 7.7.2. clint therefore logs EVERY invocation to `cscpt/.clint.log` (git-ignored), tagged by the stage reached: `no_stdin`, `out_of_scope`, `no_transcript`, `unreadable_transcript`, `empty_transcript`, `clean`, `block`, `block_failed`, `yellow:spent`, `yellow:active`.
  - 7.7.3. A non-growing clint log across real turns is now UNAMBIGUOUS: the harness is not calling that command.
  - 7.7.4. The other four lints keep no log —— for them, the live probe (§7.2/§7.3) is the only liveness evidence. Adding a stage log to any of them is a cheap, worthwhile upgrade.
- 7.8. After ANY change to a hook script, its filename, its path, or the settings file:
  - 7.8.1. Run the resolvability audit (§7.6) —— the cheapest guard against §8.6.2, and the check whose absence lets a renamed lint sit dead and unnoticed.
  - 7.8.2. Re-run the live probe (§7.2). A passing unit test is not a substitute.
  - 7.8.3. Do both in the SAME turn as the change —— a wiring break has no diff and no error message, so it will not resurface on its own.

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
  - 8.6.2. A registered path that no longer exists after a rename or move —— the command exits 127 and the harness carries on silently.
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
