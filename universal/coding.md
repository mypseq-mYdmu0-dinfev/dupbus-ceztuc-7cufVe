# Coding

- Before beginning to generate scripts, check all necessary pre-requisites such as setting venv and installing libraries if needed
- Do not expect me to edit codes; always ask for input/output file paths if not yet aware in the chat/CP context
- Default output path: `/Volumes/FURY 2TB/Fury Downloads`
- When I prompt `#replace` or when editing codes with more than 1,000 lines, do not generate full content/script but quote existing snippet VERBATIM (NEVER "after xxx block", "in xxx function", etc.) to replace, e.g. if you want to add `123` between lines `xxx` & `yyy` you should print (in markdown artefact with codes in snippets):

```
## Change 01
**Replace:**
` ` `
xxx
yyy
` ` `
**With:**
` ` `
xxx
123
yyy
` ` `
```

In actual practice, `xxx` `yyy` are immediate THREE LINES above/below the line(s) being changed, i.e. in each snippet, between the first/last 3 lines MUST be the codes being changed.