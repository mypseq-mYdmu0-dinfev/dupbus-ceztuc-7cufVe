#!/usr/bin/env python3
"""Regression test for cscpt/alint.py + cscpt/alint_hook.sh —— the TEA1
IN-FLIGHT GATE that blocks `git commit` / `git push` whilst a dispatched
sub-agent is still running.

WHY this test exists (coding.md: "a fix without its test is unfinished"):
root CLAUDE.md §3.1.6 requires that Turn-End Actions happen only once no
sub-agent is in flight. That rule was breached at least four times across two
sessions —— never through misreading it, always through a conscious judgement
call that the outstanding agent "would not matter", after which it returned
with substantive work. The gate replaces the judgement with a mechanism, so
the cases below pin the mechanism.

THE ONE THAT MATTERS MOST is A1/A2, the DISPATCH-ACK TRAP: a dispatched
agent's tool_result lands within milliseconds saying `async_launched`, so any
design that treats "the Agent tool returned" as "the agent finished" is
inverted —— it would clear the gate the instant an agent started. A1 feeds a
transcript holding exactly that ack and asserts the gate still BLOCKS; A2
feeds the same transcript plus the later completion notification and asserts
it clears. Together they encode the precise failing scenario the gate exists
to survive.

Fixtures are mined from this Mac's REAL transcripts (coding.md: "Mine
historical/real data for fixtures") —— the record shapes below are the ones
observed across 368 historical dispatches, including all THREE record shapes a
completion notification arrives in (`attachment`, `queue-operation`, `user`),
which a single-shape parser would silently under-read.

Self-contained: every transcript, output file and payload is synthesised at run
time in a throwaway tempdir, removed afterwards; no repo file is read or
written, and `ALINT_LOG` is redirected so the real log is neither read nor
polluted. The gate is driven END-TO-END through its actual stdin/exit-code hook
contract (and, for the shim cases, through `alint_hook.sh` itself), never by
importing its internals —— a rule that only works when called directly is not
wired (coding.md: "'Exists + unit-tested' != done").

Run directly:

    python3 "cp/ccsim/sandbox/alint_regression_test.py"

Exits 0 if every case matches its expected verdict, 1 otherwise (with a
per-case PASS/FAIL report on stdout, and the raw stdout/stderr on any FAIL so
a break is immediately diagnosable without re-running by hand).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", ".."))
ALINT = os.path.join(REPO_ROOT, "cscpt", "alint.py")
ALINT_HOOK = os.path.join(REPO_ROOT, "cscpt", "alint_hook.sh")

# A real agent id shape: `a` + 16 hex (matched every one of 368 historical
# dispatches). Two distinct ones so multi-agent cases are unambiguous.
AGENT_A = "a3e737d9dc757e1ca"
AGENT_B = "a96d2e762fbd7e054"

_TMP = None          # per-run scratch dir, torn down in main()
_LOG = None          # redirected ALINT_LOG inside _TMP


# ---------------------------------------------------------------------------
# Fixture builders —— transcript RECORDS in the exact shapes observed live.
# ---------------------------------------------------------------------------

def rec_agent_dispatch_ack(agent_id, desc, out_path, sidechain=False):
    """The Agent tool's tool_result, as the harness really writes it: it
    arrives within milliseconds of the dispatch and says `async_launched`.
    THIS IS THE TRAP —— it is an acknowledgement, never a completion."""
    return {
        "type": "user",
        "isSidechain": sidechain,
        "timestamp": "2026-08-01T10:12:20.165Z",
        "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "toolu_%s" % agent_id[:12],
             "content": [{"type": "text",
                          "text": "Async agent launched successfully."}]}]},
        "toolUseResult": {
            "isAsync": True, "status": "async_launched", "agentId": agent_id,
            "description": desc, "prompt": "…", "outputFile": out_path,
            "canReadOutputFile": True, "resolvedModel": "claude-opus-5",
        },
    }


def _notification_xml(task_id, status="completed"):
    return ("<task-notification>\n<task-id>%s</task-id>\n"
            "<tool-use-id>toolu_%s</tool-use-id>\n<status>%s</status>\n"
            "<summary>Agent finished</summary>\n</task-notification>"
            % (task_id, task_id[:12], status))


def rec_notification(task_id, shape="user", status="completed"):
    """A completion notification in ONE of its three observed record shapes.
    Counted across this Mac's history: attachment 233, queue-operation 431,
    user 270 —— so a parser keyed on any single shape under-reads badly."""
    xml = _notification_xml(task_id, status)
    if shape == "user":
        return {"type": "user", "isSidechain": False,
                "timestamp": "2026-08-01T10:20:00.000Z",
                "message": {"role": "user", "content": xml}}
    if shape == "attachment":
        return {"type": "attachment", "isSidechain": False,
                "timestamp": "2026-08-01T10:20:00.000Z",
                "attachment": {"type": "queued_command", "prompt": xml,
                               "commandMode": "task-notification"}}
    return {"type": "queue-operation", "isSidechain": False,
            "timestamp": "2026-08-01T10:20:00.000Z",
            "operation": {"prompt": xml}}


def rec_sendmessage_resume(agent_id):
    """`SendMessage` to a rested agent restarts it —— it will notify again, so
    the gate must treat this as a fresh liveness event."""
    return {
        "type": "user", "isSidechain": False,
        "timestamp": "2026-08-01T10:30:00.000Z",
        "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "toolu_sendmsg",
             "content": [{"type": "text", "text": "ok"}]}]},
        "toolUseResult": {
            "success": True,
            "message": ("Agent \"%s\" had no active task; resumed from "
                        "transcript in the background with your message."
                        % agent_id),
        },
    }


def rec_background_bash():
    """A BACKGROUND BASH launch —— `backgroundTaskId`, no `isAsync`. Excluded
    on purpose: root CLAUDE.md §9.05 mandates a persistent Monitor sleep-loop,
    which would otherwise block every commit for the whole session."""
    return {"type": "user", "isSidechain": False,
            "timestamp": "2026-08-01T10:15:00.000Z",
            "message": {"role": "user", "content": []},
            "toolUseResult": {"backgroundTaskId": "beee1p48l", "stdout": "",
                              "stderr": "", "interrupted": False,
                              "isImage": False, "noOutputExpected": True}}


def rec_workflow_launch():
    """A WORKFLOW launch —— `taskId` + `taskType`, no `agentId`. Out of scope
    for this gate (documented gap), so it must not be counted as an agent."""
    return {"type": "user", "isSidechain": False,
            "timestamp": "2026-08-01T10:16:00.000Z",
            "message": {"role": "user", "content": []},
            "toolUseResult": {"status": "async_launched", "taskId": "wn9svy9x9",
                              "taskType": "local_workflow",
                              "workflowName": "kickoff",
                              "transcriptDir": "/tmp/nowhere"}}


def rec_noise():
    """An ordinary assistant line —— the overwhelming majority of a real
    transcript, and the thing the pre-filter must skip without misreading."""
    return {"type": "assistant", "isSidechain": False,
            "timestamp": "2026-08-01T10:14:00.000Z",
            "message": {"role": "assistant",
                        "content": [{"type": "text", "text": "working"}]}}


def write_transcript(name, records):
    path = os.path.join(_TMP, name)
    with open(path, "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")
    return path


def agent_output(agent_id, age_s=0.0):
    """A stand-in for the agent's own transcript —— the file whose mtime the
    gate uses as a liveness clock. `age_s` back-dates it to exercise the
    staleness release."""
    path = os.path.join(_TMP, "out_%s" % agent_id)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("x")
    if age_s:
        old = time.time() - age_s
        os.utime(path, (old, old))
    return path


def payload(command, transcript_path, cwd=REPO_ROOT, session_id="alint-rt",
            agent_id=None):
    """A realistic PreToolUse:Bash payload, field-for-field as captured live
    from this harness. `agent_id` (with `agent_type`) is present ONLY on a
    sub-agent's call —— that pairing is the sub-agent discriminator, and it is
    reproduced here exactly because the plausible-looking alternative
    (transcript_path pointing at the agent's own file) is FALSE: a sub-agent's
    payload carries the MAIN session transcript."""
    data = {
        "session_id": session_id,
        "transcript_path": transcript_path,
        "prompt_id": "pid-alint-rt",
        "permission_mode": "bypassPermissions",
        "hook_event_name": "PreToolUse",
        "cwd": cwd,
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "tool_use_id": "toolu_alint_rt",
    }
    if agent_id:
        data["agent_id"] = agent_id
        data["agent_type"] = "general-purpose"
    return json.dumps(data)


# ---------------------------------------------------------------------------
# Runners
# ---------------------------------------------------------------------------

def run(raw, env_extra=None, via_shim=False):
    env = dict(os.environ)
    env["ALINT_LOG"] = _LOG
    env.pop("ALINT_OFF", None)
    if env_extra:
        env.update(env_extra)
    cmd = (["bash", ALINT_HOOK] if via_shim else ["python3", ALINT])
    return subprocess.run(cmd, input=raw, capture_output=True, text=True,
                          env=env, cwd=REPO_ROOT)


def advice(result):
    """The model-visible `additionalContext` string, or "" when none."""
    try:
        return (json.loads(result.stdout or "{}")
                .get("hookSpecificOutput", {}).get("additionalContext", ""))
    except Exception:
        return ""


def log_lines():
    try:
        with open(_LOG, "r", encoding="utf-8") as fh:
            return [l for l in fh.read().splitlines() if l.strip()]
    except Exception:
        return []


_RESULTS = []


def check(label, ok, result=None):
    _RESULTS.append(bool(ok))
    print("[%s] %s" % ("PASS" if ok else "FAIL", label))
    if not ok and result is not None:
        print("        exit=%r" % result.returncode)
        print("        stdout=%r" % result.stdout[:400])
        print("        stderr=%r" % result.stderr[:400])


# ---------------------------------------------------------------------------

def main():
    global _TMP, _LOG
    _TMP = tempfile.mkdtemp(prefix="alint_rt_")
    _LOG = os.path.join(_TMP, "alint.log")
    try:
        return _run_all()
    finally:
        shutil.rmtree(_TMP, ignore_errors=True)


def _run_all():
    # === A. THE DISPATCH-ACK TRAP (the bug this gate is built around) ======
    out_a = agent_output(AGENT_A)
    t_ack = write_transcript("ack.jsonl", [
        rec_noise(),
        rec_agent_dispatch_ack(AGENT_A, "Build the gate", out_a),
        rec_noise(),
    ])
    r = run(payload("git commit -m 'x'", t_ack))
    check("A1 — dispatch ack alone is NOT completion: commit BLOCKED",
          r.returncode == 2 and AGENT_A in r.stderr, r)

    t_done = write_transcript("done.jsonl", [
        rec_agent_dispatch_ack(AGENT_A, "Build the gate", out_a),
        rec_notification(AGENT_A, "queue-operation"),
    ])
    r = run(payload("git commit -m 'x'", t_done))
    check("A2 — dispatch + completion notification: commit ALLOWED",
          r.returncode == 0 and not r.stderr.strip(), r)

    # === B. All three notification record shapes clear the gate ============
    for shape in ("user", "attachment", "queue-operation"):
        t = write_transcript("shape_%s.jsonl" % shape, [
            rec_agent_dispatch_ack(AGENT_A, "d", out_a),
            rec_notification(AGENT_A, shape),
        ])
        r = run(payload("git push", t))
        check("B — notification shape %r clears the gate" % shape,
              r.returncode == 0, r)

    # === C. Resumption re-arms the gate ====================================
    t_resume = write_transcript("resume.jsonl", [
        rec_agent_dispatch_ack(AGENT_A, "d", out_a),
        rec_notification(AGENT_A, "user"),
        rec_sendmessage_resume(AGENT_A),
    ])
    r = run(payload("git commit -m x", t_resume))
    check("C1 — SendMessage resume after a rest re-BLOCKS",
          r.returncode == 2 and AGENT_A in r.stderr, r)

    t_resume_done = write_transcript("resume_done.jsonl", [
        rec_agent_dispatch_ack(AGENT_A, "d", out_a),
        rec_notification(AGENT_A, "user"),
        rec_sendmessage_resume(AGENT_A),
        rec_notification(AGENT_A, "user"),
    ])
    r = run(payload("git commit -m x", t_resume_done))
    check("C2 — resume then rest again: ALLOWED", r.returncode == 0, r)

    # === D. Only Agent dispatches count ====================================
    t_bg = write_transcript("bg.jsonl",
                            [rec_background_bash(), rec_workflow_launch()])
    r = run(payload("git commit -m x", t_bg))
    check("D1 — background bash + workflow launches are NOT agents: ALLOWED",
          r.returncode == 0, r)

    out_b = agent_output(AGENT_B)
    t_mixed = write_transcript("mixed.jsonl", [
        rec_agent_dispatch_ack(AGENT_A, "first", out_a),
        rec_agent_dispatch_ack(AGENT_B, "second", out_b),
        rec_background_bash(),
        rec_notification(AGENT_A, "attachment"),
    ])
    r = run(payload("git commit -m x", t_mixed))
    check("D2 — one of two agents rested: still BLOCKED, names only the live one",
          r.returncode == 2 and AGENT_B in r.stderr and AGENT_A not in r.stderr,
          r)

    # === E. Sub-agent lines never count as main-session events =============
    t_side = write_transcript("side.jsonl", [
        rec_agent_dispatch_ack(AGENT_A, "d", out_a, sidechain=True)])
    r = run(payload("git commit -m x", t_side))
    check("E — an isSidechain dispatch record is ignored: ALLOWED",
          r.returncode == 0, r)

    # === F. Trigger matching —— positives ==================================
    positives = (
        "git commit -m 'x'",
        "git push",
        "git push origin main",
        "cd \"/tmp\" && git add -A && git commit -m 'y' && git push",
        "git -C /some/path commit -m z",
        "/usr/bin/git push",
        "GIT_AUTHOR_NAME=x git commit -m q",
        "git --git-dir=/tmp/.git commit -m q",
    )
    for cmd in positives:
        r = run(payload(cmd, t_ack))
        check("F — TEA1 recognised, BLOCKED: %r" % cmd, r.returncode == 2, r)

    # === G. Trigger matching —— negatives (a false block is expensive) =====
    negatives = (
        "git status",
        "git log --oneline --grep=commit",
        "echo \"git commit -m x\"",
        "grep -rn 'git push' .",
        "man git-commit",
        "ls -la",
        "git diff --stat",
        "python3 -c \"print('git commit')\"",
    )
    for cmd in negatives:
        r = run(payload(cmd, t_ack))
        check("G — not TEA1, ALLOWED: %r" % cmd,
              r.returncode == 0 and not r.stderr.strip(), r)

    # === H. Sub-agent exemption ============================================
    # H1 pins the LIVE-CAPTURED discriminator. The first implementation used
    # the transcript path instead, on the reasonable-but-false belief that a
    # sub-agent's payload names its own transcript; it names the MAIN one, so
    # that version blocked every sub-agent commit whilst a sibling ran. H2 is
    # the pin against reintroducing it: the payload here is a sub-agent's ——
    # main transcript path and all —— and must still be exempt.
    r = run(payload("git commit -m x", t_ack, agent_id=AGENT_B))
    check("H1 — `agent_id` in the payload marks a sub-agent: ALLOWED",
          r.returncode == 0, r)
    check("H2 — ...even though its transcript_path is the MAIN session file "
          "(the assumption that broke the first version)",
          r.returncode == 0 and "subagents" not in t_ack, r)
    check("H3 — the exemption is recorded as action=subagent",
          any("action=subagent" in l for l in log_lines()))

    r = run(payload("git commit -m x", t_ack))
    check("H4 — no `agent_id` means the MAIN agent: still BLOCKED",
          r.returncode == 2, r)

    # H5: the inert second signal is kept as insurance against a future
    # harness that DOES point the payload at the agent's own transcript.
    sub_tp = os.path.join(_TMP, "subagents")
    os.makedirs(sub_tp, exist_ok=True)
    sub_file = os.path.join(sub_tp, "agent-%s.jsonl" % AGENT_A)
    shutil.copyfile(t_ack, sub_file)
    r = run(payload("git commit -m x", sub_file))
    check("H5 — a `/subagents/` transcript path is exempt too (insurance)",
          r.returncode == 0, r)

    # === I. Repo scope —— a blocking lint must not police other repos ======
    r = run(payload("git commit -m x", t_ack, cwd="/tmp"))
    check("I1 — out-of-repo cwd: ALLOWED", r.returncode == 0, r)
    r = run(payload("git commit -m x", t_ack, cwd=REPO_ROOT + "-sibling"))
    check("I2 — a `-sibling` path is NOT a sub-path of the repo: ALLOWED",
          r.returncode == 0, r)
    r = run(payload("git commit -m x", t_ack,
                    cwd=os.path.join(REPO_ROOT, "cscpt")))
    check("I3 — a genuine sub-path IS in scope: BLOCKED", r.returncode == 2, r)

    # === J. Fail OPEN, but never silently ==================================
    r = run(payload("git commit -m x", os.path.join(_TMP, "missing.jsonl")))
    check("J1 — unreadable transcript: ALLOWED (fail open)",
          r.returncode == 0, r)
    check("J2 — ...and the fail-open is VISIBLE to the model",
          "UNKNOWN" in advice(r), r)
    check("J3 — ...and logged as its own stage",
          any("action=no_transcript" in l for l in log_lines()))

    for bad in ("{not json", "", json.dumps([1, 2, 3])):
        r = run(bad)
        check("J4 — malformed payload %r: exit 0, silent" % bad[:12],
              r.returncode == 0 and not r.stderr.strip(), r)

    # === K. Staleness release —— the gate can never brick a repo ===========
    stale_out = agent_output("stale", age_s=60 * 60 * 3)
    t_stale = write_transcript("stale.jsonl", [
        rec_agent_dispatch_ack(AGENT_A, "never returned", stale_out)])
    r = run(payload("git commit -m x", t_stale))
    check("K1 — an agent quiet past the threshold is RELEASED: ALLOWED",
          r.returncode == 0, r)
    check("K2 — ...and the release is announced, never silent",
          "stale" in advice(r).lower() and AGENT_A in advice(r), r)
    check("K3 — ...and logged distinctly",
          any("action=stale_release" in l for l in log_lines()))

    t_noout = write_transcript("noout.jsonl", [
        rec_agent_dispatch_ack(AGENT_A, "no output file", None)])
    r = run(payload("git commit -m x", t_noout))
    check("K4 — an un-ageable agent stays LIVE (conservative per agent)",
          r.returncode == 2, r)

    # === L. Break glass ====================================================
    r = run(payload("git commit -m x", t_ack), env_extra={"ALINT_OFF": "1"})
    check("L1 — ALINT_OFF disables the gate: ALLOWED", r.returncode == 0, r)
    check("L2 — ...and says so, so a disable cannot go unnoticed",
          "DISABLED" in advice(r), r)

    # === M. Liveness probe (proves WIRING, not just the script) ============
    r = run(payload("echo ALINT_PROBE", t_ack))
    check("M1 — the probe answers ALIVE without blocking",
          r.returncode == 0 and "ALIVE" in advice(r), r)
    check("M2 — the probe logs the transcript filename, which settles "
          "main-vs-sub-agent", any("action=probe" in l and ".jsonl" in l
                                   for l in log_lines()))

    # === N. Per-invocation logging (hook_guide § 7.7) ======================
    before = len(log_lines())
    run(payload("git status", t_ack))
    check("N — every invocation logs a line, so 'never fired' is detectable",
          len(log_lines()) == before + 1)

    # === O. The shim ========================================================
    r = run(payload("ls -la", t_ack), via_shim=True)
    check("O1 — shim: a non-git command exits 0 with no output",
          r.returncode == 0 and not r.stdout.strip() and not r.stderr.strip(),
          r)
    before = len(log_lines())
    run(payload("ls -la", t_ack), via_shim=True)
    check("O2 — shim: a non-git command never spawns Python (no log line)",
          len(log_lines()) == before)
    r = run(payload("git commit -m x", t_ack), via_shim=True)
    check("O3 — shim: a commit passes through and the block survives it",
          r.returncode == 2 and AGENT_A in r.stderr, r)
    r = run(payload("echo ALINT_PROBE", t_ack), via_shim=True)
    check("O4 — shim: the probe token passes through", "ALIVE" in advice(r), r)

    print()
    passed = sum(1 for x in _RESULTS if x)
    print("%d/%d passed" % (passed, len(_RESULTS)))
    return 0 if passed == len(_RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
