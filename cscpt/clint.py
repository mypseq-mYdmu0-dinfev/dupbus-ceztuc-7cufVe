#!/usr/bin/env python3
"""Stop hook —— enforces root CLAUDE.md §3.2 NO-CHAT-TEXT: when the MAIN agent ends
a turn, the only chat text permitted is the 5 declaration lines led by
✅ ⇠ ➡️ ⚠️ 🚨; any other non-blank line in that turn's assistant text is a breach.

=== NON-CCSIM —— all you need to RUN it ===
* Run by the harness, never by hand. Registered as a `Stop` hook in the
  USER-level `~/.claude/settings.json` (the Claude Desktop app executes
  user-level hooks and silently ignores project-level ones), so it fires in
  EVERY project on this Mac —— and self-scopes: outside THIS repo it logs
  `out_of_scope` and exits 0.
* IN: Stop-hook JSON on stdin (`transcript_path`, `cwd`, `session_id`,
  `stop_hook_active`). OUT: nothing at all on a clean turn.
* EXIT 0 = clean, out-of-scope, tolerated, or ANY failure. EXIT 2 = the FIRST
  breach under a given user prompt: a terse glyph-free reason goes to STDERR,
  Claude reads it and is forced to end the turn again. Every LATER breach under
  that same prompt is logged but never blocked —— at most ONE split turn per
  prompt.
* TOLERATED lines: blank; a `---`/`***`/`___` divider; a glyph-led line; a `**`
  bold wrapper before the glyph (`**➡️ …`, per §3.2.3.3).
* LOG `cscpt/.clint.log` —— exactly ONE tab-delimited line per invocation
  whatever the verdict (`clean`, `block`, `block_failed`, `yellow:spent`,
  `yellow:active`, `out_of_scope`, or the parse stage reached), each carrying
  `pid=` (the prompt it belongs to), so one `grep` shows every invocation for a
  prompt and why it was tiered so. A log that does NOT grow across real turns
  means the harness is not calling this hook at all.
* `CLINT_LOG=<path>` redirects it —— and with it the RED/YELLOW ledger, which
  lives in the same file, so a test run neither reads nor pollutes real
  escalation state. There is no second file to redirect.
* FAIL-SAFE: bad payload, unreadable transcript, or a failed stderr/log write ->
  exit 0. It can never break a turn on its own failure.
(Run by the harness, not read —— see README.)

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

HYBRID RED/YELLOW: a Stop hook's exit-0 output (`systemMessage` included) reaches
only the USER, never the model —— the turn has already ended —— so a non-blocking
warning can NEVER make the agent self-correct. The one channel reaching the MODEL
on Stop is a block: exit 2 feeds stderr back as an error and forces exactly one
more turn. Hence RED blocks once, YELLOW only logs. INVARIANT: YELLOW is
log/user-facing BY DESIGN and cannot be made model-facing —— anything that made
it so would BE a second RED, the very cost this tier exists to avoid.

ARMING: "the same user prompt" is keyed on the harness `promptId`, stamped on
EVERY main-agent `user` line —— genuine prompts, `tool_result` lines and the
harness's own `Stop hook feedback:` line alike. Two live-verified properties make
it the right key: the feedback line a RED injects INHERITS the interrupted
prompt's id, so the forced continuation can only ever be YELLOW; and a new
genuine prompt carries a fresh id, which re-arms the single RED shot. Do NOT key
on that line's `uuid` instead —— it is itself a new `user` line, so a uuid key
mints a new value per continuation, re-arms RED and loops. As that line is not a
`_SYSTEM_INJECTED_TAGS` wrapper it also becomes the scan boundary, so a YELLOW
reports NEW prose from the continuation, never the original breach twice.

LEDGER IN THE LOG: "RED already spent for this id" is read back from this
script's OWN log tail —— no second artefact to corrupt, desync, gitignore or
clean up, and it is the very line a human already greps. Matching is
TAB-DELIMITED field equality, never substring, so `action=block_failed` can never
read as `action=block`; `pid=` is never truncated the way `session=` is (a
shortened id could collide with another prompt's prefix and downgrade a genuine
RED); ids containing whitespace are REJECTED, not sanitised, since an embedded
tab would split a field and desync reader from writer. The 64 KiB tail keeps the
read O(1) as the log grows without bound, and a miss would degrade towards
ENFORCEMENT (one extra RED, still loop-guarded), never towards a breach going
unrecorded. `action=block` is written only AFTER the stderr write succeeds: the
ledger records shots FIRED, not attempted, so an undelivered block never spends
the prompt's RED.

LOOP GUARD: exit 2 forces a continuation that ends in another Stop, so an
unguarded block would loop forever. Two independent guards, EITHER sufficient
alone: (a) the promptId ledger; (b) `stop_hook_active`, set by the harness once
Claude is continuing because of a prior Stop-block. Both are kept —— a failed log
write would silently make (a) forget that RED was spent, and a lint that blocks
every continuation forever is far worse than one that nudges twice; conversely
(a) keeps the promise when (b) is absent or false on a same-prompt re-stop. With
neither id readable it degrades to (b) alone: the pre-hybrid behaviour.

GLYPH-FREE STDERR: `_BREACH` names NONE of the 5 glyphs. Naming them would teach
exactly which prefixes pass and invite gaming by bolting a glyph onto prose.

LOG EVERY STAGE: a breach-only log cannot tell "ran this turn and found
nothing" apart from "the harness never invoked this command" —— an empty log fits
BOTH, which is exactly how dead Stop-hook wiring went unnoticed across many real
sessions whilst the script itself was provably correct under manual invocation.
Leakage stays nil: a breach line logs only the offending text (glyph-free by
construction), every other stage logs no user content at all.

REPO SCOPE (`_in_scope`): user-level registration reaches every project and this
lint BLOCKS, so it must not police repos that never agreed to §3.2. Signals, in
order: the payload's `cwd` (confirmed present on a live PostToolUse payload, NOT
yet on a real Stop payload —— so the fallback is a live safety net, not theory),
else the `~/.claude/projects/<slug>/<uuid>.jsonl` transcript slug (the project
dir with every `/` and ` ` replaced by `-`). Both compare against values derived
from this script's OWN location, never a hard-coded path, so the repo stays
relocatable; symlinks are resolved and a sub-path counts as in-scope. It FAILS
OPEN when neither signal is usable: an unreadable payload is not evidence of a
different project, and a lint that goes dark on ambiguity is the failure this
whole wiring exists to fix.
"""

