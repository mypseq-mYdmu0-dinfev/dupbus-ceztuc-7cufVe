# Film & TV Series Watching Profile

## Purpose & Usage

This file defines a personalised decision system for film (primary) and TV (secondary) recommendations.

It enables accurate, low-friction suggestions tailored to Culous’ taste, context, and viewing mode — especially when input is minimal or ambiguous.

### Supported Prompts

1. “watch something” (primary use case)
   - Provide a small set of film recommendations (not TV)
   - No clarification questions initially
   - Mix of:
     - high-confidence match(es)
     - 1 exploration option (to probe mood)
     - 1 safe fallback
   - Each with brief, persuasive reasoning (1–2 lines)

2. “i want a [genre/mood/type]”
   - Recommend within the specified domain
   - Apply all preference filters and evaluation logic

3. “is [film_name] good?”
   - Evaluate based on Culous’ likely perception, not general opinion
   - Focus on fit, trade-offs, and whether it’s worth watching

### Constraints

- Default to films only
- Do NOT recommend TV series unless explicitly requested
- Optimise for:
  - minimal friction
  - high relevance
  - explainability (can be justified or pitched if needed)

## 1. Core Viewing Model

### 1.1 Dual-Mode System

Mode A —— Solo / Analytical (rare)
- Seeks: concept, novelty, intellectual stimulation
- Tolerates: imperfect execution if idea is strong
- Examples: Inception, Tenet, Ex Machina

Mode B —— Shared / Dinner (default)
- Seeks: low-friction, well-executed, easy-to-follow
- Must:
  - not mentally taxing
  - not emotionally irritating
  - aesthetically acceptable
- “Simple but done extremely well” > “complex but messy”

---

### 1.2 Decision Types (for “watch something”)

1. Precision Pick
   - High confidence match
   - Safe to recommend without context

2. Exploration Pick
   - Tests mood / boundary
   - May fail but provides calibration signal

3. Fallback Pick
   - Low-risk, low-effort, high completion probability

---

### 1.3 Activation Energy (replaces “time ROI”)

- Low (Netflix / instant)  
  → willing to explore, abandon freely  

- High (download / effort)  
  → optimise for certainty, avoid risk  

---

### 1.4 Pitchability (soft factor)

- Bonus if film can be summarised cleanly in 1 line  
- Helps shared viewing, but not mandatory  

---

## 2. Evaluation Framework

### 2.1 Execution (universal, highest ceiling)

Definition:
> Holistic completeness across all filmmaking dimensions

Includes:
- screenwriting, dialogue, structure
- character design
- concept integration
- scoring (e.g. Hans Zimmer, Ryuichi Sakamoto)
- production design (set, costume, VFX)
- editing (pacing, transitions)

Note:
- Visual polish = subset only (mainly for dinner mode)
- Flawless execution = “cannot be meaningfully improved further”

Effect:
- Automatically elevates film → “must watch”
- Rare due to extremely high personal standard

---

### 2.2 Priority Stack (in practice)

1. Execution (holistic completeness; gatekeeper)
2. Tightness / efficiency (no wasted time)
3. Strategic / controlled characters
4. Emotional control (low sentimentality; low kids presence)
5. Aesthetic alignment (cast, tone, visual taste)
6. Conceptual strength (value-add, not sufficient alone)

---

### 2.3 Taste Axes (weighted tendencies)

- Conceptual depth: medium (6–7/10)
- Strategic characters: max (10/10)
- Realism vs stylisation: neutral (5/10)
- Emotional intensity: low tolerance for sentimentality; dislike kids
- Humour: neutral but sensitive to “stupid/goofy”
- Structure complexity: neutral
- Tightness: max (10/10)

Additional factor:
- Actor affinity:
  - Strong performances or preferred actors can elevate overall rating
  - Misaligned casting can reduce engagement even if other aspects are strong

---

## 3. Hard Filters & Penalties

### 3.1 Kid Penalty (systematic)
- Presence → negative
- Dominance → near auto-reject
- Acceptable only if:
  - minimal screen time, or
  - functional (plot device / liability)

---

### 3.2 Teen / Culture Aversion (extreme)
- Strong rejection of:
  - teen-centric narratives
  - “kids empowerment” themes
  - American nostalgia-heavy settings (80s/90s)
- Example rejection extreme: Stranger Things

---

### 3.3 Goofy / Cringe Comedy
- Hard reject if:
  - aesthetics poor
  - humour feels “stupid” or forced
- Acceptable only if:
  - cleverly executed (e.g. The Hangover)

---

### 3.4 Sentimentality
- Low tolerance
- Acceptable if:
  - backed by strong concept / execution
- Example: The Pursuit of Happyness (moderate)

---

### 3.5 Aesthetic Filter (structural)

- Strong sensitivity to:
  - cast appearance / facial compatibility
  - styling and visual tone
  - overall “taste level” of the film

- Poor aesthetics → major downgrade
- Severe misalignment → rejection regardless of other strengths

Note:
Aesthetic judgement is subjective but consistent; certain “looks” or character vibes can strongly reduce engagement even if execution is objectively good

---

## 4. Acceptance Exceptions

### 4.1 Execution Override
- Exceptional execution can override:
  - genre dislike
  - stylistic disagreement
- e.g. Wes Anderson (respected, not aligned but still enjoyed)

---

### 4.2 Concept Override
- Strong, unique concept can justify:
  - imperfect execution
  - older films
- e.g. Jumper

---

### 4.3 Personal Resonance (rare, highest impact)
- Film aligns with life narrative → extreme value
- Example:
  - The Secret Life of Walter Mitty = identity-level resonance

---

### 4.4 Wasted Potential Penalty (critical)

- Films with strong concepts but poor execution are penalised heavily
- Often rated lower than objectively worse films with aligned execution

Rationale:
- High awareness of “what it could have been”
- Perceived as missed opportunity rather than neutral output

Example:
- Strong concept + wrong direction → severe negative reaction

---

## 5. Edge Case Handling

### 5.1 Epics / Long Films
- Accepted if:
  - culturally or structurally “elite”
- Requires:
  - dedicated session (not dinner)
- Example: Lord of the Rings

---

### 5.2 “Dumb Spectacle”
- Normally avoided
- Acceptable only when:
  - no better option (e.g. plane scenario)

---

## 6. TV Series Role

- Generally avoided
- Reasons:
  - time inefficiency
  - lower execution density
- Only acceptable if:
  - extremely high concept or execution
  - minimal “teen/kid culture” contamination

---

## 7. Recommendation Behaviour (for AI)

When user says “watch something”:
- Do NOT ask clarifying questions initially
- Provide:
  - 1–2 Precision Picks
  - 1 Exploration Pick
  - 1 Fallback Pick
- Include brief reasoning (1–2 lines each)
- Expect iterative refinement via user feedback

When user asks “is X good?”:
- Focus on:
  - user-specific fit
  - not public opinion
- Compare against better substitutes where relevant