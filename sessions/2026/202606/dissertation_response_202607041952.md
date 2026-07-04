# Response to dissertation_query_202607041952.md
*Feedback digest, corrections, and reformat plan*

## A. Your DevPlan Changes (Re 27)

39. Identified from git (no full re-read):
- 39.1. Stubbed P07~P12 to one-line completion markers (e.g. P12 "A1R v2 completed & sent; Log 22"); P07~P09 "done".
- 39.2. Restored P13's original title and points —— my rename ("Proposal Approval") made it read as if P13 spanned into P14, breaking the sequence.
- 39.3. Added the `> Standing Rules:` line at PART B top (line 174).
- 39.4. Housekeeping (Chat → Session, spacing).
40. Why and agree —— completed phases get stubbed once at reconstruction (the plan.md discipline), phases must stay sequential, and status lives in `close_`/AD not in phase titles. Agree fully; my P13 rename was the error.

## B. Your plan.md Changes + M5 (Re 28)

41. Identified:
- 41.1. Shrank my verbose "DevPlan Editing" bullet into "Stub completed phases ONCE at reconstruction" plus explicit "NEVER P0 / P[nn].0" rules.
- 41.2. Added `> Standing Rules:` in PART B so every GENERATED DevPlan carries it —— actually effective, unlike a template-internal note.
- 41.3. Deleted my "re-read this plan.md before edits" line.
- 41.4. Chat → Session, `[nn]` two-digit rule, PART C addenda pointed to `close.md`.
42. Why and agree —— my "re-read plan.md" line was useless (CC only sees it when already reading plan.md, and never sees it when not). Enforcement belongs in the generated artefact, which is exactly what your PART B Standing-Rules line achieves. Agree fully; good lesson.
43. M5 —— YES, your Standing-Rules line supersedes my `## M5. DevPlan Editing Discipline`. It is now redundant, so I am removing it (one of the two requested DevPlan edits this turn).

## C. Stale A1 Dates (Re 30)

44. You are right —— I did not read A1; I was misled by DevPlan lines still carrying original-A1 timing that earlier sessions never updated to A1R v2:
- 44.1. Header line 4 "Due: ... ethics application target Wk9 (w/c 12/05/2026)" —— stale.
- 44.2. M1 line 180 "A1R approved Wk8~9; ethics application submitted Wk9" —— stale.
- 44.3. P12.4.1 (line 72) also names Wk9, but only as the historical context of a completed phase describing why the timeline was rebuilt —— low-risk, so I leave it as a record.
45. Updating 44.1 and 44.2 to A1R §4's re-baselined milestones (ethics submitted Wk16 w/c 30/06/2026, approval Wk17 w/c 07/07/2026, collection Wk18 w/c 14/07/2026). These two live lines were the exact source that made my first-draft Sprint timeline reference the lapsed Wk9 before I corrected against §4.

## D. #debate Protocol Miss (Re 37)

46. Acknowledged, and it is a fair catch. I ran a 2-agent adversarial verification and loosely called it a "#debate" without first reading `debate.md` or creating its required files (§7.3.2 mandates reading the trigger file). Re-read §7.3.2; I will follow `debate.md` properly on the next real `#debate` and am NOT reading it now per your instruction. The QC itself was sound, but the label and protocol were not.

## E. Sprint Report Feedback (Re 5, 7, 8)

47. All noted, nothing to change —— Teams-only correct, Data Processor kept (your call, agreed it is odd wording but a non-edit field), publish window kept (you want it), no-CYC in participant docs endorsed, Risk produced and softened endorsed, weekend note you trimmed yourself. Thank you for the confirmations.

## F. Pull-Back Strategy (Re 6 —— thoughts only, no edits)

