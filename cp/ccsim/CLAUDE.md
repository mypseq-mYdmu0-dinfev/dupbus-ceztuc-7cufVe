# CC System Improvement & Maintenance (CCSIM)

*Meta-CP: improves CC's own pcmds/scripts/etc. (OS/firmware-style upkeep), not deliverables. Read root `CLAUDE.md` if not already. New file in `ccsim/`: either note here or `README.md`.*

## 1. Every Turn —— Change Hunt
- 1.1. Read `cp/ccsim/last_seen.md` (line under the heading = `[TS] [SHA]` of the last audit).
- 1.2. `git log --oneline <SHA>..HEAD` + `git status --porcelain` —— find any file change/addition since, EXCLUDING `cp/`, `temp/`, `sessions/`.
- 1.3. Surface findings ALONGSIDE the user's query: what changed + your read of why; the user confirms or explains, then improve if warranted.
- 1.4. Then overwrite `last_seen.md` with the current TS + `HEAD` SHA (TS first).

## 2. Session Start —— Recent CCSIM Index
- 2.1. Glob `ccsim_close_*` under `sessions/`; take the 5 latest by TS.
- 2.2. Read ONLY each one's line 2 (≤8w subheading).
- 2.3. Print `ccsim_close_[TS] — [subheading]` at the FOOT of the 1st `response_`, marking any not yet #r this session.
- 2.4. Reading a prior CCSIM close IN FULL is DISCRETIONARY —— only when its subheading looks relevant.
- 2.5. WSM internal-SSD health (also every session start):
  - 2.5.1. Run `smartctl -a disk0 | grep -i "Percentage Used"` (no sudo); health% = 100 − that value.
  - 2.5.2. ALERT the user in the 1st `response_` ONLY when health ≤93% (Percentage Used ≥7%); track how long each 1% drop takes (wear-rate → WSM-replacement runway).
  - 2.5.3. Baseline 202607250332 —— 6% used = 94% (unchanged from session 05).
- 2.6. Stale-session sweep (also every session start; auto-purge is OFF —— `cleanupPeriodDays: 36500`, so nothing self-cleans):
  - 2.6.1. `ls -lt ~/.claude/projects/` —— flag any dir whose newest activity is ≥90 days old AND whose project is no longer in use.
  - 2.6.2. PROPOSE deletion with sizes; NEVER delete without approval.
  - 2.6.3. ALWAYS EXEMPT `-Volumes-FURY-2TB-Fury-Documents-GitHub` —— the Reader session, kept alive indefinitely by reverting; age is meaningless for it.
  - 2.6.4. Before proposing ANY dir, check `<dir>/memory/` —— a populated one holds persistent auto-memory that no repo can restore; exclude it from the proposal.

## 3. backlog.md —— Append-Only Log
- 3.1. Collects CC's own system-improvement items (from `close_`/`wrap_` scans or ad-hoc).
- 3.2. Entry: `## [title]`, then `- Problem:` / `- Suggestion:` / `- Ref: [filename] §x.x`.
- 3.3. NEVER edit/delete an entry; append `→ ✅ RESOLVED [current_TS] (Ref: …)` beneath it.

## 4. Change Simulation QA —— Actively Propose It
- 4.1. For ANY non-trivial change to a script/pcmd/"skill" (create, edit, shrink, delete a helper, restructure), ACTIVELY PROPOSE dispatching SA(s) to simulate its real-world effect before calling the work done —— don't wait to be asked.
- 4.2. The SA runs a realistic scenario exercising the change and reports what happened; you then improve/debug from the findings and re-simulate if needed.
- 4.3. When a BEFORE/AFTER comparison is meaningful (e.g. a shrink/edit —— "as effective as before?"), run 2 BLIND SAs (each told "You're a sub-agent") on the SAME scenario —— one fed the CURRENT version, one the baseline; neither learns of the change, the other version, or the intent (uncontaminated fresh eyes).
- 4.4. Baseline source: `git show <pre-change-SHA>:<path>` for a historic version; `sandbox/` (§5) for a too-big-to-inline baseline OR a non-historic version (e.g. a brand-new pcmd's alternative draft).
- 4.5. The user approves unless trivial.

## 5. sandbox/ —— CC's Scratch Folder
- 5.1. `cp/ccsim/sandbox/` is the ONLY folder CC may delete from directly (Void Rule waived) —— keep it clean yourself.
- 5.2. Holds ONLY scratch: oversized baselines, non-historic A/B versions (new pcmds with no git history), experiments. When unsure whether something belongs elsewhere, default it here —— no drawback.
- 5.3. Before deleting anything here: commit + push → delete → commit + push, so a rare rescue stays recoverable from git.

## 6. Backlog Sweep (do after EVERY #wrap → push first → update `wrap_`)
- ##SA scan the month's comms (funnel approach: wrap→close→response→query) for EMERGENT cross-session patterns worth a CCSIM fix that no single `close_` already logged
- Append any new ones to `backlog.md` (per §3); per-session items already self-registered by each `close_` (per `close.md`), so hunt PATTERNS, not un-logged flags
- Surface `backlog.md`'s OPEN items (those without a `→ ✅ RESOLVED` line)
  - For EACH open item, PROPOSE a concrete solution + rough effort
  - This monthly sweep is what keeps the backlog from growing unbounded
  - For large items (e.g. spanned ≥3 turns), suggest a dedicated session (context concerns)
- For each surfaced problem/pattern, create/adjust pcmd and/or "skills" to optimise CC
  - Skills are just pointers to pcmds (#SA probe current skills/pcmds first)
  - A skill cannot exist w/o its pcmd, but NOT vice versa (pcmd can be triggered by #[name])
  - If trivial (not worth a pcmd/skill), consider creating/adjusting "memories" instead
- Record the sweep in the `wrap_` § Issues: the open count + your proposals, referencing `backlog.md` (don't re-list its entries)
- The 2nd `wrap_` push (post-sweep) is an ALLOWED override of root CLAUDE.md's one-commit-per-turn.