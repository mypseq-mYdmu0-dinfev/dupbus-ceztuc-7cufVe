#!/usr/bin/env python3
"""UserPromptSubmit hook —— "hashtag/trigger linter". Scans a submitted prompt (and
any comms file it names) for `#[trigger]` tokens and, for each trigger that has
a matching `[trigger].md` in this repo, injects a NON-BLOCKING reminder to read
that file (root CLAUDE.md §7.3.1: a `#[trigger]` MUST be resolved by reading its
file, never guessed).

=== NON-CCSIM —— all you need to RUN it ===
* Run by the harness, never by hand. Registered as a `UserPromptSubmit` hook in
  the USER-level `~/.claude/settings.json` (the Claude Desktop app executes
  user-level hooks and silently ignores project-level ones). NO repo-scope
  guard: it runs in EVERY project on this Mac, deliberately (see CCSIM), and
  every path it resolves is anchored on THIS repo.
* IN: UserPromptSubmit JSON on stdin (field `prompt`). OUT: on a match, JSON on
  stdout carrying `hookSpecificOutput.additionalContext` —— one line per matched
  trigger, naming the repo-relative file to read. No match -> no output.
* EXIT is ALWAYS 0. It never blocks and never emits `decision:"block"` (which
  for UserPromptSubmit would ERASE the user's prompt).
* SCAN CORPUS: the prompt text PLUS the content of any `*.md` file the prompt
  names (bare token or path, located by basename anywhere in the repo). Exactly
  ONE level deep, never recursive.
* RESOLUTION per trigger: canonical `universal/[name].md` first, else one pruned
  repo-wide search (covers CP-local triggers, §7.3.3). Unmatched -> silent.
* ADVISORY ONLY: a trigger already handled or intentionally deferred is fine ——
  the reminder line says so.
* FAIL-SAFE: any error, missing field or unreadable file -> exit 0, no output.
  It must never break or delay a prompt on its own failure.
(Run by the harness, not read —— see README.)

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
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
anchored on `_ROOT` (derived from `__file__`), NEVER on the process cwd, which
is now commonly a different repo entirely. Nothing here may reintroduce a
cwd-relative path.

REGEX PRECISION: `_TRIGGER_RE` requires the `#` NOT to follow a word char, so a
URL fragment (`file#L10`) never matches whilst a standalone `#close` does, and a
markdown heading (`# Heading`) has a space after `#` so never matches either.
`_MD_TOKEN_RE` stops at whitespace and common quoting/bracket chars, so trailing
punctuation is not swallowed. Names are deduped case-insensitively (`#close` x10
-> one reminder), first-seen casing kept.

PERFORMANCE: the repo-wide index is built LAZILY (only if a file is referenced or
a trigger is not canonical) and at most ONCE per run, pruning `.git`,
`node_modules`, `.venv` and friends. Caps (never hit in normal use) bound the
index, the referenced-file count/bytes and the reminder count, so neither a huge
file nor a trigger-stuffed prompt can stall a turn.
"""

import sys
import os
import re
import json

# Repo root = parent of this script's `cscpt/` dir (deterministic anchor; never
# relies on cwd, which may be a sub-folder for a given session).
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# GLOBAL REACH —— no repo-scope guard here, deliberately: this lint is
# ADVISORY-ONLY (one line of context, exit always 0), so it may safely run in
# every project the user-level registration reaches, and a missed `#[trigger]`
# is the expensive failure. Consequence: every path below is anchored on
# `_ROOT`, NEVER on the process cwd, since invocations routinely arrive from
# other repos. Full rationale is in the CCSIM section of the docstring above.
# ---------------------------------------------------------------------------

# Directories never worth walking (VCS internals, dependency/cache trees).
_SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    ".idea", ".vscode", ".DS_Store",
}

# A `#[name]` trigger: name = letters/digits/_/-, and the `#` is NOT preceded by
# a word char (so a URL fragment / suffix like `file#L10` never matches, whilst
# a standalone `#close` or `## 1.`-free hashtag still does; a markdown heading
# `# Heading` has a space after `#` and so never matches either).
_TRIGGER_RE = re.compile(r"(?<![A-Za-z0-9_])#([A-Za-z0-9_-]+)")

# An `*.md` filename/path token in the prompt (stops at whitespace or common
# quoting/bracket chars so trailing punctuation is not swallowed).
_MD_TOKEN_RE = re.compile(r"([^\s\"'`()<>|,;]+\.md)", re.IGNORECASE)

# Safety caps (backstops; none is hit in normal use).
_MAX_INDEX = 60000          # max .md files indexed before giving up the walk
_MAX_REF_FILES = 10         # max distinct referenced files read from a prompt
_MAX_READ_BYTES = 512 * 1024  # max bytes read from any one referenced file
_MAX_REMINDERS = 15         # max reminder lines injected (avoid a flood)

_HEADER = ("[hlint hook] Possible hashtag-trigger(s) detected —— non-blocking "
           "reminder(s):")

# Lazily-built {basename_lower: [repo-relative posix path, ...]} index of every
# .md file in the repo. None until first needed; built at most once per run.
_INDEX = None


def _rel(path):
    """Repo-relative, forward-slash path for display."""
    return os.path.relpath(path, _ROOT).replace(os.sep, "/")


def _build_index():
    """Walk the repo once (pruned) -> {basename_lower: [relpath, ...]}."""
    index = {}
    count = 0
    for dirpath, dirnames, filenames in os.walk(_ROOT):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for fn in filenames:
            if fn.lower().endswith(".md"):
                index.setdefault(fn.lower(), []).append(
                    _rel(os.path.join(dirpath, fn)))
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


def _shortest(paths):
    """Deterministic pick: shallowest, then shortest, then lexicographic."""
    return sorted(paths, key=lambda p: (p.count("/"), len(p), p))[0]


def _read_referenced(prompt):
    """Return concatenated content of `*.md` files the prompt names (bounded)."""
    parts = []
    seen = set()
    for m in _MD_TOKEN_RE.finditer(prompt):
        base = os.path.basename(m.group(1)).lower()
        if base in seen:
            continue
        seen.add(base)
        cands = _get_index().get(base)
        if not cands:
            continue
        full = os.path.join(_ROOT, _shortest(cands))
        try:
            with open(full, "r", encoding="utf-8", errors="replace") as fh:
                parts.append(fh.read(_MAX_READ_BYTES))
        except Exception:
            pass
        if len(seen) >= _MAX_REF_FILES:
            break
    return parts


def _resolve_trigger(name):
    """Repo-relative path of `[name].md`, or None. Canonical universal/ first."""
    canonical = os.path.join("universal", name + ".md")
    if os.path.isfile(os.path.join(_ROOT, canonical)):
        return canonical.replace(os.sep, "/")
    cands = _get_index().get((name + ".md").lower())
    if not cands:
        return None
    # Prefer a universal/ match, else the shallowest/shortest path.
    under_universal = [c for c in cands if c.startswith("universal/")]
    return _shortest(under_universal or cands)


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
