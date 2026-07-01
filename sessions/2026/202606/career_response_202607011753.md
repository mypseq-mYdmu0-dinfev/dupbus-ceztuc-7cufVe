# Response to `career_query_202607011753.md`
*§3.4.7 fixed; §3.4.8.1 still carries the ambiguous phrase that bit us*

## Re 4 — §3.4.8
8. "Finding" (vs "Encountering") is a good broadening —— it rightly covers files referred from a `close_`/`wrap_`, not just your msg. ✓
9. ⚠️ But 3.4.8.1 still says "current year/month", and that exact phrase is what misled me. Your 4.1 says you mean "the session's own folder" —— but the words read as the CALENDAR-current month. For a spanning session (started June, now July) the two differ: the file is in 202606, whilst "current" reads as 202607. As written, 3.4.8.1 would look in the wrong place first —— the very bug.
- 9.1. Fix (small, keeps it lean): make 3.4.8.1 say **"By the session's own folder (start-month, per 3.4.5)"** instead of "current year/month". That encodes your actual intent and cannot be misread.
- 9.2. Bonus: it also removes a term clash —— "current year/month" currently means the SESSION folder in 3.4.8.1 but the CALENDAR-current month in 3.4.7 (same phrase, two meanings). Rewording 3.4.8.1 leaves "current year/month" meaning only calendar-current, cleanly.
10. Re your "maybe `find` returns one line, do we even need this?": you are right —— `find` on a unique TS filename returns exactly ONE line, so no token bloat and that worry is unfounded. BUT the subsection still earns its place: constructing the path directly (session folder) skips the `find` subprocess entirely and is deterministic. So keep it —— just leaner:
- 10.1. With 3.4.8.1 = the session folder (deterministic), **3.4.8.2 (MM-1) becomes redundant** —— it was only a patch for the calendar-current mismatch. Dropping it leaves (1) session folder → (2) `find` fallback: two steps, correct and lean. (MM-1's only marginal use is a file from LAST month's different session referred in a `close_` —— which `find` catches anyway.)

## Re 5 — §3.4.7
11. The "1st of session AND" addition is exactly right —— it limits the wrong-folder check to SESSION START, so a later-TS query correctly sitting in the start folder (per 3.4.5) is no longer flagged as "wrong". My earlier §5 concern is fully resolved. ✓
12. Knock-on: here "current year/month folder" correctly means the CALENDAR-current month (at session start, if the 1st query is elsewhere → confirm). That reading is right —— it is only the phrase SHARED with 3.4.8.1 that is the issue (see 9.2), not 3.4.7 itself.

## Net
13. §3.4.7 = good as-is. §3.4.8 = one wording fix (9.1) prevents recurrence, and with the optional MM-1 drop (10.1) it is leaner AND correct. Want me to apply 9.1 (and 10.1) to CLAUDE.md? Otherwise no changes —— it is your core file.
