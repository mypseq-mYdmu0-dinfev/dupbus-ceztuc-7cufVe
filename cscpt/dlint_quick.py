#!/usr/bin/env python3
"""dlint `--quick` Runner + Deliverable-Escape Gate (PostToolUse hook)

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: the ONLY lint that can BLOCK. It fires on EVERY `.md` write here, runs
  `dlint.py --quick`, and refuses the turn whilst any 🔴 RED remains. It also
  BLOCKS a `response_`/`close_`/`wrap_` write whilst a deliverable you wrote
  still owes a FULL `dlint.py` run.
* IF IT BLOCKS (exit 2): the reason is on stderr. Fix, rewrite; it loops.
* NOT YOUR PROSE (a transcript, a quoted document)? Add `<!-- dlint: skip -->`
  once —— permanent. NEVER rewrite captured text to satisfy it. No escape
  exists for comms.
* 🟡 YELLOW never blocks; justify yellows as that file's LAST content.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WIRING. Run by the harness via `dlint_hook.sh`, the registered bash fast-path:
shim -> this file -> `dlint.py --quick`. Registered PostToolUse
(Edit|Write|MultiEdit) in the USER-level `~/.claude/settings.json` —— the
Claude Desktop app executes user-level hooks and silently ignores project-level
ones. IN: PostToolUse JSON on stdin. FAIL-SAFE: any error, missing field,
non-match, or a missing/slow `dlint.py` (30 s timeout) -> exit 0, so it never
blocks on its own failure.

NAMED `_quick`, NOT `_hook`: the registered hook is `dlint_hook.sh`. Across
`cscpt/` every `.sh` carries `_hook` and no `.py` does, so the filename tells
the truth about which file the harness actually launches.

SCOPE IS LOAD-BEARING because this is the one lint in the chain that BLOCKS:
under user-level registration it would otherwise pass judgement on any
project's `.md` against a style guide that has nothing to do with it. Hence
`_in_scope` runs BEFORE anything else, and the TARGET path must also resolve
inside this repo (a session here can still write elsewhere). Scope FAILS OPEN
on an unscopeable payload —— that is not evidence of a different project, and a
lint going dark on ambiguity is the failure this wiring exists to fix.

WHY THE SCOPE IS NOW EVERY `.md`, NOT THREE FILENAME ROLES. It used to fire
only on a basename containing `response_`/`close_`/`wrap_`. Everything else CC
wrote —— pcmd, guides, notes, one-pagers, anything under `temp/` —— was
covered by nothing, so a British-spelling or Hart's-quotation breach shipped
whenever it landed outside those three names. The owner's ruling: nothing but
code is exempt from `--quick`. Role and extension alone decide scope; there are
no per-folder carve-outs, and an earlier one was removed rather than repointed
once its target retired. Resist adding another.

WHAT "SCOPE" DOES AND DOES NOT MEAN, because the paragraph above reads wider
than the behaviour. This hook judges ONE file per invocation: the `file_path`
the harness just handed it. It never walks the repo, never opens a second `.md`,
and cannot fail a write because some OTHER file is non-compliant. Any count of
how many files in the repo would fail if they were linted (they are not) is a
BLAST-RADIUS estimate for a hypothetical sweep, and never describes a write.
Within that one file, carve-out 2 narrows further still.

THE THREE CARVE-OUTS, NAMED AS CARVE-OUTS RATHER THAN BURIED.
  1. `query_` files are SKIPPED ENTIRELY. Pre-existing and preserved: a
     `query_` carries the USER's words verbatim (root §3.6.2 has CC transcribe
     them on his behalf). Blocking on a breach in his own sentence would force
     CC either to falsify the record or to mark it, and neither is a service.
  2. On any file that is NOT comms, the verdict is scoped to THE TEXT THIS
     WRITE PRODUCED (`Write` content, `Edit`/`MultiEdit` new_string), not the
     whole file. Measured before shipping: widening to every `.md` would put 84
     of 521 recently-touched files into hard-block range IF each were rewritten
     wholesale (none is linted until it is written), and the overwhelming
     majority were captured third-party text —— lecture transcripts, zoom
     recordings, official course files, job descriptions —— where the only
     "fix" is to rewrite somebody else's words. CC is accountable for the prose
     she just wrote, not for prose she is editing around. Whole-file linting
     survives untouched for comms (below), so nothing enforced before this
     change is enforced less now.
  3. `<!-- dlint: skip -->` (or `dlint: internal`) in a NON-comms file silences
     it permanently, for the case carve-out 2 cannot reach: capturing a whole
     transcript in ONE `Write`, where every line is new text and none of it is
     CC's. Auditable by `grep -rn 'dlint: skip'`, so a dismissal is a
     deliberate reviewable act rather than a silent omission.
COMMS FILES (`response_`/`close_`/`wrap_`, substring match, CP prefixes and the
`hook_probe_response_.md` liveness probe included) get NONE of carve-outs 2 or
3: whole file, every time, no escape. CC authored the whole thing, so the whole
thing is hers. That is exactly the behaviour this file had before, so the
change is purely additive.
  WHOLE-FILE ON COMMS IS MANDATED, not a preference this file is free to relax:
  root `CLAUDE.md` §3.5.5 requires a `--quick` run after writing or editing ANY
  `response_`, and §3.5.6 requires every 🔴 RED in it driven to zero, naming
  this hook as the enforcement. Scoping a comms verdict to the edited fragment
  would let a `response_` end a turn with RED still in it, which is the one
  outcome §3.5.6 forbids. The residual, stated rather than fixed: editing a
  comms file written in an EARLIER session re-judges that session's text too.
  It is rare, it is still CC's own prose, and narrowing it would cost the §3.5.6
  guarantee on every ordinary turn to buy relief on an unusual one.

THE REMINDER. Every non-blocking run emits ONE line of
`hookSpecificOutput.additionalContext` —— the only PostToolUse channel that is
both model-visible and non-blocking (hook_guide §6.5). It asks whether the file,
OR A PART OF IT, warrants FULL `dlint.py` instead. `--quick` deliberately keeps
only the register-independent rules, so a file mixing internal strategy notes
with deliverable-bound prose passes quick whilst the deliverable half is
un-linted; the answer there is to EXTRACT that half and run FULL mode on the
extract (`writing.md` § Deliverable Lint). Emitted once per (session, file), so
redrafting is never nagged.

THE READ ADVISORY RIDES THE SAME CHANNEL, and unlike the reminder it fires
EVERY time. `--quick`'s one judgement-requiring YELLOW ("N bare `read` left to
judge" —— past/perfect wants `#r`, per `glossary.md`) used to reach CC on ONE
path only: the exit-2 stderr write a RED triggers. A clean run discarded the
whole report, so on the majority of writes the advisory was raised by the
linter and seen by nobody. `_read_note` lifts that one line out and forwards
it, and there is no per-session memory of having done so —— the owner's ruling
is that a false positive costs ~10 tokens whilst a false negative "could be
highly misleading", and both suppressions this file used to apply were
false-negative machines. It shares the ONE `_emit_context` call with the
reminder: stdout carries a single JSON object, so two calls would emit two and
the harness would parse neither.
  NO OTHER YELLOW IS FORWARDED. The rest are stylistic and already covered by
root §3.5.5's own `--quick` run over every `response_`. This one is the only
quick rule whose verdict a machine cannot reach, which is exactly why losing it
matters and why forwarding it is not the thin end of a wedge.

THE GATE (formerly `elint.py`'s Tier B, folded in here). A deliverable-shaped
file that has never passed FULL `dlint.py` BLOCKS the comms write that would
hand it over. This is the only actual enforcement of root §3.7.3 outside comms,
and it earned its place: a real interview cheat sheet was drafted, debated
twice, and sent, and a retroactive FULL run found 18 🔴 RED. That is a
NOT-NOTICED failure (`cp/ccsim/CLAUDE.md` §8.7), which more prose cannot repair.

WHY IT LIVES HERE NOW. It used to be a separate script on two registrations
with three tiers. Tier A (advise at the deliverable's own write) became
redundant the moment this file started firing on that same write with the same
reminder. Tier C (a Stop-time warning) reached only the user and duplicated
what Tier B had already blocked. What remains is one predicate —— "a comms file
is being written whilst a deliverable is un-linted" —— and it needs the same
payload, the same repo scope and the same file this hook already has, so a
second script and a second registration bought nothing but a second thing to
keep alive.

DELIVERY, not merely a write, is the choke point: a deliverable is written and
rewritten many times but handed over once, and in this repo handing over IS the
comms file that names it. The block lands BEFORE root §3.1.6's turn-end
actions, so the fix costs no extra turn and disturbs no declaration batch.

THE RECEIPT LEDGER —— WHY CONTENT-ADDRESSED. `dlint.py` appends one line to
`cscpt/.dlint_receipts.jsonl` on every FULL-mode FILE lint: realpath, SHA-256
of the text as it stands on disk after the quote auto-fix, and the RED count.
`--quick` and `--text` write nothing, so a receipt's existence already proves
FULL mode ran. Keying on CONTENT is load-bearing three ways: a deliverable
drafted on Monday and sent on Friday stays covered; a file linted clean and
then EDITED loses its receipt automatically because the hash moved, which is
correct since the edit is un-linted text; and a lint that ended with RED > 0
records `r > 0`, so a FAILED lint can never pass as a clean one. `dlint.py`
alone writes and prunes it; this file only reads.

THE PENDING LEDGER —— A DIRECTORY, NOT A FILE. One small JSON marker per
(session, file) under `cscpt/.dlint_state/s_<hash>/`. Independent markers have
no read-modify-write race across the parallel writes one turn issues, whereas a
single shared JSON would (coding.md § Concurrency: one writer per shared
mutable file). Losing this state costs a missed reminder or a missed gate ——
the harmless direction. Losing the RECEIPT ledger would instead cost a false
alarm, which is why receipts live in a durable git-ignored file rather than a
self-cleaning temp dir.

WHAT A DELIVERABLE IS, MECHANICALLY. `universal/glossary.md` defines it as
anything to be sent or potentially exposed to a third party, which no file
attribute can decide. So the classifier answers a narrower, decidable question
—— IS THIS PLAUSIBLY PROSE FOR SOMEONE OTHER THAN CC? —— as four gates, ALL of
which must pass: a prose extension; inside this repo; not in protocol territory
and not a protocol-shaped NAME; and enough substance to be prose at all
(`_MIN_SUBSTANCE`), which drops stubs and index fragments for free.

RECONSIDERED AFTER THE SCOPE WIDENING, AND KEPT. The obvious cut was to retire
the territory map now that `--quick` sees every `.md`. It does not follow:
`--quick` keeps only the register-independent rules, so "has this been
quick-linted" says nothing about whether it needs FULL mode, which is the only
question the gate asks. What DID go: the `cp/ccsim/sandbox/` scratch exemption
and its probe file, which existed solely to keep Tier A's fixture from becoming
a permanent Tier B obligation —— with Tier A gone, `cp/` territory already
covers the sandbox and the special case is dead weight.

WHY TERRITORY IS A DENY-LIST, NOT AN ALLOW-LIST. An allow-list of
deliverable-shaped paths (`temp/*/output/`) or names (`CHEATSHEET_*`) is
precise where it matches and blind everywhere else, so the same miss returns
under a different filename —— and the real case ALSO produced `SPEECH_*`,
`mini_SPEECH_*`, and `<Client>_<Doc>_<Name>.md`, none of which any plausible
allow-list would have held. Naming the INTERNAL trees inverts that: they are
finite, stable, repo-owned, and everything else is flagged BY DEFAULT, so a new
`deliverables/` or `client_x/` folder is covered the day it appears.

THE HONEST LIMIT OF THAT. No folder in this repo separates the two cleanly.
Root §3.4.2.1 sends non-comms output to the COMMS folder, so `sessions/` holds
both; `cp/` holds protocol files AND a CV. The territory rule is a good
default, not a proof, and the design's real answer is that BOTH errors are
correctable ONCE, permanently, in one line, at the moment of the misfire:
  * `<!-- dlint: internal -->` (or `skip`) —— never a deliverable.
  * `<!-- dlint: deliverable -->` —— always one. Beats territory.
A false positive costs one line, once; a false negative is an un-linted
deliverable in a third party's hands. Those are not comparable, so `cp/` and
the role-named comms files are the ONLY places the default may suppress.

TERRITORY, WITH THE REASON FOR EACH (see `_PROTOCOL_DIRS`):
  * `universal/`, `cscpt/`, `nscpt/`, `gscpt/`, `.claude/`, `.git/` —— pcmd and
    tooling; nothing here is ever sent anywhere.
  * `backup/` —— mirrors written by `mirror.sh`, not authored output.
  * `cp/` —— Claude Project PROTOCOL territory (root §6, §8.4). ACCEPTED FALSE
    NEGATIVE, named honestly: `cp/career/culous_yu_resume_*.md` and
    `cp/dissertation/MGTK751_A*.md` ARE deliverables and are NOT flagged. They
    need `<!-- dlint: deliverable -->` once. Excluding the tree is the lesser
    evil because every OTHER `.md` there —— CLAUDE.md, CP_index, _bg, _guide,
    backlog, and a dozen pcmd —— would otherwise nag forever.
  * `temp/temp_archive/` —— "never touch" per `temp/README.md`.
  * any `input/`, `resource/` or `build/` segment —— `temp/README.md` defines
    those as provided material, retrieved/generated material, and scratch;
    only `output/` is the deliverable slot. Written as a deny-list of the other
    three rather than an allow-list of `output/`, so a folder ignoring the
    convention is still covered.
  * `sessions/queued_queries/` —— query drafts, i.e. comms.
`sessions/` itself is deliberately IN scope apart from role-named files,
because root §3.4.2.1 makes it the DEFAULT home for a separate-file deliverable.
Excluding it wholesale would re-open the exact gap.

NAME EXCLUSIONS: the comms roles of root §3.3 anchored after at most ONE CP
prefix, plus machinery files identified by a 12-digit timestamp SUFFIX together
with a role word at any depth. The timestamp is what keeps
`Client_Project_Response_Plan.md`, a perfectly ordinary deliverable name, from
being swallowed by the second rule. Those role lists are a CONVENIENCE, not the
mechanism —— a role missing from them costs exactly one marker line.

THE GATE'S LOOP GUARD: it blocks at most ONCE per (session, deliverable), then
degrades to an advisory. Without that, a legitimate post-lint edit (a typo fix
moves the hash, so the receipt correctly lapses) could block every subsequent
comms write in the turn.

LOGGING: every invocation appends one line to `cscpt/.dlint.log` (git-ignored),
tagged by the stage reached, so "the hook never fired" stays distinguishable
from "it fired and found nothing" (hook_guide §7.7) —— an empty log is
otherwise consistent with both, which is how dead wiring once survived weeks.

KNOWN GAPS, so nobody reads more assurance into this than it earns:
  * A deliverable written AFTER the turn's last comms file is only reminded
    about; the gate has nothing left to hold.
  * A turn that writes a deliverable and NO comms file never reaches the gate.
  * `.html`, `.pages`, `.docx` and `.key` deliverables are out of scope:
    `dlint.py` reads plain prose and would flag markup as breaches.
  * Files written outside this repo are never linted or classified.
  * Carve-out 2 means a pre-existing RED in a non-comms file is never
    surfaced by the hook —— only a FULL or manual `--quick` run finds it.
  * Past `_MAX_PENDING_PER_SESSION` distinct files in one session, new
    REMINDER markers stop being created, so the overflow goes un-reminded.
    Deliberate: unbounded state is the worse failure, and a missed reminder
    costs nothing. GATE markers are exempt from the cap —— dropping one would
    silently un-gate a real deliverable.
"""

