# QQ —— Queued Query Drafting

## Basics
If not already, read `sessions/queued_queries/README.md` to know what it is

## Task
- Draft a `queued_queries/*_query_[current_TS].md` for the concerned issue(s)
- If no recipient indicated, judge:
  - If related to harness (e.g. pcmd, hook, skill), assume CCSIM (per glossary.md)
  - Else, assume a fresh CC
- Filename prefix = [CP_folder] (if applicable) + [optional_≤10char_descr]
  - e.g. an issue about #m2 trigger (CCSIM-owned): `ccsim_m2_trigger_query_[current_TS].md`
  - e.g. an issue about car fixing (fresh ses): `car_fix_query_[current_TS].md`
- Optional: suggest `#MA` `#SA` `##SA` etc. in-line
- Mandatory: last line = remind recipient to rename+move per `queued_queries/README.md`

## Examples
User may prompt: "#qq on this issue", "#qq on the m2 matter", "#qq the car fix in clean ses"