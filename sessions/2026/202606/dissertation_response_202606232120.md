# Response to "proceed"
*P12.7 —— `#replace #adv` handoff. RE-REVISED per `dissertation_query_202606240205.md`: a layout line-break (`U+2028`) is un-searchable by Pages' ⌘F, so each `Replace:` that spans a break is now split into break-free blocks (1 break → 2 blocks; ≥2 → 3). Generated via `cscpt/padv.py`.*

## How to use this
1. Each Change is ONE edit. `Replace:` may be 1, 2 or 3 break-free blocks:
- 1.1. **1 block** (no layout break): ⌘F it, swap in `With:`.
- 1.2. **2 blocks** (one break): ⌘F block 1 and block 2, select across both in .pages, replace with `With:`.
- 1.3. **3 blocks** (≥2 breaks): ⌘F block 1 (start) and block 3 (end), select everything from the first to the last, replace with `With:`; block 2 just shows the middle.
2. `**word**` in `With:` = bold it after pasting (strip the stars). Existing .pages bolds stay.
3. `With:` is one unbroken block —— you re-break for layout.
4. Word-count lines are NOT ported (internal tracking only).

---

## A. §1 Introduction

### Change 01 —— §1 ¶1 (KBF definition reworded)
**Replace:**
```
In knowledge-based firms (KBFs), individual expertise constitutes the primary source of competitive advantage (Grant, 1996; Kogut and Zander, 1992). The strategic architecture of KBFs (spanning mainly legal, accounting, consulting, engineering, IT, and R&D sectors) depends on
```
**With:**
```
Knowledge-based firms (KBFs), whose competitive advantage derives primarily from the specialist expertise of their individual professionals rather than from physical or financial capital, span sectors such as legal, accounting, consulting, engineering, IT, and R&D (Grant, 1996; Kogut and Zander, 1992). The strategic architecture of these firms depends on
```

### Change 02 —— §1 ¶2 (CYC reframe + management-challenge sentence)
**Replace** (1 break → 2 blocks; ⌘F both, select across them, then replace):
```
CYC is a management consulting firm (MCF) specialising in KM, advising KBF clients on
```
```
the governance conditions that sustain or inhibit effective knowledge contribution1. Across its client engagements, CYC has identified a recurring phenomenon carrying direct implications for KM performance, namely Tall Poppy Syndrome (TPS).
```
**With:**
```
CYC is a newly established management consulting firm (MCF) specialising in KM, intended to serve KBF clients across the Australian professional services sector¹. As a knowledge-based firm in its own right, CYC’s central commercial asset is rigorous, evidence-based knowledge of the governance conditions that sustain or inhibit effective knowledge contribution within KBFs. Its **management challenge** is therefore to strengthen the empirical foundation upon which that consulting practice will stand. The phenomenon at the centre of that challenge, carrying direct implications for KM performance, is Tall Poppy Syndrome (TPS).
```
⚠️ Footnote [1] anchor MOVES: detach the superscript ¹ from after “knowledge contribution” and reattach it after “Australian professional services sector”. Bold “management challenge”.

### Change 03 —— §1 ¶4 (“variable” → “phenomenon”)
**Replace:**
```
limiting possibilities to isolate TPS as the explanatory variable.
```
**With:**
```
limiting possibilities to isolate TPS as the explanatory phenomenon.
```

### Change 04 —— §1 ¶4 (client-base sentence)
**Replace:**
```
CYC’s primary client base spans KBFs broadly across multiple sectors; the research participant pool is drawn from within this base, providing the cross-firm diversity this study requires.
```
**With:**
```
CYC’s intended client base spans Australian KBFs broadly across multiple sectors; the research participant pool is drawn from individuals working within this base, providing the cross-firm diversity this study requires.
```

### Change 05 —— Research Aim (locked RA)
**Replace:**
```
To investigate how TPS dynamics in KBFs generate team cohesion and knowledge governance challenges, surfacing management implications for practitioners.
```
**With:**
```
To investigate how TPS influences team cohesion and knowledge governance in Australian KBFs, crystallising the empirical foundation for CYC’s KM consulting practice.
```

