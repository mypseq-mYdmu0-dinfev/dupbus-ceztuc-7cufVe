# Response to career_query_202606100314.md
*OTGC write access confirmed —— as expected, nothing to fix*

18. Re 15 —— **OTGC write access confirmed; everything as expected, nothing to fix.**
- 18.1. She loaded the Gmail tools, added `Label_2` (Actioning) to the Hays Salary Guide newsletter, verified it in `labelIds`, removed it, and confirmed restoration to `["INBOX"]`. Both `label_thread` + `unlabel_thread` work for her —— so CWI/OTGC can actuate, exactly as you presumed. Your OTG use case (label Actioning → Actioned, then track/send from the box) is fully supported.
- 18.2. Her side note is a real but harmless Gmail quirk, not our bug —— no file change needed:
  - 18.2.1. A **just-applied** label isn't immediately searchable via the `label:Label_N` operator (search-index latency), though the thread's raw `labelIds` reflect it instantly. So verify a freshly-applied/removed label via `labelIds` (as she did), not a `label:` search.
  - 18.2.2. The `-label:Label_1` skip in scans is **unaffected** —— Unimportant mail is long-indexed, so the exclusion stays reliable; the lag only bites labels applied seconds earlier.

19. Proceeding to **#close** now (per your instruction). The #job resume lands in a separate `response_` afterwards, outside the `close_`.
