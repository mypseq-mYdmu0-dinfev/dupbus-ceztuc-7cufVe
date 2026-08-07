#!/usr/bin/env python3
"""PreToolUse + PostToolUse hook —— "filename linter". ONE lint owning comms
FILENAMES (root CLAUDE.md §3.3, `[prefix]_[12-digit TS].md`), on every part of
that shape: the stray space wedged before the timestamp, anything trailing
AFTER the timestamp, and the timestamp itself clashing with a neighbour. A TS
is part of a filename, so one script.

Root scope: walks TWO repo roots —— `dupbus-ceztuc-7cufVe/sessions/` and
`AJAP_repo/inv/` —— and only their matching `YYYY/YYYYMM` sub-folders, because
those two hold ONE comms stream and TS uniqueness must hold across both. No
other repo is walked: nothing else on this Mac uses the `[prefix]_[TS].md`
convention. The dupbus root is derived from this file's own `__file__` and the
AJAP root from the written path itself, never from the process cwd —— a
user-level hook routinely runs from another repo.

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: the comms-filename gate (root §3.3, `[prefix]_[TS].md`).
* IT BLOCKS a comms name with a space before the 12 digits (`close_ 2026…`)
  or ANYTHING after them (`query_…0423a.md`); re-issue with the name it gives
  —— two files in one minute take consecutive minutes, never `a`/`b`.
  `_moved_[dir]` (§8.1.2) is exempt.
* IT WARNS on a TS clash there or in the AJAP mirror; only
  `query_`+`response_` and `close_`+`artefact_` may share one.
* IT ALERTS on an offender beside a file you wrote: raise a `⚠️`, never hunt.
  Fix with `git mv`.
* Only the block stops a call; else exit 0, silent.
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

DETECTION RULE 1 (STRAY SPACE), stated exactly: the basename must match
`^\\S*_\\s+(?=20\\d{10}(?!\\d))` —— from the START of the name, a whitespace-FREE
run ending in `_`, then one or more whitespace characters, then a 12-digit TS
beginning `20` and not sitting inside a longer digit run. Stated ONCE here and
used by both modes; the duplicate copy that used to live in `tlint.py` is
exactly the drift hazard this merge removes.

DETECTION RULE 2 (TRAILING TAIL), stated exactly: for a basename that is
COMMS-SHAPED (`_COMMS_NAME_RE`: an optional `❌_` void prefix, at most ONE CP
prefix segment, then one of the six roots of root §3.3 —— query, response,
close, wrap, slog, artefact), everything after the first bounded 12-digit TS
must be extension-only (`^(?:\\.[A-Za-z0-9]+)*$`) or a sanctioned `_moved_`
suffix. Anything else is the defect.

WHY RULE 2 EXISTS: two comms files genuinely minted in the same minute were
disambiguated with letter suffixes —— `ccsim_query_202608060423a.md` and
`…0423b.md`. Root §3.3 gives a comms filename exactly one variable part, the
12-digit TS, and every consumer of that name (the `#ww` reader, `close.md`'s
pairing, this file's own TS-clash check, `dlint_quick.py`'s `_TS_SUFFIX_RE`)
parses it positionally. A suffix silently breaks that parse whilst still LOOKING
like a comms file, and the collision it was invented to solve already has a
sanctioned answer: the SECOND file takes the next free MINUTE. So the block
names that minute rather than merely refusing the suffix —— a gate that says
"no" without saying "then what" is re-litigated every time it fires.

WHY THE SUGGESTED NAME IS COMPUTED, NOT JUST "+1 MINUTE": the first offender's
own minute is usually still free (the `a`/`b` pair should have been `0423` and
`0424`, not `0424` and `0425`), so the suggestion tries the CLEAN name first and
only bumps when that TS is actually occupied —— skipping over a sanctioned
`query_`/`response_` or `close_`/`artefact_` sibling, which may share a TS by
design. That listing is the folder `_post()` already reads, so it costs nothing
new. A `response_` gets an extra clause instead of a bare bump: root §3.5.3
BINDS its TS to its `query_`, so telling it to advance a minute would trade one
breach for another.

RULE 2's EXEMPTIONS, each verified against the live tree rather than imagined:
* EXTENSION ONLY —— `.md`, and multi-part forms like `.pages.md`.
* `_moved_[directory]` (root §8.1.2's Move Rule) and its post-extension form
  (`…202606142148.md_moved_skipped`, 2 real files). MANDATED by the root
  protocol: a rule that blocked the Move Rule would be worse than the defect it
  fixes, since the Move Rule is how every rename is recorded.
* `❌_` (root §8.2) is a PREFIX, so it never reaches this test —— but it is in
  `_COMMS_NAME_RE` so a voided comms file is still judged on its tail.
* NOT comms-shaped -> out of scope entirely. This is what spares
  `gscpt/parked/AJAP Logs 202607182259.csv`,
  `chrome_disable_ondevice_model_202607251750.mobileconfig`,
  `temp/…/Alltech_interview_transcript_202607021219_fixed.md`,
  `tests/test_live_202607190438_fixes.py`, the whole `backup_gcl/`
  `…_moved_pending.md` / `_reapplied.md` / `_stale.md` family, and
  `gscpt/parked/git_history_response_202607161603_202607171243.html` (two prefix
  segments before the role, so ONE-prefix matching correctly declines it).
  Calibrated over both comms repos: of 11,589 files, 10,706 carry a bounded
  12-digit TS and 1,344 are comms-shaped; only 10 of those 1,344 carry a tail,
  and every one of the other 24 tail shapes in the tree belongs to a file that
  is not comms-shaped. That 10 is 4 `a`/`b` queued queries plus 6 `_r2`.

`_r2` IS DELIBERATELY NOT EXEMPT, and the cost is stated rather than hidden.
`response_202607072124_r2.md` (1 here, 5 in AJAP `inv/`) is a SECOND response to
one query —— a shape §3.5.3 leaves no clean way to name, since a response may not
re-stamp. Exempting it would carve a hole the `a`/`b` defect fits through
unchanged (`_r2` and `a` differ only in spelling), so the rule stays absolute and
those six files must be renamed or the exemption added deliberately. Until then,
an EDIT of one is blocked and the fix is a `git mv`, which this gate never
touches.

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
was rejected: it would have broken both. Rule 2 is the one place a positive
form IS used, which is precisely why its exemption list is explicit and pinned
by tests rather than left to the shape of a regex.

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

THE MALFORMED-NAME SWEEP IS FREE, and that is the whole reason it sits in the
POST half rather than anywhere else: `_post()` already lists the written file's
own folder (and its mirror) for the TS check, so re-reading that same listing
for BOTH defects costs no extra I/O and no extra token. Both classes report in
ONE advisory, never two: stdout carries a single JSON object, so a second
`_advise()` call would emit a second one and risk the harness parsing neither. It fires only as a by-product
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
* `.githooks/pre-commit` covers the STRAY SPACE only, not the trailing tail, so
  a tail-defective name created outside the harness still reaches history. The
  PreToolUse gate is the only thing rule 2 has; teaching the git hook the same
  rule is the obvious next step and is deliberately not smuggled in here.
* Rule 2 sees COMMS-shaped names only. A tail on anything else is out of scope
  by design —— `_fixed`, `_reapplied` and `_notes` suffixes are ordinary naming
  everywhere else in the tree, and flagging them would be noise, not a lint.

SHAPE GUARDS: `_TS_RE`/`_has_ts` require the 12 digits not to sit inside a
longer run, so a 13+-digit id never reads as a TS nor matches one by substring.
FAIL-OPEN, per `hook_guide.md` §4.4: an unscopeable payload runs the lint anyway
(a silently disabled lint is the failure that guide exists to prevent). The
`isinstance(data, dict)` checks are not decorative: valid JSON that is not an
object would make `.get` raise and exit 1, breaking this file's own fail-safe
promise —— which matters all the more because a user-level registration means
any project's payload can arrive here.
"""

