# Google Connectors

*`CC:` = for Claude Code only, disregard if you're not.*

## General

I've connected my Google Drive, Mail, and Calendar. If access failed, STOP & alert me.

---

## Google Drive

- Never search in it unless I specifically ask so, since it only supports G docs

---

## Gmail

### Timezone
- Gmail date filters use UTC
- Always fetch current SYD (or wherever I am) timezone offset before any date-based query and adjust boundaries

### Labels (aka "boxes"in user's view)
- Each thread carries a flat `labelIds` array (system + user labels)
- `search_threads`/`get_thread` return label **IDs**, not display names; decode via `list_labels`
- labelId map (actively suggest to update as labels change):
  - `Label_1` = `Unimportant` (Non-actionable; e.g. SEEK Submitted/Viewed/Expired/Rejected)
  - `Label_2` = `Actioning` (in progress)
  - `Label_3` = `Actioned` (done)
- ANY Scan: MUST exclude `Label_1` via `-label:Label_1` in the query
- ALL Claude email-actioning tasks:
  - NEVER archive; thread stays in `INBOX`.
  - On START actioning a thread → add `Label_2`.
  - On COMPLETION → add `Label_3` → remove `Label_2`.
- Thread already on `Label_2` at session start = interrupted → alert user + ask resume or redo.
- Actuation: via `label_thread` / `unlabel_thread`.
- Requires Gmail connector write scope (granted by disconnect/reconnect; CC: "Bypass permissions" mode only needed to DELETE a label, rarely).

### `#job` Prompted
- Non-CC: Fetch & follow job.md (artefact only; no chat text); if unrecognised, reminder user to enter "Career" CP.
- CC: Read `job.md` via `career/CP_index_cc.md`

---

## Google Calendar

- My Google Calendar account has many "calendars" inside, for example (mind the space in names, they're intended):
  - `  🐟` —— my events visible to my wife
  - ` 🐁` —— my wife's events
  - ` 🐟🐁` —— events attended by me and my wife tgt
  - `Deadlines` —— deadlines
  - `Notices` —— not actually events (e.g. Taobao ETA)
  - `General Events` —— originally primary "calendar" but unshared, rarely used, mostly duplicated entries as backup for high-stake events
- Ensure to search through ALL "calendars" when responding to queries related to calendar matters
- When searching through events, prioritise those with locations (likely actual offline attendance)