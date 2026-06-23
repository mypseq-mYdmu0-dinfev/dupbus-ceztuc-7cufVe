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

## IMPORTANT

If I request to use CIC, you MUST use CIC instead of `web_search` alone or drafting a BCIC prompt. Enforced throughout session unless instr otherwise. If failed, stop & alert (no fallback).