#!/usr/bin/env python3
"""Stop hook —— enforces chat-text discipline when the MAIN agent ends a turn.

Two rules, picked by the session's working directory (see REPO SCOPE below):
* REPO mode (this repo) —— root CLAUDE.md §3.2: the only chat text permitted is
  the 5 declaration lines led by ✅ ⇠ ➡️ ⚠️ 🚨; any other non-blank line is a
  breach. Two narrow exemptions apply (`yn`, `DATS` —— see EXEMPTIONS).
* READER mode (the parent `GitHub/` folder alone) —— that folder's own
  CLAUDE.md mandates ZERO chat text "NO MATTER WHAT", so there every non-blank
  line is a breach, declaration glyphs included, and no exemption applies.

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: a Stop hook. At turn end it scans the main agent's chat text and BLOCKS
  any impermissible line.
* IF IT BLOCKS: one forced extra turn, terse reason on stderr. Delete the prose
  or fold it into a declaration, then end again. EVERY breach blocks; no
  ceiling to sit out.
* PERMITTED in this repo: blank lines; a `---`/`***`/`___` divider; a line led by
  ✅ ⇠ ➡️ ⚠️ 🚨 (a `**` wrapper before the glyph is fine). In the parent
  `GitHub/` Reader folder: blank lines ONLY, declarations included.
* Silent in other projects; verdicts log to `cscpt/.clint.log`.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WHY A HOOK, NOT TRUST: the discipline is silent to break and normally caught only
on a human re-read; a deterministic Stop-time scan surfaces the slip at once.

SCAN BOUNDARY: keep MAIN-agent lines only (`isSidechain` falsy) so a sub-agent's
prose never counts against the main turn, then scan every assistant text block
after the last GENUINE user line. `_is_real_user` excludes tool_result-only turns
AND the wrappers Claude Code appends as `type:"user"` with no human behind them
(`_SYSTEM_INJECTED_TAGS` —— task notifications, local-command echoes; exact
prefix match, so human prose merely mentioning those words is unaffected):
counting one as genuine would push the boundary PAST real prose from the current
exchange and hide the breach.

HARNESS-AUTHORED ASSISTANT TEXT: lines flagged `isApiErrorMessage: true` are
written by the CLI, not the model —— e.g. "You've hit your session limit ·
resets 11:40am". They are skipped, because blocking on one punishes the model
for text it never emitted, and does so precisely when it is least able to
comply (out of quota, or mid API failure). Live-verified: that flag is present
on such lines and absent from genuine assistant messages, in this repo's own
transcripts as well as the Reader's.

ALWAYS RED: a Stop hook's exit-0 output (`systemMessage` included) reaches only
the USER, never the model —— the turn has already ended —— so a non-blocking
warning can NEVER make the agent self-correct. The one channel reaching the
MODEL on Stop is a block: exit 2 feeds stderr back as an error and forces one
more turn. A log-only tier is therefore worthless as a corrective, and every
breach blocks. The cost is understood and accepted: a block ends that model
turn before its chapter marker is written, which is the intended loudness.

EXEMPTIONS (REPO mode only —— both come from THIS repo's protocols, which the
Reader folder does not share, and the Reader's own rule admits no exception):
* `yn` —— when the triggering user message contains the literal ` yn` (leading
  space included), the user has invoked the project override meaning "answer in
  one word in chat", so chat text is AUTHORISED and the whole turn is exempt.
  Plain substring, deliberately: the leading space is what stops `Brooklyn` or
  `synergy` matching, and requiring it at the END would be wrong —— a real
  prompt reads "Was your last turn fully completed? yn" followed by two more
  lines of instructions. The token only ever appears in a typed message.
* `DATS` —— the session-closing protocol (`universal/close.md`) mandates one
  chat line after the close files are declared, in exactly one of two forms:
  "DATS done. Fixed [no.] file(s)." or "DATS incomplete. [≤8w_comment]." Hence
  the exemption is deliberately tight: the offending text must be a SINGLE line
  starting with `DATS` and at most 10 words —— 10 being the longest sanctioned
  form (2 fixed words + an 8-word comment). A second line, or an 11th word, is
  no longer that protocol line and is NOT exempt. `yn` is tested first; if both
  somehow applied the turn was authorised outright.

LOOP GUARD: exit 2 forces a continuation that ends in another Stop, so an
unguarded block would loop forever. Two INDEPENDENT signals of the same fact
("we are already inside a block-forced continuation"), either sufficient alone:
(a) `stop_hook_active` in the payload, set by the harness; (b) the scan
boundary itself being the harness's own injected feedback line —— live-verified
as a `type:"user"`, `isMeta:true` line whose content starts with "Stop hook
feedback:". Signal (b) needs no payload field and no successful log write,
which is why the old promptId ledger (read back from this script's own log) was
deleted rather than kept: a lost log write silently disarmed it, and it also
capped enforcement at one block per prompt, which is exactly the ceiling this
rewrite removes. A blocked continuation that itself emits prose is therefore
logged (`loop_guard`) and never blocked again.

Precisely how far that guarantee reaches, stated honestly rather than
optimistically: (b) is absent in exactly two shapes —— no feedback line was
injected at all, in which case no continuation was forced and there is no loop
to run; or a LATER `type:"user"` line displaced the feedback line as the scan
boundary. Only the second is a live risk, and it is why (a) is kept: the
payload flag does not depend on transcript shape. A spiral thus needs BOTH to
fail at once —— the harness omitting `stop_hook_active` AND appending an
unrecognised user-wrapper after every block —— a combination never observed
here. Should it ever appear, the repair is one line: add that wrapper's tag to
`_SYSTEM_INJECTED_TAGS`, which restores (b) at once. A sticky per-prompt flag
is deliberately NOT added as a third guard —— that IS the ledger, ceiling and
all, which the owner ruled out.

GLYPH-FREE STDERR: neither breach message names any of the 5 glyphs. Naming them
would teach exactly which prefixes pass and invite gaming by bolting a glyph
onto prose.

LOG EVERY STAGE: a breach-only log cannot tell "ran this turn and found
nothing" apart from "the harness never invoked this command" —— an empty log fits
BOTH, which is exactly how dead Stop-hook wiring went unnoticed across many real
sessions whilst the script itself was provably correct under manual invocation.
Leakage stays minimal: a breach line logs only the offending text, every other
stage logs no user content at all. Note the offending text is glyph-free by
construction in REPO mode but NOT in READER mode, where a declaration line is
itself the breach —— the stderr message stays glyph-free in both.

REPO SCOPE (`_mode`): user-level registration reaches every project and this
lint BLOCKS, so it must not police repos that never agreed to either rule.
Signals, in order: the payload's `cwd` (confirmed present on a live PostToolUse
payload, NOT yet on a real Stop payload —— so the fallback is a live safety net,
not theory), else the `~/.claude/projects/<slug>/<uuid>.jsonl` transcript slug
(the project dir with every `/` and ` ` replaced by `-`). Both compare against
values derived from this script's OWN location, never a hard-coded path, so the
repo stays relocatable; symlinks are resolved. REPO is tested FIRST and matches
sub-paths; READER requires EXACT equality with the parent folder and never a
sub-path —— otherwise this repo (and every sibling repo under `GitHub/`, which
has its own rules) would wrongly inherit the zero-text rule. It FAILS OPEN to
REPO mode when neither signal is usable: an unreadable payload is not evidence
of a different project, and a lint that goes dark on ambiguity is the failure
this whole wiring exists to fix.

READER MODE (known limitation): the Reader folder's CLAUDE.md applies only when
that folder is the session's SOLE working directory, but no Stop-payload or
transcript field exposes additionally-added directories, so the check can only
approximate it with an exact `cwd` match. A session rooted at `GitHub/` that
ALSO added another repo would be held to the zero-text rule it no longer owes.
Accepted because that project slug has, in practice, only ever hosted the
Reader; delete the two READER branches to revert to repo-only policing.

WIRING (kept here, not in NON-CCSIM: a caller never invokes this file, so the
plumbing is dead weight to everyone but an editor). Registered as a `Stop` hook
in the USER-level `~/.claude/settings.json` —— the Claude Desktop app executes
user-level hooks and silently ignores project-level ones —— hence it fires in
every project and must self-scope. IN: Stop-hook JSON on stdin
(`transcript_path`, `cwd`, `session_id`, `stop_hook_active`); OUT: nothing at
all on a clean turn. EXIT 0 = clean, exempt, out-of-scope, loop-guarded, or ANY
failure; EXIT 2 = breach. FAIL-SAFE: a bad payload, an unreadable transcript or
a failed stderr/log write all exit 0, so the hook can never break a turn on its
own failure.

LOG FORMAT: exactly ONE tab-delimited line per invocation whatever the verdict
(`clean`, `block`, `block_failed`, `loop_guard`, `exempt:yn`, `exempt:dats`,
`out_of_scope`, or the parse stage reached), each carrying `mode=` (which rule
applied) and `pid=` (the prompt it belongs to), so one `grep` shows every
invocation for a prompt and why it was judged so. A log that does NOT grow
across real turns means the harness is not calling this hook at all —— the
diagnostic the LOG EVERY STAGE rationale above exists to enable.
`CLINT_LOG=<path>` redirects it, so a test run neither reads nor pollutes the
real log. Nothing else is written anywhere.
"""

