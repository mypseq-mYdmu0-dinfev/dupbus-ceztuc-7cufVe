# Compaction Protocol

## On Detection

1. Alert in chat (override): `🚨 COMPACTION DETECTED`
2. Fetch files in 1st line of directory.md (before "Format: ...")
3. In artefact, list every file alias whose tool result block contains "Older tool result cleared to save context" AND print 1st 10 words of my 1st msg (confirming chat history intact)
4. STOP

## Recovery (await my instr)

- I'll confirm which cleared files to be re-fetched
- Re-fetching permitted after compaction & exempted from "Each file fetched ONCE only" rule

## Post-Recovery

Resume the interrupted response from the point of detection; no need to restart the chat.