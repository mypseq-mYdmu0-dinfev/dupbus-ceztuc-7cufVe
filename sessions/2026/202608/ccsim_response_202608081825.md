# Response to ccsim_query_202608081825.md
*Your edit was swept by `git add -A`; now mechanically impossible*

## 222. re Major Violation —— Confirmed, and #rephrase

- 222.1. **WHAT** —— TEA1 ran `git add -A`, so commit `05b938d9` swept your IN-PROGRESS edit to `universal/glossary.md` (the Preamble restructure) into a CCSIM commit and pushed it.
- 222.2. **IF-UNFIXED** —— every turn end can commit whatever you happen to be typing. Worse than untidy: it can capture a half-written file, and §3.1.6.1.5 exists precisely because that risks clashing with your own save.
- 222.3. **PRE-FIX-QB** —— none.
- 222.4. **PUSH-RISK** —— a gate on staging shape could refuse a legitimate mass-move commit. Ruled: it still refuses, and the correct answer there is explicit paths plus §3.1.6.1.6.3's split, which you added for exactly that case.
- 222.5. **OUTCOME** —— FIXED as a gate in `alint`, which already parses every Bash command as a registered PreToolUse hook.
- 222.6. ⚠️ THE AGGRAVATING FACT: this is the THIRD time `git add -A` has done damage —— 88 voided files published on 07/08, your glossary edit on 08/08. Prose failed after the first, so §8.7 says prose cannot repair it.
- 222.7. Checked and cleared, so you know the blast radius: the seven `CLAUDE.md` lines in that same commit were ALL mine (§5.5.5). Only `glossary.md` was yours.

## 223. The Gate, and It Caught Me Within a Minute

- 223.1. It blocks `git add -A`, `--all`, `add .`, `commit -a`/`-am`, through `&&` chains, behind a `cd`, and via `git -C`.
- 223.2. The message gives the correct action rather than only the prohibition: run `git status --porcelain`, stage by name, and if that list is long, split the commit.
- 223.3. ⭐ It fired on my OWN test command within a minute of landing —— because the test's fixtures CONTAIN the literal text, and the first draft matched the string anywhere in a command.
- 223.4. That is the contamination trap again, and this time it bit the gate itself. Fixed by anchoring at COMMAND POSITION: the match must start the command or follow `;`, `&&`, `||`, `|` or a newline.
- 223.5. So a mention inside a heredoc, a `-c` script or a commit message can no longer fire it —— nine such cases are pinned as silent.
- 223.6. I kept that misfire in the code's own docstring rather than tidying it away: a gate that cries wolf is a gate that gets switched off.
- 223.7. New suite `alint_stage_all_regression_test.py`, 23 checks. 29 suites green.

## 224. re 201.2 and 202 —— Taken, One Deferred

- 224.1. re 201.2 —— "many lines" → "multiple lines". Noted for the `clint` message; deferred with §202 below, since both touch the same file.
- 224.2. re 202 —— you are right and the fix is obvious now you have said it: count the `🦈` lines in the LAST TEA block (after the final `➡️`, before any next `✅`), not across the whole window.
- 224.3. On your CIIW: you are correct that there should be ONE TEA set per turn even after a forced continuation. My §202 worried about a shape that should never occur —— so the window-scoping fix removes the concern rather than mitigating it.
- 224.4. ⚠️ NOT BUILT this turn. The SA carrying it died on the session limit, and the limit does not reset until 22:10. Deferred to next session; brief in the `close_`.

## 225. re 208.6 and 209.7 —— Both Deferred, With the Reason

- 225.1. Both were dispatched to the same SA that died on the session limit.
- 225.2. §208.6, the SHA resolvability gate: the full spec is already in `backlog.md`, so nothing is lost —— next session builds from there.
- 225.3. §209.7, the standfirst ≤90-char check: same, and it is a small `dlint` addition.
- 225.4. Per §9.02.4 a limit-killed agent's task is NOT done, so neither is recorded as complete.

## 226. re the Serious Numbering Error —— Both Faults Fixed

- 226.1. Confirmed: `ccsim_response_202608081632.md` carried TWO §204s and a misplaced §208.
- 226.2. CAUSE: each section was appended by a separate `Edit` anchored to a different point, so a later append landed mid-file and a number was reused.
- 226.3. ⚠️ It was NOT nlint's fault, and this one is not the Bash-bypass either: nlint's checks cover the tenth-sibling rule and level-1 resets, not a REPEATED heading. That is a genuine gap in nlint, now logged.
- 226.4. FIXED: 1632 is resequenced to §201`~`209 in your query's order, and the next response shifted to §210`~`221 and re-ordered so its sections ascend.
- 226.5. Every inbound citation was repointed —— two in `backlog.md`, two in the `close_`, two inside the responses themselves.
- 226.6. Content preservation was PROVEN, not assumed: the line multiset is identical before and after, so nothing was lost or invented by the transform.
- 226.7. ⚠️ The SA that started this died mid-way, having written a note claiming the second file was "shifted" when it was not. I finished the work and made that note true rather than leaving a false claim in the record.

## 227. re Context —— What Goes to Next Session

- 227.1. Done here because it needed my context: the violation analysis, the gate, and the whole numbering repair.
- 227.2. Deferred to next session, all recorded in the `close_`: §202's TEA-block counting, §208.6's SHA gate, §209.7's standfirst check, your §205/§206/§212.5.2 audits, the `cscpt/README.md` leanness sweep, and the still-owed sweep since August.
- 227.3. 🟡 Your §205's question —— whether nlint is truly gap-free —— now has a concrete first answer from §226.3: it is not. A repeated heading passes today.
