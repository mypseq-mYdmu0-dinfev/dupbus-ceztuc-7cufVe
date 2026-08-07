# AJAP: Post-Compaction Protocol Cannot Live On A Hook —— Findings To Adopt

## The user's own words (relayed verbatim, deliberately not interpreted for you)

> do that for both `#inv` & cockpit ses

He said neither the drafting session nor its sub-agent needs to understand what those
are. They are yours. Apply the whole of this file to both.

---

## 1. The finding —— PostCompact has no model channel, and never had one

- PostCompact is a REAL, dispatched hook event. That is not in doubt.
- But the harness's own hook registry defines it as: "Exit code 0 - stdout shown to
  user. Other exit codes - show stderr to user only".
- Its dispatch function returns a user-display string ONLY. No `additionalContext`,
  no yield, no exit code that reaches the model. Contrast `Setup`, whose registry
  entry literally says "JSON additionalContext shown to Claude".
- NET: any post-compaction protocol that relies on the hook to INSTRUCT the model has
  never worked and cannot work. Not "was misconfigured" —— cannot work.
- This was found the expensive way. On 07/08/2026 the default repo's session compacted,
  the model obeyed the summary's own "Resume directly —— do not acknowledge the
  summary", skipped root `CLAUDE.md` §5 in full (no sentinel, no halt, no context
  lists), and it surfaced only because the user noticed.
- Full write-up, already permanent, read it rather than this summary:
  `dupbus-ceztuc-7cufVe/cp/ccsim/hook_guide.md` §6 (channel table) and §6.9.

## 2. The failure is INVISIBLE —— so log, or you can never answer "did it fire?"

- PostCompact emits no `hook_started`/`hook_progress` transcript record. A hook that
  fired flawlessly and one that never fired leave an IDENTICAL trace —— none.
- The 07/08 investigation could not establish whether the hook had run at all.
- If AJAP keeps or adds any PostCompact hook, make it WRITE A LOG LINE per invocation
  before anything else. One line, one command to check. Otherwise the next incident
  repeats this exact dead end.
- Reference implementation: `dupbus-ceztuc-7cufVe/.claude/post_compact.sh` —— logs a
  `stage=` per invocation, fails OPEN when `cwd` is absent, and is kept ONLY as a
  user-facing alarm plus audit record. It is explicitly NOT the enforcement.

## 3. The fix that does work —— observable trigger, in the always-present file

- Put the protocol where the model ALWAYS has it: the instruction file the harness
  rebuilds into the system prompt on every request. No hook delivery needed.
- Trigger it on an OBSERVABLE the model can check about itself:
  - context opens on a conversation summary it did NOT write this turn; OR
  - anything tells it to "resume directly" / "as if the break never happened".
- VOID that instruction EXPLICITLY in your own text. It is the harness default and it
  is what gets obeyed otherwise. Saying "follow the protocol" is not enough —— the
  competing imperative has to be named and cancelled by name.
- The default repo's rewritten `CLAUDE.md` §5.1 is the working example. Copy the
  SHAPE, not the words: five sub-points, each an observable or a cancellation.
- Honest caveat, per CCSIM's own bar: this is still prose competing with an injected
  imperative. It is necessary and not provably sufficient. See §6 below.

## 4. Copy the CHANNEL check, not a NAME check

- Every registered event name was valid on the day this failed. A guard that validates
  event NAMES would have passed the broken config without a murmur.
- Validate what an event can REACH. "Is this event name spelled right?" is the wrong
  question; "can anything this event emits arrive in the model's context?" is the one
  that catches it.
- Same discipline for the reverse case: pin the fact with a test that FAILS if the
  event ever GAINS a model channel, so a future capability is an alarm, not a silent
  missed opportunity. The default repo does this in
  `cp/ccsim/sandbox/post_compact_regression_test.py` (43 checks).

## 5. Which binary is authoritative —— an audit against the wrong one proves nothing

- The Claude Desktop app runs its OWN bundled claude-code from
  `~/Library/Application Support/Claude/claude-code/<version>/`, NOT the Homebrew CLI
  on `PATH`.
- Checked on this Mac at 202608070505: Application Support carries 2.1.221, whilst
  `which claude` → `/opt/homebrew/bin/claude` reports 2.1.201. Different builds.
- So resolve it before quoting any registry or payload shape:
  `ls -d "$HOME/Library/Application Support/Claude/claude-code/"*/` gives the bundled
  version; `which claude && claude --version` gives the CLI one. If they differ, the
  bundled one is what actually ran your session, and the CLI is a decoy.

