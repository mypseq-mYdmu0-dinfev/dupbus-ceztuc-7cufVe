---
name: feedback-ajap-no-blocking-questions
description: "In AJAP cockpit mode (#seek), never block on AskUserQuestion or wait for a reply before continuing — the running programme must be unaffected by whether/when the user responds."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 05156150-eaae-4276-9259-8a9f3e5773f8
---

Do not use AskUserQuestion (or any other mechanism that pauses turn progress) to clarify playbook questions, ambiguous answers, or anything else while AJAP is running under [[ajap-cockpit-role]]. Surface playbook questions once, batched, in plain chat text — then continue the cockpit's own operations regardless of whether or when the user replies.

**Why:** user explicitly said (202607130712) "don't summon me again; whether or not i respond MUST NOT affect the running AJAP; continue." This matches the standing doctrine in `AJAP_dir/CLAUDE.md` that AJAP is fully autonomous and a mid-run question must never stall it — blocking tool calls (like AskUserQuestion) violate that even if the *text* of the question is fine.

**How to apply:** When ambiguity comes up (e.g. an unclear user answer to a playbook question), state the ambiguity and your best-guess interpretation in chat, then proceed — do not halt the turn waiting on a clarifying answer. Never gate cockpit operations (starting/monitoring/reporting on AJAP) behind a user response. If genuinely unresolvable, leave the question OPEN in `questions.md` for next `#seek` rather than blocking now.
