#!/usr/bin/env python3
"""PostToolUse hook —— "timestamp linter". Guards the implicit filename-TS
invariant: no two files in one comms folder (nor across the dupbus/AJAP comms
mirror) may carry the SAME 12-digit TS (YYYYMMDDHHmm), EXCEPT a sanctioned pair.

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: a PostToolUse hook guarding the filename-TS invariant —— no two files in
  one comms folder (nor across the dupbus/AJAP mirror) may share a 12-digit TS.
* SANCTIONED: `query_`+`response_`, `close_`+`artefact_`. Any other sharing is
  flagged.
* IT ALSO FLAGS a folder-mate whose name has a stray space before its TS
  (`close_ 202606142239.md`) —— alert the user; never go hunting for more.
* IT NEVER BLOCKS: always exit 0, the write untouched. Fix it yourself ——
  re-stamp, or `git mv` the stray space out.
* CHANNELS: the TS-clash line reaches the user only; the stray-space note
  reaches the model.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WIRING (kept here, not in NON-CCSIM: nobody invokes this file by hand, so the
plumbing serves only an editor). Run by the harness via `tlint_hook.sh`, the
registered bash fast-path; registered PostToolUse (Edit|Write|MultiEdit) in the
USER-level `~/.claude/settings.json` —— the Claude Desktop app executes
user-level hooks and silently ignores project-level ones. TRIGGERS only when the
written file's basename carries a TS (12 digits starting "20", not flanked by
other digits); a TS-less write —— code, docs, CLAUDE.md —— exits 0, silent.
WHERE IT LOOKS: the written file's OWN directory, plus —— only when that
directory is `.../GitHub/{dupbus.../sessions|AJAP_repo/inv}/YYYY/YYYYMM` —— the
matching year-month folder in the other repo. Two listings at most; AJAP's wider
trees are never walked. A pair counts as SANCTIONED only with an identical
optional CP prefix, exactly one co-located sibling, and nothing sharing the TS
cross-repo: `query_`+`response_` (root CLAUDE.md §3.5.3/§3.6.2) and
`close_`+`artefact_` (§3.3.5). It never exits 2. FAIL-SAFE: any error, missing
field or non-match -> exit 0.

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

STRAY-SPACE SWEEP (the second, independent check): a comms filename must be
`[prefix]_[TS].md` with NO whitespace (root CLAUDE.md §3.3), yet four have been
written with a space wedged in —— `close_ 202606142239.md` and kin —— each caught
by eye, months later. PREVENTION lives in `flint.py`, a PreToolUse gate that
blocks the write; a PostToolUse hook cannot undo one. What lives HERE is the
other half of that requirement: surfacing an offender that ALREADY exists,
WITHOUT anyone going looking for it. This hook already lists the written file's
own folder (and its cross-repo mirror) for the TS check, so re-reading that same
listing for the defect costs no extra I/O and no extra token —— it fires only as
a by-product of a write CC was making anyway, which is exactly what "alert on
encounter, never hunt" has to mean for it to be free. The detection rule and its
false-positive calibration are stated once, in `flint.py`; do not fork them.
It is emitted as `additionalContext` (model-visible, non-blocking —— hook_guide
§6.5) rather than on stderr beside the TS-clash line, because the model is who
must raise the `⚠️`; nothing is done to the file.
  NO DE-DUPLICATION LEDGER, deliberately: repeat writes into a folder that holds
an offender will re-fire. That nagging IS the forcing function, it self-
extinguishes the moment the file is renamed, and with `flint.py` gating creation
the only offenders left are historical. A per-session ledger would buy quiet at
the cost of another state file and another failure mode.

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

# The stray-space defect: from the START of a basename, a whitespace-FREE run
# ending in `_`, then whitespace, then a bounded 12-digit TS. Kept byte-identical
# to `flint.py`'s `_DEFECT_RE` —— that file states the rule and its
# false-positive calibration in full; this is the same rule, not a variant.
_STRAY_RE = re.compile(r"^\S*_\s+(?=20\d{10}(?!\d))")


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


def _advise_stray(paths):
    """Report stray-space filenames on the ONE PostToolUse channel that is both
    non-blocking and model-visible (hook_guide.md §6.5). The model is the
    audience on purpose: it is the party that must raise the `⚠️` to the user,
    which an exit-0 stderr line —— user-only —— could never make it do."""
    listing = "; ".join("`" + p + "`" for p in paths)
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                "[tlint] Stray-space filename(s) in a folder you just wrote to: "
                + listing + ". Root CLAUDE.md §3.3 names comms files "
                "`[prefix]_[TS].md`, with no space before the 12 digits. ALERT "
                "THE USER (a `⚠️` declaration) —— this surfaced on its own, "
                "so do NOT go hunting for others. Rename only on his say-so, with "
                "`git mv` in a move-only commit (universal/coding.md § Git "
                "Discipline)."
            ),
        }
    }) + "\n")


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

    def _entries(d):
        """One listing per folder, reused by BOTH checks below. Splitting this
        out is the whole reason the stray-space sweep is free: it reads nothing
        the TS check was not already reading."""
        try:
            return os.listdir(d)
        except Exception:
            return []

    def _ts_hits(d, entries):
        return [e for e in entries
                if _has_ts(e, ts) and os.path.isfile(os.path.join(d, e))]

    own_entries = _entries(dirpath)
    mdir = _mirror_dir(dirpath)
    mirror_entries = _entries(mdir) if mdir else []

    # --- CHECK 2 —— STRAY-SPACE SWEEP. Independent of the TS check and reported
    # even when the timestamps are clean, so it must run BEFORE that check's
    # early return. Scans names only: a stat would buy nothing, since a
    # directory carrying the defect is just as wrong as a file.
    stray = [os.path.join(dirpath, e) for e in sorted(own_entries)
             if _STRAY_RE.search(e)]
    if mdir:
        stray += [os.path.join(mdir, e) for e in sorted(mirror_entries)
                  if _STRAY_RE.search(e)]
    if stray:
        _advise_stray(stray)

    # --- CHECK 1 —— TS CLASH. Same-TS files in the written file's OWN folder
    # (incl. itself), plus any in the cross-repo mirror folder (dupbus sessions
    # <-> AJAP inv, same year-month).
    own = _ts_hits(dirpath, own_entries)
    own_others = [e for e in own if e != w_base]
    mirror_others = _ts_hits(mdir, mirror_entries) if mdir else []

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
