#!/usr/bin/env python3
"""Stop hook —— enforces chat-text discipline when the MAIN agent ends a turn.

Two rules, picked by the session's working directory (see REPO SCOPE below):
* REPO mode (this repo) —— root CLAUDE.md §3.2: the only chat text permitted is
  the 5 declaration lines, and each of the 5 glyphs is OWNED by its own
  declaration type (see DECLARATION CONTRACTS); any other non-blank line is a
  breach. Four exemptions apply (`override`, `yn`, `sic`, `DATS`).
* READER mode (the parent `GitHub/` folder alone) —— that folder's own
  CLAUDE.md mandates ZERO chat text "NO MATTER WHAT", so there every non-blank
  line is a breach, declaration glyphs included, and only `override` applies.

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: a Stop hook scanning the main agent's chat text at turn end, BLOCKING
  any impermissible line.
* IF IT BLOCKS: one forced extra turn, terse reason on stderr. Recast or delete
  the prose, then end again. EVERY breach blocks.
* PERMITTED: blank lines; a `---`/`***`/`___` divider; each glyph ONLY in the
  declaration it owns —— the 3 I/O glyphs a backticked file list (notes in
  brackets/italics), the blocker glyph a real blocker in ≤5 words, the sentinel
  its exact protocol wording. Parent `GitHub/` Reader folder: blank lines ONLY.
* Silent elsewhere; verdicts log to `cscpt/.clint.log`.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WHY A HOOK, NOT TRUST: the discipline is silent to break and normally caught only
on a human re-read; a deterministic Stop-time scan surfaces the slip at once.

DECLARATION CONTRACTS (glyph ownership —— the core rule): a prefix check alone
was gameable. The agent could satisfy it by CHOOSING A PREFIX rather than by
telling the truth —— real observed abuse: `⚠️ Fleet running; awaiting reports.`,
a progress note wearing the blocker glyph, and `✅ **Hooks are now live** —— dlint
fired and blocked that edit. Reverting the probe…`, a paragraph wearing the
read-declaration glyph. So each of the 5 glyphs is now OWNED by the ONE
declaration type root CLAUDE.md §3.2 assigns it, and a line bearing a glyph must
satisfy THAT type's shape:
* `✅`/`⇠`/`➡️` (§3.2.1–3, I/O) —— a FILE LIST. Strip bracketed `(...)` notes and
  backticked `` `...` `` spans; whatever remains must be punctuation/separators
  only, and at least one backtick-span or bracket must have been present. So
  `` ✅ `a.md`, `b.py` ``, `` ➡️ **`x.md`** ``, `` ➡️ `x.md` (renamed) `` and
  `✅ *(none this turn)*` all pass, whilst an un-bracketed prose tail does not.
  Mined from this repo's own transcripts: the bracketed/italic annotation is the
  established real-world convention, so it is permitted deliberately —— the
  smuggling vector is the BARE prose tail, and that is what this blocks. An
  agent needing an annotation brackets it; nothing truthful is lost.
* `🚨` (§3.2.5) —— the post-compaction sentinel, EXACT wording only, taken
  verbatim from §3.2.5 (`_SENTINEL_CANON`). No bold wrapper, no paraphrase: the
  whole value of a sentinel is that it cannot be approximated, and any other
  text carrying it is by definition not that sentinel.
* `⚠️` (§3.2.4) —— a genuine BLOCKER, "stop & alert", capped three ways:
  `_WARN_MAX_WORDS` (§3.2.4's own ≤5w), `_WARN_MAX_HYPHENS`, `_WARN_MAX_CHARS`,
  tested in that order so the first limit breached is the one reported. The
  hyphen cap exists because words can be skewered together with hyphens to
  smuggle long prose past a WORD count; the character cap is the final safety
  net against the same class of evasion (any other joiner —— en dashes, slashes,
  underscores —— still grows the character count).
  `_WARN_MAX_CHARS = 68` is deliberately documented ONLY here, never in the
  NON-CCSIM block, never in any guide, and never in the stderr message. A limit
  an agent can SEE is a limit it will spend up to; 5 words should never come
  close to it, so it is contingency only and its value must stay invisible to
  stay effective. If you edit it, keep it out of every agent-readable surface.

⚠️ IS NOT A PROGRESS NOTE: the three caps above are all satisfied by
`⚠️ Fleet running; awaiting reports.` (4 words, 0 hyphens, well under the
character cap), so caps alone cannot close the loophole that motivated this
rule. Two further ownership tests run on a `⚠️` line:
(a) CROSS-TYPE —— if the line would satisfy the I/O file-list shape, or equals
    the sentinel body, it is another type's declaration wearing this glyph.
(b) PROGRESS TRAP —— `_PROGRESS_RE` (continuation/status vocabulary: running,
    awaiting, proceeding, dispatched, monitoring, done…) fires ONLY when
    `_BLOCKER_RE` (failure vocabulary: blocked, failed, cannot, denied,
    missing, unavailable, 404…) does not also match. Stated honestly: this is a
    targeted trap for the observed abuse class, NOT a proof of truthfulness —— a
    linter cannot verify a claim, only its form. It is a DENYLIST rescued by an
    allowlist, and deliberately that way round: wrongly blocking a genuine
    blocker delays an urgent alert, whereas a missed exotic phrasing leaks one
    note. Hence `⚠️ Cannot continue; auth denied.` passes (progress word
    "continue", but "cannot"/"denied" rescue it) whilst the fleet line does not.
    Bare negators (no/not/none/never) are excluded from the rescue list on
    purpose —— they are common enough to rescue almost any progress note.

DELIBERATE NON-GOAL: `✅` vs `⇠` (§3.2.1.2/§3.2.2.2 —— non-comms vs comms files)
is NOT discriminated, though a filename regex could. Ownership as specified is
glyph-vs-TYPE, and all three I/O glyphs share one type-shape; splitting them on
a naming heuristic would let one mis-detected filename block a truthful
declaration, which costs more than it catches.

SCAN BOUNDARY: keep MAIN-agent lines only (`isSidechain` falsy) so a sub-agent's
prose never counts against the main turn, then scan every assistant text block
after the last GENUINE user line. `_is_real_user` excludes tool_result-only turns
AND the wrappers Claude Code appends as `type:"user"` with no human behind them
(`_SYSTEM_INJECTED_TAGS` —— task notifications, local-command echoes; exact
prefix match, so human prose merely mentioning those words is unaffected):
counting one as genuine would push the boundary PAST real prose from the current
exchange and hide the breach.

HARNESS-AUTHORED ASSISTANT TEXT: lines flagged `isApiErrorMessage: true` are
written by the CLI, not the model —— e.g. "You've hit your session limit ·
resets 11:40am". They are skipped, because blocking on one punishes the model
for text it never emitted, and does so precisely when it is least able to
comply (out of quota, or mid API failure). Live-verified: that flag is present
on such lines and absent from genuine assistant messages, in this repo's own
transcripts as well as the Reader's.

ALWAYS RED: a Stop hook's exit-0 output (`systemMessage` included) reaches only
the USER, never the model —— the turn has already ended —— so a non-blocking
warning can NEVER make the agent self-correct. The one channel reaching the
MODEL on Stop is a block: exit 2 feeds stderr back as an error and forces one
more turn. A log-only tier is therefore worthless as a corrective, and every
breach blocks. The cost is understood and accepted: a block ends that model
turn before its chapter marker is written, which is the intended loudness.

EXEMPTIONS. All read the USER'S TYPED MESSAGE —— the last GENUINE user line
(`_is_real_user`, which already excludes tool_results and the system-injected
wrappers), never a `query_` file's contents: this script opens no file but the
transcript, so an override token sitting inside a comms file can never arm one
of these. `override` applies in BOTH modes; the other three are REPO mode only,
because they come from THIS repo's protocols, which the Reader folder does not
share, and the Reader's own rule admits no exception:
* `override`/`overriding` —— the user explicitly suspending a rule for one turn
  (root §8.6.1 uses the same word for the same purpose). Disarms this lint
  ENTIRELY for that turn, in READER mode too: the folder protocol outranks the
  agent, but not the human who wrote it, and a user typing `override` and still
  being blocked would read as a bug rather than as discipline.
* `sic` —— `universal/glossary.md`: a status-report-in-chat override, "respond
  w/ 10w only in chat", modifier `sic [n]w` changing that cap. Matched as a
  WHOLE WORD (`\bsic\b`), NOT on a leading space, because it legitimately opens
  a message ("sic 8w as i saw you …"); the word boundary is what stops `music`
  or `sicker` matching. The cap is measured over the OFFENDING lines only, not
  all chat text —— a turn may owe its normal declaration batch AND the sanctioned
  status line, and counting the declarations would blow any cap and make the
  exemption unusable. Over-cap is NOT exempt and still blocks, logged distinctly
  (`block:sic_overrun`) so an over-long "answer" is auditable rather than
  indistinguishable from ordinary prose.
* `yn` —— when the triggering user message contains the literal ` yn` (leading
  space included), the user has invoked the project override meaning "answer in
  one word in chat", so chat text is AUTHORISED and the whole turn is exempt.
  Plain substring, deliberately: the leading space is what stops `Brooklyn` or
  `synergy` matching, and requiring it at the END would be wrong —— a real
  prompt reads "Was your last turn fully completed? yn" followed by two more
  lines of instructions. The token only ever appears in a typed message.
* `DATS` —— the session-closing protocol (`universal/close.md`) mandates one
  chat line after the close files are declared, in exactly one of two forms:
  "DATS done. Fixed [no.] file(s)." or "DATS incomplete. [≤8w_comment]." Hence
  the exemption is deliberately tight: the offending text must be a SINGLE line
  starting with `DATS` and at most 10 words —— 10 being the longest sanctioned
  form (2 fixed words + an 8-word comment). A second line, or an 11th word, is
  no longer that protocol line and is NOT exempt.
Tested in order `override` → `yn` → `sic` → `DATS`, widest authorisation first,
so the log names the STRONGEST reason a turn was let through; where several
apply the turn was authorised outright anyway.

LOOP GUARD: exit 2 forces a continuation that ends in another Stop, so an
unguarded block would loop forever. Two INDEPENDENT signals of the same fact
("we are already inside a block-forced continuation"), either sufficient alone:
(a) `stop_hook_active` in the payload, set by the harness; (b) the scan
boundary itself being the harness's own injected feedback line —— live-verified
as a `type:"user"`, `isMeta:true` line whose content starts with "Stop hook
feedback:". Signal (b) needs no payload field and no successful log write,
which is why the old promptId ledger (read back from this script's own log) was
deleted rather than kept: a lost log write silently disarmed it, and it also
capped enforcement at one block per prompt, which is exactly the ceiling this
rewrite removes. A blocked continuation that itself emits prose is therefore
logged (`loop_guard`) and never blocked again.

Precisely how far that guarantee reaches, stated honestly rather than
optimistically: (b) is absent in exactly two shapes —— no feedback line was
injected at all, in which case no continuation was forced and there is no loop
to run; or a LATER `type:"user"` line displaced the feedback line as the scan
boundary. Only the second is a live risk, and it is why (a) is kept: the
payload flag does not depend on transcript shape. A spiral thus needs BOTH to
fail at once —— the harness omitting `stop_hook_active` AND appending an
unrecognised user-wrapper after every block —— a combination never observed
here. Should it ever appear, the repair is one line: add that wrapper's tag to
`_SYSTEM_INJECTED_TAGS`, which restores (b) at once. A sticky per-prompt flag
is deliberately NOT added as a third guard —— that IS the ledger, ceiling and
all, which the owner ruled out.

GLYPH-FREE STDERR: neither breach message names any of the 5 glyphs. Naming them
would teach exactly which prefixes pass and invite gaming by bolting a glyph
onto prose. For the same reason the message carries NO numeric limit and NO
breach class: it says what is owed, never how close the last attempt came. The
precise class is recorded in the log, which the model does not read.

LOG EVERY STAGE: a breach-only log cannot tell "ran this turn and found
nothing" apart from "the harness never invoked this command" —— an empty log fits
BOTH, which is exactly how dead Stop-hook wiring went unnoticed across many real
sessions whilst the script itself was provably correct under manual invocation.
Leakage stays minimal: a breach line logs only the offending text, every other
stage logs no user content at all. The logged text may itself carry a glyph in
EITHER mode —— in READER mode a declaration line is the breach, and under glyph
ownership a REPO breach is often a MISUSED glyph (this was untrue of the older
prefix-only check, which could only ever log glyph-free lines). That is fine:
the log is read by a human, and it is the stderr message reaching the MODEL
that stays glyph-free.

REPO SCOPE (`_mode`): user-level registration reaches every project and this
lint BLOCKS, so it must not police repos that never agreed to either rule.
Signals, in order: the payload's `cwd` (confirmed present on a live PostToolUse
payload, NOT yet on a real Stop payload —— so the fallback is a live safety net,
not theory), else the `~/.claude/projects/<slug>/<uuid>.jsonl` transcript slug
(the project dir with every `/` and ` ` replaced by `-`). Both compare against
values derived from this script's OWN location, never a hard-coded path, so the
repo stays relocatable; symlinks are resolved. REPO is tested FIRST and matches
sub-paths; READER requires EXACT equality with the parent folder and never a
sub-path —— otherwise this repo (and every sibling repo under `GitHub/`, which
has its own rules) would wrongly inherit the zero-text rule. It FAILS OPEN to
REPO mode when neither signal is usable: an unreadable payload is not evidence
of a different project, and a lint that goes dark on ambiguity is the failure
this whole wiring exists to fix.

READER MODE (known limitation): the Reader folder's CLAUDE.md applies only when
that folder is the session's SOLE working directory, but no Stop-payload or
transcript field exposes additionally-added directories, so the check can only
approximate it with an exact `cwd` match. A session rooted at `GitHub/` that
ALSO added another repo would be held to the zero-text rule it no longer owes.
Accepted because that project slug has, in practice, only ever hosted the
Reader; delete the two READER branches to revert to repo-only policing.

WIRING (kept here, not in NON-CCSIM: a caller never invokes this file, so the
plumbing is dead weight to everyone but an editor). Registered as a `Stop` hook
in the USER-level `~/.claude/settings.json` —— the Claude Desktop app executes
user-level hooks and silently ignores project-level ones —— hence it fires in
every project and must self-scope. IN: Stop-hook JSON on stdin
(`transcript_path`, `cwd`, `session_id`, `stop_hook_active`); OUT: nothing at
all on a clean turn. EXIT 0 = clean, exempt, out-of-scope, loop-guarded, or ANY
failure; EXIT 2 = breach. FAIL-SAFE: a bad payload, an unreadable transcript or
a failed stderr/log write all exit 0, so the hook can never break a turn on its
own failure.

LOG FORMAT: exactly ONE tab-delimited line per invocation whatever the verdict,
each carrying `mode=` (which rule applied) and `pid=` (the prompt it belongs
to), so one `grep` shows every invocation for a prompt and why it was judged so.
Actions: `clean`; `out_of_scope`; `loop_guard`; `block_failed`; the parse stage
reached; one `exempt:` per exemption (`exempt:override`, `exempt:yn`,
`exempt:sic`, `exempt:dats`); and one `block:` per breach CLASS —— `block:prose`
(no glyph at all), `block:io_shape` (an I/O glyph not carrying a file list),
`block:sentinel` (compaction glyph, wrong wording), `block:warn_shape`
(blocker glyph carrying another type's declaration), `block:warn_empty`,
`block:warn_words`, `block:warn_hyphens`, `block:warn_chars`,
`block:warn_progress` (a progress note wearing the blocker glyph),
`block:reader` (any chat text in Reader mode), plus `block:sic_overrun` (a `sic`
answer past its cap). The class is that of the FIRST offending line, matching
the `first=` field, so record and class always describe the same text. A log
that does NOT grow
across real turns means the harness is not calling this hook at all —— the
diagnostic the LOG EVERY STAGE rationale above exists to enable.
`CLINT_LOG=<path>` redirects it, so a test run neither reads nor pollutes the
real log.

LOG RETENTION: one line per invocation, forever, is unbounded growth in a file
nobody deletes —— and the log's ONE question ("did this hook run for that turn,
and why was it judged so?") is only ever asked about the current session or a
very recent one, so old lines carry no value at all. It therefore SELF-PRUNES
to a recent window: `_LOG_MAX_LINES` triggers, `_LOG_KEEP_LINES` survives, the
newest lines always being the ones kept. Sizing is measured, not guessed ——
the real log ran ~90 bytes per line and ~105 lines per day at the heaviest
observed usage, so retaining 800 lines is over a week of THAT (and far longer
at ordinary rates) inside ~70 KB. The gap between the two marks is deliberate
hysteresis: it bounds the rewrite to at most one invocation in 200, so the
common turn pays a single `os.stat` and nothing else. Mechanics and their
guarantees (atomic rename, never truncate in place, order versus the append,
fail-safety, the concurrency caveat) are in `_prune_log`'s own docstring, where
an editor changing that code will actually be looking. The growth diagnostic
above survives untouched: a pruned log still gains a line every turn, and its
LAST line is always the newest. Nothing else is written anywhere, bar the
short-lived `.tmp.<pid>` sibling a prune renames into place.
"""

