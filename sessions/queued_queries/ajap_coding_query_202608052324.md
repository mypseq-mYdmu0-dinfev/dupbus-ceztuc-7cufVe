# AJAP: Bring `AJAP_repo/` Scripts & pcmds Into `coding.md` Compliance

## Context (pointer only, NOT truth —— verify everything yourself)
- The owner rewrote `universal/coding.md` in the default repo over 4`~`5 Aug. Two sections changed materially: § Layout (code/config) and § Markdown Hygiene (`.md` only).
- His stated intent, verbatim: "the pt is to cut the verbose prose and make everything #bite pts... top comments are capped at ≤130chars/line for easier reading in VSC".
- He has asked that `AJAP_repo/`'s scripts and pcmds follow the same compliance. His words: "#qq to let AJAP CC make `AJAP_repo/`'s scripts/pcmds follow the new compliance of coding.md".

## What the rules now are
- READ `universal/coding.md` in the default repo directly —— do not work from this summary, which will rot. It is at `/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/universal/coding.md`.
- In outline, so you can judge the size of the job before starting: top comments (`"""`) capped per line; in-line comments (`# `) kept short; `.md` files never hard-wrapped and kept within a line-length cap by splitting into points rather than wrapping.
- ⚠️ The two sections are deliberately mutually exclusive —— § Layout governs code/config and explicitly EXEMPTS `.md`, which § Markdown Hygiene governs alone. Applying the wrong one to a file is the mistake to avoid.

## What is being asked (#SA)
1. AUDIT first, act second. Count how many files in `AJAP_repo/` actually breach each rule, and report the number BEFORE changing anything. The default repo's own audit found the corpus overwhelmingly non-compliant, so the honest answer may be "this is a session's work, not a turn's".
2. If the volume is large, propose doing it OPPORTUNISTICALLY —— every file you touch for another reason gets brought into line —— rather than one bulk reflow.
3. ⚠️ A bulk reflow is NOT a formatting job. `coding.md` § Markdown Hygiene mandates a content-preservation check on any mechanical transform: abort unless the whitespace-normalised before/after text is byte-identical. And splitting a long bullet into sub-points CHANGES the numbering, which is a semantic edit, not a cosmetic one.
4. Report back what you did, what you deferred, and the count either way.

## Note on ownership
- This is AJAP CC's call to make within its own repo. CCSIM owns `coding.md` itself and is not reaching across —— the ask is that the two repos end up under one convention, not that CCSIM applies it for you.
- If you disagree with any rule as it applies to AJAP's code, say so rather than complying silently; the owner would rather hear the objection.

## Reminder
- Rename and move this file per `sessions/queued_queries/README.md` before addressing it.
