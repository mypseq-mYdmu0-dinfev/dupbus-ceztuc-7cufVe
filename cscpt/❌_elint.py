#!/usr/bin/env python3
"""ESCAPE lint —— stops a DELIVERABLE escaping to the user un-linted.

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: enforces root CLAUDE.md §3.7.3 (a deliverable must pass FULL
  `dlint.py` first) for files no other lint covers.
* IF IT ADVISES: you wrote a deliverable-shaped file. Run
  `python3 cscpt/dlint.py <path>`, loop until 🔴 RED = 0.
* IF IT BLOCKS (exit 2, on a `response_`/`close_`/`wrap_` write): a
  deliverable is still un-linted. Same fix, then rewrite.
* WRONGLY FLAGGED? Put `<!-- dlint: internal -->` in that file —— one line,
  permanent, never flagged again. NEVER rewrite an internal file to satisfy
  this lint.
* MISSED a deliverable? `<!-- dlint: deliverable -->` forces it in.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===

THE GAP THIS CLOSES. `dlint_quick.py` fires only on a basename containing
`response_`/`close_`/`wrap_`. A genuine prose deliverable written anywhere
else —— an interview cheat sheet, a one-pager, a speech —— was therefore
covered by NOTHING mechanical, and root §3.7.3 rested entirely on the agent
remembering it mid-turn. It was not remembered: a real cheat sheet was
drafted, debated twice, and sent, and a retroactive FULL lint then found 18
🔴 RED and 20⁺ 🟡 YELLOW. That is a NOT-NOTICED failure (`cp/ccsim/CLAUDE.md`
§8.7), so more prose could not repair it —— hence this file.

WIRING (kept here, not in NON-CCSIM: nobody invokes this by hand). ONE script,
TWO registrations, selected by argv:
  * `post` —— PostToolUse (Edit|Write|MultiEdit), fronted by `elint_hook.sh`.
  * `stop` —— Stop, registered directly (fires once per turn, so a bash shim
    would save nothing —— same reason clint and hlint have none).
`hook_event_name` is used as a fallback only; an unrecognisable mode exits 0.

THE THREE TIERS, AND WHY THE MIDDLE ONE IS THE REAL GATE.
  * TIER A —— PostToolUse on the DELIVERABLE's own write. Emits
    `hookSpecificOutput.additionalContext` at exit 0: the one PostToolUse
    channel that is BOTH model-visible and non-blocking. Once per (session,
    file), so redrafting a long deliverable is never nagged.
  * TIER B —— PostToolUse on a `response_`/`close_`/`wrap_`/`artefact_` write
    whilst a deliverable is still un-receipted. Exit 2, so the model sees it.
    THIS is the choke point: a deliverable is written and rewritten many
    times but delivered once, and in this repo delivery IS the comms file
    that names it. It lands BEFORE root §3.1.6's turn-end actions, so the fix
    costs no extra turn and disturbs no declaration batch.
  * TIER C —— Stop. Exit 0 always: a user-visible line plus a log entry.

WHY TIER C MUST NOT BLOCK, THOUGH IT COULD. A Stop hook's only model-visible
channel is a non-zero exit, which BLOCKS the stop and buys one more model
turn. That turn would land AFTER root §3.1.6's TEAs —— commit, chapter
marker, then the I/O declaration batch that §3.1.7.5 says nothing may follow.
Blocking there would force the agent to violate one protocol to satisfy
another, which is exactly the cascade that got clint's own Stop block
demoted: every block forced an extra turn, and with nothing new to declare
the agent re-emitted its declaration batch —— the very breach it was
enforcing. Tier C is therefore an AUDIT NET, and it is honest about it:
`.elint.log` records EVERY invocation, so "never fired" is distinguishable
from "fired and found nothing" (hook_guide §7.7), and the exit-0 line reaches
the USER —— who is the deliverable's recipient and can simply ask for the
lint. Enforcement proper lives in Tier B.

THE RECEIPT LEDGER —— WHY CONTENT-ADDRESSED, NOT TURN-SCOPED. `dlint.py`
appends one line to `cscpt/.dlint_receipts.jsonl` on every FULL-mode FILE
lint: the target's realpath, the SHA-256 of the text as it stands on disk
AFTER the quote auto-fix, and the RED count. `--quick` and `--text` write
nothing, so a receipt's existence already proves FULL mode ran.

Keying on CONTENT rather than on "was dlint run this turn" is load-bearing in
three ways. A deliverable drafted on Monday and sent on Friday stays covered.
A file linted clean and then EDITED loses its receipt automatically, because
the hash moved —— which is correct, since the edit is un-linted text. And a
lint that ended with RED > 0 records `r > 0`, so a FAILED lint can never be
mistaken for a passed one. Single writer by construction: `dlint.py` alone
appends and alone prunes; this file only ever reads it.

THE PENDING LEDGER —— A DIRECTORY, NOT A FILE. One small JSON marker per
(session, deliverable) under `cscpt/.elint_state/s_<hash>/`. A directory of
independent markers has no read-modify-write race across the parallel writes
one turn issues, whereas a single shared JSON would (coding.md § Concurrency:
one writer per shared mutable file). Losing this state costs a missed
reminder —— the harmless direction. Losing the RECEIPT ledger would instead
cost a false alarm, which is why the receipts live in a durable git-ignored
file rather than the self-cleaning OS temp dir.

WHAT A DELIVERABLE IS, MECHANICALLY. `universal/glossary.md` defines it as
anything to be sent or potentially exposed to a third party, which no file
attribute can decide. So the classifier answers a narrower, decidable
question —— IS THIS FILE PLAUSIBLY PROSE FOR SOMEONE OTHER THAN CC? —— as
four gates, ALL of which must pass:
  1. Extension `.md` or `.txt`.
  2. Inside this repo. Outside it there is no territory map to apply, and a
     lint that can BLOCK must not roam (hook_guide §4.7).
  3. Not in PROTOCOL TERRITORY, and not a protocol-shaped NAME.
  4. Enough substance to be prose at all (`_MIN_SUBSTANCE` non-space chars),
     which drops stubs, placeholders, and index fragments for free.

WHY TERRITORY IS A DENY-LIST, NOT AN ALLOW-LIST. An allow-list of
deliverable-shaped paths (`temp/*/output/`) or names (`CHEATSHEET_*`) is
precise where it matches and blind everywhere else, so the same miss returns
under a different filename —— and the real case ALSO produced `SPEECH_*`,
`mini_SPEECH_*`, and `<Client>_<Doc>_<Name>.md`, none of which any plausible
allow-list would have held. Naming the INTERNAL trees inverts that: they are
finite, stable, repo-owned, and everything else is flagged BY DEFAULT, so a
new `deliverables/` or `client_x/` folder is covered the day it appears.

THE HONEST LIMIT OF THAT, STATED RATHER THAN HIDDEN. No folder in this repo
separates the two cleanly. Root §3.4.2.1 sends non-comms output to the COMMS
folder, so `sessions/` holds both; `cp/` holds protocol files AND a CV. The
territory rule is therefore a good default, not a proof, and the design's
real answer is that BOTH errors are correctable ONCE, permanently, in one
line, at the moment of the misfire:
  * `<!-- dlint: internal -->`    —— never a deliverable. Beats the default.
  * `<!-- dlint: deliverable -->` —— always one. Beats the default.
This is the single structural difference from `plint.py`'s `CP_notes.md`
misfire: plint had no way to record that a hit was wrong, so it fired
forever and was tuned out. Here a false positive costs one line ONCE and the
flagged set shrinks monotonically as it is met. A marker is plain text in the
repo, so `grep -rn 'dlint: internal'` audits every dismissal ever made ——
and a marker on a genuine deliverable is a deliberate, reviewable act rather
than a silent omission, which is the whole point of moving the failure from
forgetting to lying.

WHY THE FAIL DIRECTION LEANS TOWARDS FLAGGING. A false positive costs one
line, once, and the file is then permanently quiet. A false negative is an
un-linted deliverable in a third party's hands. Those are not comparable, so
`cp/` and the role-named comms files are the ONLY places the default is
allowed to suppress, and each is justified below.

TERRITORY, WITH THE REASON FOR EACH (see `_PROTOCOL_DIRS`):
  * `universal/`, `cscpt/`, `nscpt/`, `gscpt/`, `.claude/`, `.git/` —— pcmd
    and tooling; nothing here is ever sent anywhere.
  * `backup/` —— mirrors written by `mirror.sh`, not authored output.
  * `cp/` —— Claude Project PROTOCOL territory (root §6, §8.4). ACCEPTED
    FALSE NEGATIVE, named honestly: `cp/career/culous_yu_resume_*.md` and
    `cp/dissertation/MGTK751_A*.md` ARE deliverables and are NOT flagged.
    They need `<!-- dlint: deliverable -->` once. Excluding the tree is the
    lesser evil because every OTHER `.md` there —— CLAUDE.md, CP_index,
    _bg, _guide, backlog, and a dozen pcmd —— would otherwise nag forever.
  * `temp/temp_archive/` —— "never touch" per `temp/README.md`.
  * any `input/`, `resource/` or `build/` segment —— `temp/README.md` defines
    those as provided material, retrieved/generated material, and scratch
    respectively; only `output/` is the deliverable slot. Written as a
    deny-list of the other three rather than an allow-list of `output/`, so a
    folder ignoring the convention is still covered.
  * `sessions/queued_queries/` —— query drafts, i.e. comms.
`sessions/` itself is deliberately IN scope apart from role-named files,
because root §3.4.2.1 makes it the DEFAULT home for a separate-file
deliverable. Excluding it wholesale would have re-opened the exact gap.

NAME EXCLUSIONS: two rules, argued in full beside the constants —— the comms
roles of root §3.3 anchored after at most ONE CP prefix, plus machinery files
identified by a 12-digit timestamp SUFFIX together with a role word at any
depth. The timestamp is what keeps `Client_Project_Response_Plan.md`, a
perfectly ordinary deliverable name, from being swallowed by the second rule.
Those role lists are a CONVENIENCE, not the mechanism —— they only spare the
common cases from needing a marker, and a role missing from them costs exactly
one marker line. Also excluded: `❌_` (voided, §8.2), `temp_` (§8.3.2),
`user_notes` (§8.3.1), `_otg` (§8.3.3), `_DevPlan`, and the fixed protocol
basenames in `_EXCLUDED_BASENAMES`.

SCOPE GUARD: repo-scoped, because this lint can BLOCK (hook_guide §4.7).
Signals are the payload `cwd`, else the `~/.claude/projects/<slug>/`
transcript slug, both derived from this file's OWN location. FAILS OPEN on
an unscopeable payload —— that is a shape that cannot be read, not evidence
of another project, and a silently disabled lint is the failure the whole
hook guide exists to prevent.

FAIL-SAFE THROUGHOUT: any malformed payload, unreadable file, missing
`dlint.py`, or unwritable state exits 0 with no output. The only non-zero
exit in the file is Tier B's deliberate one.

TIER B's LOOP GUARD: it blocks at most ONCE per (session, deliverable), then
degrades to a Tier-A-style advisory. Without that, a legitimate post-lint
edit (a typo fix moves the hash, so the receipt correctly lapses) could
block every subsequent comms write in the turn.

KNOWN GAPS, so nobody reads more assurance into this than it earns:
  * A deliverable written AFTER the turn's comms file is only advised
    (Tier A) and warned about (Tier C); Tier B has nothing left to gate.
  * A turn that writes a deliverable and NO comms file at all never reaches
    Tier B, so it ends with a user-visible warning and nothing more.
  * `.html`, `.pages`, `.docx`, and `.key` deliverables are out of scope:
    `dlint.py` reads plain prose and would flag markup as breaches.
  * Files written outside this repo are never classified (gate 2).
  * Everything here depends on Tier A having recorded the write, so a
    deliverable authored before this lint existed is invisible to Tiers B
    and C until it is next edited.
"""

