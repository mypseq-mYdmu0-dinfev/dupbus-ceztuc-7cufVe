#!/usr/bin/env python3
"""Agent-In-Flight Linter (PreToolUse hook)

The TEA1 IN-FLIGHT GATE. It BLOCKS `git commit` / `git push` whilst any
sub-agent OR workflow dispatched by this session is still running, so root
CLAUDE.md §3.1.6's precondition ("After ALL tasks' completion, ensuring no SAs
in-flight, do Turn-End Actions") stops being a judgement call and becomes a
mechanical one.

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: a PreToolUse hook on `Bash`. It blocks a commit/push whilst a
  dispatched agent or workflow has not yet reported back; every other Bash
  call passes.
* IF IT BLOCKS: something is still running. WAIT for its completion
  notification, or `TaskStop` the id the message prints. The block names each
  outstanding one, its kind, and how long it has been quiet.
* IT NEVER BLOCKS: a sub-agent's own commits, another repo, or any non-git
  command. It warns instead of blocking when it cannot read the evidence.
* Verdicts log to `cscpt/.alint.log`, one line per invocation.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WHY A HOOK, NOT PROSE (the diagnosis this file is built on, recorded here
because the fix is meaningless without it): root CLAUDE.md §3.1.6 already
states the precondition in plain, unambiguous words, and it was still breached
at least four times across two sessions. The breaches were NOT a
comprehension failure and NOT a not-noticed failure: each time the rule was
read, understood, and consciously overridden by a judgement call along the
lines of "that agent will not matter" —— after which the agent returned with
substantive work, forcing a second commit or a corrected claim. Rewording,
bolding or relocating the rule therefore cannot help; only removing the
judgement can. Hence a mechanical gate at the MOMENT OF THE ACT.

THE SIGNAL, AND HOW IT WAS ESTABLISHED (all of it verified against this Mac's
real transcripts —— 368 historical agent dispatches and 40 workflow launches ——
not inferred):
* A dispatched agent's tool_result arrives WITHIN MILLISECONDS of dispatch and
  says `status: async_launched`. It is an ACKNOWLEDGEMENT, not a completion.
  Measured: every one of 368 dispatches had its tool_result inside ~200 ms of
  its tool_use. THIS IS THE TRAP that sinks the obvious design —— a ledger
  that adds on PreToolUse:Agent and removes on PostToolUse:Agent would never
  clear, and would block every commit forever.
* COMPLETION is a separate, later event: a `<task-notification>` carrying
  `<task-id>` and `<status>` (completed | killed | failed), injected into the
  main transcript. Of 368 historical dispatches, 363 have one; the 5 that do
  not are agents that never came to rest (see STALENESS RELEASE).
* Therefore: IN FLIGHT = launched (or resumed) more recently than it last came
  to rest. Both events live in the MAIN session transcript, which every hook
  payload hands over as `transcript_path` —— so an external process can answer
  the question with one file read and no harness cooperation.

ORDERING IS BY LINE POSITION, NOT TIMESTAMP: the transcript is append-ordered,
so "launched after it last rested" is just "later line index". That sidesteps
timestamp parsing, mixed record shapes, and clock skew entirely. Staleness (the
one place a real duration is needed) uses file mtimes instead, never the
transcript's own strings.

THE NOTIFICATION APPEARS IN THREE RECORD SHAPES and the parser must accept all
three, because which one lands first varies: `type:"attachment"` (queued, the
XML sitting in `attachment.prompt`), `type:"queue-operation"`, and
`type:"user"` (delivered, the XML as plain string content). Counted across this
Mac's history: 233 / 431 / 270 respectively. Hence the scan is a RAW SUBSTRING
test for `<task-notification>` on the line, then a regex for `<task-id>` ——
deliberately not a walk into one named field, which would have missed two
shapes out of three and silently under-reported completions.

WHAT COUNTS, AND WHAT DELIBERATELY DOES NOT. Two shapes are gated and one is
not, and each boundary was measured rather than assumed:
* An AGENT dispatch is exactly `toolUseResult.isAsync == true` carrying an
  `agentId`. Verified exclusive —— all 368 such records are Agent-tool
  dispatches.
* A WORKFLOW launch carries `taskId` AND `taskType` (plus `workflowName`,
  `runId`, `summary`, `transcriptDir`, `scriptPath`) and has NEITHER `isAsync`
  NOR `agentId`. All 40 historical launches carry exactly those eight keys.
  That absence is why the agent test could not see one.
* BOTH FIELDS ARE REQUIRED, and this is the trap in the obvious design: a bare
  `taskId` with no `taskType` appears on 111 further records —— 110 TodoWrite
  status changes (`taskId` is just `"2"`, `"3"`) and the Monitor sleep-loop's
  own timeout record. Keying on `taskId` alone would have made every todo tick
  an in-flight workflow and blocked every commit forever. Pinned by a test.
* BACKGROUND BASH uses `backgroundTaskId` and no `isAsync`, and is EXCLUDED ON
  PURPOSE —— load-bearing rather than an oversight: root CLAUDE.md §9.05
  mandates a persistent Monitor sleep-loop for timed wakes, which is a
  background bash command that stays alive by design for the whole session.
  Gating on it would block every commit of every session that used one —— the
  gate would be uninstalled within a day.

WHY A WORKFLOW MUST BE GATED SEPARATELY, rather than being covered by its
children: a workflow's child agents do NOT appear in the main session
transcript at all. Measured on run `wf_9704e270-7d9` (a 14-agent fan-out):
0 of its 14 children appear there as `isAsync` dispatches, and none of their
ids appears as a notification task-id —— they live only under the workflow's
own `transcriptDir`. So there is no double-counting to worry about, and more
importantly nothing else was ever watching them. Before this, a 14-agent
workflow in flight was worth exactly nothing to the gate and a TEA1 fired
mid-run sailed straight through.

A WORKFLOW RESTS BY THE SAME MECHANISM, which is what makes the gate one
mechanism and not two: its completion arrives as the very same
`<task-notification>`, carrying its `taskId` as the `<task-id>`. So the same
"launched at a later line than it last rested" rule decides it, and agents and
workflows share one `last_live`/`last_rest` pair. Their id namespaces are
disjoint in shape (`a` + 16 hex vs a short token like `wmi909npt`), so sharing
is correct rather than merely convenient. Historically 40 of 40 workflow
launches have a later notification —— a better rate than agents' 363 of 368.

RESUMPTION: `SendMessage` to a rested agent restarts it ("had no active task;
resumed from transcript in the background"), and it will notify again. Any
successful tool result naming a known agent id therefore counts as a fresh
liveness event at that line. This is deliberately generous —— the other
SendMessage outcome ("Message queued for delivery ... at its next tool round")
names an agent that was already live, so treating both alike costs nothing and
missing the resume case would let a revived agent slip past the gate.

STALENESS RELEASE (why the gate cannot brick a repo): an agent killed by an app
quit, a session limit, or a crash may never emit its notification —— 5 of 368
historically. Left alone that would block committing FOREVER, which is a worse
defect than the one being fixed. So a launch whose output file has not been
touched for `_STALE_S` is RELEASED: the gate passes, but says so loudly in a
model-visible note naming the agent. Release is never silent, because a silent
release is indistinguishable from a gate that never ran.
* THE WORKFLOW CLOCK IS A DIRECTORY, not a file, and that is what kept this
  case unsolved when the gate was first built: a workflow launch exposes a
  `transcriptDir` and no `outputFile`, so there is no single mtime to read.
  The answer is the NEWEST mtime across that directory AND its entries. It is
  a sound liveness signal —— arguably sounder than the agent case, because it
  aggregates `journal.jsonl` (a line as each child starts and as each returns)
  with every child's own `agent-*.jsonl` (a write on every tool call any child
  makes), so any activity anywhere in the fleet advances it, whereas an agent
  rests on one file alone.
* Reading the ENTRIES rather than the directory alone is load-bearing, not
  belt-and-braces: appending to a file does NOT update its parent directory's
  mtime, so a directory-only clock would have called a furiously busy 14-agent
  workflow stale and released it. A test pins exactly that (a 3-hour-old
  directory with fresh children must stay LIVE).
* Honest limit: the scan is ONE level deep, which matched the real layout
  exactly (29 entries, no subdirectories). A future harness that nested deeper
  would age a workflow optimistically —— i.e. release it early, with the loud
  notice, never block it silently. That is the recoverable direction.
* The threshold is generous on purpose. The FAST path out of a stuck agent or
  workflow is `TaskStop`, which emits a `killed` notification and clears the
  gate at once —— the block message says so, and for a workflow the id to pass
  is its task id. Staleness is only the last-resort automatic release for the
  case where nobody is watching.
* An agent killed by a usage limit SHOULD block: root CLAUDE.md §9.02.4 is
  explicit that its task is not done and must be re-dispatched or redone. The
  gate holding the commit in that case is correct behaviour, not a false
  positive.

FAIL DIRECTION —— OPEN, BUT NEVER SILENTLY (the deliberate call, argued rather
than defaulted). Every other lint in `cscpt/` fails open, and this one does too
whenever it cannot READ the evidence, for three reasons:
1. A closed failure has no recovery path the agent can act on. It cannot make
   an unreadable transcript readable, so a payload-shape change —— and payload
   shapes are harness-owned and change without notice —— would permanently
   brick `git commit` on this Mac, with no error message pointing at the cause.
   That is exactly the class of silent, undiagnosable wiring failure
   `cp/ccsim/hook_guide.md` §2 exists to prevent.
2. The asymmetry favours open. A premature commit is recoverable (amend, or a
   second commit). A permanently blocked commit is not recoverable without
   hand-editing a settings file outside the repo.
3. Failing open here does NOT restore the defect, and this is the whole point:
   the four documented breaches all happened on the ONE path where the evidence
   was perfectly readable and agents were demonstrably live. On that path this
   file is hard-closed and no judgement can reopen it. Fail-open only covers
   paths the breaches never took.
The price is paid in VISIBILITY: every fail-open branch emits a model-visible
note AND a log line naming the stage reached, so "the gate went dark" can never
be mistaken for "the gate ran and found nothing" —— the distinction whose
absence let dead hook wiring survive for weeks (hook_guide § 7.7).

SUB-AGENT EXEMPTION: TEA1 belongs to the MAIN agent, and a sub-agent commits
its own work routinely (`cp/ccsim/CLAUDE.md` §5.3 positively requires it before
deleting from `sandbox/`), so blocking a sub-agent's commit would be a fresh
defect. The discriminator is the payload's `agent_id` field, and it was
established by CAPTURING REAL PAYLOADS rather than by reasoning:
* Sub-agent calls carry `agent_id` + `agent_type`; main-agent calls carry
  neither. Confirmed across 8 live PreToolUse payloads spanning two different
  concurrent sub-agents and the main agent, with no exception.
* THE OBVIOUS DESIGN WAS WRONG, and only the capture caught it. A sub-agent's
  transcript RECORDS live under `.../subagents/agent-<id>.jsonl` and never
  appear in the main session file (also verified), so "the payload's
  transcript_path will point there" looks certain —— and is false. Every
  sub-agent payload hands over the MAIN session transcript. Shipping the
  path-based test alone would have blocked every sub-agent commit whilst any
  sibling ran, i.e. exactly the fresh defect this exemption exists to avoid.
  Recorded because the reasoning was persuasive and still wrong.

TRIGGER MATCHING —— WHY A TOKEN WALK AND NOT A REGEX: the command must be
recognised as "git is being asked to commit or push", not merely "the string
git commit appears somewhere". A naive search flags `git log --grep=commit` and
`echo "git commit"`. So the command is split on shell separators (`;`, `&&`,
`||`, `|`, newline, and the openers of `$(` / backtick substitutions), and each
segment must START with `git` (after leading `VAR=value` assignments and an
optional path prefix such as `/usr/bin/git`), after which global options are
skipped and the first remaining token must be `commit` or `push`.
* Accepted deliberately: `git -C /path commit`, `cd x && git add -A && git
  commit -m ...`, `git push origin main`.
* Rejected deliberately: `git log --grep=commit`, `echo git push`, `man
  git-commit`, `xargs git commit` (a segment not starting with git).
* `xargs git commit` is a known, accepted miss. Recognising it would mean
  flagging any segment merely CONTAINING the words, which is precisely the
  false-positive class this walk exists to remove, and a false BLOCK on a
  blocking hook costs far more than a missed exotic invocation.

WHY THE `.sh` SHIM: the matcher is tool-name-only, so this fires on EVERY Bash
call —— by far the most frequent tool. `alint_hook.sh` exits instantly unless
the payload mentions `git`, sparing a Python start on the common call. The
rigorous checks stay HERE; the shim's substring test only decides whether
Python is worth spawning. Naming follows the folder rule: every `.sh` in
`cscpt/` carries `_hook` and is the file settings.json invokes; no `.py` does.

REPO SCOPE: user-level registration reaches every project on this Mac and this
lint BLOCKS, so per hook_guide § 4.7 it must be repo-scoped. Signals in order:
payload `cwd`, else the `~/.claude/projects/<slug>/` transcript slug, both
derived from this file's OWN location so the repo stays relocatable. Neither
usable -> FAIL OPEN (run the check), per hook_guide § 4.3.3 and § 8.6.5: a
scope guard that fails closed silently disables a lint, and the check itself
then fails open again if it cannot read the transcript, so the combined
behaviour is still "warn, never brick".

BREAK GLASS: `ALINT_OFF=1` in the environment disables the gate for that
process. It is deliberately an ENVIRONMENT variable and not a file flag or a
prompt token: a hook runs as a child of the harness, so it inherits the
environment the USER launched the app with, and nothing the agent types into
its own Bash call can reach it. Every disabled invocation still emits a
model-visible note and a log line, so an unnoticed permanent disable is not
possible.

WIRING (kept here, not in NON-CCSIM: a caller never invokes this file).
Registered as a `PreToolUse` hook with matcher `Bash` in the USER-level
`~/.claude/settings.json` —— the Claude Desktop app executes user-level hooks
and silently ignores project-level ones. IN: PreToolUse JSON on stdin
(`tool_input.command`, `transcript_path`, `cwd`, `session_id`). OUT: exit 2
with the reason on STDERR to BLOCK (the only PreToolUse channel that both
reaches the model and stops the call); otherwise exit 0, optionally with
`hookSpecificOutput.additionalContext` for a model-visible warning.
⚠️ REGISTRATION CHANGES TAKE MINUTES TO GO LIVE —— measured, and the reason a
"the hook did not fire" test can lie. A new entry added to
`~/.claude/settings.json` did not fire when tested twice within a few minutes,
and then fired unaided ~15 minutes later, in the SAME session, whilst the other
registered hooks ran normally throughout. So the app DOES re-read that file
without a restart, just not promptly. Two consequences worth more than the
observation itself:
* An early "it did not fire" proves nothing. Wait, retest, and only then
  conclude the wiring is dead (hook_guide § 8's signature still applies, but
  only after the delay has passed).
* A registration whose command file is MISSING does NOT fail silently at
  PreToolUse: the harness reports a hook error and BLOCKS the tool call
  outright. Observed live —— deleting a still-registered script made every
  Bash call fail until the file was restored. Delete the FILE only after the
  live settings no longer name it, never the other way round.

LOG EVERY STAGE (hook_guide § 7.7): one tab-delimited line per invocation to
`cscpt/.alint.log`, whatever the verdict, because a breach-only log cannot tell
"ran and found nothing" from "never invoked". Actions: `no_stdin`, `probe`,
`not_git` (a git-ish command that is not a commit/push —— the shim absorbs
everything else), `out_of_scope`, `subagent`, `disabled`, `no_transcript`,
`unreadable_transcript`, `clear`, `stale_release`, `block`. `ALINT_LOG=<path>`
redirects it so a test neither reads nor pollutes the real log.
The `note=` field tags each named item by kind: a bare id is an AGENT, `wf:<id>`
a workflow, and `wf?:<id>` a workflow whose `transcriptDir` could not be read at
all. `wf?` is the named stage for that one new unreadable path —— such a
workflow is held LIVE on NO liveness evidence (the conservative per-item
direction, matching an agent with no output file), and without its own tag it
would be indistinguishable in the log from one held live on good evidence.

LIVE TEST (hook_guide § 7.3's row for this hook): run `echo ALINT_PROBE`
through the real Bash tool. A reply saying the gate is ALIVE, plus a new
`action=probe` line in the log, means the harness invoked this file unaided.
Silence means the wiring is dead —— go to hook_guide § 8. The probe also logs
`note=<transcript filename>`, which is how the SUB-AGENT EXEMPTION assumption
above gets settled: run it once from the main agent and once from a sub-agent
and compare (`<uuid>.jsonl` vs `agent-<id>.jsonl`).
"""

