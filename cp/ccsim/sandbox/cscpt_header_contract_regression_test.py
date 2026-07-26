#!/usr/bin/env python3
"""Regression test —— the `cscpt/` header contract must stay intact.

WHY THIS EXISTS (self-contained; no conversation or comms file explains it):

Every script in `cscpt/` is thousands of tokens and is meant to be RUN, never
read into a caller's context. The top comment is therefore split in two: a
`NON-CCSIM` block holding all a CALLER needs (what the tool does, its limits,
what to do about its output) and a `CCSIM` block holding what only an EDITOR
needs (wiring, payload shapes, design rationale). `cscpt/README.md` tells a
caller to extract the first block and read nothing else.

TWO INVARIANTS, both of which failed silently before they were checked here:

1. THE BLOCK MUST BE FENCED AT BOTH ENDS. An opening marker with no closing one
   gives an extractor no stopping point, so it reads to end-of-file and the
   caller ingests the entire script —— wasting precisely the context the split
   exists to save, and doing it invisibly, because the output still "looks
   right" at the top. Hence: exactly ONE start marker, exactly ONE end marker,
   start before end.

2. THE BLOCK MUST STAY SMALL. Every word here is paid for by every future
   caller of that script. Left unchecked these blocks grew past 200 words by
   accretion —— each addition individually reasonable, the total no longer
   something a busy agent will read. Hence the 100-word cap, measured over the
   content BETWEEN the markers (the marker lines themselves are structure, not
   content).

Anything trimmed under invariant 2 belongs in that script's `CCSIM` block, never
in the bin: a caller's needless detail is still an editor's load-bearing fact.
Invariant 3 below therefore checks the `CCSIM` block still exists, so a trim can
never quietly become a deletion.

AND THE RECIPE ITSELF IS EXERCISED, NOT ASSUMED. A marker pair that no command
can actually exploit would satisfy invariants 1–2 and still leave the caller
opening the whole file, so `test_documented_recipe_extracts_exactly_the_block`
runs the literal `sed` command README.md publishes and checks its real output.
That is the difference between "the markers exist" and "the documented workflow
works".

RUN:
    cd "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
    python3 cp/ccsim/sandbox/cscpt_header_contract_regression_test.py

Dependency-free by design (PyYAML is not installed system-wide on this Mac).
"""

import os
import re
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CSCPT = os.path.join(REPO, "cscpt")
README = os.path.join(CSCPT, "README.md")

WORD_CAP = 100

# Marker shapes. ASCII-only patterns on purpose —— they must never depend on
# matching the `——` inside the marker text, so no locale or encoding difference
# can make a check silently pass by matching nothing.
START_RE = re.compile(r"NON-CCSIM.*start")
END_RE = re.compile(r"NON-CCSIM.*end")
CCSIM_RE = re.compile(r"(?<!NON-)CCSIM\b")

# The extraction command `cscpt/README.md` publishes at rung 2 of its Read
# Order. Kept here verbatim so a silent edit to either side breaks this test
# rather than a caller's context budget.
RECIPE = r"sed -n '/NON-CCSIM.*start/,/NON-CCSIM.*end/p' {path}"

failures = []
checks = 0


def scripts():
    """Every runnable script in cscpt/, sorted. `.html` is a read template, not
    a script, so it carries no header contract and is excluded."""
    return sorted(
        f for f in os.listdir(CSCPT)
        if f.endswith((".py", ".sh")) and not f.startswith(".")
    )


def content_words(lines):
    """Words between the markers. A `.sh` block is comment-prefixed, so `# ` is
    stripped before counting —— otherwise every line would score a phantom
    word and the cap would bind ~30% tighter on shell scripts than on Python."""
    text = "\n".join(lines)
    text = re.sub(r"^\s*#\s?", "", text, flags=re.M)
    return text.split()


def check(ok, label, detail=""):
    global checks
    checks += 1
    if ok:
        print(f"[PASS] {label}")
    else:
        print(f"[FAIL] {label} —— {detail}")
        failures.append(label)


