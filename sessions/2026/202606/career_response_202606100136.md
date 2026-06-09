# Response to career_query_202606100136.md
*Mission 3 done in files; google.md left to you (#replace); 3 flags*

4. Created (concise, machine-read, no prose):
- 4.1. `career/job.md` —— `#job` scan spec; prereq google.md; CC + OTG. Holds scope / exclude / include / flag rules + CC-only post-scan step.
- 4.2. `career/jop.md` —— `#jop` processing (moved from CP_notes.md) + the **CC-actioning/actioned label protocol** + the `Label_2`/`Label_3` ID map; CC-exclusive.

5. Edited:
- 5.1. `career/CP_index_cc.md` —— added `job.md` + `jop.md` entries; added § 3.4 routing (`#job` → google.md then job.md; `#jop` → jop.md; flagged both as CP-scoped, not universal triggers).
- 5.2. `career/CP_index_otg.md` —— added `job.md` entry + `#job` routing line (report-only, no actuation); **NO `jop.md`** (CC-exclusive, per your instruction).
- 5.3. `career/CP_notes.md` —— replaced the bulky `#jop` section with a 1-line pointer to `jop.md` (avoids duplication; keeps CP unconditionals lean). Flagging since you didn't name this file —— revert if unwanted.

6. **YOUR `#replace` on `universal/google.md`** (I did not touch it):
- 6.1. **DELETE** this whole block under `## Gmail` (the `#job` scan spec):
```
- When prompted `#job`, scan for anything related to job application/interview/offer, etc.
  - Exclude application confirmations inc. but not limited to
    - SEEK official: Title "Your application was successfully submitted" from `noreply@s.seek.com.au`
    - Employer automatic: e.g. content inc. received, will be in touch, find out more, will review, in process/progress, track application, assessing
  - Briefly include progress update (e.g. "viewed"), rejection (e.g. "haven't progressed")
  - Flag pending actions (even automatic): e.g. complete your application, a few more questions
  - Flag employer manual (judge by yourself; e.g. "move forward", "invite")
  - Order: prioritise importance then recency
  - Scope: 1 week unless specified
  - Sender: any, NOT just SEEK
- CC: When prompted `#job`, read `career/CP_notes.md`
```
- 6.2. **REPLACE** with one line:
```
- `#job` scan spec → `career/job.md` (career CP; route via `career/CP_index_cc.md` § 3.4)
```
- 6.3. **KEEP unchanged:** the Timezone line (general Gmail) and the entire `### Labels` block. That block already holds **only `Label_1`** —— no `CC-actioning/actioned` is in google.md, matching your "general usage" rule. (Their map lives in `jop.md`.)

7. Flags / your call:
- 7.1. **Label-protocol home** —— I housed the CC-actioning/actioned protocol + `Label_2`/`Label_3` map in **`jop.md`** (CC-exclusive, matches "only CC actuates"). It is nominally "ALL tasks", but jop.md is the sole CC email-actioning context here. If you want it truly global, name a CC-only universal file and I'll move it.
- 7.2. **OTG index URL** —— `CP_index_otg.md`'s new `job.md` entry has a **placeholder** where the pinned GitHub raw URL goes (OTGC fetches by URL, not path). **Add the real raw URL after you commit `career/job.md`**, in the same pinned-commit form as the other entries.
- 7.3. **Root `CLAUDE.md` § 7.2** —— I left the row "`google.md` | … OR `#job` mentioned" **as-is** (didn't touch root). It still works: `#job` loads google.md, which now points to job.md. Optional tidy if you'd rather `#job` route straight via the CP index —— tell me and I'll give that as a separate `#replace`.

8. Net read-path after your 6: `#job` → google.md (lean Gmail + Label_1 skip + pointer) → `career/job.md` (scan) → CC: `career/jop.md` (`#jop` + labels). Unconditionals stay lighter (CP_notes.md trimmed).
