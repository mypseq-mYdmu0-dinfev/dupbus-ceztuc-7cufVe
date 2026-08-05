#!/usr/bin/env python3
"""CCSIM Session-Start Housekeeping (RUN, don't read)

Three read-only sweeps over the queues only the USER can clear: voided files
awaiting his manual delete, queued queries awaiting his manual send, and
stray-space filenames awaiting a rename. It PRINTS; the user acts. It never
deletes, renames, moves or sends anything.

=== NON-CCSIM —— start of all you need to RUN it ===
WHAT: prints three queues only the USER can clear, oldest first, with ages.
  1. Voided `❌_*` files, flagged at >=7 days old (root §8.2.4).
  2. `sessions/queued_queries/*` awaiting a dedicated session.
  3. Stray-space filenames (a space before the 12-digit TS) needing a rename.

CLI:  python3 cscpt/ccsim_housekeeping.py           -> all three queues
      python3 cscpt/ccsim_housekeeping.py --quiet   -> silent when all empty

CCSIM ONLY, at session start. Other sessions must not run it —— the output is
noise they have no standing to act on. Exit 0 always.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WHY IT EXISTS: root `CLAUDE.md` §8.2.4 mandates reminding the user of any
voided file >=7 days old and then disarms itself in the same line —— "don't
actively search". So the reminder could never fire. Each session saw only what
it voided that day; the queue accumulated invisibly (9 files, the oldest 37
days, when this was written). `sessions/queued_queries/` had the identical
shape: CC's half done, the user's half invisible. Stray-space filenames are the
third instance of that shape —— the lint that knows the rule only ever sees the
folder in front of it. Three queues, ONE mechanism, deliberately —— three
mechanisms for one problem is the drift `cp/ccsim/CLAUDE.md` §8.2 warns against.

WHY A SCRIPT, NOT A TEMPLATE LINE: a template line is an instruction to
remember, which is the failure class here. A script invoked at a defined moment
is a condition (§8.1).

WHY CCSIM-ONLY, AND WHY THAT IS IN THE NAME: every entry it prints needs a
decision only the user can make, so any other session gets a wall of text it
cannot act on and must then explain away. The filename says who owns the call
so nobody has to look it up.

Root scope: EVERY sibling under `Fury Documents/GitHub/` —— today
`dupbus-ceztuc-7cufVe/` alone, tomorrow whatever work repos are added beside it
—— MINUS `AJAP_repo/`, the single exclusion, for the reason below. Loose files
sitting directly in `GitHub/` are swept too. Anchored on this file's own
`__file__`, never on the process cwd. ONE exception: queue 2 stays anchored to
THIS repo, because `sessions/queued_queries/` is a dupbus convention no sibling
has; a sibling adopting it needs `_QUEUE_DIRS` extended, one line.

AJAP EXCLUSION —— LOAD-BEARING, NOT TIDINESS: `AJAP_repo/` holds 790+
`❌_`-prefixed files under `gcl/skipped/skipped_archive/`. THERE the prefix
means "skipped job, archived", NOT "awaiting the user's delete" (root §8.2).
Sweeping it would bury the real queue under hundreds of false entries and
invite a catastrophic mass-delete on the prefix alone. It must survive any
future widening; a repo earns an exclusion only by REDEFINING `❌_`, never by
merely being large or noisy.

WHY GitHub-WIDE RATHER THAN THIS REPO ALONE: the Void Rule and the filename
convention are the USER's, not one repo's. A sweep scoped to whichever repo
happens to hold the script re-creates the exact invisibility it was built to
end —— a voided file in a sibling would age forever because no session ever
looks there. Adding a repo therefore needs no edit here.

`backup/` IS NOT EXCLUDED, and the earlier exclusion was a mistake worth
naming: it rested on `backup/README.md`'s ban on editing or deleting anything
there, which made a voided file inside it look un-actionable. That confuses
this script with a deleter. It only PRINTS, and a file the user cannot delete
is still one he should be told about —— one exists today, a `_moved_` leftover
under `backup/backup_Claude/backup_Claude_AJAP_3.0/backup_.claude/`, and hiding
it was the wrong default. If it should stay put, un-void it there; do not blind
the sweep.

STRAY-SPACE RULE IS IMPORTED, NEVER COPIED: the detection regex lives in
`cscpt/flint.py` as `_DEFECT_RE`, which owns it and documents its full
calibration (why the anchored form and not "any whitespace"). Two copies of one
rule is the drift `universal/coding.md` warns about, so this file imports it.
If flint is renamed or folded into another lint the import BREAKS LOUDLY ——
queue 3 reports itself DISABLED and names the fix, and
`cp/ccsim/sandbox/ccsim_housekeeping_regression_test.py` fails. That is the
intended behaviour: re-point the import, never paste the regex back.

DIVISION OF LABOUR with the lint that already knows that rule: flint BLOCKS a
new offender at write time and warns about one already sitting in the folder it
just wrote to. It never looks further, by design. This is the periodic full
sweep that catches what Bash, Finder, a git operation, or another repo let in.
=== CCSIM —— end ===
"""

