#!/usr/bin/env python3
"""Hashtag/Trigger Linter + Chat-Discipline Tally (UserPromptSubmit hook)

TWO jobs now, both advisory, sharing the one prompt-time channel PROVEN to
reach the model without waking it or costing an extra turn:
1. TRIGGERS (global; the job the filename names): `#[trigger]` tokens in the
   prompt (and in any comms file it names) that resolve to a `[trigger].md` in
   the SEARCH SCOPE below get a NON-BLOCKING reminder to READ that file (root
   CLAUDE.md §7.3.1: a `#[trigger]` MUST be resolved by reading its file,
   never guessed).
2. CHAT-DISCIPLINE TALLY (this repo only): when the PREVIOUS turn's chat text
   drew a breach verdict from `cscpt/clint.py` (the Stop-side chat linter,
   root CLAUDE.md §3.2), ONE line names the count and breach class so the new
   turn starts corrected instead of repeating it. Design and deliberate
   limits: CHAT-DISCIPLINE TALLY in the CCSIM section.

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: a UserPromptSubmit hook, ADVISORY —— never blocks. Each `#[trigger]`
  draws a line naming its protocol file (root CLAUDE.md §7.3.1). IF IT FIRES:
  read that file, or declare why not.
* TALLY (this repo only): one line counts the PREVIOUS turn's chat breaches
  (root §3.2). IF IT FIRES: declarations-only chat; never apologise in chat.
* BACKTICKED/FENCED `#name`s are DISCUSSED, not invoked —— only a bare token
  fires.
* ONLY YOUR WORDS FIRE: scanned = the prompt + any `*query_[TS].md` it names;
  nothing else.
* BLIND SPOT: triggers resolve only under `universal/`, `cp/`,
  `AJAP_repo/protocols/`, `AJAP_repo/inv/inveng.md`. Silence is not proof.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WIRING (kept here, not in NON-CCSIM: a caller never invokes this file, so the
plumbing is dead weight to everyone but an editor). Registered as a
`UserPromptSubmit` hook in the USER-level `~/.claude/settings.json` —— the
Claude Desktop app executes user-level hooks and silently ignores project-level
ones. IN: UserPromptSubmit JSON on stdin (fields `prompt`, `session_id`, `cwd`).
OUT: on a match, JSON on stdout carrying
`hookSpecificOutput.additionalContext` —— the chat-discipline tally line first
when it is due (CHAT-DISCIPLINE TALLY below), then one line per matched
trigger; nothing due -> no output. EXIT is ALWAYS 0, and it never emits
`decision:"block"` —— for UserPromptSubmit that would ERASE the user's prompt.
SCAN CORPUS: the prompt text PLUS the content of any `*query_[TS].md` file it
names, exactly ONE level deep, never recursive (see WHY ONLY `query_` FILES ARE
EXPANDED). A prompt whose envelope is `<task-notification>` is not a user
message and is not scanned at all (see WHY A TASK-NOTIFICATION IS NOT A
PROMPT). SEARCH SCOPE, in priority order:
`universal/` (canonical home of most triggers), `cp/` (recursive, CP-local),
`AJAP_repo/protocols/` (recursive), then `AJAP_repo/inv/inveng.md` alone ——
`inv/` is NEVER walked. Anything else, notably `sessions/`, is out of scope.
FAIL-SAFE: any error, missing field, absent directory or unreadable file ->
exit 0, no output; it must never break or delay a prompt on its own failure.

WHY A HOOK, NOT TRUST: forgetting to read a trigger's protocol file is a silent,
high-cost slip (running `#replace`/`#debate` from a guessed meaning). A
deterministic prompt-time scan names the right file BEFORE the turn starts.

WHY NO REPO-SCOPE GUARD, unlike clint/dlint_quick/nlint (tlint likewise has
none): those three can BLOCK a turn, so loosing them on a project that never
agreed to this repo's conventions is a genuine hazard. This one is purely
ADVISORY —— one appended line of context, exit always 0 —— so its worst misfire
elsewhere is a single ignorable line, set against the far larger cost of a MISSED
`#[trigger]` (guessing a protocol instead of reading it). Intentional asymmetry
—— do not "restore consistency" with a guard. THE TALLY HALF IS THE ONE
EXCEPTION: it IS cwd-gated, for its own reasons (see CHAT-DISCIPLINE TALLY ——
chat discipline is this repo's rule, and a foreign cockpit must not be nagged
about it); that asymmetry is equally deliberate, in the opposite direction.

CONSEQUENCE FOR PATHS: because invocations routinely arrive from OTHER repos,
`#[name]` must still resolve against THIS repo's `universal/`. Every path is
anchored on `_ROOT`/`_PARENT` (both derived from `__file__`), NEVER on the
process cwd, which is now commonly a different repo entirely. Nothing here may
reintroduce a cwd-relative path.

WHY THE SCOPE REACHES INTO `AJAP_repo/` (points 3 and 4): being global is only
half the job —— running everywhere is useless if the corpus is one repo. An AJAP
session was prompted `#eng`, this hook stayed silent because `eng.md` lives in
`AJAP_repo/protocols/` and nothing outside this repo was ever searched, the
protocol went unread, and the resulting rework cost over 100 hours. Reaching
across to the sibling AJAP protocol directory IS the point of the scope, not an
optional extra. `inv/` gets a single named file rather than a walk because that
tree is enormous; walking it would reintroduce exactly the latency this scope
was narrowed to remove.

WHY `sessions/` IS EXCLUDED: it holds ~1k comms files (`*_[TS].md`), which are
transcripts, never protocols. Indexing them made every non-canonical trigger pay
a walk over thousands of files, and let a token like `#career_close_202607181951`
"resolve" to a past transcript —— a reminder to read a file that defines nothing.
Pure latency for zero benefit. The exclusion is structural (`sessions/` is simply
not a search root) AND defended by `_EXCLUDED_DIR_NAMES`, so a later widening of
the scope cannot silently re-admit it. Corpus expansion still READS a named comms
file, but by computing its folder from the `[TS]` in its own filename (root
CLAUDE.md §3.4.9.1–2: start-month, else one month back) —— two direct stats, no
walk.

WHY SIBLING-RELATIVE, NOT HOME-RELATIVE: `AJAP_repo` is located as a sibling of
this repo via `_PARENT`, never via `$HOME`/`~`. This checkout lives on an
external volume (`~/.claude` is itself a symlink onto it) and has been relocated
before; a home-anchored constant would resolve to nothing after the next move and
the hook would go quietly silent —— the exact failure mode described above.

=== CHAT-DISCIPLINE TALLY (the second job) ===

WHY IT LIVES HERE, OF ALL PLACES: root CLAUDE.md §3.1 forbids chat prose
absolutely; `cscpt/clint.py` (Stop) detects breaches; and clint was demoted to
warn-only. But at Stop there is NO channel that reaches the model without
waking it, BY CONSTRUCTION —— the model has stopped, so reaching it means
starting it again. Verified against the Desktop harness binary itself: Stop
exit-0 plain stdout goes nowhere; exit-0 `systemMessage` becomes an attachment
whose model mapping is empty and which the Desktop surface never renders (142
sat unseen in this project's transcripts); exit-0 `additionalContext` at Stop
DOES reach the model but RE-INVOKES it on the same continuation path as a
block —— a block wearing a softer name, the exact deadlock clint's demotion
was ordered to end (clint's ALWAYS RED -> ALWAYS YELLOW section). hook_guide
§6.4.1 names the channels that reach the model WITHOUT waking it, and this
hook already owns one: UserPromptSubmit `additionalContext` —— model-visible
at the next turn's opening, zero extra turns, zero chapter-marker risk. The
price is stated, not hidden: correction arrives at the NEXT prompt, never
mid-turn. The owner accepted this explicitly as better than nothing, whilst
mandating that CCSIM keep looking for a genuinely live channel.

WHAT COUNTS AS "THE PREVIOUS TURN" —— the LAST clint log entry for this
session, and ONLY that entry, never a sum. clint logs one verdict PER STOP,
and a turn can Stop several times: every background task-notification wake
re-Stops and re-scans the SAME window (clint's boundary is the last GENUINE
user line, which a wake is not), so a single breach window was observed
logging SEVEN growing `yellow:prose` entries —— under fresh promptIds each
time, which also defeats any per-promptId ledger. The final Stop's scan
covers the whole window and supersedes every earlier partial scan, so its
`lines=` field IS the turn's defensible count: reported verbatim. If that
field will not parse as an integer, the line reports NO number at all ——
never a number that cannot be defended. Entries are matched on `session=`
(clint stores the id's first 8 chars), so parallel sessions sharing one log
can never cross-report; `exempt:*`/`clean:*` verdicts carry no breach and
`message_failed` lost its class, so only `yellow:*` fires.

WHY IT NEVER BECOMES WALLPAPER (three layers): (1) silent at zero —— a
reminder firing every turn is one nobody reads; (2) each clint verdict entry
is reported ONCE —— a ledger mark (sha1 of the raw entry, first 12 hex) rides
in this hook's own `tally=fired:` log line and is checked on the next prompt,
so the log doubles as the dedup ledger, the precedent mlint set (its log is
its per-prompt block ledger); no second state file exists to drift, leak into
`git status`, or need its own pruning, and `_prune_log`'s 800-line window
comfortably outlives any gap between two prompts of one session. A LOST
ledger line (log writes are swallowed on failure) costs one duplicate
advisory, never a loop. (3) The line names the concrete class and count,
which change with each real breach —— not a fixed sermon that fades.

WHY THE TALLY IS CWD-GATED whilst the trigger half is deliberately global:
one edge each way, both intentional. A missed `#trigger` ANYWHERE is the
expensive failure (a protocol guessed instead of read), so that half runs
everywhere and fails open. Chat discipline is THIS repo's rule: injecting
"you breached §3.2" into a project that never adopted §3.2 —— an AJAP `#seek`
cockpit, any foreign repo —— is noise at best and bait for phantom compliance
at worst. So the tally requires the payload `cwd` to resolve (realpath)
inside this repo and stays silent otherwise, INCLUDING when `cwd` is absent:
for this sub-feature silence is the conservative direction, and nothing is
lost —— the ledger only advances on a fire, so the next in-repo prompt still
reports the same entry. Do not "restore consistency" in either direction.
Root scope note: the tally reads `cscpt/.clint.log` and `cscpt/.hlint.log`
beside this file only —— anchored on `__file__`, never the cwd it gates on.

WHAT THE LINE SAYS, and what it deliberately does not: count + clint's own
class tag + a one-clause gloss + the rule + the correction, in ONE line ——
actionable without being a lecture. The rule clause is per-class where it
must be (`_TALLY_RULE`): the generic "declarations only" correction is
actively WRONG for a class like `sha_label`, whose offending line already
was a declaration —— there the clause names the one act that fixes it (drop
the repo label; root §3.2.4.5). Every class without an entry keeps the
generic clause, and the map stays minimal on purpose —— a bespoke sermon per
class is wallpaper by another route. The first offender is quoted only as an
IDENTIFYING STUB: hard-capped at `_TALLY_EXCERPT_CHARS`, wrapped in backticks
(this file's own convention —— backticked = discussed, never live), and
dropped entirely when it carries a backtick of its own rather than escaped.
The full offending text stays in clint's log for a human audit; re-injecting
a paragraph of the very prose being suppressed, for the model to echo back,
would be self-defeating —— that trade was weighed, not defaulted. The gloss
map never quotes a hidden numeric cap (clint documents why its char cap must
stay invisible to agents). The line also pre-empts the one reflex that turns
a correction into a fresh breach: it forbids apologising IN CHAT.

TALLY FAIL-OPEN + STAGE LOG: the whole computation is wrapped so ANY failure
degrades to "no tally line" with stage `error` —— never a broken, delayed,
or (worst of all) erased prompt. Stages, one per invocation in the `tally=`
log field: `off_scope` (cwd absent/foreign), `no_sid` (unusable session id),
`no_log` (clint log missing/unreadable), `no_entry` (no line for this
session), `clean` (last verdict not `yellow:*`), `dup` (already reported),
`fired:<class>:<count>@<mark>`, `error`; `-` on invocations that never reach
the tally (bad payload, task-notification). Logged because a missing log
line is how a hook stays dead unnoticed —— this repo paid 70 days for that
lesson once. A wake NEVER fires the tally: the computation sits AFTER the
`<task-notification>` gate, so a wake is logged `not_user_prompt` and the
tally is not even attempted —— a wake is not a new turn, and correcting one
mid-turn is the re-invocation trap this design exists to avoid. COST,
measured end-to-end on this Mac against live-sized logs (40-run medians,
pre-change vs post-change, same payload/env): 26.4 ms -> 30.0 ms, i.e. ≈4 ms
added to a ~27 ms event inside a ~0.39 s round trip against a 1 s budget
(p90 was unchanged, 35.5 -> 35.9 ms); both log reads are bounded by the two
files' own prune ceilings.

REGEX PRECISION: `_TRIGGER_RE` requires the `#` NOT to follow a word char, so a
URL fragment (`file#L10`) never matches whilst a standalone `#close` does, and a
markdown heading (`# Heading`) has a space after `#` so never matches either.
`_MD_TOKEN_RE` stops at whitespace and common quoting/bracket chars, so trailing
punctuation is not swallowed. Names are deduped case-insensitively (`#close` x10
-> one reminder), first-seen casing kept.

BACKTICK / FENCE EXEMPTION: a `#name` enclosed in single backticks
(`` `#close` ``) or sitting inside a ``` fenced ``` block is SKIPPED, never
treated as a live trigger. Two reasons, both named by the owner: (1) it lets a
`#trigger` be DISCUSSED ("what does `#close` do?") without being INVOKED —
right now those are indistinguishable and the hook cannot tell intent from a
bare token; (2) it stops premature reads fired by a trigger merely quoted
inside an EXAMPLE — root CLAUDE.md itself carries several (`` `#replace` ``,
`` `#debate` ``) precisely as illustrations, and every one of them used to
misfire when that file was read in as referenced content. Fenced blocks get
the SAME exemption as inline backticks, deliberately, not by omission: a
```` ``` ````-fenced example is quoting for exactly the same reason a
single-backtick one is (a shown command, a pasted transcript, a doc excerpt),
and treating the two fence styles differently would be an arbitrary line with
no principled basis — a user who wraps the same example in triple backticks
instead of one would otherwise get a different, surprising result. Mechanics:
`_quoted_spans()` first finds every fenced span on the RAW text (so its
coordinates are exact), then masks those characters out (spaces, newlines
kept) before scanning for inline single-backtick spans — the mask stops a
fence's own ``` delimiters, or a stray backtick used INSIDE example code, from
pairing with a backtick outside the fence and wrongly swallowing real prompt
text as "quoted". A trigger match is exempted when its `#` falls inside any
span. This scan runs PER SOURCE (the prompt, then each referenced file, never
a joined blob), so a fence or backtick span can never straddle the boundary
between the prompt and a file it names. An unterminated fence (no closing
```` ``` ````) matches nothing and is therefore NOT exempted — fail-open, the
same direction as every other lint in this repo: a rare unclosed-fence corner
case firing an extra (harmless, advisory) reminder is preferable to a fence
that never closes silently blanking out the rest of the prompt.

WHY ONLY `query_` FILES ARE EXPANDED —— the fix for the worst misfire this hook
has had, and the reason a wider corpus must never be restored. Corpus expansion
once read EVERY `*.md` the prompt named. That conflated two opposite things: a
file whose content IS the user's instruction, and a file the user merely asked
to have READ. Protocol and doc files are the second kind, and they are full of
bare `#name` tokens because their JOB is to describe triggers. Measured on the
live repo, the prompt "re-read root CLAUDE.md (also its Unconditionals +
coding.md)" —— which invokes no trigger whatsoever —— drew reminders for `#wrap`
and `#numbered`, matched at root `CLAUDE.md` §3.4.7.2 ("incl. in its #wrap") and
§5.3 ("non-#numbered list"). Both are prose ABOUT a trigger. `universal/close.md`
and `universal/m2.md` carry the same shape, as does `cp/ccsim/backlog.md`, so
naming any of them fired the same phantom set.

WHY THAT IS WORSE THAN SILENCE, which is the whole reason it is fixed rather
than tolerated: root CLAUDE.md §7.3.1 makes a `#[trigger]` a MANDATE to read a
protocol file. A hook that invents triggers therefore mandates reads nobody
asked for, and the agent that complies burns context on an irrelevant protocol
whilst the agent that does not is being trained to overrule this hook on
judgement. Either way the reminder stops being evidence. The day it is RIGHT it
will be ignored along with the noise —— which is precisely the `#cic` incident
recorded below, arriving by a different door.

THE LINE DRAWN, and why here: only `*query_[TS].md` is expanded. Root CLAUDE.md
§3.3.1 defines that type as the user's own message, and §3.6.2 writes a long
chat message into one on the user's behalf —— so a `query_` file IS the prompt,
merely delivered as a file, and a bare `#name` in it is a real invocation. Every
other type is somebody DESCRIBING a trigger: `response_`/`close_`/`wrap_` are
this agent's own past output (a `close_` that records "the user sent #close"
must not re-mandate `close.md`), and a protocol/guide/backlog is documentation.
This costs the win NOTHING: the `#cic` incident below turned on a bare `#cic`
inside a `query_` file, which is exactly the case still expanded. Anyone tempted
to widen this again should first note that ~27% of `response_` files and ~49% of
`close_` files in this repo contain a bare, resolving trigger token —— the wider
corpus is not a slightly noisier signal, it is mostly noise.

WHY A TASK-NOTIFICATION IS NOT A PROMPT: when a background agent finishes, the
harness delivers its report through the SAME `prompt` field a human types into,
wrapped in a `<task-notification>` envelope. Nothing in that payload is the
user's; it is a sub-agent's prose, which the harness itself flags as untrusted
observed content. Firing a protocol MANDATE off it is wrong twice over —— it
mid-turn re-mandates reads for a turn already underway, and it lets any text a
sub-agent happens to emit direct this agent's reading. A prompt whose stripped
text starts with that envelope is logged `not_user_prompt` and scanned no
further. The check is deliberately a prefix test on the exact envelope tag, not
a fuzzy "looks automated" heuristic: a false NEGATIVE here costs one advisory
line, whilst a false positive would silence a real user prompt that merely
quoted the tag.

WHY THE REMINDER READS AS A MANDATE, NOT A SUGGESTION —— the wording is the
enforcement, so it is specified here rather than left to whoever edits the
f-string next. The line used to end "unless already read or INTENTIONALLY
DEFERRED", and that clause was itself the defect. On a live prompt this hook
worked perfectly: it read the named comms file, found a bare `#cic` inside it,
and injected TWO reminders on one line —— that trigger and a second one. The
agent read the SECOND file, silently self-certified the first as "intentionally
deferred", answered from a web search instead of the mandated route, and
shipped. The owner's reasonable conclusion was that the hook had never fired.
It had; only its wording failed. Three lessons are baked into the current text:
(1) an advisory that ships its own escape hatch WILL be escaped, so the hedge is
gone; (2) it now cites root CLAUDE.md §7.3.1–2 by number, because a reminder
that reads as a suggestion loses to whatever the agent already planned to do,
whilst one that names the rule it is enforcing does not; (3) reaching a similar
answer by some OTHER route is stated NOT to discharge the read —— that was the
exact substitution made, and nothing in the old line forbade it. A deferral is
still permitted, but must be DECLARED: a visible deferral the user can overrule
is categorically better than an invisible one he discovers in the output.
RESIDUAL, stated rather than papered over: UserPromptSubmit must never block
(see below and `cp/ccsim/hook_guide.md` §6.6 —— `decision:"block"` here ERASES
the user's prompt), so WORDING is the only lever this hook has and compliance
remains the model's choice. Anyone wanting a guarantee must add enforcement at
a channel that can gate the act, not strengthen this sentence again.

WHY IT LOGS EVERY INVOCATION: the incident above cost a forensic dig through
session transcripts to establish something the hook itself should have been
able to answer —— "did you fire, and what did you say?". A log written only on a
match cannot tell "never ran" apart from "ran and found nothing"
(`cp/ccsim/hook_guide.md` §7.7), and that ambiguity is precisely what let the
blame land on the hook. One TAB-separated line per invocation goes to
`cscpt/.hlint.log` (git-ignored), tagged by the stage reached: `no_stdin`,
`not_dict`, `no_prompt`, `not_user_prompt`, `silent`, `fired`. A `fired` line
carries the trigger names, so a later "you never told me" is settled by one
`grep`. Logging is
housekeeping —— every failure is swallowed, exactly as in `clint.py`, because a
logging error must never break a prompt.

PERFORMANCE: a canonical `universal/[name].md` is a single stat —— no index at
all. Otherwise the scope index is built LAZILY and at most ONCE per run, over a
few hundred files instead of the whole repo, pruning `.git`, `node_modules`,
`.venv` and friends. Caps (never hit in normal use) bound the index, the
referenced-file count/bytes and the reminder count, so neither a huge file nor a
trigger-stuffed prompt can stall a turn. The log append is one `open`+`write`
on a small file, with the prune amortised across ~0.5% of invocations.

=== RETIRED: THE QUERY/RESPONSE PAIRING REMINDER (do not re-add here) ===

This file briefly also carried a second check —— a `*_query_[TS].md` named in the
prompt with no `*_response_[TS].md` beside it drew a reminder naming the response
it owed (root CLAUDE.md §3.5.3). It was REMOVED, and the reasoning is kept here
so it is not rebuilt from scratch by whoever next reads §3.5.3 and reaches for a
hook.

WHY IT WENT: at prompt-submit time it had NO discriminating power. A brand-new
`query_` has no `response_` yet BY CONSTRUCTION, so the check fired identically
on a perfectly compliant turn and on the breach —— a metronome, not a detector.
Measured over the live `.hlint.log`: 5 fires in 29 real invocations, i.e. once
for essentially every turn opened by a query file, at ~124 tokens a fire. The
token bill was small; the PRECISION was the defect, and a reminder that fires on
every correct turn is how a check earns being tuned out.

WHAT NOW COVERS IT: `.githooks/pre-commit`'s REVERSE PAIRING ARM (non-blocking,
adds-only) at commit time, and root CLAUDE.md §3.1.7.7 in prose. Both are
POST-HOC —— by the time either speaks, the wrong file has already been written.
That gap is real and is recorded as such rather than papered over.

WHERE IT BELONGS IF REBUILT: `cscpt/flint.py`, which already owns comms
FILENAMES and already models the `{query, response}` same-TS role pair. Its
PreToolUse half fires at the MOMENT OF THE WRITE (`cp/ccsim/CLAUDE.md` §8.7),
where the check regains its precision: it can compare the `response_` being
written against the NEWEST unpaired `query_` in that folder and stay silent
unless they disagree —— which on a compliant turn they never do. ⚠️ It needs a
per-`prompt_id` ledger there, or the sanctioned mid-turn case (a follow-up query
answered inside the CURRENT response, root §3.1.7.6.1) re-fires on every edit of
a long sprint. That accepted false positive is irreducible: no script can tell it
from the breach, since the two produce identical file operations and differ only
in whether the agent was IDLE when the message arrived.
"""

