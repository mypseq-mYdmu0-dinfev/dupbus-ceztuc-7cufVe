# Reply to dissertation_response_202606150723.md

## DevPlan P12
P12.0.2: create a new step (maybe immediately before/after this) to validate such assumption by revisiting Lu.md fully (suggest to use SA)
P12.3.3: see below pt 4.2
P12.3 completion: do a word count for ALL (sub-)sections in §1–3 then append `([no.] words)` as a new line after each; then briefly tell user the sum & if that remains socially reasonable (despite Lu said unlimited words)

## DevPlan M4
to be reviewed verbatim by me whilst you're working on P12; so far it seems good

## DevPlan Changes
identify my changes; infer why; tell if agree
special notes: i've changed from "fetch" to "read", because "fetch" was there originally for CWI/OTGC, which i dont see myself using for serious works (mainly only OTG); if agree, help me cleanly change all "fetch" to "read" (minor)

## Deliverable

*update DevPlan to concisely note of these, just in case you compacted and lost it*

### The Situation

A1R.md is apparently an internal file, and i can't simply copy-paste everything as they need reformatting (e.g. `##`) and relayouting (e.g. widow/orphan handling in real .pages)
i hence backed up its current state at `dissertation/archive/MGTK751_A1R_backup_202606192247.md` —— ensure it remains untouched NO MATTER WHAT; i already checked it currently perfectly mirrors my .pages working file
when the entire P12 is done, i'd need you to compare that backup against latest A1R.md, so you can thoroughly identify all changes made by P12 and issue #replace based on `MGTK751_A1R.pages.md` (to be created; a direct copy-paste from .pages into a .md file; the lines would be almost all broken due to layout design, hence not recommended for reading but solely for #replace so you can quote the broken lines, and so i can ⌘F in .pages which can actually catch them) for me to actually apply each of them to the working .pages file
rear to that, i'd adjust some wording for layout and my personal touch, etc.
finally, after i exported as PDF, i'd (probably in another session for this simple task) mirror to A1R.md so you see the latest state
then we can discuss whether it's truly ready to be sent to Lu

### Ops Summary

| filename | what it is | dos & don'ts |
|---|---|---|
| `MGTK751_A1R_backup_202606192247.md` | already created; backup of current A1R | read-only; never edit/delete; unbroken lines |
| `MGTK751_A1R.md` | your working file | all P12 works in here |
| `MGTK751_A1R.pages.md` | to be created by directly ⌘A my working file then copy-paste here | read-only; never edit/delete; broken lines mirroring my working file, difficult to read |
| `MGTK751 _ A1R _ [TS].pages` | my working file | never read/edit/delete |
---
simplified overview:
you do P12 on `MGTK751_A1R.md` → i rough check `MGTK751_A1R.md` → you compare `MGTK751_A1R.md` against `MGTK751_A1R_backup_202606192247.md` to identify all changes by P12 → special process (see below) → you issue #replace → i apply #replace to `MGTK751 _ A1R _ [TS].pages` → i manually polish `MGTK751 _ A1R _ [TS].pages` → i mirror to `MGTK751_A1R.md` → you identify all changes since your last edit; infer why; tell if agree → if all agreed, P12 is done
---
special process:
e.g. `MGTK751_A1R.md` has this sentence: `this is an example sentence`
your P12 changes need to add "actually" to it
so your #replace should normally be:
## Change [no.]
**Replace:**
```
[10 words before changing content]
this is an example sentence
[10 words after changing content]
```
**With:**
```
[10 words before changing content]
this is actually an example sentence
[10 words after changing content]
```
HOWEVER, since `this is an example sentence` might be broken in `MGTK751_A1R.pages.md` like:
```
this is an 
example sentence
```
the above replace block will lead to failure in finding them via ⌘F
so you should identify that sentence in `MGTK751_A1R.pages.md` then adjust accordingly:
## Change [no.]
**Replace:**
```
[10 words before changing content]
this is an 
example sentence
[10 words after changing content]
```
**With:**
```
[10 words before changing content]
this is actually an example sentence
[10 words after changing content]
```
and yes, you do not have to re-apply the line break for me (i'll do it), but only help me directly find what to replace
---

### Side Request

if feasible, help me generalise § The Situation & § Ops Summary for future projects (i.e. don't hard-code filenames) by creating `universal/replace_adv.md` (FYI: meaning advanced replace)
trigger: `#replace #adv` → which will ensure replace.md is read first; `#adv` is a modifier (inspired by sprint.md)
but unlike sprint.md, since this might be quite long, we're creating this separate file, so replace.md would needa pt to this new file by a simple line (similar to sprint.md: gotta tell if `#replace #adv` prompted → there is NO adv.md → read replace_adv.md)
.
in this new file, concisely tell the situation (which we will likely encounter again in future, not just this CP, owing to my layouting in .pages) then instr how we should handle that (you'd have to guide me; e.g. creating `MGTK751_A1R.pages.md`-equivalent file for future task as i won't remember)
so that i dont have to explain with the above long chunk again in future, streamlining our workflow

## 4
4.1: agree for now; but whenever detected new ones could be valuable, go for it via #cic (not now)
4.2: i would lightly push back: first, i dont think she will notice that even if we don't remove it as it's just unchanged; second, if you do that, all TP/mgr samples can't be used, which can undermine sample size & even lead to failure in reaching the 6pax target; third, they yield truly valuable insights and indeed come to my own academic interests, so i dont think we should simply kill those opportunities solely because her short, soft, non-mandatory, suggestion/advice-like comment
4.3: agree, do it reasonably

## 5
5.1: "critical path" is usually a series of items (CIIW); i assume you meant the most critical item that requires my intervention (that you can't do independently) is P12.2; if true, you may now (if no qb) create a .svg so i can create in .pages based on that; put it in `dissertation/` following filename convention

## Sprinting
im planning to #sprint for the remainder of tasks (exc. P12.2 & other named steps that requires my manual ops; e.g. working w/ .pages), except P12.7 as i needa finalise first (P12.6: still do for your working file A1R.md; then again after i manually finalised + updated A1R.md)
before starting (assuming i'll prompt `#sprint P12` in next turn), briefly tell your plan in 100w (still #numbered)
then raise only most critical QB that you already know/expect

## Reminder
DevPlan P06–P11 still in full (not stubbed), which doesn't matter to you as they're already in context
but they do matter in new session (unnecessary context consumption)
so if we still haven't stubbed them when i prompt `#close` (not now), remind me to do that FIRST, before carrying on to `#close`

## Your Missions
- Execute actions if any explicitly instructed & no qb
- Tell your thoughts on all above (don't miss any)
- Reminder: no chat text; don't start `#sprint` yet