import sys
import os
import re
import json
import time
import shutil
import hashlib

# ---------------------------------------------------------------------------
# ANCHORS. Every path is derived from this file's OWN location, never from the
# process cwd —— a user-level hook routinely runs with the cwd of a different
# project entirely (hook_guide §4.5.2).
# ---------------------------------------------------------------------------
_CSCPT = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT_REAL = os.path.realpath(os.path.dirname(_CSCPT))
_REPO_SLUG = re.sub(r"[/ ]", "-", _REPO_ROOT_REAL.rstrip("/"))

# Written by `dlint.py` (sole writer), read here. Shared constant duplicated
# in dlint.py by necessity —— the two scripts are separate processes and
# neither imports the other; both derive it from their own `__file__`, so a
# repo move keeps them pointing at the same file.
_RECEIPTS = os.path.join(_CSCPT, ".dlint_receipts.jsonl")
_STATE_ROOT = os.path.join(_CSCPT, ".elint_state")
_LOG = os.path.join(_CSCPT, ".elint.log")

_PROSE_EXTS = {".md", ".txt"}

# NAME-BASED INTERNAL DETECTION, in two independent rules. Both are needed,
# and a single looser regex was tried first and REJECTED —— see below.
#
# RULE 1, the comms roles of root §3.3, anchored at the start after at most
# ONE optional CP-folder prefix, which is exactly what §3.3.6 permits
# (`career_response_<TS>.md`). Precise, and true with or without a timestamp.
_COMMS_ROLES = ("query", "response", "close", "wrap", "slog", "artefact")
_COMMS_RE = re.compile(
    r"^(?:[A-Za-z0-9][A-Za-z0-9-]*_)?(?:" +
    "|".join(_COMMS_ROLES) + r")_", re.IGNORECASE)