import sys
import os
import re
import json
from datetime import datetime

# ---------------------------------------------------------------------------
# SCOPE GUARD —— user-level registration fires in EVERY project on this Mac, so
# self-scope and exit silently elsewhere. Signals, in order: the payload's
# `cwd`, else the `~/.claude/projects/<slug>/` transcript slug —— both compared
# against values derived from this file's OWN location, never a hard-coded
# path. FAILS OPEN to REPO mode when neither is usable. Full rationale (why
# user-level, why fail-open, why READER is exact-match only) is in the CCSIM
# section of the module docstring above.
# ---------------------------------------------------------------------------
_REPO_ROOT_REAL = os.path.realpath(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_REPO_SLUG = re.sub(r"[/ ]", "-", _REPO_ROOT_REAL.rstrip("/"))

# The Reader folder = this repo's immediate parent (`.../GitHub`). Derived, not
# hard-coded, so the whole tree stays relocatable.
_READER_ROOT_REAL = os.path.dirname(_REPO_ROOT_REAL)
_READER_SLUG = re.sub(r"[/ ]", "-", _READER_ROOT_REAL.rstrip("/"))

MODE_REPO = "repo"       # root CLAUDE.md §3.2 —— declarations only
MODE_READER = "reader"   # GitHub/ CLAUDE.md —— absolutely no chat text
MODE_OFF = "off"         # some other project —— not ours to police


def _mode(data):
    """Which rule this invocation is under: MODE_REPO, MODE_READER or
    MODE_OFF. REPO is tested first and matches sub-paths; READER matches ONLY
    an exact parent-folder hit (see docstring REPO SCOPE). Never raises: any
    unexpected error must default to "run the repo lint", exactly like every
    other fail-safe path in this file."""
    try:
        if not isinstance(data, dict):
            return MODE_REPO
        cwd = data.get("cwd")
        if isinstance(cwd, str) and cwd:
            real_cwd = os.path.realpath(cwd)
            if (real_cwd == _REPO_ROOT_REAL
                    or real_cwd.startswith(_REPO_ROOT_REAL + os.sep)):
                return MODE_REPO
            if real_cwd == _READER_ROOT_REAL:   # EXACT only, never a sub-path
                return MODE_READER
            return MODE_OFF
        tp = data.get("transcript_path")
        if isinstance(tp, str) and tp:
            m = re.search(r"/projects/([^/]+)/", tp)
            if m:
                slug = m.group(1)
                if slug == _REPO_SLUG or slug.startswith(_REPO_SLUG + "-"):
                    return MODE_REPO
                if slug == _READER_SLUG:        # EXACT only, never a sub-path
                    return MODE_READER
                return MODE_OFF
            # transcript_path present but not the recognised
            # .../projects/<slug>/... shape -> unparseable -> fall through.
        return MODE_REPO  # neither field usable -> FAIL-OPEN
    except Exception:
        return MODE_REPO  # never let a scope-check error silence the lint


# Base glyph codepoints (variation selectors ignored, so `➡️` and `➡` both pass).
_GLYPHS = ("✅", "⇠", "➡", "⚠", "\U0001f6a8")  # ✅ ⇠ ➡ ⚠ 🚨
_VS16 = "️"                 # the emoji variation selector, stripped before matching

# Each glyph's OWNER declaration type (root CLAUDE.md §3.2; see docstring
# DECLARATION CONTRACTS). `_IO_GLYPHS` = the three I/O declarations §3.2.1–3,
# which share one shape: a list of backticked file paths.
_IO_GLYPHS = ("✅", "⇠", "➡")
_G_WARN = "⚠"                    # §3.2.4 blocker
_G_SENTINEL = "\U0001f6a8"       # §3.2.5 post-compaction sentinel

# §3.2.5's wording, copied VERBATIM from root CLAUDE.md —— a sentinel that may be
# paraphrased is not a sentinel. Compared against the whole stripped line.
_SENTINEL_CANON = "🚨 Compaction Detected —— stopped all tasks.".replace(_VS16, "")
_SENTINEL_BODY = _SENTINEL_CANON.split(" ", 1)[1]

# A markdown horizontal-rule / chapter divider line: 3+ of -, *, or _.
_HR_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")

# --- I/O declaration shape (§3.2.1–3) -------------------------------------
# A bracketed note `(...)`, applied repeatedly so a nested pair also clears.
_PAREN_RE = re.compile(r"\([^()]*\)")
# A backticked span —— the file path itself.
_TICKED_RE = re.compile(r"`[^`]*`")
# What may remain once notes and paths are removed: separators and emphasis
# markers only. Any surviving LETTER is an un-bracketed prose tail —— the exact
# vector by which a paragraph used to ride behind a declaration glyph.
_IO_RESIDUE_RE = re.compile(r"^[\s,;:.*_~×0-9+\-–—…]*$")

# --- Blocker declaration caps (§3.2.4) ------------------------------------
_WARN_MAX_WORDS = 5              # §3.2.4's own "≤5w"
_WARN_MAX_HYPHENS = 3            # hyphens can skewer words past a WORD count
# Final safety net against the same evasion. Its VALUE is documented in the
# CCSIM block only, never in NON-CCSIM, any guide, or the stderr message: a
# limit an agent can see is a limit it will spend up to.
_WARN_MAX_CHARS = 68

# Continuation/status vocabulary —— a progress note, not a blocker (word-boundary,
# case-insensitive). Fires only when no blocker word rescues the line.
_PROGRESS_RE = re.compile(
    r"\b(?:run|runs|running|ran|await|awaits|awaiting|wait|waits|waiting"
    r"|proceed\w*|continu\w*|ongoing|underway|in-?flight|progress\w*|start\w*"
    r"|dispatch\w*|monitor\w*|work|works|working|pending|queued|still|next"
    r"|standby|standing|checking|reading|writing|building|testing|verifying"
    r"|fleet|done|complet\w*|finish\w*|updating|updated|now)\b", re.I)

# Failure vocabulary —— evidence the line really is "blocker detected: stop &
# alert". Bare negators are excluded on purpose (see docstring).
_BLOCKER_RE = re.compile(
    r"\b(?:block\w*|stop\w*|halt\w*|abort\w*|stall\w*|fail\w*|error\w*"
    r"|crash\w*|broke|broken|cannot|can't|cant|unable|deni\w*|refus\w*"
    r"|reject\w*|forbidden|missing|absent|unavailable|offline|unreachable"
    r"|timeout|timed|expired|conflict\w*|clash\w*|mismatch\w*|corrupt\w*"
    r"|invalid|malformed|unknown|unrecognis\w*|unrecogniz\w*|ambiguous"
    r"|unclear|404|403|500|limit|limits|died|dead|risk\w*|unsafe|wrong"
    r"|incorrect|stale|desync\w*|lost|clobber\w*|overwrit\w*)\b", re.I)

# Fixed, GLYPH-FREE breach messages fed to the model via stderr on exit 2 (see
# docstring GLYPH-FREE STDERR —— must not name the glyphs, quote any numeric
# limit, or name the breach class, or it teaches how to game the check). Terse
# and terminal: tell the model to END the turn, not write more. One per mode,
# because "emit ONLY the 5 permitted declarations" would be actively wrong
# advice in a session that owes zero chat text.
_BREACH = {
    MODE_REPO: ("Chat-prose breach (root CLAUDE.md §3.2): each declaration "
                "glyph is reserved for its own declaration type —— emit ONLY "
                "correctly-formed declarations, never prose behind a glyph. "
                "Avoid further prose."),
    MODE_READER: ("Chat-text breach (GitHub/ CLAUDE.md): this session must "
                  "emit NO chat text at all. End the turn silently."),
}

# Known system-injected wrapper tags Claude Code appends as `type: "user"`
# turns (notifications/command echoes) even though no human typed them —
# see `_is_real_user`. Exact prefix match only, never substring, so real
# human prose that merely mentions these words is unaffected.
_SYSTEM_INJECTED_TAGS = (
    "<task-notification>", "<local-command-caveat>",
    "<local-command-stdout>", "<command-name>", "<command-message>",
    "<command-args>")

# The harness's own injected continuation line after a Stop hook blocks —— a
# `type:"user"`, `isMeta:true` line beginning with this exact prefix. Used as
# loop-guard signal (b); see docstring LOOP GUARD.
_STOP_FEEDBACK_PREFIX = "Stop hook feedback:"

# The `yn` override token (see docstring EXEMPTIONS). The leading space is
# load-bearing —— without it `Brooklyn` and `synergy` would match.
_YN_TOKEN = " yn"

# `override`/`overriding` in the typed message disarms this lint for the turn.
_OVERRIDE_RE = re.compile(r"\boverrid(?:e|ing)\b", re.I)

# `sic` (universal/glossary.md): status-report-in-chat override, default 10
# words, modifier `sic [n]w`. Whole-word match —— it may OPEN a message, so a
# leading space cannot be required; the word boundary alone stops `music`.
_SIC_RE = re.compile(r"\bsic\b", re.I)
_SIC_NW_RE = re.compile(r"\bsic\s+(\d{1,3})\s*w\b", re.I)
_SIC_DEFAULT_WORDS = 10

# Longest sanctioned `DATS` chat line: "DATS incomplete." + an 8-word comment.
_DATS_MAX_WORDS = 10

# Log path (overridable for tests via CLINT_LOG); default beside this script.
_LOG = os.environ.get("CLINT_LOG") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".clint.log")

