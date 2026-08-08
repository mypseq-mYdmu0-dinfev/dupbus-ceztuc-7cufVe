#!/usr/bin/env python3
"""Batch-Time Linter —— mid-turn chat corrector + chapter-marker guard (four hook stages in one body)

The one lint that reaches the model MID-TURN. Stop-side clint detects a chat-discipline breach only after the turn has
ended (and its warning reaches nobody in the Desktop app); hlint's tally corrects only at the NEXT prompt. This file
closes the gap in between: `batch` rides PostToolBatch —— the sole mid-turn model channel that costs zero extra
invocations —— and the three marker stages make the 30/07 duplicate-chapter failure structurally impossible.

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: four harness stages; never run by hand.
* `batch` (PostToolBatch): mid-turn corrector —— IF IT FIRES, this turn's chat text already breached root
  CLAUDE.md §3.2. Emit no further chat prose, land content in the `response_`, never apologise in chat.
* `marker-pre`/`marker-post`: deny a SECOND `mark_chapter` per turn (root §3.1.6.2). IF DENIED: the marker
  already exists —— do NOT retry; continue with TEA3.
* `prompt`: disarms the marker guard on each genuine prompt.
* Verdicts log to `cscpt/.blint.log`. Only a marker deny exits 2; every other verdict exits 0.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
Root scope: every path is anchored on this file's own `__file__` —— the repo root (its parent's parent) for scope
checks and the log, plus the repo root's PARENT (`.../GitHub`, the Reader folder) for READER-mode detection. No other
repo is walked or resolved; a user-level hook routinely runs from foreign repos, so nothing here may ever be
cwd-relative.

WIRING. FOUR registrations in the USER-level `~/.claude/settings.json` (the Desktop app silently ignores
project-level hooks), all pointing at this one file with a stage word:
  PostToolBatch (no matcher)                          -> `blint.py batch`
  PreToolUse  matcher `mcp__ccd_session__mark_chapter` -> `blint.py marker-pre`
  PostToolUse matcher `mcp__ccd_session__mark_chapter` -> `blint.py marker-post`
  UserPromptSubmit (no matcher)                        -> `blint.py prompt`
One body, not four scripts: the stages share the scope guard, the transcript reader, the ledger and the stdin guard,
and a marker guard split across files would let a half-edit desynchronise the arm/disarm pair.

WHY POSTTOOLBATCH, verified against the installed Desktop binary's own hook registry (2.1.222), not from docs:
* It fires once after every tool-call batch resolves, BEFORE the next model request; exit-0
  `hookSpecificOutput.additionalContext` is injected into that ALREADY-SCHEDULED request. Zero extra model
  invocations, zero extra turns, no second apparent turn-end —— the properties Stop can never have (at Stop the model
  is stopped, and reaching it means waking it; that is why clint was demoted to warn-only).
* ⚠️ EXIT 2 THERE KILLS THE AGENTIC LOOP —— registry text: "Exit code 2 - stop the agentic loop (stderr shown to user
  only)". The turn would die mid-flight and the TEAs would never run. The `batch` stage therefore exits 0 on EVERY
  verdict, breach included; nothing in it may ever return 2. The marker `pre` stage is different BY EVENT: PreToolUse
  exit 2 denies one tool call and the turn continues —— that is the one sanctioned 2 in this file.
* Payload carries `tool_calls` and the common fields but NOT the assistant's text, so the prose is read from the
  transcript tail —— the approach alint proved in production. The read is byte-bounded (8 MB, mlint's bound) and
  parses BACKWARDS only to the turn boundary, so the common case costs a few records, not the window.
* BLIND SPOT, stated: prose in a turn's FINAL message is followed by Stop, not another batch, so this stage never
  sees it. hlint's next-prompt tally remains the net under that gap; this stage exists for the mid-turn breaches.

CLASSIFICATION IS COPIED FROM clint.py, BY MANDATE, NOT BY ACCIDENT. The line contracts (`_split_glyph` through
`_line_breach`, the exemptions, the dot and sentinel-lists escapes) are clint's, duplicated here. A parallel change
stream owned clint.py when this file was created, so importing or refactoring it was off the table; and a hook body
importing a sibling module also couples both hooks to one half-saved edit, where a copy fails alone. DRIFT RULE:
clint.py is CANONICAL for the line contracts —— when its contracts change, re-sync these copies in the same turn, and
say so in the commit. The solo-SHA-label check is deliberately NOT copied: it needs the window's COMPLETE `🦈`-line
count, and mid-turn the window is incomplete by definition —— the first line of a legal multi-repo batch would be
false-flagged. Stop-side clint keeps that check; mid-turn it is unsound.

SCOPE IS CONSERVATIVE, the OPPOSITE of clint's fail-open, and both are deliberate: clint's worst misfire is a log
line, so it fails open to REPO mode; this stage INJECTS MODEL-VISIBLE TEXT, and nagging a foreign cockpit about a
rule it never adopted is noise at best and bait for phantom compliance at worst (the hlint-tally precedent). So:
`cwd` resolving into this repo -> REPO; exactly the repo's parent -> READER; the transcript slug as fallback; neither
usable -> OFF, silent. Sub-agent payloads (`agent_id`/`agent_type`, the only reliable discriminator —— the transcript
path LIES for sub-agents, which always hand over the MAIN session's) are skipped: an SA's text is its return value to
the caller, not chat.

DEDUP IS BY CONTENT HASH, NEVER PROMPT ID. Task-notification wakes re-fire hooks under FRESH prompt ids over the SAME
unchanged window (clint once logged seven growing verdicts for one breach window this way), so a prompt-id ledger
re-corrects on every wake. The sha1 of the offending lines changes exactly when the breach content changes: same
content -> silent, a NEW breach line -> one new correction counting the whole window. The ledger rides this file's
own stage log (the mlint/hlint precedent —— no second state file to drift or leak into `git status`); a pruned or
lost ledger line costs one duplicate advisory, never a loop.

ACCEPTED OVERLAP WITH HLINT, stated rather than hidden: hlint tallies clint's Stop verdict at the NEXT prompt with no
knowledge of this file, so a mid-turn breach corrected here is tallied AGAIN one prompt later. Sharing state safely
was impossible at build time (hlint was under the same parallel ownership as clint), and the duplicate is one
advisory line, in different turns, each true when emitted. If hlint later learns to read this log, key the skip on
the `corrected:*@hash` ledger entries.

THE MARKER GUARD, and why it fails OPEN everywhere: root §3.1.6.2 allows ONE chapter marker per practical turn, and a
marker cannot be removed once made. MCP tools are never hook-exempt, so `marker-pre` (PreToolUse) can deny the
duplicate before it exists —— the 30/07 failure (a Stop-block continuation re-running TEA2) becomes impossible. But a
FALSE deny blocks a LEGITIMATE marker and breaks the user's navigation —— the very thing being protected —— so every
doubtful path allows:
* State keys on `session_id`, NEVER `prompt_id` (wakes and continuations mint fresh prompt ids).
* `marker_recorded` (written by `marker-post`, skipped when the tool call errored so a retry stays legal) arms;
  `prompt_reset` (written by `prompt`) disarms; newest wins. A Stop-block continuation fires no UserPromptSubmit, so
  the guard STAYS ARMED across it —— exactly the property the 30/07 mode requires. A `<task-notification>` wake DOES
  fire UserPromptSubmit, so `prompt` ignores prompts opening with a system-injected tag.
* SECOND BELT: `marker_recorded` stores the uuid of the turn's genuine user line, and a deny requires that uuid to
  STILL be the transcript's newest genuine user line. A dead or lagging `prompt` registration therefore cannot deny
  past its own turn —— the next genuine prompt moves the anchor and the guard falls open on its own.
* IF THE STATE (this log) IS LOST: the guard disarms entirely until the next `marker_recorded` —— duplicate markers
  become possible again, i.e. the exact pre-guard status quo. Nothing is ever denied on a lost ledger.
* KNOWN RESIDUAL: two mark_chapter calls in ONE batch are both approved before either records (pre fires before
  post). Mid-turn user messages also re-arm via `prompt_reset` although root §3.1.7.6.1 keeps them in the same
  practical turn. Both fail towards ALLOW, are rare, and are accepted —— closing them would trade a real false-deny
  risk for a corner case hlint already reports.

LOG. One line per invocation, TAB-separated, stage named —— `no_stdin`, `subagent`, `off_scope`, `no_transcript`,
`unreadable_transcript`, `no_boundary`, `clean`, `clean:dot`, `clean:compaction`, `exempt:*`, `dup`,
`corrected:<class>:<n>@<hash12>`, `message_failed`, `bad_stage`, and the marker stages' `mk_*`/`p_*`/
`marker_recorded`/`prompt_reset` family. The `corrected:` and `marker_recorded`/`prompt_reset` lines double as the
ledgers above —— the one part of the log that is parsed back. Same 1000/800 prune hysteresis as the sibling lints;
path overridable via BLINT_LOG for tests. A hook that leaves no trace is how PostCompact stayed dead 70 days ——
"never fired" must stay distinguishable from "fired and found nothing".

FAIL-SAFE CONTRACT: any missing field, unreadable file or internal error degrades to silence (batch) or allow
(marker); the stdin guard is the only non-zero exit outside the marker deny, and it exits 3, never 2, so a hand run
can never block a tool call. Pinned by `cp/ccsim/sandbox/blint_batch_corrector_regression_test.py` and
`cp/ccsim/sandbox/blint_marker_guard_regression_test.py`.
"""

