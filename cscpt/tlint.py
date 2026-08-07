#!/usr/bin/env python3
"""PreToolUse + PostToolUse hook —— "time-integrity linter". ONE lint owning the
question root CLAUDE.md §2.1.7 answers by mandate: is the time CC is using a
REAL Sydney clock reading, or something recalled, guessed, or taken from a
US-formatted source? Four checks, all ADVISORY, all about the same defect.

Root scope: resolves paths in TWO repo roots —— `dupbus-ceztuc-7cufVe/sessions/`
and `AJAP_repo/inv/` —— because those two hold ONE comms stream stamped in one
timezone. No other repo is walked: nothing else on this Mac stamps files
`[prefix]_[TS].md`. The dupbus root comes from this file's own `__file__` and
the AJAP root from the written path itself, never from the process cwd —— a
user-level hook routinely runs from another repo. CHECK A resolves no path at
all and is deliberately global (see REACH below).

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: the time-integrity lint (root §2.1.7/§2.2.2). ADVISORY ONLY, never
  blocks. Stage log: `cscpt/.tlint.log`.
* IT WARNS when a Bash call reads the clock without `TZ='Australia/Sydney'`.
  Re-issue with that prefix.
* IT WARNS when you create a comms file whose NEW timestamp sits 6 h+ from real
  Sydney time, or when nothing this session ever read the clock. Re-stamp from
  a real `date` call.
* IT WARNS on a US-format date (`August 5, 2026`, `08/25/2026`) in text you just
  wrote —— §2.2.2 wants `at HH:mm on DD/MM/YYYY`, 24-hour.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WIRING (kept here, not in NON-CCSIM: nobody invokes this by hand, so the
plumbing serves only an editor). Run by the harness via `tlint_hook.sh`, the
registered bash fast-path, from TWO registrations in the USER-level
`~/.claude/settings.json` —— the Claude Desktop app executes user-level hooks
and silently ignores project-level ones:
  * PreToolUse  (Bash),                 argument `pre`   -> CHECK A
  * PostToolUse (Edit|Write|MultiEdit), argument `post`  -> CHECKS B, C, D
MODE SELECTION is argv-first with a `hook_event_name` fallback, the house
pattern (`flint.py`). Argv is authoritative; the payload fallback covers the
minutes-long window in which a settings edit has not gone live yet
(`hook_guide.md` §7.9). The fallback default is POST, because a pre payload
misread as post finds no `tool_input.file_path` worth judging and exits, whilst
a post payload misread as pre finds no `command` and exits —— neither direction
can produce a wrong verdict here, since nothing blocks.

WHAT A HOOK CAN AND CANNOT OBSERVE, stated first because it bounds everything
below. A hook sees TOOL PAYLOADS and the session transcript; it CANNOT see the
model's reasoning. "CC guessed the time" is therefore not directly observable.
Three things ARE:
  1. The COMMAND —— `tool_input.command` on a PreToolUse Bash payload names the
     exact clock call, so a malformed one is caught BEFORE it returns a wrong
     answer. This is the only check that reaches the defect at its source.
  2. The ANSWER —— this hook runs on the same Mac and can read the real Sydney
     clock itself, so a freshly-minted timestamp can be checked against ground
     truth. It never has to INFER whether CC read the clock; it can ask whether
     the result is right. That is strictly stronger than the correlation the
     brief proposed, and it is why CHECK B is the load-bearing one.
  3. The HISTORY —— past Bash commands live in the transcript
     (`transcript_path`, every payload), so "no clock read happened in this
     session at all" is answerable. That is CHECK C, and it is the only one
     that catches a guess which happened to land close enough for B to miss.

CHECK A —— CLOCK-CALL FORM (PreToolUse, Bash). Fires when a command invokes
`date` in COMMAND POSITION without `TZ=Australia/Sydney` in that invocation's
own env prefix. Command position, not "the word date anywhere", is load-bearing:
measured over 4630 real Bash calls from this repo's transcripts, a bare-word
match flags 431 commands of which 12 are prose ("stale date refs", "context type
+ date"); the command-position match flags 704 of which 701 carry the TZ. Of the
3 remaining, all are the SAME command, whose `date -v-80M` computes a relative
mtime for a `touch -t` fixture rather than reading the clock for a timestamp.
Invocations carrying an EXPLICIT input date (`-d`, `--date`, `-j`, `-r`, `-f`)
are excluded outright —— they parse a GIVEN time, so no timezone slip is
possible; one such call exists historically (`date -j -f "%Y-%m-%d" ...` deriving
a weekday). Net measured fire rate on that corpus: 1 in 4630 calls.

CHECK B —— MINT DRIFT (PostToolUse). Fires when a `Write` creates a file in a
comms tree whose basename carries a 12-digit TS, that TS has NO same-TS sibling
already on disk, and it sits `_DRIFT_LIMIT_MIN` from the real Sydney clock.

  WHY "Write + no same-TS sibling" IS THE MINT TEST, and why the obvious
  alternatives were rejected. Only a NEWLY MINTED timestamp is suspect; a
  citation of a historical one is not, and a `close_` listing a dozen of them
  must never fire. Filename-only (never body text) disposes of the citation
  problem entirely. The sibling exemption disposes of the biggest legitimate
  class: root §3.5.3 says a `response_` copies its `query_`'s TS and §3.3.5 says
  an `artefact_` copies its `close_`'s, so those are DERIVED, not minted, and
  the derivation's source is sitting in the same folder to prove it.

  CALIBRATED AGAINST GROUND TRUTH, not estimate: 4760 session transcripts were
  replayed, taking each write tool call's own record timestamp as the real
  moment of writing, and comparing it with the TS in the filename. 3270 write
  calls carried a TS; 1385 of those landed in a comms tree via `Write`. Split by
  the sibling test:
    * 878 WITH a same-TS sibling —— median drift 5 min but max 7589 min (a
      `response_` legitimately written five days after its `query_`). Exempting
      these is what makes the check usable at all.
    * 507 WITHOUT one, i.e. the fire set —— median 1 min, p90 5 min, p99 34 min,
      MAX 352 min, that maximum being a single deliverable email draft.
  `Edit`/`MultiEdit` are excluded for the same reason: their equivalent bucket
  runs to a max of 8594 min, because an edit revisits a file minted long ago.
  So `_DRIFT_LIMIT_MIN = 360` scores ZERO false positives across every mint this
  repo has ever made, whilst every timezone a slip could plausibly land in is
  further out than that: UTC is 600 min from AEST, UK 540, US Eastern 840, US
  Pacific 1020, and any wrong-DAY guess is 1440.
  ⚠️ KNOWN GAP, and it is real: a slip to a NEARBY zone (Singapore/HK +8, Tokyo
  +9) is 60-120 min out and this check cannot see it. Narrowing the threshold to
  reach them would start firing on the p99 of legitimate mints. CHECK C covers
  that gap only when the clock was never read at all; otherwise the miss stands.

CHECK C —— UNCLOCKED MINT (PostToolUse). Same trigger as B, plus: the session
transcript contains NO command-position `date` invocation anywhere. This is the
correlation the brief asked about, and it IS buildable —— measured on the same
4760 transcripts, 506 of 507 mints had a clock read earlier in their own
session, and the single exception drifted only 7 min. One fire in 507 is a
usable signal, and it is the ONLY check that catches a guess that happened to
land inside B's threshold.
  SUB-AGENT PAYLOADS SKIP THIS CHECK, deliberately. `hook_guide.md` §5.6.2: an
  SA's payload hands over the MAIN session `transcript_path` whilst its own
  records live in `<session>/subagents/agent-<id>.jsonl`. An SA that ran `date`
  itself would therefore look unclocked. `agent_id`/`agent_type` is the only
  reliable discriminator (§5.6.1). B and D still run for an SA —— neither reads
  the transcript.

CHECK D —— US DATE FORMAT (PostToolUse). Purely textual, over the text THIS
write produced (`content` for Write, `new_string` for Edit, the concatenated
`new_string`s for MultiEdit), `.md` only. Two shapes, both unambiguous:
month-name-first (`August 5, 2026`) and numeric `MM/DD/YYYY` whose second field
exceeds 12 (`08/25/2026`), which no DD/MM reading can explain. Fenced blocks,
inline code spans and `>` blockquote lines are masked first —— that is not
decoration: all 8 historical month-first hits in the live repo sit inside a
fence in ONE `ccsim_query_`, being a verbatim paste of Claude's own device list.
Masked, the live repo (1270 `.md`, backups and archives excluded) scores ZERO.

  ⛔ WHAT THIS CHECK DELIBERATELY DOES NOT DO, and the refusal is the finding:
  root §2.2.2 also bans the 12-hour clock, and an AM/PM regex is trivial to
  write. It is NOT here because it was measured first: `9am deadline`, `3pm
  interview`, `12-1pm` and the like score 356 hits across 113 `.md` in this
  repo, essentially all of them legitimate. §2.2.2 governs DELIVERABLES, and
  every one of those hits is internal comms prose, which the rule does not
  reach. A PostToolUse hook cannot tell a deliverable from a `close_`, so the
  check belongs in `dlint.py`'s FULL-mode set (`run_checks`, the `if not quick`
  branch), which runs on deliverables and nothing else. Shipping it here would
  have made this lint fire ~356 times on files it has no business judging, and
  a lint that cries wolf gets uninstalled.

WHY NOTHING BLOCKS. A wrong timestamp is recoverable —— a `git mv` renames the
file and an edit fixes the text —— whereas the two blocking positions available
here are both expensive: CHECK A would sit on PreToolUse-Bash, this repo's
busiest event and already home to `alint`'s commit gate, and CHECK B would have
to block a comms write over a filename smell that only a human can adjudicate
(the same reasoning that keeps `flint`'s TS-clash check warn-only). At
PreToolUse an exit-0 `additionalContext` already reaches the MODEL, so CC can
re-issue the call unaided; the enforcement gained by escalating to exit 2 is
small and the blast radius is not. ⛔ No future edit may teach any check here to
return 2 without re-running the calibrations above.

REACH (`hook_guide.md` §4.7: a lint that can BLOCK must be repo-scoped, one that
can only advise may be global). NOTHING here blocks, so there is no `_in_scope`
guard and no call site for one. The scoping that matters is STRUCTURAL and
per-check: B and C only fire on a path inside one of the two comms trees, so a
foreign repo cannot reach them however it is invoked. A and D are genuinely
global, on purpose —— root §2.1.7's Sydney mandate is a USER-level convention,
not a repo-level one, and both repos measured here obey it. ⛔ Do not "tidy" a
cwd guard onto this file: it would delete AJAP coverage whilst every unit test
still passed.

CHANNELS: every advisory is an exit-0 `hookSpecificOutput.additionalContext`,
the one channel on either event that is BOTH non-blocking and model-visible
(`hook_guide.md` §6.5). The model is the audience on purpose —— it is the party
that must re-issue the call or re-stamp the file. Nothing is written to stderr,
because at exit 0 stderr reaches the user alone and none of these findings is
his to act on.

ONE ADVISORY PER INVOCATION, ALWAYS. The harness JSON-parses the WHOLE of
stdout, so two `json.dump` calls make it unparseable and BOTH findings vanish
silently —— a write carrying a US date AND a bad timestamp would report neither.
`_post` therefore accumulates findings and `_advise` emits once. ⛔ Nothing may
call `_advise` twice in one run.

LOGGING, per `hook_guide.md` §7.7: EVERY invocation appends one line to
`cscpt/.tlint.log`, tagged by the stage(s) reached, `+`-joined when a write
trips more than one —— `no_stdin`, `no_command`, `clock_ok`, `clock_warn`,
`no_path`, `not_comms`, `has_sibling`, `no_tz_db`, `mint_ok:<n>min`,
`drift:<n>min`, `unclocked`, `subagent_skip`, `us_date`, `clean`, `error`. A
breach-only log cannot tell "never fired" from "fired and found nothing", which
is exactly how dead wiring survived for weeks (§2). `TLINT_LOG=<path>` redirects
it, which is how the regression suite reads verdicts without touching the real
log.

FAIL-OPEN, per `hook_guide.md` §4.4: any unreadable payload, missing key, absent
tz database or unparseable transcript yields a silent exit 0 rather than a
guess. The `isinstance(data, dict)` checks are not decorative —— valid JSON that
is not an object would make `.get` raise, and a user-level registration means
any project's payload can arrive here.
"""

