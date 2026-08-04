#!/usr/bin/env python3
"""Stop hook —— BLOCKS one turn-end when an `#m2` sequence stopped dead at its
INTERIM declaration and its `#sprint` never ran.

Root scope: THIS repo only (`dupbus-ceztuc-7cufVe`), anchored on this file's own
`__file__` and never on the process cwd. `#m2` is defined by `universal/m2.md`,
which exists in no other repo, so the sibling `AJAP_repo` and the parent Reader
folder (`GitHub/`) are deliberately out of scope —— neither has an m2 protocol to
breach, and a hook that can BLOCK must not police a repo that never agreed to
the rule (`cp/ccsim/hook_guide.md` § Global Reach & Self-Scoping).

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: a Stop hook. It blocks ONE turn-end when this turn invoked `#m2`, ended
  on the interim declaration, and shows no sign the `#sprint` ever started.
* IF IT FIRES: do NOT re-emit the declaration. Run m2 step 3 now —— `#sprint` the
  instructed actions, update this query's `response_`, then declare the real TEA3.
* FALSE ALARM: reply with a lone `.` and nothing else. It never fires twice for
  the same prompt, and the word `override` in the prompt disarms it outright.
* Verdicts log to `cscpt/.mlint.log`, one line per invocation.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===

THE DEFECT THIS EXISTS FOR, stated once and precisely. `universal/m2.md` orders:
(1) write a `response_` of initial thoughts; (2) commit + push + declare THAT
FILE ALONE in chat; (3) `#sprint` the real work; (4) update the `response_`;
(5) declare again as the real TEA3. Step 2's declaration is explicitly NOT a
TEA3 and m2.md says so in as many words —— yet agents repeatedly emitted it as
the last content of a message and stopped there, across at least three separate
sessions, each costing the owner a manual `continue`.

WHY PROSE COULD NOT FIX IT: a message whose final content is chat text ENDS the
assistant's turn. That is harness behaviour, not a choice —— an agent that emits
the interim declaration last has its turn ended FOR it, having disobeyed
nothing it could see. Root `CLAUDE.md` §3.1.7.5 ("absolutely nothing follows
TEA3's batch") trains that exact shape as "turn over" everywhere ELSE in the
protocol, so m2's one narrow exception loses to the far stronger general
pattern. m2.md once carried the countermeasure ("emit that declaration in the
SAME message as your next tool call"); it was trimmed out on 202608012123 and
the stalls continued. It is now restored —— and this hook is the half that does
not depend on anybody recalling it (`cp/ccsim/CLAUDE.md` §8.1, §8.7).

WHY THIS BLOCKS, WHEN clint DELIBERATELY DOES NOT (read before touching the
exit code). `clint.py` was demoted from blocking to warn-only because its
blocks forced an extra model turn in which the agent had NOTHING NEW TO DO ——
its content had already reached the `response_` file —— so it filled the turn
with repeated declaration batches and invented chapter markers, making the
outcome worse than the breach. THAT deadlock cannot arise here, and the
difference is structural, not a hopeful assertion:
* clint's forced turn was EMPTY by construction. mlint's forced turn is the
  ENTIRE MISSING SPRINT —— the extra turn is not overhead, it IS the work the
  user would otherwise have had to request by hand.
* clint blocked on a breach that had already happened and could not be undone.
  mlint blocks on work NOT YET DONE, which is exactly the kind a continuation
  can discharge.
* clint fired on any turn with stray chat text —— common. mlint fires only when
  four independent conditions coincide (below), so an ordinary turn never sees
  it at all.
* The stderr text names the ONE next action in one sentence, AND names the
  escape hatch (a lone `.`) for the case where the block is wrong. clint's
  message could name no action at all.
The residual risk is honestly stated: a WRONG block still costs one turn with
nothing to do, which is the clint failure in miniature. That is why the message
names the lone-`.` escape (root `CLAUDE.md` §3.1.8.2's sanctioned no-op reply,
which `clint.py` recognises as CLEAN in both modes) and why every detection
signal below is biased towards NOT firing.

THE FOUR CONDITIONS —— all must hold, and every one fails OPEN:
1. M2 EVIDENCE —— the turn was an `#m2` turn (see M2 EVIDENCE below).
2. NO SPRINT EVIDENCE —— nothing in the turn says a sprint began (see SPRINT
   EVIDENCE).
3. DECLARATION END —— the turn's LAST non-blank chat line is an I/O declaration
   (`✅`/`⇠`/`➡️`, root §3.2.1–3), i.e. the observed failure shape. A turn ending
   on a `⚠️` blocker (§3.2.4), the `🚨` sentinel (§3.2.5), a lone `.`, plain
   prose, a harness-authored API-error line, or nothing at all is left alone ——
   those are other situations, and one of them (the blocker) is a legitimate,
   urgent early stop that must never be held open.
4. NOT ALREADY FIRED —— see LOOP GUARD.
Plus: `override` in the typed message disarms everything, matching the house
exemption in `clint.py`.

M2 EVIDENCE, and why it is this narrow. Two sources, OR'd:
(a) the TYPED user message, and (b) any `[prefix_]query_[TS].md` file the turn
opened by `file_path`, read from disk. In both, `#m2` counts only when it
starts a line (leading whitespace allowed) and is NOT inside a backtick span or
a fenced block. Mined from every real occurrence in this repo's `sessions/`:
8 genuine invocations, all at column 1, most as the file's last line, some with
a trailing modifier (`#m2 expect 2`, `#m2 (ensure you re-read it…)`); 4
DISCUSSIONS of `#m2`, every one inline and backticked. The line-start test and
the backtick test each rule out all 4 discussions independently, so they are
belt and braces rather than one clever rule. The quoting logic mirrors
`hlint.py`'s (fences masked first, then inline spans, so a stray backtick
cannot pair across a fence); it is duplicated rather than imported because a
hook must stay self-contained and importable-from-nowhere.
* Why the typed message alone is not enough: the real incident's typed message
  was the bare filename `career_query_202608041846.md` —— the `#m2` lived in the
  file. Root §3.6 makes that the NORMAL case, so (b) is load-bearing.
* Why the file is read from DISK rather than from the tool_result: a Read
  result is line-numbered and truncatable, so `^#m2` would need a fragile
  prefix-stripping hack; the absolute path is right there in `tool_input` and
  the file is a few KB. A missing/unreadable file simply yields no evidence.
* Why not "the turn read `universal/m2.md`", which looks like the obvious
  signal: every CCSIM session that MAINTAINS m2.md reads it too, so that test
  fires on the sessions least able to tolerate it. (m2.md itself contains no
  line-start `#m2`, so it is inert under the rule above even if opened.)
* KNOWN MISS: a `query_` file opened via `cat`/`grep` in Bash rather than the
  Read tool carries no `file_path`, so it is invisible here. Root protocol uses
  Read; this is a fail-open gap, not a silent one —— the log says `no_m2`.

SPRINT EVIDENCE —— any ONE of these means the sprint began, so no block:
(a) a `[prefix_]slog_[TS].md` touched by `file_path` —— `universal/sprint.md`
    makes the slog a MANDATORY pair with every sprint, so this is the strongest
    signal and the one that survives a long session;
(b) `universal/sprint.md` opened by `file_path` —— root §7.3.1's mandated read
    on `#sprint`. Weaker than it looks: a `#trigger` file is read ONCE per
    session, so a second `#m2` later in the same session shows no re-read. It
    can only ever cause a missed block, never a wrong one, so it stays;
(c) an `Agent`/`Task` dispatch —— m2 step 3's stated vehicle ("use SA(s) if
    apt"). ⚠️ `TaskUpdate` is a TODO-list tool, NOT a dispatch, and appears all
    over ordinary turns —— matching it would disarm this hook almost everywhere.
    The match is therefore an EXACT tool-name set, never a prefix.
Verified against the real incident: its window held Bash/Read/Write only —— no
slog, no sprint.md, no Agent —— whilst the legitimate post-sprint turn from the
same session held an `Agent` dispatch AND a `career_slog_202608042032.md` edit.

TURN WINDOW: records after the LAST genuine user message, the same boundary
`clint.py` uses, with the same `_is_real_user` exclusions (tool_result-only
turns, and the wrappers Claude Code injects as `type:"user"` with no human
behind them). Sub-agent lines (`isSidechain`) are dropped —— an SA's own reads
are not the main turn's evidence.
* Consequence, accepted: a mid-turn user message (root §3.1.7.6.1 says the turn
  has not ended) MOVES the boundary, so the m2 evidence falls outside the window
  and nothing fires. Same for the harness's own
  "[Your previous response had no visible output…]" nudge, observed live in the
  incident session. Both fail OPEN, which is the direction that costs a missed
  block rather than a wrong one.
* That same property is a third loop guard for free: the harness injects its
  "Stop hook feedback:" as a user message, so after a block the window resets
  and the m2 evidence is no longer in it.

LOOP GUARD, three independent layers, because an unguarded blocking Stop hook
retries forever:
1. `stop_hook_active` in the payload —— true once the agent is already
   continuing from a prior Stop block. Documented in
   `cp/ccsim/hook_guide.md` §5.5.
2. A per-prompt ledger read back out of this hook's OWN log: a previous
   `action=block` line carrying the same `pid=` means this prompt has had its
   one turn and must never be blocked again. The prompt id comes from the
   transcript's last main-agent `user` line, which STAYS CONSTANT across a
   block-forced continuation and changes on every new genuine user message ——
   precisely the key this needs.
3. The window reset described above.
ORDER IS LOAD-BEARING: the ledger line is written BEFORE the block is issued,
and if that write fails the hook exits 0 (`block_unlogged`) rather than
blocking. A block whose record did not land is a block that could repeat, and
repeating is the one failure mode worse than missing.

FAIL OPEN, ALWAYS, AND NEVER SILENTLY: every stage that cannot read its
evidence exits 0 and logs the stage it died at (`no_stdin`, `out_of_scope`,
`no_transcript`, `unreadable_transcript`, `oversize_transcript`,
`empty_transcript`, `no_boundary`, `no_m2`, `sprint_ran`,
`not_declaration_end`, `exempt:override`, `loop_guard`, `already_blocked`,
`block_unlogged`, `block`). A breach-only log cannot tell "ran and found
nothing" from "the harness never called this command" —— that ambiguity is
exactly how dead hook wiring survived unnoticed here for weeks, so EVERY
invocation writes a line (`hook_guide.md` §7.7).

TRANSCRIPT SIZE: the file is read whole up to `_MAX_TRANSCRIPT_BYTES`; past
that only the trailing window is read, newline-aligned, because one turn is
never more than a few thousand records. `hook_guide.md` §12.7 measures clint at
`~`165 ms on the largest transcript on disk (53 MB) reading unbounded; this cap
keeps mlint flat instead. Stop hooks run in PARALLEL (§12.3), so a hook no
slower than the incumbent worst adds ZERO to the event —— mlint does strictly
less work than clint on the same file.

LOG FORMAT: one tab-delimited line per invocation —— timestamp, `session=`,
`pid=`, `action=`, `m2=`, `sprint=`, `first=` (the turn's final chat line,
flattened and truncated; last because it alone carries free text). `MLINT_LOG=`
redirects it so a test neither reads nor pollutes the real log. It self-prunes
to a recent window (`_LOG_MAX_LINES` triggers, `_LOG_KEEP_LINES` survives) by
atomic rename, never truncation, AFTER the current line is on disk —— the same
mechanism and the same guarantees as `clint.py`'s, for the same reason: the log
answers only "did this run for that turn, and why", which is asked about the
current session or a very recent one.
"""

