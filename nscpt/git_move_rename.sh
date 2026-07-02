cd '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe'

git diff --quiet && git diff --cached --quiet || { echo "Uncommitted changes detected. Commit or stash them first."; exit 1; }

git mv 'temp/temp.md' 'temp/temp1.md'

git commit -m "Move/Rename temp/temp.md to temp/temp1.md"

git push origin main