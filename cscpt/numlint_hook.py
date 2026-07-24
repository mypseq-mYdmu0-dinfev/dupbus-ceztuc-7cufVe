#!/usr/bin/env python3
"""PostToolUse hook —— after a CC-authored `response_` file is written/edited,
flag a possible "Numbering Continuity" breach (numbered.md § Optimise for Reply)
where the response RESETS top-level numbering back to pt 1 whilst it is actually
REPLYING to a prior response (the one prohibited condition —— continuing at n+1
is the default, resetting is allowed only for a fresh/non-reply turn).

Why a mechanical check rather than trusting the instruction: a reset-vs-continue
mistake is silent and only caught on a later human re-read; a tiny deterministic
regex catches the common, high-signal case at write time (per coding.md —— back a
prompt-declared invariant with cheap code enforcement).

How it decides (all self-contained, no external state):
  1. Scope —— acts ONLY on a comms RESPONSE file: basename = optional CP prefix
     (e.g. `ccsim_`) + `response_` + exactly 12 digits + `.md`. Anything else
     (query_/close_/wrap_/code/etc.) -> exit 0 silently. This is deliberately
     NARROWER than dlint (which also lints close_/wrap_): continuity-reset only
     has meaning for a `response_`.
  2. Reset —— after masking fenced code blocks (```...```) so code never
     false-triggers, a body line that (ignoring leading whitespace) begins a
     level-1 count at 1: a heading `## 1.`, a bullet `- 1.1.`, or a bare `1.`.
  3. Reply-signal —— read the response's first line `# Response to <FILE>`, take
     <FILE> as the trimmed remainder after `Response to `, open that file in the
     SAME directory, and read ITS first line. The turn "replies to a response"
     (making a reset a breach) when that first line contains `response_`
     (case-insensitive) OR matches `[Rr]eply`. (Refined from a cruder "contains
     `re`" so ordinary words containing `re` do not false-positive.)

Verdicts (mirrors dlint's block convention —— stderr + exit 2 blocks the turn so
CC sees & fixes it; exit 0 never blocks):
  * reset AND reply-signal            -> RED  : block (exit 2).
  * reset AND no reply-signal / query file absent -> YELLOW: advise (exit 0).
  * no reset                          -> silent exit 0.

FAIL-SAFE —— on ANY error, missing field, or non-match it exits 0; it can never
block on its own failure. (Run by the harness, not read —— see README.)"""

import sys
import os
import re
import json

# A comms RESPONSE file: optional CP prefix segment(s) ending in `_`
# (e.g. `ccsim_`, `career_`), then `response_`, exactly 12 digits, `.md`.
_RESPONSE_RE = re.compile(r"^(?:[A-Za-z0-9-]+_)*response_\d{12}\.md$")

# A top-level numbering RESET (numbering restarted at 1): after leading
# whitespace, an optional heading marker (`## `) OR bullet (`- `), then `1.`
# followed by whitespace, a digit (the `.1` of `1.1.`), or end-of-line.
_RESET_RE = re.compile(r"^\s*(?:#{1,6}\s+)?(?:-\s+)?1\.(?:\s|\d|$)")

# Fence delimiter line: three backticks (optionally a language), any indent.
_FENCE_RE = re.compile(r"^\s*```")

_MSG_RED = (
    "You might have reset pt no. in prohibited conditions "
    "(per numbered.md) —— renumber accordingly."
)
_MSG_YELLOW = 'Remember "Numbering Continuity" per numbered.md.'


def _read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


def _has_reset(lines):
    """True if any non-fenced body line restarts level-1 numbering at 1."""
    in_fence = False
    for ln in lines:
        if _FENCE_RE.match(ln):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if _RESET_RE.match(ln):
            return True
    return False


def _reply_signal(first_line):
    """True if a query/first-line signals this turn REPLIES to a response."""
    low = first_line.lower()
    return ("response_" in low) or bool(re.search(r"[Rr]eply", first_line))


def _referenced_filename(response_first_line):
    """Extract <FILE> from `# Response to <FILE>` (tolerate a missing `# `)."""
    s = response_first_line.lstrip()
    s = re.sub(r"^#+\s*", "", s)  # drop any leading heading hashes
    m = re.match(r"Response to\s+(.+)$", s)
    if not m:
        return ""
    return m.group(1).strip()


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    fp = (data.get("tool_input") or {}).get("file_path") or ""
    base = os.path.basename(fp)

    # Scope: response_ files only (incl. CP-prefixed). Everything else -> silent.
    if not _RESPONSE_RE.match(base):
        return 0
    if not os.path.isfile(fp):
        return 0

    try:
        lines = _read_lines(fp)
    except Exception:
        return 0

    if not _has_reset(lines):
        return 0  # continued numbering (or empty) -> nothing to flag

    # Reset present. Decide RED (breach) vs YELLOW (reminder) via the referenced
    # file's first line. Missing/unreadable referenced file -> YELLOW (can't
    # confirm a reply, so only remind).
    first_line = lines[0] if lines else ""
    ref = _referenced_filename(first_line)
    ref_path = os.path.join(os.path.dirname(os.path.abspath(fp)), ref) if ref else ""

    reply = False
    if ref_path and os.path.isfile(ref_path):
        try:
            ref_lines = _read_lines(ref_path)
            reply = _reply_signal(ref_lines[0] if ref_lines else "")
        except Exception:
            reply = False

    if reply:
        sys.stderr.write(_MSG_RED + "\n")
        return 2

    sys.stderr.write(_MSG_YELLOW + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
