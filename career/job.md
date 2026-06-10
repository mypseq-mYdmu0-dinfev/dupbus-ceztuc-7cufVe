# Job-targeted Gmail Scan
*Strict Prereq: `google.md`*

## Trigger
- `#job` → scan Gmail for criteria below.

## Scope
- Criteria: responding / related to submitted job applications; or signal job interview / offer.
- Window: 1 week unless specified.
- Sender: any (not just SEEK).
- MUST disregard by `-label:Label_1 -label:Label_2 -label:Label_3` (DON'T read any).
- Timezone: Gmail filters use UTC; fetch current SYD offset, adjust date boundaries.
- Order: importance, then recency.

## Exclude (completely disregard; DON'T include in response)
- SEEK official "Your application was successfully submitted" from `noreply@s.seek.com.au`.
- Employer auto-ack: received / will be in touch / find out more / will review / in process / in progress / track application / assessing.
- Anything criteria-unrelated / labelled BEFORE this session.

## 👀 Filter (note very briefly)
- Spam/Promo: criteria-related but w/ spam/promo signals inc. no subject/title, all caps (e.g. "LOADS", "FREE"), double exclamation (`!!`), podcast, and other marketing CTA elements
- Post-Flag Rejection: if an email was flagged (see below) but a subsequent email from the same company (might not be identical email address) implies rejection
- CC: The concerned job's AR is in `pending/` (user to process in PAR session, not #job)
- All Filtered: Briefly note at end for user review: sender email address, title (if any), why filtered

## 🗑️ FYI (report briefly)
- Progress update: e.g. "viewed".
- Rejection: e.g. "haven't progressed".

## ⛳ Flag (actionable)
- Pending action (even automatic): e.g. "complete your application", "a few more questions".
- SEEK relay (body truncated): e.g. "... has responded to your application"
- Employer manual (judge): "move forward", "invite".

## Avoid Revisiting
- To avoid surfacing in next #job, directly label:
  - § Filter & Note → Label_3
  - § Include → Label_3
  - § Flag → Label_2
- Goal: If `#job` again, assuming no new emails, no results should surface since all labelled.

## CC: Post-label `#jop`
If & ONLY if any flagged items (in order):
- Identify session as `/career/` CP
- Read CP Unconditionals
- Apply CP prefix to comms files
- Read `jop.md` via `career/CP_index_cc.md`