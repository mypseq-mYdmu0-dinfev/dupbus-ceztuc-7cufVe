# Job Opportunity Processing (`#jop`)
*Strict Prereq: `job.md`*

## Trigger
- `#jop` (CC-usable term, not just user) OR any flagged items from `#job`
- Before processing, request approval in the same `career_response_`; per item, state plan briefly.

## Processing order
- Follow `#job` result order: **importance, then recency (NEWEST first)** —— NOT oldest first.
- Rationale: oldest may have EXPIRED (effort wasted); the freshest are most likely still live.

## Flagged item types
- FL1. **Employer manual invite**: find AR → read files / open job post / CIC as needed → draft professional reply → append invite (verbatim) + reply to AR.
- FL2. **SEEK relay msg (truncated)**: ask user for full content → process as above.
- FL3. **Pending action**: assess URL safety (STOP if unsafe) → open via CIC → clear consent gates → find AR → read files / open job post / CIC as needed → pre-fill all fields (mind char limit; revise if over) → STOP before Submit → append questions + pre-filled answers to AR.
- Find AR per `career/CP_notes.md` § AR Finding.

## Consent gates (CIC)
- AGREE to every consent REQUIRED to proceed: ToS, privacy, e-signature auth, etc.
- DON'T opt into anything unnecessary (proceed-able w/o it): marketing / commercial-comms / promotional consents, optional surveys, talent-community subscriptions —— leave UNticked.
- Cookie banners: choose the privacy-preserving option (reject non-essential).
- NEVER create account or enter credentials (prohibited) —— skip.

## Reply rules
- Open "Dear Hiring Manager" unless sender name disclosed.
- My availability = current_TS + 72h → next 3pm on a working day.

## Answer rules
- Salary: AR Score < 85: ~$75,000/yr (~$1,438/wk); Score ≥ 85 or Fully Remote Work: ~$60,000/yr (~$1,151/wk); Select nearest available option ≤ target; never above.
- Visa: 485 Graduate Work Visa
- Full Driver's License: Yes
- Email (if asked): culousyu@gmail.com (NEVER use c@CulousYu.com despite in resumes)
- Availability to start working = current_TS + 72h + 1 week → next Monday
- Anything else: read `seek/context/ajap.md` § AJAP Handling Notes

## AR output
- Outputs go to the job's AR, never `response_`.
- NEVER dup AR or edit AR filename, so user can track diff.
- Append: `## 7. Engagements` → `### Employer Reply` + `### User Reply` (FL1&2) OR `### Additional Questions` + `### User Answers` (FL3).
- FL3 only: Immediately UNDER the `### Additional Questions` heading line, print **true URL** —— the CIC-opened tab's URL, NOT the long email link —— so open tabs map to ARs.
- When all done, briefly note thoughts in `response_`.

## Video Upload (only if requested)
- Upload '/Volumes/FURY 2TB/IYM/Private/Virtual Presentation/20250430/Export/renamed/Culous_Yu_Presentation.mov'
- If failed (too large, etc.), upload '/Volumes/FURY 2TB/IYM/Private/Virtual Presentation/20250430/Export/presentation_url.txt'
- If URL input allowed, extract from the .txt & paste into field
- if all failed (.txt unacceptable + no URL input field) or video time limit enforced (e.g. 60s): skip

## Skipped Items
- Remain `Label_2`.