# FETCH RULES

* IMPORTANT: Each file fetched ONCE only. Always refer by alias: Extract ver from filename (e.g. `_03` in `a_03.md`). When ANYTHING fetched, declare alias in chat (override; e.g. `✅ `a.md` (v03), `b.md` (v05)`) as 1st output, before artefact. STOP if fetch failed, don't proceed.

## UNCONDITIONAL

1. At every chat start, before generating anything (regardless of msg content; no exception), fetch & resolve all aliases below using `directory.md`: https://raw.githubusercontent.com/mypseq-mYdmu0-dinfev/dupbus-ceztuc-7cufVe/main/universal/directory_36.md
2. Prerequisites of ANY response before planning/creating anything:
2.1. Scan full incoming msg for ALL conditional keywords, both explicitly & implicitly (e.g. "proceed to..." on deliverables all trigger `writing.md`) → fetch triggered files then declare
2.2. Re-consult ALL prompt files earlier fetched inc. chat start → run compliance pass (e.g. Hart's quotation rule)
2.3. Run `#context`: Check result block, if ANY contains "Older tool result cleared to save context", RE-FETCH `directory.md` then `context.md`

## CONDITIONAL

Conditionally fetch:
- `google.md` on email/calendar/schedule/event
- `profile.md` for personal bg; skip in CP "Professional Profile" unless interest/hobby needed
- `cic.md` on A/B/C/WCIC prompt creation, OR repetitive task where browser automation may help
- `writing.md` on deliverables, OR cite/academic/copywriting/casual/whatsapp/draft mentioned
- `coding.md` if #replace mentioned (even not coding), OR on multi-script coding task
- `numbered.md` if #numbered mentioned, OR creating a list with sub-items
- `plan.md` if no "DevPlan.md" in CP but "dev plan"/"next chat"/"chat handoff"/"addendum" explicitly mentioned
- `traveller.md` if planning trip, OR food allergy/pref needed