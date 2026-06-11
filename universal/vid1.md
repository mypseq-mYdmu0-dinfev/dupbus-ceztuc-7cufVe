# Video Task Brief Builder (`#vid1`)

*Phase 1 of 2. Pairs with `universal/vid2.md` (`#vid2`), the executor. Use `#brief` to interrogate a hand-off task with me and draft a complete, self-sufficient `query_` brief; then a fresh session runs `#vid2` against that brief and completes it unattended. Goal of this phase is a brief so complete that the executor never needs to ask me anything.*

---

1. When to use
- 1.1. Any sizeable task I intend to hand off and walk away from, expecting it fully finished on return (deliverables, creative production, multi-step builds, research, migrations).
- 1.2. If the task is trivial or conversational, skip this; just do it.

2. How to run this phase
- 2.1. This is the ONE phase where back-and-forth with me is expected and cheap. Use it fully now so the execution phase needs zero input.
- 2.2. Ask me the gaps below in as few rounds as possible (batch questions). Propose sensible defaults so I can confirm rather than compose. Do NOT start producing the deliverable here.
- 2.3. Convert every relative date to absolute, state the timezone, and resolve any "latest/current" facts before they reach the brief.

3. Interrogate until each of these is pinned down
- 3.1. Context & goal —— what the artefact is, who it is for, the real stakes (e.g. interview, client submission, publication), and the one sentence definition of success.
- 3.2. Reference material —— exact local paths to read for context (CP files, profile, prior work). For any external/binary brief (PDF, slides, email), ask me to also drop a plain-text or `.md` copy so the executor stays post-compaction safe and never needs to re-fetch.
- 3.3. Deliverables —— enumerate every distinct artefact expected, with format and dimensions where relevant. Leave nothing implied.
- 3.4. Requirements & judging criteria —— mandatory features plus how the work will be assessed, so the executor can self-check against them at the end.
- 3.5. Creative / production direction —— palette, tone, structure, brand cues, length, and explicitly what is real versus fictional/sample (guards against false claims).
- 3.6. Tools & assets —— which MCPs, CLIs, or local tools are available; account tier and limits; what is allowed or forbidden; and crucially which tools need an action only I can take (paste-back generators, sign-in, public sharing, payments). Flag those now.
- 3.7. Output hygiene —— where files go, naming, and the split between deliverable-facing files and internal process notes. State a versioning rule (never overwrite a prior version; create `_v2`, `_v3`).
- 3.8. Interaction window —— how long I will be reachable after handing off, and confirm the executor must front-load all questions and external-tool prompt requests into that window, then run to completion without pausing.
- 3.9. Governance & permissions —— which `CLAUDE.md` governs, whether external uploads/hosting are permitted (e.g. to feed a URL-only tool), and any hard "never do X" lines.
- 3.10. Delegation —— decide whether sub-agents (SA) suit the work (independent parallel strands, broad sweeps, large file sets). If so, note the intended split in the brief; otherwise note inline execution.

4. Output of this phase
- 4.1. Draft a `query_[TS].md` (CP-prefixed if a CP chat) on my behalf, written as instructions to the executor, structured along §3 above. This mirrors a strong hand-off brief.
- 4.2. Include a short "Rules for this session" block at the end covering the window, no-start-then-pause, finish-completely, self-sufficiency, honesty / no false claims, and the governing `CLAUDE.md`.
- 4.3. Present it for my review and edits. Once I approve, a new session (or this one) runs `universal/vid2.md` against it.
- 4.4. Keep the draft tight and unambiguous. Every answer I gave in §3 should be reflected so the executor is never blocked on something I already know.