import sys
import io
import select
import stat
import os
import re
import json
import hashlib
from datetime import datetime

# Repo root = parent of this script's `cscpt/` dir (deterministic anchor; never
# relies on cwd, which may be a sub-folder for a given session).
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Realpathed twin of `_ROOT`, for the tally's cwd gate:
# a payload cwd may arrive through a symlink (`~/.claude`
# itself is one on this Mac), and comparing realpaths is
# what keeps the gate honest across such aliases.
_ROOT_REAL = os.path.realpath(_ROOT)

# The directory that holds this repo. Sibling repos are derived from here rather
# than from `$HOME`, because this checkout sits on an external volume and has
# been relocated before —— a home-anchored path would silently resolve to
# nothing after a move, and the hook would go quietly silent.
_PARENT = os.path.dirname(_ROOT)

# Sibling repo carrying its own protocol set (see the AJAP note in the docstring).
_AJAP = os.path.join(_PARENT, "AJAP_repo")

# ---------------------------------------------------------------------------
# GLOBAL REACH —— no repo-scope guard here, deliberately: this lint is
# ADVISORY-ONLY (one line of context, exit always 0), so it may safely run in
# every project the user-level registration reaches, and a missed `#[trigger]`
# is the expensive failure. Consequence: every path below is anchored on
# `_ROOT`/`_PARENT`, NEVER on the process cwd, since invocations routinely
# arrive from other repos. Full rationale is in the CCSIM docstring above.
# ---------------------------------------------------------------------------