import sys
import os
import re
import json
from datetime import datetime

# --- Repo scope (see docstring Root scope) ---------------------------------
_REPO_ROOT_REAL = os.path.realpath(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_REPO_SLUG = re.sub(r"[/ ]", "-", _REPO_ROOT_REAL.rstrip("/"))
_SPRINT_MD_REAL = os.path.join(_REPO_ROOT_REAL, "universal", "sprint.md")

# --- Filename shapes (root CLAUDE.md §3.3; `[CP_]name_[TS].md`) ------------
_QUERY_FILE_RE = re.compile(r"^(?:[A-Za-z0-9-]+_)*query_\d{12}\.md$", re.I)
_SLOG_FILE_RE = re.compile(r"^(?:[A-Za-z0-9-]+_)*slog_\d{12}\.md$", re.I)

# --- `#m2` invocation shape (see docstring M2 EVIDENCE) --------------------
# Line-start only. `\b` after the token so `#m2x` never matches whilst
# `#m2 expect 2` and a bare `#m2` both do.
_M2_RE = re.compile(r"^[ \t]*#m2\b", re.I | re.M)
_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_BACKTICK_RE = re.compile(r"`[^`\n]*`")

# --- Declaration glyphs (root CLAUDE.md §3.2) ------------------------------
_VS16 = "️"                       # emoji variation selector
_IO_GLYPHS = ("✅", "⇠", "➡")     # ✅ ⇠ ➡ —— §3.2.1–3

# `override` in the typed message disarms this hook, exactly as in `clint.py`.
_OVERRIDE_RE = re.compile(r"\boverrid(?:e|ing)\b", re.I)

# Wrappers Claude Code injects as `type:"user"` with no human behind them.
# Exact prefix match only, so human prose mentioning these words is unaffected.
_SYSTEM_INJECTED_TAGS = (
    "<task-notification>", "<local-command-caveat>",
    "<local-command-stdout>", "<command-name>", "<command-message>",
    "<command-args>")

# EXACT tool names that mean "a sub-agent was dispatched". `TaskUpdate` is a
# TODO tool and must NEVER be matched here —— see docstring SPRINT EVIDENCE.
_DISPATCH_TOOLS = frozenset(("Agent", "Task"))

# Safety caps. None is reached in normal use; each bounds a pathological input.
_MAX_TRANSCRIPT_BYTES = 8 * 1024 * 1024   # tail-read past this
_MAX_QUERY_FILES = 5                      # query files opened per invocation
_MAX_QUERY_BYTES = 256 * 1024             # bytes read from any one of them
_LEDGER_TAIL_LINES = 400                  # log lines scanned for a prior block

_LOG = os.environ.get("MLINT_LOG") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".mlint.log")
_LOG_MAX_LINES = 1000
_LOG_KEEP_LINES = 800
_LOG_MIN_BYTES_PER_LINE = 60
_LOG_PRUNE_AT_BYTES = _LOG_MAX_LINES * _LOG_MIN_BYTES_PER_LINE

