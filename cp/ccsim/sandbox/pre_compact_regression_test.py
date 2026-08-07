#!/usr/bin/env python3
"""Regression test —— the pre-compaction hook, the ONLY hook channel that can
reach the model across a compaction, and the two ways it could quietly die.

WHY THIS EXISTS (self-contained; no conversation or comms file explains it):

On 07/08/2026 a real auto-compaction fired and the model skipped root
CLAUDE.md §5 in full —— it obeyed the summary's own "Resume directly"
instruction. The PostCompact hook could never have prevented that: its registry
entry offers no model-facing channel at any exit code. PreCompact is different,
and the difference was extracted from the installed Desktop binary (2.1.221),
not from documentation. Its registry entry reads, verbatim:

    PreCompact: "Before conversation compaction.
        Exit code 0 - stdout appended as custom compact instructions
        Exit code 2 - block compaction
        Other exit codes - show stderr to user only but continue with compaction"

and the dispatch function in the same binary collects exit-0 stdout from every
non-blocked PreCompact hook, joins multiple hooks with blank lines, and returns
it as `newCustomInstructions`. The compaction pipeline merges that with any
user /compact argument (user text first, hook text second) and appends it to
the summarisation prompt under the literal heading "Additional Instructions:".
Both triggers ("auto" and "manual") take this path, including the background
precompute variant.

TWO HONEST LIMITS, so nobody reads this suite as proving more than it does:
  (a) The channel is ADVISORY twice over. The hook instructs the SUMMARISING
      model, which may comply, paraphrase, or drop the ask; and even a summary
      that carries the sentinel section is followed —— in the same message ——
      by the harness's hardcoded tail ("Resume directly ... as if the break
      never happened"; `suppressFollowUpQuestions` is hardcoded true on the
      reactive path). Root CLAUDE.md §5, delivered via the system prompt, stays
      the PRIMARY mechanism; the hook is an in-band second cue, nothing more.
  (b) No test here can force a real compaction. The suite pins the script, the
      registration, and the binary's channel; whether a live summary actually
      carries the section remains unverifiable until a real compaction runs.

THE ONE WAY THE HOOK COULD DO DAMAGE, pinned hardest below: exit code 2 BLOCKS
compaction. On an auto trigger a blocked compaction means the session cannot
shrink its context and dies at the hard ceiling. The script must exit 0 on
every input, including junk. Related: stdout must never START with "{" —— the
harness would then parse it as hook JSON, and a schema failure discards the
instructions entirely.

A note for whoever changes the script: do NOT parse the payload with a single
`read -r a b c`. Word-splitting tears `/Volumes/FURY 2TB/...` in two, the
guard classifies this repo as foreign, and the hook goes silent in the only
place it matters —— the defect that shipped in post_compact.sh's first draft.
"""

import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCRIPT = os.path.join(REPO, ".claude", "pre_compact.sh")
ROOT_CMD = os.path.join(REPO, "CLAUDE.md")
LIVE_LOG = os.path.join(REPO, "cscpt", ".pre_compact.log")
USER_SETTINGS = "/Volumes/FURY 2TB/.claude/settings.json"
SENTINEL = "🚨 Compaction Detected —— stopped all tasks."

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
    env["CCSIM_PRE_COMPACT_LOG"] = log_path
    p = subprocess.run(["bash", SCRIPT], input=payload, capture_output=True,
                       text=True, env=env)
    return p


# --- 1. The script itself ---------------------------------------------------

def test_script_present_and_executable():
    check("script missing", os.path.isfile(SCRIPT), SCRIPT)
    check("script not executable", os.access(SCRIPT, os.X_OK), SCRIPT)


