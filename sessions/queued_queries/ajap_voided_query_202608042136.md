# AJAP: 792 Voided `❌_` Files —— Are They Ready to Delete?

## Context (pointer only, NOT truth —— verify everything yourself)
- A CCSIM session sweeping `GitHub/` for voided files counted **792** `❌_`-prefixed files under `AJAP_repo/`, nearly all in `gcl/skipped/skipped_archive/2026/[YYYYMM]/`.
- CCSIM did NOT touch any of them and does not own them —— this is handed over, not delegated.
- The owner's read, which you should confirm rather than assume: "the void rule is the same across both repos; mostly those voided ones were just reprocessed and then went to `applied/` or `pending/`".
- So the working hypothesis is that each `❌_` file has a live successor elsewhere in the tree, and the voided copy is redundant history awaiting the owner's manual delete.

## Why This Is Being Raised Now
- Root `CLAUDE.md` §8.2.4 says to remind the owner of any voided file whose mod time is ≥7 days. These are far older than that and nothing has ever surfaced them.
- The default repo now has `cscpt/ccsim_housekeeping.py`, which prints exactly this queue. It walks EVERY sibling repo under `GitHub/` and prunes `AJAP_repo/` alone —— precisely because a blanket `❌_` sweep would drown in these 792 and invite a catastrophic mass-delete on the prefix. That exclusion is load-bearing and documented in the script.
- ⚠️ That exclusion means NOTHING watches AJAP's voided queue, and nothing will. That is the gap this query exists to close, and it is now the ONLY reason the exclusion exists —— so answering it either retires the exclusion or confirms it permanently.

## What Is Being Asked (#SA)
- Dispatch a sub-agent to investigate BRIEFLY —— this is a triage, not an audit. Sample rather than enumerate all 792.
1. Confirm what the `❌_` prefix actually means in `AJAP_repo`. Is it the root Void Rule (CC renames, owner deletes), or an AJAP-specific "skipped, archived" convention that merely shares the glyph? The two need opposite handling.
2. For a sample, verify the successor hypothesis: does each voided file have a live counterpart in `applied/` or `pending/`? Say how you sampled and how confident the result is.
3. Establish whether ANYTHING still reads them —— a script, a log, an index, a test. A file nothing reads is safe to delete; one that a script globs is not.
4. Advise: are they ready for the owner to delete, in whole or in part? If only in part, give the discriminator he can apply himself.

## Scope Limits
- READ-ONLY investigation. Do NOT delete, rename, or move anything —— deletion is the owner's half of the Void Rule.
- Do NOT touch the default repo (`dupbus-ceztuc-7cufVe/`).
- Do NOT `ls` whole month folders indiscriminately; use `find` with a name filter.

## Reminder
- If the answer is "yes, deletable", the useful deliverable is a single copy-paste command the owner can run in a fresh terminal, with the count it will remove stated first so he can sanity-check it before pressing return.
- If the prefix turns out NOT to mean the Void Rule in this repo, say so loudly —— that is a naming collision worth fixing at the source, and the default repo would want to know.
