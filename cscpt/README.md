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

## Scripts —— ≤30 Words Each Description

**You run these:**

- `set_dates.py` —— macOS Finder-date setter: stamps Created / Modified / Added / Last Opened on a file or a whole tree to a given Sydney timestamp.
- `dlint.py` —— deterministic prose linter: auto-fixes quotes, flags 🔴 RED / 🟡 YELLOW breaches of `universal/writing.md`. FULL for deliverables, quick elsewhere; every FULL run leaves a receipt.
- `pending.py` —— prints the two queues only the USER can clear: voided `❌_` files (flagged ≥7 days) and queued queries awaiting a dedicated session. Read-only.
- `usage_pct.py` —— prints live Claude usage: current 5-hourly session % and weekly %. Drives the "Claude Web" app by keystroke, so leave the Mac alone whilst it runs.
- `padv.py` —— `#replace #adv` helper: extracts a verbatim span from a `.pages.md` mirror and splits it into the break-free blocks a Pages find-and-replace can actually match.
- `otg_sync.py` —— `#sync` runner: re-pins every file URL in an OTG index to its last-commit SHA, then commits + pushes only that index and its prefs file.

**The harness runs these (the lints):**

- `alint.py` —— PreToolUse. BLOCKS a `git commit`/`git push` whilst any sub-agent OR workflow this session dispatched is still running. Wait for it, or `TaskStop` the id it prints.
- `clint.py` —— Stop hook. Warns when chat text is not a permitted declaration line. WARN-only: never blocks, and the warning reaches the user, not CC. Logged to `.clint.log`.
- `dlint_quick.py` —— PostToolUse. The only lint that blocks on CONTENT. Quick-lints EVERY `.md`, and blocks a comms write whilst a deliverable still owes a FULL `dlint.py` run.
- `flint.py` —— PreToolUse. BLOCKS a filename that wedges a space before its 12-digit timestamp. The refusal names the name you meant; a corrective `git mv` is never gated.
- `nlint.py` —— PostToolUse. Two advisory checks against `universal/numbered.md`, neither blocking: a numbered level reaching its 10th item, and a response file resetting its top-level numbering with no excuse in evidence.
- `tlint.py` —— PostToolUse. Warns on a timestamp clash with a non-paired neighbour, and on any stray-space filename already in that folder. Warn-only; never go hunting for more.
- `hlint.py` —— UserPromptSubmit. Reminds CC to read each `#trigger` file the prompt names, and to create the `response_[TS]` any named `query_[TS]` still owes. Never blocks.
- `plint.py` —— PreToolUse. Before a script, pcmd or letter-like file is written, reminds CC to read the governing protocol first. Advisory; never gates the write.
- `DADC.py` —— PreToolUse + PostToolUse. Preserves a file's macOS Date Added and Date Created across an agent's edit, everywhere (no folder scope). New files untouched; always exits 0.
- `*_hook.sh` —— thin bash fast-path shims, one per lint that needs one. Each IS the registered hook, exiting instantly on irrelevant payloads before any Python spawns.

**You read this one:**

- `dark_mode.html` —— **READ, don't run.** Copy-paste light/dark toggle button (CSS + JS) plus its design rationale, for building a toggle into any new `.html`. A default template —— adapt it.
