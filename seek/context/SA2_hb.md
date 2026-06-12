# SA2 Watchdog Contract (`SA2_hb.md`)

*The independent timekeeper that catches MA or SA1 stalling. MA reads this at Session Start to spawn it. SA2 is a deterministic bash `Monitor` —— NOT an LLM, so it cannot stall or compact, and it reads no other file. This file is the entire spec.*

## Context it guards
- MA orchestrates; SA1 applies to jobs one at a time. MA re-reads `MA_hb.md` and checks SA1 on every heartbeat. If MA freezes (e.g. compaction) or SA1 stalls/idles, heartbeats stop —— SA2 is the backstop that re-wakes MA.

## Three tasks (every 900s = 15 min)
1. MA-stall: `ma_hb_reread_marker` older than 6 min (MA has not re-read `MA_hb.md`) → alert MA to recover.
2. SA1-stall: `ma_c2_marker` older than 14 min (no `🎯[N]` —— SA1 idle/stuck, or MA missed a declaration) → alert MA to check SA1. SA1 averages ~326s/job, so 14 min is very lenient; an alert is a PROMPT to investigate, never an auto-retire.
3. Full-reread-stall (SILENT-COMPACTION backstop): `ma_full_reread_marker` older than 75 min → MA has not re-read ALL mandatory files in over 75 min. The PostCompact hook is NOT 100% reliable, and a silent compaction is INVISIBLE to check 1 (MA keeps re-reading `MA_hb.md`, so `ma_hb_reread_marker` stays fresh and hides the loss). This filesystem-timestamp check is the hook-independent signal that MA may have lost full context → alert MA to do a full mandatory re-read.

## How it wakes MA (two paths)
- WRITES the alert to `/seek/.claude/tmp/sa2_alert.md` (MA's primary Monitor also file-watches that path → the write wakes MA) AND echoes the same line (a Monitor stdout line is itself a direct wake, independent of the primary). Either path re-wakes MA even if the primary Monitor died.

## Canonical command —— spawn ONCE at Session Start (`persistent=true`; full `/seek/...` paths when issuing)
```
HB=/seek/.claude/tmp/ma_hb_reread_marker; C2=/seek/.claude/tmp/ma_c2_marker; FR=/seek/.claude/tmp/ma_full_reread_marker; A=/seek/.claude/tmp/sa2_alert.md
while true; do
  sleep 900
  msg=""
  if find "$HB" -mmin +6 2>/dev/null | grep -q .; then msg="WATCHDOG-MA-STALL"; fi
  if find "$C2" -mmin +14 2>/dev/null | grep -q .; then msg="$msg WATCHDOG-SA1-STALL"; fi
  if find "$FR" -mmin +75 2>/dev/null | grep -q .; then msg="$msg WATCHDOG-FULLREAD-STALL"; fi
  if [ -n "$msg" ]; then printf '%s %s\n' "$(date +%H%M)" "$msg" > "$A"; echo "$msg"; else echo "watchdog-alive"; fi
done
```

## MA reactions
- `WATCHDOG-MA-STALL` → re-read `MA_hb.md`; rebuild the primary Monitor; stamp markers.
- `WATCHDOG-FULLREAD-STALL` → treat as a POSSIBLE SILENT compaction: run the full `main_ajap.md § MA Post-Compaction Recovery` (re-read ALL 9 mandatory files + emit `✅` for each), then `touch /seek/.claude/tmp/ma_full_reread_marker` as the final step. Do this even if your context "looks" intact —— a compaction summary can mask the loss; the stale marker is the objective signal.
- `WATCHDOG-SA1-STALL` → actively check SA1 (stuck `⏳_`, no new AR, or idle); act per `main_ajap.md`; if SA1 is legitimately busy, just re-stamp.
- `watchdog-alive` → normal heartbeat wake.

## Lifecycle (resolves the SA2-compaction loophole)
- Being bash, SA2 NEVER compacts/degrades —— so no 5-hour retire and no periodic respawn are needed.
- Spawned ONCE; recorded as `watchdog_task` in `ma_state.md`; NEVER TaskStop'd by dynamic-interval churn.
- On MA post-compaction recovery only: `TaskStop` the stored `watchdog_task` (kills any survivor —— `TaskList` does NOT list Monitors, so always TaskStop by the stored id), then respawn fresh and update the id. This guarantees exactly one watchdog, no clutter.
