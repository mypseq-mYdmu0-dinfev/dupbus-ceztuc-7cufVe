# Response to ccsim_query_202608070300.md
*`🦈` broke a blocking hook silently; both renames costed; 22/22*

## 123. re flint Upgrade —— Built, Blocking, Proven Live

- 123.1. Done. A comms filename must now END at its 12-digit TS; `…0423a.md` is blocked at creation.
- 123.2. The message COMPUTES the fix rather than just naming the fault —— it offers the clean minute first, so your `a`/`b` pair lands on `0423`/`0424`, not `0424`/`0425`, and it skips minutes already taken by a sanctioned sibling.
- 123.3. A `response_` gets a different clause instead of a bump, because §3.5.3 binds its TS to its `query_` —— advancing it would trade one breach for another.
- 123.4. Exemptions verified against the live tree, not imagined: extensions (incl. `.pages.md`), and the Move Rule's `_moved_[dir]` in BOTH observed positions. Blocking that would have made the gate fight its own fix.
- 123.5. Calibrated on 11,589 files: 1,344 are comms-shaped, and only 10 carry a tail. Every other tail in the repo belongs to a non-comms file, which is why the rule is scoped to comms shape rather than to "has a TS".
- 123.6. ⭐ PROVEN LIVE: two real Writes to `…202608070000a.md` and `ccsim_query_202608070423b.md` were blocked by the harness, with the corrected name offered. Suite 83 → 117, the 18 new cases run against the old file first (all 18 failed).
- 123.7. 🟡 NEEDS YOUR RULING: six live files use `_r2` (a SECOND response to one query). The SA refused to exempt it, because `_r2` and `a` differ only in spelling —— carving one out reopens the other. Either rename the six or exempt `_r2` deliberately.
- 123.8. ⚠️ And you did not fix the `0423a/b` pair —— all four `a`/`b` files are still live in `queued_queries/`.

## 124. re Major Renaming Plan —— Costed, and the Verdict Splits

- 124.1. `universal/` → `gpcmd/`: **62 live files / 193 lines**, 8 executable sites. **3`~`4 turns.**
- 124.2. `sessions/` → `ses/`: **32 live files / 123 lines**, 10 executable sites. **3`~`4 turns.** Both, sequenced: **6`~`9 turns.**
- 124.3. ⭐ The risk you and I both expected is EMPTY: neither rename touches a hook registration. All 14 point at `cscpt/*`. So `hook_guide.md` §1.7's silent-death scenario does not apply.
- 124.4. ⚠️ But the real hazard is worse than a dead hook: **eleven sites degrade SILENTLY**. hlint stops resolving `#triggers`, plint stops reminding, tlint stops checking comms timestamps, flint stops enforcing cross-repo TS uniqueness, housekeeping reports an empty queue. Nothing crashes. You find out weeks later, by absence.
- 124.5. My honest read, and it splits: **`universal/` → `gpcmd/` earns its cost. `sessions/` → `ses/` does not.**
- 124.6. Why: `gpcmd/` + `gscpt/` + `cp/` states the general/narrow axis out loud, and §1.2.1 makes every session type `universal/glossary.md` at start —— it pays back daily.
- 124.7. Whereas `sessions/` is nearly INVISIBLE in daily use: §3.1.2 forces declarations to carry one slash, so comms are declared `202608/response_x.md`, never with the folder name. Most churn (1,066 files), least visible benefit, and it is the folder four test `SKIP_DIRS` guards depend on by literal name.
- 124.8. One point in `ses/`'s favour I should state: `glossary.md` already defines `ses = session`, so it is consistent with house terminology, not colliding.
- 124.9. If you want both: do `universal/` first and let it sit a fortnight. Silent degradation is found by absence, and one rename at a time is the only thing that makes "the reminder stopped appearing" attributable.

## 125. re Owed Answer —— It Is Called a Standfirst

