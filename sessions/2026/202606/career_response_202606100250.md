# Response to career_query_202606100250.md
*OTGC verify-prompt + files suffice; all closed bar commit/push*

15. Re 10 —— OTGC write-capability verify prompt (reversible live test; copy-paste):
```
Read my Gmail file google.md (via my OTG index). Then verify you can WRITE labels, not just read: pick one low-stakes email, add the `Actioning` label, confirm it shows, then remove it again. Tell me that email's subject and whether BOTH the add and the remove succeeded. If you have no tool to add/remove a label (read-only on Gmail), say so plainly. Change nothing else.
```
- 15.1. Live add+remove rather than self-report —— capability is proven by doing, it's fully reversible (ends clean), and if she's read-only she'll surface the missing tool.

16. Re "do current files suffice for the use case" —— **yes, conditional only on that write scope:**
- 16.1. The use case isn't `#job`; it's general email-actioning, already governed by google.md ("ALL Claude email-actioning tasks": never archive; add `Actioning` on start; `Actioned` on completion; IDs `Label_2`/`Label_3`; actuate via label_thread/unlabel_thread). OTGC reading google.md gets all of it.
- 16.2. No job.md/jop.md needed —— correct, since she can't reach ARs/CIC; those stay CC-only. Your reminder "read google.md + follow labelling rules" is sufficient.
- 16.3. Sole dependency = she actually holds the write tools (15 verifies). If read-only, she labels via Gmail-web clicks or you do it manually; the state semantics are unchanged.
- 16.4. So the convenience you're after —— track the involved emails in `Actioned`, then send the drafted replies later straight from that box —— is fully supported as-is.

17. Re your Missions —— **all gaps closed, all missions resolved bar commit/push:**
- 17.1. 12.1 —— confirmed fixed (jop.md line is now just "Read when `#jop`").
- 17.2. 12.2 —— accepted: google.md sits in userPref, fetched via that `index_otg.md` for every OTGC session CP-independently, so it's reachable. Not a gap.
- 17.3. Missions 1–3 done —— scope live (1); labels exist + actuation verified, test emails reverted by you (2); files built + your refinements (3).
- 17.4. Outstanding = **commit & push only.** Once pushed, tell me and I'll `#sync career/` to replace the job.md placeholder URL in CP_index_otg.md with the pinned-commit raw URL.
