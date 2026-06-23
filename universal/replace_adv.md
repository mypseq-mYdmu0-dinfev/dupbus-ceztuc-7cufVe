# Advanced Replace (`#replace #adv`)

*Trigger: `#replace #adv`. `#adv` is a modifier —— there is NO `adv.md`; read `replace.md` (base rules) first, then this file.*

## The Situation (why this exists)

A deliverable is authored and finalised by the user (e.g. in .pages) where the user manually polishes layout —— widow/orphan, deliberate line breaks, kerning. Instead of editing that layout file (inefficient), CC works on a plain-text `.md` mirror, and the user ports CC's edits back by ⌘F (find) in the layout app. **The trap:** a copy-paste out of the layout app carries every layout line-break as a `U+2028` character (Pages soft-return), and **the layout app's ⌘F cannot match any string that contains a `U+2028`** —— confirmed empirically (even copying a 2-line run straight out of .pages and pasting it into that same app's Find fails to match). A `Replace:` target therefore can NEVER span a line-break; it must be quoted as break-free blocks the user CAN ⌘F-find. This recurs whenever the user's true deliverable lives in a layout app.

## Four Artefacts (per deliverable)

| Role | Naming pattern | CC may | Notes |
|---|---|---|---|
| Working file | `<name>.md` | read + edit | where all CC edits land |
| Pre-edit backup | `<name>_backup_[TS].md` | read only | read-only snapshot taken BEFORE the edit batch; never edit/delete; diff against it to enumerate changes |
| Layout mirror | `<name>.pages.md` (or `.[fmt].md`) | read only | a direct ⌘A copy-paste of the layout file; carries the `U+2028` breaks; exists SOLELY for CC to read exact break positions and split each `Replace:` |
| Layout file | `<name>.pages` / `.docx` | none | the user's real deliverable; CC never reads/edits |

## Workflow

1. **Setup (user/CC, once):** snapshot the working `.md` (user must have verified it syncs w/ the layout file) as `<name>_backup_[TS].md` (read-only; optional: in an `archive/` of CP) BEFORE further edits.
2. **Edit (CC):** make all edits on the working `.md` as normal.
3. **Handoff (user, after the batch):** ⌘A-copy the current layout file into a fresh read-only `<name>.pages.md`. Tell CC the filename.
4. **Diff (CC):** compare the backup against the finished working `.md` to enumerate every change.
5. **Emit `#replace` (CC):** for each change, take the target's exact text from `<name>.pages.md` and split it at its `U+2028` breaks into break-free `Replace:` blocks (see § Splitting). Extract programmatically —— the breaks are invisible-ish, so never retype. The single `With:` block holds the corrected text, breaks stripped (the user re-breaks for layout). `cscpt/padv.py` automates the extract-and-split.
6. **Apply (user):** ⌘F the break-free block(s) in the layout file (for a multi-block target, find the first and last blocks and select across), apply, polish layout, export PDF, then mirror the final back into the working `.md`.
7. **Verify (CC):** diff the mirrored working `.md` to confirm the final state before any send/use.

## Splitting a `Replace:` (because ⌘F cannot cross a `U+2028`)

Quote each target as break-free blocks, MAX 3:

- **0 breaks** —— ONE block (a normal `#replace`).
- **1 break** —— TWO blocks: [1] text before the break; [2] text after it. The user ⌘F-finds both, selects across them, replaces.
- **≥2 breaks** —— THREE blocks (never more): [1] before the FIRST break; [3] after the LAST break; [2] everything between, with its internal breaks cancelled into one running line (reference only). The user ⌘F-finds blocks 1 and 3, selects from first to last, then replaces; block 2 just shows what sits between for visual confirmation.

Each block is its own fenced snippet; the `With:` block stays single and unbroken. Example (1 break):

```
## Change [no.]
**Replace** (1 break → 2 blocks; ⌘F both, select across, replace):
   [block 1]  the sentence up to where the layout
   [block 2]  wraps onto the next line
**With:**
   the corrected sentence, unbroken (the user re-breaks for layout)
```

## Notes

- Per block, keep enough unique context (≈10 words, per `replace.md`) so each ⌘F lands exactly once.
- A target with no `U+2028` needs no splitting —— one block, as normal.
- If the user has not yet created the backup or the layout mirror, ask for them before emitting `#replace #adv` (the workflow needs both).