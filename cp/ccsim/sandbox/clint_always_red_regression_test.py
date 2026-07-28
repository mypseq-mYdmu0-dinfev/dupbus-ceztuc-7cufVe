#!/usr/bin/env python3
"""Regression test for cscpt/clint.py's ALWAYS-RED rewrite.

WHY this test exists (coding.md: "a fix without its test is unfinished").
clint.py used to tier its verdicts: the FIRST chat-prose breach under a given
user prompt blocked (exit 2), every later breach under that same prompt was
downgraded to a log-only "yellow" by a ledger read back from clint's own log.
The owner reversed that: EVERY breach must block, the ledger and the yellow
tier are gone, and two narrow exemptions were added (the `yn` one-word-answer
override, and the single `DATS` status line that `universal/close.md` mandates
after a #close). This test pins:

  A. the ceiling is really gone -- three successive breaches under ONE promptId
     all exit 2 (under the old ledger, breaches 2 and 3 exited 0);
  B. the loop is still impossible -- a continuation that was itself forced by a
     block never blocks again, via EITHER guard independently, so the two
     guards are proven to work alone and not merely together;
  C. the `yn` exemption, using the three REAL prompts mined from this Mac's own
     transcripts (coding.md: "mine historical/real data for fixtures") --
     including one where ` yn` sits mid-message, not at the end, which is why
     the check is a plain substring and not a trailing match;
  D. the `DATS` exemption's exact boundaries -- the sanctioned one-liner is
     exempt, a 2-line block is not, an 11-word line is not;
  E. harness-authored assistant text (`isApiErrorMessage`) never triggers a
     block, since the model did not write it;
  F. READER mode -- a session whose cwd is exactly the parent `GitHub/` folder
     owes ZERO chat text, so even a declaration glyph blocks there, whilst the
     same line is clean in this repo; and sibling repos under `GitHub/` are NOT
     dragged into that rule;
  G. every fail-safe path still exits 0 (malformed payload, out-of-scope,
     missing transcript).

It drives the REAL registered command from ~/.claude/settings.json
(`python3 .../cscpt/clint.py`, Stop hook) with synthesised payloads and
synthesised transcripts, so the behaviour is proven through the wiring the
harness actually uses, not through imported internals (coding.md: "'exists +
unit-tested' != done -- done only when WIRED and exercised end-to-end").

Self-contained: every transcript is written into a throwaway tempdir at run
time and CLINT_LOG is redirected there, so the real cscpt/.clint.log is
neither read nor polluted. Run directly:

    python3 "cp/ccsim/sandbox/clint_always_red_regression_test.py"

Exits 0 if every case matches its expected verdict, 1 otherwise (per-case
PASS/FAIL on stdout, full diagnostics on any FAIL, and the resulting log lines
printed at the end).
"""
import json
import os
import subprocess
import sys
import tempfile

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.realpath(os.path.join(_THIS_DIR, "..", "..", ".."))
CLINT = os.path.join(REPO_ROOT, "cscpt", "clint.py")

# The Reader session's working directory: this repo's immediate parent. Its own
# CLAUDE.md mandates zero chat text, hence clint's stricter second rule.
READER_CWD = os.path.dirname(REPO_ROOT)
# A sibling repo under the same parent -- must NOT inherit the Reader rule.
SIBLING_CWD = os.path.join(READER_CWD, "AJAP_repo")

_RESULTS = []


def _record(label, ok, detail=None):
    print("[%s] %s" % ("PASS" if ok else "FAIL", label))
    if not ok and detail is not None:
        print("        %s" % detail)
    _RESULTS.append(ok)
    return ok


# --- fixture builders ------------------------------------------------------
# Transcript line shapes copied from real captured transcripts on this Mac
# (keys verified live: user lines carry `promptId`/`isMeta`, the harness's
# post-block injection is a `type:"user"`, `isMeta:true` line whose content
# starts with "Stop hook feedback:").

