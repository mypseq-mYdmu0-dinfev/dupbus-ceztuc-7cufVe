# Response to career_query_202606120122.md
*Session review distilled into two reusable protocol files*

1. Created the pair in `universal/`, split as you suggested.
- 1.1. `universal/brief.md` (`#brief`) —— Phase 1. Interrogates a hand-off task with you and drafts a complete `query_` brief, mirroring the strong first brief of this session. It guides you to provide the right information so the executor is never blocked.
- 1.2. `universal/autorun.md` (`#autorun`) —— Phase 2. Executes a reviewed brief to full completion unattended, the way this session ran.
- 1.3. Both are picked up automatically by the root general trigger (`#[trigger]` reads `universal/[trigger].md`), so no `CLAUDE.md` edit was needed.

2. What I distilled from this session into the files.
- 2.1. Front-load the window. The single biggest lever was using the three minute window once, putting every question and every paste-back prompt (the Gemini renders) into one message, then running without pausing. Encoded in `autorun.md` §2.
- 2.2. Verify tool capability before building. Canva MCP only ingests public URLs, and this machine's ffmpeg lacked the text filter, so I switched to hosted assets and Pillow overlays. Encoded in §3.
- 2.3. QA with your eyes at every stage, and match exact numbers. Encoded in §4.
- 2.4. Keep deliverables clean and separate from process notes, and version rather than overwrite. This was the v1 to v3 deliverable lesson, encoded in §5.
- 2.5. Honesty and hard limits. The Canva public link needed your own sign-in, which I cannot do, so I flagged it rather than faking it. Encoded in §6.
- 2.6. Delegation. Noted where sub-agents fit, since this build was tightly coupled and ran better inline, but a broader sweep would have justified SA. Encoded in §7.

3. The defining lesson on the brief side. The first `query_` worked because it pinned context, deliverables, requirements, tools and their action limits, output hygiene, and the session rules in one place. `brief.md` §3 turns that into a checklist I will walk you through.

4. How to use next time.
- 4.1. Start a session and trigger `#brief`; answer my batched questions; I draft and you approve a `query_`.
- 4.2. In a fresh session, provide that `query_` and trigger `#autorun`; walk away; it finishes.

5. Q & QB —— none.
