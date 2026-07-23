# CCSIM Backlog

*Append-only system-improvement log. Entry format + rules: see `cp/ccsim/CLAUDE.md` §3. NEVER edit/delete an entry —— resolve by appending `→ ✅ RESOLVED [TS] (ref …)` beneath it.*

---

## `close_202606262244.md` — SUMMON-on-failed-#sprint rule never written
Problem: This session flagged that `sprint.md` needed a "SUMMON the user on a failed/unfinished `#sprint`" rule (so failure is never silent, after a prior silent-sprint-failure disappointment), but the edit that turn was scoped to `cic.md`/`cic_bot.md` only, and the rule was never added to `sprint.md`. It predates the backlog-wiring mechanism (built 23 Jul), so it sat unlogged until this sweep caught it.
Suggestion: Add a short clause to `universal/sprint.md` (Sprint Report or Push-Through Mechanism section): if a `#sprint` ends with an unresolved blocker and no path forward, write the report then SUMMON the user via push notification, mirroring the existing Critical/Untracked-Task Caveat language.
Ref: `wrap_202607232332.md` §3.9

## `wrap_202607232332.md` — Recurring stray-space-before-TS filename defect
Problem: At least 4 comms filenames across 2 months carry an accidental space between the prefix and the TS digits (`close_ 202605310448.md` [since renamed by the user], `close_ 202606142239.md`, `career_close_ 202606162244.md`, `dissertation_close_ 202607151919.md`). Each instance was noticed ad hoc and left for a manual rename; none was ever root-caused as a recurring pattern.
Suggestion: Add a lightweight filename-format check to the existing pre-commit pairing-lint hook (`.githooks/pre-commit`) — a regex per root CLAUDE.md §3.3.8's naming convention — flagging (not necessarily blocking) any comms filename with an embedded space before the TS digits.
Ref: `wrap_202607232332.md` §3.14

## `wrap_202607232332.md` — No documented method for editing Automator .app bundles
Problem: CC has now edited/rebuilt 3⁺ separate Automator `.app` bundles (`SortSS.app` via `#replace` instructions, `PDF Conversion.app` via the Option C rebuild + adhoc re-sign, `Continue.app`/`SimpleContinue.app`/`CCC.app` rework) — each time apparently re-deriving the extract-`document.wflow`/edit/re-sign technique from scratch rather than following a written method.
Suggestion: Once the current `CCC.app` work settles, distil the proven technique (locate `document.wflow` inside `Contents/`, edit, `codesign --force --deep -s -` to re-sign adhoc) into a short reference file (e.g. a new `automator/README.md`), so future `.app` edits don't re-derive it.
Ref: `wrap_202607232332.md` §1.2 / §5.1

## `wrap_202607232332.md` — `queued_queries/` has no forcing function to get picked up
Problem: 3 items currently sit in `sessions/queued_queries/` (`ccsim_query_202607060438.md` since 6 Jul, `citi_query_202607162351.md` and `ajap_query_202607162356.md` since 16 Jul) awaiting the user to manually send each to a dedicated new session; nothing currently surfaces their age or count except an ad hoc check like this sweep's.
Suggestion: Have `universal/wrap.md`'s template (or the CCSIM §2 Session-Start check) glob + list `sessions/queued_queries/` open items (excluding `README.md`/`.DS_Store`) with their queued-since date, so ageing items surface automatically at every `#wrap` rather than needing a manual find.
Ref: `wrap_202607232332.md` §3.1 / §3.4 / §3.5
