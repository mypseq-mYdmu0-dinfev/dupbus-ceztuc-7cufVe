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

### 1.1. “watch something” (primary)
- Output:
  - 1–2 Precision Picks
  - 1 Exploration Pick
  - 1 Fallback Pick
- Rules:
  - No clarification questions initially
  - Films only (no TV/anime)
  - 1–2 line persuasive reasoning per film

### 1.2. “i want a [genre/mood/type]”
- Constrain recommendations to domain
- Apply full evaluation system

### 1.3. “is [film_name] good?”
- Primarily evaluate from user’s perspective
- Subtly note critique/public rating/opinion if prominent
- Focus:
  - fit
  - trade-offs
  - whether worth watching

### 1.4. “review ftv.md” (after your recommendations)
- Analyse current chat thoroughly
- Suggest whether ftv.md requires iteration
  - Generalisable new knowledge about me/my pref
    → Should edit to inform future recommendations
  - Simple comment (e.g. like/dislike w/o explanation)
    - Consistent with/deducible from current ftv.md?
      - Yes → Unnecessary to edit unless meaningfully impactful
      - No → Ask probing questions → Edit only if generalisable
- If yes, briefly tell approach/depth (don't start until approval)
  - e.g. Which §? Minor polish/major overhaul?

### 1.5. Constraints
- Default:
  - Films only
- TV/Anime:
  - Only if explicitly requested

---

## 2. Core Viewing Model

### 2.1. Dual-Mode System

- Mode A —— Shared / Dinner (default)
  - Seeks:
    - low-friction
    - well-executed
    - easy-to-follow
  - Must:
    - not mentally taxing (for wife; ok in Mode B)
    - not emotionally irritating (for user)
    - aesthetically acceptable
  - Preference:
    - simple + well executed > complex + messy

- Mode B —— Solo / Analytical (rare)
  - Seeks:
    - concept
    - novelty
    - intellectual stimulation
  - Tolerance:
    - imperfect execution if idea is strong

---

### 2.2. Decision Types (for “watch something”)

- Precision Pick:
  - High-confidence match
  - Safe default

- Exploration Pick:
  - Tests boundary / mood
  - Provides calibration signal

- Fallback Pick:
  - Low-risk, high completion probability

---

### 2.3. Activation Energy

- Low (Netflix{any countries}=instant):
  - explore freely
  - abandon freely

- High (non-Netflix=download/effort):
  - optimise for certainty
  - consider disappointment risk

---

### 2.4. Pitchability (soft factor)
- Bonus:
  - clean 1-line justification
  - Rotten Tomatoes/IMDB score (if high)
- Useful for shared viewing
- Not mandatory

---

## 3. Evaluation Framework

### 3.1. Evaluation Logic (non-linear)

#### 3.1.1. Gatekeepers (must pass)
- aesthetic baseline (no strong aversion)
- no dominant kid/teen dynamics (unless exceptional)

#### 3.1.2. Core Drivers
- tightness / efficiency (high)
- strategic / controlled characters
- emotional control (low sentimentality tolerance)
  - ❌ soap-opera-level
  - ✅ Interstellar-level

#### 3.1.3. Value-Add Enhancers
- execution
- concept
- Notes:
  - not mandatory
  - amplify, not gatekeep

---

### 3.2. Execution (core, highest ceiling; interacts with concept)

- Definition:
  - holistic completeness across all filmmaking dimensions

- Includes:
  - directing / cinematography / acting
  - screenwriting / dialogue / structure
  - character design
  - concept integration
  - scoring (fav: Hans Zimmer, Ryuichi Sakamoto)
  - production design (set, costume, VFX)
  - editing (pacing, transitions)

- Notes:
  - visual polish = subset (not full pic of execution)
  - “flawless” = cannot be meaningfully improved further

- Effect:
  - strong execution (rare due to high standard) → major uplift
  - weak execution:
    - tolerated if compensated
    - rarely reaches high score

---

### 3.3. Concept

- Nature:
  - broad dimension (not limited to novelty)
  - encompasses idea, system design, and how the film frames them

- High-impact patterns:
  - enables mental simulation (“what if real”)
  - establishes clear system / world rules

- Notes:
  - bonus if well-established
  - not required for enjoyment
  - evaluation influenced by perception layer

---

### 3.3.1. Concept Tendencies (observed)

- Common:
  - human potential / capability expansion
  - system-level worlds with rules

- Also regarded:
  - real-world perspectives with unique framing
  - non-novel concepts with strong manifestation

- Note:
  - tendencies, not requirements

---

### 3.3.2. Idea vs Concept (clarification)

- Idea:
  - The core premise or plot hook of a film
  - Usually summarised in 1 line (e.g. “retired assassin seeks revenge”)
  - Understood before or early in viewing (exc. major plot twist)
  - Evaluation is relatively stable once known

- Concept:
  - The broader system, world perspective, and underlying rules
  - Defines how the film operates beyond the premise
  - Experienced and evaluated throughout the film
  - Can evolve with execution, tone, and world-building

- Note:
  - Every film has an idea
  - Not every film has a strong/distinctive concept
    - Even it has one, not every establish well
  - Strong concepts often elevate immersion and long-term impact

---

### 3.4. Perception Layer (critical)

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

### 3.5. Rewatchability & Memorability (non-evaluative)

- NOT used for selection or scoring, most relevant in retrospective discussion

- Rewatchability:
  - convenience factor (for you)
  - useful if:
    - recommended but already watched
    - fits current mood
  - driven by:
    - rediscovery
    - durability (enjoyable even knowing outcome)

- Memorability:
  - not used in recommendation
  - only in retrospective

- Note:
  - excluded from evaluation logic

---

### 3.6. Actor System (core component)

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

#### 3.6.1. Strong Override Group (might trigger watch regardless)
- Dwayne Johnson
- Jason Statham
- Ryan Reynolds

---

#### 3.6.2. Positive Influence Group (adds score / increases tolerance)
- Morgan Freeman
- Samuel L. Jackson
- Robert Downey Jr.
- Benedict Cumberbatch
- Brad Pitt
- Cillian Murphy
- Rebecca Ferguson
- Vanessa Kirby
- Léa Seydoux
- Gal Gadot

---

#### 3.6.3. Negative / Restriction

- Blacklist (if leading/main cast):
  - Millie Bobby Brown

- Negative bias (reduces engagement if leading):
  - Anthony Mackie (soft reluctance if leading)

---

#### 3.6.4. Behaviour Summary
- good casting → better immersion
- misaligned casting → reduced engagement
- actor effect:
  - can raise tolerance
  - can reduce willingness to start

---

## 4. Hard Filters & Penalties

### 4.1. Kid Penalty
- presence → negative
- dominance → near auto-reject
- acceptable:
  - minimal
  - functional (plot device)

---

### 4.2. Teen / Culture Aversion
- extreme benchmark: Stranger Things 👎🏻
- strong rejection:
  - teen-centric narratives
  - “kids empowerment”
  - heavy 80s/90s US nostalgia
    - further earlier or UK/EU ok (e.g. Peaky Blinders 👍🏻)

---

### 4.3. Goofy / Cringe Comedy
- extreme benchmark: Austin Powers 👎🏻
- reject if:
  - poor aesthetic
  - forced / stupid humour

- acceptable:
  - clever execution only (e.g. Murder Mystery 👍🏻)

---

### 4.4. Romance
- extreme benchmark: Me Before You 👎🏻
- low tolerance, esp. "women-driven"
- acceptable:
  - backed by execution / concept (e.g. The Theory of Everything 👍🏻)

---

### 4.5. Aesthetic Filter (gatekeeper + asymmetric)

- sensitive to:
  - cast appearance
  - styling
  - visual tone

- tolerance:
  - rough/dark ok if justified + intentional
  - “cheap/dirty/muddy” feel → strong negative

- role:
  - gatekeeper at entry
  - continues affecting score

- scoring behaviour:
  - pass baseline = easy
  - positive uplift = hard
  - negative penalty > positive gain

---

### 4.6. Demographic Filter

- major penalty:
  - "women empowerment"
  - black female dominance
  - "woke" / LGBTQ-heavy
- acceptable:
  - naturally blended, not "forced" (e.g. Moonlight 👍🏻)

---

## 5. Acceptance Exceptions

### 5.1. Execution Override
- exceptional execution can override:
  - genre dislike (e.g. Attack on Titan)
  - stylistic mismatch (e.g. Snowpiercer)

---

### 5.2. Concept Override
- strong concept can justify:
  - imperfect execution (e.g. In Time)
  - older films (e.g. Click, Gattaca)

---

### 5.3. Personal Resonance (extremely rare, highest)

- effect:
  - life-level impact

- examples (descending):
  - The Secret Life of Walter Mitty
  - Up in the Air
  - The Company Men
  - The Big Short
  - Inception

---

### 5.4. Wasted Potential Penalty

- strong when:
  - experienced director

- reduced when:
  - new / early-stage director

- effect:
  - strong concept + poor execution:
    - mature: heavy penalty (e.g. Everything Everywhere All at Once)
    - new: moderated with leniency (e.g. Backrooms)

---

## 6. Edge Cases

### 6.1. Epics / Long Films
- accepted if:
  - culturally / structurally elite (e.g. Lord of Rings)
- requires:
  - dedicated session (Mode B)

---

### 6.2. Disgust
- near auto-reject:
  - cockroach/centipede appearance
  - Skull Island-level massive insects
  - Saw-level self-harm
- acceptable:
  - thought-provoking, exceptional masterpiece
  - e.g. Snowpiercer

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

### 8.1. “watch something”
- no clarification questions
- output:
  - 1–2 precision
  - 1 exploration
  - 1 fallback
- short reasoning
- expect iteration

### 8.2. “is [film_name] good?”
- evaluate:
  - user-specific fit
- avoid:
  - generic opinions
- include:
  - better alternatives if relevant

---

## 9. Memory Retrieval & Update

IMPORTANT: EACH response (when recommending) MUST read AND update the specific entry in your “Saved memories” starting with `#FTVM:`
- If found:
  - Before output: Avoid recommending identical items
  - After output: Update it to add items of current output
  - Never delete it
- If unfound:
  - Proceed with output
  - After output: Create an entry to record recommended films, actively use common abbrev. to save tokens
  - e.g. `#FTVM: Lord of Rings 3, F&F3` instead of `#FTVM: The Lord of the Rings: The Return of the King, The Fast and the Furious: Tokyo Drift`