import json
import os
import re
import sys
import io
import select
import stat
from datetime import datetime, timedelta

try:
    from zoneinfo import ZoneInfo
except Exception:                                    # pragma: no cover
    ZoneInfo = None

# Repo anchor. Derived from this file's own location, never hard-coded, so the
# repo stays relocatable (hook_guide.md §4.5.1).
_REPO_ROOT_REAL = os.path.realpath(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

_LOG = os.environ.get("TLINT_LOG") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".tlint.log")
_LOG_MAX_LINES = 1000
_LOG_KEEP_LINES = 800

# Drift beyond which a freshly-minted TS is reported. 360 min = ZERO false
# positives across all 507 historical mints (max legitimate drift 352 min),
# whilst every plausible timezone slip is >=540 min. See CHECK B.
_DRIFT_LIMIT_MIN = 360

# Bound the transcript read, as `alint.py` does. A session file runs to a few
# MB; the largest on this Mac is 53 MB.
_MAX_TRANSCRIPT_BYTES = 64 * 1024 * 1024

# A 12-digit filename TS (YYYYMMDDHHmm) starting "20", not inside a longer digit
# run —— so a 13+-digit id never reads as a TS nor matches one by substring.
_TS_RE = re.compile(r"(?<!\d)(20\d{10})(?!\d)")

