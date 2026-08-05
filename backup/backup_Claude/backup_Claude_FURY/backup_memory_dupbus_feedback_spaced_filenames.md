---
name: feedback-spaced-filenames
description: "A space in a filename means it is the user's own file, not CC's — never \"fix\" it"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fec61349-1d3d-4508-9a15-73719aab002d
  modified: 2026-08-05T13:28:11.936Z
---

A filename containing a stray space is almost always one of Culous' OWN files, not something CC is expected to use directly (e.g. a `.numbers` sheet, a scanned document, an employer's `.docx`). A filename containing ` _ ` (space-underscore-space) before a 12-digit timestamp means the same, plus it is very likely an EXPORT carrying its export time.

His actual workflow, which explains the pattern: work in `X.md` → lay out in `X _ [TS].pages` → export `X _ [TS].pdf` for stakeholders. So the spaced name is a deliberate stage marker, not a typo.

**Why:** a repo-wide sweep once flagged 47 spaced filenames, of which only 2 were genuine defects (comms files with a stray space before their TS, which `cscpt/flint.py` now blocks at creation). Treating the rest as defects would have broken working files: every Automator `.app` bundle carries an Apple-generated `Contents/MacOS/Automator Application Stub`, including the `PDF Conversion.app` that root §8.8.3 itself depends on — rename it and the documented iWork pipeline dies. This is not a judgement call: `cp/ccsim/sandbox/flint_filename_gate_regression_test.py` pins a `REAL_LEGITIMATE` set of actual repo filenames carrying BOTH a 12-digit TS and whitespace, and asserts the gate leaves every one alone — the broad "whitespace in a TS-bearing name is a defect" rule was REJECTED because it flagged all of them.

**How to apply:** only ever flag a space that breaks a stated naming convention — in practice, a comms file where §3.3 mandates `[prefix]_[TS].md`. Leave every other spaced filename alone, and never propose a bulk rename on the space alone. If genuinely unsure, ask rather than rename: a wrong rename breaks references silently. Related: [[feedback-sa-brief-frontload-mandate]].
