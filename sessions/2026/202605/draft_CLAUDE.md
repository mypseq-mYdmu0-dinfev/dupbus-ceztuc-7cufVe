# Claude Code —— Root Workspace Guidelines

*Root CLAUDE.md for `/dupbus-ceztuc-7cufVe/`. Governs all CC sessions started from this root,*
*unless a subfolder's CLAUDE.md specifies otherwise.*

---

## Session Start

At the start of every session, before generating anything, read the following in order:

1. `universal/glossary_12.md` (alias: `glossary.md`) —— terminology & definitions
2. `universal/cc_22.md` (alias: `cc.md`) —— interaction guidelines; **skip the `#pp` section entirely** (CWI-only)

Declare in chat: ✅ `glossary.md`, `cc.md`

**Version note:** Filenames include version numbers (e.g. `_12`, `_22`). If a file is not found, try a neighbouring version or alert with ⚠️.

**Monthly reminder:** If any previous month's subfolder in `/sessions/` lacks a `summary_` file (and that month's subfolder exists), remind the user once per session.

---

## Language & Conventions

ALWAYS use:
- British English (e.g. `learnt` `amidst` `towards` `amongst` `whilst`, but DON'T convert to GBP)
- Metric units (°C, metre, gram, litre, etc.)
- AUD; show original currency in brackets
- Hart's logical quotation rule: punctuation inside quotes only if it was in the original quote (e.g. ✅ `He said "I'm leaving", then left.` ❌ `He said "I'm leaving," then left.`)
- HK Traditional Chinese for any Chinese-language terms

Formatting:
- Timezone: SYD (`Australia/Sydney`); obtain timestamp via `TZ='Australia/Sydney' date +"%Y%m%d%H%M"`
- Date: internal = `YYYYMMDDHHmm`; deliverables = `DD/MM/YYYY`
- "More than" `+`: superscript form (e.g. `10⁺ yr`); regular `+` acceptable for addition and names (e.g. `iCloud+`)
- Em dash: always ` —— ` (doubled, space before and after)
- Emojis: if skin tone modifier is supported → ALWAYS apply light skin tone 🏻, NEVER use default; if not supported (e.g. ⭐, 😊), use as-is
- Use web_search actively for validation whenever needed

---

## Comms Protocol

All responses must be written to a file. Chat text is restricted to the 5 elements below only —— no other chat text unless a Special Command override applies.

### Chat Interface

```
✅ `alias1.md`, `alias2.md`       ← non-/sessions/ file(s) read (event-grouped, comma-separated)
⇠ `202605/query_[TS].md`         ← /sessions/ file(s) read (one line each; enclosing folder/filename only)
➡️ `202605/response_[TS].md`      ← file(s) generated (one line each; enclosing folder/filename only)
⚠️ [brief message]                ← blocking alert: stop & notify (file not found, ambiguity, missing input)
🚨 Post-compaction —— stop.       ← compaction detected: halt everything immediately (see § Post-Compaction)
```

### File Naming

Four file types in `/sessions/`:

| Type | Filename | Created by |
|---|---|---|
| User input | `query_[TS].md` | User (or me on their behalf per 5.3.2) |
| My output | `response_[TS].md` | Me |
| Session summary | `close_[TS].md` | Me (on user prompt; see `universal/close.md`) |
| Monthly summary | `summary_[TS].md` | Me (on user prompt; one per month) |

For CP chats, all 4 types are prefixed: `[CP]_query_[TS].md`, `[CP]_response_[TS].md`, etc.

`[TS]` = timestamp from `TZ='Australia/Sydney' date +"%Y%m%d%H%M"`.

### File Organisation

- All sessions files live in `/sessions/[year]/[yearmonth]/` (e.g. `/sessions/2026/202605/`)
- Create the subfolder if it doesn't exist when first needed in a month
- If a `query_` file is found in a wrong subfolder: confirm with the user before moving (they may be continuing a prior month's chat intentionally)

### Response File Rules

Each `response_[TS].md`:
1. Line 1: `# Response to [query_filename]`
2. Line 2 (optional): `*Title up to 8 words*`
3. Timestamp matches the corresponding `query_` file (not the current time)
4. Placed in the same subfolder as the `query_` file

For messages that are NOT a `query_` file:
- If ≤ 30 words: include the user's message verbatim at the top of the `response_` file
- If > 30 words: create a `query_[TS].md` on the user's behalf (both files share the same timestamp)

### Timestamp Pairing

- Responding to a `query_` file → match its timestamp
- Responding to a direct message → use current SYD timestamp for both `query_` and `response_`

### Long / Non-MD Output

- If generated content is short: include inline in `response_[TS].md`
- If long or non-MD (e.g. HTML, Python): create a separate file; filename determined on the spot; must end with timestamp (e.g. `name_[TS].html`)

---

## Session Memory & Context (Funnel Approach)

Do NOT read past sessions files automatically at session start. Read on demand, judging relevance on the spot. Funnel:

**Current month's files:**
- Read `close_` files of the current month when context is needed
- Skip CP-prefixed `close_` files if not in that CP; skip non-CP `close_` files if currently in a CP

**Past months:**
1. Read that month's `summary_[TS].md` first (lightweight)
2. If insufficient: escalate to individual `close_` files of that month
3. If still insufficient: escalate to individual `query_`/`response_` files of that session

---

## Post-Compaction

When the PostCompact hook fires, a 🚨 prompt appears in the chat.

Upon seeing 🚨:
1. Output `🚨 Post-compaction —— stop.` in chat immediately
2. Halt all tasks and background work without exception
3. Re-read this CLAUDE.md in full
4. Check the compaction summary (or recent `query_` filenames in `/sessions/`) to identify if a CP was active → if so, re-read that CP's `CP_instr.md`
5. Do NOT continue previous work. Await the user's instruction.

---

## Move & Void Rules

**Move Rule:** Copy to target folder → void original (Void Rule) → add suffix `moved_[directory]` to the original filename. NEVER leave identical-filename copies across folders.

**Void Rule:** Add `❌_` prefix to the original filename, signalling the user to manually delete. NEVER delete a file yourself.

---

## Claude Projects (CP) System

A CP is any folder directly under the root (except `/universal/`, `/backup/`, `/temp/`, `/sessions/`, `/seek/`) that contains a file with `CP_instr` in its filename (e.g. `CP_instr_00.md`).

Current CPs (FYI; not exhaustive): `/pro_profile/`, `/dissertation/`, `/mip/`

### CP Identification

A chat is a CP chat when:
- The user's `query_` file has a CP folder name as prefix (e.g. `pro_profile_query_[TS].md`), OR
- The user declares it verbally and I confirm

### CP Chat Rules

Once identified as a CP chat:
1. All my output files use the CP prefix
2. Immediately read the CP's `CP_instr.md` (and any unconditional files it directs) if not already read this session, or if post-compaction
3. `close_` = `[CP]_close_[TS].md`; addendum (if applicable) = separate `[CP]_response_[TS].md`

See `universal/close.md` for the full `close_` and addendum template.

### CP CLAUDE.md

Each CP folder has a `CLAUDE.md` that mandates (at minimum):
1. Read `/dupbus-ceztuc-7cufVe/CLAUDE.md` (this file) for comms protocols
2. Read the CP's `CP_instr.md` (via local path, not GH link)

---

## Conditional File Reads

Read only when conditions are met; declare in chat with ✅. Use the alias as the declared name.

| Alias | Actual File | Read When |
|---|---|---|
| `google.md` | `universal/google_04.md` | Email, calendar, schedule/event topic, OR `#job` mentioned |
| `profile.md` | `universal/profile_06.md` | Personal background of the user needed |
| `cic.md` | `universal/cic_08.md` | A/B/C/WCIC prompt creation, OR browser automation relevant |
| `writing.md` | `universal/writing_06.md` | Deliverables required, OR "casual"/"whatsapp" style mentioned |
| `coding.md` | `universal/coding_05.md` | `#replace` mentioned, OR multi-script coding task |
| `numbered.md` | `universal/numbered_04.md` | `#numbered` mentioned, OR multi-level list needed |
| `plan.md` | `universal/plan_04.md` | No `DevPlan.md` in CP but "dev plan"/"addendum" discussed |
| `shrink.md` | `universal/shrink_01.md` | Shrink/summarise/synthesise/distil/condense requested |

**General trigger:** any `#[name]` in user's message → attempt to read `universal/[name]_*.md`; if not found, alert ⚠️.

---

## File Read Declarations

Each time a non-`/sessions/` file is (re-)read, declare in chat:

```
✅ `alias.md`, `alias2.md`
```

Use the alias if defined above; otherwise use the filename only (no path prefix).

---

## Special Commands

*(User-only unless stated otherwise)*

- `yn` —— respond with one word only in chat: Yes or No
- Single `.` as separator in user prompts: 1 blank line = same-issue break; 3 blank lines = new-issue break
- If user's message is nothing but a single `.`: respond with nothing but `.` only (no file, no declarations)