import hashlib
import io
import json
import os
import re
import select
import stat
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# SCOPE —— derived from this file's own location, never hard-coded, so the
# repo stays relocatable. CONSERVATIVE: unusable signals mean OFF, because
# this lint injects model-visible text / denies a tool call (see docstring
# SCOPE IS CONSERVATIVE for why this inverts clint's fail-open).
# ---------------------------------------------------------------------------
_REPO_ROOT_REAL = os.path.realpath(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_REPO_SLUG = re.sub(r"[/ ]", "-", _REPO_ROOT_REAL.rstrip("/"))
_READER_ROOT_REAL = os.path.dirname(_REPO_ROOT_REAL)
_READER_SLUG = re.sub(r"[/ ]", "-", _READER_ROOT_REAL.rstrip("/"))

MODE_REPO = "repo"       # root CLAUDE.md §3.2 —— declarations only
MODE_READER = "reader"   # GitHub/ CLAUDE.md —— zero chat text
MODE_OFF = "off"         # elsewhere, or unknowable —— stay silent


def _mode(data):
    """MODE_REPO, MODE_READER or MODE_OFF for this payload. Unlike clint,
    every unusable shape is OFF: a corrector must never nag, and a guard must
    never deny, a project it cannot place. Never raises."""
    try:
        if not isinstance(data, dict):
            return MODE_OFF
        cwd = data.get("cwd")
        if isinstance(cwd, str) and cwd:
            real = os.path.realpath(cwd)
            if (real == _REPO_ROOT_REAL
                    or real.startswith(_REPO_ROOT_REAL + os.sep)):
                return MODE_REPO
            if real == _READER_ROOT_REAL:  # EXACT, never a sub-path
                return MODE_READER
            return MODE_OFF
        tp = data.get("transcript_path")
        if isinstance(tp, str) and tp:
            m = re.search(r"/projects/([^/]+)/", tp)
            if m:
                slug = m.group(1)
                if slug == _REPO_SLUG or slug.startswith(_REPO_SLUG + "-"):
                    return MODE_REPO
                if slug == _READER_SLUG:
                    return MODE_READER
        return MODE_OFF
    except Exception:
        return MODE_OFF


def _is_subagent(data):
    """hook_guide §5.6.1: `agent_id`/`agent_type` is the ONLY reliable
    sub-agent discriminator —— the transcript path lies (an SA's payload
    hands over the MAIN session's path)."""
    return bool(data.get("agent_id") or data.get("agent_type"))


# ---------------------------------------------------------------------------
# LINE CONTRACTS —— copied from clint.py by mandate (docstring: CLASSIFICATION
# IS COPIED). clint.py stays canonical; re-sync on any contract change there.
# ---------------------------------------------------------------------------
_GLYPHS = ("✅", "⇠", "➡", "\U0001f988", "⚠", "\U0001f6a8")
_VS16 = "️"                 # emoji variation selector
_IO_GLYPHS = ("✅", "⇠", "➡")
_G_SHA = "\U0001f988"
_G_SENTINEL = "\U0001f6a8"
_SENTINEL_CANON = "🚨 Compaction Detected —— stopped all tasks.".replace(_VS16, "")
_SENTINEL_BODY = _SENTINEL_CANON.split(" ", 1)[1]
_HR_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
_PAREN_RE = re.compile(r"\([^()]*\)")
_TICKED_RE = re.compile(r"`[^`]*`")
_IO_RESIDUE_RE = re.compile(r"^[\s,;:.*_~×0-9+\-–—…]*$")
_SHA_LABEL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,23}:\s+")
_SHA_TOKEN_RE = re.compile(r"^[0-9a-fA-F]{8,40}$")
_SHA_RESIDUE_RE = re.compile(r"^[\s,;·|&+]*$")
_WARN_MAX_WORDS = 5
_WARN_MAX_HYPHENS = 3
# Kept out of every agent-readable surface, as in clint: a
# visible limit is a limit an agent will spend up to.
_WARN_MAX_CHARS = 68
_PROGRESS_RE = re.compile(
    r"\b(?:run|runs|running|ran|await|awaits|awaiting|wait|waits|waiting"
    r"|proceed\w*|continu\w*|ongoing|underway|in-?flight|progress\w*|start\w*"
    r"|dispatch\w*|monitor\w*|work|works|working|pending|queued|still|next"
    r"|standby|standing|checking|reading|writing|building|testing|verifying"
    r"|fleet|done|complet\w*|finish\w*|updating|updated|now)\b", re.I)