# RULE 2, the machinery files this repo actually generates —— debate boards,
# digests, handoffs, revert logs. Their role word can sit at ANY depth
# (`dissertation_A1Rv2_debate_suggestions_<TS>.md`), so rule 1's anchor cannot
# reach them. The obvious repair —— letting rule 1 skip two prefix segments
# instead of one —— was tried and REJECTED, because it also swallows a
# perfectly ordinary deliverable name: `Client_Project_Response_Plan.md` would
# have matched, and a false NEGATIVE is the failure this whole lint exists to
# prevent. What actually separates the two is the 12-digit timestamp SUFFIX
# every session-keyed machinery file carries (root §2.2.1) and a hand-named
# deliverable generally does not. So rule 2 fires only when BOTH hold: the
# basename ends in `_<12 digits>` AND one of its underscore-delimited segments
# is a role word. `Client_Project_Response_Plan.md` has no timestamp and
# survives; `debate_board_<TS>.md` has both and is excluded.
# Kept DELIBERATELY narrow. `board` and `log` were considered and dropped:
# both are ordinary English that a real deliverable can carry
# (`Acme_Board_Briefing_<TS>.md`), and every machinery file they would have
# caught already carries `debate` or `revertlog` as another segment. A role
# word only earns a place here if it is effectively never part of a document's
# own title.
_MACHINERY_ROLES = frozenset(_COMMS_ROLES) | frozenset((
    "debate", "digest", "handoff", "revertlog",
))
_TS_SUFFIX_RE = re.compile(r"_\d{12}$")

