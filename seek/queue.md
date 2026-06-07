# AJAP Queue

*Referenced by `ajap.md § Tab 1 Accessibility Check` (A6) and `§ S7 Pagination`. NOT a `context/` file (mutable run-data, not protocol). Reorder via the `order:` line only; never cut-paste Qi rows.*

---

## order: 07, 01, 03, 05, 08, 02, 04, 06

*Process Qi strictly left → right on this line, Qi01 → Qi06, sequentially. There is NO `n`/`p` system —— each Qi is a complete, ready-to-open URL. Qi01–03 are the New-to-you (`&tags=new`) views; Qi04–06 are the plain (all-jobs) views of the SAME three searches (its "new twin" is shown in the table). To reprioritise, edit ONLY this line (e.g. `order: 03, 06, 01, 04, 02, 05`).*

---

## Queue Table

| # | keyword | &tags=new | new twin | URL |
|---|---|---|---|---|
| Qi01 | `business analyst` | yes | — | `https://au.seek.com/business-analyst-jobs/in-Sydney-NSW-2000?classification=6263%2C6076%2C6281%2C6008&distance=25&salaryrange=0-100000&salarytype=annual&tags=new` |
| Qi02 | `business analyst` | no | Qi01 | `https://au.seek.com/business-analyst-jobs/in-Sydney-NSW-2000?classification=6263%2C6076%2C6281%2C6008&distance=25&salaryrange=0-100000&salarytype=annual` |
| Qi03 | `ui/ux` | yes | — | `https://au.seek.com/jobs/in-Sydney-NSW-2000?classification=6263%2C6076%2C6281%2C6008&distance=25&keywords=ui%2Fux&salaryrange=0-100000&salarytype=annual&tags=new` |
| Qi04 | `ui/ux` | no | Qi02 | `https://au.seek.com/jobs/in-Sydney-NSW-2000?classification=6263%2C6076%2C6281%2C6008&distance=25&keywords=ui%2Fux&salaryrange=0-100000&salarytype=annual` |
| Qi05 | `business` | yes | — | `https://au.seek.com/business-jobs/in-Sydney-NSW-2000?classification=6263%2C6076%2C6281%2C6008&distance=25&salaryrange=0-100000&salarytype=annual&tags=new` |
| Qi06 | `business` | no | Qi03 | `https://au.seek.com/business-jobs/in-Sydney-NSW-2000?classification=6263%2C6076%2C6281%2C6008&distance=25&salaryrange=0-100000&salarytype=annual` |
| Qi07 | `project` | yes | — | `https://au.seek.com/project-jobs/in-Sydney-NSW-2000?classification=6263%2C6076%2C6281%2C6008&distance=25&salaryrange=0-100000&salarytype=annual&tags=new` |
| Qi08 | `project` | no | — | `https://au.seek.com/project-jobs/in-Sydney-NSW-2000?classification=6263%2C6076%2C6281%2C6008&distance=25&salaryrange=0-100000&salarytype=annual` |

---

## Processing Rules

1. Process Qi01 → Qi06 in the `order:` line sequence. For each Qi, navigate to its exact URL (no editing) and process all cards across all its pages, then advance to the next Qi. Move on only when a Qi is exhausted.
2. **New-to-you handling (open the right Qi —— NEVER click the pill, NEVER append `&tags=new`):**
- 2.1. After landing on any Qi page, read the "New to you" pill (blue stroke; green count to its right) and report it in the SA loop report as `newtoyou=[n]`.
- 2.2. On a `tags=new` Qi (Qi01–03): you are already on the New-to-you view; proceed.
- 2.3. On a plain Qi (Qi04–06) with `n` = 0: New-to-you genuinely consumed; proceed with the plain view.
- 2.4. On a plain Qi (Qi04–06) with `n` > 0 (jobs just posted): do NOT click the pill and do NOT append `&tags=new` to the current URL —— appending on a page the "new" view does not extend to (e.g. you are on p.7 but "new" has 1 page) CRASHES the site. Instead NAVIGATE to this Qi's **new twin** URL (Qi01–03 per the table), process those fresh cards, then return to the plain Qi.
3. URL restriction (per `ajap.md` A7): use ONLY the exact URLs in this table. Never hand-build or edit any SEEK URL.

---

## All-Qi-Exhausted Edge Case

*Runs ONLY when every Qi01–06 is genuinely exhausted —— extremely rare. Execute in order.*

1. **Step A — recover mislabelled externals (always runs).** Re-scan THIS-session `gcl/skipped/` files (NOT `skipped_archive`) for the keyword `external`. For each, re-open the job post and re-verify the apply method. If it is actually "Quick apply" (not a true external portal) AND its score qualifies (≥35 per `ajap.md` bands), void the bad skip AR and apply properly.
2. **Step B — lower the external gate (GATED; off by default).**
- 2.1. `Active: false`
- 2.2. While `Active: false`, Step B never runs. To arm it, the user replaces `false` with `active` on the line above.
- 2.3. When armed (and ONLY after Step A is complete): temporarily treat the external-portal score gate as **35** instead of the `ajap.md`-defined **70** —— attempt any external-portal job scoring ≥35 (still respecting external-portal time limits and the struggle path). The `ajap.md` 70-gate value itself is NOT edited; this is a one-off, edge-case override defined here.
