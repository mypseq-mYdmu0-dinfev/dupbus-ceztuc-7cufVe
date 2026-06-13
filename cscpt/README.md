# `cscpt/` —— CC scripts (RUN, don't READ)

Every script in this folder is CC-only and **designed to be RUN via the shell, NEVER read into context**. Read a script ONLY when explicitly asked to POLISH that script itself. Reading one wastes context (each is thousands of tokens); its behaviour is documented where it is actually needed, so a caller never has to open the `.py`.

(`gscpt/` is the user's own scripts —— different folder, different owner.)

## Scripts

- `dlint.py` —— deterministic deliverable/output linter (auto-fixes straight quotes → typographic, then flags 🔴 RED / 🟡 YELLOW breaches of `universal/writing.md` + root `CLAUDE.md`). Usage, modes (FULL / `--text` / `--quick`) and the run-and-loop workflow live in `universal/writing.md` § Deliverable Lint. **Run, never read.**