# A comms file whose write means "this turn's output is being handed over".
# `query_` is excluded —— it carries the USER's words, not a delivery. ONE
# optional CP prefix only, per root §3.3.6; a looser prefix would make
# `hook_probe_response_.md` (the dlint live probe) read as a delivery.
_DELIVERY_RE = re.compile(
    r"^(?:[A-Za-z0-9][A-Za-z0-9-]*_)?"
    r"(?:response|close|wrap|artefact)_", re.IGNORECASE)

# First path segment (repo-relative) that puts a file in protocol/tooling
# territory. Rationale per entry is in the module docstring (TERRITORY).
_PROTOCOL_DIRS = {
    "universal", "cscpt", "nscpt", "gscpt", "backup", ".claude", ".git", "cp",
}

# Whole repo-relative prefixes excluded for a reason of their own.
_EXCLUDED_PREFIXES = (
    ("temp", "temp_archive"),
    ("sessions", "queued_queries"),
)

# Directory names that `temp/README.md` itself defines as NOT the deliverable
# slot: `input/` is provided material, `resource/` is retrieved or generated
# material (research, images), `build/` is scratch and script I/O. Only
# `output/` holds "official deliverables" —— but this is written as a deny-list
# of the other three rather than an allow-list of `output/`, so a folder that
# ignores the convention is still covered.
_NON_OUTPUT_SEGMENTS = {"input", "resource", "build"}

# Basenames that are protocol furniture wherever they sit.
_EXCLUDED_BASENAMES = {
    "claude.md", "readme.md", "cp_instr.md", "placeholder.md",
    "last_seen.md", "backlog.md",
}

