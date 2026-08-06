# Response to ccsim_query_202608070415.md
*Memory renamed and corrected; two SAs on the last holes*

## 131. re 126.8 —— Memory Fixed and Renamed, Cleanly

- 131.1. Done under your override. `feedback_no_chat_text.md` → `feedback_no_chat_prose.md`, and the content now says SIX declaration types, listing `🦈` in its right place between `➡️` and `⚠️`.
- 131.2. The self-check line —— the one operational sentence in the file —— now reads `✅ / ⇠ / ➡️ / 🦈 / ⚠️ / 🚨`. That is the line that actually gets used, so it mattered most.
- 131.3. "Cleanly across" covered four surfaces, not just the file: the memory itself, its `MEMORY.md` index line, the mirror MAP in `mirror.sh`, and the backup copy (renamed via `git mv`, so history follows).
- 131.4. Verified rather than assumed: `mirror.sh sync` returns exit 0, and `mirror_test.sh` is 13/13.
- 131.5. Historical mentions in `sessions/` comms files are left as written —— they recorded the name accurately at the time, per the standing convention.
- 131.6. One line added that was not asked for, and I think earns its place: **verify the count before quoting it.** That file said "five" for two months after `🦈` landed. The set is defined by root §3.2, which is authoritative; the memory is a reminder, not a second source of truth.

## 132. Dispatched, Reporting Below

- 132.1. §127.6's real hole —— an Opus SA is closing it. The instruction and the range-command option are both on the table; it will say which it took and why.
- 132.2. §128 —— an Opus SA is checking what genuinely remains. It has explicit permission to answer "already closed" and change nothing, which is the honest outcome if that is what it finds.
- 132.3. Both were told your false-positive-over-false-negative ruling, since it bears directly on the two exclusions still standing in the `read`/`#r` advisory.

## 133. re 127.6 & 128 —— Both Closed

- 133.1. The SHA hole is fixed at source: root §3.2.4.3 now says to run the command RIGHT AFTER EACH commit and carry the SHA forward, with the reason inline (run once at TEA3 it yields HEAD alone). `m2.md` step 2 changed from "its SHA waits for TEA3" to "capture SHA now; `🦈` at TEA3" —— that clause was the single most likely bug site, since m2 mandates the interim commit.
- 133.2. ⚠️ CORRECTING MYSELF: my §128.5 priced your decision on the wrong axis. The 970-hit figure was every filter removed, not the two exclusions actually in question. The real cost of dropping both is **581 → 791**. You were being asked to rule on a number roughly twice the true one. Struck at source.
- 133.3. And on that corrected number the ruling is KEEP BOTH, on evidence rather than deference: of 222 hyphenated hits, **122 are tenseless** (`read-only` 41, `delta-read`, `machine-read` —— compound adjectives with no tense to judge), and all 13 tool-name hits are the proper noun, zero verbs.
- 133.4. So your false-positive-over-false-negative rule does not REACH these two classes —— there is no false negative hiding in them to buy. Going maximal would add 210 flags, every one unactionable.
- 133.5. ⚠️ One genuine residual, named not buried: `re-read` DOES carry the /riːd/ vs /rɛd/ ambiguity the advisory exists to kill, and the exclusion silences it —— 100 occurrences. Closing it needs a house form (`re-#r`) that does not exist. Your call whether to mint one.
- 133.6. The range-from-turn-start command was tested and WORKS, but was deliberately kept as recovery only: a range is a DAG window, so it swallows a parallel session's commits. Making `🦈` range-derived would make `close.md`'s "cross-check your own `🦈` lines" circular.
- 133.7. A mechanical check in `clint` was considered and REFUSED, with reasons I accept: it scopes by prompt id whilst a practical turn spans mid-turn messages, so it would false-warn precisely on the long interrupted turns that actually have interim commits.
- 133.8. Suites: dlint 302 → 307, clint untouched at 118/118.
