#!/usr/bin/env python3
"""Stop hook —— when the MAIN agent finishes a turn, verify it obeyed the
project's NO-CHAT-TEXT discipline (root CLAUDE.md §3.2): the only chat text
permitted is the 5 declaration lines, each led by one of the glyphs
✅ ⇠ ➡️ ⚠️ 🚨. Any other non-blank line in the turn's final assistant text is
prose —— a breach.

WHY a hook, not trust: the discipline is silent to break and only caught on a
human re-read; a deterministic Stop-time scan surfaces the slip immediately
(coding.md —— back a prompt-declared invariant with cheap code enforcement).

WHAT it does, self-contained (no external state):
  1. Read the Stop-hook stdin JSON; take `transcript_path` (a JSONL file).
  2. Parse it defensively. Keep MAIN-agent lines only (`isSidechain` falsy) so a
     sub-agent's prose never counts against the main turn. Find the last GENUINE
     user message (a `user` line whose content is NOT purely tool_result blocks,
     AND not a system-injected wrapper such as a task-notification or
     local-command echo that Claude Code appends as a `type: "user"` turn with
     no human behind it —— see `_is_real_user`), then scan every assistant text
     block AFTER it —— the final turn's chat.
  3. Flag a breach if any assistant text line, after leading whitespace, is
     non-blank yet does NOT begin with one of the 5 glyphs. Tolerated: a blank
     line; a markdown horizontal-rule / chapter divider (`---`/`***`/`___`); a
     `**` bold wrapper before the glyph (e.g. `**➡️ …`, per §3.2.3.3's bolded
     response_ line).

VERDICT —— BLOCK-ONCE by design. A Stop hook's `systemMessage` (exit 0) reaches
only the USER, never the model —— so a non-blocking warning can NEVER make the
agent self-correct: its turn has already ended and it never sees the note. The one
channel that reaches the MODEL on Stop is a block —— exit 2 feeds stderr back to
Claude as an error and forces exactly one more turn. So on a breach this hook
exits 2 with a terse, glyph-free stderr instruction to end the turn adding no
further prose; Claude reads it, ends cleanly, and future turns self-correct. The
event is still appended to `cscpt/.clint.log`. No breach -> exit 0, no output.

LOOP GUARD —— exit 2 forces a continuation that ends in another Stop, so an
unguarded block would loop forever. The hook honours `stop_hook_active` (set true
by the harness once Claude is already continuing because of a prior Stop-block):
when it is true the hook logs the breach but exits 0, letting the turn finally end.
Net effect —— at most ONE extra turn per stop-cycle; each fresh genuine user turn
re-arms a single enforcement shot. This deliberately blocks ONCE (the only way to
reach the model on Stop); it does not force the agent to keep producing prose ——
the message tells it to stop, and the guard guarantees the next Stop succeeds.

CRITICAL —— the stderr text carries NONE of the 5 glyphs/emoji: naming them would
teach exactly which prefixes pass and invite gaming by bolting a glyph onto prose.
`_BREACH` is a fixed, glyph-free string.

DIAGNOSTIC —— every exit from `main()` logs exactly ONE terse line via
`_log_event`, tagged by the stage reached (no_stdin / no_transcript /
unreadable_transcript / empty_transcript / clean / block / suppressed), not
only breaches. WHY: a log that writes solely on a breach can never tell "ran
this turn and found nothing" apart from "the harness never invoked this
command" —— an empty log is consistent with BOTH, which is precisely how a
dead Stop-hook wiring went unnoticed across many real sessions even though the
script itself was proven correct under direct/manual invocation. A non-growing
log across real turns is now unambiguous: the harness is not calling this
command. The extra log line never adds a leakage surface: the breach line
already logs the offending text (glyph-free by construction, see CRITICAL);
every other stage logs no user content at all.

FAIL-SAFE —— any parse error (including stdin JSON that parses but is not an
object), missing field, or unreadable transcript -> log the stage, then exit 0
silently; a linter must never break a turn on its own failure. A stderr-write
failure on the block path also falls back to exit 0, never a broken turn. The
log write itself is equally fail-safe (see `_log_event`): a full disk or a
permissions error there must never break a turn either.
(Run by the harness, not read —— see README.)"""

