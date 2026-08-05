#!/usr/bin/env python3
"""Regression test —— `cscpt/tlint.py`, the time-integrity linter.

WHY THIS EXISTS (self-contained; no conversation or comms file explains it):

Root `CLAUDE.md` §2.1.7 mandates Sydney time obtained as
`TZ='Australia/Sydney' date +"%Y%m%d%H%M"`, and §2.2.2 mandates
`at HH:mm on DD/MM/YYYY` for any date a reader sees. The failure those rules
exist to prevent is CC writing a time it did NOT read from a real clock ——
recalled, guessed, or taken from a US-formatted source. `tlint.py` is the
enforcement, in four advisory checks, and this suite pins each one plus the
calibration that keeps it quiet.

EVERY CASE IS DRIVEN THROUGH `tlint_hook.sh`, exactly as `~/.claude/settings.json`
invokes it —— never by importing the module or piping the `.py` directly. Running
the script by hand proves the SCRIPT and nothing else (`cp/ccsim/CLAUDE.md` §8.5);
driving the shim proves the shim's grep gate does not silently drop a payload the
lint would have flagged, which is the one failure a fast path must never have.

THE CALIBRATION IS RE-DERIVED, NOT TRUSTED. Two sweeps run against the LIVE repo
rather than a fixture:
  * `test_live_repo_has_no_us_dates` re-scans every `.md` outside backups and
    archives. It scored ZERO when the rule was written; if a future widening of
    the pattern starts matching legitimate prose, this fails rather than a user
    discovering it.
  * `test_ambiguous_numeric_date_is_not_flagged` pins the deliberate blind spot:
    `08/05/2026` is a correct DD/MM date far more often than it is a US one, so
    the numeric check only fires when the second field exceeds 12.

RUN:
    cd "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
    python3 cp/ccsim/sandbox/tlint_time_integrity_regression_test.py

Dependency-free by design (PyYAML is not installed system-wide on this Mac).
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta

try:
    from zoneinfo import ZoneInfo
    SYD = ZoneInfo("Australia/Sydney")
except Exception:                                    # pragma: no cover
    SYD = None

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SHIM = os.path.join(REPO, "cscpt", "tlint_hook.sh")
SESSIONS = os.path.join(REPO, "sessions")

failures = []
checks = 0
_LOGFILE = None


def record(ok, label, detail=""):
    global checks
    checks += 1
    if ok:
        print(f"[PASS] {label}")
    else:
        print(f"[FAIL] {label} —— {detail}")
        failures.append(label)


# ---------------------------------------------------------------------------
# Driving the REAL registered path
# ---------------------------------------------------------------------------

def run(payload, arg):
    """Feed a payload through `tlint_hook.sh`, as settings.json does. `TLINT_LOG`
    is redirected so the suite never writes to the live stage log."""
    env = dict(os.environ)
    env["TLINT_LOG"] = _LOGFILE
    return subprocess.run(
        ["/bin/sh", SHIM, arg],
        input=json.dumps(payload), capture_output=True, text=True,
        cwd=REPO, env=env,
    )


def advised(res):
    """True if the run emitted a model-visible advisory. Anything non-zero is a
    failure in its own right —— nothing in this lint may ever block."""
    if res.returncode != 0:
        return False
    out = res.stdout.strip()
    if not out:
        return False
    try:
        obj = json.loads(out)
    except Exception:
        return False
    ctx = (obj.get("hookSpecificOutput") or {}).get("additionalContext")
    return isinstance(ctx, str) and "[tlint]" in ctx


def pre_payload(command, **kw):
    d = {"hook_event_name": "PreToolUse", "session_id": "testsess",
         "cwd": REPO, "tool_name": "Bash", "tool_input": {"command": command}}
    d.update(kw)
    return d


def post_payload(path, tool="Write", content=None, **kw):
    ti = {"file_path": path}
    if content is not None:
        ti["content"] = content
    d = {"hook_event_name": "PostToolUse", "session_id": "testsess",
         "cwd": REPO, "tool_name": tool, "tool_input": ti}
    d.update(kw)
    return d


def ts_offset(minutes):
    """A 12-digit TS `minutes` away from real Sydney time."""
    return (datetime.now(SYD) - timedelta(minutes=minutes)).strftime("%Y%m%d%H%M")


def make_transcript(td, name, clocked):
    """A minimal main-session transcript. `clocked=True` includes one real
    `TZ='Australia/Sydney' date` Bash call, exactly as a compliant session has."""
    p = os.path.join(td, name)
    rows = [{"type": "user", "message": {"role": "user", "content": "hello"}}]
    if clocked:
        rows.append({"type": "assistant", "message": {"role": "assistant",
                     "content": [{"type": "tool_use", "name": "Bash",
                                  "input": {"command":
                                            "TZ='Australia/Sydney' date "
                                            "+\"%Y%m%d%H%M\""}}]}})
    else:
        rows.append({"type": "assistant", "message": {"role": "assistant",
                     "content": [{"type": "tool_use", "name": "Bash",
                                  "input": {"command": "ls -la sessions/"}}]}})
    with open(p, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    return p


# ---------------------------------------------------------------------------
# CHECK A —— clock-call form
# ---------------------------------------------------------------------------

def test_check_a_clock_call_form():
    print("\n--- CHECK A: clock-call form (PreToolUse, Bash) ---")
    # The mandated command, and everything shaped like it, must stay SILENT.
    silent = [
        ("A1 the mandated command",
         "TZ='Australia/Sydney' date +\"%Y%m%d%H%M\""),
        ("A2 mandated command, double-quoted TZ",
         'TZ="Australia/Sydney" date +%Y%m%d%H%M'),
        ("A3 mandated command after a cd",
         "cd /tmp && TZ='Australia/Sydney' date +%Y%m%d%H%M"),
        ("A4 `date` as a bare word in prose, not a command",
         "grep -n 'stale date refs' notes.md"),
        ("A5 `date` inside a longer word (update/validate/dateutil)",
         "python3 -c 'import dateutil' && ./update.sh && validate"),
        ("A6 `--date=` flag on another command",
         "git log --date=iso-strict --pretty=format:%ad"),
        ("A7 `date -j -f` parses a GIVEN date, no current clock read",
         'date -j -f "%Y-%m-%d" "2026-05-09" +"%A"'),
        ("A8 `date -d` (GNU form) parses a GIVEN date",
         'date -d "2026-05-09" +%A'),
        ("A9 a path segment ending in `date`",
         "ls /var/db/update && cat ./mydate"),
    ]
    for label, cmd in silent:
        r = run(pre_payload(cmd), "pre")
        record(r.returncode == 0 and not advised(r), label,
               f"rc={r.returncode} out={r.stdout[:200]}")

    # A bare clock read, in every position a shell allows, must WARN.
    warn = [
        ("A10 bare `date` at the start of the command", "date +%Y%m%d%H%M"),
        ("A11 bare `date` after `&&`", "cd /tmp && date +%Y%m%d%H%M"),
        ("A12 bare `date` after `;`", "echo hi; date"),
        ("A13 bare `date` in a `$(...)` substitution",
         'TS=$(date +%Y%m%d%H%M); echo "$TS"'),
        ("A14 bare `date` in a pipeline", "date | tr a-z A-Z"),
        ("A15 the WRONG timezone, explicitly",
         "TZ='America/Los_Angeles' date +%Y%m%d%H%M"),
        ("A16 UTC, the cloud-session slip", "TZ=UTC date +%Y%m%d%H%M"),
        ("A17 a correct call followed by a bare one",
         "TZ='Australia/Sydney' date +%Y%m%d%H%M; date +%H:%M"),
        ("A18 `/usr/bin/date` spelled in full", "/usr/bin/date +%Y%m%d%H%M"),
    ]
    for label, cmd in warn:
        r = run(pre_payload(cmd), "pre")
        record(advised(r), label, f"rc={r.returncode} out={r.stdout[:200]}")

    # The advisory must name the fix, or the model cannot act on it.
    r = run(pre_payload("date +%Y%m%d%H%M"), "pre")
    ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
    record("TZ='Australia/Sydney'" in ctx and "§2.1.7" in ctx,
           "A19 advisory quotes the exact mandated command and its rule",
           ctx[:200])


# ---------------------------------------------------------------------------
# CHECK B —— mint drift
# ---------------------------------------------------------------------------

def test_check_b_mint_drift():
    print("\n--- CHECK B: minted-timestamp drift (PostToolUse, Write) ---")
    ym = datetime.now(SYD).strftime("%Y/%Y%m")
    folder = os.path.join(SESSIONS, ym)
    fresh = ts_offset(2)

    # B1: a fresh mint in a real comms folder is SILENT. Nothing is written to
    # disk —— the payload alone drives the lint.
    r = run(post_payload(os.path.join(folder, f"close_{fresh}.md")), "post")
    record(not advised(r), "B1 mint 2 min old -> silent", r.stdout[:200])

    # B2/B3: the timezone slips this check exists for.
    for label, mins in (("B2 UTC slip (10 h)", 600),
                        ("B3 US Pacific slip (17 h)", 1020)):
        ts = ts_offset(mins)
        r = run(post_payload(os.path.join(folder, f"close_{ts}.md")), "post")
        record(advised(r), f"{label} -> WARNS", r.stdout[:200])

    # B4: a wrong-DAY guess.
    ts = ts_offset(1440)
    r = run(post_payload(os.path.join(folder, f"wrap_{ts}.md")), "post")
    record(advised(r), "B4 guessed a day out -> WARNS", r.stdout[:200])

    # B5: the p99 of legitimate mints (34 min) must stay silent, and so must the
    # historical maximum (352 min) —— that is the calibration, not a guess.
    for label, mins in (("B5 legitimate p99 drift (34 min)", 34),
                        ("B6 historical max legitimate drift (352 min)", 352)):
        ts = ts_offset(mins)
        r = run(post_payload(os.path.join(folder, f"close_{ts}.md")), "post")
        record(not advised(r), f"{label} -> silent", r.stdout[:200])

    # B7: THE SIBLING EXEMPTION. A `response_` copies its `query_`'s TS (root
    # §3.5.3), so a stale-looking stamp with its source beside it is DERIVED,
    # not minted. Without this the check would fire on the commonest write in
    # the repo —— historically 878 of 1385 comms writes.
    with tempfile.TemporaryDirectory() as td:
        sub = os.path.join(td, "sessions", "2026", "202608")
        os.makedirs(sub)
        old = ts_offset(4320)                       # three days old
        open(os.path.join(sub, f"query_{old}.md"), "w").close()
        # Not a real comms tree, so drive the equivalent case inside `sessions/`
        # by pointing at a REAL folder that holds a REAL pair.
    real_pair = _find_real_pair()
    if real_pair:
        path, note = real_pair
        r = run(post_payload(path), "post")
        record(not advised(r), f"B7 real derived pair -> silent ({note})",
               r.stdout[:200])
    else:
        record(False, "B7 real derived pair -> silent", "no pair found in repo")

    # B8: an Edit is never a mint —— it revisits a file stamped long ago
    # (historical max drift in that bucket: 8594 min).
    ts = ts_offset(1440)
    r = run(post_payload(os.path.join(folder, f"close_{ts}.md"), tool="Edit"),
            "post")
    record(not advised(r), "B8 Edit of an old-stamped file -> silent",
           r.stdout[:200])

    # B9: outside the two comms trees nothing is stamped by root §3.3, so a
    # TS-bearing sandbox fixture must never fire.
    ts = ts_offset(1440)
    r = run(post_payload(os.path.join(REPO, "cp", "ccsim", "sandbox",
                                      f"probe_{ts}.md")), "post")
    record(not advised(r), "B9 TS-bearing file outside sessions/ -> silent",
           r.stdout[:200])

    # B10: a 13-digit id must not read as a timestamp.
    r = run(post_payload(os.path.join(folder, "close_2026080512345.md")), "post")
    record(not advised(r), "B10 13-digit id is not a TS -> silent",
           r.stdout[:200])

    # B11: the advisory must tell the model what to DO.
    ts = ts_offset(1020)
    r = run(post_payload(os.path.join(folder, f"close_{ts}.md")), "post")
    ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
    record("TZ='Australia/Sydney'" in ctx and "git mv" in ctx,
           "B11 drift advisory names the command and the rename route", ctx[:200])


def _find_real_pair():
    """A real `query_`/`response_` pair on disk, used to prove the sibling
    exemption against live data rather than a fixture. Returns the response's
    path, or None."""
    ts_re = re.compile(r"(?<!\d)(20\d{10})(?!\d)")
    for root, _dirs, files in os.walk(SESSIONS):
        by_ts = {}
        for f in files:
            m = ts_re.search(f)
            if m:
                by_ts.setdefault(m.group(1), []).append(f)
        for ts, group in by_ts.items():
            resp = [f for f in group if f.endswith(".md") and "response_" in f]
            quer = [f for f in group if "query_" in f]
            if resp and quer:
                return os.path.join(root, resp[0]), f"{resp[0]} + {quer[0]}"
    return None


# ---------------------------------------------------------------------------
# CHECK C —— unclocked mint
# ---------------------------------------------------------------------------

def test_check_c_unclocked_mint():
    print("\n--- CHECK C: mint in a session that never read the clock ---")
    ym = datetime.now(SYD).strftime("%Y/%Y%m")
    folder = os.path.join(SESSIONS, ym)
    fresh = ts_offset(2)
    target = os.path.join(folder, f"close_{fresh}.md")

    with tempfile.TemporaryDirectory() as td:
        clocked = make_transcript(td, "clocked.jsonl", True)
        unclocked = make_transcript(td, "unclocked.jsonl", False)

        r = run(post_payload(target, transcript_path=clocked), "post")
        record(not advised(r), "C1 session DID run the clock -> silent",
               r.stdout[:200])

        r = run(post_payload(target, transcript_path=unclocked), "post")
        record(advised(r), "C2 session NEVER ran the clock -> WARNS",
               r.stdout[:200])

        # C3: THE TRAP. Root CLAUDE.md quotes the mandated command verbatim, so
        # every transcript that read the protocol contains the literal string
        # `Australia/Sydney`. A raw substring search would call this session
        # clocked. Only parsing tool_use inputs gets it right.
        p = os.path.join(td, "quoted.jsonl")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"type": "user", "message": {
                "role": "user", "content":
                "obtain TS via TZ='Australia/Sydney' date +\"%Y%m%d%H%M\""}}) + "\n")
        r = run(post_payload(target, transcript_path=p), "post")
        record(advised(r),
               "C3 protocol TEXT quoting the command is not a clock READ -> WARNS",
               r.stdout[:200])

        # C4: a sub-agent payload hands over the MAIN transcript
        # (hook_guide.md §5.6.2), so its own clock read is invisible here.
        # Accusing it would be a guaranteed false positive.
        r = run(post_payload(target, transcript_path=unclocked,
                             agent_id="agent-1", agent_type="general-purpose"),
                "post")
        record(not advised(r), "C4 sub-agent payload -> skipped, never accused",
               r.stdout[:200])

        # C5: an unreadable transcript must fail OPEN (hook_guide.md §4.4).
        r = run(post_payload(target, transcript_path=os.path.join(td, "gone.jsonl")),
                "post")
        record(not advised(r), "C5 missing transcript -> fails open, silent",
               r.stdout[:200])

        # C6: drift OUTRANKS the unclocked note —— one finding per write, and
        # the wrong stamp is the more urgent one.
        stale = os.path.join(folder, f"close_{ts_offset(1020)}.md")
        r = run(post_payload(stale, transcript_path=unclocked), "post")
        ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
        record("real Sydney clock" in ctx,
               "C6 drift + unclocked -> reports the drift, not the weaker note",
               ctx[:160])


# ---------------------------------------------------------------------------
# CHECK D —— US date format
# ---------------------------------------------------------------------------

def test_check_d_us_date_format():
    print("\n--- CHECK D: US-format dates in written text ---")
    target = os.path.join(SESSIONS, "2026", "202608", "response_202608052335.md")

    warn = [
        ("D1 `August 5, 2026`", "Submitted on August 5, 2026 to the panel."),
        ("D2 `Aug 5, 2026`", "Interview held Aug 5, 2026 at head office."),
        ("D3 `Aug. 5th, 2026`", "Filed Aug. 5th, 2026 with the registrar."),
        ("D4 `December 25, 2026`", "Closing December 25, 2026 for the break."),
        ("D5 unambiguous numeric `08/25/2026`", "Due 08/25/2026 per the letter."),
        ("D6 unambiguous numeric `12/31/2026`", "Ends 12/31/2026 at midnight."),
    ]
    for label, text in warn:
        r = run(post_payload(target, content=text), "post")
        record(advised(r), f"{label} -> WARNS", f"rc={r.returncode} {r.stdout[:200]}")

    silent = [
        ("D7 the mandated form `at HH:mm on DD/MM/YYYY`",
         "Submitted at 14:30 on 05/08/2026 to the panel."),
        ("D8 British long form `5 August 2026`",
         "Submitted on 5 August 2026 to the panel."),
        ("D9 ISO `2026-08-05`", "Recorded 2026-08-05 in the ledger."),
        ("D10 AMBIGUOUS `08/05/2026` is a correct DD/MM date -> never flagged",
         "Submitted 08/05/2026 to the panel."),
        ("D11 a month and year with no day", "Reviewed in August 2026 as agreed."),
        ("D12 a bare figure that is not a date", "Scored 12/31 on the rubric."),
    ]
    for label, text in silent:
        r = run(post_payload(target, content=text), "post")
        record(not advised(r), f"{label} -> silent", r.stdout[:200])

    # D13-D15: QUOTED material is not CC choosing a format. All 8 historical
    # month-first hits in this repo sit inside a fence, in a verbatim paste of
    # Claude's own device list. Masking is what makes the live-repo count zero.
    quoted = [
        ("D13 inside a fenced block",
         "Pasted from the console:\n```\nLast seen Aug 5, 2026, 7:42 PM\n```\n"),
        ("D14 inside an inline code span",
         "The console prints `Aug 5, 2026` verbatim."),
        ("D15 inside a `>` blockquote",
         "He wrote:\n\n> Deadline is August 5, 2026 sharp.\n"),
    ]
    for label, text in quoted:
        r = run(post_payload(target, content=text), "post")
        record(not advised(r), f"{label} -> silent (quoted, not authored)",
               r.stdout[:200])

    # D16: an Edit is judged on what it INTRODUCED, not on the whole file.
    d = {"hook_event_name": "PostToolUse", "session_id": "testsess", "cwd": REPO,
         "tool_name": "Edit",
         "tool_input": {"file_path": target, "old_string": "x",
                        "new_string": "Signed August 5, 2026 by the director."}}
    r = run(d, "post")
    record(advised(r), "D16 Edit introducing a US date -> WARNS", r.stdout[:200])

    # D17: not a `.md`, so not CC's prose —— a `%m/%d/%Y` format string in code
    # must never be mistaken for a date.
    r = run(post_payload(os.path.join(REPO, "cscpt", "zz_probe.py"),
                         content='fmt = "August 5, 2026"'), "post")
    record(not advised(r), "D17 non-.md target -> silent", r.stdout[:200])

    # D18: the advisory must name the correct form.
    r = run(post_payload(target, content="Due 08/25/2026."), "post")
    ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
    record("DD/MM/YYYY" in ctx and "§2.2.2" in ctx,
           "D18 advisory names the mandated form and its rule", ctx[:200])


# ---------------------------------------------------------------------------
# Fail-safety, logging, and the live-repo calibration sweeps
# ---------------------------------------------------------------------------

def test_stdout_is_always_one_json_object():
    """PINS A REAL BUG. The first build emitted a separate `json.dump` per
    finding, so a write carrying BOTH a US date and a bad timestamp produced two
    objects on stdout. The harness parses stdout as ONE object, so that stream
    is `Extra data: line 2` and BOTH advisories are lost —— the lint finds two
    defects and silently reports neither. Every path must emit at most one."""
    print("\n--- stdout shape: one object, always ---")
    ym = datetime.now(SYD).strftime("%Y/%Y%m")
    folder = os.path.join(SESSIONS, ym)
    stale = os.path.join(folder, f"close_{ts_offset(1020)}.md")

    r = run(post_payload(stale, content="Signed August 5, 2026 by the director."),
            "post")
    ok, ctx = False, ""
    try:
        ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
        ok = True
    except Exception as exc:
        ctx = repr(exc)
    record(ok, "J1 US date + drifted timestamp -> stdout still parses as ONE "
               "object", r.stdout[:160])
    record(ok and "US-format date" in ctx and "real Sydney clock" in ctx,
           "J2 both findings survive in that one object", ctx[:160])

    # J3: every warning case in this suite must produce parseable stdout, not
    # merely the one combination above.
    target = os.path.join(SESSIONS, "2026", "202608", "response_202608052335.md")
    bad = []
    for arg, payload in (
            ("pre", pre_payload("date +%Y%m%d%H%M")),
            ("post", post_payload(stale)),
            ("post", post_payload(target, content="Due 08/25/2026.")),
            ("post", post_payload(target, content="Due August 5, 2026.")),
            ("post", post_payload(stale, content="Due 08/25/2026 and 12/31/2026.")),
    ):
        res = run(payload, arg)
        if res.stdout.strip():
            try:
                json.loads(res.stdout)
            except Exception:
                bad.append(str(payload)[:80])
    record(not bad, "J3 every warning path emits parseable stdout", "; ".join(bad))


def test_fail_open_and_never_blocks():
    print("\n--- fail-safety: nothing here may ever block ---")
    cases = [
        ("F1 empty stdin", ""),
        ("F2 malformed JSON", "{not json"),
        ("F3 valid JSON that is not an object", '["date 20260805"]'),
        ("F4 object with no tool_input", '{"tool_name":"Bash","x":"date"}'),
        ("F5 tool_input of the wrong type",
         '{"tool_name":"Bash","tool_input":"date 202608052335"}'),
    ]
    for arg in ("pre", "post"):
        for label, raw in cases:
            env = dict(os.environ)
            env["TLINT_LOG"] = _LOGFILE
            r = subprocess.run(["/bin/sh", SHIM, arg], input=raw,
                               capture_output=True, text=True, cwd=REPO, env=env)
            record(r.returncode == 0, f"{label} ({arg}) -> exit 0",
                   f"rc={r.returncode} err={r.stderr[:120]}")

    # F6: no argument at all —— the state during the minutes-long window in
    # which a settings edit has not gone live (hook_guide.md §7.9). The payload's
    # own `hook_event_name` must carry the mode.
    env = dict(os.environ)
    env["TLINT_LOG"] = _LOGFILE
    r = subprocess.run(["/bin/sh", SHIM], input=json.dumps(
        pre_payload("date +%Y%m%d%H%M")), capture_output=True, text=True,
        cwd=REPO, env=env)
    record(r.returncode == 0 and advised(r),
           "F6 argument-less call falls back to hook_event_name", r.stdout[:200])

    # F7: nothing may reach stderr —— at exit 0 stderr reaches the USER alone,
    # and none of these findings is his to act on.
    r = run(pre_payload("date +%Y%m%d%H%M"), "pre")
    record(r.stderr.strip() == "", "F7 advisory never writes to stderr",
           r.stderr[:200])


def test_stage_log_records_every_invocation():
    print("\n--- stage log (hook_guide.md §7.7) ---")
    before = _log_lines()
    run(pre_payload("TZ='Australia/Sydney' date +%Y%m%d%H%M"), "pre")
    after_clean = _log_lines()
    run(pre_payload("date +%Y%m%d%H%M"), "pre")
    after_warn = _log_lines()
    record(len(after_clean) == len(before) + 1,
           "L1 a CLEAN invocation still appends a line "
           "('never fired' must differ from 'fired, found nothing')",
           f"{len(before)} -> {len(after_clean)}")
    record(len(after_warn) == len(after_clean) + 1
           and "action=clock_warn" in after_warn[-1],
           "L2 a WARNING invocation appends a tagged line", after_warn[-1:])
    record("action=clock_ok" in after_clean[-1],
           "L3 the clean line is tagged by the stage reached", after_clean[-1:])


def _log_lines():
    try:
        with open(_LOGFILE, encoding="utf-8") as fh:
            return fh.read().splitlines()
    except Exception:
        return []


def test_live_repo_has_no_us_dates():
    """Re-derive the CHECK D calibration against the live repo. It scored ZERO
    when the rule was written; a future widening that starts matching legitimate
    prose fails here rather than in a user's face."""
    print("\n--- live-repo sweep: CHECK D calibration ---")
    sys.path.insert(0, os.path.join(REPO, "cscpt"))
    import tlint                                             # noqa: E402
    skip = {".git", "node_modules", "__pycache__", "backup", "archive"}
    hits, scanned = [], 0
    for dp, dn, fn in os.walk(REPO):
        dn[:] = [d for d in dn if d not in skip]
        for f in fn:
            if not f.endswith(".md"):
                continue
            p = os.path.join(dp, f)
            scanned += 1
            try:
                text = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            masked = tlint._mask_quoted(text)
            for rx in (tlint._US_MONTH_RE, tlint._US_NUM_RE):
                for m in rx.finditer(masked):
                    hits.append(f"{os.path.relpath(p, REPO)}: {m.group(0)}")
    record(not hits,
           f"S1 no US-format date in any live .md ({scanned} scanned, "
           f"backups and archives excluded)",
           "; ".join(hits[:6]))


