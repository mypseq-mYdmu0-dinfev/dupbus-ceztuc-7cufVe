# Autonomous Video Production (`#vid2`)

*Phase 2 of 2. Pairs with `universal/vid1.md` (`#vid1`), which produces the reviewed `query_` brief this phase executes. Run a hand-off task to full completion, unattended, surfacing decisions only inside the interaction window. Default assumption is that I have left and expect a finished, verified result on return.*

---

1. Read and orient first
- 1.1. Read the brief in full, plus every reference it points to and the governing `CLAUDE.md` / CP unconditionals. Confirm which environment rules apply before acting.
- 1.2. Restate nothing back to me unless it goes in the window (§2). Silence outside the window is correct.

2. Use the interaction window once, completely
- 2.1. The window (often only a few minutes) is the ONLY time I am reachable. Front-load EVERYTHING into a single message, or a single file if chat text is restricted.
- 2.2. Put in it, in this order. Any genuine blocking question; every prompt that a paste-back tool needs (Gemini, Claude Design, etc.) written out ready to copy; and the creative/technical decisions I am locking in, stated so I can veto.
- 2.3. If I gave nothing to ask, begin immediately. Never start work, then pause mid-task to ask something. Starting and stopping is the main failure mode.
- 2.4. Assume no reply will come after the window. Design every dependency to have a fallback so the task still finishes if a paste-back never arrives.

3. Verify tool capability before committing to a pipeline
- 3.1. Probe the real constraints early, not after building. Examples seen to matter. Does the MCP accept local files or only public URLs. Does the local binary actually have the needed feature (a tool can be installed yet lack a module). Is an account tier or watermark going to block export.
- 3.2. Pick the route that gives the most control and uses the best assets, and keep a documented fallback. If a managed tool (e.g. a template generator) is loose or low quality, a deterministic local build usually wins on precision; reserve the managed tool for what only it can do.
- 3.3. If a tool needs a public URL for a local asset, hosting it briefly on a public file host is acceptable for non-sensitive material; never publish sensitive or personal data this way.

4. Build reproducibly and check your own work with your eyes
- 4.1. Drive generation from scripts/configs, not one-off commands, so any fix is a re-run. Keep intermediates in a working subfolder.
- 4.2. QA visually at every stage. Render a frame, composite an overlay on a flat background, pull a contact sheet, export a preview, and actually look at it. Fix before moving on. Do not trust that it worked because the command exited zero.
- 4.3. Match the brief's exact numbers (dimensions, duration, counts) and re-measure the final artefact against them.

5. Output hygiene
- 5.1. Keep deliverable-facing files clean and submission ready. Put process notes, rationale, and caveats in a separate internal file, never inside the deliverable.
- 5.2. Version, never destroy. New iterations become `_v2`, `_v3`; prior versions stay for record. Honour the repo Move and Void rules rather than deleting.
- 5.3. Leave the working folder tidy and name files so the next reader knows what to submit versus what is scaffolding.

6. Honesty and limits
- 6.1. Report blockers plainly the moment they are real; never fake success or paper over a gap. If tests fail or a step was skipped, say so.
- 6.2. State clearly what only I can do (authenticate, set public sharing, approve a payment, accept terms) and stop at that line. Do not enter credentials or perform prohibited actions to push through.
- 6.3. Keep every factual claim in deliverables true; mark sample/fictional data as such.

7. Delegate when it fits
- 7.1. Use sub-agents (SA) for independent parallel strands, broad multi-file sweeps, or work too large for one context, then synthesise their returns. Keep orchestration and final judgement with the main agent.
- 7.2. For a single tightly coupled build, inline execution is usually clearer than fanning out. Choose by the shape of the work, not by habit.

8. Finish completely
- 8.1. The task is done only when every deliverable exists, is verified, and is clean, with process notes captured separately. A half-built result or a message awaiting my reply is a failure when I return.
- 8.2. Self-check against the brief's requirements and judging criteria (§3.4 of `universal/vid1.md`) before declaring done, then emit the I/O declarations per the comms protocol.
