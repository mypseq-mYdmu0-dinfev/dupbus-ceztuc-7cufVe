#!/usr/bin/env python3
"""Regression test for cscpt/plint.py —— DELIVERABLE marker list (P), the
README-first read reminder (R), and its ANCESTOR WALK extension (A).

WHY the README cases exist (R1-R14): the standing instruction "on accessing any
folder, read its README FIRST" was already written down in prose and was still
skipped —— a file inside a README-bearing folder was read and acted on, and the
folder's documented procedure was missed. Prose that is not noticed cannot be
repaired with more prose, so plint gained a read-time rule that names the
README at the moment of the read. Its ONE load-bearing property is that it
fires at most ONCE PER README PER SESSION: reads are the most frequent tool
call there is, so a per-read reminder would be tuned out inside a single
session and would take the other two rules' credibility with it. R2 pins that
guard, R6 pins that a new session re-arms it, and the rest pin the silence
cases (the README itself, an already-read README, no README, project roots,
vendor folders) plus the tool-name split that keeps a bare Read from tripping
the write rules (R11). Every R case runs against fixture folders under a
private state dir (`PLINT_STATE_DIR`), so the test never reads or pollutes the
real ledger and leaves nothing behind.

WHY the ANCESTOR cases exist (A1-A8, root CLAUDE.md §8.5.1): the R-rule above
checked only the read target's OWN directory, and that narrower rule was
itself skipped on exactly this account —— a file was read several levels
under a folder whose own `README.md` governs the whole tree (a generic
`temp/` folder, several levels above one dated run's specific output
sub-folder), and because the rule never looked past the immediate directory,
that governing README was never surfaced. The fix walks from the target's
directory up through EVERY ancestor to the repo root. A1/A3 pin that an
ancestor README fires and re-arms exactly like the immediate-folder case; A2
pins the same once-per-README guard across a DIFFERENT folder under an
already-claimed ancestor; A4 pins that reading the ancestor README itself
still claims it; A5 pins total silence with no README anywhere in the chain
(bounded by `_MAX_ANCESTORS` so the climb cannot run away up the real
filesystem); A6 pins that the immediate folder's own README and a different
ancestor's README are independent and both fire, nearest first, in ONE call;
A7 pins the load-bearing boundary —— the walk STOPS at the first ancestor
that is itself a project root (`.git`), so a README ABOVE that boundary,
belonging to something else entirely, is never reached; A8 pins
`_MAX_README_LINES_PER_CALL` bounding one call's line count even when more
ancestor READMEs exist than the cap.

WHY the P cases exist (coding.md: "pin EVERY fixed bug w/ a regression test
encoding the exact failing scenario"): plint's DELIVERABLE rule reminds the
writer to read `universal/writing.md` when the content being written looks
like a letter. It detected that by matching greeting/sign-off markers, and one
of those markers was a bare `yours`. Word boundaries stop `yourself` matching,
but nothing can stop `yours` itself —— it is an everyday English possessive
("the choice is yours", "yours may differ") that occurs constantly in ordinary
prose and in this repo's own protocol files. The rule therefore fired on writes
that were in no sense deliverables, and a heuristic that cries wolf is worse
than no heuristic (plint's own design contract: a false positive must stay
rare, because its whole cost model assumes the reader still reads the line).

The fix replaced that single marker with exactly the two real letter sign-offs
built on the word —— "yours sincerely" and "yours faithfully" —— keeping every
genuine hit whilst dropping the noise. These cases pin BOTH directions: the two
phrases must still fire (P1-P2, including across a line break, since the marker
list matches inner spaces as `\\s+`), and the generic forms must not (P3-P5).
P6-P7 confirm the untouched markers and the word-boundary guard still behave,
so a future edit cannot quietly gut the rest of the list.

Self-contained: every fixture is synthesised inline (no repo files touched,
nothing to void afterwards) and the real plint.py is driven end-to-end through
its actual stdin/stdout hook contract, not by importing its internals —— a
rule that only works when called directly is not wired. Run directly:

    python3 "cp/ccsim/sandbox/plint_regression_test.py"

Exits 0 if every case matches its expected verdict, 1 otherwise (with a
per-case PASS/FAIL report on stdout, and the raw stdout/stderr on any FAIL so
a break is immediately diagnosable without re-running by hand).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", ".."))
PLINT = os.path.join(REPO_ROOT, "cscpt", "plint.py")

# The DELIVERABLE rule is identified by a stable phrase from its own message,
# so a hit from the CODE rule (which fires on any .py/.sh/pcmd target) can
# never be mistaken for one. Both rules can fire on the same call.
_DELIVERABLE_SIG = "greeting/sign-off marker"

# A path the CODE rule ignores (not a script, not a pcmd, not under
# `universal/` or `cp/<project>/`), so each case isolates the DELIVERABLE rule.
NEUTRAL_TARGET = os.path.join(REPO_ROOT, "temp", "plint_regression_fixture.txt")


def _run(content, file_path=NEUTRAL_TARGET):
    payload = {
        "session_id": "regression-test",
        "transcript_path": "/dev/null",
        "cwd": REPO_ROOT,
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": file_path, "content": content},
    }
    return subprocess.run(
        ["python3", PLINT], input=json.dumps(payload),
        capture_output=True, text=True, timeout=30,
    )


def _fired(r):
    """(deliverable_rule_fired, echoed_marker_or_empty) for a completed run."""
    out = r.stdout.strip()
    if not out:
        return False, ""
    try:
        ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        # Unparseable output counts as fired, so malformed JSON can never
        # masquerade as a clean silent pass.
        return True, ""
    for line in ctx.splitlines():
        if _DELIVERABLE_SIG in line:
            marker = line.split('("', 1)[-1].split('")', 1)[0]
            return True, marker
    return False, ""


def _check(label, content, expect_fire, expect_marker=None):
    r = _run(content)
    fired, marker = _fired(r)
    ok = (fired == expect_fire)
    if ok and expect_marker is not None:
        ok = (marker.lower() == expect_marker.lower())
    status = "PASS" if ok else "FAIL"
    detail = f", marker={marker!r}" if fired else ""
    print(f"[{status}] {label}: expected {'FIRE' if expect_fire else 'silent'}"
          f"{f' ({expect_marker!r})' if expect_marker else ''}, got "
          f"{'FIRE' if fired else 'silent'}{detail} (exit={r.returncode})")
    if not ok:
        print(f"        stdout={r.stdout!r}")
        print(f"        stderr={r.stderr!r}")
    return ok


# --- README rule (R cases) --------------------------------------------------
# Each rule is identified by a stable phrase from its own message, so the R
# cases can tell WHICH rule fired rather than merely that something did.
_README_SIG = "folder that has a `README.md`"
_CODE_SIG = "is a script/pcmd"


def _run_payload(payload):
    """Drive plint end-to-end through its real stdin/stdout hook contract.
    `payload` may be a str (deliberately malformed) or a dict."""
    body = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        ["python3", PLINT], input=body,
        capture_output=True, text=True, timeout=30,
    )


def _read_payload(path, session_id="R-session-1"):
    """A realistic PreToolUse payload for the Read tool (hook_guide § Verified
    Payload Shapes: `session_id`, `transcript_path`, `cwd`, `tool_name`,
    `tool_input`). `session_id` is what the once-per-session guard keys on."""
    return {
        "session_id": session_id,
        "transcript_path": "/dev/null",
        "cwd": REPO_ROOT,
        "hook_event_name": "PreToolUse",
        "tool_name": "Read",
        "tool_input": {"file_path": path},
    }


def _context(r):
    """The additionalContext block, or "" when the hook stayed silent."""
    out = r.stdout.strip()
    if not out:
        return ""
    try:
        return json.loads(out)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        # Unparseable output counts as output, so malformed JSON can never
        # masquerade as a clean silent pass.
        return out


def _check_rule(label, payload, sig, expect_fire, expect_path=None):
    """Assert whether the rule identified by `sig` fired, and (optionally) that
    it named `expect_path`. Exit 0 is checked on EVERY case —— this hook may
    never gate a tool call, whatever else it decides."""
    r = _run_payload(payload)
    ctx = _context(r)
    hits = [l for l in ctx.splitlines() if sig in l]
    fired = bool(hits)
    ok = (fired == expect_fire) and r.returncode == 0
    if ok and expect_path is not None:
        ok = expect_path in hits[0]
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label}: expected {'FIRE' if expect_fire else 'silent'}, "
          f"got {'FIRE' if fired else 'silent'} (exit={r.returncode})")
    if not ok:
        print(f"        stdout={r.stdout!r}")
        print(f"        stderr={r.stderr!r}")
    return ok


def _cap():
    """plint's live `_MAX_DIRS_PER_SESSION`, read from the source rather than
    copied. A hard-coded number here would keep "passing" while testing
    nothing the day somebody moves the cap. Parsed textually (not imported) so
    this test keeps driving plint ONLY through its real hook contract."""
    src = open(PLINT, encoding="utf-8").read()
    m = re.search(r"^_MAX_DIRS_PER_SESSION\s*=\s*(\d+)", src, re.M)
    if not m:
        raise SystemExit("plint._MAX_DIRS_PER_SESSION not found —— cap renamed?")
    return int(m.group(1))


def _read_int_const(name):
    """Any other integer module-level constant from plint's own source, same
    reasoning as `_cap()` above —— generalised so the ANCESTOR WALK cases
    (A8) can pin `_MAX_README_LINES_PER_CALL` without copying its value."""
    src = open(PLINT, encoding="utf-8").read()
    m = re.search(r"^%s\s*=\s*(\d+)" % re.escape(name), src, re.M)
    if not m:
        raise SystemExit("plint.%s not found —— renamed?" % name)
    return int(m.group(1))


def _report(label, ok, r, results):
    """Shared PASS/FAIL printer for the ancestor cases below, whose
    assertions inspect MULTIPLE reminder lines at once (unlike `_check_rule`,
    which pins a single rule's fire/silent verdict)."""
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label}")
    if not ok:
        print(f"        exit={r.returncode}")
        print(f"        stdout={r.stdout!r}")
        print(f"        stderr={r.stderr!r}")
    results.append(ok)
    return ok


