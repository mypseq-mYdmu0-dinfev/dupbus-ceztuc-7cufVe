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

VERDICT —— NON-BLOCKING by design (variant a). A Stop hook that exits 2 (or emits
`decision:"block"`) would FORCE the agent to continue —— the opposite of what we
want. So on a breach it exits 0, surfaces a user-facing warning via the universal
`systemMessage` JSON field (shown to the user, NOT fed to the model as an
instruction), and appends the event to `cscpt/.clint_hook.log`. No breach ->
exit 0 with no output.

CRITICAL —— the warning text carries NONE of the 5 glyphs/emoji: naming them
would teach exactly which prefixes pass and invite gaming by bolting a glyph onto
prose. `_WARN` is a fixed, glyph-free string.

FAIL-SAFE —— any parse error, missing field, or unreadable transcript -> exit 0
silently; a linter must never break a turn on its own failure. (`stop_hook_active`
needs no special handling here: this hook never blocks, so it cannot induce the
stop-hook loop that flag guards against.)
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

# Fixed, GLYPH-FREE warning (see docstring CRITICAL —— must not name the glyphs).
_WARN = "No chat text except the 5 declarations (per root CLAUDE.md §3.2)."

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

    # Breach. Log it first (offending prose is glyph-free by definition, so the
    # log never leaks the passing glyphs; the user-facing WARN is glyph-free too).
    try:
        sid = str(data.get("session_id") or "")[:8]
        with open(_LOG, "a", encoding="utf-8") as lf:
            lf.write("%s\tsession=%s\tlines=%d\tfirst=%s\n" % (
                datetime.now().isoformat(timespec="seconds"),
                sid, len(offending),
                offending[0][:200].replace("\t", " ").replace("\n", " ")))
    except Exception:
        pass                              # logging must never break the turn

    # Surface the warning to the user, NON-blocking (exit 0, no decision:block).
    try:
        sys.stdout.write(json.dumps({"systemMessage": _WARN}))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
