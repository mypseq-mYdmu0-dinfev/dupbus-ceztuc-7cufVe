{
  "skipWorkflowUsageWarning": true,
  "switchModelsOnFlag": false,
  "agentPushNotifEnabled": true,
  "inputNeededNotifEnabled": true,
  "cleanupPeriodDays": 36500,
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/DADC.py' hook-capture"
          }
        ]
      },
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/plint.py'"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/DADC.py' hook-restore"
          }
        ]
      },
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/dlint_hook.sh'"
          }
        ]
      },
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/nlint_hook.sh'"
          }
        ]
      },
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/tlint_hook.sh'"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/hlint.py'"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/clint.py'"
          }
        ]
      }
    ],
    "PostCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/.claude/post_compact.sh'"
          }
        ]
      }
    ]
  }
}