# SEARCH SCOPE, in priority order —— the ONLY directories a `#[trigger]` may
# resolve within. Deliberately narrow: `universal/` is where nearly every
# trigger lives, `cp/` carries the CP-local ones (root CLAUDE.md §7.3.3), and
# `AJAP_repo/protocols/` is reached because this hook runs globally and an
# unresolved `#eng` there once cost over 100 hours. An absent directory (e.g. a
# machine without the AJAP checkout) is skipped silently, never an error.
_SEARCH_DIRS = (
    os.path.join(_ROOT, "universal"),
    os.path.join(_ROOT, "cp"),
    os.path.join(_AJAP, "protocols"),
)

# Individually named files admitted to the scope. `AJAP_repo/inv/` is far too
# large to walk, so its one protocol-bearing file is listed outright.
_SEARCH_FILES = (
    os.path.join(_AJAP, "inv", "inveng.md"),
)

# Directories never worth walking (VCS internals, dependency/cache trees).
_SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    ".idea", ".vscode", ".DS_Store",
}

# Pruned inside EVERY search root as a second line of defence. `sessions/` is
# already out of scope by construction (it is not a search root); this set makes
# the exclusion survive any future widening of `_SEARCH_DIRS`, so comms
# transcripts can never be re-admitted as trigger targets by accident.
_EXCLUDED_DIR_NAMES = {"sessions"}

