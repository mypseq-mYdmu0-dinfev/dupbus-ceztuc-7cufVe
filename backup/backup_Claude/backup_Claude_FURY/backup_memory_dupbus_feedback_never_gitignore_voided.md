---
name: feedback-never-gitignore-voided
description: "Never .gitignore voided `❌_` files — they must stay tracked so the user can SEE what CC voided"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0b6a0a90-0e48-4a4a-b4c2-496613e7d387
  modified: 2026-08-07T07:47:37.146Z
---

# NEVER `.gitignore` voided `❌_` files

**If it is ever considered again, PROPOSE it to the user with justifications first — do not just do it.**

## The rule
Voided files (`❌_` prefix, root CLAUDE.md §8.2) stay TRACKED. Never add a `❌_*` stanza to
`.gitignore`, and never `git rm --cached` them as a tidiness measure.

## Why (the user's own two reasons, both stronger than the problem they would solve)
1. **A voided file is voided precisely BECAUSE it is not yet ready to delete.** That is the whole
   difference between voiding and deleting. Making it untracked treats it as already gone.
2. **He cannot see CC's actions except through git.** He does not always get a `➡️` for each voided
   file — at volume that is correct and he agrees with it — so the commit diff is his ONLY window
   onto what CC voided. Untracking removes it. Consequences: an accidental void becomes invisible
   until something breaks, and a warranted void becomes invisible so he never knows to delete it.

## The context that produced the mistake
On 07/08/2026 a TEA1 `git add -A` swept 88 voided files (13,190 lines, 74% of that commit) onto the
public repo. The instinct was to ignore `❌_*` so it could not recur. That cures the noise by
destroying his visibility — a worse trade.

**The correct fix for that problem is root CLAUDE.md §3.1.6.1.6.3** (≥10 files changed in a turn →
split the commit), which he wrote in response to this incident. It attacks the real problem — a
commit he cannot read — rather than hiding the files that made it unreadable.

Related: [[feedback-spaced-filenames]], [[feedback-no-chat-prose]].
