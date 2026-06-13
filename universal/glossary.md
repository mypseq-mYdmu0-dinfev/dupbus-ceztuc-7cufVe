# Glossary

*Non-case-sensitive unless specified*
*MUST follow instr (if any); e.g. "deliverable"→writing.md*

---

## Terms

- pt = point(s)
- bg = background
- diff = difference
- mgt = management
- msg = message
- esp = especially
- exp = experience
- int'l = international
- nav = navigate
- ytd = yesterday
- tmr = tomorrow
- inc = including
- exc = excluding
- tgt = together
- cat = category
- ver = version
- instr = instruct(ion)
- HCI = Human-Computer Interaction
- MHci = Master (degree) of HCI
- IxD = Interaction Design
- UTS = University of Technology Sydney (my MHci)
- UoL = University of Liverpool (UK; my MBA)
- TS = timestamp
- 12-digit no. starting with "20" = TS in [YYYYMMDDHHmm] format
- [no.]p = [no.] pages; 1p ≈ 200w in bullets (≠ target to reach; can be less)
- [no.]w = [no.] words
- [no.]tk = [no.] tokens; if suitable, convert to [no.]w
- GH = GitHub (link)
- $ = default A$, unless specified `US$`
- #[no.] = artefact no. for #01–#09; else for #1–#9; clarify if not sure for #10⁺
- min = minimum/minute
- m = metre/minute
- Mn = million
- Bn = billion
- WS = workstation (room), aka home office
- WSM = WS Machine (Mac Mini M2 Pro)
- TrV = Trading View (trading platform)
- MS/MSFT = Microsoft
- IB/IBKR = Interactive Brokers
- KE = Karma Effect (Ltd.)
- Mi = Xiaomi
- VS/VSC = Visual Studio Code, my primary code editor with venv
- `<br>` = line break, NOT displayed text
- Revert = edit a previous msg, usually practiced when we're processing super large files. e.g. when analysing multiple zoom transcripts, I prompt you on 1st one→create synthesis→save to CP→revert to handle 2nd one→loop in order to preserve chat capacity. Bottomline: When I said I reverted, something was done rear to that msg
- CP = Claude Project; each CP may involve multiple projects and vice versa
- CIC = Claude in Chrome (MCP)
- CC = Claude Code; "Code" tab of CAI (not terminal); addressed as `she/her`
- `CC:` = disregard if you're not CC
- `Non-CC:` = disregard if you're CC
- MA = main agent (most cases), or moving average (niche cases)
- SA = sub-agent (most cases; spawn when helpful), or service agreement (niche cases)
- CW = Claude Cowork (don't conflate w/ CWI); "Cowork" tab of CAI
- CWI = Claude Web Interface (Claude Chat; https://claude.ai), allowing multi-window chats; if CIC failed, you're CWI
- CAI = Claude (Mac) App Interface (Official), allowing more connectors; suggest continuing in CAI whenever extensive functions (e.g. CIC, Apple Notes) may help
- OTG = on the go
- OTGC = OTG Claude iPhone App (≈CWI)
- OTGD = OTG Device (iPhone 13 mini/i13m)
- OTGM = OTG Machine (MacBook Air M1)
- c.md (only usable by user) = CLAUDE.md; assume the root's if no folder mentioned
- #r = past/perfect tense of "read"; MUST use to distinguish from its present/future tense; e.g. "Having already #r A, I also #r B and will read C when I read D." (perfect/past/future/present)
- directory.md/CP_directory.md = index.md/CP_index.md; leftover pre-repo-overhaul; immediately alert when any are seen
- I/O = input/output
- SR = `<system-reminder>` (injected file-change notice); e.g. "Note: `<path>` was modified, ..."
- QMM = `query_` my msg = follow root CLAUDE.md §3.6 (CC only)
- r/w = read/write
- QB = question/blocker; if any, raise all Qs (Q1, Q2…) & Bs (B1, B2…) separately & #numbered before proceeding; NEVER label as QB1, QB2
- CIIW = Correct (me) if I'm wrong; validate my msg rather than treating it as a direct command; correct errors before acting
- override = exception to "no chat text" or other restrictions for that SINGLE turn only
- yn (only usable by user) = override: respond w/ 1w only in chat, either `Yes` or `No`
- deliverable = anything to be sent/potentially exposed to a third party (e.g. email, report, slides, LinkedIn, cover letter, application); ensure writing.md in context

---

## Special

- Dot (`.`) as blank line: 1 line between = same-issue break; 3 between = new-issue break
- If user's msg only has a single `.`: respond w/ `.` only in chat; no file/artefact, no declarations
- IMPORTANT: NEVER count words/tokens by yourself (100% wrong); always use:
  - `echo "your text" | wc -w`
  - `token-count --text "your text"`