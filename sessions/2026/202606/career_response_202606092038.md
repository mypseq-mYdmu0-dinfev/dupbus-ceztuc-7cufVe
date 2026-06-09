# Response to career_query_202606092038.md
*CC-Actioned label workflow — feasibility + 1 blocker*

5. Yes — I can see each email's "box". Every `search_threads`/`get_thread` result carries `labelIds`. Your examples map cleanly:
- 5.1. Important → `IMPORTANT`; Inbox → `INBOX`; Unimportant → `Label_1` (confirmed: it's your **only** user label right now, via `list_labels`).
- 5.2. Also visible: `STARRED`, `UNREAD`, `SENT`, etc. So reading box + star state is fully supported, no blocker there.

6. On the concept — I agree with the design and the semantics. "In box + starred = being actioned (NOT done); in box + unstarred = actioned" is clean, and it doubles as **crash recovery**: a future session that finds a *starred* CC-Actioned mail knows the prior action was interrupted and can resume/redo it. Worth keeping that recovery meaning explicit in the protocol. So yes — recommend creating the box.

7. Blocker — **B1 (tooling gap, changes the plan):**
- 7.1. The connected Gmail connector exposes only: read (`search_threads`, `get_thread`) + label-**definition** mgmt (`create_label`, `update_label`, `delete_label`, `list_labels`).
- 7.2. It has **no** tool to apply/remove a label on a message/thread, nor to star/unstar one. (`list_labels`'s own docs name `label_thread`/`label_message` etc., but those tools are **not** connected in this session — verified.)
- 7.3. Consequence: I cannot run "star + move to CC-Actioned … then unstar" through the data connector. The only actuation path is **CIC** (Gmail web UI, clicking) — per-email, slower, needs Chrome connected. So this can't be a silent background step; it runs via CIC at the **start** (star + label) and **end** (unstar, optionally archive) of acting on each email.
- 7.4. This is why I'm **not** editing files yet — the actuation method materially shapes the protocol wording.

8. Decisions needed before I edit anything (QB):
- Q1. **Actuation** — OK to do this via CIC clicks in Gmail web? (If you later connect a label-a-message tool, I'll auto-switch to it — faster, no browser.)
- Q2. **"Move" semantics** — Gmail labels are additive, not folders; a literal "move" = add label **and** remove `INBOX` (archive). Pick one:
  - 8.1. (recommended) On **start**: add `CC-Actioned` + `STARRED`, keep in Inbox. On **finish**: unstar **and** remove `INBOX` (archive) → mail lands solely under CC-Actioned, Inbox stays clean, in-progress items stay visible in Inbox.
  - 8.2. (literal) Archive immediately on start (Inbox cleared at once; in-progress items only findable via the label/star).
- Q3. **Where the rule lives** — since it's ALL tasks (not just `#job`), canonical spec → `universal/google.md` (Gmail section); plus a 1-line pointer in `career/CP_notes.md` § Job Processing (step 0). Confirm if you also want a pointer in root `CLAUDE.md`. No new file needed.

9. Draft spec (drops into `google.md` once Q1–Q3 set; shown so you can vet wording):
```
## Gmail — CC-Actioned protocol (ALL tasks)
- Before performing ANY action triggered by/affecting an email (any task, e.g. #job link-open, reply draft):
  1. Via CIC: add label `CC-Actioned` + `STARRED` to that thread FIRST (before any other action).
  2. Then perform the action(s).
  3. On full completion: remove `STARRED` [and remove `INBOX`/archive per Q2]; thread now formally CC-Actioned.
- State semantics: CC-Actioned + starred = mid-action / interrupted (resume or redo); CC-Actioned + unstarred = done.
- Never unstar before the action is fully finished.
```

10. On approval I will, in order: 10.1 create the `CC-Actioned` label (top-level) via connector; 10.2 edit `google.md` + `CP_notes.md` per Q3; 10.3 declare changes. I won't touch existing filenames (your GH-trace requirement preserved).
