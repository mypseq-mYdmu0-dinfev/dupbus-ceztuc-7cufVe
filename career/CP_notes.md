# Career CP Notes

*`CC:` = for Claude Code only, disregard if you're not.*

## Purpose
This CP ("Career") is for anything related to work: resume, cover letter (CL), interview, pitch, etc. Always use confident language & powerful proactive verbs to highlight relevant skills/experience in deliverables. Never use "I believe/feel/think".

## AJAP (Agentic Job Application Programme)
Fully autonomous CC agent that scans job cards, researches firms, scores roles, drafts CLs, and submits job applications via CIC — no user input; runs indefinitely; based on GCL.

## AR (Accountability Record)
Per-job .md logs storing score breakdown + GCL outputs.

## PAR (Pending AR)
Identified by `Outcome: Pending` on Line 4. Saved for manual ops due to consulting-related (need CCL), scored ≥110, blocked during application, or special opportunity. When received:
- Start by opening & reading full job post on Line 3 `URL:` via CIC; stop if failed (no fallback)
- In 1st artefact, critically evaluate PAR after full read; concisely tell if further research needed
- If research needed, follow cic.md using web_search + CIC
- If my msg doesn't indicate CCL/GCL, tell at 1st artefact end which protocol suits
- In 2nd artefact, follow CCL/GCL instr

## CC: AR Finding
- AR filename format: [Company]_[Role]_[TS].md
  - e.g. Dentons_BusinessAnalyst_202605091830.md = Business Analyst at Dentons
- `find` AR in (incl. subfolders):
  - `/seek/gcl/applied/` —— for applied/interview invite received
  - `/seek/gcl/skipped/` —— for skipped; least possible
  - `/seek/gcl/pending/`
    - for § PAR; `When received:` doesn't apply to you (`find` it)
    - "1st artefact" = `response_`
    - "2nd artefact" = move PAR to `/seek/gcl/applied/` as `⏳_[original_filename]_[current_TS].md` → edit it accordingly → `Outcome: Applying`
    - Start from oldest unless told otherwise
    - Stop at each PAR completion

## CC: Job Opportunity Processing (`#jop`)
- Spec moved to `career/jop.md` (CC-exclusive; read when `#job` flags items or `#jop` is prompted). Route via `career/CP_index_cc.md` § 3.4.

## Remarks
- IMPORTANT: NO FALSE CLAIMS; e.g. ✅ `16⁺yr in content & project mgmt` (generic) | ❌ `16⁺yr in [industry]/[other_domain]` (specific); check CP files (e.g. pro_profile.md § Domain Exp)
- Assume CAI by default in this CP. If CIC access fails, stop & remind to use CAI.
- Never disclose that I founded KE in any deliverable.
  - Exception: may suggest disclosing only if reliable evidence confirms the employer genuinely values entrepreneurial founding experience —— always seek my explicit approval before including in any deliverable.
- Willingness to travel/relocate for work: consulting roles only, not general/non-consulting roles.
- UTS: MUST use `GPA 6.63/7 (HD)` instead of `WAM 88%`.
- MBA: use `Grade A` or equiv. wording; only disclose if necessary: WAM 71%