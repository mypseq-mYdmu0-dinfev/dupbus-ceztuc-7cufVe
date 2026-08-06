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
# The DISCUSSION case is generated, never borrowed from `sessions/`. It used to
# point at a real incident write-up; that file was later voided (`❌_` prefix)
# and the test went on PASSING —— vacuously, because a missing file yields no
# evidence, which is the fail-open direction. A regression test that passes for
# the wrong reason is worse than none, and `universal/coding.md` forbids a
# script depending on a specific comms file precisely because they move.
Q_DISCUSSION_TEXT = (
    "# Incident write-up\n\n"
    "- The session invoked `#m2` and stalled at the interim declaration.\n"
    "- Every mention of `#m2` in this file is inline and backticked.\n"
    "- A fenced example follows:\n\n"
    "```\n#m2 expect 2\n```\n\n"
    "- Nothing here invokes `#m2`.\n")
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


def test_workflow_dispatch_lets_it_pass():
    """LIVE NEAR-MISS, 202608050209: that turn ran its entire sprint through a
    `Workflow` script and no `Agent` call at all, so the original
    `Agent`/`Task`-only set recorded it as sprint=none (confirmed in the real
    `.mlint.log` line for that turn). Had it declared correctly and ended on the
    declaration, this hook would have blocked a turn whose sprint was already
    running —— a WRONG block."""
    recs = insert_before_final_text(fixture_records(), [
        assistant_tool("Workflow", {"script": "export const meta = {}"})])
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "sprint_ran",
          "a Workflow dispatch lets the turn end",
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


