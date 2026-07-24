# Response: i3 skills created (per ccsim_query_202607250012.md mission)
*Sprint Report + the 8 alias-skills*

## 80. Sprint Report (202607250031–202607250032) · ran ~1m
- 80.1. Done —— created 8 thin ALIAS-skills under `.claude/skills/<name>/SKILL.md`, one per situational `universal/` pcmd (per `ccsim_close_202607232054.md` §6.1.2). Each is a frontmatter (`name` + `description`) plus a one-line body pointing CC to read+follow the real file. All 8 frontmatters validated; all 8 target files confirmed to exist.
- 80.2. Assumed (no blocker needed clearing) —— (a) project-scoped `.claude/skills/` (not `~/.claude/skills/`), since each references dupbus-repo paths (`universal/...`, `cp/career/...`); (b) descriptions mirror each file's root `CLAUDE.md` §7.2 trigger condition (I had those in context, so no SA/pcmd-read was needed —— faster + cheaper than the suggested `#SA read all pcmds`); (c) kept the manual `#trigger`/§7.2 conditional-read intact —— these skills ADD a model-invoked path, they don't replace it; OTG untouched.
- 80.3. Interruptions —— none (0 compactions, 0 limits).
- 80.4. Open (i4/i5, next session) —— i4: install vetted EXTERNAL skills, but build a SAFETY-GATE skill FIRST (vets the safety of installing a skill); i5: have CCSIM/#wrap auto-propose skills for surfaced problems. i4/i5 were always gated behind i3 + a safety review; not started.

## 81. The 8 skills
- 81.1. `writing` → `universal/writing.md` —— fires on ANY deliverable (email/report/slides/letter/cover-letter/application) or "casual"/"whatsapp".
- 81.2. `profile` → `universal/profile.md` —— the user's PERSONAL background is needed.
- 81.3. `pro-profile` → `cp/career/pro_profile.md` —— the user's PROFESSIONAL background is needed.
- 81.4. `coding` → `universal/coding.md` —— creating/editing ANY script or `.md` pcmd.
- 81.5. `cic` → `universal/cic.md` —— ANY CIC browser op, or research needing accuracy/recency.
- 81.6. `shrink` → `universal/shrink.md` —— shrink/summarise/synthesise/distil/condense.
- 81.7. `plan` → `universal/plan.md` —— "dev plan"/"addendum" mentioned but no `*_DevPlan.md` in the CP.
- 81.8. `google` → `universal/google.md` —— personal email/calendar, or `#job`.

## 82. How they work + notes
- 82.1. Model-invoked: Claude auto-matches the `description` to the task and invokes the skill via the Skill tool, which loads the SKILL.md → CC then reads the real pcmd. So the §7.2 conditional-read now ALSO fires without the manual trigger —— belt-and-braces.
- 82.2. Authoritative rules stay in `universal/<file>.md` (single source of truth); the SKILL.md is a thin pointer, so the pcmds can change freely without touching the skills.
- 82.3. Caveat —— skill auto-invocation depends on Claude Code's skill-matching; if a skill over/under-fires in practice, tighten its `description`. Report any mis-fires and I'll tune them.
- 82.4. Explicit `#trigger` files (close/wrap/sync/br/debate/replace/sprint/int/job/jop) stay PLAIN —— no alias-skill (they already have a hard `#name` trigger; a skill would be redundant).
- 82.5. Next: i4 (external skills behind a safety-gate) —— recommend a dedicated session (external skills are untrusted code + instructions; the safety-gate skill is the right first move, never enable an unreviewed external skill).
