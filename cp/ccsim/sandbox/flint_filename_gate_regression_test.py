#!/usr/bin/env python3
"""Regression test —— the two MALFORMED COMMS FILENAME defects must stay
mechanically impossible to create, and mechanically impossible to walk past.

WHY THIS EXISTS (self-contained; no conversation or comms file explains it):

Root CLAUDE.md §3.3 names comms files `[prefix]_[TS].md`. Two different ways of
breaking that shape have both shipped repeatedly:

* THE STRAY SPACE, wedged between the prefix underscore and the 12 digits ——
  `close_ 202606142239.md` and kin, at least four across two months.
* THE TRAILING TAIL, appended after the 12 digits —— `ccsim_query_202608060423a`
  and `…0423b`, two files minted in one minute and disambiguated with letters
  instead of taking consecutive minutes. Four such files were live when this
  half was written, and earlier ones had already been hand-renamed.

Every instance of both was spotted by eye, months later, and hand-renamed. Prose
said the right thing and was skipped every time, so prose was never going to fix
it (`cp/ccsim/CLAUDE.md` §8.7: not-noticed is an enforcement gap, and the prose
that failed cannot repair it). Three mechanisms replaced it, and this file pins
all three (the git hook covers the stray space only —— see KNOWN GAPS in
`flint.py`):

* `cscpt/flint.py pre` —— PreToolUse. BLOCKS the write. This is the only one
  that can prevent creation at all: a PostToolUse hook cannot undo a write.
* `cscpt/flint.py post` —— PostToolUse. Sweeps the folder it was ALREADY listing
  for its timestamp check and reports any offender it finds there. Encounter,
  not hunt: it reads nothing extra and fires only as a by-product of a write.
  (This half was `cscpt/tlint.py` until it was merged in —— a timestamp is part
  of a filename, so one lint owns filenames. Its own timestamp-clash and
  cross-repo-mirror duties came across unchanged and are pinned below.)
* `.githooks/pre-commit` —— catches whatever reached the index by a route no
  PreToolUse hook sees (Bash, Finder), blocking a staged ADD.

THE MERGE'S OWN HAZARD, pinned by the M-series and T8/T9: the two halves have
DIFFERENT REACH on purpose (`cp/ccsim/hook_guide.md` §4.7 —— a lint that can
BLOCK must be repo-scoped, a lint that can only advise may be global). The PRE
block is repo-scoped; the ENTIRE POST half is global, because a missed TS clash
in the sibling AJAP repo is silent and expensive. One misplaced scope guard at
the top of `main()` would delete that coverage whilst every other test here
still passed, so T8/T9 assert it from the outside.

THE FIXTURES ARE REAL, not synthesised (`universal/coding.md` § Testing: mine
historical data —— real past inputs catch failure classes synthetic cases miss).
`REAL_DEFECTS` are the actual filenames recorded in `cp/ccsim/backlog.md`.
`REAL_LEGITIMATE` are the files that a broader, obvious-looking rule ("a
TS-bearing name containing whitespace") WOULD have blocked: of the 7 whitespace-
bearing TS filenames in this repo, 5 are innocent, deliberately spaced
throughout. F8 is therefore the false-positive test that decided the rule's
shape, and F18 re-derives that verdict from the live repo on every run, so a
future edit that broadens the rule fails here rather than in someone's commit.

Both halves are driven end-to-end through their real stdin/stdout hook
contract, never by importing their internals —— a rule that only works when
called directly is not wired. F17/M4 additionally drive `flint_hook.sh`, because
the shim, not the `.py`, is what the harness launches: a shim that swallowed the
exit code —— or dropped the mode argument —— would leave every unit test passing
and one half of the gate dead.

Run directly (from anywhere):

    python3 "cp/ccsim/sandbox/flint_filename_gate_regression_test.py"

Exits 0 if every case matches its expected verdict, 1 otherwise, with a
per-case PASS/FAIL report and the raw stdout/stderr on any FAIL. Self-contained:
every fixture is created in a throwaway tempdir (including a real scratch git
repo for the pre-commit cases) and removed afterwards; no repo file is touched.
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
FLINT = os.path.join(REPO_ROOT, "cscpt", "flint.py")
FLINT_HOOK = os.path.join(REPO_ROOT, "cscpt", "flint_hook.sh")
PRECOMMIT = os.path.join(REPO_ROOT, ".githooks", "pre-commit")

# The two registered invocations, spelled exactly as `~/.claude/settings.json`
# spells them. Every test below drives one of these, never a bare `flint.py`:
# the mode argument IS part of the wiring, so a test that omitted it would pass
# against a build whose registration had lost it.
PRE = ["python3", FLINT, "pre"]
POST = ["python3", FLINT, "post"]

# The four instances recorded in cp/ccsim/backlog.md. Two are still in the repo;
# two were hand-renamed before this gate existed. All four must be caught.
REAL_DEFECTS = (
    "close_ 202605310448.md",
    "close_ 202606142239.md",
    "career_close_ 202606162244.md",
    "dissertation_close_ 202607151919.md",
)

# Real repo filenames that carry BOTH a 12-digit TS and whitespace, and are
# entirely legitimate. The rule must leave every one of them alone.
REAL_LEGITIMATE = (
    "MGTK746 Dev Plan _ 202603170315.txt",
    "MGTK746 CP Instructions _ 202603212044.txt",
    "MGTK746 Dev Plan _ 202603260158.txt",
    "MGTK746 Thematic Analysis _ 202602172022.txt",
    "AJAP Logs 202607182259.csv",
)

# Legitimate shapes root CLAUDE.md itself mandates —— §8.1.2's `_moved_` suffix
# and §8.2's `❌_` void prefix. A positive-form "must match the canonical name
# exactly" check would have broken both, which is why rule 1 is negative-form and
# rule 2 carries an explicit exemption list instead.
REAL_CONVENTIONS = (
    "close_202606142239.md",
    "ccsim_response_202608011839.md",
    "❌_push_classifier_query_202607282109_moved_202607.md",
    "backup_❌_SEEKLimited_OperationsSquadLead_202606142148.md_moved_skipped",
    "slog_202607311200.md",
    # The Move Rule applied to a plainly comms-shaped name —— the shape rule 2
    # would break if its exemption were ever dropped. No live instance exists
    # today, which is exactly why it needs a fixture: the day one is created is
    # the day a missing exemption would block root §8.1.2 itself.
    "query_202607282109_moved_202607.md",
    "ccsim_close_202607282109.md_moved_skipped",
    # Multi-part extension.
    "response_202606231628.pages.md",
)

# THE TRAILING-TAIL DEFECT (rule 2). The first two are the exact filenames the
# owner rejected; the rest are real live siblings of the same class. `_r2` is a
# SECOND response to one query —— deliberately NOT exempted, because `_r2` and
# `a` differ only in spelling, so an exemption for one re-opens the other.
REAL_TAIL_DEFECTS = (
    "ccsim_query_202608060423a.md",
    "ccsim_query_202608060423b.md",
    "ccsim_query_202608052118a.md",
    "ccsim_query_202608052118b.md",
    "response_202607072124_r2.md",
)

# Real TS-bearing repo filenames that DO carry something after the timestamp and
# are entirely innocent, because none of them is comms-shaped. Rule 2 must not
# reach a single one. Mined from both comms repos (11,589 files; 10,706 carry a
# bounded 12-digit TS; 1,344 are comms-shaped).
REAL_NON_COMMS_TAILS = (
    "backup_❌_⏳_DXCTechnology_ChangeAnalyst_202606182347_moved_pending.md",
    "backup_TheOnset_LeadDeliveryManager_202607050002_reapplied.md",
    "backup_❌_⚠️_SelectServicePartner_CommercialMarketingManagerANZ"
    "_202606210220_stale.md",
    "test_live_202607190438_fixes.py",
    "MGTK746_A2_202603270408_notes.txt",
    "cowork_202604120846_report.md",
    "Alltech_interview_transcript_202607021219_fixed.md",
    "git_history_response_202607161603_202607171243.html",
    "chrome_disable_ondevice_model_202607251750.mobileconfig",
    "document.wflow.bak_202607230551",
)

results = []


def _check(label, ok, detail=""):
    print("[%s] %s" % ("PASS" if ok else "FAIL", label))
    if not ok and detail:
        print("        " + detail.replace("\n", "\n        "))
    results.append(bool(ok))


def _run(cmd, payload):
    """Drive a hook end-to-end through its real stdin contract. `payload` may be
    a dict or a raw str (deliberately malformed)."""
    body = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(cmd, input=body, capture_output=True, text=True)


def _pre_payload(path, tool="Write", cwd=REPO_ROOT, transcript=None,
                 key="file_path"):
    """A realistic PreToolUse payload (hook_guide.md § Verified Payload Shapes).
    `cwd=None` drops the field entirely —— the fail-open branch."""
    d = {
        "session_id": "flint-regression",
        "prompt_id": "pid-flint-regression",
        "permission_mode": "default",
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": {key: path},
    }
    if cwd is not None:
        d["cwd"] = cwd
    if transcript is not None:
        d["transcript_path"] = transcript
    return d


def _post_payload(path, cwd=REPO_ROOT, transcript=None):
    """A realistic PostToolUse payload. `cwd=None` drops the field entirely."""
    d = {
        "session_id": "flint-regression",
        "prompt_id": "pid-flint-regression",
        "permission_mode": "default",
        "hook_event_name": "PostToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": path, "content": "x"},
        "tool_response": {"filePath": path},
    }
    if cwd is not None:
        d["cwd"] = cwd
    if transcript is not None:
        d["transcript_path"] = transcript
    return d


def _advice(r):
    """The `additionalContext` string a hook emitted, or '' if it emitted none."""
    out = r.stdout.strip()
    if not out:
        return ""
    try:
        return (json.loads(out).get("hookSpecificOutput") or {}).get(
            "additionalContext", "")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# FLINT —— prevention at creation
# ---------------------------------------------------------------------------

def test_flint_blocks_every_real_defect():
    for i, name in enumerate(REAL_DEFECTS, 1):
        p = os.path.join(REPO_ROOT, "sessions", "2026", "202606", name)
        r = _run(PRE,_pre_payload(p))
        want = name.replace("_ ", "_", 1)
        ok = r.returncode == 2 and want in r.stderr and "BLOCKED" in r.stderr
        _check("F1.%d — real defect `%s` BLOCKED, correct name offered" % (i, name),
               ok, "rc=%s stderr=%r" % (r.returncode, r.stderr))


def test_flint_blocks_every_write_class_tool():
    p = os.path.join(REPO_ROOT, "sessions", "2026", "202608", "close_ 202608011234.md")
    for tool, key in (("Write", "file_path"), ("Edit", "file_path"),
                      ("MultiEdit", "file_path"), ("NotebookEdit", "notebook_path")):
        r = _run(PRE,_pre_payload(p, tool=tool, key=key))
        _check("F2 — %s on a defect path is BLOCKED (exit 2)" % tool,
               r.returncode == 2, "rc=%s stderr=%r" % (r.returncode, r.stderr))


def test_flint_blocks_exotic_whitespace_runs():
    cases = (
        ("close_  202608011234.md", "two spaces"),
        ("close_\t202608011234.md", "a tab"),
        ("close_ 202608011234.md", "a non-breaking space"),
        ("ccsim_close_ 202608011234.md", "a CP prefix"),
        ("a_b_c_ 202608011234.md", "several underscores"),
    )
    for name, what in cases:
        p = os.path.join(REPO_ROOT, "sessions", "2026", "202608", name)
        r = _run(PRE,_pre_payload(p))
        _check("F3 — BLOCKED with %s" % what, r.returncode == 2,
               "rc=%s stderr=%r" % (r.returncode, r.stderr))


def test_flint_ignores_clean_and_conventional_names():
    for name in REAL_CONVENTIONS:
        p = os.path.join(REPO_ROOT, "sessions", "2026", "202606", name)
        r = _run(PRE,_pre_payload(p))
        ok = r.returncode == 0 and not r.stdout.strip() and not r.stderr.strip()
        _check("F7 — clean/conventional `%s` passes silently" % name, ok,
               "rc=%s out=%r err=%r" % (r.returncode, r.stdout, r.stderr))


def test_flint_does_not_touch_legitimate_spaced_names():
    """THE false-positive test. These 5 real files carry a TS and whitespace and
    are innocent; the obvious broad rule would have blocked all of them."""
    for name in REAL_LEGITIMATE:
        p = os.path.join(REPO_ROOT, "cp", "archive", "mip", name)
        r = _run(PRE,_pre_payload(p))
        ok = r.returncode == 0 and not r.stdout.strip() and not r.stderr.strip()
        _check("F8 — legitimate spaced name `%s` NOT blocked" % name, ok,
               "rc=%s out=%r err=%r" % (r.returncode, r.stdout, r.stderr))


def test_flint_boundary_cases():
    cases = (
        ("close_ 2026061422391.md", "13-digit run is not a TS"),
        ("close_ 199906142239.md", "a TS not starting 20"),
        ("close_ 20260614223.md", "11 digits"),
        ("plain notes 202608011234.md", "space but no underscore before the TS"),
        ("Dev Plan _ 202608011234.md", "spaces before the underscore too"),
    )
    for name, what in cases:
        p = os.path.join(REPO_ROOT, "sessions", "2026", "202608", name)
        r = _run(PRE,_pre_payload(p))
        ok = r.returncode == 0 and not r.stdout.strip()
        _check("F9 — not flagged: %s (`%s`)" % (what, name), ok,
               "rc=%s out=%r err=%r" % (r.returncode, r.stdout, r.stderr))


def test_flint_advises_on_read_never_blocks():
    p = os.path.join(REPO_ROOT, "sessions", "2026", "202606", "close_ 202606142239.md")
    r = _run(PRE,_pre_payload(p, tool="Read"))
    adv = _advice(r)
    ok = (r.returncode == 0 and "[flint]" in adv and "ALERT THE USER" in adv
          and "do not go hunting" in adv and "close_202606142239.md" in adv)
    _check("F10 — a READ of an offender advises the model, never blocks", ok,
           "rc=%s out=%r" % (r.returncode, r.stdout))


def test_flint_downgrades_to_advisory_out_of_scope():
    """hook_guide.md §4.7 —— a lint that can BLOCK must be repo-scoped. Out of
    scope it must still SAY something, not go silent (§4.4)."""
    other = "/Users/culous/some-other-project"
    p = os.path.join(other, "close_ 202608011234.md")
    r = _run(PRE,_pre_payload(p, cwd=other))
    ok = r.returncode == 0 and "[flint]" in _advice(r)
    _check("F11 — out-of-repo cwd: advises, does NOT block", ok,
           "rc=%s out=%r err=%r" % (r.returncode, r.stdout, r.stderr))

    r = _run(PRE,_pre_payload(
        p, cwd=None, transcript="/Users/culous/.claude/projects/-Users-culous-other/x.jsonl"))
    ok = r.returncode == 0 and "[flint]" in _advice(r)
    _check("F12 — out-of-repo transcript slug: advises, does NOT block", ok,
           "rc=%s out=%r err=%r" % (r.returncode, r.stdout, r.stderr))


def test_flint_fails_open_on_unscopeable_payload():
    """§4.4 —— an unreadable scope is not evidence of another project."""
    p = "/somewhere/close_ 202608011234.md"
    r = _run(PRE,_pre_payload(p, cwd=None))
    _check("F13 — no cwd and no transcript_path: FAILS OPEN and blocks",
           r.returncode == 2, "rc=%s stderr=%r" % (r.returncode, r.stderr))

    r = _run(PRE,_pre_payload(
        p, cwd=None, transcript="/not/the/expected/shape.jsonl"))
    _check("F14 — unparseable transcript_path: FAILS OPEN and blocks",
           r.returncode == 2, "rc=%s stderr=%r" % (r.returncode, r.stderr))

    sub = os.path.join(REPO_ROOT, "cp", "ccsim")
    r = _run(PRE,_pre_payload(
        os.path.join(sub, "close_ 202608011234.md"), cwd=sub))
    _check("F15 — a cwd BELOW the repo root is in scope and blocks",
           r.returncode == 2, "rc=%s stderr=%r" % (r.returncode, r.stderr))


def test_flint_fail_safe_on_malformed_payloads():
    malformed = (
        "{not json at all",
        json.dumps([1, 2, 3]),
        json.dumps({"tool_name": "Write"}),
        json.dumps({"tool_name": "Write", "tool_input": "a string"}),
        json.dumps({"tool_name": "Write", "tool_input": {"file_path": 123}}),
        json.dumps({"tool_input": {"file_path": "close_ 202608011234.md"},
                    "tool_name": None}),
        "",
    )
    for i, bad in enumerate(malformed, 1):
        r = _run(PRE,bad)
        # The `tool_name: None` case still has a real defect path, so it must
        # advise rather than crash —— never exit 1, never traceback.
        ok = r.returncode in (0, 2) and "Traceback" not in r.stderr
        _check("F16.%d — malformed payload: no traceback, no exit 1" % i, ok,
               "rc=%s err=%r" % (r.returncode, r.stderr))


def test_flint_hook_shim_is_the_wiring():
    """The harness launches the SHIM. A shim that swallowed the exit code would
    leave every test above passing and the gate dead (hook_guide.md §7.1)."""
    p = os.path.join(REPO_ROOT, "sessions", "2026", "202606", "close_ 202606142239.md")
    r = _run(["sh", FLINT_HOOK, "pre"], _pre_payload(p))
    _check("F17a — shim propagates the exit 2 from flint.py",
           r.returncode == 2 and "BLOCKED" in r.stderr,
           "rc=%s err=%r" % (r.returncode, r.stderr))

    r = _run(["sh", FLINT_HOOK, "pre"], _pre_payload(
        os.path.join(REPO_ROOT, "universal", "coding.md")))
    _check("F17b — shim exits 0 instantly on a TS-less payload",
           r.returncode == 0 and not r.stdout.strip(),
           "rc=%s out=%r" % (r.returncode, r.stdout))

    r = _run(["sh", FLINT_HOOK, "pre"], _pre_payload(p, tool="Read"))
    _check("F17c — shim passes the READ advisory through on stdout",
           r.returncode == 0 and "[flint]" in _advice(r),
           "rc=%s out=%r" % (r.returncode, r.stdout))


# ---------------------------------------------------------------------------
# RULE 2 —— nothing may follow the timestamp
# ---------------------------------------------------------------------------

def test_flint_blocks_the_letter_suffix_defect():
    """THE case the owner rejected, verbatim. `a`/`b` on one minute is not a
    disambiguator —— the second file takes the next MINUTE."""
    tmp = tempfile.mkdtemp(prefix="flint-reg-tail-")
    try:
        a = os.path.join(tmp, "ccsim_query_202608060423a.md")
        r = _run(PRE, _pre_payload(a))
        ok = (r.returncode == 2 and "BLOCKED" in r.stderr
              and "ccsim_query_202608060423.md" in r.stderr)
        _check("F19a — `…0423a.md` BLOCKED, and the FREE minute 0423 offered",
               ok, "rc=%s stderr=%r" % (r.returncode, r.stderr))

        _check("F19b — the block names the remedy (next minute, not a suffix)",
               "NEXT minute" in r.stderr or "consecutive MINUTES" in r.stderr,
               "stderr=%r" % r.stderr)

        # With 0423 genuinely taken, the suggestion must ADVANCE, not collide.
        open(os.path.join(tmp, "ccsim_query_202608060423.md"), "w").close()
        r = _run(PRE, _pre_payload(os.path.join(
            tmp, "ccsim_query_202608060423b.md")))
        ok = (r.returncode == 2
              and "ccsim_query_202608060424.md" in r.stderr)
        _check("F19c — `…0423b.md` with 0423 taken -> offered 0424", ok,
               "rc=%s stderr=%r" % (r.returncode, r.stderr))

        # And it keeps walking rather than offering an occupied minute twice.
        open(os.path.join(tmp, "ccsim_query_202608060424.md"), "w").close()
        r = _run(PRE, _pre_payload(os.path.join(
            tmp, "ccsim_query_202608060423b.md")))
        _check("F19d — 0423 and 0424 both taken -> offered 0425",
               "ccsim_query_202608060425.md" in r.stderr,
               "stderr=%r" % r.stderr)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_flint_blocks_every_real_tail_defect():
    for i, name in enumerate(REAL_TAIL_DEFECTS, 1):
        p = os.path.join(REPO_ROOT, "sessions", "2026", "202608", name)
        r = _run(PRE, _pre_payload(p))
        _check("F20.%d — real tail defect `%s` BLOCKED" % (i, name),
               r.returncode == 2 and "BLOCKED" in r.stderr,
               "rc=%s stderr=%r" % (r.returncode, r.stderr))


def test_flint_tail_rule_spares_every_sanctioned_shape():
    """The exemptions, each one a shape root CLAUDE.md itself mandates or a real
    repo file that is simply not comms. A rule that blocked §8.1.2's Move Rule
    would be worse than the defect it fixes."""
    for name in REAL_NON_COMMS_TAILS:
        p = os.path.join(REPO_ROOT, "sessions", "2026", "202608", name)
        r = _run(PRE, _pre_payload(p))
        ok = r.returncode == 0 and not r.stdout.strip() and not r.stderr.strip()
        _check("F21 — non-comms tail `%s` untouched" % name, ok,
               "rc=%s out=%r err=%r" % (r.returncode, r.stdout, r.stderr))


def test_flint_tail_rule_minute_rollover_and_pairing():
    tmp = tempfile.mkdtemp(prefix="flint-reg-tail2-")
    try:
        # A sanctioned same-TS sibling (§3.5.3) must NOT make the minute look
        # occupied —— a query_ and its response_ share one by design.
        open(os.path.join(tmp, "response_202608060423.md"), "w").close()
        r = _run(PRE, _pre_payload(os.path.join(tmp, "query_202608060423a.md")))
        _check("F22a — a sanctioned query_/response_ TS is not 'occupied'",
               "query_202608060423.md" in r.stderr, "stderr=%r" % r.stderr)

        # Midnight rollover: 2359 + 1 minute is the NEXT DAY, not 2360.
        open(os.path.join(tmp, "close_202608062359.md"), "w").close()
        r = _run(PRE, _pre_payload(os.path.join(tmp, "close_202608062359a.md")))
        _check("F22b — 2359 rolls to 202608070000, never 2360",
               "close_202608070000.md" in r.stderr, "stderr=%r" % r.stderr)

        # A `response_` may not simply re-stamp (§3.5.3), so the block says so
        # instead of silently instructing a different breach.
        r = _run(PRE, _pre_payload(os.path.join(tmp, "response_202607072124_r2.md")))
        _check("F22c — a response_ block cites §3.5.3 rather than just bumping",
               r.returncode == 2 and "3.5.3" in r.stderr,
               "rc=%s stderr=%r" % (r.returncode, r.stderr))

        # A 12-digit run that is not a real calendar time must not raise —— and
        # the clean name is pre-created so the BUMP path (which is what parses
        # the date) is genuinely exercised rather than short-circuited.
        open(os.path.join(tmp, "close_209913991399.md"), "w").close()
        r = _run(PRE, _pre_payload(os.path.join(tmp, "close_209913991399a.md")))
        _check("F22d — an impossible date still blocks, never a traceback",
               r.returncode == 2 and "Traceback" not in r.stderr,
               "rc=%s stderr=%r" % (r.returncode, r.stderr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_flint_tail_rule_advises_on_read_and_out_of_scope():
    """Same reach contract as rule 1 (hook_guide.md §4.7): the BLOCK is
    repo-scoped, and everything outside it downgrades to an advisory rather than
    going quiet (§4.4)."""
    p = os.path.join(REPO_ROOT, "sessions", "2026", "202608",
                     "ccsim_query_202608060423a.md")
    r = _run(PRE, _pre_payload(p, tool="Read"))
    adv = _advice(r)
    ok = (r.returncode == 0 and "[flint]" in adv and "ALERT THE USER" in adv
          and "ccsim_query_202608060423.md" in adv)
    _check("F23a — a READ of a tail offender advises, never blocks", ok,
           "rc=%s out=%r" % (r.returncode, r.stdout))

    other = "/Users/culous/some-other-project"
    r = _run(PRE, _pre_payload(os.path.join(other, "close_202608011234a.md"),
                               cwd=other))
    _check("F23b — out-of-repo cwd: advises, does NOT block",
           r.returncode == 0 and "[flint]" in _advice(r),
           "rc=%s out=%r err=%r" % (r.returncode, r.stdout, r.stderr))

    r = _run(["sh", FLINT_HOOK, "pre"], _pre_payload(p))
    _check("F23c — the shim propagates the rule-2 exit 2 too",
           r.returncode == 2 and "BLOCKED" in r.stderr,
           "rc=%s err=%r" % (r.returncode, r.stderr))


def test_tail_rule_against_the_whole_live_repo():
    """Re-derive rule 2's calibration on every run, exactly as F18 does for rule
    1: over every real basename in this repo the rule must hit the known
    offenders and NOTHING else. Missing hits are fine (they mean a rename
    happened); an UNEXPECTED hit is a broadened rule and fails here rather than
    in someone's commit."""
    comms = re.compile(r"^(?:❌_)?(?:[A-Za-z0-9][A-Za-z0-9-]*_)?"
                       r"(?:query|response|close|wrap|slog|artefact)_", re.I)
    ts_re = re.compile(r"(?<!\d)(20\d{10})(?!\d)")
    ok_tail = re.compile(r"^(?:\.[A-Za-z0-9]+)*$")
    moved = re.compile(r"^(?:\.[A-Za-z0-9]+)*_moved_")
    hits = []
    for dp, dns, fns in os.walk(REPO_ROOT):
        dns[:] = [d for d in dns if d not in (".git", "__pycache__", ".venv")]
        for f in fns:
            if not comms.match(f):
                continue
            m = ts_re.search(f)
            if not m:
                continue
            tail = f[m.end():]
            if ok_tail.match(tail) or moved.match(tail):
                continue
            hits.append(os.path.relpath(os.path.join(dp, f), REPO_ROOT))
    unexpected = [h for h in hits
                  if os.path.basename(h) not in REAL_TAIL_DEFECTS]
    _check("F24 — live repo sweep: %d tail hit(s), all of them known defects"
           % len(hits), not unexpected, "unexpected=%r" % unexpected)


