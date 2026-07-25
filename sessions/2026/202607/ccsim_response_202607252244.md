# Response to ccsim_query_202607252244.md
*413MB safely deletable; two dirs hold your memory*

## 42. ⚠️ Read This First
- 42.1. These folders are NOT only transcripts. Two of them hold your persistent auto-memory (`MEMORY.md` + entries) that loads into every future session for that project.
- 42.2. Deleting those would permanently destroy that memory —— silently, with nothing in the repo to restore it from.
- 42.3. That is the one real hazard here; everything else is just history.

## 43. Inventory (6 dirs, `~`1.47GB)
- 43.1. `…-dupbus-ceztuc-7cufVe` —— 507M, 67 sessions, active today. **HAS MEMORY** (8 files).
- 43.2. `…-AJAP-repo` —— 548M, 3,500 files, active today. **HAS MEMORY** (3 files).
- 43.3. `…-dupbus-ceztuc-7cufVe-seek` —— 400M, orphaned.
- 43.4. `…-AJAP` (bare) —— 13M, orphaned.
- 43.5. `…-dupbus…-sessions-2026-202607` —— 8K, empty of transcripts.
- 43.6. `…-GitHub` (plain) —— 1.1M, active today. Has an EMPTY `memory/`.

## 44. Safe to Delete —— `~`413MB
- 44.1. `-Volumes-FURY-2TB-Fury-Documents-GitHub-dupbus-ceztuc-7cufVe-seek` (400M) —— your hunch CONFIRMED. Verified not by guessing the name but by reading the `cwd` recorded inside its own session files: it is exactly `…/dupbus-ceztuc-7cufVe/seek`, and that path no longer exists. No memory. Biggest single win.
- 44.2. `-Volumes-FURY-2TB-Fury-Documents-GitHub-AJAP` (13M) —— the stale PRE-RENAME slug. Its sessions start with cwd `…/GitHub/AJAP` then switch to `…/AJAP_repo` mid-cluster, i.e. captured the rename itself. Superseded by the live `AJAP-repo` dir. No memory.
- 44.3. `…-dupbus-ceztuc-7cufVe-sessions-2026-202607` (8K) —— a real path, but holds zero transcripts; just a stray workflow fragment. Negligible either way.

## 45. Must NOT Delete
- 45.1. `…-dupbus-ceztuc-7cufVe` (507M) —— holds 8 memory files, incl. the no-chat-text discipline, the AJAP display_N correction, the two heartbeat rules, your chameleon-veteran positioning, and the SA-brief mandate. Losing these means re-learning them the hard way.
- 45.2. `…-AJAP-repo` (548M) —— holds 3 memory files (AJAP cockpit-mode rules: no blocking questions, no permission prompts).
- 45.3. Both are also your live, active projects. Size is real but so is the value.

## 46. re Your `GitHub/` Question —— You Are Right
- 46.1. Correct on all counts: deleting it affects ONLY that session's history. The Reader session still works, because its behaviour lives in the `CLAUDE.md` sitting in that folder, which is re-read fresh every session.
- 46.2. One nuance you could not have known: it DOES have a `memory/` dir —— but it is currently empty, so there is nothing to lose today.
- 46.3. Verdict: not worth deleting. 1.1M reclaim, used today, and the empty-memory state could change. Leave it.

## 47. What Deletion Actually Costs
- 47.1. NOT affected —— the repo, its `CLAUDE.md`, skills, hooks, or scripts. None of that lives here. Hooks are in `~/.claude/settings.json`; everything else is in the repo.
- 47.2. Lost —— session resume (`--resume` / the session picker), searchable transcript history, and SA transcripts for that project.
- 47.3. Lost if memory present —— the auto-memory, permanently.
- 47.4. Worth knowing: `cleanupPeriodDays` is NOT set, so the 30-day default auto-purge already applies to TRANSCRIPTS. Both orphans are near that window anyway —— but the purge never touches `memory/`, which is exactly why the memory-bearing dirs need your explicit protection rather than benign neglect.

## 48. To Run (yours —— I do not delete data)
```bash
cd "/Users/culous/.claude/projects"
rm -rf "-Volumes-FURY-2TB-Fury-Documents-GitHub-dupbus-ceztuc-7cufVe-seek"
rm -rf "-Volumes-FURY-2TB-Fury-Documents-GitHub-AJAP"
rm -rf "-Volumes-FURY-2TB-Fury-Documents-GitHub-dupbus-ceztuc-7cufVe-sessions-2026-202607"
du -sh * | sort -h
```
- 48.1. Sanity check before you paste: confirm neither of the first two contains a `memory/` folder —— `ls -la "<dir>/memory" 2>/dev/null` should say no such file.

## 49. Thought
- 49.1. The memory-in-projects fact is the genuinely useful discovery here —— it makes this directory look disposable when part of it is not. Worth remembering before any future `~/.claude` tidy-up.