import sys
import io
import select
import stat
import os
import re
import json
import time
from datetime import datetime

# ---------------------------------------------------------------------------
# SCOPE GUARD —— user-level registration fires in EVERY project on this Mac, so
# self-scope. Both signals derive from this file's OWN location, never a
# hard-coded path. FAILS OPEN (run the check) when neither is usable; see the
# module docstring (REPO SCOPE) for why open is the only safe direction here.
# ---------------------------------------------------------------------------
_REPO_ROOT_REAL = os.path.realpath(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_REPO_SLUG = re.sub(r"[/ ]", "-", _REPO_ROOT_REAL.rstrip("/"))

# An agent id as the harness mints it: `a` + 16 hex. Verified against 368
# historical dispatches —— every one matched. Used to spot an id inside a
# free-text tool result (the SendMessage resume case), where no structured
# field carries it.
_AGENT_ID_RE = re.compile(r"\ba[0-9a-f]{16}\b")

# The completion record. Matched as a RAW SUBSTRING first because the XML
# arrives in three different record shapes (docstring: THREE RECORD SHAPES).
_NOTIF_TOKEN = "<task-notification>"
_TASK_ID_RE = re.compile(r"<task-id>([^<]{1,64})</task-id>")
_STATUS_RE = re.compile(r"<status>([^<]{1,32})</status>")

# How long an agent's output file may go untouched before the gate RELEASES it
# rather than blocking forever (docstring: STALENESS RELEASE). Generous on
# purpose: `TaskStop` is the fast, deliberate way out, and this is only the
# unattended last resort.
_STALE_S = 45 * 60

# Liveness-probe token. Running `echo ALINT_PROBE` through the real Bash tool
# makes this file answer, which is the only cheap way to prove the WIRING
# without performing a real commit (hook_guide § 7.1: piping a payload in by
# hand tests the SCRIPT and says nothing about the harness).
_PROBE_TOKEN = "ALINT_PROBE"

# Bound the transcript read. A session file runs to a few MB; this is a
# backstop against a pathological one turning a Bash call into a long pause.
_MAX_TRANSCRIPT_BYTES = 64 * 1024 * 1024

# Bound the workflow-directory scan. A real `transcriptDir` held 29 entries
# (`journal.jsonl` plus two files per child agent); this is a backstop only.
_MAX_DIR_ENTRIES = 2000

# Git global options that may sit between `git` and its subcommand. Ones that
# take a SEPARATE value argument are listed apart, so the value is skipped too
# and `git -C commit` cannot be misread as the commit subcommand.
_GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace",
                        "--exec-path", "--config-env"}
