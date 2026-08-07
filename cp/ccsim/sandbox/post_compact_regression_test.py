#!/usr/bin/env python3
"""Regression test —— the post-compaction hook, and the class of failure that
made it useless for weeks without anyone being able to tell.

WHY THIS EXISTS (self-contained; no conversation or comms file explains it):

On 07/08/2026 a real auto-compaction fired for the first time in this project's
history. `.claude/post_compact.sh` was correctly registered on a REAL event
(`PostCompact` is genuine —— it appears in the harness's own hook registry as
"After conversation compaction"), the script was executable, and its repo guard
was sound. The model still skipped root CLAUDE.md §5 entirely: no `🚨` sentinel,
no halt, no context lists. It obeyed the compaction summary's own "Resume
directly" instruction instead.

The reason is a CHANNEL fact, not a wiring fact, and it is the thing this file
exists to stop anyone re-deriving the hard way:

    PostCompact's registry entry reads, verbatim:
        "Exit code 0 - stdout shown to user
         Other exit codes - show stderr to user only"

    Compare `Setup` ("Exit code 0 - JSON additionalContext shown to Claude") and
    `PostToolBatch` ("Return additionalContext via hookSpecificOutput to inject
    context"). Those two name a model-facing channel. PostCompact names none,
    at any exit code. It is the same shape as the Stop hook, which this repo
    already demoted `clint` over for exactly this reason.

    NET: a PostCompact hook can inform the USER and can leave a record. It can
    never instruct the MODEL. Anything that must reach the model after a
    compaction has to live in root CLAUDE.md, which the harness re-injects into
    the fresh context by itself.

So the checks below pin THREE separate things, because fixing only one leaves
the failure reachable by another route:

(1) THE SCRIPT behaves —— it fires inside this repo (including from a path
    containing spaces, which is every real path on this Mac), stays silent in
    other projects, fails OPEN rather than silently when the payload is
    unreadable, and LOGS every invocation. The log is the point: the 07/08
    investigation could not establish whether the hook had fired at all, and
    spent real effort on that question, because the script left no trace.

(2) THE REGISTRATION names an event the harness actually dispatches. This is
    checked against the INSTALLED BINARY'S OWN event list rather than a list
    written down here, because a hard-coded roster of valid event names is the
    same silent-death bug one level up: it would go stale the day Anthropic
    renames an event, and would then certify a dead hook as healthy. When the
    binary cannot be found or its list cannot be parsed, this check SKIPS
    LOUDLY —— never silently, and never by passing.

(3) ROOT CLAUDE.md §5 does not depend on the hook. §5.1 must key on something
    the model can observe in its own context, and must void the "resume
    directly" instruction in so many words.

A note for whoever changes the script: do NOT parse the payload with a single
`read -r a b c`. The first draft of the fix did, and word-splitting tore
`/Volumes/FURY 2TB/...` in two, so the guard classified this repo as a foreign
one and the hook went silent in the only place it matters. That is the same
defect that once broke `.githooks/pre-commit`'s `for f in $staged`.
"""

import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCRIPT = os.path.join(REPO, ".claude", "post_compact.sh")
ROOT_CMD = os.path.join(REPO, "CLAUDE.md")
USER_SETTINGS = "/Volumes/FURY 2TB/.claude/settings.json"

failures = []
skips = []
passed = 0


def check(label, condition, detail=""):
    global passed
    if condition:
        passed += 1
    else:
        failures.append("%s%s" % (label, (" —— " + detail) if detail else ""))


def run_hook(payload, log_path):
    env = dict(os.environ)
    env["CCSIM_POST_COMPACT_LOG"] = log_path
    p = subprocess.run(["bash", SCRIPT], input=payload, capture_output=True,
                       text=True, env=env)
    return p


# --- 1. The script itself ---------------------------------------------------

def test_script_present_and_executable():
    check("script missing", os.path.isfile(SCRIPT), SCRIPT)
    check("script not executable", os.access(SCRIPT, os.X_OK), SCRIPT)


def test_fires_in_repo_including_spaced_paths():
    # REPO genuinely contains a space on this Mac; assert that rather than
    # assume it, so the test still means something if the volume is renamed.
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, "pc.log")
        for cwd in (REPO, os.path.join(REPO, "cp", "ccsim")):
            p = run_hook(json.dumps({"session_id": "t", "cwd": cwd,
                                     "trigger": "auto"}), log)
            check("silent inside the repo", p.stdout.strip() != "", cwd)
            check("non-zero exit inside the repo", p.returncode == 0, cwd)
        body = open(log).read() if os.path.exists(log) else ""
        check("no in-repo log line", "stage=fired_in_repo" in body, body[:120])
        if " " in REPO:
            check("spaced repo path was torn by word-splitting",
                  REPO in body,
                  "the guard must compare the WHOLE cwd, not its first field")
        else:
            skips.append("repo path has no space —— tearing check not exercised")


