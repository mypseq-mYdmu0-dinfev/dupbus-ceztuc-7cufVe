#!/usr/bin/env python3
"""Regression test —— FILE-LESS modifiers must stay file-less, and must stay
declared as such in the one file that governs each.

WHY THIS EXISTS (self-contained; no conversation or comms file explains it):

Root CLAUDE.md §7.3.1 resolves a `#[trigger]` by READING `universal/
[trigger].md`, and `cscpt/hlint.py` mechanises that at prompt-submit time by
injecting "READ `<path>`" for every `#name` whose file it can find. Three
triggers deliberately have NO file of their own —— they are MODIFIERS defined
inside a section of a larger protocol file:

    #bite      -> universal/numbered.md  § Bite-size —— `#bite`
    #opt       -> universal/numbered.md  § Optional-Reading Offload —— `#opt`
    #rephrase  -> universal/coding.md    § `#rephrase` —— How to Report a Problem

That arrangement is only safe while BOTH halves hold:

(1) NO `bite.md` / `opt.md` / `rephrase.md` EXISTS IN HLINT'S SEARCH SCOPE.
    The day one appears, two failures land at once. hlint starts injecting
    "READ `universal/bite.md`" —— which is correct behaviour for a trigger that
    HAS a file, so nothing looks broken —— and the modifier acquires a second
    source of truth that will drift from the section that actually governs it.
    §7.3.1 sends the session to the file; the section keeps being edited. This
    check is the cheap guard: a stat, not a careful memory.

(2) EACH OWNING FILE SAYS SO, IN WORDS. A reader who meets `#bite` and finds no
    `bite.md` must not conclude the protocol is missing and go hunting (or, far
    worse, invent one). Every modifier therefore carries a "never find
    `<name>.md`" clause at the top of its own section, and this test pins that
    clause so a later trim of an Unconditional file cannot quietly remove it.

The three are checked together, not one per test file, because they are ONE
convention with one failure mode —— and because `#rephrase` is the house
precedent the other two copy, so a drift between them is itself the defect.

WHY THE SELECTOR RULING IS PINNED TOO: `#numbered` and `#bite` both apply by
DEFAULT (numbered.md is an Unconditional), so a prompt naming exactly one of
them can only mean "this one, not the other" —— it cannot mean "remind me",
which is what naming BOTH means. That distinction has no safe default: if the
file stops stating it, a session prompted `#bite` alone must guess whether
numbering is suspended or merely unmentioned, and coding.md § Prompted
Components names precisely that as a coin-flip at runtime. So the wording is
enforced, not trusted.

RUN:
    cd "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
    python3 cp/ccsim/sandbox/modifier_trigger_regression_test.py

Dependency-free by design (PyYAML is not installed system-wide on this Mac).
"""

import os
import re
import sys
import importlib.util

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PARENT = os.path.dirname(REPO)

# Modifier -> the file whose section defines it. Mirrors hlint's own scope
# (`universal/`, `cp/`, `AJAP_repo/protocols/`, `AJAP_repo/inv/inveng.md`);
# a name resolving ANYWHERE in there would make hlint fire.
MODIFIERS = {
    "bite": "universal/numbered.md",
    "opt": "universal/numbered.md",
    "rephrase": "universal/coding.md",
}

# Where a stray `<name>.md` would be found by hlint and therefore matter.
SCOPE_DIRS = [
    os.path.join(REPO, "universal"),
    os.path.join(REPO, "cp"),
    os.path.join(PARENT, "AJAP_repo", "protocols"),
]

# Directories never walked (VCS internals, caches) —— mirrors hlint.
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "sessions",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
}

failures = []