_BLOCKER_RE = re.compile(
    r"\b(?:block\w*|stop\w*|halt\w*|abort\w*|stall\w*|fail\w*|error\w*"
    r"|crash\w*|broke|broken|cannot|can't|cant|unable|deni\w*|refus\w*"
    r"|reject\w*|forbidden|missing|absent|unavailable|offline|unreachable"
    r"|timeout|timed|expired|conflict\w*|clash\w*|mismatch\w*|corrupt\w*"
    r"|invalid|malformed|unknown|unrecognis\w*|unrecogniz\w*|ambiguous"
    r"|unclear|404|403|500|limit|limits|died|dead|risk\w*|unsafe|wrong"
    r"|incorrect|stale|desync\w*|lost|clobber\w*|overwrit\w*)\b", re.I)
_SYSTEM_INJECTED_TAGS = (
    "<task-notification>", "<local-command-caveat>",
    "<local-command-stdout>", "<command-name>", "<command-message>",
    "<command-args>")
_YN_TOKEN = " yn"
_OVERRIDE_RE = re.compile(r"\boverrid(?:e|ing)\b", re.I)
_SIC_RE = re.compile(r"\bsic\b", re.I)
_SIC_NW_RE = re.compile(r"\bsic\s+(\d{1,3})\s*w\b", re.I)
_SIC_DEFAULT_WORDS = 10
_DATS_MAX_WORDS = 10


