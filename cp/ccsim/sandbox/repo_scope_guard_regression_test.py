#!/usr/bin/env python3
"""Regression test for the REPO-SCOPE GUARD added to all 5 cscpt/ hook
scripts (clint.py, hlint.py, nlint.py, tlint.py, dlint_hook.py).

WHY this test exists (coding.md: "a fix without its test is unfinished"):
all 5 hooks moved from a PROJECT-level settings.json registration (which
Claude Desktop never actually executes) to the USER-level
~/.claude/settings.json (which it does execute) — but a user-level
registration fires for EVERY project open on the Mac, not just this repo.
Each script therefore gained a guard that must (a) let this repo's own
invocations through completely unchanged, (b) go silent for any OTHER
project, using EITHER the payload's `cwd` or a `transcript_path` project
slug fallback, and (c) fail OPEN (i.e. behave as if the guard were absent)
whenever neither field is usable, because a lint that goes silently dark on
ambiguity is exactly the class of bug this whole hook-migration effort
exists to fix. This test drives each of the 5 scripts through its REAL
registered invocation path (the exact shim/interpreter command listed in
.claude/settings.json) with synthesised payloads, so it proves the guard is
WIRED end-to-end, not just correct in isolation (coding.md: "'exists +
unit-tested' != done -- done only when WIRED and exercised end-to-end").

Self-contained: every fixture (transcripts, comms-file pairs, TS-clash
pairs) is synthesised into a throwaway tempdir at run time; the one
exception is cscpt's own real `cp/ccsim/sandbox/hook_probe_response_.md`
probe fixture, reused deliberately for the dlint_hook.py cases because it
is the exact artefact the task's own acceptance test names (a real file
with 5 guaranteed dlint RED flags) -- nothing here is deleted or modified.
Run directly:

    python3 "cp/ccsim/sandbox/repo_scope_guard_regression_test.py"

Exits 0 if every case matches its expected verdict, 1 otherwise (with a
per-case PASS/FAIL report on stdout, and full diagnostics on any FAIL).
"""
import json
import os
import re
import subprocess
import sys
import tempfile

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.realpath(os.path.join(_THIS_DIR, "..", "..", ".."))
CSCPT = os.path.join(REPO_ROOT, "cscpt")

# An out-of-scope project directory: a SIBLING of this repo under the same
# GitHub/ parent. It need not actually exist on disk -- os.path.realpath()
# never requires a path to exist, it only resolves the symlink components
# that DO -- so this is safe regardless of what's really on this Mac.
OUT_OF_SCOPE_CWD = os.path.join(os.path.dirname(REPO_ROOT), "AJAP_repo")

# A sibling directory whose NAME merely shares this repo's path as a raw
# string PREFIX, with no path separator in between (e.g.
# ".../dupbus-ceztuc-7cufVe-sibling" vs ".../dupbus-ceztuc-7cufVe"). Used to
# pin that the guard's cwd check is separator-bounded, not a naive
# str.startswith(), which would otherwise wrongly call this in-scope.
PREFIX_COLLISION_CWD = REPO_ROOT + "-sibling"

# A genuine sub-directory of the repo (real, on disk) -- used to pin that a
# session whose cwd is a sub-path of the repo root is still in-scope.
SUBDIR_CWD = os.path.join(REPO_ROOT, "cp", "ccsim")


def _project_slug(path):
    """Mirrors the guard's own slug transform: Claude Code's
    ~/.claude/projects/ folder name for a project directory is that
    directory's path with every '/' and ' ' replaced by '-' (verified live
    against a real captured transcript_path this session)."""
    return re.sub(r"[/ ]", "-", path.rstrip("/"))


REPO_SLUG = _project_slug(REPO_ROOT)
OOS_SLUG = _project_slug(OUT_OF_SCOPE_CWD)

# transcript_path values whose slug segment matches / does not match this
# repo -- used for the "no cwd, fall back to transcript_path" branch. The
# files need not exist; the guard only ever regexes the string.
IN_SCOPE_TP = "/Users/culous/.claude/projects/%s/deadbeef-inscope.jsonl" % REPO_SLUG
OOS_TP = "/Users/culous/.claude/projects/%s/deadbeef-oos.jsonl" % OOS_SLUG
UNPARSEABLE_TP = "/dev/null"  # present, but no '/projects/<slug>/' shape at all

