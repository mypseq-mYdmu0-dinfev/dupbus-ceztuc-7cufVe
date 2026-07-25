#!/usr/bin/env python3
"""PostToolUse hook —— "timestamp linter". Guards the implicit filename-TS
invariant: no two files in one comms folder (nor across the dupbus/AJAP comms
mirror) may carry the SAME 12-digit TS (YYYYMMDDHHmm), EXCEPT a sanctioned pair.

=== NON-CCSIM —— all you need to RUN it ===
* Run by the harness via `tlint_hook.sh` (the registered bash fast-path), never
  by hand. Registered PostToolUse (Edit|Write|MultiEdit) in the USER-level
  `~/.claude/settings.json` (the Claude Desktop app executes user-level hooks
  and silently ignores project-level ones). NO repo-scope guard: it runs in
  EVERY project on this Mac, deliberately (see CCSIM).
* TRIGGERS only when the written file's basename carries a TS —— 12 digits
  starting "20", not flanked by other digits. A TS-less write (code, docs,
  CLAUDE.md) -> exit 0, silent.
* WHERE IT LOOKS: the written file's OWN directory, plus —— only when that
  directory is `.../GitHub/{dupbus.../sessions|AJAP_repo/inv}/YYYY/YYYYMM` ——
  the matching year-month folder in the other repo. Two listings at most; AJAP's
  wider trees are never walked.
* SANCTIONED same-TS pairs (identical optional CP prefix, exactly one
  co-located sibling, nothing sharing the TS cross-repo): `query_`+`response_`
  (root CLAUDE.md §3.5.3/§3.6.2) and `close_`+`artefact_` (§3.3.5). Anything
  else sharing a TS is flagged.
* OUT: one warning line to STDERR naming the clashing files, then EXIT 0 ——
  ALWAYS. It never exits 2, never blocks, never alters a write. Mind the
  channel: PostToolUse delivers text to the MODEL only via exit-2 stderr or
  structured exit-0 JSON, so this line surfaces to the user/hook output, not CC.
* FAIL-SAFE: any error, missing field or non-match -> exit 0.
(Run by the harness, not read —— see README.)

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WHY IT EXISTS (self-contained —— no comms/conversation file explains it, per
coding.md): a comms TS is the join key between a turn's files, and root CLAUDE.md
sanctions only the two many-to-one cases above. Every other same-TS collision is
an accident —— a second `response_`, a `close_` over a turn's TS, a file
mis-stamped from a neighbour —— silent at write time and surfacing far later as
the wrong two files being paired (a `#close` or `#ww` grabbing the wrong
sibling). A cheap write-time check beats hoping the convention is obeyed.

WHY WARN-ONLY, NEVER RED: a TS clash is a smell, not a correctness bug the
harness can auto-resolve —— the fix ("re-stamp which file?") is human
judgement, and blocking a write over a filename smell harms more than the smell.

WHY NO REPO-SCOPE GUARD, unlike clint/dlint_quick/nlint (hlint likewise has
none): those three can BLOCK, so a stray firing elsewhere is a real hazard. This
one's only output is a stderr line at an always-0 exit, so it can never block,
alter or fail a write anywhere —— whilst a missed clash stays invisible until far
too late. The residual false positive (another project stamping 12-digit "20"
filenames and writing two that share one) costs one line of text; the guard it
replaces cost total blindness everywhere but here. Intentional asymmetry —— do
not "restore consistency" by adding a guard.

CROSS-REPO MIRROR: dupbus `sessions/` and AJAP `inv/` hold one comms stream, so
TS uniqueness must hold across both. `_mirror_dir` maps one to the other for the
SAME year-month only —— narrow by design, keeping the check to two listings
rather than a tree walk, and returning None when the shape does not match.

SHAPE GUARDS: `_TS_RE`/`_has_ts` require the 12 digits not to sit inside a
longer run, so a 13+-digit id never reads as a TS nor matches one by substring.
The `isinstance(data, dict)` check is not decorative: valid JSON that is not an
object would make `.get` raise and exit 1, breaking this file's own fail-safe
promise —— which matters all the more now any project's payload can arrive.
"""

import sys
import os
import re
import json

# ---------------------------------------------------------------------------
# GLOBAL REACH —— no repo-scope guard here, deliberately: this lint is
# WARN-ONLY (one stderr line, exit always 0), so it may safely run in every
# project the user-level registration reaches, and a missed TS clash is the
# expensive failure. Full rationale —— and why clint/dlint_quick/nlint DO
# self-scope —— is in the CCSIM section of the module docstring above.
# ---------------------------------------------------------------------------

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

    # Valid JSON that is not an object (a bare list/string/number) would make
    # the `.get` below raise AttributeError, printing a traceback and exiting
    # 1 —— breaking this file's own FAIL-SAFE promise. Cheap to rule out, and
    # it matters more now the hook runs machine-wide: an unexpected payload
    # shape from ANY project must still cost nothing but a silent exit 0.
    if not isinstance(data, dict):
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
