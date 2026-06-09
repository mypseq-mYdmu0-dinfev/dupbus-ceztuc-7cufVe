# Response to dissertation_query_202606092006.md
*Housekeeping —— thoughts only, nothing moved*

---

36. Numbering note (edge case for your rule)
- 36.1. This query is a fresh "Housekeeping" issue, yet the word `response_` appears in your line 3 note. By the literal rule (reset only if `response_` AND a prior pt no. are BOTH absent), the presence of `response_` blocks a reset, so I have continued from pt 36. If you would rather an incidental filename mention NOT count as "replying a response", the rule needs a carve-out (e.g. "a bare filename reference in a note does not count"). Flagging so you can refine; I followed the letter as written.

---

37. Directory Cleanup

- 37.1. Filename mapping (confirm before I move —— your aliases → actual files):
  - 37.1.1. "A1 (temp).md" → `MGTK751_A1_formative.md` (16 KB)
  - 37.1.2. "A1 (overview).md" → `MGTK751_A1_overview.md` (4.7 KB)
  - 37.1.3. "A1 (temp) feedback.md" → `MGTK751_A1_formative_feedback.md` (2 KB)
  - 37.1.4. "A1 (temp) email.md" → `MGTK751_A1_temp_email.md` (2.9 KB)
- 37.2. ⚠️ Folder name collision: an `Archive/` folder already exists (capital A; holds `MGTK751_A1_DevPlan.md` and `WCIC_Research/`). This volume is almost certainly case-insensitive, so your proposed `archive/` would resolve to the SAME folder. Recommend we simply use the existing `Archive/` rather than create a near-duplicate. Consolidates everything in one place.
- 37.3. Additional archival candidates I would add:
  - 37.3.1. `MGTK751 Official Files _ full _ inc A1-3.md` (121 KB) —— biggest single win. Superseded by `MGTK751_Official_Files_full.md` (86 KB) + `MGTK751_A1-3.md` (21 KB); not in the index; old combined dump. Strong archive (or void) candidate.
  - 37.3.2. `MGTK751_A1_Template.md` (3.7 KB) —— A1 submitted; template no longer needed; not in index.
- 37.4. Keep (do NOT archive): `MGTK751_A1.md` (submitted v09 —— A1R derives from it, A3 reuse), `MGTK751_A1-3.md` (live A1–A3 briefs/criteria, needed for A3), `MGTK751_A1R.md` (active).
- 37.5. Borderline: `MGTK751_A1_grade.md` (1.5 KB) —— historical but small, and it IS in the index. Keep for record, or archive and update its index path. Your call; low impact either way.
- 37.6. After cleanup (directory):
  - 37.6.1. Apply Move Rule (§8.1) on each: copy to `Archive/` → void original with `❌_` prefix + `_moved_dissertation` suffix (you then delete the `❌_` originals). Bulk move means several `❌_` stubs to clear.
  - 37.6.2. Index impact is minimal —— only `A1_grade.md` is indexed (and only if you choose to move it). Recommend adding a short "Archived" note to `CP_index_cc.md` recording what now lives in `Archive/`, so future instances do not hunt for them.

---

38. DevPlan Cleanup

- 38.1. Strongly agree with the goal —— DevPlan is an unconditional every-session read (`CP_index_cc.md` §1.2), so trimming PART C directly cuts per-session token load. PART C ≈ 44 KB of the 56 KB is the right target.
- 38.2. `A1_DevPlan` already exists at `Archive/MGTK751_A1_DevPlan.md` (36 KB) —— so "add A1_DevPlan to index" just means indexing that existing file. Nothing to create.
- 38.3. AD01–AD07 externalisation: agree these are pre-A1R history and safe to externalise; AD08–AD10 (A1R-relevant) stay full inline, consistent with this CP's "focus AD08 onwards" steer.
- 38.4. One lean refinement to consider: instead of 7 separate `MGTK751_Addendum_AD0X.md` files, a SINGLE combined `MGTK751_Addenda_AD01-07.md` in `addenda/` is less folder clutter for content that is rarely reopened, and simpler to index (one entry, no `[no.]` placeholder). Trade-off: individual files give finer retrieval per CLAUDE.md §4.2 funnel. My lean is the single combined file for these historical seven; happy to do per-AD if you prefer granularity. (`addenda/` has no case collision —— safe to create.)
- 38.5. Truncation + remark: agree —— each externalised AD reduced to its heading line plus an optional ≤20w summary, with a one-line remark after the PART C header pointing readers to the standalone file(s) when a stub is insufficient.
- 38.6. Sequencing (history safety): extract full AD01–07 text into the archive file(s) FIRST, then truncate in DevPlan —— never truncate before the copy exists.
- 38.7. After cleanup (DevPlan):
  - 38.7.1. Update `CP_index_cc.md`: add `Archive/MGTK751_A1_DevPlan.md` and the `addenda/` location.
  - 38.7.2. Verify DevPlan line 17 ("archived as A1_DevPlan.md") resolves to the indexed `Archive/` path.
  - 38.7.3. When P12 eventually runs, update P12.3 (and AD09.4.1) —— AD01–07 will already be externalised, so P12.3 then only needs to handle AD08+ distillation. Worth a one-line note in P12.3 now so the future instance does not redo this.
- 38.8. Projected result: DevPlan back to ~14–16 KB (12 KB core + truncated stubs). That should comfortably return you to default Sonnet for routine sessions.

---

39. Lu's Update —— notification test
- 39.1. Yes, I was auto-notified. It arrived as a system-injected file-change notice (a `<system-reminder>`), not chat input, with this literal signature you can condition on: **"Note: `<path>` was modified, either by the user or by a linter. This change was intentional… Here are the relevant changes (shown with line numbers):"**.
- 39.2. I do not have a guaranteed vendor API name for it, so rather than invent one (per §2.8.1), the reliable trigger to reference in future is that literal lead-in —— e.g. you can say "if you received the file-modified system reminder for `lu.md`, proceed…". The phrase "was modified, either by the user or by a linter" is the stable, matchable marker.
- 39.3. Important caveat: the notice showed the file from line 1 and then "[311 lines truncated]", so the excerpt I received was the unchanged head, not your actual new edit (which sits further down). The notification confirms lu.md changed, but does NOT reliably surface WHAT changed. So if you want me to act on a specific new edit, the notification alone is insufficient —— I would need to re-read (which I have not done, per your instruction).

---

40. Net
- 40.1. Nothing moved or edited this turn. On your go-ahead I will (a) confirm the 37.1 mapping, (b) execute the directory archival into existing `Archive/`, (c) externalise + truncate AD01–07, and (d) update `CP_index_cc.md` accordingly —— in that order, with Move/Void Rules observed.
