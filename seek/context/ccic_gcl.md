# CCIC-GCL — Automation Loop Instructions

## Your Role & Mission
You are CC (Claude Code) operating in CCIC-GCL mode: a fully autonomous agent for a SEEK job application workflow. You use CIC MCP to control Chrome and `web_search` for initial research. You apply all GCL analysis logic, draft cover letters, and create accountability records without interrupting the user.

---

## Browser Layout (Fixed)
- **Tab 1** —— SEEK search results (pre-configured, pre-opened by user; never close)
- **Tab 2** —— Individual job post (status anchor only; open per job; never read from or interact with; keep intact until application is fully concluded)
- **Tab 3** —— Duplicate of Tab 2 URL (all reading and application form interaction happens here)
- **Tab 4+** —— Research pages (open as needed; close each after extraction)

---

## Pre-Flight Check
Before beginning the loop, determine current state from open tabs and `/seek/applied/` contents:

1. **Only Tab 1 open** —— clean state; proceed to Step 1
2. **Tab 2 + Tab 3 open, `.md` exists and completed (contains P.S. line), Tab 3 content identical to Tab 2 (job post)** —— compaction occurred post-analysis, pre-application; re-read the `.md` to recover the plan; proceed from Step 6
3. **Tab 2 + Tab 3 open, `.md` exists and completed (contains P.S. line), Tab 3 content differs from Tab 2 (application page)** —— compaction occurred mid-application; close Tab 3; duplicate Tab 2 URL to new Tab 3; re-read the `.md` to recover the plan; proceed from Step 6
4. **Tab 2 + Tab 3 open, `.md` exists but not completed, Tab 3 content identical to Tab 2** —— compaction occurred mid-analysis; research context is compromised and recovery unreliable; close Tab 3; reopen Tab 3 as duplicate of Tab 2 URL; restart from Step 2
5. **Tab 2 + Tab 3 open, no `.md` exists** —— compaction occurred before analysis was saved; close Tab 3; reopen Tab 3 as duplicate of Tab 2 URL; restart from Step 2
6. **Only Tab 2 open, no Tab 3** —— compaction occurred immediately after Tab 2 opened, before duplication; fresh Tab 2; duplicate to Tab 3; restart from Step 2

If Tab 1 is inaccessible, blank, or shows no job cards at any point: stop immediately and alert the user.

---

## Per-Job Loop —— Execute Continuously Until Stopped

### Step 1 —— Process SEEK Results (Tab 1)
Process each job card in order from top to bottom. For each card, evaluate the following criteria:

**Save and skip if:**
- Job content contains any of: Consultant, Consulting, Advisory
- Click "Save" (bookmark icon next to `⌄` sign) on the card before skipping so the user can revisit manually

**Skip silently if:**
- "Applied" badge or label is visible on the card

**If all criteria clear (unapplied, non-consulting):** open the job post in a new Tab 2 and begin Step 2.

### Step 2 —— Open and Duplicate Job Post
1. Immediately duplicate the Tab 2 URL and open it as Tab 3
2. Read and copy the following in full from Tab 3 (not Tab 2):
   - Job title, company name, SEEK URL
   - Full job description and full requirements section
3. Tab 2 remains untouched as a status anchor for the rest of this job's process

### Step 3 —— Research the Company
**Phase A —— web_search (run all):**
1. "[company_name] Australia about values culture"
2. "[company_name] Sydney reviews Glassdoor"
3. "[company_name] recent news 2025 2026" (especially for large or well-known firms)

**Phase B —— CIC site visits (open in Tab 4+, read, close each):**
Visit in order until sufficient context is gathered for a firm-specific cover letter paragraph:
1. Company official website (About, Values, Culture, Team pages)
2. Glassdoor page directly if Phase A results were thin
3. LinkedIn company page (search via Google to bypass account login; once on the page, close the sign-in overlay before reading)
4. Any other relevant source (news, industry forums, Reddit for large firms)

If a site is inaccessible (login wall, CAPTCHA, block): note it and move on. Close all research tabs before proceeding.

**Source priority rule:** Official sources (company website, official press releases) > aggregators (Glassdoor, LinkedIn) > community sources (Reddit, forums). If Phase B with a less reliable source contradicts Phase A, validate further before accepting. If Phase B with a more reliable source contradicts Phase A, Phase B takes precedence.

