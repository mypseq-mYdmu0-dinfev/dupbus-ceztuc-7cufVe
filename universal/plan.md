# [title] Dev Plan (Template for Development/Project Plan)
**Goal/Output:** [one_line_descr]
**Organisation:** [name]
**Due:** [YYYYMMDDHHmm]
**Target Result:** [value/descr]
**Created:** [YYYYMMDDHHmm] (Session [nn])

```
**Internal Rules (delete when creating):**
- Filename: `[project_alias]_DevPlan.md`
- This opening (before "PART A") must be concise, start w/ `# [title] Dev Plan`, and end w/ `**Created:** …`; lines between = examples (editable)
- "PARTS A–C" are mandatory, add more if necessary after approval
- ONLY use separators `---` right after opening and between "PARTS" (see below)
- `[nn]` = 2-digit no.; e.g. ❌ "Session 1"; ✅ "Session 01"
```

---

## PART A —— PROJECT PHASES

### P1. [brief_heading]

- P1.1. [brief_heading]
> [one_liner] (only if no sub-bullets needed; max. 10 words)

- P1.2. [brief_heading]
  - P1.2.1. [task]
  - P1.2.2. [task]
  …
  - P1.2.9. Remarks: [remarks] (if applicable)

### P2. [brief_heading]
…

```
**Internal Rules (delete when creating):**
- [task] = executable items (e.g. "Decide ..."), anything else (e.g. rationale) → [remarks]
- [remarks] = non-executable items (e.g. concise rationale, internal notes); must be a sub-phase's final item (e.g. P1.2.9 for P1.2.1–P1.2.8), NOT a phase (e.g. P3) or sub-phase (e.g. P1.3)
- Plan all the way to true completion (e.g. QC+delivery)
  - Embed as one (or more if multiple deliverables) of phases: provisional content outline (numbering system temporarily changes from `P` to `S`; e.g. `S1` for Section/Slide 1; e.g. `S1.1` for S1's 1st item) for writeup/keynote, provisional architecture for technical project, or other naming you see fit
  - If applicable, specify which phase performs further research, refines/finalises outline/architecture, reviews/updates Dev Plan, etc.
- Max. 9 items each level
  - ✅ `P9. …`; ❌ `P10. …`
  - ✅ `P1.9. …`; ❌ `P1.10. …`
  - ✅ `P1.1.9. …`; ❌ `P1.1.10. …`
  - This avoids ⌘F `P1` returning `P1` `P10` `P11` etc.
  - This avoids the need of 2-digit numbers (e.g. `P01.01. …`)
- Build more levels (Pnn.n.n.n. etc.) or multiple Dev Plan if necessary
- NEVER:
  - P0 in PART A; see `- P0 ...` in PART C
  - P[nn].0; see `> [one_liner] ...` above
- For very long (usually months) and/or growing (adding phases post-creation) projects:
  - User may prompt for reconstruction to lean, which is why you're reading this after its creation
  - Stub completed phases ONCE at each reconstruction, together, never piecemeal
```

---

## PART B —— MASTER CONTEXT

> Standing Rules: DevPlan can't be edited by CC unless requested (only on requested lines). Precise Status: by `close_` & AD. Phase (not sub-phase) Completion: reminder user to note on heading line by suggesting e.g. `P1. [heading] *(done on [TS]; [optional_≤20chars_remarks]*)`. When user requests to reconstruct DevPlan (e.g. lean), immediately read plan.md before action.

### M1. Organisation & Scope
…

### M2. Core Thesis/Objective
…

### M3. Key Theories/Assumptions
…

```
**Internal Rules (delete when creating):**
- Focus on constant info remaining unchanged throughout (e.g. deadline, budget)
- Above M1–3 are examples only, not necessarily applicable
- No max. item limit like "PART A"; be most efficient by all means; intended for Claude only
- If academic: build `[project_code/alias]_RefRepo.md` instead of including here
- DON'T repeat other synthesised files (e.g. `ProjectSummary.md` `Core_File_Summary.md`)
- The line `> Standing Rules: ...` must remain verbatim in DevPlan just like `## PART [X] ...`
- "DevPlan can't be edited" is enforced AFTER user's confirmation of initial creation completion
```

---

## PART C —— PER-SESSION ADDENDA

### AD01. P0 (Session [nn]) —— [≤8w_Heading]

- AD01.1. Coverage
  - AD01.1.1. …

- AD01.2. Decisions
...

```
**Internal Rules (delete when creating):**
- Follow close.md § Addendum Template for canonical requirements
- 1st level `AD[nn]. …` must be 2-digit to accommodate 9⁺ sessions
- P0 (Phase 0) = anything before & during Dev Plan creation
- Reminder: must be MECE (per close.md § Addendum Rules)
```