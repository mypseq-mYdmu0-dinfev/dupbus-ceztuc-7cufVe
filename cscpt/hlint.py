#!/usr/bin/env python3
"""Hashtag/Trigger Linter (UserPromptSubmit hook)

ONE job, named by the file: `#[trigger]` tokens in the prompt (and in any comms
file it names) that resolve to a `[trigger].md` in the SEARCH SCOPE below get a
NON-BLOCKING reminder to READ that file (root CLAUDE.md §7.3.1: a `#[trigger]`
MUST be resolved by reading its file, never guessed).

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: a UserPromptSubmit hook, ADVISORY —— never blocks. Each `#[trigger]`
  gets a line naming its protocol file (root CLAUDE.md §7.3.1 —— READ it, never
  guess).
* IF IT FIRES: read that file, or declare why not.
* BACKTICKED NAMES DON'T FIRE: a `#name`, fence or filename in backticks is
  DISCUSSED, not invoked. Only a bare token fires.
* BLIND SPOT: triggers resolve only under `universal/`, `cp/`,
  `AJAP_repo/protocols/`, `AJAP_repo/inv/inveng.md`. Silence is not proof.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WIRING (kept here, not in NON-CCSIM: a caller never invokes this file, so the
plumbing is dead weight to everyone but an editor). Registered as a
`UserPromptSubmit` hook in the USER-level `~/.claude/settings.json` —— the
Claude Desktop app executes user-level hooks and silently ignores project-level
ones. IN: UserPromptSubmit JSON on stdin (field `prompt`). OUT: on a match, JSON
on stdout carrying `hookSpecificOutput.additionalContext`, one line per matched
trigger; no match -> no output. EXIT is ALWAYS 0, and it never emits
`decision:"block"` —— for UserPromptSubmit that would ERASE the user's prompt.
SCAN CORPUS: the prompt text PLUS the content of any `*.md` file it names,
exactly ONE level deep, never recursive. SEARCH SCOPE, in priority order:
`universal/` (canonical home of most triggers), `cp/` (recursive, CP-local),
`AJAP_repo/protocols/` (recursive), then `AJAP_repo/inv/inveng.md` alone ——
`inv/` is NEVER walked. Anything else, notably `sessions/`, is out of scope.
FAIL-SAFE: any error, missing field, absent directory or unreadable file ->
exit 0, no output; it must never break or delay a prompt on its own failure.

WHY A HOOK, NOT TRUST: forgetting to read a trigger's protocol file is a silent,
high-cost slip (running `#replace`/`#debate` from a guessed meaning). A
deterministic prompt-time scan names the right file BEFORE the turn starts.

WHY NO REPO-SCOPE GUARD, unlike clint/dlint_quick/nlint (tlint likewise has
none): those three can BLOCK a turn, so loosing them on a project that never
agreed to this repo's conventions is a genuine hazard. This one is purely
ADVISORY —— one appended line of context, exit always 0 —— so its worst misfire
elsewhere is a single ignorable line, set against the far larger cost of a MISSED
`#[trigger]` (guessing a protocol instead of reading it). Intentional asymmetry
—— do not "restore consistency" with a guard.

CONSEQUENCE FOR PATHS: because invocations routinely arrive from OTHER repos,
`#[name]` must still resolve against THIS repo's `universal/`. Every path is
anchored on `_ROOT`/`_PARENT` (both derived from `__file__`), NEVER on the
process cwd, which is now commonly a different repo entirely. Nothing here may
reintroduce a cwd-relative path.

WHY THE SCOPE REACHES INTO `AJAP_repo/` (points 3 and 4): being global is only
half the job —— running everywhere is useless if the corpus is one repo. An AJAP
session was prompted `#eng`, this hook stayed silent because `eng.md` lives in
`AJAP_repo/protocols/` and nothing outside this repo was ever searched, the
protocol went unread, and the resulting rework cost over 100 hours. Reaching
across to the sibling AJAP protocol directory IS the point of the scope, not an
optional extra. `inv/` gets a single named file rather than a walk because that
tree is enormous; walking it would reintroduce exactly the latency this scope
was narrowed to remove.

WHY `sessions/` IS EXCLUDED: it holds ~1k comms files (`*_[TS].md`), which are
transcripts, never protocols. Indexing them made every non-canonical trigger pay
a walk over thousands of files, and let a token like `#career_close_202607181951`
"resolve" to a past transcript —— a reminder to read a file that defines nothing.
Pure latency for zero benefit. The exclusion is structural (`sessions/` is simply
not a search root) AND defended by `_EXCLUDED_DIR_NAMES`, so a later widening of
the scope cannot silently re-admit it. Corpus expansion still READS a named comms
file, but by computing its folder from the `[TS]` in its own filename (root
CLAUDE.md §3.4.9.1–2: start-month, else one month back) —— two direct stats, no
walk.

WHY SIBLING-RELATIVE, NOT HOME-RELATIVE: `AJAP_repo` is located as a sibling of
this repo via `_PARENT`, never via `$HOME`/`~`. This checkout lives on an
external volume (`~/.claude` is itself a symlink onto it) and has been relocated
before; a home-anchored constant would resolve to nothing after the next move and
the hook would go quietly silent —— the exact failure mode described above.

REGEX PRECISION: `_TRIGGER_RE` requires the `#` NOT to follow a word char, so a
URL fragment (`file#L10`) never matches whilst a standalone `#close` does, and a
markdown heading (`# Heading`) has a space after `#` so never matches either.
`_MD_TOKEN_RE` stops at whitespace and common quoting/bracket chars, so trailing
punctuation is not swallowed. Names are deduped case-insensitively (`#close` x10
-> one reminder), first-seen casing kept.

BACKTICK / FENCE EXEMPTION: a `#name` enclosed in single backticks
(`` `#close` ``) or sitting inside a ``` fenced ``` block is SKIPPED, never
treated as a live trigger. Two reasons, both named by the owner: (1) it lets a
`#trigger` be DISCUSSED ("what does `#close` do?") without being INVOKED —
right now those are indistinguishable and the hook cannot tell intent from a
bare token; (2) it stops premature reads fired by a trigger merely quoted
inside an EXAMPLE — root CLAUDE.md itself carries several (`` `#replace` ``,
`` `#debate` ``) precisely as illustrations, and every one of them used to
misfire when that file was read in as referenced content. Fenced blocks get
the SAME exemption as inline backticks, deliberately, not by omission: a
```` ``` ````-fenced example is quoting for exactly the same reason a
single-backtick one is (a shown command, a pasted transcript, a doc excerpt),
and treating the two fence styles differently would be an arbitrary line with
no principled basis — a user who wraps the same example in triple backticks
instead of one would otherwise get a different, surprising result. Mechanics:
`_quoted_spans()` first finds every fenced span on the RAW text (so its
coordinates are exact), then masks those characters out (spaces, newlines
kept) before scanning for inline single-backtick spans — the mask stops a
fence's own ``` delimiters, or a stray backtick used INSIDE example code, from
pairing with a backtick outside the fence and wrongly swallowing real prompt
text as "quoted". A trigger match is exempted when its `#` falls inside any
span. This scan runs PER SOURCE (the prompt, then each referenced file, never
a joined blob), so a fence or backtick span can never straddle the boundary
between the prompt and a file it names. An unterminated fence (no closing
```` ``` ````) matches nothing and is therefore NOT exempted — fail-open, the
same direction as every other lint in this repo: a rare unclosed-fence corner
case firing an extra (harmless, advisory) reminder is preferable to a fence
that never closes silently blanking out the rest of the prompt.

WHY THE REMINDER READS AS A MANDATE, NOT A SUGGESTION —— the wording is the
enforcement, so it is specified here rather than left to whoever edits the
f-string next. The line used to end "unless already read or INTENTIONALLY
DEFERRED", and that clause was itself the defect. On a live prompt this hook
worked perfectly: it read the named comms file, found a bare `#cic` inside it,
and injected TWO reminders on one line —— that trigger and a second one. The
agent read the SECOND file, silently self-certified the first as "intentionally
deferred", answered from a web search instead of the mandated route, and
shipped. The owner's reasonable conclusion was that the hook had never fired.
It had; only its wording failed. Three lessons are baked into the current text:
(1) an advisory that ships its own escape hatch WILL be escaped, so the hedge is
gone; (2) it now cites root CLAUDE.md §7.3.1–2 by number, because a reminder
that reads as a suggestion loses to whatever the agent already planned to do,
whilst one that names the rule it is enforcing does not; (3) reaching a similar
answer by some OTHER route is stated NOT to discharge the read —— that was the
exact substitution made, and nothing in the old line forbade it. A deferral is
still permitted, but must be DECLARED: a visible deferral the user can overrule
is categorically better than an invisible one he discovers in the output.
RESIDUAL, stated rather than papered over: UserPromptSubmit must never block
(see below and `cp/ccsim/hook_guide.md` §6.6 —— `decision:"block"` here ERASES
the user's prompt), so WORDING is the only lever this hook has and compliance
remains the model's choice. Anyone wanting a guarantee must add enforcement at
a channel that can gate the act, not strengthen this sentence again.

WHY IT LOGS EVERY INVOCATION: the incident above cost a forensic dig through
session transcripts to establish something the hook itself should have been
able to answer —— "did you fire, and what did you say?". A log written only on a
match cannot tell "never ran" apart from "ran and found nothing"
(`cp/ccsim/hook_guide.md` §7.7), and that ambiguity is precisely what let the
blame land on the hook. One TAB-separated line per invocation goes to
`cscpt/.hlint.log` (git-ignored), tagged by the stage reached: `no_stdin`,
`not_dict`, `no_prompt`, `silent`, `fired`. A `fired` line carries the trigger
names, so a later "you never told me" is settled by one `grep`. Logging is
housekeeping —— every failure is swallowed, exactly as in `clint.py`, because a
logging error must never break a prompt.

PERFORMANCE: a canonical `universal/[name].md` is a single stat —— no index at
all. Otherwise the scope index is built LAZILY and at most ONCE per run, over a
few hundred files instead of the whole repo, pruning `.git`, `node_modules`,
`.venv` and friends. Caps (never hit in normal use) bound the index, the
referenced-file count/bytes and the reminder count, so neither a huge file nor a
trigger-stuffed prompt can stall a turn. The log append is one `open`+`write`
on a small file, with the prune amortised across ~0.5% of invocations.

=== RETIRED: THE QUERY/RESPONSE PAIRING REMINDER (do not re-add here) ===

This file briefly also carried a second check —— a `*_query_[TS].md` named in the
prompt with no `*_response_[TS].md` beside it drew a reminder naming the response
it owed (root CLAUDE.md §3.5.3). It was REMOVED, and the reasoning is kept here
so it is not rebuilt from scratch by whoever next reads §3.5.3 and reaches for a
hook.

WHY IT WENT: at prompt-submit time it had NO discriminating power. A brand-new
`query_` has no `response_` yet BY CONSTRUCTION, so the check fired identically
on a perfectly compliant turn and on the breach —— a metronome, not a detector.
Measured over the live `.hlint.log`: 5 fires in 29 real invocations, i.e. once
for essentially every turn opened by a query file, at ~124 tokens a fire. The
token bill was small; the PRECISION was the defect, and a reminder that fires on
every correct turn is how a check earns being tuned out.

WHAT NOW COVERS IT: `.githooks/pre-commit`'s REVERSE PAIRING ARM (non-blocking,
adds-only) at commit time, and root CLAUDE.md §3.1.7.7 in prose. Both are
POST-HOC —— by the time either speaks, the wrong file has already been written.
That gap is real and is recorded as such rather than papered over.

WHERE IT BELONGS IF REBUILT: `cscpt/flint.py`, which already owns comms
FILENAMES and already models the `{query, response}` same-TS role pair. Its
PreToolUse half fires at the MOMENT OF THE WRITE (`cp/ccsim/CLAUDE.md` §8.7),
where the check regains its precision: it can compare the `response_` being
written against the NEWEST unpaired `query_` in that folder and stay silent
unless they disagree —— which on a compliant turn they never do. ⚠️ It needs a
per-`prompt_id` ledger there, or the sanctioned mid-turn case (a follow-up query
answered inside the CURRENT response, root §3.1.7.6.1) re-fires on every edit of
a long sprint. That accepted false positive is irreducible: no script can tell it
from the breach, since the two produce identical file operations and differ only
in whether the agent was IDLE when the message arrived.
"""

