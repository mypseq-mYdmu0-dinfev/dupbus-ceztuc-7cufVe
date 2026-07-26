#!/usr/bin/env python3
"""Regression test for cscpt/nlint.py —— BOTH of its independent advisories:
§ Numbering Continuity (Tests 1-6) and the tenth-sibling reminder (A1-A12,
in `section_tenth`, which carries its own rationale).

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


# nlint emits BOTH checks in a single `hookSpecificOutput.additionalContext`,
# one line each, so a stable phrase from each message template tells the test
# WHICH check fired. Asserting per-check (rather than "any output at all") is
# load-bearing now that nlint runs two independent checks: a real response can
# legitimately trip one and not the other, and a check-agnostic assertion would
# then report a true positive from check A as a failure of check B. That is not
# hypothetical —— it is exactly what the real fixture in Test 1 does.
_RESET_SIG = "numbering reset detected"
_TENTH_SIG = "reached its 10th item"


def _fired(r):
    """Return `(reset_fired, tenth_fired)` for a completed hook run."""
    out = r.stdout.strip()
    if not out and r.returncode == 0:
        return False, False
    try:
        ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        # Unparseable/non-zero output counts as BOTH firing, so a malformed
        # payload can never masquerade as a clean silent pass.
        return True, True
    return (_RESET_SIG in ctx), (_TENTH_SIG in ctx)


def _run_hook(file_path, content=""):
    """Drive the REAL shim -> python chain with a realistic PostToolUse payload.

    `content` is the text a Write would actually carry, and it is not cosmetic:
    nlint_hook.sh gates the TENTH-SIBLING check on the payload TEXT, because a
    check that applies to any file cannot be gated on the filename. Leaving it
    empty therefore exercises the `response_` filename gate alone."""
    payload = {
        "session_id": "regression-test",
        "transcript_path": "/dev/null",
        "cwd": REPO_ROOT,
        "hook_event_name": "PostToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": file_path, "content": content},
        "tool_response": {"filePath": file_path, "success": True},
    }
    r = subprocess.run(
        ["bash", SHIM], input=json.dumps(payload),
        capture_output=True, text=True, timeout=30,
    )
    return r


def _check(label, file_path, expect_reset=None, expect_tenth=None,
           content="", required=True):
    """Assert either check independently. `None` = not asserted here, so a case
    written for one check never silently locks in the other's behaviour."""
    if not os.path.isfile(file_path):
        msg = f"[{'FAIL' if required else 'SKIP'}] {label}: fixture missing -> {file_path}"
        print(msg)
        return False if required else None
    r = _run_hook(file_path, content=content)
    reset, tenth = _fired(r)
    ok = ((expect_reset is None or reset == expect_reset)
          and (expect_tenth is None or tenth == expect_tenth))
    status = "PASS" if ok else "FAIL"
    want = []
    if expect_reset is not None:
        want.append(f"reset={'FLAG' if expect_reset else 'silent'}")
    if expect_tenth is not None:
        want.append(f"tenth={'FLAG' if expect_tenth else 'silent'}")
    print(f"[{status}] {label}: expected {', '.join(want)}, got "
          f"reset={'FLAG' if reset else 'silent'}, "
          f"tenth={'FLAG' if tenth else 'silent'} (exit={r.returncode})")
    if not ok:
        print(f"        stdout={r.stdout!r}")
        print(f"        stderr={r.stderr!r}")
    return ok


