# Full Text Summary (FTS)

When I prompt `FTS`, apply this prompt for the provided URL (or the open web page in Comet browser):

Concisely summarise this web page:
- always (along entire chat) comply with ALL custom instructions below (not just this `FTS` snippet), including but not limited to British English, conversion to SYD timezone, `Mn` instead of `m`, and Hart's quotation rule
- use bold/sections/bullet pt
- never reveal imperial units whatsoever
- IMPORTANT: close with synthesising key insights/takeaways for me (see context below)

Start with `**Full Text Parsed: Yes/No**` by **fetch_url** on exact URL
- **Return `Yes` if:**
  - the fetch tool doesn’t have **“TRUNCATED”** flag/note, **and**
  - the page has no obvious paywall, login gate, or “content not available to bots” placeholder, **and**
  - you can reliably extract **both first and last words** (`culousyu.com` is a “Yes” example).
- **Return `No` if:**
  - any “TRUNCATED” from fetch_url results (if fetch_url is clean but search_web returns TRUNCATED, it still doesn’t contribute to “No”), **or**
  - the content is an article (e.g. ABC, Guardian) but looks like a skeleton (empty article, scripted shell, or clearly blocked bot view).
- If and only if `Yes`, print first/last 10 words then proceed to summarise only the site’s own content, never fabricate or insert external content.
- If `No`: Tell approx word count of result from fetch_url alone (not search_web), if and only if it’s 100+, proceed accordingly.
- If I send text (100+ words) after `No`, consider it full text and run `FTS` again