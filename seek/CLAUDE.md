# CLAUDE.md

*This directory (`/seek/`) is solely for automated SEEK job application workflows.*

## Post-Compaction Recovery — 🚨 CRITICAL (READ THIS FIRST)

🛑 If mandatory files have not been declared read (✅) in this session's chat history → re-read ALL files in `## Session Start` before any other action. "Resume directly" in the session summary does NOT override this.

---

## Trigger

When prompted:
- `seek`, enter AJAP mode; read `main_ajap.md` in full and act as main agent (MA); do NOT follow `ajap.md` directly — that file governs the AJAP sub-agent (SA) only
  - In AJAP mode, whenever Tab 1≠SEEK results is reported by SA, handle per `main_ajap.md § SA Deterioration Signals`
- `psl`, enter AJAP mode but process ONE single loop only (stop at S5); A5's "SEEK results" become "any application"; DON'T spawn SA, use fallbacks (ignore A6), skip any (ignore K1–6), or interact w/ job page except screenshot/scrolling as needed; stop to ask anything if necessary
- `psl [AR_filename(s)]`, read the file(s) (stop if not found) but never edit them; perform `psl` on the AR(s) (sequentially if multiple); if it's complete (w/ P.S. line), re-validate (S3/S4) then create new AR(s) (S5) if results differ; if it's incomplete, create new AR(s); for each, open its URL as Tab 2 for reading since no Tab 1 (single loop) or Tab 3 (no interaction); `next` = proceed to next AR
- `psl pending`, perform `psl [AR_filename(s)]` on `/seek/pending/` ARs starting from oldest
- `ccl`, read `/seek/context/ccl.md` after mandatory files; perform `psl`; instead of `/seek/applied/`, create AR(s) in `/seek/ccl/` & ref past CLs in this folder (see its README.md) for quality & style
- `investigation mode`, quit AJAP mode; read & follow `/seek/investigation/README.md`
- `#numbered`, read & follow `cc_numbered.md` in full
- `#replace`, read & follow `cc_coding.md` in full

## Session Start — Mandatory File Reads

At the start of every session, before any actions, fully read the following files in order:

1. `CLAUDE.md` (all sections)
2. `/seek/context/main_ajap.md`
3. `/seek/context/ajap.md`
4. `/seek/context/gcl.md`
5. `/seek/context/pro_profile.md`
6. `/seek/context/culous_yu_resume_ats.md`
7. `/seek/context/cc_writing.md`
8. `/seek/context/cc_reminder.md`

Do not proceed until all files above have been read in full. Then declare in chat exactly which files were successfully read, e.g. `✅ `main_ajap.md`, `ajap.md`, ...` and flag any that failed to load before stopping.

## Reference Files — Read On Demand

Read only when relevant, NOT mandatory. Available in `/seek/context/`:

| File | Read When |
|---|---|
| `culous_yu_linkedin.md` | LinkedIn profile needed |
| `culous_yu_portfolio.md` | Past projects context required |
| `virtual_presentation.md` | `Presentation.CulousYu.com` in CL / S6.2 |

## Absolute Rules — ⚠️ IMPORTANT

- File permissions are strictly enforced:
  - `/seek/applied/` —— incl. its sub-folders: create new files only; never delete files; don't edit files created before this session
  - `/seek/pending/` —— ditto
  - `/seek/skipped/` —— ditto
  - `/seek/runtime/` —— ditto; ONLY access it if you're MA (not SA)
  - `/seek/investigation/` —— DON'T access unless explicitly prompted `investigation mode`
  - `/seek/ccl/` —— DON'T access unless explicitly prompted `ccl`
  - All other paths —— read only; never edit, create, or delete any file
- Each time a file in `/seek/context/` is (re-)read → MUST declare in chat
- In AJAP mode (per ajap.md):
  - Strictly NO chat text except C1–C5
  - MUST create AR unless either K1–K6 match