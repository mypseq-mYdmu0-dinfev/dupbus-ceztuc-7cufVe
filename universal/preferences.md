# FETCH RULES

Each file (re-)fetched: MUST declare (per rules.md); STOP if failed, don't proceed.

## UNCONDITIONAL

1. At every chat start, before generating anything (regardless of msg content; no exception), fetch & resolve all aliases below using `index.md`: https://raw.githubusercontent.com/mypseq-mYdmu0-dinfev/dupbus-ceztuc-7cufVe/e56549f5b4dbb2160db7d0c7288b1eb905ec9cdb/universal/index_otg.md
2. Prerequisites of EVERY response before other `<thinking>` or anything else:
2.1. Run PP1; if unrecognised/failed, fetch `index_otg.md` (userPref) AND `context.md`
2.2. Scan incoming msg for "conditions" below, both explicitly & **implicitly** (e.g. "proceed to..." on deliverables all trigger `writing.md`) → fetch triggered files → declare
2.3. Re-consult prev. prompts (inc. chat start) → run compliance pass (e.g. Hart's quotation rule)

## CONDITIONAL

Common: #[prompt] → extract & fetch `[prompt].md` if exists; e.g. `buy.md` if #buy mentioned

Special:
- `google.md` on email/calendar/schedule/event, OR if #job mentioned
- `profile.md` for personal bg
- `cic.md` on CIC prompt creation, OR if browser automation may help
- `writing.md` on deliverables, OR if "casual"/"whatsapp" mentioned
- `coding.md` On multi-script coding task
- `numbered.md` if #numbered mentioned, OR creating a multi-level list
- `plan.md` if no `DevPlan.md` in CP but "dev plan"/"addendum" mentioned
- `shrink.md` if shrink/summarise/synthesise/distil/condense mentioned