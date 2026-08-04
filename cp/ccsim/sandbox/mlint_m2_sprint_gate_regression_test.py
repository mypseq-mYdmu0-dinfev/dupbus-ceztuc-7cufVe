#!/usr/bin/env python3
"""Regression suite for `cscpt/mlint.py` —— the Stop hook that blocks a turn
ending on `#m2`'s INTERIM declaration when the `#sprint` never ran.

WHY THIS SUITE EXISTS, in one paragraph so it is never mistaken for boilerplate.
`universal/m2.md` orders: write a `response_` of first thoughts, commit + push +
declare THAT FILE ALONE, then `#sprint` the real work, then update the
`response_` and declare the real TEA3. Agents repeatedly emitted the interim
declaration as the LAST content of a message and stopped —— because chat text as
a message's final content ends the turn, and root `CLAUDE.md` §3.1.7.5 trains
that exact shape as "turn over" everywhere else. Each occurrence cost the owner
a manual `continue`. `mlint.py` blocks that stop once; this suite pins the exact
failing scenario against the day someone "simplifies" a signal.

REAL DATA, NOT SYNTHETIC. `mlint_incident_fixture.jsonl` beside this file is a
genuine slice of the transcript of the 202608041846 incident (main-agent records
only, large tool results trimmed to `[trimmed]`, thinking blocks dropped): the
`career_query_202608041846.md` read, the `universal/m2.md` read, the
`response_` write, the commit, and the final message whose entire content was
the declaration `➡️ **`202608/career_response_202608041846.md`**`. Test 1 is
that turn, replayed byte-for-byte. Every other transcript case is that same
fixture with ONE record added or changed, so each test isolates exactly one
signal.

THE TWO HALVES OF THE FIX. `mlint.py` is the mechanical half; `universal/m2.md`
carries the instruction half (emit the interim declaration in the SAME message
as the next tool call). Both are pinned here —— the file half is what makes this
suite fail against the pre-change state even where the hook is concerned only
with behaviour.

WIRING IS A SEPARATE CLAIM FROM CORRECTNESS (`cp/ccsim/CLAUDE.md` §8.5): the
final group of checks reads the LIVE `~/.claude/settings.json` and asserts mlint
is registered there and that the path still resolves. A hook that passes every
behavioural test and is not registered does precisely nothing, which is the
failure this repo has already lived through once.

Run: `python3 cp/ccsim/sandbox/mlint_m2_sprint_gate_regression_test.py`
Exit 0 = every check passed.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MLINT = os.path.join(REPO, "cscpt", "mlint.py")
M2_MD = os.path.join(REPO, "universal", "m2.md")
FIXTURE = os.path.join(HERE, "mlint_incident_fixture.jsonl")
SETTINGS = os.path.expanduser("~/.claude/settings.json")

# Real paths from the incident, reused so the fixtures stay faithful.
Q_REAL = os.path.join(REPO, "sessions", "2026", "202608",
                      "career_query_202608041846.md")
Q_DISCUSSION = os.path.join(REPO, "sessions", "queued_queries",
                            "ccsim_query_202608042035.md")
SPRINT_MD = os.path.join(REPO, "universal", "sprint.md")
M2_READ = {"file_path": M2_MD}

failures = []
checks = 0


def check(ok, label, detail=""):
    global checks
    checks += 1
    if ok:
        print("[PASS] %s" % label)
    else:
        print("[FAIL] %s —— %s" % (label, detail))
        failures.append(label)


# ---------------------------------------------------------------------------
# Transcript helpers —— every case is the real fixture plus/minus ONE record.
# ---------------------------------------------------------------------------

def fixture_records():
    out = []
    with open(FIXTURE, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if raw:
                out.append(json.loads(raw))
    return out


def assistant_tool(name, inp, sidechain=False):
    rec = {"type": "assistant", "isSidechain": sidechain,
           "message": {"role": "assistant",
                       "content": [{"type": "tool_use", "id": "t-x",
                                    "name": name, "input": inp}]}}
    return rec


def assistant_text(text, sidechain=False, api_error=False):
    rec = {"type": "assistant", "isSidechain": sidechain,
           "message": {"role": "assistant",
                       "content": [{"type": "text", "text": text}]}}
    if api_error:
        rec["isApiErrorMessage"] = True
    return rec


def user_msg(text, pid="ef515fb4-9324-4dbc-9550-a278b9e9217b"):
    return {"type": "user", "isSidechain": False, "promptId": pid,
            "message": {"role": "user", "content": text}}


def insert_before_final_text(records, extra):
    """Put `extra` immediately before the turn's final declaration message, so
    the declaration stays the last thing in the turn (the failure shape) whilst
    the new signal sits inside the window."""
    out = list(records)
    for i in range(len(out) - 1, -1, -1):
        if out[i].get("type") == "assistant":
            return out[:i] + list(extra) + out[i:]
    return out + list(extra)


def replace_final_text(records, text):
    out = list(records)
    for i in range(len(out) - 1, -1, -1):
        if out[i].get("type") == "assistant":
            out[i] = assistant_text(text)
            return out
    return out


def run(records, cwd=REPO, stop_hook_active=False, log=None, session="testsess",
        transcript=True):
    """Run mlint over a transcript built from `records`. Returns
    (exit_code, stderr, log_lines)."""
    tmpdir = tempfile.mkdtemp(prefix="mlint_test_")
    try:
        tpath = os.path.join(tmpdir, "t.jsonl")
        if transcript:
            with open(tpath, "w", encoding="utf-8") as fh:
                for r in records:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        logpath = log or os.path.join(tmpdir, "mlint.log")
        payload = {"session_id": session, "transcript_path": tpath,
                   "cwd": cwd, "hook_event_name": "Stop"}
        if stop_hook_active:
            payload["stop_hook_active"] = True
        env = dict(os.environ, MLINT_LOG=logpath)
        proc = subprocess.run([sys.executable, MLINT],
                              input=json.dumps(payload), text=True,
                              capture_output=True, env=env, cwd="/")
        lines = []
        if os.path.exists(logpath):
            with open(logpath, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        return proc.returncode, proc.stderr, lines
    finally:
        if not log:
            shutil.rmtree(tmpdir, ignore_errors=True)
        else:
            shutil.rmtree(tmpdir, ignore_errors=True)


def action_of(lines):
    if not lines:
        return "<no log line>"
    m = re.search(r"\taction=([^\t]+)", lines[-1])
    return m.group(1) if m else "<unparsed>"


# ---------------------------------------------------------------------------
# 0. Preconditions
# ---------------------------------------------------------------------------

def test_preconditions():
    check(os.path.isfile(MLINT), "cscpt/mlint.py exists",
          "the Stop hook has not been created")
    check(os.path.isfile(FIXTURE), "real-incident fixture present",
          "mlint_incident_fixture.jsonl missing")
    check(os.path.isfile(Q_REAL),
          "incident query file still on disk (m2 evidence source)",
          "%s missing —— fixture case 1 would fail open" % Q_REAL)


# ---------------------------------------------------------------------------
# 1. THE FAILING SCENARIO —— must be caught
# ---------------------------------------------------------------------------

def test_real_incident_is_blocked():
    recs = fixture_records()
    code, err, lines = run(recs)
    check(code == 2, "REAL incident turn is BLOCKED (exit 2)",
          "exit=%d action=%s" % (code, action_of(lines)))
    check("m2" in err.lower() and "sprint" in err.lower(),
          "block message names m2 and the sprint", repr(err[:120]))
    check("lone `.`" in err,
          "block message names the lone-dot escape for a wrong verdict",
          repr(err[:200]))
    check(action_of(lines) == "block", "block is recorded in the log",
          action_of(lines))
    check("\tm2=query\t" in (lines[-1] if lines else ""),
          "m2 evidence came from the query FILE, not the typed message",
          lines[-1] if lines else "")


def test_typed_m2_is_blocked():
    """The other m2 source: the user typing `#m2` directly (root §3.6.1)."""
    recs = fixture_records()
    recs[0] = user_msg("do the thing below, then\n#m2")
    code, err, lines = run(recs)
    check(code == 2, "typed line-start #m2 is BLOCKED", "exit=%d" % code)
    check("\tm2=typed\t" in (lines[-1] if lines else ""),
          "m2 evidence attributed to the typed message",
          lines[-1] if lines else "")


# ---------------------------------------------------------------------------
# 2. SPRINT EVIDENCE —— each signal independently lets the turn end
# ---------------------------------------------------------------------------

def test_slog_write_lets_it_pass():
    recs = insert_before_final_text(fixture_records(), [
        assistant_tool("Edit", {"file_path": os.path.join(
            REPO, "sessions", "2026", "202608",
            "career_slog_202608042032.md")})])
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "sprint_ran",
          "a slog_ write lets the turn end",
          "exit=%d action=%s" % (code, action_of(lines)))
    check("\tsprint=slog\t" in (lines[-1] if lines else ""),
          "slog recorded as the sprint signal", lines[-1] if lines else "")


def test_sprint_md_read_lets_it_pass():
    recs = insert_before_final_text(fixture_records(), [
        assistant_tool("Read", {"file_path": SPRINT_MD})])
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "sprint_ran",
          "a universal/sprint.md read lets the turn end",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_agent_dispatch_lets_it_pass():
    recs = insert_before_final_text(fixture_records(), [
        assistant_tool("Agent", {"description": "sprint SA"})])
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "sprint_ran",
          "an Agent dispatch lets the turn end",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_taskupdate_is_not_a_dispatch():
    """THE TRAP: `TaskUpdate` is a TODO tool that appears all over ordinary
    turns —— matching it by prefix would disarm this hook almost everywhere.
    Observed 9 times in the incident session's own legitimate turn."""
    recs = insert_before_final_text(fixture_records(), [
        assistant_tool("TaskUpdate", {"taskId": "x"})])
    code, _, lines = run(recs)
    check(code == 2, "TaskUpdate is NOT sprint evidence —— still blocked",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_slog_beats_other_signals():
    recs = insert_before_final_text(fixture_records(), [
        assistant_tool("Read", {"file_path": SPRINT_MD}),
        assistant_tool("Write", {"file_path": os.path.join(
            REPO, "sessions", "2026", "202608", "ccsim_slog_202608012011.md")})])
    _, _, lines = run(recs)
    check("\tsprint=slog\t" in (lines[-1] if lines else ""),
          "slog outranks sprint_md in the recorded reason",
          lines[-1] if lines else "")


# ---------------------------------------------------------------------------
# 3. M2 PRECISION —— discussion of #m2 must never arm the hook
# ---------------------------------------------------------------------------

def test_backticked_m2_is_not_an_invocation():
    """The real incident WRITE-UP (`queued_queries/ccsim_query_202608042035.md`)
    is itself a `query_[TS].md` file that mentions `#m2` four times —— every one
    backticked and inline. A CCSIM session reading it must not be blocked."""
    recs = fixture_records()
    recs = [r for r in recs if not _reads(r, Q_REAL)]
    recs = insert_before_final_text(recs, [
        assistant_tool("Read", {"file_path": Q_DISCUSSION})])
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "no_m2",
          "backticked #m2 in a query file is NOT an invocation",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_reading_m2_md_is_not_an_invocation():
    """The signal a maintenance session would trip on. m2.md carries no
    line-start `#m2`, and it is not a `query_` file either."""
    recs = fixture_records()
    recs = [r for r in recs if not _reads(r, Q_REAL)]
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "no_m2",
          "reading universal/m2.md alone is NOT an m2 invocation",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_fenced_m2_is_not_an_invocation():
    recs = fixture_records()
    recs[0] = user_msg("see the snippet:\n```\n#m2\n```\nthat is all")
    recs = [r for r in recs if not _reads(r, Q_REAL)]
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "no_m2",
          "#m2 inside a fenced block is NOT an invocation",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_midline_m2_is_not_an_invocation():
    recs = fixture_records()
    recs[0] = user_msg("remind me what #m2 does")
    recs = [r for r in recs if not _reads(r, Q_REAL)]
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "no_m2",
          "mid-line #m2 in prose is NOT an invocation",
          "exit=%d action=%s" % (code, action_of(lines)))


