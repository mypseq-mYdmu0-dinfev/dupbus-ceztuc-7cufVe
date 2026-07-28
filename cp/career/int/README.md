# Interviews Preparation & Analysis

## Basics
- Outside AJAP scope (`AJAP_repo/`)
- Enriched ARs of jobs at interview stage (scheduled or completed)
- Special: an AR might be placed here w/ trial task received, even w/o interview scheduled
- TS = upcoming/last interview time, NOT AR creation time
- Original ARs remain in `AJAP_repo/gcl|ccl/` w/ creation TS
- `g_int/` = general (non-consulting) roles, dup from `gcl/`
- `c_int/`= consulting roles, dup from `ccl/`

## Structure
- Original AR's §1 ("Employer") expands into e.g. `1.1. Company Basics` `1.2. Scale & Footprint` `1.3. Leadership & People` `1.4. Interviewer` (not necessary to follow; adapt as needed)
- Original AR's §5 ("Interviewer Questions") renames as "Interview Prep" AND expands into `5.1. Anticipated Interviewer Questions` `5.2. Questions to Ask Interviewer` `5.3. Logistics & Format` (e.g. virtual/physical? parking available?) `5.4. Strategy & Key Talking Points` (ideal to follow; add more subsections as needed)
- Original AR's §2 & §4 is audited against job post (if still live)
- Original AR's §3 & §6 is kept intact to mirror application
- Remind user to create §7 ("Engagements") & append emails/calls (exc. long convo) as `### 7.01. Employer Invite` `### 7.02. User Reply` etc.
- After 1st interview OR if there's a trial task (TT), add §8 ("Interviews") to store everything interview-related, e.g. TT Summary (enumerate+distill what were received), TT Synthesis (what it actually tests), TT Strategy (how to handle & present), interviews
- Each interview section has:
  - heading: `### 8.[n]. [1st/2nd/3rd] Interview ([start_TS])`
  - subsection 1: `#### 8.[n].1. Summary` —— by CC, based on Transcript
  - subsection 2: `#### 8.[n].2. Transcript` —— usually by Gemini; if needed, break into 2 sub-subsections: `##### 8.[n].2.1. Context` (user's in-meeting notes & any other remarks; e.g. transcript was compromised & reconstructed by CC via inference) & `##### 8.[n].2.1. Dialogue`
- If hired or there're multiple rounds of interviews, add §9 ("Stakeholder Profiles"); e.g. hierarchy, background, character, any other info useful for future comms & decisions —— based on user's/CC's direct/indirect observations and/or inferences