def test_fires_in_repo_on_both_triggers_including_spaced_paths():
    # REPO genuinely contains a space on this Mac; assert that rather than
    # assume it, so the test still means something if the volume is renamed.
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, "pc.log")
        for trigger, cwd in (("auto", REPO),
                             ("manual", os.path.join(REPO, "cp", "ccsim"))):
            p = run_hook(json.dumps({"session_id": "pc-test-in",
                                     "cwd": cwd, "trigger": trigger,
                                     "custom_instructions": None}), log)
            check("silent inside the repo", p.stdout.strip() != "",
                  "%s @ %s" % (trigger, cwd))
            check("non-zero exit inside the repo", p.returncode == 0,
                  "%s -> %d" % (trigger, p.returncode))
        body = open(log).read() if os.path.exists(log) else ""
        check("no in-repo log line", "stage=fired_in_repo" in body, body[:120])
        check("trigger not logged", "trigger=auto" in body
              and "trigger=manual" in body,
              "the log must say WHICH trigger fired, or auto/manual "
              "diagnosis needs the transcript")
        if " " in REPO:
            check("spaced repo path was torn by word-splitting",
                  REPO in body,
                  "the guard must compare the WHOLE cwd, not its first field")
        else:
            skips.append("repo path has no space —— tearing check not exercised")


def test_silent_in_other_projects():
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, "pc.log")
        p = run_hook(json.dumps({"session_id": "pc-test-out",
                                 "cwd": "/tmp/elsewhere",
                                 "trigger": "auto"}), log)
        check("injected instructions into a FOREIGN project's summary",
              p.stdout.strip() == "", p.stdout[:80])
        check("bad exit in a foreign project", p.returncode == 0)
        body = open(log).read() if os.path.exists(log) else ""
        check("foreign-project skip not logged",
              "stage=skipped_other_repo" in body,
              "a skip must still leave a trace, or 'never ran' and 'ran and "
              "stood down' look identical")


def test_fails_open_never_silently():
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, "pc.log")
        for payload in ('{"session_id":"pc-test-noCwd"}', "not json at all", ""):
            p = run_hook(payload, log)
            check("stayed silent on an unreadable payload",
                  p.stdout.strip() != "", repr(payload[:30]))
        body = open(log).read() if os.path.exists(log) else ""
        check("fail-open path not logged", body.count("stage=fired_no_cwd") >= 3)


def test_never_exits_2_the_compaction_blocker():
    """Exit 2 blocks compaction; on auto that strands the session at the
    context ceiling. Every input shape must exit 0 —— junk included."""
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, "pc.log")
        shapes = (json.dumps({"cwd": REPO, "trigger": "auto"}),
                  json.dumps({"cwd": "/tmp/elsewhere", "trigger": "manual"}),
                  json.dumps({"trigger": "auto"}),
                  "not json", "", "{", "[]", "null",
                  json.dumps({"cwd": 42, "trigger": ["x"]}))
        for payload in shapes:
            p = run_hook(payload, log)
            check("EXIT 2 —— this BLOCKS compaction", p.returncode != 2,
                  repr(payload[:40]))
            check("non-zero exit", p.returncode == 0,
                  "%r -> %d" % (payload[:40], p.returncode))


def test_stdout_is_plain_text_never_json_shaped():
    """Stdout starting with '{' is parsed as hook JSON; a schema failure then
    discards the instructions. The text must stay unmistakably plain."""
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, "pc.log")
        p = run_hook(json.dumps({"cwd": REPO, "trigger": "auto",
                                 "session_id": "pc-test-shape"}), log)
        out = p.stdout.lstrip()
        check("stdout starts with '{' —— harness would JSON-parse it",
              not out.startswith("{"), out[:60])
        check("stdout starts with '[' —— same hazard, array form",
              not out.startswith("["), out[:60])


def test_instruction_content_carries_the_protocol():
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, "pc.log")
        p = run_hook(json.dumps({"cwd": REPO, "trigger": "auto",
                                 "session_id": "pc-test-content"}), log)
        out = p.stdout
        check("sentinel sentence missing or reworded", SENTINEL in out,
              "the summary must be able to carry §3.2.6's EXACT wording")
        check("does not ask for VERBATIM inclusion", "VERBATIM" in out,
              "a paraphrasable ask invites paraphrase; the whole point is the "
              "exact section surviving into the summary")
        check("does not name the <summary> block", "<summary>" in out,
              "text outside the block risks being stripped with <analysis>; "
              "content INSIDE <summary> is what the harness keeps")
        check("does not pre-void the harness tail",
              "resume directly" in out.lower(),
              "the summary is ALWAYS followed by the hardcoded 'Resume "
              "directly' wrapper; an instruction that does not name it "
              "re-fights the incident with one hand tied")
        check("does not cite root CLAUDE.md §5", "§5" in out,
              "the resuming model must be pointed at the PRIMARY mechanism, "
              "not handed a free-floating rule")
        check("instruction bloated", len(out) < 2500,
              "%d chars —— the longer the ask, the likelier the summariser "
              "truncates or paraphrases it" % len(out))


