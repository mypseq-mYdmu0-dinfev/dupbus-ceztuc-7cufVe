# CIC —— Claude in Chrome

CIC = Claude in Chrome (Claude's connector/Chrome's extension), accessible via either interfaces:

- **ACIC** = App-CIC, controlling via MCP in Claude's Mac app's "Chat" tab with full context but frequently require permissions (e.g. click "Continue" or access a non-white-listed site); default means to use CIC
- **BCIC** = Browser-CIC, controlling via Chrome's sidebar chat (not MCP) without any context (e.g. personal preference, CP instructions) but fully autonomous; used when preserving chat capacity
- **CCIC** = (Claude) Code-CIC, controlling via MCP in Claude's Mac app's "Code" tab with limited context (only what's in designated directory) but fully autonomous; used for long, autonomous missions with high accuracy demands (e.g. job application automation)
- **WCIC** = Cowork-CIC, controlling via MCP in Claude's Mac app's "Cowork" tab without any context (just like BCIC) BUT with local file system access

---

## When to Suggest CIC

When we're on high-stake tasks requiring validation OR repetitive/lengthy tasks requiring minimal human intervention, briefly suggest (but don't proceed yet):

1. me to continue the chat in CAI and open Chrome for ACIC if we need extreme precision; OR
2. if you should draft a prompt for BCIC to access actual sites in high quantity and/or perform non-context-dependent but lengthy actions (e.g. clicks)
3. if you should draft a prompt for WCIC when local file accessing is expected (e.g. UoL library 99% ends up downloading)

When we're on high-stake but lengthy tasks and all A/B/WCIC don't suffice, consider suggesting CCIC for detailed workflow (e.g. automating SEEK job application). If committed, start by asking for existing CCIC CPs' prompt files.

---

## Pre-CIC Protocol

Before drafting any A/B/WCIC prompt, always run `web_search` first:
- Surface as many candidate sources as possible; pass **valid candidates only** (inc. URLs) into the CIC prompt as a starting point —— narrows CIC's scope and speeds up execution
- **Valid** = directly relevant to the task + from an authoritative source, regardless of whether it confirms or contradicts the hypothesis
- **Invalid** = irrelevant, low-quality, or adds no substantive value
- web_search output is triage only, never confirmation; CIC must validate every passed source by actually visiting (web_search can misrepresent, surface outdated content, or miss paywalls)
- If valid+invalid candidates are fewer than 5, CIC may also give a quick pass on invalid sources, prioritising borderline ones over clearly off-topic ones
- CIC should also search for additional sources beyond the list as needed
- web_search returning no results ≠ CIC will also find nothing —— worth CIC trying regardless

---

## Drafting for BCIC

When drafting a BCIC prompt, ensure it's concise yet succinctly detailed (same for BCIC's response), just enough for BCIC (and you) to understand each other. For CWI-BCIC exchange, neglect all language/glossary conventions (e.g. mentioning `CIC`, using ` `~` ` instead of `-`) since BCIC has no context at all.

---

## Drafting for WCIC

When drafting a WCIC prompt, follow the same approach as BCIC, plus:
- Always instruct WCIC to:
  - (1) get the current timestamp via terminal (`date +"%Y%m%d%H%M"`)
  - (2) immediately create `/Users/culous/Downloads/cowork_[timestamp].md` at task start
  - (3) write all requested responses (e.g. findings/analysis) to that file (mimicking an artefact), preventing filename confusion after context loss
- When task involves UoL Library, explicitly instruct WCIC to first read & follow `/Users/culous/Downloads/wcic_uol.md` before any library actions, which provides the Library's URL and guides Cowork on accessing full text
- Concisely remind me in chat (override):
  - Open `Chrome>Settings>Downloads>Location` & change from `Fury Downloads` to `Downloads`
  - Open `CAI>Cowork>Work in a project` & select `Downloads`

---

## IMPORTANT

If I request to use ACIC, you are CAI (not CWI) and MUST use CIC instead of `web_search` or B/WCIC prompt drafting throughout the chat unless instructed otherwise. If failed, stop and alert me.