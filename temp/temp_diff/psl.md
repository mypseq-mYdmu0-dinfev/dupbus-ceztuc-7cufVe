# PSL (Process Single Loop) —— NEW-AJAP Edition

*Proposed replacement for `psl.md` (the verbatim old copy beside this file). After user review: copy-paste this content into `psl.md`, delete this file.*

*Read prompt-matching section; e.g. on `#psl`, read § `#psl`.*

## What Changed vs the Old System

- The CC no longer processes cards herself —— she drives the PROGRAMME's single-job mode: `./.venv/bin/python -m AJAP_code.main --psl "<job_url>"`.
- The programme does everything up to S5-equivalent (score, band, research per band, CL, deterministic lint, LLM audit w/ playbook) and writes a `PSL_` AR —— it NEVER submits in this mode unless `--apply` is added.
- Old `#auto` / `#para` / `#unpara` dissolve: there is no manual loop to auto-advance, and run state lives in the LEDGER (the programme never re-reads `gcl/` filenames mid-run), so PSL file moves can never collide w/ a running AJAP —— `--psl-done` below also updates the ledger atomically (WAL-safe at any time), which closes the last gap of the old parallel-session era.

## Shared Rules

- 🔴 The LEDGER is the single source of truth: NEVER hand-move an AR ACROSS status folders (`pending/` ↔ `applied/` ↔ `skipped/`) —— a hand-move leaves the ledger row stale (dirty analytics + sabotage of a running AJAP); ALWAYS use the commands below, which move the file AND update the ledger in one atomic step. (mirror.py self-heals stale rows at the next programme start —— a safety net, not a licence.) Archiving WITHIN a status (e.g. `applied/` → `applied/applied_archive/`) is always safe: the ledger row is path-agnostic.
- AR lands in `gcl/pending/` (Outcome: Pending) w/ prefix `PSL_` (clickable), written by the programme —— NOT `applied/`, so ajap_logs counts stay clean; declare `➡️` as usual
- The CC reads the AR back to the user (concise) and awaits his verdict
- For any questions/blockers: summon user via the interactive-question tool
- `#apply` = re-run w/ `--apply` appended: the programme performs the real submission (quick-apply flow or agentic portal driver), then confirms —— the AR is promoted to `applied/` by the programme itself
- `#done` = user submitted manually himself —— run: `cd AJAP_repo && ./.venv/bin/python -m AJAP_code.main --psl-done "<job_url_or_AR_filename>"` (promotes the `PSL_` pending AR → `applied/`, Outcome→Applied, prefix stripped, TS restamped to promotion time, ledger outcome `PslApplied` —— invisible to ajap_logs by design; safe whether or not AJAP is running)
- `#skip` = user deems the job no longer worth applying —— run: `cd AJAP_repo && ./.venv/bin/python -m AJAP_code.main --user-skip "<job_url_or_AR_filename>"` (moves the pending AR → `skipped/`, Outcome→Skipped (user), prefixes stripped, ledger outcome `UserSkipped` —— invisible to ajap_logs; original TS kept, a skip is not an application event)
- `#next` = leave current AR untouched; await the next URL/AR from the user

## `#psl`

- User supplies a job URL (or has it open); run: `cd AJAP_repo && ./.venv/bin/python -m AJAP_code.main --psl "<job_url>"`
- The programme scrapes the job, scores it, researches per band, writes the CL, runs both gates, and STOPS before submission
- ONLY skip if score < 35 after the programme's evaluation (its routing says so); otherwise present the AR whatever the band
- DON'T proceed anywhere else; single loop means exactly one job

## `#psl [AR_filename(s)]`

- For each AR (sequentially): extract its SEEK URL (bash grep, avoid full read) → run `--psl "<url>"` → programme re-validates and writes a fresh `PSL_` AR; never edit the original AR
- If 404/closed/expired: void the original per Void Rule, tell the user, move on

## `#psl pending`

- Perform `#psl [AR_filename(s)]` over `gcl/pending/` ARs, oldest first
- Batch-verify URLs first via SA(s) (no full AR reads); void unavailable ones (no Apply button); tell counts voided/remaining, then proceed oldest-first

## `#ccl`

- Read `seek/context/ccl.md` (consulting-CL doctrine) —— pass its rules to the run by exporting `AJAP_CCL=1` before `--psl` (the worker prompt then loads ccl.md as doctrine)
- AR goes to `AJAP_repo/ccl/` (NOT `seek/ccl/` —— that tree is read-only until cutover; the two merge at P6.4)
- Reference past ARs in `seek/ccl/` (+ `ccl_archive/`) for quality & style