- 125.1. British journalism calls it a **standfirst**; American press calls it a **dek**; software docs just say **preamble**. It is NOT frontmatter —— that term means specifically the `---`-delimited metadata block.
- 125.2. Standfirst is the precise word; preamble is the one nobody has to look up.
- 125.3. On operationalising ≤90 chars for it: `coding.md` § Markdown Hygiene already caps EVERY `.md` line at ≤90, so a standfirst is covered without a new rule. Adding one would be a second place for the same rule to drift.
- 125.4. If you want it named specifically so the rule is findable, that is one clause in § Markdown Hygiene rather than a new section. Say the word.

## 126. re 120 —— `🦈` Broke a BLOCKING Hook, Silently

- 126.1. ⚠️ This is the finding of the turn. Your new class defeated `mlint`'s SHAPE A —— its "did the turn stop on a declaration batch?" test knew only `✅`/`⇠`/`➡️`, and a batch now ENDS on `🦈`. Measured: `not_declaration_end` before, `block` after the fix.
- 126.2. So the `#m2` stall gate had been silently disarmed by a protocol edit. Exactly the class §8.7 exists for, and nothing would have surfaced it.
- 126.3. `clint` too, as you predicted: every compliant `🦈` turn was being logged as `yellow:prose` AND firing a user-facing warning. Fixed as its own contract (`sha_shape`), deliberately not folded into the existing I/O test —— that would have flagged your multi-repo `🦈 Default:` label as a prose tail.
- 126.4. Suites: clint 90 → 118, mlint 76 → 80, both directions pinned.
- 126.5. Also fixed: two stale `§3.4.8` refs in `hlint.py`, `hook_guide.md` §7.7.2 (it named four RETIRED clint tags and missed every current one), and a `§3.2.5`→`§3.2.6` ref in the glossary skill.
- 126.6. 🟡 TWO CONTRADICTIONS LEFT OPEN, deliberately —— you were editing `CLAUDE.md` live and §3.1.6.1.5 says not to write over you:
  - 126.6.1. §3.1.6.3 still reads "TEA3 —— I/O Declarations (for §3.2.1–3)", but its example now contains two §3.2.4 lines. `🦈` is not I/O. Suggest "TEA3 —— Declarations (for §3.2.1–4)".
  - 126.6.2. §3.4.8.2.2 appears TWICE (lines 176–177), then jumps to §3.4.8.2.4.
- 126.7. 🟡 PUSH-BACK, and I think it is right: "8 chars exactly" is not safely enforceable as an equality, because `git rev-parse --short=8` LENGTHENS its own output when 8 is ambiguous. Implemented as floor 8, ceiling 40 —— short is a real breach, long is git being careful. Overrule and it will pin 8.
- 126.8. ⚠️ HIGHEST-VALUE OPEN ITEM: your auto-memory `feedback_no_chat_text.md` still says "the five declaration types of §3.2.1–§3.2.5". It is now wrong, and it is the one surface I read EVERY session. §8.6.3.1 needs your explicit `override` before I may edit it.

## 127. re 102 —— Answered, Fixed, and One Real Hole

- 127.1. re 102.8, your actual question: `git rev-parse --short=8 HEAD` prints **exactly ONE** SHA. It is right for the per-turn `🦈` and useless for `close.md` §7.
- 127.2. Your placeholder was already gone (deleted in your own restructure), so the CLI went in at the equivalent spot: `git log --pretty=%h --abbrev=8 [1st_session_SHA]^..HEAD`. The `^..` matters —— without it your own first commit is excluded.
- 127.3. Honest caveat recorded with it: a range is a graph slice, so a parallel session's commits on the same branch fall inside it and no author/date filter removes them. Your `🦈` lines remain the only ground truth.
- 127.4. re 102.6 —— done. "abbrev" is gone from prose; §3.2.4.3 now says "8 chars exactly" and names the command with `(prints 1 SHA)` inside it.
- 127.5. re 102.7 —— yes, do it, and it is done. ⚠️ Worth knowing: your example did NOT contain real SHAs. It held MALFORMED ones —— `abc123456` is 9 chars and `xyz67890` is not hex —— so it was teaching the wrong shape whilst §3.2.4.3 mandated 8. Now `deadbeef`/`cafef00d`/`0ddba115`/`feedface`, all verified non-resolving in both repos.
- 127.6. ⚠️ 🟡 A REAL HOLE, and it is the one that corrupts `close.md` §7: §3.2.4.1 demands ANY commit this turn, but the CLI returns HEAD only. On an interim-commit turn —— which `#m2` step 2 MANDATES —— running it once at TEA3 under-reports. The fix is a sub-point telling CC to capture each SHA as it commits. Not added, under the cut-by-default rule. Your call.
- 127.7. re 102.5 —— agreed, well understood as written. re 102.4 —— your §3.2.3.2 exemption is effective; `🦈` grouping and `➡️` no-grouping now agree.

