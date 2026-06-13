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

## Deliverable Lint —— `cscript/dlint.py` (MANDATORY)

- After creating ANY deliverable (separate file OR embedded in `response_`; any style above), you MUST lint it before finalising: `python3 cscript/dlint.py <deliverable_path>`
  - Run on the deliverable TEXT ONLY, NEVER on a `response_`/comms file (those legitimately use ` —— `, colons, etc.)
  - Long deliverable = its own file (per root §3.7.2) → lint that file directly
  - Short deliverable embedded in `response_` → extract to a temp file beside the `response_`, lint it, paste back when clean, then VOID the temp (Void Rule)
- It auto-fixes straight quotes → typographic in place, then prints two flag tiers:
  - 🔴 RED (hard breaches: em/en-dash punctuation, banned Americanisms per root §2.1.1, mid-sentence colons) —— you CANNOT proceed until RED = 0; rectify then rerun, LOOPING until clean
  - 🟡 YELLOW (conditional: bare `+`, spaced hyphen, sentence-initial `Where`, GenAI/cliche words & phrases) —— you MAY proceed with yellows remaining ONLY IF you concisely JUSTIFY each in `response_` (e.g. `+` is part of `iCloud+`)
- Lists in `dlint.py` are seeded from this file + root `CLAUDE.md`, not exhaustive; the script does not replace your own judgement on rules it cannot lint (verb-object separation, ≥3-object Oxford comma, Hart's quotation)

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
- Avoid common GenAI words including but not limited to (unless literally meaning that e.g. "elevate" in context of elevator/lift, or it's a trademark/conventional term e.g. "command" key of mac): elevate, captivate, tapestry, delve, leverage, resonate, embark, unleash, plethora, myriad, utilise, paradigm, landscape, evolving, nuanced, perspective, comprehensive, supercharge, dynamic, elucidate, holistic, synergy, pivotal, robust, aid, beacon, bolster, breeze, churn, command, crack, crucial, employ, enable, encourage, ensure, evoke, enhance, entices, essential, gaze, facilitate, forge, fortify, inundated, ignite, imperative, instrument, instills, navigate, irresistible, master, material(ly), paramount, promptly, realm, soar, revolutionize, safeguard, cutting-edge, triangulate(ion), enumerate(ion), substantive, persuasive, sparks, streamline, uncover, vast, journey, seamless, adhere, supercharge, evolve, beyond, bustling, enigma, It is important to note that..., Master the art of..., In summary/conclusion..., A testament to..., In the dynamic world of..., A tapestry of..., Delve into..., Embark on a journey..., A treasure trove of..., An ongoing voyage of, As we conclude, Captivating narrative, Encountered hurdles, Ever-evolving, Game-changer, Golden ticket, In a sea of, Let it shine through, On the ascent to, Reaching new heights, Seize the, To furnish, To thrive, Uncharted waters, Well-crafted
- Briefly use web_search to fetch latest common GenAI words, since the above could be dated

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