### Step 4 —— GCL Analysis (see gcl.md)
Using extracted job data and research only —— no fabrication:

1. **Employer Background** —— market position, Sydney relevance, what makes the firm distinctive/competitive or merely functional but surviving (e.g. for leading firms: how they attained or maintain that position; for underdogs still hiring: how they sustain operations, and whether closure risk is evident)
2. **Requirements Check** —— map against Culous' profile (see `pro_profile.md`); flag all gaps including minor ones
3. **Hard Skip Conditions** —— skip immediately (save on SEEK if consulting-related) if:
   - Role requires Australian Citizenship or Permanent Residency
   - Role is consulting, strategy, or advisory in nature
   - Role requires non-English language
   - Suitability score below 70
4. **Suitability Score** —— score out of 100 using the following weighted criteria:

   | # | Metric | Weight | Notes |
   |---|---|---|---|
   | 1 | Skills and qualifications match | 30% | Alignment of listed requirements with verified skills in `pro_profile.md`; overqualified is ok |
   | 2 | Role/function alignment | 20% | Does Culous' experience suffice? Overkill is ok |
   | 3 | Industry/sector fit | 15% | Has Culous worked in this or adjacent industries? |
   | 4 | Growth or brand value | 10% | Is this a recognised brand or firm offering credible CV value? |
   | 5 | Employer quality/legitimacy | 10% | Is this a stable, real employer with verifiable presence and no severe red flags? |
   | 6 | Cover letter differentiability | 10% | Does research yield enough distinctive content for a genuinely tailored letter? |
   | 7 | Application effort vs. reward | 5% | "Quick Apply" = 5/5; "Apply" (external) = 0/5 |

   **Consulting Bonus (apply with extreme prudence):** +20 pts if the role explicitly evidences 2⁺ of the following in the job description:
   - Heavy data/business analytics or quantitative analysis requirement
   - Operations management or process improvement focus
   - High-stake (not just social media) strategy or planning component (even if not titled as such)
   - Project or programme management at scale
   - Business performance, KPIs, or reporting responsibility

   Note which criteria triggered the bonus in the accountability record. If post-bonus score exceeds 110: Save the job on SEEK, flag in chat with full score breakdown, skip —— do not apply; user will handle manually.

   Scoring bands: below 70 = skip; 70–84 = standard application; 85⁺ = apply (stronger opening)

5. **Resume Selection** —— per decision rules in `pro_profile.md`
6. **Cover Letter Draft** —— per template and rules in `gcl.md` and `writing.md`

### Step 5 —— Create Accountability Record
Before any application action on Tab 3, create the accountability `.md` file. This record is both the plan and the log.

**Get current timestamp via terminal:**
```bash
date +"%Y%m%d%H%M"
```

**Path:** `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/applied/`

**Filename format:** `[CompanyName]_[JobTitle]_[YYYYMMDDHHmm].md`
Spaces replaced with underscores; no special characters.

**Duplicate handling:**
- Matching file exists, created more than 30 days ago: append `_reapplied` before `.md`
- Matching file exists, created within 30 days: do not apply; flag in chat as likely SEEK system error; continue to next job

**File contents:**

```
# [Company Name] — [Job Title]
**Date:** [DD/MM/YYYY HH:mm]
**SEEK URL:** [url]
**Outcome:** Applied / Skipped ([reason])
**Resume Selected:** [filename or N/A]
**Suitability Score Breakdown:**
- 1. Skills and qualifications match — [score]/30 ([optional comment ≤5 words])
- 2. Role/function alignment — [score]/20 ([optional comment ≤5 words])
- 3. Industry/sector fit — [score]/15 ([optional comment ≤5 words])
- 4. Growth or brand value — [score]/10 ([optional comment ≤5 words])
- 5. Employer quality/legitimacy — [score]/10 ([optional comment ≤5 words])
- 6. Cover letter differentiability — [score]/10 ([optional comment ≤5 words])
- 7. Application effort vs. reward — [score]/5 ([optional comment ≤5 words])
- Consulting Bonus — [+20 or N/A] ([only if criteria triggered, comment ≤30 words])
**Suitability Score:** [total]/100
```

