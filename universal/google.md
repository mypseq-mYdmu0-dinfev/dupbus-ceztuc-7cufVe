# Google Connectors

*`CC:` = for Claude Code only, disregard if you're not.*

## General

I've connected my Google Drive, Mail, and Calendar. If access failed (e.g. asked about events but calendar unlinked), STOP & alert me.

---

## Google Drive

- Never search in it unless I specifically ask so, since it only supports G docs

---

## Gmail

- Timezone: Gmail date filters use UTC; always fetch current SYD (or wherever I am) timezone offset before any date-based query and adjust boundaries
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
- CC: When prompted `#job`, after above actions:
  - Identify as `/career/` CP session → read Unconditionals → prefix forthcoming output files
  - In the same `response_`, ask for approval to process "flagged" items
  - For each, briefly tell you plan (see below)
- CC: "Flagged" items processing:
  - **Employer manual invite** → find AR in `/seek/applied/` → read other files, open job post, and use CIC as needed → draft a professional reply → append invite + reply to AR
  - **SEEK relay msg (truncated)** → ask user for full content → process as above
  - **Pending actions** → assess if URL is safe (STOP if not) → open via CIC → find AR in `/seek/applied/` → read other files, open job post, and use CIC as needed → pre-fill all fields (mind char limit; revise if over) → STOP before Submit → append questions + pre-filled answers to AR
  - For reply, start w/ "Dear Hiring Manager" unless sender name is disclosed
  - My availability = current_TS + 72h → next 3pm on a working day
  - Ensure outputs are in corresponding AR, not `response_`
  - Appending to AR: Create `## 7. Engagements` `### Employer Reply` `### User Reply`
  - When all done, briefly tell your thoughts in `response_`

---

## Google Calendar

- My Google Calendar account has many "calendars" inside, for example (mind the space in names, they're intended):
  - `  🐟` —— my events visible to my wife
  - ` 🐁` —— my wife's events
  - ` 🐟🐁` —— events attended by me and my wife tgt
  - `Deadlines` —— deadlines
  - `Notices` —— not actually events (e.g. Taobao ETA)
  - `General Events` —— originally primary "calendar" but unshared, rarely used, mostly duplicated entries as backup for high-stake events
- Ensure to search through ALL "calendars" when responding to queries related to calendar matters
- When searching through events, prioritise those with locations (likely actual offline attendance)
