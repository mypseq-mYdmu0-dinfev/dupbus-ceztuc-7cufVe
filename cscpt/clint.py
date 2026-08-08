#!/usr/bin/env python3
"""Chat-Text Linter (Stop hook)

Logs a chat-text-discipline WARNING when the MAIN agent ends a turn with an
impermissible line. It NEVER blocks the turn (see ALWAYS RED -> ALWAYS YELLOW
in the CCSIM section below for why, and the price of that choice).

Two rules, picked by the session's working directory (see REPO SCOPE below):
* REPO mode (this repo) —— root CLAUDE.md §3.2: the only chat text permitted is
  the 6 declaration lines, and each of the 6 glyphs is OWNED by its own
  declaration type (see DECLARATION CONTRACTS); any other non-blank line is a
  breach. Four exemptions apply (`override`, `yn`, `sic`, `DATS`), plus a lone
  `.` (see DOT ESCAPE) which stays CLEAN rather than merely quieter.
* READER mode (the parent `GitHub/` folder alone) —— that folder's own
  CLAUDE.md mandates ZERO chat text "NO MATTER WHAT", so there every non-blank
  line is a breach, declaration glyphs included; only `override` and that same
  lone `.` are exempt (see DOT ESCAPE for why the dot alone crossed over).

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: a Stop hook scanning the agent's chat text at turn end. NEVER blocks ——
  every verdict exits 0; breaches are logged, never shown.
* PERMITTED: blank lines; a `---`/`***`/`___` divider; each glyph ONLY in its
  own declaration —— I/O glyphs a backticked file list, SHA glyph backticked
  hashes, blocker ≤5 words, sentinel verbatim; plus a lone `.` (both modes).
  Reader folder: blank lines and that lone `.` only.
* Comply regardless: root CLAUDE.md §3.2 mandates declarations-only chat.
* Also RECORDS comms files written via Bash (a PostToolUse-lint bypass);
  hlint advises next prompt.
* Verdicts log to `cscpt/.clint.log`.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
WHY A HOOK, NOT TRUST: the discipline is silent to break and normally caught only
on a human re-read; a deterministic Stop-time scan surfaces the slip at once.

DECLARATION CONTRACTS (glyph ownership —— the core rule): a prefix check alone
was gameable. The agent could satisfy it by CHOOSING A PREFIX rather than by
telling the truth —— real observed abuse: `⚠️ Fleet running; awaiting reports.`,
a progress note wearing the blocker glyph, and `✅ **Hooks are now live** —— dlint
fired and blocked that edit. Reverting the probe…`, a paragraph wearing the
read-declaration glyph. So each of the 6 glyphs is now OWNED by the ONE
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
* `🦈` (§3.2.4, ADDED when the owner split the turn's commit SHAs out of `➡️`
  into a SIXTH declaration class) —— a COMMIT-HASH LIST: an optional single-word
  repo shorthand (`Default:`, `AJAP:`, §3.2.4.5.2) followed by backticked
  abbreviated SHAs, separators only in between. Deliberately NOT folded into the
  I/O shape above, for a reason the I/O rule itself creates: `_io_ok` permits an
  un-backticked tail only inside brackets, so the §3.2.4.5 multi-repo form
  `🦈 Default: `…`` would be judged a prose tail and flagged on every compliant
  multi-repo turn. Two independent tests are applied to each hash, and each pays
  for itself: HEX (`_SHA_TOKEN_RE`), because a git SHA is hex by construction and
  nothing else this glyph may carry is —— that single test is what stops a
  sentence being backticked into place, which is the whole smuggling vector; and
  a LENGTH FLOOR of §3.2.4.3's 8, so a SHORTER abbreviation is flagged. The
  ceiling is deliberately not 8 but a full 40, and that asymmetry is the whole
  point: `git rev-parse --short=8` LENGTHENS its own output when 8 chars are
  ambiguous in that repo, so a hard 8 would flag the correct command's own
  result —— punishing obedience. Short is a real breach and is caught; long is
  git being careful and is not.
  SOLO-LABEL CHECK (`sha_label`) —— the owner's own answer to the cross-line
  objection recorded in the non-goal below, which used to keep this whole rule
  out of reach: §3.2.4.5 sanctions the repo shorthand ONLY when MULTIPLE repos
  were touched, and when the scan window carries exactly ONE `🦈` line then one
  repo was declared BY CONSTRUCTION —— so ANY label on that line is a breach,
  and proving it needs no per-line context at all, only the window's
  `🦈`-line COUNT, which is already in hand where the verdicts are gathered.
  `_flag_solo_sha_label` therefore RECLASSIFIES the window's lone, labelled,
  otherwise shape-valid `🦈` line from clean to `sha_label`, and
  `_line_breach` stays one-line-at-a-time, untouched. Its OWN class,
  deliberately never folded into `sha_shape`: hlint's next-prompt tally names
  the class to the model, and "drop the label" is a different correction from
  "that is not a SHA list" —— one tag per correction, or the tally teaches
  the wrong fix. Precedence, each edge deliberate: a lone line already in
  breach keeps `sha_shape` (the label rides a body that is not a SHA list at
  all, and one line gets one class —— the coarser, truer verdict); 2+ `🦈`
  lines are the legal multi-repo form and are never label-FLAGGED by this
  check, even when a sibling line is separately in breach; REPO mode only
  (§3.2.4 is this repo's protocol, and in READER any chat text is class
  `reader` anyway).
  MISSING-LABEL CHECK (`sha_nolabel`) —— the solo check's exact MIRROR, added
  when the owner ordered the scan reversed: §3.2.4.5.1 mandates that when a
  turn's window carries MULTIPLE `🦈` lines (the multi-repo form —— m2.md's
  mid-turn push declares no `🦈` of its own, its SHA waits for TEA3, so no
  same-repo turn legitimately emits two), EVERY one of them must open with
  its repo shorthand —— a bare line there leaves the reader unable to tell
  WHICH repo a hash belongs to, which is the whole point of the labels. So
  with 2+ `🦈` lines in the window, `_flag_unlabelled_multi_sha` reclassifies
  every bare, otherwise shape-valid one from clean to `sha_nolabel`. Same
  precedence spine as the solo check, count-gated the opposite way: a line
  already in breach keeps its own class (`sha_shape` is the truer verdict);
  0–1 lines are the solo check's territory and this one never runs; REPO
  mode only. Its OWN class for the same reason `sha_label` has one: hlint's
  next-prompt tally names the class, and "add the labels" is a different
  correction from "drop the label" or "that is not a SHA list". THE PANIC
  HAZARD, named so nobody re-words the tally casually: that correction
  arrives at the NEXT turn's start, describing the PREVIOUS turn —— and the
  next turn is usually SINGLE-repo, where adding a label is itself the
  `sha_label` breach. A correction worded as a standing order would convert
  one breach into its mirror image, forever. hlint's `sha_nolabel` rule
  clause therefore carries the CONDITION (labels ONLY on a multi-repo
  turn), and its own suite pins that wording —— see `_TALLY_RULE` there
  before touching either side.
  DELIBERATE NON-GOAL, narrowed by the checks above but kept honest: a
  REDUNDANT second `🦈` line —— the same repo declared twice, e.g. one
  shorthand on two lines —— is still not caught, because two labelled lines
  are byte-identical to the legal §3.2.4.5 form and only the turn's actual
  pushes, which no transcript line records, could tell the two apart. The
  solo case IS caught precisely because it needs no such knowledge.
* `🚨` (§3.2.6) —— the post-compaction sentinel, EXACT wording only, taken
  verbatim from §3.2.6 (`_SENTINEL_CANON`). No bold wrapper, no paraphrase: the
  whole value of a sentinel is that it cannot be approximated, and any other
  text carrying it is by definition not that sentinel.
* `⚠️` (§3.2.5) —— a genuine BLOCKER, "stop & alert", capped three ways:
  `_WARN_MAX_WORDS` (§3.2.5's own ≤5w), `_WARN_MAX_HYPHENS`, `_WARN_MAX_CHARS`,
  tested in that order so the first limit breached is the one reported. The
  hyphen cap exists because words can be skewered together with hyphens to
  smuggle long prose past a WORD count; the character cap is the final safety
  net against the same class of evasion (any other joiner —— en dashes, slashes,
  underscores —— still grows the character count).
  `_WARN_MAX_CHARS = 68` is deliberately documented ONLY here, never in the
  NON-CCSIM block, never in any guide, and never in the user-facing message. A
  limit an agent can SEE is a limit it will spend up to; 5 words should never come
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

ALWAYS RED -> ALWAYS YELLOW (DEMOTION —— READ THIS BEFORE TOUCHING EXIT CODES):
the always-RED policy that used to sit here worked EXACTLY as designed —— it
fired correctly and repeatedly —— and that is precisely what forced its own
reversal. Every fired block cost one extra model turn, and by the DOT ESCAPE
deadlock (below) the agent regularly had nothing new left to say in that extra
turn; in practice it reached for the one concrete thing still on hand, its own
declaration batch, which is exactly the breach being enforced against. The
observed result, repeatedly and across more than one session: repeated
declaration batches, duplicate chapter markers, and increasingly erratic
turn-end behaviour —— the enforcement was making the outcome MEASURABLY WORSE
than the breach it existed to stop. The owner ordered the policy demoted:
every RED block becomes a YELLOW warning, and this file's exit code is now
UNCONDITIONALLY 0. It never blocks a turn again, for any reason.

THE PRICE OF THIS, STATED AS PLAINLY AS POSSIBLE —— and CORRECTED (2026-08-07)
against the Desktop harness binary (2.1.221) itself plus this Mac's own
transcripts: a Stop hook's exit-0 `systemMessage` never reaches the model
(the harness converts it to a `hook_system_message` attachment whose
model-message mapping is EMPTY), and in practice it does not reach the OWNER
either —— it lands in the transcript record and in the harness's terminal
renderer, but the Claude Desktop surface this repo's sessions actually run in
renders no such attachment (none exists in its local resources), and the
owner confirms never seeing one (142 recorded across this project's
transcripts by the audit date, none ever seen). So the warning is an AUDIT
TRAIL —— transcript record plus log —— not a live user alert. Model-reaching
channels at Stop, verified in that same binary: exit 2's stderr (which this
file no longer uses), and —— contrary to hook_guide's channel table —— an
exit-0 `hookSpecificOutput.additionalContext`, which the harness injects as a
"Stop hook additional context" meta message and then RE-INVOKES the model
(the same `stop_hook_blocking` continuation a block uses, capped by
CLAUDE_CODE_STOP_HOOK_BLOCK_CAP, default 8). There is NO channel that reaches
the model at Stop without waking it for another turn —— by construction: the
model has already stopped. additionalContext is deliberately NOT used here:
the injected context is persisted as an ATTACHMENT, never as a `type:"user"`
transcript line, so the SCAN BOUNDARY would not move, and each further Stop
of the same window (task-notification wakes carry FRESH promptIds, defeating
any per-prompt ledger) would find the same breach and re-inject —— the
demotion's deadlock reborn under a friendlier name. CONSEQUENCE, UNDERLINED
SO IT CANNOT BE MISSED: clint corrects the agent NOWHERE, in any
circumstance, for any breach class; enforcement rests on root CLAUDE.md
§3.1.6's TEAs. This is a DELIBERATE TRADE, not an oversight —— anyone tempted
to "restore the block", or to reach the model via additionalContext instead,
MUST read this paragraph first, because either unknowingly reintroduces the
exact deadlock this demotion was ordered to end.

WHAT SURVIVES, UNCHANGED: every detection rule below (glyph ownership, the
caps, the sentinel, Reader mode) still runs in full, every exemption still
exempts, and every breach still logs its own granular class (see LOG EVERY
STAGE) —— the log is now the PRIMARY artefact, not a secondary trail behind a
block, so it must lose none of the detail it already had.

EXEMPTIONS. All read the USER'S TYPED MESSAGE —— the last GENUINE user line
(`_is_real_user`, which already excludes tool_results and the system-injected
wrappers), never a `query_` file's contents: this script opens no file but the
transcript, so an override token sitting inside a comms file can never arm one
of these. `override` applies in BOTH modes; the other three are REPO mode only,
because they come from THIS repo's protocols, which the Reader folder does not
share, and the Reader's own rule admits no exception (bar the lone `.`, a
separate and earlier check —— see DOT ESCAPE —— which is not one of these four
and which now crosses into READER mode too, for reasons that have nothing to
do with any of the four below):
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
  exemption unusable. Over-cap is NOT exempt and stays a breach, logged
  distinctly (`yellow:sic_overrun`) so an over-long "answer" is auditable
  rather than indistinguishable from ordinary prose.
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

DOT ESCAPE: root CLAUDE.md §3.1.8.2 (the Harness Nudge; it was §3.1.6.2 when
this paragraph was written, and the section has since been renumbered TWICE ——
§3.1.6.2 is now TEA2, chapter marking, so the old pointer sent a reader to
entirely the wrong rule) sanctions a lone `.` and nothing else —— written in direct
response to a deadlock the OLD always-RED policy created (see ALWAYS RED ->
ALWAYS YELLOW above for the full history: a block forcing one more model turn
with nothing new left to declare, resolved in practice by re-emitting the
declaration batch —— exactly the breach being enforced against, observed three
times in one turn and in another session too). Demotion removes clint's own
half of that deadlock outright: a REPO turn is never blocked by this file
again, so this file can no longer force the extra turn that had nothing left
to say. This recognition logic is KEPT anyway, for two independent reasons:

1. OTHER Stop hooks in this repo (present or future) may still block, and the
   sanctioned reply protocol prescribes for THAT deadlock is this same lone
   `.` —— clint must not itself misclassify that legitimate, protocol-mandated
   reply as an ordinary prose breach. A wrong block is no longer the risk, but
   a false `yellow:prose` still is: the log is the primary artefact now (see
   LOG EVERY STAGE), and a polluted audit trail is a real cost, not a
   cosmetic one.
2. READER MODE, NEWLY (Change 2, unrelated to the deadlock entirely): the
   owner has a standing, concrete need to send the Reader session a lone `.`
   and have her reply in kind, purely to open a session-limit window —— no
   work done, nothing read, nothing written. `universal/glossary.md` and the
   `GitHub/` CLAUDE.md both already mandate exactly this reply as the
   sanctioned response to a lone `.` from the user. Before this change, Reader
   mode flagged EVERY non-blank line with no exception but `override`, so the
   very reply that folder's OWN protocol requires was itself flagged —— that
   was always a bug, not a feature: the strict zero-text rule was written to
   catch UNSANCTIONED chat prose, never to make a protocol-SANCTIONED reply
   impossible to give.

MATCHING RULE (`_lone_dot_turn`), deliberately narrow and IDENTICAL in both
modes: every non-blank line the assistant produced since the triggering user
message —— across every text block, not only the ones already flagged as
breaches —— must total to EXACTLY one line, and that line must strip to
EXACTLY one full stop. Consequences, each intended: `..`/`...` fail (not one
full stop); `. ` plus more text on the same line fails (not exactly a full
stop); and a `.` sharing the turn with ANY other non-blank line —— even a
well-formed declaration that would pass fine on its own —— still fails,
because checking only the already-flagged `offending` lines would let a real
declaration batch ride alongside a decorative "." and pass; checking EVERY
non-blank line closes that door. A bold-wrapped `**.**` fails too: §3.1.6's
bold wrapper is tolerated for a GLYPH line elsewhere in this file, but the dot
carries no glyph and the rule text says only "optionally surrounded by
whitespace" —— widening tolerance further was never asked for and would only
widen the token's shape, the opposite of what a minimal escape hatch should
do.

BOTH MODES, NOW (Change 2 widened this from REPO-only): the reasoning that
originally kept this REPO-only does not carry over, because READER's need for
the escape is a DIFFERENT need entirely, not the deadlock's twin. REPO's dot
used to cost nothing extra because the real content already reached a
`response_` file before any block landed; that argument cannot apply to
READER, which creates no files at all. But READER's lone-`.` requirement was
never about salvaging swallowed content in the first place —— the user's lone
`.` and the mandated `.` reply ARE the entire, complete, deliberate exchange;
there is no other content being redirected anywhere. So "does this session
have somewhere to put swallowed content?" was always the wrong question for
READER's case, and answering it "no" was never a real reason to keep flagging
a reply that protocol positively requires. The two modes log under DISTINCT
tags precisely because the justification differs (`clean:dot` vs
`clean:dot_reader`) even though the matching rule above is byte-for-byte
identical —— see LOG EVERY STAGE.

SENTINEL LISTS (root §5.3–§5.4; REPO mode only): a turn carrying the EXACT
§3.2.6 sentinel owes the user two further chat artefacts by that same root
protocol —— §5.3's "non-#numbered list" of still-useful reads and §5.4's list
of the remainder, bullet lines per §5.3's own example. mlint (SHAPE C ——
hook_guide §6.9.9) BLOCKS the turn until precisely this output exists, so
before this escape the suite mandated and forbade the SAME lines: every real
compaction logged a false `yellow:prose` (live: a fully §5-compliant response
logged 17 offending lines), polluting the log —— the PRIMARY artefact ——
exactly as the DOT ESCAPE's first rationale warns against. So, when the scan
window CONTAINS the exact canon (deliberately not "starts with": a §3.1.8 dot
reply from an earlier wake legitimately precedes it in a multi-notification
window), two shapes are re-sanctioned, and ONLY out of the `prose` class:
* a line starting `- ` —— a §5.3-shape list item;
* a line ending `:` whose NEXT non-blank line is such an item —— the header
  that makes §5.3's list tellable from §5.4's.
Everything else keeps its verdict: glyph misuse stays its own class, a free
paragraph still flags, and READER mode is untouched (its class is `reader`,
never `prose`, and §5 is this repo's protocol, not that folder's). If nothing
else offends, the turn logs `clean:compaction` —— its own tag, so a genuine
compaction stays auditable rather than silent. TRUST MODEL, STATED HONESTLY
—— weaker than the dot's: the sentinel is AGENT-authored, so an agent could
forge one and bullet-ify prose beneath it. Accepted, for two reasons: the
forgery is the loudest possible lie (a "Compaction Detected" banner the user
falsifies at a glance), whereas the alternative is a GUARANTEED false breach
on every genuine compaction; and a linter cannot verify a claim, only its
form —— the same trade the ⚠️ IS NOT A PROGRESS NOTE paragraph already
documents.

BASH-WRITE CATCH (`bashw=`; REPO mode only) —— a SECOND job this Stop scan
performs on the window it already parsed, closing a hole the PostToolUse
suite structurally cannot: every content lint (nlint, dlint's gate, flint,
tlint) is registered on Write|Edit|MultiEdit, so a comms file written or
edited THROUGH A BASH COMMAND —— a `python3` heredoc, a `>` redirect, `tee`,
`sed -i` —— is never seen by any of them. Not theory: a real turn appended
eleven numbered sub-points to a live `response_` via a `python3 - <<'PY'`
heredoc (`open(path, "w")`), sailed past nlint's tenth-sibling rule, and the
breach surfaced only when the OWNER read the file —— he then blamed nlint,
whose rule was in fact correct and fires when shown the file; the lint was
bypassed, not broken. A NOT-NOTICED failure is an enforcement gap prose
cannot repair, so the catch is mechanical:
* WHERE IT LIVES, weighed not defaulted: a PreToolUse(Bash) guard was the
  alternative, and it loses on every axis —— it needs NEW settings wiring
  (this file is already a registered Stop hook), it taxes EVERY Bash call
  with a subprocess spawn to protect the rare offender, and at pre-time the
  write has not happened yet, so it can only guess intent from command text;
  at Stop the file's own mtime can CONFIRM a modification actually landed.
* DETECTION, two independent gates so legitimate Bash never fires it:
  (1) TEXT —— the window's Bash `tool_use` commands are scanned for `.md`
  tokens that live under `sessions/` (or carry a comms basename, resolved to
  its TS-derived month folder exactly as root §3.4.9.1–2 prescribes) AND a
  write signal in the same command: a `>`/`>>` redirect aimed at that token,
  `tee`, `sed`/`perl` in-place, a write/append-mode `open(`, or
  `write_text(`. Plain reads (`cat`, `grep`), `git` operations, and lint
  invocations carry no such signal and never reach gate 2. `mv`/`cp`/`touch`
  are EXCLUDED deliberately: the Move/Void Rules (root §8.1–8.2) and
  `set_dates.py` make those routine, legitimate comms-file Bash uses, and
  their content was already linted when first written —— flagging them would
  make the catch wallpaper. (2) MTIME —— the named file must exist and have
  been modified since the turn's triggering user message (the transcript
  line's own `timestamp`, minus a small clock-skew slack); a command that
  merely MENTIONS a write shape but changed nothing (failed assert, dry run)
  is suppressed, as is a token whose file cannot be found. When the trigger
  timestamp itself is unreadable the text verdict stands alone —— the armed
  direction, same as every other fail-open here.
* DELIVERY, and why this file writes NO message for it: at Stop nothing
  reaches the model without waking it (THE PRICE OF THIS, above), so the
  catch only RECORDS —— the log line's `bashw=` field carries the offending
  basename(s), and hlint's UserPromptSubmit half reads it at the NEXT prompt
  and injects the advisory exactly as its chat-discipline tally does,
  dedup-ledgered the same way. The field rides EVERY post-scan verdict ——
  clean, exempt, yellow alike —— because the bypass is orthogonal to chat
  discipline: a chat-exempt turn (`override`, `yn`) can still have written
  an unlinted comms file, and the exemptions govern CHAT text, not lint
  coverage. ADVISORY ONLY, by construction: this file's exit code stays
  unconditionally 0 and the field changes no verdict.
* RESIDUALS, stated rather than papered over: a sub-agent's Bash writes ride
  sidechain lines this scan already excludes (the SA's own hooks saw its
  tool calls); content smuggled through `cp`/`mv` from outside `sessions/`
  is unseen (excluded above, trade accepted); a write whose file is MOVED
  later in the same turn stats stale and is suppressed. Each is the quiet
  direction on purpose —— this catch must never fire on legitimate Bash use,
  and a rare miss still beats the guaranteed miss that existed before it.
* Root scope: resolves `sessions/`-relative and bare comms basenames against
  THIS repo's root alone (derived from `__file__`, never cwd) —— the only
  tree whose comms conventions these lints police; other repos' files never
  resolve and so never fire.
* COST, measured end-to-end on this Mac (40-run medians, same fixture both
  sides: a 60-message transcript carrying 20 Bash tool_use blocks, live-sized
  log): 28.7 ms -> 30.8 ms, i.e. ≈2 ms on a Stop event against a 1 s budget
  (p90 29.8 -> 31.7 ms); the scan is bounded by `_BASHW_MAX_CMDS`/`_TOKENS`
  and stats at most a handful of paths.

LOOP GUARD —— REMOVED (justified, not merely deleted): the guard used to exist
SOLELY to stop an infinite retry cascade that only exit 2 could cause —— a
block forces one more model turn, that turn ends in another Stop, and an
unguarded block-on-every-breach would fire again forever. Demotion (ALWAYS RED
-> ALWAYS YELLOW, above) deletes the ROOT CAUSE outright: this file's exit
code is now unconditionally 0, so it can never itself force a continuation,
and a mechanism that exists only to stop a loop THIS FILE could cause is
provably inert once this file can no longer cause that loop.

Kept-vs-removed was a real decision, not a default: an argument FOR keeping it
existed —— some OTHER Stop hook in this repo might still block, and the
resulting forced continuation could in principle carry fresh clint-detectable
prose that the old guard would have suppressed under an opaque `loop_guard`
tag. REMOVED anyway, because that suppression was never a benefit on its own
terms: under ALWAYS YELLOW every breach is meant to log its true granular
class (the log is the primary artefact now —— see LOG EVERY STAGE), and hiding
a real breach behind `loop_guard` —— for a loop this file cannot itself cause
any more —— would only make that audit trail LESS informative for zero safety
benefit. Simpler code, a more honest log, nothing left uncovered: removing it
is the correct call, not merely the convenient one.

`_is_stop_feedback`, `_STOP_FEEDBACK_PREFIX`, and the `stop_hook_active`
payload field are gone from this file along with it. The SCAN BOUNDARY
behaviour that used to share context with the guard —— treating a
harness-injected "Stop hook feedback:" line as a genuine boundary-mover —— is
UNCHANGED and never depended on the guard's existence; see `_is_real_user`'s
docstring.

GLYPH-FREE, CLASS-FREE, NUMBER-FREE MESSAGE (was GLYPH-FREE STDERR): under the
retired RED policy this message reached the MODEL via stderr, so naming a
glyph, a breach class, or a numeric limit would have taught the agent exactly
which prefixes/shapes pass and invited gaming. Under ALWAYS YELLOW the message
reaches only user-side surfaces —— and on the owner's actual Desktop surface,
none render it (see THE PRICE OF THIS) —— so that specific
hazard is gone —— but the constraint is KEPT anyway, unchanged, as cheap
insurance: it costs nothing to keep the user-facing text free of exploitable
detail, and it stays correct automatically if this channel's model-isolation
is ever wrong, or if this code is ever copied into a hook shape where exit-0
output is NOT model-isolated. The precise class stays recorded in the log,
which is where granular detail belongs either way.

AUDIT NOTE, NOT A CORRECTION (was REDIRECT, NOT ONLY REFUSAL): under the
retired RED policy a hard block risked swallowing content the agent meant to
say —— it was told to stop, and did, without ever getting the point out, so the
REPO message named where that content belonged (`response_`) as a genuine
remedy the agent could act on before ending its turn. That corrective value is
gone now that this message reaches only the user: the agent never reads it and
cannot act on it (see ALWAYS RED -> ALWAYS YELLOW). What survives is a
courtesy to the HUMAN reading it afterwards —— a hint of where to look if
something seems to have gone missing. The REPO message keeps that hint; the
READER message does not, because that session creates no files at all, so
there is nothing for even a human to go check —— there, the message's whole
job is to say plainly that a rule was broken and nothing more.

LOG EVERY STAGE: a breach-only log cannot tell "ran this turn and found
nothing" apart from "the harness never invoked this command" —— an empty log fits
BOTH, which is exactly how dead Stop-hook wiring went unnoticed across many real
sessions whilst the script itself was provably correct under manual invocation.
Leakage stays minimal: a breach line logs only the offending text, every other
stage logs no user content at all. The logged text may itself carry a glyph in
EITHER mode —— in READER mode a declaration line is the breach, and under glyph
ownership a REPO breach is often a MISUSED glyph (this was untrue of the older
prefix-only check, which could only ever log glyph-free lines). That is fine:
the log is read by a human, and it is the exit-0 `systemMessage` reaching the
USER that stays glyph-free (kept as cheap insurance now that the model never
reads any of this either —— see GLYPH-FREE, CLASS-FREE, NUMBER-FREE MESSAGE).

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
Reader; delete the two READER branches to revert to repo-only policing. One
deliberate, narrow exception to READER's zero-text rule exists on top of this:
the lone-`.` reply (see DOT ESCAPE), carved in for a real, unrelated business
need and logged under its own `clean:dot_reader` tag rather than silently
folded into READER's ordinary silence.

WIRING (kept here, not in NON-CCSIM: a caller never invokes this file, so the
plumbing is dead weight to everyone but an editor). Registered as a `Stop` hook
in the USER-level `~/.claude/settings.json` —— the Claude Desktop app executes
user-level hooks and silently ignores project-level ones —— hence it fires in
every project and must self-scope. IN: Stop-hook JSON on stdin
(`transcript_path`, `cwd`, `session_id`); OUT: nothing at all on a clean turn,
or `{"systemMessage": "..."}` JSON on stdout for a demoted breach (a user-side
record only, never the model —— see THE PRICE OF THIS). EXIT is UNCONDITIONALLY 0 ——
clean, exempt, out-of-scope, a demoted breach, or ANY failure, all alike; this
file never again returns 2 for any reason. FAIL-SAFE: a bad payload, an
unreadable transcript, or a failed message/log write all exit 0 regardless, so
the hook can never break a turn on its own failure —— true before this change
and mechanically guaranteed now.

LOG FORMAT: exactly ONE tab-delimited line per invocation whatever the verdict,
each carrying `mode=` (which rule applied) and `pid=` (the prompt it belongs
to), so one `grep` shows every invocation for a prompt and why it was judged so.
Actions: `clean` and its `clean:dot`/`clean:dot_reader` variants (see docstring
DOT ESCAPE) plus `clean:compaction` (see SENTINEL LISTS); `out_of_scope`;
`message_failed` (the exit-0 warning write itself
failed); the parse stage reached; one `exempt:` per exemption
(`exempt:override`, `exempt:yn`, `exempt:sic`, `exempt:dats`); and one
`yellow:` per breach CLASS —— `yellow:prose` (no glyph at all),
`yellow:io_shape` (an I/O glyph not carrying a file list), `yellow:sha_shape`
(the SHA glyph not carrying a backticked hex commit-hash list),
`yellow:sha_label` (the window's LONE SHA line wearing a repo shorthand ——
one `🦈` line means one repo, so the label is unearned; see SOLO-LABEL
CHECK), `yellow:sha_nolabel` (a bare SHA line amongst the window's MULTIPLE
`🦈` lines —— the multi-repo form owes every line its shorthand; see
MISSING-LABEL CHECK), `yellow:sentinel`
(compaction glyph, wrong wording), `yellow:warn_shape` (blocker glyph carrying
another type's declaration), `yellow:warn_empty`, `yellow:warn_words`,
`yellow:warn_hyphens`, `yellow:warn_chars`, `yellow:warn_progress` (a progress
note wearing the blocker glyph), `yellow:reader` (any chat text in Reader
mode), plus `yellow:sic_overrun` (a `sic` answer past its cap). Every
post-scan record additionally carries `bashw=` —— `-` normally, else the
basename(s) of comms files this turn wrote via Bash (see BASH-WRITE CATCH);
it rides clean and exempt verdicts too, because the bypass it records is
orthogonal to the chat verdict, and hlint reads it at the next prompt. The
field sits BEFORE `first=` so that free-text field stays last. The class is
that of the FIRST offending line, matching the `first=` field, so record and
class always describe the same text —— this naming and granularity are
UNCHANGED from the retired RED policy (only the `block:` prefix became
`yellow:`), because the log is now the PRIMARY artefact and must lose none of
the detail it already had. A log that does NOT grow across real turns means
the harness is not calling this hook at all —— the diagnostic the LOG EVERY
STAGE rationale above exists to enable. `CLINT_LOG=<path>` redirects it, so a
test run neither reads nor pollutes the real log.

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
import io
import select
import stat
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
_GLYPHS = ("✅", "⇠", "➡", "\U0001f988", "⚠", "\U0001f6a8")  # ✅ ⇠ ➡ 🦈 ⚠ 🚨
_VS16 = "️"                 # the emoji variation selector, stripped before matching

# Each glyph's OWNER declaration type (root CLAUDE.md §3.2; see docstring
# DECLARATION CONTRACTS). `_IO_GLYPHS` = the three I/O declarations §3.2.1–3,
# which share one shape: a list of backticked file paths.
_IO_GLYPHS = ("✅", "⇠", "➡")
_G_SHA = "\U0001f988"            # §3.2.4 commit-SHA declaration
_G_WARN = "⚠"                    # §3.2.5 blocker
_G_SENTINEL = "\U0001f6a8"       # §3.2.6 post-compaction sentinel

# §3.2.6's wording, copied VERBATIM from root CLAUDE.md —— a sentinel that may be
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

# --- SHA declaration shape (§3.2.4) ---------------------------------------
# An optional repo shorthand opening the line: `Default:` / `AJAP:`
# (§3.2.4.5.2). ONE word, so it cannot become a sentence; the colon and the
# following space are what mark it as a label rather than a stray hash.
_SHA_LABEL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,23}:\s+")
# One abbreviated commit hash. HEX is the load-bearing half —— it is what stops
# prose being backticked into place. The FLOOR is §3.2.4.3's 8; the CEILING is
# open to a full 40 because `git rev-parse --short=8` lengthens its OWN output
# on an ambiguous prefix, and flagging a correct command's result would be the
# worse error (see docstring DECLARATION CONTRACTS).
_SHA_TOKEN_RE = re.compile(r"^[0-9a-fA-F]{8,40}$")
# What may remain between the hashes: separators only, exactly as for I/O.
_SHA_RESIDUE_RE = re.compile(r"^[\s,;·|&+]*$")

# --- Blocker declaration caps (§3.2.5) ------------------------------------
_WARN_MAX_WORDS = 5              # §3.2.5's own "≤5w"
_WARN_MAX_HYPHENS = 3            # hyphens can skewer words past a WORD count
# Final safety net against the same evasion. Its VALUE is documented in the
# CCSIM block only, never in NON-CCSIM, any guide, or the user-facing message:
# a limit an agent can see is a limit it will spend up to.
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

# Fixed, GLYPH-FREE WARNING messages shown to the USER ONLY via an exit-0
# `systemMessage` (see docstring GLYPH-FREE, CLASS-FREE, NUMBER-FREE MESSAGE ——
# must not name the glyphs, quote any numeric limit, or name the breach class).
# These NEVER reach the model (ALWAYS RED -> ALWAYS YELLOW), so they read as a
# WARNING about what already happened, never as an instruction telling the
# (absent) recipient what to do next. One per mode, because "this session owes
# ZERO chat text" would be actively wrong framing for the other mode, and only
# the REPO message keeps the courtesy hint of where lost content might belong
# (docstring AUDIT NOTE, NOT A CORRECTION) —— READER creates no files, so it
# has nothing to hint at.
_BREACH = {
    MODE_REPO: ("WARNING (root CLAUDE.md §3.2): this turn's chat text was not "
                "a clean declaration batch —— either prose with no declaration "
                "glyph, or a glyph carrying content outside its own type. "
                "Logged only; clint no longer blocks the turn or reaches the "
                "agent. If real content was lost, it may still need to land "
                "in this turn's `response_` file."),
    MODE_READER: ("WARNING (GitHub/ CLAUDE.md): this session emitted chat "
                  "text where the rule is ZERO, always. Logged only; clint "
                  "no longer blocks the turn or reaches the agent."),
}

# Known system-injected wrapper tags Claude Code appends as `type: "user"`
# turns (notifications/command echoes) even though no human typed them —
# see `_is_real_user`. Exact prefix match only, never substring, so real
# human prose that merely mentions these words is unaffected.
_SYSTEM_INJECTED_TAGS = (
    "<task-notification>", "<local-command-caveat>",
    "<local-command-stdout>", "<command-name>", "<command-message>",
    "<command-args>")

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


def _sha_ok(rest):
    """True if `rest` is a well-formed SHA declaration body (§3.2.4): an
    optional one-word repo shorthand, then backticked abbreviated commit
    hashes separated by punctuation and nothing else.

    Method: drop the label if present, then require at least one backticked
    span, every span to be a hex hash of git-abbreviation length, and whatever
    sits between them to be separators only. Kept SEPARATE from `_io_ok`
    because that function would reject the §3.2.4.5 multi-repo form's label as
    an un-bracketed prose tail —— see docstring DECLARATION CONTRACTS for why
    the hex test, not the length, is what does the real work here."""
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
    if "`" in residue:                   # unbalanced backtick -> not a clean list
        return False
    return bool(_SHA_RESIDUE_RE.match(residue))


def _flag_solo_sha_label(judged):
    """Reclassify the window's LONE, labelled, otherwise shape-valid `🦈`
    line from clean to `sha_label`, in place. No-op in every other case.

    Root §3.2.4.5 sanctions the repo shorthand ONLY when multiple repos were
    touched —— and that form is multiple `🦈` lines, one per repo. So exactly
    ONE `🦈` line in the window means one repo BY CONSTRUCTION, and any label
    on it is a breach. This is the owner's answer to the old cross-line
    objection (see docstring SOLO-LABEL CHECK): nothing is threaded through
    `_line_breach`, which stays one-line-at-a-time; the ONLY turn-level fact
    used is the `🦈`-line count, read here where the window's verdicts
    already sit. Precedence: a line already in breach keeps its own class
    (`sha_shape` is the truer verdict when the body is not a SHA list at
    all); 2+ lines are the legal multi-repo form and are never touched, even
    when a sibling line is separately in breach. The CALLER gates on REPO
    mode —— §3.2.4 is this repo's protocol, and READER flags all chat text
    as `reader` regardless. Runs BEFORE the offending/classes split so the
    verdict, `lines=` and `first=` all describe the reclassified line."""
    idx = [i for i, (s, k) in enumerate(judged)
           if _split_glyph(s)[0] == _G_SHA]
    if len(idx) != 1:
        return
    s, k = judged[idx[0]]
    if k is not None:
        return                           # own breach class already stands
    _, rest = _split_glyph(s)
    if _SHA_LABEL_RE.match(rest):
        judged[idx[0]] = (s, "sha_label")


def _flag_unlabelled_multi_sha(judged):
    """Reclassify every BARE, otherwise shape-valid `🦈` line from clean to
    `sha_nolabel`, in place, when the window carries TWO OR MORE `🦈` lines.
    No-op with 0–1 lines —— that territory belongs to `_flag_solo_sha_label`.

    The solo check's exact mirror (see docstring MISSING-LABEL CHECK): root
    §3.2.4.5.1 makes multiple `🦈` lines the multi-repo form, and there EVERY
    line owes its repo shorthand —— a bare line leaves its hashes un-owned.
    Same precedence spine, count-gated the other way: a line already in
    breach keeps its own class (the coarser, truer verdict —— one line, one
    class), and only shape-valid bare lines are touched, so the legal fully
    labelled form passes through untouched even when a sibling line is
    separately in breach. The CALLER gates on REPO mode, exactly as for the
    solo check."""
    idx = [i for i, (s, k) in enumerate(judged)
           if _split_glyph(s)[0] == _G_SHA]
    if len(idx) < 2:
        return
    for i in idx:
        s, k = judged[i]
        if k is not None:
            continue                     # own breach class already stands
        _, rest = _split_glyph(s)
        if not _SHA_LABEL_RE.match(rest):
            judged[i] = (s, "sha_nolabel")


def _warn_breach(rest):
    """Breach class for a `⚠️` line's body, or None if it is a permitted
    blocker declaration (§3.2.5). Caps are tested words -> hyphens -> chars so
    the FIRST limit breached is the one recorded."""
    if not rest:
        return "warn_empty"              # a glyph declaring nothing
    if _io_ok(rest) or _sha_ok(rest) or rest == _SENTINEL_BODY:
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
    if g == _G_SHA:
        return None if _sha_ok(rest) else "sha_shape"
    if g == _G_SENTINEL:
        # EXACT §3.2.6 wording only, measured on the raw line: not even a bold
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
    twice). This repo used to also recognise that exact line separately, as
    loop-guard signal (b); that guard is gone (see docstring LOOP GUARD ——
    REMOVED) because nothing this file does can force a continuation any
    more, but the boundary point made here stands regardless of that
    history."""
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