import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
_GITHUB = os.path.dirname(_REPO)   # the parent holding every sibling repo

_VOID_PREFIX = "❌_"           # ❌_
_STALE_DAYS = 7                    # root CLAUDE.md §8.2.4
_QUEUE_DIRS = [os.path.join(_REPO, "sessions", "queued_queries")]
_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".pytest_cache"}
_EXCLUDED_REPOS = {"AJAP_repo"}    # LOAD-BEARING —— see AJAP EXCLUSION above
_QUEUE_IGNORE = {"README.md", ".DS_Store"}

# The stray-space rule is OWNED by flint.py. Imported so one source of truth
# stays one source of truth; a broken import DISABLES queue 3 loudly rather
# than tempting anyone to paste the regex back in here.
sys.path.insert(0, _HERE)
try:
    from flint import _DEFECT_RE as _STRAY_RE
    _STRAY_ERR = ""
except Exception as exc:                                       # noqa: BLE001
    _STRAY_RE = None
    _STRAY_ERR = repr(exc)
finally:
    if _HERE in sys.path:
        sys.path.remove(_HERE)


def _age_days(path):
    try:
        return (time.time() - os.path.getmtime(path)) / 86400.0
    except OSError:
        return 0.0


def scan():
    """Every in-scope file as (abs_path, rel_path_from_GitHub). ONE walk feeds
    every filename sweep —— two walks of the same tree would be pure waste."""
    out = []
    try:
        tops = sorted(os.listdir(_GITHUB))
    except OSError:
        return out
    for top in tops:
        if top in _EXCLUDED_REPOS or top.startswith("."):
            continue
        full = os.path.join(_GITHUB, top)
        if os.path.isfile(full):
            out.append((full, top))
            continue
        if not os.path.isdir(full):
            continue
        for root, dirs, files in os.walk(full):
            dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
            for name in files:
                p = os.path.join(root, name)
                out.append((p, os.path.relpath(p, _GITHUB)))
    return out


def voided(entries=None):
    """Every `❌_` file in scope, oldest first, as (rel_path, age_days)."""
    if entries is None:
        entries = scan()
    out = [(rel, _age_days(p)) for p, rel in entries
           if os.path.basename(rel).startswith(_VOID_PREFIX)]
    out.sort(key=lambda r: -r[1])
    return out


def stray_space(entries=None):
    """Filenames wedging a space before the 12-digit TS, oldest first. Returns
    None —— NOT an empty list —— when flint's rule could not be imported, so a
    disabled sweep can never read as a clean one."""
    if _STRAY_RE is None:
        return None
    if entries is None:
        entries = scan()
    out = [(rel, _age_days(p)) for p, rel in entries
           if _STRAY_RE.search(os.path.basename(rel))]
    out.sort(key=lambda r: -r[1])
    return out


def queued():
    """Queued queries awaiting a dedicated session, oldest first."""
    out = []
    for qdir in _QUEUE_DIRS:
        if not os.path.isdir(qdir):
            continue
        for name in os.listdir(qdir):
            if name in _QUEUE_IGNORE or name.startswith(_VOID_PREFIX):
                continue
            full = os.path.join(qdir, name)
            if os.path.isfile(full):
                out.append((name, _age_days(full)))
    out.sort(key=lambda r: -r[1])
    return out


def _print_aged(rows, indent="    "):
    for rel, age in rows:
        print("%s%4.0fd  %s" % (indent, age, rel))


def main(argv):
    quiet = "--quiet" in argv
    entries = scan()
    v, q, s = voided(entries), queued(), stray_space(entries)
    if quiet and not v and not q and not s and _STRAY_RE is not None:
        return 0

    print("=== HOUSEKEEPING —— waiting on the USER ===")

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
    _print_aged(q)

    if s is None:
        print("\nStray-space filenames: SWEEP DISABLED —— could not import "
              "`_DEFECT_RE` from `cscpt/flint.py` (%s)." % _STRAY_ERR)
        print("  FIX: re-point the import at whichever lint now owns that "
              "rule. Never paste the regex back in here.")
    else:
        print("\nStray-space filenames awaiting `git mv` (%d):" % len(s))
        if not s:
            print("  (none)")
        _print_aged(s)

    print("\nCC never deletes, renames or sends these —— print, then leave "
          "them to the user.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
