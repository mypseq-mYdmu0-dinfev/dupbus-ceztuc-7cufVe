#!/usr/bin/env python3
"""Regression suite —— blint.py marker guard (mark_chapter once-per-turn gate).

WHAT THIS PINS. Root CLAUDE.md §3.1.6.2 mandates exactly ONE chapter marker
(TEA2) per practical turn, at the true turn end. On 30/07 a Stop-block
continuation re-ran the TEAs and marked a SECOND chapter for the same turn ——
and a marker cannot be removed once made. hook_guide §6.13: MCP tools are
never hook-exempt, so a PreToolUse hook matched on
`mcp__ccd_session__mark_chapter` can DENY the duplicate before it exists.

THE DESIGN, so a failure here reads correctly:
* State is keyed on `session_id`, NEVER `prompt_id` —— task-notification wakes
  and Stop-block continuations mint fresh prompt ids (clint's and hlint's
  docstrings), so a prompt-id key re-arms exactly when it must stay armed.
* The ledger is blint's own stage log (the mlint/hlint precedent —— no second
  state file to drift): `marker_recorded` arms, `prompt_reset` disarms, and
  the newest of the two for the session wins.
* The reset rides the GENUINE-prompt path only: a Stop-block continuation
  fires no UserPromptSubmit at all (the exact 30/07 failure mode), and a
  `<task-notification>` wake's UserPromptSubmit must be ignored.
* SECOND BELT —— the transcript anchor: `marker_recorded` stores the uuid of
  the turn's genuine user line, and the deny requires that anchor to STILL be
  the transcript's newest genuine user line. So a lost or dead reset path can
  never deny past its own turn: a new genuine prompt changes the anchor and
  the guard falls open.
* FAIL OPEN ON ANY DOUBT: a false deny blocks a LEGITIMATE marker and breaks
  the navigation this guard exists to protect. Lost log, unreadable payload,
  missing sid, foreign cwd, sub-agent payload, unreadable anchor —— all ALLOW.
  The price of failing open is one duplicate marker, i.e. exactly the
  pre-guard status quo, never anything worse.

Run: python3 cp/ccsim/sandbox/blint_marker_guard_regression_test.py
"""

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BLINT = os.path.join(REPO, "cscpt", "blint.py")
SETTINGS = os.path.expanduser("~/.claude/settings.json")
TOOL = "mcp__ccd_session__mark_chapter"

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


def user_rec(text, uuid):
    return {"type": "user", "uuid": uuid,
            "message": {"role": "user", "content": text}}


