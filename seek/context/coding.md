When I prompt `#replace`, you MUST NOT generate full content OR update previous artefacts, but quote existing snippet VERBATIM (NEVER "after xxx block", "in xxx function", etc.) to replace, e.g. to add `123` between lines `xxx` & `yyy` you should print (use code blocks for the snippets):

```
## Change 01
**Replace:**
```
xxx
yyy
```
**With:**
```
xxx
123
yyy
```
```

In actual practice, `xxx` `yyy` are immediate THREE LINES above/below the line(s) being changed, i.e. in each snippet, between the first/last 3 lines MUST be the content being changed. Strictly ensure ENTIRE text blocks in respective snippets; i.e. from `xxx` all the way to `yyy` in above example, don't leave any outside (e.g. `yyy`).