_TRIGGER_SUBCOMMANDS = {"commit", "push"}

# Shell separators that start a NEW command segment. Longest first, so `&&` is
# consumed before `&` and `||` before `|`.
_SEGMENT_SPLIT_RE = re.compile(r"&&|\|\||[;&|\n\r]|\$\(|`|\{|\}|\(|\)")

# Log path (overridable for tests via ALINT_LOG); default beside this script.
_LOG = os.environ.get("ALINT_LOG") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".alint.log")

# --- Log retention. Same shape and rationale as clint's: one line per
# invocation forever is unbounded growth in a file nobody deletes, and the log
# only ever answers a question about a recent session. Hysteresis bounds the
# rewrite to at most one invocation in 200.
_LOG_MAX_LINES = 1000
_LOG_KEEP_LINES = 800
_LOG_MIN_BYTES_PER_LINE = 50
_LOG_PRUNE_AT_BYTES = _LOG_MAX_LINES * _LOG_MIN_BYTES_PER_LINE


def _in_scope(data):
    """True if this invocation belongs to this repo. FAILS OPEN —— an
    unreadable payload is not evidence of a different project, and a scope
    guard that fails closed silently disables a lint (hook_guide § 8.6.5).
    Never raises."""
    try:
        if not isinstance(data, dict):
            return True
        cwd = data.get("cwd")
        if isinstance(cwd, str) and cwd:
            real = os.path.realpath(cwd)
            return real == _REPO_ROOT_REAL or real.startswith(
                _REPO_ROOT_REAL + os.sep)
        tp = data.get("transcript_path")
        if isinstance(tp, str) and tp:
            m = re.search(r"/projects/([^/]+)/", tp)
            if m:
                slug = m.group(1)
                return slug == _REPO_SLUG or slug.startswith(_REPO_SLUG + "-")
        return True
    except Exception:
        return True


