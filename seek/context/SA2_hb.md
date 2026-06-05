# SA2 Watchdog Contract (`SA2_hb.md`)

*Independent timekeeper watchdog —— SEPARATE from MA's primary heartbeat. Read by MA at Session Start (mandatory file #9) to spawn/maintain the watchdog, and consulted when reacting to a watchdog wake. The "timekeeper-SA" long-planned in prior investigations.*

---

## What it is

- A SECOND, independent, persistent `Monitor` (deterministic bash —— NOT an LLM agent, for maximum robustness; an LLM watchdog could itself stall/compact).
- Spawned ONCE at Session Start. NEVER `TaskStop`'d during dynamic-interval churn (unlike the primary Monitor, which churns 60/300). Re-confirmed/respawned only during post-compaction recovery if its liveness cannot be assumed.
- Cadence 900s (15 min). It is the GUARANTEED independent MA wake: even if the primary Monitor is lost to churn or compaction, the watchdog keeps waking MA.
- Liveness fact: `TaskList` does NOT enumerate background Monitors —— so the watchdog (not TaskList) is the heartbeat liveness mechanism.

## Measurement surface (MA must stamp; reading a file leaves no trace)

- `ma_hb_reread_marker` —— MA `touch`es it at the TOP of every wake when it re-reads `MA_hb.md`.
- `ma_c2_marker` —— MA `touch`es it on every `🎯[N]` (C2) emission.
- Both are seeded (touched) at Session Start so early cycles do not false-trip.

## Canonical watchdog Monitor command

Spawn at Session Start with `persistent=true`. (Use the full absolute `/seek/...` paths when issuing; `/seek/` shown for brevity.)

```
HB=/seek/.claude/tmp/ma_hb_reread_marker
C2=/seek/.claude/tmp/ma_c2_marker
while true; do
  sleep 900
  if [ -e "$HB" ] && find "$HB" -mmin +6 | grep -q .; then echo "WATCHDOG-MA-STALL"; fi
  if [ -e "$C2" ] && find "$C2" -mmin +14 | grep -q .; then echo "WATCHDOG-SA1-STALL"; fi
  echo "watchdog-alive"
done
```

- Thresholds: MA-stall = `MA_hb.md` not re-read in `>6 min` (6 not 5 —— avoids tripping whilst MA is mid-reread). SA1-stall = no `🎯[N]` in `>14 min` (SA1 averages ~326s/job, so 14 min ≫ one loop —— very lenient; a slow research/external-portal job can legitimately approach this, so a trip is a PROMPT TO INVESTIGATE, never an auto-retire).
- Quiet by design: it only emits the two STALL lines on a trip, plus a sparse `watchdog-alive` tick —— low event volume (avoids the Monitor auto-stop-on-too-many-events limit).

## MA reactions (on each watchdog wake)

- `WATCHDOG-MA-STALL` → MA re-reads `MA_hb.md`, rebuilds/repairs the PRIMARY Monitor (it likely died or was orphaned), stamps `ma_hb_reread_marker`. Log the repair (rlog DO-list).
- `WATCHDOG-SA1-STALL` → MA investigates SA1: run the broad file check; is a `⏳_` AR stuck awaiting approval? has no new AR appeared? is SA idle (20×15s exhausted)? Act accordingly (write `ma_msg.md` / respawn SA). If SA1 is legitimately busy (active `⏳_`, tab live), take no action and re-stamp. If MA simply missed a `🎯[N]`, emit it now. Log only a genuine stall/retire (not a benign busy check).
- `watchdog-alive` (no trip) → treat as a normal heartbeat wake (re-read `MA_hb.md`, broad check, stamp). This is the redundant 15-min MA wake; if the primary Monitor is dead, MA rebuilds it here.

## Spawn / recovery rules

- Session Start: seed both markers; spawn the watchdog; record `watchdog_task: [id]` in `ma_state.md`.
- Dynamic-interval churn touches the PRIMARY Monitor only —— NEVER the watchdog.
- Post-compaction recovery: re-confirm/respawn BOTH the primary Monitor and the watchdog (the primary is the most fragile; the watchdog is the safety net that woke MA in the first place).

## Design note (convertibility)

- Implemented as a deterministic Monitor for robustness. To convert to a true LLM SA2 later: spawn a background agent (`run_in_background=True`) whose sole loop is "read `SA2_hb.md`, perform the two marker checks, write any finding to `ma_msg.md`", driven by its own `sleep 900` Monitor. The file structure is unchanged; the Monitor form is preferred unless a reasoning-based watchdog is explicitly wanted.