### Change 06 —— RO4 (reworded)
**Replace:**
```
RO4. Formulate management recommendations addressing TPS-related KM and team cohesion risks.
```
**With:**
```
RO4. Synthesise a knowledge base on TPS-related KM and team cohesion risks from research insights to entrench CYC’s service offering foundation.
```

### Change 07 —— insert new golden-thread paragraph (INSERTION, no line break)
Place the cursor at the START of the “This study contributes …” paragraph and insert this BEFORE it (do not retype the existing sentence):
```
Together, the 2 questions carry the aim’s golden thread: RQ1 examines the conditions shaping TPS and RQ2 the team-level experience of its dynamics, addressed by RO3 and RO2 respectively, whilst RO1 establishes the literature and RO4 converts the resulting insight into CYC’s consulting knowledge.
```
*⏏ locate the insertion point via “This study contributes academically by extending”.*

### Change 08 —— §1 contribution (2nd sentence reworded)
**Replace** (1 break → 2 blocks; ⌘F both, select across them, then replace):
```
For CYC, the findings will inform
```
```
a cross-sector advisory framework supporting KBF clients in diagnosing and mitigating the knowledge governance risks associated with TPS.
```
**With:**
```
For CYC, the findings will form the empirical foundation of its KM consulting practice, positioning the firm to advise future KBF clients on diagnosing and mitigating the knowledge governance risks associated with TPS.
```

### Change 09 —— remove “Structure of Chapters” subsection (CM3)
**Replace** (heading + paragraph; ⌘F each, select across, delete both):
```
Structure of Chapters (pre-drafted for Assessment 3 full paper)
```
```
Chapter 2 presents a critical literature review structured around the TPS phenomenon, its implications for KM governance, and the specific conditions under which it operates within KBFs. Chapter 3 presents the research methodology, detailing the explanatory multi-case study design, sampling approach, interview-based data collection technique, and thematic analytical procedure. Chapter 4 presents the findings from semi-structured interviews conducted across six independent KBF contexts. Chapter 5 analyses and discusses the findings in relation to the research questions and existing literature. Chapter 6 closes with the study’s conclusions, SMART3 recommendations for managers, research limitations, future research, and personal learning reflections.
```
*(delete entirely.)*

### Change 10 —— Footnote [1] (shortened)
**Replace** (2 breaks → 3 blocks; ⌘F blocks 1 & 3, select from the first to the last, then replace; block 2 = the middle, reference only):
```
As with MCFs that publish independent research,
```
```
CYC’s (simulated entity) engagement with this topic
```
```
is consistent with its specialism in KM.
```
**With:**
```
CYC is a simulated entity, created for this study.
```

### Change 11 —— remove Footnote [3] (SMART)
**Replace** (find this, then delete):
```
Specific, Measurable, Achievable, Relevant, and Time-bound
```
SMART stays defined in the Glossary; after Change 09 there is no in-text ³ anchor.

---

## B. §2 Literature Review

### Change 12 —— §2.4 (“four” → “4”)
**Replace:**
```
confirmed TPS as one of four distinctively Australian cultural dimensions
```
**With:**
```
confirmed TPS as one of 4 distinctively Australian cultural dimensions
```

### Change 13 —— §2.4 (closing phrase)
**Replace** (1 break → 2 blocks; ⌘F both, select across them, then replace):
```
particularly acute across the Australian professional services sector,
```
```
which is a context well represented within CYC’s international KBF client base.
```
**With:**
```
particularly acute across the Australian professional services sector, the context in which CYC itself is founded and intends to practise.
```

### Change 14 —— §2.5 heading
**Replace:**
```
2.5. Literature Gap & Conceptual Framework
```
**With:**
```
2.5. Literature Gap & Theoretical Framework
```

