# Response to ccsim_query_202607262028.md
*10-SA fleet; FURY split-brain risk found; two corrections*

## 43. Run Shape
- 43.1. Fan-out fleet: 10 SAs, 4 waves, 0 failures. 10 regression suites now green (was 3).
- 43.2. Change hunt —— `634e8d5` (your backup folder) and `a8f2341` (close.md DATS). Both read and acted on.
- 43.3. `#m1` DID fire hlint —— your alert-check passes. It resolved `#cic`, `#ww` and `#m1` on that prompt.

## 44. ⚠️ Two Corrections to What I Told You
- 44.1. My §37.3.2 was WRONG. The skill listing does NOT sit in the system prompt. It is a conversation-level system-reminder attachment, emitted once per agent and thereafter only as deltas.
- 44.2. The CONCLUSION still holds (bounded, does not accumulate) —— but I gave you the right answer via the wrong mechanism, and you would have written that into a permanent file.
- 44.3. Your `1Mn × 1% = 10k tk` inference —— directionally right, framing wrong. The enforced number is CHARACTERS, not tokens: `context × bytesPerToken × 0.01`. Opus 5 uses `bytesPerToken = 3`, so 1Mn context → **30,000 characters**.
- 44.4. The token-equivalent IS `~`10k (the factor cancels when converted back), so your arithmetic was internally sound. But the actionable number is 30,000 chars against a per-skill cap of 1,536 —— i.e. `~`19 skills fit at FULL description length, not 6 as a token-vs-char mix-up would suggest.
- 44.5. Verified from the shipped binary, not the docs. `skill_guide.md` carries the corrected framing.

## 45. §37 Answers

### 45.1. re Numbering —— Accepted
- 45.1.1. You are right; §37.9 should have been §37.09. Not fixing retroactively, per you. Applying it from here.
- 45.1.2. nlint now has a SECOND function: detects `- [n].10` in ANY file (not just `response_`) and yellow-flags with both remedies, stating your soft preference for splitting over 2-digit.
- 45.1.3. Two design calls worth your eye: `- 3.10 metres` does NOT fire (numbered.md mandates a dot after the number, so the dot is the only reliable discriminator —— nagging on every measurement would get the lint tuned out). And a level already using `- [n].01` suppresses the warning for that level, since numbered.md itself says `[N].01` implies `[N].10` is expected —— otherwise it would nag hardest at the file that already took the remedy.
- 45.1.4. The shim had to be widened (it gated on `response_`), done in pure bash on the written TEXT, so an ordinary edit still spawns no Python. Measured: 5ms gated-out vs 34ms when it runs.
- 45.1.5. Swept 8,875 real repo files: 41 hits, all genuine 10th siblings, zero false positives.

### 45.2. re 37.2 —— Renamed
- 45.2.1. `universal/profile.md` → `personal_bg.md`; `cp/career/pro_profile.md` → `career_bg.md`. Headings updated.
- 45.2.2. Your underscore question —— skills may NOT use underscores. Documented: lowercase letters, numbers and hyphens only.
- 45.2.3. So the split is deliberate: pcmd files use underscores (`personal_bg.md`), skills use hyphens (`personal-bg`). A test now pins this so a future tidy-up cannot "harmonise" them and silently break skill registration.
- 45.2.4. Scope widened beyond your list —— live references also existed in `glossary.md`, `shrink.md`, `context_otg.md`, `preferences_otg.md`, `rules_otg.md`, `CP_notes.md`, `int.md`. All updated. Disclosing because you named fewer.
- 45.2.5. Content proposals for both files are in the appendix (§55) —— proposals only, nothing acted on.

### 45.3. re 37.5 —— Renamed
- 45.3.1. `skiller.md` → `skill_guide.md`, and the `*_guide.md` convention is now stated inside it as a standing rule for future `ccsim/` guides.

### 45.4. re 37.6 —— No Action Was Implied
- 45.4.1. Clarifying: "Removable any time from the same pane" was purely informational —— how to UNDO the policy if you ever wanted to. It was never advice to remove anything.
- 45.4.2. Keeping the `.mobileconfig` for the trace, as you decided. Agreed.

### 45.5. re 37.7.7 —— Handled
- 45.5.1. Solved by the new §7 index (see 45.7): each entry states WHEN to read it, so nothing in `ccsim/` is a default read. Only `last_seen.md` is every-turn —— your CIIW was right.

