# Writing Rules

## General (all writing styles)

- NEVER use em dash `—` for ANY deliverables, only OK for internal use between you and me
  - When removing a banned dash, RESTRUCTURE the whole sentence —— NEVER a mere comma/colon swap. The dash carries emphasis the rest of the sentence must then absorb, so a direct substitution reads oddly. (`dlint.py` reprints this on every dash flag)
- NEVER use colons `:` in sentences (e.g. replacing dash) as it still breaks the narrative; only OK when followed by a list AND when listing per se is context-appropriate
- Avoid sentence/clause-initial "Where" (e.g. "Where [condition], [statement]"); prefer "whilst/since/as/owing to/etc." OR restructure like "[Statement], where [condition]" etc.
- Avoid verb-object separation: Don't place long descriptive or prepositional phrases between a transitive verb (e.g. identify, state, argue) and its direct object or quotation
  - ❌ e.g. [Actor] identifies [long_descr] "[quote]".
  - ✅ e.g. [Actor] identifies "[quote]" as [long_descr].
- On ≥3 objects:
  - ❌ [A], [B] and [C]
  - ✅ [A], [B], and [C]
- When drafting anything est. 1,000⁺ words, suggest (ask confirmation) to create Dev Plan

---

## Deliverable Lint —— `cscpt/dlint.py` (MANDATORY)

- After creating ANY deliverable (any style above), you MUST lint it before output —— RUN it (never read it; read only its terminal output). MODES:
  - Separate-file deliverable (per root §3.7.2) → `python3 cscpt/dlint.py <path>` (FULL; auto-fixes quotes in place)
  - Short deliverable embedded in `response_` → EXTRACT it and `python3 cscpt/dlint.py --text "the deliverable text"` (FULL; prints the quote-fixed text to paste back; no temp file)
  - NEVER lint the whole `response_`/comms files in FULL mode, as they legitimately use ` —— `, colons, etc. (the `--quick` all-output check is governed by root §3.5.5 + its hook, not here)
- It auto-fixes straight quotes → typographic, then prints two flag tiers (exact rules live in the script):
  - 🔴 RED (hard breaches) —— zero tolerance: you CANNOT proceed until RED = 0; rectify then rerun, LOOPING until clean
  - 🟡 YELLOW (conditional) —— you MAY proceed with yellows remaining ONLY IF you concisely JUSTIFY each in `response_`
- This script does NOT replace your judgement on rules herein, especially those it cannot lint deterministically (e.g. verb-object separation, Oxford comma)

---

## Casual Writing

When "casual"/"whatsapp"/"draft a text/msg" explicitly mentioned (if implicitly detected, confirm first):
- Ensure all lower case (e.g. `i am` instead of `I am`) except abbreviations (e.g. `EPS` `ATO`)
- Keep punctuation (e.g. `i'm` `he's`)
- Be extra "human" with more friendly tone in simple wordings
- Never using periods `.` and just start a new line (like `<br>`)
- When prompted "convert to whatsapp/WA":
  - Format Bold: **text** → *text*
  - Format Italic: *text* → _text_
  - Don't format the rest (monospace ``, list -, quote >, etc.; identical to markdown)

---

## Professional Copywriting

- When "copywriting" (explicit keyword or context detected), use sophisticated, witted British English, adept copywriter tone & manner w/o any abbreviations like `I'm` (LinkedIn may abbreviate if appropriate). 
- Remember #rules (CC: root CLAUDE.md)
- STRICTLY eliminate em dash `—`; en dash `–` ONLY for range (e.g. `1–2`)
- Use broader range of vocabulary (e.g. avoid cliche terms like `significant` `demonstrate`, use `empower` rather than `enable` when applicable)
- Avoid repeating same wording more than once every 1,000 words
- Avoid common GenAI/cliche words & phrases (e.g. tapestry, seamless, myriad, pivotal; "It is important to note...", "A testament to..."), UNLESS literally meant (e.g. "command" key) or a trademark/conventional term
  - `cscpt/dlint.py` enforces the full, growing list (run-not-read)
  - Briefly web_search latest GenAI words (above could be dated)
  - If a word was user-added (NOT by you) then yellow-flagged, don't rectify it but notice ONCE

---

## Academic Writing

When drafting academic works (especially but not limited to when I mention `cite`/`citation`), follow above copywriting rules AND always ensure in-text citations (either as sentence subject or bracketed item) with Harvard style reference list at the end of text using reputable sources (NO Wikipedia), for example:

```
... XXX is XXX (Smith, 2020). Smith (2020) indicated ...
[word_count]
References:
Smith, J.A. (2020) *Source Title*. Available at: https://www.example.com/ (Accessed: 01 May 2020)
```

- Word count MUST be retrieved by `echo "your text" | wc -w` (per glossary.md §Special)
- If multiple cited sources from identical author AND year, use `[author], [year]-[a/b/c]`
  - e.g. "NASA (n.d.-a) found... and XXX... (NASA, n.d.-b)."