import sys
import os
import re
import json
from datetime import datetime

# Repo root = parent of this script's `cscpt/` dir (deterministic anchor; never
# relies on cwd, which may be a sub-folder for a given session).
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The directory that holds this repo. Sibling repos are derived from here rather
# than from `$HOME`, because this checkout sits on an external volume and has
# been relocated before —— a home-anchored path would silently resolve to
# nothing after a move, and the hook would go quietly silent.
_PARENT = os.path.dirname(_ROOT)

# Sibling repo carrying its own protocol set (see the AJAP note in the docstring).
_AJAP = os.path.join(_PARENT, "AJAP_repo")

# ---------------------------------------------------------------------------
# GLOBAL REACH —— no repo-scope guard here, deliberately: this lint is
# ADVISORY-ONLY (one line of context, exit always 0), so it may safely run in
# every project the user-level registration reaches, and a missed `#[trigger]`
# is the expensive failure. Consequence: every path below is anchored on
# `_ROOT`/`_PARENT`, NEVER on the process cwd, since invocations routinely
# arrive from other repos. Full rationale is in the CCSIM docstring above.
# ---------------------------------------------------------------------------

# SEARCH SCOPE, in priority order —— the ONLY directories a `#[trigger]` may
# resolve within. Deliberately narrow: `universal/` is where nearly every
# trigger lives, `cp/` carries the CP-local ones (root CLAUDE.md §7.3.3), and
# `AJAP_repo/protocols/` is reached because this hook runs globally and an
# unresolved `#eng` there once cost over 100 hours. An absent directory (e.g. a
# machine without the AJAP checkout) is skipped silently, never an error.
_SEARCH_DIRS = (
    os.path.join(_ROOT, "universal"),
    os.path.join(_ROOT, "cp"),
    os.path.join(_AJAP, "protocols"),
)

