#!/usr/bin/env python3
"""PreToolUse + PostToolUse hook —— "filename linter". ONE lint owning comms
FILENAMES (root CLAUDE.md §3.3, `[prefix]_[12-digit TS].md`), on both halves of
that shape: the stray space wedged before the timestamp, and the timestamp
itself clashing with a neighbour. A TS is part of a filename, so one script.

Root scope: walks TWO repo roots —— `dupbus-ceztuc-7cufVe/sessions/` and
`AJAP_repo/inv/` —— and only their matching `YYYY/YYYYMM` sub-folders, because
those two hold ONE comms stream and TS uniqueness must hold across both. No
other repo is walked: nothing else on this Mac uses the `[prefix]_[TS].md`
convention. The dupbus root is derived from this file's own `__file__` and the
AJAP root from the written path itself, never from the process cwd —— a
user-level hook routinely runs from another repo.

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: the comms-filename gate (root CLAUDE.md §3.3, `[prefix]_[TS].md`).
* IT BLOCKS a write whose basename has a space before the 12 digits
  (`close_ 202606142239.md`); re-issue with the space-free name it gives.
* IT WARNS when a write's timestamp clashes with a neighbour in its folder or
  the AJAP mirror; only `query_`+`response_` and `close_`+`artefact_` may share
  one, so re-stamp the odd one out.
* IT ALERTS on any offender already beside a file you wrote: raise a `⚠️`,
  never hunt. Fixing one is `git mv`, never gated.
* Only the block stops a call. Anything else -> exit 0, silent.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WIRING (kept here, not in NON-CCSIM: nobody invokes this by hand, so the
plumbing serves only an editor). Run by the harness via `flint_hook.sh`, the
registered bash fast-path, from TWO registrations in the USER-level
`~/.claude/settings.json` —— the Claude Desktop app executes user-level hooks
and silently ignores project-level ones:
  * PreToolUse  (Edit|Write|MultiEdit|NotebookEdit|Read), argument `pre`
  * PostToolUse (Edit|Write|MultiEdit),                   argument `post`
Place the PreToolUse entry LAST in its array: it is the only entry on the write
path that can exit 2, and were the harness ever to short-circuit a chain on a
non-zero exit, an earlier position would skip `DADC.py hook-capture`'s
filesystem side effect and `alint_hook.sh`'s TEA1 gate.

MODE SELECTION is argv-first, `hook_event_name`-fallback —— the house pattern,
proven by the retired `elint.py` before it was folded into `dlint_quick.py`.
Argv is authoritative because it is unambiguous; the payload fallback exists
because a settings edit takes MINUTES to go live (`hook_guide.md` §7.9), so
for that window the OLD argument-less registration is still firing this file.
The fallback default is PRE, deliberately: mistaking a post payload for pre
costs one noisy exit 2 that cannot undo anything anyway, whilst mistaking a
pre payload for post would silently lose the BLOCK —— the one behaviour here
that is unrecoverable once missed.

CHANNELS, in full (trimmed out of NON-CCSIM to hold that block under its
100-word cap, not deleted —— a caller needs the verdicts, an editor needs the
plumbing). The PRE block is an exit-2 stderr write, which at PreToolUse reaches
the model AS AN ERROR and stops the call. Both advisories are exit-0
`additionalContext`, the one channel on either event that is BOTH non-blocking
and model-visible (`hook_guide.md` §6.5) —— the model is the audience on
purpose, because it is the party that must raise the `⚠️`. The TS-clash line is
an exit-0 stderr write, which reaches the USER only; that is deliberate, since
re-stamping is his judgement call, not CC's. PRE additionally emits its
advisory, never a block, when the offending path is one CC merely READ (the
PreToolUse registration includes `Read`) or when the write is out of repo scope.

WHY PRE MUST BLOCK AND POST CANNOT: a PostToolUse hook cannot undo a write ——
the tool has already run, so exit 2 there buys model visibility with error
framing, never a rollback (`hook_guide.md` §6.7). The defect class being fixed
is precisely "the file got created and nobody noticed", so only a PreToolUse
exit 2 stops the creation. The POST half therefore NEVER returns 2, and no
future edit may teach it to.

⚠️ REACH IS PER-BEHAVIOUR, NOT PER-FILE. `hook_guide.md` §4.7: a lint that can
BLOCK must be repo-scoped, a lint that can only advise may be global. This one
file does both, so the guard is wired to the BLOCK DECISION and to nothing
else:
  * `_in_scope()` is called at EXACTLY ONE site —— the `return 2` in `_pre()`.
  * Out of repo scope the gate DOWNGRADES to the advisory rather than going
    quiet, so §4.7 holds without buying it with blindness.
  * EVERYTHING ELSE IS GLOBAL, unguarded, in every project on this Mac: the
    PRE advisory, the whole POST half, and the cross-repo mirror check. That
    is not an oversight —— a missed TS clash is silent and expensive, it once
    cost real work in the AJAP repo, and the POST half's only outputs are a
    stderr line and a context note at an always-0 exit, so it can never block,
    alter or fail a write anywhere.
  * ⛔ DO NOT "tidy" a scope guard to the top of `main()`, or onto `_post()`,
    for consistency. That one line would silently delete AJAP coverage whilst
    every unit test still passed. `T8`/`T9` in
    `cp/ccsim/sandbox/flint_filename_gate_regression_test.py` exist to fail
    the moment anyone does.

DETECTION RULE, stated exactly: the basename must match
`^\\S*_\\s+(?=20\\d{10}(?!\\d))` —— from the START of the name, a whitespace-FREE
run ending in `_`, then one or more whitespace characters, then a 12-digit TS
beginning `20` and not sitting inside a longer digit run. Stated ONCE here and
used by both modes; the duplicate copy that used to live in `tlint.py` is
exactly the drift hazard this merge removes.

WHY THAT SHAPE AND NOT "a TS-bearing name containing any whitespace", which was
the obvious first draft: calibrated against every basename in this repo (5331
carry a bounded 12-digit TS; 7 of those also contain whitespace). The broad rule
flags 5 LEGITIMATE files —— `MGTK746 Dev Plan _ 202603170315.txt` and three
siblings in `cp/archive/mip/`, plus `gscpt/parked/AJAP Logs 202607182259.csv`
—— whose naming style uses spaces THROUGHOUT and is nobody's mistake. The `^\\S*`
anchor is what separates them: a name that is space-free right up to the
underscore and then suddenly is not, is the defect; a name spaced all the way
through is a different convention. When the rule was written the repo scored
exactly 2 hits, both the genuine article (`close_ 202606142239.md` and
`dissertation_close_ 202607151919.md`); both have since been renamed, so the
live sweep now scores 0. All 4 instances recorded in `cp/ccsim/backlog.md`
still match the rule, and none of the 5 legitimate spaced names do —— zero
false positives, zero misses. The suite's live-repo sweep re-derives that
verdict on every run rather than trusting this paragraph, which is why the
count going 2 -> 0 cost nothing but this sentence.

FALSE-POSITIVE PROFILE, honestly: a file deliberately named `<no-spaces>_ <TS>`
would be blocked. No such convention exists here, and the block message names
the exact replacement, so the cost of the theoretical case is one re-issued tool
call. Note also what is NOT flagged and why it must not be —— `_moved_[dir]`
suffixes (root §8.1.2) and `❌_` prefixes (§8.2) are legitimate and carry no
whitespace, so a positive-form "must match the canonical shape exactly" check
was rejected: it would have broken both.

WHY THE TS CHECK EXISTS: a comms TS is the join key between a turn's files, and
root CLAUDE.md sanctions only two many-to-one cases —— `query_`+`response_`
(§3.5.3/§3.6.2) and `close_`+`artefact_` (§3.3.5). Every other same-TS collision
is an accident (a second `response_`, a `close_` over a turn's TS, a file
mis-stamped from a neighbour), silent at write time and surfacing far later as
the wrong two files being paired by a `#close` or `#ww`. A cheap write-time
check beats hoping the convention is obeyed.

WHY THE TS CHECK ONLY WARNS, NEVER REDS: a clash is a smell, not a correctness
bug the harness can auto-resolve —— the fix ("re-stamp which file?") is human
judgement, and blocking a write over a filename smell harms more than the smell.

THE STRAY-SPACE SWEEP IS FREE, and that is the whole reason it sits in the POST
half rather than anywhere else: `_post()` already lists the written file's own
folder (and its mirror) for the TS check, so re-reading that same listing for
the defect costs no extra I/O and no extra token. It fires only as a by-product
of a write CC was making anyway, which is exactly what "alert on encounter,
never hunt" has to mean for it to be free. It is emitted as `additionalContext`
(model-visible, non-blocking —— `hook_guide.md` §6.5) rather than on stderr
beside the TS-clash line, because the model is who must raise the `⚠️`.
  NO DE-DUPLICATION LEDGER, deliberately: repeat writes into a folder that holds
an offender will re-fire. That nagging IS the forcing function, it self-
extinguishes the moment the file is renamed, and with the PRE half gating
creation the only offenders left are historical. A per-session ledger would buy
quiet at the cost of another state file and another failure mode.

CROSS-REPO MIRROR: dupbus `sessions/` and AJAP `inv/` hold one comms stream, so
TS uniqueness must hold across both. `_mirror_dir` maps one to the other for the
SAME year-month only —— narrow by design, keeping the check to two listings
rather than a tree walk, and returning None when the shape does not match.

KNOWN GAPS, so nobody mistakes this for total cover:
* A space INSIDE the digits (`close_2026061422 39.md`) leaves no bounded 12-digit
  TS at all, so neither half can see it.
* Only the harness's file tools are gated. A file created by Bash (`cp`, `touch`,
  a script) or by the user in Finder never reaches a PreToolUse hook —— that is
  exactly the hole `.githooks/pre-commit` closes, blocking a staged ADD of an
  offending path on the way into history.

SHAPE GUARDS: `_TS_RE`/`_has_ts` require the 12 digits not to sit inside a
longer run, so a 13+-digit id never reads as a TS nor matches one by substring.
FAIL-OPEN, per `hook_guide.md` §4.4: an unscopeable payload runs the lint anyway
(a silently disabled lint is the failure that guide exists to prevent). The
`isinstance(data, dict)` checks are not decorative: valid JSON that is not an
object would make `.get` raise and exit 1, breaking this file's own fail-safe
promise —— which matters all the more because a user-level registration means
any project's payload can arrive here.
"""