# A `#[name]` trigger: name = letters/digits/_/-, and the `#` is NOT preceded by
# a word char (so a URL fragment / suffix like `file#L10` never matches, whilst
# a standalone `#close` or `## 1.`-free hashtag still does; a markdown heading
# `# Heading` has a space after `#` and so never matches either).
_TRIGGER_RE = re.compile(r"(?<![A-Za-z0-9_])#([A-Za-z0-9_-]+)")

# A fenced code block: ``` ... ``` (DOTALL so the fence can span lines). Found
# on the RAW text first (see `_quoted_spans`), so its span coordinates are
# exact positions in the original string, before anything is masked.
_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)

# An inline single-backtick span: `...`, never crossing a newline —— mirrors
# how markdown itself never lets an inline code span cross a paragraph break,
# so a stray backtick earlier in the same prompt cannot pair across it.
_INLINE_BACKTICK_RE = re.compile(r"`[^`\n]*`")

# An `*.md` filename/path token in the prompt (stops at whitespace or common
# quoting/bracket chars so trailing punctuation is not swallowed).
_MD_TOKEN_RE = re.compile(r"([^\s\"'`()<>|,;]+\.md)", re.IGNORECASE)

# A comms filename's trailing `[TS]` = `YYYYMMDDHHmm` (root CLAUDE.md §2.2.1).
# Its `sessions/[YYYY]/[YYYYMM]/` folder is COMPUTED from this, so a named comms
# file can still be read for corpus expansion without walking `sessions/`.
_COMMS_TS_RE = re.compile(r"(\d{4})(\d{2})\d{6}\.md$", re.IGNORECASE)