# Individually named files admitted to the scope. `AJAP_repo/inv/` is far too
# large to walk, so its one protocol-bearing file is listed outright.
_SEARCH_FILES = (
    os.path.join(_AJAP, "inv", "inveng.md"),
)

# Directories never worth walking (VCS internals, dependency/cache trees).
_SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    ".idea", ".vscode", ".DS_Store",
}

# Pruned inside EVERY search root as a second line of defence. `sessions/` is
# already out of scope by construction (it is not a search root); this set makes
# the exclusion survive any future widening of `_SEARCH_DIRS`, so comms
# transcripts can never be re-admitted as trigger targets by accident.
_EXCLUDED_DIR_NAMES = {"sessions"}

# A `#[name]` trigger: name = letters/digits/_/-, and the `#` is NOT preceded by
# a word char (so a URL fragment / suffix like `file#L10` never matches, whilst
# a standalone `#close` or `## 1.`-free hashtag still does; a markdown heading
# `# Heading` has a space after `#` and so never matches either).
_TRIGGER_RE = re.compile(r"(?<![A-Za-z0-9_])#([A-Za-z0-9_-]+)")

# A fenced code block: ``` ... ``` (DOTALL so the fence can span lines). Found
# on the RAW text first (see `_quoted_spans`), so its span coordinates are
# exact positions in the original string, before anything is masked.
_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)