def _user(text, pid="pid-A"):
    return {"type": "user", "isSidechain": False, "promptId": pid,
            "message": {"role": "user", "content": text}}


def _stop_feedback(pid="pid-A"):
    """The harness's own continuation line after a Stop hook blocked."""
    return {"type": "user", "isSidechain": False, "promptId": pid,
            "isMeta": True,
            "message": {"role": "user", "content":
                        "Stop hook feedback:\n[clint.py]: Chat-prose breach"}}


def _assistant(text, api_error=False):
    o = {"type": "assistant", "isSidechain": False,
         "message": {"role": "assistant",
                     "content": [{"type": "text", "text": text}]}}
    if api_error:
        o["isApiErrorMessage"] = True
    return o


def _write_transcript(path, objs):
    with open(path, "w", encoding="utf-8") as fh:
        for o in objs:
            fh.write(json.dumps(o) + "\n")
    return path


def _payload(transcript_path, cwd=REPO_ROOT, stop_hook_active=False,
             sid="clinttest"):
    """Exact Stop-payload key set as captured live this session."""
    return {"session_id": sid, "transcript_path": transcript_path,
            "prompt_id": "pid-A", "permission_mode": "default",
            "hook_event_name": "Stop", "stop_hook_active": stop_hook_active,
            "cwd": cwd}


def _run(payload, log_path, raw=None):
    """Invoke clint exactly as settings.json does; return (exit, last_log)."""
    before = _log_lines(log_path)
    stdin = raw if raw is not None else json.dumps(payload)
    r = subprocess.run([sys.executable, CLINT], input=stdin,
                       capture_output=True, text=True,
                       env=dict(os.environ, CLINT_LOG=log_path))
    after = _log_lines(log_path)
    new = after[len(before):]
    return r.returncode, (new[-1] if new else ""), r.stderr