# --- Log retention (see docstring LOG RETENTION) ---------------------------
# The log grows one line per invocation forever. It answers exactly one
# question —— "did this hook run for that turn, and why was it judged so?" ——
# which is only ever asked about the current session or a very recent one, so a
# RECENT WINDOW carries all of the value and the rest is dead weight.
_LOG_MAX_LINES = 1000            # high-water: prune only once this is passed
_LOG_KEEP_LINES = 800            # low-water: what survives a prune
# Conservative floor on one record's byte length. A record is at minimum an
# ISO timestamp (19) + the six `\tlabel=` skeletons and their shortest possible
# values + a newline, which is ~73 bytes; 60 sits safely below that. It must
# stay below the TRUE minimum, because the pre-gate uses it to prove a small
# file cannot hold too many lines —— an over-estimate would skip prunes and let
# the log grow unbounded again. Pinned by a regression test, not trusted.
_LOG_MIN_BYTES_PER_LINE = 60
_LOG_PRUNE_AT_BYTES = _LOG_MAX_LINES * _LOG_MIN_BYTES_PER_LINE


def _split_glyph(s):
    """Split a stripped line into (base glyph, remainder), tolerating the
    `**…**` bold wrapper §3.1.6 puts round a declaration and the emoji
    variation selector. Returns (None, s) when no glyph leads the line."""
    t = s
    if t.startswith("**"):               # tolerate `**➡️ …**` bold wrapper
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
    """True if `rest` is a well-formed I/O declaration body (§3.2.1–3): a list
    of backticked paths, optionally annotated in brackets/italics.

    Method: delete bracketed notes, then backticked paths; whatever survives
    must be separators and emphasis markers only. At least one backtick-span or
    bracket must have been present, so a bare glyph declares nothing and a bare
    number is not a file list. See docstring DECLARATION CONTRACTS for why the
    bracketed annotation is permitted whilst a bare prose tail is not."""
    if not rest:
        return False
    if not (_TICKED_RE.search(rest) or "(" in rest):
        return False
    body = rest
    for _ in range(8):                   # repeat for nested bracket pairs
        stripped = _PAREN_RE.sub(" ", body)
        if stripped == body:
            break
        body = stripped
    body = _TICKED_RE.sub(" ", body)
    if "`" in body:                      # unbalanced backtick -> not a clean list
        return False
    return bool(_IO_RESIDUE_RE.match(body))


