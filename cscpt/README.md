# `cscpt/` —— CC scripts (RUN, don't READ)

Everything here is CC-only and built to be **RUN from the shell, never read into context** —— each file is thousands of tokens, and every one carries a top comment split into `NON-CCSIM` (all you need to RUN it: capped at 100 words, fenced by an explicit start/end marker pair) and `CCSIM` (only needed to EDIT it), so a caller never has to open the code.

The one exception is `dark_mode.html` —— a READ template, not a run script; see its entry.

(`gscpt/` is the user's own scripts —— different folder, different owner.)

## Read Order (mandatory)

You are a client whose context is precious. The goal is to succeed having read as LITTLE as possible, so escalate one rung at a time and stop the moment you can act:

1. **This index.** Find the entry, decide it is the tool you want, RUN it —— and read nothing further. That is the intended outcome for most calls.
2. **That script's `NON-CCSIM` block ONLY —— extract it, do NOT open the file.** The block is fenced by a matched pair of markers, so one command hands you that span and nothing else (run from the repo root, substituting the script's filename):

   ```
   sed -n '/NON-CCSIM.*start/,/NON-CCSIM.*end/p' cscpt/clint.py
   ```

   Works identically for `.py` and `.sh` —— shell scripts carry the same markers, comment-prefixed. The pattern is deliberately ASCII-only: it never has to match the `——` inside the marker text, so no locale or encoding difference can make it silently miss and dump the whole file, which is the exact accident this rung exists to prevent. Each block is capped at 100 words and answers what the tool does, what its limits are, and what to do about its output. This rung must suffice for essentially every real use.
3. **The whole file —— never silently.** If rung 2 still leaves you unable to proceed: alert the user, request approval to read the script in full, AND append an entry to `cp/ccsim/backlog.md` naming what you could not answer. Reaching this rung means this index or that `NON-CCSIM` block FAILED, and the failure is only ever fixed if it is recorded —— the escalation IS the feedback loop that keeps both honest. Reading on quietly wastes your context now and every later reader's context forever.

## Editing Anything Here (ownership)

`cscpt/` belongs to CCSIM by default —— it owns this toolchain and its change-simulation QA.

- **Large edit** —— CONSIDER drafting `sessions/queued_queries/ccsim_query_[current_TS].md` and leaving the work to CCSIM; only where doing so does not block the task in hand.
- **Small edit, an edit the user asked for, or one where you already hold context CCSIM would have to rebuild from scratch** —— edit directly, then append an entry to `cp/ccsim/backlog.md` (format: `cp/ccsim/CLAUDE.md` §3) stating what changed and why, inviting a CCSIM review.
- **Even a one-character fix gets reported.** Undocumented drift in shared tooling is exactly how a whole toolchain rots silently: each unlogged tweak is invisible on its own, and by the time the behaviour surprises someone, nobody can say which change caused it.
- **Two header invariants to preserve.** Every script keeps exactly ONE `NON-CCSIM` start marker and ONE end marker, and the span between them stays ≤100 words. A missing end marker sends the extractor in rung 2 reading to end-of-file —— wasting precisely the context the split exists to save —— and a bloated block quietly costs every future caller. Anything that no longer earns its place up there MOVES down into `CCSIM`; nothing is deleted, because a caller's needless detail is still an editor's load-bearing fact. Both invariants are machine-checked —— run `python3 cp/ccsim/sandbox/cscpt_header_contract_regression_test.py` from the repo root after touching any header here; it also executes the rung-2 command above against every script, so a recipe that stops working fails the test rather than a caller.

## Hooks

Several linters below are launched by the harness rather than by you. Registration, payload shapes, which channel reaches the model, self-scoping, verification and recovery live in `cp/ccsim/hook_guide.md` —— read it only when working ON the hooks; running anything here needs none of it.

**A hook body is not a CLI, and will now say so.** It reads its JSON payload on stdin and ignores its arguments, so `python3 cscpt/nlint.py some_file.md` checks nothing. It used to sit there blocking instead of saying that, and because a hang prints exactly as much as a pass does —— nothing —— a file once got recorded as lint-clean on the strength of a command that never ran a lint and never finished. Every hook body except `mlint.py` now refuses within two seconds, on stderr, non-zero, printing the payload-piping recipe that does work; to lint prose by hand you want `python3 cscpt/dlint.py --quick <file>`, which is a real CLI. Two things trigger the refusal, and it takes both: an argument that NAMES A FILE (no hook event ever passes one), and stdin that is not the pipe a harness gives —— a terminal, `/dev/null`, a closed descriptor, a plain file. Testing only whether stdin was READY was not enough and shipped the defect twice: `/dev/null` is ready and empty, an agent shell hands every command it runs exactly that, and the hook then exited 0 in silence, which is the same false pass as the hang by a shorter route. An EMPTY PIPE is deliberately left alone —— that is the harness sending nothing, and every lint here fails open on it. All eleven bodies refuse —— `mlint.py` was the last one retrofitted, and `blint.py` arrived with the guard built in. Machine-checked by `python3 cp/ccsim/sandbox/hook_stdin_guard_regression_test.py`, which also executes each printed recipe, so a recipe that stops working fails the test rather than a caller.

