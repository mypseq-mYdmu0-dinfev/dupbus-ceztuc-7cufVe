# `cscpt/` —— CC scripts (RUN, don't READ)

Everything here is CC-only and built to be **RUN from the shell, never read into context** —— each file is thousands of tokens, and every one carries a top comment split into `NON-CCSIM` (all you need to RUN it) and `CCSIM` (only needed to EDIT it), so a caller never has to open the code.

The one exception is `dark_mode.html` —— a READ template, not a run script; see its entry.

(`gscpt/` is the user's own scripts —— different folder, different owner.)

## Read Order (mandatory)

You are a client whose context is precious. The goal is to succeed having read as LITTLE as possible, so escalate one rung at a time and stop the moment you can act:

1. **This index.** Find the entry, decide it is the tool you want, RUN it —— and read nothing further. That is the intended outcome for most calls.
2. **That script's `NON-CCSIM` block ONLY.** Usage, flags, exit codes, preconditions and caveats all live there. Stop when the `CCSIM` marker appears; everything below it is for editors, not callers. This rung must suffice for essentially every real use.
3. **The whole file —— never silently.** If rung 2 still leaves you unable to proceed: alert the user, request approval to read the script in full, AND append an entry to `cp/ccsim/backlog.md` naming what you could not answer. Reaching this rung means this index or that `NON-CCSIM` block FAILED, and the failure is only ever fixed if it is recorded —— the escalation IS the feedback loop that keeps both honest. Reading on quietly wastes your context now and every later reader's context forever.

## Editing Anything Here (ownership)

`cscpt/` belongs to CCSIM by default —— it owns this toolchain and its change-simulation QA.

- **Large edit** —— CONSIDER drafting `sessions/queued_queries/ccsim_query_[current_TS].md` and leaving the work to CCSIM; only where doing so does not block the task in hand.
- **Small edit, an edit the user asked for, or one where you already hold context CCSIM would have to rebuild from scratch** —— edit directly, then append an entry to `cp/ccsim/backlog.md` (format: `cp/ccsim/CLAUDE.md` §3) stating what changed and why, inviting a CCSIM review.
- **Even a one-character fix gets reported.** Undocumented drift in shared tooling is exactly how a whole toolchain rots silently: each unlogged tweak is invisible on its own, and by the time the behaviour surprises someone, nobody can say which change caused it.

## Hooks

Several linters below are launched by the harness rather than by you. Registration, payload shapes, which channel reaches the model, self-scoping, verification and recovery live in `cp/ccsim/hook_guide.md` —— read it only when working ON the hooks; running anything here needs none of it.

## Scripts

**You run these:**

- `set_dates.py` —— macOS Finder-date setter: stamps Created / Modified / Added / Last Opened on a file or a whole tree to a given Sydney timestamp.
- `dlint.py` —— deterministic prose linter: auto-fixes quotes, then flags 🔴 RED / 🟡 YELLOW breaches of `universal/writing.md`. Full mode for deliverables, quick mode for comms.
- `usage_pct.py` —— prints live Claude usage: current 5-hourly session % and weekly %. Drives the "Claude Web" app by keystroke, so leave the Mac alone whilst it runs.
- `padv.py` —— `#replace #adv` helper: extracts a verbatim span from a `.pages.md` mirror and splits it into the break-free blocks a Pages find-and-replace can actually match.

**The harness runs these (the lints):**

- `clint.py` —— Stop hook. Flags chat text that is not a permitted declaration line, blocking once per prompt so CC self-corrects. Breaches logged to `.clint.log`.
- `dlint_quick.py` —— PostToolUse. On a CC-authored comms write, runs the quick lint and BLOCKS until 🔴 RED = 0. The only lint here that can block a write.
- `nlint.py` —— PostToolUse. Advises (never blocks) when a response file resets its top-level numbering with no `universal/numbered.md` excuse in evidence.
- `tlint.py` —— PostToolUse. Warns when a written file's 12-digit timestamp clashes with a neighbour that is not its sanctioned pair. Warn-only.
- `hlint.py` —— UserPromptSubmit. Spots `#trigger` tokens in the prompt (and in any `.md` it names) and reminds CC to read each matching trigger file. Never blocks.
- `plint.py` —— PreToolUse. Before a script, pcmd or letter-like file is written, reminds CC to read the governing protocol first. Advisory; never gates the write.
- `*_hook.sh` —— thin bash fast-path shims, one per lint that needs one. Each IS the registered hook, exiting instantly on irrelevant payloads before any Python spawns.

**You read this one:**

- `dark_mode.html` —— **READ, don't run.** Copy-paste light/dark toggle button (CSS + JS) plus its design rationale, for building a toggle into any new `.html`. A default template —— adapt it.
