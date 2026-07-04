# Response to dissertation_query_202607042229.md
*Feedback, CIIW on Guide A, and the 8-agent debate*

## A. Housekeeping

61. Preamble —— apologies, I let bare `~` slip into 39.1 and 52.1 again; thank you for fixing them. I am using the backtick form `` `~` `` or plain words for the rest of this session.

## B. Quick Confirmations (Re 48, 49, 51)

62. Re 48 —— agreed, we keep the full submitted question set.
63. Re 49 —— understood; the enriched `_internal` guides are a post-approval task. I am adding a durable reminder to the DevPlan so it is not lost, and I will surface it when written ethics approval lands.
64. Re 51 —— doing it: a P15 note that the 2 reference files (Key Ethics Info and the application-form example) are consulted during the online application.

## C. textutil vs pandoc (Re 52)

65. Concise comparison, for your §8.8.5.1 decision:
- 65.1. `textutil` —— macOS built-in (no install), reads BOTH legacy `.doc` and `.docx`, fast; output is plain text or HTML. It flattens structure (tables and numbering collapse), so it answers "what does it say", not "how does it look".
- 65.2. `pandoc` —— needs installing (it is present here), reads `.docx` only (not legacy `.doc`), and converts to Markdown preserving more structure (headings, lists, tables, blockquotes). Even so it is not the visual `.docx`; this entire reformat exists because pandoc dropped the section numbering and turned the data table into a messy grid.
- 65.3. Advice —— for §8.8.5.1 (a quick read, no editing) keep `textutil` as the simple default, since it also handles `.doc`. Reach for `pandoc` only when you want lightweight Markdown structure, and rely on neither for true fidelity, which is exactly what §8.8.5.2's Quick-Mode PDF is for. In short, `textutil` primary, `pandoc` as an optional richer-structure tool with that caveat.

## D. Lu's Comments in the .docx (the important catch)

66. I did NOT read Lu's in-document comments during the sprint; I worked from the pandoc text, which drops comment bubbles. Dispatching a sub-agent now to extract and read the comments from the PIS `.docx`, check the Consent and Risk `.docx` for any of their own, summarise them, and judge whether they impose changes to our `_filled` forms.
67. Consequence for Re 54 —— if Lu's comments DO impose changes, I will NOT run the apply-to-`.docx` step; I will instead edit the `_filled` files to address them, as you instructed. The apply-step only makes sense once the comments are shown immaterial AND my two flags below are settled.

## E. Your Form Changes —— Identified and Agree (Re "All 3 working .md")

68. Reviewed your edits from the diffs and your notes; I agree with almost all:
- 68.1. PIS "family doctor" restored —— agree (verbatim template, safe); your point that TPS peers may not wish to consult colleagues is fair.
- 68.2. PIS "Australian" removed —— agree for the participant-facing docs; you disclose nothing false, and it widens the recruitable pool towards the 6-participant floor (e.g. Ben in a UK KBF). One light flag: at A3 write-up, the aim's "Australian KBFs" framing will need reconciling if non-Australian participants feature, or lean on the title's plain "Knowledge-Based Firms". Not an ethics-form issue.
- 68.3. PIS KBF definition removed —— agree; it declutters a participant-facing doc, and A1R still carries the definition for compliance.
- 68.4. PIS risk section —— you kept the softened acknowledgement plus skip, pause, and stop, but dropped the external signposting; agree, it avoids over-signalling risk whilst staying honest.
- 68.5. Consent in-person and MS Teams restored —— agree as a flexibility hedge, with the flag in 69.
- 68.6. Consent vertical-bar separators —— agree; they help the later `.docx` apply.
69. Two consistency FLAGS, which are why I am NOT proceeding to Re 54 unreservedly:
- 69.1. Withdrawal deadline —— the PIS now says the recording is "destroyed within a week after the interview" whilst the Consent says "prior to completion of the transcription process". These are different windows; UoL expects the PIS and Consent to match, and a reviewer checks precisely this. It is the UoL templates' OWN inconsistency (both verbatim), so keeping it is defensible, but I would align both to one rule, suggesting "up until the transcript is completed" as the operationally meaningful cut-off. Your call.
- 69.2. Audio-deletion trigger —— the Consent now says deleted "once the transcript has been completed, and participant approved of the transcription", whilst the PIS says "once the transcript has been completed" with no approval step. Same PIS-Consent mismatch. If you want the member-checking approval step, it should appear in both; if not, drop it from the Consent. Your call.
- 69.3. Net —— settle 69.1 and 69.2, or tell me to leave both as verbatim template, and, assuming Lu's comments are immaterial, the apply-to-`.docx` is clear. Until then I hold Re 54.
70. Also noted —— "Dr. LU LIU" all-caps restored reads like a placeholder, but it is the template's own wording, so your "protect myself" call stands; and the footer removal is good.

