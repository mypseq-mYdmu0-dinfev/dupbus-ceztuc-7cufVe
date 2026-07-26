#!/usr/bin/env python3
"""PostToolUse hook —— numbering linter for `universal/numbered.md`. TWO
INDEPENDENT advisory checks: a file may trip one, the other, both, or neither.
Both only ever ADVISE; neither ever blocks.

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: a PostToolUse hook enforcing `universal/numbered.md`. TWO independent
  ADVISORY checks; a file may trip either, both, or neither. Neither blocks nor
  asserts a breach.
* CHECK A —— TENTH SIBLING fires at a level's 10th item (`- [n].10.`), because
  ⌘F `[n].1` then also hits `[n].10`, `[n].11`, ... FIX: SPLIT that level into
  separate points (preferred), or renumber 2-digit (`[n].01`–`[n].09`). Any file
  bar code/system types.
* CHECK B —— NUMBERING RESET fires when a `response_` restarts top-level
  numbering at pt 1 with no § Numbering Continuity excuse. FIX: continue the
  count, or say why the reset is warranted.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WIRING (kept here, not in NON-CCSIM: nobody invokes this file by hand, so the
plumbing serves only an editor). Run by the harness via `nlint_hook.sh`, the
registered bash fast-path; registered PostToolUse (Edit|Write|MultiEdit) in the
USER-level `~/.claude/settings.json` —— the Claude Desktop app executes
user-level hooks and silently ignores project-level ones —— and it self-scopes,
exiting 0 silently outside THIS repo. IN: PostToolUse JSON on stdin. OUT: on a
flag, JSON on stdout carrying `hookSpecificOutput.additionalContext`, the one
PostToolUse channel that reaches the model WITHOUT blocking; both checks share
ONE payload, one line each. EXIT is ALWAYS 0 —— PostToolUse cannot block anyway,
the write has already happened. FAIL-SAFE: any error, missing field,
oversized/unreadable file, or an unresolvable/unreadable query -> exit 0, no
output.

EXACT SCOPES AND GATES. CHECK A covers ANY file, comms or not, EXCEPT the types
numbered.md itself exempts (code/system extensions —— `_NUMBERING_EXEMPT_EXTS`),
and stays silent when that level is ALREADY 2-digit (a sibling `- [n].0X.`
exists), since `[n].10` is then the remedy working rather than a breach. CHECK B
covers a comms RESPONSE file only —— basename = optional CP prefix + `response_`
+ exactly 12 digits + `.md`; query_/close_/wrap_/code are never reset-checked ——
and flags only when all three hold: (1) a level-1 reset appears outside fenced
code (`## 1. `, `- 1.`, or a bare `1. `); (2) the file this response replies to
reads as a reply itself (its first line contains `response_` or "reply"); (3)
that query carries no same-line authorisation of a reset. Miss any one ->
silent.

CHECK A —— WHY THIS EXACT SHAPE. numbered.md mandates a dot between number and
text (`1.1. xxx`, never `1.1 xxx`), and THAT dot is what separates a numbered
item from a prose decimal. So `.10` must be followed by a `.` or by end-of-line:
"- 3.10. Foo" fires, whilst "- 3.10 metres" (a measurement, a price, a version)
stays silent —— the false positive to fear here is nagging ordinary prose, since
`X.10` is a far more common decimal than a genuine 10th sibling. `[n]` is a
dotted numeric prefix of ANY depth, so a nested "- 1.2.10." fires too, whilst
"- 10.1." does not (its level-2 counter is only at 1). "- 3.100." is likewise
unmatched: a level that deep necessarily passed `.10` earlier, so the reminder
was already due then. Missed the other way, deliberately: an item numbered
WITHOUT its mandatory dot ("- 3.10 foo") goes unflagged —— that already breaches
a different numbered.md rule, and a silent miss is the harmless direction.
Level-1 (`## 10.` / `10. `) is out of scope on purpose —— continuing at pt 10 is
the NORMAL state of a long-running session under § Numbering Continuity, so
flagging it would fire on nearly every mature response.

CHECK A —— WHY NOT LITERALLY EVERY FILE. numbered.md § Format exempts
"deliverables, codes (.py/.sh/etc.), and system files (.json/etc.)". Firing
there would enforce a rule its own protocol says does not apply, so exempt
extensions are skipped. Extension is the only slice of that carve-out a
stateless hook can see: a deliverable written as .md is indistinguishable from
a response and is tolerated as a possible (one-line, non-blocking) false hit.

CHECK A —— WHY IT STOPS NAGGING. Once the 2-digit fallback is applied the level
reads `[n].01 … [n].09, [n].10`, at which point `[n].10.` is CORRECT ——
numbered.md says so outright ("If `[N].01` is seen, `[N].10` (at least) is
expected").
So a sibling `- [n].0X.` anywhere in the same file suppresses the advisory for
that `[n]`. Without it the hook would nag hardest at the file that already took
its advice.

CHECK A —— WHY THE SHIM HAD TO WIDEN. The `nlint_hook.sh` fast-path used to exit
before Python unless the payload mentioned `response_`; that gate would have
suppressed Check A on every non-response file. The gate now ALSO passes a
payload whose written text carries a bullet-digit plus `.10` —— rationale for
that specific pattern, and for gating on payload text rather than disk, lives in
the shim itself.

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
# Gates CHECK B ONLY —— CHECK A is file-type-agnostic (see below).
_RESPONSE_RE = re.compile(r"^(?:[A-Za-z0-9-]+_)*response_\d{12}\.md$")

# CHECK A scope carve-out. numbered.md § Format applies "to ALL outputs EXCEPT
# deliverables, codes (.py/.sh/etc.), and system files (.json/etc.)", so a
# numbering reminder on those enforces a rule its own protocol disclaims.
# Extension is the only slice of that exemption a stateless hook can observe.
_NUMBERING_EXEMPT_EXTS = frozenset({
    ".py", ".sh", ".bash", ".zsh", ".pl", ".rb", ".go", ".rs", ".swift",
    ".c", ".h", ".cpp", ".java", ".js", ".ts", ".jsx", ".tsx", ".css",
    ".scss", ".html", ".htm", ".applescript", ".sql",
    ".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".plist", ".xml", ".lock", ".env",
    ".pyc", ".pyo", ".so",  # compiled artefacts: text-shaped only by accident
})

# CHECK A read cap. Check B only ever opened a comms `.md`; Check A can be
# handed any path the shim let through, so bound the read —— a numbered list
# never approaches this, and nothing bigger should delay the tool call.
_MAX_FILE_BYTES = 2 * 1024 * 1024

# CHECK A —— a level's TENTH sibling: after leading whitespace, a bullet, then a
# dotted numeric prefix of any depth, then `.10` that is IMMEDIATELY followed by
# a `.` (numbered.md's mandatory number/text separator) or by end-of-line. That
# lookahead is the whole false-positive defence: "- 3.10. Foo" is an item,
# "- 3.10 metres" is a measurement. Backtracking makes `[n]` land correctly at
# any depth —— "- 1.2.10." matches with `[n]`=`1.2`, whilst "- 10.1." does not
# match at all (nothing there is a 10th sibling).
_TENTH_RE = re.compile(r"^[ \t]*-[ \t]+(\d+(?:\.\d+)*)\.10(?=\.|[ \t]*$)")

# CHECK A suppressor —— the SAME shape, but a `.0X` sibling: the 2-digit
# fallback numbered.md prescribes. Its capture is the parent, so suppression is
# keyed per level rather than per file.
_TWO_DIGIT_RE = re.compile(r"^[ \t]*-[ \t]+(\d+(?:\.\d+)*)\.0[1-9](?=\.|[ \t]*$)")

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

_TENTH_MSG_TEMPLATE = (
    "nlint: a numbered level has reached its 10th item ({snippet!r}) in "
    "`{base}`. numbered.md says AVOID 9⁺ items on a level, because searching "
    "`{parent}.1` also surfaces `{parent}.10`, `{parent}.11`, etc. Two valid "
    "remedies: (1) SPLIT into separate points —— e.g. move the overflow under "
    "the next top-level pt —— so no level exceeds 9; or (2) make THAT level "
    "2-digit ({parent}.01–{parent}.09, then {parent}.10). Owner softly PREFERS "
    "(1): it is cleaner, whilst (2) is clumsier though perfectly valid. "
    "Non-blocking —— if 9⁺ siblings are genuinely unavoidable, take (2)."
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


def _find_reset_line(body):
    """CHECK B. Return the first fence-masked body line that restarts level-1
    numbering at 1, or None if numbering never resets."""
    for ln in body:
        if _RESET_RE.match(ln):
            return ln
    return None


def _find_tenth(body):
    """CHECK A. Return `(line, parent)` for the first fence-masked bullet that
    numbers a level's 10th sibling (`- [n].10.`), or None.

    Suppressed when that same level is ALREADY in the 2-digit form numbered.md
    prescribes as the fallback —— i.e. a sibling `- [n].0X.` exists —— because
    `[n].10` is then the remedy working as intended, not a breach. Suppression
    is keyed on the hit's OWN parent, so an unrelated 2-digit level elsewhere
    in the file can never launder a genuine breach. Both sweeps are single
    passes over the same list (never a nested re-scan per hit), so cost stays
    linear even on a long document full of near-misses —— this runs inside a
    PostToolUse hook, where any added latency is paid on every write."""
    two_digit_parents = set()
    hits = []
    for ln in body:
        m = _TWO_DIGIT_RE.match(ln)
        if m:
            two_digit_parents.add(m.group(1))
            continue
        m = _TENTH_RE.match(ln)
        if m:
            hits.append((ln, m.group(1)))
    # EVERY hit is kept, not just the first: one level having taken the 2-digit
    # remedy must not excuse a DIFFERENT level that has not.
    for ln, parent in hits:
        if parent not in two_digit_parents:
            return ln, parent
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


def _snippet(line):
    """Echo the offending line back, bounded, so the reader can dismiss a
    false positive at a glance without re-opening the file."""
    s = line.strip()
    return s if len(s) <= 80 else s[:77] + "..."


def _emit_advisory(messages):
    """Exit 0 + structured stdout so Claude Code delivers `additionalContext`
    to the model as a non-blocking system-reminder —— a WARN that actually
    reaches the model, without asserting a breach the hook cannot confirm, and
    without blocking (PostToolUse cannot block regardless of exit code —— the
    write already happened). Both checks share this ONE payload, one line each,
    because a second emission would simply be discarded."""
    payload = {
        "suppressOutput": True,
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "\n".join(messages),
        },
    }
    print(json.dumps(payload))


def _reset_message(fp, lines, body):
    """CHECK B end-to-end: returns the advisory message, or None when the reset
    is absent or legitimate. Every early return is a deliberate acquittal ——
    absence of positive evidence must never become evidence of a breach."""
    reset_line = _find_reset_line(body)
    if reset_line is None:
        return None  # continued numbering (or empty) -> nothing to check

    # Reset present. Reply-signal: resolve the file this response replies to
    # via its own first line, then check THAT file's first line.
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
        return None  # can't resolve/read the query -> no positive reply evidence

    if not _reply_signal(query_lines[0] if query_lines else ""):
        return None  # query doesn't read as a reply -> condition (b) satisfied

    # Sanctioned: reply-signal fired, so only "1st of session"/explicit override
    # can excuse this reset. Scan the FULL query body (not just line 1) for it.
    if _sanctioned(query_lines):
        return None  # confirmed legitimate -> silent

    # Reset + reply-signal + no sanction evident -> ADVISORY (never RED).
    return _MSG_TEMPLATE.format(snippet=_snippet(reset_line), ref=ref)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    if not _in_scope(data):
        return 0

    fp = (data.get("tool_input") or {}).get("file_path") or ""
    if not fp or not os.path.isfile(fp):
        return 0
    base = os.path.basename(fp)

    # Per-check scope, evaluated independently so a file can trip one, the
    # other, both, or neither. CHECK B: `response_` only (incl. CP-prefixed).
    # CHECK A: any file bar the types numbered.md itself exempts.
    want_reset = bool(_RESPONSE_RE.match(base))
    want_tenth = os.path.splitext(base)[1].lower() not in _NUMBERING_EXEMPT_EXTS
    if not (want_reset or want_tenth):
        return 0  # nothing to do -> don't even open the file

    try:
        if os.path.getsize(fp) > _MAX_FILE_BYTES:
            return 0
        lines = _read_lines(fp)
    except Exception:
        return 0

    # Fence-mask ONCE: neither check may ever fire on code-block content.
    body = list(_iter_unfenced(lines))

    messages = []

    if want_tenth:
        try:
            hit = _find_tenth(body)
            if hit:
                line, parent = hit
                messages.append(_TENTH_MSG_TEMPLATE.format(
                    snippet=_snippet(line), base=base, parent=parent))
        except Exception:
            pass  # one check failing must never suppress the other

    if want_reset:
        try:
            msg = _reset_message(fp, lines, body)
            if msg:
                messages.append(msg)
        except Exception:
            pass

    if messages:
        _emit_advisory(messages)
    return 0


if __name__ == "__main__":
    sys.exit(main())