# An inline single-backtick span: `...`, never crossing a newline —— mirrors
# how markdown itself never lets an inline code span cross a paragraph break,
# so a stray backtick earlier in the same prompt cannot pair across it.
_INLINE_BACKTICK_RE = re.compile(r"`[^`\n]*`")

# An `*.md` filename/path token in the prompt (stops at whitespace or common
# quoting/bracket chars so trailing punctuation is not swallowed).
_MD_TOKEN_RE = re.compile(r"([^\s\"'`()<>|,;]+\.md)", re.IGNORECASE)

# A comms filename's trailing `[TS]` = `YYYYMMDDHHmm` (root CLAUDE.md §2.2.1).
# Its `sessions/[YYYY]/[YYYYMM]/` folder is COMPUTED from this, so a named comms
# file can still be read for corpus expansion without walking `sessions/`.
_COMMS_TS_RE = re.compile(r"(\d{4})(\d{2})\d{6}\.md$", re.IGNORECASE)

# Safety caps (backstops; none is hit in normal use).
_MAX_INDEX = 60000          # max .md files indexed before giving up the walk
_MAX_REF_FILES = 10         # max distinct referenced files read from a prompt
_MAX_READ_BYTES = 512 * 1024  # max bytes read from any one referenced file
_MAX_REMINDERS = 15         # max reminder lines injected (avoid a flood)