import sys
import os
import re
import json
from datetime import datetime

# ---------------------------------------------------------------------------
# SCOPE GUARD —— user-level registration fires in EVERY project on this Mac, so
# self-scope and exit silently elsewhere. Signals, in order: the payload's
# `cwd`, else the `~/.claude/projects/<slug>/` transcript slug —— both compared
# against values derived from this file's OWN location, never a hard-coded
# path. FAILS OPEN to REPO mode when neither is usable. Full rationale (why
# user-level, why fail-open, why READER is exact-match only) is in the CCSIM
# section of the module docstring above.
# ---------------------------------------------------------------------------
_REPO_ROOT_REAL = os.path.realpath(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_REPO_SLUG = re.sub(r"[/ ]", "-", _REPO_ROOT_REAL.rstrip("/"))

# The Reader folder = this repo's immediate parent (`.../GitHub`). Derived, not
# hard-coded, so the whole tree stays relocatable.
_READER_ROOT_REAL = os.path.dirname(_REPO_ROOT_REAL)
_READER_SLUG = re.sub(r"[/ ]", "-", _READER_ROOT_REAL.rstrip("/"))

MODE_REPO = "repo"       # root CLAUDE.md §3.2 —— declarations only
MODE_READER = "reader"   # GitHub/ CLAUDE.md —— absolutely no chat text
MODE_OFF = "off"         # some other project —— not ours to police


def _mode(data):
    """Which rule this invocation is under: MODE_REPO, MODE_READER or
    MODE_OFF. REPO is tested first and matches sub-paths; READER matches ONLY
    an exact parent-folder hit (see docstring REPO SCOPE). Never raises: any
    unexpected error must default to "run the repo lint", exactly like every
    other fail-safe path in this file."""
    try:
        if not isinstance(data, dict):
            return MODE_REPO
        cwd = data.get("cwd")
        if isinstance(cwd, str) and cwd:
            real_cwd = os.path.realpath(cwd)
            if (real_cwd == _REPO_ROOT_REAL
                    or real_cwd.startswith(_REPO_ROOT_REAL + os.sep)):
                return MODE_REPO
            if real_cwd == _READER_ROOT_REAL:   # EXACT only, never a sub-path
                return MODE_READER
            return MODE_OFF
        tp = data.get("transcript_path")
        if isinstance(tp, str) and tp:
            m = re.search(r"/projects/([^/]+)/", tp)
            if m:
                slug = m.group(1)
                if slug == _REPO_SLUG or slug.startswith(_REPO_SLUG + "-"):
                    return MODE_REPO
                if slug == _READER_SLUG:        # EXACT only, never a sub-path
                    return MODE_READER
                return MODE_OFF
            # transcript_path present but not the recognised
            # .../projects/<slug>/... shape -> unparseable -> fall through.
        return MODE_REPO  # neither field usable -> FAIL-OPEN
    except Exception:
        return MODE_REPO  # never let a scope-check error silence the lint


# Base glyph codepoints (variation selectors ignored, so `➡️` and `➡` both pass).
_GLYPHS = ("✅", "⇠", "➡", "⚠", "\U0001f6a8")  # ✅ ⇠ ➡ ⚠ 🚨

# A markdown horizontal-rule / chapter divider line: 3+ of -, *, or _.
_HR_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")

# Fixed, GLYPH-FREE breach messages fed to the model via stderr on exit 2 (see
# docstring GLYPH-FREE STDERR —— must not name the glyphs, or it teaches how to
# game the check). Terse and terminal: tell the model to END the turn, not
# write more. One per mode, because "emit ONLY the 5 permitted declarations"
# would be actively wrong advice in a session that owes zero chat text.
_BREACH = {
    MODE_REPO: ("Chat-prose breach (root CLAUDE.md §3.2): emit ONLY the 5 "
                "permitted declarations. Avoid further prose."),
    MODE_READER: ("Chat-text breach (GitHub/ CLAUDE.md): this session must "
                  "emit NO chat text at all. End the turn silently."),
}

# Known system-injected wrapper tags Claude Code appends as `type: "user"`
# turns (notifications/command echoes) even though no human typed them —
# see `_is_real_user`. Exact prefix match only, never substring, so real
# human prose that merely mentions these words is unaffected.
_SYSTEM_INJECTED_TAGS = (
    "<task-notification>", "<local-command-caveat>",
    "<local-command-stdout>", "<command-name>", "<command-message>",
    "<command-args>")

# The harness's own injected continuation line after a Stop hook blocks —— a
# `type:"user"`, `isMeta:true` line beginning with this exact prefix. Used as
# loop-guard signal (b); see docstring LOOP GUARD.
_STOP_FEEDBACK_PREFIX = "Stop hook feedback:"

# The `yn` override token (see docstring EXEMPTIONS). The leading space is
# load-bearing —— without it `Brooklyn` and `synergy` would match.
_YN_TOKEN = " yn"

# Longest sanctioned `DATS` chat line: "DATS incomplete." + an 8-word comment.
_DATS_MAX_WORDS = 10

# Log path (overridable for tests via CLINT_LOG); default beside this script.
_LOG = os.environ.get("CLINT_LOG") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".clint.log")