# The ONLY filenames whose CONTENT is expanded into the scan corpus: a
# `query_[TS].md`, optionally CP-prefixed per root CLAUDE.md §3.3.6
# (`career_query_…`, `ccsim_query_…`). Rationale: docstring, WHY ONLY `query_`
# FILES ARE EXPANDED —— that type alone IS the user's message (§3.3.1/§3.6.2);
# every other `.md` describes triggers instead of invoking them.
_USER_QUERY_RE = re.compile(r"(?:^|_)query_\d{12}\.md$", re.IGNORECASE)

# The harness delivers a finished background agent's report through the same
# `prompt` field a human types into, inside this envelope. It is a sub-agent's
# prose, not the user's instruction —— see docstring, WHY A TASK-NOTIFICATION IS
# NOT A PROMPT. Matched as an exact leading tag, never a fuzzy heuristic.
_TASK_NOTIFICATION_TAG = "<task-notification>"

# Safety caps (backstops; none is hit in normal use).
_MAX_INDEX = 60000          # max .md files indexed before giving up the walk
_MAX_REF_FILES = 10         # max distinct referenced files read from a prompt
_MAX_READ_BYTES = 512 * 1024  # max bytes read from any one referenced file
_MAX_REMINDERS = 15         # max reminder lines injected (avoid a flood)

_HEADER = ("[hlint hook] Possible hashtag-trigger(s) detected —— non-blocking "
           "reminder(s):")

# Per-invocation stage log (git-ignored). Overridable via `HLINT_LOG` so a
# regression test never writes to the live file. Rationale: docstring, WHY IT
# LOGS EVERY INVOCATION —— a log written only on a match cannot distinguish
# "never ran" from "ran and found nothing".
_LOG = os.environ.get("HLINT_LOG") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".hlint.log")

# Prune hysteresis, mirroring `clint.py`: read the file only once it could
# possibly exceed the cap, rewrite only when it actually does. The 1000/800 gap
# means a rewrite happens at most once per 200 invocations.
_LOG_PRUNE_AT_BYTES = 400 * 1024
_LOG_MAX_LINES = 1000
_LOG_KEEP_LINES = 800

# --- CHAT-DISCIPLINE TALLY (rationale: docstring section of that name) ------
# clint's Stop-side verdict log, READ here at the next
# prompt. Same env knob clint itself WRITES under, so the
# pair can never point at different files —— a test that
# redirects clint's writes redirects this read with it.
_CLINT_LOG = os.environ.get("CLINT_LOG") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".clint.log")

# Identifying stub of the first offending line: hard cap,
# shown backticked, dropped if it carries its own backtick
# (docstring: WHAT THE LINE SAYS).
_TALLY_EXCERPT_CHARS = 40