# The two overrides. Matched anywhere in the file, in any comment syntax ——
# the payload is the token, not the wrapper, so `<!-- dlint: internal -->`,
# `# dlint: internal`, and a bare line all work.
_OPT_OUT_RE = re.compile(r"dlint:\s*(?:internal|skip)\b", re.IGNORECASE)
_OPT_IN_RE = re.compile(r"dlint:\s*deliverable\b", re.IGNORECASE)

# Non-whitespace characters below which a file is not prose worth linting.
# Kills stubs, placeholders and index fragments without naming any of them.
_MIN_SUBSTANCE = 200

# Backstops, none hit in normal use.
_MAX_READ_BYTES = 512 * 1024
_MAX_RECEIPT_LINES = 4000
_MAX_PENDING_PER_SESSION = 60
_STATE_TTL_S = 7 * 24 * 3600
_MAX_SWEEP = 200
_LOG_MAX_LINES = 800

_READ_TOOLS = {"Read", "NotebookRead"}


# ---------------------------------------------------------------------------
# REPO-SCOPE GUARD. Identical in shape to dlint_quick.py's and clint.py's ——
# deliberately duplicated rather than shared, because a hook that imports a
# sibling module dies silently if that module is ever moved, and these files
# must survive being run from any cwd in any project. FAILS OPEN.
# ---------------------------------------------------------------------------
def _in_scope(data):
    """True if this invocation belongs to THIS repo, or if scope genuinely
    cannot be determined. Never raises: an error here must default to
    "run the lint", like every other fail-safe path in this file."""
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
        return True  # neither field usable -> FAIL-OPEN
    except Exception:
        return True


# ---------------------------------------------------------------------------
# CLASSIFIER
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
    """Absolute path for a payload's `file_path`. A RELATIVE one is resolved
    against the PAYLOAD's `cwd`, never this process's own —— the harness may
    launch a hook from anywhere, so `os.path.abspath` alone would silently
    resolve against the wrong tree and every territory verdict would be
    nonsense (plint.py's `_target_dir` exists for the same reason)."""
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


def _name_is_internal(base):
    """True if the BASENAME alone marks this as protocol furniture, a comms
    or machinery file, or a file root CLAUDE.md says to disregard."""
    low = base.lower()
    if low in _EXCLUDED_BASENAMES:
        return True
    if base.startswith("❌_"):          # voided (root §8.2)
        return True
    if low.startswith("temp_"):             # to be deleted soon (§8.3.2)
        return True
    if "user_notes" in low:                 # private notes (§8.3.1)
        return True
    stem = os.path.splitext(low)[0]
    if stem.endswith("_otg"):               # OTG variant (§8.3.3)
        return True
    if low.endswith("_devplan.md"):
        return True
    if _COMMS_RE.match(base):                       # rule 1 (see constants)
        return True
    stem = os.path.splitext(base)[0]
    if _TS_SUFFIX_RE.search(stem):                  # rule 2 (see constants)
        parts = set(s.lower() for s in stem.split("_"))
        if parts & _MACHINERY_ROLES:
            return True
    return False


def _territory_is_internal(segs):
    """True if the repo-relative path sits in protocol/tooling territory."""
    if len(segs) <= 1:
        return True                          # a repo-ROOT file is furniture
    if segs[0] in _PROTOCOL_DIRS:
        return True
    for pref in _EXCLUDED_PREFIXES:
        if tuple(segs[:len(pref)]) == pref:
            return True
    if _NON_OUTPUT_SEGMENTS.intersection(segs[:-1]):
        return True
    return False


def classify(path):
    """(is_deliverable, reason). `reason` is for the log, never for the user.

    Gate order is cheapest-first, but the two content OVERRIDES are read
    before the territory verdict is returned, so a marker always wins over
    the default in BOTH directions (docstring: THE HONEST LIMIT)."""
    base = os.path.basename(path)
    if os.path.splitext(base)[1].lower() not in _PROSE_EXTS:
        return False, "ext"
    segs = _repo_rel(path)
    if segs is None:
        return False, "outside_repo"
    if not os.path.isfile(path):
        return False, "missing"
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


def digest_of(path):
    """SHA-256 of the file as it stands on disk, matching what `dlint.py`
    hashes into a receipt. None if unreadable."""
    text = _read_text(path)
    if text is None:
        return None
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


