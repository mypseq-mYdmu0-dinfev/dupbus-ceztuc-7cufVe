# Job-targeted Gmail Scan
*Strict Prereq: `google.md`*

## Trigger
- `#job` → scan Gmail for job-application / interview / offer signal.

## Scope
- Window: 1 week unless specified.
- Sender: any (not just SEEK).
- MUST add `-label:Label_1` (skip Unimportant; per google.md).
- Timezone: Gmail filters use UTC; fetch current SYD offset, adjust date boundaries.
- Order: importance, then recency.

## Exclude (application confirmations)
- SEEK official "Your application was successfully submitted" from `noreply@s.seek.com.au`.
- Employer auto-ack: received / will be in touch / find out more / will review / in process / in progress / track application / assessing.

## Filter & Note
- Spam/Promo: signals inc. no subject/title, all caps (e.g. "LOADS", "FREE"), double exclamation (`!!`), podcast, and other marketing CTA elements
- Post-Flag Rejection: if an email was flagged (see below) but a subsequent email from the same company (might not be identical email address) implies rejection
- CC: The concerned job's AR is in `pending/` (user to process in PAR session, not #job)
- All Filtered: Briefly note at end for user review: sender email address, title (if any), why filtered

## Include (report briefly)
- Progress update: e.g. "viewed".
- Rejection: e.g. "haven't progressed".

## Flag (actionable)
- Pending action (even automatic): e.g. "complete your application", "a few more questions".
- Employer manual (judge): "move forward", "invite".

## CC only —— after scan
If & ONLY if any flagged items (in order):
- Identify session as `/career/` CP
- Read CP Unconditionals
- Apply CP prefix to comms files
- Read `jop.md` via `career/CP_index_cc.md`