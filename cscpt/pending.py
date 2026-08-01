#!/usr/bin/env python3
"""pending.py —— the user's outstanding-queue sweep (RUN, don't read). Prints
both halves of what is waiting on HIM: voided files awaiting his manual delete,
and queued queries awaiting his manual send. Read-only; never deletes anything.

=== NON-CCSIM —— start of all you need to RUN it ===
WHAT: prints the two queues only the USER can clear, with days-since-mtime.
  1. Voided `❌_*` files in THIS repo, flagged when ≥7 days old (root §8.2.4).
  2. `sessions/queued_queries/*` awaiting a dedicated session.

CLI:  python3 cscpt/pending.py            -> both queues, oldest first
      python3 cscpt/pending.py --quiet    -> print nothing when both are empty

Exit 0 always. It PRINTS; the user acts. It never renames, moves or deletes.
Call it at CCSIM session start and at every `#wrap`.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WHY IT EXISTS: root `CLAUDE.md` §8.2.4 mandates reminding the user of any voided
file ≥7 days old and then disarms itself in the same line —— "don't actively
search". So the reminder could never fire. Each session saw only what it voided
that day; the queue accumulated invisibly (9 files, the oldest 37 days, when this
was written). `sessions/queued_queries/` had the identical shape: CC's half done,
the user's half invisible. Two queues, ONE mechanism, deliberately —— two
mechanisms for one problem is the drift `cp/ccsim/CLAUDE.md` §8.2 warns against.

WHY A SCRIPT, NOT A TEMPLATE LINE: a template line is an instruction to remember,
which is the failure class here. A script invoked at a defined moment is a
condition (§8.1).

Root scope: `dupbus-ceztuc-7cufVe/` ONLY, minus `backup/`. `AJAP_repo/` is
excluded deliberately —— see below. Anchored on this file's `__file__`.

SCOPE IS THIS REPO ONLY, AND THAT IS LOAD-BEARING: `AJAP_repo/` holds 790⁺
`❌_`-prefixed files under `gcl/skipped/skipped_archive/`. There the prefix means
"skipped job, archived", NOT "awaiting the user's delete". Widening this sweep to
sibling repos would bury the real queue under hundreds of false entries and
invite a catastrophic mass-delete on the prefix alone. Anchor on this file's own
repo root, never on the process cwd.

`backup/` IS EXCLUDED: `backup/README.md` says "NEVER edit/delete anything", so a
voided file there is not actionable and listing it would be noise the user cannot
clear. If that README is ever carved out for a subtree, drop the exclusion.
=== CCSIM —— end ===
"""

import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)

_VOID_PREFIX = "❌_"           # ❌_
_STALE_DAYS = 7                    # root CLAUDE.md §8.2.4
_QUEUE_DIR = os.path.join(_REPO, "sessions", "queued_queries")
_SKIP_DIRS = {".git", "node_modules", "__pycache__"}
_SKIP_TOP = {"backup"}             # see CCSIM header
_QUEUE_IGNORE = {"README.md", ".DS_Store"}


def _age_days(path):
    try:
        return (time.time() - os.path.getmtime(path)) / 86400.0
    except OSError:
        return 0.0


def voided():
    """Every `❌_` file in this repo, oldest first, as (rel_path, age_days)."""
    out = []
    for root, dirs, files in os.walk(_REPO):
        rel_root = os.path.relpath(root, _REPO)
        top = rel_root.split(os.sep)[0]
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        if top in _SKIP_TOP:
            dirs[:] = []
            continue
        for name in files:
            if name.startswith(_VOID_PREFIX):
                full = os.path.join(root, name)
                out.append((os.path.relpath(full, _REPO), _age_days(full)))
    out.sort(key=lambda r: -r[1])
    return out


def queued():
    """Queued queries awaiting a dedicated session, oldest first."""
    out = []
    if not os.path.isdir(_QUEUE_DIR):
        return out
    for name in os.listdir(_QUEUE_DIR):
        if name in _QUEUE_IGNORE or name.startswith(_VOID_PREFIX):
            continue
        full = os.path.join(_QUEUE_DIR, name)
        if os.path.isfile(full):
            out.append((name, _age_days(full)))
    out.sort(key=lambda r: -r[1])
    return out


def main(argv):
    quiet = "--quiet" in argv
    v, q = voided(), queued()
    if quiet and not v and not q:
        return 0

    print("=== PENDING —— waiting on the USER ===")

    stale = [r for r in v if r[1] >= _STALE_DAYS]
    print("\nVoided files awaiting manual delete (%d, %d of them >=%dd):"
          % (len(v), len(stale), _STALE_DAYS))
    if not v:
        print("  (none)")
    for rel, age in v:
        flag = "!" if age >= _STALE_DAYS else " "
        print("  %s %4.0fd  %s" % (flag, age, rel))

    print("\nQueued queries awaiting a dedicated session (%d):" % len(q))
    if not q:
        print("  (none)")
    for name, age in q:
        print("    %4.0fd  %s" % (age, name))

    print("\nCC never deletes or sends these —— print, then leave them to the user.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
