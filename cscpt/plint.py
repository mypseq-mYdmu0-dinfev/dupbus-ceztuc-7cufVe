#!/usr/bin/env python3
"""Protocol-Read Linter (PreToolUse hook)

BEFORE a file is written (or read), it looks at what is about to happen and
injects a NON-BLOCKING reminder to read the governing file FIRST.

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: a PreToolUse hook that reminds you to read a governing file FIRST,
  before a write or read.
* THREE RULES: script/pcmd write -> `universal/coding.md`; greeting/sign-off
  content -> `universal/writing.md` (incl. `## Stylisation`); reading a file
  under a README-bearing folder OR ancestor (up to the repo root) -> that
  README, once per README per session.
* IF IT FIRES: read the named file, or ignore it if already read —— ADVISORY,
  never gates a call.
* KNOWN LIMITS: the deliverable rule is a heuristic (`hello` in a script trips
  it); a comms-named pcmd is skipped; project-root/vendor READMEs are
  excluded.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WIRING (kept here, not in NON-CCSIM: a caller never invokes this file, so the
plumbing is dead weight to everyone but an editor). Registered as a `PreToolUse`
hook (Edit|Write|MultiEdit|Read) in the USER-level `~/.claude/settings.json` ——
the Claude Desktop app executes user-level hooks and silently ignores
project-level ones. IN: PreToolUse JSON on stdin (`tool_input`, plus
`tool_name`, `session_id` and `cwd` for the README rule). OUT: on a match, JSON
on stdout carrying `hookSpecificOutput.additionalContext`, one line per rule.
EXIT is ALWAYS 0 and no `permissionDecision` of `deny`/`ask` is ever emitted ——
that is the mechanism behind "can NEVER gate a write". FAIL-SAFE: any error,
missing field or unreadable payload -> exit 0, no output. Each rule is gated on
its target file EXISTING (missing -> that rule stays silent) and names it by
ABSOLUTE path, so it is openable from any project.

WHY THE MATCHER CARRIES `Read` AND WHY THE RULES SPLIT ON `tool_name`: the
README rule can only fire on a READ, so `Read` had to join the matcher —— but
the matcher is tool-name-only (there is no path filter), so the CODE and
DELIVERABLE rules would then start firing on every read too. The CODE rule keys
purely off `file_path`, so a bare `Read` of any `.py` or pcmd would have
reminded the reader to "read coding.md FIRST" before merely LOOKING at a file
—— firing on session-start reads of `CLAUDE.md` and every `universal/*.md`,
i.e. constantly, on calls where nothing is being authored. Those two rules are
therefore skipped when `tool_name` is a read tool, and the README rule requires
one. The gate is written as "skip write rules only when tool_name is EXPLICITLY
a read tool": a payload missing `tool_name` keeps the pre-existing behaviour
rather than silently losing two rules.

EXACT MATCH SETS (kept here rather than in NON-CCSIM: when the hook fires it
NAMES the file to read, so a caller never has to reconstruct which rule caught
them). CODE (mechanical, certain) —— extension `.py`/`.sh`, or a `.md` that
lives under `universal/`, is a `CLAUDE.md`, or sits under `cp/<project>/`; the
comms exclusion covers `query_`/`response_`/`close_`/`wrap_`/`slog_`/`artefact_`.
DELIVERABLE (heuristic, uncertain) —— the written CONTENT carries a
greeting/sign-off marker: `hello`, `dear`, `greetings`, `regards`, `sincerely`,
`best wishes`, `yours sincerely`, `yours faithfully`, ... —— the live list is
`_MARKERS` below, which is the spec; this is a map of it. README (mechanical,
certain) —— walk from the READ target's own directory up through EVERY
ancestor to the repo root (docstring: ANCESTOR WALK below); for each ancestor
that carries a `README.md` and is not excluded as noise, remind ONCE for that
specific README (never repeated this session) unless the target IS that
README, in which case reading it silently claims it instead.

WHY IT EXISTS (self-contained —— no conversation or comms file explains or
overrides anything here): these protocol reads get SILENTLY SKIPPED, and the cost
is asymmetric and back-loaded. A script written without coding.md misses the
issue-reporting format, bakes in a comms-file citation that rots, or ships a fix
with no regression test; a deliverable written without writing.md goes to a third
party in the wrong register —— both cheap to prevent at write time, expensive to
discover later.

WHY THE README RULE EXISTS: a folder's `README.md` carries the conventions and
procedures for the files INSIDE it —— rename/move steps, ordering, what must be
recorded —— and none of that is visible in the file actually opened. The
governing instruction ("on accessing any folder, read its README FIRST") was
already written down, in prose, and was still skipped: a file inside a
README-bearing folder was read and acted on, and the documented procedure was
missed. That is a NOT-NOTICED failure, not a misunderstood one, and prose that
was already skipped cannot repair it —— re-bolding or repeating the words
changes nothing. The enforcement has to arrive at the MOMENT OF THE ACT, which
is what this rule does: the reminder lands on the read itself, naming the exact
README by absolute path so following it costs one open.

ANCESTOR WALK (root CLAUDE.md §8.5.1 —— extended from the immediate folder to
EVERY ancestor up to the repo root): the original, immediate-folder-only rule
was itself skipped on exactly this account —— a file was read several levels
under a folder whose OWN `README.md` governs the whole tree (e.g. a generic
`temp/` folder's README, several levels above the specific dated sub-folder a
session actually touched), and because the rule only ever looked at the
target's own directory, that governing README was never named. `_ancestor_dirs`
climbs from the target's directory through successive parents, stopping AFTER
the first one that is itself a project root (contains `.git`) —— walking
further would leave the project and start surfacing READMEs that govern
something else entirely. `_MAX_ANCESTORS` backstops a chain with no `.git`
anywhere (so the climb cannot run unbounded to `/`), and
`_MAX_README_LINES_PER_CALL` separately bounds how many reminder LINES one
read may ever emit, independent of how many ancestors were examined —— a
deeply-nested, README-at-every-level tree is legal but should not dump a dozen
lines into one turn.

WHY ONCE PER README PER SESSION (the load-bearing constraint, not an
optimisation; extended from once-per-DIRECTORY to once-per-README when the
rule started walking ancestors —— see ANCESTOR WALK): reads are the single
most frequent tool call, and a reminder on every read under a README-bearing
folder would fire many times per turn. It would be tuned out within one
session and would take the other two rules' credibility with it —— the same
failure the DELIVERABLE rule's word boundaries exist to prevent. One reminder
per README is also all the rule can honestly claim: after it, the reader
either opened that README or consciously chose not to, and repeating it adds
no information. Each ancestor README earns its OWN slot, independently claimed
—— reading a child folder's file says nothing about whether a GRANDPARENT's
README was ever read, so silencing one must never silence the other. Reading
a README ITSELF also claims its own folder's slot, so the reminder never
appears for a folder whose README is already open (but ancestors ABOVE it are
still checked and may still fire).

STATE (where and why): the claim ledger lives OUTSIDE any repo —— under the OS
temp dir (`tempfile.gettempdir()`), overridable via `PLINT_STATE_DIR` for
tests. It deliberately does NOT sit beside this script: only `cscpt/.clint.log`
and its `.tmp*` siblings are git-ignored here, so any new dot-file in `cscpt/`
(dot-files are NOT invisible to git) would surface as an untracked change in
`git status` every session and eventually be committed or "tidied" away. This
hook also runs in EVERY project on this Mac (§ no repo-scope guard), so its
state cannot live in one repo anyway. The temp dir is outside every working
tree by construction, self-cleaning at the OS level, and losing it costs
exactly one duplicate reminder.

STATE SHAPE AND BOUNDS: one empty marker file per (session, README) —— keyed
on the README's own path, not its directory, since ANCESTOR WALK gave the
immediate folder's README and each ancestor's README their own independent
slot — under a per-session sub-folder keyed by a hash of `session_id`; the
marker name is a hash of the resolved README path, so no real path is written
anywhere. The claim is `os.open(..., O_CREAT|O_EXCL)` —— atomic, so the two or
three PARALLEL reads a single assistant turn issues cannot all decide they are
the first. Bounds are five: `_MAX_DIRS_PER_SESSION` caps one session's markers
(past it, the rule simply goes quiet), `_STATE_TTL_S` sweeps stale session
folders, `_MAX_SWEEP` bounds one sweep so it can never turn a read into a
directory walk, `_MAX_ANCESTORS` bounds the upward climb itself, and
`_MAX_README_LINES_PER_CALL` bounds reminder lines from one call.

FAIL DIRECTION —— CLAIM FIRST, THEN REMIND: the reminder is emitted ONLY if the
claim succeeded. If the state dir is unwritable, the rule therefore goes
SILENT rather than reminding on every read. That is deliberate and is the
opposite of the fail-open rule the repo-scope guards use, because the failure
modes are not symmetric: a scope guard failing closed silently disables a lint,
whereas THIS rule failing open would fire on every single read and destroy the
one property that makes it worth having. A hook that cries wolf is worse than
no hook. The claim is made only after every other gate has passed, so a
suppressed reminder can never be claimed away. One residual window is accepted
and named rather than hidden: if the final stdout write itself fails, the
README is already claimed and that one reminder is lost —— a missed reminder,
the harmless direction, and the same failure the other two rules already have.

README-RULE NOISE EXCLUSIONS (judgement calls, stated so they can be argued
with; applied to EVERY ancestor `_ancestor_dirs` visits, not just the
immediate folder): (1) a PROJECT ROOT —— a directory containing `.git`. A root
README is the project's front page, not a folder-level procedure, and nearly
every session reads something from the root, so it would burn the reminder on
the least specific README available —— this is also WHY the ancestor climb
stops there (see ANCESTOR WALK): it is the natural, already-argued boundary of
"a folder governing this project", so walking past it would start admitting
READMEs that belong to something else entirely. (2) DEPENDENCY / GENERATED
folders (`node_modules`, `site-packages`, `vendor`, `build`, `dist`, `.git`
internals, ...) —— their READMEs belong to third-party code and say nothing
about how the reader should behave. (3) `$HOME` and `/` —— neither is a
working folder. Everything else fires, INCLUDING outside this repo: "read the
folder's README before working in it" is generically true, exactly like the
CODE rule.

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
makes `regardless` match `regards` and `dearth` match `dear`, firing on ordinary
prose and training the reader to ignore the hook. Inner spaces match one-or-more
whitespace so a line-wrapped "best wishes" still hits, and the echoed marker is
whitespace-collapsed to keep output at one line per rule. Only NEW text is
scanned (Write `content`, Edit/MultiEdit `new_string`) —— the rule is about what
goes in, not what comes out —— and each rule sits in its own try/except so one
failing never suppresses the other.

WHY THE SIGN-OFF MARKERS ARE THE FULL PHRASES ("yours sincerely" / "yours
faithfully") AND NEVER A BARE "yours": word boundaries stop `yourself` matching,
but they cannot stop `yours` itself, which is an ordinary English possessive
("the choice is yours", "yours may differ") that appears constantly in normal
prose and in this repo's own protocol files. It was the single biggest
false-positive source in the marker list, and a heuristic that cries wolf is
worse than no heuristic —— see WHY IT CAN NEVER BLOCK above. Those two phrases
are the only genuine letter sign-offs built on the word, so matching them
exactly keeps every real hit whilst dropping the noise. ("yours sincerely" is
additionally covered by the standalone `sincerely` marker; it is listed in full
anyway so the pair reads as the deliberate, complete replacement rather than an
accidental half-edit.)
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
import tempfile

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
# `regards` and `dearth` match `dear`, which are common words that would fire
# the rule on ordinary prose and train the reader to ignore it. Inner spaces are
# `\s+` so a line-wrapped "best\nwishes" still matches.
# The sign-off built on "yours" is listed ONLY as its two full phrases: word
# boundaries cannot rescue a bare `yours`, which is an everyday possessive
# ("the choice is yours") and fired constantly on ordinary prose. These two are
# the only real letter forms of it —— full rationale in the module docstring.
_MARKERS = (
    "hello", "dear", "greetings", "regards", "sincerely",
    "best wishes", "to whom it may concern",
    "yours sincerely", "yours faithfully",
)
_MARKER_RE = re.compile(
    r"\b(" + "|".join(m.replace(" ", r"\s+") for m in _MARKERS) + r")\b",
    re.IGNORECASE)

# --- README rule ------------------------------------------------------------
# Read tools. Used ONLY as an explicit exclusion for the two write rules (a
# payload with no `tool_name` keeps its pre-existing behaviour) and as the
# entry gate for the README rule.
_READ_TOOLS = {"Read", "NotebookRead"}

_README_NAME = "README.md"

# Path segments that make a README irrelevant to how the reader should behave:
# third-party code and generated output. A README in any of these documents
# somebody else's package, not this folder's procedure.
_SKIP_SEGMENTS = {
    ".git", "node_modules", "site-packages", "dist-packages", "vendor",
    ".venv", "venv", "env", "__pycache__", ".cache", ".tox", ".mypy_cache",
    "build", "dist", ".next", "target",
}

# Claim ledger. OUTSIDE any repo by design —— see the module docstring (STATE):
# a dot-file beside this script would show up in `git status`, and this hook
# runs in every project on this Mac, so its state belongs to no single repo.
# `PLINT_STATE_DIR` exists so a test neither reads nor pollutes the real one.
_STATE_ROOT = (os.environ.get("PLINT_STATE_DIR")
               or os.path.join(tempfile.gettempdir(), "plint_readme_seen"))

# Self-limiting bounds (docstring: STATE SHAPE AND BOUNDS). Now one marker per
# (session, README) rather than (session, directory) —— see ANCESTOR WALK: a
# single read can claim several ancestor READMEs at once, so this is the cap
# on distinct READMEs a session may ever claim, not on reads or directories.
_MAX_DIRS_PER_SESSION = 200      # past this, the rule goes quiet for that session
_STATE_TTL_S = 3 * 24 * 3600     # stale session folders swept after 3 days
_MAX_SWEEP = 200                 # entries a single sweep may look at

# Bounds the UPWARD ancestor walk itself (docstring: ANCESTOR WALK) —— a
# backstop against a pathological chain (symlink loop, or a filesystem with no
# `.git` anywhere so the walk would otherwise run to `/`), never hit for a
# real repo. Kept separate from `_MAX_README_LINES_PER_CALL` below: this one
# bounds how far up the FILESYSTEM is examined, that one bounds how many
# reminder LINES a single call may emit.
_MAX_ANCESTORS = 25

# Bounds reminder LINES the README rule emits from ONE read call, independent
# of `_MAX_ANCESTORS` above —— a deeply-nested tree with a README at every
# level is legal but should not dump two dozen lines into one turn.
_MAX_README_LINES_PER_CALL = 5

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


def _target_dir(fp, cwd):
    """Absolute, symlink-resolved directory holding the read target. A relative
    `file_path` is resolved against the payload's `cwd`, never the hook
    process's own cwd —— the harness may launch this from anywhere. `realpath`
    makes the state key stable (on macOS `/var/...` and `/private/var/...` are
    the same folder and must not claim two separate slots)."""
    if not os.path.isabs(fp) and isinstance(cwd, str) and cwd:
        fp = os.path.join(cwd, fp)
    return os.path.realpath(os.path.dirname(os.path.abspath(fp)))


def _ancestor_dirs(d):
    """`d` itself, then each parent upward, stopping AFTER the first ancestor
    that is itself a project root (contains `.git`) —— walking any further
    would leave the project entirely, picking up READMEs that govern
    something else (docstring: ANCESTOR WALK). `d` is already realpath'd by
    the caller, so `os.path.dirname` climbing it stays real too.

    Bounded by `_MAX_ANCESTORS` as a backstop for a chain with no `.git`
    anywhere (e.g. a scratch folder outside any repo) so the walk cannot run
    unbounded to `/` —— it still terminates there via `parent == cur`, this
    is only insurance against a pathological symlink loop.
    """
    dirs = []
    cur = d
    for _ in range(_MAX_ANCESTORS):
        dirs.append(cur)
        if os.path.exists(os.path.join(cur, ".git")):
            break  # project root reached; its own README is noise (below)
        parent = os.path.dirname(cur)
        if parent == cur:
            break  # filesystem root
        cur = parent
    return dirs


def _is_readme(base):
    """True if this basename IS a README. Deliberately generous (`README`,
    `readme.md`, `README.txt`, ...): being wrong here only ever SUPPRESSES a
    reminder, which is the harmless direction —— a reader opening anything
    called a README is doing the very thing the rule would ask for."""
    low = base.lower()
    return low == "readme" or low.startswith("readme.")


def _readme_is_noise(d):
    """True if a README in `d` is not the folder-level procedure this rule
    exists to surface. Full rationale for each exclusion is in the module
    docstring (README-RULE NOISE EXCLUSIONS)."""
    if d in ("/", os.sep):
        return True
    try:
        if d == os.path.realpath(os.path.expanduser("~")):
            return True
    except Exception:
        pass  # unresolvable HOME is not a reason to lose the rule
    for seg in _path_parts(d):
        if seg.lower() in _SKIP_SEGMENTS:
            return True
    # A directory holding `.git` is a project ROOT (see docstring). `exists`,
    # not `isdir`: in a worktree or submodule `.git` is a FILE, and those roots
    # are just as much project front pages as an ordinary clone's.
    return os.path.exists(os.path.join(d, ".git"))


def _sweep_state(keep):
    """Delete session folders past the TTL. Best-effort and BOUNDED: runs only
    when a session folder is first created, looks at `_MAX_SWEEP` entries at
    most, and swallows every error —— housekeeping must never cost a read."""
    try:
        names = sorted(os.listdir(_STATE_ROOT))[:_MAX_SWEEP]
    except Exception:
        return
    cutoff = time.time() - _STATE_TTL_S
    for name in names:
        path = os.path.join(_STATE_ROOT, name)
        if path == keep:
            continue
        try:
            # A session folder's mtime moves every time a marker is added, so
            # an active session can never be swept out from under itself.
            if os.path.getmtime(path) < cutoff:
                shutil.rmtree(path, ignore_errors=True)
        except Exception:
            pass


def _claim_readme(session_id, readme_path):
    """Atomically record (session, README) as reminded —— once-per-README,
    extended from the original once-per-DIRECTORY (same mechanism, keyed on
    the README's own path instead of its directory, so an ancestor's README
    and the immediate folder's README each get their own independent slot).

    True  -> this is the FIRST claim, so the caller may remind.
    False -> already claimed, session cap reached, or the state is unusable.

    `O_CREAT|O_EXCL` is the whole point: a turn can issue several reads in
    parallel, and a read-then-write ledger would let two of them both conclude
    they were first. False on ANY failure keeps the rule silent rather than
    repeating —— the deliberate fail direction, argued in the docstring."""
    try:
        sid = hashlib.sha1(session_id.encode("utf-8", "replace")).hexdigest()
        sdir = os.path.join(_STATE_ROOT, "s_" + sid[:16])
        fresh = not os.path.isdir(sdir)
        os.makedirs(sdir, exist_ok=True)
        if fresh:
            _sweep_state(sdir)
        elif len(os.listdir(sdir)) >= _MAX_DIRS_PER_SESSION:
            return False
        marker = os.path.join(
            sdir,
            hashlib.sha1(readme_path.encode("utf-8", "replace")).hexdigest()[:20])
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        return True
    except Exception:
        return False


def _readme_lines(data, tool_input):
    """The README rule. Returns a list of reminder lines (possibly empty) ——
    one per NEWLY-claimed README found by walking from the read target's own
    directory up through its ancestors to the repo root (docstring: ANCESTOR
    WALK), nearest folder first.

    Gate order is deliberate: every cheap, purely-local test runs BEFORE a
    claim, so a read that was never going to be reminded about cannot consume
    that README's one slot (coding.md: claim shared state only after every
    gate that could still abort)."""
    fp = tool_input.get("file_path")
    sid = data.get("session_id")
    # No session id -> the "once per session" contract cannot be honoured, and
    # the payload is malformed anyway. Silence is the only honest answer.
    if not (isinstance(fp, str) and fp
            and isinstance(sid, str) and sid.strip()):
        return []
    d = _target_dir(fp, data.get("cwd"))
    read_base = os.path.basename(fp.replace("\\", "/").rstrip("/"))
    lines = []
    for anc in _ancestor_dirs(d):
        readme = os.path.join(anc, _README_NAME)
        if not os.path.isfile(readme) or _readme_is_noise(anc):
            continue
        if anc == d and _is_readme(read_base):
            # Reading THIS README (the immediate folder's own) IS the
            # behaviour the rule wants —— claim it so no later read in the
            # same folder produces a redundant reminder. Ancestors further up
            # are still checked below; reading a child folder's file says
            # nothing about whether a GRANDPARENT's README was ever read.
            _claim_readme(sid, readme)
            continue
        if not _claim_readme(sid, readme):
            continue  # already reminded this session, or state unusable
        lines.append(
            "Read target sits under a folder that has a `README.md` —— read "
            "`%s` FIRST (folder-level conventions/procedures live there, not "
            "in the file you opened). Shown once per README per session."
            % readme)
        if len(lines) >= _MAX_README_LINES_PER_CALL:
            break
    return lines


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
    '"tool_name":"Read",'
    '"tool_input":{"file_path":"/abs/file.py"}}\' \\\n'
    '    | python3 cscpt/plint.py\n'
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
        return 0

    if not isinstance(data, dict):
        return 0

    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0

    lines = []

    # The matcher is tool-name-only, so the rules split here: the two write
    # rules are skipped ONLY on an explicit read tool (a payload without
    # `tool_name` keeps its old behaviour), and the README rule requires one.
    # Rationale in the module docstring (WHY THE MATCHER CARRIES `Read`).
    tool_name = data.get("tool_name")
    is_read = isinstance(tool_name, str) and tool_name in _READ_TOOLS

    # --- CODE rule (mechanical) --------------------------------------------
    try:
        fp = tool_input.get("file_path")
        if (not is_read and isinstance(fp, str) and fp and _wants_coding(fp)
                and os.path.isfile(_CODING_MD)):
            lines.append(
                "Target `%s` is a script/pcmd —— read `%s` FIRST (issue-reporting "
                "format, self-contained rationale, regression test per fix)."
                % (os.path.basename(fp), _CODING_MD))
    except Exception:
        pass  # one rule failing must never suppress the other

    # --- DELIVERABLE rule (heuristic) --------------------------------------
    try:
        content = "" if is_read else _written_content(tool_input)
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

    # --- README rule (mechanical, read-time) --------------------------------
    try:
        if is_read:
            lines.extend(_readme_lines(data, tool_input))
    except Exception:
        pass  # each rule is isolated; one failing never suppresses another

    if not lines:
        return 0  # no rule matched -> silent, and the call proceeds

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