def test_ambiguous_numeric_date_is_not_flagged():
    """Pin the deliberate blind spot. `08/05/2026` is a correct DD/MM date far
    more often than a US one, so flagging it would fire on CORRECT output. Only
    a second field above 12 is unambiguous."""
    print("\n--- deliberate blind spot ---")
    sys.path.insert(0, os.path.join(REPO, "cscpt"))
    import tlint                                             # noqa: E402
    amb = [f"0{m}/0{d}/2026" for m in (1, 8) for d in (5, 9)]
    record(not any(tlint._US_NUM_RE.search(s) for s in amb),
           "S2 ambiguous MM/DD vs DD/MM dates are never flagged", str(amb))
    record(all(tlint._US_NUM_RE.search(s) for s in
               ("08/25/2026", "1/13/2026", "12/31/1999")),
           "S3 unambiguous US dates (second field >12) are flagged")


def test_shim_gate_drops_nothing_the_lint_would_flag():
    """The fast path must never swallow a real hit. Every WARNING case above is
    re-run against the `.py` DIRECTLY; any case the shim silenced but the lint
    would have flagged is a silent detection gap (`hook_guide.md` §8)."""
    print("\n--- shim gate vs the lint itself ---")
    ym = datetime.now(SYD).strftime("%Y/%Y%m")
    folder = os.path.join(SESSIONS, ym)
    target = os.path.join(SESSIONS, "2026", "202608", "response_202608052335.md")
    cases = [
        ("pre", pre_payload("date +%Y%m%d%H%M")),
        ("pre", pre_payload("TZ=UTC date")),
        ("pre", pre_payload("echo hi; date")),
        # The spelling the FIRST draft of the gate silently dropped, by
        # excluding `/` from the word boundary. Pinned so it cannot return.
        ("pre", pre_payload("/usr/bin/date +%Y%m%d%H%M")),
        ("pre", pre_payload('TS=$(date +%Y%m%d%H%M); echo "$TS"')),
        ("post", post_payload(os.path.join(folder, f"close_{ts_offset(1020)}.md"))),
        ("post", post_payload(target, content="Due August 5, 2026.")),
        ("post", post_payload(target, content="Due 08/25/2026.")),
        ("post", post_payload(target, content="Filed Aug. 5th, 2026 today.")),
    ]
    env = dict(os.environ)
    env["TLINT_LOG"] = _LOGFILE
    gaps = []
    for arg, payload in cases:
        direct = subprocess.run(
            [sys.executable, os.path.join(REPO, "cscpt", "tlint.py"), arg],
            input=json.dumps(payload), capture_output=True, text=True,
            cwd=REPO, env=env)
        via_shim = run(payload, arg)
        if advised(direct) and not advised(via_shim):
            gaps.append(str(payload)[:100])
    record(not gaps, "G1 the shim's grep gate drops nothing the lint flags",
           "; ".join(gaps))