def _lone_dot_turn(all_lines):
    """True if the WHOLE turn's non-blank content is a single line reading
    exactly one full stop (whitespace-trimmed) —— root CLAUDE.md §3.1.8.2's
    sanctioned no-op reply, recognised in BOTH REPO and READER mode (see
    docstring DOT ESCAPE for the two independent reasons why, and for why the
    match is this narrow). `all_lines` already holds every non-blank line
    stripped, so plain equality enforces "exactly one full stop, optionally
    surrounded by whitespace" and rejects `..`, `...`, `. text`, and a `.`
    sharing the turn with any other line, declaration or not. The CALLER
    still tags the two modes distinctly (`clean:dot` vs `clean:dot_reader`);
    this function only answers the shape question."""
    return len(all_lines) == 1 and all_lines[0] == "."


def _sentinel_list_line(judged, i):
    """True if judged[i] is one of the two §5.3–§5.4 shapes the SENTINEL
    LISTS escape re-sanctions (see docstring): a `- `-led list item, or a
    `:`-terminated header whose NEXT non-blank line is such an item. The
    CALLER guarantees the window carries the exact sentinel and that
    judged[i] is class `prose`; adjacency works on `judged` itself because
    blank lines were never admitted into it."""
    s = judged[i][0]
    if s.startswith("- "):
        return True
    return (s.endswith(":") and i + 1 < len(judged)
            and judged[i + 1][0].startswith("- "))


