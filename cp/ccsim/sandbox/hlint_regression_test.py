#!/usr/bin/env python3
"""Regression test for cscpt/hlint.py —— the BACKTICK / FENCE EXEMPTION added
to the hashtag-trigger linter, plus a pin that dedupe/caps/fail-safe still
hold after the rescan.

WHY this test exists (coding.md: "a fix without its test is unfinished"):
hlint used to scan a single joined corpus (prompt + any referenced `.md`
content) for bare `#name` tokens with no notion of quoting, so a trigger
merely being DISCUSSED —— `` `#close` `` in a question, or shown inside a
```fenced``` example —— fired exactly like a live `#close` invocation. Root
CLAUDE.md itself carries several such illustrations (`` `#replace` ``,
`` `#debate` ``), so reading it in as referenced content used to misfire on
every one of them. The fix: a `#name` sitting inside a fenced code block or a
single-backtick inline span is now SKIPPED, on the reasoning that both are the
same kind of quoting and deserve the same exemption (full rationale in
hlint.py's own docstring, BACKTICK / FENCE EXEMPTION —— not restated here per
coding.md self-contained-permanence: this file pins the behaviour, the source
explains it).

The rescan changed HOW triggers are collected (per-source now, not a joined
blob) without touching WHAT happens after collection, so H8-H11 pin that
dedupe, the `_MAX_REMINDERS` cap, and the fail-safe/malformed-payload paths
are exactly as before.

Self-contained: every fixture (prompts, referenced `.md` file) is synthesised
at run time (a throwaway tempdir for the referenced-file case, removed after);
no repo file is touched. hlint.py is driven end-to-end through its actual
stdin/stdout UserPromptSubmit hook contract, not by importing its internals —
a rule that only works when called directly is not wired. Run directly:

    python3 "cp/ccsim/sandbox/hlint_regression_test.py"

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
HLINT = os.path.join(REPO_ROOT, "cscpt", "hlint.py")

_HEADER_SIG = "[hlint hook]"


def _payload(prompt, session_id="hlint-regression", cwd=REPO_ROOT):
    """A realistic UserPromptSubmit payload (hook_guide § Verified Payload
    Shapes: session_id, transcript_path, cwd, hook_event_name, prompt)."""
    return {
        "session_id": session_id,
        "transcript_path": "/dev/null",
        "prompt_id": "pid-hlint-regression",
        "permission_mode": "default",
        "hook_event_name": "UserPromptSubmit",
        "prompt": prompt,
        "session_title": "hlint regression",
        "cwd": cwd,
    }


def _run(payload):
    """Drive hlint end-to-end through its real stdin/stdout hook contract.
    `payload` may be a str (deliberately malformed) or a dict."""
    body = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, HLINT], input=body,
        capture_output=True, text=True, timeout=30, cwd=REPO_ROOT,
    )


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


def _reminder_lines(ctx):
    return [l for l in ctx.splitlines() if l.startswith("`#")]


def _fired_for(ctx, name):
    """True if the reminder for `#name` specifically is present."""
    tag = "`#%s`" % name
    return any(line.startswith(tag) for line in _reminder_lines(ctx))


def _check(label, prompt_or_payload, expect):
    """`expect` is a callable(ctx, r) -> bool, or a plain bool meaning
    'any reminder fired at all'. `prompt_or_payload` is a full payload dict
    if already built (e.g. by `_payload`), otherwise a bare prompt STRING that
    still needs wrapping —— a str is never passed through as a raw body here
    (that path is exercised directly via `_run` in the malformed-payload
    cases below, never through this helper)."""
    payload = (prompt_or_payload if isinstance(prompt_or_payload, dict)
               else _payload(prompt_or_payload))
    r = _run(payload)
    ctx = _context(r)
    if callable(expect):
        ok = expect(ctx, r)
    else:
        ok = (bool(ctx) == expect) and r.returncode == 0
    status = "PASS" if ok else "FAIL"
    print("[%s] %s" % (status, label))
    if not ok:
        print("        exit=%s" % r.returncode)
        print("        stdout=%r" % r.stdout)
        print("        stderr=%r" % r.stderr)
    return ok


def _cap():
    """hlint's live `_MAX_REMINDERS`, read from the source rather than
    copied. A hard-coded number here would keep "passing" while testing
    nothing the day somebody moves the cap."""
    src = open(HLINT, encoding="utf-8").read()
    m = re.search(r"^_MAX_REMINDERS\s*=\s*(\d+)", src, re.M)
    if not m:
        raise SystemExit("hlint._MAX_REMINDERS not found —— cap renamed?")
    return int(m.group(1))


# Real trigger names with an actual `universal/<name>.md` file, so each one
# both matches the regex AND resolves to a genuine reminder line. Reused for
# the cap test (H9) —— there are comfortably more of these than the cap.
_REAL_TRIGGERS = sorted(
    os.path.splitext(fn)[0]
    for fn in os.listdir(os.path.join(REPO_ROOT, "universal"))
    if fn.endswith(".md")
)


def main():
    results = []

    # --- H1: the core case —— a bare trigger fires. -------------------------
    results.append(_check(
        "H1 — bare `#close` fires",
        "please #close this session",
        lambda ctx, r: _fired_for(ctx, "close") and r.returncode == 0))

    # --- H2: the fix —— the same trigger, backticked, does NOT fire. --------
    results.append(_check(
        "H2 — backticked `` `#close` `` does NOT fire",
        "what does `#close` do?",
        lambda ctx, r: not ctx and r.returncode == 0))

    # --- H3: a mix in one prompt fires only for the bare one. ---------------
    results.append(_check(
        "H3 — mix (backticked + bare) fires only for the bare one",
        "explain `#close` first, then actually run #close for real",
        lambda ctx, r: (_fired_for(ctx, "close") and len(_reminder_lines(ctx)) == 1
                        and r.returncode == 0)))

    # --- H4: a fenced code block exempts its trigger too. -------------------
    results.append(_check(
        "H4 — a fenced ``` block ``` containing `#close` does NOT fire",
        "see example:\n```\n#close\n```\nthanks",
        lambda ctx, r: not ctx and r.returncode == 0))

    # --- H5: fenced content is exempt, but a bare trigger OUTSIDE the fence
    # in the SAME prompt still fires —— the exemption is scoped to the span,
    # not the whole prompt.
    results.append(_check(
        "H5 — fenced `#close` is silent but a bare `#plan` outside still fires",
        "```\n#close\n```\nnow really do #plan",
        lambda ctx, r: (not _fired_for(ctx, "close") and _fired_for(ctx, "plan")
                        and r.returncode == 0)))

    # --- H6/H7: a trigger inside a REFERENCED .md file follows the same rule
    # —— bare fires, backticked doesn't —— exercised from ONE fixture so both
    # sit in the same referenced-file content, the scenario the owner named
    # (root CLAUDE.md's own quoted `#replace`/`#debate` examples).
    tmp = tempfile.mkdtemp(prefix="hlint_regression_")
    try:
        fixture = os.path.join(tmp, "fixture.md")
        with open(fixture, "w", encoding="utf-8") as fh:
            fh.write(
                "This note discusses `#shrink` as an example, but actually "
                "wants #plan actioned.\n")
        prompt = "Please check %s and let me know." % fixture
        r = _run(_payload(prompt))
        ctx = _context(r)
        ok = (_fired_for(ctx, "plan") and not _fired_for(ctx, "shrink")
              and r.returncode == 0)
        status = "PASS" if ok else "FAIL"
        print("[%s] H6/H7 — referenced .md: bare `#plan` fires, "
              "backticked `#shrink` does NOT" % status)
        if not ok:
            print("        exit=%s" % r.returncode)
            print("        stdout=%r" % r.stdout)
        results.append(ok)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # --- H8: dedupe is unaffected —— 3 bare occurrences -> ONE reminder. -----
    results.append(_check(
        "H8 — dedupe unaffected: `#close` x3 bare -> exactly one reminder",
        "#close #close #close",
        lambda ctx, r: (_fired_for(ctx, "close") and len(_reminder_lines(ctx)) == 1
                        and r.returncode == 0)))

    # --- H9: `_MAX_REMINDERS` cap is unaffected —— more distinct real
    # triggers than the cap still yields exactly `cap` reminder lines.
    cap = _cap()
    assert len(_REAL_TRIGGERS) > cap, (
        "fixture needs more universal/*.md triggers than the cap to test it")
    prompt = " ".join("#%s" % name for name in _REAL_TRIGGERS)
    results.append(_check(
        "H9 — `_MAX_REMINDERS` cap (%d) still bounds the reminder count" % cap,
        prompt,
        lambda ctx, r: len(_reminder_lines(ctx)) == cap and r.returncode == 0))

    # --- H10/H11: fail-safe paths are unaffected —— any malformed/degenerate
    # payload shape -> exit 0, no output, never an exception surfaced.
    malformed = (
        "{not json at all",
        json.dumps({"prompt": 12345}),           # non-string prompt
        json.dumps({"prompt": ""}),               # empty prompt
        json.dumps([1, 2, 3]),                    # not a dict at top level
        json.dumps({"no_prompt_key": True}),      # missing `prompt` entirely
        "",                                        # empty stdin
    )
    for i, bad in enumerate(malformed):
        r = _run(bad)
        ok = (r.returncode == 0 and not r.stdout.strip())
        status = "PASS" if ok else "FAIL"
        print("[%s] H10.%d — malformed/degenerate payload: exit 0 and silent"
              % (status, i + 1))
        if not ok:
            print("        stdout=%r" % r.stdout)
            print("        stderr=%r" % r.stderr)
        results.append(ok)

    print()
    passed = sum(1 for r in results if r)
    total = len(results)
    print("%d/%d passed" % (passed, total))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