# ---------------------------------------------------------------------------
# RECEIPTS (read-only here; `dlint.py` is the sole writer)
# ---------------------------------------------------------------------------
def receipt_status(path, digest):
    """"clean" (FULL lint passed on exactly this content), "red" (FULL lint
    ran on this content and left RED flags), or None (never FULL-linted at
    this content). Unreadable ledger -> None, i.e. treat as un-linted, which
    is the flagging direction and matches the fail-towards-flagging rule."""
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
# PENDING LEDGER —— one marker file per (session, deliverable)
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


def pending_put(session_id, path, digest, advised=None, blocked=None):
    """Create or update this (session, file) marker. Returns the stored dict,
    or None if the state is unusable —— in which case the caller simply loses
    a later reminder, the harmless direction."""
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
        elif len(os.listdir(sdir)) >= _MAX_PENDING_PER_SESSION:
            return None
        cur["p"] = os.path.realpath(path)
        cur["h"] = digest or ""
        cur["t"] = int(time.time())
        if advised is not None:
            cur["advised"] = int(advised)
        if blocked is not None:
            cur["blocked"] = int(blocked)
        cur.setdefault("advised", 0)
        cur.setdefault("blocked", 0)
        tmp = mp + ".tmp%d" % os.getpid()
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(cur, fh)
        os.replace(tmp, mp)
        return cur
    except Exception:
        return None


def pending_get(session_id, path):
    try:
        mp = _marker_path(_session_dir(session_id), path)
        with open(mp, "r", encoding="utf-8") as fh:
            return json.load(fh) or {}
    except Exception:
        return None


def pending_list(session_id):
    """Every marker recorded for this session, as dicts. Empty on any
    failure."""
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


def _is_scratch(path):
    """True for CC's own scratch folder, which can never reach a third party.

    `cp/ccsim/sandbox/` is defined by `cp/ccsim/CLAUDE.md` §5 as the ONLY
    folder CC may delete from directly —— fixtures, probes and experiments,
    none of which is ever delivered. Such a file may still be a legitimate
    TIER A subject (this repo's own liveness probe carries an opt-in marker
    precisely so the advisory fires on it), but it must NEVER become an
    outstanding obligation: nothing there goes out, so nothing there can
    escape un-linted. Without this, the probe's own opt-in marker makes it
    permanently owed, so TIER B blocks the first comms write of EVERY future
    session, and the only way to clear it is to lint the probe —— which
    writes a clean receipt and silences the probe for good. A gate whose
    fixture disarms the gate is worse than no fixture."""
    segs = _repo_rel(path)
    return bool(segs) and tuple(segs[:3]) == ("cp", "ccsim", "sandbox")


def outstanding(session_id):
    """Pending deliverables that are STILL un-linted right now.

    Re-derived from disk on every call rather than trusted from the marker:
    the file may have been linted, edited, deleted, or marked internal since
    it was recorded, and only the live file and the receipt ledger can say."""
    out = []
    for rec in pending_list(session_id):
        path = rec.get("p") or ""
        if not os.path.isfile(path):
            continue
        if _is_scratch(path):
            continue                       # scratch never leaves; see _is_scratch
        ok, _reason = classify(path)
        if not ok:
            continue                       # marked internal, or moved
        dg = digest_of(path)
        st = receipt_status(path, dg)
        if st == "clean":
            continue
        rec = dict(rec)
        rec["h"] = dg or ""
        rec["status"] = st or "none"
        out.append(rec)
    return out


# ---------------------------------------------------------------------------
# LOG —— every invocation, so "never fired" and "fired, found nothing" can be
# told apart (hook_guide §7.7). Self-pruning; never raises.
# ---------------------------------------------------------------------------
def log(action, detail=""):
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
# MESSAGES
# ---------------------------------------------------------------------------
_FIX = ("Run `python3 cscpt/dlint.py %s` (FULL mode) and loop until "
        "\U0001f534 RED = 0.")
_ESCAPE = ("If it is NOT a deliverable, do NOT rewrite it —— add a line "
           "`<!-- dlint: internal -->` to it instead; that is permanent and "
           "it will never be flagged again.")


def _advice(path):
    return ("[elint] `%s` looks like a DELIVERABLE (prose outside comms and "
            "protocol territory). Root CLAUDE.md §3.7.3: it MUST pass FULL "
            "`dlint.py` before it reaches the user. %s %s"
            % (os.path.basename(path), _FIX % _q(path), _ESCAPE))