def _split_glyph(s):
    """(base glyph, remainder) for a stripped line, tolerating the `**…**`
    bold wrapper and the variation selector; (None, s) when glyph-free."""
    t = s
    if t.startswith("**"):
        t = t[2:]
        if t.endswith("**"):
            t = t[:-2]
        t = t.strip()
    t = t.replace(_VS16, "")
    for g in _GLYPHS:
        if t.startswith(g):
            return g, t[len(g):].strip()
    return None, t


def _io_ok(rest):
    """True for a well-formed I/O declaration body (§3.2.1–3)."""
    if not rest:
        return False
    if not (_TICKED_RE.search(rest) or "(" in rest):
        return False
    body = rest
    for _ in range(8):
        stripped = _PAREN_RE.sub(" ", body)
        if stripped == body:
            break
        body = stripped
    body = _TICKED_RE.sub(" ", body)
    if "`" in body:
        return False
    return bool(_IO_RESIDUE_RE.match(body))


def _sha_ok(rest):
    """True for a well-formed SHA declaration body (§3.2.4)."""
    if not rest:
        return False
    body = _SHA_LABEL_RE.sub("", rest, count=1)
    spans = _TICKED_RE.findall(body)
    if not spans:
        return False
    for span in spans:
        if not _SHA_TOKEN_RE.match(span[1:-1].strip()):
            return False
    residue = _TICKED_RE.sub(" ", body)
    if "`" in residue:
        return False
    return bool(_SHA_RESIDUE_RE.match(residue))


def _warn_breach(rest):
    """Breach class for a `⚠️` body, or None if a permitted blocker."""
    if not rest:
        return "warn_empty"
    if _io_ok(rest) or _sha_ok(rest) or rest == _SENTINEL_BODY:
        return "warn_shape"
    if len(rest.split()) > _WARN_MAX_WORDS:
        return "warn_words"
    if rest.count("-") > _WARN_MAX_HYPHENS:
        return "warn_hyphens"
    if len(rest) > _WARN_MAX_CHARS:
        return "warn_chars"
    if _PROGRESS_RE.search(rest) and not _BLOCKER_RE.search(rest):
        return "warn_progress"
    return None


def _line_breach(line, mode):
    """None if the line is permitted chat under `mode`, else a class tag."""
    s = line.strip()
    if not s:
        return None
    if mode == MODE_READER:
        return "reader"
    if _HR_RE.match(line):
        return None
    g, rest = _split_glyph(s)
    if g is None:
        return "prose"
    if g in _IO_GLYPHS:
        return None if _io_ok(rest) else "io_shape"
    if g == _G_SHA:
        return None if _sha_ok(rest) else "sha_shape"
    if g == _G_SENTINEL:
        return None if s.replace(_VS16, "") == _SENTINEL_CANON else "sentinel"
    return _warn_breach(rest)


def _text_of(content):
    """Yield each text block of an assistant message content."""
    if isinstance(content, str):
        yield content
    elif isinstance(content, list):
        for blk in content:
            if isinstance(blk, dict) and blk.get("type") == "text":
                t = blk.get("text")
                if isinstance(t, str):
                    yield t


def _is_real_user(obj):
    """A genuine user prompt —— not a tool_result-only turn, not a
    system-injected wrapper (task notifications, command echoes)."""
    if obj.get("type") != "user":
        return False
    content = (obj.get("message") or {}).get("content")
    if isinstance(content, str):
        return not content.lstrip().startswith(_SYSTEM_INJECTED_TAGS)
    if isinstance(content, list):
        return any(isinstance(b, dict) and b.get("type") != "tool_result"
                   for b in content)
    return False


def _trigger_text(obj):
    """Human-visible text of the turn's opening user message."""
    try:
        if not isinstance(obj, dict):
            return ""
        content = (obj.get("message") or {}).get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = [b.get("text") for b in content
                     if isinstance(b, dict) and b.get("type") == "text"
                     and isinstance(b.get("text"), str)]
            return "\n".join(parts)
    except Exception:
        pass
    return ""


def _sic_cap(msg):
    """The authorised `sic` word cap, or None if not invoked."""
    try:
        if not _SIC_RE.search(msg):
            return None
        m = _SIC_NW_RE.search(msg)
        if m:
            return int(m.group(1))
        return _SIC_DEFAULT_WORDS
    except Exception:
        return None


def _dats_exempt(offending):
    """True if the whole breach is the one sanctioned `DATS` line."""
    return (len(offending) == 1
            and offending[0].startswith("DATS")
            and len(offending[0].split()) <= _DATS_MAX_WORDS)


