# Hook Liveness Probe

*Scratch fixture. Deliberately contains dlint RED triggers. Not a comms file —— the `response_` in the filename is REQUIRED: `cscpt/dlint_hook.sh` only spawns Python when the hook payload mentions `response_`, so a probe without it would prove nothing.*

## What it is for

Editing this file with the Write/Edit tool is a one-step test of whether PostToolUse hooks are actually being executed by the harness:

- Hooks LIVE → the write is blocked immediately with a dlint RED report (5 Americanisms on the probe line below).
- Hooks DEAD → the write succeeds silently.

This distinguishes "the script is broken" from "the harness never invoked the script" —— a distinction that cost a whole session's confusion once, because every lint script passed when piped a payload by hand whilst none of them had ever actually run live.

To check the script chain independently of the harness, pipe a payload in manually:

```bash
cd "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
printf '%s' '{"tool_name":"Write","tool_input":{"file_path":"cp/ccsim/sandbox/hook_probe_response_.md"}}' | bash cscpt/dlint_hook.sh; echo "exit=$?"
```

Exit 2 + a RED report = the chain works. If a live Write of this same file is NOT blocked, the harness is not running hooks.

## Probe line —— do not "fix" these spellings

I organized the color of my favorite center while analyzing the behavior.