import sys
import io
import select
import stat
import os
import re
import json
import time
import shutil
import hashlib
import subprocess

# ---------------------------------------------------------------------------
# ANCHORS. Every path is derived from this file's OWN location, never from the
# process cwd —— a user-level hook routinely runs with the cwd of a different
# project entirely (hook_guide §4.5.2).
# ---------------------------------------------------------------------------
_CSCPT = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT_REAL = os.path.realpath(os.path.dirname(_CSCPT))
_REPO_SLUG = re.sub(r"[/ ]", "-", _REPO_ROOT_REAL.rstrip("/"))

_DLINT = os.path.join(_CSCPT, "dlint.py")
# Written by `dlint.py` (sole writer), read here. The constant is duplicated in
# dlint.py by necessity —— the two are separate processes and neither imports
# the other; both derive it from their own `__file__`, so a repo move keeps
# them pointing at the same file.
_RECEIPTS = os.path.join(_CSCPT, ".dlint_receipts.jsonl")
_STATE_ROOT = os.path.join(_CSCPT, ".dlint_state")
_LOG = os.path.join(_CSCPT, ".dlint.log")

# Quick-lint scope. The owner's ruling is "any .md"; `.txt` is linted too
# because dlint reads plain prose and a `.txt` is no more code than a `.md`.
_LINT_EXTS = {".md", ".txt"}
# The gate classifies the same set —— a deliverable can perfectly well be a
# `.txt`, and keeping one set means one thing to reason about.
_PROSE_EXTS = _LINT_EXTS

