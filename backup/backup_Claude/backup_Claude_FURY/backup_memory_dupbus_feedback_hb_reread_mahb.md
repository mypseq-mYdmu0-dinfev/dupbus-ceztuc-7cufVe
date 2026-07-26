---
name: feedback_hb_reread_mahb
description: "On every heartbeat/Monitor wake in AJAP mode, MA_hb.md must be literally re-read (Read tool), not run from memory"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b15cb438-50e1-4f1a-a6c1-6c666c26cf80
---

On every heartbeat/Monitor wake AND every 5 loops, MA must literally re-read `MA_hb.md` using the Read tool — not from memory. The file itself states this requirement explicitly. Skipping the actual file read and running the checklist from context memory is a protocol violation.

**Why:** The user explicitly corrected this. The MA_hb.md contract says "Re-read this file on every heartbeat... no exceptions, no skipping" — "re-read" means the Read tool, not recall.

**How to apply:** At the top of every heartbeat handler, after `touch ma_hb_reread_marker`, immediately call `Read` on `/seek/context/MA_hb.md` before doing anything else. Declare it per C1. Then run the Active Check.
