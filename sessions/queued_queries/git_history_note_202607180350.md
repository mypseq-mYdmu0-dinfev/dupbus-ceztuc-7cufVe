# Git History Preservation for Bulk File Moves —— Technical Note for CCSIM

*From the AJAP #inv session (proven live on a 4-folder, `~`4,700-file repo rename, 202607180103 —— histories verified intact on GH). CCSIM: judge each rule against your exact situation; your files (mostly prose .md) carry ONE extra caveat, §4.*

## 1. The Core Fact
- Git stores SNAPSHOTS, never renames —— "history" across a move is RE-DETECTED afterwards by content similarity between the old and new file.
- Anything that drops similarity below git's threshold (default `~`50%) at the move commit SEVERS the file's history permanently.

## 2. The Discipline (what actually preserved history here)
- MOVE-ONLY commit: `git mv` the files/folders and commit w/ ZERO content edits —— 100% similarity, detection cannot fail.
- Edit in SEPARATE commits, before or after, never mixed w/ the move.
- NEVER delete-then-recreate across commits (severs even w/ identical content later); always `git mv` (or plain move + `git add -A`, which git treats identically —— the commit shape is what matters, not the command).
- Batch scale is fine: one move-only commit can carry thousands of files; per-file commits are unnecessary.
- Consider splitting UNRELATED move groups into separate move-only commits so the diff stays reviewable (the user accepted this as good practice for large-scale moves).

## 3. The Boundary That Cannot Be Crossed
- History CANNOT follow a file ACROSS repos —— repos share no object database; a file copied to another repo arrives as a NEW file, its history stranded in the source repo.
- If a cross-repo move is unavoidable and history is vital, the options are heavyweight (`git filter-repo` subtree extraction, subtree merge/graft) —— judge whether the history's value justifies that surgery; the AJAP migration deliberately accepted the loss for its cross-repo class.
- Within ONE repo, any path depth/reshuffle is safe under §2 —— `cp/` restructures inside the default repo preserve history if done as move-only commits.

## 4. The Prose-File Caveat (CCSIM's case specifically)
- Similarity is computed on CONTENT: a .md that gets heavily rewritten (reflowed, restructured, trimmed) in the SAME commit as its move can fall below the threshold even in-repo —— the failure mode looks identical to a delete+create.
- Small prose files are the most fragile (a 20-line note w/ 11 lines changed is already <50% similar); code files w/ boilerplate survive more edits.
- Rule of thumb: move first (move-only commit), let it land, THEN edit freely —— never "tidy whilst moving".

## 5. Verification (after every move commit)
- `git log --follow -- <new/path>` shows the pre-move history —— spot-check a few files per batch, incl. the smallest ones (most fragile).
- GH's web file-history view applies its own rename detection; if GH shows a break but `--follow` locally does not, the history is intact —— GH's view is the weaker detector, not the truth.
- Catch problems BEFORE pushing more work on top: a severed move can be redone cleanly only whilst it is the tip (reset, redo as move-only); once buried, repair needs history rewriting.
