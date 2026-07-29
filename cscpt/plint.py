#!/usr/bin/env python3
"""PreToolUse hook —— "protocol-read linter". BEFORE a file is written (or read),
it looks at what is about to happen and injects a NON-BLOCKING reminder to read
the governing file FIRST.

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: a PreToolUse hook —— before a write or read lands, it reminds you to
  read the governing file FIRST.
* THREE RULES: script/pcmd write -> `universal/coding.md`; greeting/sign-off
  content -> `universal/writing.md` (incl. `## Stylisation`); reading from a
  folder with a `README.md` -> that README, once per folder per session.
* IF IT FIRES: read the named file, or ignore it if already read —— ADVISORY,
  it can NEVER gate a call.
* KNOWN LIMITS: the deliverable rule is a heuristic (`hello` in a script trips
  it); a comms-named pcmd is skipped; project-root/vendor folders get no README
  reminder.
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
certain) —— the READ target's own directory contains a `README.md`, the target
is not itself that README, the directory is not excluded as noise, and this
directory has not already been reminded in this session.

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

WHY ONCE PER DIRECTORY PER SESSION (the load-bearing constraint, not an
optimisation): reads are the single most frequent tool call, and a reminder on
every read inside a README-bearing folder would fire many times per turn. It
would be tuned out within one session and would take the other two rules'
credibility with it —— the same failure the DELIVERABLE rule's word boundaries
exist to prevent. One reminder per folder is also all
the rule can honestly claim: after it, the reader either opened the README or
consciously chose not to, and repeating it adds no information. Reading the
README ITSELF also claims the folder, so the reminder never appears for a
folder whose README is already open.

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

STATE SHAPE AND BOUNDS: one empty marker file per (session, directory), under a
per-session sub-folder keyed by a hash of `session_id`; the marker name is a
hash of the resolved directory path, so no real path is written anywhere. The
claim is `os.open(..., O_CREAT|O_EXCL)` —— atomic, so the two or three PARALLEL
reads a single assistant turn issues cannot all decide they are the first.
Bounds are three: `_MAX_DIRS_PER_SESSION` caps one session's markers (past it,
the rule simply goes quiet), `_STATE_TTL_S` sweeps stale session folders, and
the sweep runs ONLY when a session folder is first created and scans at most
`_MAX_SWEEP` entries, so it can never turn a read into a directory walk.

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
folder is already claimed and that one reminder is lost —— a missed reminder,
the harmless direction, and the same failure the other two rules already have.

README-RULE NOISE EXCLUSIONS (judgement calls, stated so they can be argued
with): (1) a PROJECT ROOT —— a directory containing `.git`. A root README is
the project's front page, not a folder-level procedure, and nearly every
session reads something from the root, so it would burn the reminder on the
least specific README available. (2) DEPENDENCY / GENERATED folders
(`node_modules`, `site-packages`, `vendor`, `build`, `dist`, `.git` internals,
...) —— their READMEs belong to third-party code and say nothing about how the
reader should behave. (3) `$HOME` and `/` —— neither is a working folder.
Everything else fires, INCLUDING outside this repo: "read the folder's README
before working in it" is generically true, exactly like the CODE rule.

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

# Self-limiting bounds (docstring: STATE SHAPE AND BOUNDS).
_MAX_DIRS_PER_SESSION = 200      # past this, the rule goes quiet for that session
_STATE_TTL_S = 3 * 24 * 3600     # stale session folders swept after 3 days
_MAX_SWEEP = 200                 # entries a single sweep may look at

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


def _claim_dir(session_id, d):
    """Atomically record (session, directory) as reminded.

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
            sdir, hashlib.sha1(d.encode("utf-8", "replace")).hexdigest()[:20])
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        return True
    except Exception:
        return False


def _readme_line(data, tool_input):
    """The README rule. Returns the reminder line, or None to stay silent.

    Gate order is deliberate: every cheap, purely-local test runs BEFORE the
    claim, so a read that was never going to be reminded about cannot consume
    the folder's one slot (coding.md: claim shared state only after every gate
    that could still abort)."""
    fp = tool_input.get("file_path")
    sid = data.get("session_id")
    # No session id -> the "once per session" contract cannot be honoured, and
    # the payload is malformed anyway. Silence is the only honest answer.
    if not (isinstance(fp, str) and fp
            and isinstance(sid, str) and sid.strip()):
        return None
    d = _target_dir(fp, data.get("cwd"))
    readme = os.path.join(d, _README_NAME)
    if not os.path.isfile(readme) or _readme_is_noise(d):
        return None
    base = os.path.basename(fp.replace("\\", "/").rstrip("/"))
    if _is_readme(base):
        # Reading the README IS the behaviour the rule wants —— claim the
        # folder so no later read in it produces a redundant reminder.
        _claim_dir(sid, d)
        return None
    if not _claim_dir(sid, d):
        return None  # already reminded this session, or state unusable
    return ("Read target sits in a folder that has a `README.md` —— read `%s` "
            "FIRST (folder-level conventions/procedures live there, not in the "
            "file you opened). Shown once per folder per session."
            % readme)


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
            line = _readme_line(data, tool_input)
            if line:
                lines.append(line)
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
