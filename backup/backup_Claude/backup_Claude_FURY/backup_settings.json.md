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
        "matcher": "Edit|Write|MultiEdit|Read",
        "hooks": [
          {
            "type": "command",
            "command": "python3 '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/plint.py'"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/alint_hook.sh'"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/tlint_hook.sh' pre"
          }
        ]
      },
      {
        "matcher": "Edit|Write|MultiEdit|NotebookEdit|Read",
        "hooks": [
          {
            "type": "command",
            "command": "bash '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/flint_hook.sh' pre"
          }
        ]
      },
      {
        "matcher": "mcp__ccd_session__mark_chapter",
        "hooks": [
          {
            "type": "command",
            "command": "python3 '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/blint.py' marker-pre"
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
            "command": "bash '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/flint_hook.sh' post"
          }
        ]
      },
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/tlint_hook.sh' post"
          }
        ]
      },
      {
        "matcher": "mcp__ccd_session__mark_chapter",
        "hooks": [
          {
            "type": "command",
            "command": "python3 '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/blint.py' marker-post"
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
      },
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/blint.py' prompt"
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
      },
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/mlint.py'"
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/.claude/pre_compact.sh'"
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
    ],
    "PostToolBatch": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/cscpt/blint.py' batch"
          }
        ]
      }
    ]
  }
}
