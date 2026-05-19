src="/Volumes/FURY 2TB/Fury Pictures/Screenshots/Sort"
dst="$src/Delete"

mkdir -p -- "$dst"

for f in "$src"/*; do
  [[ -f "$f" ]] || continue
  name=${f:t}
  [[ "$name" == *" (4).png" ]] || mv -- "$f" "$dst/"
done