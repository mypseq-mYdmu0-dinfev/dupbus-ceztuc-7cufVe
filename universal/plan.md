# [title] Dev Plan (Template for Development/Project Plan)
**Goal/Output:** [one_line_descr]
**Organisation:** [name]
**Due:** [timestamp]
**Target Result:** [value/descr]
**Created:** [timestamp] (Chat [no.])

```
**Internal Rules (delete when creating):**
- Filename: `[project_alias]_DevPlan.md`
- This opening (before "PART A") must be concise, start w/ `# [title] Dev Plan`, and end w/ `**Created:** …`; lines between = examples (editable)
- "PARTS A-C" are mandatory, add more if necessary after approval
- ONLY use separators `---` right after opening and between "PARTS" (see below)
```

---

# PART A —— PROJECT PHASES

## P1. [brief_heading]

### P1.1. [brief_heading]
[one_line_descr] (when no sub-bullets needed)

### P1.2. [brief_heading]
- P1.2.1. [content]
- P1.2.2. [content]
…

## P2. [brief_heading]
…

```
**Internal Rules (delete when creating):**
- Plan all the way to true completion (e.g. QC+delivery)
  - Embed as one (or more if multiple deliverables) of phases: provisional content outline (numbering system temporarily changes to `S` & 2-digit e.g. `S01` for Section/Slide 1) for writeup/keynote, technical architecture for coding, or other naming you see fit
  - Specify which phase performs further research (if applicable), refines/finalises outline (if applicable)
- Max. 9 items each level
  - ✅ `P9. …`; ❌ `P10. …`
  - ✅ `P1.9. …`; ❌ `P1.10. …`
  - ✅ `P1.1.9. …`; ❌ `P1.1.10. …`
  - This avoids ⌘F `P1` returning `P1` `P10` `P11` etc.
  - This avoids the need of 2-digit numbers (e.g. `P01.01. …`)
- Build more levels (x.x.x.x. etc.) or multiple Dev Plan if necessary
```

---

# PART B —— MASTER CONTEXT


## M1. Organisation & Scope
…

## M2. Core Thesis/Objective
…

## M3. Key Theories/Assumptions
…

```
**Internal Rules (delete when creating):**
- Focus on constant info remaining unchanged throughout (e.g. deadline, budget)
- Above M1-3 are examples only, not necessarily applicable
- No max. item limit like "PART A"; be most efficient by all means; intended for Claude only
- If academic: build `[project_code/alias]_TheoryRepo.md` instead of including here
- DON'T repeat other synthesised files (e.g. `ProjectSummary.md` `Core_File_Summary.md`)
```

---

# PART C —— PER-CHAT ADDENDA

## AD01. P0 (Chat [no.]) —— [brief_heading]

### AD01.1. What Was Done
- AD01.1.1. …

### AD01.2. Key Decisions Made
- AD01.2.1. …

### AD01.3. Deviation from Dev Plan
- AD01.3.1. …

```
**Internal Rules (delete when creating):**
- Above AD01.1-3 are mandatory subsections for each addendum, input `N/A` if none
- Add subsections as needed, no limit like "PART A"
- 1st level `AD[no.]. …` must be 2-digit to accommodate 9⁺ chats
- P0 (Phase 0) = before Dev Plan creation
- DON'T repeat `Chat Handoff`
  - Chat Handoff: only for immediate next chat
  - Addendum: persists for all chats and worth it
  - Both created at each chat's end
```