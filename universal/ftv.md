# Film & TV Series Watching Profile

## 0. Purpose & Usage
Defines a personalised decision system for film (primary) and TV (secondary) recommendations.

- Goal:
  - High-accuracy suggestions with minimal input
  - Optimised for real-time “watch now” decisions
- Design principles:
  - Low friction
  - High relevance
  - Clear reasoning (pitchable if needed)

---

## 1. Supported Prompts & Behaviour

### 1.1 “watch something” (primary)
- Output:
  - 1–2 Precision Picks
  - 1 Exploration Pick
  - 1 Fallback Pick
- Rules:
  - No clarification questions initially
  - Films only (no TV)
  - 1–2 line persuasive reasoning per film

### 1.2 “i want a [genre/mood/type]”
- Constrain recommendations to domain
- Apply full evaluation system

### 1.3 “is [film_name] good?”
- Evaluate from user’s perspective, not public opinion
- Focus:
  - fit
  - trade-offs
  - whether worth watching

### 1.4 Constraints
- Default:
  - Films only
- TV:
  - Only if explicitly requested

---

## 2. Core Viewing Model

### 2.1 Dual-Mode System

- Mode A —— Solo / Analytical (rare)
  - Seeks:
    - concept
    - novelty
    - intellectual stimulation
  - Tolerance:
    - imperfect execution if idea is strong

- Mode B —— Shared / Dinner (default)
  - Seeks:
    - low-friction
    - well-executed
    - easy-to-follow
  - Must:
    - not mentally taxing
    - not emotionally irritating
    - aesthetically acceptable
  - Preference:
    - simple + well executed > complex + messy

---

### 2.2 Decision Types (for “watch something”)

- Precision Pick:
  - High-confidence match
  - Safe default

- Exploration Pick:
  - Tests boundary / mood
  - Provides calibration signal

- Fallback Pick:
  - Low-risk, high completion probability

---

### 2.3 Activation Energy

- Low (e.g. Netflix / instant):
  - explore freely
  - abandon freely

- High (download / effort):
  - optimise for certainty
  - avoid risk

---

### 2.4 Pitchability (soft factor)
- Bonus:
  - clean 1-line explanation
- Useful for shared viewing
- Not required

---

## 3. Evaluation Framework

### 3.1 Execution (core, highest ceiling; interacts with concept)

- Definition:
  - holistic completeness across all filmmaking dimensions

- Includes:
  - screenwriting / dialogue / structure
  - character design
  - concept integration
  - scoring (e.g. Hans Zimmer, Ryuichi Sakamoto)
  - production design (set, costume, VFX)
  - editing (pacing, transitions)

- Notes:
  - visual polish = subset (esp. dinner mode)
  - “flawless” = cannot be meaningfully improved further

- Effect:
  - strong execution → major uplift
  - rare due to high standard

---

### 3.2 Concept

- Nature:
  - broad dimension (not limited to novelty)

- High-impact patterns:
  - enables mental simulation (“what if real”)
  - establishes clear system / world rules

- Notes:
  - not required to be actionable
  - not required for enjoyment
  - evaluation influenced by perception layer

---

### 3.2.1 Concept Tendencies (observed)

- Common:
  - human potential / capability expansion
  - system-level worlds with rules

- Also acceptable:
  - real-world perspectives with unique framing
  - non-novel concepts with strong execution

- Note:
  - tendencies, not requirements

---

### 3.3 Perception Layer (critical)

- Core idea:
  - judgement based on what film feels like, not just premise

- Influenced by:
  - tone
  - casting
  - aesthetic

- Effect:
  - same concept may feel like:
    - “human optimisation”
    - “drug story”
    - “street-level narrative”

- Outcome:
  - can amplify or suppress concept value

---

### 3.4 Evaluation Logic (non-linear)

#### 3.4.1 Gatekeepers (must pass)
- aesthetic baseline (no strong aversion)
- no dominant kid/teen dynamics (unless exceptional)

#### 3.4.2 Core Drivers
- tightness / efficiency (high)
- strategic / controlled characters
- emotional control (low sentimentality tolerance)

#### 3.4.3 Value-Add Enhancers
- execution
- concept

- Notes:
  - not mandatory
  - amplify, not gatekeep

