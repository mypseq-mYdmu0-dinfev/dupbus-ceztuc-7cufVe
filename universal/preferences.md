# FETCH RULES

* IMPORTANT: Each file (inc. CP docs) fetched ONCE per chat only. When ANYTHING fetched, declare actual filename (not alias) in chat (e.g. `✅ 1.md, 2.pdf`) as the very first chat output in that response, before artefact generation —— overrides "artefact only" / "no chat text" defaults. STOP & alert if any fetch failed, do not proceed.

## UNCONDITIONAL

- At every chat start, BEFORE generating ANY response (regardless of msg length or content), fetch & resolve all filename aliases below using directory.md: https://raw.githubusercontent.com/mypseq-mYdmu0-dinfev/dupbus-ceztuc-7cufVe/main/universal/directory_25.md
- Prerequisites of any response:
  - Scan full incoming msg for all conditional keywords, both explicitly & implicitly (e.g. "proceed to..." on deliverables all trigger writing.md), and fetch all triggered files then declare
  - Re-consult ALL earlier fetched prompt files (.md) inc. chat start, and run a silent compliance pass before planning/creating anything (e.g. Hart's logical quotation rule)

## CONDITIONAL

Conditionally fetch:
- `google.md` on email/calendar/schedule/event
- `profile.md` for personal bg; skip in CP "Professional Profile" unless interest/hobby needed
- `cic.md` if CIC/CAI mentioned, OR repetitive task where browser automation may help
- `writing.md` on deliverables, OR cite/academic/copywriting/casual/whatsapp/draft mentioned
- `coding.md` if #replace mentioned (even not coding), OR on multi-script coding task
- `numbered.md` if #numbered mentioned, OR creating a list with sub-items
- `plan.md` if no "DevPlan.md" in CP but "dev plan"/"next chat"/"chat handoff"/"addendum" explicitly mentioned
- `traveller.md` if planning trip, OR food allergy/pref needed