_RESULTS = []


def _record(label, ok, run=None):
    status = "PASS" if ok else "FAIL"
    print("[%s] %s" % (status, label))
    if not ok and run is not None:
        print("        exit=%s" % run.returncode)
        print("        stdout=%r" % run.stdout)
        print("        stderr=%r" % run.stderr)
    _RESULTS.append(ok)
    return ok


# --- payload builders: exact top-level key lists as verified live this ----
# --- session (PostToolUse / Stop / UserPromptSubmit). `cwd=None` means ----
# --- OMIT the key entirely (simulates the one payload shape variance ------
# --- the guard must tolerate); every other field is always present. ------

def _stop_payload(transcript_path, cwd=None):
    d = {
        "session_id": "scopetest",
        "transcript_path": transcript_path,
        "prompt_id": "pid-scopetest",
        "permission_mode": "default",
        "effort": "medium",
        "hook_event_name": "Stop",
        "stop_hook_active": False,
        "last_assistant_message": "placeholder",
        "background_tasks": [],
        "session_crons": [],
    }
    if cwd is not None:
        d["cwd"] = cwd
    return d


def _user_prompt_submit_payload(prompt, transcript_path="/dev/null", cwd=None):
    d = {
        "session_id": "scopetest",
        "transcript_path": transcript_path,
        "prompt_id": "pid-scopetest",
        "permission_mode": "default",
        "hook_event_name": "UserPromptSubmit",
        "prompt": prompt,
        "session_title": "repo-scope-guard regression",
    }
    if cwd is not None:
        d["cwd"] = cwd
    return d


def _post_tool_use_payload(file_path, transcript_path="/dev/null", cwd=None,
                            tool_name="Write", content=""):
    d = {
        "session_id": "scopetest",
        "transcript_path": transcript_path,
        "prompt_id": "pid-scopetest",
        "permission_mode": "default",
        "effort": "medium",
        "hook_event_name": "PostToolUse",
        "tool_name": tool_name,
        "tool_input": {"file_path": file_path, "content": content},
        "tool_response": {"filePath": file_path, "success": True},
        "tool_use_id": "tu-scopetest",
        "duration_ms": 1,
    }
    if cwd is not None:
        d["cwd"] = cwd
    return d


def _run(cmd, payload, env_overrides=None):
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        cmd, input=json.dumps(payload), capture_output=True, text=True,
        timeout=30, cwd=REPO_ROOT, env=env,
    )


def _run_direct(script, payload, env_overrides=None):
    return _run([sys.executable, os.path.join(CSCPT, script)], payload, env_overrides)


def _run_shim(shim, payload):
    return _run(["bash", os.path.join(CSCPT, shim)], payload)


def _run_clint(payload, log_path):
    r = _run_direct("clint.py", payload, {"CLINT_LOG": log_path})
    log = ""
    if os.path.isfile(log_path):
        with open(log_path, "r", encoding="utf-8") as fh:
            log = fh.read()
    return r, log


def _make_breach_transcript(tmpdir):
    """A minimal transcript whose final turn is glyph-free prose -- clint's
    OWN (unmodified) breach condition."""
    path = os.path.join(tmpdir, "transcript.jsonl")
    lines = [
        {"type": "user", "isSidechain": False,
         "message": {"role": "user", "content": "please respond"}},
        {"type": "assistant", "isSidechain": False,
         "message": {"role": "assistant", "content": [
             {"type": "text",
              "text": "Sure, here is some unauthorised prose without a glyph."}]}},
    ]
    with open(path, "w", encoding="utf-8") as fh:
        for ln in lines:
            fh.write(json.dumps(ln) + "\n")
    return path