### 45.6. re 37.9 + 38.4 —— The Real Finding
- 45.6.1. ⚠️ You were right that `doomsday.md` described the risk without providing resilience. Now fixed, and the investigation found something worse than expected.
- 45.6.2. Established: `~/.claude` is a SYMLINK to `/Volumes/FURY 2TB/.claude`. ALL of it lives on FURY —— `settings.json` (the only live hook registration), 11 auto-memory files (`~`44KB, never cloud-synced), and `~`1.0GB of transcripts.
- 45.6.3. PROVED (read-only, nothing unmounted): a dangling symlink is NOT silently replaced. The CLI left it untouched and exited 0. So the common failure is quiet and non-destructive —— no config, no hooks, no memory.
- 45.6.4. ⚠️ PROVED to be the dangerous variant: if the mount-point DIRECTORY survives as a real folder, a complete tree gets built on the INTERNAL disk —— a fresh `settings.json` with ZERO hooks, invisible, whilst your real config sits unmounted. That is silent split-brain.
- 45.6.5. Built `nscpt/fury_unmounted.sh` —— detects all three states, never deletes (renames aside with a timestamp), refuses to act when FURY is simply absent, and verifies hooks afterwards. 12/12 tests.
- 45.6.6. Your `setup_cc_tmpdir_...sh` suspicion —— NOT the contingency you half-remembered. It relocates `CLAUDE_CODE_TMPDIR` with a mount guard. Left untouched.
- 45.6.7. Your backup approach —— agreed, and extended: the 3 AJAP memory files are now backed up alongside `settings.json`. Bulk regenerable data (transcripts, caches, session-env) deliberately excluded.
- 45.6.8. Mirroring rule documented in `hook_guide.md`; `doomsday.md` now points at the rescue script.

### 45.7. re 37.12 —— Index Built, README Voided
- 45.7.1. `ccsim/CLAUDE.md` gained §7: every file in `ccsim/` with what it is and WHEN to read it.
- 45.7.2. `ccsim/README.md` folded in and voided as `❌_README.md` (Void Rule —— yours to delete).

## 46. §38 Answers

### 46.1. re 38.1 —— Agree
- 46.1.1. Your preamble edit is accurate and better —— "harness/environment engineering" names what this CP actually does. Kept as written.

### 46.2. re 38.5.2 —— Verified Working
- 46.2.1. Date-Added preservation PROVEN live, with a control: an in-scope file kept its Date Added (mtime still changed); an out-of-scope file on the same volume had Date Added reset to now.
- 46.2.2. That control matters —— it proves the hook is load-bearing, not a no-op. Without it every edit under `sessions/` would jump to the top of your Date-Added sort.

### 46.3. re 38.6 —— Reader Session: Built
- 46.3.1. Possible, and done. clint now has two modes: `repo` (declarations-only, sub-paths match) and `reader` (blank lines ONLY —— no glyphs, no dividers, no exemptions), keyed on an EXACT cwd match with the `GitHub/` parent.
- 46.3.2. The evidence made the case: auditing the Reader session's 8 transcripts found 46 non-blank chat lines, of which 17 were declaration glyphs the repo rule would wave through. So a third of its breaches were invisible —— not redundant at all.

### 46.4. re 38.6.3 —— hlint Retargeted
- 46.4.1. Now searches ONLY: `universal/`, `cp/`, `AJAP_repo/protocols/` (recursive), and `AJAP_repo/inv/inveng.md` (that one file). `sessions/` excluded.
- 46.4.2. Verified `#eng` now resolves to `AJAP_repo/protocols/eng.md` —— the exact miss that cost you 100⁺ hours.

### 46.5. re 38.8.1 —— clint Strengthened
- 46.5.1. RED always, unlimited. YELLOW tier and the once-per-turn ledger removed, as you decided.
- 46.5.2. Exemptions implemented: ` yn` (with the leading space) in the user message, and a chat line starting `DATS` when it is one line and ≤10 words. Both logged with distinct tags so they stay auditable.
- 46.5.3. Read your `a8f2341` close.md change to match the exact DATS form.
- 46.5.4. Loop safety re-reasoned: `stop_hook_active` remains the backstop, so an unlimited RED still cannot spiral.

## 47. §39.2 —— Markers + Trim
- 47.1. Your concern was real and measurable: extracting the unterminated block on `tlint.py` pulled 202 of 207 lines —— essentially the whole script, silently.
- 47.2. Every script now has explicit start AND end markers, and `cscpt/README.md` publishes a concrete extraction recipe (deliberately ASCII-only, so the em dash is never load-bearing).
- 47.3. ≤100w cap applied —— worst was 336w. Your instinct about harness-run plumbing was right: registration paths and stdin field names were the bulk, and no agent can act on them.
- 47.4. Nothing deleted —— cut content moved to the CCSIM section.

## 48. §40 —— Encoded
- 48.1. Added to `ccsim/CLAUDE.md` as a governing section: CCSIM is harness engineering; its client is every other agent; documentation is an interface with a token budget; the lints run themselves so others need only know what to do when one fires; and the ownership/escalation rule (even a one-character fix gets reported).

