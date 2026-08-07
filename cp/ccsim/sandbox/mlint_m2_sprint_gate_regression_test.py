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

import copy
import atexit
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

# The incident's own query file —— the CONTENT source for the fixture, and only
# that. The fixture's Read is REDIRECTED to a copy in a temp folder (below).
Q_SOURCE = os.path.join(REPO, "sessions", "2026", "202608",
                        "career_query_202608041846.md")

# WHY THE COPY EXISTS, and why reading the file where it lives was a latent
# defect rather than a harmless convenience.
# `mlint.py` now looks for a `*slog_*.md` in the m2 query's OWN FOLDER (the
# disk-slog rule), so replaying the incident against the live `sessions/`
# folder asks a question about TODAY's disk, not about the moment the incident
# happened. And today that folder holds `career_slog_202608042032.md` —— the
# slog this very mission wrote two hours AFTER the stall. The replay therefore
# reported "the sprint already ran" and the suite's central test went green
# whilst detecting nothing. The hook was right; the fixture was anachronistic.
# `universal/coding.md` already forbids a script depending on a specific comms
# file "precisely because they move", and this is that rule biting: a live
# comms folder is shared, mutable state, so any verdict computed from it is a
# verdict about whatever else happens to be sitting there.
# So the query is copied into a folder this suite OWNS, and every disk-slog
# case below puts the slogs there deliberately. Hermetic by construction ——
# nothing another session writes to `sessions/` can change a result here.
_SANDBOX = tempfile.mkdtemp(prefix="mlint_fixture_")
atexit.register(shutil.rmtree, _SANDBOX, ignore_errors=True)
Q_FIXTURE = os.path.join(_SANDBOX, os.path.basename(Q_SOURCE))
# The slog that repaired the false block, pinned BY NAME as the fixture it is.
SLOG_PAIRED = "career_slog_202608042032.md"     # >= the query's TS: suppresses
SLOG_EARLIER = "career_slog_202608010001.md"    # <  the query's TS: does not


def _seed_query_copy():
    """Copy the incident query into the suite's own folder, falling back to a
    faithful stand-in. The fallback keeps the ONE property the fixture needs ——
    a column-1 `#m2` —— so a voided or moved source degrades the fidelity of
    this suite without silently gutting it (the precondition still reports it).
    """
    text = ""
    try:
        with open(Q_SOURCE, encoding="utf-8") as fh:
            text = fh.read()
    except Exception:
        text = ""
    if not re.search(r"(?m)^[ \t]*#m2\b", text):
        text = ("# Career query\n\nDraft the interview prep.\n\n#m2 expect 2\n")
    with open(Q_FIXTURE, "w", encoding="utf-8") as fh:
        fh.write(text)


_seed_query_copy()
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

# SHAPE C's fixture —— the 202608070423 auto-compaction, replayed. Same
# provenance rule as the m2 one: real records off disk, tool results trimmed,
# thinking dropped, and the compaction SUMMARY kept verbatim and WHOLE. That
# last point is not fussiness: an earlier draft truncated the summary and
# thereby deleted the incidental word "override" it contains, which is exactly
# the hazard the fixture must reproduce (see the override test below).
COMPACT_FIXTURE = os.path.join(HERE, "mlint_compaction_fixture.jsonl")
SENTINEL = "\U0001f6a8 Compaction Detected —— stopped all tasks."

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

_QUERY_NAME_RE = re.compile(r"^(?:[A-Za-z0-9-]+_)*query_\d{12}\.md$", re.I)


