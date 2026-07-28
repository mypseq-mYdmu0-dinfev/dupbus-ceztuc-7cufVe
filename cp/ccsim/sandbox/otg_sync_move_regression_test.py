#!/usr/bin/env python3
"""Regression test —— the `.sync/sync.py` -> `cscpt/otg_sync.py` move must hold.

WHY THIS EXISTS (self-contained; no conversation or comms file explains it):

The `#sync` script was renamed and relocated:

    .sync/sync.py   ->   cscpt/otg_sync.py

Two reasons, both permanent. "sync" names no job —— the script refreshes the
ON-THE-GO index's commit-SHA permalinks, which "otg_sync" says out loud. And it
was the sole occupant of a second, near-empty script folder; every CC script now
lives in `cscpt/`, so there is one place to look and one README indexing them.

WHY A MOVED SCRIPT IS THE DANGEROUS KIND. This script COMMITS AND PUSHES to a
live public repo. Three distinct things break silently when it moves, and each
breaks WITHOUT an error:

1. THE REPO ROOT. It used to derive ROOT from the CALLER's working directory
   (`git rev-parse --show-toplevel` with no cwd). Run from inside some other
   git repo, that resolves to THAT repo and the script would stage, commit and
   push there; run from outside any repo it resolves to "", and the "does this
   path exist" guard silently degrades into a cwd-relative check. ROOT is now
   anchored to `__file__` —— repo root = the script's parent's parent —— so the
   answer no longer depends on where the caller stands. Tests below prove the
   anchor resolves correctly, and prove it from a FOREIGN working directory,
   because a test run from the repo root cannot tell the two schemes apart.

2. THE PERMISSION ALLOW-RULE. `.claude/settings.json` auto-approves one exact
   command string. A rule naming the old path stops matching, so `#sync` falls
   back to a permission prompt —— an inconvenience locally and a hang in a
   cloud session. It is checked here against the literal command `universal/
   sync.md` tells the model to run, so the two can never drift apart.

3. THE INVOCATION IN THE PROTOCOL. `universal/sync.md` is what the model reads
   before running anything; a stale command there is a guaranteed failure.

`.sync/` IS RETIRED. Nothing live may return to it. This repo never deletes, so
its residue is voided with a `❌_` prefix for the owner to remove by hand ——
test_sync_folder_holds_nothing_live keeps it that way.

WHAT IS DELIBERATELY EXEMPT:
- `sessions/`, `backup/`, `gscpt/parked/` —— historical records that were
  accurate when written; rewriting them would falsify history.
- `cscpt/otg_sync.py`'s own header, which names the old path as provenance so a
  reader of an old commit can follow the trail. That exemption is narrow and
  itself policed: test_old_path_never_appears_in_executable_code proves the dead
  path survives only inside the module docstring, never in code.

RUN:
    cd "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
    python3 cp/ccsim/sandbox/otg_sync_move_regression_test.py

Dependency-free by design (PyYAML is not installed system-wide on this Mac).
"""

import io
import os
import re
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SELF = os.path.abspath(__file__)

CSCPT = os.path.join(REPO, "cscpt")
SCRIPT_REL = "cscpt/otg_sync.py"
SCRIPT = os.path.join(REPO, SCRIPT_REL)
OLD_REL = ".sync/sync.py"
SYNC_DIR = os.path.join(REPO, ".sync")

# The one command string the protocol publishes and the permission rule must
# auto-approve. Held here verbatim so a silent edit to either side fails this
# test rather than a live `#sync` run.
COMMAND = "python3 cscpt/otg_sync.py"
ALLOW_RULE = "Bash(python3 cscpt/otg_sync.py:*)"

SKIP_DIRS = {".git", "sessions", "backup", "parked", "__pycache__", "node_modules"}
SCAN_EXT = {".md", ".py", ".sh", ".json", ".txt", ".zsh"}

DEAD_PATH_RE = re.compile(r"\.sync/sync\.py")

failures = []
checks = 0


def check(ok, label, detail=""):
    global checks
    checks += 1
    if ok:
        print(f"[PASS] {label}")
    else:
        print(f"[FAIL] {label} —— {detail}")
        failures.append(label)


def live_files():
    """Every scannable file that is live protocol/config/code, not history."""
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if os.path.splitext(name)[1] not in SCAN_EXT:
                continue
            path = os.path.join(dirpath, name)
            if os.path.abspath(path) == SELF:
                continue  # this file holds the dead names as its needles
            yield path


def read(path):
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def test_script_is_at_its_new_home():
    check(os.path.isfile(SCRIPT), f"{SCRIPT_REL} exists")
    check(not os.path.exists(os.path.join(REPO, OLD_REL)),
          f"{OLD_REL} is gone", "the old file is still on disk")


def test_no_live_file_invokes_the_old_path():
    """The runnable command is the thing that actually breaks. Zero exceptions:
    any live file telling anyone to run the old path is a defect."""
    dead_cmd = "python3 " + OLD_REL
    offenders = [os.path.relpath(p, REPO) for p in live_files()
                 if dead_cmd in read(p)]
    check(not offenders, "no live file invokes the old path",
          f"still invoking `{dead_cmd}`: {offenders}")


def test_only_the_scripts_own_header_still_names_the_old_path():
    allowed = {SCRIPT_REL}
    offenders = sorted(os.path.relpath(p, REPO) for p in live_files()
                       if DEAD_PATH_RE.search(read(p))
                       and os.path.relpath(p, REPO) not in allowed)
    check(not offenders, "old path survives only in the script's own header",
          f"stale `{OLD_REL}` reference(s): {offenders}")


