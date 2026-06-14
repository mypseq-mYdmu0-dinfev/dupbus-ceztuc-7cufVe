# Response to career_query_202606150624
*DXMF.py + DAMF.py —— Line 1 now accepts full and relative paths*

1. **CIIW on DAMF:** it could NOT accept a full path either. DAMF resolved Line 1 only by `rglob(filename)`, and rglob rejects absolute patterns (raises `NotImplementedError`), so any full path would have crashed it. It only ever worked because you always fed it a bare filename. Both are now fixed.

2. **Root cause (DXMF):** DXMF did accept a clean full path, but failed on a *copied* one in two ways:
- 2.1. Drag-and-drop / terminal-style paths escape spaces with backslashes (`/Volumes/FURY\ 2TB/...`); the literal backslashes meant no path matched, and the filename fallback then hit the same `rglob` absolute-pattern crash.
- 2.2. A quoted path (`'/Volumes/...'`) kept the quotes as literal characters, so nothing matched.

3. **Fix (both scripts):** Line 1 is now resolved through ordered variants —— raw first, then quote-stripped, then shell-unescaped (`shlex`) —— and the repo filename-search is guarded to skip absolute paths so it never crashes.
- 3.1. Raw-first matters: a plain `Copy as Pathname` value has *literal* spaces (`/Volumes/FURY 2TB/...`); trying it verbatim before any unescaping means that common case is honoured and not split apart.
- 3.2. Accepted forms now, for both Line-1 inputs: a full absolute path, a repo-relative path (e.g. `temp/test.md`), or a bare filename to search for.
- 3.3. Copied-path quirks all handled: literal spaces (Copy as Pathname), backslash-escaped spaces (drag-and-drop), and surrounding quotes.

4. **Verified** all five forms on both scripts (compile clean): plain-abs, escaped-abs, quoted-abs, relative, bare-filename —— all ✅ on DXMF and DAMF.
- 4.1. Minor cosmetic note: DAMF's success line echoes your raw Line-1 text (so it may show the quotes or backslashes you typed), but the file it acted on is resolved correctly. DXMF reports a count rather than the path, so it is unaffected.

5. `cscpt/set_dates.py` needs no change —— it takes terminal arguments, where the shell already unescapes the path before it reaches the script.