# COMMS SCOPE —— substring, deliberately loose and UNCHANGED from before this
# file was widened, so `career_response_*.md` and the `hook_probe_response_.md`
# liveness probe (hook_guide §7.2.5) both still land here. Whole-file lint, no
# marker escape, no write-scoping.
_COMMS_SUBSTRINGS = ("response_", "close_", "wrap_")

# The user's own words, transcribed by CC on his behalf (root §3.6.2). Skipped
# outright —— see CARVE-OUT 1 in the docstring.
_QUERY_RE = re.compile(r"^(?:[A-Za-z0-9][A-Za-z0-9-]*_)?query_", re.IGNORECASE)

# A comms file whose write means "this turn's output is being handed over".
# `query_` is excluded —— it carries the USER's words, not a delivery. ONE
# optional CP prefix only, per root §3.3.6; a looser prefix would make
# `hook_probe_response_.md` read as a delivery and block an unrelated probe.
_DELIVERY_RE = re.compile(
    r"^(?:[A-Za-z0-9][A-Za-z0-9-]*_)?"
    r"(?:response|close|wrap|artefact)_", re.IGNORECASE)

# Comms roles of root §3.3, anchored at the start after at most ONE optional
# CP-folder prefix, which is exactly what §3.3.6 permits. Precise, and true
# with or without a timestamp.
_COMMS_ROLES = ("query", "response", "close", "wrap", "slog", "artefact")
_COMMS_RE = re.compile(
    r"^(?:[A-Za-z0-9][A-Za-z0-9-]*_)?(?:" +
    "|".join(_COMMS_ROLES) + r")_", re.IGNORECASE)