# The ONE message that reaches the model (exit 2, stderr —— the only Stop
# channel that does; `hook_guide.md` §6). It names the next action, forbids the
# re-declaration that wrecked clint's blocking era, and gives an explicit out
# for a wrong verdict.
_BLOCK_MSG = (
    "[mlint] `#m2` INCOMPLETE —— this turn invoked `#m2` and ended on the "
    "INTERIM declaration, but nothing shows the `#sprint` ever started (no "
    "`universal/sprint.md` read, no `slog_` written, no SA dispatched). That "
    "declaration is NOT TEA3 and the turn does not end there.\n"
    "CONTINUE NOW with m2 step 3: run the `#sprint`, update this query's "
    "`response_`, then declare the real TEA3 —— emitting each interim "
    "declaration in the SAME message as your next tool call.\n"
    "Do NOT simply re-emit the declaration batch. If a sprint is genuinely "
    "not owed here, reply with a lone `.` and nothing else. This fires at "
    "most once per prompt.")


def _in_scope(data):
    """True if this Stop belongs to THIS repo. Signals in order: the payload's
    `cwd`, else the `~/.claude/projects/<slug>/` transcript slug —— both compared
    against values derived from this file's own location, never a hard-coded
    path. FAILS OPEN (True) when neither is usable: an unreadable payload is
    not evidence of a different project (`hook_guide.md` §4.4), and the m2
    evidence gate downstream is itself a second de-facto scope guard —— a
    line-start `#m2` beside a `query_[TS].md` file simply does not occur outside
    this repo. Never raises."""
    try:
        if not isinstance(data, dict):
            return True
        cwd = data.get("cwd")
        if isinstance(cwd, str) and cwd:
            real = os.path.realpath(cwd)
            return (real == _REPO_ROOT_REAL
                    or real.startswith(_REPO_ROOT_REAL + os.sep))
        tp = data.get("transcript_path")
        if isinstance(tp, str) and tp:
            m = re.search(r"/projects/([^/]+)/", tp)
            if m:
                slug = m.group(1)
                return slug == _REPO_SLUG or slug.startswith(_REPO_SLUG + "-")
        return True
    except Exception:
        return True


