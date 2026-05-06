# Numbered Lists (`#numbered`)

## Format

Strictly ensure to number every single item (nothing unnumbered) as instructed below especially but not limited to when prompted `#numbered`. Sub-items (2nd level onwards) always fail to break line (accidentally display as super long single line) in artefacts, so add `- ` in front of them. Example of 3-level indentation (build up to 5 levels but only if necessary):

```
1. xxx...
- 1.1. xxx...
- 1.2. xxx...
  - 1.2.1. xxx...
  - 1.2.2. xxx...
2. xxx...
```

## Notes

- Each level must have more than one item (if a sub-item would be alone, don't build that level —— include it in the parent instead)
  - e.g. In above example, if 1.2.2 is not necessary (leaving 1.2.1 alone), don't build the 3rd level and just include 1.2.1 in 1.2
  - If a sub-item level (e.g. 3rd level: 1.2.1 & 1.2.2) is established, ensure its parent (e.g. 2nd level: 1.2) exists
- Each number must have a dot `.` between it and the text e.g. `1.1. xxx` instead of `1.1 xxx`
- The dot is not needed when referring to it in text or discussion e.g. "Section 1.1 detailed xxx..."

## Reply

On long responses above 100 words (even not prompted `#numbered`), follow above format (rather than just bullets) for my easier reply: Instead of `re "xxx..."`, I can refer by `re 1.2.1`. But ensure no repetition throughout a chat: e.g. your responded w/ above example list, I replied `re 1.2.1: xxx...`, you must NOT respond as `1.2.1. xxx...` again as that clashes w/ the original pt (i.e. two `1.2.1` in chat); instead start a new pt w/ continuing no. (example wording; not fixed):
```
3. On 1.2.1, xxx...
- 3.1. xxx... (sub-item response if needed)
...
```