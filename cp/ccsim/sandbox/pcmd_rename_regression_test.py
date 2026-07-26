#!/usr/bin/env python3
"""Regression test —— the personal_bg / career_bg rename must stay resolved.

WHY THIS EXISTS (self-contained; no conversation or comms file explains it):

Two context pcmds were renamed away from the generic word "profile", which did
not distinguish them:

    universal/profile.md        -> universal/personal_bg.md
    cp/career/pro_profile.md    -> cp/career/career_bg.md
    .claude/skills/profile/     -> .claude/skills/personal-bg/
    .claude/skills/pro-profile/ -> .claude/skills/career-bg/

A pcmd rename is only half-done when the file moves: the files are reached by
NAME from root CLAUDE.md's conditional-read table, from the CP indices, and
from the skill bodies. A single surviving old name is a silent failure —— the
governing table names a file that no longer exists, the read is skipped, and
the session proceeds without the context it was supposed to load. Nothing
errors; the answer is just wrong. So the invariant is checked mechanically
rather than trusted to a careful grep.

THE UNDERSCORE / HYPHEN ASYMMETRY IS DELIBERATE, NOT AN OVERSIGHT:
the pcmd FILENAMES use underscores (personal_bg.md, career_bg.md) whilst the
SKILL names use hyphens (personal-bg, career-bg). Claude Code skill frontmatter
permits only lowercase letters, numbers, and hyphens in `name` —— an underscore
is invalid and the skill would not register. Anyone later "tidying" the two
into a matching style must change the FILENAMES to hyphens, never the skill
names to underscores; test_skill_names_are_hyphenated below enforces that
direction so the tidy-up cannot silently break skill registration.

WHAT IS DELIBERATELY EXEMPT:
- `sessions/`, `backup/`, `gscpt/parked/` —— historical records that were
  accurate at the time they were written; rewriting them would falsify history.
- Pinned `raw.githubusercontent.com` permalinks carrying a 40-hex commit SHA.
  Those URLs address an immutable commit in which the OLD path was still the
  live one, so they still resolve and still return the right bytes. They must
  keep the old path until they are re-pinned to a newer commit —— at which
  point the new path becomes mandatory. Only the human-facing ENTRY NAME above
  each URL was renamed.

RUN:
    cd "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
    python3 cp/ccsim/sandbox/pcmd_rename_regression_test.py

Dependency-free by design (PyYAML is not installed system-wide on this Mac).
"""

import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SELF = os.path.abspath(__file__)

RENAMES = [
    ("universal/profile.md", "universal/personal_bg.md"),
    ("cp/career/pro_profile.md", "cp/career/career_bg.md"),
    (".claude/skills/profile/SKILL.md", ".claude/skills/personal-bg/SKILL.md"),
    (".claude/skills/pro-profile/SKILL.md", ".claude/skills/career-bg/SKILL.md"),
]

# Directories whose contents are historical records, not live protocol.
SKIP_DIRS = {".git", "sessions", "backup", "parked", "__pycache__", "node_modules"}

# Only text formats that can actually carry a live reference.
SCAN_EXT = {".md", ".py", ".sh", ".json", ".txt", ".zsh"}

# The dead names. Word-ish boundaries keep "LinkedIn profile" (ordinary English)
# from matching whilst still catching `profile.md`, `pro_profile`, `pro-profile`
# and `skills/profile`.
DEAD = re.compile(r"pro_profile|pro-profile|skills/profile\b|(?<![\w-])profile\.md")

# A permalink pinned to an immutable commit; the old path inside it is correct.
PINNED_URL = re.compile(
    r"https://raw\.githubusercontent\.com/\S+/[0-9a-f]{40}/\S+")

failures = []


def scan_files():
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            path = os.path.join(root, fn)
            if path == SELF:
                continue                      # this file quotes the dead names
            if os.path.splitext(fn)[1].lower() in SCAN_EXT:
                yield path