import json
import os
import re
import sys

# Repo anchor for the scope guard. Derived from this file's own location, never
# hard-coded, so the repo stays relocatable (hook_guide.md §4.5.1).
_REPO_ROOT_REAL = os.path.realpath(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
# Transcripts live at ~/.claude/projects/<slug>/<uuid>.jsonl, where <slug> is
# the project directory with every `/` and ` ` replaced by `-` (§4.3.2).
_REPO_SLUG = _REPO_ROOT_REAL.replace("/", "-").replace(" ", "-")

# THE STRAY-SPACE DEFECT. See DETECTION RULE in the docstring for the full
# calibration. ONE copy, used by both modes —— do not fork it.
_DEFECT_RE = re.compile(r"^\S*_\s+(?=20\d{10}(?!\d))")

# A filename TS: 12 digits starting "20" (YYYYMMDDHHmm), not part of a longer
# digit run (so a 13+-digit id never reads as a TS, and a TS is not matched
# inside one). Used both to find the written file's TS and to test siblings.
_TS_RE = re.compile(r"(?<!\d)(20\d{10})(?!\d)")

# Sanctioned same-TS role pairs (same optional CP prefix):
#   {query, response} —— root CLAUDE.md §3.5.3 / §3.6.2
#   {close, artefact} —— root CLAUDE.md §3.3.5
_CLEAN_ROLE_SETS = (frozenset({"query", "response"}),
                    frozenset({"close", "artefact"}))

# Tools that CREATE or REWRITE a file at the given path —— the only ones whose
# call is worth blocking. Everything else (Read chief among them) can at most be
# told about a defect that already exists.
_WRITE_TOOLS = frozenset({"Write", "Edit", "MultiEdit", "NotebookEdit"})


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _mode(argv, data):
    """PRE or POST. Argv wins; `hook_event_name` is the fallback for the
    minutes-long window in which a settings edit has not gone live yet
    (hook_guide.md §7.9). Default PRE —— see MODE SELECTION in the docstring."""
    arg = argv[1].strip().lower() if (
        len(argv) > 1 and isinstance(argv[1], str)) else ""
    if arg in ("pre", "post"):
        return arg
    ev = data.get("hook_event_name") if isinstance(data, dict) else ""
    if isinstance(ev, str) and ev.strip().lower() == "posttooluse":
        return "post"
    return "pre"


def _in_scope(data):
    """True if this invocation's project is THIS repo (or a sub-path of it), or
    if scope genuinely cannot be determined (FAIL-OPEN, hook_guide.md §4.4).
    Never raises: any unexpected error must default to "run the lint".

    ⚠️ CALLED FROM EXACTLY ONE PLACE —— the block decision in `_pre()`. Every
    other behaviour in this file is deliberately GLOBAL. See the REACH note in
    the module docstring before adding a second call site."""
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


def _target_path(data):
    """The path this tool call is about. `file_path` covers Write/Edit/MultiEdit
    /Read; `notebook_path` is NotebookEdit's own spelling of the same thing.
    Shared by both modes: POST is registered on Edit|Write|MultiEdit only, so
    the notebook key can never actually arrive there —— reusing one extractor
    still beats a second, subtly-different copy."""
    ti = data.get("tool_input")
    if not isinstance(ti, dict):
        return ""
    for key in ("file_path", "notebook_path"):
        v = ti.get(key)
        if isinstance(v, str) and v:
            return v
    return ""


def _clean_name(base):
    """The name the caller should have used: the offending whitespace run
    removed, nothing else touched. The match always ends `_` + whitespace, so
    `rstrip` can never strip it away to nothing."""
    return _DEFECT_RE.sub(lambda m: m.group(0).rstrip(), base, count=1)


def _advise(event, text):
    """Emit on the ONE channel that is BOTH non-blocking and model-visible
    (hook_guide.md §6.5). `event` must match the firing event or the harness
    may discard it."""
    json.dump({
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": text,
        }
    }, sys.stdout)
    sys.stdout.write("\n")


