#!/bin/zsh
# DO NOT paste this file's content into the terminal (the #! line and
# backticks below will break an interactive shell). Instead run it as
# a file, e.g.: zsh nscpt/trim_split_video_size.sh
set -euo pipefail

# ============================================================
# trim_split_video_size.sh
# Trims [START_TRIM_MIN, duration-END_TRIM_MIN] off a video (stream
# copy, no re-encode) then splits the remainder BY FILE SIZE, into
# parts each <= SIZE_LIMIT_BYTES. Output goes to a new timestamped
# subfolder under Fury Downloads/. Part numbering starts at 001 (no
# 000), so the last file's number = total part count.
# ============================================================

# >>> SET INPUT FILE PATH HERE <<<
SRC="/Volumes/FURY 2TB/Fury Downloads/REPLACE_ME.mov"
# >>> SET INPUT FILE PATH HERE <<<

# ---- editable settings ----
START_TRIM_MIN=0        # minutes to remove from the start (default 0)
END_TRIM_MIN=0          # minutes to remove from the end (default 0)
SIZE_LIMIT_BYTES=1900000000   # per-part size cap, default 1.9GB (Gemini max 2GB)
# ----------------------------

OUT_DIR="/Volumes/FURY 2TB/Fury Downloads/$(TZ='Australia/Sydney' date +'%Y%m%d%H%M')"
mkdir -p "$OUT_DIR"
OUT_BASE="$(basename "$SRC" | sed 's/\.[^.]*$//')_part"

DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SRC")
BIT_RATE=$(ffprobe -v error -show_entries format=bit_rate -of csv=p=0 "$SRC")
BYTES_PER_SEC=$(( BIT_RATE / 8 ))

START_SEC=$(( START_TRIM_MIN * 60 ))
END_SEC=$(( END_TRIM_MIN * 60 ))
TRIMMED_DURATION=$(echo "$DURATION - $START_SEC - $END_SEC" | bc)

# 1.45x safety margin: keyframe-aligned segments run larger than the
# naive size/bitrate estimate (observed ~1.43x overshoot empirically)
SEGMENT_TIME=$(( SIZE_LIMIT_BYTES / (BYTES_PER_SEC * 145 / 100) ))

DURATION_ARGS=()
if [ "$END_TRIM_MIN" -gt 0 ]; then
  DURATION_ARGS=(-t "$TRIMMED_DURATION")
fi

ffmpeg -v warning -ss "$START_SEC" -i "$SRC" "${DURATION_ARGS[@]}" -c copy -map 0 \
  -f segment -segment_time "$SEGMENT_TIME" -segment_start_number 1 -reset_timestamps 1 \
  "$OUT_DIR/${OUT_BASE}_%03d.mov"

echo "Done. Output folder: $OUT_DIR"
ls -la "$OUT_DIR"
