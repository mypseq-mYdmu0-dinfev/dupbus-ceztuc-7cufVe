# `gscpt/` —— the user's own scripts

Personal utility scripts, mostly activated by dropping an instruction/input file into THIS folder and running the script. Every script ignores ALL of: `blank.md` (the renamed `temp.txt`), `temp.txt`, `README.md`, any `❌_`-prefixed filename (parked in place), and everything inside `parked/`. Sibling: `cscpt/` holds CC-only scripts —— different folder, different owner.

## Input & Instruction Files

- Every script that expects a text input takes `.txt` **and** `.md` —— `DAMF.py`, `DXMF.py`, `git_history.py`, `quote_fix.py`, `battery_logs.py`, and `shopping_records.py`. `.txt` alone would now find nothing. (`trade_records.py`/`transport_records.py` take a broker/Opal `.csv`, and `ocr_reads.py` takes `.jpg`/`.png`/`.pdf` —— none of those is a text file, so `.md` does not apply.)
- Because `.md` counts, every one of those scripts also skips the artefacts the others DROP in this folder: `DATS_*`, `ajap_*`, `ghist_*`/`git_history_*`, and `quote_fix.py`'s `*_processed`. Without that, a leftover `DATS_<ts>.txt` (a list of file paths) reads as a perfectly valid instruction file.
- `DAMF.py`/`DXMF.py`/`git_history.py`: leave exactly ONE eligible file beside the script; the others go in `parked/` or get a `❌_` prefix.
- Line 1 is the **absolute path** of the target —— in Finder, select it and press ⌘⌥C ("Copy as Pathname"). Surrounding quotes, backslash-escaped spaces, and a leading `~` are tolerated; blank and `#`-leading lines are skipped.
- A bare filename is **refused**, not searched for: a search that returned one match could return the wrong one and rewrite the wrong file's dates silently, and a relative path resolved differently depending on the directory the script was run from.

### Where `DAMF.py`/`DXMF.py` May Point

- **Anywhere on this Mac, deliberately.** Most runs target files OUTSIDE the repos (re-dating a deliverable so it reads as touched earlier or later), so an earlier fence confining targets to `.../Fury Documents/GitHub/` was a regression and has been removed.
- Only shapes that cannot be a real target are refused: any **mount point** (`/` and every volume root, e.g. `/Volumes/FURY 2TB`), **`/Users`**, **`/Volumes`**, and the **home folder itself**. Those are what a copied path trimmed one component too far lands on. A symlink pointing at one of them is refused too.
- System paths (`/usr`, `/System`, `/Applications`) are deliberately NOT on that list —— a "Copy as Pathname" value cannot be truncated into them, and the 50⁺-item confirmation still covers them.

## `parked/`

Files here are ignored by every gscpt script —— park instruction files you want temporarily inactive. (Scripts scan only this folder's top level, so parked files never activate anything.) A `❌_` filename prefix parks a file in place at the top level —— equally invisible to every script.

## Scripts

- `DAMF.py` —— Date Added Manual Fixer: sets Finder's "Date Added" from a 2-line instruction file (absolute path of a file OR folder, then `YYYYMMDDHHmm` Sydney). A folder is stamped recursively, the folder itself included; symlinks are stamped but never followed. `--dry-run`/`-n` previews; `--yes`/`-y` skips the confirmation asked for at 50⁺ items.
- `DXMF.py` —— Date eXtended Manual Fixer: as DAMF (same absolute path of a file or folder, same flags) but sets all FOUR Finder dates —— Created, Modified, Added, and Last Opened.
- `DATS.py` —— "Date Added = TS": one run aligns every query/close/wrap comms file's Date Added to the TS in its filename. Scans the default repo's `sessions/` AND `AJAP_repo/inv/` (see `SCAN_DIRS`; the legacy `seek/investigation/` root was retired 202607181152). `--dry-run`/`-n` previews.
- `ocr_reads.py` —— OCR batch reader: OCRs every `.jpg`/`.png`/`.pdf` beside it into one `.md` each under a new `[YYYYMMDDHHmm]/` folder (Sydney TS), via Apple Vision accurate. Re-run within 30 min on the same inputs: duplicates the folder (`_new` if same minute), suffixes existing files `_vision-accurate`, re-OCRs with the next means (`_vision-fast`; tesseract if installed); errors out when all means are exhausted.
- `ajap_logs_legacy.py` —— FROZEN backup of the AJAP CSV engine (renamed 202608020500; do not run or edit). The live copy is `AJAP_repo/scripts/analytics_logs.py`, which AJAP runs for itself at STOP: it reads the LEDGER (not AR folders) and reads/writes `AJAP_repo/logs/analytics/`, so an AJAP run no longer writes anything into this folder.
- `git_history.py` —— renders one file's full git history (any repo) as a word-diff HTML page; target path(s) come from an instruction `.txt`/`.md`, CLI args, or stdin. (Renamed from `ghist.py`; older output files still carry the `ghist_` prefix.)
- `battery_logs.py` —— consolidates battery-reading `.txt`/`.md` files into one timestamped CSV.
- `quote_fix.py` —— converts straight quotes to typographic ones in `.txt`/`.md` inputs (`[stem]_processed[ext]` outputs).
- `shopping_records.py` / `trade_records.py` / `transport_records.py` —— receipt (`.txt`/`.md`) / IBKR-statement (`.csv`) / Opal-statement (`.csv`) processors: drop the raw file(s) beside the script, run, collect the CSV(s).