# Machinery files this repo generates —— debate boards, digests, handoffs,
# revert logs. Their role word can sit at ANY depth
# (`dissertation_A1Rv2_debate_suggestions_<TS>.md`), so the anchored rule above
# cannot reach them. The obvious repair —— letting that rule skip two prefix
# segments —— was tried and REJECTED, because it also swallows an ordinary
# deliverable name: `Client_Project_Response_Plan.md` would have matched, and a
# false NEGATIVE is the failure this gate exists to prevent. What separates the
# two is the 12-digit timestamp SUFFIX every session-keyed machinery file
# carries (root §2.2.1) and a hand-named deliverable generally does not. So the
# rule fires only when BOTH hold. `board` and `log` were considered and
# dropped: both are ordinary English a real deliverable can carry
# (`Acme_Board_Briefing_<TS>.md`), and every machinery file they would have
# caught already carries `debate` or `revertlog` as another segment.
_MACHINERY_ROLES = frozenset(_COMMS_ROLES) | frozenset((
    "debate", "digest", "handoff", "revertlog",
))
_TS_SUFFIX_RE = re.compile(r"_\d{12}$")

# First repo-relative path segment that puts a file in protocol territory.
_PROTOCOL_DIRS = {
    "universal", "cscpt", "nscpt", "gscpt", "backup", ".claude", ".git", "cp",
}
_EXCLUDED_PREFIXES = (
    ("temp", "temp_archive"),
    ("sessions", "queued_queries"),
)
_NON_OUTPUT_SEGMENTS = {"input", "resource", "build"}
_EXCLUDED_BASENAMES = {
    "claude.md", "readme.md", "cp_instr.md", "placeholder.md",
    "last_seen.md", "backlog.md",
}

# The overrides. Matched anywhere in the file, in any comment syntax —— the
# payload is the token, not the wrapper, so `<!-- dlint: internal -->`,
# `# dlint: internal`, and a bare line all work.
_OPT_OUT_RE = re.compile(r"dlint:\s*(?:internal|skip)\b", re.IGNORECASE)
_OPT_IN_RE = re.compile(r"dlint:\s*deliverable\b", re.IGNORECASE)

# Non-whitespace characters below which a file is not prose worth gating.
_MIN_SUBSTANCE = 200

