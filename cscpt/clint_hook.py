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
     user message (a `user` line whose content is NOT purely tool_result blocks),
     then scan every assistant text block AFTER it —— the final turn's chat.
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
event is still appended to `cscpt/.clint_hook.log`. No breach -> exit 0, no output.

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

FAIL-SAFE —— any parse error, missing field, or unreadable transcript -> exit 0
silently; a linter must never break a turn on its own failure. A stderr-write
failure on the block path also falls back to exit 0, never a broken turn.
(Run by the harness, not read —— see README.)"""

import sys
import os
import re
import json
from datetime import datetime

# Base glyph codepoints (variation selectors ignored, so `➡️` and `➡` both pass).
_GLYPHS = ("✅", "⇠", "➡", "⚠", "\U0001f6a8")  # ✅ ⇠ ➡ ⚠ 🚨

# A markdown horizontal-rule / chapter divider line: 3+ of -, *, or _.
_HR_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")

# Fixed, GLYPH-FREE breach message fed to the model via stderr on exit 2 (see
# docstring CRITICAL —— must not name the glyphs, or it teaches how to game the
# check). Terse and terminal: tell the model to END the turn, not write more.
_BREACH = ("Chat-prose breach (root CLAUDE.md §3.2): emit ONLY the 5 permitted "
           "declarations. Avoid further prose.")

# Log path (overridable for tests via CLINT_LOG); default beside this script.
_LOG = os.environ.get("CLINT_LOG") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".clint_hook.log")


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
    """A genuine user prompt, not a tool_result-only `user` turn."""
    if obj.get("type") != "user":
        return False
    content = (obj.get("message") or {}).get("content")
    if isinstance(content, str):
        return True
    if isinstance(content, list):
        # A tool_result-only turn is not a prompt; any non-tool_result => genuine.
        return any(isinstance(b, dict) and b.get("type") != "tool_result"
                   for b in content)
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    tp = data.get("transcript_path") or ""
    if not tp or not os.path.isfile(tp):
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
        return 0

    if not objs:
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
        return 0                          # clean turn -> silent, non-blocking

    # Are we ALREADY continuing because a prior Stop-block fired? If so, blocking
    # again would loop —— log it but let the turn end (see docstring LOOP GUARD).
    active = bool(data.get("stop_hook_active"))

    # Log every breach (offending prose is glyph-free by definition, so the log
    # never leaks the passing glyphs; the stderr message is glyph-free too).
    try:
        sid = str(data.get("session_id") or "")[:8]
        with open(_LOG, "a", encoding="utf-8") as lf:
            lf.write("%s\tsession=%s\taction=%s\tlines=%d\tfirst=%s\n" % (
                datetime.now().isoformat(timespec="seconds"),
                sid, "suppressed" if active else "block", len(offending),
                offending[0][:200].replace("\t", " ").replace("\n", " ")))
    except Exception:
        pass                              # logging must never break the turn

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
