#!/usr/bin/env python3
"""Regression test —— `cp/ccsim/skill_guide.md` rename + its standing content.

WHY THIS EXISTS (self-contained; no conversation or comms file explains it):

`cp/ccsim/skiller.md` was renamed to `cp/ccsim/skill_guide.md`. "Skiller" was a
cute name that told a newcomer nothing; `skill_guide.md` says what the file is
and matches its sibling `hook_guide.md`, which guides hook creation exactly as
this file guides skill-description creation.

A pcmd rename is only half-done when the file moves. These guides are reached by
NAME —— from other pcmds, from script docstrings, from skill bodies. One
surviving old name is a SILENT failure: the reference names a file that no
longer exists, the read is skipped, and the session proceeds without the context
it was meant to load. Nothing errors; the output is merely wrong. So the
invariant is checked mechanically rather than trusted to a careful grep.

WHAT THIS PINS

  1. The rename landed: the new path exists and the old one is gone. Leaving
     both would give two sources of truth and guarantee drift.
  2. No LIVE file still says "skiller". `sessions/` (and other historical
     records) are exempt —— they were accurate when written, and rewriting them
     would falsify history.
  3. The `*_guide.md` naming convention documented in the guide's own preamble
     is still stated there, and every guide it names actually exists. A
     convention nobody restates is a convention that decays; a convention naming
     a missing file is worse than none.
  4. The context-budget figures quoted in the guide still match the VERIFIED
     values below. If someone edits those numbers, this test fails until they
     also update the table here —— which forces re-verification instead of a
     plausible-looking guess being frozen into a permanent document.

PROVENANCE OF THE VERIFIED FIGURES (point 4)

Read directly out of the shipped Claude Code binary, v2.1.201 (build
2026-07-03), at `/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code`.
Two settings govern the skill listing, each carrying its own help string:

  skillListingMaxDescChars  default 1536
    "Per-skill description character cap in the skill listing sent to Claude
     (default: 1536). Descriptions longer than this are truncated."

  skillListingBudgetFraction  default 0.01
    "Fraction of the context window (in characters) reserved for the skill
     listing sent to Claude (default: 0.01 = 1%). When the listing exceeds
     this, descriptions are shortened to fit."

The budget is computed as `contextWindowTokens * bytesPerToken * fraction`,
with the shipped constants `200000 * 4 * 0.01` = 8,000 characters, i.e. roughly
2,000 tokens at the 4-chars-per-token factor the code itself applies. That is
why the guide's "~1% of the context window (~2,000 tokens on a 200k window)"
is accurate rather than a round-number guess.

RUN:
    cd "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
    python3 cp/ccsim/sandbox/skill_guide_rename_regression_test.py

Exit 0 = all good; exit 1 = at least one failure (details on stdout).
Dependency-free by design (PyYAML is not installed system-wide on this Mac).
"""

import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SELF = os.path.abspath(__file__)

OLD = "cp/ccsim/skiller.md"
NEW = "cp/ccsim/skill_guide.md"

# Guides the convention note names. Each must exist, or the note lies.
GUIDES = [
    "cp/ccsim/skill_guide.md",
    "cp/ccsim/hook_guide.md",
    "cp/ccsim/ssd_migration_guide.md",
]

# Verified against the shipped binary —— see PROVENANCE in the module docstring.
VERIFIED_MAX_DESC_CHARS = "1,536"
VERIFIED_BUDGET_FRACTION = "0.01"

# Historical records: accurate when written, so never rewritten.
SKIP_DIRS = {".git", "sessions", "backup", "parked", "__pycache__", "node_modules"}

# Only text formats that can carry a live reference.
SCAN_EXT = {".md", ".py", ".sh", ".json", ".txt", ".zsh"}

DEAD = re.compile(r"skiller", re.I)

failures = []


def scan_files():
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            path = os.path.join(root, fn)
            if path == SELF:
                continue                      # this file quotes the dead name
            if os.path.splitext(fn)[1].lower() in SCAN_EXT:
                yield path


def read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return fh.read()


def test_rename_landed():
    if not os.path.exists(os.path.join(REPO, NEW)):
        failures.append("missing after rename: %s" % NEW)
    if os.path.exists(os.path.join(REPO, OLD)):
        failures.append("old path still present: %s" % OLD)


def test_no_live_dead_references():
    for path in scan_files():
        try:
            lines = open(path, encoding="utf-8").readlines()
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(lines, 1):
            if DEAD.search(line):
                failures.append(
                    "%s:%d stale reference —— %s"
                    % (os.path.relpath(path, REPO), n, line.strip()[:110]))


def test_heading_renamed():
    """The H1 is what a reader sees first; a stale one contradicts the filename."""
    if not os.path.exists(os.path.join(REPO, NEW)):
        return
    head = read(NEW).splitlines()[0]
    if not head.startswith("# Skill Guide"):
        failures.append("%s: H1 not updated —— %r" % (NEW, head[:80]))


def test_naming_convention_documented_and_true():
    if not os.path.exists(os.path.join(REPO, NEW)):
        return
    raw = read(NEW)
    if "*_guide.md" not in raw:
        failures.append(
            "%s: the `*_guide.md` naming convention is no longer stated" % NEW)
    for g in GUIDES:
        name = os.path.basename(g)
        if name not in raw:
            failures.append("%s: convention no longer names %s" % (NEW, name))
        if not os.path.exists(os.path.join(REPO, g)):
            failures.append("convention names a missing file: %s" % g)
        if not name.endswith("_guide.md"):
            failures.append("convention breached by its own example: %s" % g)


def test_budget_figures_match_verified_values():
    if not os.path.exists(os.path.join(REPO, NEW)):
        return
    raw = read(NEW)
    for setting, value in (
        ("skillListingMaxDescChars", VERIFIED_MAX_DESC_CHARS),
        ("skillListingBudgetFraction", VERIFIED_BUDGET_FRACTION),
    ):
        if setting not in raw:
            failures.append("%s: no longer names `%s`" % (NEW, setting))
            continue
        if value not in raw:
            failures.append(
                "%s: `%s` default %s not found —— if the shipped default "
                "changed, re-verify against the binary and update both the "
                "guide and this test's VERIFIED_* table"
                % (NEW, setting, value))


def selftest():
    """Prove the matcher is not vacuous."""
    bad = []
    if not DEAD.search("House style: `cp/ccsim/skiller.md`."):
        bad.append("selftest: matcher failed to flag the dead name")
    if DEAD.search("House style: `cp/ccsim/skill_guide.md`."):
        bad.append("selftest: false positive on the new name")
    return bad


def main():
    failures.extend(selftest())
    test_rename_landed()
    test_no_live_dead_references()
    test_heading_renamed()
    test_naming_convention_documented_and_true()
    test_budget_figures_match_verified_values()

    if failures:
        print("FAIL —— %d problem(s):" % len(failures))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("PASS —— rename landed, no stale references, convention stated and "
          "true, budget figures match verified values.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
