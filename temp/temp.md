zixfa8-mydnug-qiXzav

## Pre-Flight Check (F[no.] = detailed actions)

Before beginning the loop, determine current state from open tabs AND contents in `/seek/applied/` `/seek/pending/` `/seek/skipped/` (incl. their sub-folders):

| Tabs Open | AR? | AR Complete (contains P.S. line)? | Tab 3 ≡ Tab 2? | State | Action |
|---|---|---|---|---|---|
| Tab 1 only | — | — | — | Clean | F1 |
| Tab 2+3 | ✅ | ✅ (filename w/ `⏳_`) | ✅ (job post) | Post-analysis, pre-application | F2 → re-read AR → S6 |
| Tab 2+3 | ✅ | ✅ (filename w/ `⏳_`) | ❌ (apply page) | Mid-application | F2 → F3 → re-read AR → S6 |
| Tab 2+3 | ✅ | ✅ (filename w/o `⏳_`) | ❌ (success page; S6.4.4) | Post-application, before S6.4.6 | F2 → F4 |
| Tab 2+3 | ✅ | ❌ | ✅ (job post) | Mid-analysis, post-AR | F2 → F5 |
| Tab 2+3 | ❌ | — | — | Pre-AR | Refresh Tab 2 → S2 |
| Tab 2 only | ✅ | ✅ (filename w/o `⏳_`) | — | Post-application, before S6.4.6 | F2 → F4 |
| Tab 2 only | ❌ | — | — | Interrupted during S2 | Refresh Tab 2 → S2 |

F1. `navigate` (refresh) Tab 1 only:
- F1.1. DON'T `read_page`, `get_page_text`, screenshot-scroll, or inspect any card content
- F1.2. Once confirm page loaded, click "New to you" (below search bar, next to "[no.] jobs") if visible, then:
  - F1.2.1. If no cards shown, click "[no.] jobs" (default view) → F1.2.2
  - F1.2.2. If cards shown, immediately proceed to S0
F2. MANDATORY: Get AR mod time (NOT current time) → Append to its Line 2: e.g. "**Date:** [creation_time] (Last Modified: [modified_time])
F3. Refresh Tab 2 → close Tab 3 → duplicate Tab 2 URL to a new Tab 3
F4. Check if AR reads `Outcome: Applied`
- F4.1. If yes → S6.4.6
- F4.2. If no → F3 → re-read AR → S6
F5. Remove existing AR (per Remove Rule), then restart from S2 (new AR) since research context is compromised & recovery unreliable

Note: If Tab 1 is inaccessible, blank, or shows no job cards at any point: stop immediately after 3 refresh attempts.
