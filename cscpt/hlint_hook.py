#!/usr/bin/env python3
"""UserPromptSubmit hook —— "hashtag/trigger linter". When the user submits a
prompt, scan it (and any comms file it references) for `#[trigger]` tokens and,
for each trigger that has a matching `[trigger].md` in the repo, inject a
NON-BLOCKING YELLOW reminder telling CC to read that file (root CLAUDE.md
§7.3.1 —— `#[trigger]` MUST be resolved by reading `universal/[trigger].md`
first, never guessed). Purely advisory: a trigger already handled or
intentionally deferred is fine.

WHY a hook, not trust: forgetting to read a trigger's protocol file is a silent,
high-cost slip (e.g. running `#replace`/`#debate` from a guessed meaning instead
of the file). A deterministic prompt-time scan surfaces the right file to read
before the turn starts (coding.md —— back a prompt-declared invariant with cheap
code enforcement).

WHAT it does, self-contained (no external state, no comms-file coupling):
  1. Read the UserPromptSubmit stdin JSON; take the prompt text (field `prompt`).
  2. Build a scan corpus = the prompt text ITSELF, PLUS the content of any `*.md`
     file the prompt names (a bare token like `ccsim_query_202607242145.md`, or a
     pathed `universal/foo.md`). Named files are located by basename anywhere in
     the repo. This is exactly ONE level of file reading (files named in the
     prompt) —— never recursive, so it is always bounded.
  3. Extract every UNIQUE `#[name]` token (name = letters/digits/_/-) from the
     corpus (case-insensitive dedupe: `#close` x10 -> once).
  4. For each unique name, resolve `[name].md`: canonical `universal/[name].md`
     first (the §7.3.1 home of most triggers), else a single pruned repo-wide
     search (covers CP-local triggers, §7.3.3). No match -> stay silent for it.
  5. Emit ONE reminder line per matched trigger, giving the repo-relative path.

SURFACING —— it injects the reminder into CC's context via the UserPromptSubmit
JSON contract `hookSpecificOutput.additionalContext` (Claude Code adds that
string to the model's context for this turn; for UserPromptSubmit, plain stdout
would also be added, but the structured field is explicit and unambiguous). It
NEVER blocks: exit is always 0, and it never emits `decision:"block"` (which for
UserPromptSubmit would ERASE the user's prompt). No matched trigger -> no output.

PERFORMANCE —— the repo-wide search runs LAZILY (only if a file is referenced or
a trigger is not canonical) and ONCE per run (indexed), pruning `.git`,
`node_modules`, `.venv`, etc.; referenced-file reads are capped in count and
bytes so a huge file can never stall the prompt.

FAIL-SAFE —— any error, missing field, or unreadable file -> exit 0 with no
output; a linter must never break or delay a prompt on its own failure.
(Run by the harness, not read —— see README.)"""

import sys
import os
import re
import json

# Repo root = parent of this script's `cscpt/` dir (deterministic anchor; never
# relies on cwd, which may be a sub-folder for a given session).
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