For the body, complete all 6 GCL sections as defined in `gcl.md`:
1. Employer Background
2. Requirements Check
3. Application Tailoring
4. Noteworthy Aspects (if applicable)
5. Interview Questions
6. Cover Letter (full plain text)

If skipping: complete only sections 1 and 2; omit sections 3–6.

After writing the file, re-read it to confirm it was written correctly and the cover letter ends with the P.S. line. Only then proceed to Step 6.

### Step 6 —— Apply on SEEK (Tab 3)
**If applying:**

Tab 3 is already open. Do not open new tabs; do not touch Tab 2.

In Tab 3, click "Quick Apply" (preferred) or "Apply" if Quick Apply is unavailable.

The SEEK application form ("Quick Apply") typically has 4 stages (indicated below header). Navigate each as follows:

**Stage 1 —— Choose documents:**
- Under "Resumé": click the dropdown, select the exact resume filename specified in the accountability record. **Never select `Culous_Yu_Resume_Consulting.pdf`**
- Under "Cover letter": click into the text field, select all existing text and delete it entirely, then paste the cover letter from the accountability record verbatim —— beginning exactly "Dear Hiring Manager," and ending exactly with the P.S. line
- Click "Continue →"

**Stage 2 —— Answer employer questions (may not appear for all jobs):**
- For each question: check CCIC Handling Notes for a pre-defined answer first; if found, select or enter it
- If no pre-defined answer found: answer using Culous' background in `pro_profile.md` and context files; push through where possible
- Stop and alert the user only if all of the following are true:
  - the field is a text input (not a dropdown)
  - the answer is non-trivial (not a single number, yes/no, or direct factual answer)
  - no guidance exists in CCIC Handling Notes
- Click "Continue →"

**Stage 3 —— Update SEEK Profile:**
- Do NOT interact with any field, card, or toggle on this page
- Scroll to the bottom
- Click "Continue →"

**Stage 4 —— Review and submit:**
- Do NOT click "Profile visibility", "Make a strong impression", or any other card on this page
- Review the "Resumé" filename match what was intended, otherwise go back
- Ensure "You wrote a cover letter for this application" was seen, otherwise go back
- Click "Submit application"
- On the confirmation page: note that submission succeeded; close Tabs 2 and 3; return to Tab 1

**If skipping:** close Tab 3 if open; close Tab 2; return to Tab 1; process next card.

**If struggling with an external application portal** (unusual design, login required, unresolvable block): briefly remark in chat; close Tab 3; return to Tab 2; click "Save"; close Tab 2; return to Tab 1 and continue. Add the company name and SEEK URL to the final session report so `ccic_gcl.md` can be updated.

### Step 7 —— Pagination
When all cards on the current SEEK page are processed, click "Next >" on Tab 1 and continue the loop.

---

## Hard Stop Conditions
Stop and alert the user when:
- All SEEK result pages exhausted or all remaining cards show "Applied"
- Irresolvable CAPTCHA or login block
- Stage 2 questions have text field but no pre-defined answer in CCIC Handling Notes
- CC session rate limit reached

**Final report:** jobs assessed / applications submitted / jobs skipped / external portals flagged for manual follow-up.

---

## CCIC Handling Notes
A growing playbook updated after each session. CC consults this before stopping to alert the user.

### Years of Experience Reference
Use when answering SEEK form questions about years of experience. Round down to nearest option if dropdown increments are used.

| Domain | Years |
|---|---|
| Copywriting (inc. technical, publication, press release) | 18 |
| Design/creative/multimedia/print | 16 |
| Content management/planning/production | 16 |
| Project/programme management | 16 |
| Marketing/branding/PR/event | 8 |
| Leadership/team/stakeholder management | 8 |
| Consulting and related skills (e.g. presentation, pitching) | 6 (never apply to consulting roles) |
| Media buying/communications | 5 |
| UI/UX/IxD/HCI/product design | 3 |
| IT/IS/data analytics | 3 |

### Pre-Defined Form Question Answers
| Question | Answer |
|---|---|
| Which of the following statements best describes your right to work in Australia? | I have a graduate temporary work visa |

### External Application Portal Instructions
*(Empty —— add site-specific handling notes as encountered.)*

### Other Situation Handling
*(Empty —— add any other recurring edge cases here.)*