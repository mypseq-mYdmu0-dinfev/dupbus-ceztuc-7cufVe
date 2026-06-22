session_start_TS: 202606202330
latest_TS: 202606221342

heartbeat_task: bjwvrypv4  [INT=60]
heartbeat_interval: 60s

watchdog_task: bge4jeltn

sa_spawn_TS: 202606221432

# STANDING OVERRIDE (survives compaction — apply on every SA spawn)
# ajap.md S6.4.2.5 default wait = 20 × 15s = 900s; override below
sa_msg_wait_override: 60 checks × 15s = 900s (15 min) — replace "up to 20 times (300s total)" with "up to 60 times (900s total)" in SA spawn prompt

sa_id: a6bcfefdea94cf5cd