def _quoted_spans(text):
    """(start, end) spans where a `#m2` is being DISCUSSED, not invoked: inside
    a fenced block or an inline backtick span. Fenced spans are found FIRST on
    the untouched text so their coordinates are exact; the inline scan then runs
    over a copy with fence characters blanked (newlines kept, so `[^`\\n]` still
    behaves), which stops a backtick inside a fence pairing with one outside."""
    spans = [m.span() for m in _FENCE_RE.finditer(text)]
    if spans:
        chars = list(text)
        for start, end in spans:
            for i in range(start, end):
                if chars[i] != "\n":
                    chars[i] = " "
        masked = "".join(chars)
    else:
        masked = text
    spans.extend(m.span() for m in _INLINE_BACKTICK_RE.finditer(masked))
    return spans


def _invokes_m2(text):
    """True if `text` INVOKES `#m2`: the token starts a line and sits outside
    every quoted span. Never raises —— an unparseable blob yields False, which
    is the fail-open direction."""
    try:
        if not text or "#m2" not in text.lower():
            return False
        spans = _quoted_spans(text)
        for m in _M2_RE.finditer(text):
            pos = m.end() - 3            # the `#` of this `#m2`
            if not any(a <= pos < b for a, b in spans):
                return True
    except Exception:
        pass
    return False