def _lone_dot_turn(all_lines):
    """True if the turn's whole non-blank content is a single `.`."""
    return len(all_lines) == 1 and all_lines[0] == "."


def _sentinel_list_line(judged, i):
    """True if judged[i] is a §5.3–§5.4 list shape (see clint)."""
    s = judged[i][0]
    if s.startswith("- "):
        return True
    return (s.endswith(":") and i + 1 < len(judged)
            and judged[i + 1][0].startswith("- "))


# ---------------------------------------------------------------------------
# TRANSCRIPT TAIL —— bounded (mlint's bound), parsed BACKWARDS to the turn
# boundary only, so the common case costs a handful of records.
# ---------------------------------------------------------------------------
_MAX_TRANSCRIPT_BYTES = 8 * 1024 * 1024


def _tail_lines(path):
    """Raw lines of the transcript's bounded tail, newline-aligned. May
    raise; callers map that to a silent/allow stage."""
    size = os.path.getsize(path)
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        if size > _MAX_TRANSCRIPT_BYTES:
            fh.seek(size - _MAX_TRANSCRIPT_BYTES)
            fh.readline()            # drop the partial first record
        return fh.read().splitlines()


def _parse_reversed(raw_lines):
    """Yield main-agent records newest-first; junk skipped."""
    for raw in reversed(raw_lines):
        raw = raw.strip()
        if not raw:
            continue
        try:
            o = json.loads(raw)
        except Exception:
            continue
        if isinstance(o, dict) and o.get("isSidechain") is not True:
            yield o


def _window(raw_lines):
    """(trigger user record, records after it in order) —— the current
    turn. (None, []) when no genuine user line sits inside the bound: the
    exemptions would be unknowable, so the caller stays silent."""
    window = []
    for o in _parse_reversed(raw_lines):
        if _is_real_user(o):
            window.reverse()
            return o, window
        window.append(o)
    return None, []


def _last_genuine_uuid(raw_lines):
    """uuid of the newest genuine user record, or ''."""
    for o in _parse_reversed(raw_lines):
        if _is_real_user(o):
            u = o.get("uuid")
            return u if isinstance(u, str) and u else ""
    return ""


# ---------------------------------------------------------------------------
# LOG + LEDGERS —— one line per invocation (hook_guide §7.7); the
# `corrected:*@hash` and `marker_recorded`/`prompt_reset` lines double as the
# dedup and marker-state ledgers (mlint/hlint precedent —— no second file).
# ---------------------------------------------------------------------------
_LOG = os.environ.get("BLINT_LOG") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".blint.log")
_LOG_MAX_LINES = 1000
_LOG_KEEP_LINES = 800
_LOG_MIN_BYTES_PER_LINE = 60
_LOG_PRUNE_AT_BYTES = _LOG_MAX_LINES * _LOG_MIN_BYTES_PER_LINE


def _prune_log():
    """Bound the log —— cheap, atomic, fail-safe (clint's pattern)."""
    tmp = None
    try:
        if os.stat(_LOG).st_size < _LOG_PRUNE_AT_BYTES:
            return
        with open(_LOG, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
        if len(lines) <= _LOG_MAX_LINES:
            return
        tmp = "%s.tmp.%d" % (_LOG, os.getpid())
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines[-_LOG_KEEP_LINES:]) + "\n")
        os.replace(tmp, _LOG)
        tmp = None
    except Exception:
        pass
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except Exception:
                pass


def _log_event(stage, sid="-", anchor="-", detail="-"):
    """Append one flattened record; all errors swallowed —— the log is
    diagnostics plus ledger, never the verdict itself."""
    try:
        with open(_LOG, "a", encoding="utf-8") as lf:
            lf.write("%s\tsession=%s\tstage=%s\tanchor=%s\tdetail=%s\n"
                     % (datetime.now().isoformat(timespec="seconds"),
                        sid, stage,
                        str(anchor)[:80].replace("\t", " ").replace("\n", " "),
                        str(detail)[:160].replace("\t", " ").replace("\n", " ")))
    except Exception:
        pass
    _prune_log()


def _ledger_fields(line):
    """{field: value} for one log line's `k=v` parts."""
    fields = {}
    for part in line.split("\t")[1:]:
        key, _, val = part.partition("=")
        fields.setdefault(key, val)
    return fields