# --- BASH-WRITE CATCH (docstring section of that name) ---------------------
# A quoted `.md` path (may carry spaces —— this repo's own absolute prefix
# does) and a bare whitespace-free `.md` token, hlint's own token convention.
_BASHW_MD_QUOTED_RE = re.compile(r"[\"']([^\"'\n]*?\.md)[\"']")
_BASHW_MD_TOKEN_RE = re.compile(r"[^\s\"'`()<>|,;=]+\.md")
# A comms basename (root §3.3.1–7): optional prefix segments, a known comms
# type, a 12-digit TS, an optional disambiguating letter. Matched on the
# BASENAME so `sessions/`-external mentions resolve (and mostly stat-fail).
_BASHW_COMMS_NAME_RE = re.compile(
    r"(?:^|_)(?:query|response|close|wrap|artefact|slog)_\d{12}[a-z]?\.md$",
    re.I)
# The TS's year+month —— the file's §3.4.9.1–2 folder is COMPUTED from it,
# exactly as hlint's corpus expansion does, so no `sessions/` walk ever runs.
_BASHW_TS_RE = re.compile(r"_(\d{4})(\d{2})\d{6}[a-z]?\.md$", re.I)
# Command-wide write signals. `tee` (word, not `.tee`), `sed`/`perl` wearing
# an in-place flag, a write/append/update-mode `open(`, or `write_text(`.
# Bare `.write(` is NOT a signal on its own —— `sys.stdout.write` rides many
# read-only verification heredocs —— and `mv`/`cp`/`touch` are excluded
# outright (Move/Void Rules + `set_dates.py`; see docstring, DETECTION).
_BASHW_TEE_RE = re.compile(r"(?<![\w.])tee(?:\s|$)")
# `-i` may ride a cluster (`perl -pi`, `sed -Ei`), so up to two flag letters
# may precede the `i`; the trailing \b keeps `-in`/`--include` unmatched;
# and the scan stops at a pipe so `sed … | grep -i` cannot borrow grep's
# flag and read as an in-place edit.
_BASHW_INPLACE_RE = re.compile(
    r"\b(?:sed|perl)\b[^\n|]{0,120}?\s-[A-Za-z]{0,2}i\b")
