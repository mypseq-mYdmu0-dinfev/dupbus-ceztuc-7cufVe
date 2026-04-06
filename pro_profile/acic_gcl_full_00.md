# ACIC-GCL (Full) — Operating Instructions

## Activation
When a msg contains `start ACIC-GCL`, enter ACIC-GCL mode and follow this file in full. Fetch gcl.md and other prerequisites. NEVER apply CCL rules. No chat text —— artefacts are the sole output.

---

## Interface Layout
- **CAI** —— Claude App (macOS); brain and hands; all reasoning, drafting, browsing, and artefact creation happen here
- **Chrome Tab 1** —— SEEK search results (pre-configured, never close)
- **Chrome Tab 2+** —— Job posts and research pages (open to extract, then close)

---

## Artefact Types

**Type 1 —— Accountability Record**
Produced once per concluded job (applied or skipped). Title format: `[Company] — [Job Title]`. Contains: employer summary, requirements assessment, suitability score, resume selected (or skip reason), and cover letter in full. Intended for Culous to read after session.

No Type 2 or Type 3 in ACIC-GCL. CAI pastes the cover letter directly from its own drafting process.

---

## Initialisation Verification —— Run Once Before Loop Begins
Confirm gcl.md fetched, then confirm Chrome Tab 1 is the SEEK search results page and that job post cards are visible. If the tab is inaccessible, blank, or shows no job posts: stop immediately and alert Culous.

## Per-Job Loop —— Execute Continuously Until Stopped

### Step 1 —— Scan SEEK Results (Chrome Tab 1)
Scroll through job cards. Skip immediately (no further action) if:
- "Applied" badge or label is visible
- Job title contains: Consultant, Consulting, Advisory, Strategy Consultant, Management Consultant

Otherwise open job post in Chrome Tab 2.

### Step 2 —— Extract Job Data (Chrome Tab 2)
Copy in full without truncation:
- Job title, company name, SEEK URL
- Full job description and full requirements section

Close tab when done.

### Step 3 —— Research the Company (Chrome Tab 2+)
Open and copy raw text in full (no summarising). Close each tab after extraction. Sources:
1. Company official website (About, Values, Culture, Team)
2. LinkedIn company page (About, recent posts if visible)
3. Glassdoor —— search "[company name] reviews"; prioritise Sydney content but copy all available
4. Reddit, news articles, industry forums if applicable —— especially for well-known firms

If a site is inaccessible (CAPTCHA, login wall): note it and move on.

### Step 4 —— GCL Analysis (CAI)
Using extracted data only —— no independent web search:

1. **Employer Background** —— market position, Sydney relevance, what distinguishes or merely sustains the firm
2. **Requirements Check** —— map against Culous' profile; flag all gaps including minor ones
3. **Hard Skip Conditions** —— skip immediately if:
   - Role requires Australian Citizenship or Permanent Residency only
   - Role is consulting, strategy, or advisory in nature
   - Role requires a language Culous does not speak
   - Suitability score below 70
4. **Suitability Score** —— out of 100; 70`~`84 = standard application; 85⁺ = stronger opening
5. **Resume Selection** —— per decision rules below
6. **Cover Letter Draft** —— per template and rules below

### Step 5 —— Apply or Skip (Chrome Tab 2)
**If applying:**
1. Return to Chrome Tab 1 (SEEK results), locate the job, click Apply
2. Resume field: select exact filename per decision rules. **Never select Consulting Resume of Culous Yu**
3. Cover letter field: paste cover letter verbatim, "Dear Hiring Manager," through "P.S. ..." only
4. Form questions:
   - All pre-filled by SEEK: proceed through all screens to confirmed submission
   - Any field NOT pre-filled, or a text input field encountered: stop; check pre-defined answer bank below; if not found, stop and alert Culous
5. Confirm submission; close application tab; return to Chrome Tab 1

**If skipping:** return to Chrome Tab 1, move to next job card.

### Step 6 —— Create Type 1 Artefact (CAI)
After each concluded job (applied or skipped), produce one 🤵🏻‍♂️ Type 1 artefact containing:
- Employer summary
- Requirements assessment with suitability score
- Resume selected or skip reason
- Cover letter in full (if applied)

### Step 7 —— Pagination
When all cards on current SEEK page are processed, click Next Page and continue.

### Step 8 —— Hard Stop
Stop and report when:
- All result pages exhausted or all remaining cards show "Applied"
- Irresolvable CAPTCHA or login block encountered
- CAI session rate limit reached

Report: jobs assessed / applications submitted / jobs skipped (with reason).

---

## Resume Decision Rules

| Role Type | Resume to Select |
|---|---|
| Marketing, Branding, PR, Social Media, Content | Marketing Resume of Culous Yu |
| UX/UI, Service Design, Product Management | IxD Resume of Culous Yu |
| IT, IS, Data Analytics, Software Engineering | IT Resume of Culous Yu |
| All others (Admin, Operations, Customer Service, etc.) | General Resume of Culous Yu |
| Consulting, Strategy, Advisory | **SKIP —— do not apply** |

**Never select Consulting Resume of Culous Yu in this workflow.**

---

## Cover Letter Rules
Refer to `gcl.md` for the full cover letter template, tone rules, prohibited vocabulary, and all writing requirements. Apply them in full when drafting.

---

## Pre-Defined Form Question Answers
*(Empty —— answers added here as new questions are encountered and confirmed.)*

---

## Absolute Rules
- Never apply to consulting, strategy, or advisory roles
- Never select Consulting Resume of Culous Yu
- Never paste cover letter with any content before "Dear Hiring Manager," or after "P.S. ..."
- Never apply to roles requiring Australian Citizenship or Permanent Residency only
- Never fabricate employer details
- One Type 1 artefact per concluded job, always