def test_silent_in_other_projects():
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, "pc.log")
        p = run_hook(json.dumps({"session_id": "t", "cwd": "/tmp/elsewhere",
                                 "trigger": "manual"}), log)
        check("spoke in a foreign project", p.stdout.strip() == "", p.stdout[:80])
        check("bad exit in a foreign project", p.returncode == 0)
        body = open(log).read() if os.path.exists(log) else ""
        check("foreign-project skip not logged",
              "stage=skipped_other_repo" in body,
              "a skip must still leave a trace, or 'never ran' and 'ran and "
              "stood down' look identical")


def test_fails_open_never_silently():
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, "pc.log")
        for payload in ('{"session_id":"t"}', "not json at all", ""):
            p = run_hook(payload, log)
            check("stayed silent on an unreadable payload",
                  p.stdout.strip() != "", repr(payload[:30]))
        body = open(log).read() if os.path.exists(log) else ""
        check("fail-open path not logged", body.count("stage=fired_no_cwd") >= 3)


def test_emits_parseable_json_naming_its_own_event():
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, "pc.log")
        p = run_hook(json.dumps({"cwd": REPO, "trigger": "auto",
                                 "session_id": "t"}), log)
        last = [ln for ln in p.stdout.splitlines() if ln.strip()][-1]
        try:
            obj = json.loads(last)
        except Exception as exc:
            check("JSON block does not parse", False, str(exc))
            return
        check("no systemMessage (the one documented all-hooks user channel)",
              isinstance(obj.get("systemMessage"), str) and obj["systemMessage"])
        hso = obj.get("hookSpecificOutput") or {}
        check("hookSpecificOutput.hookEventName wrong",
              hso.get("hookEventName") == "PostCompact", str(hso.get("hookEventName")))
        ctx = hso.get("additionalContext") or ""
        check("additionalContext absent", bool(ctx))
        # 10k is the documented ceiling for injected context; stay far inside it.
        check("additionalContext implausibly large", len(ctx) < 8000, str(len(ctx)))


def test_does_not_dump_root_claude_md():
    src = open(SCRIPT).read()
    check("script still cats root CLAUDE.md",
          not re.search(r'cat\s+["\']?[^\n]*CLAUDE\.md', src),
          "it cannot reach the model and would flood the user; the harness "
          "re-injects root CLAUDE.md by itself")
    check("script parses payload fields with a space-splitting `read`",
          not re.search(r'^\s*read\s+-r\s+\w+\s+\w+', src, re.M),
          "word-splitting tears `/Volumes/FURY 2TB/...`")
    check("script does not log", "CCSIM_POST_COMPACT_LOG" in src)


# --- 2. The registration names a real event ---------------------------------

_BINARY_CACHE = {}


def harness_event_names():
    """Valid hook events, read from the INSTALLED binary rather than hard-coded.

    A list written down here would certify a dead hook as healthy the day an
    event is renamed —— the same silent death this suite exists to catch.

    Memoised: the binary is ~230MB and two checks need it, so an uncached second
    pass roughly doubles this suite's wall-clock for no gain.
    """
    if "names" in _BINARY_CACHE:
        return _BINARY_CACHE["names"], _BINARY_CACHE["binary"]
    candidates = []
    app = os.path.expanduser(
        "~/Library/Application Support/Claude/claude-code")
    if os.path.isdir(app):
        for v in sorted(os.listdir(app), reverse=True):
            b = os.path.join(app, v, "claude.app", "Contents", "MacOS", "claude")
            if os.path.isfile(b):
                candidates.append(b)
    for b in ("/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe",
              "/usr/local/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe"):
        if os.path.isfile(b):
            candidates.append(b)
    pat = re.compile(rb'\["PreToolUse","PostToolUse"[^\]]{20,2000}\]')
    for b in candidates:
        try:
            data = open(b, "rb").read()
        except Exception:
            continue
        m = pat.search(data)
        if not m:
            continue
        try:
            names = json.loads(m.group(0).decode("utf-8"))
        except Exception:
            continue
        if isinstance(names, list) and "PostToolUse" in names:
            _BINARY_CACHE["names"] = set(names)
            _BINARY_CACHE["binary"] = b
            _BINARY_CACHE["data"] = data
            return set(names), b
    _BINARY_CACHE["names"] = None
    _BINARY_CACHE["binary"] = None
    return None, None


