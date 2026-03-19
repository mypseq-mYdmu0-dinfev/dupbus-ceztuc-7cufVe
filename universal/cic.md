# CIC —— Claude in Chrome

CIC = Claude in Chrome (Claude's connector/Chrome's extension), accessible via either interfaces:

- **ACIC** = App-CIC, controlling via MCP in Claude's Mac app with full context; default means to use CIC
- **BCIC** = Browser-CIC, controlling via Chrome's sidebar chat (not MCP) without any context (e.g. personal preference, CP instructions); mainly used when preserving chat capacity

---

## When to Suggest CIC

When we're on high-stake tasks requiring validation or repetitive/lengthy tasks requiring minimal human intervention, briefly suggest (but don't proceed yet):

1. Me to continue the chat in CAI and open Chrome for ACIC; OR
2. If you should draft a prompt for BCIC to access actual sites in high quantity and/or perform non-context-dependent but lengthy actions (e.g. clicks)

---

## Drafting for BCIC

When drafting a BCIC prompt, ensure it's concise yet succinctly detailed (same for BCIC's response), just enough for BCIC (and you) to understand each other. For CWI-BCIC exchange, neglect all language/glossary conventions (e.g. mentioning `CIC`, using `` `~` `` instead of `-`) since BCIC has no context at all.

---

## IMPORTANT

If I request to use ACIC, you are CAI (not CWI) and MUST use CIC instead of `web_search` or BCIC prompt drafting throughout the chat unless instructed otherwise. If failed, stop and alert me.