_BASHW_PYWRITE_RE = re.compile(
    r"\bopen\s*\([^)\n]*[\"'](?:[wax]|[rwa]\+|[wa][bt])[\"']"
    r"|\.write_text\s*\(")
_BASHW_SLACK_S = 120                 # clock-skew slack on the mtime gate
_BASHW_MAX_NAMES = 3                 # basenames named in the log field
_BASHW_MAX_CMDS = 200                # bound the scan on a pathological turn
_BASHW_MAX_TOKENS = 20               # ditto per command


def _redirected_into(cmd, tok):
    """True when some occurrence of `tok` in `cmd` sits directly after a
    shell redirect —— `> tok`, `>> tok`, `>"tok"` —— skipping only quotes and
    whitespace on the way back, so `2>&1` or a redirect aimed elsewhere in
    the same command never counts for this token."""
    for m in re.finditer(re.escape(tok), cmd):
        k = m.start() - 1
        while k >= 0 and cmd[k] in " \t\"'":
            k -= 1
        if k >= 0 and cmd[k] == ">":
            return True
    return False


def _bashw_resolve(tok):
    """Candidate absolute path(s) for a `.md` token found in a Bash command:
    an absolute token as-is; a token carrying a `sessions/` component
    re-anchored on THIS repo's root at that component (which also repairs a
    token truncated at the space inside this repo's own absolute prefix); a
    bare comms basename mapped to its TS-derived month folder, then one
    month back (root §3.4.9.1–2) —— two stats, never a walk. Anything else
    resolves to nothing and so can never fire."""
    if os.path.isabs(tok):
        return [tok]
    i = tok.find("sessions/")
    if i != -1:
        return [os.path.join(_REPO_ROOT_REAL, tok[i:])]
    base = os.path.basename(tok)
    m = _BASHW_TS_RE.search(base)
    if not m:
        return []
    y, mo = int(m.group(1)), int(m.group(2))
    if not 1 <= mo <= 12:
        return []
    py, pm = (y, mo - 1) if mo > 1 else (y - 1, 12)
    return [os.path.join(_REPO_ROOT_REAL, "sessions", "%04d" % yy,
                         "%04d%02d" % (yy, mm), base)
            for yy, mm in ((y, mo), (py, pm))]