_HEADER = ("[hlint hook] Possible hashtag-trigger(s) detected —— non-blocking "
           "reminder(s):")

# Per-invocation stage log (git-ignored). Overridable via `HLINT_LOG` so a
# regression test never writes to the live file. Rationale: docstring, WHY IT
# LOGS EVERY INVOCATION —— a log written only on a match cannot distinguish
# "never ran" from "ran and found nothing".
_LOG = os.environ.get("HLINT_LOG") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".hlint.log")

# Prune hysteresis, mirroring `clint.py`: read the file only once it could
# possibly exceed the cap, rewrite only when it actually does. The 1000/800 gap
# means a rewrite happens at most once per 200 invocations.
_LOG_PRUNE_AT_BYTES = 400 * 1024
_LOG_MAX_LINES = 1000
_LOG_KEEP_LINES = 800


def _prune_log():
    """Bound `_LOG` to its recent window —— cheap, atomic, fail-safe.

    Runs AFTER the current line is on disk, so this invocation's own line can
    never be a casualty of its own prune. The surviving tail is staged in a
    pid-suffixed sibling and moved in with `os.replace` (one atomic rename), so
    a crash leaves either the untouched original or the complete replacement,
    never a half file. Every failure is swallowed: pruning is housekeeping, and
    an unwritable directory must degrade to "the log keeps growing", never to
    "the hook fails"."""
    tmp = None
    try:
        if os.stat(_LOG).st_size < _LOG_PRUNE_AT_BYTES:
            return
        with open(_LOG, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
        if len(lines) <= _LOG_MAX_LINES:
            return
        tmp = "%s.tmp.%d" % (_LOG, os.getpid())
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines[-_LOG_KEEP_LINES:]) + "\n")
        os.replace(tmp, _LOG)
        tmp = None
    except Exception:
        pass
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except Exception:
                pass


def _log_event(stage, sid="-", triggers="-"):
    """Append ONE terse line for ANY invocation —— match or not.

    TAB-separated, `triggers=` last because it alone carries free text (tabs and
    newlines are flattened, so a record is always exactly one line). FAIL-SAFE:
    all errors swallowed —— nothing reads this log back, so a lost write costs
    diagnostics only, never the reminder itself. (Historic lines carry a
    `pairs=N` field from the retired pairing check; nothing parses this log, so
    the older shape is inert rather than a compatibility burden.)"""
    try:
        with open(_LOG, "a", encoding="utf-8") as lf:
            lf.write("%s\tsession=%s\tstage=%s\ttriggers=%s\n"
                     % (datetime.now().isoformat(timespec="seconds"), sid,
                        stage,
                        str(triggers)[:300].replace("\t", " ").replace("\n", " ")))
    except Exception:
        pass
    _prune_log()

# Lazily-built {basename_lower: [(scope_rank, absolute path), ...]} index of the
# search scope. None until first needed; built at most once per run.
_INDEX = None


def _rel(path):
    """Display path: repo-relative for this repo, parent-relative for siblings."""
    for base in (_ROOT, _PARENT):
        rel = os.path.relpath(path, base)
        if rel != os.pardir and not rel.startswith(os.pardir + os.sep):
            return rel.replace(os.sep, "/")
    return path.replace(os.sep, "/")