def test_taskcreate_is_not_a_dispatch():
    """THE SAME TRAP, one letter away, and the reason `Workflow` was added by
    NAME rather than by widening the match: `TaskCreate` takes
    `{subject, description, activeForm}` —— a to-do entry —— and its text merely
    NARRATES a dispatch ("Dispatch SA(s) to …") whilst dispatching nothing."""
    recs = insert_before_final_text(fixture_records(), [
        assistant_tool("TaskCreate", {"subject": "Dispatch SA(s) to convert",
                                      "description": "Dispatch SA(s) to …",
                                      "activeForm": "Dispatching"})])
    code, _, lines = run(recs)
    check(code == 2, "TaskCreate is NOT sprint evidence —— still blocked",
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
    """An incident WRITE-UP is itself a `query_[TS].md` file that mentions `#m2`
    repeatedly —— every one backticked or fenced. A CCSIM session reading one
    must not be blocked. The file is WRITTEN HERE so the check cannot rot into a
    vacuous pass when a real write-up is archived (see Q_DISCUSSION_TEXT)."""
    tmpdir = tempfile.mkdtemp(prefix="mlint_discussion_")
    try:
        path = os.path.join(tmpdir, "ccsim_query_209912312359.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(Q_DISCUSSION_TEXT)
        check(os.path.isfile(path),
              "the discussion fixture exists (guards a vacuous pass)", path)
        recs = fixture_records()
        recs = [r for r in recs if not _reads(r, Q_REAL)]
        recs = insert_before_final_text(recs, [
            assistant_tool("Read", {"file_path": path})])
        code, _, lines = run(recs)
        check(code == 0 and action_of(lines) == "no_m2",
              "backticked/fenced #m2 in a query file is NOT an invocation",
              "exit=%d action=%s" % (code, action_of(lines)))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


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


def test_lone_dot_end_after_declaring_is_left_alone():
    """Root §3.1.8.2's sanctioned no-op reply, and this hook's OWN escape hatch
    for a wrong verdict —— so it must never be held open once the interim
    declaration has actually landed."""
    recs = insert_before_final_text(fixture_records(), [
        assistant_text("➡️ **`202608/career_response_202608041846.md`**")])
    recs = replace_final_text(recs, ".")
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "not_declaration_end",
          "a lone dot AFTER the declaration landed is NOT held open",
          "exit=%d action=%s" % (code, action_of(lines)))


# ---------------------------------------------------------------------------
# 4b. SHAPE B —— the declaration that was never emitted at all
# ---------------------------------------------------------------------------

def _strip_response_writes(records):
    out = []
    for r in records:
        try:
            blocks = (r.get("message") or {}).get("content") or []
            if any(isinstance(b, dict) and b.get("type") == "tool_use"
                   and "response_" in str((b.get("input") or {}).get(
                       "file_path", "")) for b in blocks):
                continue
        except Exception:
            pass
        out.append(r)
    return out


def test_missing_declaration_is_blocked():
    """THE 202608050209 SHAPE, replayed: the `response_` was written, committed
    and PUSHED, then the next message carried only tool calls and the `➡️` line
    was never typed. The turn ended on a sanctioned lone `.` after dispatching
    its sprint —— an entirely ordinary ENDING, which is why shape A cannot see
    it. Only the ABSENCE of the declaration anywhere in the turn identifies it.
    From the owner's screen a silent push is indistinguishable from a failed
    one, and the file he is meant to click is not clickable."""
    recs = replace_final_text(fixture_records(), ".")
    code, err, lines = run(recs)
    check(code == 2, "a turn that NEVER declared its response_ is BLOCKED",
          "exit=%d action=%s" % (code, action_of(lines)))
    check(action_of(lines) == "block_nodeclare",
          "the missing-declaration block is logged under its own action",
          action_of(lines))
    check("➡️" in err and "alone" in err.lower(),
          "the message asks for the one missing line and nothing else",
          repr(err[:160]))
    check("lone `.`" in err, "it still names the escape for a wrong verdict",
          repr(err[:200]))


def test_missing_declaration_blocks_even_when_the_sprint_ran():
    """Shape B is INDIFFERENT to sprint evidence —— the real turn dispatched its
    whole sprint and still owed the line. Shape A's `sprint_ran` exit must not
    swallow it, which is why shape B is tested FIRST."""
    recs = replace_final_text(fixture_records(), ".")
    recs = insert_before_final_text(recs, [
        assistant_tool("Workflow", {"script": "export const meta = {}"})])
    code, _, lines = run(recs)
    check(code == 2 and action_of(lines) == "block_nodeclare",
          "a running sprint does not excuse the missing declaration",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_no_response_write_means_no_nodeclare_block():
    """The declaration is owed only once the file exists. A turn that wrote no
    `response_` has nothing to declare, so shape B must stay silent."""
    recs = _strip_response_writes(fixture_records())
    recs = replace_final_text(recs, ".")
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "not_declaration_end",
          "no response_ write means no missing-declaration block",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_reading_a_response_is_not_writing_one():
    """Root §4 retrospection opens old `response_` files routinely. A READ must
    never put a turn on the hook —— only a Write/Edit does."""
    recs = _strip_response_writes(fixture_records())
    recs = insert_before_final_text(recs, [
        assistant_tool("Read", {"file_path": os.path.join(
            REPO, "sessions", "2026", "202608",
            "career_response_202608041846.md")})])
    recs = replace_final_text(recs, ".")
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "not_declaration_end",
          "reading an old response_ is not writing one",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_read_declaration_glyph_does_not_satisfy_shape_b():
    """A `✅` read-list is not the owed artefact. The owner cannot click it to
    reach the `response_`, so it must not suppress the block."""
    recs = insert_before_final_text(fixture_records(), [
        assistant_text("✅ `universal/m2.md`, `universal/sprint.md`")])
    recs = replace_final_text(recs, ".")
    code, _, lines = run(recs)
    check(code == 2 and action_of(lines) == "block_nodeclare",
          "a ✅ reads-line does not stand in for the ➡️ declaration",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_harness_terminated_turn_is_not_blocked():
    """A session/usage limit ends the turn FOR the model. Blocking there spends
    the one allowed forced turn on an agent that cannot act —— the `clint.py`
    empty-turn failure in its purest form."""
    recs = replace_final_text(fixture_records(), ".")
    recs = recs + [assistant_text("You've hit your session limit · resets 8:30pm",
                                  api_error=True)]
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "not_declaration_end",
          "a harness-terminated turn is never held open for a declaration",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_sha_declaration_end_is_a_declaration_end():
    """SHAPE A must still fire when the batch ends on the SIXTH declaration
    class, `🦈` (root §3.2.4 —— the turn's commit SHAs, split out of `➡️`).

    THE DEFECT THIS PINS, because it was live: `_is_declaration_end` knew only
    the three I/O glyphs, and §3.1.6.3's batch now ordinarily FINISHES on a
    `🦈` line. So the protocol change silently defeated shape A —— an `#m2`
    turn that wrote its `response_`, declared it, committed, declared the SHA
    and never sprinted logged `not_declaration_end` and was waved through.
    Measured against the real hook: `not_declaration_end` before the fix,
    `block` after. Both the bare and the §3.2.4.5 multi-repo forms are tested,
    since the label form is the one a naive glyph check is likeliest to miss.
    """
    for label, text in (
            ("`🦈` alone", "🦈 `97ae25ba`"),
            ("batch ending on `🦈`",
             "➡️ **`202608/career_response_202608041846.md`**\n🦈 `97ae25ba`"),
            ("multi-repo `🦈` (§3.2.4.5)",
             "➡️ **`202608/career_response_202608041846.md`**\n"
             "🦈 Default: `97ae25ba`\n🦈 AJAP: `470481d8`")):
        recs = replace_final_text(fixture_records(), text)
        code, _, lines = run(recs)
        check(code == 2 and action_of(lines) in ("block", "block_nodeclare"),
              "an m2 stall ending on %s is still caught" % label,
              "exit=%d action=%s" % (code, action_of(lines)))


def test_sha_declaration_alone_does_not_suppress_shape_b():
    """`_is_io_declaration` must NOT learn `🦈`, though `_is_declaration_end`
    did. Its only caller is SHAPE B, where a hit SUPPRESSES the block —— and a
    turn that pushed, declared its SHAs and never declared the `response_` is
    precisely shape B's failure ("a successful push with no declaration looks,
    from the user's screen, exactly like a failed one"). Widening that set
    would delete coverage of the case the new glyph makes MORE likely."""
    recs = replace_final_text(fixture_records(), "🦈 `97ae25ba`")
    code, _, lines = run(recs)
    check(code == 2 and action_of(lines) == "block_nodeclare",
          "a SHA declaration alone does not stand in for the ➡️ declaration",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_urgent_stop_is_not_blocked_for_a_missing_declaration():
    """A `⚠️` blocker (§3.2.5) and the `🚨` sentinel (§3.2.6) are deliberate
    early stops. Holding a blocker open delays exactly the message the user most
    needs to see."""
    for label, text in (("⚠️ blocker", "⚠️ Contract PDF unreadable"),
                        ("🚨 sentinel",
                         "🚨 Compaction Detected —— stopped all tasks.")):
        recs = replace_final_text(fixture_records(), text)
        code, _, lines = run(recs)
        check(code == 0 and action_of(lines) == "not_declaration_end",
              "shape B leaves a %s ending alone" % label,
              "exit=%d action=%s" % (code, action_of(lines)))


def test_one_forced_turn_per_prompt_across_both_shapes():
    """`hook_guide.md` §6.3 budgets ONE extra round trip per prompt. Two shapes
    must share that budget, not have one each."""
    tmpdir = tempfile.mkdtemp(prefix="mlint_shared_")
    try:
        log = os.path.join(tmpdir, "mlint.log")
        first, _, _ = run(replace_final_text(fixture_records(), "."), log=log)
        second, _, lines = run(fixture_records(), log=log)
        check(first == 2 and second == 0,
              "a shape-B block spends the same budget as a shape-A one",
              "first=%d second=%d action=%s" % (first, second,
                                                action_of(lines)))
        check(action_of(lines) == "already_blocked",
              "the second shape logs already_blocked", action_of(lines))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


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
    """⚠️ PIN THE RULE, NOT THE OWNER'S PHRASING. These assertions read literal
    strings out of a file the owner edits BY HAND, and both of them broke that
    way: commit `d51f0004` tightened "SAME message" to "SAME msg" and swapped
    the nesting example's numbers, leaving every rule intact whilst turning the
    suite red. A pin that fails on a synonym is not testing the invariant, it is
    testing the wording —— so each check below accepts the family of phrasings
    that mean the same act, and fails only when the ACT itself goes missing."""
    text = open(M2_MD, encoding="utf-8").read()
    lowered = text.lower()
    check("same message" in lowered or "same msg" in lowered,
          "m2.md tells CC to emit the interim declaration in the SAME message",
          "the instruction half of the fix is missing —— it was deleted once "
          "before and the stalls continued")
    check("tool call" in lowered,
          "m2.md names the next TOOL CALL as what must accompany it",
          "an instruction that does not say what to attach is not actionable")
    check(text.count("\n") < 40,
          "m2.md stays terse (<40 lines)",
          "the owner watches this file's growth; %d lines" % text.count("\n"))
    # The sequencing strengthener the owner asked for: "sequentially" alone left
    # step 3 startable on a half-done step 2. It must read as a COMPLETENESS
    # test, never as a wait —— the removed "Don't proceed..." line was itself
    # diagnosed as a cause of CC stalling after step 2.
    check(re.search(r"1\s*&\s*2\s+both\s+DONE\s+before\s+3", text) is not None,
          "m2.md requires steps 1 & 2 both DONE before 3",
          "the sequencing rule rests on the word 'sequentially' alone")
    check(re.search(r"never pause, never await", text, re.I) is not None,
          "the sequencing rule is paired with an explicit NO-WAIT clause",
          "a completeness check with no no-wait clause reads as a barrier, "
          "which is the exact failure the removed line caused")


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
    # SHAPE, not specific numbers —— see the phrasing warning above. Any worked
    # example of sub-points nesting under their parent satisfies this
    # (`11.4.1/11.4.2/11.4.3` and `2.1/2.2/2.3` are the same lesson); what must
    # never happen is the anti-pattern being shown with no correct form beside it.
    check(re.search(r"\d+\.\d+/\d+\.\d+", text) is not None
          or re.search(r"\d+\.\d+\.\d+/", text) is not None,
          "m2.md shows the CORRECT nesting shape, not only the anti-pattern",
          "answers to a plan point must nest under it (e.g. 2.1/2.2/2.3); the "
          "rule was misapplied once because only the anti-pattern was worked")


def test_m2_md_snippet_is_numbered_and_acts_only():
    """THE RESTRUCTURE, pinned. Step 2 failed twice whilst its ACT sat buried
    among four explanations of WHY. The snippet now carries acts under hardcoded
    manual numbering (`universal/numbered.md`), and the reasoning lives in a
    Clarifications section BELOW it that refers to point numbers instead of
    restating them —— so nothing was deleted, only moved out of the path CC
    executes."""
    text = open(M2_MD, encoding="utf-8").read()
    snippets = re.findall(r"```(.*?)```", text, re.DOTALL)
    check(len(snippets) == 1, "m2.md holds exactly one fenced snippet",
          "found %d" % len(snippets))
    body = snippets[0] if snippets else ""
    check(re.search(r"^2\. ", body, re.M) is not None
          and re.search(r"^- 2\.1\. ", body, re.M) is not None,
          "the snippet is hardcoded-numbered with bulleted sub-items",
          "numbered.md: sub-items MUST follow bullets, top level must not")
    check(re.search(r"^\s*[-*] (?![0-9])", body, re.M) is None,
          "no unnumbered bullet survives inside the snippet",
          "numbered.md: no line may be unnumbered")
    check(re.search(r"\[?N?\]?\d+\.0\.", body) is None,
          "no `[N].0` numbering", "numbered.md forbids it")
    check("Clarifications" in text and text.index("Clarifications")
          > text.rindex("```"),
          "a Clarifications section sits BELOW the snippet",
          "the reasoning must not sit in the sequence CC executes")
    for ln in text.splitlines():
        if len(ln) > 90:
            check(False, "every m2.md line is =<90 chars",
                  "%d chars: %s" % (len(ln), ln[:60]))
            return
    check(True, "every m2.md line is =<90 chars")


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
        test_m2_md_snippet_is_numbered_and_acts_only()
    else:
        for fn in (test_preconditions,
                   test_real_incident_is_blocked,
                   test_typed_m2_is_blocked,
                   test_slog_write_lets_it_pass,
                   test_sprint_md_read_lets_it_pass,
                   test_agent_dispatch_lets_it_pass,
                   test_workflow_dispatch_lets_it_pass,
                   test_taskupdate_is_not_a_dispatch,
                   test_taskcreate_is_not_a_dispatch,
                   test_slog_beats_other_signals,
                   test_backticked_m2_is_not_an_invocation,
                   test_reading_m2_md_is_not_an_invocation,
                   test_fenced_m2_is_not_an_invocation,
                   test_midline_m2_is_not_an_invocation,
                   test_blocker_declaration_end_is_left_alone,
                   test_sentinel_end_is_left_alone,
                   test_lone_dot_end_after_declaring_is_left_alone,
                   test_missing_declaration_is_blocked,
                   test_missing_declaration_blocks_even_when_the_sprint_ran,
                   test_no_response_write_means_no_nodeclare_block,
                   test_reading_a_response_is_not_writing_one,
                   test_read_declaration_glyph_does_not_satisfy_shape_b,
                   test_harness_terminated_turn_is_not_blocked,
                   test_urgent_stop_is_not_blocked_for_a_missing_declaration,
                   test_sha_declaration_end_is_a_declaration_end,
                   test_sha_declaration_alone_does_not_suppress_shape_b,
                   test_one_forced_turn_per_prompt_across_both_shapes,
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
                   test_m2_md_snippet_is_numbered_and_acts_only,
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
