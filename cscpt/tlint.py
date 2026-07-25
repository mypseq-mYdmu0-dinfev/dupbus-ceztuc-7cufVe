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

# ---------------------------------------------------------------------------
# REPO-SCOPE GUARD.
#
# WHY: this hook is registered in the USER-level ~/.claude/settings.json, not
# a project settings.json —— proven live this session that Claude Desktop
# NEVER runs project-level hooks, only user-level ones. A user-level
# registration fires for EVERY project open on this Mac, not just this repo.
# Unscoped, that is actively harmful here: this hook enforces THIS repo's
# own comms-filename timestamp convention and would flag unrelated
# projects' files for sharing a bare numeric substring that has no meaning
# there. So before doing anything else, self-scope to this repo and exit
# silently everywhere else.
#
# HOW: prefer the payload's `cwd` (an absolute path, confirmed present on
# every real PostToolUse payload captured live this session —— exactly the
# event type this hook receives). If `cwd` is ever absent, fall back to
# `transcript_path`'s Claude-Code project slug: transcripts live at
# `~/.claude/projects/<slug>/<uuid>.jsonl`, where `<slug>` is the project
# directory with every `/` and ` ` replaced by `-` (confirmed live).
# Compare either signal against THIS repo's own root/slug, derived from
# this script's OWN location (never a hard-coded path, so the repo stays
# portable/relocatable) —— resolving symlinks via `os.path.realpath` and
# treating a sub-path of the repo as in-scope too.
#
# FAIL-OPEN: if NEITHER field is present/parseable, run exactly as if this
# guard did not exist. An unscopeable payload is not evidence of a
# different project —— it is just a shape we cannot read —— and a lint
# that goes silently dark on ambiguity is precisely the failure this whole
# hook-migration effort exists to fix.
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


def _mirror_dir(dirpath):
    """Cross-repo comms mirror of a `.../GitHub/<repo>/<sub>/<YYYY>/<YYYYMM>` folder:
    dupbus `sessions/` <-> AJAP `inv/` for the SAME year-month. Returns the mirror
    path if it exists, else None. Enforces TS-uniqueness across BOTH repos, but only
    the matching year-month sub-folder — so AJAP's huge trees are never walked."""
    ap = os.path.abspath(dirpath)
    m = re.search(r"^(.*/GitHub/)(dupbus-ceztuc-7cufVe/sessions|AJAP_repo/inv)/(\d{4})/(\d{6})$", ap)
    if not m:
        return None
    base, repo, y, ym = m.group(1), m.group(2), m.group(3), m.group(4)
    other = "AJAP_repo/inv" if repo.endswith("sessions") else "dupbus-ceztuc-7cufVe/sessions"
    cand = os.path.join(base, other, y, ym)
    return cand if os.path.isdir(cand) else None


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    if not _in_scope(data):
        return 0

    fp = (data.get("tool_input") or {}).get("file_path") or ""
    if not fp:
        return 0
    w_base = os.path.basename(fp)

    ts = _find_ts(w_base)
    if not ts:
        return 0  # written file has no TS -> nothing to check

    dirpath = os.path.dirname(fp) or "."

    def _hits(d):
        try:
            return [e for e in os.listdir(d)
                    if _has_ts(e, ts) and os.path.isfile(os.path.join(d, e))]
        except Exception:
            return []

    # Same-TS files in the written file's OWN folder (incl. itself), plus any in
    # the cross-repo mirror folder (dupbus sessions <-> AJAP inv, same year-month).
    own = _hits(dirpath)
    own_others = [e for e in own if e != w_base]
    mdir = _mirror_dir(dirpath)
    mirror_others = _hits(mdir) if mdir else []

    if not own_others and not mirror_others:
        return 0  # lone TS -> silent

    # Benign ONLY when: exactly one SAME-FOLDER sibling forms a clean pair
    # (query/response or close/artefact), AND nothing shares the TS cross-repo.
    if (not mirror_others) and len(own) == 2 and _is_clean_pair(w_base, own_others[0], ts):
        return 0

    parts = []
    if own_others:
        parts.append(", ".join(sorted(own_others)) + " (same folder)")
    if mirror_others:
        parts.append(", ".join(sorted(mirror_others)) + " (cross-repo: " + mdir + ")")
    sys.stderr.write(
        "TS clash: `" + w_base + "` shares timestamp " + ts + " with "
        + "; ".join(parts) + " —— only a co-located query_/response_ (or close_/"
        "artefact_) pair may share a TS. Re-stamp the odd one out (or confirm intentional).\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