def _build_index():
    """Walk ONLY the search scope -> {basename_lower: [(rank, abspath), ...]}.

    `rank` is the scope's position in `_SEARCH_DIRS`/`_SEARCH_FILES`, so the
    declared priority order survives into `_best()`. A missing directory is
    skipped silently: a machine without the sibling AJAP checkout must still get
    working `universal/`+`cp/` reminders, not an error.
    """
    index = {}
    count = 0
    # Individually-named files first, so the `_MAX_INDEX` backstop below can
    # never starve them (rank is assigned explicitly, so order of insertion
    # does not affect priority).
    for offset, path in enumerate(_SEARCH_FILES):
        if os.path.isfile(path):
            index.setdefault(os.path.basename(path).lower(), []).append(
                (len(_SEARCH_DIRS) + offset, path))
    for rank, root in enumerate(_SEARCH_DIRS):
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            # Sorted so the walk order is deterministic across filesystems.
            dirnames[:] = sorted(d for d in dirnames
                                 if d not in _SKIP_DIRS
                                 and d not in _EXCLUDED_DIR_NAMES)
            for fn in filenames:
                if fn.lower().endswith(".md"):
                    index.setdefault(fn.lower(), []).append(
                        (rank, os.path.join(dirpath, fn)))
                    count += 1
                    if count >= _MAX_INDEX:
                        return index
    return index


def _get_index():
    global _INDEX
    if _INDEX is None:
        try:
            _INDEX = _build_index()
        except Exception:
            _INDEX = {}
    return _INDEX


def _best(entries):
    """Deterministic pick: scope rank, then shallowest, shortest, lexicographic.

    Returns the absolute path; callers render it via `_rel()` for display.
    """
    def key(entry):
        rank, path = entry
        shown = _rel(path)
        return (rank, shown.count("/"), len(shown), shown)
    return sorted(entries, key=key)[0][1]


def _comms_candidates(base):
    """Direct candidate paths for a `*_[TS].md` comms file —— no walk.

    A comms filename carries its own `YYYYMMDDHHmm`, and comms files live in the
    folder of the session's START month, so the folder is computable: try the
    TS's own month, then one month back (root CLAUDE.md §3.4.9.1–2, which covers
    a session that ran past a month boundary). Two stats, versus a walk of ~1k
    files —— and it keeps `sessions/` out of the trigger search entirely.
    """
    m = _COMMS_TS_RE.search(base)
    if not m:
        return []
    year, month = int(m.group(1)), int(m.group(2))
    months = [(year, month)]
    months.append((year - 1, 12) if month == 1 else (year, month - 1))
    return [os.path.join(_ROOT, "sessions", "%04d" % y, "%04d%02d" % (y, mo), base)
            for y, mo in months]


def _locate(token):
    """Absolute path of an `*.md` file the prompt names, or None. Never walks.

    Order: the token taken as a path (absolute, or relative to this repo or its
    parent) -> the search-scope index by basename -> a comms file addressed by
    its own `[TS]`. Nothing is resolved against the process cwd, which for this
    globally-registered hook is routinely a different repo.
    """
    base = os.path.basename(token)
    cands = []
    if os.path.isabs(token):
        cands.append(token)
    else:
        cands.append(os.path.join(_ROOT, token))
        cands.append(os.path.join(_PARENT, token))
    entries = _get_index().get(base.lower())
    if entries:
        cands.append(_best(entries))
    cands.extend(_comms_candidates(base))
    for cand in cands:
        if os.path.isfile(cand):
            return cand
    return None


def _read_referenced(prompt):
    """Return concatenated content of `*.md` files the prompt names (bounded)."""
    parts = []
    seen = set()
    for m in _MD_TOKEN_RE.finditer(prompt):
        token = m.group(1)
        base = os.path.basename(token).lower()
        if base in seen:
            continue
        seen.add(base)
        full = _locate(token)
        if not full:
            continue
        try:
            with open(full, "r", encoding="utf-8", errors="replace") as fh:
                parts.append(fh.read(_MAX_READ_BYTES))
        except Exception:
            pass
        if len(seen) >= _MAX_REF_FILES:
            break
    return parts


