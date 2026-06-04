# Numbered Lists (`#numbered`)

*`CC:` = for Claude Code only, disregard if you're not.*

## Format

Number every single item as below especially but not limited to when prompted `#numbered`. As shown, sub-items (2nd level onwards; e.g. `- 1.1. xxx...`) MUST follow bullets to prevent line break failure (displaying as single line; `1. xxx... 1.1. xxx...`).

## Example List

e.g. 4-level indentation (build up to 5 levels but only if necessary):

```
1. xxx...
- 1.1. xxx...
- 1.2. xxx...
  - 1.2.1. xxx...
    - 1.2.1.1. xxx...
    - 1.2.1.2. xxx...
  - 1.2.2. xxx...
2. xxx...
```

## Notes

- Each level MUST have more than one item
  - If a sub-item would be alone, don't build that level —— include it in the parent instead
  - e.g. In above example, if 1.2.1.2 is not necessary (leaving 1.2.1.1 alone), don't build the 4th level and just include 1.2.1.1 in 1.2.1
  - If a sub-item level (e.g. 4th level: 1.2.1.1 & 1.2.1.2) is established, ensure its parent (e.g. 3rd level: 1.2.1) exists
- Must use hardcoded manual numbering, never markdown auto-numbering
- Strictly ensure NO sentence/bullet/line unnumbered e.g. `- xxx...`
- Each number must have a dot `.` between it and the text e.g. `1.1. xxx` instead of `1.1 xxx`
- The dot is not needed when referring to it e.g. "Item 1.1 detailed xxx..."

## Reply

- On long responses above 100 words (even not prompted `#numbered`):
  - Follow above format (rather than unnumbered bullets) for **easy reply**
  - Instead of `re "xxx..."`, I can refer by `re 1.2.1` or just `1.2.1:`
- Numbering Continuity —— No number repetition throughout an issue, reset to pt 1 only if:
  - 1st response of a session (CC: despite referring to prev. `/sessions/` files); or
  - User input is NOT replying a response (CC: the word `response_` AND any pt no. from previous `response_` were NOT found in `query_`); or
  - Snippets; or standalone/non-response outputs (e.g. codes, deliverables; CC: not `response_`)
- Let's say you responded w/ § Example List, my input: `1.2.1: xxx...` (i.e. replying a response)
  - You must NOT respond as `1.2.1. xxx...` again as that clashes w/ the original pt in last response, i.e. two counts of `1.2.1` on same issue
  - Instead start a new pt w/ continuing number (n+1), where n = last pt in last response
  - § Example List ends w/ pt 2, so next response starts w/ pt 3:

```
3. Re 1.2.1, xxx...
- 3.1. xxx... [sub-items if needed; no line can be unnumbered]
- 3.2. xxx...
...
```