def _warn_breach(rest):
    """Breach class for a `⚠️` line's body, or None if it is a permitted
    blocker declaration (§3.2.4). Caps are tested words -> hyphens -> chars so
    the FIRST limit breached is the one recorded."""
    if not rest:
        return "warn_empty"              # a glyph declaring nothing
    if _io_ok(rest) or rest == _SENTINEL_BODY:
        return "warn_shape"              # another type's declaration, wrong glyph
    if len(rest.split()) > _WARN_MAX_WORDS:
        return "warn_words"
    if rest.count("-") > _WARN_MAX_HYPHENS:
        return "warn_hyphens"
    if len(rest) > _WARN_MAX_CHARS:
        return "warn_chars"
    if _PROGRESS_RE.search(rest) and not _BLOCKER_RE.search(rest):
        return "warn_progress"           # a progress note wearing the glyph
    return None


def _line_breach(line, mode):
    """None if a single text line is permitted chat under `mode`, else a short
    breach-CLASS tag naming why (logged; never shown to the model).

    REPO mode enforces GLYPH OWNERSHIP: a glyph is permitted only in the ONE
    declaration type root CLAUDE.md §3.2 gives it, so prose cannot pass merely
    by wearing a prefix (docstring DECLARATION CONTRACTS).

    READER mode permits blank lines ONLY: a divider renders as a visible rule
    and a declaration glyph is still chat text, both of which that folder's
    CLAUDE.md forbids outright."""
    s = line.strip()
    if not s:
        return None                      # blank line —— renders as nothing
    if mode == MODE_READER:
        return "reader"                  # zero-text rule: everything else fails
    if _HR_RE.match(line):
        return None                      # markdown divider / chapter rule
    g, rest = _split_glyph(s)
    if g is None:
        return "prose"                   # no declaration glyph at all
    if g in _IO_GLYPHS:
        return None if _io_ok(rest) else "io_shape"
    if g == _G_SENTINEL:
        # EXACT §3.2.5 wording only, measured on the raw line: not even a bold
        # wrapper, because an approximable sentinel is worthless.
        return None if s.replace(_VS16, "") == _SENTINEL_CANON else "sentinel"
    return _warn_breach(rest)            # g == _G_WARN


