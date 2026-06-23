### AD12. P12.7–P12.8 (Session 16) —— A1R v2 Resubmission Build & Send-Prep

*Note: append under `## PART C` of DevPlan.md; delete this response_ after appending. MECE with `close_202606240805` (handoff = next-chat-only; this = permanent).*

- AD12.1. Coverage
  - AD12.1.1. Executed **P12.7** (`#replace #adv` .pages handoff): diffed `archive/…192247.md` against `A1R.md`, emitted Changes 01–40 in `dissertation_response_202606232120.md`, which the user applied across many turns of iterative polish.
  - AD12.1.2. Executed **P12.8**: drafted the Log 19 cover email (SA-assisted), mapped CM1–CM5 + her Log 16 sampling points to each revision; the user pushed it to `lu.md` as **Log 22** (after intervening Logs 19–21).
  - AD12.1.3. Ran a full claim audit of `A1R.md`, a fresh-eyes re-QC of the final PDF, and an SA scan of Enis's materials on qualitative-language terms; mirrored `A1R.md` to the user-finalised `.pages`; ran the P12.8.0 full dlint (body clean).
  - AD12.1.4. Protocol/tooling work (beyond the deliverable): created `cscpt/padv.py`; rewrote `universal/replace_adv.md`; added the one-edit rule to `universal/replace.md`; added **CLAUDE.md §8.9**; added the **CIC-validation Mandate** to `universal/cic.md` and removed WCIC; created `universal/cic_libs.md`.

- AD12.2. Decisions
  - AD12.2.1. **U+2028 / `#replace #adv` overhaul (critical).** Pages' ⌘F CANNOT match any string containing a layout line-break (`U+2028` soft-return) —— confirmed empirically. So every `Replace:` is split at its `U+2028` into break-free blocks (MAX 3: before-first / middle / after-last); `cscpt/padv.py` extracts the verbatim span from the `.pages.md` mirror and splits it. Codified in `replace_adv.md` § Splitting.
  - AD12.2.2. **One edit per `## Change`** moved to `replace.md` (general, not `#adv`-only).
  - AD12.2.3. **CLAUDE.md §8.9 (Creation Placement):** NEVER create in root unless told; voidable temp scripts beside the `response_`; reusable scripts in `cscpt/` + update its README.
  - AD12.2.4. **CIC-validation Mandate (`cic.md`):** when `#cic` or any high-stake validation, you MUST validate by a CIC live page read; `web_search`/CrossRef are TRIAGE ONLY and never confirmation. Established after a Crossref-only citation entered the deliverable with the wrong volume.
  - AD12.2.5. **Blumer (1954) added** (CIC/JSTOR-validated: *American Sociological Review* 19(1), pp. 3–10, doi 10.2307/2088165) to ground "sensitising concepts" at §2.5 first use, logged in RefRepo (Methodology Precedent). **Figure 1 retitled "Sensitising Concepts"**, col-1 header **"Strand"** (covers RQ1/RQ2/Stakes).
  - AD12.2.6. **Numerals refinement:** numerals for plain CARDINALS only; ORDINALS ("third", not "3rd") and established-framework counts ("six-phase", "four trustworthiness criteria", "four cultural dimensions") stay as WORDS.
  - AD12.2.7. **Citation fix:** Li, Xu and Kwan (2021) repointed to **Sung et al. (2024)** for the "reactive" KS-recalibration claim (§1 and §2.2); Li retained correctly in §2.1. Practitioner-stat scope caveats (Billan "Canadian", Young & Tong / Beatson "UK") were REJECTED by the user as counter-valuable to the Australian framing.
  - AD12.2.8. **"explanations" → "understandings" (§3.2)** for the qualitative lexicon (SA-checked: "explain/explanatory" not on Enis's avoid-list, but "understand/explore/describe" are the sanctioned verbs; "why/cause/effect/relate/influence/variable/prove/test" are the flagged ones —— all avoided save the LOCKED RA verb "influences", kept).
  - AD12.2.9. **WCIC removed** from `cic.md` (redundant: CC = CCIC, the default). **`cic_libs.md`** created (UoL/UTS library guide + the SSO credentials, by the user's informed decision: library SSO reaches nothing MFA-gated, so no real risk; lapses after 2026).
  - AD12.2.10. **`.pages` is now the source of truth** post-P12.7; `A1R.md` mirrors it (faithful twin), bolding included.

- AD12.3. Deviations
  - AD12.3.1. P12.7 ran across ~14 turns (not one batch) because the U+2028 problem only surfaced when the user tried to ⌘F the first emitted Changes; the workflow + tooling were rebuilt mid-phase.
  - AD12.3.2. The cover email is logged as **Log 22**, not Log 19 (the comms log gained Logs 19–21: Lu's speed chase, Culous' illness note, Lu's health-first reply).
  - AD12.3.3. Substantial protocol-file work this session is unrelated to the A1R deliverable but permanent (see AD12.1.4 / AD12.2).

- AD12.4. Session Files
  - AD12.4.1. Comms: the 16 `query_`/`response_` pairs + 2 standalone `response_` (202606232103, 202606232120) listed in `close_202606240805` § Session Files.
  - AD12.4.2. Non-comms created: `cscpt/padv.py`; `universal/cic_libs.md`.
  - AD12.4.3. Non-comms modified: `dissertation/MGTK751_A1R.md`, `MGTK751_RefRepo.md`, `lu.md`; `universal/replace.md`, `replace_adv.md`, `cic.md`; root `CLAUDE.md`; `cscpt/README.md`; `MGTK751_A1R_Figure2_TheoreticalFramework.svg` (figure tweaks, earlier turns).
  - AD12.4.4. Voided: `❌_temp_build_p127.py`, `❌_temp_padv_regen.py`, `❌_temp_mirror_a1r.py`, `❌_temp_log19.md` (all beside the `response_`, safe to delete).

- AD12.5. Remarks
  - AD12.5.1. Immediate next action is the USER's: fix the Log 22 typo ("managed to finished" → "managed to finish") and send; then the project enters P13 (Lu + 2 reviewers' approval → ethics).
  - AD12.5.2. P13/P14 remain to be detailed once the draft is approved; A2/A3 phases built then (AD11.5.3 stands).
