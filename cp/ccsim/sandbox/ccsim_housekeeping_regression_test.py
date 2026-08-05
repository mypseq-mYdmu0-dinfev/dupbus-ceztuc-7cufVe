#!/usr/bin/env python3
"""Regression suite for `cscpt/ccsim_housekeeping.py` —— CCSIM's session-start
three-queue sweep.

Pins the invariants whose failure would be expensive rather than merely wrong:

  A. SCOPE —— the sweep walks EVERY sibling under `GitHub/` and must never
     enter `AJAP_repo/`. That repo holds 790+ `❌_`-prefixed files where the
     prefix means "skipped job, archived", not "awaiting the user's delete". A
     sweep that reached it would bury the real queue and invite a mass-delete
     on the prefix alone. This is the catastrophic one, and it is the ONLY
     exclusion —— the suite pins both halves, because a scope that silently
     narrowed back to one repo re-creates the invisibility the tool exists to
     end, and a scope that widened into AJAP is the disaster.
  B. `backup/` IS INCLUDED —— it was once excluded on the grounds that its
     README bans deleting anything there. This script only PRINTS, so a file
     the user cannot delete is still one he should be told about. Pinned so
     nobody "restores" the exclusion by reflex.
  C. READ-ONLY —— the script prints; the user acts. A sweep that ever removed
     a file would be doing the user's half of the Void Rule for him.
  D. THE STRAY-SPACE RULE IS IMPORTED, NOT COPIED —— it belongs to
     `cscpt/flint.py`. The identity check below fails the moment someone pastes
     a second copy in, and equally the moment flint is renamed or folded away
     without re-pointing the import. Both are things the next editor must be
     told about loudly, not discover from a silently empty queue.

Plus the 7-day staleness flag from root `CLAUDE.md` §8.2.4, and the
`queued_queries/` ignore list.

Runs entirely on temp fixtures except where it reads the real module. Never
writes inside the repo.

RUN:
    cd "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
    python3 cp/ccsim/sandbox/ccsim_housekeeping_regression_test.py
"""

import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GITHUB = os.path.dirname(REPO)
CSCPT = os.path.join(REPO, "cscpt")
MODULE = "ccsim_housekeeping.py"

PASS = 0
FAIL = []


def check(name, cond, detail=""):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append("%s%s" % (name, (" —— %s" % detail) if detail else ""))


def _load():
    sys.path.insert(0, CSCPT)
    try:
        import ccsim_housekeeping
        return ccsim_housekeeping
    finally:
        sys.path.remove(CSCPT)


def _load_flint():
    sys.path.insert(0, CSCPT)
    try:
        import flint
        return flint
    finally:
        sys.path.remove(CSCPT)


def test_scope():
    """A. Anchored on its OWN location; GitHub-wide; AJAP_repo never entered."""
    p = _load()
    check("A/anchors on its own repo, not cwd",
          os.path.realpath(p._REPO) == os.path.realpath(REPO),
          "_REPO=%s" % p._REPO)
    check("A/walks the GitHub parent, not just this repo",
          os.path.realpath(p._GITHUB) == os.path.realpath(GITHUB),
          "_GITHUB=%s" % p._GITHUB)

    rels = [r for r, _ in p.voided()]
    leaked = [r for r in rels if r.startswith("..") or os.path.isabs(r)]
    check("A/never emits a path outside GitHub/", not leaked, leaked[:3])

    check("A/AJAP_repo is the declared exclusion",
          "AJAP_repo" in p._EXCLUDED_REPOS, sorted(p._EXCLUDED_REPOS))
    check("A/AJAP_repo is the ONLY exclusion",
          len(p._EXCLUDED_REPOS) == 1, sorted(p._EXCLUDED_REPOS))

    if os.path.isdir(os.path.join(GITHUB, "AJAP_repo")):
        # The real hazard, asserted against the real tree rather than a fixture.
        check("A/AJAP's voided files are absent from the sweep",
              not any(r.split(os.sep)[0] == "AJAP_repo" for r in rels),
              [r for r in rels if "AJAP_repo" in r][:3])
        scanned = [r for _, r in p.scan()]
        check("A/AJAP is not even walked",
              not any(r.split(os.sep)[0] == "AJAP_repo" for r in scanned),
              len([r for r in scanned if r.startswith("AJAP_repo")]))
    else:
        check("A/sibling AJAP absent, assertion vacuous but safe", True)
        check("A/sibling AJAP absent, walk assertion vacuous but safe", True)

    # The widening actually happened: paths are relative to GitHub/, so every
    # emitted row names its repo. A row bare of any repo segment would mean the
    # scope quietly collapsed back to one tree.
    check("A/rows are GitHub-relative, so each names its repo",
          all(os.sep in r for r in rels) if rels else True, rels[:3])


