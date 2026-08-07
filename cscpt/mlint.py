#!/usr/bin/env python3
"""Stop hook —— Mission Linter; BLOCKS one turn-end when a mandated, USER-FACING line was owed and
never emitted: an `#m2` INTERIM declaration (stopped dead ON it, or never emitted at all), or the
`🚨` post-compaction sentinel root `CLAUDE.md` §5 owes on a compaction-triggered turn.

Root scope: THIS repo only (`dupbus-ceztuc-7cufVe`), anchored on this file's own
`__file__` and never on the process cwd. `#m2` is defined by `universal/m2.md`,
which exists in no other repo, so the sibling `AJAP_repo` and the parent Reader
folder (`GitHub/`) are deliberately out of scope —— neither has an m2 protocol to
breach, and a hook that can BLOCK must not police a repo that never agreed to
the rule (`cp/ccsim/hook_guide.md` § Global Reach & Self-Scoping).
THE SCOPE GUARD IS LOAD-BEARING, NOT TIDINESS. This hook is registered in the
USER settings file, so it fires in EVERY project on this Mac, exactly as
`.claude/post_compact.sh` does —— and it is the only one of the two that can
BLOCK. `AJAP_repo`'s `#seek` cockpit runs unattended for hours and its paramount
rule is that nothing may stall it: a stalled cockpit is an unsupervised
programme. So `_in_scope` runs FIRST, before any shape is even considered, and
outside this repo every shape (A, B and C alike) exits 0 having only logged.
CONSEQUENCE, DELIBERATE: an AJAP-cwd session gets no §5 backstop from here at
all. That is correct, not a gap to close from this file —— `AJAP_repo/CLAUDE.md`
owns its own § Compaction protocol, including the cockpit's do-NOT-halt
carve-out, which this hook's message would actively contradict.

=== NON-CCSIM —— start of all you need to RUN it ===
* WHAT: a Stop hook blocking ONE turn-end in 3 cases —— an `#m2` turn that (A)
  ended ON the interim declaration, `#sprint` unstarted, or (B) wrote a
  `response_` and never declared it; or (C) an UNPAID compaction —— a summary
  you did not write, no later `🚨` (root §5).
* IF IT FIRES: do the ONE thing named: (A) the `#sprint`; (B) the `➡️` line;
  (C) §5: sentinel, halt, both lists. Never re-emit a batch.
* FALSE ALARM: reply a lone `.`, nothing else. Once per prompt; `override`
  disarms A/B only.
* Verdicts log to `cscpt/.mlint.log`, one per run.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===

THE DEFECT THIS EXISTS FOR, stated once and precisely. `universal/m2.md` orders:
(1) write a `response_` of initial thoughts; (2) commit + push + declare THAT
FILE ALONE in chat; (3) `#sprint` the real work; (4) update the `response_`;
(5) declare again as the real TEA3. Step 2's declaration is explicitly NOT a
TEA3 and m2.md says so in as many words —— yet step 2 has failed TWO ways:
* SHAPE A (`block`): the declaration was emitted as the last content of a
  message and the turn stopped there, across at least three separate sessions,
  each costing the owner a manual `continue`.
* SHAPE B (`block_nodeclare`): the declaration was never emitted AT ALL. Live
  case 202608050209 —— the agent wrote the `response_`, committed, pushed, then
  produced a message carrying only tool calls. Its own reasoning that same
  moment read "I need to emit the declaration text in the same message as my
  tool calls", and the text simply never got typed. From the owner's side a
  successful push with no declaration is indistinguishable from a failed one,
  and the file he is meant to click is not clickable.
Shape B is why this hook cannot key on the turn's ENDING alone: that turn ended
on a sanctioned lone `.` after dispatching its sprint, which is an ordinary,
correct shape. Only the ABSENCE of the `➡️` line anywhere in the turn
distinguishes it —— so shape B is detected by absence, shape A by position.

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

THE SECOND DEFECT —— §5's POST-COMPACTION SENTINEL (SHAPE C). Root `CLAUDE.md`
§5 orders that a compaction be met with an exact sentinel ("🚨 Compaction
Detected —— stopped all tasks."), a full halt, and two lists telling the owner
what context survived and what did not. On 202608070423 an auto-compaction hit
this repo's own session and §5 was skipped ENTIRELY —— no sentinel, no halt, no
lists. The cause is structural, not carelessness: the harness's compaction
summary ENDS with an imperative of its own —— "Resume directly —— do not
acknowledge the summary, do not recap what was happening… as if the break never
happened" —— and that instruction arrives as the user-side message opening the
turn, i.e. in the strongest position the context has. §5 is prose in a file read
turns earlier; the harness line is prose in the prompt itself. Prose lost.
WHY A HOOK AND NOT MORE PROSE. `.claude/post_compact.sh` is registered on the
real `PostCompact` event, but that event's contract sends stdout to the USER and
stderr to the USER —— NO exit code opens a model-facing channel, so the hook can
never instruct the model at all (verified in the harness's own hook registry).
§5 was therefore re-anchored on the OBSERVABLE (a summary you did not write),
which is correct but still prose competing head-on with the harness's own line.
`cp/ccsim/CLAUDE.md` §8.7: the breach was NOT-NOTICED, so the prose that failed
cannot repair it —— a mechanism is owed, and Stop is the only event that can
force the missing output back into the same turn.
WHY IT PASSES `hook_guide.md` §6.4.3's BLOCKING TEST ("does the blocked agent
have real work to spend the extra turn on?"). Yes, and more than either m2
shape: the forced turn produces the sentinel, the halt, and BOTH §5.3/§5.4
lists —— the only record the owner will ever get of what his session lost. Skip
it and that information is gone for good; there is no file it lands in later.
NO `#sprint` EXEMPTION: `universal/sprint.md` § Interactions says a compaction
during a sprint still emits the sentinel as always, then resumes from the slog
(§5.8). The sentinel is owed on EVERY compaction-opened turn without exception.

THE CONDITIONS —— every one fails OPEN. Condition 1 and the loop guard are
shared by the two `#m2` shapes; SHAPE C is independent of `#m2` entirely and is
tested FIRST, because §5.2's halt means a compaction-opened turn should not have
been running an m2 sprint in the first place. SHAPE B precedes SHAPE A because a
turn that never declared cannot also have ended on a declaration.
SHAPE C —— `block_nosentinel`, all must hold:
1c. AN UNPAID COMPACTION IS IN CONTEXT —— scan ALL loaded records for the LAST
    compaction summary; it is UNPAID if no assistant record AFTER it emits the
    sentinel. Root §5.1.1 defines the debt in exactly those words ("a summary
    you did NOT write is in context w/ no LATER `🚨` of yours") and §5.1.4 makes
    it survive ("Applies on ANY later turn too (post-`continue`,
    post-limit-hit), until paid").
    * WHY NOT "the record that OPENED this turn", which is what this tested
      first and what a reader will assume: that couples the debt to the ONE
      turn the summary happened to open, so ANY later user message —— a
      `continue`, a mid-turn message (root §3.1.7.6.1), a wake after a
      usage-limit death —— moves the window opener to a human record and the
      debt is never owed again. Escape once, escape forever. This is not
      hypothetical: the 202608070423 transcript has precisely that shape ——
      summary, a worked turn ending on a `✅` batch with no sentinel, then a
      typed user message. Under the trigger-coupled test the second Stop and
      every Stop after it read that session as never having compacted.
    * A summary is identified STRUCTURALLY, never by wording: `isCompactSummary`
      is `true` on the record, OR a `{"type":"system","subtype":
      "compact_boundary"}` record sits IMMEDIATELY before it AND its text opens
      with "This session is being continued from a previous conversation".
      Mined from the real compaction pairs on disk (202607150625 manual,
      202608070423 auto), which agree on both fields. Wording alone would be
      reckless HERE of all repos —— CCSIM sessions quote that sentence whilst
      discussing this very defect, and the whole transcript is now scanned, so a
      pasted quote must never arm a blocking hook.
    * WHERE THE PAIR LIVES, measured rather than assumed, because a reader has
      already re-derived it wrongly in each direction. The harness writes the
      boundary+summary pair TWICE, with an IDENTICAL `timestamp` and identical
      text: once at the TAIL of the old session's transcript, and again at the
      HEAD of the new one. Measured on the 202608070423 compaction ——
      `eaccd7dc-…`: 1666 records, boundary 1612, summary 1613, and the model
      then went on working IN THAT SAME FILE for another 50-odd records;
      `0b6a0a90-…`: boundary 6, summary 7. So NEITHER placement may be assumed:
      scanning for the LAST one anywhere in the file is the only rule that holds
      for both, which is a second, independent reason this is no longer keyed on
      the window opener.
    * §5.1.3 ("Owed PER summary") falls out for free: only the LAST summary is
      tested, and only records after IT can pay it, so a sentinel emitted before
      a second compaction never discharges the second one.
    * BUDGET —— at most `_MAX_SENTINEL_BLOCKS` blocks are ever spent on ONE
      compaction, counted from the ledger by a per-compaction id (`cid=`, a hash
      of the summary's timestamp + text, stable across both copies of the pair).
      This is the price of making the debt survive: an unpaid debt now arms on
      EVERY later turn, so without a ceiling a model that answers each block
      with the lone `.` escape would be blocked once per prompt forever. That is
      the unbounded-retry failure this file elsewhere calls worse than missing.
      The ceiling is not 1 —— 1 would re-create the hole, since the first block
      is routinely spent on a turn that cannot comply (a limit death, a lone
      `.`) —— but past a few refusals a further block only burns turns.
2c. NO SENTINEL ANYWHERE —— no assistant chat line in the turn starts with `🚨`
    (bold wrapper and the emoji variation selector tolerated).
3c. THE TURN ACTUALLY SPOKE —— at least one assistant record in the window. An
    empty window is far more likely a parse that fell short than an agent that
    genuinely produced nothing.
4c. NOT HARNESS-TERMINATED and NOT AN URGENT STOP —— same exclusions as 4b, plus
    a `⚠️` blocker ending (§3.2.5), which is a deliberate early stop that must
    never be held open even to collect the sentinel.
* Why ANYWHERE rather than FIRST, though §5.1 owes it immediately: presence
  suppresses, so scanning the whole turn is the fail-open direction. A sentinel
  emitted late is a §5 ordering fault, not the total omission this exists for,
  and it is not worth a wrong block. Ordering has no mechanical enforcement here
  —— stated plainly per `cp/ccsim/CLAUDE.md` §8.7 rather than implied away.
* Why the GLYPH and not the exact 33-character wording —— RULED ON, not left to
  taste, because owed-until-paid raises the stakes. A sentinel typed with one em
  dash instead of two, in the wrong case, or with the full stop missing, PAYS
  the debt and does NOT block. `🚨` has exactly one sanctioned use in this
  protocol (§3.2.6), so the glyph alone identifies it. Under the OLD
  trigger-coupled arming a strict wording test would merely have cost one wrong
  block; under owed-until-paid it would leave the debt permanently unpaid and
  re-arm on every later turn, so a cosmetic typo would become a recurring block.
  Verbatim wording is §5.1.2's job and stays a matter for review, never for this
  hook. Same fail-open bias as `_is_io_declaration` ("only the GLYPH is tested,
  not the file-list shape").
* Why LINE-START and not anywhere-in-the-line: that is the one line that
  separates EMITTING the sentinel from DISCUSSING it, and this repo's sessions
  discuss it constantly —— including in the very files that maintain this hook.
  A backticked or mid-sentence `🚨` therefore does not pay. The converse is
  accepted: a line that genuinely opens with the glyph pays even if it is prose
  ABOUT the sentinel. That direction only ever suppresses a block, which is the
  cheap failure.
* ACCEPTED MISS —— a FENCED example pays. `_has_sentinel` splits on lines and
  does NOT mask code fences, so a ```-fenced specimen of the sentinel discharges
  a real debt. Deliberate, not an oversight: masking fences in ASSISTANT output
  would let one unbalanced backtick anywhere in a turn hide a genuine sentinel
  and produce a WRONG BLOCK. `_invokes_m2` masks fences because there a fence
  match CAUSES firing; here it PREVENTS it, so the same technique would push the
  risk the wrong way. RESIDUAL RISK, stated rather than implied away
  (`cp/ccsim/CLAUDE.md` §8.7): a CCSIM session that compacts whilst documenting
  the sentinel can discharge its own §5 debt with an example. Nothing mechanical
  catches that; review must.
1. M2 EVIDENCE —— the turn was an `#m2` turn (see M2 EVIDENCE below). Shared.
SHAPE B —— `block_nodeclare`, all must hold:
2b. RESPONSE WRITTEN —— a `[prefix_]response_[TS].md` was touched by
    `file_path` in this turn, i.e. the declaration was actually owed.
3b. NOTHING DECLARED —— no assistant chat line in the turn starts with `➡️`
    (bold wrapper tolerated). A `✅`/`⇠` line does NOT satisfy this: the owed
    artefact is the OUTPUT declaration, the clickable one.
4b. NOT HARNESS-TERMINATED —— the turn did not end on a `⚠️` blocker, the `🚨`
    sentinel, or an `isApiErrorMessage` line. The first two are legitimate
    urgent stops; the third means the model was cut off and cannot comply, so
    blocking would burn the one allowed turn against a wall.
SHAPE A —— `block`, all must hold (unchanged behaviour):
2a. NO SPRINT EVIDENCE —— nothing in the turn says a sprint began (see SPRINT
    EVIDENCE).
3a. DECLARATION END —— the turn's LAST non-blank chat line is a declaration the
    batch can END on: an I/O declaration (`✅`/`⇠`/`➡️`, root §3.2.1–3) or the SHA
    declaration (`🦈`, §3.2.4 —— the sixth class, and the line §3.1.6.3's batch
    now ordinarily finishes with). That is the observed failure shape. A turn ending
    on a `⚠️` blocker (§3.2.5), the `🚨` sentinel (§3.2.6), a lone `.`, plain
    prose, a harness-authored API-error line, or nothing at all is left alone ——
    those are other situations, and one of them (the blocker) is a legitimate,
    urgent early stop that must never be held open.
SHARED: NOT ALREADY FIRED —— see LOOP GUARD. The ledger spans ALL THREE shapes,
so a prompt gets ONE forced turn in total, never one per shape
(`hook_guide.md` §6.3 budgets exactly one extra round trip per prompt).
Plus: `override` in the typed message disarms SHAPES A and B, matching the house
exemption in `clint.py`. It does NOT disarm SHAPE C, and the two halves of that
gate run at different points —— see `main`. Reason: an exemption must be a live
instruction for the turn at hand, and the only text a compaction turn opens with
is a machine-written recap of an OLDER turn, which both real summaries on disk
show can carry the word incidentally. The escape from a SHAPE C block is the
lone `.` its message names, not a word inside a harness recap.

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
(a2) a `[prefix_]slog_[TS].md` ON DISK in the m2 `query_`'s own folder whose
    12-digit TS is >= that query's —— `slog_disk`. Checked only when the m2
    evidence came from a query FILE, which is the only route that can point at a
    mission older than this turn.
    * THE FALSE BLOCK THIS REPAIRS, which really happened: a turn was blocked
      with `m2=query sprint=none` after merely RE-READING a three-day-old
      `career_query_202608041846.md`. That mission's sprint had run in an
      earlier session and its `career_slog_202608042032.md` had been sitting on
      disk ever since. The turn was correct; the hook was wrong; a real turn was
      spent on nothing.
    * WHY A SLOG ON DISK SETTLES IT: `universal/sprint.md`'s Preamble makes the
      slog a MANDATORY pair —— "Neither is EVER optional" —— so a slog at least
      as new as the query is proof that query's sprint already ran. The evidence
      outlives the session, which is exactly what a re-read of an old query
      needs and what an in-window `file_path` scan can never supply.
    * WHY TIMESTAMP-PAIRING WOULD NOT HAVE CAUGHT IT: the `response_` this turn
      wrote carried the SAME TS as the stale query (root §3.5.3 requires that),
      so query and response matched perfectly. Staleness is invisible in the
      pair; only the slog channel shows it.
    * WHY `>=` AGAINST THE QUERY'S OWN TS is the right comparison, and why it is
      not as loose as it looks: a query written NOW carries the newest TS in its
      folder, so nothing on disk can be >= it and a genuine fresh `#m2` is
      untouched. Only a query the folder has already moved PAST —— i.e. a stale
      one —— can match. The test is therefore a staleness test wearing a slog's
      clothes.
    * WHY ANY `*slog_*` AND NOT A PREFIX MATCH against the query's own CP: root
      §5.8.1 makes the same call for the same reason ("`*slog_*` (not `slog_*`)
      is deliberate"). A prefix match would be NARROWER, and narrower means MORE
      firing, which is the wrong direction for a signal whose only power is to
      suppress. ACCEPTED MISS, stated rather than hidden: a slog written by an
      unrelated concurrent session in the same folder and minute also suppresses.
      That costs a missed block, never a wrong one.
(b) `universal/sprint.md` opened by `file_path` —— root §7.3.1's mandated read
    on `#sprint`. Weaker than it looks: a `#trigger` file is read ONCE per
    session, so a second `#m2` later in the same session shows no re-read. It
    can only ever cause a missed block, never a wrong one, so it stays;
(c) an `Agent`/`Task`/`Workflow` dispatch —— m2 step 3's stated vehicle ("use
    SA(s) if apt"). `Workflow` was ADDED after a live near-miss: the
    202608050209 turn ran its whole sprint through a `Workflow` script, so the
    original `Agent`/`Task`-only set read that turn as sprint=none. Had that
    agent declared correctly and ended on the declaration, shape A would have
    blocked a turn whose sprint was already running —— a WRONG block, the one
    outcome this file spends its whole design budget avoiding.
⚠️ `TaskUpdate` and `TaskCreate` are TODO-list tools, NOT dispatches, and appear
all over ordinary turns —— matching either would disarm this hook almost
everywhere. Checked, not assumed: `TaskCreate`'s input is
`{subject, description, activeForm}`, the shape of a to-do entry, and its text
merely NARRATES a plan ("Dispatch SA(s) to …") whilst dispatching nothing.
`Workflow`'s input is `{script}` —— an executable fleet definition, so it always
IS a dispatch. The match is therefore an EXACT tool-name set, never a prefix.
Verified against the real incident: its window held Bash/Read/Write only —— no
slog, no sprint.md, no dispatch —— whilst the legitimate post-sprint turn from
the same session held an `Agent` dispatch AND a `career_slog_202608042032.md`
edit.

TURN WINDOW: records after the LAST genuine user message, the same boundary
`clint.py` uses, with the same `_is_real_user` exclusions (tool_result-only
turns, and the wrappers Claude Code injects as `type:"user"` with no human
behind them). Sub-agent lines (`isSidechain`) are dropped —— an SA's own reads
are not the main turn's evidence.
* The compaction summary is `type:"user"` with plain string content and none of
  the injected-wrapper prefixes, so it COUNTS as the boundary. That is exactly
  right and is what SHAPE C rests on: the compacted turn's window is everything
  the model did after the summary landed. But it is NOT a typed message, so
  `main` blanks it as m2 EVIDENCE on such a turn (a narrowing —— it can only
  reduce firing) whilst still honouring it for the `override` EXEMPTION of the
  m2 shapes, which both real summaries on disk happen to trigger.
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
   `action=block`, `block_nodeclare` OR `block_nosentinel` line carrying the
   same `pid=` means this prompt has had its one turn and must never be blocked
   again —— ALL THREE shapes share the one budget, so the ledger matches the
   names explicitly rather than by prefix (a prefix would also swallow
   `block_unlogged`, which is precisely the case where NO block was issued and
   a later one must stay possible). The prompt id comes from the
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
`block_unlogged`, `block`, `block_nodeclare`, `block_nosentinel`). A breach-only
log cannot tell "ran and found nothing" from "the harness never called this
command" —— that ambiguity is exactly how dead hook wiring survived unnoticed
here for weeks, so EVERY invocation writes a line (`hook_guide.md` §7.7).
SHAPE C gets its own answer INSIDE that same one line, never a second line: the
`compact=` field says what the compaction test concluded —— `n/a` (the run
exited before reaching it), `no` (ran; NO compaction summary anywhere in what
was loaded), `ok` (ran; the sentinel is in THIS turn), `paid` (ran; a compaction
is in context and an EARLIER turn already paid it),
`api_error`/`urgent`/`no_output` (ran; exempted), `spent` (ran; owed, but this
compaction's block budget is exhausted), `err` (the test itself raised and
failed open), `owed` (blocked). Without that field a silent `no_m2` line could
mean the compaction test passed, or that it never ran at all —— precisely the
ambiguity the paragraph above exists to forbid. `paid` and `no` are split for
the same reason: "found a compaction, debt settled" and "never compacted" are
different facts, and only the split lets the log show that owed-until-paid is
actually scanning rather than silently returning False.

TRANSCRIPT SIZE: the file is read whole up to `_MAX_TRANSCRIPT_BYTES`; past
that only the trailing window is read, newline-aligned. That cap is what keeps
the cost flat, and it now carries more weight than it did: owed-until-paid scans
EVERY loaded record for the last compaction instead of testing one, so the work
is bounded by the cap rather than by the turn.
MEASURED, not asserted —— 51 MB transcript, the largest on disk, five runs each:
whole-transcript scan 71 ms median, the old trigger-coupled test 29 ms. So the
upgrade costs ~40 ms. `hook_guide.md` §12.7 measures clint at `~`165 ms on the
same class of file reading unbounded, and Stop hooks run in PARALLEL (§12.3), so
a hook no slower than the incumbent worst still adds ZERO to the event —— mlint
remains the cheaper of the two. NOTE the earlier claim that mlint does "strictly
less work than clint" was written before this scan existed; it is now true only
in the end-to-end sense measured above, not structurally, and is restated that
way rather than left to rot.

LOG FORMAT: one tab-delimited line per invocation —— timestamp, `session=`,
`pid=`, `action=`, `m2=`, `sprint=`, `compact=`, `cid=`, `first=` (the turn's
final chat line, flattened and truncated; last because it alone carries free
text; every field before it is a fixed token, so a new field is appended BEFORE
`first=` and existing tab-delimited reads keep working —— `cid=` was added that
way). `cid=` is the compaction id the `compact=` verdict refers to, and it is
not decoration: it is the KEY the per-compaction block budget counts on, so a
ledger line without it cannot be counted. `MLINT_LOG=`
redirects it so a test neither reads nor pollutes the real log. It self-prunes
to a recent window (`_LOG_MAX_LINES` triggers, `_LOG_KEEP_LINES` survives) by
atomic rename, never truncation, AFTER the current line is on disk —— the same
mechanism and the same guarantees as `clint.py`'s, for the same reason: the log
answers only "did this run for that turn, and why", which is asked about the
current session or a very recent one.
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

# --- Repo scope (see docstring Root scope) ---------------------------------
_REPO_ROOT_REAL = os.path.realpath(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_REPO_SLUG = re.sub(r"[/ ]", "-", _REPO_ROOT_REAL.rstrip("/"))
_SPRINT_MD_REAL = os.path.join(_REPO_ROOT_REAL, "universal", "sprint.md")

# --- Filename shapes (root CLAUDE.md §3.3; `[CP_]name_[TS].md`) ------------
_QUERY_FILE_RE = re.compile(r"^(?:[A-Za-z0-9-]+_)*query_\d{12}\.md$", re.I)
_SLOG_FILE_RE = re.compile(r"^(?:[A-Za-z0-9-]+_)*slog_\d{12}\.md$", re.I)
_RESPONSE_FILE_RE = re.compile(r"^(?:[A-Za-z0-9-]+_)*response_\d{12}\.md$", re.I)

# --- `#m2` invocation shape (see docstring M2 EVIDENCE) --------------------
# Line-start only. `\b` after the token so `#m2x` never matches whilst
# `#m2 expect 2` and a bare `#m2` both do.
_M2_RE = re.compile(r"^[ \t]*#m2\b", re.I | re.M)
_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_BACKTICK_RE = re.compile(r"`[^`\n]*`")

# --- Declaration glyphs (root CLAUDE.md §3.2) ------------------------------
_VS16 = "️"                       # emoji variation selector
_IO_GLYPHS = ("✅", "⇠", "➡")     # ✅ ⇠ ➡ —— §3.2.1–3
# `🦈` (§3.2.4) is the turn's commit SHAs —— a SIXTH declaration class the owner
# split out of `➡️`. It is part of the TEA3 batch (§3.1.6.3's example ends on
# it), so it is now the LAST line a batch-ending turn shows. Added to the
# BATCH-END set only, never to `_IO_GLYPHS`: see `_is_declaration_end`.
_G_SHA = "\U0001f988"
_BATCH_END_GLYPHS = _IO_GLYPHS + (_G_SHA,)

# `🚨` —— the post-compaction sentinel (root §3.2.6/§5.1). SHAPE C tests the
# glyph alone, deliberately, for the reasons in THE CONDITIONS above.
_G_SENTINEL = "\U0001f6a8"

# The harness's compaction summary opens with this sentence, verbatim, in every
# real occurrence on disk. Used ONLY as the second half of a structural test ——
# never on its own, because this repo's own sessions quote it in prose.
_COMPACT_OPENING = "this session is being continued from a previous conversation"

# `override` in the typed message disarms this hook, exactly as in `clint.py`.
_OVERRIDE_RE = re.compile(r"\boverrid(?:e|ing)\b", re.I)

# Wrappers Claude Code injects as `type:"user"` with no human behind them.
# Exact prefix match only, so human prose mentioning these words is unaffected.
_SYSTEM_INJECTED_TAGS = (
    "<task-notification>", "<local-command-caveat>",
    "<local-command-stdout>", "<command-name>", "<command-message>",
    "<command-args>")

# EXACT tool names that mean "a sub-agent was dispatched". `TaskUpdate` and
# `TaskCreate` are TODO tools and must NEVER be matched here —— see docstring
# SPRINT EVIDENCE.
_DISPATCH_TOOLS = frozenset(("Agent", "Task", "Workflow"))

# EXACT tool names that CHANGE a file. Only these make a `response_` count as
# WRITTEN, hence its declaration OWED —— merely READING an old `response_` (a
# routine retrospection act, root §4) must never put a turn on the hook.
_WRITE_TOOLS = frozenset(("Write", "Edit", "MultiEdit", "NotebookEdit"))

# Safety caps. None is reached in normal use; each bounds a pathological input.
_MAX_TRANSCRIPT_BYTES = 8 * 1024 * 1024   # tail-read past this
_MAX_QUERY_FILES = 5                      # query files opened per invocation
_MAX_QUERY_BYTES = 256 * 1024             # bytes read from any one of them
_LEDGER_TAIL_LINES = 400                  # log lines scanned for a prior block
_MAX_DIR_ENTRIES = 4000                   # names scanned in a comms folder

# How many blocks ONE compaction may ever cost. See docstring 1c BUDGET: the
# debt now survives across turns, so an unbounded budget would let a model that
# answers each block with the lone `.` escape be blocked once per prompt for the
# rest of the session. Not 1 —— the first block is routinely spent on a turn
# that could not comply (a limit death, an already-dotted escape), and a
# ceiling of 1 would rebuild the very hole owed-until-paid exists to close.
_MAX_SENTINEL_BLOCKS = 3

# The 12-digit TS trailing a comms filename (root §3.3). Both shapes have
# already been matched by `_QUERY_FILE_RE`/`_SLOG_FILE_RE` before this is
# applied, so the group is guaranteed present.
_TS_SUFFIX_RE = re.compile(r"_(\d{12})\.md$", re.I)

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

# The SHAPE B message. Deliberately narrower than `_BLOCK_MSG`: it names ONE
# line of output and forbids everything else, because the failure it repairs is
# one missing line and a padded reply is how `clint.py`'s blocking era went
# wrong (`hook_guide.md` §6.4).
_NODECLARE_MSG = (
    "[mlint] `#m2` DECLARATION MISSING —— this turn invoked `#m2` and wrote a "
    "`response_`, but no `➡️` declaration was emitted anywhere in it. A "
    "successful push with no declaration looks, from the user's screen, "
    "exactly like a failed one, and he cannot click the file.\n"
    "EMIT IT NOW: the `➡️` line for that `response_`, alone —— nothing else, no "
    "summary, no re-run of finished work. If further work remains, put the "
    "line in the SAME message as your next tool call.\n"
    "If the declaration genuinely was not owed, reply with a lone `.` and "
    "nothing else. This fires at most once per prompt.")

# The SHAPE C message. It must do one thing the other two need not: contradict
# an instruction the model can still see. The compaction summary's closing
# "resume directly, do not acknowledge" is the harness default, and §5 overrides
# it —— so the message says that outright rather than merely asking for output
# the visible prompt appears to forbid.
_NOSENTINEL_MSG = (
    "[mlint] POST-COMPACTION §5 NOT DELIVERED —— this turn was opened by the "
    "harness's compaction summary, and no `🚨` sentinel appears anywhere in it. "
    "That summary's closing \"resume directly —— do not acknowledge\" line is "
    "the harness default; root `CLAUDE.md` §5 OVERRIDES it and is the rule you "
    "are held to. §5 was skipped in full once already, on 202608070423.\n"
    "DO NOW, in this order and nothing else: (1) emit exactly `🚨 Compaction "
    "Detected —— stopped all tasks.`; (2) halt every fore/background task "
    "(§5.2); (3) list the previously-read files/content still USEFUL to the "
    "task (§5.3), then SEPARATELY the remainder (§5.4) —— those two lists are "
    "the only record the user gets of what the session lost; (4) re-read and "
    "resume NOTHING —— await the user's instruction (§5.5–5.7). "
    "Sole exception: if §5.8's `*slog_*` glob finds a LIVE slog (no `SPRINT END` "
    "tail, TS of this session), resume from it —— AFTER the sentinel and both "
    "lists, never instead.\n"
    "If this turn genuinely was not opened by a compaction, reply with a lone "
    "`.` and nothing else. This fires at most once per prompt.")


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


def _has_output_declaration(window):
    """True if ANY assistant chat line in the turn is an OUTPUT declaration
    (`➡️`, root §3.2.3), bold wrapper tolerated. Deliberately NOT satisfied by a
    `✅` read-list or a `⇠` comms-read line: those are not the artefact m2 step 2
    owes, which is the clickable pointer to the `response_` just written.
    Harness-authored lines are skipped for the same reason as in
    `_last_chat_line`. Presence SUPPRESSES a block, so every ambiguity here ——
    including a `➡️` that happens to sit inside quoted text —— resolves in the
    fail-open direction. Never raises."""
    for o in window:
        try:
            if o.get("type") != "assistant" or o.get("isApiErrorMessage") is True:
                continue
            if (o.get("message") or {}).get("role") != "assistant":
                continue
            for ln in _message_text(o).splitlines():
                t = ln.strip()
                if t.startswith("**"):
                    t = t[2:].strip()
                if t.replace(_VS16, "").startswith("➡"):
                    return True
        except Exception:
            continue
    return False


def _is_compaction_summary(rec, preceding):
    """True if `rec` is the harness's compaction summary rather than a human
    message.

    STRUCTURAL FIRST, wording only as a chaperone. Signal (a) is the record's own
    `isCompactSummary: true`, which the harness sets and nothing else does.
    Signal (b) requires a `{"type":"system","subtype":"compact_boundary"}` record
    IMMEDIATELY before it AND the summary's opening sentence —— it exists only so
    a future harness that drops the flag but keeps the boundary is still caught.
    The wording is NEVER sufficient alone: this repo's own sessions quote that
    sentence whilst working on this very defect, and since the WHOLE transcript
    is now scanned rather than just the turn opener, a pasted quote gets more
    chances to be seen, not fewer. Never raises; anything unexpected is False,
    which is the fail-open direction."""
    try:
        if not isinstance(rec, dict) or rec.get("type") != "user":
            return False
        if rec.get("isCompactSummary") is True:
            return True
        if not (isinstance(preceding, dict)
                and preceding.get("type") == "system"
                and preceding.get("subtype") == "compact_boundary"):
            return False
        return _message_text(rec).lstrip().lower().startswith(_COMPACT_OPENING)
    except Exception:
        return False


def _compaction_id(rec):
    """A stable, whitespace-free id for ONE compaction —— the key the block
    budget counts on. Hashes the summary's `timestamp` and text together: both
    are written IDENTICALLY into the tail copy of the old transcript and the
    head copy of the new one (measured —— see docstring 1c), so the same
    compaction yields the same id whichever copy this run happens to read, and
    two different compactions in one session yield different ids because their
    recaps differ. Never raises; `-` means unidentifiable, which the budget
    treats as "do not count", leaving the per-prompt ledger as the only guard."""
    try:
        seed = str(rec.get("timestamp") or "") + _message_text(rec)
        if not seed:
            return "-"
        return hashlib.sha1(seed.encode("utf-8", "replace")).hexdigest()[:12]
    except Exception:
        return "-"


def _last_compaction(objs):
    """(index, id) of the LAST compaction summary in the loaded records, or
    (None, "-").

    Scanning the WHOLE file, not the turn opener, is upgrade 1 in one line: root
    §5.1.4 owes the sentinel "on ANY later turn too… until paid", so the debt
    cannot be keyed on the single turn the summary happened to open. Taking the
    LAST also delivers §5.1.3 ("Owed PER summary") for nothing —— a sentinel
    emitted before a second compaction sits BEFORE this index and therefore
    cannot pay it. Never raises: an unparseable record is skipped, and finding
    nothing yields (None, "-"), the fail-open answer."""
    idx = None
    try:
        for i, o in enumerate(objs):
            if _is_compaction_summary(o, objs[i - 1] if i else None):
                idx = i
    except Exception:
        return None, "-"
    if idx is None:
        return None, "-"
    return idx, _compaction_id(objs[idx])


def _has_sentinel(window):
    """True if ANY assistant chat line in the turn opens with the `🚨` sentinel
    glyph (root §3.2.6), bold wrapper and variation selector tolerated.
    Harness-authored lines are skipped, as everywhere else here. Presence
    SUPPRESSES the block, so scanning the WHOLE window —— not just the turn's
    first line, though §5.1 owes it immediately —— is the fail-open choice: a
    late sentinel is an ordering fault, not the total omission this catches.
    Never raises."""
    for o in window:
        try:
            if o.get("type") != "assistant" or o.get("isApiErrorMessage") is True:
                continue
            if (o.get("message") or {}).get("role") != "assistant":
                continue
            for ln in _message_text(o).splitlines():
                t = ln.strip()
                if t.startswith("**"):
                    t = t[2:].strip()
                if t.replace(_VS16, "").startswith(_G_SENTINEL):
                    return True
        except Exception:
            continue
    return False


def _window_spoke(window):
    """True if the turn produced at least one assistant record. An EMPTY window
    is likelier a transcript this hook mis-parsed than an agent that genuinely
    emitted nothing, so SHAPE C declines to judge it. Never raises."""
    for o in window:
        try:
            if o.get("type") == "assistant":
                return True
        except Exception:
            continue
    return False


def _ended_on_api_error(window):
    """True if the turn's LAST assistant record is harness-authored (e.g. "You've
    hit your session limit"). Such a turn was terminated FOR the model, so a
    block would spend the one allowed forced turn on an agent that cannot act.
    Only the final assistant record is consulted —— an error earlier in a turn
    that later recovered is not a termination. Never raises."""
    for o in reversed(window):
        try:
            if o.get("type") != "assistant":
                continue
            if (o.get("message") or {}).get("role") != "assistant":
                continue
            return o.get("isApiErrorMessage") is True
        except Exception:
            return False
    return False


def _is_urgent_stop(line):
    """True if `line` is a `⚠️` blocker (root §3.2.5) or the `🚨` post-compaction
    sentinel (§3.2.6). Both are legitimate, deliberate early stops that must
    never be held open —— the blocker especially, since holding one open delays
    exactly the message the user most needs to see."""
    t = line.strip()
    if t.startswith("**"):
        t = t[2:].strip()
    return t.replace(_VS16, "").startswith(("⚠", "🚨"))


def _is_io_declaration(line):
    """True if `line` is an I/O declaration (root §3.2.1–3), tolerating the
    `**…**` bold wrapper §3.1.6 puts round one and the emoji variation
    selector. Only the GLYPH is tested, not the file-list shape: `clint.py`
    already owns declaration shape, and a malformed declaration is still the
    turn-ending-on-a-declare situation this hook is looking for.

    Deliberately EXCLUDES `🦈` (§3.2.4), unlike `_is_declaration_end`. This
    function's only caller is SHAPE B, where a hit SUPPRESSES the block —— and a
    turn that pushed, declared its SHAs, and never declared the `response_` is
    PRECISELY shape B's failure ("a successful push with no declaration looks,
    from the user's screen, exactly like a failed one"). Widening this set
    would therefore delete coverage of the case the new glyph makes MORE
    likely, not less."""
    t = line.strip()
    if t.startswith("**"):
        t = t[2:].strip()
    return t.replace(_VS16, "").startswith(_IO_GLYPHS)


def _is_declaration_end(line):
    """True if `line` is the last line a DECLARATION BATCH ends on —— any I/O
    glyph (§3.2.1–3) or the SHA glyph `🦈` (§3.2.4).

    SHAPE A's whole signal is "the turn stopped ON its declaration batch". When
    the SHA declaration was split out of `➡️` into its own class, `🦈` became the
    line a batch ordinarily ENDS on (root §3.1.6.3's example), so a batch-end
    test that knew only the I/O glyphs was silently defeated by the protocol
    change: an m2 turn that committed, declared, and never sprinted logged
    `not_declaration_end` and was let through. Verified against the live hook
    before and after this line existed."""
    t = line.strip()
    if t.startswith("**"):
        t = t[2:].strip()
    return t.replace(_VS16, "").startswith(_BATCH_END_GLYPHS)


def _slog_on_disk_at_or_after(query_path):
    """True if a `*slog_*.md` at least as NEW as this `query_` already sits in
    the query's own folder —— upgrade 2, and the repair for a PROVEN false block.

    A turn was blocked with `m2=query sprint=none` for merely RE-READING a
    three-day-old query whose sprint had run days earlier; that mission's slog
    had been on disk the whole time. `universal/sprint.md`'s Preamble makes the
    slog a MANDATORY pair with every sprint ("Neither is EVER optional"), so a
    slog this new is proof the sprint already ran —— evidence that outlives the
    session, which an in-window `file_path` scan can never supply.

    `>=` against the query's own TS is what makes this a STALENESS test rather
    than a blanket disarm: a query written now carries the newest TS in its
    folder, so nothing can be >= it and a genuine fresh `#m2` is untouched. Any
    `*slog_*` counts, never a CP-prefix match, for the reason root §5.8.1 gives
    for its own glob —— a prefix match is narrower, and narrower means MORE
    firing, the wrong direction for a signal that can only suppress.

    Never raises, and every failure yields False (no suppression), so a missing
    or unreadable folder simply leaves the other signals to decide."""
    try:
        m = _TS_SUFFIX_RE.search(os.path.basename(query_path))
        if not m:
            return False
        qts = m.group(1)
        folder = os.path.dirname(os.path.abspath(query_path))
        for i, name in enumerate(os.listdir(folder)):
            if i >= _MAX_DIR_ENTRIES:
                break
            if not _SLOG_FILE_RE.match(name):
                continue
            s = _TS_SUFFIX_RE.search(name)
            if s and s.group(1) >= qts:   # 12-digit TS: lexical == chronological
                return True
    except Exception:
        pass
    return False


def _sentinel_budget_spent(cid):
    """True if this ONE compaction has already cost its `_MAX_SENTINEL_BLOCKS`,
    counted from this hook's own log by `cid=`.

    The per-prompt ledger bounds blocks per PROMPT; this bounds them per
    COMPACTION, which the per-prompt ledger cannot do now that a debt survives
    across prompts. Without it, a model answering every block with the lone `.`
    escape would be blocked once per prompt for the rest of the session.

    UNIDENTIFIABLE COMPACTION (`-`) -> False: nothing can be counted, so the
    per-prompt ledger governs alone, exactly as before this existed.
    UNREADABLE LOG -> True (treated as spent), the same conservative direction
    `_already_blocked` takes —— without a ledger nothing can prove a further
    block would be within budget, and repeating is worse than missing."""
    if not cid or cid == "-":
        return False
    try:
        if not os.path.isfile(_LOG):
            return False
        with open(_LOG, "r", encoding="utf-8", errors="replace") as fh:
            tail = fh.read().splitlines()[-_LEDGER_TAIL_LINES:]
    except Exception:
        return True
    needle = "\tcid=%s\t" % cid
    spent = sum(1 for ln in tail
                if "\taction=block_nosentinel\t" in ln and needle in ln)
    return spent >= _MAX_SENTINEL_BLOCKS


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


def _log_event(sid, action, pid="-", m2="-", sprint="-", compact="n/a",
               cid="-", first="-"):
    """Append ONE diagnostic line for ANY invocation, verdict or not. Returns
    True only if the line reached disk —— the block path DEPENDS on that return
    value, because an unrecorded block is a block that can repeat (see docstring
    LOOP GUARD). Every other caller ignores it: a lost diagnostic costs
    visibility, never enforcement.

    `compact` defaults to `n/a` —— "this run exited before the compaction test
    could run" —— so a stage that never reached it can never be misread as one
    that reached it and found nothing (docstring FAIL OPEN). `cid` names WHICH
    compaction that verdict is about; the per-compaction block budget counts
    these, so it must be written on the block line or the budget cannot see it."""
    ok = False
    try:
        with open(_LOG, "a", encoding="utf-8") as lf:
            lf.write(
                "%s\tsession=%s\tpid=%s\taction=%s\tm2=%s\tsprint=%s"
                "\tcompact=%s\tcid=%s\tfirst=%s\n"
                % (datetime.now().isoformat(timespec="seconds"), sid, pid,
                   action, m2, sprint, compact, cid,
                   str(first)[:200].replace("\t", " ").replace("\n", " ")))
        ok = True
    except Exception:
        pass
    _prune_log()
    return ok


# The ledger needles —— every action name that MEANS a block was issued, matched
# whole (the surrounding tabs are part of each needle) rather than by prefix. A
# prefix would also swallow `block_unlogged`, which is precisely the case where
# NO block was issued and a later one must stay possible. All three shapes share
# one budget, so all three names sit here.
_BLOCK_ACTIONS = ("\taction=block\t", "\taction=block_nodeclare\t",
                  "\taction=block_nosentinel\t")


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
    return any(any(n in ln for n in _BLOCK_ACTIONS) and needle_pid in ln
               for ln in tail)


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
# and adds moving parts to a gate that can BLOCK a turn-end.
_HOOK_STDIN_WAIT_S = 2.0

# Extensions a caller reaches for when treating this file as a CLI. This hook
# takes NO argv at all —— it is registered bare on `Stop` —— so any file-shaped
# argument is a caller holding the tool wrong, never a mode word.
_HOOK_FILEY_EXTS = frozenset((".md", ".py", ".sh", ".json", ".jsonl", ".txt",
                              ".html", ".yml", ".yaml", ".csv"))

_HOOK_STDIN_HOWTO = (
    '  printf \'%s\' \'{"hook_event_name":"Stop",'
    '"transcript_path":"/abs/session.jsonl"}\' \\\n'
    '    | python3 cscpt/mlint.py\n'
)


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
    # Exit 3, never 2. On THIS hook's own event a 2 is the BLOCK ——
    # it is the single channel by which the three shapes above force a
    # turn-end to be refused and the model to keep working. A hand
    # invocation must never be able to reach for that: it would stall a
    # turn on the strength of a payload nobody sent. Every other non-zero
    # code merely shows this message; none of them blocks anything.
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
            "transcript to read arrives in the payload, never on the command "
            "line" % stray[0])
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

    # Is an UNPAID compaction in context? Root §5.1.1 defines the debt as "a
    # summary you did NOT write is in context w/ no LATER `🚨` of yours", and
    # §5.1.4 keeps it owed on any later turn until paid —— so this asks about the
    # whole transcript, NOT about the record that opened this turn. Keying it on
    # the opener is the hole this replaces: one later user message and the debt
    # vanished for good. Needed BEFORE the override gate below, not just SHAPE C.
    #
    # Tail truncation fails OPEN by construction: if `_load_records` dropped the
    # pair, no summary is found, `compact=no`, and nothing fires.
    try:
        compact_idx, compact_cid = _last_compaction(objs)
        if compact_idx is None:
            compacted, compact = False, "no"
        elif _has_sentinel(window):
            compacted, compact = False, "ok"      # paid in THIS turn
        elif _has_sentinel(objs[compact_idx + 1:]):
            compacted, compact = False, "paid"    # paid in an EARLIER turn
        else:
            compacted, compact = True, "no"
    except Exception:
        compact_idx, compact_cid = None, "-"
        compacted, compact = False, "err"

    # A compaction summary is HARNESS text, not something the user typed, so it
    # supplies no typed-message EVIDENCE: a `#m2` quoted at column 1 inside a
    # recap must not arm a turn nobody invoked it on. Blanking it here can only
    # ever REDUCE firing, so it is safe. The `query_`-file route is untouched.
    #
    # GATED ON THE TRIGGER ITSELF, never on `compacted`: an unpaid debt now
    # persists across turns, so `compacted` is True on turns a HUMAN opened, and
    # blanking those would delete real typed evidence AND the real `override`
    # they may carry. Only the turn whose opener IS the summary is blanked.
    trigger_is_summary = compact_idx is not None and compact_idx == start - 1
    typed = "" if trigger_is_summary else _message_text(trigger)

    # The `override` EXEMPTION is a different question from evidence, and must
    # NOT be blanked with it. BOTH real summaries on disk carry the word
    # incidentally (each recaps a turn in which an override was granted), so
    # reading them here at all would exempt every compaction turn and leave
    # SHAPE C dead on arrival. But dropping the exemption outright would WIDEN
    # the m2 shapes onto compaction turns that were exempt before —— and the m2
    # `query`-evidence route has a live false-positive history (a `#m2` inside
    # an OLD `query_` the turn merely re-read blocked a real turn on
    # 202608070450). So the exemption is kept for the m2 shapes, on the real
    # text, exactly as before, and only SHAPE C is placed beyond its reach:
    # §5's sentinel is owed on every compaction without exception, and an
    # exemption must in any case be a live instruction for the turn at hand,
    # which a machine-written recap of an older one is not. The escape from a
    # SHAPE C block stays the lone `.` its message names.
    overridden = bool(_OVERRIDE_RE.search(_message_text(trigger)))
    if overridden and not compacted:
        _log_event(sid, "exempt:override", pid=pid, compact=compact,
                   cid=compact_cid)
        return 0

    # --- Gather evidence in ONE pass over the window -----------------------
    query_paths = []
    sprint_why = ""
    response_written = False
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
            elif _RESPONSE_FILE_RE.match(base) and name in _WRITE_TOOLS:
                response_written = True      # the declaration is now OWED
            elif not sprint_why and os.path.realpath(fp) == _SPRINT_MD_REAL:
                sprint_why = "sprint_md"
            elif _QUERY_FILE_RE.match(base) and fp not in query_paths:
                if len(query_paths) < _MAX_QUERY_FILES:
                    query_paths.append(fp)

    m2_why = "typed" if _invokes_m2(typed) else ""
    m2_path = ""
    if not m2_why:
        for path in query_paths:
            if _invokes_m2(_read_query_text(path)):
                m2_why, m2_path = "query", path
                break

    # DISK-SLOG SUPPRESSION (docstring SPRINT EVIDENCE (a2)). Only the `query_`
    # route can point at a mission older than this turn, so only it is checked ——
    # a TYPED `#m2` is by definition an instruction for now. The strongest
    # in-window signal still wins, so this never overwrites one.
    if m2_why == "query" and not sprint_why and _slog_on_disk_at_or_after(
            m2_path):
        sprint_why = "slog_disk"

    last_line = _last_chat_line(window)

    def _issue(action, msg, compact_note=None):
        """Loop-guard, record, then block. ORDER IS LOAD-BEARING: the ledger
        line is written BEFORE the block is issued, because a block whose record
        did not land is a block that can repeat. The ledger is SHARED by all
        three shapes —— one forced turn per prompt, never one per shape."""
        note = compact if compact_note is None else compact_note
        if _already_blocked(pid):
            _log_event(sid, "already_blocked", pid=pid, m2=m2_why or "-",
                       sprint=sprint_why or "none", compact=note,
                       cid=compact_cid, first=last_line)
            return 0
        if not _log_event(sid, action, pid=pid, m2=m2_why or "-",
                          sprint=sprint_why or "none", compact=note,
                          cid=compact_cid, first=last_line):
            _log_event(sid, "block_unlogged", pid=pid, m2=m2_why or "-",
                       compact=note, cid=compact_cid, first=last_line)
            return 0
        # Exit 2 + STDERR is the ONLY Stop channel that reaches the model and
        # blocks the stop (`hook_guide.md` §6). At exit 2 the harness ignores
        # stdout entirely, so nothing may be written there.
        sys.stderr.write(msg)
        return 2

    # SHAPE C first, and independent of `#m2` altogether. §5.2 halts everything,
    # so a turn carrying an unpaid compaction has no business running an m2
    # sprint anyway —— the sentinel and the two lists come before any other
    # output. The sentinel test itself already ran above (it is what decides
    # `compacted`); everything here is an exemption evaluated on the CURRENT
    # window, because whether THIS turn could comply is a question about THIS
    # turn, never about the whole post-compaction history.
    if compacted:
        if not _window_spoke(window):
            compact = "no_output"
        elif _ended_on_api_error(window):
            compact = "api_error"
        elif _is_urgent_stop(last_line):
            compact = "urgent"
        elif _sentinel_budget_spent(compact_cid):
            # This compaction has had its allowance. Owed-until-paid would
            # otherwise re-arm on every prompt for the rest of the session.
            compact = "spent"
        else:
            return _issue("block_nosentinel", _NOSENTINEL_MSG,
                          compact_note="owed")

    # The deferred half of the `override` gate. SHAPE C has now had its say, so
    # the m2 shapes below inherit the exemption on exactly the terms they had
    # before SHAPE C existed —— no compaction turn that was exempt from them
    # yesterday becomes blockable by them today.
    if overridden:
        _log_event(sid, "exempt:override", pid=pid, compact=compact,
                   cid=compact_cid)
        return 0

    if not m2_why:
        _log_event(sid, "no_m2", pid=pid, sprint=sprint_why or "-",
                   compact=compact, cid=compact_cid)
        return 0

    # SHAPE B next —— a turn that never declared cannot also have ended ON a
    # declaration, and unlike shape A it is INDIFFERENT to whether the sprint
    # ran: the 202608050209 turn dispatched its whole sprint and still never
    # emitted the line the owner needed to click.
    if (response_written and not _has_output_declaration(window)
            and not _is_io_declaration(last_line)
            and not _ended_on_api_error(window)
            and not _is_urgent_stop(last_line)):
        return _issue("block_nodeclare", _NODECLARE_MSG)

    if sprint_why:
        _log_event(sid, "sprint_ran", pid=pid, m2=m2_why, sprint=sprint_why,
                   compact=compact, cid=compact_cid)
        return 0
    if not _is_declaration_end(last_line):
        # Ended on a blocker/sentinel/prose/lone-dot/nothing —— a different
        # situation, and one of those is a legitimate urgent stop.
        _log_event(sid, "not_declaration_end", pid=pid, m2=m2_why,
                   compact=compact, cid=compact_cid, first=last_line)
        return 0

    return _issue("block", _BLOCK_MSG)


if __name__ == "__main__":
    sys.exit(main())