def _is_subagent(data):
    """True if this Bash call comes from a SUB-agent rather than the main one.

    PRIMARY SIGNAL, live-verified: the payload carries `agent_id` (and
    `agent_type`) on a sub-agent's call and carries neither on the main
    agent's. Captured across 8 real PreToolUse payloads from two different
    concurrent sub-agents plus the main agent, with no exception.

    The `transcript_path` test below is a SECOND, currently-inert signal, kept
    deliberately: a sub-agent's payload hands over the MAIN session transcript,
    not its own, so this branch never fires today —— but a sub-agent's records
    do live under `.../subagents/`, so a future harness that pointed the
    payload there would otherwise silently turn every sub-agent into a main
    agent. Cheap insurance in the safe direction.

    TEA1 is the MAIN agent's action and a sub-agent commits its own work
    routinely, so a sub-agent call is exempt (docstring: SUB-AGENT
    EXEMPTION)."""
    try:
        for key in ("agent_id", "agentId"):
            val = data.get(key)
            if isinstance(val, str) and val.strip():
                return True
        tp = data.get("transcript_path")
        if isinstance(tp, str) and "/subagents/" in tp.replace("\\", "/"):
            return True
    except Exception:
        pass
    return False


def tp_basename(data):
    """The payload's transcript filename alone (never the full path, which
    would put a user directory into a committed-adjacent log). Logged on a
    probe so one line shows whether the harness hands this call the MAIN
    session file or a sub-agent's —— the single question `_is_subagent` rests
    on and that no in-session experiment could settle."""
    try:
        tp = data.get("transcript_path")
        if isinstance(tp, str) and tp:
            return os.path.basename(tp.replace("\\", "/"))
    except Exception:
        pass
    return "-"


