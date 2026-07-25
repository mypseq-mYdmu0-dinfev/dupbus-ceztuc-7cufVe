#!/usr/bin/env python3
"""Regression test for `.claude/skills/*/SKILL.md` frontmatter.

WHY THIS EXISTS (self-contained —— no conversation or comms file explains it):

A skill's frontmatter `description` is injected into the system prompt on every
turn, and it is the ONLY thing the model matches against when deciding whether
to invoke the skill. A description that is silently damaged costs the whole
skill, invisibly: the file looks perfect on screen and the skill simply never
fires properly.

The failure this test pins actually happened. The `google` skill was authored as:

    description: Use for the user's personal email or calendar operations, or when #job is mentioned. Loads the Google email/calendar and job workflow.

YAML treats a ` #` inside an UNQUOTED scalar as the start of a comment, so
everything from `#job` onwards was discarded before the model ever saw it: 134
authored characters became 65 surviving ones (51% lost), and the published skill
listing read "…or calendar operations, or when" and simply stopped. Nothing
warned —— the file looked perfect on screen.

Rules enforced here (each is a deterministic check, which beats hoping an
instruction is obeyed —— see `universal/coding.md` § Testing):

  1. No unquoted description may contain ` #` (the truncation bug above).
     Writing `#trigger` in a description is pointless anyway: the `hlint`
     UserPromptSubmit hook already catches every literal `#trigger` in a prompt
     and points at the matching pcmd.
  2. `name` must equal the containing folder name (that is how the skill is
     addressed; a mismatch makes it unaddressable).
  3. Every path the body points at must exist —— a skill whose target has moved
     fails mid-task, after the model has already committed to using it.

House style for the descriptions themselves: `cp/ccsim/skiller.md`.

Usage: python3 cp/ccsim/sandbox/skill_desc_regression_test.py
Exit 0 = all good; exit 1 = at least one failure (details on stdout).
Deliberately dependency-free (PyYAML is not installed system-wide on this Mac),
so the ` #` rule is implemented directly rather than via a YAML parser.
"""

import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SKILLS = os.path.join(REPO, ".claude", "skills")

# The exact historic line that broke, kept as a fixture so the detector can
# never silently stop detecting it (mining the real past input, not a synthetic
# lookalike, is what makes this a regression test rather than a demo).
HISTORIC_BROKEN = (
    "description: Use for the user's personal email or calendar operations, "
    "or when #job is mentioned. Loads the Google email/calendar and job workflow."
)

PATH_RE = re.compile(r"`([^`]+\.(?:md|py|html|sh|json))`")


def truncating_hash(desc_line):
    """True if this raw `description:` line would be cut short by YAML.

    `desc_line` is everything after `description:`. A value wrapped in matching
    quotes is safe (the `#` is inside the scalar); an unquoted value is cut at
    the first ` #`, and also at a `#` that opens the value.
    """
    value = desc_line.strip()
    if len(value) >= 2 and value[0] in "'\"" and value[-1] == value[0]:
        return False
    return " #" in value or value.startswith("#")


def parse_frontmatter(text):
    """Return (raw_frontmatter, body) or (None, None) if the fences are absent."""
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
    return (m.group(1), m.group(2)) if m else (None, None)


def scalar(raw, key):
    m = re.search(r"^%s:\s*(.*)$" % re.escape(key), raw, re.M)
    return m.group(1) if m else None


def main():
    failures = []

    # --- Fixture: the detector must still catch the original defect. ----------
    if not truncating_hash(HISTORIC_BROKEN.split("description:", 1)[1]):
        failures.append(
            "FIXTURE: the historic truncated `google` description is no longer "
            "detected —— the ` #` rule has regressed."
        )
    # A quoted version of the same text must NOT be flagged (no false positive).
    if truncating_hash(' "text with #job inside" '):
        failures.append("FIXTURE: a quoted description was wrongly flagged.")

    # --- Live skills ---------------------------------------------------------
    if not os.path.isdir(SKILLS):
        print("FAIL: no skills directory at %s" % SKILLS)
        return 1

    names = sorted(
        n for n in os.listdir(SKILLS)
        if os.path.isfile(os.path.join(SKILLS, n, "SKILL.md"))
    )
    if not names:
        failures.append("no SKILL.md found under %s" % SKILLS)

    for name in names:
        path = os.path.join(SKILLS, name, "SKILL.md")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()

        raw, body = parse_frontmatter(text)
        if raw is None:
            failures.append("%s: frontmatter fences missing or malformed" % name)
            continue

        desc_line = scalar(raw, "description")
        if desc_line is None:
            failures.append("%s: no `description` key" % name)
        elif truncating_hash(desc_line):
            failures.append(
                "%s: description contains an unquoted ` #` —— YAML will discard "
                "everything from there to end of line" % name
            )

        declared = scalar(raw, "name")
        if declared is None:
            failures.append("%s: no `name` key" % name)
        elif declared.strip().strip("\"'") != name:
            failures.append(
                "%s: frontmatter name %r does not match its folder"
                % (name, declared.strip())
            )

        for target in dict.fromkeys(PATH_RE.findall(body or "")):
            if "/" not in target:          # a bare filename is prose, not a path
                continue
            resolved = (
                os.path.expanduser(target) if target.startswith("~")
                else os.path.join(REPO, target)
            )
            if not os.path.exists(resolved):
                failures.append("%s: body points at a missing file %r" % (name, target))

    if failures:
        print("FAIL (%d):" % len(failures))
        for f in failures:
            print("  - %s" % f)
        return 1

    print("PASS: %d skills —— descriptions intact, names match, targets exist."
          % len(names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