# ---------------------------------------------------------------------------
# PRE —— prevention. The only half that may block.
# ---------------------------------------------------------------------------

def _pre(data):
    fp = _target_path(data)
    if not fp:
        return 0
    base = os.path.basename(fp)
    if not _DEFECT_RE.search(base):
        return 0

    tool = data.get("tool_name")
    tool = tool if isinstance(tool, str) else ""
    fixed = _clean_name(base)

    # ⚠️ THE ONE SCOPE-GUARDED DECISION IN THIS FILE (hook_guide.md §4.7).
    if tool in _WRITE_TOOLS and _in_scope(data):
        # PreToolUse + exit 2 == the tool call is BLOCKED and the message
        # reaches the model. At exit 2 the harness ignores stdout and JSON
        # entirely, so this MUST go to stderr (hook_guide.md §6.8.2).
        sys.stderr.write(
            "flint: BLOCKED —— `" + base + "` has whitespace between the prefix "
            "and its 12-digit timestamp. Root CLAUDE.md §3.3 names comms files "
            "`[prefix]_[TS].md`, with no space. Re-issue this call as `" + fixed
            + "`. (Renaming a file that already carries the defect is `git mv`, "
            "which this gate never touches.)\n"
        )
        return 2

    # Not a write, or not this repo -> advise, never block.
    _advise("PreToolUse", (
        "[flint] Stray-space filename encountered: `" + fp + "`. Root "
        "CLAUDE.md §3.3 names comms files `[prefix]_[TS].md`, with no "
        "space before the 12 digits; this one should be `" + fixed
        + "`. ALERT THE USER (a `⚠️` declaration) —— do not go hunting "
        "for others. Rename only on his say-so, with `git mv` in a "
        "move-only commit (universal/coding.md § Git Discipline)."
    ))
    return 0