def _reads(rec, path):
    try:
        for b in (rec.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                if (b.get("input") or {}).get("file_path") == path:
                    return True
    except Exception:
        pass
    return False


# ---------------------------------------------------------------------------
# 4. TURN-SHAPE —— only the observed failure shape fires
# ---------------------------------------------------------------------------

def test_blocker_declaration_end_is_left_alone():
    recs = replace_final_text(fixture_records(), "⚠️ Contract PDF unreadable")
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "not_declaration_end",
          "a turn ending on a ⚠️ blocker is NOT held open",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_sentinel_end_is_left_alone():
    recs = replace_final_text(fixture_records(),
                             "🚨 Compaction Detected —— stopped all tasks.")
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "not_declaration_end",
          "a turn ending on the compaction sentinel is NOT held open",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_lone_dot_end_is_left_alone():
    recs = replace_final_text(fixture_records(), ".")
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "not_declaration_end",
          "a turn ending on the sanctioned lone dot is NOT held open",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_api_error_line_is_not_the_turns_last_word():
    """`isApiErrorMessage` lines are CLI-authored ("You've hit your session
    limit"), and one landed immediately after the real stall. Judging the model
    on text it never wrote would be wrong exactly when it can least comply ——
    here the declaration beneath it must still be seen."""
    recs = fixture_records() + [
        assistant_text("You've hit your session limit · resets 8:30pm",
                       api_error=True)]
    code, _, lines = run(recs)
    check(code == 2, "a CLI session-limit line does not mask the declaration",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_bold_wrapped_declaration_is_recognised():
    recs = replace_final_text(fixture_records(),
                             "**➡️ `202608/career_response_202608041846.md`**")
    code, _, _ = run(recs)
    check(code == 2, "a bold-wrapped declaration is still a declaration",
          "exit=%d" % code)


# ---------------------------------------------------------------------------
# 5. LOOP GUARDS —— never twice for one prompt
# ---------------------------------------------------------------------------

def test_stop_hook_active_disarms():
    code, _, lines = run(fixture_records(), stop_hook_active=True)
    check(code == 0 and action_of(lines) == "loop_guard",
          "stop_hook_active disarms the block (guard 1)",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_never_blocks_twice_for_one_prompt():
    tmpdir = tempfile.mkdtemp(prefix="mlint_ledger_")
    try:
        log = os.path.join(tmpdir, "mlint.log")
        first, _, _ = run(fixture_records(), log=log)
        second, _, lines = run(fixture_records(), log=log)
        check(first == 2 and second == 0,
              "the same prompt is blocked once, never twice (guard 2)",
              "first=%d second=%d action=%s" % (first, second, action_of(lines)))
        check(action_of(lines) == "already_blocked",
              "the second pass logs already_blocked", action_of(lines))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_new_prompt_is_blockable_again():
    tmpdir = tempfile.mkdtemp(prefix="mlint_ledger2_")
    try:
        log = os.path.join(tmpdir, "mlint.log")
        run(fixture_records(), log=log)
        recs = fixture_records()
        recs[0] = user_msg("career_query_202608041846.md", pid="different-pid")
        for r in recs:
            if r.get("type") == "user":
                r["promptId"] = "different-pid"
        code, _, _ = run(recs, log=log)
        check(code == 2, "a NEW prompt id is blockable again",
              "exit=%d" % code)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_unreadable_ledger_refuses_to_block():
    """No ledger, no guarantee the block would be the first —— and repeating a
    block is worse than missing one, so it declines."""
    tmpdir = tempfile.mkdtemp(prefix="mlint_badlog_")
    try:
        log = os.path.join(tmpdir, "nodir", "mlint.log")   # unwritable path
        code, _, _ = run(fixture_records(), log=log)
        check(code == 0, "an unwritable log means NO block (fail open)",
              "exit=%d" % code)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_override_disarms():
    recs = fixture_records()
    recs[0] = user_msg("career_query_202608041846.md —— override for this turn")
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "exempt:override",
          "the word override disarms the hook",
          "exit=%d action=%s" % (code, action_of(lines)))


# ---------------------------------------------------------------------------
# 6. FAIL OPEN, NEVER SILENTLY
# ---------------------------------------------------------------------------

def test_out_of_scope_repo():
    code, _, lines = run(fixture_records(), cwd="/tmp")
    check(code == 0 and action_of(lines) == "out_of_scope",
          "another repo is never policed",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_reader_folder_is_out_of_scope():
    code, _, lines = run(fixture_records(), cwd=os.path.dirname(REPO))
    check(code == 0 and action_of(lines) == "out_of_scope",
          "the parent Reader folder is out of scope",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_missing_transcript():
    code, _, lines = run(fixture_records(), transcript=False)
    check(code == 0 and action_of(lines) == "no_transcript",
          "a missing transcript fails open and says so",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_bad_stdin():
    tmpdir = tempfile.mkdtemp(prefix="mlint_stdin_")
    try:
        log = os.path.join(tmpdir, "mlint.log")
        proc = subprocess.run([sys.executable, MLINT], input="not json",
                              text=True, capture_output=True,
                              env=dict(os.environ, MLINT_LOG=log), cwd="/")
        lines = open(log, encoding="utf-8").read().splitlines() \
            if os.path.exists(log) else []
        check(proc.returncode == 0 and action_of(lines) == "no_stdin",
              "a malformed payload fails open and says so",
              "exit=%d action=%s" % (proc.returncode, action_of(lines)))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_empty_transcript():
    code, _, lines = run([])
    check(code == 0 and action_of(lines) == "empty_transcript",
          "an empty transcript fails open and says so",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_midturn_user_message_fails_open():
    """Documented, accepted gap: a mid-turn user message (root §3.1.7.6.1 says
    the turn has NOT ended) moves the window boundary past the m2 evidence.
    Pinned so the fail-open direction is a decision, not a surprise."""
    recs = insert_before_final_text(fixture_records(),
                                   [user_msg("QMM", pid="mid-turn")])
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "no_m2",
          "a mid-turn user message fails OPEN (known, accepted gap)",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_subagent_records_are_ignored():
    """An SA reading the query file is not the main turn's evidence."""
    recs = fixture_records()
    recs = [r for r in recs if not _reads(r, Q_REAL)]
    recs = insert_before_final_text(recs, [
        assistant_tool("Read", {"file_path": Q_REAL}, sidechain=True)])
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "no_m2",
          "a sub-agent's own reads are not main-turn evidence",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_every_run_logs_exactly_one_line():
    """A breach-only log cannot tell 'ran and found nothing' from 'never
    invoked' —— the ambiguity that hid dead wiring here for weeks."""
    for label, recs, kw in (
            ("blocked", fixture_records(), {}),
            ("clean", insert_before_final_text(
                fixture_records(),
                [assistant_tool("Read", {"file_path": SPRINT_MD})]), {}),
            ("out of scope", fixture_records(), {"cwd": "/tmp"})):
        _, _, lines = run(recs, **kw)
        check(len(lines) == 1, "exactly one log line per invocation (%s)" % label,
              "got %d" % len(lines))


# ---------------------------------------------------------------------------
# 7. THE INSTRUCTION HALF —— universal/m2.md
# ---------------------------------------------------------------------------

def test_m2_md_carries_the_same_message_rule():
    text = open(M2_MD, encoding="utf-8").read()
    lowered = text.lower()
    check("same message" in lowered,
          "m2.md tells CC to emit the interim declaration in the SAME message",
          "the instruction half of the fix is missing —— it was deleted once "
          "before and the stalls continued")
    check("tool call" in lowered,
          "m2.md names the next TOOL CALL as what must accompany it",
          "an instruction that does not say what to attach is not actionable")
    check(text.count("\n") < 40,
          "m2.md stays terse (<40 lines)",
          "the owner watches this file's growth; %d lines" % text.count("\n"))


def test_m2_md_carries_the_reading_load_rule():
    """The same failure class seen from the other end: the file is correct and
    the READER's cost was never considered. The owner's worked case —— a
    `response_` of 10 points that the update answers with 10 PARALLEL new ones,
    so he reads all 10 originals before discovering they no longer matter."""
    text = open(M2_MD, encoding="utf-8").read()
    lowered = text.lower()
    check("reading load" in lowered,
          "m2.md states the update goal: cut the USER's reading load",
          "the update bullets read as a menu with no judgement behind them")
    check("supersedes" in lowered or "superseded" in lowered,
          "m2.md says to strike what the update SUPERSEDES, not only what it "
          "contradicts",
          "a superseded point is still read in full before it is discarded")
    check(re.search(r"never a heading", lowered) is not None,
          "m2.md forbids striking a HEADING",
          "a struck heading reads as its whole section being gone, which makes "
          "every later section appear to shift")


# ---------------------------------------------------------------------------
# 8. HEADER CONTRACT + LIVE WIRING
# ---------------------------------------------------------------------------

def test_header_contract():
    lines = open(MLINT, encoding="utf-8").read().splitlines()
    starts = [i for i, l in enumerate(lines) if re.search(r"NON-CCSIM.*start", l)]
    ends = [i for i, l in enumerate(lines) if re.search(r"NON-CCSIM.*end", l)]
    ok = len(starts) == 1 and len(ends) == 1 and starts[0] < ends[0]
    check(ok, "mlint.py: exactly one NON-CCSIM start + one end, in order",
          "starts=%d ends=%d" % (len(starts), len(ends)))
    if ok:
        words = "\n".join(lines[starts[0] + 1:ends[0]]).split()
        check(len(words) <= 100,
              "mlint.py: NON-CCSIM block is %dw (cap 100)" % len(words),
              "%dw over" % (len(words) - 100))


def test_registered_live():
    """WIRING, not correctness (`cp/ccsim/CLAUDE.md` §8.5). Every behavioural
    check above can pass whilst the harness never calls this file once."""
    try:
        with open(SETTINGS, encoding="utf-8") as fh:
            hooks = json.load(fh).get("hooks", {})
    except Exception as exc:
        check(False, "~/.claude/settings.json readable", repr(exc))
        return
    cmds = []
    for group in hooks.get("Stop", []) or []:
        for h in (group.get("hooks") or [group]):
            cmds.append(h.get("command", ""))
    check(any("mlint.py" in c for c in cmds),
          "mlint.py is registered as a Stop hook in ~/.claude/settings.json",
          "registered Stop commands: %s" % (cmds or "<none>"))
    for c in cmds:
        if "mlint.py" in c:
            paths = [t for t in re.findall(r"'([^']+)'|\"([^\"]+)\"|(\S+)", c)]
            flat = [p for tup in paths for p in tup if p and "/" in p]
            check(all(os.path.exists(p) for p in flat),
                  "the registered mlint path resolves (no exit 127)",
                  "missing: %s" % [p for p in flat if not os.path.exists(p)])


def main():
    if not os.path.isfile(MLINT) or not os.path.isfile(FIXTURE):
        test_preconditions()
        test_m2_md_carries_the_same_message_rule()
        test_m2_md_carries_the_reading_load_rule()
    else:
        for fn in (test_preconditions,
                   test_real_incident_is_blocked,
                   test_typed_m2_is_blocked,
                   test_slog_write_lets_it_pass,
                   test_sprint_md_read_lets_it_pass,
                   test_agent_dispatch_lets_it_pass,
                   test_taskupdate_is_not_a_dispatch,
                   test_slog_beats_other_signals,
                   test_backticked_m2_is_not_an_invocation,
                   test_reading_m2_md_is_not_an_invocation,
                   test_fenced_m2_is_not_an_invocation,
                   test_midline_m2_is_not_an_invocation,
                   test_blocker_declaration_end_is_left_alone,
                   test_sentinel_end_is_left_alone,
                   test_lone_dot_end_is_left_alone,
                   test_api_error_line_is_not_the_turns_last_word,
                   test_bold_wrapped_declaration_is_recognised,
                   test_stop_hook_active_disarms,
                   test_never_blocks_twice_for_one_prompt,
                   test_new_prompt_is_blockable_again,
                   test_unreadable_ledger_refuses_to_block,
                   test_override_disarms,
                   test_out_of_scope_repo,
                   test_reader_folder_is_out_of_scope,
                   test_missing_transcript,
                   test_bad_stdin,
                   test_empty_transcript,
                   test_midturn_user_message_fails_open,
                   test_subagent_records_are_ignored,
                   test_every_run_logs_exactly_one_line,
                   test_m2_md_carries_the_same_message_rule,
                   test_m2_md_carries_the_reading_load_rule,
                   test_header_contract,
                   test_registered_live):
            fn()
    print("\n%d/%d checks passed" % (checks - len(failures), checks))
    if failures:
        print("FAILED: %s" % ", ".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