# Backstops, none hit in normal use. `_MAX_ARG_TEXT` keeps the write-scoped
# lint (carve-out 2) clear of ARG_MAX; past it the whole file is linted
# instead, which is the stricter direction.
_MAX_READ_BYTES = 512 * 1024
_MAX_ARG_TEXT = 200 * 1024
_MAX_PENDING_PER_SESSION = 200
_STATE_TTL_S = 7 * 24 * 3600
_MAX_SWEEP = 200
_LOG_MAX_LINES = 800
_DLINT_TIMEOUT_S = 30


# ---------------------------------------------------------------------------
# SCOPE GUARD —— user-level registration fires in EVERY project on this Mac, so
# self-scope to THIS repo and exit silently elsewhere. Signals, in order: the
# payload's `cwd`, else the `~/.claude/projects/<slug>/` transcript slug —— both
# compared against values derived from this file's OWN location, never a
# hard-coded path. FAILS OPEN when neither is usable.
# ---------------------------------------------------------------------------
def _in_scope(data):
    """True if this invocation's project is THIS repo (or a sub-path of it), or
    if scope genuinely cannot be determined (FAIL-OPEN). Never raises: any
    unexpected error here must default to "run the lint", exactly like every
    other fail-safe path in this file."""
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
            # present but not the recognised shape -> unparseable -> fall through
        return True                                   # neither usable -> FAIL-OPEN
    except Exception:
        return True                       # never let a scope error silence the lint


# ---------------------------------------------------------------------------
# PATHS / IO
# ---------------------------------------------------------------------------
def _repo_rel(path):
    """Repo-relative POSIX segments, or None if the path is outside the repo.
    `realpath` first so a symlinked or `/private/var` form cannot smuggle a
    protocol file past the territory map."""
    try:
        real = os.path.realpath(path)
    except Exception:
        return None
    if real != _REPO_ROOT_REAL and not real.startswith(_REPO_ROOT_REAL + os.sep):
        return None
    rel = os.path.relpath(real, _REPO_ROOT_REAL)
    return [p for p in rel.replace("\\", "/").split("/") if p and p != "."]


def _abs_target(fp, cwd):
    """Absolute path for a payload's `file_path`. A RELATIVE one resolves
    against the PAYLOAD's `cwd`, never this process's own —— the harness may
    launch a hook from anywhere, so `os.path.abspath` alone would silently
    resolve against the wrong tree and every territory verdict would be
    nonsense."""
    if not os.path.isabs(fp) and isinstance(cwd, str) and cwd:
        fp = os.path.join(cwd, fp)
    return os.path.abspath(fp)


def _read_text(path):
    """File text, bounded. None on any failure —— an unreadable file is never
    classified, which errs towards silence."""
    try:
        with open(path, "rb") as fh:
            raw = fh.read(_MAX_READ_BYTES)
        return raw.decode("utf-8", "replace")
    except Exception:
        return None


def _q(path):
    """Repo-relative where possible, shell-quoted when it holds a space —— the
    reader pastes this straight into a terminal."""
    try:
        segs = _repo_rel(path)
        rel = "/".join(segs) if segs else path
    except Exception:
        rel = path
    return "'%s'" % rel if " " in rel else rel


