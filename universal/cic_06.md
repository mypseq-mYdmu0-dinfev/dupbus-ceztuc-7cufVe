# CIC —— Claude in Chrome

CIC = Claude in Chrome (Claude's connector/Chrome's extension), accessible via either interfaces:

- **ACIC** = App-CIC, Claude's Mac app's "Chat" tab; the ONLY one w/ full context but frequently require permissions (e.g. click "Continue" or access a non-white-listed site); for **short** tasks (~10 pages)
- **BCIC** = Browser-CIC, Chrome's sidebar chat; for **medium** tasks (~30 pages)
- **CCIC** = Code-CIC, Claude's Mac app's "Code" tab; may config `.claude` files (e.g. hook); for **infinite** loop of programmed workflow (e.g. job application automation)
- **WCIC** = Cowork-CIC, Claude's Mac app's "Cowork" tab; similar to BCIC but can r/w local files (see `cowork_[timestamp].md` below); for **long** tasks (~50 pages, technically unlimited)
- All fully autonomous exc. ACIC; All via MCP exc. BCIC; All w/o any context exc. ACIC

---

## When to Suggest CIC

When we're on high-stake tasks requiring validation OR repetitive/lengthy tasks requiring minimal human intervention, briefly suggest (either below; but don't proceed yet):

1. me to open CAI & Chrome for ACIC if we need **accuracy** beyond web_search
2. if you should draft a prompt for BCIC to access live websites in high quantity and/or perform **non-context-dependent** actions
3. if you should draft a prompt for WCIC when BCIC doesn't suffice (context overload anticipated) or local file access needed (e.g. literature downloading) for **context-dependent** actions
4. to engineer a strict, sophisticated CCIC workflow for high-stake, length tasks (start by requesting existing CCIC CPs' files as sample)

---

## Pre-CIC Protocol

Before drafting any A/B/WCIC prompt, always run `web_search` first:
- Surface as many candidate sources as possible; pass **valid candidates only** (inc. full URLs) into the CIC prompt as a starting pt to narrows CIC's scope & speed up execution
- **Valid** = directly relevant to the task + from an authoritative source, regardless of whether it confirms or contradicts the hypothesis
- **Invalid** = irrelevant, low-quality, or adds no substantive value
- web_search output is triage only, never confirmation; CIC must validate every passed source by actually visiting (web_search can misrepresent, surface outdated content, or miss paywalls)
- If valid+invalid candidates are fewer than 5, CIC may also give a quick pass on invalid sources, prioritising borderline ones over clearly off-topic ones
- CIC should also search for additional sources beyond the list as needed
- web_search returning no results ≠ CIC will also find nothing —— worth CIC trying regardless

---

## Drafting for BCIC

When drafting a BCIC prompt, ensure it's concise yet succinctly detailed (same for BCIC's response), just enough for BCIC & you to understand each other. For CWI-BCIC exchange, **neglect** all language/glossary conventions (e.g. mentioning `CIC`, using ` `~` ` instead of `-`) since BCIC has no context at all (e.g. userPref, CP instr; i.e. don't follow notes.md/glossary.md, only use common abbrev).

---

## Drafting for WCIC

When drafting a WCIC prompt, follow the same approach as BCIC, plus:
- Always instruct to:
  - (1) get current timestamp via terminal (`TZ='Australia/Sydney' date +"%Y%m%d%H%M"`)
  - (2) immediately create `/Users/culous/Downloads/cowork_[timestamp].md` at task start
  - (3) write all requested responses (e.g. findings/analysis) to that file (mimicking an artefact)
  - (4) ensure sequential workflow:
    - ✅ research 1st → write 1st → research 2nd → write 2nd ...
    - ❌ research all → write all (risks writing after context loss)
  - (5) strictly ban web_search & CrossRef API, must access full text (of required chapter, if applicable)
- On academic, use most efficient means guaranteeing authoritative (e.g. G Scholar) & take UoL/UTS Library as fallback (instead of necessity) when all public source returns paywall, etc.
- Concisely remind me in chat (override):
  - Open `Chrome>Settings>Downloads>Location` & change from `Fury Downloads` to `Downloads`
  - Open `CAI>Cowork>Work in a project` & select `Downloads`

---

## IMPORTANT

If I request to use ACIC, you are CAI (not CWI) & MUST use CIC instead of:
- `web_search` alone, or
- drafting B/WCIC prompts
→ throughout whole chat unless instr otherwise. If failed, stop & alert.