## 128. re 103 —— The `read` Check Was Wrong, and Worse Than Suspected

- 128.1. re 103.2 —— it did fire, but NOT on your line. And my §116.2 claim that all four exclusions were "safe under your rule too" was **overstated**.
- 128.2. The killer was one word: `is` in the non-past list, justified last turn as "present passive, cannot be past". False —— a passive `read` is the PARTICIPLE, pronounced /rɛd/, which is exactly the form `#r` disambiguates. Corrected in code and in the suite's docstring.
- 128.3. ⚠️ And a bigger false negative nobody asked about: `dlint_quick.py` DISCARDED the whole quick report on any non-blocking run, so the advisory only reached me when a RED happened to co-occur. Measured: it was delivered on **58 of 492** `response_` files (12%); now **256** (52%).
- 128.4. So the plumbing was hiding more than the matcher was.
- 128.5. ~Measured cost: 522 → 578 hits, against a 970-hit ceiling if fully literal.~ → **MIS-PRICED, corrected at §133.2.** The 970 was a different axis (every filter off, not the two exclusions in question). The real cost of dropping both is 581 → 791.
- 128.6. Suppressions dropped as you implied: no more once-per-session, no more 8-line truncation (a hit on line nine was detected then hidden).
- 128.7. re 103.1 —— the he/his rule landed in `coding.md` § Scripts & pcmd, one line, because that file loads exactly when a pcmd is being written. Breach audit: **28 occurrences over 8 files**, but 3 are legitimate quotation examples and the real work is TWO files (`numbered.md`, `branding.md`). Smaller than it looks; not fixed, as it is the supervised pass you deferred.
- 128.8. re 103.3 —— `m1.md` needs no change; your edit names the real failure mode. `m2.md` got ONE in-place clause, no new line: step 2 now says the mid-turn commit's SHA waits for TEA3's `🦈`, closing a gap where an agent would declare at step 2 and silently drop the SHA.

## 129. Turn Record

- 129.1. 22 of 22 suites green.
- 129.2. ⚠️ Fixed a TIME BOMB in the new tlint suite: its fixtures hard-coded a timestamp, which went stale within a day and made tlint's own drift check swallow nine assertions (70/79). Now derived from the clock, with the reason written in so it cannot recur.
- 129.3. Two pre-existing over-cap headers found and trimmed by their owners; header contract 94/94.

---
*`#opt`: Below are optional reading —— record only.*
---

## 130. Detail Behind the Above

- 130.1. flint's new rule blocks only comms-SHAPED names, so `AJAP Logs 202607182259.csv`, `chrome_disable_ondevice_model_202607251750.mobileconfig` and the whole `backup_gcl/` `_moved_pending` family are untouched by construction.
- 130.2. `.githooks/pre-commit` does NOT know the new rule, so a tail-defective name created via Bash or Finder still reaches history. Recorded in flint's KNOWN GAPS.
- 130.3. The rename census excluded `.venv/`, logs and state via `git ls-files`, so the counts are tracked files only.
- 130.4. Git history survives a folder rename here —— verified against this repo's OWN past renames (`personal_bg.md` keeps 19 commits under `--follow` versus 5 without). A pure move gives byte-identical blobs, so rename detection is exact-match, not similarity-scored.
- 130.5. But `git log <dir>` and GitHub's DIRECTORY history do not follow renames —— only per-file `--follow` does.
- 130.6. The OTG pinned SHAs survive a rename (each addresses an immutable commit), but `#sync` silently stops maintaining the index and exits 0. There is an unavoidable window where the phone 404s on every protocol file.
- 130.7. `GitHub/CLAUDE.md` is tracked by NO git repository and names both folders. No hook, lint, test or grep will ever catch it.