def _bashw_epoch(trigger):
    """The turn-opening user line's timestamp as an epoch float, or None when
    unreadable —— the mtime gate then stands down and the text verdict rules
    alone (the armed direction; see docstring, DETECTION gate 2)."""
    try:
        ts = (trigger or {}).get("timestamp")
        if not isinstance(ts, str) or not ts:
            return None
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def _bash_comms_writes(cmds, trigger):
    """The `bashw=` log-field value —— comma-joined basenames of comms files
    the window's Bash commands wrote (capped, `,+N` for overflow) —— or None
    when nothing fired. Both detection gates and every deliberate exclusion
    are specified in the docstring's BASH-WRITE CATCH section; this body is
    mechanics only. Never raises: the catch is a recorder, and a failure in
    it must cost a diagnostic, never a verdict or the turn."""
    try:
        start = _bashw_epoch(trigger)
        names = []
        for cmd in cmds[:_BASHW_MAX_CMDS]:
            toks = set(_BASHW_MD_QUOTED_RE.findall(cmd))
            toks.update(_BASHW_MD_TOKEN_RE.findall(cmd))
            cands = sorted(
                t for t in toks
                if "sessions/" in t
                or _BASHW_COMMS_NAME_RE.search(os.path.basename(t)))
            if not cands:
                continue
            wide = (_BASHW_TEE_RE.search(cmd)
                    or _BASHW_INPLACE_RE.search(cmd)
                    or _BASHW_PYWRITE_RE.search(cmd))
            for tok in cands[:_BASHW_MAX_TOKENS]:
                if not wide and not _redirected_into(cmd, tok):
                    continue
                for path in _bashw_resolve(tok):
                    try:
                        st = os.stat(path)
                    except OSError:
                        continue         # absent/moved -> quiet direction
                    if (start is not None
                            and st.st_mtime < start - _BASHW_SLACK_S):
                        continue         # untouched this turn -> mentioned only
                    base = os.path.basename(path)
                    if base not in names:
                        names.append(base)
                    break
        if not names:
            return None
        shown = ",".join(names[:_BASHW_MAX_NAMES])
        if len(names) > _BASHW_MAX_NAMES:
            shown += ",+%d" % (len(names) - _BASHW_MAX_NAMES)
        return shown
    except Exception:
        return None


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