def _make_nlint_fixture(tmpdir):
    """An illegitimate numbering reset -- nlint's OWN (unmodified) flag
    condition: replies (query says 'Reply to'), resets to 1, and nothing in
    the query names both a reset word and an override word."""
    query = os.path.join(tmpdir, "illegit_query.md")
    response = os.path.join(tmpdir, "illegit_response_202501020000.md")
    with open(query, "w", encoding="utf-8") as fh:
        fh.write("# Reply to old_response_202412310000.md\n\n"
                  "## 9\nPlease continue with the next steps.\n")
    with open(response, "w", encoding="utf-8") as fh:
        fh.write("# Response to illegit_query.md\n\n"
                  "## 1. Restarted With No Excuse\n"
                  "- 1.1. No session-start or override language anywhere "
                  "in the query above.\n")
    return response


def _make_tlint_fixture(tmpdir):
    """Two same-folder, same-TS files whose roles ('note', 'other') are
    NEITHER sanctioned pair -- tlint's OWN (unmodified) flag condition."""
    ts = "202501020000"
    a = os.path.join(tmpdir, "note_%s.md" % ts)
    b = os.path.join(tmpdir, "other_%s.md" % ts)
    for p in (a, b):
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("placeholder\n")
    return a


PROBE_FILE_REL = "cp/ccsim/sandbox/hook_probe_response_.md"  # real, 5 RED flags


def section_clint():
    print("\n--- clint.py (Stop hook, invoked directly, as settings.json does) ---")
    with tempfile.TemporaryDirectory() as td:
        transcript = _make_breach_transcript(td)

        # A1: in-scope (cwd = repo root) -> block, EXACTLY as pre-guard.
        log1 = os.path.join(td, "log1.log")
        payload = _stop_payload(transcript, cwd=REPO_ROOT)
        r, log = _run_clint(payload, log1)
        _record("A1 in-scope cwd=repo root -> still BLOCKS (exit 2), breach unchanged",
                 r.returncode == 2 and "prose" in r.stderr.lower() and "action=block" in log,
                 r)

        # A2: out-of-scope via cwd -> silent, logged distinctly.
        log2 = os.path.join(td, "log2.log")
        payload = _stop_payload(transcript, cwd=OUT_OF_SCOPE_CWD)
        r, log = _run_clint(payload, log2)
        _record("A2 out-of-scope cwd (sibling repo) -> exit 0, no stderr, logged out_of_scope",
                 r.returncode == 0 and r.stderr == "" and "action=out_of_scope" in log,
                 r)

        # A3: out-of-scope via transcript_path slug (no cwd key at all).
        log3 = os.path.join(td, "log3.log")
        payload = _stop_payload(OOS_TP, cwd=None)
        r, log = _run_clint(payload, log3)
        _record("A3 out-of-scope transcript_path slug (no cwd key) -> exit 0, logged out_of_scope",
                 r.returncode == 0 and r.stderr == "" and "action=out_of_scope" in log,
                 r)

        # A4: fail-open -- neither cwd nor transcript_path usable. clint's
        # OWN (unmodified) logic then can't find a transcript either, so it
        # logs "no_transcript" -- the key assertion is that the tag is
        # no_transcript, NOT out_of_scope, proving the guard did not itself
        # swallow the invocation.
        log4 = os.path.join(td, "log4.log")
        payload = _stop_payload("", cwd=None)
        r, log = _run_clint(payload, log4)
        _record("A4 fail-open (neither field) -> falls through to clint's own no_transcript path",
                 r.returncode == 0 and "action=no_transcript" in log and "out_of_scope" not in log,
                 r)

        # A5 (nuance): a sub-directory of the repo root is still in-scope.
        log5 = os.path.join(td, "log5.log")
        payload = _stop_payload(transcript, cwd=SUBDIR_CWD)
        r, log = _run_clint(payload, log5)
        _record("A5 in-scope cwd = repo SUB-DIRECTORY -> still BLOCKS (exit 2)",
                 r.returncode == 2 and "action=block" in log,
                 r)

        # A6 (nuance): a same-PREFIX sibling (no separator) must NOT match.
        log6 = os.path.join(td, "log6.log")
        payload = _stop_payload(transcript, cwd=PREFIX_COLLISION_CWD)
        r, log = _run_clint(payload, log6)
        _record("A6 out-of-scope: prefix-collision cwd (repo-name+suffix, no separator) -> exit 0",
                 r.returncode == 0 and "action=out_of_scope" in log,
                 r)