### Change 15 —— §2.5 second paragraph replaced (gap paragraph above it is unchanged)
**Replace** (3 breaks → 3 blocks; ⌘F blocks 1 & 3, select from the first to the last, then replace; block 2 = the middle, reference only):
```
The provisional conceptual framework (Figure 1) synthesises four thematic domains.
```
```
Within this structure, SCT’s cessation-of-comparison mechanism creates the social conditions under which SET’s reciprocity logic predicts withdrawal is more probable, with KBV establishing
```
```
the strategic stakes that render this a governance-critical concern. RQ1 and RQ2 map onto the conditions and peer experience domains respectively, informing both data collection and interpretation. Domains connect through relational associations, not directional causation, consistent with interpretivist epistemology (Saunders, Lewis and Thornhill, 2023).
```
**With:**
```
The study’s **theoretical framework** is theoretically-informed yet sensitising: it orients enquiry without dictating its findings. The constituent concepts, drawn from the literature reviewed above, suggest where analytic attention might productively fall; they are not variables to be tested, nor a fixed coding frame, and any may be reshaped, merged, or displaced by themes generated from the data. Figure 1 sets out, for each research question, the sensitising themes, their informing theories, and the illustrative factors each foregrounds.

Figure 2 assembles these factors into the framework. Within it, the conditioning factors associated with RQ1, rooted in SCT and the envy literature, describe the social circumstances under which the reciprocity logic of SET, associated with RQ2, renders knowledge-sharing withdrawal more probable, whilst the KBV establishes the strategic stakes that bear on both questions rather than answering either, rendering the matter governance-critical. These themes and factors will sensitise, rather than determine, the thematic analysis (§3.4); coding is generated from the corpus, with theory aiding interpretation at the latent level rather than pre-registering codes for confirmation (Braun and Clarke, 2006). A disconfirming-evidence node is retained throughout, making explicit the study’s openness to dynamics that no listed theory anticipates. The framework asserts no causal direction, its relational lines denoting conjectural associations from the literature, and the explanatory character of the case study concerns analytic generalisation to theory rather than variable causation (Yin, 2003). The framework is provisional and will be refined once the empirical findings emerge (Saunders, Lewis and Thornhill, 2023).
```

---

## C. Figures

### Change 16 —— replace the old single figure with TWO figures
**Replace** (old figure heading, then its caption in 2 blocks; select the whole figure region incl. the image and delete):
```
Figure 1. Provisional Conceptual Framework
```
```
Connecting lines represent relational associations; no causal direction implied.
```
```
Framework to be refined post-analysis.
```
**With** —— (a) build Figure 1 as a Pages TABLE, captioned “Figure 1. Sensitising Themes, Informing Theories and Illustrative Factors by Research Question”:

| RQ | Sensitising Theme | Informing Literature | Illustrative Factor |
|---|---|---|---|
| RQ1 | Performance comparison and threat | SCT (Festinger, 1954) | comparison threat; uniformity pressure |
| RQ1 | Envy pathway | Sung et al. (2024); Li, Xu and Kwan (2021) | benign versus malicious envy |
| RQ1 | Group identification | Kim and Glomb (2014) | work-group identification (alleviating) |
| RQ1 | Structural conditions | Gully et al. (2012); Meng, Ashkanasy and Härtel (2003) | task interdependence; egalitarian norm; reward and leadership |
| RQ2 | Knowledge-sharing response | SET (Blau, 1964); Podsakoff et al. (2000) | reciprocity breakdown; KS withdrawal |
| RQ2 | Social exclusion | Breidenthal et al. (2020) | ostracism; informal exclusion |
| RQ2 | Cohesion and trust | Grossman et al. (2022); Mathieu et al. (2015) | cohesion erosion; trust breakdown |
| Stakes | Strategic consequence | KBV (Grant, 1996; Kogut and Zander, 1992) | withheld tacit knowledge; KM governance risk |

(b) then, as a separate figure, paste the SVG image `MGTK751_A1R_Figure2_TheoreticalFramework.svg` (its “Figure 2 …” caption and the sensitising/§3.4 line are baked into the image).
⚠️ Order: §2.5 prose now names Figure 1 (table) THEN Figure 2 (diagram) —— place the table before the SVG.

---

## D. §3 Research Methodology

### Change 17 —— §3.1 heading (was “Research Philosophy & Approach”)
**Replace:**
```
3.1. Research Philosophy & Approach
```
**With:**
```
3.1. Research Philosophy
```

