#!/usr/bin/env python3
"""Regression test for cscpt/hlint.py —— the CHAT-DISCIPLINE TALLY (second job).

WHY this suite exists (coding.md § Testing: pin every fix with a test encoding
the exact failing scenario): root CLAUDE.md §3.1 forbids chat prose, clint
(Stop) detects breaches, and clint is warn-only —— with NO channel at Stop that
reaches the model without waking it (a Stop-side correction IS a block wearing
a softer name; full audit in clint.py's THE PRICE OF THIS and hlint.py's
CHAT-DISCIPLINE TALLY sections). So the correction rides the NEXT prompt's
UserPromptSubmit `additionalContext`: hlint reads clint's verdict log and
injects ONE line naming the previous turn's breach count and class. This suite
pins that behaviour end-to-end through hlint's real stdin/stdout hook contract
—— never by importing internals —— because a rule that only works when called
directly is not wired.

THE COUNT RULE THESE CASES DEFEND (T2 especially): clint logs one verdict PER
STOP and task-notification wakes re-Stop and re-scan the SAME window, so one
breach was observed logging SEVEN growing `yellow:prose` entries under fresh
promptIds. The tally therefore reports the LAST entry's `lines=` verbatim ——
the final scan covers the whole window —— and never sums entries. A suite that
let a sum through would ship a reminder whose number nobody can defend, which
is how a reminder earns being ignored.

BASELINE OVERRIDE: `HLINT_UNDER_TEST=<path>` points the whole suite at another
copy of hlint.py —— used to demonstrate each NEW case failing against the
pre-change file (CCSIM CLAUDE.md §4.4's baseline pattern), so "the fix exists"
and "the fix is what makes these pass" stay two separately proven claims.
Defaults to the live `cscpt/hlint.py`.

Self-contained: every fixture (clint verdict logs in clint's exact live line
shape, hlint ledger logs, payloads) is synthesised in a run-scoped tempdir and
removed after; `CLINT_LOG`/`HLINT_LOG` env knobs isolate every run, so the
suite never reads or pollutes the live `cscpt/.clint.log`/`.hlint.log` —— those
are diagnostic evidence, and a test that wrote to them would corrupt the very
trail they exist to provide. Run directly:

    python3 "cp/ccsim/sandbox/hlint_chat_tally_regression_test.py"

Exits 0 if every case matches its expected verdict, 1 otherwise (per-case
PASS/FAIL on stdout, raw process output dumped on any FAIL)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", ".."))
HLINT = (os.environ.get("HLINT_UNDER_TEST")
         or os.path.join(REPO_ROOT, "cscpt", "hlint.py"))

_TALLY_SIG = "Chat-discipline tally"
_TRIGGER_SIG = "[hlint hook] Possible hashtag-trigger(s)"

# One clint log line, byte-shaped exactly like clint._log_event's live format
# (timestamp, then TAB-separated key=value fields, `first=` last).
_CLINT_LINE = ("2026-08-07T15:26:25\tsession=%s\tpid=%s\tmode=repo\t"
               "action=%s\tlines=%s\tfirst=%s")

# The session id every case uses unless it is testing session isolation.
# clint stores only the first 8 chars, so fixtures write `tallyses`.
SID = "tallysession-regression"
SID8 = SID[:8]


def _clint_log(tmp, lines, name="clint.log"):
    path = os.path.join(tmp, name)
    with open(path, "w", encoding="utf-8") as fh:
        for ln in lines:
            fh.write(ln + "\n")
    return path


def _payload(prompt="carry on", session_id=SID, cwd=REPO_ROOT, **extra):
    p = {
        "session_id": session_id,
        "transcript_path": "/dev/null",
        "prompt_id": "pid-tally-regression",
        "hook_event_name": "UserPromptSubmit",
        "prompt": prompt,
        "cwd": cwd,
    }
    p.update(extra)
    return p


def _run(payload, clint_log, hlint_log):
    """Drive hlint end-to-end through its real stdin/stdout hook contract."""
    env = dict(os.environ)
    env["CLINT_LOG"] = clint_log
    env["HLINT_LOG"] = hlint_log
    body = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, HLINT], input=body,
        capture_output=True, text=True, timeout=30, cwd=REPO_ROOT, env=env)


def _context(r):
    out = r.stdout.strip()
    if not out:
        return ""
    try:
        return json.loads(out)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        return out


def _verdict(label, ok, r, extra=None):
    print("[%s] %s" % ("PASS" if ok else "FAIL", label))
    if not ok:
        print("        exit=%s" % r.returncode)
        print("        stdout=%r" % r.stdout)
        print("        stderr=%r" % r.stderr)
        if extra is not None:
            # `(extra,)` not `extra`: a bare tuple would be
            # consumed as multiple % arguments and crash the
            # REPORT —— on the FAIL path, where it matters.
            print("        extra=%r" % (extra,))
    return ok


def main():
    results = []
    tmp = tempfile.mkdtemp(prefix="hlint_tally_")
    try:
        # --- T1: the core case —— a yellow verdict for this session fires ONE
        # tally line naming count and class; the stage log carries `fired:`.
        clog = _clint_log(tmp, [
            _CLINT_LINE % (SID8, "aaa", "yellow:prose", "3", "sounds good!")])
        hlog = os.path.join(tmp, "t1.hlint.log")
        r = _run(_payload(), clog, hlog)
        ctx = _context(r)
        logged = open(hlog, encoding="utf-8").read() if os.path.isfile(hlog) else ""
        results.append(_verdict(
            "T1 — previous-turn breach fires: one line, count 3, class "
            "`prose`, and the log carries tally=fired:",
            (r.returncode == 0 and _TALLY_SIG in ctx
             and "3 impermissible chat lines" in ctx and "`prose`" in ctx
             and ctx.count(_TALLY_SIG) == 1
             and "\ttally=fired:prose:3@" in logged), r, extra=ctx))

        # --- T2: THE INFLATION DEFENCE —— growing wake re-scans of one window
        # (lines=2 then lines=4) report the LAST entry's 4, never a 6 sum.
        clog = _clint_log(tmp, [
            _CLINT_LINE % (SID8, "aaa", "yellow:prose", "2", "."),
            _CLINT_LINE % (SID8, "bbb", "yellow:prose", "4", "."),
        ], "t2.clint.log")
        hlog = os.path.join(tmp, "t2.hlint.log")
        r = _run(_payload(), clog, hlog)
        ctx = _context(r)
        results.append(_verdict(
            "T2 — count = LAST entry (4), never the sum (6): wake re-scans of "
            "one window must not inflate",
            (r.returncode == 0 and "4 impermissible" in ctx
             and "6 impermissible" not in ctx
             and "2 impermissible" not in ctx), r, extra=ctx))

        # --- T3: a clean final verdict silences the tally even with an older
        # yellow above it —— the last scan superseded it.
        clog = _clint_log(tmp, [
            _CLINT_LINE % (SID8, "aaa", "yellow:prose", "2", "."),
            _CLINT_LINE % (SID8, "bbb", "clean", "0", "-"),
        ], "t3.clint.log")
        hlog = os.path.join(tmp, "t3.hlint.log")
        r = _run(_payload(), clog, hlog)
        results.append(_verdict(
            "T3 — last verdict clean -> silent (older yellow superseded)",
            r.returncode == 0 and not _context(r)
            and "\ttally=clean\t" in open(hlog, encoding="utf-8").read(), r))

        # --- T4: dedup —— the SAME verdict entry is reported exactly once;
        # the second prompt is silent with stage `dup`. Without this, every
        # prompt of a long session re-nags one historic breach forever.
        clog = _clint_log(tmp, [
            _CLINT_LINE % (SID8, "aaa", "yellow:sha_shape", "1",
                           "🦈 pushed everything, all good")], "t4.clint.log")
        hlog = os.path.join(tmp, "t4.hlint.log")
        r1 = _run(_payload(), clog, hlog)
        r2 = _run(_payload(), clog, hlog)
        logged = open(hlog, encoding="utf-8").read()
        results.append(_verdict(
            "T4 — one verdict, one report: first prompt fires, second is "
            "silent and logs tally=dup",
            (_TALLY_SIG in _context(r1) and not _context(r2)
             and r1.returncode == 0 and r2.returncode == 0
             and "\ttally=dup\t" in logged
             and logged.count("tally=fired:") == 1), r2, extra=logged))

        # --- T5: session isolation —— another session's yellow entry must
        # never cross-report (the log is shared by every session on the Mac).
        clog = _clint_log(tmp, [
            _CLINT_LINE % ("otherses", "aaa", "yellow:prose", "9", "hello")],
            "t5.clint.log")
        hlog = os.path.join(tmp, "t5.hlint.log")
        r = _run(_payload(), clog, hlog)
        results.append(_verdict(
            "T5 — another session's breach -> silent (tally=no_entry)",
            r.returncode == 0 and not _context(r)
            and "\ttally=no_entry\t" in open(hlog, encoding="utf-8").read(), r))

        # --- T6: a `<task-notification>` wake is not a new turn —— no tally,
        # no scan at all, even with a reportable yellow entry waiting.
        clog = _clint_log(tmp, [
            _CLINT_LINE % (SID8, "aaa", "yellow:prose", "2", ".")],
            "t6.clint.log")
        hlog = os.path.join(tmp, "t6.hlint.log")
        r = _run(_payload(prompt="<task-notification>\n<summary>done"
                                 "</summary>\n</task-notification>"),
                 clog, hlog)
        logged = open(hlog, encoding="utf-8").read()
        results.append(_verdict(
            "T6 — task-notification wake: no tally (stage not_user_prompt, "
            "tally=-), breach left for the next REAL prompt",
            (r.returncode == 0 and not _context(r)
             and "stage=not_user_prompt" in logged
             and "tally=fired" not in logged), r, extra=logged))

        # --- T7: cwd gate —— foreign cwd silences the TALLY whilst the
        # trigger half stays deliberately global (repo_scope_guard suite B2
        # pins the global half; this pins the asymmetry from the tally side).
        clog = _clint_log(tmp, [
            _CLINT_LINE % (SID8, "aaa", "yellow:prose", "2", ".")],
            "t7.clint.log")
        hlog = os.path.join(tmp, "t7.hlint.log")
        r = _run(_payload(prompt="#close please", cwd="/tmp"), clog, hlog)
        ctx = _context(r)
        results.append(_verdict(
            "T7 — foreign cwd: `#close` reminder still fires (global), tally "
            "does NOT (off_scope)",
            (r.returncode == 0 and _TRIGGER_SIG in ctx
             and _TALLY_SIG not in ctx
             and "\ttally=off_scope\t"
             in open(hlog, encoding="utf-8").read()), r, extra=ctx))

        # --- T7b: a repo SUB-PATH cwd is in scope —— sessions routinely run
        # from a month folder, not the root.
        hlog = os.path.join(tmp, "t7b.hlint.log")
        r = _run(_payload(cwd=os.path.join(REPO_ROOT, "cscpt")), clog, hlog)
        results.append(_verdict(
            "T7b — repo sub-path cwd is in scope: tally fires",
            r.returncode == 0 and _TALLY_SIG in _context(r), r))

        # --- T8: missing clint log —— fail OPEN, silent, stage no_log. A
        # freshly-pruned or never-created log must never break a prompt.
        hlog = os.path.join(tmp, "t8.hlint.log")
        r = _run(_payload(), os.path.join(tmp, "absent.clint.log"), hlog)
        results.append(_verdict(
            "T8 — clint log absent: exit 0, silent, tally=no_log (fail open, "
            "stage visible)",
            r.returncode == 0 and not _context(r)
            and "\ttally=no_log\t" in open(hlog, encoding="utf-8").read(), r))

        # --- T9: garbage in clint's log —— unparseable lines, a matching line
        # with no action field, binary noise —— must never crash or fire.
        clog = _clint_log(tmp, [
            "not a log line at all \x00\x01",
            "2026-08-07T15:00:00\tsession=%s\tgibberish" % SID8,
        ], "t9.clint.log")
        hlog = os.path.join(tmp, "t9.hlint.log")
        r = _run(_payload(), clog, hlog)
        results.append(_verdict(
            "T9 — malformed clint log: exit 0, no output, no crash",
            r.returncode == 0 and not _context(r) and not r.stderr.strip(), r))

        # --- T10: the excerpt contract —— capped with an ellipsis, and
        # dropped outright when the offender carries a backtick (a stub that
        # broke the line's own quoting would re-inject what it suppresses).
        long_first = "This is a very long offending prose line that keeps " \
                     "going well past any sensible stub length"
        clog = _clint_log(tmp, [
            _CLINT_LINE % (SID8, "aaa", "yellow:prose", "5", long_first)],
            "t10a.clint.log")
        hlog = os.path.join(tmp, "t10a.hlint.log")
        r = _run(_payload(), clog, hlog)
        ctx = _context(r)
        stub = ""
        if "first offender: `" in ctx:
            stub = ctx.split("first offender: `", 1)[1].split("`", 1)[0]
        ok_a = (_TALLY_SIG in ctx and stub.endswith("…")
                and len(stub) <= 41 and long_first[:20] in ctx)
        clog = _clint_log(tmp, [
            _CLINT_LINE % (SID8, "aaa", "yellow:prose", "1",
                           "a line with a `backtick` inside")],
            "t10b.clint.log")
        hlog = os.path.join(tmp, "t10b.hlint.log")
        r2 = _run(_payload(), clog, hlog)
        ctx2 = _context(r2)
        ok_b = (_TALLY_SIG in ctx2 and "first offender" not in ctx2
                and "backtick" not in ctx2)
        results.append(_verdict(
            "T10 — excerpt: hard-capped with ellipsis; dropped entirely when "
            "the offender itself carries a backtick",
            ok_a and ok_b and r.returncode == 0 and r2.returncode == 0,
            r if not ok_a else r2, extra=(stub, ctx2)))

        # --- T11: both jobs in ONE valid JSON injection —— tally line first,
        # then the trigger header; a second stdout document would be ignored
        # by the harness, so they must share one `additionalContext`.
        clog = _clint_log(tmp, [
            _CLINT_LINE % (SID8, "aaa", "yellow:prose", "2", ".")],
            "t11.clint.log")
        hlog = os.path.join(tmp, "t11.hlint.log")
        r = _run(_payload(prompt="#close please"), clog, hlog)
        ctx = _context(r)
        parsed_ok = False
        try:
            json.loads(r.stdout)
            parsed_ok = True
        except Exception:
            pass
        results.append(_verdict(
            "T11 — tally + `#close` reminder share one valid JSON context, "
            "tally first",
            (parsed_ok and _TALLY_SIG in ctx and _TRIGGER_SIG in ctx
             and ctx.index(_TALLY_SIG) < ctx.index(_TRIGGER_SIG)
             and r.returncode == 0), r, extra=ctx))

        # --- T12: exempt/authorised verdicts carry no breach —— silent.
        clog = _clint_log(tmp, [
            _CLINT_LINE % (SID8, "aaa", "exempt:yn", "1", "yes")],
            "t12.clint.log")
        hlog = os.path.join(tmp, "t12.hlint.log")
        r = _run(_payload(), clog, hlog)
        results.append(_verdict(
            "T12 — exempt:* verdict (user-authorised chat) -> silent",
            r.returncode == 0 and not _context(r)
            and "\ttally=clean\t" in open(hlog, encoding="utf-8").read(), r))

        # --- T13: an unparseable `lines=` claims NO number —— a count that
        # cannot be defended must not be invented.
        clog = _clint_log(tmp, [
            _CLINT_LINE % (SID8, "aaa", "yellow:prose", "??", ".")],
            "t13.clint.log")
        hlog = os.path.join(tmp, "t13.hlint.log")
        r = _run(_payload(), clog, hlog)
        ctx = _context(r)
        results.append(_verdict(
            "T13 — unparseable count: still fires, but claims no number",
            (r.returncode == 0 and _TALLY_SIG in ctx
             and "impermissible chat line" not in ctx
             and "drew a breach verdict" in ctx), r, extra=ctx))

        # --- T14: the prompt-erasure guard —— whatever fires, the output
        # carries no `decision` key anywhere (`decision:"block"` on
        # UserPromptSubmit ERASES the user's prompt; hook_guide §6.6).
        clog = _clint_log(tmp, [
            _CLINT_LINE % (SID8, "aaa", "yellow:prose", "2", ".")],
            "t14.clint.log")
        hlog = os.path.join(tmp, "t14.hlint.log")
        r = _run(_payload(prompt="#close please"), clog, hlog)
        try:
            doc = json.loads(r.stdout)
        except Exception:
            doc = {}
        results.append(_verdict(
            "T14 — never a `decision` key: advisory can never erase a prompt",
            (r.returncode == 0 and doc
             and "decision" not in doc
             and "decision" not in doc.get("hookSpecificOutput", {})), r))

        # --- T15: the `sha_label` class (clint's solo-label check, root
        # CLAUDE.md §3.2.4.4–5) surfaces with a correction the model can ACT
        # on in one line. The generic "declarations only" clause would teach
        # the WRONG fix here —— the offending line WAS a declaration; the fix
        # is dropping the repo label —— so this class carries its own rule
        # clause naming §3.2.4.5 and the concrete act. Anti-wallpaper stack
        # re-proven on the new class end-to-end: one report per verdict
        # (second prompt silent, stage dup), and the anti-apology tail stays.
        clog = _clint_log(tmp, [
            _CLINT_LINE % (SID8, "aaa", "yellow:sha_label", "1",
                           "🦈 Default: `302d7d8c`")], "t15.clint.log")
        hlog = os.path.join(tmp, "t15.hlint.log")
        r1 = _run(_payload(), clog, hlog)
        r2 = _run(_payload(), clog, hlog)
        ctx = _context(r1)
        logged = open(hlog, encoding="utf-8").read()
        results.append(_verdict(
            "T15 — sha_label fires its OWN actionable correction "
            "(§3.2.4.5, drop the label), not the generic clause; "
            "dedup and the no-apology tail hold",
            (r1.returncode == 0 and r2.returncode == 0
             and _TALLY_SIG in ctx and "`sha_label`" in ctx
             and "§3.2.4.5" in ctx and "drop the label" in ctx
             and "six declaration lines ONLY" not in ctx
             and "do NOT apologise in chat" in ctx
             and not _context(r2)
             and "\ttally=dup\t" in logged
             and logged.count("tally=fired:") == 1), r1, extra=ctx))

        # --- T16: the guard the rule map needs —— every OTHER class keeps
        # the generic §3.1–§3.2 clause, so the per-class override can never
        # silently leak beyond the one class that earned it.
        clog = _clint_log(tmp, [
            _CLINT_LINE % (SID8, "aaa", "yellow:prose", "2", "sounds good!")],
            "t16.clint.log")
        hlog = os.path.join(tmp, "t16.hlint.log")
        r = _run(_payload(), clog, hlog)
        ctx = _context(r)
        results.append(_verdict(
            "T16 — other classes keep the generic rule clause, never "
            "sha_label's",
            (r.returncode == 0 and _TALLY_SIG in ctx
             and "six declaration lines ONLY" in ctx
             and "§3.2.4.5" not in ctx
             and "drop the label" not in ctx), r, extra=ctx))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    passed = sum(1 for x in results if x)
    total = len(results)
    print("%d/%d passed" % (passed, total))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