def _mkfile(path, body="placeholder\n"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    return path


def readme_cases(root):
    """R1-R13. Fixtures are synthesised under `root` (a private temp dir) so no
    repo file is touched and the real claim ledger is never involved."""
    results = []

    alpha = os.path.join(root, "alpha")          # ordinary folder + README
    beta = os.path.join(root, "beta")            # a second one
    delta = os.path.join(root, "delta")          # README read first
    gamma = os.path.join(root, "gamma")          # no README at all
    proj = os.path.join(root, "projroot")        # a project ROOT (has .git)
    vend = os.path.join(root, "pkg", "node_modules", "left-pad")
    eps = os.path.join(root, "epsilon")          # for the no-session case
    zeta = os.path.join(root, "zeta")            # for the per-session cap
    eta = os.path.join(root, "eta")              # ditto

    for d in (alpha, beta, delta, proj, vend, eps, zeta, eta):
        _mkfile(os.path.join(d, "README.md"), "# Folder procedure\n")
    for d in (alpha, beta, delta, gamma, proj, vend, eps, zeta, eta):
        _mkfile(os.path.join(d, "note.md"))
    _mkfile(os.path.join(gamma, "script.py"), "print('x')\n")
    _mkfile(os.path.join(alpha, "other.md"))
    os.makedirs(os.path.join(proj, ".git"), exist_ok=True)

    def readme_at(d):
        return os.path.join(os.path.realpath(d), "README.md")

    # R1: the core case —— a read from a folder that has a README.
    results.append(_check_rule(
        "R1 — read in a README-bearing folder fires, naming that README",
        _read_payload(os.path.join(alpha, "note.md")),
        _README_SIG, True, readme_at(alpha)))

    # R2: THE load-bearing guard. A second read in the SAME folder in the SAME
    # session must be silent —— a per-read reminder would be tuned out at once.
    results.append(_check_rule(
        "R2 — second read in the SAME folder, same session, is SILENT",
        _read_payload(os.path.join(alpha, "other.md")),
        _README_SIG, False))

    # R3: the guard is per FOLDER, not per session —— a different README-bearing
    # folder in the same session still gets its one reminder.
    results.append(_check_rule(
        "R3 — a DIFFERENT README-bearing folder still fires in that session",
        _read_payload(os.path.join(beta, "note.md")),
        _README_SIG, True, readme_at(beta)))

    # R4/R5: reading the README itself is the behaviour the rule wants, so it
    # is silent AND claims the folder —— no redundant reminder afterwards.
    results.append(_check_rule(
        "R4 — reading the README ITSELF is silent",
        _read_payload(os.path.join(delta, "README.md")),
        _README_SIG, False))
    results.append(_check_rule(
        "R5 — a sibling read AFTER that README was read stays silent",
        _read_payload(os.path.join(delta, "note.md")),
        _README_SIG, False))

    # R6: no README, nothing to remind about.
    results.append(_check_rule(
        "R6 — folder with no README is silent",
        _read_payload(os.path.join(gamma, "note.md")),
        _README_SIG, False))

    # R7: a NEW session re-arms the reminder for an already-claimed folder ——
    # the guard is per session, not permanent.
    results.append(_check_rule(
        "R7 — a new session_id re-arms the reminder for the same folder",
        _read_payload(os.path.join(alpha, "note.md"), "R-session-2"),
        _README_SIG, True, readme_at(alpha)))

    # R8/R9: noise exclusions. A project root's README is a front page, not a
    # folder procedure; a vendored README documents somebody else's package.
    results.append(_check_rule(
        "R8 — a project ROOT (folder containing .git) is silent",
        _read_payload(os.path.join(proj, "note.md")),
        _README_SIG, False))
    results.append(_check_rule(
        "R9 — a vendored folder (node_modules/...) is silent",
        _read_payload(os.path.join(vend, "note.md")),
        _README_SIG, False))

    # R10: the tool-name split. Widening the matcher to Read must NOT make the
    # CODE rule fire on merely LOOKING at a script (it keys off file_path
    # alone, so without this split every read of a .py or pcmd would nag).
    results.append(_check_rule(
        "R10 — CODE rule does NOT fire on a bare Read of a .py",
        _read_payload(os.path.join(gamma, "script.py")),
        _CODE_SIG, False))

    # R11: ...and the write rules still work, so the split did not gut them.
    results.append(_check_rule(
        "R11 — CODE rule still fires on a Write of a .py",
        {"session_id": "R-session-1", "cwd": REPO_ROOT,
         "hook_event_name": "PreToolUse", "tool_name": "Write",
         "tool_input": {"file_path": os.path.join(gamma, "script.py"),
                        "content": "print('x')\n"}},
        _CODE_SIG, True))

    # R12: without a session_id the once-per-session contract cannot be
    # honoured, so the rule declines to fire rather than fire unbounded.
    results.append(_check_rule(
        "R12 — a Read payload with no session_id is silent",
        {"cwd": REPO_ROOT, "hook_event_name": "PreToolUse",
         "tool_name": "Read",
         "tool_input": {"file_path": os.path.join(eps, "note.md")}},
        _README_SIG, False))

    # R13: the ledger is SELF-LIMITING. Past `_MAX_DIRS_PER_SESSION` markers a
    # session stops claiming folders and the rule simply goes quiet, so no
    # session can grow the state without bound. Run against its own state root
    # so the padding cannot disturb the cases above. The cap is imported
    # (the one place this test looks inside plint) rather than hard-coded ——
    # a hard-coded 200 would silently start testing nothing if the cap moved.
    cap_state = os.path.join(root, "cap_state")
    previous = os.environ.get("PLINT_STATE_DIR")
    os.environ["PLINT_STATE_DIR"] = cap_state
    try:
        results.append(_check_rule(
            "R13a — fresh session on a fresh ledger fires as normal",
            _read_payload(os.path.join(zeta, "note.md"), "R-cap"),
            _README_SIG, True))
        sess_dirs = [os.path.join(cap_state, n) for n in os.listdir(cap_state)]
        for i in range(_cap() + 5):
            open(os.path.join(sess_dirs[0], "pad%04d" % i), "w").close()
        results.append(_check_rule(
            "R13b — past the per-session cap the rule goes quiet",
            _read_payload(os.path.join(eta, "note.md"), "R-cap"),
            _README_SIG, False))
    finally:
        if previous is None:
            os.environ.pop("PLINT_STATE_DIR", None)
        else:
            os.environ["PLINT_STATE_DIR"] = previous

    # R14: malformed payloads —— exit 0, no output, whatever the shape.
    for i, bad in enumerate((
            "{not json at all",
            json.dumps({"tool_name": "Read", "tool_input": "not-a-dict"}),
            json.dumps({"tool_name": "Read", "session_id": "R-session-1",
                        "tool_input": {}}),
            json.dumps([1, 2, 3]),
            "")):
        r = _run_payload(bad)
        ok = (r.returncode == 0 and not r.stdout.strip())
        print(f"[{'PASS' if ok else 'FAIL'}] R14.{i + 1} — malformed payload: "
              f"exit 0 and silent (exit={r.returncode})")
        if not ok:
            print(f"        stdout={r.stdout!r}\n        stderr={r.stderr!r}")
        results.append(ok)

    return results


def ancestor_readme_cases(root):
    """A1-A8. Pins the ANCESTOR WALK extension (root CLAUDE.md §8.5.1): the
    README-first reminder used to check ONLY the read target's own directory,
    so a file read several levels under a folder whose OWN `README.md`
    governs the whole tree (e.g. a generic `temp/` folder) never got that
    reminder —— exactly the real failure the extension fixes. These cases
    walk from the target's directory up through every ancestor to the repo
    root: an ancestor README fires from ANY depth, several independent
    ancestor READMEs each get their own slot, the walk stops at the first
    ancestor that is itself a project root (`.git`), and both new bounds
    (`_MAX_README_LINES_PER_CALL`) hold. Fixtures live under `root` (the same
    private temp dir `readme_cases` uses), so no repo file is touched and the
    real ledger is never involved.
    """
    results = []

    def readme_at(d):
        return os.path.join(os.path.realpath(d), "README.md")

    def sig_lines(ctx):
        return [l for l in ctx.splitlines() if _README_SIG in l]

    # A1: the core case —— a README TWO LEVELS above the read target fires,
    # naming that ancestor's README (the target's own directory has none).
    outer = os.path.join(root, "anc_outer")
    mid = os.path.join(outer, "mid")
    deep = os.path.join(mid, "deep")
    _mkfile(readme_at(outer), "# Tree-wide procedure\n")
    _mkfile(os.path.join(deep, "note.md"))
    r = _run_payload(_read_payload(os.path.join(deep, "note.md"), "A-session-1"))
    hits = sig_lines(_context(r))
    _report("A1 — a README two levels up fires, naming that ancestor's README",
            r.returncode == 0 and len(hits) == 1 and readme_at(outer) in hits[0],
            r, results)

    # A2: a DIFFERENT folder under the SAME already-claimed ancestor, same
    # session, stays silent —— the guard is keyed on the README, not on
    # matching the exact same immediate directory as A1.
    sibling_deep = os.path.join(mid, "deep2")
    _mkfile(os.path.join(sibling_deep, "other.md"))
    r = _run_payload(_read_payload(os.path.join(sibling_deep, "other.md"),
                                    "A-session-1"))
    _report("A2 — a different folder under the SAME claimed ancestor is silent",
            r.returncode == 0 and not sig_lines(_context(r)), r, results)

    # A3: a NEW session re-arms the same ancestor README —— the guard is per
    # session, not permanent (mirrors R7 for the immediate-folder case).
    r = _run_payload(_read_payload(os.path.join(deep, "note.md"), "A-session-2"))
    hits = sig_lines(_context(r))
    _report("A3 — a new session re-arms the same ancestor README",
            r.returncode == 0 and len(hits) == 1 and readme_at(outer) in hits[0],
            r, results)

    # A4: reading the ancestor README directly is silent AND claims it, so a
    # later read of a child file in the SAME session stays silent too.
    r = _run_payload(_read_payload(readme_at(outer), "A-session-3"))
    ok4a = r.returncode == 0 and not sig_lines(_context(r))
    r2 = _run_payload(_read_payload(os.path.join(deep, "note.md"), "A-session-3"))
    ok4b = r2.returncode == 0 and not sig_lines(_context(r2))
    _report("A4 — reading the ancestor README directly is silent and claims it",
            ok4a and ok4b, r2, results)

    # A5: no README anywhere in the chain —— the rule stays silent end to end
    # (bounded by `_MAX_ANCESTORS`, never runs away up the real filesystem).
    lonely = os.path.join(root, "anc_lonely", "a", "b", "c")
    _mkfile(os.path.join(lonely, "note.md"))
    r = _run_payload(_read_payload(os.path.join(lonely, "note.md"), "A-session-4"))
    _report("A5 — no ancestor README anywhere stays silent",
            r.returncode == 0 and not sig_lines(_context(r)), r, results)

    # A6: the IMMEDIATE folder's own README and a DIFFERENT ancestor's README
    # both exist —— ONE read fires BOTH, nearest folder first, each naming
    # its own correct README (the pre-existing immediate-folder behaviour and
    # the new ancestor behaviour are independent and compose in one call).
    combo_outer = os.path.join(root, "anc_combo")
    combo_inner = os.path.join(combo_outer, "inner")
    _mkfile(readme_at(combo_outer), "# Outer procedure\n")
    _mkfile(readme_at(combo_inner), "# Inner procedure\n")
    _mkfile(os.path.join(combo_inner, "other.md"))
    r = _run_payload(_read_payload(os.path.join(combo_inner, "other.md"),
                                    "A-session-5"))
    hits = sig_lines(_context(r))
    ok6 = (r.returncode == 0 and len(hits) == 2
           and readme_at(combo_inner) in hits[0]
           and readme_at(combo_outer) in hits[1])
    _report("A6 — immediate folder's README + a different ancestor's README "
            "both fire in one call, nearest first", ok6, r, results)

    # A7: the walk STOPS at the first ancestor that is itself a project root
    # (contains `.git`) —— a README ABOVE that boundary must never be reached,
    # exactly the "don't leave the project" rule ANCESTOR WALK states.
    beyond = os.path.join(root, "anc_beyond")          # has a README
    fake_repo = os.path.join(beyond, "fakerepo")        # contains .git
    inner_repo = os.path.join(fake_repo, "inner")       # no README of its own
    _mkfile(readme_at(beyond), "# Outside-the-project procedure\n")
    os.makedirs(os.path.join(fake_repo, ".git"), exist_ok=True)
    _mkfile(os.path.join(inner_repo, "note.md"))
    r = _run_payload(_read_payload(os.path.join(inner_repo, "note.md"),
                                    "A-session-6"))
    _report("A7 — walk stops at the first `.git` ancestor; a README above it "
            "is never reached", r.returncode == 0 and not sig_lines(_context(r)),
            r, results)

    # A8: `_MAX_README_LINES_PER_CALL` bounds one call's reminder lines, even
    # when more ancestor READMEs exist than the cap —— read live from the
    # source (never copied) so a moved cap cannot silently stop being tested.
    line_cap = _read_int_const("_MAX_README_LINES_PER_CALL")
    levels = [os.path.join(root, "anc_flood")]
    for i in range(line_cap + 3):
        levels.append(os.path.join(levels[-1], "L%d" % i))
    for d in levels[:-1]:
        _mkfile(readme_at(d), "# level procedure\n")
    _mkfile(os.path.join(levels[-1], "note.md"))
    r = _run_payload(_read_payload(os.path.join(levels[-1], "note.md"),
                                    "A-session-7"))
    hits = sig_lines(_context(r))
    _report("A8 — `_MAX_README_LINES_PER_CALL` (%d) bounds one call's "
            "reminder lines even with more ancestor READMEs available"
            % line_cap,
            r.returncode == 0 and len(hits) == line_cap, r, results)

    return results


def main():
    results = []

    # --- P1/P2: the two real sign-offs must fire. --------------------------
    results.append(_check(
        "P1 — 'Yours sincerely' fires",
        "I look forward to your reply.\n\nYours sincerely,\nCulous\n",
        True, "Yours sincerely"))

    results.append(_check(
        "P2 — 'Yours faithfully' fires across a line break (inner space is "
        "matched as whitespace, so a wrapped sign-off still hits)",
        "Thank you for considering the application.\n\nYours\nfaithfully,\n",
        True))

    # --- P3-P5: the generic forms must NOT fire. ---------------------------
    # These are the false positives the fix removed. P3 is the literal bare
    # word, P4 is the everyday possessive in ordinary prose, and P5 is the
    # near-miss phrase that is NOT one of the two real sign-offs.
    results.append(_check(
        "P3 — bare 'yours' alone does NOT fire",
        "The decision is yours.\n",
        False))

    results.append(_check(
        "P4 — 'yours' in ordinary prose does NOT fire",
        "Mine differs from yours; yours may differ again next week.\n",
        False))

    results.append(_check(
        "P5 — 'yours truly' does NOT fire (not one of the two sign-offs)",
        "That was, yours truly, an oversight.\n",
        False))

    # --- P6/P7: the untouched list and its word-boundary guard still work. --
    results.append(_check(
        "P6 — an untouched marker ('Dear') still fires",
        "Dear Ms Smith,\n\nPlease find attached.\n",
        True, "Dear"))

    results.append(_check(
        "P7 — word boundary still holds ('regardless' is not 'regards')",
        "Regardless of the outcome, the dearth of data is the real issue.\n",
        False))

    # --- R1-R13: the README-first read reminder. ---------------------------
    # `PLINT_STATE_DIR` is exported BEFORE any child runs, so every plint
    # subprocess claims folders inside this test's own throwaway ledger ——
    # the real one is neither read nor written, and repeated runs of this test
    # cannot poison each other. Removed in `finally`, so nothing is left on
    # disk even if a case blows up mid-way.
    root = tempfile.mkdtemp(prefix="plint_readme_regression_")
    os.environ["PLINT_STATE_DIR"] = os.path.join(root, "state")
    try:
        print()
        results.extend(readme_cases(root))
        print()
        results.extend(ancestor_readme_cases(root))
    finally:
        os.environ.pop("PLINT_STATE_DIR", None)
        shutil.rmtree(root, ignore_errors=True)

    print()
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"\n{passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
