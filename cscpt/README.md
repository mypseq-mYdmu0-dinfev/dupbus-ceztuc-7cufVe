# `cscpt/` —— CC scripts (RUN, don't READ)

Every script in this folder is CC-only and **designed to be RUN via the shell, NEVER read into context**. Read a script ONLY when explicitly asked to POLISH that script itself. Reading one wastes context (each is thousands of tokens); its behaviour is documented where it is actually needed, so a caller never has to open the `.py`.

(`gscpt/` is the user's own scripts —— different folder, different owner.)

## Scripts

- `set_dates.py` —— macOS date setter. Sets a file/folder's Finder dates to a target timestamp (Sydney local). Usage: `python3 cscpt/set_dates.py <mode> <YYYYMMDDHHmm> <path> [more...]`. Modes: `1`=Created, `2`=Modified, `3`=Added, `4`=Last Opened, `5`=all four. A path may be a file or a directory (recursive, deepest-first, symlink-safe). Use to strip local timestamps before a file leaves the machine, or to set a deliberate date. `ctime` cannot be set and Spotlight's displayed Last-Opened may lag (the xattr is authoritative); both are local-only and do not survive copy/upload. **Run, never read.** (Sibling: `gscpt/DXMF.py` is the user's `.txt`-driven equivalent.)
- `dlint.py` —— deterministic deliverable/output linter (auto-fixes straight quotes → typographic in FULL mode, then flags 🔴 RED / 🟡 YELLOW breaches of `universal/writing.md` + root `CLAUDE.md`). Usage, modes (FULL / `--text` / `--quick`) and the run-and-loop workflow live in `universal/writing.md` § Deliverable Lint. **Run, never read.**
- `dlint_hook.sh` —— PostToolUse fast-path shim wired in root `.claude/settings.json`. Exits 0 instantly unless the payload mentions `response_`/`close_`/`wrap_` (so Python is spawned only when relevant), then delegates to `dlint_hook.py`. **Run by the harness, not read.**
- `dlint_hook.py` —— the hook body. On a CC-authored comms write/edit (`response_`/`close_`/`wrap_` `.md`, incl. CP prefixes) it runs `dlint.py --quick` and blocks (exit 2) until 🔴 RED = 0. Ignores `query_`/`artefact_`, code, automations, `/seek/`; fail-safe (exits 0 on any error). **Run by the harness, not read.**
- `padv.py` —— `#replace #adv` helper (see `universal/replace_adv.md`). A layout app's ⌘F cannot match across a `U+2028` soft-return, so a `Replace:` target must be quoted as break-free blocks (max 3). Extracts a verbatim span from a `<name>.pages.md` mirror and splits it: 0 breaks → 1 block, 1 → 2, ≥2 → 3. Usage: `python3 cscpt/padv.py <mirror.pages.md> "<start_anchor>" ["<end_anchor>"]` (prints ready-to-paste fenced blocks); also importable (`grab`, `split_for_pages`). **Run, never read.**
