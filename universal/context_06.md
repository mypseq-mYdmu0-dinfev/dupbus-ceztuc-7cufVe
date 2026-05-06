# Context Recovery Protocol
- Fetched because PP1 failed due to #01/directory.md compaction
- Below instr temporarily override "no chat text"/"each file fetched once only"

## On Detection

1. Alert in chat: `🚨 Compaction Detected`
2. Re-fetch unconditionals of directory.md (& CP_directory.md)
3. Identify other files fetched in this chat; if no `✅` declarations found, alert in chat: `🚨☠️ FIFO: Chat history compromised`
4. For each, re-fetch if still relevant to current/planned tasks; skip otherwise or if its info already sufficiently surfaced in prior responses
5. Declare per #cc (NO `✔︎` since PP1 failed)
6. Artefact:
- Print first/last 10 words of 3rd artefact (#03) to prove chat history intact; if failed, alert in chat: `🚨☠️ FIFO: Chat history compromised`
- Briefly justify why file(s) were skipped for re-fetching
  - If ≤10 files: ≤10 words each
  - If ≥11 files: ≤5 words each
- Don't justify unconditionals
- Skip if all fetched files were re-fetched (none skipped)
7. Resume addressing my last msg in separate artefact(s); no need to restart the chat

## Notes

- Directory.md cleared (`[Older tool result cleared to save context]` found) ≠ Chat history cleared
- Re-fetch latest ver of files by directory.md in userPref (& CP_directory.md in CP instr)
- Unconditionals = 1st line (above "Format: ...") of directory.md (& CP_directory.md)
- Conditionals = everything else in directory.md (& CP_directory.md)
- "Other files fetched" inc. not just conditionals (e.g. GH provided, even not declared)
- Re-fetch skipping examples (judge per chat):
  - shrink.md if no more content shrinking expected
  - profile.md after demanded info extracted