def _line_ok(line, mode):
    """True if a single text line is permitted chat under `mode`.

    READER mode permits blank lines ONLY: a divider renders as a visible rule
    and a declaration glyph is still chat text, both of which that folder's
    CLAUDE.md forbids outright."""
    s = line.strip()
    if not s:
        return True                      # blank line —— renders as nothing
    if mode == MODE_READER:
        return False                     # zero-text rule: everything else fails
    if _HR_RE.match(line):
        return True                      # markdown divider / chapter rule
    if s.startswith(_GLYPHS):
        return True                      # a declaration glyph leads the line
    if s.startswith("**"):               # tolerate `**➡️ …**` bold wrapper
        if s[2:].lstrip().startswith(_GLYPHS):
            return True
    return False


def _text_of(content):
    """Yield the text of every text block in an assistant message `content`."""
    if isinstance(content, str):
        yield content
    elif isinstance(content, list):
        for blk in content:
            if isinstance(blk, dict) and blk.get("type") == "text":
                t = blk.get("text")
                if isinstance(t, str):
                    yield t


def _is_real_user(obj):
    """A genuine user prompt, not a tool_result-only `user` turn, and not a
    system-injected wrapper. Claude Code appends several notices as `type:
    "user"` turns with plain-string `message.content` even though no human
    typed them: background task-completion notifications
    (`<task-notification>...`) and local slash-command echoes
    (`<local-command-caveat>`, `<local-command-stdout>`, `<command-name>`,
    `<command-message>`, `<command-args>`). Treating those as genuine user
    turns would wrongly reset the scan boundary past real assistant prose
    from the current exchange, hiding it from the breach check —— so any
    string content beginning with one of these exact tag prefixes (after
    stripping leading whitespace) is excluded here.

    The harness's `Stop hook feedback:` line is deliberately NOT excluded: it
    genuinely opens a new turn, so it SHOULD move the boundary (a re-stop then
    reports fresh prose from the continuation, never the original breach
    twice). It is recognised separately by `_is_stop_feedback`."""
    if obj.get("type") != "user":
        return False
    content = (obj.get("message") or {}).get("content")
    if isinstance(content, str):
        return not content.lstrip().startswith(_SYSTEM_INJECTED_TAGS)
    if isinstance(content, list):
        # A tool_result-only turn is not a prompt; any non-tool_result => genuine.
        return any(isinstance(b, dict) and b.get("type") != "tool_result"
                   for b in content)
    return False


