#!/usr/bin/env python3
"""Regression suite for `cscpt/pending.py` —— the user's outstanding-queue sweep.

Pins the three invariants whose failure would be expensive rather than merely
wrong:

  A. SCOPE —— the sweep must never leave this repo. `AJAP_repo/` holds 790+
     `❌_`-prefixed files where the prefix means "skipped job, archived", not
     "awaiting the user's delete". A widened sweep buries the real queue and
     invites a mass-delete on the prefix alone. This is the catastrophic one.
  B. `backup/` EXCLUSION —— `backup/README.md` bans deleting anything there, so
     a voided file inside it is not actionable and listing it is noise the user
     cannot clear.
  C. READ-ONLY —— the script prints; the user acts. A sweep that ever removed a
     file would be doing the user's half of the Void Rule for him.

Plus the 7-day staleness flag from root `CLAUDE.md` §8.2.4, and the
`queued_queries/` ignore list.

Runs entirely on temp fixtures except where it reads the real module. Never
writes inside the repo.
"""

import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSCPT = os.path.join(REPO, "cscpt")

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
        import pending
        return pending
    finally:
        sys.path.remove(CSCPT)


def test_scope():
    """A. The sweep is anchored on its OWN repo root, never the process cwd."""
    p = _load()
    check("A/anchors on its own repo, not cwd",
          os.path.realpath(p._REPO) == os.path.realpath(REPO),
          "_REPO=%s" % p._REPO)

    sibling = os.path.join(os.path.dirname(REPO), "AJAP_repo")
    rels = [r for r, _ in p.voided()]
    leaked = [r for r in rels if r.startswith("..") or os.path.isabs(r)]
    check("A/never emits a path outside this repo", not leaked, leaked[:3])

    if os.path.isdir(sibling):
        # The real hazard, asserted against the real tree rather than a fixture.
        check("A/sibling repo's voided files are absent from the sweep",
              not any("AJAP" in r for r in rels),
              [r for r in rels if "AJAP" in r][:3])
    else:
        check("A/sibling repo absent, scope assertion vacuous but safe", True)


def test_backup_excluded():
    """B. `backup/` is skipped wholesale —— nothing there is user-actionable."""
    p = _load()
    rels = [r for r, _ in p.voided()]
    check("B/backup/ never appears in the queue",
          not any(r.split(os.sep)[0] == "backup" for r in rels),
          [r for r in rels if r.startswith("backup")][:3])
    check("B/and the exclusion is declared, not incidental",
          "backup" in p._SKIP_TOP)


def test_read_only():
    """C. No mutating filesystem call exists anywhere in the module source."""
    src = open(os.path.join(CSCPT, "pending.py"), encoding="utf-8").read()
    for banned in ("os.remove", "os.unlink", "os.rmdir", "shutil.rmtree",
                   "os.rename", "shutil.move", "open(", "Path("):
        if banned == "open(":
            # reading is fine; assert no write mode is ever requested
            check("C/never opens a file for writing",
                  '"w"' not in src and "'w'" not in src
                  and '"a"' not in src and "'a'" not in src)
            continue
        check("C/no %s" % banned, banned not in src)


def test_staleness_and_ignores():
    """The §8.2.4 threshold and the queued_queries ignore list."""
    p = _load()
    check("D/staleness threshold is 7 days per root §8.2.4",
          p._STALE_DAYS == 7, p._STALE_DAYS)
    check("D/README.md is ignored in the queue", "README.md" in p._QUEUE_IGNORE)
    check("D/.DS_Store is ignored in the queue", ".DS_Store" in p._QUEUE_IGNORE)
    check("D/voided prefix is the ❌ underscore form",
          p._VOID_PREFIX == "❌_", repr(p._VOID_PREFIX))


def test_fixture_tree():
    """End-to-end over a synthetic tree: ages, ordering and the stale flag."""
    p = _load()
    tmp = tempfile.mkdtemp(prefix="pending_test_")
    try:
        qdir = os.path.join(tmp, "sessions", "queued_queries")
        os.makedirs(qdir)
        os.makedirs(os.path.join(tmp, "backup"))

        old = os.path.join(tmp, "❌_old.md")
        new = os.path.join(tmp, "❌_new.md")
        hidden = os.path.join(tmp, "backup", "❌_inbackup.md")
        for f in (old, new, hidden):
            with open(f, "w", encoding="utf-8") as fh:
                fh.write("x")
        now = time.time()
        os.utime(old, (now - 40 * 86400, now - 40 * 86400))
        os.utime(new, (now - 1 * 86400, now - 1 * 86400))

        for n in ("README.md", ".DS_Store", "real_query_202607162351.md"):
            with open(os.path.join(qdir, n), "w", encoding="utf-8") as fh:
                fh.write("x")

        real_repo, real_queue = p._REPO, p._QUEUE_DIR
        try:
            p._REPO, p._QUEUE_DIR = tmp, qdir
            v = p.voided()
            q = p.queued()
        finally:
            p._REPO, p._QUEUE_DIR = real_repo, real_queue

        names = [r for r, _ in v]
        check("E/finds both voided files", len(v) == 2, names)
        check("E/skips the one under backup/",
              not any("inbackup" in n for n in names), names)
        check("E/oldest first", names and "old" in names[0], names)
        check("E/ages are plausible", v and 39 < v[0][1] < 41, v[:1])
        check("E/stale one crosses the 7-day line", v and v[0][1] >= p._STALE_DAYS)
        check("E/fresh one does not", len(v) > 1 and v[1][1] < p._STALE_DAYS)

        qnames = [n for n, _ in q]
        check("E/queue ignores README.md and .DS_Store",
              qnames == ["real_query_202607162351.md"], qnames)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    for fn in (test_scope, test_backup_excluded, test_read_only,
               test_staleness_and_ignores, test_fixture_tree):
        try:
            fn()
        except Exception as exc:                                # noqa: BLE001
            FAIL.append("%s raised %r" % (fn.__name__, exc))
    total = PASS + len(FAIL)
    print("pending-queue suite: %d/%d passed" % (PASS, total))
    for f in FAIL:
        print("  FAIL: %s" % f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