### Change 18 —— §3.1 ¶1 → new §3.1 body + new §3.2 section
**Replace** (3 breaks → 3 blocks; ⌘F blocks 1 & 3, select from the first to the last, then replace; block 2 = the middle, reference only):
```
This study adopts an interpretivist philosophy grounded in constructivist ontology and
```
```
subjectivist epistemology. TPS dynamics are constituted through social perception, attribution, and contextually contingent group behaviour; they cannot be meaningfully reduced to
```
```
objective measurement alone. An inductive, qualitative approach is accordingly adopted, permitting investigation of TPS experience without imposing confirmation bias onto an inherently socially constructed and contextually variable phenomenon (Saunders, Lewis and Thornhill, 2023).
```
**With:**
```
This study is grounded in an **interpretivist** epistemology and a constructivist ontology (Saunders, Lewis and Thornhill, 2023). Consistent with this position, TPS is regarded not as an objective, independently measurable entity but as a phenomenon constituted through the social perceptions, attributions, and contextually contingent group behaviours of those who witness and enact it. An interpretivist epistemology is correspondingly adopted because meaningful knowledge of TPS can be derived only from the subjective accounts of those who experience it, rather than from detached statistical observation. These positions suit a phenomenon whose reality is inseparable from how team members understand and respond to it.

3.2. Research Approach

An inductive, qualitative approach is adopted. Induction is followed because the study seeks to surface explanations grounded in participant accounts rather than to test propositions formulated in advance, guarding against the imposition of confirmation bias onto an inherently socially constructed and contextually variable phenomenon (Saunders, Lewis and Thornhill, 2023). A qualitative approach is correspondingly suited to the depth, nuance, and contextual sensitivity that the study of TPS dynamics demands, which quantitative measurement could not adequately capture.
```
Format “3.2. Research Approach” as a heading. Bold “interpretivist”.

### Change 19 —— §3.1 ¶2 → new §3.3 section
**Replace** (1 break → 2 blocks; ⌘F both, select across them, then replace):
```
The chosen research method is an explanatory multi-case study (Yin, 2003; Zainal, 2007).
```
```
Case study suits examining contemporary phenomena within their real-life contexts, and the explanatory variant is applied here because the study seeks to understand the conditions and mechanisms through which TPS operates within KBFs rather than merely to establish that it does (Zainal, 2007). Each sample unit constitutes a single case, with six organisations yielding six cases5. Analytical weight derives from “replication logic”, whereby patterns recurring across multiple independent cases carry stronger inferential value than those arising from a single site (Yin, 2003). This multi-case design also reflects the cross-sector character of CYC’s KBF client base. As an MCF specialising in KM, its advisory engagements span KBFs broadly, and the research participant pool is drawn from within this base.
```
**With:**
```
3.3. Research Method

The chosen research method is an **explanatory multi-case study** (Yin, 2003; Zainal, 2007). A case study is adopted because it suits the examination of a contemporary phenomenon within its real-life context, and the explanatory variant is applied because the study seeks to understand the conditions and mechanisms through which TPS operates within KBFs rather than merely to establish that it does (Zainal, 2007). Its explanatory character concerns analytic generalisation to theory rather than the inference of variable causation. Each participant constitutes a single case, with at least 6 participants drawn from independent organisations yielding a corresponding set of individual-level cases⁵. Analytical weight derives from “replication logic”, whereby patterns recurring across multiple independent cases carry stronger inferential value than those arising from a single site (Yin, 2003). This multi-case design also reflects the cross-sector character of the Australian KBFs that CYC, as an MCF specialising in KM, is founded to serve, and from which the research participant pool is drawn.
```
Format “3.3. Research Method” as a heading. Bold “explanatory multi-case study”. Footnote [5] anchors at “cases⁵” here (see Change 32).

### Change 20 —— heading renumber 3.2 → 3.4 (body unchanged)
**Replace:**
```
3.2. Data Collection
```
**With:**
```
3.4. Data Collection
```

### Change 21 —— heading renumber 3.3 → 3.5
**Replace:**
```
3.3. Sampling
```
**With:**
```
3.5. Sampling
```

