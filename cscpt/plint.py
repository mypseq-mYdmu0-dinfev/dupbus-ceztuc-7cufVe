#!/usr/bin/env python3
"""PreToolUse hook —— "protocol-read linter". BEFORE a file is written, it looks at
what is about to be written and injects a NON-BLOCKING reminder to read the
governing protocol file FIRST.

=== NON-CCSIM —— all you need to RUN it ===
* Run by the harness, never by hand. Registered as a `PreToolUse` hook
  (Edit|Write|MultiEdit) in the USER-level `~/.claude/settings.json` (the Claude
  Desktop app executes user-level hooks and silently ignores project-level
  ones). NO repo-scope guard: it runs in EVERY project on this Mac,
  deliberately (see CCSIM).
* TWO RULES:
  - CODE (mechanical, certain) —— target is a script or pcmd: extension
    `.py`/`.sh`, or a `.md` that lives under `universal/`, is a `CLAUDE.md`, or
    sits under `cp/<project>/`. -> read `universal/coding.md`. Comms files
    (`query_`/`response_`/`close_`/`wrap_`/`slog_`/`artefact_`) are excluded.
  - DELIVERABLE (heuristic, uncertain) —— the written CONTENT carries a
    greeting/sign-off marker (`hello`, `dear`, `greetings`, `regards`,
    `sincerely`, `best wishes`, `yours`, ...; the list is `_MARKERS` below).
    -> read `universal/writing.md`, and consider its `## Stylisation` section.
* Each rule is gated on its pcmd existing (missing -> that rule stays silent),
  and names the file by ABSOLUTE path so it is openable from any project.
* IN: PreToolUse JSON on stdin (`tool_input`). OUT: on a match, JSON on stdout
  carrying `hookSpecificOutput.additionalContext` —— one line per rule.
* EXIT is ALWAYS 0. It never gates a write: no `permissionDecision` of
  `deny`/`ask` is ever emitted. Advisory —— ignore it if already read.
* FAIL-SAFE: any error, missing field or unreadable payload -> exit 0, no
  output.
(Run by the harness, not read —— see README.)

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WHY IT EXISTS (self-contained —— no conversation or comms file explains or
overrides anything here): these protocol reads get SILENTLY SKIPPED, and the cost
is asymmetric and back-loaded. A script written without coding.md misses the
issue-reporting format, bakes in a comms-file citation that rots, or ships a fix
with no regression test; a deliverable written without writing.md goes to a third
party in the wrong register —— both cheap to prevent at write time, expensive to
discover later.

WHY COMMS FILES ARE EXCLUDED FROM THE CODE RULE: a `response_` can legitimately
live beside pcmd (or embed a code snippet), but writing one is a COMMS act, not
a coding task —— and those writes happen every single turn. Reminding on them
would make the hook fire constantly and be tuned out, destroying its value on
the writes that matter. (Comms prose is policed separately, post-write.)
Tolerated blind spot: a genuine pcmd named like a comms file
(`response_parser.md`) is skipped —— a missed reminder, the harmless direction.

WHY IT CAN NEVER BLOCK: the DELIVERABLE rule is an admitted heuristic —— a script
that merely prints "hello", or a doc quoting a letter, will trip it. Hence the
design contract: a false positive costs exactly ONE LINE OF TEXT and nothing
else, because a linter that can block a write on a guess is worse than none. The
scan caps (content bytes, MultiEdit fan-out) are backstops in the same spirit.

WHY NO REPO-SCOPE GUARD (clint, dlint_quick and nlint carry one; hlint and tlint
deliberately do not, and neither does this): the guarded three enforce this
repo's private conventions AND can BLOCK, so firing them elsewhere is a hazard.
"Read your coding standard before editing a script" is generically true, so this
one is allowed everywhere —— on condition it never nags about a file that does
not exist (hence the existence gate) and that pcmd paths resolve from THIS
SCRIPT's own location, never cwd, never hard-coded. The reminder's absolute path
exists for the same reason: in a session rooted elsewhere, a repo-relative
`universal/coding.md` would resolve to nothing and send the model hunting.

MATCHING DETAIL: `_COMMS_RE` is ANCHORED so an ordinary pcmd merely CONTAINING a
role word (`my_response_notes.md`) is not swallowed. `_MARKER_RE` uses
WORD-BOUNDARY matching, load-bearing rather than cosmetic: a bare substring test
makes `regardless` match `regards` and `yourself` match `yours`, firing on
ordinary prose and training the reader to ignore the hook. Inner spaces match
one-or-more whitespace so a line-wrapped "best wishes" still hits, and the echoed
marker is whitespace-collapsed to keep output at one line per rule. Only NEW text
is scanned (Write `content`, Edit/MultiEdit `new_string`) —— the rule is about
what goes in, not what comes out —— and each rule sits in its own try/except so
one failing never suppresses the other.
"""

import sys
import os
import re
import json

# Repo root = parent of this script's `cscpt/` dir (deterministic anchor; never
# relies on cwd, which may be a sub-folder — or another project entirely).
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The two pcmd this hook can point at. Gated on existence at call time, so a
# repo (or a future trim) that lacks one simply loses that rule, silently.
_CODING_MD = os.path.join(_ROOT, "universal", "coding.md")
_WRITING_MD = os.path.join(_ROOT, "universal", "writing.md")

# Extensions that are unambiguously "a script" for the CODE rule.
_CODE_EXTS = {".py", ".sh"}

