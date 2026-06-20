# Advanced Replace (`#replace #adv`)

*Trigger: `#replace #adv`. `#adv` is a modifier —— there is NO `adv.md`; read `replace.md` (base rules) first, then this file.*

## The Situation (why this exists)

A deliverable is authored and finalised by the user (e.g. in .pages) where the user manually polishes layout —— widow/orphan, deliberate line breaks, kerning. Instead of editing that layout file (inefficient), CC works on a plain-text `.md` mirror. When porting CC's edits into the layout file, the user applies them by ⌘F (find) in the layout app. Problem: a direct copy-paste out of the layout app carries HARD line breaks mid-sentence, so CC's normal `#replace` snippet (unbroken prose) will not ⌘F-match. This recurs whenever the user's true deliverable lives in a layout app.

## Four Artefacts (per deliverable)

| Role | Naming pattern | CC may | Notes |
|---|---|---|---|
| Working file | `<name>.md` | read + edit | where all CC edits land |
| Pre-edit backup | `<name>_backup_[TS].md` | read only | read-only snapshot of the working file taken BEFORE the edit batch; never edit/delete; used to diff and enumerate changes |
| Layout mirror | `<name>.pages.md` (or `.[original_format].md`) | read only | a direct ⌘A copy-paste of the layout file; lines are broken/wrapped, hard to read; exists SOLELY for CC to quote the broken form for ⌘F |
| Layout file | `<name>.pages` / `.docx` | none | the user's real deliverable; CC never reads/edits |

## Workflow

1. **Setup (user, once, before CC starts editing):** snapshot the working `.md` as `<name>_backup_[TS].md` (read-only). Tell CC the backup filename.
2. **Edit (CC):** make all edits on the working `.md` as normal.
3. **Handoff (user, after CC finishes the batch):** ⌘A-copy the current layout file into a fresh read-only `<name>.pages.md`. Tell CC the filename.
4. **Diff (CC):** compare `<name>_backup_[TS].md` against the finished working `.md` to enumerate every change made in this batch.
5. **Emit `#replace` (CC):** for each change, locate the target text in `<name>.pages.md` (where it may be split across lines) and quote the BROKEN form verbatim in the `Replace:` block, so the user can ⌘F-find it in the layout file. The `With:` block holds the corrected text; CC does NOT re-apply line breaks (the user re-breaks for layout).

```
## Change [no.]
**Replace:**            ← quote the BROKEN lines from <name>.pages.md
this is an
example sentence
**With:**               ← corrected text, unbroken; user re-breaks
this is actually an example sentence
```

6. **Apply (user):** ⌘F each broken snippet in the layout file, apply, polish layout/wording, export PDF, then mirror the final back into the working `.md`.
7. **Verify (CC):** diff the mirrored working `.md` to confirm the final state before any send/use.

## Notes

- Keep the standard 10-words-before / 10-words-after context (per `replace.md`) AROUND the broken target, so each snippet is unique.
- If a target is NOT broken in the mirror, a normal `#replace` snippet suffices —— only break-match where the mirror actually breaks.
- If the user has not yet created the backup or the layout mirror, ask for them before emitting `#replace #adv` (the workflow cannot proceed without both).
