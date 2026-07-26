---
name: declare-mahb-reread
description: "After every MA_hb.md re-read (heartbeat or 5-loop trigger), must emit ✅ declaration in chat"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b15cb438-50e1-4f1a-a6c1-6c666c26cf80
---

Always emit `✅ \`context/MA_hb.md\`` in chat after each literal re-read of MA_hb.md — whether triggered by heartbeat, watchdog wake, or every-5-loops rule.

**Why:** User correction — declarations are mandatory for every file read per CLAUDE.md §3.2.1; MA_hb.md re-reads were happening without the accompanying ✅ declaration.

**How to apply:** Immediately after the Read tool call for MA_hb.md completes, output `✅ \`context/MA_hb.md\`` as part of the chat response — no exceptions, same as any other file read. See also [[heartbeat-reread-mahb]].