def test_backup_included():
    """B. `backup/` is swept —— the old exclusion was a mistake, not a guard."""
    p = _load()
    src = open(os.path.join(CSCPT, MODULE), encoding="utf-8").read()
    check("B/no _SKIP_TOP-style backup exclusion survives",
          "_SKIP_TOP" not in src and '"backup"' not in src
          and "'backup'" not in src)
    check("B/backup/ is not in the directory skip list",
          "backup" not in p._SKIP_DIRS, sorted(p._SKIP_DIRS))
    rels = [r for r, _ in p.voided()]
    real = os.path.join(REPO, "backup")
    if os.path.isdir(real):
        # Only assert surfacing if one is actually there; the point is that
        # nothing filters them out, not that one must always exist.
        on_disk = []
        for root, _dirs, files in os.walk(real):
            on_disk += [f for f in files if f.startswith(p._VOID_PREFIX)]
        if on_disk:
            check("B/a voided file under backup/ IS surfaced",
                  any(os.sep + "backup" + os.sep in r for r in rels),
                  "on disk: %s" % on_disk[:2])
        else:
            check("B/no voided file under backup/ right now, nothing to hide",
                  True)
    else:
        check("B/backup/ absent, assertion vacuous but safe", True)


def test_read_only():
    """C. No mutating filesystem call exists anywhere in the module source."""
    src = open(os.path.join(CSCPT, MODULE), encoding="utf-8").read()
    for banned in ("os.remove", "os.unlink", "os.rmdir", "shutil.rmtree",
                   "os.rename", "shutil.move", "open(", "Path("):
        if banned == "open(":
            # reading is fine; assert no write mode is ever requested
            check("C/never opens a file for writing",
                  '"w"' not in src and "'w'" not in src
                  and '"a"' not in src and "'a'" not in src)
            continue
        check("C/no %s" % banned, banned not in src)


def test_stray_rule_is_imported():
    """D. One source of truth: flint owns the regex, this script borrows it."""
    p = _load()
    src = open(os.path.join(CSCPT, MODULE), encoding="utf-8").read()
    check("D/stray sweep is live (flint import resolved)",
          p._STRAY_RE is not None, p._STRAY_ERR)
    try:
        f = _load_flint()
    except Exception as exc:                                   # noqa: BLE001
        check("D/flint importable", False, repr(exc))
        return
    check("D/it is flint's OWN compiled object, not a copy",
          p._STRAY_RE is f._DEFECT_RE)
    check("D/the regex is nowhere pasted into this file",
          "re.compile" not in src)
    check("D/a disabled sweep returns None, never an empty list",
          "return None" in src)


def test_staleness_and_ignores():
    """The §8.2.4 threshold and the queued_queries ignore list."""
    p = _load()
    check("E/staleness threshold is 7 days per root §8.2.4",
          p._STALE_DAYS == 7, p._STALE_DAYS)
    check("E/README.md is ignored in the queue", "README.md" in p._QUEUE_IGNORE)
    check("E/.DS_Store is ignored in the queue", ".DS_Store" in p._QUEUE_IGNORE)
    check("E/voided prefix is the ❌ underscore form",
          p._VOID_PREFIX == "❌_", repr(p._VOID_PREFIX))
    check("E/queued_queries stays anchored to THIS repo",
          any(os.path.realpath(d).startswith(os.path.realpath(REPO))
              for d in p._QUEUE_DIRS), p._QUEUE_DIRS)


