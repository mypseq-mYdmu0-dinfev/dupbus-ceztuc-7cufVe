# AJAP Queue Items (Qi)

*Referenced by `ajap.md § Tab 1 Accessibility Check` (A6) and `§ S7 Pagination`. NOT a `context/` file (mutable run-data, not protocol).*

---

## order: 01, 07, 03, 05, 02, 08, 04, 06

*Process Qi strictly left → right on this line (first Qi → last Qi), sequentially. Odd numbers are the "New-to-you" views (with `&tags=new`; NEVER append manually); even numbers are the plain (all-jobs) views. User reprioritises by editing ONLY this line (e.g. `order: 03, 06, 01`), not the table below.*

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

1. Process the Qi strictly in the live `## order:` line sequence (read that line each time —— positions are defined by it, NEVER by numeric Qi number; it may have been reordered), ALWAYS working the EARLIEST non-exhausted Qi in that line. For each Qi, navigate to its exact URL (no editing) and process all cards across all its pages.
- 1.1. **Re-verification sweep (before advancing —— NEW):** when the current Qi is exhausted, do NOT jump straight to the next. First re-read the `## order:` line, then re-open every Qi that sits EARLIER than the current one on that line, walking left → right from the 1st position, each at its page-1 URL, and confirm it is still exhausted (apply rule 2 New-to-you handling on each landing). If an earlier Qi now shows unprocessed/new cards (freshly posted since it was last exhausted), process them there (ONE card per loop, as usual; already-processed cards silently K3-skip) before continuing. Advance to the NEXT (later) position on the `## order:` line ONLY once every earlier Qi AND the current Qi are confirmed exhausted within the same sweep.
- 1.2. Net effect: new jobs in earlier searches are always picked up before going deeper. Example with `order: 01, 07, 05, 02, 04` —— when Qi07 (2nd position) is exhausted: re-check Qi01 (1st), then Qi07 (2nd); if both truly exhausted, proceed to Qi05 (3rd). When Qi05 (3rd) is exhausted: re-check Qi01, Qi07, Qi05 in that order, then proceed to Qi02 (4th). The walk always follows the `## order:` line, not the numeric label.
2. **New-to-you handling (open the right Qi —— NEVER click the pill, NEVER append `&tags=new`):**
- 2.1. After landing on any Qi page, read the "New to you" pill (blue stroke; green count to its right) and report it in the SA loop report as `newtoyou=[n]`.
- 2.2. On a `tags=new` Qi (odd no.): you are already on the New-to-you view; proceed.
- 2.3. On a plain Qi (even no.) with `n` = 0: New-to-you genuinely consumed; proceed with the plain view.
- 2.4. On a plain Qi with `n` > 0 (jobs just posted): do NOT click the pill and do NOT append `&tags=new` to the current URL —— appending on a page the "new" view does not extend to (e.g. you are on p.7 but "new" has 1 page) CRASHES the site. Instead NAVIGATE to this Qi's **new twin** URL (Qi[no.-1]), process those fresh cards, then return to the plain Qi.
3. URL restriction (per `ajap.md` A7): use ONLY the exact URLs in this table. Never hand-build or edit any SEEK URL.

---

## All-Qi-Exhausted Edge Case

*Runs ONLY when ALL Qi is genuinely exhausted —— extremely rare. Execute in order.*

1. **Step A — recover mislabelled externals (always runs).** Re-scan THIS-session `gcl/skipped/` files (NOT `skipped_archive`) for the keyword `external`. For each, re-open the job post and re-verify the apply method. If it is actually "Quick apply" (not a true external portal) AND its score qualifies (≥35 per `ajap.md` bands), void the bad skip AR and apply properly.
2. **Step B — lower the external gate (GATED; off by default).**
- 2.1. `Active: false`
- 2.2. While `Active: false`, Step B never runs. To arm it, the user replaces `false` with `active` on the line above.
- 2.3. When armed (and ONLY after Step A is complete): temporarily treat the external-portal score gate as **35** instead of the `ajap.md`-defined **70** —— attempt any external-portal job scoring ≥35 (still respecting external-portal time limits and the struggle path). The `ajap.md` 70-gate value itself is NOT edited; this is a one-off, edge-case override defined here.