# --- CHECK A shapes --------------------------------------------------------
# A shell separator, or the very start of the command. `$(` and a backtick are
# included because a substitution opens a fresh command context.
_SEP = r"(?:^|[;&|(`\n]|\$\()"
# Zero or more `VAR=value` env assignments, quoted or bare, preceding the
# command word —— this is what makes `TZ='Australia/Sydney' date` one unit.
_ENV = (r"(?:\s*[A-Za-z_][A-Za-z0-9_]*="
        r"(?:\"[^\"]*\"|'[^']*'|[^\s;&|]*)\s+)*")
_DATE_CALL_RE = re.compile(
    _SEP + r"\s*" + _ENV + r"(?:/usr/bin/)?date(?![A-Za-z0-9_.-])")
# Flags that supply an EXPLICIT input time. Such a call parses a GIVEN moment,
# so no timezone slip of the CURRENT clock is possible.
_EXPLICIT_INPUT_RE = re.compile(r"^\s+(?:-d\b|--date\b|-j\b|-r\b|-f\b)")
_SYD_TZ_RE = re.compile(r"TZ=['\"]?Australia/Sydney['\"]?")

# --- CHECK D shapes --------------------------------------------------------
_MON = (r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t|tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?)")
# `August 5, 2026` / `Aug. 5th, 2026` —— month first, comma before the year.
# The comma is required: `5 August 2026` (correct) can never match.
_US_MONTH_RE = re.compile(
    r"\b" + _MON + r"\.?\s+\d{1,2}(?:st|nd|rd|th)?,\s*(?:19|20)\d{2}\b")
