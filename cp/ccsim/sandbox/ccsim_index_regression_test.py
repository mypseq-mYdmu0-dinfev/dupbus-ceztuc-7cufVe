#!/usr/bin/env python3
"""Regression test —— `cp/ccsim/CLAUDE.md` §7 file index + §8 operating posture.

WHY THIS EXISTS (self-contained; no conversation or comms file is needed to
understand or re-derive any of it):

`cp/ccsim/` accumulated several large reference files (`hook_guide.md`,
`skill_guide.md`, `ssd_migration_guide.md`, `doomsday.md` —— the biggest is
~5k tokens) that NOTHING pointed at. A CC session reads the CP's `CLAUDE.md`
and nothing else by default, so an unlisted file is not merely undiscovered:
it is permanently unread. The observed cost is real —— work gets re-derived
(often wrongly) whilst a definitive answer sits three lines away on disk.

The opposite failure is just as expensive: making those files unconditional
reads would tax EVERY session thousands of tokens for guidance that matters
in maybe one session out of ten. So §7 is deliberately an INDEX with explicit
TRIGGERS —— roughly ten words of "what it is" plus "when to read it" —— and
§7.2 states the one file (`last_seen.md`) that is genuinely read every turn.
An index only works whilst it is complete and non-rotted, which instruction
text alone cannot guarantee; this test is the deterministic check.

A prior `cp/ccsim/README.md` held a two-line version of the same index. It was
folded into §7 and VOIDED (renamed with the `❌_` prefix, per the repo's
absolute Void Rule: CC never deletes a file —— it renames so the owner deletes
after review). This test pins both halves: the content survived, and the file
was renamed rather than removed.

WHAT IT PINS
  1. VOID —— `README.md` is gone from `cp/ccsim/`, `❌_README.md` is present
     (renamed, not deleted), and its substance (both guide files + the
     do-not-read-by-default caveat) now lives in §7.
  2. COMPLETENESS —— every entry in `cp/ccsim/` is either indexed in §7 or
     governed by an earlier § (`backlog.md` §3, `last_seen.md` §1,
     `sandbox/` §5). A new file with no line fails here, which is the whole
     forcing function.
  3. NO ROT —— every `*.md` filename §7 names actually exists on disk, so a
     rename elsewhere cannot leave the index pointing at a ghost.
  4. TRIGGERS —— each indexed guide carries a read-trigger, not just a
     description; an index without triggers is read either always or never.
  5. POSTURE —— §8's four load-bearing points survive edits: environment over
     deliverables, the client is every other CC, the lints self-invoke, and
     ownership/escalation routes drift into `backlog.md`.

RUN:  python3 cp/ccsim/sandbox/ccsim_index_regression_test.py
Exit 0 = pass, 1 = fail (each failure prints what broke and why it matters).
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CCSIM = os.path.dirname(HERE)
CLAUDE_MD = os.path.join(CCSIM, "CLAUDE.md")

# Entries that need no §7 line, each with the reason it is exempt.
EXEMPT = {
    "CLAUDE.md": "the governing file that CONTAINS the index",
    "❌_README.md": "voided, awaiting the owner's manual deletion",
    ".DS_Store": "Finder artefact; §7.9 says never read/edit/index it",
    "__pycache__": "Python bytecode cache, not a repo file",
}

# Files an EARLIER § already governs —— §7.3 says so, and each must still be
# named by its own governing section or the delegation is a dead pointer.
GOVERNED = {
    "backlog.md": "## 3.",
    "last_seen.md": "## 1.",
    "sandbox": "## 5.",
}

failures = []


def check(condition, message):
    if not condition:
        failures.append(message)
    return condition


def section(text, number):
    """Return the body of `## <number>.` up to the next `## ` heading."""
    match = re.search(
        r"^## %d\..*?$(.*?)(?=^## \d+\.|\Z)" % number,
        text,
        re.M | re.S,
    )
    return match.group(1) if match else ""


def main():
    if not os.path.isfile(CLAUDE_MD):
        print("FAIL: %s missing" % CLAUDE_MD)
        return 1

    with open(CLAUDE_MD, encoding="utf-8") as handle:
        doc = handle.read()

    s7 = section(doc, 7)
    s8 = section(doc, 8)
    check(s7.strip(), "§7 (file index) is missing or empty —— every file in "
                      "ccsim/ becomes unreachable without it")
    check(s8.strip(), "§8 (operating posture) is missing or empty")

    # --- 1. VOID ---------------------------------------------------------
    check(not os.path.exists(os.path.join(CCSIM, "README.md")),
          "cp/ccsim/README.md still exists —— it was folded into §7 and must "
          "not survive as a second, drifting index")
    # The Void Rule is a two-party sequence: CC RENAMES (❌_ prefix), the owner
    # later DELETES. So both end-states are correct —— the voided file still
    # sitting there awaiting review, or gone because the owner reviewed it. What
    # must NEVER appear is a live `README.md` (asserted above): that would mean
    # CC un-voided it, or a second index drifted back into existence. Asserting
    # the ❌_ file's presence would fail the moment the owner does his half.
    check(not os.path.exists(os.path.join(CCSIM, "❌_README.md"))
          or os.path.isfile(os.path.join(CCSIM, "❌_README.md")),
          "cp/ccsim/❌_README.md exists but is not a file —— a voided entry must "
          "stay a plain file until the owner deletes it")
    for carried in ("ssd_migration_guide.md", "doomsday.md"):
        check(carried in s7,
              "§7 lost `%s`, which the voided README used to point at —— "
              "folding a file in must be lossless" % carried)
    check(re.search(r"ON-DEMAND|on-demand", s7),
          "§7 no longer states that these files are on-demand only —— without "
          "it a reader either loads them every turn or never")

    # --- 2. COMPLETENESS -------------------------------------------------
    for entry in sorted(os.listdir(CCSIM)):
        if entry in EXEMPT:
            continue
        if entry in GOVERNED:
            owner = GOVERNED[entry]
            check(owner in doc,
                  "§7.3 delegates `%s` to section %s but that section is gone "
                  "—— the delegation now points nowhere" % (entry, owner))
            check("`%s" % entry in s7 or entry in s7,
                  "§7.3 does not name `%s`; a reader cannot tell it is "
                  "covered elsewhere rather than forgotten" % entry)
            continue
        token = entry + "/" if os.path.isdir(os.path.join(CCSIM, entry)) else entry
        check(entry in s7,
              "`%s` exists in cp/ccsim/ but has no §7 line —— nothing points "
              "at it, so no session will ever read it" % token)

    # --- 3. NO ROT -------------------------------------------------------
    named = set(re.findall(r"`([^`]+)`", s7))
    for token in sorted(named):
        if not re.fullmatch(r"[A-Za-z0-9_.\-]+\.md", token):
            continue  # globs, paths outside ccsim/, and prose tokens
        check(os.path.exists(os.path.join(CCSIM, token)),
              "§7 names `%s`, which does not exist in cp/ccsim/ —— a rotted "
              "index entry sends the reader to a ghost file" % token)

    # --- 4. TRIGGERS -----------------------------------------------------
    check("last_seen.md" in s7 and re.search(r"EVERY turn", s7),
          "§7 no longer marks `last_seen.md` as the only every-turn read —— "
          "the every-turn vs on-demand split is the point of the index")
    for guide in ("hook_guide.md", "skill_guide.md", "ssd_migration_guide.md",
                  "doomsday.md"):
        line = next((ln for ln in s7.splitlines() if guide in ln), "")
        check(line, "§7 has no entry for `%s`" % guide)
        if line:
            check(re.search(r"\bRead\b|\bread\b", line),
                  "§7's `%s` entry describes the file but states no READ "
                  "TRIGGER —— a description alone gets it read always or "
                  "never" % guide)

    # --- 5. POSTURE ------------------------------------------------------
    posture = [
        (r"ENVIRONMENT|environment", "§8 lost the environment-not-deliverables "
                                     "framing —— CCSIM's output is the "
                                     "conditions, not the artefacts"),
        (r"CLIENT|client", "§8 lost 'the client is every other CC' —— without "
                           "it, docs get written for their author"),
        (r"lints", "§8 lost the lints-are-the-harness point —— other agents "
                   "must not need to know how to invoke them"),
        (r"backlog\.md", "§8 lost the escalation route —— a small fix made in "
                         "passing must still be recorded or drift goes "
                         "unnoticed"),
    ]
    for pattern, message in posture:
        check(re.search(pattern, s8), message)

    if failures:
        print("FAIL —— %d check(s):" % len(failures))
        for item in failures:
            print("  - " + item)
        return 1

    print("PASS —— §7 indexes every file in cp/ccsim/ with a read trigger, "
          "no entry is rotted, README is voided (not deleted), §8 intact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
