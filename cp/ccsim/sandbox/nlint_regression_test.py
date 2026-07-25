#!/usr/bin/env python3
"""Regression test for cscpt/nlint.py's § Numbering Continuity advisory.

WHY this test exists (coding.md: "a fix without its test is unfinished"):
a reported bug claimed nlint neither fired nor flagged on the response
sessions/2026/202607/ccsim_response_202607250326.md (replying via
sessions/2026/202607/ccsim_query_202607250326.md). Tracing the ACTUAL code
(piping realistic PostToolUse payloads through the real shim -> python
chain) showed the opposite of what was assumed: the prior version DID fire
and DID compute a flag —— a hard RED (exit 2) —— because it treated "the
query reads as a reply" alone as a confirmed breach. That was a proven
FALSE POSITIVE: the query explicitly authorises the reset (session 06's
1st response, textually "...reset from pt 1 (override)"), and numbered.md
§ Numbering Continuity itself lists "1st response of a session (CC:
despite referring to prev. comms files)" as a legitimate reset condition.
The most likely reading of "the file shows no block" is that CC correctly
judged the RED a false positive per the user's own override and moved on
(PostToolUse cannot un-write a file regardless) —— NOT that the mechanism
silently failed. Either way, the false-positive verdict itself is real and
is what this test pins.

Test 1 below is the exact reported real scenario, now expected SILENT
(advisory-suppressed, not a false "confirmed breach"). A "fix" that just
always returns 0, though, would trivially pass Test 1 alone —— so Tests
2-3 pin the OTHER direction: the hook must still actually flag a reset
that has NO excuse anywhere in its query (Test 2), and must stay silent on
an ordinary non-reset continuation (Test 3), so the mechanism keeps real
teeth instead of going permanently quiet. Tests 4 and 6 reinforce Tests 1
and 3 with FURTHER real repo history (coding.md: "mine historical/real
data for fixtures —— real past inputs catch failure classes synthetic
cases miss") — Test 4 is a real continuation, Test 6 is a real reset that
is legitimate via the OTHER route (its query is not a reply at all, rather
than an explicit override). Test 5 pins the scope guard: a non-`response_`
file with reset-shaped content must never even be inspected.

Self-contained: fixtures for Tests 2-3-5 are synthesised into a throwaway
tempdir at run time (no permanent files added to the repo, nothing to void
afterwards); Tests 1/4/6 alone read real, historical repo files, kept out
of cscpt/nlint.py itself (which must not name specific comms files —
this test script is not that script, and per coding.md test fixtures MAY
use real comms files). Run directly:

    python3 "cp/ccsim/sandbox/nlint_regression_test.py"

Exits 0 if every case matches its expected verdict, 1 otherwise (with a
per-case PASS/FAIL report on stdout, and the raw stdout/stderr on any
FAIL so a break is immediately diagnosable without re-running by hand).
"""
import json
import os
import subprocess
import sys
import tempfile

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", ".."))
SHIM = os.path.join(REPO_ROOT, "cscpt", "nlint_hook.sh")

# The exact real files the bug report named, plus two more real responses
# that reinforce (via genuine repo history) the "should stay silent" side
# from each of the two independent legitimising routes. Read live from their
# real location —— not copied —— so this test tracks the actual repo.
REAL_REPORTED_RESPONSE = os.path.join(
    REPO_ROOT, "sessions", "2026", "202607", "ccsim_response_202607250326.md"
)
REAL_CONTINUATION_RESPONSE = os.path.join(
    REPO_ROOT, "sessions", "2026", "202607", "ccsim_response_202607242319.md"
)
REAL_NOT_A_REPLY_RESET_RESPONSE = os.path.join(
    REPO_ROOT, "sessions", "2026", "202607", "ccsim_response_202607250021.md"
)