def _log_lines(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return [ln for ln in fh.read().splitlines() if ln.strip()]
    except OSError:
        return []


def _action(log_line):
    for f in log_line.split("\t"):
        if f.startswith("action="):
            return f[len("action="):]
    return "<none>"


def _family(action):
    """Tag family —— the part before the ':' qualifier.

    clint's log tags carry a granular class suffix (`block:prose`,
    `block:warn_words`, `exempt:sic`, ...) so a breach can be audited by REASON.
    A test that asserts the family (`block`) stays correct as new classes are
    added; a test that needs one specific class simply passes the full tag and
    still gets exact matching. Comparing families never blurs the outcomes that
    matter —— `block`, `exempt`, `clean` and `out_of_scope` remain distinct.
    """
    return action.split(":", 1)[0]


def _check(label, got, want_exit, want_action):
    code, line, _ = got
    got_action = _action(line)
    if ":" in want_action:          # caller asked for one exact class
        action_ok = got_action == want_action
    else:                           # caller asked for the family
        action_ok = _family(got_action) == want_action
    ok = (code == want_exit and action_ok)
    return _record("%s -> exit %d, action=%s" % (label, want_exit, want_action),
                   ok, "got exit=%s action=%s line=%r"
                   % (code, got_action, line))


# --- A. the once-per-prompt ceiling is gone --------------------------------

def section_always_red(tmp):
    print("\n--- A. RED always: 3 breaches, ONE promptId, all must block ---")
    log = os.path.join(tmp, "A.log")
    tp = os.path.join(tmp, "A.jsonl")
    objs = [_user("do the thing", pid="pid-SAME")]
    for n in (1, 2, 3):
        objs.append(_assistant("Breach %d: unauthorised chat prose." % n))
        _write_transcript(tp, objs)
        _check("breach %d (same pid, ledger would have downgraded 2 and 3)" % n,
               _run(_payload(tp), log), 2, "block")
    # And the stderr the model actually receives must never name a glyph:
    _, _, err = _run(_payload(tp), log)
    _record("stderr stays glyph-free (cannot teach which prefixes pass)",
            err.strip() != "" and not any(g in err for g in
                                          ("✅", "⇠", "➡",
                                           "⚠", "\U0001f6a8")),
            "stderr=%r" % err)


# --- B. the loop is still impossible ---------------------------------------

def section_loop_guard(tmp):
    print("\n--- B. loop guard: each signal must withhold the block ALONE ---")
    log = os.path.join(tmp, "B.log")

    # (a) payload flag alone: no feedback line in the transcript at all.
    tp = os.path.join(tmp, "B1.jsonl")
    _write_transcript(tp, [_user("go"), _assistant("More prose in the retry.")])
    _check("guard (a) stop_hook_active alone",
           _run(_payload(tp, stop_hook_active=True), log), 0, "loop_guard")

    # (b) transcript marker alone: stop_hook_active FALSE, as it would be if
    # the harness ever omitted the field -- the case that used to rely purely
    # on the deleted ledger.
    tp2 = os.path.join(tmp, "B2.jsonl")
    _write_transcript(tp2, [_user("go"), _assistant("First breach."),
                            _stop_feedback(),
                            _assistant("Still prose after being blocked.")])
    _check("guard (b) injected feedback line alone (flag false)",
           _run(_payload(tp2, stop_hook_active=False), log), 0, "loop_guard")

    # A human merely QUOTING the phrase must not be able to buy immunity.
    tp3 = os.path.join(tmp, "B3.jsonl")
    _write_transcript(tp3, [_user("Stop hook feedback: is what I want to discuss"),
                            _assistant("Sure, here is prose about it.")])
    _check("a human message quoting the marker is NOT a continuation",
           _run(_payload(tp3), log), 2, "block")

    # (b)'s one real gap, named in the docstring: a system wrapper appended
    # AFTER the feedback line displaces it as the scan boundary. Guard (a)
    # must still hold, which is why both guards are kept.
    tp4 = os.path.join(tmp, "B4.jsonl")
    _write_transcript(tp4, [_user("go"), _assistant("First breach."),
                            _stop_feedback(),
                            {"type": "user", "isSidechain": False,
                             "promptId": "pid-A",
                             "message": {"role": "user",
                                         "content": "<task-notification>done"}},
                            _assistant("Prose after the wrapper.")])
    _check("known wrapper after the feedback line: (b) still holds",
           _run(_payload(tp4, stop_hook_active=False), log), 0, "loop_guard")
    _check("UNKNOWN wrapper displaces (b) -- guard (a) must cover it",
           _run(_payload(tp4, stop_hook_active=True), log), 0, "loop_guard")

    # A NEW human prompt re-arms the block: the guard is per continuation
    # chain, never a per-prompt ceiling (that ledger is gone).
    tp5 = os.path.join(tmp, "B5.jsonl")
    _write_transcript(tp5, [_user("go", pid="pid-1"),
                            _assistant("First breach."), _stop_feedback("pid-1"),
                            _assistant("Second breach, guarded."),
                            _user("next thing please", pid="pid-2"),
                            _assistant("Fresh prose under a new prompt.")])
    _check("a new human prompt re-arms the block",
           _run(_payload(tp5, stop_hook_active=False), log), 2, "block")


# --- C. the `yn` exemption, on real mined prompts ---------------------------

def section_yn(tmp):
    print("\n--- C. ` yn` override exempts the turn (real mined prompts) ---")
    log = os.path.join(tmp, "C.log")
    # Verbatim from this Mac's own transcripts.
    real = [
        ("mid-message ` yn`, two instruction lines after it",
         "Was your last turn fully completed? yn\nIf yes, stop & do nothing\n"
         "If no, continue then update the `response_`"),
        ("trailing ` yn` after a multi-line brief",
         "FYI: i've enriched `nscpt/` with zsh/terminal commands that were "
         "originally saved in my Apple Notes; NO NEED to read them\n"
         "tell if noted yn"),
        ("trailing ` yn` after a quoted project name",
         'trying to test out Claude Design (CD)\ntell if you can access the CD '
         'project namely "Tall Poppy Syndrome research recruitment" yn'),
    ]
    for i, (label, prompt) in enumerate(real):
        tp = os.path.join(tmp, "C%d.jsonl" % i)
        # "Yes" is the exact one-word reply the log shows really being blocked
        # before this exemption existed.
        _write_transcript(tp, [_user(prompt), _assistant("Yes")])
        _check("yn: %s" % label, _run(_payload(tp), log), 0, "exempt:yn")

    # The leading space is load-bearing: a word merely ENDING in "yn" is not
    # the override and must still be policed.
    tp = os.path.join(tmp, "Cneg.jsonl")
    _write_transcript(tp, [_user("Tell me about Brooklyn and synergy"),
                           _assistant("Brooklyn is a borough of New York.")])
    _check("`Brooklyn`/`synergy` do NOT count as the override",
           _run(_payload(tp), log), 2, "block")


# --- D. the `DATS` exemption's exact boundaries ----------------------------

def section_dats(tmp):
    print("\n--- D. single sanctioned `DATS` status line is exempt ---")
    log = os.path.join(tmp, "D.log")

    cases = [
        ("sanctioned exact form (5 words)", "DATS done. Fixed 3 file(s).",
         0, "exempt:dats"),
        ("sanctioned variable form at the 10-word ceiling",
         "DATS incomplete. One two three four five six seven eight.",
         0, "exempt:dats"),
        ("11 words -- one over the ceiling, no longer that protocol line",
         "DATS incomplete. One two three four five six seven eight nine.",
         2, "block"),
    ]
    for i, (label, text, want_exit, want_action) in enumerate(cases):
        tp = os.path.join(tmp, "D%d.jsonl" % i)
        _write_transcript(tp, [_user("#close"), _assistant(text)])
        _check("DATS: %s" % label, _run(_payload(tp), log),
               want_exit, want_action)

    # 2-line DATS block: the mandated line plus anything else is prose again.
    tp = os.path.join(tmp, "Dmulti.jsonl")
    _write_transcript(tp, [_user("#close"),
                           _assistant("DATS done. Fixed 3 file(s).\n"
                                      "DATS also stamped the close file.")])
    _check("DATS: 2-line block is NOT exempt", _run(_payload(tp), log),
           2, "block")

    # A declaration batch AROUND the DATS line must not defeat the exemption:
    # glyph lines and blanks never enter the offending set in the first place.
    tp = os.path.join(tmp, "Dbatch.jsonl")
    _write_transcript(tp, [_user("#close"),
                           _assistant("✅ `universal/close.md`\n"
                                      "➡️ `202607/close_202607262230.md`\n"
                                      "\nDATS done. Fixed 2 file(s).")])
    _check("DATS: exemption survives a real declaration batch above it",
           _run(_payload(tp), log), 0, "exempt:dats")


# --- E. harness-authored assistant text ------------------------------------

def section_api_error(tmp):
    print("\n--- E. CLI-authored assistant lines are not the model's prose ---")
    log = os.path.join(tmp, "E.log")
    tp = os.path.join(tmp, "E.jsonl")
    # Verbatim shape captured from a real transcript.
    _write_transcript(tp, [
        _user("do the thing"),
        _assistant("✅ `cscpt/clint.py`"),
        _assistant("You've hit your session limit · resets 11:40am "
                   "(Australia/Sydney)", api_error=True)])
    _check("usage-limit line does not block the model for text it never wrote",
           _run(_payload(tp), log), 0, "clean")


# --- F. READER mode ---------------------------------------------------------

def section_reader(tmp):
    print("\n--- F. READER mode (parent GitHub/ folder): zero chat text ---")
    log = os.path.join(tmp, "F.log")
    tp = os.path.join(tmp, "F.jsonl")
    # A real Reader breach, verbatim from that project's own transcripts: the
    # declaration glyphs it emits are permitted HERE but forbidden THERE.
    _write_transcript(tp, [
        _user("response_202607092157.md"),
        _assistant("✅ `dupbus-ceztuc-7cufVe/universal/ww.md`\n"
                   "⇠ `202607/response_202607092157.md`")])
    _check("declaration glyphs block in the Reader session",
           _run(_payload(tp, cwd=READER_CWD), log), 2, "block")
    _check("the very same lines are clean in THIS repo",
           _run(_payload(tp, cwd=REPO_ROOT), log), 0, "clean")

    # Real Reader prose, verbatim.
    tp2 = os.path.join(tmp, "F2.jsonl")
    _write_transcript(tp2, [_user("ww it"),
                            _assistant("Reading instructions for #ww workflow.")])
    _check("Reader prose blocks", _run(_payload(tp2, cwd=READER_CWD), log),
           2, "block")

    # A genuinely silent Reader turn (tool calls only, no text block).
    tp3 = os.path.join(tmp, "F3.jsonl")
    _write_transcript(tp3, [_user("ww it"), _assistant("   \n\n")])
    _check("a silent Reader turn is clean",
           _run(_payload(tp3, cwd=READER_CWD), log), 0, "clean")

    # The exemptions are repo-only: the Reader owes silence NO MATTER WHAT.
    tp4 = os.path.join(tmp, "F4.jsonl")
    _write_transcript(tp4, [_user("did you read it yn"), _assistant("Yes")])
    _check("`yn` does NOT exempt the Reader",
           _run(_payload(tp4, cwd=READER_CWD), log), 2, "block")

    # Sub-path of the Reader folder that is a DIFFERENT repo -> not policed.
    _check("a sibling repo under GitHub/ is out of scope, not Reader-policed",
           _run(_payload(tp2, cwd=SIBLING_CWD), log), 0, "out_of_scope")

    # A sub-path of THIS repo stays repo mode (exact-match is Reader-only).
    _check("a sub-path of this repo is still repo mode",
           _run(_payload(tp, cwd=os.path.join(REPO_ROOT, "cp", "ccsim")), log),
           0, "clean")


# --- G. fail-safes ----------------------------------------------------------

def section_failsafe(tmp):
    print("\n--- G. fail-safe paths: never break a turn ---")
    log = os.path.join(tmp, "G.log")
    tp = os.path.join(tmp, "G.jsonl")
    _write_transcript(tp, [_user("go"), _assistant("✅ `cscpt/clint.py`")])

    _check("clean turn (declarations only)", _run(_payload(tp), log), 0, "clean")
    _check("out-of-scope project", _run(_payload(tp, cwd="/tmp/some-other-repo"),
                                        log), 0, "out_of_scope")
    _check("malformed payload (not JSON)",
           _run(None, log, raw="{not json at all"), 0, "no_stdin")
    _check("valid JSON but not an object",
           _run(None, log, raw='["a", "list"]'), 0, "no_stdin")
    _check("missing transcript file",
           _run(_payload(os.path.join(tmp, "nope.jsonl")), log),
           0, "no_transcript")

    # Empty stdin -- the shape a mis-wired harness would send.
    _check("empty stdin", _run(None, log, raw=""), 0, "no_stdin")


def main():
    print("clint.py ALWAYS-RED regression test")
    print("target: %s" % CLINT)
    with tempfile.TemporaryDirectory(prefix="clint-red-") as tmp:
        section_always_red(tmp)
        section_loop_guard(tmp)
        section_yn(tmp)
        section_dats(tmp)
        section_api_error(tmp)
        section_reader(tmp)
        section_failsafe(tmp)

        print("\n--- resulting log lines (all sections, in order) ---")
        for name in sorted(os.listdir(tmp)):
            if not name.endswith(".log"):
                continue
            for ln in _log_lines(os.path.join(tmp, name)):
                # Drop the leading timestamp so the output is stable to read.
                print("  " + ln.split("\t", 1)[1])

    total, passed = len(_RESULTS), sum(1 for r in _RESULTS if r)
    print("\n%d/%d passed" % (passed, total))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
