# Response to dissertation_query_202606110141.md
*Housekeeping diff + OTG + RA call*

*Preamble noted: Hart's quotation rule applied throughout.*

---

46. Your changes to the concerned files (spotted + inferred)
- 46.1. You committed my 100700 work, the DevPlan truncation, the `archive/` copies, and the `addenda/` files, and you deleted the seven `❌_` stubs (Void Rule). Agree, exactly as intended.
- 46.2. You left `CP_index_cc.md` uncommitted for this turn (the one file still showing as modified). Agree, it was the piece pending finalisation plus the OTG mirror.
- 46.3. ⚠️ Git case split (needs your action before push/#sync): the 7 new files are committed under lowercase `archive/`, but the pre-existing `Archive/MGTK751_A1_DevPlan.md` and `Archive/WCIC_Research/` remain under capital `Archive/` in git. On this case-insensitive disk they share one physical folder, but GitHub is case-sensitive, so it will render two folders and the lowercase `A1_DevPlan` URL will 404. Fix: `git mv Archive/MGTK751_A1_DevPlan.md archive/…` and the `WCIC_Research` subtree, so all paths are consistently lowercase. Not executed (git structure is yours).

47. Net `CP_index_cc.md` changes this session (uncommitted vs HEAD)
- 47.1. Removed the `A1_Grade.md` entry from "Official Files".
- 47.2. Added a new "## Archive" section: `A1_DevPlan.md`, `A1_Grade.md` (now an `archive/` path), `addenda.md` (AD01–AD07), and the "Formative A1 set + misc".
- 47.3. That is the complete diff; nothing else in the file changed.

48. `CP_index_otg.md` —— updated
- 48.1. Mirrored the CC changes: removed `A1_Grade` from "Official Files"; appended the same "## Archive" section.
- 48.2. New URLs use the `main` branch (non-SHA) per your instruction, awaiting the next #sync to pin SHAs.
- 48.3. Same case caveat as 46.3: the `A1_DevPlan` main-URL assumes lowercase `archive/`, so it resolves only after the case-normalisation.

49. RA —— my call (you asked "unless you believe we should alter RA")
- 49.1. Agree with all three of your corrections: keep "empirical foundation", no defined group, drop the "manage this challenge" tail.
- 49.2. I do recommend one small alteration, not bending to her example, but removing the exact phrase she misreads ("management challenge of CYC"): the RA ends at "for CYC's KM consulting practice", and the challenge is explained in the email instead. Full reasoning in the optimised 110211.
- 49.3. On being direct with Lu: yes, but framed as clarifying CYC's nature (MCF startup, product = KM consulting), not as correcting her, to protect the marking relationship. Her underlying logic already matches ours, so this should land as alignment, not pushback.

50. 100717 —— optimised
- 50.1. Rewritten bitesize per your comments (defend substance, educate Lu on the MCF model, RA per 49, sampling realism with the honest access caveat, theoretical framework). Ready for review; next step on your go-ahead is the email draft.