## 49. Alerts —— Nothing Critical Missed, But Three Things
- 49.1. ⚠️ `nscpt/network_diagnostics.sh` FAILS `bash -n`. Pre-existing (committed 2 July, untouched by this run) —— it is prose notes saved with a `.sh` extension, so it would break if ever run. Flagging, not fixing: it is your file and the fix is a decision (rename to `.md`, or make it a real script).
- 49.2. `index_otg.md` / `CP_index_otg.md` hold 3 permalinks with the OLD pcmd paths. NOT broken —— each is pinned to an immutable SHA where the old path was live —— but your next `#sync` must re-pin them.
- 49.3. Two SAs reported a concurrency brush (one edited a file another owned). No content was lost —— caught because both reported it —— but my ownership split was imperfect and I am recording it.

## 50. Thoughts
- 50.1. The FURY split-brain case (45.6.4) is the most valuable thing this turn produced, and neither of us was looking for it —— your question about unmounting was, in hindsight, the right instinct twice over.
- 50.2. I am struck that the two errors I had to correct today (44.1, 44.3) were both cases of me being RIGHT in conclusion whilst wrong in mechanism. That is the harder kind to catch, because nothing looks broken.
- 50.3. Commit discipline: renames are staged separately from edits, so this lands as a move-only commit plus a content commit —— history preserved on all 5 renames.

---
*`#opt`: Below is optional reading.*
---

## 51. Fleet Detail
- 51.1. Waves: Lints (5 SAs) → Renames (2) → Resilience (2) → Index (1).
- 51.2. Suites now green: nlint 19/19, clint 33/33, plint 7/7, scope-guard 23/23, cscpt-header 54/54, fury 12/12, plus 4 structural PASS suites (index, pcmd-rename, skill-guide, skill-desc).
- 51.3. `~`1.35Mn SA-tokens kept off my window.

## 52. Skill-Listing Figures (verified)
- 52.1. Formula: `budget_chars = contextWindow × bytesPerToken × 0.01`.
- 52.2. `bytesPerToken` = 3 for Opus 4.7/4.8 and the 5-series; 4 for older models.
- 52.3. 1Mn context, Opus 5 → 30,000 chars. Per-skill cap 1,536 chars → `~`19 skills at full length before truncation begins.
- 52.4. Over budget it SHORTENS silently rather than asking —— so description length is a shared finite resource, and brevity is a courtesy to every other skill.

## 53. nlint New-Check Gaps (accepted, disclosed)
- 53.1. The bash gate reads the written TEXT, so the advisory fires when `.10` is INTRODUCED, not on every later edit of a file that already holds it. That is both the performance win and a useful anti-nag property.
- 53.2. An edit adding only `- 3.11.` to a file already holding `- 3.10.` will not re-warn —— the reminder was already delivered.
- 53.3. An item written without its mandatory dot (`- 3.10 foo`) goes unflagged; it already breaches a different numbered.md rule.

## 54. FURY Rescue —— One Unproven Inference
- 54.1. The script detects, but does NOT rely on, the inference that macOS remounts a returning FURY as `/Volumes/FURY 2TB 1` when a leftover directory occupies the real name.
- 54.2. Unprovable without actually unmounting, which was out of bounds. The script scans for a numbered sibling mount and REPORTS rather than acting.

## 55. Content Proposals —— `personal_bg.md` / `career_bg.md`
- 55.1. Proposals only; nothing was changed in either file's content.
- 55.2. Core diagnosis: the old `profile` skill never fired because the FILE is organised around abstract categories rather than the concrete situations where it would help —— the same anti-pattern that made its description unmatchable.
- 55.3. Suggested direction: lead each with a short "use me when" situation list mirroring the new skill description, so the file and its trigger reinforce each other.
- 55.4. Awaiting your approval before any content edit.

## 56. Post-Turn Addendum —— §49.2 Closed, and a Real Bug Found
- 56.1. I ran `#sync` to re-pin the OTG permalinks after the pcmd renames (the loose end I flagged in §49.2). It went wrong, and I caught it immediately.
- 56.2. ⚠️ THE BUG (pre-existing in `.sync/sync.py`, not introduced by the renames): `sha_of()` pins a path to the last commit that TOUCHED it. For a renamed-away path that is the rename commit itself —— where the file no longer exists. So the re-pin silently produced 3 URLs that 404.
- 56.3. Why it matters beyond today: it would recur on EVERY future pcmd rename, and it fails silently —— the index looks correct, and only an OTG fetch would reveal it.
- 56.4. Fixed twice over: the 3 index entries now point at the new paths, and `sha_of()` now checks the working tree FIRST, aborting loudly on a stale entry instead of re-pinning a corpse. Rationale baked into the function.
- 56.5. Verified: all 50 permalinks across the three index files resolve at their pinned SHA (was 3 broken). Guard unit-tested —— an existing path returns a SHA, a renamed-away path aborts.
- 56.6. Meta: this is the third time this session that running the real mechanism —— rather than reasoning about it —— exposed something reasoning had missed. Worth remembering as the pattern, not the incident.
