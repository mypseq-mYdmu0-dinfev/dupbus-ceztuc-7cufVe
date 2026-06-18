# Interview Prep Protocol (`#int`)

*Triggered by `#int`. Codifies the repeatable end-to-end interview workflow refined across the Rennly and Alltech interviews, so any role reaching interview stage is handled consistently. Read alongside the role's AR. v1 — refine over time.*

---

## 0. Scope & Files
- 0.1. Working (enriched) AR lives in `seek/interviews/g/` (general roles) or `seek/interviews/c/` (consulting); filename TS = the upcoming/last interview time. The pristine `Outcome: Applied` original stays in `gcl/applied/` (or `ccl/`) untouched, so AJAP re-application guards still hold.
- 0.2. Read first: the role's AR, `seek/context/pro_profile.md`, and the apt resume variant. Use prior interview ARs as worked examples — Rennly (`seek/interviews/g/Rennly_CreativeMarketingSpecialist_202606121500.md`) and Alltech (`seek/interviews/g/AlltechAV_MarketingGrowthCoordinator_202606171500.md`).
- 0.3. Most outputs here are deliverables or durable records — mind `writing.md` for anything sent to the employer, and run `dlint.py` accordingly.

## 1. Phase A — Pre-Interview Research
- 1.1. Run `web_search` first to surface candidate sources, then validate every claim via CIC by actually visiting the source (web_search is triage, never confirmation).
- 1.2. Expand the AR's thin §1 stub into numbered subsections: company basics; scale/footprint; leadership; the interviewer(s) specifically; services + validated credits; work mode/structure; reputation; salary.
- 1.3. Reputation — ⚠️ anti-conflation: beware same-name entities (e.g. Glassdoor for a global namesake vs the actual SME). State explicitly when review data is NOT the employer.
- 1.4. Salary — capture the advertised band AND the part-time-vs-FTE-equivalent ambiguity; never resolve it by assumption.
- 1.5. Correct any AJAP misreads against the live job post (open it via CIC).

## 2. Phase B — Prep Deliverables (into AR §5)
- 2.1. §5A Likely interviewer questions (anticipate, mapped to the role + the firm's stated values).
- 2.2. §5B Questions to ask — ALWAYS include the signature question (§5 below); plus reporting/mentorship, first-90-day priority, P/T→F/T or promotion path, hands-on cadence, autonomy vs approval gates.
- 2.3. §5C Logistics & format (virtual/in person; what to screen-share; test kit).
- 2.4. §5D Strategy & key talking points (lead differentiator, builder framing, honest gap-handling, rapport hooks).
- 2.5. §5E Any application/assessment-specific prompts the ad asked for.

## 3. Phase C — Post-Interview Notes (into AR §7 as `Nth Interview Notes`)
- 3.1. Recordings often fail (Rennly voice recorder; Alltech Google Meet) — reconstruct from memory; mark wording as approximate; quote only what is genuinely verbatim.
- 3.2. BEFORE writing, ask the user an exhaustive clarifying set whilst memory is fresh — cover: meeting meta (length, who, camera, tone); what was shown vs only described; standard openers + framing; any scenario/task + the interviewer's reaction to the answer; AI stance (what was said, their reaction); people + decision-makers (esp. anyone at a later stage); compensation (any number? deferred?); loyalty/lifestyle probes + how handled; any concern raised about the candidate; the process/funnel; anything memorable.
- 3.3. Then write `IN.x` notes: arc/tone; process & funnel; people & reporting; role scope/workload; comp & logistics; interviewer character read; honesty/loyalty handling; the WIB usage; open items + next-stage flags.
- 3.4. Be candid (CIIW) — flag where the candidate may have over-hedged, mis-sequenced, or left a tension unresolved; do not just flatter.

## 4. Phase D — Assessment / Multi-Stage Handling
- 4.1. If an assessment/attachment pack arrives: read every file in full. Install `poppler` (`brew install poppler`) so the Read tool can render PDFs over 10 pages; `textutil -convert txt file.docx -stdout` is a fast fallback for `.docx`.
- 4.2. Read `shrink.md`; then `#summarise` (what to know/do) + `#synthesise` (decision-relevant insights, incl. the assignment's hidden test and the realism flaws to surface); append both as new sections at the AR foot (they substitute for un-embeddable attachments).
- 4.3. Note the interviewer's capability tells (typos, template artefacts, AI-but-unedited) — they calibrate positioning.
- 4.4. Draft the reply email (deliverable → `writing.md` + `dlint` FULL) into AR §7 under a `User Reply` heading; keep it lean — ask only questions that genuinely de-risk starting, banking the rest for the live session if the brief assesses the questions asked there.

## 5. Standard Questions Library
- 5.1. Signature (use in every interview — lands well, reads as experienced; echoed back as a good question by both Rennly and Alltech): **"What does success in this role look like — to you, to the company, and to me?"**
- 5.2. "How is the reporting/mentorship structured in practice?"
- 5.3. "What is the priority for the first 90 days?"
- 5.4. "What is the path (hours, seniority, scope) beyond this role, and what triggers it?"
- 5.5. "How much of the role is hands-on vs strategic, and how does that cadence look across the year?"

## 6. WIB — "What I Bring"
- 6.1. Status: the WIB **visual is not yet built** (deferred — see `career_close_202606162126.md`); use the **framework VERBALLY** until the visual exists.
- 6.2. Opener: "Rather than a title, what I bring to the table are four assets…"; tiles A1–A4 are memory triggers (A1 = "Business Innovation", etc.) — the candidate does not script.
- 6.3. Display rule: SHOW the visual (once built) only for creative/design/marketing/growth roles; keep it a private cue-card for consulting/BA/IT/finance/government.
- 6.4. Customise per role with a "dissect the role" addition (e.g. Alltech: Marketing / Growth / Coordinator / Builder-not-maintainer).

## 7. Caveats — NO FALSE CLAIMS
- 7.1. Mandarin = professional fluency, NOT native (native = Cantonese).
- 7.2. Video/editing = producer/director (creative direction); heavy hands-on editing predates the Creative Cloud era — lean on AI-accelerated production rather than overstating manual editing.
- 7.3. NEVER disclose founding KE — frame strictly as GM/leadership tenure (exception only on explicit approval where founding experience is genuinely valued).
- 7.4. Chameleon-veteran positioning: humble by default (AU tall-poppy); deploy breadth to connect/complement, holster the "dominate/checkmate" reflex.
- 7.5. Salary: hold to offer stage; let them frame the number; never re-anchor downward verbally.
- 7.6. Keep career-wide records generic (16⁺ yr content/PM, 300⁺ projects, 100⁺ clients) unless the role is marketing/content/PM; never make them domain-specific.