def _already_corrected(sid8, mark):
    """True if a `corrected:*@mark` line exists for this session. An
    unreadable ledger reads False —— a duplicate advisory beats a silently
    lost one."""
    try:
        with open(_LOG, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except Exception:
        return False
    needle = "\tsession=%s\t" % sid8
    tag = "@%s" % mark
    for line in reversed(text.splitlines()):
        if needle not in line:
            continue
        stage = _ledger_fields(line).get("stage", "")
        if stage.startswith("corrected:") and stage.endswith(tag):
            return True
    return False


def _marker_state(sid8):
    """('armed', anchor) | ('reset', None) | (None, None) —— the NEWEST of
    `marker_recorded`/`prompt_reset` for this session wins. May raise; the
    caller fails open."""
    try:
        with open(_LOG, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except FileNotFoundError:
        return None, None
    needle = "\tsession=%s\t" % sid8
    for line in reversed(text.splitlines()):
        if needle not in line:
            continue
        fields = _ledger_fields(line)
        stage = fields.get("stage", "")
        if stage == "marker_recorded":
            return "armed", fields.get("anchor", "-")
        if stage == "prompt_reset":
            return "reset", None
    return None, None


# ---------------------------------------------------------------------------
# MESSAGES
# ---------------------------------------------------------------------------
_EXCERPT_CHARS = 40                      # hlint's stub convention

_GLOSS = {
    "prose": "chat prose bearing no declaration glyph",
    "io_shape": "an I/O declaration glyph carrying non-file-list text",
    "sha_shape": "the commit-SHA glyph carrying a non-hash body",
    "sentinel": "a compaction sentinel not matching §3.2.6's exact wording",
    "warn_empty": "a blocker glyph declaring nothing",
    "warn_words": "a blocker line past §3.2.5's ≤5w cap",
    "warn_hyphens": "a blocker line evading the word cap with joiners",
    "warn_chars": "an over-long blocker line",
    "warn_shape": "another declaration type wearing the blocker glyph",
    "warn_progress": "a progress note wearing the blocker glyph",
    "sic_overrun": "a `sic` status answer past its authorised word cap",
    "reader": "chat text in the zero-text Reader folder",
}
_GLOSS_FALLBACK = "an impermissible chat line"

_RULE = {
    MODE_REPO: ("Root CLAUDE.md §3.1–§3.2: chat carries the six declaration "
                "lines ONLY; substantive content belongs in this turn's "
                "`response_` file."),
    MODE_READER: ("GitHub/ CLAUDE.md: the Reader folder mandates ZERO chat "
                  "text, no matter what."),
}


def _correction_message(mode, cls, count, first):
    """The ONE injected line: count + class + gloss + stub + rule +
    correction. The stub is identifying only —— capped, backticked, dropped
    if it carries a backtick of its own (re-injecting the suppressed prose
    at length would be self-defeating)."""
    stub = (first or "").strip()
    if "`" in stub:
        stub = ""
    elif len(stub) > _EXCERPT_CHARS:
        stub = stub[:_EXCERPT_CHARS].rstrip() + "…"
    stub = "; first offender: `%s`" % stub if stub else ""
    return ("[blint hook] MID-TURN chat-discipline correction: this turn has "
            "ALREADY emitted %d impermissible chat line%s —— class `%s` "
            "(%s)%s. %s The emitted lines cannot be retracted —— correct "
            "from HERE: no further chat text this turn beyond the sanctioned "
            "declarations, and do NOT apologise in chat, an apology is "
            "itself chat prose."
            % (count, "" if count == 1 else "s", cls,
               _GLOSS.get(cls, _GLOSS_FALLBACK), stub,
               _RULE.get(mode, _RULE[MODE_REPO])))


_DENY_MSG = ("[blint hook] TEA2 duplicate DENIED (root CLAUDE.md §3.1.6.2): "
             "a chapter marker is already recorded for this turn, and a "
             "marker cannot be removed once made. Do NOT retry mark_chapter "
             "this turn —— the marker exists; carry on with the remaining "
             "turn-end actions. The guard disarms on the next genuine user "
             "prompt.\n")


# ---------------------------------------------------------------------------
# STAGES
# ---------------------------------------------------------------------------
def _stage_batch(data):
    """PostToolBatch corrector. EVERY verdict exits 0 —— exit 2 here kills
    the agentic loop (docstring: WHY POSTTOOLBATCH)."""
    sid = str(data.get("session_id") or "")[:8] or "unknown"
    if _is_subagent(data):
        _log_event("subagent", sid)
        return 0
    mode = _mode(data)
    if mode == MODE_OFF:
        _log_event("off_scope", sid)
        return 0
    tp = data.get("transcript_path") or ""
    if not isinstance(tp, str) or not tp or not os.path.isfile(tp):
        _log_event("no_transcript", sid)
        return 0
    try:
        raw = _tail_lines(tp)
    except Exception:
        _log_event("unreadable_transcript", sid)
        return 0
    trigger, window = _window(raw)
    if trigger is None:
        # No boundary in the bound -> exemptions unknowable.
        _log_event("no_boundary", sid)
        return 0

    judged = []
    for o in window:
        if o.get("type") != "assistant":
            continue
        if o.get("isApiErrorMessage") is True:
            continue
        msg = o.get("message") or {}
        if msg.get("role") != "assistant":
            continue
        for text in _text_of(msg.get("content")):
            for ln in text.splitlines():
                s = ln.strip()
                if s:
                    judged.append((s, _line_breach(ln, mode)))

    all_lines = [s for s, _ in judged]
    offending = [s for s, k in judged if k]
    classes = [k for s, k in judged if k]
    if not offending:
        _log_event("clean", sid)
        return 0
    if _lone_dot_turn(all_lines):
        _log_event("clean:dot", sid)
        return 0
    if mode == MODE_REPO and any(
            s.replace(_VS16, "") == _SENTINEL_CANON for s in all_lines):
        kept = [(s, k) for i, (s, k) in enumerate(judged)
                if k and not (k == "prose" and _sentinel_list_line(judged, i))]
        if not kept:
            _log_event("clean:compaction", sid)
            return 0
        offending = [s for s, k in kept]
        classes = [k for s, k in kept]

    cls = classes[0]
    typed = _trigger_text(trigger)
    if _OVERRIDE_RE.search(typed):
        _log_event("exempt:override", sid)
        return 0
    if mode == MODE_REPO:
        if _YN_TOKEN in typed:
            _log_event("exempt:yn", sid)
            return 0
        cap = _sic_cap(typed)
        if cap is not None:
            if len(" ".join(offending).split()) <= cap:
                _log_event("exempt:sic", sid)
                return 0
            cls = "sic_overrun"
        if _dats_exempt(offending):
            _log_event("exempt:dats", sid)
            return 0

    mark = hashlib.sha1(
        "\n".join(offending).encode("utf-8", "replace")).hexdigest()[:12]
    if _already_corrected(sid, mark):
        _log_event("dup", sid, detail="@" + mark)
        return 0
    message = _correction_message(mode, cls, len(offending), offending[0])
    try:
        sys.stdout.write(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PostToolBatch",
            "additionalContext": message}}))
    except Exception:
        _log_event("message_failed", sid)
        return 0
    _log_event("corrected:%s:%d@%s" % (cls, len(offending), mark), sid,
               detail=offending[0][:80])
    return 0


