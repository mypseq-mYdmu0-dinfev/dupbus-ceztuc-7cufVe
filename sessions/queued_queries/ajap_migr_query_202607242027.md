# For AJAP CC —— SSD-wear migration items that touch AJAP

*Context: a CCSIM (default-repo) session is relocating write-heavy paths off the WSM internal SSD (health 94%) onto the external SSD `/Volumes/FURY 2TB` (currently HFS+, `noowners`; APFS reformat planned ~Dec 2026). Two items are AJAP's to own because AJAP runs Playwright + jobspy ~48h/week. Please analyse, then act with your own judgement. Nothing below has been changed on AJAP's behalf —— it's flagged so nothing breaks silently.*

## 1. Playwright —— BOTH the cache AND the live temp artifacts should move to FURY
- 1.1. `~/Library/Caches/ms-playwright` (~539M) —— the downloaded browser BINARIES. Static (0 writes in 7d) —— migrating it is space-only, low wear benefit. Safe to symlink to FURY when no automation is running.
- 1.2. The REAL Playwright write-churn is NOT there —— it lands in the system temp dir `$TMPDIR` (`/var/folders/.../T/playwright-artifacts-*`, `playwright_webkitdev_profile-*`) on the INTERNAL SSD, every run. Over ~48h/week this is the actual wear source, and a folder-level migration does NOT touch it.
- 1.3. Ask: redirect Playwright's artifact/temp path onto FURY (e.g. set the automation's `TMPDIR`, or Playwright's `outputDir`/artifacts path, to a `/Volumes/FURY 2TB/...` location), OR consciously accept that wear. This is the higher-value of the two.
- 1.4. Migrate BOTH (per the user's instruction) once you've decided the mechanism; verify a real AJAP run still works afterwards.

## 2. jobspy (`~/.mcp`) —— still LOCAL; AJAP's call to migrate
- 2.1. `~/.mcp/jobspy` (~117M) was NOT migrated by the CCSIM session —— it was in use (the jobspy MCP server was running) and it's static `node_modules` (0 writes in 7d; the code is read on each server spawn, not rewritten), so it's a space-only move.
- 2.2. The user believes its churn is high (jobspy used for every job). Reads do wear minimally, but the node_modules themselves aren't rewritten —— jobspy's OUTPUT goes to AJAP's own dirs, not into `~/.mcp`.
- 2.3. If AJAP wants it on FURY anyway: symlink `~/.mcp` -> `/Volumes/FURY 2TB/.mcp` while jobspy is NOT running (the MCP config path in `~/.claude.json` resolves through the symlink). Then VERIFY jobspy still launches + returns results (it's critical to AJAP).

## 3. Other CCSIM migrations that could affect AJAP (FYI —— verify, don't assume)
- 3.1. `~/.claude` (whole dir: CC transcripts, settings, hooks, future skills) is now a symlink -> `/Volumes/FURY 2TB/.claude`. Any AJAP Claude Code session's transcripts now live on FURY. Launch Claude only with FURY mounted.
- 3.2. `~/.codex` is now a symlink -> FURY (guard against internal writes from the ChatGPT app). Unlikely to affect AJAP, noted for completeness.
- 3.3. Chrome profile `~/Library/Application Support/Google/Chrome/Default` + Chrome/Perplexity caches were symlinked to FURY. If AJAP drives real Chrome (not Playwright's bundled Chromium), note the profile is now on FURY.
- 3.4. Standing rule for all of the above: never launch an app that uses a migrated path while FURY is unmounted (dangling symlink -> split-brain). Recovery patterns: `cp/ccsim/ssd_migration_guide.md`.

## 4. Register `tlint` for AJAP (cross-repo TS-uniqueness enforcement)
- 4.1. The rule `AJAP_repo/inv/CLAUDE.md:31` ("no files can share identical name, even in different repos ... either must add 1min (mm+1)") is enforced by CONVENTION only on the AJAP side —— AJAP sessions run NO PostToolUse hooks (AJAP's `.claude/settings.json` has none).
- 4.2. The dupbus repo now has `cscpt/tlint_hook.py` (a timestamp linter) that checks the written file's own folder AND its cross-repo mirror (`AJAP_repo/inv/<YYYY>/<YYYYMM>` ↔ `dupbus/sessions/<YYYY>/<YYYYMM>`). But hooks load ONLY from the launch repo, so it never fires for AJAP-launched sessions.
- 4.3. To enforce AJAP-side too: register a tlint PostToolUse hook in `AJAP_repo/.claude/settings.json` (point it at `../dupbus-ceztuc-7cufVe/cscpt/tlint_hook.sh`, or copy the script in). It already computes the `inv/`↔`sessions/` mirror, so it catches cross-repo `close_[TS]` clashes both ways. Non-blocking YELLOW only.
- 4.4. Known existing cross-repo collisions to de-collide by mm+1 (per the inv/CLAUDE.md rule): `close_202607190110.md` and `close_202607231053.md` each exist in BOTH `AJAP_repo/inv/2026/202607/` and `dupbus/sessions/2026/202607/`. Coordinate with the user on which side bumps.