def test_script_source_hygiene():
    src = open(SCRIPT).read()
    check("script parses payload fields with a space-splitting `read`",
          not re.search(r'^\s*read\s+-r\s+\w+\s+\w+', src, re.M),
          "word-splitting tears `/Volumes/FURY 2TB/...`")
    check("script does not log", "CCSIM_PRE_COMPACT_LOG" in src)
    check("script cats root CLAUDE.md into the summariser prompt",
          not re.search(r'cat\s+["\']?[^\n]*CLAUDE\.md', src),
          "thousands of tokens of rules would distort the summary; the "
          "harness re-injects root CLAUDE.md by itself")
    # Scan executable text only —— the header COMMENTS rightly discuss exit 2
    # (they exist to warn about it), so comments must not trip this check.
    code_only = "\n".join(ln.split("#", 1)[0] for ln in src.splitlines())
    check("script hardcodes an exit 2 somewhere",
          not re.search(r'\bexit\s+2\b', code_only),
          "exit 2 blocks compaction —— there is no valid reason for this "
          "script ever to do that")


def test_live_log_untouched_by_this_suite():
    """Every run above pointed CCSIM_PRE_COMPACT_LOG at a fixture. If a test
    session id appears in the live log, the override is broken."""
    if not os.path.exists(LIVE_LOG):
        return  # nothing to contaminate
    body = open(LIVE_LOG).read()
    check("test wrote to the LIVE log —— env override broken",
          "pc-test-" not in body, LIVE_LOG)


# --- 2. The channel, pinned from the installed binary -----------------------

_BINARY_CACHE = {}


def harness_binary():
    """Locate the installed Desktop binary; fall back to npm installs.

    A hard-coded list of facts about the harness would certify a dead channel
    as healthy the day an update changes it —— the silent death this suite
    exists to catch. So the facts are re-read from the binary each run.
    """
    if "binary" in _BINARY_CACHE:
        return _BINARY_CACHE["binary"]
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
    for b in candidates:
        try:
            data = open(b, "rb").read()
        except Exception:
            continue
        if b"PreCompact" in data:
            _BINARY_CACHE["binary"] = b
            _BINARY_CACHE["data"] = data
            return b
    _BINARY_CACHE["binary"] = None
    return None


def test_precompact_channel_is_still_model_facing():
    """Pin the CHANNEL, not the version. If a future binary stops appending
    PreCompact stdout to the compact instructions, this hook joins PostCompact
    as a dead letter and this test is the only thing that will say so."""
    b = harness_binary()
    if not b:
        skips.append("harness binary not found —— PreCompact channel "
                     "reachability UNVERIFIED this run")
        return
    data = _BINARY_CACHE["data"]
    m = re.search(rb'PreCompact:\{summary:.{0,700}?\}', data, re.S)
    if not m:
        skips.append("PreCompact registry entry not found in %s —— extraction "
                     "may have broken; RE-DERIVE rather than trusting this pass"
                     % os.path.basename(b))
        return
    entry = m.group(0).decode("utf-8", "replace")
    check("registry no longer appends stdout as compact instructions",
          "stdout appended as custom compact instructions" in entry,
          entry[:200])
    check("registry no longer warns exit 2 blocks compaction",
          "block compaction" in entry, entry[:200])
    # The dispatch and its consumer, by their load-bearing strings. If either
    # vanishes, the mechanism has been rebuilt and must be re-derived.
    check("dispatch no longer returns newCustomInstructions",
          b"newCustomInstructions" in data,
          "the field the compaction pipeline consumes has been renamed")
    check("summariser prompt no longer has an Additional Instructions section",
          b"Additional Instructions:" in data,
          "the injection point inside the summarisation prompt has moved")
    # Contrast anchor —— PostCompact must still be user-only. If it gains a
    # model channel, prefer it (it fires AFTER the summary exists) and retire
    # the two-hop advisory path this hook depends on.
    m2 = re.search(rb'PostCompact:\{summary:.{0,600}?\}', data, re.S)
    if m2:
        e2 = m2.group(0).decode("utf-8", "replace")
        check("PostCompact gained a model channel —— GOOD NEWS, act on it",
              "additionalContext" not in e2 and "shown to Claude" not in e2,
              "a direct post-summary channel beats instructing the "
              "summariser; re-plan before trusting this suite's premises")