def _text_of(content):
    """Yield the text of every text block in an assistant message `content`."""
    if isinstance(content, str):
        yield content
    elif isinstance(content, list):
        for blk in content:
            if isinstance(blk, dict) and blk.get("type") == "text":
                t = blk.get("text")
                if isinstance(t, str):
                    yield t


def _is_real_user(obj):
    """A genuine user prompt, not a tool_result-only `user` turn, and not a
    system-injected wrapper. Claude Code appends several notices as `type:
    "user"` turns with plain-string `message.content` even though no human
    typed them: background task-completion notifications
    (`<task-notification>...`) and local slash-command echoes
    (`<local-command-caveat>`, `<local-command-stdout>`, `<command-name>`,
    `<command-message>`, `<command-args>`). Treating those as genuine user
    turns would wrongly reset the scan boundary past real assistant prose
    from the current exchange, hiding it from the breach check —— so any
    string content beginning with one of these exact tag prefixes (after
    stripping leading whitespace) is excluded here.

    The harness's `Stop hook feedback:` line is deliberately NOT excluded: it
    genuinely opens a new turn, so it SHOULD move the boundary (a re-stop then
    reports fresh prose from the continuation, never the original breach
    twice). It is recognised separately by `_is_stop_feedback`."""
    if obj.get("type") != "user":
        return False
    content = (obj.get("message") or {}).get("content")
    if isinstance(content, str):
        return not content.lstrip().startswith(_SYSTEM_INJECTED_TAGS)
    if isinstance(content, list):
        # A tool_result-only turn is not a prompt; any non-tool_result => genuine.
        return any(isinstance(b, dict) and b.get("type") != "tool_result"
                   for b in content)
    return False