#### 3.4.4 Execution Behaviour
- acts as multiplier
- strong execution → large uplift
- weak execution:
  - tolerated if compensated
  - rarely reaches high score

---

### 3.5 Rewatchability & Memorability (non-evaluative)

- NOT used for selection or scoring

- Rewatchability:
  - convenience factor
  - useful if:
    - already watched
    - fits current mood
  - driven by:
    - rediscovery
    - durability (enjoyable even knowing outcome)

- Memorability:
  - not used in recommendation
  - only relevant in retrospective discussion

- Note:
  - excluded from evaluation logic

---

### 3.6 Actor System (core component)

- Nature:
  - “front-of-house” of film experience

- Direct impact:
  - visual comfort (appearance, styling)
  - immersion (fit to role)
  - engagement (performance)

- Role:
  - key component (not sole driver)
  - affects both:
    - willingness to start
    - overall experience

---

#### 3.6.1 Strong Override Group
- Dwayne Johnson
- Jason Statham
- Ryan Reynolds

---

#### 3.6.2 Positive Influence Group
- Morgan Freeman
- Samuel L. Jackson
- Robert Downey Jr.
- Benedict Cumberbatch
- Brad Pitt
- Cillian Murphy
- Rebecca Ferguson
- Vanessa Kirby
- Léa Seydoux

---

#### 3.6.3 Negative / Restriction

- Blacklist (if leading):
  - Millie Bobby Brown

- Negative bias:
  - Anthony Mackie (soft reluctance if leading)

---

#### 3.6.4 Behaviour Summary
- good casting → better immersion
- misaligned casting → reduced engagement
- actor effect:
  - can raise tolerance
  - can reduce willingness to start

---

## 4. Hard Filters & Penalties

### 4.1 Kid Penalty
- presence → negative
- dominance → near auto-reject
- acceptable:
  - minimal
  - functional (plot device)

---

### 4.2 Teen / Culture Aversion
- strong rejection:
  - teen-centric narratives
  - “kids empowerment”
  - heavy 80s/90s US nostalgia

---

### 4.3 Goofy / Cringe Comedy
- reject if:
  - poor aesthetic
  - forced / stupid humour

- acceptable:
  - clever execution only

---

### 4.4 Sentimentality
- low tolerance
- acceptable:
  - backed by execution / concept

---

### 4.5 Aesthetic Filter (gatekeeper + asymmetric)

- sensitive to:
  - cast appearance
  - styling
  - visual tone

- tolerance:
  - rough/dark ok if justified + intentional
  - “cheap/dirty” feel → strong negative

- role:
  - gatekeeper at entry
  - continues affecting score

- scoring behaviour:
  - pass baseline = easy
  - positive uplift = hard
  - negative penalty > positive gain

---

## 5. Acceptance Exceptions

### 5.1 Execution Override
- exceptional execution can override:
  - genre dislike
  - stylistic mismatch

---

### 5.2 Concept Override
- strong concept can justify:
  - imperfect execution
  - older films

---

### 5.3 Personal Resonance (rare, highest)

- effect:
  - life-level impact

- examples (descending):
  - The Secret Life of Walter Mitty
  - Up in the Air
  - The Company Men
  - The Big Short
  - Inception

- note:
  - extremely rare

---

### 5.4 Wasted Potential Penalty

- strong when:
  - experienced director

- reduced when:
  - new / early-stage director

- effect:
  - strong concept + poor execution:
    - heavy penalty (mature)
    - moderated (new)

---

## 6. Edge Cases

### 6.1 Epics / Long Films
- accepted if:
  - culturally / structurally elite
- requires:
  - dedicated session

---

### 6.2 Dumb Spectacle
- generally avoided
- acceptable:
  - no better option (e.g. plane)

---

## 7. TV Series Role

- generally avoided due to:
  - time inefficiency
  - lower execution density

- acceptable only if:
  - very high concept or execution
  - minimal teen/kid culture

---

## 8. Recommendation Behaviour (AI)

### 8.1 “watch something”
- no clarification questions
- output:
  - 1–2 precision
  - 1 exploration
  - 1 fallback
- short reasoning
- expect iteration

### 8.2 “is X good?”
- evaluate:
  - user-specific fit
- avoid:
  - generic opinions
- include:
  - better alternatives if relevant