_MARKER_TOOL = "mcp__ccd_session__mark_chapter"


def _stage_marker_pre(data):
    """PreToolUse gate on mark_chapter. Exit 2 DENIES the one call; every
    doubtful path exits 0 (docstring: THE MARKER GUARD)."""
    sid = str(data.get("session_id") or "")[:8]
    if _is_subagent(data):
        _log_event("mk_subagent", sid or "-")
        return 0
    if data.get("tool_name") != _MARKER_TOOL:
        _log_event("mk_off_tool", sid or "-",
                   detail=str(data.get("tool_name"))[:40])
        return 0
    if not sid:
        _log_event("mk_no_sid")
        return 0
    if _mode(data) != MODE_REPO:
        _log_event("mk_off_scope", sid)
        return 0
    try:
        state, anchor = _marker_state(sid)
    except Exception:
        _log_event("mk_error_open", sid)
        return 0
    if state != "armed":
        _log_event("mk_allow", sid)
        return 0
    if not anchor or anchor == "-":
        # Recorded blind -> a deny cannot be proven. Open.
        _log_event("mk_allow_noanchor", sid)
        return 0
    cur = ""
    tp = data.get("transcript_path") or ""
    if isinstance(tp, str) and tp and os.path.isfile(tp):
        try:
            cur = _last_genuine_uuid(_tail_lines(tp))
        except Exception:
            cur = ""
    if not cur:
        _log_event("mk_allow_noanchor", sid)
        return 0
    if cur != anchor:
        # A newer genuine prompt exists —— a dead reset path
        # must never deny past its own turn.
        _log_event("mk_allow_newturn", sid, anchor=cur)
        return 0
    try:
        sys.stderr.write(_DENY_MSG)
    except Exception:
        pass
    _log_event("mk_deny", sid, anchor=anchor)
    return 2


def _stage_marker_post(data):
    """PostToolUse recorder —— arms the guard once a marker EXISTS."""
    sid = str(data.get("session_id") or "")[:8]
    if _is_subagent(data):
        _log_event("mk_subagent", sid or "-")
        return 0
    if data.get("tool_name") != _MARKER_TOOL:
        _log_event("mk_off_tool", sid or "-",
                   detail=str(data.get("tool_name"))[:40])
        return 0
    if not sid:
        _log_event("mk_no_sid")
        return 0
    if _mode(data) != MODE_REPO:
        _log_event("mk_off_scope", sid)
        return 0
    resp = data.get("tool_response")
    if isinstance(resp, dict) and (resp.get("is_error") is True
                                   or resp.get("isError") is True):
        # A failed call made no marker; a retry stays legal.
        _log_event("mk_error_resp", sid)
        return 0
    anchor = "-"
    tp = data.get("transcript_path") or ""
    if isinstance(tp, str) and tp and os.path.isfile(tp):
        try:
            anchor = _last_genuine_uuid(_tail_lines(tp)) or "-"
        except Exception:
            anchor = "-"
    _log_event("marker_recorded", sid, anchor=anchor)
    return 0