def section_hlint():
    print("\n--- hlint.py (UserPromptSubmit hook, invoked directly) ---")
    prompt = "#buy a new laptop, what should I consider?"

    # B1: in-scope -> still emits the reminder, unchanged.
    payload = _user_prompt_submit_payload(prompt, cwd=REPO_ROOT)
    r = _run_direct("hlint.py", payload)
    _record("B1 in-scope cwd=repo root -> still emits #buy -> universal/buy.md reminder",
            r.returncode == 0 and "universal/buy.md" in r.stdout, r)

    # B2: out-of-scope via cwd -> silent.
    payload = _user_prompt_submit_payload(prompt, cwd=OUT_OF_SCOPE_CWD)
    r = _run_direct("hlint.py", payload)
    _record("B2 out-of-scope cwd (sibling repo) -> exit 0, empty stdout",
            r.returncode == 0 and r.stdout.strip() == "", r)

    # B3: out-of-scope via transcript_path slug (no cwd key).
    payload = _user_prompt_submit_payload(prompt, transcript_path=OOS_TP, cwd=None)
    r = _run_direct("hlint.py", payload)
    _record("B3 out-of-scope transcript_path slug (no cwd key) -> exit 0, empty stdout",
            r.returncode == 0 and r.stdout.strip() == "", r)

    # B4: fail-open -- neither field usable; hlint's OWN logic needs only
    # `prompt`, so a full, unsuppressed reminder is the correct proof.
    payload = _user_prompt_submit_payload(prompt, transcript_path="", cwd=None)
    r = _run_direct("hlint.py", payload)
    _record("B4 fail-open (neither field) -> STILL emits the #buy reminder in full",
            r.returncode == 0 and "universal/buy.md" in r.stdout, r)


def section_nlint():
    print("\n--- nlint.py (PostToolUse hook, invoked via nlint.sh, as settings.json does) ---")
    with tempfile.TemporaryDirectory() as td:
        response = _make_nlint_fixture(td)

        def flagged(r):
            return bool(r.stdout.strip()) or r.returncode != 0

        # C1: in-scope -> still flags the illegitimate reset.
        payload = _post_tool_use_payload(response, cwd=REPO_ROOT)
        r = _run_shim("nlint.sh", payload)
        _record("C1 in-scope cwd=repo root -> still FLAGS illegitimate reset",
                flagged(r), r)

        # C2: out-of-scope via cwd -> silent, even though the same file
        # would otherwise flag.
        payload = _post_tool_use_payload(response, cwd=OUT_OF_SCOPE_CWD)
        r = _run_shim("nlint.sh", payload)
        _record("C2 out-of-scope cwd (sibling repo) -> silent despite reset-shaped file",
                not flagged(r), r)

        # C3: out-of-scope via transcript_path slug (no cwd key).
        payload = _post_tool_use_payload(response, transcript_path=OOS_TP, cwd=None)
        r = _run_shim("nlint.sh", payload)
        _record("C3 out-of-scope transcript_path slug (no cwd key) -> silent",
                not flagged(r), r)

        # C4: fail-open -- neither field usable -> still flags (nlint's own
        # logic needs only tool_input.file_path).
        payload = _post_tool_use_payload(response, transcript_path="", cwd=None)
        r = _run_shim("nlint.sh", payload)
        _record("C4 fail-open (neither field) -> STILL flags illegitimate reset",
                flagged(r), r)

        # C5 (nuance): transcript_path present but NOT the recognised
        # '.../projects/<slug>/...' shape -> unparseable -> fail-open, not
        # a silent false "out of scope".
        payload = _post_tool_use_payload(response, transcript_path=UNPARSEABLE_TP, cwd=None)
        r = _run_shim("nlint.sh", payload)
        _record("C5 fail-open: transcript_path present but unparseable shape -> STILL flags",
                flagged(r), r)