def _strip_quotes(tok):
    """Drop matched surrounding quotes from a token, so `'git'` reads as git."""
    if len(tok) >= 2 and tok[0] == tok[-1] and tok[0] in ("'", '"'):
        return tok[1:-1]
    return tok


def _segment_triggers(seg):
    """True if ONE command segment is a git commit/push invocation.

    The segment must START with git (after any `VAR=value` assignments and an
    optional directory prefix), after which git's own global options are
    skipped —— including the value of those that take one —— and the first
    remaining token must be `commit` or `push`. Rationale, and the accepted
    misses, are in the module docstring (TRIGGER MATCHING)."""
    toks = [_strip_quotes(t) for t in seg.split() if t]
    i = 0
    # Leading environment assignments: `GIT_DIR=x git commit`.
    while i < len(toks) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[i]):
        i += 1
    if i >= len(toks):
        return False
    head = toks[i].rsplit("/", 1)[-1]           # `/usr/bin/git` -> `git`
    if head != "git":
        return False
    i += 1
    while i < len(toks):
        t = toks[i]
        if not t.startswith("-"):
            return t in _TRIGGER_SUBCOMMANDS
        # `--git-dir=x` carries its value inline; `-C x` does not.
        base = t.split("=", 1)[0]
        i += 1
        if base in _GIT_OPTS_WITH_VALUE and "=" not in t:
            i += 1                               # skip the separate value
    return False


def _is_tea1(command):
    """True if this Bash command performs TEA1 (a git commit or push) in any of
    its segments. Never raises —— an unparseable command is simply not a
    trigger, which keeps a malformed payload from blocking anything."""
    try:
        if not isinstance(command, str) or "git" not in command:
            return False
        for seg in _SEGMENT_SPLIT_RE.split(command):
            if seg and _segment_triggers(seg):
                return True
    except Exception:
        pass
    return False


def _dir_quiet_seconds(dir_path):
    """Seconds since ANYTHING in a workflow's `transcriptDir` was last touched,
    or None when that cannot be read.

    This is the workflow counterpart of `_quiet_seconds`, and it must look at
    the ENTRIES, not just the directory: appending to a file does not update
    its parent directory's mtime, so a directory-only clock would read a
    furiously busy 14-agent workflow as untouched and release it. The entries
    are what move —— `journal.jsonl` gains a line as each child starts and
    returns, and every child's own `agent-*.jsonl` grows on every tool call it
    makes.

    Scanned one level deep, which matched the real layout exactly (29 entries,
    no subdirectories). A subdirectory's own mtime is still included, so deeper
    nesting introduced by a future harness would age OPTIMISTICALLY —— it could
    release early, which is the loud, recoverable direction, never a silent
    block. None means "cannot age this one", and the caller then treats the
    workflow as LIVE (docstring: STALENESS RELEASE). Never raises."""
    try:
        if not dir_path:
            return None
        newest = os.path.getmtime(dir_path)
        with os.scandir(dir_path) as entries:
            for n, entry in enumerate(entries):
                if n >= _MAX_DIR_ENTRIES:
                    break
                try:
                    mtime = entry.stat(follow_symlinks=False).st_mtime
                except OSError:
                    continue
                if mtime > newest:
                    newest = mtime
        return max(0.0, time.time() - newest)
    except Exception:
        return None


def _scan_transcript(path):
    """Walk the MAIN session transcript once and return
    `(launches, last_live, last_rest, workflows)`.

    * `launches[agent_id]` -> `{"desc":…, "out":…}` from the dispatch record.
    * `workflows[task_id]` -> `{"desc":…, "dir":…}` from the workflow launch.
    * `last_live[id]` -> line index of its most recent dispatch OR resume.
    * `last_rest[id]` -> line index of its most recent completion notification.

    Agents and workflows SHARE `last_live`/`last_rest` because the harness
    already shares the notification: a workflow rests via the very same
    `<task-notification>`, carrying its `taskId` as the `<task-id>`. Their id
    namespaces are disjoint in shape (`a` + 16 hex vs a short token), so one
    pair of dicts is correct rather than merely convenient.

    Ordering is by LINE INDEX, never by timestamp (docstring: ORDERING IS BY
    LINE POSITION). Sub-agent lines are skipped so an agent's own internal
    chatter can never be mistaken for a main-session event. Raises only on an
    unreadable file; malformed individual lines are skipped."""
    launches, last_live, last_rest, workflows = {}, {}, {}, {}
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        read = 0
        for idx, raw in enumerate(fh):
            read += len(raw)
            if read > _MAX_TRANSCRIPT_BYTES:
                break
            raw = raw.strip()
            if not raw:
                continue
            # Cheap pre-filter: only two kinds of line can matter, and a
            # session transcript is mostly neither.
            has_notif = _NOTIF_TOKEN in raw
            if not has_notif and '"toolUseResult"' not in raw:
                continue
            try:
                obj = json.loads(raw)
            except Exception:
                continue
            if not isinstance(obj, dict) or obj.get("isSidechain") is True:
                continue
            if has_notif:
                m = _TASK_ID_RE.search(raw)
                if m:
                    last_rest[m.group(1)] = idx
            tur = obj.get("toolUseResult")
            if not isinstance(tur, dict):
                continue
            aid = tur.get("agentId")
            if tur.get("isAsync") and isinstance(aid, str) and aid:
                launches[aid] = {
                    "desc": str(tur.get("description") or "")[:70],
                    "out": tur.get("outputFile")
                            if isinstance(tur.get("outputFile"), str) else None,
                }
                last_live[aid] = idx
                continue
            # WORKFLOW launch. BOTH `taskId` and `taskType` are required, and
            # that pairing is the whole discriminator: a bare `taskId` also
            # appears on every TodoWrite status change and on the Monitor
            # sleep-loop's own record (111 such records historically, none of
            # them a workflow), so keying on it alone would block every commit
            # of every session that ticked a todo.
            tid = tur.get("taskId")
            if (isinstance(tid, str) and tid and tur.get("taskType")
                    and not tur.get("isAsync")):
                tdir = tur.get("transcriptDir")
                workflows[tid] = {
                    "desc": str(tur.get("workflowName")
                                or tur.get("summary") or "")[:70],
                    "dir": tdir if isinstance(tdir, str) else None,
                }
                last_live[tid] = idx
                continue
            # RESUMPTION: a successful tool result naming a known agent id
            # restarts it (docstring: RESUMPTION). Deliberately generous.
            if tur.get("success") is True:
                blob = json.dumps(tur)[:4000]
                for found in set(_AGENT_ID_RE.findall(blob)):
                    if found in launches:
                        last_live[found] = idx
    return launches, last_live, last_rest, workflows


