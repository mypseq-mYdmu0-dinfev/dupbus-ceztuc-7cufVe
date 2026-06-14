# Response to career_query_202606150554
*Package trimmed; DXMF reverted to .txt-only; cscpt/set_dates.py created*

6. **Package trimmed —— `temp/Rennly_20260612_dup/` (163M → 41M).**
- 6.1. **Privacy scan first:** grepped every kept text file in `build/` and `resource/` for `culous`, `/Volumes/FURY`, `/Users/`, `home789`, `dupbus` —— all clean. The build scripts use relative paths only, so they expose no local paths or your username. The one real leak was `build/.venv/` (its `pyvenv.cfg` and `bin/` shebangs hard-code your absolute home path), now removed.
- 6.2. **Removed:** `build/.venv/` (privacy leak + bulk), `build/clips/` (intermediate renders), `build/qa/` and the `qa_s*.png` previews (internal checks), `resource/aurea_music_source.mp3` (raw track, not a deliverable), and every `.DS_Store` and custom-icon `Icon` file throughout.
- 6.3. **Kept (the AI-showcase):** `AURÉA Reel.mp4`, `AURÉA Deliverables.pdf`, `build/` (the `build_reel*.sh` + `gen_overlays*.py` scripts, the `ov/` `ov2/` `txt/` overlay artwork, and the scrim PNGs —— this is what proves the work was programmed, not made in Canva), and `resource/` (the 8 hero renders + the original brief).
- 6.4. **Re-scrubbed** all 59 remaining items to 12/06/2026 20:31 across all four dates (verified on the folder, the Reel, a build script, and a render).
- 6.5. ⚠️ **One macOS quirk:** `.DS_Store` files regenerate the moment Finder browses a folder (I watched them reappear mid-delete). If you open the folder in Finder before copying, a fresh `.DS_Store` may appear. Copying the *contents* into Google Drive ignores `.DS_Store` on upload, so it will not reach the employer; just do not be surprised to see one locally.

7. **`gscpt/DXMF.py` —— reverted to your private, .txt-only tool.**
- 7.1. Removed the command-line mode entirely; it now takes input solely from a single `.txt` beside it (Line 1 target, Line 2 timestamp), exactly like DAMF.py. It still sets all four dates and still recurses if the target is a folder. Dropped the now-unused `os` import. Compiles clean.
- 7.2. DAMF.py left untouched.

8. **`cscpt/set_dates.py` —— created for my use (terminal-driven, 5 modes).**
- 8.1. Built by duplicating DXMF's internals, then swapping the `.txt` interface for terminal arguments: `python3 cscpt/set_dates.py <mode> <YYYYMMDDHHmm> <path> [more...]`.
- 8.2. Modes: `1`=Created, `2`=Modified, `3`=Added, `4`=Last Opened, `5`=all four —— exactly the 1-per-date plus all-four design you specified.
- 8.3. Folder-recursive (deepest-first), symlink-safe (NOFOLLOW), with concise top comments for the next CC. Proven live: I used `mode 5` to perform the re-scrub in 6.4 (59 items, verified).
- 8.4. Superseded my earlier `temp/set_dates.py` (only did 3 dates); voided it as `temp/❌_set_dates.py` for you to delete.

9. **`cscpt/README.md` updated.** Added a one-line entry for `set_dates.py` (usage, the 5 modes, caveats), in the same RUN-don't-READ style as the other scripts, so any future CC can use it from the README alone without opening the `.py`.

10. **Where to note that I can use it (suggestion).**
- 10.1. I did NOT use the memory store —— root CLAUDE.md §8.6 forbids CC creating/editing files there, which overrides the default memory behaviour.
- 10.2. My recommendation: add one pointer line to **root `CLAUDE.md`**, since that is the only always-loaded index every session reads. A natural home is near §2.9 (proactive suggestions) or §8 (File Rules), worded so it points to the README rather than repeating usage, e.g.:
  - `macOS file date manipulation (privacy scrub / set a deliberate date) → cscpt/set_dates.py; see cscpt/README.md.`
- 10.3. Alternatively, a line under `universal/glossary.md` if you prefer to keep CLAUDE.md lean. I can apply whichever you choose —— say the word and I will add it (I have not edited CLAUDE.md unprompted given its governing weight).

11. **Ready-to-send state.** The package is now clean, privacy-safe, and date-scrubbed. Copy the *contents* of `temp/Rennly_20260612_dup/` into your Google Drive package, confirm `http://Rennly20260612.CulousYu.com` resolves, then send the email drafted in the AR (§ User Video Submission).

---

*🟡 Justification (dlint): the `-` line under 10.2 is a verbatim example of the single pointer line to paste into CLAUDE.md, shown as a quotable snippet rather than a numbered list item; left un-numbered deliberately so it can be copied as-is.*