def _q(path):
    """Repo-relative where possible, shell-quoted when it holds a space ——
    the reader pastes this straight into a terminal."""
    try:
        segs = _repo_rel(path)
        rel = "/".join(segs) if segs else path
    except Exception:
        rel = path
    return "'%s'" % rel if " " in rel else rel


def _emit_context(event, text):
    try:
        sys.stdout.write(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": event,
                "additionalContext": text,
            }
        }))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# TIERS
# ---------------------------------------------------------------------------
def run_post(data):
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        log("post:no_input")
        return 0
    if isinstance(data.get("tool_name"), str) and data["tool_name"] in _READ_TOOLS:
        log("post:read_tool")
        return 0
    fp = tool_input.get("file_path")
    if not (isinstance(fp, str) and fp):
        log("post:no_path")
        return 0
    sid = data.get("session_id")
    if not (isinstance(sid, str) and sid.strip()):
        log("post:no_session", fp)
        return 0

    fp = _abs_target(fp, data.get("cwd"))
    base = os.path.basename(fp)

    # --- TIER B —— a comms file is being written; is anything still owed? ---
    if _DELIVERY_RE.match(base):
        owed = outstanding(sid)
        if not owed:
            log("post:delivery_clear", base)
            return 0
        first = owed[0]
        blocked_before = int(first.get("blocked") or 0)
        names = ", ".join(_q(r["p"]) for r in owed[:5])
        body = ("[elint] A comms file is being written whilst %d "
                "deliverable-shaped file(s) have never passed FULL `dlint.py`"
                ": %s. Root CLAUDE.md §3.7.3 requires it BEFORE the file "
                "reaches the user. %s %s"
                % (len(owed), names, _FIX % _q(first["p"]), _ESCAPE))
        for r in owed:
            pending_put(sid, r["p"], r.get("h"),
                        blocked=int(r.get("blocked") or 0) + 1)
        if blocked_before == 0:
            sys.stderr.write(body + "\n")
            log("post:block", names)
            return 2
        # Already blocked once this session for this file —— degrade to an
        # advisory so a legitimate post-lint edit cannot wedge the turn.
        _emit_context("PostToolUse", body)
        log("post:block_spent", names)
        return 0

    # --- TIER A —— the deliverable's own write ------------------------------
    ok, reason = classify(fp)
    if not ok:
        log("post:skip", "%s %s" % (reason, base))
        return 0
    dg = digest_of(fp)
    if receipt_status(fp, dg) == "clean":
        pending_put(sid, fp, dg)
        log("post:receipted", base)
        return 0
    prev = pending_get(sid, fp)
    already = bool(prev and int(prev.get("advised") or 0))
    pending_put(sid, fp, dg, advised=1)
    if already:
        log("post:advise_spent", base)
        return 0
    _emit_context("PostToolUse", _advice(fp))
    log("post:advise", base)
    return 0


def run_stop(data):
    sid = data.get("session_id")
    if not (isinstance(sid, str) and sid.strip()):
        log("stop:no_session")
        return 0
    owed = outstanding(sid)
    if not owed:
        log("stop:clean")
        return 0
    names = ", ".join(os.path.basename(r["p"]) for r in owed[:5])
    log("stop:warn", names)
    try:
        sys.stdout.write(json.dumps({"systemMessage": (
            "elint: %d file(s) written this session look like deliverables "
            "and have never passed a FULL dlint run: %s. Root CLAUDE.md "
            "section 3.7.3 requires it before a deliverable reaches you."
            % (len(owed), names))}))
    except Exception:
        pass
    return 0


def main(argv):
    mode = argv[1].lower() if len(argv) > 1 else ""
    try:
        data = json.load(sys.stdin)
    except Exception:
        log("no_stdin", mode)
        return 0
    if not isinstance(data, dict):
        log("bad_payload", mode)
        return 0
    if mode not in ("post", "stop"):
        ev = data.get("hook_event_name")
        mode = {"PostToolUse": "post", "Stop": "stop"}.get(ev, "")
        if not mode:
            log("bad_mode", str(ev))
            return 0
    if not _in_scope(data):
        log("out_of_scope", mode)
        return 0
    try:
        return run_post(data) if mode == "post" else run_stop(data)
    except Exception as exc:                                    # noqa: BLE001
        log("error", "%s %s" % (mode, exc))
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
