# Writing Rules

## General (shared by all writing manners)

- NEVER use em dash `—` for ANY deliverables, only OK for internal use between you and me
  - When removing dash, RESTRUCTURE whole sentence —— NEVER mere comma/colon swap
  - Dash carries emphasis the rest of sentence must then absorb; direct substitution reads oddly
- NEVER use colons `:` in sentences
  - e.g. replacing dash —— It still breaks the narrative
  - Only OK when followed by a list AND when listing per se is context-appropriate
- Writing should read fluently ALOUD if possible (esp. `#style`), not just scan well visually
  - If sounds awkward spoken, try to restructure it even if it reads fine on the page
  - Avoid sentence/clause-initial "Where" (e.g. "Where [condition], [statement]"): prefer "whilst/since/as/owing to/etc." OR restructure like "[Statement], where [condition]" etc.
  - Avoid verb-object separation: Don't place long descriptive or prepositional phrases between a transitive verb (e.g. identify, state, argue) and its direct object or quotation
    - ❌ e.g. [Actor] identifies [long_descr] "[quote]".
    - ✅ e.g. [Actor] identifies "[quote]" as [long_descr].
- Use Oxford comma on ≥3 objects:
  - ❌ [A], [B] and [C]
  - ✅ [A], [B], and [C]
- When drafting anything est. 1,000⁺ words, suggest (ask confirmation) to create Dev Plan
- Never use "Hi" (culturally impolite)
  - Vary the salutation to taste instead
  - e.g. "Hello", "Greetings"; no fixed alternatives
- Never open with recipient's name ALONE as 1st word (e.g. ❌ "Sam, ...")
  - The interface (email/DM thread) already reveals
  - Bare name-first opener reads artificial in writing, unlike face-to-face speech where it's natural
  - Open directly with content (non-email) or use "[greeting_word] [Name] ..." (e.g. "Long time no see, Sam. [content]", "Morning Sam, [content]")
  - Group Chats: if needed, use `@` (e.g. "@Sam, ... as @Amy said ...")
- Avoid english numbers (except "one"), use numerals instead (easier human reading):
  - ❌ e.g. I use 1 tool to save two minutes.
  - ✅ e.g. I use one tool to save 2 minutes.
  - Except § Casual Writing (e.g. "3rd"), use english number for ordinals (e.g. "third").
- Grammar must be stringently correct by default in deliverables
  - Zero tolerance for sloppiness
  - Flex only when the user self-applies & explicitly insists on it
  - e.g. a deliberate touch of imperfection to sound more "human"
- Prefer precise, stronger wording over weak/unsophisticated words
  - e.g. "believe" rather than "feel"/"want", unless literally a physical sensation like cold/warm
  - `dlint.py` flags `want`/`something`/`big` as concrete always-avoid cases (🟡, not banned —— insist through a mis-flag when context genuinely calls for the plain word, e.g. § Casual Writing)
- Front-load content (the what/why/how) to pre-empt the need for a follow-up meeting/call
  - User strongly avoids verbal exchange; user's comms pref ([pref%]; [concerns]):
    - WhatsApp/Instant Msg (100% preferred; none)
    - Email (90%; wait times, cyber risks)
    - Virtual Meeting (varies; synchronous exchange, schedule clash)
      - Zoom (80%; none additional)
      - Teams (60%; interface/access bugs)
      - G Meet (55%; unacceptable transcription quality)
    - Physical Meeting (50%; fuel/toll costs, stamina, small talks, inefficiency)
    - Phone Call (0%; sound quality, ineffectiveness, unknown calls default-blocked)
  - Never state this pref explicitly, but let completeness & clarity do the work instead
  - e.g. DON'T write "happy to continue this by writing" NOR "a meeting/call would suit us"
- Pre-empt accusation or push-back before it lands
  - Word strategically so neither party is left holding an easy grievance against the other
  - e.g. ❌ "I cannot attend but would not miss it next time" → ✅ "... would avoid missing it ..."
- Length follows context, not a fixed target
  - Short email/text may attach PDF for details
  - PDF may split as executive summary +body
  - Only when situation truly warrants fuller record (e.g. formal complaint), never as padding
  - Judge by case; e.g. a word-limited job application question cannot use this
- Avoid repeating the same wording more than once every 1,000 words
  - If unavoidable (e.g. proper noun/company name recurring throughout), consider introducing occasional variety where natural (e.g. "the firm" instead of the full name each time)

---

## Deliverable Lint —— `cscpt/dlint.py` (MANDATORY)

- After creating ANY deliverable (any writing manners), you MUST lint it before output —— RUN it (never read it; read only its terminal output). MODES:
  - Separate-file deliverable (per root §3.7.2) → `python3 cscpt/dlint.py <path>` (FULL; auto-fixes quotes in place)
  - Short deliverable embedded in `response_` → EXTRACT it and `python3 cscpt/dlint.py --text "the deliverable text"` (FULL; prints the quote-fixed text to paste back; no temp file)
- NEVER lint the whole `response_`/comms files in FULL mode, as they legitimately use ` —— `, colons, etc.
- The `--quick` all-output check is governed by root CLAUDE.md §3.5.5 + its hook, NOT here
- It auto-fixes straight quotes → typographic, then prints two flag tiers:
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

---

## Stylisation

- There's no `style.md`
- `#style` is a MODIFIER of whichever manner is active (Casual/Professional/Academic)
- Changes HOW that manner is executed
  - Doesn't swap to a different manner
  - Never suspend that manner's own rules
- Self-determine whether to escalate to a stylised ver when EITHER:
  - `#writing` prompted w/o `#style` (Case 1)
  - Deliverable self-detected, w/o either being prompted (Case 2)
- MUST escalate when `#writing #style` is explicitly prompted (Case 3)
- Read `universal/writing_style.md`:
  - Case 3 —— read immediately
  - Case 1/2 confidently decided YES —— read immediately
  - Case 1/2 genuinely unclear/half-committed —— read anyway, as a nudge to help decide
  - Case 1/2 confidently decided NO —— skip the read, no need to know what styles exist