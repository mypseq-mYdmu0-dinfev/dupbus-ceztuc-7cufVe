# Response to career_query_202606092214.md
*Label-tool reconnect needed + connector verdicts*

26. Re § 20.2/3 — **done now.** Edited `universal/google.md` → added a "Labels (aka boxes)" block under Gmail: (a) Gmail = labels not folders, `search`/`get` return label **IDs** (decode via `list_labels`); (b) ID map `Label_1 = Unimportant`; (c) **mandate**: any `#job`/`#jop` scan must add `-label:Label_1` to skip non-actionable mail. Future `#job` runs will no longer burn tokens on those.

27. Re § 21.1/2 ("check if true") — **not effective yet; two-layer blocker found:**
- 27.1. The apply/remove-label tools (`label_thread` / `label_message` / `unlabel_*`) are **still not exposed to my session**. Newly-enabled connector tools only load at **session start** — so I won't see them until the CC session is restarted/reloaded.
- 27.2. Worse, even `update_label` (which I *did* have) now errors: **"This connector requires additional permissions. The user needs to reconnect it with the appropriate access."** → Toggling the write tools on **added new OAuth scopes that aren't granted until you RECONNECT (re-authenticate) the Gmail connector.** Flipping visibility ≠ granting the scope.
- 27.3. So two actions on your side, in order: **(a) reconnect/re-authenticate Gmail** (to grant the write/label scope), **(b) restart this CC session** (so the new tools load). After both, I can create + apply labels.

28. Re § 21.3.2 (modify `Label_1` → "Unimportant") — couldn't complete (blocked by 27.2, which is itself the proof reconnection is needed). Two corrections regardless:
- 28.1. `Label_1`'s display name is **already** "Unimportant" (confirmed via `list_labels`), so that rename is a no-op.
- 28.2. More important: renaming the display name **wouldn't** let me drop the google.md map — because `search`/`get` always return the **ID** `Label_1`, never the name. Self-explanatory names help *you* in the UI, not *my* machine view. Hence I kept the ID map in google.md (§ 26). Net: the explainer stays necessary.

29. Re § 22 (create 2 labels + verify) — **deferred** until 27.3 is done (I can create labels but can't *apply* them to verify, so doing half now would leave untested labels). Once reconnected + restarted, in one pass I'll: create `CC-actioning` + `CC-actioned`; take one `Label_1` email into each (add new label **and** remove `Label_1` = a true move, never archived); verify via `search label:CC-actioning` etc.; then report the 2 thread subjects so you can dump them back to `Unimportant`.

30. Re § 23 — connector verdicts (tested live; Control Chrome already removed by you ✅):
- 30.1. **Word (By Anthropic)** — **works in CC.** `open_document` + `get_document_text` returned the full text of a real `.docx`. Caveats: it flattens structure (hyperlinks concatenated into the text, no headings/styles) and is single-"active-document" at a time. Overlap: the built-in **`docx` skill** (python-docx) already does read **and** structured create/edit/format/track-changes/find-replace — richer. Verdict: **redundant for producing deliverables; keep only if you want quick app-level open/read.** Lean = remove.
- 30.2. **pdf-viewer** — **little value in CC, recommend remove:**
  - 30.2.1. Sandboxed to the working-dir roots only — it **rejected** `/Volumes/FURY 2TB/Fury Downloads/…` ("not in allowed list"). Your files mostly live outside the repo, so it can't reach them; I had to copy one in to test.
  - 30.2.2. Its viewer needs the **visual app iframe** to mount; in headless CC it "never connected" and `get_text` failed. So it can't even extract text here.
  - 30.2.3. Native **Read** already renders any PDF I can reach (just read your Downloads PDF perfectly — text, layout, even the 中文), from anywhere, no sandbox.
  - 30.2.4. pdf-viewer's genuine strength = interactive annotate / stamp / **sign** / fill-form **in the visual app** (CWI/CAI) — not CC. Keep it **only** if you do that in the desktop/web app.
- 30.3. **Disadvantages of keeping either (your "alert" request):** (a) their schemas consume context when loaded; (b) a future session may pick the weaker path — pdf-viewer over Read, or the Word connector over the `docx` skill — then hit pdf-viewer's mount failure / sandbox error and waste a turn; (c) pdf-viewer's "not in allowed list" errors on your real file locations are actively confusing.
- 30.4. **Recommendation:** Remove **pdf-viewer** (CC gains nothing). Remove **Word (By Anthropic)** too unless you want app-level Word — the `docx` skill covers your `.docx` needs. **Keep:** Gmail (after reconnect), Calendar, Drive, Claude in Chrome, Filesystem, PowerPoint, Apple Notes. Nothing essential is missing to add.

31. Housekeeping:
- 31.1. To test pdf-viewer I copied one small PDF into the repo, then **voided** it per Void Rule → **`❌_temp_pdftest.pdf`** in repo root; please delete it manually.
- 31.2. Closed the Word doc **without saving** (read-only test; your file untouched).
- 31.3. § 24 & 25 (the job.md/jop.md reorg + label-protocol drafting) remain **on hold** per your instruction — resume after the reconnect/restart, when labels are live.

32. Your move: reconnect Gmail + restart the session (27.3); optionally remove pdf-viewer (± Word) per § 30.4; then tell me to proceed and I'll run § 29 (label create + verify) and § 24/25 (reorg) together.
