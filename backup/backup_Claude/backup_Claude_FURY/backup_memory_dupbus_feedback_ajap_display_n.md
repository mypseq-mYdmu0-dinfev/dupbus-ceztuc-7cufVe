---
name: feedback-ajap-display-n
description: "AJAP MA C2 output — display_N equals session_N only, not offset_N + session_N"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5ab0f162-2f49-49a1-a38f-c337c74ff654
---

display_N = session_N (session-local count only); ignore offset_N for C2 display.

**Why:** User corrected this explicitly — cumulative count (offset_N + session_N) is not what the C2 output should show; only the current session's processed count matters for the user-facing 🎯 tally.

**How to apply:** In `main_ajap.md § Between-Loop Audit`, when computing C2: use `display_N = session_N` (not `offset_N + session_N`). offset_N is still tracked internally for session log purposes but never shown in C2.
