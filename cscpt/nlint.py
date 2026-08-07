#!/usr/bin/env python3
"""Numbering Linter (PostToolUse hook)

THREE INDEPENDENT checks: two ADVISORY ones enforcing `universal/numbered.md`,
and one BLOCKING one enforcing `universal/glossary.md`'s question/blocker
labelling rule. A file may trip any combination of the three.

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: a PostToolUse hook, THREE independent checks, any combination. A/B
  ADVISE (exit 0); C BLOCKS (exit 2) —— the write already happened, so C means:
  EDIT that file.
* A —— TENTH SIBLING (numbered.md): a level's 10th item (`- [n].10.`), since ⌘F
  `[n].1` also hits it. FIX: SPLIT that level, or renumber `[n].01`–`[n].09`.
  Any file bar code/system types.
* B —— NUMBERING RESET (numbered.md): a `response_` restarting at pt 1 unexcused.
  FIX: continue the count, or say why.
* C —— QB LABEL (glossary.md): `QB1` or `QB:`, ANY file. FIX: relabel `Q[n]` /
  `B[n]`; backtick a deliberate mention.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WIRING (kept here, not in NON-CCSIM: nobody invokes this file by hand, so the
plumbing serves only an editor). Run by the harness via `nlint_hook.sh`, the
registered bash fast-path; registered PostToolUse (Edit|Write|MultiEdit) in the
USER-level `~/.claude/settings.json` —— the Claude Desktop app executes
user-level hooks and silently ignores project-level ones —— and it self-scopes,
exiting 0 silently outside THIS repo. IN: PostToolUse JSON on stdin. OUT:
whichever tier fired. ADVISORY ONLY (A and/or B) -> exit 0 with JSON on stdout
carrying `hookSpecificOutput.additionalContext`, the one PostToolUse channel
that reaches the model WITHOUT blocking; both advisories share ONE payload, one
line each. BLOCKING (C, alone or alongside A/B) -> exit 2 with the text on
STDERR, because at exit 2 the harness ignores stdout and JSON ENTIRELY —— so any
advisory that fired in the same run rides along on stderr rather than being
silently discarded, which is why the two tiers are assembled separately and
emitted once. Neither exit code undoes the write (PostToolUse never can); exit 2
buys error framing and model attention, not a rollback. FAIL-SAFE: any error,
missing field, oversized/unreadable file, or an unresolvable/unreadable query ->
exit 0, no output —— a failure in any one check can never suppress another, and
can never manufacture a block.

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
silent. CHECK C covers LITERALLY every file, with no extension carve-out at all
(see CHECK C —— WHY EVERY FILE).

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

CHECKS A AND C —— WHY THE SHIM HAD TO WIDEN, TWICE. The `nlint_hook.sh`
fast-path used to exit before Python unless the payload mentioned `response_`;
that gate would have suppressed Check A on every non-response file, and Check C
on nearly every file there is. The gate now ALSO passes a payload whose written
text carries a bullet-digit plus `.10` (A), or a merged/unnumbered QB label (C)
—— rationale for those specific patterns, and for gating on payload text rather
than disk, lives in the shim itself.

CHECK C —— WHAT IT ENFORCES. `universal/glossary.md` defines QB as
"question/blocker" and mandates that any questions and blockers be raised
SEPARATELY and numbered —— `Q1`, `Q2` for questions, `B1`, `B2` for blockers ——
and NEVER merged into a single `QB1`/`QB2` label. Two shapes are therefore
refused: `QB` immediately followed by a digit (the merged label the rule names
outright), and `QB` immediately followed by a colon (worse still, since that one
is not even numbered, so the reader cannot refer to an individual item at all).
Two lookalikes are deliberately PERMITTED, because neither is a label: a bare
`QB` with no digit and no colon (the abbreviation used as a noun, "confirmed no
QB"), and `QBs:` (a plural heading introducing a properly-numbered enumeration,
"Here are QBs: ..."). Matching is UPPERCASE-only: lowercase `qb` is the user's
own shorthand for the CONCEPT (glossary usage, e.g. "[task], qb"), whilst the
label form the rule forbids is always uppercase.

CHECK C —— WHY IT BLOCKS WHERE A AND B ONLY ADVISE. A and B both hinge on
information a stateless hook cannot fully see (session boundaries, whether a
long level was deliberate), so asserting a breach there would sometimes be a
lie. This rule has no such gap: the glossary states it absolutely, with no
excusing condition anywhere, so a genuine `QB1`/`QB:` in a written file IS a
breach and can be asserted as one. Exit 2 cannot un-write the file —— nothing on
PostToolUse can —— so the message must not read as a veto; it names the file and
tells the model to go and EDIT it, which is the only remedy that exists after
the fact.

CHECK C —— WHY EVERY FILE, INCLUDING CODE. Check A carves out code/system
extensions because numbered.md's own § Format disclaims them. glossary.md
carves out nothing: it governs how CC LABELS a question or blocker wherever one
is raised, and a malformed label is just as unreadable in a `.txt` note, a
`slog_`, a deliverable or a script comment as in a `response_`. Inheriting A's
exemption list would therefore import an exemption this rule never granted. The
cost is real and accepted: a `.py` fixture holding a literal merged label fires
too, which is precisely why this file and its regression test either backtick
such literals or assemble them from fragments.

CHECK C —— FALSE POSITIVES, AND THE TWO ESCAPE HATCHES. The forbidden strings
appear legitimately in the very files that DEFINE or discuss the rule ——
glossary.md's own entry, its backups, and any response reasoning about it. A
fence mask alone does not save them: those mentions sit in ordinary prose, not
in code blocks. So two independent hatches apply, and either one alone clears a
line:
(1) MASKED MENTION —— fenced ```...``` blocks (already masked for A and B) plus
    INLINE `` `...` `` spans are removed before the scan. A backticked token is
    a mention, not a use; this is also the fix the block message offers, so the
    remedy is always available and is correct Markdown besides.
(2) RULE STATEMENT —— a line carrying a same-line PROHIBITION word (`never`,
    `forbid`, `prohibit`, `disallow`, `banned`, `must not`, `do not`, `don't`,
    `instead of`, `rather than`, `mislabel`, `malformed`) is stating the rule,
    not breaching it: glossary.md's line reads "NEVER label as QB1, QB2". Same
    same-line co-occurrence design as the § Sanctioned scan below, and for the
    same reason —— a document-wide scan would let one distant "never" launder
    every bad label in the file.
Mined against this repo's whole history, that pair acquits every genuine
rule-discussion line found and still fires on every genuine breach found (real
ones include `QB:` alone on a line, `22. QB:`, `- 56.3. QB: pt 52.4 ——`, and
`⚠️ QB1 ——`). Bare negators (`not`, `no`) are excluded from (2) on purpose:
"..., not your message's ..." appears in a REAL breach line, and admitting them
would have acquitted it. The residual gap is stated plainly rather than papered
over —— a genuine bad label on a line that also happens to say "never" escapes.
That direction is chosen deliberately: a missed label is a silent, recoverable
imperfection, whereas a wrongly-blocked write of the glossary makes the rule
itself unwritable and invites the model to mangle a protocol file to appease a
lint.

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
import io
import select
import stat
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

# CHECK C —— the malformed question/blocker label glossary.md forbids: `QB`
# IMMEDIATELY followed by a digit (the merged label) or by a colon (the
# unnumbered form). The word boundary stops a longer token (`SQB1`) matching,
# and requiring the digit/colon to be IMMEDIATE is what keeps the permitted
# lookalikes silent: bare `QB` (no digit, no colon) and `QBs:` both fail here,
# since `s` is neither. Uppercase-only by design —— see CHECK C —— WHAT IT
# ENFORCES in the docstring. The whole match is reported back, so the message
# can name the exact token found.
_QB_RE = re.compile(r"\bQB(?:\d+|:)")

# CHECK C escape hatch (2) —— a same-line PROHIBITION word means the line is
# STATING the rule, not breaching it (glossary.md: "NEVER label as ..."). Bare
# negators (`not`, `no`) are deliberately absent: they are common enough inside
# a real question/blocker body to acquit genuine breaches.
_QB_RULE_WORD_RE = re.compile(
    r"\bnever\b|\bforbid\w*|\bprohibit\w*|\bdisallow\w*|\bbanned\b|"
    r"\bmust not\b|\bdo not\b|\bdon't\b|\binstead of\b|\brather than\b|"
    r"\bmislabel\w*|\bmalformed\b",
    re.IGNORECASE,
)

# CHECK C escape hatch (1), inline half —— a backticked span. Fenced blocks are
# already masked for every check; this removes INLINE code too, but ONLY inside
# the QB scan, so checks A and B keep their existing behaviour byte for byte.
_INLINE_CODE_RE = re.compile(r"`[^`]*`")

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

# CHECK C's message. It is a BLOCK, so it must be unambiguous about the one
# thing a PostToolUse hook cannot do: the file is already written. Hence it
# names the file, quotes the offending line, gives the exact replacement
# labelling, and offers the mention escape hatch, so a reader who was quoting
# the rule on purpose has an immediate, correct remedy rather than a standoff.
_QB_MSG_TEMPLATE = (
    "nlint 🔴 BLOCK —— malformed question/blocker label {token!r} in "
    "`{base}` ({snippet!r}). universal/glossary.md: QB = question/blocker, and "
    "questions and blockers must be raised SEPARATELY and #numbered —— `Q1`, "
    "`Q2` for questions, `B1`, `B2` for blockers —— NEVER merged into one "
    "`QB[n]` label, and never an unnumbered `QB` + colon. This hook runs AFTER "
    "the write, so the bad label is already on disk and nothing was undone: "
    "EDIT `{base}` NOW and relabel each item `Q[n]` or `B[n]` before "
    "continuing. If you were deliberately QUOTING the forbidden form (writing "
    "about the rule rather than using it), wrap the mention in backticks or a "
    "code fence —— a masked mention never fires."
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


def _find_qb(body):
    """CHECK C. Return `(line, token)` for the first fence-masked line carrying
    a malformed question/blocker label, or None.

    Two acquittals apply per line, either sufficient alone (docstring CHECK C
    —— FALSE POSITIVES): a same-line prohibition word means the line STATES the
    rule, and inline backticked spans are stripped before the scan so a quoted
    mention is invisible to it. The prohibition test reads the RAW line, so a
    prohibition word that itself sits in backticks still counts —— acquitting is
    the safe direction here. One pass, first hit wins; the ORIGINAL line is
    returned as the snippet so the reader sees what they actually wrote.

    Lines carrying U+FFFD are skipped. `_read_lines` decodes with
    `errors="replace"`, so that character means the bytes were never text, and
    this check has NO extension carve-out to fall back on: sweeping the repo
    showed every `.icns` application stub decoding to a literal QB-plus-digit,
    purely by byte coincidence. Two other guards already make that unreachable
    in practice (the shim gates on payload text, and no agent Writes a binary),
    so this is defence in depth rather than the primary defence —— but a
    BLOCKING check must not have any plausible route to blocking on noise."""
    for ln in body:
        if "�" in ln:
            continue
        if _QB_RULE_WORD_RE.search(ln):
            continue
        m = _QB_RE.search(_INLINE_CODE_RE.sub(" ", ln))
        if m:
            return ln, m.group(0)
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


def _emit_block(blocking, advisories):
    """Exit-2 channel for CHECK C. At exit 2 the harness ignores stdout and JSON
    ENTIRELY, so everything the model must see goes to STDERR —— including any
    ADVISORY that fired in the same run, which would otherwise be silently
    dropped purely because a different check blocked. Blocking lines lead, since
    they are the ones demanding an action.

    Returns the exit code to use. If even the stderr write fails, the block is
    abandoned rather than delivered blind: falling back to exit 0 keeps the
    fail-safe contract (a broken hook must never break a turn) and still gets
    the advisories out through their own channel."""
    try:
        sys.stderr.write("\n".join(blocking + advisories))
    except Exception:
        if advisories:
            try:
                _emit_advisory(advisories)
            except Exception:
                pass
        return 0
    return 2


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
    '  printf \'%s\' \'{"hook_event_name":"PostToolUse",'
    '"tool_name":"Write",'
    '"tool_input":{"file_path":"/abs/file.md"}}\' \\\n'
    '    | python3 cscpt/nlint.py\n'
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
        return 0

    if not _in_scope(data):
        return 0

    fp = (data.get("tool_input") or {}).get("file_path") or ""
    if not fp or not os.path.isfile(fp):
        return 0
    base = os.path.basename(fp)

    # Per-check scope, evaluated independently so a file can trip any
    # combination of the three. CHECK B: `response_` only (incl. CP-prefixed).
    # CHECK A: any file bar the types numbered.md itself exempts. CHECK C has
    # NO scope test —— it applies to every file (glossary.md grants no
    # carve-out), which is why the "nothing to do, don't even open the file"
    # early-out that used to sit here is gone: there is now always something to
    # do. The cost is one extra read on a payload that passed the shim gate
    # but interests neither numbering check; the shim is what keeps that rare.
    want_reset = bool(_RESPONSE_RE.match(base))
    want_tenth = os.path.splitext(base)[1].lower() not in _NUMBERING_EXEMPT_EXTS

    try:
        if os.path.getsize(fp) > _MAX_FILE_BYTES:
            return 0
        lines = _read_lines(fp)
    except Exception:
        return 0

    # Fence-mask ONCE: NO check may ever fire on code-block content.
    body = list(_iter_unfenced(lines))

    messages = []   # ADVISORY tier (checks A and B) -> exit 0, stdout JSON
    blocking = []   # BLOCKING tier (check C) -> exit 2, stderr

    if want_tenth:
        try:
            hit = _find_tenth(body)
            if hit:
                line, parent = hit
                messages.append(_TENTH_MSG_TEMPLATE.format(
                    snippet=_snippet(line), base=base, parent=parent))
        except Exception:
            pass  # one check failing must never suppress the others

    if want_reset:
        try:
            msg = _reset_message(fp, lines, body)
            if msg:
                messages.append(msg)
        except Exception:
            pass

    try:                                  # CHECK C —— unconditional, see above
        hit = _find_qb(body)
        if hit:
            line, token = hit
            blocking.append(_QB_MSG_TEMPLATE.format(
                token=token, base=base, snippet=_snippet(line)))
    except Exception:
        pass  # a failed block is a SILENT one —— never a false block, and never
        # a reason to suppress the advisories already gathered above

    if blocking:
        return _emit_block(blocking, messages)
    if messages:
        _emit_advisory(messages)
    return 0


if __name__ == "__main__":
    sys.exit(main())
