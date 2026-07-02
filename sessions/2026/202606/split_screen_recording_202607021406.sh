#!/bin/zsh
set -euo pipefail

SRC="/Volumes/FURY 2TB/Fury Downloads/Screen Recording 2026-07-02 at 12.00.00.mov"
OUT_DIR="/Volumes/FURY 2TB/Fury Downloads"
OUT_BASE="Screen Recording 2026-07-02 at 12.00.00_trimmed_part"

# Trim first 19min (1140s, vacant) + split into <=2GB parts, stream copy (no re-encode)
ffmpeg -v warning -ss 1140 -i "$SRC" -c copy -map 0 \
  -f segment -segment_time 380 -reset_timestamps 1 \
  "$OUT_DIR/${OUT_BASE}_%03d.mov"

echo "Done. Parts:"
ls -la "$OUT_DIR"/${OUT_BASE}_*.mov