def _quiet_seconds(out_path):
    """Seconds since the agent's output file was last touched, or None when
    that cannot be read. The output file is the agent's own transcript (via a
    symlink), so it advances on every tool call the agent makes —— which is
    what makes it a usable liveness clock. None means "cannot age this one",
    and the caller then treats the agent as LIVE, which is the conservative
    direction for a single agent whilst the whole-gate failure paths stay
    fail-open."""
    try:
        if not out_path:
            return None
        return max(0.0, time.time() - os.path.getmtime(out_path))
    except Exception:
        return None


def _prune_log():
    """Bound `_LOG` to its recent window —— cheaply, atomically, fail-safely.
    Runs AFTER the current line is on disk, so this invocation's own record can
    never be pruned away by its own call. One `os.stat` on almost every
    invocation; a read only when the file could exceed the high-water mark, and
    a rewrite only when it does. The tail is staged in a pid-suffixed sibling
    and moved with `os.replace` (one atomic rename), so a crash leaves either
    the original or the complete replacement, never a half file. Every failure
    is swallowed: pruning is housekeeping, and raising from here would break a
    tool call, which this file's contract forbids."""
    tmp = None
    try:
        if os.stat(_LOG).st_size < _LOG_PRUNE_AT_BYTES:
            return
        with open(_LOG, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
        if len(lines) <= _LOG_MAX_LINES:
            return
        tmp = "%s.tmp.%d" % (_LOG, os.getpid())
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines[-_LOG_KEEP_LINES:]) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, _LOG)
        tmp = None
    except Exception:
        pass
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except Exception:
                pass


def _log(sid, action, live=0, sub="-", note="-"):
    """Append ONE diagnostic line for ANY invocation, verdict or not
    (hook_guide § 7.7 —— a breach-only log cannot distinguish "ran and found
    nothing" from "never invoked"). `sub=` records the sub-agent verdict on
    every call, which is what settles the one unproven assumption in the
    docstring. `note=` stays LAST because it alone carries free text. Swallows
    every error: a logging failure must never break a tool call."""
    try:
        with open(_LOG, "a", encoding="utf-8") as fh:
            fh.write("%s\tsession=%s\taction=%s\tlive=%d\tsub=%s\tnote=%s\n"
                     % (datetime.now().isoformat(timespec="seconds"),
                        sid, action, live, sub,
                        str(note)[:220].replace("\t", " ").replace("\n", " ")))
    except Exception:
        pass
    _prune_log()


def _tag(entry):
    """One log token for a live/released item: a bare agent id, `wf:<id>` for a
    workflow, or `wf?:<id>` for a workflow whose transcript directory could not
    be aged at all. The `wf?` form is the named stage for that unreadable path
    —— without it a workflow held live on NO liveness evidence would look
    identical in the log to one held live on good evidence, which is exactly
    the "ran and found nothing" vs "went dark" confusion hook_guide § 7.7
    exists to prevent."""
    kind, key, _desc, quiet = entry
    if kind != "workflow":
        return key
    return ("wf?:%s" % key) if quiet is None else ("wf:%s" % key)


def _advise(text):
    """Emit a model-visible, NON-blocking note. On PreToolUse the structured
    `additionalContext` field is the one channel that is both non-blocking and
    read by the model (hook_guide § 6.5), which is what makes every fail-open
    branch of this file audible rather than silent."""
    try:
        sys.stdout.write(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": text,
            }
        }))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# HOOK-BODY STDIN GUARD
