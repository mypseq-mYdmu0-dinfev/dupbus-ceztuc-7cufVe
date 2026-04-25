# FETCH RULES

* IMPORTANT: Each file fetched ONCE only. Declare (#cc). STOP if fetch failed, don't proceed.

## UNCONDITIONAL

1. At every chat start, before generating anything (regardless of msg content; no exception), fetch & resolve all aliases below using `directory.md`: https://raw.githubusercontent.com/mypseq-mYdmu0-dinfev/dupbus-ceztuc-7cufVe/main/universal/directory_38.md
2. Prerequisites of ANY response before planning/creating anything:
2.1. Run `#context`: Check result block, if ANY contains "Older tool result cleared to save context", RE-FETCH `directory.md` then `context.md`
2.2. Scan full incoming msg for ALL conditional keywords, both explicitly & implicitly (e.g. "proceed to..." on deliverables all trigger `writing.md`) → fetch triggered files then declare
2.3. Re-consult ALL prompt files fetched earlier (inc. chat start) → run compliance pass (e.g. Hart's quotation rule)

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