def section_tlint():
    print("\n--- tlint.py (PostToolUse hook, invoked via tlint.sh, as settings.json does) ---")
    with tempfile.TemporaryDirectory() as td:
        written = _make_tlint_fixture(td)

        # D1: in-scope -> still flags the TS clash (stderr non-empty).
        payload = _post_tool_use_payload(written, cwd=REPO_ROOT)
        r = _run_shim("tlint.sh", payload)
        _record("D1 in-scope cwd=repo root -> still flags TS clash (stderr)",
                r.returncode == 0 and r.stderr.strip() != "", r)

        # D2: out-of-scope via cwd -> silent.
        payload = _post_tool_use_payload(written, cwd=OUT_OF_SCOPE_CWD)
        r = _run_shim("tlint.sh", payload)
        _record("D2 out-of-scope cwd (sibling repo) -> silent despite TS clash",
                r.returncode == 0 and r.stderr.strip() == "", r)

        # D3: out-of-scope via transcript_path slug (no cwd key).
        payload = _post_tool_use_payload(written, transcript_path=OOS_TP, cwd=None)
        r = _run_shim("tlint.sh", payload)
        _record("D3 out-of-scope transcript_path slug (no cwd key) -> silent",
                r.returncode == 0 and r.stderr.strip() == "", r)

        # D4: fail-open -- neither field usable -> still flags.
        payload = _post_tool_use_payload(written, transcript_path="", cwd=None)
        r = _run_shim("tlint.sh", payload)
        _record("D4 fail-open (neither field) -> STILL flags TS clash",
                r.returncode == 0 and r.stderr.strip() != "", r)


def section_dlint_hook():
    print("\n--- dlint_hook.py (PostToolUse hook, invoked via dlint_hook.sh -- MANDATORY case) ---")
    probe_abs = os.path.join(REPO_ROOT, PROBE_FILE_REL)
    if not os.path.isfile(probe_abs):
        _record("E* probe fixture missing -> %s" % probe_abs, False)
        return

    # E1: in-scope write of the REAL probe file -> STILL exit 2 (RED block),
    # genuinely unchanged from pre-guard behaviour. Uses the relative path +
    # subprocess cwd=REPO_ROOT, exactly mirroring the probe file's own
    # documented manual-invocation instructions.
    payload = _post_tool_use_payload(PROBE_FILE_REL, cwd=REPO_ROOT)
    r = _run_shim("dlint_hook.sh", payload)
    _record("E1 in-scope write of hook_probe_response_.md -> STILL exit 2 (RED block)",
            r.returncode == 2 and "RED" in r.stderr, r)

    # E2: out-of-scope via cwd -> exit 0 despite guaranteed RED content.
    payload = _post_tool_use_payload(PROBE_FILE_REL, cwd=OUT_OF_SCOPE_CWD)
    r = _run_shim("dlint_hook.sh", payload)
    _record("E2 out-of-scope cwd (sibling repo) -> exit 0 despite guaranteed RED content",
            r.returncode == 0 and r.stderr == "", r)

    # E3: out-of-scope via transcript_path slug (no cwd key).
    payload = _post_tool_use_payload(PROBE_FILE_REL, transcript_path=OOS_TP, cwd=None)
    r = _run_shim("dlint_hook.sh", payload)
    _record("E3 out-of-scope transcript_path slug (no cwd key) -> exit 0",
            r.returncode == 0 and r.stderr == "", r)

    # E4: fail-open -- neither field usable -> STILL blocks (exit 2), i.e.
    # fail-open preserves the blocking path too, not just the advisory one.
    payload = _post_tool_use_payload(PROBE_FILE_REL, transcript_path="", cwd=None)
    r = _run_shim("dlint_hook.sh", payload)
    _record("E4 fail-open (neither field) -> STILL exit 2 (RED block)",
            r.returncode == 2 and "RED" in r.stderr, r)


def main():
    section_clint()
    section_hlint()
    section_nlint()
    section_tlint()
    section_dlint_hook()

    passed = sum(1 for r in _RESULTS if r)
    total = len(_RESULTS)
    print("\n%d/%d passed" % (passed, total))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
