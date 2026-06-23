# Response to dissertation_query_202606232213.md
*replace_adv.md hardened against the U+2028 trap*

1. Done —— `universal/replace_adv.md` updated with 4 surgical edits (kept tight, no bloat):
- 1.1. **The Situation:** the mirror's breaks are now named as `U+2028` (Pages soft-returns) that render INLINE as a stray space, not a visible new line —— hence easily missed (precisely my error).
- 1.2. **Step 5:** `Replace:` must be copied VERBATIM, byte-for-byte, every `U+2028` preserved; never retype or normalise (retyping silently drops it and ⌘F fails); extract programmatically when in doubt.
- 1.3. **Example comment:** each break flagged as a `U+2028`, not a typed newline.
- 1.4. **Notes:** added the one-edit-per-`## Change` rule (the second failure).
2. Both failures are now encoded, so future CC follows the right method by default.
3. The corrected 31-change file (`…response_202606232120.md`) already embodies both fixes; nothing further owed there.
4. Hold resumes —— awaiting your application of the changes to `.pages`, then mirror back and I run P12.7.4 (re-QC).
