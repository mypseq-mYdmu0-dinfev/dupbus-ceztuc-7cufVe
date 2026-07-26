---
name: ajap-no-permission-prompts
description: "Never run anything that can surface an OS/tool permission dialog during AJAP #seek/#eng sessions"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fb5baf48-2148-4104-9f7d-069110756178
  modified: 2026-07-19T11:07:15.648Z
---

During AJAP `#seek`/`#eng` cockpit sessions, never take an action that can trigger an OS-level or tool-level permission dialog (e.g. `screencapture`, or any macOS TCC-gated command) — even for legitimate live debugging.

**Why:** 2026-07-19/20 live incident — while diagnosing a false weekly-quota stop, ran `screencapture`-backed OCR calls directly via Bash to inspect AJAP's usage panel. This almost certainly fired macOS's Screen Recording permission prompt mid-run. The user saw multiple permission requests, rejected them, and explicitly stated: "you can't do anything that will prompt permission request in a #seek session" / "Those are considered bugs." This is the same underlying guarantee as [[ajap-no-blocking-questions]] (never summon the user) — extended from chat-level interruptions to ANY interruption surface, regardless of source (macOS TCC vs. Claude Code's own permission gate).

**How to apply:** In any AJAP cockpit session (`#seek`, `#eng`, `#psl`/`#ccl` + `#eng`), diagnose from existing artifacts only — `rlog_*.md`, `progress.log`, `status.jsonl`, `usage.jsonl`, git diffs, code reading. If a live read genuinely requires a permission-gated action (screen capture, camera/mic, accessibility automation, etc.), say so in chat and ask the user to run it themselves — never attempt it. This is now codified in `AJAP_repo/dir/CLAUDE.md` § Rules (added 202607200730) as a COORDINATOR-level rule, not `#eng`-only.
