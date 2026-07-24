# For AJAP CC —— build AJAP's own Doomsday/Resilience playbook + two hook items

*Context: a CCSIM (default-repo) session hardened the WSM against hardware failure and built a doomsday playbook (`cp/ccsim/doomsday.md`). Much of AJAP's setup is ALSO highly WSM-local (won't work by just cloning `AJAP_repo/` to another Mac —— e.g. credentials). Please build the AJAP equivalent + action the two hook items. Analyse first; nothing here has been changed on AJAP's behalf.*

## 1. Build `AJAP_repo/inv/ajap_doomsday.md` (or wherever AJAP keeps meta-docs)
- 1.1. Mirror the structure of dupbus's `cp/ccsim/doomsday.md` but for AJAP. Cover the same 5 scenarios: (A) FURY unmount mishap; (B) FURY lost; (C) FURY replaced; (D) WSM replaced; (E) both lost.
- 1.2. Enumerate what is PORTABLE vs WSM-LOCAL for AJAP specifically. Known WSM-local, NOT-in-git items to list (verify + extend): `~/.ajap` (Chrome profile + `.env`, now symlinked to FURY); `seek/.claude/ajap_login.local.md` + any credential/`.env` stores (git-ignored by design —— these are the #1 doomsday gap, must be backed up off-WSM); jobspy `~/.mcp` (local); Playwright browser cache + its `$TMPDIR` artifacts; macOS Automation/keystroke permissions the cockpit relies on; any LaunchAgents AJAP installed.
- 1.3. State plainly: cloning `AJAP_repo/` to a new Mac will NOT work without re-supplying credentials + re-granting permissions + re-creating symlinks/agents. That's the whole point of the doc.
- 1.4. Prevention checklist: push often; keep an OFF-WSM backup of the credential/`.env` store; independent FURY backup.

## 2. Playwright wear (carried from the earlier AJAP migration note)
- 2.1. `~/Library/Caches/ms-playwright` (~539M) is static browser binaries —— migrating it to FURY is space-only.
- 2.2. The REAL 48h/week write-churn is in `$TMPDIR` (`/var/folders/.../playwright-artifacts-*`) on the INTERNAL SSD. To cut it, redirect Playwright's artifact/temp path (or the automation's `TMPDIR`) onto FURY, or consciously accept it. This is the higher-value item.

## 3. Register `tlint` for AJAP (cross-repo TS-uniqueness enforcement)
- 3.1. The rule `AJAP_repo/inv/CLAUDE.md:31` ("no files can share identical name, even in different repos ... either must add 1min") is currently enforced by CONVENTION only on the AJAP side —— AJAP sessions run NO PostToolUse hooks (AJAP's `.claude/settings.json` has none), so nothing checks it when AJAP writes a comms file.
- 3.2. The dupbus repo now has `cscpt/tlint_hook.py` (a timestamp linter) that, from the DUPBUS side, checks the written file's own folder AND its cross-repo mirror (`AJAP_repo/inv/<YYYY>/<YYYYMM>`). But hooks don't load from added working dirs (confirmed), so it never fires for AJAP-launched sessions.
- 3.3. To enforce the mandate on the AJAP side too: register a tlint-equivalent PostToolUse hook in `AJAP_repo/.claude/settings.json` (point it at `../dupbus-ceztuc-7cufVe/cscpt/tlint_hook.sh`, or copy the script into AJAP). It already computes the `inv/`↔`sessions/` mirror, so it will catch the cross-repo `close_[TS]` clashes both ways. Non-blocking YELLOW only.
- 3.4. Known existing cross-repo collisions to de-collide by mm+1 (per your rule): `close_202607190110.md` and `close_202607231053.md` each exist in BOTH `AJAP_repo/inv/2026/202607/` and `dupbus/sessions/2026/202607/`. Coordinate with the user on which side bumps.