import sys
import os
import re
import json
from datetime import datetime

# ---------------------------------------------------------------------------
# REPO-SCOPE GUARD —— user-level registration fires in EVERY project on this
# Mac, so self-scope to THIS repo and exit silently elsewhere. Signals, in
# order: the payload's `cwd`, else the `~/.claude/projects/<slug>/` transcript
# slug —— both compared against values derived from this file's OWN location,
# never a hard-coded path. FAILS OPEN when neither is usable. Full rationale
# (why user-level, why fail-open, why THIS lint in particular must not roam)
# is in the CCSIM section of the module docstring above.
# ---------------------------------------------------------------------------
_REPO_ROOT_REAL = os.path.realpath(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_REPO_SLUG = re.sub(r"[/ ]", "-", _REPO_ROOT_REAL.rstrip("/"))


def _in_scope(data):
    """True if this invocation's project is THIS repo (or a sub-path of
    it), or if scope genuinely cannot be determined (FAIL-OPEN, see block
    comment above). Never raises: any unexpected error here must default to
    "run the lint", exactly like every other fail-safe path in this file."""
    try:
        if not isinstance(data, dict):
            return True
        cwd = data.get("cwd")
        if isinstance(cwd, str) and cwd:
            real_cwd = os.path.realpath(cwd)
            return (real_cwd == _REPO_ROOT_REAL
                    or real_cwd.startswith(_REPO_ROOT_REAL + os.sep))
        tp = data.get("transcript_path")
        if isinstance(tp, str) and tp:
            m = re.search(r"/projects/([^/]+)/", tp)
            if m:
                slug = m.group(1)
                return (slug == _REPO_SLUG
                        or slug.startswith(_REPO_SLUG + "-"))
            # transcript_path present but not the recognised
            # .../projects/<slug>/... shape -> unparseable -> fall through.
        return True  # neither field usable -> FAIL-OPEN
    except Exception:
        return True  # never let a scope-check error silence the lint


# Base glyph codepoints (variation selectors ignored, so `➡️` and `➡` both pass).
_GLYPHS = ("✅", "⇠", "➡", "⚠", "\U0001f6a8")  # ✅ ⇠ ➡ ⚠ 🚨

# A markdown horizontal-rule / chapter divider line: 3+ of -, *, or _.
_HR_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")

# Fixed, GLYPH-FREE breach message fed to the model via stderr on exit 2 (see
# docstring CRITICAL —— must not name the glyphs, or it teaches how to game the
# check). Terse and terminal: tell the model to END the turn, not write more.
_BREACH = ("Chat-prose breach (root CLAUDE.md §3.2): emit ONLY the 5 permitted "
           "declarations. Avoid further prose.")

# Known system-injected wrapper tags Claude Code appends as `type: "user"`
# turns (notifications/command echoes) even though no human typed them —
# see `_is_real_user`. Exact prefix match only, never substring, so real
# human prose that merely mentions these words is unaffected.
_SYSTEM_INJECTED_TAGS = (
    "<task-notification>", "<local-command-caveat>",
    "<local-command-stdout>", "<command-name>", "<command-message>",
    "<command-args>")

# Log path (overridable for tests via CLINT_LOG); default beside this script.
# The log doubles as the RED/YELLOW ledger (see docstring ARMING), so pointing
# CLINT_LOG at a scratch file also isolates a test run's escalation state ——
# there is deliberately no second file to redirect and forget.
_LOG = os.environ.get("CLINT_LOG") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".clint.log")

