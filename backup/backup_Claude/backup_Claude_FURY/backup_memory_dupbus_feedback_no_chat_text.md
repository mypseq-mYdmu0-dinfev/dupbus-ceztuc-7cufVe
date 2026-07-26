# NO CHAT TEXT — strict comms discipline

**Severity: high. The user does NOT read chat prose and is troubled by any of it.**

Root CLAUDE.md §3.1–§3.2 already mandates this; reinforce here because chat-text drift has recurred.

## The rule
In chat, output ONLY the five declaration types of §3.2.1–§3.2.5:
- `✅` reads (non-comms; grouped on ONE line)
- `⇠` comms files read (one line EACH)
- `➡️` files generated (one line EACH — never grouped)
- `⚠️ [≤5w]` blocker
- `🚨` compaction sentinel

No preamble, no narration, no "Note:", no explanation before/after tool calls, no summary. Everything substantive goes in the `response_` file. Only `override` (§9.1) lifts this for one turn.

## Why (the user's rationale)
Comms are designed as a minimal-height index, like Mail's list/preview panes: `query_` files are pre-drafted off-UI; `response_`/generated files open in the File side-panel when clicked — NOT in the chat. Keeping the chat to terse declarations lets the user scroll back and locate any past query/response fast. Chat prose bloats vertical space and defeats this.

## Self-check before sending any chat turn
Does every line start with ✅ / ⇠ / ➡️ / ⚠️ / 🚨 ? If not, move it into the response file.
