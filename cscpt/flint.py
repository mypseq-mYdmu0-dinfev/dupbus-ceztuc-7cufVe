#!/usr/bin/env python3
"""PreToolUse hook —— "filename linter". Guards root CLAUDE.md §3.3's comms
filename convention `[prefix]_[12-digit TS].md` against the one defect that has
actually recurred: whitespace wedged between the prefix underscore and the TS
(`close_ 202606142239.md`).

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: a PreToolUse gate on comms filenames (root CLAUDE.md §3.3 ——
  `[prefix]_[TS].md`, never a space before the 12 digits).
* IT BLOCKS a Write/Edit whose target basename carries that space; re-issue the
  call with the space-free name it hands you. Renaming an existing offender is
  `git mv`, never gated.
* IT ADVISES, never blocks, when a path you merely READ already offends ——
  raise a `⚠️` to the user.
* CHANNELS: the block reaches the model as an error; the advisory as context.
* Any error or non-match -> exit 0, silent.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WIRING (kept here, not in NON-CCSIM: nobody invokes this by hand, so the
plumbing serves only an editor). Run by the harness via `flint_hook.sh`, the
registered bash fast-path; registered PreToolUse
(Edit|Write|MultiEdit|NotebookEdit|Read) in the USER-level
`~/.claude/settings.json` —— the Claude Desktop app executes user-level hooks
and silently ignores project-level ones. Place it LAST in the PreToolUse array,
because it is the only entry on the write path that can exit 2, and were
the harness ever to short-circuit a chain on a non-zero exit, an earlier
position would skip the hooks behind it.
non-zero exit, an earlier position would skip `DADC.py hook-capture`'s
filesystem side effect and `alint_hook.sh`'s TEA1 gate.

WHY PreToolUse, NOT PostToolUse (the whole point of a separate hook): a
PostToolUse hook cannot undo a write —— the tool has already run, so exit 2
there buys model visibility with error framing, never a rollback
(`cp/ccsim/hook_guide.md` §6.7). The defective file would exist, and the defect
class being fixed here is precisely "the file got created and nobody noticed".
Only a PreToolUse exit 2 stops the creation.

WHY A SEPARATE FILE, not a mode inside `tlint.py` (which already parses comms
filenames and their timestamps, and would otherwise be the natural home):
`hook_guide.md` §4.7 —— a lint that can BLOCK must be repo-scoped, a lint that
can only advise may be global. `tlint.py` is deliberately GLOBAL and warn-only,
and says so emphatically in its own docstring. Teaching it to block would force
either a scope guard it explicitly forbids, or a per-mode scope split that
contradicts its stated invariant at a glance. Two files, one reach each, both
internally consistent. `tlint.py` still carries the ADVISORY half of this
defect —— it already lists the written file's folder for its TS-clash check, so
sweeping that same listing for stray-space siblings costs no extra I/O.

DETECTION RULE, stated exactly: the basename must match
`^\\S*_\\s+(?=20\\d{10}(?!\\d))` —— from the START of the name, a whitespace-FREE
run ending in `_`, then one or more whitespace characters, then a 12-digit TS
beginning `20` and not sitting inside a longer digit run.

WHY THAT SHAPE AND NOT "a TS-bearing name containing any whitespace", which was
the obvious first draft: calibrated against every basename in this repo (5331
carry a bounded 12-digit TS; 7 of those also contain whitespace). The broad rule
flags 5 LEGITIMATE files —— `MGTK746 Dev Plan _ 202603170315.txt` and three
siblings in `cp/archive/mip/`, plus `gscpt/parked/AJAP Logs 202607182259.csv`
—— whose naming style uses spaces THROUGHOUT and is nobody's mistake. The `^\\S*`
anchor is what separates them: a name that is space-free right up to the
underscore and then suddenly is not, is the defect; a name spaced all the way
through is a different convention. On that rule the repo scores 2 hits, both of
them the genuine article (`sessions/2026/202606/close_ 202606142239.md`,
`sessions/2026/202607/dissertation_close_ 202607151919.md`), and all 4 instances
recorded in `cp/ccsim/backlog.md` match. Zero false positives, zero misses.

FALSE-POSITIVE PROFILE, honestly: a file deliberately named `<no-spaces>_ <TS>`
would be blocked. No such convention exists here, and the block message names
the exact replacement, so the cost of the theoretical case is one re-issued tool
call. Note also what is NOT flagged and why it must not be —— `_moved_[dir]`
suffixes (root §8.1.2) and `❌_` prefixes (§8.2) are legitimate and carry no
whitespace, so a positive-form "must match the canonical shape exactly" check
was rejected: it would have broken both.

KNOWN GAPS, so nobody mistakes this for total cover:
* A space INSIDE the digits (`close_2026061422 39.md`) leaves no bounded 12-digit
  TS at all, so neither this nor `tlint.py` can see it.
* Only the harness's file tools are gated. A file created by Bash (`cp`, `touch`,
  a script) or by the user in Finder never reaches a PreToolUse hook —— that is
  exactly the hole `.githooks/pre-commit` closes, blocking a staged ADD of an
  offending path on the way into history.

FAIL-OPEN, per `hook_guide.md` §4.4: an unscopeable payload runs the lint anyway
(a silently disabled lint is the failure that guide exists to prevent). Out of
repo scope the gate DOWNGRADES to the advisory rather than going quiet, so the
§4.7 asymmetry holds without buying it with blindness.

The `isinstance(data, dict)` check is not decorative: valid JSON that is not an
object would make `.get` raise and exit 1, breaking this file's own fail-safe
promise —— which matters all the more because a user-level registration means
any project's payload can arrive here.
"""

