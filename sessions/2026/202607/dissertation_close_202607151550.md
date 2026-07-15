# Dissertation (MP) Session Handoff (202606272120–202607151828)
*Session 17: A1R Ethics Forms + Ad Build + P15.2 Online Application Filled*

## 1. Status
- 1.1. P14 (ethics forms + guides + advertisement) is FULLY COMPLETE and content-verified.
- 1.2. `202607141922/` is the live online-portal submission package: 3 forms + 3 guides (docx+pdf) + the ad (pdf+png), PIS/Consent now v3 (EU-transfer clause added); all verified content-matched to their `.md` sources.
- 1.3. P15.2 (online ethics application) COMPLETE through Section 25 —— the SA-driven attempt failed and was abandoned; the user filled the live form personally with CC as read-only monitor (see AD14). Final snapshot: `202607141922/Ethics_Application_202607151826.pdf`.
- 1.4. Next: P15.3 —— the user clicks "Request Signature" (25.23) whenever ready; this is deliberately NOT done by CC. Then await Lu's sign-off and WRITTEN ethics approval before any data collection.

## 2. Remarks
- 2.1. The file-changes sweep from query `202607092131` (window `202607042336`–`202607092131`), findings already in `dissertation_response_202607092131.md` §108–115: `CLAUDE.md` §9 renumbered to `9.[nn]` + new §9.04 (pcmd hard-coding) and §9.05 (`.docx`/`.md` canonical-source rule, applied THIS session); `glossary.md` gained root/default-repo/AJAP-repo distinction, `ses`/`wk`/`sesL`/`wkL` terms, and the `"professional"` bar-not-degree definition; `writing.md` tightened the WA-conversion trigger and added the Title Case email sign-off rule; `debate.md` dropped model selection (all SAs now uniformly Sonnet, ~1M context); `numbered.md` had a cosmetic emphasis tweak; `universal/br.md` was renamed to `universal/ww.md` (content still unread —— appears unrelated to dissertation work, flagged not investigated further).
- 2.2. `Ethics Forms/` folder roles, so a rejection is traceable —— `202607041906` = Lu's original blank templates (PDF only); `202607041946` = what we sent Lu in Log 25; `202607092008` = what Lu sent back in Log 27 (you re-populated this as the pristine record after an earlier SA edited it in place by mistake); `202607141922` = the current, ready-to-submit package (source of truth going forward).
- 2.3. `dissertation/ethics/` holds the canonical working `.md`/`.html` —— `_filled` = exactly what was sent in Log 25 (frozen record, reverted via git); `_external` = Lu's Log-27 edits, this is what mirrors into the submission docx; `_internal` (PIS only) = the participant-facing version with "Australia" and "CYC" reverted out, plain-language purpose paragraph.
- 2.4. `MGTK751_ad.html`/`.pdf`/`.png` —— final, Chrome-headless-exported; `@page` size MUST stay in physical units (`11.25in`, not `1080px`) or the PDF's line-wrap silently diverges from the PNG/screen render (this bit us once already).
- 2.5. Submission-format rule for P15 (per this session's final query) —— ad: both `.pdf`+`.png` if the portal allows, else `.pdf` only; everything else: `.pdf` only by default, unless the portal specifically also wants `.docx`, or wants `.docx` only, in which case follow that.
- 2.6. VLE URL for P15: `https://liverpool-online-study.com/course/view.php?id=3733` —— per an earlier correction, YOU must open it yourself (not CIC), or it won't land in the right MCP tab group. UoL account is already signed in per this session's final query.
- 2.7. Standing lesson from P15.2 —— the "Key Ethics Information Required.pdf" guide's question numbers do NOT reliably match the live portal's actual field numbers (e.g. guide's "Q1.10" text is really about the portal's field 1.7); always read the guide's literal instruction text, never assume its numbering aligns. Portal's actual 1.10 (Co-Investigators) = "Yes" with Lu duplicated from 1.7 is a deliberate user decision (redundant but accepted, not a blocker).

## 3. Non-CP Files (this session)
- 3.1. Created:
  - 3.1.1. `universal/branding.md` §Typography —— Garamond Display-weight rule added (own edit refined the exact product name to "Garamond Premiere Pro")
  - 3.1.2. `dissertation/ethics/MGTK751_ad.md`, `.html`, `.pdf`, `.png` (+ voided `_mini` variant, all 3 files)
  - 3.1.3. `dissertation/ethics/Participant_Information_Sheet_external.md`, `_internal.md`, `Consent_Form_external.md`, `Risk_Assessment_external.md`
  - 3.1.4. `dissertation_slog_202607040408.md`, `dissertation_slog_202607141920.md`
  - 3.1.5. `dissertation_debate_board_202607042239.md`, `dissertation_debate_digest_202607042239.md`
- 3.2. Modified:
  - 3.2.1. `dissertation/MGTK751_DevPlan.md` —— P13–P16 rebuilt, dates corrected, M5 removed/superseded, P15 sub-phases added (ad task, review reminder)
  - 3.2.2. `dissertation/lu.md` —— Logs 25–28 (25/26/28 drafted not sent, 27 is her real reply); §C08 character-observation note added
  - 3.2.3. `universal/plan.md` —— DevPlan-editing discipline rules
  - 3.2.4. `dissertation/ethics/Participant_Information_Sheet_filled.md`, `Consent_Form_filled.md`, `Risk_Assessment_filled.md` —— reverted to the pristine Log-25 record via `git checkout`
- 3.3. Moved/Voided/Deleted:
  - 3.3.1. `❌_MGTK751_ad_mini.html`/`.pdf`/`.png` —— voided per user's ditch instruction
  - 3.3.2. `From Lu/Ethics Forms/202607092008/` —— all 6 PDFs voided then the whole set of docx moved to `202607141922/`; user separately re-populated `202607092008/` with fresh pristine downloads