def _is_real_user(obj):
    """A genuine user prompt: not a tool_result-only `user` turn, and not one of
    the system-injected wrappers Claude Code appends as `type:"user"`. Counting
    a wrapper as genuine would push the turn boundary PAST the real prompt and
    hide the evidence this hook needs."""
    if obj.get("type") != "user":
        return False
    content = (obj.get("message") or {}).get("content")
    if isinstance(content, str):
        return not content.lstrip().startswith(_SYSTEM_INJECTED_TAGS)
    if isinstance(content, list):
        return any(isinstance(b, dict) and b.get("type") != "tool_result"
                   for b in content)
    return False


def _message_text(obj):
    """All human-visible text of a message, both the plain-string and the
    block-list content shapes. Never raises."""
    try:
        content = (obj.get("message") or {}).get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(
                b.get("text") for b in content
                if isinstance(b, dict) and b.get("type") == "text"
                and isinstance(b.get("text"), str))
    except Exception:
        pass
    return ""


def _tool_uses(obj):
    """Yield (tool_name, input_dict) for every tool_use block in an assistant
    message. Never raises."""
    try:
        if obj.get("type") != "assistant":
            return
        content = (obj.get("message") or {}).get("content")
        if not isinstance(content, list):
            return
        for b in content:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                yield b.get("name"), (b.get("input") or {})
    except Exception:
        return


def _last_chat_line(window):
    """The turn's FINAL non-blank chat line, or "". Harness-authored assistant
    lines (`isApiErrorMessage`, e.g. "You've hit your session limit") are
    skipped —— they are written by the CLI, not the model, and judging the model
    on them would be wrong precisely when it is least able to act."""
    last = ""
    for o in window:
        try:
            if o.get("type") != "assistant" or o.get("isApiErrorMessage") is True:
                continue
            if (o.get("message") or {}).get("role") != "assistant":
                continue
            for ln in _message_text(o).splitlines():
                s = ln.strip()
                if s:
                    last = s
        except Exception:
            continue
    return last


def _is_io_declaration(line):
    """True if `line` is an I/O declaration (root §3.2.1–3), tolerating the
    `**…**` bold wrapper §3.1.6 puts round one and the emoji variation
    selector. Only the GLYPH is tested, not the file-list shape: `clint.py`
    already owns declaration shape, and a malformed declaration is still the
    turn-ending-on-a-declare situation this hook is looking for."""
    t = line.strip()
    if t.startswith("**"):
        t = t[2:].strip()
    return t.replace(_VS16, "").startswith(_IO_GLYPHS)