def test_fixture_tree():
    """End-to-end over a synthetic GitHub/: ages, ordering, the stale flag, the
    cross-repo reach, the AJAP exclusion, and the stray-space catch."""
    p = _load()
    tmp = tempfile.mkdtemp(prefix="housekeeping_test_")
    try:
        main_repo = os.path.join(tmp, "main_repo")
        sibling = os.path.join(tmp, "work_repo")
        ajap = os.path.join(tmp, "AJAP_repo", "gcl", "skipped")
        qdir = os.path.join(main_repo, "sessions", "queued_queries")
        for d in (qdir, sibling, ajap,
                  os.path.join(main_repo, "backup"),
                  os.path.join(main_repo, ".git")):
            os.makedirs(d)

        old = os.path.join(main_repo, "❌_old.md")
        new = os.path.join(main_repo, "❌_new.md")
        in_backup = os.path.join(main_repo, "backup", "❌_inbackup.md")
        in_sibling = os.path.join(sibling, "❌_sibling.md")
        in_ajap = os.path.join(ajap, "❌_skipped_job.md")
        in_git = os.path.join(main_repo, ".git", "❌_internal.md")
        stray = os.path.join(main_repo, "close_ 202606142239.md")
        spaced_ok = os.path.join(main_repo, "Dev Plan _ 202603170315.txt")
        for f in (old, new, in_backup, in_sibling, in_ajap, in_git, stray,
                  spaced_ok):
            with open(f, "w", encoding="utf-8") as fh:
                fh.write("x")
        now = time.time()
        os.utime(old, (now - 40 * 86400, now - 40 * 86400))
        os.utime(new, (now - 1 * 86400, now - 1 * 86400))

        for n in ("README.md", ".DS_Store", "real_query_202607162351.md"):
            with open(os.path.join(qdir, n), "w", encoding="utf-8") as fh:
                fh.write("x")

        real_gh, real_queues = p._GITHUB, p._QUEUE_DIRS
        try:
            p._GITHUB, p._QUEUE_DIRS = tmp, [qdir]
            entries = p.scan()
            v = p.voided(entries)
            q = p.queued()
            s = p.stray_space(entries)
        finally:
            p._GITHUB, p._QUEUE_DIRS = real_gh, real_queues

        names = [r for r, _ in v]
        check("F/reaches a SIBLING repo, not just its own",
              any("sibling" in n for n in names), names)
        check("F/AJAP_repo is skipped wholesale",
              not any("AJAP" in n for n in names), names)
        check("F/backup/ is NO LONGER skipped",
              any("inbackup" in n for n in names), names)
        check("F/.git internals stay out",
              not any("internal" in n for n in names), names)
        check("F/finds exactly the four in-scope voided files",
              len(v) == 4, names)
        check("F/oldest first", names and "old" in names[0], names)
        check("F/ages are plausible", v and 39 < v[0][1] < 41, v[:1])
        check("F/stale one crosses the 7-day line",
              v and v[0][1] >= p._STALE_DAYS)
        check("F/fresh ones do not",
              all(a < p._STALE_DAYS for n, a in v if "old" not in n))

        qnames = [n for n, _ in q]
        check("F/queue ignores README.md and .DS_Store",
              qnames == ["real_query_202607162351.md"], qnames)

        snames = [r for r, _ in (s or [])]
        check("F/stray sweep is enabled", s is not None, p._STRAY_ERR)
        check("F/catches the stray-space offender",
              any("close_ 2026" in n for n in snames), snames)
        check("F/spares a name spaced all the way through",
              not any("Dev Plan" in n for n in snames), snames)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    for fn in (test_scope, test_backup_included, test_read_only,
               test_stray_rule_is_imported, test_staleness_and_ignores,
               test_fixture_tree):
        try:
            fn()
        except Exception as exc:                                # noqa: BLE001
            FAIL.append("%s raised %r" % (fn.__name__, exc))
    total = PASS + len(FAIL)
    print("ccsim-housekeeping suite: %d/%d passed" % (PASS, total))
    for f in FAIL:
        print("  FAIL: %s" % f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
