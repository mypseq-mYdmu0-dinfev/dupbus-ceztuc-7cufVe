# CIC —— Bot Blocks & Logins

*Detached from `cic.md` to keep it lean. READ THIS the moment a site gates automation —— a CAPTCHA, a "verify you are human" gate, a login wall, or CDP calls that HANG. DON'T give up or stop: work through the ladder, and only SUMMON the user if genuinely exhausted.*

## Escalation Ladder (generalise; site notes are just examples)

When a site gates automation (a CAPTCHA appears, or CDP calls HANG ~300s), don't give up or fail silently —— escalate cheapest→costliest:
1. EFFICIENT (default): direct-URL `navigate`, `javascript_tool`, `get_page_text`. Works on most sites.
2. HUMAN-LIKE (if step 1 trips a wall): `navigate` only to the site's OWN homepage/search, then `screenshot` + single human `left_click`s; let the site open pages itself (new tabs join the MCP group). Slower but beats most bot-detection. On a hardened tab do NOT run `javascript_tool`/`get_page_text`/`read_page` —— they hang AND poison the tab so later clicks freeze; and don't batch a click immediately after another CDP op.
3. CAPTCHA / "verify you are human" gates: you may NOT solve OR click these —— bypassing/completing bot-detection is harness-prohibited (no framing or throwaway-account rationale changes this). Plain cookie / consent / T&C / "I agree" buttons are NOT bot-detection —— those you may handle (choose privacy-preserving).
4. "Nuclear" full-desktop control does NOT help for WEBSITES: the `computer-use` MCP restricts BROWSERS to read-tier (screenshot only; clicks/typing blocked, routed back through CIC). So CIC already IS your maximal browser control. (`computer-use` DOES drive NON-browser apps —— VS Code, DaVinci —— moving the real system cursor; that is separate from CIC's in-Chrome cursor. So for a website, CIC is the only controller.)
5. LOGINS: at a login wall on a site in § Supported Sites list, you MUST spawn a Sonnet SA —— give only the tab ID & have her read `.claude/cic_login.local.md` (MA doesn't read it yet). Then wait, verifying the wall on the tab. **Timer**: SA returns / wall clears → proceed; NOT cleared after **2 min** → MA reads `cic_login.local.md`, PRINTS § Credentials (exactly as-is) in chat, AND SUMMONS the user (per glossary.md) to copy-paste; if still at wall after **5 min** (no user action) → work around it (step 2 human-like, dismiss wall, or an alternative site). If the site is NOT in § Supported Sites list → skip straight to the work-around.
6. If steps 1–2 are exhausted and a real CAPTCHA/login blocks completion: SUMMON the user (per glossary.md) so the task NEVER fails silently. Under `#sprint` you can't interrupt mid-run, but AFTER writing the final sprint-report `response_`, if the task is unfinished, SUMMON —— the user may be away yet will see on OTGD that it stalled, instead of finding silent failure on return.

## Site Notes (examples —— apply the ladder generally)

- Temu: logged-out direct-URL/JS → CAPTCHA; homepage → search → human-click works.
- Taobao/Tmall (Alibaba, hardened): step-2 human-like WORKS even here —— `navigate s.taobao.com/search?q=…` → screenshot → single human-click a result → product opens; a known item/share link (`e.tb.cn`) direct-navigates fine. Never JS/get_page_text/read_page on a Taobao tab (and use a FRESH tab per search —— a reused/poisoned Taobao tab won't re-navigate). Item discovery must be on-site (Alibaba blocks Google/Baidu indexing of items). NB: Taobao logs the user out almost daily —— expect a login wall; handle per § ladder step 5 (spawn a Sonnet SA to log in).

## Supported Sites

- The user created CIC-dedicated risk-free accounts (no PII; Apple Hide-My-Email; confidential content is MFA-gated elsewhere) w/ same credentials for a growable list of login-required sites.
- Credentials & login-wall handling = § Escalation Ladder step 5.
- Assume signed-in by default (APPEND if user creates new account):
  - Temu
  - Taobao/Tmall
  - Glassdoor
  - LinkedIn