def test_old_path_never_appears_in_executable_code():
    """Policing the one exemption above: provenance lives in the docstring, so
    the dead path must not appear once real statements begin."""
    text = read(SCRIPT)
    end = text.find('"""', text.find('"""') + 3)
    check(end != -1, "otg_sync.py opens with a module docstring")
    if end == -1:
        return
    code = text[end + 3:]
    check(".sync" not in code, "no `.sync` reference in otg_sync.py's code",
          "the dead folder is named outside the docstring")


def test_permission_rule_matches_the_published_command():
    settings = read(os.path.join(REPO, ".claude", "settings.json"))
    check(ALLOW_RULE in settings,
          f"settings.json auto-approves `{ALLOW_RULE}`",
          "the allow-rule does not name the current script path")
    check(ALLOW_RULE == f"Bash({COMMAND}:*)",
          "allow-rule and published command are the same string")


def test_protocol_publishes_the_new_command():
    proto = read(os.path.join(REPO, "universal", "sync.md"))
    check(COMMAND in proto, f"universal/sync.md publishes `{COMMAND}`")
    check(OLD_REL not in proto, "universal/sync.md names no old path")


def test_readme_indexes_the_script():
    readme = read(os.path.join(CSCPT, "README.md"))
    check("`otg_sync.py`" in readme, "cscpt/README.md has an otg_sync.py entry",
          "a script absent from the index is a script nobody finds")


def test_repo_root_anchor_resolves_correctly():
    sys.path.insert(0, CSCPT)
    try:
        import otg_sync
    finally:
        sys.path.pop(0)
    check(os.path.realpath(otg_sync.ROOT) == os.path.realpath(REPO),
          "otg_sync.ROOT resolves to the repo root",
          f"got {otg_sync.ROOT!r}, expected {REPO!r}")
    return otg_sync


def test_repo_root_survives_a_foreign_working_directory():
    """THE test that distinguishes the fix from the bug. Imported from `/`, a
    cwd-derived ROOT would be empty or point elsewhere; a `__file__`-derived one
    is unchanged. Run in a subprocess so the cwd change cannot leak."""
    code = (
        "import sys; sys.path.insert(0, %r); import otg_sync; print(otg_sync.ROOT)"
        % CSCPT
    )
    r = subprocess.run([sys.executable, "-c", code], cwd="/",
                       capture_output=True, text=True)
    check(r.returncode == 0, "otg_sync imports cleanly from a foreign cwd",
          r.stderr.strip() or r.stdout.strip())
    check(r.stdout.strip() == os.path.realpath(REPO),
          "ROOT is unchanged when imported from `/`",
          f"got {r.stdout.strip()!r}, expected {os.path.realpath(REPO)!r}")


def test_missing_path_guard_still_aborts(otg_sync):
    """The guard that stops a renamed-away file being re-pinned to the commit
    that DELETED it (a URL that 404s silently). Called directly —— running the
    whole script would commit and push."""
    ghost = "universal/this_file_does_not_exist_regression_probe.md"
    try:
        otg_sync.sha_of(ghost)
    except SystemExit as e:
        msg = str(e)
        check("does not exist" in msg and ghost in msg,
              "sha_of aborts on a path missing from the working tree", msg[:120])
    else:
        check(False, "sha_of aborts on a path missing from the working tree",
              "it returned instead of aborting —— a stale entry would be re-pinned")


def test_committed_path_still_resolves(otg_sync):
    """The guard must not have become a blanket refusal: a real tracked file
    still yields its last-commit SHA."""
    sha = otg_sync.sha_of("universal/sync.md")
    check(bool(re.fullmatch(r"[0-9a-f]{40}", sha)),
          "sha_of returns a 40-hex SHA for a tracked file", repr(sha))


def test_sync_folder_holds_nothing_live():
    """`.sync/` is retired. It may be gone, or hold only voided (`❌_`) residue
    plus git-ignored machine detritus —— never a live file again."""
    if not os.path.isdir(SYNC_DIR):
        check(True, ".sync/ holds nothing live (directory removed)")
        return
    tolerated = {".DS_Store", "__pycache__"}
    live = [n for n in sorted(os.listdir(SYNC_DIR))
            if n not in tolerated and not n.startswith("❌_")]
    check(not live, ".sync/ holds nothing live (voided residue only)",
          f"live entries still present: {live}")


def main():
    test_script_is_at_its_new_home()
    test_no_live_file_invokes_the_old_path()
    test_only_the_scripts_own_header_still_names_the_old_path()
    test_old_path_never_appears_in_executable_code()
    test_permission_rule_matches_the_published_command()
    test_protocol_publishes_the_new_command()
    test_readme_indexes_the_script()
    otg_sync = test_repo_root_anchor_resolves_correctly()
    test_repo_root_survives_a_foreign_working_directory()
    test_missing_path_guard_still_aborts(otg_sync)
    test_committed_path_still_resolves(otg_sync)
    test_sync_folder_holds_nothing_live()

    print(f"\n{checks - len(failures)}/{checks} checks passed.")
    if failures:
        print("FAILED: " + "; ".join(failures))
        sys.exit(1)
    print("ALL PASS")


if __name__ == "__main__":
    main()
