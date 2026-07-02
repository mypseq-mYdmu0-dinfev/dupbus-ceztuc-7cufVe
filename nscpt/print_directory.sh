cd [path]
find . -print | sed 's|^\./||'
# files only
cd [path]
find . -type f | sed 's|^\./||'