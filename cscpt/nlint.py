#!/usr/bin/env python3
"""PostToolUse hook —— numbering-continuity linter. After a CC-authored `response_`
file is written/edited, it ADVISES (never blocks) when the file's top-level
numbering RESETS to pt 1 whilst none of numbered.md's § Numbering Continuity
excuses is evident.

=== NON-CCSIM —— all you need to RUN it ===
* Run by the harness via `nlint_hook.sh` (the registered bash fast-path), never
  by hand. Registered PostToolUse (Edit|Write|MultiEdit) in the USER-level
  `~/.claude/settings.json` —— the Claude Desktop app executes user-level hooks
  and silently ignores project-level ones —— and it self-scopes: outside THIS
  repo it exits 0 silently.
* SCOPE: acts ONLY on a comms RESPONSE file —— basename = optional CP prefix +
  `response_` + exactly 12 digits + `.md`. Anything else (query_/close_/wrap_/
  code) -> exit 0, silent.
* IN: PostToolUse JSON on stdin. OUT: on a flag, JSON on stdout carrying
  `hookSpecificOutput.additionalContext` —— the one PostToolUse channel that
  reaches the model WITHOUT blocking. Silent otherwise.
* EXIT is ALWAYS 0; it never blocks (PostToolUse cannot anyway —— the write has
  already happened) and never asserts a confirmed breach.
* WHEN IT FLAGS —— all three must hold: (1) a level-1 reset appears outside
  fenced code (`## 1. `, `- 1.`, or a bare `1. `); (2) the file this response
  replies to reads as a reply itself (its first line contains `response_` or
  "reply"); (3) that query contains no same-line authorisation of a reset. Miss
  any one -> silent.
* FAIL-SAFE: any error, missing field, or an unresolvable/unreadable query ->
  exit 0 with no output.
(Run by the harness, not read —— see README.)

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WHY ADVISORY, NEVER A HARD BLOCK —— a proven false positive on real data:
numbered.md excuses a reset if ANY of (a) it is the session's 1st response, (b)
the query is NOT a reply, or (c) it is a snippet/non-response ((c) can never
apply here —— scope is `response_`-only). Whether (a) holds is SESSION-BOUNDARY
information a stateless, self-contained hook cannot see, and numbered.md itself
anticipates a reset that LOOKS like a reply yet is fine: "1st response of a
session (CC: despite referring to prev. comms files)". A real turn hit exactly
that shape —— a response textually replying to prior comms that was ALSO its
session's 1st, with the user authorising the reset in-query. The PRIOR version
treated "replies to a response" alone as a confirmed breach (RED, exit 2), which
that turn disproves. Since a stateless hook can NEVER verify (a) and cannot
reliably parse arbitrary override wording, asserting a breach is never honest ——
so this hook only ever WARNS. That turn is pinned as a regression fixture in
`cp/ccsim/sandbox/` (test file named there, not here —— scripts don't cite comms
files, per coding.md).

CHANNEL CHOICE: PostToolUse cannot block regardless of exit code, and PLAIN
exit-0 stdout/stderr text never reaches the model at all —— only STRUCTURED
exit-0 JSON (or exit-2 stderr) does. `additionalContext` is therefore the single
channel that is both non-blocking AND model-visible, i.e. exactly "a WARN that
reaches the model" rather than a silent no-op or a false assertion.

DETECTION DETAIL: fenced ```...``` blocks are masked first, so code never
false-triggers either the reset scan or the sanction scan. The trailing-space
requirement on the heading and bare forms is load-bearing: it stops a prose
decimal ("1.5 million", "## 1.5 …") reading as a reset, whilst every genuine
level-1 restart ("1." + space) still fires. The bullet form deliberately has no
such rule so a sub-number (`- 1.1.`) still matches.

REPLY-SIGNAL FAIL-SAFE: an unresolvable or unreadable referenced query counts as
"not a reply" —— absence of positive evidence must not become evidence.

SANCTION SCAN is deliberately narrow: one LINE must carry BOTH a reset word and
an authorisation word (phrasing mined from the real query's own "...reset from pt
1 (override)"). A document-wide scan would let an unrelated "override" elsewhere
legitimise an unrelated reset. A differently-worded authorisation this regex
misses simply falls through to the advisory —— the model's own judgement is the
backstop, and in the real turn it reasoned through the override correctly on its
own. Precision beats recall here: a hit suppresses a warning entirely.

REPO SCOPE (`_in_scope`): this lint advises on a convention that exists only
here, so it must stay silent elsewhere. Signals in order: the payload's `cwd` (an
absolute path, confirmed present on every real PostToolUse payload captured
live), else the `~/.claude/projects/<slug>/<uuid>.jsonl` transcript slug (the
project dir with every `/` and ` ` replaced by `-`). Both are compared against
values derived from this script's OWN location, never a hard-coded path, so the
repo stays relocatable; symlinks are resolved and a sub-path counts as in-scope.
It FAILS OPEN when neither signal is usable —— an unreadable payload is not
evidence of a different project, and a lint that goes silently dark on ambiguity
is the failure this whole wiring exists to fix.
"""

import sys
import os
import re
import json

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

    if not _in_scope(data):
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