def _quoted_spans(text):
    """(start, end) spans in `text` where a `#trigger` is being DISCUSSED, not
    invoked: inside a fenced code block or an inline single-backtick span.
    Rationale in the module docstring (BACKTICK / FENCE EXEMPTION).

    Fenced spans are found FIRST, on the untouched `text`, so their
    coordinates are exact. The inline-backtick scan then runs over a MASKED
    copy —— fenced-block characters overwritten with spaces, newlines kept so
    `[^`\\n]` still behaves —— so a fence's own ``` delimiters, or a stray
    backtick used INSIDE example code, can never pair with a backtick outside
    the fence and wrongly swallow real prompt text as "quoted".
    """
    spans = [m.span() for m in _FENCE_RE.finditer(text)]
    if spans:
        chars = list(text)
        for start, end in spans:
            for i in range(start, end):
                if chars[i] != "\n":
                    chars[i] = " "
        masked = "".join(chars)
    else:
        masked = text
    spans.extend(m.span() for m in _INLINE_BACKTICK_RE.finditer(masked))
    return spans


def _is_quoted(pos, spans):
    """True if `pos` (the trigger's `#`) falls inside any quoted span."""
    return any(start <= pos < end for start, end in spans)


def _extract_triggers(text):
    """Names of `#trigger` tokens in `text`, in first-appearance order,
    SKIPPING any match sitting inside a quoted span (see `_quoted_spans`) ——
    a backticked or fenced `#name` is discussed, not invoked, and never
    reaches the caller. Run PER SOURCE (never on a joined blob) so a fence or
    backtick span can never straddle the boundary between two sources."""
    spans = _quoted_spans(text)
    return [m.group(1) for m in _TRIGGER_RE.finditer(text)
            if not _is_quoted(m.start(), spans)]


def _resolve_trigger(name):
    """Display path of `[name].md` within the search scope, or None.

    Canonical `universal/[name].md` is tried as a single stat first —— that is
    the overwhelmingly common case, and it means most prompts never build an
    index at all.
    """
    canonical = os.path.join("universal", name + ".md")
    if os.path.isfile(os.path.join(_ROOT, canonical)):
        return canonical.replace(os.sep, "/")
    entries = _get_index().get((name + ".md").lower())
    if not entries:
        return None
    return _rel(_best(entries))


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        _log_event("no_stdin")
        return 0

    if not isinstance(data, dict):
        _log_event("not_dict")
        return 0

    sid = data.get("session_id") or "-"

    prompt = data.get("prompt")
    if not isinstance(prompt, str) or not prompt:
        _log_event("no_prompt", sid)
        return 0

    try:
        referenced = _read_referenced(prompt)
    except Exception:
        referenced = []

    # Unique trigger names, case-insensitively deduped, first-seen casing kept.
    # Scanned PER SOURCE —— the prompt, then each referenced file in turn,
    # never a joined blob —— so a fence/backtick span can never straddle the
    # boundary between the prompt and a file it names (module docstring:
    # BACKTICK / FENCE EXEMPTION). The prompt goes first, so a name's first
    # appearance there always wins its displayed casing over a later file.
    seen = {}
    for text in [prompt] + referenced:
        try:
            names = _extract_triggers(text)
        except Exception:
            names = []
        for raw in names:
            seen.setdefault(raw.lower(), raw)

    lines = []
    fired_names = []          # names that actually produced a reminder (logged)
    for raw in seen.values():
        try:
            path = _resolve_trigger(raw)
        except Exception:
            path = None
        if path:
            # Wording is the enforcement here —— see the docstring section WHY
            # THE REMINDER READS AS A MANDATE before softening any of it. The
            # removed hedge ("unless ... intentionally deferred") was the
            # defect: it licensed a silent, self-certified skip.
            lines.append(
                "`#%s` detected —— READ `%s` (root CLAUDE.md §7.3.1–2: a "
                "trigger's protocol file MUST be read, never guessed; reaching "
                "a similar answer by another route does NOT discharge it). "
                "Skip only if already read THIS session. Deferring is allowed "
                "but must be DECLARED in the response, with the reason —— "
                "never taken silently."
                % (raw, path))
            fired_names.append(raw)
        if len(lines) >= _MAX_REMINDERS:
            break

    if not lines:
        # SILENT is a real outcome, not an absence —— logging it is the whole
        # point of §7.7: without this line, "hlint never ran" and "hlint ran and
        # matched nothing" are indistinguishable after the fact.
        _log_event("silent", sid)
        return 0

    _log_event("fired", sid, ",".join(fired_names) or "-")

    context = _HEADER + "\n" + "\n".join(lines)
    try:
        sys.stdout.write(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context,
            }
        }))
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
