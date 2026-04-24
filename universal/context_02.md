# Compaction Protocol

## On Detection

1. Alert in chat (override): `🚨 COMPACTION DETECTED`
2. Fetch files in 1st line of directory.md (before "Format: ...")
3. In artefact:
3.1. List every file alias whose tool result block contains "Older tool result cleared to save context" in 1 single line (not table)
3.2. Print first 10 words of my 1st msg in chat (NOT userPref or CP instr content) to confirm chat history intact
4. STOP

## Recovery (await my instr)

- I'll confirm which cleared files to be re-fetched
- Re-fetching permitted after compaction & exempted from "Each file fetched ONCE only" rule

## Post-Recovery

Resume the interrupted response from the point of detection; no need to restart the chat.