# Comms roles (root CLAUDE.md §3.3), matched at the START of a `.md` basename,
# after at most one optional CP prefix segment (`career_response_<TS>.md`).
# Anchored so an ordinary pcmd whose name merely CONTAINS a role word (e.g.
# `my_response_notes.md`) is not swallowed. Tolerated blind spot: a genuine
# pcmd named exactly like a comms file (`response_parser.md`) would be skipped
# —— a missed reminder, i.e. the harmless direction to err in.
_COMMS_RE = re.compile(
    r"^(?:[A-Za-z0-9][A-Za-z0-9-]*_)?"
    r"(?:query|response|close|wrap|slog|artefact)_",
    re.IGNORECASE)

# Greeting/sign-off markers for the DELIVERABLE rule. WORD-BOUNDARY matching is
# load-bearing, not cosmetic: a bare substring test makes `regardless` match
# `regards` and `yourself` match `yours`, which are common words that would fire
# the rule on ordinary prose and train the reader to ignore it. Inner spaces are
# `\s+` so a line-wrapped "best\nwishes" still matches.
_MARKERS = (
    "hello", "dear", "greetings", "regards", "sincerely",
    "best wishes", "to whom it may concern", "yours",
)
_MARKER_RE = re.compile(
    r"\b(" + "|".join(m.replace(" ", r"\s+") for m in _MARKERS) + r")\b",
    re.IGNORECASE)

# Safety caps (backstops; neither is hit in normal use). Bounding the scanned
# content keeps a pathologically large write from delaying the tool call, and
# bounding the MultiEdit fan-out keeps one payload from doing the same.
_MAX_SCAN_BYTES = 256 * 1024
_MAX_EDITS = 200

_HEADER = ("[plint hook] Protocol-read reminder(s) —— non-blocking, advisory "
           "only (ignore if already read this session):")


def _path_parts(fp):
    """Path split into components, separator-agnostic, empties dropped."""
    return [p for p in fp.replace("\\", "/").split("/") if p]


def _is_pcmd_md(parts):
    """True if this `.md` path is a protocol/context file (pcmd) rather than
    ordinary prose: under `universal/`, named `CLAUDE.md`, or sitting inside a
    CP folder (`cp/<project>/...`). Comms exclusion is applied by the caller."""
    if not parts:
        return False
    lower = [p.lower() for p in parts]
    if lower[-1] == "claude.md":
        return True
    dirs = lower[:-1]
    if "universal" in dirs:
        return True
    for i, seg in enumerate(dirs):
        # `cp/<project>/<file>` —— requires at least one folder between `cp`
        # and the file, so a stray `cp/foo.md` is not treated as CP protocol.
        if seg == "cp" and i + 1 < len(dirs):
            return True
    return False


def _wants_coding(fp):
    """CODE rule: does this write target a script or a pcmd?"""
    parts = _path_parts(fp)
    if not parts:
        return False
    base = parts[-1]
    ext = os.path.splitext(base)[1].lower()
    if ext in _CODE_EXTS:
        return True
    if ext != ".md":
        return False
    if _COMMS_RE.match(base):
        return False  # comms write, not a coding task —— see module docstring
    return _is_pcmd_md(parts)


def _written_content(tool_input):
    """Concatenated text this call would WRITE, across the three tool shapes:
    Write -> `content`; Edit -> `new_string`; MultiEdit -> `edits[].new_string`.
    Old text is deliberately ignored —— the rule is about what is being put in,
    not what is being taken out. Bounded by the caps above."""
    parts = []
    for key in ("content", "new_string"):
        val = tool_input.get(key)
        if isinstance(val, str):
            parts.append(val)
    edits = tool_input.get("edits")
    if isinstance(edits, list):
        for edit in edits[:_MAX_EDITS]:
            if isinstance(edit, dict):
                val = edit.get("new_string")
                if isinstance(val, str):
                    parts.append(val)
    return "\n".join(parts)[:_MAX_SCAN_BYTES]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    if not isinstance(data, dict):
        return 0

    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0

    lines = []

    # --- CODE rule (mechanical) --------------------------------------------
    try:
        fp = tool_input.get("file_path")
        if (isinstance(fp, str) and fp and _wants_coding(fp)
                and os.path.isfile(_CODING_MD)):
            lines.append(
                "Target `%s` is a script/pcmd —— read `%s` FIRST (issue-reporting "
                "format, self-contained rationale, regression test per fix)."
                % (os.path.basename(fp), _CODING_MD))
    except Exception:
        pass  # one rule failing must never suppress the other

    # --- DELIVERABLE rule (heuristic) --------------------------------------
    try:
        content = _written_content(tool_input)
        hit = _MARKER_RE.search(content) if content else None
        if hit and os.path.isfile(_WRITING_MD):
            # The matched marker is quoted back so the reader can dismiss a
            # false positive at a glance instead of re-reading the whole write.
            # Its internal whitespace is collapsed because a multi-word marker
            # can match ACROSS a line break ("Best\nwishes"), and echoing that
            # verbatim would split this reminder into two lines —— the output
            # block is strictly one line per rule.
            marker = re.sub(r"\s+", " ", hit.group(0))
            lines.append(
                "Content carries a greeting/sign-off marker (\"%s\") —— this may "
                "be a deliverable: read `%s` FIRST, and CONSIDER its "
                "`## Stylisation` section."
                % (marker, _WRITING_MD))
    except Exception:
        pass

    if not lines:
        return 0  # neither rule matched -> silent, and the write proceeds

    try:
        sys.stdout.write(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": _HEADER + "\n" + "\n".join(lines),
            }
        }))
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