import datetime
import json
import os
import re
import sys
import io
import select
import stat

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

# THE TRAILING-TAIL DEFECT (rule 2). See DETECTION RULE 2 in the docstring.
#
# A COMMS-SHAPED basename: optional `❌_` void prefix (root §8.2), at most ONE
# CP-folder prefix (root §3.3.6 permits exactly one), then one of the six comms
# roots of root §3.3. ONE prefix, never two —— `git_history_response_<TS>_<TS>`
# is a generated artefact, not comms, and two-segment matching would swallow it.
_COMMS_NAME_RE = re.compile(
    r"^(?:❌_)?(?:[A-Za-z0-9][A-Za-z0-9-]*_)?"
    r"(?:query|response|close|wrap|slog|artefact)_", re.IGNORECASE)

# What may follow the TS: nothing, or one or more dot-extensions (`.pages.md`).
_TAIL_OK_RE = re.compile(r"^(?:\.[A-Za-z0-9]+)*$")

# ...plus the Move Rule's `_moved_[directory]` (root §8.1.2), in BOTH observed
# positions —— before the extension (`_moved_202607.md`) and after it
# (`…202606142148.md_moved_skipped`). Exempting this is not a nicety: the Move
# Rule is the protocol's own way of recording every rename, so blocking it would
# make the gate fight the fix.
_MOVED_TAIL_RE = re.compile(r"^(?:\.[A-Za-z0-9]+)*_moved_")

