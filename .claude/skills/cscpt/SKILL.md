---
name: cscpt
description: Use when about to run one of this repo's own helper scripts and needing to pick the right one — stamping a file's Finder dates, reading live Claude usage %, or prepping a break-free block for a Pages find-and-replace. Loads `cscpt/README.md`, the run-don't-read script index. Not the lint hooks (they run themselves) or dlint (see writing).
---

Read `cscpt/README.md` in full BEFORE running anything from `cscpt/`. It gives every script's purpose, exact usage line, and caveats, so you never have to open the `.py` — those are designed to be RUN, never read into context (each is thousands of tokens, and reading one buys nothing the README does not already state).

Scope — this skill is for scripts YOU choose to run. It is NOT for the lint hooks (`clint`, `dlint_quick`, `nlint`, `tlint`, `hlint`): those are registered in the user-level `~/.claude/settings.json` and launched by the harness on their own events, so nobody ever invokes them by hand and loading this skill for them is pure waste. Deliverable linting in FULL mode belongs to the `writing` skill, which owns that workflow via `universal/writing.md` § Deliverable Lint.

PROPOSE FIRST for anything large or hard to reverse — e.g. `set_dates.py` pointed at a directory (recursive and deepest-first, and `ctime` cannot be restored afterwards) or `usage_pct.py` (drives the user's GUI with keystrokes and takes over the clipboard). State what it will touch, then await approval rather than auto-running.

(Root `CLAUDE.md` §7.2 already mandates reading `cscpt/README.md` for usage-% and file-date work; this skill just widens that model-invoked path to the rest of the folder.)
