#!/usr/bin/env python3
"""PostToolUse hook (fires on Write/Edit) —— "timestamp linter". Guards the
implicit filename-TS invariant: no two files in one comms folder may carry the
SAME 12-digit TS (YYYYMMDDHHmm), EXCEPT a clean `query_`/`response_` pair (same
TS, same optional CP prefix, exactly one `query_` + one `response_`).

Why this exists (self-contained rationale —— no comms/conversation file explains
it, per coding.md):
  * A comms TS is the join key between a turn's files. Root CLAUDE.md sanctions
    exactly ONE many-to-one case —— a `query_`/`response_` PAIR shares an
    identical TS (§3.5.3 "response TS matches its query"; §3.6.2 "both files
    share identical TS"). Every OTHER same-TS collision is an accident: a second
    `response_`, a `close_` written over a turn's TS, a stray script named with
    a TS, a file mis-stamped from a neighbour. Such collisions are silent at
    write time and only surface much later (a `#close` that pairs the wrong two
    files, a `#ww` that grabs the wrong sibling), so a cheap deterministic check
    at write time beats hoping the convention is obeyed (coding.md —— back a
    prompt-declared invariant with code enforcement).
  * The check is a NON-BLOCKING YELLOW only (never RED / exit 2). A TS clash is
    a smell, not a correctness bug the harness can safely auto-block on: the
    "right" fix (re-stamp which file?) is a human judgement, and blocking a
    write mid-turn on a filename smell would do more harm than the smell.

KNOWN CAVEAT (documented same-TS case this check does NOT exempt): root
CLAUDE.md §3.3.5 defines `artefact_[close_TS].md` —— an `artefact_` file
deliberately SHARES its `close_`'s TS, and both live in the same comms folder.
That legitimate pair is NOT `query_`/`response_`, so writing such an `artefact_`
beside its `close_` yields ONE non-blocking YELLOW. This is tolerated by design:
the brief scopes the sole exception to `query_`/`response_`, the false positive
is advisory-only (exit 0), and surfacing the rare artefact/close overlap is
harmless. Widen `_CLEAN_ROLES` / the pair test here only if that YELLOW proves
noisy in practice.

Scope & safety:
  * Acts ONLY when the WRITTEN file's basename carries a TS (a 12-digit run
    starting "20", not flanked by other digits —— glossary: "12-digit no.
    starting with 20"). TS-less writes (code, docs, CLAUDE.md, etc.) -> exit 0.
  * Searches the written file's OWN directory only (comms live per-folder; that
    is where TS-as-pair matters) —— exactly ONE directory listing, so it is fast.
  * Surfacing mirrors the nlint/dlint YELLOW path: warning text to STDERR, then
    exit 0 (non-blocking). It NEVER exits 2 and NEVER blocks.
  * FAIL-SAFE —— on ANY error, missing field, or non-match it exits 0; it can
    never block or crash a turn on its own failure.
(Run by the harness, not read —— see README.)"""

import sys
import os
import re
import json

# A filename TS: 12 digits starting "20" (YYYYMMDDHHmm), not part of a longer
# digit run (so a 13+-digit id never reads as a TS, and a TS is not matched
# inside one). Used both to find the written file's TS and to test siblings.
_TS_RE = re.compile(r"(?<!\d)(20\d{10})(?!\d)")

# Sanctioned same-TS role pairs (same optional CP prefix):
#   {query, response} —— root CLAUDE.md §3.5.3 / §3.6.2 (response inherits query TS)
#   {close, artefact}  —— root CLAUDE.md §3.3.5 (artefact_[close_TS] shares its close's TS)
_CLEAN_ROLE_SETS = (frozenset({"query", "response"}), frozenset({"close", "artefact"}))


def _find_ts(base):
    """First TS in a basename, or '' if none."""
    m = _TS_RE.search(base)
    return m.group(1) if m else ""


def _has_ts(base, ts):
    """True if `ts` appears in `base` as a bounded 12-digit token (not inside a
    longer digit run) —— avoids a substring false match against a 13+-digit id."""
    return re.search(r"(?<!\d)" + re.escape(ts) + r"(?!\d)", base) is not None


def _prefix_role(base, ts):
    """Split a TS-bearing basename into (cp_prefix, role) around the TS.

    e.g. `career_response_<TS>.md` -> ("career", "response")
         `response_<TS>.md`        -> ("",       "response")
         `note_<TS>.md`            -> ("",       "note")
         `foo_<TS>.sh`             -> ("",       "foo")
         `<TS>.md`                 -> ("",       "")
    The role is the underscore-segment immediately before the TS; anything
    earlier is the (optional) CP prefix. Text after the TS (extension, etc.) is
    irrelevant to pairing and ignored."""
    idx = base.find(ts)
    before = base[:idx].rstrip("_") if idx >= 0 else ""
    prefix, _sep, role = before.rpartition("_")
    return prefix, role


def _is_clean_pair(w_base, sib_base, ts):
    """True iff the written file and exactly this one sibling form a sanctioned
    same-TS pair: identical CP prefix AND roles == {query,response} or {close,artefact}."""
    wp, wr = _prefix_role(w_base, ts)
    sp, sr = _prefix_role(sib_base, ts)
    if wp != sp:
        return False
    return frozenset({wr, sr}) in _CLEAN_ROLE_SETS


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    fp = (data.get("tool_input") or {}).get("file_path") or ""
    if not fp:
        return 0
    w_base = os.path.basename(fp)

    ts = _find_ts(w_base)
    if not ts:
        return 0  # written file has no TS -> nothing to check

    dirpath = os.path.dirname(fp) or "."
    try:
        entries = os.listdir(dirpath)
    except Exception:
        return 0

    # Every file in THIS directory carrying the same TS (including the written
    # file itself). Directories are skipped; one listing, no recursion.
    same_ts = [
        e for e in entries
        if _has_ts(e, ts) and os.path.isfile(os.path.join(dirpath, e))
    ]
    others = [e for e in same_ts if e != w_base]

    if not others:
        return 0  # lone TS (only the written file) -> silent

    # A collision exists. It is benign ONLY when the written file and exactly
    # ONE sibling form a clean query_/response_ pair (no third same-TS file).
    if len(same_ts) == 2 and _is_clean_pair(w_base, others[0], ts):
        return 0

    colliding = ", ".join(sorted(others))
    sys.stderr.write(
        "TS clash: `" + w_base + "` shares timestamp " + ts + " with "
        + colliding + " in the same folder —— only a clean query_/response_ "
        "pair may share a TS. Re-stamp the odd one out (or confirm intentional).\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
