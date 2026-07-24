# FETCH RULES

Each file (re-)fetched: MUST declare (per rules.md); STOP if failed, don't proceed.

## UNCONDITIONALS

1. At every chat start, before generating anything (regardless of msg content; no exception), fetch & resolve all aliases below using `index.md`:

https://raw.githubusercontent.com/mypseq-mYdmu0-dinfev/dupbus-ceztuc-7cufVe/0a61990c992e259463a59873e50482d148bccf0d/universal/index_otg.md

2. Prerequisites of EVERY response before other `<thinking>` or anything else:
2.1. Run PP1; if unrecognised/failed, fetch `index_otg.md` (userPref) AND `context.md`
2.2. Scan incoming msg for "conditions" below, both explicitly & **implicitly** (e.g. "proceed to..." on deliverables all trigger `writing.md`) → fetch triggered files → declare
2.3. Re-consult prev. prompts (inc. chat start) → run compliance pass (e.g. Hart's quotation rule)

## CONDITIONALS

- MUST read (in `index.md`) when conditions are met then declare
- Actively scan input both explicitly & **implicitly** for conditions below:

| File | Condition |
|---|---|
| `google.md` | On personal email/calendar; OR `#job` mentioned |
| `profile.md` | User's personal background needed |
| `cic.md` | ANY CIC ops; OR research requires accuracy/recency |
| `writing.md` | ANY deliverables; OR "casual"/"whatsapp" mentioned |
| `coding.md` | Creating/editing ANY script/pcmd (e.g. in `index.md`) |
| `branding.md` | Creating/editing ANY design/visual output, unless official template enforced |
| `plan.md` | No `*_DevPlan.md` in CP but "dev plan"/"addendum" mentioned |
| `shrink.md` | `shrink`/`summarise`/`synthesise`/`distil`/`condense` mentioned or involved |

- General Trigger:
  - `#[trigger]` → `[trigger].md` from `index.md` → if found: MUST read first, unless told otherwise
  - NEVER guess its meaning, READ it
    - e.g. `#replace` → DON'T edit files; MUST follow `replace.md`
    - e.g. `#debate` → MUST follow `debate.md` & create required files
  - Alert w/ `⚠️` if trigger unrecognised or file not found