# seek/

This directory is solely for AJAP (Agentic Job Application Programme): an autonomous SEEK job-application agent. It drives Chrome (via CIC) to screen job cards, score them, draft tailored cover letters (CLs), submit applications, and log every job as an Accountability Record (AR). AJAP mode is entered ONLY when a session is explicitly prompted `#seek`/`#psl`/`#ccl`.

**If you are NOT running AJAP**: this file is all you need to understand `seek/`. Don't read `seek/CLAUDE.md` or `context/` files, UNLESS necessary (request approval first) or explicitly instructed (e.g. by `career/CP_index_cc.md`). They are AJAP operating instructions; reading them can pull a general session into AJAP mode or trigger a chain of unnecessary reads. Treat everything under `seek/` as read-only reference.

## Contents

- `gcl/` —— general ARs: `applied/`, `pending/`, `skipped/` (+ archives)
- `ccl/` —— consulting ARs (+ archive)
- `interviews/` —— enriched ARs for interview-stage jobs (read its README.md if accessing)
- `investigation/` —— investigation-mode workspace
- Other —— AJAP-only files