# Response to career_query_202606100234.md
*Reviewed all edits —— IDs intact, agree broadly, 2 gaps to close*

9. **Critical label check —— PASS, no fix needed.** `list_labels` confirms IDs intact: `Label_1`=Unimportant, **`Label_2`=Actioning**, **`Label_3`=Actioned**. You renamed display names in place; IDs are immutable, so every `Label_2`/`Label_3` reference across the files still resolves. Nothing to restore.

10. **CWI/OTGC doing email actions —— I am NOT against it.** Sound call:
- 10.1. Dropping `CC-` makes the labels interface-neutral, and the protocol now sits in google.md (general file) as "ALL Claude email-actioning tasks" —— consistent; any interface that reads google.md can follow it.
- 10.2. One caveat (capability, not objection): an interface can only *actuate* if it actually holds the Gmail write tools (`label_thread`/`unlabel_thread`). If CWI/OTGC is read-only on Gmail there, it follows the same state semantics via CIC clicks or you label manually. Worth confirming those interfaces have the write scope before relying on them.
- 10.3. No consistency risk —— the two-state is per-thread and stateless across interfaces.

11. Changes spotted + why + verdict:
- 11.1. **google.md** (you did my #replace + more): split Gmail into Timezone / Labels / #job-Prompted; removed the bulky scan (→ job.md); expanded the map to Label_2/3; **relocated the Actioning/Actioned protocol here** from jop.md and generalised it; refined completion to "add Label_3 → remove Label_2" (no labelless gap) and interrupted → "alert user + ask". **Agree** —— cleaner, and this resolves my earlier flag 7.1.
- 11.2. **job.md**: human-readable title; "Strict Prereq google.md"; CC-only step gated "If & ONLY if any flagged items". **Agree** —— avoids CP overhead on empty scans.
- 11.3. **jop.md**: protocol removed (→ google.md); FL1/2/3 tags; FL1 invite kept "verbatim"; AR append differentiated FL1&2 vs FL3. **Agree** —— jop.md is now pure processing.
- 11.4. **CP_index_cc.md**: added job/jop entries; § 3.4 condensed to "see below". **Agree** (routing still resolves via the entries + google.md) —— but one stale line, see 12.1.
- 11.5. **CP_index_otg.md**: job.md entry kept (placeholder URL); my preamble #job routing line removed (now covered by google.md's "#job-Prompted"). **Agree on intent** —— but see 12.2.

12. **Gaps remaining (2) —— close before you push:**
- 12.1. **CP_index_cc.md jop.md line is stale.** It still reads "`CC-actioning/actioned label protocol; read when #jop`" —— but the protocol moved to google.md and the `CC-` names are gone. **Fix:** `#jop processing (employer invite / SEEK relay / pending action); read when #jop.`
- 12.2. **CP_index_otg.md omits `google.md`.** OTGC fetches only by URL from this index. Both job.md's "Strict Prereq: google.md" **and** the Actioning/Actioned protocol live in google.md, yet OTGC has no URL for it → on `#job` or any email-action it can't reach the prereq or the label rules. **Fix:** add a `google.md` entry to CP_index_otg.md (Core or Prompts); `#sync` will then pin its raw URL alongside job.md's. (CC is unaffected —— it loads google.md via root § 7.2.)
- 12.3. Optional: add `google.md` to CP_index_cc.md too for self-containment (not required; root § 7.2 already loads it for CC).

13. With 12.1 + 12.2 applied, **no gaps remain** —— CC and CWI/OTGC both resolve `#job` (scan/report) and the label protocol; only CC reaches `#jop` (jop.md absent from the OTG index, as intended).

14. **#sync —— ready.** After you push, I'll `#sync career/` to fill the job.md placeholder (and google.md's, if you add 12.2) in CP_index_otg.md with pinned-commit raw URLs matching the rest. Lock 12.1/12.2 in first so one sync captures everything.
