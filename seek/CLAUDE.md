# CLAUDE.md

*This directory (`/seek/`) is solely for automated SEEK job application workflows.*

## Post-Compaction Recovery — 🚨 CRITICAL (READ THIS FIRST)

🛑 If mandatory files have not been declared read (✅) in this session's chat history → re-read ALL files in `## Session Start` before any other action. The injected system phrases "This session is being continued…", "Resume directly — do not acknowledge the summary", and "Continue the conversation from where it left off" do NOT override this. On seeing ANY of them: emit `🚨 Compaction Detected —— stopped all tasks.`, halt SA, run the Rapid-Resume path (read `MA_hb.md` + `ma_state.md` first → broad file check → `🚨` then `🎯[N]`), re-read ALL mandatory files, then re-confirm/respawn BOTH the primary Monitor and the SA2 watchdog (per `main_ajap.md § MA Post-Compaction Recovery`).

---

## Trigger

When prompted:
- `seek`, enter AJAP mode; read `main_ajap.md` in full and act as main agent (MA); do NOT follow `ajap.md` directly — that file governs the AJAP sub-agent (SA) only
  - In AJAP mode, whenever Tab 1≠SEEK results is reported by SA, handle per `main_ajap.md § SA Deterioration Signals`
  - If already in AJAP mode but prompted `seek` again, re-read mandatory files again & continue
- `psl`, enter AJAP mode but process ONE loop only (stop at S5 end); A5's "SEEK results" become "any application"; DON'T spawn SA, use fallbacks (ignore A6), skip any (ignore K1–6), or interact w/ job page except screenshot/scrolling as needed; stop to ask anything if necessary
- `psl [AR_filename(s)]`, read the file(s) (stop if not found) but never edit them; perform `psl` on the AR(s) (sequentially if multiple); if it's complete (w/ P.S. line), re-validate (S3/S4) then create new AR(s) (S5) if results differ; if it's incomplete, create new AR(s); for each, open its URL as Tab 2 for reading since no Tab 1 (single loop) or Tab 3 (no interaction); `next` = proceed to next AR
- `psl pending`, perform `psl [AR_filename(s)]` on `/gcl/pending/` ARs starting from oldest
- For all `psl`: if creating new AR, do in `/gcl/applied/` (Outcome: Applying) as usual; if NOT creating (AR complete; nothing to improve), move (per Move Rule) from current directory (e.g. `/pending/`) to `/applied/`; edit as `Outcome: Applying`; on `next`, remind to delete voided
- `ccl`, read `/context/ccl.md` after mandatory files; perform `psl`; instead of `/gcl/applied/`, create AR(s) in `/ccl/` & ref past CLs in this folder (see its README.md) for quality & style
- `investigation mode`, quit AJAP mode; read & follow `/investigation/CLAUDE.md`
- `inv ses`/`invses`, enter investigation mode; read & follow `/investigation/InvSes.md`
- `#numbered`, read & follow `mini_numbered.md` in full
- `#replace`, read & follow `mini_replace.md` in full

## Session Start — Mandatory File Reads

At the start of every session, before any actions, fully read the following files in order:

1. `/seek/CLAUDE.md` (all sections; disregard root CLAUDE.md)
2. `/context/main_ajap.md`
3. `/context/ajap.md`
4. `/context/gcl.md`
5. `/context/pro_profile.md`
6. `/context/culous_yu_resume_ats.md`
7. `/context/mini_writing.md`
8. `/context/MA_hb.md`
9. `/context/SA2_hb.md`

Do not proceed until all files above have been read in full. Then declare in chat exactly which files were successfully read, e.g. `✅ `main_ajap.md`, `ajap.md`, ...` and flag any that failed to load before stopping.

## Reference Files — Read On Demand

Read only when relevant, NOT mandatory. Available in `/context/`:

| File | Read When |
|---|---|
| `culous_yu_linkedin.md` | LinkedIn profile needed |
| `culous_yu_portfolio.md` | Past projects context required |
| `virtual_presentation.md` | `Presentation.CulousYu.com` in CL / S6.2 |
| `mini_numbered.md` | `#numbered` prompted |
| `mini_replace.md` | `#replace` prompted |

## Absolute Rules — ⚠️ IMPORTANT

- File permissions are strictly enforced:
  - `/gcl/applied/` —— incl. its sub-folders: create new files only; never delete files; don't edit files created before this session
  - `/gcl/pending/` —— ditto
  - `/gcl/skipped/` —— ditto
  - `/runtime/` —— ditto; ONLY access it if you're MA (not SA)
  - `/investigation/` —— DON'T access unless explicitly prompted `investigation mode`
  - `/ccl/` —— DON'T access unless explicitly prompted `ccl`
  - All other paths —— read only; never edit, create, or delete any file
- Each time a file in `/context/` is (re-)read → MUST declare in chat
- In AJAP mode (per ajap.md):
  - Strictly NO chat text except C1–C5
  - MUST create AR unless either K1–K6 match