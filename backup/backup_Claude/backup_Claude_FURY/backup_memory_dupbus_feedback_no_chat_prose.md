---
name: feedback-no-chat-prose
description: Chat carries ONLY the six declaration glyphs — never prose; the user does not read it
metadata: 
  node_type: memory
  type: feedback
  originSessionId: eaccd7dc-a983-47bb-ba8e-f38a6912015d
  modified: 2026-08-06T18:14:44.233Z
---

# NO CHAT PROSE — strict comms discipline

**Severity: high. The user does NOT read chat prose and is troubled by any of it.**

Root CLAUDE.md §3.1–§3.2 already mandates this; reinforced here because chat-text drift has recurred.

## The rule
In chat, output ONLY the SIX declaration types of §3.2.1–§3.2.6:
- `✅` reads (non-comms; grouped on ONE line)
- `⇠` comms files read (one line EACH)
- `➡️` files generated (one line EACH — never grouped)
- `🦈` this turn's commit SHAs (8 chars; grouped on ONE line, or one line per repo)
- `⚠️ [≤5w]` blocker
- `🚨` compaction sentinel

No preamble, no narration, no "Note:", no explanation before/after tool calls, no summary. Everything substantive goes in the `response_` file. Only `override` (see `glossary.md`) lifts this for one turn.

## Why (the user's rationale)
Comms are designed as a minimal-height index, like Mail's list/preview panes: `query_` files are pre-drafted off-UI; `response_`/generated files open in the File side-panel when clicked — NOT in the chat. Keeping the chat to terse declarations lets the user scroll back and locate any past query/response fast. Chat prose bloats vertical space and defeats this.

## Self-check before sending any chat turn
Does every line start with ✅ / ⇠ / ➡️ / 🦈 / ⚠️ / 🚨 ? If not, move it into the response file.

**Verify the count before quoting it.** This file said "five" for two months after `🦈` was added; the set is defined by root CLAUDE.md §3.2, which is authoritative. Related: [[feedback-spaced-filenames]].
