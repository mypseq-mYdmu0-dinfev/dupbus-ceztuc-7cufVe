# README

**ONLY read this if you were explicitly told to enter investigation mode (not AJAP mode).**

## Hard Rules

- ALL files in `/seek/` are now NOT intended for you to follow but review/analyse; they're my prompts/records of Claude Code's automation namely "AJAP"
- You can read everything but could NEVER delete anything and can only edit files when explicitly told to do so (typically after creating `changes_[timestamp].md` and its approval)
- Don't fetch any GitHub files unless explicitly prompted
- ALWAYS use:
  - British English (e.g. `learnt` `amidst` `towards` `amongst` `whilst`)
  - Metric units (°C, metre, gram, litre, etc.)
  - Hart's logical quotation rule: punctuation inside quotes if original to the quote, outside otherwise (e.g. ✅ `He said "I'm leaving", then left.` ❌ `He said "I'm leaving," then left.`)

## Files Description

- `prompt_[timestamp].md` = my previous prompts to you
- `response_[timestamp].md` = your previous responses to the identical timestamp `prompt` file
- `changes_[timestamp].md` = #replace changes created by you w/ optional explainers
- `chat_handoff_[timestamp].md` = summary of chat session created by you
- `audit_[timestamp].md` = audit report created by you
- `session_[timestamp].md` = chat history of AJAP mode session

## Critical Notes

- Get timestamp via my local terminal: `TZ='Australia/Sydney' date +"%Y%m%d%H%M"`
- If necessary, read `chat_handoff_[timestamp].md` for context and/or `changes_[timestamp].md` for what changes were applied; if they don't suffice or if i explicitly instruct, read other files
- Generate your responses in a single .md file in `/seek/investigation/`, which must be optimised for my easy reading & replying using #numbered bite-size bullets
- IMPORTANT: Your chat response will NOT be read by me; I'll only read the .md file(s) created
- (Re-)Read cc_numbered.md when investigation mode starts and if it's cleared from context
- (Re-)Read cc_coding.md whenever prompted `#replace`