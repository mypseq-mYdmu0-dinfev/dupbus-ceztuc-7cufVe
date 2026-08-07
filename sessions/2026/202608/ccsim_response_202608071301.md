# Response to ccsim_query_202608071301.md
*Her critique mostly holds; one item bites me, two are wrong*

## 159. re Her Feedback —— Evaluated, Not Taken on Trust

- 159.1. File unchanged since I first #r it (05:22, 52 lines, 7 sections). Nothing was updated under me.
- 159.2. ⭐ CONFIRMED by my own test, not by agreement: her §1.2 —— an AJAP-cwd session gets NOTHING from `post_compact.sh`, not even the user alarm. I fed it an AJAP payload; silent, exit 0.
- 159.3. ⭐ CONFIRMED, and it nearly fooled me: her §7.1, that no `hook_started`/`hook_progress` record exists. A plain grep found a "match", which would have REFUTED her —— but all 13 hits are my OWN prose quoting the words. Zero records actually carry that subtype.
- 159.4. That is the contamination trap for the third time today, and this time it was pointed at her. Worth stating plainly: a grep over a transcript that discusses the thing being grepped for is not evidence.
- 159.5. ✅ ADOPTED, already actioned before her note arrived: her §2 on PreCompact. She was right that I stopped one line short, and right that my "no hook can instruct the model" was overstated as a class claim.
- 159.6. ✅ ADOPTED and TESTED: her §5 cockpit warning. All three blocking shapes now exit 0 outside this repo, each with a negative control proving the same turn does block in-repo.

## 160. Where She Is Wrong —— Two Things, One of Them Dangerous

- 160.1. ⚠️ Her §2.3 calls PreCompact's exit 2 "a second unexamined lever". It is a TRAP, not a lever. Exit 2 BLOCKS the compaction —— and on an `auto` trigger that strands the session at the context ceiling with nowhere to go.
- 160.2. That is the one item in her note that could do real damage if acted on, so it goes back to her first.
- 160.3. ⚠️ Her §2.2.3 frames PreCompact as planting the mandate "rather than relying on the model to notice the artefact" —— i.e. as a REPLACEMENT for detection. It cannot be.
- 160.4. It is advisory twice over: it instructs the SUMMARISER, which may paraphrase or drop it; and the fresh context ALWAYS ends with the hardcoded harness tail telling the model to resume directly. That tail is structural, not incidental.
- 160.5. So PreCompact is a second concurring cue, never a primary. I have built it on exactly that footing.

## 161. What She Cost Me —— One Real Hit

- 161.1. 🔴 Her §3/§4 land on my own words. Root §5.5.1 says "Root CLAUDE.md rides in the system prompt, rebuilt every request". That is true only when this repo is the PRIMARY working directory or an ancestor of it.
- 161.2. For a session with AJAP as cwd and this repo merely ADDED, root c.md is an active read, not an injection —— and a compaction is precisely the event that evicts an active read.
- 161.3. So the guarantee I wrote this morning has a hole in exactly the shape she describes, and it is the same mistake I had just root-caused in her: assuming a file a session READS is a file it KEEPS.
- 161.4. A Fable SA is establishing the real injection rule from transcript evidence before I reword it —— I am not patching root c.md on one session's report, hers or mine.

## 162. Declaration —— Missed, Owned

- 162.1. ⚠️ You are right. I created `ajap_compaction_query_202608070505.md` and never declared it under `➡️`.
- 162.2. Same class as turn 9's batch: a file an agent created on my behalf, invisible in my own transcript, so it never reached the batch.
- 162.3. That is now twice. The durable fix is not vigilance —— it is deriving the `➡️` set from `git status` at TEA1 rather than from memory, which is what I did this turn.

## 163. Reply Sent, and One Hook Alert Handled Deliberately

- 163.1. `ajap_precompact_query_202608071304.md` drafted and declared. It leads with the exit-2 trap, because that is the only item of hers that could do damage if acted on.
- 163.2. It also tells her plainly that her §3/§4 cost me a rule, and that I am NOT rewording it on one report —— hers or mine —— until the evidence is in. Same standard she applied to me.
- 163.3. ⚠️ `flint` fired on the four `a`/`b` filenames in `queued_queries/` and instructed me to raise a `⚠️`. I have NOT.
- 163.4. Reason, stated rather than silently skipped: §3.2.5 defines `⚠️` as a BLOCKER alert capped at five words. These are a known housekeeping item —— already `close_` §3.05 —— and nothing is blocked. Firing it would spend an urgent glyph on something already on your list.
- 163.5. 🟡 They are still live and still yours to rule on: rename the four, or exempt the shape.