def test_registration_is_live_and_names_real_events():
    b = harness_binary()
    names = None
    if b:
        m = re.search(rb'\["PreToolUse","PostToolUse"[^\]]{20,2000}\]',
                      _BINARY_CACHE["data"])
        if m:
            try:
                parsed = json.loads(m.group(0).decode("utf-8"))
                if isinstance(parsed, list) and "PostToolUse" in parsed:
                    names = set(parsed)
            except Exception:
                pass
    if names is None:
        skips.append("harness event list not found —— registration validity "
                     "UNVERIFIED this run")
    for path in (USER_SETTINGS,
                 os.path.join(REPO, ".claude",
                              "hooks_user_settings.reference.json")):
        if not os.path.isfile(path):
            skips.append("settings file absent: %s" % path)
            continue
        try:
            hooks = (json.load(open(path)) or {}).get("hooks") or {}
        except Exception as exc:
            check("settings file does not parse", False, "%s: %s" % (path, exc))
            continue
        check("pre_compact.sh not registered in %s" % os.path.basename(path),
              any("pre_compact.sh" in json.dumps(v)
                  for k, v in hooks.items() if k == "PreCompact"),
              "the model-facing channel must stay wired, at USER level ——"
              " the Desktop app ignores project-level hooks")
        check("post_compact.sh dropped from %s" % os.path.basename(path),
              any("post_compact.sh" in json.dumps(v) for v in hooks.values()),
              "the user-facing alarm and its log are still wanted; the two "
              "hooks are complementary, not rivals")
        if names is not None:
            for event in hooks:
                check("registered event is not dispatched by this harness",
                      event in names, "%s in %s" % (event,
                                                    os.path.basename(path)))


# --- 3. Root §5 must NOT come to depend on this hook ------------------------

def test_root_protocol_remains_primary_and_hook_independent():
    """The hook is advisory twice over (summariser may drop it; the harness
    tail contradicts it). If §5 is ever rewritten to lean on PreCompact the
    way it once leant on PostCompact, the same failure is rebuilt one event
    earlier —— so pin §5's independence here, in the hook's own suite."""
    src = open(ROOT_CMD).read()
    m = re.search(r"^## 5\. Post-Compaction.*?(?=^## )", src, re.S | re.M)
    check("root CLAUDE.md has no §5", bool(m))
    if not m:
        return
    sec = m.group(0)
    check("§5 gates the sentinel on a hook firing",
          not re.search(r"[Ww]hen the Pre[Cc]ompact hook fires", sec),
          "PreCompact cannot guarantee delivery; a hook-gated §5 is a §5 "
          "that sometimes does not fire")
    check("§5 no longer keys on the observable summary",
          "summary" in sec.lower(),
          "§5.1 must key on what the model can actually see in-context")
    check("§5 no longer voids the 'resume directly' instruction",
          "resume directly" in sec.lower(),
          "that instruction is what the model obeyed in the incident, and "
          "the hook's injected text cites §5.1.3 for the void")


def main():
    test_script_present_and_executable()
    test_fires_in_repo_on_both_triggers_including_spaced_paths()
    test_silent_in_other_projects()
    test_fails_open_never_silently()
    test_never_exits_2_the_compaction_blocker()
    test_stdout_is_plain_text_never_json_shaped()
    test_instruction_content_carries_the_protocol()
    test_script_source_hygiene()
    test_live_log_untouched_by_this_suite()
    test_precompact_channel_is_still_model_facing()
    test_registration_is_live_and_names_real_events()
    test_root_protocol_remains_primary_and_hook_independent()

    for s in skips:
        print("SKIP —— %s" % s)
    if failures:
        print("FAIL —— %d problem(s):" % len(failures))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("PASS —— %d passed. Hook fires in-repo on both triggers (spaced "
          "paths intact), stays silent elsewhere, fails open, never exits 2, "
          "logs every invocation; stdout is plain text carrying the exact "
          "sentinel and the §5.1.3 void; channel re-verified against the "
          "installed binary; §5 remains observable-keyed and hook-independent."
          % passed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