def test_rule_against_the_whole_live_repo():
    """Re-derive the calibration on every run: over every real basename in this
    repo, the rule must hit the known offenders and NOTHING else. A future edit
    that broadens it fails here rather than in someone's commit."""
    defect_re = re.compile(r"^\S*_\s+(?=20\d{10}(?!\d))")
    hits = []
    for dp, dns, fns in os.walk(REPO_ROOT):
        dns[:] = [d for d in dns if d not in (".git", "__pycache__", ".venv")]
        for f in fns:
            if defect_re.search(f):
                hits.append(os.path.relpath(os.path.join(dp, f), REPO_ROOT))
    unexpected = [h for h in hits if os.path.basename(h) not in REAL_DEFECTS]
    _check("F18 — live repo sweep: %d hit(s), all of them known defects"
           % len(hits), not unexpected, "unexpected=%r" % unexpected)


# ---------------------------------------------------------------------------
# POST HALF —— TS clash + alert on encounter (never a hunt). Formerly tlint.py.
# ---------------------------------------------------------------------------

def test_post_sweeps_the_folder_it_already_lists():
    tmp = tempfile.mkdtemp(prefix="flint-reg-post-")
    try:
        offender = os.path.join(tmp, "close_ 202606142239.md")
        open(offender, "w").close()
        clean = os.path.join(tmp, "response_202608011234.md")
        open(clean, "w").close()

        r = _run(POST,_post_payload(clean))
        adv = _advice(r)
        ok = (r.returncode == 0 and "[flint]" in adv and offender in adv
              and "ALERT THE USER" in adv and "NOT go hunting" in adv)
        _check("T1 — a write into a folder holding an offender advises the model",
               ok, "rc=%s out=%r" % (r.returncode, r.stdout))

        # T2: the sweep must fire even though this folder has NO timestamp clash
        # —— it is independent of the check it borrows the listing from.
        _check("T2 — the sweep fires with a perfectly clean TS (no clash)",
               "[flint]" in adv and not r.stderr.strip(),
               "stderr=%r" % r.stderr)

        # T2b: the advisory must be tagged for the event it fired on, or the
        # harness may discard it (hook_guide.md §6.8.1).
        try:
            ev = (json.loads(r.stdout.strip()).get("hookSpecificOutput")
                  or {}).get("hookEventName", "")
        except Exception:
            ev = ""
        _check("T2b — post advisory is tagged hookEventName=PostToolUse",
               ev == "PostToolUse", "hookEventName=%r" % ev)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_post_silent_when_the_folder_is_clean():
    tmp = tempfile.mkdtemp(prefix="flint-reg-post-")
    try:
        for n in ("close_202606142239.md", "AJAP Logs 202607182259.csv",
                  "MGTK746 Dev Plan _ 202603170315.txt"):
            open(os.path.join(tmp, n), "w").close()
        clean = os.path.join(tmp, "response_202608011234.md")
        open(clean, "w").close()
        r = _run(POST,_post_payload(clean))
        ok = r.returncode == 0 and not r.stdout.strip()
        _check("T3 — legitimate spaced neighbours are NOT swept up", ok,
               "rc=%s out=%r" % (r.returncode, r.stdout))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_post_ts_clash_behaviour_is_unchanged():
    tmp = tempfile.mkdtemp(prefix="flint-reg-post-")
    try:
        # A sanctioned query_/response_ pair must still be silent on both channels.
        q = os.path.join(tmp, "query_202608011234.md")
        resp = os.path.join(tmp, "response_202608011234.md")
        open(q, "w").close()
        open(resp, "w").close()
        r = _run(POST,_post_payload(resp))
        _check("T4 — sanctioned query_/response_ pair still silent",
               r.returncode == 0 and not r.stdout.strip() and not r.stderr.strip(),
               "rc=%s out=%r err=%r" % (r.returncode, r.stdout, r.stderr))

        # An unsanctioned clash must still warn on stderr, exit 0.
        other = os.path.join(tmp, "close_202608011234.md")
        open(other, "w").close()
        r = _run(POST,_post_payload(resp))
        _check("T5 — unsanctioned TS clash still warns on stderr, exit 0",
               r.returncode == 0 and "TS clash" in r.stderr,
               "rc=%s err=%r" % (r.returncode, r.stderr))

        # Both findings at once: the clash on stderr, the stray on stdout.
        open(os.path.join(tmp, "wrap_ 202607312359.md"), "w").close()
        r = _run(POST,_post_payload(resp))
        _check("T6 — clash and stray report together, on their own channels",
               r.returncode == 0 and "TS clash" in r.stderr
               and "[flint]" in _advice(r),
               "rc=%s out=%r err=%r" % (r.returncode, r.stdout, r.stderr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_post_sweep_covers_the_tail_defect_too():
    """The sweep borrows a listing it was taking anyway, so covering the second
    defect class there is free. Both classes must arrive in ONE advisory —— a
    second `_advise()` call would put a second JSON object on stdout and the
    harness would parse neither."""
    tmp = tempfile.mkdtemp(prefix="flint-reg-post-tail-")
    try:
        tail_off = os.path.join(tmp, "ccsim_query_202608060423a.md")
        space_off = os.path.join(tmp, "close_ 202606142239.md")
        for p in (tail_off, space_off):
            open(p, "w").close()
        clean = os.path.join(tmp, "response_202608011234.md")
        open(clean, "w").close()

        r = _run(POST, _post_payload(clean))
        adv = _advice(r)
        _check("T11a — a tail offender beside a write is reported",
               r.returncode == 0 and tail_off in adv,
               "rc=%s out=%r" % (r.returncode, r.stdout))
        _check("T11b — both defect classes arrive in ONE advisory",
               space_off in adv and tail_off in adv
               and r.stdout.strip().count("hookSpecificOutput") == 1,
               "out=%r" % r.stdout)
        _check("T11c — the sweep still never blocks",
               r.returncode == 0 and "BLOCKED" not in r.stderr,
               "rc=%s err=%r" % (r.returncode, r.stderr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # And a folder of sanctioned shapes stays silent, so the sweep cannot start
    # nagging about `_moved_` files root §8.1.2 requires.
    tmp = tempfile.mkdtemp(prefix="flint-reg-post-tail2-")
    try:
        for n in ("query_202607282109_moved_202607.md",
                  "ccsim_close_202607282109.md_moved_skipped",
                  "response_202606231628.pages.md",
                  "test_live_202607190438_fixes.py"):
            open(os.path.join(tmp, n), "w").close()
        clean = os.path.join(tmp, "response_202608011234.md")
        open(clean, "w").close()
        r = _run(POST, _post_payload(clean))
        _check("T11d — sanctioned tails are NOT swept up",
               r.returncode == 0 and not r.stdout.strip(),
               "rc=%s out=%r" % (r.returncode, r.stdout))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_post_ignores_a_tsless_write():
    """The sweep must stay a by-product, never a scan: a write with no TS in its
    own name exits before any listing happens."""
    tmp = tempfile.mkdtemp(prefix="flint-reg-post-")
    try:
        open(os.path.join(tmp, "close_ 202606142239.md"), "w").close()
        target = os.path.join(tmp, "notes.md")
        open(target, "w").close()
        r = _run(POST,_post_payload(target))
        ok = r.returncode == 0 and not r.stdout.strip() and not r.stderr.strip()
        _check("T7 — a TS-less write triggers no sweep (encounter, not hunt)",
               ok, "rc=%s out=%r" % (r.returncode, r.stdout))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_post_half_stays_global_after_the_merge():
    """THE MERGE'S SHARPEST HAZARD (hook_guide.md §4.6/§4.7). The PRE half is
    repo-scoped because it BLOCKS; the POST half is deliberately GLOBAL because
    it can only warn, and a missed TS clash in the sibling AJAP repo is silent
    and expensive. Merging the two into one file makes it trivially tempting to
    hoist `_in_scope()` to the top of `main()` "for consistency" —— one line
    that would delete AJAP coverage whilst every other test here still passed.
    These cases assert the absence of that line from the outside."""
    tmp = tempfile.mkdtemp(prefix="flint-reg-reach-")
    try:
        # An unsanctioned clash AND an offender, in a folder that is nowhere
        # near this repo, reached from a foreign project.
        resp = os.path.join(tmp, "response_202608011234.md")
        for n in ("response_202608011234.md", "close_202608011234.md",
                  "wrap_ 202607312359.md"):
            open(os.path.join(tmp, n), "w").close()

        foreign = "/Users/culous/some-other-project"
        r = _run(POST, _post_payload(resp, cwd=foreign))
        _check("T8a — foreign cwd: TS clash STILL warns (post half is global)",
               r.returncode == 0 and "TS clash" in r.stderr,
               "rc=%s err=%r" % (r.returncode, r.stderr))
        _check("T8b — foreign cwd: stray sweep STILL advises",
               "[flint]" in _advice(r), "out=%r" % r.stdout)

        r = _run(POST, _post_payload(
            resp, cwd=None,
            transcript="/Users/culous/.claude/projects/-Users-culous-other/x.jsonl"))
        _check("T8c — foreign transcript slug: TS clash STILL warns",
               r.returncode == 0 and "TS clash" in r.stderr,
               "rc=%s err=%r" % (r.returncode, r.stderr))

        r = _run(POST, _post_payload(resp, cwd=None))
        _check("T8d — unscopeable payload: TS clash STILL warns (fail-open)",
               r.returncode == 0 and "TS clash" in r.stderr,
               "rc=%s err=%r" % (r.returncode, r.stderr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_post_half_never_blocks():
    """`hook_guide.md` §6.7 —— PostToolUse cannot undo a write, so an exit 2
    there buys error framing and nothing else. The post half must never return
    one, INCLUDING on the very path the pre half blocks: after the merge the
    blocking code is one function away, so this is the case that would break
    first if a mode ever leaked."""
    tmp = tempfile.mkdtemp(prefix="flint-reg-noblock-")
    try:
        bad = os.path.join(tmp, "close_ 202608011234.md")
        open(bad, "w").close()
        r = _run(POST, _post_payload(bad))
        _check("T9a — post half exits 0 on a path the pre half BLOCKS",
               r.returncode == 0 and "BLOCKED" not in r.stderr,
               "rc=%s err=%r" % (r.returncode, r.stderr))

        # And the same payload through the pre half must still block, so T9a is
        # evidence about the MODE, not about a gate that quietly went away.
        r = _run(PRE, _pre_payload(bad))
        _check("T9b — the identical path through the pre half still BLOCKS",
               r.returncode == 2 and "BLOCKED" in r.stderr,
               "rc=%s err=%r" % (r.returncode, r.stderr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# MODE SELECTION —— argv first, `hook_event_name` fallback
# ---------------------------------------------------------------------------

def test_mode_selection():
    """A settings edit takes MINUTES to go live (hook_guide.md §7.9), so for
    that window the OLD argument-less registration is still firing this file.
    The payload fallback is what keeps the gate alive across it —— untested,
    the merge would open a silent hole every time the registration changes."""
    tmp = tempfile.mkdtemp(prefix="flint-reg-mode-")
    try:
        bad = os.path.join(tmp, "close_ 202608011234.md")
        open(bad, "w").close()
        open(os.path.join(tmp, "wrap_202608011234.md"), "w").close()

        # M1 — no argv at all, PreToolUse payload -> pre half -> BLOCKS.
        r = _run(["python3", FLINT], _pre_payload(bad))
        _check("M1 — argv-less + hook_event_name=PreToolUse -> pre half blocks",
               r.returncode == 2 and "BLOCKED" in r.stderr,
               "rc=%s err=%r" % (r.returncode, r.stderr))

        # M2 — no argv at all, PostToolUse payload -> post half -> warns, exit 0.
        r = _run(["python3", FLINT], _post_payload(bad))
        _check("M2 — argv-less + hook_event_name=PostToolUse -> post half warns",
               r.returncode == 0 and "TS clash" in r.stderr
               and "BLOCKED" not in r.stderr,
               "rc=%s err=%r" % (r.returncode, r.stderr))

        # M3 — argv OVERRIDES the payload, in both directions. This is what
        # makes the registration authoritative rather than merely advisory.
        r = _run(PRE, _post_payload(bad))
        _check("M3a — argv `pre` beats a PostToolUse payload -> blocks",
               r.returncode == 2, "rc=%s err=%r" % (r.returncode, r.stderr))
        r = _run(POST, _pre_payload(bad))
        _check("M3b — argv `post` beats a PreToolUse payload -> never blocks",
               r.returncode == 0 and "BLOCKED" not in r.stderr,
               "rc=%s err=%r" % (r.returncode, r.stderr))

        # M4 — the SHIM must forward the argument. A shim that dropped it would
        # leave M1–M3 passing and the live PostToolUse half running as `pre`.
        r = _run(["sh", FLINT_HOOK, "post"], _pre_payload(bad))
        _check("M4a — shim forwards `post` (no block, TS clash warned)",
               r.returncode == 0 and "TS clash" in r.stderr,
               "rc=%s err=%r" % (r.returncode, r.stderr))
        r = _run(["sh", FLINT_HOOK, "pre"], _post_payload(bad))
        _check("M4b — shim forwards `pre` (blocks despite a post payload)",
               r.returncode == 2, "rc=%s err=%r" % (r.returncode, r.stderr))
        r = _run(["sh", FLINT_HOOK], _pre_payload(bad))
        _check("M4c — shim with NO argument still runs (falls back, blocks)",
               r.returncode == 2, "rc=%s err=%r" % (r.returncode, r.stderr))

        # M5 — a junk argument must not silently pick a half; it falls through
        # to the payload, which is the only other trustworthy signal.
        r = _run(["python3", FLINT, "banana"], _post_payload(bad))
        _check("M5 — unrecognised argv falls back to hook_event_name",
               r.returncode == 0 and "TS clash" in r.stderr,
               "rc=%s err=%r" % (r.returncode, r.stderr))

        # M6 — neither argv nor a usable event name -> default PRE, because
        # losing the block is the only unrecoverable outcome (a stray exit 2 at
        # PostToolUse is noise; a missed block is a file on disk).
        d = _pre_payload(bad)
        del d["hook_event_name"]
        r = _run(["python3", FLINT], d)
        _check("M6 — no argv and no hook_event_name -> defaults to pre (blocks)",
               r.returncode == 2, "rc=%s err=%r" % (r.returncode, r.stderr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_post_half_fail_safe_on_malformed_payloads():
    """The post half inherits the pre half's fail-safe promise: no traceback,
    no exit 1, and —— unlike the pre half —— never an exit 2 either."""
    malformed = (
        "{not json at all",
        json.dumps([1, 2, 3]),
        json.dumps({"tool_name": "Write"}),
        json.dumps({"tool_name": "Write", "tool_input": "a string"}),
        json.dumps({"tool_name": "Write", "tool_input": {"file_path": 123}}),
        json.dumps({"tool_input": {"file_path": "close_ 202608011234.md"}}),
        "",
    )
    for i, bad in enumerate(malformed, 1):
        r = _run(POST, bad)
        ok = r.returncode == 0 and "Traceback" not in r.stderr
        _check("T10.%d — post half: no traceback, no exit 1, no exit 2" % i, ok,
               "rc=%s err=%r" % (r.returncode, r.stderr))


# ---------------------------------------------------------------------------
# PRE-COMMIT —— the net under the routes no PreToolUse hook can see
# ---------------------------------------------------------------------------

def _scratch_repo():
    tmp = tempfile.mkdtemp(prefix="flint-reg-git-")
    subprocess.run(["git", "init", "-q", tmp], check=True, capture_output=True)
    subprocess.run(["git", "-C", tmp, "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", tmp, "config", "user.name", "t"], check=True)
    os.makedirs(os.path.join(tmp, "sessions", "2026", "202608"))
    return tmp


def _hook(repo):
    return subprocess.run(["sh", PRECOMMIT], cwd=repo, capture_output=True,
                          text=True)


def _stage(repo, relpath, content="x"):
    full = os.path.join(repo, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as fh:
        fh.write(content)
    subprocess.run(["git", "-C", repo, "add", "--", relpath], check=True,
                   capture_output=True)


def test_precommit_blocks_a_staged_add():
    repo = _scratch_repo()
    try:
        _stage(repo, "sessions/2026/202608/close_ 202608011234.md")
        r = _hook(repo)
        ok = r.returncode != 0 and "BLOCKED" in r.stdout
        _check("P1 — staged ADD of an offender BLOCKS the commit", ok,
               "rc=%s out=%r err=%r" % (r.returncode, r.stdout, r.stderr))
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_precommit_warns_but_allows_a_modify():
    repo = _scratch_repo()
    try:
        rel = "sessions/2026/202608/close_ 202608011234.md"
        _stage(repo, rel)
        subprocess.run(["git", "-C", repo, "commit", "-q", "--no-verify",
                        "-m", "seed"], check=True, capture_output=True)
        _stage(repo, rel, content="changed")
        r = _hook(repo)
        ok = r.returncode == 0 and "reminder" in r.stdout and "BLOCKED" not in r.stdout
        _check("P2 — staged MODIFY of an existing offender warns, does not block",
               ok, "rc=%s out=%r" % (r.returncode, r.stdout))
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_precommit_allows_clean_and_legitimate_names():
    repo = _scratch_repo()
    try:
        _stage(repo, "sessions/2026/202608/query_202608011234.md")
        _stage(repo, "sessions/2026/202608/response_202608011234.md")
        for n in REAL_LEGITIMATE:
            _stage(repo, "cp/archive/mip/" + n)
        r = _hook(repo)
        ok = r.returncode == 0 and "stray space" not in r.stdout
        _check("P3 — clean comms + legitimate spaced names commit freely", ok,
               "rc=%s out=%r" % (r.returncode, r.stdout))
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_precommit_allows_the_rename_that_fixes_it():
    """The fix must not be gated by the gate. A `git mv` to a good name stages
    as a rename (or delete+add), and neither reads as an ADD of a bad path."""
    repo = _scratch_repo()
    try:
        bad = "sessions/2026/202608/close_ 202608011234.md"
        _stage(repo, bad)
        subprocess.run(["git", "-C", repo, "commit", "-q", "--no-verify",
                        "-m", "seed"], check=True, capture_output=True)
        subprocess.run(["git", "-C", repo, "mv", "--", bad,
                        "sessions/2026/202608/close_202608011234.md"],
                       check=True, capture_output=True)
        r = _hook(repo)
        ok = r.returncode == 0 and "BLOCKED" not in r.stdout
        _check("P4 — the corrective `git mv` commits cleanly", ok,
               "rc=%s out=%r" % (r.returncode, r.stdout))
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_precommit_pairing_lint_still_works_and_survives_spaces():
    repo = _scratch_repo()
    try:
        _stage(repo, "sessions/2026/202608/response_202608011234.md")
        r = _hook(repo)
        ok = r.returncode == 0 and "no sibling query" in r.stdout
        _check("P5 — the orphaned-response reminder still fires, non-blocking",
               ok, "rc=%s out=%r" % (r.returncode, r.stdout))
    finally:
        shutil.rmtree(repo, ignore_errors=True)

    # A space-bearing path used to be torn in two by `for f in $staged`; the
    # loop now reads line-wise, so the pairing lint sees the whole path and
    # says nothing about it (it is not a `response_`).
    repo = _scratch_repo()
    try:
        rel = "sessions/2026/202608/close_ 202608011234.md"
        _stage(repo, rel)
        subprocess.run(["git", "-C", repo, "commit", "-q", "--no-verify",
                        "-m", "seed"], check=True, capture_output=True)
        _stage(repo, rel, content="changed")
        _stage(repo, "sessions/2026/202608/response_202608011299.md")
        r = _hook(repo)
        ok = ("202608011234.md" not in r.stdout.split("reminder:")[-1]
              or "no sibling query" in r.stdout)
        _check("P6 — a space-bearing path no longer word-splits in the loop",
               r.returncode == 0 and "no sibling query" in r.stdout,
               "rc=%s out=%r" % (r.returncode, r.stdout))
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_precommit_sync_path_untouched():
    """The #sync allowlist arm returns before the new net, exactly as before."""
    repo = _scratch_repo()
    try:
        _stage(repo, "sessions/2026/202608/close_ 202608011234.md")
        gitdir = subprocess.run(["git", "-C", repo, "rev-parse", "--git-dir"],
                                capture_output=True, text=True).stdout.strip()
        marker = os.path.join(repo, gitdir, "SYNC_ACTIVE") \
            if not os.path.isabs(gitdir) else os.path.join(gitdir, "SYNC_ACTIVE")
        with open(marker, "w") as fh:
            fh.write("sessions/2026/202608/close_ 202608011234.md\n")
        r = _hook(repo)
        ok = r.returncode == 0 and "BLOCKED" not in r.stdout
        _check("P7 — the #sync allowlist arm still short-circuits unchanged", ok,
               "rc=%s out=%r" % (r.returncode, r.stdout))

        # And it must still REFUSE anything off the allowlist. The loop's exit
        # plumbing changed when it was made space-safe, so the refusal is worth
        # pinning: a `while` in a pipeline runs in a subshell, where a bare
        # `exit 1` would have been swallowed and the guard silently disarmed.
        _stage(repo, "sessions/2026/202608/response_202608011234.md")
        r = _hook(repo)
        ok = r.returncode != 0 and "not in the allowlist" in r.stdout
        _check("P8 — the #sync allowlist arm still BLOCKS an off-list file", ok,
               "rc=%s out=%r" % (r.returncode, r.stdout))
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def main():
    for fn in (
        test_flint_blocks_every_real_defect,
        test_flint_blocks_every_write_class_tool,
        test_flint_blocks_exotic_whitespace_runs,
        test_flint_ignores_clean_and_conventional_names,
        test_flint_does_not_touch_legitimate_spaced_names,
        test_flint_boundary_cases,
        test_flint_advises_on_read_never_blocks,
        test_flint_downgrades_to_advisory_out_of_scope,
        test_flint_fails_open_on_unscopeable_payload,
        test_flint_fail_safe_on_malformed_payloads,
        test_flint_hook_shim_is_the_wiring,
        test_rule_against_the_whole_live_repo,
        test_flint_blocks_the_letter_suffix_defect,
        test_flint_blocks_every_real_tail_defect,
        test_flint_tail_rule_spares_every_sanctioned_shape,
        test_flint_tail_rule_minute_rollover_and_pairing,
        test_flint_tail_rule_advises_on_read_and_out_of_scope,
        test_tail_rule_against_the_whole_live_repo,
        test_post_sweeps_the_folder_it_already_lists,
        test_post_silent_when_the_folder_is_clean,
        test_post_ts_clash_behaviour_is_unchanged,
        test_post_sweep_covers_the_tail_defect_too,
        test_post_ignores_a_tsless_write,
        test_post_half_stays_global_after_the_merge,
        test_post_half_never_blocks,
        test_mode_selection,
        test_post_half_fail_safe_on_malformed_payloads,
        test_precommit_blocks_a_staged_add,
        test_precommit_warns_but_allows_a_modify,
        test_precommit_allows_clean_and_legitimate_names,
        test_precommit_allows_the_rename_that_fixes_it,
        test_precommit_pairing_lint_still_works_and_survives_spaces,
        test_precommit_sync_path_untouched,
    ):
        fn()

    print()
    passed = sum(1 for r in results if r)
    print("%d/%d passed" % (passed, len(results)))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