def _stage_prompt(data):
    """UserPromptSubmit reset —— the GENUINE-prompt path only. A Stop-block
    continuation fires no UserPromptSubmit (so the guard stays armed across
    it), and a `<task-notification>` wake is ignored here."""
    sid = str(data.get("session_id") or "")[:8]
    if _is_subagent(data):
        _log_event("p_subagent", sid or "-")
        return 0
    if not sid:
        _log_event("p_no_sid")
        return 0
    if _mode(data) != MODE_REPO:
        _log_event("p_off_scope", sid)
        return 0
    prompt = data.get("prompt")
    if (isinstance(prompt, str)
            and prompt.lstrip().startswith(_SYSTEM_INJECTED_TAGS)):
        _log_event("p_wake_ignored", sid)
        return 0
    _log_event("prompt_reset", sid)
    return 0


# ---------------------------------------------------------------------------
# HOOK-BODY STDIN GUARD —— the sibling lints' shared convention: refuse a
# hand invocation fast, on stderr, exit 3 (never 2 —— a hand run must not be
# able to block a tool call). See hlint.py for the full rationale.
# ---------------------------------------------------------------------------
_HOOK_STDIN_WAIT_S = 2.0
_HOOK_FILEY_EXTS = frozenset((".md", ".py", ".sh", ".json", ".jsonl", ".txt",
                              ".html", ".yml", ".yaml", ".csv"))
_HOOK_STDIN_HOWTO = (
    '  printf \'%s\' \'{"hook_event_name":"PostToolBatch",'
    '"session_id":"s1","transcript_path":"/tmp/t.jsonl"}\' \\\n'
    '    | python3 cscpt/blint.py batch\n'
)


def _argv_names_a_file(arg):
    """True when an argument hands over a file —— no hook event does."""
    return ("/" in arg or "\\" in arg
            or os.path.splitext(arg)[1].lower() in _HOOK_FILEY_EXTS)


def _hook_stdin_is_pipe():
    """True for the pipe/socket a harness hands a hook body; unknowable
    shapes count as a pipe so an odd environment fails towards armed."""
    try:
        mode = os.fstat(sys.stdin.fileno()).st_mode
        return stat.S_ISFIFO(mode) or stat.S_ISSOCK(mode)
    except Exception:
        return True


def _hook_refusal(reason):
    """Refuse loudly, exit 3 —— a silent success here is the false pass the
    guard exists to prevent."""
    sys.stderr.write(
        "%s is a hook body, not a command-line tool. It reads its JSON hook\n"
        "payload on stdin and ignores its arguments, so NOTHING WAS CHECKED ——\n"
        "do not read this silence as a pass.\n"
        "Cause: %s.\n"
        "Run it by hand from the repo root with:\n%s\n"
        % (os.path.basename(__file__), reason, _HOOK_STDIN_HOWTO))
    sys.exit(3)


def _require_hook_payload(argv=()):
    """Return only if a real hook payload arrived; else explain and exit 3.
    On success stdin is re-seated so main() reads what the harness sent."""
    stray = [a for a in argv if _argv_names_a_file(a)]
    if stray:
        _hook_refusal(
            "argv names the file %r, and no hook event ever passes one —— the "
            "payload arrives on stdin, never on the command line" % stray[0])
    try:
        if sys.stdin is None:
            _hook_refusal("this process has no stdin at all "
                          "(descriptor 0 closed)")
        if sys.stdin.isatty():
            _hook_refusal("stdin is a terminal, so no payload can ever arrive")
        piped = _hook_stdin_is_pipe()
        ready = select.select([sys.stdin], [], [], _HOOK_STDIN_WAIT_S)[0]
    except Exception:
        return                       # never disarm on an odd stdin
    if not ready:
        _hook_refusal("nothing reached stdin within %gs" % _HOOK_STDIN_WAIT_S)
    try:
        raw = sys.stdin.read()
    except Exception:
        return                       # never disarm on an odd stdin
    if not raw.strip() and not piped:
        _hook_refusal(
            "stdin delivered nothing and is not a pipe —— `/dev/null`, a "
            "closed descriptor or a plain file, which is what a shell hands "
            "a command run by hand. An EMPTY PIPE is left alone on purpose: "
            "that is the harness sending nothing, and every lint here fails "
            "open on it")
    sys.stdin = io.StringIO(raw)


_STAGES = {
    "batch": _stage_batch,
    "marker-pre": _stage_marker_pre,
    "marker-post": _stage_marker_post,
    "prompt": _stage_prompt,
}


def main():
    argv = sys.argv[1:]
    _require_hook_payload(argv)
    try:
        data = json.load(sys.stdin)
    except Exception:
        _log_event("no_stdin")
        return 0
    if not isinstance(data, dict):
        _log_event("no_stdin")
        return 0
    stage = argv[0] if argv else ""
    fn = _STAGES.get(stage)
    if fn is None:
        # Unknown stage word: a mis-registration must be visible
        # in the log, and must never block anything.
        _log_event("bad_stage", detail=stage or "-")
        return 0
    try:
        return fn(data)
    except Exception:
        # Any internal error degrades to silence/allow —— a lint
        # must never break a turn on its own failure.
        _log_event("error_open", str(data.get("session_id") or "")[:8] or "-",
                   detail=stage)
        return 0


if __name__ == "__main__":
    sys.exit(main())