# `08/25/2026` —— second field >12, so no DD/MM reading exists. An ambiguous
# `08/05/2026` is NOT matched: it is a legitimate DD/MM date far more often
# than not, and flagging it would fire on correct output.
_US_NUM_RE = re.compile(
    r"(?<![\d/])(?:0?[1-9]|1[0-2])/(?:1[3-9]|2\d|3[01])/(?:19|20)\d{2}(?![\d/])")
_FENCE_RE = re.compile(r"```.*?```|~~~.*?~~~", re.S)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
_BLOCKQUOTE_RE = re.compile(r"^[ \t]*>.*$", re.M)

_WRITE_TOOLS = frozenset({"Write", "Edit", "MultiEdit"})


# ---------------------------------------------------------------------------
# Shared plumbing
# ---------------------------------------------------------------------------

def _mode(argv, data):
    """PRE or POST. Argv wins; `hook_event_name` is the fallback for the window
    in which a settings edit has not gone live (hook_guide.md §7.9). Default
    POST —— see MODE SELECTION in the docstring."""
    arg = argv[1].strip().lower() if (
        len(argv) > 1 and isinstance(argv[1], str)) else ""
    if arg in ("pre", "post"):
        return arg
    ev = data.get("hook_event_name") if isinstance(data, dict) else ""
    if isinstance(ev, str) and ev.strip().lower() == "pretooluse":
        return "pre"
    return "post"


