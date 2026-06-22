# Response to `fully dlint A1R.md, CB, and ProjectSummary`
*Full dlint —— results & reading*

1. What the run did (auto-fix)
- 1.1. Full mode auto-converted straight quotes/apostrophes → typographic, in place, in all three: A1R **13** converted, plus CB and ProjectSummary. This normalised the straight apostrophes my sprint edits had introduced into A1R ("CYC's" → "CYC's" etc.); A1R now has **zero** straight double-quotes and is internally consistent. I eyeballed the result —— no toggle desync. This is the one genuinely useful outcome of the run.

2. A1R.md (the deliverable) —— 76 RED, but the prose is clean
- 2.1. **7 Americanisms + most of the 42 "mid-sentence colons" are the REFERENCE LIST** —— verbatim published titles ("Victimization of high performers:", "The dark side of creativity:…"), journal names ("Organization Studies"), and the Harvard "Available at:" convention. These are correct and MUST stay verbatim; Britishising a cited title or dropping a Harvard colon would corrupt the citation.
- 2.2. **27 em dashes + a few colons are the Table of Contents, Glossary, and Figure 1 labels** —— your "——" separators ("AU —— Australian"), the "*INTERNAL:*" note, and "consequence:" in the figure. This is your established .pages structural formatting, which Lu accepted in v1.
- 2.3. **The argumentative body (§1–§3) is CLEAN** —— zero RED in the actual writing. The 17 YELLOW are bare `+` (e.g. "10⁺"-style) and 4 GenAI/cliche words, all in the references or footnotes; none material.
- 2.4. Implication: **"0 RED" is neither achievable nor desirable** for a Harvard-referenced, glossaried deliverable —— dlint does not exclude reference lists / glossaries / TOC, so it over-flags them. Nothing in the prose needs fixing.

3. CB & ProjectSummary —— internal files, so the deliverable rules do not bind
- 3.1. dlint is a **deliverable** linter. CB (165 RED) and ProjectSummary (18 RED) are INTERNAL working files; their flags are almost entirely the house-style "——" em dash (CB 82, PS 2) and colons in bullet notes ("Method:", "Current phase:") —— both legitimate internally (writing.md §2.4 makes "——" the internal standard). These are expected noise, not breaches; no action needed. The only thing worth doing there was the quote normalisation, which ran.

4. Genuine catch (NOT a dlint rule —— flagged, not fixed)
- 4.1. Stale **"Yin, 2009"** still sits in CB (×2: §1.4, §8.1), `lu.md`, `Concept_Brief_concise.md`, and `DevPlan.md`. The confirmed edition is **Yin (2003)** (AD10.2.3; the 2009 was a corrected training-knowledge slip), and A1R + ProjectSummary already say 2003. The deliverable is correct, so this is internal tidiness only. I did NOT part-fix it (fixing CB alone would leave the other three inconsistent). Say the word and I will sweep all four to "Yin, 2003" in one go.

5. Net
- 5.1. A1R's prose is clean and now quote-normalised; its RED count is reference-list and glossary conventions, not writing faults —— leave the references untouched.
- 5.2. One deliverable decision for you: the Glossary/TOC/Figure **"——"** separators. Keep them (Lu accepted them; low risk), or, for strict writing.md compliance, switch to "–" or restructure —— but that is a `.pages` formatting change, so it is your call, not something I should impose on the mirror.
- 5.3. Optional: the Yin (4.1) sweep.