### Change 22 —— §3.5 ¶1 (reworded)
**Replace:**
```
At least six participants will be recruited through purposive sampling, drawn from KBFs broadly as CYC’s primary client base. TPS is a supra-organisational phenomenon driven by group dynamics that transcend individual firm boundaries; single-entity sampling would risk conflating findings with that firm’s idiosyncratic leadership or culture rather than isolating TPS as the explanatory variable. Cross-firm design is, therefore, methodologically necessary.
```
**With:**
```
At least 6 participants will be recruited through purposive sampling, each an individual employee working within an Australian KBF of the kind that constitutes CYC’s intended client base. Interviews centre on participants’ own professional experiences and perceptions, drawn from current or previous employers, rather than on any formal account of a current employer’s practices; this keeps the enquiry at the level of individual perspective and outside the scope of organisational authorisation. TPS is a supra-organisational phenomenon driven by group dynamics that transcend individual firm boundaries; single-entity sampling would risk conflating findings with that firm’s idiosyncratic leadership or culture rather than isolating TPS as the explanatory phenomenon. No more than one participant is recruited from any single organisation; this one-per-organisation design isolates TPS dynamics from single-firm cultural idiosyncrasies. So far as access reasonably allows, participants of broadly comparable professional standing would be sought, to strengthen cross-case comparability.
```

### Change 23 —— §3.5 ¶2 (reworded)
**Replace** (3 breaks → 3 blocks; ⌘F blocks 1 & 3, select from the first to the last, then replace; block 2 = the middle, reference only):
```
Purposive selection criteria require participants to have worked alongside standout performers in
```
```
a KBF setting and have directly observed shifts in team dynamics. Primary participants are TPPs, non-managerial professionals occupying a lateral vantage point from which TPS dynamics are fully visible. Specialised knowledge flows are laterally embedded and largely opaque to management hierarchies (Grant, 1996); peer accounts thus offer the most viable access to the informal realities of TPS-driven KM erosion. Supplementary interviews with TPs or managers will be attempted prior to analysis. One-participant-per-organisation design would be practised to
```
```
isolate TPS dynamics from single-firm cultural idiosyncrasies.
```
**With:**
```
Purposive selection criteria require participants to have worked alongside standout performers in a KBF setting and to have directly observed shifts in team dynamics. Primary participants are TPPs, non-managerial professionals occupying a lateral vantage point from which TPS dynamics are fully visible. Specialised knowledge flows are laterally embedded and largely opaque to management hierarchies (Grant, 1996); peer accounts thus offer the most viable access to the informal realities of TPS-driven KM erosion. Supplementary interviews with TPs or managers would be sought where available, as optional triangulation enriching the peer-primary design.
```

### Change 24 —— §3.5 ¶3 (“six” → “6”)
**Replace:**
```
can emerge by six homogeneous interviews
```
**With:**
```
can emerge by 6 homogeneous interviews
```

### Change 25 —— heading renumber 3.4 → 3.6
**Replace:**
```
3.4. Data Analysis
```
**With:**
```
3.6. Data Analysis
```

### Change 26 —— §3.6 ¶1 (reworded —— framework-sensitising sentence; six-phase→6-phase; third→3rd; six contexts→each context; convergent validation→corroboration)
**Replace:**
```
Thematic analysis following Braun and Clarke’s (2006, p.87) six-phase framework is adopted. Coding commences after the third interview and proceeds iteratively until saturation is reached. The analytic sequence follows a within-case then across-case approach (Ayres, Kavanaugh and Knafl, 2003). Each case is first analysed individually in depth before cross-case patterns, configurations, and variations are identified. This sequence preserves within-case richness before cross-case synthesis is attempted, consistent with the “replication logic” (Yin, 2003) of the study. Data are collected across six independent organisational contexts, enabling cross-case comparison and convergent validation of emerging themes.
```
**With:**
```
Thematic analysis following Braun and Clarke’s (2006, p.87) 6-phase framework is adopted. Coding commences after the 3rd interview and proceeds iteratively until saturation is reached. The theoretical framework set out in §2.5 sensitises this analysis, orienting attention towards the themes and factors the literature foregrounds whilst leaving the codebook to be generated from the data rather than pre-registered, so that theory aids interpretation at the latent level rather than imposing confirmation (Braun and Clarke, 2006). The analytic sequence follows a within-case then across-case approach (Ayres, Kavanaugh and Knafl, 2003). Each case is first analysed individually in depth before cross-case patterns, configurations, and variations are identified. This sequence preserves within-case richness before cross-case synthesis is attempted, consistent with the “replication logic” (Yin, 2003) of the study. Data are collected across each independent organisational context, enabling cross-case comparison and corroboration of emerging themes.
```