def write_transcript(path, records):
    with open(path, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


def run_stage(stage, payload, log):
    env = dict(os.environ, BLINT_LOG=log)
    return subprocess.run(
        [sys.executable, BLINT, stage], input=json.dumps(payload),
        capture_output=True, text=True, env=env, timeout=60)


def pre_payload(tp, sid="cafebabe0001", cwd=REPO, tool=TOOL, extra=None):
    p = {"hook_event_name": "PreToolUse", "tool_name": tool,
         "tool_input": {"title": "Turn 3"}, "session_id": sid,
         "transcript_path": tp}
    if cwd is not None:
        p["cwd"] = cwd
    if extra:
        p.update(extra)
    return p


def post_payload(tp, sid="cafebabe0001", response=None):
    return {"hook_event_name": "PostToolUse", "tool_name": TOOL,
            "tool_input": {"title": "Turn 3"}, "session_id": sid,
            "transcript_path": tp, "cwd": REPO,
            "tool_response": response if response is not None else {"ok": True}}


def prompt_payload(text, sid="cafebabe0001", cwd=REPO):
    return {"hook_event_name": "UserPromptSubmit", "prompt": text,
            "session_id": sid, "cwd": cwd}


def main():
    if not os.path.isfile(BLINT):
        check(False, "cscpt/blint.py exists", "script absent —— nothing to test")
        print("\n0/%d passed" % max(checks, 1))
        return 1

    tmp = tempfile.mkdtemp(prefix="blint_marker_")
    tp = os.path.join(tmp, "t.jsonl")
    log = os.path.join(tmp, ".blint.log")
    write_transcript(tp, [user_rec("start the turn", "uuid-turn-1")])

    # --- B1: virgin state allows
    p = run_stage("marker-pre", pre_payload(tp), log)
    check(p.returncode == 0, "B1 first marker attempt is ALLOWED (no state)",
          "rc=%s stderr=%r" % (p.returncode, p.stderr[:160]))

    # --- B2: recorder arms the guard
    p = run_stage("marker-post", post_payload(tp), log)
    txt = open(log, encoding="utf-8").read() if os.path.isfile(log) else ""
    check(p.returncode == 0 and "marker_recorded" in txt,
          "B2 marker-post records the marker (ledger line present)",
          txt[-200:])

    # --- B3: second attempt in the SAME turn is DENIED, exit 2, stderr says why
    p = run_stage("marker-pre", pre_payload(tp), log)
    check(p.returncode == 2 and "TEA2" in p.stderr,
          "B3 duplicate marker in the same turn is DENIED (exit 2, names TEA2)",
          "rc=%s stderr=%r" % (p.returncode, p.stderr[:200]))

    # --- B4: a Stop-block continuation fires no UserPromptSubmit —— the deny
    # must therefore survive doing nothing at all in between (the 30/07 mode).
    p = run_stage("marker-pre", pre_payload(tp), log)
    check(p.returncode == 2,
          "B4 still denied with no intervening prompt (Stop-block continuation)",
          "rc=%s" % p.returncode)

    # --- B5: a <task-notification> wake must NOT reset
    p = run_stage("prompt", prompt_payload(
        "<task-notification><task-id>t9</task-id>"
        "<status>completed</status></task-notification>"), log)
    q = run_stage("marker-pre", pre_payload(tp), log)
    check(p.returncode == 0 and q.returncode == 2,
          "B5 a task-notification wake does not disarm the guard",
          "prompt rc=%s pre rc=%s" % (p.returncode, q.returncode))

    # --- B6: a GENUINE prompt resets; the next marker is allowed again
    write_transcript(tp, [user_rec("start the turn", "uuid-turn-1"),
                          user_rec("next turn please", "uuid-turn-2")])
    p = run_stage("prompt", prompt_payload("next turn please"), log)
    q = run_stage("marker-pre", pre_payload(tp), log)
    check(p.returncode == 0 and q.returncode == 0,
          "B6 a genuine prompt disarms the guard —— next marker allowed",
          "prompt rc=%s pre rc=%s" % (p.returncode, q.returncode))

    # --- B7: SECOND BELT —— reset path dead, but the transcript anchor moved.
    log7 = os.path.join(tmp, ".blint7.log")
    tp7 = os.path.join(tmp, "t7.jsonl")
    write_transcript(tp7, [user_rec("turn one", "uuid-A")])
    run_stage("marker-post", post_payload(tp7, sid="cafebabe0007"), log7)
    p = run_stage("marker-pre", pre_payload(tp7, sid="cafebabe0007"), log7)
    check(p.returncode == 2, "B7a armed within the same turn (control)",
          "rc=%s" % p.returncode)
    write_transcript(tp7, [user_rec("turn one", "uuid-A"),
                           user_rec("turn two —— but the reset hook is dead",
                                    "uuid-B")])
    p = run_stage("marker-pre", pre_payload(tp7, sid="cafebabe0007"), log7)
    check(p.returncode == 0,
          "B7b anchor moved (new genuine user line) -> guard falls OPEN even "
          "with no prompt_reset —— a dead reset path cannot deny forever",
          "rc=%s stderr=%r" % (p.returncode, p.stderr[:160]))

    # --- B8: lost state file -> allow (the stated price: one duplicate marker)
    log8 = os.path.join(tmp, ".blint8.log")
    write_transcript(tp, [user_rec("start the turn", "uuid-turn-1")])
    run_stage("marker-post", post_payload(tp), log8)
    os.unlink(log8)
    p = run_stage("marker-pre", pre_payload(tp), log8)
    check(p.returncode == 0,
          "B8 lost ledger -> ALLOW (fail open; worst case is the old status quo)",
          "rc=%s" % p.returncode)

    # --- B9–B11: scope, sub-agent, wrong tool —— all allow
    log9 = os.path.join(tmp, ".blint9.log")
    run_stage("marker-post", post_payload(tp), log9)
    p = run_stage("marker-pre",
                  pre_payload(tp, cwd="/Users/somebody/other_project"), log9)
    check(p.returncode == 0,
          "B9 foreign cwd -> ALLOW (a blocking guard never leaves the repo)",
          "rc=%s" % p.returncode)
    p = run_stage("marker-pre",
                  pre_payload(tp, extra={"agent_id": "agent-1"}), log9)
    check(p.returncode == 0, "B10 sub-agent payload -> ALLOW", "rc=%s" % p.returncode)
    p = run_stage("marker-pre", pre_payload(tp, tool="TodoWrite"), log9)
    check(p.returncode == 0,
          "B11 a non-mark_chapter tool -> ALLOW (defence behind the matcher)",
          "rc=%s" % p.returncode)

    # --- B12: a failed mark_chapter is NOT recorded (a retry stays legal)
    log12 = os.path.join(tmp, ".blint12.log")
    p = run_stage("marker-post", post_payload(tp, response={"is_error": True}),
                  log12)
    q = run_stage("marker-pre", pre_payload(tp), log12)
    check(p.returncode == 0 and q.returncode == 0,
          "B12 an errored mark_chapter is not recorded —— the retry is allowed",
          "post rc=%s pre rc=%s" % (p.returncode, q.returncode))

    # --- B13: missing session_id -> allow (fail open on any doubt)
    pay = pre_payload(tp)
    del pay["session_id"]
    p = run_stage("marker-pre", pay, log9)
    check(p.returncode == 0, "B13 missing session_id -> ALLOW", "rc=%s" % p.returncode)

    # --- B14: hand invocation refuses (stdin-guard convention)
    p = subprocess.run([sys.executable, BLINT, "marker-pre", "some_file.md"],
                       capture_output=True, text=True, timeout=30,
                       stdin=subprocess.DEVNULL)
    check(p.returncode == 3 and "NOTHING WAS CHECKED" in p.stderr,
          "B14 argv naming a file refuses on stderr, exit 3",
          "rc=%s stderr=%r" % (p.returncode, p.stderr[:160]))

    # --- B15: all three stages registered live, correct events and matchers
    try:
        with open(SETTINGS, encoding="utf-8") as fh:
            hooks = json.load(fh).get("hooks", {})
    except Exception as exc:
        hooks = {}
        check(False, "B15 ~/.claude/settings.json readable", repr(exc))

    def find(event, needle, want_matcher=None):
        for g in hooks.get(event, []):
            for h in g.get("hooks", []):
                c = h.get("command", "")
                if "blint.py" in c and c.rstrip("'\" ").endswith(needle):
                    if want_matcher is None or g.get("matcher") == want_matcher:
                        return True
        return False

    check(find("PreToolUse", "marker-pre", TOOL),
          "B15 marker-pre registered on PreToolUse, matched to %s" % TOOL)
    check(find("PostToolUse", "marker-post", TOOL),
          "B16 marker-post registered on PostToolUse, matched to %s" % TOOL)
    check(find("UserPromptSubmit", "prompt"),
          "B17 prompt reset registered on UserPromptSubmit")

    print()
    if failures:
        print("%d/%d passed —— FAILURES:" % (checks - len(failures), checks))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("%d/%d passed —— marker guard contract intact." % (checks, checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
