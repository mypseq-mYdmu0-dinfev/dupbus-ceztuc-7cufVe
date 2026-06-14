# `cscpt/` —— CC scripts (RUN, don't READ)

Every script in this folder is CC-only and **designed to be RUN via the shell, NEVER read into context**. Read a script ONLY when explicitly asked to POLISH that script itself. Reading one wastes context (each is thousands of tokens); its behaviour is documented where it is actually needed, so a caller never has to open the `.py`.

(`gscpt/` is the user's own scripts —— different folder, different owner.)

## Scripts

- `dlint.py` —— deterministic deliverable/output linter (auto-fixes straight quotes → typographic in FULL mode, then flags 🔴 RED / 🟡 YELLOW breaches of `universal/writing.md` + root `CLAUDE.md`). Usage, modes (FULL / `--text` / `--quick`) and the run-and-loop workflow live in `universal/writing.md` § Deliverable Lint. **Run, never read.**
- `dlint_hook.sh` —— PostToolUse fast-path shim wired in root `.claude/settings.json`. Exits 0 instantly unless the payload mentions `response_`/`close_`/`wrap_` (so Python is spawned only when relevant), then delegates to `dlint_hook.py`. **Run by the harness, not read.**
- `dlint_hook.py` —— the hook body. On a CC-authored comms write/edit (`response_`/`close_`/`wrap_` `.md`, incl. CP prefixes) it runs `dlint.py --quick` and blocks (exit 2) until 🔴 RED = 0. Ignores `query_`/`artefact_`, code, automations, `/seek/`; fail-safe (exits 0 on any error). **Run by the harness, not read.**