def _read(rel):
    path = os.path.join(REPO, rel)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _load_hlint():
    """Import `cscpt/hlint.py` as a module so the resolver itself is
    exercised, rather than a re-implementation of it that could agree with
    a bug."""
    path = os.path.join(REPO, "cscpt", "hlint.py")
    spec = importlib.util.spec_from_file_location("hlint_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_no_modifier_file_exists():
    """(1) No `<name>.md` anywhere hlint would look."""
    wanted = {"%s.md" % n for n in MODIFIERS}
    for root in SCOPE_DIRS:
        if not os.path.isdir(root):
            continue                       # absent sibling checkout is fine
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if fn.lower() in wanted:
                    failures.append(
                        "a modifier must have NO file of its own, but "
                        "%s exists —— hlint will now inject a READ for it, "
                        "and its governing section becomes a second source "
                        "of truth" % os.path.join(dirpath, fn))


def test_hlint_stays_silent_on_each_modifier():
    """(1), behaviourally —— ask hlint's OWN resolver, not the filesystem."""
    try:
        hlint = _load_hlint()
    except Exception as exc:
        failures.append("could not import cscpt/hlint.py: %r" % exc)
        return
    # Non-vacuous: a trigger that DOES have a file must resolve, else a
    # broken resolver would pass every case below for the wrong reason.
    if hlint._resolve_trigger("numbered") != "universal/numbered.md":
        failures.append(
            "hlint no longer resolves `#numbered` to universal/numbered.md —— "
            "the silence checks below prove nothing until this passes")
        return
    for name in sorted(MODIFIERS):
        got = hlint._resolve_trigger(name)
        if got is not None:
            failures.append(
                "hlint resolves `#%s` to %s —— a file-less modifier must "
                "resolve to nothing, or sessions get sent to a file that "
                "should not exist" % (name, got))


def test_each_modifier_is_declared_file_less():
    """(2) The owning file states the absence in words."""
    for name, rel in sorted(MODIFIERS.items()):
        text = _read(rel)
        if not re.search(r"never find `%s\.md`" % re.escape(name), text):
            failures.append(
                "%s must carry a \"never find `%s.md`\" clause in the section "
                "defining `#%s`, so a reader who finds no such file does not "
                "hunt for one or invent it" % (rel, name, name))


def test_selector_ruling_is_stated():
    """The `#numbered` / `#bite` selector semantics must stay explicit."""
    text = _read("universal/numbered.md")
    needed = [
        (r"`#numbered`\s+only\s+——.*bite-size SUSPENDED",
         "`#numbered` only —— bite-size SUSPENDED"),
        (r"`#bite`\s+only\s+——.*numbering SUSPENDED",
         "`#bite` only —— numbering SUSPENDED"),
        (r"NEITHER or BOTH",
         "NEITHER or BOTH = the default (both apply)"),
    ]
    for pattern, human in needed:
        if not re.search(pattern, text):
            failures.append(
                "universal/numbered.md no longer states: %s —— without it a "
                "lone tag is a coin-flip between 'suspend the other' and "
                "'mere reminder'" % human)
    # `#opt` modifies BOTH tags and must be excluded from that selector,
    # else `#opt` alone reads as suspending something.
    if not re.search(r"`#opt`.*\bBOTH tags\b", text):
        failures.append(
            "universal/numbered.md must state that `#opt` modifies BOTH tags "
            "(so it is never read as a selector suspending one of them)")
    # TWO TAGS, TWO TARGETS, ONE SENTENCE. The selector above is per-TARGET,
    # not per-output: "ensure X #numbered & Y #bite" names both tags yet means
    # neither is a reminder —— each binds to its own target and suspends the
    # other THERE. Read per-OUTPUT instead, that sentence collapses to
    # "NEITHER or BOTH = the default", i.e. both tags on everything, which is
    # the opposite of what was asked. The two rules only coexist because the
    # scope is stated; drop the scope and they contradict.
    if not re.search(r"SELECTOR, scoped to its named TARGET", text):
        failures.append(
            "universal/numbered.md must scope the selector to the tag's named "
            "TARGET —— unscoped, `ensure X #numbered & Y #bite` reads as the "
            "both-tags default and each target's deselection is lost")
    if not re.search(r"DIFFERENT targets\s+——.*suspending the other", text):
        failures.append(
            "universal/numbered.md must state that BOTH tags on DIFFERENT "
            "targets each govern their own & suspend the other there")


def test_opt_placement_rule_is_stated():
    """`#opt` must keep its three-case placement rule.

    The user does NOT read below the `#opt` separator —— by his own account he
    treats it as a record for future CC. So anything needing his input placed
    there is not merely deprioritised, it is never seen: three real misses in
    one session (an unanswered question, a requested edit, a "worth your eye"
    finding) all traced to that single mistake. The rule is graded, not a ban,
    which is exactly why it must stay written down: case 1 is absolute, cases
    2 and 3 are judgement, and a session that remembers only "use #opt when
    long" will re-make the miss."""
    text = _read("universal/numbered.md")
    if not re.search(r"input/decision/action.*NEVER below", text):
        failures.append(
            "universal/numbered.md must state that anything needing the "
            "user's input/decision/action NEVER goes below the `#opt` line")
    if not re.search(r"future CC benefits.*lean below", text):
        failures.append(
            "universal/numbered.md must keep the middle `#opt` case (no input "
            "needed BUT future CC benefits -> judge, lean below), else the "
            "rule reads as a binary and the record-keeping half is lost")


def test_sequential_reply_rule_is_stated():
    """Reply order must track the query's order, with BOTH exemptions.

    He reads `query_` and `response_` side by side from the top, so answering
    his pt 8 before his pt 1 scrambles the thread. Model output order is not
    harness-enforceable —— no lint can see intent —— so the instruction IS the
    only control, and it must carry its two exemptions or it will be
    over-applied: GROUPING (one pt answering several of his) saves him reading
    and is wanted; an `#opt` offload necessarily sits at the bottom."""
    text = _read("universal/numbered.md")
    if not re.search(r"Sequential Reply\s+——", text):
        failures.append(
            "universal/numbered.md § Optimise for Reply must carry the "
            "Sequential Reply rule (answer his pts in HIS order)")
    if len(re.findall(r"- EXEMPT: ", text)) < 2:
        failures.append(
            "universal/numbered.md must state BOTH Sequential Reply "
            "exemptions (grouping, and pts offloaded to `#opt`) —— with "
            "either missing, the rule gets over-applied")


def selftest():
    """Prove the matchers are not vacuous —— each must reject text that omits
    the clause it is meant to pin."""
    bad = []
    if re.search(r"never find `bite\.md`", "a file named bite.md governs this"):
        bad.append("selftest: declaration matcher is too loose")
    if not re.search(r"never find `bite\.md`",
                     "- Triggered by: `#bite` —— never find `bite.md` (this "
                     "§ governs)"):
        bad.append("selftest: declaration matcher misses the real clause")
    # The three newer matchers must reject the PRIOR wording, else they would
    # pass on a file that has silently reverted to it.
    if re.search(r"SELECTOR, scoped to its named TARGET",
                 "- Tag(s) in a query that ALSO carries content = a SELECTOR:"):
        bad.append("selftest: target-scope matcher passes the unscoped form")
    if re.search(r"input/decision/action.*NEVER below",
                 "- `[optional_reading]` = still #numbered, CC-facing appendix"):
        bad.append("selftest: `#opt` placement matcher is too loose")
    if re.search(r"Sequential Reply\s+——",
                 "- Numbering Continuity —— DEFAULT is to CONTINUE at n+1"):
        bad.append("selftest: sequential-reply matcher is too loose")
    return bad


def main():
    failures.extend(selftest())
    test_no_modifier_file_exists()
    test_hlint_stays_silent_on_each_modifier()
    test_each_modifier_is_declared_file_less()
    test_selector_ruling_is_stated()
    test_opt_placement_rule_is_stated()
    test_sequential_reply_rule_is_stated()

    if failures:
        print("FAIL —— %d problem(s):" % len(failures))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("PASS —— #bite/#opt/#rephrase stay file-less, hlint stays silent on "
          "each, every owning file declares it; selector (incl. per-target "
          "scope), `#opt` placement, and sequential-reply rulings intact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