def log(action, detail=""):
    """One line per invocation. Self-pruning; never raises."""
    try:
        line = "%s\t%s\t%s\n" % (
            time.strftime("%Y-%m-%dT%H:%M:%S"), action,
            re.sub(r"\s+", " ", str(detail))[:200])
        with open(_LOG, "a", encoding="utf-8") as fh:
            fh.write(line)
        if os.path.getsize(_LOG) > _LOG_MAX_LINES * 160:
            with open(_LOG, "r", encoding="utf-8", errors="replace") as fh:
                keep = fh.readlines()[-(_LOG_MAX_LINES // 2):]
            tmp = _LOG + ".tmp%d" % os.getpid()
            with open(tmp, "w", encoding="utf-8") as fh:
                fh.writelines(keep)
            os.replace(tmp, _LOG)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# CLASSIFIER (the gate's only question: does this need FULL dlint?)
# ---------------------------------------------------------------------------
def _name_is_internal(base):
    """True if the BASENAME alone marks this as protocol furniture, a comms or
    machinery file, or a file root CLAUDE.md says to disregard."""
    low = base.lower()
    if low in _EXCLUDED_BASENAMES:
        return True
    if base.startswith("❌_"):                       # voided (root §8.2)
        return True
    if low.startswith("temp_"):                      # to be deleted soon (§8.3.2)
        return True
    if "user_notes" in low:                          # private notes (§8.3.1)
        return True
    stem = os.path.splitext(low)[0]
    if stem.endswith("_otg"):                        # OTG variant (§8.3.3)
        return True
    if low.endswith("_devplan.md"):
        return True
    if _COMMS_RE.match(base):
        return True
    stem = os.path.splitext(base)[0]
    if _TS_SUFFIX_RE.search(stem):
        if set(s.lower() for s in stem.split("_")) & _MACHINERY_ROLES:
            return True
    return False


def _territory_is_internal(segs):
    """True if the repo-relative path sits in protocol/tooling territory."""
    if len(segs) <= 1:
        return True                                  # a repo-ROOT file is furniture
    if segs[0] in _PROTOCOL_DIRS:
        return True
    for pref in _EXCLUDED_PREFIXES:
        if tuple(segs[:len(pref)]) == pref:
            return True
    if _NON_OUTPUT_SEGMENTS.intersection(segs[:-1]):
        return True
    return False


def classify(path, text=None):
    """(is_deliverable, reason). `reason` is for the log, never for the user.

    Gate order is cheapest-first, but the two content OVERRIDES are read before
    the territory verdict is returned, so a marker always wins over the default
    in BOTH directions."""
    base = os.path.basename(path)
    if os.path.splitext(base)[1].lower() not in _PROSE_EXTS:
        return False, "ext"
    segs = _repo_rel(path)
    if segs is None:
        return False, "outside_repo"
    if not os.path.isfile(path):
        return False, "missing"
    if text is None:
        text = _read_text(path)
    if text is None:
        return False, "unreadable"
    if _OPT_OUT_RE.search(text):
        return False, "marked_internal"
    forced = bool(_OPT_IN_RE.search(text))
    if not forced:
        if _name_is_internal(base):
            return False, "name"
        if _territory_is_internal(segs):
            return False, "territory"
        if len(re.sub(r"\s+", "", text)) < _MIN_SUBSTANCE:
            return False, "thin"
    return True, ("marked_deliverable" if forced else "shape")


def digest_of(path, text=None):
    """SHA-256 of the file as it stands on disk, matching what `dlint.py`
    hashes into a receipt. None if unreadable."""
    if text is None:
        text = _read_text(path)
    if text is None:
        return None
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


def receipt_status(path, digest):
    """"clean" (FULL lint passed on exactly this content), "red" (FULL lint ran
    on this content and left RED flags), or None (never FULL-linted at this
    content). An unreadable ledger -> None, i.e. treat as un-linted, which is
    the flagging direction."""
    if not digest:
        return None
    try:
        real = os.path.realpath(path)
    except Exception:
        return None
    best = None
    try:
        with open(_RECEIPTS, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("p") != real or rec.get("h") != digest:
                    continue
                best = "clean" if int(rec.get("r") or 0) == 0 else "red"
                if best == "clean":
                    return "clean"
    except Exception:
        return None
    return best


# ---------------------------------------------------------------------------
# PENDING LEDGER —— one marker file per (session, file)
# ---------------------------------------------------------------------------
def _session_dir(session_id):
    sid = hashlib.sha1(str(session_id).encode("utf-8", "replace")).hexdigest()
    return os.path.join(_STATE_ROOT, "s_" + sid[:16])


def _marker_path(sdir, path):
    key = hashlib.sha1(
        os.path.realpath(path).encode("utf-8", "replace")).hexdigest()
    return os.path.join(sdir, key[:20] + ".json")


def _sweep_state(keep):
    """Drop session folders past the TTL. Bounded, best-effort, silent ——
    housekeeping must never cost a tool call."""
    try:
        names = sorted(os.listdir(_STATE_ROOT))[:_MAX_SWEEP]
    except Exception:
        return
    cutoff = time.time() - _STATE_TTL_S
    for name in names:
        p = os.path.join(_STATE_ROOT, name)
        if p == keep:
            continue
        try:
            if os.path.getmtime(p) < cutoff:
                shutil.rmtree(p, ignore_errors=True)
        except Exception:
            pass


def marker_put(session_id, path, digest=None, owed=None, reminded=None,
               blocked=None):
    """Create or update this (session, file) marker. Returns the stored dict,
    or None if the state is unusable —— in which case the caller loses a
    reminder or a gate hold, the harmless direction."""
    try:
        sdir = _session_dir(session_id)
        fresh = not os.path.isdir(sdir)
        os.makedirs(sdir, exist_ok=True)
        if fresh:
            _sweep_state(sdir)
        mp = _marker_path(sdir, path)
        cur = {}
        if os.path.isfile(mp):
            try:
                with open(mp, "r", encoding="utf-8") as fh:
                    cur = json.load(fh) or {}
            except Exception:
                cur = {}
        elif len(os.listdir(sdir)) >= _MAX_PENDING_PER_SESSION and not owed:
            # Past the cap, stop minting REMINDER markers —— unbounded state is
            # the worse failure and a missed reminder costs nothing. A GATE
            # marker is exempt: dropping one would silently un-gate a real
            # deliverable, which is the failure this whole file exists to stop.
            return None
        cur["p"] = os.path.realpath(path)
        cur["h"] = digest or ""
        cur["t"] = int(time.time())
        for k, v in (("owed", owed), ("reminded", reminded),
                     ("blocked", blocked)):
            if v is not None:
                cur[k] = int(v)
            cur.setdefault(k, 0)
        tmp = mp + ".tmp%d" % os.getpid()
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(cur, fh)
        os.replace(tmp, mp)
        return cur
    except Exception:
        return None


def marker_get(session_id, path):
    try:
        mp = _marker_path(_session_dir(session_id), path)
        with open(mp, "r", encoding="utf-8") as fh:
            return json.load(fh) or {}
    except Exception:
        return None


def marker_list(session_id):
    """Every marker recorded for this session, as dicts. Empty on failure."""
    out = []
    try:
        sdir = _session_dir(session_id)
        for name in sorted(os.listdir(sdir)):
            if not name.endswith(".json"):
                continue
            try:
                with open(os.path.join(sdir, name), "r",
                          encoding="utf-8") as fh:
                    rec = json.load(fh)
                if isinstance(rec, dict) and rec.get("p"):
                    out.append(rec)
            except Exception:
                continue
    except Exception:
        return []
    return out


def outstanding(session_id):
    """Deliverables recorded this session that are STILL un-linted right now.

    Re-derived from disk on every call rather than trusted from the marker: the
    file may have been linted, edited, deleted, or marked internal since it was
    recorded, and only the live file plus the receipt ledger can say."""
    out = []
    for rec in marker_list(session_id):
        if not int(rec.get("owed") or 0):
            continue
        path = rec.get("p") or ""
        if not os.path.isfile(path):
            continue
        ok, _reason = classify(path)
        if not ok:
            continue                                 # marked internal, or moved
        dg = digest_of(path)
        if receipt_status(path, dg) == "clean":
            continue
        rec = dict(rec)
        rec["h"] = dg or ""
        out.append(rec)
    return out


# ---------------------------------------------------------------------------
# MESSAGES
# ---------------------------------------------------------------------------
_FIX = ("Run `python3 cscpt/dlint.py %s` (FULL mode) and loop until "
        "\U0001f534 RED = 0.")
_SKIP_HINT = ("If this text is NOT your prose (a transcript, a quoted document, "
              "captured third-party material), do NOT rewrite it —— add a line "
              "`<!-- dlint: skip -->` to that file instead; it is permanent and "
              "the file is never flagged again.")
_REMIND = ("[dlint] Quick-linted `%s`%s. Does this file —— or a PART of it —— "
           "warrant FULL `dlint.py` instead? `--quick` checks only the "
           "register-independent rules, so where internal notes and "
           "deliverable-bound prose sit in one file, EXTRACT the deliverable "
           "part and run FULL mode on the extract.")
_REMIND_DELIV = (" —— and it looks like a DELIVERABLE (prose outside comms and "
                 "protocol territory), so root CLAUDE.md §3.7.3 requires FULL "
                 "mode before it reaches anyone")


def _emit_context(text):
    try:
        sys.stdout.write(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": text,
            }
        }))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# QUICK LINT