def _prune_log():
    """Keep the stage log bounded. Best-effort: a logging failure must never
    change a verdict."""
    tmp = None
    try:
        if not os.path.isfile(_LOG):
            return
        with open(_LOG, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
        if len(lines) <= _LOG_MAX_LINES:
            return
        tmp = _LOG + ".tmp"
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


def _log(sid, action, note="-"):
    """One line per invocation, whatever the verdict (hook_guide.md §7.7).
    Never raises —— a lost diagnostic costs visibility, never a verdict."""
    try:
        with open(_LOG, "a", encoding="utf-8") as fh:
            fh.write("%s\tsession=%s\taction=%s\tnote=%s\n" % (
                datetime.now().isoformat(timespec="seconds"), sid, action,
                str(note)[:200].replace("\t", " ").replace("\n", " ")))
    except Exception:
        pass
    _prune_log()


def _advise(event, findings):
    """Emit on the ONE channel that is BOTH non-blocking and model-visible
    (hook_guide.md §6.5). `event` must match the firing event or the harness
    may discard it.

    ⚠️ EXACTLY ONE OBJECT REACHES STDOUT, whatever the number of findings. The
    harness JSON-parses the whole of stdout, so a second `json.dump` makes the
    stream `Extra data: line 2` and BOTH advisories are lost —— a lint that
    finds two defects would report neither, and silently. `_post` therefore
    collects findings and calls this once at the end; nothing may call it
    twice."""
    if not findings:
        return
    json.dump({
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": "\n\n".join(findings),
        }
    }, sys.stdout)
    sys.stdout.write("\n")


def _sid(data):
    return str(data.get("session_id") or "")[:8] or "unknown"


def _syd_now():
    """Real Sydney time, or None if the tz database is unavailable. Reading the
    clock in-process rather than shelling out keeps this free —— and this hook
    of all hooks must not model the defect it exists to catch."""
    if ZoneInfo is None:
        return None
    try:
        return datetime.now(ZoneInfo("Australia/Sydney"))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# CHECK A —— clock-call form (PreToolUse, Bash)
# ---------------------------------------------------------------------------

def _bad_clock_calls(command):
    """Every command-position `date` invocation in `command` that reads the
    CURRENT clock without `TZ=Australia/Sydney` on its own env prefix.

    Returns the matched invocation prefixes, so the advisory can quote what it
    objected to rather than the whole command line."""
    bad = []
    for m in _DATE_CALL_RE.finditer(command):
        if _EXPLICIT_INPUT_RE.match(command[m.end():m.end() + 12]):
            continue                       # parses a GIVEN date, not now
        if _SYD_TZ_RE.search(m.group(0)):
            continue                       # correctly prefixed
        bad.append(m.group(0).strip().lstrip(";&|(`").strip())
    return bad


