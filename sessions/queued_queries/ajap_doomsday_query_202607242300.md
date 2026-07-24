# For AJAP CC —— build AJAP's Doomsday/Resilience playbook

*Context: a CCSIM session built `dupbus-ceztuc-7cufVe/cp/ccsim/doomsday.md` —— a hardware-failure recovery map. Much of AJAP's setup is ALSO highly WSM-local (won't survive a bare `AJAP_repo/` clone —— credentials, `~/.ajap`, permissions). Build the AJAP equivalent. This note is DOOMSDAY-ONLY; migration items (Playwright, `.mcp`, and registering the `tlint` hook for AJAP) live in the sibling `ajap_migr_query_202607242027.md`, not here.*

## 1. Build `AJAP_repo/inv/ajap_doomsday.md` (or wherever AJAP keeps meta-docs)
- 1.1. Mirror the structure of `dupbus/cp/ccsim/doomsday.md` for AJAP —— the same 5 scenarios: (A) FURY-unmount mishap, (B) FURY lost, (C) FURY replaced, (D) WSM replaced, (E) both lost. Read that file as the template (avoids re-deriving it).
- 1.2. Enumerate what is PORTABLE vs WSM-LOCAL for AJAP. Known WSM-local, NOT-in-git items (verify + extend): `~/.ajap` (Chrome profile + `.env`, now symlinked to FURY); `seek/.claude/ajap_login.local.md` + any credential/`.env` store (git-ignored by design —— the #1 doomsday gap; MUST be backed up off-WSM); jobspy `~/.mcp`; the Playwright cache + its `$TMPDIR` artifacts; the macOS Automation/keystroke permissions the cockpit relies on; any LaunchAgents AJAP installed.
- 1.3. State plainly: cloning `AJAP_repo/` to a new Mac will NOT work without re-supplying credentials, re-granting permissions, and re-creating the symlinks/agents. That is the whole point of the doc.
- 1.4. Prevention checklist: push often; keep an OFF-WSM backup of the credential/`.env` store; keep an independent FURY backup.
