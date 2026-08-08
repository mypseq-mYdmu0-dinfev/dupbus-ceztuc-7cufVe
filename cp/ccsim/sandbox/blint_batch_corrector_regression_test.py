#!/usr/bin/env python3
"""Regression suite —— blint.py `batch` stage (PostToolBatch mid-turn chat corrector).

WHAT THIS PINS. Root CLAUDE.md §3.1 forbids chat prose; clint (Stop) detects a
breach only after the turn has ended, and hlint tallies it only at the NEXT
prompt. PostToolBatch is the one MID-TURN channel that reaches the model at
zero extra invocations (hook_guide §6.11): its exit-0
`hookSpecificOutput.additionalContext` rides the already-scheduled next model
request. blint's `batch` stage reads the transcript tail, classifies the
assistant chat lines since the last GENUINE user line with clint's own line
contracts, and injects ONE correction per new breach content.

THE INVARIANTS THAT MUST NEVER ROT, each pinned below:
* EXIT 0 ALWAYS on a parsed payload —— PostToolBatch exit 2 KILLS the agentic
  loop (stderr to the user only; verified in the installed binary 2.1.222's
  own registry text), so the turn would die and the TEAs would never run.
* Dedup by CONTENT HASH, never prompt id —— task-notification wakes mint fresh
  prompt ids (clint's and hlint's docstrings both record the observed sevenfold
  re-fire), so a prompt-id ledger re-corrects the same window on every wake.
* Sub-agent payloads (`agent_id`/`agent_type`) are SKIPPED —— an SA's chat is
  its return value, not policed chat (hook_guide §5.6.1).
* Self-scoped and SILENT elsewhere —— this is a model-visible injection, so a
  foreign cockpit must never be nagged about a rule it never adopted (the
  hlint-tally precedent, opposite of clint's fail-open, both deliberate).
* clint's exemptions are honoured (`override`, `yn`, `sic`, `DATS`, the lone
  dot, the §5.3–§5.4 sentinel lists) —— a mid-turn corrector that fires on
  SANCTIONED chat teaches the model to distrust every correction.

Run: python3 cp/ccsim/sandbox/blint_batch_corrector_regression_test.py
"""

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BLINT = os.path.join(REPO, "cscpt", "blint.py")
READER = os.path.dirname(REPO)          # the parent GitHub/ folder
SETTINGS = os.path.expanduser("~/.claude/settings.json")

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


def user_rec(text, uuid="u1"):
    return {"type": "user", "uuid": uuid,
            "message": {"role": "user", "content": text}}


def asst_rec(text, uuid="a1"):
    return {"type": "assistant", "uuid": uuid,
            "message": {"role": "assistant",
                        "content": [{"type": "text", "text": text}]}}