# ---------------------------------------------------------------------------
def _written_text(tool_name, tool_input):
    """The text THIS write produced, or None when the shape is unrecognised ——
    in which case the caller falls back to linting the whole file, the stricter
    direction. See CARVE-OUT 2 in the docstring for why this exists."""
    try:
        if tool_name == "Write":
            c = tool_input.get("content")
            return c if isinstance(c, str) else None
        if tool_name == "Edit":
            c = tool_input.get("new_string")
            return c if isinstance(c, str) else None
        if tool_name == "MultiEdit":
            edits = tool_input.get("edits")
            if not isinstance(edits, list):
                return None
            parts = [e.get("new_string") for e in edits
                     if isinstance(e, dict) and isinstance(e.get("new_string"),
                                                           str)]
            return "\n".join(parts) if parts else None
    except Exception:
        return None
    return None


def _run_dlint(args):
    """`dlint.py --quick <args>`; None on any failure so the caller exits 0."""
    if not os.path.isfile(_DLINT):
        return None
    try:
        return subprocess.run(
            [sys.executable, _DLINT, "--quick"] + list(args),
            capture_output=True, text=True, timeout=_DLINT_TIMEOUT_S)
    except Exception:
        return None


def _quick_verdict(path, is_comms, tool_name, tool_input):
    """(blocked, report, mode). `blocked` is True only when dlint exits 1."""
    if not is_comms:
        new = _written_text(tool_name, tool_input)
        if new is not None and len(new) <= _MAX_ARG_TEXT:
            if not new.strip():
                return False, "", "empty"
            r = _run_dlint(["--text", new])
            return (bool(r and r.returncode == 1),
                    (r.stdout if r else ""), "written")
    r = _run_dlint([path])
    return bool(r and r.returncode == 1), (r.stdout if r else ""), "file"


def _read_note(report, mode, base):
    """The `read`/`#r` advisory line lifted out of a dlint report, or '' if it
    did not fire.

    WHY THIS EXISTS AT ALL. `--quick`'s full report reaches CC on ONE path only
    —— the exit-2 stderr write that a RED triggers. On a clean run the report
    was simply discarded, so a YELLOW could be raised by the linter and seen by
    nobody: the advisory "fired" in every sense except the one that matters.
    That is a false negative manufactured by the plumbing, and the owner ranks a
    false negative ("could be highly misleading") far above the ~10 tokens a
    false positive costs. So the one YELLOW that asks CC to make a judgement is
    forwarded on every run, blocking or not.

    ONLY THIS YELLOW. The others (`-ize`, hyphen/#numbered, demoted Hart hits)
    are stylistic and already carried by root §3.5.5's own `--quick` run over
    every `response_`; forwarding all of them would put a report on every write
    in the repo. This one is different in kind —— it is the only quick rule
    whose verdict a machine cannot reach."""
    for line in (report or "").splitlines():
        if 'unmarked "read"' not in line:
            continue
        body = line.strip()
        body = body.split(": ", 1)[1] if body.startswith("L") and ": " in body \
            else body
        where = ("in the text this write introduced into `%s`" % base
                 if mode == "written" else "in `%s`" % base)
        return "[dlint] " + body + " (%s)" % where
    return ""


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
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
    '  printf \'%s\' \'{"hook_event_name":"PostToolUse",'
    '"tool_name":"Write",'
    '"tool_input":{"file_path":"/abs/file.md"}}\' \\\n'
    '    | python3 cscpt/dlint_quick.py\n'
    '  To lint prose by hand you almost certainly want the FULL linter:\n'
    '    python3 cscpt/dlint.py --quick /abs/file.md\n'
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