def test_postcompact_channel_is_still_user_only():
    """Pin the CHANNEL, not just the event name.

    Name validation passes clean today and would have passed on the day of the
    incident —— `PostCompact` was always a real event. What failed is that its
    dispatch returns a user-display string and nothing else, so the hook's
    output is architecturally unable to reach the model. Root CLAUDE.md §5.1.6
    now states that as fact, and §5.1 is written to work without the hook.

    Pinning the harness VERSION would fail on every routine update and be muted
    within a fortnight. So this pins the BEHAVIOUR instead: assert the known
    state directly out of the running binary. If the day comes that PostCompact
    gains a model-facing channel, this fails —— which is the correct alarm, in
    the useful direction: it means §5.1.6 has gone stale and the hook can be
    re-armed to carry the protocol itself.
    """
    _, binary = harness_event_names()
    if not binary:
        skips.append("harness binary not found —— PostCompact channel "
                     "reachability UNVERIFIED this run")
        return
    data = _BINARY_CACHE.get("data")
    if data is None:
        skips.append("harness binary bytes unavailable —— channel UNVERIFIED")
        return
    m = re.search(rb'PostCompact:\{summary:.{0,600}?\}', data, re.S)
    if not m:
        skips.append("PostCompact registry entry not found in %s —— extraction "
                     "may have broken; RE-DERIVE rather than trusting this pass"
                     % os.path.basename(binary))
        return
    entry = m.group(0).decode("utf-8", "replace")
    check("PostCompact registry entry no longer says stdout goes to the user",
          "stdout shown to user" in entry, entry[:200])
    check("PostCompact now names a model-facing channel —— GOOD NEWS, act on it",
          "additionalContext" not in entry and "shown to Claude" not in entry,
          "root CLAUDE.md §5.1.6 says this event cannot reach the model. If "
          "that is no longer true, update §5.1.6 and consider letting the hook "
          "carry the protocol again. Entry: " + entry[:200])
    # Contrast anchors —— if these two stop naming a model channel, the
    # extraction is matching the wrong thing rather than the world changing.
    setup = re.search(rb'Setup:\{summary:.{0,600}?\}', data, re.S)
    if setup and b"shown to Claude" not in setup.group(0):
        skips.append("contrast anchor `Setup` no longer names a model channel "
                     "—— extraction suspect, re-derive before trusting")


def test_every_registered_event_is_real():
    names, binary = harness_event_names()
    if not names:
        skips.append("harness binary/event list not found —— registration "
                     "validity UNVERIFIED this run (checked the Desktop app "
                     "bundle and both npm prefixes)")
        return
    for path in (USER_SETTINGS,
                 os.path.join(REPO, ".claude", "hooks_user_settings.reference.json")):
        if not os.path.isfile(path):
            skips.append("settings file absent: %s" % path)
            continue
        try:
            hooks = (json.load(open(path)) or {}).get("hooks") or {}
        except Exception as exc:
            check("settings file does not parse", False, "%s: %s" % (path, exc))
            continue
        check("no hooks registered at all in %s" % os.path.basename(path),
              bool(hooks))
        for event in hooks:
            check("registered event is not dispatched by this harness",
                  event in names,
                  "%s in %s (valid: %s...)" %
                  (event, os.path.basename(path), sorted(names)[:6]))
        check("post_compact.sh no longer registered in %s"
              % os.path.basename(path),
              any("post_compact.sh" in json.dumps(v) for v in hooks.values()),
              "the compaction alarm must stay wired")
    globals()["_binary_used"] = binary


# --- 3. Root §5 does not depend on the hook ---------------------------------

def test_root_protocol_is_not_hook_gated():
    src = open(ROOT_CMD).read()
    m = re.search(r"^## 5\. Post-Compaction.*?(?=^## )", src, re.S | re.M)
    check("root CLAUDE.md has no §5", bool(m))
    if not m:
        return
    sec = m.group(0)
    check("§5.1 still gates the sentinel on the hook firing",
          not re.search(r"5\.1\..*[Ww]hen the PostCompact hook fires", sec),
          "PostCompact cannot reach the model; a hook-gated §5 is a §5 that "
          "does not fire")
    check("§5 names no observable trigger",
          "summary" in sec.lower(),
          "§5.1 must key on the compaction summary the model can actually see")
    check("§5 does not void the 'resume directly' instruction",
          "resume directly" in sec.lower(),
          "that instruction is what the model obeyed instead of §5")
    check("§5.5 still credits the hook with re-reading root CLAUDE.md",
          not re.search(r"already re-read via the PostCompact hook", sec),
          "the harness re-injects it; the hook never did")


def main():
    test_script_present_and_executable()
    test_fires_in_repo_including_spaced_paths()
    test_silent_in_other_projects()
    test_fails_open_never_silently()
    test_emits_parseable_json_naming_its_own_event()
    test_does_not_dump_root_claude_md()
    test_postcompact_channel_is_still_user_only()
    test_every_registered_event_is_real()
    test_root_protocol_is_not_hook_gated()

    for s in skips:
        print("SKIP —— %s" % s)
    if failures:
        print("FAIL —— %d problem(s):" % len(failures))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("PASS —— %d passed. Hook fires in-repo (spaced paths intact), stays "
          "silent elsewhere, fails open, logs every invocation, and emits a "
          "valid JSON block; every registered event name verified against the "
          "harness's own list%s; root §5 keys on the observable, not the hook."
          % (passed,
             " (%s)" % os.path.basename(globals().get("_binary_used") or "")
             if globals().get("_binary_used") else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