def line_is_exempt(line):
    """A line is exempt only if every dead-name hit sits inside a pinned URL."""
    spans = [m.span() for m in PINNED_URL.finditer(line)]
    for hit in DEAD.finditer(line):
        if not any(s <= hit.start() and hit.end() <= e for s, e in spans):
            return False
    return True


def test_renames_landed():
    """New paths exist; old paths are gone. A rename that left the original in
    place would give two sources of truth and guarantee drift."""
    for old, new in RENAMES:
        if not os.path.exists(os.path.join(REPO, new)):
            failures.append("missing after rename: %s" % new)
        if os.path.exists(os.path.join(REPO, old)):
            failures.append("old path still present: %s" % old)


def test_no_live_dead_references():
    """No live protocol file may still name the old files."""
    for path in scan_files():
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.readlines()
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(lines, 1):
            if DEAD.search(line) and not line_is_exempt(line):
                failures.append(
                    "%s:%d stale reference —— %s"
                    % (os.path.relpath(path, REPO), n, line.strip()[:110]))


def test_skill_names_are_hyphenated():
    """Skill `name` must equal its folder and contain only lowercase letters,
    numbers, and hyphens —— an underscore makes the skill fail to register, and
    the failure is invisible (the skill simply never appears)."""
    for _, new in RENAMES:
        if not new.startswith(".claude/skills/"):
            continue
        folder = new.split("/")[2]
        path = os.path.join(REPO, new)
        if not os.path.exists(path):
            continue                          # already reported above
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
        m = re.search(r"^name:\s*(.+?)\s*$", raw, re.M)
        if not m:
            failures.append("%s: no `name` key" % new)
            continue
        declared = m.group(1).strip("\"'")
        if declared != folder:
            failures.append(
                "%s: frontmatter name %r != folder %r" % (new, declared, folder))
        if not re.fullmatch(r"[a-z0-9-]+", declared):
            failures.append(
                "%s: name %r must be lowercase letters/numbers/hyphens only "
                "(underscores are rejected by Claude Code)" % (new, declared))


def test_skill_bodies_point_at_live_files():
    """A skill body naming a moved file fails mid-task, after the model has
    already committed to using it."""
    for _, new in RENAMES:
        if not new.startswith(".claude/skills/"):
            continue
        path = os.path.join(REPO, new)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            body = fh.read().split("---", 2)[-1]
        targets = [t for t in re.findall(r"`([^`]+)`", body) if "/" in t]
        if not targets:
            failures.append("%s: body names no target path" % new)
        for t in targets:
            if not os.path.exists(os.path.join(REPO, t)):
                failures.append("%s: body points at missing file %r" % (new, t))


def selftest():
    """Prove the matcher is not vacuous —— it must flag the dead names and must
    tolerate a pinned permalink and ordinary English use of the word."""
    must_flag = [
        "| `profile.md` | User's personal background needed |",
        "- 1.2. `career/pro_profile.md`",
        'Read `cp/career/pro_profile.md` in full',
        'boundary clause: "use pro-profile for career work"',
        ".claude/skills/profile/SKILL.md",
    ]
    must_pass = [
        "https://raw.githubusercontent.com/o/r/" + "a" * 40 + "/universal/profile.md",
        "| `personal_bg.md` | User's personal background needed |",
        "Synthesised profile of matched DA (A2/A3 marker).",
        "high-profile LinkedIn (hosted ING annual dinner)",
    ]
    bad = []
    for s in must_flag:
        if not DEAD.search(s) or line_is_exempt(s):
            bad.append("selftest: should have flagged —— %s" % s)
    for s in must_pass:
        if DEAD.search(s) and not line_is_exempt(s):
            bad.append("selftest: false positive —— %s" % s)
    return bad


def main():
    failures.extend(selftest())
    test_renames_landed()
    test_no_live_dead_references()
    test_skill_names_are_hyphenated()
    test_skill_bodies_point_at_live_files()

    if failures:
        print("FAIL —— %d problem(s):" % len(failures))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("PASS —— renames landed, no stale references, skill names valid, "
          "skill bodies resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