## Scripts —— ≤30 Words Each Description

**You run these:**

- `set_dates.py` —— macOS Finder-date setter: stamps Created / Modified / Added / Last Opened on a file or a whole tree to a given Sydney timestamp.
- `dlint.py` —— deterministic prose linter: auto-fixes quotes, flags 🔴 RED / 🟡 YELLOW breaches of `universal/writing.md`. FULL for deliverables, quick elsewhere; quick adds one house-only advisory (bare `read` vs `#r`).
- `ccsim_housekeeping.py` —— CCSIM session-start sweep of the three queues only the USER can clear: voided `❌_` files (flagged ≥7 days), queued queries, and stray-space filenames. Read-only.
- `usage_pct.py` —— prints live Claude usage: current 5-hourly session % and weekly %. Drives the "Claude Web" app by keystroke, so leave the Mac alone whilst it runs.
- `padv.py` —— `#replace #adv` helper: extracts a verbatim span from a `.pages.md` mirror and splits it into the break-free blocks a Pages find-and-replace can actually match.
- `otg_sync.py` —— `#sync` runner: re-pins every file URL in an OTG index to its last-commit SHA, then commits + pushes only that index and its prefs file.

**The harness runs these (the lints):**

- `alint.py` —— PreToolUse. BLOCKS a `git commit`/`git push` whilst any sub-agent OR workflow this session dispatched is still running. Wait for it, or `TaskStop` the id it prints.
- `blint.py` —— PostToolBatch + 3 more stages. Mid-turn corrector: injects a §3.2 chat-discipline correction the model sees BEFORE its next request; also denies a duplicate `mark_chapter` per turn.
- `clint.py` —— Stop hook. Warns when chat text is not a permitted declaration line. WARN-only: never blocks, and the warning reaches the user, not CC. Logged to `.clint.log`.
- `mlint.py` —— Stop hook. BLOCKS one turn-end when an `#m2` turn stops at its interim declaration with no `#sprint`, or writes a `response_` and never declares it, or a compaction-opened turn never emits root §5's `🚨` sentinel.
- `dlint_quick.py` —— PostToolUse. The only lint that blocks on CONTENT. Quick-lints EVERY `.md`, and blocks a comms write whilst a deliverable still owes a FULL `dlint.py` run.
- `flint.py` —— PreToolUse + PostToolUse. Owns comms filenames: BLOCKS a name wedging a space before its 12-digit timestamp, and warns on a timestamp clash or a stray-space name already in that folder.
- `tlint.py` —— PreToolUse + PostToolUse. Advisory only: flags a clock read missing `TZ='Australia/Sydney'`, a new comms timestamp 6 h+ from real Sydney time, and US-format dates in text.
- `nlint.py` —— PostToolUse. Two advisory checks against `universal/numbered.md`, neither blocking: a numbered level reaching its 10th item, and a response file resetting its top-level numbering with no excuse in evidence.
- `hlint.py` —— UserPromptSubmit. Reminds CC to read each `#trigger` file the prompt names. Logged to `.hlint.log`; in-repo, also tallies the previous turn's `clint` chat-discipline breaches into the next prompt.
- `plint.py` —— PreToolUse. Before a script, pcmd or letter-like file is written, reminds CC to read the governing protocol first. Advisory; never gates the write.
- `DADC.py` —— PreToolUse + PostToolUse. Preserves a file's macOS Date Added and Date Created across an agent's edit, everywhere (no folder scope). New files untouched; always exits 0.
- `*_hook.sh` —— thin bash fast-path shims, one per lint that needs one. Each IS the registered hook, exiting instantly on irrelevant payloads before any Python spawns.

**You read this one:**

- `dark_mode.html` —— **READ, don't run.** Copy-paste light/dark toggle button (CSS + JS) plus its design rationale, for building a toggle into any new `.html`. A default template —— adapt it.
