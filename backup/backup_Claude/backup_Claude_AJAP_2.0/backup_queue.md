# AJAP Fallback Queue (`queue.md`)

*Referenced by `ajap.md § Tab 1 Accessibility Check` (A6) and `§ S7 Pagination`. This is NOT a `context/` file (it is mutable run-data, not protocol). The user reorders the `order:` line freely; never reorder by cut-pasting Qi rows.*

---

## order: 01, 02, 03

*AJAP processes Qi strictly in the sequence on this line (left → right), NOT by row order in the table. To reprioritise, the user edits ONLY this line (e.g. `order: 02, 01, 03`).*

---

## Queue Table

| # | keyword | `&tags=new` | param | URL |
|---|---|---|---|---|
| Qi01 | `business analyst` | yes | 100k/4class/anytime | `https://au.seek.com/business-analyst-jobs/in-Sydney-NSW-2000?classification=6263%2C6076%2C6281%2C6008&distance=25&salaryrange=0-100000&salarytype=annual&tags=new` |
| Qi02 | `ui/ux` | yes | ditto | `https://au.seek.com/jobs/in-Sydney-NSW-2000?classification=6263%2C6076%2C6281%2C6008&distance=25&keywords=ui%2Fux&salaryrange=0-100000&salarytype=annual&tags=new` |
| Qi03 | `business` | yes | ditto | `https://au.seek.com/business-jobs/in-Sydney-NSW-2000?classification=6263%2C6076%2C6281%2C6008&distance=25&salaryrange=0-100000&salarytype=annual&tags=new` |

*Note: param col is for user's view only; completely disregard it & don't be influenced.*

---

## Processing Rules (per Qi)

1. Each table URL already carries `&tags=new` (lands directly on "New to you"). AJAP derives TWO passes per Qi automatically — do NOT add separate `n`/`p` rows:
- 1.1. **`[Qi]n` (new) — process FIRST.** Navigate to the table URL **unchanged** (it has `&tags=new`). Process all "New to you" cards across all its pages.
- 1.2. **`[Qi]p` (plain) — process SECOND.** Take the SAME URL and **strip** the trailing `&tags=new` (stripping is safer than appending). Navigate there; process the default (all) view. This catches anything not surfaced under "New to you".
- 1.3. Only after BOTH `[Qi]n` and `[Qi]p` are exhausted, advance to the next Qi in the `order:` line.
2. **New-to-you enforcement on every navigation** (new page, or new Qi/pass):
- 2.1. After landing, read the "New to you" pill (blue stroke; green count to its right) and report its count in the SA loop report as `newtoyou=[n]`.
- 2.2. If the current URL contains `&tags=new` → you are correctly on the New-to-you view; proceed.
- 2.3. If the current URL does NOT contain `&tags=new` AND `n` = 0 → correct (New-to-you genuinely consumed); proceed with the plain view.
- 2.4. If the current URL does NOT contain `&tags=new` BUT `n` > 0 → either a miss or jobs were just posted; **click "New to you" immediately** and prioritise those `n` cards before continuing the plain view. MA also enforces this from the `newtoyou=` field in the report.
3. URL construction restriction (per `ajap.md` A7) still applies: use ONLY the URLs in this table (and the mechanical `&tags=new` strip). Never hand-build any other SEEK URL.

---

## All-Qi-Exhausted Edge Case

*Runs ONLY when every Qi (`n` + `p`) is genuinely exhausted — extremely rare. Execute the two steps in order.*

1. **Step A — recover mislabelled externals (always runs).** Re-scan THIS-session `gcl/skipped/` files (NOT `skipped_archive`) for the keyword `external`. For each, re-open the job post and re-verify the apply method. If it is actually "Quick apply" (not a true external portal) AND its score qualifies (≥35 per `ajap.md` bands), void the bad skip AR and apply properly.

2. **Step B — lower the external gate (GATED; off by default).**
- 2.1. `Active: false`
- 2.2. While `Active: false`, Step B never runs. To arm it, the user replaces `false` with `active` on the line above.
- 2.3. When armed (and ONLY after Step A is complete): temporarily treat the external-portal score gate as **35** instead of the `ajap.md`-defined **70** — i.e. attempt any external-portal job scoring ≥35 (still respecting external-portal time limits and the struggle path). The `ajap.md` 70-gate value itself is NOT edited; this is a one-off, edge-case override defined here.
