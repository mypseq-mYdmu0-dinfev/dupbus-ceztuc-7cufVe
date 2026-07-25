#!/usr/bin/env python3
"""PostToolUse hook —— after a CC-authored `response_` file is written/edited,
ADVISE (never hard-block) when its top-level numbering RESETS back to pt 1
whilst numbered.md's § Numbering Continuity conditions that would excuse a
reset are NOT evident. numbered.md: continuing at n+1 is the default; a
reset is legitimate if ANY of —— (a) 1st response of a session, (b) the
query is NOT a reply, or (c) a snippet/non-response (never applies here:
scope below is already `response_`-only, so every file checked IS a
response).

Why advisory, never a hard block —— a proven false positive on real data:
whether (a) holds is SESSION-BOUNDARY information this self-contained,
stateless hook (no external state, by design) cannot see. numbered.md
itself anticipates a reset that LOOKS like a reply yet is fine: "1st
response of a session (CC: despite referring to prev. comms files)". A
real reported turn hit exactly that shape —— a response textually replying
to prior comms (its query opened "# Reply to ...") that was ALSO its
session's 1st response, with the user spelling out in-query that a reset
was deliberately authorised this once (a "new session... override" style
remark). The PRIOR version of this hook treated "replies to a response"
alone as a confirmed breach (RED, exit 2) —— which is a proven false
positive on that real turn (condition (a) plus an explicit user override
both held). Since a stateless hook can NEVER verify (a), and cannot
reliably parse arbitrary override wording, asserting "confirmed breach" is
never honest —— so this hook now only ever WARNS, and does so via the
channel that reaches the model WITHOUT blocking (see §5 below). That real
turn is pinned as a regression fixture/test (see `cp/ccsim/sandbox/` —— not
named here; scripts don't cite specific comms files, per coding.md).

How it decides (self-contained, no external state):
  1. Scope —— acts ONLY on a comms RESPONSE file: basename = optional CP
     prefix (e.g. `ccsim_`) + `response_` + exactly 12 digits + `.md`.
     Anything else (query_/close_/wrap_/code/etc.) -> exit 0 silently.
  2. Reset —— after masking fenced code blocks (```...```) so code never
     false-triggers, a body line that (ignoring leading whitespace) begins
     a level-1 count at 1 in one of three forms: a heading `## 1. `
     (trailing space REQUIRED), a bullet `- 1.` (e.g. `- 1.1.`, no
     trailing-space rule so sub-numbers still match), or a bare `1. `
     (trailing space REQUIRED, so a prose decimal such as "1.5 million"
     is NOT a false positive). No reset -> exit 0 silently (nothing to
     check).
  3. Reply-signal —— read the response's first line `# Response to <FILE>`,
     take <FILE> as the trimmed remainder, open that file in the SAME
     directory, and read ITS first line. Condition (b) ("NOT a reply") is
     satisfied —— confidently, this IS checkable —— when that first line
     does NOT contain `response_` (case-insensitive) and does NOT match
     `[Rr]eply`; also treated as satisfied (fail-safe) if the referenced
     file cannot be found/read at all, since there is then no positive
     evidence of a reply either. Either way -> exit 0 silently.
  4. Sanctioned —— reply-signal DID fire (this genuinely reads as a
     reply), so the ONLY remaining excuse is condition (a) or an explicit
     user exception. Scan the QUERY body (fence-masked) for a line naming
     BOTH a numbering-reset word (reset/restart/"pt 1"/"point 1") AND an
     authorisation word (override/new session/fresh session/1st
     response/session start) —— the concrete, same-line co-occurrence
     that IS cheaply checkable, extracted from the real reported query's
     own phrasing ("...reset from pt 1 (override)"). Found -> confirmed
     legitimate -> exit 0 silently. This is deliberately narrow
     (same-line, not whole-document) —— a document-wide scan risks an
     unrelated "override" elsewhere legitimising an unrelated reset. A
     differently-worded authorisation this regex misses simply falls
     through to §5 —— the model's own judgement is the backstop (it
     already, in the real reported turn, correctly reasoned through the
     override on its own).
  5. Otherwise -> ADVISORY. A reset with no evidence excusing it is only
     ever a MAYBE (this hook cannot rule out an unusually-worded (a) or an
     override it didn't recognise) —— so it never asserts a breach and
     never hard-blocks. It surfaces via exit 0 + structured stdout
     (`hookSpecificOutput.additionalContext`), which Claude Code's own
     PostToolUse contract delivers to the model as a system-reminder next
     to the tool result WITHOUT blocking (docs: code.claude.com/docs/en/
     hooks —— PostToolUse "cannot block, the tool already ran" even on
     exit 2, and PLAIN exit-0 stdout/stderr text is never shown to the
     model at all, only STRUCTURED JSON is). This is the one channel that
     is both non-blocking AND model-visible, i.e. exactly a "WARN that
     reaches the model" rather than either a silent no-op or a false
     assertion.

FAIL-SAFE —— on ANY error, missing field, or non-match it exits 0 with NO
output; it can never block (PostToolUse cannot, regardless), and it can
never manufacture certainty it doesn't have. (Run by the harness, not
read —— see README.)"""

import sys
import os
import re
import json

# A comms RESPONSE file: optional CP prefix segment(s) ending in `_`
# (e.g. `ccsim_`, `career_`), then `response_`, exactly 12 digits, `.md`.
_RESPONSE_RE = re.compile(r"^(?:[A-Za-z0-9-]+_)*response_\d{12}\.md$")