def _is_stop_feedback(obj):
    """True if `obj` is the harness's own post-block continuation line ——
    loop-guard signal (b), see docstring LOOP GUARD. Both conditions are
    required (`isMeta` true AND the exact text prefix) so no human message can
    impersonate it by quoting the phrase."""
    try:
        if not isinstance(obj, dict) or obj.get("isMeta") is not True:
            return False
        content = (obj.get("message") or {}).get("content")
        return (isinstance(content, str)
                and content.lstrip().startswith(_STOP_FEEDBACK_PREFIX))
    except Exception:
        return False


def _trigger_text(obj):
    """All human-visible text of the user message that opened this turn ——
    the `override`, `yn` and `sic` exemptions are keyed on it, and on it alone
    (never a `query_` file's contents: this script opens no file but the
    transcript). Handles both plain-string content and the block-list form (a
    prompt carrying attachments). Never raises."""
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
    """The `sic` word cap authorised by the typed message, or None if `sic`
    was not invoked: the glossary default, or the `sic [n]w` modifier's number
    when present. Never raises."""
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
    """True if the whole breach is the single `DATS` status line that
    `universal/close.md` mandates in chat (see docstring EXEMPTIONS). Exactly
    one line, starting with `DATS`, at most 10 words —— anything longer or
    multi-line is ordinary prose and stays a breach."""
    return (len(offending) == 1
            and offending[0].startswith("DATS")
            and len(offending[0].split()) <= _DATS_MAX_WORDS)


