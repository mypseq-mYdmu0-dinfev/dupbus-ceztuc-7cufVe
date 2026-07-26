#!/usr/bin/env python3
"""Regression test for cscpt/plint.py's DELIVERABLE marker list.

WHY this test exists (coding.md: "pin EVERY fixed bug w/ a regression test
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
import subprocess
import sys

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

    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"\n{passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