# The trailing extension run of a tail, used to rebuild the corrected name.
# One-or-more (not zero-or-more): a `*` here would match empty at offset 0 and
# `search` would return that, silently dropping every extension.
_EXT_TAIL_RE = re.compile(r"(?:\.[A-Za-z0-9]+)+$")

# How many minutes forward the suggestion may walk before giving up. 60 is an
# hour of consecutive occupied minutes —— far past anything real; the cap exists
# only so a pathological folder cannot spin a PreToolUse hook.
_MAX_MINUTE_BUMP = 60

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


def _tail_defect(base):
    """The offending tail of a comms basename (everything after its 12-digit TS
    that is neither an extension nor a sanctioned `_moved_` suffix), or '' if
    the name is clean —— or is not comms-shaped at all, in which case this rule
    has no opinion about it. Name-only: no filesystem access, so it is equally
    usable by the PRE gate and by the POST folder sweep."""
    if not _COMMS_NAME_RE.match(base):
        return ""
    m = _TS_RE.search(base)
    if not m:
        return ""
    tail = base[m.end():]
    if _TAIL_OK_RE.match(tail) or _MOVED_TAIL_RE.match(tail):
        return ""
    return tail


def _bump_ts(ts, minutes):
    """`ts` advanced by `minutes`, still as YYYYMMDDHHmm. '' if `ts` is not a
    real calendar time —— `_TS_RE` matches 12 digits, not a valid date, so
    `20261399xxxx` reaches here and must not raise inside a hook."""
    try:
        t = datetime.datetime.strptime(ts, "%Y%m%d%H%M")
        return (t + datetime.timedelta(minutes=minutes)).strftime("%Y%m%d%H%M")
    except Exception:
        return ""


def _ts_available(dirpath, ts, cand_base, offender):
    """True if `cand_base` may take `ts` in `dirpath`. Occupied means some OTHER
    file there already carries that TS —— except the offending file itself (it is
    being renamed away) and except a sibling that forms a SANCTIONED same-TS pair
    with the candidate (`query_`/`response_`, `close_`/`artefact_`), which is
    exactly the case root §3.5.3/§3.3.5 require to share one. An unreadable
    folder yields an empty listing, i.e. "available", which errs towards
    suggesting the minute the caller already chose."""
    for e in _entries(dirpath):
        if e == offender or not _has_ts(e, ts):
            continue
        if e == cand_base:
            return False                    # that exact name is already on disk
        if _is_clean_pair(cand_base, e, ts):
            continue
        return False
    return True