def _pre(data):
    sid = _sid(data)
    if data.get("tool_name") != "Bash":
        _log(sid, "no_command", "tool=%s" % data.get("tool_name"))
        return 0
    ti = data.get("tool_input")
    cmd = ti.get("command") if isinstance(ti, dict) else None
    if not isinstance(cmd, str) or not cmd:
        _log(sid, "no_command")
        return 0

    bad = _bad_clock_calls(cmd)
    if not bad:
        _log(sid, "clock_ok")
        return 0

    _log(sid, "clock_warn", bad[0][:80])
    _advise("PreToolUse", [
        "[tlint] Clock read without a timezone: `" + bad[0][:120] + "`. Root "
        "CLAUDE.md §2.1.7 mandates Sydney time, obtained as "
        "`TZ='Australia/Sydney' date +\"%Y%m%d%H%M\"`. A bare `date` answers in "
        "whatever zone the machine happens to be set to, which is how a US or "
        "UTC time reaches a filename or a deliverable unnoticed. RE-ISSUE this "
        "call with the `TZ='Australia/Sydney'` prefix. (If this `date` is "
        "computing an offset rather than reading the clock, the prefix is still "
        "correct and costs nothing.)"
    ])
    return 0


# ---------------------------------------------------------------------------
# CHECK B/C/D —— the written artefact (PostToolUse)
# ---------------------------------------------------------------------------

def _target_path(data):
    """The path this tool call is about."""
    ti = data.get("tool_input")
    if not isinstance(ti, dict):
        return ""
    for key in ("file_path", "notebook_path"):
        v = ti.get(key)
        if isinstance(v, str) and v:
            return v
    return ""


def _written_text(data):
    """The text THIS write produced. `content` is Write's whole file;
    `new_string` is what an Edit introduced; MultiEdit's edits are concatenated.
    Judging only the new text is deliberate —— an Edit must not be blamed for a
    US date that was already in the file, and `dlint` scopes the same way."""
    ti = data.get("tool_input")
    if not isinstance(ti, dict):
        return ""
    parts = []
    for key in ("content", "new_string"):
        v = ti.get(key)
        if isinstance(v, str) and v:
            parts.append(v)
    edits = ti.get("edits")
    if isinstance(edits, list):
        for e in edits[:200]:
            if isinstance(e, dict) and isinstance(e.get("new_string"), str):
                parts.append(e["new_string"])
    return "\n".join(parts)


def _comms_tree(path):
    """True if `path` sits inside one of the two comms trees this repo stamps:
    dupbus `sessions/` (anchored on this file's own repo root) or AJAP `inv/`
    (matched structurally on the written path, since that repo is elsewhere).
    Anything else —— code, pcmds, sandbox fixtures, another project entirely ——
    is not stamped by root §3.3 and must never reach CHECK B or C."""
    try:
        ap = os.path.abspath(path)
        if ap.startswith(os.path.join(_REPO_ROOT_REAL, "sessions") + os.sep):
            return True
        return bool(re.search(r"/GitHub/AJAP_repo/inv/", ap))
    except Exception:
        return False


def _mask_quoted(text):
    """Blank out fenced blocks, inline code spans and `>` blockquote lines,
    preserving length so nothing shifts. These hold QUOTED material —— a pasted
    US device list, an American job ad —— which is not CC choosing a format.
    Measured: this is the difference between 8 historical hits and zero."""
    def blank(m):
        return "".join(" " if c != "\n" else "\n" for c in m.group(0))
    text = _FENCE_RE.sub(blank, text)
    text = _INLINE_CODE_RE.sub(blank, text)
    return _BLOCKQUOTE_RE.sub(blank, text)


