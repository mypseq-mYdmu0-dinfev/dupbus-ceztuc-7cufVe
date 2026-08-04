---
name: cic
description: Use for ANY Claude-in-Chrome (CIC) browser operation — open a site, navigate, fill a form, read a page — or when an answer needs live facts, not training knowledge: prices, dates, news, or whether something changed, was fixed, or is still true. Web search is not a substitute. Loads the CIC operating rules.
---

Read `universal/cic.md` in full and follow it for the current task. This skill is a thin alias for that project protocol — the authoritative, always-current rules live there, not here. (The manual `#trigger` / §7.2 conditional-read for this file still applies too; this skill just adds a model-invoked path.)

A web search or page fetch is TRIAGE only — it finds candidate sources. It never discharges a CIC obligation, and nor does handing the question to a sub-agent: brief the SA to read live via CIC, or read it yourself. If CIC genuinely cannot be used for a given claim, say so in the response and mark that claim unverified, rather than letting search results stand in for a live read silently.
