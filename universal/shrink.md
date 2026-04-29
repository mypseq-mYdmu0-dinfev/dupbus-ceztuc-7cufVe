# Content Shrinking Playbook

*4 deliberate shrinking techniques w/ command triggers.*

---

## Techniques

---

### Summarisation

**Purpose:** Condense source into shorter human-readable form. Doesn't generate new insights —— all info at least semantically present in the source. Optimised for human reading.

**Two modes:**

- **Extractive:** Select and stitch key sentences/phrases verbatim. Higher fidelity. Prefer when output will be quoted, attributed, or cross-referenced.
- **Abstractive:** Generate new sentences paraphrasing source. Lower fidelity; more readable. Prefer for casual comprehension.

**Canonical use case:** News articles, event recaps, meeting minutes.

---

### Synthesis

**Purpose:** Objective-driven transformation producing insights, decisions, or conclusions that may be absent from or not directly derivable from the source(s). High generativity; output quality scales with model capability and richness of context provided.

**Decisive test:** Does output contain something not semantically present in the source? Yes → synthesis. No → summarisation.

**Objective inference hierarchy (when not explicitly stated):**

1. CP context —— stated goals, audience, stakes (e.g. academic grade, client pitch, financial decision)
2. Culous' bg —— strategic thinker, investor, MBA, HCI/data; priorities: business impact, decision quality ("won't regret"), efficiency, scalability, intellectual precision; fetch `profile.md` and/or `pro_profile.md` if personal and/or professional bg (respectively) is centrally relevant
3. Immediate task context —— what decision or insight would be most actionable right now
4. Default: most actionable and directly applicable conclusion from available content

**Canonical use case:** Academic papers (empirical claims from data), industry research (positions from evidence), strategic/financial recommendations.

---

### Distillation

**Purpose:** Rule-governed filtering that removes content outside a defined rule's scope. Preserves authorial logic, voice, and structure of what remains; does not create new content at all. Fully optimised for Claude parsing —— not human reading.

**Why fidelity matters:** Distilled outputs are used as proxies for originals in future tasks where full requirements are not yet known. Default to broader filters; narrow only when output size is a hard constraint. A too-aggressive filter may strip content needed later; a well-defined rule prevents over-retention.

**Output format:** Always convert verbose prose to bullets during distillation. Maximises parsing efficiency and reduces token cost.

**Rule definition:** Must be explicitly defined or inferred before execution. A vague rule (e.g. "distil this website") returns near-full text; a scoped rule (e.g. "distil content concerning theme X") yields meaningfully leaner output.

**Typical use cases:**

- Files too large to feed simultaneously → distil each individually → feed distillations together for the task
- CP files too large to retain in full → distil → replace originals with distillations for ongoing tasks
- Web/document sources with heavy boilerplate (navigation, footer, ads, disclaimers) → distil to thematic content

**Canonical use case:** Pre-processing large reference files for context-constrained multi-file tasks.

---

### Condensation

**Purpose:** Editorial compression of existing writing —— reducing word count whilst preserving every element, tone, voice, and strategic meaning. No filtering; no new content. Assumes all content has value; pursues density.

**Distinction from distillation:** Condensation compresses uniformly; distillation filters selectively. Overlap in output length is coincidental, not structural.

**Applicable to:** Content Culous owns or is actively editing. Not typically applied to third-party reference material.

**Canonical use case:** Trimming a draft for word limits; tightening a report for executive readability.

---

## Spectrums

**Fidelity to source** (low → high):
`Synthesis` → `Summarisation` → `Distillation` → `Condensation`

**Generativity** (none → high):
`Condensation` ≈ `Distillation` (none) → `Extractive Summarisation` (minimal) → `Abstractive Summarisation` (moderate) → `Synthesis` (high)

**Optimised for:**
`Synthesis` → objective | `Summarisation` → human reading | `Distillation` → machine parsing | `Condensation` → authorial density

---

## Command Framework

---

### `summarise` / `summarize`

Execute immediately. Judge mode:

- **Extractive** if: output likely to be quoted/attributed; source is structured (legal, academic, policy); fidelity to wording matters
- **Abstractive** if: casual comprehension; conversational or loosely structured source; readability prioritised

### `#summarise` / `#summarize`

1. State chosen mode (extractive / abstractive) with one-sentence justification
2. Await confirmation
3. Execute

---

### `synthesise` / `synthesize`

Infer objective using hierarchy above. Execute immediately.

**Escalation:** May autonomously escalate to `#synthesise` behaviour **only** if stakes are high (academic submission, work/client deliverable, financial decision) **and** objective is genuinely ambiguous. Not applicable otherwise.

### `#synthesise` / `#synthesize`

1. State inferred objective in `~`2 sentences, citing contextual cues used (Culous' bg, CP goals, etc.)
2. Await confirmation
3. Execute

---

### `distil` / `distill`

Infer filtering rule from context. Execute immediately.

**Escalation:** May autonomously escalate to `#distil` behaviour if genuinely uncertain of the appropriate rule. Escalation is permitted here for uncertainty alone (not high-stakes alone). Does not apply to other techniques. `#distil` must never proceed without confirmation.

### `#distil` / `#distill`

1. State inferred filtering rule in `~`2 sentences
2. When input volume is large or output will be stored/fetched long-term: propose 2`~`3 breadth levels (e.g. narrow / moderate / broad) with predicted output length/size or compression ratio for each
3. Recommend most appropriate level with brief justification
4. Await confirmation
5. Execute on confirmed rule and breadth

---

### `condense`

Execute immediately. Compress word count of specified content whilst preserving all elements, tone, and meaning. No filtering; no new content generated.

*No `#condense` defined —— condensation intent (↓ word count) is always unambiguous; no confirmation step warranted.*

---

### `shrink`

Choose one of the techniques above based on context then execute immediately.

### `#shrink`

1. State chosen technique with one-sentence justification
2. Await confirmation
3. Execute