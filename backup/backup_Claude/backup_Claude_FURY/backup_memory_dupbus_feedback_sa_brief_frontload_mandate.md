---
name: feedback-sa-brief-frontload-mandate
description: "When delegating research/ops governed by a protocol file (e.g. cic.md), paste the mandate into the SA's prompt instead of just telling it to \"use X\""
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ca8c4e15-a423-480b-b651-d9ef3b206cad
---

When a task is governed by an explicit protocol file (e.g. `universal/cic.md`'s mandate that `#cic` MUST use live Claude-in-Chrome browsing, not `WebSearch`/`WebFetch` alone as confirmation), and that task gets delegated to a sub-agent (SA), don't just instruct the SA to "use CIC" / "use X mechanism" and assume it will locate and correctly apply the underlying rule itself.

**Why:** across several turns in one session, SAs were told to "use CIC" for research but actually only ran `WebSearch`/`WebFetch` and reported results as if CIC-confirmed. The main agent had itself never read `universal/cic.md` this session either (despite `#cic` being explicitly typed by the user, which root `CLAUDE.md` §7.3 makes a hard, unambiguous trigger to read that file first) — so the mandate was being guessed at, not applied, at both the main-agent and SA layer. The fix wasn't a protocol gap (the trigger mechanism was already sound); it was a delegation habit gap: SAs have no memory of this project's conventions, so a bare tool-name instruction gets satisfied however the SA interprets "use CIC" loosely.

**How to apply:** when briefing an SA (or myself) for any task gated by a specific protocol file, quote or paraphrase the file's actual operative mandate directly into the prompt/plan (e.g. "web_search is TRIAGE ONLY, never confirmation — you MUST actually visit live pages via the claude-in-chrome MCP tools before citing anything as confirmed"), rather than relying on a short tool-name reference and trusting the delegate to independently rediscover and honour the underlying rule. This applies generally to any `#[trigger]`-governed op (not just CIC) once delegated downstream.