def test_registration_is_live():
    """`~/.claude/settings.json` is the ONLY place a hook is really registered
    (hook_guide.md §1). An unregistered lint passes every unit test and does
    nothing at all, which is precisely the failure §2 of that guide records ——
    so this reads the LIVE file rather than trusting that someone edited it."""
    print("\n--- wiring ---")
    path = os.path.expanduser("~/.claude/settings.json")
    try:
        hooks = json.load(open(path, encoding="utf-8")).get("hooks", {})
    except Exception as exc:
        record(False, "W1 live settings.json is readable", repr(exc))
        return
    cmds = []
    for _ev, groups in hooks.items():
        for g in groups:
            for h in (g.get("hooks") or [g]):
                c = h.get("command", "")
                if isinstance(c, str):
                    cmds.append((_ev, c))
    pre = [c for ev, c in cmds if "tlint_hook.sh" in c and c.rstrip().endswith("pre")]
    post = [c for ev, c in cmds if "tlint_hook.sh" in c and c.rstrip().endswith("post")]
    record(bool(pre), "W1 tlint_hook.sh is registered with argument `pre`",
           "not found in ~/.claude/settings.json —— the lint is DEAD until it is")
    record(bool(post), "W2 tlint_hook.sh is registered with argument `post`",
           "not found in ~/.claude/settings.json —— the lint is DEAD until it is")
    record(os.access(SHIM, os.X_OK), "W3 the registered shim is executable")


def main():
    global _LOGFILE
    if SYD is None:
        print("FATAL: no Australia/Sydney tz database on this machine.")
        return 1
    with tempfile.TemporaryDirectory() as td:
        _LOGFILE = os.path.join(td, "tlint.log")
        print(f"Repo: {REPO}\nDriving: {SHIM}\n")
        test_check_a_clock_call_form()
        test_check_b_mint_drift()
        test_check_c_unclocked_mint()
        test_check_d_us_date_format()
        test_stdout_is_always_one_json_object()
        test_fail_open_and_never_blocks()
        test_stage_log_records_every_invocation()
        test_live_repo_has_no_us_dates()
        test_ambiguous_numeric_date_is_not_flagged()
        test_shim_gate_drops_nothing_the_lint_would_flag()
        test_registration_is_live()
    print()
    if failures:
        print(f"{checks - len(failures)}/{checks} passed —— FAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"{checks}/{checks} passed —— time-integrity lint intact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