## F. Guide A —— the employer-evaluation line (CIIW)

71. On your doubt about "do not ask the participant to evaluate any employer's policies or practices":
- 71.1. It is not an arbitrary constraint. It is the exact mechanism that keeps us clear of INSTITUTIONAL AUTHORISATION. Lu was explicit (Log 16): "If the research is designed to evaluate or investigate the practices of a participant's current organisation, institutional authorisation may be required, which the student is seeking to avoid." A1R §3.5 codifies it.
- 71.2. The nuance that gives you the adaptability you want —— participants may freely discuss their OWN experiences and observations, including things they witnessed at a current employer. What triggers authorisation is asking them to formally evaluate or represent the employer's practices or policies. So the latitude is already wide; only that single move is off-limits.
- 71.3. My recommendation —— do not delete the idea, REWORD it positively to "the questions centre on the participant's own experience and observations" and drop the negative "do not evaluate" phrasing you dislike. That keeps the reviewer reassurance and the compliance shield whilst reading as enabling. If you would rather cut it entirely, we can, but then we must self-police in the room so no question drifts into assessing an employer's policy, or we forfeit the no-org-consent design.
- 71.4. Not editing the guide now —— you asked to proceed whilst I answer, and the debate is about to run on the current text; I will fold your decision in afterwards.

## G. The 8-Agent #debate (following debate.md)

72. Launching per `debate.md`: a live append-only board with 8 background debater agents plus a hybrid Observer agent, so I can handle the rest whilst it runs.
- 72.1. Guide A flawless versus not-flawless; the same pair for Guide B and Guide C, giving 6 debaters.
- 72.2. Two "as Lu" debaters grounded in `lu.md`: the guides ARE flawless versus they are NOT, giving 2 more.
- 72.3. I oversee via the digest, close on saturation, then write the Observer verdict plus a cost and compaction check into a follow-up `response_`.
73. The Guide A wording point (71) is left as-is going into the debate, so the debaters test the real current text; I reconcile it with your decision afterwards.

## H. Net

74. Acting now —— the Lu's-comments sub-agent, the 8-agent debate, and the P15 plus post-approval DevPlan notes. Holding —— Re 54 apply-to-`.docx` (pending Lu's comments and your call on 69.1 and 69.2), the Guide A reword (your call), and the `_internal` guides (post-approval). Nothing sent to Lu.

## I. Lu's Comments —— Result (they impose nothing)

75. The extraction agent recovered all of Lu's in-document comments (PIS 6, Consent 4, Risk 4) via a LibreOffice conversion (textutil could not read them):
- 75.1. Every comment is GENERIC UoL-template guidance ("for example, Version 1…", "delete the irrelevant one", "delete the irrelevant or keep both", "please add your name", "please sign"), none a directive aimed at you.
- 75.2. Verdict —— they impose NO changes; the `_filled` forms already satisfy each (version and date set, storage phrasing chosen, in-person and Teams kept, publication clauses retained, assessor named, hazards and emergency completed).
- 75.3. The one real-world action they flag is signing the Risk Assessment (a wet or electronic signature, not a text change).
- 75.4. So the Lu-comment gate on Re 54 is CLEAR; only my 69.1 and 69.2 consistency flags still hold it. The agent independently raised the same retention-wording consistency point, which reinforces 69.

---
*dlint 🟡 (L44, 71.1): the period inside Lu's quoted "…seeking to avoid." is original to her complete sentence, so Hart's rule (§2.1.4) keeps it inside.*