# clint breach class -> one-clause gloss. Never quotes a
# hidden numeric cap (clint keeps its char cap invisible
# to agents on purpose). An unknown class falls back to a
# generic clause —— clint may grow classes before this map
# learns them, and that must not cost the report.
_TALLY_GLOSS = {
    "prose": "chat prose bearing no declaration glyph",
    "io_shape": "an I/O declaration glyph carrying non-file-list text",
    "sha_shape": "the commit-SHA glyph carrying a non-hash body",
    "sha_label": "a repo shorthand on a single-repo turn's lone SHA line",
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
_TALLY_GLOSS_FALLBACK = "an impermissible chat line"

# clint breach class -> the rule + correction clause of the
# injected line. Nearly every class shares the generic
# §3.1–§3.2 clause below; a class earns its OWN entry ONLY
# when the generic correction would teach the WRONG fix.
# `sha_label` (clint's solo-label check) is exactly that:
# its offending line already WAS a declaration, so "chat
# carries declarations only" corrects nothing —— the one
# act that fixes it is dropping the repo label, and the
# clause must say so (root §3.2.4.5: shorthands only when
# multiple repos were touched). Keep this map minimal: a
# per-class sermon for every class is wallpaper by another
# route.
_TALLY_RULE = {
    "sha_label": ("Root CLAUDE.md §3.2.4.5: repo shorthands belong ONLY on "
                  "a multi-repo turn's multiple SHA lines —— a single-repo "
                  "turn's SHA declaration is the glyph plus backticked SHAs "
                  "alone, so drop the label and its colon."),
}
_TALLY_RULE_DEFAULT = ("Root CLAUDE.md §3.1–§3.2: chat carries the six "
                       "declaration lines ONLY; substantive content belongs "
                       "in this turn's `response_` file.")


def _prune_log():
    """Bound `_LOG` to its recent window —— cheap, atomic, fail-safe.

    Runs AFTER the current line is on disk, so this invocation's own line can
    never be a casualty of its own prune. The surviving tail is staged in a
    pid-suffixed sibling and moved in with `os.replace` (one atomic rename), so
    a crash leaves either the untouched original or the complete replacement,
    never a half file. Every failure is swallowed: pruning is housekeeping, and
    an unwritable directory must degrade to "the log keeps growing", never to
    "the hook fails"."""
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


def _log_event(stage, sid="-", triggers="-", tally="-"):
    """Append ONE terse line for ANY invocation —— match or not.

    TAB-separated, `triggers=` last because it alone carries free text (tabs and
    newlines are flattened, so a record is always exactly one line). `tally=`
    names what the chat-discipline tally did this invocation (docstring: TALLY
    FAIL-OPEN + STAGE LOG); its `fired:` form doubles as the tally's dedup
    LEDGER, read back by `_tally_reported` —— the one part of this log that IS
    parsed, so a lost `fired:` line costs one duplicate advisory. FAIL-SAFE:
    all errors swallowed —— everything else here is diagnostics only, never the
    reminder itself. (Historic lines carry a `pairs=N` field from the retired
    pairing check, or no `tally=` field at all from before the tally existed;
    `_tally_reported` matches on the field marker, so both older shapes are
    inert rather than a compatibility burden.)"""
    try:
        with open(_LOG, "a", encoding="utf-8") as lf:
            lf.write("%s\tsession=%s\tstage=%s\ttally=%s\ttriggers=%s\n"
                     % (datetime.now().isoformat(timespec="seconds"), sid,
                        stage,
                        str(tally)[:120].replace("\t", " ").replace("\n", " "),
                        str(triggers)[:300].replace("\t", " ").replace("\n", " ")))
    except Exception:
        pass
    _prune_log()

# Lazily-built {basename_lower: [(scope_rank, absolute path), ...]} index of the
# search scope. None until first needed; built at most once per run.
_INDEX = None


def _rel(path):
    """Display path: repo-relative for this repo, parent-relative for siblings."""
    for base in (_ROOT, _PARENT):
        rel = os.path.relpath(path, base)
        if rel != os.pardir and not rel.startswith(os.pardir + os.sep):
            return rel.replace(os.sep, "/")
    return path.replace(os.sep, "/")


def _build_index():
    """Walk ONLY the search scope -> {basename_lower: [(rank, abspath), ...]}.

    `rank` is the scope's position in `_SEARCH_DIRS`/`_SEARCH_FILES`, so the
    declared priority order survives into `_best()`. A missing directory is
    skipped silently: a machine without the sibling AJAP checkout must still get
    working `universal/`+`cp/` reminders, not an error.
    """
    index = {}
    count = 0
    # Individually-named files first, so the `_MAX_INDEX` backstop below can
    # never starve them (rank is assigned explicitly, so order of insertion
    # does not affect priority).
    for offset, path in enumerate(_SEARCH_FILES):
        if os.path.isfile(path):
            index.setdefault(os.path.basename(path).lower(), []).append(
                (len(_SEARCH_DIRS) + offset, path))
    for rank, root in enumerate(_SEARCH_DIRS):
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            # Sorted so the walk order is deterministic across filesystems.
            dirnames[:] = sorted(d for d in dirnames
                                 if d not in _SKIP_DIRS
                                 and d not in _EXCLUDED_DIR_NAMES)
            for fn in filenames:
                if fn.lower().endswith(".md"):
                    index.setdefault(fn.lower(), []).append(
                        (rank, os.path.join(dirpath, fn)))
                    count += 1
                    if count >= _MAX_INDEX:
                        return index
    return index


def _get_index():
    global _INDEX
    if _INDEX is None:
        try:
            _INDEX = _build_index()
        except Exception:
            _INDEX = {}
    return _INDEX


def _best(entries):
    """Deterministic pick: scope rank, then shallowest, shortest, lexicographic.

    Returns the absolute path; callers render it via `_rel()` for display.
    """
    def key(entry):
        rank, path = entry
        shown = _rel(path)
        return (rank, shown.count("/"), len(shown), shown)
    return sorted(entries, key=key)[0][1]


def _comms_candidates(base):
    """Direct candidate paths for a `*_[TS].md` comms file —— no walk.

    A comms filename carries its own `YYYYMMDDHHmm`, and comms files live in the
    folder of the session's START month, so the folder is computable: try the
    TS's own month, then one month back (root CLAUDE.md §3.4.9.1–2, which covers
    a session that ran past a month boundary). Two stats, versus a walk of ~1k
    files —— and it keeps `sessions/` out of the trigger search entirely.
    """
    m = _COMMS_TS_RE.search(base)
    if not m:
        return []
    year, month = int(m.group(1)), int(m.group(2))
    months = [(year, month)]
    months.append((year - 1, 12) if month == 1 else (year, month - 1))
    return [os.path.join(_ROOT, "sessions", "%04d" % y, "%04d%02d" % (y, mo), base)
            for y, mo in months]


def _locate(token):
    """Absolute path of an `*.md` file the prompt names, or None. Never walks.

    Order: the token taken as a path (absolute, or relative to this repo or its
    parent) -> the search-scope index by basename -> a comms file addressed by
    its own `[TS]`. Nothing is resolved against the process cwd, which for this
    globally-registered hook is routinely a different repo.
    """
    base = os.path.basename(token)
    cands = []
    if os.path.isabs(token):
        cands.append(token)
    else:
        cands.append(os.path.join(_ROOT, token))
        cands.append(os.path.join(_PARENT, token))
    entries = _get_index().get(base.lower())
    if entries:
        cands.append(_best(entries))
    cands.extend(_comms_candidates(base))
    for cand in cands:
        if os.path.isfile(cand):
            return cand
    return None


def _read_referenced(prompt):
    """Content of the `*query_[TS].md` files the prompt names (bounded).

    ONLY that type is expanded —— it IS the user's message delivered as a file
    (root CLAUDE.md §3.3.1/§3.6.2), so a bare `#name` inside it is a genuine
    invocation. Every other `.md` a prompt names is a protocol, guide, or this
    agent's own past output, all of which DESCRIBE triggers in prose; scanning
    them manufactured mandates for triggers nobody invoked. Full reasoning:
    docstring, WHY ONLY `query_` FILES ARE EXPANDED. The gate sits BEFORE
    `_locate`, so a non-query name costs nothing —— not even the index build.
    """
    parts = []
    seen = set()
    for m in _MD_TOKEN_RE.finditer(prompt):
        token = m.group(1)
        base = os.path.basename(token).lower()
        if base in seen or not _USER_QUERY_RE.search(base):
            continue
        seen.add(base)
        full = _locate(token)
        if not full:
            continue
        try:
            with open(full, "r", encoding="utf-8", errors="replace") as fh:
                parts.append(fh.read(_MAX_READ_BYTES))
        except Exception:
            pass
        if len(seen) >= _MAX_REF_FILES:
            break
    return parts


def _quoted_spans(text):
    """(start, end) spans in `text` where a `#trigger` is being DISCUSSED, not
    invoked: inside a fenced code block or an inline single-backtick span.
    Rationale in the module docstring (BACKTICK / FENCE EXEMPTION).

    Fenced spans are found FIRST, on the untouched `text`, so their
    coordinates are exact. The inline-backtick scan then runs over a MASKED
    copy —— fenced-block characters overwritten with spaces, newlines kept so
    `[^`\\n]` still behaves —— so a fence's own ``` delimiters, or a stray
    backtick used INSIDE example code, can never pair with a backtick outside
    the fence and wrongly swallow real prompt text as "quoted".
    """
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


def _is_quoted(pos, spans):
    """True if `pos` (the trigger's `#`) falls inside any quoted span."""
    return any(start <= pos < end for start, end in spans)


def _extract_triggers(text):
    """Names of `#trigger` tokens in `text`, in first-appearance order,
    SKIPPING any match sitting inside a quoted span (see `_quoted_spans`) ——
    a backticked or fenced `#name` is discussed, not invoked, and never
    reaches the caller. Run PER SOURCE (never on a joined blob) so a fence or
    backtick span can never straddle the boundary between two sources."""
    spans = _quoted_spans(text)
    return [m.group(1) for m in _TRIGGER_RE.finditer(text)
            if not _is_quoted(m.start(), spans)]


def _resolve_trigger(name):
    """Display path of `[name].md` within the search scope, or None.

    Canonical `universal/[name].md` is tried as a single stat first —— that is
    the overwhelmingly common case, and it means most prompts never build an
    index at all.
    """
    canonical = os.path.join("universal", name + ".md")
    if os.path.isfile(os.path.join(_ROOT, canonical)):
        return canonical.replace(os.sep, "/")
    entries = _get_index().get((name + ".md").lower())
    if not entries:
        return None
    return _rel(_best(entries))


# ---------------------------------------------------------------------------
# CHAT-DISCIPLINE TALLY —— the second job. Full rationale in the docstring
# section of that name; the comments here cover mechanics only.
# ---------------------------------------------------------------------------

def _tally_in_scope(data):
    """True only when the payload `cwd` resolves inside THIS repo.

    Chat discipline is this repo's rule, so an absent or foreign cwd means
    SILENCE —— the conservative direction for this sub-feature, and the
    OPPOSITE of the trigger half's global fail-open (docstring: WHY THE TALLY
    IS CWD-GATED). Nothing is lost by the silence: the ledger only advances
    on a fire, so the next in-repo prompt still reports the same entry."""
    cwd = data.get("cwd")
    if not (isinstance(cwd, str) and cwd):
        return False
    real = os.path.realpath(cwd)
    return real == _ROOT_REAL or real.startswith(_ROOT_REAL + os.sep)


def _last_clint_entry(sid8):
    """The NEWEST clint log line for this session, or None. May raise OSError
    (caller maps it to stage `no_log`).

    Newest-first is the whole design: every earlier entry for the session is
    either a partial re-scan of the same window (a task-notification wake) or
    an older turn already reported/superseded —— docstring, WHAT COUNTS AS
    "THE PREVIOUS TURN". The full file is read rather than a tail-seek:
    clint's own prune bounds it (~70 KB steady state), and a seek that could
    silently miss a quiet session's last entry under another session's
    traffic would be a correctness bug bought for under a millisecond."""
    with open(_CLINT_LOG, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    needle = "\tsession=%s\t" % sid8
    for line in reversed(text.splitlines()):
        if needle in line:
            return line
    return None


def _tally_reported(sid, mark):
    """True if `mark` (this clint entry's ledger id) was already reported for
    this session —— checked against the NEWEST `tally=fired:` line for `sid`
    in this hook's OWN log, which doubles as the ledger (mlint precedent;
    docstring: WHY IT NEVER BECOMES WALLPAPER). Only the newest marker can
    match: clint's log is append-only and prune keeps the newest tail, so a
    candidate entry can never be OLDER than the last one reported. Unreadable
    ledger -> False: a duplicate advisory beats a silently lost one."""
    try:
        with open(_LOG, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except Exception:
        return False
    needle = "\tsession=%s\t" % sid
    for line in reversed(text.splitlines()):
        if needle in line and "\ttally=fired:" in line:
            return ("@%s\t" % mark) in line
    return False


def _tally_message(cls, count, excerpt):
    """The ONE injected line: count + class + gloss + rule + correction
    (docstring: WHAT THE LINE SAYS). `count` may be None —— then no number is
    claimed at all, because a number that cannot be defended teaches the
    reader to distrust the defensible ones."""
    if count is None:
        head = ("[hlint hook] Chat-discipline tally: the PREVIOUS turn's chat "
                "text drew a breach verdict from clint")
    else:
        head = ("[hlint hook] Chat-discipline tally: the PREVIOUS turn ended "
                "with %d impermissible chat line%s"
                % (count, "" if count == 1 else "s"))
    stub = "; first offender: `%s`" % excerpt if excerpt else ""
    return (head + " —— clint class `%s` (%s)%s. %s Comply THIS turn, and "
            "do NOT apologise in chat —— that would itself be a breach."
            % (cls, _TALLY_GLOSS.get(cls, _TALLY_GLOSS_FALLBACK), stub,
               _TALLY_RULE.get(cls, _TALLY_RULE_DEFAULT)))


def _chat_tally(data, sid):
    """(injected line or None, tally stage) —— never raises past its caller's
    wrapper, and every exit names its stage so a dead tally is visible in the
    log rather than indistinguishable from a clean one (docstring: TALLY
    FAIL-OPEN + STAGE LOG)."""
    if not isinstance(sid, str) or not sid or sid == "-":
        return None, "no_sid"
    if not _tally_in_scope(data):
        return None, "off_scope"
    sid8 = sid[:8]
    try:
        entry = _last_clint_entry(sid8)
    except Exception:
        return None, "no_log"
    if entry is None:
        return None, "no_entry"
    fields = {}
    for part in entry.split("\t")[1:]:
        key, _, val = part.partition("=")
        fields.setdefault(key, val)
    action = fields.get("action", "")
    if not action.startswith("yellow:"):
        # `exempt:*`/`clean:*` carry no breach; `message_failed`
        # lost its class, and reporting it would mean inventing
        # one (docstring: WHAT COUNTS AS "THE PREVIOUS TURN").
        return None, "clean"
    mark = hashlib.sha1(entry.encode("utf-8", "replace")).hexdigest()[:12]
    if _tally_reported(sid, mark):
        return None, "dup"
    cls = action[len("yellow:"):] or "unknown"
    try:
        count = int(fields.get("lines", ""))
    except (TypeError, ValueError):
        count = None                 # never claim an indefensible number
    excerpt = (fields.get("first") or "").strip()
    if excerpt in ("", "-") or "`" in excerpt:
        excerpt = ""                 # no stub beats a broken/quoting one
    elif len(excerpt) > _TALLY_EXCERPT_CHARS:
        excerpt = excerpt[:_TALLY_EXCERPT_CHARS].rstrip() + "…"
    stage = ("fired:%s:%s@%s"
             % (cls, "?" if count is None else count, mark))
    stage = stage.replace("\t", " ").replace("\n", " ")
    return _tally_message(cls, count, excerpt), stage


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
    '  printf \'%s\' \'{"hook_event_name":"UserPromptSubmit",'
    '"prompt":"#close"}\' \\\n'
    '    | python3 cscpt/hlint.py\n'
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
        _log_event("no_stdin")
        return 0

    if not isinstance(data, dict):
        _log_event("not_dict")
        return 0

    sid = data.get("session_id") or "-"

    prompt = data.get("prompt")
    if not isinstance(prompt, str) or not prompt:
        _log_event("no_prompt", sid)
        return 0

    # A finished background agent's report arrives through this same field. It
    # is not the user's instruction, so no `#name` inside it may mandate a read
    # (docstring: WHY A TASK-NOTIFICATION IS NOT A PROMPT). Logged as its own
    # stage so "hlint saw this and declined" stays distinguishable from
    # "hlint found nothing".
    if prompt.lstrip().startswith(_TASK_NOTIFICATION_TAG):
        _log_event("not_user_prompt", sid)
        return 0

    # SECOND JOB —— chat-discipline tally. Deliberately AFTER
    # the task-notification gate above (a wake is not a new
    # turn and must never draw a tally) and wrapped so no
    # failure here can break, delay, or erase a prompt.
    try:
        tally_line, tally_stage = _chat_tally(data, sid)
    except Exception:
        tally_line, tally_stage = None, "error"

    try:
        referenced = _read_referenced(prompt)
    except Exception:
        referenced = []

    # Unique trigger names, case-insensitively deduped, first-seen casing kept.
    # Scanned PER SOURCE —— the prompt, then each referenced file in turn,
    # never a joined blob —— so a fence/backtick span can never straddle the
    # boundary between the prompt and a file it names (module docstring:
    # BACKTICK / FENCE EXEMPTION). The prompt goes first, so a name's first
    # appearance there always wins its displayed casing over a later file.
    seen = {}
    for text in [prompt] + referenced:
        try:
            names = _extract_triggers(text)
        except Exception:
            names = []
        for raw in names:
            seen.setdefault(raw.lower(), raw)

    lines = []
    fired_names = []          # names that actually produced a reminder (logged)
    for raw in seen.values():
        try:
            path = _resolve_trigger(raw)
        except Exception:
            path = None
        if path:
            # Wording is the enforcement here —— see the docstring section WHY
            # THE REMINDER READS AS A MANDATE before softening any of it. The
            # removed hedge ("unless ... intentionally deferred") was the
            # defect: it licensed a silent, self-certified skip.
            lines.append(
                "`#%s` detected —— READ `%s` (root CLAUDE.md §7.3.1–2: a "
                "trigger's protocol file MUST be read, never guessed; reaching "
                "a similar answer by another route does NOT discharge it). "
                "Skip only if already read THIS session. Deferring is allowed "
                "but must be DECLARED in the response, with the reason —— "
                "never taken silently."
                % (raw, path))
            fired_names.append(raw)
        if len(lines) >= _MAX_REMINDERS:
            break

    if not lines and not tally_line:
        # SILENT is a real outcome, not an absence —— logging it is the whole
        # point of §7.7: without this line, "hlint never ran" and "hlint ran and
        # matched nothing" are indistinguishable after the fact.
        _log_event("silent", sid, tally=tally_stage)
        return 0

    # `stage=` keeps naming the TRIGGER half's outcome alone
    # (existing vocabulary, pinned by tests); the tally's own
    # outcome always rides in `tally=`. A `fired:` value here
    # is also the dedup ledger entry —— it must be on disk
    # BEFORE stdout is written, so a crash between the two
    # sides errs towards a suppressed duplicate, never a
    # re-nag loop.
    _log_event("fired" if lines else "silent", sid,
               ",".join(fired_names) or "-", tally=tally_stage)

    parts = []
    if tally_line:
        parts.append(tally_line)     # discipline first, then reminders
    if lines:
        parts.append(_HEADER + "\n" + "\n".join(lines))
    context = "\n".join(parts)
    try:
        sys.stdout.write(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context,
            }
        }))
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
