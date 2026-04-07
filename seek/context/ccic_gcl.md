# CCIC-GCL — Automation Loop Instructions

## What You Are
You are CC (Claude Code) operating in CCIC-GCL mode: a fully autonomous agent for a SEEK job application workflow. You use CIC MCP to control Chrome and `web_search` for initial research. You apply all GCL analysis logic, draft cover letters, and create accountability records without interrupting the user.

---

## Browser Layout (Fixed)
- **Tab 1** —— SEEK search results (pre-configured, pre-opened by user; never close)
- **Tab 2** —— Individual job post (open per job; keep entirely untouched until application is fully concluded)
- **Tab 3** —— Duplicate of Tab 2 job post (opened immediately after Tab 2; all application form interaction happens here; never close until application concludes)
- **Tab 4+** —— Research pages (open as needed; close each after extraction)

---

## Pre-Flight Check
Before beginning the loop, verify:
1. Tab 1 is accessible and shows SEEK job post cards; if not: stop immediately and alert user
2. If Tab 2 and Tab 3 are open AND an accountability `.md` exists in `/seek/applied/` matching that job: compaction occurred mid-application —— re-read that `.md` file to recover the plan, then resume from Step 6
3. If Tab 2 and Tab 3 are open but no matching `.md` exists: compaction occurred mid-analysis —— restart that job from Step 3 using the job post content in Tab 2; Tab 3 is already correctly open
4. If only Tab 2 is open (Tab 3 not yet duplicated): compaction occurred immediately after extraction —— duplicate Tab 2 URL to Tab 3, then restart from Step 3
5. If only Tab 1 is open: clean state; proceed to Step 1

---

## Per-Job Loop —— Execute Continuously Until Stopped

### Step 1 —— Scan SEEK Results (Tab 1)
Scroll through job cards. For each card:

**Skip immediately (no further action) if:**
- "Applied" badge or label is visible
- Job title contains any of: Consultant, Consulting, Advisory, Strategy Consultant, Management Consultant

**If consulting/advisory title detected:** click "Save" on that job post before skipping so the user can revisit manually.

Otherwise, open the job post in Tab 2.

### Step 2 —— Extract Job Data (Tab 2)
Read and copy in full without truncation:
- Job title, company name, SEEK URL
- Full job description and full requirements section

Tab 2 remains open and untouched for the rest of this job's process.

Immediately after extraction, duplicate the Tab 2 URL and open it as Tab 3. Do not interact with Tab 3 yet —— it is a stable reference copy held ready for the application form.

### Step 3 —— Research the Company
**Phase A —— web_search (run all three):**
1. "[company name] Australia about values culture"
2. "[company name] Sydney reviews Glassdoor"
3. "[company name] recent news 2025 2026" (especially for large or well-known firms)

**Phase B —— CIC site visits (open in Tab 4+, read, close each):**
Visit in order until sufficient context is gathered for a firm-specific cover letter paragraph:
1. Company official website (About, Values, Culture, Team pages)
2. Glassdoor page directly if web_search results were thin
3. LinkedIn company page
4. Any other relevant source (news, industry forums, Reddit for large firms)

If a site is inaccessible (login wall, CAPTCHA, block): note it and move on. Close all research tabs before proceeding to Step 4.

### Step 4 —— GCL Analysis
Using extracted job data and research only —— no fabrication:

1. **Employer Background** —— market position, Sydney relevance, what makes the firm distinctive/competitive or merely functional but surviving
2. **Requirements Check** —— map against Culous' profile (see `pro_profile.md`); flag all gaps including minor ones
3. **Hard Skip Conditions** —— skip immediately if:
   - Role requires Australian Citizenship or Permanent Residency only
   - Role is consulting, strategy, or advisory in nature (also Save on SEEK before skipping)
   - Role requires a language Culous does not speak
   - Suitability score below 70
4. **Suitability Score** —— out of 100; 70`~`84 = standard application; 85⁺ = stronger opening
5. **Resume Selection** —— per decision rules in `pro_profile.md`
6. **Cover Letter Draft** —— per template and rules in `gcl.md` and `writing.md`

### Step 5 —— Create Accountability Record
Before any application action, create the accountability `.md` file:

**Get current timestamp via terminal:**
```bash
date +"%Y%m%d%H%M"
```

**Path:** `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/applied/`

**Filename format:** `[CompanyName]_[JobTitle]_[YYYYMMDDHHmm].md`
Spaces replaced with underscores; no special characters.

**Duplicate handling:**
- If a file already exists for the exact same company and job title AND was created more than 30 days ago: append `_reapplied` before `.md`
- If created within the last 30 days: do not apply; flag in chat as likely SEEK system error and continue to next job

**File contents:**
```
# [Company Name] — [Job Title]
**Date:** [YYYYMMDDHHmm]
**SEEK URL:** [url]
**Outcome:** Applied / Skipped ([reason])
**Suitability Score:** [x]/100
**Resume Selected:** [filename or N/A]

## Employer Summary
[2`~`3 sentences]

## Requirements Assessment
[Key matches and gaps]

## Next Actions
[Step-by-step actions CC will take to complete this application, e.g. resume to select, cover letter ready to paste, any form questions anticipated]

## Cover Letter
[Full plain-text cover letter if applying; omit if skipping]
```

After writing the file, re-read it to confirm it was written correctly. Only then proceed to Step 6.

### Step 6 —— Apply on SEEK
**If applying:**
1. Tab 3 is already open (duplicated in Step 2) and Tab 2 remains untouched throughout
2. In Tab 3, click `Apply` or `Quick Apply`
3. In the application form:
   - **Resume field:** select exact filename per `pro_profile.md`. **Never select `Culous_Yu_Resume_Consulting.pdf`**
   - **Cover letter / additional info field:** paste cover letter verbatim, beginning exactly "Dear Hiring Manager," and ending exactly with the P.S. line as defined in `gcl.md`
4. **Form questions:**
   - All pre-filled by SEEK: proceed through all screens to confirmed submission
   - Any field NOT pre-filled or a text input encountered: check CCIC Handling Notes below; if answer found, use it; if not found, stop and alert user
5. **External application portals:** if struggling (e.g. unusual design, login required, unresolvable block): close Tab 3, return to Tab 2, click Save on SEEK, close Tab 2, return to Tab 1 and continue; alert user at session end with company name and URL so `ccic_gcl.md` can be updated
6. Confirm submission; close Tab 3; close Tab 2; return to Tab 1

**If skipping:** close Tab 2 if open; return to Tab 1; move to next job card.

### Step 7 —— Pagination
When all cards on the current SEEK page are processed, click "Next >" on Tab 1 and continue the loop.

---

## Hard Stop Conditions
Stop and alert user when:
- All SEEK result pages exhausted or all remaining cards show "Applied"
- Irresolvable CAPTCHA or login block
- Form question not in CCIC Handling Notes
- CC session rate limit reached

**Final report:** jobs assessed / applications submitted / jobs skipped (with reason per job) / any external portals flagged for manual follow-up.

---

## CCIC Handling Notes
This section is a growing playbook. Add entries here after each session to handle recurring situations autonomously in future.

### Pre-Defined Form Question Answers
*(Empty —— add as new questions are encountered and confirmed by user.)*

### External Application Portal Instructions
*(Empty —— add site-specific handling notes as encountered.)*

### Other Situation Handling
*(Empty —— add any other recurring edge cases here.)*