def section_tenth():
    """Tests A1-A12 —— nlint's SECOND, independent check: a numbered level has
    reached its 10th sibling (`- [n].10.`).

    WHY these exist: numbered.md warns that ⌘F `[n].1` also surfaces `[n].10`,
    `[n].11`, ... and offers two remedies (split into separate points, or make
    that level 2-digit). The check reminds; it must never nag. So the cases pin
    BOTH directions —— it fires on every genuine shape (A1/A3/A7/A10/A11), and
    stays silent on every near-miss that would train the reader to ignore it
    (A2 nine siblings, A4 a prose decimal, A5 code-fence content, A6 a level
    that already took the 2-digit remedy, A8 a file type numbered.md exempts).
    A6b pins the boundary between those two directions: the 2-digit excuse is
    keyed PER LEVEL, so it must not silence a different, unexcused level in the
    same file.

    A1 doubles as the proof that the shim's fast-path gate was widened
    correctly: its file is NOT a `response_`, so the original filename-only gate
    would have exited before Python ever ran. A9 pins the accepted cost of
    gating on payload text —— a write that neither names a `response_` nor
    carries the trigger text stays silent even though the file on disk holds
    it. A7 pins independence: one file, both checks, both fired."""
    results = []
    with tempfile.TemporaryDirectory() as td:

        def write(name, text):
            path = os.path.join(td, name)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            return path, text

        # --- A1: plain .md, NOT a response_ -> must still fire. -------------
        p, c = write("notes.md",
                     "# Notes\n\n- 3.9. Ninth.\n- 3.10. Tenth sibling.\n")
        results.append(_check(
            "A1 (synthetic) — `- 3.10.` in a NON-response_ .md — proves the "
            "shim gate widening (filename gate alone would have skipped it)",
            p, expect_tenth=True, content=c))

        # --- A2: nine siblings only -> nothing has overflowed yet. ----------
        p, c = write("nine.md", "# Nine\n\n- 3.8. Eighth.\n- 3.9. Ninth.\n")
        results.append(_check(
            "A2 (synthetic) — `- 3.9.` only, no tenth sibling",
            p, expect_tenth=False, content=c))

        # --- A3: nested level (parent is a dotted prefix). ------------------
        p, c = write("nested.md", "# Nested\n\n  - 1.2.10. Deep tenth.\n")
        results.append(_check(
            "A3 (synthetic) — nested `- 1.2.10.` (indented, parent `1.2`)",
            p, expect_tenth=True, content=c))

        # --- A4: prose decimal -> the false positive to avoid. --------------
        # numbered.md mandates a dot between number and text, so `- 3.10 metres`
        # (no dot) is a measurement, not an item. Firing here would nag on every
        # price and dimension in ordinary prose.
        p, c = write("prose.md", "# Prose\n\n- 3.10 metres of cable.\n"
                                 "- 3.10 per unit, ex GST.\n")
        results.append(_check(
            "A4 (synthetic) — prose decimal `- 3.10 metres` must NOT fire "
            "(no number/text dot -> not a numbered item)",
            p, expect_tenth=False, content=c))

        # --- A5: inside a code fence -> masked, exactly like check B. -------
        p, c = write("fenced.md",
                     "# Fenced\n\n```\n- 3.10. Illustrative only.\n```\n")
        results.append(_check(
            "A5 (synthetic) — `- 3.10.` inside a ``` fence is masked",
            p, expect_tenth=False, content=c))

        # --- A6: level already 2-digit -> the remedy is in force. -----------
        # numbered.md: "If `[N].01` is seen, `[N].10` (at least) is expected."
        p, c = write("twodigit.md",
                     "# Two-digit\n\n- 3.01. First.\n- 3.09. Ninth.\n"
                     "- 3.10. Tenth, correctly numbered.\n")
        results.append(_check(
            "A6 (synthetic) — level ALREADY 2-digit (`- 3.01.` present) — "
            "`- 3.10.` is the remedy working, so no nag",
            p, expect_tenth=False, content=c))

        # --- A6b: suppression is PER LEVEL, not per file. -------------------
        # Caught during development: an early single-pass implementation kept
        # only the FIRST tenth-sibling hit, so a suppressed level (`3.10.`,
        # excused by `3.01.`) swallowed a genuine unexcused one (`5.10.`) later
        # in the same file. One level taking the 2-digit remedy must never
        # excuse a different level that has not.
        p, c = write("mixed.md",
                     "# Mixed\n\n- 3.01. Deliberately 2-digit.\n"
                     "- 3.10. Legitimate under the fallback.\n"
                     "- 5.10. A DIFFERENT level, with no such excuse.\n")
        results.append(_check(
            "A6b (synthetic) — one level excused by `- 3.01.` must NOT excuse "
            "an unexcused `- 5.10.` elsewhere in the same file",
            p, expect_tenth=True, content=c))

        # --- A7: both checks, one file, independently. ----------------------
        write("a7_query.md", "# Reply to a7_response_202412310000.md\n\n"
                             "## 9\nPlease continue.\n")
        p, c = write("a7_response_202501020000.md",
                     "# Response to a7_query.md\n\n"
                     "## 1. Reset With No Excuse\n"
                     "- 1.1. Nothing in the query authorises this reset.\n"
                     "- 3.10. And a tenth sibling as well.\n")
        results.append(_check(
            "A7 (synthetic) — one response_ trips BOTH checks independently",
            p, expect_reset=True, expect_tenth=True, content=c))

        # --- A8: file type numbered.md exempts -> silent. -------------------
        p, c = write("script.py",
                     "# comment\n# - 3.10. Looks like a tenth sibling.\n")
        results.append(_check(
            "A8 (synthetic) — `.py` (numbered.md exempts code) — silent",
            p, expect_tenth=False, content=c))

        # --- A9: ACCEPTED gate gap, pinned so it stays deliberate. ----------
        # Same file as A1, but the payload carries neither `response_` nor the
        # trigger text (e.g. an unrelated later edit). The shim exits before
        # Python by design: the reminder was already delivered when `.10` was
        # introduced, and re-warning on every subsequent edit is the nagging
        # this hook must avoid.
        p, _ = write("gap.md", "# Gap\n\n- 3.10. Tenth sibling.\n")
        results.append(_check(
            "A9 (synthetic) — accepted trade-off: payload without the trigger "
            "text and without `response_` -> gated out, no re-nag",
            p, expect_tenth=False, content="just an unrelated edit"))

        # --- A10: bare `- 3.10` at end of line still counts. ----------------
        p, c = write("bare.md", "# Bare\n\n- 3.10\n")
        results.append(_check(
            "A10 (synthetic) — bare `- 3.10` at end of line",
            p, expect_tenth=True, content=c))

        # --- A11: strengthens Test 5 —— that case's payload never reaches ---
        # Python (the shim gates it out), so it pins the SHIM. This one forces
        # Python to run on a `close_` and pins the PYTHON scope guard: the
        # reset check is still refused, whilst the tenth check applies.
        p, c = write("close_202501010000.md",
                     "# Close\n\n## 1. A reset-shaped heading\n"
                     "- 3.10. And a tenth sibling.\n")
        results.append(_check(
            "A11 (synthetic) — `close_` whose payload DOES reach Python: "
            "reset check still refused (scope), tenth check still applies",
            p, expect_reset=False, expect_tenth=True, content=c))

    # --- A12: REAL repo history —— a genuine 10th sibling (`- 10.10.`). -----
    # coding.md: "mine historical/real data for fixtures". This is the same
    # real response Test 1 uses; it legitimately trips check A and not check B,
    # which is precisely why the assertions here are per-check.
    results.append(_check(
        "A12 (REAL) — historical response containing a genuine `- 10.10.`",
        REAL_REPORTED_RESPONSE, expect_tenth=True))

    return results