def _read_query_text(path):
    """Contents of a `query_` file named in the turn, or "" if unreadable.
    Bounded by `_MAX_QUERY_BYTES`; any failure is silent and simply yields no
    evidence (fail open)."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read(_MAX_QUERY_BYTES)
    except Exception:
        return ""


def _prune_log():
    """Bound `_LOG` to its recent window, cheaply and atomically. Runs AFTER the
    current line is appended, so that line can never be a casualty of its own
    prune. One `os.stat` on almost every invocation; the file is read only when
    it could exceed the high-water mark and rewritten only when it does, so the
    1000/800 hysteresis amortises the rewrite over ~200 invocations. The tail is
    written to a pid-suffixed sibling and moved in with `os.replace` (one atomic
    POSIX rename), so a crash leaves either the untouched original or the
    complete replacement —— never a half or empty file. Every failure is
    swallowed: pruning is housekeeping, and raising from here would break a
    turn, which this file's contract forbids."""
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
            fh.flush()
            os.fsync(fh.fileno())
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


def _log_event(sid, action, pid="-", m2="-", sprint="-", first="-"):
    """Append ONE diagnostic line for ANY invocation, verdict or not. Returns
    True only if the line reached disk —— the block path DEPENDS on that return
    value, because an unrecorded block is a block that can repeat (see docstring
    LOOP GUARD). Every other caller ignores it: a lost diagnostic costs
    visibility, never enforcement."""
    ok = False
    try:
        with open(_LOG, "a", encoding="utf-8") as lf:
            lf.write(
                "%s\tsession=%s\tpid=%s\taction=%s\tm2=%s\tsprint=%s\tfirst=%s\n"
                % (datetime.now().isoformat(timespec="seconds"), sid, pid,
                   action, m2, sprint,
                   str(first)[:200].replace("\t", " ").replace("\n", " ")))
        ok = True
    except Exception:
        pass
    _prune_log()
    return ok


def _already_blocked(pid):
    """True if this hook has ALREADY blocked for this prompt id —— layer 2 of the
    loop guard, read back out of this hook's own log. Scans only the tail, which
    is bounded anyway by `_prune_log`. UNREADABLE LOG -> True (treated as
    already blocked), the deliberately conservative direction: without a ledger
    nothing can prove a block would be the first, and repeating one is worse
    than missing one."""
    if not pid or pid == "-":
        return True
    try:
        if not os.path.isfile(_LOG):
            return False
        with open(_LOG, "r", encoding="utf-8", errors="replace") as fh:
            tail = fh.read().splitlines()[-_LEDGER_TAIL_LINES:]
    except Exception:
        return True
    needle_pid = "\tpid=%s\t" % pid
    return any("\taction=block\t" in ln and needle_pid in ln for ln in tail)


def _load_records(path):
    """Main-agent transcript records, newest-bounded. Reads the file whole up to
    `_MAX_TRANSCRIPT_BYTES`, else only the trailing window, newline-aligned so
    no record is half-parsed (one turn is never remotely that large). Sub-agent
    lines are dropped —— an SA's reads are not the main turn's evidence. Raises
    only on an unreadable file, which the caller turns into a fail-open exit."""
    size = os.path.getsize(path)
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        if size > _MAX_TRANSCRIPT_BYTES:
            fh.seek(size - _MAX_TRANSCRIPT_BYTES)
            fh.readline()                # discard the partial first record
        raw_lines = fh.read().splitlines()
    objs = []
    for raw in raw_lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            o = json.loads(raw)
        except Exception:
            continue
        if isinstance(o, dict) and o.get("isSidechain") is not True:
            objs.append(o)
    return objs