48. I recommend AGAINST deliberately thinning the submitted question set:
- 48.1. The flexibility we legitimately hold is rewording and probing WITHIN approved topics; hiding questions does not buy the right to ask NEW topics.
- 48.2. A withheld question on an already-approved topic adds nothing (the submitted set's probes already cover that ground); a withheld question on a NEW topic is unusable without a formal amendment, since asking an un-approved instrument is the breach we are avoiding.
- 48.3. A visibly thin guide risks reading as under-developed to a rigour-focused supervisor, and the plain test holds —— if a question is too sensitive to submit, it is too sensitive to ask.
49. The better route to the same goal —— keep the full submitted set (already pitched "just right"), and, if you want, I build `_internal` working copies that ENRICH each guide with more probes and interviewer notes on the SAME approved topics. That magnifies practical flexibility for the actual interviews without under-submitting or risking approval. Your call; I will not build them unless you say so.

## G. The Remaining 2 Files From Lu

50. Already scanned (a sub-agent read both during the sprint). What they are:
- 50.1. `Key Ethics Information Required.docx` —— UoL's guidance document, a field-by-field instruction set for the online application (e.g. upload the interview questions at Q5.14, the PIS at Q5.30, select "Online Programme" at 1.9 and "Human Participants" at 1.22). Reference only; nothing to complete.
- 50.2. `Research ethics application form - example.docx` —— a worked example of the online application form itself, i.e. the P15 form. Reference or template; not to be completed now, since Lu gated the online form.
51. Both are P15 reference material, not deliverables Lu asked for, and not needed before you email her the 6 files. They come into play at P15.

## H. Format Issues + Reformat (I now have the PDF)

52. Root cause —— I converted the `.docx` via pandoc to `.md`, which stripped its real structure. The PDF shows what I missed:
- 52.1. Sections ARE numbered 1~15; I lost the numbers. Restoring them as two-digit `**01.**`~`**15.**` so `⌘F "01"` lands cleanly.
- 52.2. The `> ` blockquotes were pandoc's rendering; I will keep a single `> ` per block but on ONE unwrapped line, so you strip the prefix once per block, not per wrapped line.
- 52.3. Item 8 ("How will my data be collected … destroyed") is a 2-column table; I will render each left-column question as a sub-heading with its answer as text beneath, which is both readable and easy to grab.
53. Reformatting all 3 forms (pristine and filled) to match the PDFs, via a sub-agent (mechanical, and it preserves my context). I will keep your pristine-vs-filled diff intact by reformatting the pristine, then re-applying only the content fills to a `_filled2` copy, and voiding the old `_filled` for your review and rename.

## I. Copy-Paste Estimate, and §8.8.5 (Side Task)

54. Copy-paste estimate across the 3 forms —— PIS about 12 filled sections, Consent about 7, Risk a whole table of roughly 15-plus cells, so comfortably over 10. A sub-agent applying the fills into the `202607041946` working `.docx` copies (Word tools, falling back to computer-use) is worth it. Per your note this is a SUGGESTION only; I am not acting on it.
55. §8.8.5 update —— apt. Had I converted the templates to PDF via Quick Mode and seen the numbering and tables, I would have built the `.md` in the right shape first time and this reformat would be unnecessary. The rule now steers future CC to do exactly that, so the issue should not recur.

## J. Net

56. Acting now —— the two requested DevPlan edits (stale dates, remove M5) and the reformat sub-agent. Holding —— the pull-back decision (yours), the copy-paste-into-docx step (suggest-only), and the interview guides (untouched, awaiting your read). Nothing sent to Lu; the email remains your draft in Log 25.

## K. Reformat Complete

57. Done —— all 3 forms reshaped to match the PDFs (I verified the PIS output directly):
- 57.1. Pristine `X.md` reformatted in place —— PIS with 15 two-digit sections (`01.`~`15.`), single-line blockquotes, and section 08's data table as bold sub-headings with text beneath; Consent with 9 numbered statements; Risk as clean pipe tables.
- 57.2. `X_filled2.md` created for each —— the reformatted structure carrying your content fills, so the pristine-vs-`_filled2` diff is exactly the fills, nothing else.
- 57.3. Old `X_filled.md` voided to `❌_X_filled.md` (awaiting your manual deletion), per the Void Rule.
58. Your finishing steps —— review the 3 `_filled2` files, delete the 3 `❌_` voided ones, and rename `_filled2` → `_filled` for clean storage.
59. dlint on the `_filled2` files —— Risk clean; PIS (RED 2) and Consent (RED 3) carry only the justified UoL template field-label colons and the "Master's"/"want" template words; authored prose clean.
60. One revertible judgement call —— the Risk table's L/M/H columns were collapsed to a single "Final risk rating" letter column (all currently `L`) for readability; say the word if you prefer the literal 3-column layout.