def _is_stop_feedback(obj):
    """True if `obj` is the harness's own post-block continuation line ——
    loop-guard signal (b), see docstring LOOP GUARD. Both conditions are
    required (`isMeta` true AND the exact text prefix) so no human message can
    impersonate it by quoting the phrase."""
    try:
        if not isinstance(obj, dict) or obj.get("isMeta") is not True:
            return False
        content = (obj.get("message") or {}).get("content")
        return (isinstance(content, str)
                and content.lstrip().startswith(_STOP_FEEDBACK_PREFIX))
    except Exception:
        return False


def _trigger_text(obj):
    """All human-visible text of the user message that opened this turn ——
    the `yn` exemption is keyed on it. Handles both plain-string content and
    the block-list form (a prompt carrying attachments). Never raises."""
    try:
        if not isinstance(obj, dict):
            return ""
        content = (obj.get("message") or {}).get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = [b.get("text") for b in content
                     if isinstance(b, dict) and b.get("type") == "text"
                     and isinstance(b.get("text"), str)]
            return "\n".join(parts)
    except Exception:
        pass
    return ""


def _dats_exempt(offending):
    """True if the whole breach is the single `DATS` status line that
    `universal/close.md` mandates in chat (see docstring EXEMPTIONS). Exactly
    one line, starting with `DATS`, at most 10 words —— anything longer or
    multi-line is ordinary prose and stays a breach."""
    return (len(offending) == 1
            and offending[0].startswith("DATS")
            and len(offending[0].split()) <= _DATS_MAX_WORDS)