def _turn_id(data, objs):
    """The prompt id this Stop belongs to —— the ledger key. Prefer the
    transcript's last main-agent `user` line's `promptId`: it stays CONSTANT
    across a block-forced continuation and changes on every new genuine user
    message, which is exactly the identity a once-per-prompt guard needs. Falls
    back to the payload's own field. Ids containing whitespace are rejected
    rather than sanitised, so a stray tab can never split a log field and
    desync the record shape. Never raises."""
    def _clean(p):
        return isinstance(p, str) and p and not any(c.isspace() for c in p)
    try:
        for o in reversed(objs):
            if isinstance(o, dict) and o.get("type") == "user":
                p = o.get("promptId")
                if _clean(p):
                    return p
        for key in ("prompt_id", "promptId"):
            p = data.get(key)
            if _clean(p):
                return p
    except Exception:
        pass
    return ""


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        _log_event("unknown", "no_stdin")
        return 0
    if not isinstance(data, dict):
        _log_event("unknown", "no_stdin")
        return 0

    sid = str(data.get("session_id") or "")[:8] or "unknown"

    if not _in_scope(data):
        _log_event(sid, "out_of_scope")
        return 0

    # Loop guard 1 —— the harness says we are already inside a forced
    # continuation, so this Stop is downstream of a block, not a fresh turn end.
    if data.get("stop_hook_active"):
        _log_event(sid, "loop_guard")
        return 0

    tp = data.get("transcript_path") or ""
    if not tp or not os.path.isfile(tp):
        _log_event(sid, "no_transcript")
        return 0
    try:
        objs = _load_records(tp)
    except Exception:
        _log_event(sid, "unreadable_transcript")
        return 0
    if not objs:
        _log_event(sid, "empty_transcript")
        return 0

    pid = _turn_id(data, objs) or "-"

    # Turn window: everything after the LAST genuine user message.
    start = None
    trigger = None
    for i, o in enumerate(objs):
        if _is_real_user(o):
            start = i + 1
            trigger = o
    if start is None:
        # No genuine prompt in what we read —— a tail-read that fell short, or a
        # transcript shape we do not recognise. Nothing can be judged.
        _log_event(sid, "no_boundary", pid=pid)
        return 0
    window = objs[start:]

    typed = _message_text(trigger)
    if _OVERRIDE_RE.search(typed):
        _log_event(sid, "exempt:override", pid=pid)
        return 0

    # --- Gather evidence in ONE pass over the window -----------------------
    query_paths = []
    sprint_why = ""
    for o in window:
        for name, inp in _tool_uses(o):
            if name in _DISPATCH_TOOLS and not sprint_why:
                sprint_why = "agent"
            fp = inp.get("file_path")
            if not isinstance(fp, str) or not fp:
                continue
            base = os.path.basename(fp)
            if _SLOG_FILE_RE.match(base):
                sprint_why = "slog"          # strongest —— always wins
            elif not sprint_why and os.path.realpath(fp) == _SPRINT_MD_REAL:
                sprint_why = "sprint_md"
            elif _QUERY_FILE_RE.match(base) and fp not in query_paths:
                if len(query_paths) < _MAX_QUERY_FILES:
                    query_paths.append(fp)

    m2_why = "typed" if _invokes_m2(typed) else ""
    if not m2_why:
        for path in query_paths:
            if _invokes_m2(_read_query_text(path)):
                m2_why = "query"
                break

    last_line = _last_chat_line(window)

    if not m2_why:
        _log_event(sid, "no_m2", pid=pid, sprint=sprint_why or "-")
        return 0
    if sprint_why:
        _log_event(sid, "sprint_ran", pid=pid, m2=m2_why, sprint=sprint_why)
        return 0
    if not _is_io_declaration(last_line):
        # Ended on a blocker/sentinel/prose/lone-dot/nothing —— a different
        # situation, and one of those is a legitimate urgent stop.
        _log_event(sid, "not_declaration_end", pid=pid, m2=m2_why,
                   first=last_line)
        return 0

    # Loop guard 2 —— once per prompt, read back out of this hook's own log.
    if _already_blocked(pid):
        _log_event(sid, "already_blocked", pid=pid, m2=m2_why, first=last_line)
        return 0

    # ORDER IS LOAD-BEARING: record the block BEFORE issuing it. If the ledger
    # write fails there is no guard, so do not block at all.
    if not _log_event(sid, "block", pid=pid, m2=m2_why, sprint="none",
                      first=last_line):
        _log_event(sid, "block_unlogged", pid=pid, m2=m2_why, first=last_line)
        return 0

    # Exit 2 + STDERR is the ONLY Stop channel that reaches the model and
    # blocks the stop (`hook_guide.md` §6). At exit 2 the harness ignores
    # stdout entirely, so nothing may be written there.
    sys.stderr.write(_BLOCK_MSG)
    return 2


if __name__ == "__main__":
    sys.exit(main())
