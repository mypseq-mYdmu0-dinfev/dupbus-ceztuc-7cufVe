# CIC —— Claude in Chrome

CIC = Claude in Chrome (Claude's connector/Chrome's extension), accessible via either interfaces:

- **BCIC** = Browser-CIC, Chrome's sidebar chat; very rarely used
- **CCIC** = Code-CIC, used by CC; the **default** means
- CC: default CIC=CCIC; actively consider spawning SA to save context if feasible (judge; e.g. [SA briefing + SA return to main] < [direct CIC output to main])

---

## Mandate —— when `#cic` is prompted (or any high-stake validation)

- When `#cic` is prompted you **MUST** validate via CIC by reading the actual live web page. `web_search` and the **CrossRef API are TRIAGE ONLY** —— they locate and target candidates and NEVER confirm. NOTHING they surface may be cited in a deliverable, added to non-`response_` files (e.g. `RefRepo.md`), or relied on for any claim until CIC has read the live source. NEVER cite or add a source on a `web_search`/CrossRef result alone.
- Scope: whenever `#cic` is prompted, OR on any high-stake task —— adding a NEW source, citing in a deliverable, or validating a statistic/figure/edition.
- Why firm: a Crossref-only citation once entered the deliverable with the wrong volume; only CIC's live read caught it. Triage ≠ confirmation.

---

## When to Suggest CIC

- CC: DON'T suggest; DIRECTLY go for it whenever applicable (false-positive leaning); CIC is always available for you, otherwise directly open Chrome by yourself.
- Non-CC: When we're on high-stake tasks requiring validation OR repetitive/lengthy tasks requiring minimal human intervention, briefly suggest me to use CCIC if we need **accuracy** beyond web_search. If user is OTG (CIC is N/A), fall back to web_search & alert for inaccuracy.

---

## Pre-CIC Protocol

Before any CIC operation, always run `web_search` first:
- Surface as many candidate sources as possible; pass **valid candidates only** (inc. full URLs) into the CIC prompt as a starting pt to narrows CIC's scope & speed up execution
- **Valid** = directly relevant to the task + from an authoritative source, regardless of whether it confirms or contradicts the hypothesis
- **Invalid** = irrelevant, low-quality, or adds no substantive value
- web_search output is triage only, never confirmation; CIC must validate every passed source by actually visiting (web_search can misrepresent, surface outdated content, or miss paywalls)
- If valid+invalid candidates are fewer than 5, CIC may also give a quick pass on invalid sources, prioritising borderline ones over clearly off-topic ones
- CIC should also search for additional sources beyond the list as needed
- web_search returning no results ≠ CIC will also find nothing —— worth CIC trying regardless
- If any candidates are PDF + no equiv/similar web ver found: DON'T use BCIC (can't handle files); pivot to CCIC → ensure PDFs are downloaded (not opened in a Chrome tab)
- On academic, use the most efficient authoritative means (e.g. G Scholar); take the UoL/UTS Library as fallback when public sources paywall —— follow `universal/cic_libs.md` for Library entry points and full-text steps (NB Library access lapses after 2026, MBA graduation)

---

## Drafting for BCIC

When drafting a BCIC prompt, ensure it's concise yet succinctly detailed (same for BCIC's response), just enough for BCIC & you to understand each other. For CWI-BCIC exchange, **neglect** all language/glossary conventions (e.g. mentioning `CIC`, using ` `~` ` instead of `-`) since BCIC has no context at all (e.g. userPref, CP instr; i.e. don't follow notes.md/glossary.md, only use common abbrev).

---

## Bot Blocks —— CAPTCHAs & Anti-Automation

Some sites (esp. e-commerce —— Temu, Taobao, etc.) run bot-detection that trips on AUTOMATION SIGNALS, not on you personally. Symptoms: a "Security Verification" CAPTCHA (slide-puzzle / rotate-objects / pick-the-image), or CDP calls that simply HANG (300s timeouts).

- TRIPS the wall (avoid on these sites): navigating by direct URL straight to a product/deep page; `javascript_tool` DOM-scraping; `get_page_text`/`read_page` on a bot-sensitive listing; any fast scripted interaction.
- WORKS (slow but effective —— behave like a human): use the `computer` tool —— `navigate` only to the site's HOMEPAGE, type into its OWN search box, then `screenshot` and human-`left_click` the product cards. Let the site open the product in a new tab itself; it joins the MCP tab group and is fully controllable. Verify each opened page with a screenshot.
- NEVER solve a CAPTCHA (prohibited bot-bypass). Its X usually just cycles a fresh one. If a site still CAPTCHAs or hangs despite human-like clicks, STOP on that site, leave its SEARCH tab open, and list the picks for the user to click —— a human clears the wall in one go.
- DEFAULT, on bot-sensitive shopping sites, to the slow screenshot + click path FROM THE START; it beats fast scripted access, which only wastes time on CAPTCHAs and 300s hangs.
- Proven (Jun 2026): Temu —— direct product-URL + `javascript_tool` = CAPTCHA, but homepage → search-box → human-CLICK opened products cleanly with no wall. Taobao (even logged-in) —— every CDP op (click, JS, `get_page_text`, even `screenshot`) hangs 300s; treat as unusable by automation and hand its home/search tab to the user. CONFIRMED: a FRESH tab + homepage + human-like clicks still hung on the very FIRST click (the tab never even left the homepage) —— Taobao detects the CDP/automation channel ITSELF, not behaviour, so the human-like trick that beats Temu does NOT work here. Don't burn 300s retrying it; load the homepage for the user and stop. Search engines can't rescue it either —— Alibaba blocks indexing of Taobao/Tmall ITEM pages (a Baidu `site:detail.tmall.com` query returns nothing; Google returns no item links), so the "find an item URL via Google/Baidu and navigate to it" fallback also fails. Conclusion: only the human can open Taobao/Tmall items —— don't sink time into it.

---

## IMPORTANT

If I request to use CIC, you MUST use CIC instead of `web_search` alone or drafting a BCIC prompt. Enforced throughout session unless instr otherwise. If failed, stop & alert (no fallback).