def _prune_log():
    """Bound `_LOG` to its recent window —— cheaply, atomically, fail-safely.

    ORDER IS LOAD-BEARING: this runs AFTER the current line has been appended
    and its handle closed. The line being written this invocation therefore
    cannot be a casualty of its own prune —— it is already on disk, and it is
    inside the tail that survives.

    CHEAP: one `os.stat` on the overwhelming majority of invocations. The file
    is READ only when it is large enough to possibly exceed the high-water
    mark, and REWRITTEN only when it actually does. The 1000/800 hysteresis is
    what makes that true: a prune can occur at most once per 200 invocations,
    so the rewrite is amortised across ~0.5% of turns instead of every turn.

    ATOMIC: the surviving tail is written to a sibling temp file and moved into
    place with `os.replace`, a single atomic rename on POSIX. The live log is
    NEVER truncated or rewritten in place, so a crash at any instant leaves
    either the untouched original or the complete replacement —— never a half
    file, never an empty one, never a wholesale loss. A crash between the write
    and the rename leaves one inert `.tmp.<pid>` sibling; the `finally` clears
    it on every non-crash path.

    FAIL-SAFE: every failure is swallowed, leaving the log exactly as it was.
    Pruning is housekeeping —— skipping it costs disk, whereas raising from here
    would break a turn, which this file's whole contract forbids. That is also
    why the write is guarded rather than the read: an unwritable directory
    (the shape a permissions slip takes) must degrade to "log keeps growing",
    not to "the hook fails".

    CONCURRENCY, stated honestly rather than optimistically: two invocations
    pruning in the same instant could read the same snapshot, and the later
    rename would then drop whatever the other appended in between. The
    pid-suffixed temp stops them corrupting each other's file; the hysteresis
    makes the overlap window vanishingly small; and the worst case is a handful
    of lost DIAGNOSTIC lines —— never corruption, and never enforcement, since
    nothing reads this log back."""
    tmp = None
    try:
        if os.stat(_LOG).st_size < _LOG_PRUNE_AT_BYTES:
            return                       # provably under the cap -> no read
        with open(_LOG, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
        if len(lines) <= _LOG_MAX_LINES:
            return                       # long lines, not too many -> leave it
        tmp = "%s.tmp.%d" % (_LOG, os.getpid())
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines[-_LOG_KEEP_LINES:]) + "\n")
            fh.flush()
            os.fsync(fh.fileno())        # rare enough to afford; makes the
            # rename swap in data that is really on disk, not just in cache
        os.replace(tmp, _LOG)
        tmp = None                       # ownership handed over; nothing to bin
    except Exception:
        pass
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except Exception:
                pass


def _log_event(sid, action, lines=0, first="-", pid="-", mode="-"):
    """Append ONE terse diagnostic line for ANY hook invocation, breach or not
    (see docstring LOG EVERY STAGE).

    Fields are TAB-separated and `first=` stays LAST because it alone may carry
    free text (tabs/newlines in it are flattened, so a record is always exactly
    one line). `mode=` records which rule applied, so a `reader:`-policed block
    is never mistaken for a repo one when auditing.

    FAIL-SAFE: swallow all errors -- a logging failure must never break a turn
    (same contract as the rest of this file). Nothing reads this log back, so a
    lost write costs diagnostics only, never enforcement."""
    try:
        with open(_LOG, "a", encoding="utf-8") as lf:
            lf.write(
                "%s\tsession=%s\tpid=%s\tmode=%s\taction=%s\tlines=%d\tfirst=%s\n"
                % (datetime.now().isoformat(timespec="seconds"),
                   sid, pid, mode, action, lines,
                   str(first)[:200].replace("\t", " ").replace("\n", " ")))
    except Exception:
        pass
    # AFTER the append, never before: the line just written must already be on
    # disk (and inside the surviving tail) before anything trims the file.
    # `_prune_log` never raises, so this cannot affect the verdict either way.
    _prune_log()


