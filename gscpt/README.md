# `gscpt/` —— the user's own scripts

Personal utility scripts, mostly activated by dropping an instruction/input file into THIS folder and running the script. Every script ignores ALL of: `blank.md` (the renamed `temp.txt`), `temp.txt`, `README.md`, any `❌_`-prefixed filename (parked in place), and everything inside `parked/`. Sibling: `cscpt/` holds CC-only scripts —— different folder, different owner.

## `parked/`

Files here are ignored by every gscpt script —— park instruction files you want temporarily inactive. (Scripts scan only this folder's top level, so parked files never activate anything; `DAMF.py`/`DXMF.py` bare-filename searches also skip `parked/` explicitly.) A `❌_` filename prefix parks a file in place at the top level —— equally invisible to every script.

## Scripts

- `DAMF.py` —— Date Added Manual Fixer: sets a file's Finder "Date Added" from a 2-line instruction `.txt` (target, then `YYYYMMDDHHmm` Sydney).
- `DXMF.py` —— Date eXtended Manual Fixer: as DAMF but sets all FOUR Finder dates (Created/Modified/Added/Last Opened); a folder target is scrubbed recursively.
- `DATS.py` —— "Date Added = TS": one run aligns every query/close/wrap comms file's Date Added to the TS in its filename. Scans the default repo's `sessions/` AND `AJAP_repo/inv/` (see `SCAN_DIRS`; the legacy `seek/investigation/` root was retired 202607181152). `--dry-run`/`-n` previews.
- `ocr_reads.py` —— OCR batch reader: OCRs every `.jpg`/`.png`/`.pdf` beside it into one `.md` each under a new `[YYYYMMDDHHmm]/` folder (Sydney TS), via Apple Vision accurate. Re-run within 30 min on the same inputs: duplicates the folder (`_new` if same minute), suffixes existing files `_vision-accurate`, re-OCRs with the next means (`_vision-fast`; tesseract if installed); errors out when all means are exhausted.
- `ajap_logs_legacy.py` —— FROZEN backup of the AJAP CSV engine (renamed 202608020500; do not run or edit). The live copy is `AJAP_repo/scripts/analytics_logs.py`, which AJAP runs for itself at STOP: it reads the LEDGER (not AR folders) and reads/writes `AJAP_repo/logs/analytics/`, so an AJAP run no longer writes anything into this folder.
- `ghist.py` —— renders one file's full git history (any repo) as a word-diff HTML page; target path comes from an instruction `.txt`/`.md`.
- `battery_logs.py` —— consolidates battery-reading `.txt` files into one timestamped CSV.
- `quote_fix.py` —— converts straight quotes to typographic ones in `.txt`/`.md` inputs (`[stem]_processed[ext]` outputs).
- `shopping_records.py` / `trade_records.py` / `transport_records.py` —— receipt / IBKR-statement / Opal-statement processors: drop the raw file(s) beside the script, run, collect the CSV(s).
