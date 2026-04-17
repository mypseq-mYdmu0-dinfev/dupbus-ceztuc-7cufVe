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

### 2.1 Execution (universal, highest ceiling; interacts with concept)

Definition:
> Holistic completeness across all filmmaking dimensions

Additional clarification:
- “Concept” is a broad dimension and not limited to novelty
- High-impact concepts often:
  - enable mental simulation (“what if this were real”)
  - establish clear rules of a system/world
- However, concept does NOT need to be personally actionable to be valued
- Concept evaluation is influenced by perception (tone, aesthetic, execution), not just premise

Perception Layer:
- Evaluation is influenced by what the film “feels like” it is about, not just its actual premise
- Tone, casting, and aesthetic can shift perception of the same underlying concept
- Example:
  - Similar premise may be perceived as:
    - “human potential” vs “drug story” vs “street-level narrative”
- This perception can amplify or suppress concept appreciation

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

### 2.1.1 Concept Tendencies (observed patterns)

Commonly appreciated:
- Human potential / capability expansion
- System-level worlds with rules (hidden structures, governed systems)

Also acceptable:
- Real-world perspectives with unique framing
- Non-novel concepts with strong execution

Note:
- These are tendencies, not requirements
- Strong concept can exist in any genre or form

---

### 2.2 Evaluation Logic (non-linear)

The system is NOT a linear priority stack. It operates as:

#### Gatekeepers (must pass to be considered)
- Aesthetic baseline (no strong visual/character aversion)
- No dominant kid/teen-centric dynamics (unless exceptional case)

#### Core Drivers (determine liking)
- Tightness / efficiency (high importance)
- Strategic / controlled characters
- Emotional control (avoid heavy sentimentality)

Execution behaviour:
- Acts as a multiplier, not a requirement
- Strong execution significantly elevates a film
- Weak execution is tolerated only if concept or other factors compensate

#### Value-Add Enhancers (can significantly elevate)
- Execution (holistic completeness across all aspects)
- Concept (world-building, rules, perspective)

Note:
- Execution and concept are NOT mandatory; they amplify, not gatekeep
- A film can be enjoyable without both, but rarely exceptional

#### Rewatchability & Memorability (non-evaluative)
- NOT used as criteria for selecting or scoring films

- Rewatchability:
  - Practical convenience factor, also useful in occasional retrospective discussion
  - If a recommended film was already watched but happens to be rewatchable and aligns with current mood, user may proceed without further refinement
  - Driven by:
    - rediscovery potential (new details on repeat viewing)
    - durability (enjoyable even knowing outcome)

- Memorability:
  - Not relevant for recommendation or scoring
  - Only surfaces in occasional retrospective discussion

- Note:
  - Both are excluded from evaluation logic during recommendation

---

### 2.3 Taste Axes (weighted tendencies)

- Conceptual depth: medium (6–7/10)
- Strategic characters: max (10/10)
- Realism vs stylisation: neutral (5/10)
- Emotional intensity: low tolerance for sentimentality; dislike kids
- Humour: neutral but sensitive to “stupid/goofy”
- Structure complexity: neutral
- Tightness: max (10/10)
- Additional factor — Actor affinity:

#### Strong override group (can trigger watch regardless)
- Dwayne Johnson
- Jason Statham
- Ryan Reynolds

#### Positive influence group (adds score / increases tolerance)
- Morgan Freeman
- Samuel L. Jackson
- Robert Downey Jr.
- Benedict Cumberbatch
- Brad Pitt
- Cillian Murphy
- Rebecca Ferguson
- Vanessa Kirby
- Léa Seydoux

#### Blacklist (if leading/main cast):
- Millie Bobby Brown

#### Negative bias (reduces engagement if leading):
- Anthony Mackie

#### Note
- Actors are a core visible component of the film experience (front-of-house equivalent)
- Their presence directly affects:
  - visual comfort (appearance, styling)
  - immersion (fit to role, screen presence)
  - engagement (performance quality)

- Role in evaluation:
  - Not the sole driver, but a key component alongside execution and concept
  - Can influence both entry (willingness to start) and overall experience

- Behaviour:
  - Good casting fit enhances immersion
  - Misaligned casting reduces engagement even if other aspects are strong
  - Certain actors may:
    - increase tolerance
    - slightly reduce willingness to start (if leading)

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

### 3.5 Aesthetic Filter (gatekeeper + asymmetric impact)

Strong sensitivity to:
- cast appearance / facial compatibility
- styling and visual tone
- overall “taste level” of the film

Tolerance nuance:
- Dark or rough aesthetics are acceptable if:
  - contextually justified (e.g. war, dystopia, horror)
  - still feel “intentional” rather than cheap or messy
- “Dirty/low-budget feel” without strong justification → strong negative reaction

Role:
- Acts as a gatekeeper at entry level (must pass baseline)
- Continues to influence scoring afterwards

Impact:
- Good aesthetics → minor positive uplift
- Poor aesthetics → major negative penalty
- Severe misalignment → rejection unless exceptional override

Scoring behaviour:
- Passing baseline is relatively easy
- Positive uplift requires high-level refinement (e.g. strong art direction, styling, visual coherence)
- Negative impact scales faster than positive uplift

Note:
Aesthetic tolerance may flex depending on genre/context (e.g. horror, war), but only within limits

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
- Highest form of impact (beyond execution or concept)

Examples (descending intensity):
1. The Secret Life of Walter Mitty —— identity-level, life-changing
2. Up in the Air —— strong current-life resonance
3. The Company Men —— similar resonance domain
4. The Big Short —— domain relevance (consulting/markets)
5. Inception —— philosophical impact (reality questioning)

Note:
- Extremely rare
- Not required for enjoyment, but creates lasting attachment

---

### 4.4 Wasted Potential Penalty (conditional)

- Applies strongly when:
  - director is experienced / expected to deliver
- Reduced when:
  - director is new or early-stage (more leniency)

Effect:
- Strong concept + poor execution → heavy penalty (mature director)
- Same scenario → moderated judgement (new director)

Rationale:
- Penalises avoidable failure, not learning-stage imperfection

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