import sys
import os
import re
import json
from datetime import datetime

# ---------------------------------------------------------------------------
# REPO-SCOPE GUARD.
#
# WHY: this hook is registered in the USER-level ~/.claude/settings.json, not
# a project settings.json —— proven live this session that Claude Desktop
# NEVER runs project-level hooks, only user-level ones. A user-level
# registration fires for EVERY project open on this Mac, not just this repo.
# Unscoped, that is actively harmful here: this hook enforces THIS repo's
# own bespoke no-chat-prose discipline (root CLAUDE.md §3.2) and would start
# BLOCKING Stop turns in unrelated projects that never agreed to any such
# rule. So before doing anything else (bar the diagnostic log —— see the
# DIAGNOSTIC docstring section above, which this guard deliberately keeps
# alive via a distinct "out_of_scope" tag), self-scope to this repo and
# exit silently everywhere else.
#
# HOW: prefer the payload's `cwd` if present (confirmed present on a live
# PostToolUse payload captured this session; NOT yet confirmed on a real
# Stop payload, which is what THIS hook actually receives —— so the
# fallback below is a live safety net, not just theoretical). If `cwd` is
# absent, fall back to `transcript_path`'s Claude-Code project slug:
# transcripts live at `~/.claude/projects/<slug>/<uuid>.jsonl`, where
# `<slug>` is the project directory with every `/` and ` ` replaced by `-`
# (confirmed live). Compare either signal against THIS repo's own
# root/slug, derived from this script's OWN location (never a hard-coded
# path, so the repo stays portable/relocatable) —— resolving symlinks via
# `os.path.realpath` and treating a sub-path of the repo as in-scope too.
#
# FAIL-OPEN: if NEITHER field is present/parseable, run exactly as if this
# guard did not exist. An unscopeable payload is not evidence of a
# different project —— it is just a shape we cannot read —— and a lint
# that goes silently dark on ambiguity is precisely the failure this whole
# hook-migration effort exists to fix.
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
_LOG = os.environ.get("CLINT_LOG") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".clint.log")


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


def _log_event(sid, action, lines=0, first="-"):
    """Append ONE terse diagnostic line for ANY hook invocation, breach or not
    (see docstring DIAGNOSTIC). FAIL-SAFE: swallow all errors -- a logging
    failure must never break a turn (same contract as the rest of this file)."""
    try:
        with open(_LOG, "a", encoding="utf-8") as lf:
            lf.write("%s\tsession=%s\taction=%s\tlines=%d\tfirst=%s\n" % (
                datetime.now().isoformat(timespec="seconds"),
                sid, action, lines,
                str(first)[:200].replace("\t", " ").replace("\n", " ")))
    except Exception:
        pass


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
        _log_event(sid, "clean")          # clean turn -> proof-of-life, non-blocking
        return 0

    # Are we ALREADY continuing because a prior Stop-block fired? If so, blocking
    # again would loop —— log it but let the turn end (see docstring LOOP GUARD).
    active = bool(data.get("stop_hook_active"))

    # Log every breach (offending prose is glyph-free by definition, so the log
    # never leaks the passing glyphs; the stderr message is glyph-free too).
    _log_event(sid, "suppressed" if active else "block", len(offending),
               offending[0])

    if active:
        return 0                          # loop guard -> allow the stop to finish

    # Fresh stop-cycle breach: block ONCE and feed the model the reason via
    # stderr. On exit 2 the harness ignores stdout/JSON, so write to STDERR.
    try:
        sys.stderr.write(_BREACH)
    except Exception:
        return 0                          # fail-safe: never break the turn
    return 2                              # blocks the stop; stderr reaches Claude


if __name__ == "__main__":
    sys.exit(main())