def main():
    _require_hook_payload(sys.argv[1:])
    try:
        data = json.load(sys.stdin)
    except Exception:
        log("no_stdin")
        return 0
    if not isinstance(data, dict):
        log("bad_payload")
        return 0
    if not _in_scope(data):
        log("out_of_scope")
        return 0

    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        log("no_input")
        return 0
    fp = tool_input.get("file_path")
    if not (isinstance(fp, str) and fp):
        log("no_path")
        return 0

    fp = _abs_target(fp, data.get("cwd"))
    base = os.path.basename(fp)
    low = base.lower()

    if os.path.splitext(low)[1] not in _LINT_EXTS:
        log("skip:ext", base)
        return 0
    if _repo_rel(fp) is None:
        log("skip:outside_repo", base)          # a lint that BLOCKS must not roam
        return 0
    if not os.path.isfile(fp):
        log("skip:missing", base)
        return 0
    if _QUERY_RE.match(base):
        log("skip:query", base)                 # CARVE-OUT 1 —— the user's words
        return 0

    tool_name = data.get("tool_name") if isinstance(data.get("tool_name"),
                                                    str) else ""
    is_comms = any(k in base for k in _COMMS_SUBSTRINGS)
    text = _read_text(fp)

    # --- CARVE-OUT 3 —— permanent per-file dismissal, non-comms only ---------
    if not is_comms and text is not None and _OPT_OUT_RE.search(text):
        log("skip:marked", base)
        return 0

    sid = data.get("session_id")
    sid = sid if isinstance(sid, str) and sid.strip() else ""

    # --- RECORD —— is this file a deliverable owing a FULL lint? -------------
    # BEFORE the quick lint, deliberately. A deliverable that fails quick RED
    # would otherwise never be recorded, and if the agent walked away from the
    # block instead of rewriting, the file would sit on disk un-linted with
    # nothing left to catch it at delivery.
    is_deliverable, reason = classify(fp, text)
    if sid and is_deliverable:
        marker_put(sid, fp, digest_of(fp, text), owed=1)

    # --- QUICK LINT ---------------------------------------------------------
    # THE `read`/`#r` ADVISORY IS NEVER SUPPRESSED, in either of the two ways it
    # once was. It used to be shown at most once per (session, file), on the
    # theory that told-once-is-told; and even that reached CC only when a RED
    # happened to co-occur, because a clean run threw the report away. Both are
    # false negatives: the second one hid the advisory on the majority of writes
    # (a `response_` with no RED in it), and the first hid a NEW instance
    # introduced by a later write to the same file. `_read_note` therefore
    # forwards it on every run, blocking or not.
    blocked, report, mode = _quick_verdict(fp, is_comms, tool_name, tool_input)
    rt_note = _read_note(report, mode, base)
    if blocked:
        where = ("this comms file" if is_comms else
                 "the text this write introduced into `%s`" % base)
        tail = "" if is_comms else " " + _SKIP_HINT
        sys.stderr.write(
            "dlint --quick found RED flag(s) in %s —— fix them (British "
            "spelling / Hart's quotation / #numbered), they then clear:\n%s%s\n"
            % (where, report, tail))
        log("red:%s" % mode, base)
        return 2                       # the report already carried `rt_note`

    # --- GATE —— a delivery is being written; is anything still owed? --------
    if sid and _DELIVERY_RE.match(base):
        owed = outstanding(sid)
        if owed:
            first = owed[0]
            spent = int(first.get("blocked") or 0)
            body = ("[dlint gate] A comms file is being written whilst %d "
                    "deliverable-shaped file(s) have never passed FULL "
                    "`dlint.py`: %s. Root CLAUDE.md §3.7.3 requires it BEFORE "
                    "the file reaches anyone. %s %s"
                    % (len(owed), ", ".join(_q(r["p"]) for r in owed[:5]),
                       _FIX % _q(first["p"]), _SKIP_HINT))
            for r in owed:
                marker_put(sid, r["p"], r.get("h"), owed=1,
                           blocked=int(r.get("blocked") or 0) + 1)
            if spent == 0:
                # The read advisory rides along rather than being lost to the
                # early return —— a gate block is still a write CC just made.
                sys.stderr.write(body + (" " + rt_note if rt_note else "")
                                 + "\n")
                log("gate:block", os.path.basename(first["p"]))
                return 2
            # Already blocked once this session for this file —— degrade to an
            # advisory so a legitimate post-lint edit cannot wedge the turn.
            _emit_context(body + (" " + rt_note if rt_note else ""))
            log("gate:spent", os.path.basename(first["p"]))
            return 0
        log("gate:clear", base)

    # --- CONTEXT —— the read advisory EVERY time, the FULL-mode reminder once
    # per (session, file). ONE `_emit_context` call for both: stdout carries a
    # single JSON object, so a second call would emit a second one and the
    # harness would parse neither.
    notes = [rt_note] if rt_note else []
    remind = True
    if sid:
        prev = marker_get(sid, fp)
        if prev and int(prev.get("reminded") or 0):
            remind = False
        elif marker_put(sid, fp, digest_of(fp, text), reminded=1) is None:
            remind = False
    if remind:
        notes.append(_REMIND % (base, _REMIND_DELIV if is_deliverable else ""))
    if notes:
        _emit_context(" ".join(notes))
    log("clean:%s%s" % ("remind" if remind else "reminded",
                        "+rt" if rt_note else ""), "%s %s" % (reason, base))
    return 0


if __name__ == "__main__":
    sys.exit(main())
