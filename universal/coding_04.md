# Coding

- Before beginning to generate scripts, check all necessary pre-requisites such as setting venv and installing libraries if needed
- Do not expect me to edit codes; always ask for input/output file paths if not yet aware in the chat/CP context
- Default output path: `/Volumes/FURY 2TB/Fury Downloads/`

## Large File Edit

When I prompt `#replace` or editing a file w/ 50⁺ lines of codes/500⁺ words of text, you MUST NOT generate full content OR update previous artefacts, but quote existing snippet VERBATIM (NEVER "after xxx block", "in xxx function", etc.) to replace, e.g. to add `123` between lines `xxx` & `yyy` you should print (ALWAYS in a `text/markdown` artefact, NEVER a code-type artefact; use code blocks for the snippets):

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

In actual practice, `xxx` `yyy` are immediate [code:] THREE LINES above/below the line(s) being changed OR [text:] TEN WORDS before/after the word(s) being changed, i.e. in each snippet, between the first/last [code:] 3 lines OR [text:] 10 words MUST be the content being changed. Strictly ensure ENTIRE text blocks in respective snippets; i.e. from `xxx` all the way to `yyy` in above example, don't leave any outside (e.g. `yyy`).

## Large Proportion Edit

If replacing 80%⁺ content of a file, DON'T #replace but generate full file in a new (separate) artefact:
- If other #replace warranted —— `## Change [no.]<br>**Replace [filename] with [separate_artefact_number]**`
- If no other #replace —— Chat text (override): `Fully replaced.`; no #replace artefact needed