# A top-level numbering RESET (numbering restarted at 1): after leading
# whitespace, ANY of three forms —
#   (i)   heading  `#{1,6}\s+1\.\s`  e.g. "## 1. " — trailing space REQUIRED
#   (ii)  bullet   `-\s+1\.`         e.g. "- 1.1.", "- 1. ", "  - 1." — no
#         trailing-space rule, so a sub-number like `1.1` still matches
#   (iii) bare     `1\.\s`           e.g. "1. text" — trailing space REQUIRED,
#         so a prose decimal like "1.5 million" does NOT false-trigger
# The trailing-space requirement on (i)/(iii) is precisely what stops a prose
# decimal ("1.5 million", "## 1.5 …") reading as a reset, whilst every genuine
# level-1 restart still fires (a real reset is always "1." + space/newline).
_RESET_RE = re.compile(r"^\s*(?:#{1,6}\s+1\.\s|-\s+1\.|1\.\s)")

# Fence delimiter line: three backticks (optionally a language), any indent.
_FENCE_RE = re.compile(r"^\s*```")

# §4 Sanctioned —— two independent, same-line co-occurring signals mined
# directly from the real reported query's own wording ("...you may reset
# from pt 1 (override)"). Deliberately a cheap keyword pair, NOT full NLP —
# a miss here is safe (falls through to the ADVISORY tier below), a hit
# suppresses a warning entirely, so precision (same line) matters more than
# recall (catching every possible phrasing).
_AUTH_WORD_RE = re.compile(
    r"\b(override|new session|fresh session|first response|1st response|"
    r"session start|new chat)\b",
    re.IGNORECASE,
)
_RESET_WORD_RE = re.compile(
    r"\b(reset|restart)\b|\bpt\.?\s*1\b|\bpoint\s*1\b",
    re.IGNORECASE,
)

_MSG_TEMPLATE = (
    "nlint: numbering reset detected ({snippet!r}) in a response whose "
    "query ({ref}) reads as a reply to a prior response. Per numbered.md, "
    "a reset is legitimate only if this is the session's 1st response or "
    "the user explicitly authorised it —— neither is evident in the query "
    "text. Confirm one genuinely applies (in which case no action is "
    "needed); if NOT, renumber this response to continue at n+1 from the "
    "prior response's last point."
)


def _read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


def _iter_unfenced(lines):
    """Yield lines with fenced ```...``` code blocks masked out, so neither
    reset-detection nor sanction-detection ever fires on code content."""
    in_fence = False
    for ln in lines:
        if _FENCE_RE.match(ln):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        yield ln


def _find_reset_line(lines):
    """Return the first non-fenced body line that restarts level-1
    numbering at 1, or None if numbering never resets."""
    for ln in _iter_unfenced(lines):
        if _RESET_RE.match(ln):
            return ln
    return None


def _reply_signal(first_line):
    """True if a query/first-line signals this turn REPLIES to a response."""
    low = first_line.lower()
    return ("response_" in low) or bool(re.search(r"[Rr]eply", first_line))


def _sanctioned(query_lines):
    """True if the query (fence-masked) has a line naming BOTH a
    numbering-reset word and an authorisation word —— the two checkable
    proxies for "this reset is legitimate" (see module docstring §4)."""
    for ln in _iter_unfenced(query_lines):
        if _AUTH_WORD_RE.search(ln) and _RESET_WORD_RE.search(ln):
            return True
    return False


def _referenced_filename(response_first_line):
    """Extract <FILE> from `# Response to <FILE>` (tolerate a missing `# `)."""
    s = response_first_line.lstrip()
    s = re.sub(r"^#+\s*", "", s)  # drop any leading heading hashes
    m = re.match(r"Response to\s+(.+)$", s)
    if not m:
        return ""
    return m.group(1).strip()


def _emit_advisory(reset_line, ref):
    """Exit 0 + structured stdout so Claude Code delivers `additionalContext`
    to the model as a non-blocking system-reminder (see module docstring
    §5) —— a WARN that actually reaches the model, without asserting a
    breach the hook cannot confirm, and without blocking (PostToolUse
    cannot block regardless of exit code —— the write already happened)."""
    snippet = reset_line.strip()
    if len(snippet) > 80:
        snippet = snippet[:77] + "..."
    msg = _MSG_TEMPLATE.format(snippet=snippet, ref=ref)
    payload = {
        "suppressOutput": True,
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": msg,
        },
    }
    print(json.dumps(payload))


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

    reset_line = _find_reset_line(lines)
    if reset_line is None:
        return 0  # continued numbering (or empty) -> nothing to check

    # Reset present. §3 Reply-signal: resolve the file this response replies
    # to via its own first line, then check THAT file's first line.
    first_line = lines[0] if lines else ""
    ref = _referenced_filename(first_line)
    ref_path = os.path.join(os.path.dirname(os.path.abspath(fp)), ref) if ref else ""

    query_lines = None
    if ref_path and os.path.isfile(ref_path):
        try:
            query_lines = _read_lines(ref_path)
        except Exception:
            query_lines = None

    if not query_lines:
        return 0  # can't resolve/read the query -> no positive reply evidence

    if not _reply_signal(query_lines[0] if query_lines else ""):
        return 0  # query doesn't read as a reply -> condition (b) satisfied

    # §4 Sanctioned: reply-signal fired, so only (a)/explicit-override can
    # excuse this reset. Scan the FULL query body (not just line 1) for it.
    if _sanctioned(query_lines):
        return 0  # confirmed legitimate -> silent

    # §5: reset + reply-signal + no sanction evident -> ADVISORY (never RED).
    _emit_advisory(reset_line, ref)
    return 0


if __name__ == "__main__":
    sys.exit(main())