def _log_event(sid, action, lines=0, first="-", pid="-", mode="-", bashw="-"):
    """Append ONE terse diagnostic line for ANY hook invocation, breach or not
    (see docstring LOG EVERY STAGE).

    Fields are TAB-separated and `first=` stays LAST because it alone may carry
    free text (tabs/newlines in it are flattened, so a record is always exactly
    one line). `mode=` records which rule applied, so a `reader:`-policed block
    is never mistaken for a repo one when auditing. `bashw=` (BASH-WRITE
    CATCH) sits just before `first=` and is flattened the same way —— hlint
    parses it back at the next prompt, the one field here that anything
    machine-reads.

    FAIL-SAFE: swallow all errors -- a logging failure must never break a turn
    (same contract as the rest of this file). Nothing else reads this log
    back, so a lost write costs diagnostics only, never enforcement (a lost
    `bashw=` value costs one missed advisory, the same quiet direction)."""
    try:
        with open(_LOG, "a", encoding="utf-8") as lf:
            lf.write(
                "%s\tsession=%s\tpid=%s\tmode=%s\taction=%s\tlines=%d"
                "\tbashw=%s\tfirst=%s\n"
                % (datetime.now().isoformat(timespec="seconds"),
                   sid, pid, mode, action, lines,
                   str(bashw)[:200].replace("\t", " ").replace("\n", " "),
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
    '  printf \'%s\' \'{"hook_event_name":"Stop",'
    '"transcript_path":"/abs/session.jsonl"}\' \\\n'
    '    | python3 cscpt/clint.py\n'
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
    # That same message is kept, because it decides the `yn` exemption (and,
    # historically, loop-guard signal (b) —— removed, see docstring LOOP GUARD
    # —— REMOVED; the boundary logic itself needed no change).
    start = 0
    trigger = None
    for i, o in enumerate(objs):
        if _is_real_user(o):
            start = i + 1
            trigger = o

    judged = []   # (stripped line, breach class or None) per NON-BLANK line,
                  # in order -- feeds the lone-dot escape AND the sentinel-
                  # lists escape below (docstrings DOT ESCAPE and SENTINEL
                  # LISTS); blanks stay out so header/item adjacency
                  # survives the blank separators between §5's two lists.
    bash_cmds = []  # the window's Bash tool_use commands, for the
                    # BASH-WRITE CATCH (docstring section of that name)
    for o in objs[start:]:
        if o.get("type") != "assistant":
            continue
        if o.get("isApiErrorMessage") is True:
            continue                     # CLI-authored, not model output
        msg = o.get("message") or {}
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content")
        if isinstance(content, list):
            for blk in content:
                if (isinstance(blk, dict)
                        and blk.get("type") == "tool_use"
                        and blk.get("name") == "Bash"):
                    cmd = (blk.get("input") or {}).get("command")
                    if isinstance(cmd, str) and cmd:
                        bash_cmds.append(cmd)
        for text in _text_of(content):
            for ln in text.splitlines():
                s = ln.strip()
                if s:
                    judged.append((s, _line_breach(ln, mode)))

    # Label checks (§3.2.4.5; REPO only): the two contracts needing a
    # window-wide fact —— the `🦈`-line count —— so they run here, after the
    # per-line verdicts and before they are split into offending/classes.
    # Count-gated mirrors: exactly one line arms the solo check, 2+ arm the
    # missing-label check; full precedence in each function's own docstring.
    # The BASH-WRITE CATCH is likewise REPO-only (comms conventions are this
    # repo's) and rides every later log call as the `bashw=` field.
    bashw = "-"
    if mode == MODE_REPO:
        _flag_solo_sha_label(judged)
        _flag_unlabelled_multi_sha(judged)
        if bash_cmds:
            bashw = _bash_comms_writes(bash_cmds, trigger) or "-"

    all_lines = [s for s, _ in judged]
    offending = [s for s, k in judged if k]
    classes = [k for s, k in judged if k]

    if not offending:
        # Clean turn -> proof-of-life, non-blocking.
        _log_event(sid, "clean", pid=plog, mode=mode, bashw=bashw)
        return 0

    # --- Lone full-stop escape (BOTH modes; see docstring DOT ESCAPE) -------
    # Checked over ALL non-blank content, not just `offending`, so a dot
    # sharing the turn with an otherwise-clean declaration still fails --
    # "alongside other lines" disqualifies it even when those other lines are
    # themselves permitted. Tagged distinctly per mode so the log alone shows
    # which rule sanctioned the exchange, without needing the separate
    # `mode=` field.
    if _lone_dot_turn(all_lines):
        dot_tag = "clean:dot" if mode == MODE_REPO else "clean:dot_reader"
        _log_event(sid, dot_tag, pid=plog, mode=mode, bashw=bashw)
        return 0

    # --- Sentinel-lists escape (root §5.3–§5.4; REPO only; see docstring
    # SENTINEL LISTS) -- the exact §3.2.6 canon anywhere in the window
    # re-sanctions the two §5 list shapes, and ONLY out of class `prose`;
    # every other class keeps its verdict, and READER is never touched
    # (its class is `reader`). Runs BEFORE the verdict is drawn so `first=`
    # and `lines=` describe the lines that actually remain in breach.
    if mode == MODE_REPO and any(
            s.replace(_VS16, "") == _SENTINEL_CANON for s in all_lines):
        kept = [(s, k) for i, (s, k) in enumerate(judged)
                if k and not (k == "prose" and _sentinel_list_line(judged, i))]
        if not kept:
            _log_event(sid, "clean:compaction", pid=plog, mode=mode,
                       bashw=bashw)
            return 0
        offending = [s for s, k in kept]
        classes = [k for s, k in kept]

    # Class of the FIRST offender, so the logged verdict and `first=` always
    # describe the same line. `sic` may override it below.
    verdict = "yellow:" + classes[0]

    # --- Exemptions (see docstring EXEMPTIONS) -------------------------------
    # Order = widest authorisation first, so the log names the strongest reason.
    typed = _trigger_text(trigger)
    if _OVERRIDE_RE.search(typed):
        # The user suspended the rule for this turn —— disarmed in BOTH modes.
        # `bashw=` still rides the record: the exemptions govern CHAT text,
        # never lint coverage (docstring BASH-WRITE CATCH, DELIVERY).
        _log_event(sid, "exempt:override", len(offending), offending[0],
                   pid=plog, mode=mode, bashw=bashw)
        return 0

    if mode == MODE_REPO:
        if _YN_TOKEN in typed:
            # The user authorised a one-word chat answer -> nothing to enforce.
            _log_event(sid, "exempt:yn", len(offending), offending[0],
                       pid=plog, mode=mode, bashw=bashw)
            return 0
        cap = _sic_cap(typed)
        if cap is not None:
            # A sanctioned status report: exempt only WITHIN its word cap,
            # counted over the offending lines alone (the turn's declarations
            # are separately permitted and would blow any cap).
            if len(" ".join(offending).split()) <= cap:
                _log_event(sid, "exempt:sic", len(offending), offending[0],
                           pid=plog, mode=mode, bashw=bashw)
                return 0
            verdict = "yellow:sic_overrun"
        if _dats_exempt(offending):
            # The single close-protocol status line -> sanctioned chat text.
            _log_event(sid, "exempt:dats", len(offending), offending[0],
                       pid=plog, mode=mode, bashw=bashw)
            return 0

    # --- YELLOW —— demoted: never blocks, still logged + shown to the USER --
    # On exit 0 a Stop hook's stdout `systemMessage` JSON reaches the USER
    # only, never the model (see docstring ALWAYS RED -> ALWAYS YELLOW). Every
    # breach reaching here is a WARNING: there is no ceiling and no ledger,
    # and (unlike the retired RED policy) the exit code never varies. The log
    # line is written only AFTER the message write succeeds, so the record
    # always reflects a warning actually delivered.
    try:
        sys.stdout.write(json.dumps({"systemMessage": _BREACH[mode]}))
    except Exception:
        _log_event(sid, "message_failed", len(offending), offending[0],
                   pid=plog, mode=mode, bashw=bashw)
        return 0                          # fail-safe: never break the turn
    _log_event(sid, verdict, len(offending), offending[0], pid=plog,
               mode=mode, bashw=bashw)
    return 0                              # NEVER 2 —— see ALWAYS RED -> ALWAYS YELLOW


if __name__ == "__main__":
    sys.exit(main())