# ---------------------------------------------------------------------------
# POST —— detection. GLOBAL, warn-only, NEVER returns 2.
# ---------------------------------------------------------------------------

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
    same-TS pair: identical CP prefix AND roles == {query,response} or
    {close,artefact}."""
    wp, wr = _prefix_role(w_base, ts)
    sp, sr = _prefix_role(sib_base, ts)
    if wp != sp:
        return False
    return frozenset({wr, sr}) in _CLEAN_ROLE_SETS


def _mirror_dir(dirpath):
    """Cross-repo comms mirror of a `.../GitHub/<repo>/<sub>/<YYYY>/<YYYYMM>`
    folder: dupbus `sessions/` <-> AJAP `inv/` for the SAME year-month. Returns
    the mirror path if it exists, else None. Enforces TS-uniqueness across BOTH
    repos, but only the matching year-month sub-folder — so AJAP's huge trees
    are never walked."""
    ap = os.path.abspath(dirpath)
    m = re.search(
        r"^(.*/GitHub/)(dupbus-ceztuc-7cufVe/sessions|AJAP_repo/inv)"
        r"/(\d{4})/(\d{6})$", ap)
    if not m:
        return None
    base, repo, y, ym = m.group(1), m.group(2), m.group(3), m.group(4)
    other = ("AJAP_repo/inv" if repo.endswith("sessions")
             else "dupbus-ceztuc-7cufVe/sessions")
    cand = os.path.join(base, other, y, ym)
    return cand if os.path.isdir(cand) else None


def _entries(d):
    """One listing per folder, reused by BOTH checks below. Splitting this out
    is the whole reason the stray-space sweep is free: it reads nothing the TS
    check was not already reading."""
    try:
        return os.listdir(d)
    except Exception:
        return []


def _post(data):
    # ⚠️ NO SCOPE GUARD ANYWHERE IN THIS FUNCTION —— deliberately GLOBAL. See
    # the REACH note in the module docstring; AJAP coverage depends on it.
    fp = _target_path(data)
    if not fp:
        return 0
    w_base = os.path.basename(fp)

    ts = _find_ts(w_base)
    if not ts:
        return 0  # written file has no TS -> nothing to check, nothing listed

    dirpath = os.path.dirname(fp) or "."

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
             if _DEFECT_RE.search(e)]
    if mdir:
        stray += [os.path.join(mdir, e) for e in sorted(mirror_entries)
                  if _DEFECT_RE.search(e)]
    if stray:
        _advise("PostToolUse", (
            "[flint] Stray-space filename(s) in a folder you just wrote to: "
            + "; ".join("`" + p + "`" for p in stray)
            + ". Root CLAUDE.md §3.3 names comms files `[prefix]_[TS].md`, "
            "with no space before the 12 digits. ALERT THE USER (a `⚠️` "
            "declaration) —— this surfaced on its own, so do NOT go hunting "
            "for others. Rename only on his say-so, with `git mv` in a "
            "move-only commit (universal/coding.md § Git Discipline)."
        ))

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
    if ((not mirror_others) and len(own) == 2
            and _is_clean_pair(w_base, own_others[0], ts)):
        return 0

    parts = []
    if own_others:
        parts.append(", ".join(sorted(own_others)) + " (same folder)")
    if mirror_others:
        parts.append(", ".join(sorted(mirror_others))
                     + " (cross-repo: " + mdir + ")")
    sys.stderr.write(
        "TS clash: `" + w_base + "` shares timestamp " + ts + " with "
        + "; ".join(parts) + " —— only a co-located query_/response_ (or close_/"
        "artefact_) pair may share a TS. Re-stamp the odd one out (or confirm "
        "intentional).\n"
    )
    return 0  # NEVER 2 —— see WHY PRE MUST BLOCK AND POST CANNOT


def main(argv):
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(data, dict):
        return 0
    try:
        if _mode(argv, data) == "post":
            return _post(data)
        return _pre(data)
    except Exception:
        return 0  # FAIL-SAFE: never a traceback, never an exit 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
