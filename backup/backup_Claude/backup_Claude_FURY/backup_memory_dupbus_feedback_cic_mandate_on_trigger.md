---
name: feedback-cic-mandate-on-trigger
description: "When user prompts #cic, MUST actually read universal/cic.md and perform live CIC reads — WebSearch/WebFetch/SA-only research is triage, not compliance"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7c59bb12-8403-4864-af5e-c588944f7db6
  modified: 2026-08-04T07:50:59.126Z
---

When `#cic` appears in a user msg (or the task is high-stake validation), `universal/cic.md` MUST be read that turn, and its mandate followed: validate via **live** Claude-in-Chrome page reads (CCIC), not `web_search`/`WebFetch`/SA-only research alone.

**Why:** Flagged as a "major violation" after a turn where SAs were dispatched with instructions to "actively #cic" but actually only used `WebSearch`/`WebFetch` — per `universal/cic.md`, those are TRIAGE ONLY and never substitute for a live CIC read; nothing they surface may be relied on for a claim until CIC has confirmed it live. The hashtag-trigger hook reminder fired but was not acted on.

**How to apply:**
- Any msg containing `#cic` → read `universal/cic.md` (if not already read this session) before dispatching research, even if the request is phrased as "have SAs #cic it" for a Workflow/SA task.
- `web_search`/`WebFetch` may surface & narrow candidates first, but the actual validation step must be a live page read — either MA doing it directly (load `mcp__claude-in-chrome__*` via ToolSearch) or an SA explicitly instructed & confirmed to use those same live-read tools (not generic web-search-capable agents).
- If CIC genuinely can't be used (Chrome unavailable etc.), the protocol says stop & alert — no silent fallback to web_search-only.
- See [[project_dupbus_ceztuc_protocol]] for the wider Absolute Protocols this session runs under.