def test_marker_pair_is_exactly_one_each():
    for name in scripts():
        lines = open(os.path.join(CSCPT, name), encoding="utf-8").read().splitlines()
        starts = [i for i, l in enumerate(lines) if START_RE.search(l)]
        ends = [i for i, l in enumerate(lines) if END_RE.search(l)]
        check(
            len(starts) == 1 and len(ends) == 1 and starts[0] < ends[0],
            f"{name}: exactly one NON-CCSIM start + one end, in order",
            f"starts={len(starts)} ends={len(ends)} "
            f"positions={starts[:3]}/{ends[:3]}",
        )


def test_block_within_word_cap():
    for name in scripts():
        lines = open(os.path.join(CSCPT, name), encoding="utf-8").read().splitlines()
        starts = [i for i, l in enumerate(lines) if START_RE.search(l)]
        ends = [i for i, l in enumerate(lines) if END_RE.search(l)]
        if not (starts and ends and starts[0] < ends[0]):
            continue  # already reported by the marker-pair test
        n = len(content_words(lines[starts[0] + 1:ends[0]]))
        check(
            n <= WORD_CAP,
            f"{name}: NON-CCSIM block is {n}w (cap {WORD_CAP})",
            f"{n - WORD_CAP}w over —— move the excess into CCSIM, do not delete it",
        )


def test_ccsim_block_survives():
    """A trim must MOVE content, not drop it. If a script has a NON-CCSIM block
    it must also still have a CCSIM block to have moved that content into."""
    for name in scripts():
        text = open(os.path.join(CSCPT, name), encoding="utf-8").read()
        check(
            bool(CCSIM_RE.search(text)),
            f"{name}: CCSIM block still present",
            "NON-CCSIM was trimmed with nowhere for the detail to land",
        )


def test_documented_recipe_extracts_exactly_the_block():
    """End-to-end: run README's own command and check what it really returns ——
    a span that starts at the start marker, ends at the end marker, and is
    strictly shorter than the file it came from."""
    for name in scripts():
        path = os.path.join("cscpt", name)
        out = subprocess.run(
            RECIPE.format(path=path),
            shell=True, cwd=REPO, capture_output=True, text=True,
        )
        got = out.stdout.splitlines()
        whole = open(os.path.join(CSCPT, name), encoding="utf-8").read().splitlines()
        ok = (
            out.returncode == 0
            and len(got) >= 3
            and START_RE.search(got[0])
            and END_RE.search(got[-1])
            and len(got) < len(whole)
            # Nothing but the two markers may match a marker pattern, so the
            # span can never have run past its own terminator.
            and not any(START_RE.search(l) or END_RE.search(l) for l in got[1:-1])
        )
        check(
            ok,
            f"{name}: README's sed recipe returns exactly the block "
            f"({len(got)} of {len(whole)} lines)",
            f"rc={out.returncode} first={got[:1]} last={got[-1:]}",
        )


def test_readme_publishes_the_recipe():
    """The recipe must be IN the README, not merely known to work —— a caller
    who never sees it opens the whole file instead."""
    text = open(README, encoding="utf-8").read()
    check(
        "NON-CCSIM.*start" in text and "NON-CCSIM.*end" in text and "sed -n" in text,
        "README.md publishes the extraction command",
        "rung 2 must give the reader a concrete way to extract just the block",
    )
    check(
        str(WORD_CAP) in text,
        f"README.md states the {WORD_CAP}-word cap",
        "an unstated cap is an uncheckable one for the next editor",
    )


def main():
    print(f"Repo: {REPO}\nScripts under test: {len(scripts())}\n")
    test_marker_pair_is_exactly_one_each()
    test_block_within_word_cap()
    test_ccsim_block_survives()
    test_documented_recipe_extracts_exactly_the_block()
    test_readme_publishes_the_recipe()
    print()
    if failures:
        print(f"{checks - len(failures)}/{checks} passed —— FAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"{checks}/{checks} passed —— header contract intact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