def fixture_records(query_dir=None):
    """The real incident transcript, with every `query_` read REDIRECTED into a
    folder this suite controls (`_SANDBOX` by default). Only the containing
    folder changes —— the basename, the tool, and every other record stay
    byte-for-byte as they were recorded. `query_dir` lets a disk-slog case point
    the same turn at a folder it has stocked differently, which is the only way
    to test a rule whose evidence is what sits NEXT to the file."""
    out = []
    target = query_dir or _SANDBOX
    with open(FIXTURE, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            rec = json.loads(raw)
            for blk in ((rec.get("message") or {}).get("content") or []):
                if not isinstance(blk, dict) or blk.get("type") != "tool_use":
                    continue
                inp = blk.get("input") or {}
                fp = inp.get("file_path")
                if isinstance(fp, str) and _QUERY_NAME_RE.match(
                        os.path.basename(fp)):
                    inp["file_path"] = os.path.join(target,
                                                    os.path.basename(fp))
            out.append(rec)
    return out


def query_dir_with(*slog_names):
    """A throwaway folder holding the incident query plus the named slogs. The
    caller removes it; every disk-slog case uses this so the evidence under test
    is created deliberately rather than inherited from a live comms folder."""
    d = tempfile.mkdtemp(prefix="mlint_slogdir_")
    shutil.copyfile(Q_FIXTURE, os.path.join(d, os.path.basename(Q_FIXTURE)))
    for name in slog_names:
        with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
            fh.write("# Sprint Log\n\n## SPRINT START\n")
    return d


def compaction_records():
    out = []
    with open(COMPACT_FIXTURE, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if raw:
                out.append(json.loads(raw))
    return out


def compaction_summary_text(recs):
    for r in recs:
        if r.get("isCompactSummary"):
            return (r.get("message") or {}).get("content") or ""
    return ""


def strip_compaction_markers(recs):
    """The same turn with every compaction signal removed —— the negative
    control for "a turn that was not opened by a compaction"."""
    out = []
    for r in recs:
        if r.get("type") == "system" and r.get("subtype") == "compact_boundary":
            continue
        r = copy.deepcopy(r)
        r.pop("isCompactSummary", None)
        out.append(r)
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


def compact_of(lines):
    """The `compact=` verdict on the last log line —— SHAPE C's named stage."""
    if not lines:
        return "<no log line>"
    m = re.search(r"\tcompact=([^\t]*)", lines[-1])
    return m.group(1) if m else "<absent>"


# ---------------------------------------------------------------------------
# 0. Preconditions
# ---------------------------------------------------------------------------

def test_preconditions():
    check(os.path.isfile(MLINT), "cscpt/mlint.py exists",
          "the Stop hook has not been created")
    check(os.path.isfile(FIXTURE), "real-incident fixture present",
          "mlint_incident_fixture.jsonl missing")
    check(os.path.isfile(COMPACT_FIXTURE), "real-compaction fixture present",
          "mlint_compaction_fixture.jsonl missing —— every SHAPE C check below "
          "would be vacuous")
    check(os.path.isfile(Q_SOURCE),
          "incident query still on disk (the fixture's CONTENT source)",
          "%s missing —— the copy falls back to a stand-in, so the m2 evidence "
          "stays real but is no longer the incident's own words" % Q_SOURCE)
    # The copy is what the hook actually reads, so ITS `#m2` is the load-bearing
    # one. Asserted directly: a copy that lost the token would make the whole
    # suite fail open and every block test would go vacuously green.
    try:
        with open(Q_FIXTURE, encoding="utf-8") as fh:
            qtext = fh.read()
    except Exception:
        qtext = ""
    check(re.search(r"(?m)^[ \t]*#m2\b", qtext) is not None,
          "the sandboxed query copy carries a column-1 `#m2`",
          "without it every m2 case below proves nothing")
    check(not any(re.match(r"^(?:[A-Za-z0-9-]+_)*slog_\d{12}\.md$", n)
                  for n in os.listdir(_SANDBOX)),
          "the default fixture folder holds NO slog",
          "a stray slog here would suppress every SHAPE A block via the "
          "disk-slog rule —— the exact anachronism the copy exists to prevent")


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
        recs = [r for r in recs if not _reads(r, Q_FIXTURE)]
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
    recs = [r for r in recs if not _reads(r, Q_FIXTURE)]
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "no_m2",
          "reading universal/m2.md alone is NOT an m2 invocation",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_fenced_m2_is_not_an_invocation():
    recs = fixture_records()
    recs[0] = user_msg("see the snippet:\n```\n#m2\n```\nthat is all")
    recs = [r for r in recs if not _reads(r, Q_FIXTURE)]
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "no_m2",
          "#m2 inside a fenced block is NOT an invocation",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_midline_m2_is_not_an_invocation():
    recs = fixture_records()
    recs[0] = user_msg("remind me what #m2 does")
    recs = [r for r in recs if not _reads(r, Q_FIXTURE)]
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
# 4b. SHAPE C —— root CLAUDE.md §5's post-compaction sentinel
#
# WHY THESE EXIST. On 202608070423 an auto-compaction hit this repo's own
# session and §5 was skipped ENTIRELY —— no `🚨` sentinel, no halt, no §5.3/§5.4
# lists. The cause is structural: the harness's compaction summary CLOSES with
# "Resume directly —— do not acknowledge the summary…", and that arrives as the
# user-side message opening the turn, the strongest position in the context. §5
# is prose read turns earlier. Prose lost, and the miss was NOT-NOTICED, so per
# `cp/ccsim/CLAUDE.md` §8.7 prose could not repair it. `PostCompact` cannot
# help —— that event's stdout and stderr both go to the USER, so no exit code
# gives it a model-facing channel. Stop is the only event that can force the
# missing output back into the same turn.
#
# WHAT THESE CANNOT PROVE, stated plainly: a real compaction cannot be forced
# on demand, so no test here exercises the LIVE path end to end. They prove the
# hook's verdict on the genuine records a real compaction wrote. The live half
# of the claim rests on mlint already being registered on Stop (see
# `test_registered_live`) and having blocked live earlier the same day.
# ---------------------------------------------------------------------------

def test_real_compaction_breach_is_blocked():
    """THE FAILING SCENARIO, replayed byte-for-byte off disk: the turn the
    202608070423 summary opened, which emitted a lone `.`, worked on, and closed
    with a TEA3 batch —— and never emitted the sentinel."""
    recs = compaction_records()
    code, err, lines = run(recs)
    check(code == 2 and action_of(lines) == "block_nosentinel",
          "the REAL post-compaction breach is BLOCKED (exit 2)",
          "exit=%d action=%s compact=%s"
          % (code, action_of(lines), compact_of(lines)))
    check(compact_of(lines) == "owed",
          "the block records compact=owed", compact_of(lines))
    for needle, label in (
            ("\U0001f6a8", "the sentinel glyph itself"),
            ("§5.2", "the HALT (§5.2)"),
            ("§5.3", "the USEFUL list (§5.3)"),
            ("§5.4", "the remainder list (§5.4)"),
            ("lone `.`", "the lone-dot escape for a wrong verdict")):
        check(needle in err, "block message names %s" % label, repr(err[:160]))
    check("§5.8" in err,
          "block message keeps the `#sprint` case (§5.8) SUBORDINATE to §5",
          "sprint.md says a compaction during a sprint still emits the "
          "sentinel; the message must not read as an exemption")


def test_summary_carrying_override_still_blocks():
    """THE REGRESSION THAT WOULD HAVE KILLED THIS OUTRIGHT. `override` in the
    typed message disarms mlint —— and BOTH real compaction summaries on disk
    contain the word incidentally, because they recap turns in which the owner
    granted one. A compaction summary is HARNESS text, not something the user
    typed, so it supplies no typed-message evidence at all. Without that, every
    compaction turn exits at `exempt:override` and SHAPE C is dead on arrival:
    verified against the pre-change hook, which does exactly that on this
    fixture."""
    recs = compaction_records()
    summary = compaction_summary_text(recs)
    check(re.search(r"\boverrid(?:e|ing)\b", summary, re.I) is not None,
          "the fixture's summary really does contain the word 'override'",
          "the fixture no longer reproduces the hazard —— do not truncate it")
    code, _, lines = run(recs)
    check(code == 2, "an 'override' inside the SUMMARY does not exempt the turn",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_override_in_summary_still_exempts_the_m2_shapes():
    """THE OTHER HALF OF THE `override` GATE, and the reason it is SPLIT.

    SHAPE C must survive an `override` sitting inside the summary (the test
    above). The lazy way to get that is to blank the summary text outright ——
    which also strips the exemption from SHAPES A and B, so a compaction turn
    that was exempt from them before becomes blockable by them now. That is a
    WIDENING onto a route with a live false-positive history: on 202608070450
    this hook issued `block_nodeclare` with `m2=query` because the turn had
    merely RE-READ an old `query_` containing a line-start `#m2`. A
    post-compaction turn re-reads old comms by design (root §5.3, §5.8.4), so
    that route is more likely there, not less.

    So the exemption is kept for the m2 shapes on the real summary text and
    only SHAPE C is placed beyond it. Below: the real summary (which carries
    the word) + a sentinel + exactly the 202608070450 shape —— an old `query_`
    read, a `response_` written, no `➡️`. It must exit at `exempt:override`,
    as the pre-change hook did. The negative control strips the word from the
    summary and shows the same turn DOES block, so this can never go vacuous.
    """
    base = compaction_records()
    head = base[:2]
    check(head[0].get("subtype") == "compact_boundary"
          and head[1].get("isCompactSummary") is True,
          "the fixture opens with the real boundary + summary pair",
          "head shapes: %s" % [r.get("type") for r in head])
    check(re.search(r"\boverrid(?:e|ing)\b",
                    compaction_summary_text(base), re.I) is not None,
          "the fixture's summary really does contain the word 'override'",
          "this check is vacuous without it")
    tmpdir = tempfile.mkdtemp(prefix="mlint_override_split_")
    try:
        qpath = os.path.join(tmpdir, "ccsim_query_209912312359.md")
        with open(qpath, "w", encoding="utf-8") as fh:
            fh.write("#m2 expect 2\n\nDo the thing.\n")
        rpath = os.path.join(tmpdir, "ccsim_response_209912312359.md")
        tail = [assistant_text(SENTINEL),
                assistant_tool("Read", {"file_path": qpath}),
                assistant_tool("Write", {"file_path": rpath}),
                assistant_text("Done, resuming the sprint.")]
        code, _, lines = run(head + tail)
        check(code == 0 and action_of(lines) == "exempt:override",
              "an `override` in the summary still exempts the m2 shapes",
              "exit=%d action=%s" % (code, action_of(lines)))

        scrubbed = copy.deepcopy(head)
        scrubbed[1]["message"]["content"] = re.sub(
            r"(?i)\boverrid(?:e|ing)\b", "permitted",
            compaction_summary_text(base))
        code, _, lines = run(scrubbed + tail)
        check(code == 2 and action_of(lines) == "block_nodeclare",
              "NEGATIVE CONTROL: without the word the same turn DOES block",
              "exit=%d action=%s" % (code, action_of(lines)))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_override_never_exempts_shape_c():
    """The split's other guarantee, stated as its own check rather than left to
    be inferred: the word disarms A and B, and NEVER C. §5 owes the sentinel on
    every compaction without exception (`universal/sprint.md` § Interactions
    says so even mid-sprint), and an exemption must be a live instruction for
    the turn at hand —— a machine recap of an older turn is not one. The escape
    from a SHAPE C block is the lone `.` its message names."""
    base = compaction_records()
    recs = base[:2] + [assistant_text("Carrying on with the flint tail rule."),
                       assistant_text("➡️ `202608/response_202608070423.md`")]
    code, err, lines = run(recs)
    check(code == 2 and action_of(lines) == "block_nosentinel",
          "`override` in the summary does not reach SHAPE C",
          "exit=%d action=%s" % (code, action_of(lines)))
    check("lone `.`" in err,
          "the SHAPE C message still names the lone-`.` escape", err[:120])


def test_summarys_own_sentinel_glyph_does_not_count():
    """The real summary quotes `🚨` in its recap. Only ASSISTANT chat lines can
    discharge §5 —— a glyph in the user-side record is the harness describing
    the past, not the model speaking now."""
    recs = compaction_records()
    check("\U0001f6a8" in compaction_summary_text(recs),
          "the fixture's summary really does contain a `🚨`",
          "this check is vacuous without it")
    code, _, lines = run(recs)
    check(code == 2, "a `🚨` inside the summary does not satisfy the sentinel",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_sentinel_anywhere_in_the_turn_suppresses_the_block():
    """NEGATIVE CONTROL. Presence suppresses, so the whole window is scanned ——
    not just the first line, though §5.1 owes it immediately. A late sentinel is
    an ordering fault, not the total omission this exists for, and it is not
    worth a wrong block. Ordering is deliberately unenforced."""
    base = compaction_records()
    first = base[:2] + [assistant_text(SENTINEL)] + base[2:]
    last = base + [assistant_text(SENTINEL)]
    for label, recs in (("first", first), ("last", last)):
        code, _, lines = run(recs)
        check(code == 0 and compact_of(lines) == "ok",
              "a sentinel emitted %s does NOT block" % label,
              "exit=%d action=%s compact=%s"
              % (code, action_of(lines), compact_of(lines)))


def test_bold_wrapped_sentinel_is_recognised():
    base = compaction_records()
    recs = base[:2] + [assistant_text("**%s**" % SENTINEL)] + base[2:]
    code, _, lines = run(recs)
    check(code == 0 and compact_of(lines) == "ok",
          "a bold-wrapped sentinel is still a sentinel",
          "exit=%d compact=%s" % (code, compact_of(lines)))


def test_no_compaction_means_no_sentinel_block():
    """NEGATIVE CONTROL. Same turn, compaction markers removed: nothing is owed
    and the compaction test says so by name (`compact=no`), never by silence."""
    code, _, lines = run(strip_compaction_markers(compaction_records()))
    check(code == 0, "a turn with no compaction is never blocked for a sentinel",
          "exit=%d action=%s" % (code, action_of(lines)))
    check(compact_of(lines) == "no",
          "a non-compaction turn logs compact=no (ran, found nothing)",
          compact_of(lines))


def test_wording_alone_never_arms_the_block():
    """A typed message QUOTING the summary's opening sentence —— no boundary
    record, no `isCompactSummary` —— must not block. CCSIM sessions quote that
    sentence whilst working on this very defect, and a pasted quote must never
    arm a hook that BLOCKS."""
    recs = [user_msg("This session is being continued from a previous "
                     "conversation that ran out of context. <- why does mlint "
                     "not fire on this?", pid="quote-only"),
            assistant_text("Because the structural flag is absent.")]
    code, _, lines = run(recs)
    check(code == 0 and compact_of(lines) == "no",
          "quoting the summary's wording does not arm SHAPE C",
          "exit=%d action=%s compact=%s"
          % (code, action_of(lines), compact_of(lines)))


def test_boundary_plus_wording_without_the_flag_is_still_caught():
    """Belt and braces for a harness that keeps `compact_boundary` but drops
    `isCompactSummary`. BOTH halves are required —— the adjacent system record
    AND the opening sentence —— so this can never degrade into the wording test
    the case above rejects."""
    recs = [copy.deepcopy(r) for r in compaction_records()]
    for r in recs:
        r.pop("isCompactSummary", None)
    code, _, lines = run(recs)
    check(code == 2 and action_of(lines) == "block_nosentinel",
          "a compact_boundary + the opening sentence still identifies the turn",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_harness_terminated_compaction_turn_is_not_blocked():
    """A turn cut off by the CLI cannot comply, so blocking would spend the one
    allowed forced turn against a wall."""
    recs = compaction_records() + [
        assistant_text("You've hit your session limit · resets 8:30pm",
                       api_error=True)]
    code, _, lines = run(recs)
    check(code == 0 and compact_of(lines) == "api_error",
          "a harness-terminated compaction turn is left alone",
          "exit=%d action=%s compact=%s"
          % (code, action_of(lines), compact_of(lines)))


def test_blocker_ending_compaction_turn_is_not_blocked():
    """A `⚠️` blocker (§3.2.5) is a deliberate early stop. Holding one open
    delays exactly the message the user most needs to see —— even to collect the
    sentinel. Fail-open by choice, and the sentinel stays missable that way."""
    recs = compaction_records() + [assistant_text("⚠️ FURY unmounted mid-turn")]
    code, _, lines = run(recs)
    check(code == 0 and compact_of(lines) == "urgent",
          "a `⚠️` ending is not held open for the sentinel",
          "exit=%d action=%s compact=%s"
          % (code, action_of(lines), compact_of(lines)))


def test_compaction_turn_with_no_assistant_output_is_not_blocked():
    """An empty window is likelier a transcript mis-parsed than an agent that
    genuinely said nothing, so SHAPE C declines to judge it."""
    recs = compaction_records()[:2]
    code, _, lines = run(recs)
    check(code == 0 and compact_of(lines) == "no_output",
          "a compaction turn with no assistant record is left alone",
          "exit=%d action=%s compact=%s"
          % (code, action_of(lines), compact_of(lines)))


def test_sentinel_block_fires_at_most_once_per_prompt():
    """`hook_guide.md` §6.3 budgets ONE extra round trip per prompt, and all
    three shapes share it. The ledger line is written BEFORE the block, so a
    failed write means no block at all."""
    tmpdir = tempfile.mkdtemp(prefix="mlint_compact_ledger_")
    try:
        log = os.path.join(tmpdir, "mlint.log")
        first, _, _ = run(compaction_records(), log=log)
        second, _, lines = run(compaction_records(), log=log)
        check(first == 2 and second == 0,
              "the same compacted prompt is blocked once, never twice",
              "first=%d second=%d action=%s"
              % (first, second, action_of(lines)))
        check(action_of(lines) == "already_blocked",
              "the second stop logs already_blocked", action_of(lines))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_sentinel_block_is_not_issued_when_it_cannot_be_recorded():
    """An unrecorded block is a block that can repeat —— worse than missing
    one."""
    tmpdir = tempfile.mkdtemp(prefix="mlint_compact_badlog_")
    try:
        log = os.path.join(tmpdir, "nodir", "mlint.log")   # unwritable path
        code, _, _ = run(compaction_records(), log=log)
        check(code == 0, "an unwritable log means NO sentinel block (fail open)",
              "exit=%d" % code)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_stop_hook_active_disarms_shape_c():
    code, _, lines = run(compaction_records(), stop_hook_active=True)
    check(code == 0 and action_of(lines) == "loop_guard",
          "stop_hook_active disarms SHAPE C too (guard 1)",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_compaction_turn_out_of_scope_repo():
    code, _, lines = run(compaction_records(), cwd="/tmp")
    check(code == 0 and action_of(lines) == "out_of_scope",
          "another repo's compaction is never policed",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_compact_field_is_on_every_log_line():
    """`compact=n/a` on a run that exited early is the whole point: it says the
    test never ran, so silence can never be read as "ran and found nothing"."""
    for label, recs, kw in (
            ("blocked compaction", compaction_records(), {}),
            ("out of scope", compaction_records(), {"cwd": "/tmp"}),
            ("m2 stall", fixture_records(), {})):
        _, _, lines = run(recs, **kw)
        check(len(lines) == 1 and compact_of(lines) not in
              ("<absent>", "<no log line>"),
              "compact= is present on the log line (%s)" % label,
              "lines=%d compact=%s" % (len(lines), compact_of(lines)))
    _, _, lines = run(compaction_records(), cwd="/tmp")
    check(compact_of(lines) == "n/a",
          "a run that exited before the test logs compact=n/a",
          compact_of(lines))


# ---------------------------------------------------------------------------
# 4c. SHAPE C, UPGRADE 1 —— the debt is OWED UNTIL PAID, not until interrupted
#
# THE HOLE THIS CLOSES, found by red-teaming SHAPE C after it shipped. SHAPE C
# originally armed only when the record OPENING the current turn window WAS the
# summary. So any later user message —— a `continue`, a mid-turn message (root
# §3.1.7.6.1), a wake after a usage-limit death —— moved the opener to a human
# record and the sentinel was never owed again. Escape once, escape forever.
# The real 202608070423 transcript has EXACTLY that shape: summary, a worked
# turn closing on a `✅` batch with no sentinel, then a typed user message.
# Root §5.1 was rewritten to match ("pay every UNPAID compaction NOW"; "UNPAID =
# a summary you did NOT write is in context w/ no LATER `🚨` of yours";
# "Applies on ANY later turn too… until paid") and these pin the code to it.
# ---------------------------------------------------------------------------

def _worked_turn(text="✅ `cscpt/dlint.py`, `CLAUDE.md`"):
    """A turn that did some work and closed on a declaration batch —— the shape
    the real breach ended on, and one carrying NO sentinel."""
    return [assistant_tool("Bash", {"command": "git status"}),
            assistant_text(text)]


def test_debt_survives_a_later_user_message():
    """THE UPGRADE, stated as the one test that matters. Compaction, an unpaid
    worked turn, then a GENUINE typed message opening a new turn that also does
    not pay. The debt must still be owed. Against the pre-change hook this turn
    exits 0, because its window opener is the human message."""
    recs = (compaction_records() + [user_msg("re-read root CLAUDE.md",
                                             pid="after-compaction")]
            + _worked_turn())
    code, err, lines = run(recs)
    check(code == 2 and action_of(lines) == "block_nosentinel",
          "an unpaid compaction is STILL owed after a later user message",
          "exit=%d action=%s compact=%s"
          % (code, action_of(lines), compact_of(lines)))
    check("\U0001f6a8" in err, "the block still names the sentinel", err[:120])


def test_debt_survives_a_continue():
    """A bare `continue` is the commonest way the old arming was lost."""
    recs = (compaction_records() + [user_msg("continue", pid="continue-1")]
            + _worked_turn())
    code, _, lines = run(recs)
    check(code == 2 and action_of(lines) == "block_nosentinel",
          "a `continue` does not discharge the sentinel debt",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_debt_survives_a_limit_death_and_wake():
    """Root §9.02.4's scenario: the turn died on a usage limit, the user woke
    the session later. The first turn is exempt (it could not comply); the woken
    one is not, and under the old arming it was never even tested."""
    recs = (compaction_records()
            + [assistant_text("You've hit your session limit", api_error=True),
               user_msg("back now, carry on", pid="after-limit")]
            + _worked_turn())
    code, _, lines = run(recs)
    check(code == 2 and action_of(lines) == "block_nosentinel",
          "a wake after a limit death still owes the sentinel",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_a_paid_debt_is_never_re_armed():
    """NEGATIVE CONTROL, and the one that stops this becoming a nag machine.
    Once an assistant record after the summary emits the sentinel, every later
    turn is clean —— `compact=paid`, exit 0, however many turns follow."""
    recs = (compaction_records()[:2] + [assistant_text(SENTINEL)]
            + [user_msg("carry on then", pid="paid-1")] + _worked_turn()
            + [user_msg("and again", pid="paid-2")] + _worked_turn())
    code, _, lines = run(recs)
    check(code == 0 and compact_of(lines) == "paid",
          "a compaction paid in an EARLIER turn is never re-armed",
          "exit=%d action=%s compact=%s"
          % (code, action_of(lines), compact_of(lines)))


def test_paid_is_distinguishable_from_never_compacted():
    """`compact=paid` vs `compact=no` —— MA-requested and load-bearing for
    diagnosis: "found a compaction, debt settled" and "never compacted" are
    different facts, and without the split the log cannot show that
    owed-until-paid is scanning at all rather than silently returning False."""
    paid = (compaction_records()[:2] + [assistant_text(SENTINEL)]
            + [user_msg("next", pid="paid-3")] + _worked_turn())
    _, _, lines = run(paid)
    check(compact_of(lines) == "paid", "a settled debt logs compact=paid",
          compact_of(lines))
    _, _, lines = run(strip_compaction_markers(compaction_records()))
    check(compact_of(lines) == "no", "no compaction at all logs compact=no",
          compact_of(lines))


def test_sentinel_in_this_turn_still_logs_ok():
    """`ok` is kept distinct from `paid`: paid-right-now and paid-earlier are
    different facts too, and `ok` is the one the original SHAPE C tests assert."""
    base = compaction_records()
    _, _, lines = run(base[:2] + [assistant_text(SENTINEL)] + base[2:])
    check(compact_of(lines) == "ok", "a sentinel in THIS turn logs compact=ok",
          compact_of(lines))


def test_second_compaction_is_owed_separately():
    """Root §5.1.3 —— "Owed PER summary… one that recaps an older sentinel is
    itself still unpaid". Only the LAST summary is tested and only records AFTER
    it can pay it, so the first compaction's sentinel cannot settle the second."""
    base = compaction_records()
    second_pair = copy.deepcopy(base[:2])
    # Make the second summary textually distinct, as a real second recap is.
    # Located by its FLAG, never by index —— the pair is boundary-then-summary
    # and an index would silently move if that ever changed.
    for rec in second_pair:
        if rec.get("isCompactSummary"):
            rec["message"]["content"] = (
                "This session is being continued from a previous conversation "
                "that ran out of context. SECOND compaction, different work.")
            rec["timestamp"] = "2026-08-07T09:00:00.000Z"
    recs = (base[:2] + [assistant_text(SENTINEL)]
            + [user_msg("keep going", pid="between")]
            + second_pair + _worked_turn())
    code, _, lines = run(recs)
    check(code == 2 and action_of(lines) == "block_nosentinel",
          "a SECOND compaction is owed even though the FIRST was paid",
          "exit=%d action=%s compact=%s"
          % (code, action_of(lines), compact_of(lines)))


def test_two_compactions_get_separate_block_budgets():
    """The budget is keyed on the compaction, so a second compaction arrives
    with a fresh allowance rather than inheriting an exhausted one."""
    tmpdir = tempfile.mkdtemp(prefix="mlint_two_compact_")
    try:
        log = os.path.join(tmpdir, "mlint.log")
        base = compaction_records()
        first = base + [user_msg("one", pid="c1")] + _worked_turn()
        code_a, _, _ = run(first, log=log)
        second = copy.deepcopy(base)
        for rec in second:
            if rec.get("isCompactSummary"):
                rec["message"]["content"] = (
                    "This session is being continued from a previous "
                    "conversation that ran out of context. A DIFFERENT recap.")
                rec["timestamp"] = "2026-08-07T09:00:00.000Z"
        code_b, _, lines = run(second + [user_msg("two", pid="c2")]
                               + _worked_turn(), log=log)
        check(code_a == 2 and code_b == 2,
              "a second compaction gets its own block budget",
              "first=%d second=%d action=%s"
              % (code_a, code_b, action_of(lines)))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_block_budget_is_bounded_per_compaction():
    """THE PRICE OF OWED-UNTIL-PAID, paid deliberately. An unpaid debt now arms
    on EVERY later turn, so without a per-compaction ceiling a model answering
    each block with the sanctioned lone `.` escape would be blocked once per
    prompt for the rest of the session —— the unbounded-retry failure this hook
    elsewhere calls worse than missing. Each new prompt id would otherwise earn
    a fresh block, so the per-prompt ledger alone cannot bound it."""
    tmpdir = tempfile.mkdtemp(prefix="mlint_budget_")
    try:
        log = os.path.join(tmpdir, "mlint.log")
        codes = []
        for n in range(6):
            recs = (compaction_records()
                    + [user_msg("nudge %d" % n, pid="budget-%d" % n)]
                    + _worked_turn())
            code, _, lines = run(recs, log=log)
            codes.append(code)
        check(codes.count(2) <= 3 and 2 in codes,
              "one compaction can never cost more than 3 blocks",
              "codes=%s" % codes)
        check(codes[-1] == 0 and compact_of(lines) == "spent",
              "past the budget the verdict is `spent`, and it is LOGGED",
              "last=%d compact=%s" % (codes[-1], compact_of(lines)))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_cid_is_stable_across_both_copies_of_the_pair():
    """The harness writes the boundary+summary pair TWICE —— tail of the old
    transcript, head of the new —— with an identical timestamp and identical
    text (measured: `eaccd7dc-…` 1666 records, boundary 1612; `0b6a0a90-…`
    boundary 6). The budget would be worthless if the two copies hashed
    differently, so the id is pinned across a change of POSITION."""
    base = compaction_records()
    head_copy = base + [user_msg("x", pid="cid-a")] + _worked_turn()
    tail_copy = ([user_msg("earlier work", pid="cid-pre")]
                 + _worked_turn("Some earlier output.") + base
                 + [user_msg("x", pid="cid-b")] + _worked_turn())
    _, _, l1 = run(head_copy)
    _, _, l2 = run(tail_copy)
    cid1 = re.search(r"\tcid=([^\t]*)", l1[-1]).group(1)
    cid2 = re.search(r"\tcid=([^\t]*)", l2[-1]).group(1)
    check(cid1 == cid2 and cid1 not in ("-", ""),
          "the same compaction hashes identically wherever it sits",
          "head=%s tail=%s" % (cid1, cid2))


def test_truncated_transcript_fails_open():
    """The tail-read may drop the pair on a huge transcript. No summary found
    means no debt —— `compact=no`, exit 0. Fail open, exactly as before."""
    recs = ([user_msg("carry on", pid="trunc")] + _worked_turn())
    code, _, lines = run(recs)
    check(code == 0 and compact_of(lines) == "no",
          "a transcript whose compaction pair was truncated away fails open",
          "exit=%d action=%s compact=%s"
          % (code, action_of(lines), compact_of(lines)))


def test_typed_override_after_a_compaction_still_disarms_the_m2_shapes():
    """The typed-text blanking is gated on the TRIGGER being the summary, never
    on `compacted`. A debt now persists across turns, so `compacted` is True on
    turns a HUMAN opened —— blanking those would delete the real `override` the
    user just typed and the real `#m2` he may have just written."""
    recs = (compaction_records()[:2] + [assistant_text(SENTINEL)]
            + [user_msg("#m2 do it —— override the lint", pid="ovr-typed")]
            + [assistant_tool("Write", {"file_path": os.path.join(
                _SANDBOX, "career_response_202608041846.md")}),
               assistant_text("Done.")])
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "exempt:override",
          "a genuine typed `override` after a compaction still disarms A/B",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_typed_m2_after_a_compaction_is_still_evidence():
    """The other half: a real `#m2` typed AFTER a paid compaction must still be
    m2 evidence. Blanking on `compacted` rather than on the trigger would have
    silently deleted it and disabled shapes A and B for the rest of the
    session."""
    recs = (compaction_records()[:2] + [assistant_text(SENTINEL)]
            + [user_msg("#m2 expect 2", pid="m2-typed-after")]
            + [assistant_tool("Bash", {"command": "git commit"}),
               assistant_text("✅ `universal/m2.md`"),
               assistant_text("\U0001f988 `deadbeef`")])
    code, _, lines = run(recs)
    check(code == 2 and action_of(lines) == "block"
          and "m2=typed" in lines[-1],
          "a `#m2` typed after a compaction is still evidence",
          "exit=%d action=%s line=%s"
          % (code, action_of(lines), lines[-1] if lines else ""))


# ---------------------------------------------------------------------------
# 4d. UPGRADE 2 —— disk-slog suppression, repairing a PROVEN false block
#
# On 202608070450 mlint blocked a turn with `m2=query sprint=none` whose final
# chat line was `➡️ **`202608/career_response_202608041846.md`**`. The turn had
# merely RE-READ a three-day-old `career_query_202608041846.md`; that mission's
# sprint had run days before and its `career_slog_202608042032.md` had been on
# disk ever since. A real turn was spent on nothing.
#
# TIMESTAMP-PAIRING WOULD NOT HAVE CAUGHT IT: root §3.5.3 makes the `response_`
# carry the query's TS, so query and response matched perfectly. Staleness is
# invisible in the pair. `universal/sprint.md`'s Preamble is what settles it ——
# the slog is a MANDATORY pair, "Neither is EVER optional", so a slog at least
# as new as the query proves that query's sprint already ran.
# ---------------------------------------------------------------------------

def test_stale_query_with_its_paired_slog_is_not_blocked():
    """THE 202608041846 FALSE BLOCK, pinned by name. Same transcript as the
    incident test, one difference: the mission's own slog is on disk beside the
    query, exactly as it really was on the day of the false block."""
    d = query_dir_with(SLOG_PAIRED)
    try:
        code, _, lines = run(fixture_records(query_dir=d))
        check(code == 0, "a stale query whose slog is on disk is NOT blocked",
              "exit=%d action=%s sprint=%s"
              % (code, action_of(lines), lines[-1] if lines else ""))
        check("sprint=slog_disk" in (lines[-1] if lines else ""),
              "the suppression names itself in the log (`sprint=slog_disk`)",
              lines[-1] if lines else "<none>")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_the_same_turn_without_the_slog_still_blocks():
    """NEGATIVE CONTROL, and the reason the case above is not simply a hole.
    Remove the slog and the identical turn blocks —— so the suppression is doing
    the discriminating, not merely disabling SHAPE A."""
    d = query_dir_with()
    try:
        code, _, lines = run(fixture_records(query_dir=d))
        check(code == 2 and action_of(lines) == "block",
              "without a slog on disk the same turn is still blocked",
              "exit=%d action=%s" % (code, action_of(lines)))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_an_older_slog_does_not_suppress():
    """`>=` against the query's OWN TS is what makes this a staleness test
    rather than a blanket disarm: a slog PREDATING the query belongs to an
    earlier mission and says nothing about this one. A fresh `#m2` carries the
    newest TS in its folder, so nothing on disk can be >= it."""
    d = query_dir_with(SLOG_EARLIER)
    try:
        code, _, lines = run(fixture_records(query_dir=d))
        check(code == 2 and action_of(lines) == "block",
              "a slog OLDER than the query does not suppress the block",
              "exit=%d action=%s" % (code, action_of(lines)))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_a_cp_prefixed_slog_from_another_project_still_suppresses():
    """Root §5.8.1 makes the same call for its own glob: any `*slog_*`, never a
    CP-prefix match. A prefix match is NARROWER, and narrower means MORE firing
    —— the wrong direction for a signal whose only power is to suppress. The
    accepted miss is stated in `mlint.py` rather than hidden here."""
    d = query_dir_with("ccsim_slog_202608070502.md")
    try:
        code, _, _ = run(fixture_records(query_dir=d))
        check(code == 0,
              "any `*slog_*` at least as new as the query suppresses",
              "exit=%d" % code)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_a_typed_m2_is_not_suppressed_by_a_disk_slog():
    """The disk-slog rule applies ONLY to the `query_`-file route, because only
    that route can point at a mission older than this turn. A TYPED `#m2` is by
    definition an instruction for now, and an old slog must never disarm it."""
    d = query_dir_with(SLOG_PAIRED)
    try:
        recs = [user_msg("#m2 expect 2", pid="typed-vs-slog"),
                assistant_tool("Read", {"file_path": os.path.join(
                    d, os.path.basename(Q_FIXTURE))}),
                assistant_text("✅ `universal/m2.md`"),
                assistant_text("\U0001f988 `deadbeef`")]
        code, _, lines = run(recs)
        check(code == 2 and action_of(lines) == "block",
              "a disk slog never suppresses a TYPED `#m2`",
              "exit=%d action=%s" % (code, action_of(lines)))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_an_in_window_slog_write_still_wins():
    """The strongest signal is unchanged: a slog WRITTEN this turn logs
    `sprint=slog`, not `slog_disk`. The new rule adds a route, never replaces
    one."""
    d = query_dir_with(SLOG_PAIRED)
    try:
        recs = insert_before_final_text(
            fixture_records(query_dir=d),
            [assistant_tool("Write", {"file_path": os.path.join(
                d, "career_slog_202608042032.md")})])
        code, _, lines = run(recs)
        check(code == 0 and "sprint=slog\t" in lines[-1],
              "an in-window slog write still reports `sprint=slog`",
              lines[-1] if lines else "<none>")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_a_vanished_query_folder_fails_open_and_never_blocks():
    """Losing the evidence must never manufacture a verdict. With the folder
    gone the query cannot be read at all, so the m2 evidence disappears with it
    and the run exits at `no_m2` —— exit 0, no block. Every failure inside the
    disk-slog check likewise yields False (no suppression) rather than raising,
    so neither half of the new rule can turn a missing file into an outcome."""
    d = query_dir_with(SLOG_PAIRED)
    recs = fixture_records(query_dir=d)
    shutil.rmtree(d, ignore_errors=True)          # folder gone before the run
    code, _, lines = run(recs)
    check(code == 0 and action_of(lines) == "no_m2",
          "a vanished query folder fails open, never blocks",
          "exit=%d action=%s" % (code, action_of(lines)))


# ---------------------------------------------------------------------------
# 4e. RED TEAM —— false-positive routes hunted deliberately
#
# This is a BLOCKING hook on a live session: a wrong block costs a real turn.
# Owed-until-paid widened the scan from ONE record to the WHOLE transcript, so
# every route below got MORE chances to fire, not fewer. Each is either closed
# and pinned here, or accepted in `mlint.py` with its reason stated.
# ---------------------------------------------------------------------------

def test_a_quoted_summary_mid_transcript_never_arms():
    """CCSIM sessions quote the summary's opening sentence constantly whilst
    working on this very defect —— the brief that commissioned this upgrade does
    it. Under the whole-transcript scan a quote is now seen wherever it sits, so
    the STRUCTURAL requirement is what keeps it inert."""
    recs = [user_msg("earlier", pid="quote-mid"),
            assistant_text("Working."),
            user_msg("This session is being continued from a previous "
                     "conversation that ran out of context. <- why does this "
                     "not arm mlint?", pid="quote-mid-2"),
            assistant_text("Because the structural flag is absent.")]
    code, _, lines = run(recs)
    check(code == 0 and compact_of(lines) == "no",
          "a quoted summary anywhere in the transcript never arms SHAPE C",
          "exit=%d action=%s compact=%s"
          % (code, action_of(lines), compact_of(lines)))


def test_an_assistant_quoting_the_summary_never_arms():
    """The mirror case: the MODEL pasting the sentence into its own output.
    Only a `type:"user"` record can be a summary, so an assistant record
    carrying the words is inert by construction."""
    recs = [user_msg("what does the summary say?", pid="assistant-quote"),
            assistant_text("It opens: \"This session is being continued from a "
                           "previous conversation that ran out of context.\"")]
    code, _, lines = run(recs)
    check(code == 0 and compact_of(lines) == "no",
          "an assistant quoting the summary never arms SHAPE C",
          "exit=%d compact=%s" % (code, compact_of(lines)))


def test_an_old_comms_file_saying_resume_directly_is_inert():
    """The contamination that produced the false block was an old `query_` being
    re-read. `Resume directly` in a comms file is not a compaction signal at all
    —— mlint reads query files ONLY for `#m2`, never for compaction evidence."""
    d = tempfile.mkdtemp(prefix="mlint_resume_")
    try:
        qp = os.path.join(d, "career_query_202608041846.md")
        with open(qp, "w", encoding="utf-8") as fh:
            fh.write("# Old write-up\n\nResume directly —— do not acknowledge "
                     "the summary, do not recap what was happening.\n"
                     "This session is being continued from a previous "
                     "conversation that ran out of context.\n")
        recs = [user_msg("have a look at that old file", pid="resume-file"),
                assistant_tool("Read", {"file_path": qp}),
                assistant_text("✅ `202608/career_query_202608041846.md`")]
        code, _, lines = run(recs)
        check(code == 0 and compact_of(lines) == "no",
              "an old comms file quoting the summary is not a compaction",
              "exit=%d action=%s compact=%s"
              % (code, action_of(lines), compact_of(lines)))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_no_shape_ever_blocks_outside_this_repo():
    """A HARD REQUIREMENT from the CC that owns `AJAP_repo`, not a nicety.
    This hook is registered in the USER settings file, so it fires in EVERY
    project on this Mac —— exactly as `.claude/post_compact.sh` does, and it is
    the only one of the two that can BLOCK. AJAP's `#seek` cockpit runs
    unattended for hours and its paramount rule is that nothing may stall it: a
    stalled cockpit is an unsupervised programme. So every shape is checked from
    an AJAP cwd, not just the one that happened to be tested before.
    SHAPE C is checked explicitly because it is the NEW one and inherits
    nothing by assumption."""
    ajap = os.path.join(os.path.dirname(REPO), "AJAP_repo")
    d = query_dir_with()
    try:
        shape_a = fixture_records(query_dir=d)
        shape_b = _strip_response_writes(fixture_records(query_dir=d))
        shape_b = insert_before_final_text(shape_b, [
            assistant_tool("Write", {"file_path": os.path.join(
                d, "career_response_202608041846.md")})])
        shape_b = replace_final_text(shape_b, "All done.")
        shape_c = (compaction_records()
                   + [user_msg("carry on", pid="ajap-c")] + _worked_turn())
        for label, recs in (("A", shape_a), ("B", shape_b), ("C", shape_c)):
            code, _, lines = run(recs, cwd=ajap)
            check(code == 0 and action_of(lines) == "out_of_scope",
                  "SHAPE %s never blocks from an AJAP cwd" % label,
                  "exit=%d action=%s" % (code, action_of(lines)))
        # And the same turns DO block from this repo —— otherwise the three
        # checks above would pass on turns that were never blockable anyway.
        for label, recs in (("A", shape_a), ("B", shape_b), ("C", shape_c)):
            code, _, _ = run(recs, cwd=REPO)
            check(code == 2,
                  "NEGATIVE CONTROL: SHAPE %s does block in THIS repo" % label,
                  "exit=%d" % code)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_an_inexactly_typed_sentinel_still_pays():
    """RULED ON, not left to taste. A sentinel with one em dash, the wrong case,
    or no full stop PAYS the debt and does not block.
    Under the old trigger-coupled arming a strict wording test would have cost
    one wrong block; under owed-until-paid it would leave the debt permanently
    unpaid and re-arm on EVERY later turn, turning a cosmetic typo into a
    recurring block. Verbatim wording is root §5.1.2's business and a matter for
    review —— never for a hook that can stall a session."""
    variants = (
        ("single em dash", "\U0001f6a8 Compaction Detected — stopped all tasks."),
        ("wrong case", "\U0001f6a8 COMPACTION DETECTED —— STOPPED ALL TASKS."),
        ("no full stop", "\U0001f6a8 Compaction Detected —— stopped all tasks"),
        ("glyph alone", "\U0001f6a8"),
        ("trailing detail", "%s Context lost below." % SENTINEL))
    base = compaction_records()
    for label, text in variants:
        code, _, lines = run(base[:2] + [assistant_text(text)] + base[2:])
        check(code == 0 and compact_of(lines) == "ok",
              "an inexact sentinel (%s) still PAYS the debt" % label,
              "exit=%d compact=%s" % (code, compact_of(lines)))


def test_merely_discussing_the_sentinel_does_not_pay():
    """The line-start anchor is what separates EMITTING from DISCUSSING, and
    this repo's sessions discuss the sentinel constantly —— including in the
    files that maintain this hook. A backticked or mid-sentence `🚨` must not
    discharge a real debt."""
    base = compaction_records()
    for label, text in (
            ("backticked", "The rule is `\U0001f6a8 Compaction Detected` "
                           "per §3.2.6."),
            ("mid-sentence", "I should have emitted \U0001f6a8 earlier."),
            ("named in prose", "Root §5 owes a \U0001f6a8 sentinel here.")):
        code, _, lines = run(base[:2] + [assistant_text(text)] + base[2:])
        check(code == 2 and action_of(lines) == "block_nosentinel",
              "%s `🚨` does NOT pay the debt" % label,
              "exit=%d action=%s compact=%s"
              % (code, action_of(lines), compact_of(lines)))


def test_a_fenced_sentinel_example_DOES_pay_and_that_is_accepted():
    """AN ACCEPTED MISS, pinned so it is a decision on the record rather than a
    surprise. `_has_sentinel` splits on lines and does not mask code fences, so
    a fenced EXAMPLE of the sentinel —— which the files maintaining this hook
    write constantly —— discharges a real debt.

    WHY IT IS NOT FIXED. Masking fences in ASSISTANT output would let one
    unbalanced backtick anywhere in a turn hide a genuine sentinel and produce a
    WRONG BLOCK, which is the expensive failure; this direction only ever
    suppresses, which is the cheap one. `_invokes_m2` masks fences because there
    a fence match CAUSES firing; here it PREVENTS it, so the same technique
    would push the risk the wrong way. Consistent with every other ambiguity in
    this hook (`hook_guide.md` §6.4: bias towards not firing).

    THE RESIDUAL RISK, stated rather than implied away (`cp/ccsim/CLAUDE.md`
    §8.7): a CCSIM session that compacts whilst documenting the sentinel can
    discharge its own §5 debt with an example. Nothing mechanical catches that;
    review must."""
    base = compaction_records()
    fenced = "```\n\U0001f6a8 Compaction Detected —— stopped all tasks.\n```"
    code, _, lines = run(base[:2] + [assistant_text(fenced)] + base[2:])
    check(code == 0 and compact_of(lines) == "ok",
          "a FENCED sentinel example pays the debt (accepted, fail-open)",
          "exit=%d compact=%s" % (code, compact_of(lines)))


def test_a_sidechain_sentinel_does_not_pay():
    """A sub-agent's output is not the main turn's speech —— root §9.02 briefs
    SAs to disregard the comms protocol entirely, so an SA that happens to print
    the glyph must never discharge the main agent's debt."""
    base = compaction_records()
    recs = base[:2] + [assistant_text(SENTINEL, sidechain=True)] + base[2:]
    code, _, lines = run(recs)
    check(code == 2 and action_of(lines) == "block_nosentinel",
          "a sub-agent's sentinel does not pay the main agent's debt",
          "exit=%d action=%s" % (code, action_of(lines)))


def test_a_malformed_transcript_fails_open():
    """Garbage lines, a truncated final record, and records of unknown shape.
    Every one must fail OPEN —— an unparseable transcript is not evidence of a
    breach."""
    tmpdir = tempfile.mkdtemp(prefix="mlint_malformed_")
    try:
        tpath = os.path.join(tmpdir, "t.jsonl")
        with open(tpath, "w", encoding="utf-8") as fh:
            fh.write("not json at all\n")
            fh.write(json.dumps({"type": "mystery"}) + "\n")
            fh.write(json.dumps(user_msg("hi", pid="malformed")) + "\n")
            fh.write(json.dumps(assistant_text("✅ `a/b.md`")) + "\n")
            fh.write('{"type":"assistant","message":{"role":')   # truncated
        payload = {"session_id": "malformed", "transcript_path": tpath,
                   "cwd": REPO, "hook_event_name": "Stop"}
        env = dict(os.environ, MLINT_LOG=os.path.join(tmpdir, "m.log"))
        proc = subprocess.run([sys.executable, MLINT],
                              input=json.dumps(payload), text=True,
                              capture_output=True, env=env, cwd="/")
        check(proc.returncode == 0,
              "a malformed transcript never blocks", "exit=%d" % proc.returncode)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_a_compaction_with_no_later_records_is_not_blocked():
    """The pair sitting at the very END of a transcript —— the TAIL copy the
    harness writes into the OLD session file. Nothing follows it, so the window
    is empty and SHAPE C declines to judge (`no_output`), exactly as it does for
    any window it may have mis-parsed."""
    code, _, lines = run(compaction_records()[:2])
    check(code == 0 and compact_of(lines) == "no_output",
          "a trailing compaction pair with nothing after it is left alone",
          "exit=%d compact=%s" % (code, compact_of(lines)))


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
    recs = [r for r in recs if not _reads(r, Q_FIXTURE)]
    recs = insert_before_final_text(recs, [
        assistant_tool("Read", {"file_path": Q_FIXTURE}, sidechain=True)])
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
                   test_real_compaction_breach_is_blocked,
                   test_summary_carrying_override_still_blocks,
                   test_override_in_summary_still_exempts_the_m2_shapes,
                   test_override_never_exempts_shape_c,
                   test_summarys_own_sentinel_glyph_does_not_count,
                   test_sentinel_anywhere_in_the_turn_suppresses_the_block,
                   test_bold_wrapped_sentinel_is_recognised,
                   test_no_compaction_means_no_sentinel_block,
                   test_wording_alone_never_arms_the_block,
                   test_boundary_plus_wording_without_the_flag_is_still_caught,
                   test_harness_terminated_compaction_turn_is_not_blocked,
                   test_blocker_ending_compaction_turn_is_not_blocked,
                   test_compaction_turn_with_no_assistant_output_is_not_blocked,
                   test_sentinel_block_fires_at_most_once_per_prompt,
                   test_sentinel_block_is_not_issued_when_it_cannot_be_recorded,
                   test_stop_hook_active_disarms_shape_c,
                   test_compaction_turn_out_of_scope_repo,
                   test_compact_field_is_on_every_log_line,
                   # 4c —— owed until PAID
                   test_debt_survives_a_later_user_message,
                   test_debt_survives_a_continue,
                   test_debt_survives_a_limit_death_and_wake,
                   test_a_paid_debt_is_never_re_armed,
                   test_paid_is_distinguishable_from_never_compacted,
                   test_sentinel_in_this_turn_still_logs_ok,
                   test_second_compaction_is_owed_separately,
                   test_two_compactions_get_separate_block_budgets,
                   test_block_budget_is_bounded_per_compaction,
                   test_cid_is_stable_across_both_copies_of_the_pair,
                   test_truncated_transcript_fails_open,
                   test_typed_override_after_a_compaction_still_disarms_the_m2_shapes,
                   test_typed_m2_after_a_compaction_is_still_evidence,
                   # 4d —— disk-slog suppression
                   test_stale_query_with_its_paired_slog_is_not_blocked,
                   test_the_same_turn_without_the_slog_still_blocks,
                   test_an_older_slog_does_not_suppress,
                   test_a_cp_prefixed_slog_from_another_project_still_suppresses,
                   test_a_typed_m2_is_not_suppressed_by_a_disk_slog,
                   test_an_in_window_slog_write_still_wins,
                   test_a_vanished_query_folder_fails_open_and_never_blocks,
                   # 4e —— red team
                   test_a_quoted_summary_mid_transcript_never_arms,
                   test_an_assistant_quoting_the_summary_never_arms,
                   test_an_old_comms_file_saying_resume_directly_is_inert,
                   test_no_shape_ever_blocks_outside_this_repo,
                   test_an_inexactly_typed_sentinel_still_pays,
                   test_merely_discussing_the_sentinel_does_not_pay,
                   test_a_fenced_sentinel_example_DOES_pay_and_that_is_accepted,
                   test_a_sidechain_sentinel_does_not_pay,
                   test_a_malformed_transcript_fails_open,
                   test_a_compaction_with_no_later_records_is_not_blocked,
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