def _run_hook(file_path):
    payload = {
        "session_id": "regression-test",
        "transcript_path": "/dev/null",
        "cwd": REPO_ROOT,
        "hook_event_name": "PostToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": file_path, "content": ""},
        "tool_response": {"filePath": file_path, "success": True},
    }
    r = subprocess.run(
        ["bash", SHIM], input=json.dumps(payload),
        capture_output=True, text=True, timeout=30,
    )
    flagged = bool(r.stdout.strip()) or r.returncode != 0
    return flagged, r


def _check(label, file_path, expect_flag, required=True):
    if not os.path.isfile(file_path):
        msg = f"[{'FAIL' if required else 'SKIP'}] {label}: fixture missing -> {file_path}"
        print(msg)
        return False if required else None
    flagged, r = _run_hook(file_path)
    ok = (flagged == expect_flag)
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label}: expected {'FLAG' if expect_flag else 'silent'}, "
          f"got {'FLAG' if flagged else 'silent'} (exit={r.returncode})")
    if not ok:
        print(f"        stdout={r.stdout!r}")
        print(f"        stderr={r.stderr!r}")
    return ok


def main():
    results = []

    # --- Test 1: THE reported real scenario. Must now be silent. -----------
    # 1st response of a NEW session + an explicit user override, yet
    # textually a reply — the prior code's false-positive trigger.
    results.append(_check(
        "Test 1 (REAL, THE reported scenario) — 1st-of-session reset + "
        "explicit override, textually a reply",
        REAL_REPORTED_RESPONSE,
        expect_flag=False,
    ))

    with tempfile.TemporaryDirectory() as td:
        # --- Test 2: synthetic illegitimate reset. Must still flag. --------
        query_2 = os.path.join(td, "illegit_query.md")
        response_2 = os.path.join(td, "illegit_response_202501020000.md")
        with open(query_2, "w") as fh:
            fh.write(
                "# Reply to illegit_response_202412310000.md\n\n"
                "## 9\nPlease continue with the next steps.\n"
            )
        with open(response_2, "w") as fh:
            fh.write(
                "# Response to illegit_query.md\n\n"
                "## 1. Restarted With No Excuse\n"
                "- 1.1. This reset has no session-start or override "
                "language anywhere in the query above.\n"
            )
        results.append(_check(
            "Test 2 (synthetic) — illegitimate reset: replies, resets, "
            "NO override/session language anywhere in the query",
            response_2,
            expect_flag=True,
        ))

        # --- Test 3: ordinary continuation (no reset at all). Silent. ------
        response_3 = os.path.join(td, "cont_response_202501030000.md")
        with open(response_3, "w") as fh:
            fh.write(
                "# Response to illegit_query.md\n\n"
                "## 10. Continues Normally\n"
                "- 10.1. No reset here, so nothing to check at all.\n"
            )
        results.append(_check(
            "Test 3 (synthetic) — ordinary continuation, no reset present",
            response_3,
            expect_flag=False,
        ))

        # --- Test 5: non-response_ file. Scope guard —— never inspected. ---
        response_5 = os.path.join(td, "close_202501010000.md")
        with open(response_5, "w") as fh:
            fh.write("# Close\n\n## 1. Anything at all, even a reset\n")
        results.append(_check(
            "Test 5 (synthetic) — non-response_ file (close_) with "
            "reset-shaped content — must be silently ignored (scope guard)",
            response_5,
            expect_flag=False,
        ))

    # --- Test 4: REAL ordinary continuation. Silent. ------------------------
    results.append(_check(
        "Test 4 (REAL) — ordinary continuation (## 70, replies but does "
        "not reset)",
        REAL_CONTINUATION_RESPONSE,
        expect_flag=False,
    ))

    # --- Test 6: REAL reset legitimised via the OTHER route (not a reply). -
    results.append(_check(
        "Test 6 (REAL) — reset legitimate via NOT-a-reply route "
        "('# New Request', no reply-signal at all)",
        REAL_NOT_A_REPLY_RESET_RESPONSE,
        expect_flag=False,
    ))

    results = [r for r in results if r is not None]
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"\n{passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