def _log_event(sid, action, lines=0, first="-", pid="-", mode="-"):
    """Append ONE terse diagnostic line for ANY hook invocation, breach or not
    (see docstring LOG EVERY STAGE).

    Fields are TAB-separated and `first=` stays LAST because it alone may carry
    free text (tabs/newlines in it are flattened, so a record is always exactly
    one line). `mode=` records which rule applied, so a `reader:`-policed block
    is never mistaken for a repo one when auditing.

    FAIL-SAFE: swallow all errors -- a logging failure must never break a turn
    (same contract as the rest of this file). Nothing reads this log back, so a
    lost write costs diagnostics only, never enforcement."""
    try:
        with open(_LOG, "a", encoding="utf-8") as lf:
            lf.write(
                "%s\tsession=%s\tpid=%s\tmode=%s\taction=%s\tlines=%d\tfirst=%s\n"
                % (datetime.now().isoformat(timespec="seconds"),
                   sid, pid, mode, action, lines,
                   str(first)[:200].replace("\t", " ").replace("\n", " ")))
    except Exception:
        pass


def _turn_id(data, objs):
    """The id of the user prompt this Stop belongs to —— logged as `pid=` so one
    grep gathers every invocation belonging to one prompt (purely diagnostic;
    nothing branches on it). Prefer the transcript's last main-agent `user`
    line's `promptId`, which stays constant across a block-forced continuation
    and changes on every new genuine user message; fall back to the payload's
    own prompt id for harnesses whose transcript lines lack the field. Returns
    "" when neither is readable. Never raises.

    Ids containing whitespace are REJECTED rather than sanitised, so a stray
    tab can never split one log field into two and desync the record shape."""
    def _clean(p):
        return isinstance(p, str) and p and not any(c.isspace() for c in p)

    try:
        for o in reversed(objs):
            if isinstance(o, dict) and o.get("type") == "user":
                p = o.get("promptId")
                if _clean(p):
                    return p
        for key in ("prompt_id", "promptId"):   # payload naming varies
            p = data.get(key)
            if _clean(p):
                return p
    except Exception:
        pass
    return ""


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        _log_event("unknown", "no_stdin")
        return 0

    if not isinstance(data, dict):
        _log_event("unknown", "no_stdin")
        return 0

    sid = str(data.get("session_id") or "")[:8] or "unknown"

    mode = _mode(data)
    if mode == MODE_OFF:
        _log_event(sid, "out_of_scope", mode=mode)
        return 0

    tp = data.get("transcript_path") or ""
    if not tp or not os.path.isfile(tp):
        _log_event(sid, "no_transcript", mode=mode)
        return 0

    try:
        objs = []
        with open(tp, "r", encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    o = json.loads(raw)
                except Exception:
                    continue
                if isinstance(o, dict) and o.get("isSidechain") is not True:
                    objs.append(o)       # MAIN-agent lines only
    except Exception:
        _log_event(sid, "unreadable_transcript", mode=mode)
        return 0

    if not objs:
        _log_event(sid, "empty_transcript", mode=mode)
        return 0

    turn = _turn_id(data, objs)               # diagnostic grep key only
    plog = turn or "-"

    # Boundary: everything after the last GENUINE user message = the final turn.
    # That same message is kept, because it decides the `yn` exemption and,
    # when it is the harness's own post-block injection, loop-guard signal (b).
    start = 0
    trigger = None
    for i, o in enumerate(objs):
        if _is_real_user(o):
            start = i + 1
            trigger = o

    offending = []
    for o in objs[start:]:
        if o.get("type") != "assistant":
            continue
        if o.get("isApiErrorMessage") is True:
            continue                     # CLI-authored, not model output
        msg = o.get("message") or {}
        if msg.get("role") != "assistant":
            continue
        for text in _text_of(msg.get("content")):
            for ln in text.splitlines():
                if not _line_ok(ln, mode):
                    offending.append(ln.strip())

    if not offending:
        # Clean turn -> proof-of-life, non-blocking.
        _log_event(sid, "clean", pid=plog, mode=mode)
        return 0

    # --- Exemptions (REPO mode only; see docstring EXEMPTIONS) ---------------
    if mode == MODE_REPO:
        if _YN_TOKEN in _trigger_text(trigger):
            # The user authorised a one-word chat answer -> nothing to enforce.
            _log_event(sid, "exempt:yn", len(offending), offending[0],
                       pid=plog, mode=mode)
            return 0
        if _dats_exempt(offending):
            # The single close-protocol status line -> sanctioned chat text.
            _log_event(sid, "exempt:dats", len(offending), offending[0],
                       pid=plog, mode=mode)
            return 0

    # --- Loop guard (see docstring LOOP GUARD) ------------------------------
    # Either signal alone withholds the block; both are checked because (a) can
    # be absent from a payload and (b) needs no payload at all.
    if bool(data.get("stop_hook_active")) or _is_stop_feedback(trigger):
        _log_event(sid, "loop_guard", len(offending), offending[0],
                   pid=plog, mode=mode)
        return 0

    # --- RED —— block and feed the model the reason via stderr ---------------
    # On exit 2 the harness ignores stdout/JSON, so write to STDERR. Every
    # breach reaching here blocks: there is no ceiling and no ledger. The log
    # line is written only AFTER the stderr write succeeds, so the record
    # always reflects a block actually delivered.
    try:
        sys.stderr.write(_BREACH[mode])
    except Exception:
        _log_event(sid, "block_failed", len(offending), offending[0],
                   pid=plog, mode=mode)
        return 0                          # fail-safe: never break the turn
    _log_event(sid, "block", len(offending), offending[0], pid=plog, mode=mode)
    return 2                              # blocks the stop; stderr reaches Claude


if __name__ == "__main__":
    sys.exit(main())