def _has_same_ts_sibling(path, ts):
    """True if another file in the same folder already carries this exact TS ——
    the DERIVED case (root §3.5.3 `query_`->`response_`, §3.3.5
    `close_`->`artefact_`), which is not a mint and must never fire."""
    try:
        folder = os.path.dirname(os.path.abspath(path)) or "."
        base = os.path.basename(path)
        bounded = re.compile(r"(?<!\d)" + re.escape(ts) + r"(?!\d)")
        for entry in os.listdir(folder):
            if entry != base and bounded.search(entry):
                return True
    except Exception:
        pass
    return False


def _is_subagent(data):
    """`agent_id`/`agent_type` is the ONLY reliable sub-agent discriminator
    (hook_guide.md §5.6.1). Not the transcript path —— an SA's payload hands
    over the MAIN session transcript (§5.6.2), which is precisely why CHECK C
    cannot judge one."""
    return bool(data.get("agent_id") or data.get("agent_type"))


def _session_read_the_clock(transcript_path):
    """True if ANY command-position `date` invocation appears in this session's
    transcript. Returns None when the transcript cannot be read, so the caller
    can fail open rather than accuse.

    Parses tool_use inputs rather than grepping the raw text: root CLAUDE.md
    §2.1.7 QUOTES the command, so the literal string `Australia/Sydney` is in
    every transcript that ever read the protocol —— a substring search would
    report success in a session that never touched the clock. Cheap line
    pre-filter, and an early return on the first hit, because a compliant
    session reads the clock in its opening turns."""
    try:
        if not transcript_path or not os.path.isfile(transcript_path):
            return None
        if os.path.getsize(transcript_path) > _MAX_TRANSCRIPT_BYTES:
            return None
        with open(transcript_path, "r", encoding="utf-8",
                  errors="replace") as fh:
            for raw in fh:
                if '"Bash"' not in raw:
                    continue
                try:
                    o = json.loads(raw.strip())
                except Exception:
                    continue
                if not isinstance(o, dict) or o.get("type") != "assistant":
                    continue
                content = (o.get("message") or {}).get("content")
                if not isinstance(content, list):
                    continue
                for b in content:
                    if not (isinstance(b, dict) and b.get("type") == "tool_use"
                            and b.get("name") == "Bash"):
                        continue
                    cmd = (b.get("input") or {}).get("command")
                    if isinstance(cmd, str) and _DATE_CALL_RE.search(cmd):
                        return True
        return False
    except Exception:
        return None