def _turn_id(data, objs):
    """The id of the user prompt this Stop belongs to —— logged as `pid=` so one
    grep gathers every invocation belonging to one prompt (purely diagnostic;
    nothing branches on it). Prefer the transcript's last main-agent `user`
    line's `promptId`, which stays constant across a block-forced continuation
    and changes on every new genuine user message; fall back to the payload's
    own prompt id for harnesses whose transcript lines lack the field. Returns
    "" when neither is readable. Never raises.

    Ids containing whitespace are REJECTED rather than sanitised, so a stray
    tab can never split one log field into two and desync the record shape."""
    def _clean(p):
        return isinstance(p, str) and p and not any(c.isspace() for c in p)

    try:
        for o in reversed(objs):
            if isinstance(o, dict) and o.get("type") == "user":
                p = o.get("promptId")
                if _clean(p):
                    return p
        for key in ("prompt_id", "promptId"):   # payload naming varies
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

    mode = _mode(data)
    if mode == MODE_OFF:
        _log_event(sid, "out_of_scope", mode=mode)
        return 0

    tp = data.get("transcript_path") or ""
    if not tp or not os.path.isfile(tp):
        _log_event(sid, "no_transcript", mode=mode)
        return 0

    try:
        objs = []
        with open(tp, "r", encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    o = json.loads(raw)
                except Exception:
                    continue
                if isinstance(o, dict) and o.get("isSidechain") is not True:
                    objs.append(o)       # MAIN-agent lines only
    except Exception:
        _log_event(sid, "unreadable_transcript", mode=mode)
        return 0

    if not objs:
        _log_event(sid, "empty_transcript", mode=mode)
        return 0

    turn = _turn_id(data, objs)               # diagnostic grep key only
    plog = turn or "-"

    # Boundary: everything after the last GENUINE user message = the final turn.
    # That same message is kept, because it decides the `yn` exemption and,
    # when it is the harness's own post-block injection, loop-guard signal (b).
    start = 0
    trigger = None
    for i, o in enumerate(objs):
        if _is_real_user(o):
            start = i + 1
            trigger = o

    offending = []
    classes = []
    for o in objs[start:]:
        if o.get("type") != "assistant":
            continue
        if o.get("isApiErrorMessage") is True:
            continue                     # CLI-authored, not model output
        msg = o.get("message") or {}
        if msg.get("role") != "assistant":
            continue
        for text in _text_of(msg.get("content")):
            for ln in text.splitlines():
                klass = _line_breach(ln, mode)
                if klass:
                    offending.append(ln.strip())
                    classes.append(klass)

    if not offending:
        # Clean turn -> proof-of-life, non-blocking.
        _log_event(sid, "clean", pid=plog, mode=mode)
        return 0

    # Class of the FIRST offender, so the logged verdict and `first=` always
    # describe the same line. `sic` may override it below.
    verdict = "block:" + classes[0]

    # --- Exemptions (see docstring EXEMPTIONS) -------------------------------
    # Order = widest authorisation first, so the log names the strongest reason.
    typed = _trigger_text(trigger)
    if _OVERRIDE_RE.search(typed):
        # The user suspended the rule for this turn —— disarmed in BOTH modes.
        _log_event(sid, "exempt:override", len(offending), offending[0],
                   pid=plog, mode=mode)
        return 0

    if mode == MODE_REPO:
        if _YN_TOKEN in typed:
            # The user authorised a one-word chat answer -> nothing to enforce.
            _log_event(sid, "exempt:yn", len(offending), offending[0],
                       pid=plog, mode=mode)
            return 0
        cap = _sic_cap(typed)
        if cap is not None:
            # A sanctioned status report: exempt only WITHIN its word cap,
            # counted over the offending lines alone (the turn's declarations
            # are separately permitted and would blow any cap).
            if len(" ".join(offending).split()) <= cap:
                _log_event(sid, "exempt:sic", len(offending), offending[0],
                           pid=plog, mode=mode)
                return 0
            verdict = "block:sic_overrun"
        if _dats_exempt(offending):
            # The single close-protocol status line -> sanctioned chat text.
            _log_event(sid, "exempt:dats", len(offending), offending[0],
                       pid=plog, mode=mode)
            return 0

    # --- Loop guard (see docstring LOOP GUARD) ------------------------------
    # Either signal alone withholds the block; both are checked because (a) can
    # be absent from a payload and (b) needs no payload at all.
    if bool(data.get("stop_hook_active")) or _is_stop_feedback(trigger):
        _log_event(sid, "loop_guard", len(offending), offending[0],
                   pid=plog, mode=mode)
        return 0

    # --- RED —— block and feed the model the reason via stderr ---------------
    # On exit 2 the harness ignores stdout/JSON, so write to STDERR. Every
    # breach reaching here blocks: there is no ceiling and no ledger. The log
    # line is written only AFTER the stderr write succeeds, so the record
    # always reflects a block actually delivered.
    try:
        sys.stderr.write(_BREACH[mode])
    except Exception:
        _log_event(sid, "block_failed", len(offending), offending[0],
                   pid=plog, mode=mode)
        return 0                          # fail-safe: never break the turn
    _log_event(sid, verdict, len(offending), offending[0], pid=plog, mode=mode)
    return 2                              # blocks the stop; stderr reaches Claude


if __name__ == "__main__":
    sys.exit(main())
