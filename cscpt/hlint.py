#!/usr/bin/env python3
"""UserPromptSubmit hook —— "hashtag/trigger linter". Scans a submitted prompt (and
any comms file it names) for `#[trigger]` tokens and, for each trigger that has
a matching `[trigger].md` inside the SEARCH SCOPE below, injects a NON-BLOCKING
reminder to read that file (root CLAUDE.md §7.3.1: a `#[trigger]` MUST be
resolved by reading its file, never guessed).

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: a UserPromptSubmit hook. It spots `#[trigger]` tokens in the prompt (and
  in any one `.md` it names) and prepends one line per trigger naming its
  protocol file —— root CLAUDE.md §7.3.1: a trigger MUST be resolved by reading
  its file, never guessed.
* IF IT FIRES: read the named file, or state why not. ADVISORY —— it never
  blocks —— so a trigger already handled or deferred is fine.
* ITS BLIND SPOT: a trigger resolves only under `universal/`, `cp/`,
  `AJAP_repo/protocols/` and `AJAP_repo/inv/inveng.md`. Silence is NOT proof no
  protocol governs it —— look yourself.
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
CLAUDE.md §3.4.8.1–2: start-month, else one month back) —— two direct stats, no
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

PERFORMANCE: a canonical `universal/[name].md` is a single stat —— no index at
all. Otherwise the scope index is built LAZILY and at most ONCE per run, over a
few hundred files instead of the whole repo, pruning `.git`, `node_modules`,
`.venv` and friends. Caps (never hit in normal use) bound the index, the
referenced-file count/bytes and the reminder count, so neither a huge file nor a
trigger-stuffed prompt can stall a turn.
"""

import sys
import os
import re
import json

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
    TS's own month, then one month back (root CLAUDE.md §3.4.8.1–2, which covers
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
        return 0

    if not isinstance(data, dict):
        return 0

    prompt = data.get("prompt")
    if not isinstance(prompt, str) or not prompt:
        return 0

    try:
        corpus = "\n".join([prompt] + _read_referenced(prompt))
    except Exception:
        corpus = prompt

    # Unique trigger names, case-insensitively deduped, first-seen casing kept.
    seen = {}
    for m in _TRIGGER_RE.finditer(corpus):
        raw = m.group(1)
        seen.setdefault(raw.lower(), raw)

    lines = []
    for raw in seen.values():
        try:
            path = _resolve_trigger(raw)
        except Exception:
            path = None
        if path:
            lines.append(
                "`#%s` detected; read `%s` unless already read or intentionally deferred."
                % (raw, path))
        if len(lines) >= _MAX_REMINDERS:
            break

    if not lines:
        return 0  # nothing matched -> silent, non-blocking

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
