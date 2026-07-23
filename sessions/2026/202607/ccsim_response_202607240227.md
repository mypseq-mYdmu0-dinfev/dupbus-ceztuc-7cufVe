# Response to ccsim_query_202607240227.md
*Hook fixed; i2 read + risk-assessed HIGH → advising, not executing*

## 1. Pre-commit hook —— fixed (block → warn)
- 1.1. what —— the pairing lint `exit 1`-blocked a valid orphan `response_` (a ≤30w chat msg quoted inline per root §3.6.1 has no `query_` sibling); it should have reminded, not blocked
- 1.2. if-unfixed —— every such legitimate commit is refused until a placeholder `query_` is manufactured (exactly what bit me last turn)
- 1.3. pre-fix-question —— none (you directed both the fix and its intended yellow-flag semantics)
- 1.4. risk-if-pushed —— demoting the block to a warning removes the hard guarantee that every `response_` has a traceable `query_`; mitigated —— the reminder still surfaces the orphan, and it only fires on `response_`, never on an intentionally response-less `query_`
- 1.5. outcome —— FIXED; verified end-to-end on 3 cases:
  - 1.5.1. orphan `response_` → prints "remember to push the query" reminder, `exit 0` (commit proceeds)
  - 1.5.2. paired `query_`+`response_` → silent, `exit 0`
  - 1.5.3. `#sync` SYNC_ACTIVE marker present → still hard-blocks a non-allowlisted file (`exit 1`) —— that guard is untouched
- 1.6. Rationale baked into the hook comment inline (no comms-file citation, per `coding.md`); backlog entry for this defect marked ✅ RESOLVED