def main():
    results = []

    # --- Test 1: THE reported real scenario. Must now be silent. -----------
    # 1st response of a NEW session + an explicit user override, yet
    # textually a reply — the prior code's false-positive trigger.
    results.append(_check(
        "Test 1 (REAL, THE reported scenario) — 1st-of-session reset + "
        "explicit override, textually a reply",
        REAL_REPORTED_RESPONSE,
        expect_reset=False,
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
            expect_reset=True,
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
            expect_reset=False,
        ))

        # --- Test 5: non-response_ file. Scope guard —— never inspected. ---
        response_5 = os.path.join(td, "close_202501010000.md")
        with open(response_5, "w") as fh:
            fh.write("# Close\n\n## 1. Anything at all, even a reset\n")
        results.append(_check(
            "Test 5 (synthetic) — non-response_ file (close_) with "
            "reset-shaped content — must be silently ignored (scope guard)",
            response_5,
            expect_reset=False,
        ))

    # --- Test 4: REAL ordinary continuation. Silent. ------------------------
    results.append(_check(
        "Test 4 (REAL) — ordinary continuation (## 70, replies but does "
        "not reset)",
        REAL_CONTINUATION_RESPONSE,
        expect_reset=False,
    ))

    # --- Test 6: REAL reset legitimised via the OTHER route (not a reply). -
    results.append(_check(
        "Test 6 (REAL) — reset legitimate via NOT-a-reply route "
        "('# New Request', no reply-signal at all)",
        REAL_NOT_A_REPLY_RESET_RESPONSE,
        expect_reset=False,
    ))

    results.extend(section_tenth())

    results = [r for r in results if r is not None]
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"\n{passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
