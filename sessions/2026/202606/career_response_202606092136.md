# Response to career_query_202606092136.md
*Label tools to enable + connector audit — answers, no actions*

20. Re § 12.2 — yes, and good catch:
- 20.1. The 30-day `#job` scan **did** pull many `Label_1` (Unimportant) threads into the search results — most of the SEEK "unlikely to progress" / "closed" / "submitted" notices carried `["UNREAD","Label_1"]`. They came back as snippets in `search_threads`, so they **did** consume a sizeable slice of tokens (I only fully opened 2 threads, but the list itself was long).
- 20.2. Agree to **mandate skipping `Label_1`** in the scan: add `-label:Label_1` to the query. Material token saving. Minor tradeoff: we'd also stop surfacing the "brief rejection" mentions — fine, since you've defined `Label_1` as precisely the non-actionable set. I'll encode this in google.md.
- 20.3. Re § 12.3 — agreed: the `labelId` map + the skip rule live in **google.md** (so CWI/OTGC also decode `Label_N` and skip to save tokens), not the new files.

21. Re § 14 — confirmed: the connector **ships** the label-write tools; you'd simply toggled them off. From the screenshot's "Write/delete tools", here's what to change (read-only tools already Always-allow, not shown):
- 21.1. **Enable → "Always allow"** (the routine actuators; reversible, non-destructive, needed for a hands-off flow):
  - 21.1.1. **Adds labels to a message** (and "Adds labels to a thread" if listed — enable both)
  - 21.1.2. **Removes labels from a message**
  - 21.1.3. **Removes labels from a thread**
- 21.2. **Enable → "Needs approval"** (used rarely / one-off):
  - 21.2.1. **Creates a new label** — needed once, to make `CC-actioning` + `CC-actioned` (you may already have this on; I currently hold it in-session).
- 21.3. **Keep OFF / "Needs approval"** (consequential or unused by us):
  - 21.3.1. **Deletes a label** — consequential (wipes a label off all its mail); keep off or Needs approval.
  - 21.3.2. **Modifies an existing label** — rare; Needs approval if on.
  - 21.3.3. **Creates a draft email**, **Lists draft emails** — not used (I draft into the AR, not Gmail); leave off.
- 21.4. Rationale: only 21.1 must be frictionless, else the "fully by me, you only approve once" goal breaks (each call would prompt). They're all reversible (re-add/remove), so Always-allow is safe.

22. Re § 15:
- 22.1. 15.1 — resolved by § 14: the exact UI labels are "Adds labels to a message/thread" & "Removes labels from a message/thread" (connector's wording for what I earlier called `label_thread`/`label_message`). Enable per § 21.
- 22.2. 15.5 — **yes, and this is the clean win:** once § 21.1 is on, I write the `CC-actioning`/`CC-actioned` label **directly server-side** via the connector. Gmail labels are IMAP folders, so they sync to Apple Mail on **both Mac and iPhone** — **no smart mailbox needed**, solving the Mac-only limitation. (On iOS Mail you may need Mailboxes → Edit to tick the `CC-actioning`/`CC-actioned` folders so they show.) So: I label it right, it appears as a mailbox on all your devices.

23. Side question — connector audit (honest read; I can introspect the Chrome ones because their tools are exposed to me, but **pdf-viewer** and **Word** are not loaded in this session, so those two are reasoned, not verified — flagging per accuracy rule):
- 23.1. **Claude in Chrome vs Control Chrome:**
  - 23.1.1. **Claude in Chrome** (marked INCLUDED) — Anthropic's first-party browser control: DOM-aware navigate/click/fill, read page text, console + network inspection, tab management, file upload. This is the robust one I'd use for CIC tasks (e.g. opening job posts, pre-filling forms).
  - 23.1.2. **Control Chrome** — a thinner third-party set (open URL, list/switch/close tabs, run JS, get page content, back/forward/reload). It **overlaps and is weaker**. **Recommend removing it** — redundant with Claude in Chrome, and fewer third-party surfaces is cleaner/safer.
- 23.2. **pdf-viewer** — I already read your local PDFs natively (Read renders pages) and have the `pdf` skill for merge/split/extract/OCR. The connector is **largely redundant for our workflows**; its plausible extra is interactive viewing/preview, which I don't need. **Removable** unless you personally use its viewer. (Unverified — tools not loaded here.)
- 23.3. **Word (By Anthropic)** — I already create/read/edit `.docx` via the `docx` skill (incl. tracked changes, find-replace, ToC). The connector likely adds live Word-app/cloud integration; for local `.docx` deliverables the skill **already covers it**, so it's **mostly redundant**. Keep only if you want me driving the Word app itself. (Unverified.)
- 23.4. **Remove / add verdict:**
  - 23.4.1. **Remove:** Control Chrome (definite). pdf-viewer + Word (By Anthropic) — optional removals if you don't use their apps interactively.
  - 23.4.2. **Keep:** Gmail, Google Calendar, Google Drive, Claude in Chrome, Filesystem, PowerPoint, Read & Write Apple Notes — all map to things you actually ask me for.
  - 23.4.3. **Add:** nothing essential is missing for your job-search + deliverables + calendar workflows. The one real gap was the Gmail label-write tools — fixed by § 21, not a new connector. (If you ever want me posting/reading LinkedIn or tracking apps in a sheet, we can revisit, but I'd not add speculatively.)

24. Re § 17 — adopting your revised structure (all in `career/`, nothing in `universal/`):
- 24.1. **`career/job.md`** (OTG-readable) — the `#job` Gmail-scan spec; prerequisite **google.md**. **`career/jop.md`** (CC-exclusive) — the `#jop` processing spec; prerequisite **job.md**.
- 24.2. **Index both** in `career/CP_index_cc.md` **and** `career/CP_index_otg.md` — but list `jop.md` **only** in the `_cc` index (CC-exclusive); `job.md` in both.
- 24.3. **Trigger wiring (the bit that needs care):** because these are career-scoped, `#job`/`#jop` must **not** rely on the root §7.3.1 general trigger (which would look in `universal/` and ⚠️-fail). So: `#job` → identify career CP → read career Unconditionals → google.md → `career/job.md`; for processing, locate `jop.md` **via `career/CP_index_cc.md`** (not a hardcoded path, per your "could change" note). I'll wire this routing into the CP index/notes so it resolves in-CP and guarantees career Unconditionals load first (your stated goal).
- 24.4. Prerequisite chain recorded as you specified: `job.md` → needs `google.md`; `jop.md` → needs `job.md`; labels themselves defined in google.md so they're "widely understood"; `CC:`-only detail points to `jop.md` **via the index**.
- 24.5. google.md ends up: lean Gmail/calendar + `labelId` map + `Label_1` skip rule + the `CC-actioning`/`CC-actioned` label definitions & state semantics + a pointer line to `career/job.md`. The bulky scan/processing logic leaves it.

25. Go/no-go — I've **not** created labels or edited files (you've yet to toggle § 21, and you've twice flagged premature action). When you confirm the tools are enabled (and Always-allow per § 21.1), say the word and I'll execute in one pass: 25.1 create the two labels; 25.2 build `career/job.md` + `career/jop.md`; 25.3 update both `career/` indexes; 25.4 trim google.md (labelId map + skip rule + label protocol + pointer); 25.5 declare every diff for your GH review. Just confirm, and whether you want the optional connector removals (§ 23.4.1) done by you in the UI (I can't touch connector settings).