# ---------------------------------------------------------------------------
# This file is a HOOK BODY, not a command-line tool: the harness pipes its JSON
# payload on stdin and closes it, and argv carries a mode word at most, never a
# file to check. Run by hand as `python3 <this> some_file.md`, the payload read
# in main() used to block FOREVER —— on a terminal, and equally on any pipe a
# caller holds open without writing (a background runner, an agent shell). That
# is far worse than merely slow: silence from a hang is indistinguishable from
# silence from a clean pass, so the hand run gets filed as a verification that
# never happened. It has already cost this repo one file recorded as
# "lint clean" when nothing had run at all.
#
# So refuse: fast, on stderr, non-zero, naming the correct incantation. A quiet
# `exit 0` would trade the hang for that same false pass in a new hat, which is
# why this path must never return success.
#
# Under the harness the payload is written and stdin closed before this runs,
# so `select` reports it readable at once and the guard costs nothing on the
# real path. The wait exists only for the caller holding an empty pipe open ——
# far longer than a local payload write, far shorter than a lost session.
#
# READINESS IS NOT ARRIVAL, and getting that wrong recreated the whole defect.
# `/dev/null`, a closed descriptor and a pipe already at EOF are all READY: a
# read on them returns immediately, with nothing. An agent shell hands its
# children `/dev/null`, so `python3 <this> some_file.md` there sailed past a
# readiness-only guard, read zero bytes, failed to parse them, and exited 0 in
# silence —— the SAME false pass as the hang, reached by a shorter route. So
# three things are checked, not one: argv that no hook ever passes, stdin that
# never becomes readable, and stdin that is readable but delivers nothing.
#
# RESIDUAL, stated rather than papered over: a caller that writes a PARTIAL
# payload and then holds the pipe open still blocks in the read below, exactly
# as it did before any of this existed. Closing that needs a deadline around
# the read, which buys nothing on the harness path (it always closes stdin)
# and adds moving parts to a gate that BLOCKS writes.
_HOOK_STDIN_WAIT_S = 2.0

# Extensions a caller reaches for when treating this file as a CLI. A hook mode
# word never carries one, so this cannot collide with `pre`/`post`, nor with
# the junk argv flint deliberately tolerates (pinned by its own suite, M5).
_HOOK_FILEY_EXTS = frozenset((".md", ".py", ".sh", ".json", ".jsonl", ".txt",
                              ".html", ".yml", ".yaml", ".csv"))


def _argv_names_a_file(arg):
    """True when this argument is a caller handing over a file to check."""
    return ("/" in arg or "\\" in arg
            or os.path.splitext(arg)[1].lower() in _HOOK_FILEY_EXTS)


def _hook_stdin_is_pipe():
    """True when stdin is the pipe or socket a harness hands a hook body.

    An EMPTY payload means opposite things on either side of this line. Over a
    PIPE it means the harness sent nothing, and every lint here fails OPEN on
    that by a contract its own suite pins —— a lint may never break a turn.
    Over `/dev/null`, a closed descriptor, a terminal or a plain file it means
    no payload was ever coming, which is a hand invocation and must never be
    allowed to read as a pass. Unknowable shapes count as a pipe, so an odd
    environment can only ever fail towards leaving the lint armed.
    """
    try:
        mode = os.fstat(sys.stdin.fileno()).st_mode
        return stat.S_ISFIFO(mode) or stat.S_ISSOCK(mode)
    except Exception:
        return True


_HOOK_STDIN_HOWTO = (
    '  printf \'%s\' \'{"hook_event_name":"PreToolUse",'
    '"tool_name":"Bash",'
    '"tool_input":{"command":"git commit -m x"}}\' \\\n'
    '    | python3 cscpt/alint.py\n'
)


def _hook_refusal(reason):
    """Say outright that nothing ran, then leave non-zero. NEVER exit 0 here:
    a silent success is the very thing this guard exists to prevent."""
    sys.stderr.write(
        "%s is a hook body, not a command-line tool. It reads its JSON hook\n"
        "payload on stdin and ignores its arguments, so NOTHING WAS CHECKED ——\n"
        "do not read this silence as a pass.\n"
        "Cause: %s.\n"
        "Run it by hand from the repo root with:\n%s\n"
        % (os.path.basename(__file__), reason, _HOOK_STDIN_HOWTO))
    # Exit 3, never 2: on Pre/PostToolUse a 2 BLOCKS the tool call,
    # and a hand invocation must not be able to block anything. Every other
    # non-zero code merely shows this message; none of them blocks.
    sys.exit(3)


def _require_hook_payload(argv=()):
    """Return only if a real hook payload arrived; else explain and exit 3.

    On success `sys.stdin` is re-seated on the text already consumed, so the
    caller's `json.load(sys.stdin)` reads exactly what the harness sent and
    needs no change. `sys.exit` raises SystemExit, which is NOT an Exception,
    so the fail-open handlers below cannot swallow a refusal.
    """
    stray = [a for a in argv if _argv_names_a_file(a)]
    if stray:
        _hook_refusal(
            "argv names the file %r, and no hook event ever passes one —— the "
            "file to check arrives in the payload, never on the command line"
            % stray[0])
    try:
        if sys.stdin is None:
            _hook_refusal("this process has no stdin at all (descriptor 0 closed)")
        if sys.stdin.isatty():
            _hook_refusal("stdin is a terminal, so no payload can ever arrive")
        piped = _hook_stdin_is_pipe()
        ready = select.select([sys.stdin], [], [], _HOOK_STDIN_WAIT_S)[0]
    except Exception:
        return  # an unselectable stdin must never disarm the lint
    if not ready:
        _hook_refusal("nothing reached stdin within %gs" % _HOOK_STDIN_WAIT_S)
    try:
        raw = sys.stdin.read()
    except Exception:
        return  # an unreadable stdin must never disarm the lint
    if not raw.strip() and not piped:
        _hook_refusal(
            "stdin delivered nothing and is not a pipe —— `/dev/null`, a closed "
            "descriptor or a plain file, which is what a shell hands a command "
            "run by hand. An EMPTY PIPE is left alone on purpose: that is the "
            "harness sending nothing, and every lint here fails open on it")
    sys.stdin = io.StringIO(raw)


