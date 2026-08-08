#!/usr/bin/env python3
"""Indiscriminate-Staging Gate Regression Test (alint PreToolUse arm)

WHY THIS EXISTS (self-contained; no conversation or comms file explains it):

`git add -A` at turn end has done real, irreversible damage twice:

  * 07/08/2026 —— it staged 88 voided files (13,190 lines, 74% of that commit)
    and pushed them to a PUBLIC repo. A voided `❌_` file is the USER's to
    delete under root CLAUDE.md §8.2; it is never CC's to commit.
  * 08/08/2026 —— it swept the user's half-finished edit to
    `universal/glossary.md` into a CCSIM commit whilst he was still typing it.
    Root CLAUDE.md §3.1.6.1.4 says commit ONLY the files CC touched this turn;
    §3.1.6.1.5 says that when his edits land on a file CC touched, CC must not
    commit at all and must raise a `⚠️` blocker instead.

After the first incident the remedy was prose ("stage explicit paths"). It
failed inside 24 hours. So this is a gate: `cscpt/alint.py` already parses every
Bash command as a registered PreToolUse hook, and now refuses the shape.

TWO THINGS THIS SUITE PINS, because each has already gone wrong once:

(1) THE SHAPE IS CAUGHT —— `-A`, `--all`, `add .`, `commit -a`/`-am`, through
    `&&` chains, behind a `cd`, and via `git -C`.

(2) A MENTION IS NOT A COMMAND. The first draft matched the string ANYWHERE in
    the command and blocked its own unit test within a minute of going live ——
    the test's fixtures contained the literal text. The gate now anchors at
    COMMAND POSITION (start of command, or after `;` `&&` `||` `|` or a
    newline). A gate that cries wolf is a gate that gets switched off, so the
    negative cases below matter as much as the positive ones.

The fixtures are the real commands from both incidents plus the shapes a future
turn is most likely to reach for. Deliberately NOT pinned: whether the tree
actually contains foreign edits at the time —— the gate judges the STAGING SHAPE
alone, so it cannot be defeated by the tree happening to look clean.
"""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ALINT = os.environ.get("ALINT_UNDER_TEST", os.path.join(REPO, "cscpt", "alint.py"))

failures = []
passed = 0


def _load():
    spec = importlib.util.spec_from_file_location("alint_ut", ALINT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(label, condition, detail=""):
    global passed
    if condition:
        passed += 1
    else:
        failures.append("%s%s" % (label, (" —— " + detail) if detail else ""))


# The two real incidents, verbatim in shape, plus the near neighbours.
BLOCKED = [
    ("git add -A", "the 07/08 litter commit"),
    ("git add --all", "long form"),
    ("git add .", "cwd-scoped, same damage from the repo root"),
    ("git add -Av", "bundled flags"),
    ("git commit -a -m 'x'", "stages every tracked modification"),
    ("git commit -am 'x'", "the short spelling of the same"),
    ("git commit --all -m 'x'", "long form"),
    ("git add -A && git commit -q -m 'x'", "the 08/08 shape that took his edit"),
    ("cd /repo && git add -A", "behind a cd"),
    ("git -C /elsewhere add -A", "another worktree is not an excuse"),
    ("git status --porcelain; git add -A", "after a separator"),
]

# Every one of these must stay silent. The last four are the misfire class.
ALLOWED = [
    ("git add cscpt/alint.py cp/ccsim/backlog.md", "explicit paths —— the point"),
    ("git add sessions/2026/202608/ccsim_response_1.md", "one explicit path"),
    ("git status --porcelain", "not a staging command"),
    ("git push -q origin main", "not a staging command"),
    ("git add -p", "interactive, hunk by hunk"),
    ("git commit -q -m 'never run git add -A again'", "a MESSAGE, not a command"),
    ('git commit -m "the git add . habit"', "ditto, double-quoted"),
    ("python3 -c \"x = 'git add -A'\"", "a mention inside a script argument"),
    ("echo 'git add --all' > notes.txt", "a mention being written to a file"),
]


def test_shapes():
    m = _load()
    for cmd, why in BLOCKED:
        check("NOT blocked: %s" % cmd, m._indiscriminate_stage(cmd) is not None, why)
    for cmd, why in ALLOWED:
        got = m._indiscriminate_stage(cmd)
        check("wrongly blocked: %s" % cmd, got is None, "%s (matched %r)" % (why, got))


def test_reported_fragment_is_useful():
    """The block message quotes what it matched, so the fix is obvious."""
    m = _load()
    frag = m._indiscriminate_stage("cd /repo && git add -A && git commit -m 'x'")
    check("no fragment reported", bool(frag))
    check("fragment does not name the offending command", frag and "git add" in frag,
          repr(frag))


def test_quote_stripper_is_fail_safe():
    """Over-stripping costs a MISSED block; under-stripping costs a WRONG one.

    A wrong block is the worse failure —— it stops legitimate work and teaches
    the operator to distrust the gate —— so the stripper is allowed to be
    greedy. This pins the direction, not the exact behaviour.
    """
    m = _load()
    check("stripper removed a real command outside quotes",
          m._indiscriminate_stage("git add -A") is not None)


def main():
    test_shapes()
    test_reported_fragment_is_useful()
    test_quote_stripper_is_fail_safe()
    if failures:
        print("FAIL —— %d problem(s):" % len(failures))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("PASS —— %d passed. Indiscriminate staging is blocked in command "
          "position (-A, --all, `add .`, `commit -a`, through chains, `cd` and "
          "`-C`), whilst explicit paths and mere mentions stay silent." % passed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