## 6. CCSIM is adding a mechanical turn-end gate —— ask for it, do not rebuild it

- A blocking Stop-hook check is being landed in the default repo so the sentinel stops
  depending on the model remembering. Its shape is not settled here and is not yours
  to reimplement blind.
- Ask CCSIM for it when you want the same guarantee. Reimplementing a blocking Stop
  hook from a paraphrase is how two divergent half-enforcements get shipped.
- If you do end up writing any Stop hook of your own, the governing test is
  `hook_guide.md` §6.4.3: block ONLY when the blocked agent has real work to spend the
  forced turn on. A block whose turn is empty by construction cascades into worse
  turn-end behaviour than the breach it was policing.

---

## 7. Your half —— what AJAP_repo has today (audited, read-only, 202608070505)

Findings, so you are not asked to rediscover them:

- AJAP_repo has NO hooks of any kind. `.claude/settings.json` and
  `.claude/settings.local.json` contain a `permissions` block and nothing else. No
  `hooks` key, no hook scripts anywhere in the tree.
- The only `post_compact.sh` on this Mac is the default repo's. It is registered on
  PostCompact in the USER settings file `/Volumes/FURY 2TB/.claude/settings.json`, so
  it fires in EVERY project —— but it self-scopes on the payload `cwd` and exits 0
  silently for any other repo. An AJAP-cwd session therefore gets NOTHING, not even
  the user-facing alarm.
- `protocols/migration.md` §4.3 retired an older `seek/.claude/post_compact.sh` with
  "never port". That directory no longer exists. Correct call —— but it means AJAP has
  had no post-compaction hook since, and nothing replaced it.
- `AJAP_repo/CLAUDE.md` (21 lines) has NO §5 equivalent and no compaction language.
- `#inv` DOES inherit §5: `inv/CLAUDE.md` § Unconditionals mandates reading
  `dupbus-ceztuc-7cufVe/CLAUDE.md` in full. So `#inv` gets the rewritten §5 for free
  —— but ONLY from the next session, and only if that reading actually happens.
- The cockpit does NOT. `#seek` opens `dir/CLAUDE.md`, and `protocols/eng.md`
  § Unconditionals says outright: "DON'T read `dupbus-ceztuc-7cufVe/CLAUDE.md`".
- So the cockpit's ENTIRE post-compaction protocol is `dir/CLAUDE.md` § COMPACTION
  HEDGE (the `clog_` block). It opens "On 🚨 PostCompact sentinel: emit it" —— gated
  on the hook by name, and on a sentinel whose exact wording appears in NO live AJAP
  file. `grep -rn "Compaction Detected"` across AJAP_repo hits only historical comms
  under `inv/2026/202607/`.
- Net: a cockpit session that compacts receives no hook output, holds no sentinel
  text, and is waiting on a trigger that cannot arrive. The hedge's clog discipline
  itself is sound —— the broken parts are the TRIGGER and the missing sentinel.

## 8. What is being asked (#SA the audit, #MA the judgement calls)

1. Fix the cockpit first —— it is the one with no protocol at all. Give
   `dir/CLAUDE.md` § COMPACTION HEDGE an observable trigger per §3 above, and inline
   the sentinel's exact wording so the cockpit does not need a file it is forbidden to
   read. Keep the override (resume from clog, never halt) —— that part is right.
2. Decide whether `#inv` inheriting §5 by reference is enough, or whether
   `inv/CLAUDE.md` should state the trigger itself. Inheritance is only as good as
   that reading actually happening.
3. Note the sprint interaction: `dupbus-ceztuc-7cufVe/universal/sprint.md`
   § Interactions holds that a compaction during a `#sprint` still emits the sentinel.
   There is no exemption from the SENTINEL, only from the halt-and-wait. The cockpit
   hedge is the same pattern —— write it that way explicitly.
4. If you add any hook, log first (§2) and validate the channel, not the name (§4).
5. Report what you changed and what you deliberately left alone, with the reason.

## Ownership

- CCSIM owns the hooks, the default root `CLAUDE.md`, and `hook_guide.md`. This is a
  handover of findings, not a patch applied across the boundary —— nothing in
  AJAP_repo was modified.
- If any of it is wrong for AJAP, say so rather than complying silently. The user would
  rather hear the objection, and the channel fact is the only part that is not
  negotiable.

## Reminder

- Rename and move this file per `sessions/queued_queries/README.md` before addressing
  it.