### Change 27 —— heading renumber 3.5 → 3.7
**Replace:**
```
3.5. Trustworthiness
```
**With:**
```
3.7. Trustworthiness
```

### Change 28 —— §3.7 (“four” → “4”)
**Replace:**
```
(2004) four trustworthiness criteria
```
**With:**
```
(2004) 4 trustworthiness criteria
```

### Change 29 —— heading renumber 3.6 → 3.8
**Replace:**
```
3.6. Feasibility & Limitations
```
**With:**
```
3.8. Feasibility & Limitations
```

### Change 30 —— heading renumber 3.7 → 3.9
**Replace:**
```
3.7. Ethics
```
**With:**
```
3.9. Ethics
```

### Change 31 —— §3.9 (de-identification sentence added)
**Replace** (1 break → 2 blocks; ⌘F both, select across them, then replace):
```
and all data would be stored on UoL OneDrive.
```
```
Data collection will not commence until written ethical approval has been received.
```
**With:**
```
and all data would be stored on UoL OneDrive. Individual accounts would be de-identified, and details capable of identifying a current employer would not be solicited, keeping the enquiry on the participant’s own professional experience. Data collection will not commence until written ethical approval has been received.
```

### Change 32 —— Footnote [5]
**Replace:**
```
One participant per organisation, totalling at least six, see §3.3.
```
**With:**
```
One participant per organisation, totalling at least 6, see §3.5.
```

---

## E. §4 Milestone Plan (update 7 cells; rows 01, 02, 10, 11 unchanged)

### Change 33 —— milestone dates (cell edits, no line breaks)
| Row | UoL Week (old → new) | Calendar Date (old → new) |
|---|---|---|
| 03 Refined proposal approved by DA and second reviewer | Week 8–9 → **Week 15** | w/c 05/05/2026 → **w/c 23/06/2026** |
| 04 Ethics application submitted | Week 9 → **Week 16** | w/c 12/05/2026 → **w/c 30/06/2026** |
| 05 Ethics application approved | Week 11 → **Week 17** | w/c 26/05/2026 → **w/c 07/07/2026** |
| 06 Data collection commences | Week 12 → **Week 18** | w/c 02/06/2026 → **w/c 14/07/2026** |
| 07 Data collection complete | Week 20 → **Week 26** | w/c 28/07/2026 → **w/c 08/09/2026** |
| 08 Transcription and coding complete | Week 24 → **Week 28** | w/c 25/08/2026 → **w/c 22/09/2026** |
| 09 Data analysis complete | Week 28 → **Week 30** | w/c 22/09/2026 → **w/c 06/10/2026** |

*(Matches your manual A1R.md timeline; the .pages still holds the old dates.)*

---

## F. §5 References / Glossary / TOC / header —— NO ACTION

The only §5 diffs were straight→curly quotes on the Ayres and Zainal entries; since Pages auto-curls quotes, your .pages already matches, so nothing is applied there. The Glossary, Table of Contents, and the header table are all unchanged by P12.

---

## Next steps
1. Apply Changes 01–33 to your working .pages; build the Figure 1 table and paste the Figure 2 SVG; polish layout; export PDF.
2. Mirror the finished .pages back into `MGTK751_A1R.md`.
3. I then re-run P12.6 on the mirror-back (whole-doc QC + FULL dlint on §1–3 + word-count recheck) and diff it before anything is sent.
4. Only once clean do we move to P12.8 (Log 19 cover email, then dispatch) —— not before you confirm send-ready.
5. After your manual edits and before dispatch, remind me to suggest any further judicious bolding (MP15 12.10).