def _post(data):
    """CHECKS D then B/C. Findings ACCUMULATE and are emitted by a single
    `_advise` at the end —— see the warning on that function: a second write to
    stdout loses every advisory, including the ones that were correct."""
    sid = _sid(data)
    fp = _target_path(data)
    tool = data.get("tool_name")
    tool = tool if isinstance(tool, str) else ""
    findings = []
    stages = []

    def done():
        _log(sid, "+".join(stages) if stages else "clean", fp[-60:])
        _advise("PostToolUse", findings)
        return 0

    # --- CHECK D —— US date format in the text this write produced. Runs on
    # ANY `.md` anywhere, first, because it is independent of the comms tree.
    if fp.lower().endswith(".md"):
        masked = _mask_quoted(_written_text(data))
        found = ([m.group(0) for m in _US_MONTH_RE.finditer(masked)]
                 + [m.group(0) for m in _US_NUM_RE.finditer(masked)])
        if found:
            stages.append("us_date")
            findings.append(
                "[tlint] US-format date in the text you just wrote to `" + fp
                + "`: " + ", ".join("`" + f + "`" for f in found[:4])
                + ". Root CLAUDE.md §2.2.2 sets `at HH:mm on DD/MM/YYYY`, "
                "24-hour, for any date a reader sees; month-first and "
                "`MM/DD/YYYY` are the American forms and read as the wrong day "
                "here. FIX THE TEXT, and check the date is right at all —— this "
                "shape usually means it came from a US-formatted source rather "
                "than from `TZ='Australia/Sydney' date`.")

    # --- CHECKS B/C —— only a Write, only into a comms tree, only a mint.
    if tool != "Write" or not fp:
        stages.append("no_path" if not fp else "not_comms")
        return done()
    if not _comms_tree(fp):
        stages.append("not_comms")
        return done()
    m = _TS_RE.search(os.path.basename(fp))
    if not m:
        stages.append("not_comms")
        return done()
    ts = m.group(1)
    if _has_same_ts_sibling(fp, ts):
        stages.append("has_sibling")        # DERIVED, not minted
        return done()

    # --- CHECK B —— drift against the real Sydney clock.
    now = _syd_now()
    if now is None:
        stages.append("no_tz_db")           # fail open, never guess
        return done()
    try:
        stamped = datetime.strptime(ts, "%Y%m%d%H%M").replace(tzinfo=now.tzinfo)
    except Exception:
        stages.append("not_comms")
        return done()
    drift = abs((now - stamped).total_seconds()) / 60.0
    if drift >= _DRIFT_LIMIT_MIN:
        stages.append("drift:%dmin" % int(drift))
        findings.append(
            "[tlint] Timestamp `" + ts + "` in `" + os.path.basename(fp)
            + "` is " + _human(drift) + " from the real Sydney clock (now "
            + now.strftime("%Y%m%d%H%M") + "), and no file beside it shares "
            "that timestamp, so it was minted here rather than copied from a "
            "`query_` or `close_`. Root CLAUDE.md §2.1.7: get it from "
            "`TZ='Australia/Sydney' date +\"%Y%m%d%H%M\"`, never from memory or "
            "another timezone. RUN THAT NOW, and if the stamp is wrong rename "
            "with `git mv` in a move-only commit "
            "(`universal/coding.md` § Git Discipline) and tell the user (`⚠️`). "
            "If the old stamp is deliberate, say so in the `response_`.")
        # CHECK C is not also reported: it is the WEAKER statement of the same
        # defect, and two notes about one timestamp is noise, not rigour.
        return done()

    # --- CHECK C —— a mint in a session that never read the clock.
    if _is_subagent(data):
        stages.append("subagent_skip")
        return done()
    clocked = _session_read_the_clock(data.get("transcript_path"))
    if clocked is None:
        stages.append("mint_ok:transcript_unreadable")   # fail open
        return done()
    if not clocked:
        stages.append("unclocked")
        findings.append(
            "[tlint] You just minted timestamp `" + ts + "` in `"
            + os.path.basename(fp) + "`, but nothing in this session ever ran "
            "`TZ='Australia/Sydney' date`. The stamp is close to the real time "
            "(within " + _human(drift) + "), so it may be right —— but nothing "
            "here shows it was READ rather than recalled, and root CLAUDE.md "
            "§2.1.7 asks for the command, not an estimate. RUN IT NOW and "
            "compare; re-stamp with `git mv` if it differs.")
        return done()

    stages.append("mint_ok:%dmin" % int(drift))
    return done()


def _human(minutes):
    """A drift figure a reader can judge at a glance."""
    m = int(round(minutes))
    if m < 90:
        return "%d min" % m
    td = timedelta(minutes=m)
    if td.days:
        return "%dd %dh" % (td.days, td.seconds // 3600)
    return "%.1f h" % (m / 60.0)


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
    '    | python3 cscpt/tlint.py post\n'
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
        _log("unknown", "no_stdin")
        return 0
    if not isinstance(data, dict):
        _log("unknown", "no_stdin")
        return 0
    try:
        if _mode(argv, data) == "pre":
            return _pre(data)
        return _post(data)
    except Exception as exc:                # FAIL-SAFE: never a traceback
        _log(_sid(data), "error", type(exc).__name__)
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
