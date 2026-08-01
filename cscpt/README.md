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

## Scripts

**You run these:**

- `set_dates.py` —— macOS Finder-date setter: stamps Created / Modified / Added / Last Opened on a file or a whole tree to a given Sydney timestamp.
- `dlint.py` —— deterministic prose linter: auto-fixes quotes, then flags 🔴 RED / 🟡 YELLOW breaches of `universal/writing.md`. Full mode for deliverables, quick mode for comms. Every FULL run leaves a content-addressed receipt that `elint.py` reads as proof the file was linted.
- `usage_pct.py` —— prints live Claude usage: current 5-hourly session % and weekly %. Drives the "Claude Web" app by keystroke, so leave the Mac alone whilst it runs.
- `padv.py` —— `#replace #adv` helper: extracts a verbatim span from a `.pages.md` mirror and splits it into the break-free blocks a Pages find-and-replace can actually match.
- `otg_sync.py` —— `#sync` runner: re-pins every file URL in an OTG index to its last-commit SHA, then commits + pushes only that index and its prefs file.

**The harness runs these (the lints):**

- `alint.py` —— PreToolUse. BLOCKS a `git commit`/`git push` whilst any sub-agent dispatched by this session is still running, so root `CLAUDE.md` §3.1.6's "no SAs in-flight" precondition is mechanical rather than a judgement call. Wait for the agent, or `TaskStop` it. Exempts sub-agents' own commits; warns instead of blocking whenever it cannot read the evidence. Logged to `.alint.log`.
- `clint.py` —— Stop hook. Warns when chat text is not a permitted declaration line. WARN-only: never blocks, and the warning reaches the user, not CC. Logged to `.clint.log`.
- `dlint_quick.py` —— PostToolUse. On a CC-authored comms write, runs the quick lint and BLOCKS until 🔴 RED = 0.
- `elint.py` —— PostToolUse + Stop. Enforces root `CLAUDE.md` §3.7.3 where no other lint reaches: a deliverable-shaped file must pass FULL `dlint.py` before it goes out. Advises at the deliverable's own write, BLOCKS a comms write whilst a lint is still owed, and warns the user at Stop. Wrongly flagged? Put `<!-- dlint: internal -->` in that file, once —— never rewrite an internal file to satisfy it. Logged to `.elint.log`.
- `nlint.py` —— PostToolUse. Two advisory checks against `universal/numbered.md`, neither blocking: a numbered level reaching its 10th item, and a response file resetting its top-level numbering with no excuse in evidence.
- `tlint.py` —— PostToolUse. Warns when a written file's 12-digit timestamp clashes with a neighbour that is not its sanctioned pair. Warn-only.
- `hlint.py` —— UserPromptSubmit. Spots `#trigger` tokens in the prompt (and in any `.md` it names) and reminds CC to read each matching trigger file. Never blocks.
- `plint.py` —— PreToolUse. Before a script, pcmd or letter-like file is written, reminds CC to read the governing protocol first. Advisory; never gates the write.
- `DADC.py` —— PreToolUse + PostToolUse. Preserves a file's macOS Date Added and Date Created across an agent's edit, everywhere (no folder scope). New files untouched; always exits 0.
- `*_hook.sh` —— thin bash fast-path shims, one per lint that needs one. Each IS the registered hook, exiting instantly on irrelevant payloads before any Python spawns.

**You read this one:**

- `dark_mode.html` —— **READ, don't run.** Copy-paste light/dark toggle button (CSS + JS) plus its design rationale, for building a toggle into any new `.html`. A default template —— adapt it.