def _suggest_name(fp, base, tail):
    """The name the caller should have used: the tail dropped, keeping the TS if
    that minute is free and otherwise walking forward to the first free one.
    Trying the CLEAN name FIRST is what makes an `a`/`b` pair land on
    `…0423`/`…0424` rather than `…0424`/`…0425`."""
    m = _TS_RE.search(base)
    if not m:
        return base
    ts, head = m.group(1), base[:m.start()]
    em = _EXT_TAIL_RE.search(tail)
    ext = em.group(0) if em else ""
    dirpath = os.path.dirname(fp) or "."
    cand = head + ts + ext
    if _ts_available(dirpath, ts, cand, base):
        return cand
    for k in range(1, _MAX_MINUTE_BUMP + 1):
        nts = _bump_ts(ts, k)
        if not nts:
            break
        cand = head + nts + ext
        if _ts_available(dirpath, nts, cand, base):
            return cand
    return head + (_bump_ts(ts, 1) or ts) + ext


def _tail_block_msg(base, tail, fixed):
    """The BLOCK text. It names the FIX, not merely the fault —— a gate that
    refuses without saying "then what" is re-argued every time it fires."""
    extra = ""
    _p, role = _prefix_role(base, _find_ts(base))
    if role.lower() == "response":
        extra = (" NOTE: a `response_` must keep its `query_`'s TS (§3.5.3), so "
                 "if this is a second response to one query, raise it rather "
                 "than re-stamping.")
    return (
        "flint: BLOCKED —— `" + base + "` has `" + tail + "` after its 12-digit "
        "timestamp. Root CLAUDE.md §3.3 ends a comms filename AT the timestamp; "
        "two files minted in one minute take consecutive MINUTES, never an "
        "`a`/`b`/`_r2` suffix. Re-issue this call as `" + fixed + "`." + extra
        + " (The one sanctioned suffix is §8.1.2's `_moved_[directory]`; "
        "renaming a file that already carries the defect is `git mv`, which "
        "this gate never touches.)\n"
    )


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

    # BOTH defect classes, stray space FIRST —— a name carrying both is a
    # whitespace bug foremost, and its message already names the whole fix.
    if _DEFECT_RE.search(base):
        fixed = _clean_name(base)
        block = (
            "flint: BLOCKED —— `" + base + "` has whitespace between the prefix "
            "and its 12-digit timestamp. Root CLAUDE.md §3.3 names comms files "
            "`[prefix]_[TS].md`, with no space. Re-issue this call as `" + fixed
            + "`. (Renaming a file that already carries the defect is `git mv`, "
            "which this gate never touches.)\n")
        advise = (
            "[flint] Stray-space filename encountered: `" + fp + "`. Root "
            "CLAUDE.md §3.3 names comms files `[prefix]_[TS].md`, with no "
            "space before the 12 digits; this one should be `" + fixed + "`.")
    else:
        tail = _tail_defect(base)
        if not tail:
            return 0
        fixed = _suggest_name(fp, base, tail)
        block = _tail_block_msg(base, tail, fixed)
        advise = (
            "[flint] Malformed comms filename encountered: `" + fp + "` carries "
            "`" + tail + "` after its 12-digit timestamp. Root CLAUDE.md §3.3 "
            "ends a comms filename AT the timestamp (a second file in the same "
            "minute takes the NEXT minute, never an `a`/`b` suffix); this one "
            "should be `" + fixed + "`.")

    tool = data.get("tool_name")
    tool = tool if isinstance(tool, str) else ""

    # ⚠️ THE ONE SCOPE-GUARDED DECISION IN THIS FILE (hook_guide.md §4.7).
    if tool in _WRITE_TOOLS and _in_scope(data):
        # PreToolUse + exit 2 == the tool call is BLOCKED and the message
        # reaches the model. At exit 2 the harness ignores stdout and JSON
        # entirely, so this MUST go to stderr (hook_guide.md §6.8.2).
        sys.stderr.write(block)
        return 2

    # Not a write, or not this repo -> advise, never block.
    _advise("PreToolUse", advise + (
        " ALERT THE USER (a `⚠️` declaration) —— do not go hunting "
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

    # --- CHECK 2 —— MALFORMED-NAME SWEEP, both defect classes. Independent of
    # the TS check and reported even when the timestamps are clean, so it must
    # run BEFORE that check's early return. Scans names only: a stat would buy
    # nothing, since a directory carrying the defect is just as wrong as a file.
    def _bad(e):
        return bool(_DEFECT_RE.search(e)) or bool(_tail_defect(e))

    stray = [os.path.join(dirpath, e) for e in sorted(own_entries) if _bad(e)]
    if mdir:
        stray += [os.path.join(mdir, e) for e in sorted(mirror_entries)
                  if _bad(e)]
    if stray:
        # ONE advisory for BOTH classes —— stdout carries a single JSON object,
        # so a second `_advise()` call would emit a second one.
        _advise("PostToolUse", (
            "[flint] Malformed comms filename(s) in a folder you just wrote to: "
            + "; ".join("`" + p + "`" for p in stray)
            + ". Root CLAUDE.md §3.3 names comms files `[prefix]_[TS].md` —— no "
            "space before the 12 digits, and nothing after them (a second file "
            "in the same minute takes the NEXT minute, never an `a`/`b` "
            "suffix). ALERT THE USER (a `⚠️` "
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


# ---------------------------------------------------------------------------
# HOOK-BODY STDIN GUARD
# ---------------------------------------------------------------------------
# This file is a HOOK BODY, not a command-line tool: the harness pipes its JSON
# payload on stdin and closes it, and argv carries a mode word at most, never a
# file to check. Run by hand as `python3 <this> some_file.md`, the payload read
# in main() used to block FOREVER —— on a terminal, and equally on any pipe a
# caller holds open without writing (a background runner, an agent shell). That
# is far worse than merely slow: silence from a hang is indistinguishable from
# silence from a clean pass, so the hand run gets filed as a verification that
# never happened. It has already cost this repo one file recorded as
# "lint clean" when nothing had run at all.
#
# So refuse: fast, on stderr, non-zero, naming the correct incantation. A quiet
# `exit 0` would trade the hang for that same false pass in a new hat, which is
# why this path must never return success.
#
# Under the harness the payload is written and stdin closed before this runs,
# so `select` reports it readable at once and the guard costs nothing on the
# real path. The wait exists only for the caller holding an empty pipe open ——
# far longer than a local payload write, far shorter than a lost session.
#
# READINESS IS NOT ARRIVAL, and getting that wrong recreated the whole defect.
# `/dev/null`, a closed descriptor and a pipe already at EOF are all READY: a
# read on them returns immediately, with nothing. An agent shell hands its
# children `/dev/null`, so `python3 <this> some_file.md` there sailed past a
# readiness-only guard, read zero bytes, failed to parse them, and exited 0 in
# silence —— the SAME false pass as the hang, reached by a shorter route. So
# three things are checked, not one: argv that no hook ever passes, stdin that
# never becomes readable, and stdin that is readable but delivers nothing.
#
# RESIDUAL, stated rather than papered over: a caller that writes a PARTIAL
# payload and then holds the pipe open still blocks in the read below, exactly
# as it did before any of this existed. Closing that needs a deadline around
# the read, which buys nothing on the harness path (it always closes stdin)
# and adds moving parts to a gate that BLOCKS writes.
_HOOK_STDIN_WAIT_S = 2.0

# Extensions a caller reaches for when treating this file as a CLI. A hook mode
# word never carries one, so this cannot collide with `pre`/`post`, nor with
# the junk argv flint deliberately tolerates (pinned by its own suite, M5).
_HOOK_FILEY_EXTS = frozenset((".md", ".py", ".sh", ".json", ".jsonl", ".txt",
                              ".html", ".yml", ".yaml", ".csv"))


def _argv_names_a_file(arg):
    """True when this argument is a caller handing over a file to check."""
    return ("/" in arg or "\\" in arg
            or os.path.splitext(arg)[1].lower() in _HOOK_FILEY_EXTS)


def _hook_stdin_is_pipe():
    """True when stdin is the pipe or socket a harness hands a hook body.

    An EMPTY payload means opposite things on either side of this line. Over a
    PIPE it means the harness sent nothing, and every lint here fails OPEN on
    that by a contract its own suite pins —— a lint may never break a turn.
    Over `/dev/null`, a closed descriptor, a terminal or a plain file it means
    no payload was ever coming, which is a hand invocation and must never be
    allowed to read as a pass. Unknowable shapes count as a pipe, so an odd
    environment can only ever fail towards leaving the lint armed.
    """
    try:
        mode = os.fstat(sys.stdin.fileno()).st_mode
        return stat.S_ISFIFO(mode) or stat.S_ISSOCK(mode)
    except Exception:
        return True


_HOOK_STDIN_HOWTO = (
    '  printf \'%s\' \'{"hook_event_name":"PreToolUse",'
    '"tool_name":"Write",'
    '"tool_input":{"file_path":"/abs/file.md"}}\' \\\n'
    '    | python3 cscpt/flint.py pre\n'
)


def _hook_refusal(reason):
    """Say outright that nothing ran, then leave non-zero. NEVER exit 0 here:
    a silent success is the very thing this guard exists to prevent."""
    sys.stderr.write(
        "%s is a hook body, not a command-line tool. It reads its JSON hook\n"
        "payload on stdin and ignores its arguments, so NOTHING WAS CHECKED ——\n"
        "do not read this silence as a pass.\n"
        "Cause: %s.\n"
        "Run it by hand from the repo root with:\n%s\n"
        % (os.path.basename(__file__), reason, _HOOK_STDIN_HOWTO))
    # Exit 3, never 2: on Pre/PostToolUse a 2 BLOCKS the tool call,
    # and a hand invocation must not be able to block anything. Every other
    # non-zero code merely shows this message; none of them blocks.
    sys.exit(3)


def _require_hook_payload(argv=()):
    """Return only if a real hook payload arrived; else explain and exit 3.

    On success `sys.stdin` is re-seated on the text already consumed, so the
    caller's `json.load(sys.stdin)` reads exactly what the harness sent and
    needs no change. `sys.exit` raises SystemExit, which is NOT an Exception,
    so the fail-open handlers below cannot swallow a refusal.
    """
    stray = [a for a in argv if _argv_names_a_file(a)]
    if stray:
        _hook_refusal(
            "argv names the file %r, and no hook event ever passes one —— the "
            "file to check arrives in the payload, never on the command line"
            % stray[0])
    try:
        if sys.stdin is None:
            _hook_refusal("this process has no stdin at all (descriptor 0 closed)")
        if sys.stdin.isatty():
            _hook_refusal("stdin is a terminal, so no payload can ever arrive")
        piped = _hook_stdin_is_pipe()
        ready = select.select([sys.stdin], [], [], _HOOK_STDIN_WAIT_S)[0]
    except Exception:
        return  # an unselectable stdin must never disarm the lint
    if not ready:
        _hook_refusal("nothing reached stdin within %gs" % _HOOK_STDIN_WAIT_S)
    try:
        raw = sys.stdin.read()
    except Exception:
        return  # an unreadable stdin must never disarm the lint
    if not raw.strip() and not piped:
        _hook_refusal(
            "stdin delivered nothing and is not a pipe —— `/dev/null`, a closed "
            "descriptor or a plain file, which is what a shell hands a command "
            "run by hand. An EMPTY PIPE is left alone on purpose: that is the "
            "harness sending nothing, and every lint here fails open on it")
    sys.stdin = io.StringIO(raw)


def main(argv):
    _require_hook_payload(sys.argv[1:])
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