def main():
    _require_hook_payload(sys.argv[1:])
    try:
        data = json.load(sys.stdin)
    except Exception:
        _log("unknown", "no_stdin")
        return 0
    if not isinstance(data, dict):
        _log("unknown", "no_stdin")
        return 0

    sid = str(data.get("session_id") or "")[:8] or "unknown"
    sub = "yes" if _is_subagent(data) else "no"

    tool_input = data.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None

    # LIVENESS PROBE (docstring: WIRING). A gate that only speaks on a commit
    # is hard to prove alive without making one, and "I ran the script by hand"
    # proves the script and never the wiring (hook_guide § 7.1). Running
    # `echo ALINT_PROBE` through the REAL Bash tool answers it in one call:
    # a reply means the harness invoked this file unaided.
    if isinstance(command, str) and _PROBE_TOKEN in command:
        _log(sid, "probe", sub=sub, note=tp_basename(data))
        _advise("[alint] ALIVE —— the TEA1 in-flight gate is wired and this "
                "invocation came from the harness. Sub-agent verdict for this "
                "call: sub=%s." % sub)
        return 0

    if not _is_tea1(command):
        _log(sid, "not_git", sub=sub)
        return 0

    if not _in_scope(data):
        _log(sid, "out_of_scope", sub=sub)
        return 0

    if sub == "yes":
        # TEA1 belongs to the main agent; a sub-agent commits its own work.
        _log(sid, "subagent", sub=sub)
        return 0

    if os.environ.get("ALINT_OFF"):
        _log(sid, "disabled", sub=sub)
        _advise("[alint] TEA1 in-flight gate is DISABLED via ALINT_OFF. Root "
                "CLAUDE.md §3.1.6's 'no SAs in-flight' precondition is NOT "
                "being checked —— verify it by hand before committing.")
        return 0

    tp = data.get("transcript_path")
    if not (isinstance(tp, str) and tp and os.path.isfile(tp)):
        _log(sid, "no_transcript", sub=sub)
        _advise("[alint] TEA1 in-flight gate could NOT run: no readable "
                "transcript in the hook payload, so whether any sub-agent is "
                "still running is UNKNOWN. Root CLAUDE.md §3.1.6 still "
                "applies —— confirm by hand that every dispatched agent has "
                "reported back before committing.")
        return 0

    try:
        launches, last_live, last_rest, workflows = _scan_transcript(tp)
    except Exception as exc:
        _log(sid, "unreadable_transcript", sub=sub, note=type(exc).__name__)
        _advise("[alint] TEA1 in-flight gate could NOT run: the session "
                "transcript could not be parsed, so whether any sub-agent is "
                "still running is UNKNOWN. Root CLAUDE.md §3.1.6 still "
                "applies —— confirm by hand before committing.")
        return 0

    # Agents and workflows are judged by the SAME rule —— launched at a later
    # line than it last rested —— and differ only in what can be aged: an agent
    # by its single output file, a workflow by its whole transcript directory.
    live, released = [], []
    for kind, items in (("agent", launches), ("workflow", workflows)):
        for key, info in items.items():
            if last_live.get(key, -1) <= last_rest.get(key, -1):
                continue                          # rested after its last start
            quiet = (_quiet_seconds(info.get("out")) if kind == "agent"
                     else _dir_quiet_seconds(info.get("dir")))
            entry = (kind, key, info.get("desc"), quiet)
            if quiet is not None and quiet > _STALE_S:
                released.append(entry)
            else:
                live.append(entry)

    if not live:
        if released:
            _log(sid, "stale_release", live=0, sub=sub,
                 note=";".join(_tag(e) for e in released))
            _advise(
                "[alint] TEA1 in-flight gate PASSED, but %d dispatched "
                "agent(s)/workflow(s) never reported back and were released "
                "as stale (quiet for over %d minutes): %s. They may hold "
                "unfinished work —— root CLAUDE.md §9.02.4 treats a died "
                "agent's task as NOT done. Re-dispatch or redo that scope if "
                "it matters."
                % (len(released), _STALE_S // 60,
                   "; ".join("%s %s (%s)" % (k, i, d or "?")
                             for k, i, d, _ in released)))
        else:
            _log(sid, "clear", live=0, sub=sub)
        return 0

    lines = []
    for kind, key, desc, quiet in sorted(live, key=lambda x: (x[0], x[1])):
        age = ("quiet %dm" % int(quiet // 60)) if quiet is not None \
            else "activity unknown"
        lines.append("  - %s %s — %s (%s)"
                     % (kind, key, desc or "(no description)", age))

    # Exit 2 + STDERR is the only PreToolUse channel that both reaches the
    # model and stops the call (hook_guide § 6). At exit 2 the harness ignores
    # stdout entirely, so nothing may be written there.
    sys.stderr.write(
        "BLOCKED by alint —— root CLAUDE.md §3.1.6: Turn-End Actions require "
        "that NO sub-agent or workflow is in flight, and %d still %s:\n%s\n"
        "This is a mechanical gate, not a judgement call: the precondition "
        "was consciously overridden four times before it existed. Do ONE of:\n"
        "  1. WAIT for each one's completion notification, then commit.\n"
        "  2. `TaskStop` one that is genuinely stuck, passing the id shown "
        "above (a workflow's id is its task id) —— that emits a killed "
        "notification and clears this gate at once.\n"
        "Note that a killed or limit-hit agent's task is NOT done "
        "(root CLAUDE.md §9.02.4): re-dispatch or redo that scope. A workflow "
        "counts for its WHOLE fleet —— its child agents never appear in this "
        "transcript, so nothing else is watching them.\n"
        % (len(live), "is" if len(live) == 1 else "are", "\n".join(lines)))
    _log(sid, "block", live=len(live), sub=sub,
         note=";".join(_tag(e) for e in live))
    return 2


if __name__ == "__main__":
    sys.exit(main())
