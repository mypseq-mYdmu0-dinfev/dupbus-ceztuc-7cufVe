# Response to career_query_202606102009.md
*Label-exclusion fix + interview reply drafts + labelling*

6. Label Exclusion —— root cause found & fixed
- 6.1. The line was **not** clear/correct. It used label **IDs** (`-label:Label_1 -label:Label_2 -label:Label_3`). Gmail's `label:` search operator matches the **display NAME**, not the internal ID, so `-label:Label_1` matched nothing and every labelled thread surfaced and consumed tokens.
- 6.2. Verified empirically this session: querying `-label:Unimportant -label:Actioning -label:Actioned` returned **zero** labelled items, whereas the ID form returned them all.
- 6.3. Edited both files to use names:
  - 6.3.1. `career/job.md` § Scope —— now excludes by name (you have since tidied it to "exclude labels per google.md").
  - 6.3.2. `universal/google.md` § Labels —— `-label:Unimportant -label:Actioning -label:Actioned`, plus a ⚠️ explaining name-vs-ID so future sessions exclude mechanically and never read labelled items.
- 6.4. Net effect: from now on, labelled threads are filtered at the **query** layer (never fetched), so they cost no tokens.

7. re 2 —— interview replies (drafts below; see §10 blocker on AR logging)
- 7.1. **home789 (Creative Marketing Specialist)** —— reply to Mary Shen (HR/Office Manager), proposing 3.00pm Fri 12/06:

```
To: hr@home789.com.au
Subject: Re: Application received for Creative Marketing Specialist

Dear Mary,

Thank you for the invitation to interview for the Creative Marketing Specialist position. I would value the opportunity to meet your team in person at the Rhodes office.

Friday 12 June 2026 suits me well. I would like to propose 3.00pm, and I am glad to adjust should another time on the day work better for you.

Please let me know if anything would be helpful from me beforehand. I look forward to meeting you.

Kind regards,
Culous Yu
```

- 7.2. **Alltech AV (Marketing & Growth Coordinator)** —— deferred per your instruction (handle after 7.1 & 7.3). Note: this is the **same SEEK relay** I had mislabelled; Elena Melnykova has in fact invited you to a first-round interview with three slots (Thu 11th after 4pm / Mon 15th after 10am / Tue 16th after 1pm). Draft below under 7.3.
- 7.3. **Alltech AV** —— reply to Elena Melnykova, proposing next Tuesday (Tue 16/06) at 3.00pm, which sits inside her offered window. Reply goes to the SEEK relay address:

```
To: (reply to noreply@seek.com.au relay thread)
Subject: Re: Alltech AV - Marketing & Growth Coordinator

Dear Elena,

Thank you for reviewing my application for the Marketing & Growth Coordinator position and for inviting me to the first round of interviews.

Tuesday 16 June 2026 works well for me. I would like to propose 3.00pm, which falls within your suggested window, though I can move earlier that afternoon if you prefer.

Please let me know if any further information would assist you ahead of our conversation. I look forward to speaking with you.

Kind regards,
Culous Yu
```

8. re 3 —— Include items handled
- 8.1. Labelled `Label_3` (the 8 non-L1 ones): people2people (Marketing Administrator), people2people (AI Chatbot), Peninsula (Paid Search), u&u (45280), StudioHawk, Rentokil, Impact Advising (Westmead), ona recruitment (Communications Advisor).
- 8.2. L1 items left untouched —— they shouldn't have surfaced in the first place; now prevented by §6.

9. re 4 —— Filter items labelled `Label_3`
- 9.1. SEEK "new activity in jobs you applied for".
- 9.2. people2people "complete your profile".
- 9.3. SEEK saved-job / "still accepting" reminders (×7) plus "save your searches".
- 9.4. The 4.4 item disregarded (you don't recognise it; it was the Oscar Wylee/Fuse talent-community welcomes —— I'll treat those as Exclude going forward).

10. re 5 + blocker
- 10.1. **B1 —— AR logging deviation.** jop.md says replies append to the job's AR, never `response_`. But the relevant ARs (`AlltechAV_MarketingGrowthCoordinator_202606052306.md`, `RocketAMS_...`) sit in `/seek/gcl/applied/applied_archive/` and were created **before this session**, which seek/CLAUDE.md forbids me to edit. Also **no home789 AR exists** (closest is `Rennly_CreativeMarketingSpecialist_202606080412.md` —— is home789 the same role advertised via Rennly, or a separate direct application?). So I placed drafts here pending your call: (a) confirm home789↔Rennly; (b) tell me whether to log into ARs by creating session copies, or keep replies in `response_`.
- 10.2. Your 5.1 (SEEK relay → Flag) confirmed present in job.md § Flag; your 5.2 (criteria narrowed to "responding/related to submitted applications; or interview/offer signal") confirmed —— this correctly reclassifies job-listing alerts and saved-job reminders as criteria-unrelated → Exclude in future. CIIW: looks right.
- 10.3. re your 5.6 —— job.md improvement advice:
  - 10.3.1. **Heading consistency**: the section titled "🗑️ FYI" carries the **Include** (progress/rejection) content, yet § Avoid Revisiting still references "§ Include" and "§ Filter & Note". Rename the section back to **Include** (or update the Avoid-Revisiting references) so the label-routing rules point at real section names.
  - 10.3.2. **Exclude precision**: add one explicit line —— "Generic job-listing alerts (LinkedIn/SEEK saved-jobs/Mastercard/Deloitte/Greenhouse/talent-community) and all non-job promo/personal = criteria-unrelated → Exclude, never label." This nails your 5.2/5.3/4.4 deterministically.
  - 10.3.3. **SEEK relay nuance**: note the deliberate sender split —— `s.seek.com.au` = SEEK automated (Exclude/Filter), `seek.com.au` = recruiter relay (Flag). Worth stating so the two are never conflated.
  - 10.3.4. **FL3 optional actions**: your 5.4 confirmed showcase-video / complete-profile / registration = Flag. The current § Flag examples cover "complete your application"; consider adding "optional enhancements (video intro, profile/registration completion)" so they're unambiguously Flag, not Filter.
- 10.4. Want me to apply 10.3.1–10.3.4 to job.md now?
