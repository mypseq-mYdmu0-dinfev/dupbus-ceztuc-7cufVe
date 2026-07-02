#!/bin/zsh
# DO NOT paste this file's content into the terminal (the #! line and
# backticks below will break an interactive shell). Instead run it as
# a file, e.g.: zsh nscpt/trim_split_video_duration.sh
set -euo pipefail

# ============================================================
# trim_split_video_duration.sh
# Trims [START_TRIM_MIN, duration-END_TRIM_MIN] off a video (stream
# copy, no re-encode) then splits the remainder BY DURATION, into
# parts each SEGMENT_MIN long. Output goes to a new timestamped
# subfolder under Fury Downloads/. Part numbering starts at 001 (no
# 000), so the last file's number = total part count.
# ============================================================

# >>> SET INPUT FILE PATH HERE <<<
SRC="/Volumes/FURY 2TB/Fury Downloads/Screen Recording 2026-07-02 at 12.00.00.mov"
# >>> SET INPUT FILE PATH HERE <<<

# ---- editable settings ----
START_TRIM_MIN=19        # minutes to remove from the start (default 0)
END_TRIM_MIN=0          # minutes to remove from the end (default 0)
SEGMENT_MIN=4.9            # length of each output part, default 5min (Gemini max)
# ----------------------------

OUT_DIR="/Volumes/FURY 2TB/Fury Downloads/$(TZ='Australia/Sydney' date +'%Y%m%d%H%M')"
mkdir -p "$OUT_DIR"
OUT_BASE="$(basename "$SRC" | sed 's/\.[^.]*$//')_part"

START_SEC=$(( START_TRIM_MIN * 60 ))
END_SEC=$(( END_TRIM_MIN * 60 ))
SEGMENT_TIME=$(( SEGMENT_MIN * 60 ))

DURATION_ARGS=()
if [ "$END_TRIM_MIN" -gt 0 ]; then
  DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SRC")
  TRIMMED_DURATION=$(echo "$DURATION - $START_SEC - $END_SEC" | bc)
  DURATION_ARGS=(-t "$TRIMMED_DURATION")
fi

ffmpeg -v warning -ss "$START_SEC" -i "$SRC" "${DURATION_ARGS[@]}" -c copy -map 0 \
  -f segment -segment_time "$SEGMENT_TIME" -segment_start_number 1 -reset_timestamps 1 \
  "$OUT_DIR/${OUT_BASE}_%03d.mov"

echo "Done. Output folder: $OUT_DIR"
ls -la "$OUT_DIR"
