#!/bin/bash
set -e
cd "$(dirname "$0")"
IMG=".."

# build_scene OUT IMGFILE DUR  OVSPEC...   (OVSPEC = "file:fin_st:fin_d:fout_st:fout_d"  fout_st empty => no fade out)
build_scene() {
  local out="$1" img="$2" D="$3"; shift 3
  local DN=$(echo "$D*30/1" | bc)
  local inputs=(-loop 1 -t "$D" -i "$IMG/$img" -loop 1 -t "$D" -i scrim_bottom.png -loop 1 -t "$D" -i scrim_top.png)
  local fc="[0:v]scale=1350:-2,setsar=1,zoompan=z='min(zoom+0.0006,1.10)':d=$DN:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30[bg];[bg][1:v]overlay=0:0[bs];[bs][2:v]overlay=0:0[v0];"
  local idx=3 prev="v0" n=0
  for spec in "$@"; do
    IFS=':' read -r f fin_st fin_d fout_st fout_d <<< "$spec"
    inputs+=(-loop 1 -t "$D" -i "ov/$f")
    local fade="format=rgba,fade=t=in:st=${fin_st}:d=${fin_d}:alpha=1"
    if [ -n "$fout_st" ]; then fade="${fade},fade=t=out:st=${fout_st}:d=${fout_d}:alpha=1"; fi
    fc+="[${idx}:v]${fade}[o${n}];[${prev}][o${n}]overlay=0:0[s${n}];"
    prev="s${n}"; idx=$((idx+1)); n=$((n+1))
  done
  fc="${fc%;}"
  ffmpeg -y "${inputs[@]}" -filter_complex "$fc" -map "[${prev}]" -r 30 -t "$D" \
    -pix_fmt yuv420p -c:v libx264 -crf 18 -preset medium "clips/$out" -loglevel error
  echo "built clips/$out"
}

build_scene s1.mp4 render_exterior_dusk.png 4.6 \
  "s1_hook.png:0.2:0.4:1.8:0.4" "s1_brand.png:2.2:0.6::"
build_scene s2.mp4 render_living.png 4.6 "s2.png:0.4:0.6:4.2:0.4"
build_scene s3.mp4 render_kitchen.png 4.2 "s3.png:0.4:0.6:3.8:0.4"
build_scene s4.mp4 render_bedroom.png 4.2 "s4.png:0.4:0.6:3.8:0.4"
build_scene s5.mp4 render_amenity1.png 4.8 "s5.png:0.4:0.6:4.4:0.4"
build_scene s6.mp4 render_aerial.png 6.8 \
  "s6_brand.png:0.3:0.6::" "s6_specs.png:0.5:0.6:3.0:0.5" "s6_cta.png:3.6:0.6::"

echo "concatenating with crossfades..."
ffmpeg -y -i clips/s1.mp4 -i clips/s2.mp4 -i clips/s3.mp4 -i clips/s4.mp4 -i clips/s5.mp4 -i clips/s6.mp4 \
 -filter_complex "[0][1]xfade=transition=fade:duration=0.6:offset=4.0[a];[a][2]xfade=transition=fade:duration=0.6:offset=8.0[b];[b][3]xfade=transition=fade:duration=0.6:offset=11.6[c];[c][4]xfade=transition=fade:duration=0.6:offset=15.2[d];[d][5]xfade=transition=fade:duration=0.6:offset=19.4[v]" \
 -map "[v]" -r 30 -pix_fmt yuv420p -c:v libx264 -crf 19 -preset slow -movflags +faststart \
 "../AUREA_Rhodes_Reel.mp4" -loglevel error
echo "DONE"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "../AUREA_Rhodes_Reel.mp4"
