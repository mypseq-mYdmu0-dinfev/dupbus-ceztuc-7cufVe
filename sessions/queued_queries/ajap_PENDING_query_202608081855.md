# Reply to response_202608061952.md & response_202608071304.md

## Preamble
major changes applied again; for all pcmds you've read in this ses, check if they were changed since your last read; if yes, retrieve the changes; if unsure, #SA read in full then tell you the delta

## DevPlan
i seem to see you have retired DevPlan from being #r by default by #inv ses which you seem to have achieved such context/token savings by extracting pending items from the DevPlan into inv/CLAUDE.md —— good call, and these items should be resolved ASAP because although YOU don't needa read the DevPlan (possibly still have to extract particular lines when we're cracking down the pending items), i would still have to read it so as to understand what those open items truly are
that said, we need a special arrangement when we `#close` (not now)
you needa serve duties of both non-DevPlan AND DevPlan ses
for the DevPlan, i need a final addendum to mark it's closed & demoted to ref-only
for the `close_`, it should be self-contained (unlike a DevPlan ses's `close_` which heavily relied on the addendum)

## WOMP Creation
refer to my `query_202608061952.md` up to the `## DevPlan Weight`
help me standardise and operationalise this complex action —— orientation, huge amount of retro reading, extracting/distilling what's critical or still open, telling what's still on my plate, etc. —— into a new, universally applicable (not just AJAP) pcmd as `universal/womp.md`
apparently it's triggered by `#womp`, which means "What's On My Plate" —— usually used when i front-loaded CC's works and accumulated multiple unread `response_`, where many content might have been superseded by subsequent actions or `response_` that i want CC to help save my time by orientating where we are now and extracting what still warrants my attention (e.g. critical things i should know, still open items that are awaiting my green light) —— similar to what you did in this ses
it will have 2 optional modifiers (if both not prompted, CC judge; if needed, clarify before `#womp`'ing):
first, `#womp #scope` —— i scope the files to be `#womp`'d, could be a long trail of `response_` or other files like DevPlan, a simpler approach in a simpler situation; prompt examples: `#womp #scope X.md, Y.md, ...` OR `#womp #scope all (X-prefixed) comms files since [TS] (in [folder]; e.g. `sessions/` `inv/` —— could be more as i'm adding new repos soon)
second, `#womp #context` —— i tell the whole story, similar to what i did in this ses; e.g. which was the last `response_` i #r, which was the last `query_` i manually wrote, etc.; prompt examples: `#womp #context [prose]` (less direct, heavily rely on CC's understanding/judgement, like this ses)

## 1
1.6.4: where did you add that? apparently this is a line that would be stale very soon, becoming deadweight (depending on where you put it)

## 3
3.01.1.3: im still serving as advisor at Karma Effect Ltd (as shown in my resume; pro bono) in parallel to my new job
3.01.3: 50hr is my max. time/wk which is possibly unfeasible and even illegal in SYD; typically a job here is 8hr/day *5 = 40hr/wk, although i can commit more than that (if the offer attracts me), hence the 50hr; KE continues alongside Alltech, as said (im explicitly permitted by the employer)
3.01.4: what is false? why does `CP_notes.md` needs update for my new employment?
3.02: again, im asking if i'm clear to start a cockpit ses, which naturally resets CONTROL.md for me
3.04: this is one of the reasons i NEED YOU; IDEALLY, i will clear `logs/analytics/` after every AJAP run by importing the data into my spreadsheet, keeping it clean; BUT i can't guarantee that (don't rely on me clearing it out) and AJAP must be aware of existing .md/.csv in that folder and not overwrites them; another way to see it is: when AJAP starts running, it must create its own input .md in that folder and always writes on that input .md only UNTIL a true stop (e.g. i or cockpit writes `STOP`, `wkstop_[n]` reached, etc.) that it will generate the output .csv where that AJAP run is truly finished; then loop
never move `logs/analytics/` files into its `archive/` for me
inside `archive/` = i've imported them into my spreadsheet which can only be manually done by me and which, as i said, should not impose impacts to AJAP at all



## 16
16.5: i dont see why you can't run it for me then act accordingly; im not asking to run it right now, im asking if i can proceed to start a new cockpit ses then prompt `#seek`; so run them now if you see fit
16.6: as said im not running AJAP now






## New QQ
CCSIM CC replied you + drafted a new one
address `ajap_compact_query_202608081725.md` `ajap_evidence_query_202608071749.md`
if necessary (you see gaps or you implemented differently that CCSIM CC should consider to follow), #qq back to her