# How much of the log tail to consult when asking "was RED already spent for
# this promptId?". 64 KiB is ~500 log lines —— many turns' worth, whilst the
# read stays O(1) as the log grows without bound. Only a handful of lines can
# ever separate a RED from the continuation it forces, so a live prompt's
# verdict cannot fall out of the window; and if one somehow did, the miss
# degrades towards ENFORCEMENT (one extra RED, still loop-guarded by
# `stop_hook_active`), never towards a breach going unrecorded.
_TAIL_BYTES = 64 * 1024


def _line_ok(line):
    """True if a single text line is permitted chat (declaration/blank/divider)."""
    s = line.strip()
    if not s:
        return True                      # blank line
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
    stripping leading whitespace) is excluded here."""
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


def _log_event(sid, action, lines=0, first="-", pid="-"):
    """Append ONE terse diagnostic line for ANY hook invocation, breach or not
    (see docstring DIAGNOSTIC). An `action=block` line is ALSO the ledger entry
    meaning "RED already spent for this pid" (see `_red_spent`), so the caller
    must write it only once the block is actually being delivered.

    Fields are TAB-separated and `first=` stays LAST because it alone may carry
    free text (tabs/newlines in it are flattened, so a record is always exactly
    one line). `pid=` is NOT truncated the way `session=` is: it is matched
    exactly by `_red_spent`, and a shortened id could collide with another
    prompt's prefix and wrongly downgrade a genuine RED to YELLOW.

    FAIL-SAFE: swallow all errors -- a logging failure must never break a turn
    (same contract as the rest of this file). A lost write only costs the
    ledger its memory, which `stop_hook_active` independently covers."""
    try:
        with open(_LOG, "a", encoding="utf-8") as lf:
            lf.write("%s\tsession=%s\tpid=%s\taction=%s\tlines=%d\tfirst=%s\n" % (
                datetime.now().isoformat(timespec="seconds"),
                sid, pid, action, lines,
                str(first)[:200].replace("\t", " ").replace("\n", " ")))
    except Exception:
        pass


def _turn_id(data, objs):
    """The id of the user prompt this Stop belongs to —— the RED/YELLOW key
    (see docstring ARMING). Prefer the transcript's last main-agent `user`
    line's `promptId`: that is the value proven live to stay constant across a
    RED-forced continuation (the injected `Stop hook feedback:` line inherits
    it) and to change on every new genuine user message. Fall back to the
    payload's own prompt id for harnesses whose transcript lines lack the
    field. Returns "" when neither is readable —— the caller then degrades to
    `stop_hook_active` alone. Never raises.

    Ids containing whitespace are REJECTED rather than sanitised: the ledger is
    tab-delimited, so an embedded tab would split one field into two and the
    reader would silently stop matching what the writer wrote. Rejecting keeps
    writer and reader in lockstep and degrades to the safe path instead."""
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


def _red_spent(turn_id):
    """True if a RED block was already delivered for this prompt id, read back
    from this script's own log tail (see docstring ARMING). Matching is
    TAB-DELIMITED field equality, never substring: `action=block_failed` shares
    a prefix with `action=block` and must NOT count as a spent shot.

    FAIL-SAFE: an unknown id, a missing/unreadable/rotated log, or any error ->
    False, i.e. "RED still armed". Failing towards enforcement keeps the lint
    alive; `stop_hook_active` remains as the independent loop guard."""
    if not turn_id:
        return False
    try:
        with open(_LOG, "rb") as lf:
            try:
                lf.seek(-_TAIL_BYTES, os.SEEK_END)
            except OSError:
                lf.seek(0)                # log shorter than the tail window
            blob = lf.read().decode("utf-8", errors="replace")
        want = "pid=" + turn_id
        for line in blob.splitlines():
            fields = line.split("\t")
            if "action=block" in fields and want in fields:
                return True
    except Exception:
        pass
    return False


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

    if not _in_scope(data):
        _log_event(sid, "out_of_scope")
        return 0

    tp = data.get("transcript_path") or ""
    if not tp or not os.path.isfile(tp):
        _log_event(sid, "no_transcript")
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
        _log_event(sid, "unreadable_transcript")
        return 0

    if not objs:
        _log_event(sid, "empty_transcript")
        return 0

    turn = _turn_id(data, objs)               # RED/YELLOW key for this prompt
    plog = turn or "-"

    # Boundary: everything after the last GENUINE user message = the final turn.
    start = 0
    for i, o in enumerate(objs):
        if _is_real_user(o):
            start = i + 1

    offending = []
    for o in objs[start:]:
        if o.get("type") != "assistant":
            continue
        msg = o.get("message") or {}
        if msg.get("role") != "assistant":
            continue
        for text in _text_of(msg.get("content")):
            for ln in text.splitlines():
                if not _line_ok(ln):
                    offending.append(ln.strip())

    if not offending:
        # Clean turn -> proof-of-life, non-blocking.
        _log_event(sid, "clean", pid=plog)
        return 0

    # --- Tier the breach (see docstring VERDICT / ARMING / LOOP GUARD) --------
    # Either guard alone downgrades RED to YELLOW; both are checked because each
    # covers the other's failure mode.
    if bool(data.get("stop_hook_active")):
        why = "yellow:active"             # harness says: already in a continuation
    elif _red_spent(turn):
        why = "yellow:spent"              # ledger says: RED already fired this prompt
    else:
        why = None                        # RED still armed

    # Offending prose is glyph-free by definition, so the log never leaks the
    # passing glyphs; the stderr message is glyph-free too.
    if why:
        # YELLOW —— record the nudge, do not block. Nothing is written to
        # stdout/stderr: at exit 0 no output of ours reaches the MODEL anyway
        # (docstring VERDICT), and staying silent keeps the turn's own ending
        # untouched. The log line IS the nudge.
        _log_event(sid, why, len(offending), offending[0], pid=plog)
        return 0

    # RED —— first breach of this prompt: block ONCE and feed the model the
    # reason via stderr. On exit 2 the harness ignores stdout/JSON, so write to
    # STDERR. The stderr write is the last gate that can still abort the block,
    # so the ledger entry (`action=block`) is claimed only AFTER it succeeds ——
    # otherwise a failed delivery would spend the shot without ever reaching the
    # model, and the real breach would be silently downgraded to YELLOW.
    try:
        sys.stderr.write(_BREACH)
    except Exception:
        _log_event(sid, "block_failed", len(offending), offending[0], pid=plog)
        return 0                          # fail-safe: never break the turn
    _log_event(sid, "block", len(offending), offending[0], pid=plog)
    return 2                              # blocks the stop; stderr reaches Claude


if __name__ == "__main__":
    sys.exit(main())
