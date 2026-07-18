# CCSIM CP —— Notes

*Working notes for the CC System Improvement & Maintenance CP. Operating rules live in `cp/ccsim/CLAUDE.md`; this file holds standing context + decisions.*

## Purpose
- Improve CC's own pcmds/scripts/protocols —— the meta-layer that keeps the wider system sharp.

## Key Files
- `CLAUDE.md` —— operating protocol (hunt, recent-index, backlog, QA, sandbox, #wrap).
- `backlog.md` —— append-only issue log.
- `last_seen.md` —— per-turn change-hunt anchor (`[TS] [SHA]`).
- `sandbox/` —— CC's directly-deletable scratch folder.

## Standing Decisions
- CCSIM comms carry the `ccsim_` prefix (`ccsim_query_`, `ccsim_response_`, `ccsim_close_`); `wrap_` stays unprefixed.
- Reading a prior `ccsim_close_` in full is discretionary, surfaced via the recent-5 index.
