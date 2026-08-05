#!/usr/bin/env python3
"""Regression suite for the QUERY <-> RESPONSE pairing enforcement.

Root CLAUDE.md §3.5.3: a `response_` carries the TS of the `query_` it answers.
One query owes exactly ONE response —— nothing less (a new query must get its
OWN `response_[TS]`, never extra sections appended to a previous turn's file)
and nothing more (a mid-turn message stays inside the current response, §3.1.7.6.1).

THE FAILURE THIS PINS, encoded verbatim as fixture R1: a new
`ccsim_query_202608012325.md` arrived, and instead of `ccsim_response_202608012325.md`
being created, thirty sections were appended to the PREVIOUS turn's
`ccsim_response_202608011950.md`. Both files went into ONE commit
(`sessions/2026/202608/ccsim_query_202608012325.md` added,
`sessions/2026/202608/ccsim_response_202608011950.md` modified) and nothing
complained, because `.githooks/pre-commit` checked only that a response_ has a
query_ —— never the reverse. Filenames below are the real ones, per
`universal/coding.md` § Testing ("mine historical/real data for fixtures").

ONE MECHANISM NOW, and the suite says so loudly rather than quietly covering
less than its name promises:
  * `.githooks/pre-commit` reverse arm —— non-blocking, adds-only, at COMMIT
    time. It is the only automated pairing check that remains.
  * `cscpt/hlint.py` (UserPromptSubmit) carried a prompt-time twin that named
    the owed response BEFORE the turn's first write. It was PURGED: a brand-new
    `query_` has no `response_` by construction, so it fired identically on a
    compliant turn and on the breach —— no discriminating power, one fire per
    turn (measured: 5 of 29 real invocations, ~124 tokens each). Its former
    checks below are RETAINED as fixtures and INVERTED: each now pins that
    hlint is silent, so a re-add is a deliberate act with a failing suite
    behind it, never a quiet drift back.

⚠️ THE COVER THAT WAS LOST, recorded so nobody reads this suite's green as
"pairing is protected": nothing now fires before the wrong write. By the time
the pre-commit arm speaks, the appended content already exists and the repair
costs a turn. Root CLAUDE.md §3.1.7.7 states the rule in prose, which is not
enforcement (`cp/ccsim/CLAUDE.md` §8.7). The rebuild target named in
`cscpt/hlint.py`'s retirement note is `cscpt/flint.py`'s PreToolUse half.

BEFORE/AFTER PROOF (test P0): the suite synthesises the PRE-CHANGE hook by
deleting the reverse arm from the live file (everything from its banner comment
to the trailing `exit 0`) and asserts that hook is SILENT on the R1 fixture
whilst the live one fires. Deriving the baseline from the live file rather than
from `git show HEAD:` is deliberate —— a `git show` baseline stops being the
"before" version the moment the fix is committed, and the test would then prove
nothing whilst still passing. It also fails loudly if anyone deletes the arm.

Run from anywhere:  python3 cp/ccsim/sandbox/pairing_lint_regression_test.py
Temp fixtures only —— it never writes into `sessions/` and never runs a commit
in the live repo.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# Repo root = three levels up from `cp/ccsim/sandbox/` (anchored on __file__,
# never on cwd —— the suite must run from anywhere).
SANDBOX = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SANDBOX)))
HOOK = os.path.join(ROOT, ".githooks", "pre-commit")
HLINT = os.path.join(ROOT, "cscpt", "hlint.py")

# The banner that opens the reverse arm. Also the marker P0 strips on.
ARM_MARKER = "# --- REVERSE PAIRING ARM"

checks = 0
failures = []


def check(ok, label, detail=""):
    global checks
    checks += 1
    if ok:
        print("[PASS] %s" % label)
    else:
        print("[FAIL] %s —— %s" % (label, detail))
        failures.append(label)


# ---------------------------------------------------------------------------
# pre-commit harness
# ---------------------------------------------------------------------------

def _git(repo, *args, **kw):
    return subprocess.run(["git"] + list(args), cwd=repo, capture_output=True,
                          text=True, **kw)


def make_repo(hook_path):
    """A throwaway git repo wired to `hook_path` via `core.hooksPath`.

    `core.hooksPath` wants a DIRECTORY, so the hook is copied into one inside
    the temp tree —— never pointed at the live `.githooks/`, so a fixture can
    never reach into the real repo.
    """
    repo = tempfile.mkdtemp(prefix="pairing-reg-")
    hooks = os.path.join(repo, "_hooks")
    os.makedirs(hooks)
    dest = os.path.join(hooks, "pre-commit")
    shutil.copyfile(hook_path, dest)
    os.chmod(dest, 0o755)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    _git(repo, "config", "commit.gpgsign", "false")
    _git(repo, "config", "core.hooksPath", hooks)
    return repo


def write(repo, relpath, text="x\n"):
    full = os.path.join(repo, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(text)
    return relpath


def commit(repo, paths, message="t"):
    """Stage `paths` and commit. Returns (returncode, combined output)."""
    for p in paths:
        _git(repo, "add", "--", p)
    res = _git(repo, "commit", "-q", "-m", message)
    return res.returncode, (res.stdout or "") + (res.stderr or "")


def seed(repo):
    """One tracked commit so `git ls-files` and HEAD exist."""
    write(repo, "seed.txt")
    _git(repo, "add", "seed.txt")
    _git(repo, "commit", "-q", "-m", "seed")


QUERY_REMINDER = "has no sibling response"
RESPONSE_REMINDER = "has no sibling query"


# ---------------------------------------------------------------------------
# P0 —— before/after
# ---------------------------------------------------------------------------

def synthesise_pre_change_hook():
    """The live hook with the reverse arm removed —— i.e. the version that let
    the R1 commit through. Returns a temp file path, or None if the marker is
    gone (which is itself a failure, reported by the caller)."""
    text = open(HOOK, encoding="utf-8").read()
    idx = text.find(ARM_MARKER)
    if idx < 0:
        return None
    path = os.path.join(tempfile.mkdtemp(prefix="pairing-base-"), "pre-commit")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text[:idx] + "exit 0\n")
    os.chmod(path, 0o755)
    return path


def r1_fixture(repo):
    """The real failing commit: a new query_ plus an EDIT to the previous
    turn's response_, and no response_ of the query's own TS."""
    seed(repo)
    d = "sessions/2026/202608"
    write(repo, d + "/ccsim_query_202608011950.md")
    write(repo, d + "/ccsim_response_202608011950.md", "# Response\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "prior turn")
    # The breach: new query, previous response grown, no response_202608012325.
    write(repo, d + "/ccsim_response_202608011950.md",
          "# Response\n\n*Reply to `ccsim_query_202608012325.md` begins.*\n")
    write(repo, d + "/ccsim_query_202608012325.md")
    return [d + "/ccsim_query_202608012325.md",
            d + "/ccsim_response_202608011950.md"]


def test_p0_before_and_after():
    base = synthesise_pre_change_hook()
    check(base is not None,
          "P0.0 — the reverse arm's marker is present in .githooks/pre-commit",
          "marker %r not found; the arm has been removed" % ARM_MARKER)
    if base is None:
        return

    repo = make_repo(base)
    rc, out = commit(repo, r1_fixture(repo))
    check(rc == 0 and QUERY_REMINDER not in out,
          "P0.1 — PRE-CHANGE hook is SILENT on the real violating commit",
          "rc=%s out=%r" % (rc, out[:400]))

    repo = make_repo(HOOK)
    rc, out = commit(repo, r1_fixture(repo))
    check(rc == 0 and QUERY_REMINDER in out,
          "P0.2 — CURRENT hook FLAGS the real violating commit (and lets it through)",
          "rc=%s out=%r" % (rc, out[:400]))
    check("ccsim_response_202608012325.md" in out,
          "P0.3 — the reminder names the exact response that was owed",
          out[:400])


# ---------------------------------------------------------------------------
# Reverse arm —— behaviour
# ---------------------------------------------------------------------------

def test_paired_commit_is_silent():
    repo = make_repo(HOOK)
    seed(repo)
    d = "sessions/2026/202608"
    paths = [write(repo, d + "/ccsim_query_202608012325.md"),
             write(repo, d + "/ccsim_response_202608012325.md")]
    rc, out = commit(repo, paths)
    check(rc == 0 and QUERY_REMINDER not in out and RESPONSE_REMINDER not in out,
          "R2 — a properly paired query+response commit is silent in BOTH arms",
          "rc=%s out=%r" % (rc, out[:400]))


def test_response_already_tracked():
    repo = make_repo(HOOK)
    seed(repo)
    d = "sessions/2026/202608"
    # m2.md mandates an interim commit of the response_ ALONE; the query_ then
    # lands at turn end. The reverse arm must see the tracked response.
    commit(repo, [write(repo, d + "/ccsim_response_202608012325.md")], "interim")
    rc, out = commit(repo, [write(repo, d + "/ccsim_query_202608012325.md")])
    check(rc == 0 and QUERY_REMINDER not in out,
          "R3 — query_ added later, response_ already tracked -> silent",
          "rc=%s out=%r" % (rc, out[:400]))


def test_queued_queries_exempt():
    repo = make_repo(HOOK)
    seed(repo)
    paths = [write(repo, "sessions/queued_queries/ajap_migr_query_202607242027.md"),
             write(repo, "sessions/queued_queries/citi_query_202607162351.md")]
    rc, out = commit(repo, paths)
    check(rc == 0 and QUERY_REMINDER not in out,
          "R4 — sessions/queued_queries/ is exempt (awaiting a future session)",
          "rc=%s out=%r" % (rc, out[:400]))


def test_blank_templates_exempt():
    repo = make_repo(HOOK)
    seed(repo)
    paths = [write(repo, "sessions/query_.md", ""),
             write(repo, "sessions/ccsim_query_.md", ""),
             write(repo, "sessions/career_query_.md", ""),
             write(repo, "sessions/dissertation_query_.md", "")]
    rc, out = commit(repo, paths)
    check(rc == 0 and QUERY_REMINDER not in out,
          "R5 — blank `*_query_.md` templates (no TS) never match",
          "rc=%s out=%r" % (rc, out[:400]))


def test_cp_prefix_is_respected():
    repo = make_repo(HOOK)
    seed(repo)
    d = "sessions/2026/202607"
    # A bare `response_` must NOT satisfy a `career_query_`: root CLAUDE.md
    # §3.3.6 prefixes every comms file of a CP chat.
    paths = [write(repo, d + "/career_query_202607181948.md"),
             write(repo, d + "/response_202607181948.md")]
    rc, out = commit(repo, paths)
    check(rc == 0 and "career_response_202607181948.md" in out,
          "R6 — a CP query needs its CP-prefixed response, not a bare one",
          "rc=%s out=%r" % (rc, out[:400]))


def test_modify_does_not_refire():
    repo = make_repo(HOOK)
    seed(repo)
    d = "sessions/2026/202607"
    q = d + "/ccsim_query_202607301747.md"
    commit(repo, [write(repo, q)], "add orphan")           # fires once
    rc, out = commit(repo, [write(repo, q, "edited\n")])   # must not re-fire
    check(rc == 0 and QUERY_REMINDER not in out,
          "R7 — a later MODIFY of an unpaired query does not re-fire (adds only)",
          "rc=%s out=%r" % (rc, out[:400]))


def test_space_in_path_survives():
    repo = make_repo(HOOK)
    seed(repo)
    # git does not quote a path merely because it contains a space; the loop
    # must read line-wise or the filename is torn into fragments.
    d = "sessions/2026/dir with space"
    rc, out = commit(repo, [write(repo, d + "/ccsim_query_202608012325.md")])
    check(rc == 0 and "ccsim_response_202608012325.md" in out
          and "dir with space" not in out.split("\n")[0],
          "R8 — a path containing spaces is handled, not word-split",
          "rc=%s out=%r" % (rc, out[:400]))


def test_non_comms_files_ignored():
    repo = make_repo(HOOK)
    seed(repo)
    paths = [write(repo, "cscpt/hlint.py", "# x\n"),
             write(repo, "universal/coding.md", "# x\n"),
             write(repo, "sessions/2026/202608/ccsim_slog_202608012011.md")]
    rc, out = commit(repo, paths)
    check(rc == 0 and QUERY_REMINDER not in out,
          "R9 — non-query files (code, pcmd, slog_) are never flagged",
          "rc=%s out=%r" % (rc, out[:400]))


def test_voided_query_exempt():
    repo = make_repo(HOOK)
    seed(repo)
    d = "sessions/2026/202607"
    # Root CLAUDE.md §8.2: a `❌_` file awaits the user's manual delete, so it
    # owes no response. NOTE the standing rule this obeys: the check is that a
    # voided name is IGNORED, never that a voided file exists anywhere real.
    rc, out = commit(repo, [write(repo, d + "/❌_ccsim_query_202607282109.md")])
    check(rc == 0 and QUERY_REMINDER not in out,
          "R13 — a voided `❌_` query is exempt (awaiting manual deletion)",
          "rc=%s out=%r" % (rc, out[:400]))


def test_forward_arm_intact():
    repo = make_repo(HOOK)
    seed(repo)
    d = "sessions/2026/202608"
    rc, out = commit(repo, [write(repo, d + "/response_202608012325.md")])
    check(rc == 0 and RESPONSE_REMINDER in out,
          "R10 — the FORWARD arm still fires on an orphan response_",
          "rc=%s out=%r" % (rc, out[:400]))


def test_stray_space_block_intact():
    repo = make_repo(HOOK)
    seed(repo)
    d = "sessions/2026/202608"
    rc, out = commit(repo, [write(repo, d + "/ccsim_query_ 202608012325.md")])
    check(rc != 0 and "BLOCKED" in out,
          "R11 — the stray-space ADD gate still BLOCKS (severity untouched)",
          "rc=%s out=%r" % (rc, out[:400]))


def test_sync_allowlist_intact():
    repo = make_repo(HOOK)
    seed(repo)
    gitdir = _git(repo, "rev-parse", "--git-dir").stdout.strip()
    marker = os.path.join(repo, gitdir, "SYNC_ACTIVE")
    with open(marker, "w", encoding="utf-8") as fh:
        fh.write("allowed.md\n")
    q = write(repo, "sessions/2026/202608/ccsim_query_202608012325.md")
    rc, out = commit(repo, [q])
    check(rc != 0 and "not in the allowlist" in out,
          "R12 — the #sync allowlist gate still short-circuits everything else",
          "rc=%s out=%r" % (rc, out[:400]))


# ---------------------------------------------------------------------------
# hlint arm —— PURGED. Every check below is the INVERSE of what it once was:
# the same fixtures, now pinning silence. Kept rather than deleted because a
# deleted test is a coverage claim nobody can audit, and because these are the
# exact inputs that would fire again the moment someone re-adds the check to
# the wrong file (see the module docstring for where it belongs instead).
# ---------------------------------------------------------------------------

def hlint(prompt):
    """Run the real hook with a real UserPromptSubmit payload.

    `HLINT_LOG` is redirected to /dev/null so this suite never appends to the
    live `cscpt/.hlint.log`. That log is diagnostic evidence —— it exists so
    "the hook never fired" stays distinguishable from "it fired and found
    nothing" —— and a test run injecting dozens of synthetic `fired` lines
    would corrupt exactly the record someone later reaches for."""
    env = dict(os.environ)
    env["HLINT_LOG"] = os.devnull
    res = subprocess.run([sys.executable, HLINT],
                         input=json.dumps({"prompt": prompt}),
                         capture_output=True, text=True, env=env)
    if not res.stdout.strip():
        return res.returncode, ""
    try:
        ctx = json.loads(res.stdout)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        ctx = res.stdout
    return res.returncode, ctx


def comms_dir(names):
    """A temp comms folder holding `names`. `tempfile` is used rather than the
    scratch tree because `hlint._MD_TOKEN_RE` stops at whitespace, so a path
    containing a space cannot be named in a prompt at all —— a pre-existing
    limit of that regex, unrelated to this check, but fatal to a fixture."""
    d = tempfile.mkdtemp(prefix="hlint-pair-")
    for n in names:
        with open(os.path.join(d, n), "w", encoding="utf-8") as fh:
            fh.write("x\n")
    return d


PAIR_TEXT = "Query/response pairing"


def test_hlint_no_longer_pairs_on_the_real_scenario():
    """THE PURGE, pinned on the exact fixture that once justified the check ——
    the real R1 filenames. If this ever fires again, the reminder is back in the
    wrong file and its precision problem is back with it."""
    d = comms_dir(["ccsim_query_202608011950.md",
                   "ccsim_response_202608011950.md",
                   "ccsim_query_202608012325.md"])
    rc, ctx = hlint(os.path.join(d, "ccsim_query_202608012325.md"))
    check(rc == 0 and ctx == "",
          "H-P1 — hlint is SILENT on the real failing query (pairing purged)",
          "rc=%s ctx=%r" % (rc, ctx[:300]))
    # Source-level, because a behavioural silence could also mean a broken
    # lookup. This proves the machinery is GONE, not merely quiet —— and with
    # it, that `.githooks/pre-commit` is now the only automated pairing check.
    src = open(HLINT, encoding="utf-8").read()
    dead = [n for n in ("_pairing_reminders", "_PAIR_HEADER",
                        "_MAX_PAIR_REMINDERS", "_newest_query_ts",
                        "_QUERY_FILE_RE", 'has no `%s` yet')
            if n in src]
    check(not dead,
          "H-P2 — the pairing machinery is REMOVED from hlint.py, not just idle",
          "still present: %s" % ", ".join(dead))
    check(rc == 0, "H-P3 — advisory: exit 0 always (never blocks a prompt)", str(rc))


def test_hlint_silent_when_paired():
    d = comms_dir(["ccsim_query_202608012325.md",
                   "ccsim_response_202608012325.md"])
    rc, ctx = hlint(os.path.join(d, "ccsim_query_202608012325.md"))
    check(rc == 0 and ctx == "",
          "H-P4 — a paired query+response prompt stays silent",
          "ctx=%r" % ctx[:300])


def test_hlint_ignores_older_query():
    # The four non-paired queries recorded in `ccsim_close_202607291954.md`
    # §6.19 are legitimate. Referring to one must not fire —— and now nothing
    # can, from either direction.
    d = comms_dir(["ccsim_query_202607301737.md",
                   "ccsim_response_202607301737.md",
                   "ccsim_query_202607301742.md",
                   "ccsim_query_202607301747.md"])
    rc, ctx = hlint(os.path.join(d, "ccsim_query_202607301742.md"))
    check(rc == 0 and ctx == "",
          "H-P5 — an OLDER unpaired query merely referred to is silent",
          "ctx=%r" % ctx[:300])


def test_hlint_backticked_is_discussion():
    d = comms_dir(["ccsim_query_202608012325.md"])
    rc, ctx = hlint("what was in `%s` again?"
                    % os.path.join(d, "ccsim_query_202608012325.md"))
    check(rc == 0 and ctx == "",
          "H-P6 — a backticked comms filename produces nothing",
          "ctx=%r" % ctx[:300])


def test_hlint_cp_prefix():
    """The CP-prefix rule (root CLAUDE.md §3.3.6) is NOT gone —— it moved to the
    commit-time arm alone, which R6 above pins. Here it must be silent."""
    d = comms_dir(["career_query_202607181948.md", "response_202607181948.md"])
    rc, ctx = hlint(os.path.join(d, "career_query_202607181948.md"))
    check(rc == 0 and ctx == "",
          "H-P7 — a CP query with only a bare response is silent (R6 owns it now)",
          "ctx=%r" % ctx[:300])


def test_hlint_templates_and_missing_files():
    d = comms_dir(["ccsim_query_.md"])
    rc, ctx = hlint(os.path.join(d, "ccsim_query_.md"))
    check(rc == 0 and ctx == "",
          "H-P8 — a blank `*_query_.md` template (no TS) never fires",
          "ctx=%r" % ctx[:300])
    rc, ctx = hlint(os.path.join(d, "ccsim_query_209812312359.md"))
    check(rc == 0 and ctx == "",
          "H-P9 — a query filename that resolves to nothing never fires",
          "ctx=%r" % ctx[:300])


def test_hlint_triggers_unaffected():
    """The whole point of the purge: hlint's remit is `#triggers`, and the
    purge must not have cost that. The second check is the discriminating one
    —— a prompt carrying BOTH a trigger and a query filename must report the
    trigger and nothing else."""
    rc, ctx = hlint("#close")
    check(rc == 0 and "universal/close.md" in ctx,
          "H-P10 — the `#trigger` check survives the purge intact",
          "ctx=%r" % ctx[:300])
    d = comms_dir(["ccsim_query_202608012325.md"])
    rc, ctx = hlint("#close " + os.path.join(d, "ccsim_query_202608012325.md"))
    check(rc == 0 and "universal/close.md" in ctx
          and PAIR_TEXT not in ctx
          and "ccsim_response_202608012325.md" not in ctx,
          "H-P11 — trigger + query filename in one prompt reports the TRIGGER ONLY",
          "ctx=%r" % ctx[:400])


def test_probe_file_is_retired():
    """The standing liveness probe existed ONLY for the purged arm. It is kept
    (sandbox scratch, harmless) but must no longer read as live wiring evidence
    —— a probe that documents a check which does not exist is worse than no
    probe, because `hook_guide.md` §7.3's liveness table is where someone goes
    when they suspect the hooks are dead."""
    probe = "ccsim_query_209912312359.md"
    path = os.path.join(SANDBOX, probe)
    check(os.path.isfile(path),
          "H-P13 — the retired probe file is still present in cp/ccsim/sandbox/",
          "missing %s" % probe)
    text = open(path, encoding="utf-8").read() if os.path.isfile(path) else ""
    check("RETIRED" in text,
          "H-P14 — the probe file DECLARES itself retired, not live",
          "no RETIRED marker; it still reads as a working liveness probe")
    rc, ctx = hlint(probe)
    check(rc == 0 and ctx == "",
          "H-P15 — naming the probe against the LIVE tree now produces nothing",
          "rc=%s ctx=%r" % (rc, ctx[:300]))


def test_hlint_fail_safe():
    env = dict(os.environ)
    env["HLINT_LOG"] = os.devnull   # never pollute the live diagnostic log
    for payload in ('', 'not json', '[]', '{}', '{"prompt": null}',
                    '{"prompt": ""}', '{"prompt": 42}'):
        res = subprocess.run([sys.executable, HLINT], input=payload,
                             capture_output=True, text=True, env=env)
        check(res.returncode == 0 and not res.stdout.strip(),
              "H-P12 — degenerate payload %r: exit 0 and silent" % payload[:20],
              "rc=%s out=%r" % (res.returncode, res.stdout[:200]))


def main():
    for fn in (test_p0_before_and_after,
               test_paired_commit_is_silent,
               test_response_already_tracked,
               test_queued_queries_exempt,
               test_blank_templates_exempt,
               test_cp_prefix_is_respected,
               test_modify_does_not_refire,
               test_space_in_path_survives,
               test_non_comms_files_ignored,
               test_voided_query_exempt,
               test_forward_arm_intact,
               test_stray_space_block_intact,
               test_sync_allowlist_intact,
               test_hlint_no_longer_pairs_on_the_real_scenario,
               test_hlint_silent_when_paired,
               test_hlint_ignores_older_query,
               test_hlint_backticked_is_discussion,
               test_hlint_cp_prefix,
               test_hlint_templates_and_missing_files,
               test_hlint_triggers_unaffected,
               test_probe_file_is_retired,
               test_hlint_fail_safe):
        fn()
    print()
    if failures:
        print("%d/%d passed —— FAILURES: %s"
              % (checks - len(failures), checks, ", ".join(failures)))
        return 1
    # Deliberately NOT "pairing intact" —— it is not. Green here means the
    # commit-time arm works and the purged prompt-time arm has stayed purged.
    # Nothing in this suite covers the moment of the WRITE (module docstring).
    print("%d/%d passed —— commit-time arm live; prompt-time arm purged, "
          "no pre-write cover." % (checks, checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
