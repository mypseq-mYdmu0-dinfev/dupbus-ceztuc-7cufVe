# FETCH RULES

* IMPORTANT: Each file (inc. CP docs) fetched ONCE per chat only. When ANYTHING fetched, declare actual filename (not alias) in chat (e.g. `✅ 1.md, 2.pdf`) as the very first chat output in that response, before artefact generation —— overrides "artefact only" / "no chat text" defaults. STOP & alert if any fetch failed, do not proceed.

## UNCONDITIONAL

- At every chat start, BEFORE generating ANY response (regardless of msg length or content), fetch & resolve all filename aliases below using directory.md: https://raw.githubusercontent.com/mypseq-mYdmu0-dinfev/dupbus-ceztuc-7cufVe/main/universal/directory_19.md
- Prerequisites of any response:
  - Scan full incoming msg for all conditional keywords, both explicitly and implicitly (e.g. "draft/create/proceed to..." on deliverables all trigger writing.md), and fetch all triggered files then declare
  - Re-consult ALL earlier fetched prompt files (.md) inc. chat start, and run a silent compliance pass before planning/creating anything (e.g. Hart's logical quotation rule)

## CONDITIONAL

Conditionally fetch:
- `google.md` if Gmail/Calendar mentioned, OR “apple notes”/capital-N "Notes" in msg, OR any calendar/schedule/event query
- `profile.md` if personal/family context, visa, professional bg needed; skip in CP "Professional Profile" unless personal context specifically required (e.g. hobbies)
- `cic.md` if CIC/CAI/CWI/Chrome mentioned, OR high-stake/repetitive task where browser automation may help
- `writing.md` if creating deliverables (as defined in glossary.md), OR cite/citation/academic/copywriting/casual/whatsapp/draft mentioned
- `coding.md` if #replace mentioned (even not coding), OR code/script mentioned/detected
- `numbered.md` if #numbered mentioned, OR creating a list with sub-items
- `plan.md` if no "DevPlan.md" in CP but "dev plan"/"next chat"/"chat handoff"/"addendum" explicitly mentioned