import json
import os
import re
import sys

# Repo anchor for the scope guard. Derived from this file's own location, never
# hard-coded, so the repo stays relocatable (hook_guide.md §4.5.1).
_REPO_ROOT_REAL = os.path.realpath(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
# Transcripts live at ~/.claude/projects/<slug>/<uuid>.jsonl, where <slug> is
# the project directory with every `/` and ` ` replaced by `-` (§4.3.2).
_REPO_SLUG = _REPO_ROOT_REAL.replace("/", "-").replace(" ", "-")

# THE DEFECT. See DETECTION RULE in the docstring for the full calibration.
_DEFECT_RE = re.compile(r"^\S*_\s+(?=20\d{10}(?!\d))")

# Tools that CREATE or REWRITE a file at the given path —— the only ones whose
# call is worth blocking. Everything else (Read chief among them) can at most be
# told about a defect that already exists.
_WRITE_TOOLS = frozenset({"Write", "Edit", "MultiEdit", "NotebookEdit"})


def _in_scope(data):
    """True if this invocation's project is THIS repo (or a sub-path of it), or
    if scope genuinely cannot be determined (FAIL-OPEN, hook_guide.md §4.4).
    Never raises: any unexpected error must default to "run the lint"."""
    try:
        if not isinstance(data, dict):
            return True
        cwd = data.get("cwd")
        if isinstance(cwd, str) and cwd:
            real_cwd = os.path.realpath(cwd)
            return (real_cwd == _REPO_ROOT_REAL
                    or real_cwd.startswith(_REPO_ROOT_REAL + os.sep))
        tp = data.get("transcript_path")
        if isinstance(tp, str) and tp:
            m = re.search(r"/projects/([^/]+)/", tp)
            if m:
                slug = m.group(1)
                return (slug == _REPO_SLUG
                        or slug.startswith(_REPO_SLUG + "-"))
            # transcript_path present but not the recognised
            # .../projects/<slug>/... shape -> unparseable -> fall through.
        return True  # neither field usable -> FAIL-OPEN
    except Exception:
        return True  # never let a scope-check error silence the lint


def _target_path(data):
    """The path this tool call is about. `file_path` covers Write/Edit/MultiEdit
    /Read; `notebook_path` is NotebookEdit's own spelling of the same thing."""
    ti = data.get("tool_input")
    if not isinstance(ti, dict):
        return ""
    for key in ("file_path", "notebook_path"):
        v = ti.get(key)
        if isinstance(v, str) and v:
            return v
    return ""


def _clean_name(base):
    """The name the caller should have used: the offending whitespace run
    removed, nothing else touched. The match always ends `_` + whitespace, so
    `rstrip` can never strip it away to nothing."""
    return _DEFECT_RE.sub(lambda m: m.group(0).rstrip(), base, count=1)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(data, dict):
        return 0

    fp = _target_path(data)
    if not fp:
        return 0
    base = os.path.basename(fp)
    if not _DEFECT_RE.search(base):
        return 0

    tool = data.get("tool_name")
    tool = tool if isinstance(tool, str) else ""
    fixed = _clean_name(base)

    if tool in _WRITE_TOOLS and _in_scope(data):
        # PreToolUse + exit 2 == the tool call is BLOCKED and the message
        # reaches the model. At exit 2 the harness ignores stdout and JSON
        # entirely, so this MUST go to stderr (hook_guide.md §6.8.2).
        sys.stderr.write(
            "flint: BLOCKED —— `" + base + "` has whitespace between the prefix "
            "and its 12-digit timestamp. Root CLAUDE.md §3.3 names comms files "
            "`[prefix]_[TS].md`, with no space. Re-issue this call as `" + fixed
            + "`. (Renaming a file that already carries the defect is `git mv`, "
            "which this gate never touches.)\n"
        )
        return 2

    # Not a write, or not this repo -> advise, never block. Exit 0 with
    # `additionalContext` is the one PreToolUse channel that is BOTH
    # non-blocking and model-visible (hook_guide.md §6, PreToolUse row).
    json.dump({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                "[flint] Stray-space filename encountered: `" + fp + "`. Root "
                "CLAUDE.md §3.3 names comms files `[prefix]_[TS].md`, with no "
                "space before the 12 digits; this one should be `" + fixed
                + "`. ALERT THE USER (a `⚠️` declaration) —— do not go hunting "
                "for others. Rename only on his say-so, with `git mv` in a "
                "move-only commit (universal/coding.md § Git Discipline)."
            ),
        }
    }, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
