# CCSIM CP —— CC System Improvement & Maintenance

*Meta-CP: improves CC's own pcmds, scripts, and protocols (OS/firmware-style upkeep), NOT user deliverables. Root `dupbus-ceztuc-7cufVe/CLAUDE.md` governs —— read it first if not already. A simple CP: no `CP_index_cc.md`.*

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

## 3. backlog.md —— Append-Only Log
- 3.1. `cp/ccsim/backlog.md` collects system-improvement items (from `close_`/`wrap_` scans or ad-hoc).
- 3.2. Entry: `## `[close_/wrap_ filename]` — [title]`, then `Problem:` / `Suggestion:` / `Ref: [filename] §x.x`.
- 3.3. NEVER edit/delete an entry; resolve by appending `→ ✅ RESOLVED [TS] (ref …)` beneath it.

## 4. Shrink/Edit QA —— Blind A/B Simulation
- 4.1. After shrinking or editing a pcmd, verify it still performs as well as before.
- 4.2. Dispatch 2 blind SAs (§9.03.1: each told "You're a sub-agent") on the SAME scenario —— one fed the CURRENT file, one the PRE-edit baseline via `git show <pre-edit-SHA>:<path>`.
- 4.3. Neither SA learns of the edit, the other version, or the intent —— fresh, uncontaminated eyes.
- 4.4. Compare, report; the user approves unless trivial.
- 4.5. If a baseline is too big to pass inline, stage it in `sandbox/` (§5) instead.

## 5. sandbox/ —— CC's Scratch Folder
- 5.1. `cp/ccsim/sandbox/` is the ONLY folder CC may delete from directly (Void Rule waived) —— keep it clean yourself.
- 5.2. Holds ONLY scratch: oversized baselines, non-historic A/B versions (new pcmds with no git history), experiments. When unsure whether something belongs elsewhere, default it here —— no drawback.
- 5.3. Before deleting anything here: commit + push → delete → commit + push, so a rare rescue stays recoverable from git.

## 6. #wrap —— a CCSIM Job
- 6.1. `#wrap` runs in a CCSIM session (SA fan-out over the month's `close_`).
- 6.2. Gate: if the user reports context >50% full, suggest a fresh session first; ≤50%, proceed. (Threshold tunable —— calibrate on the first real wrap.)
- 6.3. `wrap_` stays UNPREFIXED even here (it's repo-wide, not CCSIM-scoped) —— the §3.3.6 prefix exception.