## 2. i2 —— what the file actually is (a correction)
- 2.1. Moved `ccsim_query_202607060438.md` from `queued_queries/` → `sessions/2026/202607/` (plain move; it was untracked, well-named already, so no rename/tombstone —— kept its 6-Jul TS for provenance)
- 2.2. It is NOT "temp-file migration" and has NOTHING to do with the skills files
- 2.3. It is a **home-folder migration to cut internal-SSD wear**: relocate frequently-written hidden dirs from the internal SSD (health 94%) to the external FURY 2TB SSD, via symlink or env var
- 2.4. Correction to the record —— last close_/wrap treated i2 as "believed to hold the skills files" and made it GATE i3–i5 (skills). That belief is now disproven: **i2 does not gate the skills work at all**; the two are unrelated. The skills files' whereabouts remain unconfirmed (a separate thread)
- 2.5. Provenance caveat (from the file's own header): it was drafted by an AJAP `#inv` session from a Fable-generated audit, and explicitly says the receiving CC "MUST re-verify every claim/size/verdict" —— which I did (§3)

## 3. Live re-verification (read-only; I mutated nothing)
- 3.1. FURY 2TB filesystem —— confirmed **Journaled HFS+, `noowners`, Owners: Disabled**. So the file's core caveat holds: POSIX perms aren't enforced there; no key material; live SQLite is genuinely corruption-prone on surprise unmount
- 3.2. Current sizes (drifted materially from the 6-Jul audit —— re-verification mattered):
  - 3.2.1. `~/.claude` = 1.4G (was 1.7G), essentially all `projects/` (1.4G), HIGH write frequency
  - 3.2.2. `~/.npm` = 282M (was 67M) —— grew 4×
  - 3.2.3. `~/.vscode` = 1.2G (was 879M)
  - 3.2.4. `~/.codex` = 87M (live SQLite WAL)
  - 3.2.5. `~/.config` = 239M (was 354M), all Raycast
- 3.3. `~/.ajap` —— confirmed already a symlink → `/Volumes/FURY 2TB/.ajap` (the one "already done" item; do not touch)
- 3.4. No env mechanisms set yet —— `CLAUDE_CONFIG_DIR` unset, `CODEX_HOME` unset, `npm cache` still `~/.npm`; `~/.claude.json` correctly still in HOME

## 4. Risk verdict —— HIGH overall → discuss & advise
- 4.1. Per your branch (high → discuss; medium → self-judge + #sprint; low → Opus SA completes), I judge the task-as-a-whole **HIGH** and am therefore NOT executing any migration and NOT dispatching the completion SA
- 4.2. Drivers of the HIGH rating:
  - 4.2.1. The biggest wear-win, `~/.claude/projects` (1.4G), is **this session's own live home** —— it can't be safely moved from inside a running CC session (the file itself mandates closing ALL CC sessions + `lsof` first); a live move risks split-brain / transcript loss
  - 4.2.2. An underlying **volume-reformat question** (HFS+ → APFS, §1.3 of the file) gates any live-app-state move —— reformatting FURY is a full 2TB wipe, a pure user decision, backup-first
  - 4.2.3. Login-before-mount race (Raycast, Codex) → dangling symlink → **data reset**, a not-cleanly-reversible failure mode
  - 4.2.4. Everything here is **untracked system state** (off-GH) —— `sprint.md`'s untracked caveat says never cross an irreversible threshold unilaterally
- 4.3. Your "cleanly revertible" bar is met by only a SUBSET, not the whole —— so the whole cannot go the low-risk SA route

## 5. Per-item advice (current-state verdicts)
- 5.1. 🟢 SAFE / cleanly reversible (I can do these next turn on your go-ahead, one at a time):
  - 5.1.1. `~/.npm` (282M) —— `npm config set cache '/Volumes/FURY 2TB/npm-cache'`; env/config only, worst case npm re-downloads; no symlink, no launch-race. Best effort-to-safety ratio
  - 5.1.2. `~/.vscode` (1.2G) —— symlink after quitting VS Code; SAFE but it's a space win with near-zero wear benefit (low write freq); optional, low priority
- 5.2. 🔴 HIGH / defer —— needs a dedicated, scripted, out-of-session operation + your decisions:
  - 5.2.1. `~/.claude/projects` (1.4G) —— the real wear prize; do it via `CLAUDE_CONFIG_DIR` (survives the mount race better than a symlink), but ONLY with all CC sessions closed, the volume guaranteed mounted at launch, and acceptance of the fresh-empty-config failure mode. Cannot originate from this session
  - 5.2.2. `~/.codex` (87M, SQLite) —— only if FURY becomes APFS + treated permanent; else corruption risk
  - 5.2.3. `~/.config/raycast` (239M) —— login item starting pre-mount → data-reset risk; migrate only with a mount-guard, if at all
- 5.3. ⛔ NEVER / SKIP (agree with the file): `~/.ssh`, `~/.android` (keys; `noowners` can't hold 0600), `~/.anydesk` (identity), `~/.Trash`, `~/.zsh_sessions`, the dormant 4KB dirs; keep `~/.config/git` local
- 5.4. Addendum §5 (harness scratch `/private/tmp/claude-501/...` on the internal SSD) —— real but separate: relocation needs a LaunchAgent recreating a symlink each boot (`/tmp` is wiped) + mount-before-launch; smaller benefit than the persistent stores. Recommend treating as its own low-priority item; meanwhile the exposure is just documented here

## 6. Recommended path (if you want to progress this)
- 6.1. First settle two strategic decisions (they gate almost everything downstream) —— see QBs
- 6.2. Then, incremental cleanly-reversible wins only, one at a time, each verified before the next: start with `~/.npm` (§5.1.1)
- 6.3. Schedule the `~/.claude/projects` move as a deliberate, pre-scripted operation run from OUTSIDE any live CC session (e.g. a terminal script), never ad hoc from within a session
- 6.4. Hold Codex/Raycast until the APFS decision; keep all key/identity material local permanently

## 7. QBs (decisions I need before any execution)
- 7.1. B1 —— Is FURY 2TB to be treated as a **permanent, always-mounted** drive? (It already hosts this whole repo, so effectively yes —— but live migrations hinge on it, so I want your explicit call)
- 7.2. B2 —— Do you want to **reformat FURY to APFS (owners enabled)**? Full 2TB wipe, backup-first; it's the precondition for safely moving any live app state (`~/.claude/projects`, Codex). If "no", live-state moves stay off the table and only caches (npm) are worth doing
- 7.3. B3 —— May I proceed with the genuinely-safe subset (start `~/.npm`, optionally `~/.vscode`) next turn, one at a time? These don't need B2
- 7.4. B4 —— Priorities aside, do you want the `~/.claude/projects` migration planned now (a written, ready-to-run script for you to execute outside a session), or parked until B1/B2 are settled?

## 8. My thoughts (nothing withheld)
- 8.1. The single most valuable move (wear-wise) is also the single hardest one —— `~/.claude/projects` is 1.4G of high-churn transcripts, but it's CC's own beating heart; rushing it is how you lose session history. Worth doing, but only carefully and from outside a session
- 8.2. The `noowners` HFS+ reality (now confirmed live) is the crux: until FURY is APFS-with-owners, I would migrate ONLY caches (npm) and static extension dirs, never live databases or anything permission-sensitive
- 8.3. Honestly, the effort/benefit is lopsided —— `~/.npm` is the clean win; `~/.claude/projects` is the big win but high-effort; the rest is mostly fragility for small gains. I'd do npm now, plan `.claude/projects` properly, and skip Raycast/Codex
- 8.4. Your read-it-yourself-first instruction paid off —— it caught the wrong "i2 gates skills" assumption that had been propagating through the last two closes. The skills track (i3–i5) is now unblocked and can proceed independently whenever you want
- 8.5. Process note —— I did NOT dispatch the Opus SA because your branch ties the SA to the low-risk "complete it" path; a HIGH verdict routes to "discuss & advise", which I did directly (MA on Opus, with live recon). If you'd rather I spin up an Opus SA purely to produce a deeper, read-only migration PLAN (no execution), say so and I will
