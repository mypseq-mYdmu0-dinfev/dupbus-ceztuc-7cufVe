# CIC —— Claude in Chrome

CIC = Claude in Chrome (Claude's connector/Chrome's extension), accessible via either:

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

- CC: DON'T suggest; DIRECTLY go for it whenever applicable (false-positive leaning); CIC should be always available for you, otherwise directly open Chrome by yourself.
- Non-CC: When we're on high-stake tasks requiring validation OR repetitive/lengthy tasks requiring minimal human intervention, briefly suggest me to use CCIC if we need **accuracy** beyond web_search. If user is OTG (CIC is N/A), fall back to web_search & alert for inaccuracy.

---

## IMPORTANT

If I request to use CIC, you MUST use CIC instead of `web_search` alone or drafting a BCIC prompt. Enforced throughout session unless instr otherwise. If failed, stop & alert (no fallback).

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
- If any candidates are PDF + no equiv./similar web ver found: DON'T use BCIC (can't handle files); pivot to CCIC → ensure PDFs are downloaded (not opened in a Chrome tab)
- On academic, use the most efficient authoritative means (e.g. G Scholar); take the UoL/UTS Library as fallback when public sources paywall —— follow `universal/cic_libs.md` for Library entry points and full-text steps (NB Library access lapses after 2026, MBA graduation)

---

## Drafting for BCIC

When drafting a BCIC prompt, ensure it's concise yet succinctly detailed (same for BCIC's response), just enough for BCIC & you to understand each other. For CWI-BCIC exchange, **neglect** all language/glossary conventions (e.g. mentioning `CIC`, using ` `~` ` instead of `-`) since BCIC has no context at all (e.g. userPref, CP instr; i.e. don't follow notes.md/glossary.md, only use common abbrev).

---

## Bot Blocks & Logins —— escalation ladder (generalise; site notes are just examples)

When a site gates automation (a CAPTCHA appears, or CDP calls HANG ~300s), don't give up or fail silently —— escalate cheapest→costliest:
1. EFFICIENT (default): direct-URL `navigate`, `javascript_tool`, `get_page_text`. Works on most sites.
2. HUMAN-LIKE (if step 1 trips a wall): `navigate` only to the site's OWN homepage/search, then `screenshot` + single human `left_click`s; let the site open pages itself (new tabs join the MCP group). Slower but beats most bot-detection. On a hardened tab do NOT run `javascript_tool`/`get_page_text`/`read_page` —— they hang AND poison the tab so later clicks freeze; and don't batch a click immediately after another CDP op.
3. CAPTCHA / "verify you are human" gates: you may NOT solve OR click these —— bypassing/completing bot-detection is harness-prohibited (no framing or throwaway-account rationale changes this). Plain cookie / consent / T&C / "I agree" buttons are NOT bot-detection —— those you may handle (choose privacy-preserving).
4. "Nuclear" full-desktop control does NOT help for websites: the `computer-use` MCP restricts BROWSERS to read-tier (screenshot only; clicks/typing blocked, routed back through CIC). So CIC already IS your maximal browser control —— there is no fuller automated browser access.
5. LOGINS: CC must NOT type a password to authenticate into any field —— harness-prohibited even for a throwaway account the user supplies/authorises. Operate a session the user has ALREADY logged in, or have the user log in then proceed. (Stored logins —— e.g. `cic_libs.md`'s library SSO —— are user/historical references; CC does not type them.)
6. If steps 1–2 are exhausted and a real CAPTCHA/login blocks completion: SUMMON the user (per glossary.md) so the task NEVER fails silently. Under `#sprint` you can't interrupt mid-run, but AFTER writing the final sprint-report `response_`, if the task is unfinished, SUMMON —— the user may be away yet will see on OTGD that it stalled, instead of finding silent failure on return.

Site notes (examples —— apply the ladder generally):
- Temu: logged-out direct-URL/JS → CAPTCHA; homepage → search → human-click works.
- Taobao/Tmall (Alibaba, hardened): step-2 human-like WORKS even here —— `navigate s.taobao.com/search?q=…` → screenshot → single human-click a result → product opens; a known item/share link (`e.tb.cn`) direct-navigates fine. Never JS/get_page_text/read_page on a Taobao tab. Item discovery must be on-site (Alibaba blocks Google/Baidu indexing of items).

Credentials: the user keeps ONE dedicated low-risk account (no PII; Apple Hide-My-Email; confidential content is MFA-gated elsewhere) for a GROWABLE list of login-required sites. Exposure is low —— but CC still cannot type, author, store, OR display its password (harness rule; not framing/throwaway-dependent); the login step is the user's.

Login status by site (GROW this list as sites are met —— so future sessions know where to sign in vs browse as visitor):
- Temu —— `visitor` works (browse logged-out; may hit a CAPTCHA, which the dedicated account login may avoid).
- Taobao/Tmall —— `login` (user is normally already signed in; login improves results).
- (append each new site: `login` = needs sign-in, or `visitor` = browse without login)

Credential VALUES are NOT kept here by CC (CC won't author/echo a password). At a login wall on a `login` site, CC flags "needs login"; the user signs in; CC then operates the session.