def write_transcript(path, records):
    with open(path, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


def run_batch(transcript, log, cwd=REPO, sid="feedc0ffee11", extra=None,
              stage="batch"):
    payload = {"hook_event_name": "PostToolBatch", "session_id": sid,
               "transcript_path": transcript, "tool_calls": []}
    if cwd is not None:
        payload["cwd"] = cwd
    if extra:
        payload.update(extra)
    env = dict(os.environ, BLINT_LOG=log)
    return subprocess.run(
        [sys.executable, BLINT, stage], input=json.dumps(payload),
        capture_output=True, text=True, env=env, timeout=60)


def fired(proc):
    """(fired?, additionalContext text) from a run's stdout."""
    out = proc.stdout.strip()
    if not out:
        return False, ""
    try:
        data = json.loads(out)
    except Exception:
        return False, out
    hso = data.get("hookSpecificOutput") or {}
    if hso.get("hookEventName") != "PostToolBatch":
        return False, out
    return True, hso.get("additionalContext") or ""


def main():
    if not os.path.isfile(BLINT):
        check(False, "cscpt/blint.py exists", "script absent —— nothing to test")
        print("\n0/%d passed" % max(checks, 1))
        return 1

    tmp = tempfile.mkdtemp(prefix="blint_batch_")
    tp = os.path.join(tmp, "t.jsonl")
    log = os.path.join(tmp, ".blint.log")

    # --- A1–A3: fire on prose, dedup on content hash, re-fire on NEW content
    write_transcript(tp, [user_rec("please fix the bug"),
                          asst_rec("Working on it now, hold tight.")])
    p = run_batch(tp, log)
    ok, ctx = fired(p)
    check(p.returncode == 0 and ok and "prose" in ctx,
          "A1 prose after a genuine user line fires a correction (exit 0)",
          "rc=%s ctx=%r stderr=%r" % (p.returncode, ctx[:120], p.stderr[:120]))
    check(p.stderr == "", "A1b nothing on stderr when firing", repr(p.stderr[:120]))

    p = run_batch(tp, log)
    ok2, _ = fired(p)
    check(p.returncode == 0 and not ok2,
          "A2 identical breach content is corrected ONCE (content-hash dedup)",
          "rc=%s out=%r" % (p.returncode, p.stdout[:120]))

    write_transcript(tp, [user_rec("please fix the bug"),
                          asst_rec("Working on it now, hold tight."),
                          asst_rec("Nearly done, running tests.", uuid="a2")])
    p = run_batch(tp, log)
    ok3, ctx3 = fired(p)
    check(p.returncode == 0 and ok3 and " 2 " in ctx3,
          "A3 a NEW prose line changes the hash —— fires again, counting 2",
          "rc=%s ctx=%r" % (p.returncode, ctx3[:160]))

    # --- A4: the dedup key must NOT be the prompt id —— same content under a
    # fresh prompt_id stays silent (the task-notification-wake scenario).
    p = run_batch(tp, log, extra={"prompt_id": "freshly-minted-wake-id"})
    ok4, _ = fired(p)
    check(p.returncode == 0 and not ok4,
          "A4 fresh prompt_id, same content -> still silent (hash, not id)",
          p.stdout[:120])

    # --- A5–A7: clean shapes stay silent
    log2 = os.path.join(tmp, ".blint2.log")
    tp2 = os.path.join(tmp, "t2.jsonl")
    write_transcript(tp2, [user_rec("go"),
                           asst_rec("✅ `universal/glossary.md`, `universal/numbered.md`")])
    p = run_batch(tp2, log2)
    ok5, _ = fired(p)
    check(p.returncode == 0 and not ok5,
          "A5 a clean declaration line stays silent", p.stdout[:120])

    write_transcript(tp2, [user_rec("go"), asst_rec(".")])
    p = run_batch(tp2, log2)
    ok6, _ = fired(p)
    check(p.returncode == 0 and not ok6,
          "A6 the lone-dot turn stays silent (root §3.1.8.2)", p.stdout[:120])

    write_transcript(tp2, [
        user_rec("go"),
        asst_rec("\U0001f6a8 Compaction Detected —— stopped all tasks.\n"
                 "Lost reads still useful:\n- `universal/close.md`\n"
                 "Remainder:\n- `cp/career/CP_notes.md`")])
    p = run_batch(tp2, log2)
    ok7, _ = fired(p)
    check(p.returncode == 0 and not ok7,
          "A7 the §5.3–§5.4 sentinel lists stay silent post-compaction",
          p.stdout[:200])

    # --- A8–A10: scope and sub-agent skips
    write_transcript(tp2, [user_rec("go"), asst_rec("Chatty prose here.")])
    p = run_batch(tp2, log2, cwd="/Users/somebody/other_project")
    ok8, _ = fired(p)
    check(p.returncode == 0 and not ok8,
          "A8 foreign cwd -> silent (model-visible nag never leaves the repo)",
          p.stdout[:120])

    p = run_batch(tp2, log2, cwd=None)
    ok9, _ = fired(p)
    check(p.returncode == 0 and not ok9,
          "A9 no cwd + unrecognisable transcript slug -> silent (conservative)",
          p.stdout[:120])

    p = run_batch(tp2, log2, extra={"agent_id": "agent-123",
                                    "agent_type": "general-purpose"})
    ok10, _ = fired(p)
    check(p.returncode == 0 and not ok10,
          "A10 sub-agent payload (agent_id) -> skipped, silent", p.stdout[:120])

    # --- A11–A14: the four chat exemptions ride the TRIGGER message
    log3 = os.path.join(tmp, ".blint3.log")
    write_transcript(tp2, [user_rec("override —— talk to me in chat"),
                           asst_rec("Here is the chat answer you asked for.")])
    p = run_batch(tp2, log3)
    ok11, _ = fired(p)
    check(p.returncode == 0 and not ok11,
          "A11 `override` in the trigger disarms the corrector", p.stdout[:120])

    write_transcript(tp2, [user_rec("did it work? yn"), asst_rec("Yes")])
    p = run_batch(tp2, log3)
    ok12, _ = fired(p)
    check(p.returncode == 0 and not ok12,
          "A12 ` yn` in the trigger permits the one-word answer", p.stdout[:120])

    write_transcript(tp2, [user_rec("sic how far along?"),
                           asst_rec("Three of five suites green so far.")])
    p = run_batch(tp2, log3)
    ok13, _ = fired(p)
    check(p.returncode == 0 and not ok13,
          "A13 `sic` within its word cap stays exempt", p.stdout[:120])

    write_transcript(tp2, [user_rec("sic how far along?"),
                           asst_rec("Three of five suites are green so far and "
                                    "the other two are still compiling away merrily.")])
    p = run_batch(tp2, log3)
    ok14, ctx14 = fired(p)
    check(p.returncode == 0 and ok14 and "sic_overrun" in ctx14,
          "A14 `sic` past its cap fires, classed sic_overrun",
          "rc=%s ctx=%r" % (p.returncode, ctx14[:160]))

    # --- A15: READER mode (the parent GitHub/ folder) —— zero chat text
    log4 = os.path.join(tmp, ".blint4.log")
    write_transcript(tp2, [user_rec("read this"), asst_rec("Found it, reading now.")])
    p = run_batch(tp2, log4, cwd=READER)
    ok15, ctx15 = fired(p)
    check(p.returncode == 0 and ok15 and "reader" in ctx15,
          "A15 Reader-folder cwd fires under the zero-text rule",
          "rc=%s ctx=%r" % (p.returncode, ctx15[:160]))

    # --- A16: wake records must not move the boundary
    log5 = os.path.join(tmp, ".blint5.log")
    write_transcript(tp2, [
        user_rec("please fix the bug"),
        asst_rec("Chatty progress note."),
        user_rec("<task-notification><task-id>t1</task-id>"
                 "<status>completed</status></task-notification>", uuid="u2")])
    p = run_batch(tp2, log5)
    ok16, _ = fired(p)
    check(p.returncode == 0 and ok16,
          "A16 a <task-notification> user record does NOT hide earlier prose",
          p.stdout[:160])

    # --- A17: byte-bounded tail —— breach within the bound of a huge file
    big = os.path.join(tmp, "big.jsonl")
    pad = json.dumps(asst_rec("x" * 4000)) + "\n"
    with open(big, "w", encoding="utf-8") as fh:
        for _ in range(2500):            # ~10 MB of padding
            fh.write(pad)
        fh.write(json.dumps(user_rec("go", uuid="u9")) + "\n")
        fh.write(json.dumps(asst_rec("Tail prose to be caught.", uuid="a9")) + "\n")
    log6 = os.path.join(tmp, ".blint6.log")
    p = run_batch(big, log6)
    ok17, _ = fired(p)
    check(p.returncode == 0 and ok17 and os.path.getsize(big) > 8 * 1024 * 1024,
          "A17 breach inside the bounded tail of a >8 MB transcript is caught",
          "size=%d rc=%s out=%r" % (os.path.getsize(big), p.returncode,
                                    p.stdout[:120]))

    # --- A18: no boundary in the window -> silent (exemptions unknowable)
    big2 = os.path.join(tmp, "big2.jsonl")
    with open(big2, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(user_rec("go", uuid="u0")) + "\n")
        for _ in range(2500):
            fh.write(pad)
        fh.write(json.dumps(asst_rec("Prose beyond any visible boundary.",
                                     uuid="a8")) + "\n")
    p = run_batch(big2, log6)
    ok18, _ = fired(p)
    check(p.returncode == 0 and not ok18,
          "A18 no genuine user line within the byte bound -> silent, never a guess",
          p.stdout[:120])

    # --- A19: per-invocation stage log
    stages = open(log, encoding="utf-8").read() if os.path.isfile(log) else ""
    check("corrected:" in stages and "stage=" in stages,
          "A19 every invocation logs a named stage; corrections carry the hash mark",
          stages[-200:])

    # --- A20: exit codes —— a breach must NEVER exit 2 (it would kill the loop)
    write_transcript(tp2, [user_rec("go"), asst_rec("Loud prose breach.")])
    p = run_batch(tp2, os.path.join(tmp, ".blint7.log"))
    check(p.returncode == 0,
          "A20 a breach verdict still exits 0 —— exit 2 would kill the agentic loop",
          "rc=%s" % p.returncode)

    # --- A21: hand invocation refuses (stdin-guard convention)
    p = subprocess.run([sys.executable, BLINT, "batch", "some_file.md"],
                       capture_output=True, text=True, timeout=30,
                       stdin=subprocess.DEVNULL)
    check(p.returncode == 3 and "NOTHING WAS CHECKED" in p.stderr,
          "A21 argv naming a file refuses on stderr, exit 3",
          "rc=%s stderr=%r" % (p.returncode, p.stderr[:160]))

    # --- A22: registered live, and the registered path resolves
    try:
        with open(SETTINGS, encoding="utf-8") as fh:
            hooks = json.load(fh).get("hooks", {})
    except Exception as exc:
        hooks = {}
        check(False, "A22 ~/.claude/settings.json readable", repr(exc))
    cmds = [h.get("command", "")
            for g in hooks.get("PostToolBatch", [])
            for h in g.get("hooks", [])]
    reg = [c for c in cmds if "blint.py" in c and c.rstrip("'\" ").endswith("batch")]
    check(bool(reg),
          "A22 blint.py batch is registered on PostToolBatch in the LIVE settings",
          "PostToolBatch commands=%r" % cmds)
    check(all(os.path.isfile(BLINT) for _ in reg) and bool(reg),
          "A23 the registered blint.py path resolves on disk", BLINT)

    print()
    if failures:
        print("%d/%d passed —— FAILURES:" % (checks - len(failures), checks))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("%d/%d